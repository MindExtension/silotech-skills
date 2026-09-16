# Research

Run research in a **background subagent**, so the human keeps working while it reads.

The subagent's job:

1. Investigate the question against **primary sources**: official documentation, the law or regulation
   itself, the vendor's own pricing page, the source code, the signed contract, the actual dataset.
   Never a secondary write-up of any of those. Follow every claim back to the source that owns it.
2. Separate **what the sources say** from **what it concludes**. A conclusion with no source behind it
   must be labelled as an inference, not a fact.
3. Write the findings to a single Markdown file, citing the source of each claim, with the date it was
   checked. Put it where this repository already keeps such notes; if there is no convention, put it
   beside the map and say where.
4. Report back with the short version: the answer to the question, the confidence, and what remains
   unknown.

Say explicitly when a question could not be answered. An empty result is a real finding and often
becomes its own ticket. A plausible invented answer is worse than no answer, because the whole map will
be built on it.
