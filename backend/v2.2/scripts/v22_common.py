#!/usr/bin/env python3
"""Shared deterministic primitives for the modular mathematics backend v2.2."""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from pathlib import Path
from typing import Any, Iterable, Iterator


SCHEMA_VERSION = "2.2.0"
IDENTITY_NAMESPACE = uuid.UUID("0e4d7b37-6108-5065-b08f-d1098697cc02")
IDENTITY_FORMULA = "UUIDv5(identity_namespace, record_type + ':' + semantic_key)"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
UUID5_URN_RE = re.compile(
    r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(canonical_json_bytes(row) for row in rows)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_jsonl(path: Path) -> Iterator[tuple[dict[str, Any], bytes]]:
    with path.open("rb") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.endswith(b"\n"):
                raise ValueError(f"{path}: line {line_number} lacks LF terminator")
            if b"\r" in raw:
                raise ValueError(f"{path}: line {line_number} contains CR")
            try:
                row = json.loads(raw.decode("utf-8"))
            except Exception as exc:  # pragma: no cover - exact error is surfaced
                raise ValueError(f"{path}: invalid JSON on line {line_number}: {exc}") from exc
            yield row, raw


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, value: Any) -> None:
    write_bytes(path, canonical_json_bytes(value))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    ordered = sorted(rows, key=lambda row: (row["record_type"], row["semantic_key"]))
    write_bytes(path, canonical_jsonl_bytes(ordered))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(chunk_size)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def strip_sha256_prefix(value: str) -> str:
    return value.removeprefix("sha256:")


def global_id(record_type: str, semantic_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(IDENTITY_NAMESPACE, record_type + ':' + semantic_key)}"


def file_fact(
    root: Path,
    path: Path,
    *,
    role: str,
    media_type: str,
) -> dict[str, Any]:
    relative = path.relative_to(root).as_posix()
    return {
        "path": relative,
        "role": role,
        "media_type": media_type,
        "bytes": path.stat().st_size,
        "sha256": sha256_path(path),
    }


def combined_digest(facts: Iterable[dict[str, Any]]) -> str:
    lines = []
    for fact in sorted(facts, key=lambda item: item["path"]):
        lines.append(f'{fact["sha256"]}  {fact["bytes"]}  {fact["path"]}\n')
    return sha256_bytes("".join(lines).encode("utf-8"))


def media_type_for(path: str) -> str:
    suffix = Path(path).suffix.lower()
    return {
        ".json": "application/json",
        ".jsonl": "application/x-ndjson",
        ".py": "text/x-python",
        ".xml": "application/xml",
        ".cnxml": "application/xml",
        ".tsv": "text/tab-separated-values",
        ".csv": "text/csv",
        ".md": "text/markdown",
        ".html": "text/html",
    }.get(suffix, "application/octet-stream")


def envelope(
    *,
    record_type: str,
    semantic_key: str,
    dataset_id: str,
    owner_authority_id: str,
    recorded_at: str,
    normalized_state: str,
    owner_native_state: str | None,
    state_profile: str,
    provenance_binding_ids: Iterable[str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": global_id(record_type, semantic_key),
        "record_type": record_type,
        "semantic_key": semantic_key,
        "dataset_id": dataset_id,
        "owner_authority_id": owner_authority_id,
        "recorded_at": recorded_at,
        "normalized_state": normalized_state,
        "owner_native_state": owner_native_state,
        "state_profile": state_profile,
        "provenance_binding_ids": sorted(set(provenance_binding_ids)),
        "payload": payload,
    }


def resolve_locator(
    locator_base: str,
    locator: str,
    *,
    package_root: Path,
    program_root: Path,
    owner_root: Path,
    owner_backend_root: Path,
) -> Path:
    bases = {
        "package_root": package_root,
        "program_repository_root": program_root,
        "owner_repository_root": owner_root,
        "owner_backend_root": owner_backend_root,
    }
    if locator_base not in bases:
        raise ValueError(f"unsupported local locator_base: {locator_base}")
    candidate = (bases[locator_base] / Path(locator)).resolve()
    base = bases[locator_base].resolve()
    if candidate != base and base not in candidate.parents:
        raise ValueError(f"locator escapes {locator_base}: {locator}")
    return candidate


def assert_hash_fact(path: Path, expected_bytes: int, expected_sha256: str) -> None:
    actual_bytes = path.stat().st_size
    actual_sha256 = sha256_path(path)
    if actual_bytes != expected_bytes or actual_sha256 != strip_sha256_prefix(expected_sha256):
        raise ValueError(
            f"byte/hash mismatch for {path}: expected {expected_bytes}/{expected_sha256}, "
            f"got {actual_bytes}/{actual_sha256}"
        )

