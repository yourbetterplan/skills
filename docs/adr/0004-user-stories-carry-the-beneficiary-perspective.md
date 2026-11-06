# User Stories carry the beneficiary's perspective, not the obligated party's

Requirement-heavy endeavours — regulatory compliance, certification, tenders —
arrive as lists of things somebody must do. Written down as they arrive, every
item becomes a Project Story: organisational, obligation-shaped, addressed to
whoever is on the hook. A Story Map built that way reads as a duty roster and
tells no story at all.

In every Betterplan Story Map, a User Story is therefore written from the
perspective of the **beneficiary** — the person or body that gains something —
not from the perspective of whoever owes the work. That an obligation has to be
met and organised is self-evident and does not earn its own item. *"As a user I
want to be told when a security incident has affected my device, so that my home
stays secure"* is the Story. "Comply with Article 14" is not.

The obvious failure of that rule is that everything has a beneficiary if you
squint. The boundary is therefore **direction**, and the boundary line is the
**project team**, not the company:

1. **Is the benefit directed outward, to someone nameable outside the project
   team?** If not, it is a Project Story (organisational) or a Devteam Story
   (technical).
2. **Is something delivered that gives that beneficiary a capability?** If yes, it
   is a User Story.

Both halves are needed. Direction alone would admit the team's own planning work;
delivery alone would admit internal artefacts with no audience.

The company is outside the project team, which is what makes the awkward cases
work. A manufacturer able to answer a market surveillance authority gains a real
capability — continued market access — so *"as a manufacturer I want to be able
to meet my obligations towards the authorities by producing complete technical
documentation on reasoned request"* is a User Story, with the manufacturer as
beneficiary. Choosing which conformity assessment route to take benefits the
team's own planning, so that is a Project Story. Authorities and CSIRTs appear in
Story text as the trigger of an obligation, never as a persona — nobody works a
story titled "as a market surveillance authority".

Who *owes* the work is a second, orthogonal dimension and is carried as a tag,
not by the persona and not by the backbone structure. The tag is the **bare role
name** — `project:Hersteller`, `project:Zulieferer` — and the dimension it belongs
to is signalled by giving those tags a shared colour family in
`settings.tagDefinitions`, not by prefixing a category word. Card space is
limited, and the repo's own tag rule already says to group by colour rather than
by a second text prefix; `project:Pflicht Hersteller` would break that rule while
costing twice the width. Tags without a semantic grouping keep the default
colour.

The two dimensions coincide often and that is fine; the manufacturer is both
beneficiary and obligation-bearer of its own documentation, while a user is the
beneficiary of updates the manufacturer owes. One backbone then reads left to
right as a narrative and filters by responsibility.

Where a persona is recorded as a first-class thing, it is a **real Betterplan
persona object** — the MCP exposes them (`create_persona`, `assign_persona`,
`archive_persona`) and they are project-scoped, so they must exist before they can
be assigned. Recording one is **optional**: what this decision requires is the
beneficiary *perspective* in the Story, not a persona object behind it. A Story
whose beneficiary is named in its description satisfies the rule on its own.
`betterplan-workflow` is silent on personas today and has to document them —
including that they are optional and what a good one looks like.

## Consequences

- **This overrides the `documentation` entry in the classification list** in
  `betterplan-workflow`. The artefact's form does not decide; the beneficiary
  does. Internal documentation with no outside audience stays a Project Story; a
  document delivered to someone who can then do something is a User Story.
- `references/method-deep-dive.md` claimed Project and Devteam Stories "often sit
  under an Epic too". They do not — they are root-level, as `data-model.md` and
  `SKILL.md` state. The sentence is wrong and goes.
- **Naming the beneficiary is a gate, not a formality.** If it takes squinting to
  find one, there is none, and the item is not a User Story.
