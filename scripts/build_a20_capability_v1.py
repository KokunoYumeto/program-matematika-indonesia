"""Build the A20 zero-copy learner/educator capability adapter."""

from __future__ import annotations

import argparse
import html
from pathlib import Path
from typing import Any

from a20_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    LOCALE,
    NATIVE_COURSE_ID,
    PUBLIC_RECEIPT_PATH,
    RELEASE_COMMIT,
    RELEASE_TREE,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    derive_projection,
    identity,
    projection_errors,
    read_json,
    write_bytes,
    write_json,
)


STYLE = """
:root{color-scheme:light;--ink:#172d36;--muted:#53666d;--paper:#f3f0e7;--card:#fff;--line:#cad3d5;--accent:#086d78;--warn:#9d542c}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1160px;margin:auto;padding:28px 20px 64px}nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem}a{color:var(--accent);text-underline-offset:3px}
h1{font-size:clamp(2rem,5vw,3.4rem);line-height:1.06;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.12rem;max-width:78ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:1.5rem 0}.card,details,.notice{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{display:block;font-size:1.8rem;font-weight:760}.muted{color:var(--muted)}details{margin:.75rem 0}summary{cursor:pointer;font-weight:700}.notice{border-left:6px solid var(--warn)}code{overflow-wrap:anywhere}.module-list{display:grid;gap:.65rem;list-style:none;padding:0}.module{border-top:1px solid var(--line);padding-top:.65rem}.compact{font-size:.92rem}a:focus-visible,summary:focus-visible{outline:3px solid #d58a25;outline-offset:3px}
""".strip()


NEGATIVE_FIXTURES = (
    ("source-hash-drift", "source_lock.inputs[0].sha256", "replace", "00" * 32, "A20-SOURCE-LOCK"),
    ("native-sequence-drift", "native_record_ledger.id_sequence_sha256", "replace", "00" * 32, "A20-NATIVE-SEQUENCE"),
    ("dropped-module", "module_index[-1]", "remove", None, "A20-MODULE-INDEX"),
    ("dropped-exercise", "exercise_index[-1]", "remove", None, "A20-EXERCISE-COUNT"),
    ("invented-solution", "exercise_index[first_unsolved].solution_id", "replace", "urn:uuid:invented", "A20-SOLUTION-BOUNDARY"),
    ("copied-body", "learner_map.body", "add", "forbidden native body", "A20-COPIED-NATIVE-BODY"),
    ("invented-native-prerequisite", "claim_boundary.native_course_prerequisites_invented", "replace", True, "A20-INVENTED-NATIVE-PREREQUISITE"),
    ("stale-landing-authority", "claim_boundary.stale_repository_landing_used_as_complete_authority", "replace", True, "A20-STALE-LANDING-AUTHORITY"),
    ("false-semantic-html", "claim_boundary.indonesian_semantic_html_claimed", "replace", True, "A20-FALSE-CLAIM:indonesian_semantic_html_claimed"),
    ("false-mathml", "claim_boundary.indonesian_mathml_claimed", "replace", True, "A20-FALSE-CLAIM:indonesian_mathml_claimed"),
    ("false-pdfua", "claim_boundary.pdf_ua_claimed", "replace", True, "A20-FALSE-CLAIM:pdf_ua_claimed"),
    ("false-reversibility", "claim_boundary.reversible_exchange_claimed", "replace", True, "A20-FALSE-CLAIM:reversible_exchange_claimed"),
    ("false-english-translation", "claim_boundary.english_source_mirror_translation_claimed", "replace", True, "A20-FALSE-CLAIM:english_source_mirror_translation_claimed"),
    ("flattened-rights", "rights_index", "replace", [{"id": "all"}], "A20-RIGHTS-FLATTENED"),
    ("bad-module-route", "module_index[0].public_route", "replace", "https://example.invalid/", "A20-MODULE-ROUTE"),
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>"
        '<nav><a href="A20.html">Pelajar</a><a href="A20-pengajar.html">Pengajar</a>'
        '<a href="capabilities.json">Kapabilitas JSON</a></nav>'
        f"{body}</main></body></html>\n"
    )


def _module_item(row: dict[str, Any], *, educator: bool = False) -> str:
    governance = (
        f" · {row['concept_count']} konsep · <code>{esc(row['module_unit_id'])}</code>"
        if educator else ""
    )
    return (
        '<li class="module">'
        f'<a href="{esc(row["public_route"])}"><strong>{row["ordinal"]}. '
        f'{esc(row["title_id_ID"] or row["title_source"] or row["module_id"])}</strong></a>'
        f' <span class="muted">({esc(row["module_id"])}, hlm. {row["start_page"]})</span><br>'
        f'{row["exercise_count"]} latihan · {row["solution_identity_count"]} memiliki identitas solusi · '
        f'{row["unsolved_exercise_count"]} tanpa identitas solusi{governance}</li>'
    )


def _chapter_block(chapter: dict[str, Any], modules: dict[str, dict[str, Any]], *, educator: bool = False) -> str:
    rows = "".join(_module_item(modules[module_id], educator=educator) for module_id in chapter["module_ids"])
    return (
        f'<details><summary>Bab {chapter["ordinal"]} · {esc(chapter["title_id_ID"])} · '
        f'{chapter["module_count"]} modul · {chapter["exercise_count"]} latihan</summary>'
        f'<p><a href="{esc(chapter["public_route"])}">Mulai pada halaman {chapter["start_page"]}</a></p>'
        f'<ol class="module-list compact">{rows}</ol></details>'
    )


def render_learner(bundle: dict[str, Any]) -> str:
    learning = bundle["learner_map"]
    counts = bundle["capabilities"]["counts"]
    modules = {row["module_id"]: row for row in learning["modules"]}
    preface = "".join(_module_item(row) for row in learning["front_matter_modules"])
    chapters = "".join(_chapter_block(row, modules) for row in learning["chapters"])
    english = learning["english_source_mirror"]
    return shell(
        "A20 · Peta belajar aljabar menengah",
        f"""
<p class="muted">A20 · <code>{esc(CONTRACT)}</code> · <code>{esc(NATIVE_COURSE_ID)}</code></p>
<h1>Peta belajar A20</h1>
<p class="lede">Adapter tipis ini menghubungkan 83 modul dan identitas latihan ke edisi Bahasa Indonesia. Isi buku tetap berada di edisi native yang dipreservasi.</p>
<div class="grid"><div class="card"><span class="metric">{counts['pdf_pages']}</span>halaman</div><div class="card"><span class="metric">{counts['modules']}</span>modul</div><div class="card"><span class="metric">{counts['exercises']}</span>latihan</div><div class="card"><span class="metric">{counts['solution_identities']}</span>identitas solusi</div></div>
<p>Prasyarat kurikulum: <code>A10</code> <span class="muted">(lapisan kurikulum pusat, bukan klaim native).</span> <a href="{esc(learning['indonesian_reader']['url'])}">Buka pembaca Bahasa Indonesia</a>.</p>
<p>Butuh sumber berbahasa Inggris? <a href="{esc(english['reader_url'])}">Buka cermin HTML sumber asli</a> atau <a href="{esc(english['offline_zip_url'])}">unduh paket luringnya</a>. Ini cermin presentasi sumber, bukan terjemahan.</p>
<div class="notice"><strong>Batas solusi:</strong> {counts['solution_identities']} dari {counts['exercises']} latihan memiliki identitas solusi; {counts['unsolved_exercises']} tidak. Adapter tidak mengarang solusi yang hilang dan tidak menyalin isi latihan atau solusi.</div>
<h2>Bagian awal</h2><ol class="module-list compact">{preface}</ol>
<h2>Bab dan modul</h2>{chapters}
""",
    )


def render_educator(bundle: dict[str, Any]) -> str:
    educator = bundle["educator_map"]
    counts = bundle["capabilities"]["counts"]
    modules = {row["module_id"]: row for row in educator["selectable_modules"]}
    preface = "".join(_module_item(row, educator=True) for row in educator["front_matter_modules"])
    chapters = "".join(_chapter_block(row, modules, educator=True) for row in educator["chapter_summaries"])
    correction_rows = "".join(
        f"<li><code>{esc(status)}</code>: {count}</li>"
        for status, count in counts["correction_statuses"].items()
    )
    return shell(
        "A20 · Peta pengajar aljabar menengah",
        f"""
<p class="muted">A20 · tampilan pengajar · <code>{esc(CONTRACT)}</code></p>
<h1>Perencanaan dan tata kelola A20</h1>
<p class="lede">Pilih modul berdasarkan urutan, halaman, jumlah latihan, cakupan solusi, dan konsep. Semua pilihan memakai identitas native yang sama dengan peta pelajar.</p>
<div class="grid"><div class="card"><span class="metric">{counts['modules']}</span>modul</div><div class="card"><span class="metric">{counts['concepts']}</span>konsep</div><div class="card"><span class="metric">{counts['terms']}</span>istilah</div><div class="card"><span class="metric">{counts['corrections']}</span>koreksi</div><div class="card"><span class="metric">{counts['component_rights']}</span>rekaman hak</div></div>
<div class="notice"><strong>Batas klaim:</strong> ini bukan panduan guru resmi atau kunci jawaban lengkap. Pembaca Bahasa Indonesia berbasis halaman PDF; HTML semantik, MathML, PDF/UA, EPUB, kepatuhan WCAG, dan pertukaran reversibel tidak diklaim.</div>
<h2>Indeks tata kelola</h2><ul><li><a href="../data/exercise-index.jsonl">Identitas latihan, masalah, dan solusi</a></li><li><a href="../data/concept-index.jsonl">Konsep</a></li><li><a href="../data/terms-index.jsonl">Terminologi</a></li><li><a href="../data/corrections-index.jsonl">Koreksi</a></li><li><a href="../data/rights-index.jsonl">Hak per komponen</a></li><li><a href="../data/pedagogical-relation-index.jsonl">Relasi pedagogis</a></li><li><a href="../data/claim-boundary.json">Batas klaim mesin</a></li></ul>
<h2>Status koreksi native</h2><ul>{correction_rows}</ul>
<h2>Bagian awal</h2><ol class="module-list compact">{preface}</ol>
<h2>Pemilih bab dan modul</h2>{chapters}
""",
    )


def _fixture_bytes() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for fixture_id, path, operation, value, expected in NEGATIVE_FIXTURES:
        payload: dict[str, Any] = {
            "schema": "a20-negative-fixture/1",
            "fixture_id": fixture_id,
            "mutation": {"operation": operation, "path": path},
            "expected_error": expected,
        }
        if operation != "remove":
            payload["mutation"]["value"] = value
        files[f"fixtures/negative/{fixture_id}.json"] = canonical_json_bytes(payload)
    return files


def build(native_root: Path, adapter: Path, receipt_path: Path = PUBLIC_RECEIPT_PATH) -> dict[str, Any]:
    bundle = derive_projection(native_root, receipt_path)
    errors = projection_errors(bundle)
    if errors:
        raise ValueError(f"A20 native projection failed: {errors}")

    public_receipt = read_json(receipt_path)
    files = {
        "input/public-native-readback.json": canonical_json_bytes(public_receipt),
        "input/source-lock.json": canonical_json_bytes(bundle["source_lock"]),
        "data/native-record-ledger.json": canonical_json_bytes(bundle["native_record_ledger"]),
        "data/module-index.jsonl": canonical_jsonl_bytes(bundle["module_index"]),
        "data/exercise-index.jsonl": canonical_jsonl_bytes(bundle["exercise_index"]),
        "data/concept-index.jsonl": canonical_jsonl_bytes(bundle["concept_index"]),
        "data/pedagogical-relation-index.jsonl": canonical_jsonl_bytes(bundle["pedagogical_relation_index"]),
        "data/terms-index.jsonl": canonical_jsonl_bytes(bundle["terms_index"]),
        "data/corrections-index.jsonl": canonical_jsonl_bytes(bundle["corrections_index"]),
        "data/rights-index.jsonl": canonical_jsonl_bytes(bundle["rights_index"]),
        "data/learner-map.json": canonical_json_bytes(bundle["learner_map"]),
        "data/educator-map.json": canonical_json_bytes(bundle["educator_map"]),
        "data/public-evidence.json": canonical_json_bytes(bundle["public_evidence"]),
        "data/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "data/claim-boundary.json": canonical_json_bytes(bundle["claim_boundary"]),
        "views/A20.html": render_learner(bundle).encode("utf-8"),
        "views/A20-pengajar.html": render_educator(bundle).encode("utf-8"),
        "views/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "README.md": (
            "# A20 zero-copy intermediate-algebra capability adapter\n\n"
            "This adapter projects the complete pinned A20/R001 public native backend into "
            "`course-learning-capability/1`. It hash-binds 174,535 unique records and exposes "
            "83 modules, 8,209 exercise/problem identities, the exact 5,238/2,971 "
            "solved-versus-unsolved identity boundary, 236 concepts, 340 admitted terms, "
            "1,614 correction states, and 17 component-rights records.\n\n"
            "No textbook, segment, exercise, problem, or solution body is copied. The A10 "
            "prerequisite is a central-curriculum overlay. The Indonesian reader is a "
            "page-routed PDF; semantic HTML, MathML, PDF/UA, EPUB, portable offline HTML, "
            "WCAG conformance, an official teacher manual, and reversible exchange are not "
            "claimed. The separately verified English HTML surface is a presentation mirror "
            "of the original source, not a translation or a substitute common adapter.\n"
        ).encode("utf-8"),
        **_fixture_bytes(),
    }
    for relative, data in files.items():
        write_bytes(adapter / relative, data)

    manifest = {
        "schema": "a20-capability-manifest/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "native_family": "openstax_intermediate_algebra_2e",
        "content_policy": "identity_structure_terminology_rights_evidence_only",
        "native_release": {"commit": RELEASE_COMMIT, "tree": RELEASE_TREE},
        "projection": {
            "central_course_truth_rewritten": False,
            "component_rights_preserved": True,
            "exercise_solution_boundary_preserved": True,
            "external_hash_pinned_native_export_required_for_replay": True,
            "native_bodies_copied": False,
            "native_ids_preserved": True,
            "public_state_changed": False,
            "reversible_exchange_claimed": False,
            "stale_repository_landing_used_as_complete_authority": False,
        },
        "counts": bundle["capabilities"]["counts"],
        "inputs": bundle["source_lock"]["inputs"],
        "outputs": [identity(adapter / path, display_path=path) for path in sorted(files)],
        "validation_path": "validation.json",
        "package_receipt_path": "build/PACKET_BUILD_RECEIPT.json",
    }
    write_json(adapter / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--receipt", type=Path, default=PUBLIC_RECEIPT_PATH)
    args = parser.parse_args()
    manifest = build(args.native_root.resolve(), args.adapter.resolve(), args.receipt.resolve())
    print(
        canonical_json_bytes({
            "state": "pass",
            "course_id": COURSE_ID,
            "outputs": len(manifest["outputs"]),
            "native_records": manifest["counts"]["native_records"],
            "modules": manifest["counts"]["modules"],
            "exercises": manifest["counts"]["exercises"],
        }).decode("utf-8"),
        end="",
    )


if __name__ == "__main__":
    main()
