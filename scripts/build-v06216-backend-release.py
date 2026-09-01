#!/usr/bin/env python3
"""Preflight or assemble the exact 112-file PMI v0.62.16 GitHub payload.

The release is a narrowly bounded successor of the anonymously verified
v0.62.15 GitHub release.  It retains 108 predecessor files byte-for-byte,
replaces only ``peta-belajar-luring.html``, omits only the three versioned
v0.62.15 release files, and adds the corresponding three v0.62.16 files.

The deterministic source archive is bound to the explicit correction commit.
That commit must have the verified v0.62.15 product commit as its sole parent
and may change only ``docs/index.html`` and
``docs/peta-belajar-luring.html``.  This script has no publication operation
and performs no credential read or authenticated network request.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import types
from pathlib import Path
from typing import Any, Iterable


VERSION = "0.62.16"
PREDECESSOR_VERSION = "0.62.15"
EXPECTED_FILES = 112
EXPECTED_PREDECESSOR_FILES = 112
EXPECTED_RETAINED = 108
EXPECTED_REPLACEMENTS = 1
EXPECTED_PURE_OMISSIONS = 3
EXPECTED_PURE_ADDITIONS = 3
EXPECTED_CHECKSUM_ROWS = EXPECTED_FILES - 1

EXPECTED_SOURCE_COMMIT = "42a0656177376d5021a014f3e4d5ae6419d07ae5"
EXPECTED_SOURCE_TREE = "aa648184b56242f1a234c72d55e0d6d44a317b6c"
EXPECTED_SOURCE_PARENT = "26562bf4427974bdeacc578028d0ef324012666d"
EXPECTED_SOURCE_CHANGED_PATHS = frozenset(
    {"docs/index.html", "docs/peta-belajar-luring.html"}
)

PROJECT = Path(__file__).resolve().parents[1]
RELEASES_DIR = PROJECT / "releases"
PREDECESSOR_DIR = RELEASES_DIR / f"v{PREDECESSOR_VERSION}"
OUTPUT_DIR = RELEASES_DIR / f"v{VERSION}"
PREDECESSOR_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.15.json"

EXPECTED_PREDECESSOR_RECEIPT = (
    94_750,
    "164b2941e2d1211c85768a3e235e0e94c37d6478478537a5bb8634c73958652a",
)
EXPECTED_PREDECESSOR_TOTAL_BYTES = 745_035_211
EXPECTED_PREDECESSOR_AGGREGATE = (
    "62741d6fe384cd73b059c9d267b5703a9511f40ab6557bcfa5bd1aeaff808d5f"
)
EXPECTED_PREDECESSOR_RELEASE_ID = 380_485_973
EXPECTED_PREDECESSOR_COMMIT = "26562bf4427974bdeacc578028d0ef324012666d"
EXPECTED_PREDECESSOR_TREE = "6da0ccacd30d72d09e23cd13e54cca456319da8f"

SOURCE_ZIP_NAME = "program-matematika-indonesia-source-v0.62.16.zip"
NOTES_NAME = "RELEASE_NOTES_v0.62.16.md"
CHECKSUM_NAME = "RELEASE_CHECKSUMS_v0.62.16.sha256"

SAME_NAME_REPLACEMENTS = frozenset({"peta-belajar-luring.html"})
PURE_OMISSIONS = frozenset(
    {
        "RELEASE_CHECKSUMS_v0.62.15.sha256",
        "RELEASE_NOTES_v0.62.15.md",
        "program-matematika-indonesia-source-v0.62.15.zip",
    }
)
PURE_ADDITIONS = frozenset({CHECKSUM_NAME, NOTES_NAME, SOURCE_ZIP_NAME})
REPLACEMENT_SOURCES = {
    "peta-belajar-luring.html": PROJECT / "docs/peta-belajar-luring.html"
}

TEMPLATE_PATH = PROJECT / "scripts/build-v06215-backend-release.py"
EXPECTED_TEMPLATE = (
    46_289,
    "966c849dbc5b597b9956786492bc347b781c65c6dc5c380ac498253e7c450193",
)
BUILD_PREFIX = ".v0.62.16-build-"


def _load_template() -> types.ModuleType:
    data = TEMPLATE_PATH.read_bytes()
    identity = (len(data), hashlib.sha256(data).hexdigest())
    if identity != EXPECTED_TEMPLATE:
        raise RuntimeError("v0.62.15 builder template identity differs")
    module = types.ModuleType("pmi_v06215_release_builder_template")
    module.__file__ = str(TEMPLATE_PATH)
    module.__name__ = "pmi_v06215_release_builder_template"
    exec(compile(data, str(TEMPLATE_PATH), "exec"), module.__dict__)
    return module


template = _load_template()
BuildError = template.BuildError
require = template.require
sha256 = template.sha256
fact = template.fact
inventory_aggregate = template.inventory_aggregate
privacy_scan = template.privacy_scan
validate_source_authority = template.validate_source_authority
require_committed_bytes = template.require_committed_bytes
build_source_archive = template.build_source_archive
run_git_bytes = template.legacy.run_git_bytes
template.legacy.SOURCE_ZIP_NAME = SOURCE_ZIP_NAME


def _strict_object(path: Path, label: str) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), f"{label} is missing or symlinked")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"{label} is not valid UTF-8 JSON") from exc
    require(isinstance(value, dict), f"{label} is not an object")
    return value


def _predecessor_inventory() -> tuple[dict[str, dict[str, Any]], frozenset[str]]:
    data = PREDECESSOR_RECEIPT.read_bytes()
    require(
        (len(data), sha256(data)) == EXPECTED_PREDECESSOR_RECEIPT,
        "v0.62.15 GitHub receipt identity differs",
    )
    receipt = _strict_object(PREDECESSOR_RECEIPT, "v0.62.15 GitHub receipt")
    inventory = receipt.get("inventory")
    release = receipt.get("release")
    readback = receipt.get("anonymous_asset_readback")
    require(
        receipt.get("version") == PREDECESSOR_VERSION
        and receipt.get("state") == "published_public_verified",
        "v0.62.15 GitHub publication state differs",
    )
    require(
        isinstance(inventory, dict)
        and inventory.get("files") == EXPECTED_PREDECESSOR_FILES
        and inventory.get("bytes") == EXPECTED_PREDECESSOR_TOTAL_BYTES
        and inventory.get("aggregate_sha256") == EXPECTED_PREDECESSOR_AGGREGATE,
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
        and readback.get("aggregate_sha256") == EXPECTED_PREDECESSOR_AGGREGATE,
        "v0.62.15 anonymous readback authority differs",
    )
    payload = readback.get("entries")
    require(
        isinstance(payload, list) and len(payload) == EXPECTED_PREDECESSOR_FILES,
        "v0.62.15 anonymous inventory is not 112 rows",
    )
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
            url
            == f"https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v0.62.15/{name}",
            f"invalid predecessor public URL: {name}",
        )
        require(name not in by_name, f"duplicate predecessor filename: {name}")
        row = {"name": name, "bytes": byte_count, "sha256": digest}
        rows.append(row)
        by_name[name] = row
    require(
        sum(int(row["bytes"]) for row in rows) == EXPECTED_PREDECESSOR_TOTAL_BYTES,
        "v0.62.15 row bytes do not reproduce the total",
    )
    require(
        inventory_aggregate(rows) == EXPECTED_PREDECESSOR_AGGREGATE,
        "v0.62.15 rows do not reproduce the aggregate",
    )
    names = set(by_name)
    require(PURE_OMISSIONS <= names, "v0.62.15 lacks a required versioned omission")
    require(SAME_NAME_REPLACEMENTS <= names, "v0.62.15 lacks the replacement filename")
    retained = frozenset(names - PURE_OMISSIONS - SAME_NAME_REPLACEMENTS)
    require(len(retained) == EXPECTED_RETAINED, "v0.62.16 retained count is not 108")
    require(
        len(retained | SAME_NAME_REPLACEMENTS | PURE_ADDITIONS) == EXPECTED_FILES,
        "v0.62.16 successor name closure is not 112",
    )
    return by_name, retained


def _validate_predecessor_directory(rows: dict[str, dict[str, Any]]) -> None:
    require(
        PREDECESSOR_DIR.is_dir() and not PREDECESSOR_DIR.is_symlink(),
        "local v0.62.15 predecessor directory is missing",
    )
    entries = list(PREDECESSOR_DIR.iterdir())
    require(len(entries) == EXPECTED_PREDECESSOR_FILES, "local predecessor is not 112 entries")
    require(
        all(path.is_file() and not path.is_symlink() for path in entries),
        "local predecessor is not flat regular files",
    )
    require({path.name for path in entries} == set(rows), "local predecessor names differ")
    observed: list[dict[str, Any]] = []
    for name in sorted(rows):
        path = PREDECESSOR_DIR / name
        data = path.read_bytes()
        expected = rows[name]
        require(
            (len(data), sha256(data)) == (expected["bytes"], expected["sha256"]),
            f"local predecessor bytes differ: {name}",
        )
        observed.append({"name": name, "bytes": len(data), "sha256": sha256(data)})
    require(
        inventory_aggregate(observed) == EXPECTED_PREDECESSOR_AGGREGATE,
        "local predecessor aggregate differs",
    )


def _validate_source_delta(source_commit: str, source_tree: str) -> dict[str, Any]:
    require(source_commit == EXPECTED_SOURCE_COMMIT, "source commit differs from the bounded correction commit")
    require(source_tree == EXPECTED_SOURCE_TREE, "source tree differs from the bounded correction tree")
    validate_source_authority(source_commit, source_tree)
    parent = run_git_bytes(
        ["rev-parse", "--verify", f"{source_commit}^{{commit}}^"],
        "resolve correction parent",
    ).decode("ascii", errors="strict").strip()
    require(parent == EXPECTED_SOURCE_PARENT, "correction commit parent differs")
    raw = run_git_bytes(
        ["diff-tree", "--no-commit-id", "--name-only", "-r", "-z", source_commit],
        "inspect bounded correction paths",
    )
    changed = frozenset(
        part.decode("utf-8", errors="strict") for part in raw.rstrip(b"\0").split(b"\0") if part
    )
    require(changed == EXPECTED_SOURCE_CHANGED_PATHS, "correction commit changed paths differ")

    index_path = PROJECT / "docs/index.html"
    peta_path = PROJECT / "docs/peta-belajar-luring.html"
    index_data = index_path.read_bytes()
    peta_data = peta_path.read_bytes()
    require_committed_bytes(source_commit, index_path, index_data, "docs/index.html")
    require_committed_bytes(source_commit, peta_path, peta_data, "docs/peta-belajar-luring.html")
    for label, data in (("docs/index.html", index_data), ("docs/peta-belajar-luring.html", peta_data)):
        privacy_scan(label, data)
        text = data.decode("utf-8", errors="strict")
        require("1 September 2026" in text, f"canonical update date is absent: {label}")
        require(
            "Kesembilan ikatan kini memiliki replay publik lengkap pada snapshot pusat." in text,
            f"corrected nine-binding narrative is absent: {label}",
        )
        require(
            "C30, C40, C80, dan C130 diterima lokal dan menunggu rilis pusat penerus" not in text,
            f"stale pending-publication narrative remains: {label}",
        )
    return {
        "commit": source_commit,
        "tree": source_tree,
        "parent": parent,
        "changed_paths": sorted(changed),
        "correction_scope": "narrative_and_date_only",
    }


def _notes(source: dict[str, Any]) -> bytes:
    text = f"""# Program Matematika Indonesia v0.62.16

Rilis koreksi ini mempertahankan 108 aset v0.62.15 secara byte-identik,
mengganti hanya `peta-belajar-luring.html`, menghilangkan hanya tiga berkas
rilis berversi v0.62.15, dan menambah tiga berkas rilis berversi v0.62.16.
Hasilnya tetap tepat 112 aset datar dengan 111 baris checksum.

Koreksi menyelaraskan tanggal keadaan kanon dan narasi replay adapter pada
halaman utama serta peta belajar luring. Kesembilan ikatan peran melalui delapan
paket adapter telah memiliki replay publik lengkap pada snapshot pusat. Tidak
ada isi kurikulum, paket adapter, kapsul kursus, atau bukti edisi yang diganti.

Arsip sumber adalah `git archive --format=zip` deterministik dari commit
`{source['source_commit']}` dan tree `{source['source_tree']}`. Komentar ZIP
mengikat commit itu. Arsip berukuran {source['bytes']} byte dengan SHA-256
`{source['sha256']}`.

Provenans model: OpenAI Codex gpt-5.6-sol, Ultra.
"""
    return text.replace("\r\n", "\n").encode("utf-8")


def _checksum_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    ordered = sorted(rows, key=lambda row: str(row["name"]))
    require(len(ordered) == EXPECTED_CHECKSUM_ROWS, "pre-checksum inventory is not 111 files")
    require(
        len({str(row["name"]) for row in ordered}) == EXPECTED_CHECKSUM_ROWS,
        "duplicate pre-checksum filename",
    )
    return "".join(f"{row['sha256']}  {row['name']}\n" for row in ordered).encode("utf-8")


def _assemble(destination: Path, source_commit: str, source_tree: str) -> list[dict[str, Any]]:
    require(destination.is_dir() and not any(destination.iterdir()), "staging directory is not empty")
    predecessor, retained = _predecessor_inventory()
    _validate_predecessor_directory(predecessor)
    source_delta = _validate_source_delta(source_commit, source_tree)

    rows: list[dict[str, Any]] = []
    for name in sorted(retained):
        data = (PREDECESSOR_DIR / name).read_bytes()
        (destination / name).write_bytes(data)
        rows.append(fact(name, data, "retained_exact_from_v0.62.15"))

    for name, path in sorted(REPLACEMENT_SOURCES.items()):
        data = path.read_bytes()
        require_committed_bytes(source_commit, path, data, name)
        privacy_scan(name, data)
        expected = predecessor[name]
        require(
            (len(data), sha256(data)) != (expected["bytes"], expected["sha256"]),
            f"declared replacement is byte-identical to v0.62.15: {name}",
        )
        (destination / name).write_bytes(data)
        rows.append(fact(name, data, "commit_bound_v0.62.16_correction", path))

    source_data, source_details = build_source_archive(source_commit, source_tree)
    source_row = fact(SOURCE_ZIP_NAME, source_data, "deterministic_git_archive_of_explicit_commit")
    source_row.update(source_details)
    source_row["source_delta"] = source_delta
    (destination / SOURCE_ZIP_NAME).write_bytes(source_data)
    rows.append(source_row)

    notes = _notes(source_row)
    privacy_scan(NOTES_NAME, notes)
    (destination / NOTES_NAME).write_bytes(notes)
    rows.append(fact(NOTES_NAME, notes, "generated_release_notes"))
    require(len(rows) == EXPECTED_CHECKSUM_ROWS, "108+1+1+1 pre-checksum equation differs")

    checksum = _checksum_bytes(rows)
    (destination / CHECKSUM_NAME).write_bytes(checksum)
    rows.append(fact(CHECKSUM_NAME, checksum, "generated_release_checksum"))
    rows.sort(key=lambda row: str(row["name"]))
    _validate_staged(destination, rows)
    return rows


def _validate_staged(directory: Path, rows: list[dict[str, Any]]) -> None:
    require(len(rows) == EXPECTED_FILES, "final inventory is not 112 rows")
    entries = list(directory.iterdir())
    require(len(entries) == EXPECTED_FILES, "staged release is not 112 entries")
    require(
        all(path.is_file() and not path.is_symlink() for path in entries),
        "staged release is not flat regular files",
    )
    expected = {str(row["name"]): row for row in rows}
    require({path.name for path in entries} == set(expected), "staged name closure differs")
    observed: list[dict[str, Any]] = []
    for name in sorted(expected):
        data = (directory / name).read_bytes()
        row = expected[name]
        require(
            (len(data), sha256(data)) == (row["bytes"], row["sha256"]),
            f"staged bytes differ: {name}",
        )
        observed.append({"name": name, "bytes": len(data), "sha256": sha256(data)})
    checksum = (directory / CHECKSUM_NAME).read_bytes()
    require(
        checksum == _checksum_bytes(row for row in observed if row["name"] != CHECKSUM_NAME),
        "checksum readback differs",
    )


def _summary(status: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_name = {str(row["name"]): row for row in rows}
    source = by_name[SOURCE_ZIP_NAME]
    checksum = by_name[CHECKSUM_NAME]
    notes = by_name[NOTES_NAME]
    replacement = by_name["peta-belajar-luring.html"]
    return {
        "status": status,
        "version": VERSION,
        "output": OUTPUT_DIR.relative_to(PROJECT).as_posix(),
        "predecessor": {
            "version": PREDECESSOR_VERSION,
            "files": EXPECTED_PREDECESSOR_FILES,
            "bytes": EXPECTED_PREDECESSOR_TOTAL_BYTES,
            "aggregate_sha256": EXPECTED_PREDECESSOR_AGGREGATE,
            "receipt_bytes": EXPECTED_PREDECESSOR_RECEIPT[0],
            "receipt_sha256": EXPECTED_PREDECESSOR_RECEIPT[1],
        },
        "boundary": {
            "retained_exact": EXPECTED_RETAINED,
            "same_name_replacements": EXPECTED_REPLACEMENTS,
            "pure_omissions": EXPECTED_PURE_OMISSIONS,
            "pure_additions": EXPECTED_PURE_ADDITIONS,
            "successor_files": EXPECTED_FILES,
            "replacement_names": sorted(SAME_NAME_REPLACEMENTS),
            "omission_names": sorted(PURE_OMISSIONS),
            "addition_names": sorted(PURE_ADDITIONS),
        },
        "files": EXPECTED_FILES,
        "bytes": sum(int(row["bytes"]) for row in rows),
        "inventory_aggregate_sha256": inventory_aggregate(rows),
        "checksum": {"rows": EXPECTED_CHECKSUM_ROWS, "bytes": checksum["bytes"], "sha256": checksum["sha256"]},
        "release_notes": {"bytes": notes["bytes"], "sha256": notes["sha256"]},
        "replacement": {"name": replacement["name"], "bytes": replacement["bytes"], "sha256": replacement["sha256"]},
        "source_archive": {
            "name": SOURCE_ZIP_NAME,
            "bytes": source["bytes"],
            "sha256": source["sha256"],
            "commit": source["source_commit"],
            "tree": source["source_tree"],
            "zip_comment": source["zip_comment"],
            "zip_files": source["zip_files"],
            "source_delta": source["source_delta"],
        },
    }


def _compare_existing(expected_dir: Path, rows: list[dict[str, Any]]) -> None:
    require(OUTPUT_DIR.is_dir() and not OUTPUT_DIR.is_symlink(), "existing v0.62.16 output is not a regular directory")
    entries = list(OUTPUT_DIR.iterdir())
    require(len(entries) == EXPECTED_FILES, "existing v0.62.16 count differs")
    require(all(path.is_file() and not path.is_symlink() for path in entries), "existing v0.62.16 is not flat regular files")
    names = {str(row["name"]) for row in rows}
    require({path.name for path in entries} == names, "existing v0.62.16 names differ")
    for name in sorted(names):
        require(
            (OUTPUT_DIR / name).read_bytes() == (expected_dir / name).read_bytes(),
            f"existing v0.62.16 bytes differ: {name}",
        )


def _run_preflight(source_commit: str, source_tree: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="pmi-v0.62.16-preflight-") as temporary:
        stage = Path(temporary)
        rows = _assemble(stage, source_commit, source_tree)
        if OUTPUT_DIR.exists():
            _compare_existing(stage, rows)
            return _summary("PASS_EXISTING_BYTE_IDENTICAL", rows)
        return _summary("PASS_PREFLIGHT_READY", rows)


def _safe_remove_build_temp(path: Path) -> None:
    require(
        path.parent.resolve() == RELEASES_DIR.resolve()
        and path.name.startswith(BUILD_PREFIX)
        and path != OUTPUT_DIR,
        "unsafe build temp path",
    )
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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True, help="exact bounded correction commit")
    parser.add_argument("--source-tree", required=True, help="exact tree of the correction commit")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true", help="assemble and validate only in a temporary directory")
    modes.add_argument("--build", action="store_true", help="atomically assemble releases/v0.62.16")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = (
            _run_preflight(args.source_commit, args.source_tree)
            if args.preflight
            else _run_build(args.source_commit, args.source_tree)
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0
    except (BuildError, RuntimeError, OSError) as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(
            json.dumps({"status": "FAIL_CLOSED", "version": VERSION, "error": detail}, sort_keys=True, separators=(",", ":")),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
