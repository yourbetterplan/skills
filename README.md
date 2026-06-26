# Betterplan plugin

A collection of skills for creating well-formed Betterplan building blocks and classifying work into the right type, based on the Betterplan method (Scope → Prepare → Build → Insight).

When the Betterplan MCP server is connected, the skills create items directly in the app through its tools. Without it, they fall back to clean Markdown you can paste in. The content is the same either way — only the delivery differs.

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

No configuration required for the Markdown fallback.

To create items directly in the app, connect the Betterplan MCP server (OAuth) separately in Claude. It is not bundled in this plugin. Once its tools are present, the skills prefer them automatically (content → `title` + `description`, everything else as arguments); without it they output Markdown. The MCP describes its own tools and fields at runtime, so the plugin does not bundle an API schema.

`skills/betterplan-workflow/references/data-model.md` keeps only the conceptual mapping the MCP does not convey: the `type` values (`initiative`, `epic`, `story`, `project`, `dev`, `workitem`), how maturity maps to date fields, content versus metadata, and the bug rule.

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
