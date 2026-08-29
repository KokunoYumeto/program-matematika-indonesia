#!/usr/bin/env python3
"""Reserve PMI v0.62.6 as a new Zenodo version without changing its payload.

This script performs the single mutating ``newversion`` request.  It deliberately
does not edit metadata or files; the publication script owns those operations.
The credential is read only in process and is never written to stdout or the
sanitized reservation receipt.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse

import requests


PROJECT = Path(__file__).resolve().parents[1]
VERSION = "0.62.6"
CONCEPT_ID = 22059707
PREDECESSOR_ID = 22166520
PREDECESSOR_VERSION = "0.62.5"
EXPECTED_INHERITED_FILES = 88
EXPECTED_TOTAL_FILES = 93
API = "https://zenodo.org/api/deposit/depositions"
PUBLIC_API = "https://zenodo.org/api/records"
DEFAULT_RECEIPT = PROJECT / f"ZENODO_RESERVATION_RECEIPT_v{VERSION}.json"
OVERLAY_NAMES = {
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.6.html",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.6.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.6.zip",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.6.json",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.6.sha256",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def compact_sha256(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_token(token_file: Path) -> str:
    require(token_file.is_file(), "Zenodo credential file is unavailable")
    text = token_file.read_text(encoding="utf-8")
    candidates = re.findall(
        r"(?<![A-Za-z0-9._~-])([A-Za-z0-9._~-]{40,})(?![A-Za-z0-9._~-])",
        text,
    )
    require(bool(candidates), "Zenodo credential file contains no token candidate")
    return max(candidates, key=len)


def concept_id_of(record: dict[str, object]) -> int:
    value = record.get("conceptrecid")
    if value is None:
        metadata = record.get("metadata", {})
        if isinstance(metadata, dict):
            relations = metadata.get("relations", {})
            if isinstance(relations, dict):
                versions = relations.get("version", [])
                if isinstance(versions, list) and versions:
                    first = versions[0]
                    if isinstance(first, dict):
                        parent = first.get("parent", {})
                        if isinstance(parent, dict):
                            value = parent.get("pid_value")
    require(value is not None, "Zenodo response does not expose the concept record")
    return int(value)


def license_id(metadata: dict[str, object]) -> str | None:
    value = metadata.get("license")
    if isinstance(value, dict):
        raw = value.get("id")
        return str(raw) if raw is not None else None
    return str(value) if value is not None else None


def public_file_facts(
    record: dict[str, object], expected_count: int = EXPECTED_INHERITED_FILES
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for remote in record.get("files", []):
        require(isinstance(remote, dict), "predecessor exposes a malformed file row")
        name = remote.get("key")
        size = remote.get("size")
        checksum = str(remote.get("checksum", "")).removeprefix("md5:")
        require(isinstance(name, str) and name, "predecessor file has no name")
        require(isinstance(size, int) and size >= 0, f"predecessor file has invalid size: {name}")
        require(re.fullmatch(r"[0-9a-f]{32}", checksum) is not None, f"predecessor file has invalid MD5: {name}")
        rows.append({"name": name, "bytes": size, "md5": checksum})
    rows.sort(key=lambda row: str(row["name"]))
    require(len(rows) == expected_count, f"public record must expose exactly {expected_count} files")
    require(len({row["name"] for row in rows}) == len(rows), "predecessor contains duplicate filenames")
    return rows


def draft_file_facts(draft: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for remote in draft.get("files", []):
        require(isinstance(remote, dict), "draft exposes a malformed file row")
        name = remote.get("filename")
        size = remote.get("filesize")
        checksum = str(remote.get("checksum", "")).removeprefix("md5:")
        require(isinstance(name, str) and name, "draft file has no name")
        require(isinstance(size, int) and size >= 0, f"draft file has invalid size: {name}")
        require(re.fullmatch(r"[0-9a-f]{32}", checksum) is not None, f"draft file has invalid MD5: {name}")
        rows.append({"name": name, "bytes": size, "md5": checksum})
    rows.sort(key=lambda row: str(row["name"]))
    require(len({row["name"] for row in rows}) == len(rows), "draft contains duplicate filenames")
    return rows


def require_public_predecessor(record: dict[str, object]) -> list[dict[str, object]]:
    require(int(record.get("id", -1)) == PREDECESSOR_ID, "predecessor record ID differs")
    require(record.get("doi") == f"10.5281/zenodo.{PREDECESSOR_ID}", "predecessor DOI differs")
    require(record.get("conceptdoi") == f"10.5281/zenodo.{CONCEPT_ID}", "predecessor concept DOI differs")
    metadata = record.get("metadata", {})
    require(isinstance(metadata, dict), "predecessor metadata is malformed")
    require(metadata.get("version") == PREDECESSOR_VERSION, "predecessor version differs")
    require(metadata.get("access_right") == "open", "predecessor access is not open")
    require(license_id(metadata) == "other-open", "predecessor license differs")
    require(metadata.get("language") == "ind", "predecessor language differs")
    creators = metadata.get("creators")
    contributors = metadata.get("contributors")
    require(isinstance(creators, list) and creators, "predecessor creator array is absent")
    require(isinstance(contributors, list), "predecessor contributor array is absent")
    return public_file_facts(record)


def write_receipt(path: Path, payload: dict[str, object]) -> tuple[int, str]:
    data = canonical_bytes(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return len(data), hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token-file", required=True, type=Path)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()

    public_predecessor_response = requests.get(f"{PUBLIC_API}/{PREDECESSOR_ID}", timeout=120)
    public_predecessor_response.raise_for_status()
    public_predecessor = public_predecessor_response.json()
    inherited_files = require_public_predecessor(public_predecessor)
    predecessor_metadata = public_predecessor["metadata"]

    latest_response = requests.get(f"{PUBLIC_API}/{CONCEPT_ID}/versions/latest", timeout=120)
    latest_response.raise_for_status()
    latest = latest_response.json()
    latest_id = int(latest["id"])
    if latest_id != PREDECESSOR_ID:
        require(
            latest.get("metadata", {}).get("version") == VERSION,
            "concept latest is neither the required predecessor nor the requested successor version",
        )
        require(latest.get("doi") == f"10.5281/zenodo.{latest_id}", "successor candidate DOI differs")
        require(latest.get("conceptdoi") == f"10.5281/zenodo.{CONCEPT_ID}", "successor candidate concept DOI differs")
        latest_metadata = latest.get("metadata", {})
        require(isinstance(latest_metadata, dict), "successor candidate metadata is malformed")
        require(latest_metadata.get("access_right") == "open", "successor candidate access is not open")
        require(license_id(latest_metadata) == "other-open", "successor candidate license differs")
        require(latest_metadata.get("language") == "ind", "successor candidate language differs")
        require(latest_metadata.get("creators") == predecessor_metadata.get("creators"), "successor candidate creators differ")
        require(latest_metadata.get("contributors") == predecessor_metadata.get("contributors"), "successor candidate contributors differ")
        candidate_files = public_file_facts(latest, EXPECTED_TOTAL_FILES)
        inherited_by_name = {row["name"]: row for row in inherited_files}
        candidate_by_name = {row["name"]: row for row in candidate_files}
        require(set(inherited_by_name).issubset(candidate_by_name), "successor candidate is missing an inherited file")
        require(
            {name for name in candidate_by_name if name not in inherited_by_name} == OVERLAY_NAMES,
            "successor candidate additive filenames differ",
        )
        for name, expected in inherited_by_name.items():
            require(candidate_by_name[name] == expected, f"successor candidate changed inherited file metadata: {name}")
        receipt = {
            "schema_id": "program-matematika-indonesia/zenodo-live-overlay-reservation/v1",
            "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "result": "successor_candidate_already_published",
            "version": VERSION,
            "concept_record_id": CONCEPT_ID,
            "predecessor_record_id": PREDECESSOR_ID,
            "reserved_record_id": latest_id,
            "predecessor_file_count": len(inherited_files),
            "predecessor_inventory_md5_aggregate_sha256": compact_sha256(inherited_files),
            "candidate_file_count": len(candidate_files),
            "candidate_inventory_md5_aggregate_sha256": compact_sha256(candidate_files),
            "requires_publish_script_full_sha256_verification": True,
            "credentials_recorded": False,
            "mutation_performed": False,
        }
        receipt_bytes, receipt_sha256 = write_receipt(args.receipt.resolve(), receipt)
        print(json.dumps({
            "result": "successor_candidate_requires_full_publisher_verification",
            "record_id": latest_id,
            "receipt": args.receipt.name,
            "receipt_bytes": receipt_bytes,
            "receipt_sha256": receipt_sha256,
        }, sort_keys=True))
        return 0

    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {load_token(args.token_file.resolve())}"})
    authenticated_predecessor_response = session.get(f"{API}/{PREDECESSOR_ID}", timeout=120)
    authenticated_predecessor_response.raise_for_status()
    authenticated_predecessor = authenticated_predecessor_response.json()
    require(authenticated_predecessor.get("submitted") is True, "authenticated predecessor is not published")
    require(concept_id_of(authenticated_predecessor) == CONCEPT_ID, "authenticated predecessor concept differs")
    authenticated_metadata = authenticated_predecessor.get("metadata", {})
    require(isinstance(authenticated_metadata, dict), "authenticated predecessor metadata is malformed")
    require(authenticated_metadata.get("version") == PREDECESSOR_VERSION, "authenticated predecessor version differs")
    require(
        authenticated_metadata.get("creators") == predecessor_metadata.get("creators"),
        "authenticated predecessor creators differ from public predecessor",
    )
    require(
        authenticated_metadata.get("contributors") == predecessor_metadata.get("contributors"),
        "authenticated predecessor contributors differ from public predecessor",
    )

    response = session.post(f"{API}/{PREDECESSOR_ID}/actions/newversion", timeout=180)
    if response.status_code == 201:
        newversion_http_status = 201
        action_payload = response.json()
        draft_url = action_payload.get("links", {}).get("latest_draft")
    elif response.status_code == 409:
        newversion_http_status = 409
        refreshed_response = session.get(f"{API}/{PREDECESSOR_ID}", timeout=120)
        refreshed_response.raise_for_status()
        refreshed_predecessor = refreshed_response.json()
        draft_url = refreshed_predecessor.get("links", {}).get("latest_draft")
    else:
        response.raise_for_status()
        raise AssertionError("unreachable")
    require(isinstance(draft_url, str) and draft_url, "successor draft link is absent")
    require(urlparse(draft_url).scheme == "https", "successor draft link is not HTTPS")
    draft_response = session.get(draft_url, timeout=120)
    draft_response.raise_for_status()
    draft = draft_response.json()
    require(draft.get("submitted") is False, "successor is not an editable draft")
    require(concept_id_of(draft) == CONCEPT_ID, "successor draft concept differs")
    draft_id = int(draft["id"])
    require(draft_id not in {PREDECESSOR_ID, CONCEPT_ID}, "successor draft record ID is invalid")
    draft_metadata = draft.get("metadata", {})
    require(isinstance(draft_metadata, dict), "successor draft metadata is malformed")
    require(draft_metadata.get("creators") == predecessor_metadata.get("creators"), "successor draft creators changed")
    require(draft_metadata.get("contributors") == predecessor_metadata.get("contributors"), "successor draft contributors changed")
    draft_files = draft_file_facts(draft)
    inherited_by_name = {row["name"]: row for row in inherited_files}
    draft_by_name = {row["name"]: row for row in draft_files}
    require(set(inherited_by_name).issubset(draft_by_name), "successor draft is missing an inherited file")
    extra_names = set(draft_by_name) - set(inherited_by_name)
    require(extra_names.issubset(OVERLAY_NAMES), "successor draft contains a file outside the 88+5 boundary")
    for name, expected in inherited_by_name.items():
        require(draft_by_name[name] == expected, f"successor draft changed inherited file metadata: {name}")

    receipt = {
        "schema_id": "program-matematika-indonesia/zenodo-live-overlay-reservation/v1",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": "pass",
        "version": VERSION,
        "concept_record_id": CONCEPT_ID,
        "concept_doi": f"10.5281/zenodo.{CONCEPT_ID}",
        "predecessor_record_id": PREDECESSOR_ID,
        "predecessor_doi": f"10.5281/zenodo.{PREDECESSOR_ID}",
        "predecessor_version": PREDECESSOR_VERSION,
        "reserved_record_id": draft_id,
        "reserved_doi": f"10.5281/zenodo.{draft_id}",
        "state": "draft_reserved_in_existing_concept",
        "newversion_http_status": newversion_http_status,
        "visibility_intent": "public_open",
        "inherited_file_count": len(inherited_files),
        "inherited_inventory_md5_aggregate_sha256": compact_sha256(inherited_files),
        "already_present_overlay_file_count": len(extra_names),
        "already_present_overlay_filenames": sorted(extra_names),
        "creator_array_count": len(predecessor_metadata["creators"]),
        "creator_array_canonical_sha256": compact_sha256(predecessor_metadata["creators"]),
        "contributor_array_count": len(predecessor_metadata["contributors"]),
        "contributor_array_canonical_sha256": compact_sha256(predecessor_metadata["contributors"]),
        "authenticated_draft_readback": "pass",
        "credentials_recorded": False,
        "metadata_or_file_mutation_performed": False,
        "next_action": (
            "Run publish-live-overlay-zenodo.py with this reserved record ID and the validated "
            "flat 93-file releases/v0.62.6 payload; only its five fixed additive files may be uploaded."
        ),
    }
    receipt_bytes, receipt_sha256 = write_receipt(args.receipt.resolve(), receipt)
    print(json.dumps({
        "result": "reserved_and_verified",
        "record_id": draft_id,
        "receipt": args.receipt.name,
        "receipt_bytes": receipt_bytes,
        "receipt_sha256": receipt_sha256,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
