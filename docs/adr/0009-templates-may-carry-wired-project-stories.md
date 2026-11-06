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

## What makes a parentless item visible

ADR 0005's objection was about **visibility**. Two things supply it, and they
are not equivalent:

- A **modelled dependency** reaches planning: it shows up in the Delivery
  Timeline as the gate it is. Where an order is genuinely forced — catalogue
  access before control work — ADR 0007 already requires modelling it, and the
  visibility follows for free.
- A **`#NNN` reference** from the affected Stories reaches a reader. That is
  less than planning visibility, but it is not nothing, and it is a legitimate
  binding. Not every cross-cutting item gates anything: a company-wide status
  that changes *how* four Stories are done, without blocking any of them, has no
  dependency to model and is still cross-cutting.

So the dependency is a **strong indicator** of cross-cuttingness, not an
admission requirement. Requiring it would exclude exactly the items that are
most clearly organizational — the ones that inform rather than block.

## The rule

A Playbook template may contain a Project Story when it is **genuinely
cross-cutting**: more than one Story, in more than one place, depends on it or
is shaped by it. **A single dependant means it is not cross-cutting** — the work
belongs inside that Story, as acceptance criterion or description content.

Where a genuine ordering exists, model it as a dependency (ADR 0007 requires
that anyway). Where none exists, bind it by `#NNN` reference from the Stories it
shapes. Either way, **name the dependants when proposing it** — an item whose
reach cannot be stated is an item whose reach was not checked.

**The real safeguard is scarcity, not a mechanical test.** Project Stories are to
be used sparingly. The bar is not "is this cross-cutting enough to be allowed"
but "would the instantiating team miss something essential if this were not its
own item". Most candidates fail that bar: they fit inside a User Story, or they
are the *Why* of one and belong in its Context. A template that accumulates
root-level items has drifted back into the failure ADR 0005 named, by a
different route.

**Devteam Stories remain excluded.** They are technical work internal to the dev
team, and a template author has no dev team — the instantiating team creates
them when the need appears.

**Workitems remain excluded.** They are coordination artifacts of the executing
team on the Iteration Board, created ready or not at all. Where a clarification
has a one-to-one relationship with a Story, it becomes that Story's acceptance
criterion or description content, not a Workitem authored on the team's behalf.

## Consequences

- **The one-to-one test decides the type.** One dependant → content of that
  Story. Several dependants across several steps → Project Story. This is the
  same test the classification rules already apply; it was simply unavailable to
  templates before.
- **Reviewing a template includes asking how many root-level items it carries.**
  Not whether each is defensible in isolation — each usually is — but whether
  the set stayed small. `betterplan-storymap` requires the reach to be stated
  per item, which makes the question answerable.
- **The set of Project Stories a Playbook ships with is small and argued, not
  empty and not arbitrary.** ADR 0005 noted that an earlier draft carried a
  starter set of five clarifying decisions that became User Stories instead —
  that was right for those five, which each served one step. The four above are
  a different case.
- **ADR 0005 keeps its direction-of-departure principle**: when visibility in
  the backbone and purity of classification conflict, visibility wins. This
  decision does not reverse that. It observes that a modelled dependency *is*
  visibility, so the conflict dissolves for wired items.
