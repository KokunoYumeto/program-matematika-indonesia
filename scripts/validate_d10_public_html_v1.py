#!/usr/bin/env python3
"""Validate the D10 public HTML mirror plus its central navigation shell.

This validator is deliberately limited to the D10 reader subtree.  It checks
the native release manifest, source/destination byte identity, safe paths,
portable local links and fragments, and the component-specific licence files.
It performs no network requests and writes no files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


EXPECTED_ARCHIVE_BYTES = 15_167_715
EXPECTED_ARCHIVE_SHA256 = (
    "a0333dca723085e93d472b945a03758b133b05cbe5be3022133088e5c1f5ab00"
)
EXPECTED_READER_FILES = 138
EXPECTED_READER_BYTES = 15_166_155
EXPECTED_HTML_FILES = 98
EXPECTED_NATIVE_MANIFEST_BYTES = 13_343
EXPECTED_NATIVE_MANIFEST_SHA256 = (
    "5d7af8820f9c423b0f95a2cf3696963bdcfad2405ef668dd8a2f566d583267a4"
)
CENTRAL_PROGRAM_HREF = "../../../../id/#course-D10"
PROGRAM_NAVIGATION_MARKER = 'data-program-navigation="v1"'
SKIP_LINK = '<a class="skip-link" href="#isi">Lewati ke isi utama</a>'
MAIN_ANCHOR = '<main id="isi">'
ROOT_CONTENTS_MARKER = 'data-reader-frontmatter-navigation="v1"'
ROOT_CONTENTS_NAVIGATION = (
    '<nav data-reader-frontmatter-navigation="v1" '
    'aria-label="Bagian awal dan penutup pembaca">'
    '<a href="pendahuluan-umum/index.html">Pendahuluan umum</a> · '
    '<a href="konkordansi/index.html">Konkordansi Jilid 1</a> · '
    '<a href="referensi/index.html">Referensi Jilid 1</a>'
    '</nav>'
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_ROOT = (
    REPO_ROOT.parent
    / "curriculum_logbook"
    / "d10-capability-v1-stage"
    / "extracted-v1.0.0"
    / "fondasi-teori-ukuran-jilid-1-2-lengkap-id-v1.0.0"
)
DEFAULT_SOURCE = (
    DEFAULT_PACKAGE_ROOT
    / "output"
    / "fondasi-teori-ukuran-v1-v2-complete-id"
    / "html"
)
DEFAULT_DESTINATION = REPO_ROOT / "docs" / "id-ID" / "courses" / "D10" / "reader"
DEFAULT_MANIFEST = (
    REPO_ROOT
    / "docs"
    / "id-ID"
    / "courses"
    / "D10"
    / "D10_READER_MIRROR_MANIFEST_V1.json"
)


@dataclass(frozen=True)
class FileFact:
    path: str
    bytes: int
    sha256: str

    def as_dict(self) -> dict[str, object]:
        return {"path": self.path, "bytes": self.bytes, "sha256": self.sha256}


class ReaderHTMLParser(HTMLParser):
    """Collect local-resource candidates, anchors, and language metadata."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str]] = []
        self.anchors: set[str] = set()
        self.html_langs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value for key, value in attrs if value is not None}
        if tag.lower() == "html" and "lang" in values:
            self.html_langs.append(values["lang"])
        for key in ("id", "name"):
            if key in values:
                self.anchors.add(values[key])
        for key in ("href", "src", "poster", "data"):
            if key in values:
                self.references.append((key, values[key]))
        if "srcset" in values:
            for candidate in values["srcset"].split(","):
                url = candidate.strip().split(maxsplit=1)[0] if candidate.strip() else ""
                if url:
                    self.references.append(("srcset", url))
        if "style" in values:
            for url in css_urls(values["style"]):
                self.references.append(("style-url", url))


CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)


def css_urls(text: str) -> list[str]:
    return [match.group(2).strip() for match in CSS_URL_RE.finditer(text)]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_safe_relative_path(value: str) -> bool:
    path = PurePosixPath(value)
    return (
        bool(value)
        and "\\" not in value
        and not path.is_absolute()
        and all(part not in ("", ".", "..") for part in path.parts)
    )


def inventory(root: Path) -> list[FileFact]:
    if not root.is_dir():
        raise ValueError(f"reader root is missing or not a directory: {root}")
    facts: list[FileFact] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise ValueError(f"symlink is forbidden in reader closure: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if not is_safe_relative_path(relative):
            raise ValueError(f"unsafe reader path: {relative!r}")
        facts.append(FileFact(relative, path.stat().st_size, sha256_file(path)))
    return facts


def aggregate_sha256(facts: list[FileFact]) -> str:
    digest = hashlib.sha256()
    for fact in facts:
        digest.update(f"{fact.sha256}\t{fact.bytes}\t{fact.path}\n".encode("utf-8"))
    return digest.hexdigest()


def fact_map(facts: list[FileFact]) -> dict[str, FileFact]:
    return {fact.path: fact for fact in facts}


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
        raise ValueError("D10 source unexpectedly contains central navigation")
    if text.count(SKIP_LINK) != 1 or text.count("</footer>") != 1:
        raise ValueError("D10 central navigation injection anchors changed")
    text = text.replace(SKIP_LINK, SKIP_LINK + "\n" + navigation, 1)
    if relative == "index.html":
        if ROOT_CONTENTS_MARKER in text or text.count(MAIN_ANCHOR) != 1:
            raise ValueError("D10 root contents-navigation anchor changed")
        text = text.replace(
            MAIN_ANCHOR,
            MAIN_ANCHOR + "\n" + ROOT_CONTENTS_NAVIGATION,
            1,
        )
    text = text.replace("</footer>", program_return + "\n</footer>", 1)
    return text.encode("utf-8")


def expected_destination_inventory(source: Path) -> list[FileFact]:
    rows: list[FileFact] = []
    for fact in inventory(source):
        data = source.joinpath(*fact.path.split("/")).read_bytes()
        target = centralized_payload(fact.path, data)
        rows.append(FileFact(fact.path, len(target), hashlib.sha256(target).hexdigest()))
    return rows


def validate_destination_overlay(source: Path, destination: Path) -> tuple[list[FileFact], list[dict[str, object]]]:
    expected = expected_destination_inventory(source)
    actual = inventory(destination)
    if actual != expected:
        raise ValueError("D10 central reader differs from the deterministic navigation-overlay projection")
    source_map = fact_map(inventory(source))
    target_map = fact_map(actual)
    transformations = []
    for relative in sorted(path for path in source_map if path.endswith(".html")):
        source_fact = source_map[relative]
        target_fact = target_map[relative]
        transformations.append({
            "path": relative,
            "operation": (
                "add_central_program_navigation_and_root_contents_closure"
                if relative == "index.html"
                else "add_central_program_navigation"
            ),
            "program_home_href": program_home_href(relative),
            "root_contents_links": (
                [
                    "pendahuluan-umum/index.html",
                    "konkordansi/index.html",
                    "referensi/index.html",
                ]
                if relative == "index.html"
                else []
            ),
            "source_bytes": source_fact.bytes,
            "source_sha256": source_fact.sha256,
            "target_bytes": target_fact.bytes,
            "target_sha256": target_fact.sha256,
        })
    return actual, transformations


def validate_expected_reader_identity(facts: list[FileFact]) -> None:
    count = len(facts)
    byte_count = sum(fact.bytes for fact in facts)
    html_count = sum(fact.path.endswith(".html") for fact in facts)
    if count != EXPECTED_READER_FILES:
        raise ValueError(f"reader file count {count} != {EXPECTED_READER_FILES}")
    if byte_count != EXPECTED_READER_BYTES:
        raise ValueError(f"reader bytes {byte_count} != {EXPECTED_READER_BYTES}")
    if html_count != EXPECTED_HTML_FILES:
        raise ValueError(f"HTML route count {html_count} != {EXPECTED_HTML_FILES}")


def validate_native_manifest(root: Path, facts: list[FileFact]) -> dict[str, object]:
    manifest_path = root / "MANIFEST.tsv"
    manifest_fact = fact_map(facts).get("MANIFEST.tsv")
    if manifest_fact is None:
        raise ValueError("native MANIFEST.tsv is absent")
    if manifest_fact.bytes != EXPECTED_NATIVE_MANIFEST_BYTES:
        raise ValueError("native MANIFEST.tsv byte count changed")
    if manifest_fact.sha256 != EXPECTED_NATIVE_MANIFEST_SHA256:
        raise ValueError("native MANIFEST.tsv hash changed")

    rows: dict[str, FileFact] = {}
    for line_number, line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        columns = line.split("\t")
        if len(columns) != 3:
            raise ValueError(f"MANIFEST.tsv line {line_number}: expected three columns")
        relative, byte_text, digest = columns
        if not is_safe_relative_path(relative):
            raise ValueError(f"MANIFEST.tsv line {line_number}: unsafe path {relative!r}")
        if relative in rows:
            raise ValueError(f"MANIFEST.tsv duplicate path: {relative}")
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"MANIFEST.tsv line {line_number}: invalid SHA-256")
        rows[relative] = FileFact(relative, int(byte_text), digest)

    actual = fact_map(facts)
    expected_paths = set(actual) - {"MANIFEST.tsv"}
    if set(rows) != expected_paths:
        missing = sorted(expected_paths - set(rows))
        extra = sorted(set(rows) - expected_paths)
        raise ValueError(f"native manifest closure mismatch; missing={missing}, extra={extra}")
    mismatches = [
        path
        for path, expected in rows.items()
        if actual[path].bytes != expected.bytes or actual[path].sha256 != expected.sha256
    ]
    if mismatches:
        raise ValueError(f"native manifest byte/hash mismatch: {mismatches}")
    return {
        "path": "MANIFEST.tsv",
        "bytes": manifest_fact.bytes,
        "sha256": manifest_fact.sha256,
        "listed_files": len(rows),
        "closure_rule": "all reader files except MANIFEST.tsv itself",
    }


def _resolve_reference(root: Path, source_file: Path, raw_url: str) -> tuple[Path, str] | None:
    value = raw_url.strip()
    if not value or value.startswith("#"):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or value.startswith("//"):
        return None
    decoded_path = unquote(parsed.path)
    if not decoded_path:
        return None
    if decoded_path.startswith(("/", "\\")) or "\\" in decoded_path:
        raise ValueError(f"non-portable root/backslash URL in {source_file}: {raw_url!r}")
    candidate = source_file.parent.joinpath(*PurePosixPath(decoded_path).parts)
    resolved = candidate.resolve()
    root_resolved = root.resolve()
    if not resolved.is_relative_to(root_resolved):
        raise ValueError(f"local reference escapes reader root in {source_file}: {raw_url!r}")
    if resolved.is_dir() or decoded_path.endswith("/"):
        resolved = resolved / "index.html"
    return resolved, unquote(parsed.fragment)


def validate_local_links(
    root: Path,
    facts: list[FileFact],
    *,
    require_program_navigation: bool = True,
) -> dict[str, object]:
    html_parsers: dict[Path, ReaderHTMLParser] = {}
    local_reference_count = 0
    external_reference_count = 0
    fragment_reference_count = 0
    css_reference_count = 0
    scripts: list[str] = []
    program_navigation_files: list[str] = []

    for fact in facts:
        path = root / PurePosixPath(fact.path)
        if fact.path.endswith(".html"):
            parser = ReaderHTMLParser()
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
                if fact.path == "index.html":
                    root_links = {
                        raw_url.strip() for _key, raw_url in parser.references
                    }
                    required_root_links = {
                        "pendahuluan-umum/index.html",
                        "konkordansi/index.html",
                        "referensi/index.html",
                    }
                    if not required_root_links.issubset(root_links):
                        raise ValueError(
                            "index.html: missing front-matter/closing-section inbound links"
                        )
                    if ROOT_CONTENTS_MARKER not in path.read_text(encoding="utf-8"):
                        raise ValueError("index.html: missing root contents-navigation marker")
            html_parsers[path.resolve()] = parser
            for key, raw_url in parser.references:
                if raw_url.strip() == expected_home:
                    continue
                parsed = urlsplit(raw_url.strip())
                if parsed.scheme or parsed.netloc or raw_url.strip().startswith("//"):
                    external_reference_count += 1
                    continue
                resolved = _resolve_reference(root, path, raw_url)
                if resolved is None:
                    if raw_url.strip().startswith("#"):
                        fragment = unquote(urlsplit(raw_url.strip()).fragment)
                        if fragment and fragment not in parser.anchors:
                            raise ValueError(f"{fact.path}: missing local fragment #{fragment}")
                        fragment_reference_count += bool(fragment)
                    continue
                target, fragment = resolved
                if not target.is_file():
                    raise ValueError(f"{fact.path}: missing local target for {raw_url!r}")
                local_reference_count += 1
                if fragment:
                    fragment_reference_count += 1
                if key == "src" and target.suffix.lower() == ".js":
                    scripts.append(target.relative_to(root).as_posix())
        elif fact.path.endswith(".css"):
            for raw_url in css_urls(path.read_text(encoding="utf-8")):
                if raw_url.startswith("data:"):
                    external_reference_count += 1
                    continue
                resolved = _resolve_reference(root, path, raw_url)
                if resolved is None:
                    continue
                target, _ = resolved
                if not target.is_file():
                    raise ValueError(f"{fact.path}: missing CSS target for {raw_url!r}")
                css_reference_count += 1

    # Fragment checks need every target page's anchor set, which is now cached.
    for source_path, parser in html_parsers.items():
        source_relative = source_path.relative_to(root).as_posix()
        expected_home = program_home_href(source_relative)
        for _key, raw_url in parser.references:
            if raw_url.strip() == expected_home:
                continue
            fragment = unquote(urlsplit(raw_url.strip()).fragment)
            if not fragment or raw_url.strip().startswith("#"):
                continue
            resolved = _resolve_reference(root, source_path, raw_url)
            if resolved is None:
                continue
            target, _ = resolved
            if target.suffix.lower() == ".html":
                target_parser = html_parsers.get(target.resolve())
                if target_parser is None:
                    raise ValueError(f"fragment target is not parsed HTML: {target}")
                if fragment not in target_parser.anchors:
                    rel_source = source_path.relative_to(root).as_posix()
                    raise ValueError(
                        f"{rel_source}: missing fragment #{fragment} in "
                        f"{target.relative_to(root).as_posix()}"
                    )

    required_runtime = {
        "_static/mathjax/tex-chtml.js",
        "_static/mathjax/LICENSE",
        "_static/reader-v4.css",
        "_downloads/fondasi-teori-ukuran-jilid-1-dan-jilid-2-lengkap-id.pdf",
    }
    paths = set(fact_map(facts))
    missing_runtime = sorted(required_runtime - paths)
    if missing_runtime:
        raise ValueError(f"required local render dependencies absent: {missing_runtime}")
    if sorted(set(scripts)) != ["_static/mathjax/tex-chtml.js"]:
        raise ValueError(f"unexpected or missing reader scripts: {sorted(set(scripts))}")
    font_count = sum(
        fact.path.startswith("_static/mathjax/output/chtml/fonts/woff-v2/")
        and fact.path.endswith(".woff")
        for fact in facts
    )
    if font_count != 23:
        raise ValueError(f"local MathJax font closure {font_count} != 23")

    return {
        "html_files": len(html_parsers),
        "local_references_checked": local_reference_count,
        "external_references_observed": external_reference_count,
        "fragment_references_checked": fragment_reference_count,
        "css_local_references_checked": css_reference_count,
        "local_mathjax_script": "_static/mathjax/tex-chtml.js",
        "local_mathjax_fonts": font_count,
        "portable_subdirectory_links": True,
        "program_navigation_href": CENTRAL_PROGRAM_HREF if require_program_navigation else None,
        "program_navigation_files": program_navigation_files,
        "program_navigation_files_checked": len(program_navigation_files),
        "every_html_document_links_to_program_home": (
            not require_program_navigation or len(program_navigation_files) == len(html_parsers)
        ),
    }


def validate_manifest_file(manifest_path: Path, facts: list[FileFact]) -> dict[str, object]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("schema") != "d10-reader-mirror-manifest-v1":
        raise ValueError("unexpected D10 mirror manifest schema")
    rows = payload.get("reader", {}).get("files")
    if not isinstance(rows, list):
        raise ValueError("D10 mirror manifest has no reader.files array")
    expected = [fact.as_dict() for fact in facts]
    if rows != expected:
        raise ValueError("D10 mirror manifest inventory does not equal live reader bytes")
    if payload["reader"].get("file_count") != len(facts):
        raise ValueError("D10 mirror manifest file_count mismatch")
    if payload["reader"].get("bytes") != sum(fact.bytes for fact in facts):
        raise ValueError("D10 mirror manifest bytes mismatch")
    if payload["reader"].get("aggregate_sha256") != aggregate_sha256(facts):
        raise ValueError("D10 mirror manifest aggregate mismatch")
    return {
        "path": manifest_path.name,
        "bytes": manifest_path.stat().st_size,
        "sha256": sha256_file(manifest_path),
    }


def validate_component_licences(package_root: Path, destination: Path) -> list[dict[str, object]]:
    course_root = destination.parent
    bindings = [
        (
            package_root / "LICENSE",
            course_root / "licenses" / "Design-Science-License.txt",
            "LicenseRef-Design-Science-License",
        ),
        (
            package_root / "LICENSE-CC0-1.0.txt",
            course_root / "licenses" / "CC0-1.0.txt",
            "CC0-1.0",
        ),
        (
            package_root / "THIRD_PARTY_LICENSES" / "MathJax-3.2.2-Apache-2.0.txt",
            course_root / "licenses" / "MathJax-3.2.2-Apache-2.0.txt",
            "Apache-2.0",
        ),
    ]
    result: list[dict[str, object]] = []
    for source, target, identifier in bindings:
        if not source.is_file() or not target.is_file():
            raise ValueError(f"licence binding is missing: {source} -> {target}")
        if source.stat().st_size != target.stat().st_size or sha256_file(source) != sha256_file(target):
            raise ValueError(f"licence copy is not byte-exact: {target}")
        result.append(
            {
                "identifier": identifier,
                "path": target.relative_to(REPO_ROOT).as_posix(),
                "bytes": target.stat().st_size,
                "sha256": sha256_file(target),
            }
        )
    embedded_mathjax = destination / "_static" / "mathjax" / "LICENSE"
    if sha256_file(embedded_mathjax) != result[2]["sha256"]:
        raise ValueError("embedded MathJax licence differs from the package-level notice")
    return result


def validate(
    source: Path,
    destination: Path,
    package_root: Path,
    manifest_path: Path | None,
) -> dict[str, object]:
    source_facts = inventory(source)
    validate_expected_reader_identity(source_facts)
    destination_facts, transformations = validate_destination_overlay(source, destination)
    native_manifest = validate_native_manifest(source, source_facts)
    links = validate_local_links(destination, destination_facts)
    licences = validate_component_licences(package_root, destination)
    result: dict[str, object] = {
        "status": "pass",
        "reader": {
            "file_count": len(destination_facts),
            "bytes": sum(fact.bytes for fact in destination_facts),
            "html_files": sum(fact.path.endswith(".html") for fact in destination_facts),
            "aggregate_sha256": aggregate_sha256(destination_facts),
            "source_destination_byte_identity": False,
            "source_destination_navigation_overlay": True,
        },
        "native_manifest": native_manifest,
        "links": links,
        "component_licences": licences,
        "unsafe_paths": 0,
        "symlinks": 0,
    }
    if manifest_path is not None:
        result["mirror_manifest"] = validate_manifest_file(manifest_path, destination_facts)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        overlay = manifest.get("central_navigation_overlay")
        if not isinstance(overlay, dict) or overlay.get("transformations") != transformations:
            raise ValueError("D10 central navigation overlay binding changed")
        if overlay.get("program_home_href") != CENTRAL_PROGRAM_HREF:
            raise ValueError("D10 central program-home route changed")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--package-root", type=Path, default=DEFAULT_PACKAGE_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = validate(
            args.source.resolve(),
            args.destination.resolve(),
            args.package_root.resolve(),
            args.manifest.resolve(),
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"D10 public HTML validation: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
