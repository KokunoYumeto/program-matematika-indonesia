#!/usr/bin/env python3
"""Build the v0.63.24 central successor from a declared committed source.

This is a local, network-free preparation step.  It preserves every
v0.63.23 top-level Zenodo file except the predecessor navigator, refreshes the
exact files changed between the predecessor source commit and the declared
new commit, and adds deterministic nested packets for the three newly admitted
v2.3.1 adapters.  The source commit/tree, predecessor identities, packet
trees, ZIP metadata, member checksums, and two-build byte identity are all
bound in LOCAL_RELEASE.json.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
LOGBOOK = ROOT.parent / "curriculum_logbook"
PREVIOUS_DIR = LOGBOOK / "central-v0.63.23-candidate"
OUTPUT = LOGBOOK / "central-v0.63.24-candidate"
VERSION = "0.63.24"
TAG = "v0.63.24"
PREVIOUS_VERSION = "0.63.23"
PREVIOUS_SOURCE_COMMIT = "526a5f8b923caeb1c59adcddf483e66982a052a6"
PREVIOUS_SOURCE_TREE = "00a879c3a676a35f17da3216909193a34b9c0bfa"
PREVIOUS_RECORD = 22556271
CONCEPT_ID = 22059707
CONCEPT_DOI = "10.5281/zenodo.22059707"
PREVIOUS_DOI = "10.5281/zenodo.22556271"
PREVIOUS_RECEIPT_SHA256 = "ed9298856285f2c173009fc112566e8cb3da2a87db517fcf1e263e4cbb9065aa"
PREVIOUS_NAVIGATOR_SHA256 = "4ac9d5d40da9dc6087d159630036b76c3040d9a13c822d2c30d3281e43efcc38"
PREVIOUS_NAVIGATOR = PREVIOUS_DIR / "peta-belajar-multilingual-v0.63.23.zip"
PREVIOUS_RECEIPT = PREVIOUS_DIR / "ZENODO_PUBLICATION_RECEIPT.json"
NEW_NAVIGATOR = f"peta-belajar-multilingual-v{VERSION}.zip"
CHECKSUM_MEMBER = "CHECKSUMS.sha256"
SOURCE_MARKER = "SOURCE_COMMIT.txt"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
PACKETS = {
    "A30": ("backend/course-capsule-v1/adapters/a30-v231", "packets/A30/A30_PRECALCULUS_V231_ADAPTER.zip"),
    "B95": ("backend/course-capsule-v1/adapters/b95-v231", "packets/B95/B95_OPENINTRO_STATISTICS_V231_ADAPTER.zip"),
    "C140": ("backend/course-capsule-v1/adapters/c140-v231", "packets/C140/C140_MATHEMATICAL_STATISTICS_V231_ADAPTER.zip"),
}
PACKAGE_SOURCES = {
    "A30": "backend/course-capsule-v1/packages/A30_PRECALCULUS_V231_ADAPTER.zip",
    "B95": "backend/course-capsule-v1/packages/B95_OPENINTRO_STATISTICS_V231_ADAPTER.zip",
    "C140": "backend/course-capsule-v1/packages/C140_MATHEMATICAL_STATISTICS_V231_ADAPTER.zip",
}
ALLOWED_CHANGED_ROOTS = (
    "docs/",
    "backend/",
    "scripts/",
    "schemas/",
    "publication-history/",
    "package.json",
    "PUBLICATION_RECEIPT.json",
    "UNIVERSAL_READER_NAVIGATION.md",
)
RELEASE_ONLY_PATHS = {"PUBLICATION_RECEIPT.json"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def md5(data: bytes) -> str:
    """Return the transport checksum used by Zenodo's file inventory."""
    return hashlib.md5(data).hexdigest()


def identity(name: str, data: bytes) -> dict[str, object]:
    return {"name": name, "bytes": len(data), "sha256": sha256(data), "md5": md5(data)}


def git(args: list[str]) -> bytes:
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True)
    return result.stdout


def git_text(args: list[str]) -> str:
    return git(args).decode("utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def safe_name(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        bool(name)
        and not name.startswith(("/", "\\"))
        and ".." not in path.parts
        and ":" not in name
        and "\\" not in name
        and "\x00" not in name
        and all(ord(ch) >= 0x20 for ch in name)
    )


def sort_key(name: str) -> tuple[str, ...]:
    return tuple(part.casefold() for part in PurePosixPath(name).parts)


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (0o100644 & 0xFFFF) << 16
    info.flag_bits |= 0x800
    return info


def build_deterministic_zip(destination: Path, members: dict[str, bytes]) -> dict[str, object]:
    names = sorted(members, key=sort_key)
    require(len(names) == len(set(names)) and all(safe_name(name) for name in names), "Unsafe or duplicate nested packet member")
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as archive:
        for name in names:
            archive.writestr(zip_info(name), members[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(destination) as archive:
        infos = archive.infolist()
        require([row.filename for row in infos] == names, "Nested packet order drift")
        require(archive.testzip() is None, "Nested packet CRC failure")
        require(all(row.date_time == FIXED_TIME and not row.extra and not row.comment for row in infos), "Nested packet metadata drift")
        for name in names:
            require(sha256(archive.read(name)) == sha256(members[name]), f"Nested packet member drift: {name}")
    archive_bytes = destination.read_bytes()
    return {"path": destination.name, "entries": len(names), "uncompressed_bytes": sum(len(value) for value in members.values()), "bytes": len(archive_bytes), "sha256": sha256(archive_bytes), "md5": md5(archive_bytes)}


def source_blob(commit: str, path: str) -> bytes:
    return git(["show", f"{commit}:{path}"])


def changed_paths(commit: str) -> list[str]:
    lines = git_text(["diff", "--name-status", "--find-renames", PREVIOUS_SOURCE_COMMIT, commit]).splitlines()
    paths: set[str] = set()
    for line in lines:
        fields = line.split("\t")
        status = fields[0]
        candidate_paths = fields[1:] if status.startswith(("R", "C")) else [fields[-1]]
        for path in candidate_paths:
            if status.startswith("D"):
                require(any(path.startswith(prefix) or path == prefix for prefix in ALLOWED_CHANGED_ROOTS), f"Deleted path outside release allowlist: {path}")
                paths.add(path)
                continue
            if status.startswith(("R", "C")) and path == fields[1]:
                require(any(path.startswith(prefix) or path == prefix for prefix in ALLOWED_CHANGED_ROOTS), f"Renamed path outside release allowlist: {path}")
                paths.add(path)
                continue
            require(any(path.startswith(prefix) or path == prefix for prefix in ALLOWED_CHANGED_ROOTS), f"Changed path outside release allowlist: {path}")
            paths.add(path)
    return sorted(paths, key=sort_key)


def verify_predecessor() -> tuple[dict[str, dict], dict[str, bytes]]:
    receipt_bytes = PREVIOUS_RECEIPT.read_bytes()
    require(sha256(receipt_bytes) == PREVIOUS_RECEIPT_SHA256, "Predecessor receipt SHA-256 drift")
    receipt = json.loads(receipt_bytes)
    require(receipt["version"] == PREVIOUS_VERSION and int(receipt["record_id"]) == PREVIOUS_RECORD, "Predecessor version/record drift")
    require(receipt["concept_id"] == CONCEPT_ID and receipt["concept_doi"] == CONCEPT_DOI and receipt["doi"] == PREVIOUS_DOI, "Predecessor concept lineage drift")
    require(receipt["access"] == "open" and receipt["status"] == "published_open_and_anonymously_verified", "Predecessor is not public/open")
    files = {row["name"]: row for row in receipt["files"]}
    require(len(files) == 100 and receipt["file_count"] == 100 and receipt["inherited_top_level_files_byte_identical"] == 99, "Predecessor inventory drift")
    old_row = files[PREVIOUS_NAVIGATOR.name]
    old_data = PREVIOUS_NAVIGATOR.read_bytes()
    require(old_row["sha256"] == PREVIOUS_NAVIGATOR_SHA256 and sha256(old_data) == PREVIOUS_NAVIGATOR_SHA256, "Predecessor navigator drift")
    with zipfile.ZipFile(PREVIOUS_NAVIGATOR) as archive:
        require(archive.testzip() is None, "Predecessor navigator CRC failure")
        names = archive.namelist()
        require(names == sorted(names, key=sort_key) and len(names) == len(set(names)), "Predecessor navigator inventory/order drift")
        payload = {name: archive.read(name) for name in names}
    require(
        len(old_data) == old_row["bytes"] and sha256(old_data) == old_row["sha256"],
        "Predecessor navigator receipt identity drift",
    )
    return files, payload


def build_sources(source_commit: str, predecessor_payload: dict[str, bytes], changed: list[str]) -> tuple[dict[str, bytes], dict[str, object]]:
    sources = dict(predecessor_payload)
    sources.pop(NEW_NAVIGATOR, None)
    sources.pop(next((name for name in list(sources) if name.startswith("peta-belajar-multilingual-v0.63.23.zip")), "__absent__"), None)
    removed: list[str] = []
    refreshed: list[str] = []
    ignored_release_only: list[str] = []
    for path in changed:
        if path.endswith(".gitkeep"):
            continue
        # The committed deterministic package ZIPs are source witnesses for
        # the nested learner packets, not additional top-level release files.
        # The successor validator binds each nested packet to these paths.
        if path in PACKAGE_SOURCES.values():
            ignored_release_only.append(path)
            continue
        if path in RELEASE_ONLY_PATHS or path.startswith("publication-history/"):
            ignored_release_only.append(path)
            continue
        if (
            path.startswith("docs/")
            or path.startswith("backend/")
            or path.startswith("scripts/")
            or path.startswith("schemas/")
            or path.startswith("publication-history/")
            or path in {"package.json", "PUBLICATION_RECEIPT.json", "UNIVERSAL_READER_NAVIGATION.md"}
        ):
            try:
                data = source_blob(source_commit, path)
            except subprocess.CalledProcessError:
                if path in sources:
                    sources.pop(path)
                    removed.append(path)
                continue
            sources[path] = data
            refreshed.append(path)
    sources[SOURCE_MARKER] = (source_commit + "\n").encode("ascii")
    return sources, {
        "refreshed_paths": refreshed,
        "removed_paths": removed,
        "ignored_release_only_paths": sorted(ignored_release_only, key=sort_key),
    }


def build_packet_members(source_commit: str, prefix: str) -> dict[str, bytes]:
    names = [row for row in git_text(["ls-tree", "-r", "--name-only", source_commit, prefix]).splitlines() if row]
    require(names, f"No committed packet files under {prefix}")
    members: dict[str, bytes] = {}
    for path in names:
        require(path.startswith(prefix.rstrip("/") + "/"), f"Packet path escaped prefix: {path}")
        relative_name = path[len(prefix):].lstrip("/")
        require(safe_name(relative_name), f"Unsafe packet path: {relative_name}")
        members[relative_name] = source_blob(source_commit, path)
    return members


def make_navigator(source_commit: str, predecessor_payload: dict[str, bytes], sources: dict[str, bytes], packet_members: dict[str, dict[str, bytes]], destination: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="v06324-packets-", dir=destination.parent) as temp:
        temp_path = Path(temp)
        # Recreate generated control members from the new source; never carry
        # the predecessor checksum/source-marker bytes into the new checksum
        # closure.
        sources.pop(CHECKSUM_MEMBER, None)
        sources.pop(SOURCE_MARKER, None)
        sources[SOURCE_MARKER] = (source_commit + "\n").encode("ascii")
        packet_identities: dict[str, dict[str, object]] = {}
        for role, members in packet_members.items():
            nested = temp_path / f"{role}.zip"
            packet_identities[role] = build_deterministic_zip(nested, members)
            committed_package = source_blob(source_commit, PACKAGE_SOURCES[role])
            require(committed_package == nested.read_bytes(), f"Committed package witness drift: {role}")
            packet_identities[role].update({
                # ``path`` from build_deterministic_zip is the temporary
                # staging filename (A30.zip, etc.).  Publish the stable
                # navigator member path in the metadata instead.
                "path": PACKETS[role][1],
                "outer_member": PACKETS[role][1],
                "source_path": PACKAGE_SOURCES[role],
                "source_prefix": PACKETS[role][0],
                "source_bytes": len(committed_package),
                "source_sha256": sha256(committed_package),
                "source_md5": md5(committed_package),
            })
            sources[PACKETS[role][1]] = committed_package
        checksums = {name: sha256(data) for name, data in sources.items()}
        checksum_data = "".join(f"{checksums[name]}  {name}\n" for name in sorted(checksums, key=sort_key)).encode("utf-8")
        all_members = dict(sources)
        all_members[CHECKSUM_MEMBER] = checksum_data
        names = sorted(all_members, key=sort_key)
        with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as archive:
            for name in names:
                archive.writestr(zip_info(name), all_members[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(destination) as archive:
            require(archive.testzip() is None, "Successor navigator CRC failure")
            require(archive.namelist() == names and len(names) == len(set(names)), "Successor navigator order/uniqueness drift")
            require(all(row.date_time == FIXED_TIME and not row.extra and not row.comment for row in archive.infolist()), "Successor navigator metadata drift")
            for name in checksums:
                require(sha256(archive.read(name)) == checksums[name], f"Successor member drift: {name}")
            require(archive.read(SOURCE_MARKER) == (source_commit + "\n").encode("ascii"), "Source marker drift")
            require(archive.read(CHECKSUM_MEMBER) == checksum_data, "Successor checksum member drift")
        return {
            "name": destination.name,
            "bytes": destination.stat().st_size,
            "sha256": sha256(destination.read_bytes()),
            "entries": len(names),
            "checksum_rows": len(checksums),
            "uncompressed_bytes": sum(len(data) for data in sources.values()),
            "packet_archives": packet_identities,
            "changed_source_members": len(sources) - len(predecessor_payload),
        }


def prepare(source_commit: str, source_tree: str, preflight_only: bool) -> dict[str, object]:
    require(
        len(source_commit) == 40
        and source_commit == source_commit.lower()
        and all(ch in "0123456789abcdef" for ch in source_commit),
        "source commit must be a full lowercase SHA-1",
    )
    require(source_commit != PREVIOUS_SOURCE_COMMIT, "successor source must differ from predecessor")
    require(git_text(["rev-parse", f"{source_commit}^{{tree}}"]).strip() == source_tree, "declared source tree does not match commit")
    require(git_text(["rev-parse", f"{PREVIOUS_SOURCE_COMMIT}^{{tree}}"]).strip() == PREVIOUS_SOURCE_TREE, "pinned predecessor tree drift")
    require(git(["merge-base", "--is-ancestor", PREVIOUS_SOURCE_COMMIT, source_commit]) == b"", "new source is not a successor of v0.63.23")
    predecessor_files, predecessor_payload = verify_predecessor()
    changed = changed_paths(source_commit)
    packet_members = {role: build_packet_members(source_commit, prefix) for role, (prefix, _path) in PACKETS.items()}
    if preflight_only:
        return {"status": "ready_for_committed_build", "source_commit": source_commit, "source_tree": source_tree, "changed_paths": len(changed), "predecessor_files": len(predecessor_files), "packet_files": {role: len(rows) for role, rows in packet_members.items()}, "writes": False}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT.iterdir():
        require(path.name in {NEW_NAVIGATOR, "02_learning-map-id.html", "03_learning-map-en.html", "LOCAL_RELEASE.json", "QA_REPORT.md", "ZENODO_NEW_VERSION_INTENT.json"}, f"Unexpected candidate artifact: {path.name}")
    sources, source_refresh = build_sources(source_commit, predecessor_payload, changed)
    with tempfile.TemporaryDirectory(prefix="v06324-nav-", dir=OUTPUT) as temp:
        first = Path(temp) / "first.zip"
        second = Path(temp) / "second.zip"
        first_meta = make_navigator(source_commit, dict(predecessor_payload), sources.copy(), packet_members, first)
        second_meta = make_navigator(source_commit, dict(predecessor_payload), sources.copy(), packet_members, second)
        require(first.read_bytes() == second.read_bytes(), "Successor navigator deterministic replay drift")
        final = OUTPUT / NEW_NAVIGATOR
        if final.exists():
            require(final.read_bytes() == first.read_bytes(), "Existing successor navigator drift")
        else:
            shutil.copyfile(first, final)
    # The first/second deterministic builds use temporary names.  The
    # metadata exposed in the candidate must identify the actual successor
    # artifact that will be uploaded, never the temporary ``first.zip``.
    navigator = {**first_meta, "name": NEW_NAVIGATOR, "deterministic_builds": 2}
    id_map = source_blob(source_commit, "docs/id/learning-map.html")
    en_map = source_blob(source_commit, "docs/en/learning-map.html")
    (OUTPUT / "02_learning-map-id.html").write_bytes(id_map)
    (OUTPUT / "03_learning-map-en.html").write_bytes(en_map)
    inherited = [row for name, row in predecessor_files.items() if name != PREVIOUS_NAVIGATOR.name]
    require(len(inherited) == 99, "Successor must inherit exactly 99 top-level files")
    artifacts = [
        identity(NEW_NAVIGATOR, (OUTPUT / NEW_NAVIGATOR).read_bytes()),
        identity("02_learning-map-id.html", id_map),
        identity("03_learning-map-en.html", en_map),
    ]
    expected_total = sum(int(row["bytes"]) for name, row in predecessor_files.items() if name != PREVIOUS_NAVIGATOR.name) + navigator["bytes"]
    local = {
        "schema": "central-v0.63.24-local-candidate/1",
        "status": "prepared_and_deterministically_verified",
        "version": VERSION,
        "tag": TAG,
        "source": {"commit": source_commit, "tree": source_tree, "base": PREVIOUS_SOURCE_COMMIT, "predecessor_commit": PREVIOUS_SOURCE_COMMIT, "predecessor_tree": PREVIOUS_SOURCE_TREE, "predecessor_is_ancestor": True},
        "predecessor": {"version": PREVIOUS_VERSION, "record_id": PREVIOUS_RECORD, "doi": PREVIOUS_DOI, "concept_id": CONCEPT_ID, "concept_doi": CONCEPT_DOI, "receipt": identity(PREVIOUS_RECEIPT.name, PREVIOUS_RECEIPT.read_bytes()), "navigator": identity(PREVIOUS_NAVIGATOR.name, PREVIOUS_NAVIGATOR.read_bytes()), "file_count": 100, "inherited_top_level_files": 99},
        "navigator": navigator,
        "source_refresh": source_refresh,
        "packet_archives": navigator["packet_archives"],
        "learner_assets": [identity("02_learning-map-id.html", id_map), identity("03_learning-map-en.html", en_map)],
        "artifacts": artifacts,
        "publication_transaction": {
            "delete_only": [PREVIOUS_NAVIGATOR.name],
            "upload_only": [NEW_NAVIGATOR],
            "expected_file_count": 100,
            "expected_total_bytes": expected_total,
            "access_must_remain": "open",
        },
        "zenodo_contract": {"preserve_inherited_top_level_files": 99, "replace_only": PREVIOUS_NAVIGATOR.name, "upload_only": NEW_NAVIGATOR, "target_file_count": 100, "access": "open"},
        "publication_executed": False,
        "network_requests": 0,
        "browser_opened": False,
    }
    (OUTPUT / "LOCAL_RELEASE.json").write_text(json.dumps(local, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUTPUT / "ZENODO_NEW_VERSION_INTENT.json").write_text(json.dumps({"schema": "central-zenodo-successor-intent/1", "status": "ready_for_explicit_publication", "version": VERSION, "tag": TAG, "concept_id": CONCEPT_ID, "concept_doi": CONCEPT_DOI, "predecessor_record": PREVIOUS_RECORD, "predecessor_doi": PREVIOUS_DOI, "preserve_inherited": 99, "replace_navigator": PREVIOUS_NAVIGATOR.name, "new_navigator": NEW_NAVIGATOR, "access": "open"}, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "QA_REPORT.md").write_text(f"# Central successor {VERSION}\n\nPrepared from committed source `{source_commit}` / `{source_tree}`. The predecessor v{PREVIOUS_VERSION} remains the public base; 99 top-level files are preserved byte-for-byte and only its navigator is replaced. The new navigator has {navigator['entries']} members and SHA-256 `{navigator['sha256']}`.\n\nThree additive v2.3.1 adapter packets (A30, B95, C140) are nested under `packets/`; each was built twice with fixed ZIP metadata and re-read with CRC/checksum verification. The machine backend is secondary; learner pages retain native reader and original-source links.\n", encoding="utf-8")
    return local


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-tree", required=True)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    print(json.dumps(prepare(args.source_commit, args.source_tree, args.preflight), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
