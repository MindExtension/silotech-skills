# Technique cards and sources

One card per technique: what it catches, how this skill applies it, where it sits on the gate ladder,
its blind spot, and sources by title and URL (no quotes; read the source before quoting a number from
it). Cards are grouped by role in the skill. Read this file to understand why a step exists or to cite
a method; the steps themselves live in the other references.

## A. Systematic hazard analysis (path A of AUDIT, step B3 of BUILD)
- STPA (System-Theoretic Process Analysis). Catches losses where every component "works": flawed beliefs
  (cache taken as live, 0 taken as measured), missing feedback, unsafe publish/retry/skip/default actions.
  Apply: `hazard-sweep.md` section 2, including the belief check (process-model variables learned from
  proxies such as exit codes, counts or timestamps are hazard cells). Blind: only as good as the control
  structure drawn; no numbers.
  Sources: STPA Handbook, Leveson and Thomas (2018) https://www.flighttestsafety.org/images/STPA_Handbook.pdf ;
  From Hazard Identification to Controller Design (2025) https://arxiv.org/abs/2502.07974 ;
  Who Analyses the Analyser? Self-Validating LLM Hazard Analysis with Constitutional Meta-STPA (2026) https://arxiv.org/abs/2607.08054
- CAST (causal analysis on STAMP). Catches recurring classes behind individual incidents by clustering on
  wrong belief plus missing feedback. Apply: path B history pass, INCIDENT I3. Blind: retrospective only.
  Source: Introduction to STAMP, STPA and CAST https://ul.com/sis/blog/introduction-to-stamp-stpa-and-cast
- HAZOP guidewords for data flows. Catches omission, duplication, truncation, contamination, partial
  records, reversal, wrong entity/unit/version, timing; the data extensions STALE, WRONG FRAME and WRONG
  SCOPE catch old vintages, convention mismatches and scope reuse. Apply: `hazard-sweep.md` section 1,
  as an exhaustive guideword x parameter grid where every pruned cell carries a written reason, so the
  sweep can be audited. Blind: tedious, weak on emergent multi-flow causes. Sources: HAZOP chapter, Rausand https://ntnu.edu/documents/624876/1277591044/chapt09-hazop.pdf ;
  A Hierarchical HAZOP-Like Safety Analysis for Learning-Enabled Systems (2022) https://arxiv.org/abs/2206.10216 ;
  SCSC Data Safety Guidance https://scsc.uk/r1349
- FMEA with action priority and measured detection. Catches silent critical modes (high S, poor D).
  Apply: D from seeded-fault results, no RPN. Blind: single failures, subjective ratings.
  Sources: AIAG-VDA action priority discussion https://www.pharmaceuticalonline.com/doc/is-it-time-to-say-goodbye-to-fmea-risk-priority-number-rpn-scores-0001 ;
  Towards Quality Management of ML Systems for Medical Applications https://arxiv.org/abs/2210.08881
- Fault tree analysis, minimal cut sets, common cause. Catches single points that defeat every detector.
  Apply: top 3-5 outputs. Blind: static, needs basic events. Source: NUREG-0492 Fault Tree Handbook
  https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr0492/index
- Swiss-cheese layer matrix with independence audit. Catches classes covered by at most one real layer.
  Blind: metaphor, layers are not independent. Sources: Reason, Human error: models and management
  https://pmc.ncbi.nlm.nih.gov/articles/PMC1117770/ ; Perneger, holes in the metaphor https://pmc.ncbi.nlm.nih.gov/articles/PMC1298298
- Pre-mortem. Catches failure stories people know but do not say. Apply: BUILD on new domains. Blind: no
  coverage guarantee. Source: Klein, Performing a Project Premortem https://hbr.org/2007/09/performing-a-project-premortem
- Assurance case with defeaters (eliminative argumentation). Catches checks that pass for the wrong
  reason. Apply: `hazard-sweep.md` section 7. Blind: can become paperwork. Sources: GSN Community Standard
  https://scsc.uk/gsn ; Defeaters and Eliminative Argumentation in Assurance 2.0 https://arxiv.org/abs/2405.15800

## B. Prevention by construction (G0, G3)
- Poka-yoke. Make invalid states unrepresentable (typed units, tri-state, closed enums, mandatory
  provenance, fixed-value counts). Blind: anticipated errors only. Source: Shingo, Zero Quality Control
  https://www.routledge.com/Zero-Quality-Control-Source-Inspection-and-the-Poka-yoke-System/Shingo/p/book/9780915299072
- Data contracts with compatibility modes. Catches producer/consumer breaks; BACKWARD_TRANSITIVE readers.
  Blind: shape, not truth. Sources: Open Data Contract Standard https://github.com/bitol-io/open-data-contract-standard ;
  Schema Registry compatibility https://docs.confluent.io/platform/7.2/schema-registry/avro.html
- Versioned, curated schema with skew checks (TFDV). Catches new or vanished categories and corpus skew
  between the development tenant and new tenants. Blind: stable distributions can hold wrong values.
  Source: Data Validation for Machine Learning https://research.google/pubs/data-validation-for-machine-learning/
- Fail fast, write-audit-publish, error budgets. Catches defaults that hide missing inputs and unaudited
  data reaching consumers. Apply: G3, G6. Sources: Shore, Fail Fast https://martinfowler.com/ieeeSoftware/failFast.pdf ;
  Write-Audit-Publish https://lakefs.io/blog/data-engineering-patterns-write-audit-publish/ ;
  Menzies et al., cost-to-fix revisited https://arxiv.org/abs/1609.04886
- Jidoka / andon with partition quarantine. Stop the affected tenant, document or entity on an
  invariant violation of S >= 7, mark dependents blocked, keep state for diagnosis, never fall back
  silently; a near-zero stop rate on complex new inputs suggests insensitive detectors. Apply:
  `gate-ladder.md` G5. Source: Andon, Lean Enterprise Institute https://www.lean.org/lexicon-terms/andon/
- Declarative data tests at every stage boundary. Completeness, uniqueness, referential integrity,
  conservation; zero rows evaluated is a failure. Sources: Deequ (PVLDB 2018) https://www.vldb.org/pvldb/vol11/p1781-schelter.pdf ;
  dbt unit tests https://docs.getdbt.com/docs/build/unit-tests
- Distribution smell scan (data smells and data linting). Round constants across inputs of different
  size, neighbour or median copies, identical values at distinct keys, single-valued provenance,
  sentinels, numbers as text, mixed units. Cheapest independent path B in AUDIT and a G5 run check.
  Blind: a wrong value with a normal distribution passes. Sources: Data Smells https://arxiv.org/abs/2203.10384 ;
  The Data Linter https://research.google/pubs/the-data-linter-lightweight-automated-sanity-checking-for-ml-data-sets/
- Fellegi-Holt edits and status flags. Cross-field consistency rules, minimal error localization,
  observed/derived/imputed/defaulted flags. Blind: consistent but wrong records pass. Sources: Census
  RR99-01 https://www.census.gov/content/dam/Census/library/working-papers/1999/adrm/rr99-01.pdf ;
  generalized Fellegi-Holt https://www150.statcan.gc.ca/n1/pub/12-001-x/2016001/article/14538/01-eng.htm

## C. Provenance and lineage (G3, G6, INCIDENT I2)
- Record and column lineage (OpenLineage). Catches stale-code artifacts and undeclared consumers.
  Source: OpenLineage data quality facet https://openlineage.io/docs/spec/facets/dataset-facets/data_quality_assertions ;
  Hidden Technical Debt in ML Systems https://proceedings.neurips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf
- Provenance semirings (contributing ids with multiplicity). Catches double counting and exclusive
  buckets fed by one record. Source: Provenance Semirings https://www.cs.ucdavis.edu/~green/papers/pods07.pdf
- Why-not provenance and rejection ledgers. Catches false absence: which stage dropped the expected item.
  Sources: Why Not? (SIGMOD 2009) https://dl.acm.org/doi/10.1145/1559845.1559901 ;
  PUG https://arxiv.org/abs/1808.05752
- Citator-style checks (existence, support, currency, point-specific treatment, scope). Catches real but
  non-supporting or superseded sources. Sources: Hallucination-Free? legal research tools https://arxiv.org/abs/2405.20362 ;
  Updating cases with citators https://library.law.northwestern.edu/cases/updating
- Mandatory source grounding. Every value carries locator and span; mechanical span check. Sources:
  LangExtract https://developers.googleblog.com/en/introducing-langextract-a-gemini-powered-information-extraction-library/

## D. Oracle-free and differential testing (G2)
- Metamorphic testing. Mirror, permutation, partition additivity, duplication, unit scaling, irrelevant
  input, renaming. Blind: a consistent bias passes. Sources: ML Testing survey https://arxiv.org/abs/1906.10742 ;
  MetaCDP https://scholarworks.montana.edu/handle/1/18983 ; Metamorphic Testing of LLMs for NLP https://arxiv.org/abs/2511.02108
- Property-based testing. Round-trip, idempotence, conservation, monotonicity with shrinking. Sources:
  QuickCheck https://www.cs.tufts.edu/comp/150FP/archive/john-hughes/quick.pdf ;
  Property-Based Testing in Practice https://cis.upenn.edu/~bcpierce/papers/icse24-pbt-in-practice ;
  Hypothesis https://joss.theoj.org/papers/10.21105/joss.01891 ;
  Pandera strategies https://pandera.readthedocs.io/en/stable/data_synthesis_strategies.html
- Differential testing and key-level data diff. Old vs new over the corpus by stable key; every diff on
  an expected-change list. Blind: both sides can share a bug. Source: McKeeman, Differential Testing
  for Software https://dblp.org/pid/40/4856
- Shadow versions and A-A tests. Measure the noise floor before calling a diff a regression. Source:
  Google SRE Workbook, Canarying Releases https://sre.google/workbook/canarying-releases/
- Lineage-driven fault injection and chaos. Remove supports of a correct output; expect correct output
  via another support or a loud failure. Sources: LDFI summary https://blog.acolyer.org/2015/03/26/lineage-driven-fault-injection/ ;
  Chaos Engineering https://arxiv.org/abs/1702.05843

## E. Testing the tests (`guard-the-guards.md`)
- Mutation testing and data fault injection. Surviving mutants are blind spots. Sources: Are Mutants a
  Valid Substitute for Real Faults? https://homes.cs.washington.edu/~mernst/pubs/mutation-effectiveness-fse2014.pdf ;
  deadcanary https://pypi.org/project/deadcanary/ ; Mutation-Guided LLM-based Test Generation at Meta
  https://arxiv.org/abs/2501.12862 ; Jenga https://cdn.amazon.science/ed/04/f752caff482788a214dfb7460c43/jenga-a-framework-to-study-the-impact-of-data-errors-on-the-predictions-of-machine-learning-models.pdf ;
  ESA FAQAS mutation thresholds https://indico.esa.int/event/532/contributions/10091/attachments/6386/11033/9.%20ADCSS-PASTORE-ESA-FAQAS-Mutation-V2.pdf
- Assertions mined from fix history (SPADE) and validator alignment (EvalGen). Each prompt or rule fix
  becomes an assertion; checks are scored against human grades; criteria drift. Sources: SPADE
  https://arxiv.org/abs/2401.03038 ; Who Validates the Validators? https://arxiv.org/abs/2404.12272
- Judge TPR/TNR correction and limits. Sources: Judging LLM-as-a-Judge https://arxiv.org/abs/2306.05685 ;
  LLM Evaluators Recognize and Favor Their Own Generations https://arxiv.org/abs/2404.13076 ;
  Limits to scalable evaluation at the frontier https://arxiv.org/abs/2410.13341
- Invariant mining from accepted runs (ranges, linear relations, orderings, records per page, in/out
  ratios per stage). Mined invariants are candidates a human promotes into G3 or G5 with thresholds from
  run history; they inherit bugs in the accepted versions. Apply: `gate-ladder.md` G8. Sources: Daikon
  https://homes.cs.washington.edu/~mernst/pubs/daikon-tool-scp2007.pdf ; Auto-Validate by-History https://arxiv.org/abs/2306.02421

## F. Statistical verification and stopping (G8, `hunt-and-stop.md`)
- Capture-recapture residual estimate. Two independent, sealed paths; Chapman estimator; stopping rule
  with a planted-defect branch when overlap is too small. Blind: correlated reviewers underestimate.
  Sources: Capture-recapture in software inspections after 10 years research
  https://ebse.webspace.durham.ac.uk/ebse-bibliography/capture-recapture-in-software-inspections-after-10-years-research-theory-evaluation-and-application/ ;
  Defect content estimation for two reviewers
  https://portal.research.lu.se/en/publications/defect-content-estimation-for-two-reviewers/ ;
  Briand et al., capture-recapture models https://ehealthinformation.ca/web/default/files/wp-files/isern-98-11.pdf
- Control totals and reconciliation with signed vs absolute deviation; gross-error test before balancing.
  Sources: ACCA, auditing in a computer environment https://www.accaglobal.com/in/en/student/exam-support-resources/fundamentals-exams-study-resources/f8/technical-articles/auditing-computer-environment.html ;
  Data reconciliation and gross error detection https://skoge.folk.ntnu.no/prost/proceedings/focapo_2003/pdffiles/papers/011.pdf
- Prediction-powered inference for totals from imperfect extractors. Sources: PPI https://arxiv.org/abs/2301.09633 ;
  PPI++ https://arxiv.org/abs/2311.01453 ; Cut Costs, Not Accuracy (BARGAIN) https://arxiv.org/abs/2509.02896
- Selective editing (suspicion x impact) for review routing, plus a random stratified audit of the
  unselected items to measure what the routing misses. Apply: `gate-ladder.md` G8. Source:
  Statistics Netherlands discussion paper https://www.cbs.nl/-/media/imported/documents/2012/03/2011-x10-32.pdf
- Source data verification in both directions, risk-based. Source: Impact of SDV on data quality
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4386950/
- Double independent abstraction and blind verification. Agreement is reliability, not validity;
  dependent review misses about half. Sources: Buscemi et al. https://pubmed.ncbi.nlm.nih.gov/16765272/ ;
  Chain-of-Verification https://arxiv.org/abs/2309.11495 ; Lyberg et al. https://www.niss.org/sites/default/files/I%201%20Lyberg_itsew2013.pdf
- Independent check calculation scaled by criticality. Source: CG 300 Technical approval of highway
  structures (clauses on independent checking) https://www.standardsforhighways.co.uk/tses/attachments/17dadcc6-8e01-455d-b93e-c827d280839a
- Stratified gold with never-inspected holdout; fact-level unit tests. Sources: olmOCR 2 and olmOCR-Bench
  https://allenai.org/blog/olmocr-2 ; snapshot testing study https://sdlab.naist.jp/en/post/fujita-icsme2023/

## G. Model-stage specifics (G3, G4, G8)
- Decomposition with explicit gather and resolve steps; position-aware canaries (known facts at the
  start, middle and end of long inputs and across chunk boundaries, recall reported by position and
  length). Apply: `gate-ladder.md` G2, G4 P9, G5. Sources: DocETL
  https://arxiv.org/abs/2410.12189 ; Lost in the Middle https://aclanthology.org/2024.tacl-1.9/
- Calibrated abstention and instability alarms. Sources: Conformal factuality https://arxiv.org/abs/2402.10978 ;
  Semantic entropy https://pmc.ncbi.nlm.nih.gov/articles/PMC11186750
- Correlated errors: agreement is not independence. Sources: Correlated Errors in LLMs https://arxiv.org/abs/2506.07962 ;
  Knight and Leveson https://www.kth.se/social/files/564df871f2765419e306178d/KnightLeveson.pdf
- No intrinsic self-correction; do not ask the extractor to check itself. Source: Large Language Models
  Cannot Self-Correct Reasoning Yet https://arxiv.org/abs/2310.01798
- Format constraints can lower reasoning accuracy; put evidence before the answer field. Source: Let Me
  Speak Freely? https://arxiv.org/abs/2408.02442
- Assert-and-retry with first-attempt failure logging. Source: DSPy Assertions https://arxiv.org/abs/2312.13382

## H. Root-cause localization (INCIDENT)
- Error grouping, Data X-Ray: feature conjunctions that explain errors (template, page type, extractor
  version); one group = one platform fix. Apply: `gate-ladder.md` G8, INCIDENT I2, ST-06.
  Source: https://people.cs.umass.edu/~ameli/projects/dataxray/papers/modf554-Wang.pdf
- Leave-one-group-out localisation, Scorpion: which input subset explains an outlier aggregate; run it
  before grouping when one aggregate deviates. Source: https://dspace.mit.edu/bitstream/1721.1/89076/1/scorpion-vldb13.pdf
- Configuration bisection, BugDoc: swap one logged component at a time between the last good and first
  bad run; the minimal flipping set is the reproduction. Source: https://arxiv.org/abs/2004.06530
- Stage-wise oracle substitution for cascading errors: evaluate each stage on gold and on predicted inputs
  to separate introduction from amplification. Source: Solving the Problem of Cascading Errors
  https://aclanthology.org/W06-1673/
- Operator-level row conservation by stratum (mlinspect). Source: https://par.nsf.gov/biblio/10287318
- Error analysis by open and axial coding with first-failure tracing. Source: Hamel Husain, error analysis
  https://hamel.dev/blog/posts/evals-faq/why-is-error-analysis-so-important-in-llm-evals-and-how-is-it-performed.html
- Production-readiness and data-cascade audits. Sources: The ML Test Score
  https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/ ;
  Data Cascades https://research.google/blog/data-cascades-in-machine-learning/
