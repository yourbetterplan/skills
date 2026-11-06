# A Playbook compiles to a Template; it is not one

Betterplan already has Templates: `GET /templates` lists them, each is a file
whose id is its filename, and `GET /templates/{id}` returns something postable to
`POST /projects/import` unchanged. The obvious move was therefore to make
`betterplan-build-playbook` author template JSON directly. We decided instead
that a **Playbook Definition** is its own authored artifact — a YAML Story Map
plus the transformed reference material it was derived from — and that the
template file is *generated output*, validated against the live
`ProjectImportRequest` schema before it is handed over.

The reason is that a template file has nowhere to put the things that make a
Playbook maintainable: the regulations and standards it encodes, why a process
step exists, which options were considered for it. That material is the bulk of
the authoring effort and it has to survive for the next person to revise the
Playbook a year later. A JSON array of tasks cannot hold it, and a Playbook whose
provenance lives only in someone's memory cannot be revised, only rewritten.

## Consequences

- There is a compile step, so there is code — a Node validator in
  `betterplan-compile-playbook/scripts/`. This repo otherwise ships only
  Markdown, and that is a real cost we accepted rather than hand-check payloads
  against a 330 KB schema.
- The authored YAML is the editable thing; the generated JSON is never
  hand-edited. Anyone who edits it loses the change on the next compile.
- Instantiating a Template copies its Story Map and regenerates every UUID, so
  **a Playbook revision can never reach projects already created from it.** The
  version in `playbook.yml` records which revision a project came from; it is not
  a migration mechanism, and there is no plan to build one.
