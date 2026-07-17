# Type mapping & conventions

This file holds only the conceptual mapping that the Betterplan MCP does **not** spell out on its own. The MCP describes its tools, fields, and argument types at runtime — rely on those for exact field names, required arguments, and endpoints. Do not duplicate the API surface here; it would only drift.

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

**Workitems do not use the `Closed` state.** A Workitem is a lightweight coordination item on the Iteration Board and is complete once `doneDate` is set (the **Done** column). `completionState` stays at its default and is never set to `"closed"` for a Workitem; an obsolete Workitem is deleted rather than closed. The `Closed` row above applies to Stories (and, when explicitly stopped, Initiatives and Epics).

## Bugs

A bug is **not** a separate Story. It is a Workitem (`type: workitem`) with `isBug = true`, whose `parentId` points to the affected Story. `isBug` is set on the Workitem, never on the Story. The backend reopens the parent Story and maintains the bug rollup. See `create-workitem`.
