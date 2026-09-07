"""Credential-free local/public evidence verifier for the A30 1.0.0 release.

The producer receipts already record anonymous full-byte SHA-256 readback of
all seven public assets.  This verifier recomputes the complete local assets,
checks those receipts, and performs fresh anonymous GitHub and Zenodo inventory
checks.  It intentionally does not re-download the 499.9 MB payload.

No final derivative Git commit or tree is inferred from the release tag: the
producer evidence proves the release and its upstream source revision, but not
that stronger derivative-revision claim.
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from a30_capability_model_v1 import (
    BACKEND_ARCHIVE,
    BACKEND_RECORD_MEMBER,
    COURSE_ID,
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    EXPECTED_CANONICAL_BYTES,
    EXPECTED_CANONICAL_SHA256,
    EXPECTED_LOCAL_INPUTS,
    EXPECTED_PUBLIC_ASSETS,
    EXPECTED_PUBLIC_TOTAL_BYTES,
    NATIVE_ROLE_ID,
    PUBLIC_RECEIPT_PATH,
    PUBLIC_REPOSITORY,
    RELEASE_TAG,
    UPSTREAM_COMMIT,
    UPSTREAM_REPOSITORY,
    UPSTREAM_TREE,
    ZENODO_CONCEPT_ID,
    ZENODO_RECORD_ID,
    canonical_json_bytes,
    identity,
)


REPOSITORY = "KokunoYumeto/openstax-precalculus-2e-id"
LOCAL_ASSET_PATHS = {
    "LICENSE.txt": Path("release/reader/1.0.0/LICENSE.txt"),
    "OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf": Path("output/final-3165/OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf"),
    "README.txt": Path("release/reader/1.0.0/README.txt"),
    "SHA256SUMS.txt": Path("release/reader/1.0.0/SHA256SUMS.txt"),
    "precalculus-2e-id-ID-1.0.0-backend-core.zip": BACKEND_ARCHIVE,
    "precalculus-2e-id-ID-1.0.0-manifest.json": Path("release/reader/1.0.0/precalculus-2e-id-ID-1.0.0-manifest.json"),
    "precalculus-2e-id-ID-1.0.0-source-core.zip": Path("release/reader/1.0.0/precalculus-2e-id-ID-1.0.0-source-core.zip"),
}


class VerificationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def get_json(url: str) -> tuple[Any, int]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json, application/json",
            "User-Agent": "a30-native-public-readback/1.0",
        },
        method="GET",
    )
    require("Authorization" not in request.headers, "authorization header unexpectedly present")
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
        return json.loads(data), int(response.status)


def asset_map(rows: Any) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("name") or row.get("filename") or row.get("key")): {
            "bytes": int(row.get("bytes") if row.get("bytes") is not None else row.get("size")),
            "sha256": row.get("sha256"),
        }
        for row in (rows or [])
    }


def local_identity(native_root: Path, name: str) -> dict[str, Any]:
    path = native_root / LOCAL_ASSET_PATHS[name]
    sha256 = hashlib.sha256()
    md5 = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            sha256.update(chunk)
            md5.update(chunk)
    actual = {
        "path": LOCAL_ASSET_PATHS[name].as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256.hexdigest(),
        "md5": md5.hexdigest(),
    }
    expected = EXPECTED_PUBLIC_ASSETS[name]
    require(
        {"bytes": actual["bytes"], "sha256": actual["sha256"]} == expected,
        f"local release asset identity drift: {name}",
    )
    return {"name": name, **actual}


def verify(native_root: Path = DEFAULT_NATIVE, target: Path = PUBLIC_RECEIPT_PATH) -> dict[str, Any]:
    native_root = native_root.resolve()
    local_evidence = []
    for relative, expected in EXPECTED_LOCAL_INPUTS.items():
        actual = identity(native_root / Path(relative), display_path=relative)
        require(
            {"bytes": actual["bytes"], "sha256": actual["sha256"]} == expected,
            f"pinned producer evidence drift: {relative}",
        )
        local_evidence.append(actual)

    local_assets = [local_identity(native_root, name) for name in sorted(EXPECTED_PUBLIC_ASSETS)]
    local_assets_by_name = {row["name"]: row for row in local_assets}
    require(sum(row["bytes"] for row in local_assets) == EXPECTED_PUBLIC_TOTAL_BYTES, "local release byte total drift")

    archive_path = native_root / BACKEND_ARCHIVE
    with zipfile.ZipFile(archive_path, "r") as archive:
        info = archive.getinfo(BACKEND_RECORD_MEMBER)
        digest = hashlib.sha256()
        with archive.open(BACKEND_RECORD_MEMBER, "r") as member:
            for chunk in iter(lambda: member.read(4 * 1024 * 1024), b""):
                digest.update(chunk)
    require(info.file_size == EXPECTED_CANONICAL_BYTES, "canonical member byte count drift")
    require(digest.hexdigest() == EXPECTED_CANONICAL_SHA256, "canonical member SHA-256 drift")

    github_receipt = json.loads((native_root / "qa/GITHUB_READER_1.0.0_20260904.json").read_text(encoding="utf-8"))
    zenodo_receipt = json.loads((native_root / "qa/ZENODO_READER_1.0.0_20260904.json").read_text(encoding="utf-8"))
    require(github_receipt.get("status") == "public_and_anonymously_byte_verified", "producer GitHub receipt is not passing")
    require(zenodo_receipt.get("status") == "published_and_anonymously_verified", "producer Zenodo receipt is not passing")
    require(asset_map(github_receipt.get("release", {}).get("anonymous_asset_readback")) == EXPECTED_PUBLIC_ASSETS, "producer GitHub full-byte receipt drift")
    require(asset_map(zenodo_receipt.get("zenodo", {}).get("anonymous_file_readback")) == EXPECTED_PUBLIC_ASSETS, "producer Zenodo full-byte receipt drift")

    repo_api = f"https://api.github.com/repos/{REPOSITORY}"
    repo, repo_status = get_json(repo_api)
    require(repo.get("private") is False and repo.get("archived") is False and repo.get("disabled") is False, "GitHub repository is not public and active")

    release_api = f"{repo_api}/releases/tags/{urllib.parse.quote(RELEASE_TAG)}"
    release, release_status = get_json(release_api)
    require(release.get("tag_name") == RELEASE_TAG, "GitHub release tag drift")
    require(release.get("draft") is False and release.get("prerelease") is False, "GitHub release is not final")
    release_by_name = {str(row["name"]): row for row in release.get("assets", [])}
    require(set(release_by_name) == set(EXPECTED_PUBLIC_ASSETS), "GitHub release asset inventory drift")
    github_assets = []
    for name, expected in sorted(EXPECTED_PUBLIC_ASSETS.items()):
        row = release_by_name[name]
        require(int(row.get("size")) == expected["bytes"], f"GitHub asset size drift: {name}")
        require(row.get("digest") == f"sha256:{expected['sha256']}", f"GitHub asset digest drift: {name}")
        github_assets.append({
            "name": name,
            "url": row["browser_download_url"],
            "bytes": expected["bytes"],
            "sha256": expected["sha256"],
            "api_digest_verified": True,
            "prior_anonymous_full_byte_readback_verified": True,
        })

    zenodo_api = f"https://zenodo.org/api/records/{ZENODO_RECORD_ID}"
    zenodo, zenodo_status = get_json(zenodo_api)
    require(int(zenodo.get("id")) == ZENODO_RECORD_ID, "Zenodo record drift")
    require(int(zenodo.get("conceptrecid")) == ZENODO_CONCEPT_ID, "Zenodo concept lineage drift")
    require(zenodo.get("doi") == f"10.5281/zenodo.{ZENODO_RECORD_ID}", "Zenodo DOI drift")
    require(zenodo.get("metadata", {}).get("access_right") == "open", "Zenodo record is not open")
    require(zenodo.get("metadata", {}).get("version") == "1.0.0", "Zenodo version drift")
    zenodo_by_name = {str(row["key"]): row for row in zenodo.get("files", [])}
    require(set(zenodo_by_name) == set(EXPECTED_PUBLIC_ASSETS), "Zenodo asset inventory drift")
    zenodo_assets = []
    for name, expected in sorted(EXPECTED_PUBLIC_ASSETS.items()):
        row = zenodo_by_name[name]
        require(int(row.get("size")) == expected["bytes"], f"Zenodo asset size drift: {name}")
        checksum = str(row.get("checksum") or "").casefold()
        require(
            checksum in {local_assets_by_name[name]["md5"], f"md5:{local_assets_by_name[name]['md5']}"},
            f"Zenodo asset checksum drift: {name}",
        )
        zenodo_assets.append({
            "name": name,
            "url": row["links"]["self"],
            "bytes": expected["bytes"],
            "sha256": expected["sha256"],
            "zenodo_checksum": row.get("checksum"),
            "zenodo_checksum_verified_against_local_bytes": True,
            "prior_anonymous_full_byte_readback_verified": True,
        })

    receipt = {
        "schema": "a30-native-public-readback/1",
        "state": "pass",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "anonymous": True,
        "credentials_used": False,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "verification_mode": "fresh_public_inventory_and_github_digest_plus_recomputed_local_full_bytes_and_prior_anonymous_full_byte_receipts",
        "native_backend": {
            "records": 220_680,
            "unique_ids": 220_680,
            "canonical_member": {
                "path": f"{BACKEND_ARCHIVE.as_posix()}#{BACKEND_RECORD_MEMBER}",
                "bytes": info.file_size,
                "sha256": digest.hexdigest(),
            },
            "modules": 87,
            "chapters": 12,
            "pages": 3_165,
            "local_evidence": local_evidence,
        },
        "upstream_source": {
            "repository": UPSTREAM_REPOSITORY,
            "commit": UPSTREAM_COMMIT,
            "tree": UPSTREAM_TREE,
        },
        "repository": {
            "url": PUBLIC_REPOSITORY,
            "api_url": repo_api,
            "http_status": repo_status,
            "public": True,
            "default_branch": repo.get("default_branch"),
            "tag": RELEASE_TAG,
            "final_derivative_commit": None,
            "final_derivative_tree": None,
            "final_derivative_revision_proved": False,
        },
        "github_release": {
            "url": f"{PUBLIC_REPOSITORY}/releases/tag/{RELEASE_TAG}",
            "api_url": release_api,
            "http_status": release_status,
            "release_id": release.get("id"),
            "tag": RELEASE_TAG,
            "draft": False,
            "prerelease": False,
            "assets": github_assets,
            "total_bytes": EXPECTED_PUBLIC_TOTAL_BYTES,
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
            "total_bytes": EXPECTED_PUBLIC_TOTAL_BYTES,
        },
        "local_release_assets": local_assets,
        "historical_full_byte_receipts": {
            "github": EXPECTED_LOCAL_INPUTS["qa/GITHUB_READER_1.0.0_20260904.json"],
            "zenodo": EXPECTED_LOCAL_INPUTS["qa/ZENODO_READER_1.0.0_20260904.json"],
            "all_seven_assets_http_200_and_sha256_verified": True,
        },
        "checks": [
            "complete_local_release_sha256_recomputed",
            "final_public_backend_member_sha256_recomputed",
            "prior_anonymous_full_byte_receipts_cross_checked",
            "current_public_github_release_inventory_and_sha256_digests",
            "current_open_zenodo_inventory",
            "upstream_commit_and_tree_bound",
            "final_derivative_commit_and_tree_explicitly_unproved",
            "no_credentials",
        ],
        "failures": [],
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(canonical_json_bytes(receipt))
    return receipt


def main() -> int:
    try:
        receipt = verify(DEFAULT_NATIVE, DEFAULT_ADAPTER / "input/public-native-readback.json")
    except (OSError, KeyError, ValueError, zipfile.BadZipFile, urllib.error.URLError) as error:
        print(f"A30 native/public verification failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps({
        "state": receipt["state"],
        "local_assets": len(receipt["local_release_assets"]),
        "github_assets": len(receipt["github_release"]["assets"]),
        "zenodo_assets": len(receipt["zenodo"]["assets"]),
        "total_bytes": receipt["github_release"]["total_bytes"],
        "final_derivative_revision_proved": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
