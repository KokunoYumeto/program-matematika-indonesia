from __future__ import annotations

import hashlib
import json
import re
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE = REPO_ROOT / "backend" / "v2.2" / "packages" / "a00-openstax-prealgebra-v0.1.0"
NAMESPACE = uuid.UUID("0e4d7b37-6108-5065-b08f-d1098697cc02")
MACHINE_ROUTE = re.compile(r"(?:localhost|127\.0\.0\.1|\.(?:jsonl?|csv)(?:[?#]|$)|/api(?:/|$))")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def iter_rows(path: Path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line in handle:
            yield json.loads(line)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class A00PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_json(PACKAGE / "manifest.json")

    def test_zero_copy_native_contract(self):
        index = load_json(PACKAGE / "native-shard-index.json")
        loss = load_json(PACKAGE / "capability-loss-report.json")
        self.assertEqual(index["record_count"], 519678)
        self.assertEqual(index["view_count"], 17)
        self.assertTrue(index["zero_copy"])
        self.assertEqual(loss["native_records_copied"], 0)
        self.assertEqual(loss["native_records_referenced"], 519678)
        self.assertEqual(loss["unexplained_native_record_loss"], 0)

    def test_projected_record_ids_are_uuid5(self):
        count = 0
        for item in self.manifest["table_inventory"]:
            for row in iter_rows(PACKAGE / item["path"]):
                expected = f"urn:uuid:{uuid.uuid5(NAMESPACE, row['record_type'] + ':' + row['semantic_key'])}"
                self.assertEqual(row["id"], expected)
                count += 1
        self.assertEqual(count, 1313)

    def test_exact_unit_mapping_and_human_routes(self):
        identity_rows = list(iter_rows(PACKAGE / "identity-map.jsonl"))
        unit_maps = [row for row in identity_rows if row["kind"] == "projected_unit"]
        self.assertEqual(len(unit_maps), 75)
        self.assertEqual({row["mapping_cardinality"] for row in unit_maps}, {"one_to_one"})
        self.assertEqual(len({row["native_id"] for row in unit_maps}), 75)
        self.assertEqual(len({row["projected_record_id"] for row in unit_maps}), 75)

        routes = list(iter_rows(PACKAGE / "tables" / "routes.jsonl"))
        self.assertEqual(len(routes), 75)
        for route in routes:
            payload = route["payload"]
            self.assertFalse(payload["machine_data_only"])
            self.assertEqual(payload["target_kind"], "readable_html")
            self.assertTrue(payload["public_url"].startswith("https://"))
            self.assertIsNone(MACHINE_ROUTE.search(payload["public_url"]))

    def test_manifest_and_seal_inventory(self):
        self.assertEqual(self.manifest["build"]["build_a_sha256"], self.manifest["build"]["build_b_sha256"])
        seal = load_json(PACKAGE / "seal.json")
        actual = sorted(
            path.relative_to(PACKAGE).as_posix()
            for path in PACKAGE.rglob("*")
            if path.is_file() and path.name != "seal.json"
        )
        declared = sorted(item["path"] for item in seal["files"])
        self.assertEqual(actual, declared)
        self.assertEqual(seal["file_count"], len(declared))
        self.assertEqual(seal["total_bytes"], sum(item["bytes"] for item in seal["files"]))
        for item in seal["files"]:
            path = PACKAGE / item["path"]
            self.assertEqual(path.stat().st_size, item["bytes"])
            self.assertEqual(sha256(path), item["sha256"])

    def test_persisted_validation_receipt(self):
        report = load_json(PACKAGE / "validation-report.json")
        self.assertEqual(report["schema_id"], "interlanguage/global-modular-mathematics-validation-report/2.2.0")
        self.assertEqual(report["result"], "pass")
        self.assertEqual(report["counts"]["errors"], 0)
        self.assertEqual(report["counts"]["native_records_referenced"], 519678)
        self.assertEqual(report["counts"]["projected_records"], 1313)


if __name__ == "__main__":
    unittest.main()
