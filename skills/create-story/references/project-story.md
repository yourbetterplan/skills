# Project Story

Data model: `type: project`.

Cross-cutting work within the endeavor that has **no direct user value** but still must be done: organizational and contractual matters, procuring hardware, maintaining documentation, compliance, onboarding logistics. Also the right home for **recording important events and decisions** that influenced the course of the endeavor.

## Writing rules

- Do not force the "As a user…" form. State the need and why it matters to the project.
- Make the trigger or obligation clear (deadline, contract, dependency, external party).
- For a decision/event record, capture what was decided, when, by whom, and the consequence — this is what makes the Delivery Timeline traceable later.
- Acceptance criteria describe "done" in concrete, checkable terms (signed, delivered, published, configured).

Use the standard section structure from the create-story skill: summary, `## Context`, `## Acceptance criteria`, `## Out of scope`, `## Open questions`. For a pure decision/event record, acceptance criteria and out-of-scope often do not apply — omit them and keep the context.

## Examples

```
# Sign data-processing agreement with payment provider

We need a signed DPA with the payment provider before payments can go live.

## Context
Legal requirement for processing customer payment data. The provider supplies
a standard DPA template. This gates the payments launch.

## Acceptance criteria
- [ ] The DPA has been reviewed by legal.
- [ ] A signed copy is stored in the contracts folder.

## Open questions
- Does the provider's standard template need any custom clauses for our region?
```

```
# Decision: ship web-only first, defer native apps (2026-05)

Recorded decision: ship web-only for the first release and revisit native apps
afterwards, to keep scope focused.

## Context
Decided 2026-05 with stakeholders. Native effort was competing with core web
features. Kept here so the Delivery Timeline stays traceable later.
```
