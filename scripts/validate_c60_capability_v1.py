"""Validate C60 source locks, strict common map, negatives, HTML, and replay."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker

from build_c60_capability_v1 import DEFAULT_ADAPTER, DEFAULT_NATIVE, NEGATIVE_FIXTURES, PROJECT, build
from c60_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    canonical_json_bytes,
    derive_projection,
    identity,
    projection_errors,
    read_json,
    write_json,
)


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang = None
        self.main = 0
        self.chapter_details = 0
        self.unit_inputs = 0
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang")
        elif tag == "main":
            self.main += 1
        elif tag == "details" and "chapter" in (values.get("class") or "").split():
            self.chapter_details += 1
        elif tag == "input" and "unit-select" in (values.get("class") or "").split():
            self.unit_inputs += 1
        elif tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")


def load_bundle(adapter: Path) -> dict[str, Any]:
    return {
        "source_lock": read_json(adapter / "input/source-lock.json"),
        "learning_map": read_json(adapter / "data/learning-map.json"),
        "educator_map": read_json(adapter / "data/educator-map.json"),
        "native_id_index": read_json(adapter / "data/native-id-index.json"),
        "concept_index": read_json(adapter / "data/concept-index.json"),
        "relation_index": read_json(adapter / "data/relation-index.json"),
        "rights_and_terms": read_json(adapter / "data/rights-and-terms.json"),
        "ledger_references": read_json(adapter / "data/ledger-references.json"),
        "public_evidence": read_json(adapter / "data/public-evidence.json"),
        "claim_boundary": read_json(adapter / "data/claim-boundary.json"),
        "capabilities": read_json(adapter / "data/capabilities.json"),
    }


def tree_identity(root: Path) -> tuple[int, str]:
    rows: list[bytes] = []
    count = 0
    for path in sorted(item for item in root.rglob("*") if item.is_file() and item.name != "validation.json" and "build" not in item.relative_to(root).parts):
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        rows.append(f"{relative}\t{len(data)}\t{hashlib.sha256(data).hexdigest()}\n".encode("utf-8"))
        count += 1
    return count, hashlib.sha256(b"".join(rows)).hexdigest()


def manifest_errors(adapter: Path, manifest: dict[str, Any], bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != "c60-capability-manifest/1" or manifest.get("course_id") != COURSE_ID or manifest.get("contract") != CONTRACT:
        errors.append("C60-MANIFEST-HEADER")
    if manifest.get("strict_contract_schema_verified") is not True:
        errors.append("C60-MANIFEST-CONTRACT")
    if manifest.get("counts") != bundle["capabilities"]["counts"]:
        errors.append("C60-MANIFEST-COUNTS")
    if manifest.get("inputs") != bundle["source_lock"]["inputs"]:
        errors.append("C60-MANIFEST-INPUTS")
    outputs = manifest.get("outputs", [])
    if len(outputs) != 15 or len({row.get("path") for row in outputs}) != 15:
        errors.append("C60-MANIFEST-OUTPUTS")
    for row in outputs:
        path = adapter / str(row.get("path"))
        if not path.is_file() or identity(path, display_path=row.get("path")) != row:
            errors.append(f"C60-MANIFEST-OUTPUT-{row.get('path')}")
    return errors


def html_errors(adapter: Path) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    evidence: dict[str, Any] = {}
    for name, expected_chapters, expected_units in (("C60.html", 5, 0), ("C60-pengajar.html", 0, 548)):
        path = adapter / "views" / name
        text = path.read_text(encoding="utf-8")
        page = Page()
        page.feed(text)
        if page.lang != "id" or page.main != 1:
            errors.append(f"C60-HTML-STRUCTURE-{name}")
        if page.chapter_details != expected_chapters or page.unit_inputs != expected_units:
            errors.append(f"C60-HTML-COUNT-{name}")
        if not any(link.startswith("https://kokunoyumeto.github.io/yet-another-introductory-number-theory-textbook-id/") for link in page.links):
            errors.append(f"C60-HTML-READER-{name}")
        if any(token in text for token in ("text_latex", "source_text", "target_text", "C:\\Users\\")):
            errors.append(f"C60-HTML-BODY-OR-LOCAL-PATH-{name}")
        evidence[name] = {"links": len(page.links), "chapter_details": page.chapter_details, "unit_inputs": page.unit_inputs}
    return errors, evidence


def mutate_cases(bundle: dict[str, Any]) -> list[tuple[str, str, Callable[[dict[str, Any]], None]]]:
    def set_path(*path_value: Any) -> Callable[[dict[str, Any]], None]:
        *path, value = path_value
        def mutate(target: dict[str, Any]) -> None:
            node: Any = target
            for key in path[:-1]:
                node = node[key]
            node[path[-1]] = value
        return mutate

    cases: list[tuple[str, str, Callable[[dict[str, Any]], None]]] = [
        ("source_head_change", "C60-SOURCE-PUBLIC-HEAD", set_path("source_lock", "repository", "current_public_head", "0" * 40)),
        ("backend_tree_change", "C60-SOURCE-BACKEND-TREE", set_path("source_lock", "repository", "current_backend_tree", "0" * 40)),
        ("source_hash_change", "C60-SOURCE-INPUT-HASH", set_path("source_lock", "inputs", 0, "sha256", "bad")),
        ("native_class_count_change", "C60-NATIVE-ID-CLASSES", set_path("native_id_index", "class_counts", "unit", 547)),
        ("unit_route_loss", "C60-UNIT-ROUTE", set_path("educator_map", "selector", "units", 0, "reader_route", "url", None)),
        ("exact_route_loss", "C60-UNIT-DIRECT-ROUTE", set_path("educator_map", "selector", "units", next(i for i, row in enumerate(bundle["educator_map"]["selector"]["units"]) if row["direct_reader_url"]), "direct_reader_url", None)),
        ("exercise_support_invention", "C60-EXERCISE-SUPPORT-INVENTION", set_path("learning_map", "units", 0, "exercises", 0, "hint", "status", "complete")),
        ("concept_route_loss", "C60-CONCEPT-ROUTES", set_path("concept_index", "concepts", 0, "primary_reader_url", None)),
        ("relation_type_change", "C60-RELATION-TYPES", set_path("relation_index", "relation_type_counts", "covers", 881)),
        ("derived_relation_invention", "C60-RELATION-INVENTION", set_path("relation_index", "derived_relations_invented", 1)),
        ("blanket_license_claim", "C60-RIGHTS", set_path("rights_and_terms", "blanket_license_claimed", True)),
        ("migration_replay_loss", "C60-MIGRATION-REPLAY", set_path("ledger_references", "independent_receipt_replay", "state", "fail")),
        ("migration_mapping_change", "C60-MIGRATION-ID-MAPPING", set_path("ledger_references", "independent_receipt_replay", "native_id_mapping_recomputed", "sha256", "0" * 64)),
        ("migration_roundtrip_change", "C60-MIGRATION-ROUNDTRIP", set_path("ledger_references", "common_projection", "exact_reverse_extraction", 5271)),
        ("native_body_copy", "C60-BOUNDARY-NATIVE_BODIES_COPIED", set_path("claim_boundary", "native_bodies_copied", True)),
        ("assessment_invention", "C60-NONZERO-ASSESSMENT_INSTANCES", set_path("claim_boundary", "assessment_instances", 1)),
        ("learner_result_invention", "C60-NONZERO-LEARNER_RESULT_INSTANCES", set_path("claim_boundary", "learner_result_instances", 1)),
        ("live_execution_claim", "C60-BOUNDARY-LIVE_EXECUTION_CLAIMED", set_path("claim_boundary", "live_execution_claimed", True)),
        ("accessibility_conformance_claim", "C60-BOUNDARY-ACCESSIBILITY_CONFORMANCE_CLAIMED", set_path("claim_boundary", "accessibility_conformance_claimed", True)),
        ("offline_dependency_overclaim", "C60-BOUNDARY-FULL_OFFLINE_DEPENDENCY_CLOSURE_CLAIMED", set_path("claim_boundary", "full_offline_dependency_closure_claimed", True)),
        ("central_truth_rewrite", "C60-BOUNDARY-CENTRAL_COURSE_TRUTH_REWRITTEN", set_path("claim_boundary", "central_course_truth_rewritten", True)),
        ("historical_receipt_rewrite", "C60-BOUNDARY-HISTORICAL_MIGRATION_RECEIPT_REWRITTEN", set_path("claim_boundary", "historical_migration_receipt_rewritten", True)),
        ("virtual_backend_materialization", "C60-BOUNDARY-COMMON_VIRTUAL_BACKEND_MATERIALIZED", set_path("claim_boundary", "common_virtual_backend_materialized", True)),
        ("excluded_destination_activation", "C60-BOUNDARY-EXCLUDED_DESTINATION_USED", set_path("claim_boundary", "excluded_destination_used", True)),
        ("public_state_change", "C60-BOUNDARY-PUBLIC_STATE_CHANGED", set_path("claim_boundary", "public_state_changed", True)),
        ("attribution_value_copy", "C60-BOUNDARY-SOURCE_ATTRIBUTION_VALUES_EMBEDDED", set_path("claim_boundary", "source_attribution_values_embedded", True)),
    ]

    def append_case(name: str, code: str, action: Callable[[dict[str, Any]], None]) -> None:
        cases.append((name, code, action))
    append_case("source_input_loss", "C60-SOURCE-INPUTS", lambda value: value["source_lock"]["inputs"].pop())
    append_case("native_id_loss", "C60-NATIVE-ID-IDENTITY", lambda value: value["native_id_index"]["records"].pop())
    append_case("native_id_duplicate", "C60-NATIVE-ID-IDENTITY", lambda value: value["native_id_index"]["records"].__setitem__(1, copy.deepcopy(value["native_id_index"]["records"][0])))
    append_case("unit_loss", "C60-UNIT-IDENTITY", lambda value: value["educator_map"]["selector"]["units"].pop())
    append_case("unit_order_change", "C60-UNIT-ORDER", lambda value: value["educator_map"]["selector"]["units"].__setitem__(slice(0, 2), list(reversed(value["educator_map"]["selector"]["units"][:2]))))
    append_case("supersession_loss", "C60-UNIT-SUPERSESSION", lambda value: next(row for row in value["educator_map"]["selector"]["units"] if row["superseded_by"]).__setitem__("superseded_by", None))
    append_case("chapter_loss", "C60-CHAPTER-ROUTES", lambda value: value["educator_map"]["chapter_routes"].pop())
    append_case("section_loss", "C60-SECTION-ROUTES", lambda value: value["educator_map"]["section_routes"].pop())
    append_case("common_unit_loss", "C60-COMMON-CONTRACT", lambda value: value["learning_map"]["units"].pop())
    append_case("native_exercise_loss", "C60-COMMON-CONTRACT", lambda value: value["learning_map"]["units"][0]["exercises"].pop())
    append_case("concept_loss", "C60-CONCEPTS", lambda value: value["concept_index"]["concepts"].pop())
    append_case("relation_loss", "C60-RELATIONS", lambda value: value["relation_index"]["relations"].pop())
    append_case("terminology_loss", "C60-TERMINOLOGY", lambda value: value["rights_and_terms"]["terminology"].pop())
    append_case("correction_loss", "C60-CORRECTIONS", lambda value: value["rights_and_terms"]["corrections"].pop())
    append_case("rights_loss", "C60-RIGHTS", lambda value: value["rights_and_terms"]["component_rights"].pop())
    return cases


def validate(native_root: Path, hub_root: Path, adapter: Path) -> dict[str, Any]:
    expected = derive_projection(native_root, hub_root)
    expected_errors = projection_errors(expected)
    if expected_errors:
        raise ValueError(f"C60 derived projection invalid: {expected_errors}")
    bundle = load_bundle(adapter)
    if bundle != expected:
        raise ValueError("C60 committed adapter data differs from deterministic derivation")
    errors = projection_errors(bundle)
    manifest = read_json(adapter / "manifest.json")
    errors.extend(manifest_errors(adapter, manifest, bundle))

    schema = read_json(hub_root / "schemas/course-capsule-v1/course-learning-capability-v1.schema.json")
    schema_errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(bundle["learning_map"]), key=lambda row: list(row.absolute_path))
    if schema_errors:
        errors.append(f"C60-COMMON-SCHEMA-{list(schema_errors[0].absolute_path)}-{schema_errors[0].message}")
    page_errors, html_evidence = html_errors(adapter)
    errors.extend(page_errors)

    negative_rows = []
    names = []
    for name, expected_code, mutate in mutate_cases(bundle):
        names.append(name)
        candidate = copy.deepcopy(bundle)
        mutate(candidate)
        observed = projection_errors(candidate)
        state = "rejected" if expected_code in observed else "accepted"
        negative_rows.append({"fixture": name, "expected_error": expected_code, "state": state})
        if state != "rejected":
            errors.append(f"C60-NEGATIVE-{name}")
    if len(names) != len(NEGATIVE_FIXTURES) or set(names) != set(NEGATIVE_FIXTURES):
        errors.append("C60-NEGATIVE-FIXTURE-INDEX")

    with tempfile.TemporaryDirectory(prefix="c60-build-a-") as first_name, tempfile.TemporaryDirectory(prefix="c60-build-b-") as second_name:
        first = Path(first_name)
        second = Path(second_name)
        build(native_root, hub_root, first)
        build(native_root, hub_root, second)
        first_identity = tree_identity(first)
        second_identity = tree_identity(second)
        current_identity = tree_identity(adapter)
        if first_identity != second_identity or current_identity != first_identity:
            errors.append("C60-DETERMINISTIC-REPLAY")

    allowed = {row["path"] for row in manifest["outputs"]} | {"manifest.json", "validation.json"}
    actual = {path.relative_to(adapter).as_posix() for path in adapter.rglob("*") if path.is_file() and "build" not in path.relative_to(adapter).parts}
    unexpected = sorted(actual - allowed)
    missing = sorted(allowed - actual - {"validation.json"})
    if unexpected or missing:
        errors.append("C60-ADAPTER-FILE-BOUNDARY")
    if errors:
        raise ValueError(f"C60 validation failed: {sorted(set(errors))}")

    receipt = {
        "schema": "c60-capability-validation/1",
        "course_id": COURSE_ID,
        "contract": CONTRACT,
        "state": "pass",
        "strict_common_schema": "pass",
        "source_hashes_verified": len(bundle["source_lock"]["inputs"]),
        "native_ids_verified": bundle["native_id_index"]["record_count"],
        "migration_receipt_replay_checks": bundle["ledger_references"]["independent_receipt_replay"]["check_count"],
        "projection_errors": [],
        "negative_fixtures": negative_rows,
        "html": html_evidence,
        "isolated_two_build_byte_identity": {"byte_identical": True, "file_count": first_identity[0], "tree_sha256": first_identity[1]},
        "counts": bundle["capabilities"]["counts"],
        "claim_boundary": bundle["claim_boundary"],
        "public_state_changed": False,
    }
    write_json(adapter / "validation.json", receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--hub-root", type=Path, default=PROJECT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    args = parser.parse_args()
    receipt = validate(args.native_root.resolve(), args.hub_root.resolve(), args.adapter.resolve())
    print(json.dumps({"state": receipt["state"], "course_id": COURSE_ID, "negative_fixtures": len(receipt["negative_fixtures"]), "deterministic_files": receipt["isolated_two_build_byte_identity"]["file_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
