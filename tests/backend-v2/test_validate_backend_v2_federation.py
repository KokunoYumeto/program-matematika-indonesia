#!/usr/bin/env python3
"""Bounded, generated fixtures for the strict federation-v2 validator."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
import uuid
from pathlib import Path
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO / "scripts/validate-backend-v2-federation.py"
SPEC = importlib.util.spec_from_file_location("validate_backend_v2", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)

NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
TABLE_TYPES = {
    "datasets": "dataset",
    "programs": "program",
    "courses": "course",
    "reader_surfaces": "reader_surface",
    "web_routes": "web_route",
    "publication_events": "publication_event",
    "qa_events": "qa_event",
    "identity_crosswalks": "identity_crosswalk",
}
CSV_HEADER = ["record_type", "semantic_key", "id", "record_json"]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_record(record_type: str, semantic_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": f"urn:uuid:{uuid.uuid5(NAMESPACE, record_type + ':' + semantic_key)}",
        "record_type": record_type,
        "semantic_key": semantic_key,
        "payload": payload,
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical(value) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(canonical(row) + "\n" for row in rows), encoding="utf-8", newline="\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_HEADER, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "record_type": row["record_type"],
                "semantic_key": row["semantic_key"],
                "id": row["id"],
                "record_json": canonical(row),
            }
        )
    path.write_text(buffer.getvalue(), encoding="utf-8", newline="\n")


def file_fact(path: Path, root: Path) -> dict[str, Any]:
    return {
        "bytes": path.stat().st_size,
        "path": path.relative_to(root).as_posix(),
        "sha256": sha(path),
    }


def fixture_schema() -> dict[str, Any]:
    record = {
        "type": "object",
        "additionalProperties": False,
        "required": ["id", "record_type", "semantic_key", "payload"],
        "properties": {
            "id": {"type": "string"},
            "record_type": {"type": "string"},
            "semantic_key": {"type": "string"},
            "payload": {"type": "object"},
        },
    }
    table_properties = {name: {"type": "array", "items": record} for name in TABLE_TYPES}
    fact = {
        "type": "object",
        "additionalProperties": False,
        "required": ["path", "bytes", "sha256"],
        "properties": {
            "path": {"type": "string"},
            "bytes": {"type": "integer"},
            "sha256": {"type": "string"},
        },
    }
    status = {
        "type": "object",
        "additionalProperties": False,
        "required": ["table_name", "record_type", "materialized", "record_count"],
        "properties": {
            "table_name": {"type": "string"},
            "record_type": {"type": "string"},
            "materialized": {"type": "boolean"},
            "record_count": {"type": "integer"},
        },
    }
    required = [
        "schema_name",
        "schema_version",
        "package_id",
        "dataset_id",
        "dataset_version",
        "generated_at",
        "namespace_uuid",
        "id_formula",
        "canonical_serialization",
        "records_file",
        "records_sha256",
        "record_count",
        "record_counts",
        "tables",
        "table_statuses",
        "files",
        "source_facts",
    ]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": {
            "schema_name": {"type": "string"},
            "schema_version": {"type": "string"},
            "package_id": {"type": "string"},
            "dataset_id": {"type": "string"},
            "dataset_version": {"type": "string"},
            "generated_at": {"type": "string"},
            "namespace_uuid": {"type": "string"},
            "id_formula": {"type": "string"},
            "canonical_serialization": {"type": "object"},
            "records_file": {"type": "string"},
            "records_sha256": {"type": "string"},
            "record_count": {"type": "integer"},
            "record_counts": {"type": "object"},
            "tables": {
                "type": "object",
                "additionalProperties": False,
                "properties": table_properties,
                "required": list(TABLE_TYPES),
            },
            "table_statuses": {"type": "array", "items": status},
            "files": {"type": "array", "items": fact},
            "source_facts": {"type": "array", "items": fact},
        },
    }


def fixture_record_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["id", "record_type", "semantic_key", "payload"],
        "properties": {
            "id": {"type": "string", "pattern": "^urn:uuid:"},
            "record_type": {"enum": list(TABLE_TYPES.values())},
            "semantic_key": {"type": "string", "minLength": 1},
            "payload": {"type": "object"},
        },
    }


def base_tables() -> dict[str, list[dict[str, Any]]]:
    dataset = make_record(
        "dataset",
        "C80:openlogic-release",
        {
            "canonical_owner_id": "https://github.com/KokunoYumeto/OpenLogic-id",
            "dataset_role": "corpus",
            "publication_state": "draft",
        },
    )
    program = make_record("program", "test-program", {"dataset_id": dataset["id"]})
    route_a_id = f"urn:uuid:{uuid.uuid5(NAMESPACE, 'web_route:A00:current')}"
    route_b_id = f"urn:uuid:{uuid.uuid5(NAMESPACE, 'web_route:A10:current')}"
    matrix_a = {action: None for action in ["learn", "html", "pdf", "epub", "offline", "source", "repository", "doi", "backend"]}
    matrix_a["learn"] = "https://example.test/program/#course-A00"
    matrix_b = {action: None for action in ["learn", "html", "pdf", "epub", "offline", "source", "repository", "doi", "backend"]}
    matrix_b["learn"] = "https://example.test/program/#course-A10"
    course_a = make_record(
        "course",
        "A00",
        {
            "artifact_matrix": matrix_a,
            "course_id": "A00",
            "dataset_id": dataset["id"],
            "learner_start_url": "https://example.test/program/#course-A00",
            "prerequisite_course_ids": [],
            "program_id": program["id"],
            "unit_route_state": "not_published",
            "web_route_id": route_a_id,
            "web_route_root": "https://example.test/program/#course-A00",
        },
    )
    course_b = make_record(
        "course",
        "A10",
        {
            "artifact_matrix": matrix_b,
            "course_id": "A10",
            "dataset_id": dataset["id"],
            "learner_start_url": "https://example.test/program/#course-A10",
            "prerequisite_course_ids": ["A00"],
            "program_id": program["id"],
            "unit_route_state": "not_published",
            "web_route_id": route_b_id,
            "web_route_root": "https://example.test/program/#course-A10",
        },
    )
    surface_a = make_record(
        "reader_surface",
        "A00:learn",
        {
            "action": "learn",
            "availability_state": "available",
            "course_id": course_a["id"],
            "dataset_id": dataset["id"],
            "display_order": 0,
            "primary": True,
            "url": "https://example.test/program/#course-A00",
        },
    )
    surface_b = make_record(
        "reader_surface",
        "A10:learn",
        {
            "action": "learn",
            "availability_state": "available",
            "course_id": course_b["id"],
            "dataset_id": dataset["id"],
            "display_order": 0,
            "primary": True,
            "url": "https://example.test/program/#course-A10",
        },
    )
    route_a = make_record(
        "web_route",
        "A00:current",
        {
            "availability_state": "available",
            "course_id": course_a["id"],
            "course_ids": ["A00"],
            "learner_fallback_url": "https://example.test/program/#course-A00",
            "path": "/#course-A00",
            "primary": True,
            "public_url": "https://example.test/program/#course-A00",
            "unit_route_state": "not_published",
        },
    )
    route_b = make_record(
        "web_route",
        "A10:current",
        {
            "availability_state": "available",
            "course_id": course_b["id"],
            "course_ids": ["A10"],
            "learner_fallback_url": "https://example.test/program/#course-A10",
            "path": "/#course-A10",
            "primary": True,
            "public_url": "https://example.test/program/#course-A10",
            "unit_route_state": "not_published",
        },
    )
    # A future clean route is permitted only while explicitly non-public and
    # non-primary; current fragment routes remain the learner authority.
    route_planned = make_record(
        "web_route",
        "A00:planned-clean",
        {
            "availability_state": "not_published",
            "course_id": course_a["id"],
            "course_ids": ["A00"],
            "primary": False,
            "route": "/id-ID/courses/A00/units/unit-1/",
            "unit_route_state": "not_published",
        },
    )
    publication = make_record(
        "publication_event",
        "C80:release:test",
        {
            "artifacts": [
                {
                    "bytes": 3,
                    "path": "reader.html",
                    "sha256": hashlib.sha256(b"abc").hexdigest(),
                    "url": "https://example.test/releases/reader.html",
                }
            ],
            "dataset_id": dataset["id"],
            "evidence_kind": "anonymous_public_readback",
            "evidence_locator": "receipt.json",
            "evidence_sha256": hashlib.sha256(b"receipt").hexdigest(),
            "public_readback": {"result": "pass"},
            "public_url": "https://example.test/releases/test",
            "publication_state": "published",
        },
    )
    qa = make_record("qa_event", "C80:qa:test", {"dataset_id": dataset["id"], "result": "pass"})
    crosswalk = make_record(
        "identity_crosswalk",
        "v1:A00",
        {
            "dataset_id": dataset["id"],
            "v1_id": "urn:uuid:00000000-0000-0000-0000-000000000001",
            "v2_id": course_a["id"],
            "v2_record_type": "course",
            "v2_semantic_key": course_a["semantic_key"],
        },
    )
    tables = {
        "datasets": [dataset],
        "programs": [program],
        "courses": [course_a, course_b],
        "reader_surfaces": [surface_a, surface_b],
        "web_routes": [route_a, route_b, route_planned],
        "publication_events": [publication],
        "qa_events": [qa],
        "identity_crosswalks": [crosswalk],
    }
    return {
        table: sorted(rows, key=lambda row: (row["record_type"], row["semantic_key"]))
        for table, rows in tables.items()
    }


def seal(package: Path, envelope: dict[str, Any]) -> None:
    for stale_root in (package / "data", package / "csv"):
        if stale_root.exists():
            shutil.rmtree(stale_root)
    all_rows: list[dict[str, Any]] = []
    for table, rows in envelope["tables"].items():
        rows.sort(key=lambda row: (row["record_type"], row["semantic_key"]))
        write_jsonl(package / "data" / f"{table}.jsonl", rows)
        write_csv(package / "csv" / f"{table}.csv", rows)
        all_rows.extend(rows)
    all_rows.sort(key=lambda row: (row["record_type"], row["semantic_key"]))
    write_jsonl(package / "records.jsonl", all_rows)
    write_csv(package / "records.csv", all_rows)
    envelope["record_count"] = len(all_rows)
    envelope["record_counts"] = {table: len(rows) for table, rows in envelope["tables"].items()}
    for status in envelope["table_statuses"]:
        status["record_count"] = len(envelope["tables"].get(status["table_name"], []))
        status["materialized"] = status["table_name"] in envelope["tables"]
    envelope["records_sha256"] = sha(package / "records.jsonl")
    projection_paths = [package / "records.jsonl", package / "records.csv"]
    projection_paths.extend(sorted((package / "data").glob("*.jsonl")))
    projection_paths.extend(sorted((package / "csv").glob("*.csv")))
    envelope["files"] = sorted((file_fact(path, package) for path in projection_paths), key=lambda item: item["path"])
    write_json(package / "federation.json", envelope)
    manifest_paths = [package / "federation.json", *projection_paths]
    manifest = {
        "dataset_id": envelope["dataset_id"],
        "dataset_version": envelope["dataset_version"],
        "files": sorted((file_fact(path, package) for path in manifest_paths), key=lambda item: item["path"]),
        "record_count": envelope["record_count"],
        "record_counts": envelope["record_counts"],
    }
    write_json(package / "manifest.json", manifest)


def make_fixture(root: Path) -> tuple[Path, Path, Path]:
    package = root / "package"
    package.mkdir(parents=True)
    source_root = root / "source"
    source_root.mkdir()
    authority = source_root / "authority.txt"
    authority.write_text("frozen authority\n", encoding="utf-8", newline="\n")
    (source_root / "receipt.json").write_bytes(b"receipt")
    schema_path = root / "schema.json"
    write_json(schema_path, fixture_schema())
    write_json(root / "federation-record-v2.schema.json", fixture_record_schema())
    tables = base_tables()
    envelope = {
        "canonical_serialization": {"encoding": "UTF-8", "json": "RFC8785-compatible", "line_endings": "LF"},
        "dataset_id": f"urn:uuid:{uuid.uuid5(NAMESPACE, 'package:test-federation')}",
        "dataset_version": "test-v0.1.0",
        "files": [],
        "generated_at": "2026-08-25T00:00:00Z",
        "id_formula": "record_type:semantic_key",
        "namespace_uuid": str(NAMESPACE),
        "package_id": "test-federation",
        "record_count": 0,
        "record_counts": {},
        "records_file": "records.jsonl",
        "records_sha256": "0" * 64,
        "schema_name": "interlanguage/test-federation-v2",
        "schema_version": "2.0.0",
        "source_facts": [file_fact(authority, source_root)],
        "table_statuses": [
            {
                "materialized": True,
                "record_count": len(tables[table]),
                "record_type": record_type,
                "table_name": table,
            }
            for table, record_type in TABLE_TYPES.items()
        ],
        "tables": tables,
    }
    seal(package, envelope)
    return package, schema_path, source_root


def load_envelope(package: Path) -> dict[str, Any]:
    return json.loads((package / "federation.json").read_text(encoding="utf-8"))


def find_row(envelope: dict[str, Any], table: str, key: str) -> dict[str, Any]:
    return next(row for row in envelope["tables"][table] if row["semantic_key"] == key)


class ValidatorFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="pmi-v2-validator-")
        self.root = Path(self.temporary.name)
        self.package, self.schema, self.source_root = make_fixture(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def assert_fault(self, expected: str, mutate: Callable[[Path], None]) -> None:
        mutate(self.package)
        with self.assertRaises(VALIDATOR.ValidationFailure) as raised:
            VALIDATOR.validate_package(self.package, self.schema, source_root=self.source_root)
        self.assertIn(expected, str(raised.exception))

    def mutate_and_seal(self, mutate: Callable[[dict[str, Any]], None]) -> None:
        envelope = load_envelope(self.package)
        mutate(envelope)
        seal(self.package, envelope)

    def test_passing_fixture_uri_owner_fragment_routes_and_planned_clean_route(self) -> None:
        result = VALIDATOR.validate_package(self.package, self.schema, source_root=self.source_root)
        self.assertEqual(result["record_count"], 12)
        self.assertEqual(result["owner_profile"]["distinct_task_owners"], 0)
        self.assertEqual(result["source_fact_count_replayed"], 1)

    def test_duplicate_json_key_rejected(self) -> None:
        def fault(package: Path) -> None:
            path = package / "federation.json"
            text = path.read_text(encoding="utf-8")
            path.write_text('{"schema_name":"duplicate",' + text[1:], encoding="utf-8", newline="\n")

        self.assert_fault("duplicate JSON key:schema_name", fault)

    def test_bom_rejected(self) -> None:
        self.assert_fault(
            "UTF-8 BOM forbidden",
            lambda package: (package / "federation.json").write_bytes(b"\xef\xbb\xbf" + (package / "federation.json").read_bytes()),
        )

    def test_crlf_rejected(self) -> None:
        self.assert_fault(
            "CR/CRLF forbidden",
            lambda package: (package / "federation.json").write_bytes((package / "federation.json").read_bytes().replace(b"\n", b"\r\n")),
        )

    def test_noncanonical_json_rejected(self) -> None:
        def fault(package: Path) -> None:
            value = load_envelope(package)
            (package / "federation.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

        self.assert_fault("noncanonical JSON", fault)

    def test_unsafe_manifest_path_rejected(self) -> None:
        def fault(package: Path) -> None:
            manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
            manifest["files"][0]["path"] = "../escape"
            write_json(package / "manifest.json", manifest)

        self.assert_fault("unsafe relative path", fault)

    def test_uuidv5_mismatch_rejected(self) -> None:
        def mutate(envelope: dict[str, Any]) -> None:
            find_row(envelope, "courses", "A10")["id"] = "urn:uuid:00000000-0000-0000-0000-000000000000"

        self.assert_fault("UUIDv5 mismatch", lambda _: self.mutate_and_seal(mutate))

    def test_duplicate_typed_semantic_key_rejected(self) -> None:
        def mutate(envelope: dict[str, Any]) -> None:
            envelope["tables"]["courses"].append(dict(find_row(envelope, "courses", "A00")))

        self.assert_fault("duplicate typed semantic key:course:A00", lambda _: self.mutate_and_seal(mutate))

    def test_typed_foreign_key_mismatch_rejected(self) -> None:
        def mutate(envelope: dict[str, Any]) -> None:
            course = find_row(envelope, "courses", "A10")
            course["payload"]["program_id"] = find_row(envelope, "courses", "A00")["id"]

        self.assert_fault("foreign key type mismatch", lambda _: self.mutate_and_seal(mutate))

    def test_learner_start_mismatch_rejected(self) -> None:
        def mutate(envelope: dict[str, Any]) -> None:
            payload = find_row(envelope, "courses", "A10")["payload"]
            payload["learner_start_url"] = "https://example.test/wrong"
            payload["artifact_matrix"]["learn"] = "https://example.test/wrong"

        self.assert_fault("artifact matrix action lacks matching reader surface", lambda _: self.mutate_and_seal(mutate))

    def test_duplicate_route_rejected(self) -> None:
        def mutate(envelope: dict[str, Any]) -> None:
            find_row(envelope, "web_routes", "A10:current")["payload"]["public_url"] = "https://example.test/program/#course-A00"

        self.assert_fault("duplicate web route URL", lambda _: self.mutate_and_seal(mutate))

    def test_duplicate_reader_surface_url_rejected(self) -> None:
        def mutate(envelope: dict[str, Any]) -> None:
            first = find_row(envelope, "reader_surfaces", "A00:learn")
            second = find_row(envelope, "reader_surfaces", "A10:learn")
            second["payload"]["url"] = first["payload"]["url"]

        self.assert_fault("duplicate reader surface URL", lambda _: self.mutate_and_seal(mutate))

    def test_prerequisite_cycle_rejected(self) -> None:
        def mutate(envelope: dict[str, Any]) -> None:
            a = find_row(envelope, "courses", "A00")
            a["payload"]["prerequisite_course_ids"] = ["A10"]

        self.assert_fault("prerequisite cycle", lambda _: self.mutate_and_seal(mutate))

    def test_published_event_without_readback_rejected(self) -> None:
        def mutate(envelope: dict[str, Any]) -> None:
            payload = find_row(envelope, "publication_events", "C80:release:test")["payload"]
            payload.pop("public_readback")
            payload["publication_state"] = "published_and_readback_verified"
            payload["evidence_kind"] = "publication_receipt"

        self.assert_fault("readback-verified event has wrong evidence kind", lambda _: self.mutate_and_seal(mutate))

    def test_published_dataset_without_evidence_rejected(self) -> None:
        def mutate(envelope: dict[str, Any]) -> None:
            payload = find_row(envelope, "datasets", "C80:openlogic-release")["payload"]
            payload["publication_state"] = "published"
            payload["reader_surface_ids"] = [find_row(envelope, "reader_surfaces", "A00:learn")["id"]]
            payload["migration_validation_result"] = "not_run"

        self.assert_fault("published dataset lacks passing migration evidence", lambda _: self.mutate_and_seal(mutate))

    def test_source_fact_hash_mismatch_rejected(self) -> None:
        self.assert_fault(
            "source fact byte/hash mismatch",
            lambda _: (self.source_root / "authority.txt").write_text(
                "changed authority\n", encoding="utf-8", newline="\n"
            ),
        )

    def test_manifest_hash_mismatch_rejected(self) -> None:
        def fault(package: Path) -> None:
            path = package / "records.csv"
            path.write_bytes(path.read_bytes() + b"\n")

        self.assert_fault("byte mismatch:manifest.files:records.csv", fault)

    def test_table_projection_mismatch_rejected(self) -> None:
        def fault(package: Path) -> None:
            path = package / "data/courses.jsonl"
            rows = list(reversed(VALIDATOR.load_jsonl(path)))
            write_jsonl(path, rows)
            envelope = load_envelope(package)
            envelope["files"] = [
                file_fact(package / item["path"], package) if item["path"] == "data/courses.jsonl" else item
                for item in envelope["files"]
            ]
            write_json(package / "federation.json", envelope)
            manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
            manifest["files"] = [file_fact(package / item["path"], package) for item in manifest["files"]]
            write_json(package / "manifest.json", manifest)

        self.assert_fault("embedded table/JSONL mismatch", fault)

    def test_empty_emitted_table_rejected(self) -> None:
        def mutate(envelope: dict[str, Any]) -> None:
            envelope["tables"]["qa_events"] = []

        self.assert_fault("empty emitted table:qa_events", lambda _: self.mutate_and_seal(mutate))

    def test_replay_byte_mismatch_rejected(self) -> None:
        replay = self.root / "replay"
        shutil.copytree(self.package, replay)
        manifest = json.loads((replay / "manifest.json").read_text(encoding="utf-8"))
        manifest["dataset_version"] = "different"
        write_json(replay / "manifest.json", manifest)
        with self.assertRaises(VALIDATOR.ValidationFailure) as raised:
            VALIDATOR.validate_package(
                self.package,
                self.schema,
                source_root=self.source_root,
                replay_package=replay,
            )
        self.assertIn("replay byte mismatch", str(raised.exception))

    def test_replay_byte_identical_passes(self) -> None:
        replay = self.root / "replay"
        shutil.copytree(self.package, replay)
        result = VALIDATOR.validate_package(
            self.package,
            self.schema,
            source_root=self.source_root,
            replay_package=replay,
        )
        self.assertEqual(result["deterministic_replay"]["result"], "byte-identical")


if __name__ == "__main__":
    unittest.main(verbosity=2)
