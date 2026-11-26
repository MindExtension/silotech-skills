---
name: gmail-multi-account
description: >
  Manage MANY Gmail mailboxes from one agent: search and read mail, pull attachments
  (e.g. invoices for bookkeeping) and create reply drafts in any of the connected
  accounts. One shared Google OAuth Desktop client, one token file per mailbox,
  three dependency-free Python scripts (stdlib only). Includes the full one-time
  Google Cloud setup walkthrough and a consent flow that works even on a headless
  or remote machine (code-copy-back, no loopback listener). Drafts only - the agent
  never sends; the human reviews in Gmail and presses Send. Use when a user says
  "connect my mailboxes", "collect the invoices from my inboxes", "answer this from
  my other account", or when a Gmail action fails with a missing/expired token.
metadata:
  type: skill
---

# gmail-multi-account

Give an agent controlled access to any number of Gmail mailboxes: **read + search +
download attachments** and **create drafts**. Never send. The human stays the sender.

Typical jobs this enables:
- sweep several inboxes for supplier invoices (`has:attachment filename:pdf newer_than:31d`)
  and download the PDFs for bookkeeping,
- triage what needs answering across accounts,
- prepare reply drafts in the right mailbox, threaded into the right conversation.

## How it is wired

- **One Google Cloud OAuth client (type "Desktop app") is shared by ALL mailboxes.**
  You create it once, in one Google Cloud project, no matter how many mailboxes follow.
- **Each mailbox gets its own token file**, created by a one-time browser consent.
- Everything lives in one config dir: `$GMAIL_ACCOUNTS_DIR` or `~/.config/gmail-accounts/`
  - `google-credentials.json` - the shared Desktop OAuth client (downloaded once)
  - `google-token.<email>.json` - one per connected mailbox
- Scripts are plain Python 3 stdlib (no pip installs): `get_token.py`, `read_mail.py`, `create_draft.py`.
- Scopes requested: `gmail.readonly` + `gmail.compose`. That allows reading, searching,
  downloading attachments and creating drafts. It does NOT allow deleting mail, and the
  scripts never call send.

## A. One-time Google Cloud setup (once, not per mailbox)

If you are an agent doing this for a user: you run the commands, the user does the
browser steps. Tell them each browser step in simple words, in their language.

1. Go to https://console.cloud.google.com/ signed in as the user's MAIN Google account,
   create a project (name it e.g. `mail-agent`).
2. **Enable the Gmail API**: APIs & Services -> Library -> search "Gmail API" -> Enable.
3. **OAuth consent screen** (APIs & Services -> OAuth consent screen):
   - User type: **External**, fill only the required fields (app name, support email).
   - Under **Audience / Test users: add EVERY mailbox address you plan to connect.**
     A mailbox that is not listed as a test user cannot complete consent while the
     app is in Testing mode.
   - Note on token lifetime: while the app is in **Testing** mode, refresh tokens
     expire after ~7 days, so every mailbox needs re-consent weekly. For a
     personal/long-lived setup, switch the app to **In production** (Publish app).
     Google will show an "unverified app" warning during consent (expected - it is
     your own app; verification is not required for personal use), but refresh
     tokens then live until revoked.
4. **Create the OAuth client**: APIs & Services -> Credentials -> Create credentials ->
   OAuth client ID -> Application type **Desktop app**. Download the JSON and save it as:
   ```bash
   mkdir -p ~/.config/gmail-accounts
   mv ~/Downloads/client_secret_*.json ~/.config/gmail-accounts/google-credentials.json
   chmod 600 ~/.config/gmail-accounts/google-credentials.json
   ```

## B. Connect a mailbox (repeat per mailbox, ~2 min each)

This is the **code-copy-back** flow. It works from any browser on any device (the
machine running the scripts never needs to open a browser), which is why there is
no loopback listener to babysit.

1. Generate the consent URL:
   ```bash
   python3 scripts/get_token.py url the.mailbox@gmail.com
   ```
2. Give the URL to the user. Tell them, verbatim and simply:
   - Open it and sign in as **exactly that mailbox** (not your main account -
     check the account picker).
   - On the "Google hasn't verified this app" screen: **Advanced -> Go to <app> -> Continue**
     (expected - it is your own app).
   - The browser then lands on a page saying **"This site can't be reached"** at
     `localhost:8765`. **That is normal and means it worked.** Do not close it.
   - **Copy the ENTIRE address from the browser's address bar** (it contains `?code=...`)
     and paste it back.
3. Exchange the pasted URL for a saved token:
   ```bash
   python3 scripts/get_token.py exchange the.mailbox@gmail.com "<pasted localhost URL>"
   ```
   The code is single-use and expires in ~10 minutes - exchange promptly. If it
   expired, just generate a fresh URL and repeat.
4. Verify: `python3 scripts/read_mail.py search the.mailbox@gmail.com "newer_than:7d" --max 3`

Repeat for every mailbox. Same shared credentials file, one token file per mailbox.

## C. Read, search, pull attachments

```bash
# what's new
python3 scripts/read_mail.py search box@gmail.com "in:inbox newer_than:7d" --max 20

# find invoices across the last month
python3 scripts/read_mail.py search box@gmail.com "has:attachment filename:pdf newer_than:31d"

# read a whole conversation
python3 scripts/read_mail.py thread box@gmail.com <threadId>

# download a message's attachments (e.g. the invoice PDFs)
python3 scripts/read_mail.py attachments box@gmail.com <messageId> --out ./invoices/2026-07
```

Queries use normal Gmail search syntax (`from:`, `subject:`, `newer_than:`, `has:attachment`, ...).

## D. Create a draft (never send)

Verify content first: take recipient addresses from real message headers (not from
notes), and if replying, fetch `threadId` + the last `messageId` via `read_mail.py`.

```bash
cat > /tmp/draft.json <<'JSON'
{
  "account": "box@gmail.com",
  "to": ["client@example.com"],
  "subject": "Re: Original subject",
  "body": "Plain-text reply body...",
  "attachments": ["/path/to/file.pdf"],
  "threadId": "<threadId of the conversation>",
  "replyToId": "<messageId being replied to>"
}
JSON
python3 scripts/create_draft.py /tmp/draft.json
```

Omit `threadId`/`replyToId` for a fresh email. Then tell the user the draft is
waiting in that mailbox's **Drafts** folder for review and manual Send.

Recommended house rule for agent-written drafts: end the body, after the signature,
with a separate marker line such as "Drafted by <name>'s AI assistant" (in the
user's language), so the human always notices it is machine-prepared and edits or
deletes the marker before sending.

## Gotchas

- `invalid_grant` on refresh = the token expired or was revoked. In Testing mode this
  happens every ~7 days by design. Re-run step B for that mailbox, or publish the app
  to production to stop the weekly expiry.
- The consent must be completed while signed in as the exact target mailbox; with many
  Gmail accounts in one browser, the account picker matters. A wrong-account token
  shows up immediately: `read_mail.py search` returns someone else's mail.
- Google Workspace mailboxes (custom-domain accounts managed by an organization) may
  block third-party OAuth apps. If the "Go to app" step is refused by policy, that
  mailbox cannot be connected until the Workspace admin allowlists your OAuth client
  ID. Report it; do not retry in a loop.
- Token files grant real mailbox access: keep the config dir out of git and backups
  you share, permissions `600`.
- The scripts intentionally have no `send` command. If a user asks the agent to send,
  the answer is: the draft is ready in Gmail, sending stays a human action.
