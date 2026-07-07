# SiloTech Skills

A small, public collection of [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
built at [SiloTech](https://silotech.xyz) (UAB Silo Tech) and used in real client work. Each skill is a
self-contained folder you can drop into Claude Code or any agent runtime that reads the Agent Skills format.

Skills are shared here as-is, one item per folder, so you can read them, learn from them, and adapt them.

## Skills

| Skill | What it does |
|---|---|
| [`refine`](./refine) | A generalized, domain-agnostic iterative-improvement harness. Turns "make this better" into a disciplined loop: frame the purpose, decompose into independently-improvable units, derive the evaluation lenses that purpose demands, observe the real rendered output, improve every unit in parallel, verify, iterate, and accumulate lessons so it gets better each run. Works on a slide deck, a document, a codebase, or an analysis. |

## The `refine` super-prompt

`refine` is a full skill (an orchestrator plus a parallel workflow and a growing lessons log), but its
core is a single self-contained prompt that runs the whole loop with or without a workflow engine. It is
the distilled synthesis of five well-studied patterns:

- **Self-Refine** (Madaan et al., 2023) - generate, critique, refine, iterate on the model's own feedback.
- **Evaluator-optimizer + orchestrator-workers + parallelization** (Anthropic, *Building Effective Agents*).
- **Reflexion** (Shinn et al., 2023) - an episodic memory of past mistakes fed back in as verbal rules.
- **LLM-as-judge, multi-perspective rubric panels** - lenses derived from the artifact's purpose.
- **Design-QA field lessons** - judge the rendered reality, not the source; one writer per unit; harvest the lesson before the re-pass.

Read it in [`refine/references/super-prompt.md`](./refine/references/super-prompt.md).

## Install

Copy a skill folder into your skills directory:

```bash
# user-level (all projects)
cp -R refine ~/.claude/skills/refine

# or project-level
cp -R refine /path/to/project/.claude/skills/refine
```

Claude Code discovers it automatically. Invoke it by intent ("refine this deck", "review and improve
everything") or by name.

## License

[MIT](./LICENSE). Use it, adapt it, ship it.
