# Betterplan Skills

Official skill registry for [Betterplan](https://yourbetterplan.com) — agile project planning for small teams.

## Skills

| Skill | Purpose |
|-------|---------|
| `betterplan-workflow` | Classifies work into the correct building block; holds shared conventions |
| `betterplan-create-initiative` | Creates an **Initiative** (business goal) |
| `betterplan-create-epic` | Creates an **Epic** (step in the process) |
| `betterplan-create-story` | Creates a **Story** (user, project, or devteam story) |
| `betterplan-create-workitem` | Creates **Workitems** or bug entries for a Story |
| `betterplan-implement-story` | Implements a Story autonomously via an agent — proposes Workitems, creates them in the Iteration Board, implements with one commit per Workitem, and tracks progress in real time |
| `betterplan-transform` | Transforms raw project material (PDF, DOCX, XLSX, CSV, …) into agent-friendly Markdown under `.betterplan/references/` |
| `betterplan-goal` | Defines the **goal** of the endeavor and records it in `.betterplan/GOAL.md` — runs between transform and extract |
| `betterplan-extract` | Extracts requirements, constraints, risks and open questions from the transformed references |

## Install

### Claude Code (Plugin Marketplace)

```shell
/plugin marketplace add yourbetterplan/skills
/plugin install betterplan-workflow@betterplan-skills
```

Install the other skills the same way — `betterplan-create-initiative`,
`betterplan-create-epic`, `betterplan-create-story`, `betterplan-create-workitem`,
`betterplan-implement-story`, `betterplan-transform`, `betterplan-goal`,
`betterplan-extract`.
Browse everything with `/plugin` and pull in updates with
`/plugin marketplace update betterplan-skills`.

`betterplan-transform` ships a Python script. See its SKILL.md for the one-time
`uv sync` setup.

### Other agents

Works with **pi**, Codex, Cursor, and [70+ other agents](https://www.npmjs.com/package/skills).

```bash
# Install all skills (project-local)
npx skills@latest add yourbetterplan/skills

# Or globally
npx skills@latest add yourbetterplan/skills -g

# Install only specific skills
npx skills@latest add yourbetterplan/skills --skill betterplan-workflow

# Preview without installing
npx skills@latest add yourbetterplan/skills --list
```

**With pi directly:**
```bash
pi install git:github.com/yourbetterplan/skills
```

## Third-party skills

`.agents/skills/` holds skills authored by others — `domain-modeling`,
`grill-me`, `grill-with-docs` and `grilling`, from
[mattpocock/skills](https://github.com/mattpocock/skills). They are not part of
the `betterplan-*` registry and no Betterplan skill depends on them. See
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) for licensing, and do not edit
the vendored copies — re-running the `skills` CLI overwrites them.

## License

The `betterplan-*` skills in this repository are MIT — see [LICENSE](LICENSE).
Vendored third-party skills carry their own license; see
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
