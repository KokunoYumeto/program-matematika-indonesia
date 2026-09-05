#!/usr/bin/env python3
"""Build and replay the metadata/evidence-only D100 capability packet."""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from build_d100_capability_v1 import DEFAULT_ADAPTER, DEFAULT_NATIVE, PROJECT
from d100_capability_model_v1 import (
    COURSE_ID,
    file_identity,
    read_json,
    sha256_bytes,
    write_bytes,
    write_json,
)


ADAPTER_REL = Path("backend/course-capsule-v1/adapters/d100-capability-v1")
DEFAULT_OUTPUT = DEFAULT_ADAPTER / "build"
ARCHIVE_NAME = "D100_THIN_CAPABILITY_METADATA_V1.zip"
RECEIPT_NAME = "PACKET_BUILD_RECEIPT.json"
SCRIPT_NAMES = (
    "d100_capability_model_v1.py",
    "build_d100_capability_v1.py",
    "validate_d100_capability_v1.py",
    "package_d100_capability_v1.py",
)
PUBLICATION_NAMES = (
    "GITHUB_READBACK_9b9480ff5b2c.json",
    "GITHUB_READBACK_d80d17cf191b.json",
    "GITHUB_READBACK_f119c2d97073.json",
)
FORBIDDEN_SUFFIXES = {
    ".pdf", ".tex", ".ltx", ".sty", ".cls", ".bib", ".bbl",
    ".dtx", ".ins", ".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg",
}
LOCAL_PROFILE_PATTERN = re.compile(
    rb"(?i)(?:[A-Za-z]:[\\/]+Users[\\/]+[^\\/\r\n\t\"']+|/(?:home|Users)/[^/\r\n\t\"']+)"
)


class PacketError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def safe_relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value.replace("\\", "/"))
    if (
        not value
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
        or (path.parts and ":" in path.parts[0])
    ):
        raise PacketError("D100-PACKET-UNSAFE-PATH:" + value)
    return path


def safe_member(name: str) -> bool:
    try:
        path = safe_relative_path(name)
    except PacketError:
        return False
    return path.as_posix() == name


def collect_members(native: Path, adapter: Path) -> dict[str, bytes]:
    required = (
        adapter / "manifest.json",
        adapter / "validation.json",
        adapter / "README.md",
        adapter / "input/source-lock.json",
    )
    for path in required:
        if not path.is_file():
            raise PacketError("D100-PACKET-REQUIRED-FILE-MISSING:" + path.name)

    members: dict[str, bytes] = {}

    def add(name: str, path: Path) -> None:
        normalized = PurePosixPath(name).as_posix()
        if not safe_member(normalized) or normalized in members:
            raise PacketError("D100-PACKET-MEMBER-PATH:" + normalized)
        if path.suffix.casefold() in FORBIDDEN_SUFFIXES:
            raise PacketError("D100-PACKET-FORBIDDEN-PAYLOAD:" + normalized)
        data = path.read_bytes()
        if LOCAL_PROFILE_PATTERN.search(data):
            raise PacketError("D100-PACKET-LOCAL-PROFILE-DATA:" + normalized)
        members[normalized] = data

    manifest = read_json(adapter / "manifest.json")
    declared_outputs = {safe_relative_path(str(row["path"])) for row in manifest.get("outputs", [])}
    fixtures = {
        PurePosixPath(path.relative_to(adapter).as_posix())
        for path in (adapter / "fixtures/negative").glob("*.json")
        if path.is_file()
    }
    publication = {PurePosixPath("publication") / name for name in PUBLICATION_NAMES}
    for relative in publication:
        receipt = read_json(adapter / Path(relative.as_posix()))
        if receipt.get("state") != "pass" or receipt.get("failure_count") not in (None, 0):
            raise PacketError("D100-PACKET-PUBLIC-RECEIPT-STATE:" + relative.as_posix())
    allowed_adapter = declared_outputs | fixtures | publication | {
        PurePosixPath("manifest.json"),
        PurePosixPath("validation.json"),
        PurePosixPath("README.md"),
        PurePosixPath("input/source-lock.json"),
    }
    actual_adapter = {
        PurePosixPath(path.relative_to(adapter).as_posix())
        for path in adapter.rglob("*")
        if path.is_file() and path.relative_to(adapter).parts[0] != "build"
    }
    if actual_adapter != allowed_adapter:
        missing = sorted(path.as_posix() for path in allowed_adapter - actual_adapter)
        extra = sorted(path.as_posix() for path in actual_adapter - allowed_adapter)
        raise PacketError(f"D100-PACKET-ADAPTER-FILE-SET:missing={missing}:extra={extra}")
    for relative in sorted(allowed_adapter, key=lambda item: item.as_posix()):
        add((ADAPTER_REL / Path(relative.as_posix())).as_posix(), adapter / Path(relative.as_posix()))

    for name in SCRIPT_NAMES:
        add((Path("scripts") / name).as_posix(), PROJECT / "scripts" / name)

    lock = read_json(adapter / "input/source-lock.json")
    if len(lock.get("inputs", [])) != 19:
        raise PacketError("D100-PACKET-LOCK-COUNT")
    for row in lock["inputs"]:
        relative = safe_relative_path(str(row["path"]))
        source = native / Path(relative.as_posix())
        identity = file_identity(source)
        expected = {"bytes": row.get("bytes"), "sha256": row.get("sha256")}
        if identity != expected:
            raise PacketError("D100-PACKET-LOCK-DRIFT:" + relative.as_posix())
        add((Path("native") / Path(relative.as_posix())).as_posix(), source)

    start_here = """# D100 thin capability validation packet

This packet contains the D100 common-backend adapter, its four standard-library
Python scripts, public readback evidence, negative fixtures, and the 19 exact
hash-locked native inputs required for deterministic adapter replay. Those
inputs include structured JSON/JSONL records with mathematical Markdown; this
is not a metadata-only package. It excludes PDFs, TeX, images, source archives,
rendered reader/book files, credentials, caches, and runtime artifacts.

From this extracted directory run:

    python -B scripts/build_d100_capability_v1.py --native-root native --output-root backend/course-capsule-v1/adapters/d100-capability-v1 --source-lock backend/course-capsule-v1/adapters/d100-capability-v1/input/source-lock.json
    python -B scripts/validate_d100_capability_v1.py --native-root native --output-root backend/course-capsule-v1/adapters/d100-capability-v1 --source-lock backend/course-capsule-v1/adapters/d100-capability-v1/input/source-lock.json --receipt backend/course-capsule-v1/adapters/d100-capability-v1/validation.json

This is a metadata/evidence projection, not a complete native-book roundtrip.
The native build and strict source-profile replay remain available but unverified.
""".encode("utf-8")
    members["START_HERE.md"] = start_here
    inventory = {
        "schema": "d100-capability-thin-packet-inventory/1",
        "course_id": COURSE_ID,
        "content_policy": "adapter_plus_hash_locked_structured_native_replay_inputs",
        "structured_mathematical_payloads_included": True,
        "full_native_roundtrip_claimed": False,
        "native_build_claimed_verified": False,
        "strict_source_profile_replay_claimed": False,
        "included_before_inventory": [
            {"path": name, "bytes": len(data), "sha256": sha256_bytes(data)}
            for name, data in sorted(members.items())
        ],
        "locked_native_inputs": 19,
        "public_readback_receipts": len(publication),
        "negative_fixtures": len(fixtures),
        "exclusions": [
            "PDF, TeX, image, and source-archive bytes",
            "rendered reader and book files; structured Markdown records are included",
            "credentials, caches, logs, and runtime artifacts",
        ],
    }
    members["PACKET_INVENTORY.json"] = canonical_json(inventory)
    return members


def zip_bytes(members: dict[str, bytes]) -> bytes:
    sink = io.BytesIO()
    with zipfile.ZipFile(sink, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100644 & 0xFFFF) << 16
            info.extra = b""
            info.comment = b""
            info.flag_bits |= 0x800
            archive.writestr(info, members[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return sink.getvalue()


def verify_zip(payload: bytes, members: dict[str, bytes]) -> dict[str, Any]:
    with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if names != sorted(members) or len(names) != len(set(names)):
            raise PacketError("D100-PACKET-ZIP-INVENTORY")
        if archive.testzip() is not None:
            raise PacketError("D100-PACKET-ZIP-CRC")
        for info in infos:
            if not safe_member(info.filename):
                raise PacketError("D100-PACKET-ZIP-PATH:" + info.filename)
            if info.date_time != (1980, 1, 1, 0, 0, 0) or info.extra or info.comment:
                raise PacketError("D100-PACKET-ZIP-METADATA:" + info.filename)
            data = archive.read(info.filename)
            if data != members[info.filename] or info.file_size != len(data):
                raise PacketError("D100-PACKET-ZIP-BYTES:" + info.filename)
    return {
        "sorted_member_order": True,
        "fixed_member_metadata": True,
        "crc_and_full_entry_readback": True,
        "member_count": len(members),
        "payload_bytes": sum(len(data) for data in members.values()),
    }


def run_checked(command: list[str], cwd: Path, code: str) -> None:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=600)
    if result.returncode:
        raise PacketError(code + ":" + (result.stderr or result.stdout).strip())


def extracted_replay(payload: bytes, members: dict[str, bytes]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="d100-thin-packet-") as temporary:
        root = Path(temporary)
        with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
            for info in archive.infolist():
                if not safe_member(info.filename):
                    raise PacketError("D100-PACKET-EXTRACT-PATH")
                destination = root / PurePosixPath(info.filename)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(info.filename))
        adapter = root / ADAPTER_REL
        native = root / "native"
        lock = adapter / "input/source-lock.json"
        run_checked(
            [sys.executable, "-B", str(root / "scripts/build_d100_capability_v1.py"), "--native-root", str(native), "--output-root", str(adapter), "--source-lock", str(lock)],
            root,
            "D100-PACKET-EXTRACTED-BUILD",
        )
        run_checked(
            [sys.executable, "-B", str(root / "scripts/validate_d100_capability_v1.py"), "--native-root", str(native), "--output-root", str(adapter), "--source-lock", str(lock), "--receipt", str(adapter / "validation.json")],
            root,
            "D100-PACKET-EXTRACTED-VALIDATE",
        )
        adapter_prefix = ADAPTER_REL.as_posix() + "/"
        checked = 0
        for name, expected in members.items():
            if not name.startswith(adapter_prefix):
                continue
            if (root / PurePosixPath(name)).read_bytes() != expected:
                raise PacketError("D100-PACKET-EXTRACTED-DRIFT:" + name)
            checked += 1
        validation = read_json(adapter / "validation.json")
        if validation.get("state") != "pass":
            raise PacketError("D100-PACKET-EXTRACTED-VALIDATION")
        return {
            "extraction_safe": True,
            "rebuild_pass": True,
            "validation_pass": True,
            "rebuilt_adapter_bytes_identical": True,
            "rebuilt_adapter_file_count": checked,
            "validation_receipt": file_identity(adapter / "validation.json"),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    native = args.native.resolve()
    adapter = args.adapter.resolve()
    output = args.output.resolve()
    run_checked(
        [sys.executable, "-B", str(PROJECT / "scripts/validate_d100_capability_v1.py"), "--native-root", str(native), "--output-root", str(adapter), "--source-lock", str(adapter / "input/source-lock.json"), "--receipt", str(adapter / "validation.json")],
        PROJECT,
        "D100-PACKET-PREVALIDATION",
    )
    members = collect_members(native, adapter)
    first = zip_bytes(members)
    second = zip_bytes(members)
    if first != second:
        raise PacketError("D100-PACKET-TWO-BUILD-DRIFT")
    checks = verify_zip(first, members)
    replay = extracted_replay(first, members)
    output.mkdir(parents=True, exist_ok=True)
    archive_path = output / ARCHIVE_NAME
    write_bytes(archive_path, first)
    receipt = {
        "schema": "d100-capability-thin-packet-build-receipt/1",
        "course_id": COURSE_ID,
        "result": "PASS",
        "archive": {"path": (Path("build") / ARCHIVE_NAME).as_posix(), **file_identity(archive_path)},
        "adapter_manifest": file_identity(adapter / "manifest.json"),
        "adapter_validation": file_identity(adapter / "validation.json"),
        "content_policy": "adapter_plus_hash_locked_structured_native_replay_inputs",
        "structured_mathematical_payloads_included": True,
        "full_native_roundtrip_claimed": False,
        "native_build_claimed_verified": False,
        "strict_source_profile_replay_claimed": False,
        "public_state_changed": False,
        "forbidden_payloads_included": False,
        "local_profile_data_included": False,
        "locked_inputs_included": 19,
        "public_readback_receipts_included": len(PUBLICATION_NAMES),
        "negative_fixtures_included": len(list((adapter / "fixtures/negative").glob("*.json"))),
        "two_build_byte_identity": True,
        "zip_checks": checks,
        "extracted_replay": replay,
    }
    write_json(output / RECEIPT_NAME, receipt)
    print(json.dumps({"result": "PASS", "archive": str(archive_path), "identity": receipt["archive"], "members": checks["member_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (PacketError, KeyError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired, zipfile.BadZipFile) as exc:
        print(f"D100 packet build failed: {exc}", file=sys.stderr)
        sys.exit(1)
