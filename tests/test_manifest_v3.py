"""The managed-web-app manifest schema, checked against canonical cases.

A managed web app is an existing self-hosted web server that a host installs,
runs as a local native service and publishes on its own web address. The schema
is the boundary between a package author and a host, so the cases that matter
are the ones a careless or hostile package would try: a combined POSIX target
that hides which binary runs, an archive without a digest, a data directory
that points at somebody's Documents folder, an install hook, or a manifest that
claims the SDK bridge it is not entitled to.

Every file under `tests/fixtures/manifest-v3/valid` must validate and every file
under `.../invalid` must not. The file name is the reason, so a fixture that
starts passing names what stopped being rejected.

Run with: python -m unittest discover -s tests.
"""

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "manifest-v3.schema.json"
FIXTURES = ROOT / "tests/fixtures/manifest-v3"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class ManifestV3SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load(SCHEMA_PATH)
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def test_the_published_copy_matches_the_one_the_scripts_use(self):
        """`scripts/` carries its own copy so the checks run from a checkout."""
        self.assertEqual(load(SCHEMA_PATH), load(ROOT / "scripts/manifest-v3.schema.json"))

    def test_it_is_a_separate_version_from_v2(self):
        """v1 and v2 keep their meaning: a v3 host feature cannot be smuggled
        into an app an older host already accepts."""
        self.assertEqual(self.schema["properties"]["schemaVersion"]["const"], 3)
        v2 = load(ROOT / "manifest-v2.schema.json")
        self.assertEqual(v2["properties"]["schemaVersion"]["const"], 2)
        self.assertFalse(set(self.schema["properties"]) & {"runtime", "capabilities", "widgets"})

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

    def test_native_trust_is_the_only_accepted_word(self):
        """A package cannot describe itself as confined. The host runs the
        executable with the user's own operating-system permissions and the
        install review has to be able to say so."""
        trust = self.schema["properties"]["service"]["properties"]["trust"]
        self.assertEqual(trust["const"], "trusted-native")
        self.assertIn("not a sandbox", trust["description"])

    def test_artifacts_separate_operating_system_from_architecture(self):
        artifact = self.schema["$defs"]["artifact"]
        self.assertEqual(set(artifact["properties"]["os"]["enum"]), {"windows", "macos", "linux"})
        self.assertEqual(set(artifact["properties"]["arch"]["enum"]), {"x64", "arm64", "armv7"})
        self.assertIn("os", artifact["required"])
        self.assertIn("arch", artifact["required"])
        self.assertIn("sha256", artifact["required"])
        self.assertIn("size", artifact["required"])

    def test_integration_flags_can_only_say_no(self):
        """They exist so a package cannot imply an SDK or agent grant it never
        receives, not so it can ask for one."""
        integration = self.schema["properties"]["integration"]["properties"]
        self.assertEqual(integration["sdk"], {"const": False})
        self.assertEqual(integration["agent"], {"const": False})


if __name__ == "__main__":
    unittest.main()
