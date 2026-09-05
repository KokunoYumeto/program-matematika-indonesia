#!/usr/bin/env python3
"""Anonymously verify every centrally hosted D100 English course byte."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from validate_d100_english_public_html_v1 import REPO_ROOT, sha256_file


COURSE_ROOT = REPO_ROOT / "docs" / "en" / "courses" / "D100"
MANIFEST_PATH = COURSE_ROOT / "D100_ENGLISH_READER_MIRROR_MANIFEST_V1.json"
DEFAULT_RECEIPT = COURSE_ROOT / "D100_ENGLISH_READER_PUBLIC_READBACK_V1.json"
BASE_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/D100/"
LANDING_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/en/"
OWNER_READER_URL = "https://kokunoyumeto.github.io/algebraic-geometry-bridge-id/en/"
EXPECTED_COMMIT = "a241226a492c69af94fd4668a7016da25be935c8"
EXPECTED_TREE = "e58481d10abcdb23cdd786d42d44de27b9480a40"
EXPECTED_RUN_ID = 33978057621


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_fact(path: Path, logical: str) -> dict[str, object]:
    return {"path": logical, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def public_url(logical: str, cache_key: str) -> str:
    escaped = "/".join(quote(part, safe="") for part in logical.split("/"))
    return f"{BASE_URL}{escaped}?commit={quote(cache_key, safe='')}"


def fetch(url: str) -> tuple[int, bytes]:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            request = Request(url, headers={"User-Agent": "d100-english-public-readback-v1"})
            with urlopen(request, timeout=60) as response:
                return int(response.status), response.read()
        except (HTTPError, URLError, TimeoutError) as error:
            last_error = error
            if attempt < 2:
                time.sleep(attempt + 1)
    assert last_error is not None
    raise last_error


def check_one(expected: dict[str, object], cache_key: str) -> dict[str, object]:
    logical = str(expected["path"])
    url = public_url(logical, cache_key)
    try:
        status, payload = fetch(url)
        actual_bytes = len(payload)
        actual_sha256 = sha256_bytes(payload)
        exact = (
            status == 200
            and actual_bytes == expected["bytes"]
            and actual_sha256 == expected["sha256"]
        )
        return {
            "path": logical,
            "url": url,
            "http_status": status,
            "expected_bytes": expected["bytes"],
            "actual_bytes": actual_bytes,
            "expected_sha256": expected["sha256"],
            "actual_sha256": actual_sha256,
            "exact": exact,
        }
    except Exception as error:  # bounded transport failure is receipt evidence
        return {
            "path": logical,
            "url": url,
            "http_status": None,
            "expected_bytes": expected["bytes"],
            "actual_bytes": None,
            "expected_sha256": expected["sha256"],
            "actual_sha256": None,
            "exact": False,
            "error": f"{type(error).__name__}: {error}",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", default=EXPECTED_COMMIT)
    parser.add_argument("--tree", default=EXPECTED_TREE)
    parser.add_argument("--run-id", type=int, default=EXPECTED_RUN_ID)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    receipt_path = args.receipt.resolve()
    if receipt_path != DEFAULT_RECEIPT.resolve():
        print("D100 English public readback: FAIL: receipt path is not canonical", file=sys.stderr)
        return 1
    if not 1 <= args.workers <= 16:
        print("D100 English public readback: FAIL: workers must be between 1 and 16", file=sys.stderr)
        return 1
    if args.commit != EXPECTED_COMMIT or args.tree != EXPECTED_TREE or args.run_id != EXPECTED_RUN_ID:
        print("D100 English public readback: FAIL: deployment identity changed", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    reader_rows = [
        {"path": f"reader/{row['path']}", "bytes": row["bytes"], "sha256": row["sha256"]}
        for row in manifest["reader"]["files"]
    ]
    control_names = [
        "D100_ENGLISH_READER_MIRROR_MANIFEST_V1.json",
        "D100_ENGLISH_READER_MIRROR_RECEIPT_V1.json",
        "README.md",
        "RIGHTS_AND_ATTRIBUTION.md",
    ]
    expected = reader_rows + [file_fact(COURSE_ROOT / name, name) for name in control_names]
    if len(expected) != 478 or len({row["path"] for row in expected}) != len(expected):
        print("D100 English public readback: FAIL: expected course closure changed", file=sys.stderr)
        return 1

    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(check_one, row, args.commit): row["path"] for row in expected}
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: str(row["path"]))
    failures = [row for row in results if not row["exact"]]

    landing_status, landing_bytes = fetch(f"{LANDING_URL}?commit={args.commit}")
    local_landing = (REPO_ROOT / "docs" / "en" / "index.html").read_bytes()
    landing_text = landing_bytes.decode("utf-8")
    landing = {
        "url": LANDING_URL,
        "http_status": landing_status,
        "bytes": len(landing_bytes),
        "sha256": sha256_bytes(landing_bytes),
        "matches_local": landing_bytes == local_landing,
        "contains_central_reader": BASE_URL + "reader/" in landing_text,
        "contains_owner_alternate": OWNER_READER_URL in landing_text,
    }
    script = Path(__file__).resolve()
    all_exact = not failures and landing_status == 200 and all(
        landing[key]
        for key in ("matches_local", "contains_central_reader", "contains_owner_alternate")
    )
    receipt = {
        "schema": "d100-english-reader-public-readback-v1",
        "status": "pass" if all_exact else "fail",
        "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "authentication": "anonymous",
        "public_access": "open" if all_exact else "unverified",
        "deployment": {
            "repository": "https://github.com/KokunoYumeto/program-matematika-indonesia",
            "commit": args.commit,
            "tree": args.tree,
            "pages_run_id": args.run_id,
            "pages_run_url": f"https://github.com/KokunoYumeto/program-matematika-indonesia/actions/runs/{args.run_id}",
            "base_url": BASE_URL,
        },
        "manifest": file_fact(
            MANIFEST_PATH,
            MANIFEST_PATH.relative_to(REPO_ROOT).as_posix(),
        ),
        "verification_script": file_fact(
            script,
            script.relative_to(REPO_ROOT).as_posix(),
        ),
        "scope": {
            "reader_files": len(reader_rows),
            "course_control_files": len(control_names),
            "files_checked": len(results),
            "bytes_checked": sum(int(row["actual_bytes"] or 0) for row in results),
            "exact_files": sum(bool(row["exact"]) for row in results),
            "failures": len(failures),
        },
        "landing_page": landing,
        "files": results,
        "invariants": {
            "every_course_file_http_200": not failures and all(row["http_status"] == 200 for row in results),
            "every_course_file_byte_and_sha256_exact": not failures,
            "central_reader_is_primary_on_english_landing": landing["contains_central_reader"],
            "owner_host_is_retained_as_alternate": landing["contains_owner_alternate"],
            "credential_material_recorded": False,
        },
    }
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": receipt["status"],
                "receipt": {
                    "path": receipt_path.relative_to(REPO_ROOT).as_posix(),
                    "bytes": receipt_path.stat().st_size,
                    "sha256": sha256_file(receipt_path),
                },
                "scope": receipt["scope"],
                "landing_page": landing,
                "first_failures": failures[:3],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if all_exact else 1


if __name__ == "__main__":
    raise SystemExit(main())
