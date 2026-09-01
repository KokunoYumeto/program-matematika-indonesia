#!/usr/bin/env python3
"""Build and verify the deterministic public course-capsule v1 package."""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import tempfile
import zipfile
import zlib
from collections.abc import Callable
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "backend"
    / "course-capsule-v1"
    / "builds"
    / "program-matematika-indonesia-course-capsule-v1.zip"
)
PACKAGE_RECEIPT = OUTPUT.with_name(
    f"{OUTPUT.stem}.PACKAGE_RECEIPT.json"
)
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
D40_READBACK_MEMBER = (
    "backend/course-capsule-v1/validation/"
    "D40_O010_INDEPENDENT_ANONYMOUS_READBACK.json"
)
VALIDATION_RECEIPT_MEMBER = (
    "backend/course-capsule-v1/validation/VALIDATION_RECEIPT.json"
)
V23_ADAPTER_INDEX_V1_MEMBER = "backend/authority/v23-adapter-index-v1.json"
V23_ADAPTER_INDEX_V2_MEMBER = (
    "backend/course-capsule-v1/authority/v23-adapter-index-v2.json"
)
V2_PATTERN_INDEX_MEMBER = (
    "backend/course-capsule-v1/authority/modular-backend-pattern-index-v2.json"
)
V2_FEATURE_PROVENANCE_MEMBER = (
    "backend/course-capsule-v1/authority/feature-adoption-provenance-v1.json"
)
V2_COMPARISON_EVIDENCE_MEMBER = (
    "backend/course-capsule-v1/authority/comparison-evidence-manifest-v1.json"
)
V2_RECEIPT_MEMBER = (
    "backend/course-capsule-v1/validation/MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json"
)
V2_PUBLIC_RECEIPT_MEMBER = (
    "docs/data/modular-backend-snapshot-v2-validation-receipt.json"
)
V2_VALIDATOR_MEMBER = "scripts/validate-modular-backend-snapshots-v2.py"
TERMINOLOGY_ROOT = (
    "backend/course-capsule-v1/authority/native-terminology-qa/"
    "unib-teori-bilangan-20260831"
)
PUBLIC_TERMINOLOGY_ROOT = (
    "docs/data/course-capsule-v1/native-terminology-qa/"
    "unib-teori-bilangan-20260831"
)
TERMINOLOGY_CONCORDANCE_MEMBER = f"{TERMINOLOGY_ROOT}/terminology_concordance.json"
TERMINOLOGY_POLICY_ROOT = (
    "backend/course-capsule-v1/authority/terminology-policy-v1"
)
PUBLIC_TERMINOLOGY_POLICY_ROOT = (
    "docs/data/course-capsule-v1/terminology-policy-v1"
)
TERMINOLOGY_POLICY_MEMBER = (
    f"{TERMINOLOGY_POLICY_ROOT}/canonical-register-policy.json"
)
D40_READBACK_IDENTITY = {
    "path": D40_READBACK_MEMBER,
    "bytes": 7570,
    "sha256": "a34f5532208ad45c27d5c4b4108e51f5d3b76e8ded0ef5d334f31465f61e33f9",
}

BASE_EXACT_MEMBERS = (
    "backend/course-capsule-v1/README.md",
    "backend/course-capsule-v1/authority/backend-design-policy-v1.json",
    "backend/course-capsule-v1/authority/integration-overrides-v1.json",
    "backend/course-capsule-v1/authority/native-package-references-v1.json",
    "backend/course-capsule-v1/validation/CLP_PUBLIC_NATIVE_EVIDENCE_ADDENDUM_20260831.json",
    "backend/course-capsule-v1/authority/public-baseline-v0.62.12.json",
    "backend/course-capsule-v1/generated/course-capsules.json",
    "backend/course-capsule-v1/generated/course-capsules.jsonl",
    "backend/course-capsule-v1/generated/manifest.json",
    "backend/course-capsule-v1/validation/D40_O010_INDEPENDENT_ANONYMOUS_READBACK.json",
    "backend/course-capsule-v1/validation/SITE_VALIDATION_RECEIPT.json",
    "backend/course-capsule-v1/validation/VALIDATION_RECEIPT.json",
    "backend/authority/learner-delivery-overrides-v1.json",
    "backend/authority/modular-backend-pattern-index-v1.json",
    "backend/authority/v23-adapter-index-v1.json",
    "backend/authority/learner-delivery-v1.json",
    "backend/authority/learner-tools-overrides-v1.json",
    "backend/authority/learner-tools-v1.json",
    "schemas/course-capsule-v1/backend-design-policy-v1.schema.json",
    "schemas/course-capsule-v1/course-capsule-v1.schema.json",
    "schemas/course-capsule-v1/public-baseline-v1.schema.json",
    "schemas/v1/a00-assessment-map-v1.schema.json",
    "schemas/v1/learner-delivery-v1.schema.json",
    "schemas/v1/learner-tools-v1.schema.json",
    "schemas/v1/v23-adapter-index-v1.schema.json",
    "scripts/build-and-validate-course-capsules-v1.mjs",
    "scripts/build-course-capsule-package-v1.py",
    "scripts/build-course-capsules-v1.mjs",
    "scripts/build-judson-course-capsule-v1.mjs",
    "scripts/import-judson-course-capsule-v1.py",
    "scripts/test-course-capsule-ui-v1.mjs",
    "scripts/test-course-capsule-educator-truth-v1.mjs",
    "scripts/build-learner-delivery-v1.mjs",
    "scripts/build-learner-tools-v1.mjs",
    "scripts/sync-course-capsules-v1.mjs",
    "scripts/validate-course-capsule-site-v1.mjs",
    "scripts/validate-course-capsules-v1.mjs",
    "scripts/validate-static-site.mjs",
    "docs/courses.js",
    "docs/data/learner-delivery-v1.json",
    "docs/data/modular-backend-pattern-index-v1.json",
    "docs/data/v23-adapter-index-v1.json",
    "docs/data/learner-tools-v1.json",
    "docs/learner-delivery.js",
    "docs/learner-tools.js",
    "docs/live-course-publications.js",
    "docs/schema/v1/a00-assessment-map-v1.schema.json",
    "docs/schema/v1/learner-delivery-v1.schema.json",
    "docs/schema/v1/learner-tools-v1.schema.json",
    "docs/schema/v1/v23-adapter-index-v1.schema.json",
)

PUBLIC_EXACT_MEMBERS = (
    "docs/backend/backend.css",
    "docs/backend/backend.js",
    "docs/backend/index.html",
    "docs/backend/index.template.html",
    "docs/backend/judson/C30.html",
    "docs/backend/judson/C40.html",
    "docs/backend/judson/chapters.json",
    "docs/backend/judson/contribution.md",
    "docs/backend/judson/route-evidence.json",
    "docs/backend/judson/validation.json",
    "docs/backend/openlogic/C80.html",
    "docs/backend/openlogic/learner-route.json",
    "docs/backend/openlogic/validation.json",
    "docs/backend/c130/C130.html",
    "docs/backend/c130/learner-route.json",
    "docs/backend/c130/validation.json",
    "docs/data/course-capsule-v1/backend-design-policy-v1.json",
    "docs/data/course-capsule-v1/course-capsules.json",
    "docs/data/course-capsule-v1/course-capsules.jsonl",
    "docs/data/course-capsule-v1/manifest.json",
    "docs/data/course-capsule-v1/native-family-public-evidence-note-v1.md",
    "docs/data/course-capsule-v1/native-family-public-evidence-v1.json",
    "docs/data/course-capsule-v1/native-package-references-v1.json",
    f"{PUBLIC_TERMINOLOGY_ROOT}/checksums.sha256",
    f"{PUBLIC_TERMINOLOGY_ROOT}/README.md",
    f"{PUBLIC_TERMINOLOGY_ROOT}/terminology_concordance.json",
    "docs/data/course-capsule-v1/public-baseline-v0.62.12.json",
    "docs/data/course-capsule-v1/README.md",
    "docs/data/course-capsule-v1/validation-receipt.json",
    "docs/id-ID/courses/A00/latihan/anchor-audit-v1.json",
    "docs/id-ID/courses/A00/latihan/assessment-map-v1.json",
    "docs/id-ID/courses/A00/latihan/index.html",
    "docs/id-ID/courses/A00/latihan/latihan.css",
    "docs/id-ID/courses/A00/latihan/latihan.js",
    "docs/schema/course-capsule-v1/backend-design-policy-v1.schema.json",
    "docs/schema/course-capsule-v1/course-capsule-v1.schema.json",
    "docs/schema/course-capsule-v1/public-baseline-v1.schema.json",
)

V2_DATA_MIRROR_PAIRS = (
    (
        V23_ADAPTER_INDEX_V2_MEMBER,
        "docs/data/v23-adapter-index-v2.json",
    ),
    (
        V2_PATTERN_INDEX_MEMBER,
        "docs/data/modular-backend-pattern-index-v2.json",
    ),
    (
        V2_FEATURE_PROVENANCE_MEMBER,
        "docs/data/feature-adoption-provenance-v1.json",
    ),
    (
        V2_COMPARISON_EVIDENCE_MEMBER,
        "docs/data/comparison-evidence-manifest-v1.json",
    ),
)
V2_SCHEMA_MIRROR_PAIRS = (
    (
        "schemas/course-capsule-v1/v2/v23-adapter-index-v2.schema.json",
        "docs/schema/v2/v23-adapter-index-v2.schema.json",
    ),
    (
        "schemas/course-capsule-v1/v2/modular-backend-pattern-index-v2.schema.json",
        "docs/schema/v2/modular-backend-pattern-index-v2.schema.json",
    ),
    (
        "schemas/course-capsule-v1/v2/feature-adoption-provenance-v1.schema.json",
        "docs/schema/v2/feature-adoption-provenance-v1.schema.json",
    ),
    (
        "schemas/course-capsule-v1/v2/comparison-evidence-manifest-v1.schema.json",
        "docs/schema/v2/comparison-evidence-manifest-v1.schema.json",
    ),
)
V2_EXACT_MEMBERS = tuple(
    member for pair in V2_DATA_MIRROR_PAIRS + V2_SCHEMA_MIRROR_PAIRS for member in pair
) + (
    V2_RECEIPT_MEMBER,
    V2_PUBLIC_RECEIPT_MEMBER,
    V2_VALIDATOR_MEMBER,
)
TERMINOLOGY_EXACT_MEMBERS = (
    f"{TERMINOLOGY_ROOT}/README.md",
    TERMINOLOGY_CONCORDANCE_MEMBER,
    f"{TERMINOLOGY_ROOT}/checksums.sha256",
)
TERMINOLOGY_POLICY_DATA_MIRROR_PAIRS = (
    (
        f"{TERMINOLOGY_POLICY_ROOT}/README.md",
        f"{PUBLIC_TERMINOLOGY_POLICY_ROOT}/README.md",
    ),
    (
        TERMINOLOGY_POLICY_MEMBER,
        f"{PUBLIC_TERMINOLOGY_POLICY_ROOT}/canonical-register-policy.json",
    ),
    (
        f"{TERMINOLOGY_POLICY_ROOT}/checksums.sha256",
        f"{PUBLIC_TERMINOLOGY_POLICY_ROOT}/checksums.sha256",
    ),
)
TERMINOLOGY_POLICY_SCHEMA_MIRROR_PAIRS = (
    (
        "schemas/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json",
        "docs/schema/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json",
    ),
    (
        "schemas/course-capsule-v1/v2/terminology-concept-record-v1.schema.json",
        "docs/schema/course-capsule-v1/v2/terminology-concept-record-v1.schema.json",
    ),
)
TERMINOLOGY_POLICY_EXACT_MEMBERS = tuple(
    member
    for pair in TERMINOLOGY_POLICY_DATA_MIRROR_PAIRS
    + TERMINOLOGY_POLICY_SCHEMA_MIRROR_PAIRS
    for member in pair
)
ADAPTER_INTEGRATION_EXACT_MEMBERS = (
    "scripts/build-openlogic-course-capsule-v1.mjs",
    "scripts/import-openlogic-course-capsule-v1.py",
    "scripts/build-c130-course-capsule-v1.mjs",
    "scripts/build-modular-backend-snapshots-v2.mjs",
    "backend/course-capsule-v1/validation/C130_AUTHORITY_REPLAY_RECEIPT_20260901.json",
    "releases/v0.62.14/v23-adapter-index-v2.json",
    "GITHUB_PUBLICATION_RECEIPT_v0.62.14.json",
    "PUBLICATION_RECEIPT_v0.62.14.json",
)
EXACT_MEMBERS = (
    BASE_EXACT_MEMBERS
    + PUBLIC_EXACT_MEMBERS
    + V2_EXACT_MEMBERS
    + TERMINOLOGY_EXACT_MEMBERS
    + TERMINOLOGY_POLICY_EXACT_MEMBERS
    + ADAPTER_INTEGRATION_EXACT_MEMBERS
)

ADAPTER_SPECS = (
    {
        "key": "judson_c30_c40",
        "label": "Judson",
        "root": "backend/course-capsule-v1/adapters/judson-v231",
        "archive": (
            "backend/course-capsule-v1/builds/"
            "program-matematika-indonesia-judson-c30-c40-v2.3.1.zip"
        ),
        "admission": "backend/course-capsule-v1/adapters/judson-v231/ADMISSION.json",
        "manifest": "backend/course-capsule-v1/adapters/judson-v231/manifest.json",
        "site_validation": "docs/backend/judson/validation.json",
        "learner_route": "docs/backend/judson/route-evidence.json",
        "archive_bytes": 16905857,
        "archive_sha256": "177eda23cf07dd7d1225a176466f8686bbcdb91c233309f81252dd897a024700",
        "manifest_bytes": 28845,
        "manifest_sha256": "00b80a3f7406c96b375ddb390981dbd0a1f1e3d41e0d240c93b194694521c28a",
        "package_id": "urn:uuid:f2d0324c-322c-5f7b-a9e6-8beccf50656c",
        "dataset_id": "urn:uuid:d96f3a23-1002-5be5-bff2-bb035a386a3c",
        "admission_state": "locally_admitted_public_release_pending",
        "role_ids": ("C30", "C40"),
        "relationship": "directly_consumes_adapter_outputs",
        "input_count": 65,
        "manifest_count": 62,
        "seal_count": 63,
        "checksum_count": 64,
    },
    {
        "key": "openlogic_c80",
        "label": "OpenLogic",
        "root": "backend/course-capsule-v1/adapters/openlogic-v231",
        "archive": (
            "backend/course-capsule-v1/builds/"
            "program-matematika-indonesia-openlogic-c80-v2.3.1.zip"
        ),
        "admission": "backend/course-capsule-v1/adapters/openlogic-v231/ADMISSION.json",
        "manifest": "backend/course-capsule-v1/adapters/openlogic-v231/manifest.json",
        "site_validation": "docs/backend/openlogic/validation.json",
        "learner_route": "docs/backend/openlogic/learner-route.json",
        "archive_bytes": 2409875,
        "archive_sha256": "eb4293a9745dd7c6f98f7c94c05d214e4dfc904ef5dda3afea571e0ee1363673",
        "manifest_bytes": 22315,
        "manifest_sha256": "01974670c902a50d3e0166214f665286e0030a270a781a56413976be52ca4b01",
        "package_id": "urn:uuid:601e07e9-660e-5f8e-97bb-228be6c69566",
        "dataset_id": "urn:uuid:fdfa2782-db96-5e60-bcb3-d206d78b960a",
        "admission_state": "locally_admitted_central_release_pending",
        "role_ids": ("C80",),
        "relationship": "course_link_only_no_adapter_consumption_claim",
        "input_count": 67,
        "manifest_count": 64,
        "seal_count": 65,
        "checksum_count": 66,
    },
    {
        "key": "c130_operations_research",
        "label": "C130",
        "root": "backend/course-capsule-v1/adapters/c130-v231",
        "archive": (
            "backend/course-capsule-v1/builds/"
            "program-matematika-indonesia-c130-operations-research-v2.3.1.zip"
        ),
        "admission": "backend/course-capsule-v1/adapters/c130-v231/ADMISSION.json",
        "manifest": "backend/course-capsule-v1/adapters/c130-v231/manifest.json",
        "site_validation": "docs/backend/c130/validation.json",
        "learner_route": "docs/backend/c130/learner-route.json",
        "archive_bytes": 21213937,
        "archive_sha256": "eb195d1aa555e9d5e639c1e35a08b6f4425be24cc93b7f1f633161e9cacee865",
        "manifest_bytes": 22488,
        "manifest_sha256": "cad2922d9bd1facb33cc9d54a9836bb168fe0b8d996d9d4ef2e5d8c26053f239",
        "package_id": "urn:uuid:a84539b5-455b-5baf-89a4-f4c0336e33ab",
        "dataset_id": "urn:uuid:2e16c60d-7ee3-52f4-9c05-2c4dea0b07ca",
        "admission_state": "locally_admitted_central_release_pending",
        "role_ids": ("C130",),
        "relationship": "course_link_only_no_adapter_consumption_claim",
        "input_count": 65,
        "manifest_count": 62,
        "seal_count": 63,
        "checksum_count": 64,
    },
)

EXPECTED_STATIC_MEMBER_COUNT = 127
EXPECTED_MEMBER_COUNT = EXPECTED_STATIC_MEMBER_COUNT + sum(
    int(spec["input_count"]) + 2 for spec in ADAPTER_SPECS
)
EXPECTED_V2_SUMMARY = {
    "curriculum_roles": 40,
    "role_bindings": 9,
    "published_role_bindings": 9,
    "pending_role_bindings": 0,
    "distinct_adapter_packages": 8,
    "published_adapter_packages": 8,
    "pending_adapter_packages": 0,
    "represented_native_families": 8,
    "unbound_roles": 31,
    "families_without_local_adapter": 25,
    "families_without_public_replay_complete_adapter": 25,
    "package_deduplicated_canonical_records": 285829,
}
EXPECTED_V2_ROLE_ORDER = (
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
EXPECTED_V2_PACKAGE_FIELDS = {
    "judson_c30_c40": {
        "canonical_records": 17745,
        "unit_records": 3323,
        "relation_records": 6505,
        "source_translation_pairs": 4466,
        "jsonl_csv_table_pairs": 19,
    },
    "openlogic_c80": {
        "canonical_records": 5807,
        "unit_records": 722,
        "ordered_import_relations": 725,
        "namespace_mappings": 1445,
        "rights_assignments": 728,
        "reader_reachable_units": 642,
        "retained_non_reader_units": 80,
        "reader_pages": 1116,
        "native_html_claimed": False,
        "unit_or_page_anchors_claimed": False,
        "jsonl_csv_table_pairs": 19,
    },
    "c130_operations_research": {
        "canonical_records": 51704,
        "unit_records": 1993,
        "relation_records": 9545,
        "rights_assignments": 7634,
        "namespace_mappings": 17273,
        "public_artifacts": 83,
        "reader_pages": 666,
        "native_html_claimed": False,
        "unit_or_page_anchors_claimed": False,
        "jsonl_csv_table_pairs": 19,
    },
}

FORBIDDEN_MEMBERS = {
    "backend/course-capsule-v1/INTEGRATION_GOAL.md",
    "backend/course-capsule-v1/INTEGRATION_LOG.md",
    (
        "backend/course-capsule-v1/adapters/judson-v231/"
        "MANAGER_INTEGRATION_HANDOFF_20260831.json"
    ),
}
FORBIDDEN_PREFIXES = (
    "backend/course-capsule-v1/validation/manager-followthrough/",
    "backend/course-capsule-v1/adapters/judson-v231/evidence/",
)

PRIVATE_PATH_PATTERNS = (
    re.compile(
        rb"(?i)(?:^|[^A-Za-z0-9])[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\"']{1,64}[\\/]"
    ),
    re.compile(rb"(?i)(?:^|[^A-Za-z0-9])/(?:home|Users)/[^/\s]+/"),
    # Require ordinary server/share characters so this detector cannot match
    # its own regular-expression source while still rejecting real UNC paths.
    re.compile(
        rb"(?i)(?:^|[^A-Za-z0-9])\\\\[A-Za-z0-9._-]+\\[A-Za-z0-9$._-]+(?:\\|$)"
    ),
    re.compile(rb"(?i)[\\/]\.codex[\\/]"),
)

CREDENTIAL_PATTERNS = (
    re.compile(rb"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(rb"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{20,}"),
    re.compile(
        rb"(?i)[\"'](?:access[_-]?token|api[_-]?key|client[_-]?secret)[\"']\s*:\s*[\"'][^\"']{8,}[\"']"
    ),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_json_object(data: bytes, member_name: str) -> dict[str, object]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"invalid JSON in packaged member {member_name}") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"packaged member is not a JSON object: {member_name}")
    return value


def verify_d40_validation_binding(members: dict[str, bytes]) -> dict[str, object]:
    readback_bytes = members[D40_READBACK_MEMBER]
    readback_identity = {
        "path": D40_READBACK_MEMBER,
        "bytes": len(readback_bytes),
        "sha256": sha256(readback_bytes),
    }
    if readback_identity != D40_READBACK_IDENTITY:
        raise RuntimeError("D40 independent-readback receipt identity differs")

    validation_receipt = parse_json_object(
        members[VALIDATION_RECEIPT_MEMBER], VALIDATION_RECEIPT_MEMBER
    )
    if validation_receipt.get("state") != "pass":
        raise RuntimeError("packaged validation receipt state is not pass")

    checks = validation_receipt.get("checks")
    if not isinstance(checks, dict):
        raise RuntimeError("packaged validation receipt checks are missing")
    d40_check = checks.get("d40_independent_anonymous_readback")
    if d40_check != "pass_7_of_7":
        raise RuntimeError(
            "packaged validation receipt D40 readback check is not pass_7_of_7"
        )

    artifacts = validation_receipt.get("artifacts")
    if not isinstance(artifacts, dict):
        raise RuntimeError("packaged validation receipt artifacts are missing")
    bound_identity = artifacts.get("d40_independent_anonymous_readback")
    if bound_identity != D40_READBACK_IDENTITY:
        raise RuntimeError(
            "packaged validation receipt does not bind the exact D40 readback identity"
        )

    return {
        "receipt_artifact": dict(readback_identity),
        "validation_receipt": {
            "member": VALIDATION_RECEIPT_MEMBER,
            "state": validation_receipt["state"],
            "check": d40_check,
            "artifact": dict(D40_READBACK_IDENTITY),
        },
    }


def data_identity(data: bytes) -> dict[str, object]:
    return {"bytes": len(data), "sha256": sha256(data)}


def member_identity(members: dict[str, bytes], name: str) -> dict[str, object]:
    data = members.get(name)
    if data is None:
        raise RuntimeError(f"required packaged member is absent: {name}")
    return {"path": name, **data_identity(data)}


def validate_relative_member_path(relative_path: object, label: str) -> str:
    if (
        not isinstance(relative_path, str)
        or not relative_path
        or relative_path.startswith(("/", "\\"))
        or "\\" in relative_path
        or ".." in Path(relative_path).parts
    ):
        raise RuntimeError(f"unsafe {label} path: {relative_path!r}")
    return relative_path


def parse_checksum_rows(data: bytes, member_name: str) -> dict[str, str]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError(f"invalid UTF-8 checksum file: {member_name}") from error
    rows: dict[str, str] = {}
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            raise RuntimeError(
                f"invalid checksum row in {member_name}:{line_number}"
            )
        digest, raw_path = match.groups()
        relative_path = validate_relative_member_path(raw_path, member_name)
        if relative_path in rows:
            raise RuntimeError(f"duplicate checksum path in {member_name}: {relative_path}")
        rows[relative_path] = digest
    return rows


def admitted_input_identities(
    spec: dict[str, object],
    admission: dict[str, object],
    read_member: Callable[[str], bytes],
) -> dict[str, dict[str, object]]:
    label = str(spec["label"])
    raw_inputs = admission.get("inputs")
    expected: dict[str, dict[str, object]] = {}
    if isinstance(raw_inputs, dict):
        for raw_path, raw_identity in raw_inputs.items():
            relative_path = validate_relative_member_path(raw_path, f"{label} admitted")
            if not isinstance(raw_identity, dict):
                raise RuntimeError(f"{label} admitted identity is not an object: {relative_path}")
            byte_count = raw_identity.get("bytes")
            digest = raw_identity.get("sha256")
            if (
                not isinstance(byte_count, int)
                or byte_count < 0
                or not isinstance(digest, str)
                or re.fullmatch(r"[0-9a-f]{64}", digest) is None
            ):
                raise RuntimeError(f"{label} admitted identity is invalid: {relative_path}")
            expected[relative_path] = {"bytes": byte_count, "sha256": digest}
    else:
        # C130's admission binds the checksum file rather than duplicating its
        # complete 64-row digest map. The checksum file plus its admitted own
        # identity is the exact 65-file closure.
        if spec["key"] != "c130_operations_research":
            raise RuntimeError(f"{label} admission inputs are missing")
        checksum_member = f"{spec['root']}/PACKAGE_CHECKSUMS.sha256"
        checksum_reference = admission.get("checksums")
        if not isinstance(checksum_reference, dict):
            raise RuntimeError("C130 admission checksum reference is missing")
        checksum_data = read_member(checksum_member)
        checksum_actual = member_identity_from_data(checksum_member, checksum_data)
        for field in ("path", "bytes", "sha256"):
            if checksum_reference.get(field) != checksum_actual[field]:
                raise RuntimeError(f"C130 admission checksum {field} differs")
        checksum_rows = parse_checksum_rows(checksum_data, checksum_member)
        for relative_path, digest in checksum_rows.items():
            expected[relative_path] = {"sha256": digest}
        expected["PACKAGE_CHECKSUMS.sha256"] = data_identity(checksum_data)

    expected_count = int(spec["input_count"])
    if len(expected) != expected_count:
        raise RuntimeError(
            f"{label} admission must expose exactly {expected_count} inputs; "
            f"found {len(expected)}"
        )
    return expected


def member_identity_from_data(name: str, data: bytes) -> dict[str, object]:
    return {"path": name, **data_identity(data)}


def reference_matches(
    reference: object,
    actual: dict[str, object],
    label: str,
) -> None:
    if not isinstance(reference, dict):
        raise RuntimeError(f"{label} identity is missing")
    for field in ("path", "bytes", "sha256"):
        if reference.get(field) != actual[field]:
            raise RuntimeError(f"{label} {field} differs")


def verify_adapter_package_binding(
    members: dict[str, bytes], spec: dict[str, object]
) -> dict[str, object]:
    label = str(spec["label"])
    root = str(spec["root"])
    archive_member = str(spec["archive"])
    admission_member = str(spec["admission"])
    manifest_member = str(spec["manifest"])
    archive_bytes = members[archive_member]
    archive_identity = member_identity_from_data(archive_member, archive_bytes)
    pinned_archive = {
        "path": archive_member,
        "bytes": spec["archive_bytes"],
        "sha256": spec["archive_sha256"],
    }
    if archive_identity != pinned_archive:
        raise RuntimeError(f"{label} nested archive identity differs")

    admission = parse_json_object(members[admission_member], admission_member)
    if admission.get("state") != spec["admission_state"]:
        raise RuntimeError(f"{label} admission state differs")
    if admission.get("archive") != pinned_archive:
        raise RuntimeError(f"{label} admission archive identity differs")
    for field in ("package_id", "dataset_id"):
        value = admission.get(field)
        if value is None and spec["key"] == "judson_c30_c40":
            continue
        if value != spec[field]:
            raise RuntimeError(f"{label} admission {field.replace('_', ' ')} differs")
    if spec["key"] in {"judson_c30_c40", "c130_operations_research"}:
        if admission.get("independent_trees_identical") is not True:
            raise RuntimeError(f"{label} independent-tree replay is not identical")

    def read_packaged(name: str) -> bytes:
        data = members.get(name)
        if data is None:
            raise RuntimeError(f"{label} admitted member is absent: {name}")
        return data

    admitted_inputs = admitted_input_identities(spec, admission, read_packaged)
    actual_inputs: dict[str, dict[str, object]] = {}
    for relative_path, expected_identity in admitted_inputs.items():
        member = f"{root}/{relative_path}"
        data = read_packaged(member)
        actual_identity = data_identity(data)
        if actual_identity.get("sha256") != expected_identity.get("sha256"):
            raise RuntimeError(f"{label} admitted input hash differs: {relative_path}")
        if "bytes" in expected_identity and actual_identity != expected_identity:
            raise RuntimeError(f"{label} admitted input identity differs: {relative_path}")
        actual_inputs[relative_path] = actual_identity

    expected_input_names = set(admitted_inputs)
    with zipfile.ZipFile(io.BytesIO(archive_bytes), mode="r") as nested:
        infos = nested.infolist()
        nested_names = [info.filename for info in infos]
        if len(nested_names) != int(spec["input_count"]):
            raise RuntimeError(f"{label} nested archive member count differs")
        if len(nested_names) != len(set(nested_names)):
            raise RuntimeError(f"{label} nested archive contains duplicate members")
        if set(nested_names) != expected_input_names:
            raise RuntimeError(f"{label} nested archive inventory differs from admission")
        for info in infos:
            if info.is_dir():
                raise RuntimeError(f"{label} nested archive contains a directory entry")
            validate_relative_member_path(info.filename, f"{label} nested archive")
            nested_data = nested.read(info.filename)
            loose_data = members[f"{root}/{info.filename}"]
            if nested_data != loose_data:
                raise RuntimeError(
                    f"{label} nested/loose member bytes differ: {info.filename}"
                )
            if info.CRC != (zlib.crc32(nested_data) & 0xFFFFFFFF):
                raise RuntimeError(f"{label} nested member CRC differs: {info.filename}")

    total_input_bytes = sum(int(row["bytes"]) for row in actual_inputs.values())
    tree_material = "".join(
        f"{relative_path}\0{actual_inputs[relative_path]['bytes']}\0"
        f"{actual_inputs[relative_path]['sha256']}\n"
        for relative_path in sorted(actual_inputs)
    ).encode("utf-8")
    if admission.get("package_tree_sha256") != sha256(tree_material):
        raise RuntimeError(f"{label} package-tree aggregate hash differs")
    for count_field in ("package_files", "archive_members", "admitted_inputs"):
        value = admission.get(count_field)
        if isinstance(value, int) and value != int(spec["input_count"]):
            raise RuntimeError(f"{label} admission {count_field} differs")
    for bytes_field in ("package_bytes", "archive_member_bytes"):
        value = admission.get(bytes_field)
        if isinstance(value, int) and value != total_input_bytes:
            raise RuntimeError(f"{label} admission {bytes_field} differs")

    manifest_identity = member_identity(members, manifest_member)
    if manifest_identity != {
        "path": manifest_member,
        "bytes": spec["manifest_bytes"],
        "sha256": spec["manifest_sha256"],
    }:
        raise RuntimeError(f"{label} manifest identity differs")
    manifest_reference = admission.get("manifest")
    if isinstance(manifest_reference, dict):
        reference_matches(manifest_reference, manifest_identity, f"{label} admission manifest")
    manifest = parse_json_object(members[manifest_member], manifest_member)
    if manifest.get("package_id") != spec["package_id"]:
        raise RuntimeError(f"{label} manifest package id differs")
    if manifest.get("dataset_id") != spec["dataset_id"]:
        raise RuntimeError(f"{label} manifest dataset id differs")
    manifest_files = manifest.get("files")
    if not isinstance(manifest_files, list) or len(manifest_files) != int(spec["manifest_count"]):
        raise RuntimeError(f"{label} manifest file count differs")
    manifest_paths: set[str] = set()
    for row in manifest_files:
        if not isinstance(row, dict) or row.get("path_base") != "package_root":
            raise RuntimeError(f"{label} manifest contains an unsupported row")
        relative_path = validate_relative_member_path(row.get("path"), f"{label} manifest")
        if relative_path in manifest_paths:
            raise RuntimeError(f"{label} manifest path is duplicated: {relative_path}")
        manifest_paths.add(relative_path)
        if actual_inputs.get(relative_path) != {
            "bytes": row.get("bytes"),
            "sha256": row.get("sha256"),
        }:
            raise RuntimeError(f"{label} manifest identity differs: {relative_path}")
    closure_extras = expected_input_names - manifest_paths
    if closure_extras != {"manifest.json", "seal.json", "PACKAGE_CHECKSUMS.sha256"}:
        raise RuntimeError(f"{label} files outside manifest closure differ")

    seal_member = f"{root}/seal.json"
    seal = parse_json_object(members[seal_member], seal_member)
    seal_files = seal.get("files")
    if not isinstance(seal_files, list) or len(seal_files) != int(spec["seal_count"]):
        raise RuntimeError(f"{label} seal file count differs")
    seal_paths: set[str] = set()
    aggregate_rows: list[dict[str, object]] = []
    for row in seal_files:
        if not isinstance(row, dict) or row.get("path_base") != "package_root":
            raise RuntimeError(f"{label} seal contains an unsupported row")
        relative_path = validate_relative_member_path(row.get("path"), f"{label} seal")
        if relative_path in seal_paths:
            raise RuntimeError(f"{label} seal path is duplicated: {relative_path}")
        seal_paths.add(relative_path)
        expected_identity = {
            "bytes": row.get("bytes"),
            "sha256": row.get("sha256"),
        }
        if actual_inputs.get(relative_path) != expected_identity:
            raise RuntimeError(f"{label} seal identity differs: {relative_path}")
        aggregate_rows.append(
            {"path": relative_path, **expected_identity}
        )
    if seal_paths != manifest_paths | {"manifest.json"}:
        raise RuntimeError(f"{label} seal closure differs from manifest closure")
    if seal.get("file_count") != int(spec["seal_count"]):
        raise RuntimeError(f"{label} seal declared file count differs")
    if seal.get("bytes") != sum(int(row["bytes"]) for row in aggregate_rows):
        raise RuntimeError(f"{label} seal declared byte count differs")
    aggregate_material = "".join(
        f"{row['path']}\0{row['bytes']}\0{row['sha256']}\n"
        for row in sorted(aggregate_rows, key=lambda item: str(item["path"]))
    ).encode("utf-8")
    if seal.get("aggregate_sha256") != sha256(aggregate_material):
        raise RuntimeError(f"{label} seal aggregate hash differs")
    seal_identity = member_identity(members, seal_member)
    if isinstance(admission.get("seal"), dict):
        reference_matches(admission["seal"], seal_identity, f"{label} admission seal")

    checksum_member = f"{root}/PACKAGE_CHECKSUMS.sha256"
    checksum_rows = parse_checksum_rows(members[checksum_member], checksum_member)
    if len(checksum_rows) != int(spec["checksum_count"]):
        raise RuntimeError(f"{label} checksum row count differs")
    if set(checksum_rows) != expected_input_names - {"PACKAGE_CHECKSUMS.sha256"}:
        raise RuntimeError(f"{label} checksum inventory differs")
    for relative_path, digest in checksum_rows.items():
        if actual_inputs[relative_path]["sha256"] != digest:
            raise RuntimeError(f"{label} checksum hash differs: {relative_path}")
    checksum_identity = member_identity(members, checksum_member)
    if isinstance(admission.get("checksums"), dict):
        reference_matches(
            admission["checksums"],
            checksum_identity,
            f"{label} admission checksums",
        )

    count_bindings = {
        "manifest_bound_files_verified": int(spec["manifest_count"]),
        "seal_bound_files_verified": int(spec["seal_count"]),
        "checksum_rows_verified": int(spec["checksum_count"]),
    }
    for field, expected_count in count_bindings.items():
        if field in admission and admission.get(field) != expected_count:
            raise RuntimeError(f"{label} admission {field} differs")

    return {
        "key": spec["key"],
        "archive": archive_identity,
        "admission": member_identity(members, admission_member),
        "manifest": manifest_identity,
        "seal": seal_identity,
        "checksums": checksum_identity,
        "role_bindings": list(spec["role_ids"]),
        "public_package_files_verified": int(spec["input_count"]),
        "manifest_files_verified": int(spec["manifest_count"]),
        "seal_files_verified": int(spec["seal_count"]),
        "checksum_rows_verified": int(spec["checksum_count"]),
        "uncompressed_bytes_verified": total_input_bytes,
    }


def verify_site_binding(
    members: dict[str, bytes],
    spec: dict[str, object],
    adapter_binding: dict[str, object],
) -> dict[str, object]:
    label = str(spec["label"])
    validation_member = str(spec["site_validation"])
    site = parse_json_object(members[validation_member], validation_member)
    if site.get("state") != "pass":
        raise RuntimeError(f"{label} learner-projection validation is not pass")
    admission_identity = adapter_binding["admission"]
    manifest_identity = adapter_binding["manifest"]
    archive_identity = adapter_binding["archive"]

    if spec["key"] == "c130_operations_research":
        imported = site.get("imported_package")
        if not isinstance(imported, dict):
            raise RuntimeError("C130 imported-package site binding is missing")
        reference_matches(site.get("admission"), admission_identity, "C130 site admission")
        reference_matches(imported.get("archive"), archive_identity, "C130 site archive")
        reference_matches(imported.get("manifest"), manifest_identity, "C130 site manifest")
        reference_matches(imported.get("seal"), adapter_binding["seal"], "C130 site seal")
        reference_matches(
            imported.get("checksums"),
            adapter_binding["checksums"],
            "C130 site checksums",
        )
        if imported.get("admitted_inputs") != 65:
            raise RuntimeError("C130 site admitted-input count differs")
        if imported.get("archive_members_decompressed_and_sha256_matched") is not True:
            raise RuntimeError("C130 site archive member verification is not pass")
        expected_semantics = {
            "canonical_records": 51704,
            "identity_crosswalks": 17273,
            "reader_pages": 666,
            "relations": 9545,
            "rights_assignments": 7634,
            "routes": 7,
            "units": 1993,
            "native_html_claimed": False,
            "unit_or_page_anchors_claimed": False,
        }
        semantics = site.get("semantic_counts")
        if not isinstance(semantics, dict):
            raise RuntimeError("C130 site semantic counts are missing")
        for field, expected in expected_semantics.items():
            if semantics.get(field) != expected:
                raise RuntimeError(f"C130 site semantic count differs: {field}")
        routes = site.get("learner_routes")
        if not isinstance(routes, dict) or routes.get("count") != 7:
            raise RuntimeError("C130 learner-route count differs")
        if routes.get("linked_pdf_is_only_primary_reader") is not True:
            raise RuntimeError("C130 linked PDF is not the sole primary reader")
        if routes.get("machine_downloads_are_secondary") is not True:
            raise RuntimeError("C130 machine downloads are not marked secondary")
    else:
        reference_matches(site.get("admission"), admission_identity, f"{label} site admission")
        reference_matches(site.get("archive"), archive_identity, f"{label} site archive")
        reference_matches(site.get("manifest"), manifest_identity, f"{label} site manifest")
        if spec["key"] == "judson_c30_c40":
            if site.get("checked_public_package_inputs") != 65:
                raise RuntimeError("Judson site input count differs")
            if site.get("admitted_courses") != ["C30", "C40"]:
                raise RuntimeError("Judson site course scope differs")
            if site.get("chapter_counts") != {"C30": 15, "C40": 8}:
                raise RuntimeError("Judson chapter counts differ")
            if site.get("native_chapter_joins") != 23:
                raise RuntimeError("Judson native chapter-join count differs")
            evidence = site.get("evidence_document")
            route_member = str(spec["learner_route"])
            if not isinstance(evidence, dict):
                raise RuntimeError("Judson route-evidence binding is missing")
            actual = member_identity(members, route_member)
            if evidence.get("bytes") != actual["bytes"] or evidence.get("sha256") != actual["sha256"]:
                raise RuntimeError("Judson public route-evidence identity differs")
        else:
            if site.get("verified_admitted_inputs") != 67:
                raise RuntimeError("OpenLogic site input count differs")
            semantics = site.get("semantic_counts")
            expected_semantics = {
                "native_units": 722,
                "reversible_prior_v1_mappings": 722,
                "ordered_import_relations": 725,
                "rights_assignments": 728,
                "reader_reachable_units": 642,
                "retained_non_reader_units": 80,
                "native_html": False,
                "unit_or_page_anchors": False,
                "machine_data_is_primary_learner_destination": False,
            }
            if not isinstance(semantics, dict):
                raise RuntimeError("OpenLogic site semantic counts are missing")
            for field, expected in expected_semantics.items():
                if semantics.get(field) != expected:
                    raise RuntimeError(f"OpenLogic site semantic count differs: {field}")
            if site.get("pdf_is_first_learner_action") is not True:
                raise RuntimeError("OpenLogic PDF is not the first learner action")
            if site.get("machine_data_is_secondary") is not True:
                raise RuntimeError("OpenLogic machine data is not marked secondary")

    outputs = site.get(
        "artifacts" if spec["key"] == "judson_c30_c40" else "outputs"
    )
    if not isinstance(outputs, dict):
        raise RuntimeError(f"{label} learner-projection outputs are missing")
    output_root = Path(validation_member).parent.as_posix()
    for filename, reference in outputs.items():
        relative_path = validate_relative_member_path(filename, f"{label} output")
        actual = member_identity(members, f"{output_root}/{relative_path}")
        if not isinstance(reference, dict):
            raise RuntimeError(f"{label} output identity is invalid: {filename}")
        if reference.get("bytes") != actual["bytes"] or reference.get("sha256") != actual["sha256"]:
            raise RuntimeError(f"{label} output identity differs: {filename}")

    route_member = str(spec["learner_route"])
    if spec["key"] != "judson_c30_c40":
        route = parse_json_object(members[route_member], route_member)
        expected_course = str(spec["role_ids"][0])
        if route.get("course_id") != expected_course:
            raise RuntimeError(f"{label} learner-route course id differs")
        adapter = route.get("adapter")
        if not isinstance(adapter, dict):
            raise RuntimeError(f"{label} learner-route adapter binding is missing")
        reference_matches(adapter.get("admission"), admission_identity, f"{label} route admission")
        reference_matches(adapter.get("manifest"), manifest_identity, f"{label} route manifest")
        reference_matches(adapter.get("archive"), archive_identity, f"{label} route archive")

    return {
        "member": validation_member,
        "bytes": len(members[validation_member]),
        "sha256": sha256(members[validation_member]),
        "state": "pass",
    }


def verify_v1_index_binding(members: dict[str, bytes]) -> dict[str, object]:
    public_member = "docs/data/v23-adapter-index-v1.json"
    if members[V23_ADAPTER_INDEX_V1_MEMBER] != members[public_member]:
        raise RuntimeError("immutable v1 adapter-index authority/public bytes differ")
    identity = member_identity(members, V23_ADAPTER_INDEX_V1_MEMBER)
    if identity["bytes"] != 11370 or identity["sha256"] != (
        "31e45fc3a852b1d1b7742ac66d5d919aa1d229feff408913951018451f755381"
    ):
        raise RuntimeError("immutable v1 adapter-index identity differs from v0.62.13")
    index = parse_json_object(
        members[V23_ADAPTER_INDEX_V1_MEMBER], V23_ADAPTER_INDEX_V1_MEMBER
    )
    expected_summary = {
        "curriculum_roles": 40,
        "proof_roles": 5,
        "legacy_proofs": 0,
        "contract_2_3_1_adapters": 5,
        "unbound_roles": 35,
    }
    if index.get("summary") != expected_summary:
        raise RuntimeError("immutable v1 adapter-index summary differs")
    adapters = index.get("adapters")
    if not isinstance(adapters, list) or [row.get("role_id") for row in adapters] != [
        "A00",
        "B10",
        "D20",
        "D60",
        "D110",
    ]:
        raise RuntimeError("immutable v1 adapter-index role closure differs")
    return {"authority": identity, "public_mirror_equal": True, "role_bindings": 5}


def evidence_rows_by_path(
    document: dict[str, object], member_name: str
) -> dict[str, dict[str, object]]:
    rows = document.get("evidence")
    if not isinstance(rows, list):
        raise RuntimeError(f"evidence list is missing: {member_name}")
    result: dict[str, dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError(f"invalid evidence row: {member_name}")
        path = validate_relative_member_path(row.get("path"), f"{member_name} evidence")
        if path in result:
            raise RuntimeError(f"duplicate evidence path in {member_name}: {path}")
        result[path] = row
    return result


def verify_terminology_binding(members: dict[str, bytes]) -> dict[str, object]:
    filenames = ("README.md", "terminology_concordance.json", "checksums.sha256")
    for filename in filenames:
        authority_member = f"{TERMINOLOGY_ROOT}/{filename}"
        public_member = f"{PUBLIC_TERMINOLOGY_ROOT}/{filename}"
        if members[authority_member] != members[public_member]:
            raise RuntimeError(f"terminology authority/public bytes differ: {filename}")

    checksum_member = f"{TERMINOLOGY_ROOT}/checksums.sha256"
    checksum_rows = parse_checksum_rows(members[checksum_member], checksum_member)
    if set(checksum_rows) != {"README.md", "terminology_concordance.json"}:
        raise RuntimeError("terminology checksum closure differs")
    for filename, digest in checksum_rows.items():
        if sha256(members[f"{TERMINOLOGY_ROOT}/{filename}"]) != digest:
            raise RuntimeError(f"terminology checksum differs: {filename}")

    concordance = parse_json_object(
        members[TERMINOLOGY_CONCORDANCE_MEMBER], TERMINOLOGY_CONCORDANCE_MEMBER
    )
    if concordance.get("schema") != "interlanguage-native-terminology-qa-v1":
        raise RuntimeError("terminology concordance schema differs")
    qa_result = concordance.get("qa_result")
    if not isinstance(qa_result, dict):
        raise RuntimeError("terminology QA result is missing")
    if qa_result.get("restricted_prose_copied") is not False:
        raise RuntimeError("terminology packet reports copied restricted prose")
    if qa_result.get("result") != "complete_with_manager_correction_queue":
        raise RuntimeError("terminology packet completion result differs")

    return {
        "authority": member_identity(members, TERMINOLOGY_CONCORDANCE_MEMBER),
        "authority_public_files_equal": 3,
        "checksum_rows_verified": 2,
    }


def verify_terminology_policy_binding(members: dict[str, bytes]) -> dict[str, object]:
    mirror_pairs = (
        TERMINOLOGY_POLICY_DATA_MIRROR_PAIRS
        + TERMINOLOGY_POLICY_SCHEMA_MIRROR_PAIRS
    )
    for authority_member, public_member in mirror_pairs:
        if members[authority_member] != members[public_member]:
            raise RuntimeError(
                "terminology-policy authority/public bytes differ: "
                f"{authority_member}"
            )

    checksum_member = f"{TERMINOLOGY_POLICY_ROOT}/checksums.sha256"
    checksum_rows = parse_checksum_rows(members[checksum_member], checksum_member)
    if set(checksum_rows) != {"README.md", "canonical-register-policy.json"}:
        raise RuntimeError("terminology-policy checksum closure differs")
    for filename, digest in checksum_rows.items():
        if sha256(members[f"{TERMINOLOGY_POLICY_ROOT}/{filename}"]) != digest:
            raise RuntimeError(f"terminology-policy checksum differs: {filename}")

    policy = parse_json_object(
        members[TERMINOLOGY_POLICY_MEMBER], TERMINOLOGY_POLICY_MEMBER
    )
    if policy.get("schema_id") != (
        "interlanguage/program-matematika-indonesia-"
        "canonical-terminology-register-policy/v1"
    ):
        raise RuntimeError("terminology-policy schema id differs")
    if policy.get("locale") != "id-ID":
        raise RuntimeError("terminology-policy locale differs")
    decision_procedure = policy.get("decision_procedure")
    if not isinstance(decision_procedure, list) or [
        row.get("sequence") if isinstance(row, dict) else None
        for row in decision_procedure
    ] != list(range(1, 10)):
        raise RuntimeError("terminology-policy decision procedure differs")

    termbase_contract = policy.get("termbase_contract")
    if not isinstance(termbase_contract, dict) or termbase_contract.get(
        "schema_id"
    ) != "interlanguage/program-matematika-indonesia-terminology-concept/v1":
        raise RuntimeError("terminology-policy concept-record binding differs")

    probability_family = policy.get("probability_family_audit")
    if not isinstance(probability_family, dict):
        raise RuntimeError("terminology-policy probability-family audit is missing")
    concepts = probability_family.get("concepts")
    if (
        probability_family.get("status") != "evidence_required"
        or probability_family.get("automatic_replacement_allowed") is not False
        or not isinstance(concepts, list)
        or len(concepts) != 9
    ):
        raise RuntimeError("terminology-policy probability-family boundary differs")
    concept_ids = [
        row.get("concept_id") if isinstance(row, dict) else None for row in concepts
    ]
    if (
        len(set(concept_ids)) != 9
        or any(not isinstance(concept_id, str) for concept_id in concept_ids)
        or any(
            not isinstance(row, dict)
            or row.get("decision_state") != "evidence_required"
            or not isinstance(row.get("search_forms"), list)
            or not all(isinstance(form, str) for form in row["search_forms"])
            or not any("peluang" in form for form in row["search_forms"])
            or not any("probabilitas" in form for form in row["search_forms"])
            for row in concepts
        )
    ):
        raise RuntimeError("terminology-policy probability concepts differ")

    expected_schema_ids = {
        TERMINOLOGY_POLICY_SCHEMA_MIRROR_PAIRS[0][0]: (
            "https://kokunoyumeto.github.io/program-matematika-indonesia/"
            "schema/course-capsule-v1/v2/"
            "canonical-terminology-register-policy-v1.schema.json"
        ),
        TERMINOLOGY_POLICY_SCHEMA_MIRROR_PAIRS[1][0]: (
            "https://kokunoyumeto.github.io/program-matematika-indonesia/"
            "schema/course-capsule-v1/v2/terminology-concept-record-v1.schema.json"
        ),
    }
    for schema_member, expected_id in expected_schema_ids.items():
        schema = parse_json_object(members[schema_member], schema_member)
        if (
            schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
            or schema.get("$id") != expected_id
        ):
            raise RuntimeError(f"terminology-policy schema identity differs: {schema_member}")

    return {
        "authority": member_identity(members, TERMINOLOGY_POLICY_MEMBER),
        "authority_public_mirror_pairs_equal": len(mirror_pairs),
        "checksum_rows_verified": 2,
        "probability_concepts_audited": len(concepts),
        "probability_family_state": probability_family["status"],
    }


def verify_v2_snapshot_binding(
    members: dict[str, bytes],
    adapter_bindings: dict[str, dict[str, object]],
) -> dict[str, object]:
    for authority_member, public_member in V2_DATA_MIRROR_PAIRS + V2_SCHEMA_MIRROR_PAIRS:
        if members[authority_member] != members[public_member]:
            raise RuntimeError(
                f"v2 authority/public mirror bytes differ: {authority_member}"
            )
    if members[V2_RECEIPT_MEMBER] != members[V2_PUBLIC_RECEIPT_MEMBER]:
        raise RuntimeError("v2 validation-receipt authority/public bytes differ")

    index = parse_json_object(
        members[V23_ADAPTER_INDEX_V2_MEMBER], V23_ADAPTER_INDEX_V2_MEMBER
    )
    pattern = parse_json_object(members[V2_PATTERN_INDEX_MEMBER], V2_PATTERN_INDEX_MEMBER)
    feature = parse_json_object(
        members[V2_FEATURE_PROVENANCE_MEMBER], V2_FEATURE_PROVENANCE_MEMBER
    )
    comparison = parse_json_object(
        members[V2_COMPARISON_EVIDENCE_MEMBER], V2_COMPARISON_EVIDENCE_MEMBER
    )
    receipt = parse_json_object(members[V2_RECEIPT_MEMBER], V2_RECEIPT_MEMBER)

    if index.get("summary") != EXPECTED_V2_SUMMARY:
        raise RuntimeError("v2 adapter-index summary differs")
    if receipt.get("status") != "pass" or receipt.get("summary") != EXPECTED_V2_SUMMARY:
        raise RuntimeError("v2 validation receipt status or summary differs")
    snapshot = index.get("snapshot")
    if not isinstance(snapshot, dict):
        raise RuntimeError("v2 adapter-index snapshot is missing")
    snapshot_id = snapshot.get("snapshot_id")
    if (
        not isinstance(snapshot_id, str)
        or snapshot.get("mutable_overlay") is not True
        or snapshot.get("central_release_version") != "v0.62.14"
        or snapshot.get("central_release_record_doi") != "10.5281/zenodo.22217240"
        or snapshot.get("public_replay_state")
        != "postpublication_release_assets_readback_complete"
    ):
        raise RuntimeError("v2 adapter-index postpublication snapshot binding differs")
    pattern_snapshot = pattern.get("snapshot")
    if not isinstance(pattern_snapshot, dict) or pattern_snapshot.get("snapshot_id") != snapshot_id:
        raise RuntimeError("v2 pattern snapshot id differs")
    for document, label in (
        (feature, "feature provenance"),
        (comparison, "comparison evidence"),
        (receipt, "validation receipt"),
    ):
        if document.get("snapshot_id") != snapshot_id:
            raise RuntimeError(f"v2 {label} snapshot id differs")

    if index.get("policy") != {
        "aggregate_conformance_claim": False,
        "machine_data_secondary": True,
        "owner_native_authoritative": True,
        "zero_copy": True,
    }:
        raise RuntimeError("v2 adapter-index policy differs")

    packages = index.get("packages")
    adapters = index.get("adapters")
    if not isinstance(packages, list) or len(packages) != 8:
        raise RuntimeError("v2 adapter package count differs")
    if not isinstance(adapters, list) or len(adapters) != 9:
        raise RuntimeError("v2 role-binding count differs")
    package_by_id: dict[str, dict[str, object]] = {}
    for package in packages:
        if not isinstance(package, dict) or not isinstance(package.get("package_id"), str):
            raise RuntimeError("v2 adapter package row is invalid")
        package_id = str(package["package_id"])
        if package_id in package_by_id:
            raise RuntimeError(f"duplicate v2 adapter package id: {package_id}")
        package_by_id[package_id] = package
        if package.get("owner_native_authoritative") is not True:
            raise RuntimeError(f"v2 package is not owner-native authoritative: {package_id}")
        if package.get("zero_copy") is not True:
            raise RuntimeError(f"v2 package is not zero-copy: {package_id}")

    expected_roles = list(EXPECTED_V2_ROLE_ORDER)
    actual_roles = [row.get("role_id") if isinstance(row, dict) else None for row in adapters]
    if actual_roles != expected_roles or len(set(actual_roles)) != 9:
        raise RuntimeError("v2 adapter role order or uniqueness differs")
    for adapter in adapters:
        if not isinstance(adapter, dict):
            raise RuntimeError("v2 adapter role row is invalid")
        package_id = adapter.get("adapter_package_id")
        if package_id not in package_by_id:
            raise RuntimeError(f"v2 adapter role has no package: {adapter.get('role_id')}")

    published_packages = [
        row for row in packages if row.get("admission_state") == "published"
    ]
    pending_packages = [
        row for row in packages if row.get("admission_state") == "admitted_pending_release"
    ]
    if len(published_packages) != 8 or pending_packages:
        raise RuntimeError("v2 published/pending package split differs")
    published_bindings = sum(
        package_by_id[str(row["adapter_package_id"])].get("admission_state")
        == "published"
        for row in adapters
    )
    if published_bindings != 9 or len(adapters) - published_bindings != 0:
        raise RuntimeError("v2 published/pending role split differs")
    canonical_total = sum(int(row.get("canonical_records", -1)) for row in packages)
    if canonical_total != 285829:
        raise RuntimeError("v2 deduplicated canonical-record total differs")

    role_rows = {str(row["role_id"]): row for row in adapters}
    for spec in ADAPTER_SPECS:
        binding = adapter_bindings[str(spec["key"])]
        package = package_by_id.get(str(spec["package_id"]))
        if package is None:
            raise RuntimeError(f"v2 package is missing: {spec['label']}")
        if package.get("dataset_id") != spec["dataset_id"]:
            raise RuntimeError(f"v2 dataset id differs: {spec['label']}")
        if package.get("admission_state") != "published":
            raise RuntimeError(f"v2 admission state differs: {spec['label']}")
        if package.get("public_replay_status") != "published_public_asset_readback_verified":
            raise RuntimeError(f"v2 replay state differs: {spec['label']}")
        if not package.get("public_asset_url") or not package.get("release_url"):
            raise RuntimeError(f"v2 published package lacks a release URL: {spec['label']}")
        if "planned_release" in package:
            raise RuntimeError(f"v2 published package retains a planned release: {spec['label']}")
        reference_matches(package.get("archive"), binding["archive"], f"v2 {spec['label']} archive")
        reference_matches(
            package.get("manifest"), binding["manifest"], f"v2 {spec['label']} manifest"
        )
        for field, expected in EXPECTED_V2_PACKAGE_FIELDS[str(spec["key"])].items():
            if package.get(field) != expected:
                raise RuntimeError(f"v2 {spec['label']} package field differs: {field}")
        for role_id in spec["role_ids"]:
            row = role_rows.get(str(role_id))
            if row is None or row.get("adapter_package_id") != spec["package_id"]:
                raise RuntimeError(f"v2 package binding differs: {role_id}")
            if row.get("learner_runtime_relationship") != spec["relationship"]:
                raise RuntimeError(f"v2 learner relationship differs: {role_id}")
            projection = row.get("central_learner_projection")
            expected_projection = (
                "docs/backend/judson/" if spec["key"] == "judson_c30_c40" else
                "docs/backend/openlogic/" if spec["key"] == "openlogic_c80" else
                "docs/backend/c130/"
            ) + f"{role_id}.html"
            if not isinstance(projection, dict) or projection.get("path") != expected_projection:
                raise RuntimeError(f"v2 learner projection differs: {role_id}")
            if projection.get("status") != "published":
                raise RuntimeError(f"v2 learner projection is not published: {role_id}")

    index_identity = member_identity(members, V23_ADAPTER_INDEX_V2_MEMBER)
    adapter_snapshot = pattern.get("adapter_snapshot")
    if not isinstance(adapter_snapshot, dict):
        raise RuntimeError("v2 pattern adapter snapshot is missing")
    reference_matches(
        adapter_snapshot.get("adapter_index"), index_identity, "v2 pattern adapter index"
    )
    for field in (
        "distinct_adapter_packages",
        "families_without_local_adapter",
        "families_without_public_replay_complete_adapter",
        "pending_role_bindings",
        "published_role_bindings",
        "represented_native_families",
        "role_bindings",
        "unbound_roles",
    ):
        if adapter_snapshot.get(field) != EXPECTED_V2_SUMMARY[field]:
            raise RuntimeError(f"v2 pattern adapter summary differs: {field}")
    families = pattern.get("families")
    if not isinstance(families, list) or len(families) != 33:
        raise RuntimeError("v2 pattern family count differs")
    family_roles = [role for row in families if isinstance(row, dict) for role in row.get("roles", [])]
    if len(family_roles) != 40 or len(set(family_roles)) != 40:
        raise RuntimeError("v2 pattern family role closure differs")
    c130_family = next(
        (
            row
            for row in families
            if isinstance(row, dict)
            and row.get("native_family_id") == "family-20-operations-research"
        ),
        None,
    )
    expected_c130_binding = {
        "adapter_package_id": ADAPTER_SPECS[2]["package_id"],
        "admission_state": "published",
        "public_replay_status": "published_public_asset_readback_verified",
        "role_id": "C130",
    }
    if c130_family is None or c130_family.get("adapter_bindings") != [expected_c130_binding]:
        raise RuntimeError("v2 C130 pattern-family binding differs")

    feature_rows = evidence_rows_by_path(feature, V2_FEATURE_PROVENANCE_MEMBER)
    comparison_rows = evidence_rows_by_path(
        comparison, V2_COMPARISON_EVIDENCE_MEMBER
    )
    bound_evidence_members = [TERMINOLOGY_CONCORDANCE_MEMBER]
    for spec in ADAPTER_SPECS:
        bound_evidence_members.extend((str(spec["admission"]), str(spec["manifest"])))
    bound_evidence_members.extend((
        "backend/course-capsule-v1/validation/C130_AUTHORITY_REPLAY_RECEIPT_20260901.json",
        "GITHUB_PUBLICATION_RECEIPT_v0.62.14.json",
        "PUBLICATION_RECEIPT_v0.62.14.json",
    ))
    for evidence_member in bound_evidence_members:
        actual = member_identity(members, evidence_member)
        reference_matches(
            feature_rows.get(evidence_member), actual, f"v2 feature evidence {evidence_member}"
        )
        reference_matches(
            comparison_rows.get(evidence_member),
            actual,
            f"v2 comparison evidence {evidence_member}",
        )
    reference_matches(
        feature_rows.get(V23_ADAPTER_INDEX_V2_MEMBER),
        index_identity,
        "v2 feature adapter snapshot",
    )
    if feature.get("policy") != {
        "course_native_authoritative": True,
        "human_evidence_is_not_a_release_gate": True,
        "unsupported_claims_forbidden": True,
        "zero_copy": True,
    }:
        raise RuntimeError("v2 feature-provenance policy differs")
    if not isinstance(feature.get("layers"), list) or len(feature["layers"]) != 7:
        raise RuntimeError("v2 feature-provenance layer count differs")
    sanitization = comparison.get("sanitization")
    if not isinstance(sanitization, dict) or any(
        sanitization.get(field) is not True
        for field in (
            "absolute_local_paths_excluded",
            "coordination_transcripts_excluded",
            "credentials_excluded",
            "public_safe_repository_relative_paths_only",
        )
    ):
        raise RuntimeError("v2 comparison-evidence sanitization differs")

    validated_files = receipt.get("validated_files")
    canonical_v2_members = [
        authority for authority, _public in V2_DATA_MIRROR_PAIRS + V2_SCHEMA_MIRROR_PAIRS
    ]
    if not isinstance(validated_files, list) or len(validated_files) != 8:
        raise RuntimeError("v2 validation receipt file closure differs")
    validated_by_path: dict[str, dict[str, object]] = {}
    for row in validated_files:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("v2 validation receipt contains an invalid file row")
        if row["path"] in validated_by_path:
            raise RuntimeError(f"duplicate v2 receipt path: {row['path']}")
        validated_by_path[str(row["path"])] = row
    if set(validated_by_path) != set(canonical_v2_members):
        raise RuntimeError("v2 validation receipt inventory differs")
    for canonical_member in canonical_v2_members:
        reference_matches(
            validated_by_path[canonical_member],
            member_identity(members, canonical_member),
            f"v2 receipt {canonical_member}",
        )
    reference_matches(
        receipt.get("validator"),
        member_identity(members, V2_VALIDATOR_MEMBER),
        "v2 validation receipt validator",
    )

    return {
        "snapshot_id": snapshot_id,
        "summary": dict(EXPECTED_V2_SUMMARY),
        "authority_public_mirror_pairs_equal": 8,
        "validation_receipt_mirror_equal": True,
        "validated_authority_files": 8,
        "receipt": member_identity(members, V2_RECEIPT_MEMBER),
    }


def verify_all_bindings(members: dict[str, bytes]) -> dict[str, object]:
    adapter_bindings: dict[str, dict[str, object]] = {}
    site_bindings: dict[str, dict[str, object]] = {}
    for spec in ADAPTER_SPECS:
        key = str(spec["key"])
        adapter_bindings[key] = verify_adapter_package_binding(members, spec)
        site_bindings[key] = verify_site_binding(members, spec, adapter_bindings[key])
    return {
        "d40": verify_d40_validation_binding(members),
        "v1_adapter_index": verify_v1_index_binding(members),
        "adapters": adapter_bindings,
        "learner_projections": site_bindings,
        "terminology": verify_terminology_binding(members),
        "terminology_policy": verify_terminology_policy_binding(members),
        "v2_snapshot": verify_v2_snapshot_binding(members, adapter_bindings),
    }


def read_required_disk_member(name: str) -> bytes:
    path = ROOT / Path(name)
    if not path.is_file():
        raise FileNotFoundError(f"required file is missing: {name}")
    return path.read_bytes()


def required_member_names() -> list[str]:
    c130_dependencies = (
        ADAPTER_SPECS[2]["admission"],
        "docs/backend/c130/C130.html",
        "docs/backend/c130/learner-route.json",
        "docs/backend/c130/validation.json",
        "scripts/build-c130-course-capsule-v1.mjs",
    )
    missing_c130 = [
        str(name) for name in c130_dependencies if not (ROOT / Path(str(name))).is_file()
    ]
    if missing_c130:
        raise FileNotFoundError(
            "C130 package dependencies are missing: " + ", ".join(missing_c130)
        )

    if len(EXACT_MEMBERS) != EXPECTED_STATIC_MEMBER_COUNT:
        raise RuntimeError(
            f"static member declaration must contain {EXPECTED_STATIC_MEMBER_COUNT} rows"
        )
    names = set(EXACT_MEMBERS)
    if len(names) != EXPECTED_STATIC_MEMBER_COUNT:
        raise RuntimeError("static member declaration contains duplicate paths")

    derived_expected_count = len(EXACT_MEMBERS)
    for spec in ADAPTER_SPECS:
        admission_member = str(spec["admission"])
        admission = parse_json_object(
            read_required_disk_member(admission_member), admission_member
        )
        admitted_inputs = admitted_input_identities(
            spec, admission, read_required_disk_member
        )
        derived_expected_count += len(admitted_inputs) + 2
        names.add(admission_member)
        names.add(str(spec["archive"]))
        for relative_path in admitted_inputs:
            names.add(f"{spec['root']}/{relative_path}")

    overlap = names & FORBIDDEN_MEMBERS
    if overlap:
        raise RuntimeError(f"forbidden integration files selected: {sorted(overlap)}")
    forbidden_prefix_members = sorted(
        name
        for name in names
        if any(name.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)
    )
    if forbidden_prefix_members:
        raise RuntimeError(
            "forbidden integration prefixes selected: "
            + ", ".join(forbidden_prefix_members)
        )
    if derived_expected_count != EXPECTED_MEMBER_COUNT:
        raise RuntimeError(
            "admission-derived member count differs from the declared exact closure"
        )
    if len(names) != derived_expected_count:
        raise RuntimeError(
            f"exact package closure must contain {derived_expected_count} members; "
            f"found {len(names)}"
        )
    return sorted(names)


def collect_members() -> dict[str, bytes]:
    members: dict[str, bytes] = {}
    for name in required_member_names():
        data = read_required_disk_member(name)
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(data):
                raise RuntimeError(f"private absolute path rejected in {name}")
        for pattern in CREDENTIAL_PATTERNS:
            if pattern.search(data):
                raise RuntimeError(f"credential-shaped material rejected in {name}")
        members[name] = data
    if list(members) != sorted(members):
        raise RuntimeError("collected package member closure is not exact and sorted")
    return members


def write_zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(
        path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for name, data in members.items():
            info = zipfile.ZipInfo(filename=name, date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(
                info,
                data,
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )


def verify_zip(path: Path, members: dict[str, bytes]) -> dict[str, object]:
    expected_names = list(members)
    if len(expected_names) != len(set(expected_names)):
        raise RuntimeError("ZIP expected-member closure contains duplicates")
    with zipfile.ZipFile(path, mode="r") as archive:
        infos = archive.infolist()
        actual_names = [info.filename for info in infos]
        if actual_names != expected_names:
            raise RuntimeError("ZIP member order or inventory differs from the exact closure")
        if len(actual_names) != len(set(actual_names)):
            raise RuntimeError("ZIP contains duplicate member names")
        if any(
            name in FORBIDDEN_MEMBERS
            or any(name.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)
            for name in actual_names
        ):
            raise RuntimeError("ZIP contains a forbidden member or prefix")
        if archive.testzip() is not None:
            raise RuntimeError("ZIP CRC verification failed")
        for info in infos:
            expected = members[info.filename]
            data = archive.read(info.filename)
            if data != expected:
                raise RuntimeError(f"ZIP member bytes differ: {info.filename}")
            if info.CRC != (zlib.crc32(expected) & 0xFFFFFFFF):
                raise RuntimeError(f"ZIP member CRC differs: {info.filename}")
            if info.date_time != FIXED_TIMESTAMP:
                raise RuntimeError(f"ZIP member timestamp differs: {info.filename}")
            if info.create_system != 3 or info.external_attr != 0o100644 << 16:
                raise RuntimeError(f"ZIP member mode metadata differs: {info.filename}")
    return verify_all_bindings(members)


def canonical_json_bytes(value: dict[str, object]) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def write_atomic_receipt(path: Path, value: dict[str, object]) -> dict[str, object]:
    data = canonical_json_bytes(value)
    for pattern in PRIVATE_PATH_PATTERNS + CREDENTIAL_PATTERNS:
        if pattern.search(data):
            raise RuntimeError("package receipt sanitization failed")
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
    if path.read_bytes() != data:
        raise RuntimeError("atomic package-receipt readback differs")
    return member_identity_from_data(path.relative_to(ROOT).as_posix(), data)


def main() -> None:
    members = collect_members()
    bindings = verify_all_bindings(members)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="course-capsule-v1-") as temp_dir:
        first = Path(temp_dir) / "first.zip"
        second = Path(temp_dir) / "second.zip"
        write_zip(first, members)
        write_zip(second, members)
        verify_zip(first, members)
        verify_zip(second, members)
        first_bytes = first.read_bytes()
        second_bytes = second.read_bytes()
        if first_bytes != second_bytes:
            raise RuntimeError("two-build deterministic replay differs")
        os.replace(first, OUTPUT)

    bindings = verify_zip(OUTPUT, members)
    archive_bytes = OUTPUT.read_bytes()
    archive_identity = member_identity_from_data(
        OUTPUT.relative_to(ROOT).as_posix(), archive_bytes
    )
    receipt = {
        "schema_id": "interlanguage/course-capsule-package-build-receipt/v2",
        "state": "pass",
        "archive": archive_identity,
        "member_count": len(members),
        "payload_bytes": sum(len(data) for data in members.values()),
        "member_names": list(members),
        "bindings": bindings,
        "verification": {
            "admission_driven_adapter_closures_exact": True,
            "allow_list_exact": True,
            "credential_scan_pass": True,
            "d40_readback_receipt_binding_exact": True,
            "fixed_timestamps_and_modes": True,
            "forbidden_members_and_prefixes_absent": True,
            "member_bytes_and_crc_exact": True,
            "nested_archive_crc_name_and_bytes_exact": True,
            "private_path_scan_pass": True,
            "terminology_authority_public_mirrors_exact": True,
            "two_build_byte_replay_pass": True,
            "v1_immutable_index_binding_exact": True,
            "v2_authority_schema_receipt_closure_exact": True,
        },
    }
    receipt_identity = write_atomic_receipt(PACKAGE_RECEIPT, receipt)
    result = dict(receipt)
    result["package_receipt"] = receipt_identity
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
