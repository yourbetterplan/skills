# Defining the project goal is its own step, not part of extraction

`betterplan-extract` reads the transformed references and writes requirements,
open questions and a glossary. It was built to run without being told what the
project is for, and the first real run showed what that costs: given a folder of
EU regulation and BSI technical guidelines, it invented a plausible project goal,
flagged it as an open question, and then produced 146 sourced requirements
organised along a structure that goal implied. The content was right. The cut was
wrong — the actual goal was to make the *division of responsibility* between a
device manufacturer and its contract developer visible, which needs dimensions
the output did not have.

We therefore added a separate skill, **`betterplan-goal`**, which runs **after
`betterplan-transform` and before `betterplan-extract`**, reads the transformed
references, and writes `.betterplan/GOAL.md`. `betterplan-extract` treats that
file as a **hard precondition**: without it, it stops and points at the goal
skill rather than proceeding on an assumption. It then uses the goal to frame the
extraction, and writes `.betterplan/EXTRACTION-REPORT.md` alongside its other
output — a short account of what it extracted, how it cut it, and which calls it
made on its own. Refining the goal once the material is understood is a
**re-invocation of `betterplan-goal`**, not a feature of extraction.

The skill runs after transform, not before, because the questions worth asking
are not answerable from an empty folder. The goal of this very playbook was
reached in 37 questions over several rounds, and the sharp ones were only askable
with the corpus already read.

`betterplan-goal` is deliberately **thin**. It does not implement interviewing;
it invokes the generic `grilling` skill for that. What it owns is the *question
territory* of a Betterplan project goal, the *output contract* other skills rely
on, and *re-entry* to sharpen an existing goal. The reason that territory cannot
be left to generic grilling is that several of the decisions that shaped this
goal were only reachable with the Betterplan data model in hand — personas versus
parallel backbone strands, obligation-bearer as a tag because tags admit no
nested namespace, an Epic having exactly one Initiative as parent, Project
Stories sitting at root level. A generic interview produces a goal that then
collides with the data model.

## What `GOAL.md` holds

The sections are chosen as the ones whose absence caused the failure above, and
are our call rather than a stated requirement: **purpose** (what the endeavour
achieves, for whom), **usage context** (who reads this document and in what
situation), **roles** (who bears obligations, who benefits), **scope** (what kind
of product or subject matter, explicitly narrowed), **finish line** (what state
counts as done), **non-goals**, **backbone shape** (the Initiatives the Story Map
will carry), and **open facts** — questions only the human can answer, recorded
rather than guessed.

`GOAL.md` is authored content and may be hand-edited, unlike the generated index
files of ADR 0003. `betterplan-goal` requires `betterplan-transform` to have run,
on the same hard-precondition pattern it imposes on extraction. When the
references change after a goal was written, extraction **warns and proceeds**
rather than blocking — blocking on every re-transform would make the chain
hostile to use.

## Consequences

- **Any other grilling session calls `grilling` directly.** `betterplan-goal` is
  not a grilling entry point and must not become one; its own documentation says
  so. Goal definition is the only thing it is for.
- **The goal has more than one consumer.** Story Map authoring needs it as much as
  extraction does. This is why it could not be folded into `betterplan-extract` as
  a precondition check — a goal owned by extraction cannot be requested by anything
  else.
- **`betterplan-extract` loses the ability to run unattended on a fresh project.**
  That is the point. It stays re-runnable and incremental once a goal exists.
- `.betterplan/GOAL.md` is project data and lives in the project, next to
  `references/` and `requirements/` — never in this repo.
