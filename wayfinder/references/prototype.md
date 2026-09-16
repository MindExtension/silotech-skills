# Prototype

A prototype is a **throwaway artifact that answers a question**. It exists because some questions are
never settled by discussion: the human has to see the thing to know whether it is right.

The question decides the shape. Before building anything, state which question this prototype answers.

## Pick the shape

- **"What should this look like?"** Build two or three **radically different** versions side by side,
  not one polished version. A page, a screen, a one-page offer, a report layout, a slide, an email. The
  point is contrast: differences are what make a human able to choose.
- **"Does this logic hold up?"** Build one runnable, drivable thing that pushes the process through the
  cases that are hard to reason about on paper. A single file the human can open and click through, a
  spreadsheet with the real formulas and a few real rows, a worked example with the actual numbers.
- **"Would this actually work in the real world?"** Build the smallest real instance: one real invoice,
  one real customer record, one real application form filled in with real data.

## Rules

1. **Throwaway from day one, and clearly marked as such.** Name it so no one mistakes it for the real
   thing. Keep it next to the work it is prototyping so the context is obvious.
2. **Trivial to open.** One click, one command, one link. If the human has to set something up to see
   it, the prototype has failed.
3. **No persistence, no polish.** No error handling beyond what makes it runnable, no tests, no
   abstractions, no real data store. The point is to learn something fast.
4. **Surface the state.** After every action, show the full relevant state, so the human sees exactly
   what changed and why.
5. **Capture the answer when done.** Record the verdict and the question it settled on the ticket, and
   link the prototype as an asset. The decision moves forward; the prototype itself stays behind.

## Why this matters

A long plan built entirely out of discussion is a guess. Prototypes are the thing that keeps a
wayfinder map from turning into a large, confident, wrong document: they replace opinion with
reaction to something concrete, at the moment the decision is being made rather than after the work is
built.
