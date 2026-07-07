---
name: refine
description: Generalized iterative refinement harness. Takes ANY artifact or project you are improving (a presentation, a document, a codebase, a dataset, an analysis), frames its purpose, breaks it into independently-improvable units, derives the right evaluation perspectives from that purpose, then observes and improves every unit in parallel, verifies the result, and iterates, accumulating lessons so it gets better each run. Composes with domain skills (for example the presentation design rubric). Use when the user hands you a thing to make better and wants a structured, multi-perspective, multi-pass improvement rather than a single edit. Trigger keywords - refine, iterate and improve, review and improve everything, polish, break down and improve, pasiimk kaip projektą ir pagerink, pereik viską ir pagerink, iteruok ir pagerink, suskaidyk ir pagerink, /refine.
---

# Refine - generalized iterative improvement harness

Turn "make this better" into a disciplined loop: frame the purpose, decompose into units, derive the
evaluation lenses that purpose demands, then observe and improve every unit, verify, and iterate. The
same shape works for a slide deck, a document, a codebase, or an analysis. What changes per project is
the decomposition, the lenses, and the "observe" command; the loop is constant.

This skill is the orchestrator. When a domain already has a rubric and helpers (for example the
`silotech-presentation-generator` skill has `references/design-review-rubric.md`, `scripts/split_slides.py`,
and `scripts/design-qa-workflow.js`), compose with them instead of reinventing.

Related but different: `autonomous-loop` drives an unfinished project toward completion; `refine` improves
an artifact that already exists by reviewing it from many angles and raising its quality.

## The loop

### 1. Frame
State, in one or two lines each: what the artifact IS, its PURPOSE, its AUDIENCE, and the QUALITY BAR
(what "done and good" means here). Derive these from the artifact and context. Ask the user only if the
purpose or bar is genuinely ambiguous and the answer changes the lenses. Frame drives everything below.

### 2. Decompose
Split the artifact into independently-improvable units and pick an isolation strategy so parallel work
never conflicts:
- Structured single file (HTML deck, long Markdown): split into one file per unit, improve each, reassemble.
  For SiloTech decks reuse `silotech-presentation-generator/scripts/split_slides.py` + `reassemble_slides.py`;
  for other single files write a small splitter on the section delimiter. Verify the split roundtrips
  byte-identically before touching anything.
- Multi-file project (repo, folder): units are files. One agent per file is already conflict-free. If
  agents must build or run tests that mutate shared state, give each a git worktree (`isolation: 'worktree'`).
- Monolith that cannot be split cleanly: improve sequentially, or have agents return the new unit as text
  and splice in the main loop (single writer).
Cap the unit count to something sensible; if you sample or bound coverage, say so, never silently.

### 3. Derive lenses
From the PURPOSE, generate 3 to 6 expert evaluation perspectives, a panel that a great practitioner in
that domain would apply. Reuse a domain rubric when one exists. See `references/lenses.md` for how to
derive lenses and example sets (presentation, document, code, data/analysis). Write the chosen lenses
down as the rubric the reviewers will score against.

### 4. Observe baseline
Build / render / run / read the current state so reviewers judge REALITY, not just source. Produce a
per-unit snapshot the critic can look at: a PNG for a slide, program output for code, the rendered text
for a doc. Looking at the real output is where most real problems surface (a deck that "reads fine" in
HTML shows its empty space only when rendered).

### 5. Improve loop
Run the parallel improve pass via `scripts/refine-workflow.js`: one agent per unit, each reads its unit
file, its snapshot, the lenses, and `references/lessons.md`, scores against the lenses, and rewrites ONLY
its own unit file. Isolated files means all run in parallel with no write conflicts. Agents change form,
structure, and quality within the constraints; they never change meaning or data unless the task itself is
about content.

### 6. Verify and iterate
Reassemble / rebuild, observe again, and re-score. Re-run a TARGETED pass (`onlyUnits`) on units still
below the bar. Loop until the bar is met or the budget is hit. Multi-pass matters: the first pass fixes
the obvious, later passes catch the residue. Report any unit left below bar; never claim uniform success.

### 7. Harvest lessons
When review catches a class of problem not already recorded, append a dated one-line rule to
`references/lessons.md` (and to the domain rubric if broadly useful). Next run starts smarter. This is the
self-improvement: over time the lenses and lessons encode more of what an expert would catch.

## Running the improve workflow

```
Workflow({ scriptPath: "<this skill>/scripts/refine-workflow.js", args: {
  unitFiles:  ["/abs/unit-01.ext", "/abs/unit-02.ext", ...],   // one editable file per unit
  snapshots:  ["/abs/unit-01.png", ...],                        // optional, per-unit rendered view to look at
  lensPath:   "/abs/rubric.md",                                 // or lensText: "...inline lenses..."
  lessonsPath:"/abs/lessons.md",                                // optional growing log
  purpose:    "one line: what this artifact is for and for whom",
  constraints:"what must NOT change (e.g. wording, data, meaning, public API)"
}})
```

Targeted re-pass: add `onlyUnits: [2, 7, 9]` (1-based indices into unitFiles) to re-run just those.
`args` may be an object or a JSON string; the script handles both.

## Guardrails
- Frame first. Improving without a stated purpose and quality bar produces aimless churn.
- One writer per unit. Never let two agents edit the same file.
- Verify by observing the rebuilt output, not by trusting the diff.
- Preserve meaning and data unless the task is explicitly about changing content.
- No silent capping. If coverage was bounded (sampled units, capped passes), say so.
- Keep the domain's conventions and house style; refine form, do not homogenize voice.
- Harvest at least one lesson per run when the review found real problems.
