---
name: betterplan-transform
description: >
  Transforms raw project materials (PDF, DOCX, XLSX, CSV, Markdown, HTML, RTF, ODT, TXT)
  into agent-friendly Markdown stored in .betterplan/references/. Run from the project root.
  Re-runnable: re-transforms everything, overwrites existing references.
metadata:
  version: "0.2.0"
---

# betterplan-transform

Konvertiert Rohmaterial aus dem Projektordner in Markdown-Dateien unter
`.betterplan/references/`. Jede Datei bekommt einen Metadaten-Header
mit Quellname, Format, Konvertierungsdatum und Größe.

## Voraussetzungen

- **Python 3.12+**
- **uv** (https://docs.astral.sh/uv/) — löst die Abhängigkeiten zur Laufzeit auf
- **pdftotext** (für PDFs): `brew install poppler`
- **textutil** (für HTML/RTF/ODT) — ist auf macOS vorinstalliert

## Setup

Keins. `scripts/transform.py` deklariert seine Abhängigkeiten inline
(PEP 723), `uv` baut die Umgebung beim ersten Aufruf in seinem eigenen Cache.
Es entsteht **kein `.venv/` im Skill-Verzeichnis** — der Skill bleibt damit
installierbar und frei von rechnerspezifischen Pfaden.

## Aufruf

Im Projektroot (z.B. `FUBA/`) — das Skript nimmt das aktuelle
Arbeitsverzeichnis als Projektwurzel:

```bash
cd /pfad/zu/FUBA
uv run --script ~/.agents/skills/betterplan-transform/scripts/transform.py
```

Trockenlauf (zeigt nur an, was konvertiert würde):

```bash
uv run --script ~/.agents/skills/betterplan-transform/scripts/transform.py --dry-run
```

**Oder -- wenn der Skill projektlokal installiert ist -- kürzer:**

```bash
cd /pfad/zu/FUBA
uv run --script .agents/skills/betterplan-transform/scripts/transform.py
```

Ein anderes Projektverzeichnis lässt sich mit `--project-dir <pfad>` wählen.

## Unterstützte Formate

| Format | Werkzeug | Ergebnis |
|---|---|---|
| PDF | pdftotext | Codeblock |
| DOCX | python-docx | Markdown (Überschriften, Listen, Tabellen) |
| XLSX | openpyxl | Markdown-Tabellen (alle Sheets) |
| CSV | csv (Python) | Markdown-Tabelle |
| TXT | — | Inhalt 1:1 |
| MD | — | Inhalt + Metadaten-Header |
| HTML / RTF / ODT | macOS textutil | Text |

## Was passiert

1. Scannt den Projektordner (obere Ebene, nicht rekursiv) nach Dateien mit
   unterstützten Endungen.
2. Überspringt versteckte Dateien (`.`), `.betterplan/`, `.git/`, `node_modules/`.
3. Konvertiert jede Datei in Markdown.
4. Schreibt das Ergebnis nach `.betterplan/references/<slug>.md`.
   Der Slug leitet sich aus dem Originaldateinamen ab.
5. Enthält einen Metadaten-Header mit Quellname, Format und Konvertierungszeit.

## Notizen

- **Immer wiederholbar**: Ein erneuter Aufruf überschreibt alle Referenzen neu.
- **PDF-Textqualität hängt vom PDF ab**: pdftotext extrahiert den Textlayer;
  gescannte PDFs (Bilder) brauchen vorher OCR.
- **Excel-Zahlen**: `data_only=True` — Formelergebnisse, nicht die Formeln.
- **Kein Automatismus**: Der Skill läuft nur, wenn du ihn explizit aufrufst.
  Neue Rohmaterialien bedeuten einen erneuten Aufruf.