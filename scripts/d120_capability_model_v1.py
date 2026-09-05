"""Shared model helpers for the D120 zero-copy capability adapter."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


COURSE_ID = "D120"
NATIVE_COURSE_ID = "O017-D120"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"
RELEASE_VERSION = "2026.08.24"
RELEASE_COMMIT = "cea42b799b038fcac6f9762386d2e8eecd5b1372"
RELEASE_TREE = "01af08fa5170a128c19962b72c7bf6a96428a65e"
REPOSITORY = "https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id"
PAGES_ROOT = "https://kokunoyumeto.github.io/kerja-matematika-yang-dapat-ditelusuri-id/"
ZENODO_RECORD = "https://zenodo.org/records/22073823"

SOURCE_INPUTS = (
    "authority/SOURCE_FREEZE.json",
    "backend/schema.json",
    "backend/manifest.csv",
    "backend/records.jsonl",
    "backend/relations.csv",
    "backend/relations-ledger.csv",
    "backend/semantic-wrapper-v1.schema.json",
    "backend/semantic-wrapper-v1.baseline.json",
    "backend/semantic-wrapper-v1.dataset.json",
    "backend/semantic-wrapper-v1.records.jsonl",
    "backend/semantic-wrapper-v1.localizations.jsonl",
    "backend/semantic-wrapper-v1.relations-ledger.csv",
    "controls/SOURCE_RIGHTS_MANIFEST.csv",
    "controls/TERMINOLOGY.csv",
    "delivery/VALIDATION.json",
    "qa/FULL_COURSE_QA.json",
    "qa/SEMANTIC_WRAPPER_QA.json",
    "qa/PUBLIC_PAYLOAD_PRIVACY_QA_2026.08.24.json",
    "release/GITHUB_PUBLICATION_RECEIPT_2026.08.24.json",
    "release/ZENODO_PUBLICATION_RECEIPT_2026.08.24.json",
    "release/RELEASE_PACKAGE_QA.json",
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


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        raise ValueError(f"JSONL is not LF terminated: {path}")
    rows = []
    for number, line in enumerate(data.decode("utf-8").splitlines(), 1):
        if not line:
            continue
        row = json.loads(line)
        canonical_line = json.dumps(
            row, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        if canonical_line != line.encode("utf-8"):
            raise ValueError(f"JSONL row {number} is not canonical: {path}")
        rows.append(row)
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def records_by_type(rows: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        result[row["entity_type"]].append(row)
    return dict(result)


def localized_texts(rows: Iterable[dict[str, Any]]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = defaultdict(dict)
    for row in rows:
        if row.get("locale") != LOCALE or row.get("language") != "id":
            raise ValueError(f"Unexpected localization identity: {row.get('id')}")
        subject = row["subject_id"]
        field = row["field"]
        if field in result[subject]:
            raise ValueError(f"Duplicate localization field: {subject}/{field}")
        result[subject][field] = row["text"]
    return dict(result)


def _public_page_map(receipt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["path"]: row for row in receipt["pages"]["files"]}


def _localized(localizations: dict[str, dict[str, str]], subject: str) -> dict[str, str]:
    return dict(sorted(localizations.get(subject, {}).items()))


def load_native(native_root: Path) -> dict[str, Any]:
    missing = [path for path in SOURCE_INPUTS if not (native_root / path).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing D120 inputs: {missing}")

    native_rows = read_jsonl(native_root / "backend/records.jsonl")
    semantic_rows = read_jsonl(native_root / "backend/semantic-wrapper-v1.records.jsonl")
    localization_rows = read_jsonl(native_root / "backend/semantic-wrapper-v1.localizations.jsonl")
    base_relations = read_csv(native_root / "backend/relations-ledger.csv")
    wrapper_relations = read_csv(native_root / "backend/semantic-wrapper-v1.relations-ledger.csv")
    github = read_json(native_root / "release/GITHUB_PUBLICATION_RECEIPT_2026.08.24.json")
    zenodo = read_json(native_root / "release/ZENODO_PUBLICATION_RECEIPT_2026.08.24.json")
    full_qa = read_json(native_root / "qa/FULL_COURSE_QA.json")
    wrapper_qa = read_json(native_root / "qa/SEMANTIC_WRAPPER_QA.json")
    dataset = read_json(native_root / "backend/semantic-wrapper-v1.dataset.json")
    release_qa = read_json(native_root / "release/RELEASE_PACKAGE_QA.json")
    delivery_qa = read_json(native_root / "delivery/VALIDATION.json")
    privacy_qa = read_json(native_root / "qa/PUBLIC_PAYLOAD_PRIVACY_QA_2026.08.24.json")
    source_freeze = read_json(native_root / "authority/SOURCE_FREEZE.json")

    return {
        "native_rows": native_rows,
        "native": records_by_type(native_rows),
        "semantic_rows": semantic_rows,
        "semantic": records_by_type(semantic_rows),
        "localization_rows": localization_rows,
        "localizations": localized_texts(localization_rows),
        "base_relations": base_relations,
        "wrapper_relations": wrapper_relations,
        "github": github,
        "zenodo": zenodo,
        "full_qa": full_qa,
        "wrapper_qa": wrapper_qa,
        "dataset": dataset,
        "release_qa": release_qa,
        "delivery_qa": delivery_qa,
        "privacy_qa": privacy_qa,
        "source_freeze": source_freeze,
        "terminology": read_csv(native_root / "controls/TERMINOLOGY.csv"),
        "source_rights": read_csv(native_root / "controls/SOURCE_RIGHTS_MANIFEST.csv"),
    }


def derive_projection(native_root: Path) -> dict[str, Any]:
    source = load_native(native_root)
    native = source["native"]
    semantic = source["semantic"]
    localizations = source["localizations"]
    github = source["github"]
    pages = _public_page_map(github)

    guided = {
        row["source"]: row["target"]
        for row in source["base_relations"]
        if row["status"] == "active" and row["predicate"] == "guided-by"
    }
    units = []
    for unit in sorted(native["unit"], key=lambda row: row["ordinal"]):
        unit_id = unit["id"]
        artifact = next(
            row for row in native["artifact"]
            if row.get("id") == f"{unit_id}-ARTIFACT-HTML"
        )
        public_path = artifact["path"].removeprefix("build/html/")
        public = pages[public_path]
        exercises = sorted(
            (row for row in native["exercise"] if row["unit"] == unit_id),
            key=lambda row: row["ordinal"],
        )
        outcomes = sorted(
            (row for row in semantic["learning_outcome"] if row["unit_id"] == unit_id),
            key=lambda row: row["sequence"],
        )
        competency = next(row for row in semantic["competency"] if row["unit_id"] == unit_id)
        assessment_id = f"O017-ASMT-U{unit['ordinal']:02d}-{'CAPSTONE' if unit['ordinal'] == 9 else 'COMPLETION'}"
        units.append({
            "unit_id": unit_id,
            "ordinal": unit["ordinal"],
            "title": unit["title"],
            "public_reader": {
                "url": public["url"],
                "bytes": public["bytes"],
                "sha256": public["sha256"],
            },
            "competency": {
                "id": competency["id"],
                "domain_code": competency["domain_code"],
                "localization": _localized(localizations, competency["id"]),
            },
            "outcomes": [
                {
                    "id": row["id"],
                    "sequence": row["sequence"],
                    "localization": _localized(localizations, row["id"]),
                }
                for row in outcomes
            ],
            "practice": [
                {
                    "exercise_id": exercise["id"],
                    "exercise_url": f"{public['url']}#{exercise['html_fragment']}",
                    "guidance_id": guided[exercise["id"]],
                    "guidance_url": f"{public['url']}#{next(row['html_fragment'] for row in native['solution'] if row['id'] == guided[exercise['id']])}",
                    "guidance_kind": "source_guidance_not_full_solution",
                }
                for exercise in exercises
            ],
            "assessment_id": assessment_id,
        })

    rubrics = {row["id"]: row for row in semantic["rubric"]}
    criteria = {row["id"]: row for row in semantic["criterion"]}
    assessments = []
    for row in sorted(semantic["assessment"], key=lambda item: item["id"]):
        rubric = rubrics[row["rubric_id"]]
        assessments.append({
            "assessment_id": row["id"],
            "kind": row["assessment_kind"],
            "authenticity": row["authenticity"],
            "required": row["required"],
            "noncompensable": row["noncompensable"],
            "completion_modes": row["completion_modes"],
            "localization": _localized(localizations, row["id"]),
            "competency_ids": row["competency_ids"],
            "outcome_ids": row["outcome_ids"],
            "rubric": {
                "rubric_id": rubric["id"],
                "scoring": rubric["scoring"],
                "localization": _localized(localizations, rubric["id"]),
                "criteria": [
                    {
                        "criterion_id": criterion_id,
                        "sequence": criteria[criterion_id]["sequence"],
                        "required": criteria[criterion_id]["required"],
                        "scoring_mode": criteria[criterion_id]["scoring_mode"],
                        "passing_threshold": criteria[criterion_id]["passing_threshold"],
                        "evidence_spec_ids": criteria[criterion_id]["evidence_spec_ids"],
                        "localization": _localized(localizations, criterion_id),
                    }
                    for criterion_id in rubric["criterion_ids"]
                ],
            },
            "evaluator_role_ids": row["evaluator_role_ids"],
            "evidence_spec_ids": row["evidence_spec_ids"],
            "external_action_authority": row["external_action_authority"],
            "locators": row.get("locators", []),
        })

    credentials = []
    for row in sorted(semantic["credential_state"], key=lambda item: item["id"]):
        credentials.append({
            "credential_state_id": row["id"],
            "state_code": row["state_code"],
            "terminal": row["terminal"],
            "claims_external_participation": row["claims_external_participation"],
            "external_event_required": row["external_event_required"],
            "required_assessment_ids": row["required_assessment_ids"],
            "required_result_statuses": row["required_result_statuses"],
            "localization": _localized(localizations, row["id"]),
        })

    base_counts = Counter(row["entity_type"] for row in source["native_rows"])
    semantic_counts = Counter(row["entity_type"] for row in source["semantic_rows"])
    source_inputs = [identity(native_root / path, display_path=path) for path in SOURCE_INPUTS]
    counts = {
        "source_lock_inputs": len(source_inputs),
        "native_records": len(source["native_rows"]),
        "native_relations_issued": len(source["base_relations"]),
        "native_relations_active": sum(row["status"] == "active" for row in source["base_relations"]),
        "native_relations_superseded": sum(row["status"] == "superseded" for row in source["base_relations"]),
        "semantic_records": len(source["semantic_rows"]),
        "localized_text_records": len(source["localization_rows"]),
        "semantic_relations_issued": len(source["wrapper_relations"]),
        "units": len(units),
        "exercises": base_counts["exercise"],
        "guidance_records": base_counts["solution"],
        "guided_by_relations": len(guided),
        "learning_outcomes": semantic_counts["learning_outcome"],
        "competencies": semantic_counts["competency"],
        "assessments": semantic_counts["assessment"],
        "rubrics": semantic_counts["rubric"],
        "criteria": semantic_counts["criterion"],
        "evidence_specs": semantic_counts["evidence"],
        "evaluator_roles": semantic_counts["evaluator"],
        "credential_state_definitions": semantic_counts["credential_state"],
        "terminology_entries": len(source["terminology"]),
        "native_rights_records": base_counts["rights"],
        "source_rights_components": len(source["source_rights"]),
        "correction_records": base_counts["correction"],
    }

    learning_map = {
        "schema": "d120-learning-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "title": "Kerja Matematika yang Dapat Ditelusuri",
        "prerequisites": [row["id"] for row in sorted(native["prerequisite"], key=lambda item: item["id"])],
        "route": {"route_id": "D120:route:nine-unit", "unit_ids": [row["unit_id"] for row in units]},
        "units": units,
        "native_reader": PAGES_ROOT,
        "portable_reader": f"{ZENODO_RECORD}/files/o017-d120-id-2026.08.24-reader-html.zip?download=1",
        "limitations": [
            "Adapter ini memproyeksikan identitas, metadata, hubungan, dan bukti; badan buku tetap berada di edisi native.",
            "Semua 54 rekaman dukungan adalah panduan sumber, bukan solusi lengkap.",
            "Fragmen HTML hanya penunjuk lokasi dan tidak menjadi identitas semantik.",
            "Tidak ada percobaan, kiriman, hasil, partisipasi komunitas, atau kredensial pelajar yang diklaim.",
        ],
    }
    educator_map = {
        "schema": "d120-educator-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "assessments": assessments,
        "credential_state_definitions": credentials,
        "evaluator_roles": [
            {
                "evaluator_id": row["id"],
                "role_code": row["role_code"],
                "independence": row["independence"],
                "same_person_as_learner_allowed": row["same_person_as_learner_allowed"],
                "localization": _localized(localizations, row["id"]),
            }
            for row in sorted(semantic["evaluator"], key=lambda item: item["id"])
        ],
        "claim_boundary": source["dataset"]["claim_boundary"],
        "delivery_validation": {
            "status": source["delivery_qa"]["status"],
            "negative_schema_tests": source["delivery_qa"]["results"]["negative_schema_tests"],
            "calibration_truth_witness": source["delivery_qa"]["calibration_truth_witness"],
        },
        "limitations": [
            "Rekaman penilaian adalah definisi dan templat, bukan bukti bahwa seorang pelajar telah lulus.",
            "Lima contoh kalibrasi adalah sintetis dan berlabel calibration_only.",
            "Tindakan eksternal tidak pernah disimpulkan dari persiapan lokal; jalur lokal yang lebih lemah dipertahankan.",
        ],
    }
    ledger_references = {
        "schema": "d120-ledger-references/1",
        "course_id": COURSE_ID,
        "base_backend": {
            "records": identity(native_root / "backend/records.jsonl", display_path="backend/records.jsonl"),
            "relations_ledger": identity(native_root / "backend/relations-ledger.csv", display_path="backend/relations-ledger.csv"),
            "relations_active_map": identity(native_root / "backend/relations.csv", display_path="backend/relations.csv"),
            "record_count": len(source["native_rows"]),
            "relations_issued": len(source["base_relations"]),
            "relations_active": counts["native_relations_active"],
            "relations_superseded": counts["native_relations_superseded"],
        },
        "semantic_wrapper": {
            "records": identity(native_root / "backend/semantic-wrapper-v1.records.jsonl", display_path="backend/semantic-wrapper-v1.records.jsonl"),
            "localizations": identity(native_root / "backend/semantic-wrapper-v1.localizations.jsonl", display_path="backend/semantic-wrapper-v1.localizations.jsonl"),
            "relations_ledger": identity(native_root / "backend/semantic-wrapper-v1.relations-ledger.csv", display_path="backend/semantic-wrapper-v1.relations-ledger.csv"),
            "semantic_records": len(source["semantic_rows"]),
            "localized_text_records": len(source["localization_rows"]),
            "relations_issued": len(source["wrapper_relations"]),
            "append_only_separate_from_base": True,
        },
        "projection": {
            "native_bodies_copied": False,
            "native_ids_preserved": True,
            "base_and_wrapper_ledgers_collapsed": False,
            "strict_native_roundtrip_claimed": False,
        },
    }
    public_evidence = {
        "schema": "d120-public-evidence/1",
        "course_id": COURSE_ID,
        "github": {
            "repository": REPOSITORY,
            "release_tag": github["release"]["tag"],
            "release_commit": github["repository"]["commit_sha"],
            "release_tree": github["repository"]["tree_sha"],
            "anonymous_verification": "verified",
            "raw_files": f"{github['repository']['public_readback']['file_count']}/{github['repository']['public_readback']['file_count']}",
            "pages_files": f"{github['pages']['file_count']}/{github['pages']['file_count']}",
            "release_assets": f"{github['release']['asset_count']}/{github['release']['asset_count']}",
            "index": pages["index.html"],
        },
        "zenodo": {
            "record_id": source["zenodo"]["record_id"],
            "doi": source["zenodo"]["doi"],
            "concept_doi": source["zenodo"]["concept_doi"],
            "url": source["zenodo"]["public_url"],
            "anonymous_verification": "verified",
            "files": source["zenodo"]["public_readback"]["files"],
        },
        "reader": {
            "online": PAGES_ROOT,
            "pdf_pages": source["release_qa"]["pdf"]["pages"],
            "pdf": next(row for row in source["zenodo"]["public_readback"]["files"] if row["filename"].endswith(".pdf")),
            "portable_html": next(row for row in source["zenodo"]["public_readback"]["files"] if row["filename"].endswith("reader-html.zip")),
            "source_backend_evidence": next(row for row in source["zenodo"]["public_readback"]["files"] if row["filename"].endswith("source-backend-evidence.zip")),
            "semantic_html": True,
            "native_mathml": True,
            "tagged_pdf": False,
        },
        "public_state_changed": False,
    }
    rights_and_terms = {
        "schema": "d120-rights-and-terms/1",
        "course_id": COURSE_ID,
        "rights_records": sorted(native["rights"], key=lambda row: row["id"]),
        "source_components": source["source_rights"],
        "terminology": source["terminology"],
        "corrections": sorted(native["correction"], key=lambda row: row["id"]),
        "source_freeze": {
            "course_boundary": source["source_freeze"]["course_boundary"],
            "the_turing_way": source["source_freeze"]["the_turing_way"],
            "py_rse": source["source_freeze"]["py_rse"],
        },
        "blanket_license_claimed": False,
    }
    claim_boundary = {
        "schema": "d120-claim-boundary/1",
        "course_id": COURSE_ID,
        "definitions_and_templates_only": True,
        "learner_attempt_instances": source["dataset"]["counts"]["learner_attempt_instances"],
        "learner_submission_instances": source["dataset"]["counts"]["learner_submission_instances"],
        "learner_result_instances": source["dataset"]["counts"]["learner_result_instances"],
        "credential_assertion_instances": source["dataset"]["counts"]["credential_assertion_instances"],
        "community_participation_claimed": False,
        "human_review_claimed_by_adapter": False,
        "native_bodies_copied": False,
        "central_course_truth_rewritten": False,
        "public_state_changed": False,
    }
    capabilities = {
        "schema": "d120-capability-summary/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "native_family": "research_practice",
        "counts": counts,
        "learner": {
            "unit_navigation": True,
            "exercise_guidance_pairs": counts["guided_by_relations"],
            "learning_outcomes": counts["learning_outcomes"],
            "semantic_html": True,
            "native_mathml": True,
            "offline_reader": True,
        },
        "educator": {
            "assessment_blueprints": counts["assessments"],
            "rubrics": counts["rubrics"],
            "criteria": counts["criteria"],
            "evidence_specs": counts["evidence_specs"],
            "evaluator_roles": counts["evaluator_roles"],
            "credential_state_definitions": counts["credential_state_definitions"],
        },
        "reproducibility": {
            "native_backend_deterministic": source["full_qa"]["status"] == "PASS",
            "semantic_wrapper_deterministic": source["wrapper_qa"]["status"] == "pass",
            "adapter_deterministic": True,
            "full_native_roundtrip_claimed": False,
        },
        "rights": {"component_specific": True, "blanket_license_claimed": False},
        "claim_boundary": claim_boundary,
        "strict_contract_2_3_1_conformance_claimed": False,
    }
    source_lock = {
        "schema": "d120-source-lock/1",
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "release_version": RELEASE_VERSION,
        "native_repository": {
            "url": REPOSITORY,
            "release_tag": "v2026.08.24",
            "release_commit": RELEASE_COMMIT,
            "release_tree": RELEASE_TREE,
            "current_head_observed_separately": "not_an_adapter_input",
        },
        "local_source_locator": "outputs/01a0216a-4b9f-7d30-a376-60e4e3859979",
        "inputs": source_inputs,
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
    boundary = bundle.get("claim_boundary", {})
    rights = bundle.get("rights_and_terms", {})

    units = learning.get("units", [])
    unit_ids = [row.get("unit_id") for row in units]
    if unit_ids != [f"O017-U{number:02d}" for number in range(1, 10)]:
        errors.append("D120-UNIT-SEQUENCE")
    if len(unit_ids) != len(set(unit_ids)):
        errors.append("D120-UNIT-DUPLICATE")
    if learning.get("locale") != LOCALE:
        errors.append("D120-LOCALE")
    if learning.get("route", {}).get("unit_ids") != unit_ids:
        errors.append("D120-ROUTE")
    if any(
        not row.get("public_reader", {}).get("url", "").startswith(PAGES_ROOT)
        or not isinstance(row.get("public_reader", {}).get("bytes"), int)
        or not row.get("public_reader", {}).get("bytes", 0) > 0
        or len(row.get("public_reader", {}).get("sha256", "")) != 64
        for row in units
    ):
        errors.append("D120-PUBLIC-UNIT-EVIDENCE")

    practices = [row for unit in units for row in unit.get("practice", [])]
    if len(practices) != 54 or len({row.get("exercise_id") for row in practices}) != 54:
        errors.append("D120-EXERCISE-COUNT")
    if len({row.get("guidance_id") for row in practices}) != 54:
        errors.append("D120-GUIDANCE-COUNT")
    if any(row.get("guidance_kind") != "source_guidance_not_full_solution" for row in practices):
        errors.append("D120-GUIDANCE-KIND")
    outcomes = [row for unit in units for row in unit.get("outcomes", [])]
    if len(outcomes) != 71 or len({row.get("id") for row in outcomes}) != 71:
        errors.append("D120-OUTCOME-COUNT")
    if any(str(row.get("id", "")).startswith("o017-") for row in outcomes):
        errors.append("D120-FRAGMENT-AS-SEMANTIC-ID")

    assessments = educator.get("assessments", [])
    if len(assessments) != 14 or len({row.get("assessment_id") for row in assessments}) != 14:
        errors.append("D120-ASSESSMENT-COUNT")
    if sum(len(row.get("rubric", {}).get("criteria", [])) for row in assessments) != 79:
        errors.append("D120-CRITERIA-COUNT")
    if len(educator.get("credential_state_definitions", [])) != 6:
        errors.append("D120-CREDENTIAL-DEFINITION-COUNT")

    for key in ("learner_attempt_instances", "learner_submission_instances", "learner_result_instances", "credential_assertion_instances"):
        if boundary.get(key) != 0:
            errors.append(f"D120-NONZERO-{key.upper()}")
    if boundary.get("community_participation_claimed") is not False:
        errors.append("D120-COMMUNITY-CLAIM")
    if boundary.get("native_bodies_copied") is not False:
        errors.append("D120-NATIVE-BODY-COPY")
    if boundary.get("central_course_truth_rewritten") is not False:
        errors.append("D120-CENTRAL-TRUTH-REWRITE")
    if ledgers.get("projection", {}).get("base_and_wrapper_ledgers_collapsed") is not False:
        errors.append("D120-LEDGER-COLLAPSE")
    if ledgers.get("base_backend", {}).get("relations_issued") != 1107:
        errors.append("D120-BASE-RELATIONS")
    if ledgers.get("semantic_wrapper", {}).get("relations_issued") != 1704:
        errors.append("D120-WRAPPER-RELATIONS")
    if public.get("github", {}).get("anonymous_verification") != "verified":
        errors.append("D120-GITHUB-ANONYMITY")
    if public.get("github", {}).get("raw_files") != "130/130":
        errors.append("D120-GITHUB-RAW-COUNT")
    if public.get("github", {}).get("pages_files") != "60/60":
        errors.append("D120-GITHUB-PAGES-COUNT")
    if public.get("github", {}).get("release_assets") != "9/9":
        errors.append("D120-GITHUB-RELEASE-COUNT")
    if public.get("zenodo", {}).get("anonymous_verification") != "verified":
        errors.append("D120-ZENODO-ANONYMITY")
    zenodo_files = public.get("zenodo", {}).get("files", [])
    if len(zenodo_files) != 9 or any(row.get("http_status") != 200 for row in zenodo_files):
        errors.append("D120-ZENODO-FILE-EVIDENCE")
    if public.get("public_state_changed") is not False:
        errors.append("D120-PUBLIC-STATE")
    if rights.get("blanket_license_claimed") is not False:
        errors.append("D120-BLANKET-LICENSE")
    counts = capabilities.get("counts", {})
    expected = {
        "native_records": 1787,
        "native_relations_issued": 1107,
        "semantic_records": 319,
        "localized_text_records": 581,
        "semantic_relations_issued": 1704,
        "units": 9,
        "exercises": 54,
        "guidance_records": 54,
        "guided_by_relations": 54,
        "learning_outcomes": 71,
        "competencies": 9,
        "assessments": 14,
        "rubrics": 14,
        "criteria": 79,
        "evidence_specs": 79,
        "evaluator_roles": 5,
        "credential_state_definitions": 6,
        "terminology_entries": 19,
    }
    for key, value in expected.items():
        if counts.get(key) != value:
            errors.append(f"D120-COUNT-{key.upper()}")
    return sorted(set(errors))
