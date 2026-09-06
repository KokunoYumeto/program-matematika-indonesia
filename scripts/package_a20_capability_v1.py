"""Create the deterministic metadata-only A20 capability packet."""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from a20_capability_model_v1 import (
    COURSE_ID,
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    PROJECT,
    PUBLIC_RECEIPT_PATH,
    RELEASE_COMMIT,
    RELEASE_TREE,
    identity,
    read_json,
    sha256_bytes,
    write_bytes,
    write_json,
)
from validate_a20_capability_v1 import validate


ADAPTER_REL = Path("backend/course-capsule-v1/adapters/a20-capability-v1")
DEFAULT_OUTPUT = DEFAULT_ADAPTER / "build"
ARCHIVE_NAME = "A20_THIN_CAPABILITY_METADATA_V1.zip"
RECEIPT_NAME = "PACKET_BUILD_RECEIPT.json"
SCRIPT_NAMES = (
    "a20_capability_model_v1.py",
    "build_a20_capability_v1.py",
    "validate_a20_capability_v1.py",
    "package_a20_capability_v1.py",
    "verify_a20_native_public_v1.py",
)
FORBIDDEN_SUFFIXES = {
    ".pdf", ".tex", ".ltx", ".sty", ".cls", ".bib", ".bbl", ".epub",
    ".csv", ".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg",
}
LOCAL_PROFILE_PATTERN = re.compile(
    rb"(?i)(?:[A-Za-z]:[\\/]+Users[\\/]+[^\\/\r\n\t\"']+|/(?:home|Users)/[^/\r\n\t\"']+)"
)


class PacketError(ValueError):
    pass


def safe_relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value.replace("\\", "/"))
    if (
        not value
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
        or (path.parts and ":" in path.parts[0])
    ):
        raise PacketError("A20-PACKET-UNSAFE-PATH:" + value)
    return path


def safe_member(name: str) -> bool:
    try:
        return safe_relative_path(name).as_posix() == name
    except PacketError:
        return False


def _add_member(members: dict[str, bytes], name: str, path: Path) -> None:
    normalized = PurePosixPath(name).as_posix()
    if not safe_member(normalized) or normalized in members:
        raise PacketError("A20-PACKET-MEMBER-PATH:" + normalized)
    if path.suffix.casefold() in FORBIDDEN_SUFFIXES:
        raise PacketError("A20-PACKET-FORBIDDEN-PAYLOAD:" + normalized)
    data = path.read_bytes()
    if LOCAL_PROFILE_PATTERN.search(data):
        raise PacketError("A20-PACKET-LOCAL-PROFILE-DATA:" + normalized)
    members[normalized] = data


def collect_members(adapter: Path) -> dict[str, bytes]:
    required = (
        adapter / "manifest.json",
        adapter / "validation.json",
        adapter / "README.md",
        adapter / "input/source-lock.json",
        adapter / "input/public-native-readback.json",
    )
    for path in required:
        if not path.is_file():
            raise PacketError("A20-PACKET-REQUIRED-FILE-MISSING:" + path.name)

    manifest = read_json(adapter / "manifest.json")
    declared = {safe_relative_path(str(row["path"])) for row in manifest.get("outputs", [])}
    allowed_adapter = declared | {PurePosixPath("manifest.json"), PurePosixPath("validation.json")}
    actual_adapter = {
        PurePosixPath(path.relative_to(adapter).as_posix())
        for path in adapter.rglob("*")
        if path.is_file() and path.relative_to(adapter).parts[0] not in {"build", "publication"}
    }
    if actual_adapter != allowed_adapter:
        missing = sorted(path.as_posix() for path in allowed_adapter - actual_adapter)
        extra = sorted(path.as_posix() for path in actual_adapter - allowed_adapter)
        raise PacketError(f"A20-PACKET-ADAPTER-FILE-SET:missing={missing}:extra={extra}")

    members: dict[str, bytes] = {}
    for relative in sorted(allowed_adapter, key=lambda item: item.as_posix()):
        _add_member(
            members,
            (ADAPTER_REL / Path(relative.as_posix())).as_posix(),
            adapter / Path(relative.as_posix()),
        )
    for name in SCRIPT_NAMES:
        _add_member(members, (Path("scripts") / name).as_posix(), PROJECT / "scripts" / name)

    members["START_HERE.md"] = (
        "# A20 thin capability packet\n\n"
        "This packet contains only A20 adapter metadata, stable-identity indexes, generated "
        "learner and educator views, validation evidence, negative fixtures, and standard-library "
        "Python scripts. It does not contain the native backend dataset, textbook bodies, TeX "
        "source, PDFs, EPUBs, images, credentials, caches, or logs.\n\n"
        "Deterministic replay requires the separately preserved A20 interoperability export "
        f"identified by SHA-256 `{read_json(adapter / 'input/source-lock.json')['native_export']['jsonl_sha256']}` "
        "and the exact public-release evidence in `input/public-native-readback.json`. Then run:\n\n"
        "    python -B scripts/build_a20_capability_v1.py --native-root PATH_TO_PINNED_NATIVE\n"
        "    python -B scripts/validate_a20_capability_v1.py --native-root PATH_TO_PINNED_NATIVE\n\n"
        "The adapter preserves the exact solved/unsolved identity boundary and does not claim "
        "semantic Indonesian HTML, MathML, PDF/UA, WCAG conformance, complete solutions, or "
        "reversible exchange.\n"
    ).encode("utf-8")
    inventory = {
        "schema": "a20-capability-thin-packet-inventory/1",
        "course_id": COURSE_ID,
        "content_policy": "adapter_metadata_only_external_native_replay_dependency",
        "native_release": {"commit": RELEASE_COMMIT, "tree": RELEASE_TREE},
        "adapter_files": len(allowed_adapter),
        "scripts": len(SCRIPT_NAMES),
        "native_inputs_included": 0,
        "native_content_bodies_included": False,
        "exercise_or_solution_bodies_included": False,
        "reversible_exchange_claimed": False,
        "external_hash_pinned_native_export_required_for_replay": True,
        "included_before_inventory": [
            {"path": name, "bytes": len(data), "sha256": sha256_bytes(data)}
            for name, data in sorted(members.items())
        ],
        "excluded_payload_classes": [
            "native JSONL and CSV datasets",
            "textbook, segment, exercise, problem, and solution bodies",
            "TeX, PDF, EPUB, images, credentials, caches, logs, and runtime artifacts",
        ],
    }
    members["PACKET_INVENTORY.json"] = (
        json.dumps(inventory, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
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
            raise PacketError("A20-PACKET-ZIP-INVENTORY")
        if archive.testzip() is not None:
            raise PacketError("A20-PACKET-ZIP-CRC")
        for info in infos:
            if not safe_member(info.filename):
                raise PacketError("A20-PACKET-ZIP-PATH:" + info.filename)
            if info.date_time != (1980, 1, 1, 0, 0, 0) or info.extra or info.comment:
                raise PacketError("A20-PACKET-ZIP-METADATA:" + info.filename)
            data = archive.read(info.filename)
            if data != members[info.filename] or info.file_size != len(data):
                raise PacketError("A20-PACKET-ZIP-BYTES:" + info.filename)
            if PurePosixPath(info.filename).suffix.casefold() in FORBIDDEN_SUFFIXES:
                raise PacketError("A20-PACKET-ZIP-FORBIDDEN-PAYLOAD:" + info.filename)
            if LOCAL_PROFILE_PATTERN.search(data):
                raise PacketError("A20-PACKET-ZIP-LOCAL-PROFILE:" + info.filename)
    return {
        "crc_and_full_entry_readback": True,
        "fixed_member_metadata": True,
        "member_count": len(members),
        "payload_bytes": sum(len(data) for data in members.values()),
        "sorted_member_order": True,
    }


def package(native: Path, adapter: Path, output: Path, receipt_path: Path = PUBLIC_RECEIPT_PATH) -> dict[str, Any]:
    validation = validate(native, adapter, receipt_path=receipt_path, write_receipt=True)
    members = collect_members(adapter)
    first = zip_bytes(members)
    second = zip_bytes(members)
    if first != second:
        raise PacketError("A20-PACKET-TWO-BUILD-DRIFT")
    zip_checks = verify_zip(first, members)

    output.mkdir(parents=True, exist_ok=True)
    archive_path = output / ARCHIVE_NAME
    write_bytes(archive_path, first)
    receipt = {
        "schema": "a20-capability-thin-packet-build-receipt/1",
        "course_id": COURSE_ID,
        "result": "PASS",
        "archive": identity(archive_path, display_path=(Path("build") / ARCHIVE_NAME).as_posix()),
        "adapter_manifest": identity(adapter / "manifest.json", display_path="manifest.json"),
        "adapter_validation": identity(adapter / "validation.json", display_path="validation.json"),
        "content_policy": "adapter_metadata_only_external_native_replay_dependency",
        "external_hash_pinned_native_export_required_for_replay": True,
        "native_inputs_included": 0,
        "native_content_bodies_included": False,
        "exercise_or_solution_bodies_included": False,
        "forbidden_payloads_included": False,
        "local_profile_data_included": False,
        "public_state_changed": False,
        "reversible_exchange_claimed": False,
        "negative_fixtures_included": len(validation["negative_fixtures"]),
        "two_build_byte_identity": True,
        "zip_checks": zip_checks,
    }
    write_json(output / RECEIPT_NAME, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path, default=PUBLIC_RECEIPT_PATH)
    args = parser.parse_args()
    receipt = package(
        args.native_root.resolve(), args.adapter.resolve(), args.output.resolve(), args.receipt.resolve()
    )
    print(json.dumps({"result": receipt["result"], "archive": receipt["archive"], "members": receipt["zip_checks"]["member_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (PacketError, KeyError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(f"A20 packet build failed: {error}", file=sys.stderr)
        sys.exit(1)
