# Delivery stalls (ST-01 .. ST-15): rules that keep the work moving

Product defects are half the cost. The other half is how the team and its agents find and ship fixes.
These 15 stall modes came from the same history (72 stall instances). Each entry: how you notice it
(with a measurable trigger), the rule, and the check that proves you followed it. Apply the rules in
every mode; SKILL.md keeps only the run-gating rules (ST-01, ST-02, ST-03) inline. When a trigger fires,
record an ST finding in `findings.jsonl` with cause root Process or Operations, the ST id in `st` (`fm`
may stay empty) and the trigger value as evidence.

## Run economics (AUDIT A1, BUILD before an expensive run, whenever run history exists)
In the source history 47 of 56 expensive runs failed in one week (f = 0.84), and 72% of the failed
compute was catchable by a preflight of one minute or less (c = 0.72); this is the one home of those
numbers. Measure your own before arguing about them.
1. List the expensive runs in the window (full runs, paid model batches, jobs over ~10 minutes) with
   status, duration or cost, code revision and first error. Write one `runs.jsonl` row per run
   (`templates.md` section 10).
2. Fingerprint each failure: `sha1(node | error_class | field_path | normalized_message)`. Collapse
   identical fingerprints, keep the run count and compute per fingerprint. Also key each failure by its
   class `(first_error.node, first_error.error_class)`: three or more failed runs sharing a class is ST-06
   and opens INCIDENT on the class (`incident-to-class.md` I9) even when every value-level fingerprint
   differs.
3. For each fingerprint decide the lowest gate that would have caught it before launch: `G1` static,
   `G2` CI fixtures, `G3` write-time validation in a smoke run, `G4` preflight P-item, or `runtime_only`
   (only real scale or real time could show it: a timeout on the largest tenant, a provider outage).
   Name the check that would have fired (`catching_check`).
4. Report three numbers with the instance and window: failed runs / all runs, failed compute / all
   compute, and the share of failed compute that was catchable at G1-G4.
5. Every catchable fingerprint becomes a proposed preflight item `P<n>+<fingerprint>` (`gate-ladder.md`
   G4) or a G1-G3 check, registered as a proposed guard with the original failing input as its seeded
   fault. A fingerprint seen twice with no change touching its node, inputs or config in between is an
   ST-02 finding.
`ledger_check.py` validates the rows (fingerprint, first-error class, catchable, catching check, P-item,
ST-02 findings for repeats, ST-06 findings for a class failing in three or more runs) and prints the three
numbers, or NOT-CHECKED for the compute shares when a run has no `minutes`.

### ST-01 Serial blocker discovery on expensive runs
- Notice: the full run is the first real test; each run reveals one new blocker. Trigger: two expensive
  runs fail in a row, or a change's first test is a full run, or the catchable share of failed compute
  (run economics) is above 20%.
- Rule: no run over ~10 minutes or paid batch without a G4 preflight PASS (the PREFLIGHT mode); keep-going
  mode on smoke records; pilot one tenant before fanning out to the rest. The battery holds P1-P10 plus one
  item per catchable failure fingerprint from the run history.
- Check: the run record cites a preflight report id with every applicable P-item PASS on the same code
  revision (`ledger_check.py <dir> --mode preflight`).

### ST-02 Rerun without diagnosis
- Notice: deterministic errors are retried; stored errors are truncated to the last line or a help URL.
  Trigger: the same fingerprint in two runs with no change in between; a retry on a deterministic class;
  a stored error without node, field or value.
- Rule: every failure is stored as a structured error record; a rerun is allowed only if the fingerprint
  is `retryable` or a change since the last failure touches the failing node, its inputs or its config.
  A change that only admits the failing value (one more enum member, one more allowlisted key) is a spot
  fix and does not count as a change for this rule. Queued or scheduled runs of the same code after a
  deterministic failure are held, meaning paused or cancelled and not left to be claimed, until the change
  lands; recommend the hold at once; executing it needs the same permission as launching the runs
  (SKILL.md truth rule 9).

```json
{"node": "normalize_terms", "error_class": "schema_enum", "retryable": false,
 "field_path": "clauses[].risk_class", "value": "hybrid", "version_id": "v41", "code_rev": "a1b2c3d",
 "attempt": 1, "fingerprint": "sha1(node|error_class|field_path|normalized_message)",
 "full_trace_ref": "logs/r-0192/normalize_terms.err"}
```
  Retryable classes: network 5xx, rate limit, timeout with no partial write. Everything else is
  deterministic: schema, enum, missing file, type error, assertion, permission.
- Check: no two failed runs share a fingerprint without an intervening change listed in the run record.

### ST-03 Verification on the wrong or stale instance
- Notice: a check passes locally while production fails; nobody can say which version was checked.
  Trigger: any result without an instance header; local and production counts disagree.
- Rule: every check output starts with its target identity: code revision, data version id, environment,
  tenant set. Checks against caches, old dev servers, other worktrees or index files are NOT-CHECKED for
  claims about production. Hydrate the live version into a fresh workspace with one command; reviewers get
  read-only access to the live store and pin the snapshot at the start.
- Check: grep the report for claims without an instance line; each is downgraded to NOT-CHECKED.

### ST-04 Merge now, verify later, and the integration bottleneck
- Notice: merged changes carry "not verified"; defects surface days later in batches at the one person
  who merges. Trigger: more than 20% of merged changes in the window carry an "unverified" marker.
- Rule: a change that touches a seam (artifact shape, vocabulary, producer graph or lineage, source of
  truth, promotion, tenant scope, model stage) merges only after a production-shaped mini-tenant check
  (G4 smoke records through the full chain, every final consumer included) ran on the change. CI from day
  one. Batches of parallel changes merge with one reduced verification round.
- Check: the change record lists the mini-tenant check id; no open NOT-CHECKED on a seam without an owner
  and a date.

### ST-05 Human-gate waits
- Notice: routine actions wait for a yes; uncertain values wait for an expert for weeks. Trigger: any
  item waiting more than one working day on a human.
- Rule: the user writes down standing permissions for well-defined, reversible routine action classes
  (who granted them, scope, expiry); the agent never grants itself one (truth rule 9 in SKILL.md).
  Uncertain values get labelled working choices with evidence (`status: assumed`) and a human override
  path. Questions are batched, deduped and ranked by unlock fan-out (`contracts-by-construction.md`
  section 10).
- Check: no blocked item older than one working day whose action class has a standing permission; every
  question carries a consumer key and fan-out count.

### ST-06 Spot fixes and fix-of-fix chains
- Notice: each fix is judged only on the reported case. Trigger: a file or rule fixed three or more times
  within 48 hours; one mode fixed twice; a revert; three or more failed runs sharing a first-error class
  (run economics step 2).
- Rule: every pinpointed defect goes through INCIDENT mode: class predicate, sibling sweep, root fix,
  earliest detector. For multi-case rules (geometry, precedence, tiered rates) write the decision table
  before the first fix. Every rule change ships a corpus-wide per-unit differential (blast radius); error
  grouping (`gate-ladder.md` G8) turns scattered reports into one platform fix.
- Check: the fix record has a class predicate, sibling count and blast-radius diff id.

### ST-07 Premature done and the human as oracle
- Notice: completion claims get retracted. Trigger: two "are you sure" exchanges on one item; a
  self-correction after a done claim; an acceptance record citing a test that does not exist.
- Rule: "done" is a computed predicate written before the work starts; the claim quotes the command output
  and names the live surface where the result is visible, with the instance identity. Every cited check
  resolves and runs (`gate-ladder.md` G1 citation resolution).
- Check: each done claim has (predicate, command, output excerpt, instance, surface).

### ST-08 Instrument work instead of output
- Notice: days spent on metrics, gates and documents while no delivered value moved. Trigger: a work item
  closes with moved metrics N = 0; a branch is staffed whose ceiling was computable in seconds.
- Rule: before staffing instrument work, compute its ceiling (the most it could move the deliverable) in
  minutes, not days; after the work, report "moved metrics: N" (N = 0 must be reported) with before/after.
- Check: each instrument task has a ceiling estimate and a moved-metrics line.

### ST-09 Plan churn, WIP explosion, refactor during delivery
- Notice: priorities multiply; a large refactor near a milestone deletes guards. Trigger: WIP above the
  cap; more than one live ordering; a refactor touching guarded code within two weeks of a milestone.
- Rule: one ordering; a mechanical WIP cap; no refactor inside the milestone freeze window; migrations use
  a strangler pattern with parity gates; never delete or loosen a guard before its replacement kills the
  same seeded faults. A parity gate's scope is every field and predicate any consumer reads, not only the
  quantity being refactored.
- Check: WIP count <= cap; every removed guard has a replacement id with killed seeded faults.

### ST-10 Multi-agent collisions
- Notice: lost work after a shared stash or checkout; duplicate implementations. Trigger: two agents edit
  one file area; a lost hunk after merge; shared stash or scratch space; colliding migration ids.
- Rule: one worktree or branch per agent; before starting, list open changes and worktrees touching the
  same files; file-area locks with expiry; acknowledged messages; a lost-hunk check before merge (every
  hunk of each branch is present after the merge or explicitly dropped).
- Check: lock record per file area; lost-hunk check output attached to the merge.

### ST-11 Knowledge sprawl and rediscovery
- Notice: agents rediscover facts or act on stale comments. Trigger: the same ad hoc inspection repeated
  three times; a comment or doc citing a path or command that does not resolve.
- Rule: any manual inspection repeated three times becomes a tool or one canonical line in the project
  instructions; paths and commands cited in docs and comments are linted (G1 citation resolution);
  documentation and evidence size have ratchets. Build the chain map from code and runtime, not from docs.
- Check: the citation lint is green; the repeated-command list is shorter than in the last batch.

### ST-12 Noisy and blind reviews
- Notice: review findings are refuted as intentional; one finding arrives from several reviewers.
  Trigger: refuted share above 10% in a round; one finding reported by three or more finders. (In the
  source history 14% were refuted, and cheap-model audits were wrong about one time in three.)
- Rule: reviewers receive the intentional-state registry (documented deliberate behaviours) and runtime
  read access; findings are deduped in two stages, by candidate signature before the refutation pass and
  by class predicate after classification (`hunt-and-stop.md` section 2); verifiers run in a separate
  context and see the source, not the finder's reasoning.
- Check: refuted share and duplicate share per review round are reported; refuted-as-intentional falls.

### ST-13 Test churn and no CI
- Notice: environment-dependent reds become "normal"; suites guard code about to be deleted. Trigger: a
  failure accepted as "also red on the base"; a suite longer than one hour; no CI on the main branch.
- Rule: tiered tests (G1 seconds, G2 minutes, slow suite nightly); hermetic fixtures; CI from day one; a
  quarantine list compared as a SET (names), never as a count; no new tests for code about to be replaced.
- Check: quarantine set diff per change is empty or explained.

### ST-14 Fragile long sessions and workflows
- Notice: work dies with a session, a reboot or a quote character in an argument. Trigger: work lost to a
  session end, rate limit or reboot; a job longer than an hour without checkpoints.
- Rule: long work runs as short, checkpointed, idempotent jobs with durable state outside the session;
  arguments are parsed defensively (structured, not interpolated into shell strings); ledgers are written
  to files as you go, so a hunt can resume from them.
- Check: killing a job mid-way and restarting it gives the same final state.

### ST-15 Budget burned on open-ended model work
- Notice: a whole model budget spent with zero applied results. Trigger: applied results = 0 after a
  budgeted pass; identical request digests paid more than once.
- Rule: pilot 20 items and measure the acceptance rate before scaling; one question per missing fact with
  candidates and the consumer key that will read the answer; cache by request digest; open-ended
  "read everything and tell me" passes are forbidden on production budgets.
- Check: each batch record has pilot acceptance rate, cache hit rate and applied-results count.

## Done predicate template (ST-07)
```
DONE when all hold on instance <code_rev, version_id, env, tenants>:
  1. <command> exits 0 and prints executed_count > 0       (quote the line)
  2. <live surface> shows <expected observable>              (quote or screenshot path)
  3. NOT-CHECKED list is empty, or each item has owner + date
  4. guards added in this work killed their seeded faults   (guard ids)
```
