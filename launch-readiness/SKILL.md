---
name: launch-readiness
description: Multi-agent launch-readiness review. Detects the signals that make a product look early-stage, unfinished, or not really live (placeholder copy, test data, default favicons and metadata, dead links, test-mode payments, raw i18n keys, debug routes, missing legal or analytics) and turns them into a verified, triage-able action plan, then hands the plan to autonomous-loop for fixing. Runs 10-15 perspective subagents over the codebase and the live product in several discovery rounds with adversarial verification. This skill should be used when a product is about to launch or is already public and the user wants it to look and behave like a live, operated product; not for general quality polish of a working artifact (that is refine). Trigger keywords - launch readiness, does this look live, production polish, early-stage smells, polish before launch, go-live review, ar atrodom gyvi, nupoliruok prieš paleidimą, pasiruošimas paleidimui, launch check, /launch-readiness.
---

# Launch readiness - make the product look and behave live

An "early-stage smell" is anything visible to a first-time visitor, a paying customer, or a crawler
that says "nobody actually launched or operates this": lorem ipsum, a default framework favicon,
a stale footer year, a dead pricing link, a raw i18n key, mail from onboarding@resend.dev, a noindex
left on, a checkout on test keys. Individually small, together they kill trust and conversion. Find
them systematically, verify each one adversarially, and produce a numbered action plan the user can
triage and hand to an execution loop.

Related but different: `refine` raises the quality of an artifact that already works; `autonomous-loop`
drives a task queue to completion. `launch-readiness` is the detector and planner that sits in front of
them: it produces the verified task queue.

## The loop

### 1. Scope
Establish, in one or two lines each:
- **Target**: absolute project directory, and the live URL if the product is deployed.
- **Intentional constraints**: read the target repo's `CLAUDE.md` / product docs first. Decisions that
  look early-stage but are by design (for example a zero-human-touch product deliberately has no
  support chat) must be listed as constraints so finders never report them.
- **Perspectives**: default is all 15 lenses in `references/smell-catalog.md`. Drop only lenses that
  clearly do not apply (for example the payments lens when there is no checkout); keep at least 10.
  If coverage is reduced, say so in the final report, never silently.

### 2. Sweep (multi-round, parallel)
Run the workflow script. Round 1 fans out one finder agent per perspective over the codebase and the
live product. Between rounds a completeness critic reads what was found and proposes up to 6 targeted
extra probes (a different modality: built output, HTTP headers, email templates, sitemap vs real pages),
which run as the next round. The loop stops when the critic finds no gaps, a round yields nothing
fresh, or `maxRounds` is hit.

`<skill>` below = the absolute path of the directory containing this SKILL.md; substitute it before
calling. In `planPath`, replace `YYYYMMDD` with today's date; if `planPath` is omitted the script
defaults to `<projectDir>/launch-readiness-plan.md`.

```
Workflow({ scriptPath: "<skill>/scripts/launch-readiness-workflow.js", args: {
  projectDir:  "/abs/path/to/product",                     // required
  catalogPath: "<skill>/references/smell-catalog.md",      // required
  liveUrl:     "https://product.example",                  // optional, enables live probes
  lessonsPath: "<skill>/references/lessons.md",            // optional growing log
  planPath:    "/abs/path/to/product/docs/launch-readiness-plan-YYYYMMDD.md",
  constraints: "intentional decisions finders must NOT report, one per line",
  perspectives:["placeholder-content", ...],               // optional subset of catalog keys, default all 15
  maxRounds:   2
}})
```

The workflow returns rounds, raw/confirmed/refuted counts, severity totals, and 3-5 highlights;
relay these to the user when presenting the plan.

### 3. Verify (built into the workflow)
Every fresh finding is adversarially re-judged by an independent verifier per area: does the cited
file and line exist, is it actually reachable in the shipped product, would a real visitor notice,
or is it intentional per the constraints. Only confirmed findings survive; severity is re-graded by
the verifier, not the finder.

### 4. Plan
The workflow writes the action plan to `planPath`: one checkbox line per task, stable IDs `LR-01 ...`,
grouped by severity then area, each with file:line or URL evidence, a one-line fix, and an effort tag
(S/M/L). The header records coverage: perspectives run, rounds, raw vs confirmed counts, and anything
dropped. The file ends with a "Deferred / not doing" section used during triage.
If the workflow returned `planPath: null`, nothing was confirmed: report the coverage facts to the
user, skip steps 5 and 6, still do step 7.

### 5. Triage with the user
Present the numbered task list. The user goes through it and says what to drop or change. Rules:
- Numbering is stable; never renumber or reuse an LR-NN ID after the first presentation.
- Apply each decision to the plan file immediately: drop = move the whole task line into the
  "Deferred / not doing" section, change = edit the line in place.
- After each batch of decisions, re-show the remaining list so the user sees a shrinking backlog.
- Do not fix anything during triage.

### 6. Fix
After triage, two paths:
- Small S-effort items: fix inline in the session, verifying each by observing the rebuilt output.
- The rest: invoke the `autonomous-loop` skill with `planPath` as its work queue. Each unchecked
  `- [ ] **LR-NN**` line is one task with its evidence and machine-checkable fix; the loop checks a
  task off only after verifying the fix. Deferred-section lines are out of scope.

### 7. Harvest lessons
When the sweep catches a smell class not yet in `references/smell-catalog.md`, or a verifier kills a
false-positive class, append a one-line rule `- YYYY-MM-DD: rule` to the top of the list in
`references/lessons.md` (newest first). The next run starts smarter.

## Guardrails
- Judge the shipped surface: production build, live URL, crawler view. A smell only counts if it is
  visible outside the dev team. Dev docs, tests, and internal comments are not smells by themselves,
  except where they leak into the shipped bundle.
- Respect intentional design. Everything in `constraints` is off-limits for findings.
- The sweep is read-only. Finders and verifiers never edit the product; the only file the workflow
  writes is the plan.
- Live probes are read-only GET requests. Never submit forms with real data, never trigger real payments,
  never create accounts on the live product without explicit permission.
- Never auto-fix before the user has triaged the plan.
- No silent capping: if perspectives were dropped, rounds were cut, or findings were sampled, the plan
  header must say so.
- No em-dashes or en-dashes in anything written; use commas or hyphens. Keep Lithuanian diacritics correct.
