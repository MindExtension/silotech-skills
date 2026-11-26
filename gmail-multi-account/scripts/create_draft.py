#!/usr/bin/env python3
"""Create a Gmail DRAFT (never sends) in any connected mailbox, with optional
attachments and optional in-thread reply threading. The human reviews the
draft in Gmail and presses Send themselves.

Reads a JSON spec (file path or inline string) describing the draft.

Spec fields:
  account      (required)  the mailbox, e.g. "you@example.com"
  to           list[str]   primary recipients (plain addresses)
  cc           list[str]
  bcc          list[str]
  subject      str
  body         str         plain-text body
  attachments  list[str]   file paths to attach
  threadId     str         Gmail threadId to attach the draft to (keeps it in-thread)
  replyToId    str         messageId being replied to (sets In-Reply-To/References)

Usage:
  python3 create_draft.py spec.json
  python3 create_draft.py '{"account":"you@example.com","to":["x@y.z"],"subject":"..","body":".."}'

Config dir: $GMAIL_ACCOUNTS_DIR or ~/.config/gmail-accounts
Needs google-token.<account>.json there (create it with get_token.py).
"""
import sys, os, json, base64, urllib.request, urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

CFG = os.environ.get("GMAIL_ACCOUNTS_DIR") or os.path.expanduser("~/.config/gmail-accounts")

def access_token(account):
    # Find a token file that has (or can refresh into) gmail.compose.
    candidates = [f"{CFG}/google-token.{account}.json", f"{CFG}/google-token-compose.{account}.json"]
    for tf in candidates:
        if not os.path.exists(tf):
            continue
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
        at = json.load(urllib.request.urlopen(urllib.request.Request(
            c.get("token_uri", "https://oauth2.googleapis.com/token"), data=data)))["access_token"]
        info = json.load(urllib.request.urlopen(f"https://oauth2.googleapis.com/tokeninfo?access_token={at}"))
        if "gmail.compose" in info.get("scope", "") or "gmail.modify" in info.get("scope", "") or "mail.google.com" in info.get("scope", ""):
            return at, tf
    raise SystemExit(f"No gmail.compose-capable token for {account}. Run get_token.py first.")

def build_raw(spec, at, account):
    msg = MIMEMultipart()
    msg["From"] = account
    if spec.get("to"):  msg["To"]  = ", ".join(spec["to"])
    if spec.get("cc"):  msg["Cc"]  = ", ".join(spec["cc"])
    if spec.get("bcc"): msg["Bcc"] = ", ".join(spec["bcc"])
    msg["Subject"] = spec.get("subject", "")
    # Threading headers for a proper reply.
    if spec.get("replyToId"):
        m = json.load(urllib.request.urlopen(urllib.request.Request(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{spec['replyToId']}?format=metadata&metadataHeaders=Message-ID&metadataHeaders=References",
            headers={"Authorization": f"Bearer {at}"})))
        h = {x["name"].lower(): x["value"] for x in m["payload"]["headers"]}
        if h.get("message-id"):
            msg["In-Reply-To"] = h["message-id"]
            msg["References"] = (h.get("references", "") + " " + h["message-id"]).strip()
    msg.attach(MIMEText(spec.get("body", ""), "plain", "utf-8"))
    for path in spec.get("attachments", []) or []:
        sub = "pdf" if path.lower().endswith(".pdf") else "octet-stream"
        with open(path, "rb") as f:
            part = MIMEApplication(f.read(), _subtype=sub)
        part.add_header("Content-Disposition", "attachment", filename=os.path.basename(path))
        msg.attach(part)
    return base64.urlsafe_b64encode(msg.as_bytes()).decode()

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    arg = sys.argv[1]
    spec = json.load(open(arg)) if os.path.exists(arg) else json.loads(arg)
    account = spec["account"]
    at, tf = access_token(account)
    raw = build_raw(spec, at, account)
    payload = {"message": {"raw": raw}}
    if spec.get("threadId"):
        payload["message"]["threadId"] = spec["threadId"]
    req = urllib.request.Request("https://gmail.googleapis.com/gmail/v1/users/me/drafts",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {at}", "Content-Type": "application/json"}, method="POST")
    resp = json.load(urllib.request.urlopen(req))
    print("DRAFT CREATED in", account, "(token:", os.path.basename(tf) + ")")
    print("draft id:", resp.get("id"))
    print("message id:", resp.get("message", {}).get("id"))
    print("thread id:", resp.get("message", {}).get("threadId"))

if __name__ == "__main__":
    main()
