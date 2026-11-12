---
name: betterplan-workflow
description: >
  This skill should be used to classify a piece of work into the correct
  Betterplan building block and to understand the Betterplan method. Use it
  when the user is unsure "what type" something is, says things like "is this
  an epic or a story", "how should I structure this", "what goes in the
  backlog", "help me plan in Betterplan", or when any create-* Betterplan skill
  needs the shared rules (maturity levels, open/closed, story points, output
  format). It routes the request to betterplan-create-initiative, betterplan-create-epic,
  betterplan-create-story, or betterplan-create-workitem.
metadata:
  version: "0.4.0"
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
| Initiative | Structure | A **business goal** — the outcome we want to achieve. Not worked on directly. |
| Epic | Structure | A **step in the business process** that fulfils the goal. Structure, not worked on directly. |
| User Story | Implementation | A **tool or option that fulfils a process step**, with concrete user value. A tool can be a person, a service, or a system. |
| Project Story | Implementation | A tool that fulfils a step but has no direct user value: organizational, hardware, docs, decisions/events. |
| Devteam Story | Implementation | A technical tool internal to the dev team (refactoring, build pipeline, technical debt). |
| Workitem | Implementation detail | Smallest unit. Belongs to a Story, used only on the Iteration Board to coordinate delivery. No story points. |

## Starting from a rough idea

Often the user does not arrive with a fully classified piece of work. They say "I just have an idea", "we should do something with X", "Idee: Y", or "what about Z?". When that happens, **do not start with a classification quiz**. The work is light, fast, and one-directional:

1. **Capture the idea as an Idea Story.** Default `type` is `story` with maturity tag `progress:idea`. Title = a short activity-form distillation of the user's sentence. Description: one line of intent (use the user-story form when it is already implicit; otherwise a plain intent sentence is fine).
2. **Propose where it belongs in the Story Map.** Look at existing Initiatives and Epics in the project. Suggest the most plausible parent (`parentId`) with one line of reasoning. If nothing fits, propose a new Initiative or Epic to host it, with one line of why.
3. **Ask the user to confirm or correct the placement.** One question, not a multi-choice list of all Initiatives. If the user corrects, just move it — no debate.
4. **Stop here unless the user wants more.** The idea is captured and placed. Further refinement (Draft, Ready) happens later via `betterplan-create-story` — the user decides when.

Only step into the classification flow (next section) when the user explicitly wants to commit to a non-Story type, or when the idea is obviously not a Story (e.g. a clear large goal that asks for an Initiative). The user can always say "this is a <type>" and skip the on-ramp; take that at face value.

## Classification — pick the right type

Walk this decision in order and stop at the first match:

1. **Does it set overall direction and is too big to build directly?** → Initiative. (e.g. "Increase self-service checkout adoption")
2. **Is it a step the user takes toward a goal, made of several options/variants?** → Epic. (e.g. "Search", "Checkout")
3. **Two questions, both must hold** → User Story. (e.g. "Text search with autocomplete")
   - *Direction*: is the benefit aimed **outward**, at someone nameable **outside the project team**?
   - *Deliverable*: is something handed over that gives that beneficiary a capability?
4. **Is it needed, but fails either test in step 3?** — no outward beneficiary, or nothing handed over that gives one a capability.
   - Organizational, contractual, hardware, or recording a decision/event → Project Story. (Obtaining an access credential granted only on request; signing a supplier contract; procuring a test device; writing down which of two approaches was chosen and why. Outward-facing or infrastructural, but nothing is handed over that gives a beneficiary a new capability.)
   - Technical and internal to the dev team (refactoring, CI/CD, tech debt) → Devteam Story.
5. **Is it a small task that only helps coordinate the delivery of one Story inside an iteration?** → Workitem.

Edge cases:

- **A document is not automatically a Project Story.** The artifact's form does not decide; the beneficiary does. Internal documentation with no outside audience is a Project Story. A document *delivered* to someone who can then do something — a runbook the operations team needs to take a service over, an integration guide another team needs to connect to it, a parts list a customer feeds into their own planning — passes both tests in step 3 and is a User Story. This is why `documentation` is absent from the step 4 list.
- "Bug / rework" on a Story: do **not** create a new Story. Add a **Workitem with `isBug = true`** to the affected Story (use `betterplan-create-workitem`). The backend handles the rest — reopening the Story and the bug rollup. Knowledge stays on the Story.
- An unplanned task with no home Story → Devteam Story (technical cause) or Project Story (organizational).
- If an Epic turns out to have only one way to do it, it may simply be a User Story. If a User Story keeps growing options, it may be an Epic. Structure is allowed to change.

When the type is decided, hand off. The `type` column is the value used in the data model (see `references/data-model.md` for the mapping):

| Block | `type` | Skill |
|---|---|---|
| Initiative | `initiative` | `betterplan-create-initiative` |
| Epic | `epic` | `betterplan-create-epic` |
| User Story | `story` | `betterplan-create-story` |
| Project Story | `project` | `betterplan-create-story` |
| Devteam Story | `dev` | `betterplan-create-story` |
| Workitem | `workitem` | `betterplan-create-workitem` |

## Shared conventions

Every `create-*` skill follows these. They are defined once here.

### Perspective: a Story belongs to its beneficiary

A User Story is written from the perspective of the **beneficiary** — the person or body that gains something — never from the perspective of whoever owes the work. That an obligation has to be met, and organized, is self-evident and does not earn its own item.

This matters most where the material arrives as a list of duties: regulation, certification, tenders, audits. Written down as they arrive, every item becomes a duty roster and the Story Map tells no story at all.

| | |
|---|---|
| Story | *"Als Nutzer möchte ich erfahren, wenn ein Sicherheitsvorfall mein Gerät betrifft, damit mein Zuhause sicher bleibt."* |
| Not a Story | "Artikel 14 erfüllen" |

**Who owes the work is a second, orthogonal dimension** and is carried as a tag with the bare role name — `project:Hersteller`, `project:Zulieferer` — grouped by colour, never by a category word inside the value (see the tag rules in `references/data-model.md`). The two dimensions coincide often, and that is fine: a manufacturer is both beneficiary and obligation-bearer of its own documentation, while a user is the beneficiary of updates the manufacturer owes. One backbone then reads left to right as a narrative and filters by responsibility.

**Counterparties are not personas.** A supervisory authority, an auditor, a certifying body, a funding agency appears in the Story text as the *trigger* of an obligation — "on the authority's substantiated request", "before the audit date" — never in the Why-line. Nobody works a Story titled "As the supervisory authority I want…". The test is not whether the party is important but whether the Story hands it a new capability; a party that only asks, checks or permits does not get one.

### Personas

A persona is a **real Betterplan object**: the MCP exposes `create_persona`, `assign_persona` and `archive_persona`, they are project-scoped, and one must exist before it can be assigned.

Recording a persona is **optional**. What the perspective rule above requires is the beneficiary's *point of view* in the Story; a Story that names its beneficiary in the description satisfies it on its own. Create persona objects when the same beneficiary recurs across many Stories and is worth seeing on the board — not as paperwork for a one-off.

A usable persona is a concrete audience, under the same rule as every other name here: never a role label that could be anyone ("the user", "Product Manager"). "Layman consumer setting up a smart-home device at home" is a persona; "End user" is a placeholder.

### Playbook templates

Two rules apply only to a Playbook — a Story Map authored to be instantiated by teams the author never meets.

**A template carries no Devteam Stories and no Workitems.** A Playbook exists to make visible which task belongs to which step, and its Story Map read left to right *is* the product. Devteam Stories are technical work internal to the dev team, and a template author has no dev team. Workitems are coordination artifacts of the executing team on the Iteration Board, created ready or not at all. Both are created during execution, by the team doing the work, when the need appears.

Where that forces a clarifying decision into Story shape, find the beneficiary on the company side rather than abandoning the rule: *"Als Hersteller möchte ich früh wissen, welcher Konformitätsweg für mein Produkt gilt, damit ich das nicht kurz vor Markteintritt feststelle."*

**A template may carry a Project Story, but only a wired one.** Some work in a Playbook genuinely has no single step it belongs to — obtaining an access credential that gates several Epics, establishing a company-wide status that decides four different things, keeping track of regulation that is still arriving. Attached to any one Epic, such an item lies about its reach; left out, the template is silent about work the team cannot skip.

The test is **cross-cuttingness**: more than one Story, in more than one place, depends on it or is shaped by it. **One dependant means it is not cross-cutting** — the work belongs inside that Story, as acceptance criterion or description content.

A Project Story takes no parent, so it needs binding to the Stories it affects. Two ways, not equivalent:

- Where an ordering is genuinely forced, **model the dependency**. It then reaches the Delivery Timeline and appears as the gate it is. The dependency rule above requires this anyway.
- Where none is forced, a **`#NNN` reference** from the affected Stories is enough. A company-wide status that changes *how* four Stories are done without blocking any of them has no dependency to model and is still cross-cutting.

A forced ordering is therefore a **strong indicator** of cross-cuttingness, not an admission requirement — demanding it would exclude exactly the items that inform rather than block. What must be stated either way is the **reach**: an item whose dependants cannot be named is an item whose reach was not checked.

**Use Project Stories sparingly.** The bar is not "is this cross-cutting enough to be allowed" but "would the instantiating team miss something essential if this were not its own item". Most candidates fail it: they fit inside a User Story, or they are the *Why* of one and belong in its Context. A template that accumulates root-level items has drifted back into the problem this rule carves an exception from.

**Template Stories land at Idea, with fully worked content.** Work each Story as far as the source material allows — description, acceptance criteria, source citation, out-of-scope — and still set maturity to **Idea**. This looks like a contradiction of the maturity rules and is not: the Discovery dialogue belongs to the team that instantiates the template, and it has not happened yet. A template Story is a fully argued *proposal*, not an agreement. The open questions that remain are the decisions that team must make — product-specific choices the author cannot answer — and they stay written down rather than being dropped to make the Story look Ready.

Template personas carry the same note: the instantiating team sharpens them to its actual product. A template cannot name a concrete audience it has never seen, so it names the audience *types* the source material distinguishes and says so.

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
- **Prefer one open question per beat over a multi-choice salvo.** Multi-choice freezes the user into the assistant's option set; an open question invites the user's own framing. Multi-choice is fine when the user asks for options, or when the choice is genuinely categorical (e.g. selecting a type in Step 1 of `betterplan-create-story`).
- **Refinement is pauseable and resumable.** The user can stop the dialogue at any time; the assistant lands the Story at the highest maturity whose minimum is actually satisfied, writes the current state into the description (open questions stay explicit), and on the next invocation reconstructs the canvas from the description plus activity log to resume from the unfinished gate.

These rules are operationalized in `betterplan-create-story` Steps 3, 3a, and 3b. Other `create-*` skills follow the same spirit at their **proportional scale** — Initiatives and Epics are structure (no maturity levels), Workitems are coordination (no maturity, no discovery), so the dialogue shrinks accordingly:

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

For Stories this is operationalised in `betterplan-create-story` Step 3b with maturity gates. For Epics and Initiatives the same spirit applies without maturity tags. For Workitems it does not apply — Workitems are mechanical break-downs and are not refined in dialogue.

### Open vs Closed

Every Story is Open (still in progress, anywhere from Idea to Done) or Closed (finished or deliberately stopped). Closing a low-value Story early is a good outcome, not a failure (~20% of stories carry ~80% of value).

**When closing an item as obsolete or "won't do":** preserve the existing description **as-is** — do not overwrite it with a closing rationale. The original idea has historical and learning value (what was the intent, what shape did it have, what made it look promising once). Put the reason for closing into the **activity log** via a comment ("Closed as obsolete because …", "Superseded by #N", "Won't do — out of scope after …"). The same applies to Initiatives and Epics. If the closed item is replaced by another, link to the successor in the comment, not in the description.

**Workitems have no Closed state.** They are lightweight coordination items on the Iteration Board, complete once they reach **Done** (`progress:done`) — never set `completionState = "closed"` on a Workitem. An obsolete Workitem is simply deleted; there is no closing rationale to preserve (unlike a Story, it carries no planning or historical value).

### Estimation (Stories only)

Stories are estimated in **Story Points**, used together with team Velocity to forecast the Delivery Timeline. Do not invent a precise number. Suggest a relative size only when asked, and note that Betterplan auto-fills unestimated stories with the team median. Workitems have **no** story points.

### Dependencies: hard ones are modelled, soft ones are textual

Two kinds of relation between items, and they are carried differently.

A **hard dependency** forces an order: item B cannot start, or cannot be finished, until item A is done. These are the relations that would form a critical path in project management. Model them as **real Betterplan dependencies** (`create_dependency`) — only then do they reach the Delivery Timeline and show what actually gates what. Naming the dependency in prose instead leaves it invisible to planning.

A **soft reference** explains, contrasts, or points at related work without forcing an order. Carry it as a `#N` reference in the description. No dependency object — and not by choice: `blocks` is the only `dependencyType` there is, so the data model has nothing else to offer. `#N` is the task's **number**, a server-assigned field of its own, not its `task_id`; see *References and dependencies* in `references/data-model.md` for the three identifiers, the direction `blocks` runs in, and the two traps an import walks into.

| Relation | Carried as | Example |
|---|---|---|
| Hard — B is gated by A | `create_dependency` | Conformity route can only be assessed once the product category is determined |
| Soft — B is informed by A | `#NNN` in the description | "Builds on the glossary established in #214" |

Two consequences worth stating:

- **Decide deliberately, both ways.** An order modelled where none exists blocks work that could run in parallel; an order left unmodelled where one exists makes the timeline lie. When creating or refining an item, ask whether something genuinely gates it.
- **An intermediate format must be able to carry hard dependencies.** Where a Story Map is drafted outside Betterplan first — in Markdown, for review in Git — the format needs a place for them (frontmatter, keyed by stable item id). A format that cannot express them is unusable as a precursor, because the dependencies would have to be reconstructed from prose on import. This does not change the single-item Markdown fallback below, which still keeps structural fields out of the artifact and names them in the chat reply.

### Content separation: Description vs AC vs Tags

Three layers, three jobs. Do not mix them.

| Layer | Job | Style |
|---|---|---|
| **Description** | What value, for whom, why now. The reader picks up the Story in 30 seconds. | Plain prose, user-story form by default ("Als …, will ich …, damit …"). Includes all the usual sections (Context, Acceptance criteria, Out of scope, Open questions) — see `betterplan-create-story` Step 4. |
| **Acceptance criteria** | Observable states that must be true at the end. Live as a section inside the description. | Markdown checkboxes, behavior not pixels. 2–4 at Story level; finer detail belongs in Workitems. |
| **Tags** | Metadata labels for filtering and reporting. | Single words or short phrases, namespaced `project:<value>` — `project:Persistenz`, `project:UI`, `project:Audit`. The value carries no category word; the colour says which dimension it belongs to. See the tag rules in `references/data-model.md`, including why the `tagDefinitions` entry is spelled *without* the prefix. |

Hard rules — generic (every `create-*` skill):

- **Tag content does not belong in the description.** Mirroring a tag (e.g. writing "Persistenz" into the description because there is a Persistenz tag) is not real content. Tags are labels for filtering; the description is content.
- **Be specific, not generic.** Avoid role labels that could be anyone ("Product Manager", "Developer", "the user"). Name the actual person, team, or situation — for Stories, carry the real persona from the Canvas Why-line; for Epics and Initiatives, name the concrete audience ("Customer Service team", "Stakeholder PMs in Reviews/Retros").
- **Titles are checkable.** A title is a short verb phrase naming one observable outcome, so that "done" is a fact and not an opinion — "Set up the intake channel", not "Vulnerability topic"; "Determine the product category", not "Product categories". If you cannot tick it off, you have written a heading, not an item. This holds at every level: an Initiative's outcome is larger than an Epic's, but both must be nameable as a result that either exists or does not.
- **No index prefixes in titles.** A title carries meaning, not position — never prefix it with an outline or sequence number ("I1 · …", "E1.1 · …", "Story 3: …", "R2 – …"). Ordering and hierarchy already live in the map structure and `displayOrder`; a number baked into the title goes stale the instant anything is reordered or reparented, and makes reordering harder because every move means a rename. Refer to items by name **when you are talking to the user**. (If you need a stable outline id for cross-referencing, keep it in the source doc, not the Betterplan title.)
- **Inside a description, refer to another item as `#N`** — its task number, written as plain text. Betterplan resolves it; there is nothing to create and nothing to link. Not by title: a title goes stale the moment that item is renamed, and only the number is what Betterplan resolves and what `list_task_references` finds. Look the number up with `list_tasks(query=…)` rather than guessing — a wrong number points at someone else's work, and nothing flags it. A reference is not a dependency: `#N` says "related, read this too", and if the other item has to be *done first*, model that as well (see *Dependencies* below). If the number does not exist yet, say so and leave the reference out; a `#N` pointing at nothing is worse than naming the item in prose.
- **Context, not ceremony.** Every section of the description should teach or frame something the implementer needs. Cut anything that only restates what is already obvious from structure or tags.
- **Write it so it reads once.** The six plain-language rules below are not style preference; a description nobody finishes reading carries no information. See *Plain language* immediately after this section.

Hard rules — Story-only:

- **AC do not encode UI / design decisions.** Grey font, specific icon, session vs persistent storage — those are decisions that live in the description's `## Context` section as named decisions with one line of rationale. AC say what behavior must hold.
- **AC are not implementation tasks.** "Implement X" is work, not a verifiable state. Phrase as the state that exists once the work is done.

A separate, longer implementation concept is **out of scope for this skill version**; the description is the only artifact produced by `betterplan-create-story`. The concept document — its shape, who writes it, and when — will be defined in a later skill iteration. For now, the description must be precise enough that the later concept can be derived from it.

### Plain language

Applies to **every** item type — Initiative, Epic, Story (user / project / devteam), Workitem — and to every section of a description, not only the summary line. The reader does not have the discovery dialogue in their head. Write for that person.

Six rules, ordered by effect:

1. **One thought per sentence.** Aim for an average under 16 words; split anything past 30. A sentence that needs two em-dashes to hold itself together is two sentences.
2. **Verbs, not nominalizations.** `prüfen` beats `die Prüfung erfolgt`, `entscheiden` beats `die Entscheidungsfindung`. German lets you stack nouns forever, and that is the single biggest source of descriptions nobody reads twice.
3. **Concrete things, not category names.** `ein Installer, den der Kunde herunterlädt` beats `ein in Verkehr gebrachtes Artefakt`. If the reader has to translate your term into an example before they can think, you picked the wrong word.
4. **References at the end of the sentence or on their own line — never mid-clause.** `… gelingt praktisch nicht. (CRA-EG(9))` beats `… fasst CRA-EG(9) weit: …`. An id inside a clause interrupts the reader twice. This holds for `#N` item references too.
5. **Direct address where the reader has to act or decide.** `Zähl auf, was dein Haus verlässt` beats `Es ist ein Inventar zu erstellen`. Use **du**, not Sie — these are working documents, not correspondence. Purely descriptive background stays impersonal.
6. **No invented labels.** Do not compress a thought behind a marker you made up (`*Prüft:*`, `*Richtungssinn:*`). A thought that needs a label nobody knows needs a sentence instead.

Two checks before saving: read it out loud — every place you have to restart a sentence is a rewrite. Then measure the average sentence length. Under 16 words it reads, over 20 it does not, and rereading your own text will not tell you which side you are on.

The rules are about **how** a description reads, not what it contains. They never justify dropping a decision, a constraint or an open question — a short description that leaves the implementer guessing is worse than a dense one that does not.

### Creating an item: MCP first, Markdown fallback

Before creating anything, check whether **Betterplan MCP tools are available** in the current session (tool names contain `betterplan`).

**Always confirm before creating.** In the turn *before* any create or update call (MCP or Markdown), show the full proposed artifact in chat — title, description / content, the intended `type`, the intended `parentId` (if any), and any maturity tag or `isBug` flag you plan to set. Ask explicitly, e.g.:

> *"Soll ich das jetzt so anlegen — als <type>, unter <parent>, mit Maturity <Idea | Draft | Ready>?"*

Never call the create / update tool, post a comment, or change a maturity tag in the **same turn** you first show the proposed content. The user must see what is going in and approve it. If the user replies with a change request, do not patch the proposed text silently — update the working surface (canvas for Stories, notes for Epics / Initiatives), re-derive the proposal, and show it again.

**If the Betterplan MCP is available**, create the item by calling its create tool — do not just print Markdown. Map:

- content → `title` + `description`
- everything else → arguments: `type` (use the mapping in the routing table / `references/data-model.md`), `parentId`, `releaseId`, `estimation`, maturity dates, `tags`, `isBug`.

The MCP describes its own tools and field names at runtime — follow those for exact arguments. After creating, confirm with a short chat summary (what was created, its type and parent). If a required argument is missing (e.g. the target project or parent), ask the user.

**Always set `parentId` on an Epic, a User Story and a Workitem.** Create the parent first if it does not exist yet, or ask which one the user means. Never fall back to creating the item parentless — a parentless item has been seen to become unupdatable. See *The hierarchy* in `references/data-model.md` for the full table and the status of the backend's enforcement (Project and Devteam Stories are root-level and take no parent).

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

See `references/glossary.md` for term definitions, `references/method-deep-dive.md` for the full method, prioritization, and the Story Map layout, and `references/data-model.md` for the conceptual mapping the MCP does not spell out (the `type` values, how maturity is stored, content vs metadata, the tag namespacing rules, the bug rule).

## The Betterplan MCP

The Betterplan MCP server (OAuth) lets these skills read and write items directly in the app. It is connected separately by the user, not bundled in this plugin. When its tools are present, prefer them (see "Creating an item" above); when they are not, fall back to Markdown. The MCP describes its tools, fields, and arguments itself, so rely on those at call time for exact field names; use `references/data-model.md` only for the conceptual mapping (which `type` to use, how maturity and bugs work).
