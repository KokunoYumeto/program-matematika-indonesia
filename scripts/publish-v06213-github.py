#!/usr/bin/env python3
"""Publish or anonymously verify the exact PMI v0.62.13 GitHub release.

The default mode is anonymous, read-only verification.  Remote mutation is
possible only with the explicit ``--publish`` switch and an explicit token
file.  Publication is resumable and idempotent: the script creates at most one
release, uploads only absent assets, never deletes or replaces an asset, and
fails closed if any existing asset has the wrong name, size, or digest.

``--preflight`` performs configuration checks without inspecting the release
directory, loading credentials, or using the network.  ``--dry-run`` validates
the complete local payload without loading credentials or using the network.
No mode invokes Git.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import time
from typing import Any
from urllib.parse import quote
import zipfile

import requests


PROJECT = Path(__file__).resolve().parents[1]
RELEASE_DIR = PROJECT / "releases/v0.62.13"
RECEIPT_PATH = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.13.json"
CHECKSUM_NAME = "RELEASE_CHECKSUMS_v0.62.13.sha256"

OWNER = "KokunoYumeto"
REPOSITORY = "program-matematika-indonesia"
REPOSITORY_SLUG = f"{OWNER}/{REPOSITORY}"
REPOSITORY_URL = f"https://github.com/{REPOSITORY_SLUG}"
API_ROOT = f"https://api.github.com/repos/{REPOSITORY_SLUG}"
VERSION = "0.62.13"
TAG = f"v{VERSION}"
RELEASE_URL = f"{REPOSITORY_URL}/releases/tag/{TAG}"
LEARNER_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
EXPECTED_FILES = 100
EXPECTED_UNCHANGED = 78
EXPECTED_REPLACEMENTS = 9
EXPECTED_PURE_ADDITIONS = 13
EXPECTED_COURSE_COUNT = 40
EXPECTED_PUBLISHED_ROLE_COUNT = 35
EXPECTED_PRODUCTION_ROLE_IDS = ("A20", "A30", "B95", "C140", "D100")
EXPECTED_PRODUCTION_ROLE_COUNT = len(EXPECTED_PRODUCTION_ROLE_IDS)
EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS = 31
PREDECESSOR_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.12.json"
EXPECTED_PREDECESSOR_RECEIPT = (
    51_506,
    "5867905ef9bd9c819cd5998d1f7758e023392249e3aad91106399bd8b479ac3a",
)
EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE = (
    "3254b566c27819c2230ecf4ef2009879058e6bd41359b3926bd5e3fc36fd7c33"
)
SOURCE_ARCHIVE_NAME = "program-matematika-indonesia-source-v0.62.13.zip"
COURSE_CAPSULE_ARCHIVE_NAME = "program-matematika-indonesia-course-capsule-v1.zip"
COURSE_CAPSULE_JSONL_NAME = "course-capsules-v1.jsonl"
COURSE_ID_PATTERN = re.compile(r"([A-D])(00|[1-9][0-9]{1,2})")

# This boundary is intentionally explicit.  A successor may not silently turn
# an inherited file into a replacement or exchange one new artifact for
# another merely while preserving the final cardinality.
PURE_OMISSIONS = frozenset(
    {
        "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.8.html",
        "01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.62.0.html",
        "LIVE_OVERLAY_CHECKSUMS_v0.62.8.sha256",
        "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.8.json",
        "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.8.json",
        "RELEASE_CHECKSUMS_v0.62.11.sha256",
        "RELEASE_CHECKSUMS_v0.62.12.sha256",
        "RELEASE_NOTES_v0.62.11.md",
        "RELEASE_NOTES_v0.62.12.md",
        "o001-a00-assessments-v0.1.0.zip",
        "program-matematika-indonesia-live-overlay-source-v0.62.8.zip",
        "program-matematika-indonesia-source-v0.62.0.zip",
        "program-matematika-indonesia-v0.62.0.html",
    }
)
SAME_NAME_REPLACEMENTS = frozenset(
    {
        "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md",
        "course-capsule-v1.schema.json",
        "course-capsules-v1.jsonl",
        "learner-delivery-v1.json",
        "modular-backend-pattern-index-v1.json",
        "peta-belajar-luring.html",
        COURSE_CAPSULE_ARCHIVE_NAME,
        "v23-adapter-index-v1.json",
        "v23-adapter-index-v1.schema.json",
    }
)
PURE_ADDITIONS = frozenset(
    {
        "A00_O001_V231_ADAPTER_AND_LEARNER_NAVIGATOR_20260831.json",
        "A00_O001_V231_ADAPTER_VALIDATION_REPORT_v0.1.0.json",
        "GITHUB_A00_O001_V231_SOURCE_PUBLICATION_RECEIPT.json",
        "RELEASE_CHECKSUMS_v0.62.13.sha256",
        "RELEASE_NOTES_v0.62.13.md",
        "a00-assessment-map-v1.schema.json",
        "assessment-capability-manifest-v0.1.schema.json",
        "assessment-route-binding-v0.1.schema.json",
        "learner-tools-v1.json",
        "learner-tools-v1.schema.json",
        "program-matematika-indonesia-a00-latihan-v0.1.0.zip",
        "program-matematika-indonesia-backend-v2.3.1-a00-o001-assessment-adapter-v0.1.0.zip",
        SOURCE_ARCHIVE_NAME,
    }
)
USER_AGENT = "Codex-PMI-v06213-GitHub-Publisher/1.0"
MAX_GET_ATTEMPTS = 3
MAX_READBACK_ATTEMPTS = 3
MAX_WORKERS = 6

RELEASE_NAME = "Program Matematika Indonesia v0.62.13 — backend modular terpadu"
RELEASE_BODY = f"""{LEARNER_URL}

Mulai belajar melalui situs Bahasa Indonesia di atas. Berkas JSON, JSONL, CSV,
dan ZIP dalam rilis ini adalah lapisan backend modular dan bukti reproduksi;
berkas tersebut bukan pengganti jalur belajar manusia.

Rilis {TAG} mengintegrasikan kapsul tujuh-lapis untuk {EXPECTED_COURSE_COUNT} peran kurikulum,
dukungan siswa dan pengajar, federasi tanpa penyalinan korpus, serta adapter
lintas-format yang tetap mempertahankan sumber native setiap mata kuliah.
Status penyelesaian setiap peran mengikuti bukti publik yang terikat di dalam
manifest; rilis ini tidak mengubah ketidakpastian menjadi klaim selesai.
Snapshot terikat berisi {EXPECTED_PUBLISHED_ROLE_COUNT} peran dipublikasikan dan {len(EXPECTED_PRODUCTION_ROLE_IDS)} masih berproduksi
({", ".join(EXPECTED_PRODUCTION_ROLE_IDS)}), melalui {EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS} rekaman DOI edisi terbit berbeda.

Provenans model: OpenAI Codex gpt-5.6-sol, Ultra.
"""


class VerificationError(RuntimeError):
    """A local or public identity boundary failed closed."""


class MutationUncertain(RuntimeError):
    """A single mutation may have reached GitHub and must not be repeated."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def api_integer(value: Any, label: str, *, minimum: int | None = None) -> int:
    """Accept only JSON integer fields rather than coercing malformed values."""

    require(type(value) is int, f"{label} is not an integer")
    if minimum is not None:
        require(value >= minimum, f"{label} is below its allowed minimum")
    return value


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_inventory_sha(rows: list[dict[str, Any]]) -> str:
    """Hash the same sorted checksum material used by the v0.62.12 receipt."""

    material = "".join(
        f"{row['sha256']}  {row['name']}\n"
        for row in sorted(rows, key=lambda row: str(row["name"]))
    ).encode("utf-8")
    return sha256_bytes(material)


def validate_course_snapshot(path: Path) -> dict[str, Any]:
    """Derive the public program snapshot from the exact release JSONL."""

    require(path.is_file() and not path.is_symlink(), "course-capsules-v1.jsonl is missing or symlinked")
    data = path.read_bytes()
    require(data.endswith(b"\n") and b"\r" not in data, "course-capsules-v1.jsonl is not canonical LF JSONL")
    raw_lines = data[:-1].split(b"\n")
    require(
        len(raw_lines) == EXPECTED_COURSE_COUNT and all(raw_lines),
        f"course-capsules-v1.jsonl is not exactly {EXPECTED_COURSE_COUNT} nonblank rows",
    )
    rows: list[dict[str, Any]] = []
    for number, raw in enumerate(raw_lines, 1):
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise VerificationError(f"course-capsules-v1.jsonl row {number} is invalid") from exc
        require(isinstance(value, dict), f"course-capsules-v1.jsonl row {number} is not an object")
        rows.append(value)

    canonical_course_ids: list[str] = []
    curricular_keys: list[tuple[str, int]] = []
    for row in rows:
        course_id = row.get("course_id")
        require(isinstance(course_id, str), "course-capsules-v1.jsonl contains a non-string course identity")
        match = COURSE_ID_PATTERN.fullmatch(course_id)
        require(match is not None, f"course-capsules-v1.jsonl contains a noncanonical identity: {course_id!r}")
        assert match is not None
        canonical_course_ids.append(course_id)
        curricular_keys.append((match.group(1), int(match.group(2))))
    require(
        len(set(canonical_course_ids)) == EXPECTED_COURSE_COUNT,
        "course-capsules-v1.jsonl course identities are not unique",
    )
    require(
        curricular_keys == sorted(curricular_keys),
        "course-capsules-v1.jsonl course identities are not in natural curricular order",
    )
    published_ids: list[str] = []
    production_ids: list[str] = []
    published_dois: set[str] = set()
    for row in rows:
        course_id = str(row["course_id"])
        course = row.get("course")
        require(isinstance(course, dict), f"course capsule lacks course state: {course_id}")
        state = course.get("state")
        require(state in {"published", "production"}, f"course capsule state differs: {course_id}")
        if state == "published":
            published_ids.append(course_id)
            course_native = row.get("course_native")
            require(isinstance(course_native, dict), f"published course-native boundary missing: {course_id}")
            doi = course_native.get("zenodo")
            require(
                isinstance(doi, str)
                and re.fullmatch(r"https://doi\.org/10\.5281/zenodo\.\d+", doi) is not None,
                f"published course DOI is missing or malformed: {course_id}",
            )
            published_dois.add(doi)
        else:
            production_ids.append(course_id)

    require(
        len(published_ids) == EXPECTED_PUBLISHED_ROLE_COUNT,
        f"published role count differs: {len(published_ids)}",
    )
    require(
        tuple(production_ids) == EXPECTED_PRODUCTION_ROLE_IDS,
        f"production role roster differs: {production_ids!r}",
    )
    require(
        len(published_dois) == EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS,
        f"distinct published DOI-record count differs: {len(published_dois)}",
    )
    return {
        "course_count": len(rows),
        "published_role_count": len(published_ids),
        "production_role_count": len(production_ids),
        "production_role_ids": production_ids,
        "distinct_published_doi_records": len(published_dois),
        "canonical_course_ids": canonical_course_ids,
        "published_role_ids": published_ids,
    }


def validate_course_capsule_archive(
    path: Path,
    flat_jsonl: bytes,
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Bind both packaged projections and their receipts to the flat JSONL."""

    backend_jsonl_name = "backend/course-capsule-v1/generated/course-capsules.jsonl"
    docs_jsonl_name = "docs/data/course-capsule-v1/course-capsules.jsonl"
    backend_manifest_name = "backend/course-capsule-v1/generated/manifest.json"
    docs_manifest_name = "docs/data/course-capsule-v1/manifest.json"
    backend_validation_name = "backend/course-capsule-v1/validation/VALIDATION_RECEIPT.json"
    docs_validation_name = "docs/data/course-capsule-v1/validation-receipt.json"
    required_names = {
        backend_jsonl_name,
        docs_jsonl_name,
        backend_manifest_name,
        docs_manifest_name,
        backend_validation_name,
        docs_validation_name,
    }

    require(path.is_file() and not path.is_symlink(), "course-capsule archive is missing or symlinked")
    require(path.name == COURSE_CAPSULE_ARCHIVE_NAME, "course-capsule archive filename differs")
    require(zipfile.is_zipfile(path), "course-capsule archive is not a ZIP file")
    try:
        with zipfile.ZipFile(path, "r") as archive:
            members = archive.infolist()
            member_names = [member.filename for member in members]
            require(len(member_names) == len(set(member_names)), "course-capsule archive has duplicate members")
            require(required_names <= set(member_names), "course-capsule archive lacks a required semantic member")
            for name in required_names:
                member = archive.getinfo(name)
                require(not member.is_dir(), f"course-capsule semantic member is a directory: {name}")
                require(member.flag_bits & 0x1 == 0, f"course-capsule semantic member is encrypted: {name}")
            corrupt = archive.testzip()
            require(corrupt is None, f"course-capsule archive CRC validation failed: {corrupt}")
            embedded = {name: archive.read(name) for name in required_names}
    except VerificationError:
        raise
    except (OSError, zipfile.BadZipFile, KeyError, RuntimeError, UnicodeError) as exc:
        raise VerificationError("course-capsule archive could not be validated") from exc

    require(
        embedded[backend_jsonl_name] == flat_jsonl,
        "course-capsule backend JSONL differs from the flat release JSONL",
    )
    require(
        embedded[docs_jsonl_name] == flat_jsonl,
        "course-capsule docs JSONL differs from the flat release JSONL",
    )
    require(
        embedded[backend_manifest_name] == embedded[docs_manifest_name],
        "course-capsule backend/docs manifests differ",
    )
    require(
        embedded[backend_validation_name] == embedded[docs_validation_name],
        "course-capsule backend/docs validation receipts differ",
    )

    def json_object(data: bytes, label: str) -> dict[str, Any]:
        try:
            value = json.loads(data.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise VerificationError(f"embedded {label} is not valid UTF-8 JSON") from exc
        require(isinstance(value, dict), f"embedded {label} is not a JSON object")
        return value

    manifest = json_object(embedded[backend_manifest_name], "course-capsule manifest")
    validation = json_object(embedded[backend_validation_name], "course-capsule validation receipt")
    require(
        manifest.get("schema_id") == "interlanguage/open-course-capsule-manifest/v1",
        "embedded course-capsule manifest schema differs",
    )
    require(
        validation.get("schema_id") == "interlanguage/open-course-capsule-validation-receipt/v1"
        and validation.get("state") == "pass",
        "embedded course-capsule validation receipt is not a passing canonical receipt",
    )

    canonical_identity = {
        "path": "generated/course-capsules.jsonl",
        "bytes": len(flat_jsonl),
        "sha256": sha256_bytes(flat_jsonl),
    }
    require(manifest.get("output") == canonical_identity, "embedded manifest JSONL identity differs")
    artifacts = validation.get("artifacts")
    require(isinstance(artifacts, dict), "embedded validation artifact inventory is missing")
    require(
        artifacts.get("course_capsules_jsonl") == canonical_identity,
        "embedded validation JSONL identity differs",
    )

    expected_counts = {
        "course_count": EXPECTED_COURSE_COUNT,
        "published_count": EXPECTED_PUBLISHED_ROLE_COUNT,
        "production_count": EXPECTED_PRODUCTION_ROLE_COUNT,
    }
    summary = manifest.get("summary")
    require(isinstance(summary, dict), "embedded manifest summary is missing")
    require(
        all(type(summary.get(key)) is int and summary.get(key) == value for key, value in expected_counts.items()),
        "embedded manifest 40/35/5 summary differs",
    )
    checks = validation.get("checks")
    require(isinstance(checks, dict), "embedded validation checks are missing")
    expected_checks: dict[str, Any] = {
        "canonical_jsonl": "pass",
        "schema_instances": EXPECTED_COURSE_COUNT,
        "unique_course_ids": EXPECTED_COURSE_COUNT,
        "seven_layer_rows": EXPECTED_COURSE_COUNT,
        "published_count": EXPECTED_PUBLISHED_ROLE_COUNT,
        "production_count": EXPECTED_PRODUCTION_ROLE_COUNT,
    }
    require(
        all(checks.get(key) == value for key, value in expected_checks.items()),
        "embedded validation 40/35/5 canonical checks differ",
    )
    require(
        snapshot.get("course_count") == EXPECTED_COURSE_COUNT
        and snapshot.get("published_role_count") == EXPECTED_PUBLISHED_ROLE_COUNT
        and snapshot.get("production_role_count") == EXPECTED_PRODUCTION_ROLE_COUNT,
        "flat JSONL snapshot differs from the embedded 40/35/5 contract",
    )

    return {
        "name": COURSE_CAPSULE_ARCHIVE_NAME,
        "canonical_jsonl_identity": canonical_identity,
        "backend_jsonl_byte_identical": True,
        "docs_jsonl_byte_identical": True,
        "backend_docs_manifest_byte_identical": True,
        "backend_docs_validation_receipt_byte_identical": True,
        "course_count": EXPECTED_COURSE_COUNT,
        "published_role_count": EXPECTED_PUBLISHED_ROLE_COUNT,
        "production_role_count": EXPECTED_PRODUCTION_ROLE_COUNT,
        "canonical_course_ids": snapshot["canonical_course_ids"],
        "production_role_ids": snapshot["production_role_ids"],
    }


def predecessor_inventory() -> dict[str, dict[str, Any]]:
    """Load the immutable v0.62.12 inventory used for boundary comparison."""

    require(
        PREDECESSOR_RECEIPT.is_file() and not PREDECESSOR_RECEIPT.is_symlink(),
        "v0.62.12 publication receipt is missing or symlinked",
    )
    data = PREDECESSOR_RECEIPT.read_bytes()
    require(
        (len(data), sha256_bytes(data)) == EXPECTED_PREDECESSOR_RECEIPT,
        "v0.62.12 publication receipt identity differs",
    )
    try:
        receipt = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError("v0.62.12 publication receipt is not valid UTF-8 JSON") from exc
    require(isinstance(receipt, dict), "v0.62.12 publication receipt is not an object")
    require(receipt.get("version") == "0.62.12", "v0.62.12 receipt version differs")
    require(
        receipt.get("payload_inventory_aggregate_sha256")
        == EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
        "v0.62.12 receipt inventory aggregate differs",
    )
    payload = receipt.get("payload_inventory")
    require(isinstance(payload, list) and len(payload) == EXPECTED_FILES, "v0.62.12 inventory is not 100 rows")
    rows: list[dict[str, Any]] = []
    by_name: dict[str, dict[str, Any]] = {}
    for raw in payload:
        require(isinstance(raw, dict), "v0.62.12 inventory row is not an object")
        name = raw.get("name")
        byte_count = raw.get("bytes")
        digest = raw.get("sha256")
        require(
            isinstance(name, str)
            and name not in {".", ".."}
            and "/" not in name
            and "\\" not in name
            and not any(ord(character) < 32 for character in name),
            "v0.62.12 inventory contains an unsafe filename",
        )
        require(type(byte_count) is int and byte_count >= 0, f"v0.62.12 byte count is invalid: {name}")
        require(
            isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
            f"v0.62.12 SHA-256 is invalid: {name}",
        )
        require(name not in by_name, f"v0.62.12 inventory has a duplicate filename: {name}")
        row = {"name": name, "bytes": byte_count, "sha256": digest}
        rows.append(row)
        by_name[name] = row
    require(
        canonical_inventory_sha(rows) == EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
        "v0.62.12 recomputed inventory aggregate differs",
    )
    return by_name


def validate_release_boundary(local_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Prove the exact 78 unchanged + 9 replacements + 13 new contract."""

    require(len(PURE_OMISSIONS) == 13, "pure-omission allowlist cardinality differs")
    require(len(SAME_NAME_REPLACEMENTS) == EXPECTED_REPLACEMENTS, "replacement allowlist cardinality differs")
    require(len(PURE_ADDITIONS) == EXPECTED_PURE_ADDITIONS, "pure-addition allowlist cardinality differs")
    require(SOURCE_ARCHIVE_NAME in PURE_ADDITIONS, "source archive is not a pure addition")

    predecessor = predecessor_inventory()
    local = {str(row["name"]): row for row in local_rows}
    predecessor_names = set(predecessor)
    local_names = set(local)
    omissions = predecessor_names - local_names
    additions = local_names - predecessor_names
    shared = predecessor_names & local_names
    require(omissions == PURE_OMISSIONS, "v0.62.13 pure-omission set differs")
    require(additions == PURE_ADDITIONS, "v0.62.13 pure-addition set differs")
    require(SAME_NAME_REPLACEMENTS <= shared, "a required replacement is absent from the shared inventory")

    changed = {
        name
        for name in shared
        if (
            int(local[name]["bytes"]),
            str(local[name]["sha256"]),
        )
        != (
            int(predecessor[name]["bytes"]),
            str(predecessor[name]["sha256"]),
        )
    }
    unchanged = shared - changed
    require(changed == SAME_NAME_REPLACEMENTS, "v0.62.13 same-name replacement set differs")
    require(len(unchanged) == EXPECTED_UNCHANGED, "v0.62.13 unchanged predecessor count differs")
    require(
        len(local) == EXPECTED_UNCHANGED + EXPECTED_REPLACEMENTS + EXPECTED_PURE_ADDITIONS,
        "v0.62.13 78+9+13 file-count equation differs",
    )
    for name in unchanged:
        require(local[name] == predecessor[name], f"supposedly unchanged predecessor bytes differ: {name}")

    return {
        "predecessor_version": "0.62.12",
        "predecessor_inventory_aggregate_sha256": EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
        "predecessor_files": EXPECTED_FILES,
        "successor_files": EXPECTED_FILES,
        "unchanged_exact_files": EXPECTED_UNCHANGED,
        "same_name_replacements": EXPECTED_REPLACEMENTS,
        "pure_additions": EXPECTED_PURE_ADDITIONS,
        "pure_omissions": len(PURE_OMISSIONS),
        "same_name_replacement_names": sorted(SAME_NAME_REPLACEMENTS),
        "pure_addition_names": sorted(PURE_ADDITIONS),
        "pure_omission_names": sorted(PURE_OMISSIONS),
        "result": "pass_exact_78_unchanged_9_replacements_13_pure_new",
    }


def validate_source_archive(
    path: Path,
    row: dict[str, Any],
    *,
    expected_commit: str | None = None,
) -> dict[str, Any]:
    """Validate a deterministic ``git archive --format=zip`` source archive.

    Git records the archived commit in the ZIP comment.  The caller-supplied
    tree is checked against the GitHub commit object before mutation; the
    checksum manifest and this receipt bind these exact ZIP bytes to that pair.
    """

    require(path.is_file() and not path.is_symlink(), "source archive is missing or symlinked")
    require(path.name == SOURCE_ARCHIVE_NAME, "source archive filename differs")
    require(path.stat().st_size == int(row["bytes"]), "source archive byte count changed")
    require(sha256_file(path) == row["sha256"], "source archive SHA-256 changed")
    require(zipfile.is_zipfile(path), "source archive is not a ZIP file")
    try:
        with zipfile.ZipFile(path, "r") as archive:
            comment = archive.comment
            require(
                re.fullmatch(rb"[0-9a-f]{40}", comment) is not None,
                "source archive ZIP comment is not an exact lowercase commit SHA",
            )
            archive_commit = comment.decode("ascii")
            if expected_commit is not None:
                require(archive_commit == expected_commit, "source archive ZIP comment differs from --target-commit")
            members = archive.infolist()
            require(bool(members), "source archive is empty")
            names = [member.filename for member in members]
            require(len(names) == len(set(names)), "source archive contains duplicate member names")
            require(names == sorted(names), "source archive member order is not deterministic")
            timestamps = {member.date_time for member in members}
            require(len(timestamps) == 1, "source archive members do not share one deterministic timestamp")
            creator_systems = {member.create_system for member in members}
            require(creator_systems <= {0, 3}, "source archive uses unsupported creator metadata")
            require(len(creator_systems) == 1, "source archive mixes creator metadata systems")
            for member in members:
                name = member.filename
                require(
                    name
                    and not name.startswith(("/", "\\"))
                    and "\\" not in name
                    and not any(part in {"", ".", ".."} for part in name.rstrip("/").split("/"))
                    and not any(ord(character) < 32 for character in name),
                    f"source archive contains an unsafe member: {name}",
                )
                require(not (name == ".git" or name.startswith(".git/")), "source archive contains Git internals")
                if member.create_system == 3:
                    unix_mode = (member.external_attr >> 16) & 0xFFFF
                    require(not stat.S_ISLNK(unix_mode), f"source archive member is a symbolic link: {name}")
                require(member.flag_bits & 0x1 == 0, f"source archive member is encrypted: {name}")
                require(
                    member.compress_type in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED},
                    f"source archive member uses a non-git compression method: {name}",
                )
            corrupt = archive.testzip()
            require(corrupt is None, f"source archive CRC validation failed: {corrupt}")
            uncompressed_bytes = sum(member.file_size for member in members)
    except (OSError, zipfile.BadZipFile, UnicodeError) as exc:
        raise VerificationError("source archive could not be validated") from exc

    return {
        "name": SOURCE_ARCHIVE_NAME,
        "bytes": int(row["bytes"]),
        "sha256": str(row["sha256"]),
        "format": "git archive --format=zip",
        "zip_comment_commit": archive_commit,
        "members": len(members),
        "uncompressed_bytes": uncompressed_bytes,
        "member_order_deterministic": True,
        "single_archive_timestamp": True,
        "creator_systems": sorted(creator_systems),
        "unix_symlink_metadata_checked": 3 in creator_systems,
        "dos_creator_bound_by_exact_archive_identity": 0 in creator_systems,
        "crc_validation": "pass",
    }


def local_inventory() -> tuple[list[dict[str, Any]], dict[str, Path], dict[str, Any]]:
    require(RELEASE_DIR.is_dir(), "local v0.62.13 release directory is missing")
    entries = list(RELEASE_DIR.iterdir())
    require(len(entries) == EXPECTED_FILES, "local release is not exactly 100 entries")
    require(
        all(path.is_file() and not path.is_symlink() for path in entries),
        "local release contains a directory, special file, or symbolic link",
    )
    paths = {path.name: path for path in entries}
    require(len(paths) == EXPECTED_FILES, "local release filenames are not unique")
    for name in paths:
        require(
            name not in {".", ".."}
            and "/" not in name
            and "\\" not in name
            and not any(ord(character) < 32 for character in name),
            "local release contains an unsafe filename",
        )

    rows: list[dict[str, Any]] = []
    for name in sorted(paths):
        path = paths[name]
        rows.append(
            {
                "name": name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    checksum_path = paths.get(CHECKSUM_NAME)
    require(checksum_path is not None, "release checksum manifest is missing")
    try:
        lines = checksum_path.read_text(encoding="utf-8").splitlines()
    except UnicodeError as exc:
        raise VerificationError("release checksum manifest is not UTF-8") from exc
    require(len(lines) == EXPECTED_FILES - 1, "release checksum manifest is not 99 rows")
    parsed: dict[str, str] = {}
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/\\\r\n]+)", line)
        require(match is not None, "release checksum manifest syntax differs")
        assert match is not None
        name = match.group(2)
        require(name not in parsed, f"duplicate checksum row: {name}")
        parsed[name] = match.group(1)
    require(
        set(parsed) == set(paths) - {CHECKSUM_NAME},
        "release checksum manifest coverage differs",
    )
    hashes = {str(row["name"]): str(row["sha256"]) for row in rows}
    for name, digest in parsed.items():
        require(digest == hashes[name], f"release checksum mismatch: {name}")
    boundary = validate_release_boundary(rows)
    course_jsonl_path = paths.get(COURSE_CAPSULE_JSONL_NAME)
    require(course_jsonl_path is not None, "flat release course-capsules-v1.jsonl is missing")
    course_snapshot = validate_course_snapshot(course_jsonl_path)
    boundary["course_snapshot"] = course_snapshot
    course_archive_path = paths.get(COURSE_CAPSULE_ARCHIVE_NAME)
    require(course_archive_path is not None, "release course-capsule archive is missing")
    boundary["course_capsule_archive"] = validate_course_capsule_archive(
        course_archive_path,
        course_jsonl_path.read_bytes(),
        course_snapshot,
    )
    source_row = next(row for row in rows if row["name"] == SOURCE_ARCHIVE_NAME)
    boundary["source_archive"] = validate_source_archive(paths[SOURCE_ARCHIVE_NAME], source_row)
    return rows, paths, boundary


def endpoint(path_or_url: str) -> str:
    if path_or_url.startswith("https://"):
        return path_or_url
    return f"{API_ROOT}{path_or_url}"


class GitHubClient:
    """Small GitHub API client with retries only for read-only requests."""

    def __init__(self, token: str | None = None) -> None:
        self.authenticated = token is not None
        self.session = requests.Session()
        # Do not inherit .netrc credentials or ambient proxy credentials.  In
        # particular, token=None must mean a genuinely anonymous observation.
        self.session.trust_env = False
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": USER_AGENT,
        }
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        self.session.headers.update(headers)

    def close(self) -> None:
        self.session.close()

    def json(
        self,
        method: str,
        path_or_url: str,
        *,
        expected: set[int],
        body: Any | None = None,
        mutation: bool = False,
        timeout: int = 120,
    ) -> tuple[int, Any]:
        url = endpoint(path_or_url)
        attempts = 1 if mutation else MAX_GET_ATTEMPTS
        response: requests.Response | None = None
        for attempt in range(1, attempts + 1):
            try:
                response = self.session.request(
                    method,
                    url,
                    json=body,
                    timeout=timeout,
                )
            except requests.RequestException as exc:
                if mutation:
                    raise MutationUncertain(f"{method} outcome is unknown") from exc
                if attempt == attempts:
                    raise VerificationError(f"bounded {method} request failed") from exc
                time.sleep(float(attempt))
                continue
            if response.status_code in expected:
                if not response.content:
                    return response.status_code, {}
                try:
                    return response.status_code, response.json()
                except ValueError as exc:
                    raise VerificationError(f"GitHub API {method} returned invalid JSON") from exc
            if not mutation and response.status_code in {429, 500, 502, 503, 504} and attempt < attempts:
                time.sleep(float(attempt))
                continue
            if mutation:
                raise MutationUncertain(
                    f"{method} returned HTTP {response.status_code}; outcome will not be retried"
                )
            raise VerificationError(f"GitHub API {method} returned HTTP {response.status_code}")
        raise VerificationError(f"bounded {method} request exhausted")


def token_candidates(path: Path) -> list[str]:
    try:
        require(path.is_file(), "GitHub credential file is unavailable")
        require(path.stat().st_size <= 1024 * 1024, "GitHub credential file is unexpectedly large")
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise VerificationError("GitHub credential file could not be read") from exc
    except UnicodeError as exc:
        raise VerificationError("GitHub credential file is not UTF-8") from exc
    labelled = re.findall(
        r"(?im)^\s*(?:github\s+)?(?:access\s+)?token\s*[:=]\s*[`\"']?([A-Za-z0-9_\-.]{32,})",
        text,
    )
    shaped = re.findall(r"(?:github_pat_[A-Za-z0-9_]{40,}|gh[opusr]_[A-Za-z0-9]{32,})", text)
    compact = text.strip().strip("`\"'")
    values = [*labelled, *shaped]
    if compact and not re.search(r"\s", compact) and len(compact) >= 32:
        values.append(compact)
    unique: list[str] = []
    for value in values:
        candidate = value.strip("`\"' \t\r\n")
        if candidate and candidate not in unique:
            unique.append(candidate)
    require(bool(unique), "GitHub credential file contains no token candidate")
    return unique


def authenticated_client(path: Path) -> GitHubClient:
    for candidate in token_candidates(path):
        client = GitHubClient(candidate)
        try:
            status, payload = client.json(
                "GET",
                "https://api.github.com/user",
                expected={200, 401, 403},
            )
        except VerificationError:
            client.close()
            continue
        if status == 200 and isinstance(payload, dict) and payload.get("login") == OWNER:
            return client
        client.close()
    raise VerificationError("no credential candidate authenticates as the repository owner")


def fetch_release(client: GitHubClient) -> dict[str, Any] | None:
    status, payload = client.json(
        "GET",
        f"/releases/tags/{quote(TAG, safe='')}",
        expected={200, 404},
    )
    if status == 404:
        return None
    require(isinstance(payload, dict), "GitHub release response is not an object")
    return payload


def paginated_assets(client: GitHubClient, release_id: int) -> list[dict[str, Any]]:
    _, first = client.json(
        "GET",
        f"/releases/{release_id}/assets?per_page=100&page=1",
        expected={200},
    )
    _, second = client.json(
        "GET",
        f"/releases/{release_id}/assets?per_page=100&page=2",
        expected={200},
    )
    require(isinstance(first, list) and isinstance(second, list), "release asset response is not a list")
    require(not second, "release contains more than 100 assets")
    require(all(isinstance(asset, dict) for asset in first), "release asset row is not an object")
    return first


def validate_remote_inventory(
    assets: list[dict[str, Any]],
    local_rows: list[dict[str, Any]],
    *,
    require_complete: bool,
) -> list[str]:
    local = {str(row["name"]): row for row in local_rows}
    names = [str(asset.get("name") or "") for asset in assets]
    require(len(names) == len(set(names)), "remote release asset names are not unique")
    remote = {str(asset.get("name") or ""): asset for asset in assets}
    extra = sorted(set(remote) - set(local))
    require(not extra, f"remote release contains an extra asset: {extra[0]}")
    for name, asset in remote.items():
        row = local[name]
        require(asset.get("state") == "uploaded", f"remote asset is not uploaded: {name}")
        require(
            api_integer(asset.get("size"), f"remote asset size is invalid: {name}", minimum=0)
            == int(row["bytes"]),
            f"remote asset size differs: {name}",
        )
        require(asset.get("digest") == f"sha256:{row['sha256']}", f"remote asset digest differs: {name}")
    missing = sorted(set(local) - set(remote))
    if require_complete:
        require(not missing, f"remote release is missing asset: {missing[0]}")
        require(len(remote) == EXPECTED_FILES, "remote release is not exactly 100 assets")
    return missing


def resolve_tag_commit(client: GitHubClient) -> tuple[str, str]:
    encoded = quote(f"tags/{TAG}", safe="/")
    _, reference = client.json("GET", f"/git/ref/{encoded}", expected={200})
    require(isinstance(reference, dict), "public tag reference is not an object")
    target = reference.get("object", {})
    require(isinstance(target, dict), "public tag reference target is not an object")
    object_type = target.get("type")
    object_sha = target.get("sha")
    for _ in range(4):
        require(
            isinstance(object_sha, str) and re.fullmatch(r"[0-9a-f]{40}", object_sha) is not None,
            "public tag object lacks a full Git SHA",
        )
        if object_type == "commit":
            break
        require(object_type == "tag", "public tag points to an unsupported object type")
        _, annotated = client.json("GET", f"/git/tags/{object_sha}", expected={200})
        require(isinstance(annotated, dict), "annotated tag response is not an object")
        target = annotated.get("object", {})
        require(isinstance(target, dict), "annotated tag target is not an object")
        object_type = target.get("type")
        object_sha = target.get("sha")
    require(object_type == "commit", "public tag indirection is too deep")
    assert isinstance(object_sha, str)
    _, commit = client.json("GET", f"/git/commits/{object_sha}", expected={200})
    require(isinstance(commit, dict), "public target commit response is not an object")
    tree_object = commit.get("tree")
    require(isinstance(tree_object, dict), "public target commit tree is not an object")
    tree = tree_object.get("sha")
    require(
        isinstance(tree, str) and re.fullmatch(r"[0-9a-f]{40}", tree) is not None,
        "public target commit lacks a full tree SHA",
    )
    return object_sha, tree


def create_release_once(client: GitHubClient, target_commit: str) -> tuple[dict[str, Any], bool]:
    """Create one draft at most; after uncertainty, resume by exact tag only."""

    existing = fetch_release(client)
    if existing is not None:
        return existing, False
    payload = {
        "tag_name": TAG,
        "target_commitish": target_commit,
        "name": RELEASE_NAME,
        "body": RELEASE_BODY,
        "draft": True,
        "prerelease": False,
    }
    try:
        _, created = client.json(
            "POST",
            "/releases",
            expected={201},
            body=payload,
            mutation=True,
        )
        require(isinstance(created, dict), "created release response is not an object")
        return created, True
    except MutationUncertain as exc:
        resumed = fetch_release(client)
        if resumed is None:
            raise VerificationError(
                "release creation outcome is uncertain and no exact-tag release is visible; refusing a second create"
            ) from exc
        return resumed, False


def upload_asset_once(
    client: GitHubClient,
    upload_url: str,
    row: dict[str, Any],
    path: Path,
    release_id: int,
) -> dict[str, Any]:
    """Upload one absent asset once; resolve an uncertain outcome by listing."""

    name = str(row["name"])
    require(path.stat().st_size == int(row["bytes"]), f"local asset changed before upload: {name}")
    require(sha256_file(path) == row["sha256"], f"local asset hash changed before upload: {name}")
    clean_upload_url = upload_url.split("{", 1)[0]
    try:
        with path.open("rb") as stream:
            response = client.session.post(
                clean_upload_url,
                params={"name": name},
                headers={"Content-Type": "application/octet-stream"},
                data=stream,
                timeout=1800,
            )
    except requests.RequestException as exc:
        response = None
        uncertain: Exception = exc
    else:
        uncertain = MutationUncertain(f"asset upload returned HTTP {response.status_code}")
        if response.status_code == 201:
            try:
                asset = response.json()
            except ValueError as exc:
                raise MutationUncertain("asset upload returned invalid JSON") from exc
            require(isinstance(asset, dict), "asset upload response is not an object")
            validate_remote_inventory([asset], [row], require_complete=False)
            return asset

    assets = paginated_assets(client, release_id)
    matches = [asset for asset in assets if str(asset.get("name") or "") == name]
    if len(matches) == 1:
        validate_remote_inventory(matches, [row], require_complete=False)
        return matches[0]
    if len(matches) > 1:
        raise VerificationError(f"uncertain upload produced duplicate assets: {name}") from uncertain
    raise VerificationError(
        f"asset upload outcome is uncertain and asset is absent; refusing a second upload: {name}"
    ) from uncertain


def finalize_release_once(client: GitHubClient, release: dict[str, Any]) -> dict[str, Any]:
    """Publish a draft/prerelease once, resolving uncertainty by exact-tag readback."""

    if not release.get("draft") and not release.get("prerelease"):
        return release
    release_id = api_integer(release.get("id"), "release ID", minimum=1)
    try:
        _, finalized = client.json(
            "PATCH",
            f"/releases/{release_id}",
            expected={200},
            body={
                "name": RELEASE_NAME,
                "body": RELEASE_BODY,
                "draft": False,
                "prerelease": False,
            },
            mutation=True,
        )
        require(isinstance(finalized, dict), "finalized release response is not an object")
        return finalized
    except MutationUncertain as exc:
        resumed = fetch_release(client)
        if resumed is None or resumed.get("draft") or resumed.get("prerelease"):
            raise VerificationError(
                "release finalization outcome is uncertain; refusing a second finalization request"
            ) from exc
        return resumed


def publish(
    target_commit: str,
    requested_tree: str,
    token_file: Path,
    local_rows: list[dict[str, Any]],
    local_paths: dict[str, Path],
) -> dict[str, Any]:
    require(re.fullmatch(r"[0-9a-f]{40}", target_commit) is not None, "--target-commit must be a full lowercase SHA")
    require(re.fullmatch(r"[0-9a-f]{40}", requested_tree) is not None, "--target-tree must be a full lowercase SHA")
    source_row = next(row for row in local_rows if row["name"] == SOURCE_ARCHIVE_NAME)
    source_archive = validate_source_archive(
        local_paths[SOURCE_ARCHIVE_NAME],
        source_row,
        expected_commit=target_commit,
    )
    client = authenticated_client(token_file)
    try:
        _, commit = client.json("GET", f"/git/commits/{target_commit}", expected={200})
        require(isinstance(commit, dict), "target commit response is not an object")
        target_tree_object = commit.get("tree")
        require(isinstance(target_tree_object, dict), "target commit tree is not an object")
        target_tree = target_tree_object.get("sha")
        require(
            isinstance(target_tree, str) and re.fullmatch(r"[0-9a-f]{40}", target_tree) is not None,
            "target commit lacks a full tree SHA",
        )
        require(target_tree == requested_tree, "target commit tree differs from --target-tree")
        release, created = create_release_once(client, target_commit)
        require(release.get("tag_name") == TAG, "resumed release tag differs")
        release_html_url = release.get("html_url")
        if release.get("draft"):
            require(
                isinstance(release_html_url, str)
                and release_html_url.startswith(f"{REPOSITORY_URL}/releases/tag/untagged-"),
                "resumed draft release URL differs",
            )
        else:
            require(release_html_url == RELEASE_URL, "resumed public release URL differs")
        if not release.get("draft") and not release.get("prerelease"):
            require(release.get("name") == RELEASE_NAME, "existing public release name differs")
            require(release.get("body") == RELEASE_BODY, "existing public release body differs")
        release_id = api_integer(release.get("id"), "resumed release ID", minimum=1)

        # If a tag already resolves, it must bind the requested immutable commit.
        encoded_tag = quote(f"tags/{TAG}", safe="/")
        tag_status, _ = client.json(
            "GET",
            f"/git/ref/{encoded_tag}",
            expected={200, 404},
        )
        if tag_status == 404:
            require(
                release.get("draft") and release.get("target_commitish") == target_commit,
                "release target cannot be bound to the requested commit",
            )
        else:
            tag_commit, _ = resolve_tag_commit(client)
            require(tag_commit == target_commit, "existing v0.62.13 tag targets a different commit")

        assets = paginated_assets(client, release_id)
        missing = validate_remote_inventory(assets, local_rows, require_complete=False)
        upload_url = str(release.get("upload_url") or "")
        require(upload_url.startswith("https://uploads.github.com/"), "release upload URL differs")
        uploaded: list[str] = []
        for name in missing:
            upload_asset_once(client, upload_url, {row["name"]: row for row in local_rows}[name], local_paths[name], release_id)
            uploaded.append(name)

        final_assets = paginated_assets(client, release_id)
        validate_remote_inventory(final_assets, local_rows, require_complete=True)
        release = finalize_release_once(client, release)
        require(not release.get("draft") and not release.get("prerelease"), "release is not public final")
        return {
            "created_in_this_execution": created,
            "resumed_existing_release": not created,
            "assets_present_before": len(assets),
            "assets_uploaded_in_this_execution": len(uploaded),
            "uploaded_names": uploaded,
            "target_commit_preflight": target_commit,
            "target_tree_preflight": target_tree,
            "source_archive_preflight": source_archive,
        }
    finally:
        client.close()


def readback_one(asset: dict[str, Any], local: dict[str, Any]) -> dict[str, Any]:
    name = str(asset.get("name") or "")
    url = str(asset.get("browser_download_url") or "")
    expected_prefix = f"{REPOSITORY_URL}/releases/download/{TAG}/"
    require(url.startswith(expected_prefix), f"asset download URL differs: {name}")
    require(
        api_integer(asset.get("size"), f"API asset size is invalid: {name}", minimum=0)
        == int(local["bytes"]),
        f"API asset size differs: {name}",
    )
    require(asset.get("digest") == f"sha256:{local['sha256']}", f"API asset digest differs: {name}")

    last_failure = "anonymous readback failed"
    session = requests.Session()
    session.trust_env = False
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/octet-stream"})
    try:
        for attempt in range(1, MAX_READBACK_ATTEMPTS + 1):
            digest = hashlib.sha256()
            byte_count = 0
            response: requests.Response | None = None
            try:
                response = session.get(url, stream=True, timeout=(30, 180))
                if response.status_code != 200:
                    last_failure = f"anonymous asset HTTP {response.status_code}"
                else:
                    for chunk in response.iter_content(1024 * 1024):
                        if chunk:
                            digest.update(chunk)
                            byte_count += len(chunk)
                    actual_sha = digest.hexdigest()
                    if byte_count == int(local["bytes"]) and actual_sha == local["sha256"]:
                        return {
                            "name": name,
                            "bytes": byte_count,
                            "sha256": actual_sha,
                            "api_digest": str(asset.get("digest")),
                            "anonymous_http_status": 200,
                            "anonymous_byte_identity": True,
                            "url": url,
                        }
                    last_failure = "anonymous asset bytes differ"
            except requests.RequestException:
                last_failure = "anonymous asset transport failed"
            finally:
                if response is not None:
                    response.close()
            if attempt < MAX_READBACK_ATTEMPTS:
                time.sleep(float(attempt))
    finally:
        session.close()
    raise VerificationError(f"{last_failure}: {name}")


def anonymous_public_readback(
    local_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], str, str, list[dict[str, Any]]]:
    client = GitHubClient()
    try:
        _, repository = client.json("GET", "", expected={200})
        require(isinstance(repository, dict), "repository response is not an object")
        require(repository.get("private") is False, "repository is not public")
        require(repository.get("disabled") is False, "repository is disabled")
        release = fetch_release(client)
        require(release is not None, "public v0.62.13 release is absent")
        assert release is not None
        require(release.get("html_url") == RELEASE_URL, "public release URL differs")
        require(release.get("tag_name") == TAG, "public release tag differs")
        require(not release.get("draft"), "public release is a draft")
        require(not release.get("prerelease"), "public release is a prerelease")
        require(release.get("name") == RELEASE_NAME, "public release name differs")
        require(release.get("body") == RELEASE_BODY, "public release body differs")
        release_id = api_integer(release.get("id"), "public release ID", minimum=1)
        assets = paginated_assets(client, release_id)
        validate_remote_inventory(assets, local_rows, require_complete=True)
        source_commit, source_tree = resolve_tag_commit(client)
    finally:
        client.close()

    local = {str(row["name"]): row for row in local_rows}
    remote = {str(asset.get("name") or ""): asset for asset in assets}
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(readback_one, remote[name], local[name]): name
            for name in sorted(local)
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                raise VerificationError(f"anonymous readback failed for {name}: {exc}") from exc
    results.sort(key=lambda row: str(row["name"]))
    require(len(results) == EXPECTED_FILES, "anonymous readback count differs")
    require(
        sum(int(row["bytes"]) for row in results) == sum(int(row["bytes"]) for row in local_rows),
        "anonymous readback byte total differs",
    )
    require(
        canonical_inventory_sha(results) == canonical_inventory_sha(local_rows),
        "anonymous readback inventory aggregate differs",
    )
    return release, source_commit, source_tree, results


def receipt_payload(
    local_rows: list[dict[str, Any]],
    local_paths: dict[str, Path],
    boundary: dict[str, Any],
    release: dict[str, Any],
    source_commit: str,
    source_tree: str,
    readback: list[dict[str, Any]],
    execution: dict[str, Any],
) -> dict[str, Any]:
    total_bytes = sum(int(row["bytes"]) for row in local_rows)
    aggregate = canonical_inventory_sha(local_rows)
    checksum_row = next(row for row in local_rows if row["name"] == CHECKSUM_NAME)
    source_row = next(row for row in local_rows if row["name"] == SOURCE_ARCHIVE_NAME)
    source_archive = validate_source_archive(
        local_paths[SOURCE_ARCHIVE_NAME],
        source_row,
        expected_commit=source_commit,
    )
    require(boundary.get("source_archive") == source_archive, "source archive evidence changed before receipt")
    publisher = Path(__file__).resolve()
    body_bytes = str(release.get("body") or "").encode("utf-8")
    return {
        "schema_id": "program-matematika-indonesia/github-publication-receipt/1.2.0",
        "recorded_at_utc": utc_now(),
        "version": VERSION,
        "tag": TAG,
        "state": "published_public_verified",
        "mode": "publish_then_anonymous_verify" if execution.get("publish_requested") else "anonymous_verify_only",
        "repository": REPOSITORY_URL,
        "repository_public": True,
        "learner_primary_url": LEARNER_URL,
        "model_provenance": "OpenAI Codex gpt-5.6-sol, Ultra",
        "source": {
            "commit": source_commit,
            "tree": source_tree,
            "tag_resolves_to_commit": True,
            "archive": source_archive,
        },
        "release": {
            "id": api_integer(release.get("id"), "receipt release ID", minimum=1),
            "url": str(release["html_url"]),
            "name": str(release.get("name") or ""),
            "created_at": str(release.get("created_at") or ""),
            "published_at": str(release.get("published_at") or ""),
            "draft": False,
            "prerelease": False,
            "tag": TAG,
            "tag_target_commit": source_commit,
            "tag_target_tree": source_tree,
            "tag_resolves_to_commit": True,
            "body_sha256": sha256_bytes(body_bytes),
        },
        "replacement_boundary": boundary,
        "inventory": {
            "files": EXPECTED_FILES,
            "bytes": total_bytes,
            "aggregate_sha256": aggregate,
            "canonicalization": "sorted rows formatted as '<sha256>  <name>\\n'",
            "checksum_manifest": {
                "name": CHECKSUM_NAME,
                "rows": EXPECTED_FILES - 1,
                "bytes": int(checksum_row["bytes"]),
                "sha256": str(checksum_row["sha256"]),
                "coverage": "all_release_files_except_self",
            },
            "entries": local_rows,
        },
        "anonymous_asset_readback": {
            "result": "pass_100_of_100",
            "files": EXPECTED_FILES,
            "bytes": total_bytes,
            "aggregate_sha256": aggregate,
            "entries": readback,
        },
        "execution": execution,
        "publisher": {
            "path": publisher.relative_to(PROJECT).as_posix(),
            "bytes": publisher.stat().st_size,
            "sha256": sha256_file(publisher),
            "git_commands_used": 0,
            "asset_deletions": 0,
            "asset_replacements": 0,
            "mutation_retry_policy": "single_attempt_then_exact_tag_or_asset_readback",
        },
        "privacy": {
            "absolute_profile_paths_recorded": False,
            "credential_locator_recorded": False,
            "credentials_recorded": False,
            "personal_name_recorded": False,
        },
    }


def atomic_write_receipt(receipt: dict[str, Any]) -> None:
    encoded = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    lowered = encoded.lower()
    require(b"c:\\users\\" not in lowered, "receipt contains an absolute profile path")
    require(b"authorization: bearer" not in lowered, "receipt contains an authorization header")
    require(b"access_token=" not in lowered, "receipt contains a credential query")
    require(
        re.search(rb"(?:github_pat_[a-z0-9_]{20,}|gh[opusr]_[a-z0-9]{20,})", lowered) is None,
        "receipt contains a credential-shaped value",
    )
    handle, temp_name = tempfile.mkstemp(prefix=".v06213-github-receipt-", suffix=".json", dir=PROJECT)
    temp = Path(temp_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        parsed = json.loads(temp.read_text(encoding="utf-8"))
        require(parsed == receipt, "temporary receipt JSON readback differs")
        os.replace(temp, RECEIPT_PATH)
    finally:
        if temp.exists():
            temp.unlink()


def preflight() -> dict[str, Any]:
    require(VERSION == "0.62.13" and TAG == "v0.62.13", "version/tag constants differ")
    require(RELEASE_DIR == PROJECT / "releases/v0.62.13", "release directory boundary differs")
    require(RECEIPT_PATH == PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.13.json", "receipt path boundary differs")
    require(EXPECTED_FILES == 100, "expected release count differs")
    require(
        EXPECTED_UNCHANGED + EXPECTED_REPLACEMENTS + EXPECTED_PURE_ADDITIONS == EXPECTED_FILES,
        "78+9+13 release equation differs",
    )
    require(len(PURE_OMISSIONS) == 13, "pure-omission allowlist differs")
    require(len(SAME_NAME_REPLACEMENTS) == EXPECTED_REPLACEMENTS, "replacement allowlist differs")
    require(len(PURE_ADDITIONS) == EXPECTED_PURE_ADDITIONS, "pure-addition allowlist differs")
    require(
        EXPECTED_COURSE_COUNT == 40
        and EXPECTED_PUBLISHED_ROLE_COUNT == 35
        and EXPECTED_PRODUCTION_ROLE_COUNT == 5
        and EXPECTED_PUBLISHED_ROLE_COUNT + EXPECTED_PRODUCTION_ROLE_COUNT == EXPECTED_COURSE_COUNT,
        "35+5=40 course-count constants differ",
    )
    require(
        len(EXPECTED_PRODUCTION_ROLE_IDS)
        == len(set(EXPECTED_PRODUCTION_ROLE_IDS))
        == EXPECTED_PRODUCTION_ROLE_COUNT,
        "production roster is not exactly five unique identities",
    )
    require(
        all(COURSE_ID_PATTERN.fullmatch(course_id) is not None for course_id in EXPECTED_PRODUCTION_ROLE_IDS)
        and list(EXPECTED_PRODUCTION_ROLE_IDS)
        == sorted(EXPECTED_PRODUCTION_ROLE_IDS, key=lambda course_id: (course_id[0], int(course_id[1:]))),
        "production roster identities are not canonical and naturally ordered",
    )
    require(
        EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS == 31
        and 0 < EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS <= EXPECTED_PUBLISHED_ROLE_COUNT,
        "0<31<=35 distinct DOI-count constants differ",
    )
    require(RELEASE_BODY.startswith(LEARNER_URL), "learner URL is not first in the release body")
    require("token" not in RELEASE_BODY.casefold(), "release body contains credential terminology")
    return {
        "status": "PASS_OFFLINE_PREFLIGHT",
        "version": VERSION,
        "tag": TAG,
        "expected_files": EXPECTED_FILES,
        "expected_unchanged": EXPECTED_UNCHANGED,
        "expected_replacements": EXPECTED_REPLACEMENTS,
        "expected_pure_additions": EXPECTED_PURE_ADDITIONS,
        "expected_course_count": EXPECTED_COURSE_COUNT,
        "expected_published_role_count": EXPECTED_PUBLISHED_ROLE_COUNT,
        "expected_production_role_count": EXPECTED_PRODUCTION_ROLE_COUNT,
        "expected_production_role_ids": list(EXPECTED_PRODUCTION_ROLE_IDS),
        "expected_distinct_published_doi_records": EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS,
        "network_calls": 0,
        "credential_reads": 0,
        "release_directory_inspected": False,
        "git_commands_used": 0,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--publish",
        action="store_true",
        help="explicitly create/resume and publish v0.62.13 before anonymous verification",
    )
    modes.add_argument(
        "--dry-run",
        action="store_true",
        help="validate the exact local 100-file payload without network or credentials",
    )
    modes.add_argument(
        "--preflight",
        action="store_true",
        help="validate script constants without release bytes, network, or credentials",
    )
    parser.add_argument(
        "--target-commit",
        help="exact lowercase 40-character commit required only with --publish",
    )
    parser.add_argument(
        "--target-tree",
        help="exact lowercase 40-character tree required only with --publish",
    )
    parser.add_argument(
        "--token-file",
        type=Path,
        help="credential file read only with --publish; never serialized or printed",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.preflight:
            require(args.token_file is None, "--preflight refuses --token-file")
            require(args.target_commit is None, "--preflight does not need --target-commit")
            require(args.target_tree is None, "--preflight does not need --target-tree")
            print(json.dumps(preflight(), sort_keys=True, separators=(",", ":")))
            return 0

        if args.dry_run:
            require(args.token_file is None, "--dry-run refuses --token-file")
            require(args.target_commit is None, "--dry-run does not need --target-commit")
            require(args.target_tree is None, "--dry-run does not need --target-tree")
            rows, _, boundary = local_inventory()
            result = {
                "status": "PASS_LOCAL_DRY_RUN_100_OF_100",
                "version": VERSION,
                "tag": TAG,
                "files": len(rows),
                "bytes": sum(int(row["bytes"]) for row in rows),
                "inventory_aggregate_sha256": canonical_inventory_sha(rows),
                "replacement_boundary": boundary,
                "network_calls": 0,
                "credential_reads": 0,
                "receipt_written": False,
                "git_commands_used": 0,
            }
            print(json.dumps(result, sort_keys=True, separators=(",", ":")))
            return 0

        if args.publish:
            require(args.token_file is not None, "--publish requires --token-file")
            require(args.target_commit is not None, "--publish requires --target-commit")
            require(args.target_tree is not None, "--publish requires --target-tree")
        else:
            require(args.token_file is None, "anonymous verify-only mode refuses --token-file")
            require(args.target_commit is None, "anonymous verify-only mode derives the exact tag target")
            require(args.target_tree is None, "anonymous verify-only mode derives the exact tag tree")

        rows, paths, boundary = local_inventory()
        execution: dict[str, Any] = {
            "publish_requested": bool(args.publish),
            "created_in_this_execution": False,
            "resumed_existing_release": False,
            "assets_present_before": None,
            "assets_uploaded_in_this_execution": 0,
            "uploaded_names": [],
            "release_mutation_calls_are_bounded": True,
            "git_commands_used": 0,
        }
        if args.publish:
            assert args.target_commit is not None and args.target_tree is not None and args.token_file is not None
            execution.update(
                publish(
                    args.target_commit,
                    args.target_tree,
                    args.token_file.resolve(),
                    rows,
                    paths,
                )
            )

        release, source_commit, source_tree, readback = anonymous_public_readback(rows)
        if args.publish:
            require(source_commit == args.target_commit, "anonymous tag target differs from requested commit")
            require(source_tree == args.target_tree, "anonymous tag tree differs from requested tree")
        source_row = next(row for row in rows if row["name"] == SOURCE_ARCHIVE_NAME)
        validate_source_archive(paths[SOURCE_ARCHIVE_NAME], source_row, expected_commit=source_commit)
        final_rows, _, final_boundary = local_inventory()
        require(final_rows == rows, "local release bytes changed during verification")
        require(final_boundary == boundary, "local release boundary changed during verification")
        receipt = receipt_payload(
            rows,
            paths,
            boundary,
            release,
            source_commit,
            source_tree,
            readback,
            execution,
        )
        atomic_write_receipt(receipt)
        receipt_bytes = RECEIPT_PATH.read_bytes()
        require(json.loads(receipt_bytes.decode("utf-8")) == receipt, "final receipt JSON readback differs")
        print(
            json.dumps(
                {
                    "status": "PASS_PUBLIC_ANONYMOUS_READBACK_100_OF_100",
                    "mode": receipt["mode"],
                    "release": RELEASE_URL,
                    "source_commit": source_commit,
                    "source_tree": source_tree,
                    "files": EXPECTED_FILES,
                    "bytes": receipt["inventory"]["bytes"],
                    "inventory_aggregate_sha256": receipt["inventory"]["aggregate_sha256"],
                    "receipt": RECEIPT_PATH.relative_to(PROJECT).as_posix(),
                    "receipt_bytes": len(receipt_bytes),
                    "receipt_sha256": sha256_bytes(receipt_bytes),
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    except (VerificationError, MutationUncertain, OSError) as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(
            json.dumps(
                {"status": "FAIL_CLOSED", "version": VERSION, "error": detail},
                sort_keys=True,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
