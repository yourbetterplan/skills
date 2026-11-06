# Building the Story Map is its own step, with its own skill

ADR 0002 split goal definition out of extraction. The same seam now has to be cut
one step further along: the chain ran `transform → goal → extract` and then
stopped, with nothing owning the step that turns a goal and a pile of
requirements into a Story Map. The `create-*` skills author one item at a time
and require a parent to attach it to; none of them decides what the backbone
should be, which Epics carry which obligations, or whether every requirement has
found a home.

The absence showed up as a **drift in the goal step**. Running `betterplan-goal`
on the CRA playbook, the interview slid from the Initiative level down to the
Epic level — 22 Epics with source citations, each argued individually — because
nothing downstream was going to do it and the question territory did not say
where its own floor was. The detail was not wasted: it was at Epic level that two
findings surfaced which changed the goal itself (the Art. 69 transitional switch
that splits the obligation set in two, and the Art. 14 reporting deadline falling
fifteen months before everything else). But the output had the wrong shape. A
`GOAL.md` carrying 22 Epics freezes a structure the map-building step must stay
free to overturn.

We therefore add a skill, **`betterplan-storymap`**, which runs after
`betterplan-extract` and owns the Story Map: the backbone at Epic level, the
Stories under each Epic, personas, responsibility tags, dependencies, and the
coverage check back against the extracted requirements.

## The altitude boundary

`betterplan-goal` is now explicit about its floor. The `goal:backbone` section
holds exactly three things: the Initiatives with one sentence each, their order,
and the reasoning behind order decisions that are not self-evident. The
justification is not tidiness — it is **who consumes what**. The Initiatives
determine how `betterplan-extract` cuts the requirements, so they must be settled
before extraction runs. The Epics determine nothing about extraction; settling
them early only removes freedom from the step that is supposed to decide them.

The rule is stated as a positive contract rather than a prohibition, and it is
paired with a conditional for the case that actually occurs: when the interview
does run into Epic territory, the result goes into a working note in the
project's map directory, marked as a draft, and `goal:backbone` points at it.
Forbidding the drift would discard the findings that make the drift worthwhile.

## Consequences

- **The chain is now four steps**: `transform → goal → extract → storymap`. Each
  has a hard precondition on its predecessor's output file.
- **`GOAL.md` gains a pointer, not a structure.** The Epic-level draft is project
  data in the map directory, explicitly non-binding, and `betterplan-storymap` may
  discard it entirely.
- **The 22-Epic draft from the CRA run is the first test case** for the new skill:
  if the skill cannot reproduce or improve on a hand-grilled backbone, it is not
  doing its job.
- **`betterplan-goal` stays thin.** It gained a boundary, not a responsibility.
