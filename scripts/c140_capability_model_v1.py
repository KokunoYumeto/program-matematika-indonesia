"""Pure model for the complete C140/C5 zero-copy course capability.

The producer checkout is read-only input.  The projection carries stable
identities, hashes, structure, terminology, corrections, rights, and public
routes; it never copies Penn, Random, companion, exercise, answer, or solution
bodies into the central programme.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_NATIVE = PROJECT.parent / "penn-state-stat-415-id"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/c140-capability-v1"

COURSE_ID = "C140"
NATIVE_ROLE_ID = "O006"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"
BOUNDARY_ID = "C140-C5-54"
NATIVE_FAMILY = "penn_stat415_random_completeness_original_companion"
REPOSITORY = "https://github.com/KokunoYumeto/penn-state-stat-415-id"
PUBLIC_BASE = "https://kokunoyumeto.github.io/penn-state-stat-415-id/"
CONTENT_COMMIT = "40acd8e846a4603ac5a90d311794b7e9c9db7bb9"
PAGES_COMMIT = "903d54c0971d3c14ec8f6fa0961136b881a73b82"
RELEASE_TAG = "v2026.08.31.c140-companion-c5"
RELEASE_ID = 379767406
ZENODO_RECORD_ID = 22208527
ZENODO_CONCEPT_ID = 22077422
ZENODO_DOI = "10.5281/zenodo.22208527"
ZENODO_CONCEPT_DOI = "10.5281/zenodo.22077422"
TRANSLATION_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"

GITHUB_RECEIPT = "00_control/GITHUB_RELEASE_RECEIPT_2026-08-31_C140_COMPANION_C5.json"
PAGES_RECEIPT = "00_control/GITHUB_PAGES_RECEIPT_2026-08-31_C140_COMPANION_C5.json"
ZENODO_RECEIPT = "00_control/ZENODO_PUBLIC_READBACK_2026-08-31_C140_COMPANION_C5.json"

PENN_CATALOGUES = ["backend/first_unit_structures.jsonl"] + [
    f"backend/lesson{number:02d}_source_catalogue.jsonl" for number in range(1, 13)
]
PENN_BINDINGS = ["backend/first_unit_translation_bindings.jsonl"] + [
    f"backend/lesson{number:02d}_translation_bindings.jsonl" for number in range(1, 13)
]

CORE_INPUTS = [
    "00_control/TRANSLATION_LEDGER.csv",
    "00_control/TERMINOLOGY_GLOSSARY_ID_ID.csv",
    "00_control/RIGHTS_AND_COMPONENTS.md",
    "backend/through_lesson12_corrections.jsonl",
    "components/random-completeness/backend/entities.jsonl",
    "components/random-completeness/backend/relations.csv",
    "components/random-completeness/backend/translation_ledger.csv",
    "components/random-completeness/backend/TERMINOLOGY_GLOSSARY_ID_ID.csv",
    "components/random-completeness/backend/adverse_records.jsonl",
    "components/random-completeness/LICENSE_AND_ATTRIBUTION.md",
    "components/c140-companion/backend/documents.jsonl",
    "components/c140-companion/backend/entities.jsonl",
    "components/c140-companion/backend/relations.csv",
    "components/c140-companion/LICENSE.md",
    "components/c140-companion/build/C5_BUILD_RECEIPT.json",
    "components/c140-companion/build/C5_QA_RECEIPT.json",
    GITHUB_RECEIPT,
    PAGES_RECEIPT,
    ZENODO_RECEIPT,
] + PENN_CATALOGUES + PENN_BINDINGS

EXPECTED_COUNTS = {
    "public_documents": 54,
    "penn_documents": 14,
    "random_documents": 1,
    "companion_documents": 39,
    "penn_units": 6510,
    "penn_segments": 4932,
    "penn_math_surfaces": 3156,
    "penn_terms": 192,
    "penn_corrections": 242,
    "random_entities": 325,
    "random_relations": 474,
    "random_terms": 42,
    "random_adverse_records": 19,
    "companion_entities": 1523,
    "companion_relations": 1949,
    "stable_entity_ids": 8358,
    "structural_relations": 2423,
    "terminology_rows": 234,
    "correction_and_adverse_rows": 261,
    "component_rights": 9,
    "companion_solved_problems": 146,
    "companion_rubrics": 62,
    "companion_theory_documents": 13,
    "companion_simulation_documents": 6,
    "companion_mastery_documents": 13,
    "companion_assessment_documents": 4,
    "companion_capstone_documents": 2,
}

FORBIDDEN_CONTENT_KEYS = {
    "answer_body",
    "answer_text",
    "body",
    "book_body",
    "exercise_body",
    "html_body",
    "latex_body",
    "prompt",
    "solution_body",
    "solution_text",
    "source_text",
    "target_text",
}
LOCAL_PROFILE = re.compile(r"(?i)(?:[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\"']+|/(?:home|Users)/[^/\s\"']+)")


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        for row in rows
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path, *, display_path: str | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": display_path or path.as_posix(), "bytes": len(data), "sha256": sha256_bytes(data)}


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, value: Any) -> None:
    write_bytes(path, canonical_json_bytes(value))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"C140 JSONL row {number} is not an object: {path}")
        rows.append(value)
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _input_identity(native_root: Path, relative: str) -> dict[str, Any]:
    return identity(native_root / relative, display_path=relative)


def _safe_pick(row: dict[str, Any], names: Iterable[str]) -> dict[str, Any]:
    return {name: row[name] for name in names if name in row}


def _page_fact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": row["path"],
        "url": row["url"],
        "bytes": int(row["bytes"]),
        "sha256": row["sha256"],
        "http_status": int(row["http_status"]),
        "source": row["source"],
    }


def _rights_index() -> list[dict[str, Any]]:
    return [
        {
            "id": "c140.rights.penn-stat415",
            "component": "penn-stat415",
            "status": "verified",
            "license": "CC-BY-NC-4.0",
            "scope": "Penn State prose and instructional graphics except separately excluded items",
            "evidence_path": "00_control/RIGHTS_AND_COMPONENTS.md",
        },
        {
            "id": "c140.rights.penn-marks-excluded",
            "component": "penn-stat415-excluded-shared-chrome",
            "status": "excluded",
            "license": "NOASSERTION",
            "scope": "Penn State marks, banner, badge, and unnecessary upstream runtime chrome are not redistributed",
            "evidence_path": "00_control/RIGHTS_AND_COMPONENTS.md",
        },
        {
            "id": "c140.rights.random-home-witness",
            "component": "random-completeness",
            "status": "verified-distinct-witness",
            "license": "CC-BY-2.0",
            "scope": "Random landing-page licence witness; not flattened with the Credits witness",
            "evidence_path": "components/random-completeness/LICENSE_AND_ATTRIBUTION.md",
        },
        {
            "id": "c140.rights.random-credits-witness",
            "component": "random-completeness",
            "status": "verified-distinct-witness",
            "license": "CC-BY-1.0",
            "scope": "Random Credits-page licence-link witness; discrepancy remains explicit",
            "evidence_path": "components/random-completeness/LICENSE_AND_ATTRIBUTION.md",
        },
        {
            "id": "c140.rights.mathjax",
            "component": "random-mathjax-runtime",
            "status": "verified",
            "license": "Apache-2.0",
            "scope": "MathJax 3.1.2 runtime",
            "evidence_path": "components/random-completeness/LICENSE_AND_ATTRIBUTION.md",
        },
        {
            "id": "c140.rights.original-companion",
            "component": "c140-original-companion",
            "status": "verified",
            "license": "CC-BY-SA-4.0",
            "scope": "Original companion prose, exercises, solutions, simulations, and repository-original support",
            "evidence_path": "components/c140-companion/LICENSE.md",
        },
        {
            "id": "c140.rights.cp01-dataset",
            "component": "c140-capstone-cp01-dataset",
            "status": "verified",
            "license": "CC-BY-4.0",
            "scope": "Concrete Compressive Strength data and faithful derivatives",
            "evidence_path": "components/c140-companion/LICENSE.md",
        },
        {
            "id": "c140.rights.cp02-dataset",
            "component": "c140-capstone-cp02-dataset",
            "status": "verified",
            "license": "CC0-1.0",
            "scope": "Greater sage-grouse source data and faithful derivatives",
            "evidence_path": "components/c140-companion/LICENSE.md",
        },
        {
            "id": "c140.rights.evidence-witnesses",
            "component": "third-party-rights-and-transport-evidence",
            "status": "preserved-without-relicense",
            "license": "NOASSERTION",
            "scope": "Public rights witnesses, source metadata, and transport evidence retain source terms",
            "evidence_path": "components/c140-companion/LICENSE.md",
        },
    ]


def derive_projection(native_root: Path) -> dict[str, Any]:
    native_root = native_root.resolve()
    ledger = read_csv(native_root / "00_control/TRANSLATION_LEDGER.csv")
    penn_terms = read_csv(native_root / "00_control/TERMINOLOGY_GLOSSARY_ID_ID.csv")
    corrections_native = read_jsonl(native_root / "backend/through_lesson12_corrections.jsonl")
    pages_receipt = read_json(native_root / PAGES_RECEIPT)
    github_receipt = read_json(native_root / GITHUB_RECEIPT)
    zenodo_receipt = read_json(native_root / ZENODO_RECEIPT)

    if len(ledger) != 14 or any(row.get("status") != "complete" for row in ledger):
        raise ValueError("C140 Penn translation ledger is not exactly 14 complete documents")
    if sum(int(row["segments"]) for row in ledger) != EXPECTED_COUNTS["penn_segments"]:
        raise ValueError("C140 Penn segment ledger count drift")
    if sum(int(row["structures"]) for row in ledger) != EXPECTED_COUNTS["penn_units"]:
        raise ValueError("C140 Penn structure ledger count drift")
    if sum(int(row["math_nodes"]) for row in ledger) != EXPECTED_COUNTS["penn_math_surfaces"]:
        raise ValueError("C140 Penn math-surface ledger count drift")

    page_by_path = {str(row["path"]): row for row in pages_receipt["files"]}
    if len(page_by_path) != 259 or pages_receipt.get("status") != "pass" or not pages_receipt.get("anonymous_content_readback"):
        raise ValueError("C140 complete Pages receipt is not the pinned anonymous 259-file pass")

    documents: list[dict[str, Any]] = []
    for row in ledger:
        public_path = "index.html" if row["component_id"] == "index" else f"{row['component_id']}.html"
        public = _page_fact(page_by_path[public_path])
        documents.append({
            "document_id": row["document_id"],
            "component": "penn-stat415",
            "document_type": "course-index" if row["component_id"] == "index" else "lesson",
            "title": "Penn State STAT 415 · pengantar" if row["component_id"] == "index" else f"Penn State STAT 415 · {row['component_id']}",
            "locale": LOCALE,
            "status": "complete",
            "native_source": {
                "path": row["target_path"],
                "bytes": int(row["target_bytes"]),
                "sha256": row["target_sha256"],
            },
            "public_page": public,
            "segments": int(row["segments"]),
            "structures": int(row["structures"]),
            "math_nodes": int(row["math_nodes"]),
        })

    random_ledger = read_csv(native_root / "components/random-completeness/backend/translation_ledger.csv")
    if len(random_ledger) != 1 or random_ledger[0].get("status") != "complete":
        raise ValueError("C140 Random donor ledger is not exactly one complete page")
    random_row = random_ledger[0]
    random_public_path = "components/random-completeness/random/point/Sufficient.html"
    documents.append({
        "document_id": "O006-016-00-0001",
        "component": "random-completeness",
        "document_type": "completeness-donor",
        "title": "Statistik cukup, lengkap, dan aksesori",
        "locale": LOCALE,
        "status": "complete",
        "native_source": {
            "path": f"components/random-completeness/{random_row['target_path']}",
            "bytes": int(random_row["target_bytes"]),
            "sha256": random_row["target_sha256"],
        },
        "public_page": _page_fact(page_by_path[random_public_path]),
    })

    companion_docs_native = read_jsonl(native_root / "components/c140-companion/backend/documents.jsonl")
    if len(companion_docs_native) != 39 or any(row.get("status") != "complete" for row in companion_docs_native):
        raise ValueError("C140 companion is not exactly 39 complete documents")
    for row in companion_docs_native:
        public_path = f"components/c140-companion/{row['output_path']}"
        documents.append({
            "document_id": row["document_id"],
            "component": "c140-original-companion",
            "document_type": row["type"],
            "title": row["title"],
            "locale": LOCALE,
            "status": row["status"],
            "native_source": {
                "path": f"components/c140-companion/{row['source_path']}",
                "bytes": int(row["bytes"]),
                "sha256": row["sha256"],
            },
            "public_page": _page_fact(page_by_path[public_path]),
            "anchors": int(row["anchors"]),
            "references": int(row["references"]),
        })
    document_by_id = {row["document_id"]: row for row in documents}
    if len(document_by_id) != len(documents):
        raise ValueError("C140 document IDs are not unique")

    penn_units: list[dict[str, Any]] = []
    for index, relative in enumerate(PENN_CATALOGUES):
        for row in read_jsonl(native_root / relative):
            if index and row.get("record_type") != "unit":
                continue
            selected = _safe_pick(row, (
                "entity_id", "component_id", "document_id", "ordinal", "tag", "classes",
                "native_id", "native_id_occurrence", "role", "parent_unit_id", "section_id",
                "text_sha256", "translation_status", "source_sha256",
            ))
            selected.update({
                "id": row["entity_id"],
                "component": "penn-stat415",
                "source_file": relative,
                "public_route": document_by_id[row["document_id"]]["public_page"]["url"],
                "route_precision": "document-context",
            })
            penn_units.append(selected)

    penn_segments: list[dict[str, Any]] = []
    for relative in PENN_BINDINGS:
        for row in read_jsonl(native_root / relative):
            selected = _safe_pick(row, (
                "segment_id", "component_id", "document_id", "ordinal", "section_id", "locale",
                "source_sha256", "target_sha256", "status", "translation_provenance",
            ))
            selected.update({"id": row["segment_id"], "component": "penn-stat415", "source_file": relative})
            penn_segments.append(selected)

    penn_corrections = []
    for row in corrections_native:
        selected = _safe_pick(row, (
            "correction_id", "status", "surface", "surfaces", "replacement_count", "document_id",
            "math_id", "unit_id", "asset_id", "selector", "source_defect_id", "source_surface_sha256",
            "target_surface_sha256", "source_unit_sha256", "target_unit_sha256", "protected_math_ids",
            "removed_unit_ids", "application_layer",
        ))
        selected.update({"id": row["correction_id"], "component": "penn-stat415"})
        penn_corrections.append(selected)
    penn_term_index = [
        {"id": row["term_id"], "component": "penn-stat415", "en_US": row["en_US"], "id_ID": row["id_ID"], "decision": row["decision"]}
        for row in penn_terms
    ]

    random_entities_native = read_jsonl(native_root / "components/random-completeness/backend/entities.jsonl")
    random_entities = []
    for row in random_entities_native:
        selected = {key: value for key, value in row.items() if key != "source_text"}
        selected["id"] = row["entity_id"]
        selected["component"] = "random-completeness"
        selected["public_route"] = document_by_id["O006-016-00-0001"]["public_page"]["url"]
        selected["route_precision"] = "document-context"
        random_entities.append(selected)
    random_relations = read_csv(native_root / "components/random-completeness/backend/relations.csv")
    random_terms_native = read_csv(native_root / "components/random-completeness/backend/TERMINOLOGY_GLOSSARY_ID_ID.csv")
    random_terms = [{"id": row["term_id"], "component": "random-completeness", **row} for row in random_terms_native]
    random_adverse = [
        _safe_pick(row, ("id", "status", "kind", "source", "target"))
        for row in read_jsonl(native_root / "components/random-completeness/backend/adverse_records.jsonl")
    ]

    companion_entities_native = read_jsonl(native_root / "components/c140-companion/backend/entities.jsonl")
    companion_entities: list[dict[str, Any]] = []
    for row in companion_entities_native:
        selected = dict(row)
        selected["id"] = row["entity_id"]
        selected["component"] = "c140-original-companion"
        if row.get("document_id") in document_by_id:
            base_route = document_by_id[row["document_id"]]["public_page"]["url"]
            selected["public_route"] = f"{base_route}#{row['entity_id']}"
            selected["route_precision"] = "stable-native-anchor"
        else:
            selected["public_route"] = document_by_id["O006-C140-CMP-INDEX"]["public_page"]["url"]
            selected["route_precision"] = "component-index-context"
        companion_entities.append(selected)
    companion_relations = read_csv(native_root / "components/c140-companion/backend/relations.csv")

    rights_index = _rights_index()
    problem_rows = [row for row in companion_entities if row.get("entity_type") == "p"]
    rubric_rows = [row for row in companion_entities if row.get("entity_type") == "rub"]
    type_counts = Counter(row["document_type"] for row in documents if row["component"] == "c140-original-companion")

    counts = {
        "public_documents": len(documents),
        "penn_documents": sum(row["component"] == "penn-stat415" for row in documents),
        "random_documents": sum(row["component"] == "random-completeness" for row in documents),
        "companion_documents": sum(row["component"] == "c140-original-companion" for row in documents),
        "penn_units": len(penn_units),
        "penn_segments": len(penn_segments),
        "penn_math_surfaces": sum(int(row["math_nodes"]) for row in ledger),
        "penn_terms": len(penn_term_index),
        "penn_corrections": len(penn_corrections),
        "random_entities": len(random_entities),
        "random_relations": len(random_relations),
        "random_terms": len(random_terms),
        "random_adverse_records": len(random_adverse),
        "companion_entities": len(companion_entities),
        "companion_relations": len(companion_relations),
        "stable_entity_ids": len(penn_units) + len(random_entities) + len(companion_entities),
        "structural_relations": len(random_relations) + len(companion_relations),
        "terminology_rows": len(penn_term_index) + len(random_terms),
        "correction_and_adverse_rows": len(penn_corrections) + len(random_adverse),
        "component_rights": len(rights_index),
        "companion_solved_problems": len(problem_rows),
        "companion_rubrics": len(rubric_rows),
        "companion_theory_documents": type_counts["theory"],
        "companion_simulation_documents": type_counts["simulation"],
        "companion_mastery_documents": type_counts["mastery"],
        "companion_assessment_documents": type_counts["assessment"],
        "companion_capstone_documents": type_counts["capstone"],
    }

    public_files = github_receipt.get("public", {}).get("files", [])
    github_pdf = next(row for row in public_files if row["name"] == "00_00_stat415-pengantar-statistika-matematis-id.pdf")
    github_epub = next(row for row in public_files if row["name"] == "00_01_stat415-pengantar-statistika-matematis-id.epub")
    c5_backend = next(row for row in public_files if row["name"] == "16_C140_COMPANION_C5_SOURCE_BACKEND_DATA_RIGHTS.zip")
    public_evidence = {
        "schema": "c140-public-evidence/1",
        "status": "pass",
        "repository": {
            "url": REPOSITORY,
            "content_commit": CONTENT_COMMIT,
            "release_tag": RELEASE_TAG,
            "release_id": RELEASE_ID,
            "release_url": github_receipt["public"]["url"],
            "file_count": int(github_receipt["public"]["file_count"]),
            "total_bytes": int(github_receipt["public"]["total_bytes"]),
            "anonymous_asset_readback": bool(github_receipt["public"]["public_asset_readback_anonymous"]),
        },
        "pages": {
            "base_url": PUBLIC_BASE,
            "source_commit": CONTENT_COMMIT,
            "deployment_commit": PAGES_COMMIT,
            "workflow_run_id": int(pages_receipt["control_plane"]["workflow_run_id"]),
            "collection_files": int(pages_receipt["collection"]["files"]),
            "collection_bytes": int(pages_receipt["collection"]["bytes"]),
            "anonymous_readback": bool(pages_receipt["anonymous_content_readback"]),
            "course_document_files": [_page_fact(page_by_path[row["public_page"]["path"]]) for row in documents],
        },
        "zenodo": {
            "record_id": ZENODO_RECORD_ID,
            "record_url": f"https://zenodo.org/records/{ZENODO_RECORD_ID}",
            "doi": ZENODO_DOI,
            "concept_id": ZENODO_CONCEPT_ID,
            "concept_doi": ZENODO_CONCEPT_DOI,
            "access_right": "open",
            "file_count": int(zenodo_receipt["public"]["file_count"]),
            "total_bytes": int(zenodo_receipt["public"]["total_bytes"]),
            "anonymous_readback": bool(zenodo_receipt["public"]["anonymous_readback"]),
        },
        "reader": {
            "primary_pdf": _safe_pick(github_pdf, ("name", "download_url", "bytes", "sha256", "http_status")),
            "epub": _safe_pick(github_epub, ("name", "download_url", "bytes", "sha256", "http_status")),
            "complete_c5_backend": _safe_pick(c5_backend, ("name", "download_url", "bytes", "sha256", "http_status")),
            "native_html_document_count": len(documents),
            "single_uniform_pdf_for_all_components_claimed": False,
        },
        "translation_provenance": TRANSLATION_PROVENANCE,
    }

    source_paths = set(CORE_INPUTS)
    source_paths.update(row["native_source"]["path"] for row in documents)
    source_lock = {
        "schema": "c140-source-lock/1",
        "course_id": COURSE_ID,
        "boundary_id": BOUNDARY_ID,
        "repository": REPOSITORY,
        "public_content_commit": CONTENT_COMMIT,
        "public_pages_commit": PAGES_COMMIT,
        "release_tag": RELEASE_TAG,
        "inputs": [_input_identity(native_root, relative) for relative in sorted(source_paths)],
    }
    source_lock["input_count"] = len(source_lock["inputs"])

    component_groups = {
        "penn_spine": [row for row in documents if row["component"] == "penn-stat415"],
        "random_completeness": [row for row in documents if row["component"] == "random-completeness"],
        "companion_index": [row for row in documents if row["document_type"] == "index"],
        "companion_theory": [row for row in documents if row["document_type"] == "theory"],
        "companion_simulations": [row for row in documents if row["document_type"] == "simulation"],
        "companion_mastery": [row for row in documents if row["document_type"] == "mastery"],
        "companion_assessments": [row for row in documents if row["document_type"] == "assessment"],
        "companion_capstones": [row for row in documents if row["document_type"] == "capstone"],
    }
    learner_map = {
        "schema": "c140-learner-map/1",
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "boundary_id": BOUNDARY_ID,
        "central_prerequisite_overlay": ["B40", "B90", "B95", "C10"],
        "public_home": PUBLIC_BASE,
        "components": component_groups,
        "document_count": len(documents),
        "selection_guidance": [
            "Gunakan tulang punggung Penn untuk urutan kuliah utama.",
            "Gunakan donor Random untuk kecukupan dan kelengkapan.",
            "Gunakan teori, simulasi, set penguasaan, asesmen, dan capstone pendamping untuk latihan dan pendalaman.",
        ],
    }
    educator_map = {
        "schema": "c140-educator-map/1",
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "boundary_id": BOUNDARY_ID,
        "documents": documents,
        "solved_problems": [
            _safe_pick(row, ("id", "document_id", "entity_type", "title", "public_route", "route_precision"))
            for row in problem_rows
        ],
        "rubrics": [
            _safe_pick(row, ("id", "document_id", "entity_type", "title", "public_route", "route_precision"))
            for row in rubric_rows
        ],
        "simulations": component_groups["companion_simulations"],
        "assessments": component_groups["companion_assessments"],
        "capstones": component_groups["companion_capstones"],
        "governance": {
            "penn_units": "data/penn-unit-index.jsonl",
            "penn_segments": "data/penn-segment-index.jsonl",
            "penn_terms": "data/penn-terms-index.jsonl",
            "penn_corrections": "data/penn-corrections-index.jsonl",
            "random_entities": "data/random-entity-index.jsonl",
            "random_relations": "data/random-relation-index.jsonl",
            "random_terms": "data/random-terms-index.jsonl",
            "random_adverse": "data/random-adverse-index.jsonl",
            "companion_entities": "data/companion-entity-index.jsonl",
            "companion_relations": "data/companion-relation-index.jsonl",
            "component_rights": "data/rights-index.jsonl",
        },
    }
    claim_boundary = {
        "schema": "c140-claim-boundary/1",
        "course_id": COURSE_ID,
        "boundary_id": BOUNDARY_ID,
        "whole_course_component_boundary_proven": True,
        "public_documents": 54,
        "component_count": 3,
        "native_html_available": True,
        "central_html_reauthors_native_content": False,
        "native_bodies_copied": 0,
        "source_text_copied": 0,
        "exercise_answer_or_solution_bodies_copied": 0,
        "fully_solved_problem_identities": 146,
        "component_rights_flattened": False,
        "uniform_license_claimed": False,
        "single_uniform_pdf_claimed": False,
        "wcag_conformance_claimed": False,
        "pdf_ua_claimed": False,
        "reversible_content_exchange_claimed": False,
        "public_access_state_changed": False,
    }
    capabilities = {
        "schema": CONTRACT,
        "course_id": COURSE_ID,
        "boundary_id": BOUNDARY_ID,
        "native_family": NATIVE_FAMILY,
        "locale": LOCALE,
        "status": "verified",
        "counts": counts,
        "features": {
            "unit_identity": "verified",
            "translation_ledger": "verified",
            "terminology": "verified",
            "corrections": "verified",
            "component_rights": "verified-distinct",
            "learner_navigation": "verified",
            "educator_unit_alignment": "verified",
            "deterministic_projection": "verified",
            "native_html_delivery": "verified",
            "native_body_centralization": "not-performed",
        },
        "views": {"learner": "views/C140.html", "educator": "views/C140-pengajar.html"},
    }
    bundle = {
        "documents": documents,
        "penn_units": penn_units,
        "penn_segments": penn_segments,
        "penn_terms": penn_term_index,
        "penn_corrections": penn_corrections,
        "random_entities": random_entities,
        "random_relations": random_relations,
        "random_terms": random_terms,
        "random_adverse": random_adverse,
        "companion_entities": companion_entities,
        "companion_relations": companion_relations,
        "rights_index": rights_index,
        "source_lock": source_lock,
        "public_evidence": public_evidence,
        "learner_map": learner_map,
        "educator_map": educator_map,
        "claim_boundary": claim_boundary,
        "capabilities": capabilities,
    }
    errors = projection_errors(bundle)
    if errors:
        raise ValueError(f"C140 projection failures: {errors}")
    return bundle


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
    if counts != EXPECTED_COUNTS:
        errors.append("C140-COUNTS")
    documents = bundle.get("documents", [])
    document_ids = [row.get("document_id") for row in documents]
    routes = [row.get("public_page", {}).get("url") for row in documents]
    if len(documents) != 54 or len(set(document_ids)) != 54 or len(set(routes)) != 54:
        errors.append("C140-DOCUMENT-CLOSURE")
    if any(row.get("status") != "complete" or row.get("public_page", {}).get("http_status") != 200 for row in documents):
        errors.append("C140-DOCUMENT-STATE")
    for key, expected in (("penn_units", 6510), ("random_entities", 325), ("companion_entities", 1523)):
        ids = [row.get("id") for row in bundle.get(key, [])]
        if len(ids) != expected or len(set(ids)) != expected:
            errors.append(f"C140-{key.upper()}-IDENTITIES")
    all_entity_ids = [row["id"] for key in ("penn_units", "random_entities", "companion_entities") for row in bundle.get(key, [])]
    if len(all_entity_ids) != 8358 or len(set(all_entity_ids)) != 8358:
        errors.append("C140-GLOBAL-ENTITY-IDENTITIES")
    if len({row.get("id") for row in bundle.get("penn_segments", [])}) != 4932:
        errors.append("C140-PENN-SEGMENT-IDENTITIES")
    if len({row.get("id") for row in bundle.get("penn_corrections", [])}) != 242:
        errors.append("C140-PENN-CORRECTION-IDENTITIES")
    if len({row.get("id") for row in bundle.get("penn_terms", [])}) != 192:
        errors.append("C140-PENN-TERM-IDENTITIES")
    if len({row.get("id") for row in bundle.get("random_terms", [])}) != 42:
        errors.append("C140-RANDOM-TERM-IDENTITIES")
    rights = bundle.get("rights_index", [])
    if len(rights) != 9 or len({row.get("id") for row in rights}) != 9:
        errors.append("C140-RIGHTS-COUNT")
    if {row.get("license") for row in rights if row.get("component") == "random-completeness"} != {"CC-BY-1.0", "CC-BY-2.0"}:
        errors.append("C140-RANDOM-RIGHTS-DISCREPANCY")
    claims = bundle.get("claim_boundary", {})
    false_claims = (
        "central_html_reauthors_native_content", "component_rights_flattened", "uniform_license_claimed",
        "single_uniform_pdf_claimed", "wcag_conformance_claimed", "pdf_ua_claimed",
        "reversible_content_exchange_claimed", "public_access_state_changed",
    )
    if any(claims.get(key) is not False for key in false_claims):
        errors.append("C140-CLAIM-BOUNDARY")
    if any(claims.get(key) != 0 for key in ("native_bodies_copied", "source_text_copied", "exercise_answer_or_solution_bodies_copied")):
        errors.append("C140-COPIED-NATIVE-BODY")
    public = bundle.get("public_evidence", {})
    if public.get("status") != "pass" or public.get("zenodo", {}).get("access_right") != "open":
        errors.append("C140-PUBLIC-ACCESS")
    if not public.get("repository", {}).get("anonymous_asset_readback") or not public.get("pages", {}).get("anonymous_readback") or not public.get("zenodo", {}).get("anonymous_readback"):
        errors.append("C140-PUBLIC-READBACK")
    if len(public.get("pages", {}).get("course_document_files", [])) != 54:
        errors.append("C140-PUBLIC-ROUTES")
    if forbidden_content_paths(bundle):
        errors.append("C140-FORBIDDEN-CONTENT-KEY")
    encoded = canonical_json_bytes(bundle).decode("utf-8")
    if LOCAL_PROFILE.search(encoded):
        errors.append("C140-LOCAL-PROFILE")
    return sorted(set(errors))
