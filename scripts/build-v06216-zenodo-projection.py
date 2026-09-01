#!/usr/bin/env python3
"""Build the lossless 100-file Zenodo projection for PMI v0.62.16.

The v0.62.14 predecessor has two deliberately distinct public authorities:
112 flat GitHub assets and a lossless 100-file Zenodo projection.  This builder
accepts only the finalized v0.62.16 GitHub authority and produces a fresh
100-file Zenodo projection; it never treats the predecessor Zenodo inventory as
the GitHub inventory.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import sys
import zipfile
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT / "releases/v0.62.16"
TARGET_DIR = PROJECT / "releases/v0.62.16-zenodo"
GITHUB_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.16.json"

UNRESOLVED = "__UNRESOLVED_V0_62_16__"
CONFIGURATION_FINALIZED = True

# These predecessor counts are authority boundaries, not interchangeable
# aliases.  Freeze the successor GitHub count and byte identities only after
# its release directory and anonymous publication receipt exist.
EXPECTED_PREDECESSOR_GITHUB_FILES = 112
EXPECTED_PREDECESSOR_ZENODO_FILES = 100
EXPECTED_GITHUB_RECEIPT: tuple[int | None, str] = (
    87_782,
    "1c5649a9b5fede9b808783d1c353c436ea2d9afedbe950b095933a7b81942c34",
)
EXPECTED_SOURCE_FILES: int | None = 112
EXPECTED_SOURCE_BYTES: int | None = 745_034_611
EXPECTED_SOURCE_AGGREGATE = "4aff7541a77e76ea937b5f4588a621487cb21a68e007bd7008f911dcd4df50b2"
EXPECTED_TARGET_FILES = 100
EXPECTED_DIRECT_GITHUB_FILES = EXPECTED_TARGET_FILES - 2

SOURCE_ARCHIVE_NAME = "program-matematika-indonesia-source-v0.62.16.zip"
ZENODO_BUNDLE_NAME = "program-matematika-indonesia-v0.62.16-zenodo-additions.zip"
ZENODO_CHECKSUM_NAME = "ZENODO_RELEASE_CHECKSUMS_v0.62.16.sha256"
EXPECTED_GITHUB_COMMIT = "42a0656177376d5021a014f3e4d5ae6419d07ae5"
EXPECTED_GITHUB_TREE = "aa648184b56242f1a234c72d55e0d6d44a317b6c"
BUNDLE_COMMENT: bytes | None = (
    b"PMI v0.62.16 Zenodo additions; GitHub tag commit "
    b"42a0656177376d5021a014f3e4d5ae6419d07ae5"
)

BUNDLED_NAMES = frozenset(
    {
        "RELEASE_CHECKSUMS_v0.62.16.sha256",
        "RELEASE_NOTES_v0.62.16.md",
        "comparison-evidence-manifest-v1.json",
        "comparison-evidence-manifest-v1.schema.json",
        "feature-adoption-provenance-v1.json",
        "feature-adoption-provenance-v1.schema.json",
        "modular-backend-pattern-index-v2.json",
        "modular-backend-pattern-index-v2.schema.json",
        "program-matematika-indonesia-c130-operations-research-v2.3.1.zip",
        "program-matematika-indonesia-judson-c30-c40-v2.3.1.zip",
        "program-matematika-indonesia-openlogic-c80-v2.3.1.zip",
        "v23-adapter-index-v2.json",
        "v23-adapter-index-v2.schema.json",
        "MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json",
    }
)


class BuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BuildError(message)


def valid_identity(value: tuple[int | None, str]) -> bool:
    return (
        type(value[0]) is int
        and value[0] >= 0
        and isinstance(value[1], str)
        and re.fullmatch(r"[0-9a-f]{64}", value[1]) is not None
    )


def validate_configuration() -> None:
    require(CONFIGURATION_FINALIZED is True, "successor GitHub artifacts are not finalized")
    require(EXPECTED_PREDECESSOR_GITHUB_FILES == 112, "GitHub predecessor count differs")
    require(EXPECTED_PREDECESSOR_ZENODO_FILES == 100, "Zenodo predecessor count differs")
    require(type(EXPECTED_SOURCE_FILES) is int and EXPECTED_SOURCE_FILES >= 99, "successor GitHub file count is unresolved")
    require(type(EXPECTED_SOURCE_BYTES) is int and EXPECTED_SOURCE_BYTES > 0, "successor GitHub byte total is unresolved")
    require(re.fullmatch(r"[0-9a-f]{64}", EXPECTED_SOURCE_AGGREGATE) is not None, "successor GitHub aggregate is unresolved")
    require(valid_identity(EXPECTED_GITHUB_RECEIPT), "successor GitHub receipt identity is unresolved")
    require(re.fullmatch(r"[0-9a-f]{40}", EXPECTED_GITHUB_COMMIT) is not None, "successor GitHub commit is unresolved")
    require(re.fullmatch(r"[0-9a-f]{40}", EXPECTED_GITHUB_TREE) is not None, "successor GitHub tree is unresolved")
    require(
        BUNDLE_COMMENT
        == f"PMI v0.62.16 Zenodo additions; GitHub tag commit {EXPECTED_GITHUB_COMMIT}".encode("ascii"),
        "bundle comment is not bound to the successor GitHub commit",
    )
    require(
        len(BUNDLED_NAMES) == EXPECTED_SOURCE_FILES - EXPECTED_DIRECT_GITHUB_FILES,
        "bundle member count does not close the 98-direct projection",
    )
    require(UNRESOLVED not in json.dumps(
        {
            "receipt": EXPECTED_GITHUB_RECEIPT,
            "aggregate": EXPECTED_SOURCE_AGGREGATE,
            "commit": EXPECTED_GITHUB_COMMIT,
            "tree": EXPECTED_GITHUB_TREE,
        },
        sort_keys=True,
    ), "configuration contains an unresolved marker")


def preflight() -> dict[str, Any]:
    finalized = CONFIGURATION_FINALIZED is True
    if finalized:
        validate_configuration()
    else:
        require(EXPECTED_GITHUB_RECEIPT == (None, UNRESOLVED), "unfinalized receipt sentinel differs")
        require(EXPECTED_SOURCE_FILES == 112 and EXPECTED_SOURCE_BYTES is None, "unfinalized source counts differ")
        require(EXPECTED_SOURCE_AGGREGATE == UNRESOLVED, "unfinalized aggregate sentinel differs")
        require(
            EXPECTED_GITHUB_COMMIT == "42a0656177376d5021a014f3e4d5ae6419d07ae5"
            and EXPECTED_GITHUB_TREE == "aa648184b56242f1a234c72d55e0d6d44a317b6c",
            "pinned v0.62.16 source commit/tree differs",
        )
        require(
            BUNDLE_COMMENT
            == f"PMI v0.62.16 Zenodo additions; GitHub tag commit {EXPECTED_GITHUB_COMMIT}".encode("ascii"),
            "unfinalized bundle comment is not bound to the pinned commit",
        )
    return {
        "status": (
            "PASS_OFFLINE_PREFLIGHT_CONFIGURATION_FINALIZED"
            if finalized
            else "PASS_OFFLINE_PREFLIGHT_WAITING_FOR_SUCCESSOR_ARTIFACTS"
        ),
        "version": "0.62.16",
        "configuration_finalized": finalized,
        "predecessor_github_files": EXPECTED_PREDECESSOR_GITHUB_FILES,
        "predecessor_zenodo_files": EXPECTED_PREDECESSOR_ZENODO_FILES,
        "zenodo_target_files": EXPECTED_TARGET_FILES,
        "network_calls": 0,
        "credential_reads": 0,
        "filesystem_artifact_reads": 0,
        "writes": 0,
        "pinned_source_commit": EXPECTED_GITHUB_COMMIT,
        "pinned_source_tree": EXPECTED_GITHUB_TREE,
        "remaining_freezes": [] if finalized else [
            "GITHUB_PUBLICATION_RECEIPT_v0.62.16.json byte count and SHA-256",
            "v0.62.16 GitHub release total bytes and inventory aggregate SHA-256",
        ],
    }


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def identity(path: Path) -> tuple[int, str]:
    return path.stat().st_size, sha256_file(path)


def inventory_sha(rows: list[dict[str, Any]]) -> str:
    payload = "".join(
        f"{row['sha256']}  {row['name']}\n"
        for row in sorted(rows, key=lambda item: str(item["name"]))
    ).encode("utf-8")
    return sha256_bytes(payload)


def safe_flat_name(name: str) -> bool:
    return (
        bool(name)
        and name not in {".", ".."}
        and "/" not in name
        and "\\" not in name
        and not any(ord(character) < 32 for character in name)
    )


def load_source_authority() -> tuple[list[dict[str, Any]], dict[str, Path]]:
    validate_configuration()
    require(SOURCE_DIR.is_dir() and not SOURCE_DIR.is_symlink(), "source release directory is absent")
    require(identity(GITHUB_RECEIPT) == EXPECTED_GITHUB_RECEIPT, "GitHub receipt identity differs")
    receipt = json.loads(GITHUB_RECEIPT.read_text(encoding="utf-8"))
    readback = receipt.get("anonymous_asset_readback", {})
    source = receipt.get("source", {})
    inventory = receipt.get("inventory", {})
    require(
        receipt.get("version") == "0.62.16"
        and receipt.get("state") == "published_public_verified"
        and receipt.get("tag") == "v0.62.16",
        "GitHub release state/tag authority differs",
    )
    require(
        isinstance(source, dict)
        and source.get("commit") == EXPECTED_GITHUB_COMMIT
        and source.get("tree") == EXPECTED_GITHUB_TREE
        and source.get("tag_resolves_to_commit") is True,
        "GitHub commit/tag authority differs",
    )
    require(
        isinstance(readback, dict)
        and readback.get("result") == f"pass_{EXPECTED_SOURCE_FILES}_of_{EXPECTED_SOURCE_FILES}",
        "GitHub anonymous readback state differs",
    )
    require(
        isinstance(inventory, dict)
        and inventory.get("files") == EXPECTED_SOURCE_FILES
        and inventory.get("bytes") == EXPECTED_SOURCE_BYTES
        and inventory.get("aggregate_sha256") == EXPECTED_SOURCE_AGGREGATE,
        "GitHub inventory summary differs",
    )
    rows = readback.get("entries")
    require(isinstance(rows, list) and len(rows) == EXPECTED_SOURCE_FILES, "GitHub receipt row count differs")
    paths = {path.name: path for path in SOURCE_DIR.iterdir()}
    require(len(paths) == EXPECTED_SOURCE_FILES, "source release directory count differs")
    require(all(path.is_file() and not path.is_symlink() for path in paths.values()), "source release is not flat regular files")
    by_name: dict[str, dict[str, Any]] = {}
    normalized: list[dict[str, Any]] = []
    for raw in rows:
        require(isinstance(raw, dict), "GitHub receipt contains a malformed row")
        name = str(raw.get("name", ""))
        byte_count = raw.get("bytes")
        digest = str(raw.get("sha256", ""))
        require(safe_flat_name(name) and name not in by_name, f"unsafe or duplicate source name: {name}")
        require(type(byte_count) is int and byte_count >= 0, f"invalid source byte count: {name}")
        require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None, f"invalid source SHA-256: {name}")
        row = {"name": name, "bytes": byte_count, "sha256": digest}
        by_name[name] = row
        normalized.append(row)
    require(set(by_name) == set(paths), "GitHub receipt/source filename sets differ")
    for name, path in paths.items():
        require(identity(path) == (by_name[name]["bytes"], by_name[name]["sha256"]), f"source identity differs: {name}")
    require(sum(int(row["bytes"]) for row in normalized) == EXPECTED_SOURCE_BYTES, "source total bytes differ")
    require(inventory_sha(normalized) == EXPECTED_SOURCE_AGGREGATE, "source aggregate differs")
    require(BUNDLED_NAMES <= set(paths), "bundle member boundary differs")
    require(SOURCE_ARCHIVE_NAME not in BUNDLED_NAMES, "source archive must remain top-level")
    return normalized, paths


def bundle_bytes(paths: dict[str, Path]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.comment = BUNDLE_COMMENT
        for name in sorted(BUNDLED_NAMES):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, paths[name].read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return output.getvalue()


def validate_bundle(data: bytes, paths: dict[str, Path]) -> dict[str, Any]:
    with zipfile.ZipFile(io.BytesIO(data), "r") as archive:
        require(archive.comment == BUNDLE_COMMENT, "bundle comment differs")
        files = [item for item in archive.infolist() if not item.is_dir()]
        names = [item.filename for item in files]
        require(names == sorted(BUNDLED_NAMES), "bundle member order/boundary differs")
        require(len(names) == len(set(names)) == 14, "bundle member names are not unique")
        require(len({item.date_time for item in files}) == 1, "bundle timestamps differ")
        require(archive.testzip() is None, "bundle CRC validation failed")
        for name in names:
            require(archive.read(name) == paths[name].read_bytes(), f"bundle member bytes differ: {name}")
        return {
            "members": len(names),
            "uncompressed_bytes": sum(item.file_size for item in files),
            "crc_validation": "pass",
        }


def target_rows(directory: Path) -> list[dict[str, Any]]:
    paths = sorted(directory.iterdir(), key=lambda path: path.name)
    require(len(paths) == EXPECTED_TARGET_FILES, "Zenodo projection is not 100 entries")
    require(all(path.is_file() and not path.is_symlink() for path in paths), "Zenodo projection is not flat regular files")
    return [
        {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in paths
    ]


def build() -> dict[str, Any]:
    validate_configuration()
    _, source_paths = load_source_authority()
    require(not TARGET_DIR.exists(), "Zenodo projection target already exists; refusing an ambiguous rebuild")
    temp = TARGET_DIR.with_name(TARGET_DIR.name + ".tmp-build")
    require(not temp.exists(), "Zenodo projection temporary directory already exists")
    temp.mkdir(parents=False)
    try:
        direct_names = sorted(set(source_paths) - BUNDLED_NAMES)
        require(len(direct_names) == EXPECTED_DIRECT_GITHUB_FILES, "direct original asset count differs")
        for name in direct_names:
            destination = temp / name
            try:
                os.link(source_paths[name], destination)
            except OSError:
                shutil.copyfile(source_paths[name], destination)

        first = bundle_bytes(source_paths)
        second = bundle_bytes(source_paths)
        require(first == second, "Zenodo additions bundle is not byte-deterministic")
        bundle_detail = validate_bundle(first, source_paths)
        (temp / ZENODO_BUNDLE_NAME).write_bytes(first)

        manifest_paths = sorted(temp.iterdir(), key=lambda path: path.name)
        require(len(manifest_paths) == EXPECTED_TARGET_FILES - 1, "pre-checksum Zenodo projection count differs")
        checksum = "".join(
            f"{sha256_file(path)}  {path.name}\n" for path in manifest_paths
        ).encode("utf-8")
        (temp / ZENODO_CHECKSUM_NAME).write_bytes(checksum)

        rows = target_rows(temp)
        checksum_rows: dict[str, str] = {}
        for line in checksum.decode("utf-8").splitlines():
            digest, name = line.split("  ", 1)
            require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None, "Zenodo checksum digest is malformed")
            require(name not in checksum_rows, "Zenodo checksum names are not unique")
            checksum_rows[name] = digest
        require(set(checksum_rows) == {row["name"] for row in rows} - {ZENODO_CHECKSUM_NAME}, "Zenodo checksum coverage differs")
        for row in rows:
            if row["name"] != ZENODO_CHECKSUM_NAME:
                require(checksum_rows[row["name"]] == row["sha256"], f"Zenodo checksum differs: {row['name']}")

        temp.replace(TARGET_DIR)
        return {
            "status": "pass",
            "target": TARGET_DIR.relative_to(PROJECT).as_posix(),
            "top_level_files": len(rows),
            "top_level_bytes": sum(int(row["bytes"]) for row in rows),
            "top_level_aggregate_sha256": inventory_sha(rows),
            "original_github_assets_preserved": EXPECTED_SOURCE_FILES,
            "direct_original_assets": len(direct_names),
            "nested_original_assets": len(BUNDLED_NAMES),
            "bundle": {
                "name": ZENODO_BUNDLE_NAME,
                "bytes": len(first),
                "sha256": sha256_bytes(first),
                **bundle_detail,
            },
            "checksum": {
                "name": ZENODO_CHECKSUM_NAME,
                "bytes": len(checksum),
                "sha256": sha256_bytes(checksum),
                "rows": len(checksum_rows),
            },
        }
    except BaseException:
        if temp.exists() and temp.resolve().parent == TARGET_DIR.resolve().parent:
            shutil.rmtree(temp)
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", action="store_true", help="validate configuration without artifact reads or writes")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = preflight() if args.preflight else build()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(f"FAIL: {type(exc).__name__}: {detail}", file=sys.stderr)
        raise SystemExit(1)
