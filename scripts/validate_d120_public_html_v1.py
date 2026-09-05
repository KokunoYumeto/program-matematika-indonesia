#!/usr/bin/env python3
"""Validate D120's frozen reader body plus its central navigation shell."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from validate_d10_public_html_v1 import (
    FileFact,
    ReaderHTMLParser,
    aggregate_sha256,
    css_urls,
    fact_map,
    inventory,
    is_safe_relative_path,
    sha256_file,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OWNER_ROOT = REPO_ROOT.parents[1] / "01a0216a-4b9f-7d30-a376-60e4e3859979"
DEFAULT_SOURCE = OWNER_ROOT / "build" / "html"
DEFAULT_ARCHIVE = OWNER_ROOT / "release" / "o017-d120-id-2026.08.24-reader-html.zip"
DEFAULT_DESTINATION = REPO_ROOT / "docs" / "id-ID" / "courses" / "D120" / "reader"
DEFAULT_MANIFEST = (
    REPO_ROOT
    / "docs"
    / "id-ID"
    / "courses"
    / "D120"
    / "D120_READER_MIRROR_MANIFEST_V1.json"
)
DEFAULT_RECEIPT = (
    REPO_ROOT
    / "docs"
    / "id-ID"
    / "courses"
    / "D120"
    / "D120_READER_MIRROR_RECEIPT_V1.json"
)

EXPECTED_ARCHIVE_BYTES = 787_617
EXPECTED_ARCHIVE_SHA256 = "c47fb636c821d574cc987a39d512f608bc4796fe2c737d8d7d02b5d0540df7e9"
EXPECTED_RELEASE_MANIFEST_BYTES = 10_561
EXPECTED_RELEASE_MANIFEST_SHA256 = "89922b33b21fe423bd4323a414c1d970d594efd340656220b2be62279d2d6857"
EXPECTED_READER_FILES = 60
EXPECTED_READER_BYTES = 2_844_307
EXPECTED_HTML_FILES = 11
EXPECTED_ENTRYPOINT_BYTES = 36_311
EXPECTED_ENTRYPOINT_SHA256 = "91875291e302741f442fa98ebecc9539ac3de43b4dbfdb07ea34bb559f978a42"
CENTRAL_PROGRAM_HREF = "../../../../id/#course-D120"
PROGRAM_NAVIGATION_MARKER = 'data-program-navigation="v1"'
SKIP_LINK = '<a class="o017-skip-link" href="#quarto-document-content">Langsung ke isi utama</a>'
CSS_IMPORT_RE = re.compile(
    r"@import\s+(?:url\(\s*)?(['\"]?)([^'\"\)\s;]+)\1\s*\)?",
    re.IGNORECASE,
)


def css_imports(text: str) -> list[str]:
    return [match.group(2).strip() for match in CSS_IMPORT_RE.finditer(text)]


def is_external_runtime_url(value: str) -> bool:
    candidate = value.strip()
    if not candidate or candidate.lower().startswith("data:"):
        return False
    parsed = urlsplit(candidate)
    return bool(parsed.scheme or parsed.netloc or candidate.startswith("//"))


class D120HTMLParser(ReaderHTMLParser):
    """Track all links plus the subset that can load runtime resources."""

    def __init__(self) -> None:
        super().__init__()
        self.runtime_references: list[tuple[str, str]] = []
        self._style_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        super().handle_starttag(tag, attrs)
        tag = tag.lower()
        values = {key.lower(): value for key, value in attrs if value is not None}
        if tag == "style":
            self._style_depth += 1
        for key in ("src", "poster", "data"):
            if key in values:
                self.runtime_references.append((f"{tag}:{key}", values[key]))
        if "srcset" in values:
            for candidate in values["srcset"].split(","):
                url = candidate.strip().split(maxsplit=1)[0] if candidate.strip() else ""
                if url:
                    self.runtime_references.append((f"{tag}:srcset", url))
        if "style" in values:
            for url in [*css_urls(values["style"]), *css_imports(values["style"])]:
                self.runtime_references.append((f"{tag}:style", url))
        rel = {token.lower() for token in values.get("rel", "").split()}
        if tag == "link" and "stylesheet" in rel and "href" in values:
            self.runtime_references.append(("link:stylesheet", values["href"]))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "style" and self._style_depth:
            self._style_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._style_depth:
            for url in [*css_urls(data), *css_imports(data)]:
                self.runtime_references.append(("style:block", url))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def program_home_href(relative: str) -> str:
    depth = len(PurePosixPath(relative).parent.parts)
    return "../" * depth + CENTRAL_PROGRAM_HREF


def reader_contents_href(relative: str) -> str | None:
    depth = len(PurePosixPath(relative).parent.parts)
    return None if depth == 0 else "../" * depth


def navigation_fragments(relative: str) -> tuple[str, str]:
    href = program_home_href(relative)
    contents_href = reader_contents_href(relative)
    contents = (
        f' · <a data-reader-contents href="{contents_href}">Daftar isi pembaca</a>'
        if contents_href is not None
        else ""
    )
    navigation = (
        '<nav data-program-navigation="v1" aria-label="Navigasi program">'
        f'<a data-program-home href="{href}">← Kembali ke Program Matematika</a>'
        f'{contents}</nav>'
    )
    program_return = (
        f'<p data-program-return><a data-program-home href="{href}">'
        '← Kembali ke Program Matematika</a></p>'
    )
    return navigation, program_return


def centralized_payload(relative: str, source_bytes: bytes) -> bytes:
    if not relative.endswith(".html"):
        return source_bytes
    text = source_bytes.decode("utf-8")
    navigation, program_return = navigation_fragments(relative)
    if PROGRAM_NAVIGATION_MARKER in text or 'data-program-return' in text:
        raise ValueError("D120 source unexpectedly contains central navigation")
    if text.count(SKIP_LINK) != 1 or text.count("</body>") != 1:
        raise ValueError("D120 central navigation injection anchors changed")
    text = text.replace(SKIP_LINK, SKIP_LINK + "\n" + navigation, 1)
    text = text.replace("</body>", program_return + "\n</body>", 1)
    return text.encode("utf-8")


def expected_destination_inventory(source: Path) -> list[FileFact]:
    rows: list[FileFact] = []
    for fact in inventory(source):
        data = source.joinpath(*fact.path.split("/")).read_bytes()
        target = centralized_payload(fact.path, data)
        rows.append(FileFact(fact.path, len(target), sha256_bytes(target)))
    return rows


def validate_destination_overlay(source: Path, destination: Path) -> tuple[list[FileFact], list[dict[str, object]]]:
    expected = expected_destination_inventory(source)
    actual = inventory(destination)
    if actual != expected:
        raise ValueError("D120 central reader differs from the deterministic navigation-overlay projection")
    source_map = fact_map(inventory(source))
    target_map = fact_map(actual)
    transformations = []
    for relative in sorted(path for path in source_map if path.endswith(".html")):
        source_fact = source_map[relative]
        target_fact = target_map[relative]
        transformations.append({
            "path": relative,
            "operation": "add_central_program_navigation",
            "program_home_href": program_home_href(relative),
            "source_bytes": source_fact.bytes,
            "source_sha256": source_fact.sha256,
            "target_bytes": target_fact.bytes,
            "target_sha256": target_fact.sha256,
        })
    return actual, transformations


def release_manifest(archive: Path) -> dict[str, object]:
    if not archive.is_file():
        raise ValueError(f"D120 archive is missing: {archive}")
    if archive.stat().st_size != EXPECTED_ARCHIVE_BYTES:
        raise ValueError("D120 archive byte count changed")
    if sha256_file(archive) != EXPECTED_ARCHIVE_SHA256:
        raise ValueError("D120 archive SHA-256 changed")

    with zipfile.ZipFile(archive) as bundle:
        infos = bundle.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise ValueError("D120 archive contains duplicate paths")
        if any(info.is_dir() or not is_safe_relative_path(info.filename) for info in infos):
            raise ValueError("D120 archive contains a directory or unsafe path")
        if "RELEASE_MANIFEST.json" not in names:
            raise ValueError("D120 archive lacks RELEASE_MANIFEST.json")
        raw_manifest = bundle.read("RELEASE_MANIFEST.json")
        if len(raw_manifest) != EXPECTED_RELEASE_MANIFEST_BYTES:
            raise ValueError("D120 release manifest byte count changed")
        if sha256_bytes(raw_manifest) != EXPECTED_RELEASE_MANIFEST_SHA256:
            raise ValueError("D120 release manifest SHA-256 changed")
        data = json.loads(raw_manifest)
        if data.get("schema") != "o017-release-archive-manifest-v1":
            raise ValueError("D120 release manifest schema changed")
        if data.get("file_count") != EXPECTED_READER_FILES:
            raise ValueError("D120 release manifest file count changed")
        if data.get("total_uncompressed_bytes") != EXPECTED_READER_BYTES:
            raise ValueError("D120 release manifest total bytes changed")
        rows = data.get("files")
        if not isinstance(rows, list) or len(rows) != EXPECTED_READER_FILES:
            raise ValueError("D120 release manifest file rows are incomplete")
        row_names = [row.get("path") for row in rows]
        if len(row_names) != len(set(row_names)):
            raise ValueError("D120 release manifest contains duplicate paths")
        if set(names) != set(row_names) | {"RELEASE_MANIFEST.json"}:
            raise ValueError("D120 archive and release-manifest closure differ")
        for row in rows:
            name = row.get("path")
            if not isinstance(name, str) or not is_safe_relative_path(name):
                raise ValueError(f"D120 manifest path is unsafe: {name!r}")
            payload = bundle.read(name)
            if len(payload) != row.get("bytes") or sha256_bytes(payload) != row.get("sha256"):
                raise ValueError(f"D120 archive payload identity changed: {name}")
    return data


def validate_frozen_identity(root: Path, manifest: dict[str, object]) -> list[object]:
    facts = inventory(root)
    if len(facts) != EXPECTED_READER_FILES:
        raise ValueError(f"D120 reader file count {len(facts)} != {EXPECTED_READER_FILES}")
    if sum(fact.bytes for fact in facts) != EXPECTED_READER_BYTES:
        raise ValueError("D120 reader total bytes changed")
    if sum(fact.path.endswith(".html") for fact in facts) != EXPECTED_HTML_FILES:
        raise ValueError("D120 HTML route count changed")
    expected = {
        row["path"]: (row["bytes"], row["sha256"])
        for row in manifest["files"]
    }
    actual = {fact.path: (fact.bytes, fact.sha256) for fact in facts}
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        changed = sorted(path for path in set(actual) & set(expected) if actual[path] != expected[path])
        raise ValueError(
            f"D120 reader differs from release manifest; missing={missing}, extra={extra}, changed={changed}"
        )
    entrypoint = fact_map(facts).get("index.html")
    if (
        entrypoint is None
        or entrypoint.bytes != EXPECTED_ENTRYPOINT_BYTES
        or entrypoint.sha256 != EXPECTED_ENTRYPOINT_SHA256
    ):
        raise ValueError("D120 entrypoint identity changed")
    return facts


def resolve_local(root: Path, source_file: Path, raw_url: str) -> tuple[Path, str] | None:
    value = raw_url.strip()
    if not value:
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or value.startswith("//"):
        return None
    decoded = unquote(parsed.path)
    if not decoded:
        return source_file.resolve(), unquote(parsed.fragment)
    if decoded.startswith(("/", "\\")) or "\\" in decoded:
        raise ValueError(f"nonportable D120 URL in {source_file}: {raw_url!r}")
    target = source_file.parent.joinpath(*PurePosixPath(decoded).parts).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f"D120 URL escapes reader root in {source_file}: {raw_url!r}")
    if target.is_dir() or decoded.endswith("/"):
        target = target / "index.html"
    return target, unquote(parsed.fragment)


def validate_links(
    root: Path,
    facts: list[object],
    *,
    require_program_navigation: bool = True,
) -> dict[str, object]:
    parsers: dict[Path, ReaderHTMLParser] = {}
    local_refs = 0
    fragments = 0
    external_refs = 0
    css_refs = 0
    program_navigation_files: list[str] = []
    for fact in facts:
        path = root / PurePosixPath(fact.path)
        if fact.path.endswith(".html"):
            parser = D120HTMLParser()
            parser.feed(path.read_text(encoding="utf-8"))
            parser.close()
            if parser.html_langs != ["id-ID"]:
                raise ValueError(f"{fact.path}: expected exactly html lang=id-ID")
            expected_home = program_home_href(fact.path)
            if require_program_navigation:
                program_links = sum(raw_url.strip() == expected_home for _key, raw_url in parser.references)
                if program_links < 2 or PROGRAM_NAVIGATION_MARKER not in path.read_text(encoding="utf-8"):
                    raise ValueError(f"{fact.path}: lacks top-and-bottom program navigation")
                expected_contents = reader_contents_href(fact.path)
                if expected_contents is not None and not any(
                    raw_url.strip() == expected_contents for _key, raw_url in parser.references
                ):
                    raise ValueError(f"{fact.path}: lacks a reader-contents return link")
                program_navigation_files.append(fact.path)
            external_runtime = [
                (kind, url)
                for kind, url in parser.runtime_references
                if is_external_runtime_url(url)
            ]
            if external_runtime:
                raise ValueError(
                    f"{fact.path}: external runtime dependencies are forbidden: {external_runtime[:5]}"
                )
            parsers[path.resolve()] = parser
        elif fact.path.endswith(".css"):
            css_text = path.read_text(encoding="utf-8")
            for raw_url in dict.fromkeys([*css_urls(css_text), *css_imports(css_text)]):
                if raw_url.startswith("data:"):
                    continue
                if is_external_runtime_url(raw_url):
                    raise ValueError(f"{fact.path}: external CSS runtime dependency {raw_url!r}")
                resolved = resolve_local(root, path, raw_url)
                if resolved is None:
                    external_refs += 1
                    continue
                target, _fragment = resolved
                if not target.is_file():
                    raise ValueError(f"{fact.path}: missing CSS dependency {raw_url!r}")
                css_refs += 1

    for source_path, parser in parsers.items():
        source_relative = source_path.relative_to(root).as_posix()
        expected_home = program_home_href(source_relative)
        for _key, raw_url in parser.references:
            if raw_url.strip() == expected_home:
                continue
            parsed = urlsplit(raw_url.strip())
            if parsed.scheme or parsed.netloc or raw_url.strip().startswith("//"):
                external_refs += 1
                continue
            resolved = resolve_local(root, source_path, raw_url)
            if resolved is None:
                continue
            target, fragment = resolved
            if not target.is_file():
                raise ValueError(
                    f"{source_path.relative_to(root).as_posix()}: missing local dependency {raw_url!r}"
                )
            local_refs += 1
            if fragment:
                fragments += 1
                if target.suffix.lower() == ".html":
                    target_parser = parsers.get(target.resolve())
                    if target_parser is None or fragment not in target_parser.anchors:
                        raise ValueError(
                            f"{source_path.relative_to(root).as_posix()}: missing fragment #{fragment}"
                        )
    return {
        "html_files": len(parsers),
        "local_references_checked": local_refs,
        "fragment_references_checked": fragments,
        "css_references_checked": css_refs,
        "external_references_observed": external_refs,
        "external_runtime_dependencies": 0,
        "portable_subdirectory_links": True,
        "program_navigation_href": CENTRAL_PROGRAM_HREF if require_program_navigation else None,
        "program_navigation_files": program_navigation_files,
        "program_navigation_files_checked": len(program_navigation_files),
        "every_html_document_links_to_program_home": (
            not require_program_navigation or len(program_navigation_files) == len(parsers)
        ),
    }


def validate(source: Path, destination: Path, archive: Path, mirror_manifest: Path) -> dict[str, object]:
    release = release_manifest(archive)
    source_facts = validate_frozen_identity(source, release)
    destination_facts, transformations = validate_destination_overlay(source, destination)
    links = validate_links(destination, destination_facts)
    if not mirror_manifest.is_file():
        raise ValueError("D120 central mirror manifest is missing")
    data = json.loads(mirror_manifest.read_text(encoding="utf-8"))
    if data.get("schema") != "d120-reader-mirror-manifest-v1":
        raise ValueError("D120 central mirror manifest schema changed")
    reader = data.get("reader", {})
    if reader.get("file_count") != EXPECTED_READER_FILES:
        raise ValueError("D120 central mirror manifest count changed")
    if reader.get("bytes") != sum(fact.bytes for fact in destination_facts):
        raise ValueError("D120 central mirror manifest bytes changed")
    if reader.get("aggregate_sha256") != aggregate_sha256(destination_facts):
        raise ValueError("D120 central mirror manifest aggregate changed")
    if reader.get("files") != [fact.as_dict() for fact in destination_facts]:
        raise ValueError("D120 central mirror manifest file inventory changed")
    overlay = data.get("central_navigation_overlay")
    if not isinstance(overlay, dict) or overlay.get("transformations") != transformations:
        raise ValueError("D120 central navigation overlay binding changed")
    if overlay.get("program_home_href") != CENTRAL_PROGRAM_HREF:
        raise ValueError("D120 central program-home route changed")
    return {
        "status": "pass",
        "reader": {
            "file_count": len(destination_facts),
            "bytes": sum(fact.bytes for fact in destination_facts),
            "html_files": sum(fact.path.endswith(".html") for fact in destination_facts),
            "aggregate_sha256": aggregate_sha256(destination_facts),
            "source_destination_byte_identity": False,
            "source_destination_navigation_overlay": True,
        },
        "archive": {
            "bytes": archive.stat().st_size,
            "sha256": sha256_file(archive),
            "release_manifest_bytes": EXPECTED_RELEASE_MANIFEST_BYTES,
            "release_manifest_sha256": EXPECTED_RELEASE_MANIFEST_SHA256,
        },
        "links": links,
        "unsafe_paths": 0,
        "symlinks": 0,
    }


def validate_receipt(
    receipt_path: Path,
    source: Path,
    destination: Path,
    archive: Path,
    manifest_path: Path,
    validation: dict[str, object],
) -> None:
    if not receipt_path.is_file():
        raise ValueError("D120 central mirror receipt is missing")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    expected_keys = {
        "schema", "status", "course_id", "locale", "operation", "source",
        "destination", "manifest", "scripts", "validation", "invariants",
    }
    if set(receipt) != expected_keys:
        raise ValueError("D120 mirror receipt fields changed")
    if (
        receipt.get("schema") != "d120-reader-mirror-receipt-v1"
        or receipt.get("status") != "pass"
        or receipt.get("course_id") != "D120"
        or receipt.get("locale") != "id-ID"
        or receipt.get("operation") != "idempotent_stage_or_verify_with_navigation_overlay"
    ):
        raise ValueError("D120 mirror receipt identity changed")
    facts = inventory(destination)
    expected_destination = {
        "path": destination.relative_to(REPO_ROOT).as_posix(),
        "entrypoint": destination.joinpath("index.html").relative_to(REPO_ROOT).as_posix(),
        "file_count": len(facts),
        "bytes": sum(fact.bytes for fact in facts),
        "aggregate_sha256": aggregate_sha256(facts),
    }
    if receipt.get("destination") != expected_destination:
        raise ValueError("D120 mirror receipt destination facts changed")
    expected_manifest = {
        "path": manifest_path.relative_to(REPO_ROOT).as_posix(),
        "bytes": manifest_path.stat().st_size,
        "sha256": sha256_file(manifest_path),
    }
    if receipt.get("manifest") != expected_manifest:
        raise ValueError("D120 mirror receipt manifest facts changed")
    expected_source = {
        "repository": "https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id",
        "zenodo": "https://zenodo.org/records/22073823",
        "archive_url": "https://zenodo.org/records/22073823/files/o017-d120-id-2026.08.24-reader-html.zip?download=1",
        "archive_bytes": archive.stat().st_size,
        "archive_sha256": sha256_file(archive),
        "file_count": len(inventory(source)),
    }
    if receipt.get("source") != expected_source:
        raise ValueError("D120 mirror receipt source facts changed")
    expected_scripts = []
    for script in (Path(__file__).with_name("stage_d120_public_html_v1.py").resolve(), Path(__file__).resolve()):
        expected_scripts.append({
            "path": script.relative_to(REPO_ROOT).as_posix(),
            "bytes": script.stat().st_size,
            "sha256": sha256_file(script),
        })
    if receipt.get("scripts") != expected_scripts:
        raise ValueError("D120 mirror receipt script identities changed")
    if receipt.get("validation") != validation:
        raise ValueError("D120 mirror receipt validation result changed")
    if receipt.get("invariants") != {
        "source_destination_byte_identity": False,
        "source_destination_navigation_overlay": True,
        "release_manifest_closure_preserved": True,
        "component_rights_preserved": True,
        "local_render_dependencies_complete": True,
        "portable_subdirectory_links": True,
        "every_reader_entrypoint_links_to_program_home": True,
        "every_reader_html_document_links_to_program_home": True,
        "semantic_body_rewritten": False,
    }:
        raise ValueError("D120 mirror receipt invariants changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    try:
        result = validate(
            args.source.resolve(),
            args.destination.resolve(),
            args.archive.resolve(),
            args.manifest.resolve(),
        )
        validate_receipt(
            args.receipt.resolve(),
            args.source.resolve(),
            args.destination.resolve(),
            args.archive.resolve(),
            args.manifest.resolve(),
            result,
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(f"D120 public HTML validation: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
