# Playbook Definition format

This is the compiler's input contract. `compile.mjs` enforces it, so this file
and the validator must change together.

```
<playbook-slug>/
├── playbook.yml        # metadata
├── storymap.yml        # the whole Story Map, one file
├── references/         # transformed source material (Markdown)
│   ├── 01-standards.md
│   └── 02-regulation.md
└── output/
    └── <playbook-slug>.json    # generated — never hand-edited
```

## `playbook.yml`

```yaml
title: Eine GmbH gründen          # becomes the Template's title
version: 1.0.0                    # Playbook revision; bump by hand
language: de                      # language of the content, not of this file
icon: rocket                      # Template picker icon — see the caveat below
description: >
  Führt von der Geschäftsidee bis zum Handelsregistereintrag.

initiativePattern: phases         # phases | goals
titleStyle: outcome               # outcome | activity

tags:                             # optional: colors for the tags used in storymap.yml
  - name: "project:Organisation"
    color: "#5B8DEF"
```

`title`, `version`, `language`, `description` and `icon` are required.
`initiativePattern` and `titleStyle` record the authoring conventions so a later
revision stays consistent; the compiler does not read them.

> **`icon` is unverified.** `TemplateMetadata.icon` is an undocumented free-form
> string in the API spec, and the only example given anywhere is `"rocket"`.
> `GET /templates` needs a bearer token, so the real vocabulary has not been
> enumerated. Whatever you put here passes the compiler and may not render.

## `storymap.yml`

Type comes from the **key name**, not from a `type:` field and not from nesting
depth:

| Key | Type emitted |
|---|---|
| `initiatives:` (root) | `initiative` |
| `epics:` (under an initiative) | `epic` |
| `stories:` (under an epic) | `story` — a User Story |
| `stories:` (root) | `project` or `dev`, from an explicit `type:` |
| `workitems:` (under any story) | `workitem` |

```yaml
initiatives:
  - title: Vorbereitung & Entscheidung
    description: >
      Die Idee ist geprüft und die Rechtsform steht fest.
    epics:
      - title: Rechtsform wählen
        description: >
          Legt Haftung, Stammkapital und Buchführungspflichten fest.
        stories:
          - title: Rechtsform GmbH gewählt und begründet
            estimation: 5
            tags: ["project:Organisation"]
            description: |
              **Als** Gründerin **will ich** die Rechtsform festlegen,
              **damit** Haftung und Kapitalbedarf geklärt sind.

              ## Kontext
              § 5 GmbHG — Stammkapital mindestens 25.000 €.

              ## Akzeptanzkriterien
              - [ ] Entscheidung dokumentiert
            workitems:
              - title: Stammkapital festlegen

stories:                      # root-level, cross-cutting — never User Stories
  - type: project
    title: Projektablage aufgesetzt
    workitems:
      - title: Ordnerstruktur anlegen
```

The root `stories:` key **never** contains User Stories. A User Story needs an
Epic, so it can only appear under one; `type:` there is mandatory and must be
`project` or `dev`.

### Rules the compiler enforces

- Every node needs a non-empty `title`.
- `type:` is allowed **only** on root-level `stories:` entries, and only as `project` or `dev`. Anywhere else it is an error — the key name already decided the type.
- `estimation` is allowed only on a User Story, and only from the scale `0, 1, 2, 3, 5, 8, 13, 20, 40, 60, 100`. Only a User Story counts towards scope and velocity.
- Tags must match `project:<value>` with exactly one colon. `progress:*` tags are refused — see below.
- Every tag used must have a `tagDefinitions` entry, which the compiler generates from `playbook.yml`'s `tags:` (falling back to a default color, with a warning).

### What the compiler generates, and why you must not write it

- **`id`** — a fresh UUID per task, with `parentId` wired from the nesting. The import regenerates UUIDs and remaps references; a non-UUID correlation key is undocumented and untested.
- **`displayOrder`** — `{"storyboard": <n>}`, a sequential index among siblings sharing a parent. Initiatives and root-level stories share one counter, because the root counts as a single shared parent. A task without one has been seen to vanish from views the first time it is edited.
- **`progress:*` tags** — deliberately **not** emitted. Omit the tag and the server picks the starting phase per type: `progress:todo` for a Workitem, `progress:idea` for everything else. That is exactly what a fresh Playbook wants, and hard-coding `progress:idea` everywhere would put every Workitem in the wrong column.
- **`metadata`** — `{description, icon, taskCount}` for the Template picker. `taskCount` is counted, not declared.

### What a Playbook never carries

No maturity dates, no `completionState`, no `assignee`, no `releaseId`, no
`isBug`. A Playbook is a starting point; lead-time stamps describe work that
already happened. See `betterplan-workflow/references/data-model.md`.
