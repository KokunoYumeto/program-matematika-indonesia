#!/usr/bin/env python3
"""Publish or anonymously verify PMI v0.62.16 at Zenodo lineage index 40.

This is a fail-closed successor overlay over the immutable v0.62.13 publisher.  It
retains that publisher's bounded draft transaction, race convergence, public
lineage search, metadata preservation, and every-file anonymous readback.  Its
predecessor authorities are deliberately split: the Zenodo lineage predecessor
is public v0.62.14 (record 22217240/index 39), while the GitHub release used for
local successor comparison is public v0.62.15.  The finalized v0.62.16 GitHub
authority is projected losslessly into exactly 100 Zenodo top-level files.

The overlay is constructed only after a fail-closed configuration gate.  Until
the deterministic local build and GitHub publication receipt have been frozen,
the script performs no dynamic template load, credential read, network request,
draft operation, publication, or receipt write.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import types
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = PROJECT / "scripts/publish-v06213-zenodo.py"
EXPECTED_TEMPLATE = (
    121_121,
    "036a0790f4ea7e26c619f0bc2b7899ff9d47cd509860f6e13a3ac676a33ff987",
)

VERSION = "0.62.16"
PREDECESSOR_VERSION = "0.62.14"
GITHUB_PREDECESSOR_VERSION = "0.62.15"
CONCEPT_ID = 22_059_707
PREDECESSOR_ID = 22_217_240
PREDECESSOR_INDEX = 39
SUCCESSOR_INDEX = 40
EXPECTED_PUBLIC_RECORDS_BEFORE = 40
EXPECTED_PUBLIC_RECORDS_AFTER = 41
EXPECTED_DRAFT_ID: int | None = None
EXPECTED_PREDECESSOR_GITHUB_FILES = 112
EXPECTED_PREDECESSOR_ZENODO_FILES = 100
EXPECTED_PREDECESSOR_FILES = EXPECTED_PREDECESSOR_ZENODO_FILES
EXPECTED_GITHUB_FILES: int | None = 112
EXPECTED_FILES = 100
EXPECTED_RETAINED: int | None = 93
EXPECTED_SAME_NAME_REPLACEMENTS: int | None = 4
EXPECTED_PURE_OMISSIONS = 3
EXPECTED_PURE_ADDITIONS = 3
EXPECTED_EFFECTIVE_OMISSIONS: int | None = 7
EXPECTED_EFFECTIVE_ADDITIONS: int | None = 7

EXPECTED_PREDECESSOR_RECEIPT = (
    58_227,
    "e34bdc951961bf6c18d4ffacfb80fc2fda411f02cba7de001c05ae6898229ad8",
)
EXPECTED_PREDECESSOR_AGGREGATE = (
    "322938b537d631023c484017caf3235775760d8e6620036dd0f3a832d964a29d"
)
EXPECTED_PREDECESSOR_TOTAL_BYTES = 744_312_466
EXPECTED_PREDECESSOR_GITHUB_RECEIPT = (
    88_060,
    "8a3883c811574864f0d40f029d1f48ca13870327feb0e9048cd3cad1d1abf390",
)
EXPECTED_PREDECESSOR_GITHUB_TOTAL_BYTES = 744_845_735
EXPECTED_PREDECESSOR_GITHUB_AGGREGATE = "4aa98d92ad3c84752d6914f24b568a46adb27994c75676d5b8a5b86400a5502f"
EXPECTED_PREDECESSOR_COMMIT = "809baf41177fc4f0fca3c5f696c36be152ec2c01"
EXPECTED_PREDECESSOR_TREE = "d72037b889eb01acb7abc85151ccb5f989c77155"

# This authority is intentionally distinct from the v0.62.14 GitHub receipt
# cross-bound into the Zenodo predecessor receipt above.  It is the public
# GitHub release from which the v0.62.16 flat-release delta is constructed.
EXPECTED_GITHUB_PREDECESSOR_RECEIPT = (
    94_750,
    "164b2941e2d1211c85768a3e235e0e94c37d6478478537a5bb8634c73958652a",
)
EXPECTED_GITHUB_PREDECESSOR_TOTAL_BYTES = 745_035_211
EXPECTED_GITHUB_PREDECESSOR_AGGREGATE = "62741d6fe384cd73b059c9d267b5703a9511f40ab6557bcfa5bd1aeaff808d5f"
EXPECTED_GITHUB_PREDECESSOR_COMMIT = "26562bf4427974bdeacc578028d0ef324012666d"
EXPECTED_GITHUB_PREDECESSOR_TREE = "6da0ccacd30d72d09e23cd13e54cca456319da8f"

GITHUB_CHECKSUM_NAME = "RELEASE_CHECKSUMS_v0.62.16.sha256"
CHECKSUM_NAME = "ZENODO_RELEASE_CHECKSUMS_v0.62.16.sha256"
SOURCE_ARCHIVE_NAME = "program-matematika-indonesia-source-v0.62.16.zip"
COURSE_CAPSULE_ARCHIVE_NAME = "program-matematika-indonesia-course-capsule-v1.zip"
ZENODO_BUNDLE_NAME = "program-matematika-indonesia-v0.62.16-zenodo-additions.zip"

SAME_NAME_REPLACEMENTS: set[str] = {
    "course-capsules-v1.jsonl",
    "learner-delivery-v1.json",
    "peta-belajar-luring.html",
    COURSE_CAPSULE_ARCHIVE_NAME,
}
PURE_OMISSIONS = {
    "ZENODO_RELEASE_CHECKSUMS_v0.62.14.sha256",
    "program-matematika-indonesia-source-v0.62.14.zip",
    "program-matematika-indonesia-v0.62.14-zenodo-additions.zip",
}
PURE_ADDITIONS = {
    CHECKSUM_NAME,
    SOURCE_ARCHIVE_NAME,
    ZENODO_BUNDLE_NAME,
}
OMITTED = SAME_NAME_REPLACEMENTS | PURE_OMISSIONS
ADDITIONS = SAME_NAME_REPLACEMENTS | PURE_ADDITIONS

BUNDLED_GITHUB_NAMES = frozenset(
    {
        GITHUB_CHECKSUM_NAME,
        "RELEASE_NOTES_v0.62.16.md",
        "comparison-evidence-manifest-v1.json",
        "comparison-evidence-manifest-v1.schema.json",
        "feature-adoption-provenance-v1.json",
        "feature-adoption-provenance-v1.schema.json",
        "modular-backend-pattern-index-v2.json",
        "modular-backend-pattern-index-v2.schema.json",
        "program-matematika-indonesia-c130-operations-research-v2.3.1.zip",
        "program-matematika-indonesia-judson-c30-c40-v2.3.1.zip",
        "program-matematika-indonesia-openlogic-c80-v2.3.1.zip",
        "v23-adapter-index-v2.json",
        "v23-adapter-index-v2.schema.json",
        "MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json",
    }
)

ADAPTER_BOUND_ROLES = ("A00", "B10", "C30", "C40", "C80", "C130", "D20", "D60", "D110")
NATIVE_ONLY_ROLE_COUNT = 31
EXPECTED_V2_SUMMARY = {
    "curriculum_roles": 40,
    "distinct_adapter_packages": 8,
    "families_without_local_adapter": 25,
    "families_without_public_replay_complete_adapter": 25,
    "package_deduplicated_canonical_records": 285_829,
    "pending_adapter_packages": 0,
    "pending_role_bindings": 0,
    "published_adapter_packages": 8,
    "published_role_bindings": 9,
    "represented_native_families": 8,
    "role_bindings": 9,
    "unbound_roles": 31,
}
EXPECTED_C130_PACKAGE_ID = "urn:uuid:a84539b5-455b-5baf-89a4-f4c0336e33ab"
EXPECTED_C130_ARCHIVE_SHA256 = "eb195d1aa555e9d5e639c1e35a08b6f4425be24cc93b7f1f633161e9cacee865"
EXPECTED_TERMINOLOGY_POLICY_SHA256 = "c3bc63376dfeac2427703cc53635c50418c1a5db93abe3074ad65aa760b1acaa"

UNRESOLVED = "__UNRESOLVED_V0_62_16__"
CONFIGURATION_FINALIZED = True
EXPECTED_GITHUB_TOTAL_BYTES: int | None = 745_034_611
EXPECTED_GITHUB_AGGREGATE_SHA256 = "4aff7541a77e76ea937b5f4588a621487cb21a68e007bd7008f911dcd4df50b2"
EXPECTED_SUCCESSOR_TOTAL_BYTES: int | None = 744_499_480
EXPECTED_SUCCESSOR_AGGREGATE_SHA256 = "dd4208d2806caf8f8651c23a7194e3895618dbc161cf3baf538245b9017c79aa"
EXPECTED_GITHUB_RECEIPT_IDENTITY: tuple[int | None, str] = (
    87_782,
    "1c5649a9b5fede9b808783d1c353c436ea2d9afedbe950b095933a7b81942c34",
)
EXPECTED_GITHUB_CHECKSUM_IDENTITY: tuple[int | None, str] = (
    12_461,
    "120adabada169d60a317a548a679ec9cc85877b195a72f78dfeaa76aee5ce8a6",
)
EXPECTED_CHECKSUM_IDENTITY: tuple[int | None, str] = (
    11_185,
    "8852a4a04964900e146d963f393e27c01cee353688d793e3ec63c919b21d865f",
)
EXPECTED_ZENODO_BUNDLE_IDENTITY: tuple[int | None, str] = (
    40_124_571,
    "1ad9c8101874f912033f2585d6530e6b7baec79fc79b5187b881d746d42c0d1c",
)
EXPECTED_ZENODO_BUNDLE_MEMBERS: int | None = 14
EXPECTED_SOURCE_ARCHIVE_IDENTITY: tuple[int | None, str] = (
    508_950_409,
    "4d1b758e4f06fab48bb8ecba63a0b85138dbec4345812d4fee8dea694a8155d0",
)
EXPECTED_SOURCE_ARCHIVE_MEMBERS: int | None = 3_140
EXPECTED_COURSE_CAPSULE_IDENTITY: tuple[int | None, str] = (
    82_165_750,
    "e0b85de2d8752b6a45edae58c364eec61107af1fd5fb453bc343448f1f00e46f",
)
EXPECTED_COURSE_CAPSULE_MEMBERS: int | None = 330
EXPECTED_GITHUB_COMMIT = "42a0656177376d5021a014f3e4d5ae6419d07ae5"
EXPECTED_GITHUB_TREE = "aa648184b56242f1a234c72d55e0d6d44a317b6c"


def _identity(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(8 * 1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def _valid_identity(value: tuple[int | None, str]) -> bool:
    return (
        type(value[0]) is int
        and value[0] >= 0
        and isinstance(value[1], str)
        and re.fullmatch(r"[0-9a-f]{64}", value[1]) is not None
    )


def validate_pinned_predecessor_and_source() -> None:
    if not (
        EXPECTED_GITHUB_PREDECESSOR_RECEIPT
        == (
            94_750,
            "164b2941e2d1211c85768a3e235e0e94c37d6478478537a5bb8634c73958652a",
        )
        and EXPECTED_GITHUB_PREDECESSOR_TOTAL_BYTES == 745_035_211
        and EXPECTED_GITHUB_PREDECESSOR_AGGREGATE
        == "62741d6fe384cd73b059c9d267b5703a9511f40ab6557bcfa5bd1aeaff808d5f"
        and EXPECTED_GITHUB_PREDECESSOR_COMMIT
        == "26562bf4427974bdeacc578028d0ef324012666d"
        and EXPECTED_GITHUB_PREDECESSOR_TREE
        == "6da0ccacd30d72d09e23cd13e54cca456319da8f"
    ):
        raise RuntimeError("public v0.62.15 GitHub comparison-predecessor authority differs")
    if (
        EXPECTED_GITHUB_COMMIT != "42a0656177376d5021a014f3e4d5ae6419d07ae5"
        or EXPECTED_GITHUB_TREE != "aa648184b56242f1a234c72d55e0d6d44a317b6c"
    ):
        raise RuntimeError("pinned v0.62.16 source commit/tree differs")


def validate_configuration() -> None:
    if CONFIGURATION_FINALIZED is not True:
        raise RuntimeError("set CONFIGURATION_FINALIZED only after freezing the final local build and GitHub receipt")
    if _identity(TEMPLATE_PATH) != EXPECTED_TEMPLATE:
        raise RuntimeError("v0.62.13 Zenodo publisher template identity differs")
    if (
        EXPECTED_PREDECESSOR_GITHUB_FILES != 112
        or EXPECTED_PREDECESSOR_ZENODO_FILES != 100
        or EXPECTED_PREDECESSOR_FILES != EXPECTED_PREDECESSOR_ZENODO_FILES
        or type(EXPECTED_GITHUB_FILES) is not int
        or EXPECTED_GITHUB_FILES < 99
        or EXPECTED_FILES != 100
    ):
        raise RuntimeError("split predecessor/successor authority counts differ")
    if EXPECTED_PUBLIC_RECORDS_BEFORE != 40 or EXPECTED_PUBLIC_RECORDS_AFTER != 41:
        raise RuntimeError("public lineage cardinality boundary differs")
    validate_pinned_predecessor_and_source()
    if EXPECTED_DRAFT_ID is not None:
        raise RuntimeError("draft ID must come only from the v0.62.16 reservation cursor")
    boundary_counts = (
        EXPECTED_RETAINED,
        EXPECTED_SAME_NAME_REPLACEMENTS,
        EXPECTED_EFFECTIVE_OMISSIONS,
        EXPECTED_EFFECTIVE_ADDITIONS,
    )
    if not all(type(value) is int and value >= 0 for value in boundary_counts):
        raise RuntimeError("successor boundary counts are unresolved")
    if not (
        len(SAME_NAME_REPLACEMENTS) == EXPECTED_SAME_NAME_REPLACEMENTS
        and len(PURE_OMISSIONS) == EXPECTED_PURE_OMISSIONS
        and len(PURE_ADDITIONS) == EXPECTED_PURE_ADDITIONS
        and len(OMITTED) == EXPECTED_EFFECTIVE_OMISSIONS
        and len(ADDITIONS) == EXPECTED_EFFECTIVE_ADDITIONS
    ):
        raise RuntimeError("release-boundary set cardinalities differ")
    if not (
        SAME_NAME_REPLACEMENTS.isdisjoint(PURE_OMISSIONS)
        and SAME_NAME_REPLACEMENTS.isdisjoint(PURE_ADDITIONS)
        and PURE_OMISSIONS.isdisjoint(PURE_ADDITIONS)
    ):
        raise RuntimeError("release-boundary sets overlap")
    if EXPECTED_RETAINED + EXPECTED_SAME_NAME_REPLACEMENTS + EXPECTED_PURE_OMISSIONS != EXPECTED_PREDECESSOR_FILES:
        raise RuntimeError("Zenodo predecessor equation differs")
    if EXPECTED_RETAINED + EXPECTED_SAME_NAME_REPLACEMENTS + EXPECTED_PURE_ADDITIONS != EXPECTED_FILES:
        raise RuntimeError("Zenodo successor equation differs")
    if (
        type(EXPECTED_ZENODO_BUNDLE_MEMBERS) is not int
        or len(BUNDLED_GITHUB_NAMES) != EXPECTED_ZENODO_BUNDLE_MEMBERS
        or EXPECTED_ZENODO_BUNDLE_MEMBERS != EXPECTED_GITHUB_FILES - 98
    ):
        raise RuntimeError("Zenodo bundle member boundary differs")
    if type(EXPECTED_GITHUB_TOTAL_BYTES) is not int or EXPECTED_GITHUB_TOTAL_BYTES <= 0:
        raise RuntimeError("GitHub successor total-byte identity is unresolved")
    if re.fullmatch(r"[0-9a-f]{64}", EXPECTED_GITHUB_AGGREGATE_SHA256) is None:
        raise RuntimeError("GitHub successor aggregate is unresolved")
    if type(EXPECTED_SUCCESSOR_TOTAL_BYTES) is not int or EXPECTED_SUCCESSOR_TOTAL_BYTES <= 0:
        raise RuntimeError("successor total-byte identity is unresolved")
    if re.fullmatch(r"[0-9a-f]{64}", EXPECTED_SUCCESSOR_AGGREGATE_SHA256) is None:
        raise RuntimeError("successor aggregate identity is unresolved")
    identities = {
        "github_receipt": EXPECTED_GITHUB_RECEIPT_IDENTITY,
        "github_checksum": EXPECTED_GITHUB_CHECKSUM_IDENTITY,
        "checksum": EXPECTED_CHECKSUM_IDENTITY,
        "zenodo_bundle": EXPECTED_ZENODO_BUNDLE_IDENTITY,
        "source_archive": EXPECTED_SOURCE_ARCHIVE_IDENTITY,
        "course_capsule": EXPECTED_COURSE_CAPSULE_IDENTITY,
    }
    for label, value in identities.items():
        if not _valid_identity(value):
            raise RuntimeError(f"{label} identity is unresolved")
    if type(EXPECTED_SOURCE_ARCHIVE_MEMBERS) is not int or EXPECTED_SOURCE_ARCHIVE_MEMBERS <= 0:
        raise RuntimeError("source archive member count is unresolved")
    if type(EXPECTED_COURSE_CAPSULE_MEMBERS) is not int or EXPECTED_COURSE_CAPSULE_MEMBERS <= 0:
        raise RuntimeError("course-capsule member count is unresolved")
    if not (
        len(ADAPTER_BOUND_ROLES) == 9
        and EXPECTED_V2_SUMMARY.get("published_adapter_packages") == 8
        and EXPECTED_V2_SUMMARY.get("published_role_bindings") == 9
        and EXPECTED_V2_SUMMARY.get("pending_adapter_packages") == 0
        and EXPECTED_V2_SUMMARY.get("pending_role_bindings") == 0
    ):
        raise RuntimeError("all-nine public-replay metadata boundary differs")
    serialized = json.dumps(
        {
            "aggregate": EXPECTED_SUCCESSOR_AGGREGATE_SHA256,
            "identities": identities,
        },
        sort_keys=True,
    )
    if UNRESOLVED in serialized or "TODO" in serialized or "REPLACE_ME" in serialized:
        raise RuntimeError("configuration contains an unresolved marker")


def offline_preflight() -> dict[str, Any]:
    """Check only static safety sentinels; never inspect artifacts or the network."""

    finalized = CONFIGURATION_FINALIZED is True
    validate_pinned_predecessor_and_source()
    if finalized:
        validate_configuration()
    else:
        if EXPECTED_GITHUB_FILES != 112 or EXPECTED_GITHUB_TOTAL_BYTES is not None:
            raise RuntimeError("unfinalized GitHub successor count/bytes sentinel differs")
        if EXPECTED_GITHUB_AGGREGATE_SHA256 != UNRESOLVED:
            raise RuntimeError("unfinalized GitHub aggregate sentinel differs")
        if EXPECTED_SUCCESSOR_TOTAL_BYTES is not None or EXPECTED_SUCCESSOR_AGGREGATE_SHA256 != UNRESOLVED:
            raise RuntimeError("unfinalized Zenodo successor identity sentinel differs")
        unresolved_identities = (
            EXPECTED_GITHUB_RECEIPT_IDENTITY,
            EXPECTED_GITHUB_CHECKSUM_IDENTITY,
            EXPECTED_CHECKSUM_IDENTITY,
            EXPECTED_ZENODO_BUNDLE_IDENTITY,
            EXPECTED_SOURCE_ARCHIVE_IDENTITY,
            EXPECTED_COURSE_CAPSULE_IDENTITY,
        )
        if any(value != (None, UNRESOLVED) for value in unresolved_identities):
            raise RuntimeError("unfinalized release/projection identity sentinel differs")
        if EXPECTED_SOURCE_ARCHIVE_MEMBERS is not None or EXPECTED_COURSE_CAPSULE_MEMBERS is not None:
            raise RuntimeError("unfinalized archive member-count sentinel differs")
        if EXPECTED_DRAFT_ID is not None:
            raise RuntimeError("unfinalized draft ID must be absent")
        if not (
            len(ADAPTER_BOUND_ROLES) == 9
            and EXPECTED_V2_SUMMARY.get("published_adapter_packages") == 8
            and EXPECTED_V2_SUMMARY.get("published_role_bindings") == 9
            and EXPECTED_V2_SUMMARY.get("pending_adapter_packages") == 0
            and EXPECTED_V2_SUMMARY.get("pending_role_bindings") == 0
        ):
            raise RuntimeError("all-nine public-replay metadata boundary differs")
    return {
        "status": (
            "PASS_OFFLINE_PREFLIGHT_CONFIGURATION_FINALIZED"
            if finalized
            else "PASS_OFFLINE_PREFLIGHT_WAITING_FOR_SUCCESSOR_ARTIFACTS"
        ),
        "version": VERSION,
        "configuration_finalized": finalized,
        "predecessor_github_files": EXPECTED_PREDECESSOR_GITHUB_FILES,
        "predecessor_zenodo_files": EXPECTED_PREDECESSOR_ZENODO_FILES,
        "predecessor_index": PREDECESSOR_INDEX,
        "successor_index": SUCCESSOR_INDEX,
        "public_records_before": EXPECTED_PUBLIC_RECORDS_BEFORE,
        "public_records_after": EXPECTED_PUBLIC_RECORDS_AFTER,
        "reservation_cursor": "ZENODO_RESERVATION_CURSOR_v0.62.16.json",
        "zenodo_predecessor": {
            "version": PREDECESSOR_VERSION,
            "record_id": PREDECESSOR_ID,
            "index": PREDECESSOR_INDEX,
        },
        "github_comparison_predecessor": {
            "version": GITHUB_PREDECESSOR_VERSION,
            "receipt_bytes": EXPECTED_GITHUB_PREDECESSOR_RECEIPT[0],
            "receipt_sha256": EXPECTED_GITHUB_PREDECESSOR_RECEIPT[1],
            "commit": EXPECTED_GITHUB_PREDECESSOR_COMMIT,
            "tree": EXPECTED_GITHUB_PREDECESSOR_TREE,
        },
        "pinned_source_commit": EXPECTED_GITHUB_COMMIT,
        "pinned_source_tree": EXPECTED_GITHUB_TREE,
        "adapter_public_replay": "complete_9_of_9_bindings",
        "remaining_freezes": [] if finalized else [
            "GITHUB_PUBLICATION_RECEIPT_v0.62.16.json byte count and SHA-256",
            "v0.62.16 GitHub release total bytes and inventory aggregate SHA-256",
            "v0.62.16 GitHub checksum, source archive, and course-capsule identities/member counts",
            "v0.62.16 Zenodo projection total bytes and inventory aggregate SHA-256",
            "v0.62.16 Zenodo checksum and deterministic additions-bundle identities",
            "v0.62.14-to-v0.62.16 retained/replaced/omitted/added boundary verification",
        ],
        "network_calls": 0,
        "credential_reads": 0,
        "artifact_reads": 0,
        "writes": 0,
    }


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"template transform {label} expected one match, observed {count}")
    return text.replace(old, new, 1)


def _replace_between(text: str, start: str, end: str, replacement: str, label: str) -> str:
    first = text.find(start)
    if first < 0:
        raise RuntimeError(f"template transform {label} start marker is absent")
    second = text.find(end, first)
    if second < 0:
        raise RuntimeError(f"template transform {label} end marker is absent")
    if text.find(start, first + 1) >= 0:
        raise RuntimeError(f"template transform {label} start marker is not unique")
    return text[:first] + replacement + text[second:]


def _python_set_literal(values: set[str] | frozenset[str]) -> str:
    if not values:
        return "set()"
    body = "\n".join(f"    {value!r}," for value in sorted(values))
    return "{\n" + body + "\n}"


def _transformed_source() -> str:
    data = TEMPLATE_PATH.read_bytes()
    if (len(data), hashlib.sha256(data).hexdigest()) != EXPECTED_TEMPLATE:
        raise RuntimeError("v0.62.13 Zenodo publisher template identity differs")
    text = data.decode("utf-8").replace("\r\n", "\n")

    # Shift the current/predecessor labels without allowing cascading replaces.
    text = text.replace("public-baseline-v0.62.12.json", "__PMI_PUBLIC_BASELINE_FILENAME__")
    text = text.replace("v0.62.13", "__PMI_CURRENT_DOTTED__")
    text = text.replace("v0.62.12", "__PMI_PREDECESSOR_DOTTED__")
    text = text.replace("__PMI_CURRENT_DOTTED__", "v0.62.16")
    text = text.replace("__PMI_PREDECESSOR_DOTTED__", "v0.62.14")
    text = text.replace("__PMI_PUBLIC_BASELINE_FILENAME__", "public-baseline-v0.62.12.json")
    text = text.replace('"0.62.13"', '"__PMI_CURRENT_VERSION__"')
    text = text.replace('"0.62.12"', '"__PMI_PREDECESSOR_VERSION__"')
    text = text.replace('"__PMI_CURRENT_VERSION__"', '"0.62.16"')
    text = text.replace('"__PMI_PREDECESSOR_VERSION__"', '"0.62.14"')
    text = text.replace("V06213", "V06216").replace("v06213", "v06216")
    text = text.replace("index-38", "index-40").replace("index 38", "index 40")
    text = text.replace("index-37", "index-39").replace("index 37", "index 39")
    text = _replace_once(
        text,
        'RELEASE_DIR = PROJECT / "releases/v0.62.16"',
        'RELEASE_DIR = PROJECT / "releases/v0.62.16-zenodo"',
        "Zenodo projection release directory",
    )
    text = _replace_once(
        text,
        'CHECKSUM_FILE = RELEASE_DIR / "RELEASE_CHECKSUMS_v0.62.16.sha256"',
        'CHECKSUM_FILE = RELEASE_DIR / "ZENODO_RELEASE_CHECKSUMS_v0.62.16.sha256"',
        "Zenodo projection checksum filename",
    )
    text = _replace_once(
        text,
        '"size": page_size,\n                "page": page,',
        '"size": page_size,\n                "page": page,\n                "sort": "oldest",',
        "stable public-lineage pagination",
    )

    text = _replace_once(text, "PREDECESSOR_ID = 22182000", "PREDECESSOR_ID = 22217240", "predecessor record")
    text = _replace_once(text, "PREDECESSOR_INDEX = 37", "PREDECESSOR_INDEX = 39", "predecessor index")
    text = _replace_once(text, "SUCCESSOR_INDEX = 38", "SUCCESSOR_INDEX = 40", "successor index")
    count_constants = (
        f"EXPECTED_PREDECESSOR_FILES = {EXPECTED_PREDECESSOR_FILES}\n"
        f"EXPECTED_GITHUB_FILES = {EXPECTED_GITHUB_FILES}\n"
        f"EXPECTED_FILES = {EXPECTED_FILES}\n"
        f"EXPECTED_RETAINED = {EXPECTED_RETAINED}\n"
        f"EXPECTED_SAME_NAME_REPLACEMENTS = {EXPECTED_SAME_NAME_REPLACEMENTS}\n"
        f"EXPECTED_PURE_OMISSIONS = {EXPECTED_PURE_OMISSIONS}\n"
        f"EXPECTED_PURE_ADDITIONS = {EXPECTED_PURE_ADDITIONS}"
    )
    text = _replace_once(
        text,
        "EXPECTED_FILES = 100\nEXPECTED_RETAINED = 78\nEXPECTED_SAME_NAME_REPLACEMENTS = 9\nEXPECTED_PURE_OMISSIONS = 13\nEXPECTED_PURE_ADDITIONS = 13",
        count_constants,
        "file-count constants",
    )
    text = _replace_once(
        text,
        'ADAPTER_BOUND_ROLES = ("A00", "B10", "D20", "D60", "D110")\nNATIVE_ONLY_ROLE_COUNT = 35',
        'ADAPTER_BOUND_ROLES = ("A00", "B10", "C30", "C40", "C80", "C130", "D20", "D60", "D110")\nNATIVE_ONLY_ROLE_COUNT = 31',
        "adapter role constants",
    )
    text = _replace_once(
        text,
        'EXPECTED_PREDECESSOR_RECEIPT = (\n    51_506,\n    "5867905ef9bd9c819cd5998d1f7758e023392249e3aad91106399bd8b479ac3a",\n)',
        'EXPECTED_PREDECESSOR_RECEIPT = (\n    58_227,\n    "e34bdc951961bf6c18d4ffacfb80fc2fda411f02cba7de001c05ae6898229ad8",\n)',
        "predecessor receipt identity",
    )
    text = _replace_once(
        text,
        'EXPECTED_PREDECESSOR_AGGREGATE = (\n    "3254b566c27819c2230ecf4ef2009879058e6bd41359b3926bd5e3fc36fd7c33"\n)',
        'EXPECTED_PREDECESSOR_AGGREGATE = (\n    "322938b537d631023c484017caf3235775760d8e6620036dd0f3a832d964a29d"\n)',
        "predecessor aggregate",
    )

    replacement_sets = (
        f"SAME_NAME_REPLACEMENTS = {_python_set_literal(SAME_NAME_REPLACEMENTS)}\n\n"
        f"PURE_OMISSIONS = {_python_set_literal(PURE_OMISSIONS)}\n\n"
        f"PURE_ADDITIONS = {_python_set_literal(PURE_ADDITIONS)}\n"
    )
    text = _replace_between(
        text,
        "SAME_NAME_REPLACEMENTS = {",
        "\n\nOMITTED = SAME_NAME_REPLACEMENTS | PURE_OMISSIONS",
        replacement_sets,
        "release-boundary sets",
    )

    # Only predecessor inventory operations use the predecessor count.  The
    # transformed publisher otherwise operates on the 100-file Zenodo
    # projection; the separate 112-file GitHub authority is checked below.
    predecessor_count_replacements = {
        'int(predecessor_zenodo.get("file_count", -1)) == EXPECTED_FILES': 'int(predecessor_zenodo.get("file_count", -1)) == EXPECTED_PREDECESSOR_FILES',
        'isinstance(predecessor_rows, list) and len(predecessor_rows) == EXPECTED_FILES': 'isinstance(predecessor_rows, list) and len(predecessor_rows) == EXPECTED_PREDECESSOR_FILES',
        'isinstance(receipt_rows, list) and len(receipt_rows) == EXPECTED_FILES': 'isinstance(receipt_rows, list) and len(receipt_rows) == EXPECTED_PREDECESSOR_FILES',
        'ORIGINAL_PUBLIC_FILE_STUBS(record, EXPECTED_FILES, "predecessor-stubs")': 'ORIGINAL_PUBLIC_FILE_STUBS(record, EXPECTED_PREDECESSOR_FILES, "predecessor-stubs")',
        'base.require(len(predecessor) == EXPECTED_FILES, "predecessor receipt inventory differs")': 'base.require(len(predecessor) == EXPECTED_PREDECESSOR_FILES, "predecessor receipt inventory differs")',
        'ORIGINAL_PUBLIC_FILE_STUBS(predecessor_record, EXPECTED_FILES, "predecessor-before-lineage")': 'ORIGINAL_PUBLIC_FILE_STUBS(predecessor_record, EXPECTED_PREDECESSOR_FILES, "predecessor-before-lineage")',
        'ORIGINAL_PUBLIC_FILE_STUBS(predecessor_after, EXPECTED_FILES, "predecessor-after-lineage")': 'ORIGINAL_PUBLIC_FILE_STUBS(predecessor_after, EXPECTED_PREDECESSOR_FILES, "predecessor-after-lineage")',
        '"predecessor_files": EXPECTED_FILES': '"predecessor_files": EXPECTED_PREDECESSOR_FILES',
    }
    for old, new in predecessor_count_replacements.items():
        text = _replace_once(text, old, new, f"predecessor count: {old[:32]}")

    text = _replace_once(
        text,
        '_require(readback.get("result") == "pass_100_of_100", "GitHub anonymous readback differs")',
        f'_require(readback.get("result") == "pass_{EXPECTED_GITHUB_FILES}_of_{EXPECTED_GITHUB_FILES}", "GitHub anonymous readback differs")',
        "GitHub successor readback label",
    )
    text = _replace_once(
        text,
        'f"<p>Batas bukti saat rilis adalah {len(ADAPTER_BOUND_ROLES)} adapter terverifikasi: {adapter_role_text}. "',
        'f"<p>Batas overlay penerus adalah {len(ADAPTER_BOUND_ROLES)} ikatan peran: {adapter_role_text}. Seluruh sembilan ikatan mempunyai replay publik lengkap pada snapshot ini. "',
        "metadata adapter-state boundary",
    )
    text = _replace_once(
        text,
        'f\'<p>Rilis GitHub yang identik tersedia pada <a href="{GITHUB_RELEASE}">GitHub v0.62.16</a>. Payload memuat \'',
        'f\'<p>Varian datar GitHub yang mempertahankan {EXPECTED_GITHUB_FILES} aset asli tersedia pada <a href="{GITHUB_RELEASE}">GitHub v0.62.16</a>. Proyeksi lossless Zenodo memuat \'',
        "metadata GitHub/Zenodo variant wording",
    )
    text = _replace_once(
        text,
        'f"adapter terverifikasi adalah {adapter_role_text}; {NATIVE_ONLY_ROLE_COUNT} peran tetap native-only, sedangkan "',
        'f"ikatan peran adapter adalah {adapter_role_text}; seluruh sembilan mempunyai replay publik lengkap. {NATIVE_ONLY_ROLE_COUNT} peran tetap native-only, sedangkan "',
        "metadata notes adapter-state boundary",
    )
    text = _replace_once(
        text,
        '"format sumber global.</p>"',
        '"format sumber global.</p>"\n        "<p>Paket kapsul juga memuat kebijakan terminologi berbasis konsep dan register. Kebijakan ini mempertahankan bukti native yang lama serta tidak mengklaim harmonisasi global tanpa bukti khusus per konsep dan bidang.</p>"\n        f"<p>GitHub menyediakan {EXPECTED_GITHUB_FILES} aset sebagai berkas datar. Karena batas keras Zenodo adalah 100 berkas per rekaman, proyeksi Zenodo mempertahankan 98 aset secara langsung dan {EXPECTED_ZENODO_BUNDLE_MEMBERS} aset asli byte demi byte di dalam satu bundel deterministik; tidak ada aset GitHub yang dibuang.</p>"',
        "metadata terminology-policy disclosure",
    )
    text = _replace_once(
        text,
        'result.append({"identifier": GITHUB_RELEASE, "relation": "isIdenticalTo", "scheme": "url"})',
        'result.append({"identifier": GITHUB_RELEASE, "relation": "isVariantFormOf", "scheme": "url"})',
        "GitHub relation is a lossless variant rather than flat-byte identity",
    )
    text = _replace_once(
        text,
        '"published_or_converged_single_index_38_draft"',
        '"published_or_converged_single_index_40_draft"',
        "successor execution-mode index",
    )
    text = _replace_once(
        text,
        '"v0.62.16_same_name_replacement"\n                if row["name"] in SAME_NAME_REPLACEMENTS\n                else "v0.62.16_pure_addition"\n                if row["name"] in PURE_ADDITIONS\n                else "retained_exact_from_v0.62.14"',
        '"v0.62.16_same_name_replacement"\n                if row["name"] in SAME_NAME_REPLACEMENTS\n                else "v0.62.16_pure_addition"\n                if row["name"] in PURE_ADDITIONS\n                else "retained_exact_from_v0.62.14"',
        "successor provenance labels",
    )
    return text


def _validate_v2_release(module: types.ModuleType, rows: list[dict[str, Any]], paths: dict[str, Path]) -> dict[str, Any]:
    row_by_name = {str(row["name"]): row for row in rows}
    required = {
        "v23-adapter-index-v2.json",
        "modular-backend-pattern-index-v2.json",
        "feature-adoption-provenance-v1.json",
        "comparison-evidence-manifest-v1.json",
        "MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json",
        GITHUB_CHECKSUM_NAME,
        SOURCE_ARCHIVE_NAME,
        COURSE_CAPSULE_ARCHIVE_NAME,
    }
    module.base.require(required <= set(paths), "v0.62.16 release assets are incomplete")
    total = sum(int(row["bytes"]) for row in rows)
    aggregate = module._inventory_sha(rows)
    module.base.require(len(rows) == EXPECTED_GITHUB_FILES, "GitHub release row count differs")
    module.base.require(total == EXPECTED_GITHUB_TOTAL_BYTES, "GitHub total-byte freeze differs")
    module.base.require(aggregate == EXPECTED_GITHUB_AGGREGATE_SHA256, "GitHub aggregate freeze differs")
    module.base.require(_identity(module.GITHUB_RECEIPT) == EXPECTED_GITHUB_RECEIPT_IDENTITY, "GitHub receipt identity freeze differs")
    module.base.require(
        _identity(paths[GITHUB_CHECKSUM_NAME]) == EXPECTED_GITHUB_CHECKSUM_IDENTITY,
        "GitHub checksum identity freeze differs",
    )
    module.base.require(_identity(paths[SOURCE_ARCHIVE_NAME]) == EXPECTED_SOURCE_ARCHIVE_IDENTITY, "source archive identity freeze differs")
    module.base.require(_identity(paths[COURSE_CAPSULE_ARCHIVE_NAME]) == EXPECTED_COURSE_CAPSULE_IDENTITY, "course-capsule identity freeze differs")

    index = module._load_json(paths["v23-adapter-index-v2.json"], "v2 adapter index")
    adapters = index.get("adapters")
    packages = index.get("packages")
    module.base.require(isinstance(adapters, list) and isinstance(packages, list), "v2 adapter arrays are missing")
    roles = tuple(str(row.get("role_id")) for row in adapters if isinstance(row, dict))
    module.base.require(roles == ADAPTER_BOUND_ROLES, "v2 adapter role order differs")
    module.base.require(index.get("summary") == EXPECTED_V2_SUMMARY, "v2 summary differs from C130 boundary")
    c130 = [row for row in packages if isinstance(row, dict) and row.get("package_id") == EXPECTED_C130_PACKAGE_ID]
    module.base.require(len(c130) == 1 and c130[0].get("canonical_records") == 51_704, "C130 package row differs")
    module.base.require(c130[0].get("archive", {}).get("sha256") == EXPECTED_C130_ARCHIVE_SHA256, "C130 archive binding differs")
    receipt = module._load_json(paths["MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json"], "v2 snapshot receipt")
    module.base.require(receipt.get("status") == "pass" and receipt.get("summary") == EXPECTED_V2_SUMMARY, "v2 snapshot receipt differs")

    with zipfile.ZipFile(paths[SOURCE_ARCHIVE_NAME], "r") as archive:
        module.base.require(len([item for item in archive.infolist() if not item.is_dir()]) == EXPECTED_SOURCE_ARCHIVE_MEMBERS, "source archive member-count freeze differs")
        github = module._load_json(module.GITHUB_RECEIPT, "GitHub receipt")
        commit = github.get("source", {}).get("commit")
        module.base.require(archive.comment == str(commit).encode("ascii"), "source archive comment differs from GitHub tag commit")
    with zipfile.ZipFile(paths[COURSE_CAPSULE_ARCHIVE_NAME], "r") as archive:
        names = [item.filename for item in archive.infolist() if not item.is_dir()]
        module.base.require(len(names) == EXPECTED_COURSE_CAPSULE_MEMBERS, "course-capsule member-count freeze differs")
        module.base.require(len(names) == len(set(names)), "course-capsule member names are not unique")
        required_members = {
            "backend/course-capsule-v1/authority/public-baseline-v0.62.12.json",
            "docs/data/course-capsule-v1/public-baseline-v0.62.12.json",
            "backend/course-capsule-v1/authority/v23-adapter-index-v2.json",
            "docs/data/v23-adapter-index-v2.json",
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
            "backend/course-capsule-v1/builds/program-matematika-indonesia-c130-operations-research-v2.3.1.zip",
        }
        module.base.require(required_members <= set(names), "course-capsule C130/v2 closure differs")
        module.base.require(
            archive.read("backend/course-capsule-v1/authority/public-baseline-v0.62.12.json")
            == archive.read("docs/data/course-capsule-v1/public-baseline-v0.62.12.json"),
            "course-capsule baseline mirrors differ",
        )
        terminology_pairs = (
            ("backend/course-capsule-v1/authority/terminology-policy-v1/README.md", "docs/data/course-capsule-v1/terminology-policy-v1/README.md"),
            ("backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json", "docs/data/course-capsule-v1/terminology-policy-v1/canonical-register-policy.json"),
            ("backend/course-capsule-v1/authority/terminology-policy-v1/checksums.sha256", "docs/data/course-capsule-v1/terminology-policy-v1/checksums.sha256"),
            ("schemas/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json", "docs/schema/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json"),
            ("schemas/course-capsule-v1/v2/terminology-concept-record-v1.schema.json", "docs/schema/course-capsule-v1/v2/terminology-concept-record-v1.schema.json"),
        )
        for authority, public in terminology_pairs:
            module.base.require(archive.read(authority) == archive.read(public), f"course-capsule terminology mirror differs: {authority}")
        module.base.require(
            hashlib.sha256(
                archive.read("backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json")
            ).hexdigest()
            == EXPECTED_TERMINOLOGY_POLICY_SHA256,
            "course-capsule terminology-policy identity differs",
        )
        module.base.require(
            hashlib.sha256(
                archive.read("backend/course-capsule-v1/builds/program-matematika-indonesia-c130-operations-research-v2.3.1.zip")
            ).hexdigest()
            == EXPECTED_C130_ARCHIVE_SHA256,
            "course-capsule embedded C130 package differs",
        )
    return {"adapter_role_order": list(roles), "summary": EXPECTED_V2_SUMMARY}


def _file_row(path: Path) -> dict[str, Any]:
    sha256 = hashlib.sha256()
    try:
        md5 = hashlib.md5(usedforsecurity=False)
    except TypeError:  # pragma: no cover - compatibility with older Python builds
        md5 = hashlib.md5()
    size = 0
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(8 * 1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            sha256.update(chunk)
            md5.update(chunk)
    return {
        "name": path.name,
        "bytes": size,
        "md5": md5.hexdigest(),
        "sha256": sha256.hexdigest(),
    }


def _flat_inventory(root: Path, expected: int, label: str) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    if not root.is_dir() or root.is_symlink():
        raise RuntimeError(f"{label} directory is missing or symlinked")
    entries = list(root.iterdir())
    if len(entries) != expected:
        raise RuntimeError(f"{label} is not exactly {expected} entries")
    if not all(path.is_file() and not path.is_symlink() for path in entries):
        raise RuntimeError(f"{label} is not a flat regular nonsymlink inventory")
    paths = {path.name: path for path in entries}
    if len(paths) != expected:
        raise RuntimeError(f"{label} filenames are not unique")
    rows = [_file_row(paths[name]) for name in sorted(paths)]
    return rows, paths


def _checksum_rows(path: Path) -> dict[str, str]:
    data = path.read_bytes()
    if b"\r" in data or not data.endswith(b"\n"):
        raise RuntimeError(f"checksum manifest is not canonical LF text: {path.name}")
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"checksum manifest is not UTF-8: {path.name}") from exc
    rows: dict[str, str] = {}
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)", line)
        if match is None:
            raise RuntimeError(f"checksum manifest row is malformed: {path.name}")
        digest, name = match.groups()
        if name in rows:
            raise RuntimeError(f"checksum manifest contains a duplicate name: {name}")
        rows[name] = digest
    if list(rows) != sorted(rows):
        raise RuntimeError(f"checksum manifest names are not sorted: {path.name}")
    return rows


def _install_projection_authority(module: types.ModuleType) -> dict[str, Any]:
    """Install split predecessor and lossless successor authorities."""

    state: dict[str, Any] = {}
    github_release_dir = PROJECT / "releases/v0.62.16"
    zenodo_release_dir = PROJECT / "releases/v0.62.16-zenodo"
    predecessor_github_receipt_path = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.14.json"
    github_comparison_predecessor_receipt_path = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.15.json"

    def exact_remote(remote: dict[str, Any], expected: dict[str, Any]) -> bool:
        return (
            int(remote.get("bytes", -1)) == int(expected["bytes"])
            and str(remote.get("md5", "")) == str(expected["md5"])
        )

    def cursor_draft_id() -> int:
        cursor = module._load_reservation_cursor()
        module.base.require(isinstance(cursor, dict), "v0.62.16 reservation cursor is absent")
        module.base.require(cursor.get("state") == "draft_discovered", "reservation cursor is not resumable")
        draft_id = cursor.get("draft_id")
        module.base.require(
            type(draft_id) is int and draft_id > 0 and draft_id != PREDECESSOR_ID,
            "reservation cursor draft ID differs",
        )
        return draft_id

    def custom_local_authority() -> tuple[Any, ...]:
        cached = state.get("result")
        if cached is not None:
            return cached

        base = module.base
        base.require(_identity(TEMPLATE_PATH) == EXPECTED_TEMPLATE, "v0.62.13 publisher template identity differs")
        base.require(
            _identity(module.PREDECESSOR_RECEIPT) == EXPECTED_PREDECESSOR_RECEIPT,
            "v0.62.14 Zenodo predecessor receipt identity differs",
        )
        base.require(
            _identity(predecessor_github_receipt_path) == EXPECTED_PREDECESSOR_GITHUB_RECEIPT,
            "v0.62.14 GitHub predecessor receipt identity differs",
        )
        base.require(
            _identity(github_comparison_predecessor_receipt_path)
            == EXPECTED_GITHUB_PREDECESSOR_RECEIPT,
            "v0.62.15 GitHub comparison-predecessor receipt identity differs",
        )
        base.require(
            _identity(module.GITHUB_RECEIPT) == EXPECTED_GITHUB_RECEIPT_IDENTITY,
            "GitHub v0.62.16 publication receipt identity differs",
        )

        github_comparison_predecessor = module._load_json(
            github_comparison_predecessor_receipt_path,
            "GitHub v0.62.15 comparison-predecessor receipt",
        )
        module._assert_sanitized_receipt(
            github_comparison_predecessor,
            "github_comparison_predecessor_receipt",
        )
        comparison_source = github_comparison_predecessor.get("source", {})
        comparison_readback = github_comparison_predecessor.get("anonymous_asset_readback", {})
        comparison_rows = comparison_readback.get("entries")
        comparison_summary = github_comparison_predecessor.get("inventory", {})
        base.require(
            github_comparison_predecessor.get("version") == GITHUB_PREDECESSOR_VERSION
            and github_comparison_predecessor.get("state") == "published_public_verified"
            and github_comparison_predecessor.get("tag") == "v0.62.15",
            "GitHub comparison-predecessor release state differs",
        )
        base.require(
            isinstance(comparison_source, dict)
            and comparison_source.get("commit") == EXPECTED_GITHUB_PREDECESSOR_COMMIT
            and comparison_source.get("tree") == EXPECTED_GITHUB_PREDECESSOR_TREE
            and comparison_source.get("tag_resolves_to_commit") is True,
            "GitHub comparison-predecessor commit/tree authority differs",
        )
        base.require(
            isinstance(comparison_readback, dict)
            and comparison_readback.get("result") == "pass_112_of_112"
            and isinstance(comparison_rows, list)
            and len(comparison_rows) == EXPECTED_PREDECESSOR_GITHUB_FILES,
            "GitHub comparison-predecessor anonymous inventory differs",
        )
        normalized_comparison_rows: list[dict[str, Any]] = []
        comparison_names: set[str] = set()
        for raw in comparison_rows:
            base.require(isinstance(raw, dict), "GitHub comparison-predecessor row is malformed")
            name = str(raw.get("name", ""))
            byte_count = raw.get("bytes")
            digest = str(raw.get("sha256", ""))
            base.require(
                bool(name)
                and name not in comparison_names
                and type(byte_count) is int
                and byte_count >= 0
                and re.fullmatch(r"[0-9a-f]{64}", digest) is not None
                and raw.get("anonymous_byte_identity") is True,
                f"GitHub comparison-predecessor byte authority differs: {name}",
            )
            comparison_names.add(name)
            normalized_comparison_rows.append(
                {"name": name, "bytes": byte_count, "sha256": digest}
            )
        base.require(
            isinstance(comparison_summary, dict)
            and int(comparison_summary.get("files", -1)) == EXPECTED_PREDECESSOR_GITHUB_FILES
            and int(comparison_summary.get("bytes", -1)) == EXPECTED_GITHUB_PREDECESSOR_TOTAL_BYTES
            and comparison_summary.get("aggregate_sha256") == EXPECTED_GITHUB_PREDECESSOR_AGGREGATE
            and sum(int(row["bytes"]) for row in normalized_comparison_rows)
            == EXPECTED_GITHUB_PREDECESSOR_TOTAL_BYTES
            and module._inventory_sha(normalized_comparison_rows)
            == EXPECTED_GITHUB_PREDECESSOR_AGGREGATE,
            "GitHub comparison-predecessor rows do not close their authority",
        )

        predecessor_github = module._load_json(
            predecessor_github_receipt_path, "GitHub v0.62.14 predecessor receipt"
        )
        module._assert_sanitized_receipt(predecessor_github, "predecessor_github_receipt")
        predecessor_github_source = predecessor_github.get("source", {})
        predecessor_github_readback = predecessor_github.get("anonymous_asset_readback", {})
        predecessor_github_rows = predecessor_github_readback.get("entries")
        predecessor_github_summary = predecessor_github.get("inventory", {})
        base.require(
            predecessor_github.get("version") == PREDECESSOR_VERSION
            and predecessor_github.get("state") == "published_public_verified"
            and predecessor_github.get("tag") == "v0.62.14",
            "GitHub predecessor release state differs",
        )
        base.require(
            isinstance(predecessor_github_source, dict)
            and predecessor_github_source.get("commit") == EXPECTED_PREDECESSOR_COMMIT
            and predecessor_github_source.get("tree") == EXPECTED_PREDECESSOR_TREE
            and predecessor_github_source.get("tag_resolves_to_commit") is True,
            "GitHub predecessor commit/tree authority differs",
        )
        base.require(
            isinstance(predecessor_github_readback, dict)
            and predecessor_github_readback.get("result") == "pass_112_of_112"
            and isinstance(predecessor_github_rows, list)
            and len(predecessor_github_rows) == EXPECTED_PREDECESSOR_GITHUB_FILES,
            "GitHub predecessor anonymous inventory differs",
        )
        base.require(
            isinstance(predecessor_github_summary, dict)
            and int(predecessor_github_summary.get("files", -1)) == EXPECTED_PREDECESSOR_GITHUB_FILES
            and int(predecessor_github_summary.get("bytes", -1)) == EXPECTED_PREDECESSOR_GITHUB_TOTAL_BYTES
            and predecessor_github_summary.get("aggregate_sha256") == EXPECTED_PREDECESSOR_GITHUB_AGGREGATE,
            "GitHub predecessor inventory summary differs",
        )
        predecessor_github_names: set[str] = set()
        normalized_predecessor_github_rows: list[dict[str, Any]] = []
        for raw in predecessor_github_rows:
            base.require(isinstance(raw, dict), "GitHub predecessor row is malformed")
            name = str(raw.get("name", ""))
            byte_count = raw.get("bytes")
            digest = str(raw.get("sha256", ""))
            base.require(
                bool(name)
                and name not in predecessor_github_names
                and type(byte_count) is int
                and byte_count >= 0
                and re.fullmatch(r"[0-9a-f]{64}", digest) is not None
                and raw.get("anonymous_byte_identity") is True,
                f"GitHub predecessor byte authority differs: {name}",
            )
            predecessor_github_names.add(name)
            normalized_predecessor_github_rows.append(
                {"name": name, "bytes": byte_count, "sha256": digest}
            )
        base.require(
            sum(int(row["bytes"]) for row in normalized_predecessor_github_rows)
            == EXPECTED_PREDECESSOR_GITHUB_TOTAL_BYTES
            and module._inventory_sha(normalized_predecessor_github_rows)
            == EXPECTED_PREDECESSOR_GITHUB_AGGREGATE,
            "GitHub predecessor rows do not close their authority",
        )

        github_rows, github_paths = _flat_inventory(
            github_release_dir, EXPECTED_GITHUB_FILES, "GitHub v0.62.16 local release"
        )
        github_local = {str(row["name"]): row for row in github_rows}
        base.require(
            sum(int(row["bytes"]) for row in github_rows) == EXPECTED_GITHUB_TOTAL_BYTES,
            "GitHub v0.62.16 local byte total differs",
        )
        base.require(
            module._inventory_sha(github_rows) == EXPECTED_GITHUB_AGGREGATE_SHA256,
            "GitHub v0.62.16 local aggregate differs",
        )
        github_checksums = _checksum_rows(github_paths[GITHUB_CHECKSUM_NAME])
        base.require(
            set(github_checksums) == set(github_paths) - {GITHUB_CHECKSUM_NAME},
            "GitHub checksum coverage differs from the finalized successor release",
        )
        for name, digest in github_checksums.items():
            base.require(github_local[name]["sha256"] == digest, f"GitHub checksum differs: {name}")

        github = module._load_json(module.GITHUB_RECEIPT, "GitHub v0.62.16 publication receipt")
        module._assert_sanitized_receipt(github, "github_receipt")
        base.require(github.get("state") == "published_public_verified", "GitHub release is not public verified")
        base.require(github.get("tag") == "v0.62.16", "GitHub release tag differs")
        source = github.get("source", {})
        base.require(
            isinstance(source, dict)
            and source.get("commit") == EXPECTED_GITHUB_COMMIT
            and source.get("tree") == EXPECTED_GITHUB_TREE
            and source.get("tag_resolves_to_commit") is True,
            "GitHub source commit/tree/tag authority differs",
        )
        base.require(
            github.get("release", {}).get("url")
            == "https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.16",
            "GitHub release URL differs",
        )
        readback = github.get("anonymous_asset_readback", {})
        base.require(
            isinstance(readback, dict)
            and readback.get("result") == f"pass_{EXPECTED_GITHUB_FILES}_of_{EXPECTED_GITHUB_FILES}",
            "GitHub anonymous readback differs",
        )
        github_remote_rows = readback.get("entries")
        base.require(
            isinstance(github_remote_rows, list) and len(github_remote_rows) == EXPECTED_GITHUB_FILES,
            "GitHub anonymous inventory count differs",
        )
        github_remote: dict[str, dict[str, Any]] = {}
        for row in github_remote_rows:
            base.require(isinstance(row, dict), "GitHub anonymous inventory row is malformed")
            name = str(row.get("name", ""))
            base.require(bool(name) and name not in github_remote, "GitHub anonymous names are not unique")
            github_remote[name] = row
        base.require(set(github_remote) == set(github_local), "GitHub anonymous/local names differ")
        for name, local in github_local.items():
            remote = github_remote[name]
            base.require(int(remote.get("bytes", -1)) == int(local["bytes"]), f"GitHub size differs: {name}")
            base.require(remote.get("sha256") == local["sha256"], f"GitHub SHA-256 differs: {name}")
        github_summary = github.get("inventory", {})
        base.require(
            isinstance(github_summary, dict)
            and int(github_summary.get("files", -1)) == EXPECTED_GITHUB_FILES
            and int(github_summary.get("bytes", -1)) == EXPECTED_GITHUB_TOTAL_BYTES
            and github_summary.get("aggregate_sha256") == EXPECTED_GITHUB_AGGREGATE_SHA256,
            "GitHub inventory summary differs",
        )

        zenodo_rows, zenodo_paths = _flat_inventory(
            zenodo_release_dir, EXPECTED_FILES, "Zenodo v0.62.16 projection"
        )
        zenodo_local = {str(row["name"]): row for row in zenodo_rows}
        base.require(
            sum(int(row["bytes"]) for row in zenodo_rows) == EXPECTED_SUCCESSOR_TOTAL_BYTES,
            "Zenodo projection byte total differs",
        )
        base.require(
            module._inventory_sha(zenodo_rows) == EXPECTED_SUCCESSOR_AGGREGATE_SHA256,
            "Zenodo projection aggregate differs",
        )
        base.require(
            _identity(zenodo_paths[CHECKSUM_NAME]) == EXPECTED_CHECKSUM_IDENTITY,
            "Zenodo projection checksum identity differs",
        )
        zenodo_checksums = _checksum_rows(zenodo_paths[CHECKSUM_NAME])
        base.require(
            set(zenodo_checksums) == set(zenodo_paths) - {CHECKSUM_NAME},
            "Zenodo checksum coverage differs from the 100-file projection",
        )
        for name, digest in zenodo_checksums.items():
            base.require(zenodo_local[name]["sha256"] == digest, f"Zenodo checksum differs: {name}")

        direct_names = set(github_local) - set(BUNDLED_GITHUB_NAMES)
        expected_projection_names = direct_names | {CHECKSUM_NAME, ZENODO_BUNDLE_NAME}
        base.require(len(direct_names) == 98, "Zenodo direct GitHub-asset count differs")
        base.require(
            set(zenodo_local) == expected_projection_names,
            "Zenodo projection is not exactly 98 direct GitHub assets plus checksum and bundle",
        )
        for name in direct_names:
            base.require(
                zenodo_local[name]["bytes"] == github_local[name]["bytes"]
                and zenodo_local[name]["sha256"] == github_local[name]["sha256"],
                f"Zenodo direct asset differs from GitHub: {name}",
            )

        bundle_path = zenodo_paths[ZENODO_BUNDLE_NAME]
        base.require(_identity(bundle_path) == EXPECTED_ZENODO_BUNDLE_IDENTITY, "Zenodo bundle identity differs")
        bundled_rows: dict[str, dict[str, Any]] = {}
        try:
            with zipfile.ZipFile(bundle_path, "r") as archive:
                infos = [info for info in archive.infolist() if not info.is_dir()]
                names = [info.filename for info in infos]
                base.require(
                    names == sorted(BUNDLED_GITHUB_NAMES) and len(names) == EXPECTED_ZENODO_BUNDLE_MEMBERS,
                    "Zenodo bundle member set/order differs",
                )
                base.require(archive.testzip() is None, "Zenodo bundle CRC validation failed")
                for info in infos:
                    pure = PurePosixPath(info.filename)
                    base.require(
                        not pure.is_absolute()
                        and ".." not in pure.parts
                        and pure.as_posix() == info.filename
                        and len(pure.parts) == 1,
                        f"Zenodo bundle member path is unsafe: {info.filename}",
                    )
                    digest = hashlib.sha256()
                    size = 0
                    with archive.open(info, "r") as stream:
                        while True:
                            chunk = stream.read(8 * 1024 * 1024)
                            if not chunk:
                                break
                            size += len(chunk)
                            digest.update(chunk)
                    expected = github_local[info.filename]
                    base.require(
                        size == int(expected["bytes"]) and digest.hexdigest() == expected["sha256"],
                        f"Zenodo bundle member differs from GitHub: {info.filename}",
                    )
                    bundled_rows[info.filename] = expected
        except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
            raise RuntimeError("Zenodo additions bundle could not be validated") from exc
        base.require(
            set(bundled_rows) == set(BUNDLED_GITHUB_NAMES),
            "Zenodo bundle does not preserve every omitted GitHub asset",
        )

        predecessor = module._load_json(module.PREDECESSOR_RECEIPT, "v0.62.14 predecessor receipt")
        module._assert_sanitized_receipt(predecessor, "predecessor_receipt")
        predecessor_zenodo = predecessor.get("zenodo", {})
        base.require(predecessor.get("version") == PREDECESSOR_VERSION, "predecessor receipt version differs")
        base.require(
            isinstance(predecessor_zenodo, dict)
            and int(predecessor_zenodo.get("record_id", -1)) == PREDECESSOR_ID
            and int(predecessor_zenodo.get("concept_record_id", -1)) == CONCEPT_ID
            and predecessor_zenodo.get("concept_doi") == f"10.5281/zenodo.{CONCEPT_ID}"
            and predecessor_zenodo.get("access_right") == "open"
            and int(predecessor_zenodo.get("file_count", -1)) == EXPECTED_PREDECESSOR_FILES,
            "predecessor Zenodo receipt boundary differs",
        )
        lineage = predecessor.get("lineage_verification", {})
        predecessor_github_authority = predecessor.get("github_authority", {})
        base.require(
            isinstance(lineage, dict)
            and int(lineage.get("successor_version_index", -1)) == PREDECESSOR_INDEX
            and int(lineage.get("concept_record_count_observed", -1)) == EXPECTED_PUBLIC_RECORDS_BEFORE
            and int(lineage.get("concept_latest_record_id", -1)) == PREDECESSOR_ID
            and lineage.get("target_is_current_latest") is True,
            "predecessor lineage index differs",
        )
        base.require(
            isinstance(predecessor_github_authority, dict)
            and predecessor_github_authority.get("receipt_sha256") == EXPECTED_PREDECESSOR_GITHUB_RECEIPT[1]
            and predecessor_github_authority.get("anonymous_readback") == "pass_112_of_112"
            and predecessor_github_authority.get("inventory_aggregate_sha256") == EXPECTED_PREDECESSOR_GITHUB_AGGREGATE
            and predecessor_github_authority.get("source_commit") == EXPECTED_PREDECESSOR_COMMIT
            and predecessor_github_authority.get("source_tree") == EXPECTED_PREDECESSOR_TREE,
            "predecessor GitHub/Zenodo authority cross-binding differs",
        )
        predecessor_rows = predecessor.get("payload_inventory")
        base.require(
            isinstance(predecessor_rows, list) and len(predecessor_rows) == EXPECTED_PREDECESSOR_FILES,
            "predecessor receipt inventory count differs",
        )
        predecessor_local: dict[str, dict[str, Any]] = {}
        for row in predecessor_rows:
            base.require(isinstance(row, dict), "predecessor receipt row is malformed")
            name = str(row.get("name", ""))
            base.require(bool(name) and name not in predecessor_local, "predecessor names are not unique")
            base.require(
                isinstance(row.get("bytes"), int)
                and int(row["bytes"]) >= 0
                and re.fullmatch(r"[0-9a-f]{32}", str(row.get("md5", ""))) is not None
                and re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256", ""))) is not None,
                f"predecessor identity is malformed: {name}",
            )
            predecessor_local[name] = row
        base.require(
            sum(int(row["bytes"]) for row in predecessor_rows) == EXPECTED_PREDECESSOR_TOTAL_BYTES,
            "predecessor byte total differs",
        )
        base.require(
            module._inventory_sha(predecessor_rows) == EXPECTED_PREDECESSOR_AGGREGATE
            and predecessor.get("payload_inventory_aggregate_sha256") == EXPECTED_PREDECESSOR_AGGREGATE,
            "predecessor aggregate differs",
        )

        predecessor_names = set(predecessor_local)
        local_names = set(zenodo_local)
        changed_same_name = {
            name
            for name in predecessor_names & local_names
            if int(predecessor_local[name]["bytes"]) != int(zenodo_local[name]["bytes"])
            or predecessor_local[name]["sha256"] != zenodo_local[name]["sha256"]
        }
        omitted = (predecessor_names - local_names) | changed_same_name
        additions = (local_names - predecessor_names) | changed_same_name
        retained = (predecessor_names & local_names) - changed_same_name
        base.require(changed_same_name == SAME_NAME_REPLACEMENTS, "Zenodo same-name replacement set differs")
        base.require(omitted == OMITTED and additions == ADDITIONS, "Zenodo predecessor/successor boundary differs")
        base.require(
            (
                len(retained),
                len(changed_same_name),
                len(predecessor_names - local_names),
                len(local_names - predecessor_names),
            )
            == (
                EXPECTED_RETAINED,
                EXPECTED_SAME_NAME_REPLACEMENTS,
                EXPECTED_PURE_OMISSIONS,
                EXPECTED_PURE_ADDITIONS,
            ),
            "Zenodo retained/replaced/omitted/added equation differs",
        )
        for name in retained:
            base.require(
                int(predecessor_local[name]["bytes"]) == int(zenodo_local[name]["bytes"])
                and predecessor_local[name]["sha256"] == zenodo_local[name]["sha256"],
                f"Zenodo retained file differs: {name}",
            )

        snapshot = module._course_snapshot(zenodo_paths[module.COURSE_CAPSULE_JSONL_NAME])
        package_closure = module._course_capsule_package_closure(
            zenodo_paths[COURSE_CAPSULE_ARCHIVE_NAME],
            zenodo_paths[module.COURSE_CAPSULE_JSONL_NAME],
            snapshot,
        )
        github_boundary = github.get("replacement_boundary", {})
        base.require(
            isinstance(github_boundary, dict)
            and module._same_canonical_json_value(github_boundary.get("course_snapshot"), snapshot),
            "GitHub receipt course snapshot differs from Zenodo projection",
        )
        v2 = _validate_v2_release(module, github_rows, github_paths)
        if isinstance(package_closure, dict):
            package_closure["v2_snapshot"] = v2
            package_closure["members"] = EXPECTED_COURSE_CAPSULE_MEMBERS
            package_closure["zenodo_projection"] = {
                "top_level_files": EXPECTED_FILES,
                "direct_github_assets": len(direct_names),
                "bundled_github_assets": len(bundled_rows),
                "original_github_assets_preserved": EXPECTED_GITHUB_FILES,
                "bundle": ZENODO_BUNDLE_NAME,
            }

        result = (zenodo_rows, zenodo_paths, github, predecessor, snapshot, package_closure)
        state.update(
            {
                "result": result,
                "local": zenodo_local,
                "local_rows": zenodo_rows,
                "predecessor": predecessor_local,
                "predecessor_rows": predecessor_rows,
                "bundled": bundled_rows,
                "github": github_local,
            }
        )
        return result

    def custom_validate_draft_boundary(
        draft: dict[str, Any],
        predecessor_rows: list[dict[str, Any]],
        local_rows: list[dict[str, Any]],
    ) -> None:
        if "result" not in state:
            custom_local_authority()
        base = module.base
        base.require(int(draft.get("id", -1)) == cursor_draft_id(), "draft ID is not the cursor-authorized successor draft")
        base.require(
            len(predecessor_rows) == EXPECTED_PREDECESSOR_FILES
            and module._inventory_sha(predecessor_rows) == EXPECTED_PREDECESSOR_AGGREGATE,
            "live predecessor rows differ from pinned authority",
        )
        base.require(
            len(local_rows) == EXPECTED_FILES
            and module._inventory_sha(local_rows) == EXPECTED_SUCCESSOR_AGGREGATE_SHA256,
            "live local rows differ from Zenodo projection authority",
        )
        remote_rows = module.base.draft_file_rows(draft)
        remote = {str(row["name"]): row for row in remote_rows}
        base.require(len(remote) == len(remote_rows) <= EXPECTED_FILES, "draft filenames are duplicate or exceed 100")
        allowed = set(state["local"]) | set(state["predecessor"]) | set(state["bundled"])
        base.require(set(remote) <= allowed, "draft contains a file outside exact predecessor/projection/bundle authority")
        for name, row in remote.items():
            matches_local = name in state["local"] and exact_remote(row, state["local"][name])
            matches_predecessor = name in state["predecessor"] and exact_remote(row, state["predecessor"][name])
            matches_bundled = name in state["bundled"] and exact_remote(row, state["bundled"][name])
            base.require(
                matches_local or matches_predecessor or matches_bundled,
                f"draft file matches no exact authorized byte identity: {name}",
            )

    def custom_delete_omissions(client: Any, draft_id: int) -> int:
        if "result" not in state:
            custom_local_authority()
        base = module.base
        base.require(draft_id == cursor_draft_id(), "cleanup target is not the cursor-authorized successor draft")
        state["client"] = client
        deleted = 0
        deleted_predecessor: list[str] = []
        deleted_staged_bundle: list[str] = []
        initial = base.get_draft(client, draft_id)
        custom_validate_draft_boundary(initial, state["predecessor_rows"], state["local_rows"])
        for name in sorted({str(row["name"]) for row in base.draft_file_rows(initial)}):
            draft = base.get_draft(client, draft_id)
            by_name = {str(row["name"]): row for row in base.draft_file_rows(draft)}
            if name not in by_name:
                continue
            remote = by_name[name]
            local_match = name in state["local"] and exact_remote(remote, state["local"][name])
            if local_match:
                continue
            predecessor_match = name in state["predecessor"] and exact_remote(remote, state["predecessor"][name])
            bundled_match = name in state["bundled"] and exact_remote(remote, state["bundled"][name])
            base.require(
                predecessor_match or bundled_match,
                f"obsolete draft file is not an exact predecessor or bundled-original byte identity: {name}",
            )
            absent = False
            for attempt in range(3):
                response = None
                try:
                    response = client.delete(
                        f"{base.DEPOSIT_API}/{draft_id}/files/{remote['id']}",
                        timeout=(20, 180),
                        allow_redirects=False,
                    )
                except base.requests.RequestException:
                    response = None
                if response is not None:
                    base.require(
                        response.status_code in (204, 404, 429, 500, 502, 503, 504),
                        f"Zenodo draft delete returned HTTP {response.status_code}",
                    )
                base.time.sleep(2 * (attempt + 1))
                refreshed = base.get_draft(client, draft_id)
                absent = name not in {str(row["name"]) for row in base.draft_file_rows(refreshed)}
                if absent:
                    break
            base.require(absent, f"obsolete draft file was not deleted: {name}")
            if predecessor_match:
                deleted_predecessor.append(name)
            else:
                deleted_staged_bundle.append(name)
            deleted += 1
        final = base.get_draft(client, draft_id)
        final_rows = base.draft_file_rows(final)
        final_by_name = {str(row["name"]): row for row in final_rows}
        base.require(
            all(
                name in state["local"] and exact_remote(row, state["local"][name])
                for name, row in final_by_name.items()
            ),
            "draft cleanup did not leave a strict exact subset of the final Zenodo projection",
        )
        state["deleted_predecessor_names"] = sorted(deleted_predecessor)
        state["deleted_staged_bundle_names"] = sorted(deleted_staged_bundle)
        return deleted

    def custom_verify_exact_draft(draft: dict[str, Any], local_rows: list[dict[str, Any]]) -> None:
        """Prove final draft bytes by authenticated SHA-256 before publication."""

        base = module.base
        authorized_draft_id = cursor_draft_id()
        base.require(int(draft.get("id", -1)) == authorized_draft_id, "final draft ID differs")
        remote_rows = base.draft_file_rows(draft)
        remote = {str(row["name"]): row for row in remote_rows}
        local = {str(row["name"]): row for row in local_rows}
        base.require(
            len(remote_rows) == EXPECTED_FILES and set(remote) == set(local),
            "final draft is not the exact 100-file Zenodo projection",
        )
        for name, expected in local.items():
            base.require(exact_remote(remote[name], expected), f"final draft size/MD5 differs: {name}")
        cache_key = tuple(
            (name, int(remote[name]["bytes"]), str(remote[name]["md5"])) for name in sorted(remote)
        )
        if state.get("prepublish_sha256_cache") == cache_key:
            return
        client = state.get("client")
        base.require(client is not None, "authenticated client is absent for prepublication SHA-256 readback")
        raw_files = draft.get("files", [])
        raw_by_name = {
            str(row.get("filename")): row for row in raw_files if isinstance(row, dict)
        }
        base.require(len(raw_by_name) == EXPECTED_FILES, "raw draft file inventory differs")
        prefix = f"https://zenodo.org/api/records/{authorized_draft_id}/draft/files/"
        for name in sorted(local):
            raw = raw_by_name[name]
            links = raw.get("links", {})
            url = links.get("download") if isinstance(links, dict) else None
            base.require(
                isinstance(url, str) and url.startswith(prefix) and url.endswith("/content"),
                f"draft content URL differs: {name}",
            )
            response = None
            try:
                response = client.get(
                    url,
                    stream=True,
                    timeout=(20, 1200),
                    allow_redirects=False,
                )
                base.require(response.status_code == 200, f"draft content readback returned HTTP {response.status_code}: {name}")
                digest = hashlib.sha256()
                size = 0
                for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
                    if chunk:
                        size += len(chunk)
                        digest.update(chunk)
                base.require(
                    size == int(local[name]["bytes"]) and digest.hexdigest() == local[name]["sha256"],
                    f"draft prepublication SHA-256 differs: {name}",
                )
            finally:
                if response is not None:
                    response.close()
        state["prepublish_sha256_cache"] = cache_key

    original_reserve_or_resume = module.reserve_or_resume

    def bounded_reserve_or_resume(client: Any) -> tuple[int, bool, str, int]:
        """Use the template's one-POST transaction and bind its result to the cursor."""

        state["client"] = client
        result = original_reserve_or_resume(client)
        draft_id, observed_201, route, requests_attempted = result
        module.base.require(
            requests_attempted in (0, 1),
            "new-version transaction count exceeds the bounded one-request policy",
        )
        module.base.require(
            draft_id == cursor_draft_id(),
            "reservation result is not immediately persisted in the v0.62.16 cursor",
        )
        module.base.require(
            not observed_201 or requests_attempted == 1,
            "HTTP 201 observation is inconsistent with the bounded transaction",
        )
        return draft_id, observed_201, route, requests_attempted

    module._local_authority = custom_local_authority
    module.reserve_or_resume = bounded_reserve_or_resume
    module.validate_draft_boundary = custom_validate_draft_boundary
    module.delete_omissions = custom_delete_omissions
    module.verify_exact_draft = custom_verify_exact_draft
    module.base.validate_draft_boundary = custom_validate_draft_boundary
    module.base.delete_omissions = custom_delete_omissions
    module.base.verify_exact_draft = custom_verify_exact_draft
    return state


def _load_successor_module() -> types.ModuleType:
    validate_configuration()
    source = _transformed_source()
    module = types.ModuleType("pmi_v06216_zenodo_successor")
    module.__file__ = str(Path(__file__).resolve())
    module.__name__ = "pmi_v06216_zenodo_successor"
    # The transformed metadata adds this successor-only constant; bind it
    # before executing the inherited publisher module.
    module.__dict__["EXPECTED_ZENODO_BUNDLE_MEMBERS"] = EXPECTED_ZENODO_BUNDLE_MEMBERS
    original_argv = sys.argv
    try:
        # The pinned v0.62.12 bootstrap has an historical preflight branch
        # that inspects process-wide argv without checking module identity.
        # Nested template loading must never consume the successor CLI.
        sys.argv = [original_argv[0]]
        exec(compile(source, str(Path(__file__).resolve()), "exec"), module.__dict__)
    finally:
        sys.argv = original_argv

    _install_projection_authority(module)

    original_preflight = module._standalone_preflight

    def enhanced_preflight() -> dict[str, Any]:
        validate_configuration()
        result = original_preflight()
        result["status"] = "PASS_LOCAL_PREFLIGHT_NO_NETWORK_NO_CREDENTIAL_NO_WRITE"
        result["predecessor_files"] = EXPECTED_PREDECESSOR_FILES
        result["successor_files"] = EXPECTED_FILES
        result["github_flat_files"] = EXPECTED_GITHUB_FILES
        result["zenodo_top_level_files"] = EXPECTED_FILES
        result["zenodo_direct_github_assets"] = EXPECTED_GITHUB_FILES - EXPECTED_ZENODO_BUNDLE_MEMBERS
        result["zenodo_bundled_github_assets"] = EXPECTED_ZENODO_BUNDLE_MEMBERS
        result["original_github_assets_preserved"] = EXPECTED_GITHUB_FILES
        return result

    original_publication_main = module.publication_main

    def enhanced_publication_main(token_file: Path | None = None) -> None:
        validate_configuration()
        original_publication_main(token_file)

    module._standalone_preflight = enhanced_preflight
    module.publication_main = enhanced_publication_main
    return module


def main() -> None:
    if sys.argv[1:] == ["--preflight"] and CONFIGURATION_FINALIZED is not True:
        print(json.dumps(offline_preflight(), sort_keys=True, separators=(",", ":")))
        return
    validate_configuration()
    module = _load_successor_module()
    module.main()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(f"FAIL: {type(exc).__name__}: {detail}", file=sys.stderr)
        raise SystemExit(1)
