# Attribution

This skill is the `cook` skill from **github.com/Leonxlnx/cook** by **Leon Lin**, published under the
MIT License. It is included here unmodified, copied from upstream commit
`b23cac6fd9439dfddcab61b14808e7bf72549b46` (2026-10-31), so the team can install it from the same place
as our own skills.

Only the upstream `README.md` and `.gitignore` are left out. The original licence text is in
[`LICENSE`](./LICENSE) in this folder. For demos, updates and the author's notes, see the upstream
repository.

## Notes for our use

- A run is long and costly by design: the default time floor is 8 hours and the skill tells the agent
  not to ask questions after intake. Set a hard cap and a usage limit in the intake when the job is small.
- By default it prepares everything locally and does not push or publish. Keep it that way for client work.
- `scripts/side-by-side.mjs` needs Node 18+ and ffmpeg on PATH.
