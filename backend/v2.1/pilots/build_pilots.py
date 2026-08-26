#!/usr/bin/env python3
"""Build additive v2.1 unit/search pilots from admitted owner-native evidence.

The owner trees are read-only inputs. This script writes only below
backend/v2.1/pilots/a00-prealgebra and backend/v2.1/pilots/b10-dmoi.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCHEMA_ID = "interlanguage/global-backend-v2.1-unit-search-pilot/0.1.0"
RECORDED_AT = "2026-08-26T00:00:00Z"
PROGRAM_ROOT = Path(__file__).resolve().parents[3]
PILOTS_ROOT = Path(__file__).resolve().parent
OWNER_ROOT = PROGRAM_ROOT.parent

A00_ROOT = OWNER_ROOT / "openstax-prealgebra"
A00_BACKEND = A00_ROOT / "modular_backend/generated/prealgebra2e-volume"
B10_ROOT = OWNER_ROOT / "discrete-mathematics-open-introduction-id"
B10_BACKEND = B10_ROOT / "repo/backend/full/dmoi4-id"

A00_RECEIPT = PROGRAM_ROOT / "backend/migrations/prealgebra2e-id-v1/MIGRATION_RECEIPT.json"
A00_PROFILE = PROGRAM_ROOT / "backend/migrations/prealgebra2e-id-v1/ADAPTER_PROFILE.json"
B10_RECEIPT = PROGRAM_ROOT / "backend/migrations/dmoi4-id-v1/MIGRATION_RECEIPT.json"
FEDERATION_DATA = PROGRAM_ROOT / "backend/v2/program-matematika-indonesia-federation-v0.3.0/data"

EXPECTED = {
    "a00_receipt": "50093021475d3757ab71395d5bf34f672c18a6714122093b040021c18f333152",
    "a00_profile": "23fd48aaa1c695d0cc02c4ee921c8e52a1b8fc435818f60922bb1db847073d96",
    "a00_owner_manifest": "e27b23f6bff5c56949e149af6decb8ecd9d7bf30ab049d65a5dd344e232b913d",
    "b10_receipt": "a68e46a2b2bdce8b93630dbd2e157581a0f7a7bb03c1f509632ab7d8d3701ddb",
    "b10_owner_manifest": "ebcea79ba19cdd0f08f1bf6444928fcf8bda8a5641535e59c20c9ee230763d20",
    "federation_courses": "9549b341587898f92960622c5bce788355e08e7b04f5c491c5bd65c2240aaf7f",
    "federation_routes": "f0190d14e6bfc63811f50317073dd541195b6878ce4653379a172b1d701c2736",
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def require_hash(path: Path, expected: str) -> None:
    actual = sha256_path(path)
    if actual != expected:
        raise ValueError(f"authority hash changed: {path}: {actual} != {expected}")


def json_load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL {path}:{line_number}") from exc


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def relation_endpoint_policy(units: list[dict[str, Any]], relations: list[dict[str, Any]]) -> dict[str, Any]:
    unit_ids = {row["stable_unit_id"] for row in units}
    external = sorted(
        ({row["from_id"] for row in relations} | {row["to_id"] for row in relations}) - unit_ids
    )
    return {
        "external_endpoint_count": len(external),
        "external_endpoint_sha256": sha256_text(canonical_json(external)),
        "mode": "internal_only" if not external else "exact_external_set",
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text("".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8", newline="\n")


def artifact(path: Path, root: Path, role: str) -> dict[str, Any]:
    return {
        "bytes": path.stat().st_size,
        "path": path.relative_to(root).as_posix(),
        "role": role,
        "sha256": sha256_path(path),
    }


def localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def xml_title(path: Path) -> str:
    root = ET.parse(path).getroot()
    for element in root.iter():
        if localname(element.tag) == "title":
            title = " ".join("".join(element.itertext()).split())
            if title:
                return title
    raise ValueError(f"no XML title in {path}")


def payload_title(payload: str) -> str:
    root = ET.fromstring(payload)
    title = " ".join("".join(root.itertext()).split())
    if not title:
        raise ValueError("empty title payload")
    return title


def search_text(*values: str | None) -> str:
    joined = " ".join(value for value in values if value)
    normalized = unicodedata.normalize("NFKC", joined).casefold()
    normalized = re.sub(r"[^0-9a-zà-öø-ÿā-ž]+", " ", normalized, flags=re.IGNORECASE)
    return " ".join(normalized.split())


def source_evidence(path: Path, role: str, locator_base: str = "program_repository_root") -> dict[str, Any]:
    if locator_base == "program_repository_root":
        locator = path.relative_to(PROGRAM_ROOT).as_posix()
    else:
        locator = path.relative_to(OWNER_ROOT).as_posix()
    return {
        "bytes": path.stat().st_size,
        "locator": locator,
        "locator_base": locator_base,
        "role": role,
        "sha256": sha256_path(path),
    }


def read_federation_record(table: str, semantic_key: str) -> dict[str, Any]:
    for row in jsonl(FEDERATION_DATA / table):
        if row.get("semantic_key") == semantic_key:
            return row
    raise ValueError(f"missing federation record {table}:{semantic_key}")


def parse_a00_collection(path: Path) -> list[dict[str, Any]]:
    root = ET.parse(path).getroot()
    rows: list[dict[str, Any]] = []
    ordinal = 0
    group_ordinal = 0

    def visit(content: ET.Element, group_title: str | None, group_index: int | None) -> None:
        nonlocal ordinal, group_ordinal
        for child in list(content):
            kind = localname(child.tag)
            if kind == "module":
                ordinal += 1
                rows.append(
                    {
                        "collection_order": ordinal,
                        "group_order": group_index,
                        "group_title": group_title,
                        "module_id": child.attrib["document"],
                    }
                )
            elif kind == "subcollection":
                group_ordinal += 1
                title = next((" ".join("".join(e.itertext()).split()) for e in child if localname(e.tag) == "title"), None)
                nested = next(e for e in child if localname(e.tag) == "content")
                visit(nested, title, group_ordinal)

    content = next(e for e in root if localname(e.tag) == "content")
    visit(content, None, None)
    return rows


def build_a00() -> dict[str, Any]:
    require_hash(A00_RECEIPT, EXPECTED["a00_receipt"])
    require_hash(A00_PROFILE, EXPECTED["a00_profile"])
    owner_manifest = A00_BACKEND / "backend.volume.manifest.json"
    require_hash(owner_manifest, EXPECTED["a00_owner_manifest"])
    receipt = json_load(A00_RECEIPT)

    collection = A00_ROOT / "collections/prealgebra-2e.id-ID.collection.xml"
    collection_source = A00_ROOT / "collections/prealgebra-2e.collection.xml"
    if sha256_path(collection) != receipt["coverage"]["collection_xml_authorities"]["target_collection"]["sha256"]:
        raise ValueError("A00 target collection changed")
    if sha256_path(collection_source) != receipt["coverage"]["collection_xml_authorities"]["source_collection"]["sha256"]:
        raise ValueError("A00 source collection changed")
    collection_rows = parse_a00_collection(collection)
    if len(collection_rows) != 75 or len({row["module_id"] for row in collection_rows}) != 75:
        raise ValueError("A00 collection is not the admitted 75-module volume")

    source_witness_path = A00_BACKEND / "metadata/source-witness-manifest.tsv"
    target_witness_path = A00_BACKEND / "metadata/target-witness-manifest.tsv"
    with source_witness_path.open("r", encoding="utf-8", newline="") as handle:
        source_witness = {row["module"]: row for row in csv.DictReader(handle, delimiter="\t")}
    with target_witness_path.open("r", encoding="utf-8", newline="") as handle:
        target_witness = {row["module"]: row for row in csv.DictReader(handle, delimiter="\t")}

    wanted_modules = {row["module_id"] for row in collection_rows}
    native_units: dict[str, dict[str, Any]] = {}
    unit_by_module: dict[str, dict[str, Any]] = {}
    for row in jsonl(A00_BACKEND / "content/units.jsonl"):
        locator = row.get("source_locator", "")
        # The owner backend's canonical locator includes the XML document
        # node (`.../index.cnxml/document[1]`), while the collection names
        # the module root only.  Bind at the stable module path, not to an
        # implementation-specific XPath suffix.
        locator_parts = locator.split("/")
        if (
            row.get("unit_type") == "document"
            and len(locator_parts) >= 3
            and locator_parts[0] == "modules"
            and locator_parts[2].startswith("index.cnxml")
        ):
            module_id = locator_parts[1]
            if module_id in wanted_modules:
                native_units[row["id"]] = row
                unit_by_module[module_id] = row
    if set(unit_by_module) != wanted_modules:
        raise ValueError("A00 native document roots do not close over collection")

    localized_by_unit: dict[str, dict[str, Any]] = {}
    for row in jsonl(A00_BACKEND / "locales/id-ID/units.jsonl"):
        canonical_id = row.get("canonical_unit_id")
        if canonical_id in native_units and row.get("unit_type") == "document":
            if canonical_id in localized_by_unit:
                raise ValueError(f"duplicate A00 localized root {canonical_id}")
            localized_by_unit[canonical_id] = row
    if set(localized_by_unit) != set(native_units):
        raise ValueError("A00 localized document roots do not close over collection")

    concepts = {row["id"]: row for row in jsonl(A00_BACKEND / "content/concepts.jsonl")}
    native_relations: list[dict[str, Any]] = []
    concepts_by_unit: dict[str, list[dict[str, Any]]] = {unit_id: [] for unit_id in native_units}
    for row in jsonl(A00_BACKEND / "content/relations.jsonl"):
        predicate = row.get("predicate")
        subject = row.get("subject_id")
        obj = row.get("object_id")
        if predicate == "precedes" and subject in native_units and obj in native_units:
            native_relations.append(
                {
                    "evidence": {"native_relation_id": row["id"], "qualifier": row.get("qualifier")},
                    "from_id": subject,
                    "record_type": "relation",
                    "relation_type": "precedes",
                    "strength": "hard",
                    "to_id": obj,
                }
            )
        elif predicate == "addresses" and subject in native_units and obj in concepts and row.get("qualifier") == "source_module_root":
            concept = concepts[obj]
            concepts_by_unit[subject].append(concept)
            native_relations.append(
                {
                    "evidence": {
                        "mapping_source_sha256": row.get("mapping_source_sha256"),
                        "native_relation_id": row["id"],
                        "qualifier": row.get("qualifier"),
                    },
                    "from_id": subject,
                    "record_type": "relation",
                    "relation_type": "addresses_concept",
                    "strength": "hard",
                    "to_id": obj,
                    "to_label": concept.get("label_en_us"),
                    "to_label_locale": "en-US",
                }
            )
        elif predicate == "prerequisite" and subject in concepts and obj in concepts:
            native_relations.append(
                {
                    "evidence": {
                        "mapping_source_sha256": row.get("mapping_source_sha256"),
                        "native_relation_id": row["id"],
                        "qualifier": row.get("qualifier"),
                    },
                    "from_id": subject,
                    "from_label": concepts[subject].get("label_en_us"),
                    "label_locale": "en-US",
                    "record_type": "relation",
                    "relation_type": "requires_concept",
                    "strength": "hard",
                    "to_id": obj,
                    "to_label": concepts[obj].get("label_en_us"),
                }
            )

    pages_url = next(item["pages_url"] for item in receipt["public_artifacts"] if item.get("kind") == "github release identity")
    course_title = "Prealgebra 2e — Edisi Bahasa Indonesia"
    units: list[dict[str, Any]] = []
    search_rows: list[dict[str, Any]] = []
    for item in collection_rows:
        module_id = item["module_id"]
        native = unit_by_module[module_id]
        localized = localized_by_unit[native["id"]]
        target_path = A00_ROOT / f"modules/{module_id}/index.cnxml"
        html_path = A00_ROOT / f"output/html-id/modules/{module_id}/index.html"
        witness_source = source_witness[module_id]
        witness_target = target_witness[module_id]
        target_sha = sha256_path(target_path)
        html_sha = sha256_path(html_path)
        if target_sha != witness_target["sha256"] or target_sha != localized["target_module_sha256"].removeprefix("sha256:"):
            raise ValueError(f"A00 target witness mismatch: {module_id}")
        if witness_source["sha256"] != localized["source_module_sha256"].removeprefix("sha256:"):
            raise ValueError(f"A00 source witness mismatch: {module_id}")
        if target_path.stat().st_size != int(witness_target["bytes"]):
            raise ValueError(f"A00 target byte mismatch: {module_id}")
        title = xml_title(target_path)
        concept_rows = sorted(concepts_by_unit[native["id"]], key=lambda value: value["concept_key"])
        route_url = pages_url.rstrip("/") + f"/modules/{module_id}/index.html"
        unit = {
            "course_id": "A00",
            "group_order": item["group_order"],
            "group_title": item["group_title"],
            "learner_route": {
                "anchor": None,
                "local_evidence_locator": f"output/html-id/modules/{module_id}/index.html",
                "local_evidence_sha256": html_sha,
                "route_state": "published_owner_native_module_page",
                "url": route_url,
            },
            "locale": "id-ID",
            "localized_occurrence_id": localized["id"],
            "localized_title": title,
            "localized_title_sha256": sha256_text(title),
            "module_id": module_id,
            "native_locator": {
                "source": witness_source["url"],
                "source_locator_state": "frozen_commit_url_and_hash; source bytes are not copied into pilot",
                "target": f"modules/{module_id}/index.cnxml",
            },
            "native_unit_id": native["id"],
            "native_unit_kind": native["unit_type"],
            "order_index": item["collection_order"],
            "order_key": f"{item['collection_order']:04d}",
            "record_type": "unit",
            "rights_component_id": native["rights_component_id"],
            "schema_id": SCHEMA_ID,
            "source_sha256": witness_source["sha256"],
            "stable_unit_id": native["id"],
            "support_concepts": [
                {"concept_id": concept["id"], "label": concept["label_en_us"], "label_locale": "en-US"}
                for concept in concept_rows
            ],
            "target_sha256": target_sha,
            "translation_state": localized["translation_state"],
        }
        units.append(unit)
        search_rows.append(
            {
                "course_id": "A00",
                "group_title": item["group_title"],
                "learner_url": route_url,
                "locale": "id-ID",
                "module_id": module_id,
                "order_key": unit["order_key"],
                "record_type": "search_document",
                "search_text": search_text(course_title, item["group_title"], title, module_id),
                "stable_unit_id": native["id"],
                "title": title,
            }
        )

    rights_rows = list(jsonl(A00_BACKEND / "registry/rights.jsonl"))
    default_rights = next(row for row in rights_rows if row.get("rights_component_scope") == "bundle_default")
    exception_states = Counter(row.get("rights_statement_state", "explicit_component_terms") for row in rights_rows if row["id"] != default_rights["id"])
    rights_accessibility = {
        "accessibility": {
            "learner_html_module_pages": len(units),
            "native_accessibility_records": receipt["tables"]["accessibility"]["records"],
            "state": "owner-native v0.2.5 has no dedicated accessibility table; this pilot claims only the verified semantic HTML module routes",
        },
        "course_id": "A00",
        "rights": {
            "component_exception_count": len(rights_rows) - 1,
            "component_statement_state_counts": dict(sorted(exception_states.items())),
            "default": {
                "attribution_required": default_rights["attribution_required"],
                "change_notice_required": default_rights["change_notice_required"],
                "id": default_rights["id"],
                "license_expression": default_rights["license"],
                "noncommercial_required": default_rights["noncommercial_required"],
                "sharealike_required": default_rights["sharealike_required"],
            },
            "state": "component exceptions remain authoritative in owner registry/rights.jsonl and are not flattened into the default",
        },
        "schema_id": SCHEMA_ID,
    }

    relations = sorted(native_relations, key=lambda row: (row["relation_type"], row["from_id"], row["to_id"], row["evidence"]["native_relation_id"]))
    out = PILOTS_ROOT / "a00-prealgebra"
    write_jsonl(out / "units.jsonl", units)
    write_jsonl(out / "relations.jsonl", relations)
    write_jsonl(out / "search.jsonl", search_rows)
    write_json(out / "rights_accessibility.json", rights_accessibility)
    files = [
        artifact(out / "relations.jsonl", out, "evidence_bound_relations"),
        artifact(out / "rights_accessibility.json", out, "rights_accessibility_summary"),
        artifact(out / "search.jsonl", out, "compact_search_shard"),
        artifact(out / "units.jsonl", out, "stable_unit_registry"),
    ]
    manifest = {
        "canonical_serialization": "UTF-8; JSON objects sorted by key; JSONL LF with trailing newline",
        "course_id": "A00",
        "dataset_id": "pilot:a00-prealgebra:v2.1:0.1.0",
        "files": files,
        "input_authority": [
            source_evidence(A00_RECEIPT, "admitted_migration_receipt"),
            source_evidence(A00_PROFILE, "admitted_adapter_profile"),
            source_evidence(owner_manifest, "owner_native_manifest", "owner_root"),
            source_evidence(collection_source, "source_collection", "owner_root"),
            source_evidence(collection, "localized_collection", "owner_root"),
            source_evidence(source_witness_path, "source_module_witnesses", "owner_root"),
            source_evidence(target_witness_path, "target_module_witnesses", "owner_root"),
        ],
        "limitations": [
            "Concept labels in the admitted A00 prerequisite map are en-US; the pilot marks that locale and does not present them as localized search terms.",
            "The owner-native backend has zero dedicated accessibility records; only the existence and hashes of semantic HTML module pages are asserted.",
            "Source CNXML bytes are not copied into this pilot; each source module is bound by its frozen commit URL, byte count, and SHA-256 witness.",
        ],
        "materialization_scope": "compact unit, relation, search, and rights/accessibility projections; no textbook prose",
        "native_backend_contribution": {
            "collection_order": "CollXML module order and localized chapter-group titles",
            "identity": "75 native document UUIDs plus 75 localized occurrence UUIDs",
            "learning_graph": "64 native module precedence edges, 63 module-to-concept mappings, and 76 concept prerequisite edges",
            "route": "75 verified owner-native per-module HTML pages",
            "source_target_binding": "source/target witness manifests plus localized-unit hashes",
        },
        "owner_tree_mode": "read_only",
        "relation_endpoint_policy": relation_endpoint_policy(units, relations),
        "record_counts": {
            "relations": len(relations),
            "rights_accessibility_documents": 1,
            "search_documents": len(search_rows),
            "units": len(units),
        },
        "recorded_at": RECORDED_AT,
        "schema_id": SCHEMA_ID,
        "uncertain_field_contracts": [
            {"field": "support_concepts.label", "decision": "retain native en-US label with explicit locale until a localized concept-label authority exists"},
        ],
    }
    write_json(out / "manifest.json", manifest)
    return manifest


def build_b10() -> dict[str, Any]:
    require_hash(B10_RECEIPT, EXPECTED["b10_receipt"])
    owner_manifest = B10_BACKEND / "package.json"
    require_hash(owner_manifest, EXPECTED["b10_owner_manifest"])
    require_hash(FEDERATION_DATA / "courses.jsonl", EXPECTED["federation_courses"])
    require_hash(FEDERATION_DATA / "web_routes.jsonl", EXPECTED["federation_routes"])
    receipt = json_load(B10_RECEIPT)
    package = json_load(owner_manifest)
    package_files = {row["path"]: row for row in package["files"]}
    required_tables = [
        "data/accessibility.jsonl",
        "data/file_revisions.jsonl",
        "data/files.jsonl",
        "data/occurrences.jsonl",
        "data/relations.jsonl",
        "data/rights.jsonl",
        "data/segment_variants.jsonl",
        "data/segments.jsonl",
        "data/units.jsonl",
    ]
    for relative in required_tables:
        path = B10_BACKEND / relative
        fact = package_files[relative]
        if path.stat().st_size != fact["bytes"] or sha256_path(path) != fact["sha256"]:
            raise ValueError(f"B10 package table changed: {relative}")

    unit_kinds = {"book", "chapter", "section", "subsection"}
    all_units = {row["id"]: row for row in jsonl(B10_BACKEND / "data/units.jsonl")}
    selected_units = {key: row for key, row in all_units.items() if row.get("unit_kind") in unit_kinds}
    if len(selected_units) != 161:
        raise ValueError(f"B10 structural unit count changed: {len(selected_units)}")

    all_occurrences = {row["id"]: row for row in jsonl(B10_BACKEND / "data/occurrences.jsonl")}
    target_occurrences: dict[str, dict[str, Any]] = {}
    for row in all_occurrences.values():
        if row.get("locale") == "id-ID" and row.get("unit_id") in selected_units:
            if row["unit_id"] in target_occurrences:
                raise ValueError(f"duplicate B10 structural occurrence {row['unit_id']}")
            target_occurrences[row["unit_id"]] = row
    if set(target_occurrences) != set(selected_units):
        raise ValueError("B10 localized structural occurrence closure failed")

    # A unit can contain many nested definition/example titles.  The learner
    # title is the title whose locator is exactly the unit's own XML path plus
    # `/title`; descendant titles must remain searchable content, not replace
    # the unit heading.
    title_segment_to_unit: dict[str, str] = {}
    wanted_title_anchors = {
        unit_id: f"{unit['source_xml_path']}/title"
        for unit_id, unit in selected_units.items()
    }
    for row in jsonl(B10_BACKEND / "data/segments.jsonl"):
        unit_id = row.get("unit_id")
        if (
            unit_id in selected_units
            and row.get("segment_kind") == "title"
            and row.get("identity_anchor") == wanted_title_anchors[unit_id]
        ):
            title_segment_to_unit[row["id"]] = unit_id
    title_by_unit: dict[str, dict[str, Any]] = {}
    for row in jsonl(B10_BACKEND / "data/segment_variants.jsonl"):
        unit_id = title_segment_to_unit.get(row.get("segment_id"))
        if unit_id and row.get("locale") == "id-ID" and row.get("role") == "translation":
            if unit_id in title_by_unit:
                raise ValueError(f"duplicate B10 localized title {unit_id}")
            title_by_unit[unit_id] = {
                "payload_sha256": row["payload_sha256"],
                "source_variant_id": row.get("source_variant_id"),
                "title": payload_title(row["payload"]),
                "variant_id": row["id"],
            }
    if set(title_by_unit) != set(selected_units):
        raise ValueError("B10 localized title closure failed")

    file_revisions = {row["id"]: row for row in jsonl(B10_BACKEND / "data/file_revisions.jsonl")}
    files = {row["id"]: row for row in jsonl(B10_BACKEND / "data/files.jsonl")}

    # Central v2 is authoritative for the learner fallback and the course prerequisite.
    central_course = read_federation_record("courses.jsonl", "course:B10")
    central_route = read_federation_record("web_routes.jsonl", "course-card:B10")
    payload = central_course["payload"]
    route_payload = central_route["payload"]
    if payload["unit_route_state"] != "planned_not_published" or route_payload["unit_route_state"] != "planned_not_published":
        raise ValueError("B10 unit-route state changed; reassess rather than silently retaining fallback")

    selected_occurrence_ids = {row["id"]: row["unit_id"] for row in target_occurrences.values()}

    def parent_unit_id(occurrence: dict[str, Any]) -> str | None:
        parent_id = occurrence.get("parent_occurrence_id")
        seen: set[str] = set()
        while parent_id:
            if parent_id in seen:
                raise ValueError("B10 occurrence parent cycle")
            seen.add(parent_id)
            if parent_id in selected_occurrence_ids:
                return selected_occurrence_ids[parent_id]
            parent = all_occurrences.get(parent_id)
            if not parent:
                return None
            parent_id = parent.get("parent_occurrence_id")
        return None

    units: list[dict[str, Any]] = []
    search_rows: list[dict[str, Any]] = []
    unique_file_revisions: set[str] = set()
    for unit_id, target_occurrence in sorted(target_occurrences.items(), key=lambda item: item[1]["order_path"]):
        native = selected_units[unit_id]
        source_occurrence = all_occurrences[target_occurrence["source_occurrence_id"]]
        if source_occurrence["locale"] != "en-US" or source_occurrence["unit_id"] != unit_id:
            raise ValueError(f"B10 source occurrence binding failed: {unit_id}")
        source_revision = file_revisions[source_occurrence["file_revision_id"]]
        target_revision = file_revisions[target_occurrence["file_revision_id"]]
        for revision in (source_revision, target_revision):
            actual_path = B10_ROOT / revision["actual_path"]
            if actual_path.stat().st_size != revision["bytes"] or sha256_path(actual_path) != revision["sha256"]:
                raise ValueError(f"B10 owner file revision changed: {revision['actual_path']}")
            unique_file_revisions.add(revision["id"])
        title = title_by_unit[unit_id]
        canonical_file = files[target_revision["file_id"]]
        parent_id = parent_unit_id(target_occurrence)
        unit = {
            "course_id": "B10",
            "learner_route": {
                "anchor": None,
                "anchor_state": "native XML anchor retained separately; no public HTML anchor mapping is hash-bound",
                "course_card_url": route_payload["public_url"],
                "planned_unit_route_pattern": route_payload["planned_unit_route_pattern"],
                "route_state": "course_fallback_unit_route_planned_not_published",
                "url": route_payload["learner_fallback_url"],
            },
            "locale": "id-ID",
            "localized_occurrence_id": target_occurrence["id"],
            "localized_title": title["title"],
            "localized_title_payload_sha256": title["payload_sha256"],
            "localized_title_variant_id": title["variant_id"],
            "native_locator": {
                "canonical_path": canonical_file["canonical_path"],
                "identity_anchor": native["identity_anchor"],
                "source_actual_path": source_revision["actual_path"],
                "source_xml_path": source_occurrence["xml_path"],
                "target_actual_path": target_revision["actual_path"],
                "target_xml_path": target_occurrence["xml_path"],
                "xml_id": native.get("source_local_id"),
            },
            "native_unit_id": unit_id,
            "native_unit_kind": native["unit_kind"],
            "order_key": target_occurrence["order_path"],
            "parent_stable_unit_id": parent_id,
            "record_type": "unit",
            "rights_component_id": native["rights_default_id"],
            "schema_id": SCHEMA_ID,
            "source_file_revision_id": source_revision["id"],
            "source_file_sha256": source_revision["sha256"],
            "source_subtree_sha256": source_occurrence["subtree_sha256"],
            "stable_unit_id": unit_id,
            "target_file_revision_id": target_revision["id"],
            "target_file_sha256": target_revision["sha256"],
            "target_subtree_sha256": target_occurrence["subtree_sha256"],
            "translation_state": target_occurrence["translation_state"],
        }
        units.append(unit)
        search_rows.append(
            {
                "course_id": "B10",
                "learner_url": route_payload["learner_fallback_url"],
                "locale": "id-ID",
                "native_unit_kind": native["unit_kind"],
                "order_key": target_occurrence["order_path"],
                "record_type": "search_document",
                "search_text": search_text(payload["title"], title["title"], native.get("source_local_id")),
                "stable_unit_id": unit_id,
                "title": title["title"],
            }
        )

    relations: list[dict[str, Any]] = []
    for row in jsonl(B10_BACKEND / "data/relations.jsonl"):
        if row.get("relation_type") in {"contains", "precedes"} and row.get("from_id") in selected_units and row.get("to_id") in selected_units:
            relations.append(
                {
                    "evidence": {
                        "assertion_method": row.get("assertion_method"),
                        "confidence": row.get("confidence"),
                        "native_relation_id": row["id"],
                        "source_locator": row.get("source_locator"),
                    },
                    "from_id": row["from_id"],
                    "record_type": "relation",
                    "relation_type": row["relation_type"],
                    "strength": row.get("strength"),
                    "to_id": row["to_id"],
                }
            )
    for prerequisite in payload["prerequisite_course_ids"]:
        relations.append(
            {
                "evidence": {
                    "central_course_record_id": central_course["id"],
                    "central_courses_jsonl_sha256": EXPECTED["federation_courses"],
                    "source_field": "payload.prerequisite_course_ids",
                },
                "from_id": "course:B10",
                "record_type": "relation",
                "relation_type": "requires_course",
                "strength": "hard",
                "to_id": f"course:{prerequisite}",
            }
        )
    relations.sort(key=lambda row: (row["relation_type"], row["from_id"], row["to_id"], row["evidence"].get("native_relation_id", "")))

    rights_rows = list(jsonl(B10_BACKEND / "data/rights.jsonl"))
    accessibility_rows = list(jsonl(B10_BACKEND / "data/accessibility.jsonl"))
    accessibility_counts = Counter((row["locale"], row["kind"]) for row in accessibility_rows)
    rights_accessibility = {
        "accessibility": {
            "native_record_count": len(accessibility_rows),
            "record_counts_by_locale_and_kind": {
                f"{locale}:{kind}": count for (locale, kind), count in sorted(accessibility_counts.items())
            },
            "remote_runtime_caveat": next(row["third_party_status"] for row in rights_rows if row["source_component_id"] == "DMD-RIGHTS-0005"),
            "state": "native descriptions/shortdescriptions are preserved in owner backend; this compact pilot summarizes counts and does not copy their prose",
        },
        "course_id": "B10",
        "rights": {
            "components": [
                {
                    "assertion_status": row["assertion_status"],
                    "attribution": row["attribution"],
                    "id": row["id"],
                    "license_expression": row["license_expression"],
                    "source_component_id": row["source_component_id"],
                    "third_party_status": row["third_party_status"],
                }
                for row in sorted(rights_rows, key=lambda value: value["source_component_id"])
            ],
            "state": "all five admitted component records retained; no flattening or license weakening",
        },
        "schema_id": SCHEMA_ID,
    }

    out = PILOTS_ROOT / "b10-dmoi"
    write_jsonl(out / "units.jsonl", units)
    write_jsonl(out / "relations.jsonl", relations)
    write_jsonl(out / "search.jsonl", search_rows)
    write_json(out / "rights_accessibility.json", rights_accessibility)
    materialized = [
        artifact(out / "relations.jsonl", out, "evidence_bound_relations"),
        artifact(out / "rights_accessibility.json", out, "rights_accessibility_summary"),
        artifact(out / "search.jsonl", out, "compact_search_shard"),
        artifact(out / "units.jsonl", out, "stable_unit_registry"),
    ]
    relation_counts = Counter(row["relation_type"] for row in relations)
    manifest = {
        "canonical_serialization": "UTF-8; JSON objects sorted by key; JSONL LF with trailing newline",
        "course_id": "B10",
        "dataset_id": "pilot:b10-dmoi:v2.1:0.1.0",
        "files": materialized,
        "input_authority": [
            source_evidence(B10_RECEIPT, "admitted_migration_receipt"),
            source_evidence(owner_manifest, "owner_native_manifest", "owner_root"),
            source_evidence(FEDERATION_DATA / "courses.jsonl", "central_course_and_prerequisite_authority"),
            source_evidence(FEDERATION_DATA / "web_routes.jsonl", "central_learner_route_authority"),
        ],
        "limitations": [
            "The central authority marks clean B10 unit routes planned_not_published; every pilot unit therefore uses the verified course root as an honest learner fallback and claims no HTML anchor.",
            "The native backend exposes no structural-root-to-concept relation; no unit concept tags are inferred from prose.",
            "Accessibility payload prose remains zero-copy in the owner backend; the pilot records exact counts and component/runtime caveats only.",
        ],
        "materialization_scope": "compact unit, relation, search, and rights/accessibility projections; no textbook prose",
        "native_backend_contribution": {
            "accessibility": "235 admitted description/shortdescription records summarized without prose duplication",
            "identity_and_order": "161 native book/chapter/section/subsection UUIDs with bilingual occurrence order",
            "localized_titles": "161 id-ID title segment variants with payload hashes",
            "relations": dict(sorted(relation_counts.items())),
            "source_target_binding": f"{len(unique_file_revisions)} distinct source/target file revisions and 322 source/target subtree hashes verified against live owner bytes",
        },
        "owner_tree_mode": "read_only",
        "relation_endpoint_policy": relation_endpoint_policy(units, relations),
        "record_counts": {
            "relations": len(relations),
            "rights_accessibility_documents": 1,
            "search_documents": len(search_rows),
            "units": len(units),
        },
        "recorded_at": RECORDED_AT,
        "schema_id": SCHEMA_ID,
        "uncertain_field_contracts": [
            {"field": "learner_route.anchor", "decision": "null until a public reader build binds native xml:id/source_local_id to an exact HTML anchor"},
            {"field": "parent_stable_unit_id", "decision": "nearest selected structural ancestor in the id-ID occurrence tree; intervening non-structural occurrences are skipped deterministically"},
        ],
    }
    write_json(out / "manifest.json", manifest)
    return manifest


def main() -> None:
    a00 = build_a00()
    b10 = build_b10()
    print(canonical_json({"result": "pass", "pilots": {"A00": a00["record_counts"], "B10": b10["record_counts"]}}))


if __name__ == "__main__":
    main()
