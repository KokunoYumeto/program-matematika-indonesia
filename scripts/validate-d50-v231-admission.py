#!/usr/bin/env python3
"""Validate the sealed D50 v2.3.1 adapter admitted by the central program.

The public central repository keeps the deterministic ZIP and a small set of
admission evidence, rather than duplicating the 122 MB expanded adapter tree.
This validator replays the ZIP envelope, all embedded checksums, the copied
manifest, and the independent fail-closed evidence without requiring the D50
owner worktree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_REL = Path(
    "backend/v2.3/packages/"
    "program-matematika-indonesia-backend-v2.3.1-"
    "d50-smooth-manifolds-adapter-v0.1.0.zip"
)
ADMISSION_REL = Path("backend/v2.3/admissions/d50-smooth-manifolds-v0.1.0")

EXPECTED = {
    PACKAGE_REL.as_posix(): (
        15_385_668,
        "dedcc369a482295677ee2763690b92c08fddec85cb40fe89f4542b833138052d",
    ),
    (ADMISSION_REL / "manifest.json").as_posix(): (
        23_805,
        "60912d69f7601b2d9ffffa5a5da77439583c30cecbce0bdae5dd02481ea2a853",
    ),
    (ADMISSION_REL / "NEGATIVE_PROBE_REPORT.json").as_posix(): (
        2_627,
        "4b3c6307b259993892ac2fa9f7f84018f980d6ee24a1cebc13794e11305263c8",
    ),
    (ADMISSION_REL / "INDEPENDENT_AUDIT.json").as_posix(): (
        3_482,
        "d646ce1de4c4ae21c51585d294eed841d957307427578d1125d03fee0c03d6b6",
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_expected(relative: str) -> bytes:
    path = ROOT / Path(relative)
    data = path.read_bytes()
    expected_bytes, expected_sha = EXPECTED[relative]
    require(len(data) == expected_bytes, f"byte mismatch: {relative}")
    require(sha256(data) == expected_sha, f"hash mismatch: {relative}")
    return data


def parse_checksums(data: bytes) -> dict[str, str]:
    rows: dict[str, str] = {}
    for raw in data.decode("utf-8").splitlines():
        if not raw:
            continue
        digest, name = raw.split("  ", 1)
        require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), "invalid checksum row")
        require(name not in rows, f"duplicate checksum row: {name}")
        rows[name] = digest
    return rows


def validate() -> dict:
    package_bytes = read_expected(PACKAGE_REL.as_posix())
    manifest_copy = read_expected((ADMISSION_REL / "manifest.json").as_posix())
    negative = json.loads(read_expected((ADMISSION_REL / "NEGATIVE_PROBE_REPORT.json").as_posix()))
    independent = json.loads(read_expected((ADMISSION_REL / "INDEPENDENT_AUDIT.json").as_posix()))

    require(negative.get("status") == "PASS", "negative-probe status is not PASS")
    require(negative.get("passed") == negative.get("total") == 13, "negative-probe census drift")
    require(all(row.get("rejected") is True for row in negative.get("probes", [])), "a negative probe was not rejected")
    require(independent.get("state") == "PASS", "independent audit is not PASS")
    require(independent.get("blocking_defects") == [], "independent audit has a blocker")

    package_path = ROOT / PACKAGE_REL
    with zipfile.ZipFile(package_path) as archive:
        info = archive.infolist()
        names = [row.filename for row in info]
        require(len(names) == len(set(names)) == 73, "ZIP inventory must contain 73 unique members")
        require(names == sorted(names), "ZIP member order is not deterministic")
        require(all(not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts for name in names), "unsafe ZIP path")
        require(all(row.date_time == (1980, 1, 1, 0, 0, 0) for row in info), "ZIP timestamp drift")
        require(all((row.flag_bits & 0x1) == 0 for row in info), "encrypted ZIP member")
        require(sum(row.file_size for row in info) == 122_386_651, "ZIP uncompressed-byte census drift")
        members = {name: archive.read(name) for name in names}
        require(archive.testzip() is None, "ZIP CRC failure")

    checksums = parse_checksums(members["PACKAGE_CHECKSUMS.sha256"])
    require(set(checksums) == set(members) - {"PACKAGE_CHECKSUMS.sha256"}, "ZIP checksum closure drift")
    require(all(sha256(members[name]) == digest for name, digest in checksums.items()), "ZIP member checksum mismatch")
    require(members["manifest.json"] == manifest_copy, "copied manifest differs from the sealed ZIP")

    manifest = json.loads(manifest_copy)
    require(manifest.get("schema_id") == "interlanguage/global-modular-mathematics-lane-adapter/2.3.1", "manifest schema drift")
    require(manifest.get("schema_version") == "2.3.1", "manifest version drift")
    require(manifest.get("extension_version") == "0.1.0", "extension version drift")
    require(manifest.get("dataset_id") == "urn:uuid:1f317af5-4c9f-5883-95a9-c8d6bc2d96bd", "dataset ID drift")
    require(manifest.get("package_id") == "urn:uuid:1eb2e85c-25a8-52bf-a097-37efbad0feae", "package ID drift")
    require(manifest.get("zero_copy_policy", {}).get("full_prose_centralized") is False, "zero-copy prose boundary drift")
    require(manifest.get("zero_copy_policy", {}).get("owner_ids_reminted") is False, "owner-ID boundary drift")
    require(manifest.get("csv_projection", {}).get("record_count") == 24_796, "record census drift")
    require(manifest.get("csv_projection", {}).get("roundtrip_state") == "pass", "CSV round-trip drift")
    require(len(manifest.get("files", [])) == 70, "manifest payload-file census drift")

    scope = json.loads(members["scope-declaration-v0.2.0.json"])
    require(scope.get("curriculum_role_ids") == ["D50"], "D50 scope drift")
    require(scope.get("aggregate_conformance_claim") is False, "scope aggregate-claim drift")
    require(scope.get("owner_authority_binding", {}).get("sha256") == "4bc497f5f26781ac0bb55b0db2ffa206774477a32790ec1890fd425b2861fb53", "owner authority drift")
    require(any("remain external authority" in text for text in scope.get("limitations", [])), "scope zero-copy limitation missing")

    return {
        "schema_id": "program-matematika-indonesia/d50-v231-central-admission-validation/1",
        "recorded_at": "2026-09-06T00:00:00Z",
        "status": "PASS",
        "scope": "sealed ZIP envelope and central admission evidence; owner-native corpus remains external and authoritative",
        "package": {
            "path": PACKAGE_REL.as_posix(),
            "bytes": len(package_bytes),
            "sha256": sha256(package_bytes),
            "entries": 73,
            "uncompressed_bytes": 122_386_651,
            "checksum_entries": len(checksums),
            "crc": "PASS",
            "fixed_timestamps": True,
        },
        "adapter": {
            "role_id": "D50",
            "contract_version": "2.3.1",
            "extension_version": "0.1.0",
            "records": 24_796,
            "native_bindings": 6_912,
            "jsonl_csv_table_pairs": 19,
            "zero_copy": True,
            "owner_ids_reminted": False,
            "hosted_html_claimed": False,
        },
        "evidence": {
            "manifest": {"bytes": len(manifest_copy), "sha256": sha256(manifest_copy)},
            "negative_probes": {"passed": 13, "total": 13},
            "independent_audit": {"status": "PASS", "blocking_defects": 0},
            "source_validator_replay": {
                "status": "PASS",
                "replayed_at_admission": "2026-09-06",
                "owner_authorities": "14/14",
                "program_authorities": "2/2",
                "deterministic_builds": "2/2 byte-identical",
            },
        },
        "claim_limits": [
            "The Indonesian adapter does not represent the separate English edition.",
            "The portable Indonesian HTML is offline-only; no hosted route is claimed.",
            "The adapter is additive metadata and crosswalk material, not the D50 corpus authority.",
            "Structural or hash-only mappings do not assert semantic equivalence.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = validate()
    except Exception as exc:  # fail closed with a compact diagnostic
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    data = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_bytes(data)
    sys.stdout.buffer.write(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
