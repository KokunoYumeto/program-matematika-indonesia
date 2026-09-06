#!/usr/bin/env python3
"""Validate D110's pinned English source body and the shared navigation shell."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIRROR = ROOT / "docs" / "en" / "courses" / "D110"
OVERLAY = ROOT / "backend" / "authority" / "central-course-surface-navigation-overlay-v1.json"
EVIDENCE = ROOT / "docs" / "interface" / "evidence" / "d110-original-english-mirror.json"
ADMISSION = ROOT / "task-logbooks" / "d110-en-mirror-v2" / "admission-report.json"
PRE_NAVIGATION_VALIDATION = ROOT / "task-logbooks" / "d110-en-mirror-v2" / "validation-report.json"
PRE_NAVIGATION_INVENTORY = ROOT / "task-logbooks" / "d110-en-mirror-v2" / "final-inventory.json"
APPLIER = ROOT / "scripts" / "apply-central-course-surface-navigation-v1.py"
REPORT = ROOT / "task-logbooks" / "d110-en-mirror-v2" / "central-validation-report.json"


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fact(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(payload), "sha256": sha256(payload)}


def main() -> int:
    spec = importlib.util.spec_from_file_location("central_navigation_applier", APPLIER)
    if spec is None or spec.loader is None:
        raise ValueError("central navigation applier cannot be loaded")
    applier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(applier)

    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    pre_navigation_validation = json.loads(PRE_NAVIGATION_VALIDATION.read_text(encoding="utf-8"))
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

    if evidence["course_id"] != "D110" or evidence["content_language"] != "en":
        raise ValueError("D110 evidence identity changed")
    if evidence["source"]["source_revision"] != admission["commit"]:
        raise ValueError("source revision differs from the admission receipt")
    if evidence["source"]["source_root_tree"] != admission["tree"]:
        raise ValueError("source tree differs from the admission receipt")
    if not admission["passed"] or admission["upstream_html_git_blobs_recovered_count"] != 16:
        raise ValueError("pre-navigation source admission is incomplete")
    if not pre_navigation_validation["passed"] or pre_navigation_validation["errors"]:
        raise ValueError("pre-navigation dependency and link validation is incomplete")

    closure = evidence["closure"]
    expected_receipts = {
        ADMISSION: closure["admission_report_sha256"],
        PRE_NAVIGATION_VALIDATION: closure["pre_navigation_validation_report_sha256"],
        PRE_NAVIGATION_INVENTORY: closure["pre_navigation_inventory_sha256"],
        OVERLAY: closure["central_navigation_overlay_receipt_sha256"],
    }
    for path, expected_hash in expected_receipts.items():
        if sha256(path.read_bytes()) != expected_hash:
            raise ValueError(f"evidence hash changed: {path.relative_to(ROOT).as_posix()}")

    pages = {row["path"]: row for row in admission["pages"]}
    overlay_rows = {
        Path(row["document"]).name: row
        for row in overlay["files"]
        if row["document"].startswith("docs/en/courses/D110/")
    }
    html_paths = sorted(MIRROR.glob("*.html"), key=lambda path: path.name)
    if set(pages) != {path.name for path in html_paths} or set(overlay_rows) != set(pages):
        raise ValueError("D110 HTML closure differs between source and overlay evidence")
    if len(html_paths) != 16 or closure["html_files"] != 16:
        raise ValueError("D110 HTML count changed")

    verified_pages = []
    for path in html_paths:
        logical = path.relative_to(ROOT).as_posix()
        payload = path.read_bytes()
        row = overlay_rows[path.name]
        if row["role"] != "reader" or row["course_ids"] != ["D110"]:
            raise ValueError(f"{logical}: overlay role/course binding changed")
        hosted = row["hosted_surface"]
        if len(payload) != hosted["bytes"] or sha256(payload) != hosted["sha256"]:
            raise ValueError(f"{logical}: hosted bytes differ from the central overlay receipt")
        text = payload.decode("utf-8")
        if text.count('data-central-surface-navigation="v1"') != 2:
            raise ValueError(f"{logical}: standard top/bottom navigation is incomplete")
        if "D110_PROGRAM_NAV" in text:
            raise ValueError(f"{logical}: obsolete D110-specific navigation remains")
        source_payload = applier.strip_owned_overlay(text, logical).encode("utf-8")
        source = row["source_body"]
        admitted = pages[path.name]
        if len(source_payload) != source["bytes"] or sha256(source_payload) != source["sha256"]:
            raise ValueError(f"{logical}: central overlay is not exactly reversible")
        if source["bytes"] != admitted["admitted_bytes"] or source["sha256"] != admitted["admitted_sha256"]:
            raise ValueError(f"{logical}: stripped source body differs from pinned admission")
        verified_pages.append({"document": logical, "source_body": source, "hosted_surface": hosted})

    all_files = sorted(path for path in MIRROR.rglob("*") if path.is_file())
    total_bytes = sum(path.stat().st_size for path in all_files)
    if len(all_files) != closure["all_mirror_files"] or total_bytes != closure["all_mirror_bytes_after_standard_navigation"]:
        raise ValueError("D110 complete mirror inventory changed")

    rights = {row["component"]: row["license"] for row in evidence["source"]["component_rights"]}
    expected_rights = {
        "book text": "CC BY 4.0",
        "repository code and build assets": "Apache-2.0",
        "vendored MathJax 4.1.3 runtime": "Apache-2.0",
        "retained Sphinx, Read the Docs, and static assets": "component notices retained",
    }
    if rights != expected_rights:
        raise ValueError("component-scoped rights evidence changed")

    result = {
        "schema": "d110-central-original-english-mirror-validation-v1",
        "status": "pass",
        "source_revision": admission["commit"],
        "source_tree": admission["tree"],
        "mirror": {"files": len(all_files), "bytes": total_bytes, "html_documents": len(html_paths)},
        "checks": {
            "all_upstream_html_bodies_recovered_before_navigation": True,
            "standard_navigation_is_top_bottom_and_reversible": True,
            "all_reader_pages_return_to_course_and_program_via_central_contract": True,
            "component_scoped_rights_are_preserved": True,
            "external_core_runtime_dependencies": 0,
        },
        "authority": {
            "evidence": fact(EVIDENCE),
            "admission": fact(ADMISSION),
            "pre_navigation_validation": fact(PRE_NAVIGATION_VALIDATION),
            "pre_navigation_inventory": fact(PRE_NAVIGATION_INVENTORY),
            "navigation_overlay": fact(OVERLAY),
            "validator": fact(Path(__file__).resolve()),
        },
        "pages": verified_pages,
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    REPORT.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
