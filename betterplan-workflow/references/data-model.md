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
- **Group by color, not by a second text prefix.** Don't build a nested namespace like `project:Aufwand:gering` — that's the extra-colon mistake. Fold the category into the value with a space (`project:Aufwand gering`) and give same-category tags related colors via `tagDefinitions`.
- **Keep values short, and add a category word only when the value alone is ambiguous.** Card space is limited: a tag wide enough to crowd the title has cost more than it carries. `gering` means nothing on its own, so `project:Aufwand gering` earns its category word. `Hersteller` is already unambiguous, so the obligation-bearer tag is `project:Hersteller` and **not** `project:Pflicht Hersteller`; `Must` carries its own meaning, so a MoSCoW tag is `project:Must` and **not** `project:Priorität Must`. The colour family says which dimension a tag belongs to, at no width. Tags with no grouping keep the default colour; don't invent one to look organised.
- **A value that is the default of the whole project earns no tag at all.** Where one value dominates — every item `Must`, every item the same team — tagging it costs width on every card and carries nothing, because a filter on it returns everything. Tag the **deviations** and document the default once. The cost is that you can no longer filter *for* the default, only exclude the exceptions; for "what do we have to do", that is the same answer.
- **Every tag used on a task needs an entry in `settings.tagDefinitions` — and the two are spelled differently.** The task carries the namespaced string, the definition carries the **bare value**: a task tagged `project:Must` needs `{"name": "Must", "color": "red"}`, *not* `{"name": "project:Must"}`. Verified against a live project on 2026-11-09 (`tags:["progress:idea","project:Must"]` alongside `tagDefinitions:[{"name":"Must","color":"red"},…]`). An earlier version of this file said "exact string match" — that was wrong, and it produces definitions that never match. Collect the full set of distinct values across all tasks, strip the `project:` prefix, and emit one definition per value; don't declare a subset and hope the rest fall back. Nothing rejects the import for a missing or misspelled definition — the tag simply does not get styled.
- **`progress:*` needs no definition.** It is the reserved system namespace and is styled by the app; only the custom `project:*` values go into `tagDefinitions`.

Example from a real import (spreadsheet columns Kategorie / Aufwand / Gewichtung /
Priorität turned into tags):
`["progress:idea", "project:Stammdaten", "project:Must", "project:Aufwand gering", "project:Gewichtung 3"]`

## References and dependencies

A task carries **two** identifiers, and conflating them is the common mistake:

| Field on the task | Type | Who assigns it |
|---|---|---|
| `id` | UUID | **you may set it**; the server mints one only when you don't |
| `taskNumber` | integer ≥ 1 | the server, always — **the `#570` people and commits mean** |

**There is no third identifier.** The MCP argument spelled `task_id` **is** the
task's `id` field; `get_task(task_id=…)` and `update_task(task_id=…)` take that
UUID. An earlier version of this file listed `task_id` as server-assigned and a
"map-local id" as a separate species — both wrong. A Markdown precursor's id is
simply the `id` the task will be created with.

**`id` is settable, and it is already being used that way.** `TaskCreate` and
`TaskImport` both have an `id` slot with no caveat — compare `create_bucket`,
whose `id` says "Accepted and ignored — the server always mints its own bucket
id." Verified on 2026-11-09: the tasks in a live project carry hand-assigned ids
of the form `33333333-0000-4000-8000-000000000001`.

**`taskNumber` is the one thing you cannot set.** `create_task` "automatically
handles task numbering", and no payload has a slot for it. To go the other way,
`list_tasks(task_number=N)` turns a number into a task.

**A `#N` reference is plain text in a description, and that is all it is.** You
write the number into the Markdown and Betterplan resolves it — there is no
reference object to create and nothing to link. `list_task_references` *searches*
descriptions, discussion comments and activity logs for the number.

Two consequences, both only for a precursor format that is imported rather than
typed by a human:

- Writing the **`id`** instead of the number produces a reference
  `list_task_references` will never find — present to a reader, invisible to the
  product, and nothing rejects it.
- **The `#N` references are the only thing an import cannot finish in one pass**,
  because the target's number does not exist yet when the referrer is created.
  Everything structural — `parentId`, `releaseId`, dependencies — resolves in a
  single pass, because you set the `id`s yourself.

**Scope that second pass to the references, and don't let it grow.** It touches
only the handful of tasks whose descriptions carry a `#N`, not the whole import.
Weigh it against simply naming the other item in prose: a reader understands
"…see *Set up the intake channel*" perfectly well, it just isn't clickable and
`list_task_references` won't find it. At ten references that is a trade-off, not
a necessity.

**That second pass must send `description` only.** `update_task` warns that
re-sending a task you read first is "not harmless, because `reworkPoints` is a
delta that accumulates" — a full write-back adds the task's rework points to its
own lifetime total again, silently corrupting a quality metric. Send `task_id`
and the fields you are changing, nothing else (ADR-029).

**Dependency direction is the other silent error.** `create_dependency` knows
exactly one `dependencyType`, `blocks`, with `sourceTaskId` = "the task that has
to be done **first**" and `targetTaskId` = "the task that is **waiting**".

So a precursor field meaning "A depends on B" maps to **`sourceTaskId` = B,
`targetTaskId` = A** — the dependency's *source* is the thing the entry pointed
at. Import it the other way round and the critical path runs backwards on the
Delivery Timeline while every call succeeds.

That `blocks` is the only type is also why **soft references have to be text**:
the data model offers no object for them. It is not a stylistic choice.

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

- **Set `displayOrder` on every task**, as `{"storyboard": <n>}` — a sequential index among siblings sharing a parent (root level counts as one shared parent), **zero-based**; a live project shows `0, 1, 2` across three sibling stories. The single-task create routes compute this themselves and ignore what you send; the bulk write and the import keep it. A task that reaches the database without one has been seen to disappear from views the first time it is edited.
- **Use UUIDs for `id`.** The import regenerates them and remaps every reference, so the ids in the payload are pure correlation keys — their only job is to let `parentId`, `releaseId` and the dependencies point at each other. A non-UUID key (a slug) is undocumented and untested; slugs were previously recommended here, treat that as unverified.
- **Leave `progress:*` out** unless a task needs a phase other than its type's default. The server sets `progress:todo` for a Workitem and `progress:idea` for everything else. Blanket-setting `progress:idea` across a payload puts Workitems in the wrong column.
- **It always creates a new project.** There is no import into an existing one. A map that should land next to existing work has to be created task by task instead.

### What the import does not carry

The project object — what `list_projects(include_data=true)` answers with — has
`tasks`, `releases`, `buckets`, `timelineNotes`, `iterations`, `discussions` and
`dependencies`. **It has no `personas` key.** Personas are a separate resource:
create them with `create_persona` after the import and attach them with
`assign_persona`. A precursor format that assigns personas to stories therefore
always has a post-import step, however the rest is delivered.

Treat the top-level key names of `ProjectImportRequest` as **derived, not
documented**: they match the project object's shape, which is strong evidence but
not a schema. The same caution applies to `team_id` — this file names it in
`snake_case`, while the project object answers with `teamId`. If an import is
rejected, those are the first two things to vary.

When in doubt about any other field, compare against a real project's `tasks[]`
as ground truth — `list_tasks(project_id=…, limit=3)` is enough and far cheaper
than `get_project`. The schema documents what a field *accepts*, not what the app
relies on being present.
