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

## Install

Works with **pi**, Claude Code, Codex, Cursor, and [70+ other agents](https://www.npmjs.com/package/skills).

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

## License

MIT
