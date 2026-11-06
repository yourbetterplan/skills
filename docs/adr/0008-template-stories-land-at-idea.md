# Template Stories land at Idea, with fully worked content

The maturity rules treat **Idea** as thin: a short distillation of a sentence
someone said, placed in the map, refined later. **Ready** is the state where
nothing is open. A Playbook template breaks that correspondence, and it took
authoring one to see why.

A template Story is written for a team the author will never meet, about a
product the author has never seen. The author can and should work it out in
full — the beneficiary's perspective, the context, acceptance criteria as
observable states, the source citation, what is out of scope. What the author
cannot do is answer the product-specific questions: which controls apply, which
support period, which product class, which conformity route. Those are open
questions, and open questions block Ready.

So the two obvious options are both wrong. Marking such a Story **Ready** lies
about the open questions and invites the instantiating team to skip a
conversation it must have. Leaving it genuinely thin at **Idea** throws away the
one thing a template is for: the author has read the source material and the
team has not.

We therefore separate **content depth** from **maturity**. Template Stories are
worked as far as the material allows and still carry maturity **Idea**. The
maturity tag records the state of the *agreement*, not the amount of text: the
Discovery dialogue with the instantiating team has not happened. A template
Story is a fully argued proposal, not a settled one.

The open questions stay written down. They are not a defect of the template —
they are its handover: precisely the decisions the team must make, already
located in the right Story.

The same reasoning applies to personas. A persona is supposed to be a concrete
audience rather than a role label, and a template cannot name an audience it has
never seen. It therefore names the audience *types* the source material itself
distinguishes — for the CRA playbook, the integrator, administrator and end user
that TR-03183-1 §4.2 separates — and states in each persona that the
instantiating team sharpens it to its actual product.

## Consequences

- **A template's Story count never moves off Idea by itself.** The first
  maturity transitions happen in the instantiating project, which is correct.
- **Reviewing a template cannot use maturity as a quality signal.** The quality
  signal is coverage of the source material (ADR 0006's map step owns the check),
  not how far right the Stories have moved.
- **`betterplan-create-story` keeps its rule** that open questions block Ready.
  This is not an exception to it; it is a different reading of what Idea means
  when the author and the eventual owner are different people.
