# Betterplan method — deep dive

Background for classification and structuring decisions.

## The Story Map (Scope)

The Story Map is the heart of Betterplan and the shared reference everyone uses.

- **Left → right**: the major steps / sections of the endeavor, read like a narrative.
- **Top → bottom**: importance and options — most important on top, supplementary below.
- **Three levels of granularity**: Initiatives (goals) → Epics (steps) → Stories (options/tasks under an epic).
- **Releases**: horizontal swimlanes / milestones. Assign Stories to a Release to structure the endeavor by time as well as content.

Screenplay test: the Story Map tells the story of the user within the endeavor. Goals become Initiatives; the steps to reach them become Epics. If the story reads right, the structure is right.

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
    └── User Story / Project Story / Devteam Story (buildable work)
        └── Workitem (delivery coordination, iteration board only)
```

Project and Devteam Stories often sit under an Epic too, but may also stand alone when they are cross-cutting.

## Splitting guidance

- Initiative too vague to act on → break into Epics (the steps).
- Epic with one obvious implementation → it may really be a User Story.
- User Story too big for one iteration → split by option, by step in the user's flow, by data variation, or by happy-path vs edge-case. Keep each split independently valuable.
- A Story that mixes user value and technical work → keep the user value as a User Story; split the technical part into a Devteam Story only if it is genuinely cross-cutting.
