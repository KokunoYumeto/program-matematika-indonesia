"""Build the bounded O014/D80 capability adapter from pinned native evidence.

The projection copies unit-level metadata only.  Large/native semantic ledgers
are bound by identity and summarized distinctions, never flattened or copied.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from d80_capability_model_v1 import (
    BRIDGE_IDS,
    CONTRACT,
    EXPECTED_NATIVE_STATUS_COUNTS,
    EXPECTED_SUPERSEDED_TARGET_HASH_SEQUENCES,
    GITHUB_MAIN_COMMIT,
    MALFORMED_SUPERSEDED_TARGET_HASH_SEQUENCES,
    PAGES_BASE,
    PAGES_HEAD,
    PAGES_TREE,
    SOURCE_COMMIT,
    SOURCE_TREE,
    UNIT_001_BYTES,
    UNIT_001_ID,
    UNIT_001_SHA256,
    UNIT_001_TARGET,
    D80Error,
    canonical_json,
    file_identity,
    load_bundle,
    read_json,
    read_jsonl,
    sha256_bytes,
    validate_bundle,
    write_bytes,
    write_json,
    write_jsonl,
)


SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parent.parent
ADAPTER_REL = Path("backend/course-capsule-v1/adapters/d80-capability-v1")
DEFAULT_ADAPTER = PROJECT / ADAPTER_REL
DEFAULT_NATIVE = PROJECT.parent / "methods-of-algebra-volume-2-id"

BRIDGE_SPECS = (
    {
        "unit_id": BRIDGE_IDS[0],
        "sequence": 147,
        "title_id": "Jembatan Penguasaan 001: Pengejaran Diagram",
        "path": "source/id-ID/mastery-bridge-001-diagram-chasing.tex",
    },
    {
        "unit_id": BRIDGE_IDS[1],
        "sequence": 148,
        "title_id": "Jembatan Penguasaan 002: Funktor Turunan dan Barisan Spektral",
        "path": "source/id-ID/mastery-bridge-002-derived-functors-spectral-sequences.tex",
    },
)


def fail(message: str) -> None:
    raise D80Error(message)


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_lock(native: Path, lock: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by_role: dict[str, dict[str, Any]] = {}
    for item in lock["inputs"]:
        path = native / item["path"]
        if not path.is_file():
            fail(f"D80-LOCK-MISSING:{item['path']}")
        actual = file_identity(path)
        if actual["bytes"] != item["bytes"] or actual["sha256"] != item["sha256"]:
            fail(f"D80-LOCK-DRIFT:{item['path']}")
        by_role[item["role"]] = item
    if lock["native_repository"]["source_commit"] != SOURCE_COMMIT:
        fail("D80-LOCK-SOURCE-COMMIT")
    if lock["native_repository"]["source_tree"] != SOURCE_TREE:
        fail("D80-LOCK-SOURCE-TREE")
    if lock["native_repository"]["github_main_commit"] != GITHUB_MAIN_COMMIT:
        fail("D80-LOCK-MAIN-COMMIT")
    if lock["corrected_reader"]["url"] != PAGES_BASE:
        fail("D80-LOCK-PAGES-URL")
    if lock["corrected_reader"]["head"] != PAGES_HEAD or lock["corrected_reader"]["tree"] != PAGES_TREE:
        fail("D80-LOCK-PAGES-IDENTITY")
    return by_role


def exact_input_counts(native: Path, roles: dict[str, dict[str, Any]]) -> None:
    jsonl_roles = ("native_units", "segment_ledger_reference")
    csv_roles = (
        "term_ledger_reference",
        "figure_alt_ledger_reference",
        "source_correction_ledger_reference",
        "terminology_control_reference",
        "upstream_authority_file_manifest",
        "translation_target_manifest",
    )
    for role in jsonl_roles:
        expected = roles[role]["records"]
        actual = len(read_jsonl(native / roles[role]["path"]))
        if actual != expected:
            fail(f"D80-LOCK-COUNT:{role}:{actual}")
    for role in csv_roles:
        expected = roles[role]["records"]
        actual = len(csv_rows(native / roles[role]["path"]))
        if actual != expected:
            fail(f"D80-LOCK-COUNT:{role}:{actual}")
    overrides = read_json(native / roles["diagram_override_ledger_reference"]["path"])["overrides"]
    if len(overrides) != roles["diagram_override_ledger_reference"]["records"]:
        fail("D80-LOCK-COUNT:diagram_override_ledger_reference")


def reader_ids(native: Path, roles: dict[str, dict[str, Any]]) -> set[str]:
    data = (native / roles["corrected_reader_entry"]["path"]).read_text(encoding="utf-8")
    return set(re.findall(r'\bid=["\']([^"\']+)["\']', data))


def build_native_units(
    native: Path, roles: dict[str, dict[str, Any]], ids: set[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_units = read_jsonl(native / roles["native_units"]["path"])
    manifest_rows = csv_rows(native / roles["translation_target_manifest"]["path"])
    target_manifest = {row["path"]: row for row in manifest_rows}
    if len(source_units) != 146 or len(target_manifest) != 146:
        fail("D80-NATIVE-UNIT-BOUNDARY")
    if [row.get("sequence") for row in source_units] != list(range(1, 147)):
        fail("D80-NATIVE-UNIT-SEQUENCE")
    if len({row.get("unit_id") for row in source_units}) != 146:
        fail("D80-NATIVE-UNIT-IDENTITY")

    status_counts = Counter(row.get("status") for row in source_units)
    if dict(sorted(status_counts.items())) != EXPECTED_NATIVE_STATUS_COUNTS:
        fail(f"D80-NATIVE-STATUS:{dict(status_counts)}")

    units: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []
    superseded_target_sequences: set[int] = set()
    for row in source_units:
        if row.get("course_id") != "O014" or row.get("role_id") != "D80":
            fail(f"D80-NATIVE-COURSE:{row.get('unit_id')}")
        if row.get("source_commit") != SOURCE_COMMIT or row.get("source_tree") != SOURCE_TREE:
            fail(f"D80-NATIVE-SOURCE-PIN:{row.get('unit_id')}")

        repaired = row.get("unit_id") == UNIT_001_ID
        target_path = row.get("target_path")
        if repaired:
            if target_path is not None or row.get("target_sha256") is not None:
                fail("D80-UNIT001-NATIVE-ROW-UNEXPECTEDLY-FILLED")
            target_path = UNIT_001_TARGET
        elif not target_path:
            fail(f"D80-NATIVE-TARGET-MISSING:{row.get('unit_id')}")

        manifest_row = target_manifest.get(target_path)
        if not manifest_row:
            fail(f"D80-TARGET-NOT-IN-MANIFEST:{target_path}")
        target_identity = file_identity(native / target_path)
        expected_identity = {
            "bytes": int(manifest_row["bytes"]),
            "sha256": manifest_row["sha256"],
        }
        if target_identity != expected_identity:
            fail(f"D80-TARGET-DRIFT:{target_path}")
        native_target_sha256 = row.get("target_sha256")
        target_hash_disagrees = not repaired and native_target_sha256 != target_identity["sha256"]
        if target_hash_disagrees:
            sequence = row.get("sequence")
            if (
                sequence not in EXPECTED_SUPERSEDED_TARGET_HASH_SEQUENCES
                or row.get("status") != "translated_built_qa_passed"
                or not isinstance(native_target_sha256, str)
            ):
                fail(f"D80-TARGET-HASH-DISAGREEMENT:{row.get('unit_id')}")
            superseded_target_sequences.add(sequence)
        if repaired and target_identity != {"bytes": UNIT_001_BYTES, "sha256": UNIT_001_SHA256}:
            fail("D80-UNIT001-REPAIR-DRIFT")

        translation_target: dict[str, Any] = {"path": target_path, **target_identity}
        if repaired:
            translation_target["projection_repair"] = "translation_manifest_fill_for_missing_native_fields"
            translation_target["native_hash_state"] = "missing_in_historical_checkpoint_051"
            translation_target["identity_authority"] = "qa/FULL_TRANSLATION_DRAFT_UNIT_MANIFEST.csv"
        elif target_hash_disagrees:
            native_hash_format = (
                "sha256"
                if re.fullmatch(r"[0-9a-f]{64}", native_target_sha256)
                else "malformed_67_hex"
                if row.get("sequence") in MALFORMED_SUPERSEDED_TARGET_HASH_SEQUENCES
                and re.fullmatch(r"[0-9a-f]{67}", native_target_sha256)
                else None
            )
            if native_hash_format is None:
                fail(f"D80-HISTORICAL-TARGET-HASH-FORMAT:{row.get('unit_id')}")
            translation_target["native_unit_index_sha256"] = native_target_sha256
            translation_target["native_unit_index_hash_format"] = native_hash_format
            translation_target["native_hash_state"] = "superseded_historical_checkpoint_051"
            translation_target["identity_authority"] = "qa/FULL_TRANSLATION_DRAFT_UNIT_MANIFEST.csv"
        anchor = "unit-" + Path(target_path).stem
        if anchor not in ids:
            fail(f"D80-CORRECTED-READER-MISSING-ANCHOR:{anchor}")
        unit_id = row["unit_id"]
        units.append(
            {
                "schema": "d80-capability-unit/1",
                "unit_id": unit_id,
                "unit_type": "translated_source_unit",
                "sequence": row["sequence"],
                "course_id": "D80",
                "native_course_id": row["course_id"],
                "owner_lane": row["role_id"],
                "title_id": row["title_id"],
                "locale": row["locale"],
                "license_id": row["license_id"],
                "source_author": row["source_author"],
                "source_author_attribution_applies": True,
                "source_locator": {
                    "commit": row["source_commit"],
                    "tree": row["source_tree"],
                    "path": row["source_path"],
                    "start_line": row["source_start_line"],
                    "end_line": row["source_end_line"],
                    "slice_sha256": row["source_slice_sha256"],
                },
                "translation_target": translation_target,
                "owner_native_status": row["status"],
                "normalized_release_state": "complete_owner_reconciled",
                "next_native_unit_id": row.get("next_unit_id"),
                "reader_route_id": "d80.route.section." + unit_id,
            }
        )
        routes.append(
            {
                "schema": "d80-capability-route/1",
                "route_id": "d80.route.section." + unit_id,
                "unit_id": unit_id,
                "route_type": "unit_section",
                "target_kind": "corrected_github_pages_reader",
                "target_anchor": anchor,
                "target_url": PAGES_BASE + "#" + anchor,
                "reader_head": PAGES_HEAD,
                "reader_tree": PAGES_TREE,
            }
        )
    if superseded_target_sequences != set(EXPECTED_SUPERSEDED_TARGET_HASH_SEQUENCES):
        fail(
            "D80-HISTORICAL-TARGET-HASH-BOUNDARY:"
            + ",".join(str(value) for value in sorted(superseded_target_sequences))
        )
    return units, routes


def build_bridges_and_fragments(
    native: Path, ids: set[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    units: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []
    fragments: list[dict[str, Any]] = []
    for spec in BRIDGE_SPECS:
        source = native / spec["path"]
        lines = source.read_text(encoding="utf-8").splitlines()
        stable_units = [
            match.group(1)
            for line in lines
            if (match := re.search(r"^% stable-unit-id:\s*(\S+)\s*$", line))
        ]
        if stable_units != [spec["unit_id"]]:
            fail(f"D80-BRIDGE-STABLE-ID:{spec['path']}")
        anchor = "unit-" + Path(spec["path"]).stem
        if anchor not in ids or spec["unit_id"] not in ids:
            fail(f"D80-BRIDGE-READER-ANCHOR:{spec['unit_id']}")
        source_identity = file_identity(source)
        unit = {
            "schema": "d80-capability-unit/1",
            "unit_id": spec["unit_id"],
            "unit_type": "independent_mastery_bridge",
            "sequence": spec["sequence"],
            "course_id": "D80",
            "native_course_id": None,
            "owner_lane": "O014",
            "title_id": spec["title_id"],
            "locale": "id-ID",
            "license_id": "CC-BY-4.0",
            "source_author": None,
            "source_author_attribution_applies": False,
            "independent_creator_attribution": "OpenAI Codex gpt-5.6-sol, Ultra",
            "source_locator": {"path": spec["path"], **source_identity},
            "translation_target": None,
            "owner_native_status": "not_applicable_independent_material",
            "normalized_release_state": "complete_owner_reconciled",
            "next_native_unit_id": None,
            "reader_route_id": "d80.route.section." + spec["unit_id"],
        }
        units.append(unit)
        routes.append(
            {
                "schema": "d80-capability-route/1",
                "route_id": "d80.route.section." + spec["unit_id"],
                "unit_id": spec["unit_id"],
                "route_type": "independent_mastery_bridge_section",
                "target_kind": "corrected_github_pages_reader",
                "target_anchor": anchor,
                "target_url": PAGES_BASE + "#" + anchor,
                "reader_head": PAGES_HEAD,
                "reader_tree": PAGES_TREE,
            }
        )
        for line_number, line in enumerate(lines, 1):
            match = re.search(r"^% stable-(exercise|solution)-id:\s*(\S+)\s*$", line)
            if not match:
                continue
            kind, fragment_id = match.groups()
            expected_prefix = spec["unit_id"].rsplit(".", 1)[0] + "." + spec["unit_id"].rsplit(".", 1)[1]
            if not fragment_id.startswith(expected_prefix + (".ex" if kind == "exercise" else ".sol")):
                fail(f"D80-FRAGMENT-ID-PREFIX:{fragment_id}")
            if fragment_id not in ids:
                fail(f"D80-FRAGMENT-READER-ANCHOR:{fragment_id}")
            ordinal = int(fragment_id[-2:])
            fragments.append(
                {
                    "schema": "d80-capability-mastery-fragment/1",
                    "fragment_id": fragment_id,
                    "fragment_type": "independent_mastery_" + kind,
                    "bridge_unit_id": spec["unit_id"],
                    "ordinal": ordinal,
                    "locale": "id-ID",
                    "license_id": "CC-BY-4.0",
                    "source_author": None,
                    "source_author_attribution_applies": False,
                    "independent_creator_attribution": "OpenAI Codex gpt-5.6-sol, Ultra",
                    "source_locator": {"path": spec["path"], "marker_line": line_number},
                    "target_anchor": fragment_id,
                    "target_url": PAGES_BASE + "#" + fragment_id,
                    "reader_head": PAGES_HEAD,
                }
            )
    fragments.sort(key=lambda row: (BRIDGE_IDS.index(row["bridge_unit_id"]), row["ordinal"], row["fragment_type"]))
    if len(fragments) != 32:
        fail(f"D80-FRAGMENT-COUNT:{len(fragments)}")
    return units, routes, fragments


def ledger_references(native: Path, roles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    backend_validation = read_json(native / roles["native_backend_validation"]["path"])
    terms = csv_rows(native / roles["term_ledger_reference"]["path"])
    term_control = csv_rows(native / roles["terminology_control_reference"]["path"])
    corrections = csv_rows(native / roles["source_correction_ledger_reference"]["path"])
    term_by_id = {row["concept_id"]: row for row in terms}
    control_by_id = {row["concept_id"]: row for row in term_control}
    drift_ids = ("math.homological.cup_product", "math.set_theory.regular_small_cardinal")
    drift = [
        {
            "concept_id": concept_id,
            "backend_preferred_id": term_by_id[concept_id]["preferred_id"],
            "control_preferred_id": control_by_id[concept_id]["o013_o014_preferred_id"],
            "resolution": "preserve_both_no_adapter_override",
        }
        for concept_id in drift_ids
    ]
    correction_counts = dict(sorted(Counter(row["status"] for row in corrections).items()))
    pending = next(row for row in corrections if row["correction_id"] == "O014-O001")

    def ref(role: str, ledger_id: str, record_count: int) -> dict[str, Any]:
        item = roles[role]
        return {
            "ledger_id": ledger_id,
            "native_path": item["path"],
            "bytes": item["bytes"],
            "sha256": item["sha256"],
            "record_count": record_count,
            "projection": "reference_only",
            "bodies_copied": False,
        }

    segments = ref("segment_ledger_reference", "segments", 6347)
    segments["precision_partition"] = {
        "exact_source_span": backend_validation["segments"]["exact_source_span_records"],
        "unit_slice": backend_validation["segments"]["unit_slice_source_span_records"],
        "total": backend_validation["segments"]["count"],
    }
    segments["precision_rule"] = "unit_slice_is_not_exact_per_segment_source_span"
    terms_ref = ref("term_ledger_reference", "terms", 511)
    terms_ref["status_counts"] = dict(sorted(Counter(row["status"] for row in terms).items()))
    terms_ref["control_ledger"] = {
        "native_path": roles["terminology_control_reference"]["path"],
        "bytes": roles["terminology_control_reference"]["bytes"],
        "sha256": roles["terminology_control_reference"]["sha256"],
        "record_count": 511,
    }
    terms_ref["preserved_cross_ledger_disagreements"] = drift
    alt = ref("figure_alt_ledger_reference", "figure_alt_text", 829)
    alt["semantic_note"] = "diagram descriptions are summaries, not complete substitutes for visual relations"
    overrides = ref("diagram_override_ledger_reference", "diagram_overrides", 13)
    overrides["semantic_note"] = "reader-only source-derived replacements; canonical alt ledger unchanged"
    correction_ref = ref("source_correction_ledger_reference", "source_corrections", 73)
    correction_ref["status_counts"] = correction_counts
    correction_ref["pending_correction_id"] = pending["correction_id"]
    correction_ref["pending_state"] = pending["status"]
    correction_ref["accepted_recorded_correction_id"] = "O014-C037"
    return {
        "schema": "d80-capability-ledger-references/1",
        "zero_copy": True,
        "ledgers": [segments, terms_ref, alt, overrides, correction_ref],
    }


def course_record(lock: dict[str, Any], native: Path, roles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    reconciliation = read_json(native / roles["owner_completion_reconciliation"]["path"])
    pages = reconciliation["public_evidence"]["github_pages"]
    github = reconciliation["public_evidence"]["github_main"]
    zenodo = reconciliation["public_evidence"]["zenodo_latest"]
    if pages["head"] != PAGES_HEAD or pages["tree"] != PAGES_TREE or pages["root_sha256"] != lock["corrected_reader"]["entry_sha256"]:
        fail("D80-RECONCILIATION-PAGES-DRIFT")
    return {
        "schema": "d80-capability-course/1",
        "contract_2_3_1_conformance": "not_claimed",
        "course_id": "D80",
        "course_uuid": lock["central_course_uuid"],
        "owner_lane": "O014",
        "native_dataset_id": lock["native_dataset_id"],
        "title_id": "Teori Kategori dan Metode Homologis",
        "topic": "Aljabar",
        "level": "D",
        "prerequisites": ["C30", "C80", "D70"],
        "locale": "id-ID",
        "reader_route_authority": "github_pages_corrected",
        "source_authority": {
            "author": "Wen-Wei Li",
            "work": "Methods of Algebra, Volume 2: Linear Algebra",
            "commit": SOURCE_COMMIT,
            "tree": SOURCE_TREE,
            "license": "CC-BY-4.0",
        },
        "public_lineage": {
            "github_main": {
                "repository": github["repository"],
                "commit": github["commit"],
                "tree": github["tree"],
                "reader_routable": False,
                "reader_state": "superseded_by_corrected_pages",
            },
            "github_pages": {
                "url": pages["url"],
                "head": pages["head"],
                "tree": pages["tree"],
                "root_bytes": pages["root_bytes"],
                "root_sha256": pages["root_sha256"],
                "reader_routable": True,
            },
            "zenodo": {
                "concept_doi": zenodo["concept_doi"],
                "complete_parent_record_id": zenodo["parent_record_id"],
                "latest_correction_record_id": zenodo["record_id"],
                "latest_correction_doi": zenodo["doi"],
                "access": zenodo["access"],
            },
        },
        "central_catalog_context": {
            "recorded_state": "production",
            "recorded_checkpoint_through_unit": 50,
            "recorded_zenodo_record_id": "22143171",
            "superseded_for_adapter_routing": True,
        },
        "normalized_release_state": "complete_owner_reconciled",
    }


def capabilities_record(native: Path, roles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    reader_validation = read_json(native / roles["corrected_reader_validation"]["path"])
    source_authority = (native / roles["source_scope_authority"]["path"]).read_text(encoding="utf-8")
    if "194 top-level exercises and 117 embedded hints" not in source_authority:
        fail("D80-SOURCE-SCOPE-COUNTS")
    if reader_validation["mathml_elements"] != 0 or reader_validation["mathjax_source_elements"] != 27308:
        fail("D80-READER-MATH-FACTS")
    return {
        "schema": "d80-capability-declarations/1",
        "course_id": "D80",
        "learner": {
            "searchable_unit_navigation": True,
            "corrected_reader_routes": 148,
            "exact_mastery_fragment_routes": 32,
            "complete_pdf_available": True,
            "native_semantic_bodies_embedded": False,
        },
        "educator": {
            "shared_unit_identities_with_learner": True,
            "owner_status_visible": True,
            "source_and_independent_material_separated": True,
            "precision_and_correction_caveats_visible": True,
        },
        "source_exercises": {"exercises": 194, "hints": 117, "answers": 0, "solutions": 0},
        "independent_mastery_material": {"bridges": 2, "exercises": 16, "solutions": 16},
        "accessibility": {
            "html_reader": True,
            "diagram_textual_fallbacks": reader_validation["diagram_alt_texts_applied"],
            "native_mathml": False,
            "math_rendering": "MathJax_source_with_runtime_assistive_MathML_only",
            "mathjax_source_nodes": reader_validation["mathjax_source_elements"],
            "local_references_checked": reader_validation["local_references_checked"],
            "wcag_conformance_claimed": False,
            "tagged_pdf_claimed": False,
            "complete_tounicode_claimed": False,
            "user_assistive_technology_testing_claimed": False,
        },
        "limitations": [
            "This adapter provides identities, evidence, and routes; it does not copy native unit, segment, term, correction, or diagram bodies.",
            "The corrected reader contains no native MathML; assistive MathML depends on MathJax runtime, browser, and assistive technology.",
            "Diagram descriptions summarize visual relations and are not complete substitutes for them.",
            "The PDF is not claimed to be tagged and has incomplete ToUnicode coverage.",
            "No WCAG level or user assistive-technology test result is claimed.",
            "GitHub main retains a superseded reader; learner routes intentionally use the corrected GitHub Pages head.",
            "The frozen 51-unit checkpoint index omits Unit 001's target identity and retains superseded target hashes for Units 002--051; the final 146-row translation manifest and matching current bytes govern adapter routes while the historical identities remain disclosed.",
            "The source work provides no answers or solutions; all exposed solution fragments are independent mastery-bridge material.",
            "The public repository does not contain a self-contained native backend/reader replay toolchain.",
        ],
    }


def learning_map_record(
    lock: dict[str, Any],
    units: list[dict[str, Any]],
    routes: list[dict[str, Any]],
    fragments: list[dict[str, Any]],
    capabilities: dict[str, Any],
) -> dict[str, Any]:
    """Emit the exact strict shared-contract shape without widening its schema."""

    route_by_unit = {row["unit_id"]: row for row in routes}
    fragments_by_bridge: dict[str, list[dict[str, Any]]] = {bridge_id: [] for bridge_id in BRIDGE_IDS}
    for fragment in fragments:
        fragments_by_bridge[fragment["bridge_unit_id"]].append(fragment)
    map_units = []
    previous: str | None = None
    for unit in units:
        component_source = (
            "d80.source.independent-mastery"
            if unit["unit_type"] == "independent_mastery_bridge"
            else "d80.source.translated-edition"
        )
        exercises = []
        if unit["unit_id"] in BRIDGE_IDS:
            bridge_fragments = fragments_by_bridge[unit["unit_id"]]
            exercise_by_ordinal = {
                row["ordinal"]: row for row in bridge_fragments if row["fragment_type"] == "independent_mastery_exercise"
            }
            solution_by_ordinal = {
                row["ordinal"]: row for row in bridge_fragments if row["fragment_type"] == "independent_mastery_solution"
            }
            for ordinal in range(1, 9):
                exercise = exercise_by_ordinal[ordinal]
                solution = solution_by_ordinal[ordinal]
                exercises.append(
                    {
                        "id": exercise["fragment_id"],
                        "unit_id": unit["unit_id"],
                        "title": f"Latihan mastery {ordinal}",
                        "kind": "independent_mastery_exercise",
                        "sequence": ordinal,
                        "curriculum_status": "independent_mastery_material",
                        "href": exercise["target_url"],
                        "hint": {"status": "not_present", "source_anchor": exercise["fragment_id"], "label": None, "href": None},
                        "check": {"status": "not_present", "source_anchor": exercise["fragment_id"], "label": None, "href": None},
                        "solution": {
                            "status": "complete",
                            "source_anchor": solution["fragment_id"],
                            "label": f"Solusi lengkap {ordinal}",
                            "href": solution["target_url"],
                        },
                    }
                )
        map_units.append(
            {
                "id": unit["unit_id"],
                "title": unit["title_id"],
                "href": route_by_unit[unit["unit_id"]]["target_url"],
                "sections": [route_by_unit[unit["unit_id"]]["target_anchor"]],
                "objectives_href": None,
                "previous_units": [] if previous is None else [previous],
                "components": [
                    {
                        "id": "d80.component." + unit["unit_id"],
                        "source": component_source,
                        "license": "CC-BY-4.0",
                    }
                ],
                "exercises": exercises,
            }
        )
        previous = unit["unit_id"]
    github_commit = lock["native_repository"]["github_main_commit"]
    return {
        "contract": CONTRACT,
        "course_id": "D80",
        "locale": "id-ID",
        "native_dataset": lock["native_dataset_id"],
        "source_catalog": {
            "path": "backend/units.jsonl",
            "bytes": 109448,
            "sha256": "d4b7cccf260f4576735ef5f3e904bb10087f0837e367e32d353f54f9bff0e33a",
            "url": "https://raw.githubusercontent.com/KokunoYumeto/metode-aljabar-jilid-2-id/"
            + github_commit
            + "/backend/units.jsonl",
        },
        "units": map_units,
        "prerequisite_routes": [],
        "labs": [],
        "environments": [],
        "artifacts": [
            {"id": "d80.artifact.corrected-reader", "kind": "html-reader", "path": PAGES_BASE},
            {
                "id": "d80.artifact.complete-pdf",
                "kind": "pdf",
                "path": "https://zenodo.org/records/22167691/files/00_metode-dalam-aljabar-jilid-2-edisi-bahasa-indonesia.pdf",
            },
            {
                "id": "d80.artifact.semantic-backend",
                "kind": "native-backend-archive",
                "path": "https://zenodo.org/records/22167691/files/02_backend-semantik.zip",
            },
        ],
        "sources": [
            {
                "id": "d80.source.authority",
                "role": "source_authority",
                "license": "CC-BY-4.0",
                "identity": SOURCE_COMMIT + ":" + SOURCE_TREE,
            },
            {
                "id": "d80.source.translated-edition",
                "role": "indonesian_translation",
                "license": "CC-BY-4.0",
                "identity": github_commit,
            },
            {
                "id": "d80.source.corrected-reader",
                "role": "reader_route_authority",
                "license": "CC-BY-4.0",
                "identity": PAGES_HEAD + ":" + PAGES_TREE,
            },
            {
                "id": "d80.source.independent-mastery",
                "role": "independent_mastery_material",
                "license": "CC-BY-4.0",
                "identity": "d216070b6d1fe6ea12b72cd53574b1980b24acd4099442749ea37ede2f581342:627b2f66e1c411df15819f9be9bbd0204d0abcb16940be9ef1d8f29806865745",
            },
        ],
        "external_relation_nodes": ["C30", "C80", "D70"],
        "limitations": capabilities["limitations"],
    }


def style() -> str:
    return """
:root{color-scheme:light dark;--bg:#f5f3ed;--ink:#17221f;--card:#fff;--line:#c8d0ca;--accent:#075e54;--soft:#e4f3ee;--warn:#7a4d00}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1180px;margin:auto;padding:2rem 1rem 4rem}header{border-bottom:4px solid var(--accent);margin-bottom:1.5rem}h1{line-height:1.12}
a{color:var(--accent)}.lede{max-width:78ch}.facts{display:flex;gap:.6rem;flex-wrap:wrap}.badge{background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:.25rem .65rem}
.controls{display:grid;grid-template-columns:minmax(15rem,1fr) auto;gap:.7rem;margin:1.2rem 0}input,select{font:inherit;padding:.65rem;border:1px solid var(--line);border-radius:.4rem;background:var(--card);color:inherit}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:.75rem}.card,section{background:var(--card);border:1px solid var(--line);border-radius:.55rem;padding:1rem}.card h2{font-size:1rem;margin:.15rem 0}.id{font:12px/1.4 ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere}.meta{font-size:.88rem;color:#4d5b56}.mastery{border-left:5px solid #9b6500}
table{width:100%;border-collapse:collapse;background:var(--card);font-size:.88rem}th,td{text-align:left;vertical-align:top;border:1px solid var(--line);padding:.45rem;overflow-wrap:anywhere}th{position:sticky;top:0;background:var(--soft)}.scroll{overflow:auto;max-height:70vh}.warning{border-left:5px solid var(--warn)}
@media(prefers-color-scheme:dark){:root{--bg:#111815;--ink:#eef4ef;--card:#18221e;--line:#3e5149;--accent:#79d5be;--soft:#203830;--warn:#f1bf68}.meta{color:#b8c6c0}}
""".strip()


def learner_html(course: dict[str, Any], units: list[dict[str, Any]], routes: list[dict[str, Any]], fragments: list[dict[str, Any]]) -> str:
    route_by_unit = {row["unit_id"]: row for row in routes}
    cards = []
    for unit in units:
        route = route_by_unit[unit["unit_id"]]
        kind = "Jembatan mandiri" if unit["unit_type"] == "independent_mastery_bridge" else "Unit sumber terjemahan"
        css = "card mastery" if unit["unit_type"] == "independent_mastery_bridge" else "card"
        cards.append(
            f'<article class="{css}" data-unit-id="{html.escape(unit["unit_id"], quote=True)}" data-unit-type="{html.escape(unit["unit_type"], quote=True)}">'
            f'<div class="meta">{unit["sequence"]:03d} · {kind}</div><h2>{html.escape(unit["title_id"])}</h2>'
            f'<div class="id">{html.escape(unit["unit_id"])}</div><p><a href="{html.escape(route["target_url"], quote=True)}">Buka di pembaca terkoreksi</a></p></article>'
        )
    frag_items = []
    for fragment in fragments:
        label = "Latihan" if fragment["fragment_type"].endswith("exercise") else "Solusi"
        frag_items.append(
            f'<li data-fragment-id="{html.escape(fragment["fragment_id"], quote=True)}"><a href="{html.escape(fragment["target_url"], quote=True)}">'
            f'{label} {fragment["ordinal"]}: <span class="id">{html.escape(fragment["fragment_id"])}</span></a></li>'
        )
    return f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>D80 · Hub pembelajar</title><style>{style()}</style></head><body><main>
<header><p>D80 · O014 · id-ID</p><h1>{html.escape(course['title_id'])}</h1><p class="lede">Navigasi 146 unit sumber terjemahan dan dua jembatan penguasaan mandiri. Semua pranala membaca memakai GitHub Pages terkoreksi pada head <span class="id">{PAGES_HEAD}</span>, bukan pembaca lama di GitHub main.</p></header>
<div class="facts"><span class="badge">148 rute unit</span><span class="badge">16 latihan mastery</span><span class="badge">16 solusi mastery</span><span class="badge">864 halaman PDF</span></div>
<p><a href="D80-pengajar.html">Buka tampilan pengajar</a> · <a href="https://doi.org/10.5281/zenodo.22167691">Edisi koreksi Zenodo</a> · <a href="https://github.com/KokunoYumeto/metode-aljabar-jilid-2-id">Repositori publik</a></p>
<div class="controls"><label>Cari judul atau ID <input id="q" type="search" autocomplete="off"></label><label>Jenis <select id="kind"><option value="">Semua</option><option value="translated_source_unit">Unit sumber</option><option value="independent_mastery_bridge">Jembatan mandiri</option></select></label></div>
<div id="units" class="grid">{''.join(cards)}</div>
<section><h2>Latihan dan solusi jembatan mandiri</h2><p>Fragmen ini materi tambahan independen; karya sumber memiliki 194 latihan dan 117 petunjuk, tetapi tidak menyediakan jawaban atau solusi.</p><ol>{''.join(frag_items)}</ol></section>
<section class="warning"><h2>Batas aksesibilitas</h2><p>Pembaca menyediakan 829 ringkasan diagram dan sumber matematika MathJax. Tidak ada MathML native; keluaran bantu MathML hanya tersedia saat runtime. Tidak ada klaim WCAG, PDF bertag, ToUnicode lengkap, atau pengujian teknologi bantu pengguna.</p></section>
</main><script>const q=document.querySelector('#q'),k=document.querySelector('#kind'),cards=[...document.querySelectorAll('[data-unit-id]')];function f(){{const s=q.value.toLocaleLowerCase('id'),t=k.value;for(const c of cards)c.hidden=!!((t&&c.dataset.unitType!==t)||(s&&!c.textContent.toLocaleLowerCase('id').includes(s)))}}q.addEventListener('input',f);k.addEventListener('change',f);</script></body></html>
"""


def educator_html(course: dict[str, Any], units: list[dict[str, Any]], routes: list[dict[str, Any]], ledgers: dict[str, Any]) -> str:
    route_by_unit = {row["unit_id"]: row for row in routes}
    rows = []
    for unit in units:
        source = unit["source_locator"]
        if unit["unit_type"] == "translated_source_unit":
            source_locator = f"{source['path']}:{source['start_line']}-{source['end_line']}"
            target = unit["translation_target"]["path"]
        else:
            source_locator = source["path"]
            target = "—"
        rows.append(
            f'<tr data-unit-id="{html.escape(unit["unit_id"], quote=True)}"><td>{unit["sequence"]:03d}</td><td class="id">{html.escape(unit["unit_id"])}</td>'
            f'<td>{html.escape(unit["unit_type"])}</td><td>{html.escape(unit["title_id"])}</td><td>{html.escape(str(unit["owner_native_status"]))}</td>'
            f'<td class="id">{html.escape(source_locator)}</td><td class="id">{html.escape(target)}</td><td><a href="{html.escape(route_by_unit[unit["unit_id"]]["target_url"], quote=True)}">baca</a></td></tr>'
        )
    segment = next(row for row in ledgers["ledgers"] if row["ledger_id"] == "segments")
    terms = next(row for row in ledgers["ledgers"] if row["ledger_id"] == "terms")
    corrections = next(row for row in ledgers["ledgers"] if row["ledger_id"] == "source_corrections")
    drift_rows = "".join(
        f"<li><span class=\"id\">{html.escape(row['concept_id'])}</span>: backend “{html.escape(row['backend_preferred_id'])}”; kontrol “{html.escape(row['control_preferred_id'])}” — keduanya dipertahankan tanpa override adapter.</li>"
        for row in terms["preserved_cross_ledger_disagreements"]
    )
    return f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>D80 · Tampilan pengajar</title><style>{style()}</style></head><body><main>
<header><p>D80 · bukti dan penyelarasan pengajar</p><h1>{html.escape(course['title_id'])}</h1><p class="lede">Tampilan ini memakai 148 identitas unit dan rute yang sama dengan hub pembelajar, sambil mempertahankan status pemilik, provenans, dan batas bukti.</p></header>
<p><a href="D80.html">Kembali ke hub pembelajar</a></p>
<section><h2>Pemisahan status</h2><p>146 baris native mempertahankan status pemilik apa adanya: 51 <span class="id">translated_built_qa_passed</span> dan 95 <span class="id">translated_backend_indexed</span>. Status rilis terormalisasi <span class="id">complete_owner_reconciled</span> adalah bidang terpisah yang dibuktikan oleh rekonsiliasi 146 unit; ia tidak menulis ulang ledger native. Dua jembatan adalah materi instruksional mandiri, bukan teks sumber Wen-Wei Li.</p></section>
<section><h2>Presisi, istilah, koreksi</h2><p>Ledger segmen dirujuk tanpa disalin: {segment['precision_partition']['exact_source_span']:,} rekaman memiliki rentang sumber eksak; {segment['precision_partition']['unit_slice']:,} hanya memiliki presisi <span class="id">unit_slice</span>. Jangan menyamakannya.</p><ul>{drift_rows}</ul><p>Koreksi: 71 <span class="id">accepted_disclosed</span>, satu <span class="id">accepted_recorded</span> (O014-C037), dan O014-O001 tetap <span class="id">{html.escape(corrections['pending_state'])}</span>.</p></section>
<section class="warning"><h2>Penilaian dan aksesibilitas</h2><p>Sumber memiliki 194 latihan dan 117 petunjuk, tanpa jawaban atau solusi. Hanya dua jembatan mandiri yang menyumbang 16 latihan dan 16 solusi terpetakan. Pembaca tidak memiliki MathML native; tidak ada klaim WCAG, PDF bertag, ToUnicode lengkap, atau uji teknologi bantu pengguna.</p></section>
<h2>Keselarasan 148 unit</h2><div class="scroll"><table><thead><tr><th>No.</th><th>ID stabil</th><th>Tipe</th><th>Judul</th><th>Status pemilik</th><th>Lokator sumber</th><th>Target</th><th>Rute</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
</main></body></html>
"""


def tooling_inventory(project: Path, adapter: Path) -> list[dict[str, Any]]:
    paths = [
        project / "scripts/d80_capability_model_v1.py",
        project / "scripts/build_d80_capability_v1.py",
        project / "scripts/validate_d80_capability_v1.py",
        adapter / "README.md",
        adapter / "input/source-lock.json",
    ]
    paths.extend(sorted((adapter / "fixtures/negative").glob("*.json"), key=lambda p: p.as_posix()))
    result = []
    for path in paths:
        if not path.is_file():
            fail(f"D80-TOOLING-MISSING:{path}")
        result.append({"path": path.relative_to(project).as_posix(), **file_identity(path)})
    return result


def build(native: Path, output: Path, lock_path: Path) -> dict[str, Any]:
    lock = read_json(lock_path)
    roles = verify_lock(native, lock)
    exact_input_counts(native, roles)
    ids = reader_ids(native, roles)
    native_units, native_routes = build_native_units(native, roles, ids)
    bridge_units, bridge_routes, fragments = build_bridges_and_fragments(native, ids)
    units = native_units + bridge_units
    routes = native_routes + bridge_routes
    ledgers = ledger_references(native, roles)
    course = course_record(lock, native, roles)
    capabilities = capabilities_record(native, roles)
    learning_map = learning_map_record(lock, units, routes, fragments, capabilities)

    write_json(output / "data/course.json", course)
    write_json(output / "data/learning-map.json", learning_map)
    write_jsonl(output / "data/units.jsonl", units)
    write_jsonl(output / "data/routes.jsonl", routes)
    write_jsonl(output / "data/mastery-fragments.jsonl", fragments)
    write_json(output / "data/ledger-references.json", ledgers)
    write_json(output / "data/capabilities.json", capabilities)
    write_bytes(output / "views/D80.html", learner_html(course, units, routes, fragments).encode("utf-8"))
    write_bytes(output / "views/D80-pengajar.html", educator_html(course, units, routes, ledgers).encode("utf-8"))

    generated_paths = [
        "data/capabilities.json",
        "data/course.json",
        "data/ledger-references.json",
        "data/learning-map.json",
        "data/mastery-fragments.jsonl",
        "data/routes.jsonl",
        "data/units.jsonl",
        "views/D80-pengajar.html",
        "views/D80.html",
    ]
    outputs = [{"path": path, **file_identity(output / path)} for path in generated_paths]
    output_tree_sha256 = sha256_bytes(
        b"".join(canonical_json(row) for row in sorted(outputs, key=lambda row: row["path"]))
    )
    manifest = {
        "schema": "d80-capability-manifest/1",
        "contract": CONTRACT,
        "contract_projection_path": "data/learning-map.json",
        "contract_2_3_1_conformance": "not_claimed",
        "course_id": "D80",
        "owner_lane": "O014",
        "native_family": "category_and_homological_methods",
        "counts": {
            "native_units": 146,
            "independent_mastery_bridges": 2,
            "corrected_reader_routes": 148,
            "mastery_fragments": 32,
            "independent_mastery_exercises": 16,
            "independent_mastery_solutions": 16,
            "superseded_checkpoint_target_hashes": 50,
            "malformed_superseded_checkpoint_hashes": 1,
        },
        "projection": {
            "native_ids_preserved": True,
            "native_status_preserved_separately": True,
            "unit_001_manifest_repair": True,
            "historical_checkpoint_target_hashes_preserved": 50,
            "native_ledger_bodies_copied": False,
            "corrected_pages_routes_only": True,
            "public_state_changed": False,
        },
        "inputs": lock["inputs"],
        "tooling": tooling_inventory(PROJECT, DEFAULT_ADAPTER),
        "outputs": outputs,
        "output_tree_sha256": output_tree_sha256,
        "public_release_status": "unchanged_not_published_by_adapter",
    }
    write_json(output / "manifest.json", manifest)
    errors = validate_bundle(load_bundle(output))
    if errors:
        fail("D80-BUILT-MODEL-INVALID:" + ",".join(errors))
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--source-lock", type=Path, default=DEFAULT_ADAPTER / "input/source-lock.json")
    args = parser.parse_args()
    manifest = build(args.native_root.resolve(), args.output_root.resolve(), args.source_lock.resolve())
    print(
        json.dumps(
            {
                "state": "pass",
                "course_id": "D80",
                "output_root": str(args.output_root.resolve()),
                "output_tree_sha256": manifest["output_tree_sha256"],
                "counts": manifest["counts"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (D80Error, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"D80 build failed: {exc}", file=sys.stderr)
        sys.exit(1)
