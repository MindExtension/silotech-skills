# SiloTech Skills

A small, public collection of [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
built at [SiloTech](https://silotech.xyz) (UAB Silo Tech) and used in real client work. Each skill is a
self-contained folder you can drop into Claude Code or any agent runtime that reads the Agent Skills format.

Skills are shared here as-is, one item per folder, so you can read them, learn from them, and adapt them.

## Skills

| Skill | What it does |
|---|---|
| [`refine`](./refine) | A generalized, domain-agnostic iterative-improvement harness. Turns "make this better" into a disciplined loop: frame the purpose, decompose into independently-improvable units, derive the evaluation lenses that purpose demands, observe the real rendered output, improve every unit in parallel, verify, iterate, and accumulate lessons so it gets better each run. Works on a slide deck, a document, a codebase, or an analysis. |
| [`autonomous-loop`](./autonomous-loop) | A generalized "loop engineering" harness. Turns "just let the agent finish the project on its own" into a robust MISSION goal file: it discovers the project's real verification gates and work queue, draws three live diagrams (the loop, the task-dependency DAG, the data flow), installs safety guardrails (stop-don't-fabricate, no-auto-commit, adversarial verification, hygiene, explicit termination), and self-checks the plan. Run it plan-only to produce an implementation roadmap a team can estimate and execute, or hand the MISSION to an agent to drive to completion. |
| [`launch-readiness`](./launch-readiness) | A multi-agent "does this look live?" review. Fans out 10-15 perspective subagents (placeholder copy, test data, default assets, SEO leftovers, dead links, test-mode payments, raw i18n keys, debug routes, legal gaps, funnel walkthrough) over the codebase and the deployed product in several discovery rounds, adversarially verifies every finding, and writes a stable-numbered action plan the user triages and hands to `autonomous-loop` for fixing. The detector and planner that sits in front of the other two skills. |

## Which one, when

- You have a thing (deck, doc, codebase, analysis) and want it **better** -> `refine`.
- You have a project and want an agent to **drive it to done** (or produce the roadmap for that) -> `autonomous-loop`.
- You have a product that is about to go (or just went) **live** and want to know what still smells unfinished -> `launch-readiness`, then hand its plan to `autonomous-loop`, and polish individual artifacts with `refine`.

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
