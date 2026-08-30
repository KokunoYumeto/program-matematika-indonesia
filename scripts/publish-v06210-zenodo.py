#!/usr/bin/env python3
"""Publish and anonymously verify PMI v0.62.10 on the existing Zenodo concept."""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
BASE_SCRIPT = PROJECT / "scripts/publish-v0629-zenodo.py"

spec = importlib.util.spec_from_file_location("pmi_v0629_zenodo_base", BASE_SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load the proven v0.62.9 Zenodo publisher")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

RELEASE_DIR = PROJECT / "releases/v0.62.10"
ASSEMBLY_RECEIPT = (
    WORKSPACE
    / "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/178_D60_V231_RELEASE_ASSEMBLY_V06210_20260830.json"
)
GITHUB_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.10.json"
PREDECESSOR_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.9.json"
VERSION_RECEIPT = PROJECT / "PUBLICATION_RECEIPT_v0.62.10.json"
ROOT_RECEIPT = PROJECT / "PUBLICATION_RECEIPT.json"
TOKEN_FILE_ENV = "PMI_V06210_ZENODO_TOKEN_FILE"

CONCEPT_ID = 22059707
PREDECESSOR_ID = 22175073
PREDECESSOR_VERSION = "0.62.9"
VERSION = "0.62.10"
LEARNER_FILE = "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.8.html"
LEARNER_SITE = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
GITHUB_RELEASE = "https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.10"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
USER_AGENT = "Codex-PMI-v06210-Zenodo-Publisher/1.0"

TITLE = "Program Matematika Indonesia v0.62.10 — Adapter Backend D60 v2.3.1"
DESCRIPTION = (
    '<p><strong>Mulai belajar sekarang:</strong> <a href="https://kokunoyumeto.github.io/program-matematika-indonesia/">'
    "buka halaman siswa Program Matematika Indonesia</a>. Halaman ini adalah pintu masuk manusia untuk jalur prasyarat, "
    "status mata kuliah, dan bahan belajar.</p>"
    "<p>Versi 0.62.10 mempertahankan tampilan siswa v0.62.8 dan menambahkan adapter backend lintas-korpus v2.3.1 "
    "yang tervalidasi untuk D60, <em>Topologi Aljabar</em>. Pembaca HTML D60 adalah jalur utama siswa dan PDF "
    "adalah unduhan sekunder. Berkas JSON, CSV, dan ZIP adalah infrastruktur mesin, bukan halaman awal siswa. "
    "Program 40-peran keseluruhan belum lengkap.</p>"
    "<p>Payload penerus berisi tepat 100 berkas: 93 berkas publik versi 0.62.9 dipertahankan byte demi byte dan "
    "tujuh artefak D60 ditambahkan. Lima artefak overlay v0.62.2 yang tidak diduplikasi tetap terbuka pada record "
    "pendahulu. Tidak ada record pendahulu yang diubah, ditutup, atau dibatasi.</p>"
    "<p>Hak komponen tidak diratakan dan tetap mengikuti bukti hak masing-masing. Paket gabungan memakai lisensi "
    "<em>other-open</em> karena tidak memiliki satu lisensi tunggal.</p>"
    "<p>Produksi, integrasi, dan QA dibantu oleh <strong>OpenAI Codex gpt-5.6-sol, Ultra</strong> atas instruksi "
    "pengguna. Semua kredit sumber, penulis, dan kontributor manusia yang diwarisi tetap dipertahankan.</p>"
)
NOTES = (
    "Rilis v0.62.10 menambahkan adapter backend D60 v2.3.1 sebagai infrastruktur mesin sekunder. "
    "Situs siswa dan pembaca HTML D60 tetap menjadi pintu masuk utama; program keseluruhan belum lengkap. "
    "Payload 100 berkas mengganti lima artefak overlay lama yang tetap dipreservasi pada record pendahulu "
    "dengan tujuh artefak D60."
)

OMITTED = {
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.2.html",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.2.sha256",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.2.json",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.2.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.2.zip",
}
ADDITIONS = {
    "program-matematika-indonesia-backend-v2.3.1-d60-adapter-v0.1.0.zip",
    "175_D60_V231_ADAPTER_VALIDATION_V010_FINAL_20260830.json",
    "176_D60_V231_ADAPTER_CANONICAL_ADMISSION_20260830.json",
    "177_D60_V231_ADAPTER_DETERMINISTIC_PACKAGE_20260830.json",
    "GITHUB_D60_V231_SOURCE_PUBLICATION_RECEIPT.json",
    "RELEASE_NOTES_v0.62.10.md",
    "RELEASE_CHECKSUMS_v0.62.10.sha256",
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
    setattr(base, name, value)


def local_inventory() -> tuple[list[dict[str, Any]], dict[str, Path], dict[str, Any], dict[str, Any]]:
    base.require(RELEASE_DIR.is_dir(), "v0.62.10 release directory is missing")
    base.require(ASSEMBLY_RECEIPT.is_file(), "assembly receipt is missing")
    base.require(GITHUB_RECEIPT.is_file(), "GitHub v0.62.10 publication receipt is missing")
    entries = list(RELEASE_DIR.iterdir())
    base.require(len(entries) == 100, "local release is not exactly 100 entries")
    base.require(all(path.is_file() and not path.is_symlink() for path in entries), "local release is not flat regular files")
    paths = {path.name: path for path in entries}
    assembly = json.loads(ASSEMBLY_RECEIPT.read_text(encoding="utf-8"))
    github = json.loads(GITHUB_RECEIPT.read_text(encoding="utf-8"))
    base.require(assembly.get("version") == VERSION, "assembly version differs")
    base.require(github.get("state") == "published_public_verified", "GitHub release is not public verified")
    base.require(github.get("tag") == f"v{VERSION}", "GitHub tag differs")
    base.require(github.get("release", {}).get("url") == GITHUB_RELEASE, "GitHub release URL differs")
    base.require(github.get("anonymous_asset_readback", {}).get("result") == "pass_100_of_100", "GitHub readback differs")
    expected_rows = assembly.get("inventory")
    base.require(isinstance(expected_rows, list) and len(expected_rows) == 100, "assembly inventory differs")
    expected = {str(row["name"]): row for row in expected_rows}
    base.require(set(expected) == set(paths), "local filenames differ from assembly")
    github_rows = github.get("anonymous_asset_readback", {}).get("entries")
    base.require(isinstance(github_rows, list) and len(github_rows) == 100, "GitHub readback inventory differs")
    github_by_name = {str(row["name"]): row for row in github_rows}
    base.require(set(github_by_name) == set(paths), "GitHub/local filename sets differ")
    rows: list[dict[str, Any]] = []
    for name in sorted(paths):
        data = paths[name].read_bytes()
        row = {
            "name": name,
            "path": paths[name],
            "bytes": len(data),
            "md5": base.md5_bytes(data),
            "sha256": base.sha256_bytes(data),
        }
        base.require(row["bytes"] == int(expected[name]["bytes"]), f"assembly size differs: {name}")
        base.require(row["sha256"] == expected[name]["sha256"], f"assembly hash differs: {name}")
        base.require(row["bytes"] == int(github_by_name[name]["bytes"]), f"GitHub size differs: {name}")
        base.require(row["sha256"] == github_by_name[name]["sha256"], f"GitHub hash differs: {name}")
        rows.append(row)
    base.require(base.inventory_sha(rows) == assembly["inventory_aggregate_sha256"], "local/assembly aggregate differs")
    base.require(github.get("inventory", {}).get("aggregate_sha256") == base.inventory_sha(rows), "GitHub aggregate differs")
    base.require(set(paths) & OMITTED == set(), "local release retains an exact omission")
    predecessor_receipt = json.loads(PREDECESSOR_RECEIPT.read_text(encoding="utf-8"))
    predecessor_names = {str(row["name"]) for row in predecessor_receipt["payload_inventory"]}
    base.require(set(paths) - predecessor_names == ADDITIONS, "local additive set differs")
    base.require(predecessor_names - set(paths) == OMITTED, "local omission set differs")
    return rows, paths, assembly, github


def verify_exact_draft(draft: dict[str, Any], local_rows: list[dict[str, Any]]) -> None:
    remote = {str(row["name"]): row for row in base.draft_file_rows(draft)}
    local = {str(row["name"]): row for row in local_rows}
    base.require(len(remote) == 100 and set(remote) == set(local), "final draft is not exact 100-file inventory")
    for name, expected in local.items():
        base.require(int(remote[name]["bytes"]) == int(expected["bytes"]), f"final draft size differs: {name}")
        base.require(remote[name]["md5"] == expected["md5"], f"final draft MD5 differs: {name}")


def verify_final_draft_metadata(draft: dict[str, Any], payload: dict[str, Any]) -> None:
    metadata = draft.get("metadata", {})
    base.require(isinstance(metadata, dict), "final draft metadata is malformed")
    for field, expected in payload.items():
        if field == "license":
            base.require(base.license_id(metadata) == expected, "final draft license differs")
        else:
            base.require(metadata.get(field) == expected, f"final draft target metadata differs: {field}")
    rows = draft.get("files", [])
    base.require(isinstance(rows, list) and len(rows) == 100, "final draft file list differs")


def verify_rdm_learner_preview(value: dict[str, Any]) -> None:
    files = value.get("files", {})
    base.require(isinstance(files, dict) and files.get("enabled") is True, "InvenioRDM files are not enabled")
    base.require(files.get("count") == 100, "InvenioRDM file count differs")
    base.require(files.get("default_preview") == LEARNER_FILE, "InvenioRDM default preview differs")


def write_receipts(
    record: dict[str, Any],
    observed: list[dict[str, Any]],
    predecessor_metadata: dict[str, Any],
    predecessor_rows: list[dict[str, Any]],
    github: dict[str, Any],
    lineage: dict[str, Any],
    draft_id: int,
    newversion_http_201_observed: bool,
    deleted: int,
    uploaded: int,
    execution_mode: str,
    reservation_route: str,
) -> tuple[int, str]:
    metadata = record["metadata"]
    publisher = Path(__file__).resolve()
    payload = [
        {
            "name": row["name"],
            "bytes": row["bytes"],
            "md5": row["md5"],
            "sha256": row["sha256"],
            "anonymous_url": row["url"],
            "anonymous_byte_identity": True,
            "provenance": "d60_v2.3.1_additive" if row["name"] in ADDITIONS else "retained_exact_from_v0.62.9",
        }
        for row in observed
    ]
    receipt = {
        "schema_id": "program-matematika-indonesia/zenodo-publication-receipt/1.0.0",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "state": "published_open_cap_compatible_backend_successor",
        "version": VERSION,
        "student_entry": {
            "primary_url": LEARNER_SITE,
            "description_first_href": LEARNER_SITE,
            "related_identifiers_first": LEARNER_SITE,
            "zenodo_default_preview": LEARNER_FILE,
            "machine_backend_is_secondary": True,
        },
        "zenodo": {
            "record_id": int(record["id"]),
            "version_doi": record["doi"],
            "concept_record_id": CONCEPT_ID,
            "concept_doi": record["conceptdoi"],
            "predecessor_record_id": PREDECESSOR_ID,
            "predecessor_doi": f"10.5281/zenodo.{PREDECESSOR_ID}",
            "access_right": metadata["access_right"],
            "license": base.license_id(metadata),
            "language": metadata["language"],
            "publication_date": metadata["publication_date"],
            "file_count": len(payload),
            "anonymous_readback": "pass_100_of_100",
            "concept_latest": "pass",
        },
        "github_authority": {
            "release": GITHUB_RELEASE,
            "receipt_sha256": base.sha256_bytes(GITHUB_RECEIPT.read_bytes()),
            "tag_target_commit": github["release"]["tag_target_commit"],
            "anonymous_readback": github["anonymous_asset_readback"]["result"],
            "inventory_aggregate_sha256": github["inventory"]["aggregate_sha256"],
        },
        "replacement_boundary": {
            "predecessor_files": 98,
            "retained_exact_files": 93,
            "omitted_preserved_in_public_predecessor": sorted(OMITTED),
            "additive_files": sorted(ADDITIONS),
            "successor_files": 100,
            "omission_present_to_absent_transitions_observed_in_this_execution": deleted,
            "addition_absent_to_present_transitions_observed_in_this_execution": uploaded,
            "draft_id": draft_id,
            "newversion_http_201_observed": newversion_http_201_observed,
            "draft_creation_not_inferred_from_http_status": True,
            "execution_mode": execution_mode,
            "reservation_route": reservation_route,
        },
        "payload_inventory": payload,
        "payload_inventory_aggregate_sha256": base.inventory_sha(payload),
        "payload_total_bytes": sum(int(row["bytes"]) for row in payload),
        "inheritance": {
            "predecessor_inventory_aggregate_sha256": base.inventory_sha(predecessor_rows),
            "predecessor_unchanged": True,
            "creators_count": len(metadata["creators"]),
            "creators_canonical_sha256": base.compact_sha(metadata["creators"]),
            "contributors_count": len(metadata["contributors"]),
            "contributors_canonical_sha256": base.compact_sha(metadata["contributors"]),
            "source_and_human_credits_preserved": True,
            "stable_metadata_preserved": True,
        },
        "lineage_verification": lineage,
        "overall_program_complete": False,
        "model_provenance": MODEL,
        "publisher": {
            "path": publisher.relative_to(PROJECT).as_posix(),
            "bytes": publisher.stat().st_size,
            "sha256": base.sha256_bytes(publisher.read_bytes()),
            "git_commands_used": 0,
        },
        "privacy": {
            "credentials_recorded": False,
            "credential_locator_recorded": False,
            "absolute_profile_paths_recorded": False,
            "personal_name_recorded": False,
        },
    }
    data = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    for path in (VERSION_RECEIPT, ROOT_RECEIPT):
        temporary = path.with_name(f".{path.name}.tmp-v06210")
        temporary.write_bytes(data)
        temporary.replace(path)
    return len(data), base.sha256_bytes(data)


def reuse_existing_receipts(
    record: dict[str, Any],
    observed: list[dict[str, Any]],
    github: dict[str, Any],
) -> tuple[int, str] | None:
    existing = []
    for path in (VERSION_RECEIPT, ROOT_RECEIPT):
        if not path.is_file():
            continue
        try:
            candidate = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            raise RuntimeError("existing publication receipt is unreadable") from None
        if candidate.get("version") == VERSION:
            existing.append(path)
    if not existing:
        return None
    data = existing[0].read_bytes()
    for path in existing[1:]:
        base.require(path.read_bytes() == data, "existing publication receipts differ")
    receipt = json.loads(data.decode("utf-8"))
    zenodo = receipt.get("zenodo", {})
    base.require(int(zenodo.get("record_id", -1)) == int(record["id"]), "existing receipt record differs")
    base.require(int(zenodo.get("file_count", -1)) == 100, "existing receipt file count differs")
    base.require(receipt.get("payload_inventory_aggregate_sha256") == base.inventory_sha(observed), "existing receipt inventory differs")
    base.require(int(receipt.get("payload_total_bytes", -1)) == sum(int(row["bytes"]) for row in observed), "existing receipt bytes differ")
    base.require(
        receipt.get("github_authority", {}).get("receipt_sha256") == base.sha256_bytes(GITHUB_RECEIPT.read_bytes()),
        "existing receipt GitHub authority differs",
    )
    base.require(
        receipt.get("github_authority", {}).get("tag_target_commit") == github.get("release", {}).get("tag_target_commit"),
        "existing receipt GitHub commit differs",
    )
    base.require(receipt.get("inheritance", {}).get("predecessor_unchanged") is True, "existing receipt lineage differs")
    for path in (VERSION_RECEIPT, ROOT_RECEIPT):
        if not path.is_file() or path.read_bytes() != data:
            temporary = path.with_name(f".{path.name}.tmp-v06210-restore")
            temporary.write_bytes(data)
            temporary.replace(path)
    return len(data), base.sha256_bytes(data)


base.local_inventory = local_inventory
base.verify_exact_draft = verify_exact_draft
base.verify_final_draft_metadata = verify_final_draft_metadata
base.verify_rdm_learner_preview = verify_rdm_learner_preview
base.write_receipts = write_receipts
base.reuse_existing_receipts = reuse_existing_receipts


if __name__ == "__main__":
    base.main()
