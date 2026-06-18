# Betterplan data model (for the future MCP)

This is the shape items take in the Betterplan API/MCP. It is **not connected yet** — until then the skills output Markdown (title + description). When the MCP is available, map the same content onto these fields.

Every building block is one task object, distinguished by the `type` field. `title` and `description` hold the content; everything else is structure/metadata set on the task, not written into the description.

## `type` values

| Building block | `type` |
|---|---|
| Initiative | `initiative` |
| Epic | `epic` |
| User Story | `story` |
| Project Story | `project` |
| Devteam Story | `dev` |
| Workitem | `workitem` |

Note the mapping: the three story types are distinct `type` values — a User Story is `story`, a Project Story is `project`, a Devteam Story is `dev`.

## Key fields of TaskCreate

| Field | Type | Meaning |
|---|---|---|
| `type` | string (enum above) | The building block type. Required. |
| `title` | string | Item title. Required. **Content.** |
| `description` | string (Markdown) | Item body, incl. acceptance criteria. Default "". **Content.** |
| `parentId` | string \| null | Parent task: epic→initiative, story→epic, workitem→story. **Structure, not content.** |
| `releaseId` | string \| null | Release assignment. |
| `estimation` | integer \| null | Story Points. Workitems have none. Auto-filled with team median if null. |
| `priority` | integer (default 0) | Ordering within a maturity stage. |
| `completionState` | string (default `open`) | `open` or `closed`. |
| `tags` | string[] | Tag names (see project tag definitions). |
| `assignee` | string \| null | Assignee user id. |
| `isBug` | boolean (default false) | Set **on a Workitem** (`type: workitem`) to mark it as a bug — never on the Story. The Workitem's `parentId` points to the affected Story. The backend reopens that Story and maintains the bug rollup (`ProjectResponse.bugRollup` = task ids with an unresolved fix descendant). |
| `color`, `cardImageAttachmentId`, `displayOrder` | — | Presentation/ordering. |

## Maturity is expressed through date fields

There is **no single status field**. A Story's maturity level is derived from which date fields are set (and `completionState`):

| Maturity | Set field |
|---|---|
| Idea | none of the below set |
| Draft | `draftDate` |
| Ready | `readyDate` |
| Todo | `todoDate` |
| Doing | `startedDate` |
| Done | `doneDate` |
| Closed | `closedDate` + `completionState = "closed"` |

A new item created without dates is at **Idea**. Initiatives and Epics are structure and normally do not carry maturity dates.

## Related objects (not created by these skills yet)

- **Releases** (`ReleaseCreate`): `title`, `position`, optional `date`, `goal`, `features`, `metrics`, `status` (default `planned`).
- **Dependencies** (`CreateDependencyRequest`): `sourceTaskId`, `targetTaskId`, `dependencyType` (e.g. blocks/requires — exact strings TBC).
- **Discussions / comments** (`DiscussionCreate`, `CommentCreate`): per-task threads with markdown content.
- **Attachments** (`AttachmentUploadJsonRequest`): base64 upload tied to an `entity_type` + `entity_id`.

## Implication for the create-* skills

Output only `title` + `description` content. Do not bake `type`, `parentId`, `estimation`, maturity, tags, or dependencies into the text — those are fields. When the MCP is connected, set them as arguments on the create call instead.
