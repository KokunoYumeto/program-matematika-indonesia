#!/usr/bin/env python3
"""Build the deterministic v0.62.1 learner-access overlay release.

This is an additive adapter over the immutable v0.62.0 release.  The builder
copies every base-release byte unchanged and creates exactly five new files.
It uses only bounded Git object reads for provenance, performs read-only public
QA, and never mutates a network service or publishes.
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
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


VERSION = "0.62.1"
BASE_VERSION = "0.62.0"
REPOSITORY_URL = "https://github.com/KokunoYumeto/program-matematika-indonesia"
STUDENT_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
PAGES_RUN_ID = 33249907757
PAGES_RUN_URL = (
    "https://github.com/KokunoYumeto/program-matematika-indonesia/actions/runs/"
    f"{PAGES_RUN_ID}"
)
FIXED_ZIP_TIME = (2026, 8, 29, 0, 0, 0)

BASE_EXPECTED = {
    "files": 59,
    "bytes": 28_048_762,
    "aggregate_sha256": "75ea3727d403fa496ab4c095bd2b3abca9c2670a385e60904fa90bff6f277ef3",
    "checksum_file": {
        "name": "CHECKSUMS.sha256",
        "bytes": 6_384,
        "sha256": "e90e5930bf0440ad8fb314af305c1be7d3b9c1e676888468adf3d8c81a33e107",
        "entries": 58,
    },
}

ADDITIVE_NAMES = (
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.1.html",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.1.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.1.zip",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.1.json",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.1.sha256",
)
STANDALONE_NAME, MANIFEST_NAME, SOURCE_ZIP_NAME, RECEIPT_NAME, CHECKSUM_NAME = ADDITIVE_NAMES
BUILD_MARKER_NAME = ".pmi-live-overlay-v0.62.1-building.json"

SOURCE_MEMBERS = (
    "docs/app.js",
    "docs/courses.js",
    "docs/id-ID/courses/D30/index.html",
    "docs/index.html",
    "docs/learner-state.js",
    "docs/live-course-publications.js",
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
    "docs/id-ID/courses/B95/index.html",
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
    "A20", "A30", "B30", "B50", "B95", "C10", "C90", "C100",
    "C140", "D10", "D20", "D30", "D50", "D60", "D70", "D100",
)

PAGES_READBACKS = (
    {
        "path": "docs/index.html",
        "url": STUDENT_URL,
        "bytes": 13_230,
        "sha256": "f24452f630419773ee6fb6f18de772262502e7afa5809858042f93d09953d62c",
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
        "bytes": 18_281,
        "sha256": "cda0cb0b2d45349f775e67e8bb56fd0dd0b77285775a53ac49c013a08ef3a0bf",
    },
    {
        "path": "docs/id-ID/courses/D30/index.html",
        "url": f"{STUDENT_URL}id-ID/courses/D30/",
        "bytes": 4_406,
        "sha256": "deb39d9cebf1cb01c677f9fa227bf238edc30fe1c0beef8f3c6bbdd13fff49be",
    },
)
RECEIPT_CHECKS = {
    "base_release": "59/59 byte-identical",
    "standalone_export_replay": "byte-identical",
    "source_archive": "inventory, CRC, member bytes, timestamps, and order pass",
    "overlay_rows": "16/16",
    "effective_completed_public_roles": "22",
    "distinct_completed_public_records": "21",
    "strict_public_links": "151/151; live network gate executed",
    "static_site_validation": "pass; 40 courses; 16 overlay rows; 22 effective published roles",
    "github_pages_readbacks": "4/4 exact live HTTP 200 byte/hash matches",
    "privacy_scan": "pass",
}

PRIVATE_MARKERS = (
    b"c:" + b"\\users\\",
    b"c:" + b"/users/",
    b"file:" + b"//",
    b".codex" + b"/attachments",
    b"new " + b"zenodo " + b"token.md",
    b"github " + b"tokens.md",
    b"zenodo " + b"token.md",
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


def git_blob(root: Path, commit: str, name: str) -> bytes:
    process = subprocess.run(
        ["git", "show", f"{commit}:{name}"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if process.returncode != 0:
        diagnostic = process.stderr.decode("utf-8", "replace").strip()
        raise ValueError(f"cannot read committed source {commit}:{name}: {diagnostic}")
    return process.stdout


def verify_source_commit(root: Path, commit: str) -> dict[str, bytes]:
    commit = validate_full_commit(commit)
    process = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    head = process.stdout.strip().lower()
    if head != commit:
        raise ValueError(f"builder requires HEAD == --source-commit; HEAD is {head}")
    committed: dict[str, bytes] = {}
    for name in SOURCE_MEMBERS:
        data = git_blob(root, commit, name)
        live = (root / name).read_bytes()
        if live != data:
            raise ValueError(f"working-tree source differs from committed blob: {name}")
        committed[name] = data
    return committed


def static_validation_inputs(root: Path, commit: str, require_live: bool) -> dict[str, bytes]:
    values = {name: git_blob(root, commit, name) for name in STATIC_VALIDATION_FIXED_INPUTS}
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
        values[name] = git_blob(root, commit, name)
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
        raise ValueError("existing v0.62.1 output is not a directory")
    paths = sorted(output.iterdir(), key=lambda value: value.name)
    if any(not path.is_file() for path in paths):
        raise ValueError("existing v0.62.1 output is not a flat release")
    if {path.name for path in paths} != base_names | set(ADDITIVE_NAMES):
        raise ValueError("existing v0.62.1 output is not a recognized 59+5 candidate")
    manifest = json.loads((output / MANIFEST_NAME).read_text(encoding="utf-8"))
    if manifest.get("schema_id") != "program-matematika-indonesia/live-publication-overlay-manifest/v1":
        raise ValueError("existing v0.62.1 manifest is not recognized")
    if manifest.get("version") != VERSION:
        raise ValueError("existing v0.62.1 manifest version mismatch")
    checksums = parse_checksum(output / CHECKSUM_NAME)
    non_checksum = [path for path in paths if path.name != CHECKSUM_NAME]
    if set(checksums) != {path.name for path in non_checksum}:
        raise ValueError("existing v0.62.1 checksum inventory mismatch")
    for path in non_checksum:
        if checksums[path.name] != sha256_file(path):
            raise ValueError(f"existing v0.62.1 checksum mismatch: {path.name}")


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
        "overlay_rows": 16,
        "selected_course_roles": 40,
        "effective_published_roles": 22,
        "distinct_completed_public_records": 21,
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
            headers={"User-Agent": "program-matematika-indonesia-release-validator/0.62.1"},
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
    if report.get("status") != "pass" or report.get("checked") != 151:
        raise ValueError("strict public-link count/result mismatch")
    if not isinstance(links, list) or len(links) != 151:
        raise ValueError("strict public-link result inventory mismatch")
    if any(not isinstance(row.get("status"), int) or not 200 <= row["status"] < 400 for row in links):
        raise ValueError("strict public-link report contains a non-success status")
    return {
        "command": "node scripts/check-public-links.mjs",
        "mode": "strict; no pending-central exception",
        "executed": True,
        "result": "pass",
        "checked": 151,
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
        "effectivePublishedRoles": 22,
        "liveOverlayRows": 16,
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
) -> dict[str, Any]:
    members = []
    for name in SOURCE_MEMBERS:
        data = committed_sources[name]
        privacy_scan(name, data)
        members.append({"name": name, "bytes": len(data), "sha256": sha256_bytes(data)})
    archive_manifest = {
        "schema_id": "program-matematika-indonesia/live-overlay-source-archive/v1",
        "version": VERSION,
        "source_commit": source_commit,
        "purpose": "Reproduce the standalone learner site and inspect the live-publication adapter.",
        "members": members,
    }
    manifest_data = (
        json.dumps(archive_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    entries = [(item["name"], committed_sources[item["name"]]) for item in members]
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
        "fixed_member_timestamp": "2026-08-29T00:00:00Z",
        "manifest": {
            "name": "SOURCE_ARCHIVE_MANIFEST.json",
            "bytes": len(manifest_data),
            "sha256": sha256_bytes(manifest_data),
        },
        "source_members": members,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(__file__).resolve().parent.parent
    base = (root / args.base_release).resolve()
    output = (root / args.output).resolve()
    releases_root = (root / "releases").resolve()
    expected_base = releases_root / "v0.62.0"
    expected_output = releases_root / "v0.62.1"
    if base != expected_base:
        raise ValueError(f"base release must be exactly {expected_base}")
    if output != expected_output:
        raise ValueError(f"output must be exactly {expected_output}")
    committed_sources = verify_source_commit(root, args.source_commit)
    static_inputs = static_validation_inputs(root, args.source_commit, require_live=True)

    base_facts = verify_base(base)
    summary = overlay_summary(root)
    readbacks = verify_pages_sources(root, args.source_commit)
    strict_link_result = run_strict_link_check(root)
    static_site_result = {
        "command": "node scripts/validate-static-site.mjs",
        "report": run_static_site_validation(root),
        "additional_committed_input_closure": dependency_closure(static_inputs),
    }

    staging = output.with_name(f"{output.name}.building")
    expected_staging = releases_root / "v0.62.1.building"
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
        )
        standalone_fact = fact(standalone, STANDALONE_NAME)
        source_facts = [data_fact(committed_sources[name], name) for name in SOURCE_MEMBERS]
        manifest = {
            "schema_id": "program-matematika-indonesia/live-publication-overlay-manifest/v1",
            "version": VERSION,
            "release_kind": "additive-learner-access-live-publication-adapter",
            "immutable_base": {
                "version": BASE_VERSION,
                "directory": "releases/v0.62.0",
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
            "curriculum_boundary": {
                "frozen_authority_version": BASE_VERSION,
                "authority_file": "curriculum-authority-v1.json",
                "authority_changed": False,
                "live_overlay_is_authority_replacement": False,
                "overall_program_complete": False,
            },
            "live_publication_overlay": summary,
            "strict_public_link_check": strict_link_result,
            "static_site_validation": static_site_result,
            "github_pages": {
                "workflow_run_id": PAGES_RUN_ID,
                "workflow_run_url": PAGES_RUN_URL,
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
                "inherited_files": 59,
                "additive_files": 5,
                "successor_files": 64,
                "checksum_entries": 63,
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
        if len(before_receipt) != 62:
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
                "files_before_checksum": 63,
                "checksum_entries": 63,
                "final_files": 64,
                "inherited_files": 59,
                "additive_files": 5,
            },
            "validation_command": (
                "python scripts/validate-live-overlay-release.py --release-dir releases/v0.62.1 "
                f"--source-commit {args.source_commit}"
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
        if len(pre_checksum) != 63:
            raise ValueError(f"pre-checksum inventory mismatch: {len(pre_checksum)}")
        (staging / CHECKSUM_NAME).write_bytes(
            "".join(
                f"{item['sha256']}  {item['name']}\n"
                for item in sorted(pre_checksum, key=lambda value: value["name"])
            ).encode("utf-8")
        )
        (staging / BUILD_MARKER_NAME).unlink()
        if len(list(staging.iterdir())) != 64:
            raise ValueError("final inventory is not 64 files")
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
    parser.add_argument("--base-release", default="releases/v0.62.0")
    parser.add_argument("--output", default="releases/v0.62.1")
    parser.add_argument("--source-commit", required=True, help="full commit containing every packaged source")
    parser.add_argument("--force", action="store_true", help="replace only the exact output directory")
    return parser.parse_args()


if __name__ == "__main__":
    build(parse_args())
