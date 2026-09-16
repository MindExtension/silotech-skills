# Tracker: local markdown (default)

No accounts, no tooling, works in any folder. The map and its tickets are plain files in the working
repository, so they are readable by a human, diffable in git, and visible to every later session.

## Layout

```
wayfinder/<effort-slug>/
├── map.md                       the map body
└── tickets/
    ├── 01-where-icons-come-from.md
    ├── 02-pricing-model.md
    └── 03-supplier-shortlist.md
```

One directory per effort. Tickets are numbered from `01`, never combined into one file.

## Ticket file

```markdown
# 02 - Pricing model for the second tier

Type: grilling
Decider: human
Status: open
Blocked by: 01

## Question

<the decision this ticket resolves>
```

- `Type` is one of `research`, `prototype`, `grilling`, `task`.
- `Decider` is `human` or `agent`, and defaults to `human`.
- `Status` is one of `open`, `claimed`, `resolved`.
- `Blocked by` lists ticket numbers, or is omitted when nothing blocks it.

## Operations

- **Frontier**: scan `tickets/` for files that are `open`, unclaimed, and whose every `Blocked by`
  ticket is `resolved`. Lowest number wins.
- **Claim**: set `Status: claimed` and save the file **before** any work, so a parallel session skips it.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append one
  line (gist plus relative link) to **Decisions so far** in `map.md`.
- **Out of scope**: set `Status: resolved` with an `## Answer` of "Out of scope", and put the one-line
  reason in the map's **Out of scope** section instead of **Decisions so far**.
- **Supersede**: when a new answer contradicts a resolved ticket, leave that ticket resolved, prefix its
  line in **Decisions so far** with `Superseded by <new ticket name>`, and reopen or replace whatever
  depended on it.
- **New tickets**: create the files first, then wire `Blocked by` in a second pass, once the numbers
  exist.

## Assets

Anything produced while resolving a ticket (a prototype, a research note, a quote, a spreadsheet) lives
beside the map as a file, or wherever the repository already keeps such things. The ticket links it. It
is never pasted into the ticket body.
