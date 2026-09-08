"""Acquire only the three immutable A10 inputs, with bounded resumable reads."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "work/a10-native-inputs-v1"
INPUTS = {
    "reader.pdf": {
        "url": "https://zenodo.org/records/22236314/files/00-elementary-algebra-2e-bahasa-indonesia-EA2-C0082-reader.pdf?download=1",
        "bytes": 74917277,
        "sha256": "e4bc958edeb60a41604862dd0b67692bbfbcbb85b5de906c92af1f6c93bda505",
    },
    "backend-core.zip": {
        "url": "https://zenodo.org/records/22236314/files/elementary-algebra-2e-id-ID-1.0.3-backend-core.zip?download=1",
        "bytes": 147766660,
        "sha256": "6dc5ddafb3178d82308819ced69f724919dcb388168c5c63ec39db9e99777b13",
    },
    "reader-build-manifest.json": {
        "url": "https://zenodo.org/api/records/22236314/files/00-elementary-algebra-2e-bahasa-indonesia-EA2-C0082-reader-build-manifest.json/content",
        "bytes": 4282699,
        "sha256": "821d123602e75f6c1008c0d91350c2cc2c6c9ddeea5c76d00e922f59bd34a7b3",
    },
}


def file_identity(path: Path) -> dict:
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"bytes": path.stat().st_size, "sha256": digest}


def acquire(name: str, session: requests.Session) -> dict:
    spec = INPUTS[name]
    target = DESTINATION / name
    expected = {key: spec[key] for key in ("bytes", "sha256")}
    if target.exists():
        assert file_identity(target) == expected, f"Existing input identity differs: {name}"
        return {"name": name, "url": spec["url"], **expected, "state": "verified_existing"}
    partial = target.with_suffix(target.suffix + ".part")
    offset = partial.stat().st_size if partial.exists() else 0
    assert offset <= spec["bytes"], f"Partial input exceeds pinned size: {name}"
    if offset < spec["bytes"]:
        headers = {"Range": f"bytes={offset}-"} if offset else {}
        with session.get(spec["url"], headers=headers, stream=True, timeout=(15, 45)) as response:
            assert "Authorization" not in response.request.headers
            response.raise_for_status()
            if offset:
                assert response.status_code == 206
                assert response.headers.get("Content-Range", "").startswith(f"bytes {offset}-")
            with partial.open("ab" if offset else "wb") as stream:
                size = offset
                for block in response.iter_content(1024 * 1024):
                    size += len(block)
                    assert size <= spec["bytes"], f"Response exceeds pinned size: {name}"
                    stream.write(block)
    assert file_identity(partial) == expected, f"Downloaded input identity differs: {name}"
    partial.replace(target)
    return {"name": name, "url": spec["url"], **expected, "state": "downloaded_and_verified"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=tuple(INPUTS))
    args = parser.parse_args()
    DESTINATION.mkdir(parents=True, exist_ok=True)
    with requests.Session() as session:
        session.trust_env = False
        session.auth = None
        session.headers.clear()
        session.headers["User-Agent"] = "PMI-A10-ImmutableInputReadback/1"
        for name in ([args.only] if args.only else INPUTS):
            print(json.dumps(acquire(name, session)), flush=True)


if __name__ == "__main__":
    main()
