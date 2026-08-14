# Betterplan Skills

Official skill registry for [Betterplan](https://yourbetterplan.com) — agile project planning for small teams.

## What is this?

This repository contains skills specific to the Betterplan workflow:

| Skill                          | Purpose                                                                  |
| ------------------------------ | ------------------------------------------------------------------------ |
| `betterplan-workflow`          | Classifies work into the correct building blocks; holds shared conventions |
| `betterplan-create-initiative` | Creates an **Initiative** (business goal)                                |
| `betterplan-create-epic`       | Creates an **Epic** (step in the process)                                |
| `betterplan-create-story`      | Creates a **Story** (user, project, or devteam story)                      |
| `betterplan-create-workitem`   | Creates **Workitems** or bug entries for a Story                           |

## Install into your agent

### Via `skills` CLI (recommended)

The [`skills`](https://www.npmjs.com/package/skills) package works with **pi**, Claude Code, Codex, Cursor, and many other agents.

**GitHub** (shorthand):
```bash
npx skills@latest add yourbetterplan/skills
```

**Install only a specific skill** (custom path inside the repo):
```bash
npx skills@latest add https://github.com/yourbetterplan/skills/tree/main/betterplan-workflow
```

**Options:**
```bash
# Install globally instead of project-local
npx skills@latest add yourbetterplan/skills -g

# Install only specific skills
npx skills@latest add yourbetterplan/skills --skill betterplan-workflow --skill betterplan-create-story

# List what would be installed without installing
npx skills@latest add yourbetterplan/skills --list
```

### Via `pi` directly

If you use **pi**, you can also install this repository as a package:

```bash
# GitHub shorthand
pi install git:github.com/yourbetterplan/skills

# SSH
pi install git:git@github.com:yourbetterplan/skills.git
```

## Manage this registry locally

```bash
# List all skills registered in this repo
npx skills list

# Add a new skill (copies the folder into the repo and registers it in the manifest)
npx skills add ~/path/to/new-skill

# Remove a skill (deletes the folder and removes the manifest entry)
npx skills remove betterplan-create-epic
```

## Repository Structure

```
.
├── skills.json              # Central manifest of all skills
├── package.json             # NPM metadata & CLI binaries
├── bin/skills-cli.js        # CLI tool (list / add / remove)
├── README.md
├── betterplan-workflow/
│   ├── SKILL.md
│   └── references/
├── betterplan-create-initiative/
│   └── SKILL.md
├── betterplan-create-epic/
│   └── SKILL.md
├── betterplan-create-story/
│   ├── SKILL.md
│   └── references/
└── betterplan-create-workitem/
    └── SKILL.md
```

## Manifest (`skills.json`)

Every skill is registered in the manifest:

```json
{
  "id": "betterplan-create-epic",
  "name": "betterplan-create-epic",
  "path": "betterplan-create-epic",
  "version": "0.1.0",
  "description": "..."
}
```

- `id` — unique skill name (must match the `name` field in `SKILL.md`)
- `path` — folder name in the repository
- `version` — semantic version

## Conventions for New Skills

1. **Folder names** must be prefixed with `betterplan-` (e.g. `betterplan-my-skill`).
2. Every skill folder must contain at least a `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: betterplan-my-skill
   description: >
     Short description of when this skill is used.
   metadata:
     version: "0.1.0"
   ---
   ```
3. Cross-references to other skills use the full name in backticks:  
   ``Use `betterplan-workflow` for classification.``
4. After creating a new skill folder:  
   `npx skills add ./betterplan-my-skill`

## Development

The CLI tool is a simple Node.js script with no external dependencies:

```bash
node bin/skills-cli.js list
node bin/skills-cli.js add ./path/to/skill
node bin/skills-cli.js remove betterplan-create-epic
```

## License

MIT
