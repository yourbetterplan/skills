"""Nagelt die Zusagen von `build-import.py` fest, die der Docstring macht.

    cd betterplan-storymap/scripts && python3 -m unittest discover tests

Die reinen Funktionen werden importiert und direkt geprüft; die Nutzlast einmal
über einen echten Lauf. Geprüft wird vor allem, was **lautlos** falsch werden
kann: eine Liste, die als Zeichenkette ankommt, eine Richtung, die sich dreht,
ein Feldwert, der im Nachbarfeld landet.
"""
from __future__ import annotations
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

import _fixture as fx

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
BUILD = SCRIPTS / "build-import.py"

_spec = importlib.util.spec_from_file_location("build_import", BUILD)
bi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bi)

TEAM = "99999999-9999-4999-8999-999999999999"


class TempFile(unittest.TestCase):
    def write(self, text: str) -> pathlib.Path:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                          encoding="utf-8")
        tmp.write(text)
        tmp.close()
        path = pathlib.Path(tmp.name)
        self.addCleanup(path.unlink)
        return path


class TestFrontmatter(TempFile):
    def test_inline_list_arrives_as_a_list(self):
        """Der dokumentierte Fallstrick. Käme `[PSIRT, Recht]` als Zeichenkette
        an, erzeugte `[f"project:{t}" for t in wert]` je **Zeichen** einen Tag —
        das scheitert nicht, es produziert Unsinn."""
        fm, _ = bi.frontmatter(self.write(
            "---\nid: x\ntags: [PSIRT, Recht]\n---\nRumpf\n"))
        self.assertEqual(fm["tags"], ["PSIRT", "Recht"])

    def test_block_list_arrives_as_a_list(self):
        fm, _ = bi.frontmatter(self.write(
            "---\nid: x\nsources:\n  - L §1\n  - L §2\n---\nRumpf\n"))
        self.assertEqual(fm["sources"], ["L §1", "L §2"])

    def test_both_list_forms_agree(self):
        inline, _ = bi.frontmatter(self.write("---\nt: [a, b]\n---\n\n"))
        block, _ = bi.frontmatter(self.write("---\nt:\n  - a\n  - b\n---\n\n"))
        self.assertEqual(inline["t"], block["t"])

    def test_body_is_returned_stripped(self):
        _, body = bi.frontmatter(self.write("---\nid: x\n---\n\nRumpf\n\n"))
        self.assertEqual(body, "Rumpf")

    def test_file_without_frontmatter_yields_no_fields(self):
        fm, body = bi.frontmatter(self.write("# Nur Prosa\n"))
        self.assertEqual(fm, {})
        self.assertIn("Nur Prosa", body)


class TestCatalogue(TempFile):
    def test_multiline_value_keeps_its_markdown(self):
        entries = bi.catalogue(self.write(
            "# Releases\n\n## r1\n\n- **title:** Erstes\n- **goal:**\n"
            "  Erster Absatz.\n\n  Zweiter Absatz.\n- **position:** 1\n"))
        self.assertEqual(entries["r1"]["goal"],
                         "Erster Absatz.\n\nZweiter Absatz.")
        self.assertEqual(entries["r1"]["position"], "1")

    def test_list_inside_a_field_survives(self):
        entries = bi.catalogue(self.write(
            "# R\n\n## r1\n\n- **features:**\n  - Eins\n  - Zwei\n"))
        self.assertEqual(entries["r1"]["features"], "- Eins\n- Zwei")

    def test_comment_after_the_fields_lands_in_no_value(self):
        """Die erste nicht eingerückte Zeile, die kein Feld beginnt, beendet den
        Feldblock — sonst zieht der letzte Wert den Kommentar mit hinein."""
        entries = bi.catalogue(self.write(
            "# R\n\n## r1\n\n- **title:** Erstes\n\n"
            "> *Kommentar:* steht außerhalb.\n"))
        self.assertEqual(entries["r1"]["title"], "Erstes")
        self.assertNotIn("Kommentar", json.dumps(entries, ensure_ascii=False))

    def test_backticks_around_the_key_are_markup(self):
        entries = bi.catalogue(self.write(
            "# P\n\n## `integrator`\n\n- **name:** Integrator\n"))
        self.assertIn("integrator", entries)

    def test_prose_section_without_fields_is_not_an_entry(self):
        entries = bi.catalogue(self.write(
            "# P\n\n## Warum diese Personas\n\nWeil wir sie brauchen.\n\n"
            "## kundin\n\n- **name:** Kundin\n"))
        self.assertEqual(list(entries), ["kundin"])

    def test_key_may_contain_spaces(self):
        """Tag-Werte dürfen Leerzeichen tragen (`Aufwand gering`), eine
        Überschrift mit Leerzeichen ist also kein Prosa-Indiz."""
        entries = bi.catalogue(self.write(
            "# T\n\n## Aufwand gering\n\n- **color:** green\n"))
        self.assertEqual(entries["Aufwand gering"]["color"], "green")

    def test_heading_in_the_very_first_line_is_an_entry(self):
        """Regression: getrennt wurde auf `\\n## `, womit eine Datei ohne
        Vorlauf **keinen** Treffer hatte und als leer gelesen wurde."""
        entries = bi.catalogue(self.write("## kundin\n\n- **name:** Kundin\n"))
        self.assertEqual(list(entries), ["kundin"])

    def test_missing_file_is_empty_not_an_error(self):
        self.assertEqual(bi.catalogue(pathlib.Path("/nirgendwo/_tags.md")), {})


class TestGoalFields(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = fx.write(pathlib.Path(self._tmp.name))
        self.addCleanup(self._tmp.cleanup)

    def test_title_comes_from_the_goal_line(self):
        title, _, _ = bi.goal_fields(self.root / ".betterplan" / "GOAL.md")
        self.assertEqual(title, "Testvorhaben")

    def test_vision_is_the_first_paragraph_only(self):
        """Unter der Vision steht oft ein Blockzitat mit dem, was an ihr offen
        ist. Nimmt man den Abschnitt ganz, landet die offene Frage im Feld —
        und weil es bei 200 Zeichen endet, mitten im Wort."""
        _, vision, _ = bi.goal_fields(self.root / ".betterplan" / "GOAL.md")
        self.assertEqual(vision, "Das Vorhaben liefert eine prüfbare Map.")
        self.assertNotIn("Offen ist", vision)

    def test_vision_is_capped_at_the_field_length(self):
        goal = self.root / ".betterplan" / "GOAL.md"
        goal.write_text("# Ziel: X\n\n## V <!-- goal:vision -->\n\n"
                        + "wort " * 100, encoding="utf-8")
        _, vision, _ = bi.goal_fields(goal)
        self.assertLessEqual(len(vision), bi.VISION_MAX)


class TestPayload(unittest.TestCase):
    """Ein echter Lauf über die Fixture-Map."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = fx.write(pathlib.Path(cls._tmp.name))
        p = subprocess.run([sys.executable, str(BUILD), "--project", str(cls.root),
                            "--team", TEAM], capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        out = cls.root / ".betterplan" / "import"
        cls.payload = json.loads((out / "projects-import.json").read_text())
        cls.personas = json.loads((out / "personas.json").read_text())
        cls.nachtraege = json.loads((out / "nachtraege.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def task(self, title: str) -> dict:
        return next(t for t in self.payload["tasks"] if t["title"] == title)

    def test_team_id_is_carried_in_snake_case(self):
        self.assertEqual(self.payload["team_id"], TEAM)

    def test_every_item_becomes_a_task(self):
        self.assertEqual(len(self.payload["tasks"]), 4)

    def test_hierarchy_is_built_from_parent_ids(self):
        self.assertEqual(self.task("Kaufen können")["parentId"], fx.EPIC)
        self.assertEqual(self.task("Epic")["parentId"], fx.INIT)
        self.assertNotIn("parentId", self.task("Querschnittlich"))

    def test_display_order_is_zero_based_per_sibling_group(self):
        """Wurzelebene zählt als **eine** Gruppe: Initiative und Project Story
        teilen sie, also 0 und 1."""
        root = sorted(t["displayOrder"]["storyboard"] for t in self.payload["tasks"]
                      if not t.get("parentId"))
        self.assertEqual(root, [0, 1])
        self.assertEqual(self.task("Epic")["displayOrder"]["storyboard"], 0)

    def test_progress_tag_is_left_out(self):
        """Der Server setzt den Typ-Default. Ein pauschales `progress:idea`
        stellte Workitems in die falsche Spalte."""
        for t in self.payload["tasks"]:
            self.assertFalse([x for x in t.get("tags", []) if x.startswith("progress:")],
                             f'{t["title"]} trägt einen progress-Tag')

    def test_release_is_resolved_to_an_id(self):
        rid = self.payload["releases"][0]["id"]
        self.assertEqual(self.task("Kaufen können")["releaseId"], rid)
        self.assertEqual(self.payload["releases"][0]["position"], 1)

    def test_tag_definitions_carry_the_bare_value(self):
        """Am Task steht `project:<wert>`, in den Definitionen der nackte Wert —
        die Asymmetrie, die kein Schema ausdrückt."""
        names = {d["name"] for d in self.payload["settings"]["tagDefinitions"]}
        for name in names:
            self.assertFalse(name.startswith("project:"), name)

    def test_vision_and_description_reach_the_settings(self):
        self.assertEqual(self.payload["settings"]["vision"],
                         "Das Vorhaben liefert eine prüfbare Map.")
        self.assertEqual(self.payload["settings"]["description"],
                         "Damit die Prüfung belegt ist.")

    def test_personas_travel_beside_the_payload_not_inside_it(self):
        """Der Import trägt keine Personas — sie sind eine eigene Ressource."""
        self.assertNotIn("personas", self.payload)
        self.assertEqual(len(self.personas["personas"]), 1)
        self.assertEqual(self.personas["personas"][0]["name"], "Kundin")


class TestDependencyDirection(unittest.TestCase):
    def test_depends_on_becomes_source_equals_the_blocker(self):
        """`dependsOn: [B]` an A heißt „A wartet auf B", und
        `create_dependency` erwartet `sourceTaskId` = das zuerst Fertige.
        Verdreht importiert läuft der kritische Pfad rückwärts, und **nichts
        schlägt fehl** — deshalb steht die Richtung in einem Test."""
        with tempfile.TemporaryDirectory() as tmp:
            root = fx.write(pathlib.Path(tmp))
            sm = root / ".betterplan" / "storymap"
            (sm / "01-eins" / "01-epic" / "01-story.md").write_text(
                fx.item(fx.STORY, "story", "Kaufen können", parent=fx.EPIC,
                        maturity="idea", persona="kundin", order=1,
                        sources=["L §1"], dependsOn=[fx.PROJECT]),
                encoding="utf-8")
            p = subprocess.run([sys.executable, str(BUILD), "--project", str(root),
                                "--team", TEAM], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            deps = json.loads(
                (root / ".betterplan" / "import" / "projects-import.json")
                .read_text())["dependencies"]
        self.assertEqual(deps, [{"sourceTaskId": fx.PROJECT,
                                 "targetTaskId": fx.STORY,
                                 "dependencyType": "blocks"}])


class TestAborts(unittest.TestCase):
    def run_build(self, root: pathlib.Path) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(BUILD), "--project", str(root),
                               "--team", TEAM], capture_output=True, text=True)

    def test_item_file_with_type_but_no_id_aborts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fx.write(pathlib.Path(tmp))
            (root / ".betterplan" / "storymap" / "_querschnitt" / "02-halb.md"
             ).write_text("---\ntype: project\ntitle: Halb\n---\nRumpf.\n",
                          encoding="utf-8")
            p = self.run_build(root)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("id oder type", p.stdout + p.stderr)

    def test_colour_outside_the_palette_aborts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fx.write(pathlib.Path(tmp))
            (root / ".betterplan" / "storymap" / "_tags.md").write_text(
                "# T\n\n## Could\n\n- **color:** neongelb\n", encoding="utf-8")
            p = self.run_build(root)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("neongelb", p.stdout + p.stderr)

    def test_release_without_position_aborts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fx.write(pathlib.Path(tmp))
            (root / ".betterplan" / "storymap" / "_releases.md").write_text(
                "# R\n\n## r1\n\n- **title:** Erstes\n", encoding="utf-8")
            p = self.run_build(root)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("position", p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
