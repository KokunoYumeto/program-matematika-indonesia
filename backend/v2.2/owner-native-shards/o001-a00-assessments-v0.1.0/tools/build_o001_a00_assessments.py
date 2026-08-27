#!/usr/bin/env python3
"""Build the zero-prose O001/A00 CNXML assessment inventory.

The builder reads exactly two owner witness manifests, replays each source
document with an exact ``git show COMMIT:modules/MODULE/index.cnxml`` command,
and reads the corresponding localized target path.  It never copies prose or
formula bodies.  Selected XML subtrees are represented only by native IDs,
stable UUIDv5 IDs, structural tag/class context, byte spans, sizes, and hashes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import uuid
import xml.parsers.expat
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PACKAGE_NAME = "o001-a00-assessments-v0.1.0"
PACKAGE_ID = "urn:uuid:0b253fa5-067e-55b5-8248-cc528b0b4bd1"
SCHEMA_ID = "interlanguage/o001-a00-owner-native-assessment-inventory/1.0.0"
SCHEMA_VERSION = "1.0.0"
RECORDED_AT = "2026-08-28T00:00:00Z"
SOURCE_COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
SOURCE_MANIFEST_REL = (
    "modular_backend/generated/prealgebra2e-volume/metadata/"
    "source-witness-manifest.tsv"
)
TARGET_MANIFEST_REL = (
    "modular_backend/generated/prealgebra2e-volume/metadata/"
    "target-witness-manifest.tsv"
)
SOURCE_MANIFEST_BYTES = 17_907
SOURCE_MANIFEST_SHA256 = (
    "608507fe5ddd9c80715877715d19bf7ce61b01112648a4963f7c81d362e4d5be"
)
TARGET_MANIFEST_BYTES = 8_156
TARGET_MANIFEST_SHA256 = (
    "cd5cb2be648b8cd2bd0eec3fab4184c48f284331f9fb74c17345f96ec1b83abb"
)
EXPECTED = {
    "modules": 75,
    "assessments": 8_105,
    "problems": 8_105,
    "solutions": 5_240,
    "assessment_components": 13_345,
    "solution_gaps": 2_865,
}
ID_NAMESPACE = uuid.UUID("2c1308d9-fe65-5179-a8f3-954f3e8c9da9")
SELECTED_TAGS = {"exercise", "problem", "solution"}
STRUCTURAL_TAGS = {"content", "section", "example", "note", "div", "list", "item"}
FORBIDDEN_PAYLOAD_KEYS = {
    "text",
    "prose",
    "formula",
    "content",
    "body",
    "title",
    "solution_text",
    "problem_text",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def canonical_jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return b"".join(canonical_json_bytes(row) for row in rows)


def stable_id(record_type: str, semantic_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(ID_NAMESPACE, record_type + ':' + semantic_key)}"


def file_fact(path: Path, relative_path: str, role: str, media_type: str) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "bytes": len(data),
        "media_type": media_type,
        "path": relative_path,
        "role": role,
        "sha256": sha256_bytes(data),
    }


def parse_tsv_bytes(data: bytes, expected_headers: list[str]) -> list[dict[str, str]]:
    text = data.decode("utf-8")
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    if reader.fieldnames != expected_headers:
        raise ValueError(f"TSV header mismatch: {reader.fieldnames!r}")
    rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError("TSV contains a malformed row")
    return rows


def class_tokens(attrs: dict[str, str]) -> list[str]:
    return [token for token in attrs.get("class", "").split() if token]


def structural_context(stack: list[dict[str, Any]]) -> dict[str, Any]:
    path: list[dict[str, Any]] = []
    for frame in stack:
        if frame["tag"] not in STRUCTURAL_TAGS:
            continue
        item: dict[str, Any] = {"tag": frame["tag"]}
        native_id = frame["attrs"].get("id")
        classes = class_tokens(frame["attrs"])
        if native_id:
            item["native_id"] = native_id
        if classes:
            item["classes"] = classes
        path.append(item)

    nearest = None
    for item in reversed(path):
        if item.get("classes"):
            nearest = item
            break
    if nearest is None and path:
        nearest = path[-1]
    if nearest is None:
        classification = "document"
    else:
        suffix = ".".join(nearest.get("classes", []))
        classification = nearest["tag"] + (":" + suffix if suffix else "")

    signature_parts = []
    for item in path:
        suffix = ".".join(item.get("classes", []))
        signature_parts.append(item["tag"] + (":" + suffix if suffix else ""))
    return {
        "classification": classification,
        "structural_path": path,
        "structural_signature": ">".join(signature_parts),
    }


class NodeCollector:
    """Collect exact byte spans for selected elements using Expat indices."""

    def __init__(self, raw: bytes, module: str, side: str):
        self.raw = raw
        self.module = module
        self.side = side
        self.stack: list[dict[str, Any]] = []
        self.nodes: list[dict[str, Any]] = []
        self.kind_ordinals: Counter[str] = Counter()
        self.document_order = 0

    def start(self, tag: str, attrs: dict[str, str]) -> None:
        parser = self.parser
        frame: dict[str, Any] = {
            "attrs": dict(attrs),
            "start": parser.CurrentByteIndex,
            "tag": tag,
        }
        if tag in SELECTED_TAGS:
            native_id = attrs.get("id")
            if not native_id:
                raise ValueError(f"{self.module} {self.side} {tag} lacks id")
            self.kind_ordinals[tag] += 1
            self.document_order += 1
            parent_exercise = next(
                (
                    ancestor["attrs"].get("id")
                    for ancestor in reversed(self.stack)
                    if ancestor["tag"] == "exercise"
                ),
                None,
            )
            frame["selected"] = {
                "context": structural_context(self.stack),
                "document_order": self.document_order,
                "kind": tag,
                "kind_ordinal": self.kind_ordinals[tag],
                "native_id": native_id,
                "parent_exercise_native_id": parent_exercise,
                "start": parser.CurrentByteIndex,
            }
        self.stack.append(frame)

    def end(self, tag: str) -> None:
        if not self.stack:
            raise ValueError(f"{self.module} {self.side} unbalanced XML stack")
        frame = self.stack.pop()
        if frame["tag"] != tag:
            raise ValueError(
                f"{self.module} {self.side} XML stack mismatch: {frame['tag']} != {tag}"
            )
        selected = frame.get("selected")
        if selected is None:
            return
        closing_start = self.parser.CurrentByteIndex
        closing_end = self.raw.find(b">", closing_start)
        if closing_end < 0:
            raise ValueError(f"{self.module} {self.side} missing closing tag end")
        end_exclusive = closing_end + 1
        subtree = self.raw[selected["start"] : end_exclusive]
        selected.update(
            {
                "byte_end_exclusive": end_exclusive,
                "byte_start": selected.pop("start"),
                "bytes": len(subtree),
                "sha256": sha256_bytes(subtree),
            }
        )
        self.nodes.append(selected)

    def collect(self) -> list[dict[str, Any]]:
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler = self.start
        self.parser.EndElementHandler = self.end
        self.parser.Parse(self.raw, True)
        if self.stack:
            raise ValueError(f"{self.module} {self.side} XML stack not empty")
        self.nodes.sort(key=lambda node: node["document_order"])
        return self.nodes


def collect_nodes(raw: bytes, module: str, side: str) -> list[dict[str, Any]]:
    return NodeCollector(raw, module, side).collect()


def read_authority(owner_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_manifest_path = owner_root / SOURCE_MANIFEST_REL
    target_manifest_path = owner_root / TARGET_MANIFEST_REL
    source_manifest = source_manifest_path.read_bytes()
    target_manifest = target_manifest_path.read_bytes()
    if len(source_manifest) != SOURCE_MANIFEST_BYTES or sha256_bytes(source_manifest) != SOURCE_MANIFEST_SHA256:
        raise ValueError("source witness manifest byte/hash mismatch")
    if len(target_manifest) != TARGET_MANIFEST_BYTES or sha256_bytes(target_manifest) != TARGET_MANIFEST_SHA256:
        raise ValueError("target witness manifest byte/hash mismatch")

    source_rows = parse_tsv_bytes(
        source_manifest,
        ["ordinal", "module", "bytes", "sha256", "path", "url"],
    )
    target_rows = parse_tsv_bytes(
        target_manifest,
        ["ordinal", "module", "bytes", "sha256", "path"],
    )
    if len(source_rows) != EXPECTED["modules"] or len(target_rows) != EXPECTED["modules"]:
        raise ValueError("witness manifest module count mismatch")
    if [(r["ordinal"], r["module"]) for r in source_rows] != [
        (r["ordinal"], r["module"]) for r in target_rows
    ]:
        raise ValueError("source/target manifest order mismatch")

    modules: list[dict[str, Any]] = []
    aggregate = Counter()
    for source_row, target_row in zip(source_rows, target_rows, strict=True):
        ordinal = int(source_row["ordinal"])
        module = source_row["module"]
        git_path = f"modules/{module}/index.cnxml"
        source_raw = subprocess.check_output(
            ["git", "-C", str(owner_root), "show", f"{SOURCE_COMMIT}:{git_path}"]
        )
        if len(source_raw) != int(source_row["bytes"]) or sha256_bytes(source_raw) != source_row["sha256"]:
            raise ValueError(f"{module} source git-show byte/hash mismatch")
        target_path = owner_root / target_row["path"]
        target_raw = target_path.read_bytes()
        if len(target_raw) != int(target_row["bytes"]) or sha256_bytes(target_raw) != target_row["sha256"]:
            raise ValueError(f"{module} target byte/hash mismatch")

        source_nodes = collect_nodes(source_raw, module, "source")
        target_nodes = collect_nodes(target_raw, module, "target")
        source_counts = Counter(node["kind"] for node in source_nodes)
        target_counts = Counter(node["kind"] for node in target_nodes)
        aggregate.update({f"source_{key}": value for key, value in source_counts.items()})
        aggregate.update({f"target_{key}": value for key, value in target_counts.items()})
        modules.append(
            {
                "module": module,
                "module_ordinal": ordinal,
                "source": {
                    "bytes": len(source_raw),
                    "git_object_path": f"{SOURCE_COMMIT}:{git_path}",
                    "manifest_witness_path": source_row["path"],
                    "sha256": sha256_bytes(source_raw),
                },
                "source_nodes": source_nodes,
                "target": {
                    "bytes": len(target_raw),
                    "owner_relative_path": target_row["path"].replace("\\", "/"),
                    "sha256": sha256_bytes(target_raw),
                },
                "target_nodes": target_nodes,
            }
        )

    authority = {
        "source_commit": SOURCE_COMMIT,
        "source_manifest": {
            "bytes": len(source_manifest),
            "owner_relative_path": SOURCE_MANIFEST_REL,
            "sha256": sha256_bytes(source_manifest),
        },
        "target_manifest": {
            "bytes": len(target_manifest),
            "owner_relative_path": TARGET_MANIFEST_REL,
            "sha256": sha256_bytes(target_manifest),
        },
    }
    return modules, authority


def side_binding(node: dict[str, Any] | None) -> dict[str, Any]:
    if node is None:
        return {"present": False}
    return {
        "byte_end_exclusive": node["byte_end_exclusive"],
        "byte_start": node["byte_start"],
        "bytes": node["bytes"],
        "document_order": node["document_order"],
        "present": True,
        "sha256": node["sha256"],
    }


def index_nodes(nodes: list[dict[str, Any]], module: str, side: str) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for node in nodes:
        key = (node["kind"], node["native_id"])
        if key in result:
            raise ValueError(f"{module} {side} duplicate selected node {key}")
        result[key] = node
    return result


def build_records(modules: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    assessments: list[dict[str, Any]] = []
    components: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []

    for module_data in modules:
        module = module_data["module"]
        module_ordinal = module_data["module_ordinal"]
        source_index = index_nodes(module_data["source_nodes"], module, "source")
        target_index = index_nodes(module_data["target_nodes"], module, "target")
        keys = sorted(
            set(source_index) | set(target_index),
            key=lambda key: (
                min(
                    source_index.get(key, {}).get("document_order", 10**12),
                    target_index.get(key, {}).get("document_order", 10**12),
                ),
                key,
            ),
        )
        exercise_ids = [native_id for kind, native_id in keys if kind == "exercise"]
        context_counts: Counter[str] = Counter()
        module_gap_count = 0

        by_parent_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
        by_parent_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for node in module_data["source_nodes"]:
            if node["kind"] in {"problem", "solution"}:
                by_parent_source[node["parent_exercise_native_id"]].append(node)
        for node in module_data["target_nodes"]:
            if node["kind"] in {"problem", "solution"}:
                by_parent_target[node["parent_exercise_native_id"]].append(node)

        for exercise_ordinal, native_id in enumerate(exercise_ids, start=1):
            source_node = source_index.get(("exercise", native_id))
            target_node = target_index.get(("exercise", native_id))
            context = (source_node or target_node)["context"]
            if source_node and target_node and source_node["context"] != target_node["context"]:
                raise ValueError(f"{module} exercise {native_id} structural context drift")
            context_counts[context["classification"]] += 1
            semantic_key = f"a00:prealgebra2e:{module}:exercise:{native_id}"
            assessment_id = stable_id("assessment", semantic_key)
            source_children = by_parent_source.get(native_id, [])
            target_children = by_parent_target.get(native_id, [])
            child_keys = sorted(
                {
                    (node["kind"], node["native_id"])
                    for node in source_children + target_children
                },
                key=lambda key: (
                    min(
                        source_index.get(key, {}).get("document_order", 10**12),
                        target_index.get(key, {}).get("document_order", 10**12),
                    ),
                    key,
                ),
            )
            problem_component_count = 0
            solution_component_count = 0
            for component_ordinal, (kind, component_native_id) in enumerate(child_keys, start=1):
                if kind not in {"problem", "solution"}:
                    raise ValueError(f"{module} unexpected assessment child kind {kind}")
                component_kind = "statement" if kind == "problem" else "solution"
                component_semantic_key = (
                    f"a00:prealgebra2e:{module}:{kind}:{component_native_id}"
                )
                component_id = stable_id("assessment_component", component_semantic_key)
                if kind == "problem":
                    problem_component_count += 1
                else:
                    solution_component_count += 1
                source_component = source_index.get((kind, component_native_id))
                target_component = target_index.get((kind, component_native_id))
                availability = (
                    "source_and_target"
                    if source_component and target_component
                    else "source_only"
                    if source_component
                    else "target_only"
                )
                components.append(
                    {
                        "assessment_id": assessment_id,
                        "availability": availability,
                        "component_kind": component_kind,
                        "id": component_id,
                        "module": module,
                        "module_ordinal": module_ordinal,
                        "native_id": component_native_id,
                        "native_tag": kind,
                        "ordinal": component_ordinal,
                        "record_type": "assessment_component",
                        "semantic_key": component_semantic_key,
                        "source": side_binding(source_component),
                        "target": side_binding(target_component),
                        "topology_match": bool(
                            source_component
                            and target_component
                            and source_component["parent_exercise_native_id"]
                            == target_component["parent_exercise_native_id"]
                        ),
                    }
                )

            source_solution_count = sum(
                node["kind"] == "solution" for node in source_children
            )
            target_solution_count = sum(
                node["kind"] == "solution" for node in target_children
            )
            if source_solution_count > 1 or target_solution_count > 1:
                raise ValueError(f"{module} exercise {native_id} has multiple solutions")
            if source_solution_count == target_solution_count == 1:
                solution_availability = "available_source_and_target"
            elif source_solution_count == target_solution_count == 0:
                solution_availability = "missing_source_and_target"
            elif source_solution_count:
                solution_availability = "source_only"
            else:
                solution_availability = "target_only"

            assessment = {
                "assessment_kind": "exercise",
                "availability": (
                    "source_and_target"
                    if source_node and target_node
                    else "source_only"
                    if source_node
                    else "target_only"
                ),
                "context_classification": context["classification"],
                "context_structural_signature": context["structural_signature"],
                "id": assessment_id,
                "module": module,
                "module_ordinal": module_ordinal,
                "native_id": native_id,
                "ordinal": exercise_ordinal,
                "problem_component_count": problem_component_count,
                "record_type": "assessment",
                "semantic_key": semantic_key,
                "solution_availability": solution_availability,
                "solution_component_count": solution_component_count,
                "source": side_binding(source_node),
                "target": side_binding(target_node),
                "topology_match": bool(source_node and target_node),
            }
            assessments.append(assessment)

            if solution_availability == "missing_source_and_target":
                module_gap_count += 1
                gap_semantic_key = f"a00:prealgebra2e:{module}:solution-gap:{native_id}"
                gaps.append(
                    {
                        "assessment_id": assessment_id,
                        "context_classification": context["classification"],
                        "gap_kind": "explicit_solution_node_absent",
                        "id": stable_id("solution_gap", gap_semantic_key),
                        "module": module,
                        "module_ordinal": module_ordinal,
                        "native_exercise_id": native_id,
                        "ordinal": module_gap_count,
                        "record_type": "solution_gap",
                        "semantic_key": gap_semantic_key,
                        "source_solution_count": 0,
                        "target_solution_count": 0,
                    }
                )

        source_counts = Counter(node["kind"] for node in module_data["source_nodes"])
        target_counts = Counter(node["kind"] for node in module_data["target_nodes"])
        summaries.append(
            {
                "context_counts": dict(sorted(context_counts.items())),
                "counts": {
                    "assessments": len(exercise_ids),
                    "problems_source": source_counts["problem"],
                    "problems_target": target_counts["problem"],
                    "solutions_source": source_counts["solution"],
                    "solutions_target": target_counts["solution"],
                    "solution_gaps": module_gap_count,
                },
                "module": module,
                "module_ordinal": module_ordinal,
                "record_type": "module_summary",
                "source": module_data["source"],
                "source_target_node_topology_match": [
                    (node["kind"], node["native_id"], node["parent_exercise_native_id"])
                    for node in module_data["source_nodes"]
                ]
                == [
                    (node["kind"], node["native_id"], node["parent_exercise_native_id"])
                    for node in module_data["target_nodes"]
                ],
                "target": module_data["target"],
            }
        )

    assessments.sort(key=lambda row: (row["module_ordinal"], row["ordinal"], row["id"]))
    assessment_order = {
        row["id"]: (row["module_ordinal"], row["ordinal"]) for row in assessments
    }
    components.sort(
        key=lambda row: (
            assessment_order[row["assessment_id"]][0],
            assessment_order[row["assessment_id"]][1],
            row["ordinal"],
            row["id"],
        )
    )
    gaps.sort(key=lambda row: (row["module_ordinal"], row["ordinal"], row["id"]))
    summaries.sort(key=lambda row: row["module_ordinal"])

    if len(assessments) != EXPECTED["assessments"]:
        raise ValueError(f"assessment count mismatch: {len(assessments)}")
    if sum(row["native_tag"] == "problem" for row in components) != EXPECTED["problems"]:
        raise ValueError("problem count mismatch")
    if sum(row["native_tag"] == "solution" for row in components) != EXPECTED["solutions"]:
        raise ValueError("solution count mismatch")
    if len(components) != EXPECTED["assessment_components"]:
        raise ValueError("assessment component count mismatch")
    if len(gaps) != EXPECTED["solution_gaps"]:
        raise ValueError("solution gap count mismatch")
    if not all(row["topology_match"] for row in assessments + components):
        raise ValueError("source/target selected-node topology mismatch")
    if not all(row["source_target_node_topology_match"] for row in summaries):
        raise ValueError("per-module source/target topology mismatch")

    return {
        "assessments": assessments,
        "assessment_components": components,
        "solution_gaps": gaps,
        "module_summaries": summaries,
    }


def schema_document() -> dict[str, Any]:
    binding_properties = {
        "byte_end_exclusive": {"type": "integer", "minimum": 1},
        "byte_start": {"type": "integer", "minimum": 0},
        "bytes": {"type": "integer", "minimum": 1},
        "document_order": {"type": "integer", "minimum": 1},
        "present": {"const": True},
        "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    }
    absent_binding = {
        "type": "object",
        "additionalProperties": False,
        "required": ["present"],
        "properties": {"present": {"const": False}},
    }
    present_binding = {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(binding_properties),
        "properties": binding_properties,
    }
    structural_item = {
        "type": "object",
        "additionalProperties": False,
        "required": ["tag"],
        "properties": {
            "classes": {"type": "array", "items": {"type": "string"}},
            "native_id": {"type": "string"},
            "tag": {"enum": sorted(STRUCTURAL_TAGS)},
        },
    }
    common = {
        "id": {"type": "string", "pattern": "^urn:uuid:[0-9a-f-]{36}$"},
        "module": {"type": "string", "pattern": "^m[0-9]+$"},
        "module_ordinal": {"type": "integer", "minimum": 1, "maximum": 75},
        "ordinal": {"type": "integer", "minimum": 1},
        "semantic_key": {"type": "string", "minLength": 1},
    }
    assessment_properties = {
        **common,
        "assessment_kind": {"const": "exercise"},
        "availability": {
            "enum": ["source_and_target", "source_only", "target_only"]
        },
        "context_classification": {"type": "string", "minLength": 1},
        "context_structural_signature": {"type": "string"},
        "native_id": {"type": "string", "minLength": 1},
        "problem_component_count": {"type": "integer", "minimum": 0},
        "record_type": {"const": "assessment"},
        "solution_availability": {
            "enum": [
                "available_source_and_target",
                "missing_source_and_target",
                "source_only",
                "target_only",
            ]
        },
        "solution_component_count": {"type": "integer", "minimum": 0},
        "source": {"oneOf": [present_binding, absent_binding]},
        "target": {"oneOf": [present_binding, absent_binding]},
        "topology_match": {"type": "boolean"},
    }
    component_properties = {
        **common,
        "assessment_id": common["id"],
        "availability": {
            "enum": ["source_and_target", "source_only", "target_only"]
        },
        "component_kind": {"enum": ["statement", "solution"]},
        "native_id": {"type": "string", "minLength": 1},
        "native_tag": {"enum": ["problem", "solution"]},
        "record_type": {"const": "assessment_component"},
        "source": {"oneOf": [present_binding, absent_binding]},
        "target": {"oneOf": [present_binding, absent_binding]},
        "topology_match": {"type": "boolean"},
    }
    gap_properties = {
        **common,
        "assessment_id": common["id"],
        "context_classification": {"type": "string"},
        "gap_kind": {"const": "explicit_solution_node_absent"},
        "native_exercise_id": {"type": "string"},
        "record_type": {"const": "solution_gap"},
        "source_solution_count": {"const": 0},
        "target_solution_count": {"const": 0},
    }
    module_summary_properties = {
        "context_counts": {
            "type": "object",
            "additionalProperties": {"type": "integer", "minimum": 0},
        },
        "counts": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "assessments",
                "problems_source",
                "problems_target",
                "solution_gaps",
                "solutions_source",
                "solutions_target",
            ],
            "properties": {
                "assessments": {"type": "integer", "minimum": 0},
                "problems_source": {"type": "integer", "minimum": 0},
                "problems_target": {"type": "integer", "minimum": 0},
                "solution_gaps": {"type": "integer", "minimum": 0},
                "solutions_source": {"type": "integer", "minimum": 0},
                "solutions_target": {"type": "integer", "minimum": 0},
            },
        },
        "module": common["module"],
        "module_ordinal": common["module_ordinal"],
        "record_type": {"const": "module_summary"},
        "source": {
            "type": "object",
            "additionalProperties": False,
            "required": ["bytes", "git_object_path", "manifest_witness_path", "sha256"],
            "properties": {
                "bytes": {"type": "integer", "minimum": 1},
                "git_object_path": {"type": "string", "minLength": 1},
                "manifest_witness_path": {"type": "string", "minLength": 1},
                "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            },
        },
        "source_target_node_topology_match": {"const": True},
        "target": {
            "type": "object",
            "additionalProperties": False,
            "required": ["bytes", "owner_relative_path", "sha256"],
            "properties": {
                "bytes": {"type": "integer", "minimum": 1},
                "owner_relative_path": {"type": "string", "minLength": 1},
                "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            },
        },
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://kokunoyumeto.github.io/program-matematika-indonesia/schema/o001-a00-assessment-inventory-v1.schema.json",
        "title": "O001/A00 zero-prose assessment inventory record",
        "oneOf": [
            {
                "type": "object",
                "additionalProperties": False,
                "required": sorted(assessment_properties),
                "properties": assessment_properties,
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": sorted(component_properties),
                "properties": component_properties,
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": sorted(gap_properties),
                "properties": gap_properties,
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": sorted(module_summary_properties),
                "properties": module_summary_properties,
            },
        ],
    }


def readme_text() -> str:
    return """# O001 / A00 owner-native assessment inventory

This deterministic shard inventories the explicit CNXML `exercise`, `problem`,
and `solution` nodes in the frozen OpenStax Prealgebra 2e English source and its
Bahasa Indonesia target. It contains **no mathematical prose, formula bodies,
titles, answers, or solution text**. It records only stable IDs, module/order,
explicit tag/class context, exact byte spans, subtree sizes and SHA-256 hashes,
source/target presence, topology, and solution-availability gaps.

The English source bytes are replayed only with the exact narrow command
`git show 38cae454e644abf9f0a623e876994553881597c9:modules/<module>/index.cnxml`.
Both source and target document bytes must match the two frozen owner witness
manifests before any record is emitted. The owner repository is read-only.

## Files

- `data/assessments.jsonl`: one stable assessment row per explicit exercise.
- `data/assessment-components.jsonl`: problem nodes projected as `statement`
  components and solution nodes projected as `solution` components.
- `data/solution-gaps.jsonl`: exact exercises for which neither source nor
  target contains an explicit solution node.
- `summaries/modules.jsonl`: exact source/target document bindings, structural
  counts, and context counts for each of the 75 modules.
- `manifest.json`: authority, counts, projection contract, and file inventory.
- `CHECKSUMS.sha256` and `seal.json`: a non-circular package seal. The checksum
  file binds every content file including the manifest, but excludes itself and
  the seal. The seal binds the checksum file and excludes itself.

## Projection into common backend v2.2

This is an owner-native O001 infrastructure shard, not a mutation of the sealed
`a00-openstax-prealgebra-v0.1.0` package. A later aggregate adapter resolves each
`module` to that package's existing navigation `unit_id`, then projects:

- each `assessment` row to the optional v2.2 `assessments` capability;
- each `problem` row to `assessment_components.component_kind=statement`;
- each `solution` row to `assessment_components.component_kind=solution`;
- source/target byte-span hashes to content/native bindings;
- the explicit missing-solution rows to capability-loss/gap reporting.

The stable UUIDv5 IDs may be retained. Rights IDs, learner routes, and unit IDs
must be resolved from the sealed A00 lane package at integration time rather
than guessed here. No assessment content is promoted to a learner-navigation
unit, and no missing solution is invented.

## Replay

From this package directory:

```powershell
python -B tools/build_o001_a00_assessments.py --owner-root <openstax-prealgebra> --output <build-dir>
python -B tools/validate_o001_a00_assessments.py --owner-root <openstax-prealgebra> --package-root <build-dir>
```

Two builds from the same frozen inputs must be byte-identical for every file.
"""


def ensure_no_forbidden_payload(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_PAYLOAD_KEYS:
                raise ValueError(f"forbidden payload key at {path}.{key}")
            ensure_no_forbidden_payload(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            ensure_no_forbidden_payload(child, f"{path}[{index}]")
    elif isinstance(value, str):
        if "<m:" in value or "<math" in value or "<para" in value:
            raise ValueError(f"forbidden markup payload at {path}")


def reset_output(output: Path, protected: list[Path]) -> None:
    resolved = output.resolve()
    if len(resolved.parts) < 4 or resolved == resolved.anchor:
        raise ValueError(f"refusing unsafe output path: {resolved}")
    if any(resolved == item.resolve() for item in protected):
        raise ValueError(f"refusing protected output path: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    (resolved / "data").mkdir(parents=True)
    (resolved / "schema").mkdir(parents=True)
    (resolved / "summaries").mkdir(parents=True)
    (resolved / "tools").mkdir(parents=True)


def write_package(owner_root: Path, output: Path) -> dict[str, Any]:
    builder_source = Path(__file__).read_bytes()
    validator_path = Path(__file__).with_name("validate_o001_a00_assessments.py")
    validator_source = validator_path.read_bytes()
    modules, authority = read_authority(owner_root)
    records = build_records(modules)
    for rows in records.values():
        ensure_no_forbidden_payload(rows)

    reset_output(output, [owner_root, owner_root.parent])
    output = output.resolve()
    generated: dict[str, bytes] = {
        "README.md": readme_text().replace("\r\n", "\n").encode("utf-8"),
        "data/assessments.jsonl": canonical_jsonl_bytes(records["assessments"]),
        "data/assessment-components.jsonl": canonical_jsonl_bytes(
            records["assessment_components"]
        ),
        "data/solution-gaps.jsonl": canonical_jsonl_bytes(records["solution_gaps"]),
        "schema/assessment-inventory-v1.schema.json": canonical_json_bytes(
            schema_document()
        ),
        "summaries/modules.jsonl": canonical_jsonl_bytes(records["module_summaries"]),
        "tools/build_o001_a00_assessments.py": builder_source.replace(b"\r\n", b"\n"),
        "tools/validate_o001_a00_assessments.py": validator_source.replace(
            b"\r\n", b"\n"
        ),
    }
    for relative_path, data in generated.items():
        destination = output / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)

    counts = {
        "assessment_components": len(records["assessment_components"]),
        "assessments": len(records["assessments"]),
        "modules": len(records["module_summaries"]),
        "problems": sum(
            row["native_tag"] == "problem" for row in records["assessment_components"]
        ),
        "solutions": sum(
            row["native_tag"] == "solution" for row in records["assessment_components"]
        ),
        "solution_gaps": len(records["solution_gaps"]),
    }
    validation_report = {
        "authority_document_hashes": "pass",
        "counts": counts,
        "expected_counts": EXPECTED,
        "forbidden_payload_audit": "pass",
        "schema_id": SCHEMA_ID,
        "source_replay": "pass",
        "source_target_selected_node_topology": "pass",
        "target_replay": "pass",
        "validation_state": "pass",
        "zero_prose": "pass",
    }
    (output / "validation-report.json").write_bytes(canonical_json_bytes(validation_report))

    role_by_path = {
        "README.md": ("documentation", "text/markdown"),
        "data/assessments.jsonl": ("assessment_table", "application/x-ndjson"),
        "data/assessment-components.jsonl": (
            "assessment_component_table",
            "application/x-ndjson",
        ),
        "data/solution-gaps.jsonl": ("gap_table", "application/x-ndjson"),
        "schema/assessment-inventory-v1.schema.json": (
            "schema",
            "application/schema+json",
        ),
        "summaries/modules.jsonl": ("module_summary_table", "application/x-ndjson"),
        "tools/build_o001_a00_assessments.py": ("builder", "text/x-python"),
        "tools/validate_o001_a00_assessments.py": ("validator", "text/x-python"),
        "validation-report.json": ("validation_report", "application/json"),
    }
    file_inventory = []
    for relative_path in sorted(role_by_path):
        role, media_type = role_by_path[relative_path]
        file_inventory.append(file_fact(output / relative_path, relative_path, role, media_type))

    manifest = {
        "authority": authority,
        "build": {
            "canonical_serialization": {
                "encoding": "UTF-8",
                "json_keys": "lexicographically_sorted",
                "jsonl_order": "module_then_document_order",
                "newline": "LF",
                "trailing_newline": True,
            },
            "replay_commands": [
                "python -B tools/build_o001_a00_assessments.py --owner-root <owner> --output <build>",
                "python -B tools/validate_o001_a00_assessments.py --owner-root <owner> --package-root <build>",
            ],
            "two_build_requirement": "all_files_byte_identical",
        },
        "counts": counts,
        "files": file_inventory,
        "identity": {
            "formula": "UUIDv5(namespace, record_type + ':' + semantic_key)",
            "namespace": str(ID_NAMESPACE),
        },
        "package_id": PACKAGE_ID,
        "package_name": PACKAGE_NAME,
        "projection_contract": {
            "assessment_component_mapping": {
                "problem": "statement",
                "solution": "solution",
            },
            "common_capabilities": ["assessments", "assessment_components"],
            "integration_policy": "resolve module to sealed A00 unit; preserve owner-native IDs and bindings",
            "sealed_v22_package_mutated": False,
            "unit_id_resolution": "deferred_to_common_adapter",
        },
        "recorded_at": RECORDED_AT,
        "schema": {
            "$ref": "schema/assessment-inventory-v1.schema.json",
            "schema_id": SCHEMA_ID,
            "schema_version": SCHEMA_VERSION,
        },
        "seal_policy": {
            "checksum_file": "CHECKSUMS.sha256",
            "checksum_file_excludes": ["CHECKSUMS.sha256", "seal.json"],
            "manifest_self_hash_excluded_from_manifest": True,
            "seal_excluded_from_own_digest": True,
            "seal_file": "seal.json",
        },
        "zero_prose_policy": {
            "allowed": [
                "stable IDs",
                "module and order",
                "explicit structural tags/classes/IDs",
                "byte spans, sizes, and SHA-256",
                "presence, topology, and gap state",
            ],
            "copied_formula_bodies": False,
            "copied_mathematical_prose": False,
        },
    }
    (output / "manifest.json").write_bytes(canonical_json_bytes(manifest))

    bound_paths = sorted(
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
        and path.relative_to(output).as_posix() not in {"CHECKSUMS.sha256", "seal.json"}
    )
    checksum_lines = []
    total_bytes = 0
    for relative_path in bound_paths:
        data = (output / relative_path).read_bytes()
        total_bytes += len(data)
        checksum_lines.append(f"{sha256_bytes(data)}  {relative_path}\n")
    checksum_bytes = "".join(checksum_lines).encode("utf-8")
    (output / "CHECKSUMS.sha256").write_bytes(checksum_bytes)
    seal = {
        "algorithm": "sha256-sorted-relative-path-bytes-v1",
        "bound_file_count": len(bound_paths),
        "bound_paths": bound_paths,
        "bound_total_bytes": total_bytes,
        "checksum_manifest_bytes": len(checksum_bytes),
        "checksum_manifest_path": "CHECKSUMS.sha256",
        "checksum_manifest_sha256": sha256_bytes(checksum_bytes),
        "excluded_from_checksum_manifest": ["CHECKSUMS.sha256", "seal.json"],
        "package_id": PACKAGE_ID,
        "seal_excluded_from_own_digest": True,
    }
    (output / "seal.json").write_bytes(canonical_json_bytes(seal))
    return {"counts": counts, "seal": seal}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = write_package(args.owner_root.resolve(), args.output.resolve())
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
