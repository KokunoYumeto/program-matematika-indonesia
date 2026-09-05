"""Validate C120 source locks, truth boundaries, HTML, and deterministic replay."""

from __future__ import annotations

import argparse
import copy
import hashlib
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from build_c120_capability_v1 import (
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    PROJECT,
    build,
    render_educator,
    render_learner,
)
from c120_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    CURRENT_BACKEND_TREE,
    CURRENT_PUBLIC_HEAD,
    CURRENT_PUBLIC_TREE,
    FROZEN_BACKEND_COMMIT,
    LOCALE,
    MIGRATION_RECEIPT,
    NATIVE_INPUTS,
    ZENODO_RECORD_ID,
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
        self.project_checkboxes = 0
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
            classes = set((values.get("class") or "").split())
            self.unit_checkboxes += "unit-select" in classes
            self.project_checkboxes += "project-select" in classes


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True, encoding="utf-8",
    )
    return completed.stdout.strip()


def load_bundle(adapter: Path) -> dict:
    return {
        "source_lock": read_json(adapter / "input/source-lock.json"),
        "learning_map": read_json(adapter / "data/learning-map.json"),
        "educator_map": read_json(adapter / "data/educator-map.json"),
        "capabilities": read_json(adapter / "data/capabilities.json"),
        "ledger_references": read_json(adapter / "data/ledger-references.json"),
        "public_evidence": read_json(adapter / "data/public-evidence.json"),
        "rights_and_terms": read_json(adapter / "data/rights-and-terms.json"),
        "claim_boundary": read_json(adapter / "data/claim-boundary.json"),
    }


def source_lock_errors(source_lock: dict, native_root: Path, hub_root: Path) -> list[str]:
    errors: list[str] = []
    if source_lock.get("schema") != "c120-source-lock/1":
        errors.append("C120-SOURCE-LOCK-SCHEMA")
    if source_lock.get("course_id") != COURSE_ID or source_lock.get("locale") != LOCALE:
        errors.append("C120-SOURCE-LOCK-IDENTITY")
    repository = source_lock.get("native_repository", {})
    if repository.get("frozen_backend_commit") != FROZEN_BACKEND_COMMIT or repository.get("current_backend_tree") != CURRENT_BACKEND_TREE:
        errors.append("C120-SOURCE-LOCK-BACKEND")
    if repository.get("current_public_head") != CURRENT_PUBLIC_HEAD or repository.get("current_public_tree") != CURRENT_PUBLIC_TREE:
        errors.append("C120-SOURCE-LOCK-CURRENT")
    if [row.get("path") for row in source_lock.get("native_inputs", [])] != list(NATIVE_INPUTS):
        errors.append("C120-SOURCE-LOCK-INVENTORY")
    else:
        for row in source_lock["native_inputs"]:
            path = native_root / row["path"]
            if not path.is_file() or row != identity(path, display_path=row["path"]):
                errors.append(f"C120-SOURCE-HASH:{row['path']}")
    migration = source_lock.get("migration_input", {})
    migration_path = hub_root / MIGRATION_RECEIPT
    if not migration_path.is_file() or migration != identity(migration_path, display_path=MIGRATION_RECEIPT):
        errors.append(f"C120-SOURCE-HASH:{MIGRATION_RECEIPT}")
    integrity = source_lock.get("backend_integrity", {})
    if integrity.get("files") != 81 or integrity.get("bytes") != 3270308 or integrity.get("all_file_hashes_verified") is not True:
        errors.append("C120-SOURCE-LOCK-BACKEND-INVENTORY")
    try:
        if _git(native_root, "rev-parse", "HEAD") != CURRENT_PUBLIC_HEAD:
            errors.append("C120-GIT-HEAD")
        if _git(native_root, "rev-parse", "HEAD^{tree}") != CURRENT_PUBLIC_TREE:
            errors.append("C120-GIT-TREE")
        if _git(native_root, "rev-parse", "HEAD:backend") != CURRENT_BACKEND_TREE:
            errors.append("C120-GIT-BACKEND-TREE")
    except (OSError, subprocess.CalledProcessError):
        errors.append("C120-GIT-IDENTITY-UNREADABLE")
    return errors


def manifest_errors(adapter: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != "c120-capability-manifest/1":
        errors.append("C120-MANIFEST-SCHEMA")
    if manifest.get("course_id") != COURSE_ID or manifest.get("contract") != CONTRACT:
        errors.append("C120-MANIFEST-IDENTITY")
    expected_projection = {
        "zero_copy_native_bodies": True,
        "native_ids_preserved": True,
        "existing_reversible_migration_reused": True,
        "source_and_bridge_units_distinct": True,
        "mastery_support_types_preserved": True,
        "project_result_reproduction_claimed": False,
        "central_course_truth_rewritten": False,
        "historical_migration_receipt_rewritten": False,
        "common_virtual_backend_materialized": False,
        "public_state_changed": False,
    }
    if manifest.get("projection") != expected_projection:
        errors.append("C120-MANIFEST-PROJECTION")
    paths = [row.get("path") for row in manifest.get("outputs", [])]
    if len(paths) != len(set(paths)) or len(paths) != 12:
        errors.append("C120-MANIFEST-OUTPUT-INVENTORY")
    for row in manifest.get("outputs", []):
        path = adapter / row.get("path", "")
        if not path.is_file() or row != identity(path, display_path=row.get("path")):
            errors.append(f"C120-OUTPUT-HASH:{row.get('path')}")
    return errors


def html_errors(adapter: Path, bundle: dict) -> tuple[list[str], int]:
    errors: list[str] = []
    pages = [
        (adapter / "views/C120.html", render_learner(bundle), "learner"),
        (adapter / "views/C120-pengajar.html", render_educator(bundle), "educator"),
    ]
    link_count = 0
    for path, expected, label in pages:
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            errors.append(f"C120-HTML-REPLAY:{path.name}")
        parsed = Page(actual)
        if parsed.language != "id":
            errors.append(f"C120-HTML-LANGUAGE:{path.name}")
        if len(parsed.ids) != len(set(parsed.ids)):
            errors.append(f"C120-HTML-DUPLICATE-ID:{path.name}")
        if parsed.scripts < 1:
            errors.append(f"C120-HTML-NO-INTERACTION:{label}")
        if label == "educator" and (parsed.unit_checkboxes != 26 or parsed.project_checkboxes != 12):
            errors.append("C120-EDUCATOR-CHECKBOXES")
        for href in parsed.links:
            if not href or href in ("undefined", "null", "#"):
                errors.append(f"C120-HTML-EMPTY-LINK:{path.name}")
                continue
            if urlsplit(href).scheme not in ("", "https"):
                errors.append(f"C120-HTML-SCHEME:{href}")
            link_count += 1
    learner = pages[0][0].read_text(encoding="utf-8")
    educator = pages[1][0].read_text(encoding="utf-8")
    for unit in bundle["learning_map"]["units"]:
        for text, label in ((learner, "LEARNER"), (educator, "EDUCATOR")):
            if unit["unit_id"] not in text or unit["title_id"] not in text:
                errors.append(f"C120-{label}-UNIT:{unit['unit_id']}")
    for project in bundle["educator_map"]["selector"]["projects"]:
        if project["project_id"] not in educator or project["title_id"] not in educator:
            errors.append(f"C120-EDUCATOR-PROJECT:{project['project_id']}")
    if "14 rubrik kualitatif" not in learner or "bukan klaim reproduksi hasil artikel" not in learner:
        errors.append("C120-LEARNER-CLAIM-BOUNDARY")
    if "tidak mengklaim reproduksi hasil penelitian" not in educator or "C120-rencana-pengajar.json" not in educator:
        errors.append("C120-EDUCATOR-EXPORT-BOUNDARY")
    return errors, link_count


def mutate_cases(bundle: dict) -> list[tuple[str, str, callable]]:
    return [
        ("duplicate_unit", "C120-UNIT-IDENTITY", lambda x: x["learning_map"]["units"].append(copy.deepcopy(x["learning_map"]["units"][0]))),
        ("missing_unit", "C120-UNIT-IDENTITY", lambda x: x["learning_map"]["units"].pop()),
        ("unit_order_change", "C120-UNIT-ORDER", lambda x: x["learning_map"]["route"]["unit_ids"].reverse()),
        ("source_bridge_collapse", "C120-SOURCE-BRIDGE-BOUNDARY", lambda x: x["learning_map"]["units"][-1].update(origin_kind="source_derived_translation")),
        ("problem_loss", "C120-MASTERY-IDENTITY", lambda x: next(row for row in x["learning_map"]["units"] if row["problem_support"])["problem_support"].pop()),
        ("support_type_collapse", "C120-SUPPORT-TYPE-BOUNDARY", lambda x: next(row for row in x["learning_map"]["units"] if any(p["support_type"] == "qualitative_rubric" for p in row["problem_support"]))["problem_support"][0].update(support_type="worked_solution")),
        ("hint_loss", "C120-HINT-CLOSURE", lambda x: next(row for row in x["learning_map"]["units"] if row["problem_support"])["problem_support"][0].update(hint_available=False)),
        ("project_loss", "C120-PROJECT-IDENTITY", lambda x: x["educator_map"]["selector"]["projects"].pop()),
        ("project_result_claim", "C120-PROJECT-RESULT-CLAIM", lambda x: x["educator_map"]["selector"]["projects"][0].update(result_reproduction_claimed=True)),
        ("notebook_count_change", "C120-COUNT-TOTAL_NOTEBOOKS", lambda x: x["capabilities"]["counts"].update(total_notebooks=25)),
        ("segment_count_change", "C120-COUNT-SEGMENTS", lambda x: x["capabilities"]["counts"].update(segments=4104)),
        ("terminology_loss", "C120-TERMINOLOGY-ROWS", lambda x: x["rights_and_terms"]["terminology"].pop()),
        ("correction_loss", "C120-CORRECTION-ROWS", lambda x: x["rights_and_terms"]["corrections"].pop()),
        ("backend_hash_downgrade", "C120-BACKEND-INTEGRITY", lambda x: x["ledger_references"]["backend_integrity"].update(all_file_hashes_verified=False)),
        ("nonanonymous_github", "C120-GITHUB-ANONYMITY", lambda x: x["public_evidence"]["github"].update(anonymous_verification="authenticated")),
        ("nonanonymous_zenodo", "C120-ZENODO-ANONYMITY", lambda x: x["public_evidence"]["zenodo"].update(anonymous_verification="authenticated")),
        ("reader_access_downgrade", "C120-READER-ACCESSIBILITY", lambda x: x["public_evidence"]["reader"].update(tagged_pdf=False)),
        ("blanket_license_claim", "C120-RIGHTS-BOUNDARY", lambda x: x["rights_and_terms"].update(blanket_license_claimed=True)),
        ("native_body_copy", "C120-BOUNDARY-NATIVE_BODIES_COPIED", lambda x: x["claim_boundary"].update(native_bodies_copied=True)),
        ("native_outcome_invention", "C120-BOUNDARY-NATIVE_UNIT_OUTCOMES_INVENTED", lambda x: x["claim_boundary"].update(native_unit_outcomes_invented=True)),
        ("native_prerequisite_invention", "C120-BOUNDARY-NATIVE_UNIT_PREREQUISITES_INVENTED", lambda x: x["claim_boundary"].update(native_unit_prerequisites_invented=True)),
        ("virtual_backend_materialization", "C120-BOUNDARY-COMMON_VIRTUAL_BACKEND_MATERIALIZED", lambda x: x["claim_boundary"].update(common_virtual_backend_materialized=True)),
        ("historical_receipt_rewrite", "C120-BOUNDARY-HISTORICAL_MIGRATION_RECEIPT_REWRITTEN", lambda x: x["claim_boundary"].update(historical_migration_receipt_rewritten=True)),
        ("public_state_change", "C120-PUBLIC-STATE", lambda x: x["public_evidence"].update(public_state_changed=True)),
    ]


def tree_identity(root: Path, *, omit_validation: bool = False) -> tuple[int, str]:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file() and not (omit_validation and path.name == "validation.json"))
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(4, "big")); digest.update(relative)
        digest.update(len(data).to_bytes(8, "big")); digest.update(data)
    return len(files), digest.hexdigest()


def validate(native_root: Path, hub_root: Path, adapter: Path) -> dict:
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
            errors.append(f"C120-FRESH-PROJECTION:{key}")

    migration = read_json(hub_root / MIGRATION_RECEIPT)
    zenodo = read_json(native_root / "00_control/ZENODO_PUBLICATION_RECEIPT_CANONICAL_20260823.json")
    release = read_json(native_root / "release/zenodo/reader-first-complete-20260823-r5/RELEASE_MANIFEST.json")
    if migration.get("validation", {}).get("result") != "pass" or migration.get("source", {}).get("backend_file_count") != 81:
        errors.append("C120-MIGRATION-RECEIPT")
    if migration.get("validation", {}).get("exact_native_logical_record_reverse_extraction") != 4941 or migration.get("target", {}).get("record_count") != 16029:
        errors.append("C120-MIGRATION-ROUNDTRIP")
    if zenodo.get("record_id") != ZENODO_RECORD_ID or zenodo.get("anonymous_readback", {}).get("all_six_sha256_and_byte_counts_match_local") is not True:
        errors.append("C120-ZENODO-RECEIPT")
    primary = next(row for row in release.get("artifacts", []) if row.get("role") == "primary_reader")
    if primary.get("pages") != 355 or primary.get("tagged") is not True:
        errors.append("C120-RELEASE-PDF")

    negative = []
    for name, expected, mutator in mutate_cases(bundle):
        altered = copy.deepcopy(bundle)
        mutator(altered)
        observed = projection_errors(altered)
        if expected not in observed:
            errors.append(f"C120-NEGATIVE-ACCEPTED:{name}")
        negative.append({"fixture": name, "expected_error": expected, "state": "rejected" if expected in observed else "accepted"})
    altered_lock = copy.deepcopy(bundle["source_lock"])
    altered_lock["native_inputs"][0]["sha256"] = "0" * 64
    expected = f"C120-SOURCE-HASH:{NATIVE_INPUTS[0]}"
    observed = source_lock_errors(altered_lock, native_root, hub_root)
    negative.append({"fixture": "input_hash_change", "expected_error": expected, "state": "rejected" if expected in observed else "accepted"})
    if expected not in observed:
        errors.append("C120-NEGATIVE-ACCEPTED:input_hash_change")

    with tempfile.TemporaryDirectory(prefix="c120-adapter-replay-") as temporary:
        base = Path(temporary)
        first, second = base / "first", base / "second"
        build(native_root, hub_root, first); build(native_root, hub_root, second)
        first_count, first_tree = tree_identity(first)
        second_count, second_tree = tree_identity(second)
        if (first_count, first_tree) != (second_count, second_tree):
            errors.append("C120-TWO-BUILD-REPLAY")
        committed_count, committed_tree = tree_identity(adapter, omit_validation=True)
        if (committed_count, committed_tree) != (first_count, first_tree):
            errors.append("C120-COMMITTED-REPLAY")

    if errors:
        raise AssertionError("; ".join(sorted(set(errors))))
    receipt = {
        "schema": "c120-capability-validation/1",
        "state": "pass",
        "course_id": COURSE_ID,
        "contract": CONTRACT,
        "locale": LOCALE,
        "source_hashes_verified": len(NATIVE_INPUTS) + 1,
        "native_backend_hashes_verified": 81,
        "counts": manifest["counts"],
        "checks": {
            "native_ids_preserved": True,
            "source_and_bridge_units_distinct": True,
            "all_141_mastery_problem_ids_close": True,
            "mastery_support_types_preserved": True,
            "all_26_notebooks_accounted_by_kind": True,
            "all_12_project_packets_preserved": True,
            "project_result_reproduction_not_claimed": True,
            "terminology_and_corrections_preserved": True,
            "component_rights_preserved": True,
            "existing_migration_receipt_preserved": True,
            "current_backend_tree_equals_frozen_backend_tree": True,
            "native_bodies_copied": False,
            "common_virtual_backend_materialized": False,
            "central_course_truth_rewritten": False,
            "public_state_changed": False,
            "anonymous_github_handoff_verified": True,
            "anonymous_zenodo_receipt_verified": True,
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
