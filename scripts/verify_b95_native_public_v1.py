"""Verify the bounded B95 native/public evidence locally, without credentials.

The producer's publication receipts are treated as evidence inputs.  This
script checks their public-state and byte/hash-readback claims, checks the
adapter's byte-for-byte preserved completion receipt, and never changes the
producer checkout or publication state.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from b95_capability_model_v1 import (
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    GITHUB_RECEIPT_PATH,
    PUBLIC_RECEIPT_PATH,
    RELEASE_ID,
    ZENODO_RECEIPT_PATH,
    ZENODO_RECORD_ID,
    canonical_json_bytes,
    identity,
    read_json,
)


def verify(native_root: Path, adapter: Path) -> dict[str, Any]:
    completion = read_json(PUBLIC_RECEIPT_PATH if native_root == DEFAULT_NATIVE else native_root / PUBLIC_RECEIPT_PATH.relative_to(DEFAULT_NATIVE))
    github = read_json(GITHUB_RECEIPT_PATH if native_root == DEFAULT_NATIVE else native_root / GITHUB_RECEIPT_PATH.relative_to(DEFAULT_NATIVE))
    zenodo = read_json(ZENODO_RECEIPT_PATH if native_root == DEFAULT_NATIVE else native_root / ZENODO_RECEIPT_PATH.relative_to(DEFAULT_NATIVE))

    if completion.get("status") != "COMPLETE_TRANSLATED_ADMITTED_PUBLISHED_AND_PUBLICLY_READ_BACK":
        raise ValueError("B95 completion receipt is not public-complete")
    if completion.get("boundary_id") != "R011-B039" or completion.get("complete_corpus") is not True:
        raise ValueError("B95 completion receipt identity drift")
    publication = completion.get("publication", {})
    if publication.get("github", {}).get("public") is not True or publication.get("zenodo", {}).get("public") is not True:
        raise ValueError("B95 completion receipt does not assert public mirrors")
    if github.get("status") != "PUBLIC_AND_ANONYMOUSLY_VERIFIED" or github.get("anonymous_public_byte_readback") is not True:
        raise ValueError("B95 GitHub receipt is not anonymously verified")
    if zenodo.get("status") != "PUBLIC_AND_ANONYMOUSLY_VERIFIED" or zenodo.get("anonymous_public_byte_readback") is not True:
        raise ValueError("B95 Zenodo receipt is not anonymously verified")
    if zenodo.get("access_right") != "open" or zenodo.get("record_id") != ZENODO_RECORD_ID:
        raise ValueError("B95 Zenodo public access identity drift")
    if github.get("release_id") != RELEASE_ID or zenodo.get("release_id") != RELEASE_ID:
        raise ValueError("B95 release identity drift")

    github_assets = github.get("ordered_assets", [])
    zenodo_assets = zenodo.get("ordered_files", [])
    if len(github_assets) != 9 or len(zenodo_assets) != 9:
        raise ValueError("B95 public release asset count drift")
    if github_assets != zenodo_assets:
        raise ValueError("B95 GitHub/Zenodo asset byte inventory drift")
    reader = completion.get("reader", {})
    if reader.get("pages") != 462 or reader.get("sha256") != github_assets[0].get("sha256"):
        raise ValueError("B95 reader public identity drift")

    preserved = adapter / "input/public-native-readback.json"
    if preserved.read_bytes() != (native_root / PUBLIC_RECEIPT_PATH.relative_to(DEFAULT_NATIVE)).read_bytes():
        raise ValueError("B95 adapter completion receipt is not byte-preserved")

    return {
        "schema": "b95-native-public-verification/1",
        "course_id": "B95",
        "release_id": RELEASE_ID,
        "result": "PASS",
        "anonymous": True,
        "credentials_used": False,
        "public_github": True,
        "public_zenodo": True,
        "zenodo_record_id": ZENODO_RECORD_ID,
        "asset_count": len(github_assets),
        "reader_pages": reader["pages"],
        "reader": {"filename": github_assets[0]["filename"], "bytes": github_assets[0]["bytes"], "sha256": github_assets[0]["sha256"]},
        "preserved_completion_receipt": identity(preserved, display_path="input/public-native-readback.json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    args = parser.parse_args()
    result = verify(args.native_root.resolve(), args.adapter.resolve())
    print(canonical_json_bytes(result).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"B95 native/public verification failed: {error}")
