"""Validate D10 source locks, identities, truth boundaries, HTML, and replay."""

from __future__ import annotations

import argparse
import copy
import hashlib
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from build_d10_capability_v1 import DEFAULT_ADAPTER, DEFAULT_NATIVE, build, render_educator, render_learner
from d10_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    CURRENT_PUBLIC_HEAD,
    CURRENT_PUBLIC_TREE,
    LOCALE,
    RELEASE_COMMIT,
    RELEASE_TREE,
    SOURCE_INPUTS,
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
        self.checkboxes = 0
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
            self.checkboxes += 1


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


def source_lock_errors(source_lock: dict, native_root: Path) -> list[str]:
    errors: list[str] = []
    if source_lock.get("schema") != "d10-source-lock/1":
        errors.append("D10-SOURCE-LOCK-SCHEMA")
    if source_lock.get("course_id") != COURSE_ID or source_lock.get("locale") != LOCALE:
        errors.append("D10-SOURCE-LOCK-IDENTITY")
    repository = source_lock.get("native_repository", {})
    if repository.get("release_commit") != RELEASE_COMMIT or repository.get("release_tree") != RELEASE_TREE:
        errors.append("D10-SOURCE-LOCK-RELEASE")
    if repository.get("current_public_head_observed_separately") != CURRENT_PUBLIC_HEAD or repository.get("current_public_tree_observed_separately") != CURRENT_PUBLIC_TREE:
        errors.append("D10-SOURCE-LOCK-CURRENT-HEAD")
    inputs = source_lock.get("inputs", [])
    if [row.get("path") for row in inputs] != list(SOURCE_INPUTS):
        errors.append("D10-SOURCE-LOCK-INVENTORY")
        return errors
    for row in inputs:
        path = native_root / row["path"]
        if not path.is_file():
            errors.append(f"D10-SOURCE-MISSING:{row['path']}")
            continue
        if row != identity(path, display_path=row["path"]):
            errors.append(f"D10-SOURCE-HASH:{row['path']}")
    catalog = source_lock.get("catalog_manifest", {})
    if catalog.get("listed_files") != 506 or catalog.get("tree_files_including_manifest") != 507 or catalog.get("all_listed_hashes_verified") is not True:
        errors.append("D10-SOURCE-LOCK-CATALOG")
    return errors


def manifest_errors(adapter: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != "d10-capability-manifest/1":
        errors.append("D10-MANIFEST-SCHEMA")
    if manifest.get("course_id") != COURSE_ID or manifest.get("contract") != CONTRACT:
        errors.append("D10-MANIFEST-IDENTITY")
    expected_projection = {
        "zero_copy_native_bodies": True,
        "native_ids_preserved": True,
        "catalog_manifest_replayed": True,
        "reader_routes_distinct_from_catalog_units": True,
        "source_hints_not_retyped_as_full_solutions": True,
        "central_course_truth_rewritten": False,
        "public_state_changed": False,
        "strict_native_roundtrip_claimed": False,
    }
    if manifest.get("projection") != expected_projection:
        errors.append("D10-MANIFEST-PROJECTION")
    paths = [row.get("path") for row in manifest.get("outputs", [])]
    if len(paths) != len(set(paths)) or len(paths) != 12:
        errors.append("D10-MANIFEST-OUTPUT-INVENTORY")
    for row in manifest.get("outputs", []):
        path = adapter / row.get("path", "")
        if not path.is_file() or row != identity(path, display_path=row.get("path")):
            errors.append(f"D10-OUTPUT-HASH:{row.get('path')}")
    return errors


def html_errors(adapter: Path, bundle: dict) -> tuple[list[str], int]:
    errors: list[str] = []
    pages = [
        (adapter / "views/D10.html", render_learner(bundle), "learner"),
        (adapter / "views/D10-pengajar.html", render_educator(bundle), "educator"),
    ]
    link_count = 0
    for path, expected, label in pages:
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            errors.append(f"D10-HTML-REPLAY:{path.name}")
        parsed = Page(actual)
        if parsed.language != "id":
            errors.append(f"D10-HTML-LANGUAGE:{path.name}")
        if len(parsed.ids) != len(set(parsed.ids)):
            errors.append(f"D10-HTML-DUPLICATE-ID:{path.name}")
        if parsed.scripts < 1:
            errors.append(f"D10-HTML-NO-INTERACTION:{label}")
        if label == "educator" and parsed.checkboxes != 94:
            errors.append("D10-EDUCATOR-CHECKBOXES")
        for href in parsed.links:
            if not href or href in ("undefined", "null", "#"):
                errors.append(f"D10-HTML-EMPTY-LINK:{path.name}")
                continue
            if urlsplit(href).scheme not in ("", "https"):
                errors.append(f"D10-HTML-SCHEME:{href}")
            link_count += 1
    learner = pages[0][0].read_text(encoding="utf-8")
    educator = pages[1][0].read_text(encoding="utf-8")
    for unit in bundle["learning_map"]["units"]:
        if unit["unit_id"] not in learner or unit["title_id"] not in learner:
            errors.append(f"D10-LEARNER-UNIT:{unit['unit_id']}")
        if unit["unit_id"] not in educator or unit["title_id"] not in educator:
            errors.append(f"D10-EDUCATOR-UNIT:{unit['unit_id']}")
    if "tidak ada bank solusi lengkap" not in learner:
        errors.append("D10-LEARNER-SOLUTION-BOUNDARY")
    if "nol solusi lengkap" not in educator or "D10-rencana-pengajar.json" not in educator:
        errors.append("D10-EDUCATOR-EXPORT-BOUNDARY")
    return errors, link_count


def mutate_cases(bundle: dict) -> list[tuple[str, str, callable]]:
    return [
        ("duplicate_unit", "D10-UNIT-IDENTITY", lambda x: x["learning_map"]["units"].append(copy.deepcopy(x["learning_map"]["units"][0]))),
        ("missing_unit", "D10-UNIT-IDENTITY", lambda x: x["learning_map"]["units"].pop()),
        ("exercise_loss", "D10-TYPED-EXERCISES", lambda x: x["learning_map"]["units"][4]["exercise_ids"].pop()),
        ("variant_header_loss", "D10-VARIANT-IDENTITIES", lambda x: next(row for row in x["learning_map"]["units"] if "243Xo" in row["exercise_ids"])["exercise_ids"].remove("243Xo")),
        ("wrong_hint_count", "D10-COUNT-EXPLICIT_HINTS", lambda x: x["capabilities"]["counts"].update(explicit_hints=275)),
        ("wrong_formula_count", "D10-COUNT-FORMULA_OCCURRENCES", lambda x: x["capabilities"]["counts"].update(formula_occurrences=53490)),
        ("wrong_page_total", "D10-COUNT-OFFICIAL_PAGES", lambda x: x["capabilities"]["counts"].update(official_pages=686)),
        ("terminology_loss", "D10-TERMINOLOGY-ROWS", lambda x: x["rights_and_terms"]["terminology"].update(data_row_count=131)),
        ("correction_loss", "D10-CORRECTION-ROWS", lambda x: x["rights_and_terms"]["corrections"].pop()),
        ("catalog_manifest_downgrade", "D10-CATALOG-MANIFEST", lambda x: x["ledger_references"]["catalog_integrity"].update(all_listed_hashes_verified=False)),
        ("nonanonymous_github", "D10-GITHUB-ANONYMITY", lambda x: x["public_evidence"]["github"].update(anonymous_verification="authenticated")),
        ("nonanonymous_zenodo", "D10-ZENODO-ANONYMITY", lambda x: x["public_evidence"]["zenodo"].update(anonymous_verification="authenticated")),
        ("public_asset_loss", "D10-PUBLIC-ASSETS", lambda x: x["public_evidence"]["github"]["release_assets"].pop()),
        ("blanket_license_claim", "D10-BLANKET-LICENSE", lambda x: x["rights_and_terms"].update(blanket_license_claimed=True)),
        ("native_body_copy", "D10-BOUNDARY-NATIVE_BODIES_COPIED", lambda x: x["claim_boundary"].update(native_bodies_copied=True)),
        ("solution_invention", "D10-NONZERO-COMPLETE_SOLUTION_RECORDS", lambda x: x["claim_boundary"].update(complete_solution_records=1)),
        ("native_outcome_invention", "D10-BOUNDARY-NATIVE_LEARNING_OUTCOMES_INVENTED", lambda x: x["claim_boundary"].update(native_learning_outcomes_invented=True)),
        ("native_prerequisite_invention", "D10-BOUNDARY-NATIVE_UNIT_PREREQUISITES_INVENTED", lambda x: x["claim_boundary"].update(native_unit_prerequisites_invented=True)),
        ("online_native_html_invention", "D10-BOUNDARY-ONLINE_NATIVE_HTML_CLAIMED", lambda x: x["claim_boundary"].update(online_native_html_claimed=True)),
        ("tagged_pdf_invention", "D10-BOUNDARY-TAGGED_PDF_CLAIMED", lambda x: x["claim_boundary"].update(tagged_pdf_claimed=True)),
        ("public_state_change", "D10-PUBLIC-STATE", lambda x: x["public_evidence"].update(public_state_changed=True)),
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


def validate(native_root: Path, adapter: Path) -> dict:
    bundle = load_bundle(adapter)
    manifest = read_json(adapter / "manifest.json")
    errors = projection_errors(bundle)
    errors.extend(source_lock_errors(bundle["source_lock"], native_root))
    errors.extend(manifest_errors(adapter, manifest))
    html_failures, links = html_errors(adapter, bundle)
    errors.extend(html_failures)

    fresh = derive_projection(native_root)
    for key in bundle:
        if bundle[key] != fresh[key]:
            errors.append(f"D10-FRESH-PROJECTION:{key}")

    github = read_json(native_root / "qa/PUBLICATION_RECEIPT_V100_COMPLETE_CORPUS.json")
    zenodo = read_json(native_root / "qa/ZENODO_PUBLICATION_RECEIPT_V100_COMPLETE_CORPUS.json")
    backend = read_json(native_root / "backend/complete-corpus-backend-validation.json")
    package = read_json(native_root / "qa/complete-corpus-release-package.json")
    if github.get("boundary", {}).get("commit") != RELEASE_COMMIT or github.get("boundary", {}).get("tree") != RELEASE_TREE:
        errors.append("D10-GITHUB-RECEIPT")
    if github.get("verification", {}).get("anonymous_every_asset_byte_sha256_readback") is not True:
        errors.append("D10-GITHUB-RECEIPT-ANONYMITY")
    if zenodo.get("record", {}).get("id") != 22181780 or zenodo.get("verification", {}).get("anonymous_every_asset_byte_sha256_readback") is not True:
        errors.append("D10-ZENODO-RECEIPT")
    if backend.get("pass") is not True or backend.get("official_coverage") != "672/672":
        errors.append("D10-NATIVE-BACKEND-QA")
    if package.get("pass") is not True or package.get("admitted") is not True or package.get("publication_ready") is not True:
        errors.append("D10-NATIVE-PACKAGE-QA")

    negative = []
    for name, expected, mutator in mutate_cases(bundle):
        altered = copy.deepcopy(bundle)
        mutator(altered)
        observed = projection_errors(altered)
        if expected not in observed:
            errors.append(f"D10-NEGATIVE-ACCEPTED:{name}")
        negative.append({"fixture": name, "expected_error": expected, "state": "rejected" if expected in observed else "accepted"})
    altered_lock = copy.deepcopy(bundle["source_lock"])
    altered_lock["inputs"][0]["sha256"] = "0" * 64
    source_mutation_errors = source_lock_errors(altered_lock, native_root)
    expected = f"D10-SOURCE-HASH:{SOURCE_INPUTS[0]}"
    negative.append({"fixture": "input_hash_change", "expected_error": expected, "state": "rejected" if expected in source_mutation_errors else "accepted"})
    if expected not in source_mutation_errors:
        errors.append("D10-NEGATIVE-ACCEPTED:input_hash_change")

    with tempfile.TemporaryDirectory(prefix="d10-adapter-replay-") as temporary:
        base = Path(temporary)
        first, second = base / "first", base / "second"
        build(native_root, first); build(native_root, second)
        first_count, first_tree = tree_identity(first)
        second_count, second_tree = tree_identity(second)
        if (first_count, first_tree) != (second_count, second_tree):
            errors.append("D10-TWO-BUILD-REPLAY")
        committed_count, committed_tree = tree_identity(adapter, omit_validation=True)
        if (committed_count, committed_tree) != (first_count, first_tree):
            errors.append("D10-COMMITTED-REPLAY")

    if errors:
        raise AssertionError("; ".join(sorted(set(errors))))
    receipt = {
        "schema": "d10-capability-validation/1",
        "state": "pass",
        "course_id": COURSE_ID,
        "contract": CONTRACT,
        "locale": LOCALE,
        "source_hashes_verified": len(SOURCE_INPUTS),
        "catalog_manifest_hashes_verified": 506,
        "counts": manifest["counts"],
        "checks": {
            "native_ids_preserved": True,
            "all_94_units_close": True,
            "typed_exercise_1096_vs_standard_header_1094_boundary_preserved": True,
            "explicit_hints_not_promoted_to_full_solutions": True,
            "catalog_manifest_replayed": True,
            "terminology_and_corrections_preserved": True,
            "component_rights_preserved": True,
            "reader_routes_distinct_from_units": True,
            "learner_and_educator_views_share_unit_exercise_ids": True,
            "native_bodies_copied": False,
            "central_course_truth_rewritten": False,
            "online_native_html_claimed": False,
            "tagged_pdf_claimed": False,
            "public_state_changed": False,
            "anonymous_github_receipt_verified": True,
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
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    args = parser.parse_args()
    receipt = validate(args.native_root.resolve(), args.adapter.resolve())
    print(canonical_json_bytes(receipt).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
