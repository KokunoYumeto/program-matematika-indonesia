"""Normalize the removable central-site navigation shell around staged HTML.

Reader-specific manifests bind the native reader plus its original one-locale
navigation.  The central site adds a second, independently removable shell so
every hosted page can return to every interface locale.  Stagers call this
module before comparing a live destination with their own manifest.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import replace
from pathlib import Path
from typing import TypeVar


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

T = TypeVar("T")


def strip_central_surface_overlay(payload: bytes, logical: str) -> bytes:
    text = payload.decode("utf-8")
    marker_count = text.count(MARKER)
    if marker_count not in (0, 2):
        raise ValueError(f"{logical}: malformed central-surface marker count {marker_count}")
    stripped, top_count = TOP_OVERLAY_RE.subn("", text)
    stripped, bottom_count = BOTTOM_OVERLAY_RE.subn("", stripped)
    if top_count != marker_count // 2 or bottom_count != marker_count // 2:
        raise ValueError(f"{logical}: central-surface overlay is not exactly removable")
    return stripped.encode("utf-8")


def inventory_without_central_surface_overlay(root: Path, facts: list[T]) -> list[T]:
    normalized: list[T] = []
    for fact in facts:
        path = root / Path(*fact.path.split("/"))
        if path.suffix.lower() != ".html":
            normalized.append(fact)
            continue
        payload = strip_central_surface_overlay(path.read_bytes(), fact.path)
        normalized.append(
            replace(
                fact,
                bytes=len(payload),
                sha256=hashlib.sha256(payload).hexdigest(),
            )
        )
    return normalized


def remove_central_surface_overlays_in_tree(root: Path) -> int:
    writes: list[tuple[Path, bytes]] = []
    for path in sorted(root.rglob("*.html"), key=lambda item: item.as_posix()):
        payload = path.read_bytes()
        stripped = strip_central_surface_overlay(
            payload, path.relative_to(root).as_posix()
        )
        if stripped != payload:
            writes.append((path, stripped))
    for path, payload in writes:
        path.write_bytes(payload)
    return len(writes)
