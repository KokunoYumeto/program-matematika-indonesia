"""Build the complete 54-document C140 zero-copy capability adapter."""

from __future__ import annotations

import argparse
import html
from pathlib import Path
from typing import Any

from c140_capability_model_v1 import (
    BOUNDARY_ID,
    CONTENT_COMMIT,
    CONTRACT,
    COURSE_ID,
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    GITHUB_RECEIPT,
    LOCALE,
    NATIVE_FAMILY,
    NATIVE_ROLE_ID,
    PAGES_COMMIT,
    PAGES_RECEIPT,
    RELEASE_ID,
    RELEASE_TAG,
    REPOSITORY,
    TRANSLATION_PROVENANCE,
    ZENODO_CONCEPT_ID,
    ZENODO_DOI,
    ZENODO_RECEIPT,
    ZENODO_RECORD_ID,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    derive_projection,
    identity,
    projection_errors,
    write_bytes,
    write_json,
)


STYLE = """
:root{color-scheme:light;--ink:#172d36;--muted:#53666d;--paper:#f2eee4;--card:#fff;--line:#c7d2d5;--accent:#086d78;--warn:#9d542c}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1180px;margin:auto;padding:28px 20px 64px}nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem}a{color:var(--accent);text-underline-offset:3px}
h1{font-size:clamp(2rem,5vw,3.4rem);line-height:1.06;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.12rem;max-width:82ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:1.5rem 0}.card,details,.notice{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{display:block;font-size:1.8rem;font-weight:760}.muted{color:var(--muted)}details{margin:.75rem 0}summary{cursor:pointer;font-weight:700}.notice{border-left:6px solid var(--warn)}code{overflow-wrap:anywhere}.index{columns:2;column-width:350px}.index li{break-inside:avoid;margin:.4rem 0}.compact{font-size:.92rem}a:focus-visible,summary:focus-visible{outline:3px solid #d58a25;outline-offset:3px}
""".strip()


NEGATIVE_FIXTURES: tuple[tuple[str, str], ...] = (
    ("source-lock-drift", "C140-SOURCE-LOCK"),
    ("dropped-document", "C140-DOCUMENT-CLOSURE"),
    ("altered-penn-unit-id", "C140-PENN_UNITS-IDENTITIES"),
    ("copied-source-text", "C140-FORBIDDEN-CONTENT-KEY"),
    ("copied-solution-body", "C140-FORBIDDEN-CONTENT-KEY"),
    ("flattened-rights", "C140-RIGHTS-COUNT"),
    ("collapsed-random-witness", "C140-RANDOM-RIGHTS-DISCREPANCY"),
    ("restricted-public-access", "C140-PUBLIC-ACCESS"),
    ("false-uniform-pdf", "C140-CLAIM-BOUNDARY"),
    ("false-wcag", "C140-CLAIM-BOUNDARY"),
    ("bad-public-route", "C140-DOCUMENT-CLOSURE"),
    ("copied-native-body-count", "C140-COPIED-NATIVE-BODY"),
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>"
        '<nav><a href="C140.html">Pelajar</a><a href="C140-pengajar.html">Pengajar</a>'
        '<a href="capabilities.json">Kapabilitas JSON</a></nav>'
        f"{body}</main></body></html>\n"
    )


def _document_list(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f'<li><a href="{esc(row["public_page"]["url"])}">{esc(row["title"])}</a> '
        f'<span class="muted">· <code>{esc(row["document_id"])}</code></span></li>'
        for row in rows
    )


def render_learner(bundle: dict[str, Any]) -> str:
    learner = bundle["learner_map"]
    counts = bundle["capabilities"]["counts"]
    labels = {
        "penn_spine": "Tulang punggung Penn State STAT 415",
        "random_completeness": "Donor kecukupan dan kelengkapan Random",
        "companion_index": "Gerbang pendamping orisinal",
        "companion_theory": "Teori pendamping",
        "companion_simulations": "Simulasi",
        "companion_mastery": "Set penguasaan",
        "companion_assessments": "Asesmen kumulatif",
        "companion_capstones": "Proyek akhir",
    }
    groups = "".join(
        f'<details open><summary>{esc(labels[key])} · {len(rows)} dokumen</summary><ol class="index compact">{_document_list(rows)}</ol></details>'
        for key, rows in learner["components"].items()
    )
    return shell(
        "C140 · Peta belajar statistika matematis",
        f"""
<p class="muted">C140 · <code>{esc(CONTRACT)}</code> · <code>{esc(BOUNDARY_ID)}</code> · {esc(LOCALE)}</p>
<h1>Statistika Matematis</h1>
<p class="lede">Peta ini menyatukan 14 dokumen kuliah Penn State, satu donor tentang kecukupan dan kelengkapan, serta 39 dokumen pendamping orisinal. Semua isi tetap pada pembaca native publik; backend pusat hanya membawa identitas, hash, struktur, istilah, koreksi, hak, dan rute.</p>
<div class="grid"><div class="card"><span class="metric">{counts['public_documents']}</span>dokumen publik</div><div class="card"><span class="metric">{counts['penn_units']}</span>unit Penn</div><div class="card"><span class="metric">{counts['penn_segments']}</span>segmen terjemahan</div><div class="card"><span class="metric">{counts['companion_solved_problems']}</span>soal berjawaban lengkap</div><div class="card"><span class="metric">{counts['companion_simulation_documents']}</span>simulasi</div></div>
<p><a href="{esc(learner['public_home'])}">Buka koleksi native</a> · <a href="../data/document-index.jsonl">Indeks 54 dokumen</a> · <a href="../data/learner-map.json">Peta mesin</a></p>
<div class="notice"><strong>Batas klaim:</strong> tiga kelas hak tetap terpisah, termasuk dua saksi lisensi Random yang tidak konsisten. Tidak ada badan buku, soal, jawaban, atau solusi yang disalin. Tidak ada klaim satu PDF seragam, PDF/UA, WCAG, atau pertukaran konten reversibel.</div>
<h2>Urutan yang disarankan</h2><ol>{''.join(f'<li>{esc(item)}</li>' for item in learner['selection_guidance'])}</ol>
<h2>Komponen dan dokumen</h2>{groups}
""",
    )


def render_educator(bundle: dict[str, Any]) -> str:
    educator = bundle["educator_map"]
    counts = bundle["capabilities"]["counts"]
    problems = "".join(
        f'<li><a href="{esc(row["public_route"])}"><code>{esc(row["id"])}</code></a> · {esc(row.get("title", "soal"))}</li>'
        for row in educator["solved_problems"]
    )
    rubrics = "".join(
        f'<li><a href="{esc(row["public_route"])}"><code>{esc(row["id"])}</code></a> · {esc(row.get("title", "rubrik"))}</li>'
        for row in educator["rubrics"]
    )
    governance = "".join(
        f'<li><a href="../{esc(path)}">{esc(label.replace("_", " "))}</a></li>'
        for label, path in educator["governance"].items()
    )
    return shell(
        "C140 · Peta pengajar statistika matematis",
        f"""
<p class="muted">C140 · tampilan pengajar · <code>{esc(CONTRACT)}</code></p>
<h1>Perencanaan dan penilaian C140</h1>
<p class="lede">Pilih dokumen, masalah, rubrik, simulasi, asesmen, atau capstone dengan identitas native yang sama dengan peta pelajar. Tautan membuka isi lengkap pada pembaca publik; indeks pusat tidak menduplikasi isi tersebut.</p>
<div class="grid"><div class="card"><span class="metric">{counts['companion_solved_problems']}</span>masalah terselesaikan</div><div class="card"><span class="metric">{counts['companion_rubrics']}</span>rubrik</div><div class="card"><span class="metric">{counts['companion_assessment_documents']}</span>asesmen</div><div class="card"><span class="metric">{counts['companion_capstone_documents']}</span>capstone</div><div class="card"><span class="metric">{counts['terminology_rows']}</span>rekaman istilah</div></div>
<div class="notice"><strong>Batas klaim:</strong> ini adalah pemilih dan ledger pengajar, bukan satu manual guru berlisensi seragam. Isi masalah dan solusi tetap pada komponen CC BY-SA; materi Penn, Random, MathJax, dan dataset mempertahankan hak masing-masing.</div>
<h2>Indeks tata kelola</h2><ul>{governance}</ul>
<h2>Masalah dengan solusi lengkap</h2><ol class="index compact">{problems}</ol>
<h2>Rubrik</h2><ol class="index compact">{rubrics}</ol>
<h2>Simulasi</h2><ol>{_document_list(educator['simulations'])}</ol>
<h2>Asesmen</h2><ol>{_document_list(educator['assessments'])}</ol>
<h2>Capstone</h2><ol>{_document_list(educator['capstones'])}</ol>
""",
    )


def _fixture_bytes() -> dict[str, bytes]:
    return {
        f"fixtures/negative/{fixture_id}.json": canonical_json_bytes({
            "schema": "c140-negative-fixture/1",
            "fixture_id": fixture_id,
            "expected_error": expected_error,
        })
        for fixture_id, expected_error in NEGATIVE_FIXTURES
    }


def build(native_root: Path, adapter: Path) -> dict[str, Any]:
    bundle = derive_projection(native_root)
    errors = projection_errors(bundle)
    if errors:
        raise ValueError(f"C140 native projection failed: {errors}")

    files: dict[str, bytes] = {
        "input/source-lock.json": canonical_json_bytes(bundle["source_lock"]),
        "input/github-release-readback.json": (native_root / GITHUB_RECEIPT).read_bytes(),
        "input/github-pages-readback.json": (native_root / PAGES_RECEIPT).read_bytes(),
        "input/zenodo-readback.json": (native_root / ZENODO_RECEIPT).read_bytes(),
        "data/document-index.jsonl": canonical_jsonl_bytes(bundle["documents"]),
        "data/penn-unit-index.jsonl": canonical_jsonl_bytes(bundle["penn_units"]),
        "data/penn-segment-index.jsonl": canonical_jsonl_bytes(bundle["penn_segments"]),
        "data/penn-terms-index.jsonl": canonical_jsonl_bytes(bundle["penn_terms"]),
        "data/penn-corrections-index.jsonl": canonical_jsonl_bytes(bundle["penn_corrections"]),
        "data/random-entity-index.jsonl": canonical_jsonl_bytes(bundle["random_entities"]),
        "data/random-relation-index.jsonl": canonical_jsonl_bytes(bundle["random_relations"]),
        "data/random-terms-index.jsonl": canonical_jsonl_bytes(bundle["random_terms"]),
        "data/random-adverse-index.jsonl": canonical_jsonl_bytes(bundle["random_adverse"]),
        "data/companion-entity-index.jsonl": canonical_jsonl_bytes(bundle["companion_entities"]),
        "data/companion-relation-index.jsonl": canonical_jsonl_bytes(bundle["companion_relations"]),
        "data/rights-index.jsonl": canonical_jsonl_bytes(bundle["rights_index"]),
        "data/learner-map.json": canonical_json_bytes(bundle["learner_map"]),
        "data/educator-map.json": canonical_json_bytes(bundle["educator_map"]),
        "data/public-evidence.json": canonical_json_bytes(bundle["public_evidence"]),
        "data/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "data/claim-boundary.json": canonical_json_bytes(bundle["claim_boundary"]),
        "views/C140.html": render_learner(bundle).encode("utf-8"),
        "views/C140-pengajar.html": render_educator(bundle).encode("utf-8"),
        "views/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        **_fixture_bytes(),
        "README.md": (
            "# C140 complete zero-copy capability adapter\n\n"
            "This adapter binds the complete C5 course boundary: fourteen Penn State STAT 415 "
            "documents, exactly one Random sufficiency/completeness donor page, and thirty-nine "
            "original Indonesian companion documents. It preserves 8,358 stable entity IDs, "
            "4,932 Penn translation bindings, 234 terminology rows, 242 Penn corrections, "
            "nineteen Random adverse records, 2,423 structural relations, 146 solved-problem "
            "identities, and all component-scoped rights.\n\n"
            "The central projection contains no textbook, source segment, exercise, answer, or "
            "solution bodies. Learner and educator pages link to the exact public native HTML. "
            "Penn State, Random, companion, MathJax, and dataset rights remain distinct; in "
            "particular, the Random CC BY 2.0 and CC BY 1.0 witnesses are not collapsed.\n\n"
            f"Translation provenance: `{TRANSLATION_PROVENANCE}`.\n"
        ).encode("utf-8"),
    }
    for relative, data in files.items():
        write_bytes(adapter / relative, data)

    manifest = {
        "schema": "c140-capability-manifest/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "boundary_id": BOUNDARY_ID,
        "native_family": NATIVE_FAMILY,
        "locale": LOCALE,
        "content_policy": "identity_structure_terminology_corrections_rights_and_public_routes_only",
        "authority": {
            "repository": REPOSITORY,
            "content_commit": CONTENT_COMMIT,
            "pages_commit": PAGES_COMMIT,
            "release_tag": RELEASE_TAG,
            "release_id": RELEASE_ID,
            "zenodo_record_id": ZENODO_RECORD_ID,
            "zenodo_doi": ZENODO_DOI,
            "zenodo_concept_id": ZENODO_CONCEPT_ID,
        },
        "projection": {
            "whole_course_component_boundary_proven": True,
            "component_rights_preserved": True,
            "native_ids_preserved": True,
            "native_bodies_copied": False,
            "external_native_backend_required_for_replay": True,
            "public_access_state_changed": False,
            "reversible_content_exchange_claimed": False,
        },
        "counts": bundle["capabilities"]["counts"],
        "inputs": bundle["source_lock"]["inputs"],
        "output_paths": sorted(files),
        "outputs": [identity(adapter / path, display_path=path) for path in sorted(files)],
        "validation_path": "validation.json",
        "package_receipt_path": "build/PACKET_BUILD_RECEIPT.json",
        "negative_fixture_count": len(NEGATIVE_FIXTURES),
    }
    write_json(adapter / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    args = parser.parse_args()
    manifest = build(args.native_root.resolve(), args.adapter.resolve())
    print(canonical_json_bytes({
        "state": "pass",
        "course_id": COURSE_ID,
        "outputs": len(manifest["outputs"]),
        "documents": manifest["counts"]["public_documents"],
        "stable_entity_ids": manifest["counts"]["stable_entity_ids"],
        "solved_problems": manifest["counts"]["companion_solved_problems"],
    }).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
