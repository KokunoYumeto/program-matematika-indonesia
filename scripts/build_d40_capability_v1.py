"""Build the isolated, zero-copy D40 learning-capability adapter.

The build reads a hash-locked native repository and writes only the requested
adapter projection.  It never executes TeX, notebooks, or FEniCSx.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from d40_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    DIONNE_COMMIT,
    DIONNE_TREE,
    FENICSX_COMMIT,
    FENICSX_TREE,
    MANIFEST_URL,
    NATIVE_CORPUS_ID,
    PDF_IDENTITY,
    PDF_URL,
    RECORD_URL,
    RELEASE_MANIFEST_IDENTITY,
    ZIP_IDENTITY,
    ZIP_URL,
    D40Error,
    expected_source_ids,
    expected_unit_ids,
    file_identity,
    read_json,
    read_jsonl,
    tree_identity,
    write_bytes,
    write_json,
    write_jsonl,
)


SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parent.parent
ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/d40-capability-v1"
DEFAULT_NATIVE = PROJECT.parent / "partial-differential-equations-id"
REQUIRED_ROLES = {
    "completion_receipt",
    "terminology_ledger",
    "terminology_qa",
    "source_corrections",
    "terminology_witness",
    "dionne_objects",
    "complete_corpus",
    "complete_components",
    "complete_imports",
    "complete_objects",
    "complete_relations",
    "complete_rights",
    "complete_spans",
    "complete_checksums_json",
    "complete_checksums_csv",
    "final_backend_verification",
    "mastery_validation",
    "translation_qa",
    "html_build_receipt",
    "html_visual_qa",
    "pdf_visual_qa",
    "release_manifest",
    "release_receipt",
    "release_independent_verification",
    "publication_receipt",
    "public_readback",
    "component_license_boundaries",
    "public_pdf",
    "public_zip",
}


def fail(code: str) -> None:
    raise D40Error(code)


def csv_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8-sig").splitlines()))


def verify_lock(
    native: Path,
    lock: dict[str, Any],
    allow_identity_only_public_artifacts: bool = False,
) -> dict[str, dict[str, Any]]:
    if lock.get("schema") != "d40-capability-source-lock/1":
        fail("D40-BUILD-LOCK-SCHEMA")
    if (
        lock.get("course_id") != COURSE_ID
        or lock.get("owner_lane") != "O010"
        or lock.get("native_corpus_id") != NATIVE_CORPUS_ID
    ):
        fail("D40-BUILD-LOCK-IDENTITY")
    if lock.get("native_repository") != {
        "expected_sibling_directory": "partial-differential-equations-id",
        "dionne_commit": DIONNE_COMMIT,
        "dionne_tree": DIONNE_TREE,
        "fenicsx_commit": FENICSX_COMMIT,
        "fenicsx_tree": FENICSX_TREE,
    }:
        fail("D40-BUILD-LOCK-AUTHORITY")
    roles: dict[str, dict[str, Any]] = {}
    native_resolved = native.resolve()
    for item in lock.get("inputs", []):
        role = item.get("role")
        if not isinstance(role, str) or role in roles:
            fail("D40-BUILD-LOCK-ROLE")
        relative = Path(str(item.get("path", "")))
        if relative.is_absolute() or ".." in relative.parts:
            fail("D40-BUILD-LOCK-PATH")
        path = (native_resolved / relative).resolve()
        try:
            path.relative_to(native_resolved)
        except ValueError:
            fail("D40-BUILD-LOCK-ESCAPE")
        if not path.is_file():
            if not (allow_identity_only_public_artifacts and role in {"public_pdf", "public_zip"}):
                fail("D40-BUILD-LOCK-MISSING:" + relative.as_posix())
        elif file_identity(path) != {"bytes": item.get("bytes"), "sha256": item.get("sha256")}:
            fail("D40-BUILD-LOCK-DRIFT:" + relative.as_posix())
        roles[role] = item
    if set(roles) != REQUIRED_ROLES:
        fail("D40-BUILD-LOCK-ROLE-SET")
    return roles


def role_path(native: Path, roles: dict[str, dict[str, Any]], role: str) -> Path:
    return native / roles[role]["path"]


def archive_member(source_path: str) -> str:
    prefix = "composite/"
    if not source_path.startswith(prefix):
        fail("D40-BUILD-ARCHIVE-PATH:" + source_path)
    member = source_path[len(prefix) :]
    pure = PurePosixPath(member)
    if (
        not member
        or "\\" in member
        or ":" in member
        or pure.is_absolute()
        or pure.as_posix() != member
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        fail("D40-BUILD-ARCHIVE-PATH:" + source_path)
    return member


def projected_metadata(row: dict[str, Any]) -> dict[str, Any]:
    """Copy only native identity metadata, never a semantic/code body."""

    allowed = {
        "object_id",
        "parent_id",
        "kind",
        "component",
        "rights_id",
        "source_id",
        "source_path",
        "source_order",
        "node",
        "surface",
        "run_id",
        "cell_index",
        "cell_type",
        "jupytext_pair",
        "identity",
        "identities",
        "record_identity",
        "title",
        "locale_neutral_id",
        "verdict",
        "rights_scope",
    }
    return {key: row[key] for key in row if key in allowed}


def support_record(
    status: str,
    source_anchor: str | None,
    label: str | None,
    href: str | None,
) -> dict[str, Any]:
    return {"status": status, "source_anchor": source_anchor, "label": label, "href": href}


def build_views(
    units: list[dict[str, Any]],
    rights: list[dict[str, Any]],
    capabilities: dict[str, Any],
    execution: dict[str, Any],
) -> tuple[bytes, bytes]:
    style = """
    :root{font-family:system-ui,sans-serif;color:#17243a;background:#f3f6fa;line-height:1.5}
    body{max-width:78rem;margin:auto;padding:1.5rem}header,.panel,article{background:white;border:1px solid #d7dfeb;border-radius:.8rem;padding:1rem;margin:.8rem 0}
    h1,h2,h3{line-height:1.2}nav a,.actions a{display:inline-block;margin:.25rem .5rem .25rem 0;padding:.5rem .75rem;border-radius:.45rem;background:#174ea6;color:white;text-decoration:none}
    code{overflow-wrap:anywhere}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(18rem,1fr));gap:.75rem}.muted{color:#526176}.warning{border-left:.35rem solid #a46200;padding-left:.8rem}
    table{width:100%;border-collapse:collapse}th,td{border:1px solid #d7dfeb;padding:.45rem;text-align:left;vertical-align:top}summary{cursor:pointer;font-weight:700}
    """

    def unit_cards(educator: bool) -> str:
        groups = [
            ("practice_problem", "48 latihan"),
            ("assessment_item", "16 butir asesmen"),
            ("computational_lab", "4 laboratorium"),
        ]
        sections: list[str] = []
        for kind, heading in groups:
            cards: list[str] = []
            for unit in (row for row in units if row["unit_type"] == kind):
                paths = "<br>".join(f"<code>{html.escape(path)}</code>" for path in unit["archive_member_paths"])
                support = ", ".join(
                    f"{html.escape(name)}: {len(ids)}" for name, ids in sorted(unit["support_ids"].items())
                )
                detail = ""
                if educator:
                    identity = html.escape(json.dumps(unit["native_identity"], ensure_ascii=False, sort_keys=True))
                    detail = (
                        f"<p><strong>Rights:</strong> <code>{html.escape(unit['rights_id'])}</code></p>"
                        f"<details><summary>Identitas byte/span native</summary><code>{identity}</code></details>"
                    )
                cards.append(
                    f'<article data-unit-id="{html.escape(unit["unit_id"])}" '
                    f'data-source-id="{html.escape(unit["native_source_id"])}">'
                    f"<h3>{html.escape(unit['title_id'])}</h3>"
                    f"<p><strong>ID native:</strong> <code>{html.escape(unit['unit_id'])}</code></p>"
                    f"<p><strong>Lokasi di dalam ZIP:</strong><br>{paths}</p>"
                    f"<p><strong>Dukungan:</strong> {html.escape(support or 'metadata anak tidak ada')}</p>"
                    f"{detail}<p><a href=\"{ZIP_URL}\">Unduh ZIP terverifikasi</a></p></article>"
                )
            sections.append(f"<section><h2>{heading}</h2><div class=\"grid\">{''.join(cards)}</div></section>")
        return "".join(sections)

    access = capabilities["accessibility"]
    access_note = (
        "HTML semantik luring berada di dalam ZIP pada <code>reader/html/index.html</code>. "
        "Bukti mencatat 24.118 elemen MathML statis dan nol dependensi jaringan runtime; "
        "ini bukan klaim MathJax runtime, WCAG, atau hasil uji teknologi bantu. "
        "Status penandaan PDF tidak diketahui karena tidak ada bukti tagging."
    )
    common_header = (
        "<!doctype html><html lang=\"id\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<style>{style}</style><title>D40 — Persamaan Diferensial Parsial</title></head><body>"
    )
    actions = (
        f'<nav aria-label="Akses publik"><a href="{PDF_URL}">PDF lengkap</a>'
        f'<a href="{ZIP_URL}">ZIP lengkap + HTML luring</a>'
        f'<a href="{RECORD_URL}">Rekaman Zenodo</a></nav>'
    )
    learner = (
        common_header
        + "<header><h1>D40 — Persamaan Diferensial Parsial</h1>"
        + "<p>Indeks pembelajar berbasis 68 identitas primer native. Isi tetap berada pada rilis D40.</p>"
        + actions
        + "</header><section class=\"panel warning\"><h2>Cara mengakses</h2><p>"
        + access_note
        + "</p></section>"
        + unit_cards(False)
        + "<section class=\"panel\"><h2>Bukti komputasional</h2>"
        + f"<p>{execution['counts']['executed_notebooks']} notebook solusi tereksekusi, "
        + f"{execution['counts']['execution_surfaces']} surface eksekusi, dan "
        + f"{execution['counts']['required_cells']} sel wajib tercatat sebagai metadata di adapter. "
        + "Notebook tersedia hanya sebagai anggota ZIP.</p></section>"
        + "</body></html>"
    )
    rights_rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(str(row['rights_id']))}</code></td>"
        f"<td>{html.escape(str(row.get('component', '')))}</td>"
        f"<td>{html.escape(str(row.get('license_id', '')))}</td>"
        f"<td>{html.escape(str(row.get('rights_assertion', 'asserted by native record')))}</td>"
        "</tr>"
        for row in rights
    )
    educator = (
        common_header
        + "<header><h1>D40 — tampilan pengajar</h1>"
        + "<p>Identitas pembelajar dan pengajar sama; metadata hak, hash, dan batas akses ditampilkan eksplisit.</p>"
        + actions
        + "</header><section class=\"panel warning\"><h2>Batas klaim</h2><p>"
        + access_note
        + "</p><p>Tidak ada lisensi agregasi. Hak Dionne, mastery, FEniCSx, bukti runtime, dan metadata tetap terpisah pada tingkat rekaman.</p></section>"
        + "<section class=\"panel\"><h2>Matriks hak native</h2><table><thead><tr><th>ID hak</th><th>Komponen</th><th>Lisensi/status</th><th>Asersi</th></tr></thead><tbody>"
        + rights_rows
        + "</tbody></table></section>"
        + unit_cards(True)
        + "</body></html>"
    )
    return learner.encode("utf-8"), educator.encode("utf-8")


def build(
    native: Path,
    output: Path,
    lock_path: Path,
    allow_identity_only_public_artifacts: bool = False,
) -> dict[str, Any]:
    lock = read_json(lock_path)
    roles = verify_lock(native, lock, allow_identity_only_public_artifacts)
    corpus = read_json(role_path(native, roles, "complete_corpus"))
    dionne_objects = read_jsonl(role_path(native, roles, "dionne_objects"))
    components = read_jsonl(role_path(native, roles, "complete_components"))
    imports = read_jsonl(role_path(native, roles, "complete_imports"))
    objects = read_jsonl(role_path(native, roles, "complete_objects"))
    relations = read_jsonl(role_path(native, roles, "complete_relations"))
    rights = read_jsonl(role_path(native, roles, "complete_rights"))
    checksums = read_json(role_path(native, roles, "complete_checksums_json"))
    final_backend = read_json(role_path(native, roles, "final_backend_verification"))
    mastery = read_json(role_path(native, roles, "mastery_validation"))
    translation = read_json(role_path(native, roles, "translation_qa"))
    terminology_witness = read_json(role_path(native, roles, "terminology_witness"))
    html_receipt = read_json(role_path(native, roles, "html_build_receipt"))
    html_visual = read_json(role_path(native, roles, "html_visual_qa"))
    pdf_visual = read_json(role_path(native, roles, "pdf_visual_qa"))
    release_manifest = read_json(role_path(native, roles, "release_manifest"))
    release_receipt = read_json(role_path(native, roles, "release_receipt"))
    release_independent = read_json(role_path(native, roles, "release_independent_verification"))
    publication = read_json(role_path(native, roles, "publication_receipt"))
    readback = read_json(role_path(native, roles, "public_readback"))
    license_boundaries = read_json(role_path(native, roles, "component_license_boundaries"))
    terminology_rows = csv_rows(role_path(native, roles, "terminology_ledger"))
    correction_rows = csv_rows(role_path(native, roles, "source_corrections"))
    completion = read_json(role_path(native, roles, "completion_receipt"))

    if (
        completion.get("schema") != "o010-d40-final-completion-receipt-v1"
        or completion.get("verdict") != "PASS_O010_D40_COMPLETE_PUBLIC_READBACK_CLOSED"
        or completion.get("authority")
        != {
            "dionne_commit": DIONNE_COMMIT,
            "dionne_tree": DIONNE_TREE,
            "fenicsx_commit": FENICSX_COMMIT,
            "fenicsx_tree": FENICSX_TREE,
        }
    ):
        fail("D40-BUILD-COMPLETION-AUTHORITY")

    if corpus.get("schema") != "o010-d40-complete-backend-v1" or corpus.get("corpus_id") != NATIVE_CORPUS_ID or corpus.get("status") != "complete":
        fail("D40-BUILD-CORPUS")
    if final_backend.get("verdict") != "PASS_FINAL_INDEPENDENT_D40_COMPLETE_BACKEND":
        fail("D40-BUILD-FINAL-BACKEND")
    if mastery.get("verdict") != "PASS" or mastery.get("counts") != {
        "assessment_files": 2,
        "assessment_items": 16,
        "lab_files": 8,
        "lab_pairs": 4,
        "practice_files": 6,
        "practice_items": 48,
    }:
        fail("D40-BUILD-MASTERY")
    if html_receipt.get("verdict") != "PASS" or html_visual.get("verdict") != "PASS_COMPLETE_HTML_VISUAL_QA_FINAL":
        fail("D40-BUILD-HTML")
    html_access = html_receipt.get("reader", {}).get("accessibility", {})
    if html_access.get("mathml_elements") != 24_118 or html_access.get("runtime_network_dependencies") != 0:
        fail("D40-BUILD-HTML-MATH")
    if pdf_visual.get("pdf", {}).get("sha256") != PDF_IDENTITY["sha256"]:
        fail("D40-BUILD-PDF-QA")
    if release_receipt.get("verdict") != "PASS_RELEASE_PACKAGE" or release_independent.get("verdict") != "PASS_INDEPENDENT_RELEASE_PACKAGE_VERIFICATION":
        fail("D40-BUILD-RELEASE-QA")
    if publication.get("publication_status") != "published" or publication.get("access_right") != "open" or publication.get("all_public_bytes_match") is not True:
        fail("D40-BUILD-PUBLICATION")
    if readback.get("verdict") != "PASS_INDEPENDENT_ANONYMOUS_PUBLIC_READBACK" or readback.get("file_count") != 7:
        fail("D40-BUILD-READBACK")
    readback_files = {row["filename"]: row for row in readback.get("files", [])}
    for filename, identity in (
        ("PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_LENGKAP.pdf", PDF_IDENTITY),
        ("D40_COMPLETE_ID_20260831.zip", ZIP_IDENTITY),
    ):
        row = readback_files.get(filename, {})
        if any(
            record.get("bytes") != identity["bytes"] or record.get("sha256") != identity["sha256"]
            for record in (row.get("local", {}), row.get("anonymous_download", {}))
        ):
            fail("D40-BUILD-PUBLIC-IDENTITY-EVIDENCE:" + filename)
    if license_boundaries.get("aggregation_license") is not None:
        fail("D40-BUILD-BLANKET-LICENSE")
    if len(components) != 3 or len(imports) != 3 or len(objects) != 851 or len(relations) != 1638 or len(rights) != 5:
        fail("D40-BUILD-NATIVE-COUNTS")

    object_by_id = {row["object_id"]: row for row in objects}
    if len(object_by_id) != len(objects):
        fail("D40-BUILD-OBJECT-DUPLICATE")
    by_source = {row["source_id"]: row for row in objects if row.get("source_id") in expected_source_ids()}
    primary_source_ids = corpus.get("coverage", {}).get("mastery", {}).get("primary_ids", [])
    if len(primary_source_ids) != 68 or set(primary_source_ids) != expected_source_ids() or set(row["object_id"] for row in by_source.values()) != expected_unit_ids():
        fail("D40-BUILD-PRIMARY-IDENTITIES")

    release_entries = {row["path"]: row for row in release_manifest.get("entries", [])}
    if len(release_entries) != 271 or release_manifest.get("entry_count") != 271:
        fail("D40-BUILD-RELEASE-MANIFEST")
    entries_by_sha: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in release_entries.values():
        entries_by_sha[entry["sha256"]].append(entry)

    children: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in objects:
        if row.get("parent_id"):
            children[row["parent_id"]].append(row)
    prerequisites = [row for row in relations if row.get("relation") == "prerequisite_for"]
    if len(prerequisites) != 108:
        fail("D40-BUILD-PREREQUISITES")
    previous_by_target: dict[str, list[str]] = defaultdict(list)
    for relation in prerequisites:
        previous_by_target[relation["target_id"]].append(relation["source_id"])

    units: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []
    for projection_order, source_id in enumerate(primary_source_ids, 1):
        native_row = by_source[source_id]
        identity_values = native_row.get("identities") or [native_row.get("identity")]
        if not identity_values or any(not value for value in identity_values):
            fail("D40-BUILD-UNIT-IDENTITY:" + source_id)
        member_paths = sorted({archive_member(value["path"]) for value in identity_values})
        if any(path not in release_entries for path in member_paths):
            fail("D40-BUILD-MISSING-ARCHIVE-MEMBER:" + source_id)
        child_groups: dict[str, list[str]] = defaultdict(list)
        for child in children[native_row["object_id"]]:
            child_groups[child["kind"]].append(child["object_id"])
        support_ids = {key: sorted(value) for key, value in sorted(child_groups.items())}
        unit = {
            "schema": "d40-capability-unit/1",
            "course_id": COURSE_ID,
            "unit_id": native_row["object_id"],
            "native_object_id": native_row["object_id"],
            "native_source_id": source_id,
            "unit_type": native_row["kind"],
            "title_id": native_row["title"]["id"],
            "native_parent_id": native_row["parent_id"],
            "rights_id": native_row["rights_id"],
            "locale": "id-ID",
            "locale_neutral_id": native_row.get("locale_neutral_id") is True,
            "projection_order": projection_order,
            "native_identity": native_row.get("identities") or native_row.get("identity"),
            "archive_member_paths": member_paths,
            "support_ids": support_ids,
            "content_embedded": False,
            "access_route_id": "d40.route.zip." + native_row["object_id"],
        }
        units.append(unit)
        routes.append(
            {
                "schema": "d40-capability-route/1",
                "adapter_route_id": unit["access_route_id"],
                "native_object_id": unit["unit_id"],
                "native_source_id": source_id,
                "target_kind": "public_zip_download_with_member_locator",
                "access_url": ZIP_URL,
                "public_container": {"filename": "D40_COMPLETE_ID_20260831.zip", **ZIP_IDENTITY},
                "member_paths": member_paths,
                "member_url": None,
                "directly_addressable": False,
            }
        )

    if Counter(row["unit_type"] for row in units) != Counter({"practice_problem": 48, "assessment_item": 16, "computational_lab": 4}):
        fail("D40-BUILD-UNIT-KINDS")

    dionne_import = next((row for row in imports if row.get("import_id") == "o010.d40.import.dionne-full"), None)
    if not dionne_import or dionne_import.get("object_count") != 3920 or dionne_import.get("endpoint_ids_sha256") != "cd12f638f0a8b7cfb39630d16199c519a3103978372069bc1f8cb4223edfbfbd":
        fail("D40-BUILD-DIONNE-IMPORT")
    if len(dionne_objects) != 3920 or len({row.get("object_id") for row in dionne_objects}) != 3920:
        fail("D40-BUILD-DIONNE-OBJECTS")
    dionne_chapters = [projected_metadata(row) for row in dionne_objects if row.get("kind") == "chapter"]
    supports_relations = [row for row in relations if row.get("relation") == "supports"]
    if len(dionne_chapters) != 14 or len(supports_relations) != 130:
        fail("D40-BUILD-DIONNE-THEORY-LINKS")
    chapter_ids = {row["object_id"] for row in dionne_chapters}
    if any(row["source_id"] not in chapter_ids or row["target_id"] not in expected_unit_ids() for row in supports_relations):
        fail("D40-BUILD-DIONNE-SUPPORT-ENDPOINTS")
    theory_links = {
        "schema": "d40-capability-theory-links/1",
        "course_id": COURSE_ID,
        "zero_copy": True,
        "native_bodies_copied": 0,
        "dionne_objects_source": {key: roles["dionne_objects"][key] for key in ("path", "bytes", "sha256")},
        "chapters": dionne_chapters,
        "supports_relations": supports_relations,
        "relationship_semantics": "native many-to-many supports edges; no single-chapter assignment is inferred",
    }
    execution_kinds = {
        "executed_notebooks": "executed_solution_notebook",
        "execution_surfaces": "execution_surface",
        "required_cells": {"notebook_code_cell", "notebook_markdown_cell"},
        "source_nodes": "fenicsx_source_node",
    }
    execution_lists: dict[str, list[dict[str, Any]]] = {}
    for label, kind in execution_kinds.items():
        selected = [row for row in objects if row.get("kind") in kind] if isinstance(kind, set) else [row for row in objects if row.get("kind") == kind]
        projected = [projected_metadata(row) for row in selected]
        if label == "executed_notebooks":
            for native_row, projected_row in zip(selected, projected):
                matches = [entry for entry in entries_by_sha[native_row["identity"]["sha256"]] if entry["path"].startswith("solutions/fenicsx/")]
                if len(matches) != 1:
                    fail("D40-BUILD-NOTEBOOK-ARCHIVE-MEMBER:" + native_row["object_id"])
                projected_row["archive_member_path"] = matches[0]["path"]
                projected_row["direct_online_url"] = None
        execution_lists[label] = projected
    execution_counts = {
        "executed_notebooks": len(execution_lists["executed_notebooks"]),
        "execution_surfaces": len(execution_lists["execution_surfaces"]),
        "required_cells": len(execution_lists["required_cells"]),
        "code_cells": sum(row["kind"] == "notebook_code_cell" for row in execution_lists["required_cells"]),
        "markdown_cells": sum(row["kind"] == "notebook_markdown_cell" for row in execution_lists["required_cells"]),
        "source_nodes": len(execution_lists["source_nodes"]),
    }
    if execution_counts != {"executed_notebooks": 4, "execution_surfaces": 8, "required_cells": 116, "code_cells": 54, "markdown_cells": 62, "source_nodes": 18}:
        fail("D40-BUILD-EXECUTION")
    executed_as = [row for row in relations if row.get("relation") == "executed_as"]
    execution = {
        "schema": "d40-capability-execution-evidence/1",
        "course_id": COURSE_ID,
        "run_id": corpus["coverage"]["fenicsx"]["run_id"],
        "projection": "metadata_only_preexecuted_evidence",
        "adapter_execution_performed": False,
        "counts": execution_counts,
        **execution_lists,
        "lab_execution_relations": executed_as,
        "limitations": [
            "Notebook, Python, cache, log, and artifact bodies are not embedded in the adapter.",
            "The adapter reports native executed evidence; it does not replay FEniCSx.",
            "Runtime/cache/log evidence remains record-level/unasserted, distinct from CC-BY-4.0 scientific tutorial artifacts.",
        ],
    }

    correction_counts = dict(sorted(Counter(row["status"] for row in correction_rows).items()))
    queued = [row for row in correction_rows if row["status"] == "queued"]
    terminology_counts = dict(sorted(Counter(row["status"] for row in terminology_rows).items()))
    reference_closure = translation.get("reference_closure", {})
    evidence = {
        "schema": "d40-capability-evidence/1",
        "course_id": COURSE_ID,
        "dionne_import": {
            **dionne_import,
            "projection_mode": "reference_only",
            "zero_copy": True,
            "native_records_copied": 0,
        },
        "native_backend": {
            "schema": corpus["schema"],
            "status": corpus["status"],
            "topology": corpus["topology"],
            "coverage": corpus["coverage"],
            "semantic_checksums": checksums,
            "final_independent_verdict": final_backend["verdict"],
        },
        "source_corrections": {
            "path": roles["source_corrections"]["path"],
            "bytes": roles["source_corrections"]["bytes"],
            "sha256": roles["source_corrections"]["sha256"],
            "record_count": len(correction_rows),
            "status_counts": correction_counts,
            "queued_correction_ids": [row["correction_id"] for row in queued],
            "queued_records": queued,
        },
        "terminology": {
            "path": roles["terminology_ledger"]["path"],
            "bytes": roles["terminology_ledger"]["bytes"],
            "sha256": roles["terminology_ledger"]["sha256"],
            "record_count": len(terminology_rows),
            "status_counts": terminology_counts,
            "qa_receipt": {key: roles["terminology_qa"][key] for key in ("path", "bytes", "sha256")},
            "witness": {key: roles["terminology_witness"][key] for key in ("path", "bytes", "sha256")},
            "witness_verdict": terminology_witness["decision"]["verdict"],
            "propagation_required": terminology_witness["decision"]["propagation_required"],
            "supported_current_terms": terminology_witness["decision"]["supported_current_terms"],
            "witness_silent_on": terminology_witness["decision"]["silent_on"],
            "limitation": "The witness supports only the recorded classical/applied terms; silence is absence of evidence, not contrary evidence.",
        },
        "translation_qa": {
            "schema": translation["schema"],
            "verdict": translation["verdict"],
            "authority_commit": translation["authority_commit"],
            "file_count": len(translation["files"]),
            "failures": translation["failures"],
            "reference_closure": reference_closure,
            "reference_closure_authority": "deterministic_latex_build",
            "static_regex_unresolved_are_not_build_failures": True,
        },
        "release": {
            "manifest": {"schema": release_manifest["schema"], "status": release_manifest["status"], "entry_count": release_manifest["entry_count"], "payload_bytes": release_manifest["payload_bytes"], **RELEASE_MANIFEST_IDENTITY},
            "release_receipt_verdict": release_receipt["verdict"],
            "independent_release_verdict": release_independent["verdict"],
            "publication_status": publication["publication_status"],
            "access_right": publication["access_right"],
            "record_url": RECORD_URL,
            "doi": publication["doi"],
            "concept_doi": publication["conceptdoi"],
            "public_files": readback["files"],
            "all_public_bytes_match": publication["all_public_bytes_match"],
        },
        "receipt_bindings": [
            {key: roles[role][key] for key in ("role", "path", "bytes", "sha256")}
            for role in (
                "completion_receipt",
                "final_backend_verification",
                "mastery_validation",
                "html_build_receipt",
                "html_visual_qa",
                "pdf_visual_qa",
                "release_manifest",
                "release_receipt",
                "release_independent_verification",
                "publication_receipt",
                "public_readback",
            )
        ],
    }

    limitations = [
        "This thin adapter copies no native semantic, exercise, solution, code, notebook, or Dionne backend bodies.",
        "The complete semantic HTML reader is a member of the public ZIP, not a directly hosted file; no per-unit online URL is claimed.",
        "The HTML evidence records static semantic HTML with 24,118 MathML elements and zero runtime network dependencies; MathJax runtime is not claimed or required.",
        "No WCAG conformance or assistive-technology user-test result is claimed.",
        "PDF tagging and complete PDF accessibility are unknown because the supplied evidence does not establish them.",
        "The release is a mixed-rights aggregation with no blanket license; every projected object retains its native rights_id.",
        "Runtime/cache/log evidence remains record-level/unasserted and is not relicensed as FEniCSx tutorial content.",
        "Source correction O010-C002 remains queued; the adapter does not upgrade it to applied.",
        "The terminology witness is limited to classical/applied PDE usage and is silent on the recorded modern-analysis terms.",
        "Translation QA's static-regex unresolved references are not build failures; the receipt names the deterministic LaTeX build as the authoritative closure gate.",
        "The adapter reports pre-executed FEniCSx evidence and performs no computational replay.",
        "GitHub URLs in provenance are upstream sources, not a dedicated public repository for this Indonesian D40 edition.",
    ]
    course = {
        "schema": "d40-capability-course/1",
        "course_id": COURSE_ID,
        "owner_lane": "O010",
        "native_corpus_id": NATIVE_CORPUS_ID,
        "locale": "id-ID",
        "level": "D",
        "topic": "Analisis",
        "title_id": "Persamaan Diferensial Parsial",
        "prerequisites": ["B70", "C110", "D10", "D20"],
        "normalized_release_state": "verified_complete_public",
        "contract_2_3_1_conformance": "not_claimed",
        "content_projection": "zero_copy_metadata_only",
        "full_native_roundtrip_claimed": False,
        "aggregation_license": None,
        "rights_policy": "record-level; no blanket license",
        "source_authority": {
            "author": "Benoit Dionne",
            "work": "Partial Differential Equations",
            "license": "CC-BY-NC-SA-4.0",
            "commit": lock["native_repository"]["dionne_commit"],
            "tree": lock["native_repository"]["dionne_tree"],
        },
        "public_lineage": {
            "record_url": RECORD_URL,
            "doi": "10.5281/zenodo.22184259",
            "concept_doi": "10.5281/zenodo.22059503",
            "access": "public_open",
            "pdf": {"url": PDF_URL, **PDF_IDENTITY, "direct_public_file": True},
            "zip": {"url": ZIP_URL, **ZIP_IDENTITY, "direct_public_file": True},
            "offline_html": {
                "container_url": ZIP_URL,
                "member_path": "reader/html/index.html",
                "direct_online_url": None,
            },
            "github_edition_repository": None,
        },
    }
    capabilities = {
        "schema": "d40-capability-declarations/1",
        "course_id": COURSE_ID,
        "learner": {
            "complete_pdf_available": True,
            "complete_zip_available": True,
            "offline_html_in_zip": True,
            "direct_online_complete_html": False,
            "native_learning_identities": 68,
            "native_semantic_bodies_embedded": False,
            "full_native_roundtrip_claimed": False,
        },
        "educator": {
            "shared_unit_identities_with_learner": True,
            "record_level_rights_visible": True,
            "source_hashes_visible": True,
            "prerequisite_routes_visible": True,
            "source_and_runtime_rights_separated": True,
        },
        "coverage": {
            "practice_problems": 48,
            "assessment_items": 16,
            "computational_labs": 4,
            "executed_notebooks": 4,
            "execution_surfaces": 8,
            "required_notebook_cells": 116,
            "execution_artifacts_and_logs": 226,
            "dionne_imported_objects": 3920,
        },
        "accessibility": {
            "offline_html": {
                "availability": "public_zip_member_only",
                "entrypoint": "reader/html/index.html",
                "direct_online_url": None,
                "static_semantic_html": True,
                "html_language": "id-ID",
                "semantic_blocks": 775,
                "source_anchors": 1314,
                "figure_groups": 70,
                "localized_figure_alt_text": 70,
                "math_representation": "static_mathml",
                "mathml_elements": 24118,
                "runtime_mathjax_required": False,
                "mathjax_claimed": False,
                "runtime_network_dependencies": 0,
            },
            "pdf": {
                "pages": 679,
                "tagged_pdf_status": "unknown_not_evidenced",
                "tagged_pdf_claimed": False,
                "complete_tounicode_status": "unknown_not_evidenced",
                "wcag_conformance_claimed": False,
                "assistive_technology_user_testing_claimed": False,
            },
        },
        "limitations": limitations,
    }

    units_by_id = {row["unit_id"]: row for row in units}
    route_by_id = {row["native_object_id"]: row for row in routes}
    map_units = []
    for unit in units:
        support = unit["support_ids"]
        if unit["unit_type"] == "practice_problem":
            hint = support_record("complete", support["hint"][0], "Petunjuk", ZIP_URL)
            check = support_record("not_present", None, None, None)
            solution = support_record("complete", support["solution"][0], "Solusi lengkap", ZIP_URL)
        elif unit["unit_type"] == "assessment_item":
            hint = support_record("not_present", None, None, None)
            check = support_record("complete", support["rubric"][0], "Rubrik", ZIP_URL)
            solution = support_record("complete", support["solution"][0], "Solusi lengkap", ZIP_URL)
        else:
            hint = support_record("not_present", None, None, None)
            validation_ids = support.get("lab_validation", [])
            check = (
                support_record("complete", validation_ids[0], "Validasi native", ZIP_URL)
                if validation_ids
                else support_record("not_present", None, None, None)
            )
            solution = support_record("complete", support["lab_solution_document"][0], "Dokumen solusi", ZIP_URL)
        exercise = {
            "id": unit["unit_id"],
            "unit_id": unit["unit_id"],
            "title": unit["title_id"],
            "kind": unit["unit_type"],
            "sequence": 1,
            "curriculum_status": "complete_native_record",
            "href": ZIP_URL,
            "hint": hint,
            "check": check,
            "solution": solution,
        }
        map_units.append(
            {
                "id": unit["unit_id"],
                "title": unit["title_id"],
                "href": ZIP_URL,
                "sections": unit["archive_member_paths"],
                "objectives_href": None,
                "previous_units": sorted(set(previous_by_target[unit["unit_id"]])),
                "components": [
                    {
                        "id": unit["unit_id"],
                        "source": "d40.source.mastery",
                        "license": "CC-BY-NC-SA-4.0",
                        "rights_id": unit["rights_id"],
                    }
                ],
                "exercises": [exercise],
            }
        )
    prerequisite_routes = [
        {
            "id": row["relation_id"],
            "unit": row["target_id"],
            "prerequisite": row["source_id"],
            "required_for_course": True,
            "sections": route_by_id[row["target_id"]]["member_paths"],
            "exercises": [row["target_id"]],
            "href": ZIP_URL,
            "native_evidence": row["evidence"],
        }
        for row in prerequisites
    ]
    executed_by_lab: dict[str, list[str]] = {}
    for row in executed_as:
        executed_by_lab.setdefault(row["source_id"], []).append(row["target_id"])
    map_labs = []
    for unit in (row for row in units if row["unit_type"] == "computational_lab"):
        map_labs.append(
            {
                "id": unit["unit_id"],
                "unit": unit["unit_id"],
                "environment": "d40.environment.preexecuted-fenicsx",
                "exercise_ids": [unit["unit_id"]],
                # Preserve the native many-to-many topology: D40-L02 has two
                # execution artifacts and D40-L04 has none. Inventing a
                # one-artifact-per-lab mapping would falsify the source graph.
                "artifact_ids": sorted(executed_by_lab.get(unit["unit_id"], [])),
                "archive_member_paths": unit["archive_member_paths"],
            }
        )
    artifact_rows = [
        {"id": "d40.artifact.pdf", "kind": "complete-course-pdf", "path": PDF_URL, "availability": "direct_public_file", **PDF_IDENTITY},
        {"id": "d40.artifact.zip", "kind": "complete-course-archive", "path": ZIP_URL, "availability": "direct_public_file", **ZIP_IDENTITY},
        {"id": "d40.artifact.offline-html", "kind": "semantic-html-reader", "path": "reader/html/index.html", "availability": "public_zip_member_only", "container_url": ZIP_URL, "direct_online_url": None},
    ]
    artifact_rows.extend(
        {
            "id": row["object_id"],
            "kind": "executed-solution-notebook",
            "path": row["archive_member_path"],
            "availability": "public_zip_member_only",
            "container_url": ZIP_URL,
            "direct_online_url": None,
            "identity": row["identity"],
        }
        for row in execution_lists["executed_notebooks"]
    )
    relevant_relations = [
        row
        for row in relations
        if row.get("relation") in {"supports", "implemented_by", "executed_as", "computational_companion"}
        and (row.get("source_id") in units_by_id or row.get("target_id") in units_by_id)
    ]
    external_nodes = sorted(
        {
            endpoint
            for row in relevant_relations
            for endpoint in (row["source_id"], row["target_id"])
            if endpoint not in units_by_id
        }
        | chapter_ids
    )
    learning_map = {
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "locale": "id-ID",
        "native_dataset": NATIVE_CORPUS_ID,
        "source_catalog": {"path": "RELEASE_MANIFEST.json", **RELEASE_MANIFEST_IDENTITY, "url": MANIFEST_URL},
        "units": map_units,
        "prerequisite_routes": prerequisite_routes,
        "labs": map_labs,
        "environments": [
            {
                "id": "d40.environment.preexecuted-fenicsx",
                "runtime_version": "captured_by_native_execution_receipt_not_replayed",
                "lock": {key: roles["final_backend_verification"][key] for key in ("path", "bytes", "sha256")},
            }
        ],
        "artifacts": artifact_rows,
        "sources": [
            {"id": "d40.source.dionne", "role": "hash_bound_zero_copy_theory_import", "license": "CC-BY-NC-SA-4.0", "identity": dionne_import["endpoint_ids_sha256"], "rights_id": "o010.rights.dionne.core"},
            {"id": "d40.source.mastery", "role": "native_mastery_records", "license": "CC-BY-NC-SA-4.0", "identity": roles["complete_objects"]["sha256"], "rights_id": "o010.rights.d40.mastery"},
            {"id": "d40.source.fenicsx", "role": "localized_preexecuted_tutorial_evidence", "license": "CC-BY-4.0", "identity": corpus["coverage"]["fenicsx"]["run_id"], "rights_id": "o010.rights.fenicsx.tutorial"},
            {"id": "d40.source.runtime", "role": "runtime_cache_log_evidence", "license": "record-level/unasserted", "identity": roles["complete_rights"]["sha256"], "rights_id": "o010.rights.fenicsx.runtime-record"},
            {"id": "d40.source.terminology-witness", "role": "bounded_terminology_evidence", "license": terminology_witness["record"]["license"], "identity": roles["terminology_witness"]["sha256"]},
        ],
        "external_relation_nodes": external_nodes,
        "limitations": limitations,
    }

    output_files = {
        "data/capabilities.json": lambda path: write_json(path, capabilities),
        "data/course.json": lambda path: write_json(path, course),
        "data/evidence.json": lambda path: write_json(path, evidence),
        "data/execution.json": lambda path: write_json(path, execution),
        "data/learning-map.json": lambda path: write_json(path, learning_map),
        "data/routes.jsonl": lambda path: write_jsonl(path, routes),
        "data/rights.jsonl": lambda path: write_jsonl(path, rights),
        "data/theory-links.json": lambda path: write_json(path, theory_links),
        "data/units.jsonl": lambda path: write_jsonl(path, units),
    }
    for relative, writer in output_files.items():
        writer(output / relative)
    learner_html, educator_html = build_views(units, rights, capabilities, execution)
    write_bytes(output / "views/D40.html", learner_html)
    write_bytes(output / "views/D40-pengajar.html", educator_html)
    generated_paths = sorted([*output_files, "views/D40.html", "views/D40-pengajar.html"])
    output_rows = [{"path": relative, **file_identity(output / relative)} for relative in generated_paths]

    tooling_paths = [
        "scripts/d40_capability_model_v1.py",
        "scripts/build_d40_capability_v1.py",
        "scripts/validate_d40_capability_v1.py",
        "scripts/package_d40_capability_v1.py",
        "backend/course-capsule-v1/adapters/d40-capability-v1/README.md",
        "backend/course-capsule-v1/adapters/d40-capability-v1/input/source-lock.json",
    ]
    fixture_root = ADAPTER / "fixtures/negative"
    tooling_paths.extend(path.relative_to(PROJECT).as_posix() for path in sorted(fixture_root.glob("*.json"), key=lambda p: p.name))
    tooling = []
    for relative in tooling_paths:
        path = PROJECT / relative
        if not path.is_file():
            fail("D40-BUILD-MISSING-TOOLING:" + relative)
        tooling.append({"path": relative, **file_identity(path)})

    manifest = {
        "schema": "d40-capability-manifest/1",
        "course_id": COURSE_ID,
        "owner_lane": "O010",
        "native_family": "partial_differential_equations",
        "contract": CONTRACT,
        "contract_projection_path": "data/learning-map.json",
        "contract_2_3_1_conformance": "not_claimed",
        "inputs": lock["inputs"],
        "outputs": output_rows,
        "output_tree_sha256": tree_identity(output, generated_paths)["sha256"],
        "tooling": tooling,
        "counts": {
            "learning_units": 68,
            "practice_problems": 48,
            "assessment_items": 16,
            "computational_labs": 4,
            "prerequisite_relations": 108,
            "executed_notebooks": 4,
            "execution_surfaces": 8,
            "required_notebook_cells": 116,
            "rights_records": 5,
            "dionne_imported_objects": 3920,
            "dionne_chapters": 14,
            "native_supports_relations": 130,
        },
        "projection": {
            "native_ids_preserved": True,
            "native_bodies_copied": False,
            "dionne_import_mode": "hash_bound_reference_only",
            "full_native_roundtrip_claimed": False,
            "record_level_rights_preserved": True,
            "blanket_license_asserted": False,
            "archive_members_claimed_as_direct_urls": False,
            "public_state_changed": False,
        },
        "public_release_status": "unchanged_not_published_by_adapter",
    }
    write_json(output / "manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--output-root", type=Path, default=ADAPTER)
    parser.add_argument("--source-lock", type=Path, default=ADAPTER / "input/source-lock.json")
    parser.add_argument(
        "--allow-identity-only-public-artifacts",
        action="store_true",
        help="Permit absent PDF/ZIP bytes only when their locked identities are proven by the included public readback receipt.",
    )
    args = parser.parse_args()
    manifest = build(
        args.native_root.resolve(),
        args.output_root.resolve(),
        args.source_lock.resolve(),
        args.allow_identity_only_public_artifacts,
    )
    print(
        json.dumps(
            {
                "state": "pass",
                "course_id": COURSE_ID,
                "outputs": len(manifest["outputs"]) + 1,
                "output_tree_sha256": manifest["output_tree_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (D40Error, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"D40 build failed: {exc}", file=sys.stderr)
        sys.exit(1)
