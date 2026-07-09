# Loop engineering - concepts and harness design

Reference for designing autonomous agent loops. Load when building a non-trivial loop or when
explaining the rationale behind the MISSION harness.

## The core shift

Prompt engineering: the operator writes the right series of instructions to drive the agent, and is
the loop - checking output, finding issues, re-prompting between every step.

Loop engineering: the operator designs the *system* that prompts the agent. Define the end goal; the
agent figures out the steps, corrects itself, and works around problems until it reaches the goal.
The operator's role does not shrink - it concentrates into defining the goal and the gates that
decide when work is truly done. The judgment moves from "what should it do next" to "what proves it
succeeded, and where must it stop and ask".

This only became practical once models could sustain long, multi-step tasks. The leverage now comes
from preparing the project to run over the long term, not from hand-walking the agent through each
step. But capability raises the stakes: an unsupervised loop with weak gates produces confident,
plausible, wrong work faster. The harness is what makes capability safe.

## The two loop types

**Deterministic loop** - "done" is machine-checkable: tests pass, code compiles, a validator returns
within tolerance, a schema validates. The end goal is unambiguous, so the agent knows exactly when
it may mark a task complete. These are the strong, safe candidates for autonomy.

**Non-deterministic loop** - "done" needs human judgment: a UI looks right, a feature behaves
sensibly, prose reads well. There is no clean machine verdict. To run these autonomously, manufacture
a verifier: a separate agent (ideally a *different model* than the builder) that critiques against an
explicit rubric, forming an adversarial builder/verifier pair. Without a real verifier, a
non-deterministic loop drifts toward generic, low-quality output ("AI slop"). When even an
adversarial verifier cannot stand in for human taste, keep the human in the loop and do not automate
that judgment.

## The five loop steps

Every iteration runs the same cycle:

1. **Orient** - check the current state of the project. Re-read the goal file and status. From that,
   decide what the next action should be.
2. **Select** - pick one concrete next task (smallest useful unit, deterministic first).
3. **Act** - do the work: call tools, edit files, run commands.
4. **Verify** - gather real feedback (test output, build result, validator number, screenshot) and
   turn it into a verdict via the verification gate.
5. **Record** - write progress and findings to state files; mark the task done only if the gate
   passed. Then repeat.

Prompt engineering only ever controls step 3 (the decision). Loop engineering owns all five.

## The six harness ingredients

A loop that works gets all six right. Each exists because of a specific failure it prevents.

1. **Context management.** What goes into context each turn determines what the agent knows. Even
   with huge context windows, the system prompt and instructions get buried under recent tool output
   as the conversation grows, and attention pulls toward whatever is most recent. Counter it: keep
   the goal in an external **goal file** the agent re-reads every iteration, and start from clean
   context when possible.

2. **Feedback quality.** Feedback is the signal that tells the agent how it did - test output, a
   validator's number, a screenshot of the UI. Whatever form it takes, it must be concrete and
   trustworthy; the agent's next move is only as good as the feedback it reads. Vague or absent
   feedback is the root of most loop drift.

3. **Verification gates.** Gates turn feedback into a clear verdict: done or not done. They are the
   checkpoints that prevent self-declared completion. "I think it's fixed" is not a gate; "the test
   that reproduced the bug now passes" is. Done must be *proven*.

4. **Termination condition.** An explicit rule for when the whole loop stops. Without it the agent
   either quits too early or grinds forever without real progress. State it concretely: all queue
   items pass their gates; or everything remaining is human-gated; or a deliberate
   confirmation/safety limit is hit.

5. **Error handling.** Spell out what to do when a tool call or command fails, so the system recovers
   cleanly instead of leaving a half-broken state that breeds more failures. Rule of thumb: never
   leave a partially-written file or broken build; after N failed attempts on the same gate, stop
   digging, log the blocker, and move on.

6. **State across turns.** The context window cannot hold everything forever. Keep truth in external
   files - a status doc, a journal/findings log, run artifacts - so the agent can lose the chat
   history and still know exactly where the task stands.

## Stop-don't-fabricate

The single rule that most distinguishes a safe loop from a dangerous one. When a task needs an answer
that does not exist in the project's data - an external decision, a missing reference, an ambiguous
acceptance criterion - the agent must **record the open question in a state file and move to other
work**, never guess and proceed. An autonomous loop that fabricates missing inputs produces a large
volume of confidently-wrong work before anyone notices. Make this an explicit, non-negotiable rule in
every MISSION.

## Expert techniques

- **Fresh context.** Launch the loop in a new session so the goal file is not competing with a long
  scrollback. Clean context measurably improves loop performance.
- **Goal file, not chat.** The mission lives in a file the agent re-reads each iteration. This is the
  practical fix for context management - instructions never get buried.
- **Adversarial builder/verifier.** Separate the agent that builds from the agent that checks, ideally
  different models, so the verifier is not invested in the builder's reasoning. Have the verifier try
  to *refute* the work, not confirm it.
- **Smallest step, frequent verification.** Small units with a gate after each catch errors early and
  keep state recoverable, instead of one large unverified leap.
- **Self-evolving rubric.** When the verifier keeps missing a class of defect, update its checklist/
  skill to encode the new pattern, so the harness gets stronger over time.
- **No-auto-commit by default.** Leave changes in the working tree for human review rather than
  committing autonomously, unless the user explicitly wants commits. Cheap to relax, expensive to undo.

## Legibility: the plan is a map, not a wall

As a MISSION accumulates tasks, findings, and journal entries it turns into a wall of prose. The
essence - which task blocks which, where the critical path runs, what is already done or already dead -
sinks under the text, and the agent (and the human) lose the plot. Legibility is a harness concern, not
cosmetics: an illegible plan produces a drifting loop.

The fix is three diagrams at the top of the goal file, re-read first each iteration:

- **Loop cycle** (flowchart) - the five steps with the gate-fail / retry branches, so the harness
  shape is obvious.
- **Task dependency DAG** (`graph TD`) - nodes = tasks, edges = "must exist before", node color = live
  status via a `classDef` block (done / partial / not-started / blocked / human-gated). Name the
  keystone: the node that unblocks the most. This is what makes "smallest task first" safe - without it
  the greedy heuristic does easy leaves while the bottleneck rots.
- **Data flow** (flowchart) - inputs → producers → product → consumers, expensive edges and the regen
  step marked, reference/golden shown as validation-only.

Convention: keep the DAG node colors current - the graph *is* live state, updated in the RECORD step,
and the plan self-check verifies the colors against the real checkboxes. A diagram that lies is worse
than none.

## Hygiene: dead code is a first-class loop concern

An autonomous loop that only ever adds code steadily rots the repo: duplicate producers, replaced paths
left wired in, orphan files. The damage is quiet and compounding - a second producer computing the same
quantity a different (wrong) way is a latent correctness bug, not just clutter.

Bake hygiene into the harness with two live lists:

- **Already dead / duplicated** - detected at setup, refreshed when suspicious. The sharpest smell is
  two paths that compute the same truth; also unused exports, orphan files, and `deprecated / legacy /
  fallback` markers still on a live path.
- **Predicted dead after a change** - for each task that *replaces* behavior, name what it makes dead so
  the old path is retired *with* the change. "Migration done" includes deleting the thing it replaced;
  otherwise both run and drift.

Deletion is gated, never on suspicion: it needs a passing parity gate (the new path provably covers the
old) plus proof of no live importers. If unproven, mark it blocked and record it - the same
stop-don't-fabricate discipline applies to removal as to invention.

## Performance and flow budget

Loops are token-hungry and some steps are slow, wide-blast, or destructive. Make the expensive edges
explicit so the agent prefers the cheap path instead of thrashing:

- **Surgical before sweeping.** Prefer the one-unit variant of an expensive operation (regen one unit,
  rebuild one target) over the full sweep; run the full sweep only when required.
- **Drift guard after any wide regen.** Diff the product/output tree against HEAD and revert anything
  the change did not intend to touch. Wide regens silently drop parked units or rewrite unrelated ones.
- **Parallelism where safe.** Independent read-only checks (adversarial verify, per-unit QA) can fan
  out; writes to shared files must not.
- **No-progress budget.** If N iterations pass with no new gate closed, stop and hand back rather than
  burning tokens in a circle. This is a termination condition, not a suggestion.

## Verify the plan itself

The loop verifies the code; something must verify the *plan*. Plans drift: checkboxes go stale,
`file:line` references rot as code moves, a task named in the termination condition never made it into
the queue, a diagram's colors stop matching reality. A plan that misrepresents its own state routes the
loop into redoing finished work or waiting on a blocker that already cleared.

Run a self-check on the goal file - at setup and periodically during a long loop, before selecting the
next task: every termination task exists in the queue and as a DAG node; every node color matches the
real checkbox and the code; the DAG is acyclic and the keystone is named; every gate command runs as
written; every file:line reference resolves; the hygiene lists are current; nothing out-of-scope has
quietly become a blocker of the core. Fix drift before acting on the plan.

## Common failure modes (design against these)

- **Self-declared done** - the agent says "fixed" with no gate. Fix: require a passing gate as the
  only definition of done.
- **Fabricated inputs** - the agent invents a missing external answer. Fix: stop-don't-fabricate.
- **Reference/golden overfitting** - when validating against a reference, the agent tweaks parameters
  to match the reference instead of solving the problem. Fix: tolerance-based validation only; forbid
  fitting parameters to the reference.
- **No termination** - the agent loops forever on diminishing returns. Fix: explicit stop rules and
  an N-attempt cap per gate.
- **Context burial** - instructions lost under tool output. Fix: goal file re-read each iteration.
- **Verifier capture** - the same reasoning that built the work also "verifies" it. Fix: adversarial,
  ideally different-model, verification.
- **Runaway cost** - loops are token-hungry because the agent, not the operator, searches the path.
  Fix: scope to deterministic work, smallest-first, and a clear termination condition.
- **Repo rot / silent duplication** - an additive-only loop leaves dead paths and duplicate producers
  behind; two paths compute the same truth and drift. Fix: hygiene lists + parity-gated retirement.
- **Plan drift** - stale checkboxes, rotted file:line references, diagram colors that no longer match
  reality; the loop redoes finished work or waits on a cleared blocker. Fix: verify the plan itself.
- **Wall-of-text plan** - the essence buried under accumulated prose; the loop loses the critical path.
  Fix: the three diagrams at the top of the goal file, kept as live state.

## Cost note

Loops are expensive in tokens - the agent, not the operator, is searching for the path. Use them
deliberately: scope to work where "done" is machine-checkable, do the cheapest/smallest items first,
and rely on a firm termination condition. More token budget generally yields better loop outcomes,
but only when the gates and guardrails keep that spend pointed at real progress.
