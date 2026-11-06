# Betterplan method — deep dive

Background for classification and structuring decisions.

## The Story Map (Scope)

The Story Map is the heart of Betterplan and the shared reference everyone uses.

- **Left → right**: the major steps / sections of the endeavor, read like a narrative.
- **Top → bottom**: importance and options — most important on top, supplementary below.
- **Three levels of granularity**: Initiatives (goals) → Epics (steps) → Stories (options/tasks under an epic).
- **Releases**: horizontal swimlanes / milestones. Assign Stories to a Release to structure the endeavor by time as well as content.

Screenplay test: the Story Map tells the story of the user within the endeavor. Goals become Initiatives; the steps to reach them become Epics. If the story reads right, the structure is right.

### Building a map: breadth before depth

**Mile wide, inch deep.** Reach the end of the big story before going deep on any part of it. Complete the backbone — every step, left to right — before writing Stories under any one step. Deciding the details of step 1 before knowing whether step 7 exists produces a map that has to be rebuilt.

**Even altitude.** Epics along the backbone should be comparable in size. Mixed granularity breaks the narrative, because a reader cannot tell whether the next card is the next step or a detail of the previous one. An Epic obviously larger than its neighbours either hides several steps, or the neighbours should be merged.

**One protagonist per map.** A map tells one actor's journey. When it interleaves the journeys of different actors — a manufacturer and its supplier, a buyer and a seller — the left-to-right reading stops being a narrative and becomes a schedule. Two actors, two maps; the relation between them lives in dependencies.

**Establishing and operating are two steps, not one.** A capability that is built once and then run continuously — an intake channel, a reporting duty, a support obligation — appears twice on the map: establishing it, where it belongs in the journey, and operating it, in a late step after the thing is live. Collapsed into one step, the map claims the work finishes when it does not.

### Slicing releases

A release is **an outcome, not a batch of items**. Slice horizontally: a release cuts thinly across *all* the steps rather than completing the leftmost ones.

**The first slice is a walking skeleton** — the thinnest end-to-end path through every step. It barely works and solves one problem badly, and it is still worth more than a perfect first step with nothing behind it.

**A release may be a learning goal.** Its purpose is then to test the riskiest assumption rather than to deliver value — Patton's minimum viable product experiment. Such a release states the question it answers and which result would change the plan. A release with neither a stated outcome nor a question is a date, not a release.

## Prepare — prioritization

Prioritization in the Backlog follows one principle: **stop starting, start finishing.** Whatever is furthest along has the highest priority — a Story in progress beats one still in draft. Within a maturity stage, top-to-bottom order sets priority.

Use the Story Map for initial prioritization: a well-told story implies which step must come first.

## Discovery — the bravest sentence is "we're not building that"

Discovery is a filter, not a formality. Closing low-value Stories early is the right use of limited resources (Pareto: ~20% of stories carry ~80% of value). A Story can be Closed in any phase, even as an early idea.

## Build — iterations and tracks

An iteration is a fixed time box with two parallel tracks inside one Story:

- Discovery track: Draft → Ready (clarify and prepare).
- Delivery track: Todo → Doing → Done (implement and deliver).

Betterplan decides a Story's track automatically from its progress. The first iteration is created automatically when the first Story moves into a Discovery/Delivery status.

## Insight — the Delivery Timeline

A forecast, not a manual plan. Computed from prioritization, Story estimates, and team velocity; updates automatically when priority or pace changes. States: done (solid), in progress (dashed), planned (outline). Releases appear as target markers. Project settings need Velocity and Iteration Length to forecast well; start conservative.

## How the blocks nest

```
Initiative (goal)
└── Epic (step toward the goal)
    └── User Story (buildable work)
        └── Workitem (delivery coordination, iteration board only)

Project Story / Devteam Story (buildable work, root-level — takes no parent)
└── Workitem (delivery coordination, iteration board only)
```

Project and Devteam Stories sit at the root. They take no parent, so they hang beside the backbone rather than under a step — correct for genuinely cross-cutting work, and the reason a Playbook template does not use them (see *Shared conventions* in `SKILL.md`).

## Splitting guidance

- Initiative too vague to act on → break into Epics (the steps).
- Epic with one obvious implementation → it may really be a User Story.
- User Story too big for one iteration → split by option, by step in the user's flow, by data variation, or by happy-path vs edge-case. Keep each split independently valuable.
- A Story that mixes user value and technical work → keep the user value as a User Story; split the technical part into a Devteam Story only if it is genuinely cross-cutting.
