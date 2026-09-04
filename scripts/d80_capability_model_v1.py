"""Reusable data model and invariants for the bounded D80 capability adapter.

Standard-library only.  The builder and validator deliberately share stable
serialization and identity rules, while the validator adds independent source,
HTML, hash, and negative-fixture checks.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


CONTRACT = "course-learning-capability/1"
SCHEMA_PREFIX = "d80-capability"
PAGES_BASE = "https://kokunoyumeto.github.io/metode-aljabar-jilid-2-id/"
GITHUB_MAIN_COMMIT = "8dbaeb4443978aef6d89365149e28a6ba06e005a"
PAGES_HEAD = "b6ea8ca709af090f01dca5cba69d4e3b6e603412"
PAGES_TREE = "ec6674a946684fbe770d628bb55baef89c2e651e"
SOURCE_COMMIT = "9a5803ff77dd3257484cb177f851a73770a59dd3"
SOURCE_TREE = "23bd05c2fb8434278df4fdfb636559a6a2b0d2ff"
UNIT_001_ID = "o014.aljabr2.prelude.linear-algebra"
UNIT_001_TARGET = "source/id-ID/prelude-unit-001.tex"
UNIT_001_BYTES = 4885
UNIT_001_SHA256 = "bf874c48715910f265d197caa02a22951d8c4b84840217b856eaa59e753ec39d"
HISTORICAL_CHECKPOINT_END = 51
EXPECTED_SUPERSEDED_TARGET_HASH_SEQUENCES = frozenset(range(2, HISTORICAL_CHECKPOINT_END + 1))
MALFORMED_SUPERSEDED_TARGET_HASH_SEQUENCES = frozenset({26})
BRIDGE_IDS = (
    "o014.mastery.diagram-chasing.001",
    "o014.mastery.derived-spectral.002",
)
EXPECTED_NATIVE_STATUS_COUNTS = {
    "translated_backend_indexed": 95,
    "translated_built_qa_passed": 51,
}
EXPECTED_CORRECTION_STATUS_COUNTS = {
    "accepted_disclosed": 71,
    "accepted_recorded": 1,
    "observed_not_modified_pending_consolidated_review": 1,
}
EXPECTED_TERM_DRIFT = {
    "math.homological.cup_product": ("hasil kali cawan", "hasil kali cup"),
    "math.set_theory.regular_small_cardinal": (
        "kardinal kecil reguler",
        "kardinal kecil regular",
    ),
}


class D80Error(ValueError):
    """A stable-code D80 model error."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def canonical_json_line(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


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
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise D80Error(f"D80-JSONL-OBJECT:{path}:{line_number}")
        rows.append(value)
    return rows


def load_bundle(output_root: Path) -> dict[str, Any]:
    return {
        "course": read_json(output_root / "data/course.json"),
        "learning_map": read_json(output_root / "data/learning-map.json"),
        "units": read_jsonl(output_root / "data/units.jsonl"),
        "routes": read_jsonl(output_root / "data/routes.jsonl"),
        "fragments": read_jsonl(output_root / "data/mastery-fragments.jsonl"),
        "ledgers": read_json(output_root / "data/ledger-references.json"),
        "capabilities": read_json(output_root / "data/capabilities.json"),
        "manifest": read_json(output_root / "manifest.json"),
    }


def _add(errors: list[str], condition: bool, code: str) -> None:
    if not condition:
        errors.append(code)


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    """Return stable error codes for semantic projection defects."""

    errors: list[str] = []
    course = bundle["course"]
    learning_map = bundle["learning_map"]
    units = bundle["units"]
    routes = bundle["routes"]
    fragments = bundle["fragments"]
    ledgers = bundle["ledgers"]
    capabilities = bundle["capabilities"]
    manifest = bundle["manifest"]

    _add(errors, course.get("schema") == "d80-capability-course/1", "D80-COURSE-SCHEMA")
    _add(errors, "contract" not in course, "D80-CONTRACT-COLLISION")
    _add(errors, course.get("course_id") == "D80", "D80-COURSE-ID")
    _add(errors, course.get("owner_lane") == "O014", "D80-OWNER-LANE")
    _add(errors, course.get("contract_2_3_1_conformance") == "not_claimed", "D80-V231-CLAIM")
    _add(errors, course.get("reader_route_authority") == "github_pages_corrected", "D80-READER-AUTHORITY")
    pages = course.get("public_lineage", {}).get("github_pages", {})
    _add(errors, pages.get("url") == PAGES_BASE, "D80-PAGES-URL")
    _add(errors, pages.get("head") == PAGES_HEAD and pages.get("tree") == PAGES_TREE, "D80-PAGES-IDENTITY")
    _add(
        errors,
        course.get("public_lineage", {}).get("github_main", {}).get("reader_routable") is False,
        "D80-MAIN-READER-ROUTABLE",
    )

    native_units = [u for u in units if u.get("unit_type") == "translated_source_unit"]
    bridges = [u for u in units if u.get("unit_type") == "independent_mastery_bridge"]
    unit_ids = [u.get("unit_id") for u in units]
    _add(errors, len(native_units) == 146, "D80-COUNT-NATIVE-UNITS")
    _add(errors, len(bridges) == 2, "D80-COUNT-BRIDGES")
    _add(errors, len(units) == 148, "D80-COUNT-UNITS")
    _add(errors, len(set(unit_ids)) == len(unit_ids), "D80-UNIT-ID-DUPLICATE")
    _add(errors, [u.get("sequence") for u in units] == list(range(1, 149)), "D80-UNIT-SEQUENCE")
    _add(errors, {u.get("unit_id") for u in bridges} == set(BRIDGE_IDS), "D80-BRIDGE-IDENTITY")
    _add(
        errors,
        all(u.get("source_author_attribution_applies") is False for u in bridges),
        "D80-BRIDGE-ATTRIBUTION",
    )
    _add(
        errors,
        all(u.get("normalized_release_state") == "complete_owner_reconciled" for u in units),
        "D80-RELEASE-STATE",
    )
    status_counts: dict[str, int] = {}
    for unit in native_units:
        status = unit.get("owner_native_status")
        status_counts[status] = status_counts.get(status, 0) + 1
        if unit.get("source_author_attribution_applies") is not True:
            errors.append("D80-SOURCE-ATTRIBUTION")
    _add(errors, status_counts == EXPECTED_NATIVE_STATUS_COUNTS, "D80-NATIVE-STATUS")

    unit_001 = next((u for u in units if u.get("unit_id") == UNIT_001_ID), {})
    repair = unit_001.get("translation_target", {})
    _add(
        errors,
        repair.get("path") == UNIT_001_TARGET
        and repair.get("bytes") == UNIT_001_BYTES
        and repair.get("sha256") == UNIT_001_SHA256
        and repair.get("projection_repair") == "translation_manifest_fill_for_missing_native_fields"
        and repair.get("native_hash_state") == "missing_in_historical_checkpoint_051"
        and repair.get("identity_authority") == "qa/FULL_TRANSLATION_DRAFT_UNIT_MANIFEST.csv",
        "D80-UNIT001-REPAIR",
    )

    superseded_sequences: set[int] = set()
    for unit in native_units:
        target = unit.get("translation_target") or {}
        sequence = unit.get("sequence")
        if sequence in EXPECTED_SUPERSEDED_TARGET_HASH_SEQUENCES:
            native_hash = target.get("native_unit_index_sha256")
            valid_hash = isinstance(native_hash, str) and bool(native_hash)
            expected_format = (
                "malformed_67_hex"
                if sequence in MALFORMED_SUPERSEDED_TARGET_HASH_SEQUENCES
                else "sha256"
            )
            if (
                valid_hash
                and native_hash != target.get("sha256")
                and target.get("native_unit_index_hash_format") == expected_format
                and target.get("native_hash_state") == "superseded_historical_checkpoint_051"
                and target.get("identity_authority") == "qa/FULL_TRANSLATION_DRAFT_UNIT_MANIFEST.csv"
            ):
                superseded_sequences.add(sequence)
        elif sequence != 1 and any(
            key in target
            for key in (
                "native_unit_index_sha256",
                "native_unit_index_hash_format",
                "native_hash_state",
                "identity_authority",
            )
        ):
            errors.append("D80-HISTORICAL-TARGET-HASH-BOUNDARY")
    _add(
        errors,
        superseded_sequences == set(EXPECTED_SUPERSEDED_TARGET_HASH_SEQUENCES),
        "D80-HISTORICAL-TARGET-HASH-DISAGREEMENTS",
    )

    route_ids = [r.get("route_id") for r in routes]
    _add(errors, len(routes) == 148, "D80-COUNT-ROUTES")
    _add(errors, len(set(route_ids)) == len(route_ids), "D80-ROUTE-ID-DUPLICATE")
    _add(errors, {r.get("unit_id") for r in routes} == set(unit_ids), "D80-ROUTE-UNIT-COVERAGE")
    _add(
        errors,
        all(
            r.get("target_kind") == "corrected_github_pages_reader"
            and str(r.get("target_url", "")).startswith(PAGES_BASE + "#")
            and r.get("reader_head") == PAGES_HEAD
            for r in routes
        ),
        "D80-ROUTE-CORRECTED-PAGES",
    )

    fragment_ids = [f.get("fragment_id") for f in fragments]
    _add(errors, len(fragments) == 32, "D80-COUNT-FRAGMENTS")
    _add(errors, len(set(fragment_ids)) == 32, "D80-FRAGMENT-ID-DUPLICATE")
    _add(
        errors,
        sum(f.get("fragment_type") == "independent_mastery_exercise" for f in fragments) == 16
        and sum(f.get("fragment_type") == "independent_mastery_solution" for f in fragments) == 16,
        "D80-FRAGMENT-TYPES",
    )
    _add(errors, all(f.get("bridge_unit_id") in BRIDGE_IDS for f in fragments), "D80-FRAGMENT-BRIDGE")
    _add(
        errors,
        all(
            f.get("source_author_attribution_applies") is False
            and f.get("target_url") == PAGES_BASE + "#" + str(f.get("fragment_id"))
            for f in fragments
        ),
        "D80-FRAGMENT-ROUTE",
    )

    access = capabilities.get("accessibility", {})
    source_exercises = capabilities.get("source_exercises", {})
    _add(errors, access.get("native_mathml") is False, "D80-NATIVE-MATHML")
    _add(errors, access.get("mathjax_source_nodes") == 27308, "D80-MATHJAX-COUNT")
    _add(errors, access.get("wcag_conformance_claimed") is False, "D80-WCAG-CLAIM")
    _add(errors, access.get("tagged_pdf_claimed") is False, "D80-TAGGED-PDF-CLAIM")
    _add(
        errors,
        source_exercises.get("exercises") == 194
        and source_exercises.get("hints") == 117
        and source_exercises.get("answers") == 0
        and source_exercises.get("solutions") == 0,
        "D80-SOURCE-SOLUTIONS",
    )
    _add(
        errors,
        capabilities.get("independent_mastery_material", {}).get("solutions") == 16,
        "D80-MASTERY-SOLUTIONS",
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
    _add(errors, set(learning_map) == required_map_keys, "D80-LEARNING-MAP-SHAPE")
    _add(
        errors,
        learning_map.get("contract") == CONTRACT
        and learning_map.get("course_id") == "D80"
        and learning_map.get("locale") == "id-ID"
        and learning_map.get("native_dataset") == "urn:uuid:a5c69da3-3783-56e1-ac81-b70ca0cb8d5a",
        "D80-LEARNING-MAP-CONTRACT",
    )
    map_units = learning_map.get("units", [])
    _add(errors, len(map_units) == 148, "D80-LEARNING-MAP-UNIT-COUNT")
    _add(errors, {u.get("id") for u in map_units} == set(unit_ids), "D80-LEARNING-MAP-UNIT-IDS")
    required_unit_keys = {"id", "title", "href", "sections", "objectives_href", "previous_units", "components", "exercises"}
    _add(errors, all(set(u) == required_unit_keys for u in map_units), "D80-LEARNING-MAP-UNIT-SHAPE")
    map_exercises = [exercise for unit in map_units for exercise in unit.get("exercises", [])]
    _add(errors, len(map_exercises) == 16, "D80-LEARNING-MAP-EXERCISE-COUNT")
    _add(
        errors,
        all(
            exercise.get("solution", {}).get("status") == "complete"
            and exercise.get("solution", {}).get("href") == PAGES_BASE + "#" + exercise["id"].replace(".ex", ".sol")
            and exercise.get("hint", {}).get("status") == "not_present"
            and exercise.get("check", {}).get("status") == "not_present"
            for exercise in map_exercises
        ),
        "D80-LEARNING-MAP-SUPPORT",
    )

    refs = {row.get("ledger_id"): row for row in ledgers.get("ledgers", [])}
    _add(errors, set(refs) == {"segments", "terms", "figure_alt_text", "diagram_overrides", "source_corrections"}, "D80-LEDGER-SET")
    _add(
        errors,
        all(
            row.get("projection") == "reference_only"
            and row.get("bodies_copied") is False
            and not any(key in row for key in ("records", "rows", "payload", "body"))
            for row in refs.values()
        ),
        "D80-LEDGER-ZERO-COPY",
    )
    precision = refs.get("segments", {}).get("precision_partition", {})
    _add(
        errors,
        precision.get("exact_source_span") == 4611
        and precision.get("unit_slice") == 1736
        and precision.get("total") == 6347,
        "D80-SEGMENT-PRECISION",
    )
    drift_rows = refs.get("terms", {}).get("preserved_cross_ledger_disagreements", [])
    drift = {
        row.get("concept_id"): (row.get("backend_preferred_id"), row.get("control_preferred_id"))
        for row in drift_rows
    }
    _add(errors, drift == EXPECTED_TERM_DRIFT, "D80-TERM-DRIFT")
    corrections = refs.get("source_corrections", {})
    _add(
        errors,
        corrections.get("status_counts") == EXPECTED_CORRECTION_STATUS_COUNTS,
        "D80-CORRECTION-STATUS",
    )
    _add(
        errors,
        corrections.get("pending_correction_id") == "O014-O001"
        and corrections.get("pending_state") == "observed_not_modified_pending_consolidated_review",
        "D80-PENDING-CORRECTION",
    )

    counts = manifest.get("counts", {})
    _add(errors, manifest.get("contract") == CONTRACT, "D80-CONTRACT")
    _add(errors, manifest.get("contract_projection_path") == "data/learning-map.json", "D80-CONTRACT-PROJECTION")
    _add(
        errors,
        counts.get("native_units") == 146
        and counts.get("independent_mastery_bridges") == 2
        and counts.get("corrected_reader_routes") == 148
        and counts.get("mastery_fragments") == 32
        and counts.get("superseded_checkpoint_target_hashes") == 50
        and counts.get("malformed_superseded_checkpoint_hashes") == 1,
        "D80-MANIFEST-COUNTS",
    )
    return sorted(set(errors))


def apply_negative_mutation(bundle: dict[str, Any], mutation: str) -> dict[str, Any]:
    """Apply one named mutation used by published negative fixtures."""

    changed = copy.deepcopy(bundle)
    if mutation == "duplicate_unit_id":
        changed["units"][1]["unit_id"] = changed["units"][0]["unit_id"]
    elif mutation == "bridge_retyped_as_source":
        bridge = next(u for u in changed["units"] if u["unit_id"] in BRIDGE_IDS)
        bridge["unit_type"] = "translated_source_unit"
    elif mutation == "stale_github_main_route":
        changed["routes"][0]["target_url"] = (
            "https://raw.githubusercontent.com/KokunoYumeto/metode-aljabar-jilid-2-id/"
            + GITHUB_MAIN_COMMIT
            + "/reader/index.html#unit-prelude-unit-001"
        )
        changed["routes"][0]["target_kind"] = "github_main_reader"
    elif mutation == "native_mathml_claim":
        changed["capabilities"]["accessibility"]["native_mathml"] = True
    elif mutation == "remove_unit_001_repair":
        unit = next(u for u in changed["units"] if u["unit_id"] == UNIT_001_ID)
        unit["translation_target"].pop("projection_repair", None)
    elif mutation == "erase_historical_target_hash_disagreement":
        unit = next(
            u for u in changed["units"] if u.get("sequence") in EXPECTED_SUPERSEDED_TARGET_HASH_SEQUENCES
        )
        unit["translation_target"].pop("native_unit_index_sha256", None)
    elif mutation == "claim_source_solutions":
        changed["capabilities"]["source_exercises"]["solutions"] = 16
    elif mutation == "flatten_segment_precision":
        segment = next(r for r in changed["ledgers"]["ledgers"] if r["ledger_id"] == "segments")
        segment["precision_partition"] = {"exact_source_span": 6347, "unit_slice": 0, "total": 6347}
    elif mutation == "collapse_terminology_drift":
        terms = next(r for r in changed["ledgers"]["ledgers"] if r["ledger_id"] == "terms")
        terms["preserved_cross_ledger_disagreements"] = terms["preserved_cross_ledger_disagreements"][:1]
    elif mutation == "accept_pending_correction":
        corrections = next(r for r in changed["ledgers"]["ledgers"] if r["ledger_id"] == "source_corrections")
        corrections["pending_state"] = "accepted_disclosed"
    elif mutation == "drop_mastery_fragment":
        changed["fragments"].pop()
    else:
        raise D80Error(f"D80-UNKNOWN-NEGATIVE-MUTATION:{mutation}")
    return changed


def tree_identity(root: Path, relative_paths: Iterable[str]) -> dict[str, Any]:
    rows = []
    for relative in sorted(relative_paths):
        identity = file_identity(root / relative)
        rows.append({"path": relative.replace("\\", "/"), **identity})
    return {
        "files": rows,
        "sha256": sha256_bytes(b"".join(canonical_json_line(row) for row in rows)),
    }
