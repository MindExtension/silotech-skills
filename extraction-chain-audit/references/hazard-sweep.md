# Systematic hazard sweep (HAZOP + STPA + FMEA + FTA)

The sweep is the systematic path: it starts from the chain map, not from history, so it finds defects
nobody has seen yet. Coverage comes from walking every cell, not from imagination. Output rows go to
`hazards.jsonl` and seam intents to `seams.jsonl` (schemas in `templates.md`). Use it in BUILD step B3
(changed seams), AUDIT path A and DESIGN REVIEW (all seams).

Input: the chain map (stages, seams producer -> consumer, control actions, tenants, guards).
Time box: about 10 minutes per seam in AUDIT, 5 minutes per changed seam in BUILD. Pruning a parameter
the seam does not carry takes one row for all 12 guidewords.

Catalog-blind rule (AUDIT path A): this file carries no failure-mode ids, so path A can read all of it.
Do not open the failure-mode catalog (including its guideword and UCA map), the symptom index or the
selection tables while sweeping. Leave `fm` empty; fill it after path A's list is sealed. Otherwise path
A turns into a copy of path B and the residual estimate shrinks for no reason.

## 1. HAZOP over data seams

### 1.1 Design intent first
Before sweeping a seam, write its intent in `seams.jsonl`: what crosses, the contract (schema and
version), expected cardinality, units, frame, scope, version rules. A seam without a stated intent is
itself a Structure finding; a seam without a contract is swept from a sample record and also gets that
finding. For export and delivery seams, take the intent from the deliverable contract or client
specification (which quantity, surface or layer the client receives), not from the code; "map from
code" (`delivery-stalls.md`) applies to wiring, not to intent. A disagreement between code and
deliverable is a finding.

### 1.2 Parameters a seam can carry
| Code | Parameter | What to look at |
|---|---|---|
| PRES | presence and cardinality | are the expected items there, how many, one or many carriers |
| VAL | value | the number, text, geometry or date itself |
| UNIT | unit and scale | units, scale factors, currency, precision, rounding |
| ID | identity | keys, joins, aliases, entity binding, identifier format |
| VOC | vocabulary | categorical codes, statuses, enums, schema and version names |
| SCOPE | scope and coverage | extent, denominator, partition, window, tenant, variant |
| FRAME | frame and convention | reference origin, sign, direction, ordering, coordinate order, calendar, notation, text encoding and codepage, escape and format codes (DXF/MTEXT `\U+XXXX`, `\M+`, `%%c`; HTML entities; `\uXXXX`), Unicode normalization (NFC/NFD) |
| PROV | provenance and status | source id, revision, locator, span; observed, derived, imputed, defaulted, human |
| VER | version and time | code revision, input vintage, schema version, decision time, reference edition |
| SIG | outcome signal | exit status, done flag, verdict, status field, visible pointer, error record, executed count |

### 1.3 Applicability matrix
`X` = always sweep when the seam carries the parameter. `o` = sweep when the seam has the feature (a
join, an aggregate, a model call, a human step, a cache); otherwise prune as `feature_absent`. Blank =
prune as `matrix_blank` unless the seam is unusual; write why it is not unusual.

| Guideword | PRES | VAL | UNIT | ID | VOC | SCOPE | FRAME | PROV | VER | SIG |
|---|---|---|---|---|---|---|---|---|---|---|
| NO | X | X | o | X | o | o | o | X | o | X |
| MORE | X | X | o | X | o | X |  | o | o | o |
| LESS | X | X | o | o | o | X | o | X |  | o |
| AS WELL AS | X | o |  | X | o | X |  | X | X |  |
| PART OF | X | X | X | o |  | X | o | X |  | o |
| OTHER THAN |  | X | X | X | X | o | o | X | o | X |
| REVERSE |  | o |  | o | o |  | X |  |  | o |
| EARLY | X |  |  |  |  | o |  |  | X | X |
| LATE | o |  |  |  |  |  |  |  | X | X |
| STALE |  | o |  |  |  | o |  | o | X | X |
| WRONG FRAME |  | o | X | o |  | o | X |  |  |  |
| WRONG SCOPE |  | X |  | o |  | X |  | o | o | o |

### 1.4 Guidewords
Each: meaning for data flows, what to look for, the seeded fault that tests a safeguard, and the
cheapest probe with its gate (`gate-ladder.md`). The failure modes each guideword usually maps to are in
`failure-modes.md` (guideword and UCA map), read only after sealing in AUDIT.

**NO**: the item, carrier, value, citation, version stamp or signal is absent and the absence is not
represented. Look for carriers never read (nested containers, second file of a role, image-only pages,
appendices), readers that default to empty on failure, no-op nodes reported as executed, values with no
citation, a missing check result counted as pass, a field with no consumer.
- Seed: delete one input file, page, nested container or category; empty an upstream artifact; remove a write flag.
- Probe: G1 lint for default-empty reads; G4 census per carrier vs output counts; G3 output hash changed
  or explicit unchanged record.

**MORE**: duplicates, multiplicity, inflated values, extra codes, overlapping coverage. Look for
overlapping chunks or views, a fact read from both a document and its restatement, one-to-many joins,
alternatives summed, closed intervals sharing a boundary, retries publishing twice, unit scale x1000,
several witnesses that copy one author, an entity mapped to more than one reporting group.
- Seed: duplicate 5% of records; duplicate a whole document; scale one value by 1000.
- Probe: G3 natural-key uniqueness; G2 MR-3 duplication relation; G5 disjointness of grouping keys.

**LESS**: part of the input or of a value is lost. Look for character slices, first-N limits, call
budgets, context windows, default row limits, size-based skips, performance filters, fixed-count
resampling, rounding, flags lost at projection, vocabularies inferred from a sample, fewer checks executed,
header detection that consumes the first data row or drops a trailing row when file templates vary
(extra title lines, merged headers, totals rows).
- Seed: append items beyond each cap; put the key fact at the end of a long document; drop 10% of records;
  add or remove one header line in one tenant's file; append a totals row.
- Probe: grep pack GP-2 (caps); G5 `n_available` vs `n_used` on every cap; G5 flag-count conservation.

**AS WELL AS**: something extra is mixed in from another evidence class, tenant, revision or reference.
Look for legends, title blocks, examples and sample tables read as content; existing items counted as
proposed; superseded revisions; another tenant's objects; the answer key in a prompt, fallback or
golden value.
- Seed: add an unrelated document; inject a superseded revision; inject one row from another tenant; drop
  the answer-key file into the input folder.
- Probe: G1 taint rule (no edge from a reference node to compute); G2 oracle removal, outputs
  bit-identical; G6 every artifact's tenant equals the version's tenant.

**PART OF**: only part of the intended thing crosses: one carrier of many, a value without unit, scope or
provenance, a composite missing a component, part of the declared range, a missing definitional slot, a
partial write acknowledged as complete. Look for `first()` over a multi-file role, top-level-only
traversal, citations without locator, jobs marked done before every key is saved.
- Seed: split a role across two files; move a fact into a nested container; strip units; kill the writer
  after half the keys.
- Probe: G4 carrier census per role (P4); G6 required-component checklist; G3 unsaved keys = 0 and
  re-read before done.

**OTHER THAN**: the wrong thing arrives: wrong entity, unit, version, vocabulary value or evidence class;
a fabricated or neighbour value; a status set from a proxy; an error turned into a domain state. Look
for substring and nearest-label matching, unknown enum values coerced, "blocked" emitted by a broad
exception handler, "exported" set from schema validity, constants filled in for missing values.
- Seed: relabel a category; insert an unseen code; swap two fields; replace a value with a plausible one
  from another document; inject a programming error into a producer.
- Probe: G1 enum closure; G1 broad-handler lint; G4 consumers accept rare-state records (P6); G3
  assumption counter > 0 whenever a fallback fired.

**REVERSE**: direction, sign, order or relation is inverted: debit and credit, inflow and outflow, left and
right, start and end, ascending vs descending order, parent and child, "A amends B" read as "B amends A",
inverted ordinal scales, inverted pass and fail.
- Seed: mirror the input; reverse the reference direction; swap amendment order; flip a comparison.
- Probe: G2 MR-6 mirror and reversal relations; G3 ordering invariants.

**EARLY**: an action happens before its preconditions: aggregate before all partitions load, publish
before readers support the version, consume before the producer finishes or a human decision exists,
done before the durable write, promotion before checks finish.
- Seed: run the aggregate with one partition missing; publish a schema version the reader does not list;
  acknowledge before the write.
- Probe: G1 reader support list vs producer versions; G2 promotion decision table; G3 re-read after write.

**LATE**: information arrives after it could matter: validation only at the final sink, errors after hours
of compute, human answers after the run or export, timeouts only on the largest tenant.
- Seed: inject a schema violation in an early node and time how long the chain runs before failing.
- Probe: move the check to G1-G4; per-node timing; largest tenant in preflight (P8).

**STALE**: an old vintage is used as current: cached artifact, previous version, old code revision,
superseded source, a verdict computed before a guard was tightened. Look for per-tenant runs that skip
shared nodes and carry old outputs, freshness from file timestamps, "latest" pointers, verification on a
stale cache or old deployment, baselines without a settings hash.
- Seed: serve the previous version's artifact to one node; run an older code revision; reuse an old
  verdict after tightening the guard.
- Probe: G3 every artifact stamped with run id, code revision and input digests; G6 lineage homogeneity;
  G4 running revision equals the expected commit (P1).

**WRONG FRAME**: the value is right in some frame but read in another: units, origin or datum, axis, sign
convention, coordinate order, identifier notation, calendar vs business days. Look for several parsers
and formatters for one identifier, offsets without a side, values normalized against a weak or competing
reference, resampling whose resolution changes with size, text decoded with the wrong codepage or with
escape sequences left literal ("Stra\U+00DFe" instead of the national character), mojibake pairs, the
replacement character U+FFFD.
- Seed: change input units; swap coordinate order; write identifiers in an alternative notation; re-save
  a fixture in another codepage; write national characters as source-format escapes.
- Probe: G2 MR-4 unit scaling; G2 identifier round-trip on a golden corpus; G5 shared landmarks agree
  across artifacts; G2 decode round-trip on a golden corpus in the source language and script; G5 smell
  scan and grep pack GP-11 for undecoded escapes.

**WRONG SCOPE**: a value computed over one scope is read at another: a window value read as a point
value, a whole-extent maximum used locally, a portfolio verdict applied to each item, one tenant's value
reused for another, a page mixing versions.
- Seed: replace a point value with its window aggregate; give two locations the same value; mix two
  versions on one read.
- Probe: G0 scope field required on every derived value; G5 identical values at distinct keys; G7
  render-time version homogeneity.

### 1.5 Procedure per seam (exhaustive, auditable)
1. Write the intent (1.1). List the parameters the seam carries (`carries`, never empty) and, for VAL
   and UNIT, every numeric field it carries with its unit as written in the source (dose, amount,
   length, energy, currency). A numeric field without a typed unit, or with more than one unit spelling
   across tenants or templates, is a hazard row on UNIT x OTHER THAN, even in an audit of a description.
2. Walk all 120 cells (12 guidewords x 10 parameters). Every cell ends as exactly one of: a hazard row,
   or a pruned row. One row may cover several cells (lists of parameters or guidewords, `"*"` for all)
   when cause, consequence and reason are the same; `no_credible_cause` and `prevented_by_construction`
   take exactly one guideword per row, because each guideword is its own question. No cell is skipped
   silently.
3. Pruned rows (`"status": "pruned"`) carry one `prune_reason` and a non-empty `prune_detail`:
   - `not_carried`: only parameters absent from the seam's `carries` (name it).
   - `feature_absent`: only `o` cells; name the missing feature (no join, no aggregate, no model call).
   - `matrix_blank`: only blank cells; say why the seam is not unusual.
   - `prevented_by_construction`: name the mechanism, the effective guard or test that proves it
     (`guard`) and what you read (`examined`).
   - `represented_by`: a seam of the same `type` with shared code whose own grid is fully covered was
     swept; name it in `represented_by` (`SM-07`, or `SM-07@<prior ledger dir>` for the last full sweep
     of the same seam). The derived invariants still run on every instance of the type at G5.
   - `no_credible_cause`: a swept cell where no cause was found; list what you examined in `examined`
     (code paths, contract fields, record ids) and say in `prune_detail` why no cause exists.
   - `not_examined`: the cell was listed but not examined (no code or records, for example in a DESIGN
     REVIEW); it counts as NOT-CHECKED in the report and coverage, never as swept, and keeps an AUDIT
     from stopping.
4. Hazard rows: name the cause concretely ("chunk overlap of 200 tokens re-extracts boundary clauses"),
   the consequence (which delivered aggregate or decision moves, by roughly how much), S, O, D (section
   3), safeguards (only EFFECTIVE guards count, `guard-the-guards.md`; anything else is listed as none),
   and the proposed control: prevention (G0) first, otherwise the earliest gate.
5. If no catalog mode fits a credible deviation (checked after sealing), record `FM-NEW-<n>` with a
   signature and its guideword x parameter cell. New modes are the most valuable output of an audit.

`scripts/ledger_check.py` rebuilds the grid for every seam in scope (all seams in AUDIT and DESIGN
REVIEW, seams with `"changed": true` in BUILD) and reports cells neither swept nor pruned, prune reasons
that do not fit the cell or the seam's `carries`, missing `examined` lists and guards, representatives
that do not exist or are not fully swept, and 0 seams in scope.

## 2. STPA over control actions
Controllers: orchestrator, each extractor and matcher, aggregator, validators and gates, cache,
publisher, human reviewer or expert, code-merge process, and the agent itself. For each control action
write the four unsafe-control-action types: not provided; provided and causes harm; provided too early,
too late or out of order; stopped too soon or applied too long.

| Control action | Not provided | Provided, harmful | Wrong timing / order | Wrong duration |
|---|---|---|---|---|
| accept value | correct value dropped as unresolved | empty or truncated model output accepted; value from the wrong entity or evidence class | accepted before the cross-field check ran | acceptance threshold kept after the source type changed |
| default / impute | missing value blocks every dependent | default emitted as observed | default applied before the lookup of the real source finished | fallback left on after the source or answer arrived |
| skip, cap, filter | n/a | skip reported as success or zero | filter before dedupe or after aggregation | cap set for a pilot applied to all |
| retry | transient error kills hours of work | deterministic error retried; retry-until-pass masks instability | retry after a partial write | retries continue after the budget is exhausted |
| reuse cache | n/a | cache reused after inputs or rules changed | cache read before the producer finished writing | carried across versions or code revisions |
| join, merge, dedupe | merge not done, duplicates summed | wrong-key merge | dedupe after summing | merge across tenants |
| write shared artifact | expected update missing for one tenant | partial writer replaces the whole artifact | two runs write concurrently | shrink permission left open |
| claim / lease job | job never claimed and never reported | job claimed twice or by the wrong worker class | claimed before its input is durable; enqueued after the pass snapshot | lease never expires after a worker crash |
| promote / publish | correct smaller version never shown | partial or failed version made visible | published before readers support the version | pointer kept after the predicate was tightened |
| apply human answer | answer recorded but never applied | answer applied to the wrong scope | applied after the export was sent | superseded answer still applied |
| ask expert, block | question the source already answers | duplicate or already answered question | asked before the evidence was viewed | blocks everything for one unknown |
| declare done, pass gate | n/a | done from exit code, schema validity or count | done before the durable write | verdict reused after tightening |
| change schema or vocabulary | consumer not updated | registered version edited in place | producer changes before readers | old readers kept on removed producers |
| merge code change | n/a | merged without a production-shaped check | merged before the dependent schema migration | verification deferred indefinitely |
| delete / loosen guard | n/a | guard removed before its replacement | removed during a milestone freeze | warning-only guard kept forever |

**Belief check.** For each controller, list the process-model variables it acts on: input complete,
input fresh, same tenant, zero means measured zero, the store read is the one the current producer
writes, schema supported by all readers, human approved, write durable, check executed, witnesses
independent, this is the live instance. For each, write how the
controller learns the value. If it reads the actual state (key set, content hash, re-read object,
approval record, executed count), note the read. If it infers the value from a proxy (exit code 0, file
exists, artifact or row count, timestamp, schema validity, "latest", absence of exceptions), every such
proxy belief is a hazard cell: guideword OTHER THAN on SIG at that controller's seam, with the real-state
read as the proposed control.

## 3. Ranking with an evidenced detection axis (FMEA, action priority)
- Severity S: the one scale, its labels and its floor rule live in `templates.md` section 0. Rows carry
  both `S` and the label `severity`; `ledger_check.py` rejects a label that does not match S.
- Occurrence O: from history (incidents, failed runs, fix counts) or 5 if unknown.
- Detection D, MEASURED, not believed: 1-3 an effective guard at G0-G3 killed the seeded fault for this
  row; 4-6 an effective guard at G4-G6; 7-8 only human review or G8 sampling, named in
  `detection_evidence`; 9-10 no guard, or the guard never killed a seeded fault, or it is warn-only.
  `ledger_check.py` rejects a D that the listed safeguards and evidence do not support.
- Priority (no RPN multiplication): S >= 7 and D >= 7 is `must_fix` now; S >= 7 otherwise is
  `before_release`; the rest is `backlog` ranked by O. A hazard whose consequence is a failed expensive
  run is never backlog (the floor rule makes it S >= 7); its control sits at G1-G4. After every escaped
  defect raise O or D for its row: an escape proves D was overrated.

## 4. Fault tree for the top outputs
Required in AUDIT (rows with `source: fta`). For the 3-5 most consequential delivered outputs, draw the
top event "delivered value wrong beyond tolerance AND no alarm raised" as AND(error introduced, every
detector missed, human review missed). Expand "detector missed" as OR(not run, ran on stale or cached
input, ran on empty input and passed, tolerance absorbs the error, compared against data derived from the
same faulty extraction, warn-only). Every order-1 cut set (one basic event that defeats all detectors,
such as "all validators read the same cache") is `must_fix`. Common-cause list to check across detectors:
same parser, same unit table, same model family or prompt template, same reference dataset, same author
of extractor and check.

## 5. Defence-in-depth matrix
Optional; use it when several layers claim the same error class. Rows: error classes (one per guideword,
or per FM after sealing). Columns: layers (input contract, write-time validation, stage audits,
cross-stage reconciliation, independent derivation, model verification, human review, client acceptance).
Mark `sees` / `blind` from seeded-fault results, not belief. Merge layers that share inputs, code, model
or person before counting. Any row with at most one effective layer is a gap and becomes a hazard row.

## 6. Pre-mortem prompts (fast, for BUILD and new domains)
Required in BUILD for a new domain or tenant type (rows with `source: premortem`). Write answers
individually before discussing. "Three months after release a client found: (a) a total 25% too low; (b)
a cited clause or value that does not exist in the source; (c) a value taken from a superseded revision;
(d) a category silently dropped for one tenant; (e) a rule applied to a new source type where it does not
hold; (f) a green check that never ran. Write how it happened." Each story becomes a hazard row, a seeded
fault and a run-time monitor.

## 7. Defeaters for every PASS you rely on (assurance-case discipline)
Required before any release claim (BUILD B8, the AUDIT report; rows with `source: defeater`). For each
piece of evidence behind a release claim ask: rebutting (is there a known record where it is wrong?),
undermining (was it produced on the current version, live data, the full set; could it pass on empty or
cached input?), undercutting (does passing actually imply the claim: citation exists does not imply
citation supports; totals match does not imply items correct; a reference reused as input makes the
comparison circular). Unresolved defeaters are findings or listed residual doubts in the report.
