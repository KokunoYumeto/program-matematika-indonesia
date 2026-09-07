"""Create a deterministic, metadata-only C140 capability packet."""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from c140_capability_model_v1 import (
    COURSE_ID,
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    PROJECT,
    identity,
    read_json,
    sha256_bytes,
    write_bytes,
    write_json,
)
from validate_c140_capability_v1 import validate


ADAPTER_REL = Path("backend/course-capsule-v1/adapters/c140-capability-v1")
DEFAULT_OUTPUT = DEFAULT_ADAPTER / "build"
ARCHIVE_NAME = "C140_COMPLETE_THIN_CAPABILITY_METADATA_V1.zip"
RECEIPT_NAME = "PACKET_BUILD_RECEIPT.json"
SCRIPT_NAMES = (
    "c140_capability_model_v1.py",
    "build_c140_capability_v1.py",
    "validate_c140_capability_v1.py",
    "package_c140_capability_v1.py",
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
    if not value or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts) or (path.parts and ":" in path.parts[0]):
        raise PacketError("C140-PACKET-UNSAFE-PATH:" + value)
    return path


def safe_member(name: str) -> bool:
    try:
        return safe_relative_path(name).as_posix() == name
    except PacketError:
        return False


def _add_member(members: dict[str, bytes], name: str, path: Path) -> None:
    normalized = PurePosixPath(name).as_posix()
    if not safe_member(normalized) or normalized in members:
        raise PacketError("C140-PACKET-MEMBER-PATH:" + normalized)
    if path.suffix.casefold() in FORBIDDEN_SUFFIXES:
        raise PacketError("C140-PACKET-FORBIDDEN-PAYLOAD:" + normalized)
    data = path.read_bytes()
    if LOCAL_PROFILE_PATTERN.search(data):
        raise PacketError("C140-PACKET-LOCAL-PROFILE-DATA:" + normalized)
    members[normalized] = data


def collect_members(adapter: Path) -> dict[str, bytes]:
    required = (
        adapter / "manifest.json",
        adapter / "validation.json",
        adapter / "README.md",
        adapter / "input/source-lock.json",
        adapter / "input/github-release-readback.json",
        adapter / "input/github-pages-readback.json",
        adapter / "input/zenodo-readback.json",
    )
    for path in required:
        if not path.is_file():
            raise PacketError("C140-PACKET-REQUIRED-FILE-MISSING:" + path.name)

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
        raise PacketError(f"C140-PACKET-ADAPTER-FILE-SET:missing={missing}:extra={extra}")

    members: dict[str, bytes] = {}
    for relative in sorted(allowed_adapter, key=lambda item: item.as_posix()):
        _add_member(members, (ADAPTER_REL / Path(relative.as_posix())).as_posix(), adapter / Path(relative.as_posix()))
    for name in SCRIPT_NAMES:
        _add_member(members, (Path("scripts") / name).as_posix(), PROJECT / "scripts" / name)

    members["START_HERE.md"] = (
        "# C140 complete thin capability packet\n\n"
        "This packet contains only the complete C140/C5 metadata projection, stable identity "
        "indexes, component-aware rights, public route evidence, learner and educator views, "
        "negative fixtures, and standard-library Python scripts. It does not contain Penn, "
        "Random, companion, problem, answer, solution, PDF, EPUB, TeX, image, or dataset bodies.\n\n"
        "Deterministic replay needs the separately preserved, hash-pinned native checkout. Run:\n\n"
        "    python -B scripts/build_c140_capability_v1.py --native-root PATH_TO_PINNED_NATIVE\n"
        "    python -B scripts/validate_c140_capability_v1.py --native-root PATH_TO_PINNED_NATIVE\n\n"
        "The boundary is fourteen Penn documents, one Random completeness donor, and thirty-nine "
        "original companion documents. Rights for Penn, both Random witnesses, MathJax, the "
        "companion, and both capstone datasets remain separate.\n"
    ).encode("utf-8")
    inventory = {
        "schema": "c140-capability-thin-packet-inventory/1",
        "course_id": COURSE_ID,
        "content_policy": "adapter_metadata_only_external_native_replay_dependency",
        "adapter_files": len(allowed_adapter),
        "scripts": len(SCRIPT_NAMES),
        "native_inputs_included": 0,
        "native_content_bodies_included": False,
        "exercise_answer_or_solution_bodies_included": False,
        "external_hash_pinned_native_checkout_required_for_replay": True,
        "included_before_inventory": [
            {"path": name, "bytes": len(data), "sha256": sha256_bytes(data)}
            for name, data in sorted(members.items())
        ],
        "excluded_payload_classes": [
            "native content and dataset bodies",
            "Penn, Random, and companion prose, exercises, answers, and solutions",
            "PDF, EPUB, TeX, CSV, images, credentials, caches, logs, and runtime artifacts",
        ],
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
        names = [info.filename for info in infos]
        if names != sorted(members) or len(names) != len(set(names)) or archive.testzip() is not None:
            raise PacketError("C140-PACKET-ZIP-INVENTORY-OR-CRC")
        for info in infos:
            data = archive.read(info.filename)
            if not safe_member(info.filename) or info.date_time != (1980, 1, 1, 0, 0, 0) or info.extra or info.comment:
                raise PacketError("C140-PACKET-ZIP-METADATA:" + info.filename)
            if data != members[info.filename] or info.file_size != len(data):
                raise PacketError("C140-PACKET-ZIP-BYTES:" + info.filename)
            if PurePosixPath(info.filename).suffix.casefold() in FORBIDDEN_SUFFIXES or LOCAL_PROFILE_PATTERN.search(data):
                raise PacketError("C140-PACKET-ZIP-FORBIDDEN-DATA:" + info.filename)
    return {
        "crc_and_full_entry_readback": True,
        "fixed_member_metadata": True,
        "member_count": len(members),
        "payload_bytes": sum(len(data) for data in members.values()),
        "sorted_member_order": True,
    }


def package(native: Path, adapter: Path, output: Path) -> dict[str, Any]:
    validation = validate(native, adapter, write_receipt=True)
    members = collect_members(adapter)
    first = zip_bytes(members)
    second = zip_bytes(members)
    if first != second:
        raise PacketError("C140-PACKET-TWO-BUILD-DRIFT")
    checks = verify_zip(first, members)
    output.mkdir(parents=True, exist_ok=True)
    archive_path = output / ARCHIVE_NAME
    write_bytes(archive_path, first)
    receipt = {
        "schema": "c140-capability-thin-packet-build-receipt/1",
        "course_id": COURSE_ID,
        "result": "PASS",
        "archive": identity(archive_path, display_path=(Path("build") / ARCHIVE_NAME).as_posix()),
        "adapter_manifest": identity(adapter / "manifest.json", display_path="manifest.json"),
        "adapter_validation": identity(adapter / "validation.json", display_path="validation.json"),
        "content_policy": "adapter_metadata_only_external_native_replay_dependency",
        "external_hash_pinned_native_checkout_required_for_replay": True,
        "native_inputs_included": 0,
        "native_content_bodies_included": False,
        "exercise_answer_or_solution_bodies_included": False,
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    receipt = package(args.native_root.resolve(), args.adapter.resolve(), args.output.resolve())
    print(json.dumps({"result": receipt["result"], "archive": receipt["archive"], "members": receipt["zip_checks"]["member_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (PacketError, KeyError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(f"C140 packet build failed: {error}", file=sys.stderr)
        sys.exit(1)
