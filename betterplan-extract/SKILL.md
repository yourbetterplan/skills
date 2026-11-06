---
name: betterplan-extract
description: >
  Extracts structured domain knowledge from transformed references:
  requirements, constraints, risks, ambiguities. Reads from
  .betterplan/references/, writes to .betterplan/requirements/,
  .betterplan/unklarheiten.md, and .betterplan/GLOSSARY.md.
  Rerunnable: updates existing files, preserves manual edits via markers.
metadata:
  version: "0.2.0"
---

# betterplan-extract

Extrahiert aus den transformierten Referenzen (`.betterplan/references/`)
das strukturierte Domänenwissen des Projekts:

| Ausgabe | Inhalt |
|---|---|
| `requirements/` | Kategorisierte Anforderungen |
| `unklarheiten.md` | Offene Fragen, Widersprüche, Entscheidungsbedarf |
| `GLOSSARY.md` | Zentrale Begriffe und ihre Definitionen |

Das ist Lesearbeit, kein Konvertieren: der Agent führt sie selbst aus.
Es gibt kein Skript, kein Setup und keine Abhängigkeiten.

## Voraussetzung

`betterplan-transform` wurde vorher ausgeführt, `.betterplan/references/`
existiert und ist nicht leer. Fehlt das Verzeichnis, brich ab und verweise
auf `betterplan-transform`.

## Vorgehen

1. **Lies** alle Referenzen aus `.betterplan/references/*.md` — vollständig,
   nicht nur die Überschriften. Der Metadaten-Header jeder Datei nennt die
   Originalquelle; zitiere sie später als Belegstelle.
2. **Bestimme den Projektkontext** aus dem Material (Software, Bau, Event,
   Organisation, …). Er entscheidet, welcher Qualitätsrahmen greift —
   ISO 25010 für Software, DIN-Normen für Bau, Veranstaltungsrecht für Events.
3. **Extrahiere je Referenz**:
   - **Fachliche Anforderungen** — was muss das Projekt/die Lösung können?
   - **Rahmenbedingungen** — Budget, Termin, Rechtliches, Organisation
   - **Qualitätsanforderungen** — nach dem in Schritt 2 bestimmten Rahmen
   - **Risiken & Chancen** — was könnte schiefgehen, was wäre ein Gewinn?
   - **Stakeholder** — wer ist beteiligt, wer entscheidet, wer ist betroffen?
4. **Erkenne Widersprüche** zwischen verschiedenen Quellen. Ein Widerspruch
   wird nicht aufgelöst, sondern mit beiden Quellen in `unklarheiten.md`
   notiert.
5. **Notiere Unklarheiten** — alles, was sich aus den Materialien *nicht*
   beantworten lässt. Erfinde nichts; eine offene Frage ist ein Ergebnis.
6. **Schreibe Glossareinträge** für Fachbegriffe, die im Material ohne
   Erklärung vorausgesetzt werden.

Jede Anforderung bekommt eine Belegstelle — die Referenzdatei, aus der sie
stammt. Was keine Belegstelle hat, gehört nach `unklarheiten.md`.

## Output

```
.betterplan/
├── requirements/
│   ├── 01-fachlich.md
│   ├── 02-rahmenbedingungen.md
│   ├── 03-qualitaet.md
│   ├── 04-risiken.md
│   └── 05-stakeholder.md
├── unklarheiten.md
└── GLOSSARY.md
```

## Erneutes Ausführen

Der Skill ist wiederholbar. Bei einem erneuten Durchlauf:

- Vergleiche die Referenzen mit dem, was in den Zieldateien schon steht.
- Ergänze Neues, korrigiere Veraltetes, lösche nichts ohne Grund.
- Beantwortete Punkte in `unklarheiten.md` werden nach `requirements/`
  überführt, nicht doppelt geführt.

## Manuelle Markierungen

Ein Abschnitt, dessen Überschrift von `<!-- manual -->` gefolgt wird, ist
Handarbeit des Menschen und wird **nicht überschrieben** — auch dann nicht,
wenn das Material etwas anderes sagt. Ein Konflikt mit einem solchen
Abschnitt gehört nach `unklarheiten.md`.

```markdown
## Budgetrahmen
<!-- manual -->

Vom Lenkungskreis am 12.03. festgelegt: 240k, nicht verhandelbar.
```
