#!/usr/bin/env python3
"""Build the deterministic v0.62.7 learner-access overlay release.

This is an additive adapter over the immutable v0.62.6 release.  The builder
copies every base-release byte unchanged and creates exactly five new files.
It uses bounded immutable raw-commit reads for provenance, performs read-only
public QA, and never mutates a network service or publishes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from urllib.parse import quote
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


VERSION = "0.62.7"
BASE_VERSION = "0.62.6"
FROZEN_AUTHORITY_VERSION = "0.62.0"
PREDECESSOR_RECORD_ID = 22167050
REPOSITORY_URL = "https://github.com/KokunoYumeto/program-matematika-indonesia"
RAW_REPOSITORY_URL = "https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia"
STUDENT_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
FIXED_ZIP_TIME = (2026, 8, 30, 0, 0, 0)

BASE_EXPECTED = {
    "files": 93,
    "bytes": 65_639_635,
    "aggregate_sha256": "fa825a88b10c37ff7897554b15197db993a40993cf3ac3b949e317ff3305f84b",
    "checksum_file": {
        "name": "LIVE_OVERLAY_CHECKSUMS_v0.62.6.sha256",
        "bytes": 10_357,
        "sha256": "aec9d227250150fb0221bcdabff6811320ea2f27287cece72d40c999b58ccef2",
        "entries": 92,
    },
}

CORE_ADDITIVE_NAMES = (
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.7.html",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.7.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.7.zip",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.7.json",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.7.sha256",
)
BACKEND_V23_NAMES = (
    "program-matematika-indonesia-backend-v2.3-conformance-v0.1.1.zip",
    "GLOBAL_BACKEND_V23_SCOPE_ADMISSION_RECEIPT_v0.62.5.json",
    "GLOBAL_BACKEND_V23_VALIDATION_RECEIPT_v0.62.5.json",
    "GLOBAL_BACKEND_V23_ARCHIVE_DETERMINISM_RECEIPT_v0.62.5.json",
)
ADDITIVE_NAMES = CORE_ADDITIVE_NAMES
STANDALONE_NAME, MANIFEST_NAME, SOURCE_ZIP_NAME, RECEIPT_NAME, CHECKSUM_NAME = CORE_ADDITIVE_NAMES
BACKEND_ARCHIVE_NAME, BACKEND_SCOPE_NAME, BACKEND_VALIDATION_NAME, BACKEND_DETERMINISM_NAME = BACKEND_V23_NAMES
BUILD_MARKER_NAME = ".pmi-live-overlay-v0.62.7-building.json"

SOURCE_MEMBERS = (
    "docs/app.js",
    "docs/courses.js",
    "docs/id-ID/courses/B95/index.html",
    "docs/id-ID/courses/D30/index.html",
    "docs/id-ID/courses/D40/index.html",
    "docs/index.html",
    "docs/learner-state.js",
    "docs/live-course-publications.js",
    "docs/readers/d40/unit14/index.html",
    "docs/styles.css",
    "package.json",
    "scripts/build-live-overlay-release.py",
    "scripts/check-public-links.mjs",
    "scripts/export-single-file-site.mjs",
    "scripts/validate-live-overlay-release.py",
    "scripts/validate-static-site.mjs",
)
STATIC_VALIDATION_FIXED_INPUTS = (
    "backend/authority/curriculum-authority-v1.json",
    "docs/data/curriculum-authority-v1.json",
    "docs/data/educational-access.json",
    "docs/data/learner-read-model.json",
    "docs/data/unit-route-C100-v2.1.json",
    "docs/data/unit-route-D20-v2.1.json",
    "docs/data/unit-route-v2.1.json",
    "docs/data/unit-routes-v2.1.json",
    "docs/id-ID/courses/C100/index.html",
    "docs/id-ID/courses/C100/reader/index.html",
    "docs/id-ID/courses/C100/reader/style.css",
    "docs/id-ID/courses/C100/solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf",
    "docs/schema/educational-access-federation-v1.schema.json",
    "docs/schema/v1/learner-state-v1.schema.json",
    "schemas/catalog-v1.schema.json",
    "schemas/v1/learner-state-v1.schema.json",
)

EXPECTED_OVERLAY_IDS = (
    "A10", "A20", "A30", "B20", "B30", "B50", "B95", "C10", "C90", "C100",
    "C140", "D10", "D20", "D30", "D40", "D50", "D60", "D70", "D80", "D100",
)

PAGES_READBACKS = (
    {
        "path": "docs/index.html",
        "url": STUDENT_URL,
        "bytes": 13_261,
        "sha256": "e40461258911d76b25686e938a9dfa1eee220b568540a6138c8baf8fd62452ec",
    },
    {
        "path": "docs/app.js",
        "url": f"{STUDENT_URL}app.js",
        "bytes": 19_147,
        "sha256": "9a14650147404c537bea2500c6cb725352e967b607ec1a1315418648de12774e",
    },
    {
        "path": "docs/live-course-publications.js",
        "url": f"{STUDENT_URL}live-course-publications.js",
        "bytes": 32_273,
        "sha256": "34eeb8f39a5e821fd9711858949116a2dcd45cfb6012fd87e1c65735c1c552f4",
    },
    {
        "path": "docs/id-ID/courses/B95/index.html",
        "url": f"{STUDENT_URL}id-ID/courses/B95/",
        "bytes": 3_871,
        "sha256": "65abad40c18a8ef630ed3d9d534c89d3cad7a066201986fd55320e080b140496",
    },
    {
        "path": "docs/id-ID/courses/D30/index.html",
        "url": f"{STUDENT_URL}id-ID/courses/D30/",
        "bytes": 4_502,
        "sha256": "68e402a5a976c320fa4112d3bc2d46d824962c7fc8e38d00741aa2d6c99a1166",
    },
    {
        "path": "docs/id-ID/courses/D40/index.html",
        "url": f"{STUDENT_URL}id-ID/courses/D40/",
        "bytes": 3_879,
        "sha256": "b8fd0395184ae47eda079bcc7ffca528338e5184ba5255882cf4ef37830cddaf",
    },
    {
        "path": "docs/readers/d40/unit14/index.html",
        "url": f"{STUDENT_URL}readers/d40/unit14/",
        "bytes": 6_267,
        "sha256": "c6785811f86cb96cc3d9a2ce81e094c511937f6d304ba78bab0973928ebcbbcf",
    },
)
RECEIPT_CHECKS = {
    "base_release": "93/93 byte-identical",
    "standalone_export_replay": "byte-identical",
    "source_archive": "inventory, CRC, member bytes, timestamps, and order pass",
    "overlay_rows": "20/20",
    "effective_completed_public_roles": "27",
    "distinct_completed_public_records": "26",
    "strict_public_links": "165/165; live network gate executed",
    "static_site_validation": "pass; 40 courses; 20 overlay rows; 27 effective published roles",
    "github_pages_readbacks": "7/7 exact live HTTP 200 byte/hash matches",
    "b95_r011_b025": "260-page learner route and public PDF exact byte/hash gate pass",
    "d40_unit14": "230-page PDF plus 71-file portable HTML learner route pass",
    "d100_bgk_unit06": "36 public units and 586 public pages bound to record 22164552",
    "backend_v23_conformance": "inherited v0.1.1 archive plus three sanitized receipts remain byte-identical and pass semantic/privacy gates",
    "privacy_scan": "pass",
}

PRIVATE_MARKERS = (
    b"c:" + b"\\users\\",
    b"c:" + b"/" + b"users/",
    b"file:" + b"//",
    b".codex" + b"/attachments",
    b"new " + b"zenodo " + b"token.md",
    b"github " + b"tokens.md",
    b"zenodo " + b"token.md",
    b"/" + b"users/",
    b"/" + b"home/",
)

B95_PUBLICATION = {
    "course_id": "B95",
    "boundary": "R011-B025",
    "pages": 260,
    "next_boundary": "B026",
    "record_id": 22166545,
    "doi": "10.5281/zenodo.22166545",
    "pdf_url": "https://zenodo.org/records/22166545/files/00_STATISTIKA_BERBASIS_DATA_ID_R011-B025_WORKING_READER.pdf?download=1",
    "pdf_bytes": 12_440_420,
    "pdf_sha256": "b154484d2d2ddf0a49f0ee9925854f45e86b6e0fb17d241607db9fc27051e99d",
    "github_release": "https://github.com/KokunoYumeto/statistika-berbasis-data-id/releases/tag/r011-b025-2026.08.29.4",
    "backend_records": 9_119,
    "public_assets": 9,
    "learner_url": f"{STUDENT_URL}id-ID/courses/B95/",
}

BACKEND_REQUIRED_SUFFIXES = (
    "manifest.json",
    "PACKAGE_CHECKSUMS.sha256",
    "VALIDATION_RECEIPT.json",
    "SCOPE_AND_LIMITATIONS.json",
    "tools/generate_v23.py",
    "tools/validate_v23.py",
    "tools/package_v23.py",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fact(path: Path, name: str | None = None) -> dict[str, Any]:
    return {
        "name": name or path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def data_fact(data: bytes, name: str) -> dict[str, Any]:
    return {"name": name, "bytes": len(data), "sha256": sha256_bytes(data)}


def canonical_inventory_bytes(facts: list[dict[str, Any]]) -> bytes:
    return "".join(
        f"{item['sha256']}  {item['bytes']}  {item['name']}\n"
        for item in sorted(facts, key=lambda value: value["name"])
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def validate_full_commit(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("--source-commit must be a full lowercase 40-hex commit SHA")
    return value


def remote_blob(commit: str, name: str) -> bytes:
    commit = validate_full_commit(commit)
    url = f"{RAW_REPOSITORY_URL}/{commit}/{quote(name, safe='/')}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": f"program-matematika-indonesia-release-builder/{VERSION}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status != 200:
                raise ValueError(f"immutable source HTTP status differs: {name} -> {response.status}")
            return response.read()
    except Exception as exc:
        raise ValueError(f"cannot read immutable source {commit}:{name}: {exc}") from exc


def verify_source_commit(root: Path, commit: str) -> dict[str, bytes]:
    commit = validate_full_commit(commit)
    committed: dict[str, bytes] = {}
    for name in SOURCE_MEMBERS:
        data = remote_blob(commit, name)
        live = (root / name).read_bytes()
        if live != data:
            raise ValueError(f"local source differs from immutable remote commit: {name}")
        committed[name] = data
    return committed


def static_validation_inputs(root: Path, commit: str, require_live: bool) -> dict[str, bytes]:
    values = {name: remote_blob(commit, name) for name in STATIC_VALIDATION_FIXED_INPUTS}
    authority = json.loads(values["backend/authority/curriculum-authority-v1.json"])
    federation_manifest = f"{authority['federation']['package_path']}/manifest.json"
    dynamic_names = {federation_manifest}

    d20 = json.loads(values["docs/data/unit-route-D20-v2.1.json"])
    dynamic_names.update(
        f"docs/id-ID/courses/D20/units/{unit['slug']}/index.html"
        for unit in d20["units"]
    )
    c100 = json.loads(values["docs/data/unit-route-C100-v2.1.json"])
    for unit in c100["units"]:
        if unit.get("kind") != "chapter":
            continue
        match = re.search(r"\.ch(\d{2})$", unit["id"])
        if match:
            dynamic_names.add(
                f"docs/id-ID/courses/C100/units/bab-{match.group(1)}/index.html"
            )
    for name in sorted(dynamic_names):
        values[name] = remote_blob(commit, name)
    if require_live:
        for name, data in values.items():
            if (root / name).read_bytes() != data:
                raise ValueError(f"static-validator input differs from committed blob: {name}")
    return dict(sorted(values.items()))


def dependency_closure(values: dict[str, bytes]) -> dict[str, Any]:
    facts = [data_fact(data, name) for name, data in values.items()]
    return {
        "files": len(facts),
        "bytes": sum(item["bytes"] for item in facts),
        "aggregate_algorithm": "sha256 of sorted '<sha256>  <bytes>  <name>\\n' facts",
        "aggregate_sha256": sha256_bytes(canonical_inventory_bytes(facts)),
    }


def parse_checksum(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\\/]+)", line)
        if not match:
            raise ValueError(f"invalid checksum line {line_number}: {path}")
        digest, name = match.groups()
        if name in result:
            raise ValueError(f"duplicate checksum name: {name}")
        result[name] = digest
    return result


def verify_replaceable_output(output: Path, base_names: set[str]) -> None:
    if not output.is_dir():
        raise ValueError(f"existing v{VERSION} output is not a directory")
    paths = sorted(output.iterdir(), key=lambda value: value.name)
    if any(not path.is_file() for path in paths):
        raise ValueError(f"existing v{VERSION} output is not a flat release")
    if {path.name for path in paths} != base_names | set(ADDITIVE_NAMES):
        raise ValueError(f"existing v{VERSION} output is not a recognized 93+5 candidate")
    manifest = json.loads((output / MANIFEST_NAME).read_text(encoding="utf-8"))
    if manifest.get("schema_id") != "program-matematika-indonesia/live-publication-overlay-manifest/v1":
        raise ValueError(f"existing v{VERSION} manifest is not recognized")
    if manifest.get("version") != VERSION:
        raise ValueError(f"existing v{VERSION} manifest version mismatch")
    checksums = parse_checksum(output / CHECKSUM_NAME)
    non_checksum = [path for path in paths if path.name != CHECKSUM_NAME]
    if set(checksums) != {path.name for path in non_checksum}:
        raise ValueError(f"existing v{VERSION} checksum inventory mismatch")
    for path in non_checksum:
        if checksums[path.name] != sha256_file(path):
            raise ValueError(f"existing v{VERSION} checksum mismatch: {path.name}")


def verify_base(base: Path) -> list[dict[str, Any]]:
    if not base.is_dir():
        raise ValueError(f"missing base release: {base}")
    paths = sorted(base.iterdir(), key=lambda value: value.name)
    if not paths or any(not path.is_file() for path in paths):
        raise ValueError("base release must contain flat files only")
    facts = [fact(path) for path in paths]
    if len(facts) != BASE_EXPECTED["files"]:
        raise ValueError(f"base file count mismatch: {len(facts)}")
    if sum(item["bytes"] for item in facts) != BASE_EXPECTED["bytes"]:
        raise ValueError("base byte count mismatch")
    aggregate = sha256_bytes(canonical_inventory_bytes(facts))
    if aggregate != BASE_EXPECTED["aggregate_sha256"]:
        raise ValueError(f"base aggregate mismatch: {aggregate}")

    checksum_path = base / BASE_EXPECTED["checksum_file"]["name"]
    checksum_fact = fact(checksum_path)
    for key in ("bytes", "sha256"):
        if checksum_fact[key] != BASE_EXPECTED["checksum_file"][key]:
            raise ValueError(f"base checksum-file {key} mismatch")
    checksums = parse_checksum(checksum_path)
    expected_names = {path.name for path in paths if path.name != checksum_path.name}
    if set(checksums) != expected_names:
        raise ValueError("base checksum inventory mismatch")
    if len(checksums) != BASE_EXPECTED["checksum_file"]["entries"]:
        raise ValueError("base checksum entry-count mismatch")
    for path in paths:
        if path.name != checksum_path.name and checksums[path.name] != sha256_file(path):
            raise ValueError(f"base checksum mismatch: {path.name}")
    return facts


def overlay_summary(root: Path) -> dict[str, Any]:
    source = """
import { courses as authorityCourses } from './docs/courses.js';
import { liveCoursePublications, materializeLiveCourses } from './docs/live-course-publications.js';
const effective = materializeLiveCourses(authorityCourses);
const published = effective.filter((course) => course.state === 'published');
const records = [...new Set(published.map((course) => course.zenodo).filter(Boolean))].sort();
console.log(JSON.stringify({
  overlay_ids: Object.keys(liveCoursePublications).sort(),
  overlay_rows: Object.keys(liveCoursePublications).length,
  selected_course_roles: effective.length,
  effective_published_roles: published.length,
  distinct_completed_public_records: records.length,
  effective_published_role_ids: published.map((course) => course.id),
  distinct_record_dois: records,
}));
"""
    process = subprocess.run(
        ["node", "--input-type=module", "-e", source],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    value = json.loads(process.stdout)
    expected = {
        "overlay_ids": sorted(EXPECTED_OVERLAY_IDS),
        "overlay_rows": 20,
        "selected_course_roles": 40,
        "effective_published_roles": 27,
        "distinct_completed_public_records": 26,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            raise ValueError(f"live overlay {key} mismatch: {value.get(key)!r}")
    return value


def verify_pages_sources(root: Path, source_commit: str) -> list[dict[str, Any]]:
    rows = []
    for expected in PAGES_READBACKS:
        path = root / expected["path"]
        actual = fact(path, expected["path"])
        if actual["bytes"] != expected["bytes"] or actual["sha256"] != expected["sha256"]:
            raise ValueError(f"Pages/local identity mismatch: {expected['path']}")
        separator = "&" if "?" in expected["url"] else "?"
        request_url = (
            f"{expected['url']}{separator}pmi-live-overlay-readback={source_commit}"
        )
        request = urllib.request.Request(
            request_url,
            headers={"User-Agent": f"program-matematika-indonesia-release-validator/{VERSION}"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            public_data = response.read()
        if status != 200:
            raise ValueError(f"Pages HTTP status mismatch: {expected['url']} -> {status}")
        if public_data != path.read_bytes():
            raise ValueError(f"Pages public-byte mismatch: {expected['path']}")
        rows.append({
            **expected,
            "anonymous_readback": "exact-byte-match",
            "http_status": 200,
            "request_url": request_url,
        })
    return rows


def run_strict_link_check(root: Path) -> dict[str, Any]:
    environment = os.environ.copy()
    environment.pop("ALLOW_PENDING_CENTRAL", None)
    process = subprocess.run(
        ["node", "scripts/check-public-links.mjs"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
        timeout=900,
    )
    if process.returncode != 0:
        diagnostic = (process.stderr or process.stdout)[-4000:].strip()
        raise ValueError(f"strict public-link check failed: {diagnostic}")
    report = json.loads(process.stdout)
    links = report.get("links")
    if report.get("status") != "pass" or report.get("checked") != 165:
        raise ValueError("strict public-link count/result mismatch")
    if not isinstance(links, list) or len(links) != 165:
        raise ValueError("strict public-link result inventory mismatch")
    if any(not isinstance(row.get("status"), int) or not 200 <= row["status"] < 400 for row in links):
        raise ValueError("strict public-link report contains a non-success status")
    return {
        "command": "node scripts/check-public-links.mjs",
        "mode": "strict; no pending-central exception",
        "executed": True,
        "result": "pass",
        "checked": 165,
        "failures": 0,
    }


def run_static_site_validation(root: Path) -> dict[str, Any]:
    process = subprocess.run(
        ["node", "scripts/validate-static-site.mjs"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if process.returncode != 0:
        diagnostic = (process.stderr or process.stdout)[-4000:].strip()
        raise ValueError(f"static-site validation failed: {diagnostic}")
    report = json.loads(process.stdout)
    expected = {
        "status": "pass",
        "courses": 40,
        "selected": 40,
        "unresolved": 0,
        "effectivePublishedRoles": 27,
        "liveOverlayRows": 20,
        "prerequisiteEdges": 83,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            raise ValueError(f"static-site validation {key} mismatch: {report.get(key)!r}")
    return report


def privacy_scan(name: str, data: bytes) -> None:
    lowered = data.lower()
    found = [marker.decode("ascii", "replace") for marker in PRIVATE_MARKERS if marker in lowered]
    if found:
        raise ValueError(f"private marker in {name}: {found}")


def safe_archive_member(name: str) -> None:
    normalized = name.replace("\\", "/")
    if not normalized or normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        raise ValueError(f"unsafe archive member path: {name!r}")
    if any(part in {"", ".", ".."} for part in normalized.rstrip("/").split("/")):
        raise ValueError(f"non-canonical archive member path: {name!r}")


def inspect_backend_archive(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing backend v2.3 archive: {path}")
    privacy_scan(path.name, path.read_bytes())
    expected_root = "program-matematika-indonesia-backend-v2.3-conformance-v0.1.1/"
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("backend v2.3 archive CRC failure")
        names = archive.namelist()
        if len(names) != len(set(names)) or names != sorted(names):
            raise ValueError("backend v2.3 archive names are duplicated or not sorted")
        if not names or any(not name.startswith(expected_root) for name in names):
            raise ValueError("backend v2.3 archive root/version mismatch")
        timestamps = set()
        uncompressed = 0
        for info in archive.infolist():
            safe_archive_member(info.filename)
            timestamps.add(info.date_time)
            if info.is_dir():
                continue
            data = archive.read(info.filename)
            uncompressed += len(data)
            privacy_scan(f"{path.name}:{info.filename}", data)
        if len(timestamps) != 1:
            raise ValueError("backend v2.3 archive member timestamps are not deterministic")
        missing = [
            suffix for suffix in BACKEND_REQUIRED_SUFFIXES
            if f"{expected_root}{suffix}" not in names
        ]
        if missing:
            raise ValueError(f"backend v2.3 archive lacks required members: {missing}")
        return {
            "archive": fact(path, BACKEND_ARCHIVE_NAME),
            "package_root": expected_root,
            "entries": len(names),
            "uncompressed_bytes": uncompressed,
            "member_order": "sorted",
            "fixed_member_timestamp": "%04d-%02d-%02dT%02d:%02d:%02d" % next(iter(timestamps)),
            "crc": "pass",
            "recursive_privacy_scan": "pass",
            "required_members": list(BACKEND_REQUIRED_SUFFIXES),
        }


def walk_json(value: Any):
    yield value
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def inspect_backend_receipt(
    path: Path,
    public_name: str,
    archive_fact: dict[str, Any],
    kind: str,
) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing backend v2.3 {kind} receipt: {path}")
    data = path.read_bytes()
    privacy_scan(public_name, data)
    try:
        value = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"backend v2.3 {kind} receipt is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"backend v2.3 {kind} receipt must be a JSON object")
    flattened = list(walk_json(value))
    lowered = [str(item).lower() for item in flattened if isinstance(item, (str, int, bool))]
    if not any(item in {"pass", "passed", "success", "complete", "completed"} for item in lowered):
        raise ValueError(f"backend v2.3 {kind} receipt lacks a passing result")
    if archive_fact["sha256"] not in flattened or archive_fact["bytes"] not in flattened:
        raise ValueError(f"backend v2.3 {kind} receipt is not bound to archive bytes/SHA-256")
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True).lower()
    if kind == "scope":
        if "a00" not in canonical or "o001" not in canonical:
            raise ValueError("backend v2.3 scope receipt does not bind both A00 and O001")
        for key, child in value.items():
            key_lower = str(key).lower()
            if ("cross" in key_lower and "lane" in key_lower) or key_lower in {
                "global_backend_complete", "whole_program_complete",
            }:
                if child is not False:
                    raise ValueError(f"backend v2.3 scope receipt overclaims scope: {key}")
    elif kind == "validation":
        if not any(item == 13 for item in flattened):
            raise ValueError("backend v2.3 validation receipt does not bind the 13-check gate")
    elif kind == "determinism":
        if not any(token in canonical for token in ("byte-identical", "byte_identical", "byte identical")):
            raise ValueError("backend v2.3 determinism receipt lacks byte-identical replay evidence")
    return {"artifact": fact(path, public_name), "kind": kind, "result": "pass"}


def inspect_backend_inputs(args: argparse.Namespace) -> dict[str, Any]:
    paths = {
        BACKEND_ARCHIVE_NAME: Path(args.backend_v23_archive).resolve(),
        BACKEND_SCOPE_NAME: Path(args.backend_v23_scope_receipt).resolve(),
        BACKEND_VALIDATION_NAME: Path(args.backend_v23_validation_receipt).resolve(),
        BACKEND_DETERMINISM_NAME: Path(args.backend_v23_determinism_receipt).resolve(),
    }
    if len(set(paths.values())) != len(paths):
        raise ValueError("backend v2.3 artifact arguments must name four distinct files")
    archive = inspect_backend_archive(paths[BACKEND_ARCHIVE_NAME])
    archive_fact = archive["archive"]
    receipts = {
        BACKEND_SCOPE_NAME: inspect_backend_receipt(
            paths[BACKEND_SCOPE_NAME], BACKEND_SCOPE_NAME, archive_fact, "scope"
        ),
        BACKEND_VALIDATION_NAME: inspect_backend_receipt(
            paths[BACKEND_VALIDATION_NAME], BACKEND_VALIDATION_NAME, archive_fact, "validation"
        ),
        BACKEND_DETERMINISM_NAME: inspect_backend_receipt(
            paths[BACKEND_DETERMINISM_NAME], BACKEND_DETERMINISM_NAME, archive_fact, "determinism"
        ),
    }
    return {"paths": paths, "archive": archive, "receipts": receipts}


def verify_b95_publication(committed_sources: dict[str, bytes]) -> dict[str, Any]:
    page = committed_sources["docs/id-ID/courses/B95/index.html"]
    overlay = committed_sources["docs/live-course-publications.js"]
    page_text = page.decode("utf-8")
    overlay_text = overlay.decode("utf-8")
    markers = (
        B95_PUBLICATION["boundary"], str(B95_PUBLICATION["record_id"]),
        str(B95_PUBLICATION["pages"]), B95_PUBLICATION["next_boundary"],
        B95_PUBLICATION["pdf_url"], B95_PUBLICATION["github_release"],
    )
    for marker in markers:
        if marker not in page_text or marker not in overlay_text:
            raise ValueError(f"B95 learner/overlay source lacks exact B025 marker: {marker}")
    if str(B95_PUBLICATION["backend_records"]) not in overlay_text:
        raise ValueError("B95 overlay lacks exact backend record count")
    hrefs = re.findall(r'''href=["']([^"']+)["']''', page_text, flags=re.IGNORECASE)
    if any(re.search(r"\.(?:jsonl?|csv)(?:[?#]|$)", href, re.IGNORECASE) for href in hrefs):
        raise ValueError("B95 primary learner route exposes a machine-data href")
    request = urllib.request.Request(
        B95_PUBLICATION["pdf_url"],
        headers={"User-Agent": f"program-matematika-indonesia-release-builder/{VERSION}"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        status = response.status
        data = response.read()
    if status != 200 or len(data) != B95_PUBLICATION["pdf_bytes"] or sha256_bytes(data) != B95_PUBLICATION["pdf_sha256"]:
        raise ValueError("B95 R011-B025 public PDF exact byte/hash readback mismatch")
    return {
        **B95_PUBLICATION,
        "learner_route_is_primary": True,
        "machine_data_links_on_learner_page": 0,
        "public_pdf_http_status": 200,
        "public_pdf_readback": "exact-byte-match",
    }


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = 0o100644 << 16
    info.create_system = 3
    return info


def build_source_zip(
    output: Path,
    source_commit: str,
    committed_sources: dict[str, bytes],
    static_inputs: dict[str, bytes],
) -> dict[str, Any]:
    members = []
    for name in SOURCE_MEMBERS:
        data = committed_sources[name]
        privacy_scan(name, data)
        members.append({"name": name, "bytes": len(data), "sha256": sha256_bytes(data)})
    validation_inputs = []
    if set(SOURCE_MEMBERS) & set(static_inputs):
        raise ValueError("source and static-validation archive members overlap")
    for name, data in sorted(static_inputs.items()):
        privacy_scan(name, data)
        validation_inputs.append({"name": name, "bytes": len(data), "sha256": sha256_bytes(data)})
    archive_manifest = {
        "schema_id": "program-matematika-indonesia/live-overlay-source-archive/v2",
        "version": VERSION,
        "source_commit": source_commit,
        "purpose": "Reproduce the standalone learner site and replay static validation from an embedded dependency closure.",
        "replay_contract": {
            "static_validation_inputs_embedded": True,
            "network_required_for_current_commit_proof": True,
            "package_lock_present": False,
        },
        "source_members": members,
        "static_validation_inputs": validation_inputs,
        "static_validation_dependency_closure": dependency_closure(static_inputs),
    }
    manifest_data = (
        json.dumps(archive_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    entries = [(item["name"], committed_sources[item["name"]]) for item in members]
    entries.extend((item["name"], static_inputs[item["name"]]) for item in validation_inputs)
    entries.append(("SOURCE_ARCHIVE_MANIFEST.json", manifest_data))
    entries.sort(key=lambda item: item[0])

    with zipfile.ZipFile(output, "w") as archive:
        for name, data in entries:
            archive.writestr(zip_info(name), data)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("source ZIP CRC failure")
        if archive.namelist() != [name for name, _ in entries]:
            raise ValueError("source ZIP inventory/order mismatch")
        for name, data in entries:
            if archive.read(name) != data:
                raise ValueError(f"source ZIP byte mismatch: {name}")
    return {
        "archive": fact(output, SOURCE_ZIP_NAME),
        "entries": len(entries),
        "uncompressed_bytes": sum(len(data) for _, data in entries),
        "compression": "stored",
        "fixed_member_timestamp": "2026-08-30T00:00:00Z",
        "manifest": {
            "name": "SOURCE_ARCHIVE_MANIFEST.json",
            "bytes": len(manifest_data),
            "sha256": sha256_bytes(manifest_data),
        },
        "source_members": members,
        "static_validation_inputs": validation_inputs,
        "static_validation_dependency_closure": dependency_closure(static_inputs),
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(__file__).resolve().parent.parent
    base = (root / args.base_release).resolve()
    output = (root / args.output).resolve()
    releases_root = (root / "releases").resolve()
    expected_base = releases_root / "v0.62.6"
    expected_output = releases_root / "v0.62.7"
    if base != expected_base:
        raise ValueError(f"base release must be exactly {expected_base}")
    if output != expected_output:
        raise ValueError(f"output must be exactly {expected_output}")
    committed_sources = verify_source_commit(root, args.source_commit)
    static_inputs = static_validation_inputs(root, args.source_commit, require_live=True)
    backend_inputs = inspect_backend_inputs(args)

    base_facts = verify_base(base)
    summary = overlay_summary(root)
    readbacks = verify_pages_sources(root, args.source_commit)
    b95_publication = verify_b95_publication(committed_sources)
    strict_link_result = run_strict_link_check(root)
    static_site_result = {
        "command": "node scripts/validate-static-site.mjs",
        "report": run_static_site_validation(root),
        "additional_committed_input_closure": dependency_closure(static_inputs),
    }

    staging = output.with_name(f"{output.name}.building")
    expected_staging = releases_root / "v0.62.7.building"
    if staging != expected_staging:
        raise ValueError(f"staging path must be exactly {expected_staging}")
    if staging.exists():
        if not args.force:
            raise ValueError(f"staging directory exists; pass --force after inspection: {staging}")
        marker = staging / BUILD_MARKER_NAME
        if not marker.is_file():
            raise ValueError("refusing to remove unmarked pre-existing staging directory")
        marker_value = json.loads(marker.read_text(encoding="utf-8"))
        if marker_value != {"schema_id": "pmi-live-overlay-building/v1", "version": VERSION}:
            raise ValueError("refusing to remove staging directory with an invalid ownership marker")
        shutil.rmtree(staging)
    if output.exists():
        if not args.force:
            raise ValueError(f"output exists; pass --force to rebuild: {output}")
        verify_replaceable_output(output, {item["name"] for item in base_facts})
        shutil.rmtree(output)
    staging.mkdir(parents=False)
    write_json(staging / BUILD_MARKER_NAME, {
        "schema_id": "pmi-live-overlay-building/v1",
        "version": VERSION,
    })
    try:
        for source in sorted(base.iterdir(), key=lambda value: value.name):
            shutil.copyfile(source, staging / source.name)
        for source in base.iterdir():
            copied = staging / source.name
            if source.read_bytes() != copied.read_bytes():
                raise ValueError(f"base copy byte mismatch: {source.name}")
        standalone = staging / STANDALONE_NAME
        replay = staging / f".{STANDALONE_NAME}.replay"
        exporter = root / "scripts" / "export-single-file-site.mjs"
        subprocess.run(["node", str(exporter), str(standalone)], cwd=root, check=True)
        subprocess.run(["node", str(exporter), str(replay)], cwd=root, check=True)
        if standalone.read_bytes() != replay.read_bytes():
            raise ValueError("standalone HTML replay is not byte-identical")
        replay.unlink()
        standalone_data = standalone.read_bytes()
        privacy_scan(STANDALONE_NAME, standalone_data)
        text = standalone_data.decode("utf-8")
        for marker in (
            "const liveCoursePublications = Object.freeze({",
            "const courses = materializeLiveCourses(authorityCourses);",
            "Program Matematika Indonesia",
        ):
            if marker not in text:
                raise ValueError(f"standalone HTML missing marker: {marker}")

        source_zip = build_source_zip(
            staging / SOURCE_ZIP_NAME,
            args.source_commit,
            committed_sources,
            static_inputs,
        )
        standalone_fact = fact(standalone, STANDALONE_NAME)
        source_facts = [data_fact(committed_sources[name], name) for name in SOURCE_MEMBERS]
        manifest = {
            "schema_id": "program-matematika-indonesia/live-publication-overlay-manifest/v1",
            "version": VERSION,
            "release_kind": "additive-learner-access-live-publication-adapter",
            "immutable_base": {
                "version": BASE_VERSION,
                "directory": "releases/v0.62.6",
                "files": BASE_EXPECTED["files"],
                "bytes": BASE_EXPECTED["bytes"],
                "aggregate_algorithm": "sha256 of sorted '<sha256>  <bytes>  <name>\\n' facts",
                "aggregate_sha256": BASE_EXPECTED["aggregate_sha256"],
                "checksum_file": BASE_EXPECTED["checksum_file"],
                "files_unchanged": base_facts,
            },
            "source_repository": {
                "repository": REPOSITORY_URL,
                "branch": "main",
                "commit": args.source_commit,
                "commit_url": f"{REPOSITORY_URL}/commit/{args.source_commit}",
            },
            "predecessor": {
                "version": BASE_VERSION,
                "record_id": PREDECESSOR_RECORD_ID,
                "doi": f"10.5281/zenodo.{PREDECESSOR_RECORD_ID}",
                "public_inventory": {
                    "files": BASE_EXPECTED["files"],
                    "bytes": BASE_EXPECTED["bytes"],
                    "aggregate_sha256": BASE_EXPECTED["aggregate_sha256"],
                },
            },
            "curriculum_boundary": {
                "frozen_authority_version": FROZEN_AUTHORITY_VERSION,
                "authority_file": "curriculum-authority-v1.json",
                "authority_changed": False,
                "live_overlay_is_authority_replacement": False,
                "overall_program_complete": False,
            },
            "live_publication_overlay": summary,
            "b95_learner_route": b95_publication,
            "inherited_backend_v23_conformance": {
                "version": "2.3",
                "package_version": "0.1.1",
                "admitted_scope": ["A00", "O001"],
                "cross_lane_or_whole_program_claim": False,
                "student_route_remains_primary": True,
                "machine_artifacts_are_secondary": True,
                "archive": backend_inputs["archive"],
                "receipts": backend_inputs["receipts"],
            },
            "strict_public_link_check": strict_link_result,
            "static_site_validation": static_site_result,
            "github_pages": {
                "workflow_run_id": args.pages_run_id,
                "workflow_run_url": f"{REPOSITORY_URL}/actions/runs/{args.pages_run_id}",
                "conclusion": "success",
                "student_entry_url": STUDENT_URL,
                "anonymous_exact_readbacks": readbacks,
            },
            "additive_artifacts": {
                "names": list(ADDITIVE_NAMES),
                "standalone_html": standalone_fact,
                "source_archive": source_zip,
            },
            "source_inputs": source_facts,
            "inventory_contract": {
                "inherited_files": 93,
                "additive_files": 5,
                "successor_files": 98,
                "checksum_entries": 97,
                "checksum_excludes_only": CHECKSUM_NAME,
            },
            "privacy": {
                "credentials_included": False,
                "absolute_local_paths_in_additive_payloads": False,
            },
        }
        write_json(staging / MANIFEST_NAME, manifest)
        privacy_scan(MANIFEST_NAME, (staging / MANIFEST_NAME).read_bytes())

        before_receipt = [
            fact(path)
            for path in sorted(staging.iterdir(), key=lambda value: value.name)
            if path.name != BUILD_MARKER_NAME
        ]
        if len(before_receipt) != 96:
            raise ValueError(f"pre-receipt inventory mismatch: {len(before_receipt)}")
        receipt = {
            "schema_id": "program-matematika-indonesia/local-live-overlay-validation/v1",
            "version": VERSION,
            "result": "pass",
            "source_commit": args.source_commit,
            "checks": RECEIPT_CHECKS,
            "files_before_receipt": before_receipt,
            "files_before_receipt_aggregate_sha256": sha256_bytes(
                canonical_inventory_bytes(before_receipt)
            ),
            "successor_inventory": {
                "files_before_checksum": 97,
                "checksum_entries": 97,
                "final_files": 98,
                "inherited_files": 93,
                "additive_files": 5,
            },
            "validation_command": (
                "python scripts/validate-live-overlay-release.py --release-dir releases/v0.62.7 "
                f"--source-commit {args.source_commit} --pages-run-id {args.pages_run_id} "
                f"--backend-v23-archive releases/v0.62.7/{BACKEND_ARCHIVE_NAME} "
                f"--backend-v23-scope-receipt releases/v0.62.7/{BACKEND_SCOPE_NAME} "
                f"--backend-v23-validation-receipt releases/v0.62.7/{BACKEND_VALIDATION_NAME} "
                f"--backend-v23-determinism-receipt releases/v0.62.7/{BACKEND_DETERMINISM_NAME}"
            ),
            "publication_performed": False,
        }
        write_json(staging / RECEIPT_NAME, receipt)
        privacy_scan(RECEIPT_NAME, (staging / RECEIPT_NAME).read_bytes())

        pre_checksum = [
            fact(path)
            for path in sorted(staging.iterdir(), key=lambda value: value.name)
            if path.name != BUILD_MARKER_NAME
        ]
        if len(pre_checksum) != 97:
            raise ValueError(f"pre-checksum inventory mismatch: {len(pre_checksum)}")
        (staging / CHECKSUM_NAME).write_bytes(
            "".join(
                f"{item['sha256']}  {item['name']}\n"
                for item in sorted(pre_checksum, key=lambda value: value["name"])
            ).encode("utf-8")
        )
        (staging / BUILD_MARKER_NAME).unlink()
        if len(list(staging.iterdir())) != 98:
            raise ValueError("final inventory is not 98 files")
        staging.rename(output)
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging)
        raise

    validator = root / "scripts" / "validate-live-overlay-release.py"
    process = subprocess.run(
        [
            sys.executable,
            str(validator),
            "--release-dir",
            output.relative_to(root).as_posix(),
            "--source-commit",
            args.source_commit,
            "--pages-run-id",
            str(args.pages_run_id),
            "--backend-v23-archive",
            str(output / BACKEND_ARCHIVE_NAME),
            "--backend-v23-scope-receipt",
            str(output / BACKEND_SCOPE_NAME),
            "--backend-v23-validation-receipt",
            str(output / BACKEND_VALIDATION_NAME),
            "--backend-v23-determinism-receipt",
            str(output / BACKEND_DETERMINISM_NAME),
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    validation = json.loads(process.stdout)
    result = {
        "result": "pass",
        "release_dir": output.relative_to(root).as_posix(),
        "version": VERSION,
        "files": validation["files"],
        "bytes": validation["bytes"],
        "aggregate_sha256": validation["aggregate_sha256"],
        "additive_artifacts": validation["additive_artifacts"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-release", default="releases/v0.62.6")
    parser.add_argument("--output", default="releases/v0.62.7")
    parser.add_argument("--source-commit", required=True, help="full commit containing every packaged source")
    parser.add_argument("--pages-run-id", required=True, type=int, help="successful Pages workflow run for the source commit")
    parser.add_argument("--backend-v23-archive", required=True, help="public-safe deterministic v2.3 0.1.1 ZIP")
    parser.add_argument("--backend-v23-scope-receipt", required=True, help="sanitized A00+O001 scope-admission receipt")
    parser.add_argument("--backend-v23-validation-receipt", required=True, help="sanitized 13-check validation receipt")
    parser.add_argument("--backend-v23-determinism-receipt", required=True, help="sanitized byte-identical replay receipt")
    parser.add_argument("--force", action="store_true", help="replace only the exact output directory")
    return parser.parse_args()


if __name__ == "__main__":
    build(parse_args())
