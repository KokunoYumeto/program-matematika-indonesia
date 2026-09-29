#!/usr/bin/env python3
"""Reseal or verify unit manifests after the presentation-only nav overlay."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


def identity(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    return str(len(data)), hashlib.sha256(data).hexdigest()


def expected(manifest: Path) -> tuple[list[dict[str, str]], bytes]:
    with manifest.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    rebuilt = []
    for row in rows:
        target = (manifest.parent / row["path"]).resolve()
        target.relative_to(manifest.parent.resolve())
        size, digest = identity(target)
        rebuilt.append({"path": row["path"], "bytes": size, "sha256": digest})
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=("path", "bytes", "sha256"), delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rebuilt)
    return rebuilt, output.getvalue().encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("mode", choices=("reseal", "check")); parser.add_argument("root", type=Path); args = parser.parse_args()
    manifests = sorted(args.root.rglob("PACKAGE_MANIFEST.tsv"))
    if not manifests: raise RuntimeError("no unit manifests found")
    files = 0
    for manifest in manifests:
        rows, data = expected(manifest); files += len(rows)
        if args.mode == "reseal": manifest.write_bytes(data)
        elif manifest.read_bytes() != data: raise RuntimeError(f"stale manifest: {manifest}")
    print(json.dumps({"mode": args.mode, "manifests": len(manifests), "bound_files": files}, sort_keys=True))
    return 0


if __name__ == "__main__": raise SystemExit(main())
