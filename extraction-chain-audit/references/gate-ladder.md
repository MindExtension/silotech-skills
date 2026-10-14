# Gate ladder: earliest, cheapest detector first

Every hazard gets the LOWEST gate that can catch it. A higher gate is added only as a second,
independent layer (different inputs, code or method), never as the first line. Validation that exists
only at the final sink is a finding in itself. Shift-left rule (this is its one home): a defect first
caught at G5-G8 also opens a Process finding (escape root `late_gate`) against the missing lower-gate
detector, naming that gate. AUDIT path A may read this file for detectors; leave the FM ids in it aside
until path A is sealed.

| Gate | Where it runs | Typical cost | Blocks |
|---|---|---|---|
| G0 Design | contract and schema, before code | minutes of design | the bad state is unrepresentable |
| G1 Static | pre-merge, no data | seconds | the merge |
| G2 Behaviour | CI on fixtures | minutes | the merge |
| G3 Write-time | every artifact write, inside the run | milliseconds per write | that write, then the node |
| G4 Preflight | production image, 1-3 real records per tenant | 1-5 minutes | the expensive run |
| G5 Run audit | end of each stage in the real run | seconds per stage | the stage and its dependents |
| G6 Promotion | before a version becomes visible or a base | minutes | visibility |
| G7 Display / post-publish | readers, screens, exports, daily | seconds | the shown claim |
| G8 Independent / statistical | per release, per new source type | hours (labels, second path) | the release claim |

Economics: if a run costs R minutes, fails with probability f, and a preflight of p minutes catches a
share c of those failures, the preflight saves about f*c*R - p minutes per run. With the history in
`delivery-stalls.md` (f = 0.84, c = 0.72), R = 60 and p = 1 the saving is about 35 minutes per run,
before counting the human diagnosis time. Measure your own f and c with the run-economics procedure
there.

## G0 Design (prevent by construction)
Apply `contracts-by-construction.md`: value envelope (tri-state, status, scope, unit, provenance),
aggregate envelope (denominator, exclusions, contributing ids), closed vocabularies with explicit
`unresolved` and `assumed` members, definitional slots, immutable registered versions, tenant sharding,
reference taint, decision store with consumer keys, model-call envelope.
A schema enforces nothing until its enforcement layer is tested: when constrained decoding or a validator
library carries the contract, feed it one seeded violating output per keyword the contract relies on
(enum, pattern, required, nullability, ranges, nested references) and observe a rejection. Engines often
accept a schema yet ignore some of its keywords (`techniques.md` section G).

## G1 Static (seconds, pre-merge)
| Check | How | Prevents |
|---|---|---|
| Enum closure | collect every literal producers can emit (AST over code, vocabulary files, prompt option lists); assert subset of each consumer enum; reverse: every enum code is emitted somewhere | FM-01, FM-24 |
| Schema immutability | pin the content hash of every registered schema version; a changed registered version fails | FM-02 |
| Consumer matrix present | every artifact type lists its readers in every runtime (workers, API, UI, export, internal tools) with the versions they support and their acceptance predicates; every hard-coded supported-version or schema allowlist outside the registry is a second implementation and fails the duplicate-implementation lint unless it imports the registry (grep pack GP-12) | FM-02, FM-28 |
| Shared types | types for every runtime are generated from one schema; type-check scope covers every runtime folder | FM-02 |
| Read-failure lint | readers raise on unknown schema, unresolved pointer, missing file; no `except: return []` / default-empty | FM-04, FM-20 |
| Error-laundering lint | broad handlers in producers re-raise programming errors (name, type, import, attribute); entry points require their write flag | FM-05 |
| Identifier lint | no substring, prefix or LIKE matching on identifiers; one canonical parser and formatter per identifier family | FM-03 |
| Constant lint | every domain constant (code AND data cards AND prompts) has a citation and applicability; uncited fails | FM-06, FM-27 |
| Tenant-literal guard | flag literals (labels, layer or block names, phrases, regexes) that occur in exactly one tenant's corpus; scans code, data and prompts in every language; baseline stores identities, only shrinks | FM-26 |
| Display-field lint | compute consumers never read artifacts tagged `display` | FM-25 |
| Reader effect lint | effect, memo and data-fetch hook dependency lists hold only stable values (ids, primitives, memoized objects); an object or array built during render inside a dependency list fails (in React: `react-hooks/exhaustive-deps` as error plus an unstable-dependency rule) | FM-31 |
| Duplicate-implementation lint | registry of the canonical implementation per concept; a second emitter of the same quantity fails | FM-28 |
| Graph lint | every read has a producer or a declared source; every product has a consumer or a `diagnostic` tag; removing a producer that still has readers fails; no edge from a reference node into compute; run logs, job queues and other operational tables are graph nodes: a reader (RPC, view, doc) of a table whose writer was removed fails | FM-15, FM-17, FM-10 |
| Bundle derivation | the deploy bundle is derived from a scan of what producers read | FM-20 |
| Citation resolution | every guard, test, path and command cited in docs, plans and acceptance records resolves and has a runner, and each cited RPC, table or command still reads what the current producer writes (currency, not only existence) | FM-23, ST-11 |

### Grep pack (candidates, not findings)
Ids GP-1..GP-12 (distinct from gate ids) live in `grep-pack.tsv` next to this file: one pattern per row,
each with a sample it must match. Run `python3 <skill-dir>/scripts/grep_pack.py <paths> [--only GP-2,GP-9]
[--exclude 'test*']` (`--exclude` takes globs matched against each path component; an unknown `--only` id
is a usage error). It first runs every pattern on its own sample (a pattern that misses it is
NOT-CHECKED), then prints hits per id and the number of files scanned; a zero counts only when the control
passed, files scanned > 0 and no file was skipped for that id. Binary or unreadable files, and files over
2 MB for multi-line patterns (line patterns stream them), print as `SKIPPED` and make the id NOT-CHECKED;
exclude known binary types explicitly (`--exclude '*.png,*.pdf'`). Every hit is opened and judged: a
deliberate, logged, fail-closed path (listed in the intentional-state registry) is not a defect. Use it in
QUICK SCAN step 3 on touched files, in AUDIT path B over the whole chain, and GP-11 over output files and
fixtures.

| Id | Looks for | Modes |
|---|---|---|
| GP-1 | defaults on failure or missing; a handler that returns an empty default within 3 lines | FM-04, FM-05 |
| GP-2 | caps and truncation | FM-09 |
| GP-3 | substring identity matching (keep hits on identifier variables) | FM-03 |
| GP-4 | broad or swallowed errors | FM-05 |
| GP-5 | silent fallbacks and bare constants (keep hits near domain quantity names) | FM-06 |
| GP-6 | failure hidden by the runner; shell scripts without pipefail | FM-23 |
| GP-7 | reference leakage (also prompts and configs; `--exclude 'test*'`) | FM-10 |
| GP-8 | retry without a first-attempt record | ST-02, FM-21 |
| GP-9 | unpinned "current" reads | FM-17, FM-18, FM-28 |
| GP-10 | rounding before comparison | FM-03, FM-22 |
| GP-11 | undecoded escapes, replacement characters, mojibake, files that are not UTF-8 | FM-29, FM-08 |
| GP-12 | hard-coded supported-version or schema allowlists | FM-28, FM-02 |

## G2 Behaviour (CI, minutes, on fixtures)
- Property tests from the contract (round-trip `format(parse(id)) == id`, `parse(serialize(x)) == x`,
  idempotence, conservation under regrouping, monotonicity), with adversarial generators: empty, null,
  unresolved, duplicates, overlapping and zero-length ranges, extreme magnitudes, mixed units. FM-03, FM-25.
- Metamorphic relations (no oracle needed). Run each that applies on 1-3 recorded records per tenant:

| Id | Transformation | Expected output | Catches |
|---|---|---|---|
| MR-1 | permute pages, documents, files or layers | identical record set | FM-14, FM-21 |
| MR-2 | split the input in two, process each, combine | equals processing the whole (boundary loss, duplication) | FM-09, FM-13, FM-14 |
| MR-3 | duplicate one document | deduplicated, or exactly doubled counts; nothing else | FM-14 |
| MR-4 | change input units or scale | outputs scale exactly | FM-11 |
| MR-5 | translate or rotate coordinates | derived measures unchanged | FM-11, FM-25 |
| MR-6 | mirror, or reverse the reference direction | signs and orders flip consistently | FM-11 |
| MR-7 | add an irrelevant document or page | nothing changes | FM-10, FM-14, FM-29 |
| MR-8 | rename labels, tenants or files to neutral names; neutral names keep the source script (renaming to ASCII hides encoding defects) | values unchanged (overfitting to names) | FM-26 |
| MR-9 | remove one item | the aggregate drops by exactly that item's contribution | FM-12, FM-13, FM-14 |
| MR-10 | run tenant A alone vs A together with B | A's outputs identical (isolation, partition additivity) | FM-19 |
| MR-11 | change chunk boundaries or chunk size | same records (chunk-edge loss or duplication) | FM-09, FM-14 |
| MR-12 | the same model request twice | same parsed answer, or the noise floor is measured and recorded | FM-21 |

- Fault injection per producer: inject a programming error, the node must FAIL, not emit a domain status
  (FM-05); delete an input, the value must be `unavailable`, not 0 (FM-04); return an empty or
  length-truncated model answer, the wrapper must reject it (FM-21); delete the output, then run (FM-05).
- Position-aware canaries on fixtures: canary facts with known answers at the start, middle and end of
  long inputs and across chunk boundaries; any miss fails; report recall by position and length. FM-09, FM-21.
- Decision-table test of the promotion predicate over all states: full, partial, failed, sampled or
  profile run, legitimate shrink, registry lag, concurrent run. FM-18.
- Differential test of twin implementations and of verifier vs producer on the same inputs. FM-28.
- Oracle removal: run with reference files removed or perturbed; outputs must be bit-identical. FM-10.
- Consumer-existence mutation: mutate one field, answer or card; the final output must change. FM-15, FM-07, FM-16.
- Migration test: status, assumption and evidence-count histograms are preserved old to new. FM-07.
- Cold tenant: a synthetic or renamed tenant runs end to end from upload to first visible version. FM-26.
- Tenant isolation: each producer runs in a workspace holding one tenant; other tenants' bytes unchanged. FM-19.
- Script fixtures: at least one fixture per tenant language whose labels, names and identifiers carry its
  national characters; decode, display and export must round-trip them byte-exact. FM-29, FM-08.
- Queue tests: two or more jobs of different kinds and resource classes, a job enqueued during the pass,
  an unexpired lease, a worker killed after claim; the test asserts the per-pass conservation line (G5),
  not only the returned status. FM-09, ST-14.
- Read tracing: an audit hook records every file or table read; undeclared reads fail. FM-17.
- Status mapping: exhaustive status-to-style test, unknown states render neutral or red; one fixture per
  diagnostic code triggers exactly that code. FM-24.
- Metric contract: `checked > 0`, a non-shrinking checked set, the denominator printed with every
  percentage; deleting output in one region must lower the score, not raise it. FM-22.

## G3 Write-time validation (every artifact write)
- Validate against the contract when written, not at final publish; unknown enum value or missing
  envelope field rejects the write. FM-01, FM-04.
- Natural-key uniqueness; unit-typed sums refuse mixed units. FM-14.
- Shared artifacts: expected-entity set, read-merge-write, refuse to shrink without an explicit,
  key-specific permission whose baseline the executor cannot delete. FM-19.
- Referential integrity at write: every key, path or id an artifact references resolves in the pinned
  input set of this write (same version, same tenant or declared shared); a dangling reference rejects the
  write, not the publish. Corpus-level readers of per-tenant artifacts pin (tenant, version) per input.
  FM-17, FM-19.
- Every fallback writes a counted assumption record; invariant `fallback_fired => assumption_count > 0`. FM-06.
- Cross-field identities per record (parts sum to whole, start < end, derived difference equals labelled
  difference, assumption implies status not observed). FM-29, FM-07.
- Post-node: each declared output's hash changed, or an explicit `unchanged, same input digest` record. FM-05.
- Stamp run id, code revision, input digests, schema version, tenant and purpose on every artifact. FM-17.
- Model-call wrapper: reject empty completions, `finish_reason = length`, budget stops and echoed
  defaults; record `n_requested` and `n_succeeded`; quorum is computed over requested members; cache key
  `(model+version, prompt hash, input digest)`; purpose and consumer key logged; first-attempt failure
  rate logged for any retry or self-repair loop. FM-21, FM-09.
- Durability: a node is `done` only after re-reading the persisted object; unsaved keys == 0. FM-20.
- A violation stops the partition, not the whole run (see G5, stop the line).

## G4 Preflight battery (before any run over ~10 minutes or any paid batch)
Runs inside the production image with production config against a scratch sink (truth rule 9 in SKILL.md:
print and confirm the sink, cache and model endpoints first). Every item is tri-state, and any FAIL or
NOT-CHECKED on an applicable item blocks the expensive run. An item that cannot apply (P9 when the chain
has no model stage) is `not_applicable` with the chain-map feature answer as its reason. P1-P4, P6, P7 and
fingerprint items always apply; P5 is `not_applicable` only for a tenant's first run or a chain with no
published versions, citing that feature answer.

| Id | Check | Catches |
|---|---|---|
| P1 | Running code revision equals the expected commit; image built from it | FM-17, FM-20 |
| P2 | Schema hashes unchanged; every reader supports every version this run will write | FM-02 |
| P3 | Enum closure on the code actually deployed | FM-01 |
| P4 | Every declared input, pointer, config, citation and reference index resolves inside the image; each declared role has count > 0; container and modality census per tenant; every extracted text field decodes (no literal `\U+`, `\M+`, `%%`, `&#`, U+FFFD or mojibake in smoke records) | FM-04, FM-08, FM-20, FM-29 |
| P5 | The base is an explicit last-passing version and still passes the promotion predicate | FM-18 |
| P6 | Smoke records: 1-3 recorded real records per tenant through the full chain, including write-time validators and the final consumers (UI and export readers) | FM-01, FM-02, FM-05, FM-21, FM-24 |
| P7 | Dry-run write diff: the run writes only its own tenant's keys | FM-19 |
| P8 | Budget extrapolation: smoke timing x size of the largest tenant vs platform time, memory and payload limits | FM-20 |
| P9 | Model stages: canary record with a known answer (position-aware for long inputs), cache hit on a replayed request, 20-item pilot with measured acceptance rate before any batch over ~100 calls | FM-21, FM-09, ST-15 |
| P10 | Environment: import every dependency (not one), secrets present (never printed), sink writable | FM-20 |

Add one item per catchable failure fingerprint from the run history (run economics, `delivery-stalls.md`
ST-01); name it `P<n>+<fingerprint>` so the run record shows which past failure it prevents.

Smoke-record selection per tenant: (1) the record that exercises the most rare branches (null,
unresolved, assumed, fallback, alternative variants); (2) the largest or most complex record; (3) a record
from the newest source format or the area just changed; (4) when the change deletes, moves, renames or
cleans up inputs or intermediate files, a record whose deleted or moved item is still referenced
downstream (page images, attachments, cached tiles), so dangling references fail in preflight, not at
publish. Records are captured from real sources, stored as fixtures with digests, and refreshed when a
tenant's sources change.

Expectation record (written before launch, never after seeing results): for each published aggregate
with S >= 7 and each tenant, the expected value or range from an independent route (last accepted
version, a disaggregated estimate by stratum, a control total from another source), the acceptable
difference, and the breach procedure (who investigates, what is held). G5 compares against it; a breach
runs the procedure and opens an INCIDENT. Matching the expectation is not proof of correctness, and a
result that matches a hypothesis suspiciously exactly is itself a reason to look.

Keep-going mode: on smoke records the chain continues past failures and collects ALL errors into one
report keyed by `(node, error class, field path)`. Fix all of them, rerun preflight, then start the
expensive run. Pilot one tenant (smallest complete one) through the full run and promotion before
fanning out to all tenants.

## G5 Run audit (end of each stage, in the real run)
- Record conservation per stage: `in = out + rejected(reason) + merged(reason)`, with a hash total of
  entity keys; per stratum (source type, tenant, category) so a loss concentrated in one group shows; for
  file ingest, against an independent raw row count per file and template variant. Also per worker pass
  and per batch: `available_at_start = done + failed(reason) + deferred(reason: claim cap, lease held,
  resource-class slot, enqueued during pass)`; a pass that returns success with deferred > 0 and no
  reason fails. All FM.
- Census vs consumed per carrier; census > 0 and consumed = 0 stops the tenant. FM-08.
- Join coverage per key family: matched, left-only, right-only, multiplicity; 0% hits or unexpected
  multiplicity alarms. FM-03.
- Cap counters: `n_available` vs `n_used` for every limit, slice, top-N, size skip. FM-09.
- Every zero is paired with a reached-step count and a positive control (a known-present sibling found by
  the same lookup). FM-04.
- Counters `solved` vs `fallback_used` per node; share of non-observed values per delivered field. FM-05, FM-06.
- Yield per extractor per tenant and default-bucket share; near-zero yield fails. FM-26.
- Block-code concentration: one code over 90% of entities alarms. FM-30.
- Each S >= 7 aggregate against its expectation record (G4): outside the acceptable difference runs the
  pre-written breach procedure; volume and value distribution per seam against the previous run.
- Distribution smell scan per field and tenant (also the cheapest independent path B in AUDIT): round
  constants across inputs of different size; a child value equal to its neighbour's or the cohort median;
  identical values at distinct locations; a provenance field with one value across N items; a large
  distance between a value and its nearest evidence; constant point or row counts per entity; sentinel
  values (0, -1, 9999) standing for unknown; numbers stored as text; mixed units in one column;
  undecoded escape sequences, replacement characters or mojibake in text fields; national characters
  present in the source census but absent from the output. A smell above threshold with no recorded
  explanation fails. Seed: replace a measured field with its median. FM-06, FM-07, FM-11, FM-12, FM-25, FM-29.
- Windowed residuals instead of global averages; multimodality test before a single-statistic summary;
  plausibility bounds (extent, scale, coordinate system, units, geometry validity). FM-29.
- Frame health without a reference: features are distributed as the domain specifies around the
  reference frame, and shared landmarks agree across artifacts; a failed frame verdict blocks export. FM-11.
- Position-aware canaries on real-shaped inputs: canaries planted in long inputs of this run are all
  recovered; recall by position and length is logged. FM-09, FM-21.
- Stop the line per partition: when a G3 or G5 detector fails, stop only the affected partition
  (document, entity, tenant), mark its dependents blocked, keep inputs and intermediate state for
  diagnosis, never fall back silently. S >= 7 stops; lower severities flag and continue. Track the stop
  rate per run: near-zero stops on complex new inputs suggest insensitive detectors (run the guard audit).

## G6 Promotion (write-audit-publish)
A version becomes visible or becomes a base only if ALL hold; every rejection records its reason.
1. Required key set present for the tenant; zero failed and zero skipped nodes (skip = fail). FM-18, FM-17.
2. One code revision across the version; all inputs from the same version AND, for artifacts any reader
   combines, the same root source digest (lineage homogeneity). Regenerating a legacy artifact inside the
   new version does not make it homogeneous if its root source differs. FM-17.
3. Every artifact belongs to the version's tenant; no cross-tenant key or content-hash overlap for
   artifacts that are not declared shared. FM-19.
4. Every reader supports every schema version present. FM-02.
5. Status fields computed from a content checklist (required parts present, cross-quantity identities
   within tolerance, mandatory gap list when upstream knows of holes), never from schema validity. FM-24.
6. Aggregates carry covered/total in the deliverable's physical unit and an excluded bucket with reasons;
   share of non-observed values under its threshold. FM-13, FM-06.
7. Key-level diff vs the last accepted version: every added, removed or changed record maps to an
   expected-change list; unexplained diffs block. Model stages first measure an A-A noise floor (same
   version twice). A change above 10% on any delivered aggregate needs a stated reason. FM-27, FM-22.
8. Answered-but-unapplied human decisions for this tenant = 0 or listed in the version notes. FM-16.
9. The base for the next run is this explicit version id, never "latest" or "displayed"; one in-flight
   run per entity. FM-18.
10. Every final consumer in the consumer matrix (UI pages, exports, API, agent and CLI read tools) reads
    and renders the candidate version on the smoke keys; any reader refusal blocks visibility. FM-02, FM-17.

Moving the visible or base pointer is a side effect: it needs the user's yes or a standing permission
(truth rule 9 in SKILL.md).

## G7 Display and post-publish
- Runtime budget after every deploy that changes a reader (an auto-deploy from the main branch moves the
  visible code pointer): open the shown version on the live or preview surface with the instance printed;
  per page load, identical requests per (version, key) <= 1 within 60 s, total requests and function
  invocations under a stated budget, console errors = 0, loaded state within a stated time. Seed: a
  dependency list holding an object rebuilt each render. FM-31.
- Daily: the shown version satisfies the CURRENT predicate (re-evaluated after any tightening) and no
  newer allowed version is hidden. FM-18.
- Render-time assertion: all artifacts on one page share one version set; every read pins (entity, version). FM-28.
- Cross-count: screen count == index count == source census. FM-04.
- Show version age and code distance from HEAD; alert when no successful version exists from recent code. FM-17.
- Queue health: answered-unapplied count, closed/opened ratio per review queue, alarm on zero closures. FM-16.

## G8 Independent and statistical (per release, per new source type)
- Stratified gold set with dev split and a never-inspected holdout; fact-level unit tests (value V for
  item K at locator L; item K absent; A precedes B). FM-10, FM-26.
- Alignment buckets: align predicted to gold records first (stable keys, unit tolerance), then report per
  field and stratum: matched-correct, matched-wrong, missing, spurious, duplicated. Never one macro score.
- Selective editing for scarce review: score = suspicion (validator flags, path disagreement, model
  instability, distance from a predicted value) x impact (share of a delivered total the item moves);
  review the top scores AND a random stratified audit of the unselected items (by tenant, source type,
  field class) to measure what the routing misses. The checker re-derives each value from the source
  without seeing the extracted value; a dependent check is not an independent layer. FM-03, FM-11, FM-29.
- Source data verification in both directions on critical fields: output-to-source (precision) and
  source-to-output (recall, from an independent expected-presence list such as a table of contents,
  legend or schedule). FM-08, FM-29.
- Independent derivation path for the 3-5 most consequential aggregates (different method and, where
  possible, different inputs; checker blind to intermediate results; error correlation measured on gold
  before agreement counts). FM-13, FM-14, FM-28.
- Prediction-powered (rectified) totals with a confidence interval from a random gold sample; a pipeline
  total outside the interval means systematic bias, the per-stratum rectifier shows where. FM-13.
- Error grouping: label checked records right or wrong with features (source type, template, author,
  page kind, extractor and prompt version, field); find feature sets whose error rate is far above
  baseline. When an aggregate deviates, localise first with leave-one-group-out deltas over its
  contributing records by each feature, then generalise with the grouping. One group = one platform fix.
  FM-26, ST-06.
- Stage attribution by oracle substitution: on a small golden subset keep gold intermediates per stage;
  evaluate each stage with gold inputs (isolated) and predicted inputs (end to end). A stage wrong in
  isolation while end to end looks right means compensating errors; end-to-end error above the sum of
  isolated errors means amplification.
- Configuration bisection for a regression with no obvious diff: log every run's full configuration
  (model, prompt hash, parser version, config values, input set); swap one component at a time between
  the last good and first bad run until the flipping component is isolated; repeat model stages enough
  to clear the A-A noise floor. The minimal flipping set is the finding's reproduction. FM-17, FM-21, FM-28.
- Invariant mining from accepted versions: mine value ranges, linear relations between fields, orderings,
  records per page and in/out ratios per stage; a human promotes useful ones into G3 or G5 checks with
  thresholds from run history. Mined invariants inherit bugs in the accepted versions: review first.
  FM-07, FM-11, FM-12, FM-29.
- Judge TPR/TNR and witness error-correlation audit before agreement counts as confirmation. FM-21, FM-10.
- 4-cell metric decomposition (old/new metric x old/new chain on one version). FM-22.
- Labelled sensitivity table over definitional choices. FM-27.
- Capture-recapture residual estimate (see `hunt-and-stop.md`).
