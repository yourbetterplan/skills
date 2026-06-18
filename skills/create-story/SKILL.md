---
name: create-story
description: >
  This skill should be used when the user wants to create a Betterplan Story —
  a User Story (user value), a Project Story (organizational, no user value), or
  a Devteam Story (technical, no user value). Triggers include "write a user
  story", "create a story", "add a project story", "add a devteam story",
  "turn this into a backlog item", or describing concrete work to be built. If
  the right story type is unclear, classify with the betterplan-workflow skill
  first.
metadata:
  version: "0.1.0"
---

# Create a Betterplan Story

Stories are the **implementation** blocks that live in the Backlog. There are three types. They share the same mechanics and differ in purpose and how they are written. Each maps to a `type` value in the Betterplan data model (used by the future MCP):

- **User Story** (`type: story`) — concrete user/customer value. → see `references/user-story.md`
- **Project Story** (`type: project`) — needed but no direct user value: organizational, hardware, docs, recording decisions/events. → see `references/project-story.md`
- **Devteam Story** (`type: dev`) — cross-cutting technical work internal to the team: refactoring, build pipeline, tech debt. → see `references/devteam-story.md`

## Step 1 — confirm the type

If the type is given, use it. If not, ask one question or apply this quick test:

- Does a user/customer directly benefit? → **User Story**.
- No user value, and it is organizational/contractual/informational? → **Project Story**.
- No user value, and it is technical and internal to the dev team? → **Devteam Story**.

When still unsure, use the `betterplan-workflow` skill to classify, then return here.

## Step 2 — apply the shared rules

From the `betterplan-workflow` skill:

- New Stories start at maturity **Idea** unless told otherwise. Keep Discovery and Delivery in one Story; never split clarification from implementation.
- Estimate in **Story Points** only when asked; otherwise leave it out and note Betterplan auto-fills the team median.
- A Story can be Closed in any phase — closing low-value work early is good.

## Step 3 — write it well

This quality bar (INVEST-style) is the target for a **Ready** Story. An Idea or early Draft need not meet it yet — fill in detail as the Story matures (see "Match depth to maturity").

- **Independent** enough to build on its own.
- **Negotiable** — describes intent, not a rigid spec.
- **Valuable** — the value is explicit (to a user, or to the project/team for Project/Devteam Stories).
- **Estimable** — small and clear enough to size.
- **Small** — fits within an iteration; if not, split it (see method-deep-dive in betterplan-workflow).
- **Testable** — has acceptance criteria you could check.

Read the matching `references/<type>.md` for the type-specific template, voice, and examples, then produce the Markdown.

## Output shape

Output **content only** — what goes into the Story's title and description. Do **not** include type, parent epic, maturity, story points, or dependency lines in the pasteable block; those are set on the Story inside Betterplan. If type or relationships matter, say so in your chat reply around the artifact.

A Story description **may** use these sections (in this order). Everything is optional — see "Match depth to maturity" below. Read the matching `references/<type>.md` for the type-specific voice and a worked example.

```
# <Title>

<1–2 sentence summary of the story. For a User Story:
"As a <role>, I want <capability> so that <benefit>.">

## Context
<Helpful background and additional info: why this matters now, relevant
decisions, links, constraints. Keep it to what helps someone pick the story up.>

## Acceptance criteria
- [ ] <a checkable state — see rules below>
- [ ] <a checkable state>

## Out of scope
- <what is explicitly NOT part of this story, to set a clear boundary>

## Open questions
- <unresolved questions that still need an answer>
```

### Match depth to maturity

All information is optional. How much a Story is filled in depends on its maturity — do not force the full template onto an early Story, and never pad with placeholder text. Fill in only what is actually known.

- **Idea**: usually just a title and maybe a one-line summary. Often the only other content is a few `Open questions`. That is fine and expected.
- **Draft**: the Story is being explored, so it fills up — add `Context`, sketch `Acceptance criteria`, capture `Out of scope` and `Open questions` as they surface.
- **Ready**: fully thought through — `Acceptance criteria` are complete and checkable, `Out of scope` is clear, open questions are resolved (or moved elsewhere).

If you do not know the Story's maturity, ask, or default to a light Idea-level draft and offer to flesh it out.

### Acceptance criteria rules

- Use Markdown checkboxes (`- [ ]`).
- Phrase each one as a **state that can be checked true or false**, not a task to do.
  - Good: `- [ ] Suggestions appear after the user types at least 2 characters.`
  - Avoid: `- [ ] Implement autocomplete.` (that is work, not a verifiable state)
- One condition per box. Cover the happy path plus the important empty/error states.
- Given/When/Then is fine when it helps express a behavioral state.

After producing a Story, offer to break it into Workitems with the `create-workitem` skill once it is Ready for an iteration.
