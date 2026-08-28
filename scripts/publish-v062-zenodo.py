#!/usr/bin/env python3
"""Publish PMI v0.62.0 to its reserved Zenodo version and verify all public surfaces."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.parse import quote, urlparse

import requests


PROJECT = Path(__file__).resolve().parents[1]
VERSION = "0.62.0"
RELEASE_DIR = PROJECT / "releases" / f"v{VERSION}"
RECORD_ID = 22150264
CONCEPT_ID = 22059707
PREDECESSOR_ID = 22148050
AUTHORITY_SOURCE_COMMIT = ""
RELEASE_COMMIT = ""
LOGBOOK = (
    PROJECT.parents[2]
    / "outputs"
    / "01a01ec1-e685-70d0-b022-211396334723"
    / "curriculum_logbook"
)
ROOT_RECEIPT = PROJECT / f"PUBLICATION_RECEIPT_v{VERSION}.json"
CURRENT_RECEIPT = PROJECT / "PUBLICATION_RECEIPT.json"
LOGBOOK_RECEIPT = LOGBOOK / "144_CENTRAL_V062_PUBLICATION_RECEIPT_20260828.json"

LEARNER_SITE = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
GITHUB_REPOSITORY = "https://github.com/KokunoYumeto/program-matematika-indonesia"
GITHUB_API = "https://api.github.com/repos/KokunoYumeto/program-matematika-indonesia"
GITHUB_RELEASE = f"{GITHUB_REPOSITORY}/releases/tag/v{VERSION}"
ZENODO_DEPOSIT = f"https://zenodo.org/api/deposit/depositions/{RECORD_ID}"
ZENODO_PUBLIC = f"https://zenodo.org/api/records/{RECORD_ID}"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
TITLE = "Program Matematika Indonesia v0.62.0 — Mulai Belajar dan Peta Kurikulum Terbuka"
DESCRIPTION = (
    '<p><strong>Mulai belajar sekarang:</strong> <a href="https://kokunoyumeto.github.io/program-matematika-indonesia/">'
    "buka halaman siswa Program Matematika Indonesia</a>. Halaman ini adalah pintu masuk utama yang dapat dibaca manusia—bukan "
    "katalog JSON—dengan jalur prasyarat, pencarian mata kuliah, status edisi, dan tautan langsung ke pembaca matematika.</p>"
    "<p>Rilis v0.62.0 menerima B20 Kalkulus Diferensial dan D90 Optimisasi Lanjut sebagai edisi lengkap publik, sehingga "
    "katalog pusat memuat 21 peran kursus lengkap pada 20 rekaman edisi berbeda. A10 maju ke checkpoint 32/82 tanpa promosi "
    "kelengkapan; B40 memisahkan buku teks, jawaban bekerja, dan laboratorium Sage; D80 tetap diproduksi pada Unit 050 dengan "
    "D70 sebagai prasyarat kanonik. Program keseluruhan belum lengkap dan status produksi tetap ditandai secara eksplisit. "
    "Untuk mulai tanpa browser, buka <code>00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.62.0.pdf</code> atau "
    "<code>01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.62.0.html</code>.</p>"
    "<p>Lapisan mesin tersedia sebagai pendamping sekunder: katalog kurikulum, authority snapshot, backend federasi v2 dan v2.1, "
    "backend modular v2.2, kontrak kapabilitas global, shard asesmen O001/A00, dan kontrak status belajar lokal-peramban. "
    "Setiap korpus tetap mempertahankan atribusi, "
    "lisensi, provenance, dan otoritas publikasinya sendiri; rekaman ini menggunakan <em>other-open</em> karena paket gabungan "
    "tidak memiliki satu lisensi tunggal.</p>"
    "<p>Produksi, integrasi backend, dan QA rilis dibantu oleh <strong>OpenAI Codex gpt-5.6-sol, Ultra</strong> atas instruksi pengguna. "
    "Semua kredit penulis, penerjemah, editor, dan kontributor manusia yang tercatat tetap dipertahankan.</p>"
)
NOTES = (
    "Snapshot korektif terverifikasi v0.62.0: 21 peran kursus lengkap pada 20 rekaman edisi berbeda; B20 dan D90 lengkap, "
    "A10 32/82, B40 memiliki tiga bahan belajar berbeda, dan D80 memiliki prasyarat D70. Program keseluruhan belum lengkap; "
    "status lengkap dan produksi berjalan ditampilkan secara eksplisit."
)
EXPECTED_CREATOR_COUNT = 2
EXPECTED_CREATOR_SHA256 = "55b0eef2628b12fa0b9dcb5c4c97224f4afda69395a22eec84657b621ab38976"
EXPECTED_CONTRIBUTOR_COUNT = 1
EXPECTED_CONTRIBUTOR_SHA256 = "511a35893f61636bf334c93c32ab573cf0afffe139a641210c60db37fbe435b1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def compact_json_sha256(value: object) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def require_credit_anchors(creators: object, contributors: object, label: str) -> tuple[str, str]:
    require(isinstance(creators, list) and len(creators) == EXPECTED_CREATOR_COUNT, f"{label}: creator count differs")
    require(isinstance(contributors, list) and len(contributors) == EXPECTED_CONTRIBUTOR_COUNT, f"{label}: contributor count differs")
    creator_hash = compact_json_sha256(creators)
    contributor_hash = compact_json_sha256(contributors)
    require(creator_hash == EXPECTED_CREATOR_SHA256, f"{label}: inherited creator array differs")
    require(contributor_hash == EXPECTED_CONTRIBUTOR_SHA256, f"{label}: inherited contributor array differs")
    return creator_hash, contributor_hash


def load_token(token_file: Path) -> str:
    require(token_file.is_file(), "Zenodo credential file is unavailable")
    text = token_file.read_text(encoding="utf-8")
    candidates = re.findall(
        r"(?<![A-Za-z0-9._~-])([A-Za-z0-9._~-]{40,})(?![A-Za-z0-9._~-])",
        text,
    )
    require(bool(candidates), "Zenodo credential file contains no token candidate")
    return max(candidates, key=len)


def request(session: requests.Session, method: str, url: str, **kwargs: object) -> requests.Response:
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


def local_inventory() -> list[dict[str, object]]:
    names = sorted(path.name for path in RELEASE_DIR.iterdir() if path.is_file())
    require("CHECKSUMS.sha256" in names, "release directory has no checksum manifest")
    require(
        f"LOCAL_RELEASE_VALIDATION_v{VERSION}.json" in names,
        "release directory has no local validation receipt",
    )
    rows: list[dict[str, object]] = []
    for name in names:
        path = RELEASE_DIR / name
        require(not path.is_symlink(), f"release file may not be a symlink: {name}")
        rows.append(
            {
                "name": name,
                "path": path,
                "bytes": path.stat().st_size,
                "md5": hash_file(path, "md5"),
                "sha256": hash_file(path, "sha256"),
            }
        )
    checksums = (RELEASE_DIR / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines()
    require(len(checksums) == len(names) - 1, "CHECKSUMS.sha256 row count differs from the derived payload inventory")
    declared: dict[str, str] = {}
    for line in checksums:
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, f"malformed checksum row: {line}")
        declared[match.group(2)] = match.group(1)
    expected = {row["name"] for row in rows if row["name"] != "CHECKSUMS.sha256"}
    require(len(declared) == len(checksums), "checksum inventory contains duplicate filenames")
    require(set(declared) == expected, "checksum inventory does not bind exactly every other release file")
    for row in rows:
        if row["name"] != "CHECKSUMS.sha256":
            require(declared[row["name"]] == row["sha256"], f"checksum mismatch: {row['name']}")
    validation = json.loads((RELEASE_DIR / f"LOCAL_RELEASE_VALIDATION_v{VERSION}.json").read_text(encoding="utf-8"))
    require(validation.get("result") == "pass", "local release validation is not pass")
    require(validation.get("reserved_zenodo_record_id") == RECORD_ID, "local validation record binding differs")
    require(validation.get("checks", {}).get("source_commit_binding") == AUTHORITY_SOURCE_COMMIT, "source commit binding differs")
    return rows


def catalog_and_related_identifiers() -> tuple[dict[str, object], list[dict[str, str]]]:
    catalog_path = RELEASE_DIR / f"program-matematika-indonesia-catalog-v{VERSION}.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    require(catalog.get("sourceCommit") == AUTHORITY_SOURCE_COMMIT, "catalog source commit differs")
    require(catalog.get("program", {}).get("website") == LEARNER_SITE, "catalog learner site differs")
    require(catalog.get("program", {}).get("zenodo") == f"https://doi.org/10.5281/zenodo.{RECORD_ID}", "catalog DOI differs")
    expected_counts = {
        "courseRoles": 40,
        "selectedCorpusRoles": 40,
        "unresolvedRoles": 0,
        "completedPublicCourseRoles": 21,
        "completedPublicRecords": 20,
    }
    require(catalog.get("counts") == expected_counts, "catalog must expose the exact v0.62 21-role/20-record counts")
    dois = catalog.get("program", {}).get("completedPublicRecordDois")
    require(isinstance(dois, list) and len(dois) == 20, "catalog must bind 20 completed public record DOIs")
    normalized: list[str] = []
    for value in dois:
        require(isinstance(value, str), "catalog DOI must be a string")
        doi = value.removeprefix("https://doi.org/")
        require(re.fullmatch(r"10\.5281/zenodo\.\d+", doi) is not None, f"unexpected completed record DOI: {value}")
        normalized.append(doi)
    require(len(normalized) == len(set(normalized)), "catalog completed record DOI list has duplicates")
    require({"10.5281/zenodo.21938930", "10.5281/zenodo.22142120"}.issubset(normalized), "B20/D90 completion DOIs are absent")
    require("10.5281/zenodo.22104724" not in normalized, "obsolete partial D90 DOI remains complete-course authority")
    courses = {row.get("id"): row for row in catalog.get("courses", [])}
    require(courses.get("A10", {}).get("state") == "production" and "32 dari 82" in courses["A10"].get("note", ""), "A10 is not the 32/82 production checkpoint")
    require(courses.get("B20", {}).get("state") == "published" and courses["B20"].get("zenodo") == "https://doi.org/10.5281/zenodo.21938930", "B20 complete-course authority differs")
    require(courses.get("B40", {}).get("state") == "published" and len(courses["B40"].get("supplements", [])) >= 2, "B40 learner materials remain collapsed")
    require(courses.get("D80", {}).get("state") == "production" and set(courses["D80"].get("prerequisites", [])) == {"C30", "C80", "D70"}, "D80 prerequisite correction differs")
    d90 = courses.get("D90", {})
    require(d90.get("state") == "published" and d90.get("zenodo") == "https://doi.org/10.5281/zenodo.22142120" and "22104724" not in json.dumps(d90), "D90 terminal authority differs")
    learner_state = catalog.get("program", {}).get("backend", {}).get("learnerStateV1", {})
    require(
        learner_state
        == {
            "version": "1.0.0",
            "status": "validated",
            "schema": f"https://zenodo.org/records/{RECORD_ID}/files/learner-state-v1.schema.json",
            "storage": "browser-local",
            "privacy": "not-transmitted",
            "derivedEligibilityPersisted": False,
        },
        "learner-state contract differs",
    )
    related = [
        {"identifier": LEARNER_SITE, "relation": "isSupplementTo", "scheme": "url"}
    ]
    related.extend(
        {"identifier": doi, "relation": "references", "scheme": "doi"}
        for doi in normalized
    )
    related.extend(
        [
            {"identifier": GITHUB_REPOSITORY, "relation": "isSupplementTo", "scheme": "url"},
            {"identifier": GITHUB_RELEASE, "relation": "isIdenticalTo", "scheme": "url"},
        ]
    )
    return catalog, related


def anonymous_download(url: str, expected: dict[str, object], label: str) -> dict[str, object]:
    digest = hashlib.sha256()
    observed = 0
    with requests.get(
        url,
        stream=True,
        timeout=(20, 1200),
        headers={"User-Agent": "Program-Matematika-Indonesia-public-readback"},
    ) as response:
        response.raise_for_status()
        for block in response.iter_content(chunk_size=1024 * 1024):
            if block:
                observed += len(block)
                digest.update(block)
    require(observed == expected["bytes"], f"{label}: byte count differs")
    require(digest.hexdigest() == expected["sha256"], f"{label}: SHA-256 differs")
    return {"bytes": observed, "sha256": digest.hexdigest()}


def verify_github(local: list[dict[str, object]]) -> tuple[dict[str, object], list[dict[str, object]]]:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Program-Matematika-Indonesia-public-readback"}
    release_response = requests.get(f"{GITHUB_API}/releases/tags/v{VERSION}", headers=headers, timeout=60)
    release_response.raise_for_status()
    release = release_response.json()
    require(not release.get("draft") and not release.get("prerelease"), "GitHub release is not public final")
    require(release.get("tag_name") == f"v{VERSION}", "GitHub release tag differs")
    require(release.get("html_url") == GITHUB_RELEASE, "GitHub release URL differs")
    by_name = {row["name"]: row for row in release.get("assets", [])}
    require(set(by_name) == {row["name"] for row in local}, "GitHub release asset set differs")
    expected_by_name = {row["name"]: row for row in local}
    for name, remote in by_name.items():
        require(remote.get("size") == expected_by_name[name]["bytes"], f"GitHub API size differs: {name}")

    ref_response = requests.get(f"{GITHUB_API}/git/ref/tags/v{VERSION}", headers=headers, timeout=60)
    ref_response.raise_for_status()
    ref = ref_response.json()["object"]
    require(ref.get("type") == "commit" and ref.get("sha") == RELEASE_COMMIT, "GitHub tag target differs")

    def one(row: dict[str, object]) -> dict[str, object]:
        remote = by_name[row["name"]]
        result = anonymous_download(remote["browser_download_url"], row, f"GitHub {row['name']}")
        return {
            "name": row["name"],
            "bytes": row["bytes"],
            "sha256": row["sha256"],
            "github_url": remote["browser_download_url"],
            "github_anonymous_byte_identity": result["sha256"] == row["sha256"],
        }

    with ThreadPoolExecutor(max_workers=4) as executor:
        inventory = list(executor.map(one, local))
    return release, inventory


def metadata_payload(inherited: dict[str, object], related: list[dict[str, str]]) -> dict[str, object]:
    creators = inherited.get("creators")
    contributors = inherited.get("contributors")
    require(isinstance(creators, list) and len(creators) == 2, "inherited creator array must have two entries")
    require(isinstance(contributors, list) and len(contributors) == 1, "inherited contributor array must have one entry")
    payload: dict[str, object] = {
        "upload_type": inherited.get("upload_type") or "publication",
        "publication_type": inherited.get("publication_type") or "technicalnote",
        "title": TITLE,
        "creators": creators,
        "contributors": contributors,
        "description": DESCRIPTION,
        "access_right": "open",
        "license": "other-open",
        "keywords": inherited.get("keywords") or [],
        "language": "ind",
        "version": VERSION,
        "publication_date": "2026-08-28",
        "related_identifiers": related,
        "notes": NOTES,
    }
    if inherited.get("imprint_publisher"):
        payload["imprint_publisher"] = inherited["imprint_publisher"]
    return payload


def verify_public_zenodo(
    record: dict[str, object],
    local: list[dict[str, object]],
    expected_creators: list[dict[str, object]],
    expected_contributors: list[dict[str, object]],
    expected_related: list[dict[str, str]],
) -> list[dict[str, object]]:
    require(record.get("id") == RECORD_ID, "public Zenodo record ID differs")
    require(record.get("doi") == f"10.5281/zenodo.{RECORD_ID}", "public Zenodo DOI differs")
    require(record.get("conceptdoi") == f"10.5281/zenodo.{CONCEPT_ID}", "public Zenodo concept DOI differs")
    metadata = record.get("metadata", {})
    require(metadata.get("version") == VERSION, "public Zenodo version differs")
    require(metadata.get("title") == TITLE, "public Zenodo title differs")
    require(metadata.get("description") == DESCRIPTION, "public Zenodo description differs")
    require(metadata.get("access_right") == "open", "public Zenodo access is not open")
    license_value = metadata.get("license")
    license_id = license_value.get("id") if isinstance(license_value, dict) else license_value
    require(license_id == "other-open", "public Zenodo license differs")
    require(metadata.get("language") == "ind", "public Zenodo language differs")
    require(metadata.get("creators") == expected_creators, "public Zenodo creators differ from inherited array")
    require(metadata.get("contributors") == expected_contributors, "public Zenodo contributors differ from inherited array")
    require_credit_anchors(metadata.get("creators"), metadata.get("contributors"), "public Zenodo")
    require(metadata.get("related_identifiers") == expected_related, "public Zenodo related identifiers differ")
    require(metadata.get("related_identifiers", [{}])[0].get("identifier") == LEARNER_SITE, "public Zenodo related identifiers are not learner-site-first")
    first_href = re.search(r'href=["\']([^"\']+)', metadata.get("description", ""), flags=re.I)
    require(first_href is not None and first_href.group(1) == LEARNER_SITE, "Zenodo description is not learner-site-first")
    require(MODEL in metadata.get("description", ""), "Zenodo model provenance is absent")
    require("belum lengkap" in metadata.get("description", ""), "Zenodo incomplete-program boundary is absent")

    by_name = {row["key"]: row for row in record.get("files", [])}
    expected_by_name = {row["name"]: row for row in local}
    require(set(by_name) == set(expected_by_name), "public Zenodo file set differs")
    rows: list[dict[str, object]] = []
    for name in sorted(by_name):
        remote = by_name[name]
        expected = expected_by_name[name]
        require(remote.get("size") == expected["bytes"], f"Zenodo API size differs: {name}")
        api_md5 = str(remote.get("checksum", "")).removeprefix("md5:")
        require(api_md5 == expected["md5"], f"Zenodo API MD5 differs: {name}")
        result = anonymous_download(remote["links"]["self"], expected, f"Zenodo {name}")
        rows.append(
            {
                "name": name,
                "bytes": expected["bytes"],
                "sha256": expected["sha256"],
                "zenodo_url": remote["links"]["self"],
                "zenodo_anonymous_byte_identity": result["sha256"] == expected["sha256"],
            }
        )
    return rows


def verify_zenodo_lineage() -> None:
    latest = requests.get(f"https://zenodo.org/api/records/{CONCEPT_ID}/versions/latest", timeout=60)
    latest.raise_for_status()
    require(latest.json().get("id") == RECORD_ID, f"Zenodo concept latest does not resolve to v{VERSION}")
    resolver = requests.get(f"https://doi.org/10.5281/zenodo.{RECORD_ID}", timeout=60)
    resolver.raise_for_status()
    require(urlparse(resolver.url).path.rstrip("/") == f"/records/{RECORD_ID}", "DOI resolver does not end at the exact published record")


def publish_zenodo(
    local: list[dict[str, object]],
    related: list[dict[str, str]],
    token_file: Path,
) -> tuple[dict[str, object], list[dict[str, object]], str, str]:
    public_existing = requests.get(ZENODO_PUBLIC, timeout=30)
    if public_existing.status_code == 200:
        record = public_existing.json()
        require(record.get("metadata", {}).get("version") == VERSION, "record ID already published as another version")
        creators = record["metadata"]["creators"]
        contributors = record["metadata"]["contributors"]
        creator_hash, contributor_hash = require_credit_anchors(creators, contributors, "already-public Zenodo")
        inventory = verify_public_zenodo(record, local, creators, contributors, related)
        verify_zenodo_lineage()
        return record, inventory, creator_hash, contributor_hash
    require(public_existing.status_code == 404, f"unexpected public-record preflight HTTP {public_existing.status_code}")

    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {load_token(token_file)}"})
    draft_response = request(session, "GET", ZENODO_DEPOSIT, timeout=60)
    draft_response.raise_for_status()
    draft = draft_response.json()
    require(draft.get("id") == RECORD_ID and not draft.get("submitted"), "reserved Zenodo draft is not the expected editable record")
    concept_id = draft.get("conceptrecid") or draft.get("metadata", {}).get("relations", {}).get("version", [{}])[0].get("parent", {}).get("pid_value")
    require(concept_id is not None and int(concept_id) == CONCEPT_ID, "Zenodo draft concept differs or is absent")
    inherited_metadata = draft.get("metadata", {})
    creators = inherited_metadata.get("creators")
    contributors = inherited_metadata.get("contributors")
    payload = metadata_payload(inherited_metadata, related)
    creator_hash, contributor_hash = require_credit_anchors(creators, contributors, "reserved Zenodo draft")

    inherited_files = list(draft.get("files", []))
    for remote in inherited_files:
        delete_url = remote.get("links", {}).get("self") or f"{ZENODO_DEPOSIT}/files/{remote['id']}"
        response = request(session, "DELETE", delete_url, timeout=120)
        response.raise_for_status()
    empty = request(session, "GET", ZENODO_DEPOSIT, timeout=60)
    empty.raise_for_status()
    require(empty.json().get("files") == [], "Zenodo draft inventory is not empty after exact inherited-file deletion")

    update = request(session, "PUT", ZENODO_DEPOSIT, json={"metadata": payload}, timeout=120)
    update.raise_for_status()
    draft = update.json()
    bucket = draft.get("links", {}).get("bucket", "").rstrip("/")
    require(bool(bucket), "Zenodo draft has no upload bucket")
    upload_order = [row for row in local if row["name"] != "CHECKSUMS.sha256"]
    upload_order.append(next(row for row in local if row["name"] == "CHECKSUMS.sha256"))
    for row in upload_order:
        with row["path"].open("rb") as stream:
            response = request(
                session,
                "PUT",
                f"{bucket}/{quote(str(row['name']), safe='')}",
                data=stream,
                timeout=(20, 1200),
            )
        response.raise_for_status()

    prepublish_response = request(session, "GET", ZENODO_DEPOSIT, timeout=120)
    prepublish_response.raise_for_status()
    prepublish = prepublish_response.json()
    remote_by_name = {row["filename"]: row for row in prepublish.get("files", [])}
    expected_by_name = {row["name"]: row for row in local}
    require(set(remote_by_name) == set(expected_by_name), "authenticated Zenodo draft inventory differs")
    for name, remote in remote_by_name.items():
        expected = expected_by_name[name]
        require(remote.get("filesize") == expected["bytes"], f"authenticated Zenodo draft size differs: {name}")
        require(str(remote.get("checksum", "")).removeprefix("md5:") == expected["md5"], f"authenticated Zenodo draft MD5 differs: {name}")
    metadata = prepublish.get("metadata", {})
    require(metadata.get("title") == TITLE and metadata.get("version") == VERSION, "authenticated Zenodo draft metadata differs")
    require(metadata.get("access_right") == "open", "authenticated Zenodo draft is not open")
    draft_license = metadata.get("license")
    draft_license_id = draft_license.get("id") if isinstance(draft_license, dict) else draft_license
    require(draft_license_id == "other-open", "authenticated Zenodo draft license differs")
    require(metadata.get("creators") == creators, "authenticated Zenodo draft creators changed")
    require(metadata.get("contributors") == contributors, "authenticated Zenodo draft contributors changed")
    require_credit_anchors(metadata.get("creators"), metadata.get("contributors"), "updated Zenodo draft")
    require(metadata.get("related_identifiers") == related, "authenticated Zenodo related identifiers differ")
    require(metadata.get("related_identifiers", [{}])[0].get("identifier") == LEARNER_SITE, "authenticated Zenodo related identifiers are not learner-site-first")

    publish = request(session, "POST", f"{ZENODO_DEPOSIT}/actions/publish", timeout=180)
    publish.raise_for_status()
    require(publish.json().get("id") == RECORD_ID, "Zenodo publish response record differs")

    record: dict[str, object] | None = None
    for attempt in range(1, 31):
        response = requests.get(ZENODO_PUBLIC, timeout=60)
        if response.status_code == 200:
            candidate = response.json()
            if candidate.get("metadata", {}).get("version") == VERSION:
                record = candidate
                break
        time.sleep(min(10, attempt))
    require(record is not None, "published Zenodo record did not become anonymously readable")
    inventory = verify_public_zenodo(record, local, creators, contributors, related)
    verify_zenodo_lineage()
    return record, inventory, creator_hash, contributor_hash


def verify_student_site() -> dict[str, object]:
    expected_paths = [
        ("index.html", LEARNER_SITE),
        ("courses.js", f"{LEARNER_SITE}courses.js"),
        ("data/curriculum-authority-v1.json", f"{LEARNER_SITE}data/curriculum-authority-v1.json"),
        ("data/learner-read-model.json", f"{LEARNER_SITE}data/learner-read-model.json"),
        ("learner-state.js", f"{LEARNER_SITE}learner-state.js"),
        ("schema/v1/learner-state-v1.schema.json", f"{LEARNER_SITE}schema/v1/learner-state-v1.schema.json"),
        ("schema/v2.2/global-capability-contract-v0.1.schema.json", f"{LEARNER_SITE}schema/v2.2/global-capability-contract-v0.1.schema.json"),
    ]
    rows = []
    for relative, url in expected_paths:
        local_path = PROJECT / "docs" / relative
        local_bytes = local_path.read_bytes()
        remote_bytes: bytes | None = None
        for attempt in range(1, 31):
            response = requests.get(url, timeout=60, headers={"User-Agent": "Program-Matematika-Indonesia-public-readback"})
            if response.status_code == 200 and response.content == local_bytes:
                remote_bytes = response.content
                break
            time.sleep(min(10, attempt))
        require(remote_bytes is not None, f"GitHub Pages byte identity did not converge: {relative}")
        rows.append({"path": relative, "url": url, "bytes": len(local_bytes), "sha256": sha256_bytes(local_bytes)})
    root_text = (PROJECT / "docs" / "index.html").read_text(encoding="utf-8")
    require("Mulai" in root_text and "JSON" in root_text, "learner root does not preserve learner/machine boundary")
    return {
        "result": "pass",
        "primary_url": LEARNER_SITE,
        "machine_surfaces_are_secondary": True,
        "exact_byte_readbacks": rows,
    }


def write_receipt(
    local: list[dict[str, object]],
    github_release: dict[str, object],
    github_inventory: list[dict[str, object]],
    zenodo_record: dict[str, object],
    zenodo_inventory: list[dict[str, object]],
    creator_hash: str,
    contributor_hash: str,
    student_site: dict[str, object],
    catalog: dict[str, object],
) -> tuple[int, str]:
    github_by_name = {row["name"]: row for row in github_inventory}
    zenodo_by_name = {row["name"]: row for row in zenodo_inventory}
    payload = []
    for row in local:
        payload.append(
            {
                "name": row["name"],
                "bytes": row["bytes"],
                "sha256": row["sha256"],
                "github_url": github_by_name[row["name"]]["github_url"],
                "zenodo_url": zenodo_by_name[row["name"]]["zenodo_url"],
                "github_anonymous_byte_identity": True,
                "zenodo_anonymous_byte_identity": True,
            }
        )
    aggregate = sha256_bytes(
        ("".join(f"{row['sha256']}  {row['name']}\n" for row in sorted(payload, key=lambda item: item["name"]))).encode("utf-8")
    )
    total_bytes = sum(int(row["bytes"]) for row in local)
    metadata = zenodo_record["metadata"]
    backend = catalog["program"]["backend"]
    federation = backend["federationV2"]
    assessment = backend["assessmentInventoryV1"]["counts"]
    capability_contract = json.loads(
        (PROJECT / "backend/v2.2/global-capability-contract-v0.1.0.json").read_text(encoding="utf-8")
    )
    receipt = {
        "schema_id": "program-matematika-indonesia/combined-publication-receipt/v18",
        "version": VERSION,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "state": "published_current_release_authority",
        "overall_program_complete": False,
        "credentials_recorded": False,
        "model_provenance": MODEL,
        "student_entry": student_site,
        "curriculum_state": {
            "course_roles": catalog["counts"]["courseRoles"],
            "selected_corpus_roles": catalog["counts"]["selectedCorpusRoles"],
            "unresolved_roles": catalog["counts"]["unresolvedRoles"],
            "completed_public_course_roles": catalog["counts"]["completedPublicCourseRoles"],
            "completed_public_records": catalog["counts"]["completedPublicRecords"],
            "completion_scope_note": "The program remains in production; completed and in-progress course editions remain explicitly distinguished.",
        },
        "local_release": {
            "directory": f"releases/v{VERSION}",
            "files": len(local),
            "bytes": total_bytes,
            "checksum_manifest_entries": len(local) - 1,
            "checksum_manifest_sha256": next(row["sha256"] for row in local if row["name"] == "CHECKSUMS.sha256"),
            "validation_result": "pass",
            "authority_source_commit": AUTHORITY_SOURCE_COMMIT,
            "release_commit": RELEASE_COMMIT,
            "payload_inventory_aggregate_sha256": aggregate,
        },
        "github": {
            "repository": GITHUB_REPOSITORY,
            "release": GITHUB_RELEASE,
            "tag": f"v{VERSION}",
            "tag_kind": "lightweight",
            "tag_target": RELEASE_COMMIT,
            "draft": False,
            "prerelease": False,
            "published_at": github_release.get("published_at"),
            "asset_count": len(github_inventory),
            "asset_bytes": total_bytes,
            "anonymous_filename_size_sha256_readback": f"pass_{len(local)}_of_{len(local)}",
        },
        "zenodo": {
            "record_id": RECORD_ID,
            "version_doi": zenodo_record["doi"],
            "concept_doi": zenodo_record["conceptdoi"],
            "public_record": f"https://zenodo.org/records/{RECORD_ID}",
            "version": metadata["version"],
            "publication_date": metadata["publication_date"],
            "access_right": metadata["access_right"],
            "license": "other-open",
            "file_count": len(zenodo_inventory),
            "total_bytes": total_bytes,
            "anonymous_filename_size_sha256_readback": f"pass_{len(local)}_of_{len(local)}",
            "description_first_href": LEARNER_SITE,
            "related_identifiers_first": LEARNER_SITE,
            "credits_inherited_from_record_id": PREDECESSOR_ID,
            "machine_layer_secondary": True,
            "creator_array_count": len(metadata["creators"]),
            "creator_array_canonical_sha256": creator_hash,
            "contributor_array_count": len(metadata["contributors"]),
            "contributor_array_canonical_sha256": contributor_hash,
            "source_and_human_credits_preserved": True,
        },
        "backend_state": {
            "layers": len(capability_contract["layers"]),
            "capabilities": len(capability_contract["capability_profiles"]),
            "validation_gates": len(capability_contract["validation_gates"]),
            "federation_records": federation["recordCount"],
            "datasets": federation["datasetCount"],
            "courses": federation["courseCount"],
            "reader_surfaces": federation["learnerSurfaceCount"],
            "web_routes": federation["webRouteCount"],
            "identity_crosswalks": federation["identityCrosswalkCount"],
            "publication_events": federation["publicationEventCount"],
            "qa_events": federation["qaEventCount"],
            "assessment_items": assessment["assessments"],
            "assessment_solutions": assessment["solutions"],
            "assessment_solution_gaps": assessment["solution_gaps"],
        },
        "payload_inventory": payload,
        "privacy": {"credentials_recorded": False, "credential_values_in_public_artifacts": False},
        "publication_boundary_result": {
            "github_release": "pass",
            "zenodo_open_record": "pass",
            "github_pages_student_entry": "pass",
            "overall_public_release": "pass",
        },
    }
    data = canonical_bytes(receipt)
    ROOT_RECEIPT.write_bytes(data)
    CURRENT_RECEIPT.write_bytes(data)
    LOGBOOK_RECEIPT.write_bytes(data)
    return len(data), sha256_bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority-source-commit", required=True)
    parser.add_argument("--release-commit", required=True)
    parser.add_argument("--token-file", required=True, type=Path)
    args = parser.parse_args()
    require(re.fullmatch(r"[0-9a-f]{40}", args.authority_source_commit) is not None, "authority source commit is invalid")
    require(re.fullmatch(r"[0-9a-f]{40}", args.release_commit) is not None, "release commit is invalid")
    global AUTHORITY_SOURCE_COMMIT, RELEASE_COMMIT
    AUTHORITY_SOURCE_COMMIT = args.authority_source_commit
    RELEASE_COMMIT = args.release_commit

    local = local_inventory()
    catalog, related = catalog_and_related_identifiers()
    github_release, github_inventory = verify_github(local)
    student_site = verify_student_site()
    zenodo_record, zenodo_inventory, creator_hash, contributor_hash = publish_zenodo(
        local,
        related,
        args.token_file.resolve(),
    )
    receipt_bytes, receipt_sha256 = write_receipt(
        local,
        github_release,
        github_inventory,
        zenodo_record,
        zenodo_inventory,
        creator_hash,
        contributor_hash,
        student_site,
        catalog,
    )
    print(
        json.dumps(
            {
                "result": "published_and_anonymously_verified",
                "github_release": GITHUB_RELEASE,
                "zenodo_record": f"https://zenodo.org/records/{RECORD_ID}",
                "files": len(local),
                "bytes": sum(int(row["bytes"]) for row in local),
                "receipt_bytes": receipt_bytes,
                "receipt_sha256": receipt_sha256,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
