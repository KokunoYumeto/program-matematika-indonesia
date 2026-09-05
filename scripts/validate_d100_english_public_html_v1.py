#!/usr/bin/env python3
"""Validate the D100 English reader plus its central navigation shell."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from validate_d10_public_html_v1 import (
    FileFact,
    aggregate_sha256,
    fact_map,
    inventory,
    is_safe_relative_path,
    sha256_file,
)
from validate_d120_public_html_v1 import (
    D120HTMLParser,
    css_imports,
    css_urls,
    is_external_runtime_url,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = REPO_ROOT.parents[2]
OWNER_ROOT = WORKSPACE_ROOT / "04_mirrors" / "id" / "algebraic-geometry-bridge-id"
DEFAULT_SOURCE = OWNER_ROOT / "build" / "english" / "docs-en-v1.0.0"
COURSE_ROOT = REPO_ROOT / "docs" / "en" / "courses" / "D100"
DEFAULT_DESTINATION = COURSE_ROOT / "reader"
DEFAULT_MANIFEST = COURSE_ROOT / "D100_ENGLISH_READER_MIRROR_MANIFEST_V1.json"
DEFAULT_RECEIPT = COURSE_ROOT / "D100_ENGLISH_READER_MIRROR_RECEIPT_V1.json"

SOURCE_COMMIT = "93dbf3b19907e9e13d42c8e342b449ebd0afc635"
SOURCE_TREE = "bbad2aaddef6af27eb3563be2e01e252afe0edfc"
EXPECTED_FILES = 474
EXPECTED_BYTES = 50_946_101
EXPECTED_HTML_FILES = 4
EXPECTED_AGGREGATE_SHA256 = "d9dd8b8c4358e38e7cd05b570899ae211fd24c39e04f746e571d1af92be59508"
EXPECTED_PUBLIC_MANIFEST_BYTES = 3_995
EXPECTED_PUBLIC_MANIFEST_SHA256 = "6bd23d544dc759292205edd8d5c937f434896e17bd351ab39e0a4eea1fb6fb9e"
EXPECTED_INVENTORY_BYTES = 83_610
EXPECTED_INVENTORY_SHA256 = "517ea1c66cfd64849321d743715d2646b28ca84f5a835593569794164d26df16"
EXPECTED_ENTRYPOINTS = {
    "index.html": (1_120, "d316fafa4e8ca49006ad5051d5b950d0029756d63c5642269826d8f0a890f019"),
    "ak.html": (4_915_565, "92e0db157501daff37b452d5e77220b66a6c16d99fdd09784364cc752dcd46e5"),
    "bgk.html": (4_343_251, "cfc5289c2cf05e489d5cfbeb4ba4f7358edfdef81a805642a1dc9d488ca1a3aa"),
    "companion.html": (1_487_123, "f49a5bfb33757c63591dd05e794f855938c5f98f1d4e130f67cc1a63aa16d549"),
}
CENTRAL_PROGRAM_HREF = "../../../#course-D100"
CENTRAL_PROGRAM_LABEL = "Full mathematics program"
PROGRAM_NAVIGATION_MARKER = 'data-program-navigation="v1"'
PROGRAM_RETURN = (
    f'<p class="program-return"><a data-program-home href="{CENTRAL_PROGRAM_HREF}">'
    f'← {CENTRAL_PROGRAM_LABEL}</a></p>'
)
SKIP_LINK = '<a class="skip-link" href="#main-content">Skip to main content</a>'
NAVIGATION_HTML_PATHS = frozenset(EXPECTED_ENTRYPOINTS)
NAVIGATION_CSS_PATH = "reader.css"
NAVIGATION_CSS = """

/* Central-program navigation shell; the mathematical reader body is unchanged. */
.program-navigation {
  margin: 0 0 1.25rem;
  padding: .7rem .9rem;
  border: 1px solid var(--rule);
  border-radius: .35rem;
  background: var(--panel);
  font-family: system-ui, sans-serif;
  font-size: .9rem;
}
.program-navigation a, .program-return a { font-weight: 700; }
@media print { .program-navigation, .program-return { display: none; } }
"""
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def centralized_payload(relative: str, source_bytes: bytes) -> bytes:
    """Add only the central-site navigation shell to frozen reader bytes."""
    if relative in NAVIGATION_HTML_PATHS:
        text = source_bytes.decode("utf-8")
        if PROGRAM_NAVIGATION_MARKER in text or PROGRAM_RETURN in text:
            raise ValueError(f"D100 English source unexpectedly contains central navigation: {relative}")
        if text.count(SKIP_LINK) != 1 or text.count("</footer>") != 1:
            raise ValueError(f"D100 English navigation injection anchors changed: {relative}")
        contents = (
            ' · <a data-reader-contents href="index.html">Algebraic Geometry reader home</a>'
            if relative != "index.html"
            else ""
        )
        navigation = (
            '<nav class="program-navigation" data-program-navigation="v1" aria-label="Program navigation">'
            f'<a data-program-home href="{CENTRAL_PROGRAM_HREF}">← {CENTRAL_PROGRAM_LABEL}</a>'
            f'{contents}</nav>'
        )
        text = text.replace(SKIP_LINK, SKIP_LINK + "\n" + navigation, 1)
        text = text.replace("</footer>", PROGRAM_RETURN + "\n</footer>", 1)
        return text.encode("utf-8")
    if relative == NAVIGATION_CSS_PATH:
        text = source_bytes.decode("utf-8")
        marker = "/* Central-program navigation shell;"
        if marker in text:
            raise ValueError("D100 English source unexpectedly contains central navigation CSS")
        return (text.rstrip("\r\n") + NAVIGATION_CSS).encode("utf-8")
    return source_bytes


def expected_destination_inventory(source: Path) -> list[FileFact]:
    rows: list[FileFact] = []
    for fact in inventory(source):
        data = source.joinpath(*fact.path.split("/")).read_bytes()
        target = centralized_payload(fact.path, data)
        rows.append(FileFact(fact.path, len(target), sha256_bytes(target)))
    return rows


def validate_destination_overlay(source: Path, destination: Path) -> tuple[list[FileFact], list[dict[str, object]]]:
    source_facts = inventory(source)
    destination_facts = inventory(destination)
    expected = expected_destination_inventory(source)
    if destination_facts != expected:
        raise ValueError("D100 English central reader differs from the deterministic navigation-overlay projection")
    source_by_path = fact_map(source_facts)
    destination_by_path = fact_map(destination_facts)
    transformations: list[dict[str, object]] = []
    for relative in sorted((*NAVIGATION_HTML_PATHS, NAVIGATION_CSS_PATH)):
        before = source_by_path[relative]
        after = destination_by_path[relative]
        transformations.append({
            "path": relative,
            "operation": "add_central_program_navigation" if relative.endswith(".html") else "add_central_navigation_styles",
            "source_bytes": before.bytes,
            "source_sha256": before.sha256,
            "target_bytes": after.bytes,
            "target_sha256": after.sha256,
        })
    return destination_facts, transformations


def read_json(path: Path, context: str) -> dict[str, object]:
    if not path.is_file():
        raise ValueError(f"{context} is missing: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a JSON object")
    return value


def validate_source_inventory(root: Path) -> tuple[list[object], dict[str, object], dict[str, object]]:
    facts = inventory(root)
    if len(facts) != EXPECTED_FILES:
        raise ValueError(f"D100 English reader file count {len(facts)} != {EXPECTED_FILES}")
    if sum(fact.bytes for fact in facts) != EXPECTED_BYTES:
        raise ValueError("D100 English reader total bytes changed")
    if aggregate_sha256(facts) != EXPECTED_AGGREGATE_SHA256:
        raise ValueError("D100 English reader aggregate SHA-256 changed")
    if sum(fact.path.endswith(".html") for fact in facts) != EXPECTED_HTML_FILES:
        raise ValueError("D100 English HTML route count changed")

    by_path = fact_map(facts)
    for name, (expected_bytes, expected_sha256) in EXPECTED_ENTRYPOINTS.items():
        fact = by_path.get(name)
        if fact is None or fact.bytes != expected_bytes or fact.sha256 != expected_sha256:
            raise ValueError(f"D100 English entrypoint identity changed: {name}")

    public_manifest_path = root / "public-manifest.json"
    inventory_path = root / "sha256-inventory.json"
    if (
        public_manifest_path.stat().st_size != EXPECTED_PUBLIC_MANIFEST_BYTES
        or sha256_file(public_manifest_path) != EXPECTED_PUBLIC_MANIFEST_SHA256
    ):
        raise ValueError("D100 English public manifest identity changed")
    if (
        inventory_path.stat().st_size != EXPECTED_INVENTORY_BYTES
        or sha256_file(inventory_path) != EXPECTED_INVENTORY_SHA256
    ):
        raise ValueError("D100 English SHA-256 inventory identity changed")

    public_manifest = read_json(public_manifest_path, "D100 English public manifest")
    if public_manifest.get("schema") != "d100-en-github-pages-stage-v1" or public_manifest.get("status") != "PASS":
        raise ValueError("D100 English public manifest state changed")
    reader_checks = public_manifest.get("reader_checks")
    if not isinstance(reader_checks, dict) or reader_checks.get("external_render_dependencies") != 0:
        raise ValueError("D100 English source manifest does not prove a dependency-free reader")
    if public_manifest.get("entrypoint") != "index.html":
        raise ValueError("D100 English source entrypoint changed")

    source_inventory = read_json(inventory_path, "D100 English SHA-256 inventory")
    rows = source_inventory.get("files")
    if source_inventory.get("schema") != "d100-en-public-sha256-inventory-v1" or not isinstance(rows, list):
        raise ValueError("D100 English SHA-256 inventory schema changed")
    if len(rows) != EXPECTED_FILES - 1:
        raise ValueError("D100 English SHA-256 inventory row count changed")
    expected: dict[str, tuple[int, str]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("D100 English SHA-256 inventory contains a non-object row")
        path = row.get("path")
        size = row.get("bytes")
        digest = row.get("sha256")
        if (
            not isinstance(path, str)
            or not is_safe_relative_path(path)
            or path == "sha256-inventory.json"
            or not isinstance(size, int)
            or size < 0
            or not isinstance(digest, str)
            or not HEX_SHA256.fullmatch(digest)
            or path in expected
        ):
            raise ValueError(f"invalid D100 English SHA-256 inventory row: {row!r}")
        expected[path] = (size, digest)
    actual = {
        fact.path: (fact.bytes, fact.sha256)
        for fact in facts
        if fact.path != "sha256-inventory.json"
    }
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        changed = sorted(path for path in set(actual) & set(expected) if actual[path] != expected[path])
        raise ValueError(
            f"D100 English inventory closure differs; missing={missing}, extra={extra}, changed={changed}"
        )
    return facts, public_manifest, source_inventory


def validate_pinned_git_tree(root: Path, facts: list[object]) -> dict[str, object]:
    tree_row = subprocess.check_output(
        ["git", "-C", str(OWNER_ROOT), "ls-tree", SOURCE_COMMIT, "docs/en"],
        text=True,
        encoding="utf-8",
    ).strip()
    if f"tree {SOURCE_TREE}\tdocs/en" not in tree_row:
        raise ValueError("D100 English pinned source tree changed")
    raw = subprocess.check_output(
        ["git", "-C", str(OWNER_ROOT), "ls-tree", "-r", "-z", SOURCE_COMMIT, "--", "docs/en"]
    )
    remote: dict[str, str] = {}
    for row in raw.split(b"\0"):
        if not row:
            continue
        metadata, name = row.split(b"\t", 1)
        _mode, object_type, object_id = metadata.split()
        if object_type != b"blob":
            raise ValueError("D100 English pinned tree contains a non-blob entry")
        decoded = name.decode("utf-8")
        prefix = "docs/en/"
        if not decoded.startswith(prefix):
            raise ValueError(f"D100 English pinned path escaped its root: {decoded}")
        remote[decoded[len(prefix):]] = object_id.decode("ascii")
    if set(remote) != {fact.path for fact in facts}:
        raise ValueError("D100 English pinned Git tree and source inventory paths differ")
    for fact in facts:
        data = root.joinpath(*fact.path.split("/")).read_bytes()
        if git_blob_sha1(data) != remote[fact.path]:
            raise ValueError(f"D100 English source differs from pinned Git blob: {fact.path}")
    return {"commit": SOURCE_COMMIT, "tree": SOURCE_TREE, "files_checked": len(remote)}


def parse_html(path: Path) -> D120HTMLParser:
    parser = D120HTMLParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def local_target(root: Path, current_file: Path, raw_url: str) -> tuple[Path | None, str | None, bool]:
    value = raw_url.strip()
    if not value or value.lower().startswith(("data:", "javascript:", "mailto:", "tel:")):
        return None, None, False
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or value.startswith("//"):
        return None, None, True
    decoded = unquote(parsed.path)
    if decoded.startswith("/"):
        raise ValueError(f"D100 English reader contains a root-absolute local path: {value}")
    if not decoded:
        target = current_file
    else:
        pure = PurePosixPath(decoded)
        candidate = (current_file.parent / Path(*pure.parts)).resolve()
        if not candidate.is_relative_to(root.resolve()):
            raise ValueError(f"D100 English reader link escaped its root: {value}")
        target = candidate
    if target.is_dir():
        target = target / "index.html"
    return target, unquote(parsed.fragment) if parsed.fragment else None, False


def validate_links(
    root: Path,
    facts: list[object],
    *,
    require_program_navigation: bool = False,
) -> dict[str, object]:
    by_path = fact_map(facts)
    html_parsers: dict[str, D120HTMLParser] = {}
    for fact in facts:
        if fact.path.endswith(".html"):
            parser = parse_html(root.joinpath(*fact.path.split("/")))
            if not parser.html_langs or any(not value.lower().startswith("en") for value in parser.html_langs):
                raise ValueError(f"D100 English HTML language metadata changed: {fact.path}")
            html_parsers[fact.path] = parser

    local_references = 0
    fragment_references = 0
    external_references = 0
    external_runtime: list[dict[str, str]] = []
    runtime_references = 0
    program_navigation_files: list[str] = []
    for relative, parser in html_parsers.items():
        current = root.joinpath(*relative.split("/"))
        program_links = sum(
            value.strip() == CENTRAL_PROGRAM_HREF
            for _kind, value in parser.references
        )
        if require_program_navigation:
            if program_links < 2:
                raise ValueError(f"D100 English reader lacks top-and-bottom program navigation: {relative}")
            program_navigation_files.append(relative)
        for kind, value in parser.runtime_references:
            if is_external_runtime_url(value):
                external_runtime.append({"file": relative, "kind": kind, "url": value})
            elif value.strip() and not value.lower().startswith("data:"):
                runtime_references += 1
        for _kind, value in parser.references:
            if value.strip() == CENTRAL_PROGRAM_HREF:
                continue
            target, fragment, external = local_target(root, current, value)
            if external:
                external_references += 1
                continue
            if target is None:
                continue
            target_relative = target.relative_to(root).as_posix()
            if target_relative not in by_path:
                raise ValueError(f"D100 English reader has a missing local target: {relative} -> {value}")
            local_references += 1
            if fragment and target_relative.endswith(".html"):
                target_parser = html_parsers.get(target_relative)
                if target_parser is None:
                    target_parser = parse_html(target)
                    html_parsers[target_relative] = target_parser
                if fragment not in target_parser.anchors:
                    raise ValueError(f"D100 English reader has a missing fragment: {relative} -> {value}")
                fragment_references += 1

    css_references = 0
    for fact in facts:
        if not fact.path.endswith(".css"):
            continue
        current = root.joinpath(*fact.path.split("/"))
        text = current.read_text(encoding="utf-8")
        for value in [*css_urls(text), *css_imports(text)]:
            if is_external_runtime_url(value):
                external_runtime.append({"file": fact.path, "kind": "css", "url": value})
                continue
            target, _fragment, external = local_target(root, current, value)
            if external:
                external_runtime.append({"file": fact.path, "kind": "css", "url": value})
            elif target is not None:
                relative_target = target.relative_to(root).as_posix()
                if relative_target not in by_path:
                    raise ValueError(f"D100 English CSS has a missing local target: {fact.path} -> {value}")
                css_references += 1
    if external_runtime:
        raise ValueError(f"D100 English reader has external runtime dependencies: {external_runtime[:5]}")
    return {
        "html_files": len(html_parsers),
        "local_references_checked": local_references,
        "fragment_references_checked": fragment_references,
        "runtime_references_checked": runtime_references,
        "css_references_checked": css_references,
        "external_references_observed": external_references,
        "external_runtime_dependencies": 0,
        "portable_subdirectory_links": True,
        "program_navigation_href": CENTRAL_PROGRAM_HREF if require_program_navigation else None,
        "program_navigation_files": sorted(program_navigation_files),
        "program_navigation_files_checked": len(program_navigation_files),
        "every_html_document_links_to_program_home": (
            not require_program_navigation or len(program_navigation_files) == len(html_parsers)
        ),
    }


def validate(
    source: Path,
    destination: Path,
    manifest_path: Path,
) -> dict[str, object]:
    source_facts, public_manifest, _source_inventory = validate_source_inventory(source)
    git_tree = validate_pinned_git_tree(source, source_facts)
    destination_facts, transformations = validate_destination_overlay(source, destination)
    links = validate_links(destination, destination_facts, require_program_navigation=True)
    manifest = read_json(manifest_path, "D100 English central mirror manifest")
    if manifest.get("schema") != "d100-english-reader-mirror-manifest-v1":
        raise ValueError("D100 English central mirror manifest schema changed")
    if manifest.get("course_id") != "D100" or manifest.get("locale") != "en":
        raise ValueError("D100 English central mirror manifest identity changed")
    reader = manifest.get("reader")
    if not isinstance(reader, dict) or reader.get("files") != [fact.as_dict() for fact in destination_facts]:
        raise ValueError("D100 English central mirror manifest file closure changed")
    if (
        reader.get("file_count") != len(destination_facts)
        or reader.get("bytes") != sum(fact.bytes for fact in destination_facts)
        or reader.get("aggregate_sha256") != aggregate_sha256(destination_facts)
    ):
        raise ValueError("D100 English central mirror manifest aggregate changed")
    overlay = manifest.get("central_navigation_overlay")
    if not isinstance(overlay, dict) or overlay.get("transformations") != transformations:
        raise ValueError("D100 English central navigation overlay binding changed")
    if overlay.get("program_home_href") != CENTRAL_PROGRAM_HREF:
        raise ValueError("D100 English central program-home route changed")
    source_authority = manifest.get("source_authority")
    if not isinstance(source_authority, dict) or source_authority.get("source_commit") != SOURCE_COMMIT or source_authority.get("source_tree") != SOURCE_TREE:
        raise ValueError("D100 English central mirror source authority changed")
    source_manifest = source_authority.get("public_manifest")
    source_inventory = source_authority.get("sha256_inventory")
    if not isinstance(source_manifest, dict) or source_manifest.get("sha256") != EXPECTED_PUBLIC_MANIFEST_SHA256:
        raise ValueError("D100 English public-manifest binding changed")
    if not isinstance(source_inventory, dict) or source_inventory.get("sha256") != EXPECTED_INVENTORY_SHA256:
        raise ValueError("D100 English inventory binding changed")
    if public_manifest.get("html_tree", {}).get("closure_sha256") != "b3280485a41236908e19406e9f3ed0d0f9b32ae9733803893e31c724be031474":
        raise ValueError("D100 English source HTML-tree closure changed")
    return {
        "status": "pass",
        "source_destination_byte_identity": False,
        "source_destination_navigation_overlay": True,
        "transformed_files": len(transformations),
        "reader": {
            "file_count": len(destination_facts),
            "bytes": sum(fact.bytes for fact in destination_facts),
            "html_files": sum(fact.path.endswith(".html") for fact in destination_facts),
            "aggregate_sha256": aggregate_sha256(destination_facts),
        },
        "links": links,
        "pinned_git_tree": git_tree,
        "unsafe_paths": 0,
        "symlinks": 0,
    }


def validate_receipt(
    receipt_path: Path,
    source: Path,
    destination: Path,
    manifest_path: Path,
    validation: dict[str, object],
) -> None:
    receipt = read_json(receipt_path, "D100 English central mirror receipt")
    if receipt.get("schema") != "d100-english-reader-mirror-receipt-v1" or receipt.get("status") != "pass":
        raise ValueError("D100 English central mirror receipt state changed")
    if receipt.get("course_id") != "D100" or receipt.get("locale") != "en":
        raise ValueError("D100 English central mirror receipt identity changed")
    destination_row = receipt.get("destination")
    if not isinstance(destination_row, dict):
        raise ValueError("D100 English central mirror receipt lacks destination facts")
    destination_facts = inventory(destination)
    if destination_row != {
        "path": destination.relative_to(REPO_ROOT).as_posix(),
        "entrypoint": destination.joinpath("index.html").relative_to(REPO_ROOT).as_posix(),
        "file_count": len(destination_facts),
        "bytes": sum(fact.bytes for fact in destination_facts),
        "aggregate_sha256": aggregate_sha256(destination_facts),
    }:
        raise ValueError("D100 English central mirror receipt destination changed")
    manifest_row = receipt.get("manifest")
    if not isinstance(manifest_row, dict) or manifest_row != {
        "path": manifest_path.relative_to(REPO_ROOT).as_posix(),
        "bytes": manifest_path.stat().st_size,
        "sha256": sha256_file(manifest_path),
    }:
        raise ValueError("D100 English central mirror receipt manifest binding changed")
    if receipt.get("validation") != validation:
        raise ValueError("D100 English central mirror receipt validation result is stale")
    scripts = receipt.get("scripts")
    if not isinstance(scripts, list) or len(scripts) != 2:
        raise ValueError("D100 English central mirror receipt script closure changed")
    for row in scripts:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise ValueError("D100 English central mirror receipt has an invalid script row")
        path = REPO_ROOT.joinpath(*row["path"].split("/"))
        if path.stat().st_size != row.get("bytes") or sha256_file(path) != row.get("sha256"):
            raise ValueError(f"D100 English central mirror receipt script binding changed: {row.get('path')}")
    source_row = receipt.get("source")
    if not isinstance(source_row, dict) or source_row.get("source_commit") != SOURCE_COMMIT or source_row.get("source_tree") != SOURCE_TREE:
        raise ValueError("D100 English central mirror receipt source binding changed")
    validate_destination_overlay(source, destination)
    if receipt.get("invariants") != {
        "source_destination_byte_identity": False,
        "source_destination_navigation_overlay": True,
        "source_inventory_closure_preserved": True,
        "component_rights_preserved": True,
        "local_render_dependencies_complete": True,
        "portable_subdirectory_links": True,
        "every_reader_entrypoint_links_to_program_home": True,
        "every_reader_html_document_links_to_program_home": True,
        "semantic_body_rewritten": False,
    }:
        raise ValueError("D100 English central mirror receipt invariants changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    try:
        result = validate(args.source.resolve(), args.destination.resolve(), args.manifest.resolve())
        validate_receipt(
            args.receipt.resolve(),
            args.source.resolve(),
            args.destination.resolve(),
            args.manifest.resolve(),
            result,
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        print(f"D100 English public HTML validation: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
