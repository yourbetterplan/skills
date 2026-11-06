---
name: betterplan-extract
description: >
  Extracts structured domain knowledge from the transformed references:
  requirements, constraints, quality attributes, risks, stakeholders, open
  questions and a glossary. Requires .betterplan/GOAL.md — without a goal the
  extraction has no basis for deciding how to cut. Reads from
  .betterplan/references/, writes to .betterplan/requirements/,
  .betterplan/unklarheiten.md, .betterplan/GLOSSARY.md and
  .betterplan/EXTRACTION-REPORT.md. Re-runnable: updates existing files,
  preserves manual edits via markers.
metadata:
  version: "0.2.0"
---

# betterplan-extract

Extrahiert aus den transformierten Referenzen (`.betterplan/references/`) das
strukturierte Domänenwissen des Projekts.

| Ausgabe | Inhalt |
|---|---|
| `requirements/` | Kategorisierte Anforderungen |
| `unklarheiten.md` | Offene Fragen, Widersprüche, Entscheidungsbedarf |
| `GLOSSARY.md` | Zentrale Begriffe und ihre Definitionen |
| `EXTRACTION-REPORT.md` | Was gelesen wurde, wie geschnitten wurde, und warum |

Das ist **Agentenarbeit, kein Skript.** Kategorisieren, Widersprüche erkennen
und Unklarheiten benennen ist semantische Arbeit; ein Skript, das Dateien
anlegt, würde mehr versprechen als es hält.

## Voraussetzungen

| | |
|---|---|
| `.betterplan/references/` | aus `betterplan-transform` |
| `.betterplan/GOAL.md` | aus `betterplan-goal` — **harte Vorbedingung** |

Fehlt eines der beiden, **brich ab** und verweise auf den zuständigen Skill.
Nicht weiterlaufen.

Als fehlend gilt ein `GOAL.md` auch dann, wenn es existiert, aber leer ist oder
nur aus Überschriften ohne Inhalt besteht. Prüfe die acht Anker:

`goal:purpose` · `goal:usage-context` · `goal:roles` · `goal:scope` ·
`goal:finish-line` · `goal:non-goals` · `goal:backbone` · `goal:open-facts`

## Warum ein Ziel Pflicht ist

Ohne Ziel erfindet ein Agent eines. Das ist nicht hypothetisch: Beim ersten
Lauf dieses Skills auf einen Ordner mit EU-Verordnung und BSI-Richtlinien
entstand eine plausible, als offene Frage markierte Annahme über das
Projektziel — und darauf 146 vollständig belegte Anforderungen, geschnitten
entlang einer Struktur, die am tatsächlichen Vorhaben vorbeiging. Der Inhalt war
richtig, der Schnitt falsch.

Ein Abbruch kostet eine Minute. Ein falscher Schnitt kostet die Arbeit, die
darauf aufbaut.

## Ablauf

1. **Vorbedingungen prüfen.** Beide. Bei Verstoß abbrechen.
2. **`GOAL.md` lesen** — zuerst, vor dem Material. Zweck, Rollen, Zuschnitt und
   Ziellinie bestimmen, welche Kategorien es gibt und wie geschnitten wird.
3. **Referenzen lesen** (siehe unten).
4. **Extrahieren** und die Ausgabedateien schreiben.
5. **`EXTRACTION-REPORT.md` schreiben.**
6. Im Chat nur so viel zeigen, dass der Mensch entscheiden kann, ob er
   weiterliest oder abbricht.

## Referenzen lesen

Lies `references/` **rekursiv**, nicht flach.

1. `references/INDEX.md` gibt den Überblick über alle Dokumente.
2. Für ein aufgeteiltes Dokument ist `references/<slug>/INDEX.md` der Einstieg —
   es listet die Abschnitte mit sprechenden Titeln.
3. **Hole Abschnittsdateien gezielt**, nicht alle. Ein 465-KB-Dokument
   vollständig in den Kontext zu ziehen, nur um eine Fristenregel zu finden, ist
   genau das, wogegen die Aufteilung gebaut wurde.
4. Dokumente unter der Aufteilungsschwelle liegen als einzelne
   `references/<slug>.md` vor.

Verlasse dich beim Zitieren auf den Kopf jeder Abschnittsdatei: er nennt
Quelldokument und Zeilenbereich im Original.

## Was extrahiert wird

Für jede Referenz, gerahmt durch das Ziel:

- **Fachliche Anforderungen** — was muss das Projekt oder die Lösung können?
- **Rahmenbedingungen** — Termine, Recht, Budget, Organisation, Quellenstatus
- **Qualitätsanforderungen** — abhängig vom Projektkontext
  (für Software: ISO 25010; für Bau: DIN-Normen; für Events: Veranstaltungsrecht)
- **Risiken & Chancen** — was könnte schiefgehen, was wäre ein Gewinn?
- **Stakeholder** — wer trägt Pflichten, wer hat Nutzen, wer ist nur Adressat?

Dazu quer über alle Referenzen:

- **Widersprüche** zwischen Quellen — und innerhalb einer Quelle
- **Unklarheiten**, die sich aus dem Material nicht beantworten lassen
- **Glossareinträge** für Fachbegriffe

**Jede Anforderung trägt einen Quellenverweis.** Eine Anforderung ohne Beleg ist
eine Behauptung und für ein Playbook wertlos.

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
├── GLOSSARY.md
└── EXTRACTION-REPORT.md
```

Die Gliederung der `requirements/` ist ein Vorschlag, nicht Gesetz. Wenn das
Ziel einen anderen Schnitt verlangt, nimm den anderen Schnitt — und begründe
ihn im Bericht.

## Der Extraktionsbericht

Das Material ist in der Regel zu umfangreich, um die Ausgabe vollständig
gegenzulesen, bevor man merkt, dass die Richtung falsch war. Dafür ist der
Bericht da. Er enthält:

- **Was gelesen wurde** — welche Dokumente, welche Abschnitte, was ausgelassen
  wurde und warum
- **Wie geschnitten wurde, und warum** — welche Kategorien entstanden sind und
  welche Entscheidung des Ziels sie begründet
- **Welche Entscheidungen ohne Auftrag getroffen wurden** — Annahmen,
  Gliederungsentscheidungen, Einordnungen, die der Mensch nicht vorgegeben hat
- **Was nicht extrahiert wurde** — und ob das Absicht war
- **Vorschlag zur Zielschärfung** — was das Material über das Ziel gelehrt hat

Die Schärfung selbst ist ein **erneuter Aufruf von `betterplan-goal`**, nicht
ein zweiter Lauf der Extraktion.

## Manuelle Markierungen

Abschnitte mit `<!-- manual -->` im Kopf werden bei einem erneuten Lauf **nicht
überschrieben**. So überleben handgeschriebene Ergänzungen die Neu-Extraktion.

## Erneuter Lauf

Der Skill ist wiederholbar und arbeitet inkrementell — über gelesene Zeitstempel
und Markierungen, nicht über Skriptlogik:

- Ist eine Referenz **neuer** als die Ausgaben, in die sie eingeflossen ist,
  melde das und extrahiere sie neu.
- Haben sich die Referenzen geändert, **nachdem** `GOAL.md` geschrieben wurde,
  ist das Ziel möglicherweise überholt: **warnen und weiterlaufen**, nicht
  blockieren. Bei jedem erneuten `transform` zu blockieren wäre feindselig.
  Ob das Ziel nachgezogen wird, entscheidet der Mensch.
- `<!-- manual -->` bleibt unangetastet.

## Notizen

- **Kein Automatismus.** Der Skill läuft nur auf ausdrücklichen Aufruf.
- **Sprache**: Schreibe in der Sprache, in der der Mensch schreibt.
- **Anforderungen sind kein Ziel.** Das Ziel sagt, wozu das Vorhaben da ist;
  die Anforderungen sagen, was dafür gilt. Wer das vermischt, extrahiert
  Wunschdenken.
