"""Bounded mutation tests for native Hermitian navigation; no production writes."""
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NATIVE = runpy.run_path(str(ROOT / "scripts/finite-hermitian-navigation-v1.py"))
PREFIX = NATIVE["PREFIX"]


class NativeNavigationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hermitian-navigation-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        directory = self.root / PREFIX
        directory.mkdir(parents=True)
        source = ROOT / PREFIX
        manifest = json.loads((source / "READER_MANIFEST.json").read_bytes())
        for name in ["READER_MANIFEST.json"] + [row["path"] for row in manifest["files"]]:
            shutil.copy2(source / name, directory / name)
        for locale in ("en", "id"):
            path = Path("docs") / locale / "programme/index.html"
            (self.root / path).parent.mkdir(parents=True)
            shutil.copy2(ROOT / path, self.root / path)

    def change_reader(self, before, after, reseal=False):
        path = self.root / PREFIX / "index.html"
        raw = path.read_bytes()
        self.assertIn(before, raw)
        changed = raw.replace(before, after, 1)
        path.write_bytes(changed)
        if reseal:
            manifest_path = self.root / PREFIX / "READER_MANIFEST.json"
            manifest = json.loads(manifest_path.read_bytes())
            row = next(row for row in manifest["files"] if row["path"] == "index.html")
            row.update(bytes=len(changed), sha256=hashlib.sha256(changed).hexdigest())
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    def test_exact_native_reader(self):
        self.assertEqual(NATIVE["validate"](self.root)["state"], "pass")

    def test_unsealed_body_change(self):
        self.change_reader(b"Linear algebra", b"Wrong course")
        with self.assertRaisesRegex(ValueError, "Sealed Hermitian file changed"):
            NATIVE["validate"](self.root)

    def test_resealed_wrong_return(self):
        self.change_reader(b"programme/#core-B40", b"programme/#core-A00", True)
        with self.assertRaisesRegex(ValueError, "programme returns changed"):
            NATIVE["validate"](self.root)

    def test_resealed_wrong_locale(self):
        self.change_reader(b'lang="en"', b'lang="id"', True)
        with self.assertRaisesRegex(ValueError, "locale/overlay changed"):
            NATIVE["validate"](self.root)

    def test_resealed_missing_proof_anchor(self):
        self.change_reader(b'id="' + NATIVE["ANCHORS"][0].encode() + b'"', b'id="missing-proof"', True)
        with self.assertRaisesRegex(ValueError, "native proof anchor"):
            NATIVE["validate"](self.root)

    def test_missing_source(self):
        (self.root / PREFIX / "00-finite-hermitian.tex").unlink()
        with self.assertRaises(FileNotFoundError):
            NATIVE["validate"](self.root)

    def test_missing_programme_destination(self):
        path = self.root / "docs/en/programme/index.html"
        path.write_bytes(path.read_bytes().replace(b'id="core-B40"', b'id="missing-course"'))
        with self.assertRaisesRegex(ValueError, "return destination"):
            NATIVE["validate"](self.root)

    def test_missing_reciprocal_proof_links(self):
        path = self.root / "docs/id/programme/index.html"
        path.write_bytes(path.read_bytes().replace(NATIVE["PUBLIC"].encode(), b"https://example.invalid/"))
        with self.assertRaisesRegex(ValueError, "links back"):
            NATIVE["validate"](self.root)


if __name__ == "__main__":
    unittest.main()
