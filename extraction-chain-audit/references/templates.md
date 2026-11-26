# Output templates

All artifacts live in one audit directory: a scratch folder or a folder the user names, never the
product's data store or repository data paths. Machine-readable ledgers are JSONL (one object per line)
so `python3 <skill-dir>/scripts/ledger_check.py <dir> --mode <mode>` can validate them. Examples use
neutral domains (a legal clause register unless stated otherwise); ids such as `t-02` or `v41` are
placeholders.

## 0. Files per mode and the severity scale
| File | Holds | QUICK | PREFLIGHT | BUILD | INCIDENT | AUDIT | DESIGN |
|---|---|---|---|---|---|---|---|
| `instance.json` | pinned identities; every other file refers to its `instance_id` | R | R | R | R | R | R (digest of the description) |
| `chain-map.md` | stages, consumers, control actions, feature answers, applicable modes, intentional states | - | - | R | O | R | R |
| `seams.jsonl` | one row per seam with its design intent (HAZOP input) | - | - | R (changed seams) | O | R | R |
| `hazards.jsonl` | HAZOP grid rows (hazard or pruned), STPA, belief, FTA, pre-mortem, defeater rows | - | - | R | O | R | R |
| `invariants.jsonl` | invariant ledger | O | O | R | R | R | - |
| `guards.jsonl` | guard registry with audit verdicts | O | O | R | R | R | R (predicted verdicts) |
| `findings.jsonl` | findings ledger | O (max 3) | O | O | R | R | R (plausible only) |
| `coverage.jsonl` | status of FM-01..FM-31 and ST-01..ST-15 | - | - | - | - | R | - |
| `rounds.jsonl` | round 0 (planting) and hunt rounds for the stop rule | - | - | - | - | R | - |
| `runs.jsonl` | run economics over expensive-run history | - | O | O | O | R when history exists | - |
| `planted.jsonl` | sealed planted defects, planted before round 1 | - | - | - | - | R | - |
| `preflight.json` | G4 preflight report | - | R | R before an expensive run (`--expensive-run`) | O | - | - |
| `quick-scan.md` | QUICK SCAN note | R | - | - | - | - | - |
| `report.md` | one-page report; BUILD adds the contract diff and promotion record, INCIDENT the CAST clusters and containment matrix | - | O | R | R | R | R |

R = required, O = optional, - = not used. `ledger_check.py` treats a missing required JSON or JSONL file
as a violation and a missing Markdown file as NOT-CHECKED.

Severity, the one scale for hazards, findings and guards (rows carry both `S` and the label); this table
is its one home:

| S | `severity` | Meaning |
|---|---|---|
| 9-10 | critical | wrong delivered number or decision with no flag |
| 7-8 | high | wrong but flagged or bounded; every floor case below |
| 4-6 | medium | bounded delay, rework or cost on one item or one cheap run |
| 1-3 | low | internal, meaning-preserving display defects only |

Floor rule: S is at least 7 (high) when the consequence is (a) a failed or wasted run over ~10 minutes or
a paid batch, (b) a shown or exported product that a reader refuses or cannot render, (c) every entity of
a tenant blocked or flagged, (d) users or agents losing their read path, or (e) text, labels or names
shown wrong in a deliverable. A hazard whose consequence is a failed expensive run is never backlog; its
control sits at G1-G4.

Thresholds used in the skill sit on these boundaries only: S >= 4 (medium or higher: B4 controls, the
stop rule counts) and S >= 7 (high or higher: blocking guards, partition stop, `must_fix` with D >= 7,
gap rounds, QUICK SCAN escalation). A label that does not match S is a ledger violation.

## 1. instance.json
```json
{"code_rev": "a1b2c3d", "env": "production", "access": "read-only",
 "data_versions": {"t-01": "v41", "t-02": "v17"}, "pinned_at": "2026-10-14T09:12:00Z",
 "how_pinned": "read-only snapshot export + version ids from the version table"}
```
`instance_id` = the first 12 hex digits of the sha256 of `code_rev`, `env` and `data_versions`, printed by
`ledger_check.py <dir> --digest`. Every finding, invariant, guard `last_run` and preflight report carries
it; a row whose `instance_id` differs from the current pin is `wrong_instance`. A DESIGN REVIEW pins the
description instead: `{"code_rev": "none (description)", "env": "description", "data_versions": {"doc":
"sha256:..."}}`.

## 2. chain-map.md
| Stage | Kind | Inputs (artifact@schema) | Outputs | Implementations | Consumers (fields) | Control actions | Model? cache? | Tenant scope | Runtime | Cost/run | Effective guards |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S3 extract_clauses | extract | pages@2 | clauses@3 | worker/py | S4 (type, span), UI (all) | accept, skip, retry | yes, keyed | per tenant | batch image | 12 min/100 docs | GR-004 (G3) |

Kinds: ingest, parse, extract, identify/match, normalize, derive/compute, assemble, aggregate,
publish/version, read/display, export, ops/runtime, human loop.

Then, under headings: consumer matrix with acceptance predicates (`contracts-by-construction.md` section
6); reference inputs (tainted); shared multi-tenant artifacts; every path that moves a visible or base
pointer; source census per carrier and tenant; intentional-state registry (behaviour, where documented,
who accepted it, date); feature answers; "Applicable modes" (ordered list from `selection.md`, written
after path A is sealed in AUDIT).

Feature answers (A2): answer each as a plain fact with where you saw it; ids are mapped later. Does the
chain have model or ML stages; several tenants sharing code or stores; several readers or runtimes of one
artifact (internal tools included); published versions, a "current" pointer or caches; human answers fed
back; delivered aggregates; joins across sources; units, signs, frames, dates or scales; text in national
scripts, codepages or source escape codes; fallbacks or defaults; reference answers or gold sets;
multi-carrier sources; caps, budgets or filters; status fields shown or exported; simplified copies
reused; definitions experts may choose differently; runs over a few minutes or paid fan-out; job queues,
workers or leases; several agents changing the chain at once; long-lived docs and plans; repeated fixes
in one area; strict blocking gates on uncertain values?

## 3. seams.jsonl
```json
{"id": "SM-03", "producer": "S3 extract_clauses", "consumer": "S4 normalize_terms", "type": "extractor->normalizer",
 "artifact": "clauses@3", "fields": ["type", "span", "party"],
 "carries": ["PRES", "VAL", "ID", "VOC", "SCOPE", "PROV", "VER", "SIG"], "features": ["join", "model_call"],
 "intent": "every clause of every document in the contract family, typed from the closed clause vocabulary, bound to one party id, with page and span",
 "contract": "clauses schema v3", "cardinality": "0..n per document", "units": "none",
 "frame": "document order", "scope": "one tenant, one contract family",
 "versions": "writes v3; reader supports v2, v3", "cross_runtime": false, "changed": true}
```
`carries` (required, never empty) uses the parameter codes of `hazard-sweep.md` 1.2; `type` is required
(`represented_by` matches on it). `features` names what makes `o` cells apply: join, aggregate,
model_call, human_step, cache, cap, shared_store, queue. `changed` marks the seams a BUILD sweeps. A
seam without `intent` is a Structure finding.

## 4. hazards.jsonl
HAZOP rows, one or more grid cells per row (`"*"` = all guidewords or all parameters):
```json
{"id": "HZ-012", "source": "hazop", "seam": "SM-03", "status": "hazard",
 "parameter": ["ID"], "guideword": ["OTHER THAN"],
 "deviation": "defined term bound to a longer term that contains it",
 "cause": "substring match on party names", "consequence": "obligations attributed to the parent entity; exposure per party wrong by up to 100%",
 "S": 9, "severity": "critical", "O": 4, "D": 10, "detection_evidence": "none", "safeguards": [],
 "control": {"kind": "prevent", "gate": "G0", "description": "canonical party-id parser + alias crosswalk; ban substring match (G1)"},
 "fm": [], "priority": "must_fix"}
{"id": "HZ-013", "source": "hazop", "seam": "SM-03", "status": "pruned", "parameter": ["FRAME"], "guideword": "*",
 "prune_reason": "not_carried", "prune_detail": "clause records carry no coordinates, sign, direction or calendar convention"}
{"id": "HZ-014", "source": "hazop", "seam": "SM-03", "status": "pruned", "parameter": ["UNIT"], "guideword": ["LESS"],
 "prune_reason": "no_credible_cause", "prune_detail": "notice periods are integers with a typed unit; none rounded",
 "examined": ["normalize_units()", "clauses schema v3 field notice_period", "records r-001..r-040"]}
```
`prune_reason`: not_carried | feature_absent | matrix_blank | prevented_by_construction | represented_by |
no_credible_cause | not_examined; `prune_detail` is never empty. `no_credible_cause` and
`prevented_by_construction` take one guideword per row and an `examined` list; `prevented_by_construction`
also names an effective `guard`; `represented_by` names the representative seam (`SM-07` or
`SM-07@<prior ledger dir>`). Rules in `hazard-sweep.md` 1.5. `fm` stays empty in AUDIT path A until the
list is sealed; a new mode is written `FM-NEW-<n>`.

Other sources use the same table without the grid fields:
`"source": "stpa", "control_action": "promote", "uca_type": "wrong_timing"` (`uca_type`: not_provided |
harmful | wrong_timing | wrong_duration); `"source": "belief", "controller": "publisher", "belief":
"run complete", "learned_from": "exit code 0"`; `"source"`: fta | premortem | defeater for the other
sections of `hazard-sweep.md`. `priority`: must_fix | before_release | backlog. D must match its
evidence: 1-3 needs an effective safeguard at G0-G3, 4-6 one at G0-G6, 7-8 a human review or G8 step
named in `detection_evidence`; otherwise D is 9 or 10.

## 5. invariants.jsonl
```json
{"id": "INV-003", "family": "record_conservation",
 "statement": "per stage: in = out + rejected(reason) + merged(reason)",
 "predicate": "python tools/conservation.py --stage all --version v41",
 "stages": ["S2", "S3", "S4"], "tenants": "all", "gate": "G5", "guard": "GR-007",
 "result": "fail", "reason": "S3 loses 37 records in t-02 with no rejection reason",
 "executed_count": 6, "instance_id": "3f9c2a7b1d04"}
```
`result`: pass | fail | not_checked; pass needs `executed_count > 0`; fail and not_checked need `reason`.
Tolerances come from source precision, units or a stated domain rule, never from what makes today's run pass.

Invariant library (families; the `family` field takes these names):

| Family | Predicate | Gate | Modes | Seeded fault |
|---|---|---|---|---|
| record_conservation | in = out + rejected(reason) + merged(reason) per stage and stratum; key hash total carried through | G5 | FM-08, FM-09, FM-14 | drop 10% silently; duplicate 5% |
| quantity_conservation | parts sum to stated totals; every grouping dimension is a partition whose groups sum to the parent; two partitions give one total; signed and absolute deviation side by side | G5 | FM-13, FM-14, FM-29 | move one item between groups; map one entity to two groups; double one line and drop another of equal value |
| partition_coverage | union of extracted ranges = declared scope; no gaps or overlaps; denominator in physical units | G5 | FM-12, FM-13, FM-14 | remove one zone; extend a zone into its neighbour |
| round_trip | `parse(serialize(x)) == x`; `format(parse(id)) == id`; re-read export equals the internal model | G2 | FM-03, FM-11, FM-25 | simplify before export; add an identifier notation |
| metamorphic | MR-1..MR-12 hold (`gate-ladder.md` G2) | G2 | FM-11, FM-14, FM-19, FM-26 | invert one sign convention in one node |
| monotonicity_rank | ordered things stay ordered; start < end; adding an item never lowers a sum | G3 | FM-11, FM-29 | swap two adjacent items |
| frame_consistency | one frame id per tenant and version; shared landmarks agree across artifacts; features distributed as the domain specifies around the reference frame | G5 | FM-11, FM-03 | offset one artifact's frame by a constant |
| closed_vocabulary | producer emit set within every consumer enum; every code emitted or reserved; unknown abstains | G1 | FM-01, FM-24 | emit an unseen code |
| provenance_completeness | observed values carry source, revision, locator, span; derived carry rule and inputs; status flag consistent | G3 | FM-07, FM-06 | strip provenance from one value |
| tri_state_presence | measured, empty (scope, positive control), unavailable (reason); zeros paired with reached counts | G3 | FM-04, FM-08 | delete one input; expect unavailable, not 0 |
| lineage_homogeneity | one code revision and one input version set per version; no undeclared reads; skip = fail | G6 | FM-17, FM-18 | serve one stale input |
| tenant_isolation | a run for tenant A leaves B byte-identical; artifacts belong to their version's tenant | G6 | FM-19 | inject a row from another tenant |
| consumption | mutating any emitted field, answer or card changes the final output; every read has a producer | G2 | FM-15, FM-16 | mutate one field |
| promotion_monotonicity | a visible or base version satisfies the current predicate; no newer allowed version hidden | G6, G7 | FM-18 | promote a partial version |
| cross_field_identity | domain equations per record (parts sum to whole, start < end, derived difference = labelled difference) | G3 | FM-29, FM-07 | break one identity |
| uniqueness_identity | natural keys unique; aliases resolve to one entity; identity stable across versions | G3 | FM-03, FM-14 | duplicate a key under a new id |
| scope_declaration | every derived value states its scope; identical values at distinct keys flagged | G0, G5 | FM-12 | give two locations one value |
| oracle_separation | removing or perturbing references leaves outputs bit-identical | G2 | FM-10 | put the answer key in the input folder |
| answer_closure | an answered question is cited by the next version or listed as answered-unapplied | G6 | FM-16 | answer without applying |
| witness_independence | critical facts have at least 2 evidence channels; disagreements go to triage; agreeing witnesses do not share source, model family, prompt or author; error correlation is measured on gold | G8 | FM-21, FM-10 | make two witnesses read one cache |

## 6. guards.jsonl
```json
{"id": "GR-004", "name": "enum closure for clause vocabulary", "protects": ["FM-01"], "invariants": ["INV-008"],
 "gate": "G1", "runner": "pytest tests/test_enum_closure.py", "trigger": "pre-merge", "mode": "block",
 "S": 8, "severity": "high", "scope": "python producers, vocabulary yaml, prompt option lists",
 "blind_spots": "values built at runtime from concatenated strings",
 "baseline": {"source": "none", "can_be_empty": false, "settings_hash": null},
 "seeded_fault": {"id": "SF-004", "description": "producer returns unseen 'hybrid'", "killed": true, "last_killed": "2026-10-14"},
 "last_run": {"instance_id": "3f9c2a7b1d04", "executed_count": 214, "result": "pass"},
 "status": "registered", "verdict": "effective", "predicted_verdict": null,
 "verdict_reason": "steps 1-9 passed; SF-004 killed; positive control passed",
 "scope_audit": "Q1-Q7 answered in guards/GR-004-scope.md", "owner": "chain team", "expires": null,
 "ceiling": null, "replaces": null, "replaced_by": null}
```
`trigger`: pre-merge | ci | write | preflight | run | promotion | display | periodic. `mode`: block | warn.
`status`: proposed (written during a hunt) | registered | retired. `verdict` (ordered audit in
`guard-the-guards.md` section 2): unaudited | phantom | vacuous | never_passes | narrow | warn_only |
effective. `predicted_verdict` (same enum) is set when the runner could not be reached or in a DESIGN
REVIEW, where `verdict` stays `unaudited`. `S` is the highest severity among the hazards it protects.
Only `verdict: effective` counts as a safeguard, and `ledger_check.py` also requires: runner set, seeded
fault killed, last `executed_count > 0` on the pinned `instance_id`, and `mode: block` (or owner,
`ceiling` and expiry with S < 7).

## 7. findings.jsonl
```json
{"id": "F-007", "title": "Clauses on image-only schedule pages never extracted",
 "fm": ["FM-08", "FM-04"], "st": [], "symptom": "S-36",
 "cause_root": "collection", "secondary_roots": ["process"], "escape_root": "narrow_scope",
 "stage_introduced": "parse", "stage_detected": "audit", "detected_gate": "audit",
 "instance_id": "3f9c2a7b1d04", "tenants": ["t-02"],
 "evidence": {"repro": "python tools/census.py --tenant t-02 --role schedule", "observed": "census 23 pages, consumed 0", "expected": "23 consumed or 23 skipped with reason"},
 "verdict": "confirmed", "verdict_reason": "reproduced; not in the intentional-state registry; R1-R7 did not refute",
 "verification": {"by": "fresh_session", "saw_candidate": false},
 "S": 8, "severity": "high",
 "signature": {"seam_type": "parser->extractor", "parameter": "PRES", "guideword": "PART OF", "carrier": "image-only schedule pages"},
 "class_predicate": "census(role) > 0 and consumed(role) = 0, all tenants, all roles",
 "siblings": 3, "positive_control": "predicate finds the original t-02 case on v41",
 "blast_radius": "obligation counts for 3 tenants; portfolio exposure",
 "earliest_detector": {"gate": "G4", "description": "census vs consumed per carrier in preflight", "guard": "GR-019"},
 "fix_locus": "platform", "found_by": "B", "round": 1, "planted": null, "related": [], "guards": ["GR-019"],
 "duplicate_of": null, "intentional_state_checked": true, "status": "open"}
```
Enums: `cause_root` collection | structure | logic | operations | process; `escape_root` absent |
vacuous | narrow_scope | warn_only | wrong_instance | not_run | late_gate | none; `verdict` confirmed |
plausible | refuted | not_checked; `severity` per section 0; `detected_gate` G0..G8 | audit | user
(found after delivery); `fix_locus` platform | stage | spot; `found_by` A | B | AB | incident | quick;
`status` open | fixed | accepted_risk; `verification.by` fresh_session | human | same_context;
`saw_candidate` is false only when the value was re-derived blind (location and question, not the
finder's value). `escape_root: none` means the intended earliest gate caught it. `fm` takes FM-01..FM-31
or `FM-NEW-<n>`; `st` takes ST-01..ST-15. `related` lists finding ids; `guards` lists guard ids (an
FM-23 finding names the guards it is about); `duplicate_of` marks a deduped row, which is kept, never
deleted.

Rules the script enforces: at least one of `fm` or `st` (a stall-only finding has `fm: []`; a path-A
row may leave both empty until sealing); `instance_id` equals the current pin; in AUDIT an integer
`round` >= 1. Confirmed needs `evidence.repro`, plus `class_predicate` and `intentional_state_checked:
true` unless `found_by` is quick; in AUDIT also `verification.by` other than same_context and
`saw_candidate: false` (not required for planted-defect findings: the reveal is their oracle); a DESIGN
REVIEW has no confirmed findings. Collection or structure needs `fix_locus: platform`; plausible,
refuted and not_checked need `verdict_reason`; a confirmed finding with `detected_gate` G5..G8 or
`user` needs a Process finding with `escape_root: late_gate` whose `related` lists it (shift-left rule,
`gate-ladder.md`); INCIDENT needs at least one `found_by: incident` finding with `signature`,
`siblings`, `earliest_detector.gate`, and `positive_control` when `siblings` is 0. Findings on planted
defects carry `planted: "<PL id>"` and `copy`, the scratch copy they reproduce on (truth rule 1 in
SKILL.md).

## 8. coverage.jsonl (AUDIT)
```json
{"id": "FM-14", "status": "guarded", "guards": ["GR-011"], "findings": [], "stages": ["identify/match", "aggregate"], "reason": "uniqueness at write + dedupe census"}
{"id": "FM-21", "status": "not_applicable", "feature": "model or ML stages: none (chain map, stage list)", "reason": "no model calls anywhere in the chain"}
{"id": "ST-02", "status": "not_checked", "guards": [], "findings": [], "reason": "no access to run history"}
```
`status`: guarded | finding | not_applicable | not_checked. For an FM id, `guarded` needs an effective
guard whose `protects` lists the id; for an ST id it needs `evidence` that the ST "Check" line passed.
`finding` needs a finding whose `fm` or `st` lists the id (for an ST id: its trigger fired).
`not_applicable` needs `reason` and `feature` (the chain-map feature answer it relies on) and is never
allowed for the universal ids FM-04, FM-05, FM-15, FM-23, ST-03, ST-07. `not_checked` needs `reason`. An
AUDIT with no guard rows marks FM-23 `not_checked` with the reason. One row for every FM-01..FM-31 and
ST-01..ST-15, written by the completeness critic from the FM x stage matrix.

## 9. rounds.jsonl (AUDIT)
```json
{"round": 0, "planted_by": "script", "planted_digest": "9b41c0e27d5a6f13", "completed": true}
{"round": 1, "path": "A", "angle": "HAZOP grid + STPA + contract audit, catalog-blind", "completed": true, "sealed": true, "sealed_digest": "51d2e8a0c4b7f9e6", "started_at": "2026-10-14T09:30:00Z"}
{"round": 1, "path": "B", "angle": "smell scan, grep pack, FM probes, run history", "completed": true, "sealed": true, "started_at": "2026-10-14T09:30:00Z"}
{"round": 2, "path": "B", "angle": "tenant by tenant, least tuned first", "completed": true}
```
Round 0 records the planting (`planted_by`: sub_agent | human | script | self, where self means the
finder applied its own seeds and cannot certify the stop rule; `planted_digest` from `ledger_check.py
<dir> --digest`). Round 1 holds the two paths (`path` A, B, or `both` when one agent ran both, which
makes it a solo audit) with `started_at`. `sealed: true` on round 1 means the path's list was written
before the other path's output was read; the path-A row (or `both`) carries `sealed_digest` over the id
and title of round-1 rows with `found_by` A or AB, and only then do `AB` findings count as overlap. Later
rounds are fresh angles; a completed round that adds no new confirmed S >= 4 finding is a dry round.

## 10. runs.jsonl (run economics, `delivery-stalls.md` ST-01)
```json
{"run_id": "r-0192", "kind": "full_run", "tenant": "t-02", "code_rev": "a1b2c3d", "minutes": 95, "status": "failed",
 "fingerprint": "9f1c", "first_error": {"node": "normalize_terms", "error_class": "schema_enum", "field_path": "clauses[].risk_class", "value": "hybrid"},
 "catchable": "G4", "catching_check": "P3 enum closure on deployed code", "p_item": "P11+9f1c",
 "change_since_last_same_fingerprint": null}
```
`status`: succeeded | failed | cancelled. `catchable`: G1 | G2 | G3 | G4 | runtime_only. Each failed run
needs `fingerprint` and `catchable`; `first_error.node` and `first_error.error_class` are required on
failed runs (class recurrence: three or more failed runs of one class need an ST-06 finding); a run
without `minutes` makes the compute shares NOT-CHECKED; catchable at G1-G4 needs `catching_check` and a
proposed `p_item`. `change_since_last_same_fingerprint`: null on first occurrence; false on a repeat with
no change touching the failing node, its inputs or config, which needs an ST-02 finding.

## 11. planted.jsonl (AUDIT, sealed from finders)
```json
{"id": "PL-1", "seed": "duplicate 5% of records in the t-02 scratch copy", "guideword": "MORE", "parameter": "PRES",
 "expected_fm": ["FM-14"], "location": "scratch/t-02/records.jsonl", "sealed": true, "planted_at": "2026-10-14T09:05:00Z"}
```
3-5 rows, each `sealed: true` with a `planted_at` earlier than round 1; `--plant N` writes them with
`target_rank` and an empty `location` for the planter (a fresh sub-agent or a human) to fill after
applying. Finders do not open this file before the reveal.

## 12. preflight.json
```json
{"instance_id": "3f9c2a7b1d04", "image": "sha256:...", "sink": "scratch", "cache": "scratch", "model_calls": "off",
 "smoke_records": {"t-01": ["rec-rare-branches", "rec-largest"], "t-02": ["rec-new-format"]},
 "items": [{"id": "P1", "result": "pass", "evidence": "running rev a1b2c3d == expected", "executed_count": 1},
           {"id": "P6", "result": "fail", "evidence": "3 errors (keep-going), see errors", "executed_count": 5},
           {"id": "P9", "result": "not_applicable", "reason": "model or ML stages: none (chain map)"},
           {"id": "P11+9f1c", "result": "pass", "evidence": "risk_class closure on deployed code", "executed_count": 14}],
 "errors": [{"fingerprint": "7a20", "node": "assemble_register", "error_class": "missing_field", "field_path": "clauses[].party_id", "value": null, "retryable": false}],
 "verdict": "no_go", "elapsed_seconds": 74}
```
Every item P1-P10 and every fingerprint item from `runs.jsonl` is present; a missing item is NOT-CHECKED.
`result`: pass | fail | not_checked | not_applicable (with `reason`, never for P1-P4, P6, P7 or a
fingerprint item; P5 only for a tenant's first run or a chain with no published versions). `verdict`: go
only when every present, applicable item is pass; `--expensive-run` and `--mode preflight` also require
`verdict: go`.

## 13. quick-scan.md (QUICK SCAN, at most 15 lines)
```
Quick scan <change or seam>, <date>, instance <code rev / version / env>
Q1 vocab PASS (enum closure test ran, 214 checked) | Q4 absence NOT-CHECKED (no fixture with a missing page) | ...
Findings (max 3, each with a reproduction):
  1. <S, label> <one line> repro: <command or record pointer>
Cheapest missing detector: <gate> <check>, protects <FM id>
Checked <n> of 14, failed <n>, not checked <n>. Not a clean bill: only the listed checks ran.
Next: none | BUILD step B<n> | AUDIT | INCIDENT on <item>
```

## 14. report.md (about one page)
```
# <scope> chain audit, <date>
Instance: code <rev>, versions <ids>, env <env>, access read-only.  Mode: AUDIT | BUILD | INCIDENT | DESIGN REVIEW.
Verdict: COMPLETE | INCOMPLETE (<failed stop criteria>) | DESIGN REVIEW (never COMPLETE)
Verification: fresh context | human | same-context, unverified (verdicts capped at plausible)

## Top risks (max 5, severity first)
F-007 S8 high  Collection  FM-08  <one line>  -> fix: <platform fix>; detector: G4 census
## Counts
confirmed <n> (critical/high/medium/low), plausible <n>, refuted <n>, not_checked <n>
by cause root: C <n> S <n> L <n> O <n> P <n>;  escape roots: absent <n> vacuous <n> late_gate <n> ...
## Guards
effective <n> of <n> registered; by verdict: phantom <n> vacuous <n> never_passes <n> narrow <n> warn_only <n>
unaudited <n>; lowest mutation scores per FM (5); proposed guards with seeds: <ids>
## Run economics
failed <n> of <n> expensive runs; failed compute <x>% of all; catchable at G1-G4 <y>% of failed compute;
new P-items <ids>; repeated fingerprints (ST-02) <ids>
## Residual
<the what-remains statement from hunt-and-stop.md section 3>
## NOT-CHECKED (each with reason)
## Next actions (ordered by severity, then cheapest earliest gate)
```
INCIDENT reports replace "Residual" with: class signature, predicate, siblings found and fixed, detector
id and its killed seed, blast-radius diff summary (records changed per tenant, aggregates moved), CAST
clusters and the containment matrix. BUILD reports add the contract diff and the promotion record (G6
predicate result, key-level diff, expected-change list, live-surface check). DESIGN REVIEW reports
replace "Residual" with a predicted verdict per guard and the checks to run first.
