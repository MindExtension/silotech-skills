# Hunting, verification, stop rule and multi-agent fan-out (AUDIT)

## 1. Two independent hunting paths
Independence is what makes the residual estimate meaningful. Path B must not read path A's candidates
(and vice versa) until both are complete, and path A must not be driven by the failure-mode catalog that
path B walks. Finish and seal path A's list first: write it to `findings.jsonl` with `found_by: "A"`, run
`ledger_check.py <dir> --digest` and log round 1 with `"sealed": true` and the printed `sealed_digest`
(id and title of each path-A row stay unchanged from then on). Then work path B from its own inputs (in
a solo run, in a fresh context: section 4). Mark overlaps only at merge: the path-A row stays canonical
with `found_by: "AB"` and the path-B row gets `duplicate_of: <path-A id>`.

Path A, systematic and catalog-blind (from the chain map and contracts only):
1. HAZOP every seam over the full guideword x parameter grid, every cell swept or pruned with a reason
   (`hazard-sweep.md` section 1).
2. STPA every control action, with the belief check (`hazard-sweep.md` section 2).
3. Contract audit against `contracts-by-construction.md`: every missing envelope field, missing
   denominator, open vocabulary, mutable registered version, unsharded shared artifact is a candidate.
Do not open `failure-modes.md`, `symptom-index.md` or `selection.md` during path A; map FM ids after
sealing. The FM x stage coverage matrix is not a path A tool: it belongs to the completeness critic
(section 3, criterion 4).

Path B, signature and evidence driven (from the instance and its history):
1. Order the modes: map the chain facts recorded in A2 to the feature questions and chain shapes in
   `selection.md`, which give the starting set and order.
2. Cheapest first: the distribution smell scan over all outputs (`gate-ladder.md` G5) and the grep pack
   GP-1..GP-12 (`gate-ladder.md` G1). Hits are candidates, not findings.
3. For every FM run its "Probe" from `failure-modes.md` on the pinned instance (read-only).
4. History pass (CAST-lite): take the incident log, failed-run log (`runs.jsonl` from AUDIT A1) and fix
   history; for each item record stage introduced, stage detected, the controller whose belief was
   wrong, the missing feedback; cluster by (wrong belief, missing feedback), not by symptom. Hot spots:
   files with 3 or more fixes within 48 hours, error fingerprints that recur, tenants with the lowest
   yield. Every catchable run fingerprint becomes a proposed P-item; a fingerprint repeated with no change
   in between is an ST-02 finding.
5. Probes on a scratch copy (truth rule 9 in SKILL.md: confirm sinks, caches and model endpoints are
   scratch and paid calls are off or capped): metamorphic relations MR-1..MR-12 and seeded faults on 1-3
   recorded records per tenant; position-aware canaries in long inputs; two-direction source verification
   on a stratified sample; follow one delivered number backwards from output to source span. Data probes
   run over the planted copy.

## 2. Candidate verification (before anything is called a finding)
For each candidate, in this order:
1. Restate the claim as a falsifiable sentence: on instance X, invariant Y fails at location Z with value
   V (expected W). Reproduce on the pinned instance with a command or record pointer anyone can rerun.
   No reproduction: verdict `not_checked` with the reason (no access, cost, missing fixture), never
   `confirmed`.
2. Check the intentional-state registry (documented deliberate behaviours, accepted risks, known
   fail-closed paths). Intentional: `refuted` with the registry entry cited.
3. Refute. An independent verifier (rules below) runs the refutation checklist; any item that succeeds
   ends as `refuted` with its reason. Most refuted findings in the source history were intentional
   documented states, unreachable paths, claims disproved by actual data, or correct code citations with
   wrong impact.
   - R1 Instance: is this the instance users see? Code revision vs the intended one? Cache vs live? Were
     relayed numbers re-run?
   - R2 Intentional state: a documented decision, a deliberate compatibility shim, a logged fail-closed
     path? (The finding may become "undocumented" or "unlogged", not "wrong".)
   - R3 Reachability: does any real input reach this path, given the graph order and upstream gates?
   - R4 Data reality: does the failing state occur in actual artifacts, or only in theory? Count it.
   - R5 Probe validity: does the probe read the right field, version, frame and unit? Does it pass on a
     known-good case?
   - R6 Source defect: is the source itself wrong or contradictory? Then the finding stands with root
     Collection (no cross-check at ingest) and the source issue is reported separately.
   - R7 Reference validity: if the finding rests on a reference, is the reference a checked document,
     matched to the same feature, current, and covering this item?
   Verifier independence rules:
   - The verifier is not the finder's context: a fresh session, a different prompt, ideally a different
     model family or a human. Self-verification by the same model in the same context does not count:
     record `verification: {by, saw_candidate}` on the finding (section 4).
   - Blind re-derivation first: give the verifier the source, the location and the question, not the
     candidate answer or the finder's reasoning; only then the full claim for R1-R7 (section 4 rule 1).
   - Use a different evidence channel when possible (a table vs an annotation vs geometry), not the same
     text read twice.
   - An automated judge is used only with measured TPR and TNR on human labels (`guard-the-guards.md`
     section 6); report corrected rates, never raw judge pass rates.
4. Verdict: `confirmed` (reproduced, not intentional, survived refutation), `plausible` (mechanism shown,
   not reproduced on this instance; state what would confirm it), `refuted` (with reason, kept in the
   ledger; intentional states go to the registry given to future finders), `not_checked`.
5. Classify cause root and escape root (`incident-to-class.md` I3); map to FM and ST ids; write the class
   signature and predicate.
6. Severity: S 1-10 from delivered impact and its label (`hazard-sweep.md` section 3); for aggregates
   report signed and absolute effect. Blast radius = siblings matched by the class predicate and
   aggregates affected.

Dedupe in two stages, marking duplicates with `duplicate_of: <id>` instead of deleting rows (deleting
would break the seal digest). Before the refutation pass, by candidate signature (stage or seam,
parameter, guideword, location), so a verifier never sees one claim twice. After step 5, by
`(fm and st ids, cause_root, class_predicate)`: contiguous locations of one predicate are one finding
with a sibling count, not N findings (ST-12).

## 3. Stop rule and residual estimate
After each round, compute on confirmed findings of medium or higher severity (S >= 4), deduped, excluding
findings on planted defects:
- `n1` found by path A, `n2` found by path B, `m` found by both. A finding counts toward `m` only when
  round 1 shows both paths sealed (`rounds.jsonl`); unsealed `AB` rows count for path A only.
- Chapman estimate of the total: `N = (n1 + 1) * (n2 + 1) / (m + 1) - 1`.
- Found so far: `F = n1 + n2 - m`. Residual: `R = N - F`.
- Worked example: n1 = 14, n2 = 11, m = 8 gives N = 15 * 12 / 9 - 1 = 19, F = 17, R = 2.
- The estimate is a LOWER bound: paths that share the spec, model family or person overlap more, which
  shrinks R (historically about a quarter too low). Say so in the report. Hazard cells that stayed
  NOT-CHECKED are listed separately, never folded into the residual. In a solo or description-only audit
  where path B is catalog matching by the same agent on the same text, count A and B as one path: do not
  use Chapman; certify with planted defects (low-count branch) or label the report DESIGN REVIEW.

Branch choice:
- Standard branch when `m >= 3` and `F >= 6`.
- Low-count branch when `m < 3` or `F < 6` (few defects, or too little overlap for Chapman to mean
  anything; with m = 0 the estimate is undefined), and always in a solo audit (round 1 `path: "both"`).
  Capture-recapture cannot certify such a hunt, so planted defects certify it instead.

Value-weighted residual (the error in each published total). Chapman counts bugs; readers rely on
totals. For every published aggregate with S >= 7, fix before the hunt the tolerable error `TE` and the
expectation record (`gate-ladder.md` G4). Then:
- Sample source units with probability proportional to their contribution to the total (money or
  quantity unit sampling), stratified by tenant and rare state. Add an omission stratum sampled from
  sources or regions where nothing was extracted: value-weighted sampling never selects what is missing.
- Recheck each sampled unit against the source blind, by a route independent of the producer.
- Project per stratum: taint = error / recorded value; projected error = mean taint x stratum value; add
  the omission stratum's projected missing value. With zero errors the 95% upper bound is 3.0 x the
  sampling interval (stratum value / n).
- PASS for that total only when the upper bound is below `TE`; otherwise FAIL with the projected error.
Review order for candidates and records: score = suspicion (model disagreement, failed edit rules, no
source span, unusual value) x impact (share of a published total it can move); work from the top down
until the remaining expected impact is below `TE`, plus a small random stratified sample so the score
itself is checked.
Open doubts (defeaters): any recorded reason to doubt a PASS (unverified assumption, untested guard,
unread source) stays open until eliminated with evidence; an open doubt keeps that PASS at `plausible`.

Stop when ALL hold:
1. Both paths completed and sealed for the agreed scope.
2. Standard branch: `R <= max(2, 0.1 * F)`. Low-count branch: at least 3 planted defects in
   `planted.jsonl` and planted recall >= 0.8.
3. K = 2 consecutive extra rounds, each from a fresh angle, produced no new confirmed finding with
   S >= 4 (both branches). Fresh angles: stage by stage; FM cluster (identity, absence, aggregation,
   versioning, model stages, human loop, runtime); tenant by tenant starting with the least tuned;
   control action by control action; a guideword family not yet used as the lead; one delivered number
   traced backwards; hot files from history; a pre-mortem story set.
4. Coverage: the completeness critic builds the FM x stage matrix (for every FM, each stage type where it
   can originate per `selection.md`, which effective guard exists at which gate) and gives every
   FM-01..FM-31 and ST-01..ST-15 a status in `coverage.jsonl` (rules in `templates.md` section 8). For an
   ST id, `finding` means its trigger fired and `guarded` means its "Check" line passed with evidence.
   Empty matrix cells for modes with S >= 7 start a gap round (one more round aimed at those cells)
   before the stop rule is evaluated again.
5. Planted recall >= 0.8 (both branches; planting before round 1 is mandatory, `guard-the-guards.md`
   section 7).
6. No HAZOP cell in scope is left `not_examined`.
7. Every S >= 7 published total has a value-weighted upper bound below its `TE`, or is listed as
   NOT-CHECKED(tolerance) with the reason; no open doubt undercuts a PASS on such a total.

Budget stop: when time or token budget ends first, stop, label the report `INCOMPLETE`, list which stop
criteria failed, and list the NOT-CHECKED items. Never present an incomplete hunt as clean.

Log every round (path, angle, completed, sealed, started_at) in `rounds.jsonl`; a round that is not
logged did not happen. `python3 <skill-dir>/scripts/ledger_check.py <audit-dir> --mode audit
--require-stop` checks the seal and planting digests and computes n1, n2, m, N, R, the branch, planted
recall, the dry-round count and coverage gaps; it exits 3 while the stop rule is unmet and prints "NOT
EVALUATED" while any violation stands. Run `--selftest` first; without its PASS line do not trust the
script's verdict.

What-remains statement (copy into the report):
```
Instance: <code revision> / <version id> / <environment> / <tenants> / <time>
Results: pass <n> | fail <n> | not-checked <n> (reasons: access <n>, approval <n>, cost <n>, other <n>)
Confirmed S>=4 findings: <n>; paths A <n1>, B <n2>, both <m> (sealed: yes|no)
Verification: fresh context | human | same-context, unverified (verdicts capped at plausible)
Stop branch: standard (residual <R>, lower bound) | low-count (planted recall <x> of <k>); dry rounds <d>
Totals: <total>: upper bound <x> vs TE <y> (PASS|FAIL|NOT-CHECKED) for each S>=7 total
Open doubts: <defeaters still open, each capping a PASS at plausible>
Not swept: <seams, grid cells or FM ids>
Unknown: <what this audit cannot say and why>
```

## 4. Solo protocol (the default)
One agent that writes path A, path B and the verdicts is not independent of itself. Solo runs follow three
rules, and the ledger records them.
1. Fresh contexts, two parts. A fresh read-only sub-agent first re-derives the value at the claimed
   location from the instance header, the location and the question only (never the finder's value or
   reasoning; this is `saw_candidate: false`), then runs R1-R7 (section 2 step 3) on the full claim. Path
   B runs in another fresh sub-agent given the instance, the chain map and the catalog, never path A's
   rows. Each finding records `verification: {by: fresh_session | human | same_context, saw_candidate:
   true | false}`. Without a sub-agent or human verifier, verdicts cap at `plausible`, the report says
   "same-context, unverified" and the stop rule cannot be met: say so before starting. `ledger_check.py`
   rejects a confirmed AUDIT finding verified in the same context or without the blind re-derivation.
2. Planted branch always. Round 1 is logged as `path: "both"`; Chapman is printed for information only
   and the stop rule uses the low-count branch. Seeds are applied by a fresh sub-agent or a human who
   alone opens `planted.jsonl`; `ledger_check.py <dir> --plant N` only draws them at random for that
   planter (`planted_by: script`), applied and sealed before round 1. A finder that applies its own seeds
   records round 0 `planted_by: self`; its recall is not blind and cannot certify the stop rule.
3. Seal by digest. Path A's list and the planted list are sealed with the digests from `--digest`; the
   script recomputes both, so an edit after sealing is caught.

## 5. Multi-agent fan-out (only when the user opts in)
With multiple agents:

| Role | Count | Input | Output | Rules |
|---|---|---|---|---|
| Mapper | 1 | repo, live read access | chain map, seams with intents, census, guard registry, intentional-state registry, pinned instance ids, planted defects (sealed) | runs first; everyone else uses its pins |
| Path A finders | 2-4, by angle (seams, control actions, contracts) | chain map, seams, contracts | candidate rows `found_by: A`, hazard rows | never read path B output or the FM catalog |
| Path B finders | 2-4, by FM cluster or by tenant | pinned instance, history, selection | candidate rows `found_by: B` | never read path A output |
| Verifiers | 1 per ~15 candidates | location and question, then the claim (section 4 rule 1) | verdict per candidate | fresh session; different model family where available; must reproduce or refute (R1-R7) |
| Completeness critic | 1 | merged ledger, guard registry, selection tables | FM x stage matrix, `coverage.jsonl`, gap list | checks every FM/ST status, NOT-CHECKED reasons, stop criteria |
| Synthesizer | 1 | all ledgers | deduped ledger, report | adds no findings of its own |

Handoff contract. Each finder receives: the instance header; chain map and seams paths; its angle or mode
slice; read-only access details; its output path; a budget (time and model spend); the intentional-state
registry; the instruction to seed every detector before trusting it. Each finder returns, as files in its
output path: findings rows with `found_by` and verdict `plausible` or `confirmed`; invariant rows for
every check run, with tri-state results and executed counts; proposed guards with their seeds; a
NOT-CHECKED list with reasons. A finder returning "nothing found" must also return its executed counts and
positive controls; otherwise its result is NOT-CHECKED.

Model choice: cheap models are acceptable for finders on G1-G4 style work; verifiers and the
completeness critic use the strongest available model, because cheap-model audits were wrong about one
time in three in the history behind this skill.

All agents are read-only: no writes to code, data stores or external systems; outputs are JSONL rows in
the fixed schemas, written to the audit directory, one isolated scratch directory or worktree per agent,
messages through files with an acknowledgement line. Each row repeats the pinned instance; finders share
one pinned snapshot rather than each hydrating production. Agents that share a model family are
correlated finders: count them as one path for capture-recapture unless their inputs or angles differ.
Cap the fleet before starting (agents x expected tokens) and stop on budget as in section 3.
