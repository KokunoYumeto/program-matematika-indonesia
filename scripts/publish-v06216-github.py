#!/usr/bin/env python3
"""Publish or anonymously verify the exact 112-asset PMI v0.62.16 release.

The default mode is anonymous verify-only.  Remote mutation is reachable only
with the explicit ``--publish`` flag, an explicit credential file, and the
frozen correction commit/tree.  Publication creates or resumes only the
``v0.62.16`` release, uploads only missing assets whose names and bytes match
the local payload, never deletes or replaces an asset, and then anonymously
downloads and hashes every one of the 112 new-release assets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import types
import zipfile
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = PROJECT / "scripts/publish-v06215-github.py"
EXPECTED_TEMPLATE = (
    36_140,
    "bfcf5438349fdd2e90838e71366837b8b635b65ffd005c3c3500536a29081ba3",
)

VERSION = "0.62.16"
PREDECESSOR_VERSION = "0.62.15"
TAG = "v0.62.16"
EXPECTED_FILES = 112
EXPECTED_PREDECESSOR_FILES = 112
EXPECTED_UNCHANGED = 108
EXPECTED_REPLACEMENTS = 1
EXPECTED_PURE_OMISSIONS = 3
EXPECTED_PURE_ADDITIONS = 3
EXPECTED_CHECKSUM_ROWS = 111
EXPECTED_COURSE_COUNT = 40
EXPECTED_PUBLISHED_ROLE_COUNT = 35
EXPECTED_PRODUCTION_ROLE_IDS = ("A20", "A30", "B95", "C140", "D100")
EXPECTED_PRODUCTION_ROLE_COUNT = len(EXPECTED_PRODUCTION_ROLE_IDS)
EXPECTED_DISTINCT_PUBLISHED_DOI_RECORDS = 31

EXPECTED_TARGET_COMMIT = "42a0656177376d5021a014f3e4d5ae6419d07ae5"
EXPECTED_TARGET_TREE = "aa648184b56242f1a234c72d55e0d6d44a317b6c"
EXPECTED_TARGET_PARENT = "26562bf4427974bdeacc578028d0ef324012666d"

RELEASE_DIR = PROJECT / "releases/v0.62.16"
RECEIPT_PATH = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.16.json"
PREDECESSOR_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.15.json"
CHECKSUM_NAME = "RELEASE_CHECKSUMS_v0.62.16.sha256"
SOURCE_ARCHIVE_NAME = "program-matematika-indonesia-source-v0.62.16.zip"
COURSE_CAPSULE_ARCHIVE_NAME = "program-matematika-indonesia-course-capsule-v1.zip"
COURSE_CAPSULE_JSONL_NAME = "course-capsules-v1.jsonl"

EXPECTED_PREDECESSOR_RECEIPT = (
    94_750,
    "164b2941e2d1211c85768a3e235e0e94c37d6478478537a5bb8634c73958652a",
)
EXPECTED_PREDECESSOR_TOTAL_BYTES = 745_035_211
EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE = (
    "62741d6fe384cd73b059c9d267b5703a9511f40ab6557bcfa5bd1aeaff808d5f"
)
EXPECTED_PREDECESSOR_RELEASE_ID = 380_485_973
EXPECTED_PREDECESSOR_COMMIT = "26562bf4427974bdeacc578028d0ef324012666d"
EXPECTED_PREDECESSOR_TREE = "6da0ccacd30d72d09e23cd13e54cca456319da8f"

SAME_NAME_REPLACEMENTS = frozenset({"peta-belajar-luring.html"})
PURE_OMISSIONS = frozenset(
    {
        "RELEASE_CHECKSUMS_v0.62.15.sha256",
        "RELEASE_NOTES_v0.62.15.md",
        "program-matematika-indonesia-source-v0.62.15.zip",
    }
)
PURE_ADDITIONS = frozenset(
    {
        CHECKSUM_NAME,
        "RELEASE_NOTES_v0.62.16.md",
        SOURCE_ARCHIVE_NAME,
    }
)

EXPECTED_SUCCESSOR_TOTAL_BYTES = 745_034_611
EXPECTED_SUCCESSOR_AGGREGATE_SHA256 = (
    "4aff7541a77e76ea937b5f4588a621487cb21a68e007bd7008f911dcd4df50b2"
)
EXPECTED_CHECKSUM_IDENTITY = (
    12_461,
    "120adabada169d60a317a548a679ec9cc85877b195a72f78dfeaa76aee5ce8a6",
)
EXPECTED_SOURCE_ARCHIVE_IDENTITY = (
    508_950_409,
    "4d1b758e4f06fab48bb8ecba63a0b85138dbec4345812d4fee8dea694a8155d0",
)
EXPECTED_SOURCE_ARCHIVE_MEMBERS = 3_140
EXPECTED_REPLACEMENT_IDENTITY = (
    199_553,
    "8e026f6aa83b7acf511d20adb10bf1e5334e7d77ceb6aa3cd7f581bd6a7956c3",
)
EXPECTED_COURSE_CAPSULE_IDENTITY = (
    82_165_750,
    "e0b85de2d8752b6a45edae58c364eec61107af1fd5fb453bc343448f1f00e46f",
)
EXPECTED_COURSE_CAPSULE_MEMBERS = 330
CONFIGURATION_FINALIZED = True

OWNER = "KokunoYumeto"
REPOSITORY = "program-matematika-indonesia"
REPOSITORY_SLUG = f"{OWNER}/{REPOSITORY}"
REPOSITORY_URL = f"https://github.com/{REPOSITORY_SLUG}"
API_ROOT = f"https://api.github.com/repos/{REPOSITORY_SLUG}"
RELEASE_URL = f"{REPOSITORY_URL}/releases/tag/{TAG}"
LEARNER_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
RELEASE_NAME = "Program Matematika Indonesia v0.62.16 — koreksi narasi adapter"
RELEASE_BODY = f"""{LEARNER_URL}

Mulai belajar melalui situs Bahasa Indonesia di atas. Berkas JSON, JSONL, CSV,
schema, receipt, dan ZIP adalah lapisan backend modular serta bukti reproduksi;
berkas tersebut bukan pengganti jalur belajar manusia.

Rilis {TAG} adalah penerus koreksi sempit v0.62.15. Sebanyak 108 aset
dipertahankan secara byte-identik, hanya `peta-belajar-luring.html` yang diganti,
dan tiga berkas rilis berversi diganti oleh nama v0.62.16. Koreksi menyelaraskan
tanggal keadaan kanon dan menjelaskan bahwa kesembilan ikatan peran melalui
delapan paket adapter kini memiliki replay publik lengkap pada snapshot pusat.
Arsip sumber juga mengikat koreksi narasi yang sama pada `docs/index.html`.

Provenans model: OpenAI Codex gpt-5.6-sol, Ultra.
"""


def _load_template() -> types.ModuleType:
    data = TEMPLATE_PATH.read_bytes()
    identity = (len(data), hashlib.sha256(data).hexdigest())
    if identity != EXPECTED_TEMPLATE:
        raise RuntimeError("v0.62.15 GitHub publisher template identity differs")
    module = types.ModuleType("pmi_v06215_github_publisher_template")
    module.__file__ = str(TEMPLATE_PATH)
    module.__name__ = "pmi_v06215_github_publisher_template"
    exec(compile(data, str(TEMPLATE_PATH), "exec"), module.__dict__)
    return module


template = _load_template()
legacy = template.legacy
VerificationError = template.VerificationError
MutationUncertain = template.MutationUncertain
require = template.require
sha256_bytes = template.sha256_bytes
sha256_file = template.sha256_file
canonical_inventory_sha = template.canonical_inventory_sha

_legacy_overrides = {
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
    "USER_AGENT": "Codex-PMI-v06216-GitHub-Publisher/1.0",
    "RELEASE_NAME": RELEASE_NAME,
    "RELEASE_BODY": RELEASE_BODY,
}
legacy.__dict__.update(_legacy_overrides)


def validate_configuration() -> None:
    require(CONFIGURATION_FINALIZED is True, "local-build identities are not finalized")
    require(VERSION == "0.62.16" and TAG == "v0.62.16", "version/tag boundary differs")
    require(RELEASE_DIR == PROJECT / "releases/v0.62.16", "release directory boundary differs")
    require(RECEIPT_PATH == PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.16.json", "receipt path differs")
    require(EXPECTED_PREDECESSOR_FILES == EXPECTED_FILES == 112, "file-count boundary differs")
    require(len(SAME_NAME_REPLACEMENTS) == EXPECTED_REPLACEMENTS == 1, "replacement boundary differs")
    require(len(PURE_OMISSIONS) == EXPECTED_PURE_OMISSIONS == 3, "omission boundary differs")
    require(len(PURE_ADDITIONS) == EXPECTED_PURE_ADDITIONS == 3, "addition boundary differs")
    require(
        SAME_NAME_REPLACEMENTS.isdisjoint(PURE_OMISSIONS)
        and SAME_NAME_REPLACEMENTS.isdisjoint(PURE_ADDITIONS)
        and PURE_OMISSIONS.isdisjoint(PURE_ADDITIONS),
        "release boundary sets overlap",
    )
    require(
        EXPECTED_UNCHANGED + EXPECTED_REPLACEMENTS + EXPECTED_PURE_OMISSIONS
        == EXPECTED_PREDECESSOR_FILES,
        "108+1+3 predecessor equation differs",
    )
    require(
        EXPECTED_UNCHANGED + EXPECTED_REPLACEMENTS + EXPECTED_PURE_ADDITIONS
        == EXPECTED_FILES,
        "108+1+3 successor equation differs",
    )
    require(EXPECTED_TARGET_PARENT == EXPECTED_PREDECESSOR_COMMIT, "successor parent/predecessor commit differs")
    require(RELEASE_URL.endswith("/releases/tag/v0.62.16"), "successor release URL differs")
    require("v0.62.15" not in RELEASE_URL, "publisher could target the predecessor release")
    require(RELEASE_BODY.startswith(LEARNER_URL), "learner URL is not first in release body")
    require("OpenAI Codex gpt-5.6-sol, Ultra." in RELEASE_BODY, "exact model provenance is absent")
    require("token" not in RELEASE_BODY.casefold(), "release body contains credential terminology")
    for value in (
        EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
        EXPECTED_SUCCESSOR_AGGREGATE_SHA256,
        EXPECTED_CHECKSUM_IDENTITY[1],
        EXPECTED_SOURCE_ARCHIVE_IDENTITY[1],
        EXPECTED_REPLACEMENT_IDENTITY[1],
        EXPECTED_COURSE_CAPSULE_IDENTITY[1],
    ):
        require(re.fullmatch(r"[0-9a-f]{64}", value) is not None, "a frozen SHA-256 is malformed")


def predecessor_inventory() -> dict[str, dict[str, Any]]:
    require(
        PREDECESSOR_RECEIPT.is_file() and not PREDECESSOR_RECEIPT.is_symlink(),
        "v0.62.15 GitHub receipt is missing",
    )
    data = PREDECESSOR_RECEIPT.read_bytes()
    require(
        (len(data), sha256_bytes(data)) == EXPECTED_PREDECESSOR_RECEIPT,
        "v0.62.15 GitHub receipt identity differs",
    )
    try:
        receipt = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError("v0.62.15 GitHub receipt is not valid UTF-8 JSON") from exc
    require(isinstance(receipt, dict), "v0.62.15 GitHub receipt is not an object")
    inventory = receipt.get("inventory")
    release = receipt.get("release")
    readback = receipt.get("anonymous_asset_readback")
    require(
        receipt.get("version") == PREDECESSOR_VERSION
        and receipt.get("state") == "published_public_verified",
        "v0.62.15 GitHub state differs",
    )
    require(
        isinstance(inventory, dict)
        and inventory.get("files") == EXPECTED_PREDECESSOR_FILES
        and inventory.get("bytes") == EXPECTED_PREDECESSOR_TOTAL_BYTES
        and inventory.get("aggregate_sha256") == EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
        "v0.62.15 GitHub inventory authority differs",
    )
    require(
        isinstance(release, dict)
        and release.get("id") == EXPECTED_PREDECESSOR_RELEASE_ID
        and release.get("tag") == "v0.62.15"
        and release.get("tag_target_commit") == EXPECTED_PREDECESSOR_COMMIT
        and release.get("tag_target_tree") == EXPECTED_PREDECESSOR_TREE
        and release.get("tag_resolves_to_commit") is True
        and release.get("draft") is False
        and release.get("prerelease") is False,
        "v0.62.15 GitHub release authority differs",
    )
    require(
        isinstance(readback, dict)
        and readback.get("result") == "pass_112_of_112"
        and readback.get("files") == EXPECTED_PREDECESSOR_FILES
        and readback.get("bytes") == EXPECTED_PREDECESSOR_TOTAL_BYTES
        and readback.get("aggregate_sha256") == EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
        "v0.62.15 anonymous readback authority differs",
    )
    payload = readback.get("entries")
    require(isinstance(payload, list) and len(payload) == 112, "v0.62.15 readback is not 112 rows")
    rows: list[dict[str, Any]] = []
    by_name: dict[str, dict[str, Any]] = {}
    for raw in payload:
        require(isinstance(raw, dict), "v0.62.15 inventory row is malformed")
        name = raw.get("name")
        byte_count = raw.get("bytes")
        digest = raw.get("sha256")
        url = raw.get("url")
        require(
            isinstance(name, str)
            and name not in {".", ".."}
            and "/" not in name
            and "\\" not in name
            and not any(ord(character) < 32 for character in name),
            "unsafe predecessor filename",
        )
        require(type(byte_count) is int and byte_count >= 0, f"invalid predecessor size: {name}")
        require(
            isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
            f"invalid predecessor SHA-256: {name}",
        )
        require(
            url == f"{REPOSITORY_URL}/releases/download/v0.62.15/{name}",
            f"invalid predecessor public URL: {name}",
        )
        require(name not in by_name, f"duplicate predecessor filename: {name}")
        row = {"name": name, "bytes": byte_count, "sha256": digest}
        rows.append(row)
        by_name[name] = row
    require(sum(int(row["bytes"]) for row in rows) == EXPECTED_PREDECESSOR_TOTAL_BYTES, "predecessor row bytes differ")
    require(
        canonical_inventory_sha(rows) == EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
        "predecessor rows do not reproduce the aggregate",
    )
    return by_name


def validate_release_boundary(local_rows: list[dict[str, Any]]) -> dict[str, Any]:
    predecessor = predecessor_inventory()
    local = {str(row["name"]): row for row in local_rows}
    require(len(local) == EXPECTED_FILES, "successor local inventory is not 112 unique rows")
    predecessor_names = set(predecessor)
    local_names = set(local)
    omissions = predecessor_names - local_names
    additions = local_names - predecessor_names
    shared = predecessor_names & local_names
    changed = {
        name
        for name in shared
        if (int(local[name]["bytes"]), str(local[name]["sha256"]))
        != (int(predecessor[name]["bytes"]), str(predecessor[name]["sha256"]))
    }
    unchanged = shared - changed
    require(omissions == PURE_OMISSIONS, "v0.62.16 pure-omission set differs")
    require(additions == PURE_ADDITIONS, "v0.62.16 pure-addition set differs")
    require(changed == SAME_NAME_REPLACEMENTS, "v0.62.16 same-name replacement set differs")
    require(len(unchanged) == EXPECTED_UNCHANGED, "v0.62.16 unchanged count differs")
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
        "result": "pass_exact_108_unchanged_1_replacement_3_omissions_3_pure_new",
    }


def _validate_source_correction(path: Path, flat_peta: bytes) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(path, "r") as archive:
            require(archive.comment == EXPECTED_TARGET_COMMIT.encode("ascii"), "source ZIP commit comment differs")
            names = {item.filename for item in archive.infolist() if not item.is_dir()}
            require(
                {"docs/index.html", "docs/peta-belajar-luring.html"} <= names,
                "source archive lacks the two correction pages",
            )
            index_data = archive.read("docs/index.html")
            peta_data = archive.read("docs/peta-belajar-luring.html")
            require(peta_data == flat_peta, "flat offline map differs from the source archive")
            for label, data in (("docs/index.html", index_data), ("docs/peta-belajar-luring.html", peta_data)):
                text = data.decode("utf-8", errors="strict")
                require("1 September 2026" in text, f"canonical update date is absent: {label}")
                require(
                    "Kesembilan ikatan kini memiliki replay publik lengkap pada snapshot pusat." in text,
                    f"corrected adapter narrative is absent: {label}",
                )
                require(
                    "C30, C40, C80, dan C130 diterima lokal dan menunggu rilis pusat penerus" not in text,
                    f"stale adapter narrative remains: {label}",
                )
    except VerificationError:
        raise
    except (OSError, UnicodeError, zipfile.BadZipFile, KeyError) as exc:
        raise VerificationError("source correction pages could not be validated") from exc
    return {
        "commit": EXPECTED_TARGET_COMMIT,
        "tree": EXPECTED_TARGET_TREE,
        "parent": EXPECTED_TARGET_PARENT,
        "changed_paths": ["docs/index.html", "docs/peta-belajar-luring.html"],
        "flat_offline_map_matches_source": True,
        "corrected_narrative_present": True,
    }


def local_inventory() -> tuple[list[dict[str, Any]], dict[str, Path], dict[str, Any]]:
    validate_configuration()
    rows, paths, boundary = template._legacy_local_inventory()
    total = sum(int(row["bytes"]) for row in rows)
    aggregate = canonical_inventory_sha(rows)
    require(total == EXPECTED_SUCCESSOR_TOTAL_BYTES, "successor total-byte freeze differs")
    require(aggregate == EXPECTED_SUCCESSOR_AGGREGATE_SHA256, "successor aggregate freeze differs")
    require(
        (paths[CHECKSUM_NAME].stat().st_size, sha256_file(paths[CHECKSUM_NAME]))
        == EXPECTED_CHECKSUM_IDENTITY,
        "checksum identity freeze differs",
    )
    require(
        (paths[SOURCE_ARCHIVE_NAME].stat().st_size, sha256_file(paths[SOURCE_ARCHIVE_NAME]))
        == EXPECTED_SOURCE_ARCHIVE_IDENTITY,
        "source archive identity freeze differs",
    )
    with zipfile.ZipFile(paths[SOURCE_ARCHIVE_NAME], "r") as archive:
        source_file_members = sum(1 for item in archive.infolist() if not item.is_dir())
    require(source_file_members == EXPECTED_SOURCE_ARCHIVE_MEMBERS, "source archive member-count freeze differs")
    require(
        (paths["peta-belajar-luring.html"].stat().st_size, sha256_file(paths["peta-belajar-luring.html"]))
        == EXPECTED_REPLACEMENT_IDENTITY,
        "offline-map replacement identity freeze differs",
    )
    require(
        (paths[COURSE_CAPSULE_ARCHIVE_NAME].stat().st_size, sha256_file(paths[COURSE_CAPSULE_ARCHIVE_NAME]))
        == EXPECTED_COURSE_CAPSULE_IDENTITY,
        "course-capsule identity freeze differs",
    )
    boundary["v2_snapshot"] = template._validate_v2_assets(paths)
    boundary["source_correction"] = _validate_source_correction(
        paths[SOURCE_ARCHIVE_NAME], paths["peta-belajar-luring.html"].read_bytes()
    )
    return rows, paths, boundary


def receipt_payload(*args: Any, **kwargs: Any) -> dict[str, Any]:
    receipt = template._legacy_receipt_payload(*args, **kwargs)
    receipt["anonymous_asset_readback"]["result"] = "pass_112_of_112"
    receipt["replacement_boundary"]["predecessor_files"] = EXPECTED_PREDECESSOR_FILES
    receipt["replacement_boundary"]["successor_files"] = EXPECTED_FILES
    return receipt


def authenticated_metadata_anonymous_asset_readback(
    local_rows: list[dict[str, Any]], metadata_token_file: Path
) -> tuple[dict[str, Any], str, str, list[dict[str, Any]]]:
    """Use authenticated read-only API metadata, but anonymous asset bytes.

    GitHub's anonymous core API quota is shared by the public egress address and
    can be exhausted by a complete 112-asset audit.  Authentication here is
    limited to repository/release/tag metadata; ``legacy.readback_one`` creates
    a separate credential-free session for every public asset download.
    """

    candidates = legacy.token_candidates(metadata_token_file)
    require(len(candidates) == 1, "metadata credential file must contain exactly one GitHub token")
    client = legacy.GitHubClient(candidates[0])
    try:
        _, repository = client.json("GET", "", expected={200})
        require(isinstance(repository, dict), "repository response is not an object")
        require(repository.get("private") is False, "repository is not public")
        require(repository.get("disabled") is False, "repository is disabled")
        release = legacy.fetch_release(client)
        require(release is not None, "public v0.62.16 release is absent")
        assert release is not None
        require(release.get("html_url") == RELEASE_URL, "public release URL differs")
        require(release.get("tag_name") == TAG, "public release tag differs")
        require(not release.get("draft"), "public release is a draft")
        require(not release.get("prerelease"), "public release is a prerelease")
        require(release.get("name") == RELEASE_NAME, "public release name differs")
        require(release.get("body") == RELEASE_BODY, "public release body differs")
        release_id = legacy.api_integer(release.get("id"), "public release ID", minimum=1)
        assets = legacy.paginated_assets(client, release_id)
        legacy.validate_remote_inventory(assets, local_rows, require_complete=True)
        source_commit, source_tree = legacy.resolve_tag_commit(client)
    finally:
        client.close()

    local = {str(row["name"]): row for row in local_rows}
    remote = {str(asset.get("name") or ""): asset for asset in assets}
    results: list[dict[str, Any]] = []
    with legacy.ThreadPoolExecutor(max_workers=legacy.MAX_WORKERS) as executor:
        futures = {
            executor.submit(legacy.readback_one, remote[name], local[name]): name
            for name in sorted(local)
        }
        for future in legacy.as_completed(futures):
            name = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                raise VerificationError(f"anonymous readback failed for {name}: {exc}") from exc
    results.sort(key=lambda row: str(row["name"]))
    require(len(results) == EXPECTED_FILES, "anonymous readback count differs")
    require(
        sum(int(row["bytes"]) for row in results) == sum(int(row["bytes"]) for row in local_rows),
        "anonymous readback byte total differs",
    )
    require(
        canonical_inventory_sha(results) == canonical_inventory_sha(local_rows),
        "anonymous readback inventory aggregate differs",
    )
    return release, source_commit, source_tree, results


def preflight() -> dict[str, Any]:
    validate_configuration()
    return {
        "status": "PASS_OFFLINE_PREFLIGHT",
        "version": VERSION,
        "tag": TAG,
        "default_mode": "anonymous_verify_only",
        "publish_requires_explicit_flag": True,
        "publish_requires_credential_file": True,
        "publish_requires_frozen_commit_tree": True,
        "old_release_asset_mutations": 0,
        "asset_deletions": 0,
        "asset_replacements": 0,
        "anonymous_readback_expected_files": EXPECTED_FILES,
        "expected_predecessor_files": EXPECTED_PREDECESSOR_FILES,
        "expected_files": EXPECTED_FILES,
        "expected_unchanged": EXPECTED_UNCHANGED,
        "expected_replacements": EXPECTED_REPLACEMENTS,
        "expected_pure_omissions": EXPECTED_PURE_OMISSIONS,
        "expected_pure_additions": EXPECTED_PURE_ADDITIONS,
        "expected_checksum_rows": EXPECTED_CHECKSUM_ROWS,
        "expected_successor_bytes": EXPECTED_SUCCESSOR_TOTAL_BYTES,
        "expected_successor_aggregate_sha256": EXPECTED_SUCCESSOR_AGGREGATE_SHA256,
        "target_commit": EXPECTED_TARGET_COMMIT,
        "target_tree": EXPECTED_TARGET_TREE,
        "network_calls": 0,
        "credential_reads": 0,
        "release_directory_inspected": False,
        "git_commands_used": 0,
    }


legacy.predecessor_inventory = predecessor_inventory
legacy.validate_release_boundary = validate_release_boundary
legacy.local_inventory = local_inventory
legacy.receipt_payload = receipt_payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--publish", action="store_true", help="explicitly publish v0.62.16, then anonymously verify it")
    modes.add_argument("--dry-run", action="store_true", help="validate the exact local payload without network or credentials")
    modes.add_argument("--preflight", action="store_true", help="validate frozen constants without inspecting payload bytes")
    parser.add_argument("--target-commit", help="exact correction commit, required only with --publish")
    parser.add_argument("--target-tree", help="exact correction tree, required only with --publish")
    parser.add_argument("--token-file", type=Path, help="credential file read only with --publish")
    parser.add_argument(
        "--metadata-token-file",
        type=Path,
        help="optional read-only GitHub API credential; asset downloads remain anonymous",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        validate_configuration()
        if args.preflight:
            require(args.token_file is None and args.metadata_token_file is None, "--preflight refuses credential files")
            require(args.target_commit is None and args.target_tree is None, "--preflight refuses target identities")
            print(json.dumps(preflight(), sort_keys=True, separators=(",", ":")))
            return 0
        if args.dry_run:
            require(args.token_file is None and args.metadata_token_file is None, "--dry-run refuses credential files")
            require(args.target_commit is None and args.target_tree is None, "--dry-run refuses target identities")
            rows, _, boundary = local_inventory()
            print(
                json.dumps(
                    {
                        "status": "PASS_LOCAL_DRY_RUN_112_OF_112",
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
            require(args.metadata_token_file is None, "--publish uses --token-file for read-only metadata too")
            require(args.target_commit == EXPECTED_TARGET_COMMIT, "--publish target commit differs from the frozen correction")
            require(args.target_tree == EXPECTED_TARGET_TREE, "--publish target tree differs from the frozen correction")
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
            "old_release_asset_mutations": 0,
            "asset_deletions": 0,
            "asset_replacements": 0,
            "git_commands_used": 0,
            "metadata_api_authentication": bool(args.token_file or args.metadata_token_file),
            "asset_download_authentication": False,
        }
        if args.publish:
            assert args.target_commit is not None and args.target_tree is not None and args.token_file is not None
            execution.update(
                legacy.publish(
                    args.target_commit,
                    args.target_tree,
                    args.token_file.resolve(),
                    rows,
                    paths,
                )
            )
        metadata_token_file = args.token_file if args.publish else args.metadata_token_file
        if metadata_token_file is None:
            release, source_commit, source_tree, readback = legacy.anonymous_public_readback(rows)
        else:
            release, source_commit, source_tree, readback = authenticated_metadata_anonymous_asset_readback(
                rows, metadata_token_file.resolve()
            )
        require(source_commit == EXPECTED_TARGET_COMMIT, "public tag does not resolve to the frozen correction commit")
        require(source_tree == EXPECTED_TARGET_TREE, "public tag does not resolve to the frozen correction tree")
        source_row = next(row for row in rows if row["name"] == SOURCE_ARCHIVE_NAME)
        legacy.validate_source_archive(
            paths[SOURCE_ARCHIVE_NAME], source_row, expected_commit=EXPECTED_TARGET_COMMIT
        )
        final_rows, _, final_boundary = local_inventory()
        require(final_rows == rows and final_boundary == boundary, "local release changed during public verification")
        receipt = receipt_payload(
            rows,
            paths,
            boundary,
            release,
            source_commit,
            source_tree,
            readback,
            execution,
        )
        legacy.atomic_write_receipt(receipt)
        receipt_bytes = RECEIPT_PATH.read_bytes()
        require(json.loads(receipt_bytes.decode("utf-8")) == receipt, "final receipt JSON readback differs")
        print(
            json.dumps(
                {
                    "status": "PASS_PUBLIC_ANONYMOUS_READBACK_112_OF_112",
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
        print(
            json.dumps({"status": "FAIL_CLOSED", "version": VERSION, "error": detail}, sort_keys=True, separators=(",", ":")),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
