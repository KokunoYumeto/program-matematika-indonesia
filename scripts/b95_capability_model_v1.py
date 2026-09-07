"""Model and invariant helpers for the B95 zero-copy capability adapter.

The B95 producer is a deliberately separate checkout.  This module reads its
canonical export files and publication receipts, then projects only stable
metadata, identifiers, locators, hashes, and rights/evidence state.  Native
segment/localization bodies (and answer/solution bodies) are never copied into
the central adapter.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_NATIVE = PROJECT.parent / "openintro-statistics-id"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/b95-capability-v1"

COURSE_ID = "B95"
NATIVE_ROLE_ID = "R011"
NATIVE_COURSE_ID = "be02bb59-5807-512c-8ba1-f5d22a702812"
NATIVE_EDITION_ID = "fd249e50-2371-5c79-88c6-70abc1222771"
UPSTREAM_COMMIT = "fee25091fb24e89c36296fd67c48c1fcf7a93b6e"
UPSTREAM_TREE = "d61cc601e7d97759ce805900520f784d02a0489e"
UPSTREAM_REPOSITORY = "https://github.com/OpenIntroStat/openintro-statistics"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"
BOUNDARY_ID = "R011-B039"
RELEASE_ID = "R011-B039-v2026.09.01.2"
RELEASE_TAG = "r011-b039-2026.09.01.2"
REPOSITORY = "https://github.com/KokunoYumeto/statistika-berbasis-data-id"
RELEASE_URL = f"{REPOSITORY}/releases/tag/{RELEASE_TAG}"
GITHUB_DOWNLOAD_BASE = f"{REPOSITORY}/releases/download/{RELEASE_TAG}"
ZENODO_RECORD_ID = 22261912
ZENODO_CONCEPT_ID = 22059801
ZENODO_RECORD = f"https://zenodo.org/records/{ZENODO_RECORD_ID}"
READER_FILENAME = "00_STATISTIKA_BERBASIS_DATA_ID_R011-B039_WORKING_READER.pdf"
READER_GITHUB_URL = f"{GITHUB_DOWNLOAD_BASE}/{READER_FILENAME}"
READER_ZENODO_URL = f"{ZENODO_RECORD}/files/{READER_FILENAME}?download=1"

PUBLIC_RECEIPT_PATH = DEFAULT_NATIVE / "qa/b039-publication/R011-B039_FINAL_COMPLETION_RECEIPT.json"
GITHUB_RECEIPT_PATH = DEFAULT_NATIVE / (
    "qa/b039-publication/GITHUB_PUBLICATION_RECEIPT_R011-B039-v2026.09.01.2.json"
)
ZENODO_RECEIPT_PATH = DEFAULT_NATIVE / (
    "qa/b039-publication/ZENODO_PUBLICATION_RECEIPT_R011-B039-v2026.09.01.2.json"
)
RELEASE_MANIFEST_PATH = DEFAULT_NATIVE / "release/b039/R011-B039-v2026.09.01.2/07_RELEASE_MANIFEST.json"
CANDIDATE_MANIFEST_PATH = DEFAULT_NATIVE / (
    "backend/staging/b039/candidate-f6e61e290acc9844/CANDIDATE_MANIFEST.json"
)
REPLAY_RECEIPT_PATH = DEFAULT_NATIVE / (
    "backend/staging/b039/candidate-f6e61e290acc9844/B039_BACKEND_REPLAY.json"
)

CANONICAL_RECORD_FILES: tuple[tuple[str, str], ...] = (
    ("backend/exports/core/assets.jsonl", "asset"),
    ("backend/exports/core/concepts.jsonl", "concept"),
    ("backend/exports/core/corrections.jsonl", "correction"),
    ("backend/exports/core/courses.jsonl", "course"),
    ("backend/exports/core/editions.jsonl", "edition"),
    ("backend/exports/core/programs.jsonl", "program"),
    ("backend/exports/core/relations.jsonl", "relation"),
    ("backend/exports/core/resources.jsonl", "resource"),
    ("backend/exports/core/rights.jsonl", "rights"),
    ("backend/exports/core/segments.jsonl", "segment"),
    ("backend/exports/core/units.jsonl", "unit"),
    ("backend/exports/evidence/artifacts.jsonl", "artifact"),
    ("backend/exports/evidence/qa_events.jsonl", "qa_event"),
    ("backend/exports/locales/id-ID/localizations.jsonl", "localization"),
    ("backend/exports/locales/id-ID/terms.jsonl", "term"),
)
EXERCISE_CSV = "backend/exports/views/exercises_answers.csv"
EXPORT_MANIFEST = "backend/exports/manifest.json"

EXPECTED_RECORD_COUNTS = {
    "artifact": 1565,
    "asset": 947,
    "concept": 826,
    "correction": 302,
    "course": 1,
    "edition": 2,
    "localization": 2231,
    "program": 1,
    "qa_event": 484,
    "relation": 11127,
    "resource": 1,
    "rights": 80,
    "segment": 2231,
    "term": 859,
    "unit": 1089,
}
EXPECTED_UNIT_KINDS = {
    "answer": 1,
    "answer_layout": 2,
    "answer_section": 2,
    "book": 1,
    "chapter": 9,
    "chapter_front": 1,
    "chapter_intro": 4,
    "chapter_review": 1,
    "companion_gap": 105,
    "copyright_page": 1,
    "data_appendix": 1,
    "data_appendix_entry": 4,
    "exercise": 322,
    "guided_exercise": 126,
    "guided_solution": 15,
    "inline_public_answer": 28,
    "mastery_companion_gap": 54,
    "preface": 1,
    "public_answer": 54,
    "section": 35,
    "section_intro": 7,
    "section_review": 2,
    "semantic_subunit": 40,
    "solution": 138,
    "source_wrapper": 2,
    "subsection": 83,
    "table": 2,
    "title_page": 1,
    "translation_bundle": 1,
    "translation_range": 15,
    "worked_example": 31,
}

# Printed page starts are taken from the released reader's Indonesian table of
# contents.  These are context routes, not anchors into individual units.
CHAPTER_PAGE_STARTS = {
    1: 7,
    2: 40,
    3: 81,
    4: 136,
    5: 176,
    6: 216,
    7: 259,
    8: 322,
    9: 362,
}
CHAPTER_TITLES_ID = {
    1: "Pengantar data",
    2: "Merangkum data",
    3: "Probabilitas",
    4: "Distribusi variabel acak",
    5: "Dasar-dasar inferensi",
    6: "Inferensi untuk data kategoris",
    7: "Inferensi untuk data numerik",
    8: "Pengantar regresi linear",
    9: "Regresi berganda dan logistik",
}

FORBIDDEN_CONTENT_KEYS = {
    "answer_body",
    "body",
    "content",
    "exercise_text",
    "full_text",
    "native_body",
    "prompt",
    "prompt_text",
    "prose",
    "solution_body",
    "solution_text",
    "source_text",
    "target_text",
    "tex_body",
    "text",
}

# Explicit allow-list for the metadata ledger.  In particular, do not add
# arbitrary producer fields: several contain source/target prose or answer
# payloads.
SAFE_COMMON_KEYS = {
    "$schema",
    "id",
    "record_type",
    "status",
    "translation_state",
    "locale",
    "source_locale",
    "target_locale",
    "edition_id",
    "resource_id",
    "rights_component_ids",
    "parent_id",
    "order",
    "unit_id",
    "source_segment_id",
    "source_local_ids",
    "source_path",
    "target_path",
    "source_sha256",
    "target_sha256",
    "target_file_sha256",
    "sha256",
    "source_span",
    "target_span",
    "stable_key",
    "workflow_id",
    "boundary_id",
    "recorded_at",
    "supersedes_id",
    "unit_type",
    "exercise_id",
    "answer_availability",
    "title",
    "target_title",
    "name",
    "course_code",
    "curriculum_role",
    "program_id",
    "prerequisite_course_ids",
    "prerequisite_mapping_state",
    "edition_statement",
    "source_format",
    "resource_code",
    "official_reader",
    "authors",
    "branch_observed",
    "commit",
    "repository",
    "build_entrypoint",
    "asset_kind",
    "media_type",
    "bytes",
    "pages",
    "path",
    "evidence_copy_path",
    "artifact_kind",
    "result",
    "provenance",
    "qa_type",
    "required_result",
    "subject_id",
    "witness_artifact_id",
    "witness_path",
    "source_term",
    "target_term",
    "variants",
    "rejected_forms",
    "scope",
    "decision",
    "decision_reason",
    "evidence",
    "concept_id",
    "category",
    "confidence",
    "correction_type",
    "disposition",
    "affected_id",
    "license_expression",
    "license_url",
    "component_scope",
    "dependency_note",
    "verification_status",
    "restricted_solutions_included",
    "share_alike_required",
    "relation_type",
    "from_id",
    "to_id",
    "qualifier",
    "source_file",
}


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
        for row in rows
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity_bytes(data: bytes, *, path: str) -> dict[str, Any]:
    return {"path": path, "bytes": len(data), "sha256": sha256_bytes(data)}


def identity(path: Path, *, display_path: str | None = None) -> dict[str, Any]:
    return identity_bytes(path.read_bytes(), path=display_path or path.as_posix())


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


def _git(native_root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(native_root), *args], stderr=subprocess.STDOUT, timeout=60
    ).decode("utf-8", errors="replace").strip()


def native_checkout_identity(native_root: Path) -> dict[str, str]:
    return {"head": _git(native_root, "rev-parse", "HEAD"), "tree": _git(native_root, "rev-parse", "HEAD^{tree}")}


def _record_hash(row: dict[str, Any]) -> str:
    return sha256_bytes(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _canonical_rows(path: Path, expected_type: str) -> tuple[list[dict[str, Any]], list[bytes]]:
    data = path.read_bytes()
    if not data.endswith(b"\n"):
        raise ValueError(f"B95 JSONL is not LF terminated: {path}")
    rows: list[dict[str, Any]] = []
    raw_lines: list[bytes] = []
    for number, line in enumerate(data.splitlines(), 1):
        if not line:
            continue
        row = json.loads(line.decode("utf-8"))
        canonical = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if line != canonical:
            raise ValueError(f"B95 JSONL row {number} is not canonical: {path}")
        if row.get("record_type") != expected_type:
            raise ValueError(f"B95 record type mismatch in {path}: {row.get('record_type')!r}")
        if not row.get("id"):
            raise ValueError(f"B95 record without id in {path}:{number}")
        rows.append(row)
        raw_lines.append(line)
    return rows, raw_lines


def _load_rows(native_root: Path) -> tuple[list[dict[str, Any]], list[bytes], dict[str, list[dict[str, Any]]]]:
    all_rows: list[dict[str, Any]] = []
    all_raw: list[bytes] = []
    by_file: dict[str, list[dict[str, Any]]] = {}
    for relative, expected_type in CANONICAL_RECORD_FILES:
        rows, raw = _canonical_rows(native_root / relative, expected_type)
        by_file[relative] = rows
        all_rows.extend(rows)
        all_raw.extend(raw)
    ids = [row["id"] for row in all_rows]
    if len(ids) != len(set(ids)):
        duplicates = [item for item, count in Counter(ids).items() if count > 1]
        raise ValueError(f"B95 duplicate native ids: {duplicates[:3]}")
    return all_rows, all_raw, by_file


def _manifest_expected_identities(native_root: Path) -> dict[str, dict[str, Any]]:
    """Read the release inventory used to bind canonical export bytes.

    The release ZIP's compact manifest has a historical self-hash mismatch for
    ``backend/exports/manifest.json``.  We intentionally bind the expanded
    checkout manifest to the completion receipt's backend hash instead and do
    not silently treat the compact archive entry as the same file.
    """
    release = read_json(native_root / "release/b039/R011-B039-v2026.09.01.2/07_RELEASE_MANIFEST.json")
    return {str(row["path"]): row for row in release.get("backend_archive_inventory", [])}


def _verify_native_evidence(native_root: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    manifest_path = native_root / EXPORT_MANIFEST
    manifest = read_json(manifest_path)
    if manifest.get("boundary_id") != BOUNDARY_ID or manifest.get("complete_corpus") is not True:
        raise ValueError("B95 export manifest is not the complete R011-B039 corpus")
    if manifest.get("record_count") != len(rows) or manifest.get("record_count") != 21746:
        raise ValueError("B95 export manifest record count drift")
    actual_counts = dict(sorted(Counter(row["record_type"] for row in rows).items()))
    if actual_counts != dict(sorted(EXPECTED_RECORD_COUNTS.items())):
        raise ValueError(f"B95 record counts drift: {actual_counts}")
    release = read_json(native_root / "release/b039/R011-B039-v2026.09.01.2/07_RELEASE_MANIFEST.json")
    if release.get("boundary_id") != BOUNDARY_ID or release.get("complete_corpus") is not True:
        raise ValueError("B95 release manifest is not complete")
    if release.get("backend_record_count") != 21746 or release.get("reader_pages") != 462:
        raise ValueError("B95 release manifest coverage drift")
    authority = release.get("authority", {})
    # The release manifest intentionally records the upstream commit and
    # repository only; its tree identity is retained in the producer's
    # authoritative evidence and in this adapter's source lock.  Do not
    # mistake the observed dirty checkout tree (or the public release tag
    # target) for the upstream tree.
    if authority.get("commit") != UPSTREAM_COMMIT or authority.get("repository") != UPSTREAM_REPOSITORY:
        raise ValueError("B95 upstream authority identity drift")

    # Bind the working export bytes to the exact B039 release inventory.  The
    # inventory has two names for the expanded/compact manifest; the expanded
    # local ``manifest.json`` is intentionally checked against
    # ``FULL_LOCAL_MANIFEST.json`` and never against the compact archive entry.
    expected_inventory = _manifest_expected_identities(native_root)
    # A few evidence-side files (notably ``qa_events.jsonl``) are deliberately
    # not shipped in the compact public backend ZIP.  Their exact identities
    # are nevertheless recorded by the expanded local manifest, so use that
    # manifest as the secondary binding source rather than silently dropping
    # them from the source lock.
    expanded_manifest_files = {
        str(row["path"]): row for row in manifest.get("files", []) if isinstance(row, dict) and row.get("path")
    }
    inventory_bindings: dict[str, dict[str, Any]] = {}
    for relative, _ in CANONICAL_RECORD_FILES:
        expected = expected_inventory.get(relative)
        binding_source = "release_backend_archive_inventory"
        if expected is None and relative.startswith("backend/exports/"):
            expected = expanded_manifest_files.get(relative[len("backend/exports/") :])
            binding_source = "expanded_full_manifest"
        if expected is None:
            raise ValueError(f"B95 release/full manifest omits canonical file: {relative}")
        actual = identity(native_root / relative, display_path=relative)
        if {key: actual[key] for key in ("bytes", "sha256")} != {
            key: expected[key] for key in ("bytes", "sha256")
        }:
            raise ValueError(f"B95 canonical export hash drift: {relative}")
        inventory_bindings[relative] = {
            "bytes": actual["bytes"],
            "sha256": actual["sha256"],
            "release_path": expected["path"],
            "binding_source": binding_source,
        }
    manifest_expected = expected_inventory.get("backend/exports/FULL_LOCAL_MANIFEST.json")
    if manifest_expected is None:
        raise ValueError("B95 release inventory omits expanded full manifest")
    manifest_actual = identity(manifest_path, display_path=EXPORT_MANIFEST)
    if {key: manifest_actual[key] for key in ("bytes", "sha256")} != {
        key: manifest_expected[key] for key in ("bytes", "sha256")
    }:
        raise ValueError("B95 expanded manifest hash drift")
    exercise_expected = expected_inventory.get(EXERCISE_CSV)
    if exercise_expected is None:
        raise ValueError("B95 release inventory omits exercise view")
    exercise_actual = identity(native_root / EXERCISE_CSV, display_path=EXERCISE_CSV)
    if {key: exercise_actual[key] for key in ("bytes", "sha256")} != {
        key: exercise_expected[key] for key in ("bytes", "sha256")
    }:
        raise ValueError("B95 exercise view hash drift")

    completion = read_json(native_root / "qa/b039-publication/R011-B039_FINAL_COMPLETION_RECEIPT.json")
    if completion.get("status") != "COMPLETE_TRANSLATED_ADMITTED_PUBLISHED_AND_PUBLICLY_READ_BACK":
        raise ValueError("B95 completion receipt is not a public completion receipt")
    if completion.get("complete_corpus") is not True:
        raise ValueError("B95 completion receipt does not assert complete corpus")
    if completion.get("backend", {}).get("record_count") != 21746:
        raise ValueError("B95 completion backend count drift")
    if completion.get("reader", {}).get("pages") != 462 or completion.get("reader", {}).get("sha256") != "7ef1ed4390cd846cc636345d34a1ba3765f8afc32eb9446fd60c7862b7fde049":
        raise ValueError("B95 reader binding drift")
    publication = completion.get("publication", {})
    if publication.get("github", {}).get("public") is not True or publication.get("zenodo", {}).get("public") is not True:
        raise ValueError("B95 publication is not publicly verified")

    github = read_json(native_root / "qa/b039-publication/GITHUB_PUBLICATION_RECEIPT_R011-B039-v2026.09.01.2.json")
    zenodo = read_json(native_root / "qa/b039-publication/ZENODO_PUBLICATION_RECEIPT_R011-B039-v2026.09.01.2.json")
    if github.get("status") != "PUBLIC_AND_ANONYMOUSLY_VERIFIED" or not github.get("anonymous_public_byte_readback"):
        raise ValueError("B95 GitHub public readback is not passing")
    if zenodo.get("status") != "PUBLIC_AND_ANONYMOUSLY_VERIFIED" or not zenodo.get("anonymous_public_byte_readback"):
        raise ValueError("B95 Zenodo public readback is not passing")
    if zenodo.get("access_right") != "open" or zenodo.get("record_id") != ZENODO_RECORD_ID:
        raise ValueError("B95 Zenodo access/record drift")

    candidate = read_json(native_root / "backend/staging/b039/candidate-f6e61e290acc9844/CANDIDATE_MANIFEST.json")
    replay = read_json(native_root / "backend/staging/b039/candidate-f6e61e290acc9844/B039_BACKEND_REPLAY.json")
    if candidate.get("complete_corpus") is not True or candidate.get("logical_record_count") != 21746:
        raise ValueError("B95 candidate manifest drift")
    if replay.get("status") != "PASS_SINGLE_BOUNDED_DETERMINISTIC_COMPILATION" or replay.get("logical_record_count") != 21746:
        raise ValueError("B95 replay receipt drift")
    return {
        "manifest": manifest,
        "release": release,
        "completion": completion,
        "github": github,
        "zenodo": zenodo,
        "candidate": candidate,
        "replay": replay,
        "release_inventory": expected_inventory,
        "inventory_bindings": inventory_bindings,
        "exercise_identity": exercise_actual,
    }


def _parse_exercise_csv(native_root: Path, unit_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    path = native_root / EXERCISE_CSV
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        expected_header = [
            "exercise_id",
            "source_local_ids",
            "answer_availability",
            "answer_id",
            "o001_gap_id",
            "source_path",
            "translation_state",
            "rights_component_ids",
        ]
        if reader.fieldnames != expected_header:
            raise ValueError(f"B95 exercise CSV header drift: {reader.fieldnames}")
        for row in reader:
            exercise_id = row.get("exercise_id", "")
            if exercise_id not in unit_by_id:
                raise ValueError(f"B95 exercise CSV references unknown unit: {exercise_id}")
            if unit_by_id[exercise_id].get("unit_type") not in {"exercise", "guided_exercise"}:
                raise ValueError(f"B95 exercise CSV references non-exercise unit: {exercise_id}")
            for field in ("source_local_ids", "rights_component_ids"):
                try:
                    row[field] = json.loads(row.get(field) or "[]")
                except json.JSONDecodeError as exc:
                    raise ValueError(f"B95 exercise CSV invalid JSON in {field}") from exc
            row["answer_id"] = row.get("answer_id") or None
            row["o001_gap_id"] = row.get("o001_gap_id") or None
            rows.append(row)
    if len(rows) != 448 or len({row["exercise_id"] for row in rows}) != 448:
        raise ValueError("B95 exercise identity count/uniqueness drift")
    answer_count = sum(bool(row["answer_id"]) for row in rows)
    gap_count = sum(bool(row["o001_gap_id"]) for row in rows)
    both_count = sum(bool(row["answer_id"] and row["o001_gap_id"]) for row in rows)
    if (answer_count, gap_count, both_count) != (153, 105, 0):
        raise ValueError(f"B95 answer/gap counts drift: {(answer_count, gap_count, both_count)}")
    return rows


def _ancestor_chapter(unit: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    seen: set[str] = set()
    current: dict[str, Any] | None = unit
    while current and current.get("id") not in seen:
        seen.add(str(current.get("id")))
        if current.get("unit_type") == "chapter":
            return current
        parent = current.get("parent_id")
        current = by_id.get(parent) if parent else None
    return None


def _chapter_number(chapter: dict[str, Any]) -> int:
    order = chapter.get("order")
    if isinstance(order, int) and 4 <= order <= 12:
        return order - 3
    raise ValueError(f"B95 chapter order is not in the nine-chapter spine: {order!r}")


def _reader_route(page: int) -> str:
    return f"{READER_ZENODO_URL}#page={page}"


def _safe_span(value: Any) -> Any:
    if not isinstance(value, dict):
        return None
    return {
        key: value[key]
        for key in ("byte_start", "byte_end_exclusive", "line_start", "line_end")
        if key in value
    }


def _safe_record(row: dict[str, Any], source_file: str) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key in SAFE_COMMON_KEYS:
        if key not in row or key.casefold() in FORBIDDEN_CONTENT_KEYS:
            continue
        value = row[key]
        if key in {"source_span", "target_span"}:
            value = _safe_span(value)
        if value is not None:
            output[key] = value
    output["source_export_file"] = source_file
    output["native_record_sha256"] = _record_hash(row)
    return output


def _unit_projection(
    units: list[dict[str, Any]], exercise_rows: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    by_id = {row["id"]: row for row in units}
    chapters = sorted((row for row in units if row.get("unit_type") == "chapter"), key=lambda row: row.get("order", 0))
    if len(chapters) != 9:
        raise ValueError("B95 chapter count drift")
    # Resolve each ancestor once.  Besides being clearer, this keeps the
    # projection bounded when the native ledger grows: the earlier prototype
    # repeated the parent walk for every chapter/unit pair.
    chapter_number_by_id = {chapter["id"]: _chapter_number(chapter) for chapter in chapters}
    chapter_for_id: dict[str, int] = {}
    for unit in units:
        ancestor = _ancestor_chapter(unit, by_id)
        if ancestor is not None:
            chapter_for_id[unit["id"]] = chapter_number_by_id[ancestor["id"]]
    exercise_by_id = {row["exercise_id"]: row for row in exercise_rows}
    projected: list[dict[str, Any]] = []
    learner_hidden = {
        "answer",
        "answer_layout",
        "answer_section",
        "companion_gap",
        "guided_solution",
        "inline_public_answer",
        "mastery_companion_gap",
        "public_answer",
        "solution",
    }
    for unit in units:
        chapter = chapter_for_id.get(unit["id"])
        page = CHAPTER_PAGE_STARTS.get(chapter or 1, 1)
        kind = str(unit.get("unit_type"))
        row = _safe_record(unit, "backend/exports/core/units.jsonl")
        row.update(
            {
                "chapter": chapter,
                "public_route": _reader_route(page),
                "route_precision": "containing_chapter_start" if chapter else "reader_document_start",
                "learner_visible": kind not in learner_hidden,
                "body_content_embedded": False,
            }
        )
        if unit["id"] in exercise_by_id:
            exercise = exercise_by_id[unit["id"]]
            row["answer_id"] = exercise.get("answer_id")
            row["o001_gap_id"] = exercise.get("o001_gap_id")
            row["answer_availability"] = exercise.get("answer_availability")
        projected.append(row)

    chapter_views: list[dict[str, Any]] = []
    for chapter in chapters:
        number = _chapter_number(chapter)
        page = CHAPTER_PAGE_STARTS[number]
        chapter_id = chapter["id"]
        descendants = [row for row in projected if row.get("chapter") == number]
        sections = [
            row
            for row in descendants
            if row.get("unit_type") in {"section", "section_intro", "subsection", "semantic_subunit", "chapter_intro", "chapter_front"}
        ]
        sections.sort(key=lambda row: (row.get("order") if row.get("order") is not None else 10**9, row["id"]))
        exercises = [row for row in descendants if row.get("id") in exercise_by_id]
        exercises.sort(key=lambda row: (row.get("order") if row.get("order") is not None else 10**9, row["id"]))
        chapter_views.append(
            {
                "chapter": number,
                "id": chapter_id,
                "title_en": chapter.get("title"),
                "title_id": CHAPTER_TITLES_ID[number],
                "start_page": page,
                "public_route": _reader_route(page),
                "section_count": len([row for row in sections if row.get("unit_type") == "section"]),
                "section_unit_ids": [row["id"] for row in sections],
                "exercise_count": len(exercises),
                "exercise_ids": [row["id"] for row in exercises],
                "public_answer_count": sum(bool(exercise_by_id[row["id"]].get("answer_id")) for row in exercises),
                "o001_gap_count": sum(bool(exercise_by_id[row["id"]].get("o001_gap_id")) for row in exercises),
                "route_precision": "exact_chapter_start_from_released_reader_toc",
            }
        )
    return projected, chapter_views, chapter_for_id


def _exercise_index(exercise_rows: list[dict[str, Any]], unit_index: list[dict[str, Any]]) -> list[dict[str, Any]]:
    units = {row["id"]: row for row in unit_index}
    output = []
    for row in exercise_rows:
        unit = units[row["exercise_id"]]
        output.append(
            {
                "exercise_id": row["exercise_id"],
                "unit_type": unit.get("unit_type"),
                "chapter": unit.get("chapter"),
                "title": unit.get("title"),
                "source_local_ids": row["source_local_ids"],
                "answer_availability": row.get("answer_availability"),
                "answer_id": row.get("answer_id"),
                "o001_gap_id": row.get("o001_gap_id"),
                "source_path": row.get("source_path"),
                "translation_state": row.get("translation_state"),
                "rights_component_ids": row.get("rights_component_ids", []),
                "public_route": unit.get("public_route"),
                "route_precision": unit.get("route_precision"),
                "answer_or_solution_body_embedded": False,
            }
        )
    return sorted(output, key=lambda row: (row.get("chapter") or 0, row["exercise_id"]))


def _concept_index(rows: list[dict[str, Any]], source_file: str) -> list[dict[str, Any]]:
    return [_safe_record(row, source_file) for row in rows if row.get("record_type") == "concept"]


def _relation_index(rows: list[dict[str, Any]], source_file: str) -> list[dict[str, Any]]:
    return [_safe_record(row, source_file) for row in rows if row.get("record_type") == "relation"]


def _term_index(rows: list[dict[str, Any]], source_file: str) -> list[dict[str, Any]]:
    return [_safe_record(row, source_file) for row in rows if row.get("record_type") == "term"]


def _correction_index(rows: list[dict[str, Any]], source_file: str) -> list[dict[str, Any]]:
    return [_safe_record(row, source_file) for row in rows if row.get("record_type") == "correction"]


def _rights_index(rows: list[dict[str, Any]], source_file: str) -> list[dict[str, Any]]:
    return [_safe_record(row, source_file) for row in rows if row.get("record_type") == "rights"]


def _segment_index(rows: list[dict[str, Any]], source_file: str) -> list[dict[str, Any]]:
    return [_safe_record(row, source_file) for row in rows if row.get("record_type") == "segment"]


def _localization_index(rows: list[dict[str, Any]], source_file: str) -> list[dict[str, Any]]:
    return [_safe_record(row, source_file) for row in rows if row.get("record_type") == "localization"]


def _evidence_index(rows: list[dict[str, Any]], source_file: str) -> list[dict[str, Any]]:
    return [_safe_record(row, source_file) for row in rows if row.get("record_type") in {"artifact", "qa_event"}]


def _public_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    completion = evidence["completion"]
    github = evidence["github"]
    zenodo = evidence["zenodo"]
    release = evidence["release"]
    github_assets = github.get("ordered_assets", [])
    zenodo_assets = zenodo.get("ordered_files", [])
    if len(github_assets) != 9 or len(zenodo_assets) != 9:
        raise ValueError("B95 public release asset count drift")
    assets = []
    for github_asset, zenodo_asset in zip(github_assets, zenodo_assets):
        if github_asset.get("filename") != zenodo_asset.get("filename"):
            raise ValueError("B95 GitHub/Zenodo asset order drift")
        if github_asset.get("bytes") != zenodo_asset.get("bytes") or github_asset.get("sha256") != zenodo_asset.get("sha256"):
            raise ValueError("B95 GitHub/Zenodo asset byte/hash drift")
        filename = github_asset["filename"]
        assets.append(
            {
                "filename": filename,
                "bytes": github_asset["bytes"],
                "sha256": github_asset["sha256"],
                "github_url": f"{GITHUB_DOWNLOAD_BASE}/{filename}",
                "zenodo_url": f"{ZENODO_RECORD}/files/{filename}?download=1",
                "github_bytes": github_asset["bytes"],
                "zenodo_bytes": zenodo_asset["bytes"],
                "github_sha256": github_asset["sha256"],
                "zenodo_sha256": zenodo_asset["sha256"],
                "github_readback": True,
                "zenodo_readback": True,
            }
        )
    return {
        "schema": "b95-public-evidence/1",
        "course_id": COURSE_ID,
        "boundary_id": BOUNDARY_ID,
        "repository": {
            "url": REPOSITORY,
            "release_url": RELEASE_URL,
            "tag": RELEASE_TAG,
            "public": True,
            "tag_target_sha": github.get("tag_target_sha"),
        },
        "upstream": {
            "repository": UPSTREAM_REPOSITORY,
            "commit": UPSTREAM_COMMIT,
            "tree": UPSTREAM_TREE,
        },
        "release": {
            "release_id": RELEASE_ID,
            "asset_count": len(assets),
            "aggregate_payload_bytes": release.get("aggregate_payload_bytes_before_manifest_and_checksums"),
            "assets": assets,
            "public": True,
        },
        "zenodo": {
            "record_id": ZENODO_RECORD_ID,
            "concept_id": ZENODO_CONCEPT_ID,
            "doi": "10.5281/zenodo.22261912",
            "concept_doi": "10.5281/zenodo.22059801",
            "url": ZENODO_RECORD,
            "access_right": "open",
            "public": True,
        },
        "reader": {
            "observed_kind": "page_based_pdf",
            "pdf_filename": READER_FILENAME,
            "pdf_pages": 462,
            "pdf_sha256": "7ef1ed4390cd846cc636345d34a1ba3765f8afc32eb9446fd60c7862b7fde049",
            "github_url": READER_GITHUB_URL,
            "zenodo_url": READER_ZENODO_URL,
            "chapter_toc_page_starts": CHAPTER_PAGE_STARTS,
            "semantic_html_established": False,
            "mathml_established": False,
            "epub_established": False,
            "wcag_conformance_established": False,
            "offline_portability_established": False,
        },
        "backend": {
            "record_count": completion["backend"]["record_count"],
            "manifest_bytes": completion["backend"]["manifest"]["bytes"],
            "manifest_sha256": completion["backend"]["manifest"]["sha256"],
        },
        "anonymous_readback": True,
        "credentials_used": False,
        "github_receipt_status": github.get("status"),
        "zenodo_receipt_status": zenodo.get("status"),
    }


def _claim_boundary() -> dict[str, Any]:
    return {
        "schema": "b95-claim-boundary/1",
        "course_id": COURSE_ID,
        "boundary_id": BOUNDARY_ID,
        "projection_kind": "metadata_only_zero_copy",
        "native_bodies_copied": False,
        "source_segment_text_copied": 0,
        "target_segment_text_copied": 0,
        "answer_or_solution_bodies_copied": 0,
        "restricted_solution_records_exposed": 0,
        "public_answer_identity_rows": 153,
        "o001_gap_identity_rows": 105,
        "semantic_html_claimed": False,
        "mathml_claimed": False,
        "wcag_conformance_claimed": False,
        "epub_claimed": False,
        "offline_portability_claimed": False,
        "reversible_exchange_claimed": False,
        "native_prerequisites_invented": False,
        "public_access_state_changed": False,
        "chapter_routes_are_exact_reader_toc_starts": True,
        "nonchapter_routes_are_context_only": True,
        "explicit_exclusion": [
            "restricted instructor-only solutions",
            "components lacking established redistribution rights",
            "non-rendered upstream developer comments",
        ],
    }


def _source_lock(native_root: Path, evidence: dict[str, Any]) -> dict[str, Any]:
    inputs: list[dict[str, Any]] = []
    for relative, _ in CANONICAL_RECORD_FILES:
        path = native_root / relative
        inputs.append(identity(path, display_path=relative))
    for relative in (
        EXERCISE_CSV,
        EXPORT_MANIFEST,
        "release/b039/R011-B039-v2026.09.01.2/07_RELEASE_MANIFEST.json",
        "backend/staging/b039/candidate-f6e61e290acc9844/CANDIDATE_MANIFEST.json",
        "backend/staging/b039/candidate-f6e61e290acc9844/B039_BACKEND_REPLAY.json",
        "qa/b039-publication/R011-B039_FINAL_COMPLETION_RECEIPT.json",
        "qa/b039-publication/GITHUB_PUBLICATION_RECEIPT_R011-B039-v2026.09.01.2.json",
        "qa/b039-publication/ZENODO_PUBLICATION_RECEIPT_R011-B039-v2026.09.01.2.json",
        "authority/BUILD_AND_READER_CLOSURE.json",
        "authority/CORPUS_CLOSURE_SUMMARY.json",
        "00_control/CURRENT_CURSOR.json",
        "00_control/CURRENT_STATE.md",
    ):
        path = native_root / relative
        if path.is_file():
            inputs.append(identity(path, display_path=relative))
    return {
        "schema": "b95-capability-source-lock/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "native_edition_id": NATIVE_EDITION_ID,
        "boundary_id": BOUNDARY_ID,
        "repository": REPOSITORY,
        "release": {
            "release_id": RELEASE_ID,
            "tag": RELEASE_TAG,
            "upstream_repository": UPSTREAM_REPOSITORY,
            "upstream_commit": UPSTREAM_COMMIT,
            "upstream_tree": UPSTREAM_TREE,
        },
        "observed_native_checkout": native_checkout_identity(native_root),
        "binding_policy": "canonical export and receipt hashes; producer checkout remains external and untouched",
        "inputs": inputs,
        "public_evidence_summary": {
            "github_public": evidence["github"].get("repository_public") is True,
            "zenodo_public": evidence["zenodo"].get("access_right") == "open",
            "anonymous_readback": True,
            "credentials_used": False,
        },
    }


def derive_projection(native_root: Path) -> dict[str, Any]:
    rows, raw_lines, by_file = _load_rows(native_root)
    evidence = _verify_native_evidence(native_root, rows)
    units = by_file["backend/exports/core/units.jsonl"]
    unit_by_id = {row["id"]: row for row in units}
    exercise_rows = _parse_exercise_csv(native_root, unit_by_id)
    unit_index, chapters, chapter_for_id = _unit_projection(units, exercise_rows)
    concepts = _concept_index(by_file["backend/exports/core/concepts.jsonl"], "backend/exports/core/concepts.jsonl")
    relations = _relation_index(by_file["backend/exports/core/relations.jsonl"], "backend/exports/core/relations.jsonl")
    terms = _term_index(by_file["backend/exports/locales/id-ID/terms.jsonl"], "backend/exports/locales/id-ID/terms.jsonl")
    corrections = _correction_index(by_file["backend/exports/core/corrections.jsonl"], "backend/exports/core/corrections.jsonl")
    rights = _rights_index(by_file["backend/exports/core/rights.jsonl"], "backend/exports/core/rights.jsonl")
    segments = _segment_index(by_file["backend/exports/core/segments.jsonl"], "backend/exports/core/segments.jsonl")
    localizations = _localization_index(by_file["backend/exports/locales/id-ID/localizations.jsonl"], "backend/exports/locales/id-ID/localizations.jsonl")
    evidence_index = _evidence_index(
        by_file["backend/exports/evidence/artifacts.jsonl"] + by_file["backend/exports/evidence/qa_events.jsonl"],
        "backend/exports/evidence/artifacts.jsonl + backend/exports/evidence/qa_events.jsonl",
    )
    exercise_index = _exercise_index(exercise_rows, unit_index)
    source_by_id = {
        row["id"]: relative
        for relative, _ in CANONICAL_RECORD_FILES
        for row in by_file[relative]
    }
    native_record_index = [_safe_record(row, source_by_id[row["id"]]) for row in rows]

    counts = dict(sorted(Counter(row["record_type"] for row in rows).items()))
    unit_kinds = dict(sorted(Counter(row.get("unit_type") for row in units).items()))
    correction_statuses = dict(sorted(Counter(row.get("status") for row in by_file["backend/exports/core/corrections.jsonl"]).items()))
    term_states = dict(sorted(Counter(row.get("translation_state") for row in by_file["backend/exports/locales/id-ID/terms.jsonl"]).items()))
    answer_count = sum(bool(row.get("answer_id")) for row in exercise_rows)
    gap_count = sum(bool(row.get("o001_gap_id")) for row in exercise_rows)
    learner_map = {
        "schema": "b95-learner-map/1",
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "native_edition_id": NATIVE_EDITION_ID,
        "locale": LOCALE,
        "reader": {
            "kind": "page_based_pdf",
            "home": RELEASE_URL,
            "pdf": READER_ZENODO_URL,
            "github_pdf": READER_GITHUB_URL,
            "pages": 462,
            "download": True,
            "page_navigation": True,
            "semantic_html": False,
            "mathml": False,
        },
        "chapters": chapters,
        "exercise_identity_count": len(exercise_index),
        "public_answer_identity_count": answer_count,
        "o001_gap_identity_count": gap_count,
        "answers_or_solutions_available_as_bodies": False,
        "body_content_embedded": False,
    }
    educator_map = {
        "schema": "b95-educator-map/1",
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "selectable_units": unit_index,
        "chapter_summaries": [
            {
                "chapter": row["chapter"],
                "id": row["id"],
                "title_id": row["title_id"],
                "public_route": row["public_route"],
                "section_count": row["section_count"],
                "exercise_count": row["exercise_count"],
            }
            for row in chapters
        ],
        "governance": {
            "concept_index": "../data/concept-index.jsonl",
            "term_index": "../data/terms-index.jsonl",
            "correction_index": "../data/corrections-index.jsonl",
            "rights_index": "../data/rights-index.jsonl",
            "relation_index": "../data/relation-index.jsonl",
            "segment_index": "../data/segment-index.jsonl",
            "localization_index": "../data/localization-index.jsonl",
        },
        "correction_status_counts": correction_statuses,
        "term_translation_state_counts": term_states,
        "teacher_manual_claimed": False,
        "answer_key_claimed": False,
        "body_content_embedded": False,
    }
    public_evidence = _public_evidence(evidence)
    claim_boundary = _claim_boundary()
    capabilities = {
        "schema": "b95-capabilities/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "native_edition_id": NATIVE_EDITION_ID,
        "locale": LOCALE,
        "native_family": "openintro_statistics_fourth_edition",
        "counts": {
            "native_records": len(rows),
            "native_record_types": counts,
            "units": len(unit_index),
            "unit_kinds": unit_kinds,
            "chapters": len(chapters),
            "sections": sum(1 for row in units if row.get("unit_type") == "section"),
            "subsections": sum(1 for row in units if row.get("unit_type") == "subsection"),
            "exercises": len(exercise_index),
            "exercise_units": sum(1 for row in units if row.get("unit_type") == "exercise"),
            "guided_exercises": sum(1 for row in units if row.get("unit_type") == "guided_exercise"),
            "public_answer_ids": answer_count,
            "o001_gap_ids": gap_count,
            "concepts": len(concepts),
            "relations": len(relations),
            "terms": len(terms),
            "corrections": len(corrections),
            "component_rights": len(rights),
            "segments": len(segments),
            "localizations": len(localizations),
            "evidence_records": len(evidence_index),
            "source_files": 1245,
            "reader_pages": 462,
        },
        "curriculum_graph": {
            "course_id": COURSE_ID,
            "native_prerequisite_course_ids": [],
            "prerequisite_assertion": "not_asserted_by_upstream_text",
            "chapter_and_unit_hierarchy": True,
        },
        "learner_delivery": {
            "chapter_navigation": True,
            "exercise_identity_navigation": True,
            "public_answer_identity_navigation": True,
            "answers_or_solutions": False,
            "page_based_pdf_reader": True,
            "semantic_html": False,
        },
        "educator_delivery": {
            "unit_selector": True,
            "concept_index": True,
            "terminology_index": True,
            "correction_status_index": True,
            "component_rights_index": True,
            "translation_alignment_index": True,
            "teacher_manual": False,
        },
        "federation": {
            "stable_native_ids_preserved": True,
            "body_content_embedded": False,
            "component_rights_preserved": True,
            "external_native_backend_required_for_replay": True,
        },
        "native_id_sequence_sha256": sha256_bytes(("\n".join(row["id"] for row in rows) + "\n").encode("utf-8")),
        "native_record_sequence_sha256": sha256_bytes(b"\n".join(raw_lines) + b"\n"),
    }
    source_lock = _source_lock(native_root, evidence)
    return {
        "source_lock": source_lock,
        "native_record_index": native_record_index,
        "unit_index": unit_index,
        "exercise_index": exercise_index,
        "concept_index": concepts,
        "relation_index": relations,
        "terms_index": terms,
        "corrections_index": corrections,
        "rights_index": rights,
        "segment_index": segments,
        "localization_index": localizations,
        "evidence_index": evidence_index,
        "learner_map": learner_map,
        "educator_map": educator_map,
        "public_evidence": public_evidence,
        "capabilities": capabilities,
        "claim_boundary": claim_boundary,
        "evidence": evidence,
        "exercise_rows": exercise_rows,
        "chapter_for_id": chapter_for_id,
    }


def forbidden_content_paths(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if isinstance(key, str) and key.casefold() in FORBIDDEN_CONTENT_KEYS:
                errors.append(child_path)
            errors.extend(forbidden_content_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(forbidden_content_paths(child, f"{path}[{index}]"))
    return errors


def projection_errors(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    capabilities = bundle.get("capabilities", {})
    counts = capabilities.get("counts", {})
    native_index = bundle.get("native_record_index", [])
    units = bundle.get("unit_index", [])
    exercises = bundle.get("exercise_index", [])
    claim = bundle.get("claim_boundary", {})
    public = bundle.get("public_evidence", {})
    if len(native_index) != 21746 or len({row.get("id") for row in native_index}) != 21746:
        errors.append("B95-NATIVE-ID-COUNT")
    if native_index:
        observed_id_sequence = sha256_bytes(
            ("\n".join(str(row.get("id")) for row in native_index) + "\n").encode("utf-8")
        )
        if observed_id_sequence != capabilities.get("native_id_sequence_sha256"):
            errors.append("B95-NATIVE-ID-SEQUENCE")
    if counts.get("native_record_types") != dict(sorted(EXPECTED_RECORD_COUNTS.items())):
        errors.append("B95-RECORD-TYPE-COUNTS")
    if counts.get("unit_kinds") != dict(sorted(EXPECTED_UNIT_KINDS.items())) or len(units) != 1089:
        errors.append("B95-UNIT-KINDS")
    if len(exercises) != 448 or sum(bool(row.get("answer_id")) for row in exercises) != 153 or sum(bool(row.get("o001_gap_id")) for row in exercises) != 105:
        errors.append("B95-EXERCISE-ANSWER-GAP-COUNTS")
    if len(bundle.get("concept_index", [])) != 826:
        errors.append("B95-CONCEPT-COUNT")
    if len(bundle.get("relation_index", [])) != 11127:
        errors.append("B95-RELATION-COUNT")
    if len(bundle.get("terms_index", [])) != 859:
        errors.append("B95-TERM-COUNT")
    if len(bundle.get("corrections_index", [])) != 302:
        errors.append("B95-CORRECTION-COUNT")
    if len(bundle.get("rights_index", [])) != 80:
        errors.append("B95-RIGHTS-COUNT")
    if len({row.get("id") for row in bundle.get("rights_index", [])}) != 80:
        errors.append("B95-RIGHTS-FLAT-TABLE")
    if len(bundle.get("segment_index", [])) != 2231 or len(bundle.get("localization_index", [])) != 2231:
        errors.append("B95-TRANSLATION-INDEX-COUNT")
    # ``evidence`` and ``exercise_rows`` are internal source-side receipts used
    # while deriving the packet; they are intentionally not emitted.  Scan the
    # actual projected surfaces, not those raw inputs, for body-bearing keys.
    projected_surfaces = {
        key: value
        for key, value in bundle.items()
        if key not in {"evidence", "exercise_rows", "chapter_for_id"}
    }
    if forbidden_content_paths(projected_surfaces):
        errors.append("B95-COPIED-NATIVE-BODY")
    for key in (
        "native_bodies_copied",
        "semantic_html_claimed",
        "mathml_claimed",
        "wcag_conformance_claimed",
        "epub_claimed",
        "offline_portability_claimed",
        "reversible_exchange_claimed",
        "native_prerequisites_invented",
        "public_access_state_changed",
    ):
        if claim.get(key) is not False:
            errors.append(f"B95-CLAIM:{key}")
    for key in ("source_segment_text_copied", "target_segment_text_copied", "answer_or_solution_bodies_copied", "restricted_solution_records_exposed"):
        if claim.get(key) != 0:
            errors.append(f"B95-BOUNDARY:{key}")
    if public.get("anonymous_readback") is not True or public.get("credentials_used") is not False:
        errors.append("B95-PUBLIC-EVIDENCE")
    if public.get("repository", {}).get("public") is not True or public.get("release", {}).get("public") is not True or public.get("zenodo", {}).get("access_right") != "open":
        errors.append("B95-PUBLIC-ACCESS")
    if public.get("reader", {}).get("pdf_pages") != 462 or public.get("reader", {}).get("semantic_html_established"):
        errors.append("B95-READER-CLAIMS")
    expected_routes = [f"{READER_ZENODO_URL}#page={CHAPTER_PAGE_STARTS[number]}" for number in range(1, 10)]
    actual_routes = [row.get("public_route") for row in bundle.get("learner_map", {}).get("chapters", [])]
    if actual_routes != expected_routes:
        errors.append("B95-CHAPTER-ROUTES")
    if bundle.get("learner_map", {}).get("exercise_identity_count") != 448:
        errors.append("B95-LEARNER-EXERCISE-COUNT")
    if len(bundle.get("educator_map", {}).get("selectable_units", [])) != 1089:
        errors.append("B95-EDUCATOR-UNIT-COUNT")
    return sorted(set(errors))
