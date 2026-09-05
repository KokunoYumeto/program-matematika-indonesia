"""Exact zero-copy capability projection for C110/R015 numerical analysis."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable


COURSE_ID = "C110"
NATIVE_ROLE_ID = "R015"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"
NATIVE_VERSION = "3.0-id.2-r1"
REPOSITORY = "https://github.com/KokunoYumeto/tea-time-numerical-analysis-id"
RELEASE_URL = f"{REPOSITORY}/releases/tag/v3.0-id.2-r1"
PUBLIC_COMMIT = "cf4a425918b6555d3157001bfa7c18acc1f97026"
PUBLIC_TREE = "32004a75627e8cd0401fec5c855663c37a0848fe"
ZENODO_RECORD_ID = 22075088
ZENODO_RECORD = f"https://zenodo.org/records/{ZENODO_RECORD_ID}"
ZENODO_DOI = "10.5281/zenodo.22075088"
ZENODO_CONCEPT_DOI = "10.5281/zenodo.22054085"
PDF_NAME = "Tea-Time-Numerical-Analysis-id-ID.pdf"
ZIP_NAME = "Tea-Time-Numerical-Analysis-id-ID-v3.0-id.2-r1-source-backend.zip"
MIGRATION_RECEIPT = "backend/migrations/tea-time-id-v1/MIGRATION_RECEIPT.json"
PUBLIC_READBACK = "backend/course-capsule-v1/adapters/c110-capability-v1/input/public-native-readback.json"

NATIVE_INPUTS = (
    "backend/manifests/lane_manifest.json",
    "backend/exports/interoperability-v0/manifest.json",
    "backend/exports/interoperability-v0/records.jsonl",
    "backend/exports/interoperability-v0/records.csv",
    "backend/schema/record.schema.json",
    "00_control/TERMINOLOGY.csv",
    "00_control/ADVERSE_LEDGER.csv",
    "publication/COMPONENT_RIGHTS_AND_PROVENANCE.md",
    "publication/R1_RELEASE_INTEGRITY_QA_20260824.md",
    "publication/FINALIZATION_GATE_v3.0-id.2-r1.json",
    "publication/RELEASE_PUBLICATION_RECEIPT_v3.0-id.2-r1.json",
    f"output/pdf/{PDF_NAME}",
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


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def csv_rows(path: Path) -> list[dict[str, str]]:
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


def _verify_native_backend(native_root: Path, lane: dict[str, Any]) -> dict[str, Any]:
    verified: list[dict[str, Any]] = []
    for recorded in lane["files"]:
        relative = f"backend/{recorded['path']}"
        actual = identity(native_root / relative, display_path=relative)
        if actual["bytes"] != recorded["bytes"] or actual["sha256"] != recorded["sha256"]:
            raise ValueError(f"C110 backend identity drift: {relative}")
        if sum(1 for line in (native_root / relative).open("r", encoding="utf-8") if line.strip()) != recorded["records"]:
            raise ValueError(f"C110 backend record count drift: {relative}")
        verified.append(actual)
    inventory = _inventory_identity(verified)
    return {
        "files": len(verified),
        "bytes": sum(row["bytes"] for row in verified),
        "records": sum(row["records"] for row in lane["files"]),
        "all_file_hashes_verified": True,
        "all_record_counts_verified": True,
        "inventory_bytes": inventory["bytes"],
        "inventory_sha256": inventory["sha256"],
        "files_verified": verified,
    }


def _preorder(root_ids: list[str], children: dict[str, list[dict[str, Any]]]) -> list[str]:
    ordered: list[str] = []

    def visit(unit_id: str) -> None:
        ordered.append(unit_id)
        for child in children.get(unit_id, []):
            visit(child["id"])

    for root_id in root_ids:
        visit(root_id)
    return ordered


def _descendants(root_id: str, children: dict[str, list[dict[str, Any]]]) -> list[str]:
    output: list[str] = []
    queue = deque([root_id])
    while queue:
        current = queue.popleft()
        for child in children.get(current, []):
            output.append(child["id"])
            queue.append(child["id"])
    return output


def derive_projection(native_root: Path, hub_root: Path) -> dict[str, Any]:
    missing = [relative for relative in NATIVE_INPUTS if not (native_root / relative).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing C110 native inputs: {missing}")
    migration_path = hub_root / MIGRATION_RECEIPT
    public_readback_path = hub_root / PUBLIC_READBACK
    if not migration_path.is_file() or not public_readback_path.is_file():
        raise FileNotFoundError("Missing C110 migration or anonymous public-readback evidence")

    lane = read_json(native_root / "backend/manifests/lane_manifest.json")
    export_manifest = read_json(native_root / "backend/exports/interoperability-v0/manifest.json")
    migration = read_json(migration_path)
    public_readback = read_json(public_readback_path)
    final_gate = read_json(native_root / "publication/FINALIZATION_GATE_v3.0-id.2-r1.json")
    release_receipt = read_json(native_root / "publication/RELEASE_PUBLICATION_RECEIPT_v3.0-id.2-r1.json")
    backend_integrity = _verify_native_backend(native_root, lane)
    records = read_jsonl(native_root / "backend/exports/interoperability-v0/records.jsonl")
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_type[record["record_type"]].append(record)
    record_counts = {kind: len(rows) for kind, rows in sorted(by_type.items())}
    if record_counts != lane["record_counts"] or len(records) != lane["total_unique_records"]:
        raise ValueError("C110 canonical record inventory drift")
    if len({record["id"] for record in records}) != len(records):
        raise ValueError("C110 duplicate native IDs")
    if export_manifest["round_trip"]["round_trip_equal"] is not True:
        raise ValueError("C110 native CSV round trip is not proven")

    units_by_id = {row["id"]: row for row in by_type["unit"]}
    segments_by_id = {row["id"]: row for row in by_type["segment"]}
    localization_by_segment = {row["segment_id"]: row for row in by_type["localization"]}
    source_files_by_id = {row["id"]: row for row in by_type["source_file"]}
    children: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for unit in by_type["unit"]:
        if unit.get("parent_id"):
            children[unit["parent_id"]].append(unit)
    for rows in children.values():
        rows.sort(key=lambda row: (row.get("order", 0), row["id"]))

    contained_segments: dict[str, list[str]] = defaultdict(list)
    segment_units: dict[str, list[str]] = defaultdict(list)
    relation_counts = Counter()
    for relation in by_type["relation"]:
        relation_counts[relation["relation"]] += 1
        if relation["relation"] == "contains" and relation["from_id"] in units_by_id and relation["to_id"] in segments_by_id:
            contained_segments[relation["from_id"]].append(relation["to_id"])
            segment_units[relation["to_id"]].append(relation["from_id"])
    for values in contained_segments.values():
        values.sort(key=lambda segment_id: (segments_by_id[segment_id].get("order", 0), segment_id))
    if any(len(parent_ids) != 1 for parent_ids in segment_units.values()) or set(segment_units) != set(segments_by_id):
        raise ValueError("C110 segment-to-unit membership is not one-to-one and closed")

    def localized_title(unit: dict[str, Any]) -> dict[str, Any] | None:
        source_title = unit.get("source_title")
        if not source_title:
            return None
        candidates = []
        for segment_id in contained_segments.get(unit["id"], []):
            segment = segments_by_id[segment_id]
            localization = localization_by_segment.get(segment_id)
            if localization and segment.get("source_text") == source_title and localization.get("target_text"):
                candidates.append((segment.get("order", 0), segment_id, localization["target_text"]))
        if not candidates:
            return None
        _, segment_id, target = sorted(candidates)[0]
        return {"segment_id": segment_id, "source": source_title, "target": target}

    roots = sorted(
        [row["id"] for row in by_type["unit"] if not row.get("parent_id")],
        key=lambda unit_id: (units_by_id[unit_id].get("order", 0), unit_id),
    )
    all_unit_order = _preorder(roots, children)
    if len(all_unit_order) != 281 or set(all_unit_order) != set(units_by_id):
        raise ValueError("C110 unit hierarchy does not close over 281 native units")

    unit_rows: list[dict[str, Any]] = []
    for unit_id in all_unit_order:
        unit = units_by_id[unit_id]
        unit_rows.append({
            "unit_id": unit_id,
            "kind": unit["kind"],
            "order": unit.get("order"),
            "parent_id": unit.get("parent_id"),
            "source_file_id": unit.get("source_file_id"),
            "source_local_id": unit.get("source_local_id"),
            "source_title": unit.get("source_title"),
            "localized_title": localized_title(unit),
            "child_unit_ids": [child["id"] for child in children.get(unit_id, [])],
            "segment_ids": contained_segments.get(unit_id, []),
            "segment_count": len(contained_segments.get(unit_id, [])),
            "rights_ids": unit.get("rights_ids", [unit.get("rights_id")] if unit.get("rights_id") else []),
        })

    module_roots = sorted(
        [row for row in by_type["unit"] if row["kind"] == "included_file"],
        key=lambda row: (row["order"], row["id"]),
    )
    unit_to_module: dict[str, str] = {}
    modules: list[dict[str, Any]] = []
    for module in module_roots:
        member_ids = [module["id"], *_descendants(module["id"], children)]
        for member_id in member_ids:
            if member_id in unit_to_module:
                raise ValueError(f"C110 unit belongs to two file modules: {member_id}")
            unit_to_module[member_id] = module["id"]
        file_record = source_files_by_id[module["source_file_id"]]
        title = next((localized_title(units_by_id[item]) for item in member_ids if localized_title(units_by_id[item])), None)
        basename = Path(file_record["source_path"]).stem.lower()
        role = "solutions" if basename == "solutions" else "answers" if basename == "answers" else "preface" if basename == "preface" else "teaching"
        segment_ids = [segment_id for item in member_ids for segment_id in contained_segments.get(item, [])]
        modules.append({
            "module_id": module["id"],
            "ordinal": module["order"],
            "role": role,
            "source_file_id": module["source_file_id"],
            "source_path": file_record["source_path"],
            "source_bytes": file_record["source_bytes"],
            "source_sha256": file_record["source_sha256"],
            "target_path": file_record["target_path"],
            "target_bytes": file_record["target_bytes"],
            "target_sha256": file_record["target_sha256"],
            "title_id": title["target"] if title else Path(file_record["target_path"]).stem,
            "source_title": title["source"] if title else None,
            "title_segment_id": title["segment_id"] if title else None,
            "unit_ids": member_ids,
            "unit_count": len(member_ids),
            "segment_count": len(segment_ids),
            "localization_count": sum(segment_id in localization_by_segment for segment_id in segment_ids),
            "public_target_source": f"{REPOSITORY}/blob/{PUBLIC_COMMIT}/{file_record['target_path']}",
            "public_source_record": f"{REPOSITORY}/blob/{PUBLIC_COMMIT}/backend/topology/source_files.jsonl",
        })

    alignments: list[dict[str, Any]] = []
    for localization in sorted(by_type["localization"], key=lambda row: row["id"]):
        segment_id = localization["segment_id"]
        segment = segments_by_id[segment_id]
        unit_id = segment_units[segment_id][0]
        alignments.append({
            "alignment_id": localization["id"],
            "segment_id": segment_id,
            "unit_id": unit_id,
            "module_id": unit_to_module.get(unit_id),
            "source_file_id": segment.get("source_file_id"),
            "source_segment_sha256": localization["source_segment_sha256"],
            "target_path": localization["target_path"],
            "target_text_sha256": localization["target_text_sha256"],
            "target_block_sha256": localization["target_block_sha256"],
            "workflow_state": localization["workflow_state"],
            "language_state": localization["language_state"],
            "structure_state": localization["structure_state"],
            "interchange_state": localization["interchange_state"],
            "build_state": localization["build_state"],
            "publication_state": localization["publication_state"],
        })

    source_files = [{
        "source_file_id": row["id"],
        "role": row["role"],
        "format": row["format"],
        "source_path": row["source_path"],
        "source_bytes": row["source_bytes"],
        "source_sha256": row["source_sha256"],
        "target_path": row["target_path"],
        "target_bytes": row["target_bytes"],
        "target_sha256": row["target_sha256"],
        "rights_ids": row.get("rights_ids", [row.get("rights_id")] if row.get("rights_id") else []),
    } for row in sorted(by_type["source_file"], key=lambda row: row["source_path"])]

    experiments = []
    for experiment in sorted(by_type["experiment"], key=lambda row: row["experiment_key"]):
        experiments.append({
            "experiment_id": experiment["id"],
            "experiment_key": experiment["experiment_key"],
            "kind": experiment["kind"],
            "unit_id": experiment["unit_id"],
            "module_id": unit_to_module.get(experiment["unit_id"]),
            "instruction_segment_ids": experiment["instruction_segment_ids"],
            "runner_segment_ids": experiment["runner_segment_ids"],
            "runner_asset_version_ids": experiment["runner_asset_version_ids"],
            "expected_output_segment_ids": experiment.get("expected_output_segment_ids", []),
            "parameter_evidence_segment_ids": experiment.get("parameter_evidence_segment_ids", []),
            "result_mode": experiment.get("result_mode"),
        })

    status_counts = {
        "localization_language": dict(sorted(Counter(row["language_state"] for row in by_type["localization"]).items())),
        "localization_workflow": dict(sorted(Counter(row["workflow_state"] for row in by_type["localization"]).items())),
        "localization_build": dict(sorted(Counter(row["build_state"] for row in by_type["localization"]).items())),
        "localization_publication": dict(sorted(Counter(row["publication_state"] for row in by_type["localization"]).items())),
        "correction": dict(sorted(Counter(row["status"] for row in by_type["correction"]).items())),
        "correction_severity": dict(sorted(Counter(row["severity"] for row in by_type["correction"]).items())),
        "unit_kind": dict(sorted(Counter(row["kind"] for row in by_type["unit"]).items())),
        "relation": dict(sorted(relation_counts.items())),
    }
    solution_module = next(row for row in modules if row["role"] == "solutions")
    answer_module = next(row for row in modules if row["role"] == "answers")
    source_bytes = sum(row["source_bytes"] for row in source_files)
    target_bytes = sum(row["target_bytes"] for row in source_files)
    production = final_gate["production_qa"]
    counts = {
        "native_records": len(records),
        "native_record_types": len(by_type),
        "native_backend_files": backend_integrity["files"],
        "native_backend_bytes": backend_integrity["bytes"],
        "common_virtual_records": migration["target"]["record_count"],
        "common_generated_records": migration["transformation"]["generated_common_records"],
        "common_tables": len(migration["tables"]),
        "units": len(unit_rows),
        "file_modules": len(modules),
        "teaching_modules": sum(row["role"] in {"teaching", "preface"} for row in modules),
        "solution_modules": sum(row["role"] == "solutions" for row in modules),
        "answer_modules": sum(row["role"] == "answers" for row in modules),
        "source_files": len(source_files),
        "source_bytes": source_bytes,
        "target_files": len(source_files),
        "target_bytes": target_bytes,
        "segments": len(by_type["segment"]),
        "localizations": len(by_type["localization"]),
        "alignments": len(alignments),
        "terms": len(by_type["term"]),
        "concepts": len(by_type["concept"]),
        "corrections": len(by_type["correction"]),
        "experiments": len(experiments),
        "relations": len(by_type["relation"]),
        "artifacts": len(by_type["artifact"]),
        "rights_components": len(by_type["rights"]),
        "formula_pairs": production["formula_pairs"],
        "inset_pairs": production["inset_pairs"],
        "layout_pairs": production["layout_pairs"],
        "pdf_pages": production["reader_pages"],
        "solution_module_units": solution_module["unit_count"],
        "solution_module_segments": solution_module["segment_count"],
        "answer_module_units": answer_module["unit_count"],
        "answer_module_segments": answer_module["segment_count"],
        "github_verified_files": public_readback["github"]["verified_files"],
        "github_verified_bytes": public_readback["github"]["verified_bytes"],
        "zenodo_verified_files": public_readback["zenodo"]["verified_files"],
        "zenodo_verified_bytes": public_readback["zenodo"]["verified_bytes"],
    }

    limitations = [
        "Adapter memproyeksikan identitas, struktur, hash, dan bukti; badan buku tetap pada edisi native publik.",
        "Backend native tidak memiliki entitas latihan tersendiri, sehingga adapter tidak menciptakan hubungan latihan-ke-solusi atau latihan-ke-jawaban.",
        "Modul solusi dan jawaban dipertahankan sebagai modul native yang dapat dipilih, tetapi tidak diklaim berpasangan satu-ke-satu dengan latihan.",
        "Status not_built dan unpublished pada rekaman lokalisasi adalah status alur tingkat segmen; artefak PDF final dan rilis publik dibuktikan secara terpisah.",
        "Dua ratus koreksi open_recorded adalah temuan sumber yang dipertahankan, bukan dua ratus kegagalan rilis; gerbang final membuktikan nol ketidakcocokan formula, kontrol, numerik, atau topologi terlarang.",
        "Prasyarat B30, B40, B80, dan C10 berasal dari kurikulum pusat, bukan klaim prasyarat per unit native.",
        "Repo native tidak menyediakan pembaca HTML semantik lengkap; halaman pusat ini adalah navigator metadata dan alat pengajar, bukan salinan HTML buku.",
        "Proyeksi umum 53.055 rekaman tetap virtual dan dapat direkonstruksi dari backend native; proyeksi itu tidak dimaterialisasi ulang.",
    ]

    learning_map = {
        "schema": "c110-learning-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "title": "Analisis Numerik",
        "native_title": final_gate["release"]["title"],
        "program_prerequisites": ["B30", "B40", "B80", "C10"],
        "prerequisite_scope": "central_course_level_only_not_native_per_unit_claims",
        "route": {"route_id": "C110:route:r015-complete", "module_ids": [row["module_id"] for row in modules]},
        "root_unit_ids": roots,
        "modules": modules,
        "units": unit_rows,
        "concepts": by_type["concept"],
        "experiments": experiments,
        "public_pdf": f"{ZENODO_RECORD}/files/{PDF_NAME}?download=1",
        "portable_source_archive": f"{ZENODO_RECORD}/files/{ZIP_NAME}?download=1",
        "public_backend": f"{REPOSITORY}/tree/{PUBLIC_COMMIT}/backend",
        "limitations": limitations,
    }
    educator_map = {
        "schema": "c110-educator-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "selector": {
            "selection_unit": "native_module_or_unit_id",
            "experiment_selection": "exact_native_experiment_id",
            "export_format": "application/json",
            "body_content_embedded": False,
            "modules": modules,
            "units": unit_rows,
            "experiments": experiments,
        },
        "counts": counts,
        "claim_boundary": {
            "native_unit_outcomes_available": False,
            "course_level_outcome_source": "central_program_authority",
            "native_exercise_entity_records": 0,
            "exercise_solution_joins_inferred": False,
            "solution_module_id": solution_module["module_id"],
            "answer_module_id": answer_module["module_id"],
        },
        "limitations": limitations,
    }
    alignment_index = {
        "schema": "c110-translation-alignment-index/1",
        "course_id": COURSE_ID,
        "body_content_embedded": False,
        "alignment_count": len(alignments),
        "alignments": alignments,
    }
    ledger_references = {
        "schema": "c110-ledger-references/1",
        "course_id": COURSE_ID,
        "migration_receipt": identity(migration_path, display_path=MIGRATION_RECEIPT),
        "migration_id": migration["migration_id"],
        "migration_mode": migration["migration_mode"],
        "backend_integrity": backend_integrity,
        "native_record_counts": record_counts,
        "status_counts": status_counts,
        "source_files": source_files,
        "common_projection": {
            "record_count": migration["target"]["record_count"],
            "virtual_records_jsonl_bytes": migration["target"]["virtual_records_jsonl_bytes"],
            "virtual_records_jsonl_sha256": migration["target"]["virtual_records_jsonl_sha256"],
            "native_ids_preserved": migration["transformation"]["native_ids_preserved"],
            "native_payload_fields_changed": migration["transformation"]["native_payload_fields_changed"],
            "deterministic_virtual_assembly_equal": migration["validation"]["deterministic_virtual_assembly_equal"],
        },
        "projection": {
            "native_bodies_copied": False,
            "native_ids_preserved": True,
            "all_alignment_ids_preserved": True,
            "strict_native_csv_roundtrip_inherited_from_migration_receipt": True,
            "common_virtual_backend_materialized": False,
        },
    }
    public_evidence = {
        "schema": "c110-public-evidence/1",
        "course_id": COURSE_ID,
        "anonymous_readback_receipt": identity(public_readback_path, display_path=PUBLIC_READBACK),
        "github": public_readback["github"],
        "zenodo": public_readback["zenodo"],
        "reader": {
            "pdf_pages": production["reader_pages"],
            "pdf_bytes": final_gate["artifacts"][0]["bytes"],
            "pdf_sha256": final_gate["artifacts"][0]["sha256"],
            "portable_source_archive": True,
            "native_semantic_html": False,
            "tagged_pdf_claimed": False,
        },
        "public_state_changed": False,
    }
    rights_and_terms = {
        "schema": "c110-rights-and-terms/1",
        "course_id": COURSE_ID,
        "rights_authority": identity(native_root / "publication/COMPONENT_RIGHTS_AND_PROVENANCE.md", display_path="publication/COMPONENT_RIGHTS_AND_PROVENANCE.md"),
        "component_boundaries": by_type["rights"],
        "terminology_authority": identity(native_root / "00_control/TERMINOLOGY.csv", display_path="00_control/TERMINOLOGY.csv"),
        "terminology": by_type["term"],
        "concepts": by_type["concept"],
        "correction_authority": identity(native_root / "00_control/ADVERSE_LEDGER.csv", display_path="00_control/ADVERSE_LEDGER.csv"),
        "corrections": by_type["correction"],
        "status_counts": status_counts,
        "blanket_license_claimed": False,
    }
    claim_boundary = {
        "schema": "c110-claim-boundary/1",
        "course_id": COURSE_ID,
        "learner_attempt_instances": 0,
        "learner_submission_instances": 0,
        "learner_result_instances": 0,
        "credential_assertion_instances": 0,
        "native_exercise_entity_records": 0,
        "exercise_solution_joins_inferred": False,
        "native_unit_outcomes_invented": False,
        "native_unit_prerequisites_invented": False,
        "native_semantic_html_claimed": False,
        "tagged_pdf_claimed": False,
        "segment_workflow_states_promoted_to_release_states": False,
        "native_bodies_copied": False,
        "central_course_truth_rewritten": False,
        "historical_migration_receipt_rewritten": False,
        "common_virtual_backend_materialized": False,
        "public_state_changed": False,
    }
    capabilities = {
        "schema": "c110-capability-summary/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "native_family": "numerical_analysis_lyx_backend",
        "counts": counts,
        "learner": {
            "module_navigation": True,
            "full_unit_hierarchy": True,
            "concept_navigation": True,
            "experiment_navigation": True,
            "exact_public_pdf": True,
            "portable_source_and_backend_archive": True,
            "native_semantic_html": False,
        },
        "educator": {
            "module_selector": True,
            "unit_selector": True,
            "experiment_selector": True,
            "json_plan_export": True,
            "solution_and_answer_modules_visible": True,
            "exercise_solution_joins_inferred": False,
        },
        "reproducibility": {
            "all_native_backend_files_hash_verified": True,
            "native_csv_round_trip": True,
            "existing_virtual_projection_records": migration["target"]["record_count"],
            "public_github_and_zenodo_exact_readback": True,
            "adapter_deterministic": True,
        },
        "rights": {"component_specific": True, "blanket_license_claimed": False},
        "claim_boundary": claim_boundary,
        "strict_contract_2_3_1_conformance_claimed": False,
    }
    source_lock = {
        "schema": "c110-source-lock/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "native_version": NATIVE_VERSION,
        "native_repository": {
            "url": REPOSITORY,
            "current_public_head": PUBLIC_COMMIT,
            "current_public_tree": PUBLIC_TREE,
            "source_commit": lane["source_commit"],
            "source_tree": lane["source_tree"],
        },
        "local_source_locator": "04_mirrors/id/tea-time-numerical-analysis-id",
        "native_inputs": [identity(native_root / relative, display_path=relative) for relative in NATIVE_INPUTS],
        "migration_input": identity(migration_path, display_path=MIGRATION_RECEIPT),
        "public_readback_input": identity(public_readback_path, display_path=PUBLIC_READBACK),
        "backend_integrity": backend_integrity,
    }
    return {
        "source_lock": source_lock,
        "learning_map": learning_map,
        "educator_map": educator_map,
        "translation_alignments": alignment_index,
        "ledger_references": ledger_references,
        "public_evidence": public_evidence,
        "rights_and_terms": rights_and_terms,
        "claim_boundary": claim_boundary,
        "capabilities": capabilities,
        "release_receipt": release_receipt,
    }


def projection_errors(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    learning = bundle.get("learning_map", {})
    educator = bundle.get("educator_map", {})
    alignments = bundle.get("translation_alignments", {})
    ledgers = bundle.get("ledger_references", {})
    public = bundle.get("public_evidence", {})
    rights = bundle.get("rights_and_terms", {})
    boundary = bundle.get("claim_boundary", {})
    counts = bundle.get("capabilities", {}).get("counts", {})
    modules = learning.get("modules", [])
    units = learning.get("units", [])

    expected_counts = {
        "native_records": 28172, "native_record_types": 19, "native_backend_files": 19,
        "common_virtual_records": 53055, "common_generated_records": 24883, "common_tables": 25,
        "units": 281, "file_modules": 29, "teaching_modules": 27, "solution_modules": 1,
        "answer_modules": 1, "source_files": 31, "source_bytes": 2791045,
        "target_files": 31, "target_bytes": 2844828, "segments": 4621,
        "localizations": 4621, "alignments": 4621, "terms": 593, "concepts": 12,
        "corrections": 325, "experiments": 2, "relations": 17614, "artifacts": 2,
        "rights_components": 4, "formula_pairs": 12641, "inset_pairs": 21271,
        "layout_pairs": 11216, "pdf_pages": 387, "solution_module_units": 26,
        "solution_module_segments": 953, "answer_module_units": 26, "answer_module_segments": 529,
        "github_verified_files": 26, "github_verified_bytes": 78131265,
        "zenodo_verified_files": 4, "zenodo_verified_bytes": 41614423,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            errors.append(f"C110-COUNT-{key.upper()}")
    module_ids = [row.get("module_id") for row in modules]
    if len(module_ids) != 29 or len(set(module_ids)) != 29 or learning.get("route", {}).get("module_ids") != module_ids:
        errors.append("C110-MODULE-IDENTITY")
    unit_ids = [row.get("unit_id") for row in units]
    if len(unit_ids) != 281 or len(set(unit_ids)) != 281:
        errors.append("C110-UNIT-IDENTITY")
    unit_map = {row.get("unit_id"): row for row in units}
    if any(row.get("parent_id") is not None and row.get("parent_id") not in unit_map for row in units):
        errors.append("C110-UNIT-PARENT-CLOSURE")
    expected_children: dict[str, list[str]] = defaultdict(list)
    for row in units:
        if row.get("parent_id") is not None:
            expected_children[row["parent_id"]].append(row["unit_id"])
    if any(set(row.get("child_unit_ids", [])) != set(expected_children.get(row["unit_id"], [])) for row in units):
        errors.append("C110-UNIT-PARENT-CLOSURE")
    if learning.get("program_prerequisites") != ["B30", "B40", "B80", "C10"]:
        errors.append("C110-COURSE-PREREQUISITES")
    alignment_rows = alignments.get("alignments", [])
    if len(alignment_rows) != 4621 or len({row.get("alignment_id") for row in alignment_rows}) != 4621:
        errors.append("C110-ALIGNMENT-IDENTITY")
    if any(row.get("unit_id") not in set(unit_ids) for row in alignment_rows):
        errors.append("C110-ALIGNMENT-UNIT-CLOSURE")
    if educator.get("selector", {}).get("body_content_embedded") is not False:
        errors.append("C110-EDUCATOR-BODY-COPY")
    if len(educator.get("selector", {}).get("modules", [])) != 29 or len(educator.get("selector", {}).get("units", [])) != 281:
        errors.append("C110-EDUCATOR-SELECTION")
    if len(educator.get("selector", {}).get("experiments", [])) != 2:
        errors.append("C110-EXPERIMENT-IDENTITY")
    module_roles = Counter(row.get("role") for row in modules)
    if module_roles != Counter({"teaching": 26, "preface": 1, "solutions": 1, "answers": 1}):
        errors.append("C110-SOLUTION-ANSWER-BOUNDARY")
    if ledgers.get("backend_integrity", {}).get("all_file_hashes_verified") is not True:
        errors.append("C110-BACKEND-INTEGRITY")
    if ledgers.get("projection", {}).get("native_bodies_copied") is not False:
        errors.append("C110-NATIVE-BODY-COPY")
    if len(rights.get("component_boundaries", [])) != 4 or rights.get("blanket_license_claimed") is not False:
        errors.append("C110-RIGHTS-BOUNDARY")
    if len(rights.get("terminology", [])) != 593 or len(rights.get("corrections", [])) != 325:
        errors.append("C110-LEDGER-CLOSURE")
    if public.get("github", {}).get("commit") != PUBLIC_COMMIT or public.get("github", {}).get("tree") != PUBLIC_TREE:
        errors.append("C110-GITHUB-IDENTITY")
    if public.get("github", {}).get("verified_files") != 26 or public.get("zenodo", {}).get("verified_files") != 4:
        errors.append("C110-PUBLIC-READBACK")
    if public.get("zenodo", {}).get("access_right") != "open" or public.get("public_state_changed") is not False:
        errors.append("C110-PUBLIC-ACCESS")
    expected_false = (
        "exercise_solution_joins_inferred", "native_unit_outcomes_invented",
        "native_unit_prerequisites_invented", "native_semantic_html_claimed",
        "tagged_pdf_claimed", "segment_workflow_states_promoted_to_release_states",
        "native_bodies_copied", "central_course_truth_rewritten",
        "historical_migration_receipt_rewritten", "common_virtual_backend_materialized",
        "public_state_changed",
    )
    for key in expected_false:
        if boundary.get(key) is not False:
            errors.append(f"C110-BOUNDARY-{key.upper()}")
    for key in ("learner_attempt_instances", "learner_submission_instances", "learner_result_instances", "credential_assertion_instances", "native_exercise_entity_records"):
        if boundary.get(key) != 0:
            errors.append(f"C110-NONZERO-{key.upper()}")
    return sorted(set(errors))


def source_lock_errors(source_lock: dict[str, Any], native_root: Path, hub_root: Path) -> list[str]:
    errors: list[str] = []
    for recorded in source_lock.get("native_inputs", []):
        actual = identity(native_root / recorded["path"], display_path=recorded["path"])
        if actual != recorded:
            errors.append(f"C110-SOURCE-HASH:{recorded['path']}")
    for key, relative in (("migration_input", MIGRATION_RECEIPT), ("public_readback_input", PUBLIC_READBACK)):
        recorded = source_lock.get(key, {})
        actual = identity(hub_root / relative, display_path=relative)
        if actual != recorded:
            errors.append(f"C110-SOURCE-HASH:{relative}")
    return sorted(set(errors))
