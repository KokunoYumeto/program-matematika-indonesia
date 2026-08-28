#!/usr/bin/env python3
"""Build deterministic source and backend ZIPs for a central release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


FIXED_ZIP_TIME = (2026, 8, 22, 0, 0, 0)
MIGRATION_RECEIPT_FILENAMES = {
    "applied-combinatorics-id-v1": "applied-combinatorics-id-backend-v1-migration-receipt.json",
    "dmoi4-id-v1": "dmoi4-id-backend-v1-migration-receipt.json",
    "erdman-functional-analysis-id-v1": "erdman-functional-analysis-id-backend-v1-migration-receipt.json",
    "hefferon-linear-algebra-id-v1": "hefferon-linear-algebra-id-backend-v1-migration-receipt.json",
    "judson-id-v1": "judson-id-backend-v1-migration-receipt.json",
    "mathematics-in-lean-id-v1": "mathematics-in-lean-id-backend-v1-migration-receipt.json",
    "o002-b80-id-v1": "o002-b80-id-backend-v1-migration-receipt.json",
    "o005-c120-id-v1": "o005-c120-id-backend-v1-migration-receipt.json",
    "o018-c130-id-v1": "o018-c130-id-backend-v1-migration-receipt.json",
    "openlogic-id-v1": "openlogic-id-backend-v1-migration-receipt.json",
    "prealgebra2e-id-v1": "prealgebra2e-id-backend-v1-migration-receipt.json",
    "tea-time-id-v1": "tea-time-id-backend-v1-migration-receipt.json",
    "yaintt-id-v1": "yaintt-id-backend-v1-migration-receipt.json",
}

V2_RELEASE_FILES = {
    "schemas/v2/backend-migration-receipt-v2.schema.json": "backend-migration-receipt-v2.schema.json",
    "schemas/v2/federation-package-v2.schema.json": "federation-package-v2.schema.json",
    "schemas/v2/federation-record-v2.schema.json": "federation-record-v2.schema.json",
    "schemas/v2/namespace-v2.json": "namespace-v2.json",
    "schemas/v2/pmi-release-policy-v2.json": "pmi-release-policy-v2.json",
    "scripts/build-backend-v2-federation.py": "build-backend-v2-federation.py",
    "scripts/build-backend-v2-validation-receipt.py": "build-backend-v2-validation-receipt.py",
    "scripts/validate-backend-v2-federation.py": "validate-backend-v2-federation.py",
}

IMMUTABLE_V1_ARCHIVE_RELATIVE = Path(
    "releases/v0.56.0/program-matematika-indonesia-backend-v1-v0.56.0.zip"
)
IMMUTABLE_V1_ARCHIVE_SHA256 = "a6451613d0e1960f614314da2c5361ddfb749cd09bf147539ccc5d172abd6866"
IMMUTABLE_V1_PREFIX = "program-matematika-indonesia-backend-v1/"
IMMUTABLE_V1_MEMBER_PINS = {
    "manifest.json": "8fe45cfb07e47e9596a4d3088beadcd8287ec2f089a62db990bd4fd70f079997",
    "records.jsonl": "e563e13336701e2d3b2110debe4074b168f53f8fd3757e36fe25d36043db7783",
    "validation_report.json": "b742dbcc65c9511fa3d208a001d1f4a33ca38d04d0178f3e964d043c09534b42",
}

ASSESSMENT_SHARD_RELATIVE = Path(
    "backend/v2.2/owner-native-shards/o001-a00-assessments-v0.1.0"
)
ASSESSMENT_SHARD_IDENTITY = {
    "files": 12,
    "bytes": 19057785,
    "aggregate_sha256": "5d7c3da1a1b3c33b4f79306fec08a31ebc8f557188f1ec0c088e267e0d9ce222",
    "manifest_sha256": "5ed7b558ae1f621bef52b59be64df90dbf52c967c7e12e2fc9fc296309e2b19e",
    "checksums_sha256": "7d313ed06023a90a28882c25e8942bf9feda270b1c75cbaced38674a1ae9cd57",
    "seal_sha256": "a97c1cad9cfbd72fe7bbc44cf59050dc1adbf238d07afdd6337fd0d3c8f74b49",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def zip_bytes(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build_zip(output: Path, entries: list[tuple[str, bytes]]) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w") as archive:
        for name, data in sorted(entries):
            zip_bytes(archive, name, data)
    expected = {name: data for name, data in entries}
    with zipfile.ZipFile(output) as archive:
        archive.testzip()
        names = archive.namelist()
        if names != sorted(expected):
            raise ValueError(f"ZIP inventory/order mismatch: {output}")
        for name, data in expected.items():
            if archive.read(name) != data:
                raise ValueError(f"ZIP byte mismatch: {output}:{name}")
    return {
        "path": output.as_posix(),
        "entries": len(entries),
        "uncompressed_bytes": sum(len(data) for _, data in entries),
        "bytes": output.stat().st_size,
        "sha256": sha256_file(output),
        "verification": "pass",
    }


def package_entries(package: Path, prefix: str) -> list[tuple[str, bytes]]:
    if not package.is_dir():
        raise ValueError(f"backend package is not a directory: {package}")
    entries = []
    for path in (candidate for candidate in package.rglob("*") if candidate.is_file()):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(package).as_posix()
        entries.append((f"{prefix}{relative}", path.read_bytes()))
    if not entries:
        raise ValueError(f"backend package is empty: {package}")
    return sorted(entries, key=lambda item: (item[0].casefold(), item[0]))


def validate_assessment_shard(root: Path) -> tuple[Path, list[tuple[str, bytes]], dict]:
    shard = root / ASSESSMENT_SHARD_RELATIVE
    entries = package_entries(shard, "o001-a00-assessments-v0.1.0/")
    facts = []
    for name, data in entries:
        relative = name.split("/", 1)[1]
        facts.append((relative, len(data), hashlib.sha256(data).hexdigest()))
    aggregate = hashlib.sha256(
        "".join(f"{digest}  {size}  {path}\n" for path, size, digest in facts).encode("utf-8")
    ).hexdigest()
    if len(entries) != ASSESSMENT_SHARD_IDENTITY["files"]:
        raise ValueError("O001/A00 assessment shard file count mismatch")
    if sum(len(data) for _, data in entries) != ASSESSMENT_SHARD_IDENTITY["bytes"]:
        raise ValueError("O001/A00 assessment shard byte count mismatch")
    if aggregate != ASSESSMENT_SHARD_IDENTITY["aggregate_sha256"]:
        raise ValueError("O001/A00 assessment shard aggregate mismatch")
    for relative, expected in {
        "manifest.json": ASSESSMENT_SHARD_IDENTITY["manifest_sha256"],
        "CHECKSUMS.sha256": ASSESSMENT_SHARD_IDENTITY["checksums_sha256"],
        "seal.json": ASSESSMENT_SHARD_IDENTITY["seal_sha256"],
    }.items():
        actual = next(
            (digest for path, _, digest in facts if path == relative),
            None,
        )
        if actual != expected:
            raise ValueError(f"O001/A00 assessment shard identity mismatch: {relative}")
    return shard, entries, {
        "files": len(entries),
        "uncompressed_bytes": sum(len(data) for _, data in entries),
        "aggregate_sha256": aggregate,
    }


def validate_v22_package_shape(
    package: Path,
    canonical_package: Path,
    validation_receipt: Path,
    source_commit: str,
) -> dict:
    """Fail closed on the release-critical v2.2 layers without pinning one pilot's counts."""
    entries = package_entries(package, "program-matematika-indonesia-backend-v2.2/")
    relative_names = [name.split("/", 1)[1] for name, _ in entries]
    lowered = [name.lower() for name in relative_names]
    required_layers = {
        "schema": any("schema/" in name and name.endswith(".schema.json") for name in lowered),
        "state_vocabulary": any("state-vocabulary" in name and name.endswith(".json") for name in lowered),
        "profile": any("profile" in name and name.endswith(".json") for name in lowered),
        "adapter": any("adapter" in name for name in lowered),
        "builder": any("build" in name for name in lowered),
        "validator": any("validat" in name for name in lowered),
        "sealed_pilot": any("pilot" in name for name in lowered),
        "manifest": any("manifest" in name and name.endswith(".json") for name in lowered),
    }
    missing = sorted(layer for layer, present in required_layers.items() if not present)
    if missing:
        raise ValueError(f"backend-v2.2 package is missing required layers: {missing}")
    receipt = json.loads(validation_receipt.read_text(encoding="utf-8"))
    if receipt.get("result") != "pass" or receipt.get("credentials_recorded") is not False:
        raise ValueError("backend-v2.2 validation receipt is not a credential-free pass")
    if receipt.get("source_commit") != source_commit:
        raise ValueError("backend-v2.2 validation receipt source commit mismatch")
    declared = receipt.get("canonical_package") or receipt.get("package") or {}
    canonical_files = [path for path in canonical_package.rglob("*") if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"]
    if "file_count" in declared and declared["file_count"] != len(canonical_files):
        raise ValueError("backend-v2.2 validation receipt file_count mismatch")
    if "total_bytes" in declared and declared["total_bytes"] != sum(path.stat().st_size for path in canonical_files):
        raise ValueError("backend-v2.2 validation receipt total_bytes mismatch")
    return {
        "entries": entries,
        "layers": required_layers,
        "validation_receipt": {
            "bytes": validation_receipt.stat().st_size,
            "sha256": sha256_file(validation_receipt),
        },
    }


def validate_central_evidence(
    admission: Path,
    owner_readback: Path,
    reservation: Path | None,
    version: str,
    project_root: Path,
) -> dict:
    admission_doc = json.loads(admission.read_text(encoding="utf-8"))
    readback_doc = json.loads(owner_readback.read_text(encoding="utf-8"))
    if admission_doc.get("schema_id") != "program-matematika-indonesia/central-release-admission-manifest/v1":
        raise ValueError("central admission manifest schema mismatch")
    if admission_doc.get("target_release") != version:
        raise ValueError("central admission manifest release mismatch")
    workspace_root = project_root.parents[2]
    for fact in admission_doc.get("inputs", []):
        relative = Path(fact.get("path", ""))
        source = (
            admission.parent / relative
            if len(relative.parts) == 1
            else workspace_root / relative
        )
        if (
            not source.is_file()
            or fact.get("bytes") != source.stat().st_size
            or fact.get("sha256") != sha256_file(source)
        ):
            raise ValueError(f"central admission input binding mismatch: {fact.get('path')}")
    admissions = admission_doc.get("admissions", [])
    supplements = admission_doc.get("supplements", [])
    summary = admission_doc.get("summary", {})
    if version == "0.60.0":
        infrastructure = admission_doc.get("infrastructure_admissions", [])
        valid_primary = all(
            isinstance(row.get("record"), int)
            and row.get("doi") == f"10.5281/zenodo.{row['record']}"
            and str(row.get("learner_route", "")).startswith("https://")
            and isinstance(row.get("primary_artifact", {}).get("bytes"), int)
            and row["primary_artifact"]["bytes"] > 0
            and re.fullmatch(r"[0-9a-f]{64}", row["primary_artifact"].get("sha256", ""))
            for row in admissions
        )
        valid_infrastructure = all(
            row.get("zero_prose") is True
            and isinstance(row.get("files"), int)
            and row["files"] > 0
            and isinstance(row.get("bytes"), int)
            and row["bytes"] > 0
            and re.fullmatch(r"[0-9a-f]{64}", row.get("aggregate_sha256", ""))
            for row in infrastructure
        )
        if (
            len({row.get("course_id") for row in admissions}) != len(admissions)
            or summary.get("refreshed_course_routes") != len(admissions)
            or summary.get("new_html_readers")
            != sum(isinstance(row.get("central_html_reader"), dict) for row in admissions)
            or summary.get("new_owner_native_backend_shards") != len(infrastructure)
            or summary.get("completed_public_course_roles_before")
            != summary.get("completed_public_course_roles_after")
            or summary.get("honest_global_backend_state")
            != "phase_release_not_global_migration_complete"
            or not valid_primary
            or not valid_infrastructure
        ):
            raise ValueError("v0.60 central admission summary is not derivable from its rows")
    elif (
        len({row.get("course_id") for row in admissions}) != len(admissions)
        or summary.get("admitted_primary_course_routes") != len(admissions)
        or summary.get("admitted_partial_courses")
        != sum(row.get("state_after") != "published" for row in admissions)
        or summary.get("admitted_newly_complete_courses")
        != sum(row.get("state_after") == "published" for row in admissions)
        or summary.get("admitted_separate_supplements") != len(supplements)
        or summary.get("admitted_primary_selected_route_bytes")
        != sum(row.get("bytes", -1) for row in admissions)
        or summary.get("supplement_selected_route_bytes")
        != sum(row.get("bytes", -1) for row in supplements)
    ):
        raise ValueError("central admission summary is not derivable from its rows")
    if readback_doc.get("schema_id") != "program-matematika-indonesia/owner-reader-public-readback/v1" or readback_doc.get("result") != "pass":
        raise ValueError("owner-reader readback is not an admitted pass")
    binding = readback_doc.get("source_admission_manifest", {})
    if binding.get("bytes") != admission.stat().st_size or binding.get("sha256") != sha256_file(admission):
        raise ValueError("owner-reader readback does not bind the supplied admission manifest")
    routes = readback_doc.get("routes", [])
    if readback_doc.get("route_count") != len(routes) or readback_doc.get("total_bytes") != sum(row.get("bytes", -1) for row in routes):
        raise ValueError("owner-reader readback aggregate counts mismatch")
    for row in routes:
        if (
            row.get("http_status") != 200
            or row.get("content_type") != "text/html"
            or not isinstance(row.get("bytes"), int)
            or row["bytes"] <= 0
            or not isinstance(row.get("sha256"), str)
            or len(row["sha256"]) != 64
            or not str(row.get("url", "")).startswith("https://")
            or ".json" in str(row.get("url", "")).lower()
        ):
            raise ValueError(f"invalid owner-reader evidence row: {row.get('course_id')}")
    allowed_route_courses = {row.get("course_id") for row in admissions}
    if version in {"0.60.0", "0.61.0"}:
        live_authority = json.loads(
            (project_root / "backend" / "authority" / "curriculum-authority-v1.json").read_text(
                encoding="utf-8"
            )
        )
        allowed_route_courses = {
            row.get("id") for row in live_authority.get("catalog", {}).get("courses", [])
        }
    if not {row.get("course_id") for row in routes}.issubset(allowed_route_courses):
        raise ValueError("owner-reader evidence references a course outside the admitted curriculum")
    result = {
        "admission": {"bytes": admission.stat().st_size, "sha256": sha256_file(admission)},
        "owner_readback": {"bytes": owner_readback.stat().st_size, "sha256": sha256_file(owner_readback)},
        "owner_html_routes": len(routes),
    }
    if reservation is not None:
        reservation_doc = json.loads(reservation.read_text(encoding="utf-8"))
        authority = json.loads(
            (project_root / "backend" / "authority" / "curriculum-authority-v1.json").read_text(
                encoding="utf-8"
            )
        )
        reserved_record_id = reservation_doc.get("reserved_version", {}).get("draft_record_id")
        authority_program = authority.get("catalog", {}).get("program", {})
        if (
            reservation_doc.get("schema_id") != "program-matematika-indonesia/zenodo-version-reservation/v1"
            or reservation_doc.get("program_version") != version
            or reservation_doc.get("result") != "pass"
            or reservation_doc.get("authorization_route", {}).get("credential_material_recorded") is not False
            or reservation_doc.get("reserved_version", {}).get("visibility_intent") != "public_open"
            or authority_program.get("version") != version
            or authority_program.get("zenodo")
            != f"https://doi.org/10.5281/zenodo.{reserved_record_id}"
        ):
            raise ValueError("Zenodo reservation receipt is not a credential-free public-open reservation")
        result["reservation"] = {"bytes": reservation.stat().st_size, "sha256": sha256_file(reservation)}
    return result


def files_under(root: Path, relative: str) -> list[Path]:
    path = root / relative
    if path.is_file():
        return [path]
    return sorted(candidate for candidate in path.rglob("*") if candidate.is_file())


def committed_blob_bytes(root: Path, commit: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return result.stdout


def assert_live_matches_commit(
    root: Path,
    commit: str,
    paths: set[Path],
    tracked_paths: set[str],
) -> dict:
    facts = []
    for path in sorted(paths):
        if not path.is_file() or not path.is_relative_to(root):
            raise ValueError(f"release-critical input is not a project file: {path}")
        relative = path.relative_to(root).as_posix()
        if relative not in tracked_paths:
            raise ValueError(f"release-critical input is not bound to source commit: {relative}")
        live = path.read_bytes()
        committed = committed_blob_bytes(root, commit, relative)
        if live != committed:
            raise ValueError(f"release-critical live bytes differ from source commit: {relative}")
        facts.append((relative, len(live), hashlib.sha256(live).hexdigest()))
    aggregate = hashlib.sha256(
        "".join(f"{digest}  {size}  {path}\n" for path, size, digest in facts).encode("utf-8")
    ).hexdigest()
    return {
        "file_count": len(facts),
        "total_bytes": sum(size for _, size, _ in facts),
        "aggregate_sha256": aggregate,
    }


def load_immutable_v1_archive(root: Path) -> tuple[Path, dict[str, bytes]]:
    archive_path = root / IMMUTABLE_V1_ARCHIVE_RELATIVE
    if not archive_path.is_file() or sha256_file(archive_path) != IMMUTABLE_V1_ARCHIVE_SHA256:
        raise ValueError("published immutable backend-v1 archive identity mismatch")
    with zipfile.ZipFile(archive_path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"published immutable backend-v1 archive CRC failure: {bad}")
        names = archive.namelist()
        if len(names) != len(set(names)) or any(
            not name.startswith(IMMUTABLE_V1_PREFIX) or name.endswith("/") for name in names
        ):
            raise ValueError("published immutable backend-v1 archive inventory is unsafe")
        members = {
            name.removeprefix(IMMUTABLE_V1_PREFIX): archive.read(name)
            for name in names
        }
    if len(members) != 84:
        raise ValueError("published immutable backend-v1 archive must contain exactly 84 files")
    for relative, expected_sha256 in IMMUTABLE_V1_MEMBER_PINS.items():
        data = members.get(relative)
        if data is None or hashlib.sha256(data).hexdigest() != expected_sha256:
            raise ValueError(f"published immutable backend-v1 member mismatch: {relative}")
    manifest = json.loads(members["manifest.json"].decode("utf-8"))
    if manifest.get("record_count") != 2122:
        raise ValueError("published immutable backend-v1 record count is not 2,122")
    declared = {entry["path"]: entry for entry in manifest.get("files", [])}
    if set(members) != set(declared) | {"manifest.json", "validation_report.json"}:
        raise ValueError("published immutable backend-v1 manifest inventory mismatch")
    for relative, entry in declared.items():
        data = members[relative]
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError(f"published immutable backend-v1 manifest member mismatch: {relative}")
    return archive_path, members


def run_checked(command: list[str], root: Path) -> None:
    subprocess.run(command, cwd=root, check=True)


def deterministic_snapshot(root: Path) -> dict:
    explicit_roots = [
        "backend/v2.1/pilots/a00-prealgebra",
        "backend/v2.1/pilots/b10-dmoi",
        "backend/v2.1/pilots/c100-geometry",
        "backend/v2.1/pilots/d20-functional-analysis",
        "backend/v2.1/planning/educational-access",
        "backend/research/educational-access-v0.1.0",
        "docs/id-ID/courses/C100",
        "docs/id-ID/courses/D20",
    ]
    explicit_files = [
        "docs/data/unit-route-C100-v2.1.json",
        "docs/data/unit-route-D20-v2.1.json",
        "docs/data/unit-route-v2.1.json",
        "docs/data/unit-routes-v2.1.json",
        "docs/data/educational-access.json",
        "schemas/educational-access-federation-v1.schema.json",
    ]
    paths: list[Path] = []
    for relative in explicit_roots:
        paths.extend(files_under(root, relative))
    paths.extend(root / relative for relative in explicit_files)
    facts = []
    for path in sorted(set(paths)):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if not path.is_file():
            raise ValueError(f"deterministic v2.1 output missing: {path}")
        facts.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    encoded = json.dumps(facts, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"files": facts, "aggregate_sha256": hashlib.sha256(encoded).hexdigest()}


def run_v21_release_gates(root: Path) -> dict:
    commands = [
        [sys.executable, "-B", "backend/v2.1/pilots/build_all_pilots.py"],
        [sys.executable, "-B", "backend/v2.1/pilots/validate_pilots.py"],
        [sys.executable, "-B", "scripts/build-educational-access-planning-v21.py"],
        [sys.executable, "-B", "scripts/validate-educational-access-planning-v21.py"],
        [sys.executable, "-B", "scripts/validate-educational-access-federation-v1.py"],
        ["node", "scripts/build-v21-learner-routes.mjs"],
        ["node", "scripts/validate-v21-learner-routes.mjs"],
    ]
    snapshots = []
    for _ in range(2):
        for command in commands:
            run_checked(command, root)
        snapshots.append(deterministic_snapshot(root))
    if snapshots[0] != snapshots[1]:
        raise ValueError("v2.1 pilot/route build is not byte-deterministic across two complete replays")
    return snapshots[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--backend-package", required=True, type=Path)
    parser.add_argument("--backend-v2-package", required=True, type=Path)
    parser.add_argument("--backend-v2-validation-receipt", required=True, type=Path)
    parser.add_argument("--backend-v22-package", required=True, type=Path)
    parser.add_argument("--backend-v22-validation-receipt", required=True, type=Path)
    parser.add_argument("--admission-manifest", required=True, type=Path)
    parser.add_argument("--owner-reader-readback", required=True, type=Path)
    parser.add_argument("--reservation-receipt", type=Path)
    parser.add_argument("--release-dir", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    release = args.release_dir.resolve()
    backend = args.backend_package.resolve()
    backend_v2 = args.backend_v2_package.resolve()
    backend_v2_validation_receipt = args.backend_v2_validation_receipt.resolve()
    backend_v22 = args.backend_v22_package.resolve()
    backend_v22_validation_receipt = args.backend_v22_validation_receipt.resolve()
    canonical_backend_v22 = (
        backend_v22
        if backend_v22.parent.name == "packages"
        else backend_v22_validation_receipt.parent
    )
    backend_v22_release_root = (
        backend_v22.parent.parent
        if backend_v22.parent.name == "packages" and backend_v22.parent.parent.name == "v2.2"
        else backend_v22
    )
    admission_manifest = args.admission_manifest.resolve()
    owner_reader_readback = args.owner_reader_readback.resolve()
    reservation_receipt = args.reservation_receipt.resolve() if args.reservation_receipt else None
    version = args.version

    v22_shape = validate_v22_package_shape(
        backend_v22_release_root,
        canonical_backend_v22,
        backend_v22_validation_receipt,
        args.source_commit,
    )
    central_evidence = validate_central_evidence(
        admission_manifest,
        owner_reader_readback,
        reservation_receipt,
        version,
        root,
    )
    assessment_shard, assessment_entries, assessment_identity = validate_assessment_shard(root)

    immutable_v1_archive, immutable_v1_members = load_immutable_v1_archive(root)

    v21_gate = run_v21_release_gates(root)
    release.mkdir(parents=True, exist_ok=True)
    v21_gate_receipt = release / f"GLOBAL_BACKEND_V21_DETERMINISTIC_REPLAY_RECEIPT_v{version}.json"
    v21_gate_receipt.write_text(
        json.dumps(
            {
                "aggregate_sha256": v21_gate["aggregate_sha256"],
                "files": v21_gate["files"],
                "recorded_at": "2026-08-26T00:00:00Z",
                "replay_count": 2,
                "result": "pass",
                "schema_id": "program-matematika-indonesia/backend-v2.1-deterministic-replay-receipt/v1",
                "source_commit": args.source_commit,
                "version": version,
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    copies = {
        root / "schemas" / "catalog-v1.schema.json": release / "program-matematika-indonesia-catalog-v1.schema.json",
        root / "schemas" / "backend-v1.schema.json": release / "interlanguage-math-backend-v1.schema.json",
        root / "schemas" / "profiles" / "source-format-profile-v1.schema.json": release / "interlanguage-source-format-profile-v1.schema.json",
        root / "schemas" / "backend-migration-receipt-v1.schema.json": release / "interlanguage-backend-migration-receipt-v1.schema.json",
        root / "backend" / "BACKEND_CONVERGENCE_V1.md": release / "BACKEND_CONVERGENCE_V1.md",
        root / "backend" / "MIGRATION_HANDOFF_V1.md": release / "MIGRATION_HANDOFF_V1.md",
        root / "backend" / "authority" / "curriculum-authority-v1.json": release / "curriculum-authority-v1.json",
        root / "docs" / "data" / "learner-read-model.json": release / "learner-read-model-v1.json",
        root / "schemas" / "v1" / "curriculum-authority-v1.schema.json": release / "curriculum-authority-v1.schema.json",
        root / "schemas" / "v1" / "learner-read-model-v1.schema.json": release / "learner-read-model-v1.schema.json",
        root / "backend" / "v2.2" / "global-capability-contract-v0.1.0.json": release / "global-capability-contract-v0.1.0.json",
        root / "backend" / "v2.2" / "schema" / "global-capability-contract-v0.1.schema.json": release / "global-capability-contract-v0.1.schema.json",
        backend_v2_validation_receipt: release / f"GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v{version}.json",
        backend_v22_validation_receipt: release / f"GLOBAL_BACKEND_V22_VALIDATION_RECEIPT_v{version}.json",
        admission_manifest: release / admission_manifest.name,
        owner_reader_readback: release / owner_reader_readback.name,
    }
    if reservation_receipt is not None:
        copies[reservation_receipt] = release / reservation_receipt.name
    for source_name, release_name in V2_RELEASE_FILES.items():
        copies[root / source_name] = release / release_name
    copies[root / "backend" / "v2.1" / "schema" / "federation-unit-package-v2.1.schema.json"] = (
        release / "federation-unit-package-v2.1.schema.json"
    )
    copies[root / "backend" / "v2.1" / "schema" / "federation-unit-record-v2.1.schema.json"] = (
        release / "federation-unit-record-v2.1.schema.json"
    )
    migration_receipts = sorted((root / "backend" / "migrations").glob("*/MIGRATION_RECEIPT.json"))
    receipt_directories = {source.parent.name for source in migration_receipts}
    if receipt_directories != set(MIGRATION_RECEIPT_FILENAMES):
        raise ValueError("complete-corpus migration receipt directory identity set mismatch")
    for source in migration_receipts:
        copies[source] = release / MIGRATION_RECEIPT_FILENAMES[source.parent.name]
    for source, target in copies.items():
        shutil.copyfile(source, target)

    (release / f"program-matematika-indonesia-backend-v1-validation-v{version}.json").write_bytes(
        immutable_v1_members["validation_report.json"]
    )

    backend_zip = release / f"program-matematika-indonesia-backend-v1-v{version}.zip"
    shutil.copyfile(immutable_v1_archive, backend_zip)
    if sha256_file(backend_zip) != IMMUTABLE_V1_ARCHIVE_SHA256:
        raise ValueError("copied immutable backend-v1 archive identity mismatch")
    backend_result = {
        "path": backend_zip.as_posix(),
        "entries": len(immutable_v1_members),
        "uncompressed_bytes": sum(len(data) for data in immutable_v1_members.values()),
        "bytes": backend_zip.stat().st_size,
        "sha256": sha256_file(backend_zip),
        "verification": "pass-published-immutable-reuse",
    }

    backend_v2_entries = package_entries(
        backend_v2,
        "program-matematika-indonesia-backend-v2/",
    )
    backend_v2_zip = release / f"program-matematika-indonesia-backend-v2-v{version}.zip"
    backend_v2_result = build_zip(backend_v2_zip, backend_v2_entries)

    backend_v21 = root / "backend" / "v2.1"
    backend_v21_entries = package_entries(
        backend_v21,
        "program-matematika-indonesia-backend-v2.1/",
    )
    backend_v21_zip = release / f"program-matematika-indonesia-backend-v2.1-pilots-v{version}.zip"
    backend_v21_result = build_zip(backend_v21_zip, backend_v21_entries)

    backend_v22_zip = release / f"program-matematika-indonesia-backend-v2.2-v{version}.zip"
    backend_v22_first = build_zip(backend_v22_zip, v22_shape["entries"])
    backend_v22_result = build_zip(backend_v22_zip, v22_shape["entries"])
    for key in ("entries", "uncompressed_bytes", "bytes", "sha256", "verification"):
        if backend_v22_first[key] != backend_v22_result[key]:
            raise ValueError(f"backend-v2.2 ZIP is not byte-deterministic: {key}")
    v22_archive_receipt = release / f"GLOBAL_BACKEND_V22_ARCHIVE_RECEIPT_v{version}.json"
    v22_archive_receipt.write_text(
        json.dumps(
            {
                "schema_id": "program-matematika-indonesia/backend-v2.2-archive-receipt/v1",
                "version": version,
                "source_commit": args.source_commit,
                "recorded_at": "2026-08-27T00:00:00Z",
                "result": "pass",
                "replay_count": 2,
                "credentials_recorded": False,
                "required_layers": v22_shape["layers"],
                "validation_receipt": v22_shape["validation_receipt"],
                "archive": {
                    key: value
                    for key, value in backend_v22_result.items()
                    if key != "path"
                },
                "members": [
                    {
                        "path": name,
                        "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                    }
                    for name, data in sorted(v22_shape["entries"])
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    assessment_zip = release / "o001-a00-assessments-v0.1.0.zip"
    assessment_first = build_zip(assessment_zip, assessment_entries)
    assessment_result = build_zip(assessment_zip, assessment_entries)
    for key in ("entries", "uncompressed_bytes", "bytes", "sha256", "verification"):
        if assessment_first[key] != assessment_result[key]:
            raise ValueError(f"O001/A00 assessment ZIP is not byte-deterministic: {key}")
    if assessment_result["entries"] != assessment_identity["files"]:
        raise ValueError("O001/A00 assessment ZIP file count mismatch")
    if assessment_result["uncompressed_bytes"] != assessment_identity["uncompressed_bytes"]:
        raise ValueError("O001/A00 assessment ZIP uncompressed byte mismatch")

    source_roots = [
        ".openai/hosting.json",
        ".gitattributes",
        ".gitignore",
        "LICENSE",
        "README.md",
        "eslint.config.mjs",
        "next.config.ts",
        "package.json",
        "pnpm-lock.yaml",
        "pnpm-workspace.yaml",
        "tsconfig.json",
        "vite.config.ts",
        "app",
        # public/hub is a reproducible prebuild mirror of docs/ and is ignored by
        # Git. Include only the tracked public input; npm run prebuild recreates
        # the mirror byte-for-byte from the committed docs source.
        "public/favicon.svg",
        "public/og.png",
        "docs",
        "schemas/catalog-v1.schema.json",
        "schemas/educational-access-federation-v1.schema.json",
        "schemas/backend-v1.schema.json",
        "schemas/backend-migration-receipt-v1.schema.json",
        "schemas/profiles/source-format-profile-v1.schema.json",
        "schemas/v2/backend-migration-receipt-v2.schema.json",
        "schemas/v2/federation-package-v2.schema.json",
        "schemas/v2/federation-record-v2.schema.json",
        "schemas/v2/namespace-v2.json",
        "schemas/v2/pmi-release-policy-v2.json",
        "schemas/v1/curriculum-authority-v1.schema.json",
        "schemas/v1/learner-read-model-v1.schema.json",
        "scripts/check-public-links.mjs",
        "scripts/export-release-catalog.mjs",
        "scripts/seed-curriculum-authority.mjs",
        "scripts/advance-curriculum-authority.mjs",
        "scripts/admit-o004-v055.mjs",
        "scripts/build-learner-read-model.mjs",
        "scripts/validate-learner-read-model.mjs",
        "scripts/sync-public-schemas.mjs",
        "scripts/export-single-file-site.mjs",
        "scripts/build-learner-start-pdf.py",
        "scripts/sync-sites-public.mjs",
        "scripts/build-d20-learner-routes.mjs",
        "scripts/build-c100-learner-routes.mjs",
        "scripts/build-v21-learner-routes.mjs",
        "scripts/validate-v21-learner-routes.mjs",
        "scripts/advance-curriculum-authority-v056.mjs",
        "scripts/advance-curriculum-authority-v057.mjs",
        "scripts/advance-curriculum-authority-v058.mjs",
        "scripts/advance-curriculum-authority-v059.mjs",
        "scripts/advance-curriculum-authority-v060.mjs",
        "scripts/build-v060-admission-evidence.mjs",
        "scripts/advance-curriculum-authority-v061.mjs",
        "scripts/build-v061-admission-evidence.mjs",
        "scripts/reserve-v061-zenodo.py",
        "scripts/write-directory-public-readback.mjs",
        "scripts/write-current-central-route-readback.mjs",
        "scripts/build-v22-v060-validation-receipt.py",
        "scripts/build-v21-pilot-package.py",
        "scripts/build-educational-access-planning-v21.py",
        "scripts/validate-educational-access-planning-v21.py",
        "scripts/build-educational-access-federation-v1.py",
        "scripts/validate-educational-access-federation-v1.py",
        "scripts/validate-static-site.mjs",
        "scripts/verify-http-bytes.mjs",
        "scripts/build-backend-v1-schema.py",
        "scripts/export-curriculum-backend-v1.py",
        "scripts/validate-backend-v1.py",
        "scripts/validate-migration-receipt-v1.py",
        "scripts/build-release-bundle.py",
        "scripts/validate-release-bundle.py",
        "scripts/write-release-checksums.py",
        "scripts/build-backend-v2-federation.py",
        "scripts/build-backend-v2-validation-receipt.py",
        "scripts/validate-backend-v2-federation.py",
        "tests/backend-v2/test_build_backend_v2_federation.py",
        "tests/backend-v2/test_validate_backend_v2_federation.py",
        "backend/BACKEND_CONVERGENCE_V1.md",
        "backend/MIGRATION_HANDOFF_V1.md",
        "backend/v1/namespace.json",
        "backend/authority",
        "backend/v2.1",
        "backend/v2.2",
        "backend/research/educational-access-v0.1.0",
        "tests/backend-v2.2",
        "tests/backend-v22",
    ]
    source_paths: list[Path] = []
    for relative in source_roots:
        source_paths.extend(files_under(root, relative))
    source_paths.extend(sorted((root / "scripts").glob("migrate-*-backend-v1.py")))
    source_paths.extend(sorted((root / "scripts").glob("test-*-backend-v1.py")))
    source_paths.extend(
        path
        for path in files_under(root, "backend/migrations")
        if "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    source_paths.extend(
        [
            release / f"program-matematika-indonesia-catalog-v{version}.json",
            release / f"RELEASE_NOTES_v{version}.md",
            release / admission_manifest.name,
            release / owner_reader_readback.name,
        ]
    )
    if reservation_receipt is not None:
        source_paths.append(release / reservation_receipt.name)
    tracked_paths = set(
        subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", args.source_commit],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    )
    required_v22_sources = {
        path.relative_to(root).as_posix()
        for path in files_under(root, "backend/v2.2")
        if "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    required_v22_sources.add("scripts/advance-curriculum-authority-v059.mjs")
    required_v22_sources.add("scripts/advance-curriculum-authority-v060.mjs")
    required_v22_sources.add("scripts/advance-curriculum-authority-v061.mjs")
    required_v22_sources.add("scripts/build-v061-admission-evidence.mjs")
    required_v22_sources.add("scripts/build-v22-v060-validation-receipt.py")
    missing_v22_sources = sorted(required_v22_sources - tracked_paths)
    if missing_v22_sources:
        raise ValueError(
            f"backend-v2.2/transition source is not bound to source commit: {missing_v22_sources}"
        )
    generated_prefixes = ("docs/", "backend/authority/", "backend/v2/")
    critical_live_paths = {
        path
        for path in source_paths
        if path.is_relative_to(root)
        and not path.is_relative_to(release)
        and not path.relative_to(root).as_posix().startswith(generated_prefixes)
    }
    for package_root in (backend_v21, backend_v22_release_root, assessment_shard):
        critical_live_paths.update(
            path
            for path in package_root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        )
    critical_live_paths.update(
        source
        for source in copies
        if source.is_relative_to(root)
        and not source.is_relative_to(release)
        and source.is_file()
        and not source.relative_to(root).as_posix().startswith(generated_prefixes)
    )
    source_commit_binding = assert_live_matches_commit(
        root,
        args.source_commit,
        critical_live_paths,
        tracked_paths,
    )
    generated_catalog = release / f"program-matematika-indonesia-catalog-v{version}.json"
    generated_release_inputs = {
        generated_catalog,
        release / admission_manifest.name,
        release / owner_reader_readback.name,
    }
    if reservation_receipt is not None:
        generated_release_inputs.add(release / reservation_receipt.name)
    source_paths = [
        path
        for path in source_paths
        if path in generated_release_inputs
        or path.relative_to(root).as_posix() in tracked_paths
    ]
    if len(source_paths) != len(set(source_paths)):
        raise ValueError("duplicate source ZIP path")

    entries: list[tuple[str, bytes]] = []
    manifest_files = []
    for path in sorted(source_paths):
        if not path.is_relative_to(root):
            raise ValueError(f"source ZIP input escapes project root: {path}")
        source_path = path.relative_to(root).as_posix()
        name = source_path
        if path.parent == release:
            name = path.name
        data = path.read_bytes() if path in generated_release_inputs else committed_blob_bytes(root, args.source_commit, source_path)
        entries.append((name, data))
        manifest_files.append(
            {
                "path": name,
                "source_path": source_path,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    source_manifest = {
        "schema_id": "program-matematika-indonesia/source-manifest/v2",
        "version": version,
        "source_commit": args.source_commit,
        "files": manifest_files,
    }
    entries.append(("SOURCE_MANIFEST.json", (json.dumps(source_manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")))
    source_zip = release / f"program-matematika-indonesia-source-v{version}.zip"
    source_result = build_zip(source_zip, entries)

    print(
        json.dumps(
            {
                "backend_v1_zip": backend_result,
                "backend_v2_zip": backend_v2_result,
                "backend_v21_zip": backend_v21_result,
                "backend_v21_deterministic_gate": v21_gate,
                "backend_v22_zip": backend_v22_result,
                "backend_v22_archive_receipt": {
                    "path": v22_archive_receipt.as_posix(),
                    "bytes": v22_archive_receipt.stat().st_size,
                    "sha256": sha256_file(v22_archive_receipt),
                },
                "assessment_inventory_zip": assessment_result,
                "central_evidence": central_evidence,
                "source_commit_binding": source_commit_binding,
                "source_zip": source_result,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
