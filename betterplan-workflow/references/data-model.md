# Type mapping & conventions

This file holds only the conceptual mapping that the Betterplan MCP does **not** spell out on its own. The MCP describes its tools, fields, and argument types at runtime — rely on those for exact field names, required arguments, and endpoints. For REST endpoints the MCP doesn't cover (e.g. bulk import/export), see `openapi.json` in this same directory. Do not duplicate the API surface here; it would only drift.

What stays here is methodology, not API plumbing: how the building blocks map to `type` strings, how maturity is represented, what counts as content vs metadata, and the bug rule.

## Building block ↔ `type` value

Every building block is one task object, distinguished by `type`:

| Building block | `type` |
|---|---|
| Initiative | `initiative` |
| Epic | `epic` |
| User Story | `story` |
| Project Story | `project` |
| Devteam Story | `dev` |
| Workitem | `workitem` |

Note the non-obvious part: the three story types are distinct `type` values — a User Story is `story`, a Project Story is `project`, a Devteam Story is `dev`.

## Content vs metadata

- **Content** lives in `title` + `description` (Markdown). This is what the create-* skills produce.
- **Metadata / structure** is set as fields on the item, never written into the description: `type`, `parentId` (epic→initiative, story→epic, workitem→story), `releaseId`, `estimation` (Story Points), `tags`, `assignee`, the maturity dates, `completionState`.

## Maturity is expressed through date fields

There is **no single status field**. A Story's maturity is derived from which date fields are set (plus `completionState`):

| Maturity | Set field |
|---|---|
| Idea | none of the below set |
| Draft | `draftDate` |
| Ready | `readyDate` |
| Todo | `todoDate` |
| Doing | `startedDate` |
| Done | `doneDate` |
| Closed | `closedDate` + `completionState = "closed"` |

A new item created without dates is at **Idea**. Initiatives and Epics are structure and normally carry no maturity dates.

**Caveat — a `progress:<level>` tag may also be involved.** A real project export (task created by the app itself, not via bulk import) showed a `progress:idea` tag set on an Initiative, an Epic, and a Story alike, alongside the (unset) date fields. This contradicts "Initiatives/Epics carry no maturity" at the tag level, even though the date-field table above held for that same export. Cause unconfirmed — may be a template-seeding artifact, or the tag may be load-bearing for some views. Until this is investigated further: when bulk-importing (see below), set `progress:idea` (or the matching level) on every task regardless of type, to match observed working state.

**Workitems do not use the `Closed` state.** A Workitem is a lightweight coordination item on the Iteration Board and is complete once `doneDate` is set (the **Done** column). `completionState` stays at its default and is never set to `"closed"` for a Workitem; an obsolete Workitem is deleted rather than closed. The `Closed` row above applies to Stories (and, when explicitly stopped, Initiatives and Epics).

## Tags — namespacing rules

Confirmed directly against a live project (tags visible in project settings but not rendering on the tasks themselves, until the format below was applied):

- **Every general/custom tag must be namespaced `project:<value>`** — exactly one colon, right after the literal `project`, and **no further colon inside `<value>`**. A tag with a stray second colon, or one missing the `project:` prefix entirely, does not reliably render on the task card even though the plain string still shows up wherever raw tag lists are displayed (e.g. project settings).
- `progress:<level>` (see the maturity caveat above) is a **separate, reserved system namespace** — distinct from `project:`. Don't mix the two: system tags are `progress:idea` / `progress:draft` / etc., general tags are always `project:...`.
- **Group by color, not by a second text prefix.** Don't try to build a nested namespace like `project:Aufwand:gering` — that's the "extra colon" mistake. Instead fold the category into the value with a space (`project:Aufwand gering`, `project:Priorität Must`) and give same-category tags visually related colors via `tagDefinitions`.
- **Every tag string used on any task must have a matching entry in `settings.tagDefinitions`** (`{name, color}`, exact string match) or it won't be styled/shown correctly, even though nothing rejects the import. When bulk-importing, collect the full set of distinct tag values used across all tasks and emit one `tagDefinitions` entry per value before writing the payload — don't declare a subset and hope the rest fall back gracefully.

Example from a real import (CSV columns Kategorie / Aufwand / Gewichtung / Priorität turned into tags):
`["progress:idea", "project:Stammdaten", "project:Priorität Must", "project:Aufwand gering", "project:Gewichtung 3"]`

## Bugs

A bug is **not** a separate Story. It is a Workitem (`type: workitem`) with `isBug = true`, whose `parentId` points to the affected Story. `isBug` is set on the Workitem, never on the Story. The backend reopens the parent Story and maintains the bug rollup. See `betterplan-create-workitem`.

## Bulk import (`POST /projects/import`) — gotchas not in the OpenAPI schema

For importing many items at once (e.g. converting a requirements spreadsheet into a Story Map), `POST /projects/import` takes a `ProjectImportRequest` — see `openapi.json` for the exact shape (`title`, `team_id`, `settings`, `tasks[]` as `TaskCreate`, plus optional `releases`/`iterations`/`dependencies`/`discussions`). Hierarchy is built purely from `parentId`: give each task a self-chosen `id` string and reference it as `parentId` on its children (epic → initiative, story → epic, workitem → story).

Two fields the schema marks optional turned out to be required in practice — confirmed by comparing a hand-built import payload against a real working export and reproducing a bug where imported tasks vanished from views after being edited in the app:

- **`displayOrder` must be set on every task**, e.g. `{"storyboard": <n>}`. Every task the app creates through its normal UI flow has this field populated; a bulk-imported task that lacks it can pass validation and render fine right after import, but disappears from views (Story Map / Backlog / Iteration Board) the first time it's edited afterward. Set `<n>` to a sequential index among siblings that share the same `parentId` (use a per-parent counter; root level — i.e. Initiatives — counts as one shared "parent").
- **Set a `progress:idea` tag on every imported task** (see the maturity caveat above) — cheap to add, matches observed working state, and the cost of a stray tag is far lower than the cost of items misbehaving in the UI.
- **Any other tag you add must follow the `project:<value>` namespacing rule** below, and must be registered in `settings.tagDefinitions` — otherwise it silently fails to render on the task.

When in doubt about any other field, look at a real exported project's `tasks[]` as ground truth rather than only trusting the OpenAPI schema — the schema documents what the field *accepts*, not what the app actually *relies on being present*.
