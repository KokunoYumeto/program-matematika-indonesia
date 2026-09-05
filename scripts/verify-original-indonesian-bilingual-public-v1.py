"""Anonymous exact-byte readback for the B80/D120 English projection increment."""

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
REPOSITORY = "KokunoYumeto/program-matematika-indonesia"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_commit(value: str) -> str:
    if len(value) != 40 or any(character not in "0123456789abcdef" for character in value):
        raise argparse.ArgumentTypeError("expected a full lowercase Git commit")
    return value


parser = argparse.ArgumentParser()
parser.add_argument("--commit", required=True, type=exact_commit)
parser.add_argument("--base-commit", required=True, type=exact_commit)
args = parser.parse_args()

paths = subprocess.check_output(
    [
        "git",
        "diff",
        "--name-only",
        "--diff-filter=AM",
        args.base_commit,
        args.commit,
        "--",
        "package.json",
        "scripts",
        "backend/authority",
        "backend/course-capsule-v1",
        "docs",
    ],
    cwd=ROOT,
    text=True,
).splitlines()
assert paths
assert all(".." not in Path(path).parts for path in paths)

expected = {
    path: subprocess.check_output(["git", "show", f"{args.commit}:{path}"], cwd=ROOT)
    for path in paths
}
target = (
    ROOT
    / "backend/course-capsule-v1/localizations/original-indonesian-bilingual-v1/publication"
    / f"GITHUB_READBACK_{args.commit[:12]}.json"
)
target.parent.mkdir(parents=True, exist_ok=True)
receipt = (
    json.loads(target.read_bytes())
    if target.exists()
    else {
        "schema": "original-indonesian-bilingual-public-readback/1",
        "state": "in_progress",
        "source_commit": args.commit,
        "base_commit": args.base_commit,
        "anonymous": True,
        "credentials_used": False,
        "scope": (
            "Every added or modified B80/D120 English localization, generator, test, "
            "authority, interface, and generated learner-site file at the exact integration "
            "commit; every changed docs file is additionally checked through GitHub Pages."
        ),
        "files": [],
        "failures": [],
        "overall_program_backend_complete": False,
    }
)
assert receipt["source_commit"] == args.commit
assert receipt["base_commit"] == args.base_commit

session = requests.Session()
session.trust_env = False
session.auth = None
session.headers.clear()
session.headers["User-Agent"] = "original-indonesian-bilingual-anonymous-readback/1.0"


def save() -> None:
    target.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def read(url: str, wanted: bytes) -> dict[str, object]:
    received = bytearray()
    with session.get(url, stream=True, timeout=(15, 90)) as response:
        response.raise_for_status()
        assert "Authorization" not in response.request.headers
        for chunk in response.iter_content(65_536):
            received.extend(chunk)
            assert len(received) <= len(wanted), "unexpected larger response"
    assert len(received) == len(wanted), "public byte count differs"
    assert sha256(received) == sha256(wanted), "public SHA-256 differs"
    return {"bytes": len(received), "sha256": sha256(received), "http_status": 200}


repository_url = f"https://github.com/{REPOSITORY}"
repository_response = session.get(repository_url, timeout=(15, 30))
repository_response.raise_for_status()
assert "Authorization" not in repository_response.request.headers
receipt["public_repository"] = repository_url

complete = {(row["surface"], row["path"]) for row in receipt["files"]}
receipt["failures"] = []
jobs = [
    (
        "source",
        path,
        f"https://raw.githubusercontent.com/{REPOSITORY}/{args.commit}/{quote(path)}",
    )
    for path in paths
]
jobs.extend(
    (
        "pages",
        path,
        "https://kokunoyumeto.github.io/program-matematika-indonesia/"
        + quote(path.removeprefix("docs/")),
    )
    for path in paths
    if path.startswith("docs/")
)

for surface, path, url in jobs:
    if (surface, path) in complete:
        prior = next(
            row
            for row in receipt["files"]
            if (row["surface"], row["path"]) == (surface, path)
        )
        assert prior["bytes"] == len(expected[path])
        assert prior["sha256"] == sha256(expected[path])
        continue
    try:
        checked = read(url, expected[path])
    except (requests.RequestException, AssertionError) as error:
        receipt["failures"].append(
            {"surface": surface, "path": path, "url": url, "error": str(error)}
        )
        save()
        continue
    receipt["files"].append(
        {
            "surface": surface,
            "path": path,
            "url": url,
            "checked_utc": datetime.now(timezone.utc).isoformat(),
            **checked,
        }
    )
    save()

receipt["expected_files"] = len(jobs)
receipt["verified_files"] = len(receipt["files"])
receipt["state"] = (
    "pass"
    if not receipt["failures"] and len(receipt["files"]) == len(jobs)
    else "incomplete"
)
save()
print(
    json.dumps(
        {
            "state": receipt["state"],
            "verified": receipt["verified_files"],
            "expected": receipt["expected_files"],
            "failures": receipt["failures"],
            "receipt": target.relative_to(ROOT).as_posix(),
            "receipt_bytes": target.stat().st_size,
            "receipt_sha256": sha256(target.read_bytes()),
        }
    )
)
raise SystemExit(0 if receipt["state"] == "pass" else 1)
