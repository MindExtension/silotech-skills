# Symptom index

Lookup for INCIDENT I2/I3 and for review remarks: what you see -> likely modes (most likely first) ->
first check to run (cheapest that can confirm or rule out, with its gate) -> stage type to inspect first.
Mode cards are in `failure-modes.md` and `delivery-stalls.md`; checks in `gate-ladder.md` (G ids, MR ids,
P ids, GP grep pack ids); stage types in `selection.md`.

How to use:
1. Find the rows closest to the observation. Several rows may match; take all their modes.
2. Run the first check for the top mode on the pinned instance. FAIL confirms the mode; continue with
   INCIDENT I3. PASS from an effective check (its seeded fault was killed) rules the mode out; take the
   next. PASS from an unproven check is NOT-CHECKED.
3. No row matches: use the stage x mode table in `selection.md` for the stage where the value first goes
   wrong. If no card fits after that, record `FM-NEW-<n>` and add a row here (INCIDENT I9).
4. Record the symptom id (`S-nn`) in the finding's `symptom` field; it groups findings in the report.

## A. Runs fail, stall or waste compute
| ID | Symptom | Likely modes | First check (gate) | Inspect first |
|---|---|---|---|---|
| S-01 | Late hard failure naming one enum or literal field and an unknown value (often null, "unresolved", a fallback flag) | FM-01, FM-02 | G1 enum closure, then G4 P6 smoke records with rare states | normalize, assemble |
| S-02 | Each expensive run reveals one new blocker | ST-01, FM-01, FM-20 | G4 preflight in keep-going mode; run economics (ST-01) | whole chain |
| S-03 | The same error repeats across runs or retries | ST-02 | error fingerprint record (ST-02) | ops/runtime |
| S-04 | Stored error is a generic message with no node, field or value | ST-02 | structured error record (ST-02) | ops/runtime |
| S-05 | Works locally, fails or degrades in production; missing file read as empty | FM-20, FM-04, ST-03 | G1 bundle derivation; G4 P4 and P10 inside the image | ops/runtime, ingest |
| S-06 | Job marked done with no results; one late transient error discards hours | FM-20, ST-14 | G3 re-read before done; retry policy by error class | ops/runtime |
| S-07 | Size or timeout failures only on the largest tenant | FM-20 | G4 P8 budget extrapolation | ops/runtime |
| S-08 | Every consumer breaks when a new version becomes visible; a feature never worked end to end | FM-02 | G2 consumer matrix with N and N-1 fixtures; contract test on the real caller payload | publish/version, read/display |
| S-09 | One version id, different content | FM-02 | G1 schema immutability (content-hash pin) | publish/version |
| S-10 | Work waits days on a human answer or a "yes" | ST-05, FM-30 | unlock fan-out ranking (contracts section 10); G5 block-code concentration | human loop |
| S-11 | Work is lost when a session, job or machine ends | ST-14 | kill-and-restart idempotence check (ST-14) | ops/runtime |
| S-12 | Model budget spent, nothing applied; identical requests repeated | ST-15, FM-21 | G2 MR-12 replay and cache hit; G4 P9 20-item pilot | extract, identify/match |
| S-75 | A worker pass reports success while jobs stay queued or are never claimed | FM-09, FM-20, ST-14 | G5 per-pass conservation (deferred with reason); G2 queue tests | ops/runtime |

## B. Numbers wrong or suspicious
| ID | Symptom | Likely modes | First check (gate) | Inspect first |
|---|---|---|---|---|
| S-13 | Total about 2x for some tenants; duplicate natural-key error | FM-14 | G3 natural-key uniqueness; G2 MR-3 | aggregate, identify/match |
| S-14 | Totals match the reference but detail is wrong; absolute deviation much larger than signed | FM-14, FM-13 (cancelling), FM-12 | signed vs absolute deviation in the aggregate envelope (G6, G8) | aggregate |
| S-15 | Total more than 10% short of the reference, no exclusion list | FM-13, FM-08, FM-09 | G6 item 6 denominator and exclusions; G4 P4 census | aggregate, extract |
| S-16 | Suspicious round constants across inputs of different size | FM-06 | G5 distribution smell scan; G3 assumption counter | derive/compute |
| S-17 | A child value equals its neighbour's or the cohort median | FM-06 | G5 distribution smell scan | derive/compute |
| S-18 | Identical values at distinct locations; a local value equals the whole entity's extent | FM-12 | G5 smell scan (identical values at distinct keys); G0 scope field | aggregate |
| S-19 | Systematic offset growing along a sequence; features mirrored or misplaced | FM-11 | G2 MR-6 mirror and reversal; G5 frame health | normalize |
| S-20 | Error of exactly 10x, 100x, 1000x or another unit ratio | FM-11, FM-14 | G2 MR-4 unit scaling; G0 typed units | normalize |
| S-21 | Every entity has the same point, row or segment count | FM-11, FM-25 | G2 property test (count vs size); G5 smell scan | normalize, export |
| S-22 | Accuracy looks too good; card values equal reference values; output changes when the reference is removed | FM-10, FM-22 | G2 oracle removal; G1 grep pack GP-7 | process, derive/compute |
| S-23 | Quantities inflated by objects the source labels existing, prior or out of scope | FM-10 | evidence namespaces (contracts section 9) asserted at G3 | identify/match |
| S-24 | Global average clean, one window or segment far off | FM-29, FM-12 | G5 windowed residuals; G3 cross-field identities | extract, aggregate |
| S-25 | Source subtotal differs from its lines; names inconsistent inside one source | FM-29 | G3 cross-field identities; G4 parse plausibility | parse, extract |
| S-26 | Value labelled "from source" far from any evidence; one provenance value across N items | FM-07 | G5 smell scan; G3 provenance span check | normalize, export |
| S-27 | Class or grade histogram shifts across a migration with no data change | FM-07 | G2 migration histogram test | normalize |
| S-28 | Export valid against schema but missing required parts; "reliable" while undercounting | FM-24 | G6 content checklist; G2 status mapping test | export |
| S-29 | Export differs from the source primitives (curves became segments, amounts rounded) | FM-25 | G2 export round-trip | export |
| S-30 | Totals agree with the reference only under another boundary or convention; the expert says "minimum, not exact" | FM-27 | G1 card lint (definitional slots); G8 sensitivity table | derive/compute, aggregate |
| S-31 | Plausible values attached to the wrong entity | FM-03 | G5 join coverage and multiplicity; G8 blind re-derivation sample | identify/match |
| S-32 | Rerun gives different labels or values for the same input | FM-21 | G2 MR-12 replay diff; G6 A-A noise floor | extract, identify/match |
| S-33 | A score or total moves with no code change | FM-17, FM-21, FM-22 | G6 lineage homogeneity; A-A noise floor; G8 4-cell decomposition | publish/version |
| S-76 | Labels or names show escape codes, `?`, U+FFFD or mojibake instead of national characters | FM-29, FM-08, FM-11 | grep pack GP-11 on outputs; G4 P4 decode check; G2 script fixtures | parse, export |

## C. Absence, counts, coverage
| ID | Symptom | Likely modes | First check (gate) | Inspect first |
|---|---|---|---|---|
| S-34 | "None", "0 findings" or "clean" while the source contains the item | FM-04, FM-08 | G5 zero with reached count and positive control | read/display, ingest |
| S-35 | Displayed count, index count and source census disagree | FM-04, FM-28, FM-08 | G7 cross-count | read/display |
| S-36 | An entity class is zero for one tenant while present in its source | FM-08, FM-26 | G4 P4 census per carrier; G5 yield table | parse, extract |
| S-37 | Processed counts suspiciously round (30, 40, 400) | FM-09 | G5 cap counters; G1 grep pack GP-2 | extract, ingest |
| S-38 | Model budget ends with 0 answers; finish reason "length" | FM-09, FM-21, ST-15 | G3 model-call wrapper; G4 P9 pilot | extract |
| S-39 | Join hit rate near 0% for one key family | FM-03 | G5 join coverage per key family; G2 identifier round-trip | identify/match |
| S-40 | Coverage 100% despite known holes; "31 of 31" after hard cases were dropped | FM-13, FM-22 | G6 item 6 physical denominator; G2 metric contract | aggregate |
| S-41 | Zero counts on gates or steps that were never reached | FM-04, FM-23 | reached-step count (truth rule 3); guard audit step 2 | process |
| S-42 | Humans asked questions the source already answers | FM-08, FM-16 | G4 P4 census; pre-send dedupe (contracts section 10) | extract, human loop |
| S-43 | One block code covers more than 90% of entities; low coverage described as "honest" | FM-30 | G5 block-code concentration | derive/compute, assemble |
| S-44 | High output for one tenant, near zero for the rest; a new tenant rejected by a closed list | FM-26, FM-01 | G5 yield table per extractor x tenant; G2 cold tenant | identify/match, ingest |
| S-45 | A material class vanished after a performance or filter change | FM-09 | G6 retained-vs-dropped diff by class | extract |

## D. Versions, freshness, tenants
| ID | Symptom | Likely modes | First check (gate) | Inspect first |
|---|---|---|---|---|
| S-46 | Fix merged, nothing changes in the product | FM-17, FM-15, FM-28 | G4 P1 running revision; G2 consumer-existence mutation; G1 duplicate-implementation lint | publish/version |
| S-47 | Two screens or reports disagree | FM-28, FM-17 | G7 render-time version homogeneity; G2 differential test | read/display |
| S-48 | Users see an empty or partial product; the next run fails on a partial base | FM-18 | G2 promotion decision table; G6 predicate; G4 P5 | publish/version |
| S-49 | A correct but smaller version is never shown; a user's change vanishes after a concurrent run | FM-18 | G2 promotion decision table (legitimate shrink, concurrent run) | publish/version |
| S-50 | Tenants disappear from a shared file and the tests get greener | FM-19, FM-23 | G3 expected-entity set; guard criterion 5 (baseline) | assemble, publish/version |
| S-51 | One tenant's snapshot holds another tenant's keys | FM-19 | G6 cross-tenant overlap; G2 MR-10 | publish/version |
| S-52 | Artifact revision older than the rule it depends on; fresh file time, old content | FM-17 | G6 lineage homogeneity; G3 freshness by input digest | publish/version, ops/runtime |
| S-53 | A field exists but mutating it changes nothing; readers of a deleted producer show zeros or "in progress" | FM-15 | G2 consumer-existence mutation; G1 graph lint | assemble, aggregate |
| S-54 | Extracted facts sit next to rows marked "needs data" | FM-15, FM-16 | G2 consumer-existence mutation; G5 extracted-but-unconsumed count | assemble |
| S-77 | A page, export or tool renders empty or refuses after a producer refactor | FM-17, FM-02, FM-28 | G6 item 10 (final consumers on the candidate); acceptance predicates in the consumer matrix | publish/version, read/display |
| S-78 | A "latest" or status answer contradicts what users see | FM-17, FM-15 | truth rule 3 (name the store and its current writer); G1 graph lint on operational tables | ops/runtime |
| S-79 | Page never finishes loading or flickers; request or function-invocation rate jumps after a reader deploy | FM-31, ST-03, ST-04 | G7 runtime budget on the live surface; G1 reader effect lint | read/display |
| S-80 | A shared or corpus-level artifact fails at publish on a dangling reference after a change to a per-tenant artifact | FM-17, FM-15, FM-19 | G1 graph lint (reads by key vs declared edges); G2 read tracing; G3 referential integrity | publish/version, aggregate |

## E. Guards, status, metrics
| ID | Symptom | Likely modes | First check (gate) | Inspect first |
|---|---|---|---|---|
| S-55 | Green suite stays green when an input is emptied or a fault injected | FM-23 | guard audit with seeded faults | process |
| S-56 | Docs, plans or acceptance records cite tests or guards that do not exist or cannot run | FM-23, ST-07 | G1 citation resolution | process |
| S-57 | Node "executed" but output hash unchanged; an entity class stuck in one status after a code change | FM-05 | G3 post-node output hash; G2 programming-error injection | derive/compute |
| S-58 | Blocked item rendered green; a blocker names the wrong cause | FM-24 | G2 status mapping and one fixture per diagnostic code | read/display, export |
| S-59 | Score improves while no value changes at common points; "regression" while the measured set grew | FM-22 | G2 metric contract; G8 4-cell decomposition | process |
| S-60 | Uniform offset with tiny spread reported as a shape error | FM-22, FM-27 | comparison contract: both sides declare quantity class and frame | derive/compute |
| S-61 | Warnings fire every run and nobody reads them | FM-23, FM-17 | guard audit step 6 (warn-only) | process |
| S-62 | Retries make a check pass; first-attempt failure rate unknown | FM-21, FM-23 | G3 wrapper logs the first-attempt rate; per-attempt error records | extract, ops/runtime |

## F. Human loop and the work process
| ID | Symptom | Likely modes | First check (gate) | Inspect first |
|---|---|---|---|---|
| S-63 | Answered questions stay open or are asked again | FM-16 | G6 item 8 unapplied answers; pre-send dedupe | human loop |
| S-64 | Review queue with zero closures; most findings already answered | FM-16, ST-12 | G7 queue health; intentional-state registry | human loop |
| S-65 | The same defect class returns at new spots; fix-of-fix chains, reverts | ST-06 | INCIDENT sibling sweep; G8 error grouping | where it was fixed |
| S-66 | "Are you sure?" loops; done claims later refuted | ST-07 | done predicate (`delivery-stalls.md`) | process |
| S-67 | Local check passes, production rejects | ST-03, FM-20 | truth rule 1; G4 P6 in the production image | ops/runtime |
| S-68 | Unverified merges pile up; defects surface days later in batches | ST-04, ST-13 | mini-tenant check per change (ST-04) | process |
| S-69 | Much metric, gate or document work; the product is unchanged | ST-08 | ceiling estimate and moved-metrics line (ST-08) | process |
| S-70 | Many priority orderings; work in progress above cap; refactor started near a milestone | ST-09 | WIP count vs cap (ST-09) | process |
| S-71 | Parallel agents lose or duplicate work; stale branches; colliding migrations | ST-10 | worktree, lock and lost-hunk audit (ST-10) | process |
| S-72 | The same ad hoc inspection command repeated; stale comment claims mislead | ST-11 | G1 citation resolution; repeated-command count | process |
| S-73 | Many review findings refuted as intentional; one finding reported by several reviewers | ST-12 | refuted and duplicate share per round; dedupe before verify | process |
| S-74 | Red tests accepted as normal; the suite takes hours; no CI | ST-13 | quarantine set comparison (ST-13) | process |
