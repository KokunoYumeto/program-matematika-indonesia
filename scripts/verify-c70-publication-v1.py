"""Resumable anonymous readback of one bounded C70 integration commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[1]
PARSER = argparse.ArgumentParser()
PARSER.add_argument("--commit", required=True)
PARSER.add_argument("--base-commit", required=True)
ARGS = PARSER.parse_args()
for value in (ARGS.commit, ARGS.base_commit):
    assert len(value) == 40 and all(character in "0123456789abcdef" for character in value)

REPOSITORY = "KokunoYumeto/program-matematika-indonesia"
PATHS = subprocess.check_output(
    [
        "git",
        "diff",
        "--name-only",
        "--diff-filter=AM",
        ARGS.base_commit,
        ARGS.commit,
        "--",
        "scripts",
        "backend/course-capsule-v1",
        "docs",
    ],
    cwd=ROOT,
    text=True,
).splitlines()
assert PATHS and all(".." not in Path(path).parts for path in PATHS)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


EXPECTED = {
    path: subprocess.check_output(["git", "show", ARGS.commit + ":" + path], cwd=ROOT)
    for path in PATHS
}
TARGET = (
    ROOT
    / "backend/course-capsule-v1/adapters/c70-capability-v1/publication"
    / ("GITHUB_READBACK_" + ARGS.commit[:12] + ".json")
)
TARGET.parent.mkdir(parents=True, exist_ok=True)
RECEIPT = (
    json.loads(TARGET.read_bytes())
    if TARGET.exists()
    else {
        "schema": "c70-integration-public-readback/1",
        "state": "in_progress",
        "source_commit": ARGS.commit,
        "base_commit": ARGS.base_commit,
        "anonymous": True,
        "credentials_used": False,
        "files": [],
        "failures": [],
        "scope": (
            "Every added or modified C70 adapter, integration, test, and generated "
            "learner-site file at the exact commit, plus every changed docs file "
            "through GitHub Pages."
        ),
    }
)
assert RECEIPT["source_commit"] == ARGS.commit
assert RECEIPT["base_commit"] == ARGS.base_commit

SESSION = requests.Session()
SESSION.trust_env = False
SESSION.auth = None
SESSION.headers.clear()
SESSION.headers["User-Agent"] = "c70-capability-anonymous-readback/1.0"


def save() -> None:
    TARGET.write_text(
        json.dumps(RECEIPT, indent=2) + "\n", encoding="utf-8", newline="\n"
    )


def read(url: str, expected: bytes) -> dict[str, object]:
    received = bytearray()
    with SESSION.get(url, stream=True, timeout=(15, 90)) as response:
        response.raise_for_status()
        assert "Authorization" not in response.request.headers
        for chunk in response.iter_content(65_536):
            received.extend(chunk)
            assert len(received) <= len(expected), "Unexpected larger response"
    assert len(received) == len(expected), "Public byte count differs"
    assert sha256(received) == sha256(expected), "Public SHA-256 differs"
    return {"bytes": len(received), "sha256": sha256(received), "http_status": 200}


repository_url = "https://github.com/" + REPOSITORY
response = SESSION.get(repository_url, timeout=(15, 30))
response.raise_for_status()
assert "Authorization" not in response.request.headers
RECEIPT["public_repository"] = repository_url

complete = {(row["surface"], row["path"]) for row in RECEIPT["files"]}
RECEIPT["failures"] = []
jobs = [
    (
        "source",
        path,
        "https://raw.githubusercontent.com/"
        + REPOSITORY
        + "/"
        + ARGS.commit
        + "/"
        + quote(path),
    )
    for path in PATHS
]
jobs += [
    (
        "pages",
        path,
        "https://kokunoyumeto.github.io/program-matematika-indonesia/"
        + quote(path[5:]),
    )
    for path in PATHS
    if path.startswith("docs/")
]

for surface, path, url in jobs:
    if (surface, path) in complete:
        prior = next(
            row
            for row in RECEIPT["files"]
            if (row["surface"], row["path"]) == (surface, path)
        )
        assert prior["bytes"] == len(EXPECTED[path])
        assert prior["sha256"] == sha256(EXPECTED[path])
        continue
    try:
        checked = read(url, EXPECTED[path])
    except (requests.RequestException, AssertionError) as error:
        RECEIPT["failures"].append(
            {"surface": surface, "path": path, "error": str(error), "url": url}
        )
        save()
        continue
    RECEIPT["files"].append(
        {
            "surface": surface,
            "path": path,
            "url": url,
            "checked_utc": datetime.now(timezone.utc).isoformat(),
            **checked,
        }
    )
    save()

RECEIPT["expected_files"] = len(jobs)
RECEIPT["verified_files"] = len(RECEIPT["files"])
RECEIPT["state"] = (
    "pass"
    if not RECEIPT["failures"] and len(RECEIPT["files"]) == len(jobs)
    else "incomplete"
)
save()
print(
    json.dumps(
        {
            "state": RECEIPT["state"],
            "verified": len(RECEIPT["files"]),
            "expected": len(jobs),
            "failures": RECEIPT["failures"],
        }
    )
)
raise SystemExit(0 if RECEIPT["state"] == "pass" else 1)
