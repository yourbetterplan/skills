---
name: betterplan-implement-story
description: >
  This skill should be used to implement Betterplan Stories using a coding agent.
  The agent picks up Stories tagged with "Agent" that are in a current iteration,
  proposes Workitems, implements them autonomously (one commit per Workitem,
  one branch per Story), and updates the Iteration Board in real time. Triggers
  include "mache deine Arbeit", "implement all agent stories", or when a human
  manually adds the "Agent" tag to a Story in a current iteration.
metadata:
  version: "0.1.0"
---

# Implement a Story with the coding agent

This skill turns a **Ready Story in a current iteration** into implemented, committed, and board-tracked work — autonomously.

The flow for the human is short:
1. Bring a Story to **Ready** (via `betterplan-create-story`).
2. Put it in a **current iteration**.
3. Add the tag **`project:Agent`**.
4. Say **"mache deine Arbeit"**.

The agent does the rest: propose Workitems → confirm → branch → commit per Workitem → board updates → merge → done.

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

## Step 2 — Read & analyse the Story

The agent reads the full Story content:

- `title` and `description` (Why, Context, Acceptance Criteria, Out of scope, Open questions)
- The current maturity level
- The parent Epic (for context)
- Any existing Workitems (if someone pre-created them)

If the maturity is not **Ready**, the agent does not proceed — inform the human:

> *"Story BP-123 is tagged Agent but is at Draft maturity. Bring it to Ready first via betterplan-create-story."*

## Step 3 — Propose Workitems

The agent derives a Workitem plan from the Story, using the same logic as `betterplan-create-workitem`:

1. Each **Acceptance Criterion** becomes at least one Workitem.
2. Add implementation steps the team needs: backend, frontend, tests, review, deploy — only those that apply.
3. **Link each Workitem to one or more ACs** from the Story — note the AC reference in the proposal. This mapping drives both implementation and later AC-tracking.
4. Order them so the Story can reach Done sequentially.
5. Keep each Workitem small enough to finish in roughly a day.

**Show the proposal in chat** with the working title of each Workitem and which AC(s) it covers:

```
### Implementierungsplan für "BP-123 — Text-Suche mit Autocomplete"

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

If the Story already has Workitems (pre-created by the human or a previous session), the agent reads them and proposes the implementation sequence — the human may still adjust or confirm as-is.

## Step 4 — Confirm the plan

The human either:

- Says **"los"** / **"go"** / **"ja"** → proceeds to Step 5.
- Requests changes → update the proposal in chat, re-show, wait for confirmation.
- Cancels → stop, leave Story and tag untouched.

**One confirmation for the whole list.** Once confirmed, the agent works autonomously through all Workitems. No per-Workitem gate unless an error occurs (see Step 7).

## Step 5 — Set up & create Workitems

The agent executes the plan setup:

1. **Create the Branch**: `feature/<story-id>-<short-slug>` (e.g. `feature/bp-123-text-search`). Target branch = the repo's default branch (usually `main` or `master`).
2. **Create Workitems in Betterplan**: via the MCP, using `type: workitem`, with `parentId` set to the Story. Set initial status to **Todo** (`todoDate` set). Each Workitem's title matches the proposal.
3. **Set Story to Doing**: set `startedDate` on the Story, so the Iteration Board reflects active work.
4. **Tag `project:Agent` remains** on the Story — it was set by the human and stays until done.

If a Workitem already exists for a given AC (pre-created), the agent reuses it — update its status, don't create a duplicate.

## Step 6 — Implement (autonomous loop)

For each Workitem **in order**:

1. **Move to Doing**: update the Workitem in Betterplan — set the field that corresponds to "Doing" on the Iteration Board (typically `startedDate` or an equivalent board-column date, following what the MCP exposes).
2. **Implement**: write code, tests, configuration, or documentation needed to satisfy the AC(s) this Workitem covers. The agent operates within its normal capabilities (editing files, running commands, reading documentation).
3. **Commit**: create one commit per Workitem. Commit message format:
   ```
   <Workitem title>
   
   Story: BP-123
   Workitem: <Workitem ID or title>
   AC: <which AC this addresses, if applicable>
   ```
4. **Push** the commit to the feature branch.
5. **Mark the corresponding AC(s) in the Story description**: read the current Story description, find the AC checkbox(es) linked to this Workitem, change `- [ ]` to `- [x]`. Update the Story via the MCP (`description` field).
6. **Move to Done**: update the Workitem in Betterplan — set the "Done" column date (`doneDate`). (Workitems have no Closed state — Done is terminal.)

After each Workitem, reflect the progress on the parent Story: if at least one Workitem is Done and others remain, the Story stays at Doing.

**Repeat** until all Workitems are Done.

### Workitem content & scope

- A Workitem is a **concrete action** ("Add /search endpoint", "Write tests for empty query").
- It covers **one logical step**, not cross-cutting work (cross-cutting concerns → separate Devteam/Project Story).
- If a Workitem turns out too large during implementation (roughly >1 day), the agent may split it into two Workitems — but must **propose the split in chat** and await confirmation before continuing.

### AC-update discipline

- Mark an AC as done (`- [x]`) **only when it is truly satisfied** by the code just committed — not pre-emptively.
- If a Workitem covers multiple ACs, mark all of them.
- If a Workitem only partially satisfies an AC, **do not mark it**. The AC stays open until the Workitem (or a later one) fully satisfies it.
- Never remove or re-order ACs in the description. Only toggle the checkbox.

## Step 7 — Error handling

If a Workitem **cannot be completed** (test fails persistently, AC is not implementable as described, external dependency is missing, ambiguity the agent cannot resolve):

1. **Stop immediately**. Do not skip, retry, or work around silently.
2. **Move the failing Workitem back to Todo** — undo the in-progress status in Betterplan.
3. **Move the parent Story back to Todo** — reset `startedDate`, leave `todoDate` set.
4. **Post a comment** on the Story (via the Betterplan MCP) with:
   - Which Workitem failed and why.
   - What was tried.
   - Suggested next step for the human (fix the AC, provide credentials, unblock a dependency, etc.).
5. **Signal in chat**: describe the failure clearly.
6. **Leave the `project:Agent` tag in place** — the human decides whether to remove it (abandon the Story) or fix the issue and say "mach weiter".
7. **Do not start the next Story** — wait for human input.

The agent also stops on:
- **Human says "stopp" / "halt" / "pause"** at any point → same procedure: Workitems stay where they are, comment logged, wait.
- **Iteration ends** while working → the agent finishes the **current Workitem and Story** (the one it started), then stops. It will not pick up the next Story until the next iteration begins.
- **Branch conflict / push rejected** → report the conflict, stop, let the human resolve.

## Step 8 — Finish the Story

When all Workitems are Done:

1. **Merge the branch**: squash-merge or rebase-merge the feature branch into the default branch. Push.
2. **Move Story to Done**: set `doneDate` on the Story in Betterplan.
3. **Remove `project:Agent` tag**: the Story is no longer agent-assigned.
4. **Optional activity comment**: post a summary (optional, follow the *Activity comments* rules from `betterplan-workflow`): number of Workitems, branch name, merge commit hash.
5. **Tell the human**: "Story BP-123 is done, branch merged, tag removed."
6. **Go to next Story**: scan again (Step 1) for the next `project:Agent`-tagged Story in a current iteration. If none remain, report "All agent stories implemented."

## Manual tag assignment vs. agent-set tag

There is exactly one flow for assigning a Story to the agent:

| Action | Who | Effect |
|---|---|---|
| Add `project:Agent` tag | Human | Story is queued for the agent on next "mache deine Arbeit" |
| Remove `project:Agent` tag | Human or Agent (on completion) | Story is no longer assigned to the agent |
| Set Story to Doing | Agent (after plan confirmed) | Board reflects active work |
| Set Story to Done | Agent (after all Workitems done + merge) | Board reflects completion |

The agent **never** adds the `project:Agent` tag itself. It only removes it on completion. The human controls the queue by adding and removing the tag.

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