#!/usr/bin/env python3
"""Erzeugt aus einer Story Map die Nutzlast für `POST /projects/import`.

    python3 build-import.py --project <projektroot> --team <TEAM_ID>

Liest `<projektroot>/.betterplan/GOAL.md` und `<projektroot>/.betterplan/storymap/`,
schreibt `<projektroot>/.betterplan/import/projects-import.json` und
`nachtraege.json`. Beides ist **Generat** — ändert sich die Map, neu laufen
lassen; vorher das Prüfskript des Projekts.

Projektunabhängig. Was aus dem Projekt kommt, kommt aus seinen Dateien:

| Feld | Quelle |
|---|---|
| `title` | die `# Ziel: <name>`-Zeile aus `GOAL.md` |
| `settings.vision` | `goal:vision` (auf 200 Zeichen begrenzt, so viel nimmt das Feld) |
| `settings.description` | erster Absatz von `goal:purpose` |
| `settings.tagDefinitions` | `_tags.md`, sonst alles `slate` |
| `releases` | `_releases.md` |
| `tasks`, `dependencies` | die Item-Dateien |
| `team_id` | Argument — es gibt keinen sinnvollen Default |

Die Feldzuordnung ist gegen einen echten Datenstand belegt, nicht gegen das
Schema allein (2026-11-09):

  * ein Task hat `id` (UUID, **setzbar**) und `taskNumber` (nicht setzbar)
  * Task-Tags tragen `project:<wert>`, die `tagDefinitions` den nackten <wert>
  * `displayOrder` ist `{"storyboard": n}`, nullbasiert je Geschwistergruppe
  * Hierarchie entsteht rein aus `parentId`
  * `progress:*` bleibt weg, solange der Typ-Default passt
"""
from __future__ import annotations
import argparse, collections, json, pathlib, re, sys, uuid

PROSE_REF = re.compile(r"\[([^\]]+)\]\(#([0-9a-f-]{36})\)")
# Katalog- und Generatdateien. Alles andere unter storymap/ ist eine
# Item-Datei — auch `_initiative.md` und `_epic.md`, die ebenfalls mit `_`
# beginnen. Auf das Präfix zu filtern verschluckt den halben Backbone.
CATALOGUES = {"_personas.md", "_releases.md", "_tags.md", "_index.md"}
VISION_MAX = 200          # maxLength des Feldes
PALETTE = {"red", "orange", "amber", "yellow", "green", "teal", "blue",
           "indigo", "purple", "pink", "gray", "slate"}


def frontmatter(path: pathlib.Path) -> tuple[dict, str]:
    """Flache Schlüssel-Wert-Paare aus dem YAML-Kopf, plus den Body.

    Listen kommen in **beiden** YAML-Schreibweisen vor, und beide müssen hier
    als Liste ankommen: ein kurzer `tags: [PSIRT, Recht]` wird einzeilig
    geschrieben, ein langes `sources:` als Blockliste. Nur die Blockform zu
    lesen liefert für die Einzeiler eine **Zeichenkette**, und das fällt nicht
    auf, weil `[f"project:{t}" for t in "[a, b]"]` nicht scheitert, sondern je
    Zeichen einen Tag erzeugt.
    """
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        # Kein Frontmatter heißt keine Item-Datei — über die Folge entscheidet
        # der Aufrufer, nicht der Leser.
        return {}, text
    fm: dict = {}
    key = None
    for line in m.group(1).split("\n"):
        if line.startswith("  - ") and key:
            fm.setdefault(key, [])
            if not isinstance(fm[key], list):
                fm[key] = []
            fm[key].append(line[4:].strip())
        elif ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            key = k.strip()
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                fm[key] = [p.strip() for p in v[1:-1].split(",") if p.strip()]
            elif v:
                fm[key] = v
    return fm, m.group(2).strip()


FIELD_START = re.compile(r"^- \*\*(\w+):\*\*[ \t]?(.*)$")


def catalogue(path: pathlib.Path) -> dict[str, dict[str, str | None]]:
    """`## <schluessel>` plus `- **feld:**` je Eintrag.

    Ein `##`-Block ist ein Eintrag, **wenn er mindestens ein Feld hergibt** —
    Prosa-Abschnitte, mit denen eine Katalogdatei ihre Entscheidungen erklärt,
    tun das nicht. Am Schlüssel ist das nicht zu erkennen: Tag-Werte dürfen
    Leerzeichen enthalten (`Aufwand gering`), eine Überschrift mit Leerzeichen
    ist also kein Prosa-Indiz.

    **Ein Feldwert darf mehrzeiliges Markdown enthalten** — Listen, Absätze,
    Hervorhebungen. Die Zielfelder nehmen Markdown, und ein `features`-Feld mit
    fünf Punkten ist als Liste lesbar und als Satzkette nicht:

        - **features:**
          - Hostingmodell entschieden
          - TIA vorgelegt

    **Fortsetzungszeilen sind um zwei Leerzeichen eingerückt** und werden beim
    Lesen wieder ausgerückt; Leerzeilen innerhalb eines Wertes bleiben erhalten.
    Die Einrückung ist die Grenze: Die erste nicht eingerückte Zeile, die kein
    Feld beginnt, beendet den Feldblock — so darf hinter den Feldern ein
    Kommentar, eine Trennlinie oder ein Blockzitat stehen, ohne im letzten Wert
    zu landen.
    """
    if not path.exists():
        return {}
    out = {}
    for block in re.split(r"\n## ", path.read_text(encoding="utf-8"))[1:]:
        lines = block.split("\n")
        # Backticks um den Schlüssel sind Auszeichnung, nicht Teil des Namens:
        # `## \`integrator\`` liest sich im Katalog als Schlüssel und nicht als
        # Titel, und genau dafür schreibt man sie hin.
        key = lines[0].strip().strip("`").strip()
        fields: dict[str, list[str]] = {}
        current: str | None = None
        for line in lines[1:]:
            m = FIELD_START.match(line)
            if m:
                current = m.group(1)
                fields[current] = [m.group(2)]
            elif current is None:
                continue
            elif not line.strip():
                fields[current].append("")      # Leerzeile im Wert
            elif line.startswith("  "):
                fields[current].append(line[2:])
            else:
                current = None                  # unindentiert → Feldblock zu Ende
        clean: dict[str, str | None] = {}
        for name, buf in fields.items():
            v = "\n".join(buf).strip()
            clean[name] = None if v.startswith("*(leer)*") else (v or None)
        if clean:
            out[key] = clean
    return out


def goal_fields(goal: pathlib.Path) -> tuple[str, str, str]:
    if not goal.exists():
        sys.exit(f"❌ {goal} nicht gefunden")
    text = goal.read_text(encoding="utf-8")
    m = re.search(r"^# Ziel:\s*(.+)$", text, re.M)
    title = m.group(1).strip() if m else goal.parent.parent.name

    def section(anchor: str) -> str:
        m = re.search(rf"^## .*<!--\s*{anchor}\s*-->\s*\n(.*?)(?=^## |\Z)",
                      text, re.M | re.S)
        return m.group(1).strip() if m else ""

    def first_paragraph(anchor: str) -> str:
        """Der erste Absatz, auf eine Zeile zusammengezogen.

        **Nicht der ganze Abschnitt.** Unter `goal:vision` steht der Satz, und
        darunter oft ein Blockzitat mit dem, was an ihm noch offen ist. Nimmt
        man den Abschnitt ganz, landet die offene Frage im Vision-Feld — und
        weil das Feld bei 200 Zeichen endet, mitten im Wort.
        """
        text = section(anchor)
        return " ".join(text.split("\n\n")[0].split()) if text else ""

    vision = first_paragraph("goal:vision")[:VISION_MAX]
    description = first_paragraph("goal:purpose")
    return title, vision, description


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".", help="Projektroot (Default: .)")
    ap.add_argument("--team", required=True,
                    help="team_id für das neue Projekt; POST /projects/import "
                         "antwortet ohne sie mit 400")
    args = ap.parse_args()

    proj = pathlib.Path(args.project).resolve()
    bp = proj / ".betterplan"
    root = bp / "storymap"
    out = bp / "import"
    if not root.is_dir():
        sys.exit(f"❌ {root} nicht gefunden")
    out.mkdir(parents=True, exist_ok=True)

    title, vision, description = goal_fields(bp / "GOAL.md")

    # Nicht auf `_`-Präfix filtern: `_initiative.md` und `_epic.md` sind
    # Item-Dateien. Nur die Kataloge sind keine.
    items, bodies = {}, {}
    for p in sorted(root.glob("**/*.md")):
        if p.name in CATALOGUES:
            continue
        fm, body = frontmatter(p)
        # Im Map-Verzeichnis liegt auch Dokumentation — ein README, die
        # Arbeitsnotiz aus der Zielklärung. Was weder `id` noch `type` trägt,
        # ist keine Item-Datei; was nur eines von beiden trägt, ist eine
        # kaputte, und das ist ein Abbruch und kein Überspringen.
        if "id" not in fm and "type" not in fm:
            continue
        if "id" not in fm or "type" not in fm:
            sys.exit(f"❌ {p}: Item-Datei mit id oder type, aber nicht beidem")
        items[fm["id"]], bodies[fm["id"]] = fm, body
    if not items:
        sys.exit(f"❌ keine Item-Dateien unter {root}")
    titles = {i: fm["title"] for i, fm in items.items()}

    # --- Releases. Die ids sind reine Korrelationsschlüssel: der Import vergibt
    # jede UUID neu und remappt die Verweise, also genügt irgendeine.
    releases, rel_ids = [], {}
    for key, f in catalogue(root / "_releases.md").items():
        if "position" not in f:
            sys.exit(f"❌ _releases.md/{key}: position fehlt (Pflichtfeld)")
        rel_ids[key] = str(uuid.uuid4())
        releases.append({"id": rel_ids[key], "title": f.get("title") or key,
                         "position": int(f["position"]), "date": f.get("date"),
                         "dateLabel": f.get("dateLabel"), "goal": f.get("goal"),
                         "features": f.get("features"), "metrics": f.get("metrics"),
                         "status": f.get("status") or "planned"})
    releases.sort(key=lambda r: r["position"])

    # --- displayOrder: nullbasiert je Geschwistergruppe
    sib = collections.defaultdict(list)
    for iid, fm in items.items():
        sib[fm.get("parent", "__root__")].append((int(fm.get("order", 0)), iid))
    disp = {iid: n for kids in sib.values()
            for n, (_, iid) in enumerate(sorted(kids))}

    # --- Tasks
    tasks, nachtraege = [], []
    for iid, fm in items.items():
        body = bodies[iid]
        # Der Import vergibt die UUIDs neu — ein `[Titel](#uuid)` wäre danach
        # toter Zeiger. Also Klartext, und die Stelle vormerken.
        for shown, target in PROSE_REF.findall(body):
            nachtraege.append({"quelle": fm["title"],
                               "ziel": titles.get(target, "?"),
                               "anzeigetext": shown})
        body = PROSE_REF.sub(lambda m: f"„{m.group(1)}“", body)

        task = {"id": iid, "type": fm["type"], "title": fm["title"],
                "description": body, "displayOrder": {"storyboard": disp[iid]}}
        if fm.get("parent"):
            task["parentId"] = fm["parent"]
        if fm.get("tags"):
            task["tags"] = [f"project:{t}" for t in fm["tags"]]
        if fm.get("priority"):
            task["tags"] = task.get("tags", []) + [f"project:{fm['priority']}"]
        if fm.get("estimation"):
            task["estimation"] = int(fm["estimation"])
        if fm.get("release"):
            if fm["release"] not in rel_ids:
                sys.exit(f"❌ {fm['title']}: release {fm['release']!r} "
                         f"nicht in _releases.md")
            task["releaseId"] = rel_ids[fm["release"]]
        tasks.append(task)

    def depth(i: str) -> int:
        return 0 if not items[i].get("parent") else 1 + depth(items[i]["parent"])
    tasks.sort(key=lambda t: (depth(t["id"]), disp[t["id"]]))

    # --- Dependencies. `dependsOn: [B]` an A heißt „A wartet auf B", und
    # create_dependency erwartet sourceTaskId = das zuerst Fertige.
    dependencies = [{"sourceTaskId": dep, "targetTaskId": iid,
                     "dependencyType": "blocks"}
                    for iid, fm in items.items()
                    for dep in (fm.get("dependsOn") or [])]

    # --- tagDefinitions tragen den nackten Wert. Farben aus _tags.md, sonst slate.
    colors = {k: (f.get("color") or "slate")
              for k, f in catalogue(root / "_tags.md").items()}
    bad = {k: c for k, c in colors.items() if c not in PALETTE}
    if bad:
        sys.exit(f"❌ _tags.md: unbekannte Farbe(n) {bad} — erlaubt: "
                 f"{', '.join(sorted(PALETTE))}")
    used = sorted({t for fm in items.values() for t in (fm.get("tags") or [])}
                  | {fm["priority"] for fm in items.values() if fm.get("priority")})
    tagdefs = [{"name": t, "color": colors.get(t, "slate")} for t in used]
    undefined = [t for t in used if t not in colors]

    payload = {
        "team_id": args.team,
        "title": title,
        "settings": {"description": description, "vision": vision,
                     "tagDefinitions": tagdefs},
        "releases": releases,
        "tasks": tasks,
        "dependencies": dependencies,
    }

    # --- Personas. `TaskCreate` hat kein Persona-Feld und das Projektobjekt
    # keinen `personas`-Schlüssel: Personas sind eine eigene Ressource und
    # kommen über `assign_persona`, einen Aufruf je Paar. Nach dem Import sind
    # die Task-ids neu, also bindet der Plan über den **Titel** — er ist das
    # Einzige, was den Import überlebt.
    persona_cat = catalogue(root / "_personas.md")
    PERSONA_FIELDS = ("role", "goals", "wishes", "challenges",
                      "currentBehavior", "currentWorkaround", "notes")
    personas = []
    for key, f in persona_cat.items():
        if not f.get("name"):
            sys.exit(f"❌ _personas.md/{key}: name fehlt (Pflichtfeld, projektweit eindeutig)")
        personas.append({"_key": key, "name": f["name"],
                         **{k: f.get(k) or "" for k in PERSONA_FIELDS}})

    # Nur Initiative, Epic und User Story dürfen eine Persona nennen —
    # `assign_persona` sagt es selbst: „A Devteam Story, a Project Story and a
    # Workitem answer 400".
    #
    # Eine Project Story, die eine Persona nennt, ist deshalb **kein Fehler**:
    # die Persona steht dort für die Perspektive, aus der ihr Text geschrieben
    # ist, und die trägt der Text auch ohne Objekt am Task. Verloren geht die
    # Filterbarkeit, nicht die Aussage — also wird sie als nicht zuweisbar
    # ausgewiesen und nicht verschwiegen.
    ASSIGNABLE = {"initiative", "epic", "story"}
    assignments, unassignable, persona_errors = [], [], []
    for iid, fm in items.items():
        key = fm.get("persona")
        if not key:
            continue
        if key not in persona_cat:
            persona_errors.append(f"{fm['title']}: persona {key!r} nicht in _personas.md")
            continue
        entry = {"title": fm["title"], "type": fm["type"],
                 "persona": persona_cat[key]["name"], "personaKey": key}
        (assignments if fm["type"] in ASSIGNABLE else unassignable).append(entry)
    if persona_errors:
        sys.exit("❌ " + "\n❌ ".join(persona_errors))
    for group in (assignments, unassignable):
        group.sort(key=lambda a: (a["persona"], a["title"]))

    (out / "projects-import.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "nachtraege.json").write_text(
        json.dumps(nachtraege, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "personas.json").write_text(json.dumps(
        {"personas": personas, "assignments": assignments,
         "unassignable": unassignable},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    counts = collections.Counter(t["type"] for t in tasks)
    print(f"projects-import.json  {(out / 'projects-import.json').stat().st_size:,} Bytes")
    print(f"  title          {title}")
    print(f"  team_id        {args.team}")
    print(f"  tasks          {len(tasks)}  " +
          "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"  releases       {len(releases)}")
    print(f"  dependencies   {len(dependencies)}")
    print(f"  tagDefinitions {len(tagdefs)}" +
          (f"  ({', '.join(d['name'] for d in tagdefs)})" if tagdefs else ""))
    print(f"nachtraege.json       {len(nachtraege)} Prosa-Verweise")
    print(f"personas.json         {len(personas)} Personas, "
          f"{len(assignments)} Zuweisungen"
          + (f", {len(unassignable)} nicht zuweisbar" if unassignable else ""))
    ohne = [fm["title"] for fm in items.values()
            if fm["type"] == "story" and not fm.get("persona")]
    if ohne:
        print(f"⚠  {len(ohne)} Stor{'y' if len(ohne)==1 else 'ies'} ohne Persona: "
              + ", ".join(ohne[:3]) + (" …" if len(ohne) > 3 else ""))
    if undefined:
        print(f"⚠  ohne Farbe in _tags.md, auf slate gesetzt: {', '.join(undefined)}")
    if not vision:
        print("⚠  goal:vision ist leer — das Projekt kommt ohne Vision an")
    return 0


if __name__ == "__main__":
    sys.exit(main())
