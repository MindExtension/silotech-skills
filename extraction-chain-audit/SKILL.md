---
name: extraction-chain-audit
description: >-
  Prevent, hunt and root-cause bugs, silent errors and design flaws in complex analytical workflows:
  chained extraction, calculation and aggregation pipelines that turn messy domain sources (documents,
  drawings, scans, forms, APIs, model outputs) into a structured domain model, records and totals, in
  any domain (engineering, law, finance, health, insurance, statistics). Use when changing a stage,
  schema or vocabulary, before a long or paid run or a release, when reviewing a pipeline design, or
  after a wrong total, a silent zero or a run that keeps failing. Triggers: "audit the pipeline", "why
  does the run keep failing", "silent errors", "wrong totals", "preflight", "are our checks real",
  "guard the guards", "is this safe to ship".
---

# Extraction chain audit

Prevent defects by construction, catch the rest at the earliest and cheapest gate, and never let a
multi-hour run be the first real test (the run history behind this: `references/delivery-stalls.md`).

Terms: chain = stages from source to delivered aggregate; seam = one producer -> consumer interface;
tenant = each client, entity, site or source family; version = one published state; `<skill-dir>` = here.

## Project adapter
First read the project adapter if any: a project skill based on this one, or a project-instructions section.
It holds root-name mapping, instance pin and read-only commands, tenants, intentional-state registry path,
roles allowed to run, promote or write. Its permission rules win; project facts stay there.

## Truth rules (every mode)
1. Pin the instance first: code revision, data version ids, environment, tenants (`instance.json`). Every
   result names it. A check on a cache, old server, other worktree or index file is NOT-CHECKED for production.
   Exception: planted-defect findings reproduce on the scratch copy made from the pin, carry the pinned
   `instance_id` plus `copy: <copy id>`, and count only toward planted recall.
2. Every result is tri-state: PASS, FAIL, NOT-CHECKED(reason). PASS requires `executed_count > 0`.
   NOT-CHECKED never counts as PASS and never rolls up into "clean".
3. An empty read, zero, "none", missing artifact or a "latest / most recent" answer is not a measurement.
   Name the table, RPC or store read and show the current producer writes it (code path, or a row written
   after the last known event). A zero or empty list also needs a reached-step count and a positive
   control: a known-present sibling (such as the run behind the shown version) found by the same lookup.
4. A finding needs a reproduction (command or record pointer) on the pinned instance; without one its
   verdict is `plausible` or `not_checked`, never `confirmed`.
5. References, answer keys, gold labels and client totals validate; they are never inputs, prompt hints,
   fallbacks or fixtures. Removing them must leave outputs bit-identical.
6. A guard protects nothing until it has killed a seeded fault (`references/guard-the-guards.md`).
7. AUDIT, QUICK SCAN, PREFLIGHT and DESIGN REVIEW are read-only (artifacts go to a scratch audit
   directory); BUILD and INCIDENT change code only in the agent's own branch or worktree.
8. One severity scale, S 1-10 (`references/templates.md` section 0): 9-10 critical, 7-8 high, 4-6 medium,
   1-3 low; S is at least 7 for a failed expensive run, an unreadable deliverable, a whole-tenant block, a
   lost read path or wrong text in a deliverable. A guard protecting S >= 7 must block.
9. Paid model calls, runs over ~10 minutes, promotion or any visible or base pointer move, writes to live
   or shared stores and messages to experts each need the user's yes or a standing permission the user
   granted (scope, expiry); the agent never grants itself one. Before running chain code or a guard
   runner, print its sink, cache and model endpoints, confirm they are scratch, keep paid calls off or
   capped, never use freeze or write flags outside a scratch copy; otherwise NOT-CHECKED(approval).

## Root classes: one cause root and one escape root per finding
Cause roots: **Collection** (the fact is in the source, collected wrongly or not at all; fixed for every
tenant and stage sharing the carrier), **Structure** (the schema, prompt, card, vocabulary, dependency
graph or consumer contract has no place for the fact or edge; fixed in the shared contract), **Logic**
(collected right, rule wrong; fixed at the rule's canonical implementation), **Operations** (runtime
differs from where it was checked; build, bundle, retry, durability), **Process** (a verification or team
gap; guard, registry, delivery rule). Decision order: `references/incident-to-class.md` I3 (an undeclared
read or a reader combining artifacts of different lineage is Structure). Add a secondary Process root
whenever a guard existed and did not fire. Escape root: `absent | vacuous | narrow_scope | warn_only |
wrong_instance | not_run | late_gate`, or `none` (the intended earliest gate caught it).

## Gate ladder: always the earliest, cheapest gate that can see the hazard
G0 contract by construction -> G1 static pre-merge (seconds) -> G2 behaviour tests in CI (minutes) -> G3
write-time validation -> G4 preflight on 1-3 real records per tenant in the production image (1-5 min) ->
G5 run audit per stage -> G6 promotion (write-audit-publish) -> G7 display -> G8 independent checks per
release. `references/gate-ladder.md` holds every check and the shift-left rule (caught at G5-G8 = Process
finding against the missing earlier gate).

## Choose the mode
| Situation | Mode |
|---|---|
| small change, review comment, "is this safe to merge" | QUICK SCAN |
| new stage, field, vocabulary, tenant type, schema or prompt change | BUILD |
| producer graph, lineage or source-of-truth refactor that keeps the artifact shape (new producer for an existing artifact, legacy path kept alongside) | BUILD (B1 with acceptance predicates, B3 on PROV and VER) |
| about to launch a run over ~10 minutes or a paid batch, no design change | PREFLIGHT: G4 P1-P10 plus fingerprint items (`references/gate-ladder.md` G4), keep-going mode, about 5 minutes |
| before productization or a release; "what else is broken" | AUDIT |
| a written design or pipeline description with no instance, code or outputs | DESIGN REVIEW |
| one wrong number, silent zero, crash, complaint, a run failing again | INCIDENT |
| change already merged or auto-deployed with no check on the live surface, no defect seen yet | QUICK SCAN against the deployed revision on the live or preview surface, plus the G7 runtime budget; any FAIL -> INCIDENT |
| refactor that removes an artifact family, or a change to the promotion predicate | BUILD: B1 readers of every removed key, B3 STPA on the promote action only, G2 promotion decision table; other seams `represented_by` their last sweep |
| a status question (did it run, which version is latest, how many jobs failed) | no mode: truth rules 1 and 3, answer with the source and its writer named |

Several rows match: INCIDENT first when a failure was seen or the same class failed before (a go/no-go
after failed runs is INCIDENT on the class, then PREFLIGHT); otherwise BUILD, PREFLIGHT, QUICK SCAN, AUDIT.
DESIGN REVIEW only when nothing but a description exists; lacking instance access caps verdicts at
`plausible`, not the mode. Escalate a QUICK SCAN on any FAIL or 3+ NOT-CHECKED answers on S >= 7 outputs.

## QUICK SCAN (10 minutes, read-only)
1. (1 min) Pin the instance. Name the change and the seams it touches (producer -> consumer).
2. (2 min) Find every reader of the touched artifacts and fields in every runtime (by key, not by import).
3. (6 min) Run `python3 <skill-dir>/scripts/grep_pack.py <touched files>`; for each question that
   applies, run the cheapest existing check (test, search, one record); record PASS / FAIL / NOT-CHECKED:
   - Q1 Can the producer emit a value (incl. null, unresolved, assumed) a consumer rejects? FM-01
   - Q2 Shape or meaning changed; all readers on N and N-1; status and provenance kept? FM-02, FM-07, FM-28
   - Q3 Are entities joined by canonical keys, never substring or untoleranced nearest match? FM-03
   - Q4 Is a missing, unread or contradictory input distinct from a true empty? FM-04, FM-08, FM-29
   - Q5 Can an exception, missing flag or fallback end as success or a green status? FM-05, FM-24
   - Q6 Any value defaulted, imputed or tenant-tuned without an assumption record? FM-06, FM-26, FM-30
   - Q7 Does a cap, filter, truncation or display-grade copy lose input without a count? FM-09, FM-25
   - Q8 Does a reference or answer key reach compute, prompts, cards or fixtures? FM-10
   - Q9 Unit, sign, direction, frame, encoding, scope, boundary and comparator explicit? FM-11, FM-12, FM-27
   - Q10 Do aggregates carry a denominator, exclusions, disjoint groups, one unit? FM-13, FM-14
   - Q11 Is every new field consumed (mutating it changes output) and every read produced? FM-15, FM-16
   - Q12 Does it touch shared tenant state, caches, or the visible or base pointer? FM-17, FM-18, FM-19
   - Q13 Model stage or runtime: pinned, cached, `finish_reason` checked, inputs in the image? FM-21, FM-20
   - Q14 Did the guard I rely on run here (count > 0), can it fail, and does its scope cover every field and
     predicate any consumer of the changed artifacts reads (value parity is not provenance)? FM-22, FM-23, ST-03
   - Q15 Screen or reader change: renders live on N and N-1 (not a cache), one request per key? FM-31, ST-03
4. (1 min) Write the quick-scan note (`references/templates.md`): the Q table, at most three findings
   with reproductions, and the single cheapest missing detector (gate and check). At 10 minutes stop;
   unanswered questions are NOT-CHECKED. Never write "clean"; write "N checked, M failed, K not checked".

## BUILD: prevent while building or changing a chain
Output: contract diff, seam intents, hazard and invariant rows, guards, preflight report, promotion record.
- B1 Map: chain-map rows and `seams.jsonl` (with design intent) per touched stage; the consumer matrix of
  every touched artifact in every runtime, internal tools included, with each reader's acceptance
  predicates (what makes it refuse or render empty). Unidentified consumer = hazard; no intent = Structure.
- B2 Contract first (`references/contracts-by-construction.md`): value and aggregate envelopes (tri-state,
  status, scope, unit, provenance; denominator, exclusions, partitions), closed vocabularies with
  `unresolved` and `assumed`, definitional slots, a version bump on any meaning change. Then code.
- B3 Sweep (`references/hazard-sweep.md`): HAZOP every changed seam over the full guideword x parameter
  grid (every cell a hazard row or a pruned row with its reason); STPA every new control action with the
  belief check. Adding or renaming one vocabulary value or one field on an existing seam sweeps that
  parameter's 12 cells plus EARLY and LATE on SIG; the rest is `represented_by` the seam's last full sweep.
- B4 Control. For each hazard with S >= 4 first make the state unrepresentable (G0); otherwise pick the
  earliest gate detector. Write each control as an invariant row naming its gate.
- B5 Guard the guards: each new detector kills a seeded fault (FAIL on the mutant, PASS on clean input),
  reports `executed_count`, gets a registry row. No guard is loosened before a replacement kills its seeds.
- B6 Fast tiers. Run G1 and G2 (rare-state and script fixtures, metamorphic relations MR-1..MR-12, fault
  injection, cold tenant), then a production-shaped mini-tenant check.
- B7 Preflight, then the run (user yes, truth rule 9). G4 battery in the production image on 1-3 real
  records per tenant in keep-going mode; any FAIL or NOT-CHECKED on an applicable P-item blocks the
  run: fix all collected errors, rerun preflight. Pilot one tenant through the full run before fanning out.
- B8 Promote (user yes). Apply the G6 predicate; diff by key against the last accepted version; every
  diff maps to the expected-change list; confirm on the live surface and name the instance.

Done when: every new hazard has a control at a named gate; every new guard is effective; preflight PASS
for every tenant; promotion PASS; diff explained; NOT-CHECKED empty or each item has an owner and date.

## AUDIT: read-only hunt before productization or a release
Input: scope, budget (time, tokens, agents), read access. Output: the artifacts under Outputs.
- A1 Pin the instance read-only; plant 3-5 sealed defects in a scratch copy before any hunting
  (`references/guard-the-guards.md` section 7); collect the intentional-state registry (deliberate
  behaviours, accepted risks, fail-closed paths); run economics into `runs.jsonl` when history exists.
- A2 Map and census: stages, `seams.jsonl` with intents, consumer matrix with acceptance predicates,
  control actions, shared artifacts, pointer-moving paths, reference inputs, source census per carrier
  and tenant. Answer the feature questions (`references/templates.md` section 2) as plain facts without
  opening `references/selection.md`; map them to chain shape and modes in A5, after path A is sealed.
- A3 Guards: register every existing guard; run guard-audit steps 1-7 now and step 8 (the catalog's
  "Slipped" line) after path A is sealed (`references/guard-the-guards.md` section 2). Any verdict other
  than `effective` on an S >= 7 hazard is a finding (FM-23).
- A4 Path A, systematic and catalog-blind: HAZOP over the full grid of every seam, STPA with the belief
  check, contract audit. Do not open the failure-mode catalog, symptom index or selection tables until
  path A's list is sealed in `findings.jsonl` (`found_by: "A"`, digest in `rounds.jsonl`).
- A5 Path B, signatures and history, without reading path A: order the FMs by the A2 facts
  (`references/selection.md`); smell scan and grep pack first, then every FM probe in
  `references/failure-modes.md`, CAST-lite over incident and failed-run history, metamorphic and
  seeded-fault probes on a scratch copy (truth rule 9), one delivered number traced back to its source.
  Catchable run fingerprints become proposed P-items; one repeated with no change between is ST-02.
- A6 Verify (`references/hunt-and-stop.md` section 2): reproduce, intentional registry, R1-R7 by an
  independent verifier, tri-state verdict, both roots, class predicate, S, blast radius, two-stage dedupe.
- A7 Coverage and stop: the completeness critic gives every FM and ST id a status in `coverage.jsonl`
  (empty cells for S >= 7 modes start a gap round). Stop rule (`references/hunt-and-stop.md` section 3):
  planted recall >= 0.8, K = 2 dry rounds, and the capture-recapture residual unless counts are small or
  the audit is solo. Out of budget first: label the report INCOMPLETE and list unmet criteria.
- A8 Report: top risks, counts by root, guard health, run economics, residual, NOT-CHECKED list, next
  actions by severity, then cheapest earliest gate. Fix only on the user's opt-in (then INCIDENT I4-I9).

## DESIGN REVIEW: a written description with no instance
Path A (HAZOP listing every numeric field with its unit and every yes/no, code and count field with its
absent states: none, not assessed, unreadable; STPA with the belief check; contract audit), then
the guard anti-pattern table (`references/guard-the-guards.md` section 5) on every described guard, then
the FM catalog as a checklist. Cells nobody could examine are pruned `not_examined`. Every finding is
`plausible`; no stop rule, no Chapman (one agent on one text is one path). Output: findings, a predicted
verdict per guard, checks to run first (by severity, then cheapest gate). Report label: DESIGN REVIEW.

## INCIDENT: one defect becomes a class (`references/incident-to-class.md`)
- I1 Pin and reproduce minimally. No reproduction, no fix, no blind rerun (ST-02).
- I2 First wrong stage: `references/symptom-index.md`, then provenance back to the first failing invariant.
- I3 Cause and escape roots; guard autopsy against the FM card's "Slipped" line; map to FM and ST ids.
- I4 Class signature (seam type, parameter, guideword, carrier or rule) and an executable class predicate.
- I5 Sibling sweep: every seam of the type, tenant, version, carrier of the role, twin implementation and
  past bug. Zero siblings needs a positive control; widen a predicate that matches only the original.
- I6 Fix the root at its locus. I7 Earliest detector, with the original failing input as its seeded fault.
- I8 Blast radius (user yes for paid or long reruns): corpus-wide key-level diff, every diff expected.
- I9 Learn: raise O or D; cluster by (wrong belief, missing feedback); a mode recurring three times moves
  its prevention one gate earlier; no card fits = `FM-NEW-<n>` with a symptom row.

Stop when the predicate finds 0 open siblings on the current version (with a positive control), the
detector is effective and the diff is explained.

## Delivery stalls
No run over ~10 minutes or paid batch without a PREFLIGHT pass built from failure fingerprints (ST-01); no
rerun or queued sibling run without a stored fingerprint and a class-level change to the failing node
(ST-02); every check prints its instance (ST-03). Other triggers: `references/delivery-stalls.md`.

## Solo protocol and multi-agent
Solo is the default and needs independence (`references/hunt-and-stop.md` section 4). A fresh read-only
sub-agent re-derives the value at the claimed location from the instance header, location and question only
(never the finder's value or reasoning: `saw_candidate: false`), then runs R1-R7 on the full claim; path B
runs in another fresh sub-agent given the instance, chain map and catalog, never path A's rows. Seeds are
applied by a fresh sub-agent or a human who alone opens `planted.jsonl` (`ledger_check.py <dir> --plant N`
only draws them); self-applied seeds are `planted_by: self` and cannot certify the stop rule. With no
sub-agent or human verifier, verdicts cap at `plausible`, the report says "same-context, unverified" and
the stop rule cannot be met: say so before starting. Fleets: user opt-in only (its section 5).

## Outputs and validation
Files per mode: `references/templates.md` section 0; report what did not run. Run `python3
<skill-dir>/scripts/ledger_check.py --selftest` first (no PASS line: check by hand), then `ledger_check.py
<dir> --mode audit|build|incident|quick|design|preflight` (`--expensive-run` in BUILD before a run).

## References (read when)
- `references/gate-ladder.md`: picking a detector; G0-G8, MR-1..MR-12, preflight, G8 sampling, shift-left
  rule; its grep pack is `references/grep-pack.tsv`, run by `scripts/grep_pack.py` with per-pattern controls.
- `references/hazard-sweep.md`: B3, A4, DESIGN REVIEW; parameters, guidewords, pruning, STPA, belief, FMEA.
- `references/contracts-by-construction.md`: B2 and the contract audit; envelopes, vocabularies, consumer matrix.
- `references/failure-modes.md` and `references/selection.md`: after sealing (A5, I3, coverage); FM cards,
  the guideword and UCA map, feature questions to modes, chain shapes, stage x mode.
- `references/incident-to-class.md` and `references/symptom-index.md`: INCIDENT; roots, predicate, siblings.
- `references/delivery-stalls.md`: when the work itself stalls; ST-01..ST-15, run economics, done predicate.
- `references/guard-the-guards.md`: A3, B5, I3; effective criteria, guard audit, seeds, anti-patterns, planting.
- `references/hunt-and-stop.md`: A4-A7; paths A and B, verification, stop rule, solo protocol, multi-agent.
- `references/templates.md`: writing any artifact; files per mode, severity scale, schemas, report formats.
- `references/techniques.md`: the method behind a step, and sources to cite.
