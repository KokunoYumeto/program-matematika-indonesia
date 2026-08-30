#!/usr/bin/env python3
"""Commit the bounded v0.62.8 source set and publish its exact release assets.

This script uses the GitHub API only; it never invokes Git.  Credential values
are read at runtime, never printed, serialized, or placed in URLs.
"""

from __future__ import annotations

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import time
from typing import Any
from urllib.parse import quote

import requests


PROJECT = Path(__file__).resolve().parents[1]
OWNER = "KokunoYumeto"
REPOSITORY = "program-matematika-indonesia"
API = f"https://api.github.com/repos/{OWNER}/{REPOSITORY}"
RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPOSITORY}"
VERSION = "0.62.8"
TAG = f"v{VERSION}"
PREDECESSOR_VERSION = "0.62.7"
EXPECTED_RELEASE_FILES = 103
EXPECTED_PREDECESSOR_FILES = 98
EXPECTED_ADDITIVE_FILES = 5
EXPECTED_BASE_AGGREGATE = "9e124bbbe4aa82ef85ce90a2409fc1eb1f90766addea8e084097848de9ebfdda"
EXPECTED_ADDITIVE_NAMES = {
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.8.html",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.8.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.8.zip",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.8.json",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.8.sha256",
}
USER_AGENT = f"program-matematika-indonesia-github-publisher/{VERSION}"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fact(path: Path, name: str | None = None) -> dict[str, Any]:
    return {"name": name or path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def inventory_aggregate(rows: list[dict[str, Any]]) -> str:
    payload = "".join(
        f"{row['sha256']}  {row['bytes']}  {row['name']}\n"
        for row in sorted(rows, key=lambda item: item["name"])
    ).encode("utf-8")
    return sha256_bytes(payload)


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def token_candidates(path: Path) -> list[str]:
    require(path.is_file(), "GitHub credential file is unavailable")
    text = path.read_text(encoding="utf-8-sig")
    labelled = re.findall(
        r"(?im)^\s*(?:github\s+)?(?:access\s+)?token\s*[:=]\s*[`\"']?([A-Za-z0-9_\-.]{32,})",
        text,
    )
    shaped = re.findall(r"(?:github_pat_[A-Za-z0-9_]{40,}|gh[opusr]_[A-Za-z0-9]{32,})", text)
    compact = text.strip().strip("`\"'")
    values = [*labelled, *shaped]
    if compact and not re.search(r"\s", compact) and len(compact) >= 32:
        values.append(compact)
    unique: list[str] = []
    for value in values:
        value = value.strip("`\"' \t\r\n")
        if value and value not in unique:
            unique.append(value)
    require(bool(unique), "GitHub credential file contains no token candidate")
    return unique


def select_session(path: Path) -> requests.Session:
    for candidate in token_candidates(path):
        session = requests.Session()
        session.headers.update(
            {
                "Authorization": f"Bearer {candidate}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": USER_AGENT,
            }
        )
        try:
            response = session.get("https://api.github.com/user", timeout=30)
        except requests.RequestException:
            continue
        if response.status_code == 200 and response.json().get("login") == OWNER:
            return session
        session.close()
    raise RuntimeError("no GitHub credential candidate authenticates as the repository owner")


def api_json(
    session: requests.Session,
    method: str,
    url: str,
    *,
    expected: set[int],
    json_body: Any | None = None,
    timeout: int = 120,
) -> tuple[int, dict[str, Any]]:
    response: requests.Response | None = None
    for attempt in range(7):
        response = session.request(method, url, json=json_body, timeout=timeout)
        if response.status_code not in {429, 500, 502, 503, 504}:
            break
        time.sleep(min(2**attempt, 20))
    assert response is not None
    if response.status_code not in expected:
        raise RuntimeError(f"GitHub API {method} failed with HTTP {response.status_code}")
    if not response.content:
        return response.status_code, {}
    return response.status_code, response.json()


def bounded_paths(values: list[str]) -> list[tuple[str, Path]]:
    require(bool(values), "at least one --path is required")
    rows: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for value in values:
        logical = PurePosixPath(value).as_posix()
        require(not logical.startswith("/") and ".." not in PurePosixPath(logical).parts, f"unsafe path: {value}")
        require(logical not in seen, f"duplicate path: {logical}")
        local = (PROJECT / Path(*PurePosixPath(logical).parts)).resolve()
        require(local.is_relative_to(PROJECT) and local.is_file(), f"missing bounded source: {logical}")
        seen.add(logical)
        rows.append((logical, local))
    return sorted(rows)


def raw_readback(commit: str, logical: str, expected: bytes) -> None:
    url = f"{RAW}/{commit}/{quote(logical, safe='/')}?readback={sha256_bytes(expected)}"
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=120)
    require(response.status_code == 200, f"raw commit readback failed: {logical}")
    require(response.content == expected, f"raw commit byte mismatch: {logical}")


def commit_source(args: argparse.Namespace) -> None:
    paths = bounded_paths(args.path)
    session = select_session(args.token_file.resolve())
    _, ref = api_json(session, "GET", f"{API}/git/ref/heads/main", expected={200})
    parent = str(ref["object"]["sha"])
    require(re.fullmatch(r"[0-9a-f]{40}", parent) is not None, "main head is malformed")
    _, parent_commit = api_json(session, "GET", f"{API}/git/commits/{parent}", expected={200})
    base_tree = str(parent_commit["tree"]["sha"])

    tree_rows = []
    source_facts = []
    source_bytes: dict[str, bytes] = {}
    for logical, local in paths:
        data = local.read_bytes()
        source_bytes[logical] = data
        source_facts.append({"name": logical, "bytes": len(data), "sha256": sha256_bytes(data)})
        _, blob = api_json(
            session,
            "POST",
            f"{API}/git/blobs",
            expected={201},
            json_body={"content": base64.b64encode(data).decode("ascii"), "encoding": "base64"},
        )
        tree_rows.append({"path": logical, "mode": "100644", "type": "blob", "sha": blob["sha"]})

    _, tree = api_json(
        session,
        "POST",
        f"{API}/git/trees",
        expected={201},
        json_body={"base_tree": base_tree, "tree": tree_rows},
    )
    _, commit = api_json(
        session,
        "POST",
        f"{API}/git/commits",
        expected={201},
        json_body={"message": args.message, "tree": tree["sha"], "parents": [parent]},
    )
    commit_sha = str(commit["sha"])
    api_json(
        session,
        "PATCH",
        f"{API}/git/refs/heads/main",
        expected={200},
        json_body={"sha": commit_sha, "force": False},
    )
    _, final_ref = api_json(session, "GET", f"{API}/git/ref/heads/main", expected={200})
    require(final_ref["object"]["sha"] == commit_sha, "main did not resolve to the source commit")
    with ThreadPoolExecutor(max_workers=min(8, len(paths))) as pool:
        futures = [pool.submit(raw_readback, commit_sha, name, source_bytes[name]) for name, _ in paths]
        for future in futures:
            future.result()

    receipt = {
        "schema_id": "program-matematika-indonesia/github-source-commit-receipt/v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": "committed_and_raw_bytes_verified",
        "repository": f"https://github.com/{OWNER}/{REPOSITORY}",
        "branch": "main",
        "parent_commit": parent,
        "commit": commit_sha,
        "commit_url": f"https://github.com/{OWNER}/{REPOSITORY}/commit/{commit_sha}",
        "files": source_facts,
        "credential_recorded": False,
        "git_commands_used": 0,
    }
    write_json(args.receipt.resolve(), receipt)
    print(json.dumps({"result": receipt["result"], "commit": commit_sha, "files": len(paths), "receipt": str(args.receipt)}, sort_keys=True))


def wait_pages(args: argparse.Namespace) -> None:
    require(re.fullmatch(r"[0-9a-f]{40}", args.source_commit) is not None, "--source-commit must be full lowercase SHA")
    session = select_session(args.token_file.resolve())
    deadline = time.monotonic() + args.timeout_seconds
    successful: dict[str, Any] | None = None
    last_states: list[str] = []
    while time.monotonic() < deadline:
        _, payload = api_json(
            session,
            "GET",
            f"{API}/actions/runs?head_sha={args.source_commit}&per_page=100",
            expected={200},
        )
        candidates = [
            run
            for run in payload.get("workflow_runs", [])
            if run.get("head_sha") == args.source_commit
            and (
                "pages" in str(run.get("name", "")).lower()
                or "pages" in str(run.get("path", "")).lower()
                or "static" in str(run.get("name", "")).lower()
            )
        ]
        last_states = [f"{run.get('name')}:{run.get('status')}:{run.get('conclusion')}" for run in candidates]
        successful = next((run for run in candidates if run.get("status") == "completed" and run.get("conclusion") == "success"), None)
        if successful is not None:
            break
        failed = [run for run in candidates if run.get("status") == "completed" and run.get("conclusion") not in {None, "success"}]
        require(not failed, "Pages workflow completed unsuccessfully")
        time.sleep(10)
    require(successful is not None, f"no successful Pages workflow before timeout; states={last_states}")

    pages = (
        ("docs/index.html", "https://kokunoyumeto.github.io/program-matematika-indonesia/"),
        ("docs/app.js", "https://kokunoyumeto.github.io/program-matematika-indonesia/app.js"),
        ("docs/live-course-publications.js", "https://kokunoyumeto.github.io/program-matematika-indonesia/live-course-publications.js"),
        ("docs/id-ID/courses/D30/index.html", "https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/D30/"),
        ("docs/id-ID/courses/B95/index.html", "https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/B95/"),
    )
    readbacks = []
    for logical, url in pages:
        local = (PROJECT / logical).read_bytes()
        matched = False
        for attempt in range(12):
            response = requests.get(
                f"{url}?pmi-pages-readback={args.source_commit}-{attempt}",
                headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"},
                timeout=60,
            )
            if response.status_code == 200 and response.content == local:
                matched = True
                break
            time.sleep(5)
        require(matched, f"Pages bytes did not converge: {logical}")
        readbacks.append({"path": logical, "url": url, "bytes": len(local), "sha256": sha256_bytes(local), "http_status": 200})
    receipt = {
        "schema_id": "program-matematika-indonesia/github-pages-readback-receipt/v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": "workflow_success_and_five_exact_readbacks",
        "source_commit": args.source_commit,
        "workflow_run_id": int(successful["id"]),
        "workflow_run_url": successful["html_url"],
        "readbacks": readbacks,
        "credential_recorded": False,
        "git_commands_used": 0,
    }
    write_json(args.receipt.resolve(), receipt)
    print(json.dumps({"result": receipt["result"], "workflow_run_id": receipt["workflow_run_id"], "readbacks": len(readbacks), "receipt": str(args.receipt)}, sort_keys=True))


def release_facts(release_dir: Path) -> list[dict[str, Any]]:
    require(release_dir.is_dir(), "release directory is unavailable")
    paths = sorted(release_dir.iterdir(), key=lambda path: path.name)
    require(
        len(paths) == EXPECTED_RELEASE_FILES and all(path.is_file() for path in paths),
        "release is not an exact 103-file flat directory",
    )
    rows = [fact(path) | {"path": path} for path in paths]
    checksums = release_dir / f"LIVE_OVERLAY_CHECKSUMS_v{VERSION}.sha256"
    require(checksums.is_file(), "release checksum file is absent")
    expected = {}
    for line in checksums.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\\/]+)", line)
        require(match is not None, "release checksum syntax differs")
        digest, name = match.groups()
        require(name not in expected, "duplicate checksum entry")
        expected[name] = digest
    require(len(expected) == EXPECTED_RELEASE_FILES - 1, "release checksum entry count differs")
    for row in rows:
        if row["name"] != checksums.name:
            require(expected.get(row["name"]) == row["sha256"], f"release checksum mismatch: {row['name']}")
    return rows


def upload_asset(session: requests.Session, upload_url: str, row: dict[str, Any]) -> dict[str, Any]:
    name = row["name"]
    with row["path"].open("rb") as stream:
        response = session.post(
            upload_url,
            params={"name": name},
            headers={"Content-Type": "application/octet-stream"},
            data=stream,
            timeout=1800,
        )
    require(response.status_code == 201, f"GitHub release upload failed: {name} -> HTTP {response.status_code}")
    return response.json()


def anonymous_asset(row: dict[str, Any], remote: dict[str, Any]) -> dict[str, Any]:
    url = str(remote["browser_download_url"])
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, stream=True, timeout=120)
    require(response.status_code == 200, f"anonymous asset readback failed: {row['name']}")
    digest = hashlib.sha256()
    count = 0
    for chunk in response.iter_content(1024 * 1024):
        if chunk:
            digest.update(chunk)
            count += len(chunk)
    require(count == row["bytes"] and digest.hexdigest() == row["sha256"], f"anonymous asset mismatch: {row['name']}")
    return {"name": row["name"], "bytes": count, "sha256": digest.hexdigest(), "url": url}


def publish_release(args: argparse.Namespace) -> None:
    require(re.fullmatch(r"[0-9a-f]{40}", args.source_commit) is not None, "--source-commit must be full lowercase SHA")
    release_dir = args.release_dir.resolve()
    require(
        release_dir == (PROJECT / "releases" / f"v{VERSION}").resolve(),
        "release directory must be releases/v0.62.8",
    )
    rows = release_facts(release_dir)
    by_name = {row["name"]: row for row in rows}
    base_dir = (PROJECT / "releases" / f"v{PREDECESSOR_VERSION}").resolve()
    base_rows = [fact(path) for path in sorted(base_dir.iterdir(), key=lambda path: path.name)]
    require(len(base_rows) == EXPECTED_PREDECESSOR_FILES, "predecessor file count differs")
    require(inventory_aggregate(base_rows) == EXPECTED_BASE_AGGREGATE, "predecessor aggregate differs")
    require(
        set(by_name) - {row["name"] for row in base_rows} == EXPECTED_ADDITIVE_NAMES,
        "successor additive inventory differs",
    )
    for row in base_rows:
        require(by_name[row["name"]]["bytes"] == row["bytes"] and by_name[row["name"]]["sha256"] == row["sha256"], f"inherited byte changed: {row['name']}")

    session = select_session(args.token_file.resolve())
    status, release = api_json(session, "GET", f"{API}/releases/tags/{TAG}", expected={200, 404})
    if status == 404:
        _, release = api_json(
            session,
            "POST",
            f"{API}/releases",
            expected={201},
            json_body={
                "tag_name": TAG,
                "target_commitish": args.source_commit,
                "name": f"Program Matematika Indonesia {TAG}",
                "body": (
                    "Penerus aditif v0.62.8: hub siswa kini mengarahkan D80 ke pembaca HTML daring yang telah "
                    "divalidasi dengan 27.308 formula dan nol kesalahan MathJax, sambil mempertahankan PDF 864 halaman "
                    "sebagai edisi unduhan. ZIP HTML luring Zenodo lama tidak ditawarkan sebagai rute siswa sampai "
                    "versi yang telah diperbaiki terbit. Seluruh 98 aset v0.62.7 dipertahankan byte-for-byte; "
                    "program keseluruhan masih dalam produksi."
                ),
                "draft": False,
                "prerelease": False,
            },
        )
    require(release.get("tag_name") == TAG and not release.get("draft"), "GitHub release state differs")
    upload_url = str(release["upload_url"]).split("{", 1)[0]
    existing = {str(asset["name"]): asset for asset in release.get("assets", [])}
    require(not (set(existing) - set(by_name)), "GitHub release contains an out-of-scope asset")
    for name, asset in existing.items():
        require(int(asset.get("size", -1)) == by_name[name]["bytes"], f"existing GitHub asset size differs: {name}")
    for row in rows:
        if row["name"] not in existing:
            existing[row["name"]] = upload_asset(session, upload_url, row)

    _, release = api_json(session, "GET", f"{API}/releases/tags/{TAG}", expected={200})
    assets = {str(asset["name"]): asset for asset in release.get("assets", [])}
    require(set(assets) == set(by_name) and len(assets) == EXPECTED_RELEASE_FILES, "GitHub release inventory differs")
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(anonymous_asset, by_name[name], assets[name]) for name in sorted(by_name)]
        verified = [future.result() for future in futures]

    compact_rows = [{key: row[key] for key in ("name", "bytes", "sha256")} for row in rows]
    receipt = {
        "schema_id": "program-matematika-indonesia/github-publication-receipt/v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": "published_and_anonymously_verified",
        "version": VERSION,
        "repository": f"https://github.com/{OWNER}/{REPOSITORY}",
        "release": str(release["html_url"]),
        "release_id": int(release["id"]),
        "tag": TAG,
        "target_commit": args.source_commit,
        "files": len(rows),
        "bytes": sum(row["bytes"] for row in rows),
        "aggregate_sha256": inventory_aggregate(compact_rows),
        "inherited_files": EXPECTED_PREDECESSOR_FILES,
        "additive_files": EXPECTED_ADDITIVE_FILES,
        "anonymous_assets_verified": len(verified),
        "anonymous_mismatches": 0,
        "inventory": compact_rows,
        "credential_recorded": False,
        "git_commands_used": 0,
    }
    write_json(args.receipt.resolve(), receipt)
    print(json.dumps({"result": receipt["result"], "release": receipt["release"], "files": len(rows), "bytes": receipt["bytes"], "aggregate_sha256": receipt["aggregate_sha256"]}, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    commit = sub.add_parser("commit-source")
    commit.add_argument("--token-file", required=True, type=Path)
    commit.add_argument("--path", action="append", required=True)
    commit.add_argument("--message", default="Publish corrected D80 learner route and v0.62.8 release tooling")
    commit.add_argument("--receipt", type=Path, default=PROJECT / f"GITHUB_SOURCE_COMMIT_RECEIPT_v{VERSION}.json")
    pages = sub.add_parser("wait-pages")
    pages.add_argument("--token-file", required=True, type=Path)
    pages.add_argument("--source-commit", required=True)
    pages.add_argument("--timeout-seconds", type=int, default=900)
    pages.add_argument("--receipt", type=Path, default=PROJECT / f"GITHUB_PAGES_READBACK_RECEIPT_v{VERSION}.json")
    release = sub.add_parser("publish-release")
    release.add_argument("--token-file", required=True, type=Path)
    release.add_argument("--source-commit", required=True)
    release.add_argument("--release-dir", type=Path, default=PROJECT / "releases" / f"v{VERSION}")
    release.add_argument("--receipt", type=Path, default=PROJECT / f"GITHUB_PUBLICATION_RECEIPT_v{VERSION}.json")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.command == "commit-source":
        commit_source(arguments)
    elif arguments.command == "wait-pages":
        wait_pages(arguments)
    else:
        publish_release(arguments)
