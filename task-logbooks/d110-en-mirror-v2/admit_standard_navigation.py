#!/usr/bin/env python3
"""Remove the exact legacy D110 overlay while preserving offline MathJax."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

from build_mirror import (
    COMMIT,
    HERE,
    MATHJAX_EXTERNAL_SRC,
    MATHJAX_LOCAL_SRC,
    REPO,
    TARGET,
    TREE,
    git_blob_sha,
)


NAV_CSS = b"""<style data-d110-program-nav=\"v1\">
.d110-program-nav{box-sizing:border-box;width:100%;padding:.8rem 1rem;background:#172554;color:#f8fafc;font:600 15px/1.45 system-ui,-apple-system,Segoe UI,sans-serif;text-align:center;position:relative;z-index:1000}.d110-program-nav a{color:#fff;text-decoration:underline;text-underline-offset:.18em;margin:.2rem .45rem;display:inline-block}.d110-program-nav a.d110-authoritative{background:#fbbf24;color:#172554;text-decoration:none;padding:.35rem .65rem;border-radius:.25rem;font-weight:800}.d110-program-nav .d110-label{margin-right:.35rem}
</style>"""


def legacy_nav_block(position: str) -> bytes:
    label = "Top" if position == "TOP" else "Bottom"
    return (
        f"<!-- D110_PROGRAM_NAV_{position}_START -->\n".encode()
        + (NAV_CSS + b"\n" if position == "TOP" else b"")
        + f'<nav class="d110-program-nav" aria-label="D110 program navigation ({label.lower()})">\n'
          '  <span class="d110-label">D110 · Mathematics in Lean</span>\n'
          '  <a href="/en/#course-D110">English course card</a>\n'
          '  <a href="/id/#course-D110">Kartu kursus Indonesia</a>\n'
          '  <a href="/en/">English program</a>\n'
          '  <a href="/id/">Program Indonesia</a>\n'
          '  <a class="d110-authoritative" href="https://leanprover-community.github.io/mathematics_in_lean/">Authoritative original ↗</a>\n'
          '</nav>\n'.encode()
        + f"<!-- D110_PROGRAM_NAV_{position}_END -->".encode()
    )


TOP_WITH_PREFIX = b"\n" + legacy_nav_block("TOP")
BOTTOM_WITH_SUFFIX = legacy_nav_block("BOTTOM") + b"\n"
TEXT_RIGHTS_NOTICE = b"Copyright 2020-2025, Jeremy Avigad, Patrick Massot. Text licensed under CC BY 4.0."


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    manifest_path = HERE / "upstream-inventory.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest["repository"], manifest["commit"], manifest["tree"]) != (REPO, COMMIT, TREE):
        raise RuntimeError("pinned upstream binding mismatch")

    html_rows = [row for row in manifest["files"] if row["target_path"].endswith(".html")]
    if len(html_rows) != 16:
        raise RuntimeError(f"expected 16 pinned HTML rows, found {len(html_rows)}")

    admitted = []
    mathjax_pages = 0
    for row in sorted(html_rows, key=lambda item: item["target_path"]):
        rel = row["target_path"]
        path = TARGET / Path(PurePosixPath(rel))
        before = path.read_bytes()
        if len(before) != row["mirrored_bytes"] or sha256(before) != row["mirrored_sha256"]:
            raise RuntimeError(f"pre-admission mirror hash mismatch: {rel}")
        if before.count(TOP_WITH_PREFIX) != 1 or before.count(BOTTOM_WITH_SUFFIX) != 1:
            raise RuntimeError(f"exact legacy top/bottom blocks not found once each: {rel}")

        after = before.replace(TOP_WITH_PREFIX, b"", 1).replace(BOTTOM_WITH_SUFFIX, b"", 1)
        if b"D110_PROGRAM_NAV_" in after or b"d110-program-nav" in after:
            raise RuntimeError(f"legacy navigation residue remains: {rel}")
        if TEXT_RIGHTS_NOTICE not in after:
            raise RuntimeError(f"rendered CC BY 4.0 text notice missing: {rel}")

        localized_count = after.count(MATHJAX_LOCAL_SRC)
        if localized_count:
            mathjax_pages += 1
        recovered = after.replace(MATHJAX_LOCAL_SRC, MATHJAX_EXTERNAL_SRC)
        if recovered.count(MATHJAX_EXTERNAL_SRC) != localized_count:
            raise RuntimeError(f"MathJax reversal count mismatch: {rel}")
        if len(recovered) != row["source_bytes"] or sha256(recovered) != row["source_sha256"]:
            raise RuntimeError(f"independent upstream SHA-256 recovery failed: {rel}")
        if git_blob_sha(recovered) != row["git_blob_sha1"]:
            raise RuntimeError(f"independent upstream Git blob recovery failed: {rel}")

        path.write_bytes(after)
        row["mirrored_bytes"] = len(after)
        row["mirrored_sha256"] = sha256(after)
        row["navigation_injected"] = False
        row["mathjax_localized"] = bool(localized_count)
        admitted.append(
            {
                "path": rel,
                "legacy_bytes_removed": len(before) - len(after),
                "admitted_bytes": len(after),
                "admitted_sha256": sha256(after),
                "mathjax_rewrite_retained": bool(localized_count),
                "upstream_source_sha256": row["source_sha256"],
                "upstream_git_blob_sha1": row["git_blob_sha1"],
            }
        )

    if mathjax_pages != 11:
        raise RuntimeError(f"expected 11 localized MathJax pages, found {mathjax_pages}")

    manifest["schema"] = "d110-upstream-inventory-v2-admitted"
    manifest["source_html_count"] = len(html_rows)
    manifest["rights"] = {
        "book_text": "CC BY 4.0 per rendered copyright notice",
        "repository_code_and_build_assets": "Apache-2.0 under retained root LICENSE",
        "vendored_mathjax": "Apache-2.0 under _vendor/mathjax/LICENSE",
        "embedded_notices": "retained components keep their embedded notices",
    }
    manifest["admission"] = {
        "legacy_overlay": "D110_PROGRAM_NAV exact top/bottom blocks",
        "legacy_overlay_removed_from_html_count": len(admitted),
        "navigation_state": "clear for coordinator data-central-surface-navigation=v1 injection",
        "mathjax_rewrite_retained_html_count": mathjax_pages,
        "full_upstream_html_recovery_verified_count": len(admitted),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")

    report = {
        "schema": "d110-navigation-admission-v1",
        "passed": True,
        "repository": REPO,
        "commit": COMMIT,
        "tree": TREE,
        "html_count": len(admitted),
        "legacy_top_bottom_blocks_removed": len(admitted) * 2,
        "legacy_bytes_removed": sum(row["legacy_bytes_removed"] for row in admitted),
        "mathjax_rewrite_retained_html_count": mathjax_pages,
        "upstream_html_git_blobs_recovered_count": len(admitted),
        "pages": admitted,
    }
    (HERE / "admission-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({key: value for key, value in report.items() if key != "pages"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
