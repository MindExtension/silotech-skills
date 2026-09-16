---
name: wayfinder
description: Plan a chunk of work far bigger than one agent session as a living map of decision tickets, then resolve them one per session until the route to the destination is clear. Use when the goal is known only vaguely, the path is foggy, and a single planning conversation would run out of context or collapse into guesswork. Works for engineering, but equally for strategy, hiring, product launches, funding applications, course building, or any ambitious plan. Trigger keywords - wayfinder, chart the map, plan something big, multi-session plan, too big for one session, foggy plan, suplanuok dideli darba, nubrezk zemelapi, per didelis vienai sesijai, strateginis planas.
disable-model-invocation: true
---

# Wayfinder

A loose idea has arrived. It is too big for one session, and the way from here to the **destination**
is wrapped in fog. Wayfinding means finding that way, not charging at the destination.

This skill charts the way as a **map** of **decision tickets**: questions whose resolution is a
decision, not slices of work to execute. Each ticket is resolved in its own session. The map survives
between sessions, so the plan is no longer limited by one context window.

Nothing here is specific to code. The same shape works for a market-entry decision, a hiring round, an
EU funding application, a product launch, a course, or a building project. Only the content changes.

## Plan, don't do

Wayfinder **plans** by default. Each ticket resolves a decision. The map is done when the route is
clear and nothing is left to decide before someone goes and does the thing.

The pull to just start doing the work is usually the signal that you have reached the edge of the map
and it is time to hand off. An effort can override this in its **Notes** and carry execution into the
map, but absent that, produce decisions, not deliverables.

## Decision rights

Every ticket names **who may settle it**, and the default is the human.

- The **agent may decide** only what is reversible, cheap, and commits nobody outside the room: naming,
  ordering, format, which of two equivalent methods to use.
- The **human decides** anything that spends money, binds the organisation, touches people's jobs, goes
  public, or is expensive to undo. On those the agent researches, lays out the options with a
  recommendation, and waits. It never records its own preference as the answer.

Write the decider on the ticket. A resolved ticket whose decider was the human, but whose answer the
human never actually said, is not resolved. Reopen it.

## Refer by name

Every map and ticket has a title. In everything the human reads, refer to it by that title, never by a
bare number or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The number and the
link ride inside the name, they never replace it.

## The map

The map is one file (or one issue, see [Where the map lives](#where-the-map-lives)), and it is the
canonical artifact. Its tickets are its children.

The map is an **index, not a store**. It lists the decisions made and points at the tickets that hold
the detail. A decision lives in exactly one place, its ticket. The map only gists it and links.

Open tickets are **not** listed in the map body. They are found by looking at the tickets themselves.

### The map body

```markdown
# <effort title>

Status: <n> decided · <n> open · <n> patches of fog · destination <not reached | reached>

## Destination

<what reaching the end of this map looks like: the spec, the decision, or the change this effort is
finding its way to. One or two lines. Every session orients to it before choosing a ticket.>

## Notes

<domain; standing preferences for this effort; documents every session should consult; who the human
decision-makers are; which tracker this map uses>

## Decisions so far

<!-- the index: one line per resolved ticket, enough to judge relevance, then open the link for detail -->

- [<resolved ticket title>](link): <one-line gist of the answer>

## Assumptions

<!-- what the map leans on but nobody has verified; see "Assumptions" -->

- <assumption>: <who would know> · <what breaks if it is wrong>

## Not yet specified

<!-- in-scope fog you cannot ticket yet; graduates into tickets as the frontier advances -->

## Out of scope

<!-- work consciously ruled beyond the destination; closed, never graduates -->
```

The status line is the only thing a busy human reads before deciding whether to open the map. Update it
at the end of every session.

### Tickets

Each ticket is a child of the map. Its body is the question, sized to one agent session:

```markdown
# <ticket title>

Type: research | prototype | grilling | task
Decider: human | agent
Status: open | claimed | resolved
Blocked by: <ticket numbers, or nothing>

## Question

<the decision or investigation this ticket resolves>
```

A session **claims** a ticket before any work, so parallel sessions skip it. An open, unclaimed ticket
is takeable.

A ticket is **unblocked** when every ticket blocking it is resolved. The **frontier** is the set of
open, unblocked, unclaimed tickets: the edge of the known. That is the only place work can start.

The answer is not part of the body. It is recorded on resolution. Anything produced while resolving a
ticket (a document, a prototype, a quote, a spreadsheet) is linked from the ticket, not pasted into it.

## Ticket types

Every ticket is either **HITL** (human in the loop, worked with a human who speaks for themselves) or
**AFK** (driven by the agent alone). A HITL ticket only resolves through that live exchange. The agent
never stands in for the human's side of it. An agent that answers its own grilling questions has broken
this rule and the ticket is not resolved.

- **Research** (AFK): reading documentation, regulations, third-party sources, market data, or internal
  knowledge bases to surface a fact a decision waits on. Run it in a subagent, following
  [references/research.md](references/research.md). Use when the missing piece is knowledge, not opinion.
- **Prototype** (HITL): raise the fidelity of the discussion by making something cheap, rough, and
  concrete to react to. A one-page draft, a sample report, a mock offer, a spreadsheet, a screen, a
  stub. Follow [references/prototype.md](references/prototype.md). Use when the real question is
  "how should this look or behave", which no amount of discussion settles on paper.
- **Grilling** (HITL): conversation. The default case. Follow
  [references/grilling.md](references/grilling.md).
- **Task** (HITL or AFK): manual work that must happen before a **decision** can be made. Nothing to
  decide, prototype, or research, but the discussion is blocked until it is done. Signing up for a
  service so its terms can be judged, requesting an offer, getting access, moving data so its shape is
  visible. This is the one type that does rather than decides, and it earns its place by unblocking a
  decision, not by delivering the destination. The agent does it alone where it can; otherwise it hands
  the human a precise checklist. The answer records what was done and any facts later tickets depend on.

## Fog of war

The map is **deliberately incomplete**. Do not chart what you cannot yet see.

Beyond the live tickets lies the fog: decisions and investigations you can tell are coming but cannot
pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it and
graduates whatever is now specifiable into fresh tickets, one at a time, until the route is clear and
no tickets remain.

The **Not yet specified** section is where that dim view is written down: the suspected question, the
area to revisit. Everything there is in scope, it is just not sharp enough to ticket yet.

**Fog or ticket?** The test is whether you can state the question precisely now, not whether you can
answer it now.

- **Ticket** when the question is already sharp, even if it is blocked and you cannot act on it yet.
- **Not yet specified** when you cannot phrase it that sharply. Do not pre-slice the fog into
  ticket-sized pieces: one patch may graduate into several tickets, or none.

An empty fog section early in a large effort is a warning sign, not an achievement. It usually means
the map is charting what is comfortable to see rather than what the destination actually requires.

## Which ticket next

Not the first one on the list. Take the ticket that **clears the most fog per session**, judged in this
order:

1. **Leverage**: how many blocked tickets and fog patches does resolving it open up? A ticket that
   unblocks five others beats one that unblocks none.
2. **Irreversibility**: how expensive is it to get this wrong and find out late? Decisions that are
   hard to undo, or that everything else is built on, come early, while changing course is still cheap.
3. **Answerability**: can it genuinely be settled now, with the people and facts available today?

When you choose, say in one line why that ticket and not another. If two are equal, take the lower
number.

## Assumptions

A long plan quietly accumulates things nobody checked. Write each one in the map's **Assumptions**
section the moment it is used: the assumption, who would actually know, and what breaks if it is wrong.

The test: if the assumption being wrong would sink the destination, it is not an assumption. It is a
research ticket, and it belongs on the frontier now.

When a ticket resolves an assumption, delete it from the section and record it as a decision. The
section is a debt list, and it should shrink as the map advances.

## When a new decision contradicts an old one

Never silently overwrite. In **Decisions so far**, mark the old line as superseded and link the ticket
that replaced it, so the record shows the route actually walked, including where it turned.

Then check what was built on the old answer. Any ticket that depended on it is reopened or replaced,
and any downstream work already done is listed on the new ticket as what the change costs. A map that
hides its reversals is worth less than no map, because everyone downstream keeps trusting a decision
that no longer holds.

## Out of scope

Fog only ever gathers toward the destination. The destination fixes the scope, so work beyond it is
out of scope: it is not fog, and it does not belong in **Not yet specified**.

When a ticket turns out to sit past the destination, close it and leave one line in **Out of scope**:
the gist plus why it is out. It stays out of **Decisions so far**, which records only the route actually
walked. Out-of-scope work never graduates. It returns only if the destination is redrawn, and then as a
fresh effort, not a resumption.

## Where the map lives

Default: **local markdown in the working repository**, which needs no tooling and no accounts.

```
wayfinder/<effort-slug>/
├── map.md                       the map body above
└── tickets/
    ├── 01-<slug>.md
    └── 02-<slug>.md
```

Full conventions: [references/tracker-local.md](references/tracker-local.md).

If the repository already runs its work on **GitHub Issues** and the human wants the map there, use
[references/tracker-github.md](references/tracker-github.md) instead: the map is an issue labelled
`wayfinder:map`, tickets are sub-issues, and blocking uses the tracker's native dependency
relationship so the frontier is visible in the tracker's own UI. Ask once which one to use, then record
the answer in the map's Notes so later sessions do not ask again.

## Invocation

Two modes. Either way, **never resolve more than one ticket per session**, except research tickets,
which run in parallel subagents.

### Mode 1: chart the map

The user arrives with a loose idea.

1. **Name the destination.** Grill the user ([references/grilling.md](references/grilling.md)) to pin
   down what this map is finding its way to: a spec, a decision, a change made in place. The
   destination fixes the scope, so it is settled first.
2. **Map the frontier.** Grill again, **breadth-first** this time: fan out across the whole space
   rather than deep on one thread, surfacing the open decisions and the first steps takeable now.
   **If this surfaces no fog**, the route is already clear and the whole journey fits one session. Say
   so, do not build a map, and ask the user how they want to proceed.
3. **Create the map** with Destination and Notes filled in, Decisions so far empty, known assumptions
   written down, and the fog sketched into **Not yet specified**.
4. **Create the tickets you can specify now**, each with its decider, then wire the blocking
   relationships in a **second pass** (tickets need numbers before they can reference each other).
   Wiring sorts them into the frontier and the blocked. Everything you cannot yet specify stays in the
   fog.
5. **Fire the research subagents** for every research ticket just created, so they resolve in parallel
   while the human does something else.
6. **Stop.** Charting is one session's work. It resolves nothing by hand.

Close the session by telling the human, in plain language, what the destination is, which tickets are
takeable right now, which one you would take first and why, and what is still in fog.

### Mode 2: work through the map

The user invokes with a map, and optionally a ticket. Without a ticket, you pick the next one, not the
user.

1. Load the **map**, the low-resolution view. Do not read every ticket body.
2. Choose the ticket. If the user named one, use it. Otherwise apply
   [Which ticket next](#which-ticket-next) and say why. **Claim it** before any work.
3. Resolve it, using the type's method and respecting its decider. **Zoom as needed**: open the full
   body of any related or resolved ticket on demand. Consult whatever the map's Notes name.
4. Record the resolution: write the answer on the ticket, mark it resolved, and append a one-line gist
   plus link to the map's **Decisions so far**.
5. Update the frontier: add newly surfaced tickets (create, then wire), graduate any fog the answer has
   made specifiable and clear it from **Not yet specified**, retire any assumption the answer settled,
   rule out of scope anything the answer pushed past the destination, mark superseded anything the
   answer contradicts, and update or delete tickets the decision has invalidated.

### Before you end either session

A short pass, every time:

- The status line matches reality.
- Every decision made this session is in **Decisions so far**, one line, linked.
- Nothing that belongs in a ticket is sitting only in the chat.
- Every new ticket has a type, a decider, and its blocking wired.
- Assumptions used this session are written down, and settled ones are removed.

Then tell the human what moved: the decision made, and what is takeable now that was not before.

## When the map is complete

The map is a dense record of decisions, not a document anyone wants to read end to end. Once no tickets
remain, turn it into whatever the destination asked for: a specification, a proposal, a plan of
execution, a set of implementation tickets. Every claim in that document links back to the ticket that
settled it, so the primary source is one click away and never has to be trusted from memory.

The map is then finished, not maintained. If reality changes enough to matter, that is a new
destination and a new map, not an edit to this one.

## When not to use this

If the work can be planned and completed in a single session, plan it in a single session. If you
already know the route to the destination, walk it. Wayfinder earns its overhead only when there is real
fog: when you genuinely do not know what the steps are, and you need to start moving to find out.

## Attribution

The mapping idea comes from the MIT-licensed `wayfinder` skill by Matt Pocock
(github.com/mattpocock/skills). This version is a rewrite for non-engineering planning, with decision
rights, leverage-ordered frontier, an assumption register, and supersede handling added. See
[ATTRIBUTION.md](ATTRIBUTION.md).
