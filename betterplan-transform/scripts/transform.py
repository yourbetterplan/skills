#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-docx>=1.2",
#     "openpyxl>=3.1",
# ]
# ///
"""
betterplan-transform — Convert raw project material into agent-friendly Markdown.

Usage:
    uv run --script transform.py [--project-dir <path>] [--dry-run]

    Dependencies are declared inline (PEP 723); uv resolves them into its own
    cache on first run. No virtualenv is created next to this script.

    Defaults to the current working directory as the project root.
    Scans common file types and writes converted Markdown files into
    .betterplan/references/.

Supported input formats:
    .pdf   → text (via pdftotext)
    .docx  → Markdown (via python-docx)
    .xlsx  → Markdown tables (via openpyxl)
    .csv   → Markdown table
    .txt   → copied as Markdown code block / verbatim
    .md    → copied with a metadata header
    .html  → Markdown-ish text (via textutil)
    .rtf   → Markdown-ish text (via textutil)
    .odt   → Markdown-ish text (via textutil)
"""

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def warn(msg: str) -> None:
    print(f"  ⚠  {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    print(f"  ✓  {msg}")


def skipped(reason: str, path: Path) -> None:
    print(f"  –  übersprungen: {reason}  ({path.name})")


def run(cmd: list[str], timeout: int = 30) -> str | None:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0:
            return r.stdout
        warn(f"{' '.join(cmd)} → exit {r.returncode}: {r.stderr.strip()[:120]}")
        return None
    except FileNotFoundError:
        warn(f"Kommando nicht gefunden: {cmd[0]}")
        return None
    except subprocess.TimeoutExpired:
        warn(f"Timeout ({timeout}s): {' '.join(cmd)}")
        return None


def slugify(name: str) -> str:
    """Make a filesystem-safe slug from a filename (without extension).

    The caller strips the extension; stripping a second one here would eat the
    name itself — `4.1_Teilnahmeantrag` is a stem, not a name with an extension,
    and would collapse to `4`.
    """
    s = re.sub(r"[^a-zA-Z0-9äöüÄÖÜß_-]", "_", name)
    s = re.sub(r"_+", "_", s).strip("_")
    return s.lower()[:80]


def ext_lower(path: Path) -> str:
    return path.suffix.lower()

# ---------------------------------------------------------------------------
# converters — each returns Markdown text or None
# ---------------------------------------------------------------------------

def convert_pdf(path: Path) -> str | None:
    out = run(["pdftotext", "-layout", str(path), "-"])
    if out is None:
        return None
    text = out.strip()
    if not text:
        warn(f"{path.name}: pdftotext lieferte leeren Text")
        return None
    return f"```\n{text}\n```\n"


def convert_docx(path: Path) -> str | None:
    try:
        from docx import Document
    except ImportError:
        warn("python-docx nicht installiert (pip install python-docx)")
        return None
    try:
        doc = Document(path)
    except Exception as e:
        warn(f"{path.name}: docx-Fehler: {e}")
        return None

    lines: list[str] = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        style = p.style.name.lower() if p.style else ""
        if "heading 1" in style:
            lines.append(f"# {t}")
        elif "heading 2" in style:
            lines.append(f"## {t}")
        elif "heading 3" in style:
            lines.append(f"### {t}")
        elif "list" in style:
            lines.append(f"- {t}")
        else:
            lines.append(t)

    # tables
    for table in doc.tables:
        lines.append("")
        rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
        if rows:
            lines.append("| " + " | ".join(rows[0]) + " |")
            lines.append("| " + " | ".join("---" for _ in rows[0]) + " |")
            for row in rows[1:]:
                lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    text = "\n\n".join(lines)
    if not text.strip():
        warn(f"{path.name}: keine Textinhalte gefunden")
        return None
    return text


def convert_xlsx(path: Path) -> str | None:
    try:
        import openpyxl
    except ImportError:
        warn("openpyxl nicht installiert (pip install openpyxl)")
        return None
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    except Exception as e:
        warn(f"{path.name}: xlsx-Fehler: {e}")
        return None

    sheets: list[str] = []
    for ws in wb:
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue
        sheets.append(f"## Sheet: {ws.title}\n")
        # find last column with data
        max_col = max((len(r) for r in rows if r), default=0)
        table_rows: list[list[str]] = []
        for r in rows:
            row_vals = [str(c).strip() if c is not None else "" for c in r]
            # pad to max_col
            row_vals = (row_vals + [""] * max_col)[:max_col]
            if any(v for v in row_vals):
                table_rows.append(row_vals)

        if len(table_rows) >= 2:
            sheets.append("| " + " | ".join(table_rows[0]) + " |")
            sheets.append("| " + " | ".join("---" for _ in table_rows[0]) + " |")
            for row in table_rows[1:]:
                sheets.append("| " + " | ".join(row) + " |")
        elif len(table_rows) == 1:
            sheets.append("| " + " | ".join(table_rows[0]) + " |")
        sheets.append("")

    text = "\n".join(sheets).strip()
    if not text:
        warn(f"{path.name}: keine Daten gefunden")
        return None
    return text


def convert_csv(path: Path) -> str | None:
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            dialect = csv.Sniffer().sniff(f.read(4096))
            f.seek(0)
            reader = csv.reader(f, dialect)
            rows = [r for r in reader]
    except Exception:
        # fallback: semicolon or comma
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                content = f.read()
                delimiter = ";" if ";" in content[:512] else ","
                import io
                reader = csv.reader(io.StringIO(content), delimiter=delimiter)
                rows = [r for r in reader]
        except Exception as e:
            warn(f"{path.name}: CSV-Fehler: {e}")
            return None

    if not rows:
        return None
    lines: list[str] = []
    lines.append("| " + " | ".join(rows[0]) + " |")
    lines.append("| " + " | ".join("---" for _ in rows[0]) + " |")
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def convert_txt(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
    except Exception as e:
        warn(f"{path.name}: TXT-Fehler: {e}")
        return None
    if not text:
        return None
    # Preserve as-is; it is already text
    return text


def convert_md(path: Path) -> str | None:
    """Already Markdown — return content with a note."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
    except Exception as e:
        warn(f"{path.name}: MD-Fehler: {e}")
        return None
    if not text:
        return None
    return text


def convert_via_textutil(path: Path, fmt_hint: str = "html") -> str | None:
    """Use macOS textutil to convert a document to plain text."""
    out = run(["textutil", "-convert", "txt", "-stdout", str(path)])
    if out is None:
        return None
    text = out.strip()
    if not text:
        warn(f"{path.name}: textutil lieferte leeren Text")
        return None
    return f"({fmt_hint} convertiert via textutil)\n\n{text}"


# ---------------------------------------------------------------------------
# dispatcher
# ---------------------------------------------------------------------------

CONVERTERS: dict[str, tuple] = {
    ".pdf":  (convert_pdf,           "PDF (pdftotext)"),
    ".docx": (convert_docx,          "Word (python-docx)"),
    ".xlsx": (convert_xlsx,          "Excel (openpyxl)"),
    ".csv":  (convert_csv,           "CSV"),
    ".txt":  (convert_txt,           "Text"),
    ".md":   (convert_md,            "Markdown (kopiert)"),
    ".html": (convert_via_textutil,  "HTML (textutil)"),
    ".htm":  (convert_via_textutil,  "HTML (textutil)"),
    ".rtf":  (convert_via_textutil,  "RTF (textutil)"),
    ".odt":  (convert_via_textutil,  "ODT (textutil)"),
}

SKIP_DIRS = {".betterplan", ".git", ".agents", ".claude", "node_modules",
             "__pycache__", ".DS_Store"}


def reference_source(path: Path) -> str | None:
    """Return the `source:` filename from a reference's metadata header."""
    try:
        with path.open(encoding="utf-8") as fh:
            if fh.readline().rstrip() != "<!--":
                return None
            for line in fh:
                if line.startswith("source: "):
                    return line[len("source: "):].strip()
                if line.startswith("-->"):
                    break
    except OSError:
        pass
    return None


def transform_file(src: Path, ref_dir: Path, dry_run: bool) -> bool:
    ext = ext_lower(src)
    if ext not in CONVERTERS:
        skipped("nicht unterstütztes Format", src)
        return False

    converter, label = CONVERTERS[ext]
    ok(f"{src.name}  →  {label}")
    if dry_run:
        return True

    md_text = converter(src)
    if md_text is None:
        return False

    # build metadata header
    stat = src.stat()
    header = (
        "<!--\n"
        f"source: {src.name}\n"
        f"format: {ext.lstrip('.')}\n"
        f"converted: {datetime.now().isoformat()}\n"
        f"size: {stat.st_size} bytes\n"
        f"-->\n\n"
    )

    content = header + md_text

    # output filename: slug of the source stem
    slug = slugify(src.stem)
    out_path = ref_dir / f"{slug}.md"

    # A re-run overwrites the reference it wrote last time, so the skill stays
    # idempotent. A suffix is only for a genuine collision: a different source
    # file whose name slugifies to the same thing (or a hand-written file
    # without our header), which must not be clobbered.
    counter = 1
    while out_path.exists() and reference_source(out_path) != src.name:
        out_path = ref_dir / f"{slug}_{counter}.md"
        counter += 1

    out_path.write_text(content, encoding="utf-8")
    ok(f"  → {out_path.relative_to(ref_dir.parent.parent)}")
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Transform raw project material into Markdown")
    parser.add_argument("--project-dir", default=".", help="Project root directory (default: cwd)")
    parser.add_argument("--dry-run", action="store_true", help="Only list files, don't convert")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    if not project_dir.is_dir():
        print(f"❌ Projektordner nicht gefunden: {project_dir}", file=sys.stderr)
        sys.exit(1)

    betterplan_dir = project_dir / ".betterplan"
    ref_dir = betterplan_dir / "references"

    if not args.dry_run:
        ref_dir.mkdir(parents=True, exist_ok=True)
        ok(f"Ordner: {ref_dir.relative_to(project_dir)}/")

    print(f"\n📂 Projekt: {project_dir.name}")
    print(f"{'─' * 60}")

    # collect files from project dir (non-recursive, skip hidden and dot dirs)
    files: list[Path] = []
    for entry in sorted(project_dir.iterdir()):
        if not entry.is_file():
            continue
        if entry.name.startswith("."):
            continue
        files.append(entry)

    if not files:
        print("  (keine unterstützten Dateien gefunden)")
        sys.exit(0)

    converted = 0
    failed = 0
    for f in files:
        if transform_file(f, ref_dir, args.dry_run):
            converted += 1
        else:
            failed += 1

    print(f"{'─' * 60}")
    print(f"\nErgebnis: {converted} konvertiert, {failed} fehlgeschlagen")
    if converted:
        print(f"Referenzen: {ref_dir.relative_to(project_dir)}/")
    print()


if __name__ == "__main__":
    main()