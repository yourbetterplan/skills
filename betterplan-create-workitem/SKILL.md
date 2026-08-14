---
name: betterplan-create-workitem
description: >
  This skill should be used when the user wants to break a Betterplan Story into
  Workitems — the smallest units that coordinate delivery on the Iteration
  Board. Triggers include "break this into workitems", "add workitems", "split
  this story into tasks for the iteration", or planning the implementation steps
  of a single Story. Workitems belong to a Story and carry no story points. Also
  use it to report a bug or rework on a Story — triggers like "report a bug",
  "log a bug", "this story is broken" — since a bug is a Workitem with
  isBug=true on the affected Story.
metadata:
  version: "0.1.0"
---

# Create Betterplan Workitems

A Workitem is the **smallest unit** of work. It belongs to one Story and exists only on the Iteration Board to help the implementing team coordinate delivery. Workitems move through the board columns **Open → In Progress → Done**. Data model: `type: workitem`, with `parentId` set to the Story.

Key rules (from `betterplan-workflow`):

- A Workitem always has a **parent Story**. If there is no parent Story yet, create the Story first with `betterplan-create-story`.
- Workitems have **no story points**, **no maturity level**, and **no discovery dialogue** — they serve coordination, not planning. Do not run a Why/What/How loop here.
- A Workitem has **no `Closed` state**. It is complete when it reaches the **Done** column (`doneDate`) — never set `completionState = "closed"` on a Workitem. Unlike a Story, a Workitem carries no planning or historical value, so an obsolete Workitem is simply deleted, not closed with a rationale.
- A Workitem is either clearly formulated and ready to be created, or it is not created yet. If the team is unsure about the break-down, pause: capture what is clear and resume later — do not log half-formed Workitems.
- Keep delivery detail in Workitems, not in the Backlog. The Story stays readable; the steps live where the team works on them.

## When to create them

Create Workitems when a Story is **Ready** and about to be (or is being) implemented in an iteration. Do not pre-break every backlog Story into Workitems — only the ones in play.

## How to break a Story down

1. Read the Story's acceptance criteria; each criterion usually maps to one or more Workitems.
2. Add the implementation steps the team needs: e.g. backend, frontend, data/migration, tests, review, deploy — only those that apply.
3. Keep each Workitem small enough to finish in roughly a day and phrase it as a concrete action ("Add endpoint…", "Write tests for…").
4. Order them so the Story can reach Done; note any sequencing.
5. Do not smuggle in cross-cutting work — that belongs in a Devteam or Project Story.

## Bugs are workitems

A bug or rework on a Story is created as a **Workitem with `isBug = true`** on that Story — not as a separate Story. `isBug` is an attribute of the Workitem itself (set it as an argument on the Workitem's create call, or via the MCP); the Workitem's parent is the affected Story. The backend handles the rest (reopening the Story and the bug rollup).

Keep it Quick-Capture: **at most one clarifying question** before creating the bug Workitem — typically *what is the expected behaviour vs. what actually happens?* (apply the *one open question per beat* rule from `betterplan-workflow`). Do not run the full Story discovery loop on a bug. The Workitem content is the bug description: what is broken, expected behaviour, and (if the user offered it) reproduction steps. Do not create a new Story for a bug, and do not set any bug flag on the Story.

## Create them (MCP or Markdown)

Follow the *Creating an item: MCP first, Markdown fallback* rule in `betterplan-workflow` — including the **pre-create confirmation**: show the proposed Workitem list (or single bug Workitem) in chat first and ask *"Soll ich die so anlegen — als Workitems unter <Story>?"* before any MCP call or Markdown output. Never act in the same turn you first show the proposal. If the user requests changes, update the list in chat and re-confirm; do not silently patch.

If the Betterplan MCP is available, create each Workitem via its tool with `type: workitem` and `parentId` set to the Story (and `isBug: true` for a bug). Workitems carry no estimation. Otherwise output the Markdown checklist below.

## Output template (Markdown fallback)

Content only — the workitem actions themselves. The parent Story is a field, so no need to repeat its id or meta:

```
- [ ] <action — e.g. Add /search endpoint>
- [ ] <action — e.g. Wire autocomplete to the search box>
- [ ] <action — e.g. Add tests for empty / short queries>
- [ ] <action — e.g. Review and deploy>
```

Name the parent Story in your chat reply, not in the pasteable list. Keep the list short and action-oriented. If it grows large, the parent Story is probably too big — suggest splitting the Story instead (see method-deep-dive in `betterplan-workflow`).

## Pause if uncertain

Workitems are intentionally small and fast. There is no canvas and no resume dialogue here — but the *spirit* of *Resuming refinement of an existing item* (in `betterplan-workflow`) still applies: if you are unsure whether the list of Workitems is complete, pause. Tell the user what is captured so far and what is missing, and create the rest in a later turn. Never create an uncertain Workitem just to fill the list.
