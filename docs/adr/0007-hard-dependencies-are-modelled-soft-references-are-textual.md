# Hard dependencies are modelled, soft references stay textual

The `create-*` skills said nothing about relations between items. In practice
that meant every relation ended up in prose — "this follows from the category
decision", "see the SBOM story" — which reads fine and plans nothing. Betterplan
exposes `create_dependency`, `list_dependencies` and `delete_dependency`, and the
Delivery Timeline uses them; a relation that never becomes a dependency object is
invisible to the one view that is supposed to show when things finish.

The distinction we draw is between **gating** and **informing**.

A **hard dependency** forces an order: B cannot start, or cannot be completed,
before A is done. In project-management terms these are the relations that form a
critical path. They are modelled as real dependency objects.

A **soft reference** explains or contrasts without forcing an order. It stays a
`#NNN` reference in the description, and creates no dependency object.

The CRA playbook makes the difference concrete. "Determine the product category"
genuinely gates "choose the conformity route", which genuinely gates "carry out
the conformity assessment" — a chain with a fixed legal deadline at the end of
it, which is exactly what a timeline needs to see. By contrast, "the SBOM is
produced in the build step" merely informs the story about supplying users with
an SBOM; forcing an order there would block work that can proceed in parallel.

The error runs in both directions, which is why the guidance asks for a
deliberate call rather than a default. Over-modelling serialises work that could
run concurrently and makes the forecast pessimistic; under-modelling makes it
optimistic and wrong. Neither is safe.

## Intermediate formats

A consequence that is easy to miss: where a Story Map is drafted outside
Betterplan first — as Markdown in Git, so the map can be reviewed and versioned
before anything is created — the intermediate format must be able to express hard
dependencies, keyed by a stable item id in frontmatter. A format that cannot
carry them is unusable as a precursor, because on import the dependencies would
have to be reconstructed from prose, which is exactly the failure this decision
exists to prevent.

This does not change the **single-item** Markdown fallback in
`betterplan-workflow`, which deliberately keeps structural fields out of the
artifact and names them in the chat reply instead. That fallback hands one item
to a human to paste; a map draft is a machine-readable precursor to a bulk
import. Different artifacts, different rules.

## Consequences

- **`betterplan-workflow` carries the rule**, since it holds the conventions all
  `create-*` skills share. Each skill applies it at its own scale.
- **`betterplan-storymap` (ADR 0006) must define the frontmatter schema** for its
  Markdown draft, including item ids and dependency edges.
- **Dependencies are a review surface.** A modelled critical path can be argued
  with; a prose hint cannot. Expect dependency edges to be questioned during
  review, and treat that as the point rather than friction.
