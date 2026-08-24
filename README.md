# SiloTech Skills

A small, public collection of [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
built at [SiloTech](https://silotech.xyz) (UAB Silo Tech) and used in real client work. Each skill is a
self-contained folder you can drop into Claude Code or any agent runtime that reads the Agent Skills format.

Skills are shared here as-is, one item per folder, so you can read them, learn from them, and adapt them.

## Skills

| Skill | What it does |
|---|---|
| [`product-transcreation`](./product-transcreation) | A research-led product localization harness. It recovers the human and product truth before writing, researches how native speakers actually express the same ideas, rebuilds each locale around its own voice, runs a separate spoken-language pass to remove translated sentence structures, and independently verifies terminology, meaning, user agency, interface constraints, and source evidence. Designed for landing pages, onboarding, interfaces, pricing, and product narratives that must sound conceived in the target language, not translated from a template. |
| [`refine`](./refine) | A generalized, domain-agnostic iterative-improvement harness. Turns "make this better" into a disciplined loop: frame the purpose, decompose into independently-improvable units, derive the evaluation lenses that purpose demands, observe the real rendered output, improve every unit in parallel, verify, iterate, and accumulate lessons so it gets better each run. Works on a slide deck, a document, a codebase, or an analysis. |
| [`autonomous-loop`](./autonomous-loop) | A generalized "loop engineering" harness. Turns "just let the agent finish the project on its own" into a robust MISSION goal file: it discovers the project's real verification gates and work queue, draws three live diagrams (the loop, the task-dependency DAG, the data flow), installs safety guardrails (stop-don't-fabricate, no-auto-commit, adversarial verification, hygiene, explicit termination), and self-checks the plan. Run it plan-only to produce an implementation roadmap a team can estimate and execute, or hand the MISSION to an agent to drive to completion. |
| [`launch-readiness`](./launch-readiness) | A multi-agent "does this look live?" review. Fans out 10-15 perspective subagents (placeholder copy, test data, default assets, SEO leftovers, dead links, test-mode payments, raw i18n keys, debug routes, legal gaps, funnel walkthrough) over the codebase and the deployed product in several discovery rounds, adversarially verifies every finding, and writes a stable-numbered action plan the user triages and hands to `autonomous-loop` for fixing. The detector and planner that sits in front of the other two skills. |
| [`workflow-edgecase-audit`](./workflow-edgecase-audit) | An evidence-first, read-only workflow bug hunt. Maps end-to-end state transitions, assigns up to 10 independent audit zones, probes concurrency, idempotency, retries, timeouts, auth and integration boundaries, then adversarially revalidates and deduplicates every finding. Includes a deterministic workflow inventory helper and works in both Claude and Codex Agent Skills harnesses. |
| [`feature-factory`](./feature-factory) | A conductor that turns ONE natural-language feature request into a review-ready PR without a human writing the code, keeping a human at every decision that is genuinely theirs. Sequences the other skills (`autonomous-loop`, `refine`, plus arch-check and a shared adversarial-audit workflow) through seven gated stages: intake, CTO triage, plan+spec (with an idea tournament), build, adversarial test, UX review, delivery. Mechanical safety barriers (no push/deploy credentials in the run's worktree, path and secret guards, all external text treated as untrusted data) mean the safety model lives in mechanism, not in asking the model nicely. It never merges or deploys, and routes anything touching auth, billing, RLS, migrations, or other invariants to a human as a proposal instead of building it. |
| [`gmail-multi-account`](./gmail-multi-account) | Connect any number of Gmail mailboxes to one agent: search and read mail, download attachments (e.g. supplier invoices for bookkeeping), and create reply drafts in the right mailbox and thread. One shared OAuth Desktop client, one token file per mailbox, three stdlib-only Python scripts, and a browser consent flow that works even on headless machines. Drafts only - the human always presses Send. |
| [`plain-answers`](./plain-answers) | A plain-language output setup that fixes jargon-dense, wall-of-text agent replies. A Claude Code output style (lead with the answer, short sentences, no unexplained acronyms, length matched to the question) plus an equivalent `AGENTS.md` block for Codex. Ships with install steps and the reasoning for why an output style beats the same rule in CLAUDE.md. |
| [`bro`](./bro) | One-line skill: restate the last answer in plain human language with zero jargon, at a third of the length, keeping every decision and number that mattered. |
| [`quick`](./quick) | One-line skill: compress the last answer into the N most important takeaways (default 3), numbered, most important first; an open question for the user is always number 1. |

## Which one, when

- You have product copy in one or more languages and want it to sound **native, human, and evidence-backed**, while preserving product truth and interface constraints -> `product-transcreation`.
- You have a thing (deck, doc, codebase, analysis) and want it **better** -> `refine`.
- You have a project and want an agent to **drive it to done** (or produce the roadmap for that) -> `autonomous-loop`.
- You have a product that is about to go (or just went) **live** and want to know what still smells unfinished -> `launch-readiness`, then hand its plan to `autonomous-loop`, and polish individual artifacts with `refine`.
- You have a codebase with green happy paths but want to find **workflow and state-transition bugs** -> `workflow-edgecase-audit`, then fix accepted findings through your normal implementation workflow.
- You have **one well-scoped feature request** and want an agent to carry it from intake to a review-ready PR (with human gates on every real decision) -> `feature-factory`, which drives `autonomous-loop` for the build and `refine` for the copy/screens.
- You have **several Gmail inboxes** and want one agent to read them all, pull the invoices, and prepare replies -> `gmail-multi-account`.
- Your agent's replies are **jargon-dense walls of text** -> install `plain-answers` (the output style), then use `bro` and `quick` to shorten on demand.

## The `refine` super-prompt

`refine` is a full skill (an orchestrator plus a parallel workflow and a growing lessons log), but its
core is a single self-contained prompt that runs the whole loop with or without a workflow engine. It is
the distilled synthesis of five well-studied patterns:

- **Self-Refine** (Madaan et al., 2023) - generate, critique, refine, iterate on the model's own feedback.
- **Evaluator-optimizer + orchestrator-workers + parallelization** (Anthropic, *Building Effective Agents*).
- **Reflexion** (Shinn et al., 2023) - an episodic memory of past mistakes fed back in as verbal rules.
- **LLM-as-judge, multi-perspective rubric panels** - lenses derived from the artifact's purpose.
- **Design-QA field lessons** - judge the rendered reality, not the source; one writer per unit; harvest the lesson before the re-pass.

Read it in [`refine/references/super-prompt.md`](./refine/references/super-prompt.md).

## Install

Clone this repository, then copy a skill folder into your skills directory:

```bash
# First install for Claude Code, user-level
mkdir -p ~/.claude/skills
cp -R refine ~/.claude/skills/

# First install for Codex, user-level
mkdir -p ~/.codex/skills
cp -R refine ~/.codex/skills/

# Update an existing Claude Code or Codex installation without nesting folders
cp -R refine/. ~/.claude/skills/refine/
cp -R refine/. ~/.codex/skills/refine/
```

Replace `refine` with any folder in this repository. These paths are tested with Claude Code and
Codex; invoke the installed skill by intent or by name.

## License

[MIT](./LICENSE). Use it, adapt it, ship it.
