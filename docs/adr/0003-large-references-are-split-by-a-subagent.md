# Large references are split by a subagent, verbatim and reconciled

`betterplan-transform` converts each source document into exactly one Markdown
file. For a 1.8 MB PDF of EU regulation that produced a 465 KB reference whose
first quarter already exceeded the reading limit of an agent's file tool at
61,427 tokens against a cap of 25,000. Working with it meant grepping for the
article structure and then reading it in five offset windows. Retrieving one
detail later costs the same again.

Documents above **50 KB** are therefore split into sections, targeting **30 KB**
per file — both parameters, not constants. The measurement behind those numbers:
125 KB of this corpus's raw text came to roughly 61,000 tokens, so about 2 KB per
1,000 tokens; 50 KB sits just under a 25,000-token cap and 30 KB leaves
headroom.

The split is done by a **subagent with a fresh context, one per document**, not
by a pattern-matching script. A script can only recognise structure from text
patterns — numbered headings, `Artikel`, `ANHANG`, `§` — and both document
families here happen to be recognisable that way, but the cuts a pattern matcher
makes are blind to meaning. The deciding argument is the problem being solved:
the goal is to keep large documents *out of the working context*. A subagent is
the one place where a 230,000-token document may be read in full, because its
context is discarded afterwards and only a short report comes back.

That choice introduces a failure mode a script does not have: **a model that cuts
can lose text.** Three rules contain it.

1. **Verbatim only.** The subagent may cut and nothing else — no summarising, no
   normalising, no smoothing. Each section file gets a generated header naming the
   source document, the section path and the line range in the original. References
   are evidence; extraction cites them down to `CRA Anh. I I.2 c` and
   `TR-3 §4.3.1 j`, and a paraphrased reference makes every such citation
   unverifiable.
2. **Report only.** The subagent returns section count, size distribution, the
   heading depth it worked at and anything anomalous — and no content. Returning
   content would put the document back into the parent context in a different
   wrapper.
3. **Mechanical reconciliation.** The parent strips the headers it knows it
   generated, concatenates the section bodies in index order, and requires the
   result to **equal the original text** — not to match its character and line
   counts. Counts were the first implementation and they are not enough: review
   probes showed that reordered sections, a soft hyphen normalised to `-`, and an
   equal-length paraphrase all pass a count comparison, and the first two are
   exactly what a helpful model does to a document this branch documents as
   deliberately carrying soft hyphens and page furniture. Counts survive only to
   phrase the failure message.

   The only tolerated divergence is one trailing newline, because every
   file-writing tool appends one; and the one `converted:` line transform.py
   stamps with the clock, because it is generated metadata rather than source
   text and comparing it would make a re-transform discard every correct split.
   Index links are validated as plain section filenames before being opened —
   an unchecked link pointing at `../<doc>.md` reports a perfect split of zero
   sections, and the documented consequence of success is deleting that file.

   On any mismatch the split is discarded, the single file is kept, and the
   discrepancy is reported loudly; operator error (bad path, undecodable file)
   exits with its own code so that a typo cannot be read as text loss. The
   parent does not take the subagent's word for it. Without this check, two
   swallowed pages surface only as a requirement nobody remembers was missing.

## Layout

```
.betterplan/references/
├── INDEX.md                         generated, lists every document
└── <slug>/
    ├── INDEX.md                     generated, lists this document's sections
    └── 01-<section-slug>.md …       verbatim section, generated header
```

Both index files are **pure generated output** carrying a do-not-edit header.
`betterplan-transform` keeps its promise of being re-runnable and overwriting
everything, which is what makes maintenance of the index a non-problem: it is
never maintained, only re-derived. Hand-written notes belong elsewhere under
`.betterplan/`, never in `references/`.

## Consequences

- **The whole-document file is not kept alongside the sections.** Two copies of the
  same text drift apart the moment one is touched, and grep works across the
  sections just as well.
- **`betterplan-extract` must read `references/` recursively** and prefer the index
  files as entry points. Its current flat `references/*.md` glob breaks.
- **Where no subagent tool exists** — pi, Codex, other harnesses — transform leaves
  the document unsplit and says so in its report. A pattern-matching fallback was
  rejected: two splitters producing different structures means nobody can tell
  which layout they are looking at.
- `betterplan-transform` stops being a pure script invocation. It becomes a script
  step followed by N agent steps, and its documentation has to say that plainly.
