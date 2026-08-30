#!/usr/bin/env python3
"""Publish and independently verify the additive PMI v0.62.8 live overlay.

The reserved record ID is intentionally a required argument because Zenodo
assigns it at reservation time.  The script never deletes or replaces inherited
v0.62.7 files: it proves the exact 98-file predecessor inventory, uploads only
the five fixed validated additive files, publishes publicly, and then performs
anonymous filename/byte/SHA-256 readback of all 103 successor files and all 98
unchanged predecessor files.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import time
from urllib.parse import quote, urlparse
import zipfile

import requests


PROJECT = Path(__file__).resolve().parents[1]
VERSION = "0.62.8"
PREDECESSOR_VERSION = "0.62.7"
FROZEN_AUTHORITY_VERSION = "0.62.0"
CONCEPT_ID = 22059707
PREDECESSOR_ID = 22167525
EXPECTED_INHERITED_FILES = 98
EXPECTED_TOTAL_FILES = 103
PUBLIC_API = "https://zenodo.org/api/records"
DEPOSIT_API = "https://zenodo.org/api/deposit/depositions"
LEARNER_SITE = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
D80_READER_URL = "https://kokunoyumeto.github.io/metode-aljabar-jilid-2-id/"
D80_READER_BYTES = 4_241_400
D80_READER_SHA256 = "01cc636f087d9d8bcee9d227ad48e27c3f3a1b808569f5043420eea58333ef37"
REPOSITORY = "https://github.com/KokunoYumeto/program-matematika-indonesia"
GITHUB_RELEASE = f"{REPOSITORY}/releases/tag/v{VERSION}"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
PUBLICATION_DATE = "2026-08-30"
RELEASE_DIR = PROJECT / "releases" / "v0.62.8"
VERSION_RECEIPT = PROJECT / f"PUBLICATION_RECEIPT_v{VERSION}.json"
ROOT_RECEIPT = PROJECT / "PUBLICATION_RECEIPT.json"

OVERLAY_NAMES = (
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.8.html",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.8.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.8.zip",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.8.json",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.8.sha256",
)
EXPECTED_OVERLAY_IDS = (
    "A10", "A20", "A30", "B20", "B30", "B50", "B95", "C10", "C90", "C100",
    "C140", "D10", "D20", "D30", "D40", "D50", "D60", "D70", "D80", "D100",
)
EXPECTED_PUBLISHED_ROLE_IDS = (
    "A00", "A10", "B10", "B20", "B40", "B50", "B60", "B80", "B90", "C10", "C30",
    "C40", "C60", "C70", "C80", "C90", "C100", "C110", "C120", "C130",
    "D20", "D50", "D70", "D80", "D90", "D110", "D120",
)
EXPECTED_RECORD_DOIS = (
    "https://doi.org/10.5281/zenodo.21932787",
    "https://doi.org/10.5281/zenodo.22052196",
    "https://doi.org/10.5281/zenodo.22053905",
    "https://doi.org/10.5281/zenodo.22060439",
    "https://doi.org/10.5281/zenodo.22062005",
    "https://doi.org/10.5281/zenodo.22062017",
    "https://doi.org/10.5281/zenodo.22062144",
    "https://doi.org/10.5281/zenodo.22062449",
    "https://doi.org/10.5281/zenodo.22070458",
    "https://doi.org/10.5281/zenodo.22070653",
    "https://doi.org/10.5281/zenodo.22070683",
    "https://doi.org/10.5281/zenodo.22070943",
    "https://doi.org/10.5281/zenodo.22073823",
    "https://doi.org/10.5281/zenodo.22075088",
    "https://doi.org/10.5281/zenodo.22088947",
    "https://doi.org/10.5281/zenodo.22102628",
    "https://doi.org/10.5281/zenodo.22105195",
    "https://doi.org/10.5281/zenodo.22105443",
    "https://doi.org/10.5281/zenodo.22142120",
    "https://doi.org/10.5281/zenodo.22151139",
    "https://doi.org/10.5281/zenodo.22160944",
    "https://doi.org/10.5281/zenodo.22161090",
    "https://doi.org/10.5281/zenodo.22163372",
    "https://doi.org/10.5281/zenodo.22163663",
    "https://doi.org/10.5281/zenodo.22164136",
    "https://doi.org/10.5281/zenodo.22164668",
)
CHECKSUM_NAME = "LIVE_OVERLAY_CHECKSUMS_v0.62.8.sha256"
MANIFEST_NAME = "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.8.json"
VALIDATION_NAME = "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.8.json"
HTML_NAME = "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.8.html"
SOURCE_ZIP_NAME = "program-matematika-indonesia-live-overlay-source-v0.62.8.zip"
BACKEND_ARCHIVE_NAME = "program-matematika-indonesia-backend-v2.3-conformance-v0.1.1.zip"
BACKEND_RECEIPT_NAMES = (
    "GLOBAL_BACKEND_V23_SCOPE_ADMISSION_RECEIPT_v0.62.5.json",
    "GLOBAL_BACKEND_V23_VALIDATION_RECEIPT_v0.62.5.json",
    "GLOBAL_BACKEND_V23_ARCHIVE_DETERMINISM_RECEIPT_v0.62.5.json",
)
PRIVATE_MARKERS = (
    b"c:" + b"\\users\\", b"c:" + b"/" + b"users/", b"file:" + b"//",
    b".codex" + b"/attachments", b"new " + b"zenodo " + b"token.md",
    b"github " + b"tokens.md", b"zenodo " + b"token.md",
    b"/" + b"users/", b"/" + b"home/",
)

TITLE = "Program Matematika Indonesia v0.62.8 — Pembaca HTML D80 Terkoreksi"
DESCRIPTION_PREFIX = (
    '<p><strong>Mulai belajar sekarang:</strong> <a href="https://kokunoyumeto.github.io/program-matematika-indonesia/">'
    "buka halaman siswa Program Matematika Indonesia</a>. Ini adalah pintu masuk utama yang dapat dibaca manusia, "
    "dengan jalur prasyarat, pencarian mata kuliah, status edisi terkini, dan tautan langsung ke bahan belajar.</p>"
    "<p>Versi v0.62.8 memperbaiki rute belajar D80: katalog siswa kini membuka pembaca HTML daring yang telah "
    "divalidasi pada tampilan desktop dan seluler dengan 27.308 formula, nol kesalahan MathJax, dan pengguliran lokal untuk matematika lebar. "
    "PDF 864 halaman tetap menjadi edisi unduhan. ZIP HTML luring pada Zenodo lama belum ditawarkan sebagai rute siswa sampai versi terkoreksi diterbitkan oleh pemilik korpus. "
    "Seluruh 98 berkas v0.62.7 diwarisi tanpa perubahan. Snapshot otoritas v0.62.0 tetap "
    "dibedakan dari status publikasi langsung; program keseluruhan belum lengkap dan pekerjaan produksi terus berjalan.</p>"
    "<p>Lapisan JSON dan backend mesin tetap tersedia sebagai pendamping sekunder, bukan sebagai pintu masuk siswa. "
    "Setiap korpus mempertahankan atribusi, lisensi, provenance, dan otoritas publikasinya sendiri; paket gabungan "
    "menggunakan lisensi <em>other-open</em> karena tidak memiliki satu lisensi tunggal.</p>"
    "<p>Produksi, integrasi, dan QA rilis dibantu oleh <strong>OpenAI Codex gpt-5.6-sol, Ultra</strong> atas instruksi "
    "pengguna. Semua kredit sumber dan kontributor manusia yang diwarisi tetap dipertahankan.</p>"
)
NOTES_PREFIX = (
    "Rilis aditif v0.62.8: lima berkas overlay siswa mengarahkan D80 ke pembaca HTML daring yang "
    "telah divalidasi dan tidak menawarkan ZIP HTML luring lama; semua 98 berkas v0.62.7 dipertahankan "
    "byte-for-byte. Program keseluruhan belum lengkap."
)

# These are fields accepted by the legacy Zenodo deposition metadata API that
# remain meaningful across versions.  Release-specific fields are replaced
# below; server-managed DOI/version-relation fields are deliberately omitted.
PRESERVED_DEPOSITION_FIELDS = (
    "upload_type",
    "publication_type",
    "image_type",
    "creators",
    "contributors",
    "keywords",
    "communities",
    "grants",
    "references",
    "subjects",
    "locations",
    "dates",
    "method",
    "imprint_publisher",
    "imprint_isbn",
    "imprint_place",
    "journal_title",
    "journal_volume",
    "journal_issue",
    "journal_pages",
    "conference_title",
    "conference_acronym",
    "conference_dates",
    "conference_place",
    "conference_url",
    "conference_session",
    "partof_title",
    "partof_pages",
    "thesis_supervisors",
    "thesis_university",
)

# Public metadata fields whose exact values must survive from predecessor to
# successor.  Server-generated relations are intentionally excluded because
# Zenodo necessarily advances them when a new version is published.
PRESERVED_PUBLIC_FIELDS = (
    "resource_type",
    "creators",
    "contributors",
    "keywords",
    "communities",
    "grants",
    "references",
    "subjects",
    "locations",
    "dates",
    "method",
    "imprint_publisher",
    "imprint_isbn",
    "imprint_place",
    "journal_title",
    "journal_volume",
    "journal_issue",
    "journal_pages",
    "conference_title",
    "conference_acronym",
    "conference_dates",
    "conference_place",
    "conference_url",
    "conference_session",
    "partof_title",
    "partof_pages",
    "thesis_supervisors",
    "thesis_university",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def compact_sha256(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path, algorithm: str) -> str:
    digest = hashlib.md5(usedforsecurity=False) if algorithm == "md5" else hashlib.new(algorithm)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_token(token_file: Path) -> str:
    require(token_file.is_file(), "Zenodo credential file is unavailable")
    text = token_file.read_text(encoding="utf-8")
    candidates = re.findall(
        r"(?<![A-Za-z0-9._~-])([A-Za-z0-9._~-]{40,})(?![A-Za-z0-9._~-])",
        text,
    )
    require(bool(candidates), "Zenodo credential file contains no token candidate")
    return max(candidates, key=len)


def license_id(metadata: dict[str, object]) -> str | None:
    value = metadata.get("license")
    if isinstance(value, dict):
        raw = value.get("id")
        return str(raw) if raw is not None else None
    return str(value) if value is not None else None


def request_with_retry(
    session: requests.Session,
    method: str,
    url: str,
    **kwargs: object,
) -> requests.Response:
    timeout = kwargs.pop("timeout", (20, 1200))
    last: requests.Response | None = None
    for attempt in range(1, 6):
        response = session.request(method, url, timeout=timeout, **kwargs)
        last = response
        if response.status_code not in {429, 500, 502, 503, 504}:
            return response
        time.sleep(attempt * 1.5)
    require(last is not None, f"no HTTP response: {method} {url}")
    return last


def get_json(url: str, *, timeout: int = 120) -> dict[str, object]:
    response: requests.Response | None = None
    for attempt in range(1, 6):
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Program-Matematika-Indonesia-public-readback"},
        )
        if response.status_code not in {429, 500, 502, 503, 504}:
            break
        time.sleep(attempt * 1.5)
    require(response is not None, f"no HTTP response: GET {url}")
    response.raise_for_status()
    value = response.json()
    require(isinstance(value, dict), f"JSON response is not an object: {url}")
    return value


def read_json(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"{label} is not valid UTF-8 JSON") from exc
    require(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def validation_document_passes(value: dict[str, object], label: str) -> None:
    result = value.get("result", value.get("validation_result"))
    require(result == "pass", f"{label} does not record result=pass")
    declared_version = value.get("version", value.get("program_version", value.get("overlay_version")))
    if declared_version is not None:
        require(str(declared_version).removeprefix("v") == VERSION, f"{label} version differs")


def privacy_scan(name: str, data: bytes) -> None:
    lowered = data.lower()
    found = [marker.decode("ascii", "replace") for marker in PRIVATE_MARKERS if marker in lowered]
    require(not found, f"private marker in {name}: {found}")


def walk_json(value: object):
    yield value
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def inspect_backend_payload(release_dir: Path) -> dict[str, object]:
    archive_path = release_dir / BACKEND_ARCHIVE_NAME
    archive_bytes = archive_path.stat().st_size
    archive_sha256 = hash_file(archive_path, "sha256")
    privacy_scan(BACKEND_ARCHIVE_NAME, archive_path.read_bytes())
    root = "program-matematika-indonesia-backend-v2.3-conformance-v0.1.1/"
    required = (
        "manifest.json", "PACKAGE_CHECKSUMS.sha256", "VALIDATION_RECEIPT.json",
        "SCOPE_AND_LIMITATIONS.json", "tools/generate_v23.py",
        "tools/validate_v23.py", "tools/package_v23.py",
    )
    with zipfile.ZipFile(archive_path) as archive:
        require(archive.testzip() is None, "backend v2.3 ZIP contains a corrupt member")
        names = archive.namelist()
        require(bool(names), "backend v2.3 ZIP is empty")
        require(names == sorted(names) and len(names) == len(set(names)), "backend v2.3 ZIP inventory is not unique/sorted")
        timestamps = set()
        for member in archive.infolist():
            normalized = member.filename.replace("\\", "/")
            pure = PurePosixPath(normalized)
            require(
                normalized.startswith(root) and not pure.is_absolute() and ".." not in pure.parts,
                "backend v2.3 ZIP contains an unsafe or wrong-root path",
            )
            timestamps.add(member.date_time)
            if not member.is_dir():
                privacy_scan(f"{BACKEND_ARCHIVE_NAME}:{normalized}", archive.read(member))
        require(len(timestamps) == 1, "backend v2.3 ZIP member timestamps are not deterministic")
        for suffix in required:
            require(f"{root}{suffix}" in names, f"backend v2.3 ZIP lacks required member: {suffix}")

    receipts: list[dict[str, object]] = []
    for name, kind in zip(BACKEND_RECEIPT_NAMES, ("scope", "validation", "determinism"), strict=True):
        path = release_dir / name
        data = path.read_bytes()
        privacy_scan(name, data)
        value = read_json(path, f"backend v2.3 {kind} receipt")
        flattened = list(walk_json(value))
        lowered = [str(item).lower() for item in flattened if isinstance(item, (str, int, bool))]
        require(
            any(item in {"pass", "passed", "success", "complete", "completed"} for item in lowered),
            f"backend v2.3 {kind} receipt lacks a passing result",
        )
        require(archive_sha256 in flattened and archive_bytes in flattened, f"backend v2.3 {kind} receipt lacks archive binding")
        canonical = json.dumps(value, ensure_ascii=False, sort_keys=True).lower()
        if kind == "scope":
            require("a00" in canonical and "o001" in canonical, "backend v2.3 scope receipt lacks A00/O001")
        elif kind == "validation":
            require(any(item == 13 for item in flattened), "backend v2.3 validation receipt lacks the 13-check gate")
        else:
            require(
                any(token in canonical for token in ("byte-identical", "byte_identical", "byte identical")),
                "backend v2.3 determinism receipt lacks byte-identical evidence",
            )
        receipts.append({"name": name, "bytes": path.stat().st_size, "sha256": hash_file(path, "sha256")})
    return {
        "archive": {"name": BACKEND_ARCHIVE_NAME, "bytes": archive_bytes, "sha256": archive_sha256},
        "receipts": receipts,
        "recursive_privacy_scan": "pass",
    }


def local_release_inventory(
    release_dir: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    require(release_dir.is_dir(), "validated live-overlay release directory is unavailable")
    entries = sorted(release_dir.iterdir(), key=lambda path: path.name)
    require(len(entries) == EXPECTED_TOTAL_FILES, "live-overlay release directory must contain exactly 103 entries")
    require(all(path.is_file() for path in entries), "live-overlay release directory must be flat and file-only")
    require(all(not path.is_symlink() for path in entries), "live-overlay release directory may not contain symlinks")
    names = {path.name for path in entries}
    require(len(names) == EXPECTED_TOTAL_FILES, "live-overlay release directory contains duplicate filenames")
    require(set(OVERLAY_NAMES).issubset(names), "live-overlay release directory is missing a fixed additive file")

    rows: list[dict[str, object]] = []
    for path in entries:
        name = path.name
        rows.append({
            "name": name,
            "path": path,
            "bytes": path.stat().st_size,
            "md5": hash_file(path, "md5"),
            "sha256": hash_file(path, "sha256"),
            "provenance": "v0.62.8_additive" if name in OVERLAY_NAMES else "inherited_v0.62.7",
        })

    checksum_lines = (release_dir / CHECKSUM_NAME).read_text(encoding="utf-8").splitlines()
    declared: dict[str, str] = {}
    for line in checksum_lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\\/]+)", line)
        require(match is not None, f"malformed live-overlay checksum row: {line}")
        name = match.group(2)
        require(name not in declared, f"duplicate live-overlay checksum row: {name}")
        declared[name] = match.group(1)
    expected_checksum_names = names - {CHECKSUM_NAME}
    require(len(declared) == 102, "live-overlay checksum manifest must contain exactly 102 entries")
    require(set(declared) == expected_checksum_names, "live-overlay checksum manifest must bind exactly every other release file")
    by_name = {str(row["name"]): row for row in rows}
    for name, sha256 in declared.items():
        require(by_name[name]["sha256"] == sha256, f"live-overlay SHA-256 differs: {name}")

    manifest = read_json(release_dir / MANIFEST_NAME, "live-overlay manifest")
    validation = read_json(release_dir / VALIDATION_NAME, "live-overlay validation receipt")
    require(
        manifest.get("schema_id") == "program-matematika-indonesia/live-publication-overlay-manifest/v1",
        "live-overlay manifest schema differs",
    )
    require(str(manifest.get("version", "")).removeprefix("v") == VERSION, "live-overlay manifest version differs")
    require(
        manifest.get("curriculum_boundary")
        == {
            "authority_changed": False,
            "authority_file": "curriculum-authority-v1.json",
            "frozen_authority_version": FROZEN_AUTHORITY_VERSION,
            "live_overlay_is_authority_replacement": False,
            "overall_program_complete": False,
        },
        "live-overlay manifest curriculum boundary differs",
    )
    require(
        manifest.get("inventory_contract")
        == {
            "additive_files": 5,
            "checksum_entries": 102,
            "checksum_excludes_only": CHECKSUM_NAME,
            "inherited_files": 98,
            "successor_files": 103,
        },
        "live-overlay manifest inventory contract differs",
    )
    live_state = manifest.get("live_publication_overlay")
    require(isinstance(live_state, dict), "live-overlay manifest state block is absent")
    require(live_state.get("overlay_rows") == 20, "live-overlay manifest row count differs")
    require(live_state.get("selected_course_roles") == 40, "live-overlay manifest selected-role count differs")
    require(live_state.get("effective_published_roles") == 27, "live-overlay manifest published-role count differs")
    require(live_state.get("distinct_completed_public_records") == 26, "live-overlay manifest distinct-record count differs")
    overlay_ids = live_state.get("overlay_ids")
    published_role_ids = live_state.get("effective_published_role_ids")
    record_dois = live_state.get("distinct_record_dois")
    require(overlay_ids == sorted(EXPECTED_OVERLAY_IDS), "live-overlay ID inventory differs")
    require(published_role_ids == list(EXPECTED_PUBLISHED_ROLE_IDS), "published-role ID inventory differs")
    require(record_dois == list(EXPECTED_RECORD_DOIS), "distinct-record DOI inventory differs")
    b95 = manifest.get("b95_learner_route")
    require(isinstance(b95, dict), "B95 learner-route manifest block is absent")
    expected_b95 = {
        "boundary": "R011-B025",
        "pages": 260,
        "next_boundary": "B026",
        "record_id": 22166545,
        "doi": "10.5281/zenodo.22166545",
        "pdf_bytes": 12_440_420,
        "pdf_sha256": "b154484d2d2ddf0a49f0ee9925854f45e86b6e0fb17d241607db9fc27051e99d",
        "backend_records": 9_119,
        "public_assets": 9,
        "learner_route_is_primary": True,
        "machine_data_links_on_learner_page": 0,
        "public_pdf_readback": "exact-byte-match",
    }
    for key, expected in expected_b95.items():
        require(b95.get(key) == expected, f"B95 R011-B025 manifest fact differs: {key}")
    backend_payload = inspect_backend_payload(release_dir)
    backend = manifest.get("inherited_backend_v23_conformance")
    require(isinstance(backend, dict), "backend v2.3 manifest block is absent")
    require(backend.get("version") == "2.3" and backend.get("package_version") == "0.1.1", "backend v2.3 version binding differs")
    require(backend.get("admitted_scope") == ["A00", "O001"], "backend v2.3 scope differs")
    require(backend.get("cross_lane_or_whole_program_claim") is False, "backend v2.3 overclaims scope")
    require(backend.get("student_route_remains_primary") is True, "student route is not primary")
    require(backend.get("machine_artifacts_are_secondary") is True, "machine artifacts are not secondary")
    archive_block = backend.get("archive")
    require(isinstance(archive_block, dict), "backend v2.3 archive inspection block is absent")
    require(archive_block.get("archive") == backend_payload["archive"], "backend v2.3 archive fact differs")
    receipt_block = backend.get("receipts")
    require(isinstance(receipt_block, dict), "backend v2.3 receipt block is absent")
    for expected in backend_payload["receipts"]:
        row = receipt_block.get(expected["name"])
        require(isinstance(row, dict) and row.get("artifact") == expected, f"backend v2.3 receipt fact differs: {expected['name']}")
    validation_document_passes(validation, "live-overlay validation receipt")

    html = (release_dir / HTML_NAME).read_text(encoding="utf-8")
    require(re.search(r"<!doctype\s+html", html, flags=re.I) is not None, "live-overlay learner file is not HTML")
    require("Program Matematika Indonesia" in html, "live-overlay learner HTML has no program identity")
    require(re.search(r"<main(?:\s|>)", html, flags=re.I) is not None, "live-overlay learner HTML has no main content")

    with zipfile.ZipFile(release_dir / SOURCE_ZIP_NAME) as archive:
        require(archive.testzip() is None, "live-overlay source ZIP contains a corrupt member")
        members = archive.infolist()
        require(bool(members), "live-overlay source ZIP is empty")
        for member in members:
            pure = PurePosixPath(member.filename.replace("\\", "/"))
            require(not pure.is_absolute() and ".." not in pure.parts, "live-overlay source ZIP contains an unsafe path")
            if not member.is_dir():
                privacy_scan(f"{SOURCE_ZIP_NAME}:{member.filename}", archive.read(member))
    rows.sort(key=lambda row: str(row["name"]))
    overlay_rows = [row for row in rows if row["name"] in OVERLAY_NAMES]
    require(len(overlay_rows) == 5, "live-overlay additive selection does not contain exactly five files")
    return rows, overlay_rows


def first_description_href(description: object) -> str | None:
    if not isinstance(description, str):
        return None
    match = re.search(r'href=["\']([^"\']+)', description, flags=re.I)
    return match.group(1) if match else None


def public_file_stubs(record: dict[str, object], expected_count: int, label: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for remote in record.get("files", []):
        require(isinstance(remote, dict), f"{label}: malformed file row")
        name = remote.get("key")
        size = remote.get("size")
        md5 = str(remote.get("checksum", "")).removeprefix("md5:")
        links = remote.get("links", {})
        url = links.get("self") if isinstance(links, dict) else None
        require(isinstance(name, str) and name, f"{label}: file has no name")
        require(isinstance(size, int) and size >= 0, f"{label}: invalid size for {name}")
        require(re.fullmatch(r"[0-9a-f]{32}", md5) is not None, f"{label}: invalid MD5 for {name}")
        require(isinstance(url, str) and url.startswith("https://"), f"{label}: file has no HTTPS content URL")
        rows.append({"name": name, "bytes": size, "md5": md5, "url": url})
    rows.sort(key=lambda row: str(row["name"]))
    require(len(rows) == expected_count, f"{label}: expected {expected_count} files, found {len(rows)}")
    require(len({row["name"] for row in rows}) == len(rows), f"{label}: duplicate filenames")
    return rows


def anonymous_download(row: dict[str, object], label: str) -> dict[str, object]:
    last_error: Exception | None = None
    for attempt in range(1, 8):
        sha256 = hashlib.sha256()
        md5 = hashlib.md5(usedforsecurity=False)
        observed = 0
        try:
            with requests.get(
                str(row["url"]),
                stream=True,
                timeout=(20, 1200),
                headers={"User-Agent": "Program-Matematika-Indonesia-public-readback"},
            ) as response:
                if response.status_code in {429, 500, 502, 503, 504}:
                    response.raise_for_status()
                response.raise_for_status()
                for block in response.iter_content(chunk_size=1024 * 1024):
                    if block:
                        observed += len(block)
                        md5.update(block)
                        sha256.update(block)
            require(observed == row["bytes"], f"{label}: byte count differs for {row['name']}")
            require(md5.hexdigest() == row["md5"], f"{label}: MD5 differs for {row['name']}")
            return {
                "name": row["name"],
                "bytes": observed,
                "md5": md5.hexdigest(),
                "sha256": sha256.hexdigest(),
                "url": row["url"],
            }
        except (requests.RequestException, RuntimeError) as exc:
            last_error = exc
            if attempt < 7:
                delay = float(attempt * 2)
                response = exc.response if isinstance(exc, requests.HTTPError) else None
                retry_after = response.headers.get("Retry-After") if response is not None else None
                if retry_after is not None:
                    try:
                        delay = max(delay, min(120.0, float(retry_after)))
                    except ValueError:
                        pass
                time.sleep(delay)
    raise RuntimeError(f"{label}: anonymous readback failed for {row['name']}") from last_error


def anonymous_inventory(record: dict[str, object], expected_count: int, label: str) -> list[dict[str, object]]:
    stubs = public_file_stubs(record, expected_count, label)
    with ThreadPoolExecutor(max_workers=2) as executor:
        rows = list(executor.map(lambda row: anonymous_download(row, label), stubs))
    rows.sort(key=lambda row: str(row["name"]))
    return rows


def compact_file_inventory(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "name": row["name"],
            "bytes": row["bytes"],
            "md5": row["md5"],
            "sha256": row["sha256"],
        }
        for row in sorted(rows, key=lambda item: str(item["name"]))
    ]


def require_predecessor(record: dict[str, object]) -> dict[str, object]:
    require(int(record.get("id", -1)) == PREDECESSOR_ID, "predecessor record ID differs")
    require(record.get("doi") == f"10.5281/zenodo.{PREDECESSOR_ID}", "predecessor DOI differs")
    require(record.get("conceptdoi") == f"10.5281/zenodo.{CONCEPT_ID}", "predecessor concept DOI differs")
    metadata = record.get("metadata", {})
    require(isinstance(metadata, dict), "predecessor metadata is malformed")
    require(metadata.get("version") == PREDECESSOR_VERSION, "predecessor version differs")
    require(metadata.get("access_right") == "open", "predecessor access is not open")
    require(license_id(metadata) == "other-open", "predecessor license differs")
    require(metadata.get("language") == "ind", "predecessor language differs")
    require(isinstance(metadata.get("creators"), list) and metadata["creators"], "predecessor creators are absent")
    require(isinstance(metadata.get("contributors"), list), "predecessor contributors are absent")
    return metadata


def normalized_related(metadata: dict[str, object]) -> list[dict[str, str]]:
    related: list[dict[str, str]] = [
        {"identifier": LEARNER_SITE, "relation": "isSupplementTo", "scheme": "url"}
    ]
    seen = {(LEARNER_SITE, "isSupplementTo", "url")}
    source = metadata.get("related_identifiers", [])
    require(isinstance(source, list), "predecessor related-identifiers array is malformed")
    for raw in source:
        require(isinstance(raw, dict), "predecessor related-identifier row is malformed")
        identifier = raw.get("identifier")
        relation = raw.get("relation")
        scheme = raw.get("scheme")
        require(all(isinstance(value, str) and value for value in (identifier, relation, scheme)), "predecessor related identifier is incomplete")
        key = (str(identifier), str(relation), str(scheme))
        if str(identifier).rstrip("/") == LEARNER_SITE.rstrip("/"):
            continue
        if str(identifier).startswith(f"{REPOSITORY}/releases/tag/"):
            continue
        if key not in seen:
            related.append({"identifier": str(identifier), "relation": str(relation), "scheme": str(scheme)})
            seen.add(key)
    related.append({"identifier": GITHUB_RELEASE, "relation": "isIdenticalTo", "scheme": "url"})
    require(related[0]["identifier"] == LEARNER_SITE, "student site is not the first related identifier")
    require(related[-1]["identifier"] == GITHUB_RELEASE, "current GitHub release is not the final related identifier")
    return related


def release_notes(predecessor_metadata: dict[str, object]) -> str:
    inherited = predecessor_metadata.get("notes")
    if isinstance(inherited, str) and inherited.strip():
        return f"{NOTES_PREFIX}\n\nCatatan rilis pendahulu v0.62.7 (dipertahankan):\n{inherited}"
    return NOTES_PREFIX


def release_description(predecessor_metadata: dict[str, object]) -> str:
    inherited = predecessor_metadata.get("description")
    if isinstance(inherited, str) and inherited.strip():
        return (
            f"{DESCRIPTION_PREFIX}"
            '\n\n<h2>Deskripsi rilis pendahulu v0.62.7 yang dipertahankan</h2>'
            f"{inherited}"
        )
    return DESCRIPTION_PREFIX


def build_metadata_payload(
    draft_metadata: dict[str, object],
    predecessor_metadata: dict[str, object],
    publication_date: str,
) -> tuple[dict[str, object], list[dict[str, str]]]:
    require(draft_metadata.get("creators") == predecessor_metadata.get("creators"), "draft creators differ from predecessor")
    require(draft_metadata.get("contributors") == predecessor_metadata.get("contributors"), "draft contributors differ from predecessor")
    for field in PRESERVED_PUBLIC_FIELDS:
        if field in predecessor_metadata and field in draft_metadata:
            require(draft_metadata[field] == predecessor_metadata[field], f"draft inherited metadata differs: {field}")

    payload = {field: draft_metadata[field] for field in PRESERVED_DEPOSITION_FIELDS if field in draft_metadata}
    require(payload.get("creators") == predecessor_metadata.get("creators"), "creator preservation failed")
    require(payload.get("contributors") == predecessor_metadata.get("contributors"), "contributor preservation failed")
    related = normalized_related(draft_metadata)
    payload.update({
        "title": TITLE,
        "description": release_description(predecessor_metadata),
        "access_right": "open",
        "license": "other-open",
        "language": "ind",
        "version": VERSION,
        "publication_date": publication_date,
        "related_identifiers": related,
        "notes": release_notes(predecessor_metadata),
    })
    require(payload.get("upload_type") is not None, "inherited upload type is absent")
    require(first_description_href(payload["description"]) == LEARNER_SITE, "description is not student-site-first")
    return payload, related


def expected_public_metadata(
    predecessor_metadata: dict[str, object], publication_date: str
) -> tuple[dict[str, object], list[dict[str, str]]]:
    related = normalized_related(predecessor_metadata)
    return {
        "title": TITLE,
        "description": release_description(predecessor_metadata),
        "access_right": "open",
        "license": "other-open",
        "language": "ind",
        "version": VERSION,
        "publication_date": publication_date,
        "creators": predecessor_metadata["creators"],
        "contributors": predecessor_metadata["contributors"],
        "related_identifiers": related,
        "notes": release_notes(predecessor_metadata),
    }, related


def draft_file_facts(draft: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for remote in draft.get("files", []):
        require(isinstance(remote, dict), "draft exposes a malformed file row")
        name = remote.get("filename")
        size = remote.get("filesize")
        md5 = str(remote.get("checksum", "")).removeprefix("md5:")
        require(isinstance(name, str) and name, "draft file has no name")
        require(isinstance(size, int) and size >= 0, f"draft file has invalid size: {name}")
        require(re.fullmatch(r"[0-9a-f]{32}", md5) is not None, f"draft file has invalid MD5: {name}")
        rows.append({"name": name, "bytes": size, "md5": md5})
    rows.sort(key=lambda row: str(row["name"]))
    require(len({row["name"] for row in rows}) == len(rows), "draft contains duplicate filenames")
    return rows


def require_draft_boundary(
    draft_rows: list[dict[str, object]],
    predecessor_rows: list[dict[str, object]],
    overlay_rows: list[dict[str, object]],
) -> set[str]:
    inherited = {str(row["name"]): row for row in predecessor_rows}
    overlay = {str(row["name"]): row for row in overlay_rows}
    remote = {str(row["name"]): row for row in draft_rows}
    require(set(inherited).isdisjoint(overlay), "overlay filename collides with an inherited filename")
    require(set(remote).issubset(set(inherited) | set(overlay)), "draft contains a file outside the 98+5 boundary")
    require(set(inherited).issubset(remote), "draft is missing an inherited predecessor file")
    for name, expected in inherited.items():
        require(remote[name]["bytes"] == expected["bytes"], f"draft inherited size differs: {name}")
        require(remote[name]["md5"] == expected["md5"], f"draft inherited MD5 differs: {name}")
    present_overlay = set(remote) & set(overlay)
    for name in present_overlay:
        require(remote[name]["bytes"] == overlay[name]["bytes"], f"existing draft overlay size differs: {name}")
        require(remote[name]["md5"] == overlay[name]["md5"], f"existing draft overlay MD5 differs: {name}")
    return present_overlay


def upload_one(session: requests.Session, bucket: str, row: dict[str, object]) -> None:
    url = f"{bucket.rstrip('/')}/{quote(str(row['name']), safe='')}"
    last: requests.Response | None = None
    for attempt in range(1, 5):
        with Path(row["path"]).open("rb") as stream:
            response = session.put(url, data=stream, timeout=(20, 1200))
        last = response
        if response.status_code not in {429, 500, 502, 503, 504}:
            response.raise_for_status()
            return
        time.sleep(attempt * 2)
    require(last is not None, f"no upload response for {row['name']}")
    last.raise_for_status()


def verify_public_successor(
    record: dict[str, object],
    record_id: int,
    predecessor_metadata: dict[str, object],
    expected_metadata: dict[str, object],
    expected_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    require(int(record.get("id", -1)) == record_id, "published successor record ID differs")
    require(record.get("doi") == f"10.5281/zenodo.{record_id}", "published successor DOI differs")
    require(record.get("conceptdoi") == f"10.5281/zenodo.{CONCEPT_ID}", "published successor concept DOI differs")
    metadata = record.get("metadata", {})
    require(isinstance(metadata, dict), "published successor metadata is malformed")
    for field in ("title", "description", "access_right", "language", "version", "publication_date", "creators", "contributors", "related_identifiers", "notes"):
        require(metadata.get(field) == expected_metadata[field], f"published successor metadata differs: {field}")
    require(license_id(metadata) == expected_metadata["license"], "published successor license differs")
    require(first_description_href(metadata.get("description")) == LEARNER_SITE, "published description is not student-site-first")
    require(metadata.get("related_identifiers", [{}])[0].get("identifier") == LEARNER_SITE, "published related identifiers are not student-site-first")
    require(MODEL in str(metadata.get("description", "")), "model provenance is absent from published description")
    require("belum lengkap" in str(metadata.get("description", "")), "incomplete-program boundary is absent")
    for field in PRESERVED_PUBLIC_FIELDS:
        if field in predecessor_metadata:
            require(metadata.get(field) == predecessor_metadata[field], f"published inherited metadata differs: {field}")

    observed = anonymous_inventory(record, EXPECTED_TOTAL_FILES, "successor")
    expected = compact_file_inventory(expected_rows)
    require(compact_file_inventory(observed) == expected, "successor 103-file anonymous inventory differs")
    expected_by_name = {str(row["name"]): row for row in expected_rows}
    for row in observed:
        row["provenance"] = expected_by_name[str(row["name"])]["provenance"]
    return observed


def verify_predecessor_unchanged(
    before_record: dict[str, object],
    before_rows: list[dict[str, object]],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    after_record = get_json(f"{PUBLIC_API}/{PREDECESSOR_ID}")
    before_metadata = require_predecessor(before_record)
    after_metadata = require_predecessor(after_record)
    stable_fields = (
        "title", "creators", "contributors", "description", "access_right", "license", "language",
        "version", "publication_date", "keywords", "related_identifiers", "notes",
    ) + PRESERVED_PUBLIC_FIELDS
    before_projection = {field: before_metadata.get(field) for field in stable_fields if field in before_metadata}
    after_projection = {field: after_metadata.get(field) for field in stable_fields if field in after_metadata}
    require(after_projection == before_projection, "predecessor stable metadata changed")
    after_rows = anonymous_inventory(after_record, EXPECTED_INHERITED_FILES, "predecessor-after-publication")
    require(compact_file_inventory(after_rows) == compact_file_inventory(before_rows), "predecessor files changed")
    return after_record, after_rows


def verify_lineage(record_id: int) -> dict[str, object]:
    latest = get_json(f"{PUBLIC_API}/{CONCEPT_ID}/versions/latest")
    require(int(latest.get("id", -1)) == record_id, "concept latest does not resolve to v0.62.8")
    require(latest.get("metadata", {}).get("version") == VERSION, "concept latest version differs")
    for doi_id, expected_path in (
        (record_id, f"/records/{record_id}"),
        (CONCEPT_ID, f"/records/{record_id}"),
        (PREDECESSOR_ID, f"/records/{PREDECESSOR_ID}"),
    ):
        response = requests.get(f"https://doi.org/10.5281/zenodo.{doi_id}", timeout=120)
        response.raise_for_status()
        require(urlparse(response.url).path.rstrip("/") == expected_path, f"DOI resolver target differs: {doi_id}")
    site = requests.get(LEARNER_SITE, timeout=120, headers={"User-Agent": "Program-Matematika-Indonesia-public-readback"})
    site.raise_for_status()
    require("Program Matematika Indonesia" in site.text, "student-facing Pages root is not recognizable")
    b95_url = f"{LEARNER_SITE}id-ID/courses/B95/"
    b95 = requests.get(b95_url, timeout=120, headers={"User-Agent": "Program-Matematika-Indonesia-public-readback"})
    b95.raise_for_status()
    for marker in ("R011-B025", "260", "22166545", "B026"):
        require(marker in b95.text, f"B95 learner Pages route lacks exact marker: {marker}")
    b95_hrefs = re.findall(r'''href=["']([^"']+)["']''', b95.text, flags=re.IGNORECASE)
    require(
        not any(re.search(r"\.(?:jsonl?|csv)(?:[?#]|$)", href, re.IGNORECASE) for href in b95_hrefs),
        "B95 learner Pages route exposes a machine-data href",
    )
    d80 = requests.get(
        D80_READER_URL,
        timeout=120,
        headers={"User-Agent": "Program-Matematika-Indonesia-public-readback"},
    )
    d80.raise_for_status()
    require(len(d80.content) == D80_READER_BYTES, "D80 learner reader byte count differs")
    require(hashlib.sha256(d80.content).hexdigest() == D80_READER_SHA256, "D80 learner reader hash differs")
    require(b"mjx-container" in d80.content and b"Metode" in d80.content, "D80 learner reader is not recognizable")
    github = requests.get(
        GITHUB_RELEASE,
        timeout=120,
        headers={"User-Agent": "Program-Matematika-Indonesia-public-readback"},
    )
    github.raise_for_status()
    require(urlparse(github.url).path.rstrip("/") == urlparse(GITHUB_RELEASE).path, "GitHub release URL differs")
    require("v0.62.8" in github.text and "program-matematika-indonesia" in github.text, "GitHub release page is not recognizable")
    return {
        "concept_latest_record_id": record_id,
        "concept_latest_version": VERSION,
        "successor_doi_resolution": "pass",
        "concept_doi_latest_resolution": "pass",
        "predecessor_doi_resolution_unchanged": "pass",
        "student_site_http_readback": "pass",
        "b95_r011_b025_learner_route_readback": "pass",
        "d80_corrected_html_learner_route_exact_readback": "pass",
        "github_release": GITHUB_RELEASE,
        "github_release_public_readback": "pass",
    }


def publish_or_verify(
    record_id: int,
    token_file: Path,
    publication_date: str,
    predecessor_record: dict[str, object],
    predecessor_metadata: dict[str, object],
    predecessor_rows: list[dict[str, object]],
    overlay_rows: list[dict[str, object]],
) -> tuple[dict[str, object], list[dict[str, object]], dict[str, object], int]:
    expected_metadata, expected_related = expected_public_metadata(predecessor_metadata, publication_date)
    expected_rows: list[dict[str, object]] = []
    for row in predecessor_rows:
        expected_rows.append({**row, "provenance": "inherited_v0.62.7"})
    expected_rows.extend(overlay_rows)
    require(len(expected_rows) == EXPECTED_TOTAL_FILES, "expected successor inventory does not contain 103 files")
    require(len({row["name"] for row in expected_rows}) == EXPECTED_TOTAL_FILES, "expected successor filenames are not unique")

    public_url = f"{PUBLIC_API}/{record_id}"
    existing = requests.get(public_url, timeout=120)
    if existing.status_code == 200:
        record = existing.json()
        observed = verify_public_successor(
            record, record_id, predecessor_metadata, expected_metadata, expected_rows
        )
        return record, observed, expected_metadata, 0
    require(existing.status_code == 404, f"unexpected public successor preflight HTTP {existing.status_code}")

    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {load_token(token_file)}"})
    deposit_url = f"{DEPOSIT_API}/{record_id}"
    draft_response = request_with_retry(session, "GET", deposit_url, timeout=120)
    draft_response.raise_for_status()
    draft = draft_response.json()
    require(int(draft.get("id", -1)) == record_id, "reserved draft record ID differs")
    require(draft.get("submitted") is False, "reserved record is not an editable draft")
    concept_value = draft.get("conceptrecid")
    if concept_value is None:
        relations = draft.get("metadata", {}).get("relations", {}).get("version", [])
        if relations:
            concept_value = relations[0].get("parent", {}).get("pid_value")
    require(concept_value is not None and int(concept_value) == CONCEPT_ID, "reserved draft concept differs")
    draft_metadata = draft.get("metadata", {})
    require(isinstance(draft_metadata, dict), "reserved draft metadata is malformed")
    payload, related = build_metadata_payload(draft_metadata, predecessor_metadata, publication_date)
    require(related == expected_related, "draft/public related-identifier derivation differs")
    present_overlay = require_draft_boundary(draft_file_facts(draft), predecessor_rows, overlay_rows)

    latest_before_mutation = get_json(f"{PUBLIC_API}/{CONCEPT_ID}/versions/latest")
    require(
        int(latest_before_mutation.get("id", -1)) == PREDECESSOR_ID,
        "concept latest advanced after reservation; refusing to mutate a stale successor draft",
    )
    update = request_with_retry(session, "PUT", deposit_url, json={"metadata": payload}, timeout=120)
    update.raise_for_status()
    updated = update.json()
    bucket = updated.get("links", {}).get("bucket")
    require(isinstance(bucket, str) and bucket.startswith("https://"), "reserved draft has no HTTPS upload bucket")

    uploaded_count = 0
    for row in overlay_rows:
        if row["name"] not in present_overlay:
            upload_one(session, bucket, row)
            uploaded_count += 1

    prepublish_response = request_with_retry(session, "GET", deposit_url, timeout=120)
    prepublish_response.raise_for_status()
    prepublish = prepublish_response.json()
    prepublish_rows = draft_file_facts(prepublish)
    require_draft_boundary(prepublish_rows, predecessor_rows, overlay_rows)
    require(len(prepublish_rows) == EXPECTED_TOTAL_FILES, "authenticated successor draft does not contain exactly 103 files")
    remote_by_name = {str(row["name"]): row for row in prepublish_rows}
    for row in expected_rows:
        remote = remote_by_name[str(row["name"])]
        require(remote["bytes"] == row["bytes"], f"authenticated draft size differs: {row['name']}")
        require(remote["md5"] == row["md5"], f"authenticated draft MD5 differs: {row['name']}")
    authenticated_metadata = prepublish.get("metadata", {})
    require(isinstance(authenticated_metadata, dict), "authenticated successor metadata is malformed")
    for field in ("title", "description", "access_right", "language", "version", "publication_date", "creators", "contributors", "related_identifiers", "notes"):
        require(authenticated_metadata.get(field) == payload[field], f"authenticated successor metadata differs: {field}")
    require(license_id(authenticated_metadata) == "other-open", "authenticated successor license differs")
    latest_before_publish = get_json(f"{PUBLIC_API}/{CONCEPT_ID}/versions/latest")
    require(
        int(latest_before_publish.get("id", -1)) == PREDECESSOR_ID,
        "concept latest advanced during upload; refusing to publish a stale successor draft",
    )

    # Publishing is not retried blindly: a lost response after a successful
    # transaction must be resolved by polling the public record, not by sending
    # a second state-changing POST.
    ambiguous_publish_error: Exception | None = None
    try:
        publish = session.post(f"{deposit_url}/actions/publish", timeout=180)
        if publish.status_code in {409, 429, 500, 502, 503, 504}:
            ambiguous_publish_error = RuntimeError(
                f"ambiguous Zenodo publish HTTP {publish.status_code}; checking public state"
            )
        else:
            publish.raise_for_status()
            require(int(publish.json().get("id", -1)) == record_id, "Zenodo publish response record differs")
    except requests.RequestException as exc:
        ambiguous_publish_error = exc

    record: dict[str, object] | None = None
    for attempt in range(1, 31):
        response = requests.get(public_url, timeout=120)
        if response.status_code == 200:
            candidate = response.json()
            if candidate.get("metadata", {}).get("version") == VERSION:
                record = candidate
                break
        time.sleep(min(10, attempt))
    if record is None:
        raise RuntimeError("published successor did not become anonymously readable") from ambiguous_publish_error
    observed = verify_public_successor(
        record, record_id, predecessor_metadata, expected_metadata, expected_rows
    )
    return record, observed, expected_metadata, uploaded_count


def write_receipts(
    version_receipt: Path,
    root_receipt: Path,
    record_id: int,
    publication_date: str,
    successor: dict[str, object],
    successor_rows: list[dict[str, object]],
    predecessor_metadata: dict[str, object],
    predecessor_rows: list[dict[str, object]],
    local_release_rows: list[dict[str, object]],
    overlay_rows: list[dict[str, object]],
    lineage: dict[str, object],
    uploaded_count: int,
) -> tuple[int, str]:
    overlay_names = set(OVERLAY_NAMES)
    payload_inventory = []
    for row in successor_rows:
        payload_inventory.append({
            "name": row["name"],
            "bytes": row["bytes"],
            "sha256": row["sha256"],
            "provenance": "v0.62.8_additive" if row["name"] in overlay_names else "inherited_v0.62.7",
            "anonymous_url": row["url"],
            "anonymous_byte_identity": True,
        })
    payload_inventory.sort(key=lambda row: str(row["name"]))
    predecessor_compact = compact_file_inventory(predecessor_rows)
    overlay_public = [row for row in payload_inventory if row["name"] in overlay_names]
    successor_metadata = successor["metadata"]
    receipt = {
        "schema_id": "program-matematika-indonesia/live-overlay-publication-receipt/v1",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "state": "published_live_overlay_additive",
        "version": VERSION,
        "overall_program_complete": False,
        "student_entry": {
            "primary_url": LEARNER_SITE,
            "github_release": GITHUB_RELEASE,
            "description_first_href": LEARNER_SITE,
            "related_identifiers_first": LEARNER_SITE,
            "machine_surfaces_are_secondary": True,
        },
        "zenodo": {
            "record_id": record_id,
            "version_doi": successor["doi"],
            "concept_record_id": CONCEPT_ID,
            "concept_doi": successor["conceptdoi"],
            "predecessor_record_id": PREDECESSOR_ID,
            "predecessor_doi": f"10.5281/zenodo.{PREDECESSOR_ID}",
            "publication_date": publication_date,
            "access_right": successor_metadata["access_right"],
            "license": "other-open",
            "language": successor_metadata["language"],
            "file_count": len(successor_rows),
            "anonymous_filename_size_sha256_readback": "pass_103_of_103",
            "concept_latest": "pass",
        },
        "inheritance": {
            "inherited_file_count": len(predecessor_rows),
            "predecessor_unchanged": True,
            "predecessor_anonymous_filename_size_sha256_readback": "pass_98_of_98",
            "predecessor_inventory_aggregate_sha256": compact_sha256(predecessor_compact),
            "creator_array_count": len(predecessor_metadata["creators"]),
            "creator_array_canonical_sha256": compact_sha256(predecessor_metadata["creators"]),
            "contributor_array_count": len(predecessor_metadata["contributors"]),
            "contributor_array_canonical_sha256": compact_sha256(predecessor_metadata["contributors"]),
            "source_and_human_credits_preserved": True,
            "relevant_metadata_preserved": True,
        },
        "additive_overlay": {
            "validated_file_count": len(overlay_rows),
            "uploaded_in_this_execution": uploaded_count,
            "no_inherited_file_deleted_or_reuploaded": True,
            "files": overlay_public,
        },
        "local_release": {
            "directory": "releases/v0.62.8",
            "files": len(local_release_rows),
            "checksum_entries": 102,
            "checksum_manifest_sha256": next(
                row["sha256"] for row in local_release_rows if row["name"] == CHECKSUM_NAME
            ),
            "flat_inventory_aggregate_sha256": compact_sha256([
                {"name": row["name"], "bytes": row["bytes"], "sha256": row["sha256"]}
                for row in local_release_rows
            ]),
            "validation_result": "pass",
        },
        "lineage_verification": lineage,
        "payload_inventory": payload_inventory,
        "payload_inventory_aggregate_sha256": compact_sha256([
            {"name": row["name"], "bytes": row["bytes"], "sha256": row["sha256"]}
            for row in payload_inventory
        ]),
        "model_provenance": MODEL,
        "privacy": {
            "credentials_recorded": False,
            "credential_values_in_receipt": False,
            "personal_name_fields_in_receipt": False,
        },
        "publication_boundary_result": {
            "zenodo_open_record": "pass",
            "successor_103_file_readback": "pass",
            "predecessor_98_file_unchanged_readback": "pass",
            "concept_latest": "pass",
            "student_site": "pass",
            "overall": "pass",
        },
    }
    data = canonical_bytes(receipt)
    for path in (version_receipt, root_receipt):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_bytes(data)
        temporary.replace(path)
    return len(data), hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-id", required=True, type=int)
    parser.add_argument("--token-file", required=True, type=Path)
    parser.add_argument("--release-dir", type=Path, default=RELEASE_DIR)
    parser.add_argument("--publication-date", default=PUBLICATION_DATE)
    parser.add_argument("--version-receipt", type=Path, default=VERSION_RECEIPT)
    parser.add_argument("--root-receipt", type=Path, default=ROOT_RECEIPT)
    args = parser.parse_args()
    require(args.record_id > 0 and args.record_id not in {CONCEPT_ID, PREDECESSOR_ID}, "reserved successor record ID is invalid")
    require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.publication_date) is not None, "publication date must be YYYY-MM-DD")

    local_release_rows, overlay_rows = local_release_inventory(args.release_dir.resolve())
    predecessor_record = get_json(f"{PUBLIC_API}/{PREDECESSOR_ID}")
    predecessor_metadata = require_predecessor(predecessor_record)
    predecessor_rows = anonymous_inventory(predecessor_record, EXPECTED_INHERITED_FILES, "predecessor-preflight")
    require(set(OVERLAY_NAMES).isdisjoint({row["name"] for row in predecessor_rows}), "overlay collides with predecessor inventory")
    local_inherited_rows = [row for row in local_release_rows if row["name"] not in OVERLAY_NAMES]
    require(len(local_inherited_rows) == EXPECTED_INHERITED_FILES, "local release does not contain exactly 98 inherited files")
    require(
        compact_file_inventory(local_inherited_rows) == compact_file_inventory(predecessor_rows),
        "local inherited 98-file inventory differs from anonymous predecessor bytes",
    )

    successor, successor_rows, _expected_metadata, uploaded_count = publish_or_verify(
        args.record_id,
        args.token_file.resolve(),
        args.publication_date,
        predecessor_record,
        predecessor_metadata,
        predecessor_rows,
        overlay_rows,
    )
    _predecessor_after, predecessor_after_rows = verify_predecessor_unchanged(
        predecessor_record, predecessor_rows
    )
    lineage = verify_lineage(args.record_id)
    receipt_bytes, receipt_sha256 = write_receipts(
        args.version_receipt.resolve(),
        args.root_receipt.resolve(),
        args.record_id,
        args.publication_date,
        successor,
        successor_rows,
        predecessor_metadata,
        predecessor_after_rows,
        local_release_rows,
        overlay_rows,
        lineage,
        uploaded_count,
    )
    print(json.dumps({
        "result": "published_and_anonymously_verified",
        "version": VERSION,
        "record_id": args.record_id,
        "public_record": f"https://zenodo.org/records/{args.record_id}",
        "successor_files_verified": len(successor_rows),
        "predecessor_files_verified_unchanged": len(predecessor_after_rows),
        "new_files_uploaded": uploaded_count,
        "version_receipt": args.version_receipt.name,
        "root_receipt": args.root_receipt.name,
        "receipt_bytes": receipt_bytes,
        "receipt_sha256": receipt_sha256,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
