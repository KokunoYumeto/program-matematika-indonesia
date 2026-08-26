#!/usr/bin/env python3
"""Validate the additive v2.1 unit/search pilot packages.

The validator is deliberately independent of :mod:`build_pilots`.  It reads
only the small pilot directories and the input-authority paths named by each
manifest; it never edits an owner tree.  ``validation_report.json`` is
written beside each package and is intentionally *not* part of the manifest
inventory, so the report cannot make its own validation circular.

The pilot contract is a compact projection, not a copy of textbook prose.
This validator therefore checks both the byte/hash manifest and a few safety
properties that are easy to lose when a new producer is added: canonical
JSONL, stable record counts/IDs, HTTPS learner routes, and absence of prose
payload fields.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlparse


PILOTS_ROOT = Path(__file__).resolve().parent
# ``build_pilots.py`` derives this from the file's ``parents[3]``.  Here the
# starting object is the directory, so the equivalent program-repository
# parent is ``parents[2]`` (v2.1 -> backend -> repository).
PROGRAM_ROOT = PILOTS_ROOT.parents[2]
OWNER_ROOT = PROGRAM_ROOT.parent
REPORT_NAME = "validation_report.json"

JSONL_FILES = {
    "units.jsonl": "units",
    "search.jsonl": "search_documents",
    "relations.jsonl": "relations",
}
EXPECTED_RECORD_TYPES = {
    "units.jsonl": "unit",
    "search.jsonl": "search_document",
    "relations.jsonl": "relation",
}
ROLE_COUNT_KEYS = {
    "stable_unit_registry": "units",
    "compact_search_shard": "search_documents",
    "evidence_bound_relations": "relations",
    "rights_accessibility_summary": "rights_accessibility_documents",
    "learner_route_readback_evidence": "route_readback_documents",
    "learner_route_materialization_evidence": "route_materialization_documents",
}

EXPECTED_PACKAGES = {
    "a00-prealgebra": {"course_id": "A00", "units": 75, "search_documents": 75, "relations": 201},
    "b10-dmoi": {"course_id": "B10", "units": 161, "search_documents": 161, "relations": 284},
    "c100-geometry": {"course_id": "C100", "units": 939, "search_documents": 939, "relations": 994},
    "d20-functional-analysis": {"course_id": "D20", "units": 19, "search_documents": 19, "relations": 686},
}
EXPECTED_CORE_HASHES = {
    "a00-prealgebra": {
        "units.jsonl": "16c5e057f48d460fcbee42853e716e8537d587ba6a09953dc84c11496d943948",
        "relations.jsonl": "49ea805c2d0f8ce8d1be226a06b7aaedcefaed0de564387ebedd34d2d8075628",
        "search.jsonl": "71e70bd4d538e5fad3798117b60d81a1bcf04cd8be39f76c9f4ec580b2f43a98",
        "rights_accessibility.json": "fda5233372c820eb0cc6ab7a5139b015206d031cc19da573286552df95219285",
    },
    "b10-dmoi": {
        "units.jsonl": "80d79c94d7a780d7b8a5b317ca68c07fac25f21abf2f331747f12eed6db4c91d",
        "relations.jsonl": "0ca7768415609146c554bef2228b6cde52d3df605088b117acfa246c9ca7553d",
        "search.jsonl": "e08fb76866be2c58827f015caec3d378f053a1eb2f43cf05d990eabdfe5475b9",
        "rights_accessibility.json": "2e0c51ab3086aafc6cfe26cfd106d0e85469f5d5a95a8a7df605443549ccf2ae",
    },
    "d20-functional-analysis": {
        "units.jsonl": "90bb317d1e083471ac7bea94acd8e25734782a5857c4544a298e98e3ad1f8602",
        "relations.jsonl": "d96a127e18cda636e67db5fd9a5b1bfa9057ba429ec69836cd0aacb258910a8e",
        "search.jsonl": "4cefb887eab2cd8bd7656c2778ce25d378d55f25a4859f0c35b0b3b67e9f5879",
        "rights_accessibility.json": "6b83978ab877d8e2008b0bc40cd6fc2af63df47ea9c76be6495e095104386fa9",
    },
}

# These names denote a copied payload rather than a compact structural
# projection.  ``search_text`` and title/label fields remain deliberately
# allowed because they are bounded navigation metadata.
PROSE_KEYS = {
    "prose",
    "body",
    "body_html",
    "content",
    "content_html",
    "html",
    "html_text",
    "latex",
    "markdown",
    "raw_html",
    "raw_text",
    "source_text",
    "target_text",
    "text_payload",
    "translation_payload",
}
LONG_VALUE_ALLOWED_KEYS = {
    "decision",
    "description_state",
    "license_expression",
    "locator",
    "local_evidence_locator",
    "materialization_scope",
    "route_state",
    "source_locator_state",
    "state",
    "third_party_status",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ValidationError(Exception):
    """Internal exception used for a single package check."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def load_json(path: Path) -> Any:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValidationError(f"UTF-8 BOM is not allowed: {path.name}")
    try:
        text = raw.decode("utf-8")
        value = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid UTF-8/JSON: {path.name}: {exc}") from exc
    return value


def safe_relative_path(value: Any, field: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{field} must be a non-empty POSIX relative path")
    if "\\" in value:
        raise ValidationError(f"{field} contains a backslash: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValidationError(f"{field} is not a safe relative path: {value!r}")
    return path


def iter_regular_files(root: Path) -> Iterable[Path]:
    # Pilot packages are intentionally tiny.  Keeping traversal confined to
    # the package root avoids any repository/workspace-wide enumeration.
    for path in sorted(root.rglob("*")):
        if path.is_file():
            yield path


def authority_path(locator: str, locator_base: str) -> Path | None:
    """Resolve a manifest authority locator when it is a local path.

    URL authorities are evidence references, not local files; their syntax is
    checked but they are not fetched by this offline validator.
    """

    if re.match(r"^[a-z][a-z0-9+.-]*://", locator, re.IGNORECASE):
        return None
    relative = safe_relative_path(locator, "input_authority.locator")
    if locator_base == "program_repository_root":
        return PROGRAM_ROOT.joinpath(*relative.parts)
    if locator_base == "owner_root":
        return OWNER_ROOT.joinpath(*relative.parts)
    raise ValidationError(f"unsupported input_authority.locator_base: {locator_base!r}")


def validate_authorities(manifest: dict[str, Any], errors: list[str], facts: list[dict[str, Any]]) -> None:
    authorities = manifest.get("input_authority")
    if not isinstance(authorities, list) or not authorities:
        errors.append("manifest.input_authority must be a non-empty list")
        return
    standalone_c100_projection = (
        manifest.get("course_id") == "C100"
        and manifest.get("standalone_replay_mode") == "committed_hash_bound_projection_validation_when_owner_corpus_is_not_adjacent"
        and not (OWNER_ROOT / "foundations-of-geometry-id").exists()
    )
    for index, item in enumerate(authorities):
        prefix = f"input_authority[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} is not an object")
            continue
        locator = item.get("locator")
        locator_base = item.get("locator_base")
        expected_sha = item.get("sha256")
        expected_bytes = item.get("bytes")
        if not isinstance(expected_sha, str) or not SHA256_RE.fullmatch(expected_sha):
            errors.append(f"{prefix}.sha256 is not a lowercase SHA-256")
            continue
        if not isinstance(expected_bytes, int) or expected_bytes < 0:
            errors.append(f"{prefix}.bytes is not a non-negative integer")
            continue
        if not isinstance(locator, str) or not locator:
            errors.append(f"{prefix}.locator is missing")
            continue
        try:
            local = authority_path(locator, locator_base)
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        if local is None:
            parsed = urlparse(locator)
            if parsed.scheme != "https":
                errors.append(f"{prefix}.locator URL is not HTTPS: {locator}")
            continue
        if not local.is_file() or local.is_symlink():
            if standalone_c100_projection and locator_base == "owner_root" and locator.startswith("foundations-of-geometry-id/"):
                facts.append({
                    "bytes": expected_bytes,
                    "locator": locator,
                    "sha256": expected_sha,
                    "validation_state": "declared_owner_authority_identity_retained; owner corpus intentionally absent from standalone central release",
                })
                continue
            errors.append(f"{prefix} local authority missing or not a regular file: {locator}")
            continue
        actual_bytes = local.stat().st_size
        actual_sha = sha256_path(local)
        if actual_bytes != expected_bytes:
            errors.append(f"{prefix} byte mismatch: {locator}: {actual_bytes} != {expected_bytes}")
        if actual_sha != expected_sha:
            errors.append(f"{prefix} hash mismatch: {locator}: {actual_sha} != {expected_sha}")
        facts.append({"bytes": actual_bytes, "locator": locator, "sha256": actual_sha})


def walk_values(value: Any, path: str = "") -> Iterable[tuple[str, str, Any]]:
    """Yield ``(path, key, value)`` for every object member."""

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield child_path, str(key), child
            yield from walk_values(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_values(child, f"{path}[{index}]")


def validate_no_prose(record: dict[str, Any], record_path: str, errors: list[str]) -> int:
    checked = 0
    for field_path, key, value in walk_values(record):
        checked += 1
        key_lower = key.casefold()
        if key_lower in PROSE_KEYS:
            errors.append(f"{record_path}: prose payload key is not allowed: {field_path}")
            continue
        if isinstance(value, str) and len(value) > 4096 and key_lower not in LONG_VALUE_ALLOWED_KEYS:
            # A long arbitrary string is almost certainly copied prose.  Hash,
            # URL, path, and bounded state fields are handled explicitly.
            if not key_lower.endswith(("_sha256", "_hash")) and "url" not in key_lower and "locator" not in key_lower:
                errors.append(f"{record_path}: unbounded text-like value at {field_path} ({len(value)} chars)")
    return checked


def route_is_safe(value: str, field_path: str, errors: list[str], learner_route: bool = False) -> None:
    if not value:
        return
    parsed = urlparse(value)
    if parsed.scheme:
        if parsed.scheme != "https":
            errors.append(f"{field_path}: route URL is not HTTPS: {value}")
            return
        if parsed.hostname in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
            errors.append(f"{field_path}: route URL points to a local host: {value}")
    elif value.startswith("//"):
        errors.append(f"{field_path}: protocol-relative route URL is not allowed: {value}")
    # A learner route may point to HTML or a directory fallback, but not to a
    # machine-readable backend artifact.  Source/authority URLs (for example
    # a frozen ``raw.githubusercontent.com`` CNXML witness) are not learner
    # routes and are therefore exempt from this suffix check.
    if learner_route:
        path_lower = parsed.path.casefold()
        if path_lower.endswith((".json", ".jsonl", ".csv", ".zip", ".cnxml", ".tex")):
            errors.append(f"{field_path}: learner route points to a machine-readable/source artifact: {value}")
        if "/api/" in path_lower or path_lower.startswith("/api/"):
            errors.append(f"{field_path}: learner route points to an API path: {value}")


def validate_routes(value: Any, path: str, errors: list[str], route_count: list[int]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            key_lower = str(key).casefold()
            is_route_key = (
                isinstance(child, str)
                and (key_lower == "url" or key_lower.endswith("_url") or key_lower in {"href", "route_url"})
            )
            if is_route_key and child:
                route_count[0] += 1
                route_is_safe(child, child_path, errors, learner_route=True)
            elif isinstance(child, str) and re.match(r"^https?://", child, re.IGNORECASE):
                # Also protect URLs nested in source/authority metadata from
                # silently becoming insecure links.
                route_is_safe(child, child_path, errors, learner_route=False)
            validate_routes(child, child_path, errors, route_count)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_routes(child, f"{path}[{index}]", errors, route_count)


def parse_jsonl(path: Path, manifest_schema: str, errors: list[str]) -> list[dict[str, Any]]:
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{path.name}: cannot read UTF-8 JSONL: {exc}")
        return []
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{path.name}: UTF-8 BOM is not allowed")
    if not raw.endswith(b"\n"):
        errors.append(f"{path.name}: JSONL must end with LF")
    if b"\r" in raw:
        errors.append(f"{path.name}: CR bytes are not allowed in canonical JSONL")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.split("\n"), 1):
        if line == "" and line_number == len(text.split("\n")):
            continue
        if not line.strip():
            errors.append(f"{path.name}:{line_number}: blank JSONL line")
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{line_number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path.name}:{line_number}: JSONL record is not an object")
            continue
        if canonical_json(value) != line:
            errors.append(f"{path.name}:{line_number}: record is not canonical sorted JSON")
        if value.get("schema_id") not in (None, manifest_schema):
            errors.append(f"{path.name}:{line_number}: schema_id differs from manifest")
        rows.append(value)
    return rows


def validate_record_rows(
    path_name: str,
    rows: list[dict[str, Any]],
    manifest_schema: str,
    course_id: str,
    errors: list[str],
    warnings: list[str],
) -> dict[str, int]:
    expected_type = EXPECTED_RECORD_TYPES.get(path_name)
    ids: set[str] = set()
    duplicate_lines: set[str] = set()
    route_count = [0]
    prose_fields = 0
    for index, row in enumerate(rows, 1):
        if expected_type and row.get("record_type") != expected_type:
            errors.append(f"{path_name}:{index}: record_type {row.get('record_type')!r} != {expected_type!r}")
        row_course = row.get("course_id")
        if row_course is not None and row_course != course_id:
            errors.append(f"{path_name}:{index}: course_id {row_course!r} != {course_id!r}")
        key = row.get("stable_unit_id") or row.get("id")
        if path_name in {"units.jsonl", "search.jsonl"}:
            if not isinstance(key, str) or not key:
                errors.append(f"{path_name}:{index}: missing stable_unit_id")
            elif key in ids:
                errors.append(f"{path_name}:{index}: duplicate stable_unit_id {key}")
            else:
                ids.add(key)
        line_key = canonical_json(row)
        if line_key in duplicate_lines:
            warnings.append(f"{path_name}:{index}: exact duplicate record")
        duplicate_lines.add(line_key)
        prose_fields += validate_no_prose(row, f"{path_name}:{index}", errors)
        validate_routes(row, f"{path_name}:{index}", errors, route_count)
    return {"records": len(rows), "unique_unit_ids": len(ids), "route_urls": route_count[0], "fields_checked": prose_fields}


def validate_package(package: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    file_facts: list[dict[str, Any]] = []
    authority_facts: list[dict[str, Any]] = []
    manifest_path = package / "manifest.json"
    if not manifest_path.is_file():
        return {"package": package.name, "result": "fail", "errors": ["manifest.json is missing"], "warnings": []}
    try:
        manifest = load_json(manifest_path)
    except ValidationError as exc:
        return {"package": package.name, "result": "fail", "errors": [str(exc)], "warnings": []}
    if not isinstance(manifest, dict):
        return {"package": package.name, "result": "fail", "errors": ["manifest.json is not an object"], "warnings": []}

    course_id = manifest.get("course_id")
    schema_id = manifest.get("schema_id")
    if not isinstance(course_id, str) or not course_id:
        errors.append("manifest.course_id is missing")
        course_id = ""
    if not isinstance(schema_id, str) or not schema_id:
        errors.append("manifest.schema_id is missing")
        schema_id = ""
    if manifest.get("owner_tree_mode") != "read_only":
        errors.append("manifest.owner_tree_mode must be read_only")
    scope_text = str(manifest.get("materialization_scope", "")).casefold()
    if "no textbook prose" not in scope_text and "no prose" not in scope_text and "without payload duplication" not in scope_text:
        warnings.append("materialization_scope does not explicitly state no textbook prose")

    declared = manifest.get("files")
    declared_paths: set[str] = set()
    rows_by_file: dict[str, list[dict[str, Any]]] = {}
    if not isinstance(declared, list) or not declared:
        errors.append("manifest.files must be a non-empty list")
        declared = []
    for index, fact in enumerate(declared):
        prefix = f"manifest.files[{index}]"
        if not isinstance(fact, dict):
            errors.append(f"{prefix} is not an object")
            continue
        try:
            relative = safe_relative_path(fact.get("path"), f"{prefix}.path")
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        relative_text = relative.as_posix()
        if relative_text in declared_paths:
            errors.append(f"duplicate manifest file path: {relative_text}")
            continue
        declared_paths.add(relative_text)
        expected_bytes = fact.get("bytes")
        expected_sha = fact.get("sha256")
        if not isinstance(expected_bytes, int) or expected_bytes < 0:
            errors.append(f"{prefix}.bytes is invalid")
            continue
        if not isinstance(expected_sha, str) or not SHA256_RE.fullmatch(expected_sha):
            errors.append(f"{prefix}.sha256 is invalid")
            continue
        target = package.joinpath(*relative.parts)
        if not target.is_file() or target.is_symlink():
            errors.append(f"manifest file missing/not regular: {relative_text}")
            continue
        actual_bytes = target.stat().st_size
        actual_sha = sha256_path(target)
        file_facts.append({"bytes": actual_bytes, "path": relative_text, "role": fact.get("role"), "sha256": actual_sha})
        if actual_bytes != expected_bytes:
            errors.append(f"{relative_text}: byte mismatch {actual_bytes} != {expected_bytes}")
        if actual_sha != expected_sha:
            errors.append(f"{relative_text}: SHA-256 mismatch {actual_sha} != {expected_sha}")
        if relative.name.endswith(".jsonl"):
            rows_by_file[relative.name] = parse_jsonl(target, schema_id, errors)
        elif relative.name.endswith(".json"):
            try:
                value = load_json(target)
                if not isinstance(value, dict):
                    errors.append(f"{relative_text}: JSON root must be an object")
                else:
                    validate_routes(value, relative_text, errors, [0])
            except ValidationError as exc:
                errors.append(str(exc))

    # Inventory closure is exact except for the manifest itself and this
    # deliberately out-of-band report.
    actual_paths = {path.relative_to(package).as_posix() for path in iter_regular_files(package)}
    allowed_paths = declared_paths | {"manifest.json", REPORT_NAME}
    for extra in sorted(actual_paths - allowed_paths):
        errors.append(f"unlisted package file: {extra}")
    if "manifest.json" not in actual_paths:
        errors.append("manifest.json is missing from package inventory")
    for missing in sorted((declared_paths | {"manifest.json"}) - actual_paths):
        errors.append(f"declared/inventory file missing: {missing}")

    if course_id == "C100":
        rights_path = package / "rights_accessibility.json"
        try:
            rights_document = load_json(rights_path)
            components = rights_document.get("rights", {}).get("components", [])
            by_id = {row.get("id"): row for row in components if isinstance(row, dict)}
            expected_statuses = {
                "rights-petrunin-body-cc-by-sa-4.0": "admitted",
                "rights-p22-cover-excluded": "blocked",
                "rights-fiziko-gpl-3.0-or-later": "component-licensed",
                "rights-mppics-macros-unresolved": "blocked-for-public-source-package",
                "rights-id-terminology-witness-pdfs-internal-only": "redistribution-unproven-excluded-from-public-packages",
                "rights-h2checkers-public-domain": "mapped-pending-qa",
            }
            expected_ids = set(expected_statuses) | {
                "rights-c100-independent-solutions-cc-by-sa-4.0",
                "rights-c100-advanced-workbook-separated",
            }
            if set(by_id) != expected_ids:
                errors.append(f"C100 rights ID set mismatch: {sorted(by_id)}")
            for rights_id, status in expected_statuses.items():
                if by_id.get(rights_id, {}).get("status") != status:
                    errors.append(f"C100 rights status mismatch: {rights_id}")
                if by_id.get(rights_id, {}).get("materialized_component_bytes_in_backend") is not False:
                    errors.append(f"C100 rights payload boundary missing: {rights_id}")
            workbook = by_id.get("rights-c100-advanced-workbook-separated", {})
            if workbook.get("materialized_in_pilot_or_reader") is not False:
                errors.append("C100 separately licensed workbook must remain absent from pilot and reader")
            solutions = by_id.get("rights-c100-independent-solutions-cc-by-sa-4.0", {})
            if solutions.get("license") != "CC BY-SA 4.0" or solutions.get("materialized_component_bytes_in_backend") is not False:
                errors.append("C100 independent-solution rights/payload boundary mismatch")
            materialization = load_json(package / "route_materialization.json")
            if materialization.get("observation_state") != "local_only":
                errors.append("C100 prepublication route evidence must be explicitly local_only")
            if "observations" in materialization or "public_readback" in materialization:
                errors.append("C100 local materialization must not claim public readback evidence")
        except (OSError, ValidationError, AttributeError) as exc:
            errors.append(f"C100 rights/accessibility gate could not run: {exc}")

    validate_authorities(manifest, errors, authority_facts)

    record_counts: dict[str, int] = {}
    records_checked = 0
    route_urls = 0
    prose_fields = 0
    for filename, count_key in JSONL_FILES.items():
        rows = rows_by_file.get(filename)
        if rows is None:
            # A package may omit an optional shard only if it also omits the
            # corresponding manifest count; current pilots require all three.
            if isinstance(manifest.get("record_counts"), dict) and count_key in manifest["record_counts"]:
                errors.append(f"manifest declares {count_key} but {filename} is absent")
            continue
        stats = validate_record_rows(filename, rows, schema_id, course_id, errors, warnings)
        record_counts[count_key] = stats["records"]
        records_checked += stats["records"]
        route_urls += stats["route_urls"]
        prose_fields += stats["fields_checked"]

    unit_ids = {row.get("stable_unit_id") for row in rows_by_file.get("units.jsonl", []) if isinstance(row.get("stable_unit_id"), str)}
    search_ids = {row.get("stable_unit_id") for row in rows_by_file.get("search.jsonl", []) if isinstance(row.get("stable_unit_id"), str)}
    if unit_ids != search_ids:
        errors.append(
            f"search stable-unit set differs from units: missing={sorted(unit_ids - search_ids)[:10]}, extra={sorted(search_ids - unit_ids)[:10]}"
        )
    relation_rows = rows_by_file.get("relations.jsonl", [])
    if course_id == "C100":
        c100_units = rows_by_file.get("units.jsonl", [])
        solution_ids = {
            row["stable_unit_id"]
            for row in c100_units
            if row.get("native_unit_kind") == "independent_solution"
        }
        subpart_ids = {
            row["stable_unit_id"]
            for row in c100_units
            if isinstance(row.get("native_unit_kind"), str) and row["native_unit_kind"].endswith("exercise-subpart")
        }
        parent_exercise_ids = {
            row["stable_unit_id"]
            for row in c100_units
            if isinstance(row.get("native_unit_kind"), str)
            and "exercise" in row["native_unit_kind"]
            and not row["native_unit_kind"].endswith("exercise-subpart")
        }
        if (len(solution_ids), len(subpart_ids), len(parent_exercise_ids)) != (253, 32, 253):
            errors.append(
                "C100 exercise/solution unit partition mismatch: "
                f"solutions={len(solution_ids)}, subparts={len(subpart_ids)}, parents={len(parent_exercise_ids)}"
            )
        for row in c100_units:
            route = row.get("learner_route", {})
            if row.get("stable_unit_id") in solution_ids:
                if (
                    row.get("rights_component_id") != "rights-c100-independent-solutions-cc-by-sa-4.0"
                    or route.get("anchor") is not None
                    or route.get("route_state") != "central_exact_owner_solution_pdf_materialized_course_level_fallback_no_named_destination"
                    or not str(route.get("url", "")).endswith("/solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf")
                ):
                    errors.append(f"C100 solution learner-route/rights mismatch: {row.get('stable_unit_id')}")
            elif route.get("anchor") != row.get("stable_unit_id"):
                errors.append(f"C100 semantic-reader anchor mismatch: {row.get('stable_unit_id')}")
        solves = [row for row in relation_rows if row.get("relation_type") == "solves"]
        part_of_exercise = [row for row in relation_rows if row.get("relation_type") == "part_of_exercise"]
        has_exercise = [row for row in relation_rows if row.get("relation_type") == "has_exercise"]
        if (
            len(solves) != 253
            or {row.get("from_id") for row in solves} != solution_ids
            or {row.get("to_id") for row in solves} != parent_exercise_ids
        ):
            errors.append("C100 253-solution crosswalk relation closure mismatch")
        if len(part_of_exercise) != 32 or {row.get("from_id") for row in part_of_exercise} != subpart_ids:
            errors.append("C100 32-subpart parent relation closure mismatch")
        if len(has_exercise) != 253 or {row.get("to_id") for row in has_exercise} != parent_exercise_ids:
            errors.append("C100 253 parent-exercise chapter relation closure mismatch")
    raw_external_endpoints = (
        {row.get("from_id") for row in relation_rows} | {row.get("to_id") for row in relation_rows}
    ) - unit_ids
    if None in raw_external_endpoints:
        errors.append("relation row has a missing from_id or to_id")
        raw_external_endpoints.discard(None)
    external_endpoints = sorted(raw_external_endpoints)
    endpoint_policy = manifest.get("relation_endpoint_policy")
    if not isinstance(endpoint_policy, dict):
        errors.append("manifest.relation_endpoint_policy must be an object")
    else:
        mode = endpoint_policy.get("mode")
        if mode not in {"internal_only", "exact_external_set"}:
            errors.append("manifest.relation_endpoint_policy.mode is invalid")
        if mode == "internal_only" and external_endpoints:
            errors.append(f"relation graph has {len(external_endpoints)} endpoints outside the stable-unit set")
        actual_external_sha = sha256_bytes(canonical_json(external_endpoints).encode("utf-8"))
        if endpoint_policy.get("external_endpoint_count") != len(external_endpoints):
            errors.append("relation external-endpoint count mismatch")
        if endpoint_policy.get("external_endpoint_sha256") != actual_external_sha:
            errors.append("relation external-endpoint SHA-256 mismatch")
    # Count every materialized role from the manifest, including optional
    # evidence shards such as D20's route_gap_report.json.  This prevents an
    # undeclared or silently omitted count from looking valid merely because
    # the three common JSONL files happened to match.
    for fact in declared:
        if isinstance(fact, dict):
            count_key = ROLE_COUNT_KEYS.get(fact.get("role"))
            if count_key:
                if count_key in {"rights_accessibility_documents", "route_readback_documents", "route_materialization_documents"}:
                    record_counts[count_key] = record_counts.get(count_key, 0) + 1
                elif count_key not in record_counts:
                    # JSONL record counts were derived from parsed rows above;
                    # retain those values rather than counting files as rows.
                    record_counts[count_key] = 0
    expected_counts = manifest.get("record_counts")
    if not isinstance(expected_counts, dict):
        errors.append("manifest.record_counts must be an object")
    else:
        for key, expected in expected_counts.items():
            if not isinstance(expected, int) or expected < 0:
                errors.append(f"manifest.record_counts.{key} is invalid")
            elif key in record_counts and expected != record_counts[key]:
                errors.append(f"record count mismatch {key}: {record_counts[key]} != {expected}")
        for key, actual in record_counts.items():
            if key not in expected_counts:
                errors.append(f"record count {key} is not declared in manifest")

    expected_package = EXPECTED_PACKAGES.get(package.name)
    if expected_package is None:
        errors.append(f"unexpected pilot package directory: {package.name}")
    else:
        if course_id != expected_package["course_id"]:
            errors.append(f"package course mismatch: {course_id} != {expected_package['course_id']}")
        for key in ("units", "search_documents", "relations"):
            if record_counts.get(key) != expected_package[key]:
                errors.append(f"fixed pilot regression count mismatch {key}: {record_counts.get(key)} != {expected_package[key]}")
    for filename, expected_sha in EXPECTED_CORE_HASHES.get(package.name, {}).items():
        path = package / filename
        if not path.is_file() or sha256_path(path) != expected_sha:
            errors.append(f"legacy pilot core SHA-256 regression: {filename}")

    result = "pass" if not errors else "fail"
    return {
        "package": package.name,
        "course_id": course_id,
        "dataset_id": manifest.get("dataset_id"),
        "schema_id": schema_id,
        "result": result,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "file_facts": sorted(file_facts, key=lambda row: row["path"]),
        "authority_facts": sorted(authority_facts, key=lambda row: row["locator"]),
        "record_counts": dict(sorted(record_counts.items())),
        "records_checked": records_checked,
        "route_urls_checked": route_urls,
        "prose_fields_checked": prose_fields,
    }


def write_report(package: Path, report: dict[str, Any]) -> None:
    (package / REPORT_NAME).write_text(pretty_json(report), encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    del argv
    package_dirs = [
        path for path in sorted(PILOTS_ROOT.iterdir()) if path.is_dir() and (path / "manifest.json").is_file()
    ]
    if not package_dirs:
        result = {"result": "fail", "packages": [], "errors": ["no pilot manifest directories found"]}
        print(canonical_json(result))
        return 1
    package_names = {path.name for path in package_dirs}
    global_errors = []
    if package_names != set(EXPECTED_PACKAGES):
        global_errors.append(
            f"pilot package set mismatch: present={sorted(package_names)}, expected={sorted(EXPECTED_PACKAGES)}"
        )
    reports: list[dict[str, Any]] = []
    for package in package_dirs:
        report = validate_package(package)
        write_report(package, report)
        reports.append(report)
    overall = "pass" if not global_errors and all(report.get("result") == "pass" for report in reports) else "fail"
    summary = {
        "result": overall,
        "errors": global_errors,
        "packages": [
            {
                "course_id": report.get("course_id"),
                "errors": len(report.get("errors", [])),
                "package": report["package"],
                "record_counts": report.get("record_counts", {}),
                "result": report.get("result"),
                "warnings": len(report.get("warnings", [])),
            }
            for report in reports
        ],
    }
    print(canonical_json(summary))
    return 0 if overall == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
