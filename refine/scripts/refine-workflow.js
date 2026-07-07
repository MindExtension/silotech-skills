// Generic refine loop: one expert-reviewer agent per unit, each improves its OWN file in place.
// Isolated files => fully parallel, no write conflicts. Domain-agnostic: the lenses and constraints
// come from args, so the same script refines slides, doc sections, code files, etc.
//
// LAUNCH:
//   Workflow({ scriptPath: "<skill>/scripts/refine-workflow.js", args: {
//     unitFiles:  ["/abs/unit-01.ext", ...],   // required, one editable file per unit
//     snapshots:  ["/abs/unit-01.png", ...],   // optional, per-unit rendered view to look at
//     lensPath:   "/abs/rubric.md",            // or lensText: "...", one is required
//     lessonsPath:"/abs/lessons.md",           // optional growing lessons log
//     purpose:    "what this artifact is for and for whom",
//     constraints:"what must NOT change",
//     onlyUnits:  [2, 7]                        // optional 1-based indices to re-run just those
//   }})

export const meta = {
  name: 'refine-loop',
  description: 'Generic parallel improvement loop: one expert reviewer per unit observes it through the derived lenses and improves its own file',
  phases: [{ title: 'Improve', detail: 'one reviewer-improver agent per unit' }],
}

const A = (typeof args === 'string' && args.trim()) ? JSON.parse(args) : (args || {})
const UNITS = A.unitFiles || []
if (!UNITS.length) throw new Error('Pass args.unitFiles = array of editable unit file paths')
if (!A.lensPath && !A.lensText) throw new Error('Pass args.lensPath or args.lensText')
const SNAP = A.snapshots || []
const PURPOSE = A.purpose || 'not stated, infer it from the unit'
const CONSTRAINTS = A.constraints || 'do not change meaning, data, or wording; improve form and quality only'
const ONLY = (A.onlyUnits && A.onlyUnits.length) ? A.onlyUnits : UNITS.map((_, i) => i + 1)

const SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    unit: { type: 'integer' },
    changed: { type: 'boolean' },
    scoresBefore: { type: 'string' },
    changes: { type: 'array', items: { type: 'string' } },
  },
  required: ['unit', 'changed', 'changes'],
}

function prompt(idx) {
  const file = UNITS[idx - 1]
  const snap = SNAP[idx - 1]
  const lens = A.lensPath ? `Read the evaluation lenses / rubric here and score against EVERY check: ${A.lensPath}` : `Evaluation lenses / rubric:\n${A.lensText}`
  const lessons = A.lessonsPath ? `\n- Read the growing lessons log (past mistakes and their rules) and apply it: ${A.lessonsPath}` : ''
  const snapLine = snap ? `\n- Rendered snapshot of this unit, LOOK at it to judge reality, not just source: ${snap}` : ''
  return `You are a top-tier expert improving ONE unit of a larger artifact.

Artifact purpose (drives every judgment): ${PURPOSE}

Unit to improve, OVERWRITE this exact file with your improved version: ${file}${snapLine}
- ${lens}${lessons}

STEP 1. Read the lenses${A.lessonsPath ? ', the lessons' : ''}${snap ? ', the snapshot' : ''}, and the unit file. Score this unit against every lens and find the concrete weaknesses. Judge the REAL output where a snapshot is given.

STEP 2. Rewrite the unit to raise it on every failing lens. Make real, specific improvements, not cosmetic tweaks.

HARD CONSTRAINTS (do not violate): ${CONSTRAINTS}
- Keep the unit self-contained and valid in its format so the artifact still assembles and builds.
- Keep the house style and conventions of the surrounding artifact; refine form, do not homogenize voice.
- No em-dashes or en-dashes; use commas or hyphens. Keep any diacritics correct.

STEP 3. Overwrite ${file} with your improved unit using the Write tool.

Return the unit number, whether you changed it, a one-line note of the worst scores you found, and a short bullet list of the concrete changes you made.`
}

const results = await parallel(
  ONLY.map(n => () => agent(prompt(n), { schema: SCHEMA, label: `refine:unit-${String(n).padStart(2, '0')}`, phase: 'Improve' }))
)

const ok = results.filter(Boolean)
return {
  requested: ONLY.length,
  returned: ok.length,
  changed: ok.filter(r => r.changed).length,
  perUnit: ok.map(r => ({ unit: r.unit, changed: r.changed, n: (r.changes || []).length })),
}
