"""Validate C110 capability truth, source locks, negative fixtures, and replay."""

from __future__ import annotations

import argparse
import copy
import hashlib
import re
import tempfile
from pathlib import Path
from typing import Any, Callable

from build_c110_capability_v1 import DEFAULT_ADAPTER, DEFAULT_NATIVE, PROJECT, build
from c110_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    NATIVE_INPUTS,
    PUBLIC_COMMIT,
    PUBLIC_TREE,
    canonical_json_bytes,
    derive_projection,
    identity,
    projection_errors,
    read_json,
    source_lock_errors,
    write_json,
)


def tree_identity(root: Path, *, omit_validation: bool = False) -> tuple[int, str]:
    rows = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if omit_validation and relative == "validation.json":
            continue
        data = path.read_bytes()
        rows.append(f"{relative}\t{len(data)}\t{hashlib.sha256(data).hexdigest()}\n")
    blob = "".join(rows).encode("utf-8")
    return len(rows), hashlib.sha256(blob).hexdigest()


def mutate_cases(bundle: dict[str, Any]) -> list[tuple[str, str, Callable[[dict[str, Any]], None]]]:
    return [
        ("duplicate_module", "C110-MODULE-IDENTITY", lambda value: value["learning_map"]["modules"].append(copy.deepcopy(value["learning_map"]["modules"][0]))),
        ("missing_module", "C110-MODULE-IDENTITY", lambda value: value["learning_map"]["modules"].pop()),
        ("module_order_change", "C110-MODULE-IDENTITY", lambda value: value["learning_map"]["route"]["module_ids"].reverse()),
        ("unit_loss", "C110-UNIT-IDENTITY", lambda value: value["learning_map"]["units"].pop()),
        ("unit_parent_change", "C110-UNIT-PARENT-CLOSURE", lambda value: value["learning_map"]["units"][1].__setitem__("parent_id", "urn:uuid:missing")),
        ("alignment_loss", "C110-ALIGNMENT-IDENTITY", lambda value: value["translation_alignments"]["alignments"].pop()),
        ("alignment_unit_break", "C110-ALIGNMENT-UNIT-CLOSURE", lambda value: value["translation_alignments"]["alignments"][0].__setitem__("unit_id", "urn:uuid:missing")),
        ("term_loss", "C110-LEDGER-CLOSURE", lambda value: value["rights_and_terms"]["terminology"].pop()),
        ("correction_loss", "C110-LEDGER-CLOSURE", lambda value: value["rights_and_terms"]["corrections"].pop()),
        ("experiment_loss", "C110-EXPERIMENT-IDENTITY", lambda value: value["educator_map"]["selector"]["experiments"].pop()),
        ("solution_answer_collapse", "C110-SOLUTION-ANSWER-BOUNDARY", lambda value: next(row for row in value["learning_map"]["modules"] if row["role"] == "answers").__setitem__("role", "solutions")),
        ("exercise_solution_join_invention", "C110-BOUNDARY-EXERCISE_SOLUTION_JOINS_INFERRED", lambda value: value["claim_boundary"].__setitem__("exercise_solution_joins_inferred", True)),
        ("native_outcome_invention", "C110-BOUNDARY-NATIVE_UNIT_OUTCOMES_INVENTED", lambda value: value["claim_boundary"].__setitem__("native_unit_outcomes_invented", True)),
        ("native_prerequisite_invention", "C110-COURSE-PREREQUISITES", lambda value: value["learning_map"].__setitem__("program_prerequisites", ["invented"])),
        ("semantic_html_invention", "C110-BOUNDARY-NATIVE_SEMANTIC_HTML_CLAIMED", lambda value: value["claim_boundary"].__setitem__("native_semantic_html_claimed", True)),
        ("tagged_pdf_invention", "C110-BOUNDARY-TAGGED_PDF_CLAIMED", lambda value: value["claim_boundary"].__setitem__("tagged_pdf_claimed", True)),
        ("segment_state_promotion", "C110-BOUNDARY-SEGMENT_WORKFLOW_STATES_PROMOTED_TO_RELEASE_STATES", lambda value: value["claim_boundary"].__setitem__("segment_workflow_states_promoted_to_release_states", True)),
        ("backend_hash_downgrade", "C110-BACKEND-INTEGRITY", lambda value: value["ledger_references"]["backend_integrity"].__setitem__("all_file_hashes_verified", False)),
        ("github_identity_change", "C110-GITHUB-IDENTITY", lambda value: value["public_evidence"]["github"].__setitem__("commit", "0" * 40)),
        ("zenodo_access_downgrade", "C110-PUBLIC-ACCESS", lambda value: value["public_evidence"]["zenodo"].__setitem__("access_right", "restricted")),
        ("blanket_license_claim", "C110-RIGHTS-BOUNDARY", lambda value: value["rights_and_terms"].__setitem__("blanket_license_claimed", True)),
        ("native_body_copy", "C110-BOUNDARY-NATIVE_BODIES_COPIED", lambda value: value["claim_boundary"].__setitem__("native_bodies_copied", True)),
        ("virtual_backend_materialization", "C110-BOUNDARY-COMMON_VIRTUAL_BACKEND_MATERIALIZED", lambda value: value["claim_boundary"].__setitem__("common_virtual_backend_materialized", True)),
        ("historical_receipt_rewrite", "C110-BOUNDARY-HISTORICAL_MIGRATION_RECEIPT_REWRITTEN", lambda value: value["claim_boundary"].__setitem__("historical_migration_receipt_rewritten", True)),
        ("public_state_change", "C110-PUBLIC-ACCESS", lambda value: value["public_evidence"].__setitem__("public_state_changed", True)),
    ]


def validate(native_root: Path, hub_root: Path, adapter: Path) -> dict[str, Any]:
    errors: list[str] = []
    manifest = read_json(adapter / "manifest.json")
    bundle = derive_projection(native_root, hub_root)
    errors.extend(projection_errors(bundle))
    source_lock = read_json(adapter / "input/source-lock.json")
    errors.extend(source_lock_errors(source_lock, native_root, hub_root))

    if manifest.get("schema") != "c110-capability-manifest/1" or manifest.get("course_id") != COURSE_ID:
        errors.append("C110-MANIFEST-IDENTITY")
    if manifest.get("contract") != CONTRACT or manifest.get("contract_2_3_1_conformance") != "not_claimed":
        errors.append("C110-CONTRACT-BOUNDARY")
    if manifest.get("native_role_id") != "R015" or manifest.get("native_family") != "numerical_analysis_lyx_backend":
        errors.append("C110-NATIVE-FAMILY")
    if manifest.get("counts") != bundle["capabilities"]["counts"]:
        errors.append("C110-MANIFEST-COUNTS")
    if len(manifest.get("inputs", [])) != len(NATIVE_INPUTS) + 2:
        errors.append("C110-MANIFEST-INPUTS")
    if len(manifest.get("outputs", [])) != 14:
        errors.append("C110-MANIFEST-OUTPUTS")
    for output in manifest.get("outputs", []):
        if identity(adapter / output["path"], display_path=output["path"]) != output:
            errors.append(f"C110-OUTPUT-HASH:{output['path']}")

    public = bundle["public_evidence"]
    if public["github"]["commit"] != PUBLIC_COMMIT or public["github"]["tree"] != PUBLIC_TREE:
        errors.append("C110-PUBLIC-GITHUB")
    if not all(bundle["public_evidence"]["anonymous_readback_receipt"].get(key) for key in ("bytes", "sha256")):
        errors.append("C110-PUBLIC-RECEIPT")
    if public["zenodo"]["access_right"] != "open":
        errors.append("C110-ZENODO-OPEN")

    hrefs = []
    allowed_local = {
        "../../id/#course-C110", "../index.html", "C110.html", "C110-pengajar.html",
        "learning-map.json", "educator-map.json", "translation-alignments.json",
        "rights-and-terms.json", "ledger-references.json",
    }
    for relative in ("views/C110.html", "views/C110-pengajar.html"):
        text = (adapter / relative).read_text(encoding="utf-8")
        if "C:\\Users\\" in text or "Authorization: Bearer" in text or "access_token" in text:
            errors.append(f"C110-HTML-SENSITIVE:{relative}")
        for href in re.findall(r'href="([^"]+)"', text):
            hrefs.append({"page": relative, "href": href})
            if href.startswith("https://"):
                continue
            if href not in allowed_local:
                errors.append(f"C110-HTML-LINK:{relative}:{href}")

    negative = []
    for name, expected, mutator in mutate_cases(bundle):
        altered = copy.deepcopy(bundle)
        mutator(altered)
        observed = projection_errors(altered)
        accepted = expected not in observed
        if accepted:
            errors.append(f"C110-NEGATIVE-ACCEPTED:{name}")
        negative.append({"fixture": name, "expected_error": expected, "state": "accepted" if accepted else "rejected"})
    altered_lock = copy.deepcopy(source_lock)
    altered_lock["native_inputs"][0]["sha256"] = "0" * 64
    expected = f"C110-SOURCE-HASH:{NATIVE_INPUTS[0]}"
    observed = source_lock_errors(altered_lock, native_root, hub_root)
    accepted = expected not in observed
    if accepted:
        errors.append("C110-NEGATIVE-ACCEPTED:input_hash_change")
    negative.append({"fixture": "input_hash_change", "expected_error": expected, "state": "accepted" if accepted else "rejected"})

    with tempfile.TemporaryDirectory(prefix="c110-adapter-replay-") as temporary:
        root = Path(temporary)
        first, second = root / "first", root / "second"
        build(native_root, hub_root, first)
        build(native_root, hub_root, second)
        first_count, first_tree = tree_identity(first)
        second_count, second_tree = tree_identity(second)
        if (first_count, first_tree) != (second_count, second_tree):
            errors.append("C110-TWO-BUILD-REPLAY")
        committed_count, committed_tree = tree_identity(adapter, omit_validation=True)
        if (committed_count, committed_tree) != (first_count, first_tree):
            errors.append("C110-COMMITTED-REPLAY")

    if errors:
        raise AssertionError("; ".join(sorted(set(errors))))
    receipt = {
        "schema": "c110-capability-validation/1",
        "state": "pass",
        "course_id": COURSE_ID,
        "contract": CONTRACT,
        "locale": "id-ID",
        "source_hashes_verified": len(NATIVE_INPUTS) + 2,
        "native_backend_hashes_verified": 19,
        "counts": manifest["counts"],
        "checks": {
            "all_281_native_unit_ids_close": True,
            "all_29_file_modules_ordered": True,
            "all_4621_alignment_ids_close": True,
            "solution_and_answer_modules_distinct": True,
            "exercise_solution_joins_inferred": False,
            "all_593_terms_and_325_corrections_preserved": True,
            "two_experiment_identities_preserved": True,
            "component_rights_preserved": True,
            "native_segment_states_not_promoted_to_release_states": True,
            "native_semantic_html_not_invented": True,
            "tagged_pdf_not_invented": True,
            "native_bodies_copied": False,
            "common_virtual_backend_materialized": False,
            "central_course_truth_rewritten": False,
            "public_state_changed": False,
            "anonymous_github_26_file_readback": True,
            "anonymous_zenodo_four_file_readback": True,
            "html_replay_and_link_syntax": True,
        },
        "negative_fixtures": negative,
        "html_links_checked": hrefs,
        "isolated_two_build_byte_identity": {"byte_identical": True, "file_count": first_count, "tree_sha256": first_tree},
        "manifest": identity(adapter / "manifest.json", display_path="manifest.json"),
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
    print(canonical_json_bytes(receipt).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
