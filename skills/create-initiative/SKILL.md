---
name: create-initiative
description: >
  This skill should be used when the user wants to create or phrase a Betterplan
  Initiative — a large goal that sets direction. Triggers include "create an
  initiative", "add a new initiative", "what's our goal for…", or describing a
  big outcome that is too large to build directly. If it is unclear whether the
  request is an Initiative, Epic, or Story, use the betterplan-workflow skill
  first to classify.
metadata:
  version: "0.1.0"
---

# Create a Betterplan Initiative

An Initiative is a **large goal that sets direction**. It is structure on the Story Map and is never implemented directly — Epics underneath it carry the steps. Data model: `type: initiative`.

For shared rules, follow the `betterplan-workflow` skill — in particular *Discovery is a dialogue* (proportional scale: Initiative = one or two Why-questions, no full Why/What/How loop), *Resuming refinement of an existing item*, *Creating an item: MCP first, Markdown fallback* (including the pre-create confirmation rule), and *Content separation* (be specific, no tag-mirroring). Initiatives are structure, so they have **no maturity level, no story points, and no acceptance criteria**.

## When something is an Initiative

- It expresses an outcome or direction, not a task.
- It is too big to build in one go; it needs several Epics to be realized.
- It would still make sense as a heading a year from now.

If it is actually a concrete buildable thing, it is a Story. If it is a single step toward the goal, it is an Epic.

## How to write it

1. **Phrase it as an outcome, not an activity.** Prefer "Customers can self-serve returns" over "Build a returns portal".
2. **Clarify the goal (optional, one or two questions).** If the goal is still vague ("increase conversion", "better onboarding"), ask one open question — typically *who benefits* and *why now* — and capture the answer plus the in/out-of-scope boundary as a short notes block in chat (2–3 lines, in the user's language). This is the Initiative-scale equivalent of the Story canvas; do not run the full Why/What/How loop. Apply the *one open question per beat* rule from `betterplan-workflow` > *Discovery is a dialogue*.
3. **Keep it goal-level.** No implementation detail, no acceptance criteria.
4. **Make the value explicit.** Why does this goal matter, for whom? Use the concrete audience from the clarify step — not a generic "the user" (see *Content separation > Be specific, not generic* in `betterplan-workflow`).
5. **Title**: short, outcome-oriented, no verbs like "implement/build".
6. **Keep the description to the goal itself.** The Epics beneath it live in the map's structure — do not name them in the description.

## Quality checks (classification, not description)

- Reads as a direction, not a to-do.
- Cannot be "done" by a single team in a single iteration.
- Big enough to need more than one step (otherwise it may be an Epic or a Story).

## Resume an existing Initiative

When invoked on an Initiative that already exists, follow *Resuming refinement of an existing item* in `betterplan-workflow`: read the current `title` and `description`, summarise in one line ("Aktueller Stand: Outcome formuliert, Wer-profitiert noch unscharf"), ask the user what to tighten this session, and refine only that. Do not start from a blank page.

## Create it (MCP or Markdown)

Follow the *Creating an item: MCP first, Markdown fallback* rule in `betterplan-workflow` — including the **pre-create confirmation**: show the proposed Initiative (title + 1–3 sentence description) in chat first and ask *"Soll ich diese Initiative so anlegen?"* before any MCP call or Markdown output. Never act in the same turn you first show the proposal.

If the Betterplan MCP is available, create the Initiative via its tool with `type: initiative` (content → `title` + `description`). Otherwise output the Markdown below.

Content only — title and description, no type/parent/meta (those are fields):

```
# <Initiative title>

<1–3 sentences: the goal, who it serves, and why it matters.>
```

After creating it, offer to break it into Epics (the steps toward the goal) with the `create-epic` skill.
