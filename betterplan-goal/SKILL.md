---
name: betterplan-goal
description: >
  Defines the goal of a Betterplan project and records it in .betterplan/GOAL.md.
  Use this skill when the goal of an endeavor is unclear or needs sharpening —
  for requests like "what is this project actually for", "we need a goal",
  "define the goal", "what should come out of this", "worum geht es in diesem
  Projekt", "wir brauchen ein Ziel", or when betterplan-extract stopped because
  GOAL.md was missing. Runs after betterplan-transform and before
  betterplan-extract. Re-invocable: sharpens an existing goal rather than
  starting over. Delegates the interview itself to the generic grilling skill.
metadata:
  version: "0.1.0"
---

# betterplan-goal

Schreibt das Ziel des Projekts nach `.betterplan/GOAL.md` — das Dokument, auf
das sich die nachfolgenden Schritte verlassen.

| Ausgabe | Inhalt |
|---|---|
| `GOAL.md` | Zweck, Einsatzkontext, Rollen, Zuschnitt, Ziellinie, Nicht-Ziele, Backbone-Gestalt, offene Tatsachen |

## Warum es diesen Schritt gibt

`betterplan-extract` kategorisiert Anforderungen, erkennt Widersprüche und
notiert offene Fragen. Wie es schneidet, hängt vollständig davon ab, wozu das
Projekt überhaupt da ist. Ohne Ziel erfindet ein Agent eines — plausibel,
belegt, und möglicherweise am tatsächlichen Vorhaben vorbei. Das Ergebnis ist
dann inhaltlich richtig und strukturell falsch, was teurer ist als ein Abbruch.

## Voraussetzungen

- `betterplan-transform` wurde ausgeführt → `.betterplan/references/` existiert

Fehlt das Verzeichnis, **brich ab** und verweise auf `betterplan-transform`.
Ein Ziel, das ohne Blick auf das Material entsteht, ist eine Vermutung.

## Ablauf

1. **Referenzen lesen.** Verschaffe dir einen Überblick über das Material,
   bevor du die erste Frage stellst. Bei gesplitteten Referenzen genügen die
   `INDEX.md`-Dateien plus gezielte Abschnitte — nicht alles vollständig lesen.
2. **`grilling` aufrufen.** Das Verfahren liefert dieser Skill nicht selbst.
   Rufe den Skill `grilling` auf und führe damit die Befragung.
3. **`GOAL.md` schreiben** — in der Sprache, in der der Mensch schreibt.
4. **Nicht weiterlaufen.** Das Extrahieren (`betterplan-extract`) und das Bauen
   der Story Map (`betterplan-storymap`) sind eigene Schritte mit eigenen
   Skills.

## Das Fragenterritorium

Das hält dieser Skill, nicht `grilling`: welche Entscheidungen ein
Betterplan-Projektziel überhaupt braucht. Die Liste ist Territorium, kein
Fragebogen — niemals abhaken, sondern als Landkarte benutzen, wenn du prüfst,
was noch offen ist.

- **Zweck** — was das Vorhaben erreicht, und für wen
- **Einsatzkontext** — wer das Ergebnis liest, in welcher Situation
- **Rollen** — wer Pflichten trägt, wer Nutzen hat, wer nur Adressat ist
- **Zuschnitt** — welche Art Produkt oder Gegenstand, ausdrücklich eingegrenzt
- **Ziellinie** — welcher Zustand als fertig gilt
- **Nicht-Ziele** — was absichtlich draußen bleibt
- **Backbone-Gestalt** — welche Initiativen die Story Map tragen wird, in
  welcher Reihenfolge; zur Flughöhe siehe unten
- **Offene Tatsachen** — was nur der Mensch beantworten kann, festgehalten statt geraten

Mehrere dieser Entscheidungen lassen sich nur mit dem Betterplan-Datenmodell im
Kopf stellen: ob eine Rolle eine Persona oder ein Tag wird, ob etwas als
Initiative oder als Epic trägt, dass ein Epic genau eine Initiative als Eltern
hat, dass Project und Devteam Stories auf Wurzelebene hängen. Lies
`betterplan-workflow`, bevor du zum Backbone fragst.

### Flughöhe der Backbone-Frage

Der Abschnitt `goal:backbone` enthält genau drei Dinge:

1. die Initiativen, jede mit einem Satz, was sie erreicht,
2. ihre Reihenfolge,
3. die Begründung der Reihenfolgeentscheidungen, die nicht selbsterklärend sind.

Die Epic-Ebene gehört in den Map-Bau (`betterplan-storymap`). Rutscht die
Befragung trotzdem dorthin — das passiert, und es ist nützlich, weil
Widersprüche im Material oft erst auf Epic-Ebene auffallen —, dann landet das
Ergebnis in einer Arbeitsnotiz im Map-Verzeichnis des Projekts, ausdrücklich
als Entwurf gekennzeichnet, und `goal:backbone` verweist darauf.

Diese Grenze ist nicht kosmetisch. Die Initiativen entscheiden, wie
`betterplan-extract` die Anforderungen schneidet — deshalb gehören sie hierher.
Die Epics entscheiden nichts an der Extraktion und wären in `GOAL.md` eine
eingefrorene Struktur, die der Map-Bau später nicht mehr frei umwerfen kann.

## Format von `GOAL.md`

Acht Abschnitte. Die Überschriften stehen in der Sprache des Menschen, tragen
aber einen **stabilen Anker**, damit sich nachfolgende Skills darauf verlassen
können, ohne die Sprache zu kennen:

```markdown
# Ziel: <Projektname>

## Zweck <!-- goal:purpose -->
…

## Einsatzkontext <!-- goal:usage-context -->
…
```

Die acht Anker, vollständig und unverändert:

`goal:purpose` · `goal:usage-context` · `goal:roles` · `goal:scope` ·
`goal:finish-line` · `goal:non-goals` · `goal:backbone` · `goal:open-facts`

Jeder Abschnitt muss Inhalt haben. Eine Überschrift ohne Text zählt als
fehlend — nachfolgende Skills behandeln ein solches `GOAL.md` wie keines.

`GOAL.md` ist von Hand editierbar. Es ist Projektdatum und gehört in das
Projekt, nicht in ein Skill-Repository.

## Erneuter Aufruf

Existiert `GOAL.md` bereits, **lies es zuerst** und schärfe es. Fang nicht von
vorn an und litigiere nichts neu, was dort schon entschieden steht.

1. Zeige in einem Satz, was du gefunden hast: *"Aktueller Stand: acht Abschnitte, drei offene Tatsachen, Backbone mit fünf Initiativen."*
2. Frage, was das Ziel **dieser** Sitzung ist.
3. Grille nur die Teile, die noch offen oder inzwischen überholt sind.

Der typische Anlass dafür ist der Extraktionsbericht: `betterplan-extract`
schlägt am Ende vor, wo das Ziel nach Sichtung des Materials schärfer werden
kann. Diese Verfeinerung ist ein Aufruf dieses Skills — nicht ein zweiter Lauf
der Extraktion.

## Abgrenzung zu `grilling`

Dieser Skill ist **kein Einstiegspunkt fürs Grillen** und darf keiner werden.
Er besitzt das Fragenterritorium eines Projektziels und das Dateiformat; das
Verfahren leiht er sich.

Jede andere Grill-Sitzung — eine Architekturentscheidung, ein Plan, eine Idee —
ruft `grilling` direkt auf.

## Notizen

- **Kein Automatismus.** Der Skill läuft nur auf ausdrücklichen Aufruf.
- **Ändert sich das Material**, veraltet das Ziel möglicherweise.
  `betterplan-extract` warnt in diesem Fall und läuft weiter; es blockiert
  nicht. Ob das Ziel nachgezogen wird, entscheidet der Mensch.
- **Ein Ziel ist keine Anforderungsliste.** Anforderungen entstehen in
  `betterplan-extract` aus dem Material. Hier geht es um die Absicht, an der
  sich später entscheidet, wie dieses Material geschnitten wird.
