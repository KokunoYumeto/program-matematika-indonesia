#!/usr/bin/env python3
"""Publish and anonymously verify PMI v0.62.12 on its existing Zenodo concept.

``--preflight`` is deliberately local-only: it reads no credential, opens no
network connection, creates no draft, and writes no receipt.  With no option,
the script uses the proven v0.62.11/v0.62.10/v0.62.9 transaction chain to
create or resume one successor version, publish it open, and verify every
public byte before writing sanitized receipts.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
TEMPLATE_SCRIPT = PROJECT / "scripts/publish-v06211-zenodo.py"
TEMPLATE_V06210 = PROJECT / "scripts/publish-v06210-zenodo.py"
TEMPLATE_V0629 = PROJECT / "scripts/publish-v0629-zenodo.py"

sys.dont_write_bytecode = True

_BOOTSTRAP_TEMPLATE_IDENTITIES = {
    TEMPLATE_SCRIPT: (10_214, "95ec67c25048b3e9525a42b05fb8bc5ce614109c293277a4c6c01c06ff36fe45"),
    TEMPLATE_V06210: (17_439, "780ed7c955e33de6f911bea74698fa3713ff391c1c9550bdb877c780fe59a70e"),
    TEMPLATE_V0629: (60_924, "76cabf3f5b0b4644fea75b25a1c39471ac4b160e523cd101a605dd04c897d35c"),
}


def _stdlib_identity(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def _verify_template_chain_before_execution() -> None:
    for path, expected in _BOOTSTRAP_TEMPLATE_IDENTITIES.items():
        if _stdlib_identity(path) != expected:
            raise RuntimeError(f"publisher template identity differs: {path.name}")


def _standalone_preflight() -> dict[str, Any]:
    """Validate all local authority bytes without importing publisher code."""

    _verify_template_chain_before_execution()
    release_dir = PROJECT / "releases/v0.62.12"
    checksum_file = release_dir / "RELEASE_CHECKSUMS_v0.62.12.sha256"
    github_path = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.12.json"
    predecessor_path = PROJECT / "PUBLICATION_RECEIPT_v0.62.11.json"
    expected_github = (54_665, "24676adb7024320fb3bc123a34284de88276ca69d78c44e3fe29eb114a4c3965")
    expected_predecessor = (49_882, "8429373d0a7974537723b82e75a08d9e0bc8fabcd21d408eea3fb012394f3921")
    if _stdlib_identity(github_path) != expected_github:
        raise RuntimeError("GitHub receipt identity differs")
    if _stdlib_identity(predecessor_path) != expected_predecessor:
        raise RuntimeError("predecessor receipt identity differs")
    entries = list(release_dir.iterdir())
    if len(entries) != 100 or not all(path.is_file() and not path.is_symlink() for path in entries):
        raise RuntimeError("v0.62.12 release is not exactly 100 flat regular files")
    paths = {path.name: path for path in entries}
    if len(paths) != 100:
        raise RuntimeError("v0.62.12 release has duplicate filenames")
    rows = []
    for name in sorted(paths):
        size, digest = _stdlib_identity(paths[name])
        rows.append({"name": name, "bytes": size, "sha256": digest})
    aggregate_material = "".join(f"{row['sha256']}  {row['name']}\n" for row in rows).encode("utf-8")
    aggregate = hashlib.sha256(aggregate_material).hexdigest()
    if sum(int(row["bytes"]) for row in rows) != 131_739_644:
        raise RuntimeError("v0.62.12 release byte total differs")
    if aggregate != "3254b566c27819c2230ecf4ef2009879058e6bd41359b3926bd5e3fc36fd7c33":
        raise RuntimeError("v0.62.12 release aggregate differs")
    local = {str(row["name"]): row for row in rows}
    checksum_rows: dict[str, str] = {}
    for number, line in enumerate(checksum_file.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None or match.group(2) in checksum_rows:
            raise RuntimeError(f"malformed checksum manifest row {number}")
        checksum_rows[match.group(2)] = match.group(1)
    if set(checksum_rows) != set(local) - {checksum_file.name}:
        raise RuntimeError("checksum manifest coverage differs")
    if any(local[name]["sha256"] != digest for name, digest in checksum_rows.items()):
        raise RuntimeError("checksum manifest bytes differ")
    github = json.loads(github_path.read_text(encoding="utf-8"))
    github_rows = github.get("anonymous_asset_readback", {}).get("entries", [])
    github_by_name = {str(row["name"]): row for row in github_rows}
    if github.get("state") != "published_public_verified" or github.get("tag") != "v0.62.12":
        raise RuntimeError("GitHub publication state differs")
    if github.get("anonymous_asset_readback", {}).get("result") != "pass_100_of_100":
        raise RuntimeError("GitHub readback result differs")
    if set(github_by_name) != set(local):
        raise RuntimeError("GitHub/local filename sets differ")
    for name, row in local.items():
        if int(github_by_name[name]["bytes"]) != int(row["bytes"]) or github_by_name[name]["sha256"] != row["sha256"]:
            raise RuntimeError(f"GitHub/local byte identity differs: {name}")
    predecessor = json.loads(predecessor_path.read_text(encoding="utf-8"))
    predecessor_rows = predecessor.get("payload_inventory", [])
    predecessor_by_name = {str(row["name"]): row for row in predecessor_rows}
    if predecessor.get("version") != "0.62.11" or int(predecessor.get("zenodo", {}).get("record_id", -1)) != 22179556:
        raise RuntimeError("predecessor authority differs")
    retained = set(local) & set(predecessor_by_name)
    omitted = set(predecessor_by_name) - set(local)
    additions = set(local) - set(predecessor_by_name)
    if (len(retained), len(omitted), len(additions)) != (81, 19, 19):
        raise RuntimeError("81/19/19 replacement boundary differs")
    for name in retained:
        predecessor_row = predecessor_by_name[name]
        if int(predecessor_row["bytes"]) != int(local[name]["bytes"]) or predecessor_row["sha256"] != local[name]["sha256"]:
            raise RuntimeError(f"retained predecessor byte identity differs: {name}")
    required_additions = {
        "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md",
        "modular-backend-pattern-index-v1.json",
        "course-capsules-v1.jsonl",
        "program-matematika-indonesia-course-capsule-v1.zip",
        "learner-delivery-v1.json",
        "peta-belajar-luring.html",
        "program-matematika-indonesia-backend-v2.3.1-d20-adapter-v0.1.0.zip",
    }
    if not required_additions <= additions:
        raise RuntimeError("method/capsule/learner/D20 additive boundary is incomplete")
    return {
        "status": "PASS_LOCAL_PREFLIGHT_NO_DYNAMIC_IMPORT_NO_NETWORK_NO_CREDENTIAL_NO_WRITE",
        "version": "0.62.12",
        "concept_doi": "10.5281/zenodo.22059707",
        "predecessor_record_id": 22179556,
        "files": 100,
        "bytes": 131_739_644,
        "aggregate_sha256": aggregate,
        "github_tag_target_commit": github["release"]["tag_target_commit"],
        "retained_exact_files": 81,
        "omitted_files": 19,
        "additive_files": 19,
        "course_capsules": 40,
        "audited_native_families": 33,
        "adapter_bound_roles": ["A00", "B10", "D20", "D60", "D110"],
        "native_roles_retained": 35,
        "learner_entry": "https://kokunoyumeto.github.io/program-matematika-indonesia/",
        "backend_center": "https://kokunoyumeto.github.io/program-matematika-indonesia/backend/",
        "github_release": "https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.12",
        "default_preview": "peta-belajar-luring.html",
        "receipt_targets": ["PUBLICATION_RECEIPT_v0.62.12.json", "PUBLICATION_RECEIPT.json"],
        "template_chain_verified_before_execution": [path.name for path in _BOOTSTRAP_TEMPLATE_IDENTITIES],
    }


if sys.argv[1:] == ["--preflight"]:
    try:
        print(json.dumps(_standalone_preflight(), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    except Exception as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(f"FAIL: {type(exc).__name__}: {detail}", file=sys.stderr)
        raise SystemExit(1)
    raise SystemExit(0)

_verify_template_chain_before_execution()

spec = importlib.util.spec_from_file_location("pmi_v06211_zenodo_template", TEMPLATE_SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load the proven v0.62.11 Zenodo publisher")
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
base = previous.base


# All public verification performed by this wrapper must be genuinely
# anonymous.  Requests' default Session trusts environment credentials and
# .netrc; the inherited publisher predates this stricter boundary.  Replacing
# the module global keeps every inherited public_json/anonymous_inventory call
# on one credential-free transport without changing authenticated mutation
# calls, which continue to use their explicitly authenticated client.
_ANONYMOUS_SESSION = base.requests.Session()
_ANONYMOUS_SESSION.trust_env = False
_ANONYMOUS_SESSION.headers.update({"User-Agent": "Codex-PMI-v06212-Anonymous-Readback/1.0"})


def strict_anonymous_public_get(url: str, *, stream: bool = False, timeout: int = 180):
    last = None
    for attempt in range(5):
        response = _ANONYMOUS_SESSION.get(
            url,
            stream=stream,
            timeout=(20, timeout),
            allow_redirects=True,
        )
        if response.status_code == 200 or response.status_code not in (429, 500, 502, 503, 504):
            return response
        response.close()
        last = response
        base.time.sleep(2 * (attempt + 1))
    status = last.status_code if last is not None else 0
    raise RuntimeError(f"anonymous public retry budget exhausted after HTTP {status}")


base.public_get = strict_anonymous_public_get

RELEASE_DIR = PROJECT / "releases/v0.62.12"
CHECKSUM_FILE = RELEASE_DIR / "RELEASE_CHECKSUMS_v0.62.12.sha256"
GITHUB_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.12.json"
PREDECESSOR_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.11.json"
VERSION_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.12.json"
ROOT_RECEIPT = PROJECT / "PUBLICATION_RECEIPT.json"
TOKEN_FILE_ENV = "PMI_V06212_ZENODO_TOKEN_FILE"

CONCEPT_ID = 22059707
PREDECESSOR_ID = 22179556
PREDECESSOR_VERSION = "0.62.11"
VERSION = "0.62.12"
LEARNER_FILE = "peta-belajar-luring.html"
LEARNER_SITE = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
BACKEND_CENTER = "https://kokunoyumeto.github.io/program-matematika-indonesia/backend/"
GITHUB_RELEASE = "https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.12"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
USER_AGENT = "Codex-PMI-v06212-Zenodo-Publisher/1.0"

EXPECTED_FILES = 100
EXPECTED_BYTES = 131_739_644
EXPECTED_AGGREGATE = "3254b566c27819c2230ecf4ef2009879058e6bd41359b3926bd5e3fc36fd7c33"
EXPECTED_GITHUB_RECEIPT = (54_665, "24676adb7024320fb3bc123a34284de88276ca69d78c44e3fe29eb114a4c3965")
EXPECTED_PREDECESSOR_RECEIPT = (49_882, "8429373d0a7974537723b82e75a08d9e0bc8fabcd21d408eea3fb012394f3921")
EXPECTED_TEMPLATE_V06211 = (10_214, "95ec67c25048b3e9525a42b05fb8bc5ce614109c293277a4c6c01c06ff36fe45")
EXPECTED_TEMPLATE_V06210 = (17_439, "780ed7c955e33de6f911bea74698fa3713ff391c1c9550bdb877c780fe59a70e")

ADAPTER_BOUND_ROLES = ["A00", "B10", "D20", "D60", "D110"]
PREDECESSOR_RELATION_INDEX: int | None = None

TITLE = "Program Matematika Indonesia v0.62.12 — Metode Backend Modular dan Kapsul Kursus"
DESCRIPTION = (
    '<p><strong>Mulai belajar sekarang:</strong> <a href="https://kokunoyumeto.github.io/program-matematika-indonesia/">'
    "buka halaman siswa Program Matematika Indonesia</a>. Ini adalah pintu masuk utama untuk menelusuri prasyarat, "
    "status mata kuliah, pembaca HTML, dan unduhan belajar.</p>"
    '<p><strong>Infrastruktur dan dokumentasi metode:</strong> <a href="https://kokunoyumeto.github.io/program-matematika-indonesia/backend/">'
    "buka pusat backend modular</a>. Berkas JSON, JSONL, CSV, skema, dan ZIP adalah lapisan mesin dan reproduksibilitas "
    "sekunder; semuanya mendukung halaman siswa, bukan menggantikannya.</p>"
    "<p>Alur kerja yang didokumentasikan di versi ini sengaja dimulai dengan backend native yang dikembangkan secara "
    "independen pada lintasan produksi. Audit komparatif kemudian memeriksa 33 keluarga implementasi, mengambil pola "
    "yang dapat dipakai bersama, dan menambahkan kapsul kursus serta adapter tipis tanpa meratakan identitas, lisensi, "
    "format sumber, atau kontrol kanonik pemilik. Dengan demikian perbedaan yang berguna dipertahankan, sedangkan "
    "navigasi, pertukaran data, validasi, dan penerjemahan lintas bahasa memperoleh lapisan bersama.</p>"
    "<p>Batas bukti saat ini adalah 40 kapsul kursus dan lima peran dengan adapter yang tervalidasi: A00, B10, D20, "
    "D60, dan D110. Tiga puluh lima peran lain tetap memakai sistem native masing-masing dan tidak diklaim telah "
    "memenuhi kontrak adapter ini. Program penerjemahan keseluruhan belum lengkap.</p>"
    '<p>Rilis GitHub yang identik tersedia di <a href="https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.12">'
    "GitHub v0.62.12</a>. Payload berisi tepat 100 berkas; 81 berkas v0.62.11 dipertahankan byte demi byte, 19 artefak "
    "metode/kapsul/D20 ditambahkan, dan 19 artefak historis yang tidak diduplikasi tetap terbuka pada record pendahulu. "
    "Tidak ada record pendahulu yang diubah, ditutup, atau dibatasi.</p>"
    "<p>Hak setiap komponen dan semua kredit sumber, penulis, serta kontributor manusia tetap dipertahankan. Paket "
    "gabungan memakai lisensi <em>other-open</em> karena tidak memiliki satu lisensi tunggal. Produksi, integrasi, dan "
    "QA dibantu oleh <strong>OpenAI Codex gpt-5.6-sol, Ultra</strong> atas instruksi pengguna.</p>"
)
NOTES = (
    "Rilis v0.62.12 memublikasikan metode backend modular, audit komparatif 33 keluarga, 40 kapsul kursus, "
    "lapisan pengantaran siswa, dan adapter D20. Situs siswa adalah pintu masuk utama. Lima peran memiliki "
    "bukti adapter; 35 peran lain mempertahankan backend native dan program keseluruhan belum lengkap."
)

OMITTED = {
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.4.html",
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.5.html",
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.6.html",
    "CHECKSUMS.sha256",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.4.sha256",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.5.sha256",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.6.sha256",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.4.json",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.5.json",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.6.json",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.4.json",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.5.json",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.6.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.4.zip",
    "program-matematika-indonesia-live-overlay-source-v0.62.5.zip",
    "program-matematika-indonesia-live-overlay-source-v0.62.6.zip",
    "RELEASE_CHECKSUMS_v0.62.10.sha256",
    "RELEASE_NOTES_v0.62.0.md",
    "RELEASE_NOTES_v0.62.10.md",
}

ADDITIONS = {
    "190_LEARNER_ACCESS_OFFLINE_DELIVERY_TRANCHE_20260830.json",
    "191_D20_V231_ADAPTER_VALIDATION_V010_FINAL_20260831.json",
    "192_D20_V231_ADAPTER_CANONICAL_ADMISSION_20260831.json",
    "193_D20_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260831.json",
    "194_GLOBAL_MODULAR_BACKEND_LEARNER_DELIVERY_INTEGRATION_20260831.json",
    "course-capsule-v1.schema.json",
    "course-capsules-v1.jsonl",
    "GITHUB_D20_V231_SOURCE_PUBLICATION_RECEIPT.json",
    "learner-delivery-v1.json",
    "learner-delivery-v1.schema.json",
    "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md",
    "modular-backend-pattern-index-v1.json",
    "peta-belajar-luring.html",
    "program-matematika-indonesia-backend-v2.3.1-d20-adapter-v0.1.0.zip",
    "program-matematika-indonesia-course-capsule-v1.zip",
    "RELEASE_CHECKSUMS_v0.62.12.sha256",
    "RELEASE_NOTES_v0.62.12.md",
    "v23-adapter-index-v1.json",
    "v23-adapter-index-v1.schema.json",
}


for module in (previous, previous.template, base):
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


def file_identity(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), base.sha256_bytes(data)


def checksum_inventory() -> dict[str, str]:
    base.require(CHECKSUM_FILE.is_file(), "v0.62.12 checksum manifest is missing")
    rows: dict[str, str] = {}
    for line_number, line in enumerate(CHECKSUM_FILE.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        base.require(match is not None, f"malformed checksum row {line_number}")
        digest, name = match.groups()
        base.require(name not in rows, f"duplicate checksum row: {name}")
        rows[name] = digest
    base.require(len(rows) == 99, "checksum manifest is not exactly 99 payload rows")
    return rows


def local_inventory() -> tuple[list[dict[str, Any]], dict[str, Path], dict[str, Any], dict[str, Any]]:
    base.require(RELEASE_DIR.is_dir(), "v0.62.12 release directory is missing")
    base.require(GITHUB_RECEIPT.is_file(), "GitHub v0.62.12 publication receipt is missing")
    base.require(file_identity(GITHUB_RECEIPT) == EXPECTED_GITHUB_RECEIPT, "GitHub receipt identity differs")
    entries = list(RELEASE_DIR.iterdir())
    base.require(len(entries) == EXPECTED_FILES, "local release is not exactly 100 entries")
    base.require(all(path.is_file() and not path.is_symlink() for path in entries), "local release is not flat regular files")
    paths = {path.name: path for path in entries}
    base.require(len(paths) == EXPECTED_FILES, "local release has duplicate filenames")
    checksums = checksum_inventory()
    base.require(set(checksums) == set(paths) - {CHECKSUM_FILE.name}, "checksum coverage differs")
    github = json.loads(GITHUB_RECEIPT.read_text(encoding="utf-8"))
    base.require(github.get("state") == "published_public_verified", "GitHub release is not public verified")
    base.require(github.get("tag") == "v0.62.12", "GitHub tag differs")
    base.require(github.get("release", {}).get("url") == GITHUB_RELEASE, "GitHub release URL differs")
    base.require(github.get("anonymous_asset_readback", {}).get("result") == "pass_100_of_100", "GitHub readback differs")
    github_rows = github.get("anonymous_asset_readback", {}).get("entries")
    base.require(isinstance(github_rows, list) and len(github_rows) == EXPECTED_FILES, "GitHub inventory differs")
    github_by_name = {str(row["name"]): row for row in github_rows}
    base.require(set(github_by_name) == set(paths), "GitHub/local filename sets differ")
    rows: list[dict[str, Any]] = []
    for name in sorted(paths):
        data = paths[name].read_bytes()
        row = {"name": name, "path": paths[name], "bytes": len(data), "md5": base.md5_bytes(data), "sha256": base.sha256_bytes(data)}
        base.require(row["bytes"] == int(github_by_name[name]["bytes"]), f"GitHub size differs: {name}")
        base.require(row["sha256"] == github_by_name[name]["sha256"], f"GitHub hash differs: {name}")
        if name in checksums:
            base.require(row["sha256"] == checksums[name], f"checksum manifest differs: {name}")
        rows.append(row)
    aggregate = base.inventory_sha(rows)
    base.require(sum(int(row["bytes"]) for row in rows) == EXPECTED_BYTES, "local byte total differs")
    base.require(aggregate == EXPECTED_AGGREGATE, "local aggregate differs")
    base.require(github.get("inventory", {}).get("files") == EXPECTED_FILES, "GitHub inventory count differs")
    base.require(github.get("inventory", {}).get("bytes") == EXPECTED_BYTES, "GitHub inventory bytes differ")
    base.require(github.get("inventory", {}).get("aggregate_sha256") == aggregate, "GitHub aggregate differs")
    predecessor = json.loads(PREDECESSOR_RECEIPT.read_text(encoding="utf-8"))
    predecessor_by_name = {str(row["name"]): row for row in predecessor["payload_inventory"]}
    predecessor_names = set(predecessor_by_name)
    base.require(predecessor_names - set(paths) == OMITTED, "predecessor/local omission boundary differs")
    base.require(set(paths) - predecessor_names == ADDITIONS, "predecessor/local addition boundary differs")
    retained = predecessor_names & set(paths)
    base.require(len(retained) == 81, "retained predecessor count differs")
    local_by_name = {str(row["name"]): row for row in rows}
    for name in retained:
        base.require(int(predecessor_by_name[name]["bytes"]) == int(local_by_name[name]["bytes"]), f"retained predecessor size differs: {name}")
        base.require(predecessor_by_name[name]["sha256"] == local_by_name[name]["sha256"], f"retained predecessor SHA-256 differs: {name}")
    return rows, paths, {"version": VERSION, "inventory": [{key: row[key] for key in ("name", "bytes", "sha256")} for row in rows], "inventory_aggregate_sha256": aggregate}, github


original_public_file_stubs = previous.base_public_file_stubs


def predecessor_authority(local_rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    global PREDECESSOR_RELATION_INDEX
    base.require(file_identity(PREDECESSOR_RECEIPT) == EXPECTED_PREDECESSOR_RECEIPT, "predecessor receipt identity differs")
    record = base.public_json(f"{base.PUBLIC_API}/{PREDECESSOR_ID}")
    base.require(int(record.get("id", -1)) == PREDECESSOR_ID, "predecessor record ID differs")
    base.require(record.get("conceptdoi") == f"10.5281/zenodo.{CONCEPT_ID}", "predecessor concept differs")
    metadata = record.get("metadata", {})
    base.require(isinstance(metadata, dict), "predecessor metadata is malformed")
    base.require(metadata.get("version") == PREDECESSOR_VERSION, "predecessor version differs")
    base.require(metadata.get("access_right") == "open", "predecessor is not open")
    base.require(base.license_id(metadata) == "other-open", "predecessor license differs")
    base.require(metadata.get("language") == "ind", "predecessor language differs")
    PREDECESSOR_RELATION_INDEX = int(base.version_relation(metadata)["index"])
    receipt = json.loads(PREDECESSOR_RECEIPT.read_text(encoding="utf-8"))
    predecessor_rows = receipt.get("payload_inventory")
    base.require(isinstance(predecessor_rows, list) and len(predecessor_rows) == EXPECTED_FILES, "predecessor receipt inventory differs")
    expected = [{"name": row["name"], "bytes": int(row["bytes"]), "sha256": row["sha256"], "md5": ""} for row in predecessor_rows]
    stubs = {row["name"]: row for row in original_public_file_stubs(record, EXPECTED_FILES, "predecessor-stubs")}
    for row in expected:
        base.require(row["name"] in stubs, f"predecessor missing file: {row['name']}")
        row["md5"] = stubs[row["name"]]["md5"]
    observed = base.anonymous_inventory(record, expected, "predecessor-before")
    base.require({str(row["name"]) for row in expected} - {str(row["name"]) for row in local_rows} == OMITTED, "predecessor/local omission boundary differs")
    return record, metadata, observed


def related_identifiers(predecessor_metadata: dict[str, Any]) -> list[dict[str, str]]:
    result = [
        {"identifier": LEARNER_SITE, "relation": "isSupplementTo", "scheme": "url"},
        {"identifier": BACKEND_CENTER, "relation": "isSupplementTo", "scheme": "url"},
    ]
    for row in predecessor_metadata.get("related_identifiers", []):
        if not isinstance(row, dict):
            continue
        identifier = str(row.get("identifier", ""))
        if identifier in (LEARNER_SITE, BACKEND_CENTER):
            continue
        if re.fullmatch(r"https://github\.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v[^/]+", identifier):
            continue
        normalized = {"identifier": identifier, "relation": str(row.get("relation", "")), "scheme": str(row.get("scheme", ""))}
        if normalized not in result:
            result.append(normalized)
    result.append({"identifier": GITHUB_RELEASE, "relation": "isIdenticalTo", "scheme": "url"})
    return result


def verify_exact_draft(draft: dict[str, Any], local_rows: list[dict[str, Any]]) -> None:
    remote = {str(row["name"]): row for row in base.draft_file_rows(draft)}
    local = {str(row["name"]): row for row in local_rows}
    base.require(len(remote) == EXPECTED_FILES and set(remote) == set(local), "final draft is not exact 100-file inventory")
    for name, expected in local.items():
        base.require(int(remote[name]["bytes"]) == int(expected["bytes"]), f"final draft size differs: {name}")
        base.require(remote[name]["md5"] == expected["md5"], f"final draft MD5 differs: {name}")


def verify_final_draft_metadata(draft: dict[str, Any], payload: dict[str, Any]) -> None:
    metadata = draft.get("metadata", {})
    base.require(isinstance(metadata, dict), "final draft metadata is malformed")
    for field, expected in payload.items():
        if field == "license":
            base.require(base.license_id(metadata) == expected, "final draft license differs")
        else:
            base.require(metadata.get(field) == expected, f"final draft target metadata differs: {field}")
    base.require(isinstance(draft.get("files"), list) and len(draft["files"]) == EXPECTED_FILES, "final draft file list differs")


def verify_rdm_learner_preview(value: dict[str, Any]) -> None:
    files = value.get("files", {})
    base.require(isinstance(files, dict) and files.get("enabled") is True, "InvenioRDM files are not enabled")
    base.require(files.get("count") == EXPECTED_FILES, "InvenioRDM file count differs")
    base.require(files.get("default_preview") == LEARNER_FILE, "InvenioRDM default preview differs")


def verify_lineage(record: dict[str, Any], predecessor_record: dict[str, Any], predecessor_rows: list[dict[str, Any]]) -> dict[str, Any]:
    record_id = int(record["id"])
    latest = base.public_json(f"{base.PUBLIC_API}/{CONCEPT_ID}/versions/latest")
    base.require(int(latest.get("id", -1)) == record_id and latest.get("metadata", {}).get("version") == VERSION, "concept latest differs")
    base.require(PREDECESSOR_RELATION_INDEX is not None, "predecessor version index was not recorded")
    successor_relation = base.version_relation(record.get("metadata", {}))
    base.require(int(successor_relation["index"]) == PREDECESSOR_RELATION_INDEX + 1, "successor is not exactly one concept version after predecessor")
    predecessor_after = base.public_json(f"{base.PUBLIC_API}/{PREDECESSOR_ID}")
    before_metadata = predecessor_record.get("metadata", {})
    after_metadata = predecessor_after.get("metadata", {})
    base.require(base.stable_public_metadata(after_metadata) == base.stable_public_metadata(before_metadata), "predecessor stable metadata changed")
    relation_before = base.version_relation(before_metadata)
    relation_after = base.version_relation(after_metadata)
    base.require({k: v for k, v in relation_after.items() if k != "is_last"} == {k: v for k, v in relation_before.items() if k != "is_last"}, "predecessor relation changed")
    base.require(relation_after["is_last"] is False, "predecessor remains latest")
    before_files = [(row["name"], row["bytes"], row["md5"]) for row in original_public_file_stubs(predecessor_record, EXPECTED_FILES, "predecessor-before-lineage")]
    after_files = [(row["name"], row["bytes"], row["md5"]) for row in original_public_file_stubs(predecessor_after, EXPECTED_FILES, "predecessor-after-lineage")]
    base.require(after_files == before_files, "predecessor file inventory changed")
    observed = base.anonymous_inventory(predecessor_after, predecessor_rows, "predecessor-after")
    base.require(base.inventory_sha(observed) == base.inventory_sha(predecessor_rows), "predecessor bytes changed")
    for doi_id, expected_id in ((record_id, record_id), (CONCEPT_ID, record_id), (PREDECESSOR_ID, PREDECESSOR_ID)):
        response = base.public_get(f"https://doi.org/10.5281/zenodo.{doi_id}")
        base.require(response.status_code == 200 and response.url.rstrip("/").endswith(f"/records/{expected_id}"), "DOI resolution differs")
    student = base.public_get(LEARNER_SITE)
    base.require(student.status_code == 200 and "Program Matematika Indonesia" in student.text, "student site readback failed")
    backend = base.public_get(BACKEND_CENTER)
    base.require(backend.status_code == 200, "backend center readback failed")
    github = base.public_get(GITHUB_RELEASE)
    base.require(github.status_code == 200 and "v0.62.12" in github.text, "GitHub release readback failed")
    return {
        "concept_latest_record_id": record_id,
        "concept_latest_version": VERSION,
        "predecessor_version_index": PREDECESSOR_RELATION_INDEX,
        "successor_version_index": int(successor_relation["index"]),
        "exactly_one_successor_version": True,
        "successor_doi_resolution": "pass",
        "concept_doi_latest_resolution": "pass",
        "predecessor_doi_resolution_unchanged": "pass",
        "predecessor_open_unchanged": True,
        "predecessor_stable_metadata_unchanged": True,
        "predecessor_file_order_unchanged": True,
        "predecessor_anonymous_readback": "pass_100_of_100",
        "student_site_readback": "pass",
        "backend_center_readback": "pass",
        "github_release_readback": "pass",
    }


def write_receipts(record: dict[str, Any], observed: list[dict[str, Any]], predecessor_metadata: dict[str, Any], predecessor_rows: list[dict[str, Any]], github: dict[str, Any], lineage: dict[str, Any], draft_id: int, newversion_http_201_observed: bool, deleted: int, uploaded: int, execution_mode: str, reservation_route: str) -> tuple[int, str]:
    metadata = record["metadata"]
    publisher = Path(__file__).resolve()
    base.require(metadata.get("access_right") == "open", "successor is not open")
    base.require(lineage.get("exactly_one_successor_version") is True, "single-successor proof is absent")
    base.require(len(observed) == EXPECTED_FILES, "successor observation count differs")
    observed_by_name = {str(row["name"]): row for row in observed}
    base.require(len(observed_by_name) == EXPECTED_FILES, "successor observation names are not unique")
    local_rows, _, _, _ = local_inventory()
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
        base.compact_sha(metadata.get("contributors", [])) == base.compact_sha(predecessor_metadata.get("contributors", [])),
        "contributor credits differ from predecessor",
    )
    payload = [{"name": row["name"], "bytes": row["bytes"], "md5": row["md5"], "sha256": row["sha256"], "anonymous_url": row["url"], "anonymous_byte_identity": True, "provenance": "v0.62.12_method_capsule_additive" if row["name"] in ADDITIONS else "retained_exact_from_v0.62.11"} for row in observed]
    receipt = {
        "schema_id": "program-matematika-indonesia/zenodo-publication-receipt/1.1.0",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "state": "published_open_method_capsule_successor",
        "version": VERSION,
        "student_entry": {"primary_url": LEARNER_SITE, "backend_center_url": BACKEND_CENTER, "description_first_href": LEARNER_SITE, "related_identifiers_first": LEARNER_SITE, "zenodo_default_preview": LEARNER_FILE, "machine_backend_is_secondary": True},
        "workflow_evidence": {"program_course_capsules": 40, "audited_native_implementation_families": 33, "adapter_bound_roles": ADAPTER_BOUND_ROLES, "adapter_bound_role_count": 5, "native_roles_retained_without_adapter_claim": 35, "architecture": "independent_native_backends_then_comparative_audit_then_additive_capsule_and_thin_adapters", "native_owner_identity_and_rights_preserved": True},
        "zenodo": {"record_id": int(record["id"]), "version_doi": record["doi"], "concept_record_id": CONCEPT_ID, "concept_doi": record["conceptdoi"], "predecessor_record_id": PREDECESSOR_ID, "predecessor_doi": f"10.5281/zenodo.{PREDECESSOR_ID}", "access_right": metadata["access_right"], "license": base.license_id(metadata), "language": metadata["language"], "publication_date": metadata["publication_date"], "file_count": len(payload), "anonymous_readback": "pass_100_of_100", "concept_latest": "pass"},
        "github_authority": {"release": GITHUB_RELEASE, "receipt_sha256": base.sha256_bytes(GITHUB_RECEIPT.read_bytes()), "tag_target_commit": github["release"]["tag_target_commit"], "anonymous_readback": github["anonymous_asset_readback"]["result"], "inventory_aggregate_sha256": github["inventory"]["aggregate_sha256"]},
        "replacement_boundary": {"predecessor_files": 100, "retained_exact_files": 81, "omitted_preserved_in_public_predecessor": sorted(OMITTED), "additive_files": sorted(ADDITIONS), "successor_files": 100, "omission_present_to_absent_transitions_observed_in_this_execution": deleted, "addition_absent_to_present_transitions_observed_in_this_execution": uploaded, "draft_id": draft_id, "newversion_http_201_observed": newversion_http_201_observed, "draft_creation_not_inferred_from_http_status": True, "execution_mode": execution_mode, "reservation_route": reservation_route},
        "payload_inventory": payload,
        "payload_inventory_aggregate_sha256": base.inventory_sha(payload),
        "payload_total_bytes": sum(int(row["bytes"]) for row in payload),
        "inheritance": {"predecessor_inventory_aggregate_sha256": base.inventory_sha(predecessor_rows), "predecessor_unchanged": True, "creators_count": len(metadata["creators"]), "creators_canonical_sha256": base.compact_sha(metadata["creators"]), "contributors_count": len(metadata["contributors"]), "contributors_canonical_sha256": base.compact_sha(metadata["contributors"]), "source_and_human_credits_preserved": True, "stable_metadata_preserved": True},
        "lineage_verification": lineage,
        "overall_program_complete": False,
        "model_provenance": MODEL,
        "publisher": {"path": publisher.relative_to(PROJECT).as_posix(), "bytes": publisher.stat().st_size, "sha256": base.sha256_bytes(publisher.read_bytes()), "git_commands_used": 0},
        "anonymous_transport": {"trust_env": False, "netrc_credentials_allowed": False, "authorization_header_allowed": False},
        "privacy": {"credentials_recorded": False, "credential_locator_recorded": False, "absolute_profile_paths_recorded": False, "personal_name_recorded": False},
    }
    data = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    for path in (VERSION_RECEIPT, ROOT_RECEIPT):
        temporary = path.with_name(f".{path.name}.tmp-v06212")
        temporary.write_bytes(data)
        temporary.replace(path)
    return len(data), base.sha256_bytes(data)


def reuse_existing_receipts(record: dict[str, Any], observed: list[dict[str, Any]], github: dict[str, Any]) -> tuple[int, str] | None:
    existing = []
    for path in (VERSION_RECEIPT, ROOT_RECEIPT):
        if path.is_file():
            candidate = json.loads(path.read_text(encoding="utf-8"))
            if candidate.get("version") == VERSION:
                existing.append(path)
    if not existing:
        return None
    data = existing[0].read_bytes()
    base.require(all(path.read_bytes() == data for path in existing), "existing publication receipts differ")
    receipt = json.loads(data.decode("utf-8"))
    # Any older or partially validated receipt is superseded after the current
    # public bytes are revalidated; it is never copied forward merely because
    # a detached aggregate happens to match.
    if receipt.get("schema_id") != "program-matematika-indonesia/zenodo-publication-receipt/1.1.0":
        return None
    if receipt.get("state") != "published_open_method_capsule_successor":
        return None
    if int(receipt.get("zenodo", {}).get("record_id", -1)) != int(record["id"]):
        return None
    if receipt.get("zenodo", {}).get("access_right") != "open":
        return None
    if receipt.get("zenodo", {}).get("anonymous_readback") != "pass_100_of_100":
        return None
    if receipt.get("lineage_verification", {}).get("exactly_one_successor_version") is not True:
        return None
    if receipt.get("anonymous_transport") != {"trust_env": False, "netrc_credentials_allowed": False, "authorization_header_allowed": False}:
        return None
    if any(receipt.get("privacy", {}).get(key) is not False for key in ("credentials_recorded", "credential_locator_recorded", "absolute_profile_paths_recorded", "personal_name_recorded")):
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
    if receipt.get("payload_inventory_aggregate_sha256") != base.inventory_sha(payload):
        return None
    if receipt.get("payload_inventory_aggregate_sha256") != base.inventory_sha(observed):
        return None
    if int(receipt.get("payload_total_bytes", -1)) != sum(int(row["bytes"]) for row in observed):
        return None
    if receipt.get("github_authority", {}).get("receipt_sha256") != base.sha256_bytes(GITHUB_RECEIPT.read_bytes()):
        return None
    publisher = receipt.get("publisher", {})
    current_publisher = Path(__file__).resolve()
    if publisher.get("bytes") != current_publisher.stat().st_size or publisher.get("sha256") != base.sha256_bytes(current_publisher.read_bytes()):
        return None
    for path in (VERSION_RECEIPT, ROOT_RECEIPT):
        if not path.is_file() or path.read_bytes() != data:
            temporary = path.with_name(f".{path.name}.tmp-v06212-restore")
            temporary.write_bytes(data)
            temporary.replace(path)
    return len(data), base.sha256_bytes(data)


base.public_file_stubs = original_public_file_stubs
base.local_inventory = local_inventory
base.predecessor_authority = predecessor_authority
base.related_identifiers = related_identifiers
base.verify_exact_draft = verify_exact_draft
base.verify_final_draft_metadata = verify_final_draft_metadata
base.verify_rdm_learner_preview = verify_rdm_learner_preview
base.verify_lineage = verify_lineage
base.write_receipts = write_receipts
base.reuse_existing_receipts = reuse_existing_receipts


def preflight() -> dict[str, Any]:
    base.require(file_identity(TEMPLATE_SCRIPT) == EXPECTED_TEMPLATE_V06211, "v0.62.11 template identity differs")
    base.require(file_identity(TEMPLATE_V06210) == EXPECTED_TEMPLATE_V06210, "v0.62.10 template identity differs")
    base.require(file_identity(PREDECESSOR_RECEIPT) == EXPECTED_PREDECESSOR_RECEIPT, "predecessor receipt identity differs")
    rows, _, _, github = local_inventory()
    predecessor = json.loads(PREDECESSOR_RECEIPT.read_text(encoding="utf-8"))
    base.require(predecessor.get("version") == PREDECESSOR_VERSION, "predecessor receipt version differs")
    base.require(int(predecessor.get("zenodo", {}).get("record_id", -1)) == PREDECESSOR_ID, "predecessor receipt record differs")
    base.require(predecessor.get("zenodo", {}).get("concept_doi") == f"10.5281/zenodo.{CONCEPT_ID}", "predecessor receipt concept differs")
    base.require(predecessor.get("zenodo", {}).get("access_right") == "open", "predecessor receipt is not open")
    base.require(base.first_href(DESCRIPTION) == LEARNER_SITE, "description is not learner-first")
    base.require(BACKEND_CENTER in DESCRIPTION and GITHUB_RELEASE in DESCRIPTION, "required public links are absent")
    base.require("33 keluarga" in DESCRIPTION and "40 kapsul" in DESCRIPTION, "workflow evidence boundary is absent")
    base.require(len(OMITTED) == len(ADDITIONS) == 19, "replacement boundary cardinality differs")
    base.require(LEARNER_FILE in {row["name"] for row in rows}, "default learner preview is absent")
    return {"status": "PASS_LOCAL_PREFLIGHT_NO_NETWORK_NO_CREDENTIAL_NO_WRITE", "version": VERSION, "concept_doi": f"10.5281/zenodo.{CONCEPT_ID}", "predecessor_record_id": PREDECESSOR_ID, "files": len(rows), "bytes": sum(int(row["bytes"]) for row in rows), "aggregate_sha256": base.inventory_sha(rows), "github_tag_target_commit": github["release"]["tag_target_commit"], "retained_exact_files": 81, "omitted_files": 19, "additive_files": 19, "course_capsules": 40, "audited_native_families": 33, "adapter_bound_roles": ADAPTER_BOUND_ROLES, "native_roles_retained": 35, "learner_entry": LEARNER_SITE, "backend_center": BACKEND_CENTER, "github_release": GITHUB_RELEASE, "default_preview": LEARNER_FILE, "receipt_targets": [VERSION_RECEIPT.name, ROOT_RECEIPT.name]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true", help="local deterministic validation only; no network or writes")
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(preflight(), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return
    if not os.environ.get(TOKEN_FILE_ENV):
        os.environ[TOKEN_FILE_ENV] = str(Path.home() / "Documents/Obsidian notes/New zenodo token.md")
    base.main()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(f"FAIL: {type(exc).__name__}: {detail}", file=sys.stderr)
        raise SystemExit(1)
