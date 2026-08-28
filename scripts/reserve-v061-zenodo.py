#!/usr/bin/env python3
"""Reserve the v0.61.0 Zenodo version in the existing PMI concept.

The credential is read in process and is never written to stdout or receipts.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import requests


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
TOKEN_FILE = Path.home() / "Documents" / "Obsidian notes" / "New zenodo token.md"
LOGBOOK = WORKSPACE / "outputs" / "01a01ec1-e685-70d0-b022-211396334723" / "curriculum_logbook"
OUTPUT = LOGBOOK / "129_CENTRAL_V061_ZENODO_DRAFT_RESERVATION_20260828.json"

VERSION = "0.61.0"
CONCEPT_ID = 22059707
PREDECESSOR_ID = 22143506
API = "https://zenodo.org/api/deposit/depositions"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_token() -> str:
    text = TOKEN_FILE.read_text(encoding="utf-8")
    candidates = re.findall(
        r"(?<![A-Za-z0-9._~-])([A-Za-z0-9._~-]{40,})(?![A-Za-z0-9._~-])",
        text,
    )
    require(bool(candidates), "Zenodo credential file contains no token candidate")
    return max(candidates, key=len)


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def concept_id_of(record: dict[str, object]) -> int:
    value = record.get("conceptrecid")
    if value is None:
        relations = record.get("metadata", {}).get("relations", {})  # type: ignore[union-attr]
        versions = relations.get("version", [])
        if versions:
            value = versions[0].get("parent", {}).get("pid_value")
    require(value is not None, "Zenodo response does not expose the concept record")
    return int(value)


def main() -> int:
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {load_token()}"})

    predecessor_response = session.get(f"{API}/{PREDECESSOR_ID}", timeout=120)
    predecessor_response.raise_for_status()
    predecessor = predecessor_response.json()
    require(predecessor.get("submitted") is True, "predecessor is not a published deposition")
    require(concept_id_of(predecessor) == CONCEPT_ID, "predecessor belongs to another concept")
    require(predecessor.get("metadata", {}).get("version") == "0.60.0", "predecessor version differs")

    response = session.post(f"{API}/{PREDECESSOR_ID}/actions/newversion", timeout=180)
    if response.status_code == 201:
        request_status = 201
        payload = response.json()
        draft_url = payload.get("links", {}).get("latest_draft")
        require(isinstance(draft_url, str), "new-version response has no draft link")
        draft_response = session.get(draft_url, timeout=120)
        draft_response.raise_for_status()
        draft = draft_response.json()
    elif response.status_code == 409:
        # Zenodo returns 409 if a successor draft already exists. Follow the
        # predecessor's latest-draft link and accept it only if it is still the
        # unpublished successor in this exact concept.
        request_status = 409
        draft_url = predecessor.get("links", {}).get("latest_draft")
        require(isinstance(draft_url, str), "existing draft cannot be located")
        draft_response = session.get(draft_url, timeout=120)
        draft_response.raise_for_status()
        draft = draft_response.json()
    else:
        response.raise_for_status()
        raise AssertionError("unreachable")

    require(draft.get("submitted") is False, "successor is not an unpublished draft")
    require(concept_id_of(draft) == CONCEPT_ID, "successor draft belongs to another concept")
    draft_id = int(draft["id"])
    require(draft_id != PREDECESSOR_ID, "successor draft reuses predecessor record ID")
    inherited_files = len(draft.get("files", []))

    receipt = {
        "schema_id": "program-matematika-indonesia/zenodo-version-reservation/v1",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "manager_thread_id": "01a01ec1-e685-70d0-b022-211396334723",
        "program_version": VERSION,
        "result": "pass",
        "existing_concept": {
            "concept_record_id": CONCEPT_ID,
            "concept_doi": f"10.5281/zenodo.{CONCEPT_ID}",
            "predecessor_record_id": PREDECESSOR_ID,
            "predecessor_doi": f"10.5281/zenodo.{PREDECESSOR_ID}",
            "predecessor_version": "0.60.0",
        },
        "reserved_version": {
            "draft_record_id": draft_id,
            "reserved_doi": f"10.5281/zenodo.{draft_id}",
            "draft_url": f"https://zenodo.org/uploads/{draft_id}",
            "state": "draft_reserved",
            "visibility_intent": "public_open",
            "inherited_files": inherited_files,
        },
        "authorization_route": {
            "method": "existing scoped Zenodo API credential",
            "new_version_http_status": request_status,
            "authenticated_draft_readback": "pass",
            "credential_material_recorded": False,
        },
        "release_boundary": (
            "This is an unpublished version reservation in the existing concept, not a publication receipt. "
            "Upload, metadata validation, public publication, and anonymous file-by-file SHA-256 readback remain required."
        ),
        "next_action": (
            f"Generate and validate the complete v{VERSION} payload using record ID {draft_id}, replace the inherited "
            f"v0.60.0 draft inventory with the exact validated v{VERSION} inventory, preserve public-open metadata, "
            "publish, and anonymously verify every file."
        ),
    }
    data = canonical(receipt)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(data)
    print(json.dumps({
        "result": "pass",
        "draft_record_id": draft_id,
        "receipt": str(OUTPUT),
        "receipt_bytes": len(data),
        "receipt_sha256": hashlib.sha256(data).hexdigest(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
