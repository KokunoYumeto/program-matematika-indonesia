#!/usr/bin/env python3
"""Validate the deterministic v0.62.7 learner-access overlay release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from urllib.parse import quote
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


VERSION = "0.62.7"
BASE_VERSION = "0.62.6"
FROZEN_AUTHORITY_VERSION = "0.62.0"
PREDECESSOR_RECORD_ID = 22167050
STUDENT_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
REPOSITORY_URL = "https://github.com/KokunoYumeto/program-matematika-indonesia"
RAW_REPOSITORY_URL = "https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia"
FIXED_ZIP_TIME = (2026, 8, 30, 0, 0, 0)
BASE_EXPECTED = {
    "files": 93,
    "bytes": 65_639_635,
    "aggregate_sha256": "fa825a88b10c37ff7897554b15197db993a40993cf3ac3b949e317ff3305f84b",
    "checksum_name": "LIVE_OVERLAY_CHECKSUMS_v0.62.6.sha256",
    "checksum_bytes": 10_357,
    "checksum_entries": 92,
    "checksum_sha256": "aec9d227250150fb0221bcdabff6811320ea2f27287cece72d40c999b58ccef2",
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
EXPECTED_OVERLAY_IDS = sorted((
    "A10", "A20", "A30", "B20", "B30", "B50", "B95", "C10", "C90", "C100",
    "C140", "D10", "D20", "D30", "D40", "D50", "D60", "D70", "D80", "D100",
))
PAGES_IDENTITIES = {
    "docs/index.html": (13_261, "e40461258911d76b25686e938a9dfa1eee220b568540a6138c8baf8fd62452ec"),
    "docs/app.js": (19_147, "9a14650147404c537bea2500c6cb725352e967b607ec1a1315418648de12774e"),
    "docs/live-course-publications.js": (32_273, "34eeb8f39a5e821fd9711858949116a2dcd45cfb6012fd87e1c65735c1c552f4"),
    "docs/id-ID/courses/B95/index.html": (3_871, "65abad40c18a8ef630ed3d9d534c89d3cad7a066201986fd55320e080b140496"),
    "docs/id-ID/courses/D30/index.html": (4_502, "68e402a5a976c320fa4112d3bc2d46d824962c7fc8e38d00741aa2d6c99a1166"),
    "docs/id-ID/courses/D40/index.html": (3_879, "b8fd0395184ae47eda079bcc7ffca528338e5184ba5255882cf4ef37830cddaf"),
    "docs/readers/d40/unit14/index.html": (6_267, "c6785811f86cb96cc3d9a2ce81e094c511937f6d304ba78bab0973928ebcbbcf"),
}
PAGES_URLS = {
    "docs/index.html": STUDENT_URL,
    "docs/app.js": f"{STUDENT_URL}app.js",
    "docs/live-course-publications.js": f"{STUDENT_URL}live-course-publications.js",
    "docs/id-ID/courses/B95/index.html": f"{STUDENT_URL}id-ID/courses/B95/",
    "docs/id-ID/courses/D30/index.html": f"{STUDENT_URL}id-ID/courses/D30/",
    "docs/id-ID/courses/D40/index.html": f"{STUDENT_URL}id-ID/courses/D40/",
    "docs/readers/d40/unit14/index.html": f"{STUDENT_URL}readers/d40/unit14/",
}
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
    b"c:" + b"\\users\\", b"c:" + b"/" + b"users/", b"file:" + b"//",
    b".codex" + b"/attachments", b"new " + b"zenodo " + b"token.md",
    b"github " + b"tokens.md", b"zenodo " + b"token.md",
    b"/" + b"users/", b"/" + b"home/",
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
    return {"name": name or path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def data_fact(data: bytes, name: str) -> dict[str, Any]:
    return {"name": name, "bytes": len(data), "sha256": sha256_bytes(data)}


def canonical_inventory_bytes(facts: list[dict[str, Any]]) -> bytes:
    return "".join(
        f"{item['sha256']}  {item['bytes']}  {item['name']}\n"
        for item in sorted(facts, key=lambda value: value["name"])
    ).encode("utf-8")


def parse_checksum(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        pattern = r"([0-9a-f]{64})  ([^\\/]+)"
        match = re.fullmatch(pattern, line)
        if not match:
            raise ValueError(f"invalid checksum line {number}: {path.name}")
        digest, name = match.groups()
        if name in values:
            raise ValueError(f"duplicate checksum entry: {name}")
        values[name] = digest
    return values


def validate_full_commit(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("--source-commit must be a full lowercase 40-hex commit SHA")
    return value


def remote_blob(commit: str, name: str) -> bytes:
    commit = validate_full_commit(commit)
    url = f"{RAW_REPOSITORY_URL}/{commit}/{quote(name, safe='/')}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": f"program-matematika-indonesia-release-validator/{VERSION}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status != 200:
                raise ValueError(f"immutable source HTTP status differs: {name} -> {response.status}")
            return response.read()
    except Exception as exc:
        raise ValueError(f"cannot read immutable source {commit}:{name}: {exc}") from exc


def static_validation_inputs(root: Path, commit: str) -> dict[str, bytes]:
    values = {name: remote_blob(commit, name) for name in STATIC_VALIDATION_FIXED_INPUTS}
    authority = json.loads(values["backend/authority/curriculum-authority-v1.json"])
    dynamic_names = {f"{authority['federation']['package_path']}/manifest.json"}
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
    return dict(sorted(values.items()))


def dependency_closure(values: dict[str, bytes]) -> dict[str, Any]:
    facts = [data_fact(data, name) for name, data in values.items()]
    return {
        "files": len(facts),
        "bytes": sum(item["bytes"] for item in facts),
        "aggregate_algorithm": "sha256 of sorted '<sha256>  <bytes>  <name>\\n' facts",
        "aggregate_sha256": sha256_bytes(canonical_inventory_bytes(facts)),
    }


def assert_json_fact(actual: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    for key in ("name", "bytes", "sha256"):
        if actual.get(key) != expected.get(key):
            raise ValueError(f"{label} {key} mismatch")


def privacy_scan(name: str, data: bytes) -> None:
    lowered = data.lower()
    markers = [marker.decode("ascii", "replace") for marker in PRIVATE_MARKERS if marker in lowered]
    if markers:
        raise ValueError(f"private marker in {name}: {markers}")


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


def inspect_backend_inputs(args: argparse.Namespace, release: Path) -> dict[str, Any]:
    external = {
        BACKEND_ARCHIVE_NAME: Path(args.backend_v23_archive).resolve(),
        BACKEND_SCOPE_NAME: Path(args.backend_v23_scope_receipt).resolve(),
        BACKEND_VALIDATION_NAME: Path(args.backend_v23_validation_receipt).resolve(),
        BACKEND_DETERMINISM_NAME: Path(args.backend_v23_determinism_receipt).resolve(),
    }
    if len(set(external.values())) != len(external):
        raise ValueError("backend v2.3 artifact arguments must name four distinct files")
    for public_name, source in external.items():
        target = release / public_name
        if not source.is_file() or not target.is_file():
            raise ValueError(f"missing external or release backend v2.3 artifact: {public_name}")
        if source.stat().st_size != target.stat().st_size or sha256_file(source) != sha256_file(target):
            raise ValueError(f"release backend v2.3 artifact differs from explicit input: {public_name}")
    archive = inspect_backend_archive(release / BACKEND_ARCHIVE_NAME)
    archive_fact = archive["archive"]
    receipts = {
        BACKEND_SCOPE_NAME: inspect_backend_receipt(
            release / BACKEND_SCOPE_NAME, BACKEND_SCOPE_NAME, archive_fact, "scope"
        ),
        BACKEND_VALIDATION_NAME: inspect_backend_receipt(
            release / BACKEND_VALIDATION_NAME, BACKEND_VALIDATION_NAME, archive_fact, "validation"
        ),
        BACKEND_DETERMINISM_NAME: inspect_backend_receipt(
            release / BACKEND_DETERMINISM_NAME, BACKEND_DETERMINISM_NAME, archive_fact, "determinism"
        ),
    }
    return {"archive": archive, "receipts": receipts}


def verify_b95_publication(committed_sources: dict[str, bytes]) -> dict[str, Any]:
    page_text = committed_sources["docs/id-ID/courses/B95/index.html"].decode("utf-8")
    overlay_text = committed_sources["docs/live-course-publications.js"].decode("utf-8")
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
        headers={"User-Agent": f"program-matematika-indonesia-release-validator/{VERSION}"},
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
        ["node", "--input-type=module", "-e", source], cwd=root,
        check=True, capture_output=True, text=True,
    )
    return json.loads(process.stdout)


def verify_pages_readbacks(
    committed_sources: dict[str, bytes],
    source_commit: str,
) -> list[dict[str, Any]]:
    rows = []
    for name, (size, digest) in PAGES_IDENTITIES.items():
        data = committed_sources[name]
        if len(data) != size or sha256_bytes(data) != digest:
            raise ValueError(f"committed Pages identity mismatch: {name}")
        url = PAGES_URLS[name]
        separator = "&" if "?" in url else "?"
        request_url = f"{url}{separator}pmi-live-overlay-readback={source_commit}"
        request = urllib.request.Request(
            request_url,
            headers={"User-Agent": f"program-matematika-indonesia-release-validator/{VERSION}"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            public_data = response.read()
        if status != 200 or public_data != data:
            raise ValueError(f"Pages live readback mismatch: {name}; HTTP {status}")
        rows.append({
            "path": name,
            "url": url,
            "bytes": size,
            "sha256": digest,
            "anonymous_readback": "exact-byte-match",
            "http_status": 200,
            "request_url": request_url,
        })
    return rows


def run_strict_link_check(root: Path) -> dict[str, Any]:
    environment = os.environ.copy()
    environment.pop("ALLOW_PENDING_CENTRAL", None)
    process = subprocess.run(
        ["node", "scripts/check-public-links.mjs"], cwd=root,
        check=False, capture_output=True, text=True, env=environment, timeout=900,
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
        ["node", "scripts/validate-static-site.mjs"], cwd=root,
        check=False, capture_output=True, text=True, timeout=120,
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


def validate(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(__file__).resolve().parent.parent
    validate_full_commit(args.source_commit)
    release = (root / args.release_dir).resolve()
    base = (root / "releases" / "v0.62.6").resolve()
    expected_release = (root / "releases" / "v0.62.7").resolve()
    if release != expected_release:
        raise ValueError(f"release directory must be exactly {expected_release}")
    committed_sources = {name: remote_blob(args.source_commit, name) for name in SOURCE_MEMBERS}
    static_inputs = static_validation_inputs(root, args.source_commit)
    if not release.is_dir():
        raise ValueError(f"missing release directory: {release}")
    paths = sorted(release.iterdir(), key=lambda value: value.name)
    if any(not path.is_file() for path in paths):
        raise ValueError("successor release must contain flat files only")
    base_paths = sorted(base.iterdir(), key=lambda value: value.name)
    expected_names = {path.name for path in base_paths} | set(ADDITIVE_NAMES)
    actual_names = {path.name for path in paths}
    if actual_names != expected_names or len(paths) != 98:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        raise ValueError(f"98-file successor inventory mismatch; missing={missing}; extra={extra}")

    base_facts = [fact(path) for path in base_paths]
    if len(base_facts) != BASE_EXPECTED["files"]:
        raise ValueError("base file-count mismatch")
    if sum(item["bytes"] for item in base_facts) != BASE_EXPECTED["bytes"]:
        raise ValueError("base byte-count mismatch")
    if sha256_bytes(canonical_inventory_bytes(base_facts)) != BASE_EXPECTED["aggregate_sha256"]:
        raise ValueError("base aggregate mismatch")
    if sha256_file(base / BASE_EXPECTED["checksum_name"]) != BASE_EXPECTED["checksum_sha256"]:
        raise ValueError("base checksum identity mismatch")
    for source in base_paths:
        target = release / source.name
        if source.stat().st_size != target.stat().st_size or sha256_file(source) != sha256_file(target):
            raise ValueError(f"inherited base file changed: {source.name}")

    checksums = parse_checksum(release / CHECKSUM_NAME)
    non_checksum = [path for path in paths if path.name != CHECKSUM_NAME]
    if set(checksums) != {path.name for path in non_checksum} or len(checksums) != 97:
        raise ValueError("overlay checksum inventory mismatch")
    for path in non_checksum:
        if checksums[path.name] != sha256_file(path):
            raise ValueError(f"overlay checksum mismatch: {path.name}")

    manifest = json.loads((release / MANIFEST_NAME).read_text(encoding="utf-8"))
    expected_manifest_keys = {
        "schema_id", "version", "release_kind", "immutable_base", "source_repository", "predecessor",
        "curriculum_boundary", "live_publication_overlay", "strict_public_link_check",
        "b95_learner_route", "inherited_backend_v23_conformance", "static_site_validation",
        "github_pages", "additive_artifacts", "source_inputs",
        "inventory_contract", "privacy",
    }
    if set(manifest) != expected_manifest_keys:
        raise ValueError("manifest top-level field inventory mismatch")
    if manifest.get("schema_id") != "program-matematika-indonesia/live-publication-overlay-manifest/v1":
        raise ValueError("manifest schema_id mismatch")
    if manifest.get("version") != VERSION:
        raise ValueError("manifest version mismatch")
    if manifest.get("release_kind") != "additive-learner-access-live-publication-adapter":
        raise ValueError("manifest release-kind mismatch")
    expected_immutable = {
        "version": BASE_VERSION,
        "directory": "releases/v0.62.6",
        "files": 93,
        "bytes": 65_639_635,
        "aggregate_algorithm": "sha256 of sorted '<sha256>  <bytes>  <name>\\n' facts",
        "aggregate_sha256": BASE_EXPECTED["aggregate_sha256"],
        "checksum_file": {
            "name": BASE_EXPECTED["checksum_name"],
            "bytes": BASE_EXPECTED["checksum_bytes"],
            "sha256": BASE_EXPECTED["checksum_sha256"],
            "entries": BASE_EXPECTED["checksum_entries"],
        },
        "files_unchanged": base_facts,
    }
    if manifest.get("immutable_base") != expected_immutable:
        raise ValueError("manifest base facts mismatch")
    expected_repository = {
        "repository": REPOSITORY_URL,
        "branch": "main",
        "commit": args.source_commit,
        "commit_url": f"{REPOSITORY_URL}/commit/{args.source_commit}",
    }
    if manifest.get("source_repository") != expected_repository:
        raise ValueError("manifest source-repository binding mismatch")
    expected_predecessor = {
        "version": BASE_VERSION,
        "record_id": PREDECESSOR_RECORD_ID,
        "doi": f"10.5281/zenodo.{PREDECESSOR_RECORD_ID}",
        "public_inventory": {
            "files": BASE_EXPECTED["files"],
            "bytes": BASE_EXPECTED["bytes"],
            "aggregate_sha256": BASE_EXPECTED["aggregate_sha256"],
        },
    }
    if manifest.get("predecessor") != expected_predecessor:
        raise ValueError("manifest predecessor binding mismatch")
    expected_boundary = {
        "frozen_authority_version": FROZEN_AUTHORITY_VERSION,
        "authority_file": "curriculum-authority-v1.json",
        "authority_changed": False,
        "live_overlay_is_authority_replacement": False,
        "overall_program_complete": False,
    }
    if manifest.get("curriculum_boundary") != expected_boundary:
        raise ValueError("manifest authority/completion boundary mismatch")

    expected_inventory_contract = {
        "inherited_files": 93,
        "additive_files": 5,
        "successor_files": 98,
        "checksum_entries": 97,
        "checksum_excludes_only": CHECKSUM_NAME,
    }
    if manifest.get("inventory_contract") != expected_inventory_contract:
        raise ValueError("manifest inventory contract mismatch")
    if manifest.get("privacy") != {
        "credentials_included": False,
        "absolute_local_paths_in_additive_payloads": False,
    }:
        raise ValueError("manifest privacy contract mismatch")
    if manifest.get("additive_artifacts", {}).get("names") != list(ADDITIVE_NAMES):
        raise ValueError("manifest additive-name inventory mismatch")

    readbacks = manifest.get("github_pages", {}).get("anonymous_exact_readbacks", [])
    network_readbacks = verify_pages_readbacks(committed_sources, args.source_commit)
    if readbacks != network_readbacks:
        raise ValueError("manifest Pages readbacks do not match live exact readbacks")
    by_path = {item.get("path"): item for item in readbacks}
    if set(by_path) != set(PAGES_IDENTITIES):
        raise ValueError("Pages readback inventory mismatch")
    for name, (size, digest) in PAGES_IDENTITIES.items():
        local = data_fact(committed_sources[name], name)
        if local["bytes"] != size or local["sha256"] != digest:
            raise ValueError(f"live local Pages identity mismatch: {name}")
        item = by_path[name]
        if item.get("bytes") != size or item.get("sha256") != digest:
            raise ValueError(f"manifest Pages readback identity mismatch: {name}")
        if item.get("anonymous_readback") != "exact-byte-match" or item.get("http_status") != 200:
            raise ValueError(f"manifest Pages readback state mismatch: {name}")
    pages = manifest.get("github_pages", {})
    expected_pages = {
        "workflow_run_id": args.pages_run_id,
        "workflow_run_url": f"{REPOSITORY_URL}/actions/runs/{args.pages_run_id}",
        "conclusion": "success",
        "student_entry_url": STUDENT_URL,
        "anonymous_exact_readbacks": network_readbacks,
    }
    if pages != expected_pages:
        raise ValueError("Pages workflow/readback binding mismatch")

    b95_publication = verify_b95_publication(committed_sources)
    if manifest.get("b95_learner_route") != b95_publication:
        raise ValueError("manifest B95 R011-B025 learner/publication binding mismatch")
    backend_inputs = inspect_backend_inputs(args, release)
    expected_backend = {
        "version": "2.3",
        "package_version": "0.1.1",
        "admitted_scope": ["A00", "O001"],
        "cross_lane_or_whole_program_claim": False,
        "student_route_remains_primary": True,
        "machine_artifacts_are_secondary": True,
        "archive": backend_inputs["archive"],
        "receipts": backend_inputs["receipts"],
    }
    if manifest.get("inherited_backend_v23_conformance") != expected_backend:
        raise ValueError("manifest backend v2.3 conformance binding mismatch")

    standalone = (release / STANDALONE_NAME).read_bytes()
    privacy_scan(STANDALONE_NAME, standalone)
    standalone_text = standalone.decode("utf-8")
    if 'href="styles.css"' in standalone_text or 'src="app.js"' in standalone_text:
        raise ValueError("standalone HTML retains local runtime dependency")
    if standalone_text.count("<html") != 1 or standalone_text.count("</html>") != 1:
        raise ValueError("standalone HTML document shape mismatch")

    with zipfile.ZipFile(release / SOURCE_ZIP_NAME) as archive:
        if archive.testzip() is not None:
            raise ValueError("source ZIP CRC failure")
        expected_validation_facts = [
            data_fact(static_inputs[name], name) for name in sorted(static_inputs)
        ]
        expected_zip_names = sorted(
            (*SOURCE_MEMBERS, *static_inputs.keys(), "SOURCE_ARCHIVE_MANIFEST.json")
        )
        if archive.namelist() != expected_zip_names:
            raise ValueError("source ZIP inventory/order mismatch")
        for info in archive.infolist():
            if info.date_time != FIXED_ZIP_TIME or info.compress_type != zipfile.ZIP_STORED:
                raise ValueError(f"source ZIP metadata mismatch: {info.filename}")
        for name in SOURCE_MEMBERS:
            data = archive.read(name)
            if data != committed_sources[name]:
                raise ValueError(f"source ZIP committed-blob mismatch: {name}")
            privacy_scan(name, data)
        archived_static_inputs: dict[str, bytes] = {}
        for item in expected_validation_facts:
            name = str(item["name"])
            data = archive.read(name)
            if data != static_inputs[name]:
                raise ValueError(f"source ZIP static-validation input mismatch: {name}")
            if data_fact(data, name) != item:
                raise ValueError(f"source ZIP static-validation identity mismatch: {name}")
            privacy_scan(name, data)
            archived_static_inputs[name] = data
        inner = json.loads(archive.read("SOURCE_ARCHIVE_MANIFEST.json"))
        expected_member_facts = [data_fact(committed_sources[name], name) for name in SOURCE_MEMBERS]
        expected_inner = {
            "schema_id": "program-matematika-indonesia/live-overlay-source-archive/v2",
            "version": VERSION,
            "source_commit": args.source_commit,
            "purpose": "Reproduce the standalone learner site and replay static validation from an embedded dependency closure.",
            "replay_contract": {
                "static_validation_inputs_embedded": True,
                "network_required_for_current_commit_proof": True,
                "package_lock_present": False,
            },
            "source_members": expected_member_facts,
            "static_validation_inputs": expected_validation_facts,
            "static_validation_dependency_closure": dependency_closure(static_inputs),
        }
        if inner != expected_inner:
            raise ValueError("source ZIP manifest binding mismatch")
        privacy_scan("SOURCE_ARCHIVE_MANIFEST.json", archive.read("SOURCE_ARCHIVE_MANIFEST.json"))

        with tempfile.TemporaryDirectory(prefix="pmi-overlay-replay-") as temporary:
            snapshot_root = Path(temporary)
            for name in SOURCE_MEMBERS:
                target = snapshot_root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))
            for name, data in archived_static_inputs.items():
                target = snapshot_root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            replay = snapshot_root / "standalone.html"
            subprocess.run(
                ["node", str(snapshot_root / "scripts" / "export-single-file-site.mjs"), str(replay)],
                cwd=snapshot_root, check=True,
            )
            if replay.read_bytes() != standalone:
                raise ValueError("standalone HTML replay from committed source snapshot mismatch")
            live = overlay_summary(snapshot_root)
            strict_link_result = run_strict_link_check(snapshot_root)
            static_site_result = {
                "command": "node scripts/validate-static-site.mjs",
                "report": run_static_site_validation(snapshot_root),
                "additional_committed_input_closure": dependency_closure(static_inputs),
            }
    expected_live = {
        "overlay_ids": EXPECTED_OVERLAY_IDS,
        "overlay_rows": 20,
        "selected_course_roles": 40,
        "effective_published_roles": 27,
        "distinct_completed_public_records": 26,
    }
    for key, value in expected_live.items():
        if live.get(key) != value:
            raise ValueError(f"overlay/manifest {key} mismatch")
    if manifest.get("live_publication_overlay") != live:
        raise ValueError("manifest full live-overlay summary mismatch")
    if manifest.get("strict_public_link_check") != strict_link_result:
        raise ValueError("strict public-link live gate/binding mismatch")
    if manifest.get("static_site_validation") != static_site_result:
        raise ValueError("static-site live gate/binding mismatch")
    expected_source_members = [data_fact(committed_sources[name], name) for name in SOURCE_MEMBERS]
    expected_static_validation_inputs = [
        data_fact(static_inputs[name], name) for name in sorted(static_inputs)
    ]
    with zipfile.ZipFile(release / SOURCE_ZIP_NAME) as archive:
        inner_manifest_data = archive.read("SOURCE_ARCHIVE_MANIFEST.json")
        uncompressed_bytes = sum(info.file_size for info in archive.infolist())
        zip_entries = len(archive.infolist())
    expected_source_archive = {
        "archive": fact(release / SOURCE_ZIP_NAME),
        "entries": zip_entries,
        "uncompressed_bytes": uncompressed_bytes,
        "compression": "stored",
        "fixed_member_timestamp": "2026-08-30T00:00:00Z",
        "manifest": {
            "name": "SOURCE_ARCHIVE_MANIFEST.json",
            "bytes": len(inner_manifest_data),
            "sha256": sha256_bytes(inner_manifest_data),
        },
        "source_members": expected_source_members,
        "static_validation_inputs": expected_static_validation_inputs,
        "static_validation_dependency_closure": dependency_closure(static_inputs),
    }
    expected_additive = {
        "names": list(ADDITIVE_NAMES),
        "standalone_html": fact(release / STANDALONE_NAME),
        "source_archive": expected_source_archive,
    }
    if manifest.get("additive_artifacts") != expected_additive:
        raise ValueError("manifest additive-artifact facts mismatch")
    if manifest.get("source_inputs") != [data_fact(committed_sources[name], name) for name in SOURCE_MEMBERS]:
        raise ValueError("manifest source-input facts mismatch")

    receipt = json.loads((release / RECEIPT_NAME).read_text(encoding="utf-8"))
    expected_receipt_keys = {
        "schema_id", "version", "result", "source_commit", "checks",
        "files_before_receipt", "files_before_receipt_aggregate_sha256",
        "successor_inventory", "validation_command", "publication_performed",
    }
    if set(receipt) != expected_receipt_keys:
        raise ValueError("receipt top-level field inventory mismatch")
    if receipt.get("schema_id") != "program-matematika-indonesia/local-live-overlay-validation/v1":
        raise ValueError("receipt schema_id mismatch")
    if receipt.get("version") != VERSION or receipt.get("result") != "pass":
        raise ValueError("receipt version/result mismatch")
    if receipt.get("source_commit") != args.source_commit:
        raise ValueError("receipt source-commit mismatch")
    if receipt.get("checks") != RECEIPT_CHECKS:
        raise ValueError("receipt check summary mismatch")
    expected_validation_command = (
        "python scripts/validate-live-overlay-release.py --release-dir releases/v0.62.7 "
        f"--source-commit {args.source_commit} --pages-run-id {args.pages_run_id} "
        f"--backend-v23-archive releases/v0.62.7/{BACKEND_ARCHIVE_NAME} "
        f"--backend-v23-scope-receipt releases/v0.62.7/{BACKEND_SCOPE_NAME} "
        f"--backend-v23-validation-receipt releases/v0.62.7/{BACKEND_VALIDATION_NAME} "
        f"--backend-v23-determinism-receipt releases/v0.62.7/{BACKEND_DETERMINISM_NAME}"
    )
    if receipt.get("validation_command") != expected_validation_command:
        raise ValueError("receipt validation-command mismatch")
    files_before_receipt = [
        fact(path) for path in paths if path.name not in {RECEIPT_NAME, CHECKSUM_NAME}
    ]
    if receipt.get("files_before_receipt") != files_before_receipt:
        raise ValueError("receipt pre-receipt inventory mismatch")
    if receipt.get("files_before_receipt_aggregate_sha256") != sha256_bytes(
        canonical_inventory_bytes(files_before_receipt)
    ):
        raise ValueError("receipt pre-receipt aggregate mismatch")
    expected_successor = {
        "files_before_checksum": 97,
        "checksum_entries": 97,
        "final_files": 98,
        "inherited_files": 93,
        "additive_files": 5,
    }
    if receipt.get("successor_inventory") != expected_successor:
        raise ValueError("receipt successor inventory mismatch")
    if receipt.get("publication_performed") is not False:
        raise ValueError("local build receipt improperly claims publication")
    for name in (MANIFEST_NAME, RECEIPT_NAME, CHECKSUM_NAME):
        privacy_scan(name, (release / name).read_bytes())

    all_facts = [fact(path) for path in paths]
    result = {
        "result": "pass",
        "version": VERSION,
        "release_dir": release.relative_to(root).as_posix(),
        "files": len(all_facts),
        "bytes": sum(item["bytes"] for item in all_facts),
        "aggregate_sha256": sha256_bytes(canonical_inventory_bytes(all_facts)),
        "base_files_byte_identical": 93,
        "additive_artifacts": [fact(release / name) for name in ADDITIVE_NAMES],
        "overlay_rows": 20,
        "effective_completed_public_roles": 27,
        "distinct_completed_public_records": 26,
        "strict_public_links": "165/165",
        "pages_exact_readbacks": "7/7",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-dir", default="releases/v0.62.7")
    parser.add_argument("--source-commit", required=True, help="full commit containing every packaged source")
    parser.add_argument("--pages-run-id", required=True, type=int, help="successful Pages workflow run for the source commit")
    parser.add_argument("--backend-v23-archive", required=True, help="public-safe deterministic v2.3 0.1.1 ZIP")
    parser.add_argument("--backend-v23-scope-receipt", required=True, help="sanitized A00+O001 scope-admission receipt")
    parser.add_argument("--backend-v23-validation-receipt", required=True, help="sanitized 13-check validation receipt")
    parser.add_argument("--backend-v23-determinism-receipt", required=True, help="sanitized byte-identical replay receipt")
    return parser.parse_args()


if __name__ == "__main__":
    validate(parse_args())
