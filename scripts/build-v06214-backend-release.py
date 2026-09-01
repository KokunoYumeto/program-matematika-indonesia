#!/usr/bin/env python3
"""Preflight or assemble the exact 112-file PMI v0.62.14 release.

This successor deliberately inherits the hardened primitives of the immutable
v0.62.13 builder while defining a new, finite release boundary:

* retain 91 files byte-for-byte from the verified public v0.62.13 payload;
* replace six predecessor filenames with commit-bound v0.62.14 bytes;
* omit only the three superseded v0.62.13 versioned release files;
* add fifteen new names, including the admitted C130 package and v2 snapshot;
* generate a deterministic source ZIP from a mandatory commit/tree pair; and
* generate a 111-row checksum manifest covering every file except itself.

No publication operation exists in this script.  The only network-capable mode
is anonymous predecessor hydration, which is bounded by the pinned v0.62.13
publication receipt and refuses to overwrite an existing predecessor path.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import stat
import sys
import tempfile
import types
import zipfile
from http.client import HTTPException
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import ProxyHandler, Request, build_opener


VERSION = "0.62.14"
PREDECESSOR_VERSION = "0.62.13"
EXPECTED_FILES = 112
EXPECTED_PREDECESSOR_FILES = 100
EXPECTED_RETAINED = 91
EXPECTED_REPLACEMENTS = 6
EXPECTED_PURE_OMISSIONS = 3
EXPECTED_PURE_ADDITIONS = 15
EXPECTED_CHECKSUM_ROWS = EXPECTED_FILES - 1

PROJECT = Path(__file__).resolve().parents[1]
RELEASES_DIR = PROJECT / "releases"
PREDECESSOR_DIR = RELEASES_DIR / f"v{PREDECESSOR_VERSION}"
OUTPUT_DIR = RELEASES_DIR / f"v{VERSION}"
PREDECESSOR_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.13.json"
PREDECESSOR_GITHUB_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.13.json"

EXPECTED_TEMPLATE = (
    119_811,
    "80d5523795958b7e3efca9fac1b0e00eac82323a8b264938f006bca19c133c31",
)
EXPECTED_PREDECESSOR_RECEIPT = (
    59_438,
    "e6d59a7a13409afeab90034f1587d067a46106164fac079ec39903f1f899b4cf",
)
EXPECTED_PREDECESSOR_GITHUB_RECEIPT = (
    86_823,
    "5c372b903dfe9cf374c66c3499e527793576059b723c9de97261996eeb75d27f",
)
EXPECTED_PREDECESSOR_TOTAL_BYTES = 460_869_686
EXPECTED_PREDECESSOR_AGGREGATE = (
    "fa645e4b54973bc750ec6734a3195e22a0ade1d38cbf7f6497c4c1cbab4103ec"
)
EXPECTED_PREDECESSOR_RECORD_ID = 22_207_081
EXPECTED_PREDECESSOR_TAG_COMMIT = "4ab6eb6b270dc0a32512dad3f998653c336d8492"
EXPECTED_PREDECESSOR_TAG_TREE = "268dae1dc622ecdd6290d64a0695388f8800d7a7"
EXPECTED_CONCEPT_ID = 22_059_707
EXPECTED_CONCEPT_DOI = "10.5281/zenodo.22059707"
EXPECTED_PREDECESSOR_DOI = "10.5281/zenodo.22207081"
EXPECTED_PREDECESSOR_STATE = "published_open_modular_backend_successor"
EXPECTED_PREDECESSOR_RELEASE_ID = 379_701_122

SOURCE_ZIP_NAME = "program-matematika-indonesia-source-v0.62.14.zip"
NOTES_NAME = "RELEASE_NOTES_v0.62.14.md"
CHECKSUM_NAME = "RELEASE_CHECKSUMS_v0.62.14.sha256"
COURSE_CAPSULE_ARCHIVE_NAME = "program-matematika-indonesia-course-capsule-v1.zip"
C130_ARCHIVE_NAME = "program-matematika-indonesia-c130-operations-research-v2.3.1.zip"

# Freeze this after the final combined capsule package has been produced.  It
# is intentionally fail-closed rather than accepting an unbounded ZIP tree.
EXPECTED_COURSE_CAPSULE_MEMBER_COUNT: int | None = 326

TEMPLATE_PATH = PROJECT / "scripts/build-v06213-backend-release.py"


def _load_template() -> types.ModuleType:
    data = TEMPLATE_PATH.read_bytes()
    identity = (len(data), hashlib.sha256(data).hexdigest())
    if identity != EXPECTED_TEMPLATE:
        raise RuntimeError("v0.62.13 builder template identity differs")
    module = types.ModuleType("pmi_v06213_release_builder_template")
    module.__file__ = str(TEMPLATE_PATH)
    module.__name__ = "pmi_v06213_release_builder_template"
    exec(compile(data, str(TEMPLATE_PATH), "exec"), module.__dict__)
    module.SOURCE_ZIP_NAME = SOURCE_ZIP_NAME
    return module


legacy = _load_template()
BuildError = legacy.BuildError
require = legacy.require
sha256 = legacy.sha256
safe_flat_name = legacy.safe_flat_name
relative_display = legacy.relative_display
fact = legacy.fact
inventory_aggregate = legacy.inventory_aggregate
privacy_scan = legacy.privacy_scan
validate_json = legacy.validate_json
validate_jsonl = legacy.validate_jsonl
validate_zip = legacy.validate_zip
validate_source_authority = legacy.validate_source_authority
require_committed_bytes = legacy.require_committed_bytes
build_source_archive = legacy.build_source_archive


SAME_NAME_REPLACEMENTS = frozenset(
    {
        "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md",
        "course-capsule-v1.schema.json",
        "course-capsules-v1.jsonl",
        "learner-delivery-v1.json",
        "peta-belajar-luring.html",
        COURSE_CAPSULE_ARCHIVE_NAME,
    }
)

PURE_OMISSIONS = frozenset(
    {
        "RELEASE_CHECKSUMS_v0.62.13.sha256",
        "RELEASE_NOTES_v0.62.13.md",
        "program-matematika-indonesia-source-v0.62.13.zip",
    }
)

PURE_ADDITIONS = frozenset(
    {
        CHECKSUM_NAME,
        NOTES_NAME,
        SOURCE_ZIP_NAME,
        "program-matematika-indonesia-judson-c30-c40-v2.3.1.zip",
        "program-matematika-indonesia-openlogic-c80-v2.3.1.zip",
        C130_ARCHIVE_NAME,
        "v23-adapter-index-v2.json",
        "v23-adapter-index-v2.schema.json",
        "modular-backend-pattern-index-v2.json",
        "modular-backend-pattern-index-v2.schema.json",
        "feature-adoption-provenance-v1.json",
        "feature-adoption-provenance-v1.schema.json",
        "comparison-evidence-manifest-v1.json",
        "comparison-evidence-manifest-v1.schema.json",
        "MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json",
    }
)

REPLACEMENT_SOURCES = {
    "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md": PROJECT
    / "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md",
    "course-capsule-v1.schema.json": PROJECT
    / "docs/schema/course-capsule-v1/course-capsule-v1.schema.json",
    "course-capsules-v1.jsonl": PROJECT
    / "backend/course-capsule-v1/generated/course-capsules.jsonl",
    "learner-delivery-v1.json": PROJECT / "backend/authority/learner-delivery-v1.json",
    "peta-belajar-luring.html": PROJECT / "docs/peta-belajar-luring.html",
    COURSE_CAPSULE_ARCHIVE_NAME: PROJECT
    / "backend/course-capsule-v1/builds/program-matematika-indonesia-course-capsule-v1.zip",
}

PREPARED_ADDITION_SOURCES = {
    "program-matematika-indonesia-judson-c30-c40-v2.3.1.zip": PROJECT
    / "backend/course-capsule-v1/builds/program-matematika-indonesia-judson-c30-c40-v2.3.1.zip",
    "program-matematika-indonesia-openlogic-c80-v2.3.1.zip": PROJECT
    / "backend/course-capsule-v1/builds/program-matematika-indonesia-openlogic-c80-v2.3.1.zip",
    C130_ARCHIVE_NAME: PROJECT
    / "backend/course-capsule-v1/builds/program-matematika-indonesia-c130-operations-research-v2.3.1.zip",
    "v23-adapter-index-v2.json": PROJECT
    / "backend/course-capsule-v1/authority/v23-adapter-index-v2.json",
    "v23-adapter-index-v2.schema.json": PROJECT
    / "schemas/course-capsule-v1/v2/v23-adapter-index-v2.schema.json",
    "modular-backend-pattern-index-v2.json": PROJECT
    / "backend/course-capsule-v1/authority/modular-backend-pattern-index-v2.json",
    "modular-backend-pattern-index-v2.schema.json": PROJECT
    / "schemas/course-capsule-v1/v2/modular-backend-pattern-index-v2.schema.json",
    "feature-adoption-provenance-v1.json": PROJECT
    / "backend/course-capsule-v1/authority/feature-adoption-provenance-v1.json",
    "feature-adoption-provenance-v1.schema.json": PROJECT
    / "schemas/course-capsule-v1/v2/feature-adoption-provenance-v1.schema.json",
    "comparison-evidence-manifest-v1.json": PROJECT
    / "backend/course-capsule-v1/authority/comparison-evidence-manifest-v1.json",
    "comparison-evidence-manifest-v1.schema.json": PROJECT
    / "schemas/course-capsule-v1/v2/comparison-evidence-manifest-v1.schema.json",
    "MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json": PROJECT
    / "backend/course-capsule-v1/validation/MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json",
}

EXPECTED_ADAPTER_ROLE_ORDER = (
    "A00",
    "B10",
    "C30",
    "C40",
    "C80",
    "C130",
    "D20",
    "D60",
    "D110",
)
EXPECTED_V2_SUMMARY = {
    "curriculum_roles": 40,
    "distinct_adapter_packages": 8,
    "families_without_local_adapter": 25,
    "families_without_public_replay_complete_adapter": 28,
    "package_deduplicated_canonical_records": 285_829,
    "pending_adapter_packages": 3,
    "pending_role_bindings": 4,
    "published_adapter_packages": 5,
    "published_role_bindings": 5,
    "represented_native_families": 8,
    "role_bindings": 9,
    "unbound_roles": 31,
}
EXPECTED_C130_PACKAGE_ID = "urn:uuid:a84539b5-455b-5baf-89a4-f4c0336e33ab"
EXPECTED_C130_DATASET_ID = "urn:uuid:2e16c60d-7ee3-52f4-9c05-2c4dea0b07ca"
EXPECTED_C130_EXTENSION_ID = "urn:uuid:d46eb7f0-cab9-5646-89cb-e4e82394c344"
EXPECTED_C130_ARCHIVE = (
    21_213_937,
    "eb195d1aa555e9d5e639c1e35a08b6f4425be24cc93b7f1f633161e9cacee865",
)
EXPECTED_TERMINOLOGY_POLICY = (
    20_125,
    "c3bc63376dfeac2427703cc53635c50418c1a5db93abe3074ad65aa760b1acaa",
)
EXPECTED_C130_ADMISSION = (
    4_889,
    "b311ab7d2a6a86af40174d051fbd8ef273a8536b34f0af77b76e5a1ce9b3397e",
)
EXPECTED_C130_MANIFEST = (
    22_488,
    "cad2922d9bd1facb33cc9d54a9836bb168fe0b8d996d9d4ef2e5d8c26053f239",
)
EXPECTED_C130_OWNER_COMMIT = "a639b69cf84c4d4f60f7dcdb62dbeb5cfb153adc"
EXPECTED_C130_OWNER_TREE = "1ab559b3540d9362bc0333caf017acd9fe540a9c"
C130_ADMISSION_PATH = PROJECT / "backend/course-capsule-v1/adapters/c130-v231/ADMISSION.json"
C130_MANIFEST_PATH = PROJECT / "backend/course-capsule-v1/adapters/c130-v231/manifest.json"

V2_VALIDATED_SOURCE_PATHS = {
    "backend/course-capsule-v1/authority/v23-adapter-index-v2.json": PREPARED_ADDITION_SOURCES[
        "v23-adapter-index-v2.json"
    ],
    "backend/course-capsule-v1/authority/modular-backend-pattern-index-v2.json": PREPARED_ADDITION_SOURCES[
        "modular-backend-pattern-index-v2.json"
    ],
    "backend/course-capsule-v1/authority/feature-adoption-provenance-v1.json": PREPARED_ADDITION_SOURCES[
        "feature-adoption-provenance-v1.json"
    ],
    "backend/course-capsule-v1/authority/comparison-evidence-manifest-v1.json": PREPARED_ADDITION_SOURCES[
        "comparison-evidence-manifest-v1.json"
    ],
    "schemas/course-capsule-v1/v2/v23-adapter-index-v2.schema.json": PREPARED_ADDITION_SOURCES[
        "v23-adapter-index-v2.schema.json"
    ],
    "schemas/course-capsule-v1/v2/modular-backend-pattern-index-v2.schema.json": PREPARED_ADDITION_SOURCES[
        "modular-backend-pattern-index-v2.schema.json"
    ],
    "schemas/course-capsule-v1/v2/feature-adoption-provenance-v1.schema.json": PREPARED_ADDITION_SOURCES[
        "feature-adoption-provenance-v1.schema.json"
    ],
    "schemas/course-capsule-v1/v2/comparison-evidence-manifest-v1.schema.json": PREPARED_ADDITION_SOURCES[
        "comparison-evidence-manifest-v1.schema.json"
    ],
}

CAPSULE_REQUIRED_MEMBERS = frozenset(
    {
        "backend/course-capsule-v1/generated/course-capsules.jsonl",
        "docs/data/course-capsule-v1/course-capsules.jsonl",
        "backend/course-capsule-v1/generated/manifest.json",
        "docs/data/course-capsule-v1/manifest.json",
        "backend/course-capsule-v1/validation/VALIDATION_RECEIPT.json",
        "docs/data/course-capsule-v1/validation-receipt.json",
        "backend/course-capsule-v1/authority/public-baseline-v0.62.12.json",
        "docs/data/course-capsule-v1/public-baseline-v0.62.12.json",
        "backend/course-capsule-v1/authority/v23-adapter-index-v2.json",
        "docs/data/v23-adapter-index-v2.json",
        "backend/course-capsule-v1/authority/modular-backend-pattern-index-v2.json",
        "docs/data/modular-backend-pattern-index-v2.json",
        "backend/course-capsule-v1/authority/feature-adoption-provenance-v1.json",
        "docs/data/feature-adoption-provenance-v1.json",
        "backend/course-capsule-v1/authority/comparison-evidence-manifest-v1.json",
        "docs/data/comparison-evidence-manifest-v1.json",
        "backend/course-capsule-v1/authority/terminology-policy-v1/README.md",
        "docs/data/course-capsule-v1/terminology-policy-v1/README.md",
        "backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json",
        "docs/data/course-capsule-v1/terminology-policy-v1/canonical-register-policy.json",
        "backend/course-capsule-v1/authority/terminology-policy-v1/checksums.sha256",
        "docs/data/course-capsule-v1/terminology-policy-v1/checksums.sha256",
        "schemas/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json",
        "docs/schema/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json",
        "schemas/course-capsule-v1/v2/terminology-concept-record-v1.schema.json",
        "docs/schema/course-capsule-v1/v2/terminology-concept-record-v1.schema.json",
        "backend/course-capsule-v1/validation/MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json",
        "backend/course-capsule-v1/adapters/c130-v231/ADMISSION.json",
        "backend/course-capsule-v1/adapters/c130-v231/manifest.json",
        "backend/course-capsule-v1/builds/program-matematika-indonesia-judson-c30-c40-v2.3.1.zip",
        "backend/course-capsule-v1/builds/program-matematika-indonesia-openlogic-c80-v2.3.1.zip",
        "backend/course-capsule-v1/builds/program-matematika-indonesia-c130-operations-research-v2.3.1.zip",
    }
)

PREDECESSOR_ANONYMOUS_URL_ROOT = (
    f"https://zenodo.org/api/records/{EXPECTED_PREDECESSOR_RECORD_ID}/files"
)
HYDRATION_PREFIX = ".v0.62.13-hydrate-v06214-"
BUILD_PREFIX = ".v0.62.14-build-"


def _strict_object(path: Path, label: str) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), f"{label} is missing or symlinked")
    value = validate_json(label, path.read_bytes())
    require(isinstance(value, dict), f"{label} is not a JSON object")
    return value


def _identity(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), sha256(data)


def _validate_boundary(predecessor_names: set[str]) -> frozenset[str]:
    require(len(predecessor_names) == EXPECTED_PREDECESSOR_FILES, "predecessor name count differs")
    require(len(SAME_NAME_REPLACEMENTS) == EXPECTED_REPLACEMENTS, "replacement count differs")
    require(len(PURE_OMISSIONS) == EXPECTED_PURE_OMISSIONS, "omission count differs")
    require(len(PURE_ADDITIONS) == EXPECTED_PURE_ADDITIONS, "addition count differs")
    require(set(REPLACEMENT_SOURCES) == SAME_NAME_REPLACEMENTS, "replacement source map differs")
    require(
        set(PREPARED_ADDITION_SOURCES) == PURE_ADDITIONS - {SOURCE_ZIP_NAME, NOTES_NAME, CHECKSUM_NAME},
        "prepared addition source map differs",
    )
    require(SAME_NAME_REPLACEMENTS <= predecessor_names, "replacement absent from predecessor")
    require(PURE_OMISSIONS <= predecessor_names, "omission absent from predecessor")
    require(PURE_ADDITIONS.isdisjoint(predecessor_names), "pure addition collides with predecessor")
    require(SAME_NAME_REPLACEMENTS.isdisjoint(PURE_OMISSIONS), "replacement/omission overlap")
    retained = frozenset(predecessor_names - SAME_NAME_REPLACEMENTS - PURE_OMISSIONS)
    require(len(retained) == EXPECTED_RETAINED, "retained count differs")
    successor = retained | SAME_NAME_REPLACEMENTS | PURE_ADDITIONS
    require(len(successor) == EXPECTED_FILES, "91+6+15 successor equation differs")
    require(PURE_OMISSIONS.isdisjoint(successor), "pure omission survived successor")
    for name in predecessor_names | set(PURE_ADDITIONS):
        safe_flat_name(name)
    return retained


def _predecessor_inventory() -> tuple[dict[str, dict[str, Any]], frozenset[str]]:
    require(_identity(PREDECESSOR_RECEIPT) == EXPECTED_PREDECESSOR_RECEIPT, "predecessor receipt identity differs")
    require(
        _identity(PREDECESSOR_GITHUB_RECEIPT) == EXPECTED_PREDECESSOR_GITHUB_RECEIPT,
        "predecessor GitHub receipt identity differs",
    )
    receipt = _strict_object(PREDECESSOR_RECEIPT, "v0.62.13 publication receipt")
    require(receipt.get("version") == PREDECESSOR_VERSION, "predecessor version differs")
    require(receipt.get("state") == EXPECTED_PREDECESSOR_STATE, "predecessor state differs")
    require(receipt.get("payload_total_bytes") == EXPECTED_PREDECESSOR_TOTAL_BYTES, "predecessor bytes differ")
    require(
        receipt.get("payload_inventory_aggregate_sha256") == EXPECTED_PREDECESSOR_AGGREGATE,
        "predecessor aggregate differs",
    )
    github = receipt.get("github_authority")
    zenodo = receipt.get("zenodo")
    require(
        isinstance(github, dict)
        and github.get("tag_target_commit") == EXPECTED_PREDECESSOR_TAG_COMMIT
        and github.get("source_tree") == EXPECTED_PREDECESSOR_TAG_TREE
        and github.get("receipt_sha256") == EXPECTED_PREDECESSOR_GITHUB_RECEIPT[1]
        and github.get("anonymous_readback") == "pass_100_of_100",
        "predecessor GitHub authority differs",
    )
    require(
        isinstance(zenodo, dict)
        and zenodo.get("record_id") == EXPECTED_PREDECESSOR_RECORD_ID
        and zenodo.get("concept_record_id") == EXPECTED_CONCEPT_ID
        and zenodo.get("concept_doi") == EXPECTED_CONCEPT_DOI
        and zenodo.get("version_doi") == EXPECTED_PREDECESSOR_DOI
        and zenodo.get("access_right") == "open"
        and zenodo.get("file_count") == EXPECTED_PREDECESSOR_FILES
        and zenodo.get("anonymous_readback") == "pass_100_of_100",
        "predecessor Zenodo authority differs",
    )
    rows = receipt.get("payload_inventory")
    require(isinstance(rows, list) and len(rows) == EXPECTED_PREDECESSOR_FILES, "predecessor inventory differs")
    by_name: dict[str, dict[str, Any]] = {}
    for raw in rows:
        require(isinstance(raw, dict), "predecessor inventory row is malformed")
        name = raw.get("name")
        require(isinstance(name, str), "predecessor inventory name is malformed")
        safe_flat_name(name)
        require(name not in by_name, f"duplicate predecessor name: {name}")
        require(type(raw.get("bytes")) is int and raw["bytes"] >= 0, f"predecessor size differs: {name}")
        require(re.fullmatch(r"[0-9a-f]{64}", str(raw.get("sha256", ""))) is not None, f"predecessor SHA differs: {name}")
        require(re.fullmatch(r"[0-9a-f]{32}", str(raw.get("md5", ""))) is not None, f"predecessor MD5 differs: {name}")
        expected_url = f"{PREDECESSOR_ANONYMOUS_URL_ROOT}/{quote(name, safe='')}/content"
        require(raw.get("anonymous_url") == expected_url, f"predecessor anonymous URL differs: {name}")
        require(raw.get("anonymous_byte_identity") is True, f"predecessor public-byte proof differs: {name}")
        by_name[name] = raw
    require(sum(int(row["bytes"]) for row in rows) == EXPECTED_PREDECESSOR_TOTAL_BYTES, "predecessor total does not close")
    require(inventory_aggregate(rows) == EXPECTED_PREDECESSOR_AGGREGATE, "predecessor rows do not reproduce aggregate")
    return by_name, _validate_boundary(set(by_name))


def _validate_predecessor_directory(rows: dict[str, dict[str, Any]]) -> None:
    require(PREDECESSOR_DIR.is_dir() and not PREDECESSOR_DIR.is_symlink(), "local v0.62.13 payload is missing")
    entries = list(PREDECESSOR_DIR.iterdir())
    require(len(entries) == EXPECTED_PREDECESSOR_FILES, "local predecessor count differs")
    require(all(path.is_file() and not path.is_symlink() for path in entries), "local predecessor is not flat regular files")
    require({path.name for path in entries} == set(rows), "local predecessor names differ")
    observed: list[dict[str, Any]] = []
    for name in sorted(rows):
        data = (PREDECESSOR_DIR / name).read_bytes()
        expected = rows[name]
        require((len(data), sha256(data)) == (expected["bytes"], expected["sha256"]), f"predecessor bytes differ: {name}")
        observed.append({"name": name, "bytes": len(data), "sha256": sha256(data)})
    require(inventory_aggregate(observed) == EXPECTED_PREDECESSOR_AGGREGATE, "local predecessor aggregate differs")


def _course_snapshot(data: bytes) -> dict[str, Any]:
    rows = validate_jsonl("course-capsules-v1.jsonl", data)
    legacy.validate_course_capsules(rows)
    by_id = {str(row["course_id"]): row for row in rows}
    c130 = by_id.get("C130")
    require(isinstance(c130, dict), "C130 course capsule is absent")
    interoperability = c130.get("layers", {}).get("interoperability", {})
    semantic = interoperability.get("semantic_adapter") if isinstance(interoperability, dict) else None
    require(
        isinstance(semantic, dict)
        and semantic.get("status") == "verified"
        and semantic.get("contract_version") == "2.3.1",
        "C130 course capsule is not bound to the admitted v2.3.1 adapter",
    )
    evidence = semantic.get("evidence")
    locators = {row.get("locator") for row in evidence if isinstance(row, dict)} if isinstance(evidence, list) else set()
    require(
        {
            "backend/course-capsule-v1/adapters/c130-v231/ADMISSION.json",
            "backend/course-capsule-v1/adapters/c130-v231/manifest.json",
        }
        <= locators,
        "C130 course capsule lacks admission/manifest evidence",
    )
    return {"course_count": len(rows), "c130_semantic_adapter": "verified_v2.3.1"}


def _validate_c130(source_commit: str) -> dict[str, Any]:
    admission_data = C130_ADMISSION_PATH.read_bytes()
    manifest_data = C130_MANIFEST_PATH.read_bytes()
    require(
        (len(admission_data), sha256(admission_data)) == EXPECTED_C130_ADMISSION,
        "C130 admission identity differs",
    )
    require(
        (len(manifest_data), sha256(manifest_data)) == EXPECTED_C130_MANIFEST,
        "C130 manifest identity differs",
    )
    require_committed_bytes(source_commit, C130_ADMISSION_PATH, admission_data, "C130 admission")
    require_committed_bytes(source_commit, C130_MANIFEST_PATH, manifest_data, "C130 manifest")
    admission = _strict_object(C130_ADMISSION_PATH, "C130 admission")
    manifest = _strict_object(C130_MANIFEST_PATH, "C130 manifest")
    require(admission.get("state") == "locally_admitted_central_release_pending", "C130 admission state differs")
    require(admission.get("course_id") == "C130" and admission.get("courses") == ["C130"], "C130 course binding differs")
    for key, value in (
        ("package_id", EXPECTED_C130_PACKAGE_ID),
        ("dataset_id", EXPECTED_C130_DATASET_ID),
        ("extension_id", EXPECTED_C130_EXTENSION_ID),
    ):
        require(admission.get(key) == manifest.get(key) == value, f"C130 {key} differs")
    require(admission.get("semantic_counts", {}).get("canonical_records") == 51_704, "C130 canonical count differs")
    owner = admission.get("owner_authority")
    require(
        isinstance(owner, dict)
        and owner.get("release_commit") == EXPECTED_C130_OWNER_COMMIT
        and owner.get("release_tree") == EXPECTED_C130_OWNER_TREE
        and owner.get("owner_native_authoritative") is True
        and owner.get("owner_tree_mutated") is False,
        "C130 owner commit/tree authority differs",
    )
    archive_path = PREPARED_ADDITION_SOURCES[C130_ARCHIVE_NAME]
    require(_identity(archive_path) == EXPECTED_C130_ARCHIVE, "C130 package identity differs")
    archive = admission.get("archive")
    require(
        isinstance(archive, dict)
        and archive.get("bytes") == EXPECTED_C130_ARCHIVE[0]
        and archive.get("sha256") == EXPECTED_C130_ARCHIVE[1]
        and archive.get("path") == archive_path.relative_to(PROJECT).as_posix(),
        "C130 admission archive binding differs",
    )
    require(admission.get("public_package_excludes_admission") is True, "C130 package/admission cycle boundary differs")
    validate_zip(C130_ARCHIVE_NAME, archive_path, exact_file_count=65)
    return {
        "course_id": "C130",
        "package_id": EXPECTED_C130_PACKAGE_ID,
        "canonical_records": 51_704,
        "archive": {"bytes": EXPECTED_C130_ARCHIVE[0], "sha256": EXPECTED_C130_ARCHIVE[1]},
    }


def _validate_v2_snapshot(source_commit: str) -> dict[str, Any]:
    for path in V2_VALIDATED_SOURCE_PATHS.values():
        require_committed_bytes(source_commit, path, path.read_bytes(), path.name)
    index = _strict_object(PREPARED_ADDITION_SOURCES["v23-adapter-index-v2.json"], "v2 adapter index")
    adapters = index.get("adapters")
    packages = index.get("packages")
    require(isinstance(adapters, list) and isinstance(packages, list), "v2 adapter index arrays are missing")
    roles = tuple(str(row.get("role_id")) for row in adapters if isinstance(row, dict))
    require(roles == EXPECTED_ADAPTER_ROLE_ORDER, f"v2 adapter role order differs: {roles!r}")
    require(len({row.get("package_id") for row in packages if isinstance(row, dict)}) == 8, "v2 package identities are not eight unique values")
    require(index.get("summary") == EXPECTED_V2_SUMMARY, "v2 adapter summary differs from 9-role/8-package C130 boundary")
    c130_packages = [row for row in packages if isinstance(row, dict) and row.get("package_id") == EXPECTED_C130_PACKAGE_ID]
    require(len(c130_packages) == 1, "C130 package row is not unique")
    c130 = c130_packages[0]
    require(c130.get("dataset_id") == EXPECTED_C130_DATASET_ID, "C130 dataset ID differs in v2 index")
    require(c130.get("extension_id") == EXPECTED_C130_EXTENSION_ID, "C130 extension ID differs in v2 index")
    require(c130.get("canonical_records") == 51_704, "C130 canonical count differs in v2 index")
    require(c130.get("admission_state") == "admitted_pending_release", "C130 v2 admission state differs")
    require(c130.get("archive", {}).get("sha256") == EXPECTED_C130_ARCHIVE[1], "C130 v2 archive binding differs")

    receipt_path = PREPARED_ADDITION_SOURCES["MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json"]
    require_committed_bytes(source_commit, receipt_path, receipt_path.read_bytes(), "v2 snapshot receipt")
    receipt = _strict_object(receipt_path, "v2 snapshot receipt")
    require(receipt.get("status") == "pass", "v2 snapshot receipt is not pass")
    require(receipt.get("summary") == EXPECTED_V2_SUMMARY, "v2 snapshot receipt summary differs")
    validated = receipt.get("validated_files")
    require(isinstance(validated, list) and len(validated) == len(V2_VALIDATED_SOURCE_PATHS), "v2 receipt file count differs")
    by_path = {str(row.get("path")): row for row in validated if isinstance(row, dict)}
    require(set(by_path) == set(V2_VALIDATED_SOURCE_PATHS), "v2 receipt path closure differs")
    for relative, path in V2_VALIDATED_SOURCE_PATHS.items():
        data = path.read_bytes()
        require(
            by_path[relative].get("bytes") == len(data) and by_path[relative].get("sha256") == sha256(data),
            f"v2 receipt identity differs: {relative}",
        )
    return {"role_order": list(roles), "summary": EXPECTED_V2_SUMMARY}


def _validate_capsule_archive(path: Path, flat_jsonl: bytes) -> dict[str, Any]:
    require(EXPECTED_COURSE_CAPSULE_MEMBER_COUNT is not None, "freeze EXPECTED_COURSE_CAPSULE_MEMBER_COUNT after the final package build")
    require(type(EXPECTED_COURSE_CAPSULE_MEMBER_COUNT) is int and EXPECTED_COURSE_CAPSULE_MEMBER_COUNT > 0, "combined capsule member-count freeze is invalid")
    validate_zip(
        COURSE_CAPSULE_ARCHIVE_NAME,
        path,
        exact_file_count=EXPECTED_COURSE_CAPSULE_MEMBER_COUNT,
        required_members=CAPSULE_REQUIRED_MEMBERS,
    )
    with zipfile.ZipFile(path, "r") as archive:
        require(
            archive.read("backend/course-capsule-v1/generated/course-capsules.jsonl") == flat_jsonl
            and archive.read("docs/data/course-capsule-v1/course-capsules.jsonl") == flat_jsonl,
            "combined capsule JSONL projections differ from flat release bytes",
        )
        mirror_pairs = (
            ("backend/course-capsule-v1/authority/public-baseline-v0.62.12.json", "docs/data/course-capsule-v1/public-baseline-v0.62.12.json"),
            ("backend/course-capsule-v1/authority/v23-adapter-index-v2.json", "docs/data/v23-adapter-index-v2.json"),
            ("backend/course-capsule-v1/authority/modular-backend-pattern-index-v2.json", "docs/data/modular-backend-pattern-index-v2.json"),
            ("backend/course-capsule-v1/authority/feature-adoption-provenance-v1.json", "docs/data/feature-adoption-provenance-v1.json"),
            ("backend/course-capsule-v1/authority/comparison-evidence-manifest-v1.json", "docs/data/comparison-evidence-manifest-v1.json"),
            ("backend/course-capsule-v1/authority/terminology-policy-v1/README.md", "docs/data/course-capsule-v1/terminology-policy-v1/README.md"),
            ("backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json", "docs/data/course-capsule-v1/terminology-policy-v1/canonical-register-policy.json"),
            ("backend/course-capsule-v1/authority/terminology-policy-v1/checksums.sha256", "docs/data/course-capsule-v1/terminology-policy-v1/checksums.sha256"),
            ("schemas/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json", "docs/schema/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json"),
            ("schemas/course-capsule-v1/v2/terminology-concept-record-v1.schema.json", "docs/schema/course-capsule-v1/v2/terminology-concept-record-v1.schema.json"),
        )
        for authority, public in mirror_pairs:
            require(archive.read(authority) == archive.read(public), f"combined capsule mirror differs: {authority}")
        terminology_policy = archive.read(
            "backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json"
        )
        require(
            (len(terminology_policy), sha256(terminology_policy)) == EXPECTED_TERMINOLOGY_POLICY,
            "combined capsule terminology-policy identity differs",
        )
        c130_member = "backend/course-capsule-v1/builds/program-matematika-indonesia-c130-operations-research-v2.3.1.zip"
        require(
            (len(archive.read(c130_member)), sha256(archive.read(c130_member))) == EXPECTED_C130_ARCHIVE,
            "combined capsule C130 package identity differs",
        )
    return {"members": EXPECTED_COURSE_CAPSULE_MEMBER_COUNT, "c130_package_bound": True}


def _collect_prepared(source_commit: str) -> tuple[list[dict[str, Any]], dict[str, bytes], dict[str, Any]]:
    sources = {**REPLACEMENT_SOURCES, **PREPARED_ADDITION_SOURCES}
    rows: list[dict[str, Any]] = []
    data_by_name: dict[str, bytes] = {}
    for name, path in sorted(sources.items()):
        require(path.is_file() and not path.is_symlink(), f"prepared source is missing or symlinked: {name}")
        data = path.read_bytes()
        require(data, f"prepared source is empty: {name}")
        require_committed_bytes(source_commit, path, data, name)
        if path.suffix.lower() in {".json", ".jsonl", ".md", ".html", ".txt", ".sha256"}:
            privacy_scan(name, data)
        if path.suffix.lower() == ".zip":
            validate_zip(name, path)
        rows.append(fact(name, data, "commit_bound_v0.62.14_source", path))
        data_by_name[name] = data
    course = _course_snapshot(data_by_name["course-capsules-v1.jsonl"])
    c130 = _validate_c130(source_commit)
    v2 = _validate_v2_snapshot(source_commit)
    capsule = _validate_capsule_archive(
        REPLACEMENT_SOURCES[COURSE_CAPSULE_ARCHIVE_NAME],
        data_by_name["course-capsules-v1.jsonl"],
    )
    return rows, data_by_name, {"course": course, "c130": c130, "v2": v2, "capsule": capsule}


def _notes(source: dict[str, Any]) -> bytes:
    text = f"""# Program Matematika Indonesia v0.62.14

Rilis ini mempertahankan 91 berkas v0.62.13 secara byte-identik, mengganti
enam nama, menghilangkan hanya tiga berkas versi lama, dan menambah lima belas
nama baru. Hasilnya tepat 112 berkas datar; manifest checksum memiliki 111
baris dan tidak mencantumkan dirinya sendiri.

Snapshot backend modular mengikat sembilan peran ke delapan paket. C130 kini
terikat ke adapter operations-research v2.3.1 dengan 51.704 rekaman kanonis;
31 peran tetap tanpa klaim adapter lokal.

Paket kapsul juga membawa kebijakan terminologi berbasis konsep dan register.
Kebijakan itu mempertahankan bukti terminologi native yang lama, membedakan
bentuk umum dari bentuk teknis, dan tidak mengklaim harmonisasi global tanpa
bukti khusus per konsep dan bidang.

Arsip sumber adalah `git archive --format=zip` deterministik dari commit
`{source['source_commit']}` dan tree `{source['source_tree']}`. Komentar ZIP
mengikat commit itu. Arsip berukuran {source['bytes']} byte dengan SHA-256
`{source['sha256']}`.

Permukaan belajar manusia tetap menjadi pintu masuk utama. JSON, JSONL, CSV,
schema, receipt, dan ZIP adalah backend modular serta bukti reproduksi.
"""
    return text.replace("\r\n", "\n").encode("utf-8")


def _checksum_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    ordered = sorted(rows, key=lambda row: str(row["name"]))
    require(len(ordered) == EXPECTED_CHECKSUM_ROWS, "pre-checksum inventory is not 111 files")
    require(len({str(row["name"]) for row in ordered}) == EXPECTED_CHECKSUM_ROWS, "duplicate pre-checksum name")
    return "".join(f"{row['sha256']}  {row['name']}\n" for row in ordered).encode("utf-8")


def _assemble(destination: Path, source_commit: str, source_tree: str) -> list[dict[str, Any]]:
    require(destination.is_dir() and not any(destination.iterdir()), "staging directory is not empty")
    predecessor, retained = _predecessor_inventory()
    _validate_predecessor_directory(predecessor)
    validate_source_authority(source_commit, source_tree)
    prepared_rows, prepared_data, semantic = _collect_prepared(source_commit)
    rows: list[dict[str, Any]] = []
    for name in sorted(retained):
        data = (PREDECESSOR_DIR / name).read_bytes()
        expected = predecessor[name]
        require((len(data), sha256(data)) == (expected["bytes"], expected["sha256"]), f"retained bytes changed: {name}")
        (destination / name).write_bytes(data)
        rows.append(fact(name, data, "retained_exact_from_v0.62.13"))
    by_name = {str(row["name"]): row for row in prepared_rows}
    require(set(by_name) == set(prepared_data), "prepared inventory differs")
    for name in sorted(prepared_data):
        data = prepared_data[name]
        (destination / name).write_bytes(data)
        rows.append(dict(by_name[name]))

    source_data, source_details = build_source_archive(source_commit, source_tree)
    source_row = fact(SOURCE_ZIP_NAME, source_data, "deterministic_git_archive_of_explicit_commit")
    source_row.update(source_details)
    (destination / SOURCE_ZIP_NAME).write_bytes(source_data)
    rows.append(source_row)

    notes = _notes(source_row)
    privacy_scan(NOTES_NAME, notes)
    (destination / NOTES_NAME).write_bytes(notes)
    rows.append(fact(NOTES_NAME, notes, "generated_release_notes"))
    require(len(rows) == EXPECTED_CHECKSUM_ROWS, "91+6+12+1+1 pre-checksum equation differs")
    checksum = _checksum_bytes(rows)
    (destination / CHECKSUM_NAME).write_bytes(checksum)
    rows.append(fact(CHECKSUM_NAME, checksum, "generated_release_checksum"))
    _validate_staged(destination, rows)
    rows.sort(key=lambda row: str(row["name"]))
    source_row["semantic_validation"] = semantic
    return rows


def _validate_staged(directory: Path, rows: list[dict[str, Any]]) -> None:
    require(len(rows) == EXPECTED_FILES, "final inventory is not 112 rows")
    entries = list(directory.iterdir())
    require(len(entries) == EXPECTED_FILES, "staged release is not 112 entries")
    require(all(path.is_file() and not path.is_symlink() for path in entries), "staged release is not flat regular files")
    expected = {str(row["name"]): row for row in rows}
    require(len(expected) == EXPECTED_FILES and {path.name for path in entries} == set(expected), "staged name closure differs")
    observed: list[dict[str, Any]] = []
    for name in sorted(expected):
        data = (directory / name).read_bytes()
        row = expected[name]
        require((len(data), sha256(data)) == (row["bytes"], row["sha256"]), f"staged bytes differ: {name}")
        observed.append({"name": name, "bytes": len(data), "sha256": sha256(data)})
    checksum = (directory / CHECKSUM_NAME).read_bytes()
    require(checksum == _checksum_bytes(row for row in observed if row["name"] != CHECKSUM_NAME), "checksum readback differs")


def _summary(status: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    source = next(row for row in rows if row["name"] == SOURCE_ZIP_NAME)
    checksum = next(row for row in rows if row["name"] == CHECKSUM_NAME)
    return {
        "status": status,
        "version": VERSION,
        "output": relative_display(OUTPUT_DIR),
        "predecessor": {
            "version": PREDECESSOR_VERSION,
            "files": EXPECTED_PREDECESSOR_FILES,
            "bytes": EXPECTED_PREDECESSOR_TOTAL_BYTES,
            "aggregate_sha256": EXPECTED_PREDECESSOR_AGGREGATE,
        },
        "boundary": {
            "retained_exact": EXPECTED_RETAINED,
            "same_name_replacements": EXPECTED_REPLACEMENTS,
            "pure_omissions": EXPECTED_PURE_OMISSIONS,
            "pure_additions": EXPECTED_PURE_ADDITIONS,
            "successor_files": EXPECTED_FILES,
        },
        "files": EXPECTED_FILES,
        "bytes": sum(int(row["bytes"]) for row in rows),
        "inventory_aggregate_sha256": inventory_aggregate(rows),
        "checksum": {"rows": EXPECTED_CHECKSUM_ROWS, "bytes": checksum["bytes"], "sha256": checksum["sha256"]},
        "source_archive": {
            "name": SOURCE_ZIP_NAME,
            "bytes": source["bytes"],
            "sha256": source["sha256"],
            "commit": source["source_commit"],
            "tree": source["source_tree"],
            "zip_comment": source["zip_comment"],
            "zip_files": source["zip_files"],
        },
    }


def _compare_existing(expected_dir: Path, rows: list[dict[str, Any]]) -> None:
    require(OUTPUT_DIR.is_dir() and not OUTPUT_DIR.is_symlink(), "existing v0.62.14 output is not a regular directory")
    entries = list(OUTPUT_DIR.iterdir())
    require(len(entries) == EXPECTED_FILES, "existing v0.62.14 count differs")
    require(all(path.is_file() and not path.is_symlink() for path in entries), "existing v0.62.14 is not flat regular files")
    names = {str(row["name"]) for row in rows}
    require({path.name for path in entries} == names, "existing v0.62.14 names differ")
    for name in sorted(names):
        require((OUTPUT_DIR / name).read_bytes() == (expected_dir / name).read_bytes(), f"existing v0.62.14 bytes differ: {name}")


def _run_preflight(source_commit: str, source_tree: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="pmi-v0.62.14-preflight-") as temporary:
        stage = Path(temporary)
        rows = _assemble(stage, source_commit, source_tree)
        if OUTPUT_DIR.exists():
            _compare_existing(stage, rows)
            return _summary("PASS_EXISTING_BYTE_IDENTICAL", rows)
        return _summary("PASS_PREFLIGHT_READY", rows)


def _safe_remove_build_temp(path: Path) -> None:
    require(path.parent.resolve() == RELEASES_DIR.resolve() and path.name.startswith(BUILD_PREFIX) and path != OUTPUT_DIR, "unsafe build temp path")
    if path.exists():
        require(path.is_dir() and not path.is_symlink(), "build temp is not a regular directory")
        shutil.rmtree(path)


def _run_build(source_commit: str, source_tree: str) -> dict[str, Any]:
    require(RELEASES_DIR.is_dir() and not RELEASES_DIR.is_symlink(), "releases directory is missing")
    temporary = Path(tempfile.mkdtemp(prefix=BUILD_PREFIX, dir=RELEASES_DIR))
    committed = False
    try:
        rows = _assemble(temporary, source_commit, source_tree)
        if OUTPUT_DIR.exists():
            _compare_existing(temporary, rows)
            return _summary("PASS_EXISTING_BYTE_IDENTICAL", rows)
        temporary.rename(OUTPUT_DIR)
        committed = True
        return _summary("PASS_ASSEMBLED_NOT_PUBLISHED", rows)
    finally:
        if not committed:
            _safe_remove_build_temp(temporary)


def _run_hydrate() -> dict[str, Any]:
    rows, _ = _predecessor_inventory()
    require(RELEASES_DIR.is_dir() and not RELEASES_DIR.is_symlink(), "releases directory is missing")
    require(not PREDECESSOR_DIR.exists() and not PREDECESSOR_DIR.is_symlink(), "refusing to overwrite predecessor directory")
    temporary = Path(tempfile.mkdtemp(prefix=HYDRATION_PREFIX, dir=RELEASES_DIR))
    committed = False
    try:
        opener = build_opener(ProxyHandler({}))
        for name in sorted(rows):
            row = rows[name]
            request = Request(
                str(row["anonymous_url"]),
                headers={"Accept": "*/*", "Accept-Encoding": "identity", "User-Agent": "PMI-v06214-predecessor-hydrator/1"},
                method="GET",
            )
            with opener.open(request, timeout=180) as response:
                require(response.getcode() == 200, f"predecessor GET failed: {name}")
                data = response.read(int(row["bytes"]) + 1)
            require((len(data), sha256(data)) == (row["bytes"], row["sha256"]), f"predecessor download differs: {name}")
            with (temporary / name).open("xb") as stream:
                require(stream.write(data) == len(data), f"short predecessor write: {name}")
        original = globals()["PREDECESSOR_DIR"]
        try:
            globals()["PREDECESSOR_DIR"] = temporary
            _validate_predecessor_directory(rows)
        finally:
            globals()["PREDECESSOR_DIR"] = original
        temporary.rename(PREDECESSOR_DIR)
        committed = True
        return {
            "status": "PASS_PREDECESSOR_HYDRATED",
            "version": PREDECESSOR_VERSION,
            "files": EXPECTED_PREDECESSOR_FILES,
            "bytes": EXPECTED_PREDECESSOR_TOTAL_BYTES,
            "aggregate_sha256": EXPECTED_PREDECESSOR_AGGREGATE,
        }
    except (HTTPError, URLError, HTTPException, OSError) as exc:
        raise BuildError(f"predecessor hydration failed: {exc}") from exc
    finally:
        if not committed and temporary.exists():
            require(temporary.parent.resolve() == RELEASES_DIR.resolve() and temporary.name.startswith(HYDRATION_PREFIX), "unsafe hydration temp path")
            shutil.rmtree(temporary)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", help="full lowercase source commit archived into the release")
    parser.add_argument("--source-tree", help="full lowercase tree required to match --source-commit")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true", help="assemble and validate in a temporary directory")
    modes.add_argument("--build", action="store_true", help="atomically assemble releases/v0.62.14")
    modes.add_argument("--hydrate-predecessor", action="store_true", help="anonymously restore an absent pinned v0.62.13 payload")
    args = parser.parse_args(argv)
    if args.hydrate_predecessor:
        if args.source_commit is not None or args.source_tree is not None:
            parser.error("--hydrate-predecessor refuses --source-commit and --source-tree")
    elif args.source_commit is None or args.source_tree is None:
        parser.error("--preflight and --build require both --source-commit and --source-tree")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.hydrate_predecessor:
            result = _run_hydrate()
        elif args.preflight:
            result = _run_preflight(args.source_commit, args.source_tree)
        else:
            result = _run_build(args.source_commit, args.source_tree)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0
    except (BuildError, RuntimeError, OSError) as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(json.dumps({"status": "FAIL_CLOSED", "version": VERSION, "error": detail}, sort_keys=True, separators=(",", ":")), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
