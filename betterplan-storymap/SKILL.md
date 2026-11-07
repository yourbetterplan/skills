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
  version: "0.2.0"
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

- `.betterplan/GOAL.md`, die acht tragenden Abschnitte mit Inhalt
- `.betterplan/requirements/` aus `betterplan-extract`

Fehlt eines, **brich ab** und verweise auf den zuständigen Skill. Eine Map ohne
Ziel hat kein Ordnungsprinzip; eine Map ohne Anforderungen hat keinen Inhalt.

### Die Vision — nachfragen, nicht abbrechen

**Prüfe `goal:vision`, bevor du irgendetwas anderes tust.** Ein Satz, der sagt,
worum es geht: *„Ein Angebot erstellen, das wir einreichen können."* ·
*„Personen einen guten Start in diesen Prozess geben."* ·
*„Nutzern ermöglichen, ihr Gerät ohne Fachwissen sicher einzurichten."*

- **Vorhanden** → lies sie und halte sie beim Bauen gegen. Driftet eine
  Initiative von ihr ab, ist das ein Befund für `betterplan-goal`.
- **Fehlt** → stelle **eine** Frage: *„Worum geht es hier in einem Satz?"*,
  und schreibe die Antwort als `goal:vision` nach `GOAL.md`. Nicht abbrechen,
  nicht in `betterplan-goal` weiterschicken: es ist ein Satz, und wer die Map
  bauen will, soll dafür nicht die Richtung wechseln müssen.

Das ist die **einzige** Stelle, an der dieser Skill `GOAL.md` schreibt. Alle
übrigen Abschnitte gehören `betterplan-goal`; weicht dort etwas ab, ist das ein
Befund, kein stiller Umbau.

**Warum das vor dem Lesen kommt:** die Vision ist die erste grobe Richtung, an
der sich entscheidet, ob ein Backbone die richtige Geschichte erzählt. Und sie
wird beim späteren Übertragen nach Betterplan die **Projektbeschreibung** — ein
Playbook ohne sie liefert dem instanziierenden Team eine Map ohne Überschrift.

**Die Vision beschreibt das Vorhaben, das `GOAL.md` beschreibt.** Beim Bau einer
Vorlage ist das der Vorlagenbau selbst. Der Satz, den ein instanziierendes Team
erbt, kann ein anderer sein — diese Frage ist **nicht entschieden** und fällt
beim Übertragen nach Betterplan an. Erfinde hier keine zweite Vision.

## Ablauf

Breite vor Tiefe. Der Backbone entsteht vollständig in einem Durchgang, die
Stories danach initiativenweise — nicht umgekehrt. Wer die Stories von
Initiative 1 schreibt, bevor Initiative 5 ihre Epics hat, entscheidet Details,
die der fertige Backbone wieder umwirft.

1. **Vision prüfen.** Vor allem anderen, siehe oben: vorhanden → gegenhalten;
   fehlt → eine Frage, Antwort nach `GOAL.md`.
2. **Lesen.** `GOAL.md` vollständig, die Anforderungen, und eine eventuell im
   Map-Verzeichnis liegende Arbeitsnotiz aus der Zielklärung. Die Notiz ist
   Material, keine Festlegung — sie darf vollständig umgeworfen werden.
3. **Personas und Releases festlegen.** Aus `goal:roles` und `goal:scope`, vor
   den Stories: jede Story braucht eine Persona, und wo Fristen oder Lernziele
   bestehen, ein Release. Ein Release ohne genanntes Ergebnis und ohne Frage,
   die es beantwortet, ist kein Release, sondern ein Datum. **Beide sind eigene
   Betterplan-Objekte mit festem Feldsatz — schreibe sie feldweise**, siehe
   unten.
4. **Initiativen schreiben.** Aus `goal:backbone`, in der dort entschiedenen
   Reihenfolge. Erfinde keine Initiative dazu und lasse keine weg: weicht das
   Material davon ab, ist das ein Befund für `betterplan-goal`, kein stiller
   Umbau.
5. **Backbone vollständig vorschlagen.** Alle Epics aller Initiativen in einem
   Durchgang, als Ganzes zeigen, bestätigen lassen. Schnitt nach abgrenzbarem
   Ergebnis, gleiche Flughöhe entlang des Backbones.
6. **Anforderungen den Epics zuordnen.** Was nirgends passt, ist ein Befund und
   kein Rundungsfehler: entweder fehlt ein Epic, oder die Anforderung gehört in
   eine andere Initiative, oder sie liegt außerhalb des Zuschnitts. Benennen und
   entscheiden lassen.
7. **Stories schreiben, eine Initiative pro Durchgang.** Selbst schreiben, nach
   den Inhaltsregeln von `betterplan-create-story` — Nutznießer-Perspektive,
   Beschreibungsaufbau, Akzeptanzkriterien als Zustände. Nicht pro Story an
   `betterplan-create-story` delegieren: ein Discovery-Dialog je Story skaliert
   bei dreistelligen Story-Zahlen nicht. Zeigen, bestätigen lassen, weiter.
8. **Querschnittliche Arbeit als Project Story anlegen** — sparsam. Was mehr
   als eine Story in mehr als einer Initiative betrifft, gehört nicht unter ein
   Epic; dort würde es über seine Reichweite lügen. **Ein einziger Abhängiger
   heißt: nicht querschnittlich** — dann gehört die Arbeit in jene Story.
   Typische Fälle: ein Zugang, der erst beantragt werden muss; ein
   unternehmensweiter Status, der an mehreren Stellen Folgen hat; eine
   festzuhaltende Entscheidung; das Nachziehen von Material, das noch im
   Entstehen ist. Schlage zuerst **alle** Kandidaten vor, die du siehst, und
   lasse kürzen — die Messlatte liegt beim Menschen, nicht bei dir.
9. **Abhängigkeiten setzen.** Harte als `dependsOn`, weiche als `shapedBy` —
   letzteres wird beim Import zum `#NNN`-Bezug im Text. Die Regel steht in
   `betterplan-workflow`.
10. **Maschinell prüfen**, dann **Abdeckung prüfen** und `COVERAGE.md` schreiben.
    Erst die Verweise, dann die Inhalte: ein nicht auflösender `parent` macht
    jede Abdeckungsaussage darüber wertlos.
11. **Nicht importieren.** Die Übertragung nach Betterplan ist ein eigener
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
| `id` | alle | **UUID**, eindeutig, **nie** aus Pfad oder Titel abgeleitet |
| `type` | alle | `initiative` · `epic` · `story` · `project` |
| `parent` | Epics, User Stories | `id` des Elternteils — Project Stories haben **keinen** |
| `title` | alle | abhakbare Verbphrase, ohne Positionsnummer |
| `order` | alle | Position unter dem Elternteil |
| `persona` | Stories | Schlüssel aus `_personas.md` |
| `tags` | Stories | Zuständigkeit, nackte Rollenbezeichnung |
| `priority` | nur wo **nicht** der Projekt-Default | MoSCoW-Abweichung, siehe unten |
| `maturity` | Stories | `idea`, solange nichts anderes entschieden ist |
| `release` | wo Fristen oder Lernziele bestehen | Schlüssel aus `_releases.md` |
| `dependsOn` | wo harte Abhängigkeiten bestehen | Liste von `id`s |
| `shapedBy` | wo weiche Bezüge bestehen | Liste von `id`s — wird beim Import zu `#NNN` im Text |
| `sources` | Epics, Stories | Belegstellen im Quellmaterial |

**`id` ist eine UUID, kein sprechender Slug.** Sie wird nicht aus dem Pfad
abgeleitet, weil `parent`, `dependsOn` und `shapedBy` darauf zeigen — hinge die
Identität am Pfad, bräche jede Umsortierung stillschweigend die halbe Map. Und
sie wird auch nicht aus dem **Titel** abgeleitet, weil das derselbe Fehler eine
Schicht höher ist: ein Slug wie `E-sicher-implementieren` ist eine zweite,
informelle Bedeutungsschicht neben dem Titel, und sie veraltet, sobald der Titel
sich ändert. Übrig bliebe eine `id`, die etwas anderes behauptet als der Titel,
auf die aber alle Verweise zeigen — also nicht umbenennbar. Eine UUID kann nichts
behaupten; das ist ihr Vorzug.

Der Preis ist unleserliches Frontmatter. Dagegen zwei Regeln: **in Prosa wird
immer der Titel referenziert, nie die `id`**, und das Map-Verzeichnis trägt eine
abgeleitete `_index.md` mit Titel → `id`.

`shapedBy` ist die Markdown-Vorstufe des `#NNN`-Bezugs. In Betterplan gibt es
dafür keine Modellierung, nur Prosa — solange die Aufgabennummern nicht
existieren, trägt das Frontmatter die Beziehung, und der Import löst sie in den
Beschreibungstext auf. Ein Format, das weiche Bezüge nur in Prosa kennt, verliert
sie beim Übertragen.

Der Body ist genau das, was später `description` wird: der Nutzer-Story-Satz,
Kontext, Akzeptanzkriterien, Out of Scope, offene Fragen. Keine Metadaten in
Prosa wiederholen — was im Frontmatter steht, steht nicht nochmal im Text.

## Personas und Releases sind Objekte, nicht Prosa

Beide sind **eigene Betterplan-Objekte mit festem Feldsatz**. Eine Katalogdatei,
die sie als Prosa beschreibt, muss beim Übertragen erst zerlegt werden — und
dabei entscheidet der Übertragende, was in welches Feld gehört. Das ist eine
Entscheidung, die in den Map-Bau gehört, nicht in den Import.

**Schreibe beide feldweise, mit den Feldnamen im Text.** Die MCP-Werkzeuge
beschreiben ihre Felder zur Laufzeit selbst — frage sie ab, statt den Feldsatz
aus dem Gedächtnis zu setzen, und schreibe die Katalogdatei nach dem, was sie
sagen. Zum Zeitpunkt dieser Fassung sind das acht Felder für eine Persona (`name`
als Pflichtfeld und im Projekt eindeutig, dazu `role`, `goals`, `wishes`,
`challenges`, `currentBehavior`, `currentWorkaround`, `notes`) und für ein Release
`title` und `position` als Pflichtfelder, dazu `date`, `dateLabel`, `goal`,
`features`, `metrics`, `status`.

Drei Dinge, die sich dabei regelmäßig zeigen:

- **Ein Feld, das die Quelle nicht hergibt, wird als erschlossen markiert.**
  Bei Pflichtenmaterial ist das der Normalfall für `currentBehavior` und
  `currentWorkaround`: eine Verordnung beschreibt Pflichten, nicht
  Nutzerverhalten. Schreibe die plausible Annahme hin **und dass sie eine ist** —
  sonst nimmt das instanziierende Team eine Erfindung für eine Erkenntnis.
  Gelegentlich belegt die Quelle es doch, und dann ist die Belegstelle wertvoll.
- **Ein Release ohne Feld für Kommentar.** Releases haben kein `notes`. Was ein
  Release über sich selbst zu sagen hat, gehört in `goal`, `features` oder
  `metrics`; die Begründung des Releaseschnitts bleibt außerhalb der Felder und
  wird als Kommentar gekennzeichnet.
- **Ein Datum, das nur das instanziierende Team kennt, bleibt leer.** Hängt ein
  Release an einer Frist, die das Team selbst setzt, ist `date` leer und `goal`
  sagt, woraus sich das Datum ergibt. Ein geratenes Datum ist schlechter als
  keines.

**Dauerarbeit bekommt kein Release.** Eine Pflicht, die über Jahre läuft, hat
kein Fertigdatum; sie einem Release zuzuordnen behauptet, sie sei dort erledigt —
genau die Lüge, die die Trennung von Aufbauen und Betreiben im Backbone
verhindern soll. Hat eine Betriebs-Initiative einen einzelnen Schritt mit echtem
Ergebnis und Datum, trägt **nur dieser** ein Release.

## MoSCoW — nur wenn es unterscheidet, und nur die Abweichungen

Eine Priorisierung ist eine **Ableitung aus dem Material**, keine Schätzung. Vor
dem Tag steht deshalb eine Messung: **gibt das Quellmaterial Modalitäten her,
und unterscheiden sie sich?**

- Bei Pflichtenmaterial nach BCP 14 steht die Modalität schon auf jeder
  Anforderung (MUSS / SOLL / KANN / nicht normativ) — zähle sie aus. Sind weniger
  als rund 15 % nicht-MUSS, trägt kein Filter, und du lässt es.
- Gibt es keine Modalitäten, leitest du keine Priorität her. Eine erfundene
  Priorisierung ist schlechter als keine.

**Die Ableitungsregel: eine Story trägt die stärkste Modalität, die sie
erfüllt.** Eine Story mit mindestens einer MUSS-Anforderung ist Must, auch wenn
sie daneben zehn SOLL-Anforderungen erfüllt. Should ist eine Story, deren
Anforderungen ausschließlich SOLL sind; Could eine, deren Anforderungen
ausschließlich KANN oder nicht normativ sind.

**Taggen nur die Abweichungen vom Default.** Bei Pflichtenmaterial ist fast alles
Must — dann wird Must **nicht** getaggt, sondern einmal dokumentiert. Achtzig
`Must`-Tags kosten auf jeder Karte Breite und beantworten keine Frage, weil ein
Filter darauf alles zurückgibt. Der Wert liegt in der kleinen Menge, die man
weglassen kann, wenn ein Termin kippt.

**Tag-Werte bleiben kurz.** `Must`, `Should`, `Could` tragen ihre Bedeutung
selbst und verdienen kein Kategoriewort — `project:Should`, nicht
`project:Priorität Should`. Die Regel und ihre Begründung stehen in
`betterplan-workflow/references/data-model.md` unter *Tags — namespacing rules*;
sie gilt für jede Tag-Dimension, nicht nur für die Priorität.

**Kein `Won't`.** Was wir nicht machen, ist kein Item: es steht als abgelehnter
Kandidat mit Begründung neben der Map und in `goal:non-goals`. Ein `Won't` auf
einer Karte würde heißen „wir führen das, machen es aber nicht" — dafür gibt es
den Closed-Zustand.

**Wo die Priorität produktabhängig ist, wird nicht getaggt.** Varianten an einem
Epic sind **Alternativen, nicht Prioritäten**: welcher Weg Pflicht ist,
entscheidet eine Eigenschaft des Produkts, die eine Vorlage nicht kennt. Ein
`Could` auf einer Variante, die für manche Fälle der einzige zulässige Weg ist,
ist sachlich falsch. Die Variantenstory sagt stattdessen im Text, für welchen
Fall sie zum Pflichtweg wird.

## Die Map ist maschinell prüfbar

Das Markdown-Zwischenformat erlaubt eine Prüfung, die in Betterplan selbst
niemand mehr macht — nutze sie, statt Verweise mit dem Auge zu verfolgen. Prüfbar
und wert, geprüft zu werden, ist alles, was **stillschweigend** bricht:

- `id` ist eine UUID und projektweit eindeutig
- `parent`, `dependsOn`, `shapedBy`, `persona` und `release` lösen auf einen
  existierenden Eintrag auf
- Epics und User Stories haben einen Parent, Initiativen und Project Stories
  keinen
- keine Abhängigkeit zeigt auf sich selbst oder läuft im Kreis
- `priority` trägt nur erlaubte Werte und widerspricht nicht den `sources`
- kein Epic ohne Story

Ein Loch, das ein Skript findet, ist billiger als eines, das der Import findet.
Lege das Prüfskript ins Projekt, nicht in dieses Skill-Repository — es kennt die
Konventionen *dieser* Map.

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
