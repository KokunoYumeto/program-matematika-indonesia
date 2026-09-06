"""Model and invariant helpers for the B90 zero-copy capability adapter."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_NATIVE = PROJECT.parent / "introduction-to-probability-id-b90-current"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/b90-capability-v1"
PUBLIC_RECEIPT_PATH = DEFAULT_ADAPTER / "input/public-native-readback.json"

COURSE_ID = "B90"
NATIVE_ROLE_ID = "R010"
NATIVE_COURSE_ID = "urn:interlanguage:r010:course:b90"
PREREQUISITE_ID = "urn:interlanguage:r010:course:b30"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"
RELEASE_COMMIT = "5d1cfc55eecb678b0b4074160bc4f2d8bb2da5b6"
RELEASE_TREE = "21df3b2c0fab6827a21854bdcc41667a93edf749"
RELEASE_TAG = "v2026.08.22.1"
REPOSITORY = "https://github.com/KokunoYumeto/introduction-to-probability-id"
PAGES_URL = "https://kokunoyumeto.github.io/introduction-to-probability-id/"
ZENODO_RECORD_ID = 22062144
ZENODO_CONCEPT_ID = 22048654
ZENODO_RECORD = f"https://zenodo.org/records/{ZENODO_RECORD_ID}"

NATIVE_JSONL = "backend/public/public-safe-main.records.jsonl"
NATIVE_CSV = "backend/public/public-safe-main.records.csv"
NATIVE_SCHEMA = "backend/public/record.schema.json"
NATIVE_VALIDATION = "backend/public/PUBLIC_SAFE_EXPORT_VALIDATION.json"

EXPECTED_RECORD_COUNTS = {
    "artifact": 82,
    "asset": 120,
    "concept": 91,
    "correction": 152,
    "course": 2,
    "edition": 2,
    "program": 1,
    "qa_event": 74,
    "relation": 1694,
    "resource": 1,
    "rights": 4,
    "segment": 1574,
    "term": 119,
    "unit": 800,
}

EXPECTED_UNIT_COUNTS = {
    "backmatter": 1,
    "book-shell": 1,
    "chapter": 12,
    "exercise": 711,
    "exercise-set": 33,
    "frontmatter": 1,
    "modified_edition_history": 1,
    "preface": 1,
    "publication_notice": 1,
    "section": 33,
    "section-fragment": 5,
}

EXPECTED_RELATION_COUNTS = {
    "contains": 787,
    "has_target_expression": 2,
    "translates": 786,
    "uses_asset": 119,
}

EXPECTED_CORRECTION_STATUS_COUNTS = {
    "corrected_in_translation": 4,
    "open": 144,
    "partially_corrected_in_translation": 1,
    "partly_corrected_in_translation": 1,
    "resolved": 2,
}

EXPECTED_TERM_STATUS_COUNTS = {"admitted": 117, "superseded": 2}

CHAPTERS = (
    (1, 21, "Distribusi Peluang Diskret"),
    (2, 61, "Densitas Peluang Kontinu"),
    (3, 97, "Kombinatorika"),
    (4, 159, "Peluang Bersyarat"),
    (5, 213, "Distribusi dan Densitas Penting"),
    (6, 257, "Nilai Harapan dan Varians"),
    (7, 321, "Jumlah Peubah Acak yang Saling Bebas"),
    (8, 343, "Hukum Bilangan Besar"),
    (9, 363, "Teorema Limit Pusat"),
    (10, 405, "Fungsi Pembangkit"),
    (11, 445, "Rantai Markov"),
    (12, 515, "Jalan Acak"),
)

FRONTMATTER_PAGES = {
    "book-shell": 1,
    "frontmatter": 3,
    "modified_edition_history": 5,
    "publication_notice": 3,
    "preface": 9,
    "backmatter": 547,
}

EXPECTED_PUBLIC_IDENTITIES = {
    "CENTRAL_HUB_HANDOFF.json": {
        "bytes": 3_509,
        "sha256": "7afa66c596fb5df750512e932e1707e27ab764784c23bf81678f38dd5752ea73",
    },
    NATIVE_JSONL: {
        "bytes": 7_455_392,
        "sha256": "4981da0220b3063765d5ad9df054a6a9d37d89b7f72abb9a230900f293140952",
    },
    NATIVE_CSV: {
        "bytes": 6_309_596,
        "sha256": "ab4d670735b36dd9dd5cad38a67e986ec6e06f343751330de12447562f9ba653",
    },
    NATIVE_SCHEMA: {
        "bytes": 2_683,
        "sha256": "6c92b72345ffb5241cfc06f70c34af998fe60a12eabd54a22fad4a0c016afcb6",
    },
    NATIVE_VALIDATION: {
        "bytes": 6_952,
        "sha256": "92ad72b3b092d5d2aa687301acb89b496afc606a5ddcfa9d4ba4defa172c201c",
    },
    "index.html": {
        "bytes": 10_664,
        "sha256": "1f07fc866cdeb52653984d9237d3ce7fc67473061d63861fdebfaf66bec1faed",
    },
    "assets/reader.css": {
        "bytes": 12_575,
        "sha256": "d74e04ac22563099aa8c0c3bf298855123429e043a2cf4d42f5b03601afaaf9a",
    },
    "assets/reader.js": {
        "bytes": 12_850,
        "sha256": "ed5faceeb94f87f9eec7a93a51aacee2a80774c07a0e656be72b6ee637e3e15e",
    },
    "release/PENGANTAR_PELUANG_GRINSTEAD_SNELL_ID.pdf": {
        "bytes": 3_403_487,
        "sha256": "f4921540bb47b09bb938bb18a5a6f78fd5340835fb834fe865f1eb0930b8b2b8",
    },
}

EXPECTED_EXCLUSION = {
    "full_record_count": 5875,
    "excluded_record_count": 1159,
    "excluded_record_type_counts": {
        "artifact": 6,
        "edition": 2,
        "exercise_answer": 287,
        "qa_event": 1,
        "relation": 574,
        "resource": 1,
        "rights": 1,
        "segment": 287,
    },
    "excluded_id_list_sha256": "e78ce4f26cde2d0e7572fab575f528853671068c5f25b5cc964e61159db1fe90",
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
    "solution",
    "solution_body",
    "solution_text",
    "target_text",
    "tex_body",
    "text",
}


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
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


def read_canonical_jsonl(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        raise ValueError(f"JSONL is not LF terminated: {path}")
    rows = []
    for number, line in enumerate(data.splitlines(), 1):
        if not line:
            continue
        row = json.loads(line.decode("utf-8"))
        expected = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if line != expected:
            raise ValueError(f"JSONL row {number} is not canonical: {path}")
        rows.append(row)
    return rows


def _git(native_root: Path, *args: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(native_root), *args], stderr=subprocess.STDOUT, timeout=60
    )


def git_text(native_root: Path, *args: str) -> str:
    return _git(native_root, *args).decode("utf-8").strip()


def git_bytes(native_root: Path, path: str) -> bytes:
    return _git(native_root, "show", f"{RELEASE_COMMIT}:{path}")


def native_git_identity(native_root: Path) -> dict[str, str]:
    return {
        "commit": git_text(native_root, "rev-parse", "HEAD"),
        "tree": git_text(native_root, "rev-parse", "HEAD^{tree}"),
    }


def _record_hash(row: dict[str, Any]) -> str:
    data = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(data)


def _load_rows(native_root: Path) -> tuple[list[dict[str, Any]], list[bytes]]:
    data = git_bytes(native_root, NATIVE_JSONL)
    if not data.endswith(b"\n"):
        raise ValueError("B90 native JSONL must be LF terminated")
    raw_lines = [line for line in data.splitlines() if line]
    rows = [json.loads(line.decode("utf-8")) for line in raw_lines]
    return rows, raw_lines


def _group(rows: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["record_type"]].append(row)
    return dict(grouped)


def _native_record_index(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = (
        "id",
        "record_type",
        "status",
        "translation_state",
        "language",
        "locale",
        "edition_id",
        "resource_id",
        "rights_id",
        "parent_id",
        "order",
        "path",
        "source_local_id",
        "source_locator",
        "content_sha256",
        "artifact_ids",
        "concept_ids",
        "prerequisite_ids",
        "qa_event_ids",
        "supersedes_id",
    )
    return [
        {
            **{key: row[key] for key in keys if key in row and row[key] is not None},
            "native_record_sha256": _record_hash(row),
        }
        for row in rows
    ]


def _record_url(row_id: str) -> str:
    return f"{REPOSITORY}/blob/{RELEASE_COMMIT}/{NATIVE_JSONL}?plain=1"


def _reader_route(page: int) -> str:
    return f"{PAGES_URL}?page={page}"


def _unit_projection(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    units = [row for row in rows if row["record_type"] == "unit"]
    by_id = {row["id"]: row for row in units}
    chapter_meta = {number: {"page": page, "title_id": title} for number, page, title in CHAPTERS}

    def chapter_number(row: dict[str, Any]) -> int | None:
        current = row
        seen: set[str] = set()
        while current and current["id"] not in seen:
            seen.add(current["id"])
            if current.get("data", {}).get("kind") == "chapter":
                return int(current["data"]["chapter"])
            current = by_id.get(current.get("parent_id"))
        return None

    projected = []
    for row in units:
        kind = row["data"]["kind"]
        chapter = chapter_number(row)
        page = chapter_meta[chapter]["page"] if chapter else FRONTMATTER_PAGES.get(kind, 1)
        projected.append(
            {
                "id": row["id"],
                "kind": kind,
                "parent_id": row.get("parent_id"),
                "order": row.get("order"),
                "number": row.get("data", {}).get("number"),
                "section": row.get("data", {}).get("section"),
                "chapter": chapter,
                "status": row.get("status"),
                "translation_state": row.get("translation_state"),
                "content_sha256": row.get("content_sha256"),
                "native_record_sha256": _record_hash(row),
                "native_record_url": _record_url(row["id"]),
                "public_route": _reader_route(page),
                "route_precision": "exact_chapter_start" if kind == "chapter" else (
                    "exact_reader_landmark" if chapter is None else "containing_chapter_context"
                ),
                "body_content_embedded": False,
            }
        )

    chapter_rows = []
    for number, page, title in CHAPTERS:
        chapter_id = f"urn:interlanguage:r010:unit:chapter:{number}"
        sections = sorted(
            [row for row in projected if row["parent_id"] == chapter_id and row["kind"] == "section"],
            key=lambda row: (row.get("order") or 0, row["id"]),
        )
        section_views = []
        for section in sections:
            sets = [row for row in projected if row["parent_id"] == section["id"] and row["kind"] == "exercise-set"]
            exercise_rows = sorted(
                [row for row in projected if row["parent_id"] in {item["id"] for item in sets} and row["kind"] == "exercise"],
                key=lambda row: (row.get("order") or 0, row["id"]),
            )
            exercise_ids = [row["id"] for row in exercise_rows]
            fragments = sorted(
                [row["id"] for row in projected if row["parent_id"] == section["id"] and row["kind"] == "section-fragment"]
            )
            section_views.append(
                {
                    "id": section["id"],
                    "section": section["section"],
                    "public_route": _reader_route(page),
                    "route_precision": "containing_chapter_context",
                    "exercise_set_ids": sorted(item["id"] for item in sets),
                    "exercise_ids": exercise_ids,
                    "section_fragment_ids": fragments,
                }
            )
        chapter_rows.append(
            {
                "chapter": number,
                "id": chapter_id,
                "title_id": title,
                "start_page": page,
                "public_route": _reader_route(page),
                "sections": section_views,
                "exercise_count": sum(len(row["exercise_ids"]) for row in section_views),
            }
        )
    return projected, chapter_rows


def _concept_index(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": row["id"],
            "status": row.get("status"),
            "label_en": row.get("data", {}).get("label_en"),
            "identity_scope": row.get("data", {}).get("identity_scope"),
            "native_record_sha256": _record_hash(row),
            "native_record_url": _record_url(row["id"]),
        }
        for row in rows
        if row["record_type"] == "concept"
    ]


def _relation_index(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": row["id"],
            "relation_type": row["data"]["relation_type"],
            "from_id": row["data"]["from_id"],
            "to_id": row["data"]["to_id"],
            "status": row.get("status"),
            "native_record_sha256": _record_hash(row),
        }
        for row in rows
        if row["record_type"] == "relation"
    ]


def _term_index(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fields = ("english", "preferred_id", "variants", "scope", "status", "term_id", "evidence", "notes", "rejected")
    output = []
    for row in rows:
        if row["record_type"] != "term":
            continue
        data = row.get("data", {})
        output.append(
            {
                "id": row["id"],
                "record_status": row.get("status"),
                "translation_state": row.get("translation_state"),
                **{key: data[key] for key in fields if key in data},
                "native_record_sha256": _record_hash(row),
            }
        )
    return output


def _correction_index(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": row["id"],
            "record_status": row.get("status"),
            "correction_status": row.get("data", {}).get("status"),
            "category": row.get("data", {}).get("category"),
            "severity": row.get("data", {}).get("severity"),
            "date": row.get("data", {}).get("date"),
            "event_id": row.get("data", {}).get("event_id"),
            "native_record_sha256": _record_hash(row),
            "native_record_url": _record_url(row["id"]),
        }
        for row in rows
        if row["record_type"] == "correction"
    ]


def _rights_index(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": row["id"],
            "status": row.get("status"),
            "license_name": row.get("data", {}).get("license_name"),
            "selected_version": row.get("data", {}).get("selected_version"),
            "publication_ready": row.get("data", {}).get("publication_ready"),
            "component_rights_resolved": row.get("data", {}).get("component_rights_resolved"),
            "component_rights_ids": row.get("data", {}).get("component_rights_ids", []),
            "native_record_sha256": _record_hash(row),
            "native_record_url": _record_url(row["id"]),
        }
        for row in rows
        if row["record_type"] == "rights"
    ]


def _source_lock(native_root: Path, receipt_path: Path) -> dict[str, Any]:
    native = native_git_identity(native_root)
    inputs = []
    for source_path in EXPECTED_PUBLIC_IDENTITIES:
        data = git_bytes(native_root, source_path)
        inputs.append(identity_bytes(data, path=f"{REPOSITORY}@{RELEASE_COMMIT}:{source_path}"))
    receipt_data = receipt_path.read_bytes()
    receipt = json.loads(receipt_data.decode("utf-8"))
    if receipt_data != canonical_json_bytes(receipt):
        raise ValueError("B90 public-native readback receipt is not canonical JSON")
    inputs.append(identity_bytes(receipt_data, path="input/public-native-readback.json"))
    return {
        "schema": "b90-capability-source-lock/1",
        "course_id": COURSE_ID,
        "repository": REPOSITORY,
        "release": {"commit": RELEASE_COMMIT, "tree": RELEASE_TREE, "tag": RELEASE_TAG},
        "observed_native_checkout": native,
        "inputs": inputs,
    }


def derive_projection(native_root: Path, receipt_path: Path = PUBLIC_RECEIPT_PATH) -> dict[str, Any]:
    native = native_git_identity(native_root)
    if native != {"commit": RELEASE_COMMIT, "tree": RELEASE_TREE}:
        raise ValueError(f"B90 native checkout identity mismatch: {native}")

    rows, raw_lines = _load_rows(native_root)
    if len(rows) != 4716 or len({row["id"] for row in rows}) != 4716:
        raise ValueError("B90 native record count or uniqueness mismatch")
    counts = dict(sorted(Counter(row["record_type"] for row in rows).items()))
    if counts != EXPECTED_RECORD_COUNTS:
        raise ValueError(f"B90 native record-type counts mismatch: {counts}")
    for number, (row, raw) in enumerate(zip(rows, raw_lines), 1):
        canonical = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if canonical != raw:
            raise ValueError(f"B90 native JSONL row {number} is not canonical")

    native_validation = json.loads(git_bytes(native_root, NATIVE_VALIDATION).decode("utf-8"))
    if native_validation.get("result") != "pass":
        raise ValueError("B90 public-safe native validation is not passing")
    for key, expected in EXPECTED_EXCLUSION.items():
        if native_validation.get(key) != expected:
            raise ValueError(f"B90 public-safe exclusion boundary drift: {key}")

    handoff = json.loads(git_bytes(native_root, "CENTRAL_HUB_HANDOFF.json").decode("utf-8"))
    expected_coverage = {
        "chapters": 12,
        "pages": 554,
        "exercises": 711,
        "backend_records": 4716,
        "figure_assets": 120,
        "figure_assets_used": 118,
        "figure_assets_preserved_unused": 2,
        "unit_asset_relations": 119,
    }
    for key, expected in expected_coverage.items():
        if handoff.get("coverage", {}).get(key) != expected:
            raise ValueError(f"B90 central handoff coverage drift: {key}")
    if handoff.get("publication_state") != "public_release_with_live_html_reader":
        raise ValueError("B90 central handoff publication-state drift")

    receipt = read_json(receipt_path)
    if receipt.get("state") != "pass" or receipt.get("failures") or not receipt.get("anonymous") or receipt.get("credentials_used"):
        raise ValueError("B90 public-native receipt is not a credential-free pass")
    if receipt.get("repository", {}).get("commit") != RELEASE_COMMIT or receipt.get("repository", {}).get("tree") != RELEASE_TREE:
        raise ValueError("B90 public-native receipt revision mismatch")

    native_record_index = _native_record_index(rows)
    unit_index, chapters = _unit_projection(rows)
    concept_index = _concept_index(rows)
    relation_index = _relation_index(rows)
    terms_index = _term_index(rows)
    corrections_index = _correction_index(rows)
    rights_index = _rights_index(rows)

    learner_map = {
        "schema": "b90-learner-map/1",
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "prerequisite": {"course_id": "B30", "native_id": PREREQUISITE_ID},
        "reader": {
            "kind": "page_based_pdfjs",
            "home": PAGES_URL,
            "pdf": f"{PAGES_URL}release/PENGANTAR_PELUANG_GRINSTEAD_SNELL_ID.pdf",
            "index_route": _reader_route(547),
            "search": True,
            "page_navigation": True,
            "zoom": True,
            "rotate": True,
            "download": True,
            "semantic_html": False,
            "pdf_pages": 554,
        },
        "chapters": chapters,
        "exercise_identity_count": 711,
        "answers_or_solutions_available_in_public_backend": False,
        "body_content_embedded": False,
    }

    educator_map = {
        "schema": "b90-educator-map/1",
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "selectable_units": unit_index,
        "chapter_summaries": [
            {
                "chapter": row["chapter"],
                "id": row["id"],
                "title_id": row["title_id"],
                "public_route": row["public_route"],
                "section_count": len(row["sections"]),
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
        },
        "correction_status_counts": dict(sorted(Counter(row["correction_status"] for row in corrections_index).items())),
        "term_status_counts": dict(sorted(Counter(row["record_status"] for row in terms_index).items())),
        "teacher_manual_claimed": False,
        "answer_key_claimed": False,
        "body_content_embedded": False,
    }

    public_evidence = {
        "schema": "b90-public-evidence/1",
        "course_id": COURSE_ID,
        "repository": receipt["repository"],
        "github_release": receipt["github_release"],
        "zenodo": receipt["zenodo"],
        "pages_files": receipt["pages_files"],
        "record_backend": receipt["record_backend"],
        "reader": {
            "observed_kind": "page_based_pdfjs",
            "chapter_query_routes_observed": len(CHAPTERS),
            "semantic_html_established": False,
            "mathml_established": False,
            "wcag_conformance_established": False,
            "epub_established": False,
            "offline_portability_established": False,
            "pdf_pages": 554,
        },
        "anonymous_readback": True,
        "credentials_used": False,
    }

    claim_boundary = {
        "schema": "b90-claim-boundary/1",
        "course_id": COURSE_ID,
        "native_bodies_copied": False,
        "source_segment_text_copied": 0,
        "target_segment_text_copied": 0,
        "excluded_supplement_records_exposed": 0,
        "answers_or_solutions_claimed": False,
        "teacher_manual_claimed": False,
        "semantic_html_claimed": False,
        "mathml_claimed": False,
        "wcag_conformance_claimed": False,
        "epub_claimed": False,
        "offline_portability_claimed": False,
        "reversible_exchange_claimed": False,
        "learner_result_instances": 0,
        "public_access_state_changed": False,
        "chapter_routes_are_exact_starts": True,
        "nonchapter_unit_routes_are_context_only": True,
        "explicit_exclusion": EXPECTED_EXCLUSION,
    }

    capabilities = {
        "schema": "b90-capabilities/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "native_family": "grinstead_snell_probability",
        "counts": {
            "native_records": len(rows),
            "native_record_types": counts,
            "units": len(unit_index),
            "unit_kinds": dict(sorted(Counter(row["kind"] for row in unit_index).items())),
            "chapters": len(chapters),
            "pdf_pages": 554,
            "sections": sum(len(row["sections"]) for row in chapters),
            "exercises": sum(row["exercise_count"] for row in chapters),
            "concepts": len(concept_index),
            "relations": len(relation_index),
            "relation_kinds": dict(sorted(Counter(row["relation_type"] for row in relation_index).items())),
            "terms": len(terms_index),
            "term_statuses": dict(sorted(Counter(row["record_status"] for row in terms_index).items())),
            "corrections": len(corrections_index),
            "correction_statuses": dict(sorted(Counter(row["correction_status"] for row in corrections_index).items())),
            "component_rights": len(rights_index),
            "excluded_supplement_records": EXPECTED_EXCLUSION["excluded_record_count"],
            "excluded_answer_records": EXPECTED_EXCLUSION["excluded_record_type_counts"]["exercise_answer"],
        },
        "curriculum_graph": {
            "course_id": COURSE_ID,
            "prerequisite_course_ids": ["B30"],
            "native_prerequisite_ids": [PREREQUISITE_ID],
            "chapter_and_section_hierarchy": True,
        },
        "learner_delivery": {
            "chapter_navigation": True,
            "exercise_identity_navigation": True,
            "answers_or_solutions": False,
            "page_based_pdf_reader": True,
        },
        "educator_delivery": {
            "unit_selector": True,
            "concept_index": True,
            "terminology_index": True,
            "correction_status_index": True,
            "component_rights_index": True,
            "teacher_manual": False,
        },
        "federation": {
            "stable_native_ids_preserved": True,
            "body_content_embedded": False,
            "external_native_backend_required_for_replay": True,
        },
        "native_id_sequence_sha256": sha256_bytes(("\n".join(row["id"] for row in rows) + "\n").encode("utf-8")),
        "native_record_sequence_sha256": sha256_bytes(b"\n".join(raw_lines) + b"\n"),
    }

    return {
        "source_lock": _source_lock(native_root, receipt_path),
        "native_record_index": native_record_index,
        "unit_index": unit_index,
        "concept_index": concept_index,
        "relation_index": relation_index,
        "terms_index": terms_index,
        "corrections_index": corrections_index,
        "rights_index": rights_index,
        "learner_map": learner_map,
        "educator_map": educator_map,
        "public_evidence": public_evidence,
        "capabilities": capabilities,
        "claim_boundary": claim_boundary,
    }


def forbidden_content_paths(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key.casefold() in FORBIDDEN_CONTENT_KEYS:
                errors.append(child_path)
            errors.extend(forbidden_content_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(forbidden_content_paths(child, f"{path}[{index}]"))
    return errors


def projection_errors(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    counts = bundle.get("capabilities", {}).get("counts", {})
    native_index = bundle.get("native_record_index", [])
    unit_index = bundle.get("unit_index", [])
    rights = bundle.get("rights_index", [])
    claims = bundle.get("claim_boundary", {})
    public = bundle.get("public_evidence", {})
    learner = bundle.get("learner_map", {})

    if len(native_index) != 4716:
        errors.append("B90-NATIVE-ID-COUNT")
    ids = [row.get("id") for row in native_index]
    if len(set(ids)) != len(ids) or sha256_bytes(("\n".join(str(item) for item in ids) + "\n").encode("utf-8")) != bundle.get("capabilities", {}).get("native_id_sequence_sha256"):
        errors.append("B90-NATIVE-ID-SEQUENCE")
    if counts.get("native_record_types") != EXPECTED_RECORD_COUNTS:
        errors.append("B90-RECORD-TYPE-COUNTS")
    if counts.get("unit_kinds") != EXPECTED_UNIT_COUNTS or len(unit_index) != 800:
        errors.append("B90-UNIT-HIERARCHY")
    if counts.get("relation_kinds") != EXPECTED_RELATION_COUNTS:
        errors.append("B90-RELATION-COUNTS")
    if counts.get("correction_statuses") != EXPECTED_CORRECTION_STATUS_COUNTS:
        errors.append("B90-CORRECTION-STATES")
    if counts.get("term_statuses") != EXPECTED_TERM_STATUS_COUNTS:
        errors.append("B90-TERM-STATES")
    if len(rights) != 4 or len({row.get("id") for row in rights}) != 4:
        errors.append("B90-RIGHTS-FLATTENED")
    if forbidden_content_paths(bundle):
        errors.append("B90-COPIED-NATIVE-BODY")
    if claims.get("source_segment_text_copied") != 0 or claims.get("target_segment_text_copied") != 0:
        errors.append("B90-SEGMENT-TEXT-COPIED")
    if claims.get("excluded_supplement_records_exposed") != 0 or claims.get("explicit_exclusion") != EXPECTED_EXCLUSION:
        errors.append("B90-EXCLUDED-SUPPLEMENT-EXPOSED")
    for key in ("answers_or_solutions_claimed", "teacher_manual_claimed"):
        if claims.get(key):
            errors.append(f"B90-FALSE-CLAIM:{key}")
    if claims.get("semantic_html_claimed") or public.get("reader", {}).get("semantic_html_established"):
        errors.append("B90-FALSE-SEMANTIC-HTML")
    if claims.get("wcag_conformance_claimed") or public.get("reader", {}).get("wcag_conformance_established"):
        errors.append("B90-FALSE-WCAG")
    if claims.get("reversible_exchange_claimed"):
        errors.append("B90-FALSE-REVERSIBILITY")
    expected_routes = [_reader_route(page) for _, page, _ in CHAPTERS]
    actual_routes = [row.get("public_route") for row in learner.get("chapters", [])]
    if actual_routes != expected_routes:
        errors.append("B90-CHAPTER-ROUTE")
    if learner.get("prerequisite", {}).get("native_id") != PREREQUISITE_ID:
        errors.append("B90-PREREQUISITE")
    if public.get("anonymous_readback") is not True or public.get("credentials_used") is not False:
        errors.append("B90-PUBLIC-EVIDENCE")
    return sorted(set(errors))
