# Conventions & divergences

**The API spec is the authority on shapes:** <https://app.yourbetterplan.com/api/openapi.json>.
Fetch it when you need field names, required arguments, enums or endpoints. The
MCP likewise describes its own tools at runtime. Nothing about the API surface is
restated here — a vendored copy of the spec used to live in this directory and
drifted eleven major versions behind before anyone noticed, and an earlier
version of *this* file repeated the same mistake in prose: it explained fields
the spec had meanwhile documented better than it did.

Three things stay here, because no schema carries them:

1. **The vocabulary bridge** — how the method's building blocks map onto the API's
   words.
2. **The conventions** — tag namespacing above all, which is pure agreement and
   appears nowhere in the spec.
3. **The divergences** — the handful of places where the spec promises something
   the product does not do. These are the dangerous ones precisely because the
   spec is otherwise trustworthy.

When a claim here contradicts the spec, the spec wins and this file is stale —
except in section 3, where the disagreement *is* the content.

## The vocabulary bridge

Every building block is one task object, distinguished by `type`. The spec gives
`TaskType` as a bare enum with no explanation; this is the mapping:

| Building block | `type` |
|---|---|
| Initiative | `initiative` |
| Epic | `epic` |
| User Story | `story` |
| Project Story | `project` |
| Devteam Story | `dev` |
| Workitem | `workitem` |

The non-obvious part: the three story types are distinct `type` values — a User
Story is `story`, a Project Story is `project`, a Devteam Story is `dev`.

**Content vs metadata.** Content lives in `title` + `description` (Markdown) —
that is what the create-* skills produce. Structure is set as fields on the item
and never written into the description: `type`, `parentId`, `releaseId`,
`estimation`, `tags`, `assignee`, the lead-time dates, `completionState`.

### The hierarchy, past what `parentId` says

The spec's `parentId` covers the common case ("a story's epic, a workitem's
story"). What it leaves out:

| Type | Parent |
|---|---|
| Initiative | none — sits at the root |
| Epic | an Initiative |
| User Story | an Epic |
| Project Story | none — root-level work |
| Devteam Story | none — root-level work |
| Workitem | a Story, **Project Story or Devteam Story** |

**Always set `parentId` for an Epic, a User Story and a Workitem.** If the parent
does not exist yet, create it first. If it is unclear which parent is meant, ask —
do not guess, and do not create the item parentless "for now". The schema marks
`parentId` optional and nothing reliably rejects a parentless Epic, so there is no
error to catch the mistake for you.

### Maturity

The phase a card sits in **is** its `progress:*` tag; `MaturityPhase` in the spec
lists the six phases and explains the mapping. Three things it does not say:

- **`closed` is not a phase.** It is `completionState`, a separate axis.
- **Workitems do not use the Closed state.** A Workitem is a lightweight
  coordination item and is complete at `progress:done`; `completionState` stays
  `open`, and an obsolete one is deleted rather than closed. Closing applies to
  Stories, and to Initiatives and Epics that were deliberately stopped.
- **Setting a lead-time date does not move a card.** The dates are history;
  changing the phase is what moves it. Set them only to bring a task in *with*
  history.

## Tags — the rules no schema carries

None of this is in the spec. It was established against a live project, where the
tags sat in project settings but would not render on the cards until the rules
below were applied.

- **Every general tag must be namespaced `project:<value>`** — exactly one colon,
  right after the literal `project`, and **no further colon inside `<value>`**. A
  tag with a stray second colon, or one missing the prefix entirely, does not
  reliably render on the card even though the raw string still shows up wherever
  tag lists are displayed. (The spec's own `TaskResponse` example shows a bare
  tag next to a `progress:*` one. Don't copy it.)
- **`progress:<phase>` is a separate, reserved system namespace.** Don't mix the
  two, and don't give it a definition — the app styles it.
- **Group by colour, not by a second text prefix.** A nested namespace like
  `project:Aufwand:gering` is the extra-colon mistake. Fold the category into the
  value with a space (`project:Aufwand gering`) and give same-category tags
  related colours.
- **Keep values short; add a category word only when the value alone is
  ambiguous.** Card space is limited, and a tag wide enough to crowd the title
  costs more than it carries. `gering` means nothing alone, so `project:Aufwand
  gering` earns its category word. `Must` carries its own meaning, so the MoSCoW
  tag is `project:Must` and **not** `project:Priorität Must`. The colour family
  says which dimension a tag belongs to, at no width. Tags with no grouping keep
  the default colour; don't invent one to look organised.
- **A value that is the default of the whole project earns no tag at all.** Where
  one value dominates, tagging it costs width on every card and carries nothing,
  because a filter on it returns everything. Tag the **deviations** and document
  the default once. The cost is that you can no longer filter *for* the default,
  only exclude the exceptions; for "what do we have to do", that is the same
  answer.
- **A tag and its definition are spelled differently, and this is the trap.** The
  task carries the namespaced string, `settings.tagDefinitions` carries the
  **bare value**: a task tagged `project:Must` needs `{"name": "Must", "color":
  "red"}`, *not* `{"name": "project:Must"}`. Verified against a live project.
  Collect the distinct values across all tasks, strip the `project:` prefix, and
  emit one definition per value; don't declare a subset and hope the rest fall
  back. Nothing rejects a missing or misspelled definition — the tag simply does
  not get styled.

## References — `#N` is plain text

A task carries **two** identifiers, and conflating them is the common mistake.
`id` is a UUID that **you may set**; the server mints one only when you don't.
`taskNumber` is the integer people and commits mean by `#570`, and it is the one
thing you cannot set — no payload has a slot for it. The MCP argument spelled
`task_id` **is** the `id` field; there is no third identifier.

That `id` is settable is not documented, so here is the evidence: `TaskCreate`
and `TaskImport` both have an `id` slot with no caveat, where `create_bucket`'s
`id` says *"Accepted and ignored — the server always mints its own bucket id."*
Hand-assigned task ids have been observed surviving in a live project.

**A `#N` reference is plain text in a description, and that is all it is.** You
write the number into the Markdown and Betterplan resolves it — there is no
reference object to create and nothing to link. `list_task_references`
*searches* descriptions, comments and activity logs for the number.

Two consequences, both only for a precursor format that is imported rather than
typed by a human:

- Writing the **`id`** instead of the number produces a reference
  `list_task_references` will never find — present to a reader, invisible to the
  product, and nothing rejects it.
- **The `#N` references cannot be finished by the import**, because the target's
  number does not exist yet when the referrer is created. `parentId` and
  `releaseId` do resolve in a single pass, because you set the `id`s yourself.

**Scope that second pass to the references, and don't let it grow.** It touches
only the tasks whose descriptions carry a `#N`. Weigh it against simply naming
the other item in prose: a reader understands "…see *Set up the intake channel*"
perfectly well, it just isn't clickable. At ten references that is a trade-off,
not a necessity.

**That second pass must send `description` only** — not a task you read first and
wrote back whole. `TaskPatch.reworkPoints` is a delta added to the lifetime
total, so a full write-back adds a task's rework points to its own total again
and silently corrupts a quality metric. The spec states both semantics; the rule
is to send `task_id` and the fields you are changing, nothing else (ADR-029).

## Dependencies

The spec names the direction plainly — `sourceTaskId` is *"the task that has to
be done first"*, `targetTaskId` *"the task that is waiting"*, and `blocks` is the
only kind there is. An edge that would close a cycle is a 400.

What that leaves to say is the **conversion**: a precursor field meaning "A
depends on B" maps to `sourceTaskId` = B, `targetTaskId` = A. The dependency's
*source* is the thing the entry pointed at. Import it the other way round and the
critical path runs backwards while every call succeeds.

That `blocks` is the only type is also why **soft references have to be text**:
the data model offers no object for them. It is not a stylistic choice.

## Bugs

A bug is **not** a separate Story. It is a Workitem with `isBug = true` whose
parent is the affected Story — the spec covers what the flag does; the method
point is that a bug never gets a Story of its own. See
`betterplan-create-workitem`.

## Bulk import

`POST /projects/import` creates a new project from a `ProjectImportRequest`; the
spec documents the required `team_id`, the membership check, and that every UUID
is regenerated with its cross-references remapped. `POST /projects/import-zip`
takes the same thing as an archive. Five things the spec does not tell you:

- **Neither route is reachable from the MCP.** They carry no `mcp` tag, and the
  44 tools that do have no import among them. An agent therefore *prepares* a
  payload and hands it to a human to import — it cannot perform the import
  itself. Plan the handover accordingly.
- **The import does not carry personas**, and this is a gap, not a defect — the
  schema never offered the key, so nothing is lost silently. Personas are a
  first-class project entity on the same footing as a release, with nine routes
  that are *all* MCP-exposed: create, patch, archive, restore, assign to a task,
  remove, and read the assignments. A precursor format that assigns personas to
  stories therefore always has a post-import step, and that step an agent *can*
  do itself — unlike the import. Note the assignment is a route of its own
  (`PUT /projects/{id}/personas/{persona_id}/tasks/{task_id}`); neither
  `TaskImport` nor `TaskCreate` has a persona field.
- **It always creates a new project.** There is no import into an existing one. A
  map that should land next to existing work has to be created task by task
  instead.
- **Set `displayOrder` on every task**, as `{"storyboard": <n>}` — a sequential
  index among siblings sharing a parent (root level counts as one shared
  parent), **zero-based**. The spec says which routes honour the field; it does
  not say that a task reaching the database without one has been seen to
  disappear from views the first time it is edited.
- **Leave `progress:*` out** unless a task needs a phase other than its type's
  default, which the spec gives per field. Blanket-setting `progress:idea` across
  a payload puts Workitems in the wrong column.

### Where the spec and the product disagree

Checked against API **14.0.1**. Each entry needs a bug number in Betterplan; an
entry whose bug is fixed belongs **deleted**, not amended. This section is the
one part of this file with an expiry date, and it is the part that justifies the
file existing.

- **`dependencies` is declared and dropped — Betterplan #797.**
  `ProjectImportRequest` has a `dependencies` array with a full
  `DependencyImport` schema (`sourceTaskId`, `targetTaskId`, `dependencyType` all
  required). An import that sends it comes back with `list_dependencies` → `[]`.
  Nothing is rejected and nothing warns. This is a defect under repair, not a
  property of the format: keep emitting the array, because it is correct and
  because it is what the fix will honour. **Until #797 ships, the graph needs a
  post-import pass** — one `create_dependency` per edge, direction set by hand
  (see *Dependencies* above).
- **`GET /templates/{template_id}` points at a route that does not exist —
  Betterplan #798.** Its description says the result "can be posted unchanged to
  `POST /projects/{project_id}/import`". There is no such path, and the spec's
  own `paths` does not list it. Use `POST /projects/import`. The rest of that
  sentence is sound: the result really does match `ProjectImportRequest`.

When in doubt about any other field, compare against a real project's `tasks[]`
as ground truth — `list_tasks(project_id=…, limit=3)` is enough and far cheaper
than `get_project`. The schema documents what a field *accepts*, not what the app
relies on being present.
