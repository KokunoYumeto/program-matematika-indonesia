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
        self.surface_navigation_placements: list[str] = []
        self.home_links: list[dict[str, str]] = []
        self.program_root_links: list[dict[str, str]] = []
        self.contents_links: list[dict[str, str]] = []
        self.surface_contents_links: list[dict[str, str]] = []
        self._active: list[dict[str, str]] = []
        self._surface_placement = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "nav" and values.get("data-program-navigation") == "v1":
            self.navigation_markers += 1
        if tag.lower() == "nav" and values.get("data-central-surface-navigation") == "v1":
            self.surface_navigation_markers += 1
            self._surface_placement = values.get("data-placement", "")
            self.surface_navigation_placements.append(self._surface_placement)
        if tag.lower() != "a":
            return
        row = {
            "href": values.get("href", ""),
            "text": "",
            "course_id": values.get("data-course-id", ""),
            "interface_locale": values.get("data-interface-locale", ""),
            "placement": self._surface_placement,
            "course_card": "1" if "data-course-card" in values else "",
        }
        if "data-program-home" in values:
            self.home_links.append(row)
            self._active.append(row)
        elif "data-program-root" in values:
            self.program_root_links.append(row)
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
        elif tag.lower() == "nav" and self._surface_placement:
            self._surface_placement = ""


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


def graph_reachable(
    graph: dict[Path, set[Path]], starts: set[Path]
) -> set[Path]:
    """Return the complete directed closure within an already bounded graph."""
    reachable = set(starts)
    frontier = list(starts)
    while frontier:
        current = frontier.pop()
        for target in graph.get(current, set()):
            if target not in reachable:
                reachable.add(target)
                frontier.append(target)
    return reachable


def validate_central_overlay(
    path: Path,
    parser: NavigationParser,
    course_ids: list[str],
    interfaces: dict[str, object],
    contents_paths: list[Path] | None = None,
) -> None:
    if parser.surface_navigation_markers != 2 or sorted(
        parser.surface_navigation_placements
    ) != ["bottom", "top"]:
        raise ValueError(f"{path}: expected exact top and bottom central navigation")

    expected_card_keys = {
        (interface_locale, course_id)
        for interface_locale in interfaces
        for course_id in course_ids
    }
    marked_home_links = [
        link
        for link in parser.home_links
        if link["course_id"] and link["course_card"] and link["placement"]
    ]
    actual_card_keys = {
        (link["interface_locale"], link["course_id"])
        for link in marked_home_links
    }
    if actual_card_keys != expected_card_keys:
        raise ValueError(f"{path}: localized course-card return set changed")
    if len(marked_home_links) != 2 * len(expected_card_keys):
        raise ValueError(f"{path}: localized course-card return multiplicity changed")
    for interface_locale, course_id in sorted(expected_card_keys):
        interface_document = ROOT / Path(*interfaces[interface_locale]["document"].split("/"))
        matches: list[str] = []
        for link in marked_home_links:
            if (link["interface_locale"], link["course_id"]) != (
                interface_locale,
                course_id,
            ):
                continue
            target, fragment = resolve_href(path, link["href"])
            if target == interface_document.resolve() and fragment == f"course-{course_id}":
                matches.append(link["placement"])
            if not link["text"].strip():
                raise ValueError(f"{path}: course-card return link has no visible label")
        if sorted(matches) != ["bottom", "top"]:
            raise ValueError(
                f"{path}: {interface_locale}/course-{course_id} needs exact top/bottom returns"
            )

    expected_root_locales = set(interfaces)
    central_root_links = [link for link in parser.program_root_links if link["placement"]]
    if {link["interface_locale"] for link in central_root_links} != expected_root_locales:
        raise ValueError(f"{path}: localized program-root return set changed")
    if len(central_root_links) != 2 * len(expected_root_locales):
        raise ValueError(f"{path}: localized program-root return multiplicity changed")
    for interface_locale, interface in sorted(interfaces.items()):
        target_document = (ROOT / Path(*interface["document"].split("/"))).resolve()
        matches: list[str] = []
        for link in central_root_links:
            if link["interface_locale"] != interface_locale:
                continue
            target, fragment = resolve_href(path, link["href"])
            if target == target_document and not fragment:
                matches.append(link["placement"])
            if not link["text"].strip():
                raise ValueError(f"{path}: program-root return link has no visible label")
        if sorted(matches) != ["bottom", "top"]:
            raise ValueError(
                f"{path}: {interface_locale} program root needs exact top/bottom returns"
            )

    expected_contents = {item.resolve() for item in (contents_paths or [])}
    actual_contents: dict[Path, int] = {}
    for link in parser.surface_contents_links:
        target, fragment = resolve_href(path, link["href"])
        if fragment:
            raise ValueError(f"{path}: central related-page link unexpectedly has a fragment")
        actual_contents[target] = actual_contents.get(target, 0) + 1
        if not link["text"].strip():
            raise ValueError(f"{path}: central related-page link has no visible label")
    if set(actual_contents) != expected_contents or any(
        count != 2 for count in actual_contents.values()
    ):
        raise ValueError(f"{path}: central related-page top/bottom closure changed")


def main() -> int:
    try:
        contract = load_json(CONTRACT)
        if contract.get("schema") != "central-reader-navigation-v1":
            raise ValueError("central navigation contract schema changed")
        if contract.get("policy", {}).get("return_locale_policy") != "all_registered_interfaces":
            raise ValueError("central navigation must return to all registered interfaces")
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
            if set(interface.get("navigation", {})) != {"aria", "lead", "program_root", "related_page"}:
                raise ValueError(f"{locale}: locale navigation copy is incomplete")
            fallback = interface.get("fallback_locale")
            if fallback is not None and fallback not in interfaces:
                raise ValueError(f"{locale}: fallback locale is not registered")
        for locale in interfaces:
            seen: set[str] = set()
            current: str | None = locale
            while current is not None:
                if current in seen:
                    raise ValueError(f"{locale}: locale fallback cycle")
                seen.add(current)
                current = interfaces[current].get("fallback_locale")
        root_text = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        if root_text.count("<!-- GENERATED-INTERFACE-LOCALES-START -->") != 1 or root_text.count("<!-- GENERATED-INTERFACE-LOCALES-END -->") != 1:
            raise ValueError("program root lacks the generated locale chooser boundary")
        for locale, interface in interfaces.items():
            route = re.escape(interface["route_segment"] + "/")
            if not re.search(rf'<a\b[^>]*href="{route}"[^>]*data-interface-locale="{re.escape(locale)}"', root_text):
                raise ValueError(f"program root does not expose locale {locale}")
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
            source_navigation = row.get("source_navigation", "native-plus-central")
            if source_navigation not in {"native-plus-central", "central-overlay-only"}:
                raise ValueError(
                    f"{row['root']}: unsupported source-navigation mode {source_navigation!r}"
                )
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
            declared_by_relative = {
                path.relative_to(reader_root).as_posix(): path.resolve()
                for path in html_files
            }
            declared_reader_files = set(declared_by_relative.values())
            closure = row.get("navigation_closure")
            if len(html_files) > 1 and not isinstance(closure, dict):
                raise ValueError(
                    f"{row['root']}: multi-page reader lacks navigation_closure"
                )
            closure = closure or {
                "entry_path": "index.html",
                "contents_paths": ["index.html"],
                "overlay_links": {},
            }
            if set(closure) != {"entry_path", "contents_paths", "overlay_links"}:
                raise ValueError(f"{row['root']}: invalid reader navigation_closure")
            entry_relative = closure["entry_path"]
            contents_relatives = closure["contents_paths"]
            overlay_links = closure["overlay_links"]
            if (
                not isinstance(entry_relative, str)
                or entry_relative not in declared_by_relative
                or not isinstance(contents_relatives, list)
                or not contents_relatives
                or len(contents_relatives) != len(set(contents_relatives))
                or entry_relative not in contents_relatives
                or not set(contents_relatives).issubset(declared_by_relative)
                or not isinstance(overlay_links, dict)
            ):
                raise ValueError(f"{row['root']}: invalid reader closure paths")
            for source, targets in overlay_links.items():
                if (
                    source not in declared_by_relative
                    or not isinstance(targets, list)
                    or not targets
                    or len(targets) != len(set(targets))
                    or not set(targets).issubset(declared_by_relative)
                    or source in targets
                ):
                    raise ValueError(
                        f"{row['root']}: invalid reader overlay link map for {source!r}"
                    )
            entry_path = declared_by_relative[entry_relative]
            contents_paths = {
                declared_by_relative[value] for value in contents_relatives
            }
            reader_outbound: dict[Path, set[Path]] = {}
            for path in html_files:
                resolved_path = path.resolve()
                if resolved_path in configured_reader_files:
                    raise ValueError(f"reader file appears under two contract roots: {path}")
                configured_reader_files.add(resolved_path)
                parser = html_parser(path)
                reader_outbound[resolved_path] = article_targets(
                    path, path.read_text(encoding="utf-8"), contract["site_origin"]
                ) & declared_reader_files
                native_home_links = [
                    link for link in parser.home_links if not link["placement"]
                ]
                native_contents_links = [
                    link for link in parser.contents_links if not link["placement"]
                ]
                if source_navigation == "native-plus-central":
                    if parser.navigation_markers != 1:
                        raise ValueError(f"{path}: expected exactly one program-navigation marker")
                    if len(native_home_links) < 2:
                        raise ValueError(f"{path}: top and bottom program-home links are required")
                    for link in native_home_links:
                        target, fragment = resolve_href(path, link["href"])
                        if target != interface_document.resolve() or fragment != row["course_fragment"]:
                            raise ValueError(f"{path}: program-home link does not return to its course card")
                        if not link["text"].strip():
                            raise ValueError(f"{path}: program-home link has no visible label")
                    if resolved_path != entry_path:
                        if not native_contents_links:
                            raise ValueError(f"{path}: non-root reader page lacks a contents link")
                        for link in native_contents_links:
                            target, fragment = resolve_href(path, link["href"])
                            if target != entry_path or fragment:
                                raise ValueError(f"{path}: reader-contents link misses its declared entry")
                            if not link["text"].strip():
                                raise ValueError(f"{path}: reader-contents link has no visible label")
                else:
                    if parser.navigation_markers or native_home_links or native_contents_links:
                        raise ValueError(
                            f"{path}: central-overlay-only reader contains an undeclared native program shell"
                        )
                relative = path.relative_to(reader_root).as_posix()
                expected_contents = (
                    [] if relative in contents_relatives else list(contents_paths)
                )
                expected_contents.extend(
                    declared_by_relative[value]
                    for value in overlay_links.get(relative, [])
                )
                if len(expected_contents) != len(set(expected_contents)):
                    raise ValueError(
                        f"{row['root']}: duplicate reader overlay target for {relative}"
                    )
                validate_central_overlay(
                    path,
                    parser,
                    [course_id],
                    interfaces,
                    expected_contents,
                )

            reachable = graph_reachable(reader_outbound, {entry_path})
            if reachable != declared_reader_files:
                missing = sorted(
                    path.relative_to(reader_root.resolve()).as_posix()
                    for path in declared_reader_files - reachable
                )
                raise ValueError(
                    f"{row['root']}: declared entry cannot reach reader closure {missing}"
                )
            for path in declared_reader_files - {entry_path}:
                if not reader_outbound[path] & contents_paths:
                    raise ValueError(
                        f"{path}: non-entry reader page cannot return directly to declared contents"
                    )

            landing = ROOT / Path(*row["landing_document"].split("/"))
            landing_text = landing.read_text(encoding="utf-8")
            landing_scope = (
                course_article(landing, course_id)
                if landing.resolve() == interface_document.resolve()
                else landing_text
            )
            landing_targets = article_targets(
                landing, landing_scope, contract["site_origin"]
            )
            for suffix in row["landing_required_paths"]:
                expected_target = (
                    reader_root / (suffix if suffix else "index.html")
                ).resolve()
                if expected_target not in landing_targets:
                    raise ValueError(
                        f"{landing}: missing scoped inbound reader link "
                        f"{row['public_root'] + suffix}"
                    )

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
                "entry_path": entry_relative,
                "declared_contents_paths": len(contents_paths),
                "entry_reachable_documents": len(reachable),
                "non_entry_contents_returns": len(html_files) - 1,
            })

        convention_discovered = {
            path.resolve()
            for path in (ROOT / "docs").rglob("*.html")
            if "reader" in path.relative_to(ROOT / "docs").parts
            or path.relative_to(ROOT / "docs").parts[0] == "readers"
        }
        unregistered_convention_readers = convention_discovered - configured_reader_files
        if unregistered_convention_readers:
            missing = sorted(
                path.relative_to(ROOT).as_posix()
                for path in unregistered_convention_readers
            )
            raise ValueError(f"reader-root registry is not closed; unregistered={missing}")

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
            entry_path = (gateway_root / Path(*row["entry_path"].split("/"))).resolve()
            declared_by_relative = {
                path.relative_to(gateway_root).as_posix(): path.resolve()
                for path in html_files
            }
            declared_gateway_files = set(declared_by_relative.values())
            if entry_path not in declared_gateway_files:
                raise ValueError(f"{row['root']}: gateway entry_path is outside the registered HTML closure")
            closure = row.get("navigation_closure")
            if len(html_files) > 1 and not isinstance(closure, dict):
                raise ValueError(
                    f"{row['root']}: multi-page gateway lacks navigation_closure"
                )
            if closure is None:
                closure = {
                    "contents_paths": [row["entry_path"]],
                    "documents": [
                        {"path": row["entry_path"], "contents_paths": []}
                    ],
                }
            if set(closure) != {"contents_paths", "documents"}:
                raise ValueError(f"{row['root']}: invalid gateway navigation_closure")
            contents_relatives = closure["contents_paths"]
            documents = closure["documents"]
            if (
                not isinstance(contents_relatives, list)
                or not contents_relatives
                or len(contents_relatives) != len(set(contents_relatives))
                or row["entry_path"] not in contents_relatives
                or not set(contents_relatives).issubset(declared_by_relative)
                or not isinstance(documents, list)
            ):
                raise ValueError(f"{row['root']}: invalid gateway closure paths")
            document_map: dict[str, list[str]] = {}
            for document in documents:
                if not isinstance(document, dict) or set(document) != {
                    "path",
                    "contents_paths",
                }:
                    raise ValueError(f"{row['root']}: invalid gateway document closure row")
                relative = document["path"]
                targets = document["contents_paths"]
                if (
                    not isinstance(relative, str)
                    or relative in document_map
                    or relative not in declared_by_relative
                    or not isinstance(targets, list)
                    or len(targets) != len(set(targets))
                    or not set(targets).issubset(contents_relatives)
                    or relative in targets
                ):
                    raise ValueError(
                        f"{row['root']}: invalid gateway contents mapping for {relative!r}"
                    )
                document_map[relative] = targets
            if set(document_map) != set(declared_by_relative):
                raise ValueError(f"{row['root']}: gateway per-document closure changed")
            if document_map[row["entry_path"]]:
                raise ValueError(f"{row['root']}: gateway entry must not return to itself")
            for relative in set(document_map) - {row["entry_path"]}:
                if not document_map[relative]:
                    raise ValueError(
                        f"{row['root']}/{relative}: non-entry gateway page lacks a declared contents return"
                    )
            contents_paths = {
                declared_by_relative[value] for value in contents_relatives
            }
            gateway_outbound: dict[Path, set[Path]] = {}
            for path in html_files:
                resolved_path = path.resolve()
                if resolved_path in configured_gateway_files or resolved_path in configured_reader_files:
                    raise ValueError(f"gateway file appears under another registered root: {path}")
                configured_gateway_files.add(resolved_path)
                parser = html_parser(path)
                gateway_outbound[resolved_path] = article_targets(
                    path, path.read_text(encoding="utf-8"), contract["site_origin"]
                ) & declared_gateway_files
                native_home_links = [
                    link for link in parser.home_links if not link["placement"]
                ]
                if not native_home_links:
                    raise ValueError(f"{path}: gateway lacks data-program-home")
                for link in native_home_links:
                    target, fragment = resolve_href(path, link["href"])
                    if target != interface_document.resolve() or fragment != f"course-{course_id}":
                        raise ValueError(f"{path}: gateway program-home link is not course-scoped")
                    if not link["text"].strip():
                        raise ValueError(f"{path}: gateway program-home link has no label")
                validate_central_overlay(path, parser, [course_id], interfaces)
                relative = path.relative_to(gateway_root).as_posix()
                required_returns = {
                    declared_by_relative[value] for value in document_map[relative]
                }
                if not required_returns.issubset(gateway_outbound[resolved_path]):
                    missing = sorted(
                        target.relative_to(gateway_root.resolve()).as_posix()
                        for target in required_returns - gateway_outbound[resolved_path]
                    )
                    raise ValueError(
                        f"{path}: gateway lacks declared direct contents returns {missing}"
                    )
            reachable = graph_reachable(gateway_outbound, {entry_path})
            if reachable != declared_gateway_files:
                missing = sorted(
                    path.relative_to(gateway_root.resolve()).as_posix()
                    for path in declared_gateway_files - reachable
                )
                raise ValueError(
                    f"{row['root']}: gateway entry cannot reach declared closure {missing}"
                )
            gateway_results.append({
                "course_id": course_id,
                "root": row["root"],
                "state": row["state"],
                "html_documents": len(html_files),
                "entry_path": row["entry_path"],
                "declared_contents_paths": len(contents_paths),
                "entry_reachable_documents": len(reachable),
                "non_entry_contents_returns": len(html_files) - 1,
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
                if parser.surface_navigation_markers != 2 or sorted(parser.surface_navigation_placements) != ["bottom", "top"]:
                    raise ValueError(f"{path}: expected top and bottom course-surface navigation")
                marked_home_links = [
                    link for link in parser.home_links if link["course_id"] and link["course_card"]
                ]
                expected_card_keys = {
                    (interface_locale, course_id)
                    for interface_locale in interfaces
                    for course_id in ids
                }
                actual_card_keys = {
                    (link["interface_locale"], link["course_id"])
                    for link in marked_home_links
                }
                if actual_card_keys != expected_card_keys:
                    raise ValueError(f"{path}: localized course-card return set changed")
                for interface_locale, course_id in sorted(expected_card_keys):
                    interface_document = ROOT / Path(*interfaces[interface_locale]["document"].split("/"))
                    matches = []
                    for link in marked_home_links:
                        if (link["interface_locale"], link["course_id"]) != (interface_locale, course_id):
                            continue
                        target, fragment = resolve_href(path, link["href"])
                        if target == interface_document.resolve() and fragment == f"course-{course_id}":
                            matches.append(link["placement"])
                        if not link["text"].strip():
                            raise ValueError(f"{path}: course return link has no visible label")
                    if sorted(matches) != ["bottom", "top"]:
                        raise ValueError(
                            f"{path}: {interface_locale}/course-{course_id} needs exact top/bottom returns"
                        )
                    article = course_article(interface_document, course_id)
                    key = (interface_locale, course_id)
                    surface_docs_by_course.setdefault(key, set()).add(resolved_path)
                    interface_outbound_by_course.setdefault(
                        key,
                        article_targets(interface_document, article, contract["site_origin"]),
                    )
                expected_root_locales = set(interfaces)
                if {link["interface_locale"] for link in parser.program_root_links} != expected_root_locales:
                    raise ValueError(f"{path}: localized program-root return set changed")
                for interface_locale, interface in sorted(interfaces.items()):
                    target_document = (ROOT / Path(*interface["document"].split("/"))).resolve()
                    matches = []
                    for link in parser.program_root_links:
                        if link["interface_locale"] != interface_locale:
                            continue
                        target, fragment = resolve_href(path, link["href"])
                        if target == target_document and not fragment:
                            matches.append(link["placement"])
                        if not link["text"].strip():
                            raise ValueError(f"{path}: program-root link has no visible label")
                    if sorted(matches) != ["bottom", "top"]:
                        raise ValueError(f"{path}: {interface_locale} program root needs exact top/bottom returns")

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
                validate_central_overlay(path, parser, [], interfaces)
                target_document = (ROOT / Path(*row["target_document"].split("/"))).resolve()
                unscoped = parser.program_root_links
                matches = 0
                for link in unscoped:
                    target, fragment = resolve_href(path, link["href"])
                    if target == target_document and not fragment and link["placement"] in {"top", "bottom"}:
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
        navigation_overlay_documents = (
            reader_html_documents
            + gateway_html_documents
            + course_surface_html_documents
            + sum(bool(row["navigation_required"]) for row in generic_surfaces)
        )
        if navigation_overlay_documents != summary.get("navigation_overlay_documents"):
            raise ValueError("navigation overlay closure disagrees with the declared summary")

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
            "navigation_overlay_documents": navigation_overlay_documents,
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
