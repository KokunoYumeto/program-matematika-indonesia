"""Anonymous, bounded byte/MIME readback of the learner and capsule website."""

from __future__ import annotations

import hashlib
import json
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
PATHS = (
    "",
    "index.html",
    "app.js",
    "courses.js",
    "learner-delivery.js",
    "learner-tools.js",
    "learner-state.js",
    "backend/index.html",
    "backend/",
    "backend/backend.css",
    "backend/backend.js",
    "backend/judson/C30.html",
    "backend/judson/C40.html",
    "backend/judson/chapters.json",
    "backend/judson/route-evidence.json",
    "backend/judson/contribution.md",
    "backend/judson/validation.json",
    "data/course-capsule-v1/course-capsules.jsonl",
    "data/course-capsule-v1/course-capsules.json",
    "data/course-capsule-v1/manifest.json",
    "data/course-capsule-v1/validation-receipt.json",
    "data/course-capsule-v1/README.md",
    "data/course-capsule-v1/backend-design-policy-v1.json",
    "data/course-capsule-v1/public-baseline-v0.62.12.json",
    "data/course-capsule-v1/native-package-references-v1.json",
    "data/course-capsule-v1/native-family-public-evidence-v1.json",
    "data/course-capsule-v1/native-family-public-evidence-note-v1.md",
    "data/learner-tools-v1.json",
    "data/learner-delivery-v1.json",
    "data/modular-backend-pattern-index-v1.json",
    "data/v23-adapter-index-v1.json",
    "schema/course-capsule-v1/course-capsule-v1.schema.json",
    "schema/course-capsule-v1/backend-design-policy-v1.schema.json",
    "schema/course-capsule-v1/public-baseline-v1.schema.json",
    "schema/v1/learner-tools-v1.schema.json",
    "schema/v1/v23-adapter-index-v1.schema.json",
    "id-ID/courses/A00/latihan/index.html",
    "id-ID/courses/B95/index.html",
    "id-ID/courses/B95/",
    "id-ID/courses/D20/index.html",
    "id-ID/courses/D30/index.html",
    "id-ID/courses/D40/index.html",
    "id-ID/courses/D40/",
    "peta-belajar-luring.html",
)
DESTINATION = (
    ROOT / "backend/course-capsule-v1/validation/PUBLIC_SITE_READBACK_v0.62.13.json"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(path: str) -> dict:
    local_path = path + "index.html" if not path or path.endswith("/") else path
    expected = (ROOT / "docs" / local_path).read_bytes()
    with requests.Session() as session:
        session.trust_env = False
        session.auth = None
        session.headers.clear()
        session.headers["User-Agent"] = "PMI-CourseCapsule-AnonymousReadback/1.0"
        response = session.get(ORIGIN + path, timeout=(15, 60), allow_redirects=False)
        data = response.content
        mime = response.headers.get("Content-Type", "").split(";", 1)[0].lower()
        assert response.status_code == 200, (path, response.status_code)
        assert data == expected, (path, "public bytes differ")
        extension = Path(local_path).suffix
        expected_mimes = {
            ".html": {"text/html"},
            ".css": {"text/css"},
            ".js": {"text/javascript", "application/javascript"},
            ".json": {"application/json", "application/schema+json"} if local_path.startswith("schema/") else {"application/json"},
            ".md": {"text/plain", "text/markdown", "application/octet-stream"},
            # GitHub Pages serves this canonical export as a download. The
            # live application consumes .json, whose MIME is checked above.
            ".jsonl": {
                "application/octet-stream", "application/jsonl",
                "application/x-ndjson", "application/json", "text/plain",
            },
        }
        assert mime in expected_mimes[extension], (path, mime)
        if extension == ".json":
            json.loads(data)
        if extension == ".jsonl":
            assert len([json.loads(row) for row in data.splitlines()]) == 40
        return {
            "path": path,
            "url": response.url,
            "http_status": response.status_code,
            "content_type": response.headers.get("Content-Type"),
            "bytes": len(data),
            "sha256": sha256(data),
            "exact_local_identity": True,
            "mime_role": "downloadable_canonical_export" if extension == ".jsonl"
            else "browser_or_machine_consumer",
            "mime_compatible_with_consumer": True,
        }


def main() -> None:
    global ORIGIN, DESTINATION
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", action="store_true", help="check the retained localhost curriculum preview")
    parser.add_argument("--receipt-version", default="v0.62.14", choices=("v0.62.13", "v0.62.14"))
    args = parser.parse_args()
    DESTINATION = ROOT / f"backend/course-capsule-v1/validation/PUBLIC_SITE_READBACK_{args.receipt_version}.json"
    if args.local:
        ORIGIN = "http://localhost:3000/hub/"
        DESTINATION = ROOT / f"backend/course-capsule-v1/validation/LOCAL_HTTP_READBACK_{args.receipt_version}.json"
    with ThreadPoolExecutor(max_workers=4) as executor:
        rows = list(executor.map(check, PATHS))
    local_rows = json.loads(
        (ROOT / "docs/data/course-capsule-v1/course-capsules.json").read_text("utf-8")
    )
    ids = [row["course_id"] for row in local_rows]
    assert len(ids) == len(set(ids)) == 40
    assert all(len(row["layers"]) == 7 for row in local_rows)
    html = (ROOT / "docs/backend/index.html").read_text("utf-8")
    assert html.count("data-static-course-id=") == 40
    assert '<html lang="id">' in html
    assert 'href="backend/index.html"' in (ROOT / "docs/index.html").read_text("utf-8")
    result = {
        "schema_id": "pmi/course-capsule-public-readback/v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "state": "PASS_EXACT_LOCAL_HTTP_BYTES" if args.local else "PASS_ANONYMOUS_EXACT_PUBLIC_BYTES",
        "origin": ORIGIN,
        "network_public_verification": not args.local,
        "authentication": "none",
        "trust_env": False,
        "file_count": len(rows),
        "aggregate_bytes": sum(row["bytes"] for row in rows),
        "course_count": 40,
        "seven_layer_rows": 40,
        "no_javascript_cards": 40,
        "published_roles": sum(row["course"]["state"] == "published" for row in local_rows),
        "production_roles": [row["course_id"] for row in local_rows if row["course"]["state"] == "production"],
        "mime_note": "The browser consumes application/json. GitHub Pages exposes the canonical JSONL export as an octet-stream download; its forty records are parsed and byte-verified here.",
        "entries": rows,
    }
    DESTINATION.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"state": result["state"], "file_count": len(rows), "receipt_bytes": DESTINATION.stat().st_size, "receipt_sha256": sha256(DESTINATION.read_bytes())}))


if __name__ == "__main__":
    main()
