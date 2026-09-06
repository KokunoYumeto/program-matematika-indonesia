#!/usr/bin/env python3
"""Validate D110 upstream identity, offline link closure, and navigation contract."""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
import sys
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from build_mirror import (
    COMMIT,
    HERE,
    MATHJAX_EXTERNAL_SRC,
    MATHJAX_LOCAL_SRC,
    MATHJAX_VERSION,
    REPO,
    REPO_ROOT,
    TARGET,
    TREE,
    git_blob_sha,
)


TEXT_RIGHTS_NOTICE = "Copyright 2020-2025, Jeremy Avigad, Patrick Massot. Text licensed under CC BY 4.0."


class References(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value for key, value in attrs if value is not None}
        if "id" in values:
            self.ids.add(values["id"])
        if tag.lower() == "a" and "name" in values:
            self.ids.add(values["name"])
        for attr in ("href", "src", "data", "poster"):
            if attr in values:
                self.refs.append((tag.lower(), attr, values[attr]))
        if "srcset" in values:
            for candidate in values["srcset"].split(","):
                value = candidate.strip().split()[0] if candidate.strip() else ""
                if value:
                    self.refs.append((tag.lower(), "srcset", value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recover_upstream_html(data: bytes) -> bytes:
    """Reverse only the offline MathJax rewrite to recover pinned HTML."""
    return data.replace(MATHJAX_LOCAL_SRC, MATHJAX_EXTERNAL_SRC)


def local_target(source_rel: str, value: str) -> tuple[str | None, str | None]:
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or value.startswith("//"):
        return None, None
    if parsed.path.startswith("/"):
        return "__unexpected_root_absolute__", parsed.fragment or None
    decoded = unquote(parsed.path)
    if not decoded:
        return source_rel, parsed.fragment or None
    base = posixpath.dirname(source_rel)
    resolved = posixpath.normpath(posixpath.join(base, decoded))
    return resolved, parsed.fragment or None


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    manifest = json.loads((HERE / "upstream-inventory.json").read_text(encoding="utf-8"))
    if (manifest["repository"], manifest["commit"], manifest["tree"]) != (REPO, COMMIT, TREE):
        errors.append("upstream binding metadata mismatch")

    expected = {row["target_path"]: row for row in manifest["files"]}
    vendor_rows = manifest["vendored_dependencies"]["mathjax"]["files"]
    expected_vendor = {row["target_path"]: row for row in vendor_rows}
    actual_files = sorted(p for p in TARGET.rglob("*") if p.is_file())
    actual_rel = {p.relative_to(TARGET).as_posix() for p in actual_files}
    missing = sorted(set(expected) - actual_rel)
    unexpected = sorted(actual_rel - set(expected) - set(expected_vendor) - {"UPSTREAM.md"})
    if missing:
        errors.append(f"missing selected upstream files: {missing}")
    if unexpected:
        errors.append(f"unexpected mirror files: {unexpected}")
    missing_vendor = sorted(set(expected_vendor) - actual_rel)
    if missing_vendor:
        errors.append(f"missing vendored dependency files: {missing_vendor}")
    for rel, row in sorted(expected_vendor.items()):
        path = TARGET / Path(PurePosixPath(rel))
        if path.is_file() and (path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]):
            errors.append(f"vendored dependency byte/hash mismatch: {rel}")

    html_docs: dict[str, References] = {}
    external_resource_refs: list[dict[str, str]] = []
    external_anchor_refs: list[dict[str, str]] = []
    local_ref_count = 0
    fragment_ref_count = 0
    css_ref_count = 0

    for rel, row in sorted(expected.items()):
        path = TARGET / Path(PurePosixPath(rel))
        if not path.is_file():
            continue
        mirrored = path.read_bytes()
        if len(mirrored) != row["mirrored_bytes"] or hashlib.sha256(mirrored).hexdigest() != row["mirrored_sha256"]:
            errors.append(f"mirrored byte/hash mismatch: {rel}")
        source = recover_upstream_html(mirrored) if rel.endswith(".html") else mirrored
        if len(source) != row["source_bytes"] or hashlib.sha256(source).hexdigest() != row["source_sha256"]:
            errors.append(f"recovered source SHA-256 mismatch: {rel}")
        if git_blob_sha(source) != row["git_blob_sha1"]:
            errors.append(f"recovered Git blob mismatch: {rel}")

        if rel.endswith(".html"):
            text = mirrored.decode("utf-8")
            parser = References()
            parser.feed(text)
            html_docs[rel] = parser
            if "D110_PROGRAM_NAV_" in text or "d110-program-nav" in text:
                errors.append(f"{rel}: legacy D110 navigation residue remains")
            if "data-central-surface-navigation" in text:
                errors.append(f"{rel}: coordinator-owned standard navigation was injected prematurely")
            if TEXT_RIGHTS_NOTICE not in text:
                errors.append(f"{rel}: rendered CC BY 4.0 text notice missing")
            expected_localized = bool(row.get("mathjax_localized"))
            if (MATHJAX_LOCAL_SRC.decode() in text) != expected_localized:
                errors.append(f"{rel}: local MathJax rewrite retention mismatch")
            if MATHJAX_EXTERNAL_SRC.decode() in text:
                errors.append(f"{rel}: remote MathJax dependency remains")

    for rel, parser in html_docs.items():
        for tag, attr, value in parser.refs:
            parsed = urlsplit(value)
            if parsed.scheme in {"http", "https"} or parsed.netloc or value.startswith("//"):
                record = {"source": rel, "tag": tag, "attribute": attr, "url": value}
                if tag == "a" and attr == "href":
                    external_anchor_refs.append(record)
                else:
                    external_resource_refs.append(record)
                continue
            target_rel, fragment = local_target(rel, value)
            if target_rel is None:
                continue
            local_ref_count += 1
            if target_rel == "__unexpected_root_absolute__":
                errors.append(f"{rel}: unexpected root-absolute dependency {value}")
                continue
            target = TARGET / Path(PurePosixPath(target_rel))
            if not target.exists():
                errors.append(f"{rel}: broken local {tag}[{attr}] reference {value} -> {target_rel}")
                continue
            if fragment and target_rel.endswith(".html"):
                fragment_ref_count += 1
                destination = html_docs.get(target_rel)
                if destination is None:
                    destination = References()
                    destination.feed(target.read_text(encoding="utf-8"))
                    html_docs[target_rel] = destination
                if fragment not in destination.ids:
                    errors.append(f"{rel}: missing fragment #{fragment} in {target_rel}")

    css_url_pattern = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)", re.IGNORECASE)
    css_import_pattern = re.compile(r"@import\s+(?:url\()?\s*['\"]([^'\"]+)", re.IGNORECASE)
    for css in sorted(TARGET.rglob("*.css")):
        rel = css.relative_to(TARGET).as_posix()
        text = css.read_text(encoding="utf-8", errors="strict")
        refs = [m.group(2) for m in css_url_pattern.finditer(text)] + [m.group(1) for m in css_import_pattern.finditer(text)]
        for value in refs:
            if value.startswith("data:"):
                continue
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or value.startswith("//"):
                external_resource_refs.append({"source": rel, "tag": "css", "attribute": "url", "url": value})
                continue
            target_rel, _ = local_target(rel, value)
            if target_rel is not None:
                css_ref_count += 1
                if not (TARGET / Path(PurePosixPath(target_rel))).exists():
                    errors.append(f"{rel}: broken CSS reference {value} -> {target_rel}")

    if external_resource_refs:
        errors.append(f"external core resource dependencies found: {external_resource_refs}")
    if not (TARGET / "LICENSE").read_text(encoding="utf-8").startswith("                                 Apache License"):
        errors.append("repository Apache-2.0 LICENSE content not detected")
    if not (TARGET / "_vendor" / "mathjax" / "LICENSE").read_text(encoding="utf-8").startswith("\n                                 Apache License"):
        errors.append("vendored MathJax Apache-2.0 LICENSE content not detected")
    upstream_text = (TARGET / "UPSTREAM.md").read_text(encoding="utf-8")
    for required in (
        REPO,
        COMMIT,
        TREE,
        "Jeremy Avigad",
        "Patrick Massot",
        "Book text: CC BY 4.0",
        "Repository code and build assets: Apache License 2.0",
        "Retained components keep their embedded copyright and license notices",
        f"mathjax@{MATHJAX_VERSION}",
        "MathJax is Apache-2.0 licensed",
        "data-central-surface-navigation=v1",
    ):
        if required not in upstream_text:
            errors.append(f"UPSTREAM.md lacks required attribution/binding text: {required}")
    if (HERE / "package-replay.json").exists() or (HERE / "package").exists():
        errors.append("obsolete package artifact or package receipt remains")

    final_inventory = []
    for path in actual_files:
        final_inventory.append(
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    final_doc = {
        "schema": "d110-final-inventory-v1",
        "root": TARGET.relative_to(REPO_ROOT).as_posix(),
        "file_count": len(final_inventory),
        "html_count": len(html_docs),
        "bytes": sum(row["bytes"] for row in final_inventory),
        "files": final_inventory,
    }
    (HERE / "final-inventory.json").write_text(
        json.dumps(final_doc, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )

    report = {
        "schema": "d110-validation-report-v1",
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "upstream": {
            "repository": REPO,
            "commit": COMMIT,
            "tree": TREE,
            "blob_count": len(expected),
            "source_bytes": sum(row["source_bytes"] for row in expected.values()),
        },
        "mirror": {
            "file_count": len(final_inventory),
            "html_count": len(html_docs),
            "bytes": sum(row["bytes"] for row in final_inventory),
            "local_html_asset_references_checked": local_ref_count,
            "fragment_references_checked": fragment_ref_count,
            "css_references_checked": css_ref_count,
            "external_core_resource_dependencies": external_resource_refs,
            "external_anchor_count": len(external_anchor_refs),
            "external_anchor_urls": sorted({row["url"] for row in external_anchor_refs}),
        },
        "checks": {
            "complete_selected_inventory": not missing and not missing_vendor and not unexpected,
            "independent_upstream_html_recovery": not any("source" in error.lower() or "git blob" in error.lower() for error in errors),
            "relative_link_and_fragment_closure": not any("broken" in error.lower() or "missing fragment" in error.lower() for error in errors),
            "no_external_core_resource_dependencies": not external_resource_refs,
            "legacy_navigation_removed_and_admission_clear": not any("navigation" in error.lower() for error in errors),
            "local_mathjax_rewrite_retained": not any("mathjax dependency" in error.lower() or "rewrite retention" in error.lower() for error in errors),
            "component_scoped_rights_and_attribution": not any("license" in error.lower() or "upstream.md" in error.lower() or "cc by" in error.lower() for error in errors),
            "no_package_artifacts": not any("package" in error.lower() for error in errors),
        },
    }
    (HERE / "validation-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
