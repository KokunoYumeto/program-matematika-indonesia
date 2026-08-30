#!/usr/bin/env python3
"""Publish the exact admitted B10 v2.3.1 adapter source delta without a Git worktree scan."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OWNER = "KokunoYumeto"
REPO_NAME = "program-matematika-indonesia"
REPO = f"{OWNER}/{REPO_NAME}"
API = "https://api.github.com"
TOKEN_FILE_ENV = "B10_GITHUB_TOKEN_FILE"
RECEIPT = ROOT / "GITHUB_B10_V231_SOURCE_PUBLICATION_RECEIPT.json"
USER_AGENT = "Codex-B10-v231-Source-Publisher/1.0"
COMMIT_MESSAGE = "Admit the corpus-neutral B10 backend v2.3.1 adapter"

GENERIC_SCHEMAS = [
    "lane-adapter-v2.3.1.schema.json",
    "capability-declarations-v0.2.schema.json",
    "namespace-crosswalk-v0.2.schema.json",
    "translation-state-index-v0.2.schema.json",
    "csv-projection-manifest-v0.2.schema.json",
    "scope-declaration-v0.2.schema.json",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def request(
    url: str,
    *,
    token: str | None = None,
    method: str = "GET",
    data: bytes | None = None,
    expected: tuple[int, ...] = (200,),
    accept: str = "application/vnd.github+json",
) -> tuple[int, bytes, dict[str, str]]:
    headers = {
        "Accept": accept,
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        headers["Content-Type"] = "application/json"
        headers["Content-Length"] = str(len(data))
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=180, context=ssl.create_default_context()) as response:
                status, body, response_headers = response.status, response.read(), dict(response.headers.items())
        except urllib.error.HTTPError as exc:
            status, body = exc.code, exc.read()
            response_headers = dict(exc.headers.items()) if exc.headers else {}
        except (TimeoutError, urllib.error.URLError) as exc:
            if attempt == 5:
                raise RuntimeError(f"network failure for {method} {url}: {exc}") from exc
            time.sleep(2 * (attempt + 1))
            continue
        if status in (429, 502, 503, 504) and attempt < 5:
            time.sleep(2 * (attempt + 1))
            continue
        if status not in expected:
            raise RuntimeError(f"HTTP {status} for {method} {url}: {body.decode('utf-8', errors='replace')[:800]}")
        return status, body, response_headers
    raise RuntimeError(f"request retry budget exhausted: {method} {url}")


def api(path: str, token: str, *, method: str = "GET", payload: object | None = None, expected: tuple[int, ...] = (200,)):
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
    status, body, _ = request(API + path, token=token, method=method, data=data, expected=expected)
    return status, json.loads(body.decode("utf-8")) if body else None


def load_token() -> str:
    token_file_value = os.environ.get(TOKEN_FILE_ENV)
    if not token_file_value:
        raise RuntimeError(f"{TOKEN_FILE_ENV} is required")
    token_file = Path(token_file_value)
    if not token_file.is_file():
        raise RuntimeError("configured GitHub credential file does not exist")
    text = token_file.read_text(encoding="utf-8")
    candidates: list[str] = []
    for pattern in (r"github_pat_[A-Za-z0-9_]+", r"ghp_[A-Za-z0-9]{20,}"):
        candidates.extend(re.findall(pattern, text))
    for candidate in dict.fromkeys(candidates):
        status, body, _ = request(f"{API}/user", token=candidate, expected=(200, 401, 403))
        if status == 200 and json.loads(body.decode("utf-8")).get("login", "").casefold() == OWNER.casefold():
            return candidate
    raise RuntimeError("no working credential for the exact public repository owner")


def source_files() -> dict[str, Path]:
    files: dict[str, Path] = {
        "README.md": ROOT / "README.md",
        "scripts/sync-public-schemas.mjs": ROOT / "scripts/sync-public-schemas.mjs",
        "scripts/publish-b10-v231-source.py": Path(__file__).resolve(),
        "backend/v2.3/README.md": ROOT / "backend/v2.3/README.md",
        "backend/v2.3/authorities/B10_COURSE_ROOT_ANONYMOUS_READBACK_20260830.json": ROOT / "backend/v2.3/authorities/B10_COURSE_ROOT_ANONYMOUS_READBACK_20260830.json",
        "backend/v2.3/scripts/build_b10_v23_adapter.py": ROOT / "backend/v2.3/scripts/build_b10_v23_adapter.py",
        "backend/v2.3/scripts/validate_b10_v23_adapter.py": ROOT / "backend/v2.3/scripts/validate_b10_v23_adapter.py",
        "backend/v2.3/scripts/package_b10_v231_adapter.py": ROOT / "backend/v2.3/scripts/package_b10_v231_adapter.py",
        "docs/schema/v2.3/index.html": ROOT / "docs/schema/v2.3/index.html",
    }
    for name in GENERIC_SCHEMAS:
        files[f"backend/v2.3/schema/{name}"] = ROOT / "backend/v2.3/schema" / name
        files[f"docs/schema/v2.3/{name}"] = ROOT / "docs/schema/v2.3" / name
    extension = ROOT / "backend/v2.3/extensions/b10-dmoi-v0.2.0"
    for path in sorted(item for item in extension.rglob("*") if item.is_file()):
        relative = path.relative_to(ROOT).as_posix()
        files[relative] = path
    if len([path for path in files if path.startswith("backend/v2.3/extensions/b10-dmoi-v0.2.0/")]) != 57:
        raise RuntimeError("canonical extension file count is not 57")
    for remote_path, local_path in files.items():
        if not local_path.is_file():
            raise RuntimeError(f"missing bounded publication source: {remote_path}")
    return dict(sorted(files.items()))


def snapshot_files(files: dict[str, Path]) -> dict[str, bytes]:
    """Read the bounded source set once; these immutable bytes are the publication authority."""
    return {remote_path: local_path.read_bytes() for remote_path, local_path in files.items()}


def verify_snapshot_current(files: dict[str, Path], snapshot: dict[str, bytes], *, phase: str) -> None:
    changed = [
        remote_path
        for remote_path, local_path in files.items()
        if not local_path.is_file() or local_path.read_bytes() != snapshot[remote_path]
    ]
    if changed:
        preview = ", ".join(changed[:8])
        suffix = "" if len(changed) <= 8 else f" (+{len(changed) - 8} more)"
        raise RuntimeError(f"bounded source snapshot changed during {phase}: {preview}{suffix}")


def create_blob(token: str, data: bytes) -> str:
    _, result = api(
        f"/repos/{REPO}/git/blobs",
        token,
        method="POST",
        payload={"content": base64.b64encode(data).decode("ascii"), "encoding": "base64"},
        expected=(201,),
    )
    return result["sha"]


def publish_source(
    token: str,
    paths: dict[str, Path],
    snapshot: dict[str, bytes],
) -> tuple[str, str, str, list[dict[str, object]], bool]:
    _, ref = api(f"/repos/{REPO}/git/ref/heads/main", token)
    parent = ref["object"]["sha"]
    _, parent_commit = api(f"/repos/{REPO}/git/commits/{parent}", token)
    base_tree = parent_commit["tree"]["sha"]
    _, recursive_tree = api(f"/repos/{REPO}/git/trees/{base_tree}?recursive=1", token)
    if recursive_tree.get("truncated"):
        raise RuntimeError("GitHub returned a truncated base tree; refusing a partial comparison")
    remote_blobs = {row["path"]: row["sha"] for row in recursive_tree.get("tree", []) if row.get("type") == "blob"}

    facts: list[dict[str, object]] = []
    changed: list[tuple[str, bytes]] = []
    for remote_path, data in snapshot.items():
        blob = git_blob_sha(data)
        facts.append({"path": remote_path, "bytes": len(data), "sha256": sha256(data), "git_blob_sha1": blob})
        if remote_blobs.get(remote_path) != blob:
            changed.append((remote_path, data))
    if not changed:
        verify_snapshot_current(paths, snapshot, phase="final no-op publication check")
        return parent, base_tree, parent, facts, False

    # The validator ran against the same bytes and every API call above was read-only.
    # Fail closed before the first GitHub mutation if any bounded local source changed.
    verify_snapshot_current(paths, snapshot, phase="pre-mutation publication check")
    entries = [
        {"path": remote_path, "mode": "100644", "type": "blob", "sha": create_blob(token, data)}
        for remote_path, data in changed
    ]
    _, new_tree = api(
        f"/repos/{REPO}/git/trees",
        token,
        method="POST",
        payload={"base_tree": base_tree, "tree": entries},
        expected=(201,),
    )
    _, new_commit = api(
        f"/repos/{REPO}/git/commits",
        token,
        method="POST",
        payload={"message": COMMIT_MESSAGE, "tree": new_tree["sha"], "parents": [parent]},
        expected=(201,),
    )
    api(
        f"/repos/{REPO}/git/refs/heads/main",
        token,
        method="PATCH",
        payload={"sha": new_commit["sha"], "force": False},
    )
    return new_commit["sha"], new_tree["sha"], parent, facts, True


def wait_for_pages(token: str, commit_sha: str, changed: bool) -> dict[str, object]:
    if not changed:
        return {"status": "not_required_existing_exact_commit", "conclusion": "success", "run_id": None, "url": None}
    matched = None
    for _ in range(60):
        _, runs = api(f"/repos/{REPO}/actions/runs?branch=main&per_page=30", token)
        matched = next(
            (
                run
                for run in runs.get("workflow_runs", [])
                if run.get("head_sha") == commit_sha
                and run.get("path") == "dynamic/pages/pages-build-deployment"
                and run.get("event") == "dynamic"
                and run.get("head_branch") == "main"
            ),
            None,
        )
        if matched and matched.get("status") == "completed":
            if matched.get("conclusion") != "success":
                raise RuntimeError(f"Pages workflow failed: {matched.get('html_url')}")
            return {
                "status": matched["status"],
                "conclusion": matched["conclusion"],
                "run_id": matched["id"],
                "url": matched["html_url"],
            }
        time.sleep(10)
    raise RuntimeError(f"Pages workflow did not complete for commit {commit_sha}; last={matched}")


def retry_exact(url: str, expected: bytes, attempts: int = 36) -> bytes:
    last = b""
    for _ in range(attempts):
        try:
            status, body, _ = request(url, expected=(200, 404), accept="application/octet-stream")
            if status == 200 and body == expected:
                return body
            last = body
        except Exception:
            pass
        time.sleep(5)
    raise RuntimeError(f"public byte readback mismatch: {url}; observed_bytes={len(last)} expected_bytes={len(expected)}")


def anonymous_readback(commit_sha: str, snapshot: dict[str, bytes]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    raw_checks: list[dict[str, object]] = []
    for remote_path, expected in snapshot.items():
        url = f"https://raw.githubusercontent.com/{REPO}/{commit_sha}/{urllib.parse.quote(remote_path, safe='/')}"
        body = retry_exact(url, expected, attempts=8)
        raw_checks.append({"path": remote_path, "url": url, "bytes": len(body), "sha256": sha256(body)})

    page_sources = ["docs/schema/v2.3/index.html"] + [f"docs/schema/v2.3/{name}" for name in GENERIC_SCHEMAS]
    pages_checks: list[dict[str, object]] = []
    pages_base = f"https://{OWNER.lower()}.github.io/{REPO_NAME}/schema/v2.3/"
    for source_path in page_sources:
        expected = snapshot[source_path]
        page_name = "" if source_path.endswith("index.html") else source_path.rsplit("/", 1)[1]
        url = pages_base + page_name
        body = retry_exact(url, expected)
        pages_checks.append({"source_path": source_path, "url": url, "bytes": len(body), "sha256": sha256(body)})
    return raw_checks, pages_checks


def run_static_validation() -> dict[str, object]:
    validator_env = os.environ.copy()
    validator_env.pop(TOKEN_FILE_ENV, None)
    try:
        completed = subprocess.run(
            ["node", "scripts/validate-static-site.mjs"],
            cwd=ROOT,
            env=validator_env,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"static validation failed with exit code {exc.returncode}") from None
    result = json.loads(completed.stdout)
    if result.get("status") != "pass" or result.get("courses") != 40 or result.get("selected") != 40:
        raise RuntimeError("static validation did not preserve the 40-role closure")
    receipt_fields = (
        "status",
        "version",
        "zenodo",
        "courses",
        "selected",
        "unresolved",
        "publishedCanonRoles",
        "effectivePublishedRoles",
        "liveOverlayRows",
        "completedPublicCourseRoles",
        "completedPublicRecords",
        "publishedHtmlReaders",
        "prerequisiteEdges",
        "federationV2Records",
        "publicReadbackOverlays",
        "topics",
        "levelCounts",
    )
    return {name: result[name] for name in receipt_fields}


def main() -> None:
    paths = source_files()
    snapshot = snapshot_files(paths)
    static_validation = run_static_validation()
    verify_snapshot_current(paths, snapshot, phase="post-validation check")
    token = load_token()
    _, repo = api(f"/repos/{REPO}", token)
    if repo.get("private") or repo.get("full_name", "").casefold() != REPO.casefold():
        raise RuntimeError("destination is not the expected public repository")
    commit_sha, tree_sha, parent_sha, facts, changed = publish_source(token, paths, snapshot)
    _, live_ref = api(f"/repos/{REPO}/git/ref/heads/main", token)
    if live_ref["object"]["sha"] != commit_sha:
        raise RuntimeError("main ref did not retain the published source commit")
    workflow = wait_for_pages(token, commit_sha, changed)
    raw_checks, pages_checks = anonymous_readback(commit_sha, snapshot)
    receipt = {
        "schema_id": "program-matematika-indonesia/github-b10-v231-source-publication/1.0.0",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass",
        "repository": f"https://github.com/{REPO}",
        "branch": "main",
        "parent_commit": parent_sha,
        "source_commit": commit_sha,
        "source_tree": tree_sha,
        "commit_created": changed,
        "commit_message": COMMIT_MESSAGE if changed else "existing exact source commit",
        "bounded_file_count": len(facts),
        "bounded_file_bytes": sum(int(row["bytes"]) for row in facts),
        "bounded_snapshot_sha256": sha256(
            "".join(
                f"{sha256(data)}  {remote_path}\n"
                for remote_path, data in snapshot.items()
            ).encode("utf-8")
        ),
        "bounded_snapshot_stable_through_first_mutation": True,
        "files": facts,
        "static_site_validation": static_validation,
        "pages_workflow": workflow,
        "anonymous_raw_readback": {"files": len(raw_checks), "result": "pass", "entries": raw_checks},
        "anonymous_pages_readback": {"files": len(pages_checks), "result": "pass", "entries": pages_checks},
        "aggregate_40_role_conformance_claim": False,
        "machine_data_is_learner_destination": False,
        "credentials_recorded": False,
        "personal_name_recorded": False,
    }
    RECEIPT.write_bytes((json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({
        "status": "pass",
        "commit": commit_sha,
        "tree": tree_sha,
        "changed": changed,
        "files": len(facts),
        "raw_readbacks": len(raw_checks),
        "pages_readbacks": len(pages_checks),
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_bytes": RECEIPT.stat().st_size,
        "receipt_sha256": sha256(RECEIPT.read_bytes()),
    }, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Never serialize exception text: filesystem exceptions can contain the
        # credential locator or local profile path even when the source is safe.
        print(f"FAIL: {type(exc).__name__}: bounded publication aborted", file=sys.stderr)
        raise SystemExit(1)
