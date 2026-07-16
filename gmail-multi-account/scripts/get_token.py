#!/usr/bin/env python3
"""One-time consent helper: obtain a Gmail API token for one mailbox.

Grants gmail.readonly + gmail.compose (read, search, download attachments,
create drafts - but NOT send). One OAuth Desktop client is shared by all
mailboxes; each mailbox gets its own token file.

Works even on a headless/remote machine: it does NOT rely on a loopback
server. The user consents in any browser, lands on a "site can't be reached"
localhost page, and copies that page's full address-bar URL (which carries
?code=...) back here.

Usage:
  python3 get_token.py url <account_email> [--creds <path-to-credentials.json>]
      -> prints the consent URL to open in a browser

  python3 get_token.py exchange <account_email> "<pasted localhost url OR raw code>" [--creds <path>]
      -> exchanges the code and saves google-token.<account_email>.json

Config dir: $GMAIL_ACCOUNTS_DIR or ~/.config/gmail-accounts
Expected there: google-credentials.json (the Desktop OAuth client you downloaded
from Google Cloud Console; a google-credentials.<email>.json also works).
"""
import sys, os, json, re, urllib.request, urllib.parse

CFG = os.environ.get("GMAIL_ACCOUNTS_DIR") or os.path.expanduser("~/.config/gmail-accounts")
REDIRECT = "http://localhost:8765/"
SCOPE = "https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/gmail.readonly"
STATE = "gmail-multi-account"

def load_client(account, creds_override):
    # Prefer an account-specific credentials file; else fall back to the shared one
    # (a single Desktop OAuth client works for every mailbox in the same GCP project).
    candidates = [creds_override,
                  f"{CFG}/google-credentials.{account}.json",
                  f"{CFG}/google-credentials.json"]
    path = next((p for p in candidates if p and os.path.exists(p)), None)
    if not path and os.path.isdir(CFG):
        path = next((f"{CFG}/{c}" for c in sorted(os.listdir(CFG))
                     if c.startswith("google-credentials") and c.endswith(".json")), None)
    if not path:
        raise SystemExit(f"No google-credentials*.json found in {CFG}. "
                         "Download the Desktop OAuth client JSON from Google Cloud Console first.")
    c = json.load(open(path))
    c = c.get("installed") or c.get("web") or c
    return c["client_id"], c["client_secret"], c.get("token_uri", "https://oauth2.googleapis.com/token"), path

def make_url(account, creds_override):
    cid, _, _, used = load_client(account, creds_override)
    q = urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": REDIRECT, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent",
        "login_hint": account, "state": STATE,
    })
    sys.stderr.write(f"(using OAuth client from {used})\n")
    return "https://accounts.google.com/o/oauth2/auth?" + q

def extract_code(blob):
    blob = blob.strip()
    if blob.startswith("http"):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(blob).query)
        if "code" in qs:
            return qs["code"][0]
    m = re.search(r"code=([^&\s]+)", blob)
    if m:
        return urllib.parse.unquote(m.group(1))
    return blob  # assume the user pasted the bare code

def exchange(account, blob, creds_override):
    cid, csec, token_uri, _ = load_client(account, creds_override)
    code = extract_code(blob)
    data = urllib.parse.urlencode({
        "client_id": cid, "client_secret": csec, "code": code,
        "grant_type": "authorization_code", "redirect_uri": REDIRECT,
    }).encode()
    tok = json.load(urllib.request.urlopen(urllib.request.Request(token_uri, data=data)))
    tok.setdefault("scopes", tok.get("scope", "").split())
    os.makedirs(CFG, exist_ok=True)
    out = f"{CFG}/google-token.{account}.json"
    json.dump(tok, open(out, "w"), indent=2)
    os.chmod(out, 0o600)
    print("SAVED:", out)
    print("scopes:", tok.get("scope"))
    print("has refresh_token:", bool(tok.get("refresh_token")))

def main():
    args = [a for a in sys.argv[1:] if a != ""]
    creds_override = None
    if "--creds" in args:
        i = args.index("--creds"); creds_override = args[i+1]; del args[i:i+2]
    if len(args) >= 2 and args[0] == "url":
        print(make_url(args[1], creds_override))
    elif len(args) >= 3 and args[0] == "exchange":
        exchange(args[1], args[2], creds_override)
    else:
        print(__doc__); sys.exit(1)

if __name__ == "__main__":
    main()
