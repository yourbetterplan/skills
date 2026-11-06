#!/usr/bin/env python3
"""Verify that splitting a reference into sections lost no text.

A subagent does the splitting, and a model that cuts can drop text where a
script cannot. This is the guard: strip the headers the splitting step itself
generated, then compare character and line counts against the original
*exactly*. A tolerance would be a budget for losing text.

Usage:
    python3 verify_split.py <original.md> <section-dir>

Exit code 0 if the split accounts for every character, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

HEADER_END = "-->"
INDEX_NAME = "INDEX.md"
_LINK = re.compile(r"\]\(([^)]+)\)")


@dataclass
class SplitVerdict:
    ok: bool
    original_chars: int
    section_chars: int
    original_lines: int
    section_lines: int
    reason: str | None = None


def _normalise(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _strip_header(text: str) -> str:
    """Drop the generated `<!-- … -->` block and the single blank line after it."""
    if not text.startswith("<!--"):
        return text
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == HEADER_END:
            rest = lines[i + 1 :]
            if rest and rest[0] == "":
                rest = rest[1:]
            return "\n".join(rest)
    return text


def _indexed_sections(section_dir: Path) -> list[str]:
    index = section_dir / INDEX_NAME
    if not index.is_file():
        return []
    return _LINK.findall(_normalise(index.read_text(encoding="utf-8")))


def verify_split(original: Path, section_dir: Path) -> SplitVerdict:
    source = _normalise(original.read_text(encoding="utf-8"))
    original_chars, original_lines = len(source), source.count("\n")

    listed = _indexed_sections(section_dir)
    if not listed:
        return SplitVerdict(
            False, original_chars, 0, original_lines, 0,
            f"{INDEX_NAME} missing or lists no sections",
        )

    present = {p.name for p in section_dir.iterdir() if p.is_file()} - {INDEX_NAME}
    orphans = sorted(present - set(listed))
    if orphans:
        return SplitVerdict(
            False, original_chars, 0, original_lines, 0,
            f"not listed in {INDEX_NAME}, left over from an earlier run: "
            + ", ".join(orphans),
        )

    missing = [name for name in listed if not (section_dir / name).is_file()]
    if missing:
        return SplitVerdict(
            False, original_chars, 0, original_lines, 0,
            f"listed in {INDEX_NAME} but absent: " + ", ".join(missing),
        )

    bodies = [
        _strip_header(_normalise((section_dir / name).read_text(encoding="utf-8")))
        for name in listed
    ]
    section_chars = sum(len(b) for b in bodies)
    section_lines = sum(b.count("\n") for b in bodies)

    if section_chars != original_chars or section_lines != original_lines:
        return SplitVerdict(
            False, original_chars, section_chars, original_lines, section_lines,
            f"characters {section_chars} != {original_chars}; "
            f"lines {section_lines} != {original_lines}",
        )

    return SplitVerdict(True, original_chars, section_chars, original_lines, section_lines)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    verdict = verify_split(Path(argv[1]), Path(argv[2]))
    if verdict.ok:
        print(
            f"OK  {argv[2]}: {verdict.section_chars} chars, "
            f"{verdict.section_lines} lines — accounts for the original exactly"
        )
        return 0
    print(f"FAIL  {argv[2]}: {verdict.reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
