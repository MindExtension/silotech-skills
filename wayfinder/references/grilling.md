# Grilling

Interview the human relentlessly until you reach a shared understanding. Map the space as a **decision
tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled:
the questions you can ask now without guessing at answers you have not heard yet.

Ask the whole frontier in one round. Number each question and give your recommended answer. Then wait
for the human's answers before the next round.

Format a round like this:

```
Q1 - <question title>: <question body, may be several paragraphs, may include options>

Recommendation: <your recommended answer, and why in one line>

---

Q2 - <question title>: <question body>

Recommendation: <your recommended answer>
```

Each round of answers reshapes the tree. Settled decisions push the frontier outward and unblock
questions that depended on them. Recompute the frontier and ask the next round. A question whose answer
depends on another question still open in this round belongs to a **later** round, not this one.

## Facts are your job, decisions are theirs

Finding **facts** is never the human's job. When a question needs a fact from the environment (a file,
a system, a public source, a price, a regulation), go and find it yourself, in a subagent if it takes a
while. Do not block on it: a running search is an unsettled prerequisite, so only the questions
downstream of it wait. Ask the rest of the frontier now.

The **decisions** are the human's. Put each one to them and wait.

## Keep the words sharp

When the human uses a term that is vague or overloaded, propose a precise one and make them choose.
"You said client: do you mean the company that signs, or the person who uses it? Those are different."

When a term contradicts how the same word was used earlier in this effort, say so immediately. Record
the settled meaning in the map's Notes the moment it crystallises, so the next session inherits it
instead of re-litigating it.

Stress-test relationships with concrete scenarios. Invent cases that probe the edges and force the
human to be precise about where one concept ends and the next begins.

## Done

The session is done when the frontier is empty: every branch visited, nothing silently assumed. Do not
act on the result until the human confirms you have reached a shared understanding.
