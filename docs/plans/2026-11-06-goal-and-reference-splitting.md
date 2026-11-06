# Goal Definition and Reference Splitting — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make project-goal definition an explicit step in the Betterplan skill chain, and stop large reference documents from being unusable monoliths.

**Architecture:** Four skills, one new. `betterplan-goal` runs between transform and extract and writes `.betterplan/GOAL.md`; `betterplan-extract` requires that file and becomes an agent process rather than the script it never had; `betterplan-transform` gains a subagent splitting step guarded by a deterministic reconciliation script; `betterplan-workflow` records the authoring conventions the goal work surfaced. Everything except one Python script is Markdown.

**Tech Stack:** Markdown skills (RFC 2119 modal verbs), Python 3.12+ with `uv` for `betterplan-transform/scripts/`, pytest for the one piece of real code.

**Spec:** `docs/adr/0002-goal-definition-is-its-own-step.md`, `docs/adr/0003-large-references-are-split-by-a-subagent.md`, `docs/adr/0004-user-stories-carry-the-beneficiary-perspective.md`, `docs/adr/0005-playbook-templates-contain-no-project-or-devteam-stories.md`

## Global Constraints

- Modal verbs in skill documents follow BCP 14 (RFC 2119, RFC 8174) and are normative only in capitals.
- Skill output language follows the user's language; default English.
- Custom Betterplan tags are `project:<value>` — exactly one colon, no second colon inside the value.
- Tag values are **short**; card space is limited. Semantic grouping is carried by colour in `settings.tagDefinitions`, never by a category word inside the value. Tags with no grouping keep the default colour.
- Betterplan titles carry no index or sequence prefixes.
- Split threshold **50 KB**, section target **30 KB**, both exposed as parameters, never as literals in prose.
- Section files are **verbatim**; only a generated header may be added.
- Reconciliation is **exact** after stripping generated headers — no tolerance.
- No subagent tool available → leave the document unsplit and say so in the report.
- `GOAL.md` is hand-editable; every `INDEX.md` is generated output carrying a do-not-edit header.
- Python code in a skill must not ship a `.venv` (see `.gitignore`); the manifest stays, the environment does not.

## Review Focus

Five conditions the ADRs imply that no task's happy path exercises, most likely to bite first:

1. **A document over the threshold whose largest single section still exceeds the target** — must stay whole; ADR 0003 makes a section indivisible. Test in Task 3.
2. **Source text with CRLF line endings or a trailing-newline difference** — must not make a correct split fail reconciliation. Test in Task 3.
3. **Re-running transform where a split already exists** — must regenerate cleanly, never nest `<slug>/<slug>/` or leave orphaned section files from a previous run. Test in Task 3.
4. **`GOAL.md` present but a stub** — empty, or missing the required sections; extract must treat it as missing rather than proceed. Verification step in Task 5.
5. **A reference with no recognisable structure** (scanned PDF, garbled text layer) — must end unsplit with a stated reason, not as an empty `INDEX.md`. Verification step in Task 4.

---

### Task 1: Betterplan authoring conventions

Pure documentation, no dependency on any other task. Implements ADR 0004 and ADR 0005.

**Files:**
- Modify: `betterplan-workflow/SKILL.md`
- Modify: `betterplan-workflow/references/method-deep-dive.md:48`

**Interfaces:**
- Consumes: nothing
- Produces: the conventions Task 7 applies when writing the CRA goal's backbone shape

- [ ] **Step 1: Delete the false sentence**

In `method-deep-dive.md`, remove *"Project and Devteam Stories often sit under an Epic too, but may also stand alone when they are cross-cutting."* It contradicts `data-model.md` and `SKILL.md:192`, both of which are correct.

- [ ] **Step 2: Verify no other place repeats the claim**

Run: `grep -rn "under an Epic" betterplan-workflow/`
Expected: no hit that says Project or Devteam Stories may have an Epic parent.

- [ ] **Step 3: Add the perspective rule to `SKILL.md`**

New subsection under *Shared conventions*. States: a User Story is written from the beneficiary's perspective, not the obligated party's; the obligation-bearer is carried as a bare role tag (`project:Hersteller`, `project:Zulieferer`); authorities and other counterparties appear in Story text as the trigger of an obligation, never as a persona.

- [ ] **Step 3a: Add the tag-brevity rule to `references/data-model.md`**

Extend the existing *Tags — namespacing rules* list: values stay **short** because card space is limited, semantic grouping is carried by colour in `settings.tagDefinitions`, and a category word inside the value is the mistake this rule prevents — it duplicates what colour already says and doubles the width. Tags without a grouping keep the default colour.

- [ ] **Step 4: Replace the classification criterion in `SKILL.md:67-69`**

The two-part test from ADR 0004 replaces the current step 4 of the classification walk: *direction* (benefit aimed at someone nameable outside the project team) then *deliverable* (something handed over that gives that beneficiary a capability). State explicitly that this overrides the `documentation` bucket — a delivered document with an audience is a User Story.

- [ ] **Step 5: Document personas in `SKILL.md`**

Personas are real Betterplan objects (`create_persona`, `assign_persona`, `archive_persona`), project-scoped, and must exist before assignment. Recording one is **optional**: the rule requires the beneficiary perspective, not the object. Name what a usable persona is — the concrete audience, never a role label that could be anyone, consistent with the existing "Be specific, not generic" rule.

- [ ] **Step 6: Add the playbook-template convention to `SKILL.md`**

A Playbook template contains only Initiatives, Epics and User Stories. Project and Devteam Stories are created during execution. Give the reason — root-level items are invisible in the backbone, which defeats a template whose purpose is showing which task belongs to which step.

- [ ] **Step 7: Commit**

```bash
git add betterplan-workflow/
git commit -m "docs(workflow): beneficiary perspective, classification criterion, personas"
```

---

### Task 2: The `betterplan-goal` skill

Implements ADR 0002. Includes its own registration, because an unregistered skill cannot be invoked and the task's deliverable is an invocable skill.

**Files:**
- Create: `betterplan-goal/SKILL.md`
- Modify: `package.json` (`pi.skills` array)
- Modify: `.claude-plugin/marketplace.json` (`plugins` array)
- Modify: `README.md` (skill table)

**Interfaces:**
- Consumes: `grilling` (external skill, invoked for method)
- Produces: `.betterplan/GOAL.md` with the eight sections named below — Task 5 reads this contract

- [ ] **Step 1: Write `betterplan-goal/SKILL.md`**

Frontmatter `name: betterplan-goal`, `metadata.version: "0.1.0"`, and a description that routes on *goal*, *Ziel*, *what is this project for* — never on *grill*.

Body states: precondition `betterplan-transform` has run and `.betterplan/references/` exists, otherwise stop and point at transform. Reads the references before asking anything. Invokes `grilling` for the method and does **not** reimplement interviewing. Re-invocation on an existing `GOAL.md` reads it first and sharpens rather than restarting. Carries the boundary sentence verbatim in intent: this skill is not a grilling entry point; any other grilling session invokes `grilling` directly.

Writes `.betterplan/GOAL.md` with eight sections. Headings are prose in the user's language, each carrying a **stable anchor** so the contract survives translation:

```
## <heading in the user's language> <!-- goal:purpose -->
```

The eight anchors are `goal:purpose`, `goal:usage-context`, `goal:roles`, `goal:scope`, `goal:finish-line`, `goal:non-goals`, `goal:backbone`, `goal:open-facts`. *(Anchors rather than fixed English headings are our call, made during plan review: the skill writes in the user's language, so a heading-text check would pass in English and fail in German.)*

- [ ] **Step 2: Verify the skill is discoverable and self-consistent**

Run: `grep -c "grilling" betterplan-goal/SKILL.md`
Expected: at least 2 — one invocation instruction, one boundary statement.

Run: `grep -n "betterplan-transform" betterplan-goal/SKILL.md`
Expected: the precondition is named.

- [ ] **Step 3: Register in `package.json`**

Append `"./betterplan-goal"` to `pi.skills`, positioned after `"./betterplan-transform"` and before `"./betterplan-extract"` so the array reads in chain order.

- [ ] **Step 4: Register in `.claude-plugin/marketplace.json`**

Add a `plugins` entry copying the shape of the existing ones: `name`, `source: "./"`, `skills: ["./betterplan-goal"]`, `strict: false`, `description`, `version: "0.1.0"`, `author`, `homepage`, `repository`, `license: "MIT"`, `category: "planning"`, `keywords`.

- [ ] **Step 5: Verify the manifest still parses**

Run: `node -e "JSON.parse(require('fs').readFileSync('.claude-plugin/marketplace.json','utf8')).plugins.forEach(p=>console.log(p.name))"`
Expected: the list ends with `betterplan-goal` present exactly once.

- [ ] **Step 6: Add the README row**

One row in the skill table between `betterplan-transform` and `betterplan-extract`, and add the skill to the install prose that lists the others.

- [ ] **Step 7: Commit**

```bash
git add betterplan-goal/ package.json .claude-plugin/marketplace.json README.md
git commit -m "feat(goal): add betterplan-goal, the project-goal step before extraction"
```

---

### Task 3: Split reconciliation script

The only real code in this plan. Implements the third guard rule of ADR 0003 — and folds in the missing Python manifest, because the test harness needs one and the declared runtime dependencies currently have no home.

**Files:**
- Create: `betterplan-transform/scripts/verify_split.py`
- Create: `betterplan-transform/scripts/pyproject.toml`
- Create: `betterplan-transform/scripts/tests/test_verify_split.py`

**Interfaces:**
- Consumes: nothing
- Produces: `verify_split(original: Path, section_dir: Path) -> SplitVerdict`, where `SplitVerdict` is a dataclass with `ok: bool`, `original_chars: int`, `section_chars: int`, `original_lines: int`, `section_lines: int`, `reason: str | None`. Task 4 calls this from the skill document.

- [ ] **Step 1: Write `pyproject.toml`**

Project name `betterplan-transform-scripts`, `requires-python = ">=3.12"`, dependencies `python-docx` and `openpyxl` (both already imported by `transform.py`), dev dependency group with `pytest`. Note in a comment that the two runtime dependencies were previously undeclared, so DOCX and XLSX conversion could not work from a clean checkout.

- [ ] **Step 2: Write the failing tests**

```python
def test_exact_match_passes(tmp_path):
    # original of 3 lines, split into 2 sections each carrying a 2-line header
    verdict = verify_split(original, section_dir)
    assert verdict.ok
    assert verdict.section_chars == verdict.original_chars

def test_dropped_line_fails(tmp_path):
    # one section is missing its last line
    verdict = verify_split(original, section_dir)
    assert not verdict.ok
    assert "line" in verdict.reason

def test_crlf_source_passes(tmp_path):
    # original uses \r\n, sections use \n — normalised before counting
    assert verify_split(original, section_dir).ok

def test_oversized_indivisible_section_passes(tmp_path):
    # a single section far above the target is not an error here
    assert verify_split(original, section_dir).ok

def test_stale_section_from_previous_run_fails(tmp_path):
    # section_dir holds an extra file not accounted for by the original
    verdict = verify_split(original, section_dir)
    assert not verdict.ok
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --directory betterplan-transform/scripts pytest tests/ -v`
Expected: FAIL — `verify_split` not defined.

- [ ] **Step 4: Implement `verify_split(original, section_dir)` in `verify_split.py`**

Strips the generated header from each section file by its own delimiter, normalises line endings before counting, sums characters and lines across sections in `INDEX.md` order, and compares exactly against the original. `INDEX.md` itself is excluded from the sum; a file in `section_dir` that the index does not list is a failure, which is what catches leftovers from an earlier run. Expose a `__main__` entry so the skill can call it as a command.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run --directory betterplan-transform/scripts pytest tests/ -v`
Expected: 5 passed.

- [ ] **Step 6: Verify the existing converter still runs**

Run: `uv run --directory betterplan-transform/scripts python3 transform.py --project-dir <a folder with one small .md> --dry-run`
Expected: unchanged output; adding the manifest broke nothing.

- [ ] **Step 7: Commit**

```bash
git add betterplan-transform/scripts/
git commit -m "feat(transform): verify a split loses no text, and declare the Python deps"
```

---

### Task 4: Reference splitting in `betterplan-transform`

Implements the rest of ADR 0003.

**Files:**
- Modify: `betterplan-transform/SKILL.md`

**Interfaces:**
- Consumes: `verify_split` from Task 3
- Produces: the `references/<slug>/INDEX.md` layout that Task 5 teaches extract to read

- [ ] **Step 1: Document the two-phase shape**

Rewrite the *Aufruf* section so the skill is explicitly a script step followed by agent steps, not a single command. Phase 1 unchanged: `transform.py` converts each source to one Markdown file. Phase 2: for every reference above the threshold, dispatch one subagent with a fresh context.

- [ ] **Step 2: Write the subagent brief**

The brief states: read the reference, derive its section structure, write `references/<slug>/INDEX.md` and `<slug>/NN-<section-slug>.md`, **cut verbatim only** — no summarising, normalising or smoothing — add the generated header naming source document, section path and original line range, keep a recognised section whole even when it exceeds the target, and return **only** a report: section count, size distribution, heading depth used, anomalies. No content in the return value.

- [ ] **Step 3: Document the guards**

After each subagent returns, run `verify_split`. On failure: discard the section directory, keep the single file, report loudly. Where no subagent tool exists, skip phase 2 entirely and record in the report that the document is unsplit. Where a document has no recognisable structure, the subagent leaves it unsplit with a stated reason rather than writing an `INDEX.md` with one entry.

- [ ] **Step 4: Document the index files and the re-run promise**

`references/INDEX.md` lists every document; `<slug>/INDEX.md` lists that document's sections. Both are generated and carry a do-not-edit header. Re-running replaces a `<slug>/` directory wholesale rather than merging into it. State that the whole-document file is not kept beside the sections, and why.

- [ ] **Step 5: Verify against the real corpus**

Run the full chain against `playbooks/cra/`, which holds one 465 KB and three 39–204 KB references.
Expected: the 39 KB document stays unsplit; the other four are split; every `verify_split` passes; no section file exceeds the target except where a single section genuinely does.

- [ ] **Step 6: Commit**

```bash
git add betterplan-transform/SKILL.md
git commit -m "feat(transform): split oversized references via subagent, verbatim and verified"
```

---

### Task 5: `betterplan-extract` as an agent process

Implements the extract half of ADR 0002 and the recursive-read consequence of ADR 0003. Replaces a document that describes a program which has never existed: `extract.py`, `--dry-run`, `--force` and modification-date incrementality are all currently promised and none are real.

**Files:**
- Modify: `betterplan-extract/SKILL.md`

**Interfaces:**
- Consumes: `.betterplan/GOAL.md` contract from Task 2; the `references/<slug>/INDEX.md` layout from Task 4
- Produces: `.betterplan/EXTRACTION-REPORT.md`

- [ ] **Step 1: Remove the fictional script**

Delete the *Setup* and *Aufruf* sections describing `uv sync`, `extract.py`, `--project-dir`, `--dry-run` and `--force`, and the *Inkrementell* paragraph that attributes incrementality to script logic.

- [ ] **Step 2: Document the precondition**

`.betterplan/GOAL.md` must exist and carry its required sections. Missing, empty, or reduced to section headings with no content counts as missing: stop and point at `betterplan-goal`. Do not proceed on an assumed goal — state that this rule exists because the first run did exactly that and produced a correct inventory cut along the wrong structure.

- [ ] **Step 3: Document reading the references**

Read `references/` **recursively**, entering through `references/INDEX.md` and each `<slug>/INDEX.md`, pulling section files only as needed. Replace the current flat `references/*.md` instruction.

- [ ] **Step 4: Document goal-framed extraction and the report**

The goal frames what the categories are and how requirements are cut. On finishing, write `.betterplan/EXTRACTION-REPORT.md`: what was read, how the output was cut and why, which calls were made without instruction, what was left out, and a proposed sharpening of the goal — with the note that sharpening means re-invoking `betterplan-goal`, not re-running extraction. In chat, surface only enough to decide whether to read on or stop.

- [ ] **Step 5: Document what incrementality now means**

Re-runs preserve `<!-- manual -->` sections and compare timestamps of references against outputs; a reference newer than the outputs it fed is reported. When references changed after the goal was written, warn and proceed — never block.

- [ ] **Step 6: Verify the document promises nothing that does not exist**

Run: `grep -nE "extract\.py|--dry-run|--force|uv sync" betterplan-extract/SKILL.md`
Expected: no matches.

- [ ] **Step 7: Commit**

```bash
git add betterplan-extract/SKILL.md
git commit -m "fix(extract): describe the agent process it is, require a goal, read references recursively"
```

---

### Task 6: Re-vendor into the playbooks repo

Different repository: `/Users/torsten/werkbank/betterplan/playbooks`.

**Files:**
- Modify: `playbooks/.agents/skills/betterplan-{transform,extract}/`
- Create: `playbooks/.agents/skills/betterplan-goal/`
- Modify: `playbooks/skills-lock.json`

**Interfaces:**
- Consumes: the four skills as committed by Tasks 1–5
- Produces: a working chain in the playbooks repo

- [ ] **Step 1: Find the sync command**

The vendoring is done by the `skills` npm package (the one the README links for other agents), which owns `skills-lock.json` and computes `computedHash`.

Run: `npx skills --help`
Expected: the subcommand that re-reads `skills-lock.json` and refreshes local sources. Do **not** hand-copy the directories — a hand-copy leaves `computedHash` stale, and nothing will tell you.

- [ ] **Step 2: Re-sync the vendored copies**

Run the subcommand found in Step 1 from the playbooks repo root.

- [ ] **Step 2: Verify the lock file**

Expected: `betterplan-goal` present; `computedHash` changed for `betterplan-transform`, `betterplan-extract` and `betterplan-workflow`; the five `mattpocock/skills` entries untouched.

- [ ] **Step 3: Verify the symlinks still resolve**

Run: `/bin/ls -L playbooks/.claude/skills/`
Expected: every entry resolves; a new `betterplan-goal` link exists.

- [ ] **Step 4: Commit in the playbooks repo**

```bash
git -C playbooks add .agents/skills .claude/skills skills-lock.json
git -C playbooks commit -m "chore: re-link betterplan skills after the goal step was added"
```

---

### Task 7: `GOAL.md` for the CRA playbook

The worked example, and the artefact the 37-question session produced. Different repository.

**Files:**
- Create: `playbooks/playbooks/cra/.betterplan/GOAL.md`

**Interfaces:**
- Consumes: the eight-section contract from Task 2; the conventions from Task 1
- Produces: the precondition that unblocks re-running extraction on this project

- [ ] **Step 1: Write the eight sections from the recorded decisions**

Purpose, usage context (walked through with the customer, then the same project plan), roles (device manufacturer as obligation-bearer, contract developer as supplier, end user as beneficiary; authorised representative and importer as a boundary check only, since the customers are in the EU), scope (embedded software in devices, deliberately narrowed), finish line (placed on the market with declaration of conformity and CE marking, post-market obligations running), non-goals, backbone shape (the five Initiatives, supplier deliverables distributed across the phases where they arise and surfaced by the `project:Zulieferer` tag rather than collected in one column — one tag, not two), open facts.

- [ ] **Step 2: Verify it satisfies its own precondition**

Run: `grep -coE "goal:(purpose|usage-context|roles|scope|finish-line|non-goals|backbone|open-facts)" playbooks/cra/.betterplan/GOAL.md`
Expected: `8` — and no section consisting only of its heading.

- [ ] **Step 3: Commit in the playbooks repo**

```bash
git -C playbooks add playbooks/cra/.betterplan/GOAL.md
git -C playbooks commit -m "docs(cra): record the playbook goal"
```

---

## Deferred

Not in this plan, by decision:

- The CRA Story Map itself.
- Adding obligation-bearer and beneficiary to the 146 existing requirement entries — that belongs to the Story Map work.
- Re-running extraction on the CRA project. Task 7 unblocks it; whether to re-run is a separate call.
