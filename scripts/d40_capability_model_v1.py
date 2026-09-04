"""Shared model and invariants for the bounded D40 capability adapter.

The adapter is deliberately thin: it projects identities, relationships,
rights, evidence, and public download routes without copying native course
bodies.  Only Python's standard library is used.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


CONTRACT = "course-learning-capability/1"
COURSE_ID = "D40"
NATIVE_CORPUS_ID = "o010.d40"
DIONNE_COMMIT = "b1f909fff8f07a874f57bf8a3935a9cf5051fb3c"
DIONNE_TREE = "0422c877f9b65cd4217e26dea07d3e561de4ed29"
FENICSX_COMMIT = "033b0c2b773a5cef44620c650265e77ab678b15d"
FENICSX_TREE = "caf88b09353284eee11346b7b3dd9b5a1524750c"
RECORD_URL = "https://zenodo.org/records/22184259"
PDF_URL = (
    "https://zenodo.org/api/records/22184259/files/"
    "PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_LENGKAP.pdf/content"
)
ZIP_URL = (
    "https://zenodo.org/api/records/22184259/files/"
    "D40_COMPLETE_ID_20260831.zip/content"
)
MANIFEST_URL = (
    "https://zenodo.org/api/records/22184259/files/RELEASE_MANIFEST.json/content"
)
PDF_IDENTITY = {
    "bytes": 4_393_637,
    "sha256": "c4e4f470eeb096129e7bf7306422d316c93aaeed99d2b12890e08f15777ac13f",
}
ZIP_IDENTITY = {
    "bytes": 9_436_983,
    "sha256": "a370bba5ddb54081387a484a304b24af92691c3bc167db964c486625a79add59",
}
RELEASE_MANIFEST_IDENTITY = {
    "bytes": 92_798,
    "sha256": "3991fd2234e263134090c3686b93553dcab1215d86144509fd7937d5a4065a97",
}
EXPECTED_KIND_COUNTS = {
    "practice_problem": 48,
    "assessment_item": 16,
    "computational_lab": 4,
}
EXPECTED_EXECUTION_COUNTS = {
    "executed_notebooks": 4,
    "execution_surfaces": 8,
    "required_cells": 116,
    "code_cells": 54,
    "markdown_cells": 62,
    "source_nodes": 18,
}
EXPECTED_RIGHT_IDS = {
    "o010.rights.dionne.core",
    "o010.rights.d40.mastery",
    "o010.rights.fenicsx.tutorial",
    "o010.rights.fenicsx.runtime-record",
    "o010.rights.d40.composite-metadata",
}
EXPECTED_DIONNE_CHAPTER_IDS = {
    "o010.dionne.preface.chapter.743b50dc23efbd04",
    "o010.dionne.characteristics.chapter.chapcaract",
    "o010.dionne.chapter.02",
    "o010.dionne.chapter.03",
    "o010.dionne.chapter.04",
    "o010.dionne.chapter.05",
    "o010.dionne.chapter.06",
    "o010.dionne.chapter.07",
    "o010.dionne.chapter.08",
    "o010.dionne.laplace.chapter.chaplaplace",
    "o010.dionne.heat.chapter.chapheatequ",
    "o010.dionne.sobolev.chapter.sobolev-chap",
    "o010.dionne.elliptic.chapter.elliptic-pdes",
    "o010.dionne.shock-waves.chapter.chapshock",
}
EXPECTED_UNIT_KEYS = {
    "access_route_id",
    "archive_member_paths",
    "content_embedded",
    "course_id",
    "locale",
    "locale_neutral_id",
    "native_identity",
    "native_object_id",
    "native_parent_id",
    "native_source_id",
    "projection_order",
    "rights_id",
    "schema",
    "support_ids",
    "title_id",
    "unit_id",
    "unit_type",
}


class D40Error(ValueError):
    """A stable-code D40 adapter error."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def canonical_json_line(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": sha256_bytes(data)}


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, value: Any) -> None:
    write_bytes(path, canonical_json(value))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    write_bytes(path, b"".join(canonical_json_line(row) for row in rows))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise D40Error(f"D40-JSONL-OBJECT:{path}:{line_number}")
        rows.append(value)
    return rows


def expected_source_ids() -> set[str]:
    return {
        *(f"D40-P{i:02d}" for i in range(1, 49)),
        *(f"D40-A1-{i:02d}" for i in range(1, 9)),
        *(f"D40-A2-{i:02d}" for i in range(1, 9)),
        *(f"D40-L{i:02d}" for i in range(1, 5)),
    }


def expected_unit_ids() -> set[str]:
    return {
        *(f"o010.mastery.problem.d40-p{i:02d}" for i in range(1, 49)),
        *(f"o010.mastery.assessment.d40-a1-{i:02d}" for i in range(1, 9)),
        *(f"o010.mastery.assessment.d40-a2-{i:02d}" for i in range(1, 9)),
        *(f"o010.mastery.lab.d40-l{i:02d}" for i in range(1, 5)),
    }


def load_bundle(output_root: Path) -> dict[str, Any]:
    return {
        "course": read_json(output_root / "data/course.json"),
        "learning_map": read_json(output_root / "data/learning-map.json"),
        "units": read_jsonl(output_root / "data/units.jsonl"),
        "routes": read_jsonl(output_root / "data/routes.jsonl"),
        "capabilities": read_json(output_root / "data/capabilities.json"),
        "evidence": read_json(output_root / "data/evidence.json"),
        "execution": read_json(output_root / "data/execution.json"),
        "theory_links": read_json(output_root / "data/theory-links.json"),
        "rights": read_jsonl(output_root / "data/rights.jsonl"),
        "manifest": read_json(output_root / "manifest.json"),
    }


def _add(errors: list[str], condition: bool, code: str) -> None:
    if not condition:
        errors.append(code)


def _kind_count(units: list[dict[str, Any]], kind: str) -> int:
    return sum(row.get("unit_type") == kind for row in units)


def _contains_forbidden_payload_key(value: Any) -> bool:
    """Detect semantic/code bodies while allowing locators and identities."""

    forbidden = {
        "body",
        "code",
        "content",
        "content_text",
        "html",
        "latex",
        "markdown",
        "notebook",
        "payload",
        "prose",
        "raw_html",
        "solution_body",
        "solution_text",
        "source_code",
        "source_text",
        "text",
        "tex",
    }
    if isinstance(value, dict):
        keys = [str(key).casefold() for key in value]
        body_suffixes = (
            "_body",
            "_body_text",
            "_code",
            "_content",
            "_markdown",
            "_prose",
            "_source_text",
            "_solution_text",
        )
        return any(key in forbidden or key.endswith(body_suffixes) for key in keys) or any(
            _contains_forbidden_payload_key(item) for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_payload_key(item) for item in value)
    return False


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    """Return sorted stable error codes for projection defects."""

    errors: list[str] = []
    course = bundle["course"]
    learning_map = bundle["learning_map"]
    units = bundle["units"]
    routes = bundle["routes"]
    capabilities = bundle["capabilities"]
    evidence = bundle["evidence"]
    execution = bundle["execution"]
    theory_links = bundle["theory_links"]
    rights = bundle["rights"]
    manifest = bundle["manifest"]

    _add(errors, not _contains_forbidden_payload_key(bundle), "D40-PAYLOAD-EMBEDDED")

    _add(errors, course.get("schema") == "d40-capability-course/1", "D40-COURSE-SCHEMA")
    _add(errors, course.get("course_id") == COURSE_ID, "D40-COURSE-ID")
    _add(errors, course.get("native_corpus_id") == NATIVE_CORPUS_ID, "D40-NATIVE-CORPUS")
    _add(errors, course.get("contract_2_3_1_conformance") == "not_claimed", "D40-V231-CLAIM")
    _add(errors, course.get("content_projection") == "zero_copy_metadata_only", "D40-ZERO-COPY")
    _add(errors, course.get("full_native_roundtrip_claimed") is False, "D40-NATIVE-ROUNDTRIP-CLAIM")
    _add(errors, course.get("aggregation_license") is None, "D40-BLANKET-LICENSE")
    _add(
        errors,
        course.get("source_authority", {}).get("commit") == DIONNE_COMMIT
        and course.get("source_authority", {}).get("tree") == DIONNE_TREE,
        "D40-SOURCE-AUTHORITY",
    )
    public = course.get("public_lineage", {})
    _add(
        errors,
        public.get("pdf") == {"url": PDF_URL, **PDF_IDENTITY, "direct_public_file": True},
        "D40-PUBLIC-PDF",
    )
    _add(
        errors,
        public.get("zip") == {"url": ZIP_URL, **ZIP_IDENTITY, "direct_public_file": True},
        "D40-PUBLIC-ZIP",
    )
    _add(errors, public.get("record_url") == RECORD_URL, "D40-PUBLIC-RECORD")
    _add(errors, public.get("github_edition_repository") is None, "D40-GITHUB-EDITION-CLAIM")

    unit_ids = [row.get("unit_id") for row in units]
    source_ids = [row.get("native_source_id") for row in units]
    _add(errors, len(units) == 68, "D40-COUNT-UNITS")
    _add(errors, all(set(row) == EXPECTED_UNIT_KEYS for row in units), "D40-UNIT-SHAPE")
    _add(errors, len(set(unit_ids)) == len(unit_ids), "D40-UNIT-ID-DUPLICATE")
    _add(errors, set(unit_ids) == expected_unit_ids(), "D40-NATIVE-UNIT-ID-SET")
    _add(errors, set(source_ids) == expected_source_ids(), "D40-NATIVE-SOURCE-ID-SET")
    _add(errors, _kind_count(units, "practice_problem") == 48, "D40-COUNT-PRACTICE")
    _add(errors, _kind_count(units, "assessment_item") == 16, "D40-COUNT-ASSESSMENT")
    _add(errors, _kind_count(units, "computational_lab") == 4, "D40-COUNT-LABS")
    _add(
        errors,
        all(
            row.get("native_object_id") == row.get("unit_id")
            and row.get("rights_id") == "o010.rights.d40.mastery"
            and row.get("content_embedded") is False
            and row.get("archive_member_paths")
            and not any("://" in str(path) for path in row.get("archive_member_paths", []))
            for row in units
        ),
        "D40-UNIT-PROJECTION",
    )
    for row in units:
        support = row.get("support_ids", {})
        if row.get("unit_type") == "practice_problem":
            _add(errors, len(support.get("hint", [])) == 1, "D40-PRACTICE-HINTS")
            _add(errors, len(support.get("solution", [])) == 1, "D40-PRACTICE-SOLUTIONS")
        elif row.get("unit_type") == "assessment_item":
            for kind in ("prompt", "solution", "rubric", "alternate", "retake"):
                _add(errors, len(support.get(kind, [])) == 1, "D40-ASSESSMENT-SUPPORT")
        elif row.get("unit_type") == "computational_lab":
            _add(errors, len(support.get("lab_learner_document", [])) == 1, "D40-LAB-LEARNER")
            _add(errors, len(support.get("lab_solution_document", [])) == 1, "D40-LAB-SOLUTION")

    route_unit_ids = [row.get("native_object_id") for row in routes]
    _add(errors, len(routes) == 68 and set(route_unit_ids) == set(unit_ids), "D40-ROUTE-COVERAGE")
    _add(
        errors,
        all(
            row.get("access_url") == ZIP_URL
            and row.get("target_kind") == "public_zip_download_with_member_locator"
            and row.get("directly_addressable") is False
            and row.get("member_paths")
            and row.get("member_url") is None
            for row in routes
        ),
        "D40-ZIP-MEMBER-DIRECT-URL",
    )

    access = capabilities.get("accessibility", {})
    html_access = access.get("offline_html", {})
    pdf_access = access.get("pdf", {})
    _add(errors, html_access.get("availability") == "public_zip_member_only", "D40-HTML-AVAILABILITY")
    _add(errors, html_access.get("entrypoint") == "reader/html/index.html", "D40-HTML-ENTRYPOINT")
    _add(errors, html_access.get("direct_online_url") is None, "D40-HTML-DIRECT-URL")
    _add(errors, html_access.get("static_semantic_html") is True, "D40-HTML-SEMANTIC")
    _add(
        errors,
        html_access.get("math_representation") == "static_mathml"
        and html_access.get("mathml_elements") == 24_118
        and html_access.get("runtime_mathjax_required") is False
        and html_access.get("mathjax_claimed") is False
        and html_access.get("runtime_network_dependencies") == 0,
        "D40-HTML-MATH",
    )
    _add(
        errors,
        pdf_access.get("tagged_pdf_status") == "unknown_not_evidenced"
        and pdf_access.get("tagged_pdf_claimed") is False
        and pdf_access.get("complete_tounicode_status") == "unknown_not_evidenced"
        and pdf_access.get("wcag_conformance_claimed") is False
        and pdf_access.get("assistive_technology_user_testing_claimed") is False,
        "D40-PDF-TAGGED-CLAIM",
    )
    _add(
        errors,
        capabilities.get("learner", {}).get("full_native_roundtrip_claimed") is False,
        "D40-NATIVE-ROUNDTRIP-CLAIM",
    )
    coverage = capabilities.get("coverage", {})
    _add(errors, coverage.get("practice_problems") == 48, "D40-CAPABILITY-PRACTICE")
    _add(errors, coverage.get("assessment_items") == 16, "D40-CAPABILITY-ASSESSMENT")
    _add(errors, coverage.get("computational_labs") == 4, "D40-CAPABILITY-LABS")
    _add(
        errors,
        coverage.get("executed_notebooks") == 4
        and coverage.get("execution_surfaces") == 8
        and coverage.get("required_notebook_cells") == 116,
        "D40-CAPABILITY-EXECUTION",
    )

    dionne = evidence.get("dionne_import", {})
    _add(
        errors,
        dionne.get("zero_copy") is True
        and dionne.get("native_records_copied") == 0
        and dionne.get("object_count") == 3920
        and dionne.get("import_id") == "o010.d40.import.dionne-full"
        and dionne.get("component_id") == "o010.d40.component.dionne",
        "D40-DIONNE-ZERO-COPY",
    )
    corrections = evidence.get("source_corrections", {})
    _add(
        errors,
        corrections.get("record_count") == 500
        and corrections.get("status_counts") == {"applied": 499, "queued": 1}
        and corrections.get("queued_correction_ids") == ["O010-C002"],
        "D40-CORRECTIONS",
    )
    terminology = evidence.get("terminology", {})
    _add(
        errors,
        terminology.get("record_count") == 495
        and terminology.get("status_counts") == {"admitted": 492, "reserved": 3}
        and terminology.get("witness_verdict") == "PASS_NO_TERMINOLOGY_CHANGE_REQUIRED"
        and terminology.get("propagation_required") is False,
        "D40-TERMINOLOGY",
    )
    translation = evidence.get("translation_qa", {})
    _add(
        errors,
        translation.get("verdict") == "PASS"
        and translation.get("reference_closure_authority") == "deterministic_latex_build"
        and translation.get("static_regex_unresolved_are_not_build_failures") is True,
        "D40-TRANSLATION-QA",
    )

    rights_ids = [row.get("rights_id") for row in rights]
    _add(errors, len(rights) == 5 and set(rights_ids) == EXPECTED_RIGHT_IDS, "D40-RIGHTS-SET")
    runtime_right = next((r for r in rights if r.get("rights_id") == "o010.rights.fenicsx.runtime-record"), {})
    metadata_right = next((r for r in rights if r.get("rights_id") == "o010.rights.d40.composite-metadata"), {})
    _add(
        errors,
        runtime_right.get("license_id") == "record-level/unasserted"
        and runtime_right.get("rights_assertion") == "unasserted"
        and runtime_right.get("no_blanket_relicensing") is True,
        "D40-RUNTIME-RIGHTS",
    )
    _add(
        errors,
        metadata_right.get("license_id") == "record-level"
        and metadata_right.get("no_blanket_relicensing") is True,
        "D40-BLANKET-LICENSE",
    )

    counts = execution.get("counts", {})
    _add(
        errors,
        execution.get("adapter_execution_performed") is False
        and execution.get("projection") == "metadata_only_preexecuted_evidence",
        "D40-ADAPTER-EXECUTION",
    )
    _add(errors, counts == EXPECTED_EXECUTION_COUNTS, "D40-EXECUTION-COUNTS")
    notebooks = execution.get("executed_notebooks", [])
    surfaces = execution.get("execution_surfaces", [])
    cells = execution.get("required_cells", [])
    sources = execution.get("source_nodes", [])
    _add(errors, len(notebooks) == 4 and len({r.get("object_id") for r in notebooks}) == 4, "D40-EXECUTION-NOTEBOOKS")
    _add(errors, len(surfaces) == 8 and len({r.get("object_id") for r in surfaces}) == 8, "D40-EXECUTION-SURFACES")
    _add(errors, len(cells) == 116 and len({r.get("object_id") for r in cells}) == 116, "D40-EXECUTION-CELLS")
    _add(errors, len(sources) == 18 and len({r.get("object_id") for r in sources}) == 18, "D40-EXECUTION-SOURCES")
    _add(
        errors,
        sum(r.get("kind") == "notebook_code_cell" for r in cells) == 54
        and sum(r.get("kind") == "notebook_markdown_cell" for r in cells) == 62,
        "D40-EXECUTION-CELL-TYPES",
    )
    _add(
        errors,
        all(r.get("rights_id") == "o010.rights.fenicsx.tutorial" for r in notebooks + cells + sources)
        and all(r.get("rights_id") == "o010.rights.fenicsx.runtime-record" for r in surfaces),
        "D40-EXECUTION-RIGHTS",
    )

    chapters = theory_links.get("chapters", [])
    support_relations = theory_links.get("supports_relations", [])
    _add(
        errors,
        theory_links.get("schema") == "d40-capability-theory-links/1"
        and theory_links.get("zero_copy") is True
        and theory_links.get("native_bodies_copied") == 0,
        "D40-THEORY-ZERO-COPY",
    )
    _add(
        errors,
        len(chapters) == 14
        and {row.get("object_id") for row in chapters} == EXPECTED_DIONNE_CHAPTER_IDS
        and all(row.get("kind") == "chapter" and row.get("rights_id") == "o010.rights.dionne.core" for row in chapters),
        "D40-DIONNE-CHAPTERS",
    )
    _add(
        errors,
        len(support_relations) == 130
        and len({row.get("relation_id") for row in support_relations}) == 130
        and all(
            row.get("relation") == "supports"
            and row.get("source_id") in EXPECTED_DIONNE_CHAPTER_IDS
            and row.get("target_id") in expected_unit_ids()
            for row in support_relations
        ),
        "D40-THEORY-SUPPORTS",
    )

    required_map_keys = {
        "contract",
        "course_id",
        "locale",
        "native_dataset",
        "source_catalog",
        "units",
        "prerequisite_routes",
        "labs",
        "environments",
        "artifacts",
        "sources",
        "external_relation_nodes",
        "limitations",
    }
    _add(errors, set(learning_map) == required_map_keys, "D40-LEARNING-MAP-SHAPE")
    _add(
        errors,
        learning_map.get("contract") == CONTRACT
        and learning_map.get("course_id") == COURSE_ID
        and learning_map.get("locale") == "id-ID"
        and learning_map.get("native_dataset") == NATIVE_CORPUS_ID,
        "D40-LEARNING-MAP-CONTRACT",
    )
    catalog = learning_map.get("source_catalog", {})
    _add(
        errors,
        catalog == {
            "path": "RELEASE_MANIFEST.json",
            "bytes": RELEASE_MANIFEST_IDENTITY["bytes"],
            "sha256": RELEASE_MANIFEST_IDENTITY["sha256"],
            "url": MANIFEST_URL,
        },
        "D40-LEARNING-MAP-CATALOG",
    )
    map_units = learning_map.get("units", [])
    _add(errors, len(map_units) == 68, "D40-LEARNING-MAP-UNIT-COUNT")
    _add(errors, {row.get("id") for row in map_units} == set(unit_ids), "D40-LEARNING-MAP-UNIT-IDS")
    _add(errors, len(learning_map.get("prerequisite_routes", [])) == 108, "D40-PREREQUISITES")
    _add(errors, len(learning_map.get("labs", [])) == 4, "D40-LEARNING-MAP-LABS")
    _add(errors, len(learning_map.get("artifacts", [])) >= 3, "D40-LEARNING-MAP-ARTIFACTS")

    manifest_counts = manifest.get("counts", {})
    _add(errors, manifest.get("contract") == CONTRACT, "D40-CONTRACT")
    _add(errors, manifest.get("contract_projection_path") == "data/learning-map.json", "D40-CONTRACT-PROJECTION")
    _add(
        errors,
        manifest_counts.get("learning_units") == 68
        and manifest_counts.get("practice_problems") == 48
        and manifest_counts.get("assessment_items") == 16
        and manifest_counts.get("computational_labs") == 4
        and manifest_counts.get("executed_notebooks") == 4
        and manifest_counts.get("execution_surfaces") == 8
        and manifest_counts.get("required_notebook_cells") == 116
        and manifest_counts.get("rights_records") == 5
        and manifest_counts.get("dionne_imported_objects") == 3920
        and manifest_counts.get("dionne_chapters") == 14
        and manifest_counts.get("native_supports_relations") == 130,
        "D40-MANIFEST-COUNTS",
    )
    _add(
        errors,
        manifest.get("projection", {}).get("native_bodies_copied") is False
        and manifest.get("projection", {}).get("native_ids_preserved") is True
        and manifest.get("projection", {}).get("full_native_roundtrip_claimed") is False
        and manifest.get("projection", {}).get("public_state_changed") is False
        and manifest.get("projection", {}).get("blanket_license_asserted") is False,
        "D40-MANIFEST-PROJECTION",
    )
    return sorted(set(errors))


def apply_negative_mutation(bundle: dict[str, Any], mutation: str) -> dict[str, Any]:
    """Apply one named in-memory mutation used by negative fixtures."""

    changed = copy.deepcopy(bundle)
    if mutation == "duplicate_unit_id":
        changed["units"][1]["unit_id"] = changed["units"][0]["unit_id"]
    elif mutation == "fabricate_native_unit_identity":
        changed["units"][0]["unit_id"] = "d40.fabricated.unit"
        changed["units"][0]["native_object_id"] = "d40.fabricated.unit"
    elif mutation == "drop_practice":
        changed["units"].pop(next(i for i, row in enumerate(changed["units"]) if row["unit_type"] == "practice_problem"))
    elif mutation == "drop_assessment":
        changed["units"].pop(next(i for i, row in enumerate(changed["units"]) if row["unit_type"] == "assessment_item"))
    elif mutation == "drop_lab":
        changed["units"].pop(next(i for i, row in enumerate(changed["units"]) if row["unit_type"] == "computational_lab"))
    elif mutation == "direct_zip_member_url":
        changed["routes"][0]["access_url"] = ZIP_URL + "#reader/html/index.html"
        changed["routes"][0]["directly_addressable"] = True
        changed["routes"][0]["member_url"] = changed["routes"][0]["access_url"]
    elif mutation == "copy_dionne_object":
        changed["evidence"]["dionne_import"]["zero_copy"] = False
        changed["evidence"]["dionne_import"]["native_records_copied"] = 1
    elif mutation == "blanket_license":
        changed["course"]["aggregation_license"] = "CC-BY-4.0"
    elif mutation == "runtime_rights_upgrade":
        row = next(r for r in changed["rights"] if r["rights_id"] == "o010.rights.fenicsx.runtime-record")
        row["license_id"] = "CC-BY-4.0"
        row["rights_assertion"] = "asserted"
    elif mutation == "drop_rights_record":
        changed["rights"].pop()
    elif mutation == "claim_tagged_pdf":
        changed["capabilities"]["accessibility"]["pdf"]["tagged_pdf_status"] = "tagged"
        changed["capabilities"]["accessibility"]["pdf"]["tagged_pdf_claimed"] = True
    elif mutation == "claim_mathjax_runtime":
        changed["capabilities"]["accessibility"]["offline_html"]["math_representation"] = "runtime_mathjax_assistive_mathml"
        changed["capabilities"]["accessibility"]["offline_html"]["runtime_mathjax_required"] = True
    elif mutation == "claim_mathjax_only":
        changed["capabilities"]["accessibility"]["offline_html"]["mathjax_claimed"] = True
    elif mutation == "claim_complete_tounicode":
        changed["capabilities"]["accessibility"]["pdf"]["complete_tounicode_status"] = "complete"
    elif mutation == "claim_assistive_testing":
        changed["capabilities"]["accessibility"]["pdf"]["assistive_technology_user_testing_claimed"] = True
    elif mutation == "claim_learner_roundtrip":
        changed["capabilities"]["learner"]["full_native_roundtrip_claimed"] = True
    elif mutation == "claim_adapter_execution":
        changed["execution"]["adapter_execution_performed"] = True
    elif mutation == "embed_unit_body":
        changed["units"][0]["body"] = "forbidden payload"
    elif mutation == "embed_unit_source_code":
        changed["units"][0]["source_code"] = "forbidden payload"
    elif mutation == "drop_required_cell":
        changed["execution"]["required_cells"].pop()
    elif mutation == "drop_dionne_chapter":
        changed["theory_links"]["chapters"].pop()
    elif mutation == "drop_support_relation":
        changed["theory_links"]["supports_relations"].pop()
    elif mutation == "alter_public_pdf_hash":
        changed["course"]["public_lineage"]["pdf"]["sha256"] = "0" * 64
    elif mutation == "alter_source_authority":
        changed["course"]["source_authority"]["commit"] = "0" * 40
    elif mutation == "close_queued_correction":
        changed["evidence"]["source_corrections"]["status_counts"] = {"applied": 500, "queued": 0}
        changed["evidence"]["source_corrections"]["queued_correction_ids"] = []
    elif mutation == "claim_full_native_roundtrip":
        changed["course"]["full_native_roundtrip_claimed"] = True
        changed["manifest"]["projection"]["full_native_roundtrip_claimed"] = True
    else:
        raise D40Error(f"D40-UNKNOWN-NEGATIVE-MUTATION:{mutation}")
    return changed


def tree_identity(root: Path, relative_paths: Iterable[str]) -> dict[str, Any]:
    rows = []
    for relative in sorted(relative_paths):
        rows.append({"path": relative.replace("\\", "/"), **file_identity(root / relative)})
    return {
        "files": rows,
        "sha256": sha256_bytes(b"".join(canonical_json_line(row) for row in rows)),
    }
