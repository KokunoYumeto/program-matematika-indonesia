#!/usr/bin/env python3
"""Losslessly adapt the complete O005/C120 native backend to common v1.

The owner lane is immutable authority.  Every native unit, segment, mastery
problem, project, and stable-segment-ID binding receives exactly one common-v1
record carrying the complete native payload in a namespaced extension.  The
adapter adds common text variants and translation alignments, plus the minimum
rights/resource/course/edition/file anchors required by the shared schema.

No common-backend copy is materialized.  Exact owner-file bytes are retained
virtually in file-record extensions, and two independent reads/assemblies must
produce byte-identical canonical common backends before a receipt is written.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_NAME = "interlanguage-math-modular-backend"
SCHEMA_VERSION = "1.0.0"
RECEIPT_SCHEMA_NAME = "interlanguage-math-modular-backend-migration-receipt"
WORKFLOW = "program-matematika-indonesia/o005-c120-v1-adapter-1.0.0"
RECORDED_AT = "2026-08-23T17:24:37Z"
NAMESPACE = uuid.uuid5(
    uuid.NAMESPACE_URL,
    "https://doi.org/10.5281/zenodo.22059939#interlanguage-backend-v1",
)
NATIVE_EXTENSION = "interlanguage.o005-native"
FILE_EXTENSION = "interlanguage.o005-file"
DERIVED_EXTENSION = "interlanguage.o005-derived"
UUID_URN_RE = re.compile(
    r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

EXPECTED_BACKEND_COMMIT = "1f7e7c9a180f450d91352d1b117094f07f1158ae"
EXPECTED_BACKEND_COMMIT_TREE = "30e651d225ea716f7295a0adf3cd3b7cdd7e73b7"
EXPECTED_BACKEND_GIT_TREE = "b19efc503a4544135337ff75cf622b1daac4eefa"
EXPECTED_BACKEND_FILES = 81
EXPECTED_BACKEND_BYTES = 3_270_308
EXPECTED_BACKEND_INVENTORY_SHA256 = "848dbeccf74352f12e6cca15863f94132708405b8e9bd742844020a1f3fd33c9"
EXPECTED_NATIVE_COUNTS = {
    "unit": 26,
    "segment": 4_105,
    "mastery_problem": 141,
    "project": 12,
    "segment_id_binding": 657,
}
EXPECTED_SOURCE_SEGMENTS = 3_448
EXPECTED_BRIDGE_SEGMENTS = 657
EXPECTED_VARIANTS = 7_553
EXPECTED_ALIGNMENTS = 3_448
EXPECTED_CONTROL = {
    "00_control/ZENODO_PUBLICATION_RECEIPT_CANONICAL_20260823.json": (
        3_236,
        "6cb1962c5e14668c2be86284b78e182b4f8951a1f5d9baafcd937ae25906cab9",
    ),
    "00_control/RECOVERY_POINTER.json": (
        3_992,
        "d0a5f3ad7eba01c6bfe4371938932a0ea9d21847ba8686ed9cbe1365c47a60a5",
    ),
    "00_control/COMPLETION_AUDIT_20260823.md": (
        8_552,
        "ee3027238fff3e8378d288f50834520360d8c0f6146df50e1ca0c2efe8e9da78",
    ),
    "00_control/RIGHTS_AND_PROVENANCE.md": (
        21_619,
        "e60a44718b75b18a6a6fbcba1c8fa8ab6c9d9b53cb1dee65452ea4023fd8d512",
    ),
}


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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_value(owner_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(owner_root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def rid(record_type: str, stable_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(NAMESPACE, f'{record_type}|{stable_key}')}"


def base(record_type: str, stable_key: str, status: str = "active", **fields: Any) -> dict:
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


def exact_file(path: Path, expected_bytes: int, expected_sha256: str, label: str) -> bytes:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    raw = path.read_bytes()
    if len(raw) != expected_bytes:
        raise ValueError(f"{label} byte mismatch: {len(raw)} != {expected_bytes}")
    actual = sha256_bytes(raw)
    if actual != expected_sha256:
        raise ValueError(f"{label} SHA-256 mismatch: {actual} != {expected_sha256}")
    return raw


def validate_json(instance: Any, schema: dict, label: str) -> None:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise ValueError(f"{label}: {list(first.absolute_path)}: {first.message}")


def inventory_rows(files: dict[str, bytes]) -> list[str]:
    return [
        f"{path}\t{len(raw)}\t{sha256_bytes(raw)}"
        for path, raw in sorted(files.items())
    ]


def inventory_sha256(files: dict[str, bytes]) -> str:
    payload = ("\n".join(inventory_rows(files)) + "\n").encode("utf-8")
    return sha256_bytes(payload)


def native_inventory_rows(entries: list[dict]) -> list[str]:
    rows = []
    for entry in entries:
        ordinal = "" if entry["source_ordinal"] is None else str(entry["source_ordinal"])
        rows.append(
            "\t".join(
                [
                    entry["native_kind"],
                    entry["native_id"],
                    entry["source_path"],
                    ordinal,
                    sha256_bytes(canonical_bytes(entry["payload"])),
                ]
            )
        )
    return sorted(rows)


def native_inventory_sha256(entries: list[dict]) -> str:
    return sha256_bytes(("\n".join(native_inventory_rows(entries)) + "\n").encode("utf-8"))


def native_extension(entry: dict) -> dict:
    return {
        "canonical_payload_sha256": sha256_bytes(canonical_bytes(entry["payload"])),
        "disposition": "direct-lossless-native-extension",
        "native_id": entry["native_id"],
        "native_kind": entry["native_kind"],
        "payload": entry["payload"],
        "source_ordinal": entry["source_ordinal"],
        "source_path": entry["source_path"],
    }


def source_entry(kind: str, native_id: str, source_path: str, ordinal: int | None, payload: dict) -> dict:
    return {
        "native_kind": kind,
        "native_id": native_id,
        "source_path": source_path,
        "source_ordinal": ordinal,
        "payload": payload,
    }


@dataclass(frozen=True)
class SourceSnapshot:
    owner_root: Path
    backend_files: dict[str, bytes]
    control_files: dict[str, dict]
    units: tuple[dict, ...]
    segments: tuple[dict, ...]
    mastery_problems: tuple[dict, ...]
    projects: tuple[dict, ...]
    bindings: tuple[dict, ...]
    native_entries: tuple[dict, ...]
    publication: dict
    recovery: dict
    diagnostics: dict


def source_schema(owner_root: Path, name: str) -> dict:
    value = load_json(owner_root / "backend" / "schema" / name)
    Draft202012Validator.check_schema(value)
    return value


def load_source(owner_root: Path) -> SourceSnapshot:
    owner_root = owner_root.resolve()
    backend_commit = git_value(owner_root, "log", "-1", "--format=%H", "--", "backend")
    backend_commit_tree = git_value(owner_root, "show", "-s", "--format=%T", backend_commit)
    backend_git_tree = git_value(owner_root, "rev-parse", "HEAD:backend")
    if (
        backend_commit != EXPECTED_BACKEND_COMMIT
        or backend_commit_tree != EXPECTED_BACKEND_COMMIT_TREE
        or backend_git_tree != EXPECTED_BACKEND_GIT_TREE
    ):
        raise ValueError(
            "owner backend Git authority changed: "
            f"{backend_commit}/{backend_commit_tree}/{backend_git_tree}"
        )
    status = git_value(owner_root, "status", "--porcelain", "--", "backend")
    if status:
        raise ValueError("owner backend is not clean at the frozen authority head")

    backend_root = owner_root / "backend"
    backend_files = {
        path.relative_to(owner_root).as_posix(): path.read_bytes()
        for path in sorted(backend_root.rglob("*"))
        if path.is_file()
    }
    backend_bytes = sum(map(len, backend_files.values()))
    backend_hash = inventory_sha256(backend_files)
    if len(backend_files) != EXPECTED_BACKEND_FILES:
        raise ValueError(f"backend file count changed: {len(backend_files)}")
    if backend_bytes != EXPECTED_BACKEND_BYTES:
        raise ValueError(f"backend bytes changed: {backend_bytes}")
    if backend_hash != EXPECTED_BACKEND_INVENTORY_SHA256:
        raise ValueError(f"backend inventory changed: {backend_hash}")
    tracked = set(git_value(owner_root, "ls-tree", "-r", "--name-only", "HEAD", "--", "backend").splitlines())
    if tracked != set(backend_files):
        raise ValueError("frozen Git backend path inventory differs from live backend inventory")

    control_files: dict[str, dict] = {}
    for relative, (size, digest) in EXPECTED_CONTROL.items():
        raw = exact_file(owner_root / relative, size, digest, relative)
        control_files[relative] = {"bytes": len(raw), "sha256": sha256_bytes(raw)}
    publication = load_json(owner_root / "00_control/ZENODO_PUBLICATION_RECEIPT_CANONICAL_20260823.json")
    recovery = load_json(owner_root / "00_control/RECOVERY_POINTER.json")
    if publication.get("record_id") != 22070943 or publication.get("doi") != "10.5281/zenodo.22070943":
        raise ValueError("canonical O005 publication identity changed")
    coverage = publication.get("coverage", {})
    expected_coverage = {
        "status": "complete",
        "source_units": 22,
        "bridge_units": 4,
        "source_segments": EXPECTED_SOURCE_SEGMENTS,
        "bridge_segments": EXPECTED_BRIDGE_SEGMENTS,
        "total_segments": EXPECTED_SOURCE_SEGMENTS + EXPECTED_BRIDGE_SEGMENTS,
        "mastery_records": EXPECTED_NATIVE_COUNTS["mastery_problem"],
        "notebooks": 26,
        "projects": EXPECTED_NATIVE_COUNTS["project"],
        "pdf_pages": 355,
    }
    if coverage != expected_coverage:
        raise ValueError(f"canonical publication coverage changed: {coverage}")
    if recovery.get("status") != "complete_reader_published_zenodo_canonical_figshare_blocked":
        raise ValueError("recovery pointer no longer identifies the complete canonical reader")

    for public_file in publication["files"]:
        local = owner_root / publication["release_package"]["path"] / public_file["name"]
        exact_file(local, public_file["bytes"], public_file["sha256"], f"release artifact {public_file['name']}")

    unit_schema = source_schema(owner_root, "o005-unit.schema.json")
    bridge_unit_schema = source_schema(owner_root, "o005-bridge-unit.schema.json")
    segment_schema = source_schema(owner_root, "o005-segment.schema.json")
    bridge_segment_schema = source_schema(owner_root, "o005-bridge-segment.schema.json")
    ledger_schema = source_schema(owner_root, "o005-segment-id-ledger.schema.json")
    bridge_mastery_schema = source_schema(owner_root, "o005-bridge-mastery.schema.json")

    units: list[dict] = []
    unit_by_id: dict[str, dict] = {}
    unit_path_by_id: dict[str, str] = {}
    for path in sorted((backend_root / "units").glob("*.json")):
        relative = path.relative_to(owner_root).as_posix()
        value = json.loads(backend_files[relative])
        schema = bridge_unit_schema if value.get("schema") == "o005-bridge-unit-v1" else unit_schema
        validate_json(value, schema, relative)
        unit_id = value["unit_id"]
        if unit_id in unit_by_id or path.stem != unit_id:
            raise ValueError(f"duplicate or filename-mismatched unit {unit_id}")
        unit_by_id[unit_id] = value
        unit_path_by_id[unit_id] = relative
        units.append(source_entry("unit", unit_id, relative, None, value))
    if len(units) != EXPECTED_NATIVE_COUNTS["unit"]:
        raise ValueError(f"unit count mismatch: {len(units)}")

    segments: list[dict] = []
    segment_by_id: dict[str, dict] = {}
    segment_ids_by_unit: dict[str, list[str]] = defaultdict(list)
    segment_native_by_unit: dict[str, list[dict]] = defaultdict(list)
    source_segment_count = 0
    bridge_segment_count = 0
    for path in sorted((backend_root / "segments").glob("*.jsonl")):
        relative = path.relative_to(owner_root).as_posix()
        raw = backend_files[relative]
        if raw and not raw.endswith(b"\n"):
            raise ValueError(f"JSONL lacks terminal LF: {relative}")
        lines = raw.decode("utf-8").splitlines()
        for line_number, line in enumerate(lines, start=1):
            if not line:
                raise ValueError(f"blank JSONL row: {relative}:{line_number}")
            value = json.loads(line)
            bridge = value.get("schema") == "o005-bridge-segment-v1"
            validate_json(value, bridge_segment_schema if bridge else segment_schema, f"{relative}:{line_number}")
            segment_id = value["segment_id"]
            unit_id = value["unit_id"]
            if segment_id in segment_by_id:
                raise ValueError(f"duplicate segment ID {segment_id}")
            if unit_id not in unit_by_id:
                raise ValueError(f"segment names unknown unit {unit_id}")
            if value["ordinal"] != len(segment_ids_by_unit[unit_id]) + 1:
                raise ValueError(f"non-contiguous segment ordinal {segment_id}")
            if bridge:
                bridge_segment_count += 1
                text = value["canonical_text"]
                if sha256_bytes(text.encode("utf-8")) != value["canonical_sha256"]:
                    raise ValueError(f"bridge segment text hash mismatch {segment_id}")
            else:
                source_segment_count += 1
                for text_field, hash_field in (
                    ("source_text", "source_sha256"),
                    ("target_text", "target_sha256"),
                ):
                    if sha256_bytes(value[text_field].encode("utf-8")) != value[hash_field]:
                        raise ValueError(f"segment text hash mismatch {segment_id}:{text_field}")
            entry = source_entry("segment", segment_id, relative, line_number, value)
            segment_by_id[segment_id] = value
            segment_ids_by_unit[unit_id].append(segment_id)
            segment_native_by_unit[unit_id].append(entry)
            segments.append(entry)
    if source_segment_count != EXPECTED_SOURCE_SEGMENTS or bridge_segment_count != EXPECTED_BRIDGE_SEGMENTS:
        raise ValueError(f"segment census mismatch: {source_segment_count}+{bridge_segment_count}")
    for unit_id, unit in unit_by_id.items():
        declared = unit["segments"]
        relative = declared["path"]
        if relative not in backend_files:
            raise ValueError(f"unit segment path missing: {unit_id}:{relative}")
        if declared["count"] != len(segment_ids_by_unit[unit_id]):
            raise ValueError(f"unit segment count mismatch: {unit_id}")
        if declared["sha256"] != sha256_bytes(backend_files[relative]):
            raise ValueError(f"unit segment file hash mismatch: {unit_id}")

    mastery_problems: list[dict] = []
    problem_ids: set[str] = set()
    for path in sorted((backend_root / "mastery").glob("*.json")):
        relative = path.relative_to(owner_root).as_posix()
        value = json.loads(backend_files[relative])
        if value.get("schema") == "o005-bridge-mastery-v1":
            validate_json(value, bridge_mastery_schema, relative)
        unit_id = value.get("unit_id")
        if unit_id not in unit_by_id:
            raise ValueError(f"mastery file names unknown unit: {unit_id}")
        links = {row["link_id"] for row in value.get("article_link_catalog", [])}
        current_ids = []
        for ordinal, problem in enumerate(value.get("problems", []), start=1):
            problem_id = problem.get("problem_id")
            if not isinstance(problem_id, str) or problem_id in problem_ids:
                raise ValueError(f"missing or duplicate mastery problem ID in {relative}")
            if problem.get("ordinal") != ordinal:
                raise ValueError(f"non-contiguous mastery ordinal {problem_id}")
            if not set(problem.get("article_link_ids", [])).issubset(links):
                raise ValueError(f"mastery problem has unknown article link {problem_id}")
            problem_ids.add(problem_id)
            current_ids.append(problem_id)
            mastery_problems.append(source_entry("mastery_problem", problem_id, relative, ordinal, problem))
        if unit_by_id[unit_id].get("problems", []) != current_ids:
            raise ValueError(f"unit/mastery problem inventory mismatch: {unit_id}")
        declared_path = unit_by_id[unit_id].get("mastery_path")
        if declared_path and (declared_path != relative or unit_by_id[unit_id]["mastery_sha256"] != sha256_bytes(backend_files[relative])):
            raise ValueError(f"unit/mastery file binding mismatch: {unit_id}")
    if len(mastery_problems) != EXPECTED_NATIVE_COUNTS["mastery_problem"]:
        raise ValueError(f"mastery problem count mismatch: {len(mastery_problems)}")

    projects: list[dict] = []
    project_ids: set[str] = set()
    project_files = sorted((backend_root / "projects").glob("*.json"))
    if len(project_files) != 1:
        raise ValueError(f"expected one project catalog, found {len(project_files)}")
    project_path = project_files[0]
    project_relative = project_path.relative_to(owner_root).as_posix()
    project_catalog = json.loads(backend_files[project_relative])
    rows = project_catalog.get("projects", [])
    if project_catalog.get("project_count") != len(rows):
        raise ValueError("project catalog count mismatch")
    if project_catalog.get("project_order") != [row.get("project_id") for row in rows]:
        raise ValueError("project catalog order mismatch")
    for ordinal, project in enumerate(rows, start=1):
        project_id = project.get("project_id")
        if not isinstance(project_id, str) or project_id in project_ids:
            raise ValueError("missing or duplicate project ID")
        project_ids.add(project_id)
        projects.append(source_entry("project", project_id, project_relative, ordinal, project))
    project_unit = unit_by_id[project_catalog["unit_id"]]
    declared_projects = project_unit.get("projects", {})
    if (
        declared_projects.get("catalog_path") != project_relative
        or declared_projects.get("count") != len(rows)
        or declared_projects.get("catalog_sha256") != sha256_bytes(backend_files[project_relative])
    ):
        raise ValueError("unit/project catalog binding mismatch")
    if len(projects) != EXPECTED_NATIVE_COUNTS["project"]:
        raise ValueError(f"project count mismatch: {len(projects)}")

    bindings: list[dict] = []
    binding_ids: set[str] = set()
    for path in sorted((backend_root / "segment-ids").glob("*.json")):
        relative = path.relative_to(owner_root).as_posix()
        value = json.loads(backend_files[relative])
        validate_json(value, ledger_schema, relative)
        unit_id = value["unit_id"]
        if unit_id not in unit_by_id or unit_by_id[unit_id]["schema"] != "o005-bridge-unit-v1":
            raise ValueError(f"segment-ID ledger names non-bridge unit {unit_id}")
        ledger_ids = []
        for ordinal, binding in enumerate(value["entries"], start=1):
            segment_id = binding["segment_id"]
            if segment_id in binding_ids:
                raise ValueError(f"duplicate stable-ID binding {segment_id}")
            if segment_id not in segment_by_id or segment_by_id[segment_id]["unit_id"] != unit_id:
                raise ValueError(f"stable-ID binding does not close to bridge segment {segment_id}")
            binding_ids.add(segment_id)
            ledger_ids.append(segment_id)
            bindings.append(source_entry("segment_id_binding", segment_id, relative, ordinal, binding))
        if ledger_ids != segment_ids_by_unit[unit_id]:
            raise ValueError(f"ledger/segment order mismatch: {unit_id}")
    if len(bindings) != EXPECTED_NATIVE_COUNTS["segment_id_binding"]:
        raise ValueError(f"binding count mismatch: {len(bindings)}")

    native_entries = [*units, *segments, *mastery_problems, *projects, *bindings]
    counts = dict(Counter(entry["native_kind"] for entry in native_entries))
    if counts != EXPECTED_NATIVE_COUNTS:
        raise ValueError(f"native logical record census changed: {counts}")
    direct_keys = [(entry["native_kind"], entry["native_id"]) for entry in native_entries]
    if len(direct_keys) != len(set(direct_keys)):
        raise ValueError("native logical record keys are not unique")

    diagnostics = {
        "owner_backend_commit": backend_commit,
        "owner_backend_commit_tree": backend_commit_tree,
        "owner_backend_git_tree": backend_git_tree,
        "backend_file_count": len(backend_files),
        "backend_bytes": backend_bytes,
        "backend_inventory_bytes": len(("\n".join(inventory_rows(backend_files)) + "\n").encode("utf-8")),
        "backend_inventory_sha256": backend_hash,
        "native_record_counts": counts,
        "native_record_count": len(native_entries),
        "native_record_inventory_sha256": native_inventory_sha256(native_entries),
        "source_segments": source_segment_count,
        "bridge_segments": bridge_segment_count,
        "native_schema_files": len(list((backend_root / "schema").glob("*.json"))),
        "native_schema_validation": "all applicable unit, segment, bridge-mastery, and ledger records pass",
        "native_reference_closure": "pass",
        "canonical_publication_receipt": control_files[
            "00_control/ZENODO_PUBLICATION_RECEIPT_CANONICAL_20260823.json"
        ],
    }
    return SourceSnapshot(
        owner_root=owner_root,
        backend_files=backend_files,
        control_files=control_files,
        units=tuple(units),
        segments=tuple(segments),
        mastery_problems=tuple(mastery_problems),
        projects=tuple(projects),
        bindings=tuple(bindings),
        native_entries=tuple(native_entries),
        publication=publication,
        recovery=recovery,
        diagnostics=diagnostics,
    )


def source_unit_id_for_path(source: SourceSnapshot, path: str) -> str:
    for entry in source.units:
        if entry["source_path"] == path:
            return entry["native_id"]
    raise ValueError(f"cannot resolve unit from {path}")


def build_backend(source: SourceSnapshot, schema: dict) -> tuple[dict, dict]:
    table_names = schema["properties"]["tables"]["required"]
    tables: dict[str, list[dict]] = {name: [] for name in table_names}

    rights_key = "o005:rights:cc-by-nc-sa-4.0"
    resource_key = "o005:resource:lega-v1.01"
    program_key = "o005:program:bahasa-indonesia"
    course_key = "o005:course:C120"
    source_edition_key = "o005:edition:source-v1.01"
    target_edition_key = "o005:edition:id-complete-r5"
    rights_id = rid("rights", rights_key)
    resource_id = rid("resource", resource_key)
    program_id = rid("program", program_key)
    course_id = rid("course", course_key)
    source_edition_id = rid("edition", source_edition_key)
    target_edition_id = rid("edition", target_edition_key)

    rights_notice = source.control_files["00_control/RIGHTS_AND_PROVENANCE.md"]
    tables["rights"].append(
        base(
            "rights",
            rights_key,
            "verified",
            assertion_status="verified-owner-lane",
            attribution="Joceline Lega; Indonesian edition preserves the complete owner-lane attribution and provenance notices.",
            authority="O005 frozen rights and provenance control",
            change_notice="Indonesian translation plus explicitly marked original bridge, mastery, and computational material.",
            license_expression="CC-BY-NC-SA-4.0",
            nonendorsement="No endorsement by the original author or institution is implied.",
            notice_locator="00_control/RIGHTS_AND_PROVENANCE.md",
            notice_sha256=rights_notice["sha256"],
            source_component_id="O005",
            third_party_status="tracked in the frozen owner-lane authority",
            extensions={DERIVED_EXTENSION: {"disposition": "additive-common-anchor"}},
        )
    )
    tables["resources"].append(
        base(
            "resource",
            resource_key,
            "complete",
            authority_policy="frozen owner-lane authority plus canonical Zenodo publication receipt",
            creator_name="Joceline Lega",
            official_reader="https://opentextbooks.library.arizona.edu/mathematicalmodeling/",
            official_repository="https://github.com/KokunoYumeto/mathematical-modeling-nonlinear-dynamics-id",
            original_title="Introduction to Mathematical Modeling",
            resource_key="O005",
            work_type="open textbook and Indonesian modular edition",
            extensions={DERIVED_EXTENSION: {"disposition": "additive-common-anchor", "course_role": "C120"}},
        )
    )
    tables["programs"].append(
        base(
            "program",
            program_key,
            "active",
            curriculum_version="0.48.0",
            locale="id-ID",
            program_key="program-matematika-indonesia",
            rights_id=rights_id,
            title="Program Matematika Bahasa Indonesia",
            extensions={DERIVED_EXTENSION: {"disposition": "additive-common-anchor"}},
        )
    )
    tables["courses"].append(
        base(
            "course",
            course_key,
            "complete",
            course_key="C120",
            order_key="C120",
            program_id=program_id,
            role="Mathematical modeling and nonlinear dynamics",
            title="Pengantar Pemodelan Matematika",
            resource_keys=["O005"],
            extensions={DERIVED_EXTENSION: {"disposition": "additive-common-anchor"}},
        )
    )
    tables["editions"].extend(
        [
            base(
                "edition",
                source_edition_key,
                "frozen",
                archive_sha256="6622c9e8fabe3a96e5c4df2836c464ec0d465a5f1acadc2235141cdbf6fb3ec6",
                commit_sha=source.diagnostics["owner_backend_commit"],
                edition_kind="official-source-snapshot",
                locale="en",
                release_date="2026-03",
                resource_id=resource_id,
                rights_id=rights_id,
                source_edition_id=None,
                tree_sha=source.diagnostics["owner_backend_commit_tree"],
                vcs_ref="official-v1.01-frozen-in-owner-snapshot",
                vcs_type="snapshot",
                version_label="v1.01",
                extensions={DERIVED_EXTENSION: {"disposition": "additive-common-anchor"}},
            ),
            base(
                "edition",
                target_edition_key,
                "published",
                archive_sha256="0350d0dc9530c877c3ebcbb84d3cfe7f73654eaeb59bfad46f4ddf61d9446d72",
                commit_sha=source.diagnostics["owner_backend_commit"],
                edition_kind="complete-Indonesian-reader",
                locale="id-ID",
                release_date="2026-08-23",
                resource_id=resource_id,
                rights_id=rights_id,
                source_edition_id=source_edition_id,
                tree_sha=source.diagnostics["owner_backend_commit_tree"],
                vcs_ref="https://doi.org/10.5281/zenodo.22070943",
                vcs_type="git-plus-zenodo",
                version_label=source.publication["version"],
                extensions={DERIVED_EXTENSION: {"disposition": "additive-common-anchor"}},
            ),
        ]
    )

    for relative, raw in sorted(source.backend_files.items()):
        suffix = Path(relative).suffix.lower()
        tables["files"].append(
            base(
                "file",
                f"o005:file:{relative}",
                "frozen",
                canonical_path=relative,
                media_type="application/x-ndjson" if suffix == ".jsonl" else "application/json",
                parse_mode="json-lines" if suffix == ".jsonl" else "json",
                resource_id=resource_id,
                role="native-backend-authority",
                extensions={
                    FILE_EXTENSION: {
                        "bytes": len(raw),
                        "disposition": "additive-exact-file-anchor",
                        "raw_bytes_base64": base64.b64encode(raw).decode("ascii"),
                        "sha256": sha256_bytes(raw),
                        "source_path": relative,
                    }
                },
            )
        )

    common_unit_ids: dict[str, str] = {}
    for entry in source.units:
        payload = entry["payload"]
        unit_id = entry["native_id"]
        stable_key = f"o005:unit:{unit_id}"
        common_unit_ids[unit_id] = rid("unit", stable_key)
        is_bridge = payload["schema"] == "o005-bridge-unit-v1"
        source_meta = payload.get("source", {})
        source_label = source_meta.get("chapter") or payload.get("target", {}).get("title")
        source_path = payload.get("target", {}).get("content_path") or entry["source_path"]
        tables["units"].append(
            base(
                "unit",
                stable_key,
                "complete",
                first_edition_id=target_edition_id,
                identity_anchor=unit_id,
                identity_basis="stable native O005 unit_id",
                resource_id=resource_id,
                rights_default_id=rights_id,
                source_label=source_label,
                source_local_id=unit_id,
                source_path=source_path,
                source_xml_path=None,
                unit_kind="original-bridge" if is_bridge else payload.get("unit_type", "source-derived-unit"),
                extensions={NATIVE_EXTENSION: native_extension(entry)},
            )
        )

    common_segment_ids: dict[str, str] = {}
    source_variant_ids: dict[str, str] = {}
    target_variant_ids: dict[str, str] = {}
    for entry in source.segments:
        payload = entry["payload"]
        segment_id = entry["native_id"]
        stable_key = f"o005:segment:{segment_id}"
        common_segment_id = rid("segment", stable_key)
        common_segment_ids[segment_id] = common_segment_id
        bridge = payload["schema"] == "o005-bridge-segment-v1"
        tables["segments"].append(
            base(
                "segment",
                stable_key,
                payload.get("status", "active"),
                identity_anchor=segment_id,
                ordinal=payload["ordinal"],
                segment_kind="canonical-html-text" if bridge else "bilingual-html-text",
                segmentation_profile=payload["schema"],
                unit_id=common_unit_ids[payload["unit_id"]],
                extensions={NATIVE_EXTENSION: native_extension(entry)},
            )
        )
        if bridge:
            variant_key = f"o005:variant:{segment_id}:id-ID"
            variant_id = rid("segment_variant", variant_key)
            target_variant_ids[segment_id] = variant_id
            tables["segment_variants"].append(
                base(
                    "segment_variant",
                    variant_key,
                    payload.get("status", "active"),
                    edition_id=target_edition_id,
                    format="text/plain",
                    locale=payload["canonical_language"],
                    payload=payload["canonical_text"],
                    payload_sha256=payload["canonical_sha256"],
                    rights_id=rights_id,
                    role="original-canonical",
                    segment_id=common_segment_id,
                    source_variant_id=None,
                    translation_state="original",
                    extensions={DERIVED_EXTENSION: {"native_segment_id": segment_id, "projection": "canonical_text"}},
                )
            )
        else:
            source_key = f"o005:variant:{segment_id}:en"
            target_key = f"o005:variant:{segment_id}:id-ID"
            source_variant_id = rid("segment_variant", source_key)
            target_variant_id = rid("segment_variant", target_key)
            source_variant_ids[segment_id] = source_variant_id
            target_variant_ids[segment_id] = target_variant_id
            tables["segment_variants"].extend(
                [
                    base(
                        "segment_variant",
                        source_key,
                        "source",
                        edition_id=source_edition_id,
                        format="text/plain",
                        locale=payload["source_language"],
                        payload=payload["source_text"],
                        payload_sha256=payload["source_sha256"],
                        rights_id=rights_id,
                        role="source",
                        segment_id=common_segment_id,
                        source_variant_id=None,
                        translation_state="source",
                        extensions={DERIVED_EXTENSION: {"native_segment_id": segment_id, "projection": "source_text"}},
                    ),
                    base(
                        "segment_variant",
                        target_key,
                        payload.get("status", "translated"),
                        edition_id=target_edition_id,
                        format="text/plain",
                        locale=payload["target_language"],
                        payload=payload["target_text"],
                        payload_sha256=payload["target_sha256"],
                        rights_id=rights_id,
                        role="translation",
                        segment_id=common_segment_id,
                        source_variant_id=source_variant_id,
                        translation_state=payload.get("status", "translated"),
                        extensions={DERIVED_EXTENSION: {"native_segment_id": segment_id, "projection": "target_text"}},
                    ),
                ]
            )
            alignment_key = f"o005:alignment:{segment_id}:en-id-ID"
            tables["alignments"].append(
                base(
                    "alignment",
                    alignment_key,
                    "verified",
                    alignment_kind="one-to-one-native-bilingual-segment",
                    assertion_method="native O005 segment record",
                    confidence="exact",
                    evidence_locator=f"{entry['source_path']}#line={entry['source_ordinal']}",
                    source_id=source_variant_id,
                    source_locale=payload["source_language"],
                    source_sha256=payload["source_sha256"],
                    target_id=target_variant_id,
                    target_locale=payload["target_language"],
                    target_sha256=payload["target_sha256"],
                    extensions={DERIVED_EXTENSION: {"native_segment_id": segment_id, "projection": "bilingual_alignment"}},
                )
            )

    unit_for_mastery_path: dict[str, str] = {}
    for unit_entry in source.units:
        mastery_path = unit_entry["payload"].get("mastery_path")
        if mastery_path:
            unit_for_mastery_path[mastery_path] = unit_entry["native_id"]
    for entry in source.mastery_problems:
        problem = entry["payload"]
        unit_id = unit_for_mastery_path[entry["source_path"]]
        stable_key = f"o005:mastery:{entry['native_id']}"
        tables["modules"].append(
            base(
                "module",
                stable_key,
                "complete",
                closure_profile="complete-native-mastery-problem",
                course_id=course_id,
                description=problem["problem_summary"],
                edition_id=target_edition_id,
                locale="id-ID",
                manifest_sha256=sha256_bytes(canonical_bytes(problem)),
                module_kind="mastery-problem-with-hint-check-and-solution-or-rubric",
                module_version="o005-mastery-v1",
                root_unit_id=common_unit_ids[unit_id],
                title=entry["native_id"],
                extensions={NATIVE_EXTENSION: native_extension(entry)},
            )
        )

    project_unit_id = None
    for unit_entry in source.units:
        if unit_entry["payload"].get("projects", {}).get("catalog_path") == "backend/projects/O005-LEGA-V101-CH14.projects.json":
            project_unit_id = unit_entry["native_id"]
            break
    if project_unit_id is None:
        raise ValueError("cannot resolve project unit")
    for entry in source.projects:
        project = entry["payload"]
        stable_key = f"o005:project:{entry['native_id']}"
        tables["experiments"].append(
            base(
                "experiment",
                stable_key,
                "complete",
                edition_id=target_edition_id,
                expected_output_segment_ids=[],
                instruction_segment_ids=[],
                invocation=project["notebook_path"],
                kind="independent-open-modeling-project",
                parameter_segment_ids=[],
                resource_id=resource_id,
                result_mode="synthetic-or-model-generated-only; no cited-paper result reproduction claim",
                rights_id=rights_id,
                runner_asset_revision_ids=[],
                source_file_revision_id=None,
                unit_id=common_unit_ids[project_unit_id],
                extensions={NATIVE_EXTENSION: native_extension(entry)},
            )
        )

    ledger_meta: dict[str, dict] = {}
    for path in sorted((source.owner_root / "backend/segment-ids").glob("*.json")):
        relative = path.relative_to(source.owner_root).as_posix()
        ledger_meta[relative] = json.loads(source.backend_files[relative])
    for entry in source.bindings:
        binding = entry["payload"]
        ledger = ledger_meta[entry["source_path"]]
        stable_key = f"o005:segment-id-binding:{entry['native_id']}"
        tables["qa_events"].append(
            base(
                "qa_event",
                stable_key,
                binding.get("state", "active"),
                input_hash=binding["slot_binding_sha256"],
                method=ledger["binding_algorithm"],
                qa_type="stable-segment-id-binding",
                result=binding.get("state", "active"),
                reviewer_kind="deterministic-native-ledger",
                severity_p1=0,
                severity_p2=0,
                severity_p3=0,
                tool_name="o005-segment-id-ledger",
                tool_version=str(ledger["ledger_version"]),
                witness_locator=f"{entry['source_path']}#entries/{entry['source_ordinal'] - 1}",
                extensions={NATIVE_EXTENSION: native_extension(entry)},
            )
        )

    for rows in tables.values():
        rows.sort(key=lambda row: row["id"])
    backend = {
        "$schema": "schema/backend-v1.schema.json",
        "dataset_id": rid("dataset", "o005-c120-id"),
        "dataset_version": f"{source.publication['version']}+interlanguage-v1.0.0",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "tables": tables,
    }
    mapping = {
        "direct_native_records": len(source.native_entries),
        "direct_native_by_kind": source.diagnostics["native_record_counts"],
        "exact_file_anchors": len(source.backend_files),
        "common_anchor_records": 6,
        "derived_segment_variants": len(tables["segment_variants"]),
        "derived_translation_alignments": len(tables["alignments"]),
        "direct_table_mapping": {
            "unit": "units",
            "segment": "segments",
            "mastery_problem": "modules",
            "project": "experiments",
            "segment_id_binding": "qa_events",
        },
    }
    return backend, mapping


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


def privacy_scan(value: Any) -> dict:
    payload = canonical(value)
    forbidden_name = "".join(chr(code) for code in (70, 108, 111, 114, 105, 115))
    windows_user_root = "".join(chr(code) for code in (67, 58, 92, 85, 115, 101, 114, 115, 92))
    posix_user_root = "".join(chr(code) for code in (67, 58, 47, 85, 115, 101, 114, 115, 47))
    needles = [forbidden_name, windows_user_root, posix_user_root, ".codex", "access_token", "authorization: bearer"]
    hits = [index for index, needle in enumerate(needles) if needle.lower() in payload.lower()]
    if hits:
        raise ValueError(f"private-marker scan failed ({len(hits)} marker classes)")
    return {"marker_classes_scanned": len(needles), "private_marker_hits": 0}


def validate_backend(backend: dict, schema: dict, source: SourceSnapshot, mapping: dict) -> dict:
    validate_json(backend, schema, "strict common backend")
    tables = backend["tables"]
    if set(tables) != set(schema["properties"]["tables"]["required"]):
        raise ValueError("common table inventory is not exactly 38/38")
    records = [record for table in sorted(tables) for record in tables[table]]
    ids = [record["id"] for record in records]
    stable_keys = [record["stable_key"] for record in records]
    if len(ids) != len(set(ids)) or len(stable_keys) != len(set(stable_keys)):
        raise ValueError("common ID or stable-key uniqueness failure")
    known = set(ids)
    allowed_external = {"supersedes_id", "source_edition_id", "source_revision_id", "source_occurrence_id"}
    dangling = []
    for record in records:
        for field_path, value in referenced_uuid_urns(record):
            if field_path == ("id",):
                continue
            leaf = field_path[-1] if field_path else ""
            if value not in known and leaf not in allowed_external:
                dangling.append({"record": record["id"], "field": "/".join(field_path), "value": value})
                if len(dangling) >= 10:
                    break
        if dangling:
            break
    if dangling:
        raise ValueError(f"common foreign-key closure failure: {dangling}")

    extracted_entries = []
    for record in records:
        native = record.get("extensions", {}).get(NATIVE_EXTENSION)
        if native:
            extracted_entries.append(
                source_entry(
                    native["native_kind"],
                    native["native_id"],
                    native["source_path"],
                    native["source_ordinal"],
                    native["payload"],
                )
            )
    if len(extracted_entries) != mapping["direct_native_records"]:
        raise ValueError("direct native/common record coverage mismatch")
    if native_inventory_rows(extracted_entries) != native_inventory_rows(list(source.native_entries)):
        raise ValueError("exact native logical-record reverse extraction failed")

    reconstructed_files: dict[str, bytes] = {}
    for record in tables["files"]:
        extension = record["extensions"][FILE_EXTENSION]
        raw = base64.b64decode(extension["raw_bytes_base64"], validate=True)
        relative = extension["source_path"]
        if len(raw) != extension["bytes"] or sha256_bytes(raw) != extension["sha256"]:
            raise ValueError(f"file anchor self-check failed: {relative}")
        reconstructed_files[relative] = raw
    if reconstructed_files != source.backend_files:
        raise ValueError("exact native backend byte reconstruction failed")
    if inventory_sha256(reconstructed_files) != EXPECTED_BACKEND_INVENTORY_SHA256:
        raise ValueError("reconstructed native backend inventory hash mismatch")

    if len(tables["segment_variants"]) != EXPECTED_VARIANTS:
        raise ValueError("derived segment-variant census mismatch")
    if len(tables["alignments"]) != EXPECTED_ALIGNMENTS:
        raise ValueError("derived translation-alignment census mismatch")
    variant_by_id = {record["id"]: record for record in tables["segment_variants"]}
    for alignment in tables["alignments"]:
        source_variant = variant_by_id[alignment["source_id"]]
        target_variant = variant_by_id[alignment["target_id"]]
        if source_variant["payload_sha256"] != alignment["source_sha256"]:
            raise ValueError("alignment/source payload hash mismatch")
        if target_variant["payload_sha256"] != alignment["target_sha256"]:
            raise ValueError("alignment/target payload hash mismatch")
        if target_variant["source_variant_id"] != source_variant["id"]:
            raise ValueError("translation variant source pointer mismatch")

    table_hashes = {}
    global_hash = hashlib.sha256()
    global_bytes = 0
    for table_name in sorted(tables):
        payload = b"".join((canonical(row) + "\n").encode("utf-8") for row in tables[table_name])
        global_hash.update(payload)
        global_bytes += len(payload)
        table_hashes[table_name] = {
            "records": len(tables[table_name]),
            "virtual_jsonl_bytes": len(payload),
            "virtual_jsonl_sha256": sha256_bytes(payload),
        }
    privacy = privacy_scan(backend)
    return {
        "record_count": len(records),
        "table_count": len(tables),
        "nonempty_table_count": sum(bool(rows) for rows in tables.values()),
        "global_unique_ids": len(set(ids)),
        "global_unique_stable_keys": len(set(stable_keys)),
        "foreign_key_closure": "pass",
        "strict_schema": "pass",
        "direct_native_records_reversed": len(extracted_entries),
        "exact_native_backend_files_reconstructed": len(reconstructed_files),
        "exact_native_backend_bytes_reconstructed": sum(map(len, reconstructed_files.values())),
        "native_record_inventory_sha256": native_inventory_sha256(extracted_entries),
        "native_backend_inventory_sha256": inventory_sha256(reconstructed_files),
        "derived_segment_variants": len(tables["segment_variants"]),
        "derived_translation_alignments": len(tables["alignments"]),
        "virtual_records_jsonl_bytes": global_bytes,
        "virtual_records_jsonl_sha256": global_hash.hexdigest(),
        "canonical_backend_sha256": sha256_bytes(canonical_bytes(backend)),
        "table_hashes": table_hashes,
        **privacy,
    }


def portable_public_artifacts(source: SourceSnapshot) -> list[dict]:
    result = [
        {
            "path": "00_control/ZENODO_PUBLICATION_RECEIPT_CANONICAL_20260823.json",
            "bytes": EXPECTED_CONTROL["00_control/ZENODO_PUBLICATION_RECEIPT_CANONICAL_20260823.json"][0],
            "sha256": EXPECTED_CONTROL["00_control/ZENODO_PUBLICATION_RECEIPT_CANONICAL_20260823.json"][1],
            "status": "public_bytes_verified_by_frozen_owner-receipt",
            "doi": source.publication["doi"],
        }
    ]
    release_path = source.publication["release_package"]["path"]
    for row in source.publication["files"]:
        result.append(
            {
                "path": f"{release_path}/{row['name']}",
                "bytes": row["bytes"],
                "sha256": row["sha256"],
                "status": "public_bytes_verified_by_frozen_owner-receipt",
                "public_url": (
                    f"https://zenodo.org/api/records/{source.publication['record_id']}/files/"
                    f"{quote(row['name'])}/content"
                ),
            }
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--receipt-schema", required=True, type=Path)
    parser.add_argument("--output-receipt", required=True, type=Path)
    args = parser.parse_args()

    schema_path = args.schema.resolve()
    receipt_schema_path = args.receipt_schema.resolve()
    schema = load_json(schema_path)
    receipt_schema = load_json(receipt_schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(receipt_schema)

    first_source = load_source(args.corpus_root)
    first_backend, first_mapping = build_backend(first_source, schema)
    first_validation = validate_backend(first_backend, schema, first_source, first_mapping)

    second_source = load_source(args.corpus_root)
    if first_source.diagnostics != second_source.diagnostics:
        raise ValueError("owner authority changed between independent reads")
    if first_source.backend_files != second_source.backend_files:
        raise ValueError("owner backend bytes changed between independent reads")
    second_backend, second_mapping = build_backend(second_source, schema)
    second_validation = validate_backend(second_backend, schema, second_source, second_mapping)
    if canonical_bytes(first_backend) != canonical_bytes(second_backend):
        raise ValueError("two independent common-backend assemblies are not byte-identical")
    if first_mapping != second_mapping or first_validation != second_validation:
        raise ValueError("two independent mapping/validation results differ")

    source_files = {
        path: {"bytes": len(raw), "sha256": sha256_bytes(raw)}
        for path, raw in sorted(first_source.backend_files.items())
    }
    receipt = {
        "schema_name": RECEIPT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "migration_id": "o005-c120-id-v1.01-complete-r5-to-interlanguage-v1.0.0",
        "migration_mode": "lossless-zero-copy-one-to-one-native-record-adapter-with-additive-common-projections",
        "source": {
            "dataset_id": "O005/C120",
            "dataset_version": first_source.publication["version"],
            "schema_name": "o005-native-backend-family",
            "schema_version": "1.0.0",
            "completion": "complete-reader-published-and-anonymously-byte-verified",
            "owner_backend_commit": first_source.diagnostics["owner_backend_commit"],
            "owner_backend_commit_tree": first_source.diagnostics["owner_backend_commit_tree"],
            "owner_backend_git_tree": first_source.diagnostics["owner_backend_git_tree"],
            "backend_root": "backend",
            "backend_file_count": first_source.diagnostics["backend_file_count"],
            "backend_bytes": first_source.diagnostics["backend_bytes"],
            "backend_inventory_bytes": first_source.diagnostics["backend_inventory_bytes"],
            "backend_inventory_sha256": first_source.diagnostics["backend_inventory_sha256"],
            "backend_files": source_files,
            "native_record_count": first_source.diagnostics["native_record_count"],
            "native_record_counts": first_source.diagnostics["native_record_counts"],
            "native_record_inventory_sha256": first_source.diagnostics["native_record_inventory_sha256"],
            "control_authority_files": first_source.control_files,
            "zenodo_record_id": first_source.publication["record_id"],
            "zenodo_version_doi": first_source.publication["doi"],
            "zenodo_concept_doi": first_source.publication["concept_doi"],
            "reader_pages": first_source.publication["coverage"]["pdf_pages"],
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
            "canonical_backend_sha256": first_validation["canonical_backend_sha256"],
        },
        "coverage": {
            **first_source.diagnostics,
            **first_mapping,
            "course_role_id": "C120",
            "source_units": 22,
            "bridge_units": 4,
            "source_segments": EXPECTED_SOURCE_SEGMENTS,
            "bridge_segments": EXPECTED_BRIDGE_SEGMENTS,
            "mastery_records": EXPECTED_NATIVE_COUNTS["mastery_problem"],
            "projects": EXPECTED_NATIVE_COUNTS["project"],
            "notebooks": 26,
            "reader_pages": 355,
            "source_and_component_rights_preserved": True,
            "projection_limitations": [
                "Mastery-file envelopes and article-link catalogs remain byte-exact in common file anchors; only the 141 declared mastery problem records are promoted to standalone common modules.",
                "Project subfile inventories remain losslessly embedded in the 12 direct project extensions; they are not duplicated as common asset/file-revision records.",
                "The common backend is a deterministic virtual projection, not a second materialized copy; consumers replay the adapter against the pinned 81-file owner backend.",
                "Public identity is inherited from the frozen canonical Zenodo receipt; this migration performs no new network publication or public-byte readback.",
            ],
        },
        "transformation": {
            "native_files_modified": 0,
            "native_records_modified": 0,
            "native_records_preserved_in_extensions": first_mapping["direct_native_records"],
            "native_payload_fields_preserved": "all fields of every native logical record",
            "native_record_inventory_reconstructable": True,
            "native_backend_files_byte_reconstructable": True,
            "native_backend_bytes_changed": 0,
            "derived_identity_algorithm": "UUIDv5(namespace, record_type|stable_key)",
            "derived_segment_variants": first_mapping["derived_segment_variants"],
            "derived_translation_alignments": first_mapping["derived_translation_alignments"],
            "additive_exact_file_anchors": first_mapping["exact_file_anchors"],
            "additive_common_anchor_records": first_mapping["common_anchor_records"],
            "direct_table_mapping": first_mapping["direct_table_mapping"],
            "derived_records_materialized": False,
        },
        "validation": {
            "result": "pass",
            "owner_backend_clean_at_frozen_head": "pass",
            "owner_git_backend_path_inventory": "81/81 exact",
            "native_backend_filename_size_sha256": "pass",
            "native_backend_inventory_sha256": first_validation["native_backend_inventory_sha256"],
            "native_schema_validation": first_source.diagnostics["native_schema_validation"],
            "native_reference_closure": first_source.diagnostics["native_reference_closure"],
            "native_text_hashes": "4,105/4,105 pass",
            "native_unit_segment_file_bindings": "26/26 pass",
            "native_mastery_unit_bindings": "16/16 files and 141/141 problems pass",
            "native_project_unit_binding": "12/12 pass",
            "native_segment_id_ledger_bindings": "657/657 pass",
            "exact_native_logical_record_reverse_extraction": first_validation[
                "direct_native_records_reversed"
            ],
            "exact_native_backend_file_byte_reconstruction": first_validation[
                "exact_native_backend_files_reconstructed"
            ],
            "exact_native_backend_byte_reconstruction": first_validation[
                "exact_native_backend_bytes_reconstructed"
            ],
            "strict_common_backend_schema": first_validation["strict_schema"],
            "common_global_id_uniqueness": first_validation["global_unique_ids"],
            "common_global_stable_key_uniqueness": first_validation["global_unique_stable_keys"],
            "common_foreign_key_closure": first_validation["foreign_key_closure"],
            "common_table_inventory": "38/38 present",
            "derived_segment_variant_payload_hashes": f"{EXPECTED_VARIANTS}/{EXPECTED_VARIANTS} pass",
            "derived_translation_alignment_hashes": f"{EXPECTED_ALIGNMENTS}/{EXPECTED_ALIGNMENTS} pass",
            "two_independent_authority_reads": 2,
            "two_independent_assemblies": "byte-identical",
            "first_canonical_backend_sha256": first_validation["canonical_backend_sha256"],
            "second_canonical_backend_sha256": second_validation["canonical_backend_sha256"],
            "first_virtual_records_jsonl_sha256": first_validation["virtual_records_jsonl_sha256"],
            "second_virtual_records_jsonl_sha256": second_validation["virtual_records_jsonl_sha256"],
            "private_marker_hits": first_validation["private_marker_hits"],
            "marker_classes_scanned": first_validation["marker_classes_scanned"],
        },
        "tables": first_validation["table_hashes"],
        "materialization": {
            "status": "not duplicated locally",
            "reason": "The frozen 81-file native backend plus this deterministic reversible adapter reconstruct the strict common backend twice; the receipt records hashes without creating a redundant common-backend copy.",
            "script_path": "scripts/migrate-o005-backend-v1.py",
            "test_path": "scripts/test-o005-backend-v1.py",
        },
        "public_artifacts": portable_public_artifacts(first_source),
        "credentials_recorded": False,
    }
    privacy_scan(receipt)
    validate_json(receipt, receipt_schema, "migration receipt")
    receipt_bytes = pretty_bytes(receipt)
    args.output_receipt.parent.mkdir(parents=True, exist_ok=True)
    args.output_receipt.write_bytes(receipt_bytes)
    if args.output_receipt.read_bytes() != receipt_bytes:
        raise ValueError("migration receipt byte readback mismatch")
    print(
        canonical(
            {
                "result": "pass",
                "native_records": first_mapping["direct_native_records"],
                "target_records": first_validation["record_count"],
                "tables": first_validation["table_count"],
                "nonempty_tables": first_validation["nonempty_table_count"],
                "canonical_backend_sha256": first_validation["canonical_backend_sha256"],
                "virtual_records_jsonl_sha256": first_validation["virtual_records_jsonl_sha256"],
                "receipt": "backend/migrations/o005-c120-id-v1/MIGRATION_RECEIPT.json",
                "receipt_bytes": len(receipt_bytes),
                "receipt_sha256": sha256_bytes(receipt_bytes),
            }
        )
    )


if __name__ == "__main__":
    main()
