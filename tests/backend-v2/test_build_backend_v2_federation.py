from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = REPOSITORY_ROOT.parents[2]
LOGBOOK_ROOT = (
    WORKSPACE_ROOT
    / "outputs"
    / "01a01ec1-e685-70d0-b022-211396334723"
)
BUILDER_PATH = REPOSITORY_ROOT / "scripts" / "build-backend-v2-federation.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("pmi_backend_v2_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class ExplicitBuildInputTests(unittest.TestCase):
    def inputs(self):
        return builder.BuildInputs(
            program_repository_root=REPOSITORY_ROOT,
            coordinator_logbook_root=LOGBOOK_ROOT,
            catalog_relative=PurePosixPath(
                "releases/v0.52.0/program-matematika-indonesia-catalog-v0.52.0.json"
            ),
            v1_package_relative=PurePosixPath(
                "backend/v1/program-matematika-indonesia-v0.51.2"
            ),
            site_readback_relative=PurePosixPath(
                "curriculum_logbook/83_STUDENT_HTML_HUB_PUBLIC_READBACK_20260825.json"
            ),
            contract_relative=PurePosixPath(
                "curriculum_logbook/81_GLOBAL_MODULAR_BACKEND_V2_CONTRACT_20260825.json"
            ),
            role_map_relative=PurePosixPath(
                "curriculum_logbook/49_SEMANTIC_ROLE_MAPPING_CORRECTION_20260823.json"
            ),
            migrations_relative=PurePosixPath("backend/migrations"),
            educational_access_relative=PurePosixPath(
                "backend/research/educational-access-v0.1.0"
            ),
            dataset_version="program-matematika-indonesia-federation-test-explicit",
            recorded_at="2026-08-25T12:00:00Z",
            public_site="https://kokunoyumeto.github.io/program-matematika-indonesia/",
        )

    def test_relative_path_normalization_rejects_absolute_and_parent_escape(self):
        for value in ("../catalog.json", "releases/../catalog.json", "/catalog.json", "C:/catalog.json"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                builder.normalized_relative(value, "--catalog-relative")

    def test_explicit_catalog_is_consumed_and_replay_is_byte_identical(self):
        inputs = self.inputs()
        with tempfile.TemporaryDirectory(prefix="pmi-v2-build-a-") as a_dir, tempfile.TemporaryDirectory(
            prefix="pmi-v2-build-b-"
        ) as b_dir:
            first = builder.materialize(inputs, Path(a_dir))
            second = builder.materialize(inputs, Path(b_dir))

            first_records = Path(a_dir, "records.jsonl").read_bytes()
            second_records = Path(b_dir, "records.jsonl").read_bytes()
            self.assertEqual(first_records, second_records)
            self.assertEqual(first["record_count"], second["record_count"])

            federation = json.loads(Path(a_dir, "federation.json").read_text(encoding="utf-8"))
            self.assertEqual(
                federation["build"]["inputs"]["catalog_relative"],
                "releases/v0.52.0/program-matematika-indonesia-catalog-v0.52.0.json",
            )
            self.assertEqual(
                federation["build"]["inputs"]["v1_package_relative"],
                "backend/v1/program-matematika-indonesia-v0.51.2",
            )
            self.assertNotIn(str(REPOSITORY_ROOT), json.dumps(federation["build"], ensure_ascii=False))

            program_rows = [
                json.loads(line)
                for line in Path(a_dir, "data", "programs.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(program_rows[0]["payload"]["version"], "0.52.0")
            self.assertEqual(
                program_rows[0]["payload"]["catalog_locator"],
                "releases/v0.52.0/program-matematika-indonesia-catalog-v0.52.0.json",
            )


if __name__ == "__main__":
    unittest.main()
