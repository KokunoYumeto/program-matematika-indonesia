#!/usr/bin/env python3
"""Build the lossless 100-file Zenodo projection for PMI v0.62.14."""

from __future__ import annotations

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
SOURCE_DIR = PROJECT / "releases/v0.62.14"
TARGET_DIR = PROJECT / "releases/v0.62.14-zenodo"
GITHUB_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.14.json"

EXPECTED_GITHUB_RECEIPT = (
    88_060,
    "8a3883c811574864f0d40f029d1f48ca13870327feb0e9048cd3cad1d1abf390",
)
EXPECTED_SOURCE_FILES = 112
EXPECTED_SOURCE_BYTES = 744_845_735
EXPECTED_SOURCE_AGGREGATE = (
    "4aa98d92ad3c84752d6914f24b568a46adb27994c75676d5b8a5b86400a5502f"
)
EXPECTED_TARGET_FILES = 100

SOURCE_ARCHIVE_NAME = "program-matematika-indonesia-source-v0.62.14.zip"
ZENODO_BUNDLE_NAME = "program-matematika-indonesia-v0.62.14-zenodo-additions.zip"
ZENODO_CHECKSUM_NAME = "ZENODO_RELEASE_CHECKSUMS_v0.62.14.sha256"
BUNDLE_COMMENT = (
    b"PMI v0.62.14 Zenodo additions; GitHub tag commit "
    b"809baf41177fc4f0fca3c5f696c36be152ec2c01"
)

BUNDLED_NAMES = frozenset(
    {
        "RELEASE_CHECKSUMS_v0.62.14.sha256",
        "RELEASE_NOTES_v0.62.14.md",
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
    require(SOURCE_DIR.is_dir() and not SOURCE_DIR.is_symlink(), "source release directory is absent")
    require(identity(GITHUB_RECEIPT) == EXPECTED_GITHUB_RECEIPT, "GitHub receipt identity differs")
    receipt = json.loads(GITHUB_RECEIPT.read_text(encoding="utf-8"))
    readback = receipt.get("anonymous_asset_readback", {})
    rows = readback.get("entries")
    require(isinstance(rows, list) and len(rows) == EXPECTED_SOURCE_FILES, "GitHub receipt is not 112 rows")
    paths = {path.name: path for path in SOURCE_DIR.iterdir()}
    require(len(paths) == EXPECTED_SOURCE_FILES, "source release directory is not 112 entries")
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
    require(len(BUNDLED_NAMES) == 14 and BUNDLED_NAMES <= set(paths), "bundle member boundary differs")
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
    _, source_paths = load_source_authority()
    require(not TARGET_DIR.exists(), "Zenodo projection target already exists; refusing an ambiguous rebuild")
    temp = TARGET_DIR.with_name(TARGET_DIR.name + ".tmp-build")
    require(not temp.exists(), "Zenodo projection temporary directory already exists")
    temp.mkdir(parents=False)
    try:
        direct_names = sorted(set(source_paths) - BUNDLED_NAMES)
        require(len(direct_names) == 98, "direct original asset count differs")
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


def main() -> None:
    print(json.dumps(build(), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(f"FAIL: {type(exc).__name__}: {detail}", file=sys.stderr)
        raise SystemExit(1)
