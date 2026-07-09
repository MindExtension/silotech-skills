---
name: autonomous-loop
description: Set up and launch a self-driving "loop engineering" harness that lets an agent push a project toward completion autonomously by orienting, picking the next task, acting, machine-verifying, and recording state without a human prompting each step. This skill should be used when the user wants an agent to "run the project to the end on its own", "keep working without me", set up an autonomous or self-paced loop, apply loop engineering, or build a Ralph-loop / goal-loop style harness. It generates a project-specific MISSION goal file, discovers real verification gates, seeds a work queue from the project's own task docs, installs safety guardrails (stop-don't-fabricate, no-auto-commit, adversarial verification, explicit termination), and hands back ready-to-paste launch commands. Trigger phrases include autonomous loop, loop engineering, run it to the end, keep going on its own, self-paced agent, paleisk loop, varyk projektą iki galo, autonominis ciklas.
---

# Autonomous Loop

## Overview

Turn a vague "just let the agent finish the project on its own" request into a robust, safe
autonomous loop. The output is a **MISSION goal file** placed in the target project plus the launch
commands to run it. The loop drives itself through five repeating steps - orient → select → act →
verify → record → repeat - and stops only at genuine human-gated decisions, never by fabricating
answers.

This is "loop engineering": the operator stops writing the per-step prompt and instead designs the
*system* that prompts the agent. The hard part is not the loop - it is the harness around it
(verification gates, termination, state, guardrails). This skill installs that harness.

## When to use

Use when the user wants an agent to advance a project autonomously for a long stretch with minimal
intervention. Good fits have a clear, machine-checkable definition of "done" for most work (tests
pass, build compiles, a validator runs). Poor fits are tasks whose success only a human can judge,
or whose blockers are external answers - flag these and scope the loop to the deterministic slice.

## Two modes: plan-only vs. run

The workflow below produces a MISSION goal file. You can stop there, or launch the loop on it.

- **Plan-only mode (default for handoffs and roadmaps).** Run steps 1 to 5, produce the MISSION as a
  standalone planning deliverable, then STOP. You get the three diagrams (loop, task-dependency DAG,
  data flow), a dependency-ordered work queue, the hygiene and blast-radius lists, and a self-checked
  plan - an implementation roadmap a human team can read, estimate, and execute by hand. Nothing is
  built or committed. This is the right mode when the goal is documentation, a roadmap, or an
  estimate for a team that will do the work themselves.
- **Run mode.** After producing the MISSION, hand it to an agent (step 6) that drives the loop to
  completion. Only do this when you actually want the agent to write and verify the code.

Steps 1 to 5 are identical in both modes; run mode just adds step 6. If you only need the plan, say so
up front and do not launch the loop.

## Workflow

Work through these steps in order. Do not skip the discovery steps - a generic harness drifts and
fails; a project-grounded one works.

### 1. Discover the project's reality (before writing anything)

Ground the harness in what actually exists. Find:

- **Verification gates** - the real commands that prove "done": test runner, build, type-check,
  lint, and any project-specific validator. Read the project's `CLAUDE.md` / `README` /
  `package.json` / `Makefile` / CI config for exact invocations. These become the loop's done-signals.
- **Work queue source** - where open work is tracked: a tasks/TODO doc, status doc, GitHub issues,
  `[ ]` checkboxes, a roadmap. The loop reads this each iteration to pick the next item.
- **State files** - where progress/journal lives (status doc, changelog, findings log). The loop
  updates these so state survives context compaction.
- **Project guardrails** - golden rules in `CLAUDE.md` (e.g. "don't commit", "don't touch X",
  validation-only data). Copy these verbatim into the MISSION as non-negotiable rules.
- **Data flow & structure** - trace how truth is produced and consumed: raw inputs → producers /
  scripts → product artifacts → consumers (UI, reports, API). Note which step regenerates state and
  which steps are expensive or wide-blast. This becomes the data-flow diagram and the performance budget.
- **Hygiene baseline** - scan for existing dead or duplicated code *before* adding more: unused
  exports / orphan files, two producers writing the same truth, `TODO|deprecated|legacy|fallback|
  hardcode` markers, a "replaced" path still wired in. Record it so the loop retires cruft instead of
  piling new code on top of it.

If "done" cannot be machine-checked for most of the remaining work, say so plainly and either narrow
the loop to the deterministic subset or recommend against an autonomous loop.

### 2. Generate the MISSION goal file

Copy `assets/MISSION-template.md` into the target project (good paths: `docs/AUTONOMOUS-LOOP.md` or
`.claude/MISSION.md`) and fill every `<…>` placeholder from step 1. The MISSION is the **goal file**:
the loop re-reads it at the start of every iteration, which keeps instructions from getting buried as
context grows. Keep it tight and concrete - real commands, real task sources, real guardrails. Seed
the work queue with a few concrete first targets so the loop has unambiguous starting work. Fill the
§0.1 diagrams and the hygiene / performance / self-check sections too, not just the task list.

### 3. Draw the structure (three diagrams, so the essence never drowns in text)

A long MISSION becomes a wall of prose where the real structure - dependencies, the critical path,
what is done or dead - gets buried, and the loop loses the plot. Counter it with three mermaid diagrams
at the top of the MISSION (§0.1 of the template). They are the map the agent re-reads first:

1. **Loop cycle** - orient → select → act → verify → record as a flowchart, including the gate-fail
   and N-retry branches. Makes the harness legible at a glance.
2. **Task dependency DAG** - one node per work-queue task, edges = "must exist before". Color nodes by
   live status (done / partial / not-started / blocked / human-gated) with a `classDef` block, and name
   the **keystone** (the node that unblocks the most downstream work). This is the essence: the critical
   path becomes visible, so "smallest task first" no longer starves the keystone. The DAG is live state,
   recolored every iteration, not decoration.
3. **Data flow** - inputs → producers → product → consumers, with the regen step and expensive edges
   marked, and any reference/golden shown as validation-only.

Keep them honest: the plan self-check (step 5) verifies node colors match the real checkboxes and code.

### 4. Confirm the guardrails are installed

Every MISSION must encode the six core harness ingredients (detailed in
`references/loop-engineering.md`) plus four that keep a long, additive loop from rotting the repo.
Verify each is present and project-specific, not boilerplate:

1. **Verification gates** - done is *proven*, never self-declared.
2. **Termination condition** - explicit rules for when to stop the whole loop.
3. **Stop-don't-fabricate** - on a missing external answer, record the question and move on; never guess.
4. **Adversarial verification** - a second, skeptical pass from a different angle than the one that did the work.
5. **Error handling** - never leave a half-broken state; after N failed attempts on one gate, log and move on.
6. **State across turns** - truth lives in files, not the chat scroll.

Plus four that keep a long, additive loop healthy:

7. **Legibility** - the three §0.1 diagrams; the essence lives in a map, not buried in prose.
8. **Hygiene / dead code** - a live list of existing dead/duplicate paths AND what each planned change
   makes dead, each retired via a parity gate, never silent deletion. Additive-only loops rot repos.
9. **Performance & cost budget** - expensive/wide-blast steps flagged, surgical-first, a drift guard
   after any wide regen, and a no-progress budget so the loop stops instead of spinning.
10. **Plan self-check** - the plan is verified against reality (step 5), not just the code.

Default guardrails to always include unless the user overrides: **do not `git commit` / `git push`**
(leave changes for human review), **smallest/cheapest work first**, and **stop before any expensive
or destructive action that needs confirmation**.

### 5. Self-verify the plan before handing it back

Run the self-check (§9 of the template) on the MISSION itself, because a plan that lies about its own
state sends the loop in circles: stale checkboxes, a task named in "termination" that isn't in the
queue, a `file:line` reference that has rotted, a second producer shipped without retiring the first.
Confirm: every termination task exists in the queue and as a DAG node; every node color matches the
real checkbox and code; the DAG is acyclic and the keystone is named; every gate command runs as
written; every file:line reference still resolves; the hygiene lists are current. Fix drift here, then
hand back. Re-run this periodically during a long loop, not only at setup.

### 6. Hand back launch commands

Give the user both options and a recommendation:

- **Fresh session (recommended - clean context):** open a new agent session in the most autonomous
  permission mode; first message tells it to read the MISSION file and execute it as an autonomous
  loop until the termination condition, keeping the §0.1 diagrams in sync (recolor the task DAG each
  iteration), pausing only for the confirmation-gated cases.
- **`/loop` self-paced (same session, context-resilient):** run `/loop` with no interval, pointing it
  at the MISSION file. The self-pacing variant re-invokes across iterations and survives context
  compaction.

Recommend the fresh session when the current session is already large (clean context = better loop
performance), and `/loop` when durability across context limits matters more.

### Optional: actually launch it

If the user explicitly asks to launch the loop now (not just prepare it), use the `loop` skill with
no interval and the MISSION file as the prompt. Do not auto-launch a long autonomous run without the
user's explicit go - it is token-heavy and the user owns that decision.

## Resources

- `references/loop-engineering.md` - the concepts: the two loop types (deterministic vs
  non-deterministic), the five loop steps, the six harness ingredients in depth, legibility (why the
  plan must be a map, not a wall of text) and mermaid conventions, hygiene as a first-class loop
  concern, the performance & flow budget, verifying the plan itself, expert techniques (adversarial
  builder/verifier, fresh context, anti-slop), and the common failure modes to avoid. Load when
  designing a non-trivial loop or when the user wants the *why*.
- `assets/MISSION-template.md` - the fill-in-the-blanks goal file to copy into the target project.
