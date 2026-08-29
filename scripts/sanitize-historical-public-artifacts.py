#!/usr/bin/env python3
"""Sanitize legacy public hub artifacts without reducing public access.

This is intentionally a narrow, fail-closed migration for the v0.41.0 and
v0.42.0 central-hub artifacts.  It removes a legacy personal attribution and
machine-local home paths, updates every derived manifest/checksum, and writes a
sanitized correction receipt.  It never contacts GitHub or Zenodo.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


SCHEMA_ID = "program-matematika-indonesia/historical-public-privacy-correction/v1"
VERSIONS = ("0.41.0", "0.42.0")
RECEIPT_NAME = "PRIVACY_CORRECTION_RECEIPT_20260829.json"
TRANSACTION_NAME = ".program-matematika-indonesia-privacy-transaction-20260829"

BACKEND_PRIVATE_MEMBERS = (
    "backend.json",
    "csv/resources.csv",
    "csv/rights.csv",
    "data/resources.jsonl",
    "data/rights.jsonl",
    "records.csv",
    "records.jsonl",
)

RELEASE_PRIVATE_FILES = (
    "releases/v0.41.0/dmoi4-id-backend-v1-migration-receipt.json",
    "releases/v0.42.0/GITHUB_PUBLICATION_RECEIPT_v0.42.0.json",
    "releases/v0.42.0/LOCAL_RELEASE_VALIDATION_v0.42.0.json",
    "releases/v0.42.0/RELEASE_NOTES_v0.42.0.md",
    "releases/v0.42.0/ZENODO_PUBLICATION_RECEIPT_v0.42.0.json",
    "releases/v0.42.0/dmoi4-id-backend-v1-migration-receipt.json",
    "releases/v0.42.0/openlogic-id-backend-v1-migration-receipt.json",
    "releases/v0.42.0/program-matematika-indonesia-catalog-v0.42.0.json",
    "releases/v0.42.0/program-matematika-indonesia-v0.42.0.html",
)

EXPECTED_LOOSE_PREIMAGE = {
    "backend/v1/program-matematika-indonesia-v0.41.0/backend.json": (2, 0),
    "backend/v1/program-matematika-indonesia-v0.41.0/csv/resources.csv": (1, 0),
    "backend/v1/program-matematika-indonesia-v0.41.0/csv/rights.csv": (1, 0),
    "backend/v1/program-matematika-indonesia-v0.41.0/data/resources.jsonl": (1, 0),
    "backend/v1/program-matematika-indonesia-v0.41.0/data/rights.jsonl": (1, 0),
    "backend/v1/program-matematika-indonesia-v0.41.0/records.csv": (2, 0),
    "backend/v1/program-matematika-indonesia-v0.41.0/records.jsonl": (2, 0),
    "backend/v1/program-matematika-indonesia-v0.42.0/backend.json": (2, 0),
    "backend/v1/program-matematika-indonesia-v0.42.0/csv/resources.csv": (1, 0),
    "backend/v1/program-matematika-indonesia-v0.42.0/csv/rights.csv": (1, 0),
    "backend/v1/program-matematika-indonesia-v0.42.0/data/resources.jsonl": (1, 0),
    "backend/v1/program-matematika-indonesia-v0.42.0/data/rights.jsonl": (1, 0),
    "backend/v1/program-matematika-indonesia-v0.42.0/records.csv": (2, 0),
    "backend/v1/program-matematika-indonesia-v0.42.0/records.jsonl": (2, 0),
    "releases/v0.41.0/dmoi4-id-backend-v1-migration-receipt.json": (2, 2),
    "releases/v0.42.0/GITHUB_PUBLICATION_RECEIPT_v0.42.0.json": (1, 0),
    "releases/v0.42.0/LOCAL_RELEASE_VALIDATION_v0.42.0.json": (3, 3),
    "releases/v0.42.0/RELEASE_NOTES_v0.42.0.md": (1, 0),
    "releases/v0.42.0/ZENODO_PUBLICATION_RECEIPT_v0.42.0.json": (1, 0),
    "releases/v0.42.0/dmoi4-id-backend-v1-migration-receipt.json": (2, 2),
    "releases/v0.42.0/openlogic-id-backend-v1-migration-receipt.json": (2, 2),
    "releases/v0.42.0/program-matematika-indonesia-catalog-v0.42.0.json": (1, 0),
    "releases/v0.42.0/program-matematika-indonesia-v0.42.0.html": (1, 0),
}

EXPECTED_ARCHIVE_PREIMAGE = {
    "releases/v0.41.0/program-matematika-indonesia-backend-v1-v0.41.0.zip": {
        "program-matematika-indonesia-backend-v1/backend.json": (2, 0),
        "program-matematika-indonesia-backend-v1/csv/resources.csv": (1, 0),
        "program-matematika-indonesia-backend-v1/csv/rights.csv": (1, 0),
        "program-matematika-indonesia-backend-v1/data/resources.jsonl": (1, 0),
        "program-matematika-indonesia-backend-v1/data/rights.jsonl": (1, 0),
        "program-matematika-indonesia-backend-v1/records.csv": (2, 0),
        "program-matematika-indonesia-backend-v1/records.jsonl": (2, 0),
    },
    "releases/v0.41.0/program-matematika-indonesia-source-v0.41.0.zip": {
        "backend/migrations/dmoi4-id-v1/MIGRATION_RECEIPT.json": (2, 2),
        "scripts/export-curriculum-backend-v1.py": (2, 0),
    },
    "releases/v0.42.0/program-matematika-indonesia-backend-v1-v0.42.0.zip": {
        "program-matematika-indonesia-backend-v1/backend.json": (2, 0),
        "program-matematika-indonesia-backend-v1/csv/resources.csv": (1, 0),
        "program-matematika-indonesia-backend-v1/csv/rights.csv": (1, 0),
        "program-matematika-indonesia-backend-v1/data/resources.jsonl": (1, 0),
        "program-matematika-indonesia-backend-v1/data/rights.jsonl": (1, 0),
        "program-matematika-indonesia-backend-v1/records.csv": (2, 0),
        "program-matematika-indonesia-backend-v1/records.jsonl": (2, 0),
    },
    "releases/v0.42.0/program-matematika-indonesia-source-v0.42.0.zip": {
        "README.md": (1, 0),
        "RELEASE_NOTES_v0.42.0.md": (1, 0),
        "backend/migrations/dmoi4-id-v1/MIGRATION_RECEIPT.json": (2, 2),
        "backend/migrations/openlogic-id-v1/MIGRATION_RECEIPT.json": (2, 2),
        "docs/courses.js": (1, 0),
        "program-matematika-indonesia-catalog-v0.42.0.json": (1, 0),
        "public/hub/courses.js": (1, 0),
        "scripts/export-curriculum-backend-v1.py": (2, 0),
    },
}

TEXT_SUFFIXES = {
    ".csv",
    ".html",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".mjs",
    ".py",
    ".sha256",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

PROGRAM_HOME_RE = re.compile(
    r"C:[/\\]Users[/\\][^/\\\"]+[/\\]Documents[/\\]interlanguage[/\\]"
    r"04_mirrors[/\\]id[/\\]program-matematika-indonesia[/\\]",
    flags=re.IGNORECASE,
)
DMOI_HOME_RE = re.compile(
    r"C:[/\\]Users[/\\][^/\\\"]+[/\\]Documents[/\\]interlanguage[/\\]"
    r"04_mirrors[/\\]id[/\\]discrete-mathematics-open-introduction-id[/\\]"
    r"repo[/\\]",
    flags=re.IGNORECASE,
)
ANY_INTERLANGUAGE_HOME_RE = re.compile(
    r"C:[/\\]Users[/\\][^/\\\"]+[/\\]Documents[/\\]interlanguage[/\\]",
    flags=re.IGNORECASE,
)


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_fact(path: Path, root: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def require_root(root: Path) -> None:
    expected = "program-matematika-indonesia"
    if root.name != expected:
        raise ValueError(f"refusing unexpected repository root: {root}")
    required = (
        root / "scripts" / "validate-backend-v1.py",
        root / "scripts" / "write-release-checksums.py",
        root / "schemas" / "backend-v1.schema.json",
        root / ".git",
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"repository markers missing: {missing}")


def private_token() -> str:
    token = os.environ.get("USERNAME") or Path.home().name
    if not token or token.lower() in {"runner", "user", "users"}:
        raise ValueError("a concrete local private token is required")
    return token


def count_token(text: str, token: str) -> int:
    return len(re.findall(re.escape(token), text, flags=re.IGNORECASE))


def target_text_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for relative in (
        "backend/v1/program-matematika-indonesia-v0.41.0",
        "backend/v1/program-matematika-indonesia-v0.42.0",
        "releases/v0.41.0",
        "releases/v0.42.0",
    ):
        directory = root / relative
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                paths.append(path)
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def scan_loose_preimage(root: Path, token: str) -> dict[str, tuple[int, int]]:
    hits: dict[str, tuple[int, int]] = {}
    for path in target_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        name_count = count_token(text, token)
        path_count = len(ANY_INTERLANGUAGE_HOME_RE.findall(text))
        if name_count or path_count:
            hits[path.relative_to(root).as_posix()] = (name_count, path_count)
    return hits


def scan_archive_preimage(
    root: Path, token: str
) -> dict[str, dict[str, tuple[int, int]]]:
    result: dict[str, dict[str, tuple[int, int]]] = {}
    for archive_relative in EXPECTED_ARCHIVE_PREIMAGE:
        archive_path = root / archive_relative
        hits: dict[str, tuple[int, int]] = {}
        with zipfile.ZipFile(archive_path, "r") as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError(f"corrupt ZIP member: {archive_path}!/{bad}")
            for info in archive.infolist():
                if info.is_dir() or Path(info.filename).suffix.lower() not in TEXT_SUFFIXES:
                    continue
                try:
                    text = archive.read(info.filename).decode("utf-8")
                except UnicodeDecodeError:
                    continue
                name_count = count_token(text, token)
                path_count = len(ANY_INTERLANGUAGE_HOME_RE.findall(text))
                if name_count or path_count:
                    hits[info.filename] = (name_count, path_count)
        result[archive_relative] = hits
    return result


def require_exact_preimage(root: Path, token: str) -> dict[str, object]:
    loose = scan_loose_preimage(root, token)
    archives = scan_archive_preimage(root, token)
    if loose != EXPECTED_LOOSE_PREIMAGE:
        raise ValueError(
            "loose private-data preimage differs from the frozen 23-file locator/count manifest"
        )
    if archives != EXPECTED_ARCHIVE_PREIMAGE:
        raise ValueError(
            "archive private-data preimage differs from the frozen four-archive locator/count manifest"
        )
    return {
        "loose_files": len(loose),
        "loose_name_occurrences": sum(value[0] for value in loose.values()),
        "loose_local_path_occurrences": sum(value[1] for value in loose.values()),
        "archives": len(archives),
        "archive_entries": sum(len(value) for value in archives.values()),
        "archive_name_occurrences": sum(
            counts[0] for entries in archives.values() for counts in entries.values()
        ),
        "archive_local_path_occurrences": sum(
            counts[1] for entries in archives.values() for counts in entries.values()
        ),
        "private_token_recorded": False,
    }


def sanitize_text(text: str, token: str, locator: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}

    text, counts["dmoi_home_paths"] = DMOI_HOME_RE.subn(
        "source-repository://discrete-mathematics-open-introduction-id/", text
    )
    text, counts["program_home_paths"] = PROGRAM_HOME_RE.subn(
        "repository://program-matematika-indonesia/", text
    )

    escaped = re.escape(token)
    substitutions = (
        (
            "creator_name",
            re.compile(
                rf"{escaped} and the local Codex production workflows",
                flags=re.IGNORECASE,
            ),
            "Program Matematika Indonesia and the local Codex production workflows",
        ),
        (
            "program_attribution",
            re.compile(
                rf"{escaped}\s+—\s+Program Matematika Indonesia",
                flags=re.IGNORECASE,
            ),
            "Program Matematika Indonesia",
        ),
        (
            "english_instruction_attribution",
            re.compile(rf"{escaped}'s instructions", flags=re.IGNORECASE),
            "the user's instructions",
        ),
        (
            "indonesian_instruction_attribution",
            re.compile(rf"atas instruksi {escaped}\b", flags=re.IGNORECASE),
            "atas instruksi pengguna",
        ),
    )
    for key, pattern, replacement in substitutions:
        text, counts[key] = pattern.subn(replacement, text)

    remaining = count_token(text, token)
    if remaining:
        raise ValueError(
            f"unhandled private-token occurrence(s) in {locator}: {remaining}"
        )
    if ANY_INTERLANGUAGE_HOME_RE.search(text):
        raise ValueError(f"unhandled absolute interlanguage home path in {locator}")
    return text, {key: value for key, value in counts.items() if value}


def sanitize_file(path: Path, token: str, locator: str) -> dict[str, object]:
    before = path.read_bytes()
    text = before.decode("utf-8")
    before_matches = count_token(text, token)
    after_text, replacements = sanitize_text(text, token, locator)
    after = after_text.encode("utf-8")
    path.write_bytes(after)
    return {
        "locator": locator,
        "before_matches": before_matches,
        "replacements": replacements,
        "changed": before != after,
    }


def update_backend_manifest(package: Path) -> None:
    manifest_path = package / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        member = package / entry["path"]
        if not member.is_file():
            raise FileNotFoundError(f"manifest member missing: {member}")
        entry["bytes"] = member.stat().st_size
        entry["sha256"] = sha256_file(member)
    manifest_path.write_bytes(canonical_json(manifest))


def package_inventory(package: Path) -> list[tuple[str, int, str]]:
    rows = []
    for path in sorted(candidate for candidate in package.rglob("*") if candidate.is_file()):
        if path.name == "validation_report.json":
            continue
        rows.append(
            (
                path.relative_to(package).as_posix(),
                path.stat().st_size,
                sha256_file(path),
            )
        )
    return rows


def transform_backend_package(package: Path, token: str) -> list[dict[str, object]]:
    evidence = []
    for relative in BACKEND_PRIVATE_MEMBERS:
        member = package / relative
        if not member.is_file():
            raise FileNotFoundError(member)
        evidence.append(sanitize_file(member, token, relative))
    update_backend_manifest(package)
    return evidence


def copy_zip_info(info: zipfile.ZipInfo) -> zipfile.ZipInfo:
    clone = zipfile.ZipInfo(info.filename, date_time=info.date_time)
    clone.compress_type = info.compress_type
    clone.comment = info.comment
    clone.extra = info.extra
    clone.create_system = info.create_system
    clone.create_version = info.create_version
    clone.extract_version = info.extract_version
    clone.flag_bits = info.flag_bits
    clone.internal_attr = info.internal_attr
    clone.external_attr = info.external_attr
    clone.volume = info.volume
    return clone


def write_zip_from_payloads(
    output: Path,
    infos: list[zipfile.ZipInfo],
    payloads: dict[str, bytes],
) -> None:
    with zipfile.ZipFile(output, "w", allowZip64=True) as archive:
        for info in infos:
            clone = copy_zip_info(info)
            data = payloads.get(info.filename, b"")
            archive.writestr(clone, data)


def build_backend_zip(source_zip: Path, package: Path, output: Path) -> dict[str, int]:
    prefix = "program-matematika-indonesia-backend-v1/"
    with zipfile.ZipFile(source_zip, "r") as archive:
        infos = archive.infolist()
    payloads: dict[str, bytes] = {}
    expected_files = {
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_file()
    }
    observed_files: set[str] = set()
    for info in infos:
        if info.is_dir():
            payloads[info.filename] = b""
            continue
        if not info.filename.startswith(prefix):
            raise ValueError(f"unexpected backend ZIP member: {info.filename}")
        relative = info.filename[len(prefix) :]
        observed_files.add(relative)
        payloads[info.filename] = (package / relative).read_bytes()
    if observed_files != expected_files:
        raise ValueError(
            "backend ZIP/package inventory mismatch "
            f"missing={sorted(expected_files-observed_files)} "
            f"extra={sorted(observed_files-expected_files)}"
        )
    write_zip_from_payloads(output, infos, payloads)
    return {"entries": len(infos), "files": len(observed_files)}


def build_source_zip(
    source_zip: Path,
    output: Path,
    token: str,
) -> tuple[dict[str, int], list[dict[str, object]]]:
    with zipfile.ZipFile(source_zip, "r") as archive:
        infos = archive.infolist()
        payloads = {info.filename: archive.read(info.filename) for info in infos if not info.is_dir()}
    manifest_name = "SOURCE_MANIFEST.json"
    if manifest_name not in payloads:
        raise ValueError(f"source ZIP manifest missing: {source_zip}")

    evidence: list[dict[str, object]] = []
    for info in infos:
        if info.is_dir() or info.filename == manifest_name:
            continue
        if Path(info.filename).suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = payloads[info.filename].decode("utf-8")
        except UnicodeDecodeError:
            continue
        before_matches = count_token(text, token)
        after_text, replacements = sanitize_text(
            text, token, f"{source_zip.name}!/{info.filename}"
        )
        payloads[info.filename] = after_text.encode("utf-8")
        if before_matches or replacements:
            evidence.append(
                {
                    "entry": info.filename,
                    "before_matches": before_matches,
                    "replacements": replacements,
                }
            )

    manifest = json.loads(payloads[manifest_name].decode("utf-8"))
    manifest_paths = {entry["path"] for entry in manifest["files"]}
    payload_paths = {
        info.filename for info in infos if not info.is_dir() and info.filename != manifest_name
    }
    if manifest_paths != payload_paths:
        raise ValueError("source ZIP manifest inventory mismatch before rewrite")
    for entry in manifest["files"]:
        data = payloads[entry["path"]]
        entry["bytes"] = len(data)
        entry["sha256"] = sha256_bytes(data)
    payloads[manifest_name] = canonical_json(manifest)
    write_zip_from_payloads(output, infos, payloads)
    return {"entries": len(infos), "manifest_entries": len(manifest_paths)}, evidence


def deterministic_zip_replace(builder, source: Path, *args) -> dict[str, object]:
    first = source.with_name(source.name + ".privacy-first.tmp")
    second = source.with_name(source.name + ".privacy-second.tmp")
    for temp in (first, second):
        if temp.exists():
            raise FileExistsError(f"refusing existing temporary ZIP: {temp}")
    try:
        result_first = builder(source, first, *args)
        result_second = builder(source, second, *args)
        if sha256_file(first) != sha256_file(second):
            raise ValueError(f"nondeterministic ZIP rewrite: {source}")
        if result_first != result_second:
            raise ValueError(f"nondeterministic ZIP evidence: {source}")
        os.replace(first, source)
        return {
            "sha256": sha256_file(source),
            "bytes": source.stat().st_size,
            "result": result_first,
        }
    finally:
        for temp in (first, second):
            if temp.exists():
                temp.unlink()


def backend_zip_builder(source: Path, output: Path, package: Path):
    return build_backend_zip(source, package, output)


def source_zip_builder(source: Path, output: Path, token: str):
    return build_source_zip(source, output, token)


def run(command: list[str], cwd: Path) -> None:
    completed = subprocess.run(command, cwd=cwd, check=False, text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command}\n"
            f"stdout={completed.stdout[-2000:]}\nstderr={completed.stderr[-2000:]}"
        )


def update_local_validation(root: Path, version: str) -> None:
    release = root / "releases" / f"v{version}"
    path = release / f"LOCAL_RELEASE_VALIDATION_v{version}.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    report = json.loads(
        (
            root
            / "backend"
            / "v1"
            / f"program-matematika-indonesia-v{version}"
            / "validation_report.json"
        ).read_text(encoding="utf-8")
    )
    value["checks"]["backend"] = report["checks"]
    for entry in value["files_before_checksum"]:
        member = release / entry["name"]
        if not member.is_file():
            raise FileNotFoundError(member)
        entry["bytes"] = member.stat().st_size
        entry["sha256"] = sha256_file(member)
    path.write_bytes(canonical_json(value))


def write_historical_checksums(release: Path) -> dict[str, object]:
    """Refresh the original v0.41/v0.42 checksum inventory in place.

    Those inventories predate the learner-first release convention enforced by
    the current general checksum writer.  Their exact filename set is itself
    historical evidence, so this function preserves the existing set and order
    and updates only the hashes.
    """

    checksum_path = release / "CHECKSUMS.sha256"
    original_lines = checksum_path.read_text(encoding="utf-8").splitlines()
    names: list[str] = []
    for line in original_lines:
        if not line:
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise ValueError(f"malformed historical checksum line: {line!r}")
        names.append(parts[1])
    if len(names) != len(set(names)):
        raise ValueError(f"duplicate historical checksum filename in {release}")
    for name in names:
        member = release / name
        if not member.is_file():
            raise FileNotFoundError(member)
    payload = "".join(f"{sha256_file(release / name)}  {name}\n" for name in names)
    checksum_path.write_text(payload, encoding="utf-8", newline="\n")
    return {"entries": len(names), "sha256": sha256_file(checksum_path)}


def verify_historical_checksums(release: Path) -> dict[str, object]:
    checksum_path = release / "CHECKSUMS.sha256"
    lines = checksum_path.read_text(encoding="utf-8").splitlines()
    checked = 0
    for line in lines:
        if not line:
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            raise ValueError(f"malformed historical checksum line: {line!r}")
        expected, name = parts
        member = release / name
        if not member.is_file() or sha256_file(member) != expected:
            raise ValueError(f"historical checksum mismatch: {member}")
        checked += 1
    return {"entries": checked, "result": "pass"}


def validate_no_private_text(root: Path, token: str) -> dict[str, int]:
    checked = 0
    for path in target_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if count_token(text, token) or ANY_INTERLANGUAGE_HOME_RE.search(text):
            raise ValueError(
                f"private text remains in {path.relative_to(root).as_posix()}"
            )
        checked += 1
    return {"files": checked}


def validate_no_private_archives(root: Path, token: str) -> dict[str, int]:
    archives = []
    entries = 0
    for version in VERSIONS:
        archives.extend(
            (
                root
                / "releases"
                / f"v{version}"
                / f"program-matematika-indonesia-backend-v1-v{version}.zip",
                root
                / "releases"
                / f"v{version}"
                / f"program-matematika-indonesia-source-v{version}.zip",
            )
        )
    for archive_path in archives:
        with zipfile.ZipFile(archive_path, "r") as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError(f"corrupt ZIP member: {archive_path}!/{bad}")
            for info in archive.infolist():
                if info.is_dir() or Path(info.filename).suffix.lower() not in TEXT_SUFFIXES:
                    continue
                try:
                    text = archive.read(info.filename).decode("utf-8")
                except UnicodeDecodeError:
                    continue
                if count_token(text, token) or ANY_INTERLANGUAGE_HOME_RE.search(text):
                    raise ValueError(
                        f"private text remains in {archive_path.name}!/{info.filename}"
                    )
                entries += 1
    return {"archives": len(archives), "text_entries": entries}


def mutation_candidates(root: Path) -> list[Path]:
    paths: list[Path] = []
    for version in VERSIONS:
        package = root / "backend" / "v1" / f"program-matematika-indonesia-v{version}"
        paths.extend(package / relative for relative in BACKEND_PRIVATE_MEMBERS)
        paths.extend((package / "manifest.json", package / "validation_report.json"))
        release = root / "releases" / f"v{version}"
        paths.extend(
            (
                release / f"program-matematika-indonesia-backend-v1-v{version}.zip",
                release / f"program-matematika-indonesia-source-v{version}.zip",
                release / f"program-matematika-indonesia-backend-v1-validation-v{version}.json",
                release / f"LOCAL_RELEASE_VALIDATION_v{version}.json",
                release / "CHECKSUMS.sha256",
            )
        )
    paths.extend(root / relative for relative in RELEASE_PRIVATE_FILES)
    unique = {path.resolve(): path for path in paths}
    return sorted(unique.values(), key=lambda path: path.relative_to(root).as_posix())


def apply_correction(
    root: Path,
    token: str,
    recorded_at: str,
    receipt: Path,
    source_commit_override: str | None = None,
) -> dict:
    if receipt.exists():
        raise FileExistsError(f"refusing to overwrite receipt: {receipt}")

    preimage = require_exact_preimage(root, token)
    candidates = mutation_candidates(root)
    before = {path: file_fact(path, root) for path in candidates}
    source_commit = source_commit_override or subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()

    evidence: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="pmi-privacy-backend-") as temporary:
        temp_root = Path(temporary)
        for version in VERSIONS:
            package = root / "backend" / "v1" / f"program-matematika-indonesia-v{version}"
            first = temp_root / f"v{version}-first"
            second = temp_root / f"v{version}-second"
            shutil.copytree(package, first)
            shutil.copytree(package, second)
            first_evidence = transform_backend_package(first, token)
            second_evidence = transform_backend_package(second, token)
            if first_evidence != second_evidence or package_inventory(first) != package_inventory(second):
                raise ValueError(f"nondeterministic backend transformation for v{version}")
            for relative in (*BACKEND_PRIVATE_MEMBERS, "manifest.json"):
                shutil.copyfile(first / relative, package / relative)
            evidence.extend(
                {"scope": f"backend-v{version}", **row} for row in first_evidence
            )

            report = package / "validation_report.json"
            run(
                [
                    os.fspath(Path(os.sys.executable)),
                    "-B",
                    os.fspath(root / "scripts" / "validate-backend-v1.py"),
                    "--package",
                    os.fspath(package),
                    "--schema",
                    os.fspath(root / "schemas" / "backend-v1.schema.json"),
                    "--replay-package",
                    os.fspath(second),
                    "--report",
                    os.fspath(report),
                ],
                root,
            )
            shutil.copyfile(
                report,
                root
                / "releases"
                / f"v{version}"
                / f"program-matematika-indonesia-backend-v1-validation-v{version}.json",
            )

    for relative in RELEASE_PRIVATE_FILES:
        row = sanitize_file(root / relative, token, relative)
        evidence.append({"scope": "release-text", **row})

    archive_evidence: list[dict[str, object]] = []
    for version in VERSIONS:
        release = root / "releases" / f"v{version}"
        package = root / "backend" / "v1" / f"program-matematika-indonesia-v{version}"
        backend_zip = release / f"program-matematika-indonesia-backend-v1-v{version}.zip"
        source_zip = release / f"program-matematika-indonesia-source-v{version}.zip"
        archive_evidence.append(
            {
                "archive": backend_zip.relative_to(root).as_posix(),
                **deterministic_zip_replace(backend_zip_builder, backend_zip, package),
            }
        )
        archive_evidence.append(
            {
                "archive": source_zip.relative_to(root).as_posix(),
                **deterministic_zip_replace(source_zip_builder, source_zip, token),
            }
        )

    for version in VERSIONS:
        update_local_validation(root, version)
        release = root / "releases" / f"v{version}"
        write_historical_checksums(release)
        verify_historical_checksums(release)

    text_validation = validate_no_private_text(root, token)
    archive_validation = validate_no_private_archives(root, token)
    after = {path: file_fact(path, root) for path in candidates}
    changed = []
    for path in candidates:
        if before[path] != after[path]:
            changed.append({"before": before[path], "after": after[path]})

    result = {
        "schema_id": SCHEMA_ID,
        "recorded_at": recorded_at,
        "state": "local_public_replacement_bytes_sanitized",
        "source_commit_before_correction": source_commit,
        "scope": {
            "versions": [f"v{version}" for version in VERSIONS],
            "loose_private_files_expected": 23,
            "archives_rewritten": 4,
            "curriculum_or_mathematical_content_changed": False,
        },
        "replacement_policy": {
            "personal_attribution": "generic user attribution",
            "machine_local_paths": "repository-relative or source-repository URIs",
            "private_token_recorded": False,
        },
        "frozen_preimage": preimage,
        "public_access": {
            "access_reduction_performed": False,
            "github_or_zenodo_mutation_performed_by_this_script": False,
            "historical_remote_bytes_still_require_provider-level correction": True,
        },
        "transform_evidence": evidence,
        "archive_evidence": archive_evidence,
        "changed_files": changed,
        "validation": {
            "backend_v1": "pass_v0.41.0_and_v0.42.0_with_deterministic_replay",
            "release_checksums": "pass_v0.41.0_and_v0.42.0",
            "private_text": text_validation,
            "private_archives": archive_validation,
            "result": "pass",
        },
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_bytes(canonical_json(result))
    return result


def transactional_apply(
    root: Path, token: str, recorded_at: str, receipt: Path
) -> dict:
    """Stage, validate, and durably swap the bounded historical correction."""

    transaction = root.parent / TRANSACTION_NAME
    recover_transaction_if_needed(root, receipt, transaction)
    if transaction.exists():
        raise FileExistsError(f"unresolved transaction directory: {transaction}")

    candidates = mutation_candidates(root)
    source_commit = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    backup_root = transaction / "backup"
    stage_root = transaction / "stage" / root.name
    journal_path = transaction / "JOURNAL.json"
    before_facts = [file_fact(path, root) for path in candidates]
    journal: dict[str, object] = {
        "schema_id": "program-matematika-indonesia/privacy-transaction-journal/v1",
        "state": "initializing",
        "repository": root.name,
        "receipt_name": receipt.name,
        "receipt_existed_before": receipt.exists(),
        "source_commit": source_commit,
        "candidate_preimages": before_facts,
        "swapped_paths": [],
    }
    if receipt.exists():
        raise FileExistsError(f"refusing to overwrite receipt: {receipt}")
    transaction.mkdir(parents=False)
    write_journal(journal_path, journal)

    for path in candidates:
        relative = path.relative_to(root)
        destination = backup_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    for relative in (
        "backend/v1/program-matematika-indonesia-v0.41.0",
        "backend/v1/program-matematika-indonesia-v0.42.0",
        "releases/v0.41.0",
        "releases/v0.42.0",
    ):
        shutil.copytree(root / relative, stage_root / relative)
    for relative in (
        "scripts/validate-backend-v1.py",
        "scripts/write-release-checksums.py",
        "schemas/backend-v1.schema.json",
    ):
        source = root / relative
        destination = stage_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    journal["state"] = "staged_preimage"
    write_journal(journal_path, journal)

    try:
        stage_receipt = stage_root / receipt.name
        result = apply_correction(
            stage_root,
            token,
            recorded_at,
            stage_receipt,
            source_commit_override=source_commit,
        )
        verify_only(stage_root, token)
        stage_facts = [file_fact(stage_root / path.relative_to(root), stage_root) for path in candidates]
        journal["state"] = "stage_validated"
        journal["candidate_postimages"] = stage_facts
        write_journal(journal_path, journal)

        journal["state"] = "swapping"
        write_journal(journal_path, journal)
        swapped: list[str] = []
        for path in candidates:
            relative = path.relative_to(root)
            staged = stage_root / relative
            os.replace(staged, path)
            swapped.append(relative.as_posix())
            journal["swapped_paths"] = list(swapped)
            write_journal(journal_path, journal)
        os.replace(stage_receipt, receipt)
        journal["receipt_swapped"] = True
        write_journal(journal_path, journal)

        live_verification = verify_only(root, token)
        for expected in stage_facts:
            live = root / str(expected["path"])
            if file_fact(live, root) != expected:
                raise ValueError(f"post-swap file mismatch: {expected['path']}")
        journal["state"] = "complete"
        journal["live_verification"] = live_verification
        write_journal(journal_path, journal)
        remove_transaction_directory(root, transaction)
        return result
    except BaseException:
        restore_transaction(root, receipt, transaction, journal_path)
        raise


def write_journal(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    payload = canonical_json(value)
    with temporary.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def remove_transaction_directory(root: Path, transaction: Path) -> None:
    resolved = transaction.resolve()
    if resolved.parent != root.parent.resolve() or resolved.name != TRANSACTION_NAME:
        raise ValueError(f"refusing transaction cleanup outside fixed sibling: {resolved}")
    shutil.rmtree(resolved)


def restore_transaction(
    root: Path, receipt: Path, transaction: Path, journal_path: Path
) -> None:
    if not journal_path.is_file():
        raise RuntimeError(f"transaction exists without recovery journal: {transaction}")
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    if journal.get("state") == "initializing":
        for expected in journal["candidate_preimages"]:
            destination = root / str(expected["path"])
            if file_fact(destination, root) != expected:
                raise RuntimeError(
                    f"live file changed during transaction initialization: {expected['path']}"
                )
        remove_transaction_directory(root, transaction)
        return
    backup_root = transaction / "backup"
    expected_facts = journal["candidate_preimages"]
    for expected in expected_facts:
        relative = Path(str(expected["path"]))
        backup = backup_root / relative
        destination = root / relative
        if not backup.is_file():
            raise RuntimeError(f"transaction backup missing: {backup}")
        replacement = destination.with_name(destination.name + ".privacy-restore.tmp")
        shutil.copyfile(backup, replacement)
        os.replace(replacement, destination)
    if not bool(journal.get("receipt_existed_before")) and receipt.exists():
        receipt.unlink()
    for expected in expected_facts:
        destination = root / str(expected["path"])
        if file_fact(destination, root) != expected:
            raise RuntimeError(f"transaction rollback mismatch: {expected['path']}")
    journal["state"] = "rolled_back"
    write_journal(journal_path, journal)
    remove_transaction_directory(root, transaction)


def recover_transaction_if_needed(
    root: Path, receipt: Path, transaction: Path
) -> None:
    if not transaction.exists():
        return
    journal_path = transaction / "JOURNAL.json"
    if not journal_path.is_file():
        require_exact_preimage(root, private_token())
        remove_transaction_directory(root, transaction)
        return
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    if journal.get("state") == "complete":
        verify_only(root, private_token())
        remove_transaction_directory(root, transaction)
        return
    restore_transaction(root, receipt, transaction, journal_path)


def verify_receipt_postimages(root: Path) -> dict[str, int]:
    receipt = root / RECEIPT_NAME
    if not receipt.is_file():
        raise FileNotFoundError(f"privacy correction receipt missing: {receipt}")
    value = json.loads(receipt.read_text(encoding="utf-8"))
    if value.get("schema_id") != SCHEMA_ID or value.get("validation", {}).get("result") != "pass":
        raise ValueError("privacy correction receipt schema/result mismatch")
    changed = value.get("changed_files")
    if not isinstance(changed, list) or len(changed) != 36:
        raise ValueError("privacy correction receipt must bind exactly 36 changed files")
    seen: set[str] = set()
    for row in changed:
        expected = row["after"]
        relative = str(expected["path"])
        if relative in seen:
            raise ValueError(f"duplicate receipt postimage path: {relative}")
        seen.add(relative)
        if file_fact(root / relative, root) != expected:
            raise ValueError(f"receipt postimage mismatch: {relative}")
    return {"files": len(seen)}


def verify_only(root: Path, token: str) -> dict:
    text_validation = validate_no_private_text(root, token)
    archive_validation = validate_no_private_archives(root, token)
    for version in VERSIONS:
        package = root / "backend" / "v1" / f"program-matematika-indonesia-v{version}"
        with tempfile.TemporaryDirectory(prefix="pmi-privacy-replay-") as temporary:
            replay = Path(temporary) / "package"
            shutil.copytree(package, replay)
            report = Path(temporary) / "validation.json"
            run(
                [
                    os.fspath(Path(os.sys.executable)),
                    "-B",
                    os.fspath(root / "scripts" / "validate-backend-v1.py"),
                    "--package",
                    os.fspath(package),
                    "--schema",
                    os.fspath(root / "schemas" / "backend-v1.schema.json"),
                    "--replay-package",
                    os.fspath(replay),
                    "--report",
                    os.fspath(report),
                ],
                root,
            )
        release = root / "releases" / f"v{version}"
        verify_historical_checksums(release)
    receipt_validation = verify_receipt_postimages(root)
    return {
        "result": "pass",
        "private_text": text_validation,
        "private_archives": archive_validation,
        "receipt_postimages": receipt_validation,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--apply", action="store_true")
    group.add_argument("--verify-only", action="store_true")
    parser.add_argument("--recorded-at")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    require_root(root)
    token = private_token()
    if args.apply:
        if not args.recorded_at or not args.receipt:
            parser.error("--apply requires --recorded-at and --receipt")
        receipt = args.receipt.resolve()
        if receipt.parent != root:
            raise ValueError("privacy receipt must be written at repository root")
        result = transactional_apply(root, token, args.recorded_at, receipt)
    else:
        result = verify_only(root, token)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
