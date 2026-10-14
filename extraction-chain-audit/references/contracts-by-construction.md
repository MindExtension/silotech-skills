# Contracts by construction (G0)

Goal: make the wrong state unrepresentable or loud at the moment it is written. Each rule names the
failure modes it removes. Use this file in BUILD step B2 and as the yardstick for the contract audit in
AUDIT path A (step A4): every missing envelope field, missing denominator, open vocabulary, mutable
registered version or unsharded shared artifact is a candidate. The mode ids are for BUILD and for
mapping after path A is sealed: path A ignores the "Prevents" lines and judges against the rules.

## 1. Value envelope (every extracted or derived value)
```json
{
  "key": "contract-17/clause-9.2/notice_period",
  "value": 30,
  "unit": "day_business",
  "state": "measured",
  "status": "observed",
  "scope": {"kind": "entity", "ref": "contract-17/clause-9.2"},
  "provenance": {"source_id": "doc-17", "revision": "sha256:4be1...", "locator": "p12/para3",
                 "span": "thirty (30) Business Days", "extractor": "clause-extract@4.2",
                 "prompt_hash": "c9a0...", "model": "model-x@2026-05-01"},
  "rule_id": null, "assumption_id": null, "inputs": [],
  "frame": {"convention": "calendar-v1"},
  "run": {"run_id": "r-0192", "code_rev": "a1b2c3d", "input_digest": "sha256:77e0...", "tenant": "t-03"}
}
```
Rules:
- `state` is one of `measured | empty | unavailable | not_applicable`. `empty` requires the searched
  scope and a passed positive control; `unavailable` requires `reason` and `searched_scope`. Never encode
  absence as 0, `null`, `""` or `"none"`. Prevents FM-04, FM-08, FM-09.
- `status` is one of `observed | derived | imputed | defaulted | assumed | human`. `derived` needs
  `rule_id` and `inputs`; `imputed | defaulted | assumed` need `assumption_id` pointing to a counted
  assumption record. Cross-field rule: `assumption_id != null => status not in {observed, derived}`.
  Prevents FM-06, FM-07.
- `scope.kind` is one of `point | window | entity | group | tenant`; consumers assert the scope they
  expect. Prevents FM-12.
- `unit` is a typed unit from one registry; sums across units refuse. Prevents FM-11, FM-14.
- `provenance` is mandatory for `observed`; a value whose span does not contain it after normalization is
  rejected or re-labelled `derived`. Prevents FM-07, FM-29 (with the citator check in G8).
- `frame` names the convention module version for sign, side, direction, ordinal order and coordinate
  order. Prevents FM-11.

Drawing takeoff example: a wall length `{value: 12.4, unit: "m", scope: {kind: "entity", ref:
"level-2/wall-114"}, status: "derived", rule_id: "len-polyline-v3", inputs: ["ent:7f2a"]}`. Clinical
example: tumour size missing on a scanned page is `{state: "unavailable", reason: "ocr_page_skipped",
searched_scope: ["note-88 p1-6"]}`, never `0` or the cohort median.

## 2. Aggregate envelope (every total, count, rate, coverage)
```json
{
  "key": "portfolio/exposure/change_of_control",
  "value": 41, "unit": "contract",
  "covered": {"value": 212, "of": 230, "unit": "contract"},
  "excluded": [{"reason": "ocr_failed", "count": 11}, {"reason": "language_unsupported", "count": 7}],
  "contributors": {"ids_digest": "sha256:...", "multiplicity_max": 1},
  "group_keys": ["variant", "entity"],
  "non_observed_share": 0.04,
  "reference_check": {"signed_dev": -0.02, "abs_dev": 0.09, "reference_id": "ref-2026Q2", "role": "validation_only"}
}
```
Rules: denominator in the deliverable's physical unit (length, area, money, contracts, patients), not in
records processed (FM-13); every exclusion has a reason (FM-13); contributors carry multiplicity and
must be 1 unless declared (FM-14); alternative variants are a group key, never summed (FM-14);
`abs_dev` much larger than `|signed_dev|` means compensating errors (FM-13, FM-14); `non_observed_share`
above threshold blocks acceptance (FM-06). Each grouping dimension (segment, category, site, system) is a
partition: every contributor belongs to exactly one group per dimension, or the overlap is declared with
an elimination line; the sum over groups equals the parent aggregate, checked at G5
(`quantity_conservation`). Prevents FM-14.

## 3. Closed vocabularies
- One registry per vocabulary, versioned, imported by producer and consumer; never inferred from
  samples alone. Every closed field has explicit `unresolved` and `assumed` members, or the field uses
  the value envelope `state`. Unknown input abstains (`unresolved`), never coerces to the nearest member.
- Tests: emit set subset of consumer enum (G1); every member emitted somewhere or marked reserved (G1);
  smoke records include every rare state (G4). Prevents FM-01, FM-24, FM-26.

## 4. Identity
- One canonical parser and formatter per identifier family, with a golden corpus of real spellings from
  every tenant and a round-trip property test.
- An alias crosswalk where every label resolves to exactly one entity; two candidates = stop or
  `unresolved`.
- Bind structurally first (ownership, attribute, same container, same frame). Proximity pairing stores
  `distance`, `tolerance`, `runner_up`; tolerance is compared on unrounded values.
- Identifiers encode identity only, never sampling artefacts (index in a resampled list). Prevents FM-03.

## 5. Definitional slots (quantity cards)
Every delivered quantity declares: measurement convention, boundary (what is in and out), comparator
(`min | exact | max`), interpolation policy, unit, reference edge or datum, which layer or surface of a
layered body is delivered (for example finished grade vs subgrade vs earthworks line), variant handling,
and the executable definition it maps to. Constants live in a registry with citation and applicability
conditions. An assumptions register (every working choice, its evidence, its consumer) goes to the domain
expert in week one. Prevents FM-27, FM-06.

## 6. Artifacts and versions
- Every artifact header: `schema_version`, `run_id`, `code_rev`, `input_digests`, `tenant`, `purpose`
  (`compute | display | diagnostic`). Compute consumers never read `display`. Prevents FM-17, FM-25.
- Registered schema versions are immutable (content hash pinned). A meaning change bumps the version even
  when the shape is unchanged. Readers are BACKWARD_TRANSITIVE (read every older persisted version) and
  fail loudly on unknown versions. Prevents FM-02.
- Consumer matrix, kept next to the contract and tested in G2. Readers include internal tooling: CLIs,
  agent query tools, scripts, notebooks, monitors and docs builders.

| Artifact / field | Reader (runtime) | Fields read | Versions supported | Acceptance predicates (what makes the reader refuse or render empty) | Fixture tested |
|---|---|---|---|---|---|
| clause_register v3 | deadline-calendar (worker) | notice_period, effective_date | v2, v3 | refuses a clause without effective_date | v2 yes, v3 yes |
| clause_register v3 | review UI (web) | all | v3 | renders empty on an unknown schema version | v3 yes, v2 NOT-CHECKED |
| register_bundle (core, schedules, amendments) | contract page (web) | source_sha256 of all three | v3 | refuses unless all three source_sha256 are equal | v3 yes |

A cell without a tested fixture is a hazard. Every refusal or cross-artifact predicate a reader applies
is a seam invariant: a producer change is tested against it on the new version before merge. Prevents
FM-02, FM-15, FM-28.

## 7. Tenant isolation
Shard storage by tenant. Shared, multi-tenant artifacts change only through read-merge-write with an
expected entity set; a shrink needs an explicit, key-specific permission. A per-tenant job can write only
its own tenant's keys (enforced by the store, not by convention). Prevents FM-19.

## 8. Promotion and versioning
- Write-audit-publish: write to staging, audit with the G6 predicate, then move the pointer. Every path
  that moves a visible or base pointer (including fallback resolvers) calls the same predicate.
- The base of a run is an explicit last-passing version id. One in-flight run per entity; a concurrent
  run on the same base is refused, never merged by version number.
- Tightening the predicate re-evaluates existing pointers. Prevents FM-18.

## 9. Oracle separation
- Evidence namespaces assigned by a first-pass classifier before semantic mapping:
  `source_proposed | source_existing | reference | prior_answer | expert_decision`. References (answer
  keys, prior-year adjusted figures, registry gold labels, client-supplied totals) are tainted.
- The dependency graph forbids edges from `reference` into compute, prompts, fallbacks, cards and
  fixtures. Golden values carry `(run_id, input_digest)` provenance and are never typed by hand.
- Dev gold for tuning, holdout gold never inspected during tuning. Prevents FM-10, FM-22.

## 10. Human decisions
One decision store with a schema. An answer requires a typed value, a consumer key and a scope; its status
stays `answered_unapplied` until a version cites it (`application_verified`). Questions are deduped
against the store, the source text and prior correspondence, carry a location link, and are ranked by
unlock fan-out (how many slots one answer resolves). The agent drafts the questions; a human sends them.
Prevents FM-16, FM-30, ST-05.

## 11. Model-call envelope
Pinned model id and version; prompt hash; cache key `(model+version, prompt hash, input digest)`;
purpose and consumer key on every call; `n_requested`, `n_succeeded`; `finish_reason`. The model selects
among deterministic candidates or classifies; numbers that can be computed are computed. Evidence and
reasoning fields precede the answer field in structured output. One question per missing fact, with
candidates and the consumer key that will read the answer. Prevents FM-21, FM-09, ST-15.

## 12. Fail-closed vs provisional
A blocker emits a flagged provisional value (`status: assumed`, evidence, working choice) instead of an
empty slot, unless a wrong provisional value is worse than no value for the deliverable (decide per
quantity on the card). Compare alternatives on the outputs actually needed: if they give the same
delivered result, proceed with a working choice and flag it. Ordered assembly must not let one unknown
block independent parts. Prevents FM-30.
