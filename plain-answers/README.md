# plain-answers

A plain-language output setup for AI coding agents. Fixes the two most common complaints about
frontier-model replies: jargon-dense wording and wall-of-text answers to simple questions.

It has one core piece and two companion skills:

- **`output-style.md`** - a Claude Code output style. Lead with the answer, short sentences,
  no unexplained acronyms, length matched to the question.
- [`bro`](../bro) - restate the last answer in plain human language, zero jargon.
- [`quick`](../quick) - compress the last answer into N key takeaways (default 3).

## Why an output style and not CLAUDE.md

An output style is written into the core system prompt of the session, and Claude Code re-injects
"stick to your output style" reminders mid-session. A rule in CLAUDE.md is loaded once at the top and
fades as the context grows. Same text, much better adherence.

The wall-of-text fix deliberately lives in the `bro` and `quick` skills, not in the style itself:
long answers are sometimes exactly what you need (production code, specs), so you shorten on demand
instead of capping everything.

## Install (Claude Code)

```bash
mkdir -p ~/.claude/output-styles ~/.claude/skills
cp plain-answers/output-style.md ~/.claude/output-styles/plain-answers.md
cp -R bro quick ~/.claude/skills/
```

Then activate the style: run `/config` in Claude Code, pick **Output style** -> **Plain Answers**,
or add `"outputStyle": "Plain Answers"` to `~/.claude/settings.json`. New sessions pick it up.

## Install (Codex)

Codex has no output-style mechanism, so the same rules go into your global `AGENTS.md`
(`~/.codex/AGENTS.md`). Append this block:

```markdown
## Answer style (plain language, no jargon walls)

How to talk to the user (engineering rigor unchanged):

- First sentence = the answer or the outcome. Explanation after, only as much as needed.
- Match length to the question: a simple question gets a short answer, not an essay.
- Short sentences, one idea per sentence, common words. No unexplained acronyms:
  if a technical term is needed, add a short plain gloss in parentheses at first mention.
- Concrete over abstract: name the file, the number, the command.

Quick commands (mirror of the Claude Code /bro and /quick skills):

- User writes "bro": restate your last answer in plain human language, no jargon,
  a third of the length or less, keeping every decision and number that mattered.
- User writes "quick" or "quick N": give the N (default 3) most important takeaways
  from your last answer as a numbered list, one sentence each, most important first.
  If your answer asked the user a question, that is always number 1. Nothing after the list.
```

## Tune it

The style is a starting point, not a doctrine. If you work in a non-English language, add your
language's terminology rules to the style file (which words replace which English tech tokens).
If you want it gentler or stricter, edit the style file - that is the whole point of it being yours.
