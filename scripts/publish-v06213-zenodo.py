#!/usr/bin/env python3
"""Publish and anonymously verify PMI v0.62.13 on its Zenodo lineage.

The ``--preflight`` path is intentionally implemented before the inherited
publisher is imported.  It uses only the Python standard library, reads no
credential, opens no network connection, creates no draft, and writes no
file.  Publication mode first searches the public concept lineage through a
credential-free session.  It verifies an exact public v0.62.13 without
authentication, or creates/resumes at most one index-38 draft only while the
exact v0.62.12 predecessor remains latest.

Published records are immutable in this workflow.  File removal is permitted
only inside the unpublished successor draft and only for the exact successor
boundary: thirteen predecessor-only omissions and nine same-name replacements.
The successor retains 78 predecessor files byte-for-byte, replaces nine names,
adds thirteen genuinely new names, and therefore remains exactly 100 files.
Receipts are written only after open-access publication and full anonymous byte
readback of successor and predecessor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import threading
import types
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlencode, urljoin, urlparse


PROJECT = Path(__file__).resolve().parents[1]
TEMPLATE_SCRIPT = PROJECT / "scripts/publish-v06212-zenodo.py"
RELEASE_DIR = PROJECT / "releases/v0.62.13"
CHECKSUM_FILE = RELEASE_DIR / "RELEASE_CHECKSUMS_v0.62.13.sha256"
GITHUB_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.13.json"
PREDECESSOR_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.12.json"
VERSION_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.13.json"
ROOT_RECEIPT = PROJECT / "PUBLICATION_RECEIPT.json"
RESERVATION_CURSOR = PROJECT / "ZENODO_RESERVATION_CURSOR_v0.62.13.json"

sys.dont_write_bytecode = True

VERSION = "0.62.13"
PREDECESSOR_VERSION = "0.62.12"
CONCEPT_ID = 22059707
PREDECESSOR_ID = 22182000
PREDECESSOR_INDEX = 37
SUCCESSOR_INDEX = 38
EXPECTED_FILES = 100
EXPECTED_RETAINED = 78
EXPECTED_SAME_NAME_REPLACEMENTS = 9
EXPECTED_PURE_OMISSIONS = 13
EXPECTED_PURE_ADDITIONS = 13
EXPECTED_EFFECTIVE_OMISSIONS = EXPECTED_SAME_NAME_REPLACEMENTS + EXPECTED_PURE_OMISSIONS
EXPECTED_EFFECTIVE_ADDITIONS = EXPECTED_SAME_NAME_REPLACEMENTS + EXPECTED_PURE_ADDITIONS
EXPECTED_COURSE_COUNT = 40
EXPECTED_PUBLISHED_ROLE_COUNT = 35
EXPECTED_PRODUCTION_ROLE_COUNT = 5
EXPECTED_PRODUCTION_ROLE_IDS = ("A20", "A30", "B95", "C140", "D100")
EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS = 31
ADAPTER_BOUND_ROLES = ("A00", "B10", "D20", "D60", "D110")
NATIVE_ONLY_ROLE_COUNT = 35
IMPLEMENTATION_FAMILY_COUNT = 33
COURSE_ID_PATTERN = re.compile(r"[A-D](?:00|[1-9][0-9]{1,2})")
PUBLISHED_ZENODO_DOI_PATTERN = re.compile(
    r"https://doi\.org/10\.5281/zenodo\.([1-9][0-9]*)"
)

COURSE_CAPSULE_ARCHIVE_NAME = "program-matematika-indonesia-course-capsule-v1.zip"
COURSE_CAPSULE_JSONL_NAME = "course-capsules-v1.jsonl"
COURSE_CAPSULE_JSONL_MEMBER = (
    "backend/course-capsule-v1/generated/course-capsules.jsonl"
)
COURSE_CAPSULE_PUBLIC_JSONL_MEMBER = (
    "docs/data/course-capsule-v1/course-capsules.jsonl"
)
COURSE_CAPSULE_MANIFEST_MEMBER = "backend/course-capsule-v1/generated/manifest.json"
COURSE_CAPSULE_PUBLIC_MANIFEST_MEMBER = "docs/data/course-capsule-v1/manifest.json"
COURSE_CAPSULE_RECEIPT_MEMBER = (
    "backend/course-capsule-v1/validation/VALIDATION_RECEIPT.json"
)
COURSE_CAPSULE_PUBLIC_RECEIPT_MEMBER = (
    "docs/data/course-capsule-v1/validation-receipt.json"
)

EXPECTED_TEMPLATE = (
    43_337,
    "7ace6cbbdeb3ae80bda12f85f4fa24d7204209f860ab082c974437dddcf4cf75",
)
EXPECTED_PREDECESSOR_RECEIPT = (
    51_506,
    "5867905ef9bd9c819cd5998d1f7758e023392249e3aad91106399bd8b479ac3a",
)
EXPECTED_PREDECESSOR_AGGREGATE = (
    "3254b566c27819c2230ecf4ef2009879058e6bd41359b3926bd5e3fc36fd7c33"
)

SAME_NAME_REPLACEMENTS = {
    "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md",
    "course-capsule-v1.schema.json",
    "course-capsules-v1.jsonl",
    "learner-delivery-v1.json",
    "modular-backend-pattern-index-v1.json",
    "peta-belajar-luring.html",
    "program-matematika-indonesia-course-capsule-v1.zip",
    "v23-adapter-index-v1.json",
    "v23-adapter-index-v1.schema.json",
}

PURE_OMISSIONS = {
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

PURE_ADDITIONS = {
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
    "program-matematika-indonesia-source-v0.62.13.zip",
}

OMITTED = SAME_NAME_REPLACEMENTS | PURE_OMISSIONS
ADDITIONS = SAME_NAME_REPLACEMENTS | PURE_ADDITIONS


def _identity(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _natural_course_id_key(course_id: str) -> tuple[str, int]:
    return course_id[0], int(course_id[1:])


def _assert_constant_self_consistency() -> None:
    """Fail before file inspection when the pinned release equations disagree."""

    integer_constants = {
        "EXPECTED_FILES": EXPECTED_FILES,
        "EXPECTED_RETAINED": EXPECTED_RETAINED,
        "EXPECTED_SAME_NAME_REPLACEMENTS": EXPECTED_SAME_NAME_REPLACEMENTS,
        "EXPECTED_PURE_OMISSIONS": EXPECTED_PURE_OMISSIONS,
        "EXPECTED_PURE_ADDITIONS": EXPECTED_PURE_ADDITIONS,
        "EXPECTED_EFFECTIVE_OMISSIONS": EXPECTED_EFFECTIVE_OMISSIONS,
        "EXPECTED_EFFECTIVE_ADDITIONS": EXPECTED_EFFECTIVE_ADDITIONS,
        "EXPECTED_COURSE_COUNT": EXPECTED_COURSE_COUNT,
        "EXPECTED_PUBLISHED_ROLE_COUNT": EXPECTED_PUBLISHED_ROLE_COUNT,
        "EXPECTED_PRODUCTION_ROLE_COUNT": EXPECTED_PRODUCTION_ROLE_COUNT,
        "EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS": EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS,
        "NATIVE_ONLY_ROLE_COUNT": NATIVE_ONLY_ROLE_COUNT,
        "IMPLEMENTATION_FAMILY_COUNT": IMPLEMENTATION_FAMILY_COUNT,
    }
    _require(
        all(type(value) is int and value > 0 for value in integer_constants.values()),
        "v0.62.13 positive-integer constants differ",
    )
    _require(
        (
            EXPECTED_COURSE_COUNT,
            EXPECTED_PUBLISHED_ROLE_COUNT,
            EXPECTED_PRODUCTION_ROLE_COUNT,
            EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS,
        )
        == (40, 35, 5, 31),
        "course-snapshot constants differ from the pinned 40/35/5/31 boundary",
    )
    _require(
        EXPECTED_PRODUCTION_ROLE_IDS == ("A20", "A30", "B95", "C140", "D100"),
        "production-role constants differ from the pinned five-role roster",
    )
    _require(
        len(SAME_NAME_REPLACEMENTS) == EXPECTED_SAME_NAME_REPLACEMENTS
        and len(PURE_OMISSIONS) == EXPECTED_PURE_OMISSIONS
        and len(PURE_ADDITIONS) == EXPECTED_PURE_ADDITIONS
        and len(OMITTED) == EXPECTED_EFFECTIVE_OMISSIONS
        and len(ADDITIONS) == EXPECTED_EFFECTIVE_ADDITIONS,
        "v0.62.13 release-boundary set cardinalities differ",
    )
    _require(
        SAME_NAME_REPLACEMENTS.isdisjoint(PURE_OMISSIONS)
        and SAME_NAME_REPLACEMENTS.isdisjoint(PURE_ADDITIONS)
        and PURE_OMISSIONS.isdisjoint(PURE_ADDITIONS),
        "v0.62.13 release-boundary sets overlap unexpectedly",
    )
    _require(
        EXPECTED_RETAINED
        + EXPECTED_SAME_NAME_REPLACEMENTS
        + EXPECTED_PURE_ADDITIONS
        == EXPECTED_FILES,
        "v0.62.13 successor file-count equation differs",
    )
    _require(
        EXPECTED_EFFECTIVE_OMISSIONS
        == EXPECTED_SAME_NAME_REPLACEMENTS + EXPECTED_PURE_OMISSIONS
        and EXPECTED_EFFECTIVE_ADDITIONS
        == EXPECTED_SAME_NAME_REPLACEMENTS + EXPECTED_PURE_ADDITIONS,
        "v0.62.13 effective draft-boundary equations differ",
    )

    production_ids = list(EXPECTED_PRODUCTION_ROLE_IDS)
    _require(
        len(production_ids) == EXPECTED_PRODUCTION_ROLE_COUNT
        and len(set(production_ids)) == EXPECTED_PRODUCTION_ROLE_COUNT,
        "production-role constants are not exactly five unique identities",
    )
    _require(
        all(COURSE_ID_PATTERN.fullmatch(course_id) is not None for course_id in production_ids)
        and production_ids == sorted(production_ids, key=_natural_course_id_key),
        "production-role constants are not canonical and naturally ordered",
    )
    _require(
        EXPECTED_PUBLISHED_ROLE_COUNT + EXPECTED_PRODUCTION_ROLE_COUNT
        == EXPECTED_COURSE_COUNT,
        "course-state count constants do not close at 40",
    )
    _require(
        0 < EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS <= EXPECTED_PUBLISHED_ROLE_COUNT,
        "published DOI-record count is incompatible with the published-role count",
    )

    adapter_ids = list(ADAPTER_BOUND_ROLES)
    _require(
        len(adapter_ids) == len(set(adapter_ids))
        and all(COURSE_ID_PATTERN.fullmatch(course_id) is not None for course_id in adapter_ids)
        and adapter_ids == sorted(adapter_ids, key=_natural_course_id_key),
        "adapter-bound role constants are not unique, canonical, and naturally ordered",
    )
    _require(
        set(adapter_ids).isdisjoint(production_ids)
        and len(adapter_ids) + NATIVE_ONLY_ROLE_COUNT == EXPECTED_COURSE_COUNT,
        "adapter/native-only role constants do not partition the 40 roles",
    )
    _require(
        IMPLEMENTATION_FAMILY_COUNT == 33
        and IMPLEMENTATION_FAMILY_COUNT != EXPECTED_PUBLISHED_ROLE_COUNT
        and IMPLEMENTATION_FAMILY_COUNT < EXPECTED_COURSE_COUNT,
        "implementation-family count must remain the separate 33-family measure",
    )


def _strict_json_value(data: bytes, label: str) -> Any:
    """Parse UTF-8 JSON while rejecting BOMs, duplicate keys, and non-finite numbers."""

    _require(not data.startswith(b"\xef\xbb\xbf"), f"{label} has a UTF-8 BOM")

    def object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_nonfinite(value: str) -> Any:
        raise ValueError(f"non-finite JSON number: {value}")

    try:
        text = data.decode("utf-8")
        return json.loads(
            text,
            object_pairs_hook=object_without_duplicates,
            parse_constant=reject_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(f"{label} is not strict UTF-8 JSON") from exc


def _canonical_json_object(data: bytes, label: str) -> dict[str, Any]:
    value = _strict_json_value(data, label)
    _require(isinstance(value, dict), f"{label} is not a JSON object")
    try:
        canonical = (
            json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise RuntimeError(f"{label} cannot be represented as canonical JSON") from exc
    _require(data == canonical, f"{label} is not canonical UTF-8/LF JSON")
    return value


def _same_canonical_json_value(left: Any, right: Any) -> bool:
    """Compare JSON values without Python's bool/int or int/float equivalence."""

    try:
        options = {
            "ensure_ascii": False,
            "sort_keys": True,
            "separators": (",", ":"),
            "allow_nan": False,
        }
        return json.dumps(left, **options) == json.dumps(right, **options)
    except (TypeError, ValueError, UnicodeEncodeError):
        return False


def _inventory_sha(rows: list[dict[str, Any]]) -> str:
    material = "".join(
        f"{row['sha256']}  {row['name']}\n"
        for row in sorted(rows, key=lambda item: str(item["name"]))
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"{label} is unavailable or malformed") from exc
    try:
        value = _strict_json_value(data, label)
    except RuntimeError as exc:
        raise RuntimeError(f"{label} is unavailable or malformed") from exc
    _require(isinstance(value, dict), f"{label} is not a JSON object")
    return value


_FORBIDDEN_RECEIPT_KEYS = {
    "access_token",
    "api_key",
    "authorization",
    "cookie",
    "credential_path",
    "password",
    "proxy_authorization",
    "secret",
    "token",
    "token_file",
}


def _assert_sanitized_receipt(value: Any, location: str = "receipt") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            _require(normalized not in _FORBIDDEN_RECEIPT_KEYS, f"sensitive receipt key: {location}.{key}")
            _assert_sanitized_receipt(child, f"{location}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _assert_sanitized_receipt(child, f"{location}[{index}]")
        return
    if isinstance(value, str):
        _require(
            re.search(r"(?i)(authorization\s*:\s*bearer|access[_-]?token\s*=|api[_-]?key\s*=)", value)
            is None,
            f"credential-like receipt value: {location}",
        )
        _require(
            re.match(r"(?i)^[a-z]:[\\/]+users[\\/]", value) is None,
            f"absolute profile path in receipt: {location}",
        )
        _require(not value.lower().startswith("file://"), f"local file URL in receipt: {location}")


def _checksum_rows() -> dict[str, str]:
    _require(CHECKSUM_FILE.is_file(), "v0.62.13 checksum manifest is missing")
    rows: dict[str, str] = {}
    for line_number, line in enumerate(
        CHECKSUM_FILE.read_text(encoding="utf-8").splitlines(), 1
    ):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        _require(match is not None, f"malformed checksum manifest row {line_number}")
        digest, name = match.groups()
        _require(name not in rows, f"duplicate checksum manifest row: {name}")
        rows[name] = digest
    _require(len(rows) == EXPECTED_FILES - 1, "checksum manifest is not exactly 99 rows")
    return rows


def _course_snapshot(path: Path) -> dict[str, Any]:
    """Derive the public program snapshot from the exact release JSONL."""

    _assert_constant_self_consistency()
    _require(path.is_file() and not path.is_symlink(), "course-capsules-v1.jsonl is missing or symlinked")
    data = path.read_bytes()
    _require(data.endswith(b"\n") and b"\r" not in data, "course-capsules-v1.jsonl is not canonical LF JSONL")
    raw_lines = data[:-1].split(b"\n")
    _require(
        len(raw_lines) == EXPECTED_COURSE_COUNT and all(raw_lines),
        f"course-capsules-v1.jsonl is not exactly {EXPECTED_COURSE_COUNT} nonblank rows",
    )
    rows: list[dict[str, Any]] = []
    for number, raw in enumerate(raw_lines, 1):
        value = _strict_json_value(raw, f"course-capsules-v1.jsonl row {number}")
        _require(isinstance(value, dict), f"course-capsules-v1.jsonl row {number} is not an object")
        try:
            canonical = json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        except (TypeError, ValueError, UnicodeEncodeError) as exc:
            raise RuntimeError(
                f"course-capsules-v1.jsonl row {number} cannot be represented canonically"
            ) from exc
        _require(
            raw == canonical,
            f"course-capsules-v1.jsonl row {number} is not canonical compact JSON",
        )
        rows.append(value)

    course_ids = [row.get("course_id") for row in rows]
    _require(
        all(
            isinstance(course_id, str)
            and COURSE_ID_PATTERN.fullmatch(course_id) is not None
            for course_id in course_ids
        ),
        "course-capsules-v1.jsonl contains a noncanonical course identity",
    )
    canonical_course_ids = [str(course_id) for course_id in course_ids]
    _require(
        len(set(canonical_course_ids)) == EXPECTED_COURSE_COUNT,
        "course-capsules-v1.jsonl course identities are not unique",
    )
    _require(
        canonical_course_ids
        == sorted(canonical_course_ids, key=_natural_course_id_key),
        "course-capsules-v1.jsonl course identities are not in natural curricular order",
    )
    published_ids: list[str] = []
    production_ids: list[str] = []
    published_doi_record_ids: set[int] = set()
    for row in rows:
        course_id = str(row["course_id"])
        course = row.get("course")
        _require(isinstance(course, dict), f"course capsule lacks course state: {course_id}")
        state = course.get("state")
        _require(state in {"published", "production"}, f"course capsule state differs: {course_id}")
        if state == "published":
            published_ids.append(course_id)
            course_native = row.get("course_native")
            _require(isinstance(course_native, dict), f"published course-native boundary missing: {course_id}")
            doi = course_native.get("zenodo")
            doi_match = PUBLISHED_ZENODO_DOI_PATTERN.fullmatch(doi) if isinstance(doi, str) else None
            _require(
                doi_match is not None,
                f"published course DOI is missing or malformed: {course_id}",
            )
            assert doi_match is not None
            published_doi_record_ids.add(int(doi_match.group(1)))
        else:
            production_ids.append(course_id)

    _require(
        len(published_ids) == EXPECTED_PUBLISHED_ROLE_COUNT,
        f"published role count differs: {len(published_ids)}",
    )
    _require(
        len(production_ids) == EXPECTED_PRODUCTION_ROLE_COUNT
        and tuple(production_ids) == EXPECTED_PRODUCTION_ROLE_IDS,
        f"production role roster differs: {production_ids!r}",
    )
    _require(
        len(published_doi_record_ids) == EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS,
        f"distinct published DOI-record count differs: {len(published_doi_record_ids)}",
    )
    return {
        "course_count": len(rows),
        "published_role_count": len(published_ids),
        "production_role_count": len(production_ids),
        "production_role_ids": production_ids,
        "distinct_published_doi_records": len(published_doi_record_ids),
        "canonical_course_ids": canonical_course_ids,
        "published_role_ids": published_ids,
    }


def _safe_course_capsule_member(name: str) -> None:
    pure = PurePosixPath(name)
    raw_parts = name.split("/")
    _require(
        bool(name)
        and not pure.is_absolute()
        and "\\" not in name
        and bool(raw_parts)
        and all(part not in {"", ".", ".."} for part in raw_parts)
        and ":" not in raw_parts[0]
        and all(ord(character) >= 32 for character in name),
        f"course-capsule ZIP contains an unsafe member: {name!r}",
    )


def _course_capsule_package_closure(
    archive_path: Path,
    flat_jsonl_path: Path,
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Bind the release JSONL to its packaged bytes, manifest, and receipt."""

    _require(
        archive_path.name == COURSE_CAPSULE_ARCHIVE_NAME
        and archive_path.is_file()
        and not archive_path.is_symlink(),
        "course-capsule package is missing, renamed, or symlinked",
    )
    _require(
        flat_jsonl_path.name == COURSE_CAPSULE_JSONL_NAME
        and flat_jsonl_path.is_file()
        and not flat_jsonl_path.is_symlink(),
        "flat course-capsule JSONL is missing, renamed, or symlinked",
    )
    flat_data = flat_jsonl_path.read_bytes()
    flat_identity = {
        "bytes": len(flat_data),
        "sha256": hashlib.sha256(flat_data).hexdigest(),
    }
    archive_bytes, archive_sha256 = _identity(archive_path)
    required_members = {
        COURSE_CAPSULE_JSONL_MEMBER,
        COURSE_CAPSULE_PUBLIC_JSONL_MEMBER,
        COURSE_CAPSULE_MANIFEST_MEMBER,
        COURSE_CAPSULE_PUBLIC_MANIFEST_MEMBER,
        COURSE_CAPSULE_RECEIPT_MEMBER,
        COURSE_CAPSULE_PUBLIC_RECEIPT_MEMBER,
    }

    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            infos = archive.infolist()
            _require(bool(infos), "course-capsule ZIP is empty")
            _require(
                all(not info.is_dir() for info in infos),
                "course-capsule ZIP contains directory entries",
            )
            names = [info.filename for info in infos]
            _require(len(names) == len(set(names)), "course-capsule ZIP member names are not unique")
            _require(
                len({name.casefold() for name in names}) == len(names),
                "course-capsule ZIP member names collide under case folding",
            )
            _require(names == sorted(names), "course-capsule ZIP member order is not deterministic")
            _require(required_members <= set(names), "course-capsule ZIP closure members are missing")
            for info in infos:
                _safe_course_capsule_member(info.filename)
                unix_mode = (info.external_attr >> 16) & 0xFFFF
                _require(
                    (unix_mode & 0o170000) != 0o120000,
                    f"course-capsule ZIP contains a symlink: {info.filename}",
                )
                _require(
                    info.flag_bits & 0x1 == 0,
                    f"course-capsule ZIP contains an encrypted member: {info.filename}",
                )
                _require(
                    info.compress_type in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED},
                    f"course-capsule ZIP compression differs: {info.filename}",
                )
                _require(
                    info.date_time == (1980, 1, 1, 0, 0, 0),
                    f"course-capsule ZIP timestamp differs: {info.filename}",
                )
            failed_member = archive.testzip()
            _require(failed_member is None, f"course-capsule ZIP CRC failure: {failed_member}")

            packaged_jsonl = archive.read(COURSE_CAPSULE_JSONL_MEMBER)
            public_jsonl = archive.read(COURSE_CAPSULE_PUBLIC_JSONL_MEMBER)
            _require(
                packaged_jsonl == flat_data and public_jsonl == flat_data,
                "flat/packaged/public course-capsule JSONL bytes differ",
            )

            manifest_data = archive.read(COURSE_CAPSULE_MANIFEST_MEMBER)
            _require(
                archive.read(COURSE_CAPSULE_PUBLIC_MANIFEST_MEMBER) == manifest_data,
                "packaged/public course-capsule manifest bytes differ",
            )
            manifest = _canonical_json_object(manifest_data, "packaged course-capsule manifest")
            _require(
                manifest.get("schema_id") == "interlanguage/open-course-capsule-manifest/v1"
                and manifest.get("schema_version") == "1.0.0",
                "packaged course-capsule manifest identity differs",
            )
            expected_manifest_output = {
                "bytes": flat_identity["bytes"],
                "path": "generated/course-capsules.jsonl",
                "sha256": flat_identity["sha256"],
            }
            _require(
                _same_canonical_json_value(manifest.get("output"), expected_manifest_output),
                "packaged course-capsule manifest does not bind the flat JSONL",
            )
            manifest_summary = manifest.get("summary")
            _require(isinstance(manifest_summary, dict), "packaged course-capsule manifest summary is missing")
            for key, expected in {
                "course_count": snapshot["course_count"],
                "published_count": snapshot["published_role_count"],
                "production_count": snapshot["production_role_count"],
                "verified_semantic_adapter_count": len(ADAPTER_BOUND_ROLES),
            }.items():
                observed = manifest_summary.get(key)
                _require(
                    type(observed) is type(expected) and observed == expected,
                    f"packaged course-capsule manifest summary differs: {key}",
                )

            receipt_data = archive.read(COURSE_CAPSULE_RECEIPT_MEMBER)
            _require(
                archive.read(COURSE_CAPSULE_PUBLIC_RECEIPT_MEMBER) == receipt_data,
                "packaged/public course-capsule validation-receipt bytes differ",
            )
            validation_receipt = _canonical_json_object(
                receipt_data,
                "packaged course-capsule validation receipt",
            )
            _require(
                validation_receipt.get("schema_id")
                == "interlanguage/open-course-capsule-validation-receipt/v1"
                and validation_receipt.get("schema_version") == "1.0.0"
                and validation_receipt.get("state") == "pass",
                "packaged course-capsule validation receipt identity/state differs",
            )
            artifacts = validation_receipt.get("artifacts")
            _require(isinstance(artifacts, dict), "packaged validation-receipt artifacts are missing")
            _require(
                _same_canonical_json_value(
                    artifacts.get("course_capsules_jsonl"),
                    expected_manifest_output,
                ),
                "packaged validation receipt does not bind the flat JSONL",
            )
            expected_manifest_identity = {
                "bytes": len(manifest_data),
                "path": "generated/manifest.json",
                "sha256": hashlib.sha256(manifest_data).hexdigest(),
            }
            _require(
                _same_canonical_json_value(
                    artifacts.get("manifest_json"),
                    expected_manifest_identity,
                ),
                "packaged validation receipt does not bind the embedded manifest",
            )
            checks = validation_receipt.get("checks")
            _require(isinstance(checks, dict), "packaged validation-receipt checks are missing")
            for key, expected in {
                "canonical_jsonl": "pass",
                "unique_course_ids": snapshot["course_count"],
                "published_count": snapshot["published_role_count"],
                "production_count": snapshot["production_role_count"],
                "schema_instances": snapshot["course_count"],
            }.items():
                observed = checks.get(key)
                _require(
                    type(observed) is type(expected) and observed == expected,
                    f"packaged validation-receipt check differs: {key}",
                )
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise RuntimeError("course-capsule ZIP could not be validated") from exc

    return {
        "archive_name": COURSE_CAPSULE_ARCHIVE_NAME,
        "archive_bytes": archive_bytes,
        "archive_sha256": archive_sha256,
        "member_count": len(infos),
        "crc_validation": "pass",
        "flat_jsonl_bytes": flat_identity["bytes"],
        "flat_jsonl_sha256": flat_identity["sha256"],
        "packaged_and_public_jsonl_exact": True,
        "manifest_output_identity_exact": True,
        "validation_receipt_artifact_identities_exact": True,
        "snapshot_counts_cross_bound": True,
    }


def _local_authority() -> tuple[
    list[dict[str, Any]],
    dict[str, Path],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    """Read and cross-check the complete local release authority."""

    _require(_identity(TEMPLATE_SCRIPT) == EXPECTED_TEMPLATE, "v0.62.12 publisher identity differs")
    _require(
        _identity(PREDECESSOR_RECEIPT) == EXPECTED_PREDECESSOR_RECEIPT,
        "v0.62.12 predecessor receipt identity differs",
    )
    _require(RELEASE_DIR.is_dir() and not RELEASE_DIR.is_symlink(), "v0.62.13 release directory is missing or symlinked")
    _require(GITHUB_RECEIPT.is_file(), "GitHub v0.62.13 publication receipt is missing")

    entries = list(RELEASE_DIR.iterdir())
    _require(len(entries) == EXPECTED_FILES, "local release is not exactly 100 entries")
    _require(
        all(path.is_file() and not path.is_symlink() for path in entries),
        "local release is not exactly 100 flat regular nonsymlink files",
    )
    paths = {path.name: path for path in entries}
    _require(len(paths) == EXPECTED_FILES, "local release filenames are not unique")
    _require(
        {COURSE_CAPSULE_JSONL_NAME, COURSE_CAPSULE_ARCHIVE_NAME} <= set(paths),
        "course-capsule flat JSONL/package pair is absent from the release",
    )
    snapshot = _course_snapshot(paths[COURSE_CAPSULE_JSONL_NAME])
    package_closure = _course_capsule_package_closure(
        paths[COURSE_CAPSULE_ARCHIVE_NAME],
        paths[COURSE_CAPSULE_JSONL_NAME],
        snapshot,
    )

    rows: list[dict[str, Any]] = []
    for name in sorted(paths):
        data = paths[name].read_bytes()
        rows.append(
            {
                "name": name,
                "bytes": len(data),
                "md5": hashlib.md5(data, usedforsecurity=False).hexdigest(),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    local = {str(row["name"]): row for row in rows}

    checksums = _checksum_rows()
    _require(
        set(checksums) == set(paths) - {CHECKSUM_FILE.name},
        "checksum manifest coverage differs from the 100-file release",
    )
    for name, digest in checksums.items():
        _require(local[name]["sha256"] == digest, f"checksum manifest differs: {name}")

    predecessor = _load_json(PREDECESSOR_RECEIPT, "v0.62.12 predecessor receipt")
    predecessor_zenodo = predecessor.get("zenodo", {})
    _require(predecessor.get("version") == PREDECESSOR_VERSION, "predecessor receipt version differs")
    _require(
        isinstance(predecessor_zenodo, dict)
        and int(predecessor_zenodo.get("record_id", -1)) == PREDECESSOR_ID,
        "predecessor receipt record differs",
    )
    _require(
        int(predecessor_zenodo.get("concept_record_id", -1)) == CONCEPT_ID
        and predecessor_zenodo.get("concept_doi") == f"10.5281/zenodo.{CONCEPT_ID}",
        "predecessor receipt concept differs",
    )
    _require(predecessor_zenodo.get("access_right") == "open", "predecessor receipt is not open")
    _require(int(predecessor_zenodo.get("file_count", -1)) == EXPECTED_FILES, "predecessor count differs")
    _require(
        predecessor.get("payload_inventory_aggregate_sha256") == EXPECTED_PREDECESSOR_AGGREGATE,
        "predecessor aggregate differs",
    )
    lineage = predecessor.get("lineage_verification", {})
    _require(
        isinstance(lineage, dict) and int(lineage.get("successor_version_index", -1)) == PREDECESSOR_INDEX,
        "predecessor lineage index differs",
    )
    predecessor_rows = predecessor.get("payload_inventory")
    _require(
        isinstance(predecessor_rows, list) and len(predecessor_rows) == EXPECTED_FILES,
        "predecessor receipt is not exactly 100 files",
    )
    predecessor_by_name: dict[str, dict[str, Any]] = {}
    for row in predecessor_rows:
        _require(isinstance(row, dict), "predecessor receipt contains a malformed file row")
        name = str(row.get("name", ""))
        _require(bool(name) and name not in predecessor_by_name, "predecessor filenames are not unique")
        _require(
            isinstance(row.get("bytes"), int) and int(row["bytes"]) >= 0,
            f"predecessor size is malformed: {name}",
        )
        _require(
            re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256", ""))) is not None,
            f"predecessor SHA-256 is malformed: {name}",
        )
        _require(
            re.fullmatch(r"[0-9a-f]{32}", str(row.get("md5", ""))) is not None,
            f"predecessor MD5 is malformed: {name}",
        )
        predecessor_by_name[name] = row
    _require(
        _inventory_sha(list(predecessor_by_name.values())) == EXPECTED_PREDECESSOR_AGGREGATE,
        "predecessor payload rows do not reproduce their aggregate",
    )

    predecessor_names = set(predecessor_by_name)
    local_names = set(local)
    changed_same_name = {
        name
        for name in predecessor_names & local_names
        if int(predecessor_by_name[name]["bytes"]) != int(local[name]["bytes"])
        or predecessor_by_name[name]["sha256"] != local[name]["sha256"]
    }
    omitted = (predecessor_names - local_names) | changed_same_name
    additions = (local_names - predecessor_names) | changed_same_name
    retained = (predecessor_names & local_names) - changed_same_name
    _require(omitted == OMITTED, "v0.62.13 omission set differs")
    _require(additions == ADDITIONS, "v0.62.13 addition set differs")
    _require(
        changed_same_name == SAME_NAME_REPLACEMENTS,
        "v0.62.13 same-name replacement set differs",
    )
    _require(
        (
            len(retained),
            len(changed_same_name),
            len(predecessor_names - local_names),
            len(local_names - predecessor_names),
            len(omitted),
            len(additions),
        )
        == (
            EXPECTED_RETAINED,
            EXPECTED_SAME_NAME_REPLACEMENTS,
            EXPECTED_PURE_OMISSIONS,
            EXPECTED_PURE_ADDITIONS,
            EXPECTED_EFFECTIVE_OMISSIONS,
            EXPECTED_EFFECTIVE_ADDITIONS,
        ),
        "v0.62.13 78-retained/9-replaced/13-pure-new boundary differs",
    )
    for name in retained:
        before = predecessor_by_name[name]
        after = local[name]
        _require(int(before["bytes"]) == int(after["bytes"]), f"retained size differs: {name}")
        _require(before["sha256"] == after["sha256"], f"retained SHA-256 differs: {name}")
    aggregate = _inventory_sha(rows)
    _require(aggregate != EXPECTED_PREDECESSOR_AGGREGATE, "successor aggregate duplicates v0.62.12")

    github = _load_json(GITHUB_RECEIPT, "GitHub v0.62.13 publication receipt")
    _assert_sanitized_receipt(github, "github_receipt")
    _require(github.get("state") == "published_public_verified", "GitHub release is not public verified")
    _require(github.get("tag") == "v0.62.13", "GitHub release tag differs")
    github_source = github.get("source")
    _require(isinstance(github_source, dict), "GitHub receipt source authority is malformed")
    github_commit = github_source.get("commit")
    github_tree = github_source.get("tree")
    _require(
        isinstance(github_commit, str)
        and re.fullmatch(r"[0-9a-f]{40}", github_commit) is not None,
        "GitHub receipt source.commit is not a full lowercase commit SHA",
    )
    _require(
        isinstance(github_tree, str)
        and re.fullmatch(r"[0-9a-f]{40}", github_tree) is not None,
        "GitHub receipt source.tree is not a full lowercase tree SHA",
    )
    _require(
        github_source.get("tag_resolves_to_commit") is True,
        "GitHub receipt does not prove that the release tag resolves to source.commit",
    )
    _require(
        github.get("release", {}).get("url")
        == "https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.13",
        "GitHub release URL differs",
    )
    readback = github.get("anonymous_asset_readback", {})
    _require(isinstance(readback, dict), "GitHub anonymous readback is malformed")
    _require(readback.get("result") == "pass_100_of_100", "GitHub anonymous readback differs")
    github_rows = readback.get("entries")
    _require(isinstance(github_rows, list) and len(github_rows) == EXPECTED_FILES, "GitHub inventory count differs")
    github_by_name: dict[str, dict[str, Any]] = {}
    for row in github_rows:
        _require(isinstance(row, dict), "GitHub receipt contains a malformed asset row")
        name = str(row.get("name", ""))
        _require(bool(name) and name not in github_by_name, "GitHub receipt asset names are not unique")
        github_by_name[name] = row
    _require(set(github_by_name) == local_names, "GitHub/local filename sets differ")
    for name, row in local.items():
        remote = github_by_name[name]
        _require(int(remote.get("bytes", -1)) == int(row["bytes"]), f"GitHub size differs: {name}")
        _require(remote.get("sha256") == row["sha256"], f"GitHub SHA-256 differs: {name}")
    github_inventory = github.get("inventory", {})
    _require(isinstance(github_inventory, dict), "GitHub inventory summary is malformed")
    _require(int(github_inventory.get("files", -1)) == EXPECTED_FILES, "GitHub inventory file count differs")
    _require(
        int(github_inventory.get("bytes", -1)) == sum(int(row["bytes"]) for row in rows),
        "GitHub inventory byte total differs",
    )
    _require(github_inventory.get("aggregate_sha256") == aggregate, "GitHub inventory aggregate differs")
    github_boundary = github.get("replacement_boundary")
    _require(isinstance(github_boundary, dict), "GitHub replacement boundary is malformed")
    _require(
        _same_canonical_json_value(github_boundary.get("course_snapshot"), snapshot),
        "GitHub receipt course snapshot differs from release JSONL",
    )

    return rows, paths, github, predecessor, snapshot, package_closure


def _standalone_preflight() -> dict[str, Any]:
    _assert_constant_self_consistency()
    rows, _, github, _, snapshot, package_closure = _local_authority()
    return {
        "status": "PASS_LOCAL_PREFLIGHT_NO_IMPORT_NO_NETWORK_NO_CREDENTIAL_NO_WRITE",
        "version": VERSION,
        "concept_doi": f"10.5281/zenodo.{CONCEPT_ID}",
        "predecessor_record_id": PREDECESSOR_ID,
        "predecessor_version_index": PREDECESSOR_INDEX,
        "expected_successor_version_index": SUCCESSOR_INDEX,
        "files": len(rows),
        "bytes": sum(int(row["bytes"]) for row in rows),
        "aggregate_sha256": _inventory_sha(rows),
        "retained_exact_files": EXPECTED_RETAINED,
        "same_name_replacements": EXPECTED_SAME_NAME_REPLACEMENTS,
        "pure_omissions": EXPECTED_PURE_OMISSIONS,
        "pure_additions": EXPECTED_PURE_ADDITIONS,
        "effective_draft_omissions": EXPECTED_EFFECTIVE_OMISSIONS,
        "effective_draft_additions": EXPECTED_EFFECTIVE_ADDITIONS,
        "github_source_commit": github["source"]["commit"],
        "github_source_tree": github["source"]["tree"],
        "course_snapshot": snapshot,
        "implementation_families_compared": IMPLEMENTATION_FAMILY_COUNT,
        "adapter_bound_roles": list(ADAPTER_BOUND_ROLES),
        "native_roles_retained_without_adapter_claim": NATIVE_ONLY_ROLE_COUNT,
        "course_capsule_package_closure": package_closure,
        "receipt_targets": [VERSION_RECEIPT.name, ROOT_RECEIPT.name],
        "template_identity_verified": TEMPLATE_SCRIPT.name,
    }


# This branch must remain above every dynamic import.  It is deliberately
# exact-argv so an unsupported option cannot accidentally be treated as a
# successful preflight.
if __name__ == "__main__" and sys.argv[1:] == ["--preflight"]:
    try:
        print(json.dumps(_standalone_preflight(), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    except Exception as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(f"FAIL: {type(exc).__name__}: {detail}", file=sys.stderr)
        raise SystemExit(1)
    raise SystemExit(0)

if __name__ == "__main__" and "--preflight" in sys.argv[1:]:
    print("FAIL: --preflight accepts no additional arguments", file=sys.stderr)
    raise SystemExit(2)


_assert_constant_self_consistency()
_template_bytes = TEMPLATE_SCRIPT.read_bytes()
_require(
    (len(_template_bytes), hashlib.sha256(_template_bytes).hexdigest()) == EXPECTED_TEMPLATE,
    "v0.62.12 publisher identity differs",
)
previous = types.ModuleType("pmi_v06212_zenodo_template")
previous.__file__ = str(TEMPLATE_SCRIPT)
previous.__package__ = ""
exec(compile(_template_bytes, str(TEMPLATE_SCRIPT), "exec"), previous.__dict__)
base = previous.base


TOKEN_FILE_ENV = "PMI_V06213_ZENODO_TOKEN_FILE"
LEARNER_FILE = "peta-belajar-luring.html"
LEARNER_SITE = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
BACKEND_CENTER = "https://kokunoyumeto.github.io/program-matematika-indonesia/backend/"
PUBLIC_BASELINE_URL = (
    "https://kokunoyumeto.github.io/program-matematika-indonesia/"
    "data/course-capsule-v1/public-baseline-v0.62.12.json"
)
GITHUB_RELEASE = (
    "https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.13"
)
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
USER_AGENT = "Codex-PMI-v06213-Zenodo-Publisher/1.0"

TITLE = "Program Matematika Indonesia v0.62.13 — Backend Modular untuk Siswa dan Pendidik"


def _indonesian_roster(values: list[str] | tuple[str, ...]) -> str:
    _require(len(values) >= 2, "metadata roster is too short")
    return ", ".join(values[:-1]) + ", dan " + values[-1]


def _snapshot_metadata_text(snapshot: dict[str, Any]) -> tuple[str, str]:
    """Render every quantitative metadata claim from validated evidence/constants."""

    _require(snapshot.get("course_count") == EXPECTED_COURSE_COUNT, "metadata course count differs")
    _require(
        snapshot.get("published_role_count") == EXPECTED_PUBLISHED_ROLE_COUNT,
        "metadata published-role count differs",
    )
    _require(
        snapshot.get("production_role_count") == EXPECTED_PRODUCTION_ROLE_COUNT
        and tuple(snapshot.get("production_role_ids", [])) == EXPECTED_PRODUCTION_ROLE_IDS,
        "metadata production-role snapshot differs",
    )
    _require(
        snapshot.get("distinct_published_doi_records")
        == EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS,
        "metadata published DOI-record count differs",
    )
    production_role_text = _indonesian_roster(list(EXPECTED_PRODUCTION_ROLE_IDS))
    adapter_role_text = _indonesian_roster(list(ADAPTER_BOUND_ROLES))
    description = (
        f'<p><strong>Mulai belajar:</strong> <a href="{LEARNER_SITE}">'
        "buka Program Matematika Indonesia</a>. Halaman berbahasa Indonesia ini adalah pintu utama untuk menelusuri "
        "mata kuliah, prasyarat, bahan baca, mode luring, dan sumber yang telah dipublikasikan. HTML yang dapat dibaca "
        "siswa adalah permukaan utama; JSON backend disediakan sebagai lapisan mesin sekunder, bukan sebagai pintu masuk siswa.</p>"
        f'<p><strong>Backend modular:</strong> <a href="{BACKEND_CENTER}">'
        f"buka pusat backend siswa dan pendidik</a>. {snapshot['course_count']} kapsul kursus memaparkan tujuh lapisan "
        "secara jujur: kurikulum; penerjemahan, asal-usul, dan hak; produksi dan rilis; pengantaran dan aksesibilitas "
        "siswa; dukungan pendidik; federasi tanpa penyalinan; serta interoperabilitas dan adapter.</p>"
        f"<p><strong>Metode pengembangan:</strong> {snapshot['course_count']} jalur kerja kursus mula-mula membangun "
        "terjemahan dan backend native masing-masing tanpa dipaksa memakai satu format global. Audit komparatif selama "
        f"dan sesudah produksi lalu membandingkan {IMPLEMENTATION_FAMILY_COUNT} keluarga implementasi, mengambil pola "
        "yang benar-benar dapat diintegrasikan, dan menambahkan kapsul atau adapter tipis. Hasilnya bukan penyeragaman "
        "yang menghapus karya asli: backend native, identitas unit, hak, dan format setiap kursus tetap menjadi otoritas "
        "kanonik.</p>"
        "<p>Arsitektur v0.62.13 bersifat tipis, netral-format, dan tanpa penyalinan korpus. Kapsul JSONL, kebijakan "
        "desain, navigasi siswa, bukti pendidik, dan adapter terverifikasi menjadi lapisan integrasi. Format MyST, "
        "Quarto, XLIFF, MathML, dan keluaran lain hanya digunakan bila ada konsumen konkret dan tidak diwajibkan sebagai "
        "format sumber global.</p>"
        f"<p>Batas bukti saat rilis adalah {len(ADAPTER_BOUND_ROLES)} adapter terverifikasi: {adapter_role_text}. "
        f"{NATIVE_ONLY_ROLE_COUNT} peran lain mempertahankan backend native tanpa klaim adapter. D30 menyediakan bukti "
        f"kapsul kursus serta pengantaran siswa daring/luring, bukan adapter. Status snapshot adalah "
        f"{snapshot['published_role_count']} peran dipublikasikan dan {snapshot['production_role_count']} masih "
        f"berproduksi ({production_role_text}); edisi terbit itu memakai "
        f"{snapshot['distinct_published_doi_records']} rekaman DOI berbeda, dan program penerjemahan keseluruhan belum "
        "lengkap.</p>"
        f'<p>Rilis GitHub yang identik tersedia pada <a href="{GITHUB_RELEASE}">GitHub v0.62.13</a>. Payload memuat '
        f"tepat {EXPECTED_FILES} berkas: {EXPECTED_RETAINED} berkas v0.62.12 dipertahankan byte demi byte, "
        f"{EXPECTED_SAME_NAME_REPLACEMENTS} nama diganti dengan versi penerus, {EXPECTED_PURE_OMISSIONS} nama lama "
        f"hanya tetap pada record pendahulu yang masih terbuka, dan {EXPECTED_PURE_ADDITIONS} nama baru ditambahkan. "
        "Record pendahulu tidak diubah, dihapus, ditutup, atau dibatasi.</p>"
        "<p>Hak, lisensi, dan kredit tiap komponen dipertahankan. Paket gabungan menggunakan lisensi "
        "<em>other-open</em> karena tidak mempunyai satu lisensi tunggal. Produksi, integrasi, dan QA dibantu oleh "
        f"<strong>{MODEL}</strong> atas instruksi pengguna.</p>"
    )
    notes = (
        f"v0.62.13 mendokumentasikan metode native-first pada {snapshot['course_count']} jalur: "
        f"{IMPLEMENTATION_FAMILY_COUNT} keluarga implementasi dibandingkan, lalu kekuatan yang dapat diintegrasikan "
        f"diwujudkan sebagai kapsul dan adapter tipis tanpa mengganti otoritas native. {len(ADAPTER_BOUND_ROLES)} "
        f"adapter terverifikasi adalah {adapter_role_text}; {NATIVE_ONLY_ROLE_COUNT} peran tetap native-only, sedangkan "
        f"D30 adalah bukti kapsul/pengantaran siswa, bukan adapter. Snapshot berisi "
        f"{snapshot['published_role_count']} peran dipublikasikan dan {snapshot['production_role_count']} masih "
        f"berproduksi ({production_role_text}), melalui {snapshot['distinct_published_doi_records']} rekaman DOI edisi "
        "terbit berbeda. HTML siswa didahulukan; JSON adalah backend mesin sekunder."
    )
    return description, notes


_EXPECTED_METADATA_SNAPSHOT = {
    "course_count": EXPECTED_COURSE_COUNT,
    "published_role_count": EXPECTED_PUBLISHED_ROLE_COUNT,
    "production_role_count": EXPECTED_PRODUCTION_ROLE_COUNT,
    "production_role_ids": list(EXPECTED_PRODUCTION_ROLE_IDS),
    "distinct_published_doi_records": EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS,
}
DESCRIPTION, NOTES = _snapshot_metadata_text(_EXPECTED_METADATA_SNAPSHOT)


def _bind_snapshot_metadata(snapshot: dict[str, Any]) -> None:
    global DESCRIPTION, NOTES
    DESCRIPTION, NOTES = _snapshot_metadata_text(snapshot)
    for module in (previous, previous.previous, previous.previous.template, base):
        module.DESCRIPTION = DESCRIPTION
        module.NOTES = NOTES

PREDECESSOR_RELATION_INDEX: int | None = None


_ANONYMOUS_LOCAL = threading.local()
_ANONYMOUS_EXACT_HOSTS = {
    "doi.org",
    "github.com",
    "kokunoyumeto.github.io",
    "objects.githubusercontent.com",
    "raw.githubusercontent.com",
    "release-assets.githubusercontent.com",
    "www.zenodo.org",
    "zenodo.org",
}
_ANONYMOUS_HOST_SUFFIXES = (".amazonaws.com", ".githubusercontent.com", ".zenodo.org")


def _anonymous_session():
    session = getattr(_ANONYMOUS_LOCAL, "session", None)
    if session is None:
        session = base.requests.Session()
        session.trust_env = False
        session.auth = None
        session.cookies.clear()
        session.headers.clear()
        session.headers.update({"User-Agent": "Codex-PMI-v06213-Anonymous-Readback/1.0"})
        _ANONYMOUS_LOCAL.session = session
    return session


def _validated_anonymous_url(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    base.require(parsed.scheme == "https", "anonymous URL is not HTTPS")
    base.require(bool(host), "anonymous URL has no host")
    base.require(parsed.username is None and parsed.password is None, "anonymous URL contains userinfo")
    base.require(parsed.port in (None, 443), "anonymous URL uses a non-HTTPS port")
    base.require(
        host in _ANONYMOUS_EXACT_HOSTS or any(host.endswith(suffix) for suffix in _ANONYMOUS_HOST_SUFFIXES),
        f"anonymous URL host is outside the public allowlist: {host}",
    )
    return url


def _strict_anonymous_get(
    url: str,
    *,
    stream: bool,
    timeout: int,
    headers: dict[str, str] | None = None,
):
    request_headers = dict(headers or {})
    base.require(
        all(key.lower() not in {"authorization", "cookie", "proxy-authorization"} for key in request_headers),
        "credential-bearing header is forbidden on anonymous transport",
    )
    session = _anonymous_session()
    current = _validated_anonymous_url(url)
    for redirect_count in range(6):
        last_status = 0
        response = None
        for attempt in range(5):
            session.cookies.clear()
            response = session.get(
                current,
                stream=stream,
                timeout=(20, timeout),
                allow_redirects=False,
                headers=request_headers,
            )
            session.cookies.clear()
            last_status = response.status_code
            if response.status_code not in (429, 500, 502, 503, 504):
                break
            response.close()
            response = None
            base.time.sleep(2 * (attempt + 1))
        if response is None:
            raise RuntimeError(f"anonymous public retry budget exhausted after HTTP {last_status}")
        if response.status_code in (301, 302, 303, 307, 308):
            location = response.headers.get("Location")
            response.close()
            base.require(isinstance(location, str) and bool(location), "anonymous redirect has no location")
            current = _validated_anonymous_url(urljoin(current, location))
            continue
        _validated_anonymous_url(response.url)
        return response
    raise RuntimeError("anonymous public redirect budget exhausted")


def strict_anonymous_public_get(url: str, *, stream: bool = False, timeout: int = 180):
    return _strict_anonymous_get(url, stream=stream, timeout=timeout)


def strict_anonymous_public_rdm_json(record_id: int) -> dict[str, Any]:
    response = _strict_anonymous_get(
        f"{base.PUBLIC_API}/{record_id}",
        stream=False,
        timeout=180,
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    base.require(response.status_code == 200, f"public InvenioRDM record returned HTTP {response.status_code}")
    value = response.json()
    base.require(isinstance(value, dict), "public InvenioRDM response is not an object")
    base.require(str(value.get("id")) == str(record_id), "public InvenioRDM record ID differs")
    return value


base.public_get = strict_anonymous_public_get
base.public_rdm_json = strict_anonymous_public_rdm_json


for module in (previous, previous.previous, previous.previous.template, base):
    for name, value in {
        "RELEASE_DIR": RELEASE_DIR,
        "GITHUB_RECEIPT": GITHUB_RECEIPT,
        "PREDECESSOR_RECEIPT": PREDECESSOR_RECEIPT,
        "VERSION_RECEIPT": VERSION_RECEIPT,
        "ROOT_RECEIPT": ROOT_RECEIPT,
        "TOKEN_FILE_ENV": TOKEN_FILE_ENV,
        "CONCEPT_ID": CONCEPT_ID,
        "PREDECESSOR_ID": PREDECESSOR_ID,
        "PREDECESSOR_VERSION": PREDECESSOR_VERSION,
        "VERSION": VERSION,
        "LEARNER_FILE": LEARNER_FILE,
        "LEARNER_SITE": LEARNER_SITE,
        "GITHUB_RELEASE": GITHUB_RELEASE,
        "MODEL": MODEL,
        "USER_AGENT": USER_AGENT,
        "TITLE": TITLE,
        "DESCRIPTION": DESCRIPTION,
        "NOTES": NOTES,
        "OMITTED": OMITTED,
        "ADDITIONS": ADDITIONS,
    }.items():
        setattr(module, name, value)


ORIGINAL_PUBLIC_FILE_STUBS = previous.original_public_file_stubs


def file_identity(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), base.sha256_bytes(data)


def local_inventory() -> tuple[list[dict[str, Any]], dict[str, Path], dict[str, Any], dict[str, Any]]:
    plain_rows, paths, github, _, snapshot, package_closure = _local_authority()
    rows: list[dict[str, Any]] = []
    for row in plain_rows:
        path = paths[str(row["name"])]
        rows.append(
            {
                "name": row["name"],
                "path": path,
                "bytes": row["bytes"],
                "md5": row["md5"],
                "sha256": row["sha256"],
            }
        )
    return (
        rows,
        paths,
        {
            "version": VERSION,
            "inventory": [{key: row[key] for key in ("name", "bytes", "sha256")} for row in rows],
            "inventory_aggregate_sha256": base.inventory_sha(rows),
            "course_snapshot": snapshot,
            "course_capsule_package_closure": package_closure,
        },
        github,
    )


def predecessor_authority(
    local_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    global PREDECESSOR_RELATION_INDEX
    base.require(
        file_identity(PREDECESSOR_RECEIPT) == EXPECTED_PREDECESSOR_RECEIPT,
        "predecessor receipt identity differs",
    )
    record = base.public_json(f"{base.PUBLIC_API}/{PREDECESSOR_ID}")
    base.require(int(record.get("id", -1)) == PREDECESSOR_ID, "predecessor record ID differs")
    base.require(record.get("conceptdoi") == f"10.5281/zenodo.{CONCEPT_ID}", "predecessor concept differs")
    metadata = record.get("metadata", {})
    base.require(isinstance(metadata, dict), "predecessor metadata is malformed")
    base.require(metadata.get("version") == PREDECESSOR_VERSION, "predecessor version differs")
    base.require(metadata.get("access_right") == "open", "predecessor is not open")
    base.require(base.license_id(metadata) == "other-open", "predecessor license differs")
    base.require(metadata.get("language") == "ind", "predecessor language differs")
    relation = base.version_relation(metadata)
    base.require(int(relation["index"]) == PREDECESSOR_INDEX, "predecessor version index differs")
    PREDECESSOR_RELATION_INDEX = int(relation["index"])

    receipt = _load_json(PREDECESSOR_RECEIPT, "predecessor receipt")
    receipt_rows = receipt.get("payload_inventory")
    base.require(
        isinstance(receipt_rows, list) and len(receipt_rows) == EXPECTED_FILES,
        "predecessor receipt inventory differs",
    )
    expected = [
        {
            "name": str(row["name"]),
            "bytes": int(row["bytes"]),
            "sha256": str(row["sha256"]),
            "md5": str(row["md5"]),
        }
        for row in receipt_rows
    ]
    stubs = {
        str(row["name"]): row
        for row in ORIGINAL_PUBLIC_FILE_STUBS(record, EXPECTED_FILES, "predecessor-stubs")
    }
    base.require(set(stubs) == {str(row["name"]) for row in expected}, "predecessor public names differ")
    for row in expected:
        stub = stubs[str(row["name"])]
        base.require(int(stub["bytes"]) == int(row["bytes"]), f"predecessor size differs: {row['name']}")
        base.require(stub["md5"] == row["md5"], f"predecessor MD5 differs: {row['name']}")
    observed = base.anonymous_inventory(record, expected, "predecessor-before")
    base.require(
        base.inventory_sha(observed) == EXPECTED_PREDECESSOR_AGGREGATE,
        "predecessor anonymous aggregate differs",
    )
    expected_by_name = {str(row["name"]): row for row in expected}
    local_by_name = {str(row["name"]): row for row in local_rows}
    changed_same_name = {
        name
        for name in set(expected_by_name) & set(local_by_name)
        if int(expected_by_name[name]["bytes"]) != int(local_by_name[name]["bytes"])
        or expected_by_name[name]["sha256"] != local_by_name[name]["sha256"]
    }
    effective_omissions = (set(expected_by_name) - set(local_by_name)) | changed_same_name
    base.require(effective_omissions == OMITTED, "predecessor/local omission boundary differs")
    return record, metadata, observed


def related_identifiers(predecessor_metadata: dict[str, Any]) -> list[dict[str, str]]:
    result = [
        {"identifier": LEARNER_SITE, "relation": "isSupplementTo", "scheme": "url"},
        {"identifier": BACKEND_CENTER, "relation": "isSupplementTo", "scheme": "url"},
        {"identifier": PUBLIC_BASELINE_URL, "relation": "isSupplementTo", "scheme": "url"},
    ]
    for row in predecessor_metadata.get("related_identifiers", []):
        if not isinstance(row, dict):
            continue
        identifier = str(row.get("identifier", ""))
        if identifier in (LEARNER_SITE, BACKEND_CENTER, PUBLIC_BASELINE_URL):
            continue
        if re.fullmatch(
            r"https://github\.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v[^/]+",
            identifier,
        ):
            continue
        normalized = {
            "identifier": identifier,
            "relation": str(row.get("relation", "")),
            "scheme": str(row.get("scheme", "")),
        }
        if normalized not in result:
            result.append(normalized)
    result.append({"identifier": GITHUB_RELEASE, "relation": "isIdenticalTo", "scheme": "url"})
    return result


def verify_exact_draft(draft: dict[str, Any], local_rows: list[dict[str, Any]]) -> None:
    remote = {str(row["name"]): row for row in base.draft_file_rows(draft)}
    local = {str(row["name"]): row for row in local_rows}
    base.require(
        len(remote) == EXPECTED_FILES and set(remote) == set(local),
        "final draft is not the exact 100-file local inventory",
    )
    for name, expected in local.items():
        base.require(int(remote[name]["bytes"]) == int(expected["bytes"]), f"final draft size differs: {name}")
        base.require(remote[name]["md5"] == expected["md5"], f"final draft MD5 differs: {name}")


def validate_draft_boundary(
    draft: dict[str, Any],
    predecessor_rows: list[dict[str, Any]],
    local_rows: list[dict[str, Any]],
) -> None:
    predecessor = {str(row["name"]): row for row in predecessor_rows}
    local = {str(row["name"]): row for row in local_rows}
    remote = {str(row["name"]): row for row in base.draft_file_rows(draft)}
    retained = set(predecessor) - OMITTED
    allowed = set(predecessor) | ADDITIONS
    base.require(set(remote) <= allowed, "draft contains a file outside the pinned predecessor/addition boundary")
    base.require(set(remote) >= retained, "draft is missing a retained predecessor file")

    for name in set(remote):
        row = remote[name]
        predecessor_match = name in predecessor and (
            int(row["bytes"]) == int(predecessor[name]["bytes"])
            and row["md5"] == predecessor[name]["md5"]
        )
        local_match = name in local and (
            int(row["bytes"]) == int(local[name]["bytes"])
            and row["md5"] == local[name]["md5"]
        )
        if name in SAME_NAME_REPLACEMENTS:
            base.require(
                predecessor_match or local_match,
                f"draft same-name replacement matches neither predecessor nor successor: {name}",
            )
        elif name in PURE_OMISSIONS:
            base.require(predecessor_match, f"draft omission bytes differ from predecessor: {name}")
        elif name in PURE_ADDITIONS:
            base.require(local_match, f"draft addition bytes differ from successor: {name}")
        else:
            base.require(
                predecessor_match and local_match,
                f"draft retained file is not byte-identical across predecessor/successor: {name}",
            )


def delete_omissions(client: Any, draft_id: int) -> int:
    """Delete only obsolete draft bytes, preserving correct resumed replacements."""

    local_rows, _, _, _ = local_inventory()
    local = {str(row["name"]): row for row in local_rows}
    predecessor_receipt = _load_json(PREDECESSOR_RECEIPT, "predecessor receipt")
    predecessor = {
        str(row["name"]): row for row in predecessor_receipt.get("payload_inventory", [])
    }
    base.require(len(predecessor) == EXPECTED_FILES, "predecessor receipt inventory differs")
    deleted = 0
    for name in sorted(OMITTED):
        draft = base.get_draft(client, draft_id)
        by_name = {str(row["name"]): row for row in base.draft_file_rows(draft)}
        if name not in by_name:
            continue
        remote = by_name[name]
        local_match = name in local and (
            int(remote["bytes"]) == int(local[name]["bytes"])
            and remote["md5"] == local[name]["md5"]
        )
        if name in SAME_NAME_REPLACEMENTS and local_match:
            continue
        predecessor_match = name in predecessor and (
            int(remote["bytes"]) == int(predecessor[name]["bytes"])
            and remote["md5"] == predecessor[name]["md5"]
        )
        base.require(predecessor_match, f"draft omission is neither exact predecessor nor exact successor: {name}")
        response = None
        try:
            response = client.delete(
                f"{base.DEPOSIT_API}/{draft_id}/files/{remote['id']}",
                timeout=(20, 180),
                allow_redirects=False,
            )
        except base.requests.RequestException:
            response = None
        refreshed = base.get_draft(client, draft_id)
        base.require(
            name not in {str(row["name"]) for row in base.draft_file_rows(refreshed)},
            f"draft omission was not deleted: {name}",
        )
        if response is not None:
            base.require(
                response.status_code in (204, 404, 429, 500, 502, 503, 504),
                f"Zenodo draft delete returned HTTP {response.status_code}",
            )
        deleted += 1
    return deleted


def verify_final_draft_metadata(draft: dict[str, Any], payload: dict[str, Any]) -> None:
    metadata = draft.get("metadata", {})
    base.require(isinstance(metadata, dict), "final draft metadata is malformed")
    for field, expected in payload.items():
        if field == "license":
            base.require(base.license_id(metadata) == expected, "final draft license differs")
        else:
            base.require(metadata.get(field) == expected, f"final draft metadata differs: {field}")
    base.require(metadata.get("access_right") == "open", "final draft access is not open")
    base.require(isinstance(draft.get("files"), list) and len(draft["files"]) == EXPECTED_FILES, "final draft count differs")


def verify_rdm_learner_preview(value: dict[str, Any]) -> None:
    files = value.get("files", {})
    access = value.get("access", {})
    base.require(isinstance(files, dict) and files.get("enabled") is True, "InvenioRDM files are not enabled")
    base.require(files.get("count") == EXPECTED_FILES, "InvenioRDM file count differs")
    base.require(files.get("default_preview") == LEARNER_FILE, "InvenioRDM default preview differs")
    base.require(isinstance(access, dict), "InvenioRDM access metadata is malformed")
    base.require(access.get("record") == "public" and access.get("files") == "public", "InvenioRDM access is not public")


def _search_total(hits: dict[str, Any]) -> int:
    value = hits.get("total", -1)
    if isinstance(value, dict):
        base.require(value.get("relation") in (None, "eq"), "public lineage total is inexact")
        value = value.get("value", -1)
    return int(value)


def anonymous_lineage_search() -> dict[str, Any]:
    """Search the complete public concept lineage without credentials."""

    query = urlencode(
        {
            "q": f"conceptrecid:{CONCEPT_ID}",
            "all_versions": "true",
            "size": 100,
        }
    )
    search = base.public_json(f"{base.PUBLIC_API}?{query}")
    hits = search.get("hits", {})
    base.require(isinstance(hits, dict), "public lineage search is malformed")
    rows = hits.get("hits")
    base.require(isinstance(rows, list), "public lineage search rows are malformed")
    total = _search_total(hits)
    base.require(0 < total <= 100 and len(rows) == total, "public lineage search is incomplete")

    by_id: dict[int, dict[str, Any]] = {}
    by_index: dict[int, dict[str, Any]] = {}
    for row in rows:
        base.require(isinstance(row, dict), "public lineage contains a malformed record")
        record_id = int(row.get("id", -1))
        base.require(record_id > 0 and record_id not in by_id, "public lineage record IDs are not unique")
        base.require(row.get("conceptdoi") == f"10.5281/zenodo.{CONCEPT_ID}", "public lineage concept differs")
        metadata = row.get("metadata", {})
        base.require(isinstance(metadata, dict), "public lineage metadata is malformed")
        relation = base.version_relation(metadata)
        index = int(relation["index"])
        base.require(index not in by_index, "public lineage version indexes are not unique")
        by_id[record_id] = row
        by_index[index] = row

    latest = base.public_json(f"{base.PUBLIC_API}/{CONCEPT_ID}/versions/latest")
    latest_id = int(latest.get("id", -1))
    base.require(latest_id in by_id, "concept latest is absent from the anonymous lineage search")
    latest_relation = base.version_relation(latest.get("metadata", {}))
    base.require(int(latest_relation["index"]) == max(by_index), "concept latest index differs from search")
    base.require(latest_relation["is_last"] is True, "concept latest flag differs")
    base.require(total == int(latest_relation["index"]), "public lineage total differs from latest index")
    base.require(
        set(by_index) == set(range(1, int(latest_relation["index"]) + 1)),
        "public lineage version-index closure differs",
    )
    search_latest = by_id[latest_id]
    base.require(search_latest.get("doi") == latest.get("doi"), "latest DOI differs between search and direct read")
    base.require(
        search_latest.get("conceptdoi") == latest.get("conceptdoi"),
        "latest concept differs between search and direct read",
    )
    base.require(
        search_latest.get("metadata", {}).get("version") == latest.get("metadata", {}).get("version"),
        "latest version differs between search and direct read",
    )

    targets = [
        row for row in rows if isinstance(row.get("metadata"), dict) and row["metadata"].get("version") == VERSION
    ]
    base.require(len(targets) <= 1, "multiple public v0.62.13 records exist in the concept lineage")
    target = targets[0] if targets else None
    if target is not None:
        relation = base.version_relation(target.get("metadata", {}))
        base.require(int(relation["index"]) == SUCCESSOR_INDEX, "public v0.62.13 is not lineage index 38")
        base.require(relation["is_last"] is True, "public v0.62.13/index-38 is not marked latest")
        base.require(
            int(target.get("id", -1)) == latest_id,
            "public v0.62.13/index-38 is not the concept-latest record",
        )
        base.require(
            int(latest_relation["index"]) == SUCCESSOR_INDEX and total == SUCCESSOR_INDEX,
            "published v0.62.13 does not close the concept lineage at index 38",
        )
    return {
        "latest": latest,
        "target": target,
        "records": rows,
        "record_count": total,
    }


def _draft_index(draft: dict[str, Any], *, client: Any | None = None, draft_id: int | None = None) -> int:
    metadata = draft.get("metadata", {})
    base.require(isinstance(metadata, dict), "draft metadata is malformed")
    candidates: list[int] = []
    relations = metadata.get("relations", {})
    version_rows = relations.get("version", []) if isinstance(relations, dict) else []
    if isinstance(version_rows, list) and len(version_rows) == 1 and isinstance(version_rows[0], dict):
        if isinstance(version_rows[0].get("index"), int):
            candidates.append(int(version_rows[0]["index"]))
    versions = draft.get("versions", {})
    if isinstance(versions, dict) and isinstance(versions.get("index"), int):
        candidates.append(int(versions["index"]))
    if not candidates and client is not None and draft_id is not None:
        rdm = base.rdm_draft(client, draft_id)
        rdm_versions = rdm.get("versions", {})
        if isinstance(rdm_versions, dict) and isinstance(rdm_versions.get("index"), int):
            candidates.append(int(rdm_versions["index"]))
    base.require(bool(candidates), "draft version index is unavailable")
    base.require(len(set(candidates)) == 1, "draft version index evidence conflicts")
    base.require(candidates[0] == SUCCESSOR_INDEX, "draft is not lineage index 38")
    return candidates[0]


def _latest_draft_from_predecessor(client: Any) -> int:
    predecessor = base.auth_get(client, f"{base.DEPOSIT_API}/{PREDECESSOR_ID}")
    base.require(predecessor.status_code == 200, "authenticated predecessor deposition is unavailable")
    value = predecessor.json()
    base.require(int(value.get("id", -1)) == PREDECESSOR_ID, "authenticated predecessor ID differs")
    return base.latest_draft_id(value)


def _load_reservation_cursor() -> dict[str, Any] | None:
    if not RESERVATION_CURSOR.is_file():
        return None
    value = _load_json(RESERVATION_CURSOR, "v0.62.13 reservation cursor")
    canonical = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    base.require(RESERVATION_CURSOR.read_bytes() == canonical, "reservation cursor is not canonical JSON")
    _assert_sanitized_receipt(value, "reservation_cursor")
    base.require(
        set(value)
        == {
            "concept_id",
            "created_at_utc",
            "draft_id",
            "predecessor_id",
            "predecessor_index",
            "record_id",
            "schema_id",
            "state",
            "successor_index",
            "updated_at_utc",
            "version",
        },
        "reservation cursor fields differ",
    )
    base.require(value.get("schema_id") == "program-matematika-indonesia/zenodo-reservation-cursor/1.0.0", "reservation cursor schema differs")
    base.require(value.get("version") == VERSION, "reservation cursor version differs")
    base.require(int(value.get("concept_id", -1)) == CONCEPT_ID, "reservation cursor concept differs")
    base.require(int(value.get("predecessor_id", -1)) == PREDECESSOR_ID, "reservation cursor predecessor differs")
    base.require(int(value.get("predecessor_index", -1)) == PREDECESSOR_INDEX, "reservation cursor predecessor index differs")
    base.require(int(value.get("successor_index", -1)) == SUCCESSOR_INDEX, "reservation cursor successor index differs")
    base.require(
        value.get("state") in {"creation_intent_recorded", "draft_discovered", "published_verified"},
        "reservation cursor state differs",
    )
    base.require(isinstance(value.get("created_at_utc"), str) and bool(value["created_at_utc"]), "reservation cursor creation time differs")
    base.require(isinstance(value.get("updated_at_utc"), str) and bool(value["updated_at_utc"]), "reservation cursor update time differs")
    for key in ("draft_id", "record_id"):
        base.require(value.get(key) is None or type(value[key]) is int, f"reservation cursor {key} differs")
    return value


def _write_reservation_cursor(
    state: str,
    *,
    draft_id: int | None = None,
    record_id: int | None = None,
) -> None:
    base.require(state in {"creation_intent_recorded", "draft_discovered", "published_verified"}, "invalid cursor state")
    previous_cursor = _load_reservation_cursor()
    now = datetime.now(timezone.utc).isoformat()
    value = {
        "schema_id": "program-matematika-indonesia/zenodo-reservation-cursor/1.0.0",
        "version": VERSION,
        "concept_id": CONCEPT_ID,
        "predecessor_id": PREDECESSOR_ID,
        "predecessor_index": PREDECESSOR_INDEX,
        "successor_index": SUCCESSOR_INDEX,
        "state": state,
        "draft_id": draft_id,
        "record_id": record_id,
        "created_at_utc": previous_cursor["created_at_utc"] if previous_cursor is not None else now,
        "updated_at_utc": now,
    }
    _assert_sanitized_receipt(value, "reservation_cursor")
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    temporary = RESERVATION_CURSOR.with_name(f".{RESERVATION_CURSOR.name}.tmp")
    temporary.write_bytes(data)
    temporary.replace(RESERVATION_CURSOR)
    base.require(RESERVATION_CURSOR.read_bytes() == data, "reservation cursor readback differs")


def reserve_or_resume(client: Any) -> tuple[int, bool, str, int]:
    """Resume one draft or issue one bounded new-version transaction."""

    public_state = anonymous_lineage_search()
    latest = public_state["latest"]
    base.require(public_state["target"] is None, "public v0.62.13 appeared before reservation")
    base.require(int(latest.get("id", -1)) == PREDECESSOR_ID, "concept latest changed before reservation")
    latest_metadata = latest.get("metadata", {})
    base.require(latest_metadata.get("version") == PREDECESSOR_VERSION, "latest predecessor version differs")
    relation = base.version_relation(latest_metadata)
    base.require(
        int(relation["index"]) == PREDECESSOR_INDEX and relation["is_last"] is True,
        "exact index-37 predecessor is not latest",
    )

    predecessor = base.authenticated_predecessor(client)
    existing_id = base.latest_draft_id(predecessor)
    if existing_id != PREDECESSOR_ID:
        draft = base.get_draft(client, existing_id)
        _draft_index(draft, client=client, draft_id=existing_id)
        _write_reservation_cursor("draft_discovered", draft_id=existing_id)
        return existing_id, False, "resumed_single_existing_draft", 0

    cursor = _load_reservation_cursor()
    if cursor is not None:
        base.require(cursor["state"] != "published_verified", "published cursor exists while target is not public")
        cursor_draft_id = cursor.get("draft_id")
        if isinstance(cursor_draft_id, int) and cursor_draft_id > 0:
            draft = base.get_draft(client, cursor_draft_id)
            _draft_index(draft, client=client, draft_id=cursor_draft_id)
            return cursor_draft_id, False, "resumed_cursor_draft", 0
        draft_id = PREDECESSOR_ID
        for attempt in range(5):
            draft_id = _latest_draft_from_predecessor(client)
            if draft_id != PREDECESSOR_ID:
                break
            base.time.sleep(2 * (attempt + 1))
        base.require(
            draft_id != PREDECESSOR_ID,
            "unresolved prior creation intent; refusing another new-version request",
        )
        draft = base.get_draft(client, draft_id)
        _draft_index(draft, client=client, draft_id=draft_id)
        _write_reservation_cursor("draft_discovered", draft_id=draft_id)
        return draft_id, False, "resumed_ambiguous_cursor_draft", 0

    response = None
    requests_attempted = 1
    route = "inveniordm_record_versions_single_post"
    _write_reservation_cursor("creation_intent_recorded")
    try:
        response = client.post(
            f"{base.PUBLIC_API}/{PREDECESSOR_ID}/versions",
            json={},
            headers={
                "Accept": "application/vnd.inveniordm.v1+json",
                "Content-Type": "application/json",
            },
            timeout=(20, 180),
            allow_redirects=False,
        )
    except base.requests.RequestException:
        response = None

    if response is not None and response.status_code not in (201, 409, 429, 500, 502, 503, 504):
        raise RuntimeError(f"Zenodo new-version action returned HTTP {response.status_code}")

    if response is not None and response.status_code == 201:
        value = response.json()
        base.require(isinstance(value, dict), "Zenodo new-version response is malformed")
        draft_id = int(value.get("id", -1))
        base.require(draft_id > 0 and value.get("is_draft") is True, "Zenodo new-version draft identity differs")
        draft = base.get_draft(client, draft_id)
        _draft_index(draft, client=client, draft_id=draft_id)
        _write_reservation_cursor("draft_discovered", draft_id=draft_id)
        return draft_id, True, route, requests_attempted

    # A timeout, 409, or transient server response is ambiguous.  Never retry
    # creation.  Re-read the authoritative latest-draft link and resume exactly
    # the one draft that the single transaction may have created.
    draft_id = PREDECESSOR_ID
    for attempt in range(5):
        draft_id = _latest_draft_from_predecessor(client)
        if draft_id != PREDECESSOR_ID:
            break
        base.time.sleep(2 * (attempt + 1))
    base.require(draft_id != PREDECESSOR_ID, "new-version result is ambiguous and no resumable draft exists")
    draft = base.get_draft(client, draft_id)
    _draft_index(draft, client=client, draft_id=draft_id)
    _write_reservation_cursor("draft_discovered", draft_id=draft_id)
    observed_201 = bool(response is not None and response.status_code == 201)
    return draft_id, observed_201, route, requests_attempted


def verify_lineage(
    record: dict[str, Any],
    predecessor_record: dict[str, Any],
    predecessor_rows: list[dict[str, Any]],
    *,
    newly_published: bool,
) -> dict[str, Any]:
    record_id = int(record["id"])
    state = anonymous_lineage_search()
    target = state["target"]
    base.require(target is not None and int(target.get("id", -1)) == record_id, "target is absent from lineage")
    target_relation = base.version_relation(target.get("metadata", {}))
    base.require(int(target_relation["index"]) == SUCCESSOR_INDEX, "successor index differs")
    base.require(target_relation["is_last"] is True, "successor is not marked latest")
    latest = state["latest"]
    base.require(
        int(latest.get("id", -1)) == record_id,
        "published v0.62.13/index-38 is not concept latest",
    )
    base.require(
        int(base.version_relation(latest.get("metadata", {}))["index"]) == SUCCESSOR_INDEX
        and int(state["record_count"]) == SUCCESSOR_INDEX,
        "concept latest/lineage count does not close at v0.62.13 index 38",
    )

    predecessor_after = base.public_json(f"{base.PUBLIC_API}/{PREDECESSOR_ID}")
    before_metadata = predecessor_record.get("metadata", {})
    after_metadata = predecessor_after.get("metadata", {})
    base.require(
        base.stable_public_metadata(after_metadata) == base.stable_public_metadata(before_metadata),
        "predecessor stable metadata changed",
    )
    before_relation = base.version_relation(before_metadata)
    after_relation = base.version_relation(after_metadata)
    base.require(int(before_relation["index"]) == int(after_relation["index"]) == PREDECESSOR_INDEX, "predecessor index changed")
    base.require(after_relation["is_last"] is False, "predecessor remains latest after successor publication")
    before_files = [
        (row["name"], row["bytes"], row["md5"])
        for row in ORIGINAL_PUBLIC_FILE_STUBS(predecessor_record, EXPECTED_FILES, "predecessor-before-lineage")
    ]
    after_files = [
        (row["name"], row["bytes"], row["md5"])
        for row in ORIGINAL_PUBLIC_FILE_STUBS(predecessor_after, EXPECTED_FILES, "predecessor-after-lineage")
    ]
    base.require(after_files == before_files, "predecessor file inventory changed")
    predecessor_observed = base.anonymous_inventory(predecessor_after, predecessor_rows, "predecessor-after")
    base.require(
        base.inventory_sha(predecessor_observed) == EXPECTED_PREDECESSOR_AGGREGATE,
        "predecessor public bytes changed",
    )
    base.require(after_metadata.get("access_right") == "open", "predecessor access is no longer open")

    doi_expectations = (
        (record_id, record_id),
        (PREDECESSOR_ID, PREDECESSOR_ID),
        (CONCEPT_ID, int(latest["id"])),
    )
    for doi_id, expected_id in doi_expectations:
        response = base.public_get(f"https://doi.org/10.5281/zenodo.{doi_id}")
        base.require(response.status_code == 200, "DOI resolution failed")
        base.require(urlparse(response.url).path.rstrip("/") == f"/records/{expected_id}", "DOI target differs")

    student = base.public_get(LEARNER_SITE)
    base.require(student.status_code == 200 and "Program Matematika Indonesia" in student.text, "student site readback failed")
    backend = base.public_get(BACKEND_CENTER)
    base.require(backend.status_code == 200, "backend center readback failed")
    github = base.public_get(GITHUB_RELEASE)
    base.require(github.status_code == 200 and "v0.62.13" in github.text, "GitHub release readback failed")
    baseline = base.public_get(PUBLIC_BASELINE_URL)
    base.require(baseline.status_code == 200, "public baseline readback failed")
    expected_baseline = (RELEASE_DIR / "public-baseline-v0.62.12.json").read_bytes()
    base.require(baseline.content == expected_baseline, "public baseline bytes differ")

    return {
        "anonymous_lineage_search": "pass",
        "concept_record_count_observed": state["record_count"],
        "concept_latest_record_id": int(latest["id"]),
        "concept_latest_version": latest.get("metadata", {}).get("version"),
        "predecessor_version_index": PREDECESSOR_INDEX,
        "successor_version_index": SUCCESSOR_INDEX,
        "exactly_one_public_target_version": True,
        "publish_path_executed": bool(newly_published),
        "target_is_current_latest": int(latest["id"]) == record_id,
        "successor_doi_resolution": "pass",
        "concept_doi_latest_resolution": "pass",
        "predecessor_doi_resolution_unchanged": "pass",
        "predecessor_open_unchanged": True,
        "predecessor_stable_metadata_unchanged": True,
        "predecessor_file_order_unchanged": True,
        "predecessor_anonymous_readback": "pass_100_of_100",
        "student_site_readback": "pass",
        "backend_center_readback": "pass",
        "public_baseline_readback": "pass_exact_bytes",
        "github_release_readback": "pass",
    }


def _root_receipt_replacement_allowed() -> bool:
    if not ROOT_RECEIPT.is_file():
        return True
    if _identity(ROOT_RECEIPT) == EXPECTED_PREDECESSOR_RECEIPT:
        return True
    current = _load_json(ROOT_RECEIPT, "root publication receipt")
    _assert_sanitized_receipt(current, "root_publication_receipt")
    if current.get("version") == VERSION:
        return True
    zenodo = current.get("zenodo", {})
    base.require(isinstance(zenodo, dict), "root receipt Zenodo evidence is malformed")
    index = zenodo.get("successor_version_index")
    if index is None:
        lineage = current.get("lineage_verification", {})
        base.require(isinstance(lineage, dict), "root receipt lineage evidence is malformed")
        index = lineage.get("successor_version_index")
    base.require(type(index) is int, "root receipt successor index is unavailable")
    if int(index) > SUCCESSOR_INDEX:
        return False
    raise RuntimeError("refusing to replace an unrecognized root publication receipt")


def write_receipts(
    record: dict[str, Any],
    observed: list[dict[str, Any]],
    predecessor_metadata: dict[str, Any],
    predecessor_rows: list[dict[str, Any]],
    github: dict[str, Any],
    lineage: dict[str, Any],
    draft_id: int | None,
    newversion_http_201_observed: bool,
    deleted: int,
    uploaded: int,
    execution_mode: str,
    reservation_route: str,
    newversion_requests_attempted: int,
) -> tuple[int, str]:
    metadata = record.get("metadata", {})
    base.require(isinstance(metadata, dict) and metadata.get("access_right") == "open", "successor is not open")
    base.require(int(base.version_relation(metadata)["index"]) == SUCCESSOR_INDEX, "successor index differs")
    base.require(len(observed) == EXPECTED_FILES, "successor observation count differs")
    observed_by_name = {str(row["name"]): row for row in observed}
    base.require(len(observed_by_name) == EXPECTED_FILES, "successor observation names are not unique")
    local_rows, _, local_authority, current_github = local_inventory()
    base.require(
        _same_canonical_json_value(current_github, github),
        "GitHub receipt changed between local validation and receipt construction",
    )
    snapshot = local_authority["course_snapshot"]
    package_closure = local_authority["course_capsule_package_closure"]
    local_by_name = {str(row["name"]): row for row in local_rows}
    base.require(set(observed_by_name) == set(local_by_name), "successor/local inventory differs")
    for name, local in local_by_name.items():
        public = observed_by_name[name]
        base.require(int(public["bytes"]) == int(local["bytes"]), f"successor size differs: {name}")
        base.require(public["sha256"] == local["sha256"], f"successor SHA-256 differs: {name}")
    base.require(
        base.compact_sha(metadata.get("creators", [])) == base.compact_sha(predecessor_metadata.get("creators", [])),
        "creator credits differ from predecessor",
    )
    base.require(
        base.compact_sha(metadata.get("contributors", []))
        == base.compact_sha(predecessor_metadata.get("contributors", [])),
        "contributor credits differ from predecessor",
    )

    payload = [
        {
            "name": row["name"],
            "bytes": row["bytes"],
            "md5": row["md5"],
            "sha256": row["sha256"],
            "anonymous_url": row["url"],
            "anonymous_byte_identity": True,
            "provenance": (
                "v0.62.13_same_name_replacement"
                if row["name"] in SAME_NAME_REPLACEMENTS
                else "v0.62.13_pure_addition"
                if row["name"] in PURE_ADDITIONS
                else "retained_exact_from_v0.62.12"
            ),
        }
        for row in observed
    ]
    publisher = Path(__file__).resolve()
    receipt = {
        "schema_id": "program-matematika-indonesia/zenodo-publication-receipt/1.2.0",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "state": "published_open_modular_backend_successor",
        "version": VERSION,
        "student_entry": {
            "primary_url": LEARNER_SITE,
            "backend_center_url": BACKEND_CENTER,
            "public_baseline_url": PUBLIC_BASELINE_URL,
            "description_first_href": LEARNER_SITE,
            "related_identifiers_first": LEARNER_SITE,
            "zenodo_default_preview": LEARNER_FILE,
            "machine_backend_is_secondary": True,
        },
        "workflow_evidence": {
            "program_course_capsules": snapshot["course_count"],
            "independent_course_lanes": snapshot["course_count"],
            "implementation_families_compared": IMPLEMENTATION_FAMILY_COUNT,
            "published_roles_at_snapshot": snapshot["published_role_count"],
            "published_role_ids": snapshot["published_role_ids"],
            "production_roles_at_snapshot": snapshot["production_role_count"],
            "production_role_ids": snapshot["production_role_ids"],
            "distinct_published_doi_records": snapshot["distinct_published_doi_records"],
            "canonical_course_ids": snapshot["canonical_course_ids"],
            "adapter_bound_roles": list(ADAPTER_BOUND_ROLES),
            "adapter_bound_role_count": len(ADAPTER_BOUND_ROLES),
            "native_roles_retained_without_adapter_claim": NATIVE_ONLY_ROLE_COUNT,
            "d30_classification": "learner_delivery_and_course_capsule_evidence_not_adapter",
            "workflow_sequence": [
                "native_first_independent_lane_implementation",
                "comparative_audit_of_observed_implementations",
                "select_globally_integrable_strengths",
                "add_zero_copy_capsules_and_thin_adapters",
                "preserve_owner_native_authority",
            ],
            "architecture": "thin_format_neutral_zero_copy_capsules_over_canonical_course_native_backends",
            "learner_and_educator_layers_present": True,
            "learner_html_is_primary": True,
            "machine_json_is_secondary": True,
            "native_identity_rights_and_formats_preserved": True,
        },
        "zenodo": {
            "record_id": int(record["id"]),
            "version_doi": record["doi"],
            "concept_record_id": CONCEPT_ID,
            "concept_doi": record["conceptdoi"],
            "predecessor_record_id": PREDECESSOR_ID,
            "predecessor_doi": f"10.5281/zenodo.{PREDECESSOR_ID}",
            "predecessor_version_index": PREDECESSOR_INDEX,
            "successor_version_index": SUCCESSOR_INDEX,
            "access_right": metadata["access_right"],
            "license": base.license_id(metadata),
            "language": metadata["language"],
            "publication_date": metadata["publication_date"],
            "file_count": len(payload),
            "anonymous_readback": "pass_100_of_100",
        },
        "github_authority": {
            "release": GITHUB_RELEASE,
            "receipt_sha256": base.sha256_bytes(GITHUB_RECEIPT.read_bytes()),
            "tag_target_commit": github["source"]["commit"],
            "source_commit": github["source"]["commit"],
            "source_tree": github["source"]["tree"],
            "tag_resolves_to_source_commit": github["source"]["tag_resolves_to_commit"],
            "anonymous_readback": github["anonymous_asset_readback"]["result"],
            "inventory_aggregate_sha256": github["inventory"]["aggregate_sha256"],
            "course_snapshot": snapshot,
        },
        "replacement_boundary": {
            "predecessor_files": EXPECTED_FILES,
            "retained_exact_files": EXPECTED_RETAINED,
            "same_name_replacements": sorted(SAME_NAME_REPLACEMENTS),
            "pure_omissions_preserved_in_public_predecessor": sorted(PURE_OMISSIONS),
            "pure_additions": sorted(PURE_ADDITIONS),
            "effective_draft_omissions": sorted(OMITTED),
            "effective_draft_additions": sorted(ADDITIONS),
            "successor_files": EXPECTED_FILES,
            "draft_omissions_removed_in_this_execution": deleted,
            "draft_additions_uploaded_in_this_execution": uploaded,
            "published_record_files_deleted_or_replaced": 0,
            "draft_id": draft_id,
            "newversion_http_201_observed": newversion_http_201_observed,
            "newversion_requests_attempted": newversion_requests_attempted,
            "newversion_retried_after_ambiguity": False,
            "execution_mode": execution_mode,
            "reservation_route": reservation_route,
            "course_snapshot": snapshot,
            "course_capsule_package_closure": package_closure,
        },
        "payload_inventory": payload,
        "payload_inventory_aggregate_sha256": base.inventory_sha(payload),
        "payload_total_bytes": sum(int(row["bytes"]) for row in payload),
        "inheritance": {
            "predecessor_inventory_aggregate_sha256": base.inventory_sha(predecessor_rows),
            "predecessor_unchanged": True,
            "creators_count": len(metadata.get("creators", [])),
            "creators_canonical_sha256": base.compact_sha(metadata.get("creators", [])),
            "contributors_count": len(metadata.get("contributors", [])),
            "contributors_canonical_sha256": base.compact_sha(metadata.get("contributors", [])),
            "source_and_human_credits_preserved": True,
            "stable_metadata_preserved": True,
        },
        "lineage_verification": lineage,
        "overall_program_complete": False,
        "model_provenance": MODEL,
        "publisher": {
            "path": publisher.relative_to(PROJECT).as_posix(),
            "bytes": publisher.stat().st_size,
            "sha256": base.sha256_bytes(publisher.read_bytes()),
            "git_commands_used": 0,
        },
        "anonymous_transport": {
            "trust_env": False,
            "netrc_credentials_allowed": False,
            "authorization_header_allowed": False,
        },
        "privacy": {
            "credentials_recorded": False,
            "credential_locator_recorded": False,
            "absolute_profile_paths_recorded": False,
            "personal_name_recorded": False,
        },
    }
    _assert_sanitized_receipt(receipt)
    data = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    targets = [VERSION_RECEIPT]
    if _root_receipt_replacement_allowed():
        targets.append(ROOT_RECEIPT)
    for path in targets:
        temporary = path.with_name(f".{path.name}.tmp-v06213")
        temporary.write_bytes(data)
        temporary.replace(path)
        base.require(path.read_bytes() == data, f"receipt atomic readback differs: {path.name}")
    return len(data), base.sha256_bytes(data)


def reuse_existing_receipts(
    record: dict[str, Any], observed: list[dict[str, Any]], github: dict[str, Any]
) -> tuple[int, str] | None:
    existing: list[Path] = []
    for path in (VERSION_RECEIPT, ROOT_RECEIPT):
        if path.is_file():
            candidate = _load_json(path, path.name)
            if candidate.get("version") == VERSION:
                existing.append(path)
    if not existing:
        return None
    data = existing[0].read_bytes()
    base.require(all(path.read_bytes() == data for path in existing), "existing v0.62.13 receipts differ")
    receipt = json.loads(data.decode("utf-8"))
    try:
        _assert_sanitized_receipt(receipt)
    except RuntimeError:
        return None
    if set(receipt) != {
        "anonymous_transport",
        "github_authority",
        "inheritance",
        "lineage_verification",
        "model_provenance",
        "overall_program_complete",
        "payload_inventory",
        "payload_inventory_aggregate_sha256",
        "payload_total_bytes",
        "privacy",
        "publisher",
        "recorded_at_utc",
        "replacement_boundary",
        "schema_id",
        "state",
        "student_entry",
        "version",
        "workflow_evidence",
        "zenodo",
    }:
        return None
    if receipt.get("schema_id") != "program-matematika-indonesia/zenodo-publication-receipt/1.2.0":
        return None
    if receipt.get("state") != "published_open_modular_backend_successor":
        return None
    _, _, local_authority, _ = local_inventory()
    current_snapshot = local_authority["course_snapshot"]
    current_package_closure = local_authority["course_capsule_package_closure"]
    workflow_evidence = receipt.get("workflow_evidence", {})
    if not isinstance(workflow_evidence, dict):
        return None
    if any(
        not _same_canonical_json_value(workflow_evidence.get(key), value)
        for key, value in {
            "program_course_capsules": current_snapshot["course_count"],
            "independent_course_lanes": current_snapshot["course_count"],
            "implementation_families_compared": IMPLEMENTATION_FAMILY_COUNT,
            "published_roles_at_snapshot": current_snapshot["published_role_count"],
            "published_role_ids": current_snapshot["published_role_ids"],
            "production_roles_at_snapshot": current_snapshot["production_role_count"],
            "production_role_ids": current_snapshot["production_role_ids"],
            "distinct_published_doi_records": current_snapshot["distinct_published_doi_records"],
            "canonical_course_ids": current_snapshot["canonical_course_ids"],
            "adapter_bound_roles": list(ADAPTER_BOUND_ROLES),
            "adapter_bound_role_count": len(ADAPTER_BOUND_ROLES),
            "native_roles_retained_without_adapter_claim": NATIVE_ONLY_ROLE_COUNT,
        }.items()
    ):
        return None
    github_authority = receipt.get("github_authority")
    if not isinstance(github_authority, dict) or not _same_canonical_json_value(
        github_authority.get("course_snapshot"), current_snapshot
    ):
        return None
    replacement_boundary = receipt.get("replacement_boundary")
    if not isinstance(replacement_boundary, dict):
        return None
    if not _same_canonical_json_value(
        replacement_boundary.get("course_snapshot"), current_snapshot
    ):
        return None
    if not _same_canonical_json_value(
        replacement_boundary.get("course_capsule_package_closure"),
        current_package_closure,
    ):
        return None
    if int(receipt.get("zenodo", {}).get("record_id", -1)) != int(record["id"]):
        return None
    if receipt.get("zenodo", {}).get("access_right") != "open":
        return None
    if int(receipt.get("zenodo", {}).get("successor_version_index", -1)) != SUCCESSOR_INDEX:
        return None
    if receipt.get("zenodo", {}).get("anonymous_readback") != "pass_100_of_100":
        return None
    if receipt.get("anonymous_transport") != {
        "trust_env": False,
        "netrc_credentials_allowed": False,
        "authorization_header_allowed": False,
    }:
        return None
    if any(
        receipt.get("privacy", {}).get(key) is not False
        for key in (
            "credentials_recorded",
            "credential_locator_recorded",
            "absolute_profile_paths_recorded",
            "personal_name_recorded",
        )
    ):
        return None
    payload = receipt.get("payload_inventory")
    if not isinstance(payload, list) or len(payload) != EXPECTED_FILES:
        return None
    payload_by_name = {str(row.get("name", "")): row for row in payload if isinstance(row, dict)}
    observed_by_name = {str(row["name"]): row for row in observed}
    if len(payload_by_name) != EXPECTED_FILES or set(payload_by_name) != set(observed_by_name):
        return None
    for name, public in observed_by_name.items():
        saved = payload_by_name[name]
        if int(saved.get("bytes", -1)) != int(public["bytes"]) or saved.get("sha256") != public["sha256"]:
            return None
    if receipt.get("payload_inventory_aggregate_sha256") != base.inventory_sha(observed):
        return None
    if receipt.get("github_authority", {}).get("receipt_sha256") != base.sha256_bytes(GITHUB_RECEIPT.read_bytes()):
        return None
    current = Path(__file__).resolve()
    publisher = receipt.get("publisher", {})
    if publisher.get("bytes") != current.stat().st_size or publisher.get("sha256") != base.sha256_bytes(current.read_bytes()):
        return None
    for path in (VERSION_RECEIPT, ROOT_RECEIPT):
        if not path.is_file() or path.read_bytes() != data:
            temporary = path.with_name(f".{path.name}.tmp-v06213-restore")
            temporary.write_bytes(data)
            temporary.replace(path)
    return len(data), base.sha256_bytes(data)


base.public_file_stubs = ORIGINAL_PUBLIC_FILE_STUBS
base.local_inventory = local_inventory
base.predecessor_authority = predecessor_authority
base.related_identifiers = related_identifiers
base.verify_exact_draft = verify_exact_draft
base.validate_draft_boundary = validate_draft_boundary
base.delete_omissions = delete_omissions
base.verify_final_draft_metadata = verify_final_draft_metadata
base.verify_rdm_learner_preview = verify_rdm_learner_preview
base.write_receipts = write_receipts


def _expected_existing_metadata(
    record: dict[str, Any], predecessor_metadata: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = base.metadata_payload({"metadata": predecessor_metadata}, predecessor_metadata)
    publication_date = record.get("metadata", {}).get("publication_date")
    base.require(isinstance(publication_date, str) and bool(publication_date), "published successor date is absent")
    payload["publication_date"] = publication_date
    return payload, base.expected_public_metadata(predecessor_metadata, payload)


def _verify_public_target(
    target: dict[str, Any],
    local_rows: list[dict[str, Any]],
    predecessor_metadata: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    record = base.public_json(f"{base.PUBLIC_API}/{int(target['id'])}")
    payload, expected_metadata = _expected_existing_metadata(record, predecessor_metadata)
    observed = base.verify_public_successor(record, local_rows, predecessor_metadata, expected_metadata)
    return record, payload, observed


def _publish_or_converge(
    client: Any,
    predecessor_deposition: dict[str, Any],
    predecessor_metadata: dict[str, Any],
    predecessor_rows: list[dict[str, Any]],
    local_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    before_reservation = anonymous_lineage_search()
    if before_reservation["target"] is not None:
        record, payload, observed = _verify_public_target(
            before_reservation["target"], local_rows, predecessor_metadata
        )
        return {
            "record": record,
            "payload": payload,
            "observed": observed,
            "draft_id": None,
            "newversion_http_201_observed": False,
            "newversion_requests_attempted": 0,
            "reservation_route": "not_applicable_concurrent_public_before_reservation",
            "deleted": 0,
            "uploaded": 0,
            "execution_mode": "verification_only_concurrent_public_before_reservation",
            "newly_published": False,
        }
    base.require(
        int(before_reservation["latest"].get("id", -1)) == PREDECESSOR_ID,
        "concept latest changed before draft reservation",
    )

    (
        draft_id,
        newversion_http_201_observed,
        reservation_route,
        newversion_requests_attempted,
    ) = reserve_or_resume(client)

    after_reservation = anonymous_lineage_search()
    if after_reservation["target"] is not None:
        record, payload, observed = _verify_public_target(
            after_reservation["target"], local_rows, predecessor_metadata
        )
        return {
            "record": record,
            "payload": payload,
            "observed": observed,
            "draft_id": None,
            "newversion_http_201_observed": newversion_http_201_observed,
            "newversion_requests_attempted": newversion_requests_attempted,
            "reservation_route": reservation_route,
            "deleted": 0,
            "uploaded": 0,
            "execution_mode": "verification_only_concurrent_public_after_reservation",
            "newly_published": False,
        }
    base.require(
        int(after_reservation["latest"].get("id", -1)) == PREDECESSOR_ID,
        "concept latest changed after draft reservation",
    )

    draft = base.get_draft(client, draft_id)
    _draft_index(draft, client=client, draft_id=draft_id)
    base.verify_draft_metadata_boundary(draft, predecessor_deposition)
    base.validate_draft_boundary(draft, predecessor_rows, local_rows)

    # These operations affect only the unpublished successor draft.  A wrong
    # same-name file or a file outside the pinned boundary is never replaced
    # opportunistically.
    deleted = base.delete_omissions(client, draft_id)
    draft = base.get_draft(client, draft_id)
    base.validate_draft_boundary(draft, predecessor_rows, local_rows)
    uploaded = base.upload_additions(client, draft_id, local_rows)
    draft = base.get_draft(client, draft_id)
    verify_exact_draft(draft, local_rows)

    payload = base.metadata_payload(draft, predecessor_metadata)
    base.require(payload.get("access_right") == "open", "target metadata is not open")
    base.put_metadata(client, draft_id, payload)
    base.set_learner_default_preview(client, draft_id)
    final_draft = base.get_draft(client, draft_id)
    _draft_index(final_draft, client=client, draft_id=draft_id)
    base.verify_draft_metadata_boundary(final_draft, predecessor_deposition)
    verify_exact_draft(final_draft, local_rows)
    verify_final_draft_metadata(final_draft, payload)
    verify_rdm_learner_preview(base.rdm_draft(client, draft_id))

    before_publish = anonymous_lineage_search()
    if before_publish["target"] is not None:
        record, existing_payload, observed = _verify_public_target(
            before_publish["target"], local_rows, predecessor_metadata
        )
        return {
            "record": record,
            "payload": existing_payload,
            "observed": observed,
            "draft_id": None,
            "newversion_http_201_observed": newversion_http_201_observed,
            "newversion_requests_attempted": newversion_requests_attempted,
            "reservation_route": reservation_route,
            "deleted": deleted,
            "uploaded": uploaded,
            "execution_mode": "verification_only_concurrent_public_before_publish",
            "newly_published": False,
        }
    base.require(
        int(before_publish["latest"].get("id", -1)) == PREDECESSOR_ID,
        "concept latest changed before publish",
    )

    record = base.publish_once(client, draft_id)
    expected_metadata = base.expected_public_metadata(predecessor_metadata, payload)
    observed = base.verify_public_successor(record, local_rows, predecessor_metadata, expected_metadata)
    return {
        "record": record,
        "payload": payload,
        "observed": observed,
        "draft_id": draft_id,
        "newversion_http_201_observed": newversion_http_201_observed,
        "newversion_requests_attempted": newversion_requests_attempted,
        "reservation_route": reservation_route,
        "deleted": deleted,
        "uploaded": uploaded,
        "execution_mode": "published_or_converged_single_index_38_draft",
        "newly_published": True,
    }


def publication_main(token_file: Path | None = None) -> None:
    local_rows, _, local_authority, github = local_inventory()
    _bind_snapshot_metadata(local_authority["course_snapshot"])

    # This is the first network operation and it is always anonymous.  No
    # credential file or environment variable has been read at this point.
    public_state = anonymous_lineage_search()
    target = public_state["target"]
    latest = public_state["latest"]

    if target is None:
        latest_metadata = latest.get("metadata", {})
        base.require(int(latest.get("id", -1)) == PREDECESSOR_ID, "latest public record is not exact v0.62.12")
        base.require(latest_metadata.get("version") == PREDECESSOR_VERSION, "latest public version differs")
        relation = base.version_relation(latest_metadata)
        base.require(
            int(relation["index"]) == PREDECESSOR_INDEX and relation["is_last"] is True,
            "v0.62.12/index-37 is not the public latest version",
        )

    predecessor_record, predecessor_metadata, predecessor_rows = predecessor_authority(local_rows)

    if target is not None:
        record, payload, observed = _verify_public_target(target, local_rows, predecessor_metadata)
        result = {
            "record": record,
            "payload": payload,
            "observed": observed,
            "draft_id": None,
            "newversion_http_201_observed": False,
            "newversion_requests_attempted": 0,
            "reservation_route": "not_applicable_existing_public",
            "deleted": 0,
            "uploaded": 0,
            "execution_mode": "verification_only_exact_existing_public",
            "newly_published": False,
        }
    else:
        configured_token_file = os.environ.get(TOKEN_FILE_ENV)
        if token_file is not None:
            explicit_token_file = str(token_file)
            base.require(bool(explicit_token_file), "--token-file is empty")
            base.require(
                configured_token_file in (None, explicit_token_file),
                f"--token-file conflicts with the explicitly set {TOKEN_FILE_ENV}",
            )
            os.environ[TOKEN_FILE_ENV] = explicit_token_file
        else:
            base.require(
                bool(configured_token_file),
                f"publication requires explicit --token-file or {TOKEN_FILE_ENV}",
            )
        token = base.load_token()
        client = base.authenticated_session(token)
        predecessor_deposition = base.authenticated_predecessor(client)
        base.verify_predecessor_metadata_mapping(predecessor_deposition, predecessor_metadata)
        result = _publish_or_converge(
            client,
            predecessor_deposition,
            predecessor_metadata,
            predecessor_rows,
            local_rows,
        )

    record = result["record"]
    observed = result["observed"]
    draft_id = result["draft_id"]
    newversion_http_201_observed = bool(result["newversion_http_201_observed"])
    newversion_requests_attempted = int(result["newversion_requests_attempted"])
    reservation_route = str(result["reservation_route"])
    deleted = int(result["deleted"])
    uploaded = int(result["uploaded"])
    execution_mode = str(result["execution_mode"])
    newly_published = bool(result["newly_published"])

    lineage = verify_lineage(
        record,
        predecessor_record,
        predecessor_rows,
        newly_published=newly_published,
    )
    _write_reservation_cursor(
        "published_verified",
        draft_id=draft_id if isinstance(draft_id, int) else None,
        record_id=int(record["id"]),
    )
    # Always materialize a fresh canonical receipt from this execution's
    # verified observations.  Historical receipt bytes are never trusted as a
    # substitute for current lineage, metadata, inventory, or privacy checks.
    receipt_bytes, receipt_sha = write_receipts(
        record,
        observed,
        predecessor_metadata,
        predecessor_rows,
        github,
        lineage,
        draft_id,
        newversion_http_201_observed,
        deleted,
        uploaded,
        execution_mode,
        reservation_route,
        newversion_requests_attempted,
    )
    print(
        json.dumps(
            {
                "status": "pass",
                "execution_mode": execution_mode,
                "record_id": int(record["id"]),
                "doi": record["doi"],
                "concept_doi": record["conceptdoi"],
                "successor_version_index": SUCCESSOR_INDEX,
                "files": len(observed),
                "bytes": sum(int(row["bytes"]) for row in observed),
                "aggregate_sha256": base.inventory_sha(observed),
                "receipt": VERSION_RECEIPT.relative_to(PROJECT).as_posix(),
                "receipt_bytes": receipt_bytes,
                "receipt_sha256": receipt_sha,
            },
            separators=(",", ":"),
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Publish or anonymously verify PMI v0.62.13 on Zenodo concept 22059707."
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="strictly local validation; no dynamic import, network, credential, draft, or write",
    )
    parser.add_argument(
        "--token-file",
        type=Path,
        help=(
            "explicit Zenodo credential-file path; read only if no exact public "
            f"v0.62.13 exists (alternative: explicitly set {TOKEN_FILE_ENV})"
        ),
    )
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(_standalone_preflight(), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return
    publication_main(args.token_file)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(f"FAIL: {type(exc).__name__}: {detail}", file=sys.stderr)
        raise SystemExit(1)
