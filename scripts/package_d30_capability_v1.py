#!/usr/bin/env python3
"""Create and replay the deterministic metadata-only D30 adapter packet."""

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

from d30_capability_model_v1 import COURSE_ID, file_identity, load_bundle, read_json, sha256_bytes, validate_bundle, write_bytes, write_json


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_NATIVE = Path(r"C:\Users\Floris\Documents\interlanguage\04_mirrors\id\measure-theoretic-probability-stochastic-processes-id")
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/d30-capability-v1"
ADAPTER_REL = Path("backend/course-capsule-v1/adapters/d30-capability-v1")
ARCHIVE_NAME = "D30_THIN_CAPABILITY_METADATA_V1.zip"
RECEIPT_NAME = "PACKET_BUILD_RECEIPT.json"
SCRIPT_NAMES = (
    "d30_capability_model_v1.py",
    "build_d30_capability_v1.py",
    "validate_d30_capability_v1.py",
    "package_d30_capability_v1.py",
    "admit-d30-capability-v1.mjs",
)
FORBIDDEN_SUFFIXES = {".pdf", ".tex", ".ltx", ".bib", ".epub", ".csv", ".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg", ".ipynb", ".rmd"}
LOCAL_PROFILE_PATTERN = re.compile(rb"(?i)(?:[A-Za-z]:[\\/]+Users[\\/]+[^\\/\r\n\t\"']+|/(?:home|Users)/[^/\r\n\t\"']+)")


class PacketError(ValueError):
    pass


def safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts) and not (path.parts and ":" in path.parts[0]) and path.as_posix() == name


def add_member(members: dict[str, bytes], name: str, data: bytes) -> None:
    if not safe_member(name) or name in members:
        raise PacketError("D30-PACKET-PATH:" + name)
    if PurePosixPath(name).suffix.casefold() in FORBIDDEN_SUFFIXES:
        raise PacketError("D30-PACKET-FORBIDDEN-PAYLOAD:" + name)
    if LOCAL_PROFILE_PATTERN.search(data):
        raise PacketError("D30-PACKET-LOCAL-PROFILE:" + name)
    members[name] = data


def portable_script_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    local_native = "\\".join(["C:", "Users", "Floris", "Documents", "interlanguage", "04_mirrors", "id", "measure-theoretic-probability-stochastic-processes-id"]).encode("utf-8")
    return data.replace(local_native, b"native")


def collect_members(adapter: Path) -> dict[str, bytes]:
    manifest = read_json(adapter / "manifest.json")
    members: dict[str, bytes] = {}
    adapter_paths = ["manifest.json", "validation.json", *[row["path"] for row in manifest["outputs"]]]
    for relative in sorted(set(adapter_paths)):
        add_member(members, (ADAPTER_REL / relative).as_posix(), (adapter / relative).read_bytes())
    for name in SCRIPT_NAMES:
        add_member(members, f"scripts/{name}", portable_script_bytes(PROJECT / "scripts" / name))
    start = b"# D30 thin capability packet\n\nMetadata and evidence only. Native prose, formulas, code, HTML, PDF, notebooks, and archives are excluded. Supply the pinned native checkout with `--native` to rebuild or validate.\n"
    add_member(members, "START_HERE.md", start)
    inventory = {
        "schema": "d30-capability-thin-packet-inventory/1", "course_id": COURSE_ID,
        "content_policy": "identity_state_rights_evidence_only", "native_payloads_included": False,
        "external_pinned_native_checkout_required": True,
        "included_before_inventory": [{"path": name, "bytes": len(data), "sha256": sha256_bytes(data)} for name, data in sorted(members.items())],
        "exclusions": ["native prose and formula bodies", "HTML/PDF/EPUB and source archives", "notebooks and runtime artifacts", "credentials, logs, caches, and local profile paths"],
    }
    add_member(members, "PACKET_INVENTORY.json", (json.dumps(inventory, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return members


def zip_bytes(members: dict[str, bytes]) -> bytes:
    sink = io.BytesIO()
    with zipfile.ZipFile(sink, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100644 & 0xFFFF) << 16
            info.flag_bits |= 0x800
            archive.writestr(info, members[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return sink.getvalue()


def verify_zip(payload: bytes, members: dict[str, bytes]) -> dict[str, Any]:
    with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
        infos = archive.infolist()
        if [row.filename for row in infos] != sorted(members) or archive.testzip() is not None:
            raise PacketError("D30-PACKET-ZIP-INVENTORY")
        for info in infos:
            if not safe_member(info.filename) or info.date_time != (1980, 1, 1, 0, 0, 0) or info.extra or info.comment:
                raise PacketError("D30-PACKET-ZIP-METADATA:" + info.filename)
            if archive.read(info.filename) != members[info.filename]:
                raise PacketError("D30-PACKET-ZIP-BYTES:" + info.filename)
    return {"member_count": len(members), "sorted_member_order": True, "fixed_member_metadata": True, "crc_and_full_entry_readback": True}


def run_checked(command: list[str], cwd: Path, code: str, timeout: int = 300) -> None:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise PacketError(code + ":" + (result.stderr or result.stdout).strip())


def extracted_replay(payload: bytes, native: Path, expected_adapter: Path, members: dict[str, bytes]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="d30-thin-packet-") as temporary:
        root = Path(temporary)
        with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
            for info in archive.infolist():
                if not safe_member(info.filename):
                    raise PacketError("D30-PACKET-EXTRACT-PATH")
                target = root / PurePosixPath(info.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(info.filename))
        adapter = root / ADAPTER_REL
        run_checked([sys.executable, "-B", str(root / "scripts/validate_d30_capability_v1.py"), "--native", str(native), "--output", str(adapter), "--receipt", str(adapter / "validation.json")], root, "D30-PACKET-EXTRACTED-VALIDATE", 360)
        prefix = ADAPTER_REL.as_posix() + "/"
        checked = 0
        for name, expected in members.items():
            if name.startswith(prefix):
                if (root / PurePosixPath(name)).read_bytes() != expected:
                    raise PacketError("D30-PACKET-EXTRACTED-DRIFT:" + name)
                checked += 1
        return {"extraction_safe": True, "validation_pass": True, "rebuilt_adapter_bytes_identical": True, "rebuilt_adapter_file_count": checked}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    native = args.native.resolve()
    adapter = args.adapter.resolve()
    output = (args.output or adapter / "build").resolve()
    run_checked([sys.executable, "-B", str(PROJECT / "scripts/validate_d30_capability_v1.py"), "--native", str(native), "--output", str(adapter), "--receipt", str(adapter / "validation.json")], PROJECT, "D30-PACKET-PREVALIDATION", 360)
    if validate_bundle(load_bundle(adapter)):
        raise PacketError("D30-PACKET-BUNDLE")
    members = collect_members(adapter)
    first = zip_bytes(members)
    second = zip_bytes(members)
    if first != second:
        raise PacketError("D30-PACKET-TWO-BUILD-DRIFT")
    checks = verify_zip(first, members)
    replay = extracted_replay(first, native, adapter, members)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / ARCHIVE_NAME
    write_bytes(archive, first)
    receipt = {
        "schema": "d30-capability-thin-packet-build-receipt/1", "course_id": COURSE_ID, "result": "PASS",
        "archive": {"path": f"build/{ARCHIVE_NAME}", **file_identity(archive)},
        "adapter_manifest": file_identity(adapter / "manifest.json"), "adapter_validation": file_identity(adapter / "validation.json"),
        "content_policy": "identity_state_rights_evidence_only", "native_payloads_included": False,
        "public_state_changed": False, "local_profile_data_included": False, "two_build_byte_identity": True,
        "zip_checks": checks, "extracted_replay": replay,
    }
    write_json(output / RECEIPT_NAME, receipt)
    print(json.dumps({"result": "PASS", "archive": str(archive), "identity": receipt["archive"], "members": len(members)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.TimeoutExpired, zipfile.BadZipFile) as exc:
        print(f"D30 packet build failed: {exc}", file=sys.stderr)
        sys.exit(1)
