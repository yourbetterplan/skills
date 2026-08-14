# Devteam Story

Data model: `type: dev`.

Cross-cutting **technical** work internal to the development team, with no direct user value: refactoring, build/CI-CD pipeline, infrastructure, automated tests, tech-debt paydown, developer tooling. It is work needed to keep delivering good results sustainably, even when it is invisible to the user.

## Writing rules

- Do not use the "As a user…" form. Optionally frame value to the team: "so that the team can…".
- State the technical motivation and the cost of *not* doing it (risk, slowdown, fragility).
- Keep it genuinely cross-cutting. Technical work that belongs to one User Story should stay inside that Story (or its Workitems), not become a separate Devteam Story.
- Acceptance criteria are checkable technical outcomes.

Use the standard section structure from the betterplan-create-story skill: summary, `## Context`, `## Acceptance criteria`, `## Out of scope`, `## Open questions`.

## Example

```
# Add CI pipeline with automated tests

Set up a continuous integration pipeline that builds the app and runs tests on
every push.

## Context
There is no automated build or test run today. Regressions are caught late,
which makes releases risky and slow. No direct user value, but it enables
faster, safer delivery of every later story.

## Acceptance criteria
- [ ] Every push runs the build and the unit tests.
- [ ] A failing test blocks the merge.
- [ ] The pipeline status is visible to the whole team.

## Out of scope
- Deployment / continuous delivery to production.
- End-to-end and load testing.

## Open questions
- Which CI provider do we standardize on?
```
