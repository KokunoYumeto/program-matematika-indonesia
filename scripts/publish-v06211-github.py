#!/usr/bin/env python3
"""Publish and anonymously verify the exact 100-file PMI v0.62.11 GitHub release."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
TEMPLATE_SCRIPT = PROJECT / "scripts/publish-v06210-github.py"

spec = importlib.util.spec_from_file_location("pmi_v06210_github_template", TEMPLATE_SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load the proven v0.62.10 GitHub publisher")
template = importlib.util.module_from_spec(spec)
spec.loader.exec_module(template)
base = template.base

RELEASE_DIR = PROJECT / "releases/v0.62.11"
ASSEMBLY_RECEIPT = WORKSPACE / "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/186_D110_V231_RELEASE_ASSEMBLY_V06211_20260830.json"
PREDECESSOR_ASSEMBLY_RECEIPT = WORKSPACE / "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/178_D60_V231_RELEASE_ASSEMBLY_V06210_20260830.json"
PREDECESSOR_GITHUB_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.10.json"
SOURCE_RECEIPT = PROJECT / "GITHUB_D110_V231_SOURCE_PUBLICATION_RECEIPT.json"
PUBLICATION_RECEIPT = PROJECT / "GITHUB_PUBLICATION_RECEIPT_v0.62.11.json"
TOKEN_FILE_ENV = "PMI_V06211_GITHUB_TOKEN_FILE"

VERSION = "0.62.11"
TAG = f"v{VERSION}"
PREDECESSOR_TAG = "v0.62.10"
TARGET_COMMIT = "2f0e52280791854f904475e5f92392f52745ea24"
TARGET_TREE = "af8d0254ca0132fc5c8c8622052e4b50b9392fff"
LEARNER_SITE = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
USER_AGENT = "Codex-PMI-v06211-GitHub-Publisher/1.0"
TITLE = "Program Matematika Indonesia v0.62.11 — Adapter backend D110 v2.3.1"
BODY = f"""{LEARNER_SITE}

Mulai belajar dari situs siswa di atas. Berkas JSON, CSV, dan ZIP dalam rilis ini adalah infrastruktur backend mesin, bukan halaman awal siswa.

Rilis v0.62.11 mempertahankan tampilan siswa v0.62.8 dan menambahkan adapter lintas-korpus v2.3.1 yang tervalidasi untuk D110, *Matematika dalam Lean*. Payload publik berisi tepat 100 berkas agar kompatibel dengan batas Zenodo: 93 berkas v0.62.10 dipertahankan byte demi byte dan tujuh artefak v0.62.11 ditambahkan. Lima artefak overlay v0.62.3 dan dua berkas metadata v0.62.9 yang tidak dibawa maju tetap terbuka dalam rilis terdahulu.

Pembaca HTML D110 di https://kokunoyumeto.github.io/mathematics-in-lean-id/ adalah jalur utama siswa; PDF adalah unduhan sekunder. ZIP adapter D110 adalah infrastruktur mesin, bukan pengganti pembaca. Hak komponen dan identitas native pemilik tidak diratakan. A00, B10, D60, dan D110 adalah empat bukti jalur; rilis ini tidak menyatakan kepatuhan v2.3.1 bagi 36 peran lain atau bahwa seluruh program selesai diterjemahkan.

Provenans model: OpenAI Codex gpt-5.6-sol, Ultra. Semua kredit sumber, penulis, dan kontributor manusia dipertahankan.

Codex, atas instruksi pengguna.
"""

PREDECESSOR_OMISSIONS = {
    "00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_LIVE_v0.62.3.html",
    "LIVE_OVERLAY_CHECKSUMS_v0.62.3.sha256",
    "LIVE_PUBLICATION_OVERLAY_MANIFEST_v0.62.3.json",
    "LOCAL_LIVE_OVERLAY_VALIDATION_v0.62.3.json",
    "program-matematika-indonesia-live-overlay-source-v0.62.3.zip",
    "RELEASE_CHECKSUMS_v0.62.9.sha256",
    "RELEASE_NOTES_v0.62.9.md",
}
EXPECTED_ADDITIONS = {
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
    "PREDECESSOR_ASSEMBLY_RECEIPT": PREDECESSOR_ASSEMBLY_RECEIPT,
    "PREDECESSOR_GITHUB_RECEIPT": PREDECESSOR_GITHUB_RECEIPT,
    "SOURCE_RECEIPT": SOURCE_RECEIPT,
    "PUBLICATION_RECEIPT": PUBLICATION_RECEIPT,
    "TOKEN_FILE_ENV": TOKEN_FILE_ENV,
    "VERSION": VERSION,
    "TAG": TAG,
    "PREDECESSOR_TAG": PREDECESSOR_TAG,
    "TARGET_COMMIT": TARGET_COMMIT,
    "TARGET_TREE": TARGET_TREE,
    "LEARNER_SITE": LEARNER_SITE,
    "USER_AGENT": USER_AGENT,
    "TITLE": TITLE,
    "BODY": BODY,
    "EXPECTED_ADDITIONS": EXPECTED_ADDITIONS,
    "PREDECESSOR_OMISSIONS": PREDECESSOR_OMISSIONS,
}.items():
    setattr(template, name, value)

for name, value in {
    "RELEASE_DIR": RELEASE_DIR,
    "ASSEMBLY_RECEIPT": ASSEMBLY_RECEIPT,
    "SOURCE_RECEIPT": SOURCE_RECEIPT,
    "PUBLICATION_RECEIPT": PUBLICATION_RECEIPT,
    "TOKEN_FILE_ENV": TOKEN_FILE_ENV,
    "VERSION": VERSION,
    "TAG": TAG,
    "PREDECESSOR_TAG": PREDECESSOR_TAG,
    "TARGET_COMMIT": TARGET_COMMIT,
    "TARGET_TREE": TARGET_TREE,
    "LEARNER_SITE": LEARNER_SITE,
    "USER_AGENT": USER_AGENT,
    "TITLE": TITLE,
    "BODY": BODY,
    "EXPECTED_ADDITIONS": EXPECTED_ADDITIONS,
    "PUBLIC_V0628_OMISSIONS": PREDECESSOR_OMISSIONS,
}.items():
    setattr(base, name, value)


def local_inventory() -> tuple[list[dict[str, Any]], dict[str, Path], dict[str, Any]]:
    base.require(RELEASE_DIR.is_dir(), "v0.62.11 release directory is missing")
    base.require(ASSEMBLY_RECEIPT.is_file(), "v0.62.11 assembly receipt is missing")
    assembly = json.loads(ASSEMBLY_RECEIPT.read_text(encoding="utf-8"))
    base.require(assembly.get("state") == "assembled_validated_not_yet_published", "assembly state differs")
    base.require(assembly.get("version") == VERSION, "assembly version differs")
    expected_rows = assembly.get("inventory")
    base.require(isinstance(expected_rows, list) and len(expected_rows) == 100, "assembly inventory is not 100 files")
    expected = {str(row["name"]): row for row in expected_rows}
    base.require(len(expected) == 100, "assembly inventory names are not unique")
    entries = list(RELEASE_DIR.iterdir())
    base.require(len(entries) == 100, "local v0.62.11 directory is not exactly 100 entries")
    base.require(all(path.is_file() and not path.is_symlink() for path in entries), "local v0.62.11 release is not flat regular files")
    paths = {path.name: path for path in entries}
    base.require(set(paths) == set(expected), "local v0.62.11 filenames differ from assembly receipt")
    rows: list[dict[str, Any]] = []
    for name in sorted(paths):
        data = paths[name].read_bytes()
        row = {"name": name, "bytes": len(data), "sha256": base.sha256_bytes(data)}
        base.require(row["bytes"] == int(expected[name]["bytes"]), f"local byte count differs: {name}")
        base.require(row["sha256"] == expected[name]["sha256"], f"local hash differs: {name}")
        rows.append(row)
    base.require(base.canonical_sha(rows) == assembly["inventory_aggregate_sha256"], "assembly aggregate differs")
    checksum_name = "RELEASE_CHECKSUMS_v0.62.11.sha256"
    checksum_lines = (RELEASE_DIR / checksum_name).read_text(encoding="utf-8").splitlines()
    base.require(len(checksum_lines) == 99, "release checksum manifest is not 99 entries")
    parsed: dict[str, str] = {}
    for line in checksum_lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/\\]+)", line)
        base.require(match is not None, "release checksum syntax differs")
        parsed[match.group(2)] = match.group(1)
    base.require(set(parsed) == set(paths) - {checksum_name}, "release checksum coverage differs")
    hashes = {row["name"]: row["sha256"] for row in rows}
    for name, digest in parsed.items():
        base.require(digest == hashes[name], f"checksum differs: {name}")
    return rows, paths, assembly


def verify_source_authority(anonymous: Any, authenticated: Any) -> dict[str, Any]:
    commit = base.api_json(authenticated, "GET", f"/repos/{base.REPO}/git/commits/{TARGET_COMMIT}")
    base.require(commit["tree"]["sha"] == TARGET_TREE, "target source tree differs")
    comparison = base.api_json(authenticated, "GET", f"/repos/{base.REPO}/compare/{TARGET_COMMIT}...main")
    base.require(comparison.get("merge_base_commit", {}).get("sha") == TARGET_COMMIT, "target source is not an ancestor of main")
    base.require(comparison.get("status") in {"identical", "ahead"}, "target/main ancestry differs")
    manifest_path = "backend/v2.3/extensions/d110-mathematics-in-lean-v0.1.0/manifest.json"
    local_manifest = PROJECT / manifest_path
    base.require(local_manifest.is_file(), "canonical D110 manifest is missing")
    raw_url = f"https://raw.githubusercontent.com/{base.REPO}/{TARGET_COMMIT}/{manifest_path}"
    remote = base.request(anonymous, "GET", raw_url).content
    local = local_manifest.read_bytes()
    base.require(remote == local, "public D110 manifest differs from local canonical bytes")
    base.require(SOURCE_RECEIPT.is_file(), "D110 source publication receipt is missing")
    receipt = json.loads(SOURCE_RECEIPT.read_text(encoding="utf-8"))
    base.require(str(receipt.get("status", "")).casefold() == "pass", "source publication receipt did not pass")
    base.require(receipt.get("source_commit") == TARGET_COMMIT, "source receipt commit differs")
    base.require(receipt.get("source_tree") == TARGET_TREE, "source receipt tree differs")
    base.require(receipt.get("anonymous_raw_readback", {}).get("files") == 71, "source raw readback count differs")
    base.require(receipt.get("anonymous_pages_readback", {}).get("files") == 3, "source Pages readback count differs")
    return {
        "commit": TARGET_COMMIT,
        "tree": TARGET_TREE,
        "main_relation": comparison.get("status"),
        "manifest_bytes": len(remote),
        "manifest_sha256": base.sha256_bytes(remote),
        "source_receipt_bytes": SOURCE_RECEIPT.stat().st_size,
        "source_receipt_sha256": base.sha256_bytes(SOURCE_RECEIPT.read_bytes()),
    }


def verify_predecessor(anonymous: Any, rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    predecessor = base.api_json(anonymous, "GET", f"/repos/{base.REPO}/releases/tags/{quote(PREDECESSOR_TAG, safe='')}")
    base.require(not predecessor.get("draft") and not predecessor.get("prerelease"), "predecessor is not public final")
    assets = base.paginated_assets(anonymous, int(predecessor["id"]))
    old = {str(asset["name"]): asset for asset in assets}
    base.require(len(old) == len(assets) == 100, "public v0.62.10 inventory is not 100 unique files")
    base.require(PREDECESSOR_ASSEMBLY_RECEIPT.is_file(), "v0.62.10 assembly receipt is missing")
    previous_assembly = json.loads(PREDECESSOR_ASSEMBLY_RECEIPT.read_text(encoding="utf-8"))
    previous_rows = previous_assembly.get("inventory")
    base.require(isinstance(previous_rows, list) and len(previous_rows) == 100, "v0.62.10 assembly inventory differs")
    previous = {str(row["name"]): row for row in previous_rows}
    base.require(set(old) == set(previous), "public v0.62.10 filenames differ from frozen assembly")
    for name, row in previous.items():
        asset = old[name]
        base.require(int(asset["size"]) == int(row["bytes"]), f"public v0.62.10 size differs: {name}")
        base.require(asset.get("digest") == f"sha256:{row['sha256']}", f"public v0.62.10 digest differs: {name}")
    old_rows = [{"name": name, "bytes": int(previous[name]["bytes"]), "sha256": str(previous[name]["sha256"])} for name in sorted(previous)]
    base.require(base.canonical_sha(old_rows) == previous_assembly["inventory_aggregate_sha256"], "public v0.62.10 aggregate differs")
    if PREDECESSOR_GITHUB_RECEIPT.is_file():
        prior = json.loads(PREDECESSOR_GITHUB_RECEIPT.read_text(encoding="utf-8"))
        base.require(prior.get("state") == "published_public_verified", "v0.62.10 GitHub receipt state differs")
        base.require(int(prior.get("release", {}).get("id", -1)) == int(predecessor["id"]), "v0.62.10 release ID differs")
        base.require(prior.get("inventory", {}).get("aggregate_sha256") == base.canonical_sha(old_rows), "v0.62.10 receipt aggregate differs")
    new = {str(row["name"]): row for row in rows}
    common = set(old) & set(new)
    omitted = set(old) - set(new)
    added = set(new) - set(old)
    base.require(len(common) == 93, "v0.62.10 common boundary is not 93")
    base.require(omitted == PREDECESSOR_OMISSIONS, "v0.62.10 omission set differs")
    base.require(added == EXPECTED_ADDITIONS, "v0.62.11 additive set differs")
    inherited: list[dict[str, Any]] = []
    for name in sorted(common):
        local = new[name]
        remote = old[name]
        base.require(int(remote["size"]) == int(local["bytes"]), f"predecessor size differs: {name}")
        base.require(remote.get("digest") == f"sha256:{local['sha256']}", f"predecessor digest differs: {name}")
        inherited.append(local)
    return predecessor, inherited


template.local_inventory = local_inventory
template.verify_source_authority = verify_source_authority
template.verify_predecessor = verify_predecessor


def main() -> None:
    template.main()
    receipt = json.loads(PUBLICATION_RECEIPT.read_text(encoding="utf-8"))
    inventory = receipt["inventory"]
    inherited = inventory.pop("inherited_public_v0629_files")
    omitted = inventory.pop("omitted_public_v0629_files")
    inventory["inherited_public_v06210_files"] = inherited
    inventory["omitted_public_v06210_files"] = omitted
    publisher = Path(__file__).resolve()
    receipt["publisher"] = {
        "path": publisher.relative_to(PROJECT).as_posix(),
        "bytes": publisher.stat().st_size,
        "sha256": base.sha256_bytes(publisher.read_bytes()),
        "git_commands_used": 0,
    }
    receipt["recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
    PUBLICATION_RECEIPT.write_bytes((json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({
        "status": "PASS_FINAL_RECEIPT",
        "release": receipt["release"]["url"],
        "tag": TAG,
        "commit": TARGET_COMMIT,
        "files": receipt["inventory"]["files"],
        "receipt": PUBLICATION_RECEIPT.relative_to(PROJECT).as_posix(),
        "receipt_bytes": PUBLICATION_RECEIPT.stat().st_size,
        "receipt_sha256": base.sha256_bytes(PUBLICATION_RECEIPT.read_bytes()),
    }, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        detail = str(exc).replace("\r", " ").replace("\n", " ")[:1200]
        print(f"FAIL: {type(exc).__name__}: {detail}", file=sys.stderr)
        raise SystemExit(1)
