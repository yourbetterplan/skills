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

An Epic is a **step in the business process** that fulfils an Initiative's goal. It is structure on the Story Map between Initiatives (the goal) and Stories (the tools or options that fulfil the step). Epics are not implemented directly — the User Stories underneath them are the tools that get built. Data model: `type: epic`.

For shared rules, follow the `betterplan-workflow` skill — in particular *Discovery is a dialogue* (proportional scale: Epic = one or two clarifying questions, no full Why/What/How loop), *Resuming refinement of an existing item*, *Creating an item: MCP first, Markdown fallback* (including the pre-create confirmation rule), and *Content separation* (be specific, no tag-mirroring). Epics are structure, so they have **no maturity level, no story points, and no acceptance criteria**.

## When something is an Epic

- It is a step in the user's journey, not the whole goal and not a single buildable option.
- It groups several Stories that are different ways to accomplish the step.
- Example: under the Initiative "Find products fast", the Epic "Search" groups the Stories "Basic text search", "Search with autocomplete", "Filter options".

If it has only one obvious implementation, it may just be a User Story. If it expresses overall direction, it is an Initiative.

## How to write it

1. **Name the step, not the feature.** Use the user's verb where natural ("Search", "Check out", "Onboard").
2. **Clarify the step (optional, one or two questions).** If the step is not yet obvious, ask one open question — typically *who* takes this step in *what* situation — and capture the answer plus 1–2 use cases or variants the step must cover as a short notes block in chat (3–4 lines, in the user's language). This is the Epic-scale equivalent of the Story canvas; do not run the full Why/What/How loop here. Apply the *one open question per beat* rule from `betterplan-workflow` > *Discovery is a dialogue*.
3. **Keep it option-agnostic.** Do not bake in one solution; the Stories carry the options.
4. **Keep the description to the step itself.** The parent Initiative and the child Stories live in the map's structure — do not name them in the description.

## Quality checks (classification, not description)

- Reads as a step in a journey, not the whole goal and not a single buildable option.
- Could plausibly hold more than one option/variant (otherwise it may be a Story).

## Resume an existing Epic

When invoked on an Epic that already exists, follow *Resuming refinement of an existing item* in `betterplan-workflow`: read the current `title` and `description`, summarise the state in one line ("Aktueller Stand: Step-Beschreibung steht, 1 Use-Case noch offen"), ask the user what the goal of this session is, and only refine the parts that are still loose. Do not start from a blank page.

## Create it (MCP or Markdown)

Follow the *Creating an item: MCP first, Markdown fallback* rule in `betterplan-workflow` — including the **pre-create confirmation**: show the proposed Epic (title + 1–2 sentence description + intended `parentId`) in chat first and ask *"Soll ich diesen Epic so anlegen?"* before any MCP call or Markdown output. Never act in the same turn you first show the proposal.

If the Betterplan MCP is available, create the Epic via its tool with `type: epic` and `parentId` set to its Initiative (content → `title` + `description`). Otherwise output the Markdown below.

Content only — title and description, no type/parent/meta (those are fields):

```
# <Epic title>

<1–2 sentences: the step in the user's journey this represents.>
```

After producing it, offer to write the Stories for this step with the `create-story` skill.
