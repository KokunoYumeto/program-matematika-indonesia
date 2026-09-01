#!/usr/bin/env python3
"""Assemble and validate the v0.62.17 successor release locally.

This tool is deliberately publication-free.  It constructs two isolated,
flat payload projections from the verified v0.62.16 release directories:

* a 121-file GitHub release projection (106 exact retained files, three
  same-name successor replacements, three rotated release names, and nine
  new CLP assets); and
* a 100-file Zenodo projection (97 retained direct predecessor files plus
  three rotated names: the source archive, successor checksum, and replacement
  23-member additions bundle).

The source archive is produced twice with ``git archive`` from an explicit
commit/tree pair.  The ZIP comment, release notes, and report bind the archive
to that pair.  The script refuses a byte-identical predecessor source archive,
refuses symlinks/path traversal, validates every predecessor byte against the
immutable v0.62.16 receipts, and never writes a remote, reads credentials, or
modifies a predecessor directory.

Use ``--preflight`` for a temporary, self-cleaning validation or ``--build``
with a new narrow ``--out-root`` to retain the assembled projections.  A
non-empty or existing output is always rejected; there is no overwrite mode.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Iterable, Iterator


PROJECT = Path(__file__).resolve().parents[1]
RELEASES = PROJECT / "releases"
DEFAULT_PREDECESSOR = RELEASES / "v0.62.16"
DEFAULT_PREDECESSOR_ZENODO = RELEASES / "v0.62.16-zenodo"
DEFAULT_SUCCESSOR_ROOT = PROJECT / "tmp" / "clp-v06217-successor-staging-20260901"
VERSION = "0.62.17"
PREDECESSOR_VERSION = "0.62.16"

GH_EXPECTED_FILES = 121
GH_EXPECTED_CHECKSUM_ROWS = 120
ZENODO_EXPECTED_FILES = 100
ZENODO_EXPECTED_CHECKSUM_ROWS = 99
BUNDLE_EXPECTED_MEMBERS = 23

OLD_SOURCE = "program-matematika-indonesia-source-v0.62.16.zip"
NEW_SOURCE = "program-matematika-indonesia-source-v0.62.17.zip"
OLD_GH_CHECKSUM = "RELEASE_CHECKSUMS_v0.62.16.sha256"
NEW_GH_CHECKSUM = "RELEASE_CHECKSUMS_v0.62.17.sha256"
OLD_ZENODO_CHECKSUM = "ZENODO_RELEASE_CHECKSUMS_v0.62.16.sha256"
NEW_ZENODO_CHECKSUM = "ZENODO_RELEASE_CHECKSUMS_v0.62.17.sha256"
OLD_NOTES = "RELEASE_NOTES_v0.62.16.md"
NEW_NOTES = "RELEASE_NOTES_v0.62.17.md"
OLD_BUNDLE = "program-matematika-indonesia-v0.62.16-zenodo-additions.zip"
NEW_BUNDLE = "program-matematika-indonesia-v0.62.17-zenodo-additions.zip"

# These are the three flat GitHub names which existed in v0.62.16 and are
# replaced by the v0.62.17 CLP successor projection.
COLLISION_NAMES = (
    "comparison-evidence-manifest-v1.json",
    "feature-adoption-provenance-v1.json",
    "v23-adapter-index-v2.json",
)

# Nine CLP assets selected for the release boundary.  The paths are relative
# to the builder's successor staging root and are intentionally explicit:
# selecting by basename from an arbitrary directory would permit ambiguity.
PURE_ASSET_PATHS = {
    "CLP_LEARNER_ROUTE_EVIDENCE.identity.json": "backend/course-capsule-v1/authority/clp-family-v231/evidence/CLP_LEARNER_ROUTE_EVIDENCE.identity.json",
    "CLP_NATIVE_PROFILE_DESIGN.identity.json": "backend/course-capsule-v1/authority/clp-family-v231/evidence/CLP_NATIVE_PROFILE_DESIGN.identity.json",
    "CLP_PACKAGE_MANIFEST.identity.json": "backend/course-capsule-v1/authority/clp-family-v231/evidence/CLP_PACKAGE_MANIFEST.identity.json",
    "HANDOFF_FILE_INVENTORY.identity.json": "backend/course-capsule-v1/authority/clp-family-v231/evidence/HANDOFF_FILE_INVENTORY.identity.json",
    "clp-learner-route-input-v1.json": "backend/course-capsule-v1/authority/clp-family-v231/clp-learner-route-input-v1.json",
    "learner-reader-actions-v1.json": "backend/course-capsule-v1/authority/clp-family-v231/learner-reader-actions-v1.json",
    "modular-backend-pattern-index-v2.1.json": "backend/course-capsule-v1/authority/clp-family-v231/modular-backend-pattern-index-v2.1.json",
    "modular-backend-pattern-index-v2.1.schema.json": "backend/course-capsule-v1/authority/clp-family-v231/modular-backend-pattern-index-v2.1.schema.json",
    "CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip": "releases/v0.62.17/CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip",
}

COLLISION_PATHS = {
    "comparison-evidence-manifest-v1.json": "backend/course-capsule-v1/authority/clp-family-v231/comparison-evidence-manifest-v1.json",
    "feature-adoption-provenance-v1.json": "backend/course-capsule-v1/authority/clp-family-v231/feature-adoption-provenance-v1.json",
    "v23-adapter-index-v2.json": "backend/course-capsule-v1/authority/clp-family-v231/v23-adapter-index-v2.json",
}

# The source archive must describe the actual CLP successor, not merely an
# unrelated commit that happens to differ from the predecessor.  The first
# group below is the complete non-ZIP CLP staging boundary (the eight pure
# assets plus the three same-name collision replacements).  The central group
# contains the effective integration authority (the fourth, semantic
# collision) and the three generated capsule projections.  The expected bytes
# for these paths are read from the validated staging inputs or the current
# canonical working files at invocation time; the commit/tree is then required
# to contain byte-identical blobs at every path.
CENTRAL_SUCCESSOR_SOURCE_PATHS = (
    "backend/course-capsule-v1/authority/integration-overrides-v1.json",
    "backend/course-capsule-v1/generated/course-capsules.json",
    "backend/course-capsule-v1/generated/course-capsules.jsonl",
    "backend/course-capsule-v1/generated/manifest.json",
)

EXPECTED_CLP_ZIP = (545_418_367, "f2e2714c5f1349092e8cb574d6495e604086c9df3bc4bdf5bbe5974b5f61360d")
EXPECTED_RECEIPTS = {
    "github": (87_782, "1c5649a9b5fede9b808783d1c353c436ea2d9afedbe950b095933a7b81942c34"),
    "zenodo": (58_034, "f5265bd54ac987a5c55cf06fe8ee04cb4cef60934bec4a7ca7b1e6b662a8eb30"),
    "cursor": (408, "550cec2cb87b7311649d19d351c9475db676bc0585f65d17e7f169934eea30b2"),
}

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
UNSAFE_NAME = re.compile(r"(^$|^\.\.?$|[\\/\x00-\x1f\x7f])")
SENSITIVE_NAME = re.compile(r"(^|/)(?:\.env(?:\.|$)|.*(?:token|credential|secret|password).*)", re.I)


class AssemblyError(RuntimeError):
    """A fail-closed assembly/preflight error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssemblyError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def identity(path: Path) -> dict[str, Any]:
    size, digest = sha256_path(path)
    return {"bytes": size, "sha256": digest}


def fact(name: str, path: Path, provenance: str) -> dict[str, Any]:
    require(not path.is_symlink() and path.is_file(), f"{provenance}: missing regular file {path}")
    size, digest = sha256_path(path)
    return {"name": name, "bytes": size, "sha256": digest, "provenance": provenance}


def safe_name(name: str) -> None:
    require(isinstance(name, str) and not UNSAFE_NAME.search(name), f"unsafe flat filename: {name!r}")
    require(not SENSITIVE_NAME.search(name), f"credential-bearing filename rejected: {name!r}")


def safe_zip_path(name: str) -> None:
    """Validate a slash-separated ZIP path without allowing traversal."""
    require(isinstance(name, str) and name and not name.startswith("/"), f"unsafe ZIP path: {name!r}")
    require("\\" not in name and "\x00" not in name, f"unsafe ZIP path: {name!r}")
    parts = name.split("/")
    require(all(part not in {"", ".", ".."} for part in parts), f"unsafe ZIP path: {name!r}")
    require(not any(ord(char) < 32 or ord(char) == 127 for char in name), f"control character in ZIP path: {name!r}")
    require(not SENSITIVE_NAME.search(name), f"credential-bearing ZIP path rejected: {name!r}")


def inventory_aggregate(rows: Iterable[dict[str, Any]]) -> str:
    payload = "".join(
        f"{row['sha256']}  {row['name']}\n"
        for row in sorted(rows, key=lambda item: str(item["name"]))
    ).encode("utf-8")
    return sha256_bytes(payload)


def checksum_bytes(rows: Iterable[dict[str, Any]], checksum_name: str) -> bytes:
    ordered = sorted(rows, key=lambda item: str(item["name"]))
    names = [str(row["name"]) for row in ordered]
    require(len(names) == len(set(names)), "duplicate name before checksum generation")
    require(checksum_name not in names, f"checksum self-reference before generation: {checksum_name}")
    return "".join(f"{row['sha256']}  {row['name']}\n" for row in ordered).encode("utf-8")


def rel_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def ensure_inside(child: Path, parent: Path, label: str) -> Path:
    resolved_child = child.resolve()
    resolved_parent = parent.resolve()
    try:
        resolved_child.relative_to(resolved_parent)
    except ValueError as exc:
        raise AssemblyError(f"{label} escapes its allowed root") from exc
    return resolved_child


def copy_bytes(source: Path, destination: Path) -> None:
    require(not source.is_symlink() and source.is_file(), f"source is not a regular file: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    require(not destination.exists() and not destination.is_symlink(), f"refusing to overwrite {destination}")
    with source.open("rb") as src, destination.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)


def run_git(args: list[str], label: str, timeout: int = 900) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", str(PROJECT), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AssemblyError(f"bounded Git operation failed: {label}") from exc
    require(completed.returncode == 0, f"bounded Git operation failed: {label}: {completed.stderr[-500:].decode('utf-8', 'replace')}")
    return completed.stdout


def load_json(path: Path, label: str) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AssemblyError(f"invalid JSON in {label}: {path}") from exc
    require(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def read_receipt(path: Path, label: str, expected: tuple[int, str]) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), f"missing {label} receipt")
    raw = path.read_bytes()
    require((len(raw), sha256_bytes(raw)) == expected, f"{label} receipt identity differs")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise AssemblyError(f"{label} receipt is not UTF-8 JSON") from exc
    require(isinstance(value, dict), f"{label} receipt is not an object")
    return value


def normalize_rows(raw_rows: Any, expected_count: int, expected_aggregate: str, label: str) -> list[dict[str, Any]]:
    require(isinstance(raw_rows, list) and len(raw_rows) == expected_count, f"{label} inventory count differs")
    rows: list[dict[str, Any]] = []
    names: set[str] = set()
    for raw in raw_rows:
        require(isinstance(raw, dict), f"{label} inventory row malformed")
        name = raw.get("name")
        bytes_count = raw.get("bytes")
        digest = raw.get("sha256")
        safe_name(name)
        require(name not in names, f"{label} duplicate filename: {name}")
        require(type(bytes_count) is int and bytes_count >= 0, f"{label} invalid byte count: {name}")
        require(isinstance(digest, str) and HEX64.fullmatch(digest), f"{label} invalid SHA-256: {name}")
        names.add(name)
        rows.append({"name": name, "bytes": bytes_count, "sha256": digest})
    require(inventory_aggregate(rows) == expected_aggregate, f"{label} aggregate differs")
    return rows


@dataclass(frozen=True)
class Predecessor:
    github_rows: tuple[dict[str, Any], ...]
    zenodo_rows: tuple[dict[str, Any], ...]
    github_receipt: dict[str, Any]
    zenodo_receipt: dict[str, Any]
    cursor: dict[str, Any]


def validate_predecessor(github_root: Path, zenodo_root: Path) -> Predecessor:
    require(github_root.is_dir() and not github_root.is_symlink(), "v0.62.16 GitHub directory missing or symlinked")
    require(zenodo_root.is_dir() and not zenodo_root.is_symlink(), "v0.62.16 Zenodo directory missing or symlinked")
    gh_receipt = read_receipt(PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.16.json", "GitHub v0.62.16", EXPECTED_RECEIPTS["github"])
    z_receipt = read_receipt(PROJECT / "PUBLICATION_RECEIPT_v0.62.16.json", "Zenodo v0.62.16", EXPECTED_RECEIPTS["zenodo"])
    cursor = read_receipt(PROJECT / "ZENODO_RESERVATION_CURSOR_v0.62.16.json", "Zenodo v0.62.16 cursor", EXPECTED_RECEIPTS["cursor"])

    require((gh_receipt.get("version"), gh_receipt.get("state"), gh_receipt.get("repository_public")) == (PREDECESSOR_VERSION, "published_public_verified", True), "GitHub predecessor is not public verified")
    gh_release = gh_receipt.get("release")
    require(isinstance(gh_release, dict) and gh_release.get("tag") == "v0.62.16" and gh_release.get("draft") is False and gh_release.get("prerelease") is False, "GitHub predecessor release state differs")
    gh_inventory = gh_receipt.get("inventory")
    require(isinstance(gh_inventory, dict), "GitHub predecessor inventory missing")
    gh_rows = normalize_rows(gh_inventory.get("entries"), 112, str(gh_inventory.get("aggregate_sha256")), "GitHub predecessor")
    require(gh_inventory.get("bytes") == sum(row["bytes"] for row in gh_rows), "GitHub predecessor byte total differs")

    require((z_receipt.get("version"), z_receipt.get("state")) == (PREDECESSOR_VERSION, "published_open_modular_backend_successor"), "Zenodo predecessor state differs")
    z_meta = z_receipt.get("zenodo")
    require(isinstance(z_meta, dict) and z_meta.get("access_right") == "open" and z_meta.get("file_count") == 100, "Zenodo predecessor is not open with 100 files")
    z_rows = normalize_rows(z_receipt.get("payload_inventory"), 100, str(z_receipt.get("payload_inventory_aggregate_sha256")), "Zenodo predecessor")
    require(z_receipt.get("payload_total_bytes") == sum(row["bytes"] for row in z_rows), "Zenodo predecessor byte total differs")
    require((cursor.get("version"), cursor.get("state"), cursor.get("record_id")) == (PREDECESSOR_VERSION, "published_verified", z_meta.get("record_id")), "Zenodo predecessor cursor differs")

    # Local release directories are hard-linked snapshots in this workspace;
    # read and hash them, but never link successor output back to them.
    for root, rows, label, expected_count in (
        (github_root, gh_rows, "GitHub v0.62.16 local", 112),
        (zenodo_root, z_rows, "Zenodo v0.62.16 local", 100),
    ):
        entries = list(root.iterdir())
        require(len(entries) == expected_count, f"{label} entry count differs")
        require(all(item.is_file() and not item.is_symlink() for item in entries), f"{label} contains non-regular entry")
        expected_by_name = {row["name"]: row for row in rows}
        require({item.name for item in entries} == set(expected_by_name), f"{label} names differ from receipt")
        for name, expected in expected_by_name.items():
            observed = identity(root / name)
            require(observed == {"bytes": expected["bytes"], "sha256": expected["sha256"]}, f"{label} bytes differ: {name}")
    return Predecessor(tuple(gh_rows), tuple(z_rows), gh_receipt, z_receipt, cursor)


def validate_successor_inputs(successor_root: Path) -> dict[str, Path]:
    require(successor_root.is_dir() and not successor_root.is_symlink(), "successor staging root missing or symlinked")
    resolved_root = successor_root.resolve()
    paths: dict[str, Path] = {}
    for name, relative_path in {**PURE_ASSET_PATHS, **COLLISION_PATHS}.items():
        path = ensure_inside(resolved_root / Path(relative_path), resolved_root, f"successor input {name}")
        require(path.is_file() and not path.is_symlink(), f"missing successor input: {relative_path}")
        safe_name(name)
        paths[name] = path
    size, digest = sha256_path(paths["CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip"])
    require((size, digest) == EXPECTED_CLP_ZIP, f"sealed CLP ZIP identity differs: {(size, digest)}")
    require(len(PURE_ASSET_PATHS) == 9 and len(COLLISION_PATHS) == 3, "successor boundary constants drift")
    require(set(PURE_ASSET_PATHS).isdisjoint(COLLISION_PATHS), "successor boundary sets overlap")
    return paths


def validate_commit_tree(commit: str, tree: str) -> set[str]:
    require(isinstance(commit, str) and HEX40.fullmatch(commit), "--source-commit must be lowercase 40-character SHA")
    require(isinstance(tree, str) and HEX40.fullmatch(tree), "--source-tree must be lowercase 40-character SHA")
    resolved_commit = run_git(["rev-parse", "--verify", f"{commit}^{{commit}}"], "resolve source commit").decode("ascii").strip()
    resolved_tree = run_git(["rev-parse", "--verify", f"{commit}^{{tree}}"], "resolve source tree").decode("ascii").strip()
    require(resolved_commit == commit and resolved_tree == tree, "source commit/tree pair does not resolve exactly")
    raw = run_git(["ls-tree", "-r", "-z", "--full-tree", commit], "inspect source tree")
    require(raw.endswith(b"\0"), "source tree listing is not NUL terminated")
    paths: set[str] = set()
    for entry in raw[:-1].split(b"\0"):
        require(b"\t" in entry, "malformed source tree entry")
        metadata, raw_path = entry.split(b"\t", 1)
        fields = metadata.decode("ascii").split(" ")
        require(len(fields) == 3, "malformed source tree metadata")
        mode, object_type, object_id = fields
        path = raw_path.decode("utf-8")
        require(mode in {"100644", "100755"} and object_type == "blob", f"non-regular source tree entry: {path}")
        require(re.fullmatch(r"[0-9a-f]{40,64}", object_id) is not None, f"source tree object id malformed: {path}")
        normalized = PurePosixPath(path).as_posix()
        require(normalized == path and path not in paths and not path.startswith("/"), f"unsafe source tree path: {path}")
        safe_zip_path(path)
        paths.add(path)
    require(paths, "source tree contains no regular files")
    return paths


def validate_successor_source_tree(
    commit: str,
    tree_paths: set[str],
    successor_inputs: dict[str, Path],
) -> list[dict[str, Any]]:
    """Require successor inputs to be present, and byte-identical, in the source tree.

    ``validate_commit_tree`` proves only that a commit/tree is internally
    well-formed.  Without this second gate an unrelated commit can pass the
    release preflight while the CLP assets are supplied solely from an
    uncommitted staging directory.  Keep the allowlist explicit and narrow:
    eight non-ZIP CLP assets plus the three collision replacements, followed
    by the four effective central projections generated by the integration.
    """
    expected: dict[str, tuple[str, Path]] = {}
    for name, relative_path in {**PURE_ASSET_PATHS, **COLLISION_PATHS}.items():
        # The large ZIP is a release asset and is intentionally not required
        # in the Git source archive; its sealed identity is checked separately.
        if name == "CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip":
            continue
        require(name in successor_inputs, f"successor source expectation missing staging input: {name}")
        require(relative_path not in expected, f"duplicate successor source path: {relative_path}")
        expected[relative_path] = (name, successor_inputs[name])

    for relative_path in CENTRAL_SUCCESSOR_SOURCE_PATHS:
        require(relative_path not in expected, f"duplicate central successor source path: {relative_path}")
        local = ensure_inside(PROJECT / Path(relative_path), PROJECT, f"central successor source {relative_path}")
        require(local.is_file() and not local.is_symlink(), f"missing current central successor source: {relative_path}")
        expected[relative_path] = (relative_path, local)

    require(len(expected) == 15, f"successor source gate boundary drift: {len(expected)} paths")

    rows: list[dict[str, Any]] = []
    for relative_path, (label, expected_path) in sorted(expected.items()):
        require(relative_path in tree_paths, f"successor source tree missing required path: {relative_path}")
        expected_size, expected_digest = sha256_path(expected_path)
        observed = run_git(
            ["show", f"{commit}:{relative_path}"],
            f"read successor source blob {relative_path}",
        )
        observed_size = len(observed)
        observed_digest = sha256_bytes(observed)
        require(
            (observed_size, observed_digest) == (expected_size, expected_digest),
            f"successor source blob drift for {relative_path}: expected "
            f"{expected_size} bytes/{expected_digest}, got {observed_size} bytes/{observed_digest}",
        )
        rows.append(
            {
                "path": relative_path,
                "label": label,
                "bytes": expected_size,
                "sha256": expected_digest,
            }
        )
    return rows


def build_source_archive(
    work_root: Path,
    commit: str,
    tree: str,
    predecessor_source: Path,
    successor_inputs: dict[str, Path],
) -> tuple[Path, dict[str, Any]]:
    tree_paths = validate_commit_tree(commit, tree)
    successor_source_rows = validate_successor_source_tree(commit, tree_paths, successor_inputs)
    archive_a = work_root / "source-a.zip"
    archive_b = work_root / "source-b.zip"
    for destination in (archive_a, archive_b):
        with destination.open("wb") as handle:
            try:
                completed = subprocess.run(
                    ["git", "-C", str(PROJECT), "archive", "--format=zip", commit],
                    stdout=handle,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=900,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise AssemblyError("bounded Git archive operation failed") from exc
            require(completed.returncode == 0, f"git archive failed: {completed.stderr[-500:].decode('utf-8', 'replace')}")
    first = identity(archive_a)
    second = identity(archive_b)
    require(first == second, "git archive replay is not byte-identical")
    require(first["sha256"] != identity(predecessor_source)["sha256"], "successor source archive is byte-identical to v0.62.16")
    require(first["bytes"] > 0, "source archive is empty")
    try:
        with zipfile.ZipFile(archive_a, "r") as archive:
            require(archive.comment == commit.encode("ascii"), "source ZIP comment does not bind source commit")
            members = archive.infolist()
            files = [member for member in members if not member.is_dir()]
            require(files and {member.filename for member in files} == tree_paths, "source ZIP inventory differs from source tree")
            require([member.filename for member in members] == sorted(member.filename for member in members), "source ZIP members are not sorted")
            require(len({member.date_time for member in members}) == 1, "source ZIP timestamps are not uniform")
            folded: set[str] = set()
            for member in members:
                member_name = member.filename.rstrip("/")
                safe_zip_path(member_name)
                require(member.filename.casefold() not in folded, f"case-folded source ZIP duplicate: {member.filename}")
                folded.add(member.filename.casefold())
                require(member.flag_bits & 0x1 == 0, f"encrypted source ZIP member: {member.filename}")
                require(member.compress_type in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}, f"unsupported source ZIP compression: {member.filename}")
                if member.create_system == 3:
                    require(not stat.S_ISLNK((member.external_attr >> 16) & 0xFFFF), f"symlink source ZIP member: {member.filename}")
            require(archive.testzip() is None, "source ZIP CRC validation failed")
            details = {
                "source_commit": commit,
                "source_tree": tree,
                "successor_source_gate": successor_source_rows,
                "zip_comment": commit,
                "zip_files": len(files),
                "zip_uncompressed_bytes": sum(member.file_size for member in files),
                "deterministic_replay": "pass_byte_identical_a_b",
                "bytes": first["bytes"],
                "sha256": first["sha256"],
            }
    except (OSError, zipfile.BadZipFile) as exc:
        raise AssemblyError("invalid deterministic source ZIP") from exc
    return archive_a, details


def write_fixed_zip(destination: Path, members: list[tuple[str, Path | tuple[zipfile.ZipFile, str]]], comment: bytes) -> dict[str, Any]:
    names = [name for name, _ in members]
    require(names == sorted(names), "bundle member order must be lexical")
    require(len(names) == len(set(names)), "bundle member names duplicate")
    folded = [name.casefold() for name in names]
    require(len(folded) == len(set(folded)), "bundle member names collide case-insensitively")
    require(len(comment) <= 65_535 and comment, "bundle comment must be non-empty and bounded")
    destination.parent.mkdir(parents=True, exist_ok=True)
    require(not destination.exists() and not destination.is_symlink(), f"refusing to overwrite bundle {destination}")
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_STORED, allowZip64=True, strict_timestamps=True) as archive:
        archive.comment = comment
        for name, source in members:
            safe_name(name)
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.flag_bits |= 0x800
            with archive.open(info, "w") as output:
                if isinstance(source, tuple):
                    with source[0].open(source[1], "r") as input_stream:
                        shutil.copyfileobj(input_stream, output, length=1024 * 1024)
                else:
                    with source.open("rb") as input_stream:
                        shutil.copyfileobj(input_stream, output, length=1024 * 1024)
    with zipfile.ZipFile(destination, "r") as archive:
        require(archive.comment == comment, "bundle comment readback differs")
        infos = archive.infolist()
        require([info.filename for info in infos] == names, "bundle member order readback differs")
        require(all(not info.is_dir() and info.flag_bits & 0x1 == 0 for info in infos), "bundle contains a directory or encrypted member")
        require(archive.testzip() is None, "bundle CRC validation failed")
        return {"members": len(infos), "uncompressed_bytes": sum(info.file_size for info in infos), "comment": comment.decode("ascii")}


def validate_bundle(path: Path, expected_names: list[str], expected_rows: dict[str, dict[str, Any]], comment: bytes) -> dict[str, Any]:
    with zipfile.ZipFile(path, "r") as archive:
        require(archive.comment == comment, "bundle comment mismatch")
        infos = archive.infolist()
        require([info.filename for info in infos] == expected_names, "bundle names differ")
        require(archive.testzip() is None, "bundle CRC readback failed")
        for info in infos:
            require(not info.is_dir() and not (info.flag_bits & 0x1), f"invalid bundle member: {info.filename}")
            safe_name(info.filename)
            digest = hashlib.sha256()
            size = 0
            with archive.open(info, "r") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    size += len(chunk)
                    digest.update(chunk)
            expected = expected_rows[info.filename]
            require((size, digest.hexdigest()) == (expected["bytes"], expected["sha256"]), f"bundle member identity differs: {info.filename}")
        return {"members": len(infos), "uncompressed_bytes": sum(info.file_size for info in infos), "bytes": path.stat().st_size, "sha256": sha256_path(path)[1], "comment": comment.decode("ascii")}


def rows_for_directory(root: Path) -> list[dict[str, Any]]:
    entries = list(root.iterdir())
    require(all(entry.is_file() and not entry.is_symlink() for entry in entries), f"payload contains non-regular entry: {root}")
    rows: list[dict[str, Any]] = []
    for entry in sorted(entries, key=lambda item: item.name):
        safe_name(entry.name)
        rows.append({"name": entry.name, **identity(entry)})
    return rows


def validate_payload(root: Path, expected_count: int, checksum_name: str, expected_checksum_rows: int) -> list[dict[str, Any]]:
    rows = rows_for_directory(root)
    require(len(rows) == expected_count, f"payload count differs: {root}")
    checksum = root / checksum_name
    require(checksum.is_file() and not checksum.is_symlink(), f"missing checksum payload: {checksum_name}")
    others = [row for row in rows if row["name"] != checksum_name]
    require(len(others) == expected_checksum_rows, f"checksum row count differs for {checksum_name}")
    require(checksum.read_bytes() == checksum_bytes(others, checksum_name), f"checksum readback differs: {checksum_name}")
    return rows


def make_notes(source: dict[str, Any], predecessor: Predecessor, clp_rows: dict[str, dict[str, Any]]) -> bytes:
    text = f"""# Program Matematika Indonesia v{VERSION}

Local successor assembly (publication-free) from the immutable v{PREDECESSOR_VERSION} release and the sealed CLP-family boundary.  The GitHub projection contains 121 flat assets: 106 retained predecessor files, three same-name successor replacements, three rotated release names, and nine pure CLP additions.  The Zenodo projection contains 100 top-level files and a deterministic 23-member additions bundle.

The source archive is a deterministic `git archive --format=zip` replay of commit `{source['source_commit']}` and tree `{source['source_tree']}`.  Its ZIP comment binds that commit.  Archive identity: {source['bytes']} bytes, SHA-256 `{source['sha256']}`; members: {source['zip_files']}.

CLP adapter ZIP identity: {clp_rows['CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip']['bytes']} bytes, SHA-256 `{clp_rows['CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip']['sha256']}`.  The nine CLP additions are selected by explicit relative paths in the assembly script; collision replacements are carried under their established predecessor names.

Predecessor receipts were verified byte-for-byte before assembly.  No predecessor asset is deleted or modified, and this local tool performs no network call, credential read, or publication.

Reproducibility scope / Cakupan reproduksibilitas: this CLP adapter ZIP is a deterministic, zero-copy metadata package.  Its embedded manifest, seal, checksums, and every package member are byte-verified.  Full CLP semantic replay was validated in the source workspace against the external authorities named by the embedded manifest: six source/backend archives, four profile license files, seven learner-primary PDFs, and the frozen candidate research/control tree.  Those authorities remain intentionally zero-copy and are not bundled as the complete replay input set in this ZIP.  A ZIP-only download can verify package/seal/checksum identities but cannot perform end-to-end semantic replay; this release makes no standalone public-replay claim.  Each authority remains recorded by path and SHA-256 for any future evidenced public archive-entry mapping.

Cakupan reproduksibilitas: ZIP adapter CLP ini adalah paket metadata deterministik tanpa penyalinan prosa.  Manifest, seal, checksum, dan setiap anggota paket telah diverifikasi byte.  Replay semantik penuh CLP divalidasi di workspace sumber terhadap otoritas eksternal yang tercantum dalam manifest: enam arsip sumber/backend, empat berkas lisensi profil, tujuh PDF pembaca utama, dan pohon research/control kandidat yang dibekukan.  Otoritas tersebut sengaja tetap zero-copy dan tidak dibundel sebagai seluruh input replay di ZIP.  Unduhan ZIP saja dapat memverifikasi identitas paket/seal/checksum, tetapi tidak dapat menjalankan replay semantik end-to-end; rilis ini tidak membuat klaim replay publik mandiri.  Setiap otoritas tetap dicatat dengan path dan SHA-256 untuk pemetaan entri arsip publik yang kelak dapat dibuktikan.

Model provenance: OpenAI Codex gpt-5.6-sol, Ultra.
"""
    return text.replace("\r\n", "\n").encode("utf-8")


def assemble(out_root: Path, predecessor: Predecessor, successor_inputs: dict[str, Path], source_commit: str, source_tree: str) -> dict[str, Any]:
    require(not out_root.exists() and not out_root.is_symlink(), f"refusing to overwrite existing output: {out_root}")
    out_root.mkdir(parents=True, exist_ok=False)
    github = out_root / "github"
    zenodo = out_root / "zenodo"
    work = out_root / ".work"
    github.mkdir()
    zenodo.mkdir()
    work.mkdir()
    try:
        gh_by_name = {row["name"]: row for row in predecessor.github_rows}
        z_by_name = {row["name"]: row for row in predecessor.zenodo_rows}
        require(set(COLLISION_NAMES) <= set(gh_by_name), "predecessor lacks required collision names")
        require({OLD_SOURCE, OLD_GH_CHECKSUM, OLD_NOTES} <= set(gh_by_name), "predecessor lacks required GitHub rotations")
        require({OLD_SOURCE, OLD_ZENODO_CHECKSUM, OLD_BUNDLE} <= set(z_by_name), "predecessor lacks required Zenodo rotations")

        # GitHub: 106 exact retained + 3 same-name replacements.
        retained_gh = set(gh_by_name) - set(COLLISION_NAMES) - {OLD_SOURCE, OLD_GH_CHECKSUM, OLD_NOTES}
        require(len(retained_gh) == 106, f"GitHub retained boundary differs: {len(retained_gh)}")
        for name in sorted(retained_gh):
            copy_bytes(DEFAULT_PREDECESSOR / name, github / name)
        for name in COLLISION_NAMES:
            copy_bytes(successor_inputs[name], github / name)

        source_path, source_details = build_source_archive(
            work,
            source_commit,
            source_tree,
            DEFAULT_PREDECESSOR / OLD_SOURCE,
            successor_inputs,
        )
        copy_bytes(source_path, github / NEW_SOURCE)
        clp_rows = {name: fact(name, path, "sealed_clp_successor_input") for name, path in successor_inputs.items() if name in PURE_ASSET_PATHS}
        notes_path = work / NEW_NOTES
        notes_path.write_bytes(make_notes(source_details, predecessor, clp_rows))
        copy_bytes(notes_path, github / NEW_NOTES)
        for name, path in sorted(successor_inputs.items()):
            if name in PURE_ASSET_PATHS:
                # The CLP ZIP is already represented in source_path only as
                # source code; it must also be a flat GitHub release asset.
                if name == "CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip":
                    target = github / name
                else:
                    target = github / name
                copy_bytes(path, target)
        gh_pre_checksum = rows_for_directory(github)
        require(len(gh_pre_checksum) == 120, f"GitHub pre-checksum count differs: {len(gh_pre_checksum)}")
        (github / NEW_GH_CHECKSUM).write_bytes(checksum_bytes(gh_pre_checksum, NEW_GH_CHECKSUM))
        gh_rows = validate_payload(github, GH_EXPECTED_FILES, NEW_GH_CHECKSUM, GH_EXPECTED_CHECKSUM_ROWS)
        require(len(set(gh_by_name) - set(COLLISION_NAMES) - {OLD_SOURCE, OLD_GH_CHECKSUM, OLD_NOTES}) == 106, "GitHub retained set drift")

        # Zenodo: retain the 97 predecessor direct files other than the old
        # source/checksum/bundle, then rotate those three names.
        retained_z = set(z_by_name) - {OLD_SOURCE, OLD_ZENODO_CHECKSUM, OLD_BUNDLE}
        require(len(retained_z) == 97, f"Zenodo retained direct boundary differs: {len(retained_z)}")
        for name in sorted(retained_z):
            copy_bytes(DEFAULT_PREDECESSOR_ZENODO / name, zenodo / name)
        copy_bytes(source_path, zenodo / NEW_SOURCE)

        old_bundle_path = DEFAULT_PREDECESSOR_ZENODO / OLD_BUNDLE
        inherited: dict[str, tuple[zipfile.ZipFile, str] | Path] = {}
        old_bundle = zipfile.ZipFile(old_bundle_path, "r")
        try:
            old_infos = [info for info in old_bundle.infolist() if not info.is_dir()]
            require(len(old_infos) == 14, f"predecessor additions bundle member count differs: {len(old_infos)}")
            for info in old_infos:
                member_name = info.filename
                require(member_name not in inherited, f"duplicate predecessor bundle member: {member_name}")
                if member_name == OLD_GH_CHECKSUM:
                    inherited[NEW_GH_CHECKSUM] = github / NEW_GH_CHECKSUM
                elif member_name == OLD_NOTES:
                    inherited[NEW_NOTES] = github / NEW_NOTES
                elif member_name in COLLISION_NAMES:
                    inherited[member_name] = successor_inputs[member_name]
                else:
                    inherited[member_name] = (old_bundle, member_name)
            pure_bundle_names = sorted(name for name in PURE_ASSET_PATHS if name != "CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip")
            # All nine pure assets, including the CLP ZIP, enter the bundle.
            for name in sorted(PURE_ASSET_PATHS):
                require(name not in inherited, f"pure CLP name collides with inherited bundle member: {name}")
                inherited[name] = successor_inputs[name]
            bundle_names = sorted(inherited)
            require(len(bundle_names) == BUNDLE_EXPECTED_MEMBERS, f"successor bundle member count differs: {len(bundle_names)}")
            bundle_comment = f"program-matematika-indonesia-v{VERSION}-zenodo-additions|commit={source_commit}|tree={source_tree}".encode("ascii")
            bundle_path = zenodo / NEW_BUNDLE
            write_fixed_zip(bundle_path, [(name, inherited[name]) for name in bundle_names], bundle_comment)
        finally:
            old_bundle.close()
        bundle_rows: dict[str, dict[str, Any]] = {}
        with zipfile.ZipFile(zenodo / NEW_BUNDLE, "r") as bundle:
            for info in bundle.infolist():
                # Identity rows come from the input source bytes, not ZIP
                # metadata, and are read back again by validate_bundle.
                if info.filename in successor_inputs:
                    bundle_rows[info.filename] = fact(info.filename, successor_inputs[info.filename], "successor_bundle_member")
                elif info.filename == NEW_GH_CHECKSUM:
                    bundle_rows[info.filename] = fact(info.filename, github / NEW_GH_CHECKSUM, "rotated_bundle_member")
                elif info.filename == NEW_NOTES:
                    bundle_rows[info.filename] = fact(info.filename, github / NEW_NOTES, "rotated_bundle_member")
                else:
                    # Extracting to a temporary file would duplicate the
                    # bundle; use the known predecessor member hash instead.
                    old_name = {NEW_GH_CHECKSUM: OLD_GH_CHECKSUM, NEW_NOTES: OLD_NOTES}.get(info.filename, info.filename)
                    if old_name in gh_by_name:
                        bundle_rows[info.filename] = {"name": info.filename, "bytes": gh_by_name[old_name]["bytes"], "sha256": gh_by_name[old_name]["sha256"]}
                    else:
                        # The old Zenodo bundle is authoritative for members
                        # that are not GitHub assets; hash them streaming.
                        with zipfile.ZipFile(old_bundle_path, "r") as old:
                            data = old.read(info.filename)
                        bundle_rows[info.filename] = {"name": info.filename, "bytes": len(data), "sha256": sha256_bytes(data)}
        bundle_info = validate_bundle(zenodo / NEW_BUNDLE, bundle_names, bundle_rows, bundle_comment)
        z_pre_checksum = rows_for_directory(zenodo)
        require(len(z_pre_checksum) == 99, f"Zenodo pre-checksum count differs: {len(z_pre_checksum)}")
        (zenodo / NEW_ZENODO_CHECKSUM).write_bytes(checksum_bytes(z_pre_checksum, NEW_ZENODO_CHECKSUM))
        z_rows = validate_payload(zenodo, ZENODO_EXPECTED_FILES, NEW_ZENODO_CHECKSUM, ZENODO_EXPECTED_CHECKSUM_ROWS)

        report = {
            "status": "PASS_ASSEMBLED_NOT_PUBLISHED",
            "version": VERSION,
            "publication": {"network_calls": 0, "credentials_read": 0, "remote_state_touched": False},
            "predecessor": {
                "version": PREDECESSOR_VERSION,
                "github_files": len(predecessor.github_rows),
                "github_bytes": sum(row["bytes"] for row in predecessor.github_rows),
                "github_aggregate_sha256": inventory_aggregate(predecessor.github_rows),
                "github_receipt_sha256": EXPECTED_RECEIPTS["github"][1],
                "zenodo_files": len(predecessor.zenodo_rows),
                "zenodo_bytes": sum(row["bytes"] for row in predecessor.zenodo_rows),
                "zenodo_aggregate_sha256": inventory_aggregate(predecessor.zenodo_rows),
                "zenodo_receipt_sha256": EXPECTED_RECEIPTS["zenodo"][1],
            },
            "boundary": {
                "github": {"retained_exact": 106, "same_name_replacements": list(COLLISION_NAMES), "rotated_names": [{"old": OLD_SOURCE, "new": NEW_SOURCE}, {"old": OLD_GH_CHECKSUM, "new": NEW_GH_CHECKSUM}, {"old": OLD_NOTES, "new": NEW_NOTES}], "pure_additions": sorted(PURE_ASSET_PATHS), "files": GH_EXPECTED_FILES, "checksum_rows": GH_EXPECTED_CHECKSUM_ROWS},
                "zenodo": {"retained_direct": 97, "rotated_names": [{"old": OLD_SOURCE, "new": NEW_SOURCE}, {"old": OLD_ZENODO_CHECKSUM, "new": NEW_ZENODO_CHECKSUM}, {"old": OLD_BUNDLE, "new": NEW_BUNDLE}], "top_level_files": ZENODO_EXPECTED_FILES, "checksum_rows": ZENODO_EXPECTED_CHECKSUM_ROWS, "bundle_members": BUNDLE_EXPECTED_MEMBERS},
            },
            "source_archive": source_details,
            "clp_inputs": {name: row for name, row in sorted(clp_rows.items())},
            "github": {"files": len(gh_rows), "bytes": sum(row["bytes"] for row in gh_rows), "aggregate_sha256": inventory_aggregate(gh_rows), "entries": gh_rows},
            "zenodo": {"files": len(z_rows), "bytes": sum(row["bytes"] for row in z_rows), "aggregate_sha256": inventory_aggregate(z_rows), "bundle": bundle_info, "entries": z_rows},
            "output_root": rel_posix(out_root, PROJECT) if out_root.is_relative_to(PROJECT) else str(out_root),
        }
        return report
    finally:
        # The work directory is private to this invocation and contains only
        # reproducible temporary archives.  Remove it before exposing output.
        if work.exists():
            shutil.rmtree(work)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True, help="full commit SHA for the final successor tree")
    parser.add_argument("--source-tree", required=True, help="full tree SHA corresponding to --source-commit")
    parser.add_argument("--successor-root", type=Path, default=DEFAULT_SUCCESSOR_ROOT)
    parser.add_argument("--predecessor-root", type=Path, default=DEFAULT_PREDECESSOR)
    parser.add_argument("--predecessor-zenodo-root", type=Path, default=DEFAULT_PREDECESSOR_ZENODO)
    parser.add_argument("--out-root", type=Path, help="new narrow output directory for --build")
    parser.add_argument("--report", type=Path, help="optional report path (must not be inside payload directory)")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true", help="assemble in a temporary directory and remove it after validation")
    modes.add_argument("--build", action="store_true", help="assemble and retain a new output directory")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        predecessor_root = args.predecessor_root.resolve()
        predecessor_zenodo_root = args.predecessor_zenodo_root.resolve()
        successor_root = args.successor_root.resolve()
        require(predecessor_root == DEFAULT_PREDECESSOR.resolve(), "this bounded assembler is pinned to releases/v0.62.16")
        require(predecessor_zenodo_root == DEFAULT_PREDECESSOR_ZENODO.resolve(), "this bounded assembler is pinned to releases/v0.62.16-zenodo")
        predecessor = validate_predecessor(predecessor_root, predecessor_zenodo_root)
        successor_inputs = validate_successor_inputs(successor_root)
        if args.preflight:
            with tempfile.TemporaryDirectory(prefix="pmi-v06217-assembly-") as temporary:
                report = assemble(Path(temporary) / "projection", predecessor, successor_inputs, args.source_commit, args.source_tree)
                report["mode"] = "preflight_temporary_removed"
        else:
            require(args.out_root is not None, "--build requires --out-root")
            out_root = ensure_inside(args.out_root, PROJECT / "tmp", "--out-root")
            report = assemble(out_root, predecessor, successor_inputs, args.source_commit, args.source_tree)
            report["mode"] = "build_retained_local_only"
        rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.report is not None:
            report_path = args.report.resolve()
            require(report_path != (args.out_root.resolve() if args.out_root else Path("\\\\invalid")), "report must not be the payload root")
            require(report_path.parent == (args.out_root.resolve().parent if args.out_root else report_path.parent), "report path must be adjacent to output or omitted")
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(rendered, encoding="utf-8", newline="\n")
            report["report"] = str(report_path)
            rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        print(rendered, end="")
        return 0
    except (AssemblyError, OSError, ValueError) as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:2000]
        print(json.dumps({"status": "FAIL_CLOSED", "version": VERSION, "error": detail}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
