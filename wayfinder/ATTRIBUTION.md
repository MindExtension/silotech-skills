# Attribution

This skill is derived from the `wayfinder` skill in **github.com/mattpocock/skills** by **Matt Pocock**,
published under the MIT License. The original is an engineering planning skill that charts large work as
a map of decision tickets on an issue tracker; it was introduced in the video *"/wayfinder: Nothing is
too big to plan anymore"* (2026-07-30).

What survives from the original is the core idea: a destination, a map of decision tickets, fog of war,
a frontier, and one ticket per session.

What this version adds or changes:

- **Generalised beyond software engineering**, so the same map works for strategy, hiring, launches,
  funding applications, and other non-code planning. Written for a reader who is not a developer.
- **Decision rights on every ticket.** Each ticket names whether the agent or the human may settle it,
  the default being the human, and a ticket the human never actually answered does not count as
  resolved. Without this, a planning agent quietly decides things that spend money or bind the company.
- **Leverage-ordered frontier.** The original takes the first takeable ticket. This version takes the
  one that clears the most fog, weighing how many tickets it unblocks, how expensive it is to get wrong
  late, and whether it can honestly be answered today.
- **An assumption register on the map.** Long plans accumulate unverified beliefs that harden into
  facts. Each is written down with who would know and what breaks if it is wrong, and anything that
  would sink the destination becomes a research ticket instead.
- **Supersede handling.** When a new decision contradicts an old one, the old line is marked superseded
  rather than overwritten, and whatever was built on it is reopened. A map that hides its reversals is
  worse than no map.
- **A session-end pass and a status line**, so the map stays readable by someone who was not in the
  session.
- **Self-contained.** The grilling, prototype, and research methods are bundled as reference files, so
  it does not need the rest of the original collection installed. The original's domain-modeling
  dependency is replaced by a lighter terminology rule inside the grilling reference.
- **Local markdown is the default tracker**, so it works in any folder with no accounts and no setup.
  GitHub Issues stays available for repositories that already work that way.

## Original licence

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR OTHER DEALINGS IN THE SOFTWARE.
```
