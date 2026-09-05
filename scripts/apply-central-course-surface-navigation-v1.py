#!/usr/bin/env python3
"""Apply the reversible program-return shell to every classified course surface."""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "backend" / "authority" / "central-reader-navigation-v1.json"
RECEIPT_PATH = (
    ROOT
    / "backend"
    / "authority"
    / "central-course-surface-navigation-overlay-v1.json"
)
MARKER = 'data-central-surface-navigation="v1"'
TOP_OVERLAY_RE = re.compile(
    r'\n<nav data-central-surface-navigation="v1" data-placement="top"'
    r' aria-label="[^"]+">.*?</nav>',
    flags=re.DOTALL,
)
BOTTOM_OVERLAY_RE = re.compile(
    r'<nav data-central-surface-navigation="v1" data-placement="bottom"'
    r' aria-label="[^"]+">.*?</nav>\n',
    flags=re.DOTALL,
)
BODY_OPEN_RE = re.compile(r"<body\b[^>]*>", flags=re.IGNORECASE)
BODY_CLOSE_RE = re.compile(r"</body>", flags=re.IGNORECASE)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fact(path: str, payload: bytes) -> dict[str, object]:
    return {"path": path, "bytes": len(payload), "sha256": sha256_bytes(payload)}


def href_between(source: Path, target: Path, fragment: str = "") -> str:
    relative = os.path.relpath(target, start=source.parent).replace("\\", "/")
    return relative + (f"#{fragment}" if fragment else "")


def strip_owned_overlay(text: str, logical: str) -> str:
    marker_count = text.count(MARKER)
    if marker_count not in (0, 2):
        raise ValueError(f"{logical}: malformed central-surface marker count {marker_count}")
    stripped, top_replacements = TOP_OVERLAY_RE.subn("", text)
    stripped, bottom_replacements = BOTTOM_OVERLAY_RE.subn("", stripped)
    if top_replacements != marker_count // 2 or bottom_replacements != marker_count // 2:
        raise ValueError(f"{logical}: central-surface overlay is not exactly reversible")
    return stripped


def navigation_markup(
    source: Path,
    targets: list[tuple[Path, str | None]],
    contents: list[Path],
    locale: str,
    placement: str,
) -> str:
    aria = "Navigasi Program Matematika" if locale == "id" else "Mathematics Program navigation"
    lead = "Program:" if locale == "id" else "Program:"
    links: list[str] = []
    for target, course_id in targets:
        fragment = f"course-{course_id}" if course_id else ""
        href = href_between(source, target, fragment)
        if course_id:
            label = (
                f"Kembali ke kartu mata kuliah {course_id}"
                if locale == "id"
                else f"Back to course {course_id}"
            )
            course_attr = f' data-course-id="{html.escape(course_id)}"'
        else:
            label = "Kembali ke Program Matematika" if locale == "id" else "Back to the Mathematics Program"
            course_attr = ""
        links.append(
            f'<a data-program-home{course_attr} href="{html.escape(href)}">'
            f'{html.escape(label)}</a>'
        )
    for target in contents:
        href = href_between(source, target)
        label = "Buka halaman terkait" if locale == "id" else "Open related page"
        links.append(
            f'<a data-course-surface-contents href="{html.escape(href)}">'
            f'{html.escape(label)}</a>'
        )
    return (
        f'<nav data-central-surface-navigation="v1" data-placement="{placement}" '
        f'aria-label="{html.escape(aria)}"><span>{html.escape(lead)}</span> '
        + " · ".join(links)
        + "</nav>"
    )


def inject_overlay(
    logical: str,
    payload: bytes,
    targets: list[tuple[Path, str | None]],
    contents: list[Path],
    locale: str,
) -> tuple[bytes, bytes]:
    text = payload.decode("utf-8")
    source_text = strip_owned_overlay(text, logical)
    body_open = list(BODY_OPEN_RE.finditer(source_text))
    body_close = list(BODY_CLOSE_RE.finditer(source_text))
    if len(body_open) != 1 or len(body_close) != 1 or body_open[0].end() >= body_close[0].start():
        raise ValueError(f"{logical}: expected one well-ordered body element")
    path = ROOT / logical
    top = navigation_markup(path, targets, contents, locale, "top")
    bottom = navigation_markup(path, targets, contents, locale, "bottom")
    target_text = (
        source_text[: body_open[0].end()]
        + "\n"
        + top
        + source_text[body_open[0].end() : body_close[0].start()]
        + bottom
        + "\n"
        + source_text[body_close[0].start() :]
    )
    target_payload = target_text.encode("utf-8")
    if strip_owned_overlay(target_text, logical) != source_text:
        raise ValueError(f"{logical}: overlay removal does not reproduce the source body")
    return source_text.encode("utf-8"), target_payload


def main() -> int:
    try:
        contract_payload = CONTRACT_PATH.read_bytes()
        contract = json.loads(contract_payload.decode("utf-8"))
        interfaces = contract["interfaces"]
        course_ids: set[str] = set()
        for interface in interfaces.values():
            document = ROOT / interface["document"]
            course_ids.update(
                re.findall(
                    r'<article\b[^>]*\bid="course-([A-Z][0-9]+)"',
                    document.read_text(encoding="utf-8"),
                    flags=re.IGNORECASE,
                )
            )
        if len(course_ids) != 40:
            raise ValueError("localized course-card authority does not expose 40 course IDs")

        specifications: list[dict[str, object]] = []
        declared_course_paths: set[str] = set()
        for surface in contract["course_surfaces"]:
            root = ROOT / surface["root"]
            declared = {document["path"] for document in surface["documents"]}
            actual = {
                path.relative_to(root).as_posix()
                for path in root.rglob("*.html")
                if path.is_file()
            }
            if actual != declared:
                raise ValueError(
                    f"{surface['root']}: course-surface closure changed; "
                    f"missing={sorted(actual - declared)}, stale={sorted(declared - actual)}"
                )
            interface_target = ROOT / interfaces[surface["locale"]]["document"]
            for document in surface["documents"]:
                logical = (Path(surface["root"]) / document["path"]).as_posix()
                if logical in declared_course_paths:
                    raise ValueError(f"duplicate course-surface document: {logical}")
                declared_course_paths.add(logical)
                ids = list(document["course_ids"])
                if not ids or len(ids) != len(set(ids)) or not set(ids).issubset(course_ids):
                    raise ValueError(f"{logical}: invalid course-card binding {ids}")
                contents_paths = list(document.get("contents_paths", []))
                if len(contents_paths) != len(set(contents_paths)) or not set(contents_paths).issubset(declared):
                    raise ValueError(f"{logical}: invalid section-contents binding {contents_paths}")
                specifications.append({
                    "logical": logical,
                    "locale": surface["locale"],
                    "state": surface["state"],
                    "course_ids": ids,
                    "targets": [(interface_target, course_id) for course_id in ids],
                    "contents": [root / value for value in contents_paths],
                })

        for surface in contract["generic_surfaces"]:
            if not surface["navigation_required"]:
                continue
            logical = surface["document"]
            if logical in declared_course_paths:
                raise ValueError(f"generic surface overlaps a course surface: {logical}")
            specifications.append({
                "logical": logical,
                "locale": surface["locale"],
                "state": surface["state"],
                "course_ids": [],
                "targets": [(ROOT / surface["target_document"], None)],
                "contents": [],
            })

        expected = int(contract["summary"]["course_surface_html_documents"]) + sum(
            bool(row["navigation_required"]) for row in contract["generic_surfaces"]
        )
        if len(specifications) != expected:
            raise ValueError(f"overlay scope {len(specifications)} != expected {expected}")

        writes: list[tuple[Path, bytes]] = []
        rows: list[dict[str, object]] = []
        for specification in sorted(specifications, key=lambda row: str(row["logical"])):
            logical = str(specification["logical"])
            path = ROOT / logical
            if not path.is_file() or not path.resolve().is_relative_to((ROOT / "docs").resolve()):
                raise ValueError(f"classified surface is missing or escapes docs: {logical}")
            source_payload, target_payload = inject_overlay(
                logical,
                path.read_bytes(),
                specification["targets"],
                specification["contents"],
                str(specification["locale"]),
            )
            writes.append((path, target_payload))
            rows.append({
                "document": logical,
                "state": specification["state"],
                "locale": specification["locale"],
                "course_ids": specification["course_ids"],
                "source_body": fact(logical, source_payload),
                "hosted_surface": fact(logical, target_payload),
                "program_return_links_per_placement": len(specification["targets"]),
                "section_contents_links_per_placement": len(specification["contents"]),
                "placements": ["top", "bottom"],
                "source_body_replay_exact": True,
            })

        for path, payload in writes:
            if path.read_bytes() != payload:
                path.write_bytes(payload)

        receipt = {
            "schema": "central-course-surface-navigation-overlay-v1",
            "status": "pass",
            "authority": {
                "contract": fact(
                    CONTRACT_PATH.relative_to(ROOT).as_posix(), contract_payload
                ),
                "script": fact(
                    Path(__file__).resolve().relative_to(ROOT).as_posix(),
                    Path(__file__).resolve().read_bytes(),
                ),
            },
            "scope": {
                "course_surface_roots": len(contract["course_surfaces"]),
                "course_surface_html_documents": int(
                    contract["summary"]["course_surface_html_documents"]
                ),
                "generic_html_documents_with_overlay": sum(
                    bool(row["navigation_required"])
                    for row in contract["generic_surfaces"]
                ),
                "total_transformed_html_documents": len(rows),
            },
            "invariants": {
                "top_and_bottom_return_navigation": True,
                "course_returns_are_card_scoped": True,
                "shared_surfaces_link_every_served_course": True,
                "overlay_is_exactly_removable": True,
                "mathematical_body_rewritten": False,
            },
            "files": rows,
        }
        RECEIPT_PATH.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(json.dumps({
            "status": "pass",
            "course_surface_html_documents": contract["summary"]["course_surface_html_documents"],
            "generic_html_documents_with_overlay": sum(
                bool(row["navigation_required"]) for row in contract["generic_surfaces"]
            ),
            "transformed_html_documents": len(rows),
            "receipt": fact(
                RECEIPT_PATH.relative_to(ROOT).as_posix(), RECEIPT_PATH.read_bytes()
            ),
        }, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"central course-surface navigation overlay: FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
