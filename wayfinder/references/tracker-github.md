# Tracker: GitHub Issues

Use this only when the repository already runs its work on GitHub Issues and the human wants the map
there. Otherwise use [tracker-local.md](tracker-local.md). All operations go through the `gh` CLI, which
infers the repository from the clone it runs inside.

## Map and tickets

- **Map**: one issue labelled `wayfinder:map`, holding the Destination / Notes / Decisions so far /
  Not yet specified / Out of scope body.
  `gh issue create --label wayfinder:map --title "..." --body "..."` (heredoc for the body).
- **Ticket**: an issue linked to the map as a **sub-issue** (`gh api` on the sub-issues endpoint).
  Where sub-issues are not enabled, add the ticket to a task list in the map body and put
  `Part of #<map>` at the top of the ticket body.
  Label it `wayfinder:<type>`, one of `research`, `prototype`, `grilling`, `task`.
- **Blocking**: GitHub's native issue dependencies, which is what makes the frontier visible in the
  GitHub UI without opening the map:
  `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`,
  where `<blocker-db-id>` is the blocker's numeric **database id**
  (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`), not its `#number` and not its `node_id`.
  Where dependencies are unavailable, fall back to a `Blocked by: #<n>, #<n>` line at the top of the
  ticket body.

## Operations

- **Frontier**: list the map's open sub-issues, drop any with an open blocker
  (`issue_dependencies_summary.blocked_by > 0`, or an open issue in the `Blocked by` line) and any with
  an assignee. First in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me`, the session's first write, before any work.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, then `gh issue close <n>`, then append the
  one-line gist plus link to the map's **Decisions so far**.
- **Out of scope**: close the ticket, and put the one-line reason in the map's **Out of scope** section
  instead of **Decisions so far**.
- **Read a ticket**: `gh issue view <n> --comments`.

## Assets

Anything produced while resolving a ticket lives as a file, a branch, or a link, and the issue points at
it. Do not paste large artifacts into issue bodies; GitHub has a character limit and the issue is an
index, not a store.
