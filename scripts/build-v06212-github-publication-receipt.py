#!/usr/bin/env python3
"""Build a deterministic receipt for the existing public PMI v0.62.12 GitHub release.

This is deliberately a read-only publication verifier.  It never creates,
edits, uploads, or deletes a GitHub release.  It binds the exact local 100-file
payload to anonymous GitHub API metadata and to a fresh anonymous byte stream
of every public release asset, then atomically writes one sanitized receipt.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, BinaryIO
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


PROJECT = Path(__file__).resolve().parents[1]
RELEASE_DIR = PROJECT / "releases/v0.62.12"
RECEIPT_PATH = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.12.json"
CHECKSUM_NAME = "RELEASE_CHECKSUMS_v0.62.12.sha256"

REPOSITORY_SLUG = "KokunoYumeto/program-matematika-indonesia"
REPOSITORY_URL = f"https://github.com/{REPOSITORY_SLUG}"
TAG = "v0.62.12"
VERSION = "0.62.12"
RELEASE_URL = f"{REPOSITORY_URL}/releases/tag/{TAG}"
LEARNER_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
EXPECTED_TARGET_COMMIT = "590f25ebf033038425b8b84564bc81dd620edb38"
EXPECTED_FILES = 100
EXPECTED_BYTES = 131_739_644
EXPECTED_INVENTORY_AGGREGATE = (
    "3254b566c27819c2230ecf4ef2009879058e6bd41359b3926bd5e3fc36fd7c33"
)
USER_AGENT = "Codex-PMI-v06212-GitHub-Receipt-Builder/1.0"
MAX_WORKERS = 6
MAX_ATTEMPTS = 3


class VerificationError(RuntimeError):
    """A public/local identity or structural boundary did not pass."""


def require(value: bool, message: str) -> None:
    if not value:
        raise VerificationError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_inventory_sha(rows: list[dict[str, Any]]) -> str:
    material = "".join(
        f"{row['sha256']}  {row['name']}\n"
        for row in sorted(rows, key=lambda row: str(row["name"]))
    ).encode("utf-8")
    return sha256_bytes(material)


def anonymous_request(url: str, *, accept: str | None = None) -> Any:
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    return Request(url, headers=headers, method="GET")


def open_bounded(request: Any) -> BinaryIO:
    """Open one anonymous GET with a small bounded transient retry policy."""

    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return urlopen(request, timeout=90)
        except HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 500, 502, 503, 504} or attempt == MAX_ATTEMPTS:
                raise
        except URLError as exc:
            last_error = exc
            if attempt == MAX_ATTEMPTS:
                raise
        time.sleep(float(attempt))
    raise VerificationError(f"unreachable bounded request failure: {last_error}")


def api_json(path_or_url: str) -> Any:
    if path_or_url.startswith("https://"):
        url = path_or_url
    else:
        url = f"https://api.github.com{path_or_url}"
    request = anonymous_request(url, accept="application/vnd.github+json")
    with open_bounded(request) as response:
        require(response.status == 200, f"GitHub API HTTP {response.status}: {url}")
        data = response.read()
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"invalid GitHub API JSON: {url}") from exc


def local_inventory() -> tuple[list[dict[str, Any]], dict[str, Path]]:
    require(RELEASE_DIR.is_dir(), "local v0.62.12 release directory is missing")
    entries = list(RELEASE_DIR.iterdir())
    require(len(entries) == EXPECTED_FILES, "local release is not exactly 100 entries")
    require(
        all(path.is_file() and not path.is_symlink() for path in entries),
        "local release contains a directory or symbolic link",
    )
    paths = {path.name: path for path in entries}
    require(len(paths) == EXPECTED_FILES, "local release filenames are not unique")
    rows: list[dict[str, Any]] = []
    for name in sorted(paths):
        data = paths[name].read_bytes()
        rows.append({"name": name, "bytes": len(data), "sha256": sha256_bytes(data)})
    require(
        sum(int(row["bytes"]) for row in rows) == EXPECTED_BYTES,
        "local release byte total differs",
    )
    require(
        canonical_inventory_sha(rows) == EXPECTED_INVENTORY_AGGREGATE,
        "local release inventory aggregate differs",
    )

    checksum_path = paths.get(CHECKSUM_NAME)
    require(checksum_path is not None, "release checksum manifest is missing")
    lines = checksum_path.read_text(encoding="utf-8").splitlines()
    require(len(lines) == EXPECTED_FILES - 1, "release checksum manifest is not 99 rows")
    parsed: dict[str, str] = {}
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/\\]+)", line)
        require(match is not None, "release checksum manifest syntax differs")
        assert match is not None
        name = match.group(2)
        require(name not in parsed, f"duplicate checksum row: {name}")
        parsed[name] = match.group(1)
    require(
        set(parsed) == set(paths) - {CHECKSUM_NAME},
        "release checksum manifest coverage differs",
    )
    hashes = {str(row["name"]): str(row["sha256"]) for row in rows}
    for name, digest in parsed.items():
        require(digest == hashes[name], f"release checksum mismatch: {name}")
    return rows, paths


def resolve_tag_commit() -> tuple[str, str]:
    encoded = quote(f"tags/{TAG}", safe="/")
    reference = api_json(f"/repos/{REPOSITORY_SLUG}/git/ref/{encoded}")
    target = reference.get("object", {})
    object_type = target.get("type")
    object_sha = target.get("sha")
    require(
        isinstance(object_sha, str) and re.fullmatch(r"[0-9a-f]{40}", object_sha),
        "public tag object lacks a full Git SHA",
    )
    if object_type == "tag":
        annotated = api_json(f"/repos/{REPOSITORY_SLUG}/git/tags/{object_sha}")
        target = annotated.get("object", {})
        object_type = target.get("type")
        object_sha = target.get("sha")
    require(object_type == "commit", "public tag does not resolve to a commit")
    require(object_sha == EXPECTED_TARGET_COMMIT, "public tag target commit differs")
    commit = api_json(f"/repos/{REPOSITORY_SLUG}/git/commits/{object_sha}")
    tree = commit.get("tree", {}).get("sha")
    require(
        isinstance(tree, str) and re.fullmatch(r"[0-9a-f]{40}", tree),
        "public target commit lacks a full tree SHA",
    )
    return object_sha, tree


def public_release() -> tuple[dict[str, Any], list[dict[str, Any]], bool]:
    release = api_json(f"/repos/{REPOSITORY_SLUG}/releases/tags/{quote(TAG, safe='')}")
    require(release.get("html_url") == RELEASE_URL, "public release URL differs")
    require(not release.get("draft"), "public release is a draft")
    require(not release.get("prerelease"), "public release is a prerelease")
    require(release.get("tag_name") == TAG, "public release tag differs")
    require(
        release.get("target_commitish") == EXPECTED_TARGET_COMMIT,
        "release target_commitish differs",
    )
    body = str(release.get("body") or "")
    require(LEARNER_URL in body[:1000], "learner URL is not prominent in release body")

    assets_url = str(release.get("assets_url") or "")
    require(assets_url.startswith("https://api.github.com/"), "release assets URL differs")
    assets = api_json(f"{assets_url}?per_page=100&page=1")
    require(isinstance(assets, list), "release asset response is not a list")
    require(len(assets) == EXPECTED_FILES, "public release is not exactly 100 assets")
    require(
        len({str(asset.get('name')) for asset in assets}) == EXPECTED_FILES,
        "public release asset names are not unique",
    )
    require(
        sum(int(asset.get("size", -1)) for asset in assets) == EXPECTED_BYTES,
        "public release asset byte total differs",
    )
    latest = api_json(f"/repos/{REPOSITORY_SLUG}/releases/latest")
    is_latest = latest.get("id") == release.get("id") and latest.get("tag_name") == TAG
    require(is_latest, "v0.62.12 is not the repository's latest public release")
    return release, assets, is_latest


def readback_one(
    asset: dict[str, Any],
    local: dict[str, Any],
) -> dict[str, Any]:
    name = str(asset.get("name") or "")
    url = str(asset.get("browser_download_url") or "")
    require(url.startswith(f"{REPOSITORY_URL}/releases/download/{TAG}/"), f"asset URL differs: {name}")
    require(int(asset.get("size", -1)) == int(local["bytes"]), f"API size differs: {name}")
    api_digest = asset.get("digest")
    require(api_digest == f"sha256:{local['sha256']}", f"API digest differs: {name}")

    digest = hashlib.sha256()
    byte_count = 0
    request = anonymous_request(url, accept="application/octet-stream")
    with open_bounded(request) as response:
        require(response.status == 200, f"anonymous asset HTTP {response.status}: {name}")
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            byte_count += len(chunk)
    actual_sha = digest.hexdigest()
    require(byte_count == int(local["bytes"]), f"anonymous byte count differs: {name}")
    require(actual_sha == local["sha256"], f"anonymous SHA-256 differs: {name}")
    return {
        "name": name,
        "bytes": byte_count,
        "sha256": actual_sha,
        "api_digest": api_digest,
        "anonymous_http_status": 200,
        "anonymous_byte_identity": True,
        "url": url,
    }


def anonymous_asset_readback(
    assets: list[dict[str, Any]],
    local_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    local = {str(row["name"]): row for row in local_rows}
    remote = {str(asset.get("name")): asset for asset in assets}
    require(set(remote) == set(local), "public and local release filenames differ")
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(readback_one, remote[name], local[name]): name
            for name in sorted(local)
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                raise VerificationError(f"anonymous readback failed for {name}: {exc}") from exc
    results.sort(key=lambda row: str(row["name"]))
    require(len(results) == EXPECTED_FILES, "anonymous readback count differs")
    require(
        sum(int(row["bytes"]) for row in results) == EXPECTED_BYTES,
        "anonymous readback byte total differs",
    )
    require(
        canonical_inventory_sha(results) == EXPECTED_INVENTORY_AGGREGATE,
        "anonymous readback inventory aggregate differs",
    )
    return results


def build_receipt() -> dict[str, Any]:
    local_rows, _ = local_inventory()
    source_commit, source_tree = resolve_tag_commit()
    release, assets, is_latest = public_release()
    readback = anonymous_asset_readback(assets, local_rows)
    builder = Path(__file__).resolve()
    builder_bytes = builder.read_bytes()
    release_body = str(release.get("body") or "").encode("utf-8")
    return {
        "schema_id": "program-matematika-indonesia/github-publication-receipt/1.1.0",
        "version": VERSION,
        "tag": TAG,
        "state": "published_public_verified",
        "repository": REPOSITORY_URL,
        "repository_public": True,
        "learner_primary_url": LEARNER_URL,
        "machine_backend_is_secondary": True,
        "overall_program_complete": False,
        "model_provenance": "OpenAI Codex gpt-5.6-sol, Ultra",
        "source": {
            "commit": source_commit,
            "tree": source_tree,
            "tag_resolves_to_commit": True,
        },
        "release": {
            "id": int(release["id"]),
            "url": str(release["html_url"]),
            "name": str(release.get("name") or ""),
            "tag_target_commit": source_commit,
            "created_at": str(release.get("created_at") or ""),
            "published_at": str(release.get("published_at") or ""),
            "draft": False,
            "prerelease": False,
            "latest": is_latest,
            "created_in_this_execution": False,
            "body_sha256": sha256_bytes(release_body),
            "anonymous_repository_url": REPOSITORY_URL,
            "anonymous_expanded_assets_url": f"{REPOSITORY_URL}/releases/expanded_assets/{TAG}",
            "anonymous_expanded_assets_count": EXPECTED_FILES,
        },
        "inventory": {
            "files": EXPECTED_FILES,
            "bytes": EXPECTED_BYTES,
            "aggregate_sha256": EXPECTED_INVENTORY_AGGREGATE,
            "checksum_manifest": {
                "name": CHECKSUM_NAME,
                "rows": EXPECTED_FILES - 1,
                "bytes": next(row["bytes"] for row in local_rows if row["name"] == CHECKSUM_NAME),
                "sha256": next(row["sha256"] for row in local_rows if row["name"] == CHECKSUM_NAME),
                "coverage": "all_release_files_except_self",
            },
        },
        "anonymous_asset_readback": {
            "result": "pass_100_of_100",
            "files": EXPECTED_FILES,
            "bytes": EXPECTED_BYTES,
            "aggregate_sha256": EXPECTED_INVENTORY_AGGREGATE,
            "entries": readback,
        },
        "builder": {
            "path": builder.relative_to(PROJECT).as_posix(),
            "bytes": len(builder_bytes),
            "sha256": sha256_bytes(builder_bytes),
            "network_authorization": "anonymous_read_only",
            "release_mutation_calls": 0,
            "git_commands_used": 0,
            "determinism": "stable_public_metadata_and_sorted_exact_byte_inventory",
        },
        "privacy": {
            "absolute_profile_paths_recorded": False,
            "credential_locator_recorded": False,
            "credentials_recorded": False,
            "personal_name_recorded": False,
        },
    }


def atomic_write_receipt(receipt: dict[str, Any]) -> None:
    encoded = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    lowered = encoded.lower()
    require(b"c:\\users\\" not in lowered, "receipt contains an absolute profile path")
    require(b"authorization: bearer" not in lowered, "receipt contains an authorization header")
    require(b"access_token=" not in lowered, "receipt contains a credential query")
    require(
        re.search(rb"(?:github_pat_[a-z0-9_]{20,}|ghp_[a-z0-9]{20,})", lowered) is None,
        "receipt contains a credential-shaped value",
    )
    handle, temp_name = tempfile.mkstemp(prefix=".v06212-github-receipt-", suffix=".json", dir=PROJECT)
    temp = Path(temp_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        parsed = json.loads(temp.read_text(encoding="utf-8"))
        require(parsed == receipt, "temporary receipt JSON readback differs")
        os.replace(temp, RECEIPT_PATH)
    finally:
        if temp.exists():
            temp.unlink()


def main() -> int:
    try:
        receipt = build_receipt()
        atomic_write_receipt(receipt)
        data = RECEIPT_PATH.read_bytes()
        parsed = json.loads(data.decode("utf-8"))
        require(parsed == receipt, "final receipt JSON readback differs")
        print(
            json.dumps(
                {
                    "status": "PASS_PUBLIC_ANONYMOUS_READBACK_100_OF_100",
                    "release": RELEASE_URL,
                    "source_commit": receipt["source"]["commit"],
                    "source_tree": receipt["source"]["tree"],
                    "files": EXPECTED_FILES,
                    "bytes": EXPECTED_BYTES,
                    "inventory_aggregate_sha256": EXPECTED_INVENTORY_AGGREGATE,
                    "receipt": RECEIPT_PATH.relative_to(PROJECT).as_posix(),
                    "receipt_bytes": len(data),
                    "receipt_sha256": sha256_bytes(data),
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    except (VerificationError, HTTPError, URLError, OSError) as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(
            json.dumps(
                {"status": "FAIL_CLOSED", "version": VERSION, "error": detail},
                sort_keys=True,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
