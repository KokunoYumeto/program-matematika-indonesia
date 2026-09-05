"""Lossless, zero-copy B40 capability projection over the native R005 backend.

The adapter deliberately projects identifiers, hierarchy, locators, hashes, and
public evidence.  It never copies segment text or source/translation bodies.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


COURSE_ID = "B40"
NATIVE_ROLE_ID = "R005"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"
NATIVE_SCHEMA = "hefferon-modular-backend"
NATIVE_SCHEMA_VERSION = "0.5.2"
PUBLIC_READBACK = "backend/course-capsule-v1/adapters/b40-capability-v1/input/public-native-readback.json"
MIGRATION_RECEIPT = "releases/v0.59.0/hefferon-linear-algebra-id-backend-v1-migration-receipt.json"
LOCAL_SOURCE_LOCATOR = "04_mirrors/id/hefferon-linear-algebra-id/backend"
HUB_WORKSPACE_LOCATOR = "04_mirrors/id/program-matematika-indonesia-d120-current"
PUBLIC_READBACK_WORKSPACE = f"{HUB_WORKSPACE_LOCATOR}/{PUBLIC_READBACK}"
MIGRATION_RECEIPT_WORKSPACE = f"{HUB_WORKSPACE_LOCATOR}/{MIGRATION_RECEIPT}"

EXPECTED_ENTITY_RECORDS = 8_132
EXPECTED_NATIVE_RECORDS = 22_131
EXPECTED_UNITS = 3_541
EXPECTED_SEGMENTS = 3_528
EXPECTED_EXERCISES = 1_037
EXPECTED_ANSWERS = 1_037
EXPECTED_UPSTREAM_ANSWERS = 1_035
EXPECTED_SUPPLIED_ANSWERS = 2
EXPECTED_CONCEPTS = 114
EXPECTED_TERMS = 114
EXPECTED_CORRECTIONS = 307
EXPECTED_RELATIONS = 13_999
EXPECTED_RELATION_PROJECTION_SHA256 = "dffc2bf558d2419a92808848f19c3d4c1e07f1ac2ec7b5b22c6d9facd0dacb38"
EXPECTED_RIGHTS = 11
EXPECTED_ARTIFACTS = 8
EXPECTED_ASSETS = 432
EXPECTED_QA_EVENTS = 72
EXPECTED_SOURCE_FILES = 64

EXPECTED_PUBLIC_CHECKS = {
    "exact_commit_and_tree": True,
    "native_backend_manifest_hash_closure": True,
    "immutable_native_files_fetched": 15,
    "github_release_asset_inventory_exact": True,
    "full_release_artifacts_sha256_verified": 8,
    "large_release_artifacts_anonymously_available": 1,
    "zenodo_record_open_and_inventory_exact": True,
    "exercise_answer_bijection_verified": True,
    "target_supplied_answer_provenance_preserved": True,
    "reader_landing_page_fetched": True,
    "external_state_changed": False,
}

EXPECTED_PUBLIC_READER = {
    "url": "https://kokunoyumeto.github.io/hefferon-linear-algebra-id/",
    "status": 200,
    "bytes": 1351,
    "sha256": "ae36993c025be42644042294e409e3a81f78e9b9c5247c773e2184d5bd1b6d03",
    "scope": "release_landing_page_not_full_html_textbook",
}

EXPECTED_NATIVE_REPOSITORY = {
    "url": "https://github.com/KokunoYumeto/hefferon-linear-algebra-id",
    "current_public_head": "e84ce2956a7304830c42eba70106f940fefee7c4",
    "current_public_tree": "b434745225bb3931d51d107d8d8e5c0c8707af5d",
    "source_repository": "https://gitlab.com/jim.hefferon/linear-algebra",
    "source_commit": "df2262e089a02651c127f1dd12649c4622ee1383",
    "source_tree": "30340725aa2641b3c617b1584c59f6df83e1fdf3",
}

EXPECTED_RELATION_TYPES = {
    "adapts": 3,
    "answers": 1037,
    "contains": 7178,
    "corrects": 324,
    "depends-on": 368,
    "exercises": 2208,
    "precedes": 2273,
    "translates": 114,
    "xref": 494,
}

EXPECTED_UNIT_KINDS = {
    "answer": 1037,
    "answer_book": 1,
    "chapter": 17,
    "definition": 86,
    "example": 263,
    "exercise": 1037,
    "exercise_group": 67,
    "exercise_note": 5,
    "external_reference": 1,
    "interactive": 184,
    "program": 133,
    "proof": 113,
    "remark": 31,
    "sage_lab": 1,
    "section": 57,
    "source_file": 64,
    "subsection": 70,
    "table": 241,
    "textbook": 1,
    "theorem": 132,
}

EXPECTED_NATIVE_MEMBER_PATHS = (
    "artifacts.jsonl",
    "assets.jsonl",
    "authority.jsonl",
    "concepts.jsonl",
    "corrections.jsonl",
    "courses.jsonl",
    "interoperability.json",
    "programs.jsonl",
    "qa_events.jsonl",
    "relations.csv",
    "rights.jsonl",
    "segments.jsonl",
    "source_closure.json",
    "terminology.jsonl",
    "units.jsonl",
)

EXPECTED_ARTIFACT_IDENTITIES = {
    ("r005.hefferon-linear-algebra.artifact.answer-pdf.locale.id-id", 2_672_266, 435, "61f8a344cade529249d4f165bb62bce17579b6a4408b11634999e9f73ec9c01b"),
    ("r005.hefferon-linear-algebra.artifact.authority-answer.book.pdf.df2262e", 1_789_766, 404, "6e1761061c136a984400198f62253cf208ca36ddee81415ae13de81319b5429d"),
    ("r005.hefferon-linear-algebra.artifact.authority-sage.lab.pdf.df2262e", 13_121_660, 105, "0ca33cb79632c3b27c964a6dc8e31f8315d5a529f9e7214ced7f8cb49003b6a2"),
    ("r005.hefferon-linear-algebra.artifact.authority-textbook.pdf.df2262e", 7_626_685, 525, "5240f2782e645bc6351ad9eba69d8c19500142a5cca9c90450c17b3765a1a400"),
    ("r005.hefferon-linear-algebra.artifact.backend-snapshot.locale.id-id.current", 53_171_327, None, "783aef96ba29d701aec0d7ac2e17a33060380eb632f70b3f6205d2a72114bcd8"),
    ("r005.hefferon-linear-algebra.artifact.sage-lab-pdf.locale.id-id", 13_164_259, 109, "adb78966020355a90442c7ae68c734f1fd6b44b5d935a3f75e531ea666eeee4a"),
    ("r005.hefferon-linear-algebra.artifact.source-snapshot.locale.id-id.current", 48_131_554, None, "bb1f0b6d8201867e55504e08eb198374f1d559dffdc24110126c4f96be3cfecd"),
    ("r005.hefferon-linear-algebra.artifact.textbook-pdf.locale.id-id", 8_984_459, 580, "0462ddc8ffcc901efbc81205f79a249ae716e838a6ec32eda033444a90b8755e"),
}

COMPONENTS = (
    ("main-textbook", "textbook", "Buku teks"),
    ("answer-book-shell", "answer_book", "Buku jawaban"),
    ("sage-lab", "sage_lab", "Laboratorium Sage"),
)

PRESENTATION_TITLE_OVERRIDES = {
    "r005.hefferon-linear-algebra.unit.file.src.det.det1.tex.section.source-order.0002": {
        "raw_native_title_id": "Def inisi",
        "presentation_title_id": "Definisi",
        "basis": "presentation normalization of a native LaTeX empty-group word boundary",
    },
    "r005.hefferon-linear-algebra.unit.file.src.lab.preface.tex.section.source-order.0002": {
        "raw_native_title_id": "Mengapa ?",
        "presentation_title_id": "Mengapa Sage?",
        "basis": "presentation expansion of the omitted native Sage macro name",
    },
    "r005.hefferon-linear-algebra.unit.file.src.lab.sageintro.tex.chapter.source-order.0001": {
        "raw_native_title_id": "dan",
        "presentation_title_id": "Python dan Sage",
        "basis": "presentation expansion of omitted native Python and Sage macro names",
    },
}


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def compact_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path, *, display_path: str | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": display_path if display_path is not None else path.as_posix(),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def native_input_identity(path: Path, relative: str) -> dict[str, Any]:
    return identity(path, display_path=f"{LOCAL_SOURCE_LOCATOR}/{relative}")


def hub_input_identity(path: Path, workspace_path: str) -> dict[str, Any]:
    return identity(path, display_path=workspace_path)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _inventory_identity(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    data = b"".join(
        f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n".encode("utf-8")
        for row in rows
    )
    return {"bytes": len(data), "sha256": sha256_bytes(data)}


def _preorder(roots: list[str], children: dict[str, list[dict[str, Any]]]) -> list[str]:
    result: list[str] = []

    def visit(unit_id: str) -> None:
        result.append(unit_id)
        for child in children.get(unit_id, []):
            visit(child["id"])

    for root in roots:
        visit(root)
    return result


def _selected(record: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    """Keep exact native metadata fields, including explicit nulls, but no bodies."""
    return {field: record.get(field) for field in fields}


def _presentation_title(unit: dict[str, Any]) -> tuple[str | None, str]:
    native_title = unit.get("target_title")
    override = PRESENTATION_TITLE_OVERRIDES.get(unit["id"])
    if not override:
        return native_title, "native_title"
    if native_title != override["raw_native_title_id"]:
        raise ValueError(f"B40 presentation override no longer matches native title: {unit['id']}")
    return override["presentation_title_id"], override["basis"]


def _public_evidence_projection(public: dict[str, Any]) -> dict[str, Any]:
    """Allowlist verifier metadata so diagnostic/body payloads can never leak in."""
    github = public["github"]
    release = github["release"]
    return {
        "schema": "b40-public-evidence/1",
        "course_id": COURSE_ID,
        "verified_date": public["verified_date"],
        "access_mode": public["access_mode"],
        "github": {
            **_selected(github, ("repository", "current_head", "current_tree", "repository_public")),
            "current_commit_api": _selected(github["current_commit_api"], ("status", "bytes", "sha256")),
            "native_backend_manifest": _selected(
                github["native_backend_manifest"], ("path", "url", "status", "bytes", "sha256")
            ),
            "native_backend_files": [
                _selected(row, ("path", "url", "status", "bytes", "sha256"))
                for row in github["native_backend_files"]
            ],
            "supporting_raw_files": [
                _selected(row, ("path", "url", "status", "bytes", "sha256"))
                for row in github["supporting_raw_files"]
            ],
            "release": {
                **_selected(release, ("tag", "url")),
                "assets": [
                    _selected(row, ("name", "bytes", "sha256", "pages", "url"))
                    for row in release["assets"]
                ],
                "fully_downloaded_and_sha256_verified": [
                    _selected(row, ("name", "status", "bytes", "sha256"))
                    for row in release["fully_downloaded_and_sha256_verified"]
                ],
                "large_asset_anonymous_head_checks": [
                    _selected(
                        row,
                        ("name", "status", "final_url_host", "expected_bytes", "expected_sha256"),
                    )
                    for row in release["large_asset_anonymous_head_checks"]
                ],
            },
        },
        "zenodo": {
            **_selected(
                public["zenodo"],
                ("record_id", "doi", "concept_record_id", "concept_doi", "status", "access_right"),
            ),
            "files": [
                _selected(row, ("name", "bytes", "checksum")) for row in public["zenodo"]["files"]
            ],
        },
        "reader": _selected(public["reader"], ("url", "status", "bytes", "sha256", "scope")),
        "checks": _selected(
            public["checks"],
            (
                "exact_commit_and_tree",
                "native_backend_manifest_hash_closure",
                "immutable_native_files_fetched",
                "github_release_asset_inventory_exact",
                "full_release_artifacts_sha256_verified",
                "large_release_artifacts_anonymously_available",
                "zenodo_record_open_and_inventory_exact",
                "exercise_answer_bijection_verified",
                "target_supplied_answer_provenance_preserved",
                "reader_landing_page_fetched",
                "external_state_changed",
            ),
        ),
        "credentials_recorded": public["credentials_recorded"],
        "native_semantic_html_claimed": False,
        "native_epub_claimed": False,
        "tagged_pdf_claimed": False,
        "mathml_claimed": False,
        "accessibility_conformance_claimed": False,
        "public_state_changed": False,
    }


def _native_manifest(native_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = native_root / "manifest.json"
    manifest = read_json(manifest_path)
    if (
        manifest.get("schema") != NATIVE_SCHEMA
        or manifest.get("schema_version") != NATIVE_SCHEMA_VERSION
        or manifest.get("generated_file_count") != 15
    ):
        raise ValueError("B40 native manifest identity or member count drift")
    members = manifest.get("files", [])
    if (
        len(members) != 15
        or tuple(row.get("path") for row in members) != EXPECTED_NATIVE_MEMBER_PATHS
        or len({row.get("path") for row in members}) != 15
    ):
        raise ValueError("B40 native manifest must contain the exact 15-member inventory")
    verified = []
    for row in members:
        relative = str(row["path"])
        relative_path = Path(relative)
        candidate = native_root / relative_path
        if relative_path.is_absolute() or len(relative_path.parts) != 1 or candidate.is_symlink():
            raise ValueError(f"B40 unsafe native manifest member path: {relative}")
        actual = identity(candidate, display_path=relative)
        if actual != {"path": relative, "bytes": row["bytes"], "sha256": row["sha256"]}:
            raise ValueError(f"B40 native manifest member identity drift: {relative}")
        verified.append(actual)
    return manifest, verified


def _record_inventory(native_root: Path) -> tuple[dict[str, int], set[str]]:
    paths = (
        "artifacts.jsonl", "assets.jsonl", "authority.jsonl", "concepts.jsonl",
        "corrections.jsonl", "courses.jsonl", "programs.jsonl", "qa_events.jsonl",
        "rights.jsonl", "segments.jsonl", "terminology.jsonl", "units.jsonl",
    )
    counts: dict[str, int] = {}
    ids: set[str] = set()
    physical_rows = 0
    for relative in paths:
        count = 0
        with (native_root / relative).open("r", encoding="utf-8", newline="") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                record_id = row.get("id")
                if not isinstance(record_id, str) or not record_id or record_id in ids:
                    raise ValueError(f"B40 duplicate or missing entity ID in {relative}")
                ids.add(record_id)
                count += 1
        counts[relative] = count
        physical_rows += count
    if physical_rows != EXPECTED_ENTITY_RECORDS or len(ids) != EXPECTED_ENTITY_RECORDS:
        raise ValueError("B40 entity record inventory drift")
    return counts, ids


def _component_id(unit: dict[str, Any], root_ids: set[str]) -> str:
    matches = [unit_id for unit_id in unit.get("path", []) if unit_id in root_ids]
    if unit["id"] in root_ids and unit["id"] not in matches:
        matches.append(unit["id"])
    if len(matches) != 1:
        raise ValueError(f"B40 unit component path is not singular: {unit['id']}")
    return matches[0]


def derive_projection(native_root: Path, hub_root: Path) -> dict[str, Any]:
    public_path = hub_root / PUBLIC_READBACK
    migration_path = hub_root / MIGRATION_RECEIPT
    if not public_path.is_file() or not migration_path.is_file():
        raise FileNotFoundError("Missing B40 anonymous public readback or zero-copy migration receipt")

    manifest, native_inputs = _native_manifest(native_root)
    qualified_native_inputs = [
        {**row, "path": f"{LOCAL_SOURCE_LOCATOR}/{row['path']}"} for row in native_inputs
    ]
    record_counts_by_file, entity_ids = _record_inventory(native_root)
    public_bytes = public_path.read_bytes()
    migration_bytes = migration_path.read_bytes()
    public_input_identity = {
        "path": PUBLIC_READBACK_WORKSPACE,
        "bytes": len(public_bytes),
        "sha256": sha256_bytes(public_bytes),
    }
    migration_input_identity = {
        "path": MIGRATION_RECEIPT_WORKSPACE,
        "bytes": len(migration_bytes),
        "sha256": sha256_bytes(migration_bytes),
    }
    public = json.loads(public_bytes)
    migration = json.loads(migration_bytes)
    interoperability = read_json(native_root / "interoperability.json")
    closure = read_json(native_root / "source_closure.json")

    closure_without_hash = dict(closure)
    recorded_closure_hash = closure_without_hash.pop("closure_sha256", None)
    calculated_closure_hash = sha256_bytes(compact_json_bytes(closure_without_hash))
    if recorded_closure_hash != calculated_closure_hash or manifest.get("source_closure_sha256") != calculated_closure_hash:
        raise ValueError("B40 source-closure descriptor hash drift")
    if interoperability.get("schema") != NATIVE_SCHEMA or interoperability.get("schema_version") != NATIVE_SCHEMA_VERSION:
        raise ValueError("B40 interoperability envelope drift")

    public_files = public.get("github", {}).get("native_backend_files", [])
    public_members = [
        {"path": str(row.get("path", "")).removeprefix("backend/"), "bytes": row.get("bytes"), "sha256": row.get("sha256")}
        for row in public_files
    ]
    if public_members != native_inputs or any(row.get("status") != 200 or not row.get("url") for row in public_files):
        raise ValueError("B40 public native-backend file closure drift")
    public_manifest = public.get("github", {}).get("native_backend_manifest", {})
    manifest_native_identity = identity(native_root / "manifest.json", display_path="manifest.json")
    manifest_input_identity = native_input_identity(native_root / "manifest.json", "manifest.json")
    if {
        "path": str(public_manifest.get("path", "")).removeprefix("backend/"),
        "bytes": public_manifest.get("bytes"),
        "sha256": public_manifest.get("sha256"),
    } != manifest_native_identity or public_manifest.get("status") != 200:
        raise ValueError("B40 public native manifest identity drift")
    expected_public_counts = {
        "native_records_total": EXPECTED_NATIVE_RECORDS,
        "entity_records_excluding_csv_relations": EXPECTED_ENTITY_RECORDS,
        "units": EXPECTED_UNITS,
        "segments": EXPECTED_SEGMENTS,
        "concepts": EXPECTED_CONCEPTS,
        "terms": EXPECTED_TERMS,
        "corrections": EXPECTED_CORRECTIONS,
        "relations": EXPECTED_RELATIONS,
        "relation_types": EXPECTED_RELATION_TYPES,
        "assets": EXPECTED_ASSETS,
        "rights": EXPECTED_RIGHTS,
        "artifacts": EXPECTED_ARTIFACTS,
        "qa_events": EXPECTED_QA_EVENTS,
        "exercises": EXPECTED_EXERCISES,
        "answers": EXPECTED_ANSWERS,
        "native_upstream_answers": EXPECTED_UPSTREAM_ANSWERS,
        "indonesian_edition_supplied_answers": EXPECTED_SUPPLIED_ANSWERS,
        "unanswered_exercises": 0,
        "source_files": EXPECTED_SOURCE_FILES,
    }
    if public.get("native_backend", {}).get("counts") != expected_public_counts:
        raise ValueError("B40 public/native record counts drift")
    reader = public.get("reader", {})
    release = public.get("github", {}).get("release", {})
    release_assets = release.get("assets", [])
    if (
        public.get("schema") != "b40-native-public-readback/1"
        or public.get("course_id") != COURSE_ID
        or public.get("native_role_id") != NATIVE_ROLE_ID
        or public.get("access_mode") != "anonymous_no_credentials"
        or public.get("native_backend", {}).get("source_closure_sha256") != calculated_closure_hash
        or public.get("native_backend", {}).get("interoperability_sha256") != identity(native_root / "interoperability.json")["sha256"]
        or public.get("github", {}).get("current_head") != "e84ce2956a7304830c42eba70106f940fefee7c4"
        or public.get("github", {}).get("current_tree") != "b434745225bb3931d51d107d8d8e5c0c8707af5d"
        or public.get("github", {}).get("repository_public") is not True
        or public.get("zenodo", {}).get("record_id") != 22070458
        or public.get("zenodo", {}).get("doi") != "10.5281/zenodo.22070458"
        or public.get("zenodo", {}).get("concept_record_id") != 22070457
        or public.get("zenodo", {}).get("concept_doi") != "10.5281/zenodo.22070457"
        or public.get("zenodo", {}).get("status") != "published"
        or public.get("zenodo", {}).get("access_right") != "open"
        or public.get("checks") != EXPECTED_PUBLIC_CHECKS
        or public.get("credentials_recorded") is not False
        or reader.get("url") != "https://kokunoyumeto.github.io/hefferon-linear-algebra-id/"
        or reader.get("status") != 200
        or reader.get("scope") != "release_landing_page_not_full_html_textbook"
        or not isinstance(reader.get("bytes"), int)
        or not isinstance(reader.get("sha256"), str)
        or len(reader.get("sha256", "")) != 64
        or release.get("tag") != "v2026.08.22"
        or not str(release.get("url", "")).startswith("https://")
        or len(release_assets) != 9
        or len({row.get("name") for row in release_assets}) != 9
        or any(not str(row.get("url", "")).startswith("https://") for row in release_assets)
    ):
        raise ValueError("B40 anonymous public-evidence envelope drift")

    migration_members = migration.get("source", {}).get("manifest_members", [])
    if migration_members != native_inputs:
        raise ValueError("B40 migration/native manifest member closure drift")
    if (
        migration.get("coverage", {}).get("native_record_count") != EXPECTED_NATIVE_RECORDS
        or migration.get("coverage", {}).get("exact_reverse_extraction") != EXPECTED_NATIVE_RECORDS
        or migration.get("transformation", {}).get("crosswalk_records") != EXPECTED_NATIVE_RECORDS
        or migration.get("transformation", {}).get("native_files_modified") != 0
        or migration.get("target", {}).get("record_count") != EXPECTED_NATIVE_RECORDS
        or migration.get("materialization", {}).get("virtual_records_materialized") is not False
        or migration.get("validation", {}).get("result") != "pass"
        or migration.get("validation", {}).get("deterministic_transform_runs") != 2
        or migration.get("validation", {}).get("deterministic_virtual_assembly_equal") is not True
    ):
        raise ValueError("B40 zero-copy common migration receipt drift")

    units = read_jsonl(native_root / "units.jsonl")
    concepts = read_jsonl(native_root / "concepts.jsonl")
    terms = read_jsonl(native_root / "terminology.jsonl")
    corrections = read_jsonl(native_root / "corrections.jsonl")
    rights = read_jsonl(native_root / "rights.jsonl")
    artifacts = read_jsonl(native_root / "artifacts.jsonl")
    relations = read_csv(native_root / "relations.csv")
    authority = read_jsonl(native_root / "authority.jsonl")
    course = read_jsonl(native_root / "courses.jsonl")[0]
    program = read_jsonl(native_root / "programs.jsonl")[0]

    units_by_id = {row["id"]: row for row in units}
    if len(units) != EXPECTED_UNITS or len(units_by_id) != EXPECTED_UNITS:
        raise ValueError("B40 unit identity inventory drift")
    unit_kinds = Counter(row.get("unit_kind") for row in units)
    if dict(sorted(unit_kinds.items())) != EXPECTED_UNIT_KINDS:
        raise ValueError("B40 unit-kind inventory drift")

    children: dict[str, list[dict[str, Any]]] = defaultdict(list)
    roots = []
    for row in units:
        parent = row.get("parent_id")
        if parent in units_by_id:
            children[parent].append(row)
        else:
            roots.append(row)
    for values in children.values():
        values.sort(key=lambda row: (row.get("order", 0), row["id"]))
    roots.sort(key=lambda row: (row.get("order", 0), row["id"]))
    expected_root_kinds = [kind for _, kind, _ in COMPONENTS]
    if [row.get("unit_kind") for row in roots] != expected_root_kinds:
        raise ValueError("B40 component root order drift")
    ordered_ids = _preorder([row["id"] for row in roots], children)
    if len(ordered_ids) != EXPECTED_UNITS or set(ordered_ids) != set(units_by_id):
        raise ValueError("B40 unit hierarchy does not close over every stable unit ID")
    ordinal_by_id = {unit_id: index for index, unit_id in enumerate(ordered_ids, start=1)}
    root_ids = {row["id"] for row in roots}

    relation_ids = [row.get("relation_id") for row in relations]
    relation_counts = Counter(row.get("relation_type") for row in relations)
    if (
        len(relations) != EXPECTED_RELATIONS
        or len(set(relation_ids)) != EXPECTED_RELATIONS
        or dict(sorted(relation_counts.items())) != EXPECTED_RELATION_TYPES
    ):
        raise ValueError("B40 relation inventory drift")
    all_native_ids = entity_ids | set(relation_ids)
    if len(all_native_ids) != EXPECTED_NATIVE_RECORDS:
        raise ValueError("B40 total native ID inventory drift")
    if any(row["source_id"] not in entity_ids or row["target_id"] not in entity_ids for row in relations):
        raise ValueError("B40 relation foreign-key closure drift")

    answer_relations = [row for row in relations if row["relation_type"] == "answers"]
    exercises = [row for row in units if row.get("unit_kind") == "exercise"]
    answers = [row for row in units if row.get("unit_kind") == "answer"]
    exercise_ids = {row["id"] for row in exercises}
    answer_ids = {row["id"] for row in answers}
    if (
        len(exercises) != EXPECTED_EXERCISES
        or len(answers) != EXPECTED_ANSWERS
        or {row["target_id"] for row in answer_relations} != exercise_ids
        or {row["source_id"] for row in answer_relations} != answer_ids
        or len({row["target_id"] for row in answer_relations}) != EXPECTED_EXERCISES
        or len({row["source_id"] for row in answer_relations}) != EXPECTED_ANSWERS
    ):
        raise ValueError("B40 exercise-answer relation is not an exact bijection")
    for relation in answer_relations:
        answer = units_by_id[relation["source_id"]]
        exercise = units_by_id[relation["target_id"]]
        if (
            answer.get("unit_kind") != "answer"
            or exercise.get("unit_kind") != "exercise"
            or answer.get("answers_unit_id") != exercise["id"]
            or answer.get("parent_id") != exercise["id"]
            or answer.get("exercise_environment_order") != exercise.get("exercise_environment_order")
            or answer.get("exercise_order") != exercise.get("exercise_order")
            or answer.get("path") != [*exercise.get("path", []), answer["id"]]
            or relation.get("order") != "1"
            or relation.get("schema") != NATIVE_SCHEMA
            or relation.get("schema_version") != NATIVE_SCHEMA_VERSION
            or relation.get("status") != "active"
        ):
            raise ValueError(f"B40 answer backpointer/path/order invariant drift: {answer['id']}")

    supplied_answers = sorted(
        [row for row in answers if row.get("provenance_kind") == "indonesian_edition_supplied"],
        key=lambda row: row["id"],
    )
    upstream_answers = [row for row in answers if row.get("native_kind") == "latex_answer_environment"]
    supplied_ids = {row["id"] for row in supplied_answers}
    upstream_ids = {row["id"] for row in upstream_answers}
    if (
        len(upstream_answers) != EXPECTED_UPSTREAM_ANSWERS
        or len(supplied_answers) != EXPECTED_SUPPLIED_ANSWERS
        or supplied_ids & upstream_ids
        or supplied_ids | upstream_ids != answer_ids
    ):
        raise ValueError("B40 answer provenance split drift")
    supplied_fields = (
        "id", "answers_unit_id", "provenance_kind", "authority_answer_status",
        "authorization_event_id", "authorization_correction_id", "authorization_ledger_locator",
        "authorization_ledger_sha256", "target_locator", "target_sha256",
    )
    supplied_public = sorted(public.get("native_backend", {}).get("target_supplied_answer_units", []), key=lambda row: row["unit_id"])
    supplied_native = []
    for row in supplied_answers:
        projected = _selected(row, supplied_fields)
        projected["unit_id"] = projected.pop("id")
        projected["exercise_unit_id"] = projected.pop("answers_unit_id")
        supplied_native.append(projected)
    if supplied_native != supplied_public:
        raise ValueError("B40 supplied-answer authorization provenance drift")

    route_node_ids = root_ids | {row["id"] for row in units if row.get("unit_kind") in {"chapter", "section"}}

    def nearest_route_node(unit_id: str) -> str:
        current = unit_id
        seen: set[str] = set()
        while current in units_by_id and current not in seen:
            seen.add(current)
            if current in route_node_ids:
                return current
            current = units_by_id[current].get("parent_id")
        raise ValueError(f"B40 unit has no component/chapter/section route ancestor: {unit_id}")

    unit_rows = []
    for unit_id in ordered_ids:
        row = units_by_id[unit_id]
        presentation_title_id, presentation_title_basis = _presentation_title(row)
        unit_rows.append({
            "unit_id": unit_id,
            "preorder": ordinal_by_id[unit_id],
            "kind": row.get("unit_kind"),
            "native_kind": row.get("native_kind"),
            "parent_id": row.get("parent_id"),
            "native_order": row.get("order"),
            "component_id": _component_id(row, root_ids),
            "route_node_id": nearest_route_node(unit_id),
            "source_file_unit_id": row.get("source_file_unit_id"),
            "source_local_id": row.get("source_local_id"),
            "source_title": row.get("source_title"),
            "title_id": row.get("target_title"),
            "native_title_id": row.get("target_title"),
            "presentation_title_id": presentation_title_id,
            "presentation_title_basis": presentation_title_basis,
            "source_locator": row.get("source_locator"),
            "source_sha256": row.get("source_sha256"),
            "target_locator": row.get("target_locator"),
            "target_sha256": row.get("target_sha256"),
            "language": row.get("language"),
            "locale": row.get("locale"),
            "target_language": row.get("target_language"),
            "target_locale": row.get("target_locale"),
            "rights_id": row.get("rights_id"),
            "concept_ids": row.get("concept_ids", []),
            "prerequisite_ids": row.get("prerequisite_ids", []),
            "prerequisite_status": row.get("prerequisite_status"),
            "translation_state": row.get("translation_state"),
            "answers_unit_id": row.get("answers_unit_id"),
            "exercise_environment_order": row.get("exercise_environment_order"),
            "exercise_order": row.get("exercise_order"),
            "segment_count": len(row.get("segment_ids", [])),
        })
    unit_row_by_id = {row["unit_id"]: row for row in unit_rows}

    answer_map = []
    for relation in sorted(answer_relations, key=lambda row: row["target_id"]):
        answer = units_by_id[relation["source_id"]]
        exercise = units_by_id[relation["target_id"]]
        provenance = (
            "indonesian_edition_supplied"
            if answer.get("provenance_kind") == "indonesian_edition_supplied"
            else "native_upstream_answer"
        )
        answer_map.append({
            "relation_id": relation["relation_id"],
            "relation_direction": "answer_to_exercise",
            "relation_order": int(relation["order"]),
            "exercise_unit_id": exercise["id"],
            "answer_unit_id": answer["id"],
            "provenance_class": provenance,
            "relation_source_locator": relation.get("source_locator"),
            "exercise_source_locator": exercise.get("source_locator"),
            "exercise_source_sha256": exercise.get("source_sha256"),
            "exercise_target_locator": exercise.get("target_locator"),
            "exercise_target_sha256": exercise.get("target_sha256"),
            "answer_source_locator": answer.get("source_locator"),
            "answer_source_sha256": answer.get("source_sha256"),
            "answer_target_locator": answer.get("target_locator"),
            "answer_target_sha256": answer.get("target_sha256"),
            "authority_answer_status": answer.get("authority_answer_status"),
            "authorization_event_id": answer.get("authorization_event_id"),
            "authorization_correction_id": answer.get("authorization_correction_id"),
            "authorization_ledger_locator": answer.get("authorization_ledger_locator"),
            "authorization_ledger_sha256": answer.get("authorization_ledger_sha256"),
            "answer_path_extends_exercise_path": True,
        })

    target_artifacts = [row for row in artifacts if row.get("artifact_kind") == "reader_pdf" and row.get("language") == "id"]
    if {
        (row["id"], row.get("bytes"), row.get("page_count"), row.get("sha256")) for row in artifacts
    } != EXPECTED_ARTIFACT_IDENTITIES:
        raise ValueError("B40 exact artifact identity/page inventory drift")
    release_assets = public.get("github", {}).get("release", {}).get("assets", [])
    release_by_sha = {row.get("sha256"): row for row in release_assets}
    artifact_fields = (
        "id", "artifact_kind", "corpus_component", "language", "locale", "source_locator",
        "source_url", "target_locator", "bytes", "page_count", "sha256",
        "build_status", "manifest_locator", "manifest_sha256", "translation_state", "rights_id",
    )
    artifact_rows = []
    for row in sorted(artifacts, key=lambda item: item["id"]):
        projected = _selected(row, artifact_fields)
        release = release_by_sha.get(row.get("sha256"))
        projected["native_publication_status"] = row.get("publication_status")
        projected["native_status_recorded_on"] = row.get("recorded_on")
        projected["current_public_status"] = (
            "verified_public_release_asset" if release else "not_matched_to_verified_release_asset"
        )
        projected["current_public_status_verified_on"] = public["verified_date"]
        projected["public_release"] = (
            _selected(release, ("name", "url", "bytes", "sha256", "pages")) if release else None
        )
        artifact_rows.append(projected)
    for row in target_artifacts:
        release = release_by_sha.get(row.get("sha256"))
        if not release or release.get("bytes") != row.get("bytes") or release.get("pages") != row.get("page_count"):
            raise ValueError(f"B40 target reader artifact/public release mismatch: {row['id']}")

    closure_roots_by_id = {row["work_unit_id"]: row for row in closure.get("roots", [])}
    closure_file_ids = {row.get("file_unit_id") for row in closure.get("files", [])}
    source_file_ids = {row["id"] for row in units if row.get("unit_kind") == "source_file"}
    if (
        len(closure_roots_by_id) != 3
        or len(closure.get("files", [])) != EXPECTED_SOURCE_FILES
        or closure_file_ids != source_file_ids
        or sum(row.get("file_count", 0) for row in closure.get("roots", [])) != 66
        or [row.get("file_count") for row in closure.get("roots", [])] != [51, 4, 11]
    ):
        raise ValueError("B40 source-closure root/file membership drift")
    component_rows = []
    artifact_by_component = {row.get("corpus_component"): row for row in artifact_rows if row.get("artifact_kind") == "reader_pdf" and row.get("language") == "id"}
    for component_name, kind, label in COMPONENTS:
        root = next(row for row in roots if row.get("unit_kind") == kind)
        member_rows = [row for row in unit_rows if row["component_id"] == root["id"]]
        chapters = []
        for chapter in sorted(
            [row for row in member_rows if row["kind"] == "chapter"],
            key=lambda row: (row.get("native_order") or 0, row["unit_id"]),
        ):
            section_rows = sorted(
                [row for row in member_rows if row["kind"] == "section" and row["parent_id"] == chapter["unit_id"]],
                key=lambda row: (row.get("native_order") or 0, row["unit_id"]),
            )
            chapters.append({
                "chapter_id": chapter["unit_id"],
                "native_order": chapter["native_order"],
                "title_id": chapter["title_id"],
                "native_title_id": chapter["native_title_id"],
                "presentation_title_id": chapter["presentation_title_id"],
                "presentation_title_basis": chapter["presentation_title_basis"],
                "source_title": chapter["source_title"],
                "source_locator": chapter["source_locator"],
                "source_sha256": chapter["source_sha256"],
                "target_locator": chapter["target_locator"],
                "target_sha256": chapter["target_sha256"],
                "sections": [{
                    "section_id": section["unit_id"],
                    "native_order": section["native_order"],
                    "title_id": section["title_id"],
                    "native_title_id": section["native_title_id"],
                    "presentation_title_id": section["presentation_title_id"],
                    "presentation_title_basis": section["presentation_title_basis"],
                    "source_title": section["source_title"],
                    "source_locator": section["source_locator"],
                    "source_sha256": section["source_sha256"],
                    "target_locator": section["target_locator"],
                    "target_sha256": section["target_sha256"],
                } for section in section_rows],
            })
        closure_root = closure_roots_by_id[root["id"]]
        component_rows.append({
            "component": component_name,
            "component_label_id": label,
            "component_id": root["id"],
            "kind": kind,
            "native_order": root.get("order"),
            "title_id": root.get("target_title"),
            "native_title_id": root.get("target_title"),
            "presentation_title_id": _presentation_title(root)[0],
            "presentation_title_basis": _presentation_title(root)[1],
            "source_title": root.get("source_title"),
            "source_locator": root.get("source_locator"),
            "source_sha256": root.get("source_sha256"),
            "target_locator": root.get("target_locator"),
            "target_sha256": root.get("target_sha256"),
            "source_entrypoint": closure_root["source_entrypoint"],
            "target_entrypoint": closure_root["target_entrypoint"],
            "closure_file_count": closure_root["file_count"],
            "unit_count": len(member_rows),
            "route_bucket_counts": {
                "component": sum(row["route_node_id"] == root["id"] for row in member_rows),
                "chapter": sum(units_by_id[row["route_node_id"]].get("unit_kind") == "chapter" for row in member_rows),
                "section": sum(units_by_id[row["route_node_id"]].get("unit_kind") == "section" for row in member_rows),
            },
            "unit_kind_counts": dict(sorted(Counter(row["kind"] for row in member_rows).items())),
            "chapter_count": len(chapters),
            "section_count": sum(len(chapter["sections"]) for chapter in chapters),
            "chapters": chapters,
            "reader_artifact": artifact_by_component[component_name],
        })

    term_by_id = {row["id"]: row for row in terms}
    concept_fields = (
        "id", "canonical_source_term", "source_local_id", "source_local_id_kind", "source_locator",
        "source_sha256", "target_term_ids", "prerequisite_ids", "prerequisite_status",
        "translation_state", "translation_state_status", "rights_id",
    )
    term_fields = (
        "id", "source_term", "preferred", "variants", "register", "scope", "source_local_id",
        "source_locator", "source_sha256", "source_ledger_row", "source_ledger_sha256",
        "ledger_status", "translation_state", "rights_id",
    )
    concept_rows = []
    for concept in sorted(concepts, key=lambda row: row["id"]):
        projected = _selected(concept, concept_fields)
        projected["concept_id"] = projected.pop("id")
        projected["target_terms"] = [
            _selected(term_by_id[term_id], term_fields) for term_id in concept.get("target_term_ids", [])
        ]
        concept_rows.append(projected)
    if len(concept_rows) != EXPECTED_CONCEPTS or len(term_by_id) != EXPECTED_TERMS:
        raise ValueError("B40 concept/term inventory drift")

    relation_rows = [{
        "relation_id": row["relation_id"],
        "relation_type": row["relation_type"],
        "source_id": row["source_id"],
        "target_id": row["target_id"],
        "order": int(row["order"]),
        "source_locator": row.get("source_locator"),
        "edition_id": row.get("edition_id"),
        "rights_id": row.get("rights_id"),
        "status": row.get("status"),
    } for row in sorted(relations, key=lambda item: item["relation_id"])]

    correction_fields = (
        "id", "source_local_id", "date", "scope", "severity", "disposition", "ledger_status",
        "translation_state", "translation_state_status", "upstream_report_disposition",
        "source_locator", "source_sha256", "source_ledger_row", "source_ledger_sha256",
        "affected_source_locators", "affected_unit_ids", "affected_unit_mapping_status", "rights_id",
    )
    correction_rows = [_selected(row, correction_fields) for row in sorted(corrections, key=lambda row: row["id"])]
    if len(correction_rows) != EXPECTED_CORRECTIONS:
        raise ValueError("B40 correction inventory drift")

    counts = {
        "native_backend_manifest_members": len(native_inputs),
        "entity_records_excluding_csv_relations": EXPECTED_ENTITY_RECORDS,
        "native_records_total": EXPECTED_NATIVE_RECORDS,
        "common_virtual_records": migration["target"]["record_count"],
        "common_crosswalk_records": migration["transformation"]["crosswalk_records"],
        "units": len(units),
        "segments": record_counts_by_file["segments.jsonl"],
        "components": len(component_rows),
        "chapters": unit_kinds["chapter"],
        "sections": unit_kinds["section"],
        "source_files": unit_kinds["source_file"],
        "exercises": len(exercises),
        "answers": len(answers),
        "native_upstream_answers": len(upstream_answers),
        "indonesian_edition_supplied_answers": len(supplied_answers),
        "unanswered_exercises": 0,
        "concepts": len(concepts),
        "terms": len(terms),
        "corrections": len(corrections),
        "relations": len(relations),
        "rights_components": len(rights),
        "artifacts": len(artifacts),
        "assets": record_counts_by_file["assets.jsonl"],
        "qa_events": record_counts_by_file["qa_events.jsonl"],
        "target_reader_pdfs": len(target_artifacts),
        "target_reader_pages": sum(row["page_count"] for row in target_artifacts),
        "github_native_backend_files_verified": len(public_files),
        "github_release_assets": len(release_assets),
        "github_release_assets_fully_hash_verified": len(public["github"]["release"]["fully_downloaded_and_sha256_verified"]),
        "zenodo_files": len(public["zenodo"]["files"]),
    }

    presentation_title_overrides = [{
        "unit_id": unit_id,
        **override,
        "target_locator": units_by_id[unit_id].get("target_locator"),
        "target_sha256": units_by_id[unit_id].get("target_sha256"),
    } for unit_id, override in sorted(PRESENTATION_TITLE_OVERRIDES.items())]

    learning_map = {
        "schema": "b40-learning-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "title": course.get("target_title"),
        "source_title": course.get("source_title"),
        "program_scope": program.get("program_scope"),
        "program_prerequisites": course.get("prerequisite_ids", []),
        "prerequisite_status": course.get("prerequisite_status"),
        "outcomes_available": False,
        "route": {
            "route_id": "B40:route:r005-complete",
            "component_ids": [row["component_id"] for row in component_rows],
            "all_unit_ids": ordered_ids,
        },
        "components": component_rows,
        "presentation_title_overrides": presentation_title_overrides,
        "public_reader_landing_page": _selected(
            public["reader"], ("url", "status", "bytes", "sha256", "scope")
        ),
        "limitations": [
            "Adapter memproyeksikan ID, struktur, pencari lokasi, hash, dan bukti publik tanpa menyalin segmen atau badan buku.",
            "Tiga komponen native adalah buku teks, buku jawaban, dan laboratorium Sage; artefak pembaca yang terbukti adalah PDF.",
            "Halaman web publik yang tercatat hanyalah halaman arahan rilis, bukan buku teks HTML.",
            "Backend native tidak menyatakan hasil belajar. Prasyarat juga tidak ditebak; status native dipertahankan apa adanya.",
            "Adapter tidak mengklaim EPUB, HTML semantik buku, PDF bertag, MathML, atau pemenuhan aksesibilitas.",
        ],
    }

    educator_map = {
        "schema": "b40-educator-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "selector": {
            "selection_unit": "exact_native_unit_id",
            "export_format": "application/json",
            "body_content_embedded": False,
            "answer_selector": {
                "input": "exact_exercise_unit_id",
                "relation_type": "answers",
                "relation_direction": "answer_to_exercise",
                "lookup": "unique relation where target_id equals the exact exercise unit ID; return source_id",
                "ordinal_only_lookup_allowed": False,
            },
            "units": unit_rows,
            "exercise_answers": answer_map,
        },
        "answer_provenance": {
            "native_upstream_answer_count": len(upstream_answers),
            "indonesian_edition_supplied_answer_count": len(supplied_answers),
            "target_supplied_answers": supplied_native,
            "classification_rule": "native_kind=latex_answer_environment versus provenance_kind=indonesian_edition_supplied",
        },
        "counts": counts,
        "claim_boundary": {
            "all_native_units_indexed": True,
            "every_exercise_has_exactly_one_answer": True,
            "answer_joins_inferred": False,
            "unit_outcomes_available": False,
            "unit_prerequisites_invented": False,
        },
        "limitations": [
            "Pemilih mengekspor metadata unit dan pasangan latihan-jawaban; isi soal dan jawaban tidak disalin.",
            "Setiap pasangan mengikuti tepat satu relasi answers native, dari unit jawaban menuju unit latihan.",
            "Dua jawaban edisi Indonesia tetap dibedakan dari 1.035 jawaban hulu dan membawa bukti otorisasi HLA-A0300.",
        ],
    }

    concept_index = {
        "schema": "b40-concept-index/1",
        "course_id": COURSE_ID,
        "concept_count": len(concept_rows),
        "term_count": len(terms),
        "concepts": concept_rows,
        "body_content_embedded": False,
        "omitted_native_body_fields": ["evidence", "examples", "notes"],
    }

    relation_index = {
        "schema": "b40-relation-index/1",
        "course_id": COURSE_ID,
        "relation_count": len(relation_rows),
        "relation_type_counts": dict(sorted(relation_counts.items())),
        "relations": relation_rows,
        "exercise_answer_projection_rows": len(answer_map),
        "specialized_projection_duplicate_rows_materialized": 0,
        "body_content_embedded": False,
    }

    ledger_references = {
        "schema": "b40-ledger-references/1",
        "course_id": COURSE_ID,
        "native_manifest": manifest_input_identity,
        "native_manifest_members": qualified_native_inputs,
        "native_manifest_inventory": _inventory_identity(qualified_native_inputs),
        "interoperability": {
            "identity": native_input_identity(native_root / "interoperability.json", "interoperability.json"),
            "schema": interoperability["schema"],
            "schema_version": interoperability["schema_version"],
            "exercise_answer_model": interoperability["exercise_answer_model"],
            "identity_contract": interoperability["identity_contract"],
        },
        "source_closure": {
            "identity": native_input_identity(native_root / "source_closure.json", "source_closure.json"),
            "descriptor_sha256": calculated_closure_hash,
            "file_records": len(closure["files"]),
            "asset_records": len(closure["assets"]),
            "ledger_records": closure["ledgers"],
            "roots": [{
                "component": row["component"],
                "work_unit_id": row["work_unit_id"],
                "file_count": row["file_count"],
                "source_entrypoint": row["source_entrypoint"],
                "target_entrypoint": row["target_entrypoint"],
            } for row in closure["roots"]],
        },
        "corrections": correction_rows,
        "migration_receipt": migration_input_identity,
        "common_projection": {
            "migration_id": migration["migration_id"],
            "migration_mode": migration["migration_mode"],
            "native_record_count": migration["coverage"]["native_record_count"],
            "entity_records_excluding_csv_relations": EXPECTED_ENTITY_RECORDS,
            "relation_records": EXPECTED_RELATIONS,
            "exact_reverse_extraction": migration["coverage"]["exact_reverse_extraction"],
            "crosswalk_records": migration["transformation"]["crosswalk_records"],
            "crosswalk_sha256": migration["transformation"]["crosswalk_sha256"],
            "virtual_records_jsonl_bytes": migration["target"]["virtual_records_jsonl_bytes"],
            "virtual_records_jsonl_sha256": migration["target"]["virtual_records_jsonl_sha256"],
            "native_files_modified": migration["transformation"]["native_files_modified"],
            "virtual_records_materialized": migration["materialization"]["virtual_records_materialized"],
            "deterministic_transform_runs": migration["validation"]["deterministic_transform_runs"],
            "deterministic_virtual_assembly_equal": migration["validation"]["deterministic_virtual_assembly_equal"],
        },
        "projection": {
            "native_bodies_copied": False,
            "native_ids_preserved": True,
            "all_manifest_hashes_replayed": True,
            "common_virtual_backend_materialized": False,
            "specialized_answer_projection_double_counted": False,
        },
    }

    public_evidence = _public_evidence_projection(public)
    public_evidence["native_artifacts"] = artifact_rows

    rights_and_terms = {
        "schema": "b40-rights-and-terms/1",
        "course_id": COURSE_ID,
        "component_rights": sorted(rights, key=lambda row: row["id"]),
        "rights_component_count": len(rights),
        "terminology_reference": {
            "canonical_adapter_path": "data/concept-index.json",
            "public_documentation_path": "docs/backend/b40/concept-index.json",
            "schema": "b40-concept-index/1",
            "term_count": len(terms),
        },
        "corrections_reference": {
            "canonical_adapter_path": "data/ledger-references.json",
            "public_documentation_path": "docs/backend/b40/ledger-references.json",
            "schema": "b40-ledger-references/1",
            "correction_count": len(corrections),
        },
        "redundant_terminology_rows_materialized": 0,
        "redundant_correction_rows_materialized": 0,
        "body_content_embedded": False,
        "blanket_license_claimed": False,
    }

    claim_boundary = {
        "schema": "b40-claim-boundary/1",
        "course_id": COURSE_ID,
        "learner_attempt_instances": 0,
        "learner_submission_instances": 0,
        "learner_result_instances": 0,
        "credential_assertion_instances": 0,
        "native_unit_outcomes_invented": False,
        "native_unit_prerequisites_invented": False,
        "exercise_answer_joins_inferred": False,
        "target_supplied_answers_retyped_as_upstream": False,
        "target_supplied_authorization_omitted": False,
        "native_semantic_html_claimed": False,
        "native_epub_claimed": False,
        "tagged_pdf_claimed": False,
        "mathml_claimed": False,
        "accessibility_conformance_claimed": False,
        "native_bodies_copied": False,
        "native_segments_copied": False,
        "blanket_license_claimed": False,
        "central_course_truth_rewritten": False,
        "historical_migration_receipt_rewritten": False,
        "common_virtual_backend_materialized": False,
        "public_state_changed": False,
    }

    capabilities = {
        "schema": "b40-capability-summary/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "native_family": "hefferon_modular_latex_backend",
        "counts": counts,
        "learner": {
            "ordered_component_navigation": True,
            "chapter_and_section_navigation": True,
            "all_native_unit_ids_in_route": True,
            "concept_term_index": True,
            "linked_native_reader_pdfs": 3,
            "release_landing_page": True,
            "full_native_html_textbook": False,
            "native_epub": False,
        },
        "educator": {
            "all_unit_selector": True,
            "exercise_answer_selector": True,
            "json_plan_export": True,
            "every_exercise_has_exactly_one_answer": True,
            "upstream_answer_rows": EXPECTED_UPSTREAM_ANSWERS,
            "indonesian_edition_supplied_answer_rows": EXPECTED_SUPPLIED_ANSWERS,
        },
        "reproducibility": {
            "all_native_manifest_members_hash_verified": True,
            "source_closure_descriptor_hash_verified": True,
            "interoperability_envelope_hash_verified": True,
            "exact_reverse_extraction_records": EXPECTED_NATIVE_RECORDS,
            "common_virtual_stream_materialized": False,
            "adapter_deterministic": True,
        },
        "rights": {"component_specific": True, "blanket_license_claimed": False},
        "claim_boundary": claim_boundary,
        "strict_contract_2_3_1_conformance_claimed": False,
    }

    source_lock = {
        "schema": "b40-source-lock/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "native_repository": {
            "url": public["github"]["repository"],
            "current_public_head": public["github"]["current_head"],
            "current_public_tree": public["github"]["current_tree"],
            "source_repository": next(row["official_repository"] for row in authority if row["record_type"] == "resource"),
            "source_commit": next(row["commit"] for row in authority if row.get("record_type") == "edition" and row.get("commit")),
            "source_tree": next(row["source_tree"] for row in authority if row.get("record_type") == "edition" and row.get("commit")),
        },
        "local_source_locator": LOCAL_SOURCE_LOCATOR,
        "input_path_root": "workspace_root",
        "manifest_input": manifest_input_identity,
        "native_inputs": qualified_native_inputs,
        "native_inventory": _inventory_identity(qualified_native_inputs),
        "source_closure_descriptor_sha256": calculated_closure_hash,
        "interoperability_input": native_input_identity(native_root / "interoperability.json", "interoperability.json"),
        "source_closure_input": native_input_identity(native_root / "source_closure.json", "source_closure.json"),
        "migration_input": migration_input_identity,
        "public_readback_input": public_input_identity,
    }

    final_manifest, final_native_inputs = _native_manifest(native_root)
    if final_manifest != manifest or final_native_inputs != native_inputs:
        raise ValueError("B40 native manifest changed while the projection was being derived")
    if public_path.read_bytes() != public_bytes or migration_path.read_bytes() != migration_bytes:
        raise ValueError("B40 receipt input changed while the projection was being derived")

    return {
        "source_lock": source_lock,
        "learning_map": learning_map,
        "educator_map": educator_map,
        "concept_index": concept_index,
        "relation_index": relation_index,
        "ledger_references": ledger_references,
        "public_evidence": public_evidence,
        "rights_and_terms": rights_and_terms,
        "claim_boundary": claim_boundary,
        "capabilities": capabilities,
    }


def projection_errors(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    learning = bundle.get("learning_map", {})
    educator = bundle.get("educator_map", {})
    concepts = bundle.get("concept_index", {})
    relations = bundle.get("relation_index", {})
    ledgers = bundle.get("ledger_references", {})
    public = bundle.get("public_evidence", {})
    rights = bundle.get("rights_and_terms", {})
    boundary = bundle.get("claim_boundary", {})
    source_lock = bundle.get("source_lock", {})
    capabilities = bundle.get("capabilities", {})
    counts = capabilities.get("counts", {})
    units = educator.get("selector", {}).get("units", [])
    answers = educator.get("selector", {}).get("exercise_answers", [])
    unit_ids = [row.get("unit_id") for row in units]

    forbidden_body_fields = {"text", "source_text", "target_text", "body", "body_text", "segment_text", "html_body", "epub_body", "raw_content"}

    def contains_body_field(value: Any) -> bool:
        if isinstance(value, dict):
            return any(key in forbidden_body_fields or contains_body_field(child) for key, child in value.items())
        if isinstance(value, list):
            return any(contains_body_field(child) for child in value)
        return False

    if contains_body_field(bundle):
        errors.append("B40-DATA-BODY-COPY")
    native_prefix = f"{LOCAL_SOURCE_LOCATOR}/"
    if (
        source_lock.get("input_path_root") != "workspace_root"
        or not str(source_lock.get("manifest_input", {}).get("path", "")).startswith(native_prefix)
        or any(not str(row.get("path", "")).startswith(native_prefix) for row in source_lock.get("native_inputs", []))
        or source_lock.get("migration_input", {}).get("path") != MIGRATION_RECEIPT_WORKSPACE
        or source_lock.get("public_readback_input", {}).get("path") != PUBLIC_READBACK_WORKSPACE
    ):
        errors.append("B40-SOURCE-ROOT")
    if (
        source_lock.get("schema") != "b40-source-lock/1"
        or source_lock.get("course_id") != COURSE_ID
        or source_lock.get("native_role_id") != NATIVE_ROLE_ID
        or source_lock.get("locale") != LOCALE
    ):
        errors.append("B40-SOURCE-LOCK-IDENTITY")
    if source_lock.get("native_repository") != EXPECTED_NATIVE_REPOSITORY:
        errors.append("B40-SOURCE-LOCK-REPOSITORY")

    unit_keys = {
        "unit_id", "preorder", "kind", "native_kind", "parent_id", "native_order",
        "component_id", "route_node_id", "source_file_unit_id", "source_local_id",
        "source_title", "title_id", "native_title_id", "presentation_title_id",
        "presentation_title_basis", "source_locator", "source_sha256", "target_locator",
        "target_sha256", "language", "locale", "target_language", "target_locale",
        "rights_id", "concept_ids", "prerequisite_ids", "prerequisite_status",
        "translation_state", "answers_unit_id", "exercise_environment_order",
        "exercise_order", "segment_count",
    }
    answer_keys = {
        "relation_id", "relation_direction", "relation_order", "exercise_unit_id",
        "answer_unit_id", "provenance_class", "relation_source_locator",
        "exercise_source_locator", "exercise_source_sha256", "exercise_target_locator",
        "exercise_target_sha256", "answer_source_locator", "answer_source_sha256",
        "answer_target_locator", "answer_target_sha256", "authority_answer_status",
        "authorization_event_id", "authorization_correction_id", "authorization_ledger_locator",
        "authorization_ledger_sha256", "answer_path_extends_exercise_path",
    }
    if any(not isinstance(row, dict) or set(row) != unit_keys for row in units):
        errors.append("B40-UNIT-ALLOWLIST")
    if any(not isinstance(row, dict) or set(row) != answer_keys for row in answers):
        errors.append("B40-ANSWER-ALLOWLIST")

    reader_keys = {"url", "status", "bytes", "sha256", "scope"}
    public_keys = {
        "schema", "course_id", "verified_date", "access_mode", "github", "zenodo",
        "reader", "checks", "credentials_recorded", "native_semantic_html_claimed",
        "native_epub_claimed", "tagged_pdf_claimed", "mathml_claimed",
        "accessibility_conformance_claimed", "public_state_changed", "native_artifacts",
    }
    github_keys = {
        "repository", "current_head", "current_tree", "repository_public",
        "current_commit_api", "native_backend_manifest", "native_backend_files",
        "supporting_raw_files", "release",
    }
    release_keys = {
        "tag", "url", "assets", "fully_downloaded_and_sha256_verified",
        "large_asset_anonymous_head_checks",
    }
    public_file_keys = {"path", "url", "status", "bytes", "sha256"}
    release_asset_keys = {"name", "bytes", "sha256", "pages", "url"}
    downloaded_asset_keys = {"name", "status", "bytes", "sha256"}
    head_asset_keys = {"name", "status", "final_url_host", "expected_bytes", "expected_sha256"}
    zenodo_keys = {"record_id", "doi", "concept_record_id", "concept_doi", "status", "access_right", "files"}
    zenodo_file_keys = {"name", "bytes", "checksum"}
    check_keys = {
        "exact_commit_and_tree", "native_backend_manifest_hash_closure",
        "immutable_native_files_fetched", "github_release_asset_inventory_exact",
        "full_release_artifacts_sha256_verified", "large_release_artifacts_anonymously_available",
        "zenodo_record_open_and_inventory_exact", "exercise_answer_bijection_verified",
        "target_supplied_answer_provenance_preserved", "reader_landing_page_fetched",
        "external_state_changed",
    }
    github = public.get("github", {})
    release = github.get("release", {})
    zenodo = public.get("zenodo", {})
    if (
        set(public) != public_keys
        or set(github) != github_keys
        or set(release) != release_keys
        or set(zenodo) != zenodo_keys
        or set(public.get("reader", {})) != reader_keys
        or set(public.get("checks", {})) != check_keys
        or set(github.get("current_commit_api", {})) != {"status", "bytes", "sha256"}
        or set(github.get("native_backend_manifest", {})) != public_file_keys
        or any(set(row) != public_file_keys for row in github.get("native_backend_files", []))
        or any(set(row) != public_file_keys for row in github.get("supporting_raw_files", []))
        or any(set(row) != release_asset_keys for row in release.get("assets", []))
        or any(set(row) != downloaded_asset_keys for row in release.get("fully_downloaded_and_sha256_verified", []))
        or any(set(row) != head_asset_keys for row in release.get("large_asset_anonymous_head_checks", []))
        or any(set(row) != zenodo_file_keys for row in zenodo.get("files", []))
        or set(learning.get("public_reader_landing_page", {})) != reader_keys
    ):
        errors.append("B40-PUBLIC-ALLOWLIST")

    if len(unit_ids) != EXPECTED_UNITS or len(set(unit_ids)) != EXPECTED_UNITS:
        errors.append("B40-UNIT-IDENTITY")
    if learning.get("route", {}).get("all_unit_ids") != unit_ids:
        errors.append("B40-UNIT-ORDER")
    components = learning.get("components", [])
    if (
        len(components) != 3
        or [row.get("component") for row in components] != [row[0] for row in COMPONENTS]
        or sum(row.get("chapter_count", 0) for row in components) != 17
        or sum(row.get("section_count", 0) for row in components) != 57
        or any(row.get("chapter_count") != len(row.get("chapters", [])) for row in components)
        or any(
            row.get("section_count")
            != sum(len(chapter.get("sections", [])) for chapter in row.get("chapters", []))
            for row in components
        )
    ):
        errors.append("B40-LEARNER-ROUTE")
    unit_map = {row.get("unit_id"): row for row in units}
    expected_title_overrides = [{
        "unit_id": unit_id,
        **override,
        "target_locator": unit_map.get(unit_id, {}).get("target_locator"),
        "target_sha256": unit_map.get(unit_id, {}).get("target_sha256"),
    } for unit_id, override in sorted(PRESENTATION_TITLE_OVERRIDES.items())]
    if learning.get("presentation_title_overrides") != expected_title_overrides:
        errors.append("B40-PRESENTATION-TITLES")
    for row in units:
        override = PRESENTATION_TITLE_OVERRIDES.get(row.get("unit_id"))
        expected_title = override["presentation_title_id"] if override else row.get("title_id")
        expected_basis = override["basis"] if override else "native_title"
        if (
            row.get("native_title_id") != row.get("title_id")
            or row.get("presentation_title_id") != expected_title
            or row.get("presentation_title_basis") != expected_basis
        ):
            errors.append("B40-PRESENTATION-TITLES")
            break
    for component in components:
        route_rows = [component, *component.get("chapters", [])]
        route_rows.extend(
            section
            for chapter in component.get("chapters", [])
            for section in chapter.get("sections", [])
        )
        for route_row in route_rows:
            route_id = route_row.get("component_id") or route_row.get("chapter_id") or route_row.get("section_id")
            unit = unit_map.get(route_id, {})
            if any(
                route_row.get(key) != unit.get(key)
                for key in ("title_id", "native_title_id", "presentation_title_id", "presentation_title_basis")
            ):
                errors.append("B40-PRESENTATION-TITLES")
                break
    route_node_ids = {
        row.get("component_id") for row in components
    } | {
        chapter.get("chapter_id")
        for component in components
        for chapter in component.get("chapters", [])
    } | {
        section.get("section_id")
        for component in components
        for chapter in component.get("chapters", [])
        for section in chapter.get("sections", [])
    }
    expected_buckets = {
        "main-textbook": {"component": 587, "chapter": 12, "section": 2617},
        "answer-book-shell": {"component": 3, "chapter": 1, "section": 0},
        "sage-lab": {"component": 13, "chapter": 9, "section": 299},
    }
    if any(row.get("route_node_id") not in route_node_ids for row in units):
        errors.append("B40-ROUTE-COVERAGE")
    if any(component.get("route_bucket_counts") != expected_buckets.get(component.get("component")) for component in components):
        errors.append("B40-ROUTE-COVERAGE")
    if learning.get("program_prerequisites") != [] or learning.get("prerequisite_status") != "not asserted without curriculum evidence":
        errors.append("B40-COURSE-PREREQUISITE")
    if learning.get("outcomes_available") is not False:
        errors.append("B40-COURSE-OUTCOME")

    exercise_ids = {row.get("unit_id") for row in units if row.get("kind") == "exercise"}
    answer_ids = {row.get("unit_id") for row in units if row.get("kind") == "answer"}
    if (
        len(answers) != EXPECTED_ANSWERS
        or len({row.get("relation_id") for row in answers}) != EXPECTED_ANSWERS
        or {row.get("exercise_unit_id") for row in answers} != exercise_ids
        or {row.get("answer_unit_id") for row in answers} != answer_ids
    ):
        errors.append("B40-ANSWER-BIJECTION")
    for row in answers:
        exercise = unit_map.get(row.get("exercise_unit_id"), {})
        answer = unit_map.get(row.get("answer_unit_id"), {})
        expected_provenance = (
            "native_upstream_answer"
            if answer.get("native_kind") == "latex_answer_environment"
            else "indonesian_edition_supplied"
        )
        if row.get("provenance_class") != expected_provenance:
            errors.append("B40-ANSWER-PROVENANCE")
        if row.get("relation_direction") != "answer_to_exercise" or row.get("relation_order") != 1:
            errors.append("B40-ANSWER-DIRECTION")
        if (
            answer.get("kind") != "answer"
            or exercise.get("kind") != "exercise"
            or answer.get("answers_unit_id") != exercise.get("unit_id")
            or answer.get("parent_id") != exercise.get("unit_id")
        ):
            errors.append("B40-ANSWER-BACKPOINTER")
        if (
            answer.get("exercise_environment_order") != exercise.get("exercise_environment_order")
            or answer.get("exercise_order") != exercise.get("exercise_order")
            or row.get("answer_path_extends_exercise_path") is not True
        ):
            errors.append("B40-ANSWER-ORDER-PATH")
        if (
            row.get("exercise_source_locator") != exercise.get("source_locator")
            or row.get("exercise_source_sha256") != exercise.get("source_sha256")
            or row.get("exercise_target_locator") != exercise.get("target_locator")
            or row.get("exercise_target_sha256") != exercise.get("target_sha256")
            or row.get("answer_source_locator") != answer.get("source_locator")
            or row.get("answer_source_sha256") != answer.get("source_sha256")
            or row.get("answer_target_locator") != answer.get("target_locator")
            or row.get("answer_target_sha256") != answer.get("target_sha256")
        ):
            errors.append("B40-ANSWER-LOCATOR-HASH")
    provenance = Counter(row.get("provenance_class") for row in answers)
    if provenance != Counter({"native_upstream_answer": EXPECTED_UPSTREAM_ANSWERS, "indonesian_edition_supplied": EXPECTED_SUPPLIED_ANSWERS}):
        errors.append("B40-ANSWER-PROVENANCE")
    supplied = [row for row in answers if row.get("provenance_class") == "indonesian_edition_supplied"]
    if any(
        row.get("authorization_event_id") != "HLA-A0300"
        or not row.get("authorization_correction_id")
        or not row.get("authorization_ledger_locator")
        or not row.get("authorization_ledger_sha256")
        or row.get("authority_answer_status") != "absent_from_pinned_source_and_official_answer_book"
        for row in supplied
    ):
        errors.append("B40-ANSWER-AUTHORIZATION")
    upstream = [row for row in answers if row.get("provenance_class") == "native_upstream_answer"]
    if any(
        row.get(key) is not None
        for row in upstream
        for key in (
            "authority_answer_status", "authorization_event_id", "authorization_correction_id",
            "authorization_ledger_locator", "authorization_ledger_sha256",
        )
    ):
        errors.append("B40-ANSWER-PROVENANCE")
    if educator.get("selector", {}).get("body_content_embedded") is not False:
        errors.append("B40-EDUCATOR-BODY-COPY")
    if educator.get("selector", {}).get("answer_selector") != {
        "input": "exact_exercise_unit_id",
        "relation_type": "answers",
        "relation_direction": "answer_to_exercise",
        "lookup": "unique relation where target_id equals the exact exercise unit ID; return source_id",
        "ordinal_only_lookup_allowed": False,
    }:
        errors.append("B40-ANSWER-ID-SELECTOR")

    if concepts.get("concept_count") != EXPECTED_CONCEPTS or len(concepts.get("concepts", [])) != EXPECTED_CONCEPTS:
        errors.append("B40-CONCEPTS")
    if concepts.get("term_count") != EXPECTED_TERMS or sum(len(row.get("target_terms", [])) for row in concepts.get("concepts", [])) != EXPECTED_TERMS:
        errors.append("B40-TERMS")
    relation_rows = relations.get("relations", [])
    if relations.get("relation_count") != EXPECTED_RELATIONS or len(relation_rows) != EXPECTED_RELATIONS or len({row.get("relation_id") for row in relation_rows}) != EXPECTED_RELATIONS:
        errors.append("B40-RELATIONS")
    projected_relation_counts = Counter(row.get("relation_type") for row in relation_rows)
    if (
        relations.get("relation_type_counts") != EXPECTED_RELATION_TYPES
        or dict(sorted(projected_relation_counts.items())) != EXPECTED_RELATION_TYPES
    ):
        errors.append("B40-RELATION-TYPES")
    if sha256_bytes(canonical_json_bytes(relation_rows)) != EXPECTED_RELATION_PROJECTION_SHA256:
        errors.append("B40-RELATION-PROJECTION")
    if relations.get("specialized_projection_duplicate_rows_materialized") != 0:
        errors.append("B40-PROJECTION-DOUBLE-COUNT")

    expected_counts = {
        "native_backend_manifest_members": 15,
        "entity_records_excluding_csv_relations": EXPECTED_ENTITY_RECORDS,
        "native_records_total": EXPECTED_NATIVE_RECORDS,
        "common_virtual_records": EXPECTED_NATIVE_RECORDS,
        "common_crosswalk_records": EXPECTED_NATIVE_RECORDS,
        "units": EXPECTED_UNITS,
        "segments": EXPECTED_SEGMENTS,
        "components": 3,
        "chapters": 17,
        "sections": 57,
        "source_files": EXPECTED_SOURCE_FILES,
        "exercises": EXPECTED_EXERCISES,
        "answers": EXPECTED_ANSWERS,
        "native_upstream_answers": EXPECTED_UPSTREAM_ANSWERS,
        "indonesian_edition_supplied_answers": EXPECTED_SUPPLIED_ANSWERS,
        "unanswered_exercises": 0,
        "concepts": EXPECTED_CONCEPTS,
        "terms": EXPECTED_TERMS,
        "corrections": EXPECTED_CORRECTIONS,
        "relations": EXPECTED_RELATIONS,
        "rights_components": EXPECTED_RIGHTS,
        "artifacts": EXPECTED_ARTIFACTS,
        "assets": EXPECTED_ASSETS,
        "qa_events": EXPECTED_QA_EVENTS,
        "target_reader_pdfs": 3,
        "target_reader_pages": 1124,
        "github_native_backend_files_verified": 15,
        "github_release_assets": 9,
        "github_release_assets_fully_hash_verified": 8,
        "zenodo_files": 9,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            errors.append(f"B40-COUNT-{key.upper()}")

    expected_capabilities = {
        "schema": "b40-capability-summary/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "native_family": "hefferon_modular_latex_backend",
        "counts": expected_counts,
        "learner": {
            "ordered_component_navigation": True,
            "chapter_and_section_navigation": True,
            "all_native_unit_ids_in_route": True,
            "concept_term_index": True,
            "linked_native_reader_pdfs": 3,
            "release_landing_page": True,
            "full_native_html_textbook": False,
            "native_epub": False,
        },
        "educator": {
            "all_unit_selector": True,
            "exercise_answer_selector": True,
            "json_plan_export": True,
            "every_exercise_has_exactly_one_answer": True,
            "upstream_answer_rows": EXPECTED_UPSTREAM_ANSWERS,
            "indonesian_edition_supplied_answer_rows": EXPECTED_SUPPLIED_ANSWERS,
        },
        "reproducibility": {
            "all_native_manifest_members_hash_verified": True,
            "source_closure_descriptor_hash_verified": True,
            "interoperability_envelope_hash_verified": True,
            "exact_reverse_extraction_records": EXPECTED_NATIVE_RECORDS,
            "common_virtual_stream_materialized": False,
            "adapter_deterministic": True,
        },
        "rights": {"component_specific": True, "blanket_license_claimed": False},
        "claim_boundary": boundary,
        "strict_contract_2_3_1_conformance_claimed": False,
    }
    if capabilities != expected_capabilities:
        errors.append("B40-CAPABILITIES")

    if len(rights.get("component_rights", [])) != EXPECTED_RIGHTS or rights.get("blanket_license_claimed") is not False:
        errors.append("B40-RIGHTS")
    if rights.get("terminology_reference") != {
        "canonical_adapter_path": "data/concept-index.json",
        "public_documentation_path": "docs/backend/b40/concept-index.json",
        "schema": "b40-concept-index/1",
        "term_count": EXPECTED_TERMS,
    } or rights.get("corrections_reference") != {
        "canonical_adapter_path": "data/ledger-references.json",
        "public_documentation_path": "docs/backend/b40/ledger-references.json",
        "schema": "b40-ledger-references/1",
        "correction_count": EXPECTED_CORRECTIONS,
    }:
        errors.append("B40-LEDGER-CLOSURE")
    if (
        "terminology" in rights
        or "corrections" in rights
        or rights.get("redundant_terminology_rows_materialized") != 0
        or rights.get("redundant_correction_rows_materialized") != 0
    ):
        errors.append("B40-PROJECTION-REDUNDANCY")
    common = ledgers.get("common_projection", {})
    if (
        common.get("native_record_count") != EXPECTED_NATIVE_RECORDS
        or common.get("entity_records_excluding_csv_relations") != EXPECTED_ENTITY_RECORDS
        or common.get("relation_records") != EXPECTED_RELATIONS
        or common.get("exact_reverse_extraction") != EXPECTED_NATIVE_RECORDS
        or common.get("crosswalk_records") != EXPECTED_NATIVE_RECORDS
        or common.get("crosswalk_sha256") != "0bf86d6ee55d4b906139df44cb4d4a50881aa0664f6e3a464479cebf2eb46a5a"
        or common.get("virtual_records_jsonl_bytes") != 83_914_129
        or common.get("virtual_records_jsonl_sha256") != "fa42e1d8adf3516afa9fa7c31cfe4144d1ff40e1d9e2230e139810a2b161c049"
        or common.get("native_files_modified") != 0
        or common.get("virtual_records_materialized") is not False
        or common.get("deterministic_transform_runs") != 2
        or common.get("deterministic_virtual_assembly_equal") is not True
    ):
        errors.append("B40-MIGRATION-ROUNDTRIP")

    if public.get("access_mode") != "anonymous_no_credentials" or public.get("public_state_changed") is not False:
        errors.append("B40-PUBLIC-ACCESS")
    if (
        public.get("github", {}).get("repository_public") is not True
        or public.get("github", {}).get("repository") != EXPECTED_NATIVE_REPOSITORY["url"]
        or public.get("github", {}).get("current_head") != EXPECTED_NATIVE_REPOSITORY["current_public_head"]
        or public.get("github", {}).get("current_tree") != EXPECTED_NATIVE_REPOSITORY["current_public_tree"]
    ):
        errors.append("B40-GITHUB-IDENTITY")
    if public.get("zenodo", {}).get("access_right") != "open" or len(public.get("zenodo", {}).get("files", [])) != 9:
        errors.append("B40-ZENODO-ACCESS")
    if public.get("reader", {}).get("scope") != "release_landing_page_not_full_html_textbook":
        errors.append("B40-READER-SCOPE")
    if (
        public.get("checks") != EXPECTED_PUBLIC_CHECKS
        or public.get("credentials_recorded") is not False
        or public.get("reader") != EXPECTED_PUBLIC_READER
        or learning.get("public_reader_landing_page") != EXPECTED_PUBLIC_READER
    ):
        errors.append("B40-PUBLIC-EVIDENCE")
    artifact_rows = public.get("native_artifacts", [])
    artifact_keys = {
        "id", "artifact_kind", "corpus_component", "language", "locale", "source_locator",
        "source_url", "target_locator", "bytes", "page_count", "sha256", "build_status",
        "manifest_locator", "manifest_sha256", "translation_state", "rights_id",
        "native_publication_status", "native_status_recorded_on", "current_public_status",
        "current_public_status_verified_on", "public_release",
    }
    artifact_identities = {
        (row.get("id"), row.get("bytes"), row.get("page_count"), row.get("sha256"))
        for row in artifact_rows
    }
    if (
        len(artifact_rows) != EXPECTED_ARTIFACTS
        or artifact_identities != EXPECTED_ARTIFACT_IDENTITIES
        or any(set(row) != artifact_keys for row in artifact_rows)
    ):
        errors.append("B40-ARTIFACTS")
    target_reader_rows = [row for row in artifact_rows if row.get("artifact_kind") == "reader_pdf" and row.get("language") == "id"]
    rights_ids = {row.get("id") for row in rights.get("component_rights", [])}
    if (
        len(target_reader_rows) != 3
        or sum(row.get("page_count", 0) for row in target_reader_rows) != 1124
        or any(not row.get("rights_id") or row.get("rights_id") not in rights_ids for row in artifact_rows)
        or any(
            not row.get("public_release")
            or row["public_release"].get("bytes") != row.get("bytes")
            or row["public_release"].get("sha256") != row.get("sha256")
            or row["public_release"].get("pages") != row.get("page_count")
            for row in target_reader_rows
        )
    ):
        errors.append("B40-ARTIFACTS")
    if any(
        not row.get("native_publication_status")
        or not row.get("native_status_recorded_on")
        or row.get("current_public_status_verified_on") != public.get("verified_date")
        or row.get("current_public_status")
        != ("verified_public_release_asset" if row.get("public_release") else "not_matched_to_verified_release_asset")
        or "publication_status" in row
        for row in artifact_rows
    ):
        errors.append("B40-ARTIFACT-STATUS")
    for key in ("native_semantic_html_claimed", "native_epub_claimed", "tagged_pdf_claimed", "mathml_claimed", "accessibility_conformance_claimed"):
        if public.get(key) is not False:
            errors.append("B40-FORMAT-OVERCLAIM")

    false_keys = (
        "native_unit_outcomes_invented", "native_unit_prerequisites_invented",
        "exercise_answer_joins_inferred", "target_supplied_answers_retyped_as_upstream",
        "target_supplied_authorization_omitted", "native_semantic_html_claimed",
        "native_epub_claimed", "tagged_pdf_claimed", "mathml_claimed",
        "accessibility_conformance_claimed", "native_bodies_copied", "native_segments_copied",
        "blanket_license_claimed", "central_course_truth_rewritten",
        "historical_migration_receipt_rewritten", "common_virtual_backend_materialized",
        "public_state_changed",
    )
    for key in false_keys:
        if boundary.get(key) is not False:
            errors.append(f"B40-BOUNDARY-{key.upper()}")
    for key in ("learner_attempt_instances", "learner_submission_instances", "learner_result_instances", "credential_assertion_instances"):
        if boundary.get(key) != 0:
            errors.append(f"B40-NONZERO-{key.upper()}")
    return sorted(set(errors))


def source_lock_errors(source_lock: dict[str, Any], native_root: Path, hub_root: Path) -> list[str]:
    errors: list[str] = []
    if (
        source_lock.get("schema") != "b40-source-lock/1"
        or source_lock.get("course_id") != COURSE_ID
        or source_lock.get("native_role_id") != NATIVE_ROLE_ID
        or source_lock.get("locale") != LOCALE
        or source_lock.get("input_path_root") != "workspace_root"
        or source_lock.get("local_source_locator") != LOCAL_SOURCE_LOCATOR
    ):
        errors.append("B40-SOURCE-LOCK-IDENTITY")
    if source_lock.get("native_repository") != EXPECTED_NATIVE_REPOSITORY:
        errors.append("B40-SOURCE-LOCK-REPOSITORY")
    manifest_path = native_root / "manifest.json"
    recorded_manifest = source_lock.get("manifest_input", {})
    if not manifest_path.is_file() or recorded_manifest != native_input_identity(manifest_path, "manifest.json"):
        errors.append("B40-SOURCE-HASH:manifest.json")
    manifest = read_json(manifest_path) if manifest_path.is_file() else {}
    recorded_inputs = source_lock.get("native_inputs", [])
    expected_inputs = [
        {**row, "path": f"{LOCAL_SOURCE_LOCATOR}/{row.get('path', '')}"}
        for row in manifest.get("files", [])
    ]
    if (
        manifest.get("generated_file_count") != 15
        or len(recorded_inputs) != 15
        or recorded_inputs != expected_inputs
        or source_lock.get("native_inventory") != _inventory_identity(expected_inputs)
    ):
        errors.append("B40-SOURCE-LOCK-MEMBERS")
    if len(recorded_inputs) == 15:
        for row in recorded_inputs:
            display = str(row.get("path", ""))
            prefix = f"{LOCAL_SOURCE_LOCATOR}/"
            relative = display.removeprefix(prefix)
            path = native_root / relative
            if (
                not display.startswith(prefix)
                or "/" in relative
                or not path.is_file()
                or path.is_symlink()
                or row != native_input_identity(path, relative)
            ):
                errors.append(f"B40-SOURCE-HASH:{Path(relative).name}")
    for key, relative, display, base in (
        ("migration_input", MIGRATION_RECEIPT, MIGRATION_RECEIPT_WORKSPACE, hub_root),
        ("public_readback_input", PUBLIC_READBACK, PUBLIC_READBACK_WORKSPACE, hub_root),
        ("interoperability_input", "interoperability.json", f"{LOCAL_SOURCE_LOCATOR}/interoperability.json", native_root),
        ("source_closure_input", "source_closure.json", f"{LOCAL_SOURCE_LOCATOR}/source_closure.json", native_root),
    ):
        row = source_lock.get(key, {})
        path = base / relative
        if not path.is_file() or path.is_symlink() or row != identity(path, display_path=display):
            errors.append(f"B40-SOURCE-HASH:{Path(relative).name}")
    closure_path = native_root / "source_closure.json"
    if closure_path.is_file():
        closure = read_json(closure_path)
        recorded = closure.pop("closure_sha256", None)
        calculated = sha256_bytes(compact_json_bytes(closure))
        if source_lock.get("source_closure_descriptor_sha256") != calculated or recorded != calculated:
            errors.append("B40-SOURCE-CLOSURE-DESCRIPTOR")
    return sorted(set(errors))
