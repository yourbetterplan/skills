---
name: betterplan-workflow
description: >
  This skill should be used to classify a piece of work into the correct
  Betterplan building block and to understand the Betterplan method. Use it
  when the user is unsure "what type" something is, says things like "is this
  an epic or a story", "how should I structure this", "what goes in the
  backlog", "help me plan in Betterplan", or when any create-* Betterplan skill
  needs the shared rules (maturity levels, open/closed, story points, output
  format). It routes the request to create-initiative, create-epic,
  create-story, or create-workitem.
metadata:
  version: "0.1.0"
---

# Betterplan workflow & classification

This skill is the shared brain for working in Betterplan. It does two things:

1. Decide which building block a piece of work should become.
2. Hold the conventions that every `create-*` skill relies on, so they stay small and consistent.

Write all output in the language the user is writing in. Default to English. Format every artifact as Markdown.

## The four phases

Betterplan moves through four phases, repeatedly (this is the PDCA loop):

- **Scope** — set goals and structure the endeavor (view: Story Map).
- **Prepare** — prioritize and think work through until it is ready (view: Backlog).
- **Build** — execute in fixed iterations (view: Iteration Board).
- **Insight** — keep the overview, see where things stand and when they finish (view: Delivery Timeline).

The building blocks this plugin creates live mostly in Scope (structure) and Prepare/Build (implementation).

## The building blocks

There are two groups. **Structure** blocks are never implemented directly — they organize the path. **Implementation** blocks are the work that actually gets built.

| Block | Group | One-line purpose |
|---|---|---|
| Initiative | Structure | A large goal that sets direction. Not worked on directly. |
| Epic | Structure | A sub-goal under an initiative: a step the user takes toward the goal. |
| User Story | Implementation | An option for *how* a user takes a step. Concrete user value. |
| Project Story | Implementation | Cross-cutting work with no direct user value (organizational, hardware, docs, decisions/events). |
| Devteam Story | Implementation | Cross-cutting technical work (refactoring, build pipeline, technical debt). |
| Workitem | Implementation detail | Smallest unit. Belongs to a Story, used only on the Iteration Board to coordinate delivery. No story points. |

## Classification — pick the right type

Walk this decision in order and stop at the first match:

1. **Does it set overall direction and is too big to build directly?** → Initiative. (e.g. "Increase self-service checkout adoption")
2. **Is it a step the user takes toward a goal, made of several options/variants?** → Epic. (e.g. "Search", "Checkout")
3. **Is it concrete, buildable, and does it deliver value to a user/customer?** → User Story. (e.g. "Text search with autocomplete")
4. **Is it needed but delivers no direct user value?**
   - Organizational, contractual, hardware, documentation, or recording a decision/event → Project Story.
   - Technical and internal to the dev team (refactoring, CI/CD, tech debt) → Devteam Story.
5. **Is it a small task that only helps coordinate the delivery of one Story inside an iteration?** → Workitem.

Edge cases:

- "Bug / rework" on a Story: do **not** create a new Story. Add a **Workitem with `isBug = true`** to the affected Story (use `create-workitem`). The backend handles the rest — reopening the Story and the bug rollup. Knowledge stays on the Story.
- An unplanned task with no home Story → Devteam Story (technical cause) or Project Story (organizational).
- If an Epic turns out to have only one way to do it, it may simply be a User Story. If a User Story keeps growing options, it may be an Epic. Structure is allowed to change.

When the type is decided, hand off. The `type` column is the value the future MCP expects (see `references/data-model.md`):

| Block | `type` | Skill |
|---|---|---|
| Initiative | `initiative` | `create-initiative` |
| Epic | `epic` | `create-epic` |
| User Story | `story` | `create-story` |
| Project Story | `project` | `create-story` |
| Devteam Story | `dev` | `create-story` |
| Workitem | `workitem` | `create-workitem` |

## Shared conventions

Every `create-*` skill follows these. They are defined once here.

### Maturity levels (only for Stories)

An open Story moves through six states across two tracks. Initiatives and Epics are structure and do not carry these.

- Discovery track: **Idea** → **Draft** → **Ready**
- Delivery track: **Todo** → **Doing** → **Done**
- Then **Closed** (complete, whether delivered or deliberately stopped).

A newly created Story starts at **Idea** unless the user says otherwise. Discovery and Delivery stay inside one Story — never split clarification and implementation into separate items.

### Open vs Closed

Every Story is Open (still in progress, anywhere from Idea to Done) or Closed (finished or deliberately stopped). Closing a low-value Story early is a good outcome, not a failure (~20% of stories carry ~80% of value).

### Estimation (Stories only)

Stories are estimated in **Story Points**, used together with team Velocity to forecast the Delivery Timeline. Do not invent a precise number. Suggest a relative size only when asked, and note that Betterplan auto-fills unestimated stories with the team median. Workitems have **no** story points.

### Output format

Produce **content only** — exactly what goes into the item's title and description in Betterplan. Do **not** emit meta or structural fields: no type, no parent, no maturity level, no story points, no dependency lines. Those are set on the item inside Betterplan and would be noise in the text.

Default shape (skills adapt it per type):

```
# <Title>

<Description / intent, in plain prose>

### Acceptance criteria        (Stories only)
- [ ] ...
```

Keep it clean and paste-ready. If type, parent, or relationships matter, mention them to the user in the chat reply around the artifact, not inside the pasteable block.

See `references/glossary.md` for term definitions, `references/method-deep-dive.md` for the full method, prioritization, and the Story Map layout, and `references/data-model.md` for the API/MCP data shape (the `type` enum, how maturity maps to date fields, and which fields are structure vs content).

## Future: Betterplan MCP

A Betterplan MCP server (OAuth) will let these skills read and write items directly in the app. It is not connected yet. Until then, produce Markdown artifacts for the user to paste in. When the MCP is available, the same classification and conventions apply — create items through the MCP tools instead of Markdown, mapping content to `title` + `description` and everything else to the fields documented in `references/data-model.md`.
