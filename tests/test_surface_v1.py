"""The surface schema, checked against canonical cases.

A surface is a screen described as data that a host draws with its own
components. It usually comes from somewhere the host does not control — a
remote server panel, a companion, an app — so the cases that matter are the
ones that would make the host run, fetch or trust something: a node type it
has no component for, markup in text, an image or wallpaper by address, an SVG,
an action that carries a command, a nested value where a flat one is expected.

Every file under `tests/fixtures/surface-v1/valid` must validate and every file
under `.../invalid` must not. The file name is the reason.

Run with: python -m unittest discover -s tests.
"""

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "surface-v1.schema.json"
FIXTURES = ROOT / "tests/fixtures/surface-v1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class SurfaceV1SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load(SCHEMA_PATH)
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def test_the_published_copy_matches_the_one_the_scripts_use(self):
        self.assertEqual(load(SCHEMA_PATH), load(ROOT / "scripts/surface-v1.schema.json"))

    def test_it_is_not_an_app_manifest(self):
        self.assertEqual(self.schema["properties"]["surface"]["const"], 1)
        self.assertNotIn("schemaVersion", self.schema["properties"])
        self.assertFalse(set(self.schema["properties"]) & {"runtime", "capabilities", "data", "view"})

    def test_every_node_type_has_a_definition(self):
        """A type the dispatcher accepts without a definition behind it would
        validate with any fields at all."""
        types = self.schema["$defs"]["node"]["properties"]["type"]["enum"]
        dispatched = [rule["if"]["properties"]["type"]["const"] for rule in self.schema["$defs"]["node"]["allOf"]]
        self.assertEqual(sorted(types), sorted(dispatched))
        for name in types:
            with self.subTest(type=name):
                definition = self.schema["$defs"][name]
                self.assertEqual(definition["properties"]["type"]["const"], name)
                self.assertIs(definition["additionalProperties"], False)

    def test_a_window_only_lives_in_a_desktop(self):
        self.assertNotIn("window", self.schema["$defs"]["node"]["properties"]["type"]["enum"])

    def test_leaf_layouts_cover_the_desk_widget_layouts(self):
        """The desk's six widget layouts are the same drawings, so a host can
        reuse one component for both."""
        types = set(self.schema["$defs"]["node"]["properties"]["type"]["enum"])
        self.assertTrue({"stat", "progress", "list", "chart", "keyvalue"} <= types)

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

    def test_images_are_inline_only(self):
        pattern = self.schema["$defs"]["image"]["properties"]["src"]["pattern"]
        self.assertTrue(pattern.startswith("^data:image/(png|jpeg|webp);base64,"))


if __name__ == "__main__":
    unittest.main()
