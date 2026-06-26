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

## Starting from a rough idea

Often the user does not arrive with a fully classified piece of work. They say "I just have an idea", "we should do something with X", "Idee: Y", or "what about Z?". When that happens, **do not start with a classification quiz**. The work is light, fast, and one-directional:

1. **Capture the idea as an Idea Story.** Default `type` is `story` with maturity tag `progress:idea`. Title = a short activity-form distillation of the user's sentence. Description: one line of intent (use the user-story form when it is already implicit; otherwise a plain intent sentence is fine).
2. **Propose where it belongs in the Story Map.** Look at existing Initiatives and Epics in the project. Suggest the most plausible parent (`parentId`) with one line of reasoning. If nothing fits, propose a new Initiative or Epic to host it, with one line of why.
3. **Ask the user to confirm or correct the placement.** One question, not a multi-choice list of all Initiatives. If the user corrects, just move it — no debate.
4. **Stop here unless the user wants more.** The idea is captured and placed. Further refinement (Draft, Ready) happens later via `create-story` — the user decides when.

Only step into the classification flow (next section) when the user explicitly wants to commit to a non-Story type, or when the idea is obviously not a Story (e.g. a clear large goal that asks for an Initiative). The user can always say "this is a <type>" and skip the on-ramp; take that at face value.

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

When the type is decided, hand off. The `type` column is the value used in the data model (see `references/data-model.md` for the mapping):

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

### Discovery is a dialogue, not a structure

The Discovery track (Idea → Draft → Ready) is not just three labels — it is a **conversation that takes time**. While a Story is in Discovery, the goal is shared understanding between user and assistant, not output volume. Rules every `create-*` skill follows:

- **Do not jump maturity in a single turn.** A Story does not move from Idea straight to Ready in one conversation. The minimum path is Idea → Draft → (further dialogue) → Ready, with the user explicitly confirming each transition. Stories that are obviously small and clear may run multiple gates back-to-back, but only when the user opts in.
- **Default refinement target = the next maturity step.** When the user says "refine this Story", default to bringing it one step up (Idea → Draft, Draft → Ready). The user can override by asking for multiple steps in one session, or for staying at the current step (just adding a detail).
- **Open questions block the next maturity.** A Story is not Ready while open questions stand. Either resolve them or convert them to explicitly accepted assumptions that the user confirms.
- **Prefer one open question per beat over a multi-choice salvo.** Multi-choice freezes the user into the assistant's option set; an open question invites the user's own framing. Multi-choice is fine when the user asks for options, or when the choice is genuinely categorical (e.g. selecting a type in Step 1 of `create-story`).
- **Refinement is pauseable and resumable.** The user can stop the dialogue at any time; the assistant lands the Story at the highest maturity whose minimum is actually satisfied, writes the current state into the description (open questions stay explicit), and on the next invocation reconstructs the canvas from the description plus activity log to resume from the unfinished gate.

These rules are operationalized in `create-story` Steps 3, 3a, and 3b. Other `create-*` skills follow the same spirit at their **proportional scale** — Initiatives and Epics are structure (no maturity levels), Workitems are coordination (no maturity, no discovery), so the dialogue shrinks accordingly:

| Concept | Story | Epic | Initiative | Workitem |
|---|---|---|---|---|
| Why-gate (persona + trigger + outcome) | full | one question: who takes this step, in what situation | one question: who benefits, why now | — |
| What-gate (rules + examples) | full, drives AC | name 1–2 variants / use cases the step must cover | scope boundaries (in / out) | — |
| How-gate (shape, options, trade-offs) | full | — (lives in child Stories) | — | — |
| Working surface | full canvas (Step 3a) | 3–4 line notes (Step-Shape) | 2–3 line notes (Goal + Why-it-matters) | none |
| One open question per beat | yes | yes | yes | yes (for the single bug clarification, if any) |
| Default refinement target | next maturity step | tighten the step description | tighten the goal statement | n/a — created ready or not at all |
| Pause / resume | maturity-aware (Step 3b) | save notes into description, resume from there | save notes into description, resume from there | n/a |

When a `create-*` skill is invoked on an item that already exists, it must read the current content first and resume from there (see *Resuming refinement of an existing item* below) — never start from a blank page.

### Resuming refinement of an existing item

When a `create-*` skill is invoked on an item that already exists, do **not** start from scratch:

1. **Read** the item's current state: `title`, `description`, tags / maturity (Stories only), and recent activity comments.
2. **Reconstruct** the working surface (full canvas for Stories, short notes for Epics / Initiatives) from what is already written.
3. **Show** the user a one-sentence summary of what you found: e.g. *"Aktueller Stand: Draft, 2 offene Fragen, fehlt für Ready: <X>."* — or for an Epic / Initiative *"Aktueller Stand: Step-Beschreibung steht, 1 Use-Case offen."*
4. **Ask** what the goal of *this* session is — one question. For Stories, the default target is the next maturity step (see *Discovery is a dialogue*). For Epics / Initiatives, the default is "tighten what is already there" unless the user names something else.
5. **Re-enter** the dialogue only on the parts that are still incomplete. Do not re-litigate points that were already settled.

For Stories this is operationalised in `create-story` Step 3b with maturity gates. For Epics and Initiatives the same spirit applies without maturity tags. For Workitems it does not apply — Workitems are mechanical break-downs and are not refined in dialogue.

### Open vs Closed

Every Story is Open (still in progress, anywhere from Idea to Done) or Closed (finished or deliberately stopped). Closing a low-value Story early is a good outcome, not a failure (~20% of stories carry ~80% of value).

### Estimation (Stories only)

Stories are estimated in **Story Points**, used together with team Velocity to forecast the Delivery Timeline. Do not invent a precise number. Suggest a relative size only when asked, and note that Betterplan auto-fills unestimated stories with the team median. Workitems have **no** story points.

### Content separation: Description vs AC vs Tags

Three layers, three jobs. Do not mix them.

| Layer | Job | Style |
|---|---|---|
| **Description** | What value, for whom, why now. The reader picks up the Story in 30 seconds. | Plain prose, user-story form by default ("Als …, will ich …, damit …"). Includes all the usual sections (Context, Acceptance criteria, Out of scope, Open questions) — see `create-story` Step 4. |
| **Acceptance criteria** | Observable states that must be true at the end. Live as a section inside the description. | Markdown checkboxes, behavior not pixels. 2–4 at Story level; finer detail belongs in Workitems. |
| **Tags** | Metadata labels for filtering and reporting. | Single words or short phrases ("Persistenz", "UI", "Audit"). |

Hard rules — generic (every `create-*` skill):

- **Tag content does not belong in the description.** Mirroring a tag (e.g. writing "Persistenz" into the description because there is a Persistenz tag) is not real content. Tags are labels for filtering; the description is content.
- **Be specific, not generic.** Avoid role labels that could be anyone ("Product Manager", "Developer", "the user"). Name the actual person, team, or situation — for Stories, carry the real persona from the Canvas Why-line; for Epics and Initiatives, name the concrete audience ("Customer Service team", "Stakeholder PMs in Reviews/Retros").
- **Context, not ceremony.** Every section of the description should teach or frame something the implementer needs. Cut anything that only restates what is already obvious from structure or tags.

Hard rules — Story-only:

- **AC do not encode UI / design decisions.** Grey font, specific icon, session vs persistent storage — those are decisions that live in the description's `## Context` section as named decisions with one line of rationale. AC say what behavior must hold.
- **AC are not implementation tasks.** "Implement X" is work, not a verifiable state. Phrase as the state that exists once the work is done.

A separate, longer implementation concept is **out of scope for this skill version**; the description is the only artifact produced by `create-story`. The concept document — its shape, who writes it, and when — will be defined in a later skill iteration. For now, the description must be precise enough that the later concept can be derived from it.

### Creating an item: MCP first, Markdown fallback

Before creating anything, check whether **Betterplan MCP tools are available** in the current session (tool names contain `betterplan`).

**Always confirm before creating.** In the turn *before* any create or update call (MCP or Markdown), show the full proposed artifact in chat — title, description / content, the intended `type`, the intended `parentId` (if any), and any maturity tag or `isBug` flag you plan to set. Ask explicitly, e.g.:

> *"Soll ich das jetzt so anlegen — als <type>, unter <parent>, mit Maturity <Idea | Draft | Ready>?"*

Never call the create / update tool, post a comment, or change a maturity tag in the **same turn** you first show the proposed content. The user must see what is going in and approve it. If the user replies with a change request, do not patch the proposed text silently — update the working surface (canvas for Stories, notes for Epics / Initiatives), re-derive the proposal, and show it again.

**If the Betterplan MCP is available**, create the item by calling its create tool — do not just print Markdown. Map:

- content → `title` + `description`
- everything else → arguments: `type` (use the mapping in the routing table / `references/data-model.md`), `parentId`, `releaseId`, `estimation`, maturity dates, `tags`, `isBug`.

The MCP describes its own tools and field names at runtime — follow those for exact arguments. After creating, confirm with a short chat summary (what was created, its type and parent). If a required argument is missing (e.g. the target project or parent), ask the user.

**If the MCP is not available**, fall back to a Markdown artifact the user can paste in. Output **content only** — title and description (plus acceptance criteria for Stories). Do **not** emit meta or structural fields (type, parent, maturity, story points, dependencies); mention those in the chat reply instead. Default shape (skills adapt it per type):

```
# <Title>

<Description / intent, in plain prose>

### Acceptance criteria        (Stories only)
- [ ] ...
```

Either way, the content is identical — only the delivery (MCP call vs Markdown) differs.

### Activity comments (optional, when substantial)

After creating or refining an item, posting an activity comment is **optional**. Post one only when the change was substantial — a maturity moved (Stories), a major scope decision was settled, a known open question was closed, or the parent placement changed. Skip the comment for typo fixes, formatting passes, or minor edits; the activity log already records field changes and an extra comment for those is noise.

When you do post one, write **content reflections**, not session minutes:

- Name the decisions reached ("Persistence per session, alternative user-setting compared in Context.").
- Name the open edges ("Still open: which data source for X.").
- Name the assumptions accepted ("User confirmed: only US customers in scope.").
- For Stories, mention the maturity reached ("Moved Idea → Draft; one more conversation on X to reach Ready.").

Avoid: *"We asked 4 questions, you answered Y, I wrote Z."* — everything visible in the activity log already.

This rule applies to every `create-*` skill at its scale: Stories get maturity-level reflections, Epics / Initiatives get scope-level reflections, Workitems normally get no comment (the checklist item itself is the signal).

See `references/glossary.md` for term definitions, `references/method-deep-dive.md` for the full method, prioritization, and the Story Map layout, and `references/data-model.md` for the conceptual mapping the MCP does not spell out (the `type` values, how maturity maps to date fields, content vs metadata, the bug rule).

## The Betterplan MCP

The Betterplan MCP server (OAuth) lets these skills read and write items directly in the app. It is connected separately by the user, not bundled in this plugin. When its tools are present, prefer them (see "Creating an item" above); when they are not, fall back to Markdown. The MCP describes its tools, fields, and arguments itself, so rely on those at call time for exact field names; use `references/data-model.md` only for the conceptual mapping (which `type` to use, how maturity and bugs work).
