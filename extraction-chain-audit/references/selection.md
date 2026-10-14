# Selecting and ordering the failure modes for one chain

Use in AUDIT A5 (path B order) and A7 (coverage critic), and in BUILD for a new stage. AUDIT path A does
not open this file before it is sealed: in A2 the chain facts are recorded as plain answers to the
feature questions listed in `templates.md` section 2, and mapped to ids here afterwards.

Output: an ordered applicable-mode list (FM and ST ids, each with an S estimate and the reason it
applies) under "Applicable modes" in `chain-map.md`. Filters only add modes; a mode is dropped only with
a written reason that cites the chain-map feature answer ("no model stage in this chain"), which becomes
its `not_applicable` row in `coverage.jsonl` (`feature` and `reason`). The universal modes in section 1
are never `not_applicable`.

## 1. Universal modes (always applicable)
FM-04 false absence, FM-05 error laundering, FM-15 unconsumed facts, FM-23 vacuous guards, ST-03 wrong
instance, ST-07 premature done. Every chain has readers, handlers, consumers, guards and claims of
completion.

## 2. Feature questions mapped to modes (answers recorded in `chain-map.md` during A2)
| If the chain has... | Add |
|---|---|
| Any LLM or ML stage | FM-21, FM-09, FM-06, ST-15 |
| Several tenants (clients, entities, sites, projects) sharing code or stores | FM-19, FM-26, FM-01 |
| Several readers or runtimes of one artifact (UI and worker, two languages, exports, internal tools) | FM-02, FM-28, FM-31 |
| Published versions, a "current" pointer, caches | FM-17, FM-18, FM-02 |
| Human answers, approvals or overrides feeding back | FM-16, FM-30, ST-05 |
| Delivered aggregates or totals | FM-12, FM-13, FM-14, FM-27, FM-22 |
| Joins across sources or stages | FM-03 |
| Units, signs, frames, coordinates, currencies, dates, scales | FM-11 |
| Text in national scripts, codepages, source-format escape codes | FM-29, FM-08, FM-11 |
| Job queues, workers, leases or claim caps | FM-09, FM-20, ST-14 |
| Fallbacks, defaults, imputation, provisional values | FM-06, FM-07 |
| Reference answers, gold sets, prior-period figures, source totals | FM-10, FM-22 |
| Multi-carrier sources (nested containers, images, attachments, schedules, layers) | FM-08, FM-29 |
| Caps, budgets, pagination, filters, size limits | FM-09 |
| Status or verdict fields shown to users or exported | FM-24 |
| Simplified copies reused (display values, rounded amounts, decimated geometry, summaries) | FM-25 |
| Definitions that experts may choose differently (boundaries, conventions, comparators) | FM-27 |
| Runs longer than a few minutes, or paid fan-out | ST-01, ST-02, ST-14, FM-20 |
| Several agents or people changing the chain at once | ST-04, ST-09, ST-10, ST-12 |
| Long-lived project with docs, plans and acceptance records | ST-11, ST-13, ST-08 |
| Repeated fixes, reverts or reopened items in one area | ST-06, plus the modes of those fixes |
| Strict blocking gates on uncertain values | FM-30, ST-05 |

## 3. Chain shapes (starting sets and order; still apply sections 1, 2 and 4)
| Shape | Typical stages | Check first, in this order |
|---|---|---|
| Document to register (legal clause register, ESG disclosure register, policy library) | ingest, parse (OCR, layout), extract (spans), identify/match (parties, defined terms), normalize (dates, vocabularies), assemble, publish, read | FM-08, FM-09, FM-21, FM-03, FM-04, FM-01, FM-29, FM-07, FM-16 |
| Multi-source consolidation (financial consolidation, group emissions inventory) | ingest (system exports), normalize (accounts, currencies, signs), identify/match (intercompany), derive, aggregate, publish | FM-02, FM-11, FM-14, FM-13, FM-17, FM-19, FM-06, FM-27 |
| Record abstraction (clinical abstraction, claims coding, registry entry) | ingest notes, extract, normalize (codes), derive (stage, eligibility), assemble, registry load | FM-04, FM-07, FM-21, FM-09, FM-06, FM-16, FM-10 |
| Drawing or scan takeoff (engineering quantities, surveying) | ingest drawings, parse (layers, blocks, geometry), extract (annotations), identify/match (labels to objects), normalize (frames, units), derive (geometry), aggregate, export | FM-08, FM-11, FM-03, FM-25, FM-12, FM-14, FM-29, FM-27, FM-26 |
| Survey and statistical aggregation (official statistics, panels, audits by sample) | ingest responses, normalize (codes, weights), edit and impute, aggregate (weighted estimates), publish tables | FM-06, FM-13, FM-14, FM-12, FM-22, FM-29, FM-18 |
| API and model orchestrated enrichment (agentic extraction over many services) | ingest via APIs, extract with models, identify/match, assemble, publish | FM-21, FM-20, FM-02, FM-05, FM-09, ST-15, ST-02 |

## 4. Stage types and the modes that originate there
Used by the completeness critic to build the FM x stage coverage matrix (`hunt-and-stop.md` section 3):
for every stage in the chain map, each mode listed for its type gets a cell naming the effective guard and
its gate, or an empty cell.

| Stage type | Does | Modes originating here |
|---|---|---|
| ingest | receives and registers sources | FM-04, FM-08, FM-09, FM-20, FM-26, FM-29 |
| parse | turns files into primitives (text, tables, geometry, fields) | FM-08, FM-09, FM-29 |
| extract | pulls candidate facts (rules, OCR, LLM) | FM-08, FM-09, FM-15, FM-21, FM-25, FM-29 |
| identify/match | binds facts to entities, joins sources | FM-03, FM-04, FM-06, FM-10, FM-11, FM-14, FM-21, FM-26 |
| normalize | units, frames, vocabularies, identifiers | FM-01, FM-03, FM-07, FM-11, FM-13, FM-25, FM-27 |
| derive/compute | rules and formulas | FM-05, FM-06, FM-10, FM-11, FM-12, FM-22, FM-24, FM-26, FM-27, FM-28, FM-30 |
| assemble | builds composite records | FM-01, FM-03, FM-13, FM-14, FM-15, FM-19, FM-30 |
| aggregate | totals, summaries, estimates | FM-12, FM-13, FM-14, FM-15, FM-16, FM-17, FM-27 |
| publish/version | makes a version visible or the base of the next run | FM-01, FM-02, FM-17, FM-18, FM-19 |
| read/display | screens, APIs, reports reading versions | FM-02, FM-04, FM-07, FM-24, FM-28, FM-31 |
| export | deliverable files | FM-04, FM-07, FM-24, FM-25 |
| ops/runtime | execution environment, jobs, storage | FM-02, FM-05, FM-09, FM-17, FM-19, FM-20, FM-21 |
| human loop / process | reviews, decisions, metrics, guards | FM-10, FM-16, FM-22, FM-23, FM-28, FM-30 |

## 5. Order
Rank the applicable list by: S first (from the delivered outputs the mode can move), then silent before
loud, then the starred modes in `failure-modes.md` (most often unguarded), then detection lag (modes
whose earliest possible gate is far below where they are caught today). Path B probes in this order, so a
budget stop leaves the least important modes NOT-CHECKED.
