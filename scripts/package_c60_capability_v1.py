"""Create a deterministic metadata-only C60 capability packet."""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from build_c60_capability_v1 import DEFAULT_ADAPTER, DEFAULT_NATIVE, PROJECT
from c60_capability_model_v1 import (
    BACKEND_TREE,
    COURSE_ID,
    CURRENT_PUBLIC_HEAD,
    CURRENT_PUBLIC_TREE,
    NATIVE_RELEASE_COMMIT,
    identity,
    read_json,
    sha256_bytes,
    write_json,
)
from validate_c60_capability_v1 import validate


ADAPTER_REL = Path("backend/course-capsule-v1/adapters/c60-capability-v1")
DEFAULT_OUTPUT = DEFAULT_ADAPTER / "build"
ARCHIVE_NAME = "C60_THIN_CAPABILITY_METADATA_V1.zip"
RECEIPT_NAME = "PACKET_BUILD_RECEIPT.json"
SCRIPT_NAMES = (
    "c60_capability_model_v1.py",
    "build_c60_capability_v1.py",
    "validate_c60_capability_v1.py",
    "package_c60_capability_v1.py",
)
FORBIDDEN_SUFFIXES = {".pdf", ".tex", ".ltx", ".sty", ".cls", ".bib", ".bbl", ".epub", ".csv", ".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg"}
LOCAL_PROFILE_PATTERN = re.compile(rb"(?i)(?:[A-Za-z]:[\\/]+Users[\\/]+[^\\/\r\n\t\"']+|/(?:home|Users)/[^/\r\n\t\"']+)")


class PacketError(ValueError):
    pass


def safe_relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value.replace("\\", "/"))
    if not value or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts) or (path.parts and ":" in path.parts[0]):
        raise PacketError("C60-PACKET-UNSAFE-PATH:" + value)
    return path


def _add(members: dict[str, bytes], name: str, path: Path) -> None:
    normalized = safe_relative_path(name).as_posix()
    if normalized != name or normalized in members:
        raise PacketError("C60-PACKET-MEMBER-PATH:" + normalized)
    if path.suffix.casefold() in FORBIDDEN_SUFFIXES:
        raise PacketError("C60-PACKET-FORBIDDEN-PAYLOAD:" + normalized)
    data = path.read_bytes()
    if LOCAL_PROFILE_PATTERN.search(data):
        raise PacketError("C60-PACKET-LOCAL-PROFILE-DATA:" + normalized)
    members[normalized] = data


def collect_members(adapter: Path) -> dict[str, bytes]:
    manifest = read_json(adapter / "manifest.json")
    declared = {safe_relative_path(str(row["path"])) for row in manifest.get("outputs", [])}
    allowed = declared | {PurePosixPath("manifest.json"), PurePosixPath("validation.json")}
    actual = {PurePosixPath(path.relative_to(adapter).as_posix()) for path in adapter.rglob("*") if path.is_file() and path.relative_to(adapter).parts[0] != "build"}
    if actual != allowed:
        raise PacketError(f"C60-PACKET-ADAPTER-FILE-SET:missing={sorted(str(x) for x in allowed-actual)}:extra={sorted(str(x) for x in actual-allowed)}")
    members: dict[str, bytes] = {}
    for relative in sorted(allowed, key=lambda item: item.as_posix()):
        _add(members, (ADAPTER_REL / Path(relative.as_posix())).as_posix(), adapter / Path(relative.as_posix()))
    for name in SCRIPT_NAMES:
        _add(members, f"scripts/{name}", PROJECT / "scripts" / name)
    members["START_HERE.md"] = (
        "# C60 thin capability packet\n\n"
        "This packet contains only C60 adapter metadata, two Indonesian adapter views, validation evidence, negative fixtures, and four Python scripts. It contains no native textbook body, PDF, TeX, image, release archive, credential, cache, or learner data.\n\n"
        f"Rebuild requires the separate public source checkout at commit `{CURRENT_PUBLIC_HEAD}` (tree `{CURRENT_PUBLIC_TREE}`), whose native backend tree `{BACKEND_TREE}` is unchanged from release commit `{NATIVE_RELEASE_COMMIT}`. Run:\n\n"
        "    python -B scripts/build_c60_capability_v1.py --native-root PATH_TO_PINNED_PUBLIC_CLONE\n"
        "    python -B scripts/validate_c60_capability_v1.py --native-root PATH_TO_PINNED_PUBLIC_CLONE\n"
        "    python -B scripts/package_c60_capability_v1.py --native-root PATH_TO_PINNED_PUBLIC_CLONE\n\n"
        "The common map carries 101 native exercise identities with hint/check/solution explicitly marked `not_present` and `source_has_none`; it supplies no assessment or execution service.\n"
    ).encode("utf-8")
    inventory = {
        "schema": "c60-capability-thin-packet-inventory/1",
        "course_id": COURSE_ID,
        "content_policy": "adapter_metadata_and_views_only_external_native_replay_dependency",
        "native_release": {"public_head": CURRENT_PUBLIC_HEAD, "public_tree": CURRENT_PUBLIC_TREE, "release_commit": NATIVE_RELEASE_COMMIT, "backend_tree": BACKEND_TREE},
        "adapter_files": len(allowed),
        "scripts": len(SCRIPT_NAMES),
        "native_inputs_included": 0,
        "native_content_bodies_included": False,
        "learner_data_included": False,
        "self_contained_reversible_exchange_claimed": False,
        "external_pinned_native_checkout_required_for_replay": True,
        "included_before_inventory": [{"path": name, "bytes": len(data), "sha256": sha256_bytes(data)} for name, data in sorted(members.items())],
        "excluded_payload_classes": ["native JSON/JSONL/CSV/XLSX datasets", "textbook and exercise bodies", "TeX, PDF, EPUB, and native reader payloads", "images, credentials, caches, logs, and runtime artifacts"],
    }
    members["PACKET_INVENTORY.json"] = (json.dumps(inventory, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
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
        if [info.filename for info in infos] != sorted(members) or archive.testzip() is not None:
            raise PacketError("C60-PACKET-ZIP-INVENTORY-OR-CRC")
        for info in infos:
            data = archive.read(info.filename)
            if info.date_time != (1980, 1, 1, 0, 0, 0) or info.extra or info.comment or data != members[info.filename]:
                raise PacketError("C60-PACKET-ZIP-BYTES-OR-METADATA:" + info.filename)
            if PurePosixPath(info.filename).suffix.casefold() in FORBIDDEN_SUFFIXES or LOCAL_PROFILE_PATTERN.search(data):
                raise PacketError("C60-PACKET-ZIP-FORBIDDEN:" + info.filename)
    return {"crc_and_full_entry_readback": True, "fixed_member_metadata": True, "member_count": len(members), "payload_bytes": sum(len(data) for data in members.values()), "sorted_member_order": True}


def package(native_root: Path, hub_root: Path, adapter: Path, output: Path) -> dict[str, Any]:
    validation = validate(native_root, hub_root, adapter)
    members = collect_members(adapter)
    first = zip_bytes(members)
    second = zip_bytes(members)
    if first != second:
        raise PacketError("C60-PACKET-TWO-BUILD-DRIFT")
    checks = verify_zip(first, members)
    output.mkdir(parents=True, exist_ok=True)
    archive_path = output / ARCHIVE_NAME
    archive_path.write_bytes(first)
    receipt = {
        "schema": "c60-capability-thin-packet-build-receipt/1",
        "course_id": COURSE_ID,
        "result": "PASS",
        "archive": identity(archive_path, display_path=f"build/{ARCHIVE_NAME}"),
        "adapter_manifest": identity(adapter / "manifest.json", display_path="manifest.json"),
        "adapter_validation": identity(adapter / "validation.json", display_path="validation.json"),
        "content_policy": "adapter_metadata_and_views_only_external_native_replay_dependency",
        "external_pinned_native_checkout_required_for_replay": True,
        "native_inputs_included": 0,
        "native_content_bodies_included": False,
        "forbidden_payloads_included": False,
        "local_profile_data_included": False,
        "public_state_changed": False,
        "negative_fixtures_included": len(validation["negative_fixtures"]),
        "two_build_byte_identity": True,
        "zip_checks": checks,
    }
    write_json(output / RECEIPT_NAME, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--hub-root", type=Path, default=PROJECT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    receipt = package(args.native_root.resolve(), args.hub_root.resolve(), args.adapter.resolve(), args.output.resolve())
    print(json.dumps({"result": receipt["result"], "archive": receipt["archive"], "members": receipt["zip_checks"]["member_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (PacketError, KeyError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(f"C60 packet build failed: {error}", file=sys.stderr)
        sys.exit(1)
