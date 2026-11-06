# Type mapping & conventions

**The API spec is the authority on shapes:** <https://app.yourbetterplan.com/api/openapi.json>.
Fetch it when you need field names, required arguments, enums or endpoints. The
MCP likewise describes its own tools at runtime. Nothing about the API surface is
restated here — a vendored copy of the spec used to live in this directory and
drifted eleven major versions behind before anyone noticed.

What stays here is **meaning**, which no schema can carry: how the building
blocks map to `type` strings, what is content and what is metadata, how the
hierarchy works, how maturity is actually stored, the tag namespacing rules, and
the bug rule.

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

The spec gives these as a bare `TaskType` enum with no explanation. Note the
non-obvious part: the three story types are distinct `type` values — a User Story
is `story`, a Project Story is `project`, a Devteam Story is `dev`.

Only a User Story carries an estimate that counts towards scope and velocity.

## Content vs metadata

- **Content** lives in `title` + `description` (Markdown). This is what the create-* skills produce.
- **Metadata / structure** is set as fields on the item, never written into the description: `type`, `parentId`, `releaseId`, `estimation`, `tags`, `assignee`, the lead-time dates, `completionState`.

## The hierarchy

| Type | Parent |
|---|---|
| Initiative (`initiative`) | none — sits at the root |
| Epic (`epic`) | an Initiative |
| User Story (`story`) | an Epic |
| Project Story (`project`) | none — root-level work |
| Devteam Story (`dev`) | none — root-level work |
| Workitem (`workitem`) | a Story, Project Story or Devteam Story |

**Always set `parentId` for an Epic, a User Story and a Workitem.** If the parent
does not exist yet, create it first: an Epic before its Stories, a Story before
its Workitems. If it is unclear which parent is meant, ask — do not guess, and do
not create the item parentless "for now".

> **Status of the enforcement claim.** Creating these three without a parent was
> observed being rejected with HTTP 400, and a parentless item could then not be
> updated at all. The current schema marks `parentId` optional on both
> `TaskCreate` and `TaskImport` and describes it as *"leave it out for a task at
> the top"*, so either the check lives in route logic the schema cannot express,
> or it is laxer than it was. **Unverified against the current API.** Setting the
> parent is correct either way; do not rely on a 400 to catch a mistake.

## Maturity is the `progress:*` tag

The phase a card sits in **is** its `progress:*` tag. The phases are `idea`,
`draft`, `ready`, `todo`, `doing`, `done` — and `closed` is *not* among them;
closed is `completionState = "closed"`, a separate axis.

Omit the tag on create or import and the server adds the starting phase **for the
type**: `progress:todo` for a Workitem, `progress:idea` for everything else. Do
not blanket-set `progress:idea` on every task — that puts Workitems in the wrong
column.

**The date fields are history, not state.** `draftDate`, `readyDate`, `todoDate`,
`startedDate`, `doneDate` and `closedDate` are lead-time stamps recording when a
task entered each phase. Set them only to bring a task in *with* history — an
import of past work, or an agent creating something already refined. Setting a
date does not move a card; changing the phase does.

**Workitems do not use the `Closed` state.** A Workitem is a lightweight
coordination item on the Iteration Board and is complete at `progress:done`.
`completionState` stays `open` for a Workitem; an obsolete one is deleted rather
than closed. Closing applies to Stories (and, when deliberately stopped,
Initiatives and Epics).

## Tags — namespacing rules

Not in the spec at all, and confirmed directly against a live project (tags were
visible in project settings but would not render on the task cards until the rules
below were applied):

- **Every general/custom tag must be namespaced `project:<value>`** — exactly one colon, right after the literal `project`, and **no further colon inside `<value>`**. A tag with a stray second colon, or one missing the prefix entirely, does not reliably render on the task card even though the raw string still shows up wherever tag lists are displayed.
- `progress:<phase>` is a **separate, reserved system namespace**. Don't mix the two.
- **Group by color, not by a second text prefix.** Don't build a nested namespace like `project:Aufwand:gering` — that's the extra-colon mistake. Fold the category into the value with a space (`project:Aufwand gering`, `project:Priorität Must`) and give same-category tags related colors via `tagDefinitions`.
- **Every tag string used on any task must have a matching entry in `settings.tagDefinitions`** (exact string match) or it won't be styled correctly — and nothing rejects the import for it. Collect the full set of distinct values across all tasks and emit one definition per value; don't declare a subset and hope the rest fall back.

Example from a real import (spreadsheet columns Kategorie / Aufwand / Gewichtung /
Priorität turned into tags):
`["progress:idea", "project:Stammdaten", "project:Priorität Must", "project:Aufwand gering", "project:Gewichtung 3"]`

## Bugs

A bug is **not** a separate Story. It is a Workitem with `isBug = true` whose
parent is the affected Story. `isBug` is valid *only* on a `workitem` — any other
type is refused. It flags **every ancestor** in the project's `bugRollup` until
the Workitem reaches `progress:done`. See `betterplan-create-workitem`.

## Bulk import

`POST /projects/import` creates a new project from a `ProjectImportRequest`.
`team_id` is required in the body (**400** without it) and the caller must be a
member (**403** otherwise). Every UUID in the payload is regenerated and every
cross-reference remapped, so an import cannot collide with the project it came
from.

Note that `GET /templates/{template_id}`'s own description points at
`POST /projects/{project_id}/import` — **that route does not exist**. Use
`POST /projects/import`.

Hierarchy is built purely from `parentId`: each task carries an `id` and its
children reference it. Two things worth knowing that the schema does not tell you:

- **Set `displayOrder` on every task**, as `{"storyboard": <n>}` — a sequential index among siblings sharing a parent (root level counts as one shared parent). The single-task create routes compute this themselves and ignore what you send; the bulk write and the import keep it. A task that reaches the database without one has been seen to disappear from views the first time it is edited.
- **Use UUIDs for `id`.** The import says it regenerates *UUIDs* and remaps references; whether a non-UUID correlation key (a slug) survives that is undocumented and untested. Slugs were previously recommended here — treat that as unverified.

When in doubt about any other field, compare against a real exported project's
`tasks[]` as ground truth: the schema documents what a field *accepts*, not what
the app relies on being present.
