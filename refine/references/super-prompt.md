# The Refine super-prompt

One self-contained prompt that runs a full multi-perspective, multi-pass improvement loop on
ANY artifact. It is the distilled synthesis of five well-studied patterns, folded into one
operating procedure:

- **Self-Refine** (Madaan et al., 2023) - generate, critique, refine, iterate with the model's own feedback.
- **Evaluator-optimizer + orchestrator-workers + parallelization** (Anthropic, Building Effective Agents) - split work, improve each piece, judge against criteria in a loop.
- **Reflexion** (Shinn et al., 2023) - keep an episodic memory of past mistakes as verbal rules and feed it back in.
- **LLM-as-judge, multi-perspective rubric panels** - derive the evaluation lenses from the artifact's purpose, score against concrete checks, not vibes.
- **Design-QA field lessons** - judge the RENDERED reality, not the source; one writer per unit; harvest the lesson BEFORE the re-pass.

Paste the block below, fill the four inputs, and run it. It works with or without a workflow engine:
with parallel subagents it fans out one improver per unit; solo, it walks the units in sequence.

---

## The prompt

```
You are a top-tier practitioner running a disciplined REFINE loop on the artifact below. Your job is
not one edit. It is to raise the artifact to a clearly defined quality bar through observation,
multi-perspective critique, parallel improvement, verification, and iteration, while never changing
its meaning or data.

INPUTS
- ARTIFACT: <path or content of the thing to improve>
- PURPOSE: <what it is for, and for whom> (if blank, infer it and state your inference before acting)
- QUALITY BAR: <what "done and good" means here> (if blank, derive it from PURPOSE)
- CONSTRAINTS: <what must NOT change - wording, numbers, data, public API, house style>
  Default: preserve all meaning, data, and voice; improve form, structure, and quality only.

RUN THIS LOOP

1. FRAME. In four lines state what the artifact IS, its PURPOSE, its AUDIENCE, and the QUALITY BAR.
   Ask the user only if the purpose or bar is genuinely ambiguous AND the answer would change the
   lenses. Otherwise infer, state your inference, and proceed. Frame drives every judgment below.

2. DECOMPOSE. Split the artifact into independently improvable UNITS and choose an isolation strategy
   so parallel work never collides:
   - Structured single file (deck, long doc): split into one file per unit, improve each, reassemble.
     Verify the split roundtrips byte-identically BEFORE touching content.
   - Multi-file project: units are files; one improver per file is already conflict-free. If improvers
     must build or run tests that mutate shared state, give each its own worktree.
   - Unsplittable monolith: improve sequentially, or have workers return the new unit as text and
     splice it in from a single writer.
   Cap the unit count sensibly. If you bound or sample coverage, SAY SO. Never cap silently.

3. DERIVE LENSES. From the PURPOSE, generate 3 to 6 expert evaluation perspectives - the panel a great
   practitioner in this domain would apply. Reuse a domain rubric if one exists. Write each lens as a
   concrete pass/fail check ("one clear focal point per slide", not "looks good"). Include at least one
   lens for the failure mode this artifact type is prone to (empty space for decks, silent wrong numbers
   for analysis, hidden coupling for code, wall-of-text for docs).

4. OBSERVE REALITY. Build / render / run / read each unit to its REAL output and look at THAT, not just
   the source. Most real defects surface only in the rendered reality: a deck that "reads fine" in HTML
   shows its empty space only once rendered; code that looks correct reveals its bug only when run.
   Produce a per-unit snapshot the critic can actually inspect.

5. IMPROVE IN PARALLEL. One improver per unit. Each reads its unit, its snapshot, the lenses, and the
   lessons log; scores the unit against EVERY lens; finds the concrete weaknesses; and rewrites ONLY its
   own unit to raise it on every failing lens. Real, specific improvements, not cosmetic tweaks. Isolated
   units mean all improvers run at once with no write conflict. Improvers change form, structure, and
   quality within CONSTRAINTS; they never change meaning or data unless the task itself is about content.

6. VERIFY AND ITERATE. Reassemble / rebuild, OBSERVE AGAIN, and re-score against the lenses. The first
   pass fixes the obvious; the deeper flaw usually survives it. Run a TARGETED re-pass on only the units
   still below bar. Loop until the bar is met or the budget is hit. Report any unit left below bar. Never
   claim uniform success you did not verify by looking at the rebuilt output.

7. HARVEST LESSONS. When the review catches a class of problem not already recorded, write it as a sharp
   one-line rule in the lessons log BEFORE the re-pass - "Observation -> Rule." - so this very run
   improves, not just future ones. The lessons log is the memory that makes each pass and each run
   smarter than the last.

GUARDRAILS
- Frame first. Improving without a stated purpose and bar produces aimless churn.
- One writer per unit. Never let two workers edit the same file.
- Verify by observing the rebuilt output, not by trusting the diff.
- Preserve meaning, data, and numbers unless the task is explicitly about changing content.
- Keep the house style; refine form, do not homogenize voice.
- No silent capping. If coverage was bounded, say what was left out.
- No em-dashes or en-dashes; use commas or hyphens. Keep diacritics correct.

Now run the loop on the ARTIFACT and report: the frame, the units, the lenses, what each pass changed,
which units met the bar, which did not, and the lessons you harvested.
```

---

## Why this is the optimized form, not just a longer prompt

- It is **purpose-first**: the lenses are derived from PURPOSE, so the same prompt fits a deck, a
  contract, a codebase, or a financial model without rewriting the criteria.
- It **judges reality**: step 4 forces looking at the rendered output, which is where most defects that
  survive a source-only review actually live.
- It is **parallel-safe by construction**: decomposition and one-writer-per-unit remove the write
  conflict before it can happen, so the improve pass scales to as many units as you have.
- It **compounds**: harvesting the lesson before the re-pass turns a single run into a self-improving
  loop, and the lessons log carries that gain into every future run.
- It **refuses to lie**: no silent capping, verify-by-observation, and report-what-is-still-below-bar
  keep the output honest instead of a confident "all done."
