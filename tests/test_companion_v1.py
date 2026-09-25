"""The companion registration schema, checked against canonical cases.

A companion is a desktop app on the same computer as Vela that registers itself
by writing a file into Vela's companions folder. Any program the user runs can
write there, so the cases that matter are the ones that would make Vela talk to
something other than this computer, read a file outside that folder, or accept
a declaration it cannot draw: a LAN or public endpoint, an icon path that
climbs out of the folder, an SVG icon, a guessable token, an action that
carries a command.

Every file under `tests/fixtures/companion-v1/valid` must validate and every
file under `.../invalid` must not. The file name is the reason.

Run with: python -m unittest discover -s tests.
"""

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "companion-v1.schema.json"
FIXTURES = ROOT / "tests/fixtures/companion-v1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class CompanionV1SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load(SCHEMA_PATH)
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def test_the_published_copy_matches_the_one_the_scripts_use(self):
        self.assertEqual(load(SCHEMA_PATH), load(ROOT / "scripts/companion-v1.schema.json"))

    def test_it_is_not_an_app_manifest(self):
        """A registration is not a package. It carries no runtime, capability
        or storage declaration a host could mistake for a manifest's."""
        self.assertEqual(self.schema["properties"]["companion"]["const"], 1)
        self.assertNotIn("schemaVersion", self.schema["properties"])
        self.assertFalse(set(self.schema["properties"]) & {"runtime", "capabilities", "data", "view"})

    def test_widgets_match_the_v2_declarations(self):
        """The desk draws a companion's widget with the same components, so the
        declaration has to be the same one."""
        v2 = load(ROOT / "manifest-v2.schema.json")["properties"]["widgets"]
        self.assertEqual(self.schema["properties"]["widgets"], v2)

    def test_every_valid_fixture_validates(self):
        found = sorted((FIXTURES / "valid").glob("*.json"))
        self.assertTrue(found, "no positive fixtures")
        for path in found:
            with self.subTest(fixture=path.name):
                errors = sorted(self.validator.iter_errors(load(path)), key=str)
                self.assertEqual(errors, [], f"{path.name}: {errors[:1]}")

    def test_every_invalid_fixture_is_refused(self):
        found = sorted((FIXTURES / "invalid").glob("*.json"))
        self.assertGreaterEqual(len(found), 20, "the negative set is the interesting one")
        for path in found:
            with self.subTest(fixture=path.name):
                self.assertTrue(
                    list(self.validator.iter_errors(load(path))),
                    f"{path.name} validated, so the schema no longer refuses it",
                )

    def test_the_endpoint_is_loopback_only(self):
        pattern = self.schema["properties"]["endpoint"]["pattern"]
        self.assertTrue(pattern.startswith("^http://(127"))
        self.assertIn("Loopback only", self.schema["properties"]["endpoint"]["description"])


if __name__ == "__main__":
    unittest.main()
