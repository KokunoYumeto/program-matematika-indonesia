#!/usr/bin/env python3
"""Validate the additive CLP v2.3.1 successor without mutating its inputs.

This validator is intentionally separate from ``validate-modular-backend-
snapshots-v2.py``.  The latter validates an immutable historical snapshot and
therefore must not be made to silently change its denominator or release
identity.  This program validates a successor candidate supplied on the
command line (or the conventional ``authority/clp-family-v231`` paths).

The validator is read-only unless ``--output`` is explicitly supplied.  It
never extracts an archive.  ZIP members are read through ``ZipFile.open`` in
bounded chunks, so CRCs and member hashes are checked without materialising
the 6.6 GB uncompressed package in memory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse


VALIDATOR_VERSION = "1.0.0"
DEFAULT_INDEX = Path(
    "backend/course-capsule-v1/authority/clp-family-v231/"
    "v23-adapter-index-v2.json"
)
DEFAULT_SIDECAR = Path(
    "backend/course-capsule-v1/authority/clp-family-v231/"
    "learner-reader-actions-v1.json"
)
DEFAULT_ARCHIVE = Path(
    "backend/course-capsule-v1/authority/clp-family-v231/"
    "CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip"
)
DEFAULT_SCHEMA = Path(
    "schemas/course-capsule-v1/v2/v23-adapter-index-v2.schema.json"
)

CLP_PACKAGE_ID = "urn:uuid:8dbda99c-2e39-5fc0-a6ff-64a52cb81b26"
CLP_FAMILY_ID = "family-06-clp"
CLP_DATASET_ID = "urn:uuid:5276fa22-58b4-5bf8-b84b-3de141f617d5"
CLP_EXTENSION_ID = "urn:uuid:fb88c199-de1a-587b-9824-37fc25c797a0"
CLP_ARCHIVE_BYTES = 545_418_367
CLP_ARCHIVE_SHA256 = (
    "f2e2714c5f1349092e8cb574d6495e604086c9df3bc4bdf5bbe5974b5f61360d"
)
CLP_MANIFEST_BYTES = 31_266
CLP_MANIFEST_SHA256 = (
    "54b600004e6ce4d903f6890a0a9a5c7c0d03120da896ea57d3c85edf674f00e5"
)
CLP_MEMBER_COUNT = 70
CLP_UNCOMPRESSED_BYTES = 6_591_980_682
CLP_ROUTE_EVIDENCE_BYTES = 28_779
CLP_ROUTE_EVIDENCE_SHA256 = (
    "d806aee1d1ac177d9ad41844d847f5d4d1abf6895de47b6eedbb7c5e17c262e9"
)

CLP_ROLES = ("B20", "B30", "B50", "B60")
EXPECTED_CLP_PACKAGE_METRICS: dict[str, int] = {
    "canonical_records": 1_201_557,
    "native_records_preserved": 289_473,
    "reversible_native_mappings": 285_630,
    "additional_native_index_rows": 3_843,
    "rights_assignments": 283_778,
    "reader_pages": 4_077,
    "unit_records": 53_676,
    "relation_records": 138_673,
    "namespace_mappings": 285_630,
    "public_artifacts": 5_059,
    "jsonl_csv_table_pairs": 19,
}

EXPECTED_ROUTES: dict[tuple[str, str], dict[str, Any]] = {
    (
        "B20",
        "textbook",
    ): {
        "pages": 442,
        "bytes": 4_997_608,
        "sha256": "e0466ca75b793aed64e2c356014233d9e85072b077a3b2d3344926835c408ec2",
        "url": "https://zenodo.org/records/22183943/files/00_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_BUKU_TEKS.pdf?download=1",
    },
    (
        "B20",
        "problembook",
    ): {
        "pages": 646,
        "bytes": 3_263_082,
        "sha256": "911b2a0e3a9de6eccb9dd93042fa697e8f02e4bb1ecdacec86ade68744245021",
        "url": "https://zenodo.org/records/22183943/files/01_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_SOAL_DAN_PENYELESAIAN.pdf?download=1",
    },
    (
        "B30",
        "combined_textbook_problembook",
    ): {
        "pages": 1_243,
        "bytes": 7_793_932,
        "sha256": "2306d4bf92748ab99b8a0d57de77846fa196bfbf84f4666f3ecd8edd711d3aab",
        "url": "https://zenodo.org/records/22182941/files/CLP-2_Kalkulus_Integral_Bahasa_Indonesia_edisi_lengkap_2026-08-30.pdf?download=1",
    },
    (
        "B50",
        "textbook",
    ): {
        "pages": 410,
        "bytes": 6_136_187,
        "sha256": "0ce02a3d3fada175c97a8af4ecc6c5b3c4b5d04479bc4f0a9a3e605f2b71fe4d",
        "url": "https://zenodo.org/records/22184443/files/CLP-3-Kalkulus-Multivariabel-Bahasa-Indonesia.pdf?download=1",
    },
    (
        "B50",
        "problembook",
    ): {
        "pages": 534,
        "bytes": 5_750_878,
        "sha256": "ad1d184825fd7ac58933512b62a60997ddcfb2beae87dde5ec679503f31dae2d",
        "url": "https://zenodo.org/records/22184443/files/CLP-3-Latihan-Kalkulus-Multivariabel-Bahasa-Indonesia.pdf?download=1",
    },
    (
        "B60",
        "textbook",
    ): {
        "pages": 316,
        "bytes": 3_758_521,
        "sha256": "5ecf6047b63afd4a456cc230f69016aea59d80cd0bd2be73ce24b0000df98b87",
        "url": "https://zenodo.org/records/22105443/files/CLP-4-Kalkulus-Vektor-Bahasa-Indonesia.pdf?download=1",
    },
    (
        "B60",
        "problembook",
    ): {
        "pages": 486,
        "bytes": 3_939_483,
        "sha256": "a6253809eaa4a465d5efcc4372b1321ad828aa4964ec45042aab9130a358835b",
        "url": "https://zenodo.org/records/22105443/files/CLP-4-Latihan-Kalkulus-Vektor-Bahasa-Indonesia.pdf?download=1",
    },
}

EXPECTED_BINDING_ROUTES = {"B20": 2, "B30": 1, "B50": 2, "B60": 2}
EXPECTED_ROUTE_SEQUENCE = [
    ("B20", "textbook"),
    ("B20", "problembook"),
    ("B30", "combined_textbook_problembook"),
    ("B50", "textbook"),
    ("B50", "problembook"),
    ("B60", "textbook"),
    ("B60", "problembook"),
]
CONTROL_MEMBERS = {"manifest.json", "seal.json", "PACKAGE_CHECKSUMS.sha256"}


class DuplicateKeyError(ValueError):
    """Raised when a JSON object repeats a key."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=_unique_object)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def display_path(path: Path, root: Path) -> str:
    """Return a deterministic, non-private path for a validation receipt."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return f"external/{path.name}"


def resolve_path(root: Path, value: str | Path | None, default: Path) -> Path:
    raw = default if value is None else Path(value)
    if raw.is_absolute():
        return raw
    return root / raw


def safe_member_name(name: str) -> tuple[bool, str]:
    """Validate a ZIP name without ever resolving it on the host filesystem."""
    if not name or "\x00" in name:
        return False, "empty or NUL-containing member name"
    normalized = name.replace("\\", "/")
    # ``PurePosixPath`` collapses repeated separators before exposing
    # ``parts``.  Check the raw normalized spelling first so an archive cannot
    # smuggle an ambiguous alias such as ``docs//index.json`` through the
    # duplicate-name check below.
    if "//" in normalized:
        return False, "repeated separator member name"
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        return False, "absolute member name"
    parts = PurePosixPath(normalized).parts
    if ".." in parts:
        return False, "parent traversal member name"
    if any(part == "" for part in parts):
        return False, "empty path component member name"
    return True, normalized


def inventory_sha256(facts: Iterable[Mapping[str, Any]]) -> str:
    payload = "".join(
        f"{item['path']}\0{item['bytes']}\0{item['sha256']}\n"
        for item in sorted(facts, key=lambda item: str(item["path"]))
    ).encode("utf-8")
    return sha256_bytes(payload)


class CheckBook:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, check_id: str, passed: bool, detail: Any) -> None:
        self.rows.append(
            {
                "id": check_id,
                "status": "pass" if passed else "fail",
                "detail": detail,
            }
        )

    def require(self, check_id: str, condition: bool, detail: Any) -> bool:
        self.add(check_id, condition, detail)
        return condition

    @property
    def failed(self) -> bool:
        return any(row["status"] == "fail" for row in self.rows)

    def ordered(self) -> list[dict[str, Any]]:
        return sorted(self.rows, key=lambda row: row["id"])


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="validate-clp-successor-v231.py",
        description=(
            "Read-only validator for the additive CLP v2.3.1 successor. "
            "It checks the v2 index, one shared CLP package/four bindings, "
            "seven learner PDF actions, and a ZIP by streaming its bytes and "
            "members. No input is modified or extracted."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="central program repository root; relative inputs are resolved here",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=DEFAULT_INDEX,
        help="successor v23 adapter-index JSON (relative to --root unless absolute)",
    )
    parser.add_argument(
        "--sidecar",
        type=Path,
        default=DEFAULT_SIDECAR,
        help="seven-action learner-reader sidecar JSON",
    )
    parser.add_argument(
        "--zip",
        dest="archive",
        type=Path,
        default=DEFAULT_ARCHIVE,
        help="CLP adapter ZIP; may be an external sealed intake path",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="optional staged build_a/manifest.json; otherwise use the ZIP member",
    )
    parser.add_argument(
        "--route-evidence",
        type=Path,
        default=None,
        help="optional source route-evidence JSON for sidecar provenance replay",
    )
    parser.add_argument(
        "--sealed-route-evidence",
        type=Path,
        default=None,
        help="optional original 28,779-byte sealed route-evidence JSON for compact-source replay",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="v23-adapter-index JSON Schema (relative to --root unless absolute)",
    )
    parser.add_argument(
        "--no-schema",
        action="store_true",
        help="skip JSON Schema validation (structural CLP checks still run)",
    )
    parser.add_argument(
        "--sidecar-schema",
        type=Path,
        default=None,
        help="optional learner-reader-actions JSON Schema; auto-used when schemas/v1 copy exists",
    )
    parser.add_argument(
        "--expected-packages",
        type=int,
        default=9,
        help="required total distinct package rows in the successor",
    )
    parser.add_argument(
        "--expected-bindings",
        type=int,
        default=13,
        help="required total role-binding rows in the successor",
    )
    parser.add_argument(
        "--expected-members",
        type=int,
        default=CLP_MEMBER_COUNT,
        help="required ZIP member count; use 0 to disable this count check",
    )
    parser.add_argument(
        "--expected-uncompressed-bytes",
        type=int,
        default=CLP_UNCOMPRESSED_BYTES,
        help="required sum of ZIP member uncompressed bytes; use 0 to disable",
    )
    parser.add_argument(
        "--clp-package-id",
        default=CLP_PACKAGE_ID,
        help="CLP package UUID to require and share across B20/B30/B50/B60",
    )
    parser.add_argument(
        "--clp-family-id",
        default=CLP_FAMILY_ID,
        help="CLP native family identifier",
    )
    parser.add_argument(
        "--require-canonical-json",
        action="store_true",
        help="fail if index or sidecar bytes are not sorted-key canonical JSON",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="optional receipt path; writing is the only mutation this program can perform",
    )
    return parser.parse_args(argv)


def schema_check(
    book: CheckBook,
    index: Any,
    schema_path: Path | None,
    root: Path,
    check_id: str = "index.schema_validation",
) -> None:
    if schema_path is None:
        book.add(check_id, True, "not requested")
        return
    if not schema_path.is_file():
        book.add(check_id, False, f"missing schema: {display_path(schema_path, root)}")
        return
    try:
        schema = load_json(schema_path)
        from jsonschema import Draft202012Validator, FormatChecker

        Draft202012Validator.check_schema(schema)
        errors = sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(index),
            key=lambda error: list(error.absolute_path),
        )
        messages = [
            f"/{'/'.join(map(str, error.absolute_path))}: {error.message}"
            for error in errors[:20]
        ]
        book.add(
            check_id,
            not errors,
            {"schema": display_path(schema_path, root), "errors": messages},
        )
    except ImportError as exc:
        book.add(check_id, False, f"jsonschema unavailable: {exc}")
    except Exception as exc:  # malformed schema or validator failure
        book.add(check_id, False, f"schema validation error: {exc}")


def validate_index(
    book: CheckBook,
    index: Any,
    args: argparse.Namespace,
    index_path: Path,
    root: Path,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any]]:
    if not isinstance(index, dict):
        book.add("index.object", False, "index root is not an object")
        return None, None, {}
    packages = index.get("packages")
    bindings = index.get("adapters")
    if not isinstance(packages, list):
        book.add("index.packages_array", False, "packages is not an array")
        packages = []
    else:
        book.add("index.packages_array", True, len(packages))
    if not isinstance(bindings, list):
        book.add("index.bindings_array", False, "adapters is not an array")
        bindings = []
    else:
        book.add("index.bindings_array", True, len(bindings))

    package_ids = [row.get("package_id") for row in packages if isinstance(row, dict)]
    role_ids = [row.get("role_id") for row in bindings if isinstance(row, dict)]
    snapshot = index.get("snapshot")
    snapshot_shape = (
        isinstance(snapshot, dict)
        and snapshot.get("snapshot_kind") == "live_successor_overlay"
        and snapshot.get("mutable_overlay") is True
        and isinstance(snapshot.get("snapshot_id"), str)
        and bool(snapshot.get("snapshot_id"))
        and isinstance(snapshot.get("central_release_version"), str)
        and isinstance(snapshot.get("supersedes"), dict)
        and snapshot["supersedes"].get("central_release_version") == "v0.62.16"
        and snapshot.get("public_replay_state")
        in {"prepublication_local_validation_only", "postpublication_release_assets_readback_complete"}
    )
    book.require("index.snapshot_successor_shape", snapshot_shape, snapshot)
    book.require(
        "index.package_count",
        len(packages) == args.expected_packages,
        {"actual": len(packages), "expected": args.expected_packages},
    )
    book.require(
        "index.binding_count",
        len(bindings) == args.expected_bindings,
        {"actual": len(bindings), "expected": args.expected_bindings},
    )
    book.require(
        "index.unique_package_ids",
        len(package_ids) == len(set(package_ids)),
        {"actual": len(package_ids), "unique": len(set(package_ids))},
    )
    book.require(
        "index.unique_role_ids",
        len(role_ids) == len(set(role_ids)),
        {"actual": len(role_ids), "unique": len(set(role_ids))},
    )
    package_by_id = {
        row.get("package_id"): row
        for row in packages
        if isinstance(row, dict) and isinstance(row.get("package_id"), str)
    }
    binding_by_role = {
        row.get("role_id"): row
        for row in bindings
        if isinstance(row, dict) and isinstance(row.get("role_id"), str)
    }
    clp_package = package_by_id.get(args.clp_package_id)
    book.require(
        "clp.package_present_once",
        isinstance(clp_package, dict),
        {"package_id": args.clp_package_id},
    )
    if not isinstance(clp_package, dict):
        clp_package = None
    for metric, expected in EXPECTED_CLP_PACKAGE_METRICS.items():
        actual = clp_package.get(metric) if clp_package else None
        book.require(
            f"clp.package_metric.{metric}",
            actual == expected,
            {"actual": actual, "expected": expected},
        )
    for key, expected in {
        "native_family_id": args.clp_family_id,
        "package_id": args.clp_package_id,
        "dataset_id": CLP_DATASET_ID,
        "extension_id": CLP_EXTENSION_ID,
        "contract_version": "2.3.1",
        "adapter_version": "0.1.0",
    }.items():
        actual = clp_package.get(key) if clp_package else None
        book.require(f"clp.package_identity.{key}", actual == expected, {"actual": actual, "expected": expected})
    for key, expected in {
        "owner_native_authoritative": True,
        "zero_copy": True,
        "native_html_claimed": False,
        "unit_or_page_anchors_claimed": False,
    }.items():
        actual = clp_package.get(key) if clp_package else None
        book.require(f"clp.package_policy.{key}", actual == expected, {"actual": actual, "expected": expected})

    if clp_package:
        archive_fact = clp_package.get("archive")
        manifest_fact = clp_package.get("manifest")
        book.require(
            "clp.archive_fact",
            isinstance(archive_fact, dict)
            and archive_fact.get("bytes") == CLP_ARCHIVE_BYTES
            and archive_fact.get("sha256") == CLP_ARCHIVE_SHA256,
            archive_fact,
        )
        book.require(
            "clp.manifest_fact",
            isinstance(manifest_fact, dict)
            and manifest_fact.get("bytes") == CLP_MANIFEST_BYTES
            and manifest_fact.get("sha256") == CLP_MANIFEST_SHA256,
            manifest_fact,
        )
        state = clp_package.get("admission_state")
        pending_shape = (
            state == "admitted_pending_release"
            and clp_package.get("release_url") is None
            and clp_package.get("public_asset_url") is None
            and clp_package.get("public_replay_status")
            == "pending_release_local_seal_verified"
            and isinstance(clp_package.get("planned_release"), dict)
        )
        published_shape = (
            state == "published"
            and isinstance(clp_package.get("release_url"), str)
            and isinstance(clp_package.get("public_asset_url"), str)
            and clp_package.get("public_replay_status")
            == "published_public_asset_readback_verified"
            and "planned_release" not in clp_package
        )
        book.require(
            "clp.admission_state_shape",
            pending_shape or published_shape,
            {"state": state, "pending": pending_shape, "published": published_shape},
        )
        if state == "admitted_pending_release":
            planned = clp_package.get("planned_release") or {}
            placeholders = any(
                isinstance(planned.get(k), str) and "<" in planned.get(k, "")
                for k in ("central_release_version", "artifact_path", "public_url_after_release")
            )
            book.require("clp.planned_release_no_placeholders", not placeholders, planned)

    clp_bindings = [binding_by_role.get(role) for role in CLP_ROLES]
    book.require(
        "clp.four_role_bindings_present",
        all(isinstance(row, dict) for row in clp_bindings),
        {"roles": list(CLP_ROLES), "present": [row is not None for row in clp_bindings]},
    )
    for role, binding in zip(CLP_ROLES, clp_bindings):
        if not isinstance(binding, dict):
            continue
        expected_url = next(
            fact["url"]
            for (course, _kind), fact in EXPECTED_ROUTES.items()
            if course == role and (_kind == "textbook" or course == "B30")
        )
        checks = {
            "adapter_package_id": args.clp_package_id,
            "native_family_id": args.clp_family_id,
            "learner_runtime_relationship": "course_link_only_no_adapter_consumption_claim",
            "course_specific_route_count": EXPECTED_BINDING_ROUTES[role],
            "learner_url": expected_url,
        }
        for key, expected in checks.items():
            book.require(
                f"clp.binding.{role}.{key}",
                binding.get(key) == expected,
                {"actual": binding.get(key), "expected": expected},
            )
        projection = binding.get("central_learner_projection")
        if projection is not None:
            book.require(
                f"clp.binding.{role}.projection_shape",
                isinstance(projection, dict)
                and isinstance(projection.get("path"), str)
                and projection["path"].startswith("docs/")
                and projection.get("locale") == "id-ID"
                and projection.get("status") in {"published", "pending_successor_release"},
                projection,
            )

    # Every binding must resolve to a package, and its family must agree.
    for role, binding in binding_by_role.items():
        package = package_by_id.get(binding.get("adapter_package_id"))
        book.require(
            f"binding.resolve.{role}",
            isinstance(package, dict),
            {"adapter_package_id": binding.get("adapter_package_id")},
        )
        if isinstance(package, dict):
            book.require(
                f"binding.family_match.{role}",
                binding.get("native_family_id") == package.get("native_family_id"),
                {
                    "binding": binding.get("native_family_id"),
                    "package": package.get("native_family_id"),
                },
            )

    # Recompute the summary rather than trusting copied prose.
    published_ids = {
        row.get("package_id")
        for row in packages
        if isinstance(row, dict) and row.get("admission_state") == "published"
    }
    family_ids = {
        row.get("native_family_id")
        for row in packages
        if isinstance(row, dict) and isinstance(row.get("native_family_id"), str)
    }
    published_families = {
        row.get("native_family_id")
        for row in packages
        if isinstance(row, dict)
        and row.get("admission_state") == "published"
        and isinstance(row.get("native_family_id"), str)
    }
    derived_summary = {
        "curriculum_roles": 40,
        "role_bindings": len(bindings),
        "published_role_bindings": sum(
            binding.get("adapter_package_id") in published_ids
            for binding in bindings
            if isinstance(binding, dict)
        ),
        "pending_role_bindings": sum(
            binding.get("adapter_package_id") not in published_ids
            for binding in bindings
            if isinstance(binding, dict)
        ),
        "distinct_adapter_packages": len(packages),
        "published_adapter_packages": len(published_ids),
        "pending_adapter_packages": len(packages) - len(published_ids),
        "represented_native_families": len(family_ids),
        "unbound_roles": 40 - len(bindings),
        "families_without_local_adapter": 33 - len(family_ids),
        "families_without_public_replay_complete_adapter": 33 - len(published_families),
        "package_deduplicated_canonical_records": sum(
            int(row.get("canonical_records", 0))
            for row in packages
            if isinstance(row, dict)
        ),
    }
    book.require("index.summary_recomputed", index.get("summary") == derived_summary, derived_summary)
    state_partition = (
        {"published_adapter_packages": 9, "pending_adapter_packages": 0}
        if derived_summary["pending_adapter_packages"] == 0
        else {"published_adapter_packages": 8, "pending_adapter_packages": 1}
    )
    book.require(
        "index.summary.successor_partition",
        derived_summary["distinct_adapter_packages"] == 9
        and derived_summary["role_bindings"] == 13
        and derived_summary["represented_native_families"] == 9
        and derived_summary["unbound_roles"] == 27
        and derived_summary["families_without_local_adapter"] == 24
        and derived_summary["package_deduplicated_canonical_records"] == 1_487_386
        and derived_summary["published_adapter_packages"] in {8, 9}
        and derived_summary["pending_adapter_packages"] in {0, 1},
        {"actual": derived_summary, "accepted_partition": state_partition},
    )
    return clp_package, index, derived_summary


def normalize_route_kind(row: Mapping[str, Any]) -> str | None:
    raw = row.get("role") or row.get("kind") or row.get("reader_role")
    if not isinstance(raw, str):
        action_id = row.get("action_id")
        raw = action_id.rsplit(":", 1)[-1] if isinstance(action_id, str) else ""
    value = raw.lower().replace("-", "_").replace(" ", "_")
    if "combined" in value:
        return "combined_textbook_problembook"
    if "problem" in value or value in {"exercise", "exercises"}:
        return "problembook"
    if "text" in value or value in {"book", "primary"}:
        return "textbook"
    return None


def validate_sidecar(
    book: CheckBook,
    sidecar: Any,
    index: Mapping[str, Any] | None,
    sidecar_path: Path,
    route_evidence_path: Path | None,
    sealed_route_evidence_path: Path | None,
    sidecar_schema_path: Path | None,
    root: Path,
    require_canonical: bool,
) -> dict[str, Any]:
    if not isinstance(sidecar, dict):
        book.add("sidecar.object", False, "sidecar root is not an object")
        return {}
    book.require(
        "sidecar.schema_identity",
        sidecar.get("schema_id")
        in {
            "interlanguage/learner-reader-actions/v1",
            "interlanguage/program-matematika-indonesia-clp-learner-reader-actions/v1",
        }
        and sidecar.get("schema_version") == "1.0.0",
        {"schema_id": sidecar.get("schema_id"), "schema_version": sidecar.get("schema_version")},
    )
    if sidecar_schema_path is not None:
        schema_check(book, sidecar, sidecar_schema_path, root, "sidecar.schema_validation")
    actions = sidecar.get("actions")
    if actions is None:
        for key in ("routes", "readers", "reader_actions"):
            if isinstance(sidecar.get(key), list):
                actions = sidecar[key]
                break
    if not isinstance(actions, list):
        book.add("sidecar.actions_array", False, "no actions/routes/readers array")
        actions = []
    book.require("sidecar.action_count", len(actions) == 7, {"actual": len(actions), "expected": 7})
    snapshot_id = sidecar.get("snapshot_id")
    index_snapshot = index.get("snapshot", {}).get("snapshot_id") if isinstance(index, dict) else None
    # A compact route projection produced before the adapter snapshot may omit
    # snapshot_id; when present it must bind to the successor index.  The
    # source-evidence field still binds its bytes and route facts below.
    book.require("sidecar.snapshot_match", snapshot_id is None or snapshot_id == index_snapshot, {"sidecar": snapshot_id, "index": index_snapshot})
    book.require("sidecar.locale", sidecar.get("locale") == "id-ID", sidecar.get("locale"))
    source = sidecar.get("source") or sidecar.get("source_evidence")
    book.require("sidecar.source_identity_shape", isinstance(source, dict), source)
    if isinstance(source, dict):
        source_path_value = source.get("path")
        source_path_safe = (
            isinstance(source_path_value, str)
            and not re.match(r"(?i)^(?:[A-Z]:[\\/]|/|\\\\)", source_path_value)
            and not re.search(r"(?i)(?:^|[\\/])outputs[\\/]", source_path_value)
            and ".." not in PurePosixPath(source_path_value.replace("\\", "/")).parts
        )
        book.require("sidecar.source_path_safe", source_path_safe, source_path_value)
        sealed_authority = source.get("sealed_authority")
        direct_identity = (
            source.get("bytes") == CLP_ROUTE_EVIDENCE_BYTES
            and source.get("sha256") == CLP_ROUTE_EVIDENCE_SHA256
        )
        compact_identity = (
            source.get("bytes") == 7_553
            and source.get("sha256")
            == "2b88b7920890ff9b55d7cde6ae4df9052fbf1d22f8a02369f87c0937f2703937"
            and isinstance(sealed_authority, dict)
            and sealed_authority.get("schema_id")
            == "clp-family-v231/learner-primary-route-evidence/v1"
            and sealed_authority.get("bytes") == CLP_ROUTE_EVIDENCE_BYTES
            and sealed_authority.get("sha256") == CLP_ROUTE_EVIDENCE_SHA256
        )
        book.require(
            "sidecar.source_identity_expected",
            direct_identity or compact_identity,
            {"source": source, "direct_identity": direct_identity, "compact_identity": compact_identity},
        )
        replay_path = route_evidence_path
        if replay_path is None and isinstance(source.get("path"), str):
            candidate = Path(source["path"])
            replay_path = candidate if candidate.is_absolute() else root / candidate
        if replay_path is not None and replay_path.is_file():
            size, digest = sha256_file(replay_path)
            expected_source_identity = (
                (7_553, "2b88b7920890ff9b55d7cde6ae4df9052fbf1d22f8a02369f87c0937f2703937")
                if not direct_identity and compact_identity
                else (CLP_ROUTE_EVIDENCE_BYTES, CLP_ROUTE_EVIDENCE_SHA256)
            )
            book.require(
                "sidecar.source_replay",
                (size, digest) == expected_source_identity,
                {"bytes": size, "sha256": digest},
            )
        elif replay_path is not None:
            book.add("sidecar.source_replay", False, f"missing route evidence: {display_path(replay_path, root)}")
        if compact_identity and isinstance(sealed_authority, dict):
            sealed_path = sealed_route_evidence_path
            if sealed_path is not None and sealed_path.is_file():
                sealed_size, sealed_hash = sha256_file(sealed_path)
                book.require(
                    "sidecar.sealed_authority_replay",
                    sealed_size == CLP_ROUTE_EVIDENCE_BYTES
                    and sealed_hash == CLP_ROUTE_EVIDENCE_SHA256,
                    {"bytes": sealed_size, "sha256": sealed_hash},
                )
            elif sealed_path is not None:
                book.add("sidecar.sealed_authority_replay", False, f"missing sealed route evidence: {display_path(sealed_path, root)}")
    seen_keys: set[tuple[str, str]] = set()
    seen_ids: set[str] = set()
    observed_sequence: list[tuple[str, str]] = []
    observed_orders: list[int] = []
    actual_pages = 0
    actual_bytes = 0
    for ordinal, row in enumerate(actions, 1):
        if not isinstance(row, dict):
            book.add(f"sidecar.action.{ordinal}.object", False, "action is not an object")
            continue
        course = row.get("course_id") or row.get("role_id")
        kind = normalize_route_kind(row)
        key = (course, kind) if isinstance(course, str) and kind else ("?", "?")
        if isinstance(row.get("action_id"), str):
            action_id = row["action_id"]
            book.require(f"sidecar.action.{ordinal}.id_unique", action_id not in seen_ids, action_id)
            seen_ids.add(action_id)
        book.require(
            f"sidecar.action.{ordinal}.required_shape",
            isinstance(row.get("action_id"), str)
            and isinstance(row.get("order"), int)
            and row.get("order", 0) > 0
            and isinstance(row.get("pages"), int)
            and row.get("pages", 0) > 0
            and isinstance(row.get("bytes"), int)
            and row.get("bytes", 0) > 0
            and isinstance(row.get("sha256"), str)
            and bool(re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", ""))),
            {"action_id": row.get("action_id"), "order": row.get("order"), "pages": row.get("pages"), "bytes": row.get("bytes")},
        )
        book.require(f"sidecar.action.{ordinal}.course", course in CLP_ROLES, course)
        book.require(f"sidecar.action.{ordinal}.kind", key in EXPECTED_ROUTES, key)
        if key in seen_keys:
            book.add(f"sidecar.action.{ordinal}.unique_route", False, key)
        seen_keys.add(key)
        observed_sequence.append(key)
        if isinstance(row.get("order"), int):
            observed_orders.append(row["order"])
        expected = EXPECTED_ROUTES.get(key)
        if expected:
            for field in ("pages", "bytes", "sha256", "url"):
                book.require(
                    f"sidecar.action.{ordinal}.{field}",
                    row.get(field) == expected[field],
                    {"actual": row.get(field), "expected": expected[field]},
                )
            actual_pages += int(row.get("pages", 0)) if isinstance(row.get("pages"), int) else 0
            actual_bytes += int(row.get("bytes", 0)) if isinstance(row.get("bytes"), int) else 0
        parsed_url = urlparse(str(row.get("url", "")))
        book.require(
            f"sidecar.action.{ordinal}.https_url",
            parsed_url.scheme == "https" and bool(parsed_url.netloc),
            row.get("url"),
        )
        for field, expected_value in {
            "format": "application/pdf",
            "route_granularity": "whole_file_only",
        }.items():
            book.require(f"sidecar.action.{ordinal}.{field}", row.get(field) == expected_value, row.get(field))
        if "anchor_status" in row:
            book.require(
                f"sidecar.action.{ordinal}.anchor_status",
                row.get("anchor_status") in {"not_established", "not_claimed"},
                row.get("anchor_status"),
            )
        evidence = row.get("evidence")
        book.require(f"sidecar.action.{ordinal}.evidence", isinstance(evidence, dict), evidence)
        if isinstance(evidence, dict):
            book.require(
                f"sidecar.action.{ordinal}.evidence_status",
                evidence.get("status") in {"pass_receipt_bound", "pass", "verified", "pass_public_readback"},
                evidence.get("status"),
            )
            book.require(
                f"sidecar.action.{ordinal}.evidence_locator",
                isinstance(evidence.get("locator"), str)
                and urlparse(evidence.get("locator", "")).scheme == "https",
                evidence.get("locator"),
            )
    book.require("sidecar.route_key_set", seen_keys == set(EXPECTED_ROUTES), {"actual": sorted(seen_keys), "expected": sorted(EXPECTED_ROUTES)})
    book.require("sidecar.route_order", observed_sequence == EXPECTED_ROUTE_SEQUENCE, {"actual": observed_sequence, "expected": EXPECTED_ROUTE_SEQUENCE})
    book.require("sidecar.order_values", observed_orders == list(range(1, 8)), {"actual": observed_orders, "expected": list(range(1, 8))})
    summary = sidecar.get("summary") or sidecar.get("totals")
    expected_summary = {"course_count": 4, "action_count": 7, "pages": 4_077, "bytes": 35_639_691}
    summary_normalized = dict(summary) if isinstance(summary, dict) else {}
    if "reader_actions" in summary_normalized and "action_count" not in summary_normalized:
        summary_normalized["action_count"] = summary_normalized["reader_actions"]
    if "verified_action_count" in summary_normalized and "action_count" not in summary_normalized:
        summary_normalized["action_count"] = summary_normalized["verified_action_count"]
    if "courses" in summary_normalized and "course_count" not in summary_normalized:
        summary_normalized["course_count"] = summary_normalized["courses"]
    book.require("sidecar.summary", isinstance(summary, dict) and all(summary_normalized.get(k) == v for k, v in expected_summary.items()), {"actual": summary, "expected": expected_summary})
    book.require("sidecar.recomputed_totals", actual_pages == 4_077 and actual_bytes == 35_639_691, {"pages": actual_pages, "bytes": actual_bytes})
    if require_canonical:
        book.require("sidecar.canonical_json", sidecar_path.read_bytes() == canonical_json_bytes(sidecar), display_path(sidecar_path, root))
    return {"action_count": len(actions), "pages": actual_pages, "bytes": actual_bytes, "route_keys": sorted(seen_keys)}


def manifest_from_package_or_zip(
    clp_package: Mapping[str, Any] | None,
    root: Path,
    archive_path: Path,
    explicit_manifest: Path | None,
) -> tuple[Path | None, dict[str, Any] | None]:
    candidates: list[Path] = []
    if explicit_manifest is not None:
        candidates.append(explicit_manifest if explicit_manifest.is_absolute() else root / explicit_manifest)
    if clp_package and isinstance(clp_package.get("manifest"), dict):
        raw = clp_package["manifest"].get("path")
        if isinstance(raw, str):
            candidate = Path(raw)
            candidates.append(candidate if candidate.is_absolute() else root / candidate)
    for candidate in candidates:
        if candidate.is_file():
            try:
                value = load_json(candidate)
                return candidate, value if isinstance(value, dict) else None
            except Exception:
                return candidate, None
    return None, None


def validate_archive(
    book: CheckBook,
    archive_path: Path,
    clp_package: Mapping[str, Any] | None,
    root: Path,
    expected_members: int,
    expected_uncompressed: int,
    explicit_manifest: Path | None,
) -> dict[str, Any]:
    if not archive_path.is_file():
        book.add("archive.present", False, display_path(archive_path, root))
        return {}
    book.add("archive.present", True, display_path(archive_path, root))
    try:
        size, digest = sha256_file(archive_path)
        book.require("archive.outer_identity", size == CLP_ARCHIVE_BYTES and digest == CLP_ARCHIVE_SHA256, {"bytes": size, "sha256": digest})
        if clp_package and isinstance(clp_package.get("archive"), dict):
            fact = clp_package["archive"]
            book.require("archive.matches_index_fact", size == fact.get("bytes") and digest == fact.get("sha256"), {"actual": {"bytes": size, "sha256": digest}, "index": fact})
    except OSError as exc:
        book.add("archive.outer_identity", False, str(exc))
        return {}

    member_facts: list[dict[str, Any]] = []
    member_info: dict[str, zipfile.ZipInfo] = {}
    total_uncompressed = 0
    unsafe: list[str] = []
    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            infos = zf.infolist()
            book.require("archive.member_count", expected_members == 0 or len(infos) == expected_members, {"actual": len(infos), "expected": expected_members})
            normalized_seen: set[str] = set()
            for info in infos:
                ok, normalized = safe_member_name(info.filename)
                if not ok:
                    unsafe.append(f"{info.filename}: {normalized}")
                    continue
                if normalized in normalized_seen:
                    unsafe.append(f"{info.filename}: duplicate normalized name")
                    continue
                normalized_seen.add(normalized)
                member_info[normalized] = info
                if info.flag_bits & 0x1:
                    unsafe.append(f"{info.filename}: encrypted")
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_IFMT(mode) == stat.S_IFLNK:
                    unsafe.append(f"{info.filename}: symbolic link")
                total_uncompressed += int(info.file_size)
            book.require("archive.member_names_safe", not unsafe, unsafe[:20])
            if expected_uncompressed:
                book.require("archive.central_directory_uncompressed_sum", total_uncompressed == expected_uncompressed, {"actual": total_uncompressed, "expected": expected_uncompressed})
            # Fail closed before reading a declared over-sized archive.
            if expected_uncompressed and total_uncompressed > expected_uncompressed:
                return {"member_count": len(infos), "uncompressed_bytes": total_uncompressed, "member_facts": []}
            for name in sorted(member_info):
                info = member_info[name]
                digest_member = hashlib.sha256()
                read_bytes = 0
                try:
                    with zf.open(info, "r") as stream:
                        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                            read_bytes += len(chunk)
                            digest_member.update(chunk)
                except Exception as exc:
                    unsafe.append(f"{name}: member read/CRC failure: {exc}")
                    continue
                book.require(f"archive.member_size.{name}", read_bytes == info.file_size, {"actual": read_bytes, "expected": info.file_size})
                member_facts.append({"path": name, "bytes": read_bytes, "sha256": digest_member.hexdigest()})
            book.require("archive.member_read_crc", not any("CRC failure" in row for row in unsafe), [row for row in unsafe if "CRC failure" in row][:20])
            member_names = set(member_info)
            book.require("archive.control_members", CONTROL_MEMBERS <= member_names, {"missing": sorted(CONTROL_MEMBERS - member_names)})
            # Parse the control members after content hashes have been recorded.
            def read_control(name: str) -> Any:
                with zf.open(member_info[name], "r") as stream:
                    return json.load(stream, object_pairs_hook=_unique_object)

            manifest_member = None
            seal_member = None
            checksum_text = None
            if "manifest.json" in member_info:
                try:
                    value = read_control("manifest.json")
                    manifest_member = value if isinstance(value, dict) else None
                except Exception as exc:
                    book.add("archive.manifest_member_json", False, str(exc))
            if "seal.json" in member_info:
                try:
                    value = read_control("seal.json")
                    seal_member = value if isinstance(value, dict) else None
                except Exception as exc:
                    book.add("archive.seal_member_json", False, str(exc))
            if "PACKAGE_CHECKSUMS.sha256" in member_info:
                try:
                    with zf.open(member_info["PACKAGE_CHECKSUMS.sha256"], "r") as stream:
                        checksum_text = stream.read().decode("utf-8")
                except Exception as exc:
                    book.add("archive.checksum_member", False, str(exc))

            manifest_path, manifest_local = manifest_from_package_or_zip(clp_package, root, archive_path, explicit_manifest)
            manifest = manifest_local or manifest_member
            book.require("archive.manifest_present", isinstance(manifest, dict), display_path(manifest_path, root) if manifest_path else "manifest.json member")
            if isinstance(manifest, dict):
                book.require("archive.manifest_package_id", manifest.get("package_id") == CLP_PACKAGE_ID, manifest.get("package_id"))
                files = manifest.get("files")
                book.require("archive.manifest_file_count", isinstance(files, list) and len(files) == 67, len(files) if isinstance(files, list) else None)
                manifest_facts = [
                    {"path": row.get("path"), "bytes": row.get("bytes"), "sha256": row.get("sha256")}
                    for row in files or []
                    if isinstance(row, dict)
                ]
                payload_facts = [row for row in member_facts if row["path"] not in CONTROL_MEMBERS]
                book.require("archive.manifest_member_set", {row["path"] for row in manifest_facts} == {row["path"] for row in payload_facts}, {"manifest_only": sorted({row["path"] for row in manifest_facts} - {row["path"] for row in payload_facts})[:10], "zip_only": sorted({row["path"] for row in payload_facts} - {row["path"] for row in manifest_facts})[:10]})
                by_name = {row["path"]: row for row in member_facts}
                for row in manifest_facts:
                    actual = by_name.get(row["path"])
                    book.require(f"archive.manifest_fact.{row['path']}", actual is not None and actual["bytes"] == row["bytes"] and actual["sha256"] == row["sha256"], {"actual": actual, "manifest": row})
                if manifest_member is not None:
                    embedded = next((row for row in member_facts if row["path"] == "manifest.json"), None)
                    book.require("archive.manifest_identity", embedded is not None and embedded["bytes"] == CLP_MANIFEST_BYTES and embedded["sha256"] == CLP_MANIFEST_SHA256, embedded)
                if manifest_path and manifest_local is not None:
                    local_size, local_hash = sha256_file(manifest_path)
                    book.require("archive.staged_manifest_identity", local_size == CLP_MANIFEST_BYTES and local_hash == CLP_MANIFEST_SHA256, {"bytes": local_size, "sha256": local_hash})

            non_control_facts = [row for row in member_facts if row["path"] not in {"seal.json", "PACKAGE_CHECKSUMS.sha256"}]
            if isinstance(seal_member, dict):
                book.require("archive.seal_file_count", seal_member.get("file_count") == len(non_control_facts), {"actual": seal_member.get("file_count"), "expected": len(non_control_facts)})
                book.require("archive.seal_bytes", seal_member.get("bytes") == sum(row["bytes"] for row in non_control_facts), {"actual": seal_member.get("bytes"), "expected": sum(row["bytes"] for row in non_control_facts)})
                book.require("archive.seal_aggregate", seal_member.get("aggregate_sha256") == inventory_sha256(non_control_facts), {"actual": seal_member.get("aggregate_sha256"), "expected": inventory_sha256(non_control_facts)})
            if checksum_text is not None:
                checksum_rows: list[dict[str, Any]] = []
                malformed = []
                for ordinal, line in enumerate(checksum_text.splitlines(), 1):
                    if len(line) < 67 or line[64:66] != "  ":
                        malformed.append(ordinal)
                        continue
                    checksum_rows.append({"sha256": line[:64], "path": line[66:]})
                checksum_expected_count = len(member_facts) - 1  # omit only PACKAGE_CHECKSUMS.sha256 itself
                book.require("archive.checksum_format", not malformed and len(checksum_rows) == checksum_expected_count, {"malformed_lines": malformed[:20], "rows": len(checksum_rows), "expected": checksum_expected_count})
                book.require("archive.checksum_order", [row["path"] for row in checksum_rows] == sorted(row["path"] for row in checksum_rows), [row["path"] for row in checksum_rows[:10]])
                # The package builder writes the checksum file after seal.json
                # exists, so its closure contains the seal as well as the 68
                # seal-bound payload/manifest facts.  It excludes only itself.
                checksum_facts = [
                    row for row in member_facts if row["path"] != "PACKAGE_CHECKSUMS.sha256"
                ]
                expected_checksums = {(row["path"], row["sha256"]) for row in checksum_facts}
                actual_checksums = {(row["path"], row["sha256"]) for row in checksum_rows}
                book.require("archive.checksum_identity", actual_checksums == expected_checksums, {"missing": sorted(expected_checksums - actual_checksums)[:10], "extra": sorted(actual_checksums - expected_checksums)[:10]})
    except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
        book.add("archive.open_and_replay", False, str(exc))
        return {}
    return {"bytes": size, "sha256": digest, "member_count": len(member_info), "uncompressed_bytes": total_uncompressed, "member_facts": member_facts}


def scan_public_text(book: CheckBook, path: Path, root: Path, check_id: str) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        book.add(check_id, False, str(exc))
        return
    forbidden = []
    patterns = {
        "absolute_windows_path": r"(?i)(?:[A-Z]:\\|\\\\)",
        "private_unix_path": r"(?:/Users/|/home/)",
        "workspace_outputs_path": r"(?i)(?:^|[\\/])outputs[\\/]",
        "credential_like": r"(?i)(?:ghp_[A-Za-z0-9_\-]+|github_pat_[A-Za-z0-9_\-]+|access[_-]?token|api[_-]?key|secret)" ,
    }
    for label, pattern in patterns.items():
        if re.search(pattern, text):
            forbidden.append(label)
    book.require(check_id, not forbidden, {"forbidden_patterns": forbidden})


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    index_path = resolve_path(root, args.index, DEFAULT_INDEX)
    sidecar_path = resolve_path(root, args.sidecar, DEFAULT_SIDECAR)
    archive_path = resolve_path(root, args.archive, DEFAULT_ARCHIVE)
    schema_path = None if args.no_schema else resolve_path(root, args.schema, DEFAULT_SCHEMA)
    if args.no_schema:
        sidecar_schema_path = None
    elif args.sidecar_schema is not None:
        sidecar_schema_path = resolve_path(root, args.sidecar_schema, Path())
    else:
        auto_sidecar_schema = root / "schemas/v1/learner-reader-actions-v1.schema.json"
        sidecar_schema_path = auto_sidecar_schema if auto_sidecar_schema.is_file() else None
    manifest_path = resolve_path(root, args.manifest, Path()) if args.manifest is not None else None
    route_evidence_path = resolve_path(root, args.route_evidence, Path()) if args.route_evidence is not None else None
    sealed_route_evidence_path = resolve_path(root, args.sealed_route_evidence, Path()) if args.sealed_route_evidence is not None else None
    book = CheckBook()
    index: Any = None
    sidecar: Any = None
    if index_path.is_file():
        try:
            index = load_json(index_path)
            book.add("index.json_parse", True, display_path(index_path, root))
        except Exception as exc:
            book.add("index.json_parse", False, str(exc))
    else:
        book.add("index.present", False, display_path(index_path, root))
    if sidecar_path.is_file():
        try:
            sidecar = load_json(sidecar_path)
            book.add("sidecar.json_parse", True, display_path(sidecar_path, root))
        except Exception as exc:
            book.add("sidecar.json_parse", False, str(exc))
    else:
        book.add("sidecar.present", False, display_path(sidecar_path, root))

    clp_package = None
    derived_summary: dict[str, Any] = {}
    if index is not None:
        schema_check(book, index, schema_path, root)
        if args.require_canonical_json:
            book.require("index.canonical_json", index_path.read_bytes() == canonical_json_bytes(index), display_path(index_path, root))
        clp_package, _, derived_summary = validate_index(book, index, args, index_path, root)
        scan_public_text(book, index_path, root, "index.public_text_safety")
    if sidecar is not None:
        sidecar_summary = validate_sidecar(book, sidecar, index if isinstance(index, dict) else None, sidecar_path, route_evidence_path, sealed_route_evidence_path, sidecar_schema_path, root, args.require_canonical_json)
        scan_public_text(book, sidecar_path, root, "sidecar.public_text_safety")
    else:
        sidecar_summary = {}
    archive_summary = validate_archive(book, archive_path, clp_package, root, args.expected_members, args.expected_uncompressed_bytes, manifest_path)
    result = {
        "schema_id": "interlanguage/program-matematika-indonesia-clp-successor-validation/v1",
        "validator_version": VALIDATOR_VERSION,
        "status": "fail" if book.failed else "pass",
        "inputs": {
            "root": "repository-root",
            "index": display_path(index_path, root),
            "sidecar": display_path(sidecar_path, root),
            "archive": display_path(archive_path, root),
            "manifest": display_path(manifest_path, root) if manifest_path else None,
            "route_evidence": display_path(route_evidence_path, root) if route_evidence_path else None,
            "sealed_route_evidence": display_path(sealed_route_evidence_path, root) if sealed_route_evidence_path else None,
        },
        "derived": {
            "index_summary": derived_summary,
            "sidecar": sidecar_summary,
            "archive": {key: value for key, value in archive_summary.items() if key != "member_facts"},
        },
        "checks": book.ordered(),
    }
    # A second serialization pass is deliberately part of the validator: the
    # receipt must be byte-stable for identical inputs and options.
    first = canonical_json_bytes(result)
    second = canonical_json_bytes(json.loads(first.decode("utf-8")))
    result["deterministic_output"] = {"canonical": True, "replay_byte_identical": first == second}
    if not result["deterministic_output"]["replay_byte_identical"]:
        result["status"] = "fail"
    output = canonical_json_bytes(result)
    if args.output is not None:
        output_path = args.output if args.output.is_absolute() else root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(output)
    sys.stdout.write(output.decode("utf-8"))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
