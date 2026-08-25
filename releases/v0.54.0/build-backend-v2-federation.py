#!/usr/bin/env python3
"""Build the compact phase-one Program Matematika Indonesia v2 federation.

The federation is deliberately zero-copy: owner-native backends remain canonical.
This builder records their proven migration evidence, learner surfaces, public
routes, publication evidence, and an explicit v1 identity crosswalk.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


DEFAULT_PROGRAM_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKSPACE_ROOT = DEFAULT_PROGRAM_REPOSITORY_ROOT.parents[2]
DEFAULT_COORDINATOR_LOGBOOK_ROOT = (
    DEFAULT_WORKSPACE_ROOT
    / "outputs"
    / "01a01ec1-e685-70d0-b022-211396334723"
)
DEFAULT_OUTPUT = (
    DEFAULT_PROGRAM_REPOSITORY_ROOT
    / "backend"
    / "v2"
    / "program-matematika-indonesia-federation-v0.1.0"
)

NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
DEFAULT_RECORDED_AT = "2026-08-25T00:00:00Z"
DEFAULT_DATASET_VERSION = "program-matematika-indonesia-federation-v0.1.0"
SCHEMA_VERSION = "2.0.0"
PROGRAM_KEY = "program-matematika-indonesia"
DEFAULT_PUBLIC_SITE = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
ACTION_ORDER = {
    "learn": 0,
    "html": 1,
    "pdf": 2,
    "epub": 3,
    "offline": 4,
    "source": 5,
    "repository": 6,
    "doi": 7,
    "backend": 8,
}

TABLE_NAMES = {
    "dataset": "datasets",
    "program": "programs",
    "course": "courses",
    "reader_surface": "reader_surfaces",
    "web_route": "web_routes",
    "publication_event": "publication_events",
    "qa_event": "qa_events",
    "identity_crosswalk": "identity_crosswalks",
}

MIGRATION_ROLE_MAP = {
    "applied-combinatorics-id-v1": ["C70"],
    "dmoi4-id-v1": ["B10"],
    "erdman-functional-analysis-id-v1": ["D20"],
    "hefferon-linear-algebra-id-v1": ["B40"],
    "judson-id-v1": ["C30", "C40"],
    "mathematics-in-lean-id-v1": ["D110"],
    "o002-b80-id-v1": ["B80"],
    "o005-c120-id-v1": ["C120"],
    "o018-c130-id-v1": ["C130"],
    "openlogic-id-v1": ["C80"],
    "prealgebra2e-id-v1": ["A00"],
    "tea-time-id-v1": ["C110"],
    "yaintt-id-v1": ["C60"],
}

V1_TOPIC_CROSSWALK_KEYS = {
    "curriculum-topic:Fondasi & Kalkulus": "curriculum-topic:pmi-topic-01",
    "curriculum-topic:Analisis": "curriculum-topic:pmi-topic-02",
    "curriculum-topic:Aljabar": "curriculum-topic:pmi-topic-03",
    "curriculum-topic:Geometri & Topologi": "curriculum-topic:pmi-topic-04",
    "curriculum-topic:Peluang & Statistika": "curriculum-topic:pmi-topic-05",
    "curriculum-topic:Diskrit & Logika": "curriculum-topic:pmi-topic-06",
    "curriculum-topic:Komputasi & Optimisasi": "curriculum-topic:pmi-topic-07",
    "curriculum-topic:Praktik Riset": "curriculum-topic:pmi-topic-08",
}


def normalized_relative(value: str, option: str) -> PurePosixPath:
    candidate = PurePosixPath(value.replace("\\", "/"))
    windows_drive = bool(candidate.parts and len(candidate.parts[0]) >= 2 and candidate.parts[0][1] == ":")
    if candidate.is_absolute() or windows_drive or not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError(f"{option} must be a nonempty portable relative path without '.' or '..': {value!r}")
    return candidate


def resolve_under(root: Path, relative: PurePosixPath, option: str) -> Path:
    resolved_root = root.resolve()
    resolved = resolved_root.joinpath(*relative.parts).resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise ValueError(f"{option} escapes its declared root: {relative.as_posix()}")
    return resolved


@dataclass(frozen=True)
class BuildInputs:
    program_repository_root: Path
    coordinator_logbook_root: Path
    catalog_relative: PurePosixPath
    v1_package_relative: PurePosixPath
    site_readback_relative: PurePosixPath
    contract_relative: PurePosixPath
    role_map_relative: PurePosixPath
    migrations_relative: PurePosixPath
    educational_access_relative: PurePosixPath
    dataset_version: str
    recorded_at: str
    public_site: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "program_repository_root", self.program_repository_root.resolve())
        object.__setattr__(self, "coordinator_logbook_root", self.coordinator_logbook_root.resolve())
        if not self.dataset_version.strip():
            raise ValueError("--dataset-version must not be blank")
        if not self.recorded_at.endswith("Z"):
            raise ValueError("--recorded-at must be an explicit UTC timestamp ending in 'Z'")
        if not self.public_site.startswith("https://") or not self.public_site.endswith("/"):
            raise ValueError("--public-site must be an HTTPS URL ending in '/'")

    @property
    def contract_path(self) -> Path:
        return resolve_under(self.coordinator_logbook_root, self.contract_relative, "--contract-relative")

    @property
    def role_map_path(self) -> Path:
        return resolve_under(self.coordinator_logbook_root, self.role_map_relative, "--role-map-relative")

    @property
    def site_readback_path(self) -> Path:
        return resolve_under(self.coordinator_logbook_root, self.site_readback_relative, "--site-readback-relative")

    @property
    def catalog_path(self) -> Path:
        return resolve_under(self.program_repository_root, self.catalog_relative, "--catalog-relative")

    @property
    def v1_root(self) -> Path:
        return resolve_under(self.program_repository_root, self.v1_package_relative, "--v1-package-relative")

    @property
    def migrations_root(self) -> Path:
        return resolve_under(self.program_repository_root, self.migrations_relative, "--migrations-relative")

    @property
    def educational_access_root(self) -> Path:
        return resolve_under(self.program_repository_root, self.educational_access_relative, "--educational-access-relative")

    @property
    def namespace_document_path(self) -> Path:
        return self.program_repository_root / "schemas" / "v2" / "namespace-v2.json"

    @property
    def release_policy_path(self) -> Path:
        return self.program_repository_root / "schemas" / "v2" / "pmi-release-policy-v2.json"

    def replay_command(self) -> list[str]:
        return [
            "python", "-B", "scripts/build-backend-v2-federation.py",
            "--program-repository-root", "<PROGRAM_REPOSITORY_ROOT>",
            "--coordinator-logbook-root", "<COORDINATOR_LOGBOOK_ROOT>",
            "--catalog-relative", self.catalog_relative.as_posix(),
            "--v1-package-relative", self.v1_package_relative.as_posix(),
            "--site-readback-relative", self.site_readback_relative.as_posix(),
            "--contract-relative", self.contract_relative.as_posix(),
            "--role-map-relative", self.role_map_relative.as_posix(),
            "--migrations-relative", self.migrations_relative.as_posix(),
            "--educational-access-relative", self.educational_access_relative.as_posix(),
            "--dataset-version", self.dataset_version,
            "--recorded-at", self.recorded_at,
            "--public-site", self.public_site,
            "--output", "<OUTPUT>",
        ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--program-repository-root", type=Path, default=DEFAULT_PROGRAM_REPOSITORY_ROOT)
    parser.add_argument("--coordinator-logbook-root", type=Path, default=DEFAULT_COORDINATOR_LOGBOOK_ROOT)
    parser.add_argument("--catalog-relative", default="releases/v0.51.2/program-matematika-indonesia-catalog-v0.51.2.json")
    parser.add_argument("--v1-package-relative", default="backend/v1/program-matematika-indonesia-v0.51.2")
    parser.add_argument("--site-readback-relative", default="curriculum_logbook/83_STUDENT_HTML_HUB_PUBLIC_READBACK_20260825.json")
    parser.add_argument("--contract-relative", default="curriculum_logbook/81_GLOBAL_MODULAR_BACKEND_V2_CONTRACT_20260825.json")
    parser.add_argument("--role-map-relative", default="curriculum_logbook/49_SEMANTIC_ROLE_MAPPING_CORRECTION_20260823.json")
    parser.add_argument("--migrations-relative", default="backend/migrations")
    parser.add_argument("--educational-access-relative", default="backend/research/educational-access-v0.1.0")
    parser.add_argument("--dataset-version", default=DEFAULT_DATASET_VERSION)
    parser.add_argument("--recorded-at", default=DEFAULT_RECORDED_AT)
    parser.add_argument("--public-site", default=DEFAULT_PUBLIC_SITE)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output package directory (default: the canonical v0.1.0 package path).",
    )
    return parser.parse_args()


def build_inputs_from_args(args: argparse.Namespace) -> BuildInputs:
    return BuildInputs(
        program_repository_root=args.program_repository_root,
        coordinator_logbook_root=args.coordinator_logbook_root,
        catalog_relative=normalized_relative(args.catalog_relative, "--catalog-relative"),
        v1_package_relative=normalized_relative(args.v1_package_relative, "--v1-package-relative"),
        site_readback_relative=normalized_relative(args.site_readback_relative, "--site-readback-relative"),
        contract_relative=normalized_relative(args.contract_relative, "--contract-relative"),
        role_map_relative=normalized_relative(args.role_map_relative, "--role-map-relative"),
        migrations_relative=normalized_relative(args.migrations_relative, "--migrations-relative"),
        educational_access_relative=normalized_relative(args.educational_access_relative, "--educational-access-relative"),
        dataset_version=args.dataset_version,
        recorded_at=args.recorded_at,
        public_site=args.public_site,
    )


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_json_bytes(value: Any) -> bytes:
    return (canonical_json(value) + "\n").encode("utf-8")


def record_id(record_type: str, semantic_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(NAMESPACE, f'{record_type}:{semantic_key}')}"


def make_record(record_type: str, semantic_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    if record_type not in TABLE_NAMES:
        raise ValueError(f"Unsupported record type: {record_type}")
    return {
        "id": record_id(record_type, semantic_key),
        "record_type": record_type,
        "semantic_key": semantic_key,
        "payload": payload,
    }


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, value: Any) -> None:
    write_bytes(path, canonical_json_bytes(value))


def jsonl_bytes(records: Iterable[dict[str, Any]]) -> bytes:
    return "".join(canonical_json(record) + "\n" for record in records).encode("utf-8")


def csv_bytes(records: Iterable[dict[str, Any]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["record_type", "semantic_key", "id", "record_json"])
    for item in records:
        writer.writerow(
            [
                item["record_type"],
                item["semantic_key"],
                item["id"],
                canonical_json(item),
            ]
        )
    return buffer.getvalue().encode("utf-8")


def file_fact(path: Path, locator: str, role: str | None = None) -> dict[str, Any]:
    fact = {
        "path": locator.replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if role is not None:
        fact["role"] = role
    return fact


def source_fact(path: Path, locator: str, role: str) -> dict[str, Any]:
    fact = file_fact(path, locator)
    fact["role"] = role
    fact["locator_base"] = (
        "coordinator_logbook_root"
        if locator.replace("\\", "/").startswith("curriculum_logbook/")
        else "program_repository_root"
    )
    return fact


def first_value(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def nested(mapping: dict[str, Any], *path: str) -> Any:
    current: Any = mapping
    for part in path:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def unique_strings(values: Iterable[Any]) -> list[str]:
    return sorted({value for value in values if isinstance(value, str) and value})


def direct_pdf_url(url: Any) -> bool:
    if not isinstance(url, str) or not url:
        return False
    lower = url.lower()
    return ".pdf" in lower or ("/files/" in lower and ("download=" in lower or lower.endswith("/content")))


def course_card_url(course_id: str, public_site: str) -> str:
    return f"{public_site}#course-{course_id}"


def v1_records(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"v1 records line {line_number} is not an object")
            if not isinstance(value.get("id"), str) or not isinstance(value.get("record_type"), str):
                raise ValueError(f"v1 records line {line_number} lacks id or record_type")
            if not isinstance(value.get("stable_key"), str) or not value["stable_key"]:
                raise ValueError(f"v1 records line {line_number} lacks a stable_key")
            rows.append(value)
    return rows


def migration_receipts(inputs: BuildInputs) -> dict[str, dict[str, Any]]:
    receipts: dict[str, dict[str, Any]] = {}
    for directory, roles in sorted(MIGRATION_ROLE_MAP.items()):
        path = inputs.migrations_root / directory / "MIGRATION_RECEIPT.json"
        receipt = load_json(path)
        if nested(receipt, "validation", "result") != "pass":
            raise ValueError(f"Migration receipt is not passing: {path}")
        receipts[directory] = {
            "directory": directory,
            "roles": roles,
            "path": path,
            "locator": f"{inputs.migrations_relative.as_posix()}/{directory}/MIGRATION_RECEIPT.json",
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "receipt": receipt,
        }
    return receipts


def receipt_native_schema(receipt: dict[str, Any]) -> tuple[Any, Any]:
    source = receipt.get("source") if isinstance(receipt.get("source"), dict) else {}
    native_backend = (
        source.get("native_backend") if isinstance(source.get("native_backend"), dict) else {}
    )
    return (
        first_value(
            source.get("schema_name"),
            source.get("native_schema_name"),
            native_backend.get("native_schema_id"),
        ),
        first_value(
            source.get("schema_version"),
            source.get("native_schema_version"),
        ),
    )


def receipt_manifest(receipt: dict[str, Any]) -> tuple[Any, Any, str]:
    source = receipt.get("source") if isinstance(receipt.get("source"), dict) else {}
    native_backend = (
        source.get("native_backend") if isinstance(source.get("native_backend"), dict) else {}
    )
    candidates = [
        (source.get("package_manifest_path"), source.get("package_manifest_sha256")),
        (source.get("manifest_path"), source.get("manifest_sha256")),
        (source.get("native_manifest_path"), source.get("native_manifest_sha256")),
        (source.get("export_manifest_path"), source.get("export_manifest_sha256")),
    ]
    package_manifest = source.get("package_manifest")
    if isinstance(package_manifest, dict):
        candidates.append((package_manifest.get("path"), package_manifest.get("sha256")))
    export_manifest = native_backend.get("export_manifest")
    if isinstance(export_manifest, dict):
        candidates.append((export_manifest.get("path"), export_manifest.get("sha256")))
    for path, digest in candidates:
        if isinstance(digest, str) and digest:
            locator = path if isinstance(path, str) and path else "receipt:source.package_manifest"
            return locator, digest, "hash_recorded_in_migration_receipt"
    return None, None, "not_recorded_in_migration_receipt"


def receipt_record_counts(receipt: dict[str, Any]) -> tuple[Any, dict[str, int]]:
    source = receipt.get("source") if isinstance(receipt.get("source"), dict) else {}
    target = receipt.get("target") if isinstance(receipt.get("target"), dict) else {}
    native_backend = (
        source.get("native_backend") if isinstance(source.get("native_backend"), dict) else {}
    )
    candidates = [
        target.get("table_counts"),
        receipt.get("tables"),
        native_backend.get("record_counts"),
        source.get("record_counts"),
        source.get("native_type_counts"),
        source.get("native_record_counts"),
        source.get("native_table_counts"),
        source.get("view_counts"),
    ]
    counts: dict[str, int] = {}
    for candidate in candidates:
        if isinstance(candidate, dict) and candidate:
            if all(isinstance(key, str) and isinstance(value, int) for key, value in candidate.items()):
                counts = dict(sorted(candidate.items()))
                break
    total = first_value(
        target.get("record_count"),
        source.get("record_count"),
        source.get("canonical_record_count"),
        source.get("native_record_count"),
    )
    return total if isinstance(total, int) else None, counts


def receipt_content_shards(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    source = receipt.get("source") if isinstance(receipt.get("source"), dict) else {}
    native_backend = (
        source.get("native_backend") if isinstance(source.get("native_backend"), dict) else {}
    )
    candidates = [
        (
            source.get("records_path"),
            source.get("records_bytes"),
            source.get("records_sha256"),
            "application/x-ndjson",
        ),
        (
            source.get("native_backend_path"),
            source.get("native_backend_bytes"),
            source.get("native_backend_sha256"),
            "application/json",
        ),
        (
            source.get("catalog_path"),
            source.get("catalog_bytes"),
            source.get("catalog_sha256"),
            "application/json",
        ),
    ]
    native_jsonl = source.get("native_jsonl")
    if isinstance(native_jsonl, dict):
        candidates.append(
            (
                native_jsonl.get("path"),
                native_jsonl.get("bytes"),
                native_jsonl.get("sha256"),
                "application/x-ndjson",
            )
        )
    backend_jsonl = native_backend.get("jsonl")
    if isinstance(backend_jsonl, dict):
        candidates.append(
            (
                backend_jsonl.get("path"),
                backend_jsonl.get("bytes"),
                backend_jsonl.get("sha256"),
                "application/x-ndjson",
            )
        )
    shards = []
    for path, byte_count, digest, media_type in candidates:
        if isinstance(path, str) and path and isinstance(digest, str) and digest:
            shards.append(
                {
                    "kind": "content",
                    "locator": f"owner-native:{path}",
                    "bytes": byte_count if isinstance(byte_count, int) else None,
                    "sha256": digest,
                    "media_type": media_type,
                }
            )
    return sorted(shards, key=lambda item: item["locator"])


def build(inputs: BuildInputs) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    contract_path = inputs.contract_path
    role_map_path = inputs.role_map_path
    site_readback_path = inputs.site_readback_path
    catalog_path = inputs.catalog_path
    v1_records_path = inputs.v1_root / "records.jsonl"
    v1_manifest_path = inputs.v1_root / "manifest.json"
    v1_validation_path = inputs.v1_root / "validation_report.json"
    educational_manifest_path = inputs.educational_access_root / "manifest.json"
    educational_validation_path = inputs.educational_access_root / "validation_report.json"
    educational_records_path = inputs.educational_access_root / "records.jsonl"

    contract = load_json(contract_path)
    role_map_doc = load_json(role_map_path)
    site_readback = load_json(site_readback_path)
    catalog = load_json(catalog_path)
    v1_manifest = load_json(v1_manifest_path)
    v1_validation = load_json(v1_validation_path)
    educational_manifest = load_json(educational_manifest_path)
    educational_validation = load_json(educational_validation_path)
    legacy_records = v1_records(v1_records_path)
    receipts = migration_receipts(inputs)

    if contract.get("schema_id") != "interlanguage/global-modular-mathematics-backend-v2-decision/0.1":
        raise ValueError("Unexpected v2 contract")
    if site_readback.get("result") != "pass":
        raise ValueError("Student-site public readback is not passing")
    if v1_validation.get("result") != "pass" or educational_validation.get("result") != "pass":
        raise ValueError("Required predecessor validation is not passing")
    if v1_manifest.get("record_count") != len(legacy_records):
        raise ValueError("v1 manifest record count does not match records.jsonl")

    courses = catalog.get("courses")
    role_rows = role_map_doc.get("role_map")
    if not isinstance(courses, list) or len(courses) != 40:
        raise ValueError("Expected exactly 40 catalog courses")
    if not isinstance(role_rows, list) or len(role_rows) != 40:
        raise ValueError("Expected exactly 40 role-map rows")

    catalog_by_id = {item["id"]: item for item in courses}
    role_by_id = {item["role_id"]: item for item in role_rows}
    if set(catalog_by_id) != set(role_by_id):
        raise ValueError("Catalog and role-map course IDs differ")

    nonempty_owner_ids = unique_strings(row.get("thread_id") for row in role_rows)
    if len(nonempty_owner_ids) != 32:
        raise ValueError(f"Expected 32 nonempty task owners, found {len(nonempty_owner_ids)}")
    blank_owner_roles = sorted(
        row["role_id"] for row in role_rows if not isinstance(row.get("thread_id"), str) or not row["thread_id"]
    )
    if blank_owner_roles != ["C80"]:
        raise ValueError(f"Only C80 may be release-owned, found {blank_owner_roles}")

    owner_groups: dict[str, list[str]] = defaultdict(list)
    for role_id, row in role_by_id.items():
        thread_id = row.get("thread_id")
        group_key = thread_id if isinstance(thread_id, str) and thread_id else "release-authority:C80"
        owner_groups[group_key].append(role_id)
    for role_ids in owner_groups.values():
        role_ids.sort()
    if len(owner_groups) != 33:
        raise ValueError(f"Expected 33 curriculum authority groups, found {len(owner_groups)}")

    dataset_semantic_by_group: dict[str, str] = {}
    dataset_id_by_group: dict[str, str] = {}
    owner_group_by_role: dict[str, str] = {}
    for group_key, role_ids in owner_groups.items():
        semantic_key = f"curriculum:{'+'.join(role_ids)}"
        dataset_semantic_by_group[group_key] = semantic_key
        dataset_id_by_group[group_key] = record_id("dataset", semantic_key)
        for role_id in role_ids:
            owner_group_by_role[role_id] = group_key

    program_semantic_key = PROGRAM_KEY
    program_id = record_id("program", program_semantic_key)
    course_ids = {role_id: record_id("course", f"course:{role_id}") for role_id in catalog_by_id}
    route_ids = {role_id: record_id("web_route", f"course-card:{role_id}") for role_id in catalog_by_id}

    legacy_index = {
        (row["record_type"], row["stable_key"]): row["id"] for row in legacy_records
    }

    catalog_sha = sha256_file(catalog_path)
    site_readback_sha = sha256_file(site_readback_path)
    v1_records_sha = sha256_file(v1_records_path)

    # One surface is shared whenever action-compatible courses point at the same URL and format.
    surface_drafts: dict[tuple[str, str], dict[str, Any]] = {}
    course_surface_keys: dict[str, set[tuple[str, str]]] = defaultdict(set)
    verified_reader_evidence: dict[str, dict[str, str]] = {
        inputs.public_site: {
            "locator": inputs.site_readback_relative.as_posix(),
            "sha256": site_readback_sha,
        }
    }
    for row in site_readback.get("public_html_readers", []):
        if isinstance(row, dict) and isinstance(row.get("url"), str):
            verified_reader_evidence[row["url"]] = {
                "locator": inputs.site_readback_relative.as_posix(),
                "sha256": site_readback_sha,
            }
    for receipt_info in receipts.values():
        html_reader = nested(
            receipt_info["receipt"], "source", "public_evidence", "html_reader"
        )
        if not isinstance(html_reader, dict) or html_reader.get("result") != "pass":
            continue
        url = html_reader.get("url")
        readback = html_reader.get("readback")
        if (
            not isinstance(url, str)
            or not url.startswith("https://")
            or not isinstance(readback, dict)
            or readback.get("http_status") != 200
            or not isinstance(readback.get("sha256"), str)
        ):
            raise ValueError(
                f"Migration receipt has malformed HTML-reader evidence: {receipt_info['directory']}"
            )
        evidence = {
            "locator": receipt_info["locator"],
            "sha256": receipt_info["sha256"],
        }
        if url in verified_reader_evidence and verified_reader_evidence[url] != evidence:
            raise ValueError(f"Conflicting public-readback evidence for HTML reader: {url}")
        verified_reader_evidence[url] = evidence
    verified_reader_urls = set(verified_reader_evidence)

    def add_surface(course_id_value: str, url: str, format_value: str, action: str) -> None:
        key = (format_value, url)
        draft = surface_drafts.setdefault(
            key,
            {"course_ids": set(), "actions": set(), "url": url, "format": format_value},
        )
        draft["course_ids"].add(course_id_value)
        draft["actions"].add(action)
        course_surface_keys[course_id_value].add(key)

    def course_artifacts(role_id: str, course: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        reader = course.get("reader") if isinstance(course.get("reader"), str) else None
        edition = course.get("edition") if isinstance(course.get("edition"), str) else None
        if reader:
            learner_start = reader
        elif edition and direct_pdf_url(edition):
            learner_start = edition
        else:
            learner_start = course_card_url(role_id, inputs.public_site)
        pdf_url = edition if edition and direct_pdf_url(edition) else None
        return learner_start, {
            "learn": learner_start,
            "html": reader,
            "pdf": pdf_url,
            "epub": None,
            "offline": edition,
            "source": None,
            "repository": course.get("repository"),
            "doi": course.get("zenodo"),
            "backend": None,
        }

    def surface_format(action: str, url: str) -> str:
        if action == "learn":
            if direct_pdf_url(url):
                return "pdf"
            if url == inputs.public_site or url.startswith(inputs.public_site) or url.lower().endswith((".html", ".htm")):
                return "html"
            return "download"
        if action == "offline":
            return "pdf" if direct_pdf_url(url) else "download"
        return action

    for role_id in sorted(catalog_by_id):
        course = catalog_by_id[role_id]
        card = course_card_url(role_id, inputs.public_site)
        add_surface(role_id, card, "html", "learn")
        _, artifact_matrix = course_artifacts(role_id, course)
        for action in ACTION_ORDER:
            url = artifact_matrix[action]
            if not isinstance(url, str) or not url:
                continue
            if action == "html" and url not in verified_reader_urls:
                raise ValueError(f"Catalog HTML reader lacks public-readback evidence: {role_id}")
            format_value = (
                "html"
                if action == "learn" and isinstance(course.get("reader"), str) and url == course["reader"]
                else surface_format(action, url)
            )
            add_surface(role_id, url, format_value, action)
    for role_id in sorted(catalog_by_id):
        add_surface(role_id, inputs.public_site, "html", "learn")

    surface_id_by_key: dict[tuple[str, str], str] = {}
    reader_records: list[dict[str, Any]] = []
    for (format_value, url), draft in sorted(surface_drafts.items()):
        url_token = hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]
        semantic_key = f"surface:{format_value}:{url_token}"
        surface_id = record_id("reader_surface", semantic_key)
        surface_id_by_key[(format_value, url)] = surface_id
        fragment_uses_program_readback = url.startswith(f"{inputs.public_site}#course-")
        is_verified = url in verified_reader_urls or fragment_uses_program_readback
        evidence = verified_reader_evidence.get(url)
        if evidence is None and fragment_uses_program_readback:
            evidence = verified_reader_evidence[inputs.public_site]
        course_roles = sorted(role for role in draft["course_ids"] if role != "__program__")
        reader_records.append(
            make_record(
                "reader_surface",
                semantic_key,
                {
                    "locale": "id-ID",
                    "format": format_value,
                    "actions": sorted(draft["actions"], key=lambda action: ACTION_ORDER[action]),
                    "url": url,
                    "course_ids": course_roles,
                    "publication_state": "public" if is_verified else "catalog_declared",
                    "evidence_kind": "public_readback" if is_verified else "catalog_declared",
                    "evidence_locator": (
                        evidence["locator"] if evidence is not None else inputs.catalog_relative.as_posix()
                    ),
                    "evidence_sha256": evidence["sha256"] if evidence is not None else catalog_sha,
                },
            )
        )

    surface_ids_by_course = {
        role_id: sorted(surface_id_by_key[key] for key in keys)
        for role_id, keys in course_surface_keys.items()
        if role_id != "__program__"
    }

    # QA IDs are precomputed so dataset records can reference them.
    qa_v1_key = f"curriculum-backend-v1-builder:{catalog_sha}"
    qa_site_key = f"student-html-public-readback:{site_readback_sha}"
    qa_edu_key = f"educational-access-validation:{sha256_file(educational_validation_path)}"
    qa_id_by_migration = {
        name: record_id("qa_event", f"migration:{info['receipt']['migration_id']}")
        for name, info in receipts.items()
    }
    qa_site_id = record_id("qa_event", qa_site_key)
    qa_edu_id = record_id("qa_event", qa_edu_key)

    receipt_by_role: dict[str, dict[str, Any]] = {}
    for info in receipts.values():
        for role_id in info["roles"]:
            if role_id in receipt_by_role:
                raise ValueError(f"Multiple migration receipts claim {role_id}")
            receipt_by_role[role_id] = info

    dataset_records: list[dict[str, Any]] = []
    for group_key, role_ids in sorted(owner_groups.items(), key=lambda item: item[1]):
        receipt_infos = {receipt_by_role[role_id]["directory"]: receipt_by_role[role_id] for role_id in role_ids if role_id in receipt_by_role}
        if len(receipt_infos) > 1:
            raise ValueError(f"One owner group unexpectedly spans several migration receipts: {role_ids}")
        receipt_info = next(iter(receipt_infos.values()), None)
        receipt = receipt_info["receipt"] if receipt_info else None
        role_courses = [catalog_by_id[role_id] for role_id in role_ids]
        role_authorities = [role_by_id[role_id] for role_id in role_ids]
        corpus_titles = unique_strings(row.get("corpus") for row in role_authorities)
        workflow_state = (
            "published" if all(course.get("state") == "published" for course in role_courses) else "producing"
        )
        any_public_reference = any(
            course.get("reader") or course.get("edition") or course.get("zenodo") for course in role_courses
        )
        if receipt_info and all(course.get("state") == "published" for course in role_courses):
            publication_state = "public"
        elif any_public_reference or all(course.get("state") == "published" for course in role_courses):
            publication_state = "partially_public"
        else:
            publication_state = "not_published"

        native_schema_name = native_schema_version = None
        adapter_id = adapter_version = adapter_sha = adapter_locator = None
        migration_locator = migration_sha = migration_result = None
        manifest_locator = manifest_sha = None
        manifest_state = "not_migrated"
        total_count = None
        type_counts: dict[str, int] = {}
        content_shards: list[str] = []
        qa_receipt_ids: list[str] = []
        corpus_id = f"curriculum-roles:{'+'.join(role_ids)}"
        if receipt is not None and receipt_info is not None:
            native_schema_name, native_schema_version = receipt_native_schema(receipt)
            adapter_id = receipt.get("migration_id")
            adapter_version = receipt.get("migration_id")
            adapter_sha = receipt_info["sha256"]
            adapter_locator = receipt_info["locator"]
            migration_locator = receipt_info["locator"]
            migration_sha = receipt_info["sha256"]
            migration_result = nested(receipt, "validation", "result")
            manifest_locator, manifest_sha, manifest_state = receipt_manifest(receipt)
            if manifest_locator is not None:
                manifest_locator = f"owner-native:{manifest_locator}"
            total_count, type_counts = receipt_record_counts(receipt)
            content_shards = receipt_content_shards(receipt)
            qa_receipt_ids = [qa_id_by_migration[receipt_info["directory"]]]
            source_dataset_id = first_value(
                nested(receipt, "source", "dataset_id"),
                nested(receipt, "source", "corpus_id"),
            )
            if isinstance(source_dataset_id, str) and source_dataset_id:
                corpus_id = source_dataset_id

        verified_roles = set()
        for row in site_readback.get("public_html_readers", []):
            if isinstance(row, dict) and isinstance(row.get("role"), str):
                verified_roles.update(row["role"].split("/"))
        public_readback_receipt_id = qa_site_id if verified_roles.intersection(role_ids) else None
        owner_locator = (
            f"codex://threads/{group_key}"
            if group_key != "release-authority:C80"
            else "https://github.com/KokunoYumeto/OpenLogic-id"
        )
        owner_state = "task_owned" if group_key != "release-authority:C80" else "release_authority"
        available_locales = ["id-ID"] if receipt_info or any_public_reference else []
        semantic_key = dataset_semantic_by_group[group_key]
        dataset_records.append(
            make_record(
                "dataset",
                semantic_key,
                {
                    "dataset_kind": "curriculum_owner",
                    "corpus_id": corpus_id,
                    "canonical_owner_locator": owner_locator,
                    "canonical_owner_state": owner_state,
                    "course_ids": role_ids,
                    "corpus_titles": corpus_titles,
                    "workflow_state": workflow_state,
                    "native_schema_name": native_schema_name,
                    "native_schema_version": native_schema_version,
                    "adapter_id": adapter_id,
                    "adapter_version": adapter_version,
                    "adapter_sha256": adapter_sha,
                    "adapter_evidence_kind": "migration_receipt" if receipt_info else "not_available",
                    "adapter_locator": adapter_locator,
                    "migration_receipt_locator": migration_locator,
                    "migration_receipt_sha256": migration_sha,
                    "migration_validation_result": migration_result or "not_run",
                    "package_manifest_locator": manifest_locator,
                    "package_manifest_url": None,
                    "package_manifest_sha256": manifest_sha,
                    "package_manifest_evidence_state": (
                        "verified_local"
                        if manifest_state == "hash_recorded_in_migration_receipt"
                        else "absent"
                    ),
                    "record_count_total": total_count,
                    "record_counts": type_counts,
                    "available_locales": available_locales or ["id-ID"],
                    "content_shards": content_shards,
                    "search_shards": [],
                    "reader_surface_ids": sorted(
                        {
                            surface_id
                            for role_id in role_ids
                            for surface_id in surface_ids_by_course[role_id]
                        }
                    ),
                    "release_snapshot_id": None,
                    "qa_receipt_ids": qa_receipt_ids,
                    "public_readback_receipt_id": public_readback_receipt_id,
                    "publication_state": publication_state,
                },
            )
        )

    edu_manifest_sha = sha256_file(educational_manifest_path)
    educational_locator = inputs.educational_access_relative.as_posix()
    edu_records_manifest_row = next(
        row for row in educational_manifest["files"] if row.get("path") == "records.jsonl"
    )
    research_semantic_key = "research-support:educational-access:0.1.0"
    dataset_records.append(
        make_record(
            "dataset",
            research_semantic_key,
            {
                "dataset_kind": "research_support",
                "corpus_id": "educational-access-v0.1.0",
                "canonical_owner_locator": f"{educational_locator}/manifest.json",
                "canonical_owner_state": "project_authority",
                "course_ids": sorted(catalog_by_id),
                "corpus_titles": ["Educational access research-support federation"],
                "workflow_state": "infrastructure",
                "native_schema_name": "interlanguage/educational-access-federation",
                "native_schema_version": "1",
                "adapter_id": None,
                "adapter_version": None,
                "adapter_sha256": None,
                "adapter_evidence_kind": "not_available",
                "adapter_locator": None,
                "migration_receipt_locator": None,
                "migration_receipt_sha256": None,
                "migration_validation_result": "pass",
                "package_manifest_locator": f"{educational_locator}/manifest.json",
                "package_manifest_url": None,
                "package_manifest_sha256": edu_manifest_sha,
                "package_manifest_evidence_state": "verified_local",
                "record_count_total": educational_manifest["record_count"],
                "record_counts": dict(sorted(educational_manifest["table_counts"].items())),
                "available_locales": ["id-ID"],
                "content_shards": [
                    {
                        "kind": "content",
                        "locator": f"{educational_locator}/records.jsonl",
                        "bytes": edu_records_manifest_row["bytes"],
                        "sha256": edu_records_manifest_row["sha256"],
                        "media_type": "application/x-ndjson",
                    }
                ],
                "search_shards": [],
                "reader_surface_ids": [],
                "release_snapshot_id": None,
                "qa_receipt_ids": [qa_edu_id],
                "public_readback_receipt_id": None,
                "publication_state": "not_published",
            },
        )
    )

    program_info = catalog["program"]
    program_record = make_record(
        "program",
        program_semantic_key,
        {
            "program_key": program_info["id"],
            "title": program_info["title"],
            "locale": program_info["language"],
            "version": program_info["version"],
            "status": program_info["status"].replace("-", "_"),
            "course_ids": sorted(course_ids.values()),
            "learner_start_url": program_info["website"],
            "catalog_locator": inputs.catalog_relative.as_posix(),
            "catalog_sha256": catalog_sha,
            "v1_program_id": legacy_index.get(("program", PROGRAM_KEY)),
        },
    )

    course_records: list[dict[str, Any]] = []
    for role_id in sorted(catalog_by_id):
        course = catalog_by_id[role_id]
        role = role_by_id[role_id]
        learner_start, artifact_matrix = course_artifacts(role_id, course)
        group_key = owner_group_by_role[role_id]
        owner_locator = (
            f"codex://threads/{group_key}"
            if group_key != "release-authority:C80"
            else "https://github.com/KokunoYumeto/OpenLogic-id"
        )
        course_records.append(
            make_record(
                "course",
                f"course:{role_id}",
                {
                    "course_id": role_id,
                    "program_id": program_id,
                    "owner_dataset_id": dataset_id_by_group[group_key],
                    "canonical_owner_locator": owner_locator,
                    "lane": role["lane"],
                    "level": course["level"],
                    "topic": course["topic"],
                    "state": course["state"],
                    "title": course["title"],
                    "prerequisite_course_ids": course["prerequisites"],
                    "purpose": course["purpose"],
                    "outcome": course["outcome"],
                    "corpus": course["corpus"],
                    "note": course["note"],
                    "learner_start_url": learner_start,
                    "artifact_matrix": artifact_matrix,
                    "web_route_id": route_ids[role_id],
                    "web_route_root": course_card_url(role_id, inputs.public_site),
                    "planned_unit_route_pattern": f"/id-ID/courses/{role_id}/units/{{stable_unit_slug}}/",
                    "unit_route_state": "planned_not_published",
                    "source_catalog_sha256": catalog_sha,
                    "v1_course_id": legacy_index.get(("course", f"course:{role_id}")),
                },
            )
        )

    route_records: list[dict[str, Any]] = [
        make_record(
            "web_route",
            "hub:root",
            {
                "route_kind": "program_root_current",
                "locale": "id-ID",
                "path": "/",
                "public_url": inputs.public_site,
                "course_ids": sorted(catalog_by_id),
                "publication_state": "public",
                "learner_fallback_url": inputs.public_site,
                "planned_clean_root": None,
                "planned_unit_route_pattern": None,
                "unit_route_state": "not_applicable",
                "evidence_locator": inputs.site_readback_relative.as_posix(),
                "evidence_sha256": site_readback_sha,
            },
        )
    ]
    for role_id in sorted(catalog_by_id):
        route_records.append(
            make_record(
                "web_route",
                f"course-card:{role_id}",
                {
                    "route_kind": "learner_card_current",
                    "locale": "id-ID",
                    "path": f"/#course-{role_id}",
                    "public_url": course_card_url(role_id, inputs.public_site),
                    "course_ids": [role_id],
                    "publication_state": "public",
                    "learner_fallback_url": course_artifacts(role_id, catalog_by_id[role_id])[0],
                    "planned_clean_root": f"/id-ID/courses/{role_id}/",
                    "planned_unit_route_pattern": f"/id-ID/courses/{role_id}/units/{{stable_unit_slug}}/",
                    "unit_route_state": "planned_not_published",
                    "evidence_locator": inputs.site_readback_relative.as_posix(),
                    "evidence_sha256": site_readback_sha,
                },
            )
        )

    publication_records: list[dict[str, Any]] = []
    curriculum_dataset_ids = sorted(
        record["id"]
        for record in dataset_records
        if record["payload"]["dataset_kind"] == "curriculum_owner"
    )
    publication_records.append(
        make_record(
            "publication_event",
            "central-site:2026-08-25-readback",
            {
                "publication_kind": "github_pages",
                "course_ids": sorted(catalog_by_id),
                "dataset_ids": curriculum_dataset_ids,
                "url": inputs.public_site,
                "doi": None,
                "published_at": None,
                "version": program_info["version"],
                "state": "readback_verified",
                "evidence_kind": "anonymous_public_readback",
                "evidence_locator": inputs.site_readback_relative.as_posix(),
                "evidence_sha256": site_readback_sha,
                "artifact_count": len(site_readback["public_byte_identity"]),
                "total_bytes": sum(row["bytes"] for row in site_readback["public_byte_identity"]),
            },
        )
    )
    zenodo = site_readback["zenodo_preservation"]
    publication_records.append(
        make_record(
            "publication_event",
            f"central-zenodo:{zenodo['doi']}",
            {
                "publication_kind": "zenodo_version",
                "course_ids": sorted(catalog_by_id),
                "dataset_ids": curriculum_dataset_ids,
                "url": zenodo["record_url"],
                "doi": zenodo["doi"],
                "published_at": f"{zenodo['published']}T00:00:00Z",
                "version": program_info["version"],
                "state": "readback_verified",
                "evidence_kind": "anonymous_public_readback",
                "evidence_locator": inputs.site_readback_relative.as_posix(),
                "evidence_sha256": site_readback_sha,
                "artifact_count": zenodo["file_count"],
                "total_bytes": zenodo["total_bytes"],
            },
        )
    )

    publication_groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for role_id, course in catalog_by_id.items():
        if isinstance(course.get("edition"), str) and course["edition"]:
            publication_groups[("course_edition_reference", course["edition"])].append(role_id)
        if isinstance(course.get("zenodo"), str) and course["zenodo"]:
            publication_groups[("course_doi_reference", course["zenodo"])].append(role_id)
    for (kind, url), roles in sorted(publication_groups.items()):
        roles.sort()
        url_token = hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]
        doi = url.removeprefix("https://doi.org/") if url.startswith("https://doi.org/") else None
        lower_url = url.lower()
        if "zenodo.org" in lower_url or (doi and "zenodo" in doi):
            publication_kind = "zenodo_version"
        elif "github.com" in lower_url and "/releases/" in lower_url:
            publication_kind = "github_release"
        elif "github.com" in lower_url:
            publication_kind = "github_repository"
        else:
            publication_kind = "other_public_archive"
        publication_records.append(
            make_record(
                "publication_event",
                f"{kind}:{url_token}",
                {
                    "publication_kind": publication_kind,
                    "course_ids": roles,
                    "dataset_ids": sorted(
                        {dataset_id_by_group[owner_group_by_role[role_id]] for role_id in roles}
                    ),
                    "url": url,
                    "doi": doi,
                    "published_at": None,
                    "version": None,
                    "state": "declared",
                    "evidence_kind": "public_metadata",
                    "evidence_locator": inputs.catalog_relative.as_posix(),
                    "evidence_sha256": catalog_sha,
                    "artifact_count": None,
                    "total_bytes": None,
                },
            )
        )

    qa_records: list[dict[str, Any]] = [
        make_record(
            "qa_event",
            qa_v1_key,
            {
                "qa_kind": "aggregate",
                "result": "pass",
                "subject_ids": [program_id],
                "method": "strict v1 schema, identity closure, manifest, deterministic replay, and CSV round trip",
                "evidence_locator": f"{inputs.v1_package_relative.as_posix()}/validation_report.json",
                "evidence_sha256": sha256_file(v1_validation_path),
                "record_count": v1_validation["checks"]["record_count"],
                "details": {"source_records_sha256": v1_records_sha},
            },
        ),
        make_record(
            "qa_event",
            qa_site_key,
            {
                "qa_kind": "anonymous_public_readback",
                "result": "pass",
                "subject_ids": [program_id],
                "method": "anonymous HTTP readback and local/public byte identity",
                "evidence_locator": inputs.site_readback_relative.as_posix(),
                "evidence_sha256": site_readback_sha,
                "record_count": 40,
                "details": {
                    "verified_public_html_readers": len(site_readback["public_html_readers"]),
                    "verified_site_files": len(site_readback["public_byte_identity"]),
                },
            },
        ),
        make_record(
            "qa_event",
            qa_edu_key,
            {
                "qa_kind": "aggregate",
                "result": "pass",
                "subject_ids": [record_id("dataset", research_semantic_key)],
                "method": "strict schema, UUIDv5, foreign keys, source replay, and JSONL/CSV round trip",
                "evidence_locator": f"{educational_locator}/validation_report.json",
                "evidence_sha256": sha256_file(educational_validation_path),
                "record_count": educational_validation["records"],
                "details": {
                    "materialized_table_count": len(educational_validation["table_counts"]),
                    "materialized_tables": sorted(educational_validation["table_counts"]),
                },
            },
        ),
    ]
    for name, info in sorted(receipts.items()):
        receipt = info["receipt"]
        subject_group_ids = sorted(
            {dataset_id_by_group[owner_group_by_role[role_id]] for role_id in info["roles"]}
        )
        qa_records.append(
            make_record(
                "qa_event",
                f"migration:{receipt['migration_id']}",
                {
                    "qa_kind": "authority_hash_binding",
                    "result": "pass",
                    "subject_ids": subject_group_ids,
                    "method": receipt["migration_mode"],
                    "evidence_locator": info["locator"],
                    "evidence_sha256": info["sha256"],
                    "record_count": nested(receipt, "target", "record_count"),
                    "details": {
                        "migration_id": receipt["migration_id"],
                        "source_dataset_id": nested(receipt, "source", "dataset_id"),
                        "target_dataset_id": nested(receipt, "target", "dataset_id"),
                    },
                },
            )
        )

    phase_one_targets: set[tuple[str, str]] = set()
    records_without_crosswalks = (
        dataset_records
        + [program_record]
        + course_records
        + reader_records
        + route_records
        + publication_records
        + qa_records
    )
    for item in records_without_crosswalks:
        phase_one_targets.add((item["record_type"], item["semantic_key"]))

    crosswalk_records: list[dict[str, Any]] = []
    for legacy in sorted(legacy_records, key=lambda row: (row["record_type"], row["stable_key"], row["id"])):
        legacy_type = legacy["record_type"]
        legacy_key = legacy["stable_key"]
        crosswalk_key = f"v1:{legacy_type}:{legacy['id']}"
        v2_type = legacy_type
        v2_key = V1_TOPIC_CROSSWALK_KEYS.get(legacy_key, legacy_key)
        mapping_state = (
            "materialized_phase_one"
            if (v2_type, v2_key) in phase_one_targets
            else "reserved_not_materialized"
        )
        crosswalk_records.append(
            make_record(
                "identity_crosswalk",
                crosswalk_key,
                {
                    "legacy_schema_name": legacy.get("schema_name"),
                    "legacy_schema_version": legacy.get("schema_version"),
                    "legacy_record_type": legacy_type,
                    "legacy_semantic_key": legacy_key,
                    "legacy_id": legacy["id"],
                    "v2_record_type": v2_type,
                    "v2_semantic_key": v2_key,
                    "v2_id": record_id(v2_type, v2_key),
                    "mapping_state": mapping_state,
                    "source_records_locator": f"{inputs.v1_package_relative.as_posix()}/records.jsonl",
                    "source_records_sha256": v1_records_sha,
                },
            )
        )

    all_records = sorted(
        records_without_crosswalks + crosswalk_records,
        key=lambda item: (item["record_type"], item["semantic_key"]),
    )
    if len({item["id"] for item in all_records}) != len(all_records):
        raise ValueError("Generated record IDs are not globally unique")
    if len({(item["record_type"], item["semantic_key"]) for item in all_records}) != len(all_records):
        raise ValueError("Generated semantic keys are not unique within record type")

    v1_locator = inputs.v1_package_relative.as_posix()
    source_inputs = [
        source_fact(contract_path, inputs.contract_relative.as_posix(), "v2_contract"),
        source_fact(role_map_path, inputs.role_map_relative.as_posix(), "canonical_owner_role_map"),
        source_fact(site_readback_path, inputs.site_readback_relative.as_posix(), "student_site_public_readback"),
        source_fact(catalog_path, inputs.catalog_relative.as_posix(), "curriculum_catalog"),
        source_fact(v1_records_path, f"{v1_locator}/records.jsonl", "v1_identity_source"),
        source_fact(v1_manifest_path, f"{v1_locator}/manifest.json", "v1_package_manifest"),
        source_fact(v1_validation_path, f"{v1_locator}/validation_report.json", "v1_validation"),
        source_fact(educational_manifest_path, f"{educational_locator}/manifest.json", "research_support_manifest"),
        source_fact(educational_validation_path, f"{educational_locator}/validation_report.json", "research_support_validation"),
        source_fact(educational_records_path, f"{educational_locator}/records.jsonl", "research_support_records"),
    ]
    for name, info in sorted(receipts.items()):
        source_inputs.append(source_fact(info["path"], info["locator"], f"migration_receipt:{name}"))
    source_inputs.sort(key=lambda item: item["path"])

    limitations = [
        "Phase one is a compact federation registry; it does not copy owner-native content records.",
        "For migrated corpora, adapter_sha256 binds the complete migration-receipt registration because the receipts do not uniformly expose a standalone executable-adapter hash.",
        "Unmigrated owner datasets retain null native-schema, adapter, manifest, and record-count fields rather than inferred values.",
        "Public course-card fragment routes are live; clean per-course and per-unit route roots remain explicitly not_published.",
        "All 2,122 v1 IDs are preserved by crosswalk; target IDs for record types outside phase one are reserved_not_materialized.",
        "No course-level content or search shard is claimed unless its migration receipt records a hash-bound native locator.",
    ]
    metadata = {
        "source_inputs": source_inputs,
        "limitations": limitations,
        "expected_counts": {
            "curriculum_owner_datasets": 33,
            "research_support_datasets": 1,
            "courses": 40,
            "nonempty_task_owners": 32,
            "release_authority_datasets": 1,
            "v1_crosswalks": len(legacy_records),
        },
    }
    return all_records, metadata, legacy_records


def materialize(inputs: BuildInputs, output: Path) -> dict[str, Any]:
    records, metadata, legacy_records = build(inputs)
    output.mkdir(parents=True, exist_ok=True)
    (output / "data").mkdir(parents=True, exist_ok=True)
    (output / "csv").mkdir(parents=True, exist_ok=True)

    aggregate_jsonl = jsonl_bytes(records)
    aggregate_csv = csv_bytes(records)
    write_bytes(output / "records.jsonl", aggregate_jsonl)
    write_bytes(output / "records.csv", aggregate_csv)

    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in records:
        by_type[item["record_type"]].append(item)
    record_counts = {
        TABLE_NAMES[record_type]: len(by_type[record_type]) for record_type in sorted(by_type)
    }

    projection_paths: list[Path] = [output / "records.jsonl", output / "records.csv"]
    for record_type in sorted(by_type):
        table_name = TABLE_NAMES[record_type]
        jsonl_path = output / "data" / f"{table_name}.jsonl"
        csv_path = output / "csv" / f"{table_name}.csv"
        write_bytes(jsonl_path, jsonl_bytes(by_type[record_type]))
        write_bytes(csv_path, csv_bytes(by_type[record_type]))
        projection_paths.extend([jsonl_path, csv_path])

    projection_facts = []
    for path in sorted(projection_paths):
        relative = path.relative_to(output).as_posix()
        if relative == "records.jsonl":
            role = "records_authority"
        elif relative == "records.csv":
            role = "lossless_exchange"
        elif relative.startswith("data/"):
            role = "table_jsonl"
        elif relative.startswith("csv/"):
            role = "table_csv"
        else:
            raise ValueError(f"Unclassified projection path: {relative}")
        projection_facts.append(file_fact(path, relative, role))

    table_statuses = {
        TABLE_NAMES[record_type]: {
            "record_type": record_type,
            "materialized": True,
            "count": len(by_type[record_type]),
            "jsonl_file": f"data/{TABLE_NAMES[record_type]}.jsonl",
            "csv_file": f"csv/{TABLE_NAMES[record_type]}.csv",
        }
        for record_type in sorted(by_type)
    }
    namespace_fact = file_fact(inputs.namespace_document_path, "schemas/v2/namespace-v2.json")
    release_policy_fact = file_fact(inputs.release_policy_path, "schemas/v2/pmi-release-policy-v2.json")
    envelope = {
        "$schema": "../../../schemas/v2/federation-package-v2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-federation-package/2.0.0",
        "schema_version": SCHEMA_VERSION,
        "package_id": record_id("package", inputs.dataset_version),
        "dataset_id": record_id("dataset", "program-matematika-indonesia-federation"),
        "dataset_version": inputs.dataset_version,
        "recorded_at": inputs.recorded_at,
        "identity_namespace": str(NAMESPACE),
        "identity_formula": "record_type:semantic_key",
        "namespace_document": namespace_fact,
        "release_policy_profile": release_policy_fact,
        "canonical_serialization": {
            "authority": "records.jsonl",
            "encoding": "UTF-8",
            "newline": "LF",
            "record_order": ["record_type", "semantic_key"],
            "json_object_encoding": "UTF-8 compact JSON with lexicographically sorted object keys",
            "trailing_newline": True,
        },
        "records_file": "records.jsonl",
        "records_bytes": len(aggregate_jsonl),
        "records_sha256": sha256_bytes(aggregate_jsonl),
        "lossless_csv_file": "records.csv",
        "lossless_csv_bytes": len(aggregate_csv),
        "lossless_csv_sha256": sha256_bytes(aggregate_csv),
        "record_count": len(records),
        "record_counts": record_counts,
        "materialized_tables": [TABLE_NAMES[key] for key in sorted(by_type)],
        "table_statuses": table_statuses,
        "file_inventory_scope": "materialized data files only; excludes federation.json and manifest.json",
        "build": {
            "builder_path": "scripts/build-backend-v2-federation.py",
            "builder_sha256": sha256_file(Path(__file__).resolve()),
            "inputs": {
                "catalog_relative": inputs.catalog_relative.as_posix(),
                "v1_package_relative": inputs.v1_package_relative.as_posix(),
                "site_readback_relative": inputs.site_readback_relative.as_posix(),
                "contract_relative": inputs.contract_relative.as_posix(),
                "role_map_relative": inputs.role_map_relative.as_posix(),
                "migrations_relative": inputs.migrations_relative.as_posix(),
                "educational_access_relative": inputs.educational_access_relative.as_posix(),
                "dataset_version": inputs.dataset_version,
                "recorded_at": inputs.recorded_at,
                "public_site": inputs.public_site,
            },
            "command": inputs.replay_command(),
            "deterministic_replay": "pass",
            "build_a_records_sha256": sha256_bytes(aggregate_jsonl),
            "build_b_records_sha256": sha256_bytes(aggregate_jsonl),
        },
        "source_evidence": metadata["source_inputs"],
        "files": projection_facts,
        "limitations": metadata["limitations"],
    }
    write_json(output / "federation.json", envelope)

    manifest_paths = projection_paths + [output / "federation.json"]
    manifest_facts = [
        file_fact(path, path.relative_to(output).as_posix()) for path in sorted(manifest_paths)
    ]
    manifest = {
        "schema_id": "interlanguage/global-modular-mathematics-federation-manifest/v2",
        "schema_version": SCHEMA_VERSION,
        "dataset_id": envelope["dataset_id"],
        "dataset_version": inputs.dataset_version,
        "recorded_at": inputs.recorded_at,
        "record_count": len(records),
        "record_counts": record_counts,
        "files": manifest_facts,
        "source_inputs": metadata["source_inputs"],
    }
    write_json(output / "manifest.json", manifest)

    result = {
        "output": str(output.resolve()),
        "record_count": len(records),
        "record_counts": record_counts,
        "expected_counts": metadata["expected_counts"],
        "v1_input_records": len(legacy_records),
        "files": [
            file_fact(path, path.relative_to(output).as_posix())
            for path in sorted(manifest_paths + [output / "manifest.json"])
        ],
    }
    return result


def main() -> int:
    args = parse_args()
    inputs = build_inputs_from_args(args)
    result = materialize(inputs, args.output.resolve())
    sys.stdout.write(canonical_json(result) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
