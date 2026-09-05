"""Validate B40 source locks, exact maps, claim boundaries, HTML, and replay."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit

from build_b40_capability_v1 import (
    DEFAULT_ADAPTER,
    DEFAULT_DOCS,
    DEFAULT_NATIVE,
    NEGATIVE_FIXTURES,
    PROJECT,
)
from b40_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    EXPECTED_ANSWERS,
    EXPECTED_CONCEPTS,
    EXPECTED_CORRECTIONS,
    EXPECTED_RELATIONS,
    EXPECTED_RIGHTS,
    EXPECTED_TERMS,
    EXPECTED_UNITS,
    HUB_WORKSPACE_LOCATOR,
    LOCAL_SOURCE_LOCATOR,
    LOCALE,
    MIGRATION_RECEIPT,
    MIGRATION_RECEIPT_WORKSPACE,
    PRESENTATION_TITLE_OVERRIDES,
    PUBLIC_READBACK,
    PUBLIC_READBACK_WORKSPACE,
    canonical_json_bytes,
    derive_projection,
    identity,
    projection_errors,
    read_json,
    source_lock_errors,
    write_json,
)


BUNDLE_PATHS = {
    "source_lock": "input/source-lock.json",
    "learning_map": "data/learning-map.json",
    "educator_map": "data/educator-map.json",
    "concept_index": "data/concept-index.json",
    "relation_index": "data/relation-index.json",
    "ledger_references": "data/ledger-references.json",
    "public_evidence": "data/public-evidence.json",
    "rights_and_terms": "data/rights-and-terms.json",
    "claim_boundary": "data/claim-boundary.json",
    "capabilities": "data/capabilities.json",
}
EXPECTED_OUTPUT_PATHS = tuple(sorted((
    "README.md",
    *BUNDLE_PATHS.values(),
    "fixtures/negative-fixtures.json",
    "views/B40-pengajar.html",
    "views/B40.html",
)))
BUILD_OWNED_PATHS = tuple(sorted((*EXPECTED_OUTPUT_PATHS, "manifest.json")))
EXPECTED_DOCUMENTATION_OUTPUTS = tuple(sorted((
    "B40-pengajar.html",
    "B40.html",
    "concept-index.json",
    "educator-map.json",
    "learning-map.json",
    "ledger-references.json",
    "manifest.json",
    "public-evidence.json",
    "relation-index.json",
    "rights-and-terms.json",
    "validation.json",
)))
IMPLEMENTATION_PATHS = (
    "scripts/b40_capability_model_v1.py",
    "scripts/build_b40_capability_v1.py",
    "scripts/validate_b40_capability_v1.py",
)


class Page(HTMLParser):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.language: str | None = None
        self.ids: list[str] = []
        self.links: list[str | None] = []
        self.scripts = 0
        self.unit_checkboxes = 0
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.language = values.get("lang")
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "a":
            self.links.append(values.get("href"))
        if tag == "script":
            self.scripts += 1
        if tag == "input" and values.get("type") == "checkbox":
            self.unit_checkboxes += "unit-select" in set((values.get("class") or "").split())


def bytes_identity(data: bytes, display_path: str) -> dict[str, Any]:
    return {"path": display_path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def load_bundle_snapshot(adapter: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    bundle: dict[str, Any] = {}
    snapshots: dict[str, dict[str, Any]] = {}
    for key, relative in BUNDLE_PATHS.items():
        data = (adapter / relative).read_bytes()
        bundle[key] = json.loads(data)
        snapshots[relative] = bytes_identity(data, relative)
    return bundle, snapshots


def snapshots_for_paths(root: Path, paths: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    return {
        relative: identity(root / relative, display_path=relative)
        for relative in paths
    }


def manifest_errors(
    adapter: Path, manifest: dict[str, Any], source_lock: dict[str, Any], capability_counts: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if (
        manifest.get("schema") != "b40-capability-manifest/1"
        or manifest.get("course_id") != COURSE_ID
        or manifest.get("contract") != CONTRACT
        or manifest.get("locale") != LOCALE
    ):
        errors.append("B40-MANIFEST-IDENTITY")
    expected_projection = {
        "zero_copy_native_bodies": True,
        "native_segments_copied": False,
        "native_ids_preserved": True,
        "existing_reversible_migration_reused": True,
        "all_unit_ids_indexed": True,
        "all_relation_ids_indexed": True,
        "exercise_answer_bijection_preserved": True,
        "target_supplied_answer_provenance_preserved": True,
        "native_prerequisites_invented": False,
        "native_outcomes_invented": False,
        "native_semantic_html_claimed": False,
        "native_epub_claimed": False,
        "accessibility_conformance_claimed": False,
        "common_virtual_backend_materialized": False,
        "public_state_changed": False,
    }
    if manifest.get("projection") != expected_projection:
        errors.append("B40-MANIFEST-PROJECTION")
    if manifest.get("counts") != capability_counts:
        errors.append("B40-MANIFEST-COUNTS")
    paths = [row.get("path") for row in manifest.get("outputs", [])]
    if tuple(paths) != EXPECTED_OUTPUT_PATHS:
        errors.append("B40-MANIFEST-OUTPUT-INVENTORY")
    for row in manifest.get("outputs", []):
        relative = str(row.get("path", ""))
        path = adapter / relative
        if (
            Path(relative).is_absolute()
            or ".." in Path(relative).parts
            or not path.resolve().is_relative_to(adapter.resolve())
            or path.is_symlink()
            or not path.is_file()
            or row != identity(path, display_path=relative)
        ):
            errors.append(f"B40-OUTPUT-HASH:{row.get('path')}")
    expected_inputs = [
        source_lock.get("manifest_input"),
        *source_lock.get("native_inputs", []),
        source_lock.get("migration_input"),
        source_lock.get("public_readback_input"),
    ]
    if manifest.get("inputs") != expected_inputs:
        errors.append("B40-MANIFEST-INPUT-INVENTORY")
    if tuple(manifest.get("documentation_outputs", [])) != EXPECTED_DOCUMENTATION_OUTPUTS:
        errors.append("B40-MANIFEST-DOCUMENTATION-INVENTORY")
    if manifest.get("validation_path") != "validation.json":
        errors.append("B40-MANIFEST-VALIDATION-PATH")
    if manifest.get("public_documentation") != {
        "base_path": "docs/backend/b40",
        "learner_path": "docs/backend/b40/B40.html",
        "educator_path": "docs/backend/b40/B40-pengajar.html",
        "manifest_path": "docs/backend/b40/manifest.json",
        "validation_path": "docs/backend/b40/validation.json",
    }:
        errors.append("B40-MANIFEST-PUBLIC-RELATIONSHIPS")
    return sorted(set(errors))


def html_errors(adapter: Path, docs_root: Path, bundle: dict[str, Any]) -> tuple[list[str], int]:
    errors: list[str] = []
    pages = [
        (adapter / "views/B40.html", "learner"),
        (adapter / "views/B40-pengajar.html", "educator"),
    ]
    link_count = 0
    documentation_root = docs_root.parents[1].resolve()
    for path, label in pages:
        actual = path.read_text(encoding="utf-8")
        parsed = Page(actual)
        if parsed.language != "id":
            errors.append(f"B40-HTML-LANGUAGE:{path.name}")
        if len(parsed.ids) != len(set(parsed.ids)):
            errors.append(f"B40-HTML-DUPLICATE-ID:{path.name}")
        if parsed.scripts < (2 if label == "educator" else 1):
            errors.append(f"B40-HTML-NO-INTERACTION:{label}")
        if label == "educator" and parsed.unit_checkboxes != EXPECTED_UNITS:
            errors.append("B40-EDUCATOR-CHECKBOXES")
        for href in parsed.links:
            if not href or href in {"undefined", "null", "#"} or href != href.strip():
                errors.append(f"B40-HTML-EMPTY-LINK:{path.name}")
                continue
            parsed_href = urlsplit(href)
            if parsed_href.scheme not in {"", "https"} or href.startswith("//") or "\\" in href:
                errors.append(f"B40-HTML-SCHEME:{href}")
            if parsed_href.scheme == "":
                target = (docs_root / parsed_href.path).resolve()
                if target.is_dir():
                    target /= "index.html"
                if not target.is_relative_to(documentation_root) or not target.is_file():
                    errors.append(f"B40-HTML-BROKEN-LOCAL-LINK:{href}")
            link_count += 1
    learner = pages[0][0].read_text(encoding="utf-8")
    educator = pages[1][0].read_text(encoding="utf-8")
    for component in bundle["learning_map"]["components"]:
        if component["component_id"] not in learner or component["component_label_id"] not in learner:
            errors.append(f"B40-LEARNER-COMPONENT:{component['component_id']}")
        for chapter in component["chapters"]:
            if chapter["chapter_id"] not in learner:
                errors.append(f"B40-LEARNER-CHAPTER:{chapter['chapter_id']}")
            for section in chapter["sections"]:
                if section["section_id"] not in learner:
                    errors.append(f"B40-LEARNER-SECTION:{section['section_id']}")
    for unit in bundle["educator_map"]["selector"]["units"]:
        if unit["unit_id"] not in educator:
            errors.append(f"B40-EDUCATOR-UNIT:{unit['unit_id']}")
    required_learner = (
        "bukan buku teks HTML", "tidak mengklaim EPUB", "tidak menyediakan hasil belajar",
        "buku teks", "buku jawaban", "laboratorium Sage", "Hak penggunaan",
        "rights-and-terms.json", "Definisi", "Mengapa Sage?", "Python dan Sage",
        "judul native mentah", "Status publik saat ini", "Catatan native historis",
    )
    if any(fragment not in learner for fragment in required_learner):
        errors.append("B40-LEARNER-CLAIM-BOUNDARY")
    required_educator = ("1.035 jawaban", "Dua jawaban", "HLA-A0300", "B40-rencana-pengajar.json")
    if any(fragment not in educator for fragment in required_educator):
        errors.append("B40-EDUCATOR-PROVENANCE")
    if (
        "selectedIds.has(x.exercise_unit_id)||selectedIds.has(x.answer_unit_id)" not in educator
        or not {"teacher-filter", "kind-filter", "select-visible", "clear", "export", "selected-count"}.issubset(
            set(Page(educator).ids)
        )
    ):
        errors.append("B40-EDUCATOR-INTERACTION")
    return sorted(set(errors)), link_count


def documentation_errors(adapter: Path, docs_root: Path) -> list[str]:
    mappings = {
        "views/B40.html": "B40.html",
        "views/B40-pengajar.html": "B40-pengajar.html",
        "data/learning-map.json": "learning-map.json",
        "data/educator-map.json": "educator-map.json",
        "data/concept-index.json": "concept-index.json",
        "data/relation-index.json": "relation-index.json",
        "data/rights-and-terms.json": "rights-and-terms.json",
        "data/ledger-references.json": "ledger-references.json",
        "data/public-evidence.json": "public-evidence.json",
        "manifest.json": "manifest.json",
    }
    errors = []
    overlay_path = PROJECT / "backend/authority/central-course-surface-navigation-overlay-v1.json"
    overlay_by_document: dict[str, dict[str, Any]] = {}
    if overlay_path.is_file() and not overlay_path.is_symlink():
        overlay = read_json(overlay_path)
        if overlay.get("schema") == "central-course-surface-navigation-overlay-v1" and overlay.get("status") == "pass":
            overlay_by_document = {row.get("document"): row for row in overlay.get("files", [])}
    for source, target in mappings.items():
        source_path, target_path = adapter / source, docs_root / target
        if source_path.is_symlink() or target_path.is_symlink() or not source_path.is_file() or not target_path.is_file():
            errors.append(f"B40-DOC-MIRROR:{target}")
            continue
        source_bytes = source_path.read_bytes()
        target_bytes = target_path.read_bytes()
        if source_bytes == target_bytes:
            continue
        document = f"docs/backend/b40/{target}"
        row = overlay_by_document.get(document, {}) if target.endswith(".html") else {}
        source_fact = {
            "path": document,
            "bytes": len(source_bytes),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
        }
        target_fact = {
            "path": document,
            "bytes": len(target_bytes),
            "sha256": hashlib.sha256(target_bytes).hexdigest(),
        }
        if (
            row.get("source_body") != source_fact
            or row.get("hosted_surface") != target_fact
            or row.get("source_body_replay_exact") is not True
            or COURSE_ID not in row.get("course_ids", [])
        ):
            errors.append(f"B40-DOC-MIRROR:{target}")
    return errors


def mutate_cases(bundle: dict[str, Any]) -> list[tuple[str, str, Callable[[dict[str, Any]], None]]]:
    def symmetric_provenance_swap(value: dict[str, Any]) -> None:
        rows = value["educator_map"]["selector"]["exercise_answers"]
        upstream = next(row for row in rows if row["provenance_class"] == "native_upstream_answer")
        supplied = next(row for row in rows if row["provenance_class"] == "indonesian_edition_supplied")
        fields = (
            "provenance_class", "authority_answer_status", "authorization_event_id",
            "authorization_correction_id", "authorization_ledger_locator", "authorization_ledger_sha256",
        )
        left = {field: upstream.get(field) for field in fields}
        right = {field: supplied.get(field) for field in fields}
        upstream.update(right)
        supplied.update(left)

    return [
        ("duplicate_unit", "B40-UNIT-IDENTITY", lambda x: x["educator_map"]["selector"]["units"].append(copy.deepcopy(x["educator_map"]["selector"]["units"][0]))),
        ("missing_unit", "B40-UNIT-IDENTITY", lambda x: x["educator_map"]["selector"]["units"].pop()),
        ("unit_order_change", "B40-UNIT-ORDER", lambda x: x["learning_map"]["route"]["all_unit_ids"].reverse()),
        ("component_loss", "B40-LEARNER-ROUTE", lambda x: x["learning_map"]["components"].pop()),
        ("chapter_loss", "B40-LEARNER-ROUTE", lambda x: x["learning_map"]["components"][0]["chapters"].pop()),
        ("presentation_title_loss", "B40-PRESENTATION-TITLES", lambda x: x["learning_map"]["presentation_title_overrides"][0].update(presentation_title_id="dan")),
        ("route_assignment_loss", "B40-ROUTE-COVERAGE", lambda x: x["educator_map"]["selector"]["units"][0].update(route_node_id="missing-route-node")),
        ("prerequisite_invention", "B40-COURSE-PREREQUISITE", lambda x: x["learning_map"].update(program_prerequisites=["B10"])),
        ("outcome_invention", "B40-COURSE-OUTCOME", lambda x: x["learning_map"].update(outcomes_available=True)),
        ("answer_mapping_loss", "B40-ANSWER-BIJECTION", lambda x: x["educator_map"]["selector"]["exercise_answers"].pop()),
        ("duplicate_answer_mapping", "B40-ANSWER-BIJECTION", lambda x: x["educator_map"]["selector"]["exercise_answers"].append(copy.deepcopy(x["educator_map"]["selector"]["exercise_answers"][0]))),
        ("ordinal_answer_selector", "B40-ANSWER-ID-SELECTOR", lambda x: x["educator_map"]["selector"]["answer_selector"].update(ordinal_only_lookup_allowed=True)),
        ("answer_direction_reverse", "B40-ANSWER-DIRECTION", lambda x: x["educator_map"]["selector"]["exercise_answers"][0].update(relation_direction="exercise_to_answer")),
        ("answer_backpointer_corrupt", "B40-ANSWER-BACKPOINTER", lambda x: next(row for row in x["educator_map"]["selector"]["units"] if row["kind"] == "answer").update(answers_unit_id="missing-exercise")),
        ("answer_order_path_corrupt", "B40-ANSWER-ORDER-PATH", lambda x: x["educator_map"]["selector"]["exercise_answers"][0].update(answer_path_extends_exercise_path=False)),
        ("answer_locator_hash_corrupt", "B40-ANSWER-LOCATOR-HASH", lambda x: x["educator_map"]["selector"]["exercise_answers"][0].update(answer_target_sha256="0" * 64)),
        ("answer_provenance_collapse", "B40-ANSWER-PROVENANCE", lambda x: next(row for row in x["educator_map"]["selector"]["exercise_answers"] if row["provenance_class"] == "native_upstream_answer").update(provenance_class="indonesian_edition_supplied")),
        ("answer_provenance_symmetric_swap", "B40-ANSWER-PROVENANCE", symmetric_provenance_swap),
        ("answer_authorization_loss", "B40-ANSWER-AUTHORIZATION", lambda x: next(row for row in x["educator_map"]["selector"]["exercise_answers"] if row["provenance_class"] == "indonesian_edition_supplied").update(authorization_event_id=None)),
        ("concept_loss", "B40-CONCEPTS", lambda x: x["concept_index"]["concepts"].pop()),
        ("term_loss", "B40-TERMS", lambda x: x["concept_index"]["concepts"][0]["target_terms"].pop()),
        ("relation_loss", "B40-RELATIONS", lambda x: x["relation_index"]["relations"].pop()),
        ("relation_type_change", "B40-RELATION-TYPES", lambda x: x["relation_index"]["relations"][0].update(relation_type="answers")),
        ("relation_endpoint_change", "B40-RELATION-PROJECTION", lambda x: x["relation_index"]["relations"][0].update(source_id="missing-source")),
        ("projection_double_count", "B40-PROJECTION-DOUBLE-COUNT", lambda x: x["relation_index"].update(specialized_projection_duplicate_rows_materialized=EXPECTED_ANSWERS)),
        ("terminology_loss", "B40-LEDGER-CLOSURE", lambda x: x["rights_and_terms"]["terminology_reference"].update(term_count=113)),
        ("correction_loss", "B40-LEDGER-CLOSURE", lambda x: x["rights_and_terms"]["corrections_reference"].update(correction_count=306)),
        ("redundant_terminology_materialization", "B40-PROJECTION-REDUNDANCY", lambda x: x["rights_and_terms"].update(terminology=[{"id": "duplicate"}])),
        ("redundant_correction_materialization", "B40-PROJECTION-REDUNDANCY", lambda x: x["rights_and_terms"].update(corrections=[{"id": "duplicate"}])),
        ("rights_loss", "B40-RIGHTS", lambda x: x["rights_and_terms"]["component_rights"].pop()),
        ("artifact_page_change", "B40-ARTIFACTS", lambda x: x["public_evidence"]["native_artifacts"][0].update(page_count=434)),
        ("artifact_status_conflation", "B40-ARTIFACT-STATUS", lambda x: x["public_evidence"]["native_artifacts"][0].update(current_public_status="unpublished")),
        ("migration_roundtrip_downgrade", "B40-MIGRATION-ROUNDTRIP", lambda x: x["ledger_references"]["common_projection"].update(exact_reverse_extraction=22_130)),
        ("capability_summary_change", "B40-CAPABILITIES", lambda x: x["capabilities"]["learner"].update(ordered_component_navigation=False)),
        ("closed_public_access", "B40-PUBLIC-ACCESS", lambda x: x["public_evidence"].update(access_mode="authenticated")),
        ("public_checks_change", "B40-PUBLIC-EVIDENCE", lambda x: x["public_evidence"]["checks"].update(reader_landing_page_fetched=False)),
        ("credentials_recorded", "B40-PUBLIC-EVIDENCE", lambda x: x["public_evidence"].update(credentials_recorded=True)),
        ("reader_identity_change", "B40-PUBLIC-EVIDENCE", lambda x: x["public_evidence"]["reader"].update(sha256="0" * 64)),
        ("public_payload_injection", "B40-PUBLIC-ALLOWLIST", lambda x: x["public_evidence"]["github"].update(description="forbidden copied payload")),
        ("reader_payload_injection", "B40-PUBLIC-ALLOWLIST", lambda x: x["learning_map"]["public_reader_landing_page"].update(description="forbidden copied payload")),
        ("closed_zenodo", "B40-ZENODO-ACCESS", lambda x: x["public_evidence"]["zenodo"].update(access_right="restricted")),
        ("reader_scope_overclaim", "B40-READER-SCOPE", lambda x: x["public_evidence"]["reader"].update(scope="full_html_textbook")),
        ("semantic_html_overclaim", "B40-FORMAT-OVERCLAIM", lambda x: x["public_evidence"].update(native_semantic_html_claimed=True)),
        ("epub_overclaim", "B40-FORMAT-OVERCLAIM", lambda x: x["public_evidence"].update(native_epub_claimed=True)),
        ("accessibility_overclaim", "B40-FORMAT-OVERCLAIM", lambda x: x["public_evidence"].update(accessibility_conformance_claimed=True)),
        ("native_body_copy", "B40-BOUNDARY-NATIVE_BODIES_COPIED", lambda x: x["claim_boundary"].update(native_bodies_copied=True)),
        ("body_field_injection", "B40-DATA-BODY-COPY", lambda x: x["educator_map"]["selector"]["units"][0].update(body_text="forbidden")),
        ("native_segment_copy", "B40-BOUNDARY-NATIVE_SEGMENTS_COPIED", lambda x: x["claim_boundary"].update(native_segments_copied=True)),
        ("answer_join_inference", "B40-BOUNDARY-EXERCISE_ANSWER_JOINS_INFERRED", lambda x: x["claim_boundary"].update(exercise_answer_joins_inferred=True)),
        ("supplied_answer_retyping", "B40-BOUNDARY-TARGET_SUPPLIED_ANSWERS_RETYPED_AS_UPSTREAM", lambda x: x["claim_boundary"].update(target_supplied_answers_retyped_as_upstream=True)),
        ("authorization_omission", "B40-BOUNDARY-TARGET_SUPPLIED_AUTHORIZATION_OMITTED", lambda x: x["claim_boundary"].update(target_supplied_authorization_omitted=True)),
        ("blanket_license_claim", "B40-RIGHTS", lambda x: x["rights_and_terms"].update(blanket_license_claimed=True)),
        ("common_backend_materialization", "B40-BOUNDARY-COMMON_VIRTUAL_BACKEND_MATERIALIZED", lambda x: x["claim_boundary"].update(common_virtual_backend_materialized=True)),
        ("public_state_change", "B40-PUBLIC-ACCESS", lambda x: x["public_evidence"].update(public_state_changed=True)),
        ("unqualified_source_path", "B40-SOURCE-ROOT", lambda x: x["source_lock"]["manifest_input"].update(path="manifest.json")),
        ("source_lock_native_role_change", "B40-SOURCE-LOCK-IDENTITY", lambda x: x["source_lock"].update(native_role_id="R999")),
        ("source_repository_change", "B40-SOURCE-LOCK-REPOSITORY", lambda x: x["source_lock"]["native_repository"].update(source_commit="0" * 40)),
    ]


def locked_input_snapshot(
    source_lock: dict[str, Any], native_root: Path, hub_root: Path
) -> tuple[dict[str, bytes], list[str]]:
    specs = [
        (source_lock.get("manifest_input", {}), native_root / "manifest.json"),
        *[
            (
                row,
                native_root / str(row.get("path", "")).removeprefix(f"{LOCAL_SOURCE_LOCATOR}/"),
            )
            for row in source_lock.get("native_inputs", [])
        ],
        (source_lock.get("migration_input", {}), hub_root / MIGRATION_RECEIPT),
        (source_lock.get("public_readback_input", {}), hub_root / PUBLIC_READBACK),
    ]
    captured: dict[str, bytes] = {}
    errors: list[str] = []
    for expected, path in specs:
        display = str(expected.get("path", ""))
        if not path.is_file() or path.is_symlink():
            errors.append(f"B40-LOCKED-INPUT-FILE:{display}")
            continue
        data = path.read_bytes()
        if expected != bytes_identity(data, display):
            errors.append(f"B40-LOCKED-INPUT-HASH:{display}")
        captured[display] = data
    if len(captured) != 18:
        errors.append("B40-LOCKED-INPUT-INVENTORY")
    return captured, errors


def independent_native_projection_errors(inputs: dict[str, bytes], bundle: dict[str, Any]) -> list[str]:
    """Cross-check persisted projections directly against the hash-locked native bytes."""
    errors: list[str] = []

    def jsonl(relative: str) -> list[dict[str, Any]]:
        key = f"{LOCAL_SOURCE_LOCATOR}/{relative}"
        return [json.loads(line) for line in inputs[key].decode("utf-8").splitlines() if line.strip()]

    units = jsonl("units.jsonl")
    native_units = {row["id"]: row for row in units}
    projected_units = bundle["educator_map"]["selector"]["units"]
    projected_by_id = {row.get("unit_id"): row for row in projected_units}
    if len(native_units) != EXPECTED_UNITS or set(projected_by_id) != set(native_units):
        errors.append("B40-INDEPENDENT-UNIT-INVENTORY")
    direct_fields = {
        "kind": "unit_kind",
        "native_kind": "native_kind",
        "parent_id": "parent_id",
        "native_order": "order",
        "source_file_unit_id": "source_file_unit_id",
        "source_local_id": "source_local_id",
        "source_title": "source_title",
        "title_id": "target_title",
        "source_locator": "source_locator",
        "source_sha256": "source_sha256",
        "target_locator": "target_locator",
        "target_sha256": "target_sha256",
        "language": "language",
        "locale": "locale",
        "target_language": "target_language",
        "target_locale": "target_locale",
        "rights_id": "rights_id",
        "concept_ids": "concept_ids",
        "prerequisite_ids": "prerequisite_ids",
        "prerequisite_status": "prerequisite_status",
        "translation_state": "translation_state",
        "answers_unit_id": "answers_unit_id",
        "exercise_environment_order": "exercise_environment_order",
        "exercise_order": "exercise_order",
    }
    for unit_id, native in native_units.items():
        projected = projected_by_id.get(unit_id, {})
        if any(projected.get(target) != native.get(source) for target, source in direct_fields.items()):
            errors.append("B40-INDEPENDENT-UNIT-METADATA")
            break
        if projected.get("segment_count") != len(native.get("segment_ids", [])):
            errors.append("B40-INDEPENDENT-UNIT-SEGMENTS")
            break
        override = PRESENTATION_TITLE_OVERRIDES.get(unit_id)
        expected_presentation = override["presentation_title_id"] if override else native.get("target_title")
        expected_basis = override["basis"] if override else "native_title"
        if (
            projected.get("native_title_id") != native.get("target_title")
            or projected.get("presentation_title_id") != expected_presentation
            or projected.get("presentation_title_basis") != expected_basis
        ):
            errors.append("B40-INDEPENDENT-PRESENTATION-TITLE")
            break

    children: dict[str, list[dict[str, Any]]] = {}
    roots: list[dict[str, Any]] = []
    for row in units:
        if row.get("parent_id") in native_units:
            children.setdefault(row["parent_id"], []).append(row)
        else:
            roots.append(row)
    for rows in children.values():
        rows.sort(key=lambda row: (row.get("order", 0), row["id"]))
    roots.sort(key=lambda row: (row.get("order", 0), row["id"]))
    native_order: list[str] = []

    def visit(unit_id: str) -> None:
        native_order.append(unit_id)
        for child in children.get(unit_id, []):
            visit(child["id"])

    for root in roots:
        visit(root["id"])
    if [row.get("unit_id") for row in projected_units] != native_order:
        errors.append("B40-INDEPENDENT-UNIT-ORDER")

    reader = csv.DictReader(io.StringIO(
        inputs[f"{LOCAL_SOURCE_LOCATOR}/relations.csv"].decode("utf-8-sig"), newline=""
    ))
    native_relations = list(reader)
    expected_relations = [{
        "relation_id": row["relation_id"],
        "relation_type": row["relation_type"],
        "source_id": row["source_id"],
        "target_id": row["target_id"],
        "order": int(row["order"]),
        "source_locator": row.get("source_locator"),
        "edition_id": row.get("edition_id"),
        "rights_id": row.get("rights_id"),
        "status": row.get("status"),
    } for row in sorted(native_relations, key=lambda row: row["relation_id"])]
    if bundle["relation_index"].get("relations") != expected_relations:
        errors.append("B40-INDEPENDENT-RELATION-PROJECTION")

    native_answer_pairs = {
        row["relation_id"]: (row["source_id"], row["target_id"])
        for row in native_relations if row["relation_type"] == "answers"
    }
    projected_answer_pairs = {
        row.get("relation_id"): (row.get("answer_unit_id"), row.get("exercise_unit_id"))
        for row in bundle["educator_map"]["selector"]["exercise_answers"]
    }
    if projected_answer_pairs != native_answer_pairs:
        errors.append("B40-INDEPENDENT-ANSWER-PAIRS")
    answer_rows = bundle["educator_map"]["selector"]["exercise_answers"]
    authorization_fields = (
        "authority_answer_status", "authorization_event_id", "authorization_correction_id",
        "authorization_ledger_locator", "authorization_ledger_sha256",
    )
    for row in answer_rows:
        native_answer = native_units.get(row.get("answer_unit_id"), {})
        expected_provenance = (
            "indonesian_edition_supplied"
            if native_answer.get("provenance_kind") == "indonesian_edition_supplied"
            else "native_upstream_answer"
        )
        if (
            row.get("provenance_class") != expected_provenance
            or any(row.get(field) != native_answer.get(field) for field in authorization_fields)
        ):
            errors.append("B40-INDEPENDENT-ANSWER-PROVENANCE")
            break

    native_concepts = {row["id"]: row for row in jsonl("concepts.jsonl")}
    native_terms = {row["id"]: row for row in jsonl("terminology.jsonl")}
    projected_concepts = {row.get("concept_id"): row for row in bundle["concept_index"].get("concepts", [])}
    if set(projected_concepts) != set(native_concepts):
        errors.append("B40-INDEPENDENT-CONCEPT-INVENTORY")
    elif any(
        [term.get("id") for term in projected_concepts[concept_id].get("target_terms", [])]
        != native.get("target_term_ids", [])
        for concept_id, native in native_concepts.items()
    ) or {
        term.get("id")
        for concept in projected_concepts.values()
        for term in concept.get("target_terms", [])
    } != set(native_terms):
        errors.append("B40-INDEPENDENT-TERM-INVENTORY")

    native_correction_ids = {row["id"] for row in jsonl("corrections.jsonl")}
    projected_correction_ids = {row.get("id") for row in bundle["ledger_references"].get("corrections", [])}
    if native_correction_ids != projected_correction_ids:
        errors.append("B40-INDEPENDENT-CORRECTION-INVENTORY")
    native_rights = sorted(jsonl("rights.jsonl"), key=lambda row: row["id"])
    if bundle["rights_and_terms"].get("component_rights") != native_rights:
        errors.append("B40-INDEPENDENT-RIGHTS-PROJECTION")

    native_artifacts = {row["id"]: row for row in jsonl("artifacts.jsonl")}
    projected_artifacts = {row.get("id"): row for row in bundle["public_evidence"].get("native_artifacts", [])}
    artifact_fields = ("bytes", "page_count", "sha256", "source_locator", "target_locator", "rights_id")
    if set(native_artifacts) != set(projected_artifacts) or any(
        any(projected_artifacts[artifact_id].get(field) != native.get(field) for field in artifact_fields)
        or projected_artifacts[artifact_id].get("native_publication_status") != native.get("publication_status")
        or projected_artifacts[artifact_id].get("native_status_recorded_on") != native.get("recorded_on")
        for artifact_id, native in native_artifacts.items()
    ):
        errors.append("B40-INDEPENDENT-ARTIFACT-PROJECTION")
    return sorted(set(errors))


def isolated_build(native_root: Path, hub_root: Path, adapter: Path, docs_root: Path | None = None) -> None:
    output_arguments = ["--no-docs"] if docs_root is None else ["--docs-root", str(docs_root)]
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            (
                "import runpy,sys;"
                "module_dir=sys.argv.pop(1);script=sys.argv.pop(1);"
                "sys.path.insert(0,module_dir);sys.argv[0]=script;"
                "runpy.run_path(script,run_name='__main__')"
            ),
            str(PROJECT / "scripts"),
            str(PROJECT / "scripts/build_b40_capability_v1.py"),
            "--native-root",
            str(native_root),
            "--hub-root",
            str(hub_root),
            "--adapter",
            str(adapter),
            *output_arguments,
        ],
        cwd=PROJECT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"B40 isolated build failed: {result.stderr.strip()}")


def tree_identity(root: Path, paths: tuple[str, ...]) -> tuple[int, str]:
    rows = []
    for relative in sorted(path.replace("\\", "/") for path in paths):
        path = root / relative
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise AssertionError(f"B40 fixed replay member is missing or unsafe: {relative}")
        data = path.read_bytes()
        rows.append(f"{relative}\t{len(data)}\t{hashlib.sha256(data).hexdigest()}\n")
    blob = "".join(rows).encode("utf-8")
    return len(rows), hashlib.sha256(blob).hexdigest()


def invalidate_validation_receipts(adapter: Path, docs_root: Path) -> None:
    for path in (adapter / "validation.json", docs_root / "validation.json"):
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise AssertionError(f"B40 validation receipt target is not a regular file: {path}")
            path.unlink()


def publish_validation_pair(
    adapter_receipt: Path,
    docs_receipt: Path,
    data: bytes,
    *,
    replace: Callable[[str | bytes | Path, str | bytes | Path], None] = os.replace,
) -> None:
    targets = (adapter_receipt, docs_receipt)
    staged: list[Path] = []
    backups: dict[Path, Path] = {}
    published: list[Path] = []
    try:
        for target in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            descriptor, name = tempfile.mkstemp(
                prefix=f".{target.name}.b40-", suffix=".tmp", dir=target.parent
            )
            temporary = Path(name)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            staged.append(temporary)
        for target in targets:
            if target.exists():
                descriptor, name = tempfile.mkstemp(
                    prefix=f".{target.name}.b40-backup-", suffix=".tmp", dir=target.parent
                )
                os.close(descriptor)
                backup = Path(name)
                backup.unlink()
                replace(target, backup)
                backups[target] = backup
        for temporary, target in zip(staged, targets, strict=True):
            replace(temporary, target)
            published.append(target)
    except Exception:
        for target in published:
            if target.exists():
                target.unlink()
        for target, backup in backups.items():
            if backup.exists():
                os.replace(backup, target)
        raise
    finally:
        for temporary in staged:
            if temporary.exists():
                temporary.unlink()
        for backup in backups.values():
            if backup.exists():
                backup.unlink()


def validate(native_root: Path, hub_root: Path, adapter: Path, docs_root: Path) -> dict[str, Any]:
    invalidate_validation_receipts(adapter, docs_root)
    implementation = snapshots_for_paths(PROJECT, IMPLEMENTATION_PATHS)
    bundle, bundle_snapshots = load_bundle_snapshot(adapter)
    manifest_bytes = (adapter / "manifest.json").read_bytes()
    manifest_identity = bytes_identity(manifest_bytes, "manifest.json")
    manifest = json.loads(manifest_bytes)
    committed_snapshot = snapshots_for_paths(adapter, BUILD_OWNED_PATHS)
    input_bytes, input_snapshot_errors = locked_input_snapshot(bundle["source_lock"], native_root, hub_root)
    errors = projection_errors(bundle)
    errors.extend(input_snapshot_errors)
    errors.extend(source_lock_errors(bundle["source_lock"], native_root, hub_root))
    errors.extend(manifest_errors(
        adapter, manifest, bundle["source_lock"], bundle["capabilities"].get("counts", {})
    ))
    errors.extend(independent_native_projection_errors(input_bytes, bundle))
    html_failures, links = html_errors(adapter, docs_root, bundle)
    errors.extend(html_failures)
    errors.extend(documentation_errors(adapter, docs_root))

    fresh = derive_projection(native_root, hub_root)
    for key in bundle:
        if bundle[key] != fresh[key]:
            errors.append(f"B40-FRESH-PROJECTION:{key}")

    migration = json.loads(input_bytes[MIGRATION_RECEIPT_WORKSPACE])
    public = json.loads(input_bytes[PUBLIC_READBACK_WORKSPACE])
    if (
        migration.get("validation", {}).get("result") != "pass"
        or migration.get("coverage", {}).get("exact_reverse_extraction") != 22_131
        or migration.get("target", {}).get("virtual_records_jsonl_sha256") != "fa42e1d8adf3516afa9fa7c31cfe4144d1ff40e1d9e2230e139810a2b161c049"
        or migration.get("materialization", {}).get("virtual_records_materialized") is not False
    ):
        errors.append("B40-MIGRATION-RECEIPT")
    if (
        public.get("access_mode") != "anonymous_no_credentials"
        or public.get("checks", {}).get("external_state_changed") is not False
        or public.get("checks", {}).get("exercise_answer_bijection_verified") is not True
        or public.get("native_backend", {}).get("counts", {}).get("native_records_total") != 22_131
        or public.get("native_backend", {}).get("counts", {}).get("entity_records_excluding_csv_relations") != 8_132
    ):
        errors.append("B40-PUBLIC-READBACK")
    zenodo = public.get("zenodo", {})
    if (
        zenodo.get("record_id") != 22070458
        or zenodo.get("doi") != "10.5281/zenodo.22070458"
        or zenodo.get("concept_record_id") != 22070457
        or zenodo.get("concept_doi") != "10.5281/zenodo.22070457"
        or zenodo.get("status") != "published"
        or zenodo.get("access_right") != "open"
    ):
        errors.append("B40-ZENODO-LINEAGE")

    fixture_file = read_json(adapter / "fixtures/negative-fixtures.json")
    expected_fixture_rows = [{"name": name, "expected_error": error} for name, error in NEGATIVE_FIXTURES]
    if fixture_file.get("fixtures") != expected_fixture_rows:
        errors.append("B40-NEGATIVE-FIXTURE-INDEX")
    negative = []
    mutations = mutate_cases(bundle)
    mutation_pairs = [(name, expected) for name, expected, _ in mutations]
    special_pairs = [
        ("input_hash_change", "B40-SOURCE-HASH:units.jsonl"),
        ("manifest_count_change", "B40-MANIFEST-COUNTS"),
        ("stale_receipt_survival", "B40-STALE-RECEIPT"),
        ("publication_noise_in_replay", "B40-REPLAY-INVENTORY"),
        ("paired_receipt_partial_publish", "B40-RECEIPT-ROLLBACK"),
    ]
    if [*mutation_pairs, *special_pairs] != NEGATIVE_FIXTURES:
        errors.append("B40-NEGATIVE-FIXTURE-COVERAGE")
    for name, expected, mutator in mutations:
        altered = copy.deepcopy(bundle)
        mutator(altered)
        observed = projection_errors(altered)
        rejected = expected in observed
        if not rejected:
            errors.append(f"B40-NEGATIVE-ACCEPTED:{name}")
        negative.append({"fixture": name, "expected_error": expected, "state": "rejected" if rejected else "accepted"})
    altered_lock = copy.deepcopy(bundle["source_lock"])
    altered_lock["native_inputs"][-1]["sha256"] = "0" * 64
    expected = "B40-SOURCE-HASH:units.jsonl"
    observed = source_lock_errors(altered_lock, native_root, hub_root)
    rejected = expected in observed
    if not rejected:
        errors.append("B40-NEGATIVE-ACCEPTED:input_hash_change")
    negative.append({"fixture": "input_hash_change", "expected_error": expected, "state": "rejected" if rejected else "accepted"})

    altered_manifest = copy.deepcopy(manifest)
    altered_manifest["counts"]["units"] -= 1
    expected = "B40-MANIFEST-COUNTS"
    observed = manifest_errors(
        adapter, altered_manifest, bundle["source_lock"], bundle["capabilities"].get("counts", {})
    )
    rejected = expected in observed
    if not rejected:
        errors.append("B40-NEGATIVE-ACCEPTED:manifest_count_change")
    negative.append({"fixture": "manifest_count_change", "expected_error": expected, "state": "rejected" if rejected else "accepted"})

    with (
        tempfile.TemporaryDirectory(prefix="b40-adapter-replay-a-") as first_temporary,
        tempfile.TemporaryDirectory(prefix="b40-adapter-replay-b-") as second_temporary,
    ):
        first = Path(first_temporary) / "adapter"
        first_docs = Path(first_temporary) / "docs"
        second = Path(second_temporary) / "adapter"
        for stale in (first / "validation.json", first_docs / "validation.json"):
            stale.parent.mkdir(parents=True, exist_ok=True)
            stale.write_text('{"schema":"stale","state":"pass"}\n', encoding="utf-8")
        isolated_build(native_root, hub_root, first, first_docs)
        stale_rejected = not (first / "validation.json").exists() and not (first_docs / "validation.json").exists()
        if not stale_rejected:
            errors.append("B40-NEGATIVE-ACCEPTED:stale_receipt_survival")
        negative.append({
            "fixture": "stale_receipt_survival",
            "expected_error": "B40-STALE-RECEIPT",
            "state": "rejected" if stale_rejected else "accepted",
        })
        isolated_build(native_root, hub_root, second)
        first_count, first_tree = tree_identity(first, BUILD_OWNED_PATHS)
        second_count, second_tree = tree_identity(second, BUILD_OWNED_PATHS)
        if (first_count, first_tree) != (second_count, second_tree):
            errors.append("B40-TWO-BUILD-REPLAY")
        committed_count, committed_tree = tree_identity(adapter, BUILD_OWNED_PATHS)
        if (committed_count, committed_tree) != (first_count, first_tree):
            errors.append("B40-COMMITTED-REPLAY")
        publication = first / "publication/GITHUB_READBACK_FIXTURE.json"
        publication.parent.mkdir(parents=True, exist_ok=True)
        publication.write_text('{"state":"external-receipt"}\n', encoding="utf-8")
        publication_count, publication_tree = tree_identity(first, BUILD_OWNED_PATHS)
        publication_rejected = (publication_count, publication_tree) == (first_count, first_tree)
        if not publication_rejected:
            errors.append("B40-NEGATIVE-ACCEPTED:publication_noise_in_replay")
        negative.append({
            "fixture": "publication_noise_in_replay",
            "expected_error": "B40-REPLAY-INVENTORY",
            "state": "rejected" if publication_rejected else "accepted",
        })

    with tempfile.TemporaryDirectory(prefix="b40-receipt-rollback-") as rollback_temporary:
        rollback_root = Path(rollback_temporary)
        rollback_adapter = rollback_root / "adapter/validation.json"
        rollback_docs = rollback_root / "docs/validation.json"
        replace_calls = 0

        def fail_second_replace(source: str | bytes | Path, target: str | bytes | Path) -> None:
            nonlocal replace_calls
            replace_calls += 1
            if replace_calls == 2:
                raise OSError("deterministic paired-publication failure fixture")
            os.replace(source, target)

        try:
            publish_validation_pair(
                rollback_adapter,
                rollback_docs,
                b'{"state":"pass"}\n',
                replace=fail_second_replace,
            )
            rollback_rejected = False
        except OSError:
            rollback_rejected = (
                not rollback_adapter.exists()
                and not rollback_docs.exists()
                and not list(rollback_root.rglob("*.tmp"))
            )
        if not rollback_rejected:
            errors.append("B40-NEGATIVE-ACCEPTED:paired_receipt_partial_publish")
        negative.append({
            "fixture": "paired_receipt_partial_publish",
            "expected_error": "B40-RECEIPT-ROLLBACK",
            "state": "rejected" if rollback_rejected else "accepted",
        })

    final_inputs, final_input_errors = locked_input_snapshot(bundle["source_lock"], native_root, hub_root)
    errors.extend(final_input_errors)
    if {
        path: bytes_identity(data, path) for path, data in final_inputs.items()
    } != {
        path: bytes_identity(data, path) for path, data in input_bytes.items()
    }:
        errors.append("B40-INPUT-SNAPSHOT-CHANGED")
    if snapshots_for_paths(adapter, BUILD_OWNED_PATHS) != committed_snapshot:
        errors.append("B40-COMMITTED-SNAPSHOT-CHANGED")
    if snapshots_for_paths(adapter, tuple(BUNDLE_PATHS.values())) != bundle_snapshots:
        errors.append("B40-BUNDLE-SNAPSHOT-CHANGED")
    if snapshots_for_paths(PROJECT, IMPLEMENTATION_PATHS) != implementation:
        errors.append("B40-IMPLEMENTATION-SNAPSHOT-CHANGED")
    final_bundle, final_bundle_snapshots = load_bundle_snapshot(adapter)
    if final_bundle_snapshots != bundle_snapshots or final_bundle != bundle:
        errors.append("B40-FINAL-BUNDLE-CHANGED")
    final_manifest_bytes = (adapter / "manifest.json").read_bytes()
    final_manifest = json.loads(final_manifest_bytes)
    if final_manifest_bytes != manifest_bytes:
        errors.append("B40-FINAL-MANIFEST-CHANGED")
    errors.extend(projection_errors(final_bundle))
    errors.extend(independent_native_projection_errors(final_inputs, final_bundle))
    errors.extend(source_lock_errors(final_bundle["source_lock"], native_root, hub_root))
    errors.extend(manifest_errors(
        adapter,
        final_manifest,
        final_bundle["source_lock"],
        final_bundle["capabilities"].get("counts", {}),
    ))
    errors.extend(documentation_errors(adapter, docs_root))
    final_html_failures, final_links = html_errors(adapter, docs_root, final_bundle)
    errors.extend(final_html_failures)
    if final_links != links:
        errors.append("B40-FINAL-HTML-LINK-INVENTORY")
    final_fresh = derive_projection(native_root, hub_root)
    for key in final_bundle:
        if final_bundle[key] != final_fresh[key]:
            errors.append(f"B40-FINAL-FRESH-PROJECTION:{key}")
    final_fixture_file = read_json(adapter / "fixtures/negative-fixtures.json")
    if final_fixture_file.get("fixtures") != expected_fixture_rows:
        errors.append("B40-FINAL-NEGATIVE-FIXTURE-INDEX")

    if errors:
        raise AssertionError("; ".join(sorted(set(errors))))
    receipt = {
        "schema": "b40-capability-validation/1",
        "state": "pass",
        "course_id": COURSE_ID,
        "contract": CONTRACT,
        "locale": LOCALE,
        "source_hashes_verified": len(manifest["inputs"]),
        "native_manifest_hashes_verified": 15,
        "counts": manifest["counts"],
        "checks": {
            "all_3541_stable_units_indexed_without_body_text": True,
            "three_component_seventeen_chapter_fifty_seven_section_route": True,
            "all_13999_native_relations_indexed": True,
            "all_114_concepts_and_terms_indexed": True,
            "all_307_corrections_indexed": True,
            "all_11_component_rights_preserved": True,
            "all_8_native_artifact_hashes_and_pages_preserved": True,
            "all_15_native_manifest_members_hash_verified": True,
            "source_closure_descriptor_hash_verified": True,
            "interoperability_envelope_hash_verified": True,
            "exercise_answer_bijection_verified": True,
            "all_1037_exercise_answer_rows_preserved": True,
            "answer_provenance_1035_plus_2_preserved": True,
            "target_supplied_authorization_provenance_preserved": True,
            "presentation_safe_titles_with_raw_native_titles_preserved": True,
            "historical_native_and_current_public_status_distinguished": True,
            "strict_public_and_reader_allowlists": True,
            "root_qualified_workspace_input_paths": True,
            "canonical_term_and_correction_stores_without_duplicate_rows": True,
            "stale_pass_receipts_invalidated_before_build_and_validation": True,
            "paired_receipt_atomic_staging_and_rollback_tested": True,
            "publication_receipts_excluded_from_fixed_replay_inventory": True,
            "existing_lossless_common_migration_reused": True,
            "exact_reverse_extraction_22131": True,
            "common_virtual_stream_materialized": False,
            "native_bodies_copied": False,
            "native_segments_copied": False,
            "native_prerequisites_invented": False,
            "native_outcomes_invented": False,
            "semantic_textbook_html_claimed": False,
            "epub_claimed": False,
            "accessibility_conformance_claimed": False,
            "locked_anonymous_public_readback_receipt_hash_verified": True,
            "receipt_supplied_public_urls_and_hashes_preserved": True,
            "locked_readback_reports_zenodo_concept_lineage_open_and_published": True,
            "live_network_readback_performed_by_this_validator": False,
            "public_state_changed": False,
            "html_structure_and_documentation_links": True,
            "documentation_data_mirror_byte_identity": True,
            "documentation_html_source_body_or_reversible_navigation_overlay": True,
            "public_manifest_validation_relationships": True,
            "independent_native_projection_snapshot": True,
            "implementation_hashes_bound": True,
        },
        "negative_fixtures": negative,
        "html_links_checked": links,
        "isolated_two_build_byte_identity": {
            "byte_identical": True,
            "file_count": first_count,
            "tree_sha256": first_tree,
            "separate_python_processes": True,
            "inventory": list(BUILD_OWNED_PATHS),
        },
        "validation_scope": {
            "network_access": "not performed; verifies the hash-locked anonymous readback receipt supplied by the separate public verifier",
            "public_mutation": False,
            "common_virtual_stream_materialized": False,
        },
        "public_documentation": manifest["public_documentation"],
        "implementation": [implementation[path] for path in IMPLEMENTATION_PATHS],
        "python": {"version": sys.version.split()[0], "executable_name": Path(sys.executable).name},
        "manifest": manifest_identity,
        "public_readback": bytes_identity(input_bytes[PUBLIC_READBACK_WORKSPACE], PUBLIC_READBACK_WORKSPACE),
        "migration_receipt": bytes_identity(input_bytes[MIGRATION_RECEIPT_WORKSPACE], MIGRATION_RECEIPT_WORKSPACE),
    }
    receipt_bytes = canonical_json_bytes(receipt)
    docs_root.mkdir(parents=True, exist_ok=True)
    adapter_receipt = adapter / "validation.json"
    docs_receipt = docs_root / "validation.json"
    publish_validation_pair(adapter_receipt, docs_receipt, receipt_bytes)
    if (
        adapter_receipt.read_bytes() != receipt_bytes
        or docs_receipt.read_bytes() != receipt_bytes
        or (docs_root / "manifest.json").read_bytes() != (adapter / "manifest.json").read_bytes()
    ):
        raise AssertionError("B40 validation receipt mirror write/readback failed")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--hub-root", type=Path, default=PROJECT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--docs-root", type=Path, default=DEFAULT_DOCS)
    args = parser.parse_args()
    receipt = validate(
        args.native_root.resolve(),
        args.hub_root.resolve(),
        args.adapter.resolve(),
        args.docs_root.resolve(),
    )
    print(canonical_json_bytes(receipt).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
