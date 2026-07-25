# Feature Factory - mechanical guards

These guards move the safety model from "ask the model nicely" to "the model cannot".
They live in the TARGET REPO (hooks + a check script), not in this skill, so installing
them touches shared repo files. In a repo worked by multiple live agents (Claude Mesh),
coordinate first: `~/.claude/claude-mesh/mesh sync`, claim the `.claude/` + `scripts/`
zone, announce, install, verify, release.

Until these are installed, the skill runs in MANUAL-GATE MODE: read-mostly, all changes
in a worktree, stop at a reviewed diff, and refuse the whole sensitive/invariant list
outright. Tell the operator the human is the only barrier.

---

## 1. PreToolUse deny-hook (the core barrier)

Blocks destructive / authority-crossing commands and writes outside the run worktree.
Save as `scripts/hooks/factory-guard.mjs` in the target repo and wire it as a PreToolUse
hook on `Bash|Edit|Write|MultiEdit`.

```js
#!/usr/bin/env node
// Reads the hook payload on stdin, denies forbidden actions, else allows.
import { readFileSync } from "node:fs";

const payload = JSON.parse(readFileSync(0, "utf8"));
const tool = payload.tool_name;
const input = payload.tool_input || {};

// Only enforce when the run marks itself active (set by the conductor per run).
const active = process.env.FEATURE_FACTORY_ACTIVE === "1";
const worktree = process.env.FEATURE_FACTORY_WORKTREE || "";

function deny(reason) {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: reason,
    },
  }));
  process.exit(0);
}

if (active && tool === "Bash") {
  const cmd = String(input.command || "");
  const forbidden = [
    /\bgit\s+push\b/, /\bgit\s+commit\b/, /\bgit\s+add\s+-A\b/, /\bgit\s+add\s+\.\s*$/,
    /\bvercel\b/, /\bsupabase\s+db\s+push\b/, /\bsupabase\s+link\b/,
    /\bstripe\b/, /\bpnpm\s+publish\b/, /\bnpm\s+publish\b/,
    /\bpnpm\s+add\b/, /\bnpm\s+i(nstall)?\b/, /\bpnpm\s+i(nstall)?\b/,
    /\bpsql\b/, /\bDROP\s+POLICY\b/i, /\brm\s+-rf\s+\//,
  ];
  for (const re of forbidden) {
    if (re.test(cmd)) deny(`Feature Factory: '${cmd.slice(0,60)}' is human-authorized only. Stage a diff and hand off.`);
  }
}

if (active && (tool === "Edit" || tool === "Write" || tool === "MultiEdit")) {
  const path = String(input.file_path || input.path || "");
  if (worktree && path && !path.startsWith(worktree) && path.startsWith("/")) {
    deny(`Feature Factory: writes are confined to the run worktree (${worktree}).`);
  }
}

process.stdout.write(JSON.stringify({})); // allow
```

Wiring in the target repo `.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash|Edit|Write|MultiEdit",
        "hooks": [ { "type": "command", "command": "node scripts/hooks/factory-guard.mjs" } ] }
    ]
  }
}
```
The conductor sets `FEATURE_FACTORY_ACTIVE=1` and `FEATURE_FACTORY_WORKTREE=<path>` for
the duration of a run, and unsets them at handoff. Best of all, give the run worktree NO
push/deploy credentials at all, then the deny-hook is defense-in-depth, not the only
line.

---

## 2. Secret scanner

Run before ANY artifact (PR body, journal entry, finding, lessons.md) is written or
staged. Reject on match; never redact-and-continue silently for a staged commit.

Patterns: Supabase/JWT `eyJ[A-Za-z0-9_-]{10,}`, `SERVICE_ROLE`, `sk_live_`, `sk_test_`,
`rk_live_`, `-----BEGIN [A-Z ]*PRIVATE KEY-----`, `postgres(ql)?://[^\s]*:[^\s]*@`,
`AKIA[0-9A-Z]{16}`, and any `NEXT_PUBLIC_.*KEY` printed with a value. The existing
`local-leak-scanner` skill already encodes most of these, reuse its patterns.

Also assert the DB URL is localhost before any RLS/E2E run, so tests can never point at
production.

---

## 3. patterns-check.mjs (coherence + coverage + overengineering signals)

A new `scripts/patterns-check.mjs` in the target repo, wired into the gate. Two
severities: BLOCK (fails the gate) and WARN (advisory). Keep BLOCK small so the build
loop cannot deadlock on style.

BLOCK:
- Coverage: a new `src/app/api/**/route.ts`, an exported server action, or a migration
  RLS policy with zero referencing test.
- `globals.css` contains a component style (anything past tokens/resets/primitives).
- A hardcoded color/secret pattern in a file shipped to the browser bundle.
- An em-dash or en-dash anywhere in changed lines.

WARN:
- File over its line budget (.tsx/.ts 400, .module.css 300, globals.css 900).
- A new exported symbol referenced by <=1 caller (overengineering signal).
- A new abstraction/interface with a single implementation.
- A hex color or raw px where a design token exists.
- Diff size vs task size ratio above a threshold (gold-plating signal).

Feed WARN items into the Stage 4 overengineering/pointless lenses rather than blocking
the build. Provide a logged "justify-and-suppress" escape for a legitimate transient.

The rule-of-three lives here as the arbiter between the DRY lens and the overengineering
lens: extract a shared helper only at 2+ real callers, never speculatively. Record a
per-line decision so one lens cannot re-open a line another lens closed in a prior
round (kills DRY<->overengineering oscillation).

---

## 4. Concurrency / statefulness guards (repo conventions, not code)

- One git worktree per run (clean `.next` and files).
- A unique dev port per run; never bind the swarm's `:3000`.
- A DB-mutation mutex covering E2E + RLS (extend the existing BUILD-LOCK convention to
  mean "no other DB-mutating run"), because the local Supabase, Mailpit, and ports are
  global and a worktree does NOT isolate them.
- Namespace synthetic RLS test users per run.
- Announce the run in the MAIN tree mesh namespace (a worktree is a separate namespace
  peers do not read): the port and DB window in use.
- Serialize the expensive tail (build + gate + E2E + RLS) behind the global mutex; only
  the read-only planning/audit fan-out may overlap across runs.
- Teardown on exit: kill any dev-server PID the run spawned, reconcile or remove the
  worktree; on entry, clean stale worktrees from crashed runs.
