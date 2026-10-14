# Guard the guards

A guard is any check, test, gate, validator, schema, lint rule, monitor, judge, reviewer or audit agent
whose PASS someone relies on, including every detector you write during a hunt. In the history behind
this skill most escaped defects passed an existing guard that was vacuous, narrow, warn-only or ran on
the wrong instance, so guards are audited like product code. A guard counts as protection only when its
verdict is EFFECTIVE; unproven guards are recorded, but in the hazard table they count as `none` and
give detection D = 9-10.

## 1. Effective-guard criteria (all must hold)
1. Registered: a row in `guards.jsonl` (schema in `templates.md`) with a runner command and a trigger
   (pre-merge, CI, write, preflight, run, promotion, display, periodic). A guard cited in docs but absent
   from the registry, or registered without a runner, is phantom (FM-23).
2. Non-vacuous: it killed its seeded fault on the current code: run the guard against the mutant, observe
   FAIL or non-zero exit, restore, observe PASS on the clean input (the positive control). Record the date
   and the instance. A guard that never passes a known-good input is noise, not protection.
3. Executes: it reports how many items it checked; `executed_count = 0` is FAIL, a skip is FAIL; shell
   pipelines use `set -o pipefail`; background logs are judged by content, not exit status.
4. Scoped: `scope` says what it scans and `blind_spots` lists what it does not (languages, runtimes,
   artifact types, environments, fallback entry points, state transitions vs existing state, data vs code).
5. Baseline-safe: if it compares against a baseline, the baseline cannot be empty or deleted by the
   executor, stores a settings hash (rule version, cohort, reference id) and identities rather than
   counts, and is refrozen only in a separate change that shows the diff of the measured set.
6. Blocking by severity: protects an S >= 7 hazard => `mode: block`. A `warn` guard has an owner, a
   ceiling (how many warnings before it blocks, `ceiling` in the registry row) and an expiry date by which
   it blocks or is deleted.
7. Independent: it does not re-derive the value with the producer's own code path or read the producer's
   cache; it reads the live artifact it claims to check; a model judge is not the extractor's model family.

## 2. Guard audit: ordered verdict procedure (AUDIT A3, INCIDENT I3, BUILD B5)
For each guard in scope, in this order; stop at the first failing step and record `verdict` and
`verdict_reason` in its registry row. AUDIT runs steps 1-7 in A3 and step 8 after path A is sealed;
until then a verdict that reached step 8 is provisional.

1. Resolve the runner and run it on the pinned instance (truth rule 9 in SKILL.md: scratch sinks only,
   never freeze or write flags outside a scratch copy). Runner missing or not runnable: `phantom`. No
   access to the runner (as opposed to no runner existing): verdict `unaudited`, with `predicted_verdict`
   from the section 5 anti-patterns and the reason in `verdict_reason`.
2. Read `executed_count`. Zero or absent: `vacuous` for this instance.
3. Run the positive control (known-good input). It fails: `never_passes`.
4. Apply one seed per section 4 guideword row inside the guard's declared scope, plus each "Further
   seed family" that applies. No seed killed: `vacuous`; some survive: `narrow` (list the surviving seeds).
5. Compare the declared scope with what the protected mode needs (all languages, data files, emitted
   artifacts, fallback paths, every tenant), using the scope audit in section 3. Gap: `narrow`, gap named.
6. Check blocking: warn-only on an S >= 7 hazard, warn-only past expiry, or warnings ignored in recent
   runs: `warn_only`.
7. Check the baseline (criterion 5) and the last-run instance (`last_run.instance_id`).
8. Compare with the FM card's "Slipped" line (`failure-modes.md`; in AUDIT only after path A is sealed):
   if this guard has the same hole the card describes, it is `narrow`.
9. All passed: `effective`.

Guards not yet audited carry `unaudited`. On a guard protecting an S >= 7 hazard, any verdict other than
`effective` is an FM-23 finding plus a finding for the mode it was meant to cover. Below S 7, record the
verdict and list it in the report's guard-health line.

## 3. Guard scope audit (one written pass per guard)
Answer in writing; keep the answers in the registry row or next to it:
1. Which languages, file kinds and emitted artifacts does it scan? Which not?
2. Which environments does it run in (local, CI, production runtime)? Which not?
3. Which entry points and fallback paths reach the guarded action? Which bypass it?
4. Which tenants and versions does it cover? Does it re-check existing state or only transitions?
5. Can its baseline or input be empty? What happens then?
6. Is it cited anywhere (docs, plans, acceptance records)? Does every citation resolve to a runnable guard?
7. Does passing actually imply the claim it supports? (A citation existing does not imply it supports the
   value; matching totals do not imply correct items; a comparison against data from the same extraction
   is circular.) Name the undercutting defeater or write "none found".
Every "not" answer that touches an S >= 7 hazard becomes a hazard row with guideword NO on SIG.

## 4. Seeded-fault library (keyed to HAZOP guidewords)
Run on a copy of golden fixtures or a scratch copy of one tenant; never on live or shared state. Pick
seeds inside the guard's declared scope.

| Guideword | Data mutants | Code and check mutants |
|---|---|---|
| NO | delete an input file, page, sheet or record; empty a model response; remove a pointer target | make a reader return `[]` on error; remove a re-raise |
| MORE | duplicate a record, chunk or document under a new id; scale a unit x1000; add a second alternative variant | drop a uniqueness constraint |
| LESS | truncate a document at 60%; drop 10% of records; round values to one decimal; set a cap below input size | lower a cap; off-by-one in a range |
| AS WELL AS | inject a record from another tenant; add a superseded revision; drop the answer-key file into the input folder | widen a match to substring |
| PART OF | strip a unit; strip provenance; remove one component of a composite; drop one zone of a partition | remove a field from a migration map |
| REVERSE | flip a sign; mirror a side; reverse a sequence direction; swap amends/amended | flip a comparison operator |
| OTHER THAN | put an unseen value in an enum field; swap two fields; change the schema version id; substitute a plausible value from another document | make a status depend only on schema validity |
| EARLY | publish before all partitions finish; read before a decision is stored | acknowledge before the write |
| LATE | inject a schema violation in an early node and time the first failure | move a check to the final sink |
| STALE | serve the previous version's cached input; pin code to an older commit | reuse a verdict after tightening; key freshness on timestamps |
| WRONG FRAME | change input units; swap coordinate order; rewrite identifiers in another notation | use a second formatter for one identifier family |
| WRONG SCOPE | replace a point value with its window aggregate; give two locations one value; mix two versions on one read | drop the scope assertion at read |
| Guard itself | n/a | make the guard return PASS constantly; loosen tolerance x10; empty its baseline; disable it; add two offsetting errors of equal size |

Further seed families:
- Environment seeds: remove a bundle file or dependency; delete the baseline; make storage fail after
  acknowledging the write.
- Process seeds: cite a nonexistent test in an acceptance record; mark a guard skipped; add an
  unregistered producer.
- Incident seeds: every incident adds a seed that replays it exactly (INCIDENT I7).
- Lineage-driven seeds: take one correct delivered value, list its supports from lineage (page, layer,
  table, model call, human answer) and remove each in turn; the chain must still produce the value through
  a remaining support or fail loudly with a named code. A silent partial result is a finding.

Mutation score per guard = killed / applicable mutants. Per FM = share of its mutants killed by at least
one effective guard; a mode with no killed seed has D = 10. A surviving mutant is a finding with root
Process and escape root `vacuous` or `narrow_scope`. Data-level mutation scores under about 20% are poor,
above about 65% adequate (industrial rule of thumb; see techniques).

## 5. Guard anti-patterns and the test that exposes each
| # | Anti-pattern | Exposing test | Fix |
|---|---|---|---|
| 1 | Exit 0 taken as "output produced" | delete the output, rerun: still "success"? | post-node output check (G3) |
| 2 | Status from schema validity | export missing a required part validates? | content checklist (G6) |
| 3 | Skipped, not-checked or "no rows" counted as pass (or a missing optional reference counted as fail) | empty the input: still PASS? | tri-state, executed_count > 0 |
| 4 | Count-based completeness proxy as promotion predicate | right count, wrong keys: promoted? | required key set + content |
| 5 | Guard evaluated only on transitions | tighten predicate: existing pointer re-checked? | daily re-evaluation (G7) |
| 6 | Main path guarded, fallback or alternate entry unguarded | trigger the fallback path with bad data | one predicate for every path |
| 7 | Freeze keyed on the graph node, not the file | sibling node rewrites the frozen output | freeze by file hash |
| 8 | Shrink guard with deletable or empty baseline | delete the baseline file, run | baseline in a store the executor cannot delete; empty = FAIL |
| 9 | Opt-in guard covering only self-registered producers | add an unregistered producer | registry derived from the graph, opt-out with reason |
| 10 | Literal guard scanning one language, constants only, count-only baseline | move a literal into a data file or build it from strings | scan code, data, prompts, all languages; identity baseline |
| 11 | Policy test scans source but not emitted artifacts | emit a violating artifact from data | also scan the artifacts actually produced |
| 12 | Tautological verifier (value vs itself, abs() hiding inversion, checker picks its own sample) | REVERSE mutant; output-located sampling | independent sample from the reference grid |
| 13 | Self-referential metric sampling where output exists | delete output in one zone: score rises? | sampling fixed by the reference |
| 14 | Baseline without settings hash, or refrozen in the same change that moves the score | change cohort silently | settings hash; separate refreeze change |
| 15 | Unit test mocks the boundary it should exercise | replace mock with real writer or real caller payload | contract test on real payload |
| 16 | Validation only at the final sink after hours or paid calls | count minutes before the first failing check in a seeded run | move to G3 or G4 |
| 17 | Ensemble agreement over survivors; same-evidence models counted as independent | kill one member; correlate errors on gold | quorum over requested; correlation audit |
| 18 | Local verification on stale cache, wrong worktree or index file | print instance identity; compare with live | instance identity on every output |
| 19 | Warnings that never block | count warnings over 30 days | owner, ceiling, expiry |
| 20 | Pipes without pipefail; background logs judged by exit status | make the first command in the pipe fail | `set -o pipefail`; parse log content |
| 21 | Plan or acceptance checker validates structure, never runs the cited verification | cite a nonexistent test | resolve and execute every cited check |
| 22 | Inventory check confirms an inventory exists, not that sources were read | leave one source unread | census vs consumed per carrier |
| 23 | Retry-until-pass without first-attempt failure rate | count first-attempt failures | log and gate on first-attempt rate |
| 24 | Healthcheck imports one dependency and reports PASS | remove another dependency | import every dependency, report count |
| 25 | Gate that can never pass, so a permanent warning is normal | look for gates red for more than 7 days | fix, re-scope or delete with reason |
| 26 | Same model family as extractor and only judge | compare judge and extractor families | judge validated on human labels; diverse judge |
| 27 | Dependent review (checker sees the answer) counted as an independent layer | ask whether the checker saw the candidate | blind re-derivation (G8 selective editing) |
| 28 | Circular validation: reference derived from the same source, cache or pipeline | trace the reference's lineage | independent reference; oracle removal test |
| 29 | Auto-balancing or reconciling before testing for gross errors, smearing one error over many items | seed one large error; see if it is spread | gross-error test first, then reconcile |
| 30 | Bulk re-approval of snapshots or thresholds after a change | read approval history for bulk updates | reason code per update; separate refreeze change |
| 31 | Net-change or total-only tolerance (vs prior period, vs control total, QoQ, MoM) used as the only accuracy check | seed +x on one item and -x on another of equal size; seed a persistent error present in both periods: still PASS? | item-level or per-entity deviation with signed and absolute deviation side by side (`contracts-by-construction.md` section 2); a baseline independent of the chain's own prior output |

## 6. Model judges and graders
Measure TPR (human-pass judged pass) and TNR (human-fail judged fail) on about 100 balanced, labelled
items per field type. Report the corrected pass rate `theta = (p_obs + TNR - 1) / (TPR + TNR - 1)` with a
bootstrap interval; if `TPR + TNR - 1 < 0.3` the judge is not usable as a gate. Never use the extractor's
model family as its only judge. Re-validate after any model, prompt or source-type change. Log the
first-attempt failure rate of any assert-and-retry loop. A judge no more accurate than the system it
evaluates cannot replace most gold labels: budget for them.

## 7. Guards on the audit itself (planted defects)
Finder agents and reviewers are guards. Every AUDIT plants 3-5 known defects from the seed library in a
scratch copy before round 1, never after: the branch of the stop rule is known only after the hunt. Seeds
are applied by a fresh sub-agent or a human who alone opens `planted.jsonl`; `ledger_check.py <dir>
--plant N` only draws them at random for that planter (`hunt-and-stop.md` section 4). A finder that
applies its own seeds records round 0 `planted_by: self`; its recall is not blind and cannot certify the
stop rule. Each row in `planted.jsonl` is `sealed: true` with a `planted_at` earlier than round 1, and
round 0 in `rounds.jsonl` holds `planted_by` and the `planted_digest` printed by `--digest`; finders do
not open the file until the reveal. Planted recall = planted found / planted. Below 0.5 the hunt is
shallow: add rounds or angles. The stop rule needs recall >= 0.8 in both branches (`hunt-and-stop.md`
section 3). Findings on planted defects carry `planted: <id>` and `copy` (they reproduce on the planted
scratch copy, SKILL.md truth rule 1) and are excluded from capture-recapture counts.

## 8. Your own detectors
Every detector written during a hunt is a guard: it enters the registry with `status: proposed`, gets a
seed before its result is used, and its result carries the instance header. AUDIT leaves proposed guards
in the audit directory only; the report lists them with their seeds for the owner to adopt. BUILD and
INCIDENT move them to the agent's branch and to `status: registered` once the guard audit returns
`effective`.

## 9. Deleting or replacing a guard
Never delete or loosen a guard before its replacement is registered, effective, and kills the same seeded
faults (parity). Record `replaces` / `replaced_by` in the registry. A guard deleted in a refactor with no
replacement is a Process finding even if nothing has failed yet.
