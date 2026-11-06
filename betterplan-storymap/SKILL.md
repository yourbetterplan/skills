---
name: betterplan-storymap
description: >
  Builds the User Story Map of a Betterplan project from .betterplan/GOAL.md and
  the extracted requirements, and records it as Markdown under
  .betterplan/storymap/ together with a coverage artifact. Use this skill when a
  goal and requirements exist and the map itself is missing or unfinished — for
  requests like "baue die Story Map", "build the story map", "welche Epics
  braucht der Backbone", "mach aus den Anforderungen eine Map", "turn the
  requirements into a story map", or when betterplan-goal pointed at the map
  step. Runs after betterplan-extract. Re-invocable: continues an unfinished map
  rather than starting over.
metadata:
  version: "0.1.0"
---

# betterplan-storymap

Baut die User Story Map aus `GOAL.md` und den extrahierten Anforderungen.

| Ausgabe | Inhalt |
|---|---|
| `.betterplan/storymap/` | eine Datei pro Item — Initiativen, Epics, User Stories, ggf. querschnittliche Project Stories; dazu Personas und Releases |
| `.betterplan/COVERAGE.md` | Anforderung → Story, lückenlos |

**Lies vorher** `betterplan-workflow` (Klassifikation, geteilte Konventionen) und
dessen `references/method-deep-dive.md` (Map-Methode: Breite vor Tiefe, gleiche
Flughöhe, Release-Schnitte). Dieser Skill wiederholt beides nicht, er wendet es an.

## Warum es diesen Schritt gibt

`betterplan-goal` entscheidet die Initiativen, `betterplan-extract` liefert die
Anforderungen. Dazwischen liegt Arbeit, die keiner der beiden tut: welche Epics
den Backbone tragen, welche Story welche Anforderung erfüllt, und ob am Ende
keine Anforderung heimatlos ist. Ohne eigenen Schritt rutscht diese Arbeit in
die Zielklärung — dort entstand sie beim ersten Lauf, als 22 Epics in einem
Dokument, das Initiativen halten sollte.

## Voraussetzungen

- `.betterplan/GOAL.md`, alle acht Abschnitte mit Inhalt
- `.betterplan/requirements/` aus `betterplan-extract`

Fehlt eines, **brich ab** und verweise auf den zuständigen Skill. Eine Map ohne
Ziel hat kein Ordnungsprinzip; eine Map ohne Anforderungen hat keinen Inhalt.

## Ablauf

Breite vor Tiefe. Der Backbone entsteht vollständig in einem Durchgang, die
Stories danach initiativenweise — nicht umgekehrt. Wer die Stories von
Initiative 1 schreibt, bevor Initiative 5 ihre Epics hat, entscheidet Details,
die der fertige Backbone wieder umwirft.

1. **Lesen.** `GOAL.md` vollständig, die Anforderungen, und eine eventuell im
   Map-Verzeichnis liegende Arbeitsnotiz aus der Zielklärung. Die Notiz ist
   Material, keine Festlegung — sie darf vollständig umgeworfen werden.
2. **Personas und Releases festlegen.** Aus `goal:roles` und `goal:scope`, vor
   den Stories: jede Story braucht eine Persona, und wo Fristen oder Lernziele
   bestehen, ein Release. Ein Release ohne genanntes Ergebnis und ohne Frage,
   die es beantwortet, ist kein Release, sondern ein Datum.
3. **Initiativen schreiben.** Aus `goal:backbone`, in der dort entschiedenen
   Reihenfolge. Erfinde keine Initiative dazu und lasse keine weg: weicht das
   Material davon ab, ist das ein Befund für `betterplan-goal`, kein stiller
   Umbau.
4. **Backbone vollständig vorschlagen.** Alle Epics aller Initiativen in einem
   Durchgang, als Ganzes zeigen, bestätigen lassen. Schnitt nach abgrenzbarem
   Ergebnis, gleiche Flughöhe entlang des Backbones.
5. **Anforderungen den Epics zuordnen.** Was nirgends passt, ist ein Befund und
   kein Rundungsfehler: entweder fehlt ein Epic, oder die Anforderung gehört in
   eine andere Initiative, oder sie liegt außerhalb des Zuschnitts. Benennen und
   entscheiden lassen.
6. **Stories schreiben, eine Initiative pro Durchgang.** Selbst schreiben, nach
   den Inhaltsregeln von `betterplan-create-story` — Nutznießer-Perspektive,
   Beschreibungsaufbau, Akzeptanzkriterien als Zustände. Nicht pro Story an
   `betterplan-create-story` delegieren: ein Discovery-Dialog je Story skaliert
   bei dreistelligen Story-Zahlen nicht. Zeigen, bestätigen lassen, weiter.
7. **Querschnittliche Arbeit als Project Story anlegen** — sparsam. Was mehr
   als eine Story in mehr als einer Initiative betrifft, gehört nicht unter ein
   Epic; dort würde es über seine Reichweite lügen. **Ein einziger Abhängiger
   heißt: nicht querschnittlich** — dann gehört die Arbeit in jene Story.
   Typische Fälle: ein Zugang, der erst beantragt werden muss; ein
   unternehmensweiter Status, der an mehreren Stellen Folgen hat; eine
   festzuhaltende Entscheidung; das Nachziehen von Material, das noch im
   Entstehen ist. Schlage zuerst **alle** Kandidaten vor, die du siehst, und
   lasse kürzen — die Messlatte liegt beim Menschen, nicht bei dir.
8. **Abhängigkeiten setzen.** Harte als `dependsOn`, weiche als `#NNN`-Bezug im
   Text. Die Regel steht in `betterplan-workflow`.
9. **Abdeckung prüfen** und `COVERAGE.md` schreiben.
10. **Nicht importieren.** Die Übertragung nach Betterplan ist ein eigener
    Schritt mit eigenem Fehlerprofil.

Nach jeder bestätigten Naht ist die Map auf der Platte ein gültiger
Zwischenstand. Der Skill ist an jeder Naht pausierbar.

## Format der Item-Dateien

Eine Datei pro Item. Die Hierarchie steht im Pfad, die Identität im Frontmatter.

```
.betterplan/storymap/
  _personas.md
  _releases.md
  01-<initiative-slug>/
    _initiative.md
    01-<epic-slug>/
      _epic.md
      01-<story-slug>.md
```

| Feld | Für | Inhalt |
|---|---|---|
| `id` | alle | stabil und eindeutig, **nie** aus dem Pfad abgeleitet |
| `type` | alle | `initiative` · `epic` · `story` · `project` |
| `parent` | Epics, User Stories | `id` des Elternteils — Project Stories haben **keinen** |
| `title` | alle | abhakbare Verbphrase, ohne Positionsnummer |
| `order` | alle | Position unter dem Elternteil |
| `persona` | Stories | Nutznießer |
| `tags` | Stories | Zuständigkeit, nackte Rollenbezeichnung |
| `maturity` | Stories | `idea`, solange nichts anderes entschieden ist |
| `release` | wo Fristen oder Lernziele bestehen | Schlüssel aus `_releases.md` |
| `dependsOn` | wo harte Abhängigkeiten bestehen | Liste von `id`s |
| `sources` | Epics, Stories | Belegstellen im Quellmaterial |

`id` wird **nicht** aus dem Pfad abgeleitet, weil `parent`, `dependsOn` und die
`#NNN`-Bezüge darauf zeigen. Würde die Identität am Pfad hängen, bräche jede
Umsortierung und jede Umbenennung die halbe Map — und zwar stillschweigend.

Der Body ist genau das, was später `description` wird: der Nutzer-Story-Satz,
Kontext, Akzeptanzkriterien, Out of Scope, offene Fragen. Keine Metadaten in
Prosa wiederholen — was im Frontmatter steht, steht nicht nochmal im Text.

## Die Abdeckungsprüfung

`COVERAGE.md` führt jede Anforderung auf die Stories zurück, die sie erfüllen.
Drei Befundarten:

- **Anforderung ohne Story** → Lücke. Schließen, oder ausdrücklich als bewusst
  draußen begründen.
- **Story ohne Anforderung** → entweder legitim, etwa eine Klärungs-Story, die
  eine Entscheidung sichtbar macht, oder erfunden. Begründen oder löschen.
- **Anforderung in mehreren Stories** → kein Befund.

Ein Loch in der Map ist ein Befund, kein Formfehler. Ein Epic ohne Story, eine
Anforderung ohne Heimat: benennen, nicht wegdrücken und nicht mit einer
Platzhalter-Story zudecken.

## Die Project-Story-Prüfung

Eine Project Story nimmt **keinen Parent** und hängt damit neben dem Backbone.
Sie braucht deshalb eine Bindung an die Stories, die sie betrifft — über eine
**modellierte Abhängigkeit**, wo eine Reihenfolge erzwungen ist, sonst über
einen **`#NNN`-Bezug** aus den betroffenen Stories. Eine erzwungene Reihenfolge
ist ein starker Indikator für Querschnittlichkeit, **aber keine Bedingung**:
ein unternehmensweiter Status, der verändert *wie* vier Stories gemacht werden
ohne eine davon zu blockieren, hat keine Abhängigkeit — und ist trotzdem
querschnittlich.

Nenne beim Vorschlagen jeder Project Story ihre **Reichweite**, nicht erst auf
Nachfrage: *„betrifft vier Stories in zwei Initiativen, davon zwei gated
(Abhängigkeit gesetzt), zwei nur geformt (`#NNN`)"*. Eine Project Story, deren
Abhängige du nicht benennen kannst, ist eine, deren Reichweite du nicht geprüft
hast.

**Genau ein Abhängiger → keine Project Story**, sondern Inhalt jener Story:
Akzeptanzkriterium oder Beschreibung.

**Setze Project Stories sparsam ein.** Die Messlatte ist nicht „ist das
querschnittlich genug, um erlaubt zu sein", sondern **„würde dem
instanziierenden Team etwas Wesentliches fehlen, wenn das kein eigenes Item
wäre"**. Die meisten Kandidaten fallen durch: sie passen in eine User Story,
oder sie sind das *Warum* einer Story und gehören in ihren Context. Sammelt
eine Vorlage Items auf Wurzelebene an, ist sie in das Problem zurückgerutscht,
von dem die Regel eine Ausnahme ist.

**Devteam Stories und Workitems entstehen in einer Vorlage nicht.** Sie sind
Sache des ausführenden Teams. Die Regel und ihre Begründung stehen in
`betterplan-workflow`.

## Wenn das Quellmaterial ein Pflichtenkatalog ist

Verordnung, Ausschreibung, Norm, Zertifizierungsschema — Material, das als Liste
von Forderungen ankommt. Dann gilt zusätzlich:

- **Abdeckung ist das Fertigkriterium.** Jede Pflicht auf mindestens eine Story
  zurückführbar. Nicht die Anzahl der Stories, nicht die Tiefe der
  Beschreibungen.
- **Ein Hauptpfad.** Lässt die Quelle mehrere Wege zum selben Ziel zu, trägt
  einer den Backbone; die anderen sind Stories an *einem* Epic. Parallele
  Backbone-Stränge für Alternativen machen die Map unlesbar und verdoppeln alles
  Folgende.
- **Lebende externe Kataloge werden referenziert, nie kopiert.** Verweist die
  Quelle auf einen Katalog, der sich unabhängig weiterentwickelt, sagt die Story
  „wähle und bewerte die zutreffenden Einträge", nicht „Eintrag X umsetzen".
  Sonst veraltet die Map mit jedem Update der Quelle.

Die Gefahr bei solchem Material ist immer dieselbe: eine Map, die als
Pflichtenliste gelesen wird und keine Geschichte erzählt. Dagegen hilft die
Nutznießer-Perspektive aus `betterplan-workflow` — nicht Nachsicht bei der
Abdeckung.

## Erneuter Aufruf

Existiert ein Teil der Map, **lies sie zuerst**.

1. Zeige in einem Satz, was du gefunden hast: *"Aktueller Stand: Backbone
   bestätigt, Stories für zwei von fünf Initiativen, keine Abdeckungsprüfung."*
2. Frage, was das Ziel **dieser** Sitzung ist.
3. Setze an der unfertigen Naht an. Baue bestätigte Teile nicht neu.

## Abgrenzung

- **`betterplan-goal`** entscheidet die Initiativen, nicht die Epics. Muss eine
  Initiative fallen oder dazukommen, ist das ein Aufruf jenes Skills.
- **`betterplan-create-story`, `-epic`, `-initiative`** sind für einzelne
  Nachträge an einer bestehenden Map und für die Verfeinerung einzelner Stories
  nach dem Map-Bau — das ist die Arbeitsteilung, die Maturity `idea` vorsieht.
- **Der Import nach Betterplan** ist ein eigener Schritt.

## Notizen

- **Kein Automatismus.** Der Skill läuft nur auf ausdrücklichen Aufruf.
- **Körnung nach abgrenzbarem Ergebnis**, nicht nach Übersichtlichkeit. Ein
  Backbone darf lang sein; er darf nur nicht Pflichten unter Sammelüberschriften
  verstecken.
- **Die Map ist Projektdatum** und gehört in das Projekt, neben `GOAL.md`,
  `references/` und `requirements/` — nie in ein Skill-Repository.
- **Domänenwissen gehört nicht in diesen Skill.** Was nur für ein Vorhaben gilt
  — seine Initiativen, seine Personas, seine Fristen, seine Rechtslage — steht
  in dessen `GOAL.md` und in dessen Map. Hier steht nur, was für jede Map gilt.
