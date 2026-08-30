#!/usr/bin/env python3
"""Publish and anonymously verify PMI v0.62.11 on the existing Zenodo concept."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
TEMPLATE_SCRIPT = PROJECT / "scripts/publish-v06210-zenodo.py"

spec = importlib.util.spec_from_file_location("pmi_v06210_zenodo_template", TEMPLATE_SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load the proven v0.62.10 Zenodo publisher")
template = importlib.util.module_from_spec(spec)
spec.loader.exec_module(template)
base = template.base

RELEASE_DIR = PROJECT / "releases/v0.62.11"
ASSEMBLY_RECEIPT = WORKSPACE / "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/186_D110_V231_RELEASE_ASSEMBLY_V06211_20260830.json"
GITHUB_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.11.json"
PREDECESSOR_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.10.json"
VERSION_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.11.json"
ROOT_RECEIPT = PROJECT / "PUBLICATION_RECEIPT.json"
TOKEN_FILE_ENV = "PMI_V06211_ZENODO_TOKEN_FILE"

CONCEPT_ID = 22059707
PREDECESSOR_ID = 22178332
PREDECESSOR_VERSION = "0.62.10"
VERSION = "0.62.11"
LEARNER_FILE = "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.8.html"
LEARNER_SITE = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
GITHUB_RELEASE = "https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.11"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
USER_AGENT = "Codex-PMI-v06211-Zenodo-Publisher/1.0"

TITLE = "Program Matematika Indonesia v0.62.11 — Adapter Backend D110 v2.3.1"
DESCRIPTION = (
    '<p><strong>Mulai belajar sekarang:</strong> <a href="https://kokunoyumeto.github.io/program-matematika-indonesia/">'
    "buka halaman siswa Program Matematika Indonesia</a>. Halaman ini adalah pintu masuk manusia untuk jalur prasyarat, "
    "status mata kuliah, dan bahan belajar.</p>"
    "<p>Versi 0.62.11 mempertahankan tampilan siswa v0.62.8 dan menambahkan adapter backend lintas-korpus v2.3.1 "
    "yang tervalidasi untuk D110, <em>Matematika dalam Lean</em>. Pembaca HTML D110 di "
    '<a href="https://kokunoyumeto.github.io/mathematics-in-lean-id/">situs kursus</a> adalah jalur utama siswa; '
    "PDF adalah unduhan sekunder. Berkas JSON, CSV, dan ZIP adalah infrastruktur mesin, bukan halaman awal siswa.</p>"
    "<p>A00, B10, D60, dan D110 adalah empat bukti jalur v2.3.1. Tiga puluh enam peran lain tidak diklaim "
    "sesuai v2.3.1 dan program 40-peran keseluruhan belum lengkap.</p>"
    "<p>Payload penerus berisi tepat 100 berkas: 93 berkas publik versi 0.62.10 dipertahankan byte demi byte dan "
    "tujuh artefak v0.62.11 ditambahkan. Lima artefak overlay v0.62.3 dan dua berkas metadata v0.62.9 yang tidak "
    "diduplikasi tetap terbuka pada record pendahulu. Tidak ada record pendahulu yang diubah, ditutup, atau dibatasi.</p>"
    "<p>Hak komponen dan identitas native pemilik tidak diratakan. Paket gabungan memakai lisensi "
    "<em>other-open</em> karena tidak memiliki satu lisensi tunggal.</p>"
    "<p>Produksi, integrasi, dan QA dibantu oleh <strong>OpenAI Codex gpt-5.6-sol, Ultra</strong> atas instruksi "
    "pengguna. Semua kredit sumber, penulis, dan kontributor manusia yang diwarisi tetap dipertahankan.</p>"
)
NOTES = (
    "Rilis v0.62.11 menambahkan adapter backend D110 v2.3.1 sebagai infrastruktur mesin sekunder. "
    "Situs siswa dan pembaca HTML D110 tetap menjadi pintu masuk utama; program keseluruhan belum lengkap. "
    "Payload 100 berkas mempertahankan 93 berkas v0.62.10 dan menambahkan tujuh artefak v0.62.11."
)

OMITTED = {
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.3.html",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.3.sha256",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.3.json",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.3.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.3.zip",
    "RELEASE_CHECKSUMS_v0.62.9.sha256",
    "RELEASE_NOTES_v0.62.9.md",
}
ADDITIONS = {
    "program-matematika-indonesia-backend-v2.3.1-d110-adapter-v0.1.0.zip",
    "183_D110_V231_ADAPTER_VALIDATION_V010_FINAL_20260830.json",
    "184_D110_V231_ADAPTER_CANONICAL_ADMISSION_20260830.json",
    "185_D110_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260830.json",
    "GITHUB_D110_V231_SOURCE_PUBLICATION_RECEIPT.json",
    "RELEASE_NOTES_v0.62.11.md",
    "RELEASE_CHECKSUMS_v0.62.11.sha256",
}


for name, value in {
    "RELEASE_DIR": RELEASE_DIR,
    "ASSEMBLY_RECEIPT": ASSEMBLY_RECEIPT,
    "GITHUB_RECEIPT": GITHUB_RECEIPT,
    "PREDECESSOR_RECEIPT": PREDECESSOR_RECEIPT,
    "VERSION_RECEIPT": VERSION_RECEIPT,
    "ROOT_RECEIPT": ROOT_RECEIPT,
    "TOKEN_FILE_ENV": TOKEN_FILE_ENV,
    "CONCEPT_ID": CONCEPT_ID,
    "PREDECESSOR_ID": PREDECESSOR_ID,
    "PREDECESSOR_VERSION": PREDECESSOR_VERSION,
    "VERSION": VERSION,
    "LEARNER_FILE": LEARNER_FILE,
    "LEARNER_SITE": LEARNER_SITE,
    "GITHUB_RELEASE": GITHUB_RELEASE,
    "MODEL": MODEL,
    "USER_AGENT": USER_AGENT,
    "TITLE": TITLE,
    "DESCRIPTION": DESCRIPTION,
    "NOTES": NOTES,
    "OMITTED": OMITTED,
    "ADDITIONS": ADDITIONS,
}.items():
    setattr(template, name, value)
    setattr(base, name, value)

base_public_file_stubs = base.public_file_stubs


def public_file_stubs_v06211(record: dict, expected_count: int, label: str) -> list[dict]:
    if label.startswith("predecessor"):
        expected_count = 100
    return base_public_file_stubs(record, expected_count, label)


def predecessor_authority_v06211(local_rows: list[dict]) -> tuple[dict, dict, list[dict]]:
    record = base.public_json(f"{base.PUBLIC_API}/{PREDECESSOR_ID}")
    base.require(int(record.get("id", -1)) == PREDECESSOR_ID, "predecessor record ID differs")
    base.require(record.get("conceptdoi") == f"10.5281/zenodo.{CONCEPT_ID}", "predecessor concept differs")
    metadata = record.get("metadata", {})
    base.require(isinstance(metadata, dict), "predecessor metadata is malformed")
    base.require(metadata.get("version") == PREDECESSOR_VERSION, "predecessor version differs")
    base.require(metadata.get("access_right") == "open", "predecessor is not open")
    base.require(base.license_id(metadata) == "other-open", "predecessor license differs")
    base.require(metadata.get("language") == "ind", "predecessor language differs")
    receipt = json.loads(PREDECESSOR_RECEIPT.read_text(encoding="utf-8"))
    predecessor_rows = receipt.get("payload_inventory")
    base.require(isinstance(predecessor_rows, list) and len(predecessor_rows) == 100, "predecessor receipt inventory differs")
    expected = [
        {"name": row["name"], "bytes": int(row["bytes"]), "sha256": row["sha256"], "md5": ""}
        for row in predecessor_rows
    ]
    stubs = {row["name"]: row for row in public_file_stubs_v06211(record, 100, "predecessor-stubs")}
    for row in expected:
        base.require(row["name"] in stubs, f"predecessor missing file: {row['name']}")
        row["md5"] = stubs[row["name"]]["md5"]
    observed = base.anonymous_inventory(record, expected, "predecessor-before")
    local_names = {str(row["name"]) for row in local_rows}
    base.require({str(row["name"]) for row in expected} - local_names == OMITTED, "predecessor/local omission boundary differs")
    return record, metadata, observed


base.local_inventory = template.local_inventory
base.public_file_stubs = public_file_stubs_v06211
base.predecessor_authority = predecessor_authority_v06211
base.verify_exact_draft = template.verify_exact_draft
base.verify_final_draft_metadata = template.verify_final_draft_metadata
base.verify_rdm_learner_preview = template.verify_rdm_learner_preview
base.write_receipts = template.write_receipts
base.reuse_existing_receipts = template.reuse_existing_receipts


def correct_receipt() -> tuple[int, str]:
    receipt = json.loads(VERSION_RECEIPT.read_text(encoding="utf-8"))
    boundary = receipt["replacement_boundary"]
    boundary["predecessor_files"] = 100
    boundary["retained_exact_files"] = 93
    boundary["omitted_preserved_in_public_predecessor"] = sorted(OMITTED)
    boundary["additive_files"] = sorted(ADDITIONS)
    boundary["successor_files"] = 100
    for row in receipt["payload_inventory"]:
        row["provenance"] = "d110_v2.3.1_additive" if row["name"] in ADDITIONS else "retained_exact_from_v0.62.10"
    receipt["payload_inventory_aggregate_sha256"] = base.inventory_sha(receipt["payload_inventory"])
    receipt["accepted_lane_proofs"] = ["A00", "B10", "D60", "D110"]
    receipt["other_course_roles_unbound"] = 36
    publisher = Path(__file__).resolve()
    receipt["publisher"] = {
        "path": publisher.relative_to(PROJECT).as_posix(),
        "bytes": publisher.stat().st_size,
        "sha256": base.sha256_bytes(publisher.read_bytes()),
        "git_commands_used": 0,
    }
    receipt["recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
    data = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    for path in (VERSION_RECEIPT, ROOT_RECEIPT):
        temporary = path.with_name(f".{path.name}.tmp-v06211-final")
        temporary.write_bytes(data)
        temporary.replace(path)
    return len(data), base.sha256_bytes(data)


def main() -> None:
    base.main()
    receipt_bytes, receipt_sha = correct_receipt()
    receipt = json.loads(VERSION_RECEIPT.read_text(encoding="utf-8"))
    print(json.dumps({
        "status": "PASS_FINAL_RECEIPT",
        "record_id": receipt["zenodo"]["record_id"],
        "version_doi": receipt["zenodo"]["version_doi"],
        "concept_doi": receipt["zenodo"]["concept_doi"],
        "files": receipt["zenodo"]["file_count"],
        "receipt": VERSION_RECEIPT.relative_to(PROJECT).as_posix(),
        "receipt_bytes": receipt_bytes,
        "receipt_sha256": receipt_sha,
    }, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(f"FAIL: {type(exc).__name__}: {detail}", file=sys.stderr)
        raise SystemExit(1)
