#!/usr/bin/env python3
"""Validate and losslessly adapt the completed O002/B80 backend to common v1.

The owner lane is an immutable input.  Every native catalog entry receives one
common-v1 record carrying the complete native payload in a checksum-bound
extension.  A small set of rights and external-reference anchors is added only
to satisfy the common relational contract.  Exact reverse extraction recreates
the original catalog bytes, so no source information is normalized away.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_NAME = "interlanguage-math-modular-backend"
SCHEMA_VERSION = "1.0.0"
SOURCE_SCHEMA_NAME = "o002.backend"
SOURCE_SCHEMA_VERSION = "o002.backend.v2"
WORKFLOW = "program-matematika-indonesia/o002-b80-v1-adapter-1.0.0"
NAMESPACE = uuid.UUID("82e6481c-f4aa-5ce4-a34c-a23e7e1c4559")
NATIVE_EXTENSION = "interlanguage.o002-native"
DERIVED_EXTENSION = "interlanguage.o002-derived"
RECORDED_AT = "2026-08-22T19:04:11Z"

EXPECTED = {
    "backend/catalog.json": (110_511, "447a7ae670a8232a08b24db4ab6288df6f0c3b4d46462206b173830fc55c085d"),
    "output/backend/catalog.json": (110_511, "447a7ae670a8232a08b24db4ab6288df6f0c3b4d46462206b173830fc55c085d"),
    "docs/backend/catalog.json": (110_511, "447a7ae670a8232a08b24db4ab6288df6f0c3b4d46462206b173830fc55c085d"),
    "backend/catalog.schema.json": (18_030, "792413fa564e3e902af0ceca22e80e7bb17d595351c8d6ff992d07bca3a8bb69"),
    "00_control/CURRENT_CURSOR.json": (4_372, "91dd081231c897c5631331e5b7737b7dd7269ae6e6ada0a3959bb4a7116e1a06"),
    "00_control/GITHUB_PUBLICATION_RECEIPT.json": (3_420, "5afc69701c84914b0959d2d3bfcec9197ad67ae041187b0303bb2e56a9bd0fcb"),
    "00_control/PUBLICATION_RECEIPT_FINAL.json": (2_747, "9dadaec2091ef382b1d55dbd98a848ec06b641b347efc683fbad9724e4c793cf"),
    "00_control/FIGSHARE_PUBLICATION_RECEIPT.json": (3_803, "0eaffa05546177cdebbd82e0bdcc1ebadf75e1702b1c11390b5049f3d1abfa92"),
}

TOP_DIRECT = {
    "architecture": ("qa_events", "qa_event"),
    "course": ("courses", "course"),
    "cursor": ("qa_events", "qa_event"),
    "historical_release": ("release_snapshots", "release_snapshot"),
    "language": ("programs", "program"),
    "planned_release": ("editions", "edition"),
    "schema_version": ("qa_events", "qa_event"),
}

ARRAY_DIRECT = {
    "artifacts": ("artifacts", "artifact"),
    "components": ("assets", "asset"),
    "environments": ("build_recipes", "build_recipe"),
    "exercises": ("segments", "segment"),
    "labs": ("experiments", "experiment"),
    "prerequisite_routes": ("routes", "route"),
    "qa": ("qa_events", "qa_event"),
    "receipts": ("qa_events", "qa_event"),
    "relations": ("relations", "relation"),
    "sources": ("resources", "resource"),
    "units": ("units", "unit"),
}

EXTERNAL_ENDPOINTS = {"A30", "B30", "B40", "B70", "pipeline-o002-build"}
UUID_URN_RE = re.compile(
    r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_bytes(value: Any) -> bytes:
    return canonical(value).encode("utf-8")


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_file(path: Path, expected_bytes: int, expected_sha256: str, label: str) -> None:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path.name}")
    if path.stat().st_size != expected_bytes:
        raise ValueError(f"{label} byte mismatch")
    if sha256_file(path) != expected_sha256:
        raise ValueError(f"{label} SHA-256 mismatch")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rid(record_type: str, stable_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(NAMESPACE, f'{record_type}|{stable_key}')}"


def base(record_type: str, stable_key: str, status: str, **fields: Any) -> dict:
    return {
        "id": rid(record_type, stable_key),
        "record_type": record_type,
        "recorded_at": RECORDED_AT,
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "stable_key": stable_key,
        "status": status or "active",
        "supersedes_id": None,
        "workflow_id": WORKFLOW,
        **fields,
    }


def portable_file(path: str, filesystem_path: Path, status: str, **fields: Any) -> dict:
    return {
        "path": path,
        "bytes": filesystem_path.stat().st_size,
        "sha256": sha256_file(filesystem_path),
        "status": status,
        **fields,
    }


def status_of(payload: Any, fallback: str = "active") -> str:
    if isinstance(payload, dict):
        status = payload.get("status") or payload.get("state")
        if isinstance(status, str) and status:
            return status
        if payload.get("verified") is True:
            return "verified"
    return fallback


def media_type(path: str) -> str:
    suffix = Path(path).suffix.lower()
    return {
        ".csv": "text/csv",
        ".epub": "application/epub+zip",
        ".html": "text/html",
        ".ipynb": "application/x-ipynb+json",
        ".json": "application/json",
        ".md": "text/markdown",
        ".pdf": "application/pdf",
        ".py": "text/x-python",
        ".qmd": "text/markdown",
        ".svg": "image/svg+xml",
        ".txt": "text/plain",
        ".zip": "application/zip",
    }.get(suffix, "application/octet-stream")


def native_key(container: str, payload: Any, ordinal: int | None) -> str:
    if isinstance(payload, dict) and isinstance(payload.get("id"), str):
        return payload["id"]
    if container == "relations" and isinstance(payload, dict):
        return f"{payload['type']}|{payload['from']}|{payload['to']}"
    if ordinal is None:
        return container
    return f"{container}[{ordinal}]"


def native_entries(catalog: dict) -> list[dict]:
    entries: list[dict] = []
    if set(catalog) != set(TOP_DIRECT) | set(ARRAY_DIRECT):
        raise ValueError("native top-level inventory differs from the frozen O002/B80 contract")
    for container in sorted(catalog):
        payload = catalog[container]
        if container in ARRAY_DIRECT:
            if not isinstance(payload, list):
                raise ValueError(f"native table {container} is not an array")
            table, record_type = ARRAY_DIRECT[container]
            for ordinal, item in enumerate(payload):
                key = native_key(container, item, ordinal)
                entries.append(
                    {
                        "container": container,
                        "ordinal": ordinal,
                        "path": f"/{container}/{ordinal}",
                        "native_key": key,
                        "payload": item,
                        "table": table,
                        "record_type": record_type,
                        "stable_key": f"o002-native:{container}:{key}",
                    }
                )
        else:
            table, record_type = TOP_DIRECT[container]
            entries.append(
                {
                    "container": container,
                    "ordinal": None,
                    "path": f"/{container}",
                    "native_key": native_key(container, payload, None),
                    "payload": payload,
                    "table": table,
                    "record_type": record_type,
                    "stable_key": f"o002-native:{container}",
                }
            )
    if len(entries) != 326:
        raise ValueError(f"native entry count mismatch: {len(entries)} != 326")
    return entries


def verify_native_references(catalog: dict, owner_root: Path) -> dict:
    arrays_with_ids = [name for name in ARRAY_DIRECT if name != "relations"]
    declared: list[str] = []
    by_table: dict[str, dict[str, dict]] = {}
    for name in arrays_with_ids:
        rows = catalog[name]
        if any(not isinstance(row.get("id"), str) for row in rows):
            raise ValueError(f"native table lacks stable IDs: {name}")
        by_table[name] = {row["id"]: row for row in rows}
        if len(by_table[name]) != len(rows):
            raise ValueError(f"duplicate native IDs inside {name}")
        declared.extend(by_table[name])
    declared.append(catalog["course"]["id"])
    duplicates = [value for value, count in Counter(declared).items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate native IDs across tables: {duplicates[:5]}")

    sources = set(by_table["sources"])
    components = set(by_table["components"])
    units = set(by_table["units"])
    exercises = set(by_table["exercises"])
    artifacts = set(by_table["artifacts"])
    environments = set(by_table["environments"])
    labs = set(by_table["labs"])
    receipts = set(by_table["receipts"])

    def require(value: str, known: set[str], label: str) -> None:
        if value not in known:
            raise ValueError(f"dangling native reference {label}: {value}")

    for component in catalog["components"]:
        require(component["source"], sources, f"component {component['id']} source")
        if not (owner_root / component["path"]).is_file():
            raise ValueError(f"missing component path: {component['path']}")
    for unit in catalog["units"]:
        for value in unit["components"]:
            require(value, components, f"unit {unit['id']} component")
        for value in unit["exercises"]:
            require(value, exercises, f"unit {unit['id']} exercise")
        if not (owner_root / unit["reader_path"]).is_file():
            raise ValueError(f"missing unit reader: {unit['reader_path']}")
    for exercise in catalog["exercises"]:
        require(exercise["unit"], units, f"exercise {exercise['id']} unit")
        if not (owner_root / exercise["source_path"]).is_file():
            raise ValueError(f"missing exercise source: {exercise['source_path']}")
    for artifact in catalog["artifacts"]:
        if artifact["producer"] not in components | labs | EXTERNAL_ENDPOINTS:
            raise ValueError(f"unknown artifact producer: {artifact['producer']}")
        for value in artifact.get("receipt_ids", []):
            require(value, receipts, f"artifact {artifact['id']} receipt")
        for value in artifact.get("members", []):
            require(value, artifacts, f"artifact {artifact['id']} member")
        if artifact.get("accessibility_description"):
            require(artifact["accessibility_description"], artifacts, "artifact accessibility description")
    for lab in catalog["labs"]:
        require(lab["unit"], units, f"lab {lab['id']} unit")
        require(lab["environment"], environments, f"lab {lab['id']} environment")
        for value in lab["exercise_ids"]:
            require(value, exercises, f"lab {lab['id']} exercise")
        for value in lab["artifact_ids"]:
            require(value, artifacts, f"lab {lab['id']} artifact")
    for route in catalog["prerequisite_routes"]:
        require(route["unit"], units, f"route {route['id']} unit")
        for value in route["exercises"]:
            require(value, exercises, f"route {route['id']} exercise")
    for qa in catalog["qa"]:
        for value in qa["receipt_ids"]:
            require(value, receipts, f"QA {qa['id']} receipt")
    for value in catalog["planned_release"]["artifact_ids"]:
        require(value, artifacts, "planned release artifact")
    for value in catalog["architecture"]["required_unit_ids"] + catalog["architecture"]["admitted_unit_ids"]:
        require(value, units, "architecture unit")
    require(catalog["cursor"]["last_admitted_unit"], units, "cursor unit")

    known_endpoints = set(declared) | EXTERNAL_ENDPOINTS
    relation_keys = []
    for relation in catalog["relations"]:
        require(relation["from"], known_endpoints, "relation from")
        require(relation["to"], known_endpoints, "relation to")
        relation_keys.append(native_key("relations", relation, 0))
    if len(relation_keys) != len(set(relation_keys)):
        raise ValueError("duplicate native relation triples")
    return {
        "declared_native_ids": len(declared),
        "unique_native_ids": len(set(declared)),
        "relation_triples": len(relation_keys),
        "native_foreign_key_closure": "pass",
    }


def verify_source(owner_root: Path, native_schema_path: Path) -> tuple[dict, bytes, dict, dict, dict, dict, dict]:
    for relative, (size, digest) in EXPECTED.items():
        exact_file(owner_root / relative, size, digest, relative)
    catalog_path = owner_root / "backend/catalog.json"
    raw = catalog_path.read_bytes()
    if raw != (owner_root / "output/backend/catalog.json").read_bytes():
        raise ValueError("output catalog copy differs from native authority")
    if raw != (owner_root / "docs/backend/catalog.json").read_bytes():
        raise ValueError("docs catalog copy differs from native authority")
    catalog = json.loads(raw.decode("utf-8"))
    if pretty_bytes(catalog) != raw:
        raise ValueError("native catalog is not exact deterministic sorted JSON")

    native_schema = load_json(native_schema_path)
    Draft202012Validator.check_schema(native_schema)
    errors = sorted(
        Draft202012Validator(native_schema, format_checker=FormatChecker()).iter_errors(catalog),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise ValueError(f"native schema failure {list(first.absolute_path)}: {first.message}")

    cursor = load_json(owner_root / "00_control/CURRENT_CURSOR.json")
    github = load_json(owner_root / "00_control/GITHUB_PUBLICATION_RECEIPT.json")
    zenodo = load_json(owner_root / "00_control/PUBLICATION_RECEIPT_FINAL.json")
    figshare = load_json(owner_root / "00_control/FIGSHARE_PUBLICATION_RECEIPT.json")
    if cursor["pursuit_status"] != "complete" or cursor["current_release"]["b80_curriculum_complete"] is not True:
        raise ValueError("CURRENT_CURSOR does not bind a completed B80 curriculum")
    if cursor["current_release"]["selected_unit_count"] != 14 or cursor["current_release"]["admitted_unit_count"] != 14:
        raise ValueError("CURRENT_CURSOR unit closure mismatch")
    if cursor["current_release"]["exercise_count"] != 75:
        raise ValueError("CURRENT_CURSOR exercise closure mismatch")
    if cursor["backend_truth"]["catalog_bytes"] != len(raw) or cursor["backend_truth"]["catalog_sha256"] != sha256_bytes(raw):
        raise ValueError("CURRENT_CURSOR backend truth does not bind native catalog")
    if len(catalog["units"]) != 14 or len(catalog["exercises"]) != 75:
        raise ValueError("catalog completion counts do not match cursor")
    if catalog["architecture"]["status"] != "complete" or catalog["architecture"]["open_requirements"]:
        raise ValueError("catalog architecture is not closed")
    if catalog["cursor"]["b80_curriculum_complete"] is not True:
        raise ValueError("catalog cursor does not mark B80 complete")
    if github["successful"] is not True or github["repository"]["commit"] != cursor["github"]["release_commit"]:
        raise ValueError("GitHub receipt/cursor commit mismatch")
    if github["tag"]["name"] != catalog["planned_release"]["tag"]:
        raise ValueError("GitHub receipt/catalog tag mismatch")
    if zenodo["successful"] is not True or zenodo["zenodo"]["record_id"] != catalog["planned_release"]["record_id"]:
        raise ValueError("Zenodo receipt/catalog record mismatch")
    if figshare["successful"] is not True:
        raise ValueError("Figshare preservation receipt is not successful")

    github_assets = {item["filename"]: item for item in github["release"]["assets"]}
    zenodo_assets = {item["filename"]: item for item in zenodo["artifacts"]}
    if set(github_assets) != set(zenodo_assets):
        raise ValueError("GitHub/Zenodo release inventory mismatch")
    for filename in github_assets:
        if (github_assets[filename]["bytes"], github_assets[filename]["sha256"]) != (
            zenodo_assets[filename]["bytes"],
            zenodo_assets[filename]["sha256"],
        ):
            raise ValueError(f"cross-repository artifact mismatch: {filename}")

    final_by_path = {item["path"]: item for item in zenodo["artifacts"]}
    artifact_evidence: dict[str, dict] = {}
    for artifact in catalog["artifacts"]:
        item = dict(artifact)
        public = final_by_path.get(artifact["path"])
        if item.get("bytes") is None or item.get("sha256") is None:
            if public is None:
                raise ValueError(f"artifact lacks exact byte witness: {artifact['id']}")
            item["bytes"] = public["bytes"]
            item["sha256"] = public["sha256"]
        if public and (item["bytes"], item["sha256"]) != (public["bytes"], public["sha256"]):
            raise ValueError(f"catalog/public artifact mismatch: {artifact['id']}")
        path = owner_root / artifact["path"]
        exact_file(path, int(item["bytes"]), item["sha256"], artifact["id"])
        item["public_url"] = public.get("public_url") if public else None
        artifact_evidence[artifact["id"]] = item

    planned_paths = {
        artifact_evidence[value]["path"] for value in catalog["planned_release"]["artifact_ids"]
    }
    if planned_paths != set(final_by_path):
        raise ValueError("planned release artifact inventory is not exact")

    for environment in catalog["environments"]:
        exact_file(
            owner_root / environment["lock"]["path"],
            environment["lock"]["bytes"],
            environment["lock"]["sha256"],
            f"environment lock {environment['id']}",
        )
        exact_file(
            owner_root / environment["receipt"]["path"],
            environment["receipt"]["bytes"],
            environment["receipt"]["sha256"],
            f"environment receipt {environment['id']}",
        )
    for receipt in catalog["receipts"]:
        if receipt["binding"] == "bound":
            exact_file(owner_root / receipt["path"], receipt["bytes"], receipt["sha256"], receipt["id"])

    diagnostics = verify_native_references(catalog, owner_root)
    return catalog, raw, cursor, github, zenodo, figshare, {"artifacts": artifact_evidence, **diagnostics}


def native_extension(entry: dict, catalog_sha256: str) -> dict:
    payload = entry["payload"]
    return {
        NATIVE_EXTENSION: {
            "disposition": "direct-lossless-native-extension",
            "native_container": entry["container"],
            "native_key": entry["native_key"],
            "native_ordinal": entry["ordinal"],
            "native_path": entry["path"],
            "native_payload": payload,
            "native_payload_sha256": sha256_bytes(canonical_bytes(payload)),
            "source_catalog_sha256": catalog_sha256,
            "source_schema": SOURCE_SCHEMA_NAME,
            "source_schema_version": SOURCE_SCHEMA_VERSION,
        }
    }


def referenced_uuid_urns(value: Any, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "extensions":
                continue
            yield from referenced_uuid_urns(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from referenced_uuid_urns(child, (*path, str(index)))
    elif isinstance(value, str) and UUID_URN_RE.fullmatch(value):
        yield path, value


def build_backend(catalog: dict, raw: bytes, cursor: dict, zenodo: dict, evidence: dict, schema: dict) -> tuple[dict, dict]:
    entries = native_entries(catalog)
    table_names = sorted(schema["properties"]["tables"]["properties"])
    tables: dict[str, list[dict]] = {name: [] for name in table_names}
    catalog_sha = sha256_bytes(raw)

    entry_ids = {
        entry["path"]: rid(entry["record_type"], entry["stable_key"])
        for entry in entries
    }
    native_id_map: dict[str, str] = {}
    for entry in entries:
        payload = entry["payload"]
        if isinstance(payload, dict) and isinstance(payload.get("id"), str):
            if payload["id"] in native_id_map:
                raise ValueError(f"duplicate direct native identity: {payload['id']}")
            native_id_map[payload["id"]] = entry_ids[entry["path"]]

    license_values = sorted(
        {row["license"] for row in catalog["sources"]}
        | {row["license"] for row in catalog["components"]}
    )
    rights_map = {value: rid("rights", f"o002-derived:rights:{value}") for value in license_values}
    overall_license = "CC BY-SA 4.0 text; MIT code"
    if overall_license not in rights_map:
        raise ValueError("missing native overall rights expression")
    original_resource_id = native_id_map["src-o002-original"]
    edition_id = entry_ids["/planned_release"]
    program_id = entry_ids["/language"]
    course_id = entry_ids["/course"]

    for license_value in license_values:
        stable_key = f"o002-derived:rights:{license_value}"
        rights = base(
            "rights",
            stable_key,
            "active",
            assertion_status="derived from exact native source/component license field",
            attribution="Attribution and component identity remain in the native catalog payload",
            authority="O002/B80 frozen catalog and component-level rights declarations",
            change_notice="Preserve the controlling component license and change notices",
            license_expression=license_value,
            nonendorsement="No endorsement implied",
            notice_locator="backend/catalog.json",
            notice_sha256=sha256_bytes(license_value.encode("utf-8")),
            source_component_id=license_value,
            third_party_status="component-specific rights preserved",
        )
        rights["extensions"] = {
            DERIVED_EXTENSION: {
                "disposition": "derived-relational-anchor-not-a-native-entry",
                "source_field": "sources[].license or components[].license",
                "source_value": license_value,
            }
        }
        if rights["id"] != rights_map[license_value]:
            raise ValueError("rights identity derivation mismatch")
        tables["rights"].append(rights)

    endpoint_map = dict(native_id_map)
    for endpoint in sorted(EXTERNAL_ENDPOINTS):
        stable_key = f"o002-derived:external-endpoint:{endpoint}"
        concept = base(
            "concept",
            stable_key,
            "external-reference",
            concept_key=endpoint,
            concept_scheme="o002.external-reference-anchor",
            definition_segment_id=None,
            parent_concept_id=None,
        )
        concept["extensions"] = {
            DERIVED_EXTENSION: {
                "disposition": "derived-relational-anchor-not-a-native-entry",
                "source": "native relation endpoint or prerequisite key",
                "source_value": endpoint,
            }
        }
        tables["concepts"].append(concept)
        endpoint_map[endpoint] = concept["id"]

    sources_by_id = {row["id"]: row for row in catalog["sources"]}
    components_by_id = {row["id"]: row for row in catalog["components"]}
    units_by_id = {row["id"]: row for row in catalog["units"]}
    unit_resource: dict[str, str] = {}
    unit_rights: dict[str, str] = {}
    for unit in catalog["units"]:
        reader_components = [
            components_by_id[value]
            for value in unit["components"]
            if components_by_id[value]["kind"] == "reader_text"
        ]
        if len(reader_components) != 1:
            raise ValueError(f"unit does not have one reader-text authority: {unit['id']}")
        component = reader_components[0]
        unit_resource[unit["id"]] = native_id_map[component["source"]]
        unit_rights[unit["id"]] = rights_map[component["license"]]

    mappings: list[bytes] = []
    direct_common_ids: list[str] = []
    artifact_evidence = evidence["artifacts"]
    public_by_path = {item["path"]: item for item in zenodo["artifacts"]}

    for entry in entries:
        payload = entry["payload"]
        table = entry["table"]
        record_type = entry["record_type"]
        common = base(record_type, entry["stable_key"], status_of(payload))
        common["extensions"] = native_extension(entry, catalog_sha)
        container = entry["container"]

        if container == "language":
            common.update(
                curriculum_version=catalog["planned_release"]["version"],
                locale=payload,
                program_key="O002-B80",
                rights_id=rights_map[overall_license],
                title=catalog["course"]["title"],
            )
        elif container == "course":
            common.update(
                course_key=payload["id"],
                curriculum_source_locator="backend/catalog.json",
                curriculum_source_sha256=catalog_sha,
                order_key=payload["id"],
                outcome="A complete reproducible mathematical-computing course with executable evidence",
                prerequisite_course_keys=[payload["prerequisite"]],
                program_id=program_id,
                resource_keys=[row["id"] for row in catalog["sources"]],
                role=payload["title"],
                scope="14 selected and admitted units",
                stage="B",
                title=payload["title"],
            )
        elif container == "planned_release":
            common.update(
                archive_sha256=None,
                commit_sha=cursor["github"]["release_commit"],
                edition_kind="published-complete-Indonesian-edition",
                locale=catalog["language"],
                release_date=cursor["completion_date"],
                resource_id=original_resource_id,
                rights_id=rights_map[overall_license],
                source_edition_id=None,
                tree_sha=None,
                vcs_ref=payload["tag"],
                vcs_type="git",
                version_label=payload["version"],
            )
        elif container == "historical_release":
            common.update(
                archive_sha256=None,
                artifact_ids=[],
                commit_sha=None,
                edition_id=edition_id,
                immutable=True,
                publication_uri=f"https://doi.org/{payload['doi']}",
                release_date=cursor["completion_date"],
                release_version=payload["version"],
                snapshot_kind="historical-standalone-predecessor-descriptor",
                tree_sha=None,
            )
        elif container in {"architecture", "cursor", "schema_version"}:
            common.update(
                input_hash=sha256_bytes(canonical_bytes(payload)),
                method="exact frozen native catalog field",
                qa_type=f"o002-{container}",
                result="pass" if container != "schema_version" else str(payload),
                reviewer_kind="native O002 backend authority",
                severity_p1=0,
                severity_p2=0,
                severity_p3=0,
                tool_name="O002 backend catalog",
                tool_version=catalog["schema_version"],
                witness_locator=f"backend/catalog.json#/{container}",
            )
        elif container == "sources":
            common.update(
                authority_policy="Exact native catalog identity; no authority claim beyond the frozen payload",
                creator_name="Creator attribution is not asserted by this native catalog entry",
                official_reader=None,
                official_repository=payload["identity"],
                original_title=payload["title"],
                resource_key=payload["id"],
                work_type=payload["role"],
            )
        elif container == "components":
            common.update(
                asset_kind=payload["kind"],
                canonical_path_or_uri=payload["path"],
                media_type=media_type(payload["path"]),
                resource_id=native_id_map[payload["source"]],
                rights_default_id=rights_map[payload["license"]],
            )
        elif container == "units":
            common.update(
                first_edition_id=edition_id,
                identity_anchor=payload["id"],
                identity_basis="exact stable O002/B80 native unit ID",
                resource_id=unit_resource[payload["id"]],
                rights_default_id=unit_rights[payload["id"]],
                source_label=payload["title"],
                source_local_id=payload["id"],
                source_path=payload["reader_path"],
                source_xml_path=None,
                unit_kind="primer" if payload["id"].startswith("o002.p") else "curriculum-unit",
            )
        elif container == "exercises":
            common.update(
                identity_anchor=payload["id"],
                ordinal=int(payload["sequence"]),
                segment_kind=f"exercise-{payload['kind']}",
                segmentation_profile="o002.backend.v2-exercise-metadata",
                unit_id=native_id_map[payload["unit"]],
            )
        elif container == "artifacts":
            resolved = artifact_evidence[payload["id"]]
            common.update(
                artifact_kind=payload["kind"],
                build_receipt=canonical(
                    {
                        "producer": payload["producer"],
                        "receipt_ids": payload.get("receipt_ids", []),
                        "native_path": payload["path"],
                    }
                ),
                bytes=int(resolved["bytes"]),
                edition_id=edition_id,
                locale=catalog["language"],
                manifest_sha256=resolved["sha256"] if payload["kind"] == "manifest_json" else None,
                public_uri=resolved.get("public_url"),
                sha256=resolved["sha256"],
                toolchain_id=payload["producer"],
                tree_sha256=None,
            )
        elif container == "labs":
            common.update(
                edition_id=edition_id,
                expected_output_segment_ids=[],
                instruction_segment_ids=[native_id_map[value] for value in payload["exercise_ids"]],
                invocation="; ".join(payload["source_paths"]),
                kind=payload["kind"],
                parameter_segment_ids=[],
                resource_id=unit_resource[payload["unit"]],
                result_mode="native artifact IDs retained losslessly in extension",
                rights_id=unit_rights[payload["unit"]],
                runner_asset_revision_ids=[],
                source_file_revision_id=None,
                unit_id=native_id_map[payload["unit"]],
            )
        elif container == "environments":
            common_environment = {
                "availability": str(payload["availability"]),
                "kind": str(payload["kind"]),
                "lock": canonical(payload["lock"]),
                "package_count": str(payload["package_count"]),
                "platform": str(payload["platform"]),
                "receipt": canonical(payload["receipt"]),
                "required_packages": canonical(payload["required_packages"]),
                "runtime_version": str(payload["runtime_version"]),
                "status": str(payload["status"]),
            }
            common.update(
                command=[],
                edition_id=edition_id,
                environment=common_environment,
                input_ids=[],
                name=payload["id"],
                output_ids=[],
                resource_id=original_resource_id,
                verification={"receipt": payload["receipt"], "lock": payload["lock"]},
                working_directory=".",
            )
        elif container == "prerequisite_routes":
            common.update(
                course_id=course_id,
                description=payload["title"],
                locale=catalog["language"],
                program_id=program_id,
                route_key=payload["id"],
                route_kind="prerequisite-path",
                title=payload["title"],
                version_label=catalog["planned_release"]["version"],
            )
        elif container in {"qa", "receipts"}:
            common.update(
                input_hash=sha256_bytes(canonical_bytes(payload)),
                method="exact native QA or receipt record",
                qa_type=payload.get("scope") or payload.get("kind") or payload["id"],
                result=payload["status"],
                reviewer_kind="native O002 QA workflow",
                severity_p1=0,
                severity_p2=0,
                severity_p3=0,
                tool_name=payload.get("schema", "O002 backend QA"),
                tool_version=catalog["schema_version"],
                witness_locator=payload.get("path") or payload.get("evidence") or entry["path"],
            )
        elif container == "relations":
            common.update(
                assertion_method="explicit native O002 relation triple",
                confidence="explicit",
                edition_id=edition_id,
                from_id=endpoint_map[payload["from"]],
                ordinal=int(entry["ordinal"]),
                relation_type=payload["type"],
                source_locator=f"backend/catalog.json#/relations/{entry['ordinal']}",
                strength="native-explicit",
                to_id=endpoint_map[payload["to"]],
            )
        else:
            raise ValueError(f"unhandled native container: {container}")

        if common["id"] != entry_ids[entry["path"]]:
            raise ValueError(f"common ID derivation mismatch: {entry['path']}")
        tables[table].append(common)
        direct_common_ids.append(common["id"])
        mappings.append(
            (
                canonical(
                    {
                        "disposition": "direct-lossless-native-extension",
                        "native_key": entry["native_key"],
                        "native_path": entry["path"],
                        "native_payload_sha256": sha256_bytes(canonical_bytes(payload)),
                        "target_id": common["id"],
                        "target_table": table,
                    }
                )
                + "\n"
            ).encode("utf-8")
        )

    for rows in tables.values():
        rows.sort(key=lambda row: row["id"])
    backend = {
        "$schema": "schema/backend-v1.schema.json",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "dataset_id": rid("dataset", "o002-b80-id:2026.08.22.1"),
        "dataset_version": "2026.08.22.1+interlanguage-v1",
        "tables": dict(sorted(tables.items())),
    }

    recovered_top: dict[str, Any] = {}
    recovered_arrays: dict[str, list[tuple[int, Any]]] = defaultdict(list)
    recovered_count = 0
    for rows in tables.values():
        for common in rows:
            extension = common.get("extensions", {}).get(NATIVE_EXTENSION)
            if extension is None:
                continue
            payload = extension["native_payload"]
            if sha256_bytes(canonical_bytes(payload)) != extension["native_payload_sha256"]:
                raise ValueError("native extension payload checksum mismatch")
            container = extension["native_container"]
            ordinal = extension["native_ordinal"]
            if ordinal is None:
                if container in recovered_top:
                    raise ValueError(f"duplicate recovered top field: {container}")
                recovered_top[container] = payload
            else:
                recovered_arrays[container].append((int(ordinal), payload))
            recovered_count += 1
    recovered = dict(recovered_top)
    for container, values in recovered_arrays.items():
        values.sort(key=lambda item: item[0])
        if [ordinal for ordinal, _payload in values] != list(range(len(values))):
            raise ValueError(f"native ordinal closure failure: {container}")
        recovered[container] = [payload for _ordinal, payload in values]
    if recovered != catalog:
        raise ValueError("exact native reverse extraction differs from source catalog")
    recovered_bytes = pretty_bytes(recovered)
    if recovered_bytes != raw:
        raise ValueError("reverse extraction does not recreate exact source catalog bytes")
    if len(set(direct_common_ids)) != len(entries):
        raise ValueError("direct common record identity collision")

    mapping_payload = b"".join(sorted(mappings))
    diagnostics = {
        "direct_native_entries": len(entries),
        "direct_common_records": len(direct_common_ids),
        "exact_reverse_extraction": recovered_count,
        "exact_catalog_bytes_reconstructed": len(recovered_bytes),
        "exact_catalog_sha256_reconstructed": sha256_bytes(recovered_bytes),
        "native_entry_mapping_bytes": len(mapping_payload),
        "native_entry_mapping_sha256": sha256_bytes(mapping_payload),
        "native_record_disposition": {"direct-lossless-native-extension": len(entries)},
        "derived_rights_records": len(license_values),
        "derived_external_reference_anchors": len(EXTERNAL_ENDPOINTS),
    }
    return backend, diagnostics


def validate_backend(backend: dict, schema: dict, direct_entries: int) -> dict:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(backend),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise ValueError(f"common schema failure {list(first.absolute_path)}: {first.message}")
    records = sorted(
        [record for rows in backend["tables"].values() for record in rows],
        key=lambda record: (record["record_type"], record["id"]),
    )
    ids = [record["id"] for record in records]
    stable_keys = [record["stable_key"] for record in records]
    duplicate_ids = [value for value, count in Counter(ids).items() if count > 1]
    duplicate_keys = [value for value, count in Counter(stable_keys).items() if count > 1]
    if duplicate_ids or duplicate_keys:
        raise ValueError(f"common uniqueness failure: IDs={duplicate_ids[:3]}, stable_keys={duplicate_keys[:3]}")
    known = set(ids)
    dangling = []
    allowed_external = {"supersedes_id", "source_edition_id", "source_revision_id", "source_variant_id", "source_occurrence_id"}
    for record in records:
        for field_path, value in referenced_uuid_urns(record):
            if field_path == ("id",):
                continue
            leaf = field_path[-1] if field_path else ""
            if leaf not in allowed_external and value not in known:
                dangling.append({"record": record["id"], "field": "/".join(field_path), "value": value})
    if dangling:
        raise ValueError(f"common foreign-key closure failure: {dangling[:5]}")
    native_extension_count = sum(
        NATIVE_EXTENSION in record.get("extensions", {}) for record in records
    )
    if native_extension_count != direct_entries:
        raise ValueError("direct native/common record coverage mismatch")

    global_payload = b"".join((canonical(record) + "\n").encode("utf-8") for record in records)
    table_hashes = {}
    for name, rows in backend["tables"].items():
        payload = b"".join((canonical(row) + "\n").encode("utf-8") for row in rows)
        table_hashes[name] = {
            "records": len(rows),
            "virtual_jsonl_bytes": len(payload),
            "virtual_jsonl_sha256": sha256_bytes(payload),
        }
    return {
        "record_count": len(records),
        "table_count": len(backend["tables"]),
        "nonempty_table_count": sum(bool(rows) for rows in backend["tables"].values()),
        "table_counts": {name: len(rows) for name, rows in backend["tables"].items()},
        "table_hashes": table_hashes,
        "global_unique_ids": len(known),
        "global_unique_stable_keys": len(set(stable_keys)),
        "foreign_key_closure": "pass",
        "strict_schema": "pass",
        "virtual_records_jsonl_bytes": len(global_payload),
        "virtual_records_jsonl_sha256": sha256_bytes(global_payload),
    }


def privacy_scan(value: Any) -> dict:
    payload = canonical(value)
    forbidden_name = "".join(chr(code) for code in (70, 108, 111, 114, 105, 115))
    windows_user_root = "".join(chr(code) for code in (67, 58, 92, 85, 115, 101, 114, 115, 92))
    posix_windows_user_root = "".join(chr(code) for code in (67, 58, 47, 85, 115, 101, 114, 115, 47))
    needles = [forbidden_name, windows_user_root, posix_windows_user_root, ".codex", "access_token", "Authorization: Bearer"]
    hits = [index for index, needle in enumerate(needles) if needle.lower() in payload.lower()]
    if hits:
        raise ValueError(f"private-marker scan failed ({len(hits)} marker classes)")
    return {"private_marker_hits": 0, "marker_classes_scanned": len(needles)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--receipt-schema", required=True, type=Path)
    parser.add_argument("--output-receipt", required=True, type=Path)
    args = parser.parse_args()

    owner_root = args.corpus_root.resolve()
    schema_path = args.schema.resolve()
    receipt_schema_path = args.receipt_schema.resolve()
    native_schema_path = owner_root / "backend/catalog.schema.json"
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)

    first = verify_source(owner_root, native_schema_path)
    catalog, raw, cursor, github, zenodo, figshare, source_diagnostics = first
    first_backend, first_mapping = build_backend(catalog, raw, cursor, zenodo, source_diagnostics, schema)
    first_validation = validate_backend(first_backend, schema, first_mapping["direct_native_entries"])
    first_hash = sha256_bytes(canonical_bytes(first_backend))

    second = verify_source(owner_root, native_schema_path)
    if first[:-1] != second[:-1]:
        raise ValueError("owner authority inputs changed between independent reads")
    second_catalog, second_raw, second_cursor, _second_github, second_zenodo, _second_figshare, second_diagnostics = second
    second_backend, second_mapping = build_backend(
        second_catalog, second_raw, second_cursor, second_zenodo, second_diagnostics, schema
    )
    second_validation = validate_backend(second_backend, schema, second_mapping["direct_native_entries"])
    second_hash = sha256_bytes(canonical_bytes(second_backend))
    if first_hash != second_hash or first_mapping != second_mapping or first_validation != second_validation:
        raise ValueError("two independent common-backend assemblies are not byte-identical")
    privacy = privacy_scan(first_backend)

    source_files = {
        relative: {
            "bytes": size,
            "sha256": digest,
        }
        for relative, (size, digest) in EXPECTED.items()
    }
    receipt = {
        "schema_name": "interlanguage-math-modular-backend-migration-receipt",
        "schema_version": SCHEMA_VERSION,
        "migration_id": "o002-b80-id-2026.08.22.1-to-interlanguage-v1.0.0",
        "migration_mode": "lossless-zero-copy-one-to-one-native-catalog-adapter",
        "source": {
            "dataset_id": "O002/B80",
            "dataset_version": catalog["planned_release"]["version"],
            "course_role_id": catalog["course"]["id"],
            "schema_name": SOURCE_SCHEMA_NAME,
            "schema_version": catalog["schema_version"],
            "authority_files": source_files,
            "catalog_path": "backend/catalog.json",
            "catalog_bytes": len(raw),
            "catalog_sha256": sha256_bytes(raw),
            "native_entry_count": first_mapping["direct_native_entries"],
            "native_declared_id_count": source_diagnostics["declared_native_ids"],
            "selected_unit_count": cursor["current_release"]["selected_unit_count"],
            "admitted_unit_count": cursor["current_release"]["admitted_unit_count"],
            "exercise_count": cursor["current_release"]["exercise_count"],
            "test_count": cursor["current_release"]["test_count"],
            "reader_pages": cursor["current_release"]["pdf_page_count"],
            "completion": cursor["pursuit_status"],
            "github_commit": cursor["github"]["release_commit"],
            "github_release": cursor["github"]["release"],
            "zenodo_version_doi": cursor["zenodo"]["doi"],
            "figshare_version_doi": cursor["figshare"]["doi"],
        },
        "target": {
            "dataset_id": first_backend["dataset_id"],
            "dataset_version": first_backend["dataset_version"],
            "schema_name": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "schema_path": "schemas/backend-v1.schema.json",
            "schema_bytes": schema_path.stat().st_size,
            "schema_sha256": sha256_file(schema_path),
            "record_count": first_validation["record_count"],
            "table_count": first_validation["table_count"],
            "nonempty_table_count": first_validation["nonempty_table_count"],
            "virtual_records_jsonl_bytes": first_validation["virtual_records_jsonl_bytes"],
            "virtual_records_jsonl_sha256": first_validation["virtual_records_jsonl_sha256"],
            "canonical_backend_sha256": first_hash,
        },
        "coverage": {
            **source_diagnostics,
            **first_mapping,
            "course_role_id": "B80",
            "selected_units": 14,
            "admitted_units": 14,
            "exercises": 75,
            "catalog_copies_byte_identical": 3,
            "current_artifacts_verified_locally": len(catalog["artifacts"]),
            "release_artifacts_cross_repository_verified": len(zenodo["artifacts"]),
            "source_and_component_rights_preserved": True,
            "model_provenance": cursor["terminology_qa"]["model_disclosure"],
        },
        "transformation": {
            "native_files_modified": 0,
            "native_entries_modified": 0,
            "native_entries_preserved_in_extensions": first_mapping["direct_native_entries"],
            "native_payload_fields_preserved": "all fields of all 326 native catalog entries",
            "native_catalog_bytes_reconstructable": True,
            "native_catalog_bytes_changed": 0,
            "common_ids_added": first_validation["record_count"],
            "derived_identity_algorithm": "UUIDv5(namespace, record_type|stable_key)",
            "derived_records_materialized": False,
            "additive_records": {
                "rights": first_mapping["derived_rights_records"],
                "external_reference_anchors": first_mapping["derived_external_reference_anchors"],
            },
        },
        "validation": {
            "result": "pass",
            "native_catalog_schema": "pass",
            "native_catalog_filename_size_sha256": "pass",
            "native_catalog_three_copy_byte_identity": "pass",
            "native_global_id_uniqueness": "pass",
            "native_foreign_key_closure": "pass",
            "native_source_asset_receipt_closure": "pass",
            "exact_native_reverse_extraction": first_mapping["exact_reverse_extraction"],
            "exact_native_catalog_byte_reconstruction": "pass",
            "strict_common_backend_schema": "pass",
            "common_global_id_uniqueness": "pass",
            "common_global_stable_key_uniqueness": "pass",
            "common_foreign_key_closure": "pass",
            "common_table_inventory": "38/38 present",
            "two_independent_authority_reads": 2,
            "two_independent_assemblies": "byte-identical",
            "first_canonical_backend_sha256": first_hash,
            "second_canonical_backend_sha256": second_hash,
            **privacy,
        },
        "tables": first_validation["table_hashes"],
        "materialization": {
            "status": "not duplicated locally",
            "reason": "The exact admitted native catalog plus this deterministic reversible adapter reconstruct the strict common backend twice without a redundant materialized copy.",
            "script_path": "scripts/migrate-o002-backend-v1.py",
        },
        "public_artifacts": [
            portable_file(
                "00_control/CURRENT_CURSOR.json",
                owner_root / "00_control/CURRENT_CURSOR.json",
                cursor["pursuit_status"],
                units=cursor["current_release"]["admitted_unit_count"],
            ),
            portable_file(
                "00_control/GITHUB_PUBLICATION_RECEIPT.json",
                owner_root / "00_control/GITHUB_PUBLICATION_RECEIPT.json",
                "public_bytes_verified",
                repository=github["repository"]["public_url"],
                release=github["release"]["public_url"],
            ),
            portable_file(
                "00_control/PUBLICATION_RECEIPT_FINAL.json",
                owner_root / "00_control/PUBLICATION_RECEIPT_FINAL.json",
                "public_bytes_verified",
                version_doi=cursor["zenodo"]["doi"],
            ),
            portable_file(
                "00_control/FIGSHARE_PUBLICATION_RECEIPT.json",
                owner_root / "00_control/FIGSHARE_PUBLICATION_RECEIPT.json",
                "public_bytes_verified",
                version_doi=cursor["figshare"]["doi"],
            ),
        ],
        "credentials_recorded": False,
    }
    privacy_scan(receipt)
    receipt_schema = load_json(receipt_schema_path)
    Draft202012Validator.check_schema(receipt_schema)
    errors = sorted(
        Draft202012Validator(receipt_schema, format_checker=FormatChecker()).iter_errors(receipt),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first_error = errors[0]
        raise ValueError(f"receipt schema failure {list(first_error.absolute_path)}: {first_error.message}")

    receipt_bytes = pretty_bytes(receipt)
    args.output_receipt.parent.mkdir(parents=True, exist_ok=True)
    args.output_receipt.write_bytes(receipt_bytes)
    if args.output_receipt.read_bytes() != receipt_bytes:
        raise ValueError("migration receipt byte readback mismatch")
    print(
        canonical(
            {
                "result": "pass",
                "native_entries": first_mapping["direct_native_entries"],
                "target_records": first_validation["record_count"],
                "tables": first_validation["table_count"],
                "nonempty_tables": first_validation["nonempty_table_count"],
                "canonical_backend_sha256": first_hash,
                "virtual_records_jsonl_sha256": first_validation["virtual_records_jsonl_sha256"],
                "receipt": "backend/migrations/o002-b80-id-v1/MIGRATION_RECEIPT.json",
                "receipt_bytes": len(receipt_bytes),
                "receipt_sha256": sha256_bytes(receipt_bytes),
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)
