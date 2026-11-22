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

Die Prüfung ist eine **Entscheidungsregel**, kein Eindruck. `GOAL.md` ist
hinreichend, wenn **beides** gilt:

1. Alle acht **tragenden** Anker sind vorhanden — `goal:purpose` ·
   `goal:usage-context` · `goal:roles` · `goal:scope` · `goal:finish-line` ·
   `goal:non-goals` · `goal:backbone` · `goal:open-facts`
2. Auf **jeden** dieser Anker folgt Text, nicht nur die nächste Überschrift.

Andernfalls gilt die Datei als fehlend — auch wenn sechs von acht Abschnitten
gut gefüllt sind. Zwei fehlende Abschnitte sind zwei Entscheidungen, die nicht
getroffen wurden, und die Extraktion würde sie erfinden.

**`goal:vision` ist kein Abbruchgrund — aber kein belangloser Anker.** Die
Extraktion braucht ihn nicht zwingend, weil die Art des Vorhabens auch aus
`goal:purpose` und `goal:scope` ableitbar ist. Er ist aber **die klarste
Aussage darüber**, und davon hängt der Qualitätsrahmen ab (siehe „Was
extrahiert wird").

Fehlt die Vision: **laufe weiter, aber nenne im Bericht ausdrücklich, welche Art
Vorhaben du angenommen hast und welcher Qualitätsrahmen daraus folgt.** Eine
unausgesprochene Annahme an dieser Stelle verzerrt eine ganze Kategorie.

Ein Abbruch wäre die strengere Alternative und wäre nicht unvertretbar — er
würde allerdings jedes `GOAL.md` entwerten, das vor Einführung des Ankers
geschrieben wurde, für eine Information, die zweimal redundant im Dokument
steht.

Ein von Hand geschriebenes `GOAL.md` **ohne** Anker ist der häufigste Fall
davon. Es ist nicht unbrauchbar, aber es ist auch nicht der Vertrag: Nenne die
fehlenden Anker und verweise auf `betterplan-goal`, das ein bestehendes Ziel
schärft statt es neu zu erfinden.

## Warum ein Ziel Pflicht ist

Ohne Ziel erfindet ein Agent eines. Das ist nicht hypothetisch: beim ersten Lauf
dieses Skills auf einen Ordner voll Rechtstexte und technischer Richtlinien
entstand eine plausible, als offene Frage markierte Annahme über das
Projektziel — und darauf über hundert vollständig belegte Anforderungen,
geschnitten entlang einer Struktur, die am tatsächlichen Vorhaben vorbeiging.
Der Inhalt war richtig, der Schnitt falsch.

Ein Abbruch kostet eine Minute. Ein falscher Schnitt kostet die Arbeit, die
darauf aufbaut.

## Ablauf

1. **Vorbedingungen prüfen.** Beide. Bei Verstoß abbrechen.
2. **`GOAL.md` lesen** — zuerst, vor dem Material. Beginne mit `goal:vision`:
   der eine Satz sagt, **welche Art Vorhaben** das ist, und davon hängt der
   Qualitätsrahmen ab (siehe unten). Zweck, Rollen, Zuschnitt und
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

  **Welcher Rahmen gilt, entscheidet die Art des Vorhabens — und die steht in
  `GOAL.md`.** Lies dafür in dieser Reihenfolge: `goal:vision` (ein Satz, oft
  die klarste Aussage darüber, *was* überhaupt gebaut wird), dann `goal:purpose`
  und `goal:scope`. „Eine Software bauen" führt zu ISO 25010, „ein Angebot
  einreichen" zu Vergaberecht und Ausschreibungsunterlagen, „ein Event
  organisieren" zu Veranstaltungsrecht.

  **Nenne den gewählten Rahmen und seine Grundlage im Bericht** — auch, wenn du
  **keinen** externen Rahmen anlegst. Das ist der Normalfall, wenn das Material
  die Qualitätsanforderungen selbst normativ festlegt: eine Verordnung, eine
  Norm, ein Lastenheft. Einen externen Rahmen darüberzulegen erzeugt dann eine
  zweite Taxonomie, deren Zeilen keine Belegstelle haben.
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

Ein Abschnitt, dessen **Überschrift** von `<!-- manual -->` gefolgt wird, wird
bei einem erneuten Lauf **nicht überschrieben**. Der geschützte Bereich reicht
von der Überschrift bis zur nächsten Überschrift derselben oder einer höheren
Ebene:

```markdown
## Fristen aus dem Rahmenvertrag <!-- manual -->

Vom Kunden am 12.11. mündlich bestätigt, Vertrag folgt.

## Nächster Abschnitt            ← ab hier wieder generiert
```

Diese Markierung ist der einzige Schutz, den handgeschriebener Text hat. Zwei
Regeln dazu:

- **Widerspricht das Material einem markierten Abschnitt**, überschreibe ihn
  nicht und korrigiere ihn nicht. Der Widerspruch gehört nach
  `unklarheiten.md` — mit beiden Fassungen und der Quelle.
- **Lösche nichts ohne Grund.** Ergänze Neues, korrigiere Veraltetes, und wenn
  du etwas entfernst, sag im Bericht welche Zeile und warum.

## Erneuter Lauf

Der Skill ist wiederholbar:

- **`<!-- manual -->` bleibt unangetastet.**
- **Beantwortete Unklarheiten wandern**, statt sich zu verdoppeln. Wird eine
  Frage aus `unklarheiten.md` durch neues Material beantwortet, wird daraus
  eine Anforderung in `requirements/` und der Eintrag verschwindet aus
  `unklarheiten.md` — nicht beides.
- **Zeitstempel taugen nicht als Inkrementalitätssignal.**
  `betterplan-transform` schreibt bei jedem Lauf alle Referenzen neu, also ist
  nach einem Transform-Lauf *jede* Referenz neuer als *jede* Ausgabe. Wer darauf
  baut, extrahiert immer alles neu und nennt es inkrementell. Vergleiche
  stattdessen den `source:`- und `converted:`-Wert im Kopf der Referenz mit dem,
  was im letzten `EXTRACTION-REPORT.md` als gelesen vermerkt ist — oder sag
  ehrlich, dass dieser Lauf eine Vollextraktion ist.
- **Haben sich die Referenzen geändert, nachdem `GOAL.md` geschrieben wurde**,
  ist das Ziel möglicherweise überholt: **warnen und weiterlaufen**, nicht
  blockieren. Bei jedem erneuten `transform` zu blockieren wäre feindselig.
  Ob das Ziel nachgezogen wird, entscheidet der Mensch.

## Notizen

- **Kein Automatismus.** Der Skill läuft nur auf ausdrücklichen Aufruf.
- **Sprache**: Schreibe in der Sprache, in der der Mensch schreibt.
- **Anforderungen sind kein Ziel.** Das Ziel sagt, wozu das Vorhaben da ist;
  die Anforderungen sagen, was dafür gilt. Wer das vermischt, extrahiert
  Wunschdenken.
