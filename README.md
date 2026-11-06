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
| `betterplan-build-playbook` | Authors a **Playbook** — a reusable Story Map for a repeatable process — from reference material and an expert interview |
| `betterplan-compile-playbook` | Compiles a Playbook Definition into an importable **Template** and validates it against the live API schema |

## Install

### Claude Code (Plugin Marketplace)

```shell
/plugin marketplace add yourbetterplan/skills
/plugin install betterplan-workflow@betterplan-skills
```

Install the other skills the same way — `betterplan-create-initiative`,
`betterplan-create-epic`, `betterplan-create-story`, `betterplan-create-workitem`,
`betterplan-implement-story`, `betterplan-build-playbook`, `betterplan-compile-playbook`.
Browse everything with `/plugin` and pull in updates with
`/plugin marketplace update betterplan-skills`.

`betterplan-compile-playbook` ships a Node script. Run `npm install` at the repo
root once before using it.

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

The `betterplan-*` skills in this repository are MIT. Vendored third-party
skills carry their own license; see
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
