---
name: create-epic
description: >
  This skill should be used when the user wants to create a Betterplan Epic — a
  sub-goal under an Initiative that represents a step the user takes toward the
  goal. Triggers include "create an epic", "add an epic", "break this initiative
  into steps", or naming a step like "Search" or "Checkout". If it is unclear
  whether the request is an Epic, Initiative, or Story, use the
  betterplan-workflow skill first to classify.
metadata:
  version: "0.1.0"
---

# Create a Betterplan Epic

An Epic is a **step the user takes toward a goal**. It is structure on the Story Map between Initiatives (goals) and Stories (options/work). Epics are not implemented directly — the User Stories underneath them are. Data model: `type: epic`.

For shared rules, follow the `betterplan-workflow` skill. Epics are structure, so they have **no maturity level, no story points, and no acceptance criteria**.

## When something is an Epic

- It is a step in the user's journey, not the whole goal and not a single buildable option.
- It groups several Stories that are different ways to accomplish the step.
- Example: under the Initiative "Find products fast", the Epic "Search" groups the Stories "Basic text search", "Search with autocomplete", "Filter options".

If it has only one obvious implementation, it may just be a User Story. If it expresses overall direction, it is an Initiative.

## How to write it

1. **Name the step, not the feature.** Use the user's verb where natural ("Search", "Check out", "Onboard").
2. **Keep it option-agnostic.** Do not bake in one solution; the Stories carry the options.
3. **Keep the description to the step itself.** The parent Initiative and the child Stories live in the map's structure — do not name them in the description.

## Quality checks (classification, not description)

- Reads as a step in a journey, not the whole goal and not a single buildable option.
- Could plausibly hold more than one option/variant (otherwise it may be a Story).

## Output template

Content only — title and description, no type/parent/meta (those are set in Betterplan):

```
# <Epic title>

<1–2 sentences: the step in the user's journey this represents.>
```

After producing it, offer to write the Stories for this step with the `create-story` skill.
