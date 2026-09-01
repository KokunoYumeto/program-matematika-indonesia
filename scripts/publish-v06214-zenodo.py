#!/usr/bin/env python3
"""Publish or anonymously verify PMI v0.62.14 at Zenodo lineage index 39.

This is a pinned successor overlay over the immutable v0.62.13 publisher.  It
retains that publisher's bounded draft transaction, race convergence, public
lineage search, metadata preservation, and every-file anonymous readback.  The
GitHub authority has 112 flat assets; the lossless Zenodo projection has 100
top-level files and preserves the remaining 14 assets inside one deterministic
bundle because Zenodo records accept at most 100 files.

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

VERSION = "0.62.14"
PREDECESSOR_VERSION = "0.62.13"
CONCEPT_ID = 22_059_707
PREDECESSOR_ID = 22_207_081
PREDECESSOR_INDEX = 38
SUCCESSOR_INDEX = 39
EXPECTED_DRAFT_ID = 22_217_240
EXPECTED_PREDECESSOR_FILES = 100
EXPECTED_GITHUB_FILES = 112
EXPECTED_FILES = 100
EXPECTED_RETAINED = 91
EXPECTED_SAME_NAME_REPLACEMENTS = 6
EXPECTED_PURE_OMISSIONS = 3
EXPECTED_PURE_ADDITIONS = 3
EXPECTED_EFFECTIVE_OMISSIONS = 9
EXPECTED_EFFECTIVE_ADDITIONS = 9

EXPECTED_PREDECESSOR_RECEIPT = (
    59_438,
    "e6d59a7a13409afeab90034f1587d067a46106164fac079ec39903f1f899b4cf",
)
EXPECTED_PREDECESSOR_AGGREGATE = (
    "fa645e4b54973bc750ec6734a3195e22a0ade1d38cbf7f6497c4c1cbab4103ec"
)
EXPECTED_PREDECESSOR_TOTAL_BYTES = 460_869_686
EXPECTED_PREDECESSOR_COMMIT = "4ab6eb6b270dc0a32512dad3f998653c336d8492"
EXPECTED_PREDECESSOR_TREE = "268dae1dc622ecdd6290d64a0695388f8800d7a7"

GITHUB_CHECKSUM_NAME = "RELEASE_CHECKSUMS_v0.62.14.sha256"
CHECKSUM_NAME = "ZENODO_RELEASE_CHECKSUMS_v0.62.14.sha256"
SOURCE_ARCHIVE_NAME = "program-matematika-indonesia-source-v0.62.14.zip"
COURSE_CAPSULE_ARCHIVE_NAME = "program-matematika-indonesia-course-capsule-v1.zip"
ZENODO_BUNDLE_NAME = "program-matematika-indonesia-v0.62.14-zenodo-additions.zip"

SAME_NAME_REPLACEMENTS = {
    "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md",
    "course-capsule-v1.schema.json",
    "course-capsules-v1.jsonl",
    "learner-delivery-v1.json",
    "peta-belajar-luring.html",
    COURSE_CAPSULE_ARCHIVE_NAME,
}
PURE_OMISSIONS = {
    "RELEASE_CHECKSUMS_v0.62.13.sha256",
    "RELEASE_NOTES_v0.62.13.md",
    "program-matematika-indonesia-source-v0.62.13.zip",
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
        "RELEASE_NOTES_v0.62.14.md",
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
EXPECTED_C130_ARCHIVE_SHA256 = "eb195d1aa555e9d5e639c1e35a08b6f4425be24cc93b7f1f633161e9cacee865"
EXPECTED_TERMINOLOGY_POLICY_SHA256 = "c3bc63376dfeac2427703cc53635c50418c1a5db93abe3074ad65aa760b1acaa"

UNRESOLVED = "__UNRESOLVED_V0_62_14__"
CONFIGURATION_FINALIZED = True
EXPECTED_GITHUB_TOTAL_BYTES = 744_845_735
EXPECTED_GITHUB_AGGREGATE_SHA256 = "4aa98d92ad3c84752d6914f24b568a46adb27994c75676d5b8a5b86400a5502f"
EXPECTED_SUCCESSOR_TOTAL_BYTES: int | None = 744_312_466
EXPECTED_SUCCESSOR_AGGREGATE_SHA256 = "322938b537d631023c484017caf3235775760d8e6620036dd0f3a832d964a29d"
EXPECTED_GITHUB_RECEIPT_IDENTITY: tuple[int | None, str] = (
    88_060,
    "8a3883c811574864f0d40f029d1f48ca13870327feb0e9048cd3cad1d1abf390",
)
EXPECTED_GITHUB_CHECKSUM_IDENTITY: tuple[int | None, str] = (
    12_461,
    "700fa9d95d9834b033a009ff333211ccfab7014f417fe5b29922348e489253e5",
)
EXPECTED_CHECKSUM_IDENTITY: tuple[int | None, str] = (
    11_185,
    "dc506dd9cdf1a8534bb2ccc8282395c9c811ff13a802cb0fb8b33f33244a7588",
)
EXPECTED_ZENODO_BUNDLE_IDENTITY: tuple[int | None, str] = (
    40_123_811,
    "740ed8c4298c06f177c85c1777e976f3348ffa1dd83e7d2dffd28aa9268db1fe",
)
EXPECTED_ZENODO_BUNDLE_MEMBERS = 14
EXPECTED_SOURCE_ARCHIVE_IDENTITY: tuple[int | None, str] = (
    508_814_546,
    "359ff1c1973f37fcb68737b2a43151aea39d43cf3b7886a83bd429fbaa89195f",
)
EXPECTED_SOURCE_ARCHIVE_MEMBERS: int | None = 3_131
EXPECTED_COURSE_CAPSULE_IDENTITY: tuple[int | None, str] = (
    82_118_296,
    "28aa806ba060bdd16869f3c2e2fdcfc2b41fa0f53d96cee02fdec218f390012a",
)
EXPECTED_COURSE_CAPSULE_MEMBERS: int | None = 326
EXPECTED_GITHUB_COMMIT = "809baf41177fc4f0fca3c5f696c36be152ec2c01"
EXPECTED_GITHUB_TREE = "d72037b889eb01acb7abc85151ccb5f989c77155"


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


def validate_configuration() -> None:
    if CONFIGURATION_FINALIZED is not True:
        raise RuntimeError("set CONFIGURATION_FINALIZED only after freezing the final local build and GitHub receipt")
    if _identity(TEMPLATE_PATH) != EXPECTED_TEMPLATE:
        raise RuntimeError("v0.62.13 Zenodo publisher template identity differs")
    if EXPECTED_PREDECESSOR_FILES != 100 or EXPECTED_GITHUB_FILES != 112 or EXPECTED_FILES != 100:
        raise RuntimeError("predecessor/GitHub/Zenodo file counts differ")
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
        raise RuntimeError("91+6+3 predecessor equation differs")
    if EXPECTED_RETAINED + EXPECTED_SAME_NAME_REPLACEMENTS + EXPECTED_PURE_ADDITIONS != EXPECTED_FILES:
        raise RuntimeError("91+6+3 Zenodo successor equation differs")
    if len(BUNDLED_GITHUB_NAMES) != EXPECTED_ZENODO_BUNDLE_MEMBERS:
        raise RuntimeError("Zenodo bundle member boundary differs")
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
    serialized = json.dumps(
        {
            "aggregate": EXPECTED_SUCCESSOR_AGGREGATE_SHA256,
            "identities": identities,
        },
        sort_keys=True,
    )
    if UNRESOLVED in serialized or "TODO" in serialized or "REPLACE_ME" in serialized:
        raise RuntimeError("configuration contains an unresolved marker")


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


def _transformed_source() -> str:
    data = TEMPLATE_PATH.read_bytes()
    if (len(data), hashlib.sha256(data).hexdigest()) != EXPECTED_TEMPLATE:
        raise RuntimeError("v0.62.13 Zenodo publisher template identity differs")
    text = data.decode("utf-8").replace("\r\n", "\n")

    # Shift the current/predecessor labels without allowing cascading replaces.
    text = text.replace("public-baseline-v0.62.12.json", "__PMI_PUBLIC_BASELINE_FILENAME__")
    text = text.replace("v0.62.13", "__PMI_CURRENT_DOTTED__")
    text = text.replace("v0.62.12", "__PMI_PREDECESSOR_DOTTED__")
    text = text.replace("__PMI_CURRENT_DOTTED__", "v0.62.14")
    text = text.replace("__PMI_PREDECESSOR_DOTTED__", "v0.62.13")
    text = text.replace("__PMI_PUBLIC_BASELINE_FILENAME__", "public-baseline-v0.62.12.json")
    text = text.replace('"0.62.13"', '"__PMI_CURRENT_VERSION__"')
    text = text.replace('"0.62.12"', '"__PMI_PREDECESSOR_VERSION__"')
    text = text.replace('"__PMI_CURRENT_VERSION__"', '"0.62.14"')
    text = text.replace('"__PMI_PREDECESSOR_VERSION__"', '"0.62.13"')
    text = text.replace("V06213", "V06214").replace("v06213", "v06214")
    text = text.replace("index-38", "index-39").replace("index 38", "index 39")
    text = text.replace("index-37", "index-38").replace("index 37", "index 38")
    text = _replace_once(
        text,
        'RELEASE_DIR = PROJECT / "releases/v0.62.14"',
        'RELEASE_DIR = PROJECT / "releases/v0.62.14-zenodo"',
        "Zenodo projection release directory",
    )
    text = _replace_once(
        text,
        'CHECKSUM_FILE = RELEASE_DIR / "RELEASE_CHECKSUMS_v0.62.14.sha256"',
        'CHECKSUM_FILE = RELEASE_DIR / "ZENODO_RELEASE_CHECKSUMS_v0.62.14.sha256"',
        "Zenodo projection checksum filename",
    )
    text = _replace_once(
        text,
        '"size": page_size,\n                "page": page,',
        '"size": page_size,\n                "page": page,\n                "sort": "oldest",',
        "stable public-lineage pagination",
    )

    text = _replace_once(text, "PREDECESSOR_ID = 22182000", "PREDECESSOR_ID = 22207081", "predecessor record")
    text = _replace_once(text, "PREDECESSOR_INDEX = 37", "PREDECESSOR_INDEX = 38", "predecessor index")
    text = _replace_once(text, "SUCCESSOR_INDEX = 38", "SUCCESSOR_INDEX = 39", "successor index")
    text = _replace_once(
        text,
        "EXPECTED_FILES = 100\nEXPECTED_RETAINED = 78\nEXPECTED_SAME_NAME_REPLACEMENTS = 9\nEXPECTED_PURE_OMISSIONS = 13\nEXPECTED_PURE_ADDITIONS = 13",
        "EXPECTED_PREDECESSOR_FILES = 100\nEXPECTED_GITHUB_FILES = 112\nEXPECTED_FILES = 100\nEXPECTED_RETAINED = 91\nEXPECTED_SAME_NAME_REPLACEMENTS = 6\nEXPECTED_PURE_OMISSIONS = 3\nEXPECTED_PURE_ADDITIONS = 3",
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
        'EXPECTED_PREDECESSOR_RECEIPT = (\n    59_438,\n    "e6d59a7a13409afeab90034f1587d067a46106164fac079ec39903f1f899b4cf",\n)',
        "predecessor receipt identity",
    )
    text = _replace_once(
        text,
        'EXPECTED_PREDECESSOR_AGGREGATE = (\n    "3254b566c27819c2230ecf4ef2009879058e6bd41359b3926bd5e3fc36fd7c33"\n)',
        'EXPECTED_PREDECESSOR_AGGREGATE = (\n    "fa645e4b54973bc750ec6734a3195e22a0ade1d38cbf7f6497c4c1cbab4103ec"\n)',
        "predecessor aggregate",
    )

    replacement_sets = '''SAME_NAME_REPLACEMENTS = {
    "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md",
    "course-capsule-v1.schema.json",
    "course-capsules-v1.jsonl",
    "learner-delivery-v1.json",
    "peta-belajar-luring.html",
    "program-matematika-indonesia-course-capsule-v1.zip",
}

PURE_OMISSIONS = {
    "RELEASE_CHECKSUMS_v0.62.13.sha256",
    "RELEASE_NOTES_v0.62.13.md",
    "program-matematika-indonesia-source-v0.62.13.zip",
}

PURE_ADDITIONS = {
    "ZENODO_RELEASE_CHECKSUMS_v0.62.14.sha256",
    "program-matematika-indonesia-source-v0.62.14.zip",
    "program-matematika-indonesia-v0.62.14-zenodo-additions.zip",
}
'''
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
        '_require(readback.get("result") == "pass_112_of_112", "GitHub anonymous readback differs")',
        "GitHub successor readback label",
    )
    text = _replace_once(
        text,
        'f"<p>Batas bukti saat rilis adalah {len(ADAPTER_BOUND_ROLES)} adapter terverifikasi: {adapter_role_text}. "',
        'f"<p>Batas overlay penerus adalah {len(ADAPTER_BOUND_ROLES)} ikatan peran: {adapter_role_text}. Lima ikatan sudah mempunyai replay publik lengkap dan empat ikatan C30, C40, C80, dan C130 menunggu publikasi pusat sampai rilis ini selesai. "',
        "metadata adapter-state boundary",
    )
    text = _replace_once(
        text,
        'f\'<p>Rilis GitHub yang identik tersedia pada <a href="{GITHUB_RELEASE}">GitHub v0.62.14</a>. Payload memuat \'',
        'f\'<p>Varian datar GitHub yang mempertahankan 112 aset asli tersedia pada <a href="{GITHUB_RELEASE}">GitHub v0.62.14</a>. Proyeksi lossless Zenodo memuat \'',
        "metadata GitHub/Zenodo variant wording",
    )
    text = _replace_once(
        text,
        'f"adapter terverifikasi adalah {adapter_role_text}; {NATIVE_ONLY_ROLE_COUNT} peran tetap native-only, sedangkan "',
        'f"ikatan peran adapter adalah {adapter_role_text}; lima mempunyai replay publik lengkap dan empat menunggu publikasi pusat. {NATIVE_ONLY_ROLE_COUNT} peran tetap native-only, sedangkan "',
        "metadata notes adapter-state boundary",
    )
    text = _replace_once(
        text,
        '"format sumber global.</p>"',
        '"format sumber global.</p>"\n        "<p>Paket kapsul juga memuat kebijakan terminologi berbasis konsep dan register. Kebijakan ini mempertahankan bukti native yang lama serta tidak mengklaim harmonisasi global tanpa bukti khusus per konsep dan bidang.</p>"\n        "<p>GitHub menyediakan 112 aset sebagai berkas datar. Karena batas keras Zenodo adalah 100 berkas per rekaman, proyeksi Zenodo mempertahankan 98 aset secara langsung dan 14 aset asli byte demi byte di dalam satu bundel deterministik; tidak ada aset GitHub yang dibuang.</p>"',
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
        '"published_or_converged_single_index_39_draft"',
        "successor execution-mode index",
    )
    text = _replace_once(
        text,
        '"v0.62.14_same_name_replacement"\n                if row["name"] in SAME_NAME_REPLACEMENTS\n                else "v0.62.14_pure_addition"\n                if row["name"] in PURE_ADDITIONS\n                else "retained_exact_from_v0.62.13"',
        '"v0.62.14_same_name_replacement"\n                if row["name"] in SAME_NAME_REPLACEMENTS\n                else "v0.62.14_pure_addition"\n                if row["name"] in PURE_ADDITIONS\n                else "retained_exact_from_v0.62.13"',
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
    module.base.require(required <= set(paths), "v0.62.14 C130/v2 release assets are incomplete")
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
    """Install a lossless 112-GitHub/100-Zenodo authority boundary."""

    state: dict[str, Any] = {}
    github_release_dir = PROJECT / "releases/v0.62.14"
    zenodo_release_dir = PROJECT / "releases/v0.62.14-zenodo"

    def exact_remote(remote: dict[str, Any], expected: dict[str, Any]) -> bool:
        return (
            int(remote.get("bytes", -1)) == int(expected["bytes"])
            and str(remote.get("md5", "")) == str(expected["md5"])
        )

    def custom_local_authority() -> tuple[Any, ...]:
        cached = state.get("result")
        if cached is not None:
            return cached

        base = module.base
        base.require(_identity(TEMPLATE_PATH) == EXPECTED_TEMPLATE, "v0.62.13 publisher template identity differs")
        base.require(
            _identity(module.PREDECESSOR_RECEIPT) == EXPECTED_PREDECESSOR_RECEIPT,
            "v0.62.13 predecessor receipt identity differs",
        )
        base.require(
            _identity(module.GITHUB_RECEIPT) == EXPECTED_GITHUB_RECEIPT_IDENTITY,
            "GitHub v0.62.14 publication receipt identity differs",
        )

        github_rows, github_paths = _flat_inventory(
            github_release_dir, EXPECTED_GITHUB_FILES, "GitHub v0.62.14 local release"
        )
        github_local = {str(row["name"]): row for row in github_rows}
        base.require(
            sum(int(row["bytes"]) for row in github_rows) == EXPECTED_GITHUB_TOTAL_BYTES,
            "GitHub v0.62.14 local byte total differs",
        )
        base.require(
            module._inventory_sha(github_rows) == EXPECTED_GITHUB_AGGREGATE_SHA256,
            "GitHub v0.62.14 local aggregate differs",
        )
        github_checksums = _checksum_rows(github_paths[GITHUB_CHECKSUM_NAME])
        base.require(
            set(github_checksums) == set(github_paths) - {GITHUB_CHECKSUM_NAME},
            "GitHub checksum coverage differs from the 112-file release",
        )
        for name, digest in github_checksums.items():
            base.require(github_local[name]["sha256"] == digest, f"GitHub checksum differs: {name}")

        github = module._load_json(module.GITHUB_RECEIPT, "GitHub v0.62.14 publication receipt")
        module._assert_sanitized_receipt(github, "github_receipt")
        base.require(github.get("state") == "published_public_verified", "GitHub release is not public verified")
        base.require(github.get("tag") == "v0.62.14", "GitHub release tag differs")
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
            == "https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.14",
            "GitHub release URL differs",
        )
        readback = github.get("anonymous_asset_readback", {})
        base.require(
            isinstance(readback, dict) and readback.get("result") == "pass_112_of_112",
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
            zenodo_release_dir, EXPECTED_FILES, "Zenodo v0.62.14 projection"
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
            "Zenodo bundle does not preserve all 14 omitted GitHub assets",
        )

        predecessor = module._load_json(module.PREDECESSOR_RECEIPT, "v0.62.13 predecessor receipt")
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
        base.require(
            isinstance(lineage, dict) and int(lineage.get("successor_version_index", -1)) == PREDECESSOR_INDEX,
            "predecessor lineage index differs",
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
            "Zenodo 91-retained/6-replaced/3-omitted/3-added equation differs",
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
        base.require(int(draft.get("id", -1)) == EXPECTED_DRAFT_ID, "draft ID is not the pinned successor draft")
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
        base.require(draft_id == EXPECTED_DRAFT_ID, "cleanup target is not the pinned successor draft")
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

    def pinned_reserve_or_resume(client: Any) -> tuple[int, bool, str, int]:
        """Resume only the already-authorized index-39 draft; never POST a version."""

        base = module.base
        public_state = module.anonymous_lineage_search()
        base.require(public_state["target"] is None, "public v0.62.14 appeared before pinned resume")
        latest = public_state["latest"]
        base.require(int(latest.get("id", -1)) == PREDECESSOR_ID, "concept latest changed before pinned resume")
        latest_metadata = latest.get("metadata", {})
        base.require(latest_metadata.get("version") == PREDECESSOR_VERSION, "latest predecessor version differs")
        relation = base.version_relation(latest_metadata)
        base.require(
            int(relation["index"]) == PREDECESSOR_INDEX and relation["is_last"] is True,
            "exact index-38 predecessor is not latest",
        )
        cursor = module._load_reservation_cursor()
        base.require(isinstance(cursor, dict), "pinned successor cursor is absent")
        base.require(cursor.get("state") == "draft_discovered", "pinned successor cursor state differs")
        base.require(int(cursor.get("draft_id", -1)) == EXPECTED_DRAFT_ID, "cursor draft ID differs")
        predecessor = base.authenticated_predecessor(client)
        predecessor_latest = int(base.latest_draft_id(predecessor))
        base.require(
            predecessor_latest in (PREDECESSOR_ID, EXPECTED_DRAFT_ID),
            "authenticated predecessor points to a conflicting draft",
        )
        discovered = module._discover_single_existing_successor_draft(client)
        base.require(
            discovered == EXPECTED_DRAFT_ID,
            "authenticated draft inventory does not resolve to the pinned draft ID",
        )
        draft = base.get_draft(client, EXPECTED_DRAFT_ID)
        module._draft_index(draft, client=client, draft_id=EXPECTED_DRAFT_ID)
        state["client"] = client
        module._write_reservation_cursor("draft_discovered", draft_id=EXPECTED_DRAFT_ID)
        return EXPECTED_DRAFT_ID, False, "resumed_pinned_existing_draft_22217240", 0

    def custom_verify_exact_draft(draft: dict[str, Any], local_rows: list[dict[str, Any]]) -> None:
        """Prove final draft bytes by authenticated SHA-256 before publication."""

        base = module.base
        base.require(int(draft.get("id", -1)) == EXPECTED_DRAFT_ID, "final draft ID differs")
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
        prefix = f"https://zenodo.org/api/records/{EXPECTED_DRAFT_ID}/draft/files/"
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

    module._local_authority = custom_local_authority
    module.reserve_or_resume = pinned_reserve_or_resume
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
    module = types.ModuleType("pmi_v06214_zenodo_successor")
    module.__file__ = str(Path(__file__).resolve())
    module.__name__ = "pmi_v06214_zenodo_successor"
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
