#!/usr/bin/env python3
"""Validate bidirectional reachability for every central learner HTML surface."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "backend" / "authority" / "central-reader-navigation-v1.json"


class NavigationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.navigation_markers = 0
        self.surface_navigation_markers = 0
        self.home_links: list[dict[str, str]] = []
        self.contents_links: list[dict[str, str]] = []
        self.surface_contents_links: list[dict[str, str]] = []
        self._active: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "nav" and values.get("data-program-navigation") == "v1":
            self.navigation_markers += 1
        if tag.lower() == "nav" and values.get("data-central-surface-navigation") == "v1":
            self.surface_navigation_markers += 1
        if tag.lower() != "a":
            return
        row = {
            "href": values.get("href", ""),
            "text": "",
            "course_id": values.get("data-course-id", ""),
        }
        if "data-program-home" in values:
            self.home_links.append(row)
            self._active.append(row)
        elif "data-reader-contents" in values:
            self.contents_links.append(row)
            self._active.append(row)
        elif "data-course-surface-contents" in values:
            self.surface_contents_links.append(row)
            self._active.append(row)

    def handle_data(self, data: str) -> None:
        if self._active:
            self._active[-1]["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._active:
            self._active.pop()


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def html_parser(path: Path) -> NavigationParser:
    parser = NavigationParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def resolve_href(source: Path, href: str) -> tuple[Path, str]:
    parsed = urlsplit(href.strip())
    if parsed.scheme or parsed.netloc or href.strip().startswith("//"):
        raise ValueError(f"navigation target must be a local site route: {source} -> {href!r}")
    decoded = unquote(parsed.path)
    target = (source.parent / decoded).resolve()
    if decoded.endswith("/") or target.is_dir():
        target = target / "index.html"
    if not target.is_relative_to(ROOT.resolve()):
        raise ValueError(f"navigation target escapes the central site: {source} -> {href!r}")
    return target, unquote(parsed.fragment)


def course_article(document: Path, course_id: str) -> str:
    text = document.read_text(encoding="utf-8")
    pattern = re.compile(
        rf'<article\b[^>]*\bid="course-{re.escape(course_id)}"[^>]*>.*?</article>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise ValueError(f"{document}: expected exactly one course-{course_id} card")
    return matches[0]


def configured_html(root: Path, exclusions: list[str] | None = None) -> list[Path]:
    excluded = {
        (root / Path(*value.split("/"))).resolve() for value in (exclusions or [])
    }
    rows = []
    for path in sorted(root.rglob("*.html"), key=lambda item: item.as_posix()):
        resolved = path.resolve()
        if any(resolved == item or resolved.is_relative_to(item) for item in excluded):
            continue
        rows.append(path)
    return rows


def article_targets(document: Path, article: str, site_origin: str) -> set[Path]:
    targets: set[Path] = set()
    site = urlsplit(site_origin)
    site_prefix = site.path.rstrip("/") + "/"
    for match in re.finditer(
        r'<a\b[^>]*\bhref=(?:"([^"]*)"|\'([^\']*)\')',
        article,
        flags=re.IGNORECASE,
    ):
        href = match.group(1) if match.group(1) is not None else match.group(2)
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc:
            if (
                parsed.scheme.lower() == site.scheme.lower()
                and parsed.netloc.lower() == site.netloc.lower()
                and unquote(parsed.path).startswith(site_prefix)
            ):
                logical = unquote(parsed.path)[len(site_prefix) :]
                target = (ROOT / "docs" / Path(*logical.split("/"))).resolve()
                if not logical or logical.endswith("/") or target.is_dir():
                    target = target / "index.html"
                targets.add(target)
            continue
        try:
            target, _fragment = resolve_href(document, href)
        except ValueError:
            continue
        targets.add(target.resolve())
    return targets


def main() -> int:
    try:
        contract = load_json(CONTRACT)
        if contract.get("schema") != "central-reader-navigation-v1":
            raise ValueError("central navigation contract schema changed")
        interfaces = contract.get("interfaces")
        readers = contract.get("readers")
        gateways = contract.get("gateways")
        course_surfaces = contract.get("course_surfaces")
        generic_surfaces = contract.get("generic_surfaces")
        reciprocal_hubs = contract.get("reciprocal_hubs")
        summary = contract.get("summary")
        if not isinstance(interfaces, dict) or not isinstance(readers, list) or not isinstance(gateways, list) or not isinstance(course_surfaces, list) or not isinstance(generic_surfaces, list) or not isinstance(reciprocal_hubs, list) or not isinstance(summary, dict):
            raise ValueError("central navigation contract is incomplete")
        if not {"en", "id"}.issubset(interfaces):
            raise ValueError("current en and id interfaces are required")
        route_segments: set[str] = set()
        for locale, interface in interfaces.items():
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", interface.get("route_segment", "")):
                raise ValueError(f"{locale}: invalid stable locale route segment")
            if interface["route_segment"] in route_segments:
                raise ValueError(f"{locale}: duplicate stable locale route segment")
            route_segments.add(interface["route_segment"])
            if not interface.get("language_tag") or not interface.get("label"):
                raise ValueError(f"{locale}: locale metadata is incomplete")
        if len(readers) != summary.get("reader_roots") or len(gateways) != summary.get("gateway_roots") or len(course_surfaces) != summary.get("course_surface_roots") or len(generic_surfaces) != summary.get("generic_html_documents") or len(reciprocal_hubs) != summary.get("reciprocal_hubs"):
            raise ValueError("central navigation root counts disagree with the declared summary")

        localized_card_count = 0
        interface_course_sets: list[set[str]] = []
        for locale, interface in sorted(interfaces.items()):
            document = ROOT / Path(*interface["document"].split("/"))
            text = document.read_text(encoding="utf-8")
            course_ids = re.findall(r'<article\b[^>]*\bid="course-([A-Z][0-9]+)"', text, flags=re.IGNORECASE)
            if len(course_ids) != 40 or len(set(course_ids)) != 40:
                raise ValueError(f"{document}: expected 40 unique localized course cards")
            interface_course_sets.append(set(course_ids))
            for course_id in course_ids:
                article = course_article(document, course_id)
                if 'data-access-group="hosted-reader"' not in article:
                    raise ValueError(f"{document}: course-{course_id} lacks its hosted-reader group")
                if 'data-access-group="authoritative-original"' not in article or 'data-original-source=' not in article:
                    raise ValueError(f"{document}: course-{course_id} lacks a prominent original-source link")
                localized_card_count += 1
        if len(interface_course_sets) != len(interfaces) or any(
            item != interface_course_sets[0] for item in interface_course_sets[1:]
        ):
            raise ValueError("localized interfaces do not expose the same 40 course IDs")
        for hub in reciprocal_hubs:
            public_url = hub["public_url"]
            for locale in hub["linked_from_locales"]:
                document = ROOT / Path(*interfaces[locale]["document"].split("/"))
                if public_url not in document.read_text(encoding="utf-8"):
                    raise ValueError(f"{document}: missing reciprocal-hub link {public_url}")

        configured_reader_files: set[Path] = set()
        reader_results = []
        course_cards_checked: set[tuple[str, str]] = set()
        for row in readers:
            course_id = row["course_id"]
            locale = row["locale"]
            if row["course_fragment"] != f"course-{course_id}":
                raise ValueError(f"{row['root']}: course fragment is not bound to {course_id}")
            reader_root = ROOT / Path(*row["root"].split("/"))
            if not reader_root.resolve().is_relative_to((ROOT / "docs").resolve()):
                raise ValueError(f"{row['root']}: reader root must remain below docs/")
            interface_document = ROOT / Path(*interfaces[locale]["document"].split("/"))
            html_files = configured_html(reader_root)
            if len(html_files) != row["html_documents"]:
                raise ValueError(
                    f"{row['root']}: HTML count {len(html_files)} != {row['html_documents']}"
                )
            root_index = (reader_root / "index.html").resolve()
            if root_index not in {path.resolve() for path in html_files}:
                raise ValueError(f"{row['root']}: index.html is missing")
            for path in html_files:
                resolved_path = path.resolve()
                if resolved_path in configured_reader_files:
                    raise ValueError(f"reader file appears under two contract roots: {path}")
                configured_reader_files.add(resolved_path)
                parser = html_parser(path)
                if parser.navigation_markers != 1:
                    raise ValueError(f"{path}: expected exactly one program-navigation marker")
                if len(parser.home_links) < 2:
                    raise ValueError(f"{path}: top and bottom program-home links are required")
                for link in parser.home_links:
                    target, fragment = resolve_href(path, link["href"])
                    if target != interface_document.resolve() or fragment != row["course_fragment"]:
                        raise ValueError(f"{path}: program-home link does not return to its course card")
                    if not link["text"].strip():
                        raise ValueError(f"{path}: program-home link has no visible label")
                if resolved_path != root_index:
                    if not parser.contents_links:
                        raise ValueError(f"{path}: non-root reader page lacks a contents link")
                    for link in parser.contents_links:
                        target, fragment = resolve_href(path, link["href"])
                        if target != root_index or fragment:
                            raise ValueError(f"{path}: reader-contents link misses its root index")
                        if not link["text"].strip():
                            raise ValueError(f"{path}: reader-contents link has no visible label")

            landing = ROOT / Path(*row["landing_document"].split("/"))
            landing_text = landing.read_text(encoding="utf-8")
            for suffix in row["landing_required_paths"]:
                expected_url = row["public_root"] + suffix
                if expected_url not in landing_text:
                    raise ValueError(f"{landing}: missing inbound reader link {expected_url}")

            card_key = (locale, course_id)
            if card_key not in course_cards_checked:
                article = course_article(interface_document, course_id)
                if 'data-access-group="authoritative-original"' not in article:
                    raise ValueError(f"{interface_document}: course-{course_id} lacks original-source group")
                if 'data-original-source=' not in article:
                    raise ValueError(f"{interface_document}: course-{course_id} lacks original-source link")
                course_cards_checked.add(card_key)
            reader_results.append({
                "course_id": course_id,
                "root": row["root"],
                "state": row["state"],
                "html_documents": len(html_files),
                "program_home_links_minimum": 2 * len(html_files),
                "contents_links_required": len(html_files) - 1,
            })

        discovered = set()
        for base in (ROOT / "docs" / "en" / "courses", ROOT / "docs" / "id-ID" / "courses"):
            if base.is_dir():
                for path in base.rglob("*.html"):
                    if "reader" in path.relative_to(base).parts:
                        discovered.add(path.resolve())
        legacy = ROOT / "docs" / "readers"
        if legacy.is_dir():
            discovered.update(path.resolve() for path in legacy.rglob("*.html"))
        if discovered != configured_reader_files:
            missing = sorted(path.relative_to(ROOT).as_posix() for path in discovered - configured_reader_files)
            extra = sorted(path.relative_to(ROOT).as_posix() for path in configured_reader_files - discovered)
            raise ValueError(f"reader-root registry is not closed; unregistered={missing}, stale={extra}")

        gateway_results = []
        configured_gateway_files: set[Path] = set()
        for row in gateways:
            course_id = row["course_id"]
            locale = row["locale"]
            gateway_root = ROOT / Path(*row["root"].split("/"))
            if not gateway_root.resolve().is_relative_to((ROOT / "docs").resolve()):
                raise ValueError(f"{row['root']}: gateway root must remain below docs/")
            interface_document = ROOT / Path(*interfaces[locale]["document"].split("/"))
            html_files = configured_html(gateway_root, row.get("exclude_subtrees"))
            if len(html_files) != row["html_documents"]:
                raise ValueError(
                    f"{row['root']}: gateway HTML count {len(html_files)} != {row['html_documents']}"
                )
            for path in html_files:
                resolved_path = path.resolve()
                if resolved_path in configured_gateway_files or resolved_path in configured_reader_files:
                    raise ValueError(f"gateway file appears under another registered root: {path}")
                configured_gateway_files.add(resolved_path)
                parser = html_parser(path)
                if not parser.home_links:
                    raise ValueError(f"{path}: gateway lacks data-program-home")
                for link in parser.home_links:
                    target, fragment = resolve_href(path, link["href"])
                    if target != interface_document.resolve() or fragment != f"course-{course_id}":
                        raise ValueError(f"{path}: gateway program-home link is not course-scoped")
                    if not link["text"].strip():
                        raise ValueError(f"{path}: gateway program-home link has no label")
            gateway_results.append({
                "course_id": course_id,
                "root": row["root"],
                "state": row["state"],
                "html_documents": len(html_files),
            })

        course_surface_results = []
        configured_course_surface_files: set[Path] = set()
        surface_docs_by_course: dict[tuple[str, str], set[Path]] = {}
        surface_outbound: dict[Path, set[Path]] = {}
        interface_outbound_by_course: dict[tuple[str, str], set[Path]] = {}
        for group in course_surfaces:
            locale = group["locale"]
            root = ROOT / Path(*group["root"].split("/"))
            if not root.resolve().is_relative_to((ROOT / "docs").resolve()):
                raise ValueError(f"{group['root']}: course-surface root must remain below docs/")
            documents = group.get("documents")
            if not isinstance(documents, list) or not documents:
                raise ValueError(f"{group['root']}: course-surface document map is empty")
            actual = {path.relative_to(root).as_posix() for path in configured_html(root)}
            declared = {row["path"] for row in documents}
            if len(declared) != len(documents) or actual != declared:
                raise ValueError(
                    f"{group['root']}: course-surface closure changed; "
                    f"unregistered={sorted(actual - declared)}, stale={sorted(declared - actual)}"
                )
            interface_document = ROOT / Path(*interfaces[locale]["document"].split("/"))
            for document in documents:
                path = root / Path(*document["path"].split("/"))
                resolved_path = path.resolve()
                occupied = configured_reader_files | configured_gateway_files | configured_course_surface_files
                if resolved_path in occupied:
                    raise ValueError(f"course surface appears under another registered role: {path}")
                configured_course_surface_files.add(resolved_path)
                ids = document.get("course_ids")
                if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)):
                    raise ValueError(f"{path}: invalid course target list")
                parser = html_parser(path)
                surface_outbound[resolved_path] = article_targets(
                    path, path.read_text(encoding="utf-8"), contract["site_origin"]
                )
                if parser.surface_navigation_markers != 2:
                    raise ValueError(f"{path}: expected top and bottom course-surface navigation")
                marked_home_links = [link for link in parser.home_links if link["course_id"]]
                if set(link["course_id"] for link in marked_home_links) != set(ids):
                    raise ValueError(f"{path}: course-scoped return-link set changed")
                for course_id in ids:
                    matches = 0
                    for link in marked_home_links:
                        if link["course_id"] != course_id:
                            continue
                        target, fragment = resolve_href(path, link["href"])
                        if target == interface_document.resolve() and fragment == f"course-{course_id}":
                            matches += 1
                        if not link["text"].strip():
                            raise ValueError(f"{path}: course return link has no visible label")
                    if matches != 2:
                        raise ValueError(f"{path}: course-{course_id} needs exact top/bottom returns")
                    article = course_article(interface_document, course_id)
                    key = (locale, course_id)
                    surface_docs_by_course.setdefault(key, set()).add(resolved_path)
                    interface_outbound_by_course.setdefault(
                        key,
                        article_targets(interface_document, article, contract["site_origin"]),
                    )

                contents_paths = document.get("contents_paths", [])
                if not isinstance(contents_paths, list) or len(contents_paths) != len(set(contents_paths)):
                    raise ValueError(f"{path}: invalid section-contents list")
                expected_contents = {
                    (root / Path(*value.split("/"))).resolve() for value in contents_paths
                }
                actual_contents: dict[Path, int] = {}
                for link in parser.surface_contents_links:
                    target, fragment = resolve_href(path, link["href"])
                    if fragment:
                        raise ValueError(f"{path}: section-contents link unexpectedly has a fragment")
                    actual_contents[target] = actual_contents.get(target, 0) + 1
                    if not link["text"].strip():
                        raise ValueError(f"{path}: section-contents link has no visible label")
                if set(actual_contents) != expected_contents or any(
                    count != 2 for count in actual_contents.values()
                ):
                    raise ValueError(f"{path}: section-contents top/bottom closure changed")
            course_surface_results.append({
                "root": group["root"],
                "locale": locale,
                "state": group["state"],
                "html_documents": len(documents),
            })

        for key, required in sorted(surface_docs_by_course.items()):
            reachable = set(interface_outbound_by_course[key]) & required
            frontier = list(reachable)
            while frontier:
                current = frontier.pop()
                for target in surface_outbound.get(current, set()) & required:
                    if target not in reachable:
                        reachable.add(target)
                        frontier.append(target)
            if reachable != required:
                locale, course_id = key
                missing = sorted(path.relative_to(ROOT).as_posix() for path in required - reachable)
                raise ValueError(
                    f"{interfaces[locale]['document']}: course-{course_id} cannot reach {missing}"
                )

        generic_results = []
        configured_generic_files: set[Path] = set()
        for row in generic_surfaces:
            path = ROOT / Path(*row["document"].split("/"))
            resolved_path = path.resolve()
            occupied = configured_reader_files | configured_gateway_files | configured_course_surface_files | configured_generic_files
            if not path.is_file() or not resolved_path.is_relative_to((ROOT / "docs").resolve()):
                raise ValueError(f"generic surface is missing or outside docs: {path}")
            if resolved_path in occupied:
                raise ValueError(f"generic surface overlaps another registered role: {path}")
            configured_generic_files.add(resolved_path)
            parser = html_parser(path)
            if row["navigation_required"]:
                if parser.surface_navigation_markers != 2:
                    raise ValueError(f"{path}: generic surface needs top/bottom program returns")
                target_document = (ROOT / Path(*row["target_document"].split("/"))).resolve()
                unscoped = [link for link in parser.home_links if not link["course_id"]]
                matches = 0
                for link in unscoped:
                    target, fragment = resolve_href(path, link["href"])
                    if target == target_document and not fragment:
                        matches += 1
                    if not link["text"].strip():
                        raise ValueError(f"{path}: generic program-return link has no label")
                if matches != 2:
                    raise ValueError(f"{path}: generic surface needs exact top/bottom program returns")
            elif parser.surface_navigation_markers:
                raise ValueError(f"{path}: program root must not carry a redundant return overlay")
            generic_results.append({
                "document": row["document"],
                "state": row["state"],
                "navigation_required": row["navigation_required"],
            })

        interface_files = {
            (ROOT / Path(*row["document"].split("/"))).resolve()
            for row in interfaces.values()
        }
        all_classified = (
            configured_reader_files
            | configured_gateway_files
            | configured_course_surface_files
            | configured_generic_files
            | interface_files
        )
        all_docs_html = {
            path.resolve() for path in (ROOT / "docs").rglob("*.html") if path.is_file()
        }
        if all_classified != all_docs_html:
            missing = sorted(path.relative_to(ROOT).as_posix() for path in all_docs_html - all_classified)
            extra = sorted(path.relative_to(ROOT).as_posix() for path in all_classified - all_docs_html)
            raise ValueError(f"complete HTML classification is open; unregistered={missing}, stale={extra}")

        reader_html_documents = len(configured_reader_files)
        gateway_html_documents = len(configured_gateway_files)
        course_surface_html_documents = len(configured_course_surface_files)
        classified_html_documents = len(all_classified)
        if reader_html_documents != summary.get("reader_html_documents"):
            raise ValueError("reader HTML closure disagrees with the declared summary")
        if gateway_html_documents != summary.get("gateway_html_documents"):
            raise ValueError("gateway HTML closure disagrees with the declared summary")
        if course_surface_html_documents != summary.get("course_surface_html_documents"):
            raise ValueError("course-surface HTML closure disagrees with the declared summary")
        if len(configured_generic_files) != summary.get("generic_html_documents"):
            raise ValueError("generic HTML closure disagrees with the declared summary")
        if classified_html_documents != summary.get("classified_html_documents"):
            raise ValueError("complete HTML closure disagrees with the declared summary")
        if localized_card_count != summary.get("localized_course_cards"):
            raise ValueError("localized card closure disagrees with the declared summary")

        result = {
            "status": "pass",
            "contract": CONTRACT.relative_to(ROOT).as_posix(),
            "reader_roots": len(readers),
            "reader_html_documents": reader_html_documents,
            "gateway_roots": len(gateways),
            "gateway_html_documents": gateway_html_documents,
            "course_surface_roots": len(course_surfaces),
            "course_surface_html_documents": course_surface_html_documents,
            "generic_html_documents": len(configured_generic_files),
            "classified_html_documents": classified_html_documents,
            "localized_course_cards_with_original_sources": localized_card_count,
            "reciprocal_hubs": len(reciprocal_hubs),
            "readers": reader_results,
            "gateways": gateway_results,
            "course_surfaces": course_surface_results,
            "generic_surfaces": generic_results,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"central reader navigation validation: FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
