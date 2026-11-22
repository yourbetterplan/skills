"""Belegt, dass `check-map.py` findet, was es zu finden behauptet.

    cd betterplan-storymap/scripts && python3 -m unittest discover tests

**Standardbibliothek, kein pytest.** Die Skripte dieses Skills brauchen keine
Abhängigkeit, und ein `pyproject.toml` mit Dev-Dependency erzeugt ein `.venv` —
das wandert beim Installieren als Ballast in jedes Projekt, das das Skill zieht.

Jeder Test perturbiert **eine** Sache an der sauberen Map und erwartet **einen**
Befund. Aufgerufen wird das Skript als Unterprozess, nicht als Modul: so ist der
Exit-Code mitgeprüft, und die Sammellisten `ERRORS`/`WARNINGS` können sich nicht
zwischen zwei Tests vererben.
"""
from __future__ import annotations
import pathlib
import subprocess
import sys
import tempfile
import unittest

import _fixture as fx

CHECK = pathlib.Path(__file__).resolve().parent.parent / "check-map.py"


class MapCase(unittest.TestCase):
    """Schreibt die saubere Map neu und stellt `run()` bereit."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = fx.write(pathlib.Path(self._tmp.name))
        self.sm = self.root / ".betterplan" / "storymap"
        self.addCleanup(self._tmp.cleanup)

    def run_check(self) -> tuple[int, str]:
        p = subprocess.run([sys.executable, str(CHECK), "--project", str(self.root)],
                           capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def assertFinding(self, needle: str, *, exit_code: int = 1) -> str:
        code, out = self.run_check()
        self.assertIn(needle, out, f"Befund fehlt.\nAusgabe:\n{out}")
        self.assertEqual(code, exit_code, f"falscher Exit-Code.\nAusgabe:\n{out}")
        return out

    def story(self) -> pathlib.Path:
        return self.sm / "01-eins" / "01-epic" / "01-story.md"


class TestCleanMap(MapCase):
    """Der Ausgangszustand muss befundfrei sein, sonst sagen die anderen nichts."""

    def test_clean_map_has_no_findings_at_all(self):
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("Map konsistent", out)
        self.assertNotIn("⚠", out)
        self.assertNotIn("❌", out)

    def test_counts_are_reported(self):
        _, out = self.run_check()
        self.assertIn("4 Items", out)
        self.assertIn("1 Personas", out)
        self.assertIn("1 Releases", out)

    def test_documentation_without_id_and_type_is_skipped(self):
        # README.md liegt in der Map und ist kein Item. Würde es als eines
        # gezählt, wären es fünf.
        _, out = self.run_check()
        self.assertIn("4 Items", out)


class TestIdentity(MapCase):
    def test_id_must_be_a_uuid(self):
        self.story().write_text(
            fx.item("keine-uuid", "story", "Kaufen können", parent=fx.EPIC,
                    maturity="idea", persona="kundin", order=1,
                    sources=["L §1"]), encoding="utf-8")
        self.assertFinding("`id` ist keine UUID")

    def test_duplicate_id_names_the_other_file(self):
        (self.sm / "_querschnitt" / "02-doppelt.md").write_text(
            fx.item(fx.PROJECT, "project", "Zwilling", order=2, maturity="idea",
                    persona="kundin", sources=["L §3"]), encoding="utf-8")
        out = self.assertFinding("`id` doppelt")
        self.assertIn("01-quer.md", out)

    def test_item_file_with_type_but_no_id_is_an_error(self):
        (self.sm / "_querschnitt" / "03-halb.md").write_text(
            "---\ntype: project\ntitle: Halb\n---\nRumpf.\n", encoding="utf-8")
        self.assertFinding("id oder type, aber nicht beidem")

    def test_missing_title_is_an_error(self):
        self.story().write_text(
            "---\nid: " + fx.STORY + "\ntype: story\nparent: " + fx.EPIC
            + "\nmaturity: idea\npersona: kundin\n---\nAls Kundin …\n",
            encoding="utf-8")
        self.assertFinding("kein `title`")


class TestHierarchy(MapCase):
    def test_story_without_parent(self):
        self.story().write_text(
            fx.item(fx.STORY, "story", "Kaufen können", maturity="idea",
                    persona="kundin", order=1, sources=["L §1"]),
            encoding="utf-8")
        self.assertFinding("story ohne `parent`")

    def test_project_story_must_not_carry_a_parent(self):
        (self.sm / "_querschnitt" / "01-quer.md").write_text(
            fx.item(fx.PROJECT, "project", "Querschnittlich", parent=fx.EPIC,
                    order=1, maturity="idea", persona="kundin",
                    sources=["L §2"]), encoding="utf-8")
        self.assertFinding("project darf keinen `parent` haben")

    def test_unresolvable_parent(self):
        self.story().write_text(
            fx.item(fx.STORY, "story", "Kaufen können",
                    parent="99999999-9999-4999-8999-999999999999",
                    maturity="idea", persona="kundin", order=1,
                    sources=["L §1"]), encoding="utf-8")
        self.assertFinding("`parent` löst nicht auf")

    def test_wrong_parent_type_is_caught(self):
        """Eine Story unter einer Initiative — der Fund, den beide Vorgänger
        nur zur Hälfte hatten: `parent` löst auf, der Typ ist trotzdem falsch."""
        self.story().write_text(
            fx.item(fx.STORY, "story", "Kaufen können", parent=fx.INIT,
                    maturity="idea", persona="kundin", order=1,
                    sources=["L §1"]), encoding="utf-8")
        self.assertFinding("story hängt an initiative, erwartet epic")

    def test_epic_without_story(self):
        self.story().unlink()
        self.assertFinding("Epic ohne Story")

    def test_initiative_without_epic(self):
        self.story().unlink()
        (self.sm / "01-eins" / "01-epic" / "_epic.md").unlink()
        self.assertFinding("Initiative ohne Epic")

    def test_unknown_type(self):
        self.story().write_text(
            fx.item(fx.STORY, "saga", "Kaufen können", parent=fx.EPIC,
                    maturity="idea", persona="kundin", order=1,
                    sources=["L §1"]), encoding="utf-8")
        self.assertFinding("unbekannter `type`")


class TestCatalogues(MapCase):
    def test_unknown_persona(self):
        self._rewrite_story(persona="niemand")
        self.assertFinding("`persona` unbekannt: niemand")

    def test_unknown_release(self):
        self._rewrite_story(release="r9")
        self.assertFinding("`release` unbekannt: r9")

    def test_unknown_tag_value(self):
        self._rewrite_story(tags="[Unbekannt]")
        self.assertFinding("`tags`-Wert ohne Eintrag in `_tags.md`")

    def test_colour_outside_the_palette(self):
        (self.sm / "_tags.md").write_text(
            "# Tags\n\n## Could\n\n- **color:** neongelb\n", encoding="utf-8")
        self.assertFinding("ist kein Palettenname")

    def test_release_without_position(self):
        (self.sm / "_releases.md").write_text(
            "# Releases\n\n## r1\n\n- **title:** Erstes\n", encoding="utf-8")
        self.assertFinding("`position` fehlt")

    def test_catalogue_starting_with_a_heading_is_read(self):
        """Regression: `catalogue()` trennte auf `\\n## ` und verlor damit jeden
        Eintrag, wenn die Datei direkt mit `## ` beginnt. Bei `_personas.md`
        lautlos — die Persona galt dann als unbekannt."""
        (self.sm / "_personas.md").write_text(
            "## kundin\n\n- **name:** Kundin\n", encoding="utf-8")
        code, out = self.run_check()
        self.assertIn("1 Personas", out)
        self.assertNotIn("`persona` unbekannt", out)
        self.assertEqual(code, 0, out)

    def _rewrite_story(self, **override):
        fields = dict(maturity="idea", persona="kundin", release="r1", order=1,
                      sources=["L §1"])
        fields.update(override)
        self.story().write_text(
            fx.item(fx.STORY, "story", "Kaufen können", parent=fx.EPIC, **fields),
            encoding="utf-8")


class TestDependencies(MapCase):
    def test_self_dependency(self):
        self._depends(fx.STORY)
        self.assertFinding("`dependsOn` zeigt auf sich selbst")

    def test_unresolvable_dependency(self):
        self._depends("99999999-9999-4999-8999-999999999999")
        self.assertFinding("`dependsOn` löst nicht auf")

    def test_cycle_is_reported(self):
        self._depends(fx.PROJECT)
        (self.sm / "_querschnitt" / "01-quer.md").write_text(
            fx.item(fx.PROJECT, "project", "Querschnittlich", order=1,
                    maturity="idea", persona="kundin", sources=["L §2"],
                    dependsOn=[fx.STORY]), encoding="utf-8")
        self.assertFinding("Abhängigkeitszyklus")

    def test_a_long_chain_does_not_exhaust_the_recursion_limit(self):
        """Regression für die iterative Zyklensuche. Beide Vorgänger
        rekursierten; eine Kette echter Vorbedingungen aus einem
        Pflichtenkatalog wird länger als `sys.getrecursionlimit()`, und dann
        bricht der Prüfer ab, statt zu prüfen."""
        quer = self.sm / "_querschnitt"
        n = 1200
        self.assertGreater(n, sys.getrecursionlimit(),
                           "Die Kette muss die Rekursionsgrenze überschreiten,"
                           " sonst belegt der Test nichts.")
        previous = None
        for i in range(n):
            iid = f"5{i:07d}-0000-4000-8000-000000000000"
            quer.joinpath(f"{i + 10:04d}-kette.md").write_text(
                fx.item(iid, "project", f"Kette {i}", order=i + 10,
                        maturity="idea", persona="kundin", sources=["L §9"],
                        dependsOn=[previous] if previous else None),
                encoding="utf-8")
            previous = iid
        code, out = self.run_check()
        self.assertNotIn("RecursionError", out)
        self.assertNotIn("Abhängigkeitszyklus", out)
        self.assertEqual(code, 0, out[:2000])
        self.assertIn(f"{n - 1} Abhängigkeiten", out)

    def _depends(self, target: str):
        self.story().write_text(
            fx.item(fx.STORY, "story", "Kaufen können", parent=fx.EPIC,
                    maturity="idea", persona="kundin", release="r1", order=1,
                    sources=["L §1"], dependsOn=[target]), encoding="utf-8")


class TestProseReferences(MapCase):
    def test_unresolvable_reference(self):
        self._body("Siehe [Irgendwas](#99999999-9999-4999-8999-999999999999).")
        self.assertFinding("Verweis löst nicht auf")

    def test_reference_to_itself(self):
        self._body(f"Siehe [Kaufen können](#{fx.STORY}).")
        self.assertFinding("Verweis zeigt auf das eigene Item")

    def test_stale_display_text(self):
        """Die eigentliche Falle: der Verweis bleibt gültig, der Leser bekommt
        einen Titel zu sehen, den das Ziel nicht mehr trägt."""
        self._body(f"Siehe [Alter Titel](#{fx.EPIC}).")
        out = self.assertFinding("Anzeigetext veraltet")
        self.assertIn("'Epic'", out)

    def test_matching_display_text_is_clean(self):
        self._body(f"Siehe [Epic](#{fx.EPIC}).")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("1 Prosa-Verweise", out)

    def _body(self, extra: str):
        body = ("Als Kundin möchte ich kaufen können, damit es belegt ist.\n\n"
                f"{extra}\n\n## Akzeptanzkriterien\n\n- [ ] Es ist belegt.\n")
        self.story().write_text(
            fx.item(fx.STORY, "story", "Kaufen können", parent=fx.EPIC,
                    maturity="idea", persona="kundin", release="r1", order=1,
                    sources=["L §1"], body=body), encoding="utf-8")


class TestStoryShape(MapCase):
    def test_maturity_must_be_idea(self):
        self.story().write_text(
            fx.item(fx.STORY, "story", "Kaufen können", parent=fx.EPIC,
                    maturity="ready", persona="kundin", order=1,
                    sources=["L §1"]), encoding="utf-8")
        self.assertFinding("nicht `idea`")

    def test_priority_must_be_a_deviation_from_must(self):
        self.story().write_text(
            fx.item(fx.STORY, "story", "Kaufen können", parent=fx.EPIC,
                    maturity="idea", persona="kundin", order=1, priority="Must",
                    sources=["L §1"]), encoding="utf-8")
        self.assertFinding("getaggt werden nur die Abweichungen von Must")

    def test_priority_contradicting_a_must_requirement_is_a_hint(self):
        self.story().write_text(
            fx.item(fx.STORY, "story", "Kaufen können", parent=fx.EPIC,
                    maturity="idea", persona="kundin", order=1,
                    priority="Could", tags="[Could]",
                    sources=["L §1: Der Hersteller MUSS liefern"]),
            encoding="utf-8")
        out = self.assertFinding("die stärkste Modalität gewinnt", exit_code=0)
        self.assertIn("⚠", out)

    def test_missing_acceptance_criteria_is_a_hint(self):
        self._body("Als Kundin möchte ich kaufen können, damit es belegt ist.\n")
        self.assertFinding("ohne Abschnitt `## Akzeptanzkriterien`", exit_code=0)

    def test_body_without_the_beneficiary_perspective_is_a_hint(self):
        self._body("Es soll gekauft werden können.\n\n"
                   "## Akzeptanzkriterien\n\n- [ ] Es ist belegt.\n")
        self.assertFinding("Begünstigtenperspektive", exit_code=0)

    def test_missing_sources_is_a_hint(self):
        self.story().write_text(
            fx.item(fx.STORY, "story", "Kaufen können", parent=fx.EPIC,
                    maturity="idea", persona="kundin", order=1),
            encoding="utf-8")
        self.assertFinding("ohne `sources`", exit_code=0)

    def test_sources_on_an_epic_is_not_a_finding(self):
        """Gemessen an zwei echten Maps: 56 Epics tragen `sources` mit Absicht.
        Ein Epic, das seine Belegstelle nennt, ist gute Praxis."""
        (self.sm / "01-eins" / "01-epic" / "_epic.md").write_text(
            fx.item(fx.EPIC, "epic", "Epic", parent=fx.INIT, order=1,
                    sources=["L §1"], body="Das erste Epic.\n"),
            encoding="utf-8")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertNotIn("sources", out)

    def _body(self, body: str):
        self.story().write_text(
            fx.item(fx.STORY, "story", "Kaufen können", parent=fx.EPIC,
                    maturity="idea", persona="kundin", release="r1", order=1,
                    sources=["L §1"], body=body), encoding="utf-8")


class TestOrderAndReleases(MapCase):
    def test_siblings_sharing_an_order_are_a_hint(self):
        """Der Befund, den keiner der beiden Vorgänger hatte: der Generator
        sortiert bei gleichem `order` nach id, also nach Zufall."""
        (self.sm / "_querschnitt" / "02-zweit.md").write_text(
            fx.item("66666666-6666-4666-8666-666666666666", "project",
                    "Zweite", order=1, maturity="idea", persona="kundin",
                    sources=["L §4"]), encoding="utf-8")
        self.assertFinding("`order` mehrfach belegt", exit_code=0)

    def test_epic_without_release_is_silent_when_no_epic_has_one(self):
        """Zwei gültige Konventionen, und welche gilt, sagt die Map. In einer
        Map ohne Release an irgendeinem Epic ist das kein Befund — sonst meldet
        die Prüfung jedes Epic und wird abgeschaltet."""
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertNotIn("Epic ohne `release`", out)

    def test_epic_without_release_is_a_hint_once_another_epic_has_one(self):
        (self.sm / "01-eins" / "02-zweites").mkdir()
        other = "77777777-7777-4777-8777-777777777777"
        (self.sm / "01-eins" / "02-zweites" / "_epic.md").write_text(
            fx.item(other, "epic", "Zweites Epic", parent=fx.INIT, order=2,
                    release="r1", body="Trägt ein Release.\n"), encoding="utf-8")
        (self.sm / "01-eins" / "02-zweites" / "01-story.md").write_text(
            fx.item("88888888-8888-4888-8888-888888888888", "story",
                    "Auch kaufen", parent=other, order=1, maturity="idea",
                    persona="kundin", release="r1", sources=["L §5"]),
            encoding="utf-8")
        self.assertFinding("Epic ohne `release`", exit_code=0)


class TestExitCodes(MapCase):
    def test_missing_map_is_exit_2(self):
        p = subprocess.run([sys.executable, str(CHECK), "--project", "/nirgendwo"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)

    def test_hints_alone_do_not_fail(self):
        self.story().write_text(
            fx.item(fx.STORY, "story", "Kaufen können", parent=fx.EPIC,
                    maturity="idea", persona="kundin", order=1),
            encoding="utf-8")
        code, out = self.run_check()
        self.assertEqual(code, 0)
        self.assertIn("Keine Fehler", out)


if __name__ == "__main__":
    unittest.main()
