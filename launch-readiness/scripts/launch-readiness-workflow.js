// Launch-readiness sweep: multi-round perspective finders + adversarial verification + plan synthesis.
// Read-only over the product: the ONLY file this workflow writes is the action plan at args.planPath.
//
// LAUNCH:
//   Workflow({ scriptPath: "<skill>/scripts/launch-readiness-workflow.js", args: {
//     projectDir:  "/abs/product",                 // required
//     catalogPath: "/abs/smell-catalog.md",        // required, the lens catalog
//     liveUrl:     "https://product.example",      // optional, enables live probes (read-only GETs)
//     lessonsPath: "/abs/lessons.md",              // optional growing lessons log
//     planPath:    "/abs/product/docs/launch-readiness-plan-YYYYMMDD.md", // optional, default <projectDir>/launch-readiness-plan.md
//     constraints: "intentional decisions finders must NOT report",
//     perspectives:["placeholder-content", ...],   // optional subset of catalog keys, default all 15; unknown keys throw
//     maxRounds:   2                               // discovery rounds (round 2+ = critic-directed probes), min 1
//   }})

export const meta = {
  name: 'launch-readiness-loop',
  description: 'Multi-round launch-readiness sweep: perspective finders, adversarial verification, synthesized action plan',
  phases: [
    { title: 'Find', detail: 'one finder agent per perspective per round' },
    { title: 'Verify', detail: 'one adversarial judge per area batch' },
    { title: 'Probe', detail: 'completeness critic proposes targeted extra probes' },
    { title: 'Plan', detail: 'synthesize the triage-able action plan' },
  ],
}

const A = (typeof args === 'string' && args.trim()) ? JSON.parse(args) : (args || {})
if (!A.projectDir) throw new Error('Pass args.projectDir (absolute path to the product)')
if (!A.catalogPath) throw new Error('Pass args.catalogPath (smell-catalog.md)')
const DIR = A.projectDir
const LIVE = A.liveUrl || null
const PLAN = A.planPath || (DIR + '/launch-readiness-plan.md')
const CONSTRAINTS = A.constraints || 'none stated'
const MAX_ROUNDS = Math.max(1, A.maxRounds || 2)
const LESSONS = A.lessonsPath || null

const ALL_PERSPECTIVES = [
  { key: 'placeholder-content', focus: 'placeholder copy: lorem ipsum, coming soon, template leftovers, example.com, leaked template variables' },
  { key: 'test-demo-data', focus: 'fake or seeded data visible in production: John Doe names, test emails and phones, fake testimonials, demo records' },
  { key: 'trust-legal', focus: 'legal trust surface: privacy/terms/refund pages, cookie consent, legal entity details in footer, stale copyright year' },
  { key: 'branding-assets', focus: 'default scaffolding assets: framework favicon, missing og-image, default 404/500 pages, UI-kit demo images' },
  { key: 'seo-metadata', focus: 'SEO and metadata: default titles, noindex leftovers, robots.txt, sitemap vs real pages, OG/Twitter cards, canonical, hreflang' },
  { key: 'dead-ends', focus: 'dead ends: href="#", buttons without handlers, nav to nonexistent pages, social links to network homepages, broken internal links' },
  { key: 'error-empty-states', focus: 'error and empty states: raw errors reaching users, undefined/NaN in UI, unstyled error pages, missing empty-state copy' },
  { key: 'forms-transactions', focus: 'forms and money paths: payment test keys in shipped config, sandbox email senders, forms without validation or feedback, price inconsistencies' },
  { key: 'copy-localization', focus: 'copy and localization: mixed languages, raw i18n keys rendered, missing diacritics, untranslated fallbacks, tone jumps' },
  { key: 'code-hygiene-leaks', focus: 'dev environment leaking: console.log in bundle, debugger, TODO/FIXME in shipped files, reachable dev/debug routes, sourcemaps in prod' },
  { key: 'security-config', focus: 'staging config live: localhost/staging URLs in prod code, secrets exposed to the client, http:// on https site, missing security headers' },
  { key: 'ops-analytics', focus: 'operating signals: missing analytics or error tracking, no health endpoint, unmounted observability config, debug banners visible' },
  { key: 'performance-polish', focus: 'performance polish: multi-MB images, layout shift, FOUC, render-blocking scripts, missing caching on static assets' },
  { key: 'responsive-mobile', focus: 'mobile experience: missing viewport meta, horizontal scroll, tiny tap targets, overflowing tables, hover-only interactions' },
  { key: 'funnel-walkthrough', focus: 'end-to-end walk of the primary user journey as a skeptical first-time customer, up to the last safe read-only step' },
]
let PERSPECTIVES = ALL_PERSPECTIVES
if (A.perspectives && A.perspectives.length) {
  const requested = Array.isArray(A.perspectives) ? A.perspectives : [A.perspectives]
  const validKeys = ALL_PERSPECTIVES.map(p => p.key)
  const unknown = requested.filter(k => !validKeys.includes(k))
  if (unknown.length)
    throw new Error(`Unknown perspective key(s): ${unknown.join(', ')}. Valid keys: ${validKeys.join(', ')}`)
  PERSPECTIVES = ALL_PERSPECTIVES.filter(p => requested.includes(p.key))
}
const DROPPED = ALL_PERSPECTIVES.filter(p => !PERSPECTIVES.includes(p)).map(p => p.key)
if (DROPPED.length)
  log(`Coverage reduced by caller: ${PERSPECTIVES.length}/${ALL_PERSPECTIVES.length} perspectives (dropped: ${DROPPED.join(', ')})`)

const FINDINGS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          title: { type: 'string', description: 'short specific title of the smell' },
          area: { type: 'string', description: 'perspective key this belongs to (use your probe label in critic-directed rounds)' },
          location: { type: 'string', description: 'file:line, or URL for live findings' },
          evidence: { type: 'string', description: 'the exact string / behavior observed' },
          whyNotLive: { type: 'string', description: 'one line: what this signals to a visitor' },
          suggestedFix: { type: 'string', description: 'one concrete line, machine-checkable where possible' },
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
          effort: { type: 'string', enum: ['S', 'M', 'L'] },
        },
        required: ['title', 'area', 'location', 'evidence', 'whyNotLive', 'suggestedFix', 'severity', 'effort'],
      },
    },
  },
  required: ['findings'],
}

const VERDICTS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          index: { type: 'integer', description: '1-based index into the findings list you were given' },
          isReal: { type: 'boolean' },
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
          reason: { type: 'string', description: 'one line: confirmed evidence, or why refuted' },
        },
        required: ['index', 'isReal', 'severity', 'reason'],
      },
    },
  },
  required: ['verdicts'],
}

const PROBES_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    probes: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          label: { type: 'string', description: 'short kebab-case probe name' },
          brief: { type: 'string', description: 'what to check and HOW (modality: built output, headers, emails, sitemap diff, specific directory)' },
        },
        required: ['label', 'brief'],
      },
    },
  },
  required: ['probes'],
}

const PLAN_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    tasks: { type: 'integer' },
    high: { type: 'integer' },
    medium: { type: 'integer' },
    low: { type: 'integer' },
    highlights: { type: 'array', items: { type: 'string' }, description: 'the 3-5 findings that most damage the "we are live" impression' },
  },
  required: ['tasks', 'high', 'medium', 'low', 'highlights'],
}

const READ_ONLY = `HARD RULES:
- READ-ONLY: do not edit, create, or delete any file in the project. Do not run builds that mutate state, do not install packages.
- Live checks are read-only GET requests (curl is fine). Never submit forms, never trigger payments, never create accounts.
- Judge the SHIPPED surface: what a visitor, customer, or crawler can reach. Internal docs/tests/comments only count if they leak into it.
- In every text field you return, never use em-dashes or en-dashes; use commas or hyphens. Keep Lithuanian diacritics exactly correct.
- Do NOT report anything covered by these intentional constraints:
${CONSTRAINTS}`

function finderPrompt(label, brief) {
  return `You are a launch-readiness reviewer inspecting ONE aspect of a product about to be (or already) live.

Project directory: ${DIR}
${LIVE ? `Live product URL (probe it with read-only GETs): ${LIVE}` : 'No live URL given: judge the shipped source and build output only.'}

Your single lens: ${label}
Focus: ${brief}

First read your lens's section in the smell catalog: ${A.catalogPath} (find the section matching your lens; if none matches exactly, apply the catalog's severity/effort guides and the brief above).${LESSONS ? `
Also read past lessons and apply them: ${LESSONS}` : ''}

Hunt ONLY this class of smell. Use grep/glob over the project and, when a live URL is given, curl the relevant pages. Verify each candidate yourself: open the file, confirm the line, confirm it ships (is reachable from the app's real entry points, not a dead fixture).

${READ_ONLY}

Return your TOP findings (max 8, most damaging first; if you found more than 8, still return only the top 8 and make the 8th finding's evidence note how many were left). Each finding needs: exact location (file:line or URL), the exact evidence string, why it signals "not really live" to a visitor, a one-line concrete fix, severity per the catalog guide, and effort S/M/L. If the lens is fully clean, return an empty findings array, do not invent problems.`
}

function verifierPrompt(areaKey, items) {
  return `You are an adversarial verifier. Another agent claims these launch-readiness problems in the product at ${DIR}${LIVE ? ` (live at ${LIVE})` : ''}. Your default stance: REFUTE.

Findings to judge (JSON, 1-based order):
${JSON.stringify(items, null, 2)}

For EACH finding, check yourself with tools:
1. Does the cited location exist and contain the cited evidence? (Read the file / curl the URL.)
2. Does it actually ship? A visitor, customer, or crawler must be able to reach it. Dead code, tests, and internal docs are refuted.
3. Is it intentional? These constraints are off-limits as findings:
${CONSTRAINTS}
4. Re-grade severity per user impact: high = first-time visitor likely sees it or funnel breaks; medium = attentive visitor or crawler sees it; low = edge case or view-source only.

${READ_ONLY}

Return exactly one verdict per finding, covering EVERY 1-based index from 1 to ${items.length}, no index twice. Be strict: a finding you could not confirm with your own eyes is isReal=false.`
}

function criticPrompt(round, confirmedSoFar, coveredLabels) {
  return `You are a completeness critic for a launch-readiness sweep of ${DIR}${LIVE ? ` (live at ${LIVE})` : ''}.

Round ${round} just finished. Perspectives already covered: ${coveredLabels.join(', ')}.
Confirmed findings so far (JSON):
${JSON.stringify(confirmedSoFar.map(f => ({ area: f.area, title: f.title, location: f.location, severity: f.severity })), null, 2)}

Ask: what would a skeptical customer or crawler still catch that NO finder has looked at yet?
Prefer a DIFFERENT modality than what produced the findings above: the built/deployed output instead of
source, HTTP response headers, transactional email templates, sitemap vs actual pages, the hottest
directory that keeps appearing in findings, a locale nobody rendered. Also probe deeper where findings
cluster: a directory with 3+ confirmed smells likely hides more.

${READ_ONLY}

Propose at most 6 targeted probes, each with a short kebab-case label and a one-paragraph brief saying
exactly what to check and how. Propose ONLY probes likely to yield NEW findings; if coverage is genuinely
complete, return an empty probes array.`
}

function planPrompt(confirmed, coverage) {
  return `You are synthesizing the final launch-readiness action plan.

Confirmed findings (JSON):
${JSON.stringify(confirmed, null, 2)}

Coverage facts to state verbatim in the header: ${coverage}

Write the plan as Markdown to this exact path using the Write tool: ${PLAN}

Format (follow exactly):
1. H1 title "Launch-readiness action plan", then a header block: target (${DIR}${LIVE ? `, live ${LIVE}` : ''}),
   coverage facts, and counts by severity.
2. "How to use" note: 3 lines max, saying tasks are stable-numbered, triage by deleting or editing task
   lines, then hand this file to an execution loop.
3. Tasks grouped by severity (High, then Medium, then Low), inside each group ordered by area.
   Each task is ONE checkbox line:
   - [ ] **LR-NN** (severity, effort) title. Location: \`file:line or URL\`. Evidence: "...". Fix: ...
   Number LR-01, LR-02, ... in the order they appear in the file. IDs must be unique and stable.
4. Merge duplicates that survived (same location + same root cause): one task, evidence lists both sightings.
5. A final "Deferred / not doing" empty section for triage to move dropped tasks into.

Do NOT use em-dashes or en-dashes anywhere; use commas or hyphens. Keep any Lithuanian diacritics exactly correct.
Do not edit any other file. After writing, return the counts and the 3-5 highlights that most damage the "we are live" impression.`
}

const seen = new Set()
const confirmed = []
let roundsRun = 0
let rawTotal = 0
let refutedTotal = 0
let unjudgedTotal = 0
const coveredLabels = []

// Key = location minus trailing :line(:col), so file dupes across rounds collapse but URLs stay whole.
const dedupKey = f =>
  (f.location || '').replace(/:\d+(:\d+)?$/, '') + '|' +
  (f.title || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().slice(0, 60)

for (let round = 1; round <= MAX_ROUNDS; round++) {
  let wave
  if (round === 1) {
    wave = PERSPECTIVES.map(p => ({ label: p.key, brief: p.focus }))
    log(`Round 1: launching ${wave.length} finder agents, one per perspective`)
  } else {
    const critic = await agent(criticPrompt(round - 1, confirmed, coveredLabels), {
      schema: PROBES_SCHEMA, label: `critic:round-${round - 1}`, phase: 'Probe',
    })
    const proposed = (critic && critic.probes) || []
    wave = proposed.slice(0, 6)
    if (proposed.length > wave.length)
      log(`Round ${round}: critic proposed ${proposed.length} probes, capped at 6 (dropped: ${proposed.slice(6).map(p => p.label).join(', ')})`)
    if (!wave.length) { log(`Round ${round}: critic found no gaps, sweep is dry`); break }
    log(`Round ${round}: critic proposed ${wave.length} targeted probes: ${wave.map(w => w.label).join(', ')}`)
  }
  roundsRun = round
  coveredLabels.push(...wave.map(w => w.label))

  // Barrier on purpose: dedup needs every finder's output before verification spend.
  const finderResults = await parallel(wave.map(w => () =>
    agent(finderPrompt(w.label, w.brief), { schema: FINDINGS_SCHEMA, label: `find:${w.label}`, phase: 'Find' })
      .catch(() => null)
  ))
  const deadFinders = wave.filter((w, i) => !finderResults[i]).map(w => w.label)
  if (deadFinders.length)
    log(`Round ${round}: ${deadFinders.length} finder(s) returned nothing usable, lenses uncovered this round: ${deadFinders.join(', ')}`)
  const found = finderResults.filter(Boolean).flatMap(r => r.findings || [])
  rawTotal += found.length

  const fresh = found.filter(f => {
    const k = dedupKey(f)
    if (seen.has(k)) return false
    seen.add(k)
    return true
  })
  log(`Round ${round}: ${found.length} raw findings, ${fresh.length} fresh after dedup`)
  if (!fresh.length) { log(`Round ${round}: nothing fresh, stopping`); break }

  const byArea = {}
  for (const f of fresh) (byArea[f.area || 'misc'] = byArea[f.area || 'misc'] || []).push(f)
  const judged = await parallel(Object.entries(byArea).map(([areaKey, items]) => () =>
    agent(verifierPrompt(areaKey, items), { schema: VERDICTS_SCHEMA, label: `verify:${areaKey}`, phase: 'Verify' })
      .then(v => ({ areaKey, items, verdicts: (v && v.verdicts) || [] }))
      .catch(() => ({ areaKey, items, verdicts: [] }))
  ))
  for (const j of judged.filter(Boolean)) {
    const judgedIdx = new Set()
    for (const verdict of j.verdicts) {
      const f = j.items[verdict.index - 1]
      if (!f || judgedIdx.has(verdict.index)) continue // out-of-range or duplicate index: ignore
      judgedIdx.add(verdict.index)
      if (verdict.isReal) confirmed.push({ ...f, severity: verdict.severity || f.severity, verifierNote: verdict.reason })
      else refutedTotal++
    }
    const missed = j.items.length - judgedIdx.size
    if (missed > 0) {
      unjudgedTotal += missed
      log(`Round ${round}: verifier for area "${j.areaKey}" left ${missed} finding(s) without a verdict, dropped as unconfirmed`)
    }
  }
  log(`Round ${round}: ${confirmed.length} confirmed total, ${refutedTotal} refuted, ${unjudgedTotal} unjudged`)
}

phase('Plan')
if (!confirmed.length) {
  log('No confirmed findings, the product is launch-clean under the perspectives run. No plan file written.')
  return { confirmed: 0, raw: rawTotal, refuted: refutedTotal, unjudged: unjudgedTotal, rounds: roundsRun, planPath: null }
}
const coverage = `${PERSPECTIVES.length}/${ALL_PERSPECTIVES.length} perspectives` +
  (DROPPED.length ? ` (dropped by caller: ${DROPPED.join(', ')})` : '') +
  `, ${roundsRun} round(s), ${coveredLabels.length} finder agents, ${rawTotal} raw findings, ` +
  `${confirmed.length} confirmed, ${refutedTotal} refuted by verification` +
  (unjudgedTotal ? `, ${unjudgedTotal} dropped without a verdict` : '')
log(`Synthesizing action plan from ${confirmed.length} confirmed findings into ${PLAN}`)
const summary = await agent(planPrompt(confirmed, coverage), { schema: PLAN_SCHEMA, label: 'synthesize-plan', phase: 'Plan' })
if (!summary)
  log(`Plan synthesis agent returned no structured summary; verify the plan file exists at ${PLAN} before triage`)

return {
  planPath: PLAN,
  rounds: roundsRun,
  raw: rawTotal,
  confirmed: confirmed.length,
  refuted: refutedTotal,
  unjudged: unjudgedTotal,
  tasks: summary ? summary.tasks : confirmed.length,
  bySeverity: summary ? { high: summary.high, medium: summary.medium, low: summary.low } : null,
  highlights: summary ? summary.highlights : [],
}
