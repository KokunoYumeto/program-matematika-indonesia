#!/usr/bin/env python3
"""Create and verify a deterministic ZIP from a sealed v2.3.1 adapter."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

from v231_adapter_common import AdapterError, compact_json, parse_checksum_file, require, sha256_file


FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def package_adapter(package: Path, output: Path, replace: bool) -> dict[str, object]:
    package = package.resolve()
    output = output.resolve()
    require(package.is_dir(), f"adapter package missing: {package}")
    require((package / "manifest.json").is_file(), "adapter manifest missing")
    require((package / "seal.json").is_file(), "adapter seal missing")
    require((package / "PACKAGE_CHECKSUMS.sha256").is_file(), "adapter checksums missing")
    require(not output.exists() or replace, "output exists; pass --replace")

    checksum_rows = parse_checksum_file(package / "PACKAGE_CHECKSUMS.sha256")
    checksum_map = {relative: digest for digest, relative in checksum_rows}
    files = sorted(
        (path for path in package.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(package).as_posix(),
    )
    relative_files = [path.relative_to(package).as_posix() for path in files]
    require(set(relative_files) == set(checksum_map) | {"PACKAGE_CHECKSUMS.sha256"}, "physical adapter inventory differs from checksum closure")
    for path, relative in zip(files, relative_files, strict=True):
        if relative != "PACKAGE_CHECKSUMS.sha256":
            require(sha256_file(path) == checksum_map[relative], f"pre-ZIP checksum mismatch: {relative}")

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as archive:
        for path, relative in zip(files, relative_files, strict=True):
            info = zipfile.ZipInfo(relative, FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits |= 0x800
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    with zipfile.ZipFile(output, "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        require(names == relative_files, "ZIP member order/name drift")
        require(len(names) == len(set(names)), "duplicate ZIP member names")
        require(archive.testzip() is None, "ZIP CRC/test failure")
        for path, relative in zip(files, relative_files, strict=True):
            payload = archive.read(relative)
            require(len(payload) == path.stat().st_size, f"ZIP byte-count mismatch: {relative}")
            require(payload == path.read_bytes(), f"ZIP byte identity mismatch: {relative}")

    return {
        "schema_id": "program-matematika-indonesia/deterministic-lane-adapter-zip/1",
        "status": "PASS",
        "package_files": len(files),
        "package_bytes": sum(path.stat().st_size for path in files),
        "zip_path": str(output),
        "zip_bytes": output.stat().st_size,
        "zip_sha256": sha256_file(output),
        "member_order": "lexicographic_posix_path",
        "member_timestamp": "1980-01-01T00:00:00",
        "compression": "deflate_level_9",
        "crc_test": "pass",
        "member_byte_identity": "pass",
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        print(compact_json(package_adapter(args.package, args.output, args.replace)))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
