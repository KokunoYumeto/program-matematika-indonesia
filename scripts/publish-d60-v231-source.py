#!/usr/bin/env python3
"""Publish and anonymously verify the bounded D60 v2.3.1 source admission."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_PUBLISHER = ROOT / "scripts/publish-b10-v231-source.py"
TOKEN_FILE_ENV = "PMI_D60_GITHUB_TOKEN_FILE"
RECEIPT = ROOT / "GITHUB_D60_V231_SOURCE_PUBLICATION_RECEIPT.json"
OWNER = "KokunoYumeto"
REPO_NAME = "program-matematika-indonesia"
REPO = f"{OWNER}/{REPO_NAME}"
COMMIT_MESSAGE = "Admit the corpus-neutral D60 backend v2.3.1 adapter"


def load_base():
    spec = importlib.util.spec_from_file_location("pmi_b10_source_publisher", BASE_PUBLISHER)
    if spec is None or spec.loader is None:
        raise RuntimeError("bounded publisher helper cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.TOKEN_FILE_ENV = TOKEN_FILE_ENV
    module.COMMIT_MESSAGE = COMMIT_MESSAGE
    module.USER_AGENT = "Codex-PMI-D60-v231-Source-Publisher/1.0"
    return module


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_token(base) -> str:
    locator = os.environ.get(TOKEN_FILE_ENV)
    if not locator:
        raise RuntimeError(f"{TOKEN_FILE_ENV} is required")
    path = Path(locator)
    if not path.is_file():
        raise RuntimeError("configured GitHub credential file is unavailable")
    text = path.read_text(encoding="utf-8")
    candidates: list[str] = []
    for pattern in (r"github_pat_[A-Za-z0-9_]+", r"ghp_[A-Za-z0-9]{20,}"):
        candidates.extend(re.findall(pattern, text))
    for candidate in dict.fromkeys(candidates):
        status, body, _ = base.request(
            f"{base.API}/user", token=candidate, expected=(200, 401, 403)
        )
        if status == 200 and json.loads(body.decode("utf-8")).get("login", "").casefold() == OWNER.casefold():
            return candidate
    raise RuntimeError("no working credential for the exact public repository owner")


def source_files() -> dict[str, Path]:
    names = {
        "README.md": ROOT / "README.md",
        "backend/v2.3/README.md": ROOT / "backend/v2.3/README.md",
        "backend/v2.3/authorities/D60_FINAL_OWNER_AUTHORITY_20260830.json": ROOT / "backend/v2.3/authorities/D60_FINAL_OWNER_AUTHORITY_20260830.json",
        "backend/v2.3/scripts/build_d60_v23_adapter.py": ROOT / "backend/v2.3/scripts/build_d60_v23_adapter.py",
        "backend/v2.3/scripts/validate_d60_v23_adapter.py": ROOT / "backend/v2.3/scripts/validate_d60_v23_adapter.py",
        "backend/v2.3/scripts/v231_adapter_common.py": ROOT / "backend/v2.3/scripts/v231_adapter_common.py",
        "backend/v2.3/scripts/validate_lane_adapter_v231.py": ROOT / "backend/v2.3/scripts/validate_lane_adapter_v231.py",
        "backend/v2.3/scripts/package_lane_adapter_v231.py": ROOT / "backend/v2.3/scripts/package_lane_adapter_v231.py",
        "scripts/publish-d60-v231-source.py": Path(__file__).resolve(),
        "scripts/validate-static-site.mjs": ROOT / "scripts/validate-static-site.mjs",
        "docs/index.html": ROOT / "docs/index.html",
        "docs/live-course-publications.js": ROOT / "docs/live-course-publications.js",
        "docs/schema/v2.3/index.html": ROOT / "docs/schema/v2.3/index.html",
    }
    extension = ROOT / "backend/v2.3/extensions/d60-algebraic-topology-v0.1.0"
    extension_files = sorted(item for item in extension.rglob("*") if item.is_file())
    if len(extension_files) != 59:
        raise RuntimeError("canonical D60 extension file count is not 59")
    for path in extension_files:
        names[path.relative_to(ROOT).as_posix()] = path
    for remote_path, local_path in names.items():
        if not local_path.is_file():
            raise RuntimeError(f"missing bounded source: {remote_path}")
        if "/builds/" in f"/{remote_path}" or remote_path.endswith(".zip"):
            raise RuntimeError(f"build or release payload entered source publication: {remote_path}")
    return dict(sorted(names.items()))


def retry_exact(base, url: str, expected: bytes, attempts: int = 36) -> bytes:
    return base.retry_exact(url, expected, attempts=attempts)


def anonymous_readback(base, commit_sha: str, snapshot: dict[str, bytes]):
    raw = []
    for remote_path, expected in snapshot.items():
        url = f"https://raw.githubusercontent.com/{REPO}/{commit_sha}/{urllib.parse.quote(remote_path, safe='/')}"
        body = retry_exact(base, url, expected, attempts=12)
        raw.append({"path": remote_path, "url": url, "bytes": len(body), "sha256": sha256(body)})
    page_map = {
        "docs/index.html": "https://kokunoyumeto.github.io/program-matematika-indonesia/",
        "docs/live-course-publications.js": "https://kokunoyumeto.github.io/program-matematika-indonesia/live-course-publications.js",
        "docs/schema/v2.3/index.html": "https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v2.3/",
    }
    pages = []
    for source_path, url in page_map.items():
        expected = snapshot[source_path]
        body = retry_exact(base, url, expected)
        pages.append({"source_path": source_path, "url": url, "bytes": len(body), "sha256": sha256(body)})
    return raw, pages


def main() -> None:
    base = load_base()
    paths = source_files()
    snapshot = base.snapshot_files(paths)
    static_validation = base.run_static_validation()
    base.verify_snapshot_current(paths, snapshot, phase="post-validation check")
    token = load_token(base)
    _, repository = base.api(f"/repos/{REPO}", token)
    if repository.get("private") or repository.get("full_name", "").casefold() != REPO.casefold():
        raise RuntimeError("destination is not the exact public repository")
    commit_sha, tree_sha, parent_sha, facts, changed = base.publish_source(token, paths, snapshot)
    _, live_ref = base.api(f"/repos/{REPO}/git/ref/heads/main", token)
    if live_ref["object"]["sha"] != commit_sha:
        raise RuntimeError("main ref did not retain the D60 source commit")
    workflow = base.wait_for_pages(token, commit_sha, changed)
    raw_checks, page_checks = anonymous_readback(base, commit_sha, snapshot)
    receipt = {
        "schema_id": "program-matematika-indonesia/github-d60-v231-source-publication/1.0.0",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "repository": f"https://github.com/{REPO}",
        "branch": "main",
        "parent_commit": parent_sha,
        "source_commit": commit_sha,
        "source_tree": tree_sha,
        "commit_created": changed,
        "commit_message": COMMIT_MESSAGE if changed else "existing exact source commit",
        "bounded_file_count": len(facts),
        "bounded_file_bytes": sum(int(row["bytes"]) for row in facts),
        "bounded_snapshot_sha256": sha256("".join(f"{sha256(data)}  {path}\n" for path, data in snapshot.items()).encode("utf-8")),
        "bounded_snapshot_stable_through_first_mutation": True,
        "files": facts,
        "static_site_validation": static_validation,
        "pages_workflow": workflow,
        "anonymous_raw_readback": {"files": len(raw_checks), "result": "PASS", "entries": raw_checks},
        "anonymous_pages_readback": {"files": len(page_checks), "result": "PASS", "entries": page_checks},
        "canonical_extension_files": 59,
        "aggregate_40_role_conformance_claim": False,
        "other_course_roles_unbound": 37,
        "machine_data_is_learner_destination": False,
        "learner_primary_url": "https://kokunoyumeto.github.io/algebraic-topology-id/roberts-001-030-fomberg-001-007-ca01-hints-r01-r06-ca02-ca03-lab01-lab02-lab03-lab04-capstone/",
        "credentials_recorded": False,
        "personal_name_recorded": False,
    }
    RECEIPT.write_bytes((json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({
        "status": "PASS",
        "commit": commit_sha,
        "tree": tree_sha,
        "changed": changed,
        "files": len(facts),
        "raw_readbacks": len(raw_checks),
        "pages_readbacks": len(page_checks),
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_bytes": RECEIPT.stat().st_size,
        "receipt_sha256": sha256(RECEIPT.read_bytes()),
    }, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: bounded publication aborted", file=sys.stderr)
        raise SystemExit(1)
