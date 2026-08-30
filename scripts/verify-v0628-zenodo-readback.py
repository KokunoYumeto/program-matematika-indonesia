#!/usr/bin/env python3
"""Anonymously verify the file-cap-aware Zenodo v0.62.8 successor."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import requests


PROJECT = Path(__file__).resolve().parents[1]
RELEASES = PROJECT / "releases"
RECORD_ID = 22167788
ADDITIVE = {
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.8.html",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.8.sha256",
}
USER_AGENT = "program-matematika-indonesia-v0628-anonymous-readback/1"


def local_path(name: str) -> Path:
    version = "v0.62.8" if name in ADDITIVE else "v0.62.7"
    path = RELEASES / version / name
    if not path.is_file():
        raise RuntimeError(f"missing expected local file: {path}")
    return path


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    record_response = requests.get(
        f"https://zenodo.org/api/records/{RECORD_ID}",
        headers={"User-Agent": USER_AGENT},
        timeout=120,
    )
    record_response.raise_for_status()
    record = record_response.json()
    if record.get("metadata", {}).get("version") != "0.62.8":
        raise RuntimeError("public record version differs")

    rows: list[dict[str, object]] = []
    mismatches: list[dict[str, object]] = []
    for remote in sorted(record.get("files", []), key=lambda row: row["key"]):
        name = str(remote["key"])
        expected_path = local_path(name)
        expected_bytes = expected_path.stat().st_size
        expected_sha256 = sha256_path(expected_path)
        digest = hashlib.sha256()
        count = 0
        with requests.get(
            str(remote["links"]["self"]),
            headers={"User-Agent": USER_AGENT},
            stream=True,
            timeout=1200,
        ) as response:
            if response.status_code != 200:
                mismatches.append({"name": name, "http_status": response.status_code})
                continue
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    digest.update(chunk)
                    count += len(chunk)
        observed_sha256 = digest.hexdigest()
        if count != expected_bytes or observed_sha256 != expected_sha256:
            mismatches.append(
                {
                    "name": name,
                    "bytes": count,
                    "sha256": observed_sha256,
                    "expected_bytes": expected_bytes,
                    "expected_sha256": expected_sha256,
                }
            )
        rows.append({"name": name, "bytes": count, "sha256": observed_sha256})

    if len(rows) != 100 or mismatches:
        raise RuntimeError(json.dumps({"rows": len(rows), "mismatches": mismatches}, sort_keys=True))
    facts = "".join(
        f"{row['sha256']}  {row['bytes']}  {row['name']}\n"
        for row in sorted(rows, key=lambda row: str(row["name"]))
    )
    additive_rows = [row for row in rows if row["name"] in ADDITIVE]
    print(
        json.dumps(
            {
                "result": "published_and_anonymously_verified",
                "record_id": record["id"],
                "doi": record["doi"],
                "concept_doi": record["conceptdoi"],
                "version": record["metadata"]["version"],
                "files": len(rows),
                "bytes": sum(int(row["bytes"]) for row in rows),
                "inherited_files": len(rows) - len(additive_rows),
                "additive_files": len(additive_rows),
                "aggregate_sha256": hashlib.sha256(facts.encode("utf-8")).hexdigest(),
                "anonymous_mismatches": 0,
                "additive": additive_rows,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
