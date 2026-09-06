#!/usr/bin/env python3
"""Independently validate the A10 Elementary Algebra v2.3.1 adapter.

The semantic checks intentionally reject copied body prose, invented unit
routes, inferred translation state, flattened component rights, or fabricated
item-level assessment records.  Optional negative probes operate only on
in-memory copies and demonstrate those failure modes are rejected.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Iterable, Mapping

from v231_adapter_common import (
    CAPABILITY_NAMES,
    TABLE_ORDER,
    AdapterError,
    identity_set_sha256,
    mapping_set_sha256,
    projection_id,
    read_json,
    read_jsonl,
    require,
    sha256_bytes,
    sha256_file,
    write_json,
)
from validate_lane_adapter_v231 import validate_package as validate_generic_package


COMMON_NAMESPACE = "7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd"
LANE_NAMESPACE = uuid.uuid5(uuid.UUID(COMMON_NAMESPACE), "v2.3.1:A10:elementary-algebra-2e")
OWNER_NAMESPACE = "openstax-cnxml-module-id/elementary-algebra-2e/id-ID/v1.0.3"
CURRENT_COURSE_ID = "urn:uuid:c2a0d387-a544-54ca-9b89-6d654a9bc200"
PREREQUISITE_A00_COURSE_ID = "urn:uuid:8d8ea368-373c-54d7-a6d3-4d9cfdaf46fe"
PUBLIC_PDF = "https://zenodo.org/records/22236314/files/00-elementary-algebra-2e-bahasa-indonesia-EA2-C0082-reader.pdf?download=1"
AUTHORITY_RELATIVE = "backend/v2.3/authorities/A10_ELEMENTARY_ALGEBRA_PUBLIC_RELEASE_AUTHORITY_20260906.json"
AUTHORITY_BYTES = 50883
AUTHORITY_SHA256 = "5ae589b75842923a0ebc530d649498bec9bb962ae0d14ab1cb44a9aedb573678"

EXPECTED_TABLE_COUNTS = {
    "owner_authorities": 1,
    "datasets": 1,
    "editions": 1,
    "units": 82,
    "course_unit_memberships": 82,
    "native_bindings": 82,
    "content_bindings": 0,
    "relations": 82,
    "rights": 1,
    "rights_assignments": 2,
    "artifacts": 7,
    "build_recipes": 0,
    "reader_surfaces": 1,
    "routes": 1,
    "search_documents": 82,
    "adapter_profiles": 1,
    "adapter_runs": 1,
    "qa_events": 3,
    "identity_crosswalks": 82,
}

EXPECTED_ARTIFACTS = {
    "00-elementary-algebra-2e-bahasa-indonesia-EA2-C0082-reader.pdf": (74917277, "e4bc958edeb60a41604862dd0b67692bbfbcbb85b5de906c92af1f6c93bda505"),
    "elementary-algebra-2e-id-ID-1.0.3-source.zip": (7264274, "77a6ecfa22c4a5b58b0b7f72e5ec9db11ac4656bc7fc9c4944a4a7916a2472f3"),
    "elementary-algebra-2e-id-ID-1.0.3-backend-core.zip": (147766660, "6dc5ddafb3178d82308819ced69f724919dcb388168c5c63ec39db9e99777b13"),
    "elementary-algebra-2e-id-ID-1.0.3-release-manifest.json": (39066, "a1cb3f183b37fc80013d3be68966bcbe667ae735582063a25cb4d3dd55ea2805"),
    "00-elementary-algebra-2e-bahasa-indonesia-EA2-C0082-reader-build-manifest.json": (4282699, "821d123602e75f6c1008c0d91350c2cc2c6c9ddeea5c76d00e922f59bd34a7b3"),
    "EA2-C0082-reader-QA-final.json": (3050, "449dff1ca701690ce9bfffd5055010a5ff22b7b29ef206c480899f37689b2bb6"),
    "LICENSE.txt": (21442, "ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a"),
}


def load_tables(package: Path) -> dict[str, list[dict[str, Any]]]:
    return {name: read_jsonl(package / "tables" / f"{name}.jsonl") for name in TABLE_ORDER}


def recursively_forbidden_prose_keys(value: Any, location: str = "$") -> list[str]:
    forbidden_names = {
        "body", "body_text", "textbook_prose", "source_prose", "target_prose",
        "source_text", "target_text", "solution_text", "proof_text", "exercise_text",
    }
    failures: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in forbidden_names:
                failures.append(f"{location}.{key}")
            failures.extend(recursively_forbidden_prose_keys(child, f"{location}.{key}"))
    elif isinstance(value, list):
        for ordinal, child in enumerate(value):
            failures.extend(recursively_forbidden_prose_keys(child, f"{location}[{ordinal}]"))
    return failures


def validate_reference_closure(tables: Mapping[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Require every adapter-internal foreign key to resolve exactly once."""
    owner_ids = {str(row["id"]) for row in tables["owner_authorities"]}
    dataset_ids = {str(row["id"]) for row in tables["datasets"]}
    edition_ids = {str(row["id"]) for row in tables["editions"]}
    unit_ids = {str(row["id"]) for row in tables["units"]}
    rights_ids = {str(row["id"]) for row in tables["rights"]}
    artifact_ids = {str(row["id"]) for row in tables["artifacts"]}
    surface_ids = {str(row["id"]) for row in tables["reader_surfaces"]}
    profile_ids = {str(row["id"]) for row in tables["adapter_profiles"]}
    require(len(owner_ids) == len(dataset_ids) == len(edition_ids) == len(rights_ids) == len(surface_ids) == len(profile_ids) == 1, "A10 singleton identity census drift")

    references_checked = 0
    for table_name, rows in tables.items():
        for row in rows:
            require(str(row["dataset_id"]) in dataset_ids, f"A10 orphan dataset_id: {table_name}:{row['semantic_key']}")
            require(str(row["owner_authority_id"]) in owner_ids, f"A10 orphan owner_authority_id: {table_name}:{row['semantic_key']}")
            references_checked += 2

    for row in tables["units"]:
        require(str(row["payload"]["edition_id"]) in edition_ids, f"A10 orphan unit edition: {row['semantic_key']}")
        references_checked += 1
    for row in tables["course_unit_memberships"]:
        require(str(row["payload"]["edition_id"]) in edition_ids, f"A10 orphan membership edition: {row['semantic_key']}")
        require(str(row["payload"]["unit_id"]) in unit_ids, f"A10 orphan membership unit: {row['semantic_key']}")
        references_checked += 2
    for row in tables["native_bindings"]:
        require(str(row["payload"]["projected_record_id"]) in unit_ids, f"A10 orphan native-binding target: {row['semantic_key']}")
        references_checked += 1
    for row in tables["relations"]:
        payload = row["payload"]
        if payload["relation_type"] == "precedes_in_release_order":
            require(str(payload["source_unit_id"]) in unit_ids, f"A10 orphan sequence source: {row['semantic_key']}")
            require(str(payload["target_unit_id"]) in unit_ids, f"A10 orphan sequence target: {row['semantic_key']}")
            references_checked += 2
    for row in tables["rights_assignments"]:
        payload = row["payload"]
        require(str(payload["rights_id"]) in rights_ids, f"A10 orphan rights ID: {row['semantic_key']}")
        target_type = str(payload["target_record_type"])
        target_ids = dataset_ids if target_type == "dataset" else edition_ids if target_type == "edition" else set()
        require(str(payload["target_record_id"]) in target_ids, f"A10 orphan rights target: {row['semantic_key']}")
        references_checked += 2
    for row in tables["reader_surfaces"]:
        require(str(row["payload"]["artifact_id"]) in artifact_ids, f"A10 orphan reader artifact: {row['semantic_key']}")
        references_checked += 1
    for row in tables["routes"]:
        require(str(row["payload"]["reader_surface_id"]) in surface_ids, f"A10 orphan route surface: {row['semantic_key']}")
        references_checked += 1
    for row in tables["search_documents"]:
        require(str(row["payload"]["unit_id"]) in unit_ids, f"A10 orphan search unit: {row['semantic_key']}")
        references_checked += 1
    for row in tables["adapter_runs"]:
        require(str(row["payload"]["profile_id"]) in profile_ids, f"A10 orphan adapter profile: {row['semantic_key']}")
        references_checked += 1
    for row in tables["identity_crosswalks"]:
        require(str(row["payload"]["target_record_id"]) in unit_ids, f"A10 orphan crosswalk target: {row['semantic_key']}")
        references_checked += 1
    return {
        "result": "PASS",
        "references_checked": references_checked,
        "orphan_references": 0,
        "owner_authority_ids": len(owner_ids),
        "dataset_ids": len(dataset_ids),
    }


def validate_table_semantics(
    tables: Mapping[str, list[dict[str, Any]]], authority: Mapping[str, Any]
) -> dict[str, Any]:
    observed_counts = {name: len(tables[name]) for name in TABLE_ORDER}
    require(observed_counts == EXPECTED_TABLE_COUNTS, f"A10 canonical table census drift: {observed_counts}")
    require(sum(observed_counts.values()) == 512, "A10 canonical aggregate drift")

    for table_name, rows in tables.items():
        for row in rows:
            require(
                row["id"] == projection_id(LANE_NAMESPACE, row["record_type"], row["semantic_key"]),
                f"A10 projected UUID formula drift: {table_name}:{row['semantic_key']}",
            )

    modules = {str(item["module_id"]): item for item in authority["modules"]}
    require(len(modules) == 82, "A10 authority module census drift")
    units = {str(row["payload"]["native_module_id"]): row for row in tables["units"]}
    require(set(units) == set(modules), "A10 projected module identity set drift")
    projected_unit_ids: list[str] = []
    for native_id, module in modules.items():
        row = units[native_id]
        payload = row["payload"]
        expected_id = projection_id(LANE_NAMESPACE, "unit", f"a10:module:{native_id}")
        require(row["id"] == expected_id, f"A10 unit ID drift: {native_id}")
        require(
            payload["ordinal"] == module["ordinal"]
            and payload["label"] == module["label"]
            and payload["title"] == module["title"]
            and payload["chapter_title"] == module["chapter_title"]
            and payload["chapter_start"] == module["chapter_start"],
            f"A10 unit navigation metadata drift: {native_id}",
        )
        require(
            payload["owner_source_path"] == module["owner_source_path"]
            and payload["owner_source_bytes"] == module["bytes"]
            and payload["owner_source_sha256"] == module["sha256"],
            f"A10 unit source binding drift: {native_id}",
        )
        require(
            payload["native_translation_state"] == row["owner_native_state"] == "language_reviewed"
            and row["normalized_state"] == "published",
            f"A10 unit translation state drift: {native_id}",
        )
        require(
            payload["learner_route_state"] == "course_link_only"
            and payload["learner_course_url"] == PUBLIC_PDF
            and payload["unit_url"] is None,
            f"A10 invented or missing learner route: {native_id}",
        )
        require(payload["body_prose_copied"] is False, f"A10 unit copied body prose: {native_id}")
        projected_unit_ids.append(expected_id)

    memberships = {str(row["payload"]["native_module_id"]): row for row in tables["course_unit_memberships"]}
    require(set(memberships) == set(modules), "A10 membership coverage drift")
    bindings = {str(row["payload"]["native_record_id"]): row for row in tables["native_bindings"]}
    require(set(bindings) == set(modules), "A10 native binding coverage drift")
    for native_id, module in modules.items():
        membership = memberships[native_id]["payload"]
        require(
            membership["course_id"] == CURRENT_COURSE_ID
            and membership["unit_id"] == units[native_id]["id"]
            and membership["ordinal"] == module["ordinal"],
            f"A10 membership drift: {native_id}",
        )
        binding = bindings[native_id]["payload"]
        require(
            binding["source_namespace"] == OWNER_NAMESPACE
            and binding["native_sha256"] == module["sha256"]
            and binding["native_bytes"] == module["bytes"]
            and binding["projected_record_id"] == units[native_id]["id"]
            and binding["owner_id_preserved"] is True
            and binding["body_prose_copied"] is False,
            f"A10 native binding drift: {native_id}",
        )

    sequence = [row["payload"] for row in tables["relations"] if row["payload"]["relation_type"] == "precedes_in_release_order"]
    prerequisite = [row["payload"] for row in tables["relations"] if row["payload"]["relation_type"] == "course_prerequisite"]
    require(len(sequence) == 81 and len(prerequisite) == 1, "A10 relation census drift")
    ordered = sorted(authority["modules"], key=lambda item: int(item["ordinal"]))
    expected_pairs = [(str(left["module_id"]), str(right["module_id"])) for left, right in zip(ordered, ordered[1:])]
    observed_pairs = {(row["source_native_module_id"], row["target_native_module_id"]) for row in sequence}
    require(observed_pairs == set(expected_pairs), "A10 release sequence relation drift")
    require(
        prerequisite[0]["source_course_id"] == CURRENT_COURSE_ID
        and prerequisite[0]["target_course_id"] == PREREQUISITE_A00_COURSE_ID,
        "A10 prerequisite course relation drift",
    )

    crosswalks = {str(row["payload"]["source_record_id"]): row for row in tables["identity_crosswalks"]}
    require(set(crosswalks) == set(modules), "A10 table crosswalk coverage drift")
    for native_id, row in crosswalks.items():
        payload = row["payload"]
        require(
            payload["source_namespace"] == OWNER_NAMESPACE
            and payload["source_record_sha256"] == modules[native_id]["sha256"]
            and payload["target_record_id"] == units[native_id]["id"]
            and payload["cardinality"] == "one_to_one",
            f"A10 crosswalk drift: {native_id}",
        )

    search = {str(row["payload"]["native_module_id"]): row for row in tables["search_documents"]}
    require(set(search) == set(modules), "A10 search metadata coverage drift")
    for native_id, row in search.items():
        payload = row["payload"]
        require(
            payload["title"] == modules[native_id]["title"]
            and payload["label"] == modules[native_id]["label"]
            and payload["learner_course_url"] == PUBLIC_PDF
            and payload["unit_url"] is None
            and payload["body_prose_copied"] is False,
            f"A10 search projection drift: {native_id}",
        )

    forbidden: list[str] = []
    for table_name, rows in tables.items():
        forbidden.extend(recursively_forbidden_prose_keys(rows, f"tables/{table_name}.jsonl"))
    require(not forbidden, f"forbidden body-prose fields in A10 adapter: {forbidden[:3]}")

    rights = tables["rights"][0]["payload"]
    require(
        rights["spdx_expression"] == "CC-BY-NC-SA-4.0"
        and rights["component_rights_flattened"] is False
        and rights["native_rights_record_count"] == 4025,
        "A10 qualified rights state drift",
    )
    require(
        len(tables["rights_assignments"]) == 2
        and all(row["payload"]["component_rights_flattened"] is False for row in tables["rights_assignments"]),
        "A10 rights assignment flattening/census drift",
    )

    artifacts = {str(row["payload"]["filename"]): row["payload"] for row in tables["artifacts"]}
    require(set(artifacts) == set(EXPECTED_ARTIFACTS), "A10 projected artifact inventory drift")
    for filename, (size, digest) in EXPECTED_ARTIFACTS.items():
        require(
            artifacts[filename]["bytes"] == size
            and artifacts[filename]["sha256"] == digest
            and artifacts[filename]["external_zero_copy"] is True,
            f"A10 projected artifact fact drift: {filename}",
        )

    surface = tables["reader_surfaces"][0]["payload"]
    route = tables["routes"][0]["payload"]
    require(
        surface["url"] == PUBLIC_PDF
        and surface["pages"] == 1627
        and surface["tagged"] is True
        and surface["course_level_only"] is True
        and surface["per_unit_routes_claimed"] is False
        and surface["machine_data_is_learner_destination"] is False,
        "A10 learner surface drift",
    )
    require(
        route["url"] == PUBLIC_PDF
        and route["route_kind"] == "learner_course_link"
        and route["per_unit_route"] is False
        and route["machine_data_is_learner_destination"] is False,
        "A10 learner course route drift",
    )
    require(not tables["content_bindings"] and not tables["build_recipes"], "A10 unsupported prose/build projections must remain empty")
    reference_closure = validate_reference_closure(tables)
    return {
        "table_counts": observed_counts,
        "canonical_records": 512,
        "module_rows": 82,
        "module_id_set_sha256": identity_set_sha256(modules),
        "projected_unit_id_set_sha256": identity_set_sha256(projected_unit_ids),
        "sequence_relations": 81,
        "per_unit_routes": 0,
        "body_prose_rows": 0,
        "component_rights_flattened": False,
        "reference_closure": reference_closure,
    }


def validate_sidecars(package: Path, tables: Mapping[str, list[dict[str, Any]]], authority: Mapping[str, Any]) -> dict[str, Any]:
    crosswalk = read_json(package / "namespace-crosswalk-v0.2.0.json")
    mappings = crosswalk["mappings"]
    require(len(mappings) == 82, "A10 namespace sidecar mapping census drift")
    native_to_target = {str(row["source_record_id"]): str(row["target_record_id"]) for row in mappings}
    require(len(native_to_target) == 82, "A10 namespace mapping source collision")
    table_units = {str(row["payload"]["native_module_id"]): str(row["id"]) for row in tables["units"]}
    require(native_to_target == table_units, "A10 namespace sidecar/table target drift")
    require(
        crosswalk["identity_sets"]["source_module_id_set_sha256"] == authority["module_projection"]["module_id_set_sha256"]
        and crosswalk["identity_sets"]["projected_unit_id_set_sha256"] == identity_set_sha256(table_units.values())
        and crosswalk["identity_sets"]["mapped_pairs_sha256"] == mapping_set_sha256(table_units.items()),
        "A10 namespace identity-set drift",
    )

    translation = read_json(package / "translation-state-index-v0.2.0.json")
    require(
        translation["coverage"] == {
            "authority_rows": 82,
            "course_id": "A10",
            "granularity": "published_owner_module_snapshot",
            "indexed_rows": 82,
            "inferred_rows": 0,
        },
        "A10 translation coverage drift",
    )
    require(translation["no_inference"] is True and len(translation["records"]) == 82, "A10 translation index drift")
    require(
        all(
            row["owner_native_state"] == "language_reviewed"
            and row["normalized_publication_state"] == "published_complete_release_snapshot"
            and row["state_inferred"] is False
            and row["native_locale"] == "id-ID"
            for row in translation["records"]
        ),
        "A10 translation state inference/state drift",
    )
    require(
        translation["identity_set_sha256"] == identity_set_sha256(row["projected_unit_id"] for row in translation["records"]),
        "A10 translation identity set drift",
    )

    capability = read_json(package / "capability-declarations-v0.2.0.json")
    require([entry["name"] for entry in capability["capabilities"]] == CAPABILITY_NAMES, "A10 capability order drift")
    gap_states = {entry["name"]: entry["loss_gap_report"]["status"] for entry in capability["capabilities"]}
    require(
        gap_states == {
            "structure_localization": "closed",
            "terminology": "declared_limitation",
            "mathematical_preservation": "declared_limitation",
            "assessment_support": "declared_limitation",
            "assets": "declared_limitation",
            "accessibility": "closed",
            "corrections": "declared_limitation",
            "computational_interactives": "declared_limitation",
            "publication": "closed",
            "research_support": "declared_limitation",
        },
        "A10 capability truth table drift",
    )
    require(
        capability["rights_cross_cutting"]["native_count"] == 4025
        and "flatten" in " ".join(capability["rights_cross_cutting"]["closure_rules"]).lower(),
        "A10 rights cross-cutting limitation drift",
    )
    scope = read_json(package / "scope-declaration-v0.2.0.json")
    require(scope["curriculum_role_ids"] == ["A10"] and scope["course_ids"] == [CURRENT_COURSE_ID], "A10 scope drift")
    require(scope["aggregate_conformance_claim"] is False and len(scope["unbound_curriculum_role_ids"]) == 39, "A10 scope closure drift")
    return {
        "namespace_mappings": 82,
        "translation_rows": 82,
        "capability_states": gap_states,
        "scope_role": "A10",
    }


def validate_evidence(package: Path) -> dict[str, Any]:
    evidence = read_json(package / "evidence" / "A10_PUBLIC_RELEASE_CLOSURE.json")
    require(evidence["status"] == "PASS_WITH_EXPLICIT_LIMITATIONS", "A10 evidence status drift")
    require(evidence["release"] == {"coverage": "82/82", "pages": 1627, "record_id": 22236314, "version": "1.0.3"}, "A10 release closure drift")
    require(evidence["native_backend"] == {"copied_records": 0, "records": 561994, "tests_run": 30}, "A10 native backend evidence drift")
    require(evidence["assessment"] == {"exercises": 9406, "granularity": "release_aggregate_only", "missing_solutions": 3300, "problems": 9406, "solutions": 6106}, "A10 assessment aggregate drift")
    require(evidence["terminology_and_corrections"]["ongoing_maintenance_closed"] is False, "A10 maintenance incorrectly closed")
    require(evidence["terminology_and_corrections"]["individual_rows_projected"] == 0, "A10 individual correction/term rows invented")
    require(evidence["rights"]["flattened"] is False and evidence["rights"]["native_rights_records"] == 4025, "A10 evidence rights flattening drift")
    require(evidence["learner_relationship"]["kind"] == "course_link_only" and evidence["learner_relationship"]["per_unit_routes"] == 0, "A10 evidence route drift")
    require(evidence["authority_sha256"] == AUTHORITY_SHA256, "A10 evidence authority hash drift")
    return evidence


def expect_rejected(label: str, action: Callable[[], None]) -> dict[str, Any]:
    try:
        action()
    except AdapterError as exc:
        return {"probe": label, "result": "PASS_REJECTED", "error": str(exc)}
    raise AdapterError(f"negative probe unexpectedly accepted: {label}")


def run_negative_probes(
    tables: Mapping[str, list[dict[str, Any]]],
    authority: Mapping[str, Any],
    evidence: Mapping[str, Any],
    translation: Mapping[str, Any],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    mutated = copy.deepcopy(tables)
    mutated["units"][0]["payload"]["unit_url"] = "https://example.invalid/invented-unit"
    mutated["units"][0]["payload"]["learner_route_state"] = "published_unit_route"
    results.append(expect_rejected("invented_per_unit_route", lambda: validate_table_semantics(mutated, authority)))

    mutated = copy.deepcopy(tables)
    mutated["search_documents"][0]["payload"]["body_text"] = "invented copied prose"
    results.append(expect_rejected("copied_body_prose", lambda: validate_table_semantics(mutated, authority)))

    mutated = copy.deepcopy(tables)
    mutated["rights"][0]["payload"]["component_rights_flattened"] = True
    results.append(expect_rejected("flattened_component_rights", lambda: validate_table_semantics(mutated, authority)))

    mutated_evidence = copy.deepcopy(evidence)
    mutated_evidence["assessment"]["missing_solutions"] = 3299
    def reject_assessment() -> None:
        require(
            mutated_evidence["assessment"]
            == {"exercises": 9406, "granularity": "release_aggregate_only", "missing_solutions": 3300, "problems": 9406, "solutions": 6106},
            "A10 assessment aggregate drift",
        )
    results.append(expect_rejected("fabricated_solution_closure", reject_assessment))

    mutated_translation = copy.deepcopy(translation)
    mutated_translation["records"][0]["state_inferred"] = True
    def reject_translation_inference() -> None:
        require(all(row["state_inferred"] is False for row in mutated_translation["records"]), "A10 inferred translation state")
    results.append(expect_rejected("inferred_translation_state", reject_translation_inference))

    mutated = copy.deepcopy(tables)
    mutated["routes"][0]["payload"]["reader_surface_id"] = "urn:uuid:00000000-0000-4000-8000-000000000000"
    results.append(expect_rejected("orphan_internal_reference", lambda: validate_reference_closure(mutated)))
    return results


def validate_specific(args: argparse.Namespace) -> dict[str, Any]:
    package = args.package.resolve()
    repository_root = args.repository_root.resolve()
    authority_path = repository_root / "backend" / "v2.3" / "authorities" / "A10_ELEMENTARY_ALGEBRA_PUBLIC_RELEASE_AUTHORITY_20260906.json"
    require(authority_path.is_file(), "A10 authority file missing")
    require(authority_path.stat().st_size == AUTHORITY_BYTES and sha256_file(authority_path) == AUTHORITY_SHA256, "A10 authority identity drift")
    authority = read_json(authority_path)

    generic = validate_generic_package(
        SimpleNamespace(
            package=package,
            repository_root=repository_root,
            owner_package_root=None,
            require_authorities=True,
            build_a=args.build_a,
            build_b=args.build_b,
        )
    )
    require(generic["status"] == "PASS", "generic v2.3.1 validation did not pass")
    require(generic["extension_version"] == "0.1.0", "unexpected A10 adapter version")
    require(generic["sidecars"]["scope_roles"] == ["A10"], "generic adapter scope is not exactly A10")

    tables = load_tables(package)
    table_report = validate_table_semantics(tables, authority)
    sidecar_report = validate_sidecars(package, tables, authority)
    evidence = validate_evidence(package)
    authorities = read_json(package / "INPUT_AUTHORITIES.json")
    closure = authorities["public_release_closure"]
    require(
        closure["module_count"] == 82
        and closure["owner_native_records"] == 561994
        and closure["backend_tests"] == 30
        and closure["module_id_set_sha256"] == authority["module_projection"]["module_id_set_sha256"]
        and closure["module_sequence_sha256"] == authority["module_projection"]["module_sequence_sha256"],
        "A10 input authority closure drift",
    )
    require(
        authorities["body_prose_copied"] is False
        and authorities["native_backend_history_copied"] is False
        and authorities["owner_native_non_mutation"] is True,
        "A10 zero-copy authority drift",
    )
    translation = read_json(package / "translation-state-index-v0.2.0.json")
    negative = run_negative_probes(tables, authority, evidence, translation) if args.negative_probes else []
    return {
        "schema_id": "program-matematika-indonesia/a10-v2.3.1-adapter-validation/1",
        "status": "PASS",
        "generic_validation": generic,
        "authority": {"path": AUTHORITY_RELATIVE, "bytes": AUTHORITY_BYTES, "sha256": AUTHORITY_SHA256},
        "adapter": table_report,
        "sidecars": sidecar_report,
        "release_snapshot": {
            "record_id": 22236314,
            "version": "1.0.3",
            "modules": 82,
            "native_records": 561994,
            "exercises": 9406,
            "solutions": 6106,
            "missing_solutions": 3300,
            "reader_pages": 1627,
            "learner_route": PUBLIC_PDF,
        },
        "negative_probes": negative,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--build-a", type=Path)
    parser.add_argument("--build-b", type=Path)
    parser.add_argument("--negative-probes", action="store_true")
    parser.add_argument("--report", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = validate_specific(args)
        if args.report:
            write_json(args.report, report)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
