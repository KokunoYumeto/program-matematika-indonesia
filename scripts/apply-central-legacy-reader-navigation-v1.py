#!/usr/bin/env python3
"""Add a reversible program/course backlink shell to legacy central readers.

This bounded transformer owns only the three configured docs/readers roots.  On
its first run it freezes both the pre-overlay and hosted identities.  Later runs
accept only one of those two identities per file, which makes regeneration
idempotent without treating the navigation shell as part of the mathematical
source body.
"""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
import sys
from pathlib import Path

from central_surface_navigation_overlay_v1 import strip_central_surface_overlay


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "backend" / "authority" / "central-reader-navigation-legacy-source-lock-v1.json"
READERS = (
    ("D40", "docs/readers/d40/unit13", 42),
    ("D40", "docs/readers/d40/unit14", 50),
    ("D90", "docs/readers/d90/original-02", 1),
)
MARKER = 'data-program-navigation="v1"'
RETURN_MARKER = "data-program-return"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fact(path: str, data: bytes) -> dict[str, object]:
    return {"path": path, "bytes": len(data), "sha256": sha256(data)}


def relative_href(source_file: Path, target: Path, *, directory: bool = False) -> str:
    value = posixpath.relpath(target.as_posix(), source_file.parent.as_posix())
    if directory:
        value = value.removesuffix("/index.html") + "/"
    return value


def transform(course_id: str, reader_root: Path, path: Path, source: bytes) -> bytes:
    text = source.decode("utf-8")
    if MARKER in text or RETURN_MARKER in text:
        raise ValueError(f"source already contains a partial navigation shell: {path}")
    body = re.search(r"<body(?:\s[^>]*)?>", text, flags=re.IGNORECASE)
    if body is None or len(re.findall(r"</body>", text, flags=re.IGNORECASE)) != 1:
        raise ValueError(f"HTML body anchors changed: {path}")
    program_document = ROOT / "docs" / "id" / "index.html"
    program_href = relative_href(path, program_document, directory=True) + f"#course-{course_id}"
    contents_href = None
    if path != reader_root / "index.html":
        contents_href = relative_href(path, reader_root / "index.html")
    contents = (
        f' · <a data-reader-contents href="{contents_href}">Daftar isi pembaca</a>'
        if contents_href is not None
        else ""
    )
    navigation = (
        '<nav data-program-navigation="v1" aria-label="Navigasi program">'
        f'<a data-program-home href="{program_href}">← Kembali ke Program Matematika</a>'
        f"{contents}</nav>"
    )
    program_return = (
        f'<p data-program-return><a data-program-home href="{program_href}">'
        '← Kembali ke Program Matematika</a></p>'
    )
    top_anchor = re.search(
        r'<a\s+class="skip-link"[^>]*>.*?</a>', text, flags=re.IGNORECASE | re.DOTALL
    )
    if top_anchor is not None:
        text = text[: top_anchor.end()] + "\n" + navigation + text[top_anchor.end() :]
    else:
        text = text[: body.end()] + "\n" + navigation + text[body.end() :]
    text = re.sub(
        r"</body>", program_return + "\n</body>", text, count=1, flags=re.IGNORECASE
    )
    return text.encode("utf-8")


def remove_existing_overlay(path: Path, data: bytes) -> bytes:
    """Recover the exact pre-overlay bytes during initial lock creation only."""
    text = data.decode("utf-8")
    if text.count(MARKER) != 1 or text.count(RETURN_MARKER) != 1:
        raise ValueError(f"cannot recover a complete navigation overlay: {path}")
    text, top_count = re.subn(
        r'\n<nav data-program-navigation="v1".*?</nav>',
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text, bottom_count = re.subn(
        r'\n<p data-program-return>.*?</p>',
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if top_count != 1 or bottom_count != 1 or MARKER in text or RETURN_MARKER in text:
        raise ValueError(f"navigation overlay recovery was not exact: {path}")
    return text.encode("utf-8")


def load_lock() -> dict[str, object] | None:
    if not LOCK_PATH.is_file():
        return None
    data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if data.get("schema") != "central-reader-navigation-legacy-source-lock-v1":
        raise ValueError("legacy navigation source-lock schema changed")
    expected_roots = [row[1] for row in READERS]
    if data.get("reader_roots") != expected_roots:
        raise ValueError("legacy navigation source-lock root order changed")
    rows = data.get("files")
    if not isinstance(rows, list) or len(rows) != sum(row[2] for row in READERS):
        raise ValueError("legacy navigation source-lock must contain exactly 93 rows")
    expected_paths: set[str] = set()
    binding_by_path: dict[str, tuple[str, str]] = {}
    for course_id, relative_root, expected_html in READERS:
        reader_root = ROOT / Path(*relative_root.split("/"))
        html_files = sorted(reader_root.rglob("*.html"), key=lambda path: path.as_posix())
        if len(html_files) != expected_html:
            raise ValueError(f"{relative_root}: live HTML closure changed before lock replay")
        for path in html_files:
            relative = path.relative_to(ROOT).as_posix()
            expected_paths.add(relative)
            binding_by_path[relative] = (course_id, relative_root)
    seen: set[str] = set()
    for row in rows:
        source = row.get("source", {})
        hosted = row.get("hosted", {})
        path = source.get("path")
        if not isinstance(path, str) or path in seen or path not in expected_paths:
            raise ValueError("legacy navigation source-lock contains a duplicate or unknown path")
        seen.add(path)
        course_id, reader_root = binding_by_path[path]
        if row.get("course_id") != course_id or row.get("reader_root") != reader_root:
            raise ValueError(f"legacy navigation source-lock binding changed: {path}")
        if hosted.get("path") != path:
            raise ValueError(f"legacy navigation source/hosted path mismatch: {path}")
        for name, value in (("source", source), ("hosted", hosted)):
            if not isinstance(value.get("bytes"), int) or value["bytes"] <= 0:
                raise ValueError(f"legacy navigation {name} byte fact invalid: {path}")
            if not re.fullmatch(r"[0-9a-f]{64}", str(value.get("sha256", ""))):
                raise ValueError(f"legacy navigation {name} hash fact invalid: {path}")
    if seen != expected_paths:
        raise ValueError("legacy navigation source-lock path closure is incomplete")
    return data


def main() -> int:
    try:
        prior = load_lock()
        prior_rows = {
            row["source"]["path"]: row for row in prior.get("files", [])
        } if prior is not None else {}
        rows: list[dict[str, object]] = []
        writes: list[tuple[Path, bytes]] = []
        for course_id, relative_root, expected_html in READERS:
            reader_root = ROOT / Path(*relative_root.split("/"))
            html_files = sorted(reader_root.rglob("*.html"), key=lambda path: path.as_posix())
            if len(html_files) != expected_html:
                raise ValueError(
                    f"{relative_root}: HTML inventory {len(html_files)} != {expected_html}"
                )
            for path in html_files:
                relative = path.relative_to(ROOT).as_posix()
                current_hosted = path.read_bytes()
                current = strip_central_surface_overlay(current_hosted, relative)
                locked = prior_rows.get(relative)
                if locked is None:
                    if prior is not None:
                        raise ValueError(f"unlocked legacy reader file appeared: {relative}")
                    source = (
                        remove_existing_overlay(path, current)
                        if MARKER.encode("utf-8") in current
                        else current
                    )
                    hosted = transform(course_id, reader_root, path, source)
                else:
                    source_fact = locked["source"]
                    hosted_fact = locked["hosted"]
                    current_fact = fact(relative, current)
                    if current_fact == hosted_fact:
                        hosted = current
                    elif current_fact == source_fact:
                        source = current
                        hosted = transform(course_id, reader_root, path, source)
                        if fact(relative, hosted) != hosted_fact:
                            raise ValueError(f"legacy navigation replay changed: {relative}")
                    else:
                        raise ValueError(f"legacy reader is neither frozen source nor hosted projection: {relative}")
                if current_hosted != hosted:
                    writes.append((path, hosted))
                if locked is None:
                    rows.append({
                        "course_id": course_id,
                        "reader_root": relative_root,
                        "source": fact(relative, source),
                        "hosted": fact(relative, hosted),
                    })
                else:
                    rows.append(locked)
        for path, payload in writes:
            path.write_bytes(payload)
        if prior is None:
            payload = {
                "schema": "central-reader-navigation-legacy-source-lock-v1",
                "status": "frozen",
                "transformation": "deterministic-removable-navigation-shell",
                "mathematical_body_rewritten": False,
                "reader_roots": [row[1] for row in READERS],
                "files": rows,
            }
            LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
            LOCK_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        print(json.dumps({
            "status": "pass",
            "reader_roots": len(READERS),
            "html_documents": len(rows),
            "files_written": len(writes),
            "source_lock": LOCK_PATH.relative_to(ROOT).as_posix(),
        }, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"legacy central reader navigation: FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
