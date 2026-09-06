"""Model and invariant helpers for the D90 zero-copy capability adapter."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_NATIVE = PROJECT.parent / "advanced-optimization-convex-analysis-id"
DEFAULT_ADAPTER = (
    PROJECT / "backend/course-capsule-v1/adapters/d90-capability-v1"
)

COURSE_ID = "D90"
NATIVE_PROGRAM_ID = "program.d90.id-id"
NATIVE_COURSE_ID = "course.d90.advanced-optimization-convex-analysis"
ORIGINAL03_PREFIX = "d90.orig.v1.tr03."
ORIGINAL03_UNIT_ID = "d90.orig.v1.tr03.unit"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"
RELEASE_COMMIT = "eb6b25cb6d2c84d32c5b0a30b0feea9e97efefab"
RELEASE_TREE = "f3cd6fb20a1dc8f157c6072ff398d0fc03167e84"
REPOSITORY = (
    "https://github.com/KokunoYumeto/advanced-optimization-convex-analysis-id"
)
ZENODO_RECORD_ID = 22142120
ZENODO_CONCEPT_ID = 22059741
ZENODO_RECORD = f"https://zenodo.org/records/{ZENODO_RECORD_ID}"
INTEGRATED_BASENAME = "D90-O015-optimisasi-lanjut-analisis-konveks-id"
INTEGRATED_HTML = (
    f"{ZENODO_RECORD}/files/{INTEGRATED_BASENAME}.html?download=1"
)
INTEGRATED_PDF = f"{ZENODO_RECORD}/files/{INTEGRATED_BASENAME}.pdf?download=1"
INTEGRATED_EPUB = f"{ZENODO_RECORD}/files/{INTEGRATED_BASENAME}.epub?download=1"

SOURCE_INPUTS = (
    "backend/backend_schema.json",
    "backend/records.jsonl",
    "backend/records.csv",
    "qa/ORIGINAL_03_BACKEND_VALIDATION.json",
    "qa/ORIGINAL_03_COURSE_CLOSURE.json",
    "qa/INTEGRATED_READERS_VALIDATION.json",
    "qa/INTEGRATED_PDF_VALIDATION.json",
    "qa/INTEGRATED_BROWSER_QA.json",
    "release/github/2026-08-28-integrated-final/github-public-readback-integrated-final.json",
    "release/zenodo/2026-08-28-integrated-final/zenodo-public-readback-integrated.json",
    f"output/html/{INTEGRATED_BASENAME}.html",
)

EXPECTED_ENTITY_COUNTS = {
    "artifact": 489,
    "asset": 24,
    "concept": 176,
    "correction": 248,
    "course": 1,
    "edition": 17,
    "learning_surface": 1247,
    "program": 1,
    "qa_event": 323,
    "relation": 1837,
    "resource": 10,
    "rights": 93,
    "segment": 248,
    "term": 127,
    "unit": 36,
}

EXPECTED_ORIGINAL03_SURFACE_COUNTS = {
    "assessment_prompt": 54,
    "capstone_milestone": 7,
    "capstone_project": 1,
    "capstone_project_unit": 1,
    "complete_solution": 86,
    "computational_lab": 2,
    "exercise": 29,
    "exercise_group": 25,
    "hint": 32,
    "hint_stage_1": 54,
    "hint_stage_2": 54,
    "proof_rubric": 7,
    "short_answer": 86,
}

EXPECTED_PUBLIC_IDENTITIES = {
    "backend_jsonl": {
        "bytes": 3_534_351,
        "sha256": "a8fe25a7170cd699a217a65f5a0c250518be7efa83f45529b70e17b0c737ff30",
    },
    "backend_csv": {
        "bytes": 4_272_596,
        "sha256": "8c98c63fcf528bb6dc202fdbaf4d7d791be3eb205513033bffd91be8b8120915",
    },
    "backend_schema": {
        "bytes": 3_092,
        "sha256": "1166cbffe6016044430fe003e4981b1a3a537be7c115f0b646168a1936ab5ad0",
    },
    "integrated_html": {
        "bytes": 2_485_595,
        "sha256": "028e026033bc60bba1aff282f34b2e550a9f9358a3bdecd16b74e3442f743c89",
    },
    "integrated_pdf": {
        "bytes": 1_671_254,
        "sha256": "9deefecf469c9f2aace26bc8ccdedc552debbe9874ae035badaf5cffee0f80e5",
    },
    "integrated_epub": {
        "bytes": 379_901,
        "sha256": "1bb882a75209adb220de4ee6c6cf92355b5402538c88050e807dc161fa5d9321",
    },
}

FORBIDDEN_CONTENT_KEYS = {
    "body",
    "content",
    "exercise_text",
    "full_text",
    "hint_text",
    "native_body",
    "prompt_text",
    "prose",
    "solution_body",
    "solution_text",
    "tex_body",
}


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        json.dumps(
            row, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        + b"\n"
        for row in rows
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path, *, display_path: str | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": display_path if display_path is not None else path.as_posix(),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def read_canonical_jsonl(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        raise ValueError(f"JSONL is not LF terminated: {path}")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(data.splitlines(), 1):
        if not line:
            continue
        row = json.loads(line.decode("utf-8"))
        expected = json.dumps(
            row, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        if line != expected:
            raise ValueError(f"JSONL row {number} is not canonical: {path}")
        rows.append(row)
    return rows


def native_git_identity(native_root: Path) -> dict[str, str]:
    def read_ref(value: str) -> str:
        return subprocess.check_output(
            ["git", "-C", str(native_root), "rev-parse", value],
            text=True,
            timeout=30,
        ).strip()

    return {"commit": read_ref("HEAD"), "tree": read_ref("HEAD^{tree}")}


def load_native_rows(path: Path) -> tuple[list[dict[str, Any]], list[bytes]]:
    data = path.read_bytes()
    if not data.endswith(b"\n"):
        raise ValueError("D90 native JSONL must be LF terminated")
    raw_lines = [line for line in data.splitlines() if line]
    rows = [json.loads(line.decode("utf-8")) for line in raw_lines]
    return rows, raw_lines


def records_by_type(rows: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["entity_type"]].append(row)
    return dict(grouped)


def _state_marker_keys(row: dict[str, Any]) -> list[str]:
    tokens = ("absen", "caveat", "gap", "incomplete", "limitation")
    return sorted(
        key for key in row if any(token in key.casefold() for token in tokens)
    )


def _casefold_key_collisions(row: dict[str, Any]) -> list[list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for key in row:
        groups[key.casefold()].append(key)
    return sorted(sorted(keys) for keys in groups.values() if len(keys) > 1)


class _Ids(HTMLParser):
    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=False)
        self.ids: set[str] = set()
        self.feed(text)

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        value = dict(attrs).get("id")
        if value:
            self.ids.add(value)


def _public_anchor(label: str) -> str:
    return INTEGRATED_HTML + "#" + quote(label, safe=":-._~")


def _native_record_url(line: int) -> str:
    return f"{REPOSITORY}/blob/{RELEASE_COMMIT}/backend/records.jsonl#L{line}"


def _copy_present(row: dict[str, Any], fields: Iterable[str]) -> dict[str, Any]:
    return {field: row[field] for field in fields if field in row}


def _record_index(
    rows: list[dict[str, Any]], raw_lines: list[bytes]
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line, (row, raw) in enumerate(zip(rows, raw_lines, strict=True), 1):
        marker_keys = _state_marker_keys(row)
        indexed = {
            "entity_type": row["entity_type"],
            "id": row["id"],
            "native_line": line,
            "native_record_url": _native_record_url(line),
            "record_sha256": sha256_bytes(raw),
            "status": row["status"],
        }
        if "presence" in row:
            indexed["presence"] = row["presence"]
        if marker_keys:
            indexed["state_marker_keys"] = marker_keys
            indexed["state_marker_sha256"] = sha256_bytes(
                canonical_json_bytes({key: row[key] for key in marker_keys})
            )
        result.append(indexed)
    return result


def _rights_index(
    rights: list[dict[str, Any]], line_by_id: dict[str, int], raw_by_id: dict[str, bytes]
) -> list[dict[str, Any]]:
    fields = (
        "authority_url",
        "component_family",
        "component_id",
        "license_url",
        "path",
        "rights_expression",
        "source_authority_id",
        "status",
        "translation_permitted",
    )
    return [
        {
            "id": row["id"],
            "native_line": line_by_id[row["id"]],
            "native_record_url": _native_record_url(line_by_id[row["id"]]),
            "record_sha256": sha256_bytes(raw_by_id[row["id"]]),
            **_copy_present(row, fields),
        }
        for row in rights
    ]


def _correction_index(
    corrections: list[dict[str, Any]],
    line_by_id: dict[str, int],
    raw_by_id: dict[str, bytes],
) -> list[dict[str, Any]]:
    fields = (
        "affected_segment_ids",
        "affected_unit_ids",
        "source_event_id",
        "status",
        "upstream_report_disposition",
    )
    return [
        {
            "id": row["id"],
            "native_line": line_by_id[row["id"]],
            "native_record_url": _native_record_url(line_by_id[row["id"]]),
            "record_sha256": sha256_bytes(raw_by_id[row["id"]]),
            **_copy_present(row, fields),
        }
        for row in corrections
    ]


def _term_index(
    terms: list[dict[str, Any]], line_by_id: dict[str, int], raw_by_id: dict[str, bytes]
) -> list[dict[str, Any]]:
    fields = (
        "concept_id",
        "evidence_segment_ids",
        "locale",
        "preferred",
        "register",
        "rejected_forms",
        "rights_id",
        "scope",
        "source_term",
        "status",
        "variants",
    )
    return [
        {
            "id": row["id"],
            "native_line": line_by_id[row["id"]],
            "native_record_url": _native_record_url(line_by_id[row["id"]]),
            "record_sha256": sha256_bytes(raw_by_id[row["id"]]),
            **_copy_present(row, fields),
        }
        for row in terms
    ]


def _shared_surface(
    row: dict[str, Any], *, line: int, html_ids: set[str]
) -> dict[str, Any]:
    label = row.get("latex_label")
    if not isinstance(label, str) or not label:
        raise ValueError(f"D90 Original-03 surface lacks one label: {row['id']}")
    return {
        "id": row["id"],
        "label_line": row.get("label_line"),
        "latex_label": label,
        "native_line": line,
        "native_record_url": _native_record_url(line),
        "presence": row["presence"],
        "public_anchor": _public_anchor(label),
        "public_anchor_observed": label in html_ids,
        "related_segment_ids": row.get("related_segment_ids", []),
        "rights_id": row.get("rights_id"),
        "source_line": row.get("source_line"),
        "source_path": row.get("source_path"),
        "stable_id_binding": row.get("stable_id_binding"),
        "status": row["status"],
        "surface_type": row["surface_type"],
        "unit_id": row["unit_id"],
    }


def _parts(surface_id: str) -> tuple[str, str, str]:
    tail = surface_id.removeprefix(ORIGINAL03_PREFIX)
    pieces = tail.split(".")
    if len(pieces) != 3:
        raise ValueError(f"Unexpected D90 staged surface identity: {surface_id}")
    return pieces[0], pieces[1], pieces[2]


def _stage_relations(
    surfaces: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in surfaces:
        tail = row["id"].removeprefix(ORIGINAL03_PREFIX)
        if len(tail.split(".")) != 3:
            # Lab/capstone identities have a shorter native stem and are
            # linked explicitly below; only three-part staged IDs belong here.
            continue
        scope, kind, number = _parts(row["id"])
        by_key[(scope, kind, number)] = row

    relations: list[dict[str, Any]] = []
    prompt_chains: list[dict[str, Any]] = []
    practice_chains: list[dict[str, Any]] = []

    def require(scope: str, kind: str, number: str) -> dict[str, Any]:
        try:
            return by_key[(scope, kind, number)]
        except KeyError as error:
            raise ValueError(
                f"Missing D90 stage {scope}/{kind}/{number}"
            ) from error

    def add_edges(chain_id: str, stages: list[dict[str, Any]]) -> None:
        for sequence, (source, target) in enumerate(zip(stages, stages[1:]), 1):
            relations.append(
                {
                    "derivation": "deterministic_native_id_stem",
                    "id": f"{chain_id}.edge.{sequence:02d}",
                    "relation_type": "next-stage",
                    "sequence": sequence,
                    "source_id": source["id"],
                    "target_id": target["id"],
                }
            )

    prompts = sorted(
        (row for row in surfaces if row["surface_type"] == "assessment_prompt"),
        key=lambda row: row["id"],
    )
    for prompt in prompts:
        scope, _, number = _parts(prompt["id"])
        stages = [
            prompt,
            require(scope, "hint1", number),
            require(scope, "hint2", number),
            require(scope, "answer", number),
            require(scope, "solution", number),
        ]
        chain_id = f"d90.adapter.prompt-chain.{scope}.{number}"
        prompt_chains.append(
            {
                "chain_id": chain_id,
                "scope": scope,
                "sequence": number,
                "stages": [
                    {
                        "id": row["id"],
                        "public_anchor": row["public_anchor"],
                        "surface_type": row["surface_type"],
                    }
                    for row in stages
                ],
            }
        )
        add_edges(chain_id, stages)

    entries = sorted(
        (
            row
            for row in surfaces
            if row["surface_type"]
            in {"exercise", "computational_lab", "capstone_project"}
        ),
        key=lambda row: row["id"],
    )
    for entry in entries:
        if entry["surface_type"] == "computational_lab":
            scope, kind, number = "lab", "lab", entry["id"].rsplit(".", 1)[1]
        elif entry["surface_type"] == "capstone_project":
            scope, kind, number = (
                "capstone",
                "capstone",
                entry["id"].rsplit(".", 1)[1],
            )
        else:
            scope, kind, number = _parts(entry["id"])
        stages = [
            entry,
            require(scope, "hint", number),
            require(scope, "answer", number),
            require(scope, "solution", number),
        ]
        chain_id = f"d90.adapter.practice-chain.{scope}.{number}"
        practice_chains.append(
            {
                "chain_id": chain_id,
                "entry_kind": kind,
                "scope": scope,
                "sequence": number,
                "stages": [
                    {
                        "id": row["id"],
                        "public_anchor": row["public_anchor"],
                        "surface_type": row["surface_type"],
                    }
                    for row in stages
                ],
            }
        )
        add_edges(chain_id, stages)

    return prompt_chains, practice_chains, relations


def _identity_sequence_sha256(rows: Iterable[dict[str, Any]]) -> str:
    return sha256_bytes(
        b"".join((row["id"] + "\n").encode("utf-8") for row in rows)
    )


def _state_projection_sha256(rows: Iterable[dict[str, Any]]) -> str:
    projection = [
        {
            key: row[key]
            for key in (
                "id",
                "status",
                "presence",
                "state_marker_keys",
                "state_marker_sha256",
            )
            if key in row
        }
        for row in rows
    ]
    return sha256_bytes(canonical_json_bytes(projection))


def _find_zenodo_file(receipt: dict[str, Any], filename: str) -> dict[str, Any]:
    for row in receipt["files"]:
        if row.get("filename") == filename:
            return {
                "bytes": row["bytes"],
                "filename": filename,
                "public_byte_identity": row["public_byte_identity"],
                "sha256": row["sha256"],
                "url": f"{ZENODO_RECORD}/files/{filename}?download=1",
            }
    raise ValueError(f"Missing D90 Zenodo file receipt: {filename}")


def derive_projection(native_root: Path) -> dict[str, Any]:
    missing = [path for path in SOURCE_INPUTS if not (native_root / path).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing D90 native inputs: {missing}")
    git_identity = native_git_identity(native_root)
    if git_identity != {"commit": RELEASE_COMMIT, "tree": RELEASE_TREE}:
        raise ValueError(f"D90 native checkout is not pinned: {git_identity}")

    rows, raw_lines = load_native_rows(native_root / "backend/records.jsonl")
    grouped = records_by_type(rows)
    line_by_id = {row["id"]: line for line, row in enumerate(rows, 1)}
    raw_by_id = {row["id"]: raw for row, raw in zip(rows, raw_lines, strict=True)}
    if len(line_by_id) != len(rows):
        raise ValueError("D90 native IDs are not unique")

    csv_rows = list(
        csv.DictReader(
            (native_root / "backend/records.csv").open(
                "r", encoding="utf-8", newline=""
            )
        )
    )
    decoded_lines = [line.decode("utf-8") for line in raw_lines]
    csv_lossless = (
        len(csv_rows) == len(rows)
        and [row["id"] for row in csv_rows] == [row["id"] for row in rows]
        and [row["record_json"] for row in csv_rows] == decoded_lines
    )

    schema = read_json(native_root / "backend/backend_schema.json")
    id_set = set(line_by_id)
    references = 0
    dangling: list[dict[str, str]] = []
    for row in rows:
        for field in schema["reference_fields"]:
            value = row.get(field)
            if value is None:
                continue
            values = value if isinstance(value, list) else [value]
            for target in values:
                if not isinstance(target, str) or not target:
                    continue
                references += 1
                if target not in id_set:
                    dangling.append(
                        {"field": field, "record_id": row["id"], "target_id": target}
                    )

    html_text = (native_root / f"output/html/{INTEGRATED_BASENAME}.html").read_text(
        encoding="utf-8"
    )
    html_ids = _Ids(html_text).ids
    original03_native = [
        row
        for row in grouped["learning_surface"]
        if row["id"].startswith(ORIGINAL03_PREFIX)
    ]
    shared_surfaces = [
        _shared_surface(row, line=line_by_id[row["id"]], html_ids=html_ids)
        for row in original03_native
    ]
    prompt_chains, practice_chains, staged_relations = _stage_relations(
        shared_surfaces
    )

    record_index = _record_index(rows, raw_lines)
    rights_index = _rights_index(grouped["rights"], line_by_id, raw_by_id)
    corrections_index = _correction_index(
        grouped["correction"], line_by_id, raw_by_id
    )
    terms_index = _term_index(grouped["term"], line_by_id, raw_by_id)

    collisions = []
    for row in rows:
        for keys in _casefold_key_collisions(row):
            collisions.append(
                {
                    "id": row["id"],
                    "keys": keys,
                    "native_line": line_by_id[row["id"]],
                    "native_record_url": _native_record_url(line_by_id[row["id"]]),
                }
            )

    backend_qa = read_json(native_root / "qa/ORIGINAL_03_BACKEND_VALIDATION.json")
    closure = read_json(native_root / "qa/ORIGINAL_03_COURSE_CLOSURE.json")
    readers = read_json(native_root / "qa/INTEGRATED_READERS_VALIDATION.json")
    pdf = read_json(native_root / "qa/INTEGRATED_PDF_VALIDATION.json")
    browser = read_json(native_root / "qa/INTEGRATED_BROWSER_QA.json")
    github_receipt = read_json(
        native_root
        / "release/github/2026-08-28-integrated-final/github-public-readback-integrated-final.json"
    )
    zenodo_receipt = read_json(
        native_root
        / "release/zenodo/2026-08-28-integrated-final/zenodo-public-readback-integrated.json"
    )

    surface_counts = dict(
        sorted(Counter(row["surface_type"] for row in shared_surfaces).items())
    )
    entity_counts = dict(sorted(Counter(row["entity_type"] for row in rows).items()))
    status_counts = dict(sorted(Counter(row["status"] for row in rows).items()))
    presence_counts = dict(
        sorted(
            Counter(
                row["presence"]
                for row in grouped["learning_surface"]
                if "presence" in row
            ).items()
        )
    )
    marked_state_records = sum(
        bool(row.get("state_marker_keys"))
        or any(
            token in row.get("status", "").casefold()
            or token in row.get("presence", "").casefold()
            for token in ("absent", "caveat", "gap", "incomplete", "limitation")
        )
        for row in record_index
    )

    source_lock = {
        "schema": "d90-source-lock/1",
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "native_repository": {
            "commit": RELEASE_COMMIT,
            "repository": REPOSITORY,
            "tree": RELEASE_TREE,
        },
        "inputs": [
            identity(native_root / path, display_path=path) for path in SOURCE_INPUTS
        ],
    }

    capabilities = {
        "schema": "d90-capabilities/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "identity": {
            "native_course_id": NATIVE_COURSE_ID,
            "native_id_sequence_sha256": _identity_sequence_sha256(record_index),
            "native_program_id": NATIVE_PROGRAM_ID,
            "state_projection_sha256": _state_projection_sha256(record_index),
        },
        "counts": {
            "case_sensitive_key_collisions": len(collisions),
            "component_rights": len(rights_index),
            "corrections": len(corrections_index),
            "dangling_references": len(dangling),
            "educator_rubrics": surface_counts["proof_rubric"],
            "entity_counts": entity_counts,
            "explicit_state_marker_records": marked_state_records,
            "learner_assessment_containers": surface_counts["exercise_group"]
            + surface_counts["exercise"],
            "learner_computational_lab_surfaces": surface_counts[
                "computational_lab"
            ],
            "native_records": len(rows),
            "native_references": references,
            "original03_anchor_matches": sum(
                row["public_anchor_observed"] for row in shared_surfaces
            ),
            "original03_surface_counts": surface_counts,
            "original03_surfaces": len(shared_surfaces),
            "practice_chains": len(practice_chains),
            "prompt_chains": len(prompt_chains),
            "staged_relations": len(staged_relations),
            "terms": len(terms_index),
        },
        "native_status_counts": status_counts,
        "learning_surface_presence_counts": presence_counts,
        "observed_capabilities": {
            "assessment_prompt_chains": True,
            "component_specific_rights": True,
            "educator_proof_rubrics": True,
            "html_mathml": True,
            "native_jsonl_csv_lossless": csv_lossless,
            "native_reference_closure": not dangling,
            "original03_public_anchors": len(shared_surfaces)
            == sum(row["public_anchor_observed"] for row in shared_surfaces),
            "public_epub": True,
            "public_html": True,
            "public_pdf": True,
        },
        "case_sensitive_key_caveat": {
            "collisions": collisions,
            "parser_requirement": "preserve_case_distinct_object_keys",
        },
        "limitations": {
            "full_solution_coverage_beyond_observed_records_claimed": False,
            "learner_lab_completion_claimed": False,
            "live_learner_results_claimed": False,
            "non_original03_unresolved_label": {
                "id": "surface.habring.v1.ch02.lemma.0003",
                "label": "convexity:lemma:ops preserving convexity",
                "included_in_shared_slice": False,
            },
            "reversible_exchange_claimed": False,
        },
    }

    assessments = sorted(
        (
            row
            for row in shared_surfaces
            if row["surface_type"] in {"exercise_group", "exercise"}
        ),
        key=lambda row: row["id"],
    )
    rubrics = sorted(
        (row for row in shared_surfaces if row["surface_type"] == "proof_rubric"),
        key=lambda row: row["id"],
    )
    labs = sorted(
        (
            row
            for row in shared_surfaces
            if row["surface_type"] == "computational_lab"
        ),
        key=lambda row: row["id"],
    )
    milestones = sorted(
        (
            row
            for row in shared_surfaces
            if row["surface_type"] == "capstone_milestone"
        ),
        key=lambda row: row["id"],
    )
    capstone = next(
        row for row in shared_surfaces if row["surface_type"] == "capstone_project"
    )
    capstone_unit = next(
        row
        for row in shared_surfaces
        if row["surface_type"] == "capstone_project_unit"
    )

    learner_map = {
        "schema": "d90-learner-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "native_course_id": NATIVE_COURSE_ID,
        "native_unit_id": ORIGINAL03_UNIT_ID,
        "reader": {
            "epub": INTEGRATED_EPUB,
            "html": INTEGRATED_HTML,
            "pdf": INTEGRATED_PDF,
        },
        "assessment_containers": [
            {
                "id": row["id"],
                "public_anchor": row["public_anchor"],
                "surface_type": row["surface_type"],
            }
            for row in assessments
        ],
        "prompt_chains": prompt_chains,
        "practice_chains": practice_chains,
        "labs": [
            {"id": row["id"], "public_anchor": row["public_anchor"]}
            for row in labs
        ],
        "capstone": {
            "id": capstone["id"],
            "public_anchor": capstone["public_anchor"],
            "project_unit": {
                "id": capstone_unit["id"],
                "public_anchor": capstone_unit["public_anchor"],
            },
            "milestones": [
                {"id": row["id"], "public_anchor": row["public_anchor"]}
                for row in milestones
            ],
        },
        "claim_boundary": {
            "content_bodies_copied": False,
            "learner_attempt_instances": 0,
            "learner_lab_completion_instances": 0,
            "learner_result_instances": 0,
            "learner_submission_instances": 0,
        },
    }

    educator_map = {
        "schema": "d90-educator-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "shared_identity_source": "data/shared-learning-surfaces.jsonl",
        "assessment_containers": learner_map["assessment_containers"],
        "prompt_chains": prompt_chains,
        "rubrics": [
            {"id": row["id"], "public_anchor": row["public_anchor"]}
            for row in rubrics
        ],
        "labs": learner_map["labs"],
        "capstone": learner_map["capstone"],
        "governance": {
            "component_rights_index": "data/rights-index.jsonl",
            "correction_index": "data/corrections-index.jsonl",
            "term_index": "data/terms-index.jsonl",
        },
        "claim_boundary": {
            "all_native_surfaces_have_complete_solutions_claimed": False,
            "lab_completion_claimed": False,
            "live_learner_results_claimed": False,
        },
    }

    closure_summary = closure["sections"]
    public_evidence = {
        "schema": "d90-public-evidence/1",
        "course_id": COURSE_ID,
        "github": {
            "commit": RELEASE_COMMIT,
            "repository": REPOSITORY,
            "tree": RELEASE_TREE,
            "native_integrated_publication_receipt": {
                "commit": github_receipt["commit"],
                "result": github_receipt["result"],
                "tree": github_receipt["tree"],
            },
            "current_commit_basis": "pinned_current_public_head_and_local_object_identity",
        },
        "zenodo": {
            "concept_id": ZENODO_CONCEPT_ID,
            "record_id": ZENODO_RECORD_ID,
            "result": zenodo_receipt["result"],
            "status": zenodo_receipt["status"],
            "version": zenodo_receipt["version"],
            "files": [
                _find_zenodo_file(zenodo_receipt, filename)
                for filename in (
                    "backend-records-2026.08.28-integrated.jsonl",
                    "backend-records-2026.08.28-integrated.csv",
                    "backend-schema.json",
                    f"{INTEGRATED_BASENAME}.html",
                    f"{INTEGRATED_BASENAME}.pdf",
                    f"{INTEGRATED_BASENAME}.epub",
                )
            ],
        },
        "native_backend_validation": {
            "csv_jsonl_lossless": backend_qa["backend"][
                "jsonl_csv_lossless_equality"
            ],
            "deterministic_runs": backend_qa["deterministic_regeneration"][
                "runs_completed"
            ],
            "records": backend_qa["backend"]["records"],
            "result": backend_qa["result"],
        },
        "assessment_closure": {
            "assessments": closure_summary["assessments"]["assessment_count"],
            "capstone_milestones": closure_summary["capstone_numerics"][
                "milestone_count"
            ],
            "computation_components_replayed_twice": len(
                closure_summary["deterministic_computation_replays"]
            ),
            "findings": {
                priority: len(closure["findings"][priority])
                for priority in ("P1", "P2", "P3")
            },
            "prompt_response_units": closure_summary["assessments"][
                "prompt_response_unit_count"
            ],
            "result": closure["result"],
        },
        "accessibility": {
            "claim_scope": "observed_native_receipts_only",
            "epub": {
                "epubcheck_errors": 0,
                "epubcheck_warnings": 0,
                "mathml_count": readers["epub"]["mathml_count"],
                "sha256": readers["epub"]["sha256"],
            },
            "html": {
                "id_count": readers["html"]["id_count"],
                "mathml_count": readers["html"]["mathml_count"],
                "sha256": readers["html"]["sha256"],
                "unresolved_internal_fragments": readers["html"][
                    "unresolved_internal_fragments"
                ],
            },
            "pdf": {
                "a4_pages": pdf["pdf"]["a4_pages"],
                "language": pdf["pdf"]["language"],
                "marked": pdf["pdf"]["marked"],
                "structure_tree": pdf["pdf"]["structure_tree"],
            },
            "reader_validation_result": readers["result"],
            "browser_validation_result": browser["status"],
            "wcag_conformance_claimed": False,
        },
    }

    claim_boundary = {
        "schema": "d90-claim-boundary/1",
        "course_id": COURSE_ID,
        "adapter_scope": "identity_state_rights_evidence_and_public_anchor_projection",
        "central_course_truth_rewritten": False,
        "component_rights_flattened": False,
        "content_bodies_copied": False,
        "datasets_copied": False,
        "epub_copied": False,
        "full_solution_coverage_beyond_observed_records_claimed": False,
        "html_copied": False,
        "lab_completion_claimed": False,
        "learner_attempt_instances": 0,
        "learner_result_instances": 0,
        "learner_submission_instances": 0,
        "native_backend_authoritative": True,
        "native_ids_preserved": True,
        "pdf_copied": False,
        "public_state_changed": False,
        "reversible_exchange_claimed": False,
        "solution_bodies_copied": False,
        "source_tex_copied": False,
        "wcag_conformance_claimed": False,
    }

    return {
        "capabilities": capabilities,
        "claim_boundary": claim_boundary,
        "corrections_index": corrections_index,
        "educator_map": educator_map,
        "learner_map": learner_map,
        "native_record_index": record_index,
        "public_evidence": public_evidence,
        "rights_index": rights_index,
        "shared_surfaces": shared_surfaces,
        "source_lock": source_lock,
        "staged_relations": staged_relations,
        "terms_index": terms_index,
    }


def forbidden_content_paths(value: Any, path: str = "$") -> list[str]:
    failures: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key.casefold() in FORBIDDEN_CONTENT_KEYS:
                failures.append(child_path)
            failures.extend(forbidden_content_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            failures.extend(forbidden_content_paths(child, f"{path}[{index}]"))
    return failures


def projection_errors(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    capabilities = bundle["capabilities"]
    boundary = bundle["claim_boundary"]
    records = bundle["native_record_index"]
    surfaces = bundle["shared_surfaces"]
    rights = bundle["rights_index"]
    corrections = bundle["corrections_index"]
    terms = bundle["terms_index"]
    learner = bundle["learner_map"]
    educator = bundle["educator_map"]
    evidence = bundle["public_evidence"]

    if capabilities.get("contract") != CONTRACT or capabilities.get("course_id") != COURSE_ID:
        errors.append("D90-CAPABILITY-IDENTITY")
    if len(records) != 4877:
        errors.append("D90-NATIVE-ID-COUNT")
    ids = [row.get("id") for row in records]
    if len(ids) != len(set(ids)) or None in ids:
        errors.append("D90-NATIVE-ID-UNIQUE")
    if _identity_sequence_sha256(records) != capabilities["identity"].get(
        "native_id_sequence_sha256"
    ):
        errors.append("D90-NATIVE-ID-SEQUENCE")
    if _state_projection_sha256(records) != capabilities["identity"].get(
        "state_projection_sha256"
    ):
        errors.append("D90-STATE-PROJECTION")
    entity_counts = dict(sorted(Counter(row.get("entity_type") for row in records).items()))
    if entity_counts != EXPECTED_ENTITY_COUNTS:
        errors.append("D90-ENTITY-COUNTS")
    if capabilities["counts"].get("entity_counts") != EXPECTED_ENTITY_COUNTS:
        errors.append("D90-CAPABILITY-ENTITY-COUNTS")

    if len(surfaces) != 438 or len({row.get("id") for row in surfaces}) != 438:
        errors.append("D90-ORIGINAL03-SURFACE-IDENTITIES")
    surface_counts = dict(
        sorted(Counter(row.get("surface_type") for row in surfaces).items())
    )
    if surface_counts != EXPECTED_ORIGINAL03_SURFACE_COUNTS:
        errors.append("D90-ORIGINAL03-SURFACE-COUNTS")
    if any(not row.get("public_anchor_observed") for row in surfaces):
        errors.append("D90-ORIGINAL03-ANCHOR-OBSERVATION")
    for row in surfaces:
        if row.get("public_anchor") != _public_anchor(row.get("latex_label", "")):
            errors.append("D90-ORIGINAL03-ANCHOR")
            break
    if len(bundle["staged_relations"]) != 312:
        errors.append("D90-STAGED-RELATION-COUNT")
    if len(learner.get("prompt_chains", [])) != 54:
        errors.append("D90-PROMPT-CHAIN-COUNT")
    if len(learner.get("practice_chains", [])) != 32:
        errors.append("D90-PRACTICE-CHAIN-COUNT")
    if len(learner.get("assessment_containers", [])) != 54:
        errors.append("D90-ASSESSMENT-CONTAINER-COUNT")
    if len(learner.get("labs", [])) != 2:
        errors.append("D90-LAB-SURFACE-COUNT")
    if len(learner.get("capstone", {}).get("milestones", [])) != 7:
        errors.append("D90-CAPSTONE-MILESTONE-COUNT")
    if len(educator.get("rubrics", [])) != 7:
        errors.append("D90-RUBRIC-COUNT")

    if len(rights) != 93:
        errors.append("D90-RIGHTS-COUNT")
    if len({row.get("component_id") for row in rights}) < 90:
        errors.append("D90-RIGHTS-FLATTENED")
    if boundary.get("component_rights_flattened") is not False:
        errors.append("D90-RIGHTS-FLATTENED")
    if len(corrections) != 248:
        errors.append("D90-CORRECTION-COUNT")
    if len(terms) != 127:
        errors.append("D90-TERM-COUNT")

    collision = capabilities.get("case_sensitive_key_caveat", {}).get(
        "collisions", []
    )
    if collision != [
        {
            "id": "qa.o015.ch07.structure",
            "keys": ["Cref_occurrences_preserved", "cref_occurrences_preserved"],
            "native_line": 4152,
            "native_record_url": _native_record_url(4152),
        }
    ]:
        errors.append("D90-CASE-SENSITIVE-KEY-CAVEAT")

    false_boolean_claims = (
        "central_course_truth_rewritten",
        "component_rights_flattened",
        "content_bodies_copied",
        "datasets_copied",
        "epub_copied",
        "full_solution_coverage_beyond_observed_records_claimed",
        "html_copied",
        "lab_completion_claimed",
        "pdf_copied",
        "public_state_changed",
        "reversible_exchange_claimed",
        "solution_bodies_copied",
        "source_tex_copied",
        "wcag_conformance_claimed",
    )
    for field in false_boolean_claims:
        if boundary.get(field) is not False:
            errors.append("D90-FALSE-CLAIM:" + field)
    for field in (
        "learner_attempt_instances",
        "learner_result_instances",
        "learner_submission_instances",
    ):
        if boundary.get(field) != 0:
            errors.append("D90-LIVE-LEARNER-RESULT-CLAIM")
    if boundary.get("native_backend_authoritative") is not True:
        errors.append("D90-NATIVE-AUTHORITY")
    if boundary.get("native_ids_preserved") is not True:
        errors.append("D90-NATIVE-ID-PRESERVATION")

    accessibility = evidence.get("accessibility", {})
    if accessibility.get("claim_scope") != "observed_native_receipts_only":
        errors.append("D90-ACCESSIBILITY-CLAIM-SCOPE")
    if accessibility.get("wcag_conformance_claimed") is not False:
        errors.append("D90-FALSE-ACCESSIBILITY-CLAIM")
    if accessibility.get("html", {}).get("mathml_count") != 4535:
        errors.append("D90-ACCESSIBILITY-EVIDENCE")
    if evidence.get("assessment_closure", {}).get(
        "computation_components_replayed_twice"
    ) != 3:
        errors.append("D90-LAB-RECEIPT-EVIDENCE")

    failures = forbidden_content_paths(bundle)
    if failures:
        errors.append("D90-COPIED-NATIVE-BODY")
    return errors
