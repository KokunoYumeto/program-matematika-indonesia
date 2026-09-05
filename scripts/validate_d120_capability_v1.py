"""Validate D120 source locks, shared identities, claims, HTML, and replay."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from build_d120_capability_v1 import (
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    build,
    render_educator,
    render_learner,
)
from d120_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    LOCALE,
    RELEASE_COMMIT,
    RELEASE_TREE,
    SOURCE_INPUTS,
    canonical_json_bytes,
    derive_projection,
    identity,
    projection_errors,
    read_json,
    sha256_bytes,
    write_json,
)


class Page(HTMLParser):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.language: str | None = None
        self.ids: list[str] = []
        self.links: list[str | None] = []
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.language = values.get("lang")
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "a":
            self.links.append(values.get("href"))


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
    if source_lock.get("schema") != "d120-source-lock/1":
        errors.append("D120-SOURCE-LOCK-SCHEMA")
    if source_lock.get("course_id") != COURSE_ID or source_lock.get("locale") != LOCALE:
        errors.append("D120-SOURCE-LOCK-IDENTITY")
    repository = source_lock.get("native_repository", {})
    if repository.get("release_commit") != RELEASE_COMMIT or repository.get("release_tree") != RELEASE_TREE:
        errors.append("D120-SOURCE-LOCK-RELEASE")
    inputs = source_lock.get("inputs", [])
    if [row.get("path") for row in inputs] != list(SOURCE_INPUTS):
        errors.append("D120-SOURCE-LOCK-INVENTORY")
        return errors
    for row in inputs:
        path = native_root / row["path"]
        if not path.is_file():
            errors.append(f"D120-SOURCE-MISSING:{row['path']}")
            continue
        expected = identity(path, display_path=row["path"])
        if row != expected:
            errors.append(f"D120-SOURCE-HASH:{row['path']}")
    return errors


def manifest_errors(adapter: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != "d120-capability-manifest/1":
        errors.append("D120-MANIFEST-SCHEMA")
    if manifest.get("course_id") != COURSE_ID or manifest.get("contract") != CONTRACT:
        errors.append("D120-MANIFEST-IDENTITY")
    projection = manifest.get("projection", {})
    expected_projection = {
        "zero_copy_native_bodies": True,
        "native_ids_preserved": True,
        "base_and_wrapper_ledgers_distinct": True,
        "renderer_fragments_are_locators_only": True,
        "central_course_truth_rewritten": False,
        "public_state_changed": False,
        "strict_native_roundtrip_claimed": False,
    }
    if projection != expected_projection:
        errors.append("D120-MANIFEST-PROJECTION")
    for row in manifest.get("outputs", []):
        path = adapter / row.get("path", "")
        if not path.is_file() or row != identity(path, display_path=row.get("path")):
            errors.append(f"D120-OUTPUT-HASH:{row.get('path')}")
    return errors


def html_errors(adapter: Path, bundle: dict) -> tuple[list[str], int]:
    errors: list[str] = []
    pages = [
        (adapter / "views/D120.html", render_learner(bundle)),
        (adapter / "views/D120-pengajar.html", render_educator(bundle)),
    ]
    link_count = 0
    for path, expected in pages:
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            errors.append(f"D120-HTML-REPLAY:{path.name}")
        parsed = Page(actual)
        if parsed.language != "id":
            errors.append(f"D120-HTML-LANGUAGE:{path.name}")
        if len(parsed.ids) != len(set(parsed.ids)):
            errors.append(f"D120-HTML-DUPLICATE-ID:{path.name}")
        for href in parsed.links:
            if not href or href in ("undefined", "null"):
                errors.append(f"D120-HTML-EMPTY-LINK:{path.name}")
                continue
            parts = urlsplit(href)
            if parts.scheme not in ("", "https"):
                errors.append(f"D120-HTML-SCHEME:{href}")
            link_count += 1
    learner = pages[0][0].read_text(encoding="utf-8")
    educator = pages[1][0].read_text(encoding="utf-8")
    for unit in bundle["learning_map"]["units"]:
        if unit["unit_id"] not in learner or unit["title"] not in learner:
            errors.append(f"D120-LEARNER-UNIT:{unit['unit_id']}")
    for assessment in bundle["educator_map"]["assessments"]:
        if assessment["assessment_id"] not in educator:
            errors.append(f"D120-EDUCATOR-ASSESSMENT:{assessment['assessment_id']}")
    if "54 rekaman dukungan adalah panduan sumber, bukan solusi lengkap" not in learner:
        errors.append("D120-LEARNER-GUIDANCE-BOUNDARY")
    if "tidak memberi kredit" not in educator:
        errors.append("D120-EDUCATOR-CALIBRATION-BOUNDARY")
    return errors, link_count


def mutate_cases(bundle: dict) -> list[tuple[str, str, callable]]:
    return [
        ("duplicate_unit", "D120-UNIT-DUPLICATE", lambda x: x["learning_map"]["units"].append(copy.deepcopy(x["learning_map"]["units"][0]))),
        ("missing_unit", "D120-UNIT-SEQUENCE", lambda x: x["learning_map"]["units"].pop()),
        ("orphan_exercise", "D120-EXERCISE-COUNT", lambda x: x["learning_map"]["units"][0]["practice"].pop()),
        ("wrong_guidance_kind", "D120-GUIDANCE-KIND", lambda x: x["learning_map"]["units"][0]["practice"][0].update(guidance_kind="full_solution")),
        ("missing_outcome", "D120-OUTCOME-COUNT", lambda x: x["learning_map"]["units"][0]["outcomes"].pop()),
        ("wrong_locale", "D120-LOCALE", lambda x: x["learning_map"].update(locale="en")),
        ("fragment_promoted_to_semantic_id", "D120-FRAGMENT-AS-SEMANTIC-ID", lambda x: x["learning_map"]["units"][0]["outcomes"][0].update(id="o017-u01-outcomes")),
        ("learner_attempt_claim", "D120-NONZERO-LEARNER_ATTEMPT_INSTANCES", lambda x: x["claim_boundary"].update(learner_attempt_instances=1)),
        ("learner_submission_claim", "D120-NONZERO-LEARNER_SUBMISSION_INSTANCES", lambda x: x["claim_boundary"].update(learner_submission_instances=1)),
        ("learner_result_claim", "D120-NONZERO-LEARNER_RESULT_INSTANCES", lambda x: x["claim_boundary"].update(learner_result_instances=1)),
        ("credential_assertion_claim", "D120-NONZERO-CREDENTIAL_ASSERTION_INSTANCES", lambda x: x["claim_boundary"].update(credential_assertion_instances=1)),
        ("community_participation_claim", "D120-COMMUNITY-CLAIM", lambda x: x["claim_boundary"].update(community_participation_claimed=True)),
        ("missing_assessment", "D120-ASSESSMENT-COUNT", lambda x: x["educator_map"]["assessments"].pop()),
        ("rubric_criterion_loss", "D120-CRITERIA-COUNT", lambda x: x["educator_map"]["assessments"][0]["rubric"]["criteria"].pop()),
        ("base_ledger_count_change", "D120-BASE-RELATIONS", lambda x: x["ledger_references"]["base_backend"].update(relations_issued=1106)),
        ("wrapper_ledger_count_change", "D120-WRAPPER-RELATIONS", lambda x: x["ledger_references"]["semantic_wrapper"].update(relations_issued=1703)),
        ("ledger_collapse", "D120-LEDGER-COLLAPSE", lambda x: x["ledger_references"]["projection"].update(base_and_wrapper_ledgers_collapsed=True)),
        ("nonanonymous_github", "D120-GITHUB-ANONYMITY", lambda x: x["public_evidence"]["github"].update(anonymous_verification="authenticated")),
        ("nonanonymous_zenodo", "D120-ZENODO-ANONYMITY", lambda x: x["public_evidence"]["zenodo"].update(anonymous_verification="authenticated")),
        ("blanket_license_claim", "D120-BLANKET-LICENSE", lambda x: x["rights_and_terms"].update(blanket_license_claimed=True)),
        ("native_body_copy", "D120-NATIVE-BODY-COPY", lambda x: x["claim_boundary"].update(native_bodies_copied=True)),
        ("central_truth_rewrite", "D120-CENTRAL-TRUTH-REWRITE", lambda x: x["claim_boundary"].update(central_course_truth_rewritten=True)),
        ("public_state_change", "D120-PUBLIC-STATE", lambda x: x["public_evidence"].update(public_state_changed=True)),
    ]


def tree_identity(root: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
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
        if key == "source_lock":
            if bundle[key] != fresh[key]:
                errors.append("D120-FRESH-SOURCE-LOCK-DIFFERENCE")
        elif bundle[key] != fresh[key]:
            errors.append(f"D120-FRESH-PROJECTION:{key}")

    github = read_json(native_root / "release/GITHUB_PUBLICATION_RECEIPT_2026.08.24.json")
    zenodo = read_json(native_root / "release/ZENODO_PUBLICATION_RECEIPT_2026.08.24.json")
    full_qa = read_json(native_root / "qa/FULL_COURSE_QA.json")
    wrapper_qa = read_json(native_root / "qa/SEMANTIC_WRAPPER_QA.json")
    privacy_qa = read_json(native_root / "qa/PUBLIC_PAYLOAD_PRIVACY_QA_2026.08.24.json")
    if github.get("status") != "PASS" or github["repository"]["commit_sha"] != RELEASE_COMMIT or github["repository"]["tree_sha"] != RELEASE_TREE:
        errors.append("D120-GITHUB-RECEIPT")
    if zenodo.get("status") != "PASS" or zenodo.get("record_id") != 22073823:
        errors.append("D120-ZENODO-RECEIPT")
    if full_qa.get("status") != "PASS" or wrapper_qa.get("status") != "pass":
        errors.append("D120-NATIVE-QA")
    if privacy_qa.get("status") != "PASS" or privacy_qa.get("credential_material_stored") is not False:
        errors.append("D120-PRIVACY-QA")

    negative = []
    for name, expected, mutator in mutate_cases(bundle):
        altered = copy.deepcopy(bundle)
        mutator(altered)
        observed = projection_errors(altered)
        if expected not in observed:
            errors.append(f"D120-NEGATIVE-ACCEPTED:{name}")
        negative.append({"fixture": name, "expected_error": expected, "state": "rejected" if expected in observed else "accepted"})
    altered_lock = copy.deepcopy(bundle["source_lock"])
    altered_lock["inputs"][0]["sha256"] = "0" * 64
    source_mutation_errors = source_lock_errors(altered_lock, native_root)
    expected = f"D120-SOURCE-HASH:{SOURCE_INPUTS[0]}"
    negative.append({"fixture": "input_hash_change", "expected_error": expected, "state": "rejected" if expected in source_mutation_errors else "accepted"})
    if expected not in source_mutation_errors:
        errors.append("D120-NEGATIVE-ACCEPTED:input_hash_change")

    with tempfile.TemporaryDirectory(prefix="d120-adapter-replay-") as temporary:
        base = Path(temporary)
        first, second = base / "first", base / "second"
        build(native_root, first)
        build(native_root, second)
        first_count, first_tree = tree_identity(first)
        second_count, second_tree = tree_identity(second)
        if (first_count, first_tree) != (second_count, second_tree):
            errors.append("D120-TWO-BUILD-REPLAY")
        committed_count, committed_tree = tree_identity(adapter)
        # validation.json, if present from a prior run, is deliberately outside the
        # non-circular manifest and deterministic builder tree.
        if (adapter / "validation.json").exists():
            validation_bytes = (adapter / "validation.json").read_bytes()
            validation_path = (adapter / "validation.json").relative_to(adapter).as_posix().encode("utf-8")
            digest = hashlib.sha256()
            for path in sorted(item for item in adapter.rglob("*") if item.is_file() and item.name != "validation.json"):
                relative = path.relative_to(adapter).as_posix().encode("utf-8")
                data = path.read_bytes()
                digest.update(len(relative).to_bytes(4, "big")); digest.update(relative)
                digest.update(len(data).to_bytes(8, "big")); digest.update(data)
            committed_count -= 1
            committed_tree = digest.hexdigest()
            del validation_bytes, validation_path
        if (committed_count, committed_tree) != (first_count, first_tree):
            errors.append("D120-COMMITTED-REPLAY")

    if errors:
        raise AssertionError("; ".join(sorted(set(errors))))

    receipt = {
        "schema": "d120-capability-validation/1",
        "state": "pass",
        "course_id": COURSE_ID,
        "contract": CONTRACT,
        "locale": LOCALE,
        "source_hashes_verified": len(SOURCE_INPUTS),
        "counts": manifest["counts"],
        "checks": {
            "native_ids_preserved": True,
            "exercise_guidance_pairs_close": True,
            "outcome_competency_assessment_rubric_references_close": True,
            "base_and_wrapper_ledgers_distinct": True,
            "localized_text_is_explicit_id_id": True,
            "renderer_fragments_are_locators_only": True,
            "learner_instance_claims_zero": True,
            "component_rights_preserved": True,
            "native_bodies_copied": False,
            "central_course_truth_rewritten": False,
            "public_state_changed": False,
            "anonymous_github_receipt_verified": True,
            "anonymous_zenodo_receipt_verified": True,
            "html_replay_and_link_syntax": True,
        },
        "negative_fixtures": negative,
        "html_links_checked": links,
        "isolated_two_build_byte_identity": {
            "byte_identical": True,
            "file_count": first_count,
            "tree_sha256": first_tree,
        },
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
