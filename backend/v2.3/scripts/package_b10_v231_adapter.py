#!/usr/bin/env python3
"""Create and independently replay a deterministic public B10 v2.3.1 adapter ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath


ROOT_NAME = "program-matematika-indonesia-backend-v2.3.1-b10-adapter-v0.2.0"
FIXED_DATE = (1980, 1, 1, 0, 0, 0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory_sha256(entries: list[dict[str, object]]) -> str:
    data = "".join(
        f"{row['path']}\0{row['bytes']}\0{row['sha256']}\n"
        for row in sorted(entries, key=lambda row: str(row["path"]))
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def compact(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def build(args: argparse.Namespace) -> dict[str, object]:
    packager_path = Path(__file__).resolve()
    packager_bytes = packager_path.read_bytes()
    package = args.package_root.resolve()
    validation_receipt = args.validation_receipt.resolve()
    admission_receipt = args.admission_receipt.resolve()
    output = args.output.resolve()
    receipt_path = args.receipt.resolve()
    require(package.is_dir(), "package root is missing")
    require(validation_receipt.is_file(), "validation receipt is missing")
    require(admission_receipt.is_file(), "canonical admission receipt is missing")
    validation = json.loads(validation_receipt.read_text(encoding="utf-8"))
    admission = json.loads(admission_receipt.read_text(encoding="utf-8"))
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    require(validation["status"] == "pass", "validation receipt is not passing")
    require(validation["package_id"] == manifest["package_id"], "validation/package identity mismatch")
    require(validation["payload_inventory_sha256"] == manifest["build"]["build_a_sha256"], "validation payload identity mismatch")
    require(package.name in validation["build_labels"], "package directory is outside the validated A/B pair")
    require(admission["status"] == "admitted" and admission["package_id"] == manifest["package_id"], "canonical admission identity mismatch")
    require(admission["canonical_extension"]["full_inventory_sha256"] == validation["full_inventory_sha256"], "canonical admission inventory mismatch")

    files = sorted(path for path in package.rglob("*") if path.is_file())
    require(len(files) == validation["files_per_build"], "validated package file count drift")
    source_facts = [
        {
            "path": path.relative_to(package).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in files
    ]
    require(sum(int(row["bytes"]) for row in source_facts) == validation["bytes_per_build"], "validated package byte count drift")
    require(inventory_sha256(source_facts) == validation["full_inventory_sha256"], "validated full inventory identity drift")

    checksum_path = package / "PACKAGE_CHECKSUMS.sha256"
    checksum_rows = checksum_path.read_text(encoding="utf-8").splitlines()
    require(len(checksum_rows) == len(files) - 1, "package checksum row count drift")
    checksum_names: set[str] = set()
    for row in checksum_rows:
        digest, relative = row.split("  ", 1)
        target = package / PurePosixPath(relative)
        require(target.is_file() and sha256(target) == digest, f"package checksum mismatch: {relative}")
        checksum_names.add(relative)
    require(checksum_names == {str(row["path"]) for row in source_facts} - {"PACKAGE_CHECKSUMS.sha256"}, "package checksum closure drift")

    seal = json.loads((package / "seal.json").read_text(encoding="utf-8"))
    require(seal["aggregate_sha256"] == validation["seal_aggregate_sha256"], "validation seal identity drift")
    for row in seal["files"]:
        target = package / PurePosixPath(str(row["path"]))
        require(target.is_file(), f"sealed file missing: {row['path']}")
        require(target.stat().st_size == row["bytes"] and sha256(target) == row["sha256"], f"sealed file mismatch: {row['path']}")
    require(inventory_sha256(seal["files"]) == seal["aggregate_sha256"], "seal inventory replay drift")

    entries: list[dict[str, object]] = []
    archive_rows: list[tuple[str, bytes]] = []
    for path in files:
        relative = path.relative_to(package).as_posix()
        pure = PurePosixPath(relative)
        require(not pure.is_absolute() and ".." not in pure.parts, "unsafe package path")
        data = path.read_bytes()
        archive_name = f"{ROOT_NAME}/{relative}"
        archive_rows.append((archive_name, data))
        entries.append({"path": archive_name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "role": "validated_package_file"})

    validation_bytes = validation_receipt.read_bytes()
    validation_name = f"{ROOT_NAME}/receipts/B10_V23_ADAPTER_VALIDATION_RECEIPT.json"
    archive_rows.append((validation_name, validation_bytes))
    entries.append({"path": validation_name, "bytes": len(validation_bytes), "sha256": hashlib.sha256(validation_bytes).hexdigest(), "role": "validation_receipt"})
    admission_bytes = admission_receipt.read_bytes()
    admission_name = f"{ROOT_NAME}/receipts/B10_V23_ADAPTER_CANONICAL_ADMISSION_RECEIPT.json"
    archive_rows.append((admission_name, admission_bytes))
    entries.append({"path": admission_name, "bytes": len(admission_bytes), "sha256": hashlib.sha256(admission_bytes).hexdigest(), "role": "canonical_admission_receipt"})
    archive_rows.sort(key=lambda row: row[0])
    require(len({row[0] for row in archive_rows}) == len(archive_rows), "duplicate archive names")

    output.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        require(args.force, "output exists; pass --force")
        output.unlink()
    if receipt_path.exists():
        require(args.force, "receipt exists; pass --force")
        receipt_path.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as archive:
        for name, data in archive_rows:
            info = zipfile.ZipInfo(name, FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    with zipfile.ZipFile(output, "r") as archive:
        require(archive.testzip() is None, "ZIP CRC replay failed")
        infos = archive.infolist()
        require([info.filename for info in infos] == [row[0] for row in archive_rows], "ZIP entry order drift")
        require(len({info.filename for info in infos}) == len(infos), "ZIP duplicate names")
        for info, (name, expected) in zip(infos, archive_rows):
            actual = archive.read(info)
            require(info.filename == name and actual == expected, f"ZIP byte replay failed: {name}")
            require(info.date_time == FIXED_DATE, f"ZIP timestamp drift: {name}")

    receipt = {
        "schema_id": "program-matematika-indonesia/b10-v23-adapter-package-receipt/1.0.0",
        "recorded_at": "2026-08-30T00:00:00Z",
        "status": "pass",
        "course_id": "B10",
        "package_id": manifest["package_id"],
        "source_package": {
            "validated_build_label": package.name,
            "files": len(files),
            "bytes": sum(path.stat().st_size for path in files),
            "full_inventory_sha256": validation["full_inventory_sha256"],
            "payload_inventory_sha256": validation["payload_inventory_sha256"],
        },
        "validation_receipt": {
            "bytes": len(validation_bytes),
            "sha256": hashlib.sha256(validation_bytes).hexdigest(),
        },
        "canonical_admission_receipt": {
            "bytes": len(admission_bytes),
            "sha256": hashlib.sha256(admission_bytes).hexdigest(),
        },
        "packager": {
            "path": "backend/v2.3/scripts/package_b10_v231_adapter.py",
            "bytes": len(packager_bytes),
            "sha256": hashlib.sha256(packager_bytes).hexdigest(),
        },
        "archive": {
            "filename": output.name,
            "bytes": output.stat().st_size,
            "sha256": sha256(output),
            "entries": len(entries),
            "uncompressed_bytes": sum(int(row["bytes"]) for row in entries),
            "entry_inventory_sha256": inventory_sha256(entries),
            "crc_test": "pass",
            "byte_replay": "pass",
            "duplicate_names": 0,
            "fixed_timestamp": "1980-01-01T00:00:00",
            "compression": "ZIP_DEFLATED",
            "compression_level": 9,
            "entry_order": "lexicographic_path",
            "unix_file_mode": "100644",
        },
        "scope": "B10 adapter only; owner-native textbook bytes are referenced, not copied.",
        "aggregate_40_role_conformance_claim": False,
        "machine_data_is_learner_destination": False,
        "credentials_recorded": False,
        "personal_name_recorded": False,
    }
    receipt_path.write_bytes((json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    replay = json.loads(receipt_path.read_text(encoding="utf-8"))
    require(replay == receipt, "receipt replay drift")
    return {**receipt, "receipt_bytes": receipt_path.stat().st_size, "receipt_sha256": sha256(receipt_path)}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--validation-receipt", type=Path, required=True)
    parser.add_argument("--admission-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        result = build(parse_args(sys.argv[1:] if argv is None else argv))
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(compact(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
