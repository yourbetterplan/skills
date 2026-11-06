#!/usr/bin/env python3
"""Verify that splitting a reference into sections lost no text.

A subagent does the splitting, and a model that cuts can also reorder,
normalise or rewrite — none of which a character count can see. So this
compares the *text*: strip the headers the splitting step generated,
concatenate the bodies in index order, and require the result to equal the
original. Counts are kept only to describe a failure.

Usage:
    python3 verify_split.py <original.md> <section-dir>

Exit codes:
    0  the sections reproduce the original exactly
    1  they do not — the caller discards the split and keeps the single file
    2  operator error (bad path, undecodable file). Deliberately *not* 1, so a
       typo cannot be mistaken for text loss and throw away a correct split.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

INDEX_NAME = "INDEX.md"
_LINK = re.compile(r"\]\(([^)]+)\)")
# A section filename and nothing else: no directory separator, no traversal,
# no anchor. An index link is untrusted input — it decides which file gets
# read and, downstream, whether the original is deleted.
_SECTION_NAME = re.compile(r"^\d+-[A-Za-z0-9._-]+\.md$")
# The only generated line inside a reference's own body (transform.py writes it).
_CONVERTED = re.compile(r"^converted: .*$", re.M)


@dataclass
class SplitVerdict:
    ok: bool
    original_chars: int
    section_chars: int
    original_lines: int
    section_lines: int
    reason: str | None = None


def _normalise(text: str) -> str:
    """Line endings, plus the one line transform.py stamps with the clock.

    `converted:` in the reference's metadata header is generated, not source
    text, and it changes on every transform run. Comparing it would make a
    correct split fail against a freshly regenerated original — and the
    documented reaction to a failure is to discard the split, so leaving it in
    would turn a re-transform into a destroyer of good work.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return _CONVERTED.sub("converted: <generated>", text)


def _strip_header(text: str) -> str:
    """Drop the generated header block and the single blank line after it.

    Matches the exact five-line shape the splitting step writes — not merely
    "starts with `<!--`" — because a section's own content may legitimately
    begin with a comment block, and eating that would look like text loss.
    """
    lines = text.split("\n")
    if (
        len(lines) >= 5
        and lines[0] == "<!--"
        and lines[1].startswith("source: ")
        and lines[2].startswith("section: ")
        and lines[3].startswith("lines: ")
        and lines[4].strip() == "-->"
    ):
        rest = lines[5:]
        if rest and rest[0] == "":
            rest = rest[1:]
        return "\n".join(rest)
    return text


def _indexed_sections(section_dir: Path) -> tuple[list[str], str | None]:
    index = section_dir / INDEX_NAME
    if not index.is_file():
        return [], f"{INDEX_NAME} missing"
    listed = _LINK.findall(_normalise(index.read_text(encoding="utf-8")))
    if not listed:
        return [], f"{INDEX_NAME} lists no sections"
    bad = [n for n in listed if not _SECTION_NAME.fullmatch(n)]
    if bad:
        return [], (
            f"{INDEX_NAME} links outside the section directory or to a "
            "malformed name: " + ", ".join(bad)
        )
    duplicates = sorted({n for n in listed if listed.count(n) > 1})
    if duplicates:
        return [], f"{INDEX_NAME} lists the same section twice: " + ", ".join(duplicates)
    return listed, None


def _fail(reason: str, chars: int, lines: int) -> SplitVerdict:
    return SplitVerdict(False, chars, 0, lines, 0, reason)


def verify_split(original: Path, section_dir: Path) -> SplitVerdict:
    source = _normalise(original.read_text(encoding="utf-8"))
    chars, lines = len(source), source.count("\n")

    listed, problem = _indexed_sections(section_dir)
    if problem:
        return _fail(problem, chars, lines)

    root = section_dir.resolve()
    for name in listed:
        target = (section_dir / name).resolve()
        if target.parent != root:
            return _fail(f"{name} resolves outside {section_dir}", chars, lines)

    # Dotfiles are editor and OS litter (.DS_Store, .gitignore) — not sections.
    present = {
        p.name
        for p in section_dir.iterdir()
        if p.is_file() and not p.name.startswith(".")
    } - {INDEX_NAME}
    orphans = sorted(present - set(listed))
    if orphans:
        return _fail(
            f"not listed in {INDEX_NAME}, left over from an earlier run: "
            + ", ".join(orphans),
            chars,
            lines,
        )
    strays = sorted(
        p.name for p in section_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
    )
    if strays:
        return _fail(
            f"unexpected subdirectory in the section directory: " + ", ".join(strays),
            chars,
            lines,
        )
    missing = [n for n in listed if not (section_dir / n).is_file()]
    if missing:
        return _fail(
            f"listed in {INDEX_NAME} but absent: " + ", ".join(missing), chars, lines
        )

    bodies = [
        _strip_header(_normalise((section_dir / n).read_text(encoding="utf-8")))
        for n in listed
    ]
    recon = "".join(bodies)
    recon_chars, recon_lines = len(recon), recon.count("\n")

    # A file writer that always terminates its output with a newline is not
    # text loss. One newline of difference at the very end is the only
    # tolerated divergence, and only when everything before it is identical.
    if recon == source or recon == source + "\n" or source == recon + "\n":
        return SplitVerdict(True, chars, recon_chars, lines, recon_lines)

    if recon_chars == chars and recon_lines == lines:
        detail = "same length as the original but different text — reordered, normalised or rewritten"
    else:
        detail = f"characters {recon_chars} != {chars}; lines {recon_lines} != {lines}"
    return SplitVerdict(False, chars, recon_chars, lines, recon_lines, detail)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        verdict = verify_split(Path(argv[1]), Path(argv[2]))
    except (OSError, UnicodeDecodeError) as exc:
        print(f"ERROR  {exc}", file=sys.stderr)
        return 2
    if verdict.ok:
        print(
            f"OK  {argv[2]}: {verdict.section_chars} chars, "
            f"{verdict.section_lines} lines — text reproduces the original"
        )
        return 0
    print(f"FAIL  {argv[2]}: {verdict.reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
