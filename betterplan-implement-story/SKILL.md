---
name: betterplan-implement-story
description: >
  This skill should be used to implement Betterplan Stories using a coding agent.
  The agent picks up Stories tagged with "Agent" that are in a current iteration,
  proposes Workitems at a chosen granularity level, implements them autonomously
  (one commit per Workitem, one branch per Story), and updates the Iteration
  Board in real time. Triggers include "mache deine Arbeit", "implement all
  agent stories", or when a human manually adds the "Agent" tag to a Story in
  a current iteration.
metadata:
  version: "0.2.0"
---

# Implement a Story with the coding agent

This skill turns a **Ready Story in a current iteration** into implemented, committed, and board-tracked work — autonomously.

The flow for the human is short:
1. Bring a Story to **Ready** (via `betterplan-create-story`).
2. Put it in a **current iteration**.
3. Add the tag **`project:Agent`**.
4. Say **"mache deine Arbeit"**.

The agent does the rest: choose granularity → propose Workitems → confirm → branch → commit per Workitem → board updates → merge → done.

## Core signal: the `project:Agent` tag

The tag `project:Agent` on a Story is the **sole assignment mechanism**. It has two modes:

- **Human-to-agent signal**: A human adds the tag → "this Story is for the agent."
- **Activity indicator**: While the agent works, the tag stays on. When the Story is done, the agent removes it.

Workitems created by the agent **do not carry** the `project:Agent` tag — only the parent Story does.

## Prerequisites

Before the agent can pick up a Story, all of the following must be true:

1. **Maturity Ready** — the Story's `readyDate` is set. (Discovery was done via `betterplan-create-story`; the Why, Rules + Examples, and How-decisions are settled.)
2. **In a current iteration** — the Story is assigned to an iteration whose `startDate ≤ today ≤ endDate`.
3. **Tag `project:Agent`** — the tag is set on the Story in Betterplan.
4. **Git repo accessible** — the agent can clone, branch, commit, and push to the repository linked to the project.

The agent **will not** pick up Stories missing any of these. Stories that have the tag but fail the iteration check are mentioned once at startup and then skipped.

## Step 1 — Scan & prioritise

On "mache deine Arbeit" (or equivalent trigger), the agent:

1. Finds **all open Stories** (not Closed, not Done) with tag `project:Agent`.
2. Filters to those in a **current iteration** (any iteration where `startDate ≤ today ≤ endDate`).
3. **Sorts by Betterplan priority** — uses `displayOrder` ascending (lower number = higher priority, the natural backlog order).
4. Picks the **highest-priority Story**.
5. If multiple Stories qualify but currently in-progress work is blocked (error state), finishes the blocking Story first. Otherwise, picks the next in order.

If no Stories are found: report to the human and stop. If Stories have the tag but are not in a current iteration, mention them once:

> *"Story X, Y, and Z have the Agent tag but are not in a current iteration — skipped. Move them into an iteration to activate them."*

## Step 2 — Signal start on the board

Before the agent spends any time analysing, it signals to the team that this Story is now being worked on:

1. **Move Story to Doing**: set `startedDate` on the Story in Betterplan.
2. **Add the `project:Agent` tag**: if the human already added it (queued the Story), it is already present; if not, the agent adds it now. Either way, the tag is set.

This gives immediate visual feedback on the Iteration Board: other team members see "a Story is being implemented by an agent right now."

## Step 3 — Choose granularity level

Before reading the Story or proposing Workitems, the agent asks the human which level of detail they want for tracking:

> *"Wie detailliert soll ich die Arbeit tracken? (1 = keine Workitems, 2 = grob/Default, 3 = volles Detail)"*

| Level | Name | Beschreibung |
|---|---|---|
| **1** | Keine Workitems | Alles lokal auf dem Branch, keine Workitems in Betterplan. Der Agent committed und pusht, trackt aber nichts im Board. Sichtbar ist nur: Story Doing → Done. |
| **2** (default) | Grob — Backend/Frontend/… | Wenige grobe Workitems (z.B. "Backend", "Frontend", "Tests", "Review & Merge"). Innerhalb eines Workitems tracked der Agent den Fortschritt über eine **Checkliste im Workitem-Description** (Sub-Steps). |
| **3** | Volles Detail | Jedes AC → ein oder mehrere Workitems. Jeder logische Schritt ein eigenes Workitem auf dem Board. |

The default is **Level 2** if the human doesn't express a preference. The chosen level affects everything that follows: how Workitems are proposed, created, tracked, and completed.

## Step 4 — Read & analyse the Story

The agent reads the full Story content:

- `title` and `description` (Why, Context, Acceptance Criteria, Out of scope, Open questions)
- The current maturity level
- The parent Epic (for context)
- Any existing Workitems (if someone pre-created them)

If the maturity is not **Ready**, the agent does not proceed — inform the human:

> *"Story BP-123 is tagged Agent but is at Draft maturity. Bring it to Ready first via betterplan-create-story."*

## Step 5 — Propose Workitems (level-dependent)

The agent derives a plan. How the plan looks depends on the level chosen in Step 3.

### Level 1 (keine Workitems)

The agent shows the implementation approach as a simple list of steps in chat. No Workitems are proposed or later created in Betterplan. The human confirms just the approach, then the agent implements everything on one branch.

> *"Ich implementiere BP-123 auf branch feature/bp-123-text-search (target: main). Schritte: Backend-Endpoint, Frontend-UI, Tests, dann Merge. Einverstanden?"*

### Level 2 (grob — default)

Group the ACs and implementation steps into **few, coarse Workitems** — typically:

- **Backend** — Datenmodell, API-Endpoints, Logik
- **Frontend** — UI, Interaktionen, Validierung
- **Tests** — alle Tests (Unit, Integration, E2E) für diese Story
- **Review & Merge** — Code-Review, Branch mergen, CI grün kriegen

Each coarse Workitem gets an **inline Checkliste** of substeps. The checklist lives in the Workitem description in Betterplan and is updated by the agent as it progresses.

**Show the proposal in chat** — including the workitems plus their internal checklists:

```
### Implementierungsplan für "BP-123 — Text-Suche mit Autocomplete"

Level: Grob (2)
Branch: feature/bp-123-text-search (target: main)

Workitems:
  1. Backend                        → AC1
     [ ] Endpoint definieren
     [ ] Query-Logik implementieren
     [ ] Auditing anbinden
     [ ] Tests für Backend
  2. Frontend                       → AC1, AC2
     [ ] Input-Feld mit Autocomplete
     [ ] 2-Zeichen-Gate
     [ ] Audit-Einträge anzeigen
  3. Review & Merge

→ Sag "los" oder änder einzelne Punkte.
```

### Level 3 (volles Detail)

Each **Acceptance Criterion** becomes one or more Workitems. Add implementation steps (backend, frontend, tests, review) where they don't map to an AC directly. Each Workitem is roughly one day or smaller.

```
### Implementierungsplan für "BP-123 — Text-Suche mit Autocomplete"

Level: Detail (3)
Branch: feature/bp-123-text-search (target: main)

Workitems (Reihenfolge):
  1. Add /search endpoint with query parameter          → AC1
  2. Wire autocomplete to the search input               → AC1
  3. Add tests for empty/short queries (2+ char gate)    → AC2
  4. Add audit logging for search terms                  → AC3
  5. Review and merge

→ Sag "los" oder änder einzelne Punkte.
```

**Do not** create anything in Betterplan yet. The human must see and confirm the plan first.

If the Story already has Workitems (pre-created by the human or a previous session), the agent reads them and proposes the implementation sequence at the chosen level — the human may still adjust or confirm as-is.

## Step 6 — Confirm the plan

The human either:

- Says **"los"** / **"go"** / **"ja"** → proceeds to Step 7.
- Requests changes → update the proposal in chat, re-show, wait for confirmation.
- Cancels → **undo**: move the Story back to Todo (clear `startedDate`), remove the `project:Agent` tag, and stop. The Story is now unassigned and ready for a human or another session.

**One confirmation for the whole list.** Once confirmed, the agent works autonomously. No per-Workitem gate unless an error occurs (see Step 9).

## Step 7 — Set up (level-dependent)

### Level 1 (keine Workitems)

1. **Create the Branch**: `feature/<story-id>-<short-slug>`. Target = default branch.
2. **No Workitems created in Betterplan.** The agent works entirely on the branch and updates only the Story (Doing → Done).

### Level 2 (grob) & Level 3 (volles Detail)

1. **Create the Branch**: `feature/<story-id>-<short-slug>`. Target = default branch.
2. **Create Workitems in Betterplan**: via the MCP, using `type: workitem`, with `parentId` set to the Story. Set initial status to **Todo** (`todoDate` set).
   - **Level 2**: Each Workitem's description contains the **inline checklist** (substeps as Markdown checkboxes `- [ ]`).
   - **Level 3**: Each Workitem's title matches the proposal; no internal checklist needed.

If a Workitem already exists for a given scope (pre-created), the agent reuses it — update its status, don't create a duplicate.

(The Story is already on **Doing** with the `project:Agent` tag — both were set in Step 2.)

## Step 8 — Implement (autonomous loop, level-adapted)

### Level 1 (keine Workitems)

No Workitem loop. The agent simply implements the whole Story:

1. Write all code, tests, config across the whole Story's scope.
2. Commit (as one commit or logical sequence) and push to the feature branch.
3. Mark the corresponding ACs as done in the Story description (toggle `- [ ]` → `- [x]` as each is satisfied).

Then proceed to Step 10 (Finish).

### Level 2 (grob) — Incremental checklist tracking

For each coarse Workitem **in order**, follow this exact rhythm. The key rule: **update the board after EVERY substep — not in bulk at the end.**

1. **Move to Doing**: update the Workitem in Betterplan (`startedDate` or equivalent board-column date).

2. **Loop through each substep in the inline checklist.** For each substep:
   - **Implement**: write code, config, or docs needed for this single substep.
   - **Commit**: one commit per substep. Commit message should name the substep.
   - **Push** the commit to the feature branch.
   - **Update the checklist immediately** via the Betterplan MCP: read the current Workitem description, toggle exactly this one checkbox from `- [ ]` → `- [x]`, and write the updated description back.
   - **Do NOT** wait until later substeps are done. This toggle must happen **before** you start the next substep.
   - **Do NOT** batch several substeps into one update. Each substep produces a visible change on the board.
   - **Workitem stays on Doing** throughout — do NOT move it to Done until all substeps are complete.

3. **Mark the AC(s)** this coarse Workitem covers as done in the Story description (toggle `- [ ]` → `- [x]`) — only if fully satisfied by the completed substeps.

4. **Move to Done**: update the Workitem in Betterplan (`doneDate`).

After each Workitem, reflect progress: if at least one substep is Done and others remain, the Workitem stays at Doing. The human can open the Workitem in the board at any time and see exactly which substeps are done and which remain.

### Level 3 (volles Detail)

For each Workitem **in order**:

1. **Move to Doing**: update the Workitem in Betterplan.
2. **Implement**: write code, tests, config needed to satisfy the linked AC(s).
3. **Commit**: one commit per Workitem. Commit message:
   ```
   <Workitem title>

   Story: BP-123
   Workitem: <Workitem ID or title>
   AC: <which AC this addresses, if applicable>
   ```
4. **Push** the commit to the feature branch.
5. **Mark the AC(s)** in the Story description (`- [ ]` → `- [x]`).
6. **Move to Done**: update the Workitem in Betterplan (`doneDate`).

### AC-update discipline (all levels)

- Mark an AC as done (`- [x]`) **only when it is truly satisfied** by the code just committed — not pre-emptively.
- If a Workitem covers multiple ACs, mark all of them.
- If a Workitem only partially satisfies an AC, **do not mark it**. The AC stays open until the Workitem (or a later one) fully satisfies it.
- Never remove or re-order ACs in the description. Only toggle the checkbox.

## Step 9 — Error handling

If a Workitem **cannot be completed** (test fails persistently, AC is not implementable as described, external dependency is missing, ambiguity the agent cannot resolve):

1. **Stop immediately**. Do not skip, retry, or work around silently.
2. **Move the failing Workitem back to Todo** — undo the in-progress status in Betterplan (for Level 1: note the failure point; there is no Workitem to roll back).
3. **Move the parent Story back to Todo** — reset `startedDate`, leave `todoDate` set.
4. **Post a comment** on the Story (via the Betterplan MCP) with:
   - Which Workitem/step failed and why.
   - What was tried.
   - Suggested next step for the human (fix the AC, provide credentials, unblock a dependency, etc.).
5. **Signal in chat**: describe the failure clearly.
6. **Leave the `project:Agent` tag in place** — the human decides whether to remove it (abandon the Story) or fix the issue and say "mach weiter".
7. **Do not start the next Story** — wait for human input.

The agent also stops on:
- **Human says "stopp" / "halt" / "pause"** at any point → same procedure: Workitems stay where they are, comment logged, wait.
- **Iteration ends** while working → the agent finishes the **current Workitem and Story** (the one it started), then stops. It will not pick up the next Story until the next iteration begins.
- **Branch conflict / push rejected** → report the conflict, stop, let the human resolve.

## Step 10 — Finish the Story

When all implementation is complete (all Workitems at Done for levels 2/3, or full implementation committed for level 1):

1. **Merge the branch**: squash-merge or rebase-merge the feature branch into the default branch. Push.
2. **Move Story to Done**: set `doneDate` on the Story in Betterplan.
3. **Remove `project:Agent` tag**: the Story is no longer agent-assigned.
4. **Optional activity comment**: post a summary (optional, follow the *Activity comments* rules from `betterplan-workflow`): number of Workitems, branch name, merge commit hash.
5. **Tell the human**: "Story BP-123 is done, branch merged, tag removed."
6. **Go to next Story**: scan again (Step 1) for the next `project:Agent`-tagged Story in a current iteration. If none remain, report "All agent stories implemented."

### Level-1 variation
For Level 1 (no Workitems): there are no Workitems to summarise. Just note the branch name and merge commit. The Story went directly from Doing → Done with implementation on the branch.

## Manual tag assignment vs. agent-set tag

There is exactly one flow for assigning a Story to the agent:

| Action | Who | Effect |
|---|---|---|
| Add `project:Agent` tag | Human | Story is queued for the agent on next "mache deine Arbeit" |
| Remove `project:Agent` tag | Human or Agent (on completion) | Story is no longer assigned to the agent |
| Set Story to Doing | Agent (Step 2) | Board reflects active work immediately |
| Add `project:Agent` tag | Agent (Step 2, if not already present) | Story is tagged as agent-active |
| Remove `project:Agent` tag | Agent (Step 10, on completion) | Story is no longer agent-assigned |
| Set Story to Done | Agent (Step 10) | Board reflects completion |

The agent **adds** the tag when it starts working on a Story (Step 2) and **removes** it when the Story is done (Step 10). A human can also pre-add the tag to queue a Story for the next "mache deine Arbeit".

## Interaction with `project:Agent` across sessions

- If the agent is interrupted (session ends, tool failure), it **must read the current state on next startup**: check which Stories have the tag, which have Workitems in Todo/Doing/Done, what branch exists, and resume from where it left off. Do not re-propose the plan on existing Workitems.
- The human may **add more Workitems mid-implementation** (via Betterplan UI or `betterplan-create-workitem`). The agent detects new Workitems when it scans for the next one — add them to the queue in priority order.
- The human may **remove the `project:Agent` tag** mid-implementation → the agent finishes the current Workitem, then stops. The Story stays at its current state (no automatic rollback). The human can re-add the tag later to resume.

## What this skill does NOT do

- **Does not do Discovery** — the Story must be Ready before the tag goes on. Use `betterplan-create-story` to refine Idea → Draft → Ready.
- **Does not create Epics, Initiatives, or new Stories** — it only implements existing ones.
- **Does not manage iterations** — it only checks if a Story is in a current iteration. Creating / closing iterations is out of scope.
- **Does not deploy** — merging the branch is the final step. Deployment to staging/production is handled by the team's CI/CD pipeline or `betterplan-deploy` (future skill).
- **Does not replace the team** — the agent works autonomously within a confirmed plan, but the human owns the Story Map, priorities, iteration planning, and final review of the merged code.

## References

Workitem structure follows the conventions of `betterplan-create-workitem`: each Workitem is a concrete action, no story points, parent is the Story, bug reporting uses `isBug: true`. Shared conventions (maturity, open/closed, content separation, activity comments) are defined in `betterplan-workflow`.