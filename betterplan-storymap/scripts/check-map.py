#!/usr/bin/env python3
"""Prüft eine Story Map auf alles, was stillschweigend bricht.

    python3 check-map.py --project <projektroot>

**Vor `build-import.py` laufen lassen.** Der Generator bricht bei den groben
Fehlern ab — fehlendes `position`, unbekannte Farbe, Item-Datei mit `id` ohne
`type`. Die stillen lässt er durch: ein Verweis, der nicht auflöst, ein
Anzeigetext, der veraltet ist, ein Epic ohne Story, ein Zyklus. Die kommen
unbemerkt in Betterplan an und sind dort nicht mehr zu finden.

Geprüft wird, was ein Mensch beim Lesen nicht sieht und was der Import nicht
abweist. **Inhaltliche Qualität prüft es nicht** — dafür ist
`betterplan-create-story` der Maßstab.

Befunde sind zweigeteilt, weil sie es verdienen:

* **Fehler** (Exit 1) brechen etwas. Entweder scheitert der Import, oder er
  gelingt und die Map behauptet danach etwas Falsches.
* **Hinweise** (Exit 0) sind Urteilsfragen. Sie können richtig sein; ein
  Mensch entscheidet. Ein Prüfskript, das sie als Fehler führt, wird
  abgeschaltet, und dann findet es auch die Fehler nicht mehr.

Der Prüfer liest die Map mit **demselben Parser wie `build-import.py`**:
`frontmatter()`, `catalogue()`, `CATALOGUES`, `PALETTE` und `PROSE_REF` kommen
von dort. Zwei Vorstellungen davon, was eine Item-Datei ist, wären genau der
Fehlertyp, den dieses Skript finden soll.

Exit 0 = sauber (ggf. mit Hinweisen), 1 = Fehler, 2 = Map nicht gefunden.
"""
from __future__ import annotations
import argparse
import collections
import importlib.util
import pathlib
import re
import sys

# Der Generator liegt daneben. Sein Dateiname trägt einen Bindestrich und ist
# damit kein Modulname, also über die Datei laden. `main()` dort ist hinter
# `if __name__` geschützt, das Laden führt nichts aus.
_path = pathlib.Path(__file__).with_name("build-import.py")
_spec = importlib.util.spec_from_file_location("build_import", _path)
if _spec is None or _spec.loader is None:          # pragma: no cover
    sys.exit(f"❌ {_path} nicht lesbar — der Prüfer braucht seinen Parser")
_bi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bi)

frontmatter, catalogue = _bi.frontmatter, _bi.catalogue
CATALOGUES, PALETTE, PROSE_REF = _bi.CATALOGUES, _bi.PALETTE, _bi.PROSE_REF

UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

# Die Hierarchie aus `betterplan-workflow/references/data-model.md`. Nicht nur
# „hat einen Parent", sondern **welchen** — eine Story unter einer Initiative
# ist eine verdrehte Hierarchie, die jeder Aufruf anstandslos anlegt.
PARENT_OF = {
    "epic": {"initiative"},
    "story": {"epic"},
    "workitem": {"story", "project", "dev"},
}
ROOTLESS = {"initiative", "project", "dev"}
TYPES = {"initiative", "epic", "story", "project", "dev", "workitem"}

# Modalitäten, die eine MUSS-Anforderung anzeigen. Trägt eine Story einen
# `priority`-Tag und belegt sie gleichzeitig eine Pflicht, gewinnt die
# stärkere Modalität — ein `Could` auf einer Pflicht ist eine Fehlangabe.
MUST_MARKERS = ("MUSS", "DARF NICHT", "MUST", "SHALL")

ERRORS: list[str] = []
WARNINGS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def as_list(value) -> list:
    """Ein Feld, das eine Liste sein darf, als Liste.

    `dependsOn: <id>` und `dependsOn:` + Blockliste sind beide zulässig, und
    eine Prüfung über eine Zeichenkette iteriert über **Zeichen**. Das
    scheitert nicht, es zählt nur Unsinn.
    """
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def load(root: pathlib.Path) -> tuple[dict, dict, dict]:
    """Item-Dateien unter `storymap/`: id → Frontmatter, Pfad, Body.

    Dieselbe Auswahl wie im Generator: alles außer den Katalogen, und eine
    Datei zählt, wenn sie `id` **und** `type` trägt. Nicht auf das
    `_`-Präfix filtern — `_initiative.md` und `_epic.md` sind Item-Dateien.
    """
    items, paths, bodies = {}, {}, {}
    for path in sorted(root.glob("**/*.md")):
        if path.name in CATALOGUES:
            continue
        fm, body = frontmatter(path)
        rel = path.relative_to(root)
        if "id" not in fm and "type" not in fm:
            # README, Arbeitsnotizen — Dokumentation, keine Items.
            continue
        if "id" not in fm or "type" not in fm:
            err(f"{rel}: Item-Datei mit id oder type, aber nicht beidem"
                " — hier bricht build-import.py ab")
            continue
        iid = fm["id"]
        if iid in items:
            err(f"{rel}: `id` doppelt, auch in {paths[iid]}")
            continue
        items[iid], paths[iid], bodies[iid] = fm, rel, body
    return items, paths, bodies


def check_items(items, paths, bodies, releases, personas, tags) -> None:
    for iid, fm in items.items():
        p, typ = paths[iid], fm.get("type")

        if not UUID.match(iid):
            err(f"{p}: `id` ist keine UUID: {iid}")
        if typ not in TYPES:
            err(f"{p}: unbekannter `type`: {typ!r}")

        if not fm.get("title"):
            err(f"{p}: kein `title` — build-import.py scheitert daran")
        elif re.match(r"^(I|E|S|R)\d+[ .·\-]", fm["title"]):
            warn(f"{p}: `title` trägt eine Positionsnummer — die Reihenfolge"
                 " macht `order`, und eine Nummer im Titel veraltet beim"
                 " ersten Umsortieren")

        # --- Hierarchie
        parent = fm.get("parent")
        if typ in PARENT_OF and not parent:
            err(f"{p}: {typ} ohne `parent`")
        if typ in ROOTLESS and parent:
            err(f"{p}: {typ} darf keinen `parent` haben — {typ} steht auf"
                " Wurzelebene")
        if parent and parent not in items:
            err(f"{p}: `parent` löst nicht auf: {parent}")
        elif parent and typ in PARENT_OF:
            got = items[parent].get("type")
            if got not in PARENT_OF[typ]:
                err(f"{p}: {typ} hängt an {got}, erwartet"
                    f" {' oder '.join(sorted(PARENT_OF[typ]))}")

        # --- Kataloge. Ein unbekannter Schlüssel ist ein Abbruch im Generator
        # (release) oder eine verlorene Zuweisung (persona, tags).
        rel = fm.get("release")
        if rel and rel not in releases:
            err(f"{p}: `release` unbekannt: {rel}")
        for tag in as_list(fm.get("tags")):
            if tag not in tags:
                err(f"{p}: `tags`-Wert ohne Eintrag in `_tags.md`: {tag}"
                    " — er käme ungestylt an")

        if typ in ("story", "project", "dev"):
            persona = fm.get("persona")
            if not persona:
                warn(f"{p}: {typ} ohne `persona`")
            elif persona not in personas:
                err(f"{p}: `persona` unbekannt: {persona}")

            # ADR 0008: Template-Stories landen auf `idea`, mit voll
            # ausgearbeitetem Inhalt. Ein anderer Wert stellt die Karte beim
            # Import in die falsche Spalte.
            if fm.get("maturity") != "idea":
                err(f"{p}: `maturity` ist {fm.get('maturity')!r}, nicht `idea`"
                    " (ADR 0008)")
            if not fm.get("sources"):
                warn(f"{p}: {typ} ohne `sources` — eine Aussage ohne"
                     " Belegstelle ist eine Behauptung")

            # Zwei Formprüfungen am Rumpf. Inhaltliche Qualität ist Sache von
            # `betterplan-create-story`; *dass* die beiden Teile überhaupt da
            # sind, ist Form und hier billig zu sehen.
            body = (bodies.get(iid) or "").strip()
            if "## Akzeptanzkriterien" not in body:
                warn(f"{p}: {typ} ohne Abschnitt `## Akzeptanzkriterien`")
            first = next((l for l in body.splitlines() if l.strip()), "")
            if not first.startswith("Als "):
                warn(f"{p}: Rumpf beginnt nicht mit der Begünstigtenperspektive"
                     " (Als …, möchte ich …, damit …) — ADR 0004")

            prio = fm.get("priority")
            if prio and prio not in ("Should", "Could"):
                err(f"{p}: `priority` ist {prio!r} — getaggt werden nur die"
                    " Abweichungen von Must, also `Should` oder `Could`")
            elif prio and any(any(m in s for m in MUST_MARKERS)
                              for s in as_list(fm.get("sources"))):
                warn(f"{p}: `priority: {prio}`, aber die `sources` führen eine"
                     " MUSS-Anforderung — die stärkste Modalität gewinnt")
        else:
            # `sources` steht ausdrücklich **nicht** hier: ein Epic, das seine
            # Belegstelle nennt, ist gute Praxis und kein Befund. Beide
            # Vorläufer-Prüfer beschränkten nur `priority`, und das war richtig.
            for field in ("priority", "persona"):
                if fm.get(field):
                    warn(f"{p}: `{field}` gehört auf Stories, nicht auf {typ}")


def check_dependencies(items, paths) -> dict[str, list[str]]:
    """Auflösung, Selbstbezug, Zyklen. Gibt den geprüften Graphen zurück."""
    graph: dict[str, list[str]] = {}
    for iid, fm in items.items():
        graph[iid] = []
        for dep in as_list(fm.get("dependsOn")):
            if dep == iid:
                err(f"{paths[iid]}: `dependsOn` zeigt auf sich selbst")
            elif dep not in items:
                err(f"{paths[iid]}: `dependsOn` löst nicht auf: {dep}")
            else:
                graph[iid].append(dep)

    # Iterativ, nicht rekursiv: eine lange Kette in einem Pflichtenkatalog
    # erreicht die Rekursionsgrenze, und dann bricht der Prüfer ab, statt zu
    # prüfen. Weiß/grau/schwarz über einen expliziten Stapel.
    state: dict[str, int] = collections.defaultdict(int)
    for start in graph:
        if state[start]:
            continue
        stack = [(start, iter(graph[start]))]
        trail = [start]
        state[start] = 1
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                state[node] = 2
                stack.pop()
                trail.pop()
                continue
            if state[nxt] == 1:
                ring = trail[trail.index(nxt):] + [nxt]
                err("Abhängigkeitszyklus: "
                    + " → ".join(str(paths[n]) for n in ring))
                continue
            if state[nxt] == 0:
                state[nxt] = 1
                trail.append(nxt)
                stack.append((nxt, iter(graph[nxt])))
    return graph


def check_prose_refs(items, paths, bodies) -> int:
    """`[Titel](#id)` — löst auf, nicht auf sich selbst, Anzeigetext aktuell.

    Der Anzeigetext ist die eigentliche Falle. Veraltet er, bleibt der Verweis
    technisch gültig: der Leser bekommt den alten Titel zu sehen und folgt ihm
    zu einem Item, das inzwischen etwas anderes heißt.
    """
    total = 0
    for iid, body in bodies.items():
        for shown, target in PROSE_REF.findall(body):
            total += 1
            if target not in items:
                err(f"{paths[iid]}: Verweis löst nicht auf: [{shown}](#{target})")
            elif target == iid:
                err(f"{paths[iid]}: Verweis zeigt auf das eigene Item: {shown}")
            elif items[target].get("title") != shown:
                err(f"{paths[iid]}: Anzeigetext veraltet — {shown!r} statt"
                    f" {items[target].get('title')!r}")
            elif items[target].get("type") == "initiative":
                warn(f"{paths[iid]}: Verweis zeigt auf eine Initiative —"
                     " gemeint ist meist das Epic oder die Story darunter")
    return total


def check_completeness(items, paths) -> None:
    kids = collections.defaultdict(list)
    for iid, fm in items.items():
        if fm.get("parent") in items:
            kids[fm["parent"]].append(iid)

    for iid, fm in items.items():
        if fm.get("type") == "epic" and not kids[iid]:
            err(f"{paths[iid]}: Epic ohne Story")
        if fm.get("type") == "initiative" and not kids[iid]:
            err(f"{paths[iid]}: Initiative ohne Epic")

    # Geschwister mit gleichem `order`. Der Generator sortiert dann nach id,
    # also nach Zufall — und `displayOrder` kommt in einer Reihenfolge an, die
    # niemand gewählt hat. Fehlt `order` überall, ist das die Voreinstellung 0
    # und betrifft die ganze Gruppe.
    sib = collections.defaultdict(list)
    for iid, fm in items.items():
        sib[fm.get("parent", "__root__")].append(iid)
    for parent, group in sib.items():
        if len(group) < 2:
            continue
        orders = collections.Counter(
            str(items[i].get("order", "<fehlt>")) for i in group)
        dupes = {o: n for o, n in orders.items() if n > 1}
        if dupes:
            where = paths[parent] if parent in paths else "Wurzelebene"
            warn(f"{where}: {len(group)} Geschwister, aber `order`"
                 f" mehrfach belegt ({dupes}) — die Reihenfolge entscheidet"
                 " dann die id, nicht du")

    # Ein Epic ohne Release, dessen Stories *alle* dasselbe Release tragen.
    # Entweder fehlt es am Epic, oder die Stories sind Dauerarbeit und tragen
    # es zu Unrecht — beides sieht auf der Roadmap gleich aus. Tragen die
    # Stories verschiedene Releases, spannt das Epic über mehrere: zulässig.
    #
    # **Nur wenn die Map Releases überhaupt an Epics hängt.** Es gibt zwei
    # gültige Konventionen — Releases an den Epics, oder nur an den Stories —,
    # und welche gilt, sagt die Map selbst. Gemessen an zwei echten Maps: in
    # der einen tragen 21 von 26 Epics ein Release, in der anderen 0 von 40.
    # Ohne diese Bedingung meldet die Prüfung in der zweiten jedes Epic, und
    # eine Prüfung, die vierzig Mal dasselbe sagt, wird abgeschaltet.
    epics = [i for i, fm in items.items() if fm.get("type") == "epic"]
    if not any(items[i].get("release") for i in epics):
        return
    for iid, fm in items.items():
        if fm.get("type") != "epic" or fm.get("release"):
            continue
        shared = {items[k].get("release") for k in kids[iid]}
        if len(shared) == 1 and None not in shared:
            warn(f"{paths[iid]}: Epic ohne `release`, aber alle"
                 f" {len(kids[iid])} Stories tragen {shared.pop()!r} —"
                 " entweder fehlt es am Epic, oder die Stories behaupten,"
                 " unter einem Datum fertig zu sein")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", default=".", help="Projektroot (Default: .)")
    args = ap.parse_args()

    root = pathlib.Path(args.project).resolve() / ".betterplan" / "storymap"
    if not root.is_dir():
        print(f"❌ {root} nicht gefunden", file=sys.stderr)
        return 2

    items, paths, bodies = load(root)
    if not items:
        print(f"❌ keine Item-Dateien unter {root}", file=sys.stderr)
        return 2

    personas = catalogue(root / "_personas.md")
    releases = catalogue(root / "_releases.md")
    tags = catalogue(root / "_tags.md")

    for key, fields in releases.items():
        if "position" not in fields:
            err(f"_releases.md/{key}: `position` fehlt — Pflichtfeld, hier"
                " bricht build-import.py ab")
    for key, fields in tags.items():
        color = fields.get("color")
        if color not in PALETTE:
            err(f"_tags.md/{key}: `color` ist kein Palettenname: {color!r}"
                f" — erlaubt: {', '.join(sorted(PALETTE))}")

    check_items(items, paths, bodies, releases, personas, tags)
    graph = check_dependencies(items, paths)
    refs = check_prose_refs(items, paths, bodies)
    check_completeness(items, paths)

    # --- Bericht
    counts = collections.Counter(fm.get("type") for fm in items.values())
    print(f"{len(items)} Items — "
          + " · ".join(f"{v} {k}" for k, v in sorted(counts.items(), key=str)))
    print(f"{len(personas)} Personas · {len(releases)} Releases · "
          f"{len(tags)} Tags · {refs} Prosa-Verweise · "
          f"{sum(len(v) for v in graph.values())} Abhängigkeiten")

    moscow = collections.Counter(
        fm.get("priority", "Must") for fm in items.values()
        if fm.get("type") in ("story", "project", "dev"))
    if moscow:
        print("MoSCoW: " + " · ".join(f"{v} {k}"
                                      for k, v in sorted(moscow.items())))
        deviations = sum(v for k, v in moscow.items() if k != "Must")
        if 0 < deviations < 10:
            print(f"   Hinweis: nur {deviations} Abweichung(en) von Must."
                  " Unter rund zehn trägt der Filter nicht — lohnt das Tag?")

    for w in WARNINGS:
        print(f"⚠  {w}")
    for e in ERRORS:
        print(f"❌ {e}")

    if ERRORS:
        print(f"\n{len(ERRORS)} Fehler, {len(WARNINGS)} Hinweis(e)")
        return 1
    if WARNINGS:
        print(f"\nKeine Fehler, {len(WARNINGS)} Hinweis(e)")
        return 0
    print("\n✓ Map konsistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
