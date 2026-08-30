#!/usr/bin/env python3
"""Check or assemble the exact 100-file v0.62.12 method/capsule release.

The release is intentionally cap-compatible:

* retain 81 files byte-for-byte from the verified v0.62.11 payload;
* omit 19 superseded files that remain public in the predecessor record;
* add 17 externally prepared artifacts;
* generate deterministic release notes; and
* generate one release-specific checksum file after those notes exist.

This script does not create publication, source-readback, methodology, or
learner-delivery receipts.  Missing external artifacts are reported and cause
a fail-closed exit.  ``--build`` writes through a temporary directory and
refuses to overwrite an existing v0.62.12 directory.  With no arguments the
script performs the read-only readiness check.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
PREDECESSOR_DIR = PROJECT / "releases/v0.62.11"
PREDECESSOR_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.11.json"
OUTPUT_DIR = PROJECT / "releases/v0.62.12"
LOGBOOK = WORKSPACE / "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook"
D20_EXTENSION_ROOT = PROJECT / "backend/v2.3/extensions/d20-functional-analysis-v0.1.0"
D20_ADAPTER_ZIP = (
    PROJECT
    / "backend/v2.3/builds/d20_v23_adapter_release/program-matematika-indonesia-backend-v2.3.1-d20-adapter-v0.1.0.zip"
)

EXPECTED_PREDECESSOR_RECEIPT = (
    49_882,
    "8429373d0a7974537723b82e75a08d9e0bc8fabcd21d408eea3fb012394f3921",
)
EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE = (
    "b6067743eb2e1426e26c871b18cb2239aebb36c9d81f7ecbfcc57d53f1976187"
)
EXPECTED_PREDECESSOR_TOTAL_BYTES = 98_006_299

OMITTED = {
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.4.html",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.4.sha256",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.4.json",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.4.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.4.zip",
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.5.html",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.5.sha256",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.5.json",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.5.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.5.zip",
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.6.html",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.6.sha256",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.6.json",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.6.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.6.zip",
    "RELEASE_CHECKSUMS_v0.62.10.sha256",
    "RELEASE_NOTES_v0.62.10.md",
    "CHECKSUMS.sha256",
    "RELEASE_NOTES_v0.62.0.md",
}

ADDITIVE_SOURCES = {
    "program-matematika-indonesia-backend-v2.3.1-d20-adapter-v0.1.0.zip": (
        D20_ADAPTER_ZIP
    ),
    "191_D20_V231_ADAPTER_VALIDATION_V010_FINAL_20260831.json": (
        LOGBOOK / "191_D20_V231_ADAPTER_VALIDATION_V010_FINAL_20260831.json"
    ),
    "192_D20_V231_ADAPTER_CANONICAL_ADMISSION_20260831.json": (
        LOGBOOK / "192_D20_V231_ADAPTER_CANONICAL_ADMISSION_20260831.json"
    ),
    "193_D20_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260831.json": (
        LOGBOOK / "193_D20_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260831.json"
    ),
    "GITHUB_D20_V231_SOURCE_PUBLICATION_RECEIPT.json": (
        PROJECT / "GITHUB_D20_V231_SOURCE_PUBLICATION_RECEIPT.json"
    ),
    "learner-delivery-v1.json": PROJECT / "backend/authority/learner-delivery-v1.json",
    "learner-delivery-v1.schema.json": PROJECT / "schemas/v1/learner-delivery-v1.schema.json",
    "peta-belajar-luring.html": PROJECT / "docs/peta-belajar-luring.html",
    "190_LEARNER_ACCESS_OFFLINE_DELIVERY_TRANCHE_20260830.json": (
        LOGBOOK / "190_LEARNER_ACCESS_OFFLINE_DELIVERY_TRANCHE_20260830.json"
    ),
    "194_GLOBAL_MODULAR_BACKEND_LEARNER_DELIVERY_INTEGRATION_20260831.json": (
        LOGBOOK / "194_GLOBAL_MODULAR_BACKEND_LEARNER_DELIVERY_INTEGRATION_20260831.json"
    ),
    "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md": (
        PROJECT / "MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md"
    ),
    "modular-backend-pattern-index-v1.json": (
        PROJECT / "backend/authority/modular-backend-pattern-index-v1.json"
    ),
    "program-matematika-indonesia-course-capsule-v1.zip": (
        PROJECT
        / "backend/course-capsule-v1/builds/program-matematika-indonesia-course-capsule-v1.zip"
    ),
    "course-capsules-v1.jsonl": (
        PROJECT / "backend/course-capsule-v1/generated/course-capsules.jsonl"
    ),
    "course-capsule-v1.schema.json": (
        PROJECT / "docs/schema/course-capsule-v1/course-capsule-v1.schema.json"
    ),
    "v23-adapter-index-v1.json": PROJECT / "backend/authority/v23-adapter-index-v1.json",
    "v23-adapter-index-v1.schema.json": PROJECT / "schemas/v1/v23-adapter-index-v1.schema.json",
}

NOTES_NAME = "RELEASE_NOTES_v0.62.12.md"
CHECKSUM_NAME = "RELEASE_CHECKSUMS_v0.62.12.sha256"

# These five inputs were already sealed before this release builder was added.
# The later publication receipt, final methodology receipt, generated learner
# surfaces, capsule, indexes, schemas, and notes remain current-byte inputs and
# are measured at assembly time rather than assigned invented future hashes.
FIXED_EXPECTED = {
    "program-matematika-indonesia-backend-v2.3.1-d20-adapter-v0.1.0.zip": (
        61_438_875,
        "25e059d26f049141dad326817bd01319b120a19fc4b78fb2efc879764fea2099",
    ),
    "190_LEARNER_ACCESS_OFFLINE_DELIVERY_TRANCHE_20260830.json": (
        5_034,
        "2f29a8f2ba6d6eb855862b416814ffbc720b0f4250125ca1dcf9502414097cc1",
    ),
    "191_D20_V231_ADAPTER_VALIDATION_V010_FINAL_20260831.json": (
        3_706,
        "d5236d85114369642fee2d939bbddd9f1c5990a8941b6a644897e85b4d7ee5a7",
    ),
    "192_D20_V231_ADAPTER_CANONICAL_ADMISSION_20260831.json": (
        2_793,
        "7cf570937da52eb9d77768f35cb92ae4c6baaabdfe97fb63bc59ddef2a2713ac",
    ),
    "193_D20_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260831.json": (
        1_648,
        "d3af747ca7a67ddaad7a1a5aaa0fab5fa4eded7cd21806d0fdd064a3140938d0",
    ),
}


class BuildError(RuntimeError):
    """A deterministic boundary or validation failure."""


def require(value: bool, message: str) -> None:
    if not value:
        raise BuildError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative_display(path: Path) -> str:
    try:
        return path.resolve().relative_to(WORKSPACE.resolve()).as_posix()
    except ValueError:
        return path.name


def fact(name: str, data: bytes, provenance: str) -> dict[str, Any]:
    return {
        "name": name,
        "bytes": len(data),
        "sha256": sha256(data),
        "provenance": provenance,
    }


def inventory_aggregate(rows: list[dict[str, Any]]) -> str:
    material = "".join(
        f"{row['sha256']}  {row['name']}\n"
        for row in sorted(rows, key=lambda item: str(item["name"]))
    ).encode("utf-8")
    return sha256(material)


def release_notes() -> bytes:
    return """# Program Matematika Indonesia v0.62.12 — Metode backend modular dan kapsul kursus

Mulai belajar dari situs siswa, bukan dari berkas mesin:

- https://kokunoyumeto.github.io/program-matematika-indonesia/

Rilis aditif ini mempertahankan permukaan belajar publik yang sudah ada dan menambahkan empat lapisan yang saling melengkapi: adapter backend v2.3.1 untuk D20, catatan metode serta indeks pola dari perbandingan 33 keluarga backend, kapsul kursus lintas-program, dan inventaris pengantaran pelajar termasuk navigator HTML satu-berkas untuk penggunaan luring. Berkas JSON, JSONL, skema, dan ZIP merupakan infrastruktur mesin; halaman siswa dan pembaca masing-masing kursus tetap merupakan pintu masuk belajar.

Metodenya sengaja tidak memaksa 40 korpus memakai satu bentuk internal sejak awal. Setiap pemilik korpus mempertahankan format, identitas, hak komponen, serta pipeline native yang dapat direproduksi. Hasil-hasil native kemudian dibandingkan, kemampuan yang benar-benar sama dipetakan ke lapisan tipis bersama, dan perbedaan yang tidak lossless tetap dinyatakan sebagai batas atau ekstensi. Dokumen metode, indeks 33 keluarga, indeks adapter v2.3, dan kapsul kursus dalam rilis ini membuat keputusan tersebut dapat diaudit dan dipakai ulang.

Adapter D20 menambah bukti implementasi terverifikasi kelima bersama A00, B10, D60, dan D110. Ia tidak mengubah backend native D20 dan tidak mengklaim bahwa peran lain sudah sesuai: adapter adalah pemetaan aditif dengan identitas, provenance, relasi, status terjemahan, rute pembaca, dan hak komponen yang tetap dapat dilacak kembali.

## Batas penggantian 100 berkas

Payload ini mempertahankan 81 berkas v0.62.11 secara byte-identik, menghilangkan dari versi terbaru hanya 15 artefak overlay v0.62.4–v0.62.6 serta empat berkas metadata lama yang tetap terbuka pada versi pendahulu, lalu menambahkan 19 artefak v0.62.12. Hasilnya tepat 100 berkas; tidak ada record pendahulu yang diubah, ditutup, atau dibatasi.

## Provenans model

OpenAI Codex gpt-5.6-sol, Ultra. Semua kredit sumber, penulis, dan kontributor manusia yang diwarisi tetap dipertahankan.

Codex, atas instruksi pengguna.
""".replace("\r\n", "\n").encode("utf-8")


def privacy_scan(name: str, data: bytes) -> None:
    lowered = data.lower()
    require(b"c:\\users\\" not in lowered, f"absolute profile path in {name}")
    require(b"access_token=" not in lowered, f"credential query in {name}")
    require(b"authorization: bearer" not in lowered, f"credential header in {name}")
    require(
        re.search(rb"github_pat_[a-z0-9_]{20,}|ghp_[a-z0-9]{20,}", lowered) is None,
        f"credential pattern in {name}",
    )
    profile = Path.home().name.encode("utf-8", errors="ignore").lower()
    if profile:
        require(profile not in lowered, f"profile identifier in {name}")


def validate_json(name: str, data: bytes) -> Any:
    try:
        return json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"invalid JSON in {name}: {exc}") from exc


def validate_jsonl(name: str, data: bytes) -> int:
    try:
        lines = [line for line in data.decode("utf-8-sig").splitlines() if line.strip()]
    except UnicodeDecodeError as exc:
        raise BuildError(f"invalid UTF-8 JSONL in {name}: {exc}") from exc
    require(lines, f"empty JSONL input: {name}")
    for number, line in enumerate(lines, start=1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BuildError(f"invalid JSONL in {name} line {number}: {exc}") from exc
        require(isinstance(value, dict), f"non-object JSONL row in {name} line {number}")
    return len(lines)


def validate_zip(name: str, path: Path) -> int:
    try:
        with zipfile.ZipFile(path, "r") as archive:
            members = archive.infolist()
            names = [member.filename for member in members]
            require(members, f"empty ZIP input: {name}")
            require(len(names) == len(set(names)), f"duplicate ZIP member in {name}")
            failed = archive.testzip()
            require(failed is None, f"ZIP CRC failure in {name}: {failed}")
            return len(members)
    except zipfile.BadZipFile as exc:
        raise BuildError(f"invalid ZIP input: {name}") from exc


def d20_extension_closure() -> dict[str, dict[str, Any]]:
    require(D20_EXTENSION_ROOT.is_dir(), "D20 canonical extension root missing")
    require(D20_ADAPTER_ZIP.is_file(), "D20 deterministic adapter ZIP missing")
    local_paths = {
        path.relative_to(D20_EXTENSION_ROOT).as_posix(): path
        for path in D20_EXTENSION_ROOT.rglob("*")
        if path.is_file()
    }
    require(len(local_paths) == 61, "D20 canonical extension is not the sealed 61-file tree")
    closure: dict[str, dict[str, Any]] = {}
    try:
        with zipfile.ZipFile(D20_ADAPTER_ZIP, "r") as archive:
            members = [member for member in archive.infolist() if not member.is_dir()]
            names = [member.filename for member in members]
            require(len(members) == 61 and len(names) == len(set(names)), "D20 ZIP closure is not 61 unique files")
            require(set(names) == set(local_paths), "D20 ZIP/local extension path closure differs")
            for member in members:
                pure = PurePosixPath(member.filename)
                require(
                    not pure.is_absolute()
                    and ".." not in pure.parts
                    and "\\" not in member.filename,
                    f"unsafe D20 ZIP member path: {member.filename}",
                )
                archived = archive.read(member)
                local = local_paths[member.filename].read_bytes()
                require(archived == local, f"D20 ZIP/local byte mismatch: {member.filename}")
                closure[member.filename] = {
                    "bytes": len(archived),
                    "sha256": sha256(archived),
                }
    except zipfile.BadZipFile as exc:
        raise BuildError("invalid D20 deterministic adapter ZIP") from exc
    return closure


def validate_source_receipt(data: bytes) -> None:
    receipt = validate_json("GITHUB_D20_V231_SOURCE_PUBLICATION_RECEIPT.json", data)
    require(isinstance(receipt, dict), "D20 source receipt is not an object")
    require(receipt.get("status") == "PASS", "D20 source receipt is not PASS")
    source_commit = str(receipt.get("source_commit", ""))
    source_tree = str(receipt.get("source_tree", ""))
    require(
        re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None
        and source_commit != "0" * 40,
        "D20 source receipt commit is not a full Git identity",
    )
    require(
        re.fullmatch(r"[0-9a-f]{40}", source_tree) is not None
        and source_tree != "0" * 40,
        "D20 source receipt tree is not a full Git identity",
    )
    require(
        receipt.get("repository") == "https://github.com/KokunoYumeto/program-matematika-indonesia",
        "D20 source receipt repository drift",
    )
    raw = receipt.get("anonymous_raw_readback")
    pages = receipt.get("anonymous_pages_readback")
    require(isinstance(raw, dict) and raw.get("result") == "PASS", "D20 raw readback is not PASS")
    require(isinstance(pages, dict) and pages.get("result") == "PASS", "D20 Pages readback is not PASS")
    raw_entries = raw.get("entries")
    page_entries = pages.get("entries")
    require(
        isinstance(raw_entries, list)
        and len(raw_entries) >= 61
        and raw.get("files") == len(raw_entries),
        "D20 raw readback count drift",
    )
    require(
        isinstance(page_entries, list)
        and len(page_entries) >= 3
        and pages.get("files") == len(page_entries),
        "D20 Pages readback count drift",
    )
    require(receipt.get("bounded_file_count") == len(raw_entries), "D20 bounded source count drift")
    raw_paths: set[str] = set()
    raw_byte_total = 0
    for entry in raw_entries:
        require(isinstance(entry, dict), "D20 raw readback entry is not an object")
        path_text = entry.get("path")
        require(isinstance(path_text, str) and path_text, "D20 raw readback path missing")
        pure = PurePosixPath(path_text)
        require(
            not pure.is_absolute()
            and ".." not in pure.parts
            and "\\" not in path_text,
            f"unsafe D20 raw readback path: {path_text}",
        )
        require(path_text not in raw_paths, f"duplicate D20 raw readback path: {path_text}")
        raw_paths.add(path_text)
        expected_bytes = entry.get("bytes")
        expected_sha = str(entry.get("sha256", ""))
        require(isinstance(expected_bytes, int) and expected_bytes > 0, f"invalid D20 raw byte count: {path_text}")
        raw_byte_total += expected_bytes
        require(
            re.fullmatch(r"[0-9a-f]{64}", expected_sha) is not None
            and expected_sha != "0" * 64,
            f"invalid D20 raw SHA-256: {path_text}",
        )
        url = entry.get("url")
        expected_url = (
            "https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia/"
            f"{source_commit}/{quote(path_text, safe='/')}"
        )
        require(
            isinstance(url, str) and url == expected_url,
            f"invalid D20 raw readback URL: {path_text}",
        )
        if "http_status" in entry:
            require(entry["http_status"] == 200, f"D20 raw HTTP status is not 200: {path_text}")
        local = (PROJECT / pure.as_posix()).resolve()
        require(local.is_relative_to(PROJECT.resolve()), f"D20 raw path escapes project: {path_text}")
        require(local.is_file(), f"D20 raw-bound local file missing: {path_text}")
        local_data = local.read_bytes()
        require(
            len(local_data) == expected_bytes and sha256(local_data) == expected_sha,
            f"D20 raw/local identity mismatch: {path_text}",
        )
    if "bounded_file_bytes" in receipt:
        require(receipt["bounded_file_bytes"] == raw_byte_total, "D20 bounded source byte total drift")
    required_d20_authorities = {
        "backend/v2.3/extensions/d20-functional-analysis-v0.1.0/manifest.json": (
            32_321,
            "a8ec1635e8b2eb4034b8be1181d9cbeb39438ff095e33e5c26e686e9ba5301e9",
        ),
        "backend/v2.3/extensions/d20-functional-analysis-v0.1.0/seal.json": (
            14_100,
            "fd0e57f6238857a364b719982eb07cd68e2c34738d35c6c2e468a69a6abbcc16",
        ),
    }
    raw_by_path = {str(entry["path"]): entry for entry in raw_entries}
    for path_text, expected in required_d20_authorities.items():
        require(path_text in raw_by_path, f"D20 authority absent from raw readback: {path_text}")
        entry = raw_by_path[path_text]
        require(
            entry.get("bytes") == expected[0] and entry.get("sha256") == expected[1],
            f"D20 authority identity drift in source receipt: {path_text}",
        )
    extension_prefix = "backend/v2.3/extensions/d20-functional-analysis-v0.1.0/"
    compact_authority_paths = {
        extension_prefix + relative
        for relative in (
            "INPUT_AUTHORITIES.json",
            "PACKAGE_CHECKSUMS.sha256",
            "README.md",
            "capability-declarations-v0.2.0.json",
            "csv-projection-manifest-v0.2.0.json",
            "manifest.json",
            "scope-declaration-v0.2.0.json",
            "seal.json",
        )
    }
    require(
        compact_authority_paths <= raw_paths,
        "D20 raw readback does not cover the compact Git authority surface",
    )
    require(
        receipt.get("distribution_boundary")
        == "compact_git_authority_plus_complete_release_zip",
        "D20 Git/release distribution boundary drift",
    )
    complete_archive = receipt.get("complete_archive")
    require(isinstance(complete_archive, dict), "D20 complete archive boundary missing")
    require(
        complete_archive.get("filename")
        == "program-matematika-indonesia-backend-v2.3.1-d20-adapter-v0.1.0.zip"
        and complete_archive.get("bytes") == 61_438_875
        and complete_archive.get("sha256")
        == "25e059d26f049141dad326817bd01319b120a19fc4b78fb2efc879764fea2099"
        and complete_archive.get("member_count") == 61
        and complete_archive.get("uncompressed_bytes") == 551_281_460,
        "D20 complete release archive identity drift",
    )
    page_paths: set[str] = set()
    for entry in page_entries:
        require(isinstance(entry, dict), "D20 Pages readback entry is not an object")
        path_text = entry.get("source_path")
        require(isinstance(path_text, str) and path_text, "D20 Pages source path missing")
        pure = PurePosixPath(path_text)
        require(
            not pure.is_absolute()
            and ".." not in pure.parts
            and "\\" not in path_text,
            f"unsafe D20 Pages source path: {path_text}",
        )
        require(path_text not in page_paths, f"duplicate D20 Pages source path: {path_text}")
        page_paths.add(path_text)
        expected_bytes = entry.get("bytes")
        expected_sha = str(entry.get("sha256", ""))
        require(isinstance(expected_bytes, int) and expected_bytes > 0, f"invalid D20 Pages byte count: {path_text}")
        require(
            re.fullmatch(r"[0-9a-f]{64}", expected_sha) is not None
            and expected_sha != "0" * 64,
            f"invalid D20 Pages SHA-256: {path_text}",
        )
        url = entry.get("url")
        require(path_text.startswith("docs/"), f"D20 Pages source is outside docs/: {path_text}")
        published_path = path_text[len("docs/") :]
        if published_path == "index.html":
            expected_url = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
        elif published_path.endswith("/index.html"):
            expected_url = (
                "https://kokunoyumeto.github.io/program-matematika-indonesia/"
                + quote(published_path[: -len("index.html")], safe="/")
            )
        else:
            expected_url = (
                "https://kokunoyumeto.github.io/program-matematika-indonesia/"
                + quote(published_path, safe="/")
            )
        require(
            isinstance(url, str) and url == expected_url,
            f"invalid D20 Pages URL: {path_text}",
        )
        if "http_status" in entry:
            require(entry["http_status"] == 200, f"D20 Pages HTTP status is not 200: {path_text}")
        local = (PROJECT / pure.as_posix()).resolve()
        require(local.is_relative_to(PROJECT.resolve()), f"D20 Pages path escapes project: {path_text}")
        require(local.is_file(), f"D20 Pages-bound local file missing: {path_text}")
        local_data = local.read_bytes()
        require(
            len(local_data) == expected_bytes and sha256(local_data) == expected_sha,
            f"D20 Pages/local identity mismatch: {path_text}",
        )
    if "credentials_recorded" in receipt:
        require(receipt["credentials_recorded"] in (0, False), "D20 source receipt records credentials")
    if "personal_name_recorded" in receipt:
        require(receipt["personal_name_recorded"] in (0, False), "D20 source receipt records a personal name")


def validate_external(name: str, path: Path, data: bytes) -> dict[str, Any]:
    privacy_scan(name, data)
    details: dict[str, Any] = {}
    if name.endswith(".json"):
        value = validate_json(name, data)
        require(isinstance(value, (dict, list)), f"unexpected JSON root in {name}")
        if name == "learner-delivery-v1.json":
            require(isinstance(value, dict), "learner-delivery authority is not an object")
            require(isinstance(value.get("courses"), list) and len(value["courses"]) == 40, "learner-delivery course boundary drift")
            require(value.get("summary", {}).get("course_count") == 40, "learner-delivery summary drift")
        elif name == "modular-backend-pattern-index-v1.json":
            require(isinstance(value, dict), "backend pattern index is not an object")
            require(isinstance(value.get("families"), list) and len(value["families"]) == 33, "33-family pattern boundary drift")
        elif name == "v23-adapter-index-v1.json":
            require(isinstance(value, dict), "v2.3 adapter index is not an object")
            summary = value.get("summary", {})
            require(isinstance(value.get("adapters"), list) and len(value["adapters"]) == 5, "v2.3 adapter proof boundary drift")
            require(
                summary.get("curriculum_roles") == 40
                and summary.get("proof_roles") == 5
                and summary.get("unbound_roles") == 35,
                "v2.3 adapter summary drift",
            )
    elif name.endswith(".jsonl"):
        details["jsonl_rows"] = validate_jsonl(name, data)
        if name == "course-capsules-v1.jsonl":
            require(details["jsonl_rows"] == 40, "course-capsule row boundary drift")
    elif name.endswith(".zip"):
        details["zip_entries"] = validate_zip(name, path)
    elif name.endswith(".html"):
        require(b"<html" in data[:4096].lower(), f"HTML document marker missing in {name}")
    elif name.endswith(".md"):
        require(data.startswith(b"#"), f"Markdown heading missing in {name}")
    require(data, f"empty additive input: {name}")
    if name == "GITHUB_D20_V231_SOURCE_PUBLICATION_RECEIPT.json":
        validate_source_receipt(data)
    expected = FIXED_EXPECTED.get(name)
    if expected is not None:
        expected_bytes, expected_sha = expected
        require(
            len(data) == expected_bytes and sha256(data) == expected_sha,
            f"sealed input identity drift: {name}",
        )
    details["source"] = relative_display(path)
    return details


def validate_predecessor() -> tuple[dict[str, dict[str, Any]], list[str]]:
    require(PREDECESSOR_DIR.is_dir(), "v0.62.11 predecessor directory missing")
    require(PREDECESSOR_RECEIPT.is_file(), "v0.62.11 publication receipt missing")
    receipt_bytes = PREDECESSOR_RECEIPT.read_bytes()
    expected_bytes, expected_sha = EXPECTED_PREDECESSOR_RECEIPT
    require(
        len(receipt_bytes) == expected_bytes and sha256(receipt_bytes) == expected_sha,
        "v0.62.11 publication receipt identity drift",
    )
    predecessor = validate_json(PREDECESSOR_RECEIPT.name, receipt_bytes)
    require(isinstance(predecessor, dict), "v0.62.11 receipt is not an object")
    require(predecessor.get("version") == "0.62.11", "predecessor version drift")
    require(
        predecessor.get("state") == "published_open_cap_compatible_backend_successor",
        "predecessor publication state drift",
    )
    require(
        predecessor.get("payload_inventory_aggregate_sha256")
        == EXPECTED_PREDECESSOR_INVENTORY_AGGREGATE,
        "predecessor inventory aggregate drift",
    )
    require(
        predecessor.get("payload_total_bytes") == EXPECTED_PREDECESSOR_TOTAL_BYTES,
        "predecessor total-byte boundary drift",
    )
    payload = predecessor.get("payload_inventory")
    require(isinstance(payload, list) and len(payload) == 100, "predecessor inventory is not 100 files")
    by_name: dict[str, dict[str, Any]] = {}
    for row in payload:
        require(isinstance(row, dict) and isinstance(row.get("name"), str), "invalid predecessor inventory row")
        name = str(row["name"])
        require(name not in by_name, f"duplicate predecessor inventory name: {name}")
        require(isinstance(row.get("bytes"), int), f"invalid predecessor byte count: {name}")
        require(re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256", ""))) is not None, f"invalid predecessor SHA-256: {name}")
        by_name[name] = row
    require(len(OMITTED) == 19 and OMITTED < set(by_name), "exact 19-file omission boundary is not present")
    retained = sorted(set(by_name) - OMITTED)
    require(len(retained) == 81, "retained predecessor boundary is not 81 files")
    actual = {path.name for path in PREDECESSOR_DIR.iterdir() if path.is_file()}
    require(actual == set(by_name), "v0.62.11 directory and publication inventory differ")
    for name, row in by_name.items():
        data = (PREDECESSOR_DIR / name).read_bytes()
        require(
            len(data) == int(row["bytes"]) and sha256(data) == row["sha256"],
            f"predecessor file identity drift: {name}",
        )
    return by_name, retained


def collect_external_facts() -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    facts: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []
    for name, path in sorted(ADDITIVE_SOURCES.items()):
        if not path.is_file():
            missing.append({"name": name, "source": relative_display(path)})
            continue
        data = path.read_bytes()
        details = validate_external(name, path, data)
        row = fact(name, data, "v0.62.12_additive_external")
        row.update(details)
        facts.append(row)
    return facts, missing


def readiness() -> tuple[dict[str, dict[str, Any]], list[str], list[dict[str, Any]]]:
    by_name, retained = validate_predecessor()
    require(len(ADDITIVE_SOURCES) == 17, "external additive boundary is not 17 files")
    require(set(ADDITIVE_SOURCES).isdisjoint(retained), "additive name collides with retained predecessor")
    require(
        NOTES_NAME not in retained
        and NOTES_NAME not in ADDITIVE_SOURCES
        and CHECKSUM_NAME not in retained
        and CHECKSUM_NAME not in ADDITIVE_SOURCES,
        "generated metadata name collision",
    )
    facts, missing = collect_external_facts()
    if missing:
        print(
            json.dumps(
                {
                    "status": "BLOCKED_MISSING_INPUTS",
                    "version": "0.62.12",
                    "retained_predecessor_files": 81,
                    "required_external_additions": 17,
                    "present_external_additions": len(facts),
                    "missing": missing,
                    "generated_release_notes": NOTES_NAME,
                    "generated_after_notes_validate": CHECKSUM_NAME,
                    "expected_final_files": 100,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        raise SystemExit(2)
    require(len(facts) == 17, "validated external additive boundary is not 17 files")
    return by_name, retained, facts


def build_release(
    by_name: dict[str, dict[str, Any]],
    retained: list[str],
    external_facts: list[dict[str, Any]],
) -> dict[str, Any]:
    require(not OUTPUT_DIR.exists(), "v0.62.12 output already exists; refusing overwrite")
    build = Path(tempfile.mkdtemp(prefix=".v0.62.12-build-", dir=PROJECT / "releases"))
    complete = False
    try:
        rows: list[dict[str, Any]] = []
        for name in retained:
            source = PREDECESSOR_DIR / name
            data = source.read_bytes()
            expected = by_name[name]
            require(
                len(data) == int(expected["bytes"]) and sha256(data) == expected["sha256"],
                f"retained identity drift during copy: {name}",
            )
            privacy_scan(name, data)
            (build / name).write_bytes(data)
            rows.append(fact(name, data, "retained_exact_from_v0.62.11"))
        source_facts = {str(row["name"]): row for row in external_facts}
        for name, source in sorted(ADDITIVE_SOURCES.items()):
            data = source.read_bytes()
            measured = source_facts[name]
            require(
                len(data) == int(measured["bytes"]) and sha256(data) == measured["sha256"],
                f"additive input changed after readiness check: {name}",
            )
            (build / name).write_bytes(data)
            rows.append(fact(name, data, "v0.62.12_additive_external"))
        note_bytes = release_notes()
        privacy_scan(NOTES_NAME, note_bytes)
        require(note_bytes.startswith(b"#"), "generated release notes lack a heading")
        (build / NOTES_NAME).write_bytes(note_bytes)
        rows.append(fact(NOTES_NAME, note_bytes, "generated_release_notes"))
        require(len(rows) == 99, "pre-checksum release boundary is not 99 files")
        checksum_bytes = "".join(
            f"{row['sha256']}  {row['name']}\n"
            for row in sorted(rows, key=lambda item: str(item["name"]))
        ).encode("utf-8")
        require(len(checksum_bytes.splitlines()) == 99, "checksum row boundary is not 99")
        (build / CHECKSUM_NAME).write_bytes(checksum_bytes)
        rows.append(fact(CHECKSUM_NAME, checksum_bytes, "generated_release_checksum"))
        require(len(rows) == 100, "final release inventory is not 100 files")
        final_names = {str(row["name"]) for row in rows}
        actual_names = {path.name for path in build.iterdir() if path.is_file()}
        require(len(final_names) == 100 and actual_names == final_names, "final release filename boundary failed")
        require(not any(path.is_dir() for path in build.iterdir()), "unexpected directory in release payload")
        for row in rows:
            data = (build / str(row["name"])).read_bytes()
            require(
                len(data) == int(row["bytes"]) and sha256(data) == row["sha256"],
                f"final release readback mismatch: {row['name']}",
            )
        build.rename(OUTPUT_DIR)
        complete = True
        final = sorted(rows, key=lambda item: str(item["name"]))
        return {
            "status": "PASS_ASSEMBLED_NOT_PUBLISHED",
            "version": "0.62.12",
            "output": relative_display(OUTPUT_DIR),
            "retained_exact_files": 81,
            "omitted_preserved_in_public_predecessor": 19,
            "external_additive_files": 17,
            "generated_release_notes_files": 1,
            "generated_checksum_files": 1,
            "files": 100,
            "bytes": sum(int(row["bytes"]) for row in final),
            "inventory_aggregate_sha256": inventory_aggregate(final),
            "checksum": fact(
                CHECKSUM_NAME,
                (OUTPUT_DIR / CHECKSUM_NAME).read_bytes(),
                "generated_release_checksum",
            ),
        }
    finally:
        if not complete and build.exists():
            require(
                build.parent.resolve() == (PROJECT / "releases").resolve()
                and build.name.startswith(".v0.62.12-build-"),
                "unsafe transient build path",
            )
            shutil.rmtree(build)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--build",
        action="store_true",
        help="assemble releases/v0.62.12 after all external inputs pass",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        by_name, retained, external_facts = readiness()
        if args.build:
            result = build_release(by_name, retained, external_facts)
        else:
            result = {
                "status": "READY_TO_BUILD" if not OUTPUT_DIR.exists() else "OUTPUT_EXISTS_REFUSE_OVERWRITE",
                "version": "0.62.12",
                "output": relative_display(OUTPUT_DIR),
                "retained_exact_files": 81,
                "omitted_preserved_in_public_predecessor": 19,
                "external_additive_files": 17,
                "generated_release_notes_files": 1,
                "generated_checksum_files": 1,
                "expected_final_files": 100,
                "external_inventory_aggregate_sha256": inventory_aggregate(external_facts),
                "generated_after_notes_validate": CHECKSUM_NAME,
            }
            if OUTPUT_DIR.exists():
                print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
                return 2
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0
    except BuildError as exc:
        print(
            json.dumps(
                {"status": "FAIL_CLOSED", "version": "0.62.12", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
