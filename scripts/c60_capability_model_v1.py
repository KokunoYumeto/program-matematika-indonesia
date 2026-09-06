"""Deterministic zero-copy common-capability projection for C60/R014."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import uuid
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable


COURSE_ID = "C60"
NATIVE_ROLE_ID = "R014"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"
REPOSITORY = "https://github.com/KokunoYumeto/yet-another-introductory-number-theory-textbook-id"
PAGES_URL = "https://kokunoyumeto.github.io/yet-another-introductory-number-theory-textbook-id/"
CURRENT_PUBLIC_HEAD = "66df945d1e5281bfc4758b733c13ac9254f00410"
CURRENT_PUBLIC_TREE = "5132900227e1b1a06cdc3facac691e18a7bdb10f"
NATIVE_RELEASE_COMMIT = "11e27180632af3b90202ad38c063807c0d057766"
BACKEND_TREE = "a5a8a7a3e010e6372c2c22051d1f922327f2f763"
SOURCE_TREE = "5d0949f7917967079b11288180646ea83c0e0b1b"
DOCS_TREE = "db6215012c8ff4b00a55668bbe7860fd57717e91"
RELEASE_VERSION = "1.0.0"
ZENODO_RECORD_ID = 22052196
MIGRATION_RECEIPT = "backend/migrations/yaintt-id-v1/MIGRATION_RECEIPT.json"
ROOT_UNIT_ID = "ttp.r014.unit.book"
FINAL_EDITION_ID = "ttp.r014.edition.id-id.boundary28-final"
NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")

EXPECTED_NATIVE_COUNTS = {
    "artifact": 105,
    "asset": 14,
    "concept": 223,
    "correction": 141,
    "course": 1,
    "edition": 12,
    "program": 1,
    "qa_event": 131,
    "relation": 3297,
    "resource": 1,
    "rights": 15,
    "segment": 544,
    "term": 239,
    "unit": 548,
}

EXPECTED_RELATIONS = {
    "adapts": 11,
    "cites": 4,
    "contains": 874,
    "corrects": 149,
    "covers": 882,
    "depends_on": 138,
    "exercises": 398,
    "illustrates": 56,
    "precedes": 406,
    "prerequisite_for": 192,
    "proves": 54,
    "references": 109,
    "source_uses_asset": 1,
    "supersedes": 6,
    "translates": 15,
    "uses_asset": 2,
}

DIRECT_TYPES = {
    "program": "program",
    "course": "course",
    "resource": "resource",
    "rights": "rights",
    "edition": "edition",
    "unit": "unit",
    "segment": "segment",
    "concept": "concept",
    "term": "term",
    "correction": "correction",
    "relation": "relation",
    "qa_event": "qa_event",
    "asset": "asset",
    "artifact": "artifact",
}

REFERENCE_FIELDS = {
    "program": ["course_ids"],
    "course": ["resource_id", "resource_ids"],
    "resource": ["rights_id"],
    "edition": ["resource_id", "rights_id", "source_edition_id", "supersedes", "file_ids"],
    "unit": ["parent_unit_id", "edition_id", "rights_id", "qa_event_ids"],
    "segment": ["unit_id", "edition_id", "rights_id", "qa_event_ids"],
    "concept": ["prerequisite_concept_ids"],
    "term": ["concept_id"],
    "correction": ["affected_unit_ids"],
    "relation": ["subject_id", "object_id", "edition_id"],
    "qa_event": ["edition_id", "witness_ids"],
    "asset": ["edition_id", "resource_id", "rights_id", "dependency_ids"],
    "artifact": ["edition_id", "resource_id", "build_receipt_id"],
}

CONTROL_INPUTS = (
    "qa/BACKEND_QA.json",
    "qa/BACKEND_DETERMINISM.json",
    "docs/HTML_READER_MANIFEST.json",
    "qa/HTML_READER_QA.json",
    "publication/RELEASE_MANIFEST.json",
    "qa/INDONESIAN_TERMINOLOGY_QA.json",
    "authority/SOURCE_AUTHORITY.json",
    "authority/COMPONENT_RIGHTS.json",
    "LICENSE.md",
    "ATTRIBUTION.md",
    "README.md",
    "source/yaintt-id.tex",
)


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


def identity_bytes(data: bytes, *, path: str, revision: str) -> dict[str, Any]:
    return {"path": path, "revision": revision, "bytes": len(data), "sha256": sha256_bytes(data)}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _git(native_root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(native_root), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise ValueError(f"C60 git evidence lookup failed: {' '.join(args)}: {result.stderr.decode('utf-8', 'replace').strip()}")
    return result.stdout


def git_text(native_root: Path, *args: str) -> str:
    return _git(native_root, *args).decode("utf-8").strip()


def git_bytes(native_root: Path, revision: str, path: str) -> bytes:
    return _git(native_root, "show", f"{revision}:{path}")


def git_json(native_root: Path, revision: str, path: str) -> Any:
    return json.loads(git_bytes(native_root, revision, path).decode("utf-8"))


def git_identity(native_root: Path, revision: str, path: str, *, label: str) -> dict[str, Any]:
    return identity_bytes(git_bytes(native_root, revision, path), path=path, revision=label)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _record_hash(record: dict[str, Any]) -> str:
    return sha256_bytes(compact_json_bytes(record))


def _inventory_identity(rows: Iterable[dict[str, Any]], keys: tuple[str, ...]) -> dict[str, Any]:
    payload = b"".join(
        ("\t".join(str(row[key]) for key in keys) + "\n").encode("utf-8")
        for row in rows
    )
    return {"bytes": len(payload), "sha256": sha256_bytes(payload)}


def _parse_native_records(data: bytes) -> list[dict[str, Any]]:
    lines = data.splitlines(keepends=True)
    records: list[dict[str, Any]] = []
    for number, line in enumerate(lines, start=1):
        if not line.endswith(b"\n") or line.endswith(b"\r\n"):
            raise ValueError(f"C60 native JSONL is not canonical LF at line {number}")
        record = json.loads(line)
        if line != compact_json_bytes(record) + b"\n":
            raise ValueError(f"C60 native JSONL canonicalization drift at line {number}")
        records.append(record)
    return records


def _common_native_id(native: dict[str, Any]) -> str:
    record_type = DIRECT_TYPES[native["entity_class"]]
    stable_key = f"{record_type}|yaintt:{native['record_id']}"
    return f"urn:uuid:{uuid.uuid5(NAMESPACE, stable_key)}"


def _verify_native_backend(native_root: Path) -> dict[str, Any]:
    head = git_text(native_root, "rev-parse", "HEAD")
    tree = git_text(native_root, "show", "-s", "--format=%T", CURRENT_PUBLIC_HEAD)
    backend_tree = git_text(native_root, "rev-parse", f"{CURRENT_PUBLIC_HEAD}:backend")
    release_backend_tree = git_text(native_root, "rev-parse", f"{NATIVE_RELEASE_COMMIT}:backend")
    source_tree = git_text(native_root, "rev-parse", f"{CURRENT_PUBLIC_HEAD}:source")
    release_source_tree = git_text(native_root, "rev-parse", f"{NATIVE_RELEASE_COMMIT}:source")
    docs_tree = git_text(native_root, "rev-parse", f"{CURRENT_PUBLIC_HEAD}:docs")
    if (head, tree, backend_tree, release_backend_tree, source_tree, release_source_tree, docs_tree) != (
        CURRENT_PUBLIC_HEAD,
        CURRENT_PUBLIC_TREE,
        BACKEND_TREE,
        BACKEND_TREE,
        SOURCE_TREE,
        SOURCE_TREE,
        DOCS_TREE,
    ):
        raise ValueError("C60 public clone commit or subtree identity drift")

    manifest_data = git_bytes(native_root, CURRENT_PUBLIC_HEAD, "backend/MANIFEST.json")
    checksum_data = git_bytes(native_root, CURRENT_PUBLIC_HEAD, "backend/MANIFEST.sha256")
    manifest = json.loads(manifest_data)
    if checksum_data.decode("utf-8").strip().split()[0] != sha256_bytes(manifest_data):
        raise ValueError("C60 MANIFEST.sha256 does not bind MANIFEST.json")
    if manifest.get("record_counts") != EXPECTED_NATIVE_COUNTS or len(manifest.get("files", [])) != 33:
        raise ValueError("C60 native manifest inventory drift")

    backend_inputs = [
        identity_bytes(manifest_data, path="backend/MANIFEST.json", revision="public-main"),
        identity_bytes(checksum_data, path="backend/MANIFEST.sha256", revision="public-main"),
    ]
    for item in manifest["files"]:
        path = f"backend/{item['path']}"
        data = git_bytes(native_root, CURRENT_PUBLIC_HEAD, path)
        if len(data) != item["bytes"] or sha256_bytes(data) != item["sha256"]:
            raise ValueError(f"C60 native manifest member drift: {path}")
        backend_inputs.append(identity_bytes(data, path=path, revision="public-main"))

    records_data = git_bytes(native_root, CURRENT_PUBLIC_HEAD, "backend/records.jsonl")
    records = _parse_native_records(records_data)
    counts = Counter(row["entity_class"] for row in records)
    native_ids = [row["record_id"] for row in records]
    if len(records) != 5272 or len(set(native_ids)) != 5272 or dict(sorted(counts.items())) != EXPECTED_NATIVE_COUNTS:
        raise ValueError("C60 native record identity or class count drift")
    if any(row.get("schema") != "r014.backend.record" or row.get("schema_version") != "1.0.0" for row in records):
        raise ValueError("C60 native record schema header drift")

    known = set(native_ids)
    missing: list[tuple[str, str, str]] = []
    for row in records:
        for field in REFERENCE_FIELDS.get(row["entity_class"], []):
            for value in _as_list(row.get(field)):
                if value not in known:
                    missing.append((row["record_id"], field, value))
    if missing:
        raise ValueError(f"C60 native foreign-key closure drift: {missing[:3]}")

    catalog = git_json(native_root, CURRENT_PUBLIC_HEAD, "backend/catalog.json")
    if catalog.get("records") != records or catalog.get("record_counts") != EXPECTED_NATIVE_COUNTS:
        raise ValueError("C60 catalog/JSONL semantic equivalence drift")
    for row in records:
        if row["entity_class"] == "segment":
            for expression in row["expressions"]:
                if sha256_bytes(expression["text_latex"].encode("utf-8")) != expression["content_sha256"]:
                    raise ValueError(f"C60 segment expression hash drift: {expression['expression_id']}")

    mapping_rows = [
        {"native_id": row["record_id"], "common_id": _common_native_id(row)}
        for row in sorted(records, key=lambda item: item["record_id"])
    ]
    mapping_identity = _inventory_identity(mapping_rows, ("native_id", "common_id"))
    return {
        "records": records,
        "manifest": manifest,
        "backend_inputs": backend_inputs,
        "mapping_identity": mapping_identity,
        "commit_evidence": {
            "current_public_head": head,
            "current_public_tree": tree,
            "native_release_commit": NATIVE_RELEASE_COMMIT,
            "current_backend_tree": backend_tree,
            "release_backend_tree": release_backend_tree,
            "current_source_tree": source_tree,
            "release_source_tree": release_source_tree,
            "current_docs_tree": docs_tree,
            "native_backend_unchanged_from_release_commit": backend_tree == release_backend_tree,
            "native_source_unchanged_from_release_commit": source_tree == release_source_tree,
        },
    }


class _IdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key == "id" and value:
                self.ids.append(value)


def _flatten_sitemap(node: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [node["section"]]
    for child in node.get("subsections", []):
        rows.extend(_flatten_sitemap(child))
    return rows


def _reader_evidence(native_root: Path) -> dict[str, Any]:
    manifest = git_json(native_root, CURRENT_PUBLIC_HEAD, "docs/HTML_READER_MANIFEST.json")
    qa = git_json(native_root, CURRENT_PUBLIC_HEAD, "qa/HTML_READER_QA.json")
    chapters = git_json(native_root, CURRENT_PUBLIC_HEAD, "docs/reader/chapters.json")
    sitemap = git_json(native_root, CURRENT_PUBLIC_HEAD, "docs/reader/sitemap.json")
    if manifest.get("status") != "complete" or qa.get("status") != "passed":
        raise ValueError("C60 public reflowable reader is not complete and passed")
    if manifest.get("build", {}).get("chapters") != 5 or len(chapters) != 5:
        raise ValueError("C60 public reader chapter count drift")
    if qa.get("metrics", {}).get("missing_files") != 0 or qa.get("metrics", {}).get("missing_anchors") != 0:
        raise ValueError("C60 public reader link closure drift")

    reader_inputs: list[dict[str, Any]] = []
    anchor_pages: dict[str, list[str]] = defaultdict(list)
    for item in manifest["files"]:
        data = git_bytes(native_root, CURRENT_PUBLIC_HEAD, item["path"])
        if len(data) != item["bytes"] or sha256_bytes(data) != item["sha256"]:
            raise ValueError(f"C60 reader manifest member drift: {item['path']}")
        reader_inputs.append(identity_bytes(data, path=item["path"], revision="public-main"))
        if item["path"].startswith("docs/reader/") and item["path"].endswith(".html"):
            parser = _IdParser()
            parser.feed(data.decode("utf-8"))
            page = item["path"].removeprefix("docs/")
            for anchor in parser.ids:
                anchor_pages[anchor].append(page)
    sitemap_rows = _flatten_sitemap(sitemap)
    section_count = sum(row.get("level") == "2" for row in sitemap_rows)
    if section_count != 27:
        raise ValueError("C60 public reader section count drift")
    return {
        "manifest": manifest,
        "qa": qa,
        "chapters": chapters,
        "sitemap": sitemap,
        "sitemap_rows": sitemap_rows,
        "reader_inputs": reader_inputs,
        "anchor_pages": dict(anchor_pages),
        "section_count": section_count,
    }


def _anchor_id(source_local_id: str | None) -> str | None:
    if not source_local_id or source_local_id.startswith("generated:"):
        return None
    return re.sub(r"[:\s]+", "-", source_local_id)


def derive_projection(native_root: Path, hub_root: Path) -> dict[str, Any]:
    backend = _verify_native_backend(native_root)
    reader = _reader_evidence(native_root)
    migration_path = hub_root / MIGRATION_RECEIPT
    if not migration_path.is_file():
        raise FileNotFoundError(f"Missing C60 migration receipt: {migration_path}")
    migration_input = identity(migration_path, display_path=MIGRATION_RECEIPT)
    migration = read_json(migration_path)

    records = backend["records"]
    by_id = {row["record_id"]: row for row in records}
    by_class: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_class[row["entity_class"]].append(row)
    course = by_class["course"][0]
    resource = by_class["resource"][0]
    units = by_class["unit"]
    concepts = by_class["concept"]
    relations = by_class["relation"]
    terms = by_class["term"]
    corrections = by_class["correction"]
    rights = by_class["rights"]

    receipt_checks = {
        "schema": migration.get("schema_name") == "interlanguage-math-modular-backend-migration-receipt",
        "migration_id": migration.get("migration_id") == "yaintt-r014-id-to-interlanguage-v1.0.0",
        "migration_mode": migration.get("migration_mode") == "lossless-zero-copy-additive-native-backend-adapter",
        "manifest_identity": migration.get("source", {}).get("manifest_sha256") == backend["backend_inputs"][0]["sha256"],
        "records_identity": migration.get("source", {}).get("records_sha256") == next(row["sha256"] for row in backend["backend_inputs"] if row["path"] == "backend/records.jsonl"),
        "catalog_identity": migration.get("source", {}).get("catalog_sha256") == next(row["sha256"] for row in backend["backend_inputs"] if row["path"] == "backend/catalog.json"),
        "native_count": migration.get("source", {}).get("record_count") == 5272,
        "native_class_counts": migration.get("coverage", {}).get("native_record_counts") == EXPECTED_NATIVE_COUNTS,
        "native_unique_ids": migration.get("coverage", {}).get("native_unique_ids") == 5272,
        "exact_reverse_extraction": migration.get("validation", {}).get("exact_native_reverse_extraction") == 5272,
        "mapping_bytes": migration.get("coverage", {}).get("native_id_mapping_bytes") == backend["mapping_identity"]["bytes"],
        "mapping_sha256": migration.get("coverage", {}).get("native_id_mapping_sha256") == backend["mapping_identity"]["sha256"],
        "common_count": migration.get("target", {}).get("record_count") == 6967,
        "common_table_sum": sum(row.get("records", 0) for row in migration.get("tables", {}).values()) == 6967,
        "two_common_assemblies": migration.get("validation", {}).get("first_canonical_backend_sha256") == migration.get("validation", {}).get("second_canonical_backend_sha256") == migration.get("target", {}).get("canonical_backend_sha256"),
        "native_files_modified_zero": migration.get("transformation", {}).get("native_files_modified") == 0,
        "native_records_modified_zero": migration.get("transformation", {}).get("native_records_modified") == 0,
        "all_payload_fields_preserved": migration.get("transformation", {}).get("native_payload_fields_preserved") == "all fields of all 5,272 native records",
    }
    if not all(receipt_checks.values()):
        raise ValueError(f"C60 migration receipt replay failed: {[key for key, value in receipt_checks.items() if not value]}")

    control_inputs = [git_identity(native_root, CURRENT_PUBLIC_HEAD, path, label="public-main") for path in CONTROL_INPUTS]
    source_inputs = [*backend["backend_inputs"], *control_inputs, *reader["reader_inputs"], migration_input]

    native_id_rows = [
        {
            "native_id": row["record_id"],
            "entity_class": row["entity_class"],
            "native_object_sha256": _record_hash(row),
        }
        for row in sorted(records, key=lambda item: item["record_id"])
    ]
    native_id_inventory = _inventory_identity(native_id_rows, ("native_id", "entity_class", "native_object_sha256"))
    native_id_index = {
        "schema": "c60-native-id-index/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "record_count": len(native_id_rows),
        "class_counts": dict(sorted(Counter(row["entity_class"] for row in native_id_rows).items())),
        "inventory": native_id_inventory,
        "records": native_id_rows,
        "native_payloads_embedded": False,
    }

    units_by_id = {row["record_id"]: row for row in units}
    children: dict[str, list[dict[str, Any]]] = defaultdict(list)
    roots: list[dict[str, Any]] = []
    for unit in units:
        parent = unit.get("parent_unit_id")
        if parent is None:
            roots.append(unit)
        elif parent in units_by_id:
            children[parent].append(unit)
        else:
            raise ValueError(f"C60 unit parent is missing: {unit['record_id']}")
    for values in children.values():
        values.sort(key=lambda row: (str(row.get("order_key") or ""), int(row.get("order") or 0), row["record_id"]))
    if [row["record_id"] for row in roots] != [ROOT_UNIT_ID]:
        raise ValueError("C60 native unit root drift")

    order: list[str] = []
    def visit(unit_id: str) -> None:
        order.append(unit_id)
        for child in children.get(unit_id, []):
            visit(child["record_id"])
    visit(ROOT_UNIT_ID)
    if len(order) != 548 or set(order) != set(units_by_id):
        raise ValueError("C60 native unit hierarchy does not close")
    ordinal = {unit_id: index for index, unit_id in enumerate(order, start=1)}

    parent_edges = {(row["parent_unit_id"], row["record_id"]) for row in units if row.get("parent_unit_id")}
    contains_edges = {(row["subject_id"], row["object_id"]) for row in relations if row["predicate"] == "contains" and row["subject_id"] in units_by_id and row["object_id"] in units_by_id}
    if parent_edges != contains_edges or len(parent_edges) != 547:
        raise ValueError("C60 unit hierarchy/contains relation mismatch")

    superseded_by = {row["supersedes"]: row["record_id"] for row in units if row.get("supersedes")}
    effective_ids = set(units_by_id) - set(superseded_by)
    if len(superseded_by) != 4 or len(effective_ids) != 544:
        raise ValueError("C60 native supersession inventory drift")

    anchor_pages = reader["anchor_pages"]
    direct_url: dict[str, str] = {}
    direct_route_basis: dict[str, str] = {}
    for unit in units:
        anchor = _anchor_id(unit.get("source_local_id"))
        pages = anchor_pages.get(anchor or "", [])
        if pages:
            direct_url[unit["record_id"]] = f"{PAGES_URL}{sorted(pages)[0]}#{anchor}"
            direct_route_basis[unit["record_id"]] = "source_label"

    sitemap_rows_by_id = {row["id"]: row for row in reader["sitemap_rows"] if row.get("id")}
    sitemap_children_by_id: dict[str, list[dict[str, Any]]] = {}
    def index_sitemap_children(node: dict[str, Any]) -> None:
        section_id = node["section"].get("id")
        if section_id:
            sitemap_children_by_id[section_id] = [child["section"] for child in node.get("subsections", [])]
        for child in node.get("subsections", []):
            index_sitemap_children(child)
    index_sitemap_children(reader["sitemap"])
    structural_ids = {
        ROOT_UNIT_ID: f"{PAGES_URL}reader/index.html",
        "ttp.r014.unit.frontmatter.preface": f"{PAGES_URL}reader/-prakata.html#prakata",
        "ttp.r014.unit.frontmatter.release-notes": f"{PAGES_URL}reader/-catatan-rilis.html#catatan-rilis",
        "ttp.r014.unit.backmatter.index": f"{PAGES_URL}reader/-indeks-web.html#indeks-web",
        "ttp.r014.unit.backmatter.bibliography": f"{PAGES_URL}reader/-bibliography.html#bibliography",
    }
    for unit in units:
        if unit["unit_type"] == "subsection" and unit["record_id"] not in direct_url:
            candidates = [row for row in reader["sitemap_rows"] if row.get("level") == "3" and row.get("title") == unit.get("title_id")]
            if len(candidates) == 1:
                structural_ids[unit["record_id"]] = f"{PAGES_URL}reader/{candidates[0]['path']}"
        elif unit["unit_type"] == "exercise_group" and unit["record_id"] not in direct_url:
            parent = units_by_id[unit["parent_unit_id"]]
            parent_anchor = _anchor_id(parent.get("source_local_id"))
            if sitemap_rows_by_id.get(parent_anchor or ""):
                candidates = [row for row in sitemap_children_by_id.get(parent_anchor or "", []) if row.get("level") == "3" and row.get("title", "").startswith("Latihan untuk")]
                if len(candidates) == 1:
                    structural_ids[unit["record_id"]] = f"{PAGES_URL}reader/{candidates[0]['path']}"
        elif unit["unit_type"] == "bibliography_entry" and unit["record_id"] not in direct_url:
            anchor = f"ref-{unit.get('source_local_id')}"
            pages = anchor_pages.get(anchor, [])
            if pages:
                structural_ids[unit["record_id"]] = f"{PAGES_URL}{sorted(pages)[0]}#{anchor}"
    if len(structural_ids) != 38:
        raise ValueError(f"C60 structural reader route inventory drift: {len(structural_ids)}")
    for unit_id, url in structural_ids.items():
        direct_url[unit_id] = url
        direct_route_basis[unit_id] = "reader_structure_or_bibliography"
    if len(direct_url) != 187 or len(set(direct_url.values())) != 183:
        raise ValueError(f"C60 exact native-unit reader route inventory drift: {len(direct_url)} records/{len(set(direct_url.values()))} routes")

    def context_url(unit_id: str) -> tuple[str, str]:
        current: str | None = unit_id
        while current:
            if current in direct_url:
                return direct_url[current], "exact_anchor" if current == unit_id else "ancestor_anchor"
            current = units_by_id[current].get("parent_unit_id")
        return f"{PAGES_URL}reader/index.html", "reader_root"

    concept_ids_by_unit: dict[str, set[str]] = defaultdict(set)
    coverage_relation_ids_by_unit: dict[str, list[str]] = defaultdict(list)
    concept_unit_relations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for relation in relations:
        if relation["predicate"] in {"covers", "exercises", "illustrates"} and relation["subject_id"] in units_by_id and relation["object_id"] in by_id and by_id[relation["object_id"]]["entity_class"] == "concept":
            concept_ids_by_unit[relation["subject_id"]].add(relation["object_id"])
            coverage_relation_ids_by_unit[relation["subject_id"]].append(relation["record_id"])
            concept_unit_relations[relation["object_id"]].append(relation)
    correction_ids_by_unit: dict[str, list[str]] = defaultdict(list)
    for correction in corrections:
        for unit_id in correction.get("affected_unit_ids", []):
            correction_ids_by_unit[unit_id].append(correction["record_id"])
    segment_ids_by_unit: dict[str, list[str]] = defaultdict(list)
    for segment in by_class["segment"]:
        segment_ids_by_unit[segment["unit_id"]].append(segment["record_id"])

    unit_rows: list[dict[str, Any]] = []
    for unit_id in order:
        native = units_by_id[unit_id]
        route_url, route_kind = context_url(unit_id)
        unit_rows.append({
            "unit_id": unit_id,
            "preorder": ordinal[unit_id],
            "kind": native["unit_type"],
            "parent_id": native.get("parent_unit_id"),
            "child_unit_ids": [row["record_id"] for row in children.get(unit_id, [])],
            "ancestry": native.get("ancestry", []),
            "native_order": native.get("order"),
            "native_order_key": native.get("order_key"),
            "title_id": native.get("title_id"),
            "title_en": native.get("title_en"),
            "source_local_id": native.get("source_local_id"),
            "edition_id": native.get("edition_id"),
            "translation_state": native.get("translation_state"),
            "rights_id": native.get("rights_id"),
            "source_locator": native.get("source_locator"),
            "target_locator": native.get("target_locator"),
            "source_content_sha256": native.get("source_content_sha256"),
            "target_content_sha256": native.get("target_content_sha256"),
            "segment_ids": sorted(segment_ids_by_unit.get(unit_id, [])),
            "concept_ids": sorted(concept_ids_by_unit.get(unit_id, [])),
            "coverage_relation_ids": sorted(coverage_relation_ids_by_unit.get(unit_id, [])),
            "correction_ids": sorted(correction_ids_by_unit.get(unit_id, [])),
            "effective": unit_id in effective_ids,
            "superseded_by": superseded_by.get(unit_id),
            "direct_reader_url": direct_url.get(unit_id),
            "direct_reader_route_basis": direct_route_basis.get(unit_id),
            "reader_route": {"kind": route_kind, "url": route_url},
            "native_object_sha256": _record_hash(native),
        })
    unit_row_by_id = {row["unit_id"]: row for row in unit_rows}

    effective_by_anchor: dict[str, list[str]] = defaultdict(list)
    for unit_id in effective_ids:
        anchor = _anchor_id(units_by_id[unit_id].get("source_local_id"))
        if anchor:
            effective_by_anchor[anchor].append(unit_id)

    def native_for_reader(section: dict[str, Any], kind: str) -> str:
        candidates = [unit_id for unit_id in effective_by_anchor.get(section["id"], []) if units_by_id[unit_id]["unit_type"] == kind]
        if len(candidates) != 1:
            raise ValueError(f"C60 reader {kind} anchor lacks one native unit: {section['id']} -> {candidates}")
        return candidates[0]

    sitemap_chapters = [row for row in reader["sitemap"]["subsections"] if row["section"].get("level") == "1" and row["section"].get("number")]
    blocks: list[dict[str, Any]] = []
    section_routes: list[dict[str, Any]] = []
    for chapter_node in sitemap_chapters:
        chapter = chapter_node["section"]
        chapter_unit_id = native_for_reader(chapter, "chapter")
        descendant_ids: list[str] = []
        def descendants(unit_id: str) -> None:
            if unit_id in effective_ids:
                descendant_ids.append(unit_id)
            for child in children.get(unit_id, []):
                descendants(child["record_id"])
        descendants(chapter_unit_id)
        type_counts = Counter(units_by_id[unit_id]["unit_type"] for unit_id in descendant_ids)
        block_concepts = sorted({concept_id for unit_id in descendant_ids for concept_id in concept_ids_by_unit.get(unit_id, set())})
        chapter_sections: list[dict[str, Any]] = []
        for section_node in chapter_node.get("subsections", []):
            section = section_node["section"]
            if section.get("level") != "2":
                continue
            section_unit_id = native_for_reader(section, "section")
            route = {
                "number": section.get("number"),
                "title": section["title"],
                "anchor_id": section["id"],
                "native_unit_id": section_unit_id,
                "public_reader_url": f"{PAGES_URL}reader/{section['path']}",
            }
            chapter_sections.append(route)
            section_routes.append(route)
        blocks.append({
            "chapter_number": chapter["number"],
            "title": chapter["title"],
            "anchor_id": chapter["id"],
            "native_unit_id": chapter_unit_id,
            "public_reader_url": f"{PAGES_URL}reader/{chapter['path']}",
            "unit_ids": descendant_ids,
            "unit_count": len(descendant_ids),
            "unit_type_counts": dict(sorted(type_counts.items())),
            "concept_ids": block_concepts,
            "concept_count": len(block_concepts),
            "sections": chapter_sections,
        })
    if len(blocks) != 5 or len(section_routes) != 27:
        raise ValueError("C60 reader/native chapter or section mapping drift")

    terms_by_concept: dict[str, list[str]] = defaultdict(list)
    for term in terms:
        if term.get("concept_id"):
            terms_by_concept[term["concept_id"]].append(term["record_id"])
    concept_rows: list[dict[str, Any]] = []
    for concept in sorted(concepts, key=lambda row: row["record_id"]):
        links = concept_unit_relations[concept["record_id"]]
        linked_units = sorted({row["subject_id"] for row in links}, key=lambda unit_id: ordinal[unit_id])
        useful = sorted(
            linked_units,
            key=lambda unit_id: (
                unit_id not in effective_ids,
                unit_row_by_id[unit_id]["reader_route"]["kind"] != "exact_anchor",
                units_by_id[unit_id]["unit_type"] in {"frontmatter", "release_notes", "book"},
                ordinal[unit_id],
            ),
        )
        concept_rows.append({
            "concept_id": concept["record_id"],
            "concept_code": concept.get("concept_code"),
            "name_id": concept.get("name_id"),
            "name_en": concept.get("name_en"),
            "taxonomy_path": concept.get("taxonomy_path"),
            "prerequisite_concept_ids": concept.get("prerequisite_concept_ids", []),
            "unit_ids": linked_units,
            "coverage_relation_ids": sorted(row["record_id"] for row in links),
            "term_ids": sorted(terms_by_concept.get(concept["record_id"], [])),
            "primary_reader_url": unit_row_by_id[useful[0]]["reader_route"]["url"] if useful else None,
            "native_object_sha256": _record_hash(concept),
        })

    relation_counts = Counter(row["predicate"] for row in relations)
    relation_rows = [{
        "relation_id": row["record_id"],
        "predicate": row["predicate"],
        "subject_id": row["subject_id"],
        "object_id": row["object_id"],
        "confidence": row.get("confidence"),
        "evidence_locator": row.get("evidence_locator"),
        "native_object_sha256": _record_hash(row),
    } for row in sorted(relations, key=lambda item: item["record_id"])]

    terminology_qa = git_json(native_root, CURRENT_PUBLIC_HEAD, "qa/INDONESIAN_TERMINOLOGY_QA.json")
    rights_rows = [{
        "rights_id": row["record_id"],
        "locale": row.get("locale"),
        "license": row.get("license"),
        "license_url": row.get("license_url"),
        "rights_status": row.get("rights_status"),
        "component_paths": row.get("component_paths", []),
        "obligations": row.get("obligations", []),
        "change_notice": row.get("change_notice"),
        "non_endorsement": row.get("non_endorsement"),
        "evidence": row.get("evidence"),
        "attribution_entry_count": len(row.get("attribution", [])),
        "native_object_sha256": _record_hash(row),
    } for row in sorted(rights, key=lambda item: item["record_id"])]
    term_rows = [{
        "term_id": row["record_id"],
        "concept_id": row.get("concept_id"),
        "source_term": row.get("source_term"),
        "target_term": row.get("target_term"),
        "variants": row.get("variants", []),
        "rejected_forms": row.get("rejected_forms", []),
        "register": row.get("register"),
        "scope": row.get("scope"),
        "status": row.get("status"),
        "evidence": row.get("evidence"),
        "example_count": len(row.get("examples", [])),
        "native_object_sha256": _record_hash(row),
    } for row in sorted(terms, key=lambda item: item["record_id"])]
    correction_rows = [{
        "correction_id": row["record_id"],
        "correction_type": row.get("correction_type"),
        "affected_unit_ids": row.get("affected_unit_ids", []),
        "authority_locator": row.get("authority_locator"),
        "evidence": row.get("evidence"),
        "report_status": row.get("report_status"),
        "upstream_report_disposition": row.get("upstream_report_disposition"),
        "source_payload": {"bytes": len(row.get("source_text", "").encode("utf-8")), "sha256": sha256_bytes(row.get("source_text", "").encode("utf-8"))},
        "target_payload": {"bytes": len(row.get("target_text", "").encode("utf-8")), "sha256": sha256_bytes(row.get("target_text", "").encode("utf-8"))},
        "native_object_sha256": _record_hash(row),
    } for row in sorted(corrections, key=lambda item: item["record_id"])]

    release_manifest = git_json(native_root, CURRENT_PUBLIC_HEAD, "publication/RELEASE_MANIFEST.json")
    html_qa = reader["qa"]
    publication_receipt = next(row for row in migration["public_artifacts"] if row["path"] == "publication/PUBLICATION_RECEIPT.json")
    counts = {
        "source_lock_inputs": len(source_inputs),
        "backend_manifest_members": len(backend["manifest"]["files"]),
        "reader_manifest_members": len(reader["manifest"]["files"]),
        "native_records": len(records),
        "native_unique_ids": len(native_id_rows),
        "native_record_types": len(EXPECTED_NATIVE_COUNTS),
        "common_virtual_records": migration["target"]["record_count"],
        "common_tables": migration["target"]["table_count"],
        "common_nonempty_tables": migration["target"]["nonempty_table_count"],
        "units": len(units),
        "effective_units": len(effective_ids),
        "superseded_units": len(superseded_by),
        "unit_direct_reader_routes": len(direct_url),
        "effective_unit_direct_reader_routes": sum(unit_id in effective_ids for unit_id in direct_url),
        "unit_context_reader_routes": len(unit_rows),
        "native_exercise_units": sum(row["unit_type"] == "exercise" for row in units),
        "native_solution_records": 0,
        "segments": len(by_class["segment"]),
        "concepts": len(concepts),
        "concepts_with_reader_routes": sum(row["primary_reader_url"] is not None for row in concept_rows),
        "terms": len(terms),
        "terms_without_concept_binding": sum(row.get("concept_id") is None for row in terms),
        "corrections": len(corrections),
        "relations": len(relations),
        "rights_components": len(rights),
        "assets": len(by_class["asset"]),
        "artifacts": len(by_class["artifact"]),
        "qa_events": len(by_class["qa_event"]),
        "learner_chapters": len(blocks),
        "learner_sections": len(section_routes),
        "reader_html_pages": reader["manifest"]["build"]["html_pages"],
        "reader_html_files": html_qa["metrics"]["html_files"],
        "reader_html_bytes": html_qa["metrics"]["html_bytes"],
        "reader_unique_anchor_ids": len(anchor_pages),
        "reader_mathml_elements": html_qa["metrics"]["mathml_elements"],
        "reader_pdf_pages": html_qa["pdf"]["pages"],
    }

    claim_boundary = {
        "schema": "c60-claim-boundary/1",
        "course_id": COURSE_ID,
        "learner_attempt_instances": 0,
        "learner_submission_instances": 0,
        "learner_result_instances": 0,
        "assessment_instances": 0,
        "credential_assertion_instances": 0,
        "invented_exercise_instances": 0,
        "native_solution_records": 0,
        "native_unit_outcomes_invented": False,
        "native_unit_prerequisites_invented": False,
        "exercise_bodies_copied": False,
        "native_bodies_copied": False,
        "live_execution_claimed": False,
        "accessibility_conformance_claimed": False,
        "mathml_presence_treated_as_conformance": False,
        "full_offline_dependency_closure_claimed": False,
        "central_course_truth_rewritten": False,
        "historical_migration_receipt_rewritten": False,
        "common_virtual_backend_materialized": False,
        "excluded_destination_used": False,
        "public_state_changed": False,
        "source_attribution_values_embedded": False,
    }

    support_none = lambda exercise_id: {
        "status": "not_present",
        "source_anchor": exercise_id,
        "label": "source_has_none",
        "href": None,
    }
    capability_units: list[dict[str, Any]] = []
    for index, block in enumerate(blocks):
        exercise_ids = [unit_id for unit_id in block["unit_ids"] if units_by_id[unit_id]["unit_type"] == "exercise"]
        exercises = []
        for sequence, exercise_id in enumerate(exercise_ids, start=1):
            exercise = units_by_id[exercise_id]
            exercises.append({
                "id": exercise_id,
                "unit_id": block["native_unit_id"],
                "title": exercise.get("title_id") or f"Latihan {sequence}",
                "kind": "native_exercise_unit",
                "sequence": sequence,
                "curriculum_status": "native_source_identity_only",
                "href": unit_row_by_id[exercise_id]["reader_route"]["url"],
                "hint": support_none(exercise_id),
                "check": support_none(exercise_id),
                "solution": support_none(exercise_id),
            })
        capability_units.append({
            "id": block["native_unit_id"],
            "title": block["title"],
            "href": block["public_reader_url"],
            "sections": block["unit_ids"],
            "objectives_href": None,
            "previous_units": [] if index == 0 else [blocks[index - 1]["native_unit_id"]],
            "components": [{
                "id": block["native_unit_id"],
                "source": block["public_reader_url"],
                "license": "per-native-rights-record",
            }],
            "exercises": exercises,
        })
    if sum(len(row["exercises"]) for row in capability_units) != 101:
        raise ValueError("C60 strict capability exercise projection drift")
    catalog_input = next(row for row in backend["backend_inputs"] if row["path"] == "backend/catalog.json")
    learning_map = {
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "native_dataset": f"r014.backend.manifest@sha256:{backend['backend_inputs'][0]['sha256']}",
        "source_catalog": {
            "path": "backend/catalog.json",
            "bytes": catalog_input["bytes"],
            "sha256": catalog_input["sha256"],
            "url": f"https://raw.githubusercontent.com/KokunoYumeto/yet-another-introductory-number-theory-textbook-id/{CURRENT_PUBLIC_HEAD}/backend/catalog.json",
        },
        "units": capability_units,
        "prerequisite_routes": [{
            "id": f"route:C60:prerequisite:{prerequisite}",
            "unit": capability_units[0]["id"],
            "prerequisite": prerequisite,
            "required_for_course": True,
            "sections": [],
            "exercises": [],
            "href": f"https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/{prerequisite}/",
        } for prerequisite in course["prerequisite_course_ids"]],
        "labs": [],
        "environments": [],
        "artifacts": [
            {"id": "C60:artifact:public-reader", "kind": "text/html", "path": f"{PAGES_URL}reader/index.html"},
            {"id": "C60:artifact:public-pdf", "kind": "application/pdf", "path": f"{PAGES_URL}YAINTT_ID.pdf"},
        ],
        "sources": [
            {"id": resource["record_id"], "role": "translated_native_resource", "license": "per-native-rights-record", "identity": f"{NATIVE_RELEASE_COMMIT}:{BACKEND_TREE}"},
            {"id": "yaintt-source-2014-05-07-freeze-20260820", "role": "frozen_source_authority", "license": "per-native-rights-record", "identity": f"{NATIVE_RELEASE_COMMIT}:{SOURCE_TREE}"},
        ],
        "external_relation_nodes": course["prerequisite_course_ids"],
        "limitations": [
            "Adapter memproyeksikan identitas, struktur, istilah, koreksi, hak, dan bukti tanpa menyalin badan buku.",
            "Sebanyak 101 unit bertipe exercise berasal dari backend native; adapter tidak membuat latihan, solusi, asesmen, hasil pelajar, atau fungsi penilaian baru.",
            "Semua dukungan hint, check, dan solution ditandai not_present/source_has_none karena tidak ada rekaman dukungan native yang membuktikannya.",
            "Prasyarat B10 dan C30 adalah jangkar tingkat kursus native; tidak ada prasyarat atau hasil belajar per unit yang direka.",
            "Kehadiran MathML dan pemeriksaan struktur pembaca tidak dinyatakan sebagai sertifikasi kesesuaian aksesibilitas.",
            "Tautan utama menuju pembaca web publik; adapter tidak mengklaim penutupan dependensi luring penuh.",
        ],
    }
    educator_map = {
        "schema": "c60-educator-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "selector": {
            "selection_unit": "exact_native_unit_id",
            "export_format": "application/json",
            "body_content_embedded": False,
            "units": unit_rows,
        },
        "chapter_routes": blocks,
        "section_routes": section_routes,
        "counts": counts,
        "claim_boundary": {
            "all_native_units_indexed": True,
            "superseded_units_preserved_and_marked": True,
            "all_native_ids_preserved_in_native_id_index": True,
            "native_exercise_units_available_as_unit_metadata": counts["native_exercise_units"],
            "exercise_or_solution_bodies_embedded": False,
            "assessment_functionality_available": False,
            "live_execution_available": False,
            "unit_outcomes_available": False,
            "unit_prerequisites_available": False,
        },
        "limitations": [
            "Pemilih mengekspor metadata, ID, hierarki, hash, konsep, koreksi, dan rute pembaca; isi buku tidak disalin.",
            "Empat ID unit yang disupersesi tetap ada dan ditandai; 544 ID unit efektif tidak menggantikan inventaris native 548 unit.",
            "Jenis unit exercise adalah klasifikasi native, bukan bank asesmen baru dan bukan klaim tersedianya solusi.",
        ],
    }
    concept_index = {
        "schema": "c60-concept-index/1",
        "course_id": COURSE_ID,
        "concept_count": len(concept_rows),
        "concepts_with_reader_routes": counts["concepts_with_reader_routes"],
        "concepts": concept_rows,
        "body_content_embedded": False,
    }
    relation_index = {
        "schema": "c60-relation-index/1",
        "course_id": COURSE_ID,
        "relation_count": len(relation_rows),
        "relation_type_counts": dict(sorted(relation_counts.items())),
        "relations": relation_rows,
        "derived_relations_invented": 0,
        "body_content_embedded": False,
    }
    rights_and_terms = {
        "schema": "c60-rights-and-terms/1",
        "course_id": COURSE_ID,
        "source_contributors": resource["authors"],
        "component_rights": rights_rows,
        "terminology": term_rows,
        "corrections": correction_rows,
        "terminology_qa": {
            "status": terminology_qa["status"],
            "preferred_terms_changed": terminology_qa["result"]["preferred_terms_changed"],
            "glossary_rows_refined": terminology_qa["result"]["glossary_rows_refined"],
            "reader_passages_changed": terminology_qa["result"]["reader_passages_changed"],
            "provenance_model_identification": terminology_qa["result"]["provenance_model_identification"],
            "source_and_human_credits_preserved": terminology_qa["result"]["human_and_source_credits_preserved"],
        },
        "attribution_values_embedded": False,
        "attribution_and_full_native_payloads_preserved_by": ["native_object_sha256", "source-lock.json", MIGRATION_RECEIPT],
        "blanket_license_claimed": False,
        "body_content_embedded": False,
    }
    ledger_references = {
        "schema": "c60-ledger-references/1",
        "course_id": COURSE_ID,
        "migration_receipt": migration_input,
        "migration_id": migration["migration_id"],
        "migration_mode": migration["migration_mode"],
        "independent_receipt_replay": {
            "state": "pass",
            "checks": receipt_checks,
            "check_count": len(receipt_checks),
            "native_id_mapping_recomputed": backend["mapping_identity"],
            "native_id_inventory_recomputed": native_id_inventory,
        },
        "native": {
            "record_count": 5272,
            "record_counts": EXPECTED_NATIVE_COUNTS,
            "records_sha256": migration["source"]["records_sha256"],
            "catalog_sha256": migration["source"]["catalog_sha256"],
            "manifest_sha256": migration["source"]["manifest_sha256"],
            "foreign_key_closure": "pass",
            "catalog_exact_record_equivalence": "pass",
        },
        "common_projection": {
            "record_count": migration["target"]["record_count"],
            "table_count": migration["target"]["table_count"],
            "nonempty_table_count": migration["target"]["nonempty_table_count"],
            "canonical_backend_sha256": migration["target"]["canonical_backend_sha256"],
            "virtual_records_jsonl_bytes": migration["target"]["virtual_records_jsonl_bytes"],
            "virtual_records_jsonl_sha256": migration["target"]["virtual_records_jsonl_sha256"],
            "exact_reverse_extraction": migration["validation"]["exact_native_reverse_extraction"],
            "materialized": False,
        },
        "projection": {
            "native_ids_preserved": True,
            "native_payload_fields_preserved_by_existing_receipt": True,
            "native_bodies_copied": False,
            "historical_migration_receipt_rewritten": False,
            "common_virtual_backend_materialized": False,
        },
    }
    public_evidence = {
        "schema": "c60-public-evidence/1",
        "course_id": COURSE_ID,
        "github": {
            "repository": REPOSITORY,
            "current_public_head": CURRENT_PUBLIC_HEAD,
            "current_public_tree": CURRENT_PUBLIC_TREE,
            "native_release_commit": NATIVE_RELEASE_COMMIT,
            "native_release": RELEASE_VERSION,
            "release_url": f"{REPOSITORY}/releases/tag/v{RELEASE_VERSION}",
            "backend_tree": BACKEND_TREE,
            "source_tree": SOURCE_TREE,
            "docs_tree": DOCS_TREE,
            "backend_unchanged_from_release_commit": True,
            "source_unchanged_from_release_commit": True,
        },
        "reader": {
            "url": PAGES_URL,
            "landing_page": f"{PAGES_URL}",
            "reflowable_html": True,
            "reader_pages": reader["manifest"]["build"]["html_pages"],
            "chapters": len(blocks),
            "sections": len(section_routes),
            "mathml_elements_observed": html_qa["metrics"]["mathml_elements"],
            "local_links_checked": html_qa["metrics"]["local_links"],
            "missing_files": html_qa["metrics"]["missing_files"],
            "missing_anchors": html_qa["metrics"]["missing_anchors"],
            "pdf_pages": html_qa["pdf"]["pages"],
            "pdf_bytes": html_qa["pdf"]["bytes"],
            "pdf_sha256": html_qa["pdf"]["sha256"],
            "accessibility_conformance_claimed": False,
            "full_offline_dependency_closure_claimed": False,
        },
        "release": {
            "github_release": publication_receipt["github_release"],
            "zenodo_record": publication_receipt["zenodo_record"],
            "zenodo_version_doi": publication_receipt["zenodo_version_doi"],
            "zenodo_concept_doi": publication_receipt["zenodo_concept_doi"],
            "release_artifacts": release_manifest["required_release_artifacts"],
            "public_byte_receipt": {
                "path": publication_receipt["path"],
                "status": publication_receipt["status"],
                "bytes": publication_receipt["bytes"],
                "sha256": publication_receipt["sha256"],
            },
        },
        "verification_basis": "pinned_current_public_clone_plus_preserved_anonymous_publication_receipt",
        "excluded_destination_active": False,
        "historical_excluded_destination_receipt_preserved_only_in_migration_evidence": True,
        "public_state_changed": False,
    }
    capabilities = {
        "schema": "c60-capability-summary/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "native_family": "yaintt_r014_latex_backend_and_public_reflowable_reader",
        "counts": counts,
        "learner": {
            "ordered_chapter_navigation": True,
            "section_navigation": True,
            "all_native_unit_ids_routed": True,
            "all_concepts_routed": True,
            "direct_public_reflowable_reader": True,
            "linked_pdf": True,
        },
        "educator": {
            "all_native_unit_selector": True,
            "supersession_visible": True,
            "concept_index": True,
            "terminology_registry": True,
            "correction_registry": True,
            "json_plan_export": True,
            "assessment_functionality": False,
            "live_execution": False,
        },
        "reproducibility": {
            "git_object_inputs_hash_verified": True,
            "native_backend_unchanged_from_release_commit": True,
            "existing_reversible_migration_replayed": True,
            "existing_exact_reverse_extraction_records": 5272,
            "adapter_deterministic": True,
        },
        "rights": {"component_specific": True, "blanket_license_claimed": False},
        "claim_boundary": claim_boundary,
        "strict_contract_2_3_1_conformance_claimed": False,
    }
    source_lock = {
        "schema": "c60-source-lock/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "native_release": RELEASE_VERSION,
        "repository": {
            "url": REPOSITORY,
            **backend["commit_evidence"],
        },
        "local_source_locator": "04_mirrors/id/yet-another-introductory-number-theory-textbook-id/publication/github-pages-sync",
        "backend_inputs": backend["backend_inputs"],
        "control_inputs": control_inputs,
        "reader_inputs": reader["reader_inputs"],
        "migration_input": migration_input,
        "input_count": len(source_inputs),
        "inputs": source_inputs,
        "native_id_mapping": backend["mapping_identity"],
    }
    return {
        "source_lock": source_lock,
        "learning_map": learning_map,
        "educator_map": educator_map,
        "native_id_index": native_id_index,
        "concept_index": concept_index,
        "relation_index": relation_index,
        "rights_and_terms": rights_and_terms,
        "ledger_references": ledger_references,
        "public_evidence": public_evidence,
        "claim_boundary": claim_boundary,
        "capabilities": capabilities,
    }


def _has_forbidden_body_key(value: Any) -> bool:
    forbidden = {"text_latex", "source_text", "target_text", "source_text_latex", "target_text_latex"}
    if isinstance(value, dict):
        return any(key in forbidden or _has_forbidden_body_key(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_has_forbidden_body_key(item) for item in value)
    return False


def projection_errors(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source = bundle.get("source_lock", {})
    learning = bundle.get("learning_map", {})
    educator = bundle.get("educator_map", {})
    native_ids = bundle.get("native_id_index", {})
    concepts = bundle.get("concept_index", {})
    relations = bundle.get("relation_index", {})
    rights = bundle.get("rights_and_terms", {})
    ledgers = bundle.get("ledger_references", {})
    public = bundle.get("public_evidence", {})
    boundary = bundle.get("claim_boundary", {})
    counts = bundle.get("capabilities", {}).get("counts", {})
    unit_rows = educator.get("selector", {}).get("units", [])
    unit_ids = [row.get("unit_id") for row in unit_rows]
    native_rows = native_ids.get("records", [])
    native_row_ids = [row.get("native_id") for row in native_rows]

    if source.get("repository", {}).get("current_public_head") != CURRENT_PUBLIC_HEAD or source.get("repository", {}).get("current_public_tree") != CURRENT_PUBLIC_TREE:
        errors.append("C60-SOURCE-PUBLIC-HEAD")
    if source.get("repository", {}).get("current_backend_tree") != BACKEND_TREE or source.get("repository", {}).get("release_backend_tree") != BACKEND_TREE:
        errors.append("C60-SOURCE-BACKEND-TREE")
    if source.get("repository", {}).get("native_backend_unchanged_from_release_commit") is not True:
        errors.append("C60-SOURCE-BACKEND-DRIFT")
    inputs = source.get("inputs", [])
    if source.get("input_count") != len(inputs) or len(inputs) != 77:
        errors.append("C60-SOURCE-INPUTS")
    if len({(row.get("revision"), row.get("path")) for row in inputs}) != 77:
        errors.append("C60-SOURCE-INPUT-IDENTITY")
    if not inputs or any(row.get("bytes", -1) < 0 or not re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256", ""))) for row in inputs):
        errors.append("C60-SOURCE-INPUT-HASH")

    if len(native_rows) != 5272 or len(set(native_row_ids)) != 5272:
        errors.append("C60-NATIVE-ID-IDENTITY")
    if native_ids.get("class_counts") != EXPECTED_NATIVE_COUNTS:
        errors.append("C60-NATIVE-ID-CLASSES")
    if native_ids.get("native_payloads_embedded") is not False:
        errors.append("C60-NATIVE-PAYLOAD-COPY")
    if len(unit_rows) != 548 or len(set(unit_ids)) != 548:
        errors.append("C60-UNIT-IDENTITY")
    if [row.get("preorder") for row in unit_rows] != list(range(1, 549)):
        errors.append("C60-UNIT-ORDER")
    if len([row for row in unit_rows if row.get("effective")]) != 544 or len([row for row in unit_rows if row.get("superseded_by")]) != 4:
        errors.append("C60-UNIT-SUPERSESSION")
    if any(not row.get("reader_route", {}).get("url") for row in unit_rows):
        errors.append("C60-UNIT-ROUTE")
    if len([row for row in unit_rows if row.get("direct_reader_url")]) != 187 or len({row.get("direct_reader_url") for row in unit_rows if row.get("direct_reader_url")}) != 183:
        errors.append("C60-UNIT-DIRECT-ROUTE")
    blocks = educator.get("chapter_routes", [])
    if len(blocks) != 5 or [row.get("chapter_number") for row in blocks] != ["1", "2", "3", "4", "5"]:
        errors.append("C60-CHAPTER-ROUTES")
    if len(educator.get("section_routes", [])) != 27:
        errors.append("C60-SECTION-ROUTES")
    if [row.get("prerequisite") for row in learning.get("prerequisite_routes", [])] != ["B10", "C30"]:
        errors.append("C60-COURSE-PREREQUISITES")
    capability_units = learning.get("units", [])
    exercises = [exercise for row in capability_units for exercise in row.get("exercises", [])]
    if learning.get("contract") != CONTRACT or len(capability_units) != 5 or len(exercises) != 101 or len({row.get("id") for row in exercises}) != 101:
        errors.append("C60-COMMON-CONTRACT")
    for exercise in exercises:
        for key in ("hint", "check", "solution"):
            support = exercise.get(key, {})
            if support.get("status") != "not_present" or support.get("label") != "source_has_none" or support.get("href") is not None:
                errors.append("C60-EXERCISE-SUPPORT-INVENTION")

    concept_rows = concepts.get("concepts", [])
    if len(concept_rows) != 223 or concepts.get("concept_count") != 223:
        errors.append("C60-CONCEPTS")
    if any(not row.get("unit_ids") or not row.get("primary_reader_url") for row in concept_rows):
        errors.append("C60-CONCEPT-ROUTES")
    relation_rows = relations.get("relations", [])
    if len(relation_rows) != 3297 or relations.get("relation_count") != 3297:
        errors.append("C60-RELATIONS")
    if relations.get("relation_type_counts") != EXPECTED_RELATIONS:
        errors.append("C60-RELATION-TYPES")
    if relations.get("derived_relations_invented") != 0:
        errors.append("C60-RELATION-INVENTION")
    if len(rights.get("component_rights", [])) != 15 or rights.get("blanket_license_claimed") is not False:
        errors.append("C60-RIGHTS")
    if len(rights.get("terminology", [])) != 239:
        errors.append("C60-TERMINOLOGY")
    if len(rights.get("corrections", [])) != 141:
        errors.append("C60-CORRECTIONS")
    if rights.get("attribution_values_embedded") is not False:
        errors.append("C60-ATTRIBUTION-VALUE-COPY")

    replay = ledgers.get("independent_receipt_replay", {})
    if replay.get("state") != "pass" or replay.get("check_count") != 18 or not all(replay.get("checks", {}).values()):
        errors.append("C60-MIGRATION-REPLAY")
    if replay.get("native_id_mapping_recomputed") != {"bytes": 376458, "sha256": "0523c257438e10978881a29a8b48235478b285a91544d3b20f9551f9ce2faf52"}:
        errors.append("C60-MIGRATION-ID-MAPPING")
    if ledgers.get("common_projection", {}).get("record_count") != 6967 or ledgers.get("common_projection", {}).get("exact_reverse_extraction") != 5272:
        errors.append("C60-MIGRATION-ROUNDTRIP")
    if ledgers.get("common_projection", {}).get("materialized") is not False:
        errors.append("C60-MIGRATION-MATERIALIZATION")

    if public.get("github", {}).get("current_public_head") != CURRENT_PUBLIC_HEAD or public.get("github", {}).get("backend_unchanged_from_release_commit") is not True:
        errors.append("C60-PUBLIC-GITHUB")
    if public.get("reader", {}).get("reflowable_html") is not True or public.get("reader", {}).get("chapters") != 5 or public.get("reader", {}).get("sections") != 27:
        errors.append("C60-PUBLIC-READER")
    if public.get("reader", {}).get("accessibility_conformance_claimed") is not False or public.get("reader", {}).get("full_offline_dependency_closure_claimed") is not False:
        errors.append("C60-PUBLIC-OVERCLAIM")
    if public.get("excluded_destination_active") is not False or public.get("public_state_changed") is not False:
        errors.append("C60-PUBLIC-STATE")

    expected_counts = {
        "source_lock_inputs": 77,
        "backend_manifest_members": 33,
        "reader_manifest_members": 29,
        "native_records": 5272,
        "native_unique_ids": 5272,
        "native_record_types": 14,
        "common_virtual_records": 6967,
        "common_tables": 38,
        "common_nonempty_tables": 23,
        "units": 548,
        "effective_units": 544,
        "superseded_units": 4,
        "unit_direct_reader_routes": 187,
        "effective_unit_direct_reader_routes": 183,
        "unit_context_reader_routes": 548,
        "native_exercise_units": 101,
        "native_solution_records": 0,
        "segments": 544,
        "concepts": 223,
        "concepts_with_reader_routes": 223,
        "terms": 239,
        "terms_without_concept_binding": 16,
        "corrections": 141,
        "relations": 3297,
        "rights_components": 15,
        "assets": 14,
        "artifacts": 105,
        "qa_events": 131,
        "learner_chapters": 5,
        "learner_sections": 27,
        "reader_html_pages": 10,
        "reader_html_files": 11,
        "reader_html_bytes": 1229408,
        "reader_unique_anchor_ids": 293,
        "reader_mathml_elements": 2791,
        "reader_pdf_pages": 138,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            errors.append(f"C60-COUNT-{key.upper()}")

    false_keys = (
        "native_unit_outcomes_invented",
        "native_unit_prerequisites_invented",
        "exercise_bodies_copied",
        "native_bodies_copied",
        "live_execution_claimed",
        "accessibility_conformance_claimed",
        "mathml_presence_treated_as_conformance",
        "full_offline_dependency_closure_claimed",
        "central_course_truth_rewritten",
        "historical_migration_receipt_rewritten",
        "common_virtual_backend_materialized",
        "excluded_destination_used",
        "public_state_changed",
        "source_attribution_values_embedded",
    )
    for key in false_keys:
        if boundary.get(key) is not False:
            errors.append(f"C60-BOUNDARY-{key.upper()}")
    for key in (
        "learner_attempt_instances",
        "learner_submission_instances",
        "learner_result_instances",
        "assessment_instances",
        "credential_assertion_instances",
        "invented_exercise_instances",
        "native_solution_records",
    ):
        if boundary.get(key) != 0:
            errors.append(f"C60-NONZERO-{key.upper()}")
    if _has_forbidden_body_key(bundle):
        errors.append("C60-NATIVE-BODY-FIELD")
    return sorted(set(errors))
