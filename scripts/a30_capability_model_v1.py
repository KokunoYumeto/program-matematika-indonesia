"""Streaming model and invariants for the A30 zero-copy capability adapter.

The authoritative final backend is the canonical JSONL member of the public
1.0.0 backend-core ZIP.  The loose producer exports predate the final source
corrections and are deliberately not used here.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_NATIVE = PROJECT.parent / "openstax-precalculus-2e-id"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/a30-capability-v1"
PUBLIC_RECEIPT_PATH = DEFAULT_ADAPTER / "input/public-native-readback.json"

COURSE_ID = "A30"
NATIVE_ROLE_ID = "R002"
NATIVE_COURSE_ID = "urn:interlanguage:course:A30"
CENTRAL_PREREQUISITE_ID = "A20"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"

PUBLIC_REPOSITORY = "https://github.com/KokunoYumeto/openstax-precalculus-2e-id"
UPSTREAM_REPOSITORY = "https://github.com/openstax/osbooks-college-algebra-bundle"
UPSTREAM_COMMIT = "789b54099106b071d1d32bfcee454fed72eb4768"
UPSTREAM_TREE = "05b39123f698772482c0c33a43fa2d2d4ea562ae"
RELEASE_TAG = "v1.0.0"
ZENODO_RECORD_ID = 22290180
ZENODO_CONCEPT_ID = 22059757

BACKEND_ARCHIVE = Path("release/reader/1.0.0/precalculus-2e-id-ID-1.0.0-backend-core.zip")
BACKEND_RECORD_MEMBER = "backend/canonical/records.jsonl"
BACKEND_MANIFEST_MEMBER = "backend/exports/export-manifest.json"
RELEASE_MANIFEST = Path("release/reader/1.0.0/precalculus-2e-id-ID-1.0.0-manifest.json")
READER_QA = Path("qa/FULL87_ATTEMPT12_FINAL3165_READER_QA_V1_20260904.json")
NAVIGATION_PROFILE = Path("qa/FULL87_ATTEMPT12_FINAL3165_NAVIGATION_PROFILE_20260904.json")
TERMINAL_AUDIT = Path("qa/FULL87_FINAL_RELEASE_TERMINAL_AUDIT_1.0.0_20260904.json")
GITHUB_RECEIPT = Path("qa/GITHUB_READER_1.0.0_20260904.json")
ZENODO_RECEIPT = Path("qa/ZENODO_READER_1.0.0_20260904.json")

PDF_NAME = "OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf"
PDF_URL = f"https://zenodo.org/records/{ZENODO_RECORD_ID}/files/{PDF_NAME}?download=1"
EXPECTED_PDF = {
    "bytes": 305_654_938,
    "pages": 3_165,
    "sha256": "3cfd5294b91252cc766992f158b6601e80aa31b719b0b8bf69e1ff6d08a4fa3e",
}

EXPECTED_LOCAL_INPUTS = {
    BACKEND_ARCHIVE.as_posix(): {
        "bytes": 97_424_500,
        "sha256": "7c0d63a13a0cd3246fdb58a5faabd3f4f75e2f37a005581ff8ff97d14329fa91",
    },
    RELEASE_MANIFEST.as_posix(): {
        "bytes": 4_137,
        "sha256": "346c8c4f917137a767dcbecfb00af8ea824465cd012bc38a089c501a7eef3351",
    },
    READER_QA.as_posix(): {
        "bytes": 12_635,
        "sha256": "46305df70b0c55db648386dde31e3fa42681bdca554445de8e521c4278a5e1a7",
    },
    NAVIGATION_PROFILE.as_posix(): {
        "bytes": 58_850,
        "sha256": "659c32f156fc142473e13ee894117ad16e2778083a92a34ee40192118565d48b",
    },
    TERMINAL_AUDIT.as_posix(): {
        "bytes": 4_663,
        "sha256": "15c9f634db44a04022b5abde1cb5f468e6480cf18630a361a594d1ff2f760fde",
    },
    GITHUB_RECEIPT.as_posix(): {
        "bytes": 5_308,
        "sha256": "78a9d98907989dc3137e54920dd51d02e8a8113052e99ba2559fa49311619a42",
    },
    ZENODO_RECEIPT.as_posix(): {
        "bytes": 4_447,
        "sha256": "d428ff794308ab2132e498b77ecc4b2ab75d9bda244c5e4a4eec2dabdeb9a242",
    },
}

EXPECTED_CANONICAL_BYTES = 426_073_883
EXPECTED_CANONICAL_SHA256 = "4f2f51457adde0516c17b1633327a3bfbbf273a67925514bbb6c390f5e58a054"
EXPECTED_ID_SEQUENCE_SHA256 = "9c17bdf922dc80bda672f05f2364f3876fa1c7507bf5e1db50c5c46cbb7bdc27"
EXPECTED_RECORD_COUNTS = {
    "artifact": 14,
    "asset": 2162,
    "concept": 497,
    "correction": 703,
    "course": 1,
    "edition": 1,
    "program": 1,
    "qa_event": 18,
    "relation": 37974,
    "resource": 1,
    "rights": 1875,
    "segment": 149955,
    "term": 513,
    "unit": 26965,
}
EXPECTED_UNIT_COUNTS = {
    "chapter": 12,
    "collection": 1,
    "commentary": 181,
    "definition": 318,
    "equation": 2037,
    "example": 725,
    "exercise": 7250,
    "figure": 868,
    "list": 1094,
    "module": 87,
    "note": 1174,
    "problem": 7250,
    "section": 1340,
    "solution": 4183,
    "table": 445,
}
EXPECTED_RELATION_COUNTS = {
    "contains": 26865,
    "depends-on": 2174,
    "derived-from": 278,
    "derived-from-source-data": 1,
    "describes": 2611,
    "rights-replacement": 10,
    "solves": 4183,
    "xref": 1852,
}
EXPECTED_SEGMENT_BUCKET_COUNTS = {
    "en|source_frozen|active": 49969,
    "en|superseded|retired": 2,
    "id-ID|superseded|retired": 2,
    "id-ID|translated|active": 49990,
    "und|source_frozen|active": 49969,
    "und|superseded|retired": 2,
    "und|translated|active": 21,
}
EXPECTED_SEGMENT_STATE_COUNTS = {"source_frozen": 99938, "superseded": 6, "translated": 50011}

EXPECTED_PUBLIC_ASSETS = {
    "LICENSE.txt": {"bytes": 1_551, "sha256": "8d7c3c9767995f187c79022c4463686f4b7f5a27c0d3d187e5f3f4de5256654a"},
    PDF_NAME: {"bytes": 305_654_938, "sha256": EXPECTED_PDF["sha256"]},
    "README.txt": {"bytes": 1_833, "sha256": "7e76cc9e36a66b336d84c4ea3a458a289612b946fb688c45b8bee2d52a015b87"},
    "SHA256SUMS.txt": {"bytes": 594, "sha256": "6bd41208bef757b266d1f722152e4855143fdfd3f91677c9cd0d729ddecea4c3"},
    "precalculus-2e-id-ID-1.0.0-backend-core.zip": {"bytes": 97_424_500, "sha256": "7c0d63a13a0cd3246fdb58a5faabd3f4f75e2f37a005581ff8ff97d14329fa91"},
    "precalculus-2e-id-ID-1.0.0-manifest.json": {"bytes": 4_137, "sha256": "346c8c4f917137a767dcbecfb00af8ea824465cd012bc38a089c501a7eef3351"},
    "precalculus-2e-id-ID-1.0.0-source-core.zip": {"bytes": 96_797_004, "sha256": "04d364ad89005a13999ea27c1398e043ac56886af88d9a7add70aee3ae0d6126"},
}
EXPECTED_PUBLIC_TOTAL_BYTES = 499_884_557

SELECTED_UNIT_KINDS = {"collection", "chapter", "module", "exercise", "problem", "solution"}
FORBIDDEN_CONTENT_KEYS = {
    "answer_body",
    "body",
    "content",
    "defect",
    "exercise_text",
    "final_target_texts",
    "full_text",
    "native_body",
    "normalized_source_after_xml",
    "notes",
    "preferred_form",
    "prompt",
    "prompt_text",
    "prose",
    "rejected_forms",
    "solution_body",
    "solution_text",
    "source_before_xml",
    "source_label",
    "source_term",
    "source_text",
    "target_correction",
    "target_delta",
    "target_resolution",
    "target_text",
    "tex_body",
    "text",
    "variants",
}


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        for row in rows
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def identity(path: Path, *, display_path: str | None = None) -> dict[str, Any]:
    return {"path": display_path or path.as_posix(), "bytes": path.stat().st_size, "sha256": sha256_path(path)}


def identity_bytes(data: bytes, *, path: str) -> dict[str, Any]:
    return {"path": path, "bytes": len(data), "sha256": sha256_bytes(data)}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def read_canonical_jsonl(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        raise ValueError(f"JSONL is not LF terminated: {path}")
    rows: list[dict[str, Any]] = []
    for number, raw in enumerate(data.splitlines(), 1):
        if not raw:
            continue
        row = json.loads(raw)
        expected = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if raw != expected:
            raise ValueError(f"Noncanonical JSONL row {number}: {path}")
        rows.append(row)
    return rows


def _row_sha(raw: bytes) -> str:
    return sha256_bytes(raw[:-1] if raw.endswith(b"\n") else raw)


def _reader_route(page: int) -> str:
    return f"{PDF_URL}#page={page}"


def _project_unit(row: dict[str, Any], raw: bytes) -> dict[str, Any]:
    return {
        "id": row["id"],
        "kind": row["data"]["unit_kind"],
        "parent_id": row.get("parent_id"),
        "path": row.get("path", []),
        "order": row.get("order"),
        "source_local_id": row.get("source_local_id"),
        "source_locator": row.get("source_locator"),
        "source_sha256": row.get("source_sha256"),
        "record_status": row.get("status"),
        "translation_state": row.get("translation_state"),
        "native_record_sha256": _row_sha(raw),
    }


def _project_relation(row: dict[str, Any], raw: bytes) -> dict[str, Any]:
    data = row.get("data") or {}
    return {
        "id": row["id"],
        "relation_type": data.get("relation_type"),
        "from_id": data.get("from_id"),
        "to_id": data.get("to_id"),
        "exercise_id": data.get("exercise_id"),
        "parent_id": row.get("parent_id"),
        "record_status": row.get("status"),
        "native_record_sha256": _row_sha(raw),
    }


def _project_concept(row: dict[str, Any], raw: bytes) -> dict[str, Any]:
    return {
        "id": row["id"],
        "source_local_id": row.get("source_local_id"),
        "identity_kind": (row.get("data") or {}).get("identity_kind"),
        "prerequisite_ids": row.get("prerequisite_ids", []),
        "record_status": row.get("status"),
        "native_record_sha256": _row_sha(raw),
        "source_or_target_text_embedded": False,
    }


def _project_term(row: dict[str, Any], raw: bytes) -> dict[str, Any]:
    data = row.get("data") or {}
    return {
        "id": row["id"],
        "source_local_id": row.get("source_local_id"),
        "concept_ids": row.get("concept_ids", []),
        "decision_status": data.get("decision_status"),
        "record_status": row.get("status"),
        "native_record_sha256": _row_sha(raw),
        "source_or_target_text_embedded": False,
    }


def _as_list(data: dict[str, Any], plural: str, singular: str) -> list[Any]:
    values = data.get(plural)
    if isinstance(values, list):
        return values
    value = data.get(singular)
    return [] if value is None else [value]


def _project_correction(row: dict[str, Any], raw: bytes) -> dict[str, Any]:
    data = row.get("data") or {}
    unit_ids = list(dict.fromkeys(_as_list(data, "unit_ids", "unit_id") + list(data.get("affected_unit_ids") or [])))
    return {
        "id": row["id"],
        "parent_id": row.get("parent_id"),
        "source_local_id": row.get("source_local_id"),
        "source_locator": row.get("source_locator"),
        "correction_key": data.get("correction_key"),
        "module_ids": _as_list(data, "module_ids", "module_id"),
        "unit_ids": unit_ids,
        "event_type": data.get("event_type"),
        "primary_classification": data.get("primary_classification"),
        "target_status": data.get("target_status"),
        "upstream_disposition": data.get("upstream_disposition"),
        "protected_mathml_delta": data.get("protected_mathml_delta"),
        "record_status": row.get("status"),
        "native_record_sha256": _row_sha(raw),
        "source_or_target_text_embedded": False,
    }


def _project_rights(row: dict[str, Any], raw: bytes) -> dict[str, Any]:
    data = row.get("data") or {}
    return {
        "id": row["id"],
        "source_local_id": row.get("source_local_id"),
        "source_locator": row.get("source_locator"),
        "record_status": row.get("status"),
        "asset_path": data.get("asset_path"),
        "source_modules": data.get("source_modules"),
        "admission": data.get("admission"),
        "classification": data.get("classification"),
        "license_id": data.get("license_id"),
        "license_expression": data.get("license_expression"),
        "license_url": data.get("license_url"),
        "publication_state": data.get("publication_state"),
        "required_action": data.get("required_action"),
        "attribution": data.get("attribution"),
        "change_notice": data.get("change_notice"),
        "non_endorsement": data.get("non_endorsement"),
        "scope": data.get("scope"),
        "native_record_sha256": _row_sha(raw),
    }


def _scan_native(native_root: Path) -> dict[str, Any]:
    archive_path = native_root / BACKEND_ARCHIVE
    counts: Counter[str] = Counter()
    unit_counts: Counter[str] = Counter()
    relation_counts: Counter[str] = Counter()
    correction_statuses: Counter[str] = Counter()
    term_decision_statuses: Counter[str] = Counter()
    rights_admission_counts: Counter[str] = Counter()
    segment_state_counts: Counter[str] = Counter()
    segment_buckets: dict[str, dict[str, Any]] = {}
    ids: set[str] = set()
    id_digest = hashlib.sha256()
    file_digest = hashlib.sha256()
    type_id_digests: dict[str, Any] = defaultdict(hashlib.sha256)
    type_record_digests: dict[str, Any] = defaultdict(hashlib.sha256)
    type_first: dict[str, str] = {}
    type_last: dict[str, str] = {}
    course_rows: list[dict[str, Any]] = []
    selected_units: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    concepts: list[dict[str, Any]] = []
    terms: list[dict[str, Any]] = []
    corrections: list[dict[str, Any]] = []
    rights: list[dict[str, Any]] = []
    concept_unit_ids: dict[str, list[str]] = defaultdict(list)
    previous_key: tuple[str, str] | None = None

    with zipfile.ZipFile(archive_path, "r") as archive:
        manifest = json.loads(archive.read(BACKEND_MANIFEST_MEMBER))
        with archive.open(BACKEND_RECORD_MEMBER, "r") as handle:
            for number, raw in enumerate(handle, 1):
                if not raw.endswith(b"\n"):
                    raise ValueError(f"A30 canonical row {number} lacks LF termination")
                file_digest.update(raw)
                row = json.loads(raw)
                entity = row["entity"]
                record_id = row["id"]
                key = (entity, record_id)
                if previous_key is not None and key < previous_key:
                    raise ValueError(f"A30 canonical record order drift at row {number}")
                previous_key = key
                if record_id in ids:
                    raise ValueError(f"A30 duplicate native id: {record_id}")
                ids.add(record_id)
                counts[entity] += 1
                id_digest.update(record_id.encode("utf-8") + b"\n")
                type_id_digests[entity].update(record_id.encode("utf-8") + b"\n")
                type_record_digests[entity].update(raw)
                type_first.setdefault(entity, record_id)
                type_last[entity] = record_id

                if entity == "course":
                    course_rows.append(row)
                elif entity == "unit":
                    kind = row["data"]["unit_kind"]
                    unit_counts[kind] += 1
                    for concept_id in row.get("concept_ids", []):
                        concept_unit_ids[concept_id].append(record_id)
                    if kind in SELECTED_UNIT_KINDS:
                        selected_units.append(_project_unit(row, raw))
                elif entity == "relation":
                    projected = _project_relation(row, raw)
                    relation_counts[str(projected["relation_type"])] += 1
                    relations.append(projected)
                elif entity == "concept":
                    concepts.append(_project_concept(row, raw))
                elif entity == "term":
                    projected = _project_term(row, raw)
                    term_decision_statuses[str(projected["decision_status"])] += 1
                    terms.append(projected)
                elif entity == "correction":
                    projected = _project_correction(row, raw)
                    correction_statuses[str(projected["record_status"])] += 1
                    corrections.append(projected)
                elif entity == "rights":
                    projected = _project_rights(row, raw)
                    rights_admission_counts[str(projected["admission"])] += 1
                    rights.append(projected)
                elif entity == "segment":
                    state = str(row.get("translation_state"))
                    bucket_key = "|".join((str(row.get("locale")), state, str(row.get("status"))))
                    segment_state_counts[state] += 1
                    bucket = segment_buckets.setdefault(
                        bucket_key,
                        {"count": 0, "id_digest": hashlib.sha256(), "record_digest": hashlib.sha256()},
                    )
                    bucket["count"] += 1
                    bucket["id_digest"].update(record_id.encode("utf-8") + b"\n")
                    bucket["record_digest"].update(raw)

        record_info = archive.getinfo(BACKEND_RECORD_MEMBER)

    if dict(sorted(counts.items())) != EXPECTED_RECORD_COUNTS:
        raise ValueError(f"A30 entity count drift: {dict(sorted(counts.items()))}")
    if dict(sorted(unit_counts.items())) != EXPECTED_UNIT_COUNTS:
        raise ValueError(f"A30 unit-kind count drift: {dict(sorted(unit_counts.items()))}")
    if dict(sorted(relation_counts.items())) != EXPECTED_RELATION_COUNTS:
        raise ValueError(f"A30 relation count drift: {dict(sorted(relation_counts.items()))}")
    if len(ids) != 220_680 or id_digest.hexdigest() != EXPECTED_ID_SEQUENCE_SHA256:
        raise ValueError("A30 native ID inventory drift")
    if record_info.file_size != EXPECTED_CANONICAL_BYTES or file_digest.hexdigest() != EXPECTED_CANONICAL_SHA256:
        raise ValueError("A30 final canonical JSONL identity drift")
    if len(course_rows) != 1 or course_rows[0]["id"] != NATIVE_COURSE_ID:
        raise ValueError("A30 native course identity drift")
    if course_rows[0].get("prerequisite_ids") != []:
        raise ValueError("A30 native source unexpectedly asserts course prerequisites")
    manifest_file = next(row for row in manifest.get("files", []) if row.get("path") == BACKEND_RECORD_MEMBER)
    if manifest.get("canonical_record_count") != 220_680 or {
        "bytes": manifest_file.get("bytes"), "sha256": manifest_file.get("sha256")
    } != {"bytes": EXPECTED_CANONICAL_BYTES, "sha256": EXPECTED_CANONICAL_SHA256}:
        raise ValueError("A30 final backend manifest drift")

    bucket_counts = {key: value["count"] for key, value in sorted(segment_buckets.items())}
    if bucket_counts != EXPECTED_SEGMENT_BUCKET_COUNTS or dict(sorted(segment_state_counts.items())) != EXPECTED_SEGMENT_STATE_COUNTS:
        raise ValueError("A30 segment-state asymmetry drift")
    segment_summary = {
        "schema": "a30-segment-state-summary/1",
        "record_count": counts["segment"],
        "state_counts": dict(sorted(segment_state_counts.items())),
        "bucket_counts": bucket_counts,
        "buckets": [
            {
                "bucket": key,
                "count": value["count"],
                "id_sequence_sha256": value["id_digest"].hexdigest(),
                "record_sequence_sha256": value["record_digest"].hexdigest(),
            }
            for key, value in sorted(segment_buckets.items())
        ],
        "source_or_target_text_embedded": False,
        "asymmetry_preserved": True,
    }
    for row in concepts:
        related = sorted(concept_unit_ids.get(row["id"], []))
        row["related_unit_ids"] = related
        row["related_unit_count"] = len(related)

    ledger = {
        "schema": "a30-native-record-ledger/1",
        "record_count": len(ids),
        "unique_ids": len(ids),
        "canonical_member": {
            "path": f"{BACKEND_ARCHIVE.as_posix()}#{BACKEND_RECORD_MEMBER}",
            "bytes": record_info.file_size,
            "sha256": file_digest.hexdigest(),
        },
        "id_sequence_sha256": id_digest.hexdigest(),
        "record_sequence_sha256": file_digest.hexdigest(),
        "entities": [
            {
                "entity": entity,
                "count": counts[entity],
                "first_id": type_first[entity],
                "last_id": type_last[entity],
                "id_sequence_sha256": type_id_digests[entity].hexdigest(),
                "record_sequence_sha256": type_record_digests[entity].hexdigest(),
            }
            for entity in sorted(counts)
        ],
    }
    return {
        "ledger": ledger,
        "record_counts": dict(sorted(counts.items())),
        "unit_counts": dict(sorted(unit_counts.items())),
        "relation_counts": dict(sorted(relation_counts.items())),
        "correction_statuses": dict(sorted(correction_statuses.items())),
        "term_decision_statuses": dict(sorted(term_decision_statuses.items())),
        "rights_admission_counts": dict(sorted(rights_admission_counts.items())),
        "segment_summary": segment_summary,
        "course": course_rows[0],
        "selected_units": selected_units,
        "relations": sorted(relations, key=lambda row: (str(row["relation_type"]), row["id"])),
        "concepts": sorted(concepts, key=lambda row: row["id"]),
        "terms": sorted(terms, key=lambda row: row["id"]),
        "corrections": sorted(corrections, key=lambda row: row["id"]),
        "rights": sorted(rights, key=lambda row: row["id"]),
    }


def _assert_local_inputs(native_root: Path) -> list[dict[str, Any]]:
    inputs: list[dict[str, Any]] = []
    for relative, expected in EXPECTED_LOCAL_INPUTS.items():
        actual = identity(native_root / Path(relative), display_path=relative)
        if {"bytes": actual["bytes"], "sha256": actual["sha256"]} != expected:
            raise ValueError(f"A30 pinned producer input drift: {relative}")
        inputs.append(actual)
    return inputs


def _asset_map(rows: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list) or len(rows) != len(EXPECTED_PUBLIC_ASSETS):
        raise ValueError("A30 public asset inventory multiplicity drift")
    assets: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("A30 public asset inventory contains a non-object")
        name = str(row.get("name") or row.get("filename") or "")
        if not name or name in assets:
            raise ValueError("A30 public asset inventory contains a missing or duplicate name")
        assets[name] = {
            "bytes": row.get("bytes"),
            "sha256": row.get("sha256"),
        }
    return assets


def _assert_public_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("state") != "pass" or receipt.get("failures") or receipt.get("anonymous") is not True or receipt.get("credentials_used") is not False:
        raise ValueError("A30 public-native evidence is not a credential-free pass")
    repository = receipt.get("repository", {})
    if repository.get("url") != PUBLIC_REPOSITORY or repository.get("public") is not True or repository.get("tag") != RELEASE_TAG:
        raise ValueError("A30 public receipt repository identity drift")
    if repository.get("final_derivative_revision_proved") is not False or repository.get("final_derivative_commit") is not None or repository.get("final_derivative_tree") is not None:
        raise ValueError("A30 public receipt invents an unproved final derivative revision")
    github = receipt.get("github_release", {})
    zenodo = receipt.get("zenodo", {})
    if github.get("url") != f"{PUBLIC_REPOSITORY}/releases/tag/{RELEASE_TAG}" or github.get("tag") != RELEASE_TAG or github.get("draft") is not False or github.get("prerelease") is not False:
        raise ValueError("A30 GitHub final release evidence drift")
    if zenodo.get("record_id") != ZENODO_RECORD_ID or zenodo.get("concept_id") != ZENODO_CONCEPT_ID or zenodo.get("access_right") != "open":
        raise ValueError("A30 Zenodo final release evidence drift")
    if _asset_map(github.get("assets")) != EXPECTED_PUBLIC_ASSETS or _asset_map(zenodo.get("assets")) != EXPECTED_PUBLIC_ASSETS:
        raise ValueError("A30 public asset inventory drift")
    if github.get("total_bytes") != EXPECTED_PUBLIC_TOTAL_BYTES or zenodo.get("total_bytes") != EXPECTED_PUBLIC_TOTAL_BYTES:
        raise ValueError("A30 public asset total drift")


def _source_lock(native_root: Path, receipt_path: Path, scan: dict[str, Any]) -> dict[str, Any]:
    inputs = _assert_local_inputs(native_root)
    inputs.append(identity_bytes(
        canonical_json_bytes(read_json(receipt_path)),
        path="input/public-native-readback.json",
    ))
    return {
        "schema": "a30-capability-source-lock/1",
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "native_export": {
            "container": inputs[0],
            "canonical_member": scan["ledger"]["canonical_member"],
            "record_count": 220_680,
            "jsonl_sha256": EXPECTED_CANONICAL_SHA256,
            "standalone_full_raw_replay_claimed": False,
            "source_companion_required_for_full_replay": True,
        },
        "indonesian_release": {
            "repository": PUBLIC_REPOSITORY,
            "tag": RELEASE_TAG,
            "zenodo_record_id": ZENODO_RECORD_ID,
            "zenodo_concept_id": ZENODO_CONCEPT_ID,
            "complete_public_edition": True,
            "final_derivative_commit": None,
            "final_derivative_tree": None,
            "final_derivative_revision_proved": False,
        },
        "upstream_source": {
            "repository": UPSTREAM_REPOSITORY,
            "commit": UPSTREAM_COMMIT,
            "tree": UPSTREAM_TREE,
        },
        "inputs": inputs,
    }


def derive_projection(native_root: Path, receipt_path: Path = PUBLIC_RECEIPT_PATH) -> dict[str, Any]:
    receipt = read_json(receipt_path)
    _assert_public_receipt(receipt)
    release_manifest = read_json(native_root / RELEASE_MANIFEST)
    reader_qa = read_json(native_root / READER_QA)
    navigation = read_json(native_root / NAVIGATION_PROFILE)
    terminal = read_json(native_root / TERMINAL_AUDIT)
    github_receipt = read_json(native_root / GITHUB_RECEIPT)
    zenodo_receipt = read_json(native_root / ZENODO_RECEIPT)

    if release_manifest.get("status") != "complete" or release_manifest.get("complete_edition") is not True:
        raise ValueError("A30 release manifest is not complete")
    if release_manifest.get("authority") != {
        "collection_uuid": "f021395f-fd63-46cd-ab95-037c6f051730",
        "commit": UPSTREAM_COMMIT,
        "tree": UPSTREAM_TREE,
    }:
        raise ValueError("A30 upstream authority drift")
    reader = release_manifest.get("reader", {})
    if reader.get("pages") != EXPECTED_PDF["pages"] or reader.get("filename") != PDF_NAME:
        raise ValueError("A30 reader release coverage drift")
    if reader_qa.get("result") != "pass_release_candidate" or reader_qa.get("scope", {}).get("translated_modules") != 87:
        raise ValueError("A30 reader QA is not a complete pass")
    if terminal.get("result") != "pass_terminal_complete" or terminal.get("backend", {}).get("records") != 220_680:
        raise ValueError("A30 terminal audit drift")
    if github_receipt.get("status") != "public_and_anonymously_byte_verified" or github_receipt.get("release", {}).get("tag") != RELEASE_TAG:
        raise ValueError("A30 producer GitHub receipt drift")
    if zenodo_receipt.get("status") != "published_and_anonymously_verified" or zenodo_receipt.get("zenodo", {}).get("record_id") != ZENODO_RECORD_ID:
        raise ValueError("A30 producer Zenodo receipt drift")

    scan = _scan_native(native_root)
    selected_units = scan["selected_units"]
    units_by_id = {row["id"]: row for row in selected_units}
    by_kind: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected_units:
        by_kind[row["kind"]].append(row)

    modules_by_source = {str(row["source_local_id"]): row for row in by_kind["module"]}
    module_unit_to_source = {row["id"]: str(row["source_local_id"]) for row in by_kind["module"]}
    nav_rows = navigation.get("source_registry", {}).get("parts", {}).get("rows", [])
    module_nav = sorted((row for row in nav_rows if row.get("label") in modules_by_source), key=lambda row: row["order"])
    if len(module_nav) != 87 or [row["order"] for row in module_nav] != list(range(1, 88)):
        raise ValueError("A30 module navigation registry drift")

    exercises = {row["id"]: row for row in by_kind["exercise"]}
    problems_by_parent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    solutions_by_parent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in by_kind["problem"]:
        problems_by_parent[str(row["parent_id"])].append(row)
    for row in by_kind["solution"]:
        solutions_by_parent[str(row["parent_id"])].append(row)
    if set(problems_by_parent) != set(exercises) or any(len(rows) != 1 for rows in problems_by_parent.values()):
        raise ValueError("A30 exercise/problem identity closure drift")
    if not set(solutions_by_parent).issubset(exercises) or any(len(rows) != 1 for rows in solutions_by_parent.values()):
        raise ValueError("A30 exercise/solution identity closure drift")

    solves = [row for row in scan["relations"] if row["relation_type"] == "solves"]
    expected_solves = {
        (rows[0]["id"], problems_by_parent[exercise_id][0]["id"], exercise_id)
        for exercise_id, rows in solutions_by_parent.items()
    }
    actual_solves = {(row["from_id"], row["to_id"], row["exercise_id"]) for row in solves}
    if actual_solves != expected_solves:
        raise ValueError("A30 solves relation closure drift")

    exercise_module: dict[str, str] = {}
    for exercise_id, exercise in exercises.items():
        ancestors = [unit_id for unit_id in exercise["path"] if unit_id in module_unit_to_source]
        if len(ancestors) != 1:
            raise ValueError(f"A30 exercise/module ancestry drift: {exercise_id}")
        exercise_module[exercise_id] = module_unit_to_source[ancestors[0]]

    exercise_count_by_module = Counter(exercise_module.values())
    solution_count_by_module = Counter(exercise_module[exercise_id] for exercise_id in solutions_by_parent)
    concept_count_by_module: Counter[str] = Counter()
    for concept in scan["concepts"]:
        module_ids = {
            module_unit_to_source[unit_id]
            for unit_id in concept["related_unit_ids"]
            if unit_id in module_unit_to_source
        }
        for module_id in module_ids:
            concept_count_by_module[module_id] += 1

    module_index: list[dict[str, Any]] = []
    for ordinal, nav_row in enumerate(module_nav, 1):
        module_id = str(nav_row["label"])
        native = modules_by_source[module_id]
        parent = units_by_id.get(str(native["parent_id"]))
        if parent is None or parent["kind"] not in {"collection", "chapter"}:
            raise ValueError(f"A30 module container drift: {module_id}")
        start_page = int(nav_row["first_page_one_based"])
        module_index.append({
            "ordinal": ordinal,
            "module_id": module_id,
            "module_unit_id": native["id"],
            "parent_unit_id": native["parent_id"],
            "parent_unit_kind": parent["kind"],
            "chapter_unit_id": native["parent_id"] if parent["kind"] == "chapter" else None,
            "source_locator": native["source_locator"],
            "source_sha256": native["source_sha256"],
            "native_record_sha256": native["native_record_sha256"],
            "start_page": start_page,
            "page_span": int(nav_row["pages"]),
            "public_route": _reader_route(start_page),
            "route_precision": "exact_module_start_pdf_page_not_semantic_anchor",
            "exercise_count": exercise_count_by_module[module_id],
            "solution_identity_count": solution_count_by_module[module_id],
            "unsupported_exercise_count": exercise_count_by_module[module_id] - solution_count_by_module[module_id],
            "concept_count": concept_count_by_module[module_id],
            "exercise_pdf_destinations_indexed": False,
            "source_or_target_text_embedded": False,
        })

    module_by_id = {row["module_id"]: row for row in module_index}
    exercise_index: list[dict[str, Any]] = []
    for exercise in sorted(
        exercises.values(),
        key=lambda row: (
            module_by_id[exercise_module[row["id"]]]["ordinal"],
            -1 if row["order"] is None else row["order"],
            row["id"],
        ),
    ):
        exercise_id = exercise["id"]
        problem = problems_by_parent[exercise_id][0]
        solutions = solutions_by_parent.get(exercise_id, [])
        module = module_by_id[exercise_module[exercise_id]]
        exercise_index.append({
            "exercise_id": exercise_id,
            "problem_id": problem["id"],
            "solution_id": solutions[0]["id"] if solutions else None,
            "module_id": module["module_id"],
            "module_unit_id": module["module_unit_id"],
            "chapter_unit_id": module["chapter_unit_id"],
            "native_order": exercise["order"],
            "source_local_id": exercise["source_local_id"],
            "source_locator": exercise["source_locator"],
            "exercise_record_sha256": exercise["native_record_sha256"],
            "problem_record_sha256": problem["native_record_sha256"],
            "solution_record_sha256": solutions[0]["native_record_sha256"] if solutions else None,
            "navigation_scope": "module_identity_only_no_exercise_pdf_destination",
            "source_or_target_text_embedded": False,
        })

    chapters_native = sorted(by_kind["chapter"], key=lambda row: (row["order"], row["id"]))
    chapter_index: list[dict[str, Any]] = []
    for ordinal, chapter in enumerate(chapters_native, 1):
        modules = [row for row in module_index if row["chapter_unit_id"] == chapter["id"]]
        if not modules:
            raise ValueError(f"A30 empty native chapter: {chapter['id']}")
        chapter_index.append({
            "ordinal": ordinal,
            "chapter_unit_id": chapter["id"],
            "native_order": chapter["order"],
            "module_ids": [row["module_id"] for row in modules],
            "module_count": len(modules),
            "start_page": min(row["start_page"] for row in modules),
            "public_route": _reader_route(min(row["start_page"] for row in modules)),
            "exercise_count": sum(row["exercise_count"] for row in modules),
            "solution_identity_count": sum(row["solution_identity_count"] for row in modules),
            "unsupported_exercise_count": sum(row["unsupported_exercise_count"] for row in modules),
            "source_or_target_text_embedded": False,
        })
    collection_modules = [row for row in module_index if row["parent_unit_kind"] == "collection"]
    if [row["module_id"] for row in collection_modules] != ["m50919", "m50414"]:
        raise ValueError("A30 front/back-matter module boundary drift")

    source_lock = _source_lock(native_root, receipt_path, scan)
    learner_map = {
        "schema": "a30-learner-map/1",
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "prerequisite": {
            "course_id": CENTRAL_PREREQUISITE_ID,
            "authority": "central_curriculum_overlay",
            "native_source_assertion": False,
        },
        "indonesian_reader": {
            "kind": "continuous_page_routed_pdf",
            "url": PDF_URL,
            "pdf_pages": EXPECTED_PDF["pages"],
            "bytes": EXPECTED_PDF["bytes"],
            "sha256": EXPECTED_PDF["sha256"],
            "module_page_routes": True,
            "exercise_pdf_destinations_indexed": False,
            "semantic_html": False,
            "mathml": False,
            "pdf_ua_certified": False,
        },
        "front_matter_modules": [collection_modules[0]],
        "chapters": chapter_index,
        "back_matter_modules": [collection_modules[1]],
        "modules": module_index,
        "exercise_identity_count": len(exercise_index),
        "solution_identity_count": len(solutions_by_parent),
        "unsupported_exercise_count": len(exercise_index) - len(solutions_by_parent),
        "source_or_target_text_embedded": False,
        "body_content_embedded": False,
    }
    educator_map = {
        "schema": "a30-educator-map/1",
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "selectable_modules": module_index,
        "front_matter_modules": [collection_modules[0]],
        "chapter_summaries": chapter_index,
        "back_matter_modules": [collection_modules[1]],
        "exercise_index_path": "data/exercise-index.jsonl",
        "concept_index_path": "data/concept-index.jsonl",
        "relation_index_path": "data/pedagogical-relation-index.jsonl",
        "terminology_index_path": "data/terms-index.jsonl",
        "correction_index_path": "data/corrections-index.jsonl",
        "component_rights_index_path": "data/rights-index.jsonl",
        "segment_state_summary_path": "data/segment-state-summary.json",
        "exercise_identity_count": len(exercise_index),
        "solution_identity_count": len(solutions_by_parent),
        "unsupported_exercise_count": len(exercise_index) - len(solutions_by_parent),
        "official_teacher_manual_claimed": False,
        "solution_bodies_embedded": False,
        "source_or_target_text_embedded": False,
        "body_content_embedded": False,
    }
    public_evidence = {
        "schema": "a30-public-evidence/1",
        "course_id": COURSE_ID,
        "verification_mode": receipt["verification_mode"],
        "repository": receipt["repository"],
        "github_release": receipt["github_release"],
        "zenodo": receipt["zenodo"],
        "historical_full_byte_receipts": receipt["historical_full_byte_receipts"],
        "upstream_source": source_lock["upstream_source"],
        "indonesian_reader": learner_map["indonesian_reader"],
        "anonymous_readback": True,
        "credentials_used": False,
    }
    counts = {
        "native_records": 220_680,
        "native_record_entities": scan["record_counts"],
        "units": 26_965,
        "unit_kinds": scan["unit_counts"],
        "chapters": 12,
        "modules": 87,
        "pdf_pages": 3_165,
        "exercises": len(exercise_index),
        "problems": len(problems_by_parent),
        "solution_identities": len(solutions_by_parent),
        "unsupported_exercises": len(exercise_index) - len(solutions_by_parent),
        "concepts": len(scan["concepts"]),
        "terms": len(scan["terms"]),
        "term_decision_statuses": scan["term_decision_statuses"],
        "corrections": len(scan["corrections"]),
        "correction_statuses": scan["correction_statuses"],
        "component_rights": len(scan["rights"]),
        "rights_admission_counts": scan["rights_admission_counts"],
        "segments": scan["segment_summary"]["record_count"],
        "segment_state_counts": scan["segment_summary"]["state_counts"],
        "segment_state_bucket_counts": scan["segment_summary"]["bucket_counts"],
        "relations": len(scan["relations"]),
        "relation_kinds": scan["relation_counts"],
    }
    capabilities = {
        "schema": "a30-capabilities/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "counts": counts,
        "curriculum_graph": {
            "course_id": COURSE_ID,
            "prerequisite_course_ids": [CENTRAL_PREREQUISITE_ID],
            "prerequisite_authority": "central_curriculum_overlay",
            "native_prerequisite_ids": [],
            "native_container_hierarchy_preserved": True,
            "chapter_module_count": 85,
            "collection_level_front_matter_module_count": 1,
            "collection_level_back_matter_module_count": 1,
        },
        "learner_delivery": {
            "module_navigation": True,
            "exercise_problem_identity_index": True,
            "partial_solution_identity_coverage": True,
            "solution_bodies_embedded": False,
            "indonesian_page_based_pdf": True,
            "indonesian_semantic_html": False,
            "exercise_pdf_destinations_indexed": False,
        },
        "educator_delivery": {
            "module_selector": True,
            "exercise_bank_identity_index": True,
            "solution_availability_boundary": True,
            "concept_index": True,
            "terminology_status_index_without_term_text": True,
            "correction_status_index_without_correction_text": True,
            "component_rights_index": True,
            "segment_state_asymmetry_summary": True,
            "official_teacher_manual": False,
        },
        "federation": {
            "whole_public_backend_member_hash_bound": True,
            "stable_native_ids_preserved": True,
            "source_or_target_text_embedded": False,
            "body_content_embedded": False,
            "external_hash_pinned_public_backend_required_for_replay": True,
            "source_companion_required_for_full_replay": True,
            "standalone_raw_replay_claimed": False,
            "reversible_exchange_claimed": False,
        },
        "native_id_sequence_sha256": scan["ledger"]["id_sequence_sha256"],
        "native_record_sequence_sha256": scan["ledger"]["record_sequence_sha256"],
    }
    claim_boundary = {
        "schema": "a30-claim-boundary/1",
        "course_id": COURSE_ID,
        "native_bodies_copied": False,
        "source_segment_text_copied": 0,
        "target_segment_text_copied": 0,
        "term_source_text_copied": 0,
        "term_target_text_copied": 0,
        "correction_source_or_target_text_copied": 0,
        "exercise_or_problem_bodies_copied": 0,
        "solution_bodies_copied": 0,
        "all_exercises_claimed_solved": False,
        "unsupported_exercises_preserved": 3_067,
        "segment_state_asymmetry_preserved": True,
        "native_course_prerequisites_invented": False,
        "central_a20_prerequisite_is_overlay": True,
        "final_derivative_git_revision_claimed": False,
        "indonesian_semantic_html_claimed": False,
        "indonesian_mathml_claimed": False,
        "epub_claimed": False,
        "portable_offline_html_claimed": False,
        "pdf_ua_claimed": False,
        "wcag_conformance_claimed": False,
        "interactive_labs_claimed": False,
        "learning_runtime_claimed": False,
        "official_teacher_manual_claimed": False,
        "exhaustive_exercise_pdf_destinations_claimed": False,
        "standalone_raw_replay_claimed": False,
        "reversible_exchange_claimed": False,
        "public_access_state_changed": False,
        "learner_result_instances": 0,
    }
    return {
        "source_lock": source_lock,
        "native_record_ledger": scan["ledger"],
        "segment_state_summary": scan["segment_summary"],
        "chapter_index": chapter_index,
        "module_index": module_index,
        "exercise_index": exercise_index,
        "concept_index": scan["concepts"],
        "pedagogical_relation_index": scan["relations"],
        "terms_index": scan["terms"],
        "corrections_index": scan["corrections"],
        "rights_index": scan["rights"],
        "learner_map": learner_map,
        "educator_map": educator_map,
        "public_evidence": public_evidence,
        "capabilities": capabilities,
        "claim_boundary": claim_boundary,
    }


def forbidden_content_paths(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key.casefold() in FORBIDDEN_CONTENT_KEYS:
                errors.append(child_path)
            errors.extend(forbidden_content_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(forbidden_content_paths(child, f"{path}[{index}]"))
    return errors


def projection_errors(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    counts = bundle.get("capabilities", {}).get("counts", {})
    modules = bundle.get("module_index", [])
    exercises = bundle.get("exercise_index", [])
    relations = bundle.get("pedagogical_relation_index", [])
    rights = bundle.get("rights_index", [])
    claims = bundle.get("claim_boundary", {})
    public = bundle.get("public_evidence", {})
    ledger = bundle.get("native_record_ledger", {})
    segments = bundle.get("segment_state_summary", {})

    if ledger.get("record_count") != 220_680 or ledger.get("unique_ids") != 220_680:
        errors.append("A30-NATIVE-RECORD-COUNT")
    if ledger.get("id_sequence_sha256") != EXPECTED_ID_SEQUENCE_SHA256 or ledger.get("record_sequence_sha256") != EXPECTED_CANONICAL_SHA256:
        errors.append("A30-NATIVE-SEQUENCE")
    if counts.get("native_record_entities") != EXPECTED_RECORD_COUNTS:
        errors.append("A30-NATIVE-ENTITY-COUNTS")
    if counts.get("unit_kinds") != EXPECTED_UNIT_COUNTS or counts.get("units") != 26_965:
        errors.append("A30-UNIT-COUNTS")
    if counts.get("relation_kinds") != EXPECTED_RELATION_COUNTS or counts.get("relations") != 37_974:
        errors.append("A30-RELATION-COUNTS")
    if len(modules) != 87 or len({row.get("module_id") for row in modules}) != 87:
        errors.append("A30-MODULE-INDEX")
    if [row.get("ordinal") for row in modules] != list(range(1, 88)):
        errors.append("A30-MODULE-ORDER")
    if any(row.get("public_route") != _reader_route(int(row.get("start_page", 0))) for row in modules):
        errors.append("A30-MODULE-ROUTE")
    if any(row.get("exercise_pdf_destinations_indexed") is not False for row in modules):
        errors.append("A30-EXHAUSTIVE-EXERCISE-DESTINATIONS")
    if len(exercises) != 7_250 or len({row.get("exercise_id") for row in exercises}) != 7_250:
        errors.append("A30-EXERCISE-COUNT")
    if len({row.get("problem_id") for row in exercises}) != 7_250:
        errors.append("A30-PROBLEM-BIJECTION")
    solved = [row for row in exercises if row.get("solution_id")]
    if len(solved) != 4_183 or len({row["solution_id"] for row in solved}) != 4_183:
        errors.append("A30-SOLUTION-BOUNDARY")
    if sum(1 for row in exercises if not row.get("solution_id")) != 3_067:
        errors.append("A30-UNSUPPORTED-BOUNDARY")
    if any("public_route" in row or "pdf_destination" in row for row in exercises):
        errors.append("A30-EXHAUSTIVE-EXERCISE-DESTINATIONS")
    relation_counts = dict(sorted(Counter(row.get("relation_type") for row in relations).items()))
    if len(relations) != 37_974 or relation_counts != EXPECTED_RELATION_COUNTS:
        errors.append("A30-RELATION-INDEX")
    if len(rights) != 1_875 or len({row.get("id") for row in rights}) != 1_875:
        errors.append("A30-RIGHTS-FLATTENED")
    if len(bundle.get("concept_index", [])) != 497:
        errors.append("A30-CONCEPT-COUNT")
    if len(bundle.get("terms_index", [])) != 513:
        errors.append("A30-TERM-COUNT")
    if len(bundle.get("corrections_index", [])) != 703:
        errors.append("A30-CORRECTION-COUNT")
    if segments.get("bucket_counts") != EXPECTED_SEGMENT_BUCKET_COUNTS or segments.get("state_counts") != EXPECTED_SEGMENT_STATE_COUNTS or segments.get("asymmetry_preserved") is not True:
        errors.append("A30-SEGMENT-STATE-ASYMMETRY")
    if forbidden_content_paths(bundle):
        errors.append("A30-COPIED-SOURCE-TARGET-BODY")
    if any(claims.get(key) for key in (
        "source_segment_text_copied", "target_segment_text_copied", "term_source_text_copied",
        "term_target_text_copied", "correction_source_or_target_text_copied",
        "exercise_or_problem_bodies_copied", "solution_bodies_copied",
    )) or claims.get("native_bodies_copied"):
        errors.append("A30-COPIED-SOURCE-TARGET-BODY")
    if claims.get("all_exercises_claimed_solved") or claims.get("unsupported_exercises_preserved") != 3_067:
        errors.append("A30-FALSE-SOLUTION-COVERAGE")
    if claims.get("native_course_prerequisites_invented") or not claims.get("central_a20_prerequisite_is_overlay"):
        errors.append("A30-INVENTED-NATIVE-PREREQUISITE")
    if not claims.get("segment_state_asymmetry_preserved"):
        errors.append("A30-SEGMENT-STATE-ASYMMETRY")
    false_claim_keys = (
        "final_derivative_git_revision_claimed",
        "indonesian_semantic_html_claimed",
        "indonesian_mathml_claimed",
        "epub_claimed",
        "portable_offline_html_claimed",
        "pdf_ua_claimed",
        "wcag_conformance_claimed",
        "interactive_labs_claimed",
        "learning_runtime_claimed",
        "official_teacher_manual_claimed",
        "exhaustive_exercise_pdf_destinations_claimed",
        "standalone_raw_replay_claimed",
        "reversible_exchange_claimed",
        "public_access_state_changed",
    )
    for key in false_claim_keys:
        if claims.get(key):
            errors.append(f"A30-FALSE-CLAIM:{key}")
    repository = public.get("repository", {})
    if repository.get("final_derivative_revision_proved") is not False or repository.get("final_derivative_commit") is not None or repository.get("final_derivative_tree") is not None:
        errors.append("A30-FALSE-DERIVATIVE-REVISION")
    if public.get("anonymous_readback") is not True or public.get("credentials_used") is not False:
        errors.append("A30-PUBLIC-EVIDENCE")
    return sorted(set(errors))
