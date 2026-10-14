# Failure-mode catalog (FM-01 .. FM-31)

Distilled from 319 defect instances in one multi-tenant extraction product, generalized. Each card has
five fields plus an example: Signature (what you see), Prevent (G0 and design), Detect (detectors by gate,
cheapest first), Probe (the read-only audit query), Slipped (how existing guards missed it in practice:
check your own guards for the same hole). Use it four ways: BUILD (apply "Prevent"), AUDIT path B (run
"Probe" on the pinned instance, in the order from `selection.md`), INCIDENT (match the signature via
`symptom-index.md`, then use "Detect" to pick the earliest detector), guard audit and INCIDENT guard
autopsy (compare each guard with "Slipped"). AUDIT path A does not read this file until it is sealed;
then the guideword and UCA map at the end turns its rows into FM ids. Examples illustrate a class and must
not reproduce evaluation or backtest cases; when a case matches an example nearly word for word, record
that path B was example matching (it then counts as one path with A, `hunt-and-stop.md` section 3).
Gates G0-G8 are defined in `gate-ladder.md`, MR ids in its G2, GP ids (grep pack) in its G1. Root
letters: C collection, S structure, L logic, O operations, P process. Guidewords from `hazard-sweep.md`.
Modes marked * were the ones most often left with no guard at all in the source history; check them first.
New modes found in an audit or incident are added as `FM-NEW-<n>` cards with the same fields.

| Id | Name | Root | Guideword | Earliest gate | Silent? |
|---|---|---|---|---|---|
| FM-01 | Closed-vocabulary drift | S | OTHER THAN | G1 | loud but late |
| FM-02 | Contract and version drift across seams | S | OTHER THAN, EARLY | G1 | loud on main path |
| FM-03* | Entity association and key errors | C, L | OTHER THAN | G1 | silent |
| FM-04 | False absence, tri-state collapse | L, C | NO | G0 | silent |
| FM-05 | Error laundering, no-op success | L, S | NO | G1 | silent |
| FM-06 | Silent fallback presented as fact | L | AS WELL AS | G0 | silent |
| FM-07 | Provenance and status loss across transforms | S | PART OF | G0 | silent |
| FM-08 | Incomplete carrier traversal | C | PART OF, NO | G4 | silent |
| FM-09 | Silent truncation, caps, skips | C, O | LESS | G3 | silent |
| FM-10* | Evidence-class confusion, oracle leakage | P, C | AS WELL AS | G1 | silent |
| FM-11* | Reference frame and convention mismatch | C, L | REVERSE, WRONG FRAME | G0 | silent |
| FM-12* | Aggregate scope loss | S | WRONG SCOPE | G0 | silent |
| FM-13* | Coverage accounting failures | S, L | PART OF | G0 | silent |
| FM-14* | Double counting | S | MORE | G0 | silent |
| FM-15 | Unconsumed facts, orphan producers/consumers | S | NO | G1 | silent |
| FM-16* | Open-loop human decisions | S, P | NO, LATE | G0 | silent to the chain |
| FM-17* | Lineage and freshness failures | S, O | STALE | G2 | silent |
| FM-18 | Unguarded promotion, racing versions | L | EARLY, STALE | G2 | silent |
| FM-19* | Shared multi-tenant state clobber | S, L | AS WELL AS | G0 | silent |
| FM-20* | Environment divergence, durability gaps | O | OTHER THAN | G1 | mixed |
| FM-21* | Unpinned or degenerate model stages | S, O | OTHER THAN, NO | G3 | silent |
| FM-22* | Measurement-instrument defects | P, L | OTHER THAN | G2 | silent |
| FM-23* | Vacuous, phantom, narrow-scope guards | P | NO | G2 | silent |
| FM-24 | Status fields not computed from content | L, S | OTHER THAN | G2 | silent |
| FM-25* | Lossy representation reused downstream | S, C | LESS, WRONG FRAME | G1 | silent |
| FM-26 | Development-instance overfitting | S, L | OTHER THAN | G1 | silent |
| FM-27 | Domain definition and convention gaps | S, L | PART OF, WRONG FRAME | G0 | silent |
| FM-28* | Divergent duplicate implementations | S | AS WELL AS | G1 | silent |
| FM-29* | Source defects accepted as truth | C | AS WELL AS | G3 | silent |
| FM-30 | Over-blocking fail-closed cascades | S | NO | G5 | loud as blocks |
| FM-31 | Unbounded reader runtime (render loops, request storms) | L, O | MORE | G1 | silent in tests, loud in cost |

---

### FM-01 Closed-vocabulary drift between producer and consumer
- Signature: late hard failure naming one enum field and an unknown value from a rare branch (null,
  unresolved, assumed); fixes arrive one value per expensive run.
- Prevent: one shared vocabulary registry; explicit `unresolved` and `assumed` members; unknown abstains.
- Detect: G1 enum closure both directions; G4 smoke records carrying every rare state; G3 write validation.
- Probe: list distinct values per categorical field across all tenants in the pinned version; diff each
  against every consumer enum; list producer branches that return string literals.
- Slipped: the closure test covered one vocabulary of several; local validation on a stale cache found 0
  mismatches while production rejected about a quarter of records. Check scope and instance.
- Example (legal): the clause taxonomy lacks "hybrid indemnity"; the batch crashes after OCR and model
  spend.

### FM-02 Contract and version drift across seams
- Signature: a feature never worked end to end; all readers break when a new version becomes visible; one
  version id with two contents; fixes land one reader at a time.
- Prevent: one schema generates all runtime types; registered versions immutable; meaning change bumps
  version; readers fail on unknown versions; publish only after readers declare support.
- Detect: G1 schema hash pin; G2 consumer matrix (every reader x N and N-1 fixtures); G2 contract test
  feeding the real caller-built payload into the callee validator (not a mocked form); G6 visibility
  refusal.
- Probe: build the consumer matrix; every untested cell is a hazard; check type-check scope covers every
  runtime folder.
- Slipped: the schema registry refused mutations only at the last step; a test asserted the caller's own
  payload form; one code folder sat outside the type-check scope.
- Example (clinical): form v2 adds a field; the registry loader still parses v1 and drops it silently.

### FM-03 Entity association and key errors
- Signature: near-0% join hit rate for one key family, or plausible values on the wrong entity; the same
  entity under several names; ambiguity never recorded.
- Prevent: canonical parser/formatter per identifier family; alias crosswalk; structural binding before
  proximity; proximity records distance and runner-up; tolerance on unrounded values.
- Detect: G1 ban substring/prefix matching and second formatters; G2 round-trip property on a golden corpus
  of real spellings; G5 join coverage and multiplicity per key family; rename rate across adjacent samples.
- Probe: per join and tenant compute matched / left-only / right-only / multiplicity; sample 20 matches and
  verify ownership in the source.
- Slipped: generality and literal guards cannot see key formats; a tolerance was compared on values rounded
  twice.
- Example (legal): "Seller" matched inside "Seller Parent" attaches obligations to the wrong party.

### FM-04 False absence and tri-state collapse
- Signature: "none", "0" or "clean" while the source has the item; screen, index and census disagree; zero
  counts on steps never reached.
- Prevent: value-envelope `state`; readers raise on unknown schema, unresolved pointer, missing file.
- Detect: G1 lint default-empty on read failure, grep pack GP-1; G2 delete an input, require `unavailable`;
  G4 resolve every declared pointer with count > 0; G5 zero + reached count + positive control; G7 screen ==
  index == census.
- Probe: list every place a zero, none or empty is displayed or aggregated; for each, show the reached count
  and a positive control; if you cannot, it is a candidate.
- Slipped: the principle existed only as prose; after a layout change, skipped tests counted as passes.
- Example (clinical): "no adverse events" because the event page was a scan that OCR skipped.

### FM-05 Error laundering and no-op success
- Signature: node "executed" while its output hash is unchanged; programming errors never surface; after a
  code change a whole class of entities sits in one domain status.
- Prevent: fail fast; programming errors re-raised; exit 0 never means "output produced"; fallbacks return a
  fallback flag, not success.
- Detect: G1 broad-handler lint, grep pack GP-4; G2 inject a programming error per producer (must fail),
  delete output then run; G3 output-hash change or explicit "unchanged" record; G5 solved vs fallback
  counters.
- Probe: read every broad exception handler in producers and what it emits; compare output hashes of two
  runs with different inputs. Deliberate, logged fail-closed paths are not bugs: check logging and status
  first.
- Slipped: the guard requiring an explicit write flag was opt-in, so most producers never registered.
- Example (finance): an FX error is caught, the amount stays in source currency, the statement still
  balances.

### FM-06 Silent fallback or default presented as fact
- Signature: suspicious round constants (the same value, say exactly 30 or 0.5, across inputs of very
  different size); child equals neighbour median; assumption count 0 while fallbacks fired; the client says
  the value is not in their source.
- Prevent: no defaults for domain quantities; constants registry with citation; every fallback writes an
  assumption record and a non-observed status.
- Detect: G1 uncited-constant lint over code, cards and prompts, grep pack GP-5; G3 `fallback_fired =>
  assumption_count > 0`; G5 distribution smell scan (constants, neighbour equality); G6 non-observed share
  threshold.
- Probe: histogram each numeric field per tenant; round or repeated modes across inputs of different size
  are candidates; trace each to a code or data constant.
- Slipped: citation checks covered data cards but not constants in code.
- Example (finance): a missing depreciation life defaults to 5 years for every asset class.

### FM-07 Provenance, status and attribute loss across transforms
- Signature: status histogram changes across a migration with no data change; one provenance value across N
  items; fewer flags downstream than upstream; provenance labels far from any evidence.
- Prevent: epistemic fields are part of the contract and copied by construction; migrations map each one.
- Detect: G2 migration histogram test; G2 flip-a-flag mutation must change consumer output; G3 cross-field
  rule on assumption vs status; G5 flag-count conservation; provenance cardinality alarm; distance to
  evidence.
- Probe: per transform, count each status and flag value in vs out.
- Slipped: schema validation checked shape only; one provenance field mixed values of several kinds.
- Example (clinical): a "probable" diagnosis becomes a confirmed code in the warehouse.

### FM-08 Incomplete carrier traversal
- Signature: an entity class is zero for one tenant while a census shows it present; facts in schedules,
  nested blocks, legends or images never reach output; experts get asked what the source already says.
- Prevent: iterate every carrier of a role (all files, nested containers, all entity types, all lines, every
  modality) or record a skip with a reason in a consumption registry.
- Detect: G4 container and modality census incl. nested definitions and unknown objects after conversion; G5
  census > 0 and consumed = 0 stops; G8 source-to-output verification.
- Probe: build the census for one tenant through an independent raw parser and diff against what the
  extractor consumed. An inventory check must prove sources were read, not that an inventory exists.
- Slipped: the inventory check confirmed that an inventory existed, not that sources were read; it stayed
  green with most source sheets unread.
- Example (finance): footnote tables stored as images are skipped; contingent liabilities never reach the
  total.

### FM-09 Silent truncation, caps, skips and filters
- Signature: suspiciously round processed counts; a budget ends with 0 answers; "done" with skipped counts;
  an input class vanishes after a performance change.
- Prevent: every cap logs its dropped count; artifacts carry `n_available` and `n_used`; full coverage
  asserted unless a sampling flag is set; skip propagates as blocking to dependents.
- Detect: G1 grep pack GP-2; G3 model wrapper fails on length or budget stop; G2 and G5 position-aware
  canaries (start, middle, end, chunk boundaries); G5 cap counters and per-pass queue conservation
  (deferred jobs carry a reason); G6 retained-vs-dropped diff by semantic class after a filter change;
  G2 MR-2 and MR-11 (split and chunk-boundary relations).
- Probe: grep slices, limits, top-N, max tokens, size skips, `continue` in loops; find each dropped count in
  the run record; missing count = finding.
- Slipped: no specific guard existed.
- Example (legal): the context window truncates a 200-page agreement and termination clauses vanish.

### FM-10 Evidence-class confusion and oracle leakage
- Signature: accuracy too good; totals inflated by objects the source owner calls "existing"; card values
  equal reference values; output changes when the reference file is removed.
- Prevent: evidence namespaces assigned first; reference taint; graph forbids reference-to-compute edges;
  golden values carry provenance; dev and holdout gold.
- Detect: G1 taint lint and grep pack GP-7 over prompts, cards and fixtures; G2 references removed or
  perturbed, outputs bit-identical; G8 witness independence audit.
- Probe: copy the smallest tenant, delete every reference input, rerun, diff.
- Slipped: the leak guard protected one configuration key, not file-level reads; the oracle-separation rule
  lived only as text.
- Example (finance): prior-year auditor-adjusted figures used as prompt hints inflate measured accuracy.

### FM-11 Reference frame and convention mismatch
- Signature: systematic offset growing along a sequence; mirrored features with correct totals; two inverted
  conventions cancelling in the pilot; 100x or 1000x errors; identical point counts for entities of any
  size.
- Prevent: typed unit, sign, side, direction from one convention module; frame id and verdict per tenant;
  a failed frame verdict blocks export; resample by resolution, not fixed count.
- Detect: G2 MR-4, MR-5, MR-6 (unit scaling, translation, mirror and reversal); G5 frame health and
  physical-rank invariants; point count vs length.
- Probe: run one record mirrored, reversed and rescaled; compare with the expected transformation.
- Slipped: a frame verdict was computed and nothing consumed it; frame health was stored as prose.
- Example (finance): one subsidiary's debit/credit sign is flipped and netting hides it in the consolidated
  total.

### FM-12 Aggregate scope loss
- Signature: identical values at distinct locations; a local value equals the whole entity's extent; totals
  right, per-sample shape wrong; a portfolio verdict shown per item.
- Prevent: `scope` on every value; consumers assert expected scope; no extremum of a heterogeneous group
  used as a measure.
- Detect: G3 scope assertion at read; G5 identical-values-at-distinct-keys flag and witness constancy; G6
  per-sample checks alongside totals.
- Probe: count runs of identical values across distinct keys per field and tenant.
- Slipped: sum and extent conservation gates passed on matching totals; plausibility bounds were warnings.
- Example (clinical): the worst lab value of the admission is stored as "value at discharge".

### FM-13 Coverage accounting failures
- Signature: 100% coverage despite known holes; totals more than 10% short of a reference with no exclusion
  list; "31 of 31" after the 14 hardest cases were dropped.
- Prevent: aggregate envelope with physical-unit denominator and reasoned exclusions; scope markers
  extracted first and denominators reconciled against them.
- Detect: G3 partition conservation (every zone has a value or an explicit gate; removing a zone must
  produce a gate); G6 excluded count published and compared on a proxy; G8 rectified totals, signed vs
  absolute deviation.
- Probe: for every delivered aggregate, ask for denominator and exclusion list; absence is a finding.
- Slipped: one count-based shrink guard caught a single extent drift; nothing enforced a denominator.
- Example (legal): contracts that failed OCR drop out of portfolio exposure without a count.

### FM-14 Double counting and non-disjoint aggregation
- Signature: totals about 2x for some tenants; duplicate natural keys (sometimes a UI duplicate-key crash);
  a layered component counted twice; area added to volume.
- Prevent: unit-typed sums; key uniqueness at write; alternative-variant group keys carried end to end;
  half-open intervals at seams.
- Detect: G3 uniqueness; G2 MR-3 duplication; G5 dedup census and every grouping dimension a partition
  (sum over groups = parent aggregate); union extent vs sum of parts; G8 contributor multiplicity = 1.
- Probe: group by natural key, count > 1; list summed groups that are alternatives.
- Slipped: no structural guard; reviewers caught cases by eye.
- Example (finance): an intercompany sale counted in both entities' revenue.

### FM-15 Unconsumed facts, orphan producers and consumers
- Signature: "we pushed code but nothing moves"; mutating a field changes nothing; readers of deleted
  producers show zero or perpetual "in progress".
- Prevent: every field declares its consumer key; reads are declared; deleting a producer needs its readers
  gone.
- Detect: G1 graph lint; G2 consumer-existence mutation; G5 "extracted but unconsumed" and "output rows with
  no candidate facts" metrics.
- Probe: per extracted field find a reader by artifact key (not by import); mutate and diff the final
  output.
- Slipped: a field-reader test covered product fields only; liveness was judged by imports, missing readers
  that address artifacts by key.
- Example (clinical): the allergy list is abstracted but the conflict check reads a legacy column.

### FM-16 Open-loop human decisions
- Signature: answered-but-unapplied grows; repeated questions; review queues with zero closures; most new
  findings are already answered.
- Prevent: one decision store; answers carry typed value, consumer key, scope; `answered_unapplied` until
  cited.
- Detect: G3 reject answers without consumer key; pre-send dedupe; G6 unapplied count; G7 closed/opened
  ratio and inbox-to-store sync; finding generators dedupe by root and range.
- Probe: sample 10 answered decisions; check each changed an output in the latest version.
- Slipped: the decision store recorded the application gap but nothing gated on it.
- Example (legal): counsel's ruling stays in email and the extraction keeps flagging the clause.

### FM-17 Lineage and freshness failures
- Signature: fixes never reach the product; two screens disagree; an artifact's code revision is older than
  the rule it depends on; fresh timestamp, old content; score moves with no code change; a shared index
  publishes references to keys that one tenant's recompute removed or renamed.
- Prevent: stamp run id, code revision and input digests; freshness by digest, never timestamp; skip = fail.
- Detect: G2 read tracing; G4 running revision check; G6 lineage homogeneity; G7 version age and code
  distance.
- Probe: list the shown version's artifacts with code revisions and input digests; any mix is a finding.
- Slipped: a freshness gate warned while most nodes were stale and nobody read it; undeclared inputs were
  logged at warning level only.
- Example (finance): consolidation reruns while the FX table stays cached from last month.

### FM-18 Unguarded promotion and racing versions
- Signature: users see an empty or partial product; the next run fails on a partial base; a correct smaller
  version is never shown; a user's change vanishes after a concurrent run.
- Prevent: write-audit-publish; explicit base; one in-flight run per entity; all pointer paths use one
  predicate.
- Detect: G2 decision-table test of the predicate; G6 promote on pass only; G7 daily re-evaluation.
- Probe: enumerate every code path that moves a visible or base pointer, including fallbacks; check each.
- Slipped: the guard came after the incidents, ran only on state transitions and judged by artifact count.
- Example (clinical): a snapshot with half the sites loaded becomes the analysis cut.

### FM-19 Shared multi-tenant state and partial-writer clobber
- Signature: tenants disappear from a shared file and tests get greener; one tenant's snapshot shares keys
  or hashes with another; one tenant's stale entry blocks another's run.
- Prevent: shard by tenant; read-merge-write with expected entity set; shrink needs key-specific permission.
- Detect: G2 isolated-workspace byte-identity test and MR-10; G3 expected-entity assertion; G6 ownership and
  cross-tenant overlap check; negative authorization test for cross-tenant writes.
- Probe: hash every non-shared artifact across tenants in the shown versions; identical hashes are
  candidates. A shrink guard whose baseline the executor can delete passes vacuously: check where the
  baseline lives.
- Slipped: the shrink guard's baseline lived in a workspace the executor deleted, so it passed on an empty
  baseline.
- Example (finance): one entity's rerun overwrites the group-wide account mapping table.

### FM-20 Execution environment divergence and durability gaps
- Signature: works locally, fails or degrades in production; a missing file read as empty; "done" with no
  results; one transient error at the end discards hours; limits hit only the largest tenant.
- Prevent: bundle derived from reads; `require_file` raises; clean-room build; checkpointed idempotent
  nodes.
- Detect: G1 bundle derivation; G4 resolution inside the image, every dependency imported, largest-tenant
  budget extrapolation; G3 re-read before `done`; retry policy separates transient from deterministic.
- Probe: diff files read in a production run against the bundle; diff dependency versions local vs image.
- Slipped: a healthcheck imported one dependency and reported PASS with most packages missing; a unit test
  mocked the writer, so a key-format mismatch never ran.
- Example (clinical): the production container lacks the abbreviation dictionary; recall drops silently.

### FM-21 Unpinned or degenerate model stages
- Signature: same request, different parsed mapping; agreement computed over survivors only; zero calls with
  no error; budget spent with zero applied results.
- Prevent: model-call envelope; cache by request digest; model selects among deterministic candidates.
- Detect: G3 wrapper rejects empty, truncated, echoed defaults and degraded quorum; G2 replay twice and diff
  (A-A noise floor); G4 20-item pilot; G8 judge TPR/TNR and error-correlation audit.
- Probe: count calls lacking version or consumer link; replay 10 cached requests uncached and diff.
- Slipped: a call log existed but its run and purpose fields were never filled.
- Example (legal): the clause classifier labels the same clause differently on rerun and the report flips.

### FM-22 Measurement-instrument defects
- Signature: a score improves while no common value changed; a "regression" appears because the measured set
  grew; a uniform offset with tiny spread reported as shape error; scores depend on uncommitted code.
- Prevent: sampling grid fixed by the reference, not by the output; denominators printed with every
  percentage; comparison contract (both sides declare quantity class and frame); baselines store a settings
  hash; metric code versioned.
- Detect: G2 `checked > 0` and non-shrinking denominator; G8 4-cell decomposition; baseline refreeze only in
  a separate change with a diff of the measured set.
- Probe: recompute numerator and denominator separately for the last two versions of each headline metric.
- Slipped: the fixed-grid gate arrived after the incident; older baselines stored no settings.
- Example (clinical): F1 rises after notes that fail to parse are dropped from the evaluation set.

### FM-23 Vacuous, phantom and narrow-scope guards
- Signature: a green suite stays green under injected faults; docs cite missing guards; a guard is bypassed
  by moving logic into data files; steps "done" although their verification cannot run.
- Prevent: guard registry with runners and acceptance criteria (`guard-the-guards.md`); skip = fail;
  pipefail.
- Detect: G2 seeded-fault test per guard; G1 citation resolution; scope audit (languages, artifacts,
  environments, transitions, fallback paths, empty baselines).
- Probe: pick the 5 guards protecting the highest-severity hazards; seed their faults; count kills.
- Slipped: this mode is the guard slipping; use the ordered guard audit and the 31 anti-patterns in
  `guard-the-guards.md`.
- Example (finance): "all journals approved" passes because the approver defaults to the preparer.

### FM-24 Status and diagnostic fields not computed from content
- Signature: a schema-valid export misses required parts; "reliable: true" while undercounting 3x; a blocked
  item renders green; a blocker names the wrong cause.
- Prevent: status from a content checklist; separate fitness flags per purpose; unknown renders neutral/red.
- Detect: G2 exhaustive status-to-style test; one fixture per diagnostic code; every code emitted; G6
  checklist.
- Probe: for each status field, read the function that sets it and list its inputs; no content invariant
  among them = finding.
- Slipped: the export validator itself was missing from the runtime image (see FM-20 and FM-04).
- Example (finance): a filing passes taxonomy validation with the wrong sign on cash flow.

### FM-25 Lossy representation reused downstream
- Signature: the same point count everywhere; the exported primitive mix differs from the source (arcs in
  the source, none in the export); deviation grows with length.
- Prevent: `purpose` tag on artifacts; compute never reads display; source primitives kept.
- Detect: G1 display-field lint; G2 export round-trip within tolerance; G5 fidelity diff vs source
  primitive.
- Probe: round-trip one export per tenant and diff against the internal model AND against the source
  quantity the deliverable defines (for example the finished top line); agreement with the internal model
  alone is circular when the wrong internal artifact is exported.
- Slipped: no guard existed.
- Example (finance): presentation-rounded amounts reused as tax inputs.

### FM-26 Development-instance overfitting
- Signature: high yield on the pilot tenant, near zero elsewhere; tenant literals in code, data, regexes or
  prompts; a new tenant rejected by a closed list; a classifier that never abstains.
- Prevent: per-tenant configuration, not code; classifiers abstain on unseen vocabulary; two rows claiming
  one role = stop; cold-start path exercised in CI.
- Detect: G1 tenant-literal guard (identity baseline, only shrinks); G2 synthetic tenant end to end and MR-8
  renaming; G5 yield table; G8 error grouping and a cold run of a held-out real tenant.
- Probe: yield table per extractor x tenant from the pinned version; the lowest cells are candidates.
- Slipped: the generality guard scanned constants in one language and froze existing debt as a count.
- Example (clinical): abstraction rules tuned on one hospital's note templates.

### FM-27 Domain definition and convention gaps
- Signature: totals match the reference only under another boundary choice; the expert says "this is a
  minimum, not a constant"; a canon change yields large deltas noticed only in review.
- Prevent: definitional slots on every quantity card; one executable definition with golden values;
  assumptions register to the expert in week one.
- Detect: G1 card lint; G6 >10% version delta needs a reason; G8 sensitivity table over definitional
  choices.
- Probe: list the definitional choices behind each delivered quantity; any unwritten choice is a finding.
- Slipped: no structural guard existed.
- Example (legal): "days" not recorded as calendar or business days per clause.

### FM-28 Divergent duplicate implementations
- Signature: a fix changes nothing visible; two screens disagree; verifiers churn with every producer
  change; one page mixes versions.
- Prevent: canonical implementation registry; code generation for multi-runtime; verifiers call the
  producer's rule; reads pin (entity, version).
- Detect: G1 emission-point census and second-caller lint; G2 differential test; G7 render-time version
  homogeneity.
- Probe: grep each core quantity across runtimes; run the implementations found on 3 shared records and
  diff.
- Slipped: no parity tests; a later batch of deletions removed one side without checking readers.
- Example (finance): tax engine and invoicing compute VAT separately and round differently.

### FM-29 Source defects and contradictions accepted as truth
- Signature: a clean global average hides one bad segment; offsets equal structural constants; codes absent
  from the canon; the client says "your premise is wrong".
- Prevent: cross-field edits per record; document identity checked against filing location; reference
  datasets carry edition and date; supersession graph for revisions and amendments.
- Detect: G3 cross-field identities; G4 parse plausibility (extent, scale, coordinate system, units,
  geometry validity); G5 windowed residuals and multimodality test; G8 citator currency check.
- Probe: compute windowed residuals for each cross-check; inspect the worst window by eye in the source.
- Slipped: a global average check over the whole extent averaged a local error away.
- Example (finance): a scanned statement subtotal does not equal the sum of its lines.

### FM-30 Over-blocking fail-closed cascades
- Signature: one block code covers over 90% of entities; low coverage called "honest"; one answer would
  unlock hundreds of slots; weeks waiting for experts.
- Prevent: flagged provisional values; compare alternatives on needed outputs; independent parts not blocked
  by one unknown; questions ranked by unlock fan-out.
- Detect: G5 block-code concentration alarm; G6 coverage reported with provisional share; abstain only where
  calibration says so (conformal back-off).
- Probe: histogram block codes per tenant; for the top code, compute the alternatives on the needed outputs.
- Slipped: the gates worked exactly as designed; the design is the defect.
- Example (finance): consolidation waits on one disputed accrual.

### FM-31 Unbounded reader runtime
- Signature: a page never finishes loading or flickers; requests or function invocations per page jump
  after a reader deploy; cost rises while no data changed.
- Prevent: effects and fetches keyed on stable pinned ids (version, key); one request per pinned key.
- Detect: G1 reader effect lint; G2 component test asserting one fetch per (version, key); G7 runtime
  budget on the live surface after each deploy.
- Probe: open the shown version on the live surface and count identical requests per key over 60 s.
- Slipped: verification ran against a local cache that answered instantly, so the loop cost nothing there.
- Example (legal): a clause viewer refetches the register on every render and exhausts the API quota.

---

## Guideword and UCA map (read only after path A is sealed)
Turns sealed path-A rows into FM and ST ids; also the starting set for path B probes per guideword.

| Guideword | Typical modes |
|---|---|
| NO | FM-04, FM-05, FM-08, FM-15, FM-16, FM-24, FM-30 |
| MORE | FM-14, FM-11, FM-03, FM-10, FM-01, FM-31 |
| LESS | FM-09, FM-07, FM-13, FM-25, FM-01, FM-08 |
| AS WELL AS | FM-10, FM-19, FM-29, FM-06, FM-17 |
| PART OF | FM-07, FM-08, FM-12, FM-13, FM-20, FM-27 |
| OTHER THAN | FM-01, FM-02, FM-03, FM-05, FM-06, FM-21, FM-24 |
| REVERSE | FM-11, FM-24, FM-05 |
| EARLY | FM-02, FM-16, FM-18, FM-20 |
| LATE | FM-01, FM-02, FM-16, FM-20; ST-01, ST-04 |
| STALE | FM-17, FM-18, FM-22, FM-28; ST-03 |
| WRONG FRAME | FM-11, FM-03, FM-25, FM-27, FM-29 (encoding and escapes: FM-29, FM-08) |
| WRONG SCOPE | FM-12, FM-13, FM-19, FM-26, FM-28 |
| belief from a proxy (OTHER THAN on SIG) | FM-05, FM-24, FM-04, FM-17 |

| Control action | Not provided | Provided, harmful | Wrong timing / order | Wrong duration |
|---|---|---|---|---|
| accept value | FM-30 | FM-21, FM-03, FM-10 | FM-29 | FM-26 |
| default / impute | FM-30 | FM-06 | FM-08 | FM-06, FM-16 |
| skip, cap, filter | - | FM-09, FM-04 | FM-14 | FM-09 |
| retry | FM-20 | ST-02, FM-21 | FM-20 | ST-15 |
| reuse cache | - | FM-17 | FM-17 | FM-17 |
| join, merge, dedupe | FM-14 | FM-03 | FM-14 | FM-19 |
| write shared artifact | FM-19 | FM-19 | FM-18 | FM-19 |
| claim / lease job | FM-09 | FM-14, FM-18 | FM-20, FM-09 | ST-14 |
| promote / publish | FM-18 | FM-18, FM-24 | FM-02 | FM-18 |
| apply human answer | FM-16 | FM-16, FM-12 | FM-16 | FM-29 |
| ask expert, block | FM-08 | FM-16 | ST-05 | FM-30, ST-05 |
| declare done, pass gate | - | FM-05, FM-24 | FM-20 | FM-23 |
| change schema or vocabulary | FM-02 | FM-02 | FM-02 | FM-15 |
| merge code change | - | ST-04 | FM-02 | ST-04 |
| delete / loosen guard | - | ST-09, FM-23 | ST-09 | FM-23 |
