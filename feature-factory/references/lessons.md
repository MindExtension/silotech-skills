# Feature Factory - accumulated lessons

Read this at the start of every run; append a dated entry at the end. Each lesson is a
mistake made once, turned into a guard so it is not made again. Keep entries short and
actionable. Core safety rules do NOT live here (they live in SKILL.md and the mechanical
guards), so a poisoned lesson can never weaken them.

---

## Seeded from the design adversarial review

These came from five adversarial reviewers stress-testing the design before any run.

- **The builder grading its own tests is the top false-green risk.** Emit acceptance
  tests as executable stubs in Stage 2, forbid the builder from editing them, and
  mutation-check security tests in Stage 4 (flip the impl, the test must go red).
- **Gates prove syntax and known cases, not intent.** A correct implementation of the
  WRONG spec sails through green. The whole bet rests on Stage 1-2 converting a vague
  request into an explicit spec and bouncing questions, not guessing.
- **The security lens must check fixed invariants, not the request's spec.** A
  legit-looking request ("public profiles", "share link without auth") faithfully
  weakens RLS and the regenerated tests expect the weakened behavior. Invariants are
  attacker-independent; the spec is not.
- **A git worktree isolates files, NOT stateful services.** A local database, mail
  catcher, and ports are global. Unique port + DB-mutation mutex + per-run RLS user
  namespace, or two runs corrupt each other's build anyway via the shared DB.
- **A worktree is a separate mesh namespace.** Peers in the main tree get no signal the
  factory exists. Announce the run (port + DB window) in the MAIN tree mesh explicitly.
- **The human gate must be mechanical.** An agent with bash+git can push/deploy any
  time; one injected "OWNER AUTHORIZED" mesh line can flip a prose gate. No credentials
  in the worktree + a deny-hook. Authority only via the operator's direct channel.
- **DRY vs overengineering lenses oscillate.** Rule-of-three + a per-line decision
  ledger so a lens cannot re-open a line another closed; hard maxRounds; report
  unresolved oscillation to a human.
- **Loop-until-dry with no cap is runaway cost.** maxRounds + dry-counter + a token
  budget guard; scale fan-out to the triage size; log what was capped (silent
  truncation reads as "clean").
- **Half-applied multi-doc spec poisons every downstream gate.** Write the doc set as
  one atomic patch; on gate-red revert the whole set and retry; never proceed partial.
- **Confidence triage is miscalibrated by default.** Bias conservative; a hard tripwire
  independent of model judgement routes sensitive requests to a human; the model may
  only downgrade risk inside non-sensitive areas.
- **The PM dream dies at the human seams, not the code.** Two-tier question routing
  (PM-answerable vs owner-only), a status card as the supervision surface, a per-run
  expectation statement up front, and never showing a PM a stack trace. "Ship" = owner
  merges; the PM's job ends at PR-ready.
- **A died/off-format fan-out result silently shrinks coverage.** `filter(Boolean)`
  every fan-out and schema-validate; if too many finders died, FAIL the stage loudly
  rather than proceed on partial coverage.

---

## Field-hardened guards (generalized across runs)

Reusable operational lessons distilled from real runs, with all project specifics removed.

- **A fan-out audit is the first casualty of a session/usage limit.** When many agents
  die mid-run, scale the fan-out to the REMAINING budget and fall back to conductor-inline
  mode; never re-launch workflows that will just fail again on the same limit.
- **"Dropped: unconfirmed by refuters" is not a refutation when the refuters died.**
  Treat a dropped list from a limit-killed verify pass as UNVERIFIED, and re-check each
  finding locally and deterministically before discarding it.
- **A symlinked `node_modules` is a shared mutable resource.** A peer session reinstalling
  in the main checkout can briefly empty it and break a worktree's tool symlinks; before
  declaring a gate red, check whether a peer is reinstalling and re-run once it repopulates,
  or install into the worktree's own `node_modules` when peers are active.
- **A worktree cut from `origin/<base>` has no `node_modules` and the base may have moved
  past the main checkout's last install.** Prefer a worktree-local install whenever the
  base moved; a symlink only works while the lockfiles share lineage.
- **Green acceptance tests + green trees do NOT mean the feature works.** A change can
  silently no-op on most real targets when synthetic test fixtures do not resemble
  production data. Always include at least one product-level test that asserts a COVERAGE
  number (what fraction of real targets got the new behavior), not just synthetic + one case.
- **A PR-review-fix run should reuse the review's confirmed findings as its spec** instead
  of re-deriving one through the full plan/spec stages; a fix list is not a green-field feature.
- **Consolidate audit findings before fixing.** A size-M diff can return 20+ confirmed
  findings that collapse to a handful of unique root causes across lenses; fixing before
  consolidating causes double-fixes and contradictory edits.
- **Root-cause a red regression suite against the base branch before owning it.** A
  pre-existing failure (someone changed labels without updating the spec) is not your
  regression; grep whether your diff even touches the asserted components.
- **Environment reality beats prose.** Before betting a run on a browser download, verify
  the exact build the installed test runner wants; system Chrome via a channel config placed
  OUTSIDE the repo is a reliable fallback when headless-shell downloads stall.

---

## Run log

<!-- Append one entry per real run: date | feature | what surprised us | the guard added. -->
