# A Playbook template contains no Project or Devteam Stories

> **Partly superseded by ADR 0009.** The exclusion of **Project Stories** was too
> broad: a template may carry one when it is genuinely cross-cutting *and* bound
> to the Stories it gates by a modelled dependency — which is the visibility this
> decision asked for and could not yet obtain. ADR 0007 supplied the mechanism.
> The **Devteam Story** and **Workitem** exclusions below stand unchanged, as
> does the direction-of-departure principle.

A Playbook exists to make visible, at a glance, which task belongs to which step
of the journey. Its Story Map is read left to right as a narrative, and that
narrative is the product.

Project and Devteam Stories sit at **root level** in the Betterplan data model —
they take no parent and therefore hang beside the backbone rather than under a
step. In an ordinary project that is correct and useful: cross-cutting
organisational and technical work genuinely has no single step it belongs to. In
a Playbook template it is self-defeating. An authored item that cannot be seen
under the step it belongs to contradicts the one thing the template is for.

A Playbook template therefore contains **only Initiatives, Epics and User
Stories**. Project and Devteam Stories are created on the fly during execution,
by the team doing the work, when the need appears.

This is a deliberate departure from the classification rules, and the direction
of the departure matters: when visibility in the backbone and purity of
classification conflict, **visibility wins**. A regulatory obligation is a clear
demand from the source material; it has to be visible, and an item that cannot be
placed under its step is not visible. Where that forces a clarifying decision
into User Story shape, the beneficiary is found on the company side — *"as a
manufacturer I want to know early which conformity route applies to my product,
so that I do not discover a third-party assessment is required shortly before
market entry"* — which keeps it consistent with the beneficiary rule rather than
breaking it.

## Consequences

- The set of Project Stories a Playbook ships with is **empty**, not small. Earlier
  drafts of this decision carried a starter set of five clarifying decisions; they
  became User Stories under their Epic instead.
- A team instantiating a Playbook will add root-level work of its own. That is
  expected and is not a gap in the template.
- Should Betterplan ever allow a Project Story to take an Epic as parent, this
  decision should be revisited — the reason for it is a data-model constraint, not
  a methodological preference.
