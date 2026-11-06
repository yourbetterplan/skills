---
name: betterplan-transform
description: >
  Transforms raw project materials (PDF, DOCX, XLSX, CSV, Markdown, HTML, RTF, ODT, TXT)
  into agent-friendly Markdown stored in .betterplan/references/, and splits oversized
  references into sections so an agent can read a detail without pulling in the whole
  document. Run from the project root. Re-runnable: re-transforms everything, overwrites
  existing references.
metadata:
  version: "0.2.0"
---

# betterplan-transform

Konvertiert Rohmaterial aus dem Projektordner in Markdown unter
`.betterplan/references/` und teilt zu große Referenzen in Abschnitte auf.

Der Skill läuft in **zwei Phasen**: ein deterministisches Skript konvertiert,
anschließend teilen Subagenten die großen Ergebnisse auf. Phase 2 ist kein
Skript, weil ein Skript Struktur nur an Textmustern erkennen kann — und sie ist
ein *Subagent*, weil dessen Kontext nach der Arbeit verworfen wird. Genau das
ist der Zweck: ein 230.000-Token-Dokument darf dort gelesen werden, ohne den
Arbeitskontext zu belasten.

## Voraussetzungen

- **Python 3.12+**
- **uv** (https://docs.astral.sh/uv/) — zum Verwalten der Abhängigkeiten
- **pdftotext** (für PDFs): `brew install poppler`
- **textutil** (für HTML/RTF/ODT) — ist auf macOS vorinstalliert
- **Ein Subagenten-Werkzeug** — nur für Phase 2. Fehlt es, siehe *Ohne
  Subagenten-Werkzeug*.

## Setup (einmalig pro Rechner)

```bash
cd ~/.agents/skills/betterplan-transform/scripts
uv sync
```

`uv sync` erstellt ein `.venv/` im `scripts/`-Ordner und installiert
`python-docx` und `openpyxl`.

## Phase 1 — Konvertieren

Im Projektroot (z.B. `FUBA/`):

```bash
uv run --directory ~/.agents/skills/betterplan-transform/scripts \
  python3 transform.py --project-dir "$PWD"
```

Trockenlauf:

```bash
uv run --directory ~/.agents/skills/betterplan-transform/scripts \
  python3 transform.py --project-dir "$PWD" --dry-run
```

**Oder — wenn der Skill per Symlink installiert ist — kürzer:**

```bash
uv run --directory .agents/skills/betterplan-transform/scripts \
  python3 transform.py --project-dir "$PWD"
```

> `--directory` wechselt das Arbeitsverzeichnis. `--project-dir` ist deshalb
> nicht optional, wenn du nicht ohnehin im `scripts/`-Ordner stehst.

Das Skript schreibt je Quelldatei **eine** Markdown-Datei nach
`.betterplan/references/<slug>.md`, mit Metadaten-Header.

### Unterstützte Formate

| Format | Werkzeug | Ergebnis |
|---|---|---|
| PDF | pdftotext | Codeblock |
| DOCX | python-docx | Markdown (Überschriften, Listen, Tabellen) |
| XLSX | openpyxl | Markdown-Tabellen (alle Sheets) |
| CSV | csv (Python) | Markdown-Tabelle |
| TXT | — | Inhalt 1:1 |
| MD | — | Inhalt + Metadaten-Header |
| HTML / RTF / ODT | macOS textutil | Text |

## Phase 2 — Große Referenzen aufteilen

**Schwellen** (Parameter, keine Konstanten — passe sie an, wenn das
Lesewerkzeug andere Grenzen hat):

| Parameter | Standard | Bedeutung |
|---|---|---|
| `SPLIT_THRESHOLD` | **50 KB** | darüber wird aufgeteilt |
| `SECTION_TARGET` | **30 KB** | Zielgröße je Abschnittsdatei |

Hintergrund: 125 KB Rohtext entsprachen in der Messung etwa 61.000 Tokens, also
rund 2 KB pro 1.000 Tokens. 50 KB liegt damit knapp unter einem
25.000-Token-Limit, 30 KB lässt Luft.

Für **jede** Referenz über der Schwelle: genau einen Subagenten mit frischem
Kontext starten. Niemals mehrere Dokumente in einen Subagenten geben — der
Sinn der Übung ist, dass jeder Kontext nur ein Dokument tragen muss.

### Auftrag an den Subagenten

Gib ihm Pfad und Slug der Referenz und diesen Auftrag:

1. **Lies** die Referenz und leite ihre Abschnittsstruktur ab.
2. **Schneide ausschließlich wörtlich.** Nicht zusammenfassen, nicht
   normalisieren, nicht glätten, keine Tippfehler korrigieren. Referenzen sind
   Beweismittel: Die Extraktion zitiert sie bis auf die Ebene einzelner
   Buchstaben eines Absatzes, und eine paraphrasierte Referenz macht jeden
   dieser Verweise unprüfbar.
3. **Ein erkannter Abschnitt ist unteilbar.** Überschreitet ein einzelner
   Abschnitt `SECTION_TARGET`, bleibt er ganz. Eine mitten durchtrennte
   Anforderung ist schlimmer als eine große Datei.
4. **Schreibe** `<projektroot>/.betterplan/references/<slug>/INDEX.md` und
   `.../<slug>/NN-<abschnitt-slug>.md`, `NN` fortlaufend ab `01`. Gib dem
   Subagenten den **absoluten** Projektpfad mit; ein relativer Pfad landet in
   seinem eigenen Arbeitsverzeichnis, und der Abgleich meldet dann
   wahrheitsgemäß „INDEX.md missing" über das falsche Verzeichnis.
5. **Gib nur einen Bericht zurück** — Anzahl Abschnitte, Größenverteilung,
   genutzte Gliederungstiefe, Auffälligkeiten. **Keinen Inhalt.** Inhalt im
   Rückgabewert landet im Elternkontext und macht die ganze Phase sinnlos.
6. **Ohne erkennbare Struktur** (gescanntes PDF, zerfallener Textlayer): nicht
   aufteilen. Melde den Grund zurück, statt eine `INDEX.md` mit einem einzigen
   Eintrag zu schreiben. Dasselbe gilt, wenn das Dokument **nur einen**
   erkannten Abschnitt hat: Eine Aufteilung in genau eine Datei bringt nichts
   und kostet ein Verzeichnis — lass es ganz.

### Pflichtformate

Beide Formate werden maschinell geprüft — halte sie genau ein.

**Kopf jeder Abschnittsdatei**, gefolgt von genau einer Leerzeile, dann der
wörtliche Inhalt:

```markdown
<!--
source: BSI-TR-03183-2_v2_1_0.pdf
section: 03-content-requirements.md
lines: 419-601
-->
```

`lines` ist der Zeilenbereich in der **Gesamtdatei** aus Phase 1.

**`references/<slug>/INDEX.md`** — Abschnitte als Markdown-Links, einer pro
Zeile, in Dokumentreihenfolge:

```markdown
<!-- generated by betterplan-transform — do not edit, this file is regenerated -->
# BSI-TR-03183-2_v2_1_0.pdf

- [1 Introduction](01-introduction.md)
- [5 Content requirements](03-content-requirements.md)
```

Der Abgleich liest die Reihenfolge aus den `](dateiname)`-Klammern.

### Abgleich — nicht dem Bericht glauben

Ein Modell, das schneidet, kann Text verlieren, umsortieren oder umschreiben;
ein Skript kann das nicht. Nach jedem Subagenten, **der eine Aufteilung
gemeldet hat**:

> Hat der Subagent nach Regel 6 *keine* Aufteilung vorgenommen — unlesbare
> Struktur oder nur ein Abschnitt —, dann **überspringe den Abgleich**. Es gibt
> kein Abschnittsverzeichnis, das Skript würde wahrheitsgemäß „INDEX.md
> missing" melden, und der korrekte Ausgang wäre von Textverlust nicht zu
> unterscheiden. Vermerke ihn stattdessen als eigene Zeile im Bericht:
> *„ungeteilt, Grund: …"*.

```bash
uv run --directory ~/.agents/skills/betterplan-transform/scripts \
  python3 verify_split.py "$PWD/.betterplan/references/<slug>.md" \
                          "$PWD/.betterplan/references/<slug>/"
```

> **Absolute Pfade sind hier Pflicht.** `--directory` wechselt das
> Arbeitsverzeichnis in den `scripts/`-Ordner; relative Pfade zeigen dann ins
> Leere und das Skript bricht mit `FileNotFoundError` ab — nicht mit einem
> ehrlichen `FAIL`. Dasselbe gilt für `--project-dir` oben.

Das Skript streift die generierten Köpfe ab, normalisiert Zeilenenden und
vergleicht den **Text** — nicht seine Größe — gegen die Gesamtdatei. Keine
Toleranz außer einem abschließenden Zeilenumbruch; eine Toleranz wäre ein
Budget zum Textverlieren. Zeichen- und Zeilenzahlen dienen nur der
Fehlermeldung. Der Textvergleich ist der Punkt: Umsortierte Abschnitte,
ein zu `-` normalisierter weicher Trennstrich und eine gleichlange
Umformulierung haben alle identische Zählwerte.

Es scheitert außerdem an einer Abschnittsdatei, die die `INDEX.md` nicht
aufführt, an einem Link, der aus dem Verzeichnis hinausführt, und an einem
Unterverzeichnis — das fängt Überreste eines früheren Laufs und die
`<slug>/<slug>/`-Verschachtelung.

- **Exit 0** → Gesamtdatei löschen, Abschnitte behalten.
- **Exit 1** → Abschnittsverzeichnis **verwerfen**, Gesamtdatei behalten, und
  den Fehler **laut** berichten. Ohne diesen Schritt fallen zwei verschluckte
  Seiten erst auf, wenn eine Anforderung fehlt, die niemand mehr vermisst.
- **Exit 2** → Bedienfehler (falscher Pfad, nicht dekodierbare Datei). **Nicht**
  verwerfen. Der eigene Exit-Code existiert, damit ein Tippfehler keine korrekte
  Aufteilung vernichtet.

> **Der Abgleich gehört unmittelbar an Phase 1.** `transform.py` stempelt
> `converted:` mit der Uhrzeit, ist also nicht byte-idempotent. Eine
> Aufteilung lässt sich deshalb später nicht sinnvoll gegen eine neu
> erzeugte Gesamtdatei prüfen — das Skript normalisiert genau diese eine
> generierte Zeile weg, damit ein erneuter Transform-Lauf keine korrekten
> Aufteilungen verwirft, aber verlass dich nicht darauf: prüfe, solange die
> Gesamtdatei aus demselben Lauf stammt.

### Ohne Subagenten-Werkzeug

Läuft der Skill in einer Umgebung ohne Subagenten (pi, Codex, andere
Harnesses): **Phase 2 überspringen** und im Bericht vermerken, dass die
Dokumente ungeteilt sind. Baue keinen musterbasierten Ersatz — zwei Splitter,
die unterschiedliche Gliederungen erzeugen, und niemand weiß mehr, welches
Layout er vor sich hat.

### Abschluss von Phase 2 — immer, auch wenn nichts geteilt wurde

Zwei Schritte gehören dir, nicht dem Subagenten, und sie laufen auch dann, wenn
kein Dokument über der Schwelle lag oder kein Subagenten-Werkzeug existiert:

**1. Veraltete Aufteilungen entfernen.** Liegt zu einem Dokument ein
`references/<slug>/` vor, das Dokument ist aber jetzt **unter** der Schwelle
(Quelle gekürzt) oder gar nicht mehr vorhanden (Quelle gelöscht), dann lösche
das Verzeichnis. `transform.py` räumt `references/` nicht auf: Phase 1 schreibt
eine frische `<slug>.md`, kein Subagent wird gestartet, kein Abgleich läuft —
und die Aufteilung des Vorlaufs überlebt daneben. Genau der Zustand mit zwei
Fassungen, den das Layout verbietet, und `betterplan-extract` liest rekursiv
und sähe das Dokument doppelt.

**2. `references/INDEX.md` schreiben.** Eine Zeile je Dokument, Link auf die
`INDEX.md` des Verzeichnisses bei geteilten, auf die Datei selbst bei
ungeteilten Dokumenten:

```markdown
<!-- generated by betterplan-transform — do not edit, this file is regenerated -->
# Referenzen

- [VERORDNUNG (EU) 2024/2847](oj_l_202402847_de_txt/INDEX.md) — 17 Abschnitte
- [BSI TR-03183-H v1.0.0](bsi-tr-03183-h_v1_0_0.md) — eine Datei, unter der Schwelle
```

Nimm auf, was ein Leser braucht, um das richtige Dokument zu wählen: Titel,
Sprache, Umfang, und was die Konversion nicht hergegeben hat. Diese Datei ist
der Einstieg, den `betterplan-extract` nutzt.

## Layout unter `.betterplan/references/`

```
.betterplan/references/
├── INDEX.md                         generiert: listet alle Dokumente
├── kleines-dokument.md              unter der Schwelle: eine Datei, wie bisher
└── grosses-dokument/
    ├── INDEX.md                     generiert: listet die Abschnitte
    ├── 01-einleitung.md
    └── 02-anforderungen.md
```

- **Die Gesamtdatei wird neben den Abschnitten nicht behalten.** Zwei Kopien
  desselben Textes driften auseinander, sobald eine angefasst wird, und `grep`
  funktioniert über die Abschnitte genauso gut.
- **Beide `INDEX.md` sind reines Generat** und tragen den Do-not-edit-Hinweis
  im Kopf. Sie werden nie gepflegt, nur neu abgeleitet — deshalb können sie
  nicht veralten.
- **Ein erneuter Lauf ersetzt ein `<slug>/`-Verzeichnis vollständig**, statt
  hineinzumischen. Erst löschen, dann neu schreiben.
- **Handnotizen gehören nicht nach `references/`.** Lege sie woanders unter
  `.betterplan/` ab; alles hier wird beim nächsten Lauf überschrieben.
- **Abschnittsdateien eines Code-Fence-Dokuments haben unbalancierte Fences.**
  PDF-Konversionen umschließen den Text mit ```` ``` ````. Die öffnende Fence
  landet im ersten Abschnitt, die schließende im letzten — mehr lässt die
  Lückenlosigkeit nicht zu. Ein Markdown-Renderer, der auf einen mittleren
  Abschnitt zeigt, behandelt dessen Inhalt deshalb als ungefenct. Das ist
  Absicht: Agenten lesen diese Dateien als Text, und exakte Nachvollziehbarkeit
  ist mehr wert als die Renderbarkeit einer einzelnen Datei.

## Was passiert

1. Scannt den Projektordner (obere Ebene, nicht rekursiv) nach Dateien mit
   unterstützten Endungen.
2. Überspringt versteckte Dateien (`.`), `.betterplan/`, `.git/`, `node_modules/`.
3. Konvertiert jede Datei in Markdown mit Metadaten-Header.
4. Teilt jede Referenz über `SPLIT_THRESHOLD` per Subagent in Abschnitte auf.
5. Gleicht jede Aufteilung gegen die Gesamtdatei ab und verwirft sie bei
   Abweichung.
6. Entfernt Aufteilungen zu Dokumenten, die jetzt unter der Schwelle liegen
   oder deren Quelle verschwunden ist.
7. Schreibt `references/INDEX.md` über alle Dokumente — immer.

## Notizen

- **Immer wiederholbar**: Ein erneuter Aufruf überschreibt alle Referenzen neu.
- **PDF-Textqualität hängt vom PDF ab**: pdftotext extrahiert den Textlayer;
  gescannte PDFs (Bilder) brauchen vorher OCR. Tabellen und Abbildungen gehen
  dabei regelmäßig verloren oder verrutschen — für Detailarbeit an einer Tabelle
  bleibt das Original-PDF die Quelle.
- **Die Aufteilung putzt nichts.** Seitenmöbel (Kopf- und Fußzeilen,
  Seitenzahlen, ELI-Zeilen), Formfeed-Zeichen und weiche Trennstriche
  (U+00AD, aus der Silbentrennung des PDF) bleiben erhalten, weil „wörtlich"
  wörtlich heißt. Folgen für Konsumenten: Ein Absatz kann mitten durch
  Seitenmöbel laufen, und eine Teilstring-Suche nach einem Begriff scheitert,
  wenn das PDF ihn getrennt hatte. Für eine verlässliche Suche nach einem
  einzelnen Absatz ist das zu berücksichtigen.
- **Excel-Zahlen**: `data_only=True` — Formelergebnisse, nicht die Formeln.
- **Kein Automatismus**: Der Skill läuft nur, wenn du ihn explizit aufrufst.
  Neue Rohmaterialien bedeuten einen erneuten Aufruf.
- **Der nächste Schritt ist `betterplan-goal`**, nicht `betterplan-extract`:
  Die Extraktion braucht ein Ziel, um zu wissen, wie sie schneiden soll.
