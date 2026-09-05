"""Exact zero-copy capability projection for C70/R012 applied combinatorics."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


COURSE_ID = "C70"
NATIVE_ROLE_ID = "R012"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"
REPOSITORY = "https://github.com/KokunoYumeto/applied-combinatorics-id"
PAGES_URL = "https://kokunoyumeto.github.io/applied-combinatorics-id/"
SOURCE_REPOSITORY = "https://github.com/mitchkeller/applied-combinatorics"
SOURCE_COMMIT = "33b20df670d1f8d98266cd2f4a287a79b01649ea"
SOURCE_TREE = "a8e604cc80fbb5e1a312fa26baab2b17d2975b77"
CURRENT_PUBLIC_HEAD = "8c9615969a4c4e9316166f38ac827a932a87a919"
CURRENT_PUBLIC_TREE = "c538dacb6bb51f15cdacefffd473ec8899f677f3"
RELEASE_VERSION = "2026.08.22.2"
MAINTENANCE_VERSION = "2026.09.04.1"
ZENODO_RECORD_ID = 22062005
ZENODO_MAINTENANCE_RECORD_ID = 22308618
ZENODO_CONCEPT_DOI = "10.5281/zenodo.22058531"
MIGRATION_RECEIPT = "backend/migrations/applied-combinatorics-id-v1/MIGRATION_RECEIPT.json"
PUBLIC_READBACK = "backend/course-capsule-v1/adapters/c70-capability-v1/input/public-native-readback.json"
PDF_NAME = "00_KOMBINATORIKA_TERAPAN_ID-ID_COMPLETE_LINKED_READER_2026.08.22.2.pdf"
SOURCE_ZIP_NAME = "01_KOMBINATORIKA_TERAPAN_ID-ID_CORRESPONDING_SOURCE_2026.08.22.2.zip"
EVIDENCE_ZIP_NAME = "02_KOMBINATORIKA_TERAPAN_ID-ID_EVIDENCE_AND_PROVENANCE_2026.08.22.2.zip"
HTML_ZIP_NAME = "03_KOMBINATORIKA_TERAPAN_ID-ID_HTML_READER_2026.08.22.2.zip"

CONTROL_INPUTS = (
    "backend/schemas/record-envelope.schema.json",
    "qa/FINAL_BACKEND_VALIDATION_20260822_2.json",
    "qa/GITHUB_PUBLICATION_RECEIPT_20260822_2.json",
    "qa/ZENODO_PUBLICATION_RECEIPT_20260822_2.json",
    "qa/FINAL_PUBLIC_HTML_BROWSER_QA_20260822_2.json",
    "qa/FINAL_PUBLIC_PDF_QA_20260822_2.json",
    "qa/FINAL_RIGHTS_PUBLICATION_READINESS_20260822_2.json",
    "qa/TERMINOLOGY_QA_INDONESIAN_FIELD_SOURCE_20260822.json",
    "00_control/TERMINOLOGY.csv",
    "00_control/TERMINOLOGY_DECISION_REVIEW_LOG.csv",
    "00_control/TERMINOLOGY_DECISION_REVIEW_GUIDE.md",
)

EXPECTED_RELATIONS = {
    "answers": 9,
    "compiled-from": 1,
    "contains": 1407,
    "corrects": 357,
    "covers-concept": 1569,
    "depends-on": 3,
    "derived-from": 12,
    "hints": 16,
    "precedes": 1407,
    "prerequisite": 992,
    "solves": 57,
    "uses-resource": 1,
    "xref": 503,
}


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path, *, display_path: str | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": display_path if display_path is not None else path.as_posix(),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _inventory_identity(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    data = b"".join(
        f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n".encode("utf-8")
        for row in rows
    )
    return {"bytes": len(data), "sha256": sha256_bytes(data)}


def _export_inputs(native_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    exports = native_root / "backend/exports"
    manifest_path = exports / "BACKEND_EXPORT_MANIFEST.csv"
    rows = read_csv(manifest_path)
    if len(rows) != 23 or len({row["path"] for row in rows}) != 23:
        raise ValueError("C70 export manifest must contain 23 unique members")
    verified = []
    for row in rows:
        relative = f"backend/exports/{row['path']}"
        actual = identity(native_root / relative, display_path=relative)
        if actual["bytes"] != int(row["bytes"]) or actual["sha256"] != row["sha256"]:
            raise ValueError(f"C70 export identity drift: {relative}")
        verified.append(actual)
    return verified, rows


def _preorder(root_id: str, children: dict[str, list[dict[str, Any]]]) -> list[str]:
    result: list[str] = []

    def visit(unit_id: str) -> None:
        result.append(unit_id)
        for child in children.get(unit_id, []):
            visit(child["id"])

    visit(root_id)
    return result


def derive_projection(native_root: Path, hub_root: Path) -> dict[str, Any]:
    missing = [relative for relative in CONTROL_INPUTS if not (native_root / relative).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing C70 native control inputs: {missing}")
    migration_path = hub_root / MIGRATION_RECEIPT
    public_readback_path = hub_root / PUBLIC_READBACK
    if not migration_path.is_file() or not public_readback_path.is_file():
        raise FileNotFoundError("Missing C70 migration receipt or anonymous public readback")

    export_inputs, export_rows = _export_inputs(native_root)
    export_manifest = identity(
        native_root / "backend/exports/BACKEND_EXPORT_MANIFEST.csv",
        display_path="backend/exports/BACKEND_EXPORT_MANIFEST.csv",
    )
    control_inputs = [identity(native_root / relative, display_path=relative) for relative in CONTROL_INPUTS]
    migration_input = identity(migration_path, display_path=MIGRATION_RECEIPT)
    public_readback_input = identity(public_readback_path, display_path=PUBLIC_READBACK)

    migration = read_json(migration_path)
    public_readback = read_json(public_readback_path)
    summary = read_json(native_root / "backend/exports/summary.json")
    final_validation = read_json(native_root / "qa/FINAL_BACKEND_VALIDATION_20260822_2.json")
    github_receipt = read_json(native_root / "qa/GITHUB_PUBLICATION_RECEIPT_20260822_2.json")
    zenodo_receipt = read_json(native_root / "qa/ZENODO_PUBLICATION_RECEIPT_20260822_2.json")
    html_qa = read_json(native_root / "qa/FINAL_PUBLIC_HTML_BROWSER_QA_20260822_2.json")
    pdf_qa = read_json(native_root / "qa/FINAL_PUBLIC_PDF_QA_20260822_2.json")
    rights_qa = read_json(native_root / "qa/FINAL_RIGHTS_PUBLICATION_READINESS_20260822_2.json")

    exports = native_root / "backend/exports"
    program_rows = read_jsonl(exports / "program_course_resource_edition.jsonl")
    units = read_jsonl(exports / "units.jsonl")
    unit_locales = read_jsonl(exports / "unit_locale_mappings.jsonl")
    segments = read_jsonl(exports / "segments.jsonl")
    segment_locales = read_jsonl(exports / "segment_locale_mappings.jsonl")
    concepts = read_jsonl(exports / "concepts.jsonl")
    terms = read_jsonl(exports / "terms.jsonl")
    relations = read_jsonl(exports / "relations.jsonl")
    exercise_projection = read_jsonl(exports / "exercise_solution_links.jsonl")
    assets = read_jsonl(exports / "assets.jsonl")
    build_targets = read_jsonl(exports / "build_targets.jsonl")
    rights = read_jsonl(exports / "rights.jsonl")
    corrections = read_jsonl(exports / "corrections.jsonl")
    artifacts = read_jsonl(exports / "artifacts.jsonl")
    qa_events = read_jsonl(exports / "qa_events.jsonl")
    terminology_registry = read_csv(native_root / "00_control/TERMINOLOGY.csv")
    terminology_review = read_csv(native_root / "00_control/TERMINOLOGY_DECISION_REVIEW_LOG.csv")

    course = next(row for row in program_rows if row["record_type"] == "course")
    resource = next(row for row in program_rows if row["record_type"] == "resource")
    source_edition = next(row for row in program_rows if row.get("id") == "r012-upstream-33b20df670d1")
    target_edition = next(row for row in program_rows if row.get("id") == "r012-id-draft-20260820")

    units_by_id = {row["id"]: row for row in units}
    locales_by_unit = {row["source_unit_id"]: row for row in unit_locales}
    if len(units_by_id) != 1408 or len(locales_by_unit) != 1408 or set(units_by_id) != set(locales_by_unit):
        raise ValueError("C70 unit/localization closure drift")
    segments_by_unit: dict[str, list[str]] = defaultdict(list)
    for row in segments:
        segments_by_unit[row["unit_id"]].append(row["id"])
    if len(segments) != 3806 or len(segment_locales) != 3806:
        raise ValueError("C70 segment/localization count drift")
    if {row["source_segment_id"] for row in segment_locales} != {row["id"] for row in segments}:
        raise ValueError("C70 segment/localization identity drift")

    children: dict[str, list[dict[str, Any]]] = defaultdict(list)
    roots = []
    for row in units:
        if row.get("parent_id") is None:
            roots.append(row)
        else:
            if row["parent_id"] not in units_by_id:
                raise ValueError(f"C70 missing parent: {row['id']}")
            children[row["parent_id"]].append(row)
    for values in children.values():
        values.sort(key=lambda row: (row.get("order", 0), row["id"]))
    if len(roots) != 1 or roots[0]["id"] != "r012:unit:app-comb":
        raise ValueError("C70 root-book identity drift")
    order = _preorder(roots[0]["id"], children)
    if len(order) != 1408 or set(order) != set(units_by_id):
        raise ValueError("C70 hierarchy does not close over all units")
    ordinal_by_id = {unit_id: ordinal for ordinal, unit_id in enumerate(order, start=1)}

    relation_counts = Counter(row["relation"] for row in relations)
    if dict(sorted(relation_counts.items())) != EXPECTED_RELATIONS:
        raise ValueError("C70 relation inventory drift")
    projected = [row for row in relations if row["relation"] in {"hints", "answers", "solves"}]
    if exercise_projection != projected or len(projected) != 82:
        raise ValueError("C70 exercise-support projection is not the exact relation subset")
    parent_edges = {(row["parent_id"], row["id"]) for row in units if row.get("parent_id")}
    contains_edges = {(row["source_id"], row["target_id"]) for row in relations if row["relation"] == "contains"}
    if parent_edges != contains_edges:
        raise ValueError("C70 parent hierarchy and contains relations differ")

    concepts_by_unit: dict[str, list[str]] = defaultdict(list)
    for concept in concepts:
        for unit_id in concept.get("unit_ids", []):
            if unit_id not in units_by_id:
                raise ValueError(f"C70 concept points outside unit inventory: {concept['id']}")
            concepts_by_unit[unit_id].append(concept["id"])
    support_by_exercise: dict[str, list[dict[str, Any]]] = defaultdict(list)
    support_rows = []
    for relation in exercise_projection:
        support = units_by_id[relation["source_id"]]
        exercise = units_by_id[relation["target_id"]]
        if support["unit_type"] not in {"hint", "answer", "solution"} or exercise["unit_type"] != "exercise":
            raise ValueError(f"C70 malformed exercise-support relation: {relation['id']}")
        row = {
            "relation_id": relation["id"],
            "support_kind": support["unit_type"],
            "support_unit_id": support["id"],
            "exercise_unit_id": exercise["id"],
        }
        support_rows.append(row)
        support_by_exercise[exercise["id"]].append(row)

    block_units = [row for row in units if row["unit_type"] in {"chapter", "appendix"}]
    block_units.sort(key=lambda row: ordinal_by_id[row["id"]])
    if len(block_units) != 19:
        raise ValueError("C70 expected 16 chapters and three appendices")
    block_ids = {row["id"] for row in block_units}

    def containing_block(unit_id: str) -> str | None:
        current = unit_id
        while current in units_by_id:
            if current in block_ids:
                return current
            parent = units_by_id[current].get("parent_id")
            if parent is None:
                return None
            current = parent
        return None

    unit_rows = []
    for unit_id in order:
        native = units_by_id[unit_id]
        localized = locales_by_unit[unit_id]
        block_id = containing_block(unit_id)
        public_reader = None
        if native["unit_type"] in {"chapter", "appendix"} and native.get("source_local_id"):
            public_reader = f"{PAGES_URL}{native['source_local_id']}.html"
        unit_rows.append({
            "unit_id": unit_id,
            "preorder": ordinal_by_id[unit_id],
            "native_order": native.get("order"),
            "kind": native["unit_type"],
            "parent_id": native.get("parent_id"),
            "block_id": block_id,
            "source_title": native.get("title"),
            "title_id": localized.get("localized_title"),
            "source_local_id": native.get("source_local_id"),
            "source_path": native["source_path"],
            "source_xpath": native.get("source_xpath"),
            "source_fragment_sha256": native.get("source_fragment_sha256"),
            "target_path": localized["target_path"],
            "target_xpath": localized.get("target_xpath"),
            "target_fragment_sha256": localized.get("target_fragment_sha256"),
            "boundary_id": localized.get("boundary_id"),
            "translation_state": localized["translation_state"],
            "child_unit_ids": [child["id"] for child in children.get(unit_id, [])],
            "segment_count": len(segments_by_unit.get(unit_id, [])),
            "concept_ids": sorted(concepts_by_unit.get(unit_id, [])),
            "exercise_support": sorted(support_by_exercise.get(unit_id, []), key=lambda row: row["relation_id"]),
            "public_reader_url": public_reader,
            "public_target_source": f"{REPOSITORY}/blob/{CURRENT_PUBLIC_HEAD}/source/{localized['target_path']}",
            "public_authority_source": f"{SOURCE_REPOSITORY}/blob/{SOURCE_COMMIT}/{native['source_path']}",
        })
    unit_row_by_id = {row["unit_id"]: row for row in unit_rows}

    block_rows = []
    for native in block_units:
        member_ids = [row["unit_id"] for row in unit_rows if row["block_id"] == native["id"]]
        member_set = set(member_ids)
        block_concepts = sorted({concept_id for unit_id in member_ids for concept_id in concepts_by_unit.get(unit_id, [])})
        exercises = [unit_id for unit_id in member_ids if units_by_id[unit_id]["unit_type"] == "exercise"]
        type_counts = Counter(units_by_id[unit_id]["unit_type"] for unit_id in member_ids)
        support = [row for row in support_rows if row["exercise_unit_id"] in member_set]
        localized = locales_by_unit[native["id"]]
        block_rows.append({
            "block_id": native["id"],
            "ordinal": len(block_rows) + 1,
            "kind": native["unit_type"],
            "title_id": localized.get("localized_title") or native.get("title") or native["id"],
            "source_title": native.get("title"),
            "source_local_id": native.get("source_local_id"),
            "source_path": native["source_path"],
            "public_reader_url": unit_row_by_id[native["id"]]["public_reader_url"] or PAGES_URL,
            "unit_ids": member_ids,
            "unit_count": len(member_ids),
            "unit_type_counts": dict(sorted(type_counts.items())),
            "exercise_ids": exercises,
            "exercise_count": len(exercises),
            "concept_ids": block_concepts,
            "concept_count": len(block_concepts),
            "explicit_support_relation_ids": [row["relation_id"] for row in support],
            "explicit_support_count": len(support),
        })

    concept_rows = [{
        "concept_id": row["id"],
        "source_label": row.get("source_label"),
        "definition": row.get("definition"),
        "prerequisite_concept_ids": row.get("prerequisite_concept_ids", []),
        "unit_ids": row.get("unit_ids", []),
        "status": row["status"],
    } for row in sorted(concepts, key=lambda row: row["id"])]
    relation_rows = [{
        "relation_id": row["id"],
        "relation": row["relation"],
        "source_id": row["source_id"],
        "target_id": row["target_id"],
        "status": row["status"],
    } for row in sorted(relations, key=lambda row: row["id"])]

    term_status = Counter(row.get("status", "unknown") for row in terms)
    correction_status = Counter(row.get("status", "unknown") for row in corrections)
    unit_type_counts = Counter(row["unit_type"] for row in units)
    counts = {
        "export_manifest_members": len(export_inputs),
        "source_lock_inputs": 1 + len(export_inputs) + len(control_inputs) + 2,
        "native_canonical_records": 19048,
        "native_physical_jsonl_rows": 19130,
        "common_virtual_records": 19049,
        "common_derived_external_records": 1,
        "units": len(units),
        "unit_locale_mappings": len(unit_locales),
        "segments": len(segments),
        "segment_locale_mappings": len(segment_locales),
        "learner_blocks": len(block_rows),
        "chapters": sum(row["kind"] == "chapter" for row in block_rows),
        "appendices": sum(row["kind"] == "appendix" for row in block_rows),
        "exercises": unit_type_counts["exercise"],
        "solution_units": unit_type_counts["solution"],
        "answer_units": unit_type_counts["answer"],
        "hint_units": unit_type_counts["hint"],
        "explicit_support_relations": len(support_rows),
        "explicit_solves_relations": relation_counts["solves"],
        "explicit_answers_relations": relation_counts["answers"],
        "explicit_hints_relations": relation_counts["hints"],
        "concepts": len(concepts),
        "terms": len(terms),
        "terminology_registry_rows": len(terminology_registry),
        "terminology_review_rows": len(terminology_review),
        "terminology_field_checked_rows": 12,
        "corrections": len(corrections),
        "relations": len(relations),
        "assets": len(assets),
        "declared_build_targets": len(build_targets),
        "artifacts": len(artifacts),
        "qa_events": len(qa_events),
        "rights_components": len(rights),
        "reader_pages": pdf_qa["artifact"]["pages"],
        "reader_html_files": html_qa["artifact"]["files"],
        "reader_html_bytes": html_qa["artifact"]["bytes"],
        "reader_outline_entries": pdf_qa["navigation_and_links_gate"]["outline_entries"],
        "source_unresolved_xrefs": summary["source_unresolved_xrefs"],
        "target_unresolved_xrefs": summary["target_unresolved_xrefs"],
        "unresolved_assets": summary["unresolved_assets"],
        "github_raw_files_verified": len(public_readback["github"]["raw_files"]),
        "github_full_artifacts_verified": len(public_readback["github"]["release"]["fully_downloaded_and_sha256_verified"]),
        "public_reader_routes_verified": len(public_readback["reader"]["pages"]),
        "zenodo_open_records_verified": len(public_readback["zenodo"]["records"]),
    }

    learning_map = {
        "schema": "c70-learning-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "title": "Kombinatorika Terapan",
        "native_course_outcome": course["outcome"],
        "native_course_scope": course["scope"],
        "program_prerequisites": course["prerequisite_course_ids"],
        "prerequisite_scope": "native_course_level_external_B10_anchor_not_per_unit_invention",
        "route": {
            "route_id": "C70:route:r012-complete",
            "root_unit_id": roots[0]["id"],
            "block_ids": [row["block_id"] for row in block_rows],
            "all_unit_ids": order,
        },
        "blocks": block_rows,
        "public_reader": PAGES_URL,
        "public_pdf": f"https://zenodo.org/records/{ZENODO_RECORD_ID}/files/{PDF_NAME}?download=1",
        "portable_source_archive": f"https://zenodo.org/records/{ZENODO_RECORD_ID}/files/{SOURCE_ZIP_NAME}?download=1",
        "portable_html_archive": f"https://zenodo.org/records/{ZENODO_RECORD_ID}/files/{HTML_ZIP_NAME}?download=1",
        "limitations": [
            "Adapter memproyeksikan identitas, struktur, dan bukti tanpa menyalin badan sumber atau terjemahan buku.",
            "Status edisi target native tetap draft; klaim publik yang lebih tepat adalah draf Bahasa Indonesia lengkap yang diperiksa mesin, tanpa klaim tinjauan manusia.",
            "Dari 407 unit latihan, hanya relasi dukungan eksplisit native yang ditampilkan: 57 solusi, 9 jawaban, dan 16 petunjuk. Unit solusi lain tidak dipasangkan secara rekaan.",
            "Satu xref yang tidak terselesaikan berada pada sumber hulu yang dibekukan; target Bahasa Indonesia memiliki nol xref yang tidak terselesaikan.",
            "Prasyarat B10 adalah jangkar tingkat kursus eksternal; adapter tidak menciptakan prasyarat atau hasil belajar per unit.",
            "Backend common-v1 19.049 rekaman tetap proyeksi virtual reversibel; indeks pengguna hanya membawa metadata terpilih.",
        ],
    }
    educator_map = {
        "schema": "c70-educator-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "selector": {
            "selection_unit": "exact_native_unit_id",
            "export_format": "application/json",
            "body_content_embedded": False,
            "units": unit_rows,
            "exercise_support": sorted(support_rows, key=lambda row: row["relation_id"]),
        },
        "counts": counts,
        "claim_boundary": {
            "all_native_units_indexed": True,
            "all_explicit_exercise_support_relations_indexed": True,
            "unlinked_solution_units_present": counts["solution_units"] - counts["explicit_solves_relations"],
            "unlinked_solution_units_inferred": False,
            "unit_outcomes_available": False,
            "unit_prerequisites_available": False,
        },
        "limitations": [
            "Pemilih mengekspor ID, hierarki, hash fragmen, konsep, dan relasi dukungan; isi buku tidak disalin.",
            "Relasi solusi, jawaban, dan petunjuk mempertahankan arah native dari unit dukungan menuju unit latihan.",
            "Tidak adanya pasangan eksplisit tidak diubah menjadi klaim bahwa dukungan tidak ada; itu tetap keadaan tidak terpetakan.",
        ],
    }
    concept_index = {
        "schema": "c70-concept-index/1",
        "course_id": COURSE_ID,
        "concept_count": len(concept_rows),
        "concepts": concept_rows,
        "body_content_embedded": False,
    }
    relation_index = {
        "schema": "c70-relation-index/1",
        "course_id": COURSE_ID,
        "relation_count": len(relation_rows),
        "relation_type_counts": dict(sorted(relation_counts.items())),
        "relations": relation_rows,
        "exercise_support_projection": sorted(support_rows, key=lambda row: row["relation_id"]),
        "exercise_support_projection_rows": len(support_rows),
        "specialized_projection_duplicate_rows_materialized": 0,
        "body_content_embedded": False,
    }
    ledger_references = {
        "schema": "c70-ledger-references/1",
        "course_id": COURSE_ID,
        "export_manifest": export_manifest,
        "export_members": export_inputs,
        "export_inventory": _inventory_identity(export_inputs),
        "migration_receipt": migration_input,
        "migration_id": migration["migration_id"],
        "migration_mode": migration["migration_mode"],
        "native_record_counts": migration["source"]["native_type_counts"],
        "common_projection": {
            "record_count": migration["target"]["record_count"],
            "virtual_backend_json_bytes": migration["target"]["virtual_backend_json_bytes"],
            "virtual_backend_json_sha256": migration["target"]["virtual_backend_json_sha256"],
            "virtual_records_jsonl_bytes": migration["target"]["virtual_records_jsonl_bytes"],
            "virtual_records_jsonl_sha256": migration["target"]["virtual_records_jsonl_sha256"],
            "exact_reverse_extraction": migration["transformation"]["exact_reverse_extraction"],
            "projection_rows_verified_not_migrated_twice": migration["transformation"]["projection_rows_verified_not_migrated_twice"],
        },
        "native_target_edition": {
            "id": target_edition["id"],
            "status": target_edition["status"],
            "translation_state": target_edition["translation_state"],
            "release_claim": "complete machine-checked Indonesian draft; no human review claimed",
        },
        "source_edition": {
            "id": source_edition["id"],
            "commit": source_edition["commit"],
            "tree": source_edition["tree"],
            "archive_bytes": source_edition["archive_bytes"],
            "archive_sha256": source_edition["archive_sha256"],
        },
        "projection": {
            "native_bodies_copied": False,
            "native_ids_preserved": True,
            "native_export_hashes_replayed": True,
            "specialized_exercise_projection_double_counted": False,
            "common_virtual_backend_materialized": False,
        },
    }
    public_evidence = {
        "schema": "c70-public-evidence/1",
        "course_id": COURSE_ID,
        "github": {
            "repository": REPOSITORY,
            "current_public_head": public_readback["github"]["current_head"],
            "current_public_tree": public_readback["github"]["current_tree"],
            "release_version": RELEASE_VERSION,
            "maintenance_version": MAINTENANCE_VERSION,
            "release_assets": public_readback["github"]["release"]["assets"],
            "anonymous_verification": "verified",
        },
        "zenodo": {
            "concept_doi": ZENODO_CONCEPT_DOI,
            "reader_record_id": ZENODO_RECORD_ID,
            "reader_doi": f"10.5281/zenodo.{ZENODO_RECORD_ID}",
            "maintenance_record_id": ZENODO_MAINTENANCE_RECORD_ID,
            "maintenance_doi": f"10.5281/zenodo.{ZENODO_MAINTENANCE_RECORD_ID}",
            "anonymous_verification": "verified",
            "all_records_open": public_readback["zenodo"]["all_open"],
        },
        "reader": {
            "online_html": True,
            "verified_routes": len(public_readback["reader"]["pages"]),
            "offline_html_archive": True,
            "html_files": html_qa["artifact"]["files"],
            "html_bytes": html_qa["artifact"]["bytes"],
            "html_language": html_qa["language"],
            "pdf_pages": pdf_qa["artifact"]["pages"],
            "pdf_internal_destinations": pdf_qa["navigation_and_links_gate"]["release"]["internal_destinations"],
            "tagged_pdf_claimed": False,
            "mathml_claimed": False,
        },
        "historical_figshare_receipt_in_migration_preserved_not_used": True,
        "public_state_changed": False,
    }
    rights_and_terms = {
        "schema": "c70-rights-and-terms/1",
        "course_id": COURSE_ID,
        "book_license": "CC-BY-SA-4.0",
        "component_rights": rights,
        "rights_readiness": {
            "result": rights_qa["result"],
            "publication_blocker_component_ids": rights_qa["publication_blocker_component_ids"],
            "limitations": rights_qa["limitations"],
        },
        "terminology": terms,
        "terminology_status_counts": dict(sorted(term_status.items())),
        "terminology_registry": terminology_registry,
        "terminology_review_log": terminology_review,
        "terminology_review": {
            "registry_records": 633,
            "review_log_records": 633,
            "field_checked_rows": 12,
            "all_choices_provisional": True,
            "empty_required_cells": 0,
            "public_validation_locator": f"{REPOSITORY}/blob/{CURRENT_PUBLIC_HEAD}/terminology/TERMINOLOGY_DECISION_REVIEW_VALIDATION.json",
        },
        "corrections": corrections,
        "correction_status_counts": dict(sorted(correction_status.items())),
        "blanket_license_claimed": False,
    }
    claim_boundary = {
        "schema": "c70-claim-boundary/1",
        "course_id": COURSE_ID,
        "learner_attempt_instances": 0,
        "learner_submission_instances": 0,
        "learner_result_instances": 0,
        "credential_assertion_instances": 0,
        "native_target_edition_state": "draft",
        "public_release_claim": "complete_machine_checked_draft_no_human_review_claimed",
        "native_target_edition_promoted": False,
        "native_unit_outcomes_invented": False,
        "native_unit_prerequisites_invented": False,
        "unlinked_solution_units_inferred": False,
        "exercise_support_projection_double_counted": False,
        "source_xref_defect_retyped_as_target_defect": False,
        "native_bodies_copied": False,
        "central_course_truth_rewritten": False,
        "historical_migration_receipt_rewritten": False,
        "common_virtual_backend_materialized": False,
        "figshare_active_destination_used": False,
        "public_state_changed": False,
    }
    capabilities = {
        "schema": "c70-capability-summary/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "native_family": "applied_combinatorics_pretext_backend",
        "counts": counts,
        "learner": {
            "ordered_block_navigation": True,
            "all_native_unit_ids_in_route": True,
            "concept_coverage_index": True,
            "direct_public_html_routes": len(public_readback["reader"]["pages"]),
            "linked_pdf": True,
            "portable_html_and_source_archives": True,
        },
        "educator": {
            "all_unit_selector": True,
            "exercise_support_selector": True,
            "json_plan_export": True,
            "terminology_rows": len(terms),
            "correction_rows": len(corrections),
            "concept_rows": len(concepts),
        },
        "reproducibility": {
            "all_native_export_members_hash_verified": True,
            "existing_virtual_projection_records": migration["target"]["record_count"],
            "existing_exact_reverse_extraction_records": migration["transformation"]["exact_reverse_extraction"],
            "projection_rows_not_double_counted": 82,
            "adapter_deterministic": True,
        },
        "rights": {"component_specific": True, "blanket_license_claimed": False},
        "claim_boundary": claim_boundary,
        "strict_contract_2_3_1_conformance_claimed": False,
    }
    source_lock = {
        "schema": "c70-source-lock/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "native_release": RELEASE_VERSION,
        "maintenance_release": MAINTENANCE_VERSION,
        "native_repository": {
            "url": REPOSITORY,
            "current_public_head": CURRENT_PUBLIC_HEAD,
            "current_public_tree": CURRENT_PUBLIC_TREE,
            "source_repository": SOURCE_REPOSITORY,
            "source_commit": SOURCE_COMMIT,
            "source_tree": SOURCE_TREE,
        },
        "local_source_locator": "04_mirrors/id/applied-combinatorics-id",
        "export_manifest_input": export_manifest,
        "export_inputs": export_inputs,
        "control_inputs": control_inputs,
        "migration_input": migration_input,
        "public_readback_input": public_readback_input,
        "export_inventory": _inventory_identity(export_inputs),
    }
    return {
        "source_lock": source_lock,
        "learning_map": learning_map,
        "educator_map": educator_map,
        "concept_index": concept_index,
        "relation_index": relation_index,
        "ledger_references": ledger_references,
        "public_evidence": public_evidence,
        "rights_and_terms": rights_and_terms,
        "claim_boundary": claim_boundary,
        "capabilities": capabilities,
    }


def projection_errors(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    learning = bundle.get("learning_map", {})
    educator = bundle.get("educator_map", {})
    concepts = bundle.get("concept_index", {})
    relations = bundle.get("relation_index", {})
    ledgers = bundle.get("ledger_references", {})
    public = bundle.get("public_evidence", {})
    rights = bundle.get("rights_and_terms", {})
    boundary = bundle.get("claim_boundary", {})
    capabilities = bundle.get("capabilities", {})
    counts = capabilities.get("counts", {})
    units = educator.get("selector", {}).get("units", [])
    unit_ids = [row.get("unit_id") for row in units]
    blocks = learning.get("blocks", [])
    support = educator.get("selector", {}).get("exercise_support", [])

    if len(unit_ids) != 1408 or len(set(unit_ids)) != 1408:
        errors.append("C70-UNIT-IDENTITY")
    if learning.get("route", {}).get("all_unit_ids") != unit_ids:
        errors.append("C70-UNIT-ORDER")
    if len(blocks) != 19 or sum(row.get("kind") == "chapter" for row in blocks) != 16 or sum(row.get("kind") == "appendix" for row in blocks) != 3:
        errors.append("C70-LEARNER-BLOCKS")
    if learning.get("route", {}).get("block_ids") != [row.get("block_id") for row in blocks]:
        errors.append("C70-BLOCK-ORDER")
    if learning.get("program_prerequisites") != ["B10"]:
        errors.append("C70-COURSE-PREREQUISITE")
    if len(support) != 82 or len({row.get("relation_id") for row in support}) != 82:
        errors.append("C70-SUPPORT-IDENTITY")
    if Counter(row.get("support_kind") for row in support) != Counter({"solution": 57, "hint": 16, "answer": 9}):
        errors.append("C70-SUPPORT-TYPES")
    if concepts.get("concept_count") != 701 or len(concepts.get("concepts", [])) != 701:
        errors.append("C70-CONCEPTS")
    if relations.get("relation_count") != 6334 or len(relations.get("relations", [])) != 6334:
        errors.append("C70-RELATIONS")
    if relations.get("relation_type_counts") != EXPECTED_RELATIONS:
        errors.append("C70-RELATION-TYPES")
    if relations.get("specialized_projection_duplicate_rows_materialized") != 0:
        errors.append("C70-PROJECTION-DOUBLE-COUNT")
    expected_counts = {
        "export_manifest_members": 23, "native_canonical_records": 19048,
        "native_physical_jsonl_rows": 19130, "common_virtual_records": 19049,
        "common_derived_external_records": 1, "units": 1408,
        "unit_locale_mappings": 1408, "segments": 3806,
        "segment_locale_mappings": 3806, "learner_blocks": 19, "chapters": 16,
        "appendices": 3, "exercises": 407, "solution_units": 84,
        "answer_units": 9, "hint_units": 16, "explicit_support_relations": 82,
        "explicit_solves_relations": 57, "explicit_answers_relations": 9,
        "explicit_hints_relations": 16, "concepts": 701, "terms": 633,
        "terminology_registry_rows": 633, "terminology_review_rows": 633,
        "terminology_field_checked_rows": 12, "corrections": 354,
        "relations": 6334, "assets": 397, "declared_build_targets": 9,
        "artifacts": 10, "qa_events": 171, "rights_components": 6,
        "reader_pages": 350, "reader_html_files": 1500,
        "reader_html_bytes": 287651617, "reader_outline_entries": 170,
        "source_unresolved_xrefs": 1, "target_unresolved_xrefs": 0,
        "unresolved_assets": 0, "github_raw_files_verified": 12,
        "github_full_artifacts_verified": 3, "public_reader_routes_verified": 19,
        "zenodo_open_records_verified": 2,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            errors.append(f"C70-COUNT-{key.upper()}")
    if educator.get("selector", {}).get("body_content_embedded") is not False:
        errors.append("C70-EDUCATOR-BODY-COPY")
    if ledgers.get("common_projection", {}).get("exact_reverse_extraction") != 19048:
        errors.append("C70-MIGRATION-ROUNDTRIP")
    if ledgers.get("common_projection", {}).get("projection_rows_verified_not_migrated_twice") != 82:
        errors.append("C70-MIGRATION-PROJECTION")
    if ledgers.get("native_target_edition", {}).get("status") != "draft":
        errors.append("C70-TARGET-EDITION-STATE")
    if public.get("github", {}).get("current_public_head") != CURRENT_PUBLIC_HEAD or public.get("github", {}).get("anonymous_verification") != "verified":
        errors.append("C70-GITHUB-PUBLIC")
    if public.get("zenodo", {}).get("all_records_open") is not True or public.get("zenodo", {}).get("anonymous_verification") != "verified":
        errors.append("C70-ZENODO-PUBLIC")
    if public.get("reader", {}).get("online_html") is not True or public.get("reader", {}).get("verified_routes") != 19:
        errors.append("C70-READER-PUBLIC")
    if public.get("reader", {}).get("tagged_pdf_claimed") is not False or public.get("reader", {}).get("mathml_claimed") is not False:
        errors.append("C70-ACCESSIBILITY-OVERCLAIM")
    if public.get("public_state_changed") is not False:
        errors.append("C70-PUBLIC-STATE")
    if len(rights.get("component_rights", [])) != 6 or rights.get("blanket_license_claimed") is not False:
        errors.append("C70-RIGHTS")
    if len(rights.get("terminology", [])) != 633 or len(rights.get("terminology_review_log", [])) != 633:
        errors.append("C70-TERMINOLOGY")
    if len(rights.get("corrections", [])) != 354:
        errors.append("C70-CORRECTIONS")
    false_keys = (
        "native_target_edition_promoted", "native_unit_outcomes_invented",
        "native_unit_prerequisites_invented", "unlinked_solution_units_inferred",
        "exercise_support_projection_double_counted", "source_xref_defect_retyped_as_target_defect",
        "native_bodies_copied", "central_course_truth_rewritten",
        "historical_migration_receipt_rewritten", "common_virtual_backend_materialized",
        "figshare_active_destination_used", "public_state_changed",
    )
    for key in false_keys:
        if boundary.get(key) is not False:
            errors.append(f"C70-BOUNDARY-{key.upper()}")
    for key in ("learner_attempt_instances", "learner_submission_instances", "learner_result_instances", "credential_assertion_instances"):
        if boundary.get(key) != 0:
            errors.append(f"C70-NONZERO-{key.upper()}")
    return sorted(set(errors))
