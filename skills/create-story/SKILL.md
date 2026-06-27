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

Stories are the **implementation** blocks that live in the Backlog. A Story is a **tool or option that fulfils a step of the business process** described by its parent Epic. The tool can be a person, a service, or a system — not every Story has to be software.

There are three types. They share the same mechanics and differ in purpose and how they are written. Each maps to a `type` value in the Betterplan data model (used when creating via the MCP):

- **User Story** (`type: story`) — a tool / option with concrete user value (a feature, an automation, a service the user touches). → see `references/user-story.md`
- **Project Story** (`type: project`) — a tool needed for the process but with no direct user value: organizational (a contract, a role, a process), hardware, docs, recording decisions/events. → see `references/project-story.md`
- **Devteam Story** (`type: dev`) — a technical tool internal to the team: refactoring, build pipeline, tech debt. → see `references/devteam-story.md`

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

## Step 3 — discovery dialogue (slow down before writing)

This is the heart of the skill. **Do not write the Story description, acceptance criteria, or any concept document until this loop has settled.** Most Stories arrive as an Idea or rough Draft. Your job here is to **talk**, not to ship.

The loop has three gates. Walk them **in order**; do not jump ahead, even if you think you already know the answer.

1. **Why-gate — value & trigger.** Confirm the persona (one concrete person, not a role label), the concrete trigger moment ("in which review / meeting / situation does this hurt?"), and the outcome the person wants. Mirror it back in one sentence and ask the user to confirm before moving on.
   - *Optional shortcut for Project / Devteam Stories* when the trigger is obvious (e.g. "security patch", "CI is broken", "regulatory deadline"). State the trigger in one sentence, ask the user to confirm, then move on. Do not skip the user confirmation.
2. **What-gate — rules & examples.** For every rule the Story will need, ask the user for at least one concrete positive example and one counter-example or out-of-scope case. Capture these in the canvas (see Step 3a). A rule with no example is not a rule yet — keep asking. Move on only when the user confirms the rule set feels complete.
3. **How-gate — shape & constraints.** Only now discuss UI location, persistence, data model, classification labels, visual treatment. Surface **options with trade-offs** ("Vorschlag A … / Alternative B …, trade-off …"), do not declare decisions.

### Question discipline

Apply the *Discovery is a dialogue* rules from `betterplan-workflow` > Shared conventions: one open question per beat, mirror what you heard in one sentence, update the canvas (Step 3a), then ask the next single question. If you notice yourself wanting to write the Story now — stop. Ask one more clarifying question instead.

### Maturity-aware refinement

Before starting the loop, check the Story's current maturity (Idea / Draft / Ready) and what the user wants to achieve this session. The generic defaults — *next maturity step* as target, no silent jumps, user may override with multi-step or stay-at-current — are defined in `betterplan-workflow` > *Discovery is a dialogue*. State the chosen target explicitly and confirm before starting.

Story-specific:

- The maturity steps are **Idea → Draft → Ready**; the minimum information for each is in Step 3b.
- For an existing Story, follow *Resuming refinement of an existing item* in `betterplan-workflow`: read content + activity log first, then resume from the unfinished gate (see also Step 3b *Resume an existing Story*).

The loop ends only when the Ready-Gate checklist in Step 3b is satisfied for the chosen target maturity **and the user explicitly confirms** that the canvas reflects the Story. Until then, no description text, no AC list, no maturity tag change.

## Step 3a — the Story canvas (shared working surface)

While the discovery dialogue runs, maintain a small canvas in the chat. The canvas is the **single source** from which the Story description is later derived (in Step 4). It also doubles as the snapshot the assistant writes back into the description whenever the loop is paused (see Step 3b), so the next session can resume from it.

For now this skill produces **one artifact only: the Story description**. A separate Concept document is **out of scope** here — a detailed concept will be written later during implementation, possibly by another agent, using the description as input. Therefore the description must end up precise enough to support that.

**Write the canvas in the user's language.** If the user writes German, use German labels (Warum / Regeln / Wie / Annahmen / Offene Fragen). If English, use the English labels shown below. Stay consistent within one session.

Show the canvas back to the user **after every answer**, updated in place:

```
### Canvas — <working Story title>

Why (persona + trigger + outcome):
  <one sentence>

Rules (each will become one acceptance criterion):
  - R1: <rule> | Example: <positive> | Counter: <negative or out-of-scope>
  - R2: …

How (each becomes either a finer AC or a Context note):
  - <decision area>, Vorschlag: … | Alternative: … | Trade-off: …

Open questions (block Ready):
  - Q1: <still unresolved>

Assumptions (explicitly accepted by user):
  - A1: <user said "ok, take this as given">
```

Rules of the canvas:

- **Sort into the right section as you hear it.** The canvas sections mirror the description sections — Why stays *persona + trigger + outcome*, How holds *shape / location / persistence / classification* proposals. If the user mixes layers in one sentence (e.g. names a UI location while explaining the value), do not paste the hybrid into Why — split it, sort each part into its section, and mirror it back sorted. Keeping the canvas clean makes deriving the description in Step 4 trivial instead of a second pass of structuring.
- Every rule must have **at least one positive example**. A rule without an example is a wish, not a rule.
- Every How-entry starts as **Vorschlag + Alternative**, not as a decision. It hardens into a decision only after the user confirms. Once confirmed, it lands in the description as either a finer acceptance criterion (when it expresses observable behavior) or in the Context section (when it's a rationale, constraint, or background decision a future implementer needs).
- A point moves from Open questions to Assumptions only when the user **says so**. The assistant never promotes silently.
- The canvas itself is informal Markdown in chat — it is **not** the Story description text and is not uploaded anywhere.

## Step 3b — Maturity-Gates, pause & resume

Before writing the Story description, check that the canvas meets the **minimum information** required for the chosen target maturity. Never infer "done" from "feels done".

### Minimum information per maturity (Definition of …)

Match the bar to the target maturity chosen in Step 3 ("Maturity-aware refinement"):

| Target | Minimum information that must be on the canvas |
|---|---|
| **Idea** | Title (activity verb) + a one-line summary **or** up to 3 Open questions. No Why-mirror required, no rules, no examples. |
| **Draft** | Confirmed Why (one sentence) + at least one Rule with one positive Example + any captured Open questions. How-gate may stay empty. |
| **Ready** | Confirmed Why + every Rule has ≥1 positive Example **and** ≥1 counter-example or out-of-scope note + zero open questions (or each remaining one explicitly accepted as Assumption) + user said "yes, write it up". |

If the chosen target was lower than Ready (e.g. "bring this from Idea to Draft"), check the lighter minimum and stop there — do not silently push past it into the next maturity.

Post the relevant gate check in chat before writing:

```
Gate check for <Story title> — target maturity: <Idea / Draft / Ready>
  [ ] <items from the row above, one checkbox each>
  [ ] User said "yes, write it up"   (always last)
```

- All boxes checked → continue to Step 4.
- Any box unchecked → either keep going in the discovery loop, **or** pause (see below).

### Pause at any time

The user may pause the discovery loop at any moment ("das reicht für heute", "stop here", "schreib in die Description was wir haben"). The assistant may also offer a pause when the user signals fatigue or when the loop has produced enough for a lower maturity than originally targeted.

When pausing:

1. Run the gate check for the **highest maturity whose minimum is currently satisfied** by the canvas — that becomes the actual target this session.
2. Write the current canvas state into the Story description via Step 4, keeping Open questions explicit (a Story can land at Idea or Draft with open questions; that is the point).
3. Set the maturity tag and date for the *achieved* level, not for the originally announced target.
4. Tell the user clearly what was achieved and what is still missing for the next level, in one or two sentences.

### Resume an existing Story

When the skill is invoked on an existing Story, **do not start from scratch**. First read the Story's current state and reconstruct the canvas from it:

1. Read `title`, `description`, current maturity tag, recent activity comments, and any captured Open questions / Out of scope notes.
2. Rebuild the canvas mentally: which Why is already confirmed, which Rules have Examples, which How-decisions are settled, which Open questions remain.
3. Show the reconstructed canvas in chat with a one-line summary: "Aktueller Stand: maturity X, Y open questions, fehlt für Z: …".
4. Ask the user what the goal of *this* session is — same rules as Step 3 ("Maturity-aware refinement"): default is next step up; user may override.
5. Re-enter the loop only on the gates that are still incomplete for the chosen target. Do not re-litigate gates that were already settled.

### Maturity-mismatch warning

If, while reading the Story, the assistant finds that the **current maturity tag is higher than the minimum information present** (e.g. a Story tagged `progress:ready` whose canvas does not actually satisfy the Ready bar), point this out before starting the dialogue:

> "Diese Story ist als Ready getaggt, aber es fehlen: <konkrete Lücken>. Sollen wir nachziehen, die Maturity zurücksetzen, oder beides ignorieren?"

Let the user decide; do not silently downgrade the tag.

## Step 4 — write the description (the only artifact)

Run this step only after the Step 3b gate for the chosen target maturity has passed (or after a pause was triggered). **Derive the description from the canvas — do not start from a blank page.**

### Scope of this skill (for now)

This skill produces **one artifact: the Story's `description` field in Betterplan**. No separate Concept document, no attachment, no design spec.

"Description" here means the whole content that lives in the `description` field of the task. It is **not** just a one-line intro — it includes all the usual sections (see "Output shape" below):

- The User-Story intro line (`Als …, will ich …, damit …`) or its Project/Devteam equivalent.
- `## Context` — background, decisions, constraints a future implementer needs.
- `## Acceptance criteria` — observable states to be true at the end.
- `## Out of scope` — explicit boundary.
- `## Open questions` — anything still unresolved (or moved to Assumptions during the dialogue).

A detailed implementation concept is written **later, during implementation**, by a human or an agent. The description must be precise enough to make that later work cheap — every Rule, Example, Out-of-scope note, accepted Assumption and Open question from the canvas must be reflected, so the implementer does not have to guess what was meant.

(The future workflow for the longer implementation concept is out of scope for this skill version and will be defined separately.)

### Length guidance

The description may grow longer than a one-liner — that is fine. Keep it readable:

- Aim for a description that fits **on one screen of scrolling** when filled in.
- Cut anything that only restates what is already clear from the canvas; carry information, not ceremony.
- If the description starts to feel like a small document with multiple subsections of prose explanation, the Story may need to be split, or the extra material belongs in a later concept (not here).

### Quality bar (INVEST)

This quality bar is the target for a **Ready** Story. An Idea or early Draft need not meet it yet — fill in detail as the Story matures (see Step 3b "Minimum information per maturity").

- **Independent** enough to build on its own.
- **Negotiable** — describes intent, not a rigid spec.
- **Valuable** — the value is explicit (to a user, or to the project/team for Project/Devteam Stories).
- **Estimable** — small and clear enough to size.
- **Small** — fits within an iteration; if not, split it (see method-deep-dive in betterplan-workflow).
- **Testable** — has acceptance criteria you could check.

Read the matching `references/<type>.md` for the type-specific template, voice, and examples.

### 4.1 The user-story line

Open the description with the user-story line that matches the Story type:

- **User Story** (`type: story`): `Als <konkrete Persona aus dem Canvas Why>, will ich <Fähigkeit>, damit <Wert>.`
- **Project Story** (`type: project`): one-line statement of who in the team or organization needs what and why, taken from the Canvas Why-line.
- **Devteam Story** (`type: dev`): one-line statement of the technical motivation, also from the Canvas Why-line.

Rules:

- Carry the **real persona and trigger** from the Canvas — not a generic role label. "Produktmanagerin von Rosengarten, in Reviews/Retros" is content; "Produktmanagerin" alone is a label. This is the Story-level application of the *Be specific, not generic* and *Tag content does not belong in the description* hard rules in `betterplan-workflow` > *Content separation*.
- Stay short: one or two sentences. Detail belongs in `## Context`, not in a fat opening paragraph.

### 4.2 Acceptance criteria — behavior, not pixels

Derive one acceptance criterion per **Rule** from the canvas — not per How-detail. Acceptance criteria capture *observable behavior at the end of implementation*, not the implementation itself. Apply the AC hard rules in `betterplan-workflow` > *Content separation* (behavior not pixels, AC are not implementation tasks, design decisions belong in `## Context`).

Story-specific phrasing:

- Use Markdown checkboxes (`- [ ]`), one condition per box.
- Phrase each one as a **state that can be checked true or false**, not a task to do.
  - Good: `- [ ] Suggestions appear after the user types at least 2 characters.`
  - Good: `- [ ] Audit-Einträge können vom Nutzer ein- und ausgeblendet werden.`
  - Avoid: `- [ ] Implement autocomplete.` (work, not a verifiable state)
  - Avoid: `- [ ] Audit-Einträge nutzen ein graues Icon.` (design detail, belongs in `## Context` as a decision note)
- Aim for **2–4 AC at Story level**. More than 4 usually means How-detail or implementation tasks have leaked in — move them into `## Context` as named decisions or split the Story.
- Given/When/Then is fine when it helps express a behavioral state.

How-decisions that are **not behavior** (e.g. "pro Browser-Session statt persistent", "Icon plus graue Schrift", "in der bestehenden Activity-Sektion verortet") go into `## Context` as named decisions with one line of rationale, so the later implementation concept can pick them up without re-deciding.

### 4.3 The optional activity comment

Posting a comment after the description was updated is **optional**. Follow the *Activity comments* rule in `betterplan-workflow` > Shared conventions for when and how. Story-specific triggers worth a comment: maturity moved up (Idea → Draft, Draft → Ready), a major scope decision was settled, a known open question was closed, or assumptions were accepted. Skip it for typo fixes or minor AC tweaks.

## Step 5 — create it (MCP or Markdown)

Follow the *Creating an item: MCP first, Markdown fallback* rule in `betterplan-workflow` > Shared conventions. In particular: **always show the full proposed description plus the intended maturity in chat first and ask explicitly for confirmation** before any create / update / comment / maturity-tag call. Never act in the same turn you first show the proposal.

Story-specific:

- If the user replies with a change request (rewording, scope tweak, AC adjustment), **do not patch it in silently**. Update the canvas (Step 3a) instead, re-derive the description in Step 4, and post the new proposal. The canvas is the source of truth — direct text edits would drift the two apart.
- When creating / updating via the MCP, set `type` = `story` / `project` / `dev`, plus `parentId`, `estimation`, maturity dates as arguments. Set the maturity date for the *achieved* level (which may be lower than the original target if the loop was paused, see Step 3b).
- Post the comment from Step 4.3 only if it applies.
- If the MCP is not available, output the Markdown shape below for the user to paste in.

## Output shape (Markdown fallback)

Output **content only** — what goes into the Story's title and description. Do **not** include type, parent epic, maturity, story points, or dependency lines in the pasteable block; those are fields (set as MCP arguments, or mentioned in your chat reply when pasting Markdown).

A Story description **may** use these sections (in this order). Which sections are filled depends on the target maturity — see Step 3b "Minimum information per maturity". Read the matching `references/<type>.md` for the type-specific voice and a worked example.

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

Depth per maturity and AC rules are defined upstream — see **Step 3b "Minimum information per maturity"** for what the description must contain at Idea, Draft, and Ready, and **Step 4.2** for how acceptance criteria are phrased. Do not pad with placeholder text; fill in only what is actually on the canvas.

After producing a Story, offer to break it into Workitems with the `create-workitem` skill once it is Ready for an iteration.
