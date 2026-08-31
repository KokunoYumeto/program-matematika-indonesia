#!/usr/bin/env python3
"""Preflight or assemble the exact 100-file v0.62.13 backend release.

The successor boundary is deliberately finite and explicit:

* retain 78 files byte-for-byte from the verified public v0.62.12 payload;
* replace 9 predecessor filenames with validated v0.62.13 bytes;
* omit 13 predecessor-only filenames that remain public in that record;
* add 13 genuinely new v0.62.13 filenames, including release notes and the
  99-row checksum manifest; and
* generate the source ZIP as an exact deterministic ``git archive`` of an
  explicitly supplied commit whose tree is independently supplied and checked.

The assembly modes are local and credential-free. ``--preflight`` assembles
and validates only inside a temporary directory. ``--build`` uses an atomic
temporary directory under ``releases`` and never overwrites an existing
release. An existing ``releases/v0.62.13`` is accepted only when all 100
filenames and every byte are identical to a freshly assembled expectation.
``--hydrate-predecessor`` is the sole networked mode: it anonymously restores
an absent ``releases/v0.62.12`` from the exact URLs and byte identities sealed
in its pinned publication receipt, and refuses to replace any existing path.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from http.client import HTTPException
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import ProxyHandler, Request, build_opener


VERSION = "0.62.13"
PREDECESSOR_VERSION = "0.62.12"
PROJECT = Path(__file__).resolve().parents[1]
RELEASES_DIR = PROJECT / "releases"
PREDECESSOR_DIR = RELEASES_DIR / f"v{PREDECESSOR_VERSION}"
PREDECESSOR_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.12.json"
PREDECESSOR_GITHUB_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.12.json"
OUTPUT_DIR = RELEASES_DIR / f"v{VERSION}"

EXPECTED_PREDECESSOR_RECEIPT = (
    51_506,
    "5867905ef9bd9c819cd5998d1f7758e023392249e3aad91106399bd8b479ac3a",
)
EXPECTED_PREDECESSOR_GITHUB_RECEIPT = (
    54_665,
    "24676adb7024320fb3bc123a34284de88276ca69d78c44e3fe29eb114a4c3965",
)
EXPECTED_PREDECESSOR_TOTAL_BYTES = 131_739_644
EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE = (
    "3254b566c27819c2230ecf4ef2009879058e6bd41359b3926bd5e3fc36fd7c33"
)
EXPECTED_PREDECESSOR_RECORD_ID = 22_182_000
EXPECTED_PREDECESSOR_TAG_COMMIT = "590f25ebf033038425b8b84564bc81dd620edb38"
EXPECTED_PREDECESSOR_TAG_TREE = "15e370575cc50fb966eaaadf5b26fb4d708faa24"
EXPECTED_PREDECESSOR_MAIN_COMMIT = "15d37eea2f84ea7c4e856e81af0c4411828713b4"
EXPECTED_PREDECESSOR_MAIN_TREE = "94ed2940c858012e7e4465151c4e1e25371cbf1d"
EXPECTED_REPOSITORY = "https://github.com/KokunoYumeto/program-matematika-indonesia"
EXPECTED_RELEASE_URL = f"{EXPECTED_REPOSITORY}/releases/tag/v0.62.12"
EXPECTED_CONCEPT_DOI = "10.5281/zenodo.22059707"
EXPECTED_VERSION_DOI = "10.5281/zenodo.22182000"
EXPECTED_A00_REPOSITORY = "https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID"
PREDECESSOR_ANONYMOUS_URL_ROOT = (
    f"https://zenodo.org/api/records/{EXPECTED_PREDECESSOR_RECORD_ID}/files"
)
PREDECESSOR_HYDRATION_TEMP_PREFIX = ".v0.62.12-hydrate-"
PREDECESSOR_DOWNLOAD_TIMEOUT_SECONDS = 180
PREDECESSOR_DOWNLOAD_USER_AGENT = "program-matematika-indonesia-v0.62.13-predecessor-hydrator/1"
CANONICAL_ZENODO_DOI_URL = re.compile(
    r"https://doi\.org/10\.5281/zenodo\.([1-9][0-9]*)"
)

# This is an allowlist, not a computed remainder. Its cardinality and exact
# equality with the predecessor receipt are checked before any assembly.
RETAINED_ALLOWLIST = frozenset(
    {
        "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.62.0.pdf",
        "142_PUBLIC_OWNER_HTML_ROUTE_READBACK_V062_20260828.json",
        "168_B10_V23_ADAPTER_VALIDATION_V020_FINAL_20260830.json",
        "169_B10_V23_ADAPTER_CANONICAL_ADMISSION_20260830.json",
        "170_B10_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260830.json",
        "175_D60_V231_ADAPTER_VALIDATION_V010_FINAL_20260830.json",
        "176_D60_V231_ADAPTER_CANONICAL_ADMISSION_20260830.json",
        "177_D60_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260830.json",
        "183_D110_V231_ADAPTER_VALIDATION_V010_FINAL_20260830.json",
        "184_D110_V231_ADAPTER_CANONICAL_ADMISSION_20260830.json",
        "185_D110_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260830.json",
        "191_D20_V231_ADAPTER_VALIDATION_V010_FINAL_20260831.json",
        "192_D20_V231_ADAPTER_CANONICAL_ADMISSION_20260831.json",
        "193_D20_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260831.json",
        "190_LEARNER_ACCESS_OFFLINE_DELIVERY_TRANCHE_20260830.json",
        "194_GLOBAL_MODULAR_BACKEND_LEARNER_DELIVERY_INTEGRATION_20260831.json",
        "applied-combinatorics-id-backend-v1-migration-receipt.json",
        "BACKEND_CONVERGENCE_V1.md",
        "backend-migration-receipt-v2.schema.json",
        "build-backend-v2-federation.py",
        "build-backend-v2-validation-receipt.py",
        "curriculum-authority-v1.json",
        "curriculum-authority-v1.schema.json",
        "dmoi4-id-backend-v1-migration-receipt.json",
        "erdman-functional-analysis-id-backend-v1-migration-receipt.json",
        "federation-package-v2.schema.json",
        "federation-record-v2.schema.json",
        "federation-unit-package-v2.1.schema.json",
        "federation-unit-record-v2.1.schema.json",
        "GITHUB_B10_V231_SOURCE_PUBLICATION_RECEIPT.json",
        "GITHUB_D110_V231_SOURCE_PUBLICATION_RECEIPT.json",
        "GITHUB_D20_V231_SOURCE_PUBLICATION_RECEIPT.json",
        "GITHUB_D60_V231_SOURCE_PUBLICATION_RECEIPT.json",
        "GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v0.62.0.json",
        "GLOBAL_BACKEND_V21_DETERMINISTIC_REPLAY_RECEIPT_v0.62.0.json",
        "GLOBAL_BACKEND_V22_ARCHIVE_RECEIPT_v0.62.0.json",
        "GLOBAL_BACKEND_V22_VALIDATION_RECEIPT_v0.62.0.json",
        "GLOBAL_BACKEND_V23_ARCHIVE_DETERMINISM_RECEIPT_v0.62.5.json",
        "GLOBAL_BACKEND_V23_SCOPE_ADMISSION_RECEIPT_v0.62.5.json",
        "GLOBAL_BACKEND_V23_VALIDATION_RECEIPT_v0.62.5.json",
        "global-capability-contract-v0.1.0.json",
        "global-capability-contract-v0.1.schema.json",
        "hefferon-linear-algebra-id-backend-v1-migration-receipt.json",
        "interlanguage-backend-migration-receipt-v1.schema.json",
        "interlanguage-math-backend-v1.schema.json",
        "interlanguage-source-format-profile-v1.schema.json",
        "judson-id-backend-v1-migration-receipt.json",
        "learner-read-model-v1.json",
        "learner-read-model-v1.schema.json",
        "learner-state-v1.schema.json",
        "learner-state.js",
        "learner-delivery-v1.schema.json",
        "LOCAL_RELEASE_VALIDATION_v0.62.0.json",
        "mathematics-in-lean-id-backend-v1-migration-receipt.json",
        "MIGRATION_HANDOFF_V1.md",
        "namespace-v2.json",
        "o002-b80-id-backend-v1-migration-receipt.json",
        "o005-c120-id-backend-v1-migration-receipt.json",
        "o018-c130-id-backend-v1-migration-receipt.json",
        "openlogic-id-backend-v1-migration-receipt.json",
        "pmi-release-policy-v2.json",
        "prealgebra2e-id-backend-v1-migration-receipt.json",
        "program-matematika-indonesia-backend-v1-v0.62.0.zip",
        "program-matematika-indonesia-backend-v1-validation-v0.62.0.json",
        "program-matematika-indonesia-backend-v2-v0.62.0.zip",
        "program-matematika-indonesia-backend-v2.1-pilots-v0.62.0.zip",
        "program-matematika-indonesia-backend-v2.2-v0.62.0.zip",
        "program-matematika-indonesia-backend-v2.3-conformance-v0.1.1.zip",
        "program-matematika-indonesia-backend-v2.3.1-b10-adapter-v0.2.0.zip",
        "program-matematika-indonesia-backend-v2.3.1-d110-adapter-v0.1.0.zip",
        "program-matematika-indonesia-backend-v2.3.1-d20-adapter-v0.1.0.zip",
        "program-matematika-indonesia-backend-v2.3.1-d60-adapter-v0.1.0.zip",
        "program-matematika-indonesia-catalog-v0.62.0.json",
        "program-matematika-indonesia-catalog-v1.schema.json",
        "program-matematika-indonesia-og-v0.62.0.png",
        "tea-time-id-backend-v1-migration-receipt.json",
        "validate-backend-v2-federation.py",
        "yaintt-id-backend-v1-migration-receipt.json",
    }
)

SAME_NAME_REPLACEMENTS = frozenset(
    {
        "course-capsule-v1.schema.json",
        "course-capsules-v1.jsonl",
        "learner-delivery-v1.json",
        "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md",
        "modular-backend-pattern-index-v1.json",
        "peta-belajar-luring.html",
        "program-matematika-indonesia-course-capsule-v1.zip",
        "v23-adapter-index-v1.json",
        "v23-adapter-index-v1.schema.json",
    }
)

PURE_OMISSIONS = frozenset(
    {
        "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.8.html",
        "01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.62.0.html",
        "LIVE_OVERLAY_CHECKSUMS_v0.62.8.sha256",
        "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.8.json",
        "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.8.json",
        "o001-a00-assessments-v0.1.0.zip",
        "program-matematika-indonesia-live-overlay-source-v0.62.8.zip",
        "program-matematika-indonesia-source-v0.62.0.zip",
        "program-matematika-indonesia-v0.62.0.html",
        "RELEASE_CHECKSUMS_v0.62.11.sha256",
        "RELEASE_CHECKSUMS_v0.62.12.sha256",
        "RELEASE_NOTES_v0.62.11.md",
        "RELEASE_NOTES_v0.62.12.md",
    }
)

A00_EXTENSION_ROOT = PROJECT / "backend/v2.3/extensions/a00-o001-assessments-v0.1.0"
A00_ADAPTER_ZIP = (
    PROJECT
    / "backend/v2.3/builds/a00_o001_v23_adapter_release/"
    "program-matematika-indonesia-backend-v2.3.1-a00-o001-assessment-adapter-v0.1.0.zip"
)
A00_GITHUB_RECEIPT = PROJECT / "GITHUB_A00_O001_V231_SOURCE_PUBLICATION_RECEIPT.json"
SOURCE_ZIP_NAME = "program-matematika-indonesia-source-v0.62.13.zip"
A00_NAVIGATOR_ZIP_NAME = "program-matematika-indonesia-a00-latihan-v0.1.0.zip"
A00_COMBINED_RECEIPT_NAME = "A00_O001_V231_ADAPTER_AND_LEARNER_NAVIGATOR_20260831.json"
D40_READBACK_MEMBER = (
    "backend/course-capsule-v1/validation/"
    "D40_O010_INDEPENDENT_ANONYMOUS_READBACK.json"
)
D40_VALIDATION_RECEIPT_MEMBER = (
    "backend/course-capsule-v1/validation/VALIDATION_RECEIPT.json"
)
D40_READBACK_PATH = PROJECT / D40_READBACK_MEMBER
D40_READBACK_IDENTITY = {
    "path": D40_READBACK_MEMBER,
    "bytes": 7_570,
    "sha256": "a34f5532208ad45c27d5c4b4108e51f5d3b76e8ded0ef5d334f31465f61e33f9",
}
D40_READBACK_CHECKS = {
    "access_right_open": True,
    "all_byte_counts_match": True,
    "all_files_publicly_downloadable": True,
    "all_md5_match": True,
    "concept_alias_resolves_latest": True,
    "concept_doi": True,
    "concept_record_id": True,
    "credential_recorded": False,
    "credential_used": False,
    "doi": True,
    "exact_inventory": True,
    "inventory_count": True,
    "is_published_not_contradictory": True,
    "latest_version_endpoint": True,
    "local_vs_stream_sha256_match": True,
    "primary_pdf_public_with_pdf_signature": True,
    "published_status": True,
    "record_id": True,
    "submitted_flag": True,
    "version_relation_parent": True,
}
D40_READBACK_FILES = {
    "COMPONENT_LICENSE_BOUNDARIES.json": (
        2_131,
        "e95f98d79d5105e24d5c5808548b890dc8b14abd102bac2872a8d1519e85af4a",
    ),
    "D40_COMPLETE_ID_20260831.zip": (
        9_436_983,
        "a370bba5ddb54081387a484a304b24af92691c3bc167db964c486625a79add59",
    ),
    "PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_LENGKAP.pdf": (
        4_393_637,
        "c4e4f470eeb096129e7bf7306422d316c93aaeed99d2b12890e08f15777ac13f",
    ),
    "RELEASE_MANIFEST.json": (
        92_798,
        "3991fd2234e263134090c3686b93553dcab1215d86144509fd7937d5a4065a97",
    ),
    "RELEASE_NOTES.md": (
        1_233,
        "b3e6678c75aced1badfe1469d9b6618cfe12899ecace14473f3acd3d2ef85da3",
    ),
    "RELEASE_RECEIPT.json": (
        32_377,
        "33287e8eefff35b7cc7362d77350e19f0ae99ed94cce5f1540c854a6f9c5df81",
    ),
    "SHA256SUMS.txt": (
        30_839,
        "14043e5c57e0e402ff2233fac9b40853fba65d30fb0962e6c964c7b38c4861c2",
    ),
}

# The replacement side is exact: these nine names already exist in v0.62.12
# and receive new, validated bytes in v0.62.13.
REPLACEMENT_SOURCE_ALLOWLIST = {
    "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md": (
        PROJECT / "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md"
    ),
    "course-capsule-v1.schema.json": (
        PROJECT / "docs/schema/course-capsule-v1/course-capsule-v1.schema.json"
    ),
    "course-capsules-v1.jsonl": (
        PROJECT / "backend/course-capsule-v1/generated/course-capsules.jsonl"
    ),
    "learner-delivery-v1.json": PROJECT / "backend/authority/learner-delivery-v1.json",
    "modular-backend-pattern-index-v1.json": (
        PROJECT / "backend/authority/modular-backend-pattern-index-v1.json"
    ),
    "peta-belajar-luring.html": PROJECT / "docs/peta-belajar-luring.html",
    "program-matematika-indonesia-course-capsule-v1.zip": (
        PROJECT / "backend/course-capsule-v1/builds/program-matematika-indonesia-course-capsule-v1.zip"
    ),
    "v23-adapter-index-v1.json": PROJECT / "backend/authority/v23-adapter-index-v1.json",
    "v23-adapter-index-v1.schema.json": PROJECT / "schemas/v1/v23-adapter-index-v1.schema.json",
}

NOTES_NAME = "RELEASE_NOTES_v0.62.13.md"
CHECKSUM_NAME = "RELEASE_CHECKSUMS_v0.62.13.sha256"

# These eight pure additions are already prepared locally. The source archive,
# A00 navigator ZIP, combined A00/central receipt, release notes, and checksum
# manifest are generated deterministically by this script.
PURE_ADDITION_SOURCE_ALLOWLIST = {
    "program-matematika-indonesia-backend-v2.3.1-a00-o001-assessment-adapter-v0.1.0.zip": A00_ADAPTER_ZIP,
    "learner-tools-v1.json": PROJECT / "backend/authority/learner-tools-v1.json",
    "learner-tools-v1.schema.json": PROJECT / "schemas/v1/learner-tools-v1.schema.json",
    "a00-assessment-map-v1.schema.json": PROJECT / "schemas/v1/a00-assessment-map-v1.schema.json",
    "assessment-capability-manifest-v0.1.schema.json": PROJECT / "backend/v2.3/schema/assessment-capability-manifest-v0.1.schema.json",
    "assessment-route-binding-v0.1.schema.json": PROJECT / "backend/v2.3/schema/assessment-route-binding-v0.1.schema.json",
    "A00_O001_V231_ADAPTER_VALIDATION_REPORT_v0.1.0.json": PROJECT / "backend/v2.3/builds/a00-o001-assessments-v0.1.0/VALIDATION_REPORT.json",
    "GITHUB_A00_O001_V231_SOURCE_PUBLICATION_RECEIPT.json": A00_GITHUB_RECEIPT,
}

PURE_ADDITION_NAMES = frozenset(
    set(PURE_ADDITION_SOURCE_ALLOWLIST)
    | {
        SOURCE_ZIP_NAME,
        A00_NAVIGATOR_ZIP_NAME,
        A00_COMBINED_RECEIPT_NAME,
        NOTES_NAME,
        CHECKSUM_NAME,
    }
)

FIXED_EXPECTED_ADDITIONS = {
    "program-matematika-indonesia-backend-v2.3.1-a00-o001-assessment-adapter-v0.1.0.zip": (
        8_634_922,
        "43e122a96cf2878764ff53148c9d2d247ccb0b661b563ae6c5f04f4cd000098b",
    ),
    "A00_O001_V231_ADAPTER_VALIDATION_REPORT_v0.1.0.json": (
        3_324,
        "910c1d447dfbd6f7e7eab833bed84ec188bb39e2f687c4df891987753b254950",
    ),
    "GITHUB_A00_O001_V231_SOURCE_PUBLICATION_RECEIPT.json": (
        3_143,
        "bf0e30c1c0a87e8ea6dffa0fc1d01aa0e0043ee3dd1243eb86797010fee67010",
    ),
}

A00_NAVIGATOR_EXPECTED_SOURCES = {
    "index.html": (49_073, "7829edafb65f433ebce03ce0648412c60c5385c51cbc6e016846bdcc42191489"),
    "latihan.css": (7_124, "7238e15c9751b3bf1229c3f9fcd1a303f405d89f8ab27f72d2c8b76155aae77b"),
    "latihan.js": (6_246, "417489651db0b99c520e339060bc34e5a5378243aebb905f2f6b8aa2c0462b96"),
    "assessment-map-v1.json": (
        8_143_540,
        "2a350672680c57ad4a8d7daeb46827f12487b9cf0793597f55970ca4d9471858",
    ),
    "anchor-audit-v1.json": (
        27_516,
        "d50bd0203359a13f2eac176e021920635ed07258ee9622ab0d89e09c6ac12926",
    ),
}

# Every source/public projection identity below must be present inside the
# capsule package. Each public file must also exist in docs/ and match its
# corresponding generated source, authority, schema, or receipt byte-for-byte.
CAPSULE_REQUIRED_MIRROR_PAIRS = {
    "backend/course-capsule-v1/authority/backend-design-policy-v1.json": (
        "docs/data/course-capsule-v1/backend-design-policy-v1.json"
    ),
    "backend/course-capsule-v1/authority/public-baseline-v0.62.12.json": (
        "docs/data/course-capsule-v1/public-baseline-v0.62.12.json"
    ),
    "schemas/course-capsule-v1/backend-design-policy-v1.schema.json": (
        "docs/schema/course-capsule-v1/backend-design-policy-v1.schema.json"
    ),
    "schemas/course-capsule-v1/public-baseline-v1.schema.json": (
        "docs/schema/course-capsule-v1/public-baseline-v1.schema.json"
    ),
    "backend/authority/learner-tools-v1.json": "docs/data/learner-tools-v1.json",
    "schemas/v1/learner-tools-v1.schema.json": "docs/schema/v1/learner-tools-v1.schema.json",
    "schemas/course-capsule-v1/course-capsule-v1.schema.json": (
        "docs/schema/course-capsule-v1/course-capsule-v1.schema.json"
    ),
    "backend/course-capsule-v1/generated/course-capsules.jsonl": (
        "docs/data/course-capsule-v1/course-capsules.jsonl"
    ),
    "backend/course-capsule-v1/generated/course-capsules.json": (
        "docs/data/course-capsule-v1/course-capsules.json"
    ),
    "backend/course-capsule-v1/generated/manifest.json": (
        "docs/data/course-capsule-v1/manifest.json"
    ),
    "backend/course-capsule-v1/validation/VALIDATION_RECEIPT.json": (
        "docs/data/course-capsule-v1/validation-receipt.json"
    ),
}

CAPSULE_CORE_MEMBERS = frozenset(
    {
        "backend/authority/learner-delivery-v1.json",
        "backend/course-capsule-v1/README.md",
        "backend/course-capsule-v1/authority/integration-overrides-v1.json",
        "backend/course-capsule-v1/generated/course-capsules.json",
        "backend/course-capsule-v1/generated/course-capsules.jsonl",
        "backend/course-capsule-v1/generated/manifest.json",
        D40_READBACK_MEMBER,
        "backend/course-capsule-v1/validation/SITE_VALIDATION_RECEIPT.json",
        D40_VALIDATION_RECEIPT_MEMBER,
        "docs/backend/backend.css",
        "docs/backend/backend.js",
        "docs/backend/index.html",
        "docs/backend/index.template.html",
        "docs/courses.js",
        "docs/data/course-capsule-v1/README.md",
        "docs/data/course-capsule-v1/course-capsules.json",
        "docs/data/course-capsule-v1/course-capsules.jsonl",
        "docs/data/course-capsule-v1/manifest.json",
        "docs/data/course-capsule-v1/validation-receipt.json",
        "docs/live-course-publications.js",
        "docs/schema/course-capsule-v1/course-capsule-v1.schema.json",
        "schemas/course-capsule-v1/course-capsule-v1.schema.json",
        "scripts/build-and-validate-course-capsules-v1.mjs",
        "scripts/build-course-capsules-v1.mjs",
        "scripts/sync-course-capsules-v1.mjs",
        "scripts/validate-course-capsule-site-v1.mjs",
        "scripts/validate-course-capsules-v1.mjs",
    }
)

SEVEN_LAYERS = frozenset(
    {"curriculum", "translation", "production", "learner", "educator", "federation", "interoperability"}
)
TEXT_SUFFIXES = frozenset(
    {
        ".css",
        ".csv",
        ".html",
        ".js",
        ".json",
        ".jsonl",
        ".md",
        ".mjs",
        ".py",
        ".sha256",
        ".tex",
        ".toml",
        ".txt",
        ".xml",
        ".yaml",
        ".yml",
    }
)


class BuildError(RuntimeError):
    """A deterministic release-boundary or validation failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BuildError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_flat_name(name: str) -> None:
    pure = PurePosixPath(name)
    require(
        bool(name)
        and pure.name == name
        and not pure.is_absolute()
        and name not in {".", ".."}
        and "/" not in name
        and "\\" not in name
        and ":" not in name,
        f"unsafe non-flat release filename: {name!r}",
    )


def relative_display(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT.resolve()).as_posix()
    except ValueError:
        return path.name


def fact(name: str, data: bytes, provenance: str, source: Path | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {
        "name": name,
        "bytes": len(data),
        "sha256": sha256(data),
        "provenance": provenance,
    }
    if source is not None:
        row["source"] = relative_display(source)
    return row


def inventory_aggregate(rows: Iterable[dict[str, Any]]) -> str:
    material = "".join(
        f"{row['sha256']}  {row['name']}\n"
        for row in sorted(rows, key=lambda item: str(item["name"]))
    ).encode("utf-8")
    return sha256(material)


def privacy_scan(name: str, data: bytes) -> None:
    lowered = data.lower()
    patterns = (
        (rb"[a-z]:\\users\\[^\\\r\n]+", "absolute Windows profile path"),
        (rb"/users/[^/\r\n]+", "absolute POSIX profile path"),
        (rb"authorization\s*:\s*bearer", "bearer authorization header"),
        (rb"access[_-]?token\s*[=:]\s*[\"']?[a-z0-9._-]{16,}", "access-token material"),
        (rb"client[_-]?secret\s*[=:]\s*[\"']?[a-z0-9._-]{16,}", "client-secret material"),
        (rb"api[_-]?key\s*[=:]\s*[\"']?[a-z0-9._-]{16,}", "API-key material"),
        (rb"github_pat_[a-z0-9_]{20,}|gh[opusr]_[a-z0-9]{20,}", "GitHub credential"),
        (rb"-----begin (?:rsa |ec |openssh )?private key-----", "private key"),
    )
    for pattern, label in patterns:
        require(re.search(pattern, lowered) is None, f"{label} in {name}")
    profile = Path.home().name.encode("utf-8", errors="ignore").lower()
    if profile:
        require(profile not in lowered, f"local profile identifier in {name}")


def validate_json(name: str, data: bytes) -> Any:
    try:
        value = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"invalid JSON in {name}: {exc}") from exc
    require(isinstance(value, (dict, list)), f"unexpected JSON root in {name}")
    return value


def validate_draft_2020_12(instance: Any, schema: dict[str, Any], label: str) -> None:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
        from jsonschema.exceptions import SchemaError
    except ImportError as exc:
        raise BuildError("python package 'jsonschema' is required for Draft 2020-12 validation") from exc
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise BuildError(f"invalid Draft 2020-12 schema for {label}: {exc.message}") from exc
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.absolute_path) or "<root>"
        raise BuildError(f"Draft 2020-12 validation failed for {label} at {location}: {first.message}")


def validate_jsonl(name: str, data: bytes) -> list[dict[str, Any]]:
    try:
        lines = [line for line in data.decode("utf-8-sig").splitlines() if line.strip()]
    except UnicodeDecodeError as exc:
        raise BuildError(f"invalid UTF-8 JSONL in {name}: {exc}") from exc
    require(lines, f"empty JSONL: {name}")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(lines, start=1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BuildError(f"invalid JSONL in {name} line {number}: {exc}") from exc
        require(isinstance(value, dict), f"non-object JSONL row in {name} line {number}")
        rows.append(value)
    return rows


def validate_d40_readback_receipt(data: bytes) -> dict[str, Any]:
    observed_identity = {
        "path": D40_READBACK_MEMBER,
        "bytes": len(data),
        "sha256": sha256(data),
    }
    require(
        observed_identity == D40_READBACK_IDENTITY,
        "D40 independent anonymous-readback receipt identity drift",
    )
    privacy_scan(D40_READBACK_MEMBER, data)
    value = validate_json(D40_READBACK_MEMBER, data)
    require(isinstance(value, dict), "D40 independent readback receipt is not an object")
    expected_top_level = {
        "schema": "o010-d40-complete-independent-anonymous-readback-v1",
        "authentication": "none",
        "credential_material_recorded": False,
        "verdict": "PASS_INDEPENDENT_ANONYMOUS_PUBLIC_READBACK",
        "record_id": 22_184_259,
        "doi": "10.5281/zenodo.22184259",
        "conceptdoi": "10.5281/zenodo.22059503",
        "public_api_url": "https://zenodo.org/api/records/22184259",
        "public_record_url": "https://zenodo.org/records/22184259",
        "file_count": 7,
    }
    require(
        all(value.get(key) == expected for key, expected in expected_top_level.items()),
        "D40 independent readback top-level field binding drift",
    )
    require(value.get("checks") == D40_READBACK_CHECKS, "D40 independent readback checks drift")
    files = value.get("files")
    require(isinstance(files, list) and len(files) == 7, "D40 independent readback file boundary is not 7")
    by_name: dict[str, dict[str, Any]] = {}
    for entry in files:
        require(isinstance(entry, dict), "invalid D40 independent readback file row")
        name = entry.get("filename")
        require(isinstance(name, str) and name in D40_READBACK_FILES, "unexpected D40 readback filename")
        require(name not in by_name, f"duplicate D40 independent readback filename: {name}")
        by_name[name] = entry
    require(set(by_name) == set(D40_READBACK_FILES), "D40 independent readback inventory drift")
    for name, (expected_bytes, expected_sha256) in D40_READBACK_FILES.items():
        entry = by_name[name]
        anonymous = entry.get("anonymous_download")
        local = entry.get("local")
        public_api = entry.get("public_api_inventory")
        require(
            isinstance(anonymous, dict) and isinstance(local, dict) and isinstance(public_api, dict),
            f"D40 readback identity layers missing: {name}",
        )
        expected_url = (
            f"{expected_top_level['public_api_url']}/files/{quote(name, safe='')}/content"
        )
        require(
            entry.get("verdict") == "PASS_EXACT_PUBLIC_BYTES"
            and entry.get("canonical_anonymous_download_url") == expected_url
            and anonymous.get("bytes") == expected_bytes
            and anonymous.get("sha256") == expected_sha256
            and local.get("bytes") == expected_bytes
            and local.get("sha256") == expected_sha256
            and public_api.get("bytes") == expected_bytes,
            f"D40 exact public-byte identity drift: {name}",
        )
        anonymous_md5 = anonymous.get("md5")
        require(
            isinstance(anonymous_md5, str)
            and re.fullmatch(r"[0-9a-f]{32}", anonymous_md5) is not None
            and local.get("md5") == anonymous_md5
            and public_api.get("md5") == anonymous_md5,
            f"D40 public/local/API MD5 binding drift: {name}",
        )
    require(
        sum(int(entry["anonymous_download"]["bytes"]) for entry in by_name.values())
        == 13_989_998,
        "D40 independent readback aggregate byte count drift",
    )
    return value


def validate_d40_capsule_readback_binding(
    d40: dict[str, Any],
    readback: dict[str, Any],
) -> None:
    readback_files = readback.get("files")
    require(isinstance(readback_files, list), "D40 readback files missing during capsule binding")
    by_name = {
        str(entry["filename"]): entry
        for entry in readback_files
        if isinstance(entry, dict) and isinstance(entry.get("filename"), str)
    }
    require(set(by_name) == set(D40_READBACK_FILES), "D40 capsule/readback inventory drift")
    pdf = by_name["PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_LENGKAP.pdf"]
    portable = by_name["D40_COMPLETE_ID_20260831.zip"]
    release_manifest = by_name["RELEASE_MANIFEST.json"]
    record_url = str(readback["public_record_url"])
    doi_url = f"https://doi.org/{readback['doi']}"

    def record_file_url(entry: dict[str, Any]) -> str:
        return f"{record_url}/files/{quote(str(entry['filename']), safe='')}?download=1"

    pdf_url = record_file_url(pdf)
    portable_url = record_file_url(portable)
    manifest_url = record_file_url(release_manifest)
    course = d40.get("course")
    native = d40.get("course_native")
    layers = d40.get("layers")
    require(
        isinstance(course, dict) and isinstance(native, dict) and isinstance(layers, dict),
        "D40 capsule identity layers missing",
    )
    production = layers.get("production")
    learner = layers.get("learner")
    federation = layers.get("federation")
    interoperability = layers.get("interoperability")
    educator = layers.get("educator")
    require(
        all(isinstance(value, dict) for value in (production, learner, federation, interoperability, educator)),
        "D40 capsule delivery layers missing",
    )
    require(
        course.get("state") == "published"
        and native.get("status") == "verified"
        and native.get("version") == "2026.08.31-d40-complete"
        and "repository" not in native
        and native.get("zenodo") == doi_url
        and native.get("edition") == pdf_url
        and production.get("release_status") == "verified"
        and "repository" not in production
        and production.get("zenodo") == doi_url
        and production.get("edition") == pdf_url,
        "D40 native/production binding drift from independent readback",
    )
    evidence = d40.get("evidence")
    primary = learner.get("primary")
    learner_pdf = learner.get("pdf")
    learner_portable = learner.get("portable_html")
    require(
        isinstance(evidence, list)
        and len(evidence) == 1
        and isinstance(evidence[0], dict)
        and all(isinstance(value, dict) for value in (primary, learner_pdf, learner_portable)),
        "D40 learner evidence boundary drift",
    )
    pdf_identity = pdf["anonymous_download"]
    portable_identity = portable["anonymous_download"]
    require(
        evidence[0].get("file_name") == pdf["filename"]
        and evidence[0].get("bytes") == pdf_identity["bytes"]
        and evidence[0].get("sha256") == pdf_identity["sha256"]
        and primary.get("status") == "verified"
        and primary.get("format") == "application/pdf"
        and primary.get("bytes") == pdf_identity["bytes"]
        and primary.get("sha256") == pdf_identity["sha256"]
        and primary.get("url") == pdf_url
        and learner_pdf.get("status") == "verified"
        and learner_pdf.get("bytes") == pdf_identity["bytes"]
        and learner_pdf.get("sha256") == pdf_identity["sha256"]
        and learner_pdf.get("url") == pdf_url
        and learner_portable.get("status") == "verified"
        and learner_portable.get("bytes") == portable_identity["bytes"]
        and learner_portable.get("sha256") == portable_identity["sha256"]
        and learner_portable.get("url") == portable_url
        and learner_portable.get("entry_point") == "reader/html/index.html"
        and learner_portable.get("inventory_count") == 273
        and learner_portable.get("dependency_free") is True,
        "D40 learner artifacts drift from independent readback",
    )
    components = federation.get("components")
    require(isinstance(components, list), "D40 federation components missing")
    components_by_id = {
        str(component["id"]): component
        for component in components
        if isinstance(component, dict) and isinstance(component.get("id"), str)
    }
    require(len(components_by_id) == len(components), "duplicate or invalid D40 federation component")
    primary_component = components_by_id.get("D40:primary")
    package_component = components_by_id.get("D40:d40-complete-package")
    require(
        isinstance(primary_component, dict)
        and primary_component.get("url") == pdf_url
        and isinstance(package_component, dict)
        and package_component.get("url") == portable_url
        and package_component.get("sha256") == portable_identity["sha256"],
        "D40 federation artifacts drift from independent readback",
    )
    semantic_adapter = interoperability.get("semantic_adapter")
    require(isinstance(semantic_adapter, dict), "D40 semantic adapter missing")
    semantic_evidence = semantic_adapter.get("evidence")
    manifest_identity = release_manifest["anonymous_download"]
    require(
        semantic_adapter.get("status") == "available_unverified"
        and semantic_adapter.get("mapping_scope")
        == "course_native_composite_backend_not_yet_consumed_by_global_runtime"
        and isinstance(semantic_evidence, list)
        and len(semantic_evidence) == 1
        and isinstance(semantic_evidence[0], dict)
        and semantic_evidence[0].get("file_name") == release_manifest["filename"]
        and semantic_evidence[0].get("bytes") == manifest_identity["bytes"]
        and semantic_evidence[0].get("sha256") == manifest_identity["sha256"]
        and semantic_evidence[0].get("locator") == manifest_url,
        "D40 semantic manifest drift from independent readback",
    )
    educator_evidence = educator.get("evidence")
    locator_evidence = [
        evidence[0],
        primary.get("evidence"),
        learner_pdf.get("evidence"),
        learner_portable.get("evidence"),
    ]
    require(
        isinstance(educator_evidence, list)
        and len(educator_evidence) >= 1
        and isinstance(educator_evidence[0], dict),
        "D40 educator evidence missing",
    )
    locator_evidence.append(educator_evidence[0])
    require(
        all(isinstance(item, dict) and item.get("locator") == record_url for item in locator_evidence),
        "D40 evidence locator drift from independent readback",
    )


def validate_packaged_d40_binding(files: dict[str, zipfile.ZipInfo], archive: zipfile.ZipFile) -> dict[str, Any]:
    readback_member = files.get(D40_READBACK_MEMBER)
    validation_member = files.get(D40_VALIDATION_RECEIPT_MEMBER)
    require(readback_member is not None, "D40 independent readback receipt is absent from capsule ZIP")
    require(validation_member is not None, "validation receipt is absent from capsule ZIP")
    readback_data = archive.read(readback_member)
    validate_d40_readback_receipt(readback_data)
    validation_data = archive.read(validation_member)
    validation = validate_json(D40_VALIDATION_RECEIPT_MEMBER, validation_data)
    require(isinstance(validation, dict), "packaged capsule validation receipt is not an object")
    checks = validation.get("checks")
    artifacts = validation.get("artifacts")
    require(validation.get("state") == "pass", "packaged capsule validation receipt state is not pass")
    require(isinstance(checks, dict), "packaged capsule validation receipt checks missing")
    require(
        checks.get("d40_independent_anonymous_readback") == "pass_7_of_7",
        "packaged capsule D40 readback check is not pass_7_of_7",
    )
    require(isinstance(artifacts, dict), "packaged capsule validation receipt artifacts missing")
    require(
        artifacts.get("d40_independent_anonymous_readback") == D40_READBACK_IDENTITY,
        "packaged capsule validation receipt does not bind exact D40 readback identity",
    )
    return {
        "receipt_artifact": dict(D40_READBACK_IDENTITY),
        "validation_receipt": {
            "member": D40_VALIDATION_RECEIPT_MEMBER,
            "state": "pass",
            "check": "pass_7_of_7",
            "artifact": dict(D40_READBACK_IDENTITY),
        },
    }


def validate_course_capsules(rows: list[dict[str, Any]]) -> None:
    require(len(rows) == 40, "course-capsules-v1.jsonl does not contain exactly 40 rows")
    by_id: dict[str, dict[str, Any]] = {}
    states: list[str] = []
    for row in rows:
        course_id = row.get("course_id")
        require(
            isinstance(course_id, str) and re.fullmatch(r"[ABCD](?:00|[1-9][0-9]{1,2})", course_id) is not None,
            "invalid course capsule identity",
        )
        require(course_id not in by_id, f"duplicate course capsule identity: {course_id}")
        layers = row.get("layers")
        require(isinstance(layers, dict) and SEVEN_LAYERS <= set(layers), f"seven-layer closure missing: {course_id}")
        federation = layers.get("federation")
        require(
            isinstance(federation, dict) and federation.get("zero_copy") is True,
            f"zero-copy federation not asserted: {course_id}",
        )
        policy = row.get("open_access_policy")
        require(
            isinstance(policy, dict)
            and policy.get("public_access_required") is True
            and policy.get("private_access_forbidden") is True
            and policy.get("download_restriction_forbidden") is True,
            f"open-access policy drift: {course_id}",
        )
        course = row.get("course")
        require(isinstance(course, dict) and course.get("state") in {"published", "production"}, f"invalid state: {course_id}")
        states.append(str(course["state"]))
        by_id[course_id] = row
    require(states.count("published") == 35, "published capsule count is not 35")
    require(states.count("production") == 5, "production capsule count is not 5")
    production_ids = sorted(
        course_id for course_id, row in by_id.items() if row.get("course", {}).get("state") == "production"
    )
    require(
        production_ids == ["A20", "A30", "B95", "C140", "D100"],
        f"production capsule roster drift: {production_ids!r}",
    )
    published_record_ids: set[str] = set()
    for course_id, row in by_id.items():
        if row.get("course", {}).get("state") != "published":
            continue
        course_native = row.get("course_native")
        doi_url = course_native.get("zenodo") if isinstance(course_native, dict) else None
        match = CANONICAL_ZENODO_DOI_URL.fullmatch(doi_url) if isinstance(doi_url, str) else None
        require(match is not None, f"published capsule lacks a canonical Zenodo DOI URL: {course_id}")
        published_record_ids.add(match.group(1))
    require(
        len(published_record_ids) == 31,
        f"distinct published DOI-record count is not 31: {len(published_record_ids)}",
    )
    d30 = by_id.get("D30")
    require(isinstance(d30, dict), "D30 capsule missing")
    native = d30.get("course_native")
    production = d30.get("layers", {}).get("production")
    require(isinstance(native, dict) and isinstance(production, dict), "D30 evidence layers missing")
    d30_material = json.dumps(d30, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    require(d30.get("course", {}).get("state") == "published", "D30 is not published")
    require("22182655" in d30_material, "D30 final Zenodo record is not bound")
    require("CHECKPOINT_38" in d30_material, "D30 checkpoint-38 reader is not bound")
    require("447" in d30_material, "D30 447-page evidence is not bound")
    require(
        production.get("release_status") in {"published", "verified"},
        "D30 production release status is neither published nor verified",
    )
    d40 = by_id.get("D40")
    require(isinstance(d40, dict), "D40 capsule missing")
    production = d40.get("layers", {}).get("production")
    require(isinstance(production, dict), "D40 production layer missing")
    d40_material = json.dumps(d40, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    require(d40.get("course", {}).get("state") == "published", "D40 is not published")
    require("22184259" in d40_material, "D40 final Zenodo record is not bound")
    require("2026.08.31-d40-complete" in d40_material, "D40 complete-version evidence is not bound")
    require("679" in d40_material, "D40 679-page evidence is not bound")
    require(
        "a370bba5ddb54081387a484a304b24af92691c3bc167db964c486625a79add59" in d40_material,
        "D40 complete portable-reader archive is not bound",
    )
    require(
        production.get("release_status") in {"published", "verified"},
        "D40 production release status is neither published nor verified",
    )


def safe_zip_member(name: str) -> str:
    normalized = unicodedata.normalize("NFC", name)
    require(normalized == name, f"non-NFC ZIP member: {name!r}")
    pure = PurePosixPath(name)
    require(
        bool(name)
        and not pure.is_absolute()
        and "\\" not in name
        and ":" not in pure.parts[0]
        and all(part not in {"", ".", ".."} for part in pure.parts),
        f"unsafe ZIP member path: {name!r}",
    )
    return pure.as_posix()


def validate_zip(
    name: str,
    path: Path,
    *,
    local_root: Path | None = None,
    exact_file_count: int | None = None,
    required_members: Iterable[str] = (),
) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(path, "r") as archive:
            members = archive.infolist()
            require(members, f"empty ZIP: {name}")
            file_members = [member for member in members if not member.is_dir()]
            if exact_file_count is not None:
                require(len(file_members) == exact_file_count, f"ZIP file-count drift in {name}")
            names: list[str] = []
            folded: set[str] = set()
            for member in members:
                member_name = safe_zip_member(member.filename.rstrip("/") if member.is_dir() else member.filename)
                key = member_name.casefold()
                require(key not in folded, f"case-folded duplicate ZIP member in {name}: {member.filename}")
                folded.add(key)
                names.append(member.filename)
                require((member.flag_bits & 0x1) == 0, f"encrypted ZIP member in {name}: {member.filename}")
                unix_mode = (member.external_attr >> 16) & 0xFFFF
                require(not stat.S_ISLNK(unix_mode), f"symlink ZIP member in {name}: {member.filename}")
                require(member.date_time == (1980, 1, 1, 0, 0, 0), f"non-deterministic ZIP timestamp in {name}: {member.filename}")
                require(
                    member.compress_type in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED},
                    f"unsupported ZIP compression in {name}: {member.filename}",
                )
            require(len(names) == len(set(names)), f"duplicate ZIP member in {name}")
            failed = archive.testzip()
            require(failed is None, f"ZIP CRC failure in {name}: {failed}")
            file_names = {member.filename for member in file_members}
            required = set(required_members)
            require(required <= file_names, f"required ZIP members missing in {name}: {sorted(required - file_names)}")
            if local_root is not None:
                require(local_root.is_dir(), f"ZIP closure root missing for {name}")
                local_paths = {
                    item.relative_to(local_root).as_posix(): item
                    for item in local_root.rglob("*")
                    if item.is_file()
                }
                require(file_names == set(local_paths), f"ZIP/local path closure differs in {name}")
                for member in file_members:
                    archived = archive.read(member)
                    local = local_paths[member.filename].read_bytes()
                    require(archived == local, f"ZIP/local byte mismatch in {name}: {member.filename}")
                    if PurePosixPath(member.filename).suffix.lower() in TEXT_SUFFIXES:
                        privacy_scan(f"{name}!{member.filename}", archived)
            else:
                for member in file_members:
                    if PurePosixPath(member.filename).suffix.lower() in TEXT_SUFFIXES:
                        privacy_scan(f"{name}!{member.filename}", archive.read(member))
            return {
                "zip_files": len(file_members),
                "zip_uncompressed_bytes": sum(member.file_size for member in file_members),
            }
    except zipfile.BadZipFile as exc:
        raise BuildError(f"invalid ZIP: {name}") from exc


def run_git_bytes(arguments: list[str], label: str) -> bytes:
    """Run one bounded, read-only Git query against this small repository."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(PROJECT), *arguments],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BuildError(f"bounded Git operation failed: {label}") from exc
    require(completed.returncode == 0, f"bounded Git operation failed: {label}")
    return completed.stdout


def validate_source_authority(source_commit: str, source_tree: str) -> None:
    require(
        re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None,
        "--source-commit must be a full lowercase 40-character SHA",
    )
    require(
        re.fullmatch(r"[0-9a-f]{40}", source_tree) is not None,
        "--source-tree must be a full lowercase 40-character SHA",
    )
    resolved_commit = run_git_bytes(
        ["rev-parse", "--verify", f"{source_commit}^{{commit}}"],
        "resolve explicit source commit",
    ).decode("ascii", errors="strict").strip()
    resolved_tree = run_git_bytes(
        ["rev-parse", "--verify", f"{source_commit}^{{tree}}"],
        "resolve explicit source tree",
    ).decode("ascii", errors="strict").strip()
    require(resolved_commit == source_commit, "explicit source commit does not resolve to itself")
    require(resolved_tree == source_tree, "explicit source commit does not resolve to supplied tree")


def require_committed_bytes(source_commit: str, path: Path, data: bytes, label: str) -> None:
    resolved = path.resolve()
    require(resolved.is_relative_to(PROJECT.resolve()), f"commit-bound source escapes project: {label}")
    relative = resolved.relative_to(PROJECT.resolve()).as_posix()
    committed = run_git_bytes(["show", f"{source_commit}:{relative}"], f"read committed source for {label}")
    require(committed == data, f"working source differs from explicit commit: {label}")


def committed_regular_files(source_commit: str) -> set[str]:
    raw = run_git_bytes(
        ["ls-tree", "-r", "-z", "--full-tree", source_commit],
        "inspect explicit source tree entry modes",
    )
    require(raw.endswith(b"\0"), "explicit source tree listing is not NUL-terminated")
    paths: set[str] = set()
    for entry in raw[:-1].split(b"\0"):
        require(b"\t" in entry, "malformed explicit source tree entry")
        metadata, raw_path = entry.split(b"\t", 1)
        try:
            mode, object_type, object_id = metadata.decode("ascii", errors="strict").split(" ")
            path = raw_path.decode("utf-8", errors="strict")
        except (UnicodeDecodeError, ValueError) as exc:
            raise BuildError("explicit source tree entry is not canonical UTF-8 Git metadata") from exc
        require(mode in {"100644", "100755"}, f"non-regular source tree mode rejected: {path}")
        require(object_type == "blob", f"non-blob source tree object rejected: {path}")
        require(re.fullmatch(r"[0-9a-f]{40,64}", object_id) is not None, f"source tree object ID drift: {path}")
        normalized = safe_zip_member(path)
        require(normalized == path, f"source tree path normalization drift: {path}")
        require(path not in paths, f"duplicate source tree path: {path}")
        paths.add(path)
    require(paths, "explicit source tree has no regular files")
    return paths


def build_source_archive(source_commit: str, source_tree: str) -> tuple[bytes, dict[str, Any]]:
    """Create the exact Git ZIP archive twice and validate its commit comment."""
    validate_source_authority(source_commit, source_tree)
    tree_files = committed_regular_files(source_commit)
    command = ["archive", "--format=zip", source_commit]
    first = run_git_bytes(command, "build deterministic source archive A")
    second = run_git_bytes(command, "build deterministic source archive B")
    require(first == second, "source git archive is not byte-deterministic")
    require(first.startswith(b"PK"), "source git archive lacks ZIP signature")
    try:
        with zipfile.ZipFile(io.BytesIO(first), "r") as archive:
            require(archive.comment == source_commit.encode("ascii"), "source ZIP comment does not bind explicit commit")
            members = archive.infolist()
            files = [member for member in members if not member.is_dir()]
            require(files, "source git archive is empty")
            names: list[str] = []
            folded: set[str] = set()
            for member in members:
                normalized = safe_zip_member(
                    member.filename.rstrip("/") if member.is_dir() else member.filename
                )
                require(normalized == member.filename.rstrip("/"), "source ZIP member normalization drift")
                key = member.filename.casefold()
                require(key not in folded, f"case-folded duplicate source ZIP member: {member.filename}")
                folded.add(key)
                names.append(member.filename)
                require((member.flag_bits & 0x1) == 0, f"encrypted source ZIP member: {member.filename}")
                require(member.create_system in {0, 3}, f"unsupported source ZIP creator metadata: {member.filename}")
                if member.create_system == 3:
                    unix_mode = (member.external_attr >> 16) & 0xFFFF
                    require(not stat.S_ISLNK(unix_mode), f"symlink source ZIP member: {member.filename}")
                require(
                    member.compress_type in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED},
                    f"unsupported source ZIP compression: {member.filename}",
                )
            require(len(names) == len(set(names)), "duplicate source ZIP member")
            require(names == sorted(names), "source ZIP members are not lexically sorted")
            require(
                {member.filename for member in files} == tree_files,
                "source ZIP regular-file inventory differs from explicit Git tree",
            )
            require(len({member.date_time for member in members}) == 1, "source ZIP has more than one timestamp")
            require(archive.testzip() is None, "source ZIP CRC failure")
            for member in files:
                if PurePosixPath(member.filename).suffix.lower() in TEXT_SUFFIXES:
                    privacy_scan(f"{SOURCE_ZIP_NAME}!{member.filename}", archive.read(member))
            details = {
                "source_commit": source_commit,
                "source_tree": source_tree,
                "zip_comment": source_commit,
                "zip_files": len(files),
                "zip_uncompressed_bytes": sum(member.file_size for member in files),
                "deterministic_replay": "pass_byte_identical_a_b",
            }
    except zipfile.BadZipFile as exc:
        raise BuildError("invalid deterministic source ZIP") from exc
    return first, details


def deterministic_zip(entries: dict[str, bytes], comment: bytes) -> bytes:
    """Create a stable, flat-source ZIP under already-qualified entry names."""
    output = io.BytesIO()
    with zipfile.ZipFile(
        output,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for name in sorted(entries):
            safe_zip_member(name)
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.flag_bits |= 0x800
            archive.writestr(info, entries[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        archive.comment = comment
    return output.getvalue()


def build_a00_navigator_archive(source_commit: str) -> tuple[bytes, dict[str, Any]]:
    root = PROJECT / "docs/id-ID/courses/A00/latihan"
    names = frozenset(
        {"index.html", "latihan.css", "latihan.js", "assessment-map-v1.json", "anchor-audit-v1.json"}
    )
    require(root.is_dir(), "A00 learner navigator source directory missing")
    actual = {item.name for item in root.iterdir() if item.is_file()}
    require(actual == names, "A00 learner navigator source boundary drift")
    source_rows: list[dict[str, Any]] = []
    entries: dict[str, bytes] = {}
    prefix = "program-matematika-indonesia-a00-latihan-v0.1.0/"
    for name in sorted(names):
        path = root / name
        data = path.read_bytes()
        require(data, f"empty A00 learner navigator source: {name}")
        require(
            (len(data), sha256(data)) == A00_NAVIGATOR_EXPECTED_SOURCES[name],
            f"sealed A00 learner navigator source identity drift: {name}",
        )
        privacy_scan(f"A00 navigator {name}", data)
        require_committed_bytes(source_commit, path, data, f"A00 navigator {name}")
        source_rows.append(fact(name, data, "committed_a00_learner_source", path))
        entries[prefix + name] = data

    html = (root / "index.html").read_bytes()
    require(b'<html lang="id"' in html.lower(), "A00 learner navigator is not marked id-ID HTML")
    require(b"latihan.css" in html and b"latihan.js" in html, "A00 navigator asset linkage is incomplete")
    map_value = validate_json("assessment-map-v1.json", (root / "assessment-map-v1.json").read_bytes())
    audit_value = validate_json("anchor-audit-v1.json", (root / "anchor-audit-v1.json").read_bytes())
    require(isinstance(map_value, dict) and isinstance(audit_value, dict), "A00 navigator JSON root drift")
    require(
        map_value.get("course_id") == "A00"
        and map_value.get("locale") == "id-ID"
        and map_value.get("counts")
        == {
            "modules": 75,
            "modules_with_assessments": 60,
            "assessments": 8105,
            "components": 13345,
            "explicit_solutions": 5240,
            "without_explicit_solution": 2865,
        },
        "A00 learner assessment-map boundary drift",
    )
    require(
        audit_value.get("status") == "PASS"
        and audit_value.get("counts")
        == {
            "modules": 75,
            "assessment_anchors": 8105,
            "component_anchors": 13345,
            "expected_anchors": 21450,
            "matched_exactly_once": 21450,
            "missing": 0,
            "duplicate": 0,
        },
        "A00 learner anchor-audit boundary drift",
    )
    comment = b"program-matematika-indonesia A00 latihan v0.1.0"
    first = deterministic_zip(entries, comment)
    second = deterministic_zip(entries, comment)
    require(first == second, "A00 learner navigator ZIP is not byte-deterministic")
    try:
        with zipfile.ZipFile(io.BytesIO(first), "r") as archive:
            require(archive.comment == comment, "A00 learner navigator ZIP comment drift")
            files = [member for member in archive.infolist() if not member.is_dir()]
            require([member.filename for member in files] == sorted(entries), "A00 navigator ZIP entry boundary drift")
            require(archive.testzip() is None, "A00 learner navigator ZIP CRC failure")
            for member in files:
                require(archive.read(member) == entries[member.filename], f"A00 navigator ZIP byte drift: {member.filename}")
    except zipfile.BadZipFile as exc:
        raise BuildError("invalid deterministic A00 learner navigator ZIP") from exc
    return first, {
        "entry_prefix": prefix,
        "zip_files": len(entries),
        "zip_uncompressed_bytes": sum(len(data) for data in entries.values()),
        "deterministic_replay": "pass_byte_identical_a_b",
        "source_files": source_rows,
        "assessment_counts": map_value["counts"],
        "anchor_counts": audit_value["counts"],
    }


def validate_capsule_zip(path: Path) -> dict[str, Any]:
    required = set(CAPSULE_CORE_MEMBERS)
    required.update(CAPSULE_REQUIRED_MIRROR_PAIRS)
    required.update(CAPSULE_REQUIRED_MIRROR_PAIRS.values())
    details = validate_zip(
        "program-matematika-indonesia-course-capsule-v1.zip",
        path,
        required_members=required,
    )
    try:
        with zipfile.ZipFile(path, "r") as archive:
            files = {member.filename: member for member in archive.infolist() if not member.is_dir()}
            require(list(files) == sorted(files), "capsule ZIP member order is not deterministic")
            for member_name, member in files.items():
                local_path = (PROJECT / member_name).resolve()
                require(
                    local_path.is_relative_to(PROJECT.resolve()) and local_path.is_file(),
                    f"capsule member has no local source: {member_name}",
                )
                require(
                    archive.read(member) == local_path.read_bytes(),
                    f"capsule ZIP/local byte closure differs: {member_name}",
                )
            for source_name, public_name in CAPSULE_REQUIRED_MIRROR_PAIRS.items():
                source_path = (PROJECT / source_name).resolve()
                public_path = (PROJECT / public_name).resolve()
                require(source_path.is_relative_to(PROJECT.resolve()), f"capsule source escapes project: {source_name}")
                require(public_path.is_relative_to(PROJECT.resolve()), f"public mirror escapes project: {public_name}")
                require(source_path.is_file(), f"capsule source missing: {source_name}")
                require(public_path.is_file(), f"public site mirror missing: {public_name}")
                source_data = source_path.read_bytes()
                public_data = public_path.read_bytes()
                require(source_data == public_data, f"public site mirror byte drift: {public_name}")
                require(archive.read(files[source_name]) == source_data, f"capsule source byte drift: {source_name}")
                require(archive.read(files[public_name]) == public_data, f"capsule public mirror byte drift: {public_name}")
            details["d40_independent_anonymous_readback"] = validate_packaged_d40_binding(
                files,
                archive,
            )
    except zipfile.BadZipFile as exc:
        raise BuildError("invalid capsule ZIP during mirror closure") from exc
    return details


def validate_schema_document(name: str, value: Any) -> None:
    require(isinstance(value, dict), f"schema root is not an object: {name}")
    require(value.get("$schema") == "https://json-schema.org/draft/2020-12/schema", f"schema dialect drift: {name}")
    require(isinstance(value.get("$id"), str) and value["$id"].startswith("https://"), f"schema ID missing: {name}")
    direct_object_shape = isinstance(value.get("properties"), dict)
    composed_shape = any(
        isinstance(value.get(keyword), list) and bool(value[keyword])
        for keyword in ("oneOf", "anyOf", "allOf")
    )
    require(
        direct_object_shape or composed_shape,
        f"schema lacks direct properties or a nonempty composition: {name}",
    )
    if composed_shape:
        require(isinstance(value.get("$defs"), dict) and bool(value["$defs"]), f"composed schema definitions missing: {name}")


def validate_external(name: str, path: Path, data: bytes) -> dict[str, Any]:
    require(data, f"empty additive source: {name}")
    privacy_scan(name, data)
    details: dict[str, Any] = {}
    if name.endswith(".schema.json"):
        value = validate_json(name, data)
        validate_schema_document(name, value)
    elif name.endswith(".json"):
        value = validate_json(name, data)
        require(isinstance(value, dict), f"JSON root is not an object: {name}")
        if name == "learner-delivery-v1.json":
            require(value.get("schema_id") == "interlanguage/program-matematika-indonesia-learner-delivery/v1", "learner-delivery schema identity drift")
            courses = value.get("courses")
            require(isinstance(courses, list) and len(courses) == 40, "learner-delivery course boundary is not 40")
            require(value.get("summary", {}).get("course_count") == 40, "learner-delivery summary drift")
        elif name == "modular-backend-pattern-index-v1.json":
            families = value.get("families")
            require(isinstance(families, list) and len(families) == 33, "backend pattern family boundary is not 33")
        elif name == "v23-adapter-index-v1.json":
            adapters = value.get("adapters")
            require(isinstance(adapters, list) and len(adapters) == 5, "v2.3 adapter proof boundary is not 5")
        elif name == "backend-design-policy-v1.json":
            require(value.get("schema_id") == "interlanguage/backend-design-policy/v1", "design-policy schema identity drift")
            require(value.get("profile") == "thin_format_neutral_zero_copy", "design-policy profile drift")
            authority = value.get("authority")
            require(
                isinstance(authority, dict)
                and authority.get("course_native_authoritative") is True
                and authority.get("capsule_additive") is True
                and authority.get("native_identity_preserved") is True
                and authority.get("full_corpus_copied_into_capsule") is False,
                "design-policy authority boundary drift",
            )
            require(set(value.get("required_layers", [])) == SEVEN_LAYERS, "design-policy seven-layer boundary drift")
        elif name == "public-baseline-v0.62.12.json":
            require(value.get("schema_id") == "interlanguage/course-capsule-public-baseline/v1", "public-baseline schema identity drift")
            repository = value.get("repository")
            release = value.get("release")
            zenodo = value.get("zenodo")
            successor = value.get("successor")
            require(
                isinstance(repository, dict)
                and repository.get("url") == EXPECTED_REPOSITORY
                and repository.get("commit") == EXPECTED_PREDECESSOR_MAIN_COMMIT
                and repository.get("tree") == EXPECTED_PREDECESSOR_MAIN_TREE
                and repository.get("public") is True,
                "public-baseline repository boundary drift",
            )
            require(
                isinstance(release, dict)
                and release.get("url") == EXPECTED_RELEASE_URL
                and release.get("tag") == "v0.62.12"
                and release.get("commit") == EXPECTED_PREDECESSOR_TAG_COMMIT
                and release.get("tree") == EXPECTED_PREDECESSOR_TAG_TREE
                and release.get("draft") is False
                and release.get("prerelease") is False
                and release.get("asset_count") == 100,
                "public-baseline GitHub release boundary drift",
            )
            require(
                isinstance(zenodo, dict)
                and zenodo.get("concept_doi") == EXPECTED_CONCEPT_DOI
                and zenodo.get("record_id") == EXPECTED_PREDECESSOR_RECORD_ID
                and zenodo.get("version_doi") == EXPECTED_VERSION_DOI
                and zenodo.get("version") == PREDECESSOR_VERSION
                and zenodo.get("status") == "published"
                and zenodo.get("access") == "open"
                and zenodo.get("file_count") == 100
                and zenodo.get("payload_bytes") == EXPECTED_PREDECESSOR_TOTAL_BYTES
                and zenodo.get("inventory_aggregate_sha256") == EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
                "public-baseline Zenodo boundary drift",
            )
            require(isinstance(successor, dict) and successor.get("version") == "v0.62.13", "public-baseline successor drift")
    elif name.endswith(".jsonl"):
        rows = validate_jsonl(name, data)
        if name == "course-capsules-v1.jsonl":
            validate_course_capsules(rows)
            details["jsonl_rows"] = len(rows)
    elif name.endswith(".zip"):
        if name == "program-matematika-indonesia-course-capsule-v1.zip":
            details.update(validate_capsule_zip(path))
        elif name.startswith("program-matematika-indonesia-backend-v2.3.1-a00-"):
            details.update(
                validate_zip(
                    name,
                    path,
                    local_root=A00_EXTENSION_ROOT,
                    exact_file_count=68,
                )
            )
        else:
            details.update(validate_zip(name, path))
    elif name.endswith(".html"):
        lowered = data[:8192].lower()
        require(b"<html" in lowered and b'lang="id"' in lowered, f"Bahasa HTML document marker missing: {name}")
        require(data.lower().count(b'data-static-course-id="') == 40, "offline learner page does not contain 40 static course cards")
    elif name.endswith(".md"):
        require(data.startswith(b"#"), f"Markdown heading missing: {name}")
    expected = FIXED_EXPECTED_ADDITIONS.get(name)
    if expected is not None:
        require((len(data), sha256(data)) == expected, f"sealed additive identity drift: {name}")
    details["source"] = relative_display(path)
    return details


def load_json_object(path: Path, label: str) -> tuple[bytes, dict[str, Any]]:
    require(path.is_file(), f"required JSON source missing: {label}")
    data = path.read_bytes()
    privacy_scan(label, data)
    value = validate_json(label, data)
    require(isinstance(value, dict), f"required JSON source is not an object: {label}")
    return data, value


def expected_file_identity(path_text: str) -> dict[str, Any]:
    pure = PurePosixPath(path_text)
    require(
        not pure.is_absolute() and "\\" not in path_text and ".." not in pure.parts,
        f"unsafe evidence path: {path_text}",
    )
    path = (PROJECT / pure.as_posix()).resolve()
    require(path.is_relative_to(PROJECT.resolve()) and path.is_file(), f"evidence path missing: {path_text}")
    data = path.read_bytes()
    return {"path": path_text, "bytes": len(data), "sha256": sha256(data), "data": data}


def validate_cross_artifact_contracts() -> None:
    course_schema_data = REPLACEMENT_SOURCE_ALLOWLIST["course-capsule-v1.schema.json"].read_bytes()
    course_schema = validate_json("course-capsule-v1.schema.json", course_schema_data)
    require(isinstance(course_schema, dict), "course-capsule schema is not an object")
    course_rows = validate_jsonl(
        "course-capsules-v1.jsonl",
        REPLACEMENT_SOURCE_ALLOWLIST["course-capsules-v1.jsonl"].read_bytes(),
    )
    validate_course_capsules(course_rows)

    policy_path = PROJECT / "backend/course-capsule-v1/authority/backend-design-policy-v1.json"
    policy_data, policy = load_json_object(policy_path, "backend-design-policy-v1.json")
    policy_schema_path = PROJECT / "schemas/course-capsule-v1/backend-design-policy-v1.schema.json"
    policy_schema_data, policy_schema = load_json_object(policy_schema_path, "backend-design-policy-v1.schema.json")
    validate_schema_document("backend-design-policy-v1.schema.json", policy_schema)

    baseline_path = PROJECT / "backend/course-capsule-v1/authority/public-baseline-v0.62.12.json"
    baseline_data, baseline = load_json_object(baseline_path, "public-baseline-v0.62.12.json")
    baseline_schema_path = PROJECT / "schemas/course-capsule-v1/public-baseline-v1.schema.json"
    baseline_schema_data, baseline_schema = load_json_object(baseline_schema_path, "public-baseline-v1.schema.json")
    validate_schema_document("public-baseline-v1.schema.json", baseline_schema)

    learner_tools_path = PROJECT / "backend/authority/learner-tools-v1.json"
    learner_tools_data, learner_tools = load_json_object(learner_tools_path, "learner-tools-v1.json")
    learner_tools_schema_path = PROJECT / "schemas/v1/learner-tools-v1.schema.json"
    learner_tools_schema_data, learner_tools_schema = load_json_object(learner_tools_schema_path, "learner-tools-v1.schema.json")
    validate_schema_document("learner-tools-v1.schema.json", learner_tools_schema)

    delivery_data, delivery = load_json_object(
        REPLACEMENT_SOURCE_ALLOWLIST["learner-delivery-v1.json"],
        "learner-delivery-v1.json",
    )
    delivery_schema_data, delivery_schema = load_json_object(
        PREDECESSOR_DIR / "learner-delivery-v1.schema.json",
        "learner-delivery-v1.schema.json",
    )
    validate_schema_document("learner-delivery-v1.schema.json", delivery_schema)

    adapter_data, adapter_index = load_json_object(
        REPLACEMENT_SOURCE_ALLOWLIST["v23-adapter-index-v1.json"],
        "v23-adapter-index-v1.json",
    )
    adapter_schema_data, adapter_schema = load_json_object(
        REPLACEMENT_SOURCE_ALLOWLIST["v23-adapter-index-v1.schema.json"],
        "v23-adapter-index-v1.schema.json",
    )
    validate_schema_document("v23-adapter-index-v1.schema.json", adapter_schema)

    # Forty capsule instances plus five shared authority instances: 45 exact
    # Draft 2020-12 validations.
    for row in course_rows:
        validate_draft_2020_12(row, course_schema, f"course capsule {row.get('course_id', '<unknown>')}")
    validate_draft_2020_12(policy, policy_schema, "backend-design-policy-v1.json")
    validate_draft_2020_12(baseline, baseline_schema, "public-baseline-v0.62.12.json")
    validate_draft_2020_12(learner_tools, learner_tools_schema, "learner-tools-v1.json")
    validate_draft_2020_12(delivery, delivery_schema, "learner-delivery-v1.json")
    validate_draft_2020_12(adapter_index, adapter_schema, "v23-adapter-index-v1.json")

    policy_sha = sha256(policy_data)
    baseline_sha = sha256(baseline_data)
    policy_public_reference = {
        "locator": "https://kokunoyumeto.github.io/program-matematika-indonesia/data/course-capsule-v1/backend-design-policy-v1.json",
        "bytes": len(policy_data),
        "sha256": policy_sha,
    }
    baseline_public_reference = {
        "locator": "https://kokunoyumeto.github.io/program-matematika-indonesia/data/course-capsule-v1/public-baseline-v0.62.12.json",
        "bytes": len(baseline_data),
        "sha256": baseline_sha,
    }
    expected_policy_binding = {
        "profile": "thin_format_neutral_zero_copy",
        "course_native_authoritative": True,
        "capsule_additive": True,
        "native_identity_preserved": True,
        "content_copied_into_capsule": False,
        "canonical_capsule_format": "application/x-ndjson",
        "optional_adapters": ["myst", "quarto", "xliff"],
        "adapter_absence_blocks_release": False,
        "policy": policy_public_reference,
        "public_baseline": baseline_public_reference,
    }
    for row in course_rows:
        binding = row.get("layers", {}).get("interoperability", {}).get("design_policy")
        require(binding == expected_policy_binding, f"design-policy binding drift: {row.get('course_id')}")

    manifest_path = PROJECT / "backend/course-capsule-v1/generated/manifest.json"
    manifest_data, manifest = load_json_object(manifest_path, "course-capsule-v1 manifest")
    require(
        manifest.get("schema_id") == "interlanguage/open-course-capsule-manifest/v1"
        and manifest.get("schema_version") == "1.0.0",
        "course-capsule manifest schema identity drift",
    )
    inputs = manifest.get("inputs")
    require(isinstance(inputs, list), "course-capsule manifest inputs missing")
    inputs_by_path: dict[str, dict[str, Any]] = {}
    for entry in inputs:
        require(isinstance(entry, dict) and isinstance(entry.get("path"), str), "invalid capsule manifest input")
        path_text = str(entry["path"])
        require(path_text not in inputs_by_path, f"duplicate capsule manifest input: {path_text}")
        inputs_by_path[path_text] = entry
    manifest_required_inputs = {
        "backend/course-capsule-v1/authority/backend-design-policy-v1.json": policy_data,
        "backend/course-capsule-v1/authority/public-baseline-v0.62.12.json": baseline_data,
        "schemas/course-capsule-v1/backend-design-policy-v1.schema.json": policy_schema_data,
        "schemas/course-capsule-v1/public-baseline-v1.schema.json": baseline_schema_data,
        "backend/authority/learner-tools-v1.json": learner_tools_data,
        "schemas/course-capsule-v1/course-capsule-v1.schema.json": course_schema_data,
    }
    for path_text, data in manifest_required_inputs.items():
        entry = inputs_by_path.get(path_text)
        require(
            isinstance(entry, dict)
            and entry.get("bytes") == len(data)
            and entry.get("sha256") == sha256(data),
            f"capsule manifest input identity drift: {path_text}",
        )
    expected_manifest_policy = {
        "profile": "thin_format_neutral_zero_copy",
        "authority": {
            "path": "backend/course-capsule-v1/authority/backend-design-policy-v1.json",
            "bytes": len(policy_data),
            "sha256": policy_sha,
        },
        "schema": {
            "path": "schemas/course-capsule-v1/backend-design-policy-v1.schema.json",
            "bytes": len(policy_schema_data),
            "sha256": sha256(policy_schema_data),
        },
        "public_projection": policy_public_reference,
    }
    require(
        manifest.get("design_policy") == expected_manifest_policy,
        "capsule manifest design-policy binding drift",
    )
    expected_manifest_baseline = {
        "version": "v0.62.12",
        "authority": {
            "path": "backend/course-capsule-v1/authority/public-baseline-v0.62.12.json",
            "bytes": len(baseline_data),
            "sha256": baseline_sha,
        },
        "schema": {
            "path": "schemas/course-capsule-v1/public-baseline-v1.schema.json",
            "bytes": len(baseline_schema_data),
            "sha256": sha256(baseline_schema_data),
        },
        "public_projection": baseline_public_reference,
    }
    require(
        manifest.get("public_baseline") == expected_manifest_baseline,
        "capsule manifest public-baseline binding drift",
    )
    expected_manifest_summary = {
        "course_count": len(course_rows),
        "published_count": sum(row["course"]["state"] == "published" for row in course_rows),
        "production_count": sum(row["course"]["state"] == "production" for row in course_rows),
        "prerequisite_edge_count": sum(len(row["course"]["prerequisites"]) for row in course_rows),
        "educator_course_count": sum(
            bool(row["layers"]["educator"]["features"] or row["layers"]["educator"]["resources"])
            for row in course_rows
        ),
        "educator_resource_count": sum(
            len(row["layers"]["educator"]["resources"]) for row in course_rows
        ),
        "learner_tool_course_count": sum(
            bool(row["layers"]["learner"]["tools"]) for row in course_rows
        ),
        "learner_tool_count": sum(len(row["layers"]["learner"]["tools"]) for row in course_rows),
        "verified_semantic_adapter_count": sum(
            row["layers"]["interoperability"]["semantic_adapter"]["status"] == "verified"
            for row in course_rows
        ),
        "legacy_semantic_adapter_count": sum(
            row["layers"]["interoperability"]["semantic_adapter"]["status"] == "legacy_verified"
            for row in course_rows
        ),
    }
    require(
        expected_manifest_summary["course_count"] == 40
        and expected_manifest_summary["published_count"] == 35
        and expected_manifest_summary["production_count"] == 5
        and manifest.get("summary") == expected_manifest_summary,
        "course-capsule manifest summary drift",
    )

    catalog_courses = learner_tools.get("courses")
    require(isinstance(catalog_courses, list) and catalog_courses, "learner-tool catalog is empty")
    tools_by_course: dict[str, list[dict[str, Any]]] = {}
    for course_entry in catalog_courses:
        require(isinstance(course_entry, dict), "invalid learner-tool course entry")
        course_id = course_entry.get("course_id")
        tools = course_entry.get("tools")
        require(isinstance(course_id, str) and isinstance(tools, list) and tools, "invalid learner-tool course boundary")
        require(course_id not in tools_by_course, f"duplicate learner-tool course: {course_id}")
        tools_by_course[course_id] = tools
    capsule_by_course = {str(row["course_id"]): row for row in course_rows}
    require(set(tools_by_course) <= set(capsule_by_course), "learner-tool course absent from capsules")
    for course_id, row in capsule_by_course.items():
        capsule_tools = row.get("layers", {}).get("learner", {}).get("tools")
        require(capsule_tools == tools_by_course.get(course_id, []), f"learner-tool catalog/capsule drift: {course_id}")

    capsule_zip_path = REPLACEMENT_SOURCE_ALLOWLIST["program-matematika-indonesia-course-capsule-v1.zip"]
    try:
        with zipfile.ZipFile(capsule_zip_path, "r") as archive:
            members = {item.filename: item for item in archive.infolist() if not item.is_dir()}
            seen_tool_ids: set[str] = set()
            for course_id, tools in sorted(tools_by_course.items()):
                for tool in tools:
                    require(isinstance(tool, dict) and isinstance(tool.get("tool_id"), str), f"invalid learner tool: {course_id}")
                    tool_id = str(tool["tool_id"])
                    require(tool_id not in seen_tool_ids, f"duplicate learner tool ID: {tool_id}")
                    seen_tool_ids.add(tool_id)
                    for evidence_key in ("page", "resource", "evidence"):
                        evidence = tool.get(evidence_key)
                        require(isinstance(evidence, dict) and isinstance(evidence.get("path"), str), f"learner-tool {evidence_key} missing: {tool_id}")
                        identity = expected_file_identity(str(evidence["path"]))
                        require(
                            evidence.get("bytes") == identity["bytes"]
                            and evidence.get("sha256") == identity["sha256"],
                            f"learner-tool {evidence_key} identity drift: {tool_id}",
                        )
                        member = members.get(str(identity["path"]))
                        require(member is not None, f"learner-tool {evidence_key} absent from capsule ZIP: {tool_id}")
                        require(
                            archive.read(member) == identity["data"],
                            f"learner-tool {evidence_key} ZIP byte drift: {tool_id}",
                        )
    except zipfile.BadZipFile as exc:
        raise BuildError("invalid capsule ZIP during learner-tool closure") from exc

    # Keep variables measured so future edits cannot silently drop a validated
    # shared instance from this cross-artifact gate.
    require(
        all(len(data) > 0 for data in (course_schema_data, manifest_data, delivery_data, delivery_schema_data, adapter_data, adapter_schema_data)),
        "empty cross-artifact validation input",
    )


def validate_predecessor_receipts() -> dict[str, dict[str, Any]]:
    require(PREDECESSOR_RECEIPT.is_file(), "v0.62.12 publication receipt missing")
    receipt_data = PREDECESSOR_RECEIPT.read_bytes()
    require(
        (len(receipt_data), sha256(receipt_data)) == EXPECTED_PREDECESSOR_RECEIPT,
        "v0.62.12 publication receipt identity drift",
    )
    receipt = validate_json(PREDECESSOR_RECEIPT.name, receipt_data)
    require(isinstance(receipt, dict), "v0.62.12 publication receipt is not an object")
    require(receipt.get("version") == PREDECESSOR_VERSION, "predecessor version drift")
    require(receipt.get("state") == "published_open_method_capsule_successor", "predecessor state drift")
    require(receipt.get("payload_total_bytes") == EXPECTED_PREDECESSOR_TOTAL_BYTES, "predecessor total-byte drift")
    require(
        receipt.get("payload_inventory_aggregate_sha256") == EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
        "predecessor inventory aggregate drift",
    )
    github_authority = receipt.get("github_authority")
    zenodo = receipt.get("zenodo")
    privacy = receipt.get("privacy")
    require(
        isinstance(github_authority, dict)
        and github_authority.get("tag_target_commit") == EXPECTED_PREDECESSOR_TAG_COMMIT
        and github_authority.get("receipt_sha256") == EXPECTED_PREDECESSOR_GITHUB_RECEIPT[1]
        and github_authority.get("anonymous_readback") == "pass_100_of_100",
        "predecessor GitHub authority drift",
    )
    require(
        isinstance(zenodo, dict)
        and zenodo.get("record_id") == EXPECTED_PREDECESSOR_RECORD_ID
        and zenodo.get("access_right") == "open"
        and zenodo.get("file_count") == 100
        and zenodo.get("anonymous_readback") == "pass_100_of_100",
        "predecessor Zenodo authority drift",
    )
    require(
        isinstance(privacy, dict)
        and privacy.get("credentials_recorded") is False
        and privacy.get("personal_name_recorded") is False
        and privacy.get("absolute_profile_paths_recorded") is False,
        "predecessor privacy receipt drift",
    )
    require(PREDECESSOR_GITHUB_RECEIPT.is_file(), "v0.62.12 GitHub receipt missing")
    github_data = PREDECESSOR_GITHUB_RECEIPT.read_bytes()
    require(
        (len(github_data), sha256(github_data)) == EXPECTED_PREDECESSOR_GITHUB_RECEIPT,
        "v0.62.12 GitHub receipt identity drift",
    )

    payload = receipt.get("payload_inventory")
    require(isinstance(payload, list) and len(payload) == 100, "predecessor inventory is not 100 rows")
    by_name: dict[str, dict[str, Any]] = {}
    anonymous_urls: set[str] = set()
    expected_row_keys = {
        "anonymous_byte_identity",
        "anonymous_url",
        "bytes",
        "md5",
        "name",
        "provenance",
        "sha256",
    }
    for row in payload:
        require(isinstance(row, dict), "invalid predecessor inventory row")
        require(set(row) == expected_row_keys, "predecessor inventory row shape drift")
        name = row.get("name")
        require(isinstance(name, str), "predecessor inventory name missing")
        safe_flat_name(name)
        require(name not in by_name, f"duplicate predecessor filename: {name}")
        require(isinstance(row.get("bytes"), int) and row["bytes"] >= 0, f"invalid predecessor byte count: {name}")
        require(re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256", ""))) is not None, f"invalid predecessor SHA-256: {name}")
        require(re.fullmatch(r"[0-9a-f]{32}", str(row.get("md5", ""))) is not None, f"invalid predecessor MD5: {name}")
        require(row.get("anonymous_byte_identity") is True, f"predecessor anonymous-byte identity is not true: {name}")
        anonymous_url = row.get("anonymous_url")
        expected_url = f"{PREDECESSOR_ANONYMOUS_URL_ROOT}/{quote(name, safe='')}/content"
        require(
            isinstance(anonymous_url, str) and anonymous_url == expected_url,
            f"predecessor anonymous URL drift: {name}",
        )
        require(anonymous_url not in anonymous_urls, f"duplicate predecessor anonymous URL: {name}")
        require(isinstance(row.get("provenance"), str) and bool(row["provenance"]), f"predecessor provenance missing: {name}")
        anonymous_urls.add(anonymous_url)
        by_name[name] = row
    require(len(anonymous_urls) == 100, "predecessor anonymous URL boundary is not 100")
    require(len(RETAINED_ALLOWLIST) == 78, "retained allowlist cardinality is not 78")
    require(len(SAME_NAME_REPLACEMENTS) == 9, "same-name replacement cardinality is not 9")
    require(len(PURE_OMISSIONS) == 13, "pure-omission cardinality is not 13")
    predecessor_sets = (RETAINED_ALLOWLIST, SAME_NAME_REPLACEMENTS, PURE_OMISSIONS)
    require(
        all(left.isdisjoint(right) for index, left in enumerate(predecessor_sets) for right in predecessor_sets[index + 1 :]),
        "predecessor retained/replacement/omission sets overlap",
    )
    require(
        RETAINED_ALLOWLIST | SAME_NAME_REPLACEMENTS | PURE_OMISSIONS == set(by_name),
        "explicit 78/9/13 predecessor partition does not equal receipt inventory",
    )
    require(sum(int(row["bytes"]) for row in payload) == EXPECTED_PREDECESSOR_TOTAL_BYTES, "recomputed predecessor byte total drift")
    require(inventory_aggregate(payload) == EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE, "recomputed predecessor aggregate drift")
    return by_name


def validate_complete_predecessor_directory(
    directory: Path,
    by_name: dict[str, dict[str, Any]],
) -> None:
    require(directory.is_dir() and not directory.is_symlink(), "predecessor payload is not a regular directory")
    entries = list(directory.iterdir())
    require(len(entries) == 100, "predecessor payload directory is not 100 entries")
    require(
        all(item.is_file() and not item.is_symlink() for item in entries),
        "predecessor payload is not a flat regular-file directory",
    )
    require({item.name for item in entries} == set(by_name), "predecessor payload filenames differ from receipt")
    measured: list[dict[str, Any]] = []
    for name in sorted(by_name):
        data = (directory / name).read_bytes()
        expected = by_name[name]
        require(
            (len(data), sha256(data)) == (expected["bytes"], expected["sha256"]),
            f"predecessor payload readback identity drift: {name}",
        )
        measured.append({"name": name, "bytes": len(data), "sha256": sha256(data)})
    require(
        sum(int(row["bytes"]) for row in measured) == EXPECTED_PREDECESSOR_TOTAL_BYTES,
        "predecessor payload readback total-byte drift",
    )
    require(
        inventory_aggregate(measured) == EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
        "predecessor payload readback aggregate drift",
    )


def validate_predecessor_payload(by_name: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    require(PREDECESSOR_DIR.is_dir(), "local v0.62.12 predecessor payload directory missing")
    entries = list(PREDECESSOR_DIR.iterdir())
    require(all(item.is_file() and not item.is_symlink() for item in entries), "predecessor payload is not a flat regular-file directory")
    actual_names = {item.name for item in entries}
    require(actual_names == set(by_name), "local predecessor payload filenames differ from receipt")
    retained_facts: list[dict[str, Any]] = []
    for name in sorted(RETAINED_ALLOWLIST):
        path = PREDECESSOR_DIR / name
        data = path.read_bytes()
        expected = by_name[name]
        require((len(data), sha256(data)) == (expected["bytes"], expected["sha256"]), f"retained predecessor identity drift: {name}")
        privacy_scan(name, data)
        retained_facts.append(fact(name, data, "retained_exact_from_v0.62.12", path))
    return retained_facts


def collect_external_facts(
    source_commit: str,
    predecessor_rows: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    require(set(REPLACEMENT_SOURCE_ALLOWLIST) == SAME_NAME_REPLACEMENTS, "replacement source boundary drift")
    require(len(PURE_ADDITION_SOURCE_ALLOWLIST) == 8, "prepared pure-addition cardinality is not 8")
    combined_sources = {**REPLACEMENT_SOURCE_ALLOWLIST, **PURE_ADDITION_SOURCE_ALLOWLIST}
    require(len(combined_sources) == 17, "external source filename collision")
    missing = [
        {"name": name, "source": relative_display(path)}
        for name, path in sorted(combined_sources.items())
        if not path.is_file()
    ]
    if missing:
        raise BuildError("missing release sources: " + json.dumps(missing, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    rows: list[dict[str, Any]] = []
    commit_exempt = {
        "program-matematika-indonesia-backend-v2.3.1-a00-o001-assessment-adapter-v0.1.0.zip",
        "program-matematika-indonesia-course-capsule-v1.zip",
        "GITHUB_A00_O001_V231_SOURCE_PUBLICATION_RECEIPT.json",
    }
    for name, path in sorted(combined_sources.items()):
        safe_flat_name(name)
        data = path.read_bytes()
        if name not in commit_exempt:
            require_committed_bytes(source_commit, path, data, name)
        details = validate_external(name, path, data)
        if name in SAME_NAME_REPLACEMENTS:
            predecessor = predecessor_rows[name]
            require(
                (len(data), sha256(data)) != (predecessor["bytes"], predecessor["sha256"]),
                f"same-name replacement is byte-identical to predecessor: {name}",
            )
            provenance = "v0.62.13_same_name_replacement"
        else:
            provenance = "v0.62.13_pure_addition_external"
        row = fact(name, data, provenance, path)
        row.update(details)
        rows.append(row)
    validate_cross_artifact_contracts()
    return rows


def canonical_json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def build_combined_receipt(
    source_row: dict[str, Any],
    navigator_row: dict[str, Any],
    external_rows: list[dict[str, Any]],
) -> bytes:
    external = {str(row["name"]): row for row in external_rows}
    adapter = external["program-matematika-indonesia-backend-v2.3.1-a00-o001-assessment-adapter-v0.1.0.zip"]
    adapter_validation = external["A00_O001_V231_ADAPTER_VALIDATION_REPORT_v0.1.0.json"]
    github_receipt = external["GITHUB_A00_O001_V231_SOURCE_PUBLICATION_RECEIPT.json"]
    capsule_package = external["program-matematika-indonesia-course-capsule-v1.zip"]
    packaged_d40_binding = capsule_package.get("d40_independent_anonymous_readback")
    expected_packaged_d40_binding = {
        "receipt_artifact": dict(D40_READBACK_IDENTITY),
        "validation_receipt": {
            "member": D40_VALIDATION_RECEIPT_MEMBER,
            "state": "pass",
            "check": "pass_7_of_7",
            "artifact": dict(D40_READBACK_IDENTITY),
        },
    }
    require(
        packaged_d40_binding == expected_packaged_d40_binding,
        "course-capsule package D40 validation binding drift",
    )
    validation_value = validate_json(
        adapter_validation["name"],
        PURE_ADDITION_SOURCE_ALLOWLIST[adapter_validation["name"]].read_bytes(),
    )
    github_value = validate_json(
        github_receipt["name"],
        PURE_ADDITION_SOURCE_ALLOWLIST[github_receipt["name"]].read_bytes(),
    )
    require(
        isinstance(validation_value, dict)
        and validation_value.get("status") == "PASS"
        and validation_value.get("assessment_capability", {}).get("status") == "PASS",
        "A00 adapter validation report is not PASS",
    )
    github_repository = github_value.get("repository") if isinstance(github_value, dict) else None
    github_identity = github_value.get("source_identity") if isinstance(github_value, dict) else None
    github_checks = github_value.get("checks") if isinstance(github_value, dict) else None
    require(
        isinstance(github_value, dict)
        and github_value.get("authentication") == "anonymous"
        and isinstance(github_repository, dict)
        and github_repository.get("url") == EXPECTED_A00_REPOSITORY
        and github_repository.get("visibility") == "public"
        and github_repository.get("private") is False
        and isinstance(github_identity, dict)
        and re.fullmatch(r"[0-9a-f]{40}", str(github_identity.get("commit", ""))) is not None
        and re.fullmatch(r"[0-9a-f]{40}", str(github_identity.get("tree", ""))) is not None
        and isinstance(github_checks, dict)
        and github_checks.get("overall") == "pass"
        and all(value is True for key, value in github_checks.items() if key != "overall"),
        "A00 anonymous public source receipt is not a complete PASS",
    )

    capsule_path = REPLACEMENT_SOURCE_ALLOWLIST["course-capsules-v1.jsonl"]
    capsule_data = capsule_path.read_bytes()
    capsules = validate_jsonl(capsule_path.name, capsule_data)
    d30_rows = [row for row in capsules if row.get("course_id") == "D30"]
    require(len(d30_rows) == 1, "D30 capsule boundary is not exactly one row")
    d30 = d30_rows[0]
    d30_learner = d30.get("layers", {}).get("learner")
    d30_native = d30.get("course_native")
    require(
        d30.get("course", {}).get("state") == "published"
        and isinstance(d30_learner, dict)
        and d30_learner.get("status") == "verified"
        and isinstance(d30_native, dict)
        and d30_native.get("version") == "2026.08.30-checkpoint.38",
        "D30 combined-receipt evidence drift",
    )
    d40_rows = [row for row in capsules if row.get("course_id") == "D40"]
    require(len(d40_rows) == 1, "D40 capsule boundary is not exactly one row")
    d40 = d40_rows[0]
    d40_learner = d40.get("layers", {}).get("learner")
    d40_native = d40.get("course_native")
    require(D40_READBACK_PATH.is_file(), "D40 independent anonymous-readback receipt missing")
    d40_readback_data = D40_READBACK_PATH.read_bytes()
    d40_readback = validate_d40_readback_receipt(d40_readback_data)
    require_committed_bytes(
        str(source_row["source_commit"]),
        D40_READBACK_PATH,
        d40_readback_data,
        "D40 independent anonymous-readback receipt",
    )
    validate_d40_capsule_readback_binding(d40, d40_readback)
    require(
        d40.get("course", {}).get("state") == "published"
        and isinstance(d40_learner, dict)
        and d40_learner.get("status") == "verified"
        and isinstance(d40_native, dict)
        and d40_native.get("version") == "2026.08.31-d40-complete"
        and d40_native.get("zenodo") == "https://doi.org/10.5281/zenodo.22184259"
        and d40_learner.get("portable_html", {}).get("sha256")
        == "a370bba5ddb54081387a484a304b24af92691c3bc167db964c486625a79add59",
        "D40 combined-receipt evidence drift",
    )
    landing_path = PROJECT / "docs/index.html"
    landing_data = landing_path.read_bytes()
    require_committed_bytes(str(source_row["source_commit"]), landing_path, landing_data, "central learner landing page")
    receipt = {
        "schema_id": "program-matematika-indonesia/a00-o001-v231-adapter-learner-central-receipt/1",
        "recorded_date": "2026-08-31",
        "status": "PASS_VALIDATED_NOT_YET_RELEASED",
        "release": {
            "version": VERSION,
            "predecessor": PREDECESSOR_VERSION,
            "predecessor_partition": {
                "unchanged": 78,
                "same_name_replacements": 9,
                "pure_omissions": 13,
            },
            "successor_partition": {
                "unchanged": 78,
                "same_name_replacements": 9,
                "pure_additions": 13,
                "files": 100,
            },
        },
        "central_source": {
            "repository": EXPECTED_REPOSITORY,
            "commit": source_row["source_commit"],
            "tree": source_row["source_tree"],
            "archive": {
                "name": source_row["name"],
                "bytes": source_row["bytes"],
                "sha256": source_row["sha256"],
                "zip_comment": source_row["zip_comment"],
                "deterministic_replay": source_row["deterministic_replay"],
            },
        },
        "central_learner_surface": {
            "url": "https://kokunoyumeto.github.io/program-matematika-indonesia/",
            "local_path": "docs/index.html",
            "bytes": len(landing_data),
            "sha256": sha256(landing_data),
            "course_capsules": 40,
            "published": 35,
            "production": 5,
            "production_role_ids": ["A20", "A30", "B95", "C140", "D100"],
            "distinct_published_doi_records": 31,
        },
        "a00_o001": {
            "adapter_archive": {
                "name": adapter["name"],
                "bytes": adapter["bytes"],
                "sha256": adapter["sha256"],
                "files": adapter.get("zip_files"),
            },
            "adapter_validation": {
                "name": adapter_validation["name"],
                "bytes": adapter_validation["bytes"],
                "sha256": adapter_validation["sha256"],
                "status": "PASS",
                "assessments": 8105,
                "components": 13345,
                "explicit_solutions": 5240,
                "solution_gaps": 2865,
                "exact_html_anchors": 21450,
            },
            "learner_navigator": {
                "name": navigator_row["name"],
                "bytes": navigator_row["bytes"],
                "sha256": navigator_row["sha256"],
                "entry_prefix": navigator_row["entry_prefix"],
                "source_files": navigator_row["source_files"],
                "assessment_counts": navigator_row["assessment_counts"],
                "anchor_counts": navigator_row["anchor_counts"],
                "deterministic_replay": navigator_row["deterministic_replay"],
            },
            "public_source_receipt": {
                "name": github_receipt["name"],
                "bytes": github_receipt["bytes"],
                "sha256": github_receipt["sha256"],
                "status": "PASS",
                "repository": github_repository["url"],
                "commit": github_identity["commit"],
                "tree": github_identity["tree"],
                "learner_pages": github_value["learner_pages"],
            },
        },
        "d30_zero_copy_delivery": {
            "course_state": d30["course"]["state"],
            "version": d30_native["version"],
            "zenodo": d30_native["zenodo"],
            "repository": d30_native["repository"],
            "capsule_row_sha256": sha256(
                (json.dumps(d30, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
            ),
            "online_html": d30_learner["online_html"],
            "pdf": d30_learner["pdf"],
            "portable_html": d30_learner["portable_html"],
        },
        "d40_zero_copy_delivery": {
            "course_state": d40["course"]["state"],
            "version": d40_native["version"],
            "zenodo": d40_native["zenodo"],
            "capsule_row_sha256": sha256(
                (json.dumps(d40, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
            ),
            "online_html": d40_learner["online_html"],
            "pdf": d40_learner["pdf"],
            "portable_html": d40_learner["portable_html"],
            "d40_independent_anonymous_readback": packaged_d40_binding,
        },
        "privacy": {
            "credentials_recorded": False,
            "personal_name_recorded": False,
            "absolute_profile_paths_recorded": False,
        },
        "model_provenance": "OpenAI Codex gpt-5.6-sol, Ultra",
    }
    data = canonical_json_bytes(receipt)
    privacy_scan(A00_COMBINED_RECEIPT_NAME, data)
    return data


def release_notes(source_row: dict[str, Any]) -> bytes:
    text = f"""# Program Matematika Indonesia v0.62.13 — backend modular untuk pelajar dan pengajar

Mulai belajar dari situs Bahasa Indonesia:

- https://kokunoyumeto.github.io/program-matematika-indonesia/

Rilis aditif ini mempertahankan backend asli setiap kursus sebagai otoritas, lalu menghubungkannya melalui kapsul tujuh lapis yang tipis dan tanpa penyalinan korpus. Kapsul mencakup peta kurikulum, ledger terjemahan/provenans/hak, produksi yang dapat direproduksi, pengantaran pelajar, dukungan pengajar, federasi komponen, serta interoperabilitas. MyST, Quarto, dan XLIFF tetap adapter opsional untuk kebutuhan konkret; ketidakhadirannya bukan penghalang rilis.

Permukaan publik mencakup 40 kapsul—35 sudah dipublikasikan dan 5 masih diproduksi (A20, A30, B95, C140, dan D100)—melalui 31 rekaman DOI edisi terbit yang berbeda, navigasi Bahasa Indonesia dengan jalur tanpa JavaScript, model pengantaran luring, bahan pengajar berbasis bukti, dan alat latihan A00. B30 kini mengikat edisi lengkap CLP2 1.243 halaman. D30 memuat bukti zero-copy menuju edisi final proses stokastik checkpoint 38 (447 halaman). D40 kini juga memuat bukti zero-copy menuju edisi lengkap 679 halaman beserta pembaca HTML luring, latihan, laboratorium, pendamping FEniCSx, dan dua backend semantik. Buku-buku itu tetap berada dalam rilis kursus masing-masing, bukan disalin ke payload pusat.

## Batas penggantian 100 berkas

Payload mempertahankan 78 berkas v0.62.12 secara byte-identik, mengganti tepat 9 nama dengan byte v0.62.13 yang divalidasi, dan meninggalkan 13 nama khusus pendahulu pada record terbuka terdahulu. Versi ini menambahkan tepat 13 nama baru. Hasil akhirnya tepat 100 berkas datar, dan manifest checksum memuat 99 berkas selain dirinya sendiri.

Arsip sumber dibuat secara deterministik dengan `git archive --format=zip` dari commit `{source_row['source_commit']}` dan pohon `{source_row['source_tree']}`. Komentar ZIP mengikat commit tersebut; arsip berukuran {source_row['bytes']} byte dengan SHA-256 `{source_row['sha256']}`.

## Provenans model

OpenAI Codex gpt-5.6-sol, Ultra.
"""
    return text.replace("\r\n", "\n").encode("utf-8")


def expected_checksum_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    ordered = sorted(rows, key=lambda item: str(item["name"]))
    require(len(ordered) == 99, "pre-checksum inventory is not 99 files")
    require(len({str(row["name"]) for row in ordered}) == 99, "duplicate pre-checksum filename")
    return "".join(f"{row['sha256']}  {row['name']}\n" for row in ordered).encode("utf-8")


def validate_checksum_manifest(data: bytes, expected_rows: Iterable[dict[str, Any]]) -> None:
    expected = expected_checksum_bytes(expected_rows)
    require(data == expected, "release checksum manifest byte drift")
    lines = data.decode("utf-8").splitlines()
    require(len(lines) == 99, "release checksum manifest does not contain 99 rows")
    require(all(CHECKSUM_NAME not in line for line in lines), "checksum manifest incorrectly hashes itself")


def validate_boundary_names() -> None:
    all_names = (
        RETAINED_ALLOWLIST
        | SAME_NAME_REPLACEMENTS
        | PURE_OMISSIONS
        | set(REPLACEMENT_SOURCE_ALLOWLIST)
        | PURE_ADDITION_NAMES
    )
    for name in all_names:
        safe_flat_name(name)
    require(set(REPLACEMENT_SOURCE_ALLOWLIST) == SAME_NAME_REPLACEMENTS, "replacement-source set differs from exact replacement names")
    require(len(PURE_ADDITION_NAMES) == 13, "pure-addition cardinality is not 13")
    predecessor_names = RETAINED_ALLOWLIST | SAME_NAME_REPLACEMENTS | PURE_OMISSIONS
    successor_names = RETAINED_ALLOWLIST | SAME_NAME_REPLACEMENTS | PURE_ADDITION_NAMES
    require(PURE_ADDITION_NAMES.isdisjoint(predecessor_names), "pure addition collides with predecessor filename")
    require(PURE_OMISSIONS.isdisjoint(successor_names), "pure omission survived into successor")
    require(len(predecessor_names) == 100, "predecessor 78+9+13 equation drift")
    require(len(successor_names) == 100, "successor 78+9+13 equation drift")


def prepare_inputs(
    source_commit: str,
    source_tree: str,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, tuple[bytes, dict[str, Any]]],
]:
    validate_boundary_names()
    predecessor_rows = validate_predecessor_receipts()
    retained = validate_predecessor_payload(predecessor_rows)
    external = collect_external_facts(source_commit, predecessor_rows)

    source_data, source_details = build_source_archive(source_commit, source_tree)
    source_row = fact(SOURCE_ZIP_NAME, source_data, "deterministic_git_archive_of_explicit_commit")
    source_row.update(source_details)

    navigator_data, navigator_details = build_a00_navigator_archive(source_commit)
    navigator_row = fact(
        A00_NAVIGATOR_ZIP_NAME,
        navigator_data,
        "generated_deterministic_a00_learner_navigator",
    )
    navigator_row.update(navigator_details)

    combined_data = build_combined_receipt(source_row, navigator_row, external)
    combined_row = fact(
        A00_COMBINED_RECEIPT_NAME,
        combined_data,
        "generated_a00_adapter_navigator_central_d30_receipt",
    )
    generated = {
        SOURCE_ZIP_NAME: (source_data, source_row),
        A00_NAVIGATOR_ZIP_NAME: (navigator_data, navigator_row),
        A00_COMBINED_RECEIPT_NAME: (combined_data, combined_row),
    }
    return retained, external, generated


def stage_payload(
    destination: Path,
    retained: list[dict[str, Any]],
    external: list[dict[str, Any]],
    generated: dict[str, tuple[bytes, dict[str, Any]]],
) -> list[dict[str, Any]]:
    require(destination.is_dir() and not any(destination.iterdir()), "staging directory is not empty")
    rows: list[dict[str, Any]] = []
    for row in sorted(retained, key=lambda item: str(item["name"])):
        name = str(row["name"])
        source = PREDECESSOR_DIR / name
        data = source.read_bytes()
        require((len(data), sha256(data)) == (row["bytes"], row["sha256"]), f"retained source changed after validation: {name}")
        (destination / name).write_bytes(data)
        rows.append(fact(name, data, "retained_exact_from_v0.62.12"))
    external_sources = {**REPLACEMENT_SOURCE_ALLOWLIST, **PURE_ADDITION_SOURCE_ALLOWLIST}
    external_by_name = {str(row["name"]): row for row in external}
    require(set(external_by_name) == set(external_sources), "measured external-source boundary drift")
    for name, source in sorted(external_sources.items()):
        measured = external_by_name[name]
        data = source.read_bytes()
        require((len(data), sha256(data)) == (measured["bytes"], measured["sha256"]), f"release source changed after validation: {name}")
        (destination / name).write_bytes(data)
        rows.append(dict(measured))
    require(
        set(generated) == {SOURCE_ZIP_NAME, A00_NAVIGATOR_ZIP_NAME, A00_COMBINED_RECEIPT_NAME},
        "generated release-artifact boundary drift",
    )
    for name, (data, measured) in sorted(generated.items()):
        require((len(data), sha256(data)) == (measured["bytes"], measured["sha256"]), f"generated artifact changed after validation: {name}")
        (destination / name).write_bytes(data)
        rows.append(dict(measured))
    source_row = generated[SOURCE_ZIP_NAME][1]
    notes = release_notes(source_row)
    privacy_scan(NOTES_NAME, notes)
    (destination / NOTES_NAME).write_bytes(notes)
    rows.append(fact(NOTES_NAME, notes, "generated_release_notes"))
    require(len(rows) == 99, "pre-checksum 78+9+12 inventory is not 99 files")
    checksum = expected_checksum_bytes(rows)
    validate_checksum_manifest(checksum, rows)
    (destination / CHECKSUM_NAME).write_bytes(checksum)
    rows.append(fact(CHECKSUM_NAME, checksum, "generated_release_checksum"))
    validate_staged_release(destination, rows)
    return sorted(rows, key=lambda item: str(item["name"]))


def validate_staged_release(directory: Path, expected_rows: list[dict[str, Any]]) -> None:
    require(len(expected_rows) == 100, "final inventory is not 100 rows")
    entries = list(directory.iterdir())
    require(len(entries) == 100, "staged release does not contain 100 entries")
    require(all(item.is_file() and not item.is_symlink() for item in entries), "staged release is not a flat regular-file inventory")
    expected_by_name = {str(row["name"]): row for row in expected_rows}
    require(len(expected_by_name) == 100, "duplicate final inventory filename")
    require({item.name for item in entries} == set(expected_by_name), "staged release filename boundary drift")
    for name, row in expected_by_name.items():
        data = (directory / name).read_bytes()
        require((len(data), sha256(data)) == (row["bytes"], row["sha256"]), f"staged release readback mismatch: {name}")
    pre_checksum = [row for row in expected_rows if row["name"] != CHECKSUM_NAME]
    validate_checksum_manifest((directory / CHECKSUM_NAME).read_bytes(), pre_checksum)


def compare_existing(expected_directory: Path, expected_rows: list[dict[str, Any]]) -> None:
    require(OUTPUT_DIR.is_dir() and not OUTPUT_DIR.is_symlink(), "existing v0.62.13 output is not a regular directory")
    actual_entries = list(OUTPUT_DIR.iterdir())
    require(len(actual_entries) == 100, "existing v0.62.13 output is not 100 entries")
    require(all(item.is_file() and not item.is_symlink() for item in actual_entries), "existing v0.62.13 output is not a flat regular-file inventory")
    expected_names = {str(row["name"]) for row in expected_rows}
    require({item.name for item in actual_entries} == expected_names, "existing v0.62.13 filenames differ from expected")
    for name in sorted(expected_names):
        expected_data = (expected_directory / name).read_bytes()
        actual_data = (OUTPUT_DIR / name).read_bytes()
        require(actual_data == expected_data, f"existing v0.62.13 byte mismatch: {name}")


def summary(status: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    source = next(row for row in rows if row["name"] == SOURCE_ZIP_NAME)
    return {
        "status": status,
        "version": VERSION,
        "output": relative_display(OUTPUT_DIR),
        "predecessor_version": PREDECESSOR_VERSION,
        "predecessor_partition": {
            "retained_exact_files": 78,
            "same_name_replacement_files": 9,
            "pure_omissions_preserved_in_public_predecessor": 13,
            "files": 100,
        },
        "successor_partition": {
            "retained_exact_files": 78,
            "same_name_replacement_files": 9,
            "pure_addition_files": 13,
            "files": 100,
        },
        "checksum_rows": 99,
        "files": 100,
        "bytes": sum(int(row["bytes"]) for row in rows),
        "inventory_aggregate_sha256": inventory_aggregate(rows),
        "source_archive": {
            "name": source["name"],
            "bytes": source["bytes"],
            "sha256": source["sha256"],
            "commit": source["source_commit"],
            "tree": source["source_tree"],
            "zip_comment": source["zip_comment"],
            "deterministic_replay": source["deterministic_replay"],
        },
        "checksum": next(row for row in rows if row["name"] == CHECKSUM_NAME),
    }


def remove_safe_hydration_temp(path: Path) -> None:
    require(
        path.parent.resolve() == RELEASES_DIR.resolve()
        and path.name.startswith(PREDECESSOR_HYDRATION_TEMP_PREFIX)
        and path not in {PREDECESSOR_DIR, OUTPUT_DIR},
        "unsafe predecessor hydration cleanup path",
    )
    if path.exists() or path.is_symlink():
        require(
            path.is_dir() and not path.is_symlink(),
            "predecessor hydration temporary path is not a regular directory",
        )
        shutil.rmtree(path)


def run_hydrate_predecessor() -> dict[str, Any]:
    require(
        RELEASES_DIR.is_dir() and not RELEASES_DIR.is_symlink(),
        "releases directory missing or not a regular directory",
    )
    require(
        not PREDECESSOR_DIR.exists() and not PREDECESSOR_DIR.is_symlink(),
        "refusing to overwrite existing releases/v0.62.12 predecessor path",
    )
    predecessor_rows = validate_predecessor_receipts()
    try:
        temporary = Path(
            tempfile.mkdtemp(prefix=PREDECESSOR_HYDRATION_TEMP_PREFIX, dir=RELEASES_DIR)
        )
    except OSError as exc:
        raise BuildError(f"cannot create predecessor hydration staging directory: {exc}") from exc
    committed = False
    try:
        require(
            temporary.parent.resolve() == RELEASES_DIR.resolve()
            and temporary.name.startswith(PREDECESSOR_HYDRATION_TEMP_PREFIX)
            and temporary.is_dir()
            and not temporary.is_symlink()
            and not any(temporary.iterdir()),
            "invalid predecessor hydration staging directory",
        )
        opener = build_opener(ProxyHandler({}))
        for name in sorted(predecessor_rows):
            row = predecessor_rows[name]
            expected_bytes = int(row["bytes"])
            expected_sha256 = str(row["sha256"])
            anonymous_url = str(row["anonymous_url"])
            request = Request(
                anonymous_url,
                headers={
                    "Accept": "*/*",
                    "Accept-Encoding": "identity",
                    "User-Agent": PREDECESSOR_DOWNLOAD_USER_AGENT,
                },
                method="GET",
            )
            with opener.open(request, timeout=PREDECESSOR_DOWNLOAD_TIMEOUT_SECONDS) as response:
                require(response.getcode() == 200, f"predecessor anonymous GET status is not 200: {name}")
                require(response.geturl() == anonymous_url, f"predecessor anonymous GET URL drift: {name}")
                content_encoding = response.headers.get("Content-Encoding")
                require(
                    content_encoding in {None, "identity"},
                    f"predecessor anonymous GET content encoding is not identity: {name}",
                )
                content_length = response.headers.get("Content-Length")
                if content_length is not None:
                    require(
                        re.fullmatch(r"[0-9]+", content_length) is not None
                        and int(content_length) == expected_bytes,
                        f"predecessor anonymous GET Content-Length drift: {name}",
                    )
                data = response.read(expected_bytes + 1)
            require(len(data) == expected_bytes, f"predecessor anonymous byte count drift: {name}")
            require(sha256(data) == expected_sha256, f"predecessor anonymous SHA-256 drift: {name}")
            destination = temporary / name
            require(
                not destination.exists() and not destination.is_symlink(),
                f"predecessor hydration destination already exists: {name}",
            )
            with destination.open("xb") as stream:
                require(stream.write(data) == expected_bytes, f"short predecessor hydration write: {name}")

        validate_complete_predecessor_directory(temporary, predecessor_rows)
        require(
            not PREDECESSOR_DIR.exists() and not PREDECESSOR_DIR.is_symlink(),
            "refusing predecessor hydration rename because target now exists",
        )
        temporary.rename(PREDECESSOR_DIR)
        committed = True
        return {
            "status": "PASS_PREDECESSOR_HYDRATED",
            "version": PREDECESSOR_VERSION,
            "output": relative_display(PREDECESSOR_DIR),
            "files": 100,
            "bytes": EXPECTED_PREDECESSOR_TOTAL_BYTES,
            "inventory_aggregate_sha256": EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
            "source_receipt": {
                "path": relative_display(PREDECESSOR_RECEIPT),
                "bytes": EXPECTED_PREDECESSOR_RECEIPT[0],
                "sha256": EXPECTED_PREDECESSOR_RECEIPT[1],
            },
        }
    except BuildError:
        raise
    except (HTTPError, URLError, HTTPException, OSError) as exc:
        raise BuildError(f"predecessor hydration failed: {exc}") from exc
    finally:
        if not committed:
            remove_safe_hydration_temp(temporary)


def run_preflight(source_commit: str, source_tree: str) -> dict[str, Any]:
    retained, external, generated = prepare_inputs(source_commit, source_tree)
    with tempfile.TemporaryDirectory(prefix="pmi-v0.62.13-preflight-") as temporary:
        stage = Path(temporary)
        rows = stage_payload(stage, retained, external, generated)
        if OUTPUT_DIR.exists():
            compare_existing(stage, rows)
            return summary("PASS_EXISTING_BYTE_IDENTICAL", rows)
        return summary("PASS_PREFLIGHT_READY", rows)


def remove_safe_build_temp(path: Path) -> None:
    require(
        path.parent.resolve() == RELEASES_DIR.resolve()
        and path.name.startswith(".v0.62.13-build-")
        and path != OUTPUT_DIR,
        "unsafe temporary build cleanup path",
    )
    if path.exists():
        shutil.rmtree(path)


def run_build(source_commit: str, source_tree: str) -> dict[str, Any]:
    retained, external, generated = prepare_inputs(source_commit, source_tree)
    require(RELEASES_DIR.is_dir(), "releases directory missing")
    temporary = Path(tempfile.mkdtemp(prefix=".v0.62.13-build-", dir=RELEASES_DIR))
    committed = False
    try:
        rows = stage_payload(temporary, retained, external, generated)
        if OUTPUT_DIR.exists():
            compare_existing(temporary, rows)
            return summary("PASS_EXISTING_BYTE_IDENTICAL", rows)
        temporary.rename(OUTPUT_DIR)
        committed = True
        return summary("PASS_ASSEMBLED_NOT_PUBLISHED", rows)
    finally:
        if not committed:
            remove_safe_build_temp(temporary)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-commit",
        help="exact committed lowercase 40-character source commit archived into the release",
    )
    parser.add_argument(
        "--source-tree",
        help="exact lowercase 40-character tree required to match --source-commit",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--preflight",
        action="store_true",
        help="assemble and validate only inside a temporary directory; never publish",
    )
    modes.add_argument(
        "--build",
        action="store_true",
        help="atomically assemble releases/v0.62.13; accept an existing output only if byte-identical",
    )
    modes.add_argument(
        "--hydrate-predecessor",
        action="store_true",
        help="anonymously restore an absent releases/v0.62.12 from its pinned receipt; refuse overwrite",
    )
    args = parser.parse_args()
    if args.hydrate_predecessor:
        if args.source_commit is not None or args.source_tree is not None:
            parser.error("--hydrate-predecessor does not accept --source-commit or --source-tree")
    elif args.source_commit is None or args.source_tree is None:
        parser.error("--preflight and --build require both --source-commit and --source-tree")
    return args


def main() -> int:
    args = parse_args()
    try:
        if args.hydrate_predecessor:
            result = run_hydrate_predecessor()
        elif args.preflight:
            result = run_preflight(args.source_commit, args.source_tree)
        else:
            result = run_build(args.source_commit, args.source_tree)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0
    except BuildError as exc:
        print(
            json.dumps(
                {"status": "FAIL_CLOSED", "version": VERSION, "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
