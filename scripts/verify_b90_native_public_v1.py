"""Anonymous source, Pages, release, and Zenodo readback for B90/R010."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT.parent / "introduction-to-probability-id-b90-current"
ADAPTER = ROOT / "backend/course-capsule-v1/adapters/b90-capability-v1"
TARGET = ADAPTER / "input/public-native-readback.json"

REPOSITORY = "KokunoYumeto/introduction-to-probability-id"
REPOSITORY_URL = f"https://github.com/{REPOSITORY}"
PAGES_URL = "https://kokunoyumeto.github.io/introduction-to-probability-id/"
COMMIT = "5d1cfc55eecb678b0b4074160bc4f2d8bb2da5b6"
TREE = "21df3b2c0fab6827a21854bdcc41667a93edf749"
TAG = "v2026.08.22.1"
ZENODO_RECORD_ID = 22062144
ZENODO_CONCEPT_ID = 22048654

RAW_PATHS = (
    "README.md",
    "BUILD.md",
    "CENTRAL_HUB_HANDOFF.json",
    "authority/PUBLIC_AUTHORITY.md",
    "backend/public/README.md",
    "backend/public/PUBLIC_SAFE_EXPORT_MANIFEST.tsv",
    "backend/public/PUBLIC_SAFE_EXPORT_VALIDATION.json",
    "backend/public/record.schema.json",
    "backend/public/public-safe-main.records.jsonl",
    "backend/public/public-safe-main.records.csv",
    "index.html",
    "assets/reader.css",
    "assets/reader.js",
    "release/PENGANTAR_PELUANG_GRINSTEAD_SNELL_ID.pdf",
    "qa/MAIN_BOOK_FINAL_INPUT_MANIFEST.tsv",
    "qa/MAIN_BOOK_FINAL_QA.md",
    "qa/QUOTATION_AND_COMPONENT_RIGHTS_DISPOSITION.md",
    "qa/terminology-arxiv-qa/FINAL_COMPLETION_AUDIT.json",
    "source/LICENSES/GFDL-1.3.txt",
)

PAGES_PATHS = (
    "index.html",
    "assets/reader.css",
    "assets/reader.js",
    "release/PENGANTAR_PELUANG_GRINSTEAD_SNELL_ID.pdf",
)

RELEASE_ASSETS = {
    "PENGANTAR_PELUANG_GRINSTEAD_SNELL_ID.pdf": {
        "bytes": 3_403_487,
        "sha256": "f4921540bb47b09bb938bb18a5a6f78fd5340835fb834fe865f1eb0930b8b2b8",
    },
    "PENGANTAR_PELUANG_GRINSTEAD_SNELL_ID_SOURCE_v2026.08.22.1.zip": {
        "bytes": 2_220_925,
        "sha256": "26c62b6565b59ce5dcad146a29357dd1ada6133de50914ba57fe5ae058a81e1d",
    },
    "R010_MODULAR_BACKEND_PUBLIC_v2026.08.22.1.zip": {
        "bytes": 1_605_240,
        "sha256": "cfce8f41d06f35f30d3cdc4f0a829bc90f15ca1ef490f728ec2ff889adea30d8",
    },
}

EXPECTED_RECORD_TYPES = {
    "artifact": 82,
    "asset": 120,
    "concept": 91,
    "correction": 152,
    "course": 2,
    "edition": 2,
    "program": 1,
    "qa_event": 74,
    "relation": 1694,
    "resource": 1,
    "rights": 4,
    "segment": 1574,
    "term": 119,
    "unit": 800,
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(NATIVE), *arguments], text=True
    ).strip()


def git_bytes(path: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(NATIVE), "show", f"{COMMIT}:{path}"]
    )


def identity(data: bytes) -> dict[str, object]:
    return {"bytes": len(data), "sha256": sha256(data)}


def anonymous_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.auth = None
    session.headers.clear()
    session.headers["User-Agent"] = "b90-native-public-readback/1.0"
    return session


def get_bytes(session: requests.Session, url: str, maximum: int) -> bytes:
    received = bytearray()
    with session.get(url, stream=True, timeout=(15, 120)) as response:
        response.raise_for_status()
        assert "Authorization" not in response.request.headers
        for chunk in response.iter_content(65_536):
            received.extend(chunk)
            assert len(received) <= maximum
    return bytes(received)


assert NATIVE.is_dir(), NATIVE
assert git("rev-parse", "HEAD") == COMMIT
assert git("show", "-s", "--format=%T", "HEAD") == TREE

records_data = git_bytes("backend/public/public-safe-main.records.jsonl")
assert records_data.endswith(b"\n")
records = [json.loads(line) for line in records_data.splitlines()]
record_ids = [row["id"] for row in records]
record_types = dict(sorted(Counter(row["record_type"] for row in records).items()))
assert len(records) == 4_716
assert len(set(record_ids)) == 4_716
assert record_types == EXPECTED_RECORD_TYPES

session = anonymous_session()
repository = session.get(REPOSITORY_URL, timeout=(15, 30))
repository.raise_for_status()
assert "Authorization" not in repository.request.headers

raw_rows: list[dict[str, object]] = []
for path in RAW_PATHS:
    local = git_bytes(path)
    url = (
        f"https://raw.githubusercontent.com/{REPOSITORY}/{COMMIT}/"
        + quote(path)
    )
    received = get_bytes(session, url, len(local))
    assert received == local, path
    raw_rows.append(
        {
            "path": path,
            "url": url,
            "http_status": 200,
            "bytes": len(received),
            "sha256": sha256(received),
        }
    )

pages_rows: list[dict[str, object]] = []
for path in PAGES_PATHS:
    local = git_bytes(path)
    url = PAGES_URL + quote(path)
    received = get_bytes(session, url, len(local))
    assert received == local, path
    pages_rows.append(
        {
            "path": path,
            "url": url,
            "http_status": 200,
            "bytes": len(received),
            "sha256": sha256(received),
        }
    )

release_url = f"https://api.github.com/repos/{REPOSITORY}/releases/tags/{TAG}"
release_response = session.get(release_url, timeout=(15, 60))
release_response.raise_for_status()
assert "Authorization" not in release_response.request.headers
release = release_response.json()
assert release["tag_name"] == TAG
assert release["target_commitish"] == COMMIT
assert release["draft"] is False and release["prerelease"] is False
release_by_name = {row["name"]: row for row in release["assets"]}
assert set(release_by_name) == set(RELEASE_ASSETS)

release_rows: list[dict[str, object]] = []
release_bytes: dict[str, bytes] = {}
for name, expected in RELEASE_ASSETS.items():
    source = release_by_name[name]
    assert source["size"] == expected["bytes"]
    assert source.get("digest") == f"sha256:{expected['sha256']}"
    received = get_bytes(session, source["browser_download_url"], expected["bytes"])
    assert len(received) == expected["bytes"]
    assert sha256(received) == expected["sha256"]
    release_bytes[name] = received
    release_rows.append(
        {
            "name": name,
            "url": source["browser_download_url"],
            "http_status": 200,
            **expected,
        }
    )

zenodo_url = f"https://zenodo.org/api/records/{ZENODO_RECORD_ID}"
zenodo_response = session.get(zenodo_url, timeout=(15, 60))
zenodo_response.raise_for_status()
assert "Authorization" not in zenodo_response.request.headers
zenodo = zenodo_response.json()
assert zenodo["id"] == ZENODO_RECORD_ID
assert zenodo["doi"] == f"10.5281/zenodo.{ZENODO_RECORD_ID}"
assert zenodo["conceptrecid"] == str(ZENODO_CONCEPT_ID)
assert zenodo["metadata"]["access_right"] == "open"
zenodo_by_name = {row["key"]: row for row in zenodo["files"]}
assert set(zenodo_by_name) == set(RELEASE_ASSETS)

zenodo_rows: list[dict[str, object]] = []
for name, expected in RELEASE_ASSETS.items():
    source = zenodo_by_name[name]
    assert source["size"] == expected["bytes"]
    received = get_bytes(session, source["links"]["self"], expected["bytes"])
    assert received == release_bytes[name]
    zenodo_rows.append(
        {
            "name": name,
            "url": source["links"]["self"],
            "http_status": 200,
            **expected,
            "github_release_byte_identity": True,
        }
    )

receipt = {
    "schema": "b90-native-public-readback/1",
    "state": "pass",
    "checked_utc": datetime.now(timezone.utc).isoformat(),
    "anonymous": True,
    "credentials_used": False,
    "course_id": "B90",
    "native_role_id": "R010",
    "repository": {
        "url": REPOSITORY_URL,
        "commit": COMMIT,
        "tree": TREE,
        "tag": TAG,
        "pages_url": PAGES_URL,
    },
    "record_backend": {
        "records": len(records),
        "unique_ids": len(set(record_ids)),
        "type_counts": record_types,
        "jsonl": identity(records_data),
        "csv": identity(git_bytes("backend/public/public-safe-main.records.csv")),
    },
    "raw_source_files": raw_rows,
    "pages_files": pages_rows,
    "github_release": {
        "api_url": release_url,
        "tag": TAG,
        "target_commit": COMMIT,
        "draft": False,
        "prerelease": False,
        "assets": release_rows,
    },
    "zenodo": {
        "api_url": zenodo_url,
        "record_id": ZENODO_RECORD_ID,
        "concept_id": ZENODO_CONCEPT_ID,
        "version_doi": f"10.5281/zenodo.{ZENODO_RECORD_ID}",
        "concept_doi": f"10.5281/zenodo.{ZENODO_CONCEPT_ID}",
        "access_right": "open",
        "assets": zenodo_rows,
    },
    "checks": [
        "exact_git_commit_and_tree",
        "4716_unique_schema_versioned_public_records",
        "record_type_counts",
        "raw_commit_byte_identity",
        "live_pages_byte_identity",
        "github_release_asset_sha256",
        "open_zenodo_inventory",
        "zenodo_github_release_byte_identity",
        "no_credentials",
    ],
    "failures": [],
}
TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(
    json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(
    json.dumps(
        {
            "state": "pass",
            "raw_files": len(raw_rows),
            "pages_files": len(pages_rows),
            "release_assets": len(release_rows),
            "zenodo_assets": len(zenodo_rows),
            "records": len(records),
        },
        sort_keys=True,
    )
)
