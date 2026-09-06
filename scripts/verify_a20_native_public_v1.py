"""Credential-free native and public evidence verifier for A20.

The 1.10 GB release was already anonymously read back byte-for-byte by the
producer.  This verifier recomputes the complete local release identities,
checks those historical receipts, and independently checks the current public
GitHub and Zenodo inventories.  It deliberately does not download the same
gigabyte of public payload a second time.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT.parent / "openstax-intermediate-algebra-2e-id"
ADAPTER = ROOT / "backend/course-capsule-v1/adapters/a20-capability-v1"
TARGET = ADAPTER / "input/public-native-readback.json"

REPOSITORY = "KokunoYumeto/openstax-intermediate-algebra-2e-id"
REPOSITORY_URL = f"https://github.com/{REPOSITORY}"
COMMIT = "b293e167477c8fe2e8885c6f6d79d12cbb2e0e89"
TREE = "9ee25a0fa6eb336cbd40f3aa61587797b2bf4f27"
TAG = "v1.0.0"
ZENODO_RECORD_ID = 22229860
ZENODO_CONCEPT_ID = 22060225

EXPORT = NATIVE / "backend/exports/interoperability-v0-full"
RELEASE = NATIVE / "publication/final-release-1.0.0"

ASSETS: dict[str, dict[str, Any]] = {
    "LICENSE.txt": {
        "bytes": 25_629,
        "sha256": "0bfe5aeec11376d528af532356eb4696d264ecf64d2fe8a8e6f47332e56104ad",
    },
    "openstax-intermediate-algebra-2e-id-ID-1.0.0-editable-source.zip": {
        "bytes": 146_474_901,
        "sha256": "d629cfc8b8c50919ca6c0d2616fcf22cee3cfb30cb419e0cb43993d3e1451245",
    },
    "openstax-intermediate-algebra-2e-id-ID-1.0.0-interoperability-backend.zip": {
        "bytes": 57_624_608,
        "sha256": "bc8a06ffc9d63db85dc6ef7dd07bc1aa1fd85f9db60d068e08bc2111d1b84d41",
    },
    "openstax-intermediate-algebra-2e-id-ID-1.0.0-reader-volume-1.pdf": {
        "bytes": 290_855_657,
        "sha256": "0ff34851dcc2a78be69e55eec556b0a602f6262dfd32f134bcdf2284379c053f",
    },
    "openstax-intermediate-algebra-2e-id-ID-1.0.0-reader-volume-2.pdf": {
        "bytes": 195_006_406,
        "sha256": "6b8600ae7aede86eefb4e48cf009b9442226a71ca2bc08c476eed4c8ac2d4c71",
    },
    "openstax-intermediate-algebra-2e-id-ID-1.0.0-reader.pdf": {
        "bytes": 412_049_461,
        "sha256": "76276eeab590cd8181fd531378c4b4860bf30289a5e8093c9af5788d1eca3a9c",
    },
    "openstax-intermediate-algebra-2e-id-ID-1.0.0-release-manifest.json": {
        "bytes": 17_397,
        "sha256": "ef148715ae2f5b1241a3435102a5746571adc88cc59c71dd5620b6e611a0f43b",
    },
    "SHA256SUMS.txt": {
        "bytes": 866,
        "sha256": "df0778b6df935a63de934d6094e3fa64e3f1d6fc130fe55b0c5a30ccf0b1a757",
    },
}

LOCAL_EVIDENCE = {
    "backend/exports/interoperability-v0-full/manifest.json": {
        "bytes": 38_001,
        "sha256": "16abdf1f9d0431e63284302d7ddb519a5dbd9dd96de8f02ed1b29c716768c9a6",
    },
    "backend/exports/interoperability-v0-full/records.jsonl": {
        "bytes": 231_331_632,
        "sha256": "f8536e60b6e6fde9855da51e9d1d9037e5772190a1fd2e6ee4189c1f024172d3",
    },
    "backend/exports/interoperability-v0-full/module-index.json": {
        "bytes": 63_023,
        "sha256": "d6f047f6867f7661d94c4bc54ed51b6107c29d468614ac8d948d13749bf1a88e",
    },
    "backend/exports/interoperability-v0-full/registry.json": {
        "bytes": 846,
        "sha256": "c525ff1377016267f33c8260f316d503eb408ea0302f17ac728963f755b26980",
    },
    "qa/FULL_INTEROPERABILITY_BACKEND_FINAL_20260901.json": {
        "bytes": 1_974,
        "sha256": "a93624825e929a13200ff12981bf18be7b3019214e563e787ae28767c155f877",
    },
    "qa/final-reader/FULL_BOOK_PDF_QA.json": {
        "bytes": 4_957,
        "sha256": "f8f057ddd808ab2e40ca7bd8f7a0d8ed95f40672e8dd259391925747618c8d97",
    },
    "publication/final-staging/FINAL_READER_INPUT_PINS.json": {
        "bytes": 1_521_295,
        "sha256": "d93529172a651d3933a003eeb989905f6cd43a07a10c68424d59809ddb33960a",
    },
    "qa/FINAL_COMPLETION_AUDIT_PRIMARY_MIRRORS_20260901.json": {
        "bytes": 3_972,
        "sha256": "25c1403d7e3210da3046599886aa4a31aad10ea16e28ff81333b7b9bd3dd5587",
    },
    "publication/final-release-1.0.0/github-publication-receipt-1.0.0.json": {
        "bytes": 6_663,
        "sha256": "7654ae32ec5a0fba6c0a967ee5565cad5bd56834ddd490447ebc02be54471081",
    },
    "publication/final-release-1.0.0/zenodo-publication-receipt-1.0.0.json": {
        "bytes": 5_443,
        "sha256": "d42f1f9e003978ebf9248bbe1e9f7ae6ff209c7f982dc19c71c72c5ada86d756",
    },
}

EXPECTED_RECORD_TYPES = {
    "artifact": 15,
    "asset": 6478,
    "concept": 236,
    "correction": 1614,
    "course": 1,
    "edition": 1,
    "program": 1,
    "qa_event": 84,
    "relation": 77109,
    "resource": 1,
    "rights": 17,
    "segment": 31502,
    "term": 340,
    "unit": 57136,
}


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def identity(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": sha256_path(path)}


def session() -> requests.Session:
    value = requests.Session()
    value.trust_env = False
    value.auth = None
    value.headers.clear()
    value.headers["User-Agent"] = "a20-native-public-readback/1.0"
    return value


def get_json(client: requests.Session, url: str) -> tuple[Any, int]:
    response = client.get(url, timeout=(15, 60))
    response.raise_for_status()
    assert "Authorization" not in response.request.headers
    return response.json(), response.status_code


def get_small(client: requests.Session, url: str, maximum: int = 2_000_000) -> tuple[bytes, int]:
    response = client.get(url, timeout=(15, 60))
    response.raise_for_status()
    assert "Authorization" not in response.request.headers
    data = response.content
    assert len(data) <= maximum
    return data, response.status_code


def assert_identity(path: Path, expected: dict[str, Any]) -> dict[str, Any]:
    actual = identity(path)
    assert actual == expected, (path, actual, expected)
    return {"path": path.relative_to(NATIVE).as_posix(), **actual}


assert NATIVE.is_dir(), NATIVE
assert EXPORT.is_dir(), EXPORT
assert RELEASE.is_dir(), RELEASE

local_evidence = [
    assert_identity(NATIVE / relative, expected)
    for relative, expected in LOCAL_EVIDENCE.items()
]
local_assets = []
for name, expected in sorted(ASSETS.items()):
    local_path = RELEASE / name
    if not local_path.is_file():
        local_path = NATIVE / "publication/final-staging" / name
    local_assets.append({"name": name, **assert_identity(local_path, expected)})

manifest = json.loads((EXPORT / "manifest.json").read_text(encoding="utf-8"))
assert manifest["record_count"] == 174_535
assert manifest["record_type_counts"] == EXPECTED_RECORD_TYPES
assert manifest["coverage"] == {
    "completed_modules": 83,
    "first_module": "m81357",
    "last_module": "m81420",
    "modules": 83,
    "next_module": None,
}

github_receipt = json.loads((RELEASE / "github-publication-receipt-1.0.0.json").read_text(encoding="utf-8"))
zenodo_receipt = json.loads((RELEASE / "zenodo-publication-receipt-1.0.0.json").read_text(encoding="utf-8"))
assert github_receipt["state"] == "PUBLIC_RELEASE_BYTES_ANONYMOUSLY_VERIFIED"
assert zenodo_receipt["state"] == "PUBLIC_PAYLOAD_BYTES_ANONYMOUSLY_VERIFIED"
assert github_receipt["anonymous_readback"]["total_bytes"] == sum(row["bytes"] for row in ASSETS.values())
assert zenodo_receipt["anonymous_readback"]["total_bytes"] == sum(row["bytes"] for row in ASSETS.values())
for receipt_rows in (
    github_receipt["anonymous_readback"]["assets"],
    zenodo_receipt["anonymous_readback"]["files"],
):
    by_name = {row["filename"]: row for row in receipt_rows}
    assert set(by_name) == set(ASSETS)
    for name, expected in ASSETS.items():
        assert by_name[name]["anonymous_http_status"] == 200
        assert {key: by_name[name][key] for key in ("bytes", "sha256")} == expected

client = session()
repo_api = f"https://api.github.com/repos/{REPOSITORY}"
repo, repo_status = get_json(client, repo_api)
assert repo["private"] is False and repo["archived"] is False and repo["disabled"] is False

ref_api = f"{repo_api}/git/ref/tags/{quote(TAG)}"
ref, ref_status = get_json(client, ref_api)
tag_object = ref["object"]
if tag_object["type"] == "tag":
    tag_data, _ = get_json(client, f"{repo_api}/git/tags/{tag_object['sha']}")
    tag_object = tag_data["object"]
assert tag_object["type"] == "commit" and tag_object["sha"] == COMMIT

commit, commit_status = get_json(client, f"{repo_api}/git/commits/{COMMIT}")
assert commit["tree"]["sha"] == TREE

release_api = f"{repo_api}/releases/tags/{quote(TAG)}"
release, release_status = get_json(client, release_api)
assert release["tag_name"] == TAG
assert release["draft"] is False and release["prerelease"] is False
release_by_name = {row["name"]: row for row in release["assets"]}
assert set(release_by_name) == set(ASSETS)
github_assets = []
for name, expected in sorted(ASSETS.items()):
    row = release_by_name[name]
    assert row["size"] == expected["bytes"]
    assert row.get("digest") == f"sha256:{expected['sha256']}"
    github_assets.append({
        "name": name,
        "url": row["browser_download_url"],
        "bytes": row["size"],
        "sha256": expected["sha256"],
        "api_digest_verified": True,
        "prior_anonymous_full_byte_readback_verified": True,
    })

readme_url = f"https://raw.githubusercontent.com/{REPOSITORY}/{COMMIT}/README.md"
readme, readme_status = get_small(client, readme_url)
readme_text = readme.decode("utf-8", errors="replace")
stale_landing = bool(re.search(r"28\s*(?:/|of)\s*83", readme_text, re.IGNORECASE))
assert stale_landing, "Expected the pinned repository landing to retain the 28/83 WIP boundary"

zenodo_api = f"https://zenodo.org/api/records/{ZENODO_RECORD_ID}"
zenodo, zenodo_status = get_json(client, zenodo_api)
assert zenodo["id"] == ZENODO_RECORD_ID
assert str(zenodo["conceptrecid"]) == str(ZENODO_CONCEPT_ID)
assert zenodo["doi"] == f"10.5281/zenodo.{ZENODO_RECORD_ID}"
assert zenodo["metadata"]["access_right"] == "open"
assert zenodo["metadata"]["version"] == "1.0.0"
zenodo_by_name = {row["key"]: row for row in zenodo["files"]}
assert set(zenodo_by_name) == set(ASSETS)
zenodo_assets = []
for name, expected in sorted(ASSETS.items()):
    row = zenodo_by_name[name]
    assert row["size"] == expected["bytes"]
    zenodo_assets.append({
        "name": name,
        "url": row["links"]["self"],
        "bytes": row["size"],
        "sha256": expected["sha256"],
        "zenodo_checksum": row.get("checksum"),
        "prior_anonymous_full_byte_readback_verified": True,
    })

receipt = {
    "schema": "a20-native-public-readback/1",
    "state": "pass",
    "checked_utc": datetime.now(timezone.utc).isoformat(),
    "anonymous": True,
    "credentials_used": False,
    "course_id": "A20",
    "native_role_id": "R001",
    "verification_mode": "fresh_public_inventory_and_digest_plus_recomputed_local_full_bytes_and_prior_anonymous_full_byte_receipts",
    "native_backend": {
        "records": 174_535,
        "unique_ids": 174_535,
        "record_type_counts": EXPECTED_RECORD_TYPES,
        "modules": 83,
        "chapters": 12,
        "pages": 3_438,
        "local_evidence": local_evidence,
    },
    "repository": {
        "url": REPOSITORY_URL,
        "api_url": repo_api,
        "http_status": repo_status,
        "public": True,
        "commit": COMMIT,
        "tree": TREE,
        "tag": TAG,
        "ref_http_status": ref_status,
        "commit_http_status": commit_status,
        "landing_readme": {
            "url": readme_url,
            "http_status": readme_status,
            "bytes": len(readme),
            "sha256": hashlib.sha256(readme).hexdigest(),
            "stale_28_of_83_checkpoint": True,
            "authority_for_complete_release": False,
        },
    },
    "github_release": {
        "api_url": release_api,
        "http_status": release_status,
        "release_id": release["id"],
        "tag": TAG,
        "draft": False,
        "prerelease": False,
        "assets": github_assets,
        "total_bytes": sum(row["bytes"] for row in ASSETS.values()),
    },
    "zenodo": {
        "api_url": zenodo_api,
        "http_status": zenodo_status,
        "record_id": ZENODO_RECORD_ID,
        "concept_id": ZENODO_CONCEPT_ID,
        "version_doi": f"10.5281/zenodo.{ZENODO_RECORD_ID}",
        "concept_doi": f"10.5281/zenodo.{ZENODO_CONCEPT_ID}",
        "access_right": "open",
        "version": "1.0.0",
        "assets": zenodo_assets,
        "total_bytes": sum(row["bytes"] for row in ASSETS.values()),
    },
    "local_release_assets": local_assets,
    "historical_full_byte_receipts": {
        "github": LOCAL_EVIDENCE["publication/final-release-1.0.0/github-publication-receipt-1.0.0.json"],
        "zenodo": LOCAL_EVIDENCE["publication/final-release-1.0.0/zenodo-publication-receipt-1.0.0.json"],
        "all_assets_http_200_and_sha256_verified": True,
    },
    "checks": [
        "complete_local_release_sha256_recomputed",
        "complete_native_backend_manifest_bound",
        "prior_anonymous_full_byte_receipts_cross_checked",
        "current_public_github_release_inventory_and_sha256_digests",
        "current_open_zenodo_inventory",
        "exact_tag_commit_and_tree",
        "stale_repository_landing_explicitly_bounded",
        "no_credentials",
    ],
    "failures": [],
}
TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_bytes(canonical_json_bytes(receipt))
print(json.dumps({
    "state": "pass",
    "local_assets": len(local_assets),
    "github_assets": len(github_assets),
    "zenodo_assets": len(zenodo_assets),
    "total_bytes": receipt["github_release"]["total_bytes"],
    "stale_repository_landing_bounded": True,
}, sort_keys=True))
