"""Streaming model and invariants for the A20 zero-copy capability adapter."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_NATIVE = PROJECT.parent / "openstax-intermediate-algebra-2e-id"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/a20-capability-v1"
PUBLIC_RECEIPT_PATH = DEFAULT_ADAPTER / "input/public-native-readback.json"
ENGLISH_EVIDENCE_PATH = PROJECT / "docs/interface/evidence/a20-original-english-mirror.json"

COURSE_ID = "A20"
NATIVE_ROLE_ID = "R001"
NATIVE_COURSE_ID = "urn:uuid:ad0b27d0-84f4-5451-92f6-94872587ae53"
CENTRAL_PREREQUISITE_ID = "A10"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"

REPOSITORY = "https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id"
RELEASE_COMMIT = "b293e167477c8fe2e8885c6f6d79d12cbb2e0e89"
RELEASE_TREE = "9ee25a0fa6eb336cbd40f3aa61587797b2bf4f27"
RELEASE_TAG = "v1.0.0"
ZENODO_RECORD_ID = 22229860
ZENODO_CONCEPT_ID = 22060225
UPSTREAM_COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
UPSTREAM_TREE = "7907e4c81d43de1c3b6da173f0eb273c01dc5b55"

NATIVE_EXPORT = Path("backend/exports/interoperability-v0-full")
NATIVE_JSONL = NATIVE_EXPORT / "records.jsonl"
NATIVE_MANIFEST = NATIVE_EXPORT / "manifest.json"
NATIVE_MODULE_INDEX = NATIVE_EXPORT / "module-index.json"
NATIVE_REGISTRY = NATIVE_EXPORT / "registry.json"
NATIVE_ROUNDTRIP = NATIVE_EXPORT / "qa/roundtrip.json"
NATIVE_DEPENDENCY = NATIVE_EXPORT / "qa/dependency-closure.json"
NATIVE_PDF_QA = Path("qa/final-reader/FULL_BOOK_PDF_QA.json")
NATIVE_READER_PINS = Path("publication/final-staging/FINAL_READER_INPUT_PINS.json")
NATIVE_FINAL_BUILD = Path("publication/final-release-1.0.0/FINAL_RELEASE_BUNDLE_BUILD_RECEIPT.json")

PDF_NAME = "openstax-intermediate-algebra-2e-id-ID-1.0.0-reader.pdf"
PDF_URL = f"https://zenodo.org/records/{ZENODO_RECORD_ID}/files/{PDF_NAME}?download=1"
VOLUME_1_NAME = "openstax-intermediate-algebra-2e-id-ID-1.0.0-reader-volume-1.pdf"
VOLUME_2_NAME = "openstax-intermediate-algebra-2e-id-ID-1.0.0-reader-volume-2.pdf"

EXPECTED_RECORD_COUNTS = {
    "artifact": 15,
    "asset": 6478,
    "concept": 236,
    "correction": 1614,
    "course": 1,
    "edition": 1,
    "program": 1,
    "qa_event": 84,
    "relation": 77109,
    "resource": 1,
    "rights": 17,
    "segment": 31502,
    "term": 340,
    "unit": 57136,
}

EXPECTED_UNIT_COUNTS = {
    "book": 1,
    "caption": 21,
    "chapter": 12,
    "definition": 153,
    "entry": 4231,
    "equation": 374,
    "example": 693,
    "exercise": 8209,
    "figure": 55,
    "glossary": 49,
    "item": 1241,
    "list": 569,
    "math": 2,
    "meaning": 153,
    "media": 4006,
    "module": 83,
    "note": 2037,
    "para": 18358,
    "problem": 8209,
    "section": 736,
    "solution": 5238,
    "table": 911,
    "term": 490,
    "title": 1305,
}

EXPECTED_RELATION_COUNTS = {
    "adapts": 2475,
    "contains": 57137,
    "corrects": 2299,
    "defines": 153,
    "has-edition": 1,
    "has-solution": 5238,
    "illustrates": 4006,
    "precedes": 82,
    "solves": 5238,
    "teaches": 83,
    "xref": 397,
}

EXPECTED_ID_SEQUENCE_SHA256 = "2ba7723d09731822a1ab40b91909c05616ef5860e6d53684af30caf2153eacd3"
EXPECTED_JSONL_SHA256 = "f8536e60b6e6fde9855da51e9d1d9037e5772190a1fd2e6ee4189c1f024172d3"
EXPECTED_ENGLISH_EVIDENCE = {
    "bytes": 3336,
    "sha256": "7c259562f1281c10cea1e4ac00ad13e10b41627a83289ff938a8305b0a1bc6b2",
}

SELECTED_UNIT_KINDS = {"book", "chapter", "module", "exercise", "problem", "solution"}
SELECTED_RELATION_PREDICATES = {"contains", "has-solution", "precedes", "solves", "teaches"}

FORBIDDEN_CONTENT_KEYS = {
    "answer_body",
    "body",
    "content",
    "exercise_text",
    "full_text",
    "native_body",
    "prompt",
    "prompt_text",
    "prose",
    "solution_body",
    "solution_text",
    "target_correction",
    "target_text",
    "tex_body",
    "text",
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
    return {
        "path": display_path or path.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_path(path),
    }


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
    rows = []
    for number, raw in enumerate(data.splitlines(), 1):
        if not raw:
            continue
        row = json.loads(raw)
        expected = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if raw != expected:
            raise ValueError(f"Noncanonical JSONL row {number}: {path}")
        rows.append(row)
    return rows


def _row_sha(raw_without_newline: bytes) -> str:
    return sha256_bytes(raw_without_newline)


def _reader_route(page: int) -> str:
    return f"{PDF_URL}#page={page}"


def _project_unit(row: dict[str, Any], raw: bytes) -> dict[str, Any]:
    return {
        "id": row["id"],
        "kind": row["unit_kind"],
        "parent_id": row.get("parent_id"),
        "module_id": row.get("module_id"),
        "order_path": row.get("order_path"),
        "source_local_id": row.get("source_local_id"),
        "source_locator": row.get("source_locator"),
        "title_id_ID": row.get("title_id_ID"),
        "title_source": row.get("title_source"),
        "status": row.get("status"),
        "translation_state": row.get("translation_state"),
        "source_content_sha256": row.get("source_content_sha256"),
        "native_record_sha256": _row_sha(raw.rstrip(b"\n")),
    }


def _project_relation(row: dict[str, Any], raw: bytes) -> dict[str, Any]:
    return {
        "id": row["id"],
        "predicate": row["predicate"],
        "subject_id": row["subject_id"],
        "object_id": row["object_id"],
        "hard": row.get("hard"),
        "qualifier": row.get("qualifier"),
        "status": row.get("status"),
        "native_record_sha256": _row_sha(raw.rstrip(b"\n")),
    }


def _project_concept(row: dict[str, Any], raw: bytes) -> dict[str, Any]:
    return {
        "id": row["id"],
        "canonical_key": row.get("canonical_key"),
        "module_id": row.get("module_id"),
        "unit_ids": row.get("unit_ids", []),
        "label_id_ID": row.get("label_id_ID"),
        "label_source": row.get("label_source"),
        "prerequisite_concept_ids": row.get("prerequisite_concept_ids", []),
        "status": row.get("status"),
        "native_record_sha256": _row_sha(raw.rstrip(b"\n")),
    }


def _project_term(row: dict[str, Any], raw: bytes) -> dict[str, Any]:
    return {
        "id": row["id"],
        "source_local_id": row.get("source_local_id"),
        "source_term": row.get("source_term"),
        "preferred": row.get("preferred"),
        "variants": row.get("variants"),
        "rejected_forms": row.get("rejected_forms"),
        "scope": row.get("scope"),
        "register": row.get("register"),
        "ledger_status": row.get("ledger_status"),
        "record_status": row.get("status"),
        "translation_state": row.get("translation_state"),
        "native_record_sha256": _row_sha(raw.rstrip(b"\n")),
    }


def _project_correction(row: dict[str, Any], raw: bytes) -> dict[str, Any]:
    ledger = row.get("ledger") or {}
    return {
        "id": row["id"],
        "source_local_id": row.get("source_local_id"),
        "source_locator": row.get("source_locator"),
        "module_id": row.get("module_id"),
        "affected_unit_ids": row.get("affected_unit_ids", []),
        "ledger_status": ledger.get("status"),
        "severity": ledger.get("severity"),
        "upstream_report_disposition": row.get("upstream_report_disposition"),
        "record_status": row.get("status"),
        "translation_state": row.get("translation_state"),
        "native_record_sha256": _row_sha(raw.rstrip(b"\n")),
    }


def _project_rights(row: dict[str, Any], raw: bytes) -> dict[str, Any]:
    asset = row.get("asset_rights_manifest") or {}
    return {
        "id": row["id"],
        "source_local_id": row.get("source_local_id"),
        "source_locator": row.get("source_locator"),
        "module_id": row.get("module_id"),
        "record_status": row.get("status"),
        "asset_rights_id": asset.get("asset_rights_id"),
        "source_path": asset.get("source_path"),
        "effective_license": asset.get("effective_license"),
        "rights_basis": asset.get("rights_basis"),
        "release_decision": asset.get("release_decision"),
        "release_credit": asset.get("release_credit"),
        "rights_status": asset.get("status"),
        "asset_sha256": asset.get("sha256"),
        "native_record_sha256": _row_sha(raw.rstrip(b"\n")),
    }


def _scan_native(native_root: Path) -> dict[str, Any]:
    path = native_root / NATIVE_JSONL
    counts: Counter[str] = Counter()
    unit_counts: Counter[str] = Counter()
    relation_counts: Counter[str] = Counter()
    correction_statuses: Counter[str] = Counter()
    term_statuses: Counter[str] = Counter()
    ids: set[str] = set()
    id_digest = hashlib.sha256()
    file_digest = hashlib.sha256()
    type_id_digests: dict[str, Any] = defaultdict(hashlib.sha256)
    type_record_digests: dict[str, Any] = defaultdict(hashlib.sha256)
    type_first: dict[str, str] = {}
    type_last: dict[str, str] = {}
    course_rows = []
    selected_units = []
    concepts = []
    terms = []
    corrections = []
    rights = []
    contains_relations = []
    other_selected_relations = []
    previous_key: tuple[str, str] | None = None

    with path.open("rb") as handle:
        for number, raw in enumerate(handle, 1):
            if not raw.endswith(b"\n"):
                raise ValueError(f"A20 native JSONL row {number} lacks LF termination")
            file_digest.update(raw)
            row = json.loads(raw)
            canonical = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            if raw != canonical + b"\n":
                raise ValueError(f"A20 native JSONL row {number} is not canonical")
            record_type = row["record_type"]
            record_id = row["id"]
            key = (record_type, record_id)
            if previous_key is not None and key < previous_key:
                raise ValueError(f"A20 native record order drift at row {number}")
            previous_key = key
            if record_id in ids:
                raise ValueError(f"A20 duplicate native id: {record_id}")
            ids.add(record_id)
            counts[record_type] += 1
            id_digest.update(record_id.encode("utf-8") + b"\n")
            type_id_digests[record_type].update(record_id.encode("utf-8") + b"\n")
            type_record_digests[record_type].update(raw)
            type_first.setdefault(record_type, record_id)
            type_last[record_type] = record_id

            if record_type == "course":
                course_rows.append(row)
            elif record_type == "unit":
                kind = row["unit_kind"]
                unit_counts[kind] += 1
                if kind in SELECTED_UNIT_KINDS:
                    selected_units.append(_project_unit(row, raw))
            elif record_type == "relation":
                predicate = row["predicate"]
                relation_counts[predicate] += 1
                projected = _project_relation(row, raw)
                if predicate == "contains":
                    contains_relations.append(projected)
                elif predicate in SELECTED_RELATION_PREDICATES:
                    other_selected_relations.append(projected)
            elif record_type == "concept":
                concepts.append(_project_concept(row, raw))
            elif record_type == "term":
                projected = _project_term(row, raw)
                terms.append(projected)
                term_statuses[str(projected["ledger_status"])] += 1
            elif record_type == "correction":
                projected = _project_correction(row, raw)
                corrections.append(projected)
                correction_statuses[str(projected["ledger_status"])] += 1
            elif record_type == "rights":
                rights.append(_project_rights(row, raw))

    if dict(sorted(counts.items())) != EXPECTED_RECORD_COUNTS:
        raise ValueError(f"A20 record-type count drift: {dict(sorted(counts.items()))}")
    if dict(sorted(unit_counts.items())) != EXPECTED_UNIT_COUNTS:
        raise ValueError(f"A20 unit-kind count drift: {dict(sorted(unit_counts.items()))}")
    if dict(sorted(relation_counts.items())) != EXPECTED_RELATION_COUNTS:
        raise ValueError(f"A20 relation count drift: {dict(sorted(relation_counts.items()))}")
    if len(ids) != 174_535 or id_digest.hexdigest() != EXPECTED_ID_SEQUENCE_SHA256:
        raise ValueError("A20 native ID inventory drift")
    if file_digest.hexdigest() != EXPECTED_JSONL_SHA256:
        raise ValueError("A20 canonical JSONL identity drift")
    if len(course_rows) != 1 or course_rows[0]["id"] != NATIVE_COURSE_ID:
        raise ValueError("A20 native course identity drift")
    if course_rows[0].get("prerequisite_course_ids") != []:
        raise ValueError("A20 native source unexpectedly asserts course prerequisites")

    ledger = {
        "schema": "a20-native-record-ledger/1",
        "record_count": len(ids),
        "unique_ids": len(ids),
        "jsonl": identity(path, display_path=NATIVE_JSONL.as_posix()),
        "id_sequence_sha256": id_digest.hexdigest(),
        "record_sequence_sha256": file_digest.hexdigest(),
        "types": [
            {
                "record_type": record_type,
                "count": counts[record_type],
                "first_id": type_first[record_type],
                "last_id": type_last[record_type],
                "id_sequence_sha256": type_id_digests[record_type].hexdigest(),
                "record_sequence_sha256": type_record_digests[record_type].hexdigest(),
            }
            for record_type in sorted(counts)
        ],
    }
    return {
        "ledger": ledger,
        "record_counts": dict(sorted(counts.items())),
        "unit_counts": dict(sorted(unit_counts.items())),
        "relation_counts": dict(sorted(relation_counts.items())),
        "correction_statuses": dict(sorted(correction_statuses.items())),
        "term_statuses": dict(sorted(term_statuses.items())),
        "course": course_rows[0],
        "selected_units": selected_units,
        "contains_relations": contains_relations,
        "other_selected_relations": other_selected_relations,
        "concepts": sorted(concepts, key=lambda row: row["id"]),
        "terms": sorted(terms, key=lambda row: row["id"]),
        "corrections": sorted(corrections, key=lambda row: row["id"]),
        "rights": sorted(rights, key=lambda row: row["id"]),
    }


def _source_lock(native_root: Path, receipt_path: Path) -> dict[str, Any]:
    native_paths = (
        NATIVE_MANIFEST,
        NATIVE_JSONL,
        NATIVE_MODULE_INDEX,
        NATIVE_REGISTRY,
        NATIVE_ROUNDTRIP,
        NATIVE_DEPENDENCY,
        NATIVE_PDF_QA,
        NATIVE_READER_PINS,
        NATIVE_FINAL_BUILD,
        Path("publication/final-release-1.0.0/github-publication-receipt-1.0.0.json"),
        Path("publication/final-release-1.0.0/zenodo-publication-receipt-1.0.0.json"),
        Path("qa/FINAL_COMPLETION_AUDIT_PRIMARY_MIRRORS_20260901.json"),
    )
    inputs = [identity(native_root / relative, display_path=relative.as_posix()) for relative in native_paths]
    inputs.append(identity(receipt_path, display_path="input/public-native-readback.json"))
    inputs.append(
        identity(
            ENGLISH_EVIDENCE_PATH,
            display_path="docs/interface/evidence/a20-original-english-mirror.json",
        )
    )
    return {
        "schema": "a20-capability-source-lock/1",
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "native_export": {
            "schema": "interlanguage.interoperability-v0-full-manifest.v1",
            "record_count": 174_535,
            "jsonl_sha256": EXPECTED_JSONL_SHA256,
        },
        "indonesian_release": {
            "repository": REPOSITORY,
            "commit": RELEASE_COMMIT,
            "tree": RELEASE_TREE,
            "tag": RELEASE_TAG,
            "repository_landing_is_complete_authority": False,
            "complete_authority": "v1.0.0 release assets and exact producer receipts",
        },
        "upstream_source": {
            "repository": "https://github.com/openstax/osbooks-prealgebra-bundle",
            "commit": UPSTREAM_COMMIT,
            "tree": UPSTREAM_TREE,
        },
        "inputs": inputs,
    }


def derive_projection(native_root: Path, receipt_path: Path = PUBLIC_RECEIPT_PATH) -> dict[str, Any]:
    receipt = read_json(receipt_path)
    if receipt.get("state") != "pass" or receipt.get("failures") or not receipt.get("anonymous") or receipt.get("credentials_used"):
        raise ValueError("A20 public-native evidence is not a credential-free pass")
    if receipt.get("repository", {}).get("commit") != RELEASE_COMMIT or receipt.get("repository", {}).get("tree") != RELEASE_TREE:
        raise ValueError("A20 public-native revision drift")
    if receipt.get("github_release", {}).get("total_bytes") != 1_102_054_925:
        raise ValueError("A20 release payload total drift")

    english = read_json(ENGLISH_EVIDENCE_PATH)
    if identity(ENGLISH_EVIDENCE_PATH, display_path="x")["bytes"] != EXPECTED_ENGLISH_EVIDENCE["bytes"] or sha256_path(ENGLISH_EVIDENCE_PATH) != EXPECTED_ENGLISH_EVIDENCE["sha256"]:
        raise ValueError("A20 English mirror evidence drift")
    if english.get("interface_contract", {}).get("translation_claimed") is not False:
        raise ValueError("A20 English mirror must remain a source presentation mirror")

    manifest = read_json(native_root / NATIVE_MANIFEST)
    module_manifest = read_json(native_root / NATIVE_MODULE_INDEX)
    roundtrip = read_json(native_root / NATIVE_ROUNDTRIP)
    dependency = read_json(native_root / NATIVE_DEPENDENCY)
    pdf_qa = read_json(native_root / NATIVE_PDF_QA)
    final_build = read_json(native_root / NATIVE_FINAL_BUILD)
    if manifest.get("record_count") != 174_535 or manifest.get("record_type_counts") != EXPECTED_RECORD_COUNTS:
        raise ValueError("A20 native manifest drift")
    if roundtrip.get("state") != "PASS_LOSSLESS_JSON_JSONL_CSV_REFERENCE_ROUNDTRIP":
        raise ValueError("A20 native round-trip evidence is not passing")
    if dependency.get("state") != "PASS_ALL_83_MODULE_SELECTIONS_HARD_DEPENDENCY_CLOSED":
        raise ValueError("A20 dependency-closure evidence is not passing")
    if final_build.get("coverage") != {"chapters": 12, "complete_book": True, "modules": 83, "pages": 3438}:
        raise ValueError("A20 final release coverage drift")
    if pdf_qa.get("state") != "GO_ALL_PAGE_STRUCTURAL_AND_RASTER_QA":
        raise ValueError("A20 reader QA is not passing")

    scan = _scan_native(native_root)
    selected_units = scan["selected_units"]
    units_by_id = {row["id"]: row for row in selected_units}
    selected_ids = set(units_by_id)
    by_kind: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected_units:
        by_kind[row["kind"]].append(row)

    exercises = {row["id"]: row for row in by_kind["exercise"]}
    problems_by_parent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    solutions_by_parent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in by_kind["problem"]:
        problems_by_parent[str(row["parent_id"])].append(row)
    for row in by_kind["solution"]:
        solutions_by_parent[str(row["parent_id"])].append(row)
    if set(problems_by_parent) != set(exercises) or any(len(rows) != 1 for rows in problems_by_parent.values()):
        raise ValueError("A20 exercise/problem identity closure drift")
    if not set(solutions_by_parent).issubset(exercises) or any(len(rows) != 1 for rows in solutions_by_parent.values()):
        raise ValueError("A20 exercise/solution identity closure drift")

    relations = scan["other_selected_relations"]
    contains = [row for row in scan["contains_relations"] if row["object_id"] in selected_ids]
    relation_by_predicate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in relations:
        relation_by_predicate[row["predicate"]].append(row)
    expected_has_solution = {(exercise_id, rows[0]["id"]) for exercise_id, rows in solutions_by_parent.items()}
    actual_has_solution = {(row["subject_id"], row["object_id"]) for row in relation_by_predicate["has-solution"]}
    if actual_has_solution != expected_has_solution:
        raise ValueError("A20 has-solution relation closure drift")
    # In the native contract, ``solves`` links each solution directly back to
    # its exercise.  The exercise's nested problem remains independently
    # identity-closed above; it is not the object of the ``solves`` edge.
    expected_solves = {
        (solutions_by_parent[exercise_id][0]["id"], exercise_id)
        for exercise_id in solutions_by_parent
    }
    actual_solves = {(row["subject_id"], row["object_id"]) for row in relation_by_predicate["solves"]}
    if actual_solves != expected_solves:
        raise ValueError("A20 solves relation closure drift")
    contains_pairs = {(row["subject_id"], row["object_id"]) for row in contains}
    for row in selected_units:
        if row["parent_id"] is not None and (row["parent_id"], row["id"]) not in contains_pairs:
            raise ValueError(f"A20 selected unit lacks contains relation: {row['id']}")

    module_records = {row["module_id"]: row for row in by_kind["module"]}
    chapter_records = sorted(by_kind["chapter"], key=lambda row: (row["order_path"], row["id"]))
    chapter_by_id = {row["id"]: row for row in chapter_records}
    container_by_id = {row["id"]: row for row in by_kind["book"] + chapter_records}
    module_entries = module_manifest.get("modules", [])
    page_map = pdf_qa.get("structure", {}).get("module_start_pages_1_based", {})
    if len(module_entries) != 83 or len(page_map) != 83:
        raise ValueError("A20 module/page map cardinality drift")

    exercise_count_by_module = Counter(row["module_id"] for row in exercises.values())
    solution_count_by_module = Counter(exercises[exercise_id]["module_id"] for exercise_id in solutions_by_parent)
    concept_count_by_module = Counter(row["module_id"] for row in scan["concepts"])
    module_index = []
    for expected_ordinal, entry in enumerate(module_entries, 1):
        module_id = entry["module_id"]
        native = module_records[module_id]
        if entry["ordinal"] != expected_ordinal or entry["module_unit_id"] != native["id"]:
            raise ValueError(f"A20 module manifest identity/order drift: {module_id}")
        declared_container_id = entry["chapter_unit_id"]
        container = container_by_id.get(declared_container_id)
        if declared_container_id != native["parent_id"] or container is None:
            raise ValueError(f"A20 module/chapter crosswalk drift: {module_id}")
        if container["kind"] not in {"book", "chapter"}:
            raise ValueError(f"A20 module container kind drift: {module_id}")
        page = int(page_map[module_id])
        module_index.append({
            "ordinal": expected_ordinal,
            "module_id": module_id,
            "module_unit_id": native["id"],
            # The producer field is named ``chapter_unit_id``, but its first
            # entry is the book-level Preface.  Preserve that source boundary
            # explicitly instead of pretending all 83 modules are chapters.
            "parent_unit_id": declared_container_id,
            "parent_unit_kind": container["kind"],
            "chapter_unit_id": declared_container_id if container["kind"] == "chapter" else None,
            "title_id_ID": native["title_id_ID"],
            "title_source": native["title_source"],
            "source_locator": native["source_locator"],
            "source_content_sha256": native["source_content_sha256"],
            "native_record_sha256": native["native_record_sha256"],
            "segment_count": entry["segment_count"],
            "start_page": page,
            "public_route": _reader_route(page),
            "route_precision": "exact_pdf_page_fragment_not_semantic_anchor",
            "exercise_count": exercise_count_by_module[module_id],
            "solution_identity_count": solution_count_by_module[module_id],
            "unsolved_exercise_count": exercise_count_by_module[module_id] - solution_count_by_module[module_id],
            "concept_count": concept_count_by_module[module_id],
            "body_content_embedded": False,
        })

    module_by_id = {row["module_id"]: row for row in module_index}
    exercise_index = []
    for exercise in sorted(exercises.values(), key=lambda row: (row["order_path"], row["id"])):
        problem = problems_by_parent[exercise["id"]][0]
        solution_rows = solutions_by_parent.get(exercise["id"], [])
        module = module_by_id[exercise["module_id"]]
        exercise_index.append({
            "exercise_id": exercise["id"],
            "problem_id": problem["id"],
            "solution_id": solution_rows[0]["id"] if solution_rows else None,
            "module_id": exercise["module_id"],
            "module_unit_id": module["module_unit_id"],
            "chapter_unit_id": module["chapter_unit_id"],
            "order_path": exercise["order_path"],
            "source_local_id": exercise["source_local_id"],
            "source_locator": exercise["source_locator"],
            "exercise_record_sha256": exercise["native_record_sha256"],
            "problem_record_sha256": problem["native_record_sha256"],
            "solution_record_sha256": solution_rows[0]["native_record_sha256"] if solution_rows else None,
            "public_route": module["public_route"],
            "route_precision": module["route_precision"],
            "body_content_embedded": False,
        })

    chapters = []
    for ordinal, chapter in enumerate(chapter_records, 1):
        modules = [row for row in module_index if row["chapter_unit_id"] == chapter["id"]]
        chapters.append({
            "ordinal": ordinal,
            "chapter_unit_id": chapter["id"],
            "title_id_ID": chapter["title_id_ID"],
            "title_source": chapter["title_source"],
            "module_ids": [row["module_id"] for row in modules],
            "module_count": len(modules),
            "start_page": min(row["start_page"] for row in modules),
            "public_route": _reader_route(min(row["start_page"] for row in modules)),
            "exercise_count": sum(row["exercise_count"] for row in modules),
            "solution_identity_count": sum(row["solution_identity_count"] for row in modules),
        })
    front_matter_modules = [row for row in module_index if row["parent_unit_kind"] == "book"]
    if len(front_matter_modules) != 1 or front_matter_modules[0]["module_id"] != "m81357":
        raise ValueError("A20 book-level preface module boundary drift")

    selected_relations = sorted(contains + relations, key=lambda row: (row["predicate"], row["id"]))
    selected_relation_counts = dict(sorted(Counter(row["predicate"] for row in selected_relations).items()))
    if selected_relation_counts != {
        # Includes the programme/course container edge into the selected root
        # book as well as every selected descendant unit.
        "contains": 21752,
        "has-solution": 5238,
        "precedes": 82,
        "solves": 5238,
        "teaches": 83,
    }:
        raise ValueError(f"A20 selected pedagogical relation drift: {selected_relation_counts}")

    source_lock = _source_lock(native_root, receipt_path)
    english_mirror = {
        "status": english["status"],
        "work_kind": english["work_kind"],
        "content_language": "en",
        "reader_url": english["program_mirror"]["reader_url"],
        "repository_url": english["program_mirror"]["repository_url"],
        "release_url": english["program_mirror"]["release_url"],
        "offline_zip_url": english["program_mirror"]["offline_zip_url"],
        "offline_zip_bytes": english["program_mirror"]["offline_zip_bytes"],
        "offline_zip_sha256": english["program_mirror"]["offline_zip_sha256"],
        "modules": english["closure"]["modules"],
        "html_files": english["closure"]["html_files"],
        "mathml_expressions": english["closure"]["mathml_expressions"],
        "exercises": english["closure"]["exercises"],
        "solutions": english["closure"]["solutions"],
        "translation_claimed": False,
        "common_adapter_consumption_claimed": False,
    }

    learner_map = {
        "schema": "a20-learner-map/1",
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "prerequisite": {
            "course_id": CENTRAL_PREREQUISITE_ID,
            "authority": "central_curriculum_overlay",
            "native_source_assertion": False,
        },
        "indonesian_reader": {
            "kind": "continuous_untagged_pdf_with_two_tagged_volume_companions",
            "url": PDF_URL,
            "pdf_pages": 3438,
            "sha256": "76276eeab590cd8181fd531378c4b4860bf30289a5e8093c9af5788d1eca3a9c",
            "module_page_routes": True,
            "semantic_html": False,
            "mathml": False,
            "pdf_ua_certified": False,
        },
        "english_source_mirror": english_mirror,
        "front_matter_modules": front_matter_modules,
        "chapters": chapters,
        "modules": module_index,
        "exercise_identity_count": len(exercise_index),
        "solution_identity_count": len(solutions_by_parent),
        "unsolved_exercise_count": len(exercise_index) - len(solutions_by_parent),
        "body_content_embedded": False,
    }
    educator_map = {
        "schema": "a20-educator-map/1",
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "selectable_modules": module_index,
        "front_matter_modules": front_matter_modules,
        "chapter_summaries": chapters,
        "exercise_index_path": "data/exercise-index.jsonl",
        "concept_index_path": "data/concept-index.jsonl",
        "relation_index_path": "data/pedagogical-relation-index.jsonl",
        "terminology_index_path": "data/terms-index.jsonl",
        "correction_index_path": "data/corrections-index.jsonl",
        "component_rights_index_path": "data/rights-index.jsonl",
        "exercise_identity_count": len(exercise_index),
        "solution_identity_count": len(solutions_by_parent),
        "unsolved_exercise_count": len(exercise_index) - len(solutions_by_parent),
        "official_teacher_manual_claimed": False,
        "solution_bodies_embedded": False,
        "body_content_embedded": False,
    }
    public_evidence = {
        "schema": "a20-public-evidence/1",
        "course_id": COURSE_ID,
        "verification_mode": receipt["verification_mode"],
        "repository": receipt["repository"],
        "github_release": receipt["github_release"],
        "zenodo": receipt["zenodo"],
        "historical_full_byte_receipts": receipt["historical_full_byte_receipts"],
        "indonesian_reader": learner_map["indonesian_reader"],
        "english_source_mirror": english_mirror,
        "anonymous_readback": True,
        "credentials_used": False,
    }
    counts = {
        "native_records": 174_535,
        "native_record_types": scan["record_counts"],
        "units": 57_136,
        "unit_kinds": scan["unit_counts"],
        "chapters": 12,
        "modules": 83,
        "pdf_pages": 3438,
        "exercises": len(exercise_index),
        "problems": len(problems_by_parent),
        "solution_identities": len(solutions_by_parent),
        "unsolved_exercises": len(exercise_index) - len(solutions_by_parent),
        "concepts": len(scan["concepts"]),
        "terms": len(scan["terms"]),
        "term_statuses": scan["term_statuses"],
        "corrections": len(scan["corrections"]),
        "correction_statuses": scan["correction_statuses"],
        "component_rights": len(scan["rights"]),
        "relations": 77_109,
        "relation_kinds": scan["relation_counts"],
        "selected_pedagogical_relations": len(selected_relations),
        "selected_pedagogical_relation_kinds": selected_relation_counts,
    }
    capabilities = {
        "schema": "a20-capabilities/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "counts": counts,
        "curriculum_graph": {
            "course_id": COURSE_ID,
            "prerequisite_course_ids": [CENTRAL_PREREQUISITE_ID],
            "prerequisite_authority": "central_curriculum_overlay",
            "native_prerequisite_course_ids": [],
            "native_container_hierarchy_preserved": True,
            "chapter_module_count": 82,
            "book_level_front_matter_module_count": 1,
        },
        "learner_delivery": {
            "module_navigation": True,
            "exercise_problem_identity_navigation": True,
            "partial_solution_identity_coverage": True,
            "solution_bodies_embedded": False,
            "indonesian_page_based_pdf": True,
            "indonesian_semantic_html": False,
            "english_source_html_mirror": True,
        },
        "educator_delivery": {
            "module_selector": True,
            "exercise_bank_identity_index": True,
            "solution_availability_boundary": True,
            "concept_index": True,
            "terminology_index": True,
            "correction_status_index": True,
            "component_rights_index": True,
            "official_teacher_manual": False,
        },
        "federation": {
            "whole_native_backend_hash_bound": True,
            "stable_native_ids_preserved": True,
            "body_content_embedded": False,
            "external_hash_pinned_native_export_required_for_replay": True,
            "reversible_exchange_claimed": False,
        },
        "native_id_sequence_sha256": scan["ledger"]["id_sequence_sha256"],
        "native_record_sequence_sha256": scan["ledger"]["record_sequence_sha256"],
    }
    claim_boundary = {
        "schema": "a20-claim-boundary/1",
        "course_id": COURSE_ID,
        "native_bodies_copied": False,
        "source_segment_text_copied": 0,
        "target_segment_text_copied": 0,
        "exercise_or_problem_bodies_copied": 0,
        "solution_bodies_copied": 0,
        "all_exercises_claimed_solved": False,
        "unsolved_exercises_preserved": 2971,
        "native_course_prerequisites_invented": False,
        "central_a10_prerequisite_is_overlay": True,
        "stale_repository_landing_used_as_complete_authority": False,
        "indonesian_semantic_html_claimed": False,
        "indonesian_mathml_claimed": False,
        "epub_claimed": False,
        "portable_offline_indonesian_html_claimed": False,
        "pdf_ua_claimed": False,
        "wcag_conformance_claimed": False,
        "reversible_exchange_claimed": False,
        "english_source_mirror_translation_claimed": False,
        "english_source_mirror_common_adapter_consumption_claimed": False,
        "official_teacher_manual_claimed": False,
        "public_access_state_changed": False,
        "learner_result_instances": 0,
    }
    return {
        "source_lock": source_lock,
        "native_record_ledger": scan["ledger"],
        "module_index": module_index,
        "exercise_index": exercise_index,
        "concept_index": scan["concepts"],
        "pedagogical_relation_index": selected_relations,
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
    learner = bundle.get("learner_map", {})
    ledger = bundle.get("native_record_ledger", {})

    if ledger.get("record_count") != 174_535 or ledger.get("unique_ids") != 174_535:
        errors.append("A20-NATIVE-RECORD-COUNT")
    if ledger.get("id_sequence_sha256") != EXPECTED_ID_SEQUENCE_SHA256 or ledger.get("record_sequence_sha256") != EXPECTED_JSONL_SHA256:
        errors.append("A20-NATIVE-SEQUENCE")
    if counts.get("native_record_types") != EXPECTED_RECORD_COUNTS:
        errors.append("A20-NATIVE-TYPE-COUNTS")
    if counts.get("unit_kinds") != EXPECTED_UNIT_COUNTS or counts.get("units") != 57_136:
        errors.append("A20-UNIT-COUNTS")
    if counts.get("relation_kinds") != EXPECTED_RELATION_COUNTS:
        errors.append("A20-RELATION-COUNTS")
    if len(modules) != 83 or len({row.get("module_id") for row in modules}) != 83:
        errors.append("A20-MODULE-INDEX")
    if [row.get("ordinal") for row in modules] != list(range(1, 84)):
        errors.append("A20-MODULE-ORDER")
    if any(row.get("public_route") != _reader_route(int(row.get("start_page", 0))) for row in modules):
        errors.append("A20-MODULE-ROUTE")
    if len(exercises) != 8209 or len({row.get("exercise_id") for row in exercises}) != 8209:
        errors.append("A20-EXERCISE-COUNT")
    if len({row.get("problem_id") for row in exercises}) != 8209:
        errors.append("A20-PROBLEM-BIJECTION")
    solved = [row for row in exercises if row.get("solution_id")]
    if len(solved) != 5238 or len({row["solution_id"] for row in solved}) != 5238:
        errors.append("A20-SOLUTION-BOUNDARY")
    if sum(1 for row in exercises if not row.get("solution_id")) != 2971:
        errors.append("A20-UNSOLVED-BOUNDARY")
    relation_counts = dict(sorted(Counter(row.get("predicate") for row in relations).items()))
    if relation_counts != counts.get("selected_pedagogical_relation_kinds"):
        errors.append("A20-PEDAGOGICAL-RELATIONS")
    if len(rights) != 17 or len({row.get("id") for row in rights}) != 17:
        errors.append("A20-RIGHTS-FLATTENED")
    if forbidden_content_paths(bundle):
        errors.append("A20-COPIED-NATIVE-BODY")
    if claims.get("source_segment_text_copied") or claims.get("target_segment_text_copied") or claims.get("exercise_or_problem_bodies_copied") or claims.get("solution_bodies_copied"):
        errors.append("A20-COPIED-NATIVE-BODY")
    if claims.get("all_exercises_claimed_solved") or claims.get("unsolved_exercises_preserved") != 2971:
        errors.append("A20-FALSE-SOLUTION-COVERAGE")
    if claims.get("native_course_prerequisites_invented") or not claims.get("central_a10_prerequisite_is_overlay"):
        errors.append("A20-INVENTED-NATIVE-PREREQUISITE")
    if claims.get("stale_repository_landing_used_as_complete_authority") or public.get("repository", {}).get("landing_readme", {}).get("authority_for_complete_release"):
        errors.append("A20-STALE-LANDING-AUTHORITY")
    for key in (
        "indonesian_semantic_html_claimed",
        "indonesian_mathml_claimed",
        "epub_claimed",
        "portable_offline_indonesian_html_claimed",
        "pdf_ua_claimed",
        "wcag_conformance_claimed",
        "reversible_exchange_claimed",
        "english_source_mirror_translation_claimed",
        "english_source_mirror_common_adapter_consumption_claimed",
        "official_teacher_manual_claimed",
        "public_access_state_changed",
    ):
        if claims.get(key):
            errors.append(f"A20-FALSE-CLAIM:{key}")
    english = learner.get("english_source_mirror", {})
    if english.get("translation_claimed") or english.get("common_adapter_consumption_claimed"):
        errors.append("A20-ENGLISH-MIRROR-BOUNDARY")
    if public.get("anonymous_readback") is not True or public.get("credentials_used") is not False:
        errors.append("A20-PUBLIC-EVIDENCE")
    return sorted(set(errors))
