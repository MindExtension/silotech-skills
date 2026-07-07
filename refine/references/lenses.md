# Deriving evaluation lenses from purpose

Lenses are the perspectives a great practitioner applies when judging quality. They come from the
artifact's PURPOSE and AUDIENCE, not from a fixed list. Pick 3 to 6, write them as concrete pass/fail
checks, and have every reviewer score against all of them. When a domain skill already ships a rubric,
use it (for SiloTech decks: `silotech-presentation-generator/references/design-review-rubric.md`).

## How to derive

1. State the purpose in one line ("persuade a non-technical board", "let a new dev onboard", "give an
   analyst a defensible number").
2. Ask: for THIS purpose and audience, what does an expert check first? What makes it fail in the real
   world? What would a skeptic attack?
3. Turn each into a lens with concrete checks, not vibes. "Hierarchy: one clear focal point per slide"
   beats "looks good".
4. Include at least one lens for the failure mode this artifact is prone to (empty space for decks,
   silent wrong numbers for analysis, hidden coupling for code).

## Example lens sets

**Presentation / deck** (purpose: land a message with an audience)
- Space and whitespace: no stretched blocks with empty bottoms; 65 to 75 percent fill.
- Typography scale: readable at projection size; clear hierarchy.
- Layout and alignment: grid, balance, consistent rhythm.
- Visual hierarchy: one focal point per slide.
- Narrative order: context, problem, approach, proof, action.
- Engagement: each slide earns its place; sparse slides get tasteful scaffolding, never invented facts.

**Document / report** (purpose: inform or persuade a reader)
- Clarity: one idea per paragraph, plain language, no wall of text.
- Structure: title, lead, logical flow, scannable headings.
- Accuracy: claims are supported; numbers and names are right.
- Audience fit: right depth and jargon for the reader.
- Actionability: the reader knows what to do or conclude.
- Concision: nothing that does not earn its place.

**Code / module** (purpose: correct, maintainable behavior)
- Correctness: does what it should, edge cases handled.
- Clarity: readable, well-named, matches surrounding style.
- Simplicity: no needless abstraction or duplication.
- Safety: input validation, error handling, no injection or leak.
- Performance: no obvious waste in hot paths.
- Tests: behavior is verified; failure modes covered.

**Data / analysis** (purpose: a decision-grade result)
- Correctness of method: right computation for the question.
- Data integrity: sources, joins, filters do not silently drop or double-count.
- Robustness: sensitivity to assumptions stated; ranges not false precision.
- Clarity of result: the number and its caveats are legible.
- Reproducibility: someone else can rerun and get the same.
- Adversarial check: what would refute this?

Adapt, do not copy. The point is to reason from purpose to the perspectives that matter here.
