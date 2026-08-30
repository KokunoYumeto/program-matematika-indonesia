#!/usr/bin/env python3
"""Build and verify the deterministic public course-capsule v1 package."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import zipfile
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "backend"
    / "course-capsule-v1"
    / "builds"
    / "program-matematika-indonesia-course-capsule-v1.zip"
)
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

EXACT_MEMBERS = (
    "backend/course-capsule-v1/README.md",
    "backend/course-capsule-v1/authority/integration-overrides-v1.json",
    "backend/course-capsule-v1/generated/course-capsules.json",
    "backend/course-capsule-v1/generated/course-capsules.jsonl",
    "backend/course-capsule-v1/generated/manifest.json",
    "backend/course-capsule-v1/validation/SITE_VALIDATION_RECEIPT.json",
    "backend/course-capsule-v1/validation/VALIDATION_RECEIPT.json",
    "backend/authority/learner-delivery-v1.json",
    "schemas/course-capsule-v1/course-capsule-v1.schema.json",
    "scripts/build-and-validate-course-capsules-v1.mjs",
    "scripts/build-course-capsules-v1.mjs",
    "scripts/sync-course-capsules-v1.mjs",
    "scripts/validate-course-capsule-site-v1.mjs",
    "scripts/validate-course-capsules-v1.mjs",
    "docs/courses.js",
    "docs/live-course-publications.js",
)

TREE_MEMBERS = (
    "docs/backend",
    "docs/data/course-capsule-v1",
    "docs/schema/course-capsule-v1",
)

FORBIDDEN_MEMBERS = {
    "backend/course-capsule-v1/INTEGRATION_GOAL.md",
    "backend/course-capsule-v1/INTEGRATION_LOG.md",
}

PRIVATE_PATH_PATTERNS = (
    re.compile(
        rb"(?i)(?:^|[^A-Za-z0-9])[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\"']{1,64}[\\/]"
    ),
    re.compile(rb"(?i)(?:^|[^A-Za-z0-9])/(?:home|Users)/[^/\s]+/"),
    re.compile(rb"(?i)(?:^|[^A-Za-z0-9])\\\\[^\\\s]+\\[^\\\s]+"),
    re.compile(rb"(?i)[\\/]\.codex[\\/]"),
)

CREDENTIAL_PATTERNS = (
    re.compile(rb"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(rb"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{20,}"),
    re.compile(
        rb"(?i)[\"'](?:access[_-]?token|api[_-]?key|client[_-]?secret)[\"']\s*:\s*[\"'][^\"']{8,}[\"']"
    ),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def collect_members() -> dict[str, bytes]:
    names = set(EXACT_MEMBERS)
    for relative_root in TREE_MEMBERS:
        root = ROOT / relative_root
        if not root.is_dir():
            raise FileNotFoundError(f"required directory is missing: {relative_root}")
        for path in root.rglob("*"):
            if path.is_file():
                names.add(path.relative_to(ROOT).as_posix())

    overlap = names & FORBIDDEN_MEMBERS
    if overlap:
        raise RuntimeError(f"forbidden integration files selected: {sorted(overlap)}")

    members: dict[str, bytes] = {}
    for name in sorted(names):
        path = ROOT / Path(name)
        if not path.is_file():
            raise FileNotFoundError(f"required file is missing: {name}")
        data = path.read_bytes()
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(data):
                raise RuntimeError(f"private absolute path rejected in {name}")
        for pattern in CREDENTIAL_PATTERNS:
            if pattern.search(data):
                raise RuntimeError(f"credential-shaped material rejected in {name}")
        members[name] = data
    return members


def write_zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(
        path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for name, data in members.items():
            info = zipfile.ZipInfo(filename=name, date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(
                info,
                data,
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )


def verify_zip(path: Path, members: dict[str, bytes]) -> None:
    expected_names = list(members)
    with zipfile.ZipFile(path, mode="r") as archive:
        infos = archive.infolist()
        actual_names = [info.filename for info in infos]
        if actual_names != expected_names:
            raise RuntimeError("ZIP member order or inventory differs from the allow-list")
        if len(actual_names) != len(set(actual_names)):
            raise RuntimeError("ZIP contains duplicate member names")
        if archive.testzip() is not None:
            raise RuntimeError("ZIP CRC verification failed")
        for info in infos:
            data = archive.read(info.filename)
            expected = members[info.filename]
            if data != expected:
                raise RuntimeError(f"ZIP member bytes differ: {info.filename}")
            if info.CRC != (zlib.crc32(expected) & 0xFFFFFFFF):
                raise RuntimeError(f"ZIP member CRC differs: {info.filename}")
            if info.date_time != FIXED_TIMESTAMP:
                raise RuntimeError(f"ZIP member timestamp differs: {info.filename}")


def main() -> None:
    members = collect_members()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="course-capsule-v1-") as temp_dir:
        first = Path(temp_dir) / "first.zip"
        second = Path(temp_dir) / "second.zip"
        write_zip(first, members)
        write_zip(second, members)
        verify_zip(first, members)
        verify_zip(second, members)
        first_bytes = first.read_bytes()
        second_bytes = second.read_bytes()
        if first_bytes != second_bytes:
            raise RuntimeError("two-build deterministic replay differs")
        os.replace(first, OUTPUT)

    verify_zip(OUTPUT, members)
    archive_bytes = OUTPUT.read_bytes()
    result = {
        "archive": OUTPUT.relative_to(ROOT).as_posix(),
        "bytes": len(archive_bytes),
        "sha256": sha256(archive_bytes),
        "member_count": len(members),
        "payload_bytes": sum(len(data) for data in members.values()),
        "member_names": list(members),
        "verification": {
            "allow_list_exact": True,
            "forbidden_members_absent": True,
            "member_bytes_exact": True,
            "crc_pass": True,
            "fixed_timestamps": True,
            "private_path_scan_pass": True,
            "credential_scan_pass": True,
            "two_build_byte_replay_pass": True,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
