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

For shared rules (maturity, open/closed, output format), follow the `betterplan-workflow` skill. Initiatives are structure, so they have **no maturity level, no story points, and no acceptance criteria**.

## When something is an Initiative

- It expresses an outcome or direction, not a task.
- It is too big to build in one go; it needs several Epics to be realized.
- It would still make sense as a heading a year from now.

If it is actually a concrete buildable thing, it is a Story. If it is a single step toward the goal, it is an Epic.

## How to write it

1. **Phrase it as an outcome, not an activity.** Prefer "Customers can self-serve returns" over "Build a returns portal".
2. **Keep it goal-level.** No implementation detail, no acceptance criteria.
3. **Make the value explicit.** Why does this goal matter, for whom?
4. **Title**: short, outcome-oriented, no verbs like "implement/build".
5. **Keep the description to the goal itself.** The Epics beneath it live in the map's structure — do not name them in the description.

## Quality checks (classification, not description)

- Reads as a direction, not a to-do.
- Cannot be "done" by a single team in a single iteration.
- Big enough to need more than one step (otherwise it may be an Epic or a Story).

## Create it (MCP or Markdown)

Follow the "Creating an item: MCP first, Markdown fallback" rule in the `betterplan-workflow` skill. If the Betterplan MCP is available, create the Initiative via its tool with `type: initiative` (content → `title` + `description`). Otherwise output the Markdown below.

Content only — title and description, no type/parent/meta (those are fields):

```
# <Initiative title>

<1–3 sentences: the goal, who it serves, and why it matters.>
```

After creating it, offer to break it into Epics (the steps toward the goal) with the `create-epic` skill.
