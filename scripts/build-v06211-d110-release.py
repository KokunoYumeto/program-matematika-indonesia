#!/usr/bin/env python3
"""Assemble the exact cap-compatible v0.62.11 D110 backend release."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
PREDECESSOR_DIR = PROJECT / "releases/v0.62.10"
PREDECESSOR_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.10.json"
SOURCE_RECEIPT = PROJECT / "GITHUB_D110_V231_SOURCE_PUBLICATION_RECEIPT.json"
OUTPUT_DIR = PROJECT / "releases/v0.62.11"
LOGBOOK = WORKSPACE / "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook"
ASSEMBLY_RECEIPT = LOGBOOK / "186_D110_V231_RELEASE_ASSEMBLY_V06211_20260830.json"
OMITTED = {
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.3.html",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.3.sha256",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.3.json",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.3.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.3.zip",
    "RELEASE_CHECKSUMS_v0.62.9.sha256",
    "RELEASE_NOTES_v0.62.9.md",
}
ADDITIVE_SOURCES = {
    "program-matematika-indonesia-backend-v2.3.1-d110-adapter-v0.1.0.zip": PROJECT / "backend/v2.3/builds/d110_v23_adapter_release/program-matematika-indonesia-backend-v2.3.1-d110-adapter-v0.1.0.zip",
    "183_D110_V231_ADAPTER_VALIDATION_V010_FINAL_20260830.json": LOGBOOK / "183_D110_V231_ADAPTER_VALIDATION_V010_FINAL_20260830.json",
    "184_D110_V231_ADAPTER_CANONICAL_ADMISSION_20260830.json": LOGBOOK / "184_D110_V231_ADAPTER_CANONICAL_ADMISSION_20260830.json",
    "185_D110_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260830.json": LOGBOOK / "185_D110_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260830.json",
    "GITHUB_D110_V231_SOURCE_PUBLICATION_RECEIPT.json": SOURCE_RECEIPT,
}
EXPECTED_ADDITIONS = {
    "program-matematika-indonesia-backend-v2.3.1-d110-adapter-v0.1.0.zip": (14097074, "bfd554c0d459787ea0ccde0c2de1f22264705d2dffa20061fa2525095b83287b"),
    "183_D110_V231_ADAPTER_VALIDATION_V010_FINAL_20260830.json": (3231, "8ce318222e0e78bd5153fa966cff1156f6366751893c6fce09f8464c4bccce81"),
    "184_D110_V231_ADAPTER_CANONICAL_ADMISSION_20260830.json": (2217, "a64c9a575e421304dbddf705649de2067c4667c859ddf2dd1db7a825badc29be"),
    "185_D110_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260830.json": (1636, "f8701b7e3722e23ae34c1607eb8990190e1e51a1b59e6cac2655d97bc826c490"),
    "GITHUB_D110_V231_SOURCE_PUBLICATION_RECEIPT.json": (53080, "14d70f942fd5a6d733cfdc8720fad9523562c47b3a1612b1100fffede5e2e922"),
}
NOTES_NAME = "RELEASE_NOTES_v0.62.11.md"
CHECKSUM_NAME = "RELEASE_CHECKSUMS_v0.62.11.sha256"
SOURCE_COMMIT = "2f0e52280791854f904475e5f92392f52745ea24"
SOURCE_TREE = "af8d0254ca0132fc5c8c8622052e4b50b9392fff"


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fact(name: str, data: bytes, provenance: str) -> dict[str, object]:
    return {"name": name, "bytes": len(data), "sha256": sha256(data), "provenance": provenance}


def aggregate(rows: list[dict[str, object]]) -> str:
    return sha256("".join(f"{row['sha256']}  {row['name']}\n" for row in sorted(rows, key=lambda x: str(x["name"]))).encode("utf-8"))


def privacy_scan(name: str, data: bytes) -> None:
    lowered = data.lower()
    require(b"c:\\users\\" not in lowered, f"absolute profile path in {name}")
    require(b"access_token=" not in lowered, f"credential query in {name}")
    require(re.search(rb"github_pat_[a-z0-9_]{20,}|ghp_[a-z0-9]{20,}", lowered) is None, f"credential pattern in {name}")
    profile = Path.home().name.encode("utf-8", errors="ignore").lower()
    if profile:
        require(profile not in lowered, f"profile identifier in {name}")


def notes() -> bytes:
    return """# Program Matematika Indonesia v0.62.11 — Adapter backend D110 v2.3.1

Mulai belajar dari situs siswa, bukan dari berkas mesin:

- https://kokunoyumeto.github.io/program-matematika-indonesia/

Rilis aditif ini mempertahankan tampilan siswa v0.62.8 dan seluruh artefak adapter A00, B10, serta D60 yang masih berlaku, lalu menambahkan adapter backend lintas-korpus v2.3.1 untuk D110, *Matematika dalam Lean*. Rute utama D110 tetap pembaca HTML semantik berbahasa Indonesia di https://kokunoyumeto.github.io/mathematics-in-lean-id/; PDF adalah unduhan sekunder, sedangkan JSON, JSONL, CSV, dan ZIP adapter adalah infrastruktur mesin.

Adapter D110 memvalidasi 41.460 rekaman kanonik, 19 tabel JSONL dengan proyeksi CSV lossless, 1.213 ikatan konten sumber/target, 2.177 baris status terjemahan berbukti, 9.272 pemetaan native reversibel, dan 9.272 penetapan hak komponen. Ia mempertahankan 10.978 rekaman native pemilik secara zero-copy, mengikat 1.706 rekaman tambahan melalui hash shard, tidak menyalin prosa buku, dan tidak meratakan hak komponen.

## Batas klaim

- A00, B10, D60, dan D110 adalah empat bukti jalur; 36 peran lain tidak diklaim sesuai v2.3.1.
- Identitas native `urn:mil:*`, graf relasi prasyarat, status aset draf, serta perbedaan antara latihan pelajar dan demonstrasi solusi yang sengaja memakai Lean `sorry` dipertahankan secara eksplisit.
- Locale native `und` tidak diperlakukan sebagai bukti status terjemahan menyeluruh.
- PDF D110 tidak bertanda; HTML semantik tetap permukaan aksesibilitas dan tujuan belajar utama.

## Tampilan pengganti yang kompatibel dengan batas Zenodo

Zenodo membatasi satu record hingga 100 berkas. Payload ini mempertahankan 93 berkas v0.62.10, menghilangkan hanya lima artefak overlay v0.62.3 dan dua berkas metadata v0.62.9 yang tetap terbuka pada versi pendahulu, lalu menambahkan tujuh artefak v0.62.11. Hasilnya tepat 100 berkas; tidak ada record pendahulu yang diubah, ditutup, atau dibatasi.

## Provenans model

OpenAI Codex gpt-5.6-sol, Ultra. Semua kredit sumber, penulis, dan kontributor manusia yang diwarisi tetap dipertahankan.

Codex, atas instruksi pengguna.
""".replace("\r\n", "\n").encode("utf-8")


def main() -> None:
    require(PREDECESSOR_RECEIPT.is_file() and PREDECESSOR_DIR.is_dir(), "verified predecessor missing")
    require(not OUTPUT_DIR.exists(), "v0.62.11 exists; refusing overwrite")
    predecessor = json.loads(PREDECESSOR_RECEIPT.read_text(encoding="utf-8"))
    require(predecessor.get("version") == "0.62.10", "predecessor version drift")
    require(predecessor.get("state") == "published_open_cap_compatible_backend_successor", "predecessor state drift")
    payload = predecessor.get("payload_inventory")
    require(isinstance(payload, list) and len(payload) == 100, "predecessor inventory is not 100 files")
    by_name = {str(row["name"]): row for row in payload}
    require(len(by_name) == 100 and OMITTED < set(by_name), "omission boundary not present")
    retained = sorted(set(by_name) - OMITTED)
    require(len(retained) == 93, "retained boundary is not 93")

    source_receipt = json.loads(SOURCE_RECEIPT.read_text(encoding="utf-8"))
    require(source_receipt.get("status") == "PASS", "D110 source receipt not PASS")
    require(source_receipt.get("source_commit") == SOURCE_COMMIT and source_receipt.get("source_tree") == SOURCE_TREE, "D110 source authority drift")
    require(source_receipt.get("bounded_file_count") == 71, "D110 source snapshot count drift")
    require(source_receipt.get("anonymous_raw_readback", {}).get("files") == 71, "D110 raw readback count drift")
    require(source_receipt.get("anonymous_pages_readback", {}).get("files") == 3, "D110 Pages readback count drift")

    for name, path in ADDITIVE_SOURCES.items():
        require(path.is_file(), f"missing additive source: {name}")
        data = path.read_bytes()
        expected_bytes, expected_sha = EXPECTED_ADDITIONS[name]
        require(len(data) == expected_bytes and sha256(data) == expected_sha, f"additive identity drift: {name}")

    build = Path(tempfile.mkdtemp(prefix=".v0.62.11-build-", dir=PROJECT / "releases"))
    complete = False
    try:
        rows: list[dict[str, object]] = []
        for name in retained:
            source = PREDECESSOR_DIR / name
            data = source.read_bytes()
            expected = by_name[name]
            require(len(data) == int(expected["bytes"]) and sha256(data) == expected["sha256"], f"retained identity drift: {name}")
            privacy_scan(name, data)
            (build / name).write_bytes(data)
            rows.append(fact(name, data, "retained_exact_from_v0.62.10"))
        additions: list[str] = []
        for name, source in sorted(ADDITIVE_SOURCES.items()):
            data = source.read_bytes()
            privacy_scan(name, data)
            (build / name).write_bytes(data)
            rows.append(fact(name, data, "d110_v2.3.1_additive"))
            additions.append(name)
        note_bytes = notes()
        privacy_scan(NOTES_NAME, note_bytes)
        (build / NOTES_NAME).write_bytes(note_bytes)
        rows.append(fact(NOTES_NAME, note_bytes, "d110_v2.3.1_additive"))
        additions.append(NOTES_NAME)
        checksums = "".join(f"{row['sha256']}  {row['name']}\n" for row in sorted(rows, key=lambda x: str(x["name"]))).encode("utf-8")
        (build / CHECKSUM_NAME).write_bytes(checksums)
        rows.append(fact(CHECKSUM_NAME, checksums, "d110_v2.3.1_additive"))
        additions.append(CHECKSUM_NAME)
        require(len(additions) == 7 and len(rows) == 100 and len(list(build.iterdir())) == 100, "final 100-file boundary failed")
        final = sorted(rows, key=lambda x: str(x["name"]))
        receipt = {
            "schema_id": "program-matematika-indonesia/v06211-d110-release-assembly/1.0.0",
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "state": "assembled_validated_not_yet_published",
            "version": "0.62.11",
            "predecessor": {"version": "0.62.10", "record_id": 22178332, "files": 100, "aggregate_sha256": predecessor["payload_inventory_aggregate_sha256"]},
            "replacement_boundary": {"retained_exact_files": 93, "omitted_preserved_in_public_predecessor": sorted(OMITTED), "additive_files": 7, "final_files": 100, "zenodo_file_cap": 100},
            "source_publication": {"commit": SOURCE_COMMIT, "tree": SOURCE_TREE, "raw_readback": "PASS_71_OF_71", "pages_readback": "PASS_3_OF_3"},
            "inventory": final,
            "inventory_aggregate_sha256": aggregate(final),
            "total_bytes": sum(int(row["bytes"]) for row in final),
            "learner_primary_url": "https://kokunoyumeto.github.io/program-matematika-indonesia/",
            "d110_learner_url": "https://kokunoyumeto.github.io/mathematics-in-lean-id/",
            "machine_backend_is_secondary": True,
            "aggregate_40_role_conformance_claim": False,
            "accepted_lane_proofs": ["A00", "B10", "D60", "D110"],
            "other_course_roles_unbound": 36,
            "overall_program_complete": False,
            "privacy": {"credentials": 0, "absolute_profile_paths": 0, "personal_names": 0},
            "model_provenance": "OpenAI Codex gpt-5.6-sol, Ultra",
        }
        ASSEMBLY_RECEIPT.write_bytes((json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
        build.rename(OUTPUT_DIR)
        complete = True
        print(json.dumps({"status": "PASS", "files": 100, "bytes": receipt["total_bytes"], "inventory_sha256": receipt["inventory_aggregate_sha256"], "receipt": ASSEMBLY_RECEIPT.relative_to(WORKSPACE).as_posix(), "receipt_bytes": ASSEMBLY_RECEIPT.stat().st_size, "receipt_sha256": sha256(ASSEMBLY_RECEIPT.read_bytes())}, separators=(",", ":")))
    finally:
        if not complete and build.exists():
            require(build.parent.resolve() == (PROJECT / "releases").resolve() and build.name.startswith(".v0.62.11-build-"), "unsafe transient path")
            shutil.rmtree(build)


if __name__ == "__main__":
    main()
