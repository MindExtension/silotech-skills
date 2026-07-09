# Refine lessons (cross-project self-improving log)

Meta-lessons about running the refine loop well, learned across projects. Domain-specific design or code
lessons belong in the relevant domain skill or style guide, not here; this log holds only the cross-project
lessons about running the loop itself. Append a dated one-liner when a run teaches something reusable.
Format: `- [YYYY-MM-DD] Observation -> Rule.`

## Lessons

- [2026-07-08] Reviewers that judged only the source HTML missed wasted space that only shows in the render. -> Always give reviewers the real rendered snapshot, not just the source; judge reality.
- [2026-07-08] The first pass fixed the obvious (text size) but left the deeper flaw (top-aligned content in tall containers) on several units. -> Expect multiple passes; after pass 1, re-observe and run a targeted pass on units still below bar. One pass is rarely enough.
- [2026-07-08] The most effective fix was to write the newly-observed failure as a sharp lesson, then re-run; agents reading the updated lesson fixed it correctly. -> Harvest the lesson BEFORE the re-pass, not after; the loop improves within a single session, not just across sessions.
- [2026-07-08] Editing one shared file with many parallel agents would have raced. Splitting into one file per unit made the whole pass conflict-free and parallel. -> Always isolate units (own file or worktree) before fanning out writers; verify the split roundtrips before touching content.
