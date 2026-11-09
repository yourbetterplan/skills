#!/usr/bin/env python3
"""Leitet `storymap/_index.md` aus den Item-Dateien ab.

    python3 build-index.py [--project <projektroot>]

Die Datei ist reines Generat und trägt den Do-not-edit-Hinweis. Sie existiert,
weil die `id` eine UUID ist und in Prosa deshalb nie genannt wird — der Index
ist die einzige Stelle, an der Titel und `id` nebeneinander stehen, und damit
das, was einen Prosa-Verweis für einen Menschen auflösbar macht.

Projektunabhängig: liest nur `.betterplan/storymap/`.
"""
from __future__ import annotations
import argparse, pathlib, re, sys

CATALOGUES = {"_personas.md", "_releases.md", "_tags.md", "_index.md"}
SECTIONS = (("initiative", "Initiativen"), ("epic", "Epics"),
            ("story", "User Stories"), ("project", "Project Stories"),
            ("dev", "Devteam Stories"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".")
    root = pathlib.Path(ap.parse_args().project).resolve() / ".betterplan" / "storymap"
    if not root.is_dir():
        sys.exit(f"❌ {root} nicht gefunden")

    items = []
    for p in sorted(root.glob("**/*.md")):
        if p.name in CATALOGUES:
            continue
        fm = p.read_text(encoding="utf-8").split("---\n", 2)[1]
        get = lambda k: (m.group(1) if (m := re.search(rf"^{k}: (.+)$", fm, re.M)) else None)
        iid, typ, title = get("id"), get("type"), get("title")
        if not (iid and typ and title):
            sys.exit(f"❌ {p}: id, type oder title fehlt")
        items.append((typ, title, iid, str(p.relative_to(root))))

    out = ["<!-- generated — do not edit, this file is regenerated -->",
           "# Index: Titel → id", "",
           "Verweise in Prosa nennen immer den **Titel**, nie die `id`. Diese Tabelle",
           "löst ihn auf — und ist die einzige Stelle, an der beides nebeneinander",
           "steht.", ""]
    for typ, label in SECTIONS:
        sel = sorted((i for i in items if i[0] == typ), key=lambda i: i[3])
        if not sel:
            continue
        out += [f"## {label} ({len(sel)})", "", "| Titel | id | Pfad |", "|---|---|---|"]
        out += [f"| {t} | `{i}` | `{path}` |" for _, t, i, path in sel]
        out.append("")
    (root / "_index.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"_index.md  {len(items)} Items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
