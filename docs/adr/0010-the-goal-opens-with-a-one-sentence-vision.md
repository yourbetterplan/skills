# The goal opens with a one-sentence vision

`GOAL.md` had eight anchors and began with `goal:purpose` — several paragraphs
on what the endeavour produces, for whom, with which boundaries. Useful, and
the wrong thing to start with. A reader arriving at the CRA goal met three
paragraphs about Story Maps, templates and citation practice before learning
what anyone was trying to achieve.

`GOAL.md` now opens with `goal:vision`: **one sentence** saying what this is
about. *"Ein Angebot erstellen, das wir einreichen können."* · *"Personen einen
guten Start in diesen Prozess geben."* · *"Nutzern ermöglichen, ihr Gerät ohne
Fachwissen sicher einzurichten."*

## Why it is not folded into the purpose

The two answer different questions and collapse into each other if not kept
apart. The vision answers **why at all**, in the human's own words, and is
allowed to be rough. The purpose answers **what exactly comes out** and is
worked. Keeping the vision separate gives the project something to drift
*against*: when an Initiative no longer serves the sentence, that is visible,
which it is not against three paragraphs that already contain every
qualification.

It also has a consumer the purpose does not have. On import into Betterplan the
vision becomes the project's description and vision field. One sentence fits
there; a purpose section does not.

## Why it is asked first, before reading the material

`betterplan-goal` otherwise insists on reading the transformed references before
asking anything, because a goal formed without looking at the material is a
guess. The vision is the exception: it is the human's intent, not a finding from
the corpus, and asking for it costs one question with no preparation. In return
it tells the agent what to look for while reading.

## Why a missing vision does not block extraction

`betterplan-extract` treats the eight load-bearing anchors as a hard
precondition and stops without them. `goal:vision` is deliberately **not** among
them: how requirements get cut is decided by purpose, roles, scope and finish
line, and the vision adds nothing to that decision. Making it a gate would
invalidate every `GOAL.md` written before the anchor existed while improving no
extraction. Extraction names the gap in its report and proceeds.

`betterplan-storymap` is stricter in substance but gentler in form: it checks
for the vision before anything else and, when it is missing, **asks one question
and writes the answer** rather than aborting or redirecting. Sending someone who
wants to build a map into a different skill for one sentence is worse than the
small boundary violation of writing it.

## Consequences

- **`goal:vision` is the only section another skill may author.** Everything
  else in `GOAL.md` belongs to `betterplan-goal`; a deviation there is a finding,
  not a silent edit. Stated in both skills.
- **Nine anchors, vision first.** The order is part of the contract, because the
  file is read top to bottom by humans.
- **A template has an unresolved second vision.** The sentence an instantiating
  team inherits is plausibly not the sentence of building the template. An
  earlier draft of this decision legislated that the team's sentence wins; that
  was wrong for the playbook repo itself, whose `GOAL.md` describes building a
  template. The rule is now simply: the vision describes the endeavour that
  `GOAL.md` describes. Whether a template ships a second sentence for its
  instances is **left open** and surfaces at import time — recorded rather than
  invented.
