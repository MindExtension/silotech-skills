# Silotech Skills

A small, public collection of [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
built at [Silotech](https://silotech.xyz) (UAB Silotech) and used in real client work. Each skill is a
self-contained folder you can drop into Claude Code or any agent runtime that reads the Agent Skills format.

Skills are shared here as-is, one item per folder, so you can read them, learn from them, and adapt them.

## Skills

| Skill | What it does |
|---|---|
| [`workflow-edgecase-audit`](./workflow-edgecase-audit) | An evidence-first, read-only workflow bug hunt. Maps end-to-end state transitions, assigns up to 10 independent audit zones, probes concurrency, idempotency, retries, timeouts, auth and integration boundaries, then adversarially revalidates and deduplicates every finding. Includes a deterministic workflow inventory helper and works in both Claude and Codex Agent Skills harnesses. |
| [`extraction-chain-audit`](./extraction-chain-audit) | Error prevention for complex analytical workflows: chains that turn messy domain sources (documents, drawings, scans, forms, model outputs) into a structured domain model, calculations and aggregated totals, in any domain (engineering, law, finance, health, insurance). Six modes: QUICK SCAN, BUILD, PREFLIGHT before a long or paid run, AUDIT before release, DESIGN REVIEW of a written design, and INCIDENT, which turns one wrong number into a class and a sweep of every sibling. Built on a cheapest-earliest gate ladder, HAZOP and STPA hazard sweeps, metamorphic relations, "guard the guards" seeded faults against every existing check, and a capture-recapture estimate of the bugs still hiding. Every result is PASS, FAIL or NOT-CHECKED, pinned to one run, and an empty read is never a pass. Two stdlib-only helper scripts with self-tests. Derived from a production history where most failed runs were catchable by a one-minute preflight. |
| [`gmail-multi-account`](./gmail-multi-account) | Connect any number of Gmail mailboxes to one agent: search and read mail, download attachments (e.g. supplier invoices for bookkeeping), and create reply drafts in the right mailbox and thread. One shared OAuth Desktop client, one token file per mailbox, three stdlib-only Python scripts, and a browser consent flow that works even on headless machines. Drafts only - the human always presses Send. |
| [`plain-answers`](./plain-answers) | A plain-language output setup that fixes jargon-dense, wall-of-text agent replies. A Claude Code output style (lead with the answer, short sentences, no unexplained acronyms, length matched to the question) plus an equivalent `AGENTS.md` block for Codex. Ships with install steps and the reasoning for why an output style beats the same rule in CLAUDE.md. |
| [`bro`](./bro) | One-line skill: restate the last answer in plain human language with zero jargon, at a third of the length, keeping every decision and number that mattered. |
| [`quick`](./quick) | One-line skill: compress the last answer into the N most important takeaways (default 3), numbered, most important first; an open question for the user is always number 1. |

## Which one, when

- You have a codebase with green happy paths but want to find **workflow and state-transition bugs** -> `workflow-edgecase-audit`, then fix accepted findings through your normal implementation workflow.
- You have a pipeline that **extracts, computes and aggregates** (quantities from drawings, clauses from contracts, cases from reports, figures from filings) and runs keep failing late, totals look wrong, or you are about to ship it -> `extraction-chain-audit` (PREFLIGHT before every long run, AUDIT before release, INCIDENT after each wrong number). Use `workflow-edgecase-audit` for state, retry and concurrency bugs in app workflows; the two complement each other.
- You have **several Gmail inboxes** and want one agent to read them all, pull the invoices, and prepare replies -> `gmail-multi-account`.
- Your agent's replies are **jargon-dense walls of text** -> install `plain-answers` (the output style), then use `bro` and `quick` to shorten on demand.

This collection holds light, self-contained skills only. Long autonomous development loops are not published here.

## Install

Clone this repository, then copy a skill folder into your skills directory:

```bash
# First install for Claude Code, user-level
mkdir -p ~/.claude/skills
cp -R quick ~/.claude/skills/

# First install for Codex, user-level
mkdir -p ~/.codex/skills
cp -R quick ~/.codex/skills/

# Update an existing Claude Code or Codex installation without nesting folders
cp -R quick/. ~/.claude/skills/quick/
cp -R quick/. ~/.codex/skills/quick/
```

Replace `quick` with any folder in this repository. These paths are tested with Claude Code and
Codex; invoke the installed skill by intent or by name.

## License

[MIT](./LICENSE). Use it, adapt it, ship it.
