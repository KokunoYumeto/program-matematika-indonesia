#!/usr/bin/env python3
"""Correct two historical Zenodo file inventories without reducing public access.

The v0.41.0 and v0.42.0 records contain a small set of generated artifacts that
were sanitized locally after publication.  Zenodo's documented grace-period
workflow permits a same-DOI edit draft for minor file corrections.  This script
is deliberately narrow and resumable:

* it accepts only the two frozen record/version/concept tuples below;
* it derives the replacement filenames from the committed privacy receipt;
* it proves every unaffected public file already equals the local release file;
* it never edits metadata, access, visibility, concept lineage, or DOI values;
* it replaces only files whose public bytes differ from the sanitized local file;
* it validates the complete draft inventory before publication; and
* it anonymously downloads every public file after publication and writes a
  credential-free receipt.

Dry-run is the default.  Network mutation requires ``--execute`` and an explicit
``--token-file``.  A failed edit leaves only a non-public edit draft; rerunning
continues from that draft.  The already-published record remains public during
the entire operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

import requests


ROOT = Path(__file__).resolve().parents[1]
PRIVACY_RECEIPT = ROOT / "PRIVACY_CORRECTION_RECEIPT_20260829.json"
DEFAULT_RECEIPT = ROOT / "ZENODO_HISTORICAL_FILE_CORRECTION_RECEIPT_20260829.json"
ZENODO_API = "https://zenodo.org/api/records"
ZENODO_HOST = "zenodo.org"
NATIVE_ACCEPT = "application/vnd.inveniordm.v1+json"
CONCEPT_ID = 22059707
PRIVACY_RECEIPT_SCHEMA = (
    "program-matematika-indonesia/historical-public-privacy-correction/v1"
)
PRIVACY_RECEIPT_BYTES = 26034
PRIVACY_RECEIPT_SHA256 = (
    "7fbf1e0add54ba2850357c987b2be69941cf3e6a5a7e335409047bed7ea00415"
)
OFFICIAL_GUIDANCE = (
    "https://help.zenodo.org/docs/deposit/manage-files/"
    "#modify-files-after-publication"
)
USER_AGENT = "Program-Matematika-Indonesia-historical-file-correction/1.0"
COMMENT = (
    "Minor privacy correction: replace generated files containing an unintended "
    "local profile attribution or machine-local path. Mathematical and curricular "
    "content, metadata, public access, concept lineage, and DOI remain unchanged."
)


@dataclass(frozen=True)
class RecordSpec:
    record_id: int
    version: str
    release_dir: str
    expected_file_count: int
    expected_changed_count: int
    publication_receipt_name: str
    publication_receipt_bytes: int
    publication_receipt_sha256: str


SPECS = (
    RecordSpec(
        22060393,
        "0.41.0",
        "v0.41.0",
        14,
        6,
        "ZENODO_PUBLICATION_RECEIPT_v0.41.0.json",
        5118,
        "22ef7d4230a73a002a6300005f023e5315b395c920c5c772205e174e7037f47b",
    ),
    RecordSpec(
        22061915,
        "0.42.0",
        "v0.42.0",
        17,
        10,
        "ZENODO_PUBLICATION_RECEIPT_v0.42.0.json",
        5920,
        "f688ae3931ca1fc16602af324d1dd99b8a8aebfa28ead8a77b1209cec8bbcc94",
    ),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def hash_bytes(data: bytes, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    digest.update(data)
    return digest.hexdigest()


def hash_file(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_fact(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"required local release file is absent: {path.name}")
    return {
        "name": path.name,
        "bytes": path.stat().st_size,
        "md5": hash_file(path, "md5"),
        "sha256": hash_file(path, "sha256"),
        "path": path,
    }


def load_json(path: Path, label: str) -> dict[str, Any]:
    require(path.is_file(), f"{label} is absent")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{label} is not a JSON object")
    return value


def load_bound_json(
    path: Path,
    label: str,
    *,
    expected_bytes: int,
    expected_sha256: str,
) -> dict[str, Any]:
    require(path.is_file(), f"{label} is absent")
    require(path.stat().st_size == expected_bytes, f"{label} byte count differs")
    require(hash_file(path, "sha256") == expected_sha256, f"{label} SHA-256 differs")
    return load_json(path, label)


def require_zenodo_api_url(url: str, label: str) -> str:
    require(isinstance(url, str) and url, f"{label} is absent")
    parsed = urlparse(url)
    require(parsed.scheme == "https", f"{label} is not HTTPS")
    require(parsed.hostname == ZENODO_HOST, f"{label} leaves zenodo.org")
    require(parsed.port in {None, 443}, f"{label} uses an unexpected port")
    require(parsed.username is None and parsed.password is None, f"{label} contains user info")
    require(parsed.path.startswith("/api/"), f"{label} is outside the Zenodo API")
    require(not parsed.fragment, f"{label} contains a fragment")
    return url


def file_entries(record: dict[str, Any], label: str) -> dict[str, dict[str, Any]]:
    files = record.get("files")
    require(isinstance(files, dict), f"{label} has malformed files")
    entries = files.get("entries")
    require(isinstance(entries, dict), f"{label} has malformed file entries")
    result: dict[str, dict[str, Any]] = {}
    for name, row in entries.items():
        require(isinstance(name, str) and name, f"{label} has an invalid file key")
        require(isinstance(row, dict), f"{label} has a malformed file row: {name}")
        require(row.get("key") == name, f"{label} file key differs: {name}")
        result[name] = row
    return result


def without_links(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: without_links(item)
            for key, item in value.items()
            if key != "links"
        }
    if isinstance(value, list):
        return [without_links(item) for item in value]
    return value


def parent_identity(record: dict[str, Any]) -> dict[str, Any]:
    parent = record.get("parent")
    require(isinstance(parent, dict), "record parent is malformed")
    access = parent.get("access")
    require(isinstance(access, dict), "record parent access is malformed")
    # Zenodo adds permission-only ``grants`` and ``links`` keys to an
    # authenticated response.  They are not part of the concept identity and
    # are deliberately excluded so anonymous and authenticated projections
    # compare the same bytes.  The stable owner/settings projection remains
    # in-memory only and is represented in receipts by its hash.
    stable_access = {
        key: without_links(access.get(key))
        for key in ("owned_by", "settings")
        if key in access
    }
    return {
        "id": parent.get("id"),
        "pids": without_links(parent.get("pids")),
        "communities": without_links(parent.get("communities")),
        "access": stable_access,
    }


def immutable_record_projection(
    record: dict[str, Any], changed: set[str]
) -> dict[str, Any]:
    entries = file_entries(record, "native record")
    projected_entries: dict[str, Any] = {}
    for name in sorted(entries):
        row = entries[name]
        if name in changed:
            projected_entries[name] = {
                key: without_links(row.get(key))
                for key in (
                    "key",
                    "ext",
                    "mimetype",
                    "storage_class",
                    "metadata",
                    "access",
                )
            }
        else:
            projected_entries[name] = without_links(row)

    files = record["files"]
    media_files = record.get("media_files")
    require(isinstance(media_files, dict), "native record has malformed media files")
    return {
        "id": str(record.get("id")),
        "pids": without_links(record.get("pids")),
        "parent": parent_identity(record),
        "metadata": without_links(record.get("metadata")),
        "custom_fields": without_links(record.get("custom_fields")),
        "access": without_links(record.get("access")),
        "files": {
            "enabled": files.get("enabled"),
            "order": without_links(files.get("order")),
            "count": files.get("count"),
            "entries": projected_entries,
        },
        "media_files": without_links(media_files),
    }


def load_token(path: Path) -> str:
    require(path.is_file(), "Zenodo credential file is unavailable")
    raw = path.read_text(encoding="utf-8").strip()
    candidates = re.findall(r"(?<![A-Za-z0-9])[A-Za-z0-9._-]{40,}(?![A-Za-z0-9])", raw)
    require(len(candidates) == 1, "Zenodo credential file must contain one token")
    return candidates[0]


def request(
    session: requests.Session,
    method: str,
    url: str,
    *,
    expected: set[int],
    timeout: int = 180,
    attempts: int = 4,
    **kwargs: Any,
) -> requests.Response:
    response: requests.Response | None = None
    for attempt in range(1, attempts + 1):
        response = session.request(method, url, timeout=timeout, **kwargs)
        if response.status_code in expected:
            return response
        if response.status_code not in {429, 500, 502, 503, 504} or attempt == attempts:
            break
        time.sleep(min(3 * attempt, 12))
    assert response is not None
    diagnostic = response.text[:1000].replace("\n", " ")
    raise RuntimeError(
        f"Zenodo {method} failed with HTTP {response.status_code}: {diagnostic}"
    )


def anonymous_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": NATIVE_ACCEPT})
    return session


def authenticated_session(token: str) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": NATIVE_ACCEPT,
            "Authorization": f"Bearer {token}",
        }
    )
    return session


def public_record(session: requests.Session, record_id: int) -> dict[str, Any]:
    url = require_zenodo_api_url(
        f"{ZENODO_API}/{record_id}", f"record {record_id} public URL"
    )
    response = request(
        session,
        "GET",
        url,
        expected={200},
        attempts=5,
    )
    value = response.json()
    require(isinstance(value, dict), f"record {record_id}: malformed public JSON")
    return value


def public_rows(record: dict[str, Any], expected_count: int) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    entries = file_entries(record, "public record")
    for name, item in entries.items():
        size = item.get("size")
        checksum = str(item.get("checksum", ""))
        url = item.get("links", {}).get("content")
        require(isinstance(name, str) and name, "public file has no key")
        require(isinstance(size, int) and size >= 0, f"public file has invalid size: {name}")
        require(re.fullmatch(r"md5:[0-9a-f]{32}", checksum) is not None, f"public file has invalid checksum: {name}")
        require_zenodo_api_url(url, f"public file content URL: {name}")
        require(name not in rows, f"public record repeats filename: {name}")
        rows[name] = {
            "name": name,
            "bytes": size,
            "md5": checksum.removeprefix("md5:"),
            "url": url,
        }
    require(record["files"].get("count") == expected_count, "native public file count differs")
    require(len(rows) == expected_count, f"expected {expected_count} public files, found {len(rows)}")
    return rows


def changed_release_postimages(
    privacy: dict[str, Any], release_dir: str
) -> dict[str, dict[str, Any]]:
    prefix = f"releases/{release_dir}/"
    result: dict[str, dict[str, Any]] = {}
    changed = privacy.get("changed_files")
    require(isinstance(changed, list), "privacy receipt has no changed-file inventory")
    for row in changed:
        require(isinstance(row, dict), "privacy receipt contains malformed changed-file row")
        after = row.get("after")
        require(isinstance(after, dict), "privacy receipt changed-file row has no postimage")
        path = after.get("path")
        if isinstance(path, str) and path.startswith(prefix):
            name = Path(path).name
            require(name not in result, f"privacy receipt repeats postimage: {name}")
            size = after.get("bytes")
            sha256 = after.get("sha256")
            require(isinstance(size, int) and size >= 0, f"postimage size is invalid: {name}")
            require(
                isinstance(sha256, str)
                and re.fullmatch(r"[0-9a-f]{64}", sha256) is not None,
                f"postimage SHA-256 is invalid: {name}",
            )
            result[name] = {"bytes": size, "sha256": sha256}
    require(result, f"privacy receipt has no release changes for {release_dir}")
    return result


def publication_inventory(spec: RecordSpec) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    path = ROOT / "releases" / spec.release_dir / spec.publication_receipt_name
    receipt = load_bound_json(
        path,
        f"{spec.release_dir} publication receipt",
        expected_bytes=spec.publication_receipt_bytes,
        expected_sha256=spec.publication_receipt_sha256,
    )
    require(receipt.get("version") == spec.version, "publication receipt version differs")
    zenodo = receipt.get("zenodo")
    require(isinstance(zenodo, dict), "publication receipt Zenodo facts are malformed")
    require(zenodo.get("record_id") == spec.record_id, "publication receipt record differs")
    require(zenodo.get("file_count") == spec.expected_file_count, "publication receipt file count differs")
    rows = receipt.get("files")
    require(isinstance(rows, list), "publication receipt inventory is malformed")
    inventory: dict[str, dict[str, Any]] = {}
    for row in rows:
        require(isinstance(row, dict), "publication receipt has a malformed file row")
        name = row.get("name")
        size = row.get("bytes")
        sha256 = row.get("sha256")
        require(isinstance(name, str) and name, "publication receipt file has no name")
        require(name not in inventory, f"publication receipt repeats filename: {name}")
        require(isinstance(size, int) and size >= 0, f"publication receipt size is invalid: {name}")
        require(
            isinstance(sha256, str)
            and re.fullmatch(r"[0-9a-f]{64}", sha256) is not None,
            f"publication receipt SHA-256 is invalid: {name}",
        )
        inventory[name] = {"bytes": size, "sha256": sha256}
    require(len(inventory) == spec.expected_file_count, "publication receipt inventory length differs")
    return inventory, receipt


def require_public_identity(record: dict[str, Any], spec: RecordSpec) -> None:
    require(int(record.get("id", -1)) == spec.record_id, "public record ID differs")
    pids = record.get("pids")
    require(isinstance(pids, dict), "public PIDs are malformed")
    doi = pids.get("doi")
    require(isinstance(doi, dict), "public DOI PID is malformed")
    require(doi.get("identifier") == f"10.5281/zenodo.{spec.record_id}", "public DOI differs")
    parent = record.get("parent")
    require(isinstance(parent, dict), "public parent is malformed")
    parent_pids = parent.get("pids")
    require(isinstance(parent_pids, dict), "public parent PIDs are malformed")
    parent_doi = parent_pids.get("doi")
    require(isinstance(parent_doi, dict), "public concept DOI PID is malformed")
    require(parent_doi.get("identifier") == f"10.5281/zenodo.{CONCEPT_ID}", "public concept DOI differs")
    metadata = record.get("metadata")
    require(isinstance(metadata, dict), "public metadata is malformed")
    require(metadata.get("version") == spec.version, "public version differs")
    access = record.get("access")
    require(isinstance(access, dict), "public access is malformed")
    require(access.get("record") == "public", "public record visibility is not public")
    require(access.get("files") == "public", "public file visibility is not public")
    require(access.get("status") == "open", "public record access is not open")
    embargo = access.get("embargo")
    require(isinstance(embargo, dict) and embargo.get("active") is False, "public embargo is active")
    require(record.get("is_published") is True, "public record is not marked published")
    require(record.get("is_draft") is False, "public record is marked draft")


def preflight_record(
    anon: requests.Session,
    privacy: dict[str, Any],
    spec: RecordSpec,
) -> dict[str, Any]:
    record = public_record(anon, spec.record_id)
    require_public_identity(record, spec)
    remote = public_rows(record, spec.expected_file_count)
    original_inventory, _ = publication_inventory(spec)
    require(set(original_inventory) == set(remote), f"record {spec.record_id}: publication-receipt filenames differ")
    release = ROOT / "releases" / spec.release_dir
    require(release.is_dir(), f"local release directory is absent: {spec.release_dir}")
    local = {name: local_fact(release / name) for name in sorted(remote)}
    changed_candidates = changed_release_postimages(privacy, spec.release_dir)
    changed = set(remote) & set(changed_candidates)
    require(
        len(changed) == spec.expected_changed_count,
        f"record {spec.record_id}: expected {spec.expected_changed_count} public replacements, found {len(changed)}",
    )

    for name in sorted(changed):
        postimage = changed_candidates[name]
        require(local[name]["bytes"] == postimage["bytes"], f"record {spec.record_id}: postimage size differs: {name}")
        require(local[name]["sha256"] == postimage["sha256"], f"record {spec.record_id}: postimage SHA-256 differs: {name}")

    for name in sorted(set(remote) - changed):
        require(local[name]["bytes"] == original_inventory[name]["bytes"], f"record {spec.record_id}: unaffected local size differs from publication receipt: {name}")
        require(local[name]["sha256"] == original_inventory[name]["sha256"], f"record {spec.record_id}: unaffected local SHA-256 differs from publication receipt: {name}")
        require(remote[name]["bytes"] == local[name]["bytes"], f"record {spec.record_id}: unaffected size differs: {name}")
        require(remote[name]["md5"] == local[name]["md5"], f"record {spec.record_id}: unaffected MD5 differs: {name}")

    pending = {
        name
        for name in changed
        if remote[name]["bytes"] != local[name]["bytes"]
        or remote[name]["md5"] != local[name]["md5"]
    }
    already = changed - pending
    for name in sorted(pending):
        require(remote[name]["bytes"] == original_inventory[name]["bytes"], f"record {spec.record_id}: pending public size differs from publication receipt: {name}")
        response = request(
            anon,
            "GET",
            remote[name]["url"],
            expected={200},
            timeout=300,
            attempts=5,
            headers={"Accept": "*/*", "User-Agent": USER_AGENT},
        )
        data = response.content
        require(len(data) == original_inventory[name]["bytes"], f"record {spec.record_id}: pending public byte count differs: {name}")
        require(hash_bytes(data, "md5") == remote[name]["md5"], f"record {spec.record_id}: pending public MD5 differs: {name}")
        require(hash_bytes(data, "sha256") == original_inventory[name]["sha256"], f"record {spec.record_id}: pending public SHA-256 differs from publication receipt: {name}")
    for name in sorted(already):
        require(remote[name]["bytes"] == local[name]["bytes"], f"record {spec.record_id}: corrected public size differs: {name}")
        require(remote[name]["md5"] == local[name]["md5"], f"record {spec.record_id}: corrected public MD5 differs: {name}")

    projection = immutable_record_projection(record, changed)
    return {
        "record": record,
        "remote": remote,
        "local": local,
        "original_inventory": original_inventory,
        "changed": changed,
        "pending": pending,
        "already": already,
        "immutable_projection": projection,
        "immutable_projection_sha256": hash_bytes(canonical_bytes(projection), "sha256"),
    }


def get_draft(auth: requests.Session, record_id: int) -> dict[str, Any] | None:
    url = require_zenodo_api_url(
        f"{ZENODO_API}/{record_id}/draft", f"record {record_id} draft URL"
    )
    response = auth.get(url, timeout=120, allow_redirects=False)
    if response.status_code == 404:
        return None
    if response.status_code != 200:
        raise RuntimeError(f"record {record_id}: draft GET HTTP {response.status_code}")
    value = response.json()
    require(isinstance(value, dict), f"record {record_id}: malformed draft JSON")
    return value


def ensure_draft(
    auth: requests.Session, spec: RecordSpec
) -> tuple[dict[str, Any], bool]:
    draft = get_draft(auth, spec.record_id)
    if draft is not None:
        return draft, False
    url = require_zenodo_api_url(
        f"{ZENODO_API}/{spec.record_id}/draft", f"record {spec.record_id} create-draft URL"
    )
    try:
        response = request(
            auth,
            "POST",
            url,
            expected={200, 201},
            attempts=1,
            allow_redirects=False,
            json={},
        )
    except RuntimeError:
        recovered = get_draft(auth, spec.record_id)
        if recovered is None:
            raise
        return recovered, True
    value = response.json()
    require(isinstance(value, dict), f"record {spec.record_id}: create-draft response malformed")
    return value, True


def draft_rows(auth: requests.Session, draft: dict[str, Any]) -> dict[str, dict[str, Any]]:
    files_url = draft.get("links", {}).get("files")
    require_zenodo_api_url(files_url, "draft files URL")
    response = request(auth, "GET", files_url, expected={200}, allow_redirects=False)
    body = response.json()
    require(isinstance(body, dict), "draft file listing is malformed")
    rows: dict[str, dict[str, Any]] = {}
    raw_entries = body.get("entries", [])
    if isinstance(raw_entries, dict):
        iterable = raw_entries.values()
    else:
        require(isinstance(raw_entries, list), "draft file entries are malformed")
        iterable = raw_entries
    for item in iterable:
        require(isinstance(item, dict), "draft contains malformed file row")
        name = item.get("key")
        require(isinstance(name, str) and name, "draft file has no key")
        checksum = str(item.get("checksum", ""))
        size = item.get("size")
        status = item.get("status")
        require(name not in rows, f"draft repeats filename: {name}")
        rows[name] = {
            "name": name,
            "bytes": int(size) if isinstance(size, (int, float)) else None,
            "md5": checksum.removeprefix("md5:") if checksum.startswith("md5:") else None,
            "status": status,
            "links": item.get("links", {}),
        }
    return rows


def require_draft_identity(
    draft: dict[str, Any],
    public: dict[str, Any],
    spec: RecordSpec,
    changed: set[str],
) -> None:
    require(int(draft.get("id", -1)) == spec.record_id, "draft record ID differs")
    require(draft.get("is_draft") is True, "edit draft is not marked draft")
    require(draft.get("status") == public.get("status"), "edit draft status differs")
    require(
        immutable_record_projection(draft, changed)
        == immutable_record_projection(public, changed),
        "draft immutable identity differs from public record",
    )
    access = draft.get("access", {})
    require(access.get("record") == "public", "draft record visibility is not public")
    require(access.get("files") == "public", "draft file visibility is not public")


def unlock_files(auth: requests.Session, spec: RecordSpec) -> None:
    # The Invenio file-modification schema accepts ``comment`` (and optional
    # ``policy_id``); keep the payload to that documented surface.
    payload = {"comment": COMMENT}
    url = require_zenodo_api_url(
        f"{ZENODO_API}/{spec.record_id}/file-modification",
        f"record {spec.record_id} file-modification URL",
    )
    response = auth.post(
        url,
        json=payload,
        timeout=180,
        allow_redirects=False,
    )
    if response.status_code in {200, 201}:
        return
    diagnostic = response.text[:1000].replace("\n", " ")
    raise RuntimeError(
        f"record {spec.record_id}: file-unlock HTTP {response.status_code}: {diagnostic}"
    )


def replace_one(
    auth: requests.Session,
    draft: dict[str, Any],
    name: str,
    fact: dict[str, Any],
) -> None:
    files_url = require_zenodo_api_url(
        str(draft["links"]["files"]), "draft files URL"
    )
    encoded = quote(name, safe="")
    item_url = require_zenodo_api_url(
        f"{files_url}/{encoded}", f"draft item URL: {name}"
    )

    data = fact["path"].read_bytes()
    require(len(data) == fact["bytes"], f"local bytes changed before upload: {name}")
    require(hash_bytes(data, "md5") == fact["md5"], f"local MD5 changed before upload: {name}")
    require(hash_bytes(data, "sha256") == fact["sha256"], f"local SHA-256 changed before upload: {name}")

    current = draft_rows(auth, draft).get(name)
    if (
        current is not None
        and current.get("status") == "completed"
        and current.get("bytes") == fact["bytes"]
        and current.get("md5") == fact["md5"]
    ):
        return

    if current is not None:
        response = auth.delete(item_url, timeout=180, allow_redirects=False)
        require(response.status_code in {200, 204, 404}, f"delete draft file failed: {name}")

    try:
        response = request(
            auth,
            "POST",
            files_url,
            expected={201},
            attempts=1,
            allow_redirects=False,
            json=[{"key": name}],
        )
        init = response.json()
        raw_entries = init.get("entries", []) if isinstance(init, dict) else []
        if isinstance(raw_entries, dict):
            entries = list(raw_entries.values())
        else:
            entries = raw_entries
        require(isinstance(entries, list) and len(entries) == 1, f"file initialization response malformed: {name}")
        links = entries[0].get("links", {})
    except RuntimeError:
        recovered = draft_rows(auth, draft).get(name)
        if recovered is None:
            raise
        links = recovered.get("links", {})
    content_url = links.get("content")
    commit_url = links.get("commit")
    require_zenodo_api_url(content_url, f"file content URL: {name}")
    require_zenodo_api_url(commit_url, f"file commit URL: {name}")

    upload = request(
        auth,
        "PUT",
        content_url,
        expected={200},
        timeout=600,
        attempts=4,
        allow_redirects=False,
        data=data,
        headers={"Content-Type": "application/octet-stream"},
    )
    require(upload.status_code == 200, f"file upload failed: {name}")
    try:
        committed = request(
            auth,
            "POST",
            commit_url,
            expected={200},
            timeout=300,
            attempts=1,
            allow_redirects=False,
        ).json()
    except RuntimeError:
        recovered = draft_rows(auth, draft).get(name)
        if (
            recovered is None
            or recovered.get("status") != "completed"
            or recovered.get("bytes") != fact["bytes"]
            or recovered.get("md5") != fact["md5"]
        ):
            raise
        committed = {
            "status": recovered["status"],
            "size": recovered["bytes"],
            "checksum": f"md5:{recovered['md5']}",
        }
    require(committed.get("status") == "completed", f"file commit incomplete: {name}")
    require(int(committed.get("size", -1)) == fact["bytes"], f"committed size differs: {name}")
    require(str(committed.get("checksum", "")) == f"md5:{fact['md5']}", f"committed MD5 differs: {name}")


def require_complete_draft(
    auth: requests.Session,
    draft: dict[str, Any],
    public_remote: dict[str, dict[str, Any]],
    local: dict[str, dict[str, Any]],
    changed: set[str],
) -> None:
    rows = draft_rows(auth, draft)
    require(set(rows) == set(public_remote), "draft filename inventory differs from published record")
    for name in sorted(rows):
        expected = local[name] if name in changed else public_remote[name]
        require(rows[name].get("status") == "completed", f"draft file is not complete: {name}")
        require(rows[name].get("bytes") == expected["bytes"], f"draft file size differs: {name}")
        require(rows[name].get("md5") == expected["md5"], f"draft file MD5 differs: {name}")


def publish_edit(auth: requests.Session, spec: RecordSpec, draft: dict[str, Any]) -> None:
    publish_url = draft.get("links", {}).get("publish")
    require_zenodo_api_url(publish_url, "draft publish URL")
    response = auth.post(publish_url, timeout=300, allow_redirects=False)
    if response.status_code in {200, 201, 202}:
        return
    if response.status_code not in {409, 429, 500, 502, 503, 504}:
        diagnostic = response.text[:1000].replace("\n", " ")
        raise RuntimeError(
            f"record {spec.record_id}: publish HTTP {response.status_code}: {diagnostic}"
        )
    # Publication responses can be ambiguous.  The caller verifies the public
    # record byte-for-byte and polls the draft endpoint before deciding success.


def wait_for_draft_disappearance(
    auth: requests.Session, spec: RecordSpec, *, attempts: int = 12
) -> None:
    for attempt in range(1, attempts + 1):
        if get_draft(auth, spec.record_id) is None:
            return
        if attempt != attempts:
            time.sleep(min(3 * attempt, 15))
    raise RuntimeError(f"record {spec.record_id}: edit draft remains after publication")


def anonymous_verify(
    anon: requests.Session,
    spec: RecordSpec,
    local: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    record: dict[str, Any] | None = None
    remote: dict[str, dict[str, Any]] | None = None
    for attempt in range(1, 11):
        record = public_record(anon, spec.record_id)
        require_public_identity(record, spec)
        remote = public_rows(record, spec.expected_file_count)
        if all(
            name in remote
            and remote[name]["bytes"] == fact["bytes"]
            and remote[name]["md5"] == fact["md5"]
            for name, fact in local.items()
        ):
            break
        if attempt == 10:
            raise RuntimeError(f"record {spec.record_id}: corrected inventory did not become public")
        time.sleep(min(3 * attempt, 15))

    assert record is not None and remote is not None
    rows: list[dict[str, Any]] = []
    for name in sorted(local):
        expected = local[name]
        response = request(
            anon,
            "GET",
            remote[name]["url"],
            expected={200},
            timeout=300,
            attempts=5,
            headers={"Accept": "*/*", "User-Agent": USER_AGENT},
        )
        data = response.content
        require(len(data) == expected["bytes"], f"anonymous size differs: {name}")
        require(hash_bytes(data, "md5") == expected["md5"], f"anonymous MD5 differs: {name}")
        require(hash_bytes(data, "sha256") == expected["sha256"], f"anonymous SHA-256 differs: {name}")
        rows.append(
            {
                "name": name,
                "bytes": len(data),
                "md5": expected["md5"],
                "sha256": expected["sha256"],
                "anonymous_byte_identity": True,
            }
        )
    return record, rows


def compact_local_rows(
    local: dict[str, dict[str, Any]], changed: set[str]
) -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "bytes": local[name]["bytes"],
            "md5": local[name]["md5"],
            "sha256": local[name]["sha256"],
            "corrected": name in changed,
        }
        for name in sorted(local)
    ]


def write_receipt(path: Path, rows: list[dict[str, Any]]) -> tuple[int, str]:
    receipt = {
        "schema_id": "program-matematika-indonesia/zenodo-historical-file-correction-receipt/v1",
        "state": "published_public_same_doi_correction",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "official_guidance": OFFICIAL_GUIDANCE,
        "concept_id": CONCEPT_ID,
        "access_reduction_performed": False,
        "record_or_file_restriction_performed": False,
        "doi_changed": False,
        "metadata_changed": False,
        "credential_values_recorded": False,
        "privacy_receipt": {
            "path": PRIVACY_RECEIPT.name,
            "bytes": PRIVACY_RECEIPT_BYTES,
            "sha256": PRIVACY_RECEIPT_SHA256,
        },
        "records": rows,
    }
    data = canonical_bytes(receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    json.loads(temporary.read_text(encoding="utf-8"))
    os.replace(temporary, path)
    return len(data), hash_bytes(data, "sha256")


def run(args: argparse.Namespace) -> dict[str, Any]:
    privacy = load_bound_json(
        PRIVACY_RECEIPT,
        "privacy correction receipt",
        expected_bytes=PRIVACY_RECEIPT_BYTES,
        expected_sha256=PRIVACY_RECEIPT_SHA256,
    )
    require(privacy.get("schema_id") == PRIVACY_RECEIPT_SCHEMA, "privacy receipt schema differs")
    require(privacy.get("state") == "local_public_replacement_bytes_sanitized", "privacy receipt state differs")
    anon = anonymous_session()
    preflights: list[tuple[RecordSpec, dict[str, Any]]] = []
    try:
        for spec in SPECS:
            preflights.append((spec, preflight_record(anon, privacy, spec)))

        dry_summary = {
            "result": "preflight_pass",
            "execute": bool(args.execute),
            "records": [
                {
                    "record_id": spec.record_id,
                    "version": spec.version,
                    "public_files": spec.expected_file_count,
                    "corrected_files": len(state["changed"]),
                    "pending_replacements": len(state["pending"]),
                    "already_correct": len(state["already"]),
                    "access": "open",
                    "publication_receipt": {
                        "name": spec.publication_receipt_name,
                        "bytes": spec.publication_receipt_bytes,
                        "sha256": spec.publication_receipt_sha256,
                    },
                    "immutable_public_projection_sha256": state[
                        "immutable_projection_sha256"
                    ],
                }
                for spec, state in preflights
            ],
        }
        if not args.execute:
            return dry_summary

        require(args.token_file is not None, "--token-file is required with --execute")
        token = load_token(args.token_file.resolve())
        auth = authenticated_session(token)
        del token
        receipt_rows: list[dict[str, Any]] = []
        try:
            for spec, state in preflights:
                mutated = False
                if state["pending"]:
                    draft, created = ensure_draft(auth, spec)
                    require_draft_identity(
                        draft, state["record"], spec, state["changed"]
                    )
                    if created:
                        unlock_files(auth, spec)
                    draft = get_draft(auth, spec.record_id)
                    require(draft is not None, f"record {spec.record_id}: edit draft disappeared")
                    require_draft_identity(
                        draft, state["record"], spec, state["changed"]
                    )
                    initial_draft_rows = draft_rows(auth, draft)
                    require(set(initial_draft_rows) == set(state["remote"]), f"record {spec.record_id}: initial draft inventory differs")
                    for name in sorted(state["pending"]):
                        replace_one(auth, draft, name, state["local"][name])
                    require_complete_draft(
                        auth,
                        draft,
                        state["remote"],
                        state["local"],
                        state["changed"],
                    )
                    fresh_draft = get_draft(auth, spec.record_id)
                    require(fresh_draft is not None, f"record {spec.record_id}: draft unavailable before publish")
                    require_draft_identity(
                        fresh_draft, state["record"], spec, state["changed"]
                    )
                    publish_edit(auth, spec, fresh_draft)
                    mutated = True

                published, anonymous_rows = anonymous_verify(
                    anon, spec, state["local"]
                )
                require_public_identity(published, spec)
                wait_for_draft_disappearance(auth, spec)
                final_projection = immutable_record_projection(
                    published, state["changed"]
                )
                require(
                    final_projection == state["immutable_projection"],
                    f"record {spec.record_id}: immutable public identity changed",
                )
                receipt_rows.append(
                    {
                        "record_id": spec.record_id,
                        "version": spec.version,
                        "doi": f"10.5281/zenodo.{spec.record_id}",
                        "concept_id": CONCEPT_ID,
                        "access_right": "open",
                        "public_file_count": spec.expected_file_count,
                        "corrected_file_count": len(state["changed"]),
                        "mutation_performed_this_run": mutated,
                        "privacy_receipt_sha256": PRIVACY_RECEIPT_SHA256,
                        "publication_receipt": {
                            "name": spec.publication_receipt_name,
                            "bytes": spec.publication_receipt_bytes,
                            "sha256": spec.publication_receipt_sha256,
                        },
                        "immutable_public_projection_sha256": state[
                            "immutable_projection_sha256"
                        ],
                        "final_immutable_public_projection_sha256": hash_bytes(
                            canonical_bytes(final_projection), "sha256"
                        ),
                        "complete_expected_inventory": compact_local_rows(
                            state["local"], state["changed"]
                        ),
                        "anonymous_readback": anonymous_rows,
                        "anonymous_inventory_aggregate_sha256": hash_bytes(
                            canonical_bytes(anonymous_rows), "sha256"
                        ),
                    }
                )
        finally:
            auth.close()

        receipt_bytes, receipt_sha256 = write_receipt(
            args.receipt.resolve(), receipt_rows
        )
        return {
            "result": "published_and_anonymously_verified",
            "records": len(receipt_rows),
            "files_verified": sum(row["public_file_count"] for row in receipt_rows),
            "corrected_files": sum(row["corrected_file_count"] for row in receipt_rows),
            "access_reduction_performed": False,
            "receipt": str(args.receipt.resolve()),
            "receipt_bytes": receipt_bytes,
            "receipt_sha256": receipt_sha256,
        }
    finally:
        anon.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Correct two historical Zenodo file inventories in place."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="perform the authenticated edit-draft and publish transaction",
    )
    parser.add_argument(
        "--token-file",
        type=Path,
        help="path to the sensitive Zenodo token file; never written to receipts",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        default=DEFAULT_RECEIPT,
        help="credential-free receipt path",
    )
    return parser.parse_args()


def main() -> int:
    try:
        result = run(parse_args())
    except Exception as exc:  # noqa: BLE001 - fail closed with concise diagnostics
        print(json.dumps({"result": "fail", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
