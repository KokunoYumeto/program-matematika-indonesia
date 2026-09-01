#!/usr/bin/env python3
"""Publish or anonymously verify the exact 112-asset PMI v0.62.14 GitHub release.

The hardened v0.62.13 publisher supplies transport, bounded mutation, tag
resolution, source-archive, receipt, and anonymous byte-readback primitives.
This successor pins that historical script by hash and replaces every release
boundary affected by v0.62.14.  The default mode remains anonymous verify-only;
remote mutation requires both ``--publish`` and an explicit credential file.

Final local-build identities are deliberately unresolved until the deterministic
v0.62.14 build has completed.  No dry-run, verification, or publication may
proceed until those sentinels are replaced and CONFIGURATION_FINALIZED is true.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import re
import sys
import types
import zipfile
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = PROJECT / "scripts/publish-v06213-github.py"
EXPECTED_TEMPLATE = (
    67_072,
    "e16bae29c5f853d6937541fe51745b0193922b9efed857638ae4a86b2c19c1ae",
)

VERSION = "0.62.14"
PREDECESSOR_VERSION = "0.62.13"
TAG = "v0.62.14"
EXPECTED_PREDECESSOR_FILES = 100
EXPECTED_FILES = 112
EXPECTED_UNCHANGED = 91
EXPECTED_REPLACEMENTS = 6
EXPECTED_PURE_OMISSIONS = 3
EXPECTED_PURE_ADDITIONS = 15
EXPECTED_CHECKSUM_ROWS = 111
EXPECTED_COURSE_COUNT = 40
EXPECTED_PUBLISHED_ROLE_COUNT = 35
EXPECTED_PRODUCTION_ROLE_IDS = ("A20", "A30", "B95", "C140", "D100")
EXPECTED_PRODUCTION_ROLE_COUNT = len(EXPECTED_PRODUCTION_ROLE_IDS)
EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS = 31

RELEASE_DIR = PROJECT / "releases/v0.62.14"
RECEIPT_PATH = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.14.json"
PREDECESSOR_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.13.json"
CHECKSUM_NAME = "RELEASE_CHECKSUMS_v0.62.14.sha256"
SOURCE_ARCHIVE_NAME = "program-matematika-indonesia-source-v0.62.14.zip"
COURSE_CAPSULE_ARCHIVE_NAME = "program-matematika-indonesia-course-capsule-v1.zip"
COURSE_CAPSULE_JSONL_NAME = "course-capsules-v1.jsonl"

EXPECTED_PREDECESSOR_RECEIPT = (
    59_438,
    "e6d59a7a13409afeab90034f1587d067a46106164fac079ec39903f1f899b4cf",
)
EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE = (
    "fa645e4b54973bc750ec6734a3195e22a0ade1d38cbf7f6497c4c1cbab4103ec"
)
EXPECTED_PREDECESSOR_TOTAL_BYTES = 460_869_686
EXPECTED_PREDECESSOR_RELEASE_ID = 379_701_122
EXPECTED_PREDECESSOR_COMMIT = "4ab6eb6b270dc0a32512dad3f998653c336d8492"
EXPECTED_PREDECESSOR_TREE = "268dae1dc622ecdd6290d64a0695388f8800d7a7"

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
        "RELEASE_NOTES_v0.62.14.md",
        SOURCE_ARCHIVE_NAME,
        "program-matematika-indonesia-judson-c30-c40-v2.3.1.zip",
        "program-matematika-indonesia-openlogic-c80-v2.3.1.zip",
        "program-matematika-indonesia-c130-operations-research-v2.3.1.zip",
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
EXPECTED_C130_ARCHIVE_SHA256 = "eb195d1aa555e9d5e639c1e35a08b6f4425be24cc93b7f1f633161e9cacee865"
EXPECTED_TERMINOLOGY_POLICY_SHA256 = "c3bc63376dfeac2427703cc53635c50418c1a5db93abe3074ad65aa760b1acaa"

UNRESOLVED = "__UNRESOLVED_V0_62_14__"
CONFIGURATION_FINALIZED = True
EXPECTED_SUCCESSOR_TOTAL_BYTES: int | None = 744_845_735
EXPECTED_SUCCESSOR_AGGREGATE_SHA256 = "4aa98d92ad3c84752d6914f24b568a46adb27994c75676d5b8a5b86400a5502f"
EXPECTED_CHECKSUM_IDENTITY: tuple[int | None, str] = (
    12_461,
    "700fa9d95d9834b033a009ff333211ccfab7014f417fe5b29922348e489253e5",
)
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

OWNER = "KokunoYumeto"
REPOSITORY = "program-matematika-indonesia"
REPOSITORY_SLUG = f"{OWNER}/{REPOSITORY}"
REPOSITORY_URL = f"https://github.com/{REPOSITORY_SLUG}"
API_ROOT = f"https://api.github.com/repos/{REPOSITORY_SLUG}"
RELEASE_URL = f"{REPOSITORY_URL}/releases/tag/{TAG}"
LEARNER_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
RELEASE_NAME = "Program Matematika Indonesia v0.62.14 — C130 dan snapshot backend modular v2"
RELEASE_BODY = f"""{LEARNER_URL}

Mulai belajar melalui situs Bahasa Indonesia di atas. Berkas JSON, JSONL, CSV,
schema, receipt, dan ZIP adalah lapisan backend modular serta bukti reproduksi;
berkas tersebut bukan pengganti jalur belajar manusia.

Rilis {TAG} mempertahankan 91 aset v0.62.13 secara byte-identik, mengganti enam
nama, dan menambah snapshot backend modular v2. Sembilan peran kurikulum kini
terikat ke delapan paket adapter, termasuk C130 operations-research v2.3.1.
Lima ikatan mempunyai replay publik lengkap; empat ikatan penerus masih ditandai
menunggu publikasi pusat sampai rilis ini selesai. Sebanyak 31 peran tetap tanpa
klaim adapter lokal. Paket kapsul juga memuat kebijakan terminologi berbasis
konsep/register tanpa mengganti bukti terminologi native. Snapshot kursus tetap berisi
35 peran terbit dan lima peran produksi ({", ".join(EXPECTED_PRODUCTION_ROLE_IDS)})
melalui {EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS} rekaman DOI edisi terbit.

Provenans model: OpenAI Codex gpt-5.6-sol, Ultra.
"""


def _load_template() -> types.ModuleType:
    data = TEMPLATE_PATH.read_bytes()
    identity = (len(data), hashlib.sha256(data).hexdigest())
    if identity != EXPECTED_TEMPLATE:
        raise RuntimeError("v0.62.13 GitHub publisher template identity differs")
    module = types.ModuleType("pmi_v06213_github_publisher_template")
    module.__file__ = str(TEMPLATE_PATH)
    module.__name__ = "pmi_v06213_github_publisher_template"
    exec(compile(data, str(TEMPLATE_PATH), "exec"), module.__dict__)
    return module


legacy = _load_template()
VerificationError = legacy.VerificationError
MutationUncertain = legacy.MutationUncertain
require = legacy.require
api_integer = legacy.api_integer
sha256_bytes = legacy.sha256_bytes
sha256_file = legacy.sha256_file
canonical_inventory_sha = legacy.canonical_inventory_sha

_overrides = {
    "__file__": str(Path(__file__).resolve()),
    "PROJECT": PROJECT,
    "RELEASE_DIR": RELEASE_DIR,
    "RECEIPT_PATH": RECEIPT_PATH,
    "CHECKSUM_NAME": CHECKSUM_NAME,
    "OWNER": OWNER,
    "REPOSITORY": REPOSITORY,
    "REPOSITORY_SLUG": REPOSITORY_SLUG,
    "REPOSITORY_URL": REPOSITORY_URL,
    "API_ROOT": API_ROOT,
    "VERSION": VERSION,
    "TAG": TAG,
    "RELEASE_URL": RELEASE_URL,
    "LEARNER_URL": LEARNER_URL,
    "EXPECTED_FILES": EXPECTED_FILES,
    "EXPECTED_UNCHANGED": EXPECTED_UNCHANGED,
    "EXPECTED_REPLACEMENTS": EXPECTED_REPLACEMENTS,
    "EXPECTED_PURE_ADDITIONS": EXPECTED_PURE_ADDITIONS,
    "EXPECTED_COURSE_COUNT": EXPECTED_COURSE_COUNT,
    "EXPECTED_PUBLISHED_ROLE_COUNT": EXPECTED_PUBLISHED_ROLE_COUNT,
    "EXPECTED_PRODUCTION_ROLE_IDS": EXPECTED_PRODUCTION_ROLE_IDS,
    "EXPECTED_PRODUCTION_ROLE_COUNT": EXPECTED_PRODUCTION_ROLE_COUNT,
    "EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS": EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS,
    "PREDECESSOR_RECEIPT": PREDECESSOR_RECEIPT,
    "EXPECTED_PREDECESSOR_RECEIPT": EXPECTED_PREDECESSOR_RECEIPT,
    "EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE": EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
    "SOURCE_ARCHIVE_NAME": SOURCE_ARCHIVE_NAME,
    "COURSE_CAPSULE_ARCHIVE_NAME": COURSE_CAPSULE_ARCHIVE_NAME,
    "COURSE_CAPSULE_JSONL_NAME": COURSE_CAPSULE_JSONL_NAME,
    "PURE_OMISSIONS": PURE_OMISSIONS,
    "SAME_NAME_REPLACEMENTS": SAME_NAME_REPLACEMENTS,
    "PURE_ADDITIONS": PURE_ADDITIONS,
    "USER_AGENT": "Codex-PMI-v06214-GitHub-Publisher/1.0",
    "RELEASE_NAME": RELEASE_NAME,
    "RELEASE_BODY": RELEASE_BODY,
}
legacy.__dict__.update(_overrides)


def _valid_identity(value: tuple[int | None, str]) -> bool:
    return (
        type(value[0]) is int
        and value[0] >= 0
        and isinstance(value[1], str)
        and re.fullmatch(r"[0-9a-f]{64}", value[1]) is not None
    )


def validate_configuration() -> None:
    require(CONFIGURATION_FINALIZED is True, "set CONFIGURATION_FINALIZED only after freezing final local-build identities")
    require(EXPECTED_PREDECESSOR_FILES == 100 and EXPECTED_FILES == 112, "predecessor/successor counts differ")
    require(len(SAME_NAME_REPLACEMENTS) == EXPECTED_REPLACEMENTS, "replacement set count differs")
    require(len(PURE_OMISSIONS) == EXPECTED_PURE_OMISSIONS, "omission set count differs")
    require(len(PURE_ADDITIONS) == EXPECTED_PURE_ADDITIONS, "addition set count differs")
    require(
        SAME_NAME_REPLACEMENTS.isdisjoint(PURE_OMISSIONS)
        and SAME_NAME_REPLACEMENTS.isdisjoint(PURE_ADDITIONS)
        and PURE_OMISSIONS.isdisjoint(PURE_ADDITIONS),
        "release boundary sets overlap",
    )
    require(
        EXPECTED_UNCHANGED + EXPECTED_REPLACEMENTS + EXPECTED_PURE_OMISSIONS == EXPECTED_PREDECESSOR_FILES,
        "91+6+3 predecessor equation differs",
    )
    require(
        EXPECTED_UNCHANGED + EXPECTED_REPLACEMENTS + EXPECTED_PURE_ADDITIONS == EXPECTED_FILES,
        "91+6+15 successor equation differs",
    )
    require(type(EXPECTED_SUCCESSOR_TOTAL_BYTES) is int and EXPECTED_SUCCESSOR_TOTAL_BYTES > 0, "successor total bytes are unresolved")
    require(re.fullmatch(r"[0-9a-f]{64}", EXPECTED_SUCCESSOR_AGGREGATE_SHA256) is not None, "successor aggregate is unresolved")
    require(_valid_identity(EXPECTED_CHECKSUM_IDENTITY), "checksum identity is unresolved")
    require(_valid_identity(EXPECTED_SOURCE_ARCHIVE_IDENTITY), "source archive identity is unresolved")
    require(type(EXPECTED_SOURCE_ARCHIVE_MEMBERS) is int and EXPECTED_SOURCE_ARCHIVE_MEMBERS > 0, "source archive member count is unresolved")
    require(_valid_identity(EXPECTED_COURSE_CAPSULE_IDENTITY), "course-capsule identity is unresolved")
    require(type(EXPECTED_COURSE_CAPSULE_MEMBERS) is int and EXPECTED_COURSE_CAPSULE_MEMBERS > 0, "course-capsule member count is unresolved")
    serialized = json.dumps(
        {
            "aggregate": EXPECTED_SUCCESSOR_AGGREGATE_SHA256,
            "checksum": EXPECTED_CHECKSUM_IDENTITY,
            "source": EXPECTED_SOURCE_ARCHIVE_IDENTITY,
            "capsule": EXPECTED_COURSE_CAPSULE_IDENTITY,
        },
        sort_keys=True,
    )
    require(UNRESOLVED not in serialized and "TODO" not in serialized and "REPLACE_ME" not in serialized, "configuration contains an unresolved marker")


def predecessor_inventory() -> dict[str, dict[str, Any]]:
    require(PREDECESSOR_RECEIPT.is_file() and not PREDECESSOR_RECEIPT.is_symlink(), "v0.62.13 receipt is missing")
    data = PREDECESSOR_RECEIPT.read_bytes()
    require((len(data), sha256_bytes(data)) == EXPECTED_PREDECESSOR_RECEIPT, "v0.62.13 receipt identity differs")
    try:
        receipt = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError("v0.62.13 receipt is not valid UTF-8 JSON") from exc
    require(isinstance(receipt, dict), "v0.62.13 receipt is not an object")
    require(receipt.get("version") == PREDECESSOR_VERSION, "predecessor version differs")
    require(receipt.get("state") == "published_open_modular_backend_successor", "predecessor state differs")
    require(receipt.get("payload_total_bytes") == EXPECTED_PREDECESSOR_TOTAL_BYTES, "predecessor total bytes differ")
    require(receipt.get("payload_inventory_aggregate_sha256") == EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE, "predecessor aggregate differs")
    github = receipt.get("github_authority")
    zenodo = receipt.get("zenodo")
    require(
        isinstance(github, dict)
        and github.get("tag_target_commit") == EXPECTED_PREDECESSOR_COMMIT
        and github.get("source_tree") == EXPECTED_PREDECESSOR_TREE
        and github.get("anonymous_readback") == "pass_100_of_100",
        "predecessor GitHub authority differs",
    )
    require(
        isinstance(zenodo, dict)
        and zenodo.get("record_id") == 22_207_081
        and zenodo.get("file_count") == EXPECTED_PREDECESSOR_FILES
        and zenodo.get("access_right") == "open"
        and zenodo.get("anonymous_readback") == "pass_100_of_100",
        "predecessor Zenodo authority differs",
    )
    payload = receipt.get("payload_inventory")
    require(isinstance(payload, list) and len(payload) == EXPECTED_PREDECESSOR_FILES, "predecessor inventory is not 100 rows")
    rows: list[dict[str, Any]] = []
    by_name: dict[str, dict[str, Any]] = {}
    for raw in payload:
        require(isinstance(raw, dict), "predecessor inventory row is malformed")
        name = raw.get("name")
        byte_count = raw.get("bytes")
        digest = raw.get("sha256")
        require(isinstance(name, str) and name not in {".", ".."} and "/" not in name and "\\" not in name, "unsafe predecessor filename")
        require(type(byte_count) is int and byte_count >= 0, f"invalid predecessor size: {name}")
        require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None, f"invalid predecessor SHA: {name}")
        require(name not in by_name, f"duplicate predecessor filename: {name}")
        row = {"name": name, "bytes": byte_count, "sha256": digest}
        rows.append(row)
        by_name[name] = row
    require(canonical_inventory_sha(rows) == EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE, "predecessor rows do not reproduce aggregate")
    return by_name


def validate_release_boundary(local_rows: list[dict[str, Any]]) -> dict[str, Any]:
    predecessor = predecessor_inventory()
    local = {str(row["name"]): row for row in local_rows}
    require(len(local) == EXPECTED_FILES, "successor inventory is not 112 unique rows")
    predecessor_names = set(predecessor)
    local_names = set(local)
    pure_omissions = predecessor_names - local_names
    pure_additions = local_names - predecessor_names
    shared = predecessor_names & local_names
    changed = {
        name
        for name in shared
        if (int(local[name]["bytes"]), str(local[name]["sha256"]))
        != (int(predecessor[name]["bytes"]), str(predecessor[name]["sha256"]))
    }
    unchanged = shared - changed
    require(pure_omissions == PURE_OMISSIONS, "v0.62.14 pure-omission set differs")
    require(pure_additions == PURE_ADDITIONS, "v0.62.14 pure-addition set differs")
    require(changed == SAME_NAME_REPLACEMENTS, "v0.62.14 replacement set differs")
    require(len(unchanged) == EXPECTED_UNCHANGED, "v0.62.14 unchanged count differs")
    for name in unchanged:
        require(local[name] == predecessor[name], f"retained predecessor bytes differ: {name}")
    return {
        "predecessor_version": PREDECESSOR_VERSION,
        "predecessor_inventory_aggregate_sha256": EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
        "predecessor_files": EXPECTED_PREDECESSOR_FILES,
        "successor_files": EXPECTED_FILES,
        "unchanged_exact_files": EXPECTED_UNCHANGED,
        "same_name_replacements": EXPECTED_REPLACEMENTS,
        "pure_additions": EXPECTED_PURE_ADDITIONS,
        "pure_omissions": EXPECTED_PURE_OMISSIONS,
        "same_name_replacement_names": sorted(SAME_NAME_REPLACEMENTS),
        "pure_addition_names": sorted(PURE_ADDITIONS),
        "pure_omission_names": sorted(PURE_OMISSIONS),
        "result": "pass_exact_91_unchanged_6_replacements_3_omissions_15_pure_new",
    }


def _json_object(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"{label} is not valid UTF-8 JSON") from exc
    require(isinstance(value, dict), f"{label} is not an object")
    return value


def validate_course_capsule_archive(path: Path, flat_jsonl: bytes, snapshot: dict[str, Any]) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), "course-capsule archive is missing")
    require((path.stat().st_size, sha256_file(path)) == EXPECTED_COURSE_CAPSULE_IDENTITY, "course-capsule archive identity differs")
    required = {
        "backend/course-capsule-v1/generated/course-capsules.jsonl",
        "docs/data/course-capsule-v1/course-capsules.jsonl",
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
    try:
        with zipfile.ZipFile(path, "r") as archive:
            members = archive.infolist()
            names = [member.filename for member in members if not member.is_dir()]
            require(len(names) == EXPECTED_COURSE_CAPSULE_MEMBERS, "course-capsule member count differs")
            require(len(names) == len(set(names)), "course-capsule has duplicate members")
            require(required <= set(names), "course-capsule lacks required C130/v2 members")
            require(archive.testzip() is None, "course-capsule CRC validation failed")
            require(archive.read("backend/course-capsule-v1/generated/course-capsules.jsonl") == flat_jsonl, "backend JSONL differs")
            require(archive.read("docs/data/course-capsule-v1/course-capsules.jsonl") == flat_jsonl, "public JSONL differs")
            require(
                archive.read("backend/course-capsule-v1/authority/public-baseline-v0.62.12.json")
                == archive.read("docs/data/course-capsule-v1/public-baseline-v0.62.12.json"),
                "baseline mirror bytes differ",
            )
            terminology_pairs = (
                ("backend/course-capsule-v1/authority/terminology-policy-v1/README.md", "docs/data/course-capsule-v1/terminology-policy-v1/README.md"),
                ("backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json", "docs/data/course-capsule-v1/terminology-policy-v1/canonical-register-policy.json"),
                ("backend/course-capsule-v1/authority/terminology-policy-v1/checksums.sha256", "docs/data/course-capsule-v1/terminology-policy-v1/checksums.sha256"),
                ("schemas/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json", "docs/schema/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json"),
                ("schemas/course-capsule-v1/v2/terminology-concept-record-v1.schema.json", "docs/schema/course-capsule-v1/v2/terminology-concept-record-v1.schema.json"),
            )
            for authority, public in terminology_pairs:
                require(archive.read(authority) == archive.read(public), f"terminology mirror bytes differ: {authority}")
            require(
                sha256_bytes(archive.read("backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json"))
                == EXPECTED_TERMINOLOGY_POLICY_SHA256,
                "terminology-policy identity differs",
            )
            c130 = archive.read("backend/course-capsule-v1/builds/program-matematika-indonesia-c130-operations-research-v2.3.1.zip")
            require(sha256_bytes(c130) == EXPECTED_C130_ARCHIVE_SHA256, "embedded C130 package differs")
    except VerificationError:
        raise
    except (OSError, zipfile.BadZipFile, KeyError, RuntimeError) as exc:
        raise VerificationError("course-capsule archive could not be validated") from exc
    return {
        "name": COURSE_CAPSULE_ARCHIVE_NAME,
        "members": EXPECTED_COURSE_CAPSULE_MEMBERS,
        "course_count": snapshot["course_count"],
        "production_role_ids": snapshot["production_role_ids"],
        "c130_package_sha256": EXPECTED_C130_ARCHIVE_SHA256,
        "v2_snapshot_bound": True,
    }


def _validate_v2_assets(paths: dict[str, Path]) -> dict[str, Any]:
    required = {
        "v23-adapter-index-v2.json",
        "modular-backend-pattern-index-v2.json",
        "feature-adoption-provenance-v1.json",
        "comparison-evidence-manifest-v1.json",
        "MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json",
    }
    require(required <= set(paths), "flat v2 snapshot assets are incomplete")
    index = _json_object(paths["v23-adapter-index-v2.json"].read_bytes(), "v2 adapter index")
    adapters = index.get("adapters")
    packages = index.get("packages")
    require(isinstance(adapters, list) and isinstance(packages, list), "v2 adapter arrays are missing")
    roles = tuple(str(row.get("role_id")) for row in adapters if isinstance(row, dict))
    require(roles == EXPECTED_ADAPTER_ROLE_ORDER, "v2 adapter role order differs")
    require(index.get("summary") == EXPECTED_V2_SUMMARY, "v2 adapter summary differs")
    c130 = [row for row in packages if isinstance(row, dict) and row.get("package_id") == EXPECTED_C130_PACKAGE_ID]
    require(len(c130) == 1 and c130[0].get("canonical_records") == 51_704, "C130 package row differs")
    require(c130[0].get("archive", {}).get("sha256") == EXPECTED_C130_ARCHIVE_SHA256, "C130 archive binding differs")
    receipt = _json_object(paths["MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json"].read_bytes(), "v2 snapshot receipt")
    require(receipt.get("status") == "pass" and receipt.get("summary") == EXPECTED_V2_SUMMARY, "v2 snapshot receipt differs")
    return {"adapter_role_order": list(roles), "summary": EXPECTED_V2_SUMMARY}


_legacy_local_inventory = legacy.local_inventory


def local_inventory() -> tuple[list[dict[str, Any]], dict[str, Path], dict[str, Any]]:
    validate_configuration()
    rows, paths, boundary = _legacy_local_inventory()
    total = sum(int(row["bytes"]) for row in rows)
    aggregate = canonical_inventory_sha(rows)
    require(total == EXPECTED_SUCCESSOR_TOTAL_BYTES, "successor total-byte freeze differs")
    require(aggregate == EXPECTED_SUCCESSOR_AGGREGATE_SHA256, "successor aggregate freeze differs")
    require((paths[CHECKSUM_NAME].stat().st_size, sha256_file(paths[CHECKSUM_NAME])) == EXPECTED_CHECKSUM_IDENTITY, "checksum identity freeze differs")
    require((paths[SOURCE_ARCHIVE_NAME].stat().st_size, sha256_file(paths[SOURCE_ARCHIVE_NAME])) == EXPECTED_SOURCE_ARCHIVE_IDENTITY, "source archive identity freeze differs")
    with zipfile.ZipFile(paths[SOURCE_ARCHIVE_NAME], "r") as source_archive:
        source_file_members = sum(1 for item in source_archive.infolist() if not item.is_dir())
    require(
        source_file_members == EXPECTED_SOURCE_ARCHIVE_MEMBERS,
        "source archive regular-file member-count freeze differs",
    )
    require((paths[COURSE_CAPSULE_ARCHIVE_NAME].stat().st_size, sha256_file(paths[COURSE_CAPSULE_ARCHIVE_NAME])) == EXPECTED_COURSE_CAPSULE_IDENTITY, "course-capsule identity freeze differs")
    boundary["v2_snapshot"] = _validate_v2_assets(paths)
    return rows, paths, boundary


def paginated_assets(client: Any, release_id: int) -> list[dict[str, Any]]:
    data_pages = (EXPECTED_FILES + 99) // 100
    pages: list[list[dict[str, Any]]] = []
    for page in range(1, data_pages + 2):
        _, payload = client.json(
            "GET",
            f"/releases/{release_id}/assets?per_page=100&page={page}",
            expected={200},
        )
        require(isinstance(payload, list), f"release asset page {page} is not a list")
        require(len(payload) <= 100, f"release asset page {page} exceeds 100 rows")
        require(all(isinstance(asset, dict) for asset in payload), f"release asset page {page} contains a non-object")
        if page == data_pages + 1:
            require(not payload, "release contains more assets than the bounded successor permits")
        pages.append(payload)
    assets = [asset for page in pages[:-1] for asset in page]
    require(len(assets) <= EXPECTED_FILES, "release asset pagination exceeds 112 rows")
    return assets


_legacy_receipt_payload = legacy.receipt_payload


def receipt_payload(*args: Any, **kwargs: Any) -> dict[str, Any]:
    receipt = _legacy_receipt_payload(*args, **kwargs)
    receipt["anonymous_asset_readback"]["result"] = f"pass_{EXPECTED_FILES}_of_{EXPECTED_FILES}"
    receipt["replacement_boundary"]["predecessor_files"] = EXPECTED_PREDECESSOR_FILES
    receipt["replacement_boundary"]["successor_files"] = EXPECTED_FILES
    return receipt


def preflight() -> dict[str, Any]:
    validate_configuration()
    require(RELEASE_DIR == PROJECT / "releases/v0.62.14", "release directory boundary differs")
    require(RECEIPT_PATH == PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.14.json", "receipt path differs")
    require(RELEASE_BODY.startswith(LEARNER_URL), "learner URL is not first in release body")
    require("token" not in RELEASE_BODY.casefold(), "release body contains credential terminology")
    return {
        "status": "PASS_OFFLINE_PREFLIGHT",
        "version": VERSION,
        "tag": TAG,
        "expected_predecessor_files": EXPECTED_PREDECESSOR_FILES,
        "expected_files": EXPECTED_FILES,
        "expected_unchanged": EXPECTED_UNCHANGED,
        "expected_replacements": EXPECTED_REPLACEMENTS,
        "expected_pure_omissions": EXPECTED_PURE_OMISSIONS,
        "expected_pure_additions": EXPECTED_PURE_ADDITIONS,
        "expected_checksum_rows": EXPECTED_CHECKSUM_ROWS,
        "network_calls": 0,
        "credential_reads": 0,
        "release_directory_inspected": False,
        "git_commands_used": 0,
    }


legacy.predecessor_inventory = predecessor_inventory
legacy.validate_release_boundary = validate_release_boundary
legacy.validate_course_capsule_archive = validate_course_capsule_archive
legacy.local_inventory = local_inventory
legacy.paginated_assets = paginated_assets
legacy.receipt_payload = receipt_payload
legacy.preflight = preflight


def main(argv: list[str] | None = None) -> int:
    args = legacy.parse_args(argv)
    try:
        validate_configuration()
        if args.preflight:
            require(args.token_file is None, "--preflight refuses --token-file")
            require(args.target_commit is None and args.target_tree is None, "--preflight refuses target identities")
            print(json.dumps(preflight(), sort_keys=True, separators=(",", ":")))
            return 0
        if args.dry_run:
            require(args.token_file is None, "--dry-run refuses --token-file")
            require(args.target_commit is None and args.target_tree is None, "--dry-run refuses target identities")
            rows, _, boundary = local_inventory()
            print(
                json.dumps(
                    {
                        "status": f"PASS_LOCAL_DRY_RUN_{EXPECTED_FILES}_OF_{EXPECTED_FILES}",
                        "version": VERSION,
                        "tag": TAG,
                        "files": len(rows),
                        "bytes": sum(int(row["bytes"]) for row in rows),
                        "inventory_aggregate_sha256": canonical_inventory_sha(rows),
                        "replacement_boundary": boundary,
                        "network_calls": 0,
                        "credential_reads": 0,
                        "receipt_written": False,
                        "git_commands_used": 0,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
            return 0
        if args.publish:
            require(args.token_file is not None, "--publish requires --token-file")
            require(args.target_commit is not None and args.target_tree is not None, "--publish requires target commit/tree")
        else:
            require(args.token_file is None, "verify-only mode refuses --token-file")
            require(args.target_commit is None and args.target_tree is None, "verify-only derives tag commit/tree")

        rows, paths, boundary = local_inventory()
        execution: dict[str, Any] = {
            "publish_requested": bool(args.publish),
            "created_in_this_execution": False,
            "resumed_existing_release": False,
            "assets_present_before": None,
            "assets_uploaded_in_this_execution": 0,
            "uploaded_names": [],
            "release_mutation_calls_are_bounded": True,
            "git_commands_used": 0,
        }
        if args.publish:
            execution.update(legacy.publish(args.target_commit, args.target_tree, args.token_file.resolve(), rows, paths))
        release, source_commit, source_tree, readback = legacy.anonymous_public_readback(rows)
        if args.publish:
            require(source_commit == args.target_commit, "anonymous tag target differs from requested commit")
            require(source_tree == args.target_tree, "anonymous tag tree differs from requested tree")
        source_row = next(row for row in rows if row["name"] == SOURCE_ARCHIVE_NAME)
        source_details = legacy.validate_source_archive(paths[SOURCE_ARCHIVE_NAME], source_row, expected_commit=source_commit)
        with zipfile.ZipFile(paths[SOURCE_ARCHIVE_NAME], "r") as source_archive:
            source_file_members = sum(1 for item in source_archive.infolist() if not item.is_dir())
        require(
            source_file_members == EXPECTED_SOURCE_ARCHIVE_MEMBERS,
            "source archive regular-file member-count freeze differs",
        )
        final_rows, _, final_boundary = local_inventory()
        require(final_rows == rows and final_boundary == boundary, "local release changed during public verification")
        receipt = receipt_payload(rows, paths, boundary, release, source_commit, source_tree, readback, execution)
        legacy.atomic_write_receipt(receipt)
        receipt_bytes = RECEIPT_PATH.read_bytes()
        require(json.loads(receipt_bytes.decode("utf-8")) == receipt, "final receipt JSON readback differs")
        print(
            json.dumps(
                {
                    "status": f"PASS_PUBLIC_ANONYMOUS_READBACK_{EXPECTED_FILES}_OF_{EXPECTED_FILES}",
                    "mode": receipt["mode"],
                    "release": RELEASE_URL,
                    "source_commit": source_commit,
                    "source_tree": source_tree,
                    "files": EXPECTED_FILES,
                    "bytes": receipt["inventory"]["bytes"],
                    "inventory_aggregate_sha256": receipt["inventory"]["aggregate_sha256"],
                    "receipt": RECEIPT_PATH.relative_to(PROJECT).as_posix(),
                    "receipt_bytes": len(receipt_bytes),
                    "receipt_sha256": sha256_bytes(receipt_bytes),
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    except (VerificationError, MutationUncertain, OSError, RuntimeError) as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(json.dumps({"status": "FAIL_CLOSED", "version": VERSION, "error": detail}, sort_keys=True, separators=(",", ":")), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
