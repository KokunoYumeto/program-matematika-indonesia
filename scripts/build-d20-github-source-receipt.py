#!/usr/bin/env python3
"""Build a sanitized anonymous GitHub/Pages readback receipt for D20 v2.3.1."""

from __future__ import annotations

import hashlib
import json
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath


PROJECT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT / "GITHUB_D20_V231_SOURCE_PUBLICATION_RECEIPT.json"
REPOSITORY = "https://github.com/KokunoYumeto/program-matematika-indonesia"
RAW_ROOT = "https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia"
PAGES_ROOT = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
EXPECTED_COMMIT = "ec576caa27e08a0442ea6abac5be036e79b9a768"
EXPECTED_TREE = "e9c9a646349b9442e51b2378b26536cd5634c35e"
EXPECTED_SOURCE_FILES = 61
PAGES_RUN = {
    "database_id": 33339486099,
    "workflow": "pages-build-deployment",
    "status": "completed",
    "conclusion": "success",
    "url": "https://github.com/KokunoYumeto/program-matematika-indonesia/actions/runs/33339486099",
}
PAGE_SOURCES = (
    "docs/index.html",
    "docs/backend/index.html",
    "docs/data/modular-backend-pattern-index-v1.json",
    "docs/data/v23-adapter-index-v1.json",
    "docs/data/course-capsule-v1/course-capsules.jsonl",
    "docs/peta-belajar-luring.html",
    "docs/schema/v2.3/index.html",
)


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str) -> tuple[int, bytes]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "program-matematika-indonesia-readback/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return int(response.status), response.read()


def page_url(source_path: str) -> str:
    relative = source_path.removeprefix("docs/")
    if relative == "index.html":
        return PAGES_ROOT
    if relative.endswith("/index.html"):
        relative = relative[: -len("index.html")]
    return PAGES_ROOT + urllib.parse.quote(relative, safe="/")


def main() -> None:
    commit = run_git("rev-parse", "HEAD")
    tree = run_git("rev-parse", "HEAD^{tree}")
    if commit != EXPECTED_COMMIT or tree != EXPECTED_TREE:
        raise SystemExit(f"unexpected source identity: {commit} / {tree}")

    paths = tuple(
        line
        for line in run_git("diff", "--name-only", "HEAD^", "HEAD").splitlines()
        if line
    )
    if len(paths) != EXPECTED_SOURCE_FILES or len(paths) != len(set(paths)):
        raise SystemExit(f"unexpected bounded source inventory: {len(paths)}")

    raw_entries: list[dict[str, object]] = []
    raw_bytes = 0
    for path_text in paths:
        pure = PurePosixPath(path_text)
        if pure.is_absolute() or ".." in pure.parts or "\\" in path_text:
            raise SystemExit(f"unsafe path: {path_text}")
        local = (PROJECT / pure.as_posix()).read_bytes()
        url = f"{RAW_ROOT}/{commit}/{urllib.parse.quote(path_text, safe='/')}"
        status, public = fetch(url)
        if status != 200 or public != local:
            raise SystemExit(f"raw readback mismatch: {path_text}")
        raw_entries.append(
            {
                "path": path_text,
                "url": url,
                "http_status": status,
                "bytes": len(public),
                "sha256": sha256(public),
            }
        )
        raw_bytes += len(public)

    page_entries: list[dict[str, object]] = []
    for source_path in PAGE_SOURCES:
        local = (PROJECT / source_path).read_bytes()
        url = page_url(source_path)
        status, public = fetch(url)
        if status != 200 or public != local:
            raise SystemExit(f"Pages readback mismatch: {source_path}")
        page_entries.append(
            {
                "source_path": source_path,
                "url": url,
                "http_status": status,
                "bytes": len(public),
                "sha256": sha256(public),
            }
        )

    authority_prefix = "backend/v2.3/extensions/d20-functional-analysis-v0.1.0/"
    authority_names = (
        "INPUT_AUTHORITIES.json",
        "PACKAGE_CHECKSUMS.sha256",
        "README.md",
        "capability-declarations-v0.2.0.json",
        "csv-projection-manifest-v0.2.0.json",
        "manifest.json",
        "scope-declaration-v0.2.0.json",
        "seal.json",
    )
    authority_paths = [authority_prefix + name for name in authority_names]
    if not set(authority_paths) <= set(paths):
        raise SystemExit("compact D20 authority surface is incomplete")

    receipt = {
        "schema_id": "program-matematika-indonesia/github-d20-v231-source-publication/1.0.0",
        "status": "PASS",
        "repository": REPOSITORY,
        "branch": "main",
        "source_commit": commit,
        "source_tree": tree,
        "parent_commit": run_git("show", "-s", "--format=%P", "HEAD"),
        "recorded_at_utc": run_git("show", "-s", "--format=%cI", "HEAD"),
        "distribution_boundary": "compact_git_authority_plus_complete_release_zip",
        "boundary_note": "Git publishes the compact authority surface and learner/method artifacts. The complete sealed 61-file adapter is distributed as the release and Zenodo ZIP because one canonical CSV is larger than the normal GitHub Git-blob limit.",
        "bounded_file_count": len(raw_entries),
        "bounded_file_bytes": raw_bytes,
        "canonical_extension_files": len(authority_paths),
        "compact_authority_paths": authority_paths,
        "complete_archive": {
            "filename": "program-matematika-indonesia-backend-v2.3.1-d20-adapter-v0.1.0.zip",
            "bytes": 61438875,
            "sha256": "25e059d26f049141dad326817bd01319b120a19fc4b78fb2efc879764fea2099",
            "member_count": 61,
            "uncompressed_bytes": 551281460,
            "release": "v0.62.12",
            "zenodo_concept_doi": "10.5281/zenodo.22059707",
        },
        "anonymous_raw_readback": {
            "result": "PASS",
            "files": len(raw_entries),
            "entries": raw_entries,
        },
        "pages_workflow": PAGES_RUN,
        "anonymous_pages_readback": {
            "result": "PASS",
            "files": len(page_entries),
            "entries": page_entries,
        },
        "learner_primary_url": PAGES_ROOT,
        "machine_data_is_learner_destination": False,
        "aggregate_40_role_conformance_claim": False,
        "other_course_roles_unbound": 35,
        "credentials_recorded": False,
        "personal_name_recorded": False,
        "model_provenance": "OpenAI Codex gpt-5.6-sol, Ultra",
    }
    OUTPUT.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    data = OUTPUT.read_bytes()
    print(
        json.dumps(
            {
                "path": OUTPUT.name,
                "bytes": len(data),
                "sha256": sha256(data),
                "raw_files": len(raw_entries),
                "raw_bytes": raw_bytes,
                "pages_files": len(page_entries),
                "status": "PASS",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
