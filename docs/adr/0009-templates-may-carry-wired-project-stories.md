# A Playbook template may carry Project Stories when they are wired by dependency

This revises ADR 0005 in part. That decision excluded Project and Devteam
Stories from Playbook templates outright; the exclusion of Project Stories was
too broad, and this records the narrower rule. The Devteam exclusion and the
Workitem exclusion stand.

## What ADR 0005 got right, and what it missed

The original reasoning is sound as far as it goes. Project Stories take no parent
in the Betterplan data model, so they hang beside the backbone rather than under
a step. A Playbook exists to make visible which task belongs to which step, and
an authored item nobody can see under its step contradicts that.

What the decision missed is that **some work in a Playbook genuinely has no
single step it belongs to**, and forcing it into one lies about its scope. The
CRA playbook produced four such items:

- obtaining access to the BSI control catalogue, which is granted on request only
  and gates every control-related story in two separate Initiatives;
- establishing the company's SME status, which decides the fine exemption for the
  24-hour deadline, the PSIRT/CSIRT single-person exception, eligibility for the
  simplified technical documentation, and fee treatment by a notified body —
  four consequences in four different Initiatives;
- establishing which national authority and sanctions regime applies, which
  determines the reporting path, the market-surveillance counterpart, and the
  corrective-action exposure;
- taking stock of which announced delegated and implementing acts now exist, and
  keeping that current — fourteen are outstanding, two sources are living
  documents, one is a draft, and one guideline demands the newest published
  version on pain of silently losing conformity.

Attached to any one Epic, each of these becomes a lie about its reach. Left out,
the template is silent about work the instantiating team cannot skip.

## The missing mechanism

ADR 0005's objection was about **visibility**, and it was correct that a
reference in prose does not supply it. A `#NNN` mention reaches a reader; it does
not reach planning.

ADR 0007 supplied the mechanism after the fact. A relation that forces an order
is modelled as a real Betterplan dependency, and dependencies reach the Delivery
Timeline. A Project Story that gates visible Stories is therefore **not**
invisible: it appears as the gate it is. The catalogue access is not a floating
note beside the backbone — it is the thing that must finish before the control
stories can start, and the timeline says so.

The two decisions interlock. ADR 0005 identified a real failure mode; ADR 0007
removed its cause.

## The rule

A Playbook template may contain a Project Story when **both** hold:

1. It is genuinely cross-cutting — more than one Story in more than one place
   depends on it. A single dependant means it is not cross-cutting, and the work
   belongs inside that Story.
2. It is bound to the Stories it gates by a **modelled dependency**, not by a
   prose reference.

A Project Story with no dependency stays inadmissible. Either it gates nothing,
or it is not cross-cutting; in both cases it belongs in a User Story.

**Devteam Stories remain excluded.** They are technical work internal to the dev
team, and a template author has no dev team — the instantiating team creates
them when the need appears.

**Workitems remain excluded.** They are coordination artifacts of the executing
team on the Iteration Board, created ready or not at all. Where a clarification
has a one-to-one relationship with a Story, it becomes that Story's acceptance
criterion or description content, not a Workitem authored on the team's behalf.

## Consequences

- **The one-to-one test decides the type.** One dependant → content of that
  Story. Several dependants across several steps → Project Story with modelled
  dependencies. This is the same test the classification rules already apply; it
  was simply unavailable to templates before.
- **Reviewing a template now includes checking the dependency edges.** A
  Project Story without one is a defect, not a stylistic choice. `betterplan-storymap`
  validates this.
- **The set of Project Stories a Playbook ships with is small and argued, not
  empty and not arbitrary.** ADR 0005 noted that an earlier draft carried a
  starter set of five clarifying decisions that became User Stories instead —
  that was right for those five, which each served one step. The four above are
  a different case.
- **ADR 0005 keeps its direction-of-departure principle**: when visibility in
  the backbone and purity of classification conflict, visibility wins. This
  decision does not reverse that. It observes that a modelled dependency *is*
  visibility, so the conflict dissolves for wired items.
