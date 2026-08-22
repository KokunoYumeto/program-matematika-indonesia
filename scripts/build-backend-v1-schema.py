#!/usr/bin/env python3
"""Build the strict common backend v1 schema from the admitted DMOI kernel.

The DMOI full-backend schema is the strongest proved structural implementation
in the Indonesian corpus.  This builder preserves its 32 strict record types,
relaxes only the package-level requirement that every table be non-empty, and
adds the six cross-corpus entity types that the audited lanes require.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


SCHEMA_NAME = "interlanguage-math-modular-backend"
SCHEMA_VERSION = "1.0.0"
UUID5 = {
    "type": "string",
    "pattern": r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
}
NULLABLE_UUID5 = {"oneOf": [UUID5, {"type": "null"}]}
SHA256 = {"type": "string", "pattern": r"^[0-9a-f]{64}$"}
NULLABLE_SHA256 = {"oneOf": [SHA256, {"type": "null"}]}
DATE_TIME = {
    "type": "string",
    "format": "date-time",
    "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$",
}
EXTENSIONS = {
    "type": "object",
    "description": "Namespaced, lossless source-format data outside the common contract.",
    "propertyNames": {"pattern": r"^[a-z0-9][a-z0-9._-]*$"},
    "additionalProperties": True,
}


def common(record_type: str, fields: dict, required: list[str]) -> dict:
    properties = {
        "id": copy.deepcopy(UUID5),
        "record_type": {"const": record_type},
        "recorded_at": copy.deepcopy(DATE_TIME),
        "schema_name": {"const": SCHEMA_NAME},
        "schema_version": {"const": SCHEMA_VERSION},
        "stable_key": {"type": "string", "minLength": 1},
        "status": {"type": "string", "minLength": 1},
        "supersedes_id": copy.deepcopy(NULLABLE_UUID5),
        "workflow_id": {"type": "string", "minLength": 1},
        "extensions": copy.deepcopy(EXTENSIONS),
    }
    properties.update(fields)
    return {
        "type": "object",
        "required": sorted(
            [
                "id",
                "record_type",
                "recorded_at",
                "schema_name",
                "schema_version",
                "stable_key",
                "status",
                "supersedes_id",
                "workflow_id",
                *required,
            ]
        ),
        "properties": properties,
        "additionalProperties": False,
    }


def added_definitions() -> dict[str, dict]:
    uuid_array = {"type": "array", "items": copy.deepcopy(UUID5), "uniqueItems": True}
    string_array = {"type": "array", "items": {"type": "string"}}
    return {
        "release_snapshot_record": common(
            "release_snapshot",
            {
                "edition_id": copy.deepcopy(UUID5),
                "snapshot_kind": {"type": "string"},
                "release_version": {"type": "string"},
                "release_date": {"type": ["string", "null"]},
                "commit_sha": {"oneOf": [{"type": "string", "pattern": r"^[0-9a-f]{40}$"}, {"type": "null"}]},
                "tree_sha": {"oneOf": [{"type": "string", "pattern": r"^[0-9a-f]{40}$"}, {"type": "null"}]},
                "archive_sha256": copy.deepcopy(NULLABLE_SHA256),
                "artifact_ids": copy.deepcopy(uuid_array),
                "publication_uri": {"type": ["string", "null"]},
                "immutable": {"type": "boolean"},
            },
            [
                "edition_id",
                "snapshot_kind",
                "release_version",
                "release_date",
                "commit_sha",
                "tree_sha",
                "archive_sha256",
                "artifact_ids",
                "publication_uri",
                "immutable",
            ],
        ),
        "route_record": common(
            "route",
            {
                "program_id": copy.deepcopy(UUID5),
                "course_id": copy.deepcopy(NULLABLE_UUID5),
                "route_key": {"type": "string"},
                "route_kind": {"type": "string"},
                "locale": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "version_label": {"type": "string"},
            },
            ["program_id", "course_id", "route_key", "route_kind", "locale", "title", "description", "version_label"],
        ),
        "route_member_record": common(
            "route_member",
            {
                "route_id": copy.deepcopy(UUID5),
                "entity_id": copy.deepcopy(UUID5),
                "ordinal": {"type": "integer", "minimum": 0},
                "order_path": {"type": "string"},
                "role": {"type": "string"},
                "required": {"type": "boolean"},
                "inclusion_reason": {"type": "string"},
            },
            ["route_id", "entity_id", "ordinal", "order_path", "role", "required", "inclusion_reason"],
        ),
        "alignment_record": common(
            "alignment",
            {
                "source_id": copy.deepcopy(UUID5),
                "target_id": copy.deepcopy(UUID5),
                "alignment_kind": {"type": "string"},
                "source_locale": {"type": "string"},
                "target_locale": {"type": "string"},
                "source_sha256": copy.deepcopy(NULLABLE_SHA256),
                "target_sha256": copy.deepcopy(NULLABLE_SHA256),
                "assertion_method": {"type": "string"},
                "confidence": {"type": "string"},
                "evidence_locator": {"type": "string"},
            },
            [
                "source_id",
                "target_id",
                "alignment_kind",
                "source_locale",
                "target_locale",
                "source_sha256",
                "target_sha256",
                "assertion_method",
                "confidence",
                "evidence_locator",
            ],
        ),
        "build_recipe_record": common(
            "build_recipe",
            {
                "resource_id": copy.deepcopy(NULLABLE_UUID5),
                "edition_id": copy.deepcopy(NULLABLE_UUID5),
                "name": {"type": "string"},
                "command": copy.deepcopy(string_array),
                "working_directory": {"type": "string"},
                "input_ids": copy.deepcopy(uuid_array),
                "output_ids": copy.deepcopy(uuid_array),
                "environment": {"type": "object", "additionalProperties": {"type": "string"}},
                "verification": {"type": "object", "additionalProperties": True},
            },
            ["resource_id", "edition_id", "name", "command", "working_directory", "input_ids", "output_ids", "environment", "verification"],
        ),
        "experiment_record": common(
            "experiment",
            {
                "resource_id": copy.deepcopy(UUID5),
                "edition_id": copy.deepcopy(UUID5),
                "unit_id": copy.deepcopy(UUID5),
                "source_file_revision_id": copy.deepcopy(NULLABLE_UUID5),
                "kind": {"type": "string"},
                "invocation": {"type": "string"},
                "runner_asset_revision_ids": copy.deepcopy(uuid_array),
                "instruction_segment_ids": copy.deepcopy(uuid_array),
                "parameter_segment_ids": copy.deepcopy(uuid_array),
                "expected_output_segment_ids": copy.deepcopy(uuid_array),
                "result_mode": {"type": "string"},
                "rights_id": copy.deepcopy(UUID5),
            },
            [
                "resource_id",
                "edition_id",
                "unit_id",
                "source_file_revision_id",
                "kind",
                "invocation",
                "runner_asset_revision_ids",
                "instruction_segment_ids",
                "parameter_segment_ids",
                "expected_output_segment_ids",
                "result_mode",
                "rights_id",
            ],
        ),
    }


ADDED_TABLES = {
    "release_snapshots": "release_snapshot_record",
    "routes": "route_record",
    "route_members": "route_member_record",
    "alignments": "alignment_record",
    "build_recipes": "build_recipe_record",
    "experiments": "experiment_record",
}


def build(kernel: dict) -> dict:
    schema = copy.deepcopy(kernel)
    schema["$id"] = "https://doi.org/10.5281/zenodo.22059707/schema/backend-v1.schema.json"
    schema["title"] = "Interlanguage modular mathematics backend v1"
    schema["description"] = (
        "Strict, corpus-neutral package schema derived from the admitted DMOI structural kernel "
        "and extended for routes, release snapshots, alignments, build recipes, and experiments."
    )
    schema["properties"]["$schema"] = {"const": "schema/backend-v1.schema.json"}
    schema["properties"]["schema_name"] = {"const": SCHEMA_NAME}
    schema["properties"]["schema_version"] = {"const": SCHEMA_VERSION}

    tables = schema["properties"]["tables"]
    for table in tables["properties"].values():
        table["minItems"] = 0

    for definition in schema["$defs"].values():
        if not isinstance(definition, dict) or definition.get("type") != "object":
            continue
        properties = definition.setdefault("properties", {})
        if "schema_name" in properties:
            properties["schema_name"] = {"const": SCHEMA_NAME}
        if "schema_version" in properties:
            properties["schema_version"] = {"const": SCHEMA_VERSION}
        properties["extensions"] = copy.deepcopy(EXTENSIONS)

    schema["$defs"].update(added_definitions())
    for table_name, definition_name in ADDED_TABLES.items():
        tables["properties"][table_name] = {
            "type": "array",
            "minItems": 0,
            "items": {"$ref": f"#/$defs/{definition_name}"},
        }
        tables["required"].append(table_name)

    # A module is both an extractable dependency-closed pack and, when marked,
    # a corpus-local learner route.  The separate route table handles program-
    # level paths spanning multiple resources.
    module = schema["$defs"]["module_record"]["properties"]
    module.update(
        {
            "module_kind": {"type": "string"},
            "course_id": copy.deepcopy(NULLABLE_UUID5),
            "title": {"type": ["string", "null"]},
            "description": {"type": ["string", "null"]},
        }
    )

    tables["required"] = sorted(set(tables["required"]))
    tables["properties"] = dict(sorted(tables["properties"].items()))
    schema["$defs"] = dict(sorted(schema["$defs"].items()))
    return schema


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    kernel = json.loads(args.kernel.read_text(encoding="utf-8"))
    schema = build(kernel)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
