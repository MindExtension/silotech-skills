#!/usr/bin/env python3
"""Read/search Gmail for any connected mailbox (readonly - never modifies anything).

Usage:
  python3 read_mail.py search <account_email> "<gmail query>" [--max N]
      -> lists matching messages: id, threadId, date, from, subject, snippet
         (query uses normal Gmail search syntax, e.g.
          'has:attachment filename:pdf newer_than:30d' or 'from:billing@vendor.com')

  python3 read_mail.py thread <account_email> <threadId>
      -> prints every message in the thread with its plain-text body

  python3 read_mail.py message <account_email> <messageId>
      -> prints one message: headers, plain-text body, attachment list

  python3 read_mail.py attachments <account_email> <messageId> [--out <dir>]
      -> downloads all attachments of the message (default dir: ./attachments)

Config dir: $GMAIL_ACCOUNTS_DIR or ~/.config/gmail-accounts
Needs google-token.<account_email>.json there (create it with get_token.py).
"""
import sys, os, json, base64, urllib.request, urllib.parse

CFG = os.environ.get("GMAIL_ACCOUNTS_DIR") or os.path.expanduser("~/.config/gmail-accounts")
API = "https://gmail.googleapis.com/gmail/v1/users/me"

def access_token(account):
    token_files = [f"{CFG}/google-token.{account}.json",
                   f"{CFG}/google-token-compose.{account}.json"]
    tf = next((t for t in token_files if os.path.exists(t)), None)
    if not tf:
        raise SystemExit(f"No token for {account} in {CFG}. Run get_token.py first.")
    tok = json.load(open(tf))
    cred_candidates = [f"{CFG}/google-credentials.{account}.json", f"{CFG}/google-credentials.json"]
    cred_path = next((p for p in cred_candidates if os.path.exists(p)), None)
    if not cred_path and os.path.isdir(CFG):
        cred_path = next((f"{CFG}/{c}" for c in sorted(os.listdir(CFG))
                          if c.startswith("google-credentials") and c.endswith(".json")), None)
    c = json.load(open(cred_path)); c = c.get("installed") or c.get("web") or c
    data = urllib.parse.urlencode({
        "client_id": c["client_id"], "client_secret": c["client_secret"],
        "refresh_token": tok["refresh_token"], "grant_type": "refresh_token",
    }).encode()
    try:
        return json.load(urllib.request.urlopen(urllib.request.Request(
            c.get("token_uri", "https://oauth2.googleapis.com/token"), data=data)))["access_token"]
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        if "invalid_grant" in body:
            raise SystemExit(f"Token for {account} expired/revoked (invalid_grant). "
                             "Re-run the get_token.py consent flow for this mailbox.")
        raise

def get(at, path):
    return json.load(urllib.request.urlopen(urllib.request.Request(
        f"{API}/{path}", headers={"Authorization": f"Bearer {at}"})))

def header(msg, name):
    for h in msg.get("payload", {}).get("headers", []):
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""

def walk_parts(part, out):
    mime = part.get("mimeType", "")
    body = part.get("body", {})
    if part.get("filename") and body.get("attachmentId"):
        out["attachments"].append({"filename": part["filename"], "mimeType": mime,
                                   "attachmentId": body["attachmentId"], "size": body.get("size")})
    elif mime == "text/plain" and body.get("data"):
        out["text"].append(base64.urlsafe_b64decode(body["data"]).decode(errors="replace"))
    for p in part.get("parts", []) or []:
        walk_parts(p, out)

def render(msg):
    out = {"text": [], "attachments": []}
    walk_parts(msg.get("payload", {}), out)
    print(f"=== message {msg['id']} (thread {msg.get('threadId')})")
    for h in ("Date", "From", "To", "Cc", "Subject"):
        v = header(msg, h)
        if v:
            print(f"{h}: {v}")
    if out["attachments"]:
        print("Attachments:", ", ".join(f"{a['filename']} ({a['size']}B)" for a in out["attachments"]))
    print("---")
    print("\n".join(out["text"]).strip() or f"(no text/plain body; snippet: {msg.get('snippet','')})")
    print()
    return out

def cmd_search(account, query, maxn):
    at = access_token(account)
    q = urllib.parse.urlencode({"q": query, "maxResults": maxn})
    ids = get(at, f"messages?{q}").get("messages", []) or []
    if not ids:
        print("(no matches)"); return
    for m in ids:
        msg = get(at, f"messages/{m['id']}?format=metadata&metadataHeaders=Date&metadataHeaders=From&metadataHeaders=Subject")
        print(f"{m['id']}\tthread:{msg.get('threadId')}\t{header(msg,'Date')}\t{header(msg,'From')}\t{header(msg,'Subject')}")
        print(f"\t{msg.get('snippet','')}")

def cmd_thread(account, thread_id):
    at = access_token(account)
    for msg in get(at, f"threads/{thread_id}?format=full").get("messages", []):
        render(msg)

def cmd_message(account, msg_id):
    at = access_token(account)
    render(get(at, f"messages/{msg_id}?format=full"))

def cmd_attachments(account, msg_id, outdir):
    at = access_token(account)
    msg = get(at, f"messages/{msg_id}?format=full")
    out = {"text": [], "attachments": []}
    walk_parts(msg.get("payload", {}), out)
    if not out["attachments"]:
        print("(no attachments)"); return
    os.makedirs(outdir, exist_ok=True)
    for a in out["attachments"]:
        data = get(at, f"messages/{msg_id}/attachments/{a['attachmentId']}")["data"]
        safe = os.path.basename(a["filename"]) or "attachment.bin"
        path = os.path.join(outdir, safe)
        with open(path, "wb") as f:
            f.write(base64.urlsafe_b64decode(data))
        print("SAVED:", path)

def main():
    args = [a for a in sys.argv[1:] if a != ""]
    maxn, outdir = 20, "./attachments"
    if "--max" in args:
        i = args.index("--max"); maxn = int(args[i+1]); del args[i:i+2]
    if "--out" in args:
        i = args.index("--out"); outdir = args[i+1]; del args[i:i+2]
    if len(args) >= 3 and args[0] == "search":
        cmd_search(args[1], args[2], maxn)
    elif len(args) >= 3 and args[0] == "thread":
        cmd_thread(args[1], args[2])
    elif len(args) >= 3 and args[0] == "message":
        cmd_message(args[1], args[2])
    elif len(args) >= 3 and args[0] == "attachments":
        cmd_attachments(args[1], args[2], outdir)
    else:
        print(__doc__); sys.exit(1)

if __name__ == "__main__":
    main()
