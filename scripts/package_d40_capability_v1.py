"""Package and replay the D40 thin-metadata adapter offline.

The packet intentionally excludes whole-course/public payload bytes, source
prose, TeX, notebooks, native course code bodies, and runtime artifacts. The
four D40 adapter scripts are included. Public PDF/ZIP identities remain bound
through the locked publication/readback metadata.
"""

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

from d40_capability_model_v1 import file_identity, read_json, sha256_bytes, write_bytes, write_json


SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parent.parent
ADAPTER_REL = Path("backend/course-capsule-v1/adapters/d40-capability-v1")
ADAPTER = PROJECT / ADAPTER_REL
DEFAULT_NATIVE = PROJECT.parent / "partial-differential-equations-id"
DEFAULT_OUTPUT = ADAPTER / "build"
ARCHIVE_NAME = "D40_THIN_CAPABILITY_METADATA_V1.zip"
RECEIPT_NAME = "PACKET_BUILD_RECEIPT.json"
PUBLIC_BYTE_ROLES = {"public_pdf", "public_zip"}
SCRIPT_NAMES = (
    "d40_capability_model_v1.py",
    "build_d40_capability_v1.py",
    "validate_d40_capability_v1.py",
    "package_d40_capability_v1.py",
)
FORBIDDEN_SUFFIXES = {".pdf", ".tex", ".ipynb", ".zip"}
ABSOLUTE_PATH_PATTERN = re.compile(rb"(?i)(?<![A-Za-z0-9])[A-Za-z]:[\\/]")
SANITIZED_NATIVE_MEMBER = "native/composite/qa/mastery/D40_MASTERY_VALIDATION.json"
SANITIZED_NATIVE_RELATIVE_PATH = "composite/mastery/id-ID"


class PacketError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "\\" not in name


def collect_members(
    native: Path,
) -> tuple[dict[str, bytes], list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    if not (ADAPTER / "validation.json").is_file():
        raise PacketError("D40-PACKET-VALIDATION-MISSING")
    members: dict[str, bytes] = {}

    def add(name: str, path: Path) -> None:
        normalized = PurePosixPath(name).as_posix()
        if not safe_member(normalized) or normalized in members:
            raise PacketError("D40-PACKET-MEMBER-PATH:" + normalized)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise PacketError("D40-PACKET-FORBIDDEN-PAYLOAD:" + normalized)
        members[normalized] = path.read_bytes()

    manifest = read_json(ADAPTER / "manifest.json")
    declared_outputs = {
        PurePosixPath(str(item["path"]))
        for item in manifest.get("outputs", [])
    }
    allowed_adapter = {
        *declared_outputs,
        PurePosixPath("manifest.json"),
        PurePosixPath("validation.json"),
        PurePosixPath("README.md"),
        PurePosixPath("input/source-lock.json"),
        *(
            PurePosixPath(path.relative_to(ADAPTER).as_posix())
            for path in sorted(
                (ADAPTER / "fixtures/negative").glob("*.json"),
                key=lambda item: item.name,
            )
        ),
    }
    actual_adapter = {
        PurePosixPath(path.relative_to(ADAPTER).as_posix())
        for path in ADAPTER.rglob("*")
        if path.is_file()
        and not (
            path.relative_to(ADAPTER).parts
            and path.relative_to(ADAPTER).parts[0] in {"build", "publication"}
        )
    }
    if actual_adapter != allowed_adapter:
        missing = sorted(path.as_posix() for path in allowed_adapter - actual_adapter)
        extra = sorted(path.as_posix() for path in actual_adapter - allowed_adapter)
        raise PacketError(f"D40-PACKET-ADAPTER-FILE-SET:missing={missing}:extra={extra}")
    for relative in sorted(allowed_adapter, key=lambda item: item.as_posix()):
        add((ADAPTER_REL / relative).as_posix(), ADAPTER / relative)
    for name in SCRIPT_NAMES:
        add((Path("scripts") / name).as_posix(), PROJECT / "scripts" / name)

    lock = read_json(ADAPTER / "input/source-lock.json")
    excluded: list[dict[str, Any]] = []
    for item in lock["inputs"]:
        if item["role"] in PUBLIC_BYTE_ROLES:
            excluded.append({key: item[key] for key in ("role", "path", "bytes", "sha256")})
            continue
        source = native / item["path"]
        add((Path("native") / item["path"]).as_posix(), source)

    # The native QA receipt contains a historical absolute workstation path.
    # It is evidence-only and never used for routing, so the portable packet
    # replaces that one field with its already-recorded relative scope.  The
    # original immutable identity remains recorded in PACKET_INVENTORY.json.
    original_native = members[SANITIZED_NATIVE_MEMBER]
    sanitized_json = json.loads(original_native)
    if sanitized_json.get("scope") != SANITIZED_NATIVE_RELATIVE_PATH:
        raise PacketError("D40-PACKET-SANITIZATION-SCOPE-DRIFT")
    if not ABSOLUTE_PATH_PATTERN.search(str(sanitized_json.get("scope_absolute", "")).encode("utf-8")):
        raise PacketError("D40-PACKET-SANITIZATION-SOURCE-NOT-ABSOLUTE")
    sanitized_json["scope_absolute"] = SANITIZED_NATIVE_RELATIVE_PATH
    sanitized_native = canonical_json(sanitized_json)
    members[SANITIZED_NATIVE_MEMBER] = sanitized_native

    lock_member = (ADAPTER_REL / "input/source-lock.json").as_posix()
    packaged_lock = json.loads(members[lock_member])
    packaged_row = next(
        item
        for item in packaged_lock["inputs"]
        if item["path"] == "composite/qa/mastery/D40_MASTERY_VALIDATION.json"
    )
    if packaged_row["bytes"] != len(original_native) or packaged_row["sha256"] != sha256_bytes(original_native):
        raise PacketError("D40-PACKET-SANITIZATION-LOCK-DRIFT")
    packaged_row["bytes"] = len(sanitized_native)
    packaged_row["sha256"] = sha256_bytes(sanitized_native)
    members[lock_member] = canonical_json(packaged_lock)

    manifest_member = (ADAPTER_REL / "manifest.json").as_posix()
    packaged_manifest = json.loads(members[manifest_member])
    packaged_manifest["inputs"] = packaged_lock["inputs"]
    members[manifest_member] = canonical_json(packaged_manifest)
    sanitization_rows = [
        {
            "member": SANITIZED_NATIVE_MEMBER,
            "json_field": "scope_absolute",
            "original_bytes": len(original_native),
            "original_sha256": sha256_bytes(original_native),
            "packaged_bytes": len(sanitized_native),
            "packaged_sha256": sha256_bytes(sanitized_native),
            "replacement": SANITIZED_NATIVE_RELATIVE_PATH,
            "routing_use": False,
            "reason": "remove historical local workstation path from public portable packet",
        }
    ]

    # Rebuild the adapter projection against the package-local sanitized lock.
    # This keeps evidence.json and manifest.json truthful and makes the later
    # extracted replay byte-identical rather than merely relaxing that gate.
    with tempfile.TemporaryDirectory(prefix="d40-packet-sanitize-") as temporary:
        root = Path(temporary)
        for name, data in members.items():
            write_bytes(root / PurePosixPath(name), data)
        staged_adapter = root / ADAPTER_REL
        staged_native = root / "native"
        run_checked(
            [
                sys.executable,
                "-B",
                str(root / "scripts/build_d40_capability_v1.py"),
                "--native-root",
                str(staged_native),
                "--output-root",
                str(staged_adapter),
                "--source-lock",
                str(staged_adapter / "input/source-lock.json"),
                "--allow-identity-only-public-artifacts",
            ],
            root,
            "D40-PACKET-SANITIZED-BUILD",
        )
        run_checked(
            [
                sys.executable,
                "-B",
                str(root / "scripts/validate_d40_capability_v1.py"),
                "--native-root",
                str(staged_native),
                "--output-root",
                str(staged_adapter),
                "--source-lock",
                str(staged_adapter / "input/source-lock.json"),
                "--receipt",
                str(staged_adapter / "validation.json"),
                "--allow-identity-only-public-artifacts",
            ],
            root,
            "D40-PACKET-SANITIZED-VALIDATION",
        )
        for relative in sorted(allowed_adapter, key=lambda item: item.as_posix()):
            members[(ADAPTER_REL / relative).as_posix()] = (staged_adapter / relative).read_bytes()

    start_here = """# D40 thin capability validation packet

This packet contains only the D40 adapter, its four standard-library scripts,
and hash-locked metadata/evidence inputs. It excludes the public PDF and ZIP,
the book/reader payload, source prose, TeX, notebooks, native course code
bodies, and runtime artifacts. The four included Python files are only the D40
adapter model, builder, validator, and thin packager.

From this extracted directory run:

    python -B scripts/build_d40_capability_v1.py --native-root native --allow-identity-only-public-artifacts
    python -B scripts/validate_d40_capability_v1.py --native-root native --allow-identity-only-public-artifacts

The identity-only flag applies only to the absent public PDF/ZIP. Their exact
byte identities are cross-checked against the included publication and
anonymous-readback receipts. It is not a full native roundtrip.
""".encode("utf-8")
    members["START_HERE.md"] = start_here
    absolute_path_members = sorted(
        name for name, data in members.items() if ABSOLUTE_PATH_PATTERN.search(data)
    )
    if absolute_path_members:
        raise PacketError(
            "D40-PACKET-ABSOLUTE-PATH-MEMBERS:" + repr(absolute_path_members)
        )
    inventory_rows = [
        {"path": name, "bytes": len(data), "sha256": sha256_bytes(data)}
        for name, data in sorted(members.items())
    ]
    inventory = {
        "schema": "d40-capability-thin-packet-inventory/1",
        "course_id": "D40",
        "content_policy": "metadata_and_evidence_only",
        "full_native_roundtrip_claimed": False,
        "included_before_inventory": inventory_rows,
        "excluded_public_byte_roles": excluded,
        "verbatim_native_path_metadata": [],
        "sanitized_native_path_metadata": sanitization_rows,
        "exclusions": [
            "public PDF bytes",
            "public release ZIP bytes and offline book HTML",
            "source/book prose and TeX",
            "notebooks and native course code bodies",
            "runtime, cache, log, and scientific artifact payloads",
        ],
    }
    members["PACKET_INVENTORY.json"] = canonical_json(inventory)
    return members, excluded, absolute_path_members, sanitization_rows


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


def verify_zip(data: bytes, members: dict[str, bytes]) -> dict[str, Any]:
    with zipfile.ZipFile(io.BytesIO(data), "r") as archive:
        names = archive.namelist()
        if names != sorted(members) or len(names) != len(set(names)):
            raise PacketError("D40-PACKET-ZIP-ORDER")
        if archive.testzip() is not None:
            raise PacketError("D40-PACKET-ZIP-CRC")
        for info in archive.infolist():
            if info.date_time != (1980, 1, 1, 0, 0, 0) or info.extra or info.comment:
                raise PacketError("D40-PACKET-ZIP-METADATA:" + info.filename)
            payload = archive.read(info.filename)
            if payload != members[info.filename] or info.file_size != len(payload):
                raise PacketError("D40-PACKET-ZIP-BYTES:" + info.filename)
    return {
        "sorted_member_order": True,
        "fixed_member_metadata": True,
        "crc_and_full_entry_readback": True,
        "member_count": len(members),
        "payload_bytes": sum(len(data) for data in members.values()),
    }


def run_checked(command: list[str], cwd: Path, code: str) -> dict[str, Any]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=240)
    if result.returncode:
        raise PacketError(code + ":" + result.stderr.strip())
    # Do not persist command output: it may contain host-specific absolute
    # paths even when the command itself succeeded.
    return {"exit_code": result.returncode}


def extracted_replay(data: bytes, original_members: dict[str, bytes]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="d40-thin-packet-") as temp:
        root = Path(temp)
        with zipfile.ZipFile(io.BytesIO(data), "r") as archive:
            for info in archive.infolist():
                if not safe_member(info.filename):
                    raise PacketError("D40-PACKET-EXTRACT-PATH")
                destination = root / PurePosixPath(info.filename)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(info.filename))
        adapter = root / ADAPTER_REL
        native = root / "native"
        build_command = [
            sys.executable,
            "-B",
            str(root / "scripts/build_d40_capability_v1.py"),
            "--native-root",
            str(native),
            "--output-root",
            str(adapter),
            "--source-lock",
            str(adapter / "input/source-lock.json"),
            "--allow-identity-only-public-artifacts",
        ]
        build_result = run_checked(build_command, root, "D40-PACKET-EXTRACTED-BUILD")
        validate_command = [
            sys.executable,
            "-B",
            str(root / "scripts/validate_d40_capability_v1.py"),
            "--native-root",
            str(native),
            "--output-root",
            str(adapter),
            "--source-lock",
            str(adapter / "input/source-lock.json"),
            "--receipt",
            str(adapter / "validation.json"),
            "--allow-identity-only-public-artifacts",
        ]
        validate_result = run_checked(validate_command, root, "D40-PACKET-EXTRACTED-VALIDATE")
        check_names = [
            name
            for name in original_members
            if name.startswith(ADAPTER_REL.as_posix() + "/")
            and (
                "/data/" in name
                or "/views/" in name
                or name.endswith("/manifest.json")
            )
        ]
        for name in check_names:
            if (root / PurePosixPath(name)).read_bytes() != original_members[name]:
                raise PacketError("D40-PACKET-EXTRACTED-DRIFT:" + name)
        extracted_validation_path = adapter / "validation.json"
        extracted_validation = read_json(extracted_validation_path)
        if (
            extracted_validation.get("state") != "pass"
            or extracted_validation.get("public_artifact_validation_mode")
            != "identity_only_allowed"
        ):
            raise PacketError("D40-PACKET-EXTRACTED-VALIDATION-RECEIPT")
        return {
            "extraction_safe": True,
            "rebuild_pass": True,
            "validation_pass": True,
            "rebuilt_projection_byte_identical": True,
            "rebuilt_projection_file_count": len(check_names),
            "build_exit_code": build_result["exit_code"],
            "validation_exit_code": validate_result["exit_code"],
            "validation_receipt": file_identity(extracted_validation_path),
            "validation_mode": extracted_validation["public_artifact_validation_mode"],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--allow-identity-only-public-artifacts",
        action="store_true",
        help="Allow the two excluded public PDF/ZIP inputs to remain identity-only when rebuilding from a frozen thin packet.",
    )
    args = parser.parse_args()
    native = args.native_root.resolve()
    output = args.output_root.resolve()

    prevalidation_command = [
            sys.executable,
            "-B",
            str(PROJECT / "scripts/validate_d40_capability_v1.py"),
            "--native-root",
            str(native),
            "--output-root",
            str(ADAPTER),
            "--source-lock",
            str(ADAPTER / "input/source-lock.json"),
            "--receipt",
            str(ADAPTER / "validation.json"),
        ]
    if args.allow_identity_only_public_artifacts:
        prevalidation_command.append("--allow-identity-only-public-artifacts")
    prevalidation = run_checked(
        prevalidation_command,
        PROJECT,
        "D40-PACKET-PREVALIDATION",
    )
    members, excluded, absolute_path_members, sanitization_rows = collect_members(native)
    first = zip_bytes(members)
    second = zip_bytes(members)
    if first != second:
        raise PacketError("D40-PACKET-TWO-BUILD-DRIFT")
    zip_checks = verify_zip(first, members)
    replay = extracted_replay(first, members)
    output.mkdir(parents=True, exist_ok=True)
    archive_path = output / ARCHIVE_NAME
    write_bytes(archive_path, first)
    receipt = {
        "schema": "d40-capability-thin-packet-build-receipt/1",
        "state": "pass",
        "course_id": "D40",
        "archive": {"path": (Path("build") / ARCHIVE_NAME).as_posix(), **file_identity(archive_path)},
        "adapter_manifest": file_identity(ADAPTER / "manifest.json"),
        "adapter_validation": file_identity(ADAPTER / "validation.json"),
        "content_policy": "metadata_and_evidence_only",
        "full_native_roundtrip_claimed": False,
        "two_build_byte_identity": True,
        "zip_checks": zip_checks,
        "extracted_replay": replay,
        "prevalidation": prevalidation,
        "excluded_public_byte_roles": excluded,
        "verbatim_native_absolute_path_members": absolute_path_members,
        "sanitized_native_path_metadata": sanitization_rows,
        "locked_inputs_included": len(read_json(ADAPTER / "input/source-lock.json")["inputs"])
        - len(excluded),
        "forbidden_payloads_included": False,
        "public_state_changed": False,
    }
    write_json(output / RECEIPT_NAME, receipt)
    print(json.dumps({"state": "pass", "archive": str(archive_path), "sha256": receipt["archive"]["sha256"], "members": zip_checks["member_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (PacketError, KeyError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired, zipfile.BadZipFile) as exc:
        print(f"D40 packet build failed: {exc}", file=sys.stderr)
        sys.exit(1)
