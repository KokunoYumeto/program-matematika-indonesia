"""Resume exact anonymous readback of a bounded central-backend increment."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "KokunoYumeto/program-matematika-indonesia"
PAGES = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
SCOPES = (
    "backend", "docs", "scripts", "schema", "schemas", "releases", "tests", "app",
    "package.json", "package-lock.json", "README.md", ".gitattributes",
    ".github", ".openai/hosting.json",
)
FRONT_DOORS = (
    "docs/index.html", "docs/id/index.html", "docs/en/index.html",
    "docs/backend/index.html", "docs/backend/b95/B95.html",
    "docs/backend/b95/B95-pengajar.html", "docs/backend/c140/C140.html",
    "docs/backend/c140/C140-pengajar.html",
    "docs/backend/a10/A10.html", "docs/backend/a10/A10-en.html",
    "docs/backend/a10/A10-pengajar.html", "docs/backend/a10/A10-pengajar-en.html",
    "docs/backend/a00/A00.html", "docs/backend/a00/A00-en.html",
    "docs/backend/a00/A00-pengajar.html", "docs/backend/a00/A00-pengajar-en.html",
)


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def identity(data: bytes) -> dict:
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def make_jobs(base: str, commit: str) -> list[dict]:
    git("merge-base", "--is-ancestor", base, commit)
    removed = git("diff", "--no-renames", "--name-only", "--diff-filter=DT", base, commit, "--", *SCOPES)
    assert not removed.strip(), "This release verifier does not authorize removed or type-changed public files"
    changed = git("diff", "--no-renames", "--name-only", "--diff-filter=AM", base, commit, "--", *SCOPES)
    paths = sorted(set(changed.decode("utf-8").splitlines()) | set(FRONT_DOORS))
    assert paths and all(not Path(path).is_absolute() and ".." not in Path(path).parts for path in paths)
    result = []
    for path in paths:
        expected = identity(git("show", f"{commit}:{path}"))
        result.append({"surface": "source", "path": path,
                       "url": f"https://raw.githubusercontent.com/{REPOSITORY}/{commit}/{quote(path)}",
                       **expected})
        if path.startswith("docs/"):
            result.append({"surface": "pages", "path": path,
                           "url": PAGES + quote(path[5:]), **expected})
    return result


def fetch_identity(session: requests.Session, job: dict) -> dict:
    size, digest = 0, hashlib.sha256()
    with session.get(job["url"], stream=True, timeout=(15, 45), allow_redirects=False) as response:
        assert response.status_code == 200, f"HTTP {response.status_code}"
        assert "Authorization" not in response.request.headers
        for block in response.iter_content(65536):
            size += len(block)
            assert size <= job["bytes"], "Public response exceeds committed size"
            digest.update(block)
        assert size == job["bytes"], "Public byte count differs"
        assert digest.hexdigest() == job["sha256"], "Public SHA-256 differs"
        if job["surface"] == "pages" and job["path"].endswith(".html"):
            assert response.headers.get("Content-Type", "").split(";")[0] == "text/html"
        return {**job, "http_status": 200,
                "content_type": response.headers.get("Content-Type"),
                "checked_utc": datetime.now(timezone.utc).isoformat()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-commit", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    assert all(re.fullmatch(r"[0-9a-f]{40}", value) for value in (args.base_commit, args.commit))
    jobs = make_jobs(args.base_commit, args.commit)
    if args.plan_only:
        print(json.dumps({"jobs": len(jobs), "source_files": sum(j["surface"] == "source" for j in jobs),
                          "pages_files": sum(j["surface"] == "pages" for j in jobs),
                          "bytes": sum(j["bytes"] for j in jobs)}))
        return
    target = ROOT / "backend/course-capsule-v1/validation" / f"COMBINED_BACKEND_READBACK_{args.commit[:12]}.json"
    receipt = json.loads(target.read_bytes()) if target.exists() else {
        "schema": "combined-backend-increment-public-readback/1", "state": "in_progress",
        "base_commit": args.base_commit, "source_commit": args.commit,
        "anonymous": True, "credentials_used": False, "ambient_credentials_disabled": True,
        "scope": "Changed committed files in the listed integration scopes, plus bilingual and A00/A10/B95/C140 front doors; every docs file also checked through Pages.",
        "integration_scopes": list(SCOPES), "expected_jobs": jobs, "files": [],
        "failures": [], "overall_program_backend_complete": False,
        "zenodo_preservation_verified": False,
    }
    assert receipt["base_commit"] == args.base_commit and receipt["source_commit"] == args.commit
    assert receipt["expected_jobs"] == jobs, "Resume scope differs"
    expected = {(j["surface"], j["path"]): j for j in jobs}
    complete = {}
    for row in receipt["files"]:
        key = (row["surface"], row["path"])
        assert key not in complete and key in expected
        assert all(row[field] == expected[key][field] for field in ("url", "bytes", "sha256"))
        complete[key] = row

    def save() -> None:
        # Atomic replacement preserves the last complete cursor if interrupted.
        temporary = target.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
        temporary.replace(target)

    session = requests.Session()
    session.trust_env = False
    session.auth = None
    session.headers.clear()
    session.headers["User-Agent"] = "PMI-CombinedBackend-AnonymousReadback/1"
    with session:
        with session.get(f"https://github.com/{REPOSITORY}", timeout=(15, 30), allow_redirects=False) as response:
            assert response.status_code == 200 and "Authorization" not in response.request.headers
        receipt["public_repository"] = f"https://github.com/{REPOSITORY}"
        receipt["failures"] = []
        for job in jobs:
            if (job["surface"], job["path"]) in complete:
                continue
            try:
                receipt["files"].append(fetch_identity(session, job))
            except (requests.RequestException, AssertionError) as error:
                receipt["failures"].append({"surface": job["surface"], "path": job["path"],
                                             "error": str(error), "url": job["url"]})
            save()
            if len(receipt["files"]) % 20 == 0:
                print(json.dumps({"verified": len(receipt["files"]), "expected": len(jobs),
                                  "failures": len(receipt["failures"])}), flush=True)
    receipt["state"] = "pass" if not receipt["failures"] and len(receipt["files"]) == len(jobs) else "incomplete"
    receipt["verified_files"] = len(receipt["files"])
    receipt["expected_files"] = len(jobs)
    save()
    print(json.dumps({"state": receipt["state"], "verified": len(receipt["files"]), "expected": len(jobs),
                      "receipt": target.name, "failures": receipt["failures"]}))
    raise SystemExit(0 if receipt["state"] == "pass" else 1)


if __name__ == "__main__":
    main()
