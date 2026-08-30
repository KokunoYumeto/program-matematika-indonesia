#!/usr/bin/env python3
"""Publish and anonymously verify PMI v0.62.9 on the existing Zenodo concept."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

import requests


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
RELEASE_DIR = PROJECT / "releases/v0.62.9"
ASSEMBLY_RECEIPT = (
    WORKSPACE
    / "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/171_B10_V231_RELEASE_ASSEMBLY_V0629_20260830.json"
)
GITHUB_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.9.json"
PREDECESSOR_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.8.1.json"
VERSION_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.9.json"
ROOT_RECEIPT = PROJECT / "PUBLICATION_RECEIPT.json"
TOKEN_FILE_ENV = "PMI_V0629_ZENODO_TOKEN_FILE"

PUBLIC_API = "https://zenodo.org/api/records"
DEPOSIT_API = "https://zenodo.org/api/deposit/depositions"
CONCEPT_ID = 22059707
PREDECESSOR_ID = 22167863
PREDECESSOR_VERSION = "0.62.8.1"
VERSION = "0.62.9"
LEARNER_FILE = "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.8.html"
LEARNER_SITE = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
GITHUB_RELEASE = "https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.9"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
USER_AGENT = "Codex-PMI-v0629-Zenodo-Publisher/1.0"

TITLE = "Program Matematika Indonesia v0.62.9 — Adapter Backend B10 v2.3.1"
DESCRIPTION = (
    '<p><strong>Mulai belajar sekarang:</strong> <a href="https://kokunoyumeto.github.io/program-matematika-indonesia/">'
    "buka halaman siswa Program Matematika Indonesia</a>. Halaman ini adalah pintu masuk manusia untuk jalur prasyarat, "
    "status mata kuliah, dan bahan belajar.</p>"
    "<p>Versi 0.62.9 mempertahankan tampilan siswa v0.62.8 dan menambahkan adapter backend lintas-korpus v2.3.1 "
    "yang tervalidasi untuk B10, <em>Discrete Mathematics: An Open Introduction</em>. Berkas JSON, CSV, dan ZIP "
    "adalah infrastruktur mesin sekunder, bukan halaman awal siswa. Penambahan ini tidak menyatakan bahwa seluruh "
    "program 40-peran telah selesai diterjemahkan; program keseluruhan belum lengkap.</p>"
    "<p>Payload penerus tetap 98 berkas: 91 berkas publik versi 0.62.8.1 dipertahankan dan tujuh artefak B10 "
    "ditambahkan. Tujuh artefak historis yang tidak diduplikasi tetap terbuka dan dapat diunduh pada record "
    "pendahulu. Tidak ada record pendahulu yang diubah, ditutup, atau dibatasi.</p>"
    "<p>Hak komponen tidak diratakan. Ketentuan buku/turunan, komponen OPL/WeBWorK dan Open Logic, serta perangkat "
    "lunak, tetap mengikuti bukti hak masing-masing di dalam adapter. Paket gabungan tetap memakai lisensi "
    "<em>other-open</em> karena tidak memiliki satu lisensi tunggal.</p>"
    "<p>Produksi, integrasi, dan QA dibantu oleh <strong>OpenAI Codex gpt-5.6-sol, Ultra</strong> atas instruksi "
    "pengguna. Semua kredit sumber, penulis, dan kontributor manusia yang diwarisi tetap dipertahankan.</p>"
)
NOTES = (
    "Rilis v0.62.9 menambahkan adapter backend B10 v2.3.1 sebagai infrastruktur mesin sekunder. "
    "Situs siswa tetap menjadi pintu masuk utama; program keseluruhan belum lengkap. Payload 98 berkas "
    "mengganti tujuh artefak historis yang tetap dipreservasi pada record pendahulu dengan tujuh artefak B10."
)

OMITTED = {
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.1.html",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.1.sha256",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.1.json",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.1.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.1.zip",
    "140_CENTRAL_V062_ZENODO_DRAFT_RESERVATION_20260828.json",
    "141_CENTRAL_V062_ADMISSION_MANIFEST_20260828.json",
}

ADDITIONS = {
    "program-matematika-indonesia-backend-v2.3.1-b10-adapter-v0.2.0.zip",
    "168_B10_V23_ADAPTER_VALIDATION_V020_FINAL_20260830.json",
    "169_B10_V23_ADAPTER_CANONICAL_ADMISSION_20260830.json",
    "170_B10_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260830.json",
    "GITHUB_B10_V231_SOURCE_PUBLICATION_RECEIPT.json",
    "RELEASE_NOTES_v0.62.9.md",
    "RELEASE_CHECKSUMS_v0.62.9.sha256",
}

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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data, usedforsecurity=False).hexdigest()


def compact_sha(value: Any) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def stable_public_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    result = dict(metadata)
    result.pop("relations", None)
    return result


def version_relation(metadata: dict[str, Any]) -> dict[str, Any]:
    relations = metadata.get("relations", {})
    rows = relations.get("version", []) if isinstance(relations, dict) else []
    require(isinstance(rows, list) and len(rows) == 1 and isinstance(rows[0], dict), "version relation is malformed")
    row = rows[0]
    require(isinstance(row.get("index"), int), "version relation index is malformed")
    require(isinstance(row.get("is_last"), bool), "version relation latest flag is malformed")
    parent = row.get("parent", {})
    require(isinstance(parent, dict), "version relation parent is malformed")
    require(parent.get("pid_type") == "recid", "version relation parent type differs")
    require(int(parent.get("pid_value", -1)) == CONCEPT_ID, "version relation parent differs")
    return row


def inventory_sha(rows: list[dict[str, Any]]) -> str:
    material = "".join(
        f"{row['sha256']}  {row['name']}\n"
        for row in sorted(rows, key=lambda item: str(item["name"]))
    ).encode("utf-8")
    return sha256_bytes(material)


def license_id(metadata: dict[str, Any]) -> str | None:
    value = metadata.get("license")
    if isinstance(value, dict):
        return str(value.get("id")) if value.get("id") is not None else None
    return str(value) if value is not None else None


def first_href(description: Any) -> str | None:
    if not isinstance(description, str):
        return None
    match = re.search(r'href=["\']([^"\']+)', description, flags=re.I)
    return match.group(1) if match else None


def public_get(url: str, *, stream: bool = False, timeout: int = 180) -> requests.Response:
    last = None
    for attempt in range(7):
        try:
            response = requests.get(
                url,
                stream=stream,
                timeout=(20, timeout),
                headers={"User-Agent": USER_AGENT},
            )
        except requests.RequestException:
            response = None
        if response is not None and response.status_code not in (429, 500, 502, 503, 504):
            return response
        if response is not None:
            response.close()
        last = response
        time.sleep(2 * (attempt + 1))
    status = last.status_code if last is not None else 0
    raise RuntimeError(f"public Zenodo retry budget exhausted after HTTP {status}")


def public_json(url: str) -> dict[str, Any]:
    response = public_get(url)
    require(response.status_code == 200, f"public Zenodo JSON returned HTTP {response.status_code}")
    value = response.json()
    require(isinstance(value, dict), "public Zenodo response is not an object")
    return value


def public_rdm_json(record_id: int) -> dict[str, Any]:
    last = None
    for attempt in range(7):
        try:
            response = requests.get(
                f"{PUBLIC_API}/{record_id}",
                timeout=(20, 180),
                headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.inveniordm.v1+json"},
            )
        except requests.RequestException:
            response = None
        if response is not None and response.status_code == 200:
            value = response.json()
            require(isinstance(value, dict), "public InvenioRDM response is not an object")
            require(str(value.get("id")) == str(record_id), "public InvenioRDM record ID differs")
            return value
        if response is not None and response.status_code not in (429, 500, 502, 503, 504):
            raise RuntimeError(f"public InvenioRDM record returned HTTP {response.status_code}")
        last = response
        time.sleep(2 * (attempt + 1))
    status = last.status_code if last is not None else 0
    raise RuntimeError(f"public InvenioRDM retry budget exhausted after HTTP {status}")


def auth_get(client: requests.Session, url: str) -> requests.Response:
    last = None
    for attempt in range(6):
        try:
            response = client.get(url, timeout=(20, 180))
        except requests.RequestException:
            response = None
        if response is not None and response.status_code not in (429, 500, 502, 503, 504):
            return response
        if response is not None:
            response.close()
        last = response
        time.sleep(2 * (attempt + 1))
    status = last.status_code if last is not None else 0
    raise RuntimeError(f"authenticated Zenodo retry budget exhausted after HTTP {status}")


def load_token() -> str:
    locator = os.environ.get(TOKEN_FILE_ENV)
    require(bool(locator), f"{TOKEN_FILE_ENV} is required")
    path = Path(str(locator))
    require(path.is_file(), "configured Zenodo credential file is unavailable")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        raise RuntimeError("configured Zenodo credential file could not be read") from None
    candidates = re.findall(r"(?<![A-Za-z0-9._~-])([A-Za-z0-9._~-]{40,})(?![A-Za-z0-9._~-])", text)
    require(bool(candidates), "configured Zenodo credential file contains no candidate")
    for candidate in sorted(set(candidates), key=len, reverse=True):
        client = requests.Session()
        client.headers.update({"Authorization": f"Bearer {candidate}", "User-Agent": USER_AGENT})
        response = auth_get(client, f"{DEPOSIT_API}/{PREDECESSOR_ID}")
        if response.status_code == 200 and int(response.json().get("id", -1)) == PREDECESSOR_ID:
            return candidate
    raise RuntimeError("no working credential for the exact Zenodo lineage")


def authenticated_session(token: str) -> requests.Session:
    client = requests.Session()
    client.headers.update({"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT})
    return client


def local_inventory() -> tuple[list[dict[str, Any]], dict[str, Path], dict[str, Any], dict[str, Any]]:
    require(RELEASE_DIR.is_dir(), "v0.62.9 release directory is missing")
    require(ASSEMBLY_RECEIPT.is_file(), "assembly receipt is missing")
    require(GITHUB_RECEIPT.is_file(), "GitHub v0.62.9 publication receipt is missing")
    entries = list(RELEASE_DIR.iterdir())
    require(len(entries) == 98, "local release is not exactly 98 entries")
    require(all(path.is_file() and not path.is_symlink() for path in entries), "local release is not flat regular files")
    paths = {path.name: path for path in entries}
    assembly = json.loads(ASSEMBLY_RECEIPT.read_text(encoding="utf-8"))
    github = json.loads(GITHUB_RECEIPT.read_text(encoding="utf-8"))
    require(assembly.get("version") == VERSION, "assembly version differs")
    require(github.get("state") == "published_public_verified", "GitHub release is not public verified")
    require(github.get("tag") == f"v{VERSION}", "GitHub tag differs")
    require(github.get("release", {}).get("url") == GITHUB_RELEASE, "GitHub release URL differs")
    require(github.get("anonymous_asset_readback", {}).get("result") == "pass_98_of_98", "GitHub readback result differs")
    expected_rows = assembly.get("inventory")
    require(isinstance(expected_rows, list) and len(expected_rows) == 98, "assembly inventory differs")
    expected = {str(row["name"]): row for row in expected_rows}
    require(set(expected) == set(paths), "local filenames differ from assembly")
    github_rows = github.get("anonymous_asset_readback", {}).get("entries")
    require(isinstance(github_rows, list) and len(github_rows) == 98, "GitHub readback inventory differs")
    github_by_name = {str(row["name"]): row for row in github_rows}
    require(set(github_by_name) == set(paths), "GitHub/local filename sets differ")
    rows: list[dict[str, Any]] = []
    for name in sorted(paths):
        data = paths[name].read_bytes()
        row = {
            "name": name,
            "path": paths[name],
            "bytes": len(data),
            "md5": md5_bytes(data),
            "sha256": sha256_bytes(data),
        }
        require(row["bytes"] == int(expected[name]["bytes"]), f"assembly size differs: {name}")
        require(row["sha256"] == expected[name]["sha256"], f"assembly hash differs: {name}")
        require(row["bytes"] == int(github_by_name[name]["bytes"]), f"GitHub size differs: {name}")
        require(row["sha256"] == github_by_name[name]["sha256"], f"GitHub hash differs: {name}")
        rows.append(row)
    require(inventory_sha(rows) == assembly["inventory_aggregate_sha256"], "local/assembly aggregate differs")
    require(github.get("inventory", {}).get("aggregate_sha256") == inventory_sha(rows), "GitHub aggregate differs")
    require(set(paths) & OMITTED == set(), "local release retains an exact omission")
    predecessor_names = {str(row["name"]) for row in json.loads(PREDECESSOR_RECEIPT.read_text(encoding="utf-8"))["payload_inventory"]}
    require(set(paths) - predecessor_names == ADDITIONS, "local additive set differs")
    require(predecessor_names - set(paths) == OMITTED, "local omission set differs")
    return rows, paths, assembly, github


def public_file_stubs(record: dict[str, Any], expected_count: int, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for remote in record.get("files", []):
        require(isinstance(remote, dict), f"{label}: malformed file row")
        name = remote.get("key")
        size = remote.get("size")
        md5 = str(remote.get("checksum", "")).removeprefix("md5:")
        links = remote.get("links", {})
        url = links.get("self") if isinstance(links, dict) else None
        require(isinstance(name, str) and name, f"{label}: file has no name")
        require(isinstance(size, int) and size >= 0, f"{label}: invalid file size")
        require(re.fullmatch(r"[0-9a-f]{32}", md5) is not None, f"{label}: invalid MD5")
        require(isinstance(url, str) and url.startswith("https://"), f"{label}: missing public file URL")
        rows.append({"name": name, "bytes": size, "md5": md5, "url": url})
    require(len(rows) == expected_count, f"{label}: file count differs")
    require(len({str(row["name"]) for row in rows}) == expected_count, f"{label}: duplicate filenames")
    return rows


def anonymous_download(stub: dict[str, Any], expected: dict[str, Any], label: str) -> dict[str, Any]:
    last_error = None
    for attempt in range(7):
        response = None
        try:
            response = public_get(str(stub["url"]), stream=True, timeout=1200)
            require(response.status_code == 200, f"{label}: download HTTP differs")
            sha = hashlib.sha256()
            md5 = hashlib.md5(usedforsecurity=False)
            size = 0
            for block in response.iter_content(chunk_size=1024 * 1024):
                if block:
                    sha.update(block)
                    md5.update(block)
                    size += len(block)
            require(size == int(expected["bytes"]), f"{label}: bytes differ for {stub['name']}")
            require(md5.hexdigest() == expected["md5"], f"{label}: MD5 differs for {stub['name']}")
            require(sha.hexdigest() == expected["sha256"], f"{label}: SHA-256 differs for {stub['name']}")
            return {
                "name": stub["name"],
                "bytes": size,
                "md5": md5.hexdigest(),
                "sha256": sha.hexdigest(),
                "url": stub["url"],
                "anonymous_byte_identity": True,
            }
        except (requests.RequestException, RuntimeError) as exc:
            last_error = exc
            time.sleep(2 * (attempt + 1))
        finally:
            if response is not None:
                response.close()
    raise RuntimeError(f"{label}: anonymous download retry budget exhausted") from last_error


def anonymous_inventory(
    record: dict[str, Any],
    expected_rows: list[dict[str, Any]],
    label: str,
) -> list[dict[str, Any]]:
    expected = {str(row["name"]): row for row in expected_rows}
    stubs = public_file_stubs(record, len(expected), label)
    by_name = {str(row["name"]): row for row in stubs}
    require(set(by_name) == set(expected), f"{label}: filename set differs")
    for name, stub in by_name.items():
        require(int(stub["bytes"]) == int(expected[name]["bytes"]), f"{label}: API size differs: {name}")
        require(stub["md5"] == expected[name]["md5"], f"{label}: API MD5 differs: {name}")
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(lambda name: anonymous_download(by_name[name], expected[name], label), sorted(expected)))
    return sorted(rows, key=lambda item: str(item["name"]))


def predecessor_authority(local_rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    record = public_json(f"{PUBLIC_API}/{PREDECESSOR_ID}")
    require(int(record.get("id", -1)) == PREDECESSOR_ID, "predecessor record ID differs")
    require(record.get("conceptdoi") == f"10.5281/zenodo.{CONCEPT_ID}", "predecessor concept differs")
    metadata = record.get("metadata", {})
    require(isinstance(metadata, dict), "predecessor metadata is malformed")
    require(metadata.get("version") == PREDECESSOR_VERSION, "predecessor version differs")
    require(metadata.get("access_right") == "open", "predecessor is not open")
    require(license_id(metadata) == "other-open", "predecessor license differs")
    require(metadata.get("language") == "ind", "predecessor language differs")
    receipt = json.loads(PREDECESSOR_RECEIPT.read_text(encoding="utf-8"))
    predecessor_rows = receipt.get("payload_inventory")
    require(isinstance(predecessor_rows, list) and len(predecessor_rows) == 98, "predecessor receipt inventory differs")
    expected = []
    for row in predecessor_rows:
        expected.append(
            {
                "name": row["name"],
                "bytes": int(row["bytes"]),
                "sha256": row["sha256"],
                "md5": "",
            }
        )
    stubs = {row["name"]: row for row in public_file_stubs(record, 98, "predecessor-stubs")}
    for row in expected:
        require(row["name"] in stubs, f"predecessor missing file: {row['name']}")
        row["md5"] = stubs[row["name"]]["md5"]
    observed = anonymous_inventory(record, expected, "predecessor-before")
    local_names = {str(row["name"]) for row in local_rows}
    require({str(row["name"]) for row in expected} - local_names == OMITTED, "predecessor/local omission boundary differs")
    return record, metadata, observed


def concept_id(draft: dict[str, Any]) -> int:
    value = draft.get("conceptrecid")
    if value is not None:
        return int(value)
    relations = draft.get("metadata", {}).get("relations", {}).get("version", [])
    require(bool(relations), "draft concept relation is absent")
    return int(relations[0]["parent"]["pid_value"])


def draft_file_rows(draft: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for remote in draft.get("files", []):
        require(isinstance(remote, dict), "draft has malformed file row")
        name = remote.get("filename")
        file_id = remote.get("id")
        size = remote.get("filesize")
        md5 = str(remote.get("checksum", "")).removeprefix("md5:")
        require(isinstance(name, str) and name, "draft file has no name")
        require(isinstance(file_id, str) and file_id, "draft file has no ID")
        require(isinstance(size, int) and size >= 0, "draft file has invalid size")
        require(re.fullmatch(r"[0-9a-f]{32}", md5) is not None, "draft file has invalid MD5")
        rows.append({"name": name, "id": file_id, "bytes": size, "md5": md5})
    require(len({str(row["name"]) for row in rows}) == len(rows), "draft filenames are not unique")
    return rows


def get_draft(client: requests.Session, draft_id: int) -> dict[str, Any]:
    response = auth_get(client, f"{DEPOSIT_API}/{draft_id}")
    require(response.status_code == 200, "Zenodo draft is unavailable")
    value = response.json()
    require(int(value.get("id", -1)) == draft_id, "Zenodo draft ID differs")
    require(value.get("submitted") is False, "Zenodo draft is not editable")
    require(concept_id(value) == CONCEPT_ID, "Zenodo draft concept differs")
    return value


def authenticated_predecessor(client: requests.Session) -> dict[str, Any]:
    response = auth_get(client, f"{DEPOSIT_API}/{PREDECESSOR_ID}")
    require(response.status_code == 200, "authenticated predecessor deposition is unavailable")
    value = response.json()
    require(int(value.get("id", -1)) == PREDECESSOR_ID, "authenticated predecessor ID differs")
    require(value.get("submitted") is True, "authenticated predecessor is not published")
    require(concept_id(value) == CONCEPT_ID, "authenticated predecessor concept differs")
    metadata = value.get("metadata", {})
    require(isinstance(metadata, dict), "authenticated predecessor metadata is malformed")
    require(metadata.get("version") == PREDECESSOR_VERSION, "authenticated predecessor version differs")
    require(metadata.get("access_right") == "open", "authenticated predecessor is not open")
    require(license_id(metadata) == "other-open", "authenticated predecessor license differs")
    require(metadata.get("language") == "ind", "authenticated predecessor language differs")
    return value


def verify_draft_metadata_boundary(draft: dict[str, Any], predecessor: dict[str, Any]) -> None:
    metadata = draft.get("metadata", {})
    predecessor_metadata = predecessor.get("metadata", {})
    require(isinstance(metadata, dict), "draft metadata is malformed")
    require(isinstance(predecessor_metadata, dict), "authenticated predecessor metadata is malformed")
    for field in PRESERVED_DEPOSITION_FIELDS:
        require(
            metadata.get(field) == predecessor_metadata.get(field),
            f"draft stable metadata differs from predecessor: {field}",
        )
    require(metadata.get("access_right") == predecessor_metadata.get("access_right") == "open", "draft access differs")
    require(license_id(metadata) == license_id(predecessor_metadata) == "other-open", "draft license differs")
    require(metadata.get("language") == predecessor_metadata.get("language") == "ind", "draft language differs")
    state = (metadata.get("title"), metadata.get("version"))
    allowed_states = {
        (predecessor_metadata.get("title"), predecessor_metadata.get("version")),
        (predecessor_metadata.get("title"), None),
        (TITLE, VERSION),
    }
    require(state in allowed_states, "draft title/version state is outside the predecessor-or-target boundary")


def verify_predecessor_metadata_mapping(
    predecessor: dict[str, Any],
    predecessor_public_metadata: dict[str, Any],
) -> None:
    deposition_metadata = predecessor.get("metadata", {})
    require(isinstance(deposition_metadata, dict), "authenticated predecessor metadata is malformed")
    resource_type = predecessor_public_metadata.get("resource_type", {})
    require(isinstance(resource_type, dict), "public predecessor resource type is malformed")
    require(resource_type.get("type") == deposition_metadata.get("upload_type"), "predecessor upload type mapping differs")
    require(
        resource_type.get("subtype") == deposition_metadata.get("publication_type"),
        "predecessor publication type mapping differs",
    )
    for field in PRESERVED_PUBLIC_FIELDS:
        if field == "resource_type" or field not in predecessor_public_metadata:
            continue
        require(
            deposition_metadata.get(field) == predecessor_public_metadata.get(field),
            f"authenticated/public predecessor metadata differs: {field}",
        )


def latest_draft_id(value: dict[str, Any]) -> int:
    link = value.get("links", {}).get("latest_draft")
    require(isinstance(link, str) and link.startswith("https://"), "Zenodo latest-draft link is absent")
    match = re.search(r"/deposit/depositions/(\d+)$", link.rstrip("/"))
    require(match is not None, "Zenodo latest-draft link is malformed")
    return int(match.group(1))


def legacy_requires_rdm_version_route(response: requests.Response) -> bool:
    if response.status_code != 400:
        return False
    try:
        payload = response.json()
    except ValueError:
        return False
    expected = {
        "status": 400,
        "message": "A validation error occurred.",
        "errors": [{"field": "files.enabled", "messages": ["Please remove all files first."]}],
    }
    return payload == expected


def reserve_or_resume(client: requests.Session) -> tuple[int, bool, str]:
    latest = public_json(f"{PUBLIC_API}/{CONCEPT_ID}/versions/latest")
    require(int(latest.get("id", -1)) == PREDECESSOR_ID, "concept latest changed before reservation")
    predecessor_before = authenticated_predecessor(client)
    existing_id = latest_draft_id(predecessor_before)
    if existing_id != PREDECESSOR_ID:
        get_draft(client, existing_id)
        return existing_id, False, "resumed_existing_draft"
    response = None
    newversion_http_201_observed = False
    reservation_route = "legacy_deposition_newversion"
    try:
        response = client.post(f"{DEPOSIT_API}/{PREDECESSOR_ID}/actions/newversion", timeout=(20, 180))
        newversion_http_201_observed = response.status_code == 201
    except requests.RequestException:
        response = None
    if response is not None and legacy_requires_rdm_version_route(response):
        reservation_route = "inveniordm_record_versions"
        try:
            response = client.post(
                f"{PUBLIC_API}/{PREDECESSOR_ID}/versions",
                json={},
                headers={"Accept": "application/vnd.inveniordm.v1+json", "Content-Type": "application/json"},
                timeout=(20, 180),
            )
        except requests.RequestException:
            response = None
        if response is not None and response.status_code == 201:
            value = response.json()
            draft_id = int(value.get("id", -1))
            require(draft_id > 0 and value.get("is_draft") is True, "InvenioRDM new-version response differs")
            get_draft(client, draft_id)
            return draft_id, True, reservation_route
    if response is not None and response.status_code not in (201, 409, 429, 500, 502, 503, 504):
        raise RuntimeError(f"Zenodo new-version action returned HTTP {response.status_code}")
    predecessor = auth_get(client, f"{DEPOSIT_API}/{PREDECESSOR_ID}")
    require(predecessor.status_code == 200, "authenticated predecessor deposition is unavailable")
    link = predecessor.json().get("links", {}).get("latest_draft")
    if response is not None and response.content:
        try:
            link = response.json().get("links", {}).get("latest_draft", link)
        except ValueError:
            pass
    require(isinstance(link, str) and link.startswith("https://"), "Zenodo latest-draft link is absent")
    match = re.search(r"/deposit/depositions/(\d+)$", link.rstrip("/"))
    require(match is not None, "Zenodo latest-draft link is malformed")
    draft_id = int(match.group(1))
    get_draft(client, draft_id)
    return draft_id, newversion_http_201_observed, reservation_route


def validate_draft_boundary(
    draft: dict[str, Any],
    predecessor_rows: list[dict[str, Any]],
    local_rows: list[dict[str, Any]],
) -> None:
    predecessor = {str(row["name"]): row for row in predecessor_rows}
    local = {str(row["name"]): row for row in local_rows}
    remote = {str(row["name"]): row for row in draft_file_rows(draft)}
    allowed = set(predecessor) | ADDITIONS
    require(set(remote) <= allowed, "draft contains a file outside the exact predecessor/addition boundary")
    require(set(remote) >= set(predecessor) - OMITTED, "draft is missing a retained predecessor file")
    for name in set(remote) & set(predecessor):
        require(int(remote[name]["bytes"]) == int(predecessor[name]["bytes"]), f"draft predecessor size differs: {name}")
        require(remote[name]["md5"] == predecessor[name]["md5"], f"draft predecessor MD5 differs: {name}")
    for name in set(remote) & ADDITIONS:
        require(int(remote[name]["bytes"]) == int(local[name]["bytes"]), f"draft addition size differs: {name}")
        require(remote[name]["md5"] == local[name]["md5"], f"draft addition MD5 differs: {name}")


def delete_omissions(client: requests.Session, draft_id: int) -> int:
    deleted = 0
    for name in sorted(OMITTED):
        draft = get_draft(client, draft_id)
        by_name = {str(row["name"]): row for row in draft_file_rows(draft)}
        if name not in by_name:
            continue
        file_id = by_name[name]["id"]
        response = None
        try:
            response = client.delete(f"{DEPOSIT_API}/{draft_id}/files/{file_id}", timeout=(20, 180))
        except requests.RequestException:
            response = None
        refreshed = get_draft(client, draft_id)
        require(name not in {str(row["name"]) for row in draft_file_rows(refreshed)}, f"draft omission was not deleted: {name}")
        if response is not None:
            require(response.status_code in (204, 404, 429, 500, 502, 503, 504), f"Zenodo delete returned HTTP {response.status_code}")
        deleted += 1
    return deleted


def upload_additions(
    client: requests.Session,
    draft_id: int,
    local_rows: list[dict[str, Any]],
) -> int:
    local = {str(row["name"]): row for row in local_rows}
    uploaded = 0
    for name in sorted(ADDITIONS):
        initial = get_draft(client, draft_id)
        initial_remote = {str(row["name"]): row for row in draft_file_rows(initial)}
        initially_missing = name not in initial_remote
        if not initially_missing:
            require(int(initial_remote[name]["bytes"]) == int(local[name]["bytes"]), f"existing addition size differs: {name}")
            require(initial_remote[name]["md5"] == local[name]["md5"], f"existing addition MD5 differs: {name}")
            continue
        observed = False
        for attempt in range(5):
            draft = get_draft(client, draft_id)
            remote = {str(row["name"]): row for row in draft_file_rows(draft)}
            if name in remote:
                require(int(remote[name]["bytes"]) == int(local[name]["bytes"]), f"existing addition size differs: {name}")
                require(remote[name]["md5"] == local[name]["md5"], f"existing addition MD5 differs: {name}")
                observed = True
                break
            bucket = draft.get("links", {}).get("bucket")
            require(isinstance(bucket, str) and bucket.startswith("https://"), "draft upload bucket is absent")
            try:
                with Path(local[name]["path"]).open("rb") as stream:
                    response = client.put(
                        f"{bucket.rstrip('/')}/{quote(name, safe='')}",
                        data=stream,
                        timeout=(20, 1200),
                    )
            except requests.RequestException:
                response = None
            if response is not None and response.status_code not in (200, 201, 429, 500, 502, 503, 504):
                raise RuntimeError(f"Zenodo upload returned HTTP {response.status_code}")
            time.sleep(2 * (attempt + 1))
            refreshed = get_draft(client, draft_id)
            refreshed_remote = {str(row["name"]): row for row in draft_file_rows(refreshed)}
            if name in refreshed_remote:
                require(int(refreshed_remote[name]["bytes"]) == int(local[name]["bytes"]), f"uploaded addition size differs: {name}")
                require(refreshed_remote[name]["md5"] == local[name]["md5"], f"uploaded addition MD5 differs: {name}")
                observed = True
                break
        if not observed:
            raise RuntimeError(f"Zenodo upload retry budget exhausted: {name}")
        uploaded += int(initially_missing)
    return uploaded


def related_identifiers(predecessor_metadata: dict[str, Any]) -> list[dict[str, str]]:
    result = [{"identifier": LEARNER_SITE, "relation": "isSupplementTo", "scheme": "url"}]
    for row in predecessor_metadata.get("related_identifiers", []):
        if not isinstance(row, dict):
            continue
        identifier = str(row.get("identifier", ""))
        if identifier == LEARNER_SITE:
            continue
        if re.fullmatch(r"https://github\.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v[^/]+", identifier):
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


def metadata_payload(draft: dict[str, Any], predecessor_metadata: dict[str, Any]) -> dict[str, Any]:
    draft_metadata = draft.get("metadata", {})
    require(isinstance(draft_metadata, dict), "draft metadata is malformed")
    require(draft_metadata.get("creators") == predecessor_metadata.get("creators"), "draft creators differ")
    require(draft_metadata.get("contributors") == predecessor_metadata.get("contributors"), "draft contributors differ")
    payload = {field: draft_metadata[field] for field in PRESERVED_DEPOSITION_FIELDS if field in draft_metadata}
    payload.update(
        {
            "title": TITLE,
            "description": DESCRIPTION,
            "access_right": "open",
            "license": "other-open",
            "language": "ind",
            "version": VERSION,
            "publication_date": date.today().isoformat(),
            "related_identifiers": related_identifiers(predecessor_metadata),
            "notes": NOTES,
        }
    )
    require(payload["related_identifiers"][0]["identifier"] == LEARNER_SITE, "related identifiers are not student-first")
    require(first_href(payload["description"]) == LEARNER_SITE, "description is not student-first")
    return payload


def put_metadata(client: requests.Session, draft_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    response = None
    for attempt in range(5):
        try:
            response = client.put(
                f"{DEPOSIT_API}/{draft_id}",
                json={"metadata": payload},
                timeout=(20, 180),
            )
        except requests.RequestException:
            response = None
        if response is not None and response.status_code == 200:
            break
        if response is not None and response.status_code not in (429, 500, 502, 503, 504):
            raise RuntimeError(f"Zenodo metadata update returned HTTP {response.status_code}")
        time.sleep(2 * (attempt + 1))
    require(response is not None and response.status_code == 200, "Zenodo metadata update retry budget exhausted")
    updated = response.json()
    metadata = updated.get("metadata", {})
    for field in (
        "title",
        "description",
        "access_right",
        "language",
        "version",
        "publication_date",
        "creators",
        "contributors",
        "related_identifiers",
        "notes",
    ):
        require(metadata.get(field) == payload[field], f"updated draft metadata differs: {field}")
    require(license_id(metadata) == "other-open", "updated draft license differs")
    return updated


def verify_exact_draft(draft: dict[str, Any], local_rows: list[dict[str, Any]]) -> None:
    remote = {str(row["name"]): row for row in draft_file_rows(draft)}
    local = {str(row["name"]): row for row in local_rows}
    require(len(remote) == 98 and set(remote) == set(local), "final draft is not exact 98-file inventory")
    for name, expected in local.items():
        require(int(remote[name]["bytes"]) == int(expected["bytes"]), f"final draft size differs: {name}")
        require(remote[name]["md5"] == expected["md5"], f"final draft MD5 differs: {name}")


def verify_final_draft_metadata(draft: dict[str, Any], payload: dict[str, Any]) -> None:
    metadata = draft.get("metadata", {})
    require(isinstance(metadata, dict), "final draft metadata is malformed")
    for field, expected in payload.items():
        if field == "license":
            require(license_id(metadata) == expected, "final draft license differs")
        else:
            require(metadata.get(field) == expected, f"final draft target metadata differs: {field}")
    rows = draft.get("files", [])
    require(isinstance(rows, list) and len(rows) == 98, "final draft file list differs")


def rdm_draft(client: requests.Session, draft_id: int) -> dict[str, Any]:
    response = client.get(
        f"{PUBLIC_API}/{draft_id}/draft",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
        timeout=(20, 180),
    )
    require(response.status_code == 200, "InvenioRDM draft is unavailable")
    value = response.json()
    require(str(value.get("id")) == str(draft_id), "InvenioRDM draft ID differs")
    require(value.get("is_draft") is True and value.get("is_published") is False, "InvenioRDM draft state differs")
    parent = value.get("parent", {})
    require(isinstance(parent, dict) and int(parent.get("id", -1)) == CONCEPT_ID, "InvenioRDM draft parent differs")
    return value


def verify_rdm_learner_preview(value: dict[str, Any]) -> None:
    files = value.get("files", {})
    require(isinstance(files, dict) and files.get("enabled") is True, "InvenioRDM files are not enabled")
    require(files.get("count") == 98, "InvenioRDM file count differs")
    require(files.get("default_preview") == LEARNER_FILE, "InvenioRDM default preview differs")


def set_learner_default_preview(client: requests.Session, draft_id: int) -> None:
    draft = get_draft(client, draft_id)
    rows = draft_file_rows(draft)
    by_name = {str(row["name"]): row for row in rows}
    require(LEARNER_FILE in by_name, "learner HTML is absent from draft")
    current = rdm_draft(client, draft_id)
    metadata = current.get("metadata")
    access = current.get("access")
    custom_fields = current.get("custom_fields", {})
    require(isinstance(metadata, dict), "InvenioRDM draft metadata is malformed")
    require(isinstance(access, dict), "InvenioRDM draft access is malformed")
    require(isinstance(custom_fields, dict), "InvenioRDM custom fields are malformed")
    payload = {
        "metadata": metadata,
        "access": access,
        "files": {"enabled": True, "default_preview": LEARNER_FILE},
        "custom_fields": custom_fields,
    }
    response = None
    for attempt in range(5):
        try:
            response = client.put(
                f"{PUBLIC_API}/{draft_id}/draft",
                json=payload,
                headers={"Accept": "application/vnd.inveniordm.v1+json", "Content-Type": "application/json"},
                timeout=(20, 180),
            )
        except requests.RequestException:
            response = None
        if response is not None and response.status_code == 200:
            break
        if response is not None and response.status_code not in (429, 500, 502, 503, 504):
            raise RuntimeError(f"InvenioRDM default-preview update returned HTTP {response.status_code}")
        time.sleep(2 * (attempt + 1))
    require(response is not None and response.status_code == 200, "InvenioRDM default-preview update retry budget exhausted")
    updated = response.json()
    verify_rdm_learner_preview(updated)
    require(updated.get("metadata") == metadata, "default-preview update changed metadata")
    require(updated.get("access") == access, "default-preview update changed access")
    require(updated.get("custom_fields", {}) == custom_fields, "default-preview update changed custom fields")
    refreshed = rdm_draft(client, draft_id)
    verify_rdm_learner_preview(refreshed)
    require(refreshed.get("metadata") == metadata, "default-preview reload changed metadata")
    require(refreshed.get("access") == access, "default-preview reload changed access")
    require(refreshed.get("custom_fields", {}) == custom_fields, "default-preview reload changed custom fields")


def publish_once(client: requests.Session, draft_id: int) -> dict[str, Any]:
    latest = public_json(f"{PUBLIC_API}/{CONCEPT_ID}/versions/latest")
    require(int(latest.get("id", -1)) == PREDECESSOR_ID, "concept latest changed before publish")
    error = None
    try:
        response = client.post(f"{DEPOSIT_API}/{draft_id}/actions/publish", timeout=(20, 180))
        if response.status_code not in (200, 202):
            error = RuntimeError(f"Zenodo publish returned HTTP {response.status_code}")
    except requests.RequestException as exc:
        error = exc
    for attempt in range(30):
        response = public_get(f"{PUBLIC_API}/{draft_id}")
        if response.status_code == 200:
            record = response.json()
            if record.get("metadata", {}).get("version") == VERSION:
                return record
        time.sleep(min(10, attempt + 1))
    raise RuntimeError("published Zenodo successor did not become public") from error


def expected_public_metadata(predecessor_metadata: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "title": TITLE,
        "description": DESCRIPTION,
        "access_right": "open",
        "license": "other-open",
        "language": "ind",
        "version": VERSION,
        "publication_date": payload["publication_date"],
        "creators": predecessor_metadata["creators"],
        "contributors": predecessor_metadata["contributors"],
        "related_identifiers": payload["related_identifiers"],
        "notes": NOTES,
    }
    return expected


def verify_public_successor(
    record: dict[str, Any],
    local_rows: list[dict[str, Any]],
    predecessor_metadata: dict[str, Any],
    expected_metadata: dict[str, Any],
) -> list[dict[str, Any]]:
    record_id = int(record.get("id", -1))
    require(record_id > 0 and record_id != PREDECESSOR_ID, "successor record ID differs")
    require(record.get("doi") == f"10.5281/zenodo.{record_id}", "successor DOI differs")
    require(record.get("conceptdoi") == f"10.5281/zenodo.{CONCEPT_ID}", "successor concept differs")
    metadata = record.get("metadata", {})
    require(isinstance(metadata, dict), "successor metadata is malformed")
    for field, expected in expected_metadata.items():
        if field == "license":
            require(license_id(metadata) == expected, "successor license differs")
        else:
            require(metadata.get(field) == expected, f"successor metadata differs: {field}")
    for field in PRESERVED_PUBLIC_FIELDS:
        if field in predecessor_metadata:
            require(metadata.get(field) == predecessor_metadata[field], f"successor inherited metadata differs: {field}")
    require(first_href(metadata.get("description")) == LEARNER_SITE, "successor description is not student-first")
    require(metadata.get("related_identifiers", [{}])[0].get("identifier") == LEARNER_SITE, "successor related identifiers are not student-first")
    require(MODEL in str(metadata.get("description", "")), "successor model provenance is absent")
    require("belum lengkap" in str(metadata.get("description", "")), "successor incomplete-program boundary is absent")
    public_rdm = public_rdm_json(record_id)
    verify_rdm_learner_preview(public_rdm)
    observed = anonymous_inventory(record, local_rows, "successor")
    require(inventory_sha(observed) == inventory_sha(local_rows), "successor inventory aggregate differs")
    return observed


def verify_lineage(
    record: dict[str, Any],
    predecessor_record: dict[str, Any],
    predecessor_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    record_id = int(record["id"])
    latest = public_json(f"{PUBLIC_API}/{CONCEPT_ID}/versions/latest")
    require(int(latest.get("id", -1)) == record_id, "concept latest does not resolve to v0.62.9")
    require(latest.get("metadata", {}).get("version") == VERSION, "concept latest version differs")
    predecessor_after = public_json(f"{PUBLIC_API}/{PREDECESSOR_ID}")
    predecessor_metadata_before = predecessor_record.get("metadata", {})
    predecessor_metadata_after = predecessor_after.get("metadata", {})
    require(isinstance(predecessor_metadata_before, dict), "predecessor-before metadata is malformed")
    require(isinstance(predecessor_metadata_after, dict), "predecessor-after metadata is malformed")
    require(
        stable_public_metadata(predecessor_metadata_after) == stable_public_metadata(predecessor_metadata_before),
        "predecessor stable public metadata changed",
    )
    relation_before = version_relation(predecessor_metadata_before)
    relation_after = version_relation(predecessor_metadata_after)
    require(
        {key: value for key, value in relation_after.items() if key != "is_last"}
        == {key: value for key, value in relation_before.items() if key != "is_last"},
        "predecessor version relation changed outside the latest flag",
    )
    require(relation_after["is_last"] is False, "predecessor remains incorrectly marked latest")
    predecessor_files_before = [
        (row["name"], row["bytes"], row["md5"])
        for row in public_file_stubs(predecessor_record, 98, "predecessor-before-lineage")
    ]
    predecessor_files_after = [
        (row["name"], row["bytes"], row["md5"])
        for row in public_file_stubs(predecessor_after, 98, "predecessor-after-lineage")
    ]
    require(predecessor_files_after == predecessor_files_before, "predecessor file inventory/order changed")
    observed_after = anonymous_inventory(predecessor_after, predecessor_rows, "predecessor-after")
    require(inventory_sha(observed_after) == inventory_sha(predecessor_rows), "predecessor bytes changed")
    require(predecessor_after.get("metadata", {}).get("access_right") == "open", "predecessor access changed")

    for doi_id, expected_id in ((record_id, record_id), (CONCEPT_ID, record_id), (PREDECESSOR_ID, PREDECESSOR_ID)):
        response = public_get(f"https://doi.org/10.5281/zenodo.{doi_id}")
        require(response.status_code == 200, "DOI resolution failed")
        require(urlparse(response.url).path.rstrip("/") == f"/records/{expected_id}", "DOI target differs")
    student = public_get(LEARNER_SITE)
    require(student.status_code == 200 and "Program Matematika Indonesia" in student.text, "student site readback failed")
    github = public_get(GITHUB_RELEASE)
    require(github.status_code == 200 and "v0.62.9" in github.text, "GitHub release readback failed")
    return {
        "concept_latest_record_id": record_id,
        "concept_latest_version": VERSION,
        "successor_doi_resolution": "pass",
        "concept_doi_latest_resolution": "pass",
        "predecessor_doi_resolution_unchanged": "pass",
        "predecessor_open_unchanged": True,
        "predecessor_stable_metadata_unchanged": True,
        "predecessor_stable_metadata_canonical_sha256": compact_sha(stable_public_metadata(predecessor_metadata_after)),
        "predecessor_relation_is_last_before": relation_before["is_last"],
        "predecessor_relation_is_last_after": relation_after["is_last"],
        "predecessor_relation_expected_latest_transition": "true_to_false_or_already_false",
        "predecessor_file_order_unchanged": True,
        "predecessor_anonymous_readback": "pass_98_of_98",
        "student_site_readback": "pass",
        "github_release_readback": "pass",
    }


def write_receipts(
    record: dict[str, Any],
    observed: list[dict[str, Any]],
    predecessor_metadata: dict[str, Any],
    predecessor_rows: list[dict[str, Any]],
    github: dict[str, Any],
    lineage: dict[str, Any],
    draft_id: int,
    newversion_http_201_observed: bool,
    deleted: int,
    uploaded: int,
    execution_mode: str,
    reservation_route: str,
) -> tuple[int, str]:
    metadata = record["metadata"]
    publisher = Path(__file__).resolve()
    payload = [
        {
            "name": row["name"],
            "bytes": row["bytes"],
            "md5": row["md5"],
            "sha256": row["sha256"],
            "anonymous_url": row["url"],
            "anonymous_byte_identity": True,
            "provenance": "b10_v2.3.1_additive" if row["name"] in ADDITIONS else "retained_exact_from_v0.62.8.1",
        }
        for row in observed
    ]
    receipt = {
        "schema_id": "program-matematika-indonesia/zenodo-publication-receipt/1.0.0",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "state": "published_open_cap_compatible_backend_successor",
        "version": VERSION,
        "student_entry": {
            "primary_url": LEARNER_SITE,
            "description_first_href": LEARNER_SITE,
            "related_identifiers_first": LEARNER_SITE,
            "zenodo_default_preview": LEARNER_FILE,
            "machine_backend_is_secondary": True,
        },
        "zenodo": {
            "record_id": int(record["id"]),
            "version_doi": record["doi"],
            "concept_record_id": CONCEPT_ID,
            "concept_doi": record["conceptdoi"],
            "predecessor_record_id": PREDECESSOR_ID,
            "predecessor_doi": f"10.5281/zenodo.{PREDECESSOR_ID}",
            "access_right": metadata["access_right"],
            "license": license_id(metadata),
            "language": metadata["language"],
            "publication_date": metadata["publication_date"],
            "file_count": len(payload),
            "anonymous_readback": "pass_98_of_98",
            "concept_latest": "pass",
        },
        "github_authority": {
            "release": GITHUB_RELEASE,
            "receipt_sha256": sha256_bytes(GITHUB_RECEIPT.read_bytes()),
            "tag_target_commit": github["release"]["tag_target_commit"],
            "anonymous_readback": github["anonymous_asset_readback"]["result"],
            "inventory_aggregate_sha256": github["inventory"]["aggregate_sha256"],
        },
        "replacement_boundary": {
            "predecessor_files": 98,
            "retained_exact_files": 91,
            "omitted_preserved_in_public_predecessor": sorted(OMITTED),
            "additive_files": sorted(ADDITIONS),
            "successor_files": 98,
            "omission_present_to_absent_transitions_observed_in_this_execution": deleted,
            "addition_absent_to_present_transitions_observed_in_this_execution": uploaded,
            "draft_id": draft_id,
            "newversion_http_201_observed": newversion_http_201_observed,
            "draft_creation_not_inferred_from_http_status": True,
            "execution_mode": execution_mode,
            "reservation_route": reservation_route,
        },
        "payload_inventory": payload,
        "payload_inventory_aggregate_sha256": inventory_sha(payload),
        "payload_total_bytes": sum(int(row["bytes"]) for row in payload),
        "inheritance": {
            "predecessor_inventory_aggregate_sha256": inventory_sha(predecessor_rows),
            "predecessor_unchanged": True,
            "creators_count": len(metadata["creators"]),
            "creators_canonical_sha256": compact_sha(metadata["creators"]),
            "contributors_count": len(metadata["contributors"]),
            "contributors_canonical_sha256": compact_sha(metadata["contributors"]),
            "source_and_human_credits_preserved": True,
            "stable_metadata_preserved": True,
        },
        "lineage_verification": lineage,
        "overall_program_complete": False,
        "model_provenance": MODEL,
        "publisher": {
            "path": publisher.relative_to(PROJECT).as_posix(),
            "bytes": publisher.stat().st_size,
            "sha256": sha256_bytes(publisher.read_bytes()),
            "git_commands_used": 0,
        },
        "privacy": {
            "credentials_recorded": False,
            "credential_locator_recorded": False,
            "absolute_profile_paths_recorded": False,
            "personal_name_recorded": False,
        },
    }
    data = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    for path in (VERSION_RECEIPT, ROOT_RECEIPT):
        temporary = path.with_name(f".{path.name}.tmp-v0629")
        temporary.write_bytes(data)
        temporary.replace(path)
    return len(data), sha256_bytes(data)


def reuse_existing_receipts(
    record: dict[str, Any],
    observed: list[dict[str, Any]],
    github: dict[str, Any],
) -> tuple[int, str] | None:
    existing = []
    for path in (VERSION_RECEIPT, ROOT_RECEIPT):
        if not path.is_file():
            continue
        try:
            candidate = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            raise RuntimeError("existing publication receipt is unreadable") from None
        if candidate.get("version") == VERSION:
            existing.append(path)
    if not existing:
        return None
    data = existing[0].read_bytes()
    for path in existing[1:]:
        require(path.read_bytes() == data, "existing publication receipts differ")
    receipt = json.loads(data.decode("utf-8"))
    require(receipt.get("version") == VERSION, "existing receipt version differs")
    zenodo = receipt.get("zenodo", {})
    require(int(zenodo.get("record_id", -1)) == int(record["id"]), "existing receipt record differs")
    require(int(zenodo.get("file_count", -1)) == 98, "existing receipt file count differs")
    require(receipt.get("payload_inventory_aggregate_sha256") == inventory_sha(observed), "existing receipt inventory differs")
    require(
        int(receipt.get("payload_total_bytes", -1)) == sum(int(row["bytes"]) for row in observed),
        "existing receipt byte total differs",
    )
    require(
        receipt.get("github_authority", {}).get("receipt_sha256") == sha256_bytes(GITHUB_RECEIPT.read_bytes()),
        "existing receipt GitHub authority differs",
    )
    require(
        receipt.get("github_authority", {}).get("tag_target_commit")
        == github.get("release", {}).get("tag_target_commit"),
        "existing receipt GitHub commit differs",
    )
    require(receipt.get("inheritance", {}).get("predecessor_unchanged") is True, "existing receipt lineage differs")
    for path in (VERSION_RECEIPT, ROOT_RECEIPT):
        if not path.is_file() or path.read_bytes() != data:
            temporary = path.with_name(f".{path.name}.tmp-v0629-restore")
            temporary.write_bytes(data)
            temporary.replace(path)
    return len(data), sha256_bytes(data)


def main() -> None:
    local_rows, _, _, github = local_inventory()
    predecessor_record, predecessor_metadata, predecessor_rows = predecessor_authority(local_rows)
    token = load_token()
    client = authenticated_session(token)
    predecessor_deposition = authenticated_predecessor(client)
    verify_predecessor_metadata_mapping(predecessor_deposition, predecessor_metadata)

    latest = public_json(f"{PUBLIC_API}/{CONCEPT_ID}/versions/latest")
    already_public = latest.get("metadata", {}).get("version") == VERSION
    draft_id = int(latest.get("id", -1)) if already_public else -1
    newversion_http_201_observed = False
    reservation_route = "not_applicable_existing_public"
    deleted = 0
    uploaded = 0
    if already_public:
        record = latest
        payload = metadata_payload({"metadata": predecessor_metadata}, predecessor_metadata)
        publication_date = record.get("metadata", {}).get("publication_date")
        require(isinstance(publication_date, str) and bool(publication_date), "published successor date is absent")
        payload["publication_date"] = publication_date
        execution_mode = "verification_only_existing_public"
    else:
        require(int(latest.get("id", -1)) == PREDECESSOR_ID, "concept latest is neither predecessor nor v0.62.9")
        draft_id, newversion_http_201_observed, reservation_route = reserve_or_resume(client)
        draft = get_draft(client, draft_id)
        verify_draft_metadata_boundary(draft, predecessor_deposition)
        validate_draft_boundary(draft, predecessor_rows, local_rows)
        deleted = delete_omissions(client, draft_id)
        draft = get_draft(client, draft_id)
        validate_draft_boundary(draft, predecessor_rows, local_rows)
        uploaded = upload_additions(client, draft_id, local_rows)
        draft = get_draft(client, draft_id)
        verify_exact_draft(draft, local_rows)
        payload = metadata_payload(draft, predecessor_metadata)
        put_metadata(client, draft_id, payload)
        set_learner_default_preview(client, draft_id)
        final_draft = get_draft(client, draft_id)
        verify_draft_metadata_boundary(final_draft, predecessor_deposition)
        verify_exact_draft(final_draft, local_rows)
        verify_final_draft_metadata(final_draft, payload)
        verify_rdm_learner_preview(rdm_draft(client, draft_id))
        record = publish_once(client, draft_id)
        execution_mode = "published_new_or_resumed_draft"

    expected_metadata = expected_public_metadata(predecessor_metadata, payload)
    observed = verify_public_successor(record, local_rows, predecessor_metadata, expected_metadata)
    lineage = verify_lineage(record, predecessor_record, predecessor_rows)
    existing_receipt = reuse_existing_receipts(record, observed, github) if already_public else None
    if existing_receipt is not None:
        receipt_bytes, receipt_sha = existing_receipt
    else:
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
        )
    print(
        json.dumps(
            {
                "status": "pass",
                "record_id": int(record["id"]),
                "doi": record["doi"],
                "concept_doi": record["conceptdoi"],
                "files": len(observed),
                "bytes": sum(int(row["bytes"]) for row in observed),
                "aggregate_sha256": inventory_sha(observed),
                "receipt": VERSION_RECEIPT.relative_to(PROJECT).as_posix(),
                "receipt_bytes": receipt_bytes,
                "receipt_sha256": receipt_sha,
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: bounded Zenodo publication aborted", file=sys.stderr)
        raise SystemExit(1)
