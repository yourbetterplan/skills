# Betterplan plugin

A collection of skills for creating well-formed Betterplan building blocks and classifying work into the right type, based on the Betterplan method (Scope → Prepare → Build → Insight).

The skills produce clean Markdown you can paste into Betterplan today. They are written so they can later create items directly through the Betterplan MCP server once it is connected.

## Components

| Skill | What it does | Triggers on |
|---|---|---|
| `betterplan-workflow` | The brain: explains the method and classifies a request into the right building block; holds the shared conventions (maturity, open/closed, story points, output format). | "is this an epic or a story", "how should I structure this", "help me plan in Betterplan" |
| `create-initiative` | Creates an Initiative — a large goal that sets direction. | "create an initiative", describing a big outcome |
| `create-epic` | Creates an Epic — a step the user takes toward a goal. | "create an epic", "break this initiative into steps" |
| `create-story` | Creates a Story — User, Project, or Devteam — with type-specific guidance in `references/`. | "write a user story", "add a project/devteam story" |
| `create-workitem` | Breaks a Ready Story into Workitems for the Iteration Board. | "break this into workitems", "split into tasks" |

## How they fit together

```
Initiative  →  Epic  →  Story (User / Project / Devteam)  →  Workitem
   goal         step          buildable work                  delivery step
```

Start with `betterplan-workflow` when the type is unclear; it routes to the matching `create-*` skill. Each `create-*` skill also triggers directly (e.g. "write a user story"). The shared rules live only in `betterplan-workflow`, so the creation skills stay small.

## Setup

No configuration required. Skills output Markdown.

A Betterplan MCP server (OAuth) is planned to let the skills read and write items directly in the app. It is not part of this plugin yet. When it is connected, the same classification and conventions apply — items are created through the MCP tools instead of Markdown, mapping content to `title` + `description` and everything else to fields.

The API/MCP data model is documented in `skills/betterplan-workflow/references/data-model.md`: the `type` enum (`initiative`, `epic`, `story`, `project`, `dev`, `workitem`), how maturity maps to date fields, and which fields are structure versus content.

## Usage examples

- "We want customers to return orders themselves." → `create-initiative`
- "Break the Search initiative into epics." → `create-epic`
- "Write a user story for autocomplete in search." → `create-story` (User Story)
- "Record that we decided to ship web-only first." → `create-story` (Project Story)
- "We need a CI pipeline." → `create-story` (Devteam Story)
- "Break the autocomplete story into workitems." → `create-workitem`
- "Is 'set up the build pipeline' a story or something else?" → `betterplan-workflow`

## Reference

Method details and terminology: https://www.yourbetterplan.com/en/blog/getting-started
