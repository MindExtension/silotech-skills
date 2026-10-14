# Incident to class: one defect becomes a class-wide fix and a new detector

Use when a defect has been pinpointed (a wrong number, a silent zero, a failed run, a client complaint).
The goal is not to fix the spot. The goal is: no member of this class exists anywhere in the chain, and
the earliest gate now catches the next one. Fixing the spot instead of the class was the longest stall
in the source history (ST-06): the same class reappeared at the next location, tenant or carrier.

## I1 Pin and reproduce
Record the instance (code revision, version id, environment, tenant), the observed value, the expected
value and the source span that proves the expectation. Reduce to the smallest input that reproduces it.
No reproduction: stop and report `not_checked`; do not fix by guess and do not rerun blindly (ST-02).

## I2 Find the first wrong stage
1. Look up the observation in `symptom-index.md`; take every matching row's modes in order and run the
   first check of the top mode. FAIL confirms the mode; PASS from an effective check rules it out.
2. Walk backwards from the wrong output through provenance (contributors, inputs, rule ids). At each
   artifact evaluate its invariants on the affected units; the first artifact whose invariant fails is
   the first failing seam. Record `stage_introduced` and the stage that SHOULD have detected it.
3. When the trace is unclear (`gate-ladder.md` G8): oracle substitution with gold intermediates (a stage
   wrong on gold input introduces the error; a stage right on gold but wrong end to end amplifies it);
   configuration bisection for a regression with no obvious diff; error grouping with leave-one-group-out
   localisation when many records or an aggregate are wrong.

## I3 Two roots and the guard autopsy
Cause root, answered in sequence; the first "yes" wins:
1. Does the defect disappear when the same code and data run in the environment where checks ran, or is
   it about durability, limits or the bundle? **Operations.**
2. Is the product (including its own status fields) correct, and only a check, metric or review about it
   wrong (a guard passed or failed for the wrong reason, the wrong instance was checked, a metric moved
   without the product)? **Process.** A wrong status field inside the product is not Process: continue.
2b. Is the defect a missing or wrong edge in the dependency graph (an undeclared read, a deleted or
   moved producer whose readers remain, a reader combining artifacts of different lineage, a consumer
   whose contract lacks a field the producer has)? **Structure**: the graph or consumer contract has no
   place for the edge. When producer and consumer schemas disagree, judge by the consumer's contract.
3. Trace the fact to the source at its locator. Is it there?
   - Yes. Does the schema, prompt, card or state model have a place for it, including its unit, scope,
     qualifier, status and a consumer?
     - No place: **Structure.**
     - Place exists, value missing or wrong: **Collection.**
     - Value right, output wrong: **Logic.**
   - No, the fact is absent from the source. Did the chain say "unavailable (scope searched)"?
     - It invented, defaulted or inherited a value: **Logic** if a state for "unavailable" exists,
       **Structure** if it does not.
     - The source contradicts itself and the chain accepted one side silently: **Collection** (no
       cross-check at ingest, FM-29).
Add a **secondary Process root** whenever a guard existed or was claimed and did not fire.

Escape root (why no guard fired): `absent` (no guard), `vacuous` (guard could not fail), `narrow_scope`
(guard did not scan this language, path, artifact or transition), `warn_only`, `wrong_instance` (checked
a cache or old version), `not_run` (no runner or skipped), `late_gate` (caught only at G5-G8 after the
cost was spent; the shift-left rule in `gate-ladder.md` applies), or `none` (caught by the intended
earliest gate; no escape). Every escaped defect has a Process component through its escape root.

Guard autopsy: name the registered guard that should have fired; run the ordered guard audit on it
(`guard-the-guards.md` section 2); compare with the FM card's "Slipped" line in `failure-modes.md`. Each
guard whose verdict is not `effective` is its own FM-23 finding.

Rule: Collection and Structure are fixed platform-wide, for every tenant and stage that shares the
carrier or slot, never only at the reported location. If the fix seems to need a tenant-specific branch,
the class is probably Structure (a missing qualifier) or the fix belongs in configuration derived from
the source, not in code.

Worked classifications:

| Symptom | Trace | Class |
|---|---|---|
| Register shows "no change-of-control clause"; it is in amendment 2 | fact in source; register schema has the slot; amendments never read | Collection: read all documents of the contract family |
| Consolidation rejects a new line-item code after the close run | mapper can emit codes the schema enum lacks; enum built from last year's sample | Structure: vocabulary from what the mapper can emit; plus Process (no enum-closure test) |
| Clinical registry stores "confirmed" for "probable" diagnoses | certainty captured; migration mapped two values to one | Structure (migration lost a state) |
| Takeoff areas off by 4x on one sheet | scale is printed on the sheet; extractor uses one global scale | Collection (scale not collected per sheet) |
| Survey total too high | duplicate respondents across modes; no dedupe rule | Logic if the respondent id exists, Structure if no cross-mode id exists |
| Export marked "valid" lacks required sections | content present internally; status from schema validity | Logic (status rule) plus Process (guard anti-pattern 2) |
| Works in CI, empty in production | dictionary file missing from the image; loader returns empty | Operations, plus Logic (fail-open loader) |
| Detail page renders empty after a producer refactor | the reader requires all parts to share one source digest; one part still comes from the legacy producer | Structure (step 2b: no edge forces one lineage), plus Process (the parity gate covered values, not provenance) |
| Missing depreciation life filled with 5 years, no flag | source lacks the fact; envelope has an `unavailable` state | Logic (default presented as fact) |

## I4 Class signature and class predicate
Write the class signature as a tuple (seam type, parameter, guideword, carrier or rule):
- (extractor to register, PRES, PART OF, appendices): obligations in schedules not read.
- (mapper to consolidation, VOC, OTHER THAN, new line-item codes): unknown code rejected late.
- (abstraction to registry, PROV, LESS, migration): "probable" upgraded to "confirmed".
- (plan reader to quantity table, UNIT, WRONG FRAME, sheet scale): two scales read as one.
- (questionnaire loader to weights, PRES, MORE, multi-mode responses): respondents doubled.

Then generalize the defect into an executable query or test that finds every member of the class, and
write the invariant that would have failed, at the lowest gate:

| Class (FM) | Predicate pattern |
|---|---|
| Vocabulary (FM-01) | distinct values of field X across all tenants minus consumer enum |
| Seams (FM-02) | consumer-matrix cells without a tested fixture |
| Identity (FM-03) | join hit rate per key family < threshold, or multiplicity > 1 |
| Absence (FM-04, FM-08) | displayed zeros without reached count; census > 0 and consumed = 0 |
| Laundering (FM-05) | broad handlers in producers emitting a domain status |
| Defaults (FM-06) | values equal to a code constant across inputs of different size |
| Provenance (FM-07) | status histogram in vs out of each transform differs |
| Truncation (FM-09) | caps without dropped counters; `finish_reason = length` |
| Leakage (FM-10) | outputs that change when references are removed |
| Frame (FM-11) | metamorphic mirror/reverse/scale violations |
| Scope (FM-12) | identical values at distinct keys |
| Coverage (FM-13, FM-14) | aggregates without denominator or with contributor multiplicity > 1 |
| Orphans (FM-15) | fields whose mutation leaves final output unchanged |
| Open loop (FM-16) | answered decisions not cited by the latest version |
| Freshness (FM-17) | artifacts whose code revision or input digest differs within one version |
| Promotion (FM-18) | pointer-moving paths that skip the promotion predicate |
| Isolation (FM-19) | identical content hashes across tenants for non-shared artifacts |
| Model stages (FM-21) | parsed-output diff between two replays of the same request |
| Status (FM-24) | status setters whose inputs contain no content invariant |
| Twins (FM-28) | second emitters of a registered concept; differential mismatches |

Also search for code-idiom siblings: the same helper, the same pattern (grep for the construct, not the
variable name; the grep pack GP-1..GP-12 is a start), the twin implementation in the other runtime, and
the same vocabulary used by other stages.

## I5 Sibling sweep
Run the predicate (and the invariant) over five dimensions:
1. every seam of the same type (all extractors, all mappers, all readers of the schema family);
2. every tenant and version;
3. every carrier of the same role (containers, depths, modalities, files per role);
4. every duplicate implementation of the concept (FM-28);
5. the bug history: past incidents and fixes with the same signature tuple.
Record `siblings=<n>` with the query. Each hit is a sibling finding with its own ledger row and the same
class id. Zero siblings is an absence claim: it needs a positive control (the predicate finds the
original case, or a seeded copy of it, on the same instance). A predicate that finds only the original
case is suspicious: widen it (different tenant, stage, spelling) and rerun before accepting 1.

## I6 Fix the root
Collection and Structure: change the shared extractor, carrier traversal, schema, prompt or card so every
sibling is fixed. Logic: change the rule at its canonical implementation (registry), never a copy, after
writing its decision table over all input states and testing every row. Operations: change the build,
bundle, retry policy or durability, not the one job. Process: change the guard, registry or delivery rule
(`delivery-stalls.md`).

## I7 Add the earliest detector
Pick the lowest gate in `gate-ladder.md` that can see this class. The original failing input becomes the
seeded fault: the detector must FAIL on the pre-fix code and PASS after the fix. Register it with runner,
scope, blind spots and the killed seeded fault; run the guard audit until it is `effective`. If the fix
was a prompt, schema or card edit, derive an assertion from the edit (what output would the old version
produce that the new one must not) and add it to the stage's assertion set. If the class could have
broken an expensive run, add it to the preflight battery as a P-item.

## I8 Regression and blast radius
Run old and new code over the whole corpus (all tenants) on a scratch sink and diff at record level by
stable key; a rerun with paid model calls or over ~10 minutes needs the user's yes (truth rule 9 in
SKILL.md). Every
added, removed or changed record maps to the expected-change list; unexplained diffs block. For model
stages measure the A-A noise floor first. Report siblings fixed, records changed per tenant, aggregates
moved.

## I9 Learn
- Hazard table: add or update the row; raise O or D for the escaped mode (an escape proves D was
  overrated). Update the guard registry; if the report was refuted, update the intentional-state registry.
- CAST clustering: record which controller acted on a wrong belief and which feedback was missing or
  misleading (empty read taken as measurement, cache taken as live, green test that never exercised the
  path). Cluster incidents by (wrong belief, missing feedback); each cluster gets one platform-level
  countermeasure, one assertion and one seeded fault.
- Containment matrix: keep a table of stage introduced vs stage detected for all incidents. Mass far
  from the diagonal (introduced early, detected late) shows where to add G1-G4 detectors. CAST clusters
  and the containment matrix go in the report (`templates.md` section 0).
- Recurrence: if the same FM recurs three times, its prevention moves down one gate (for example from G5
  to G3, or from G3 to G0).
- Catalog: if no FM card fits, add `FM-NEW-<n>` to `failure-modes.md` (signature, root, guideword cell,
  detectors, probe, slipped, example) and a row to `symptom-index.md`. The catalog learns too.

Stop condition: class predicate returns 0 open siblings on the current version with a positive control;
detector registered and effective; blast-radius diff fully explained; findings ledger row has both roots,
the signature, the predicate, the sibling count and the detector id.
