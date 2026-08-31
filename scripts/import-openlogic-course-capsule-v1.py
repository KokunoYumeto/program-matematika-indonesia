"""Admit the exact C80 Open Logic v2.3.1 adapter without copying textbook prose."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
DEST = ROOT / "backend/course-capsule-v1/adapters/openlogic-v231"
ARCHIVE = ROOT / "backend/course-capsule-v1/builds/program-matematika-indonesia-openlogic-c80-v2.3.1.zip"
SOURCE_ARCHIVE_NAME = "C80_OPENLOGIC_V231_ADAPTER_0.1.0.zip"
EXPECTED = {
    "handoff": {"bytes": 6670, "sha256": "44686f3d4d80e83ed9ce931fc1888d607ad9e12d4c81bf985663f47711157361"},
    "inventory": {"bytes": 3634, "sha256": "2dbda9b52ebc81df78c625a3345796c74a33840af065f9271734fb0a798829de"},
    "archive": {"bytes": 2409875, "sha256": "eb4293a9745dd7c6f98f7c94c05d214e4dfc904ef5dda3afea571e0ee1363673"},
    "manifest": {"bytes": 22315, "sha256": "01974670c902a50d3e0166214f665286e0030a270a781a56413976be52ca4b01"},
    "seal": {"bytes": 15470, "sha256": "9ca71a3aa7cec5b3b6fbc02bfe5f6c4b29611b141262876b1389dbd3419dc9ab"},
    "checksums": {"bytes": 6229, "sha256": "c188dfc13b6cc8d50fe97af821d0bcbacb5d828cfc417b5a28dee0f5e9f3fb0d"},
}
TREE_SHA256 = "068abef4fbcb2062443dc7fce1f219cdcf64aabd3e2474076667a65cd6ebf94a"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fact(data: bytes) -> dict[str, object]:
    return {"bytes": len(data), "sha256": digest(data)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def safe_name(name: str) -> str:
    require("\\" not in name and not name.startswith("/"), f"unsafe archive path: {name}")
    path = PurePosixPath(name)
    require(name == path.as_posix() and ".." not in path.parts and "." not in path.parts,
            f"unsafe archive path: {name}")
    require(not name.endswith("/"), f"directory entry is not allowed: {name}")
    return name


def tree_identity(entries: dict[str, bytes]) -> str:
    rows = "".join(
        f"{name}\0{len(data)}\0{digest(data)}\n"
        for name, data in sorted(entries.items())
    )
    return digest(rows.encode("utf-8"))


def verify_declared_rows(document: dict, entries: dict[str, bytes], *, key: str, expected_count: int) -> None:
    rows = document[key]
    require(len(rows) == expected_count, f"{key} count drift")
    seen: set[str] = set()
    for row in rows:
        name = safe_name(row["path"])
        require(row.get("path_base") == "package_root", f"{name}: unsupported path base")
        require(name not in seen, f"{name}: duplicate declaration")
        seen.add(name)
        require(name in entries, f"{name}: declared package file missing")
        require(fact(entries[name]) == {field: row[field] for field in ("bytes", "sha256")},
                f"{name}: declared identity drift")


def verify_checksum_ledger(data: bytes, entries: dict[str, bytes]) -> int:
    rows = data.decode("utf-8").splitlines()
    require(len(rows) == 66, "checksum ledger count drift")
    names: list[str] = []
    for row in rows:
        checksum, separator, name = row.partition("  ")
        require(separator == "  " and len(checksum) == 64, "malformed checksum row")
        name = safe_name(name)
        require(name not in names, f"duplicate checksum path: {name}")
        require(name in entries and digest(entries[name]) == checksum, f"checksum mismatch: {name}")
        names.append(name)
    require(set(names) == set(entries) - {"PACKAGE_CHECKSUMS.sha256"},
            "checksum ledger coverage drift")
    return len(rows)


def read_archive(data: bytes) -> dict[str, bytes]:
    import io

    entries: dict[str, bytes] = {}
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        require(archive.testzip() is None, "adapter archive CRC failed")
        require(len(archive.infolist()) == 67, "adapter member count drift")
        for info in archive.infolist():
            name = safe_name(info.filename)
            require(name not in entries, f"duplicate archive member: {name}")
            require(info.date_time == (1980, 1, 1, 0, 0, 0), f"timestamp drift: {name}")
            require(info.compress_type == zipfile.ZIP_DEFLATED, f"compression drift: {name}")
            mode = info.external_attr >> 16
            require(not stat.S_ISLNK(mode), f"symlink member forbidden: {name}")
            entries[name] = archive.read(info)
    require(sum(map(len, entries.values())) == 20614428, "adapter member byte total drift")
    require(tree_identity(entries) == TREE_SHA256, "adapter tree identity drift")
    return entries


def run_validator(package_root: Path, script: str, owner_root: Path) -> dict[str, object]:
    command = [
        sys.executable,
        "-B",
        str(package_root / "tools" / script),
        "--package", str(package_root),
        "--repository-root", str(WORKSPACE),
        "--owner-package-root", str(owner_root),
        "--require-authorities",
    ]
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(command, check=False, capture_output=True, text=True, env=environment)
    require(result.returncode == 0, f"{script} failed:\n{result.stdout}\n{result.stderr}")
    return {
        "script": script,
        "status": "pass",
        "stdout_sha256": digest(result.stdout.encode("utf-8")),
        "stderr_empty": not result.stderr,
    }


def preserve(path: Path, data: bytes, *, allow_update: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() == data:
            return
        require(allow_update, f"existing admission differs: {path}")
    path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manager-root", type=Path, required=True)
    parser.add_argument("--owner-root", type=Path, default=WORKSPACE / "04_mirrors/id/openlogic")
    args = parser.parse_args()
    source = args.manager_root.resolve(strict=True)
    owner_root = args.owner_root.resolve(strict=True)

    handoff_bytes = (source / "MANAGER_HANDOFF.json").read_bytes()
    inventory_bytes = (source / "HANDOFF_FILE_INVENTORY.json").read_bytes()
    require(fact(handoff_bytes) == EXPECTED["handoff"], "manager handoff identity drift")
    require(fact(inventory_bytes) == EXPECTED["inventory"], "handoff inventory identity drift")
    handoff = json.loads(handoff_bytes)
    inventory = json.loads(inventory_bytes)
    require(handoff["course_id"] == "C80" and handoff["adapter"]["contract"] == "2.3.1",
            "manager handoff scope drift")
    require(len(inventory["files"]) == 11 and inventory["inventory_self_excluded"] is True,
            "handoff selected-inventory boundary drift")
    for row in inventory["files"]:
        path = (WORKSPACE / PurePosixPath(row["path"])).resolve(strict=True)
        require(WORKSPACE == path or WORKSPACE in path.parents, "handoff inventory escapes workspace")
        require(fact(path.read_bytes()) == {field: row[field] for field in ("bytes", "sha256")},
                f"handoff inventory drift: {row['path']}")

    archive_bytes = (source / SOURCE_ARCHIVE_NAME).read_bytes()
    require(fact(archive_bytes) == EXPECTED["archive"], "sealed Open Logic archive drift")
    entries = read_archive(archive_bytes)
    for name, expected in (("manifest.json", EXPECTED["manifest"]),
                           ("seal.json", EXPECTED["seal"]),
                           ("PACKAGE_CHECKSUMS.sha256", EXPECTED["checksums"])):
        require(fact(entries[name]) == expected, f"{name} identity drift")
    manifest = json.loads(entries["manifest.json"])
    seal = json.loads(entries["seal.json"])
    verify_declared_rows(manifest, entries, key="files", expected_count=64)
    verify_declared_rows(seal, entries, key="files", expected_count=65)
    checksum_rows = verify_checksum_ledger(entries["PACKAGE_CHECKSUMS.sha256"], entries)
    require(manifest["build"]["deterministic_replay"] == "byte_identical", "package replay claim drift")
    require(manifest["csv_projection"]["record_count"] == 5807, "canonical record count drift")

    with tempfile.TemporaryDirectory(prefix="openlogic-v231-intake-") as temporary:
        package_root = Path(temporary)
        for name, data in entries.items():
            target = package_root / PurePosixPath(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        validator_results = [
            run_validator(package_root, "validate_lane_adapter_v231.py", owner_root),
            run_validator(package_root, "validate_c80_openlogic_v231.py", owner_root),
        ]

    for name, data in entries.items():
        preserve(DEST / PurePosixPath(name), data)
    preserve(ARCHIVE, archive_bytes, allow_update=True)
    receipt = {
        "schema_id": "interlanguage/openlogic-course-capsule-admission/v1",
        "recorded_at": "2026-08-31",
        "state": "locally_admitted_central_release_pending",
        "course_id": "C80",
        "package_id": handoff["adapter"]["package_id"],
        "dataset_id": handoff["adapter"]["dataset_id"],
        "extension_id": handoff["adapter"]["extension_id"],
        "extension_version": handoff["adapter"]["extension_version"],
        "manager_handoff": fact(handoff_bytes),
        "selected_handoff_inventory": fact(inventory_bytes),
        "selected_handoff_inventory_entries_verified": len(inventory["files"]),
        "selected_handoff_inventory_is_not_physical_directory_inventory": True,
        "archive": {"path": ARCHIVE.relative_to(ROOT).as_posix(), **fact(archive_bytes)},
        "archive_members": 67,
        "archive_member_bytes": 20614428,
        "package_tree_sha256": TREE_SHA256,
        "inputs": {name: fact(data) for name, data in sorted(entries.items())},
        "manifest_bound_files_verified": 64,
        "seal_bound_files_verified": 65,
        "checksum_rows_verified": checksum_rows,
        "authority_validators": validator_results,
        "semantic_counts": handoff["semantic_closure"],
        "owner_authority": handoff["owner_authority"],
        "sealed_order_note": "Exact source ZIP bytes are preserved. Its declared POSIX lexical ordering label is inaccurate; no sealed member was rewritten.",
        "later_independent_audit_bound": True,
        "public_package_excludes_manager_coordination_files": True,
        "textbook_body_centralized": False,
        "limits": [
            "The verified Indonesian PDF is the primary learner surface; machine tables are secondary.",
            "No native HTML, unit anchors, page anchors, assessment engine, or full PDF accessibility is claimed.",
            "Central adapter publication remains pending until GitHub and Zenodo readback of the successor release.",
        ],
    }
    receipt_bytes = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    preserve(DEST / "ADMISSION.json", receipt_bytes, allow_update=True)
    expected_destination = set(entries) | {"ADMISSION.json"}
    actual_destination = {
        path.relative_to(DEST).as_posix()
        for path in DEST.rglob("*")
        if path.is_file()
    }
    require(actual_destination == expected_destination, "admitted Open Logic tree contains unbound files")
    print(json.dumps({
        "state": receipt["state"],
        "archive": receipt["archive"],
        "admission": fact(receipt_bytes),
        "materialized_files": len(actual_destination),
        "validators": validator_results,
    }, indent=2))


if __name__ == "__main__":
    main()
