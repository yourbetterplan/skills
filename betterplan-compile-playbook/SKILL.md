---
name: betterplan-compile-playbook
description: >
  Compiles a Playbook Definition into an importable Betterplan Template and
  validates it against the live API schema. Use it when the user says "compile
  the playbook", "generate the template", "validate the story map", or after
  editing a playbook's storymap.yml. Run it as often as you like — it is
  deterministic and overwrites its own output.
metadata:
  version: "0.1.0"
---

# Compile a Playbook

Turns a **Playbook Definition** (authored YAML, see `betterplan-build-playbook`)
into the JSON Betterplan loads as a project **Template**, and refuses to emit
anything the API would reject.

This is the mechanical half of playbook work. It holds no interview, no
judgement, and no conventions — only the input contract and the validator.

## Run it

```bash
node betterplan-compile-playbook/scripts/compile.mjs <playbook-dir> [--team <id>]
```

| Flag | Meaning |
|---|---|
| `--team <id>` | Writes `team_id` into the payload. Required by the API at import time (**400** without it), optional at compile time. |
| `--spec <url\|path>` | Schema to validate against. Defaults to `https://app.yourbetterplan.com/api/openapi.json`. Pass a local copy to work offline. |
| `--out <file>` | Output path. Defaults to `<playbook-dir>/output/<slug>.json`. |

Needs `ajv` and `yaml` — `npm install` at the repo root.

Success looks like:

```
✓ 11 tasks, valid against ProjectImportRequest (spec 14.0.1)
  …/gmbh-gruenden/output/gmbh-gruenden.json
```

Failure lists every problem at once, each with its path in the YAML, and writes
nothing. Fix the YAML and re-run — never patch the JSON.

## What it checks

Two layers, in order. The compiler's own rules run first because their messages
point at the YAML; schema errors point at the generated payload and are harder to
read back.

**The Playbook Definition contract** — every node has a title; `type:` appears
only on root-level stories and only as `project`/`dev`; `estimation` only on User
Stories and only on the scale; tags match `project:<value>` with one colon;
`progress:*` tags are refused; nothing that the compiler generates is
hand-written. Full list in `references/playbook-format.md`.

**The live API schema** — the assembled payload is validated against
`components.schemas.ProjectImportRequest` fetched from the running API. The spec
is the authority on shapes and this skill does not restate it. A vendored copy of
it once drifted eleven major versions in this repo; don't reintroduce one.

## Handing the result over

The skill stops at the file. Importing is the user's step:

```
POST /projects/import
```

`team_id` is required in the body (**400** without it) and the caller must be a
member of that team (**403** otherwise). Every UUID in the payload is regenerated
on import and every reference remapped, so importing the same template twice
gives two independent projects.

Do **not** follow `GET /templates/{template_id}`'s own description, which points
at `POST /projects/{project_id}/import` — that route does not exist.

## Known-unverified

Three things could not be checked without a bearer token. The skill works around
each; say so rather than implying the output is fully proven.

- **`icon`** is an undocumented free string in `TemplateMetadata`; `"rocket"` is the only example in existence. Whatever the Playbook declares passes the compiler and may not render.
- **UUID ids** are emitted because the import documents regenerating *UUIDs*. Whether a slug would survive the remapping is untested; the older advice in this repo recommended slugs and predates the current import.
- **`displayOrder`** is emitted on every task on the strength of an observed bug where tasks lacking it vanished from views after being edited. Whether that still reproduces is unknown; emitting it costs nothing.

## Related

| Skill | Relationship |
|---|---|
| `betterplan-build-playbook` | Authors the Playbook Definition this skill consumes |
| `betterplan-workflow` | `references/data-model.md` — what the building blocks mean, how maturity is stored, the tag rules |

`docs/adr/0001-playbook-compiles-to-template.md` records why a Playbook compiles
to a Template rather than being authored as one.
