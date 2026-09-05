"""Validate C70 source locks, truth boundaries, HTML, and deterministic replay."""

from __future__ import annotations

import argparse
import copy
import hashlib
import subprocess
import tempfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit

from build_c70_capability_v1 import (
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    PROJECT,
    build,
    render_educator,
    render_learner,
)
from c70_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    CONTROL_INPUTS,
    CURRENT_PUBLIC_HEAD,
    CURRENT_PUBLIC_TREE,
    EXPECTED_RELATIONS,
    LOCALE,
    MIGRATION_RECEIPT,
    PUBLIC_READBACK,
    SOURCE_COMMIT,
    SOURCE_TREE,
    canonical_json_bytes,
    derive_projection,
    identity,
    projection_errors,
    read_json,
    write_json,
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


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True, encoding="utf-8",
    )
    return result.stdout.strip()


def load_bundle(adapter: Path) -> dict[str, Any]:
    return {
        "source_lock": read_json(adapter / "input/source-lock.json"),
        "learning_map": read_json(adapter / "data/learning-map.json"),
        "educator_map": read_json(adapter / "data/educator-map.json"),
        "concept_index": read_json(adapter / "data/concept-index.json"),
        "relation_index": read_json(adapter / "data/relation-index.json"),
        "ledger_references": read_json(adapter / "data/ledger-references.json"),
        "public_evidence": read_json(adapter / "data/public-evidence.json"),
        "rights_and_terms": read_json(adapter / "data/rights-and-terms.json"),
        "claim_boundary": read_json(adapter / "data/claim-boundary.json"),
        "capabilities": read_json(adapter / "data/capabilities.json"),
    }


def source_lock_errors(source_lock: dict[str, Any], native_root: Path, hub_root: Path) -> list[str]:
    errors: list[str] = []
    if source_lock.get("schema") != "c70-source-lock/1" or source_lock.get("course_id") != COURSE_ID or source_lock.get("locale") != LOCALE:
        errors.append("C70-SOURCE-LOCK-IDENTITY")
    repository = source_lock.get("native_repository", {})
    if repository.get("current_public_head") != CURRENT_PUBLIC_HEAD or repository.get("current_public_tree") != CURRENT_PUBLIC_TREE:
        errors.append("C70-SOURCE-LOCK-CURRENT")
    if repository.get("source_commit") != SOURCE_COMMIT or repository.get("source_tree") != SOURCE_TREE:
        errors.append("C70-SOURCE-LOCK-AUTHORITY")
    expected_controls = list(CONTROL_INPUTS)
    if [row.get("path") for row in source_lock.get("control_inputs", [])] != expected_controls:
        errors.append("C70-SOURCE-LOCK-CONTROLS")
    else:
        for row in source_lock["control_inputs"]:
            path = native_root / row["path"]
            if not path.is_file() or row != identity(path, display_path=row["path"]):
                errors.append(f"C70-SOURCE-HASH:{row['path']}")
    manifest = source_lock.get("export_manifest_input", {})
    manifest_path = native_root / "backend/exports/BACKEND_EXPORT_MANIFEST.csv"
    if not manifest_path.is_file() or manifest != identity(manifest_path, display_path=manifest.get("path")):
        errors.append("C70-SOURCE-HASH:backend/exports/BACKEND_EXPORT_MANIFEST.csv")
    if len(source_lock.get("export_inputs", [])) != 23:
        errors.append("C70-SOURCE-LOCK-EXPORTS")
    else:
        for row in source_lock["export_inputs"]:
            path = native_root / row["path"]
            if not path.is_file() or row != identity(path, display_path=row["path"]):
                errors.append(f"C70-SOURCE-HASH:{row['path']}")
    for key, relative in (("migration_input", MIGRATION_RECEIPT), ("public_readback_input", PUBLIC_READBACK)):
        row = source_lock.get(key, {})
        path = hub_root / relative
        if not path.is_file() or row != identity(path, display_path=relative):
            errors.append(f"C70-SOURCE-HASH:{relative}")
    return sorted(set(errors))


def manifest_errors(adapter: Path, manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != "c70-capability-manifest/1" or manifest.get("course_id") != COURSE_ID or manifest.get("contract") != CONTRACT:
        errors.append("C70-MANIFEST-IDENTITY")
    expected_projection = {
        "zero_copy_native_bodies": True,
        "native_ids_preserved": True,
        "existing_reversible_migration_reused": True,
        "all_unit_ids_indexed": True,
        "all_relation_ids_indexed": True,
        "exercise_support_projection_double_counted": False,
        "unlinked_solution_units_inferred": False,
        "native_target_edition_promoted": False,
        "central_course_truth_rewritten": False,
        "historical_migration_receipt_rewritten": False,
        "common_virtual_backend_materialized": False,
        "figshare_active_destination_used": False,
        "public_state_changed": False,
    }
    if manifest.get("projection") != expected_projection:
        errors.append("C70-MANIFEST-PROJECTION")
    paths = [row.get("path") for row in manifest.get("outputs", [])]
    if len(paths) != len(set(paths)) or len(paths) != 15:
        errors.append("C70-MANIFEST-OUTPUT-INVENTORY")
    for row in manifest.get("outputs", []):
        path = adapter / str(row.get("path", ""))
        if not path.is_file() or row != identity(path, display_path=row.get("path")):
            errors.append(f"C70-OUTPUT-HASH:{row.get('path')}")
    return errors


def html_errors(adapter: Path, bundle: dict[str, Any]) -> tuple[list[str], int]:
    errors: list[str] = []
    pages = [
        (adapter / "views/C70.html", render_learner(bundle), "learner"),
        (adapter / "views/C70-pengajar.html", render_educator(bundle), "educator"),
    ]
    link_count = 0
    for path, expected, label in pages:
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            errors.append(f"C70-HTML-REPLAY:{path.name}")
        parsed = Page(actual)
        if parsed.language != "id":
            errors.append(f"C70-HTML-LANGUAGE:{path.name}")
        if len(parsed.ids) != len(set(parsed.ids)):
            errors.append(f"C70-HTML-DUPLICATE-ID:{path.name}")
        if parsed.scripts < 1:
            errors.append(f"C70-HTML-NO-INTERACTION:{label}")
        if label == "educator" and parsed.unit_checkboxes != 1408:
            errors.append("C70-EDUCATOR-CHECKBOXES")
        for href in parsed.links:
            if not href or href in {"undefined", "null", "#"}:
                errors.append(f"C70-HTML-EMPTY-LINK:{path.name}")
                continue
            if urlsplit(href).scheme not in {"", "https"}:
                errors.append(f"C70-HTML-SCHEME:{href}")
            link_count += 1
    learner = pages[0][0].read_text(encoding="utf-8")
    educator = pages[1][0].read_text(encoding="utf-8")
    for block in bundle["learning_map"]["blocks"]:
        if block["block_id"] not in learner or block["title_id"] not in learner:
            errors.append(f"C70-LEARNER-BLOCK:{block['block_id']}")
    for unit in bundle["educator_map"]["selector"]["units"]:
        if unit["unit_id"] not in educator:
            errors.append(f"C70-EDUCATOR-UNIT:{unit['unit_id']}")
    if "Dua puluh tujuh unit solusi" not in educator or "C70-rencana-pengajar.json" not in educator:
        errors.append("C70-EDUCATOR-CLAIM-BOUNDARY")
    if "draf Bahasa Indonesia lengkap" not in learner or "57 solusi" not in learner:
        errors.append("C70-LEARNER-CLAIM-BOUNDARY")
    return errors, link_count


def mutate_cases(bundle: dict[str, Any]) -> list[tuple[str, str, Callable[[dict[str, Any]], None]]]:
    return [
        ("duplicate_unit", "C70-UNIT-IDENTITY", lambda x: x["educator_map"]["selector"]["units"].append(copy.deepcopy(x["educator_map"]["selector"]["units"][0]))),
        ("missing_unit", "C70-UNIT-IDENTITY", lambda x: x["educator_map"]["selector"]["units"].pop()),
        ("unit_order_change", "C70-UNIT-ORDER", lambda x: x["learning_map"]["route"]["all_unit_ids"].reverse()),
        ("block_loss", "C70-LEARNER-BLOCKS", lambda x: x["learning_map"]["blocks"].pop()),
        ("chapter_appendix_collapse", "C70-LEARNER-BLOCKS", lambda x: x["learning_map"]["blocks"][-1].update(kind="chapter")),
        ("prerequisite_change", "C70-COURSE-PREREQUISITE", lambda x: x["learning_map"].update(program_prerequisites=[])),
        ("support_loss", "C70-SUPPORT-IDENTITY", lambda x: x["educator_map"]["selector"]["exercise_support"].pop()),
        ("support_type_collapse", "C70-SUPPORT-TYPES", lambda x: next(row for row in x["educator_map"]["selector"]["exercise_support"] if row["support_kind"] == "answer").update(support_kind="solution")),
        ("relation_loss", "C70-RELATIONS", lambda x: x["relation_index"]["relations"].pop()),
        ("relation_count_change", "C70-RELATIONS", lambda x: x["relation_index"].update(relation_count=6333)),
        ("projection_double_count", "C70-PROJECTION-DOUBLE-COUNT", lambda x: x["relation_index"].update(specialized_projection_duplicate_rows_materialized=82)),
        ("concept_loss", "C70-CONCEPTS", lambda x: x["concept_index"]["concepts"].pop()),
        ("terminology_loss", "C70-TERMINOLOGY", lambda x: x["rights_and_terms"]["terminology"].pop()),
        ("terminology_review_loss", "C70-TERMINOLOGY", lambda x: x["rights_and_terms"]["terminology_review_log"].pop()),
        ("correction_loss", "C70-CORRECTIONS", lambda x: x["rights_and_terms"]["corrections"].pop()),
        ("target_state_promotion", "C70-TARGET-EDITION-STATE", lambda x: x["ledger_references"]["native_target_edition"].update(status="complete")),
        ("backend_roundtrip_downgrade", "C70-MIGRATION-ROUNDTRIP", lambda x: x["ledger_references"]["common_projection"].update(exact_reverse_extraction=19047)),
        ("nonanonymous_github", "C70-GITHUB-PUBLIC", lambda x: x["public_evidence"]["github"].update(anonymous_verification="authenticated")),
        ("closed_zenodo", "C70-ZENODO-PUBLIC", lambda x: x["public_evidence"]["zenodo"].update(all_records_open=False)),
        ("reader_route_loss", "C70-READER-PUBLIC", lambda x: x["public_evidence"]["reader"].update(verified_routes=18)),
        ("accessibility_overclaim", "C70-ACCESSIBILITY-OVERCLAIM", lambda x: x["public_evidence"]["reader"].update(tagged_pdf_claimed=True)),
        ("blanket_license_claim", "C70-RIGHTS", lambda x: x["rights_and_terms"].update(blanket_license_claimed=True)),
        ("native_body_copy", "C70-BOUNDARY-NATIVE_BODIES_COPIED", lambda x: x["claim_boundary"].update(native_bodies_copied=True)),
        ("unit_outcome_invention", "C70-BOUNDARY-NATIVE_UNIT_OUTCOMES_INVENTED", lambda x: x["claim_boundary"].update(native_unit_outcomes_invented=True)),
        ("unit_prerequisite_invention", "C70-BOUNDARY-NATIVE_UNIT_PREREQUISITES_INVENTED", lambda x: x["claim_boundary"].update(native_unit_prerequisites_invented=True)),
        ("unlinked_solution_inference", "C70-BOUNDARY-UNLINKED_SOLUTION_UNITS_INFERRED", lambda x: x["claim_boundary"].update(unlinked_solution_units_inferred=True)),
        ("source_defect_retyping", "C70-BOUNDARY-SOURCE_XREF_DEFECT_RETYPED_AS_TARGET_DEFECT", lambda x: x["claim_boundary"].update(source_xref_defect_retyped_as_target_defect=True)),
        ("virtual_backend_materialization", "C70-BOUNDARY-COMMON_VIRTUAL_BACKEND_MATERIALIZED", lambda x: x["claim_boundary"].update(common_virtual_backend_materialized=True)),
        ("figshare_reactivation", "C70-BOUNDARY-FIGSHARE_ACTIVE_DESTINATION_USED", lambda x: x["claim_boundary"].update(figshare_active_destination_used=True)),
        ("historical_receipt_rewrite", "C70-BOUNDARY-HISTORICAL_MIGRATION_RECEIPT_REWRITTEN", lambda x: x["claim_boundary"].update(historical_migration_receipt_rewritten=True)),
        ("public_state_change", "C70-PUBLIC-STATE", lambda x: x["public_evidence"].update(public_state_changed=True)),
    ]


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


def validate(native_root: Path, hub_root: Path, adapter: Path) -> dict[str, Any]:
    bundle = load_bundle(adapter)
    manifest = read_json(adapter / "manifest.json")
    errors = projection_errors(bundle)
    errors.extend(source_lock_errors(bundle["source_lock"], native_root, hub_root))
    errors.extend(manifest_errors(adapter, manifest))
    html_failures, links = html_errors(adapter, bundle)
    errors.extend(html_failures)

    fresh = derive_projection(native_root, hub_root)
    for key in bundle:
        if bundle[key] != fresh[key]:
            errors.append(f"C70-FRESH-PROJECTION:{key}")

    migration = read_json(hub_root / MIGRATION_RECEIPT)
    public = read_json(hub_root / PUBLIC_READBACK)
    if migration.get("validation", {}).get("result") != "pass" or migration.get("transformation", {}).get("exact_reverse_extraction") != 19048:
        errors.append("C70-MIGRATION-RECEIPT")
    if migration.get("target", {}).get("record_count") != 19049 or migration.get("transformation", {}).get("double_counted_projection_rows") != 0:
        errors.append("C70-MIGRATION-PROJECTION")
    if public.get("access_mode") != "anonymous_no_credentials" or public.get("checks", {}).get("external_state_changed") is not False:
        errors.append("C70-PUBLIC-READBACK")
    if public.get("github", {}).get("current_head") != CURRENT_PUBLIC_HEAD or public.get("github", {}).get("current_tree") != CURRENT_PUBLIC_TREE:
        errors.append("C70-PUBLIC-READBACK-HEAD")

    negative = []
    for name, expected, mutator in mutate_cases(bundle):
        altered = copy.deepcopy(bundle)
        mutator(altered)
        observed = projection_errors(altered)
        if expected not in observed:
            errors.append(f"C70-NEGATIVE-ACCEPTED:{name}")
        negative.append({"fixture": name, "expected_error": expected, "state": "rejected" if expected in observed else "accepted"})
    altered_lock = copy.deepcopy(bundle["source_lock"])
    altered_lock["control_inputs"][0]["sha256"] = "0" * 64
    expected = f"C70-SOURCE-HASH:{CONTROL_INPUTS[0]}"
    observed = source_lock_errors(altered_lock, native_root, hub_root)
    negative.append({"fixture": "input_hash_change", "expected_error": expected, "state": "rejected" if expected in observed else "accepted"})
    if expected not in observed:
        errors.append("C70-NEGATIVE-ACCEPTED:input_hash_change")

    with tempfile.TemporaryDirectory(prefix="c70-adapter-replay-") as temporary:
        root = Path(temporary)
        first, second = root / "first", root / "second"
        build(native_root, hub_root, first)
        build(native_root, hub_root, second)
        first_count, first_tree = tree_identity(first)
        second_count, second_tree = tree_identity(second)
        if (first_count, first_tree) != (second_count, second_tree):
            errors.append("C70-TWO-BUILD-REPLAY")
        committed_count, committed_tree = tree_identity(adapter, omit_validation=True)
        if (committed_count, committed_tree) != (first_count, first_tree):
            errors.append("C70-COMMITTED-REPLAY")

    if errors:
        raise AssertionError("; ".join(sorted(set(errors))))
    receipt = {
        "schema": "c70-capability-validation/1",
        "state": "pass",
        "course_id": COURSE_ID,
        "contract": CONTRACT,
        "locale": LOCALE,
        "source_hashes_verified": len(manifest["inputs"]),
        "native_export_hashes_verified": 23,
        "counts": manifest["counts"],
        "checks": {
            "native_ids_preserved": True,
            "all_1408_units_indexed_in_order": True,
            "all_701_concepts_indexed": True,
            "all_6334_relations_indexed": True,
            "exercise_support_projection_not_double_counted": True,
            "all_82_explicit_support_relations_preserved": True,
            "unlinked_solution_units_not_inferred": True,
            "target_draft_state_preserved": True,
            "source_xref_defect_not_retyped_as_target_defect": True,
            "terminology_and_corrections_preserved": True,
            "component_rights_preserved": True,
            "existing_migration_receipt_preserved": True,
            "native_bodies_copied": False,
            "common_virtual_backend_materialized": False,
            "central_course_truth_rewritten": False,
            "figshare_active_destination_used": False,
            "public_state_changed": False,
            "anonymous_github_and_zenodo_verified": True,
            "html_replay_and_link_syntax": True,
        },
        "negative_fixtures": negative,
        "html_links_checked": links,
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
