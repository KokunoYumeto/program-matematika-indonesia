#!/usr/bin/env python3
"""Build and verify the deterministic federation v2.1 pilot package."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


FIXED_ZIP_TIME = (2026, 8, 26, 0, 0, 0)
PREFIX = "program-matematika-indonesia-backend-v2.1/"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add_bytes(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    source = root / "backend" / "v2.1"
    output = args.output.resolve()
    if not source.is_dir() or not output.is_relative_to(root):
        raise ValueError("source backend/v2.1 must exist and output must remain inside the repository")

    files = [
        path
        for path in sorted(source.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    entries = {
        f"{PREFIX}{path.relative_to(source).as_posix()}": path.read_bytes()
        for path in files
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w") as archive:
        for name in sorted(entries):
            add_bytes(archive, name, entries[name])

    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("v2.1 pilot package contains a corrupt member")
        if archive.namelist() != sorted(entries):
            raise ValueError("v2.1 pilot package inventory/order mismatch")
        for name, data in entries.items():
            if archive.read(name) != data:
                raise ValueError(f"v2.1 pilot package byte mismatch: {name}")

    payload = output.read_bytes()
    print(
        json.dumps(
            {
                "path": output.as_posix(),
                "entries": len(entries),
                "uncompressed_bytes": sum(len(data) for data in entries.values()),
                "bytes": len(payload),
                "sha256": sha256(payload),
                "verification": "pass",
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
