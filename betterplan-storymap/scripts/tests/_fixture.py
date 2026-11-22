"""Eine minimale, befundfreie Story Map zum Hinschreiben und Kaputtmachen.

Die Tests perturbieren je **eine** Sache und erwarten je **einen** Befund. Das
setzt voraus, dass der Ausgangszustand sauber ist — deshalb prüft
`test_check_map.TestCleanMap` ihn als erstes. Fällt der Test, sind alle anderen
wertlos, und das soll man an einem Namen sehen.
"""
from __future__ import annotations
import pathlib

# Feste ids: ein Test, der auf eine id verweist, soll sie hinschreiben können,
# und eine gewürfelte UUID macht eine Fehlermeldung unlesbar.
INIT = "11111111-1111-4111-8111-111111111111"
EPIC = "22222222-2222-4222-8222-222222222222"
STORY = "33333333-3333-4333-8333-333333333333"
PROJECT = "44444444-4444-4444-8444-444444444444"

GOAL = """# Ziel: Testvorhaben

## Vision <!-- goal:vision -->

Das Vorhaben liefert eine prüfbare Map.

> Offen ist, wer sie prüft.

## Zweck <!-- goal:purpose -->

Damit die Prüfung belegt ist.
"""

PERSONAS = """# Personas

## kundin

- **name:** Kundin
- **role:** Entscheidet über den Kauf
"""

RELEASES = """# Releases

## r1

- **title:** Erstes Release
- **position:** 1
- **goal:**
  Das Fundament steht.

  Das Datum setzt das Team.
- **features:**
  - Ein erster Durchstich
"""

TAGS = """# Tags

## Could

- **color:** teal
"""


def item(iid: str, typ: str, title: str, *, parent: str | None = None,
         body: str | None = None, **fields) -> str:
    """Eine Item-Datei. `fields` landen als flache Frontmatter-Zeilen."""
    lines = [f"id: {iid}", f"type: {typ}", f"title: {title}"]
    if parent:
        lines.append(f"parent: {parent}")
    for key, value in fields.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines += [f"  - {v}" for v in value]
        elif value is not None:
            lines.append(f"{key}: {value}")
    head = "\n".join(lines)
    if body is None:
        body = (f"Als Kundin möchte ich {title.lower()}, damit es belegt ist.\n\n"
                "## Akzeptanzkriterien\n\n- [ ] Es ist belegt.\n")
    return f"---\n{head}\n---\n{body}"


def write(root: pathlib.Path) -> pathlib.Path:
    """Schreibt die saubere Map unter `root` und gibt den Projektpfad zurück."""
    bp = root / ".betterplan"
    sm = bp / "storymap"
    (sm / "01-eins" / "01-epic").mkdir(parents=True)
    (sm / "_querschnitt").mkdir()

    (bp / "GOAL.md").write_text(GOAL, encoding="utf-8")
    (sm / "_personas.md").write_text(PERSONAS, encoding="utf-8")
    (sm / "_releases.md").write_text(RELEASES, encoding="utf-8")
    (sm / "_tags.md").write_text(TAGS, encoding="utf-8")

    (sm / "01-eins" / "_initiative.md").write_text(
        item(INIT, "initiative", "Eins", order=1,
             body="Die erste Initiative.\n"), encoding="utf-8")
    (sm / "01-eins" / "01-epic" / "_epic.md").write_text(
        item(EPIC, "epic", "Epic", parent=INIT, order=1,
             body="Das erste Epic.\n"), encoding="utf-8")
    (sm / "01-eins" / "01-epic" / "01-story.md").write_text(
        item(STORY, "story", "Kaufen können", parent=EPIC, order=1,
             maturity="idea", persona="kundin", release="r1",
             sources=["Lastenheft §1"]), encoding="utf-8")
    # `order: 2`, nicht 1: Initiativen und Project Stories stehen beide auf
    # Wurzelebene und teilen damit **eine** Geschwistergruppe. Zwei Items mit
    # `order: 1` darin sind ein Befund — und zwar ein berechtigter.
    (sm / "_querschnitt" / "01-quer.md").write_text(
        item(PROJECT, "project", "Querschnittlich", order=2, maturity="idea",
             persona="kundin", sources=["Lastenheft §2"]), encoding="utf-8")

    # Eine Datei ohne `id` und ohne `type` ist Dokumentation und kein Item —
    # dass sie übersprungen wird, gehört zum geprüften Verhalten.
    (sm / "README.md").write_text("# Diese Map\n\nKein Item.\n", encoding="utf-8")
    return root
