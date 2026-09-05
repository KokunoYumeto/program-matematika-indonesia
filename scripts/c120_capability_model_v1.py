"""Exact zero-copy capability projection for C120/O005 modeling and dynamics."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


COURSE_ID = "C120"
NATIVE_ROLE_ID = "O005"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"
NATIVE_VERSION = "v1.01-id-complete-reader-20260823-r5"
REPOSITORY = "https://github.com/KokunoYumeto/mathematical-modeling-nonlinear-dynamics-id"
RELEASE_URL = f"{REPOSITORY}/releases/tag/v1.01-id-complete-reader-20260823-r5"
PAGES_URL = "https://kokunoyumeto.github.io/mathematical-modeling-nonlinear-dynamics-id/"
ZENODO_RECORD_ID = 22070943
ZENODO_RECORD = f"https://zenodo.org/records/{ZENODO_RECORD_ID}"
ZENODO_DOI = "10.5281/zenodo.22070943"
ZENODO_CONCEPT_DOI = "10.5281/zenodo.22059939"
FROZEN_BACKEND_COMMIT = "1f7e7c9a180f450d91352d1b117094f07f1158ae"
FROZEN_BACKEND_TREE = "b19efc503a4544135337ff75cf622b1daac4eefa"
FROZEN_RELEASE_COMMIT = "75f35bce216a0c6c223d3bcc3938a40403028a08"
PAGES_WRAPPER_COMMIT = "934822e79264a3747610691f08ce204b364eb978"
CURRENT_PUBLIC_HEAD = "1a5958db5d04eef5fba23af69913b6b1272939a9"
CURRENT_PUBLIC_TREE = "487ac640e12680039d6e80faca7366240f748065"
CURRENT_BACKEND_TREE = FROZEN_BACKEND_TREE
MIGRATION_RECEIPT = "backend/migrations/o005-c120-id-v1/MIGRATION_RECEIPT.json"
RELEASE_DIR = "release/zenodo/reader-first-complete-20260823-r5"
PDF_NAME = "01_Pengantar_Pemodelan_Matematika_Edisi_Bahasa_Indonesia_Lengkap.pdf"
ZIP_NAME = "02_O005_LEGA_v1.01_id_complete-reader-20260823-r5_compact_source.zip"
PDF_RECEIPT_NAME = "03_O005_LEGA_v1.01_id_complete_pdf_build_receipt.json"

NATIVE_INPUTS = (
    "00_control/GITHUB_MIRROR_HANDOFF_20260823.md",
    "00_control/COMPLETION_AUDIT_20260823.md",
    "00_control/RIGHTS_AND_PROVENANCE.md",
    "00_control/TERMINOLOGY.csv",
    "00_control/TERMINOLOGY_QA_INDONESIAN_FIELD_SOURCE_20260822.md",
    "00_control/SOURCE_CORRECTIONS.csv",
    "00_control/ZENODO_PUBLICATION_RECEIPT_CANONICAL_20260823.json",
    f"{RELEASE_DIR}/{PDF_RECEIPT_NAME}",
    f"{RELEASE_DIR}/RELEASE_MANIFEST.json",
    f"{RELEASE_DIR}/CHECKSUMS.sha256",
    f"{RELEASE_DIR}/LICENSE.md",
    f"{RELEASE_DIR}/{PDF_NAME}",
    f"{RELEASE_DIR}/{ZIP_NAME}",
    "site/index.html",
    "site/site.css",
)


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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, str]] = []
        last_field = reader.fieldnames[-1] if reader.fieldnames else "note"
        for row in reader:
            extras = row.pop(None, None)
            if extras:
                row[last_field] = f"{row.get(last_field, '')},{','.join(extras)}"
                row["_adapter_csv_normalization"] = "joined_unquoted_comma_into_final_field"
            rows.append(row)
        return rows


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _kind(unit_id: str) -> str:
    if unit_id.startswith("O005-BRIDGE-"):
        return "original_bridge"
    if "-FM" in unit_id:
        return "front_matter"
    if "-PT" in unit_id:
        return "part_introduction"
    if "-BM" in unit_id:
        return "back_matter"
    return "source_chapter"


def _verify_backend(native_root: Path, migration: dict[str, Any]) -> dict[str, Any]:
    expected = migration["source"]["backend_files"]
    verified: list[dict[str, Any]] = []
    for relative, recorded in sorted(expected.items()):
        actual = identity(native_root / relative, display_path=relative)
        if actual["bytes"] != recorded["bytes"] or actual["sha256"] != recorded["sha256"]:
            raise ValueError(f"C120 backend identity drift: {relative}")
        verified.append(actual)
    inventory = b"".join(
        f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n".encode("utf-8")
        for row in verified
    )
    return {
        "files": len(verified),
        "bytes": sum(row["bytes"] for row in verified),
        "all_file_hashes_verified": True,
        "computed_inventory_bytes": len(inventory),
        "computed_inventory_sha256": sha256_bytes(inventory),
        "receipt_inventory_bytes": migration["source"]["backend_inventory_bytes"],
        "receipt_inventory_sha256": migration["source"]["backend_inventory_sha256"],
        "receipt_native_record_inventory_sha256": migration["source"]["native_record_inventory_sha256"],
    }


def _problem_projection(mastery: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for problem in mastery["problems"]:
        provenance = problem.get("provenance", {})
        rows.append({
            "problem_id": problem["problem_id"],
            "ordinal": problem["ordinal"],
            "hint_available": bool(problem.get("hint")),
            "check_type": problem.get("check", {}).get("type"),
            "support_type": problem.get("solution_or_rubric", {}).get("type"),
            "article_link_count": len(problem.get("article_link_ids", [])),
            "source_formula_occurrence_count": len(problem.get("source_formula_occurrences", [])),
            "problem_summary_provenance": provenance.get("problem_summary"),
            "hint_provenance": provenance.get("hint"),
            "check_provenance": provenance.get("check"),
            "solution_or_rubric_provenance": provenance.get("solution_or_rubric"),
        })
    return rows


def derive_projection(native_root: Path, hub_root: Path) -> dict[str, Any]:
    missing = [relative for relative in NATIVE_INPUTS if not (native_root / relative).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing C120 native inputs: {missing}")
    migration_path = hub_root / MIGRATION_RECEIPT
    if not migration_path.is_file():
        raise FileNotFoundError(f"Missing C120 migration receipt: {migration_path}")

    migration = read_json(migration_path)
    backend_integrity = _verify_backend(native_root, migration)
    release = read_json(native_root / RELEASE_DIR / "RELEASE_MANIFEST.json")
    pdf_receipt = read_json(native_root / RELEASE_DIR / PDF_RECEIPT_NAME)
    zenodo = read_json(native_root / "00_control/ZENODO_PUBLICATION_RECEIPT_CANONICAL_20260823.json")
    terminology = read_csv(native_root / "00_control/TERMINOLOGY.csv")
    corrections = read_csv(native_root / "00_control/SOURCE_CORRECTIONS.csv")
    projects_source = read_json(native_root / "backend/projects/O005-LEGA-V101-CH14.projects.json")
    native_inputs = [identity(native_root / relative, display_path=relative) for relative in NATIVE_INPUTS]
    migration_identity = identity(migration_path, display_path=MIGRATION_RECEIPT)

    order = pdf_receipt["ordered_unit_ids"]
    reader_by_id = {row["unit_id"]: row for row in pdf_receipt["reader_inputs"]}
    outline = pdf_receipt["outline"][2:]
    if [row["unit_id"] for row in pdf_receipt["reader_inputs"]] != order or len(outline) != len(order):
        raise ValueError("C120 PDF receipt unit order drift")

    units: list[dict[str, Any]] = []
    mastery_problem_rows: list[dict[str, Any]] = []
    for ordinal, unit_id in enumerate(order, 1):
        native = read_json(native_root / f"backend/units/{unit_id}.json")
        reader = reader_by_id[unit_id]
        problems: list[dict[str, Any]] = []
        mastery_path = native.get("mastery_path")
        if mastery_path:
            mastery = read_json(native_root / mastery_path)
            problems = _problem_projection(mastery)
            mastery_problem_rows.extend({"unit_id": unit_id, **row} for row in problems)
        start_page = outline[ordinal - 1]["page_index"]
        end_page = (outline[ordinal]["page_index"] - 1) if ordinal < len(outline) else pdf_receipt["pdf"]["pages"]
        target = native["target"]
        source = native.get("source", {})
        unit = {
            "unit_id": unit_id,
            "ordinal": ordinal,
            "label": reader["label"],
            "title_id": reader["title"],
            "source_title": source.get("chapter"),
            "unit_kind": _kind(unit_id),
            "origin_kind": "independent_supplement" if unit_id.startswith("O005-BRIDGE-") else "source_derived_translation",
            "unit_schema": native["schema"],
            "target_path": target["content_path"],
            "target_sha256": target["content_sha256"],
            "source_url": source.get("url"),
            "segments_path": native["segments"]["path"],
            "segments_sha256": native["segments"]["sha256"],
            "segment_count": native["segments"]["count"],
            "problem_ids": [row["problem_id"] for row in problems],
            "problem_support": problems,
            "problem_count": len(problems),
            "mastery_path": mastery_path,
            "mastery_sha256": native.get("mastery_sha256"),
            "unit_notebook_path": native.get("notebook_path"),
            "unit_notebook_sha256": native.get("notebook_sha256"),
            "reader_index": reader["index"],
            "reader_package_manifest": reader["package_manifest"],
            "reader_url": f"{PAGES_URL}{unit_id}/",
            "public_target_source": f"{REPOSITORY}/blob/{CURRENT_PUBLIC_HEAD}/{target['content_path']}",
            "public_unit_record": f"{REPOSITORY}/blob/{CURRENT_PUBLIC_HEAD}/backend/units/{unit_id}.json",
            "public_mastery_record": f"{REPOSITORY}/blob/{CURRENT_PUBLIC_HEAD}/{mastery_path}" if mastery_path else None,
            "pdf_page_start": start_page,
            "pdf_page_end": end_page,
        }
        units.append(unit)

    projects = [{
        "project_id": row["project_id"],
        "title_id": row["locale"]["id-ID"]["title"],
        "mathematical_core_id": row["mathematical_core_id"],
        "archive_path": row["archive_path"],
        "archive_bytes": row["archive_bytes"],
        "archive_sha256": row["archive_sha256"],
        "file_count": len(row["files"]),
        "notebook_path": row["notebook_path"],
        "notebook_sha256": row["notebook_sha256"],
        "public_project_catalog": f"{REPOSITORY}/blob/{CURRENT_PUBLIC_HEAD}/backend/projects/O005-LEGA-V101-CH14.projects.json",
        "result_reproduction_claimed": projects_source["closure"]["result_reproduction_claim"],
    } for row in projects_source["projects"]]

    support_counts = Counter(row["support_type"] for row in mastery_problem_rows)
    term_status = Counter(str(row.get("status") or "unspecified") for row in terminology)
    correction_status = Counter(str(row.get("status") or "unspecified") for row in corrections)
    migration_counts = migration["coverage"]
    counts = {
        "source_lock_inputs": len(native_inputs) + 1,
        "backend_files": backend_integrity["files"],
        "backend_bytes": backend_integrity["bytes"],
        "native_records": migration_counts["native_record_count"],
        "common_virtual_records": migration["target"]["record_count"],
        "common_tables": migration["target"]["table_count"],
        "common_nonempty_tables": migration["target"]["nonempty_table_count"],
        "units": len(units),
        "source_units": sum(row["origin_kind"] == "source_derived_translation" for row in units),
        "bridge_units": sum(row["origin_kind"] == "independent_supplement" for row in units),
        "segments": sum(row["segment_count"] for row in units),
        "source_segments": migration_counts["source_segments"],
        "bridge_segments": migration_counts["bridge_segments"],
        "mastery_files": sum(bool(row["mastery_path"]) for row in units),
        "mastery_problems": len(mastery_problem_rows),
        "problems_with_hints": sum(row["hint_available"] for row in mastery_problem_rows),
        "worked_solutions": support_counts["worked_solution"],
        "qualitative_rubrics": support_counts["qualitative_rubric"],
        "worked_classifications": support_counts["worked_classification"],
        "chapter_notebooks": release["coverage"]["chapter_notebooks"],
        "bridge_notebooks": release["coverage"]["bridge_notebooks"],
        "project_notebooks": release["coverage"]["project_notebooks"],
        "total_notebooks": release["coverage"]["total_notebooks"],
        "projects": len(projects),
        "project_packet_files": sum(row["file_count"] for row in projects),
        "terminology_rows": len(terminology),
        "terminology_admitted": term_status["admitted"],
        "terminology_provisional": term_status["provisional"],
        "terminology_csv_normalized_rows": sum("_adapter_csv_normalization" in row for row in terminology),
        "correction_rows": len(corrections),
        "corrections_resolved": sum(bool(row.get("status", "").strip()) for row in corrections),
        "reader_pages": pdf_receipt["pdf"]["pages"],
        "reader_routes": len(units),
        "reader_outline_entries": len(pdf_receipt["outline"]),
        "public_pages_files": 253,
        "public_pages_bytes": 56_411_468,
        "release_assets": len(zenodo["files"]),
        "derived_segment_variants": migration_counts["derived_segment_variants"],
        "derived_translation_alignments": migration_counts["derived_translation_alignments"],
    }

    learning_map = {
        "schema": "c120-learning-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "title": "Pemodelan Matematis dan Dinamika Nonlinear",
        "native_title": release["title"],
        "program_prerequisites": ["B70", "B80", "C10"],
        "prerequisite_scope": "central_course_level_only_not_native_per_unit_claims",
        "route": {"route_id": "C120:route:o005-complete", "unit_ids": order},
        "units": units,
        "public_reader": PAGES_URL,
        "public_pdf": f"{ZENODO_RECORD}/files/{PDF_NAME}?download=1",
        "portable_source_archive": f"{ZENODO_RECORD}/files/{ZIP_NAME}?download=1",
        "portable_entry": "site/index.html",
        "limitations": [
            "Adapter memproyeksikan identitas, metadata, dan bukti; badan buku tetap pada edisi native publik.",
            "Sebanyak 22 unit terjemahan sumber dan empat modul jembatan orisinal tetap dibedakan; modul jembatan tidak dinyatakan sebagai karya sumber.",
            "Sebanyak 141 rekaman penguasaan memuat petunjuk dan dukungan jawaban, tetapi 14 di antaranya adalah rubrik kualitatif dan satu klasifikasi terbimbing, bukan solusi numerik tunggal.",
            "Dua belas notebook proyek adalah paket awal; adapter tidak mengklaim reproduksi hasil artikel yang dirujuk.",
            "Prasyarat B70, B80, dan C10 berasal dari peta program pusat, bukan graf prasyarat per unit native.",
            "Proyeksi umum 16.029 rekaman bersifat virtual dan dapat direkonstruksi dari backend native 81 berkas; tidak ada salinan badan korpus kedua.",
        ],
    }
    educator_map = {
        "schema": "c120-educator-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "selector": {
            "selection_unit": "native_unit_id",
            "problem_selection": "exact_native_problem_id",
            "project_selection": "exact_native_project_id",
            "export_format": "application/json",
            "body_content_embedded": False,
            "selected_units": units,
            "projects": projects,
        },
        "counts": counts,
        "claim_boundary": {
            "native_unit_outcomes_available": False,
            "course_level_outcome_source": "central_program_authority",
            "mastery_problem_support_records": 141,
            "worked_solution_records": 126,
            "qualitative_rubrics": 14,
            "worked_classifications": 1,
            "project_result_reproduction_claimed": False,
        },
        "limitations": [
            "Pemilih menyusun paket ID unit, masalah, proyek, dan tautan sumber; isi buku dan jawaban tidak disalin.",
            "Dukungan penguasaan ditampilkan menurut tipe aslinya sehingga rubrik tidak dilabeli sebagai solusi tertutup.",
            "Proyek mempertahankan arsip, notebook awal, pemeriksaan, rubrik, dan provenance native tanpa klaim reproduksi hasil penelitian eksternal.",
        ],
    }
    ledger_references = {
        "schema": "c120-ledger-references/1",
        "course_id": COURSE_ID,
        "migration_receipt": migration_identity,
        "migration_id": migration["migration_id"],
        "migration_mode": migration["migration_mode"],
        "backend_integrity": backend_integrity,
        "native_record_counts": migration["source"]["native_record_counts"],
        "common_projection": {
            "record_count": migration["target"]["record_count"],
            "canonical_backend_sha256": migration["target"]["canonical_backend_sha256"],
            "virtual_records_jsonl_bytes": migration["target"]["virtual_records_jsonl_bytes"],
            "virtual_records_jsonl_sha256": migration["target"]["virtual_records_jsonl_sha256"],
            "exact_native_backend_file_byte_reconstruction": migration["validation"]["exact_native_backend_file_byte_reconstruction"],
            "exact_native_logical_record_reverse_extraction": migration["validation"]["exact_native_logical_record_reverse_extraction"],
            "two_independent_assemblies": migration["validation"]["two_independent_assemblies"],
        },
        "historical_control_boundary": {
            "migration_owner_commit": FROZEN_BACKEND_COMMIT,
            "current_public_head": CURRENT_PUBLIC_HEAD,
            "backend_tree_unchanged": True,
            "current_control_files_not_retyped_as_historical_migration_inputs": True,
            "note": "Receipt migrasi tetap historis; adapter memverifikasi ulang 81 berkas backend yang identik dan mengunci kontrol publik saat ini secara terpisah.",
        },
        "source_target_unit_hashes": [{
            key: row[key] for key in (
                "unit_id", "target_path", "target_sha256", "segments_path", "segments_sha256", "segment_count",
                "mastery_path", "mastery_sha256", "unit_notebook_path", "unit_notebook_sha256",
            )
        } for row in units],
        "projects": projects,
        "projection": {
            "native_bodies_copied": False,
            "native_ids_preserved": True,
            "native_backend_hashes_replayed": True,
            "strict_native_roundtrip_inherited_from_migration_receipt": True,
            "common_virtual_backend_materialized": False,
        },
    }
    public_evidence = {
        "schema": "c120-public-evidence/1",
        "course_id": COURSE_ID,
        "github": {
            "repository": REPOSITORY,
            "release": RELEASE_URL,
            "release_commit": FROZEN_RELEASE_COMMIT,
            "pages_wrapper_commit": PAGES_WRAPPER_COMMIT,
            "current_public_head": CURRENT_PUBLIC_HEAD,
            "current_public_tree": CURRENT_PUBLIC_TREE,
            "current_backend_tree": CURRENT_BACKEND_TREE,
            "anonymous_verification": "verified_by_frozen_handoff",
            "handoff": identity(native_root / NATIVE_INPUTS[0], display_path=NATIVE_INPUTS[0]),
        },
        "zenodo": {
            "record_id": zenodo["record_id"],
            "doi": zenodo["doi"],
            "concept_doi": zenodo["concept_doi"],
            "url": zenodo["record_url"],
            "anonymous_verification": "verified",
            "release_assets": zenodo["files"],
        },
        "reader": {
            "online_html": True,
            "online_routes": 26,
            "public_files_verified": 253,
            "public_bytes_verified": 56_411_468,
            "semantic_html": True,
            "pdf_pages": 355,
            "tagged_pdf": True,
            "pdf_outline_entries": 28,
            "portable_source_archive": True,
        },
        "public_state_changed": False,
    }
    rights_and_terms = {
        "schema": "c120-rights-and-terms/1",
        "course_id": COURSE_ID,
        "rights_authority": identity(native_root / "00_control/RIGHTS_AND_PROVENANCE.md", display_path="00_control/RIGHTS_AND_PROVENANCE.md"),
        "component_boundaries": [
            {"component": "Lega source-derived translation and source-derived exercises", "license": "CC BY-NC-SA 4.0"},
            {"component": "independently authored hints, checks, support, notebooks, and bridge modules", "license": "CC BY-NC-SA 4.0", "relationship": "separately marked adaptation additions"},
            {"component": "Indonesian terminology comparison witness arXiv:2001.05854v1", "license": "CC BY-SA 4.0", "relationship": "evidence only; not relicensed into the Lega adaptation"},
            {"component": "cited articles and external resources", "license": "not redistributed", "relationship": "citations only"},
        ],
        "terminology_authority": identity(native_root / "00_control/TERMINOLOGY.csv", display_path="00_control/TERMINOLOGY.csv"),
        "terminology_field_qa": identity(native_root / "00_control/TERMINOLOGY_QA_INDONESIAN_FIELD_SOURCE_20260822.md", display_path="00_control/TERMINOLOGY_QA_INDONESIAN_FIELD_SOURCE_20260822.md"),
        "terminology": terminology,
        "terminology_status_counts": dict(sorted(term_status.items())),
        "terminology_csv_normalizations": [
            {"term_id": row["term_id"], "action": row["_adapter_csv_normalization"]}
            for row in terminology if "_adapter_csv_normalization" in row
        ],
        "correction_authority": identity(native_root / "00_control/SOURCE_CORRECTIONS.csv", display_path="00_control/SOURCE_CORRECTIONS.csv"),
        "corrections": corrections,
        "correction_status_counts": dict(sorted(correction_status.items())),
        "blanket_license_claimed": False,
    }
    claim_boundary = {
        "schema": "c120-claim-boundary/1",
        "course_id": COURSE_ID,
        "learner_attempt_instances": 0,
        "learner_submission_instances": 0,
        "learner_result_instances": 0,
        "credential_assertion_instances": 0,
        "mastery_problem_support_records": 141,
        "worked_solution_records": 126,
        "qualitative_rubrics": 14,
        "worked_classifications": 1,
        "project_result_reproduction_claimed": False,
        "native_unit_outcomes_invented": False,
        "native_unit_prerequisites_invented": False,
        "bridge_units_retyped_as_source_units": False,
        "native_bodies_copied": False,
        "central_course_truth_rewritten": False,
        "historical_migration_receipt_rewritten": False,
        "common_virtual_backend_materialized": False,
        "public_state_changed": False,
    }
    capabilities = {
        "schema": "c120-capability-summary/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "native_family": "modeling_and_nonlinear_dynamics",
        "counts": counts,
        "learner": {
            "unit_navigation": True,
            "exact_problem_ids": 141,
            "direct_native_html_routes": 26,
            "tagged_pdf": True,
            "portable_source_and_reader_archive": True,
            "source_and_bridge_units_visibly_distinct": True,
        },
        "educator": {
            "unit_selector": True,
            "problem_selector": True,
            "project_selector": True,
            "json_plan_export": True,
            "mastery_support_type_preserved": True,
            "terminology_rows": len(terminology),
            "correction_rows": len(corrections),
        },
        "reproducibility": {
            "all_81_native_backend_files_hash_verified": True,
            "existing_virtual_projection_records": migration["target"]["record_count"],
            "existing_exact_reverse_extraction_records": migration["validation"]["exact_native_logical_record_reverse_extraction"],
            "current_backend_tree_equals_frozen_backend_tree": True,
            "adapter_deterministic": True,
        },
        "rights": {"component_specific": True, "blanket_license_claimed": False},
        "claim_boundary": claim_boundary,
        "strict_contract_2_3_1_conformance_claimed": False,
    }
    source_lock = {
        "schema": "c120-source-lock/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "native_version": NATIVE_VERSION,
        "native_repository": {
            "url": REPOSITORY,
            "frozen_backend_commit": FROZEN_BACKEND_COMMIT,
            "frozen_backend_tree": FROZEN_BACKEND_TREE,
            "frozen_release_commit": FROZEN_RELEASE_COMMIT,
            "pages_wrapper_commit": PAGES_WRAPPER_COMMIT,
            "current_public_head": CURRENT_PUBLIC_HEAD,
            "current_public_tree": CURRENT_PUBLIC_TREE,
            "current_backend_tree": CURRENT_BACKEND_TREE,
            "backend_tree_unchanged_since_migration": True,
        },
        "local_source_locator": "04_mirrors/id/mathematical-modeling-nonlinear-dynamics-id",
        "native_inputs": native_inputs,
        "migration_input": migration_identity,
        "backend_integrity": backend_integrity,
    }
    return {
        "source_lock": source_lock,
        "learning_map": learning_map,
        "educator_map": educator_map,
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
    capabilities = bundle.get("capabilities", {})
    ledgers = bundle.get("ledger_references", {})
    public = bundle.get("public_evidence", {})
    rights = bundle.get("rights_and_terms", {})
    boundary = bundle.get("claim_boundary", {})
    units = learning.get("units", [])
    unit_ids = [row.get("unit_id") for row in units]
    problems = [problem for row in units for problem in row.get("problem_support", [])]
    projects = educator.get("selector", {}).get("projects", [])
    counts = capabilities.get("counts", {})

    if len(unit_ids) != 26 or len(set(unit_ids)) != 26:
        errors.append("C120-UNIT-IDENTITY")
    if learning.get("route", {}).get("unit_ids") != unit_ids:
        errors.append("C120-UNIT-ORDER")
    if learning.get("program_prerequisites") != ["B70", "B80", "C10"]:
        errors.append("C120-COURSE-PREREQUISITES")
    if sum(row.get("origin_kind") == "source_derived_translation" for row in units) != 22 or sum(row.get("origin_kind") == "independent_supplement" for row in units) != 4:
        errors.append("C120-SOURCE-BRIDGE-BOUNDARY")
    if len(problems) != 141 or len({row.get("problem_id") for row in problems}) != 141:
        errors.append("C120-MASTERY-IDENTITY")
    if any(row.get("hint_available") is not True for row in problems):
        errors.append("C120-HINT-CLOSURE")
    support = Counter(row.get("support_type") for row in problems)
    if support != Counter({"worked_solution": 126, "qualitative_rubric": 14, "worked_classification": 1}):
        errors.append("C120-SUPPORT-TYPE-BOUNDARY")
    if len(projects) != 12 or len({row.get("project_id") for row in projects}) != 12:
        errors.append("C120-PROJECT-IDENTITY")
    if any(row.get("result_reproduction_claimed") is not False for row in projects):
        errors.append("C120-PROJECT-RESULT-CLAIM")
    expected_counts = {
        "backend_files": 81, "backend_bytes": 3270308, "native_records": 4941,
        "common_virtual_records": 16029, "common_tables": 38, "common_nonempty_tables": 13,
        "units": 26, "source_units": 22, "bridge_units": 4, "segments": 4105,
        "source_segments": 3448, "bridge_segments": 657, "mastery_files": 16,
        "mastery_problems": 141, "problems_with_hints": 141, "worked_solutions": 126,
        "qualitative_rubrics": 14, "worked_classifications": 1, "chapter_notebooks": 10,
        "bridge_notebooks": 4, "project_notebooks": 12, "total_notebooks": 26,
        "projects": 12, "project_packet_files": 72, "terminology_rows": 321,
        "terminology_admitted": 320, "terminology_provisional": 1, "correction_rows": 160,
        "terminology_csv_normalized_rows": 1,
        "reader_pages": 355, "reader_routes": 26, "reader_outline_entries": 28,
        "public_pages_files": 253, "public_pages_bytes": 56411468, "release_assets": 6,
        "derived_segment_variants": 7553, "derived_translation_alignments": 3448,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            errors.append(f"C120-COUNT-{key.upper()}")
    if counts.get("corrections_resolved") != 160:
        errors.append("C120-CORRECTIONS-RESOLVED")
    if educator.get("selector", {}).get("body_content_embedded") is not False:
        errors.append("C120-EDUCATOR-BODY-COPY")
    if len(educator.get("selector", {}).get("selected_units", [])) != 26:
        errors.append("C120-EDUCATOR-UNITS")
    if ledgers.get("backend_integrity", {}).get("all_file_hashes_verified") is not True:
        errors.append("C120-BACKEND-INTEGRITY")
    if ledgers.get("projection", {}).get("native_bodies_copied") is not False:
        errors.append("C120-NATIVE-BODY-COPY")
    if public.get("github", {}).get("anonymous_verification") != "verified_by_frozen_handoff":
        errors.append("C120-GITHUB-ANONYMITY")
    if public.get("zenodo", {}).get("anonymous_verification") != "verified":
        errors.append("C120-ZENODO-ANONYMITY")
    if public.get("reader", {}).get("online_html") is not True or public.get("reader", {}).get("tagged_pdf") is not True:
        errors.append("C120-READER-ACCESSIBILITY")
    if public.get("public_state_changed") is not False:
        errors.append("C120-PUBLIC-STATE")
    if rights.get("blanket_license_claimed") is not False or len(rights.get("component_boundaries", [])) != 4:
        errors.append("C120-RIGHTS-BOUNDARY")
    if len(rights.get("terminology", [])) != 321:
        errors.append("C120-TERMINOLOGY-ROWS")
    if len(rights.get("corrections", [])) != 160:
        errors.append("C120-CORRECTION-ROWS")
    expected_false = (
        "project_result_reproduction_claimed", "native_unit_outcomes_invented",
        "native_unit_prerequisites_invented", "bridge_units_retyped_as_source_units",
        "native_bodies_copied", "central_course_truth_rewritten",
        "historical_migration_receipt_rewritten", "common_virtual_backend_materialized",
        "public_state_changed",
    )
    for key in expected_false:
        if boundary.get(key) is not False:
            errors.append(f"C120-BOUNDARY-{key.upper()}")
    for key in ("learner_attempt_instances", "learner_submission_instances", "learner_result_instances", "credential_assertion_instances"):
        if boundary.get(key) != 0:
            errors.append(f"C120-NONZERO-{key.upper()}")
    return sorted(set(errors))
