# User Story

Data model: `type: story`.

Concrete, buildable work that delivers value **to a user or customer**. A User Story is one option for *how* a user takes the step described by its parent Epic.

## Voice

Use the classic form when it helps, but do not force it:

> As a `<role>`, I want `<capability>` so that `<benefit>`.

The "so that" is the important part — it carries the value. If you cannot state a real user benefit, it is probably a Project or Devteam Story instead.

## Writing rules

- One option per Story. "Basic text search" and "Search with autocomplete" are two Stories, not one.
- Describe intent and outcome, not the technical solution.
- Acceptance criteria describe observable behavior from the user's side, as checkable states.
- Prefer the smallest version that is still valuable; richer variants become their own Stories.

Use the standard section structure from the betterplan-create-story skill: summary, `## Context`, `## Acceptance criteria`, `## Out of scope`, `## Open questions`.

## Example

```
# Search with autocomplete

As a shopper, I want suggestions while I type so that I can find products
without spelling the full name.

## Context
Builds on basic text search. Analytics show many searches fail on misspelled
product names; suggestions should reduce empty result pages.

## Acceptance criteria
- [ ] Suggestions appear after the user types at least 2 characters.
- [ ] At most 8 matching product names are shown.
- [ ] Selecting a suggestion immediately runs the search.
- [ ] No suggestions are shown for fewer than 2 characters.

## Out of scope
- Typo-tolerant / fuzzy matching.
- Suggesting categories or brands (only product names for now).

## Open questions
- Should recently searched terms be mixed into the suggestions?
```
