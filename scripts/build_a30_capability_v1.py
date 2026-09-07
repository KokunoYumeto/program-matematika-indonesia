"""Build the A30 zero-copy learner/educator capability adapter."""

from __future__ import annotations

import argparse
import html
from pathlib import Path
from typing import Any

from a30_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    EXPECTED_CANONICAL_SHA256,
    LOCALE,
    NATIVE_COURSE_ID,
    PUBLIC_RECEIPT_PATH,
    RELEASE_TAG,
    UPSTREAM_COMMIT,
    UPSTREAM_TREE,
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
:root{color-scheme:light;--ink:#18252e;--muted:#52616c;--paper:#f3efe6;--card:#fff;--line:#cad1d4;--accent:#126a63;--warn:#9b572e}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1160px;margin:auto;padding:28px 20px 64px}nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem}a{color:var(--accent);text-underline-offset:3px}
h1{font-size:clamp(2rem,5vw,3.4rem);line-height:1.06;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.12rem;max-width:78ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:1.5rem 0}.card,details,.notice{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{display:block;font-size:1.8rem;font-weight:760}.muted{color:var(--muted)}details{margin:.75rem 0}summary{cursor:pointer;font-weight:700}.notice{border-left:6px solid var(--warn)}code{overflow-wrap:anywhere}.module-list{display:grid;gap:.65rem;list-style:none;padding:0}.module{border-top:1px solid var(--line);padding-top:.65rem}.compact{font-size:.92rem}a:focus-visible,summary:focus-visible{outline:3px solid #d58a25;outline-offset:3px}
""".strip()


NEGATIVE_FIXTURES = (
    ("source-hash-drift", "source_lock.inputs[0].sha256", "replace", "00" * 32, "A30-SOURCE-LOCK"),
    ("native-sequence-drift", "native_record_ledger.id_sequence_sha256", "replace", "00" * 32, "A30-NATIVE-SEQUENCE"),
    ("dropped-module", "module_index[-1]", "remove", None, "A30-MODULE-INDEX"),
    ("dropped-exercise", "exercise_index[-1]", "remove", None, "A30-EXERCISE-COUNT"),
    ("invented-solution", "exercise_index[first_unsupported].solution_id", "replace", "urn:uuid:invented", "A30-SOLUTION-BOUNDARY"),
    ("collapsed-segment-asymmetry", "segment_state_summary.bucket_counts", "replace", {"id-ID|translated|active": 149955}, "A30-SEGMENT-STATE-ASYMMETRY"),
    ("copied-source-text", "learner_map.source_text", "add", "forbidden source text", "A30-COPIED-SOURCE-TARGET-BODY"),
    ("copied-target-text", "learner_map.target_text", "add", "forbidden target text", "A30-COPIED-SOURCE-TARGET-BODY"),
    ("copied-body", "learner_map.body", "add", "forbidden native body", "A30-COPIED-SOURCE-TARGET-BODY"),
    ("invented-native-prerequisite", "claim_boundary.native_course_prerequisites_invented", "replace", True, "A30-INVENTED-NATIVE-PREREQUISITE"),
    ("false-final-derivative-revision", "claim_boundary.final_derivative_git_revision_claimed", "replace", True, "A30-FALSE-CLAIM:final_derivative_git_revision_claimed"),
    ("invented-public-derivative-revision", "public_evidence.repository.final_derivative_commit", "replace", "0" * 40, "A30-FALSE-DERIVATIVE-REVISION"),
    ("false-semantic-html", "claim_boundary.indonesian_semantic_html_claimed", "replace", True, "A30-FALSE-CLAIM:indonesian_semantic_html_claimed"),
    ("false-mathml", "claim_boundary.indonesian_mathml_claimed", "replace", True, "A30-FALSE-CLAIM:indonesian_mathml_claimed"),
    ("false-epub", "claim_boundary.epub_claimed", "replace", True, "A30-FALSE-CLAIM:epub_claimed"),
    ("false-portable-html", "claim_boundary.portable_offline_html_claimed", "replace", True, "A30-FALSE-CLAIM:portable_offline_html_claimed"),
    ("false-pdfua", "claim_boundary.pdf_ua_claimed", "replace", True, "A30-FALSE-CLAIM:pdf_ua_claimed"),
    ("false-wcag", "claim_boundary.wcag_conformance_claimed", "replace", True, "A30-FALSE-CLAIM:wcag_conformance_claimed"),
    ("false-labs", "claim_boundary.interactive_labs_claimed", "replace", True, "A30-FALSE-CLAIM:interactive_labs_claimed"),
    ("false-runtime", "claim_boundary.learning_runtime_claimed", "replace", True, "A30-FALSE-CLAIM:learning_runtime_claimed"),
    ("false-teacher-manual", "claim_boundary.official_teacher_manual_claimed", "replace", True, "A30-FALSE-CLAIM:official_teacher_manual_claimed"),
    ("false-exhaustive-exercise-routes", "claim_boundary.exhaustive_exercise_pdf_destinations_claimed", "replace", True, "A30-FALSE-CLAIM:exhaustive_exercise_pdf_destinations_claimed"),
    ("injected-exercise-route", "exercise_index[0].public_route", "add", "https://example.invalid/", "A30-EXHAUSTIVE-EXERCISE-DESTINATIONS"),
    ("false-standalone-raw-replay", "claim_boundary.standalone_raw_replay_claimed", "replace", True, "A30-FALSE-CLAIM:standalone_raw_replay_claimed"),
    ("false-reversibility", "claim_boundary.reversible_exchange_claimed", "replace", True, "A30-FALSE-CLAIM:reversible_exchange_claimed"),
    ("flattened-rights", "rights_index", "replace", [{"id": "all"}], "A30-RIGHTS-FLATTENED"),
    ("bad-module-route", "module_index[0].public_route", "replace", "https://example.invalid/", "A30-MODULE-ROUTE"),
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>"
        '<nav><a href="A30.html">Pelajar</a><a href="A30-pengajar.html">Pengajar</a>'
        '<a href="capabilities.json">Kapabilitas JSON</a></nav>'
        f"{body}</main></body></html>\n"
    )


def _module_item(row: dict[str, Any], *, educator: bool = False) -> str:
    governance = f" · {row['concept_count']} konsep · <code>{esc(row['module_unit_id'])}</code>" if educator else ""
    return (
        '<li class="module">'
        f'<a href="{esc(row["public_route"])}"><strong>{row["ordinal"]}. Modul {esc(row["module_id"])}</strong></a>'
        f' <span class="muted">(hlm. {row["start_page"]}, {row["page_span"]} halaman)</span><br>'
        f'{row["exercise_count"]} latihan · {row["solution_identity_count"]} didukung identitas solusi · '
        f'{row["unsupported_exercise_count"]} tanpa dukungan identitas solusi{governance}</li>'
    )


def _chapter_block(chapter: dict[str, Any], modules: dict[str, dict[str, Any]], *, educator: bool = False) -> str:
    rows = "".join(_module_item(modules[module_id], educator=educator) for module_id in chapter["module_ids"])
    return (
        f'<details><summary>Bab {chapter["ordinal"]} · {chapter["module_count"]} modul · '
        f'{chapter["exercise_count"]} latihan</summary>'
        f'<p><a href="{esc(chapter["public_route"])}">Mulai pada halaman {chapter["start_page"]}</a></p>'
        f'<ol class="module-list compact">{rows}</ol></details>'
    )


def render_learner(bundle: dict[str, Any]) -> str:
    learning = bundle["learner_map"]
    counts = bundle["capabilities"]["counts"]
    modules = {row["module_id"]: row for row in learning["modules"]}
    front = "".join(_module_item(row) for row in learning["front_matter_modules"])
    chapters = "".join(_chapter_block(row, modules) for row in learning["chapters"])
    back = "".join(_module_item(row) for row in learning["back_matter_modules"])
    return shell(
        "A30 · Peta belajar prakalkulus",
        f"""
<p class="muted">A30 · <code>{esc(CONTRACT)}</code> · <code>{esc(NATIVE_COURSE_ID)}</code></p>
<h1>Peta belajar A30</h1>
<p class="lede">Adapter metadata tipis ini menghubungkan 87 modul dan identitas latihan ke edisi Bahasa Indonesia. Teks sumber, teks target, serta isi buku tetap berada di edisi native yang dipreservasi.</p>
<div class="grid"><div class="card"><span class="metric">{counts['pdf_pages']}</span>halaman</div><div class="card"><span class="metric">{counts['modules']}</span>modul</div><div class="card"><span class="metric">{counts['exercises']}</span>latihan</div><div class="card"><span class="metric">{counts['solution_identities']}</span>identitas solusi</div></div>
<p>Prasyarat kurikulum: <code>A20</code> <span class="muted">(lapisan kurikulum pusat, bukan klaim native).</span> <a href="{esc(learning['indonesian_reader']['url'])}">Buka pembaca Bahasa Indonesia</a>.</p>
<div class="notice"><strong>Batas dukungan solusi:</strong> {counts['solution_identities']} dari {counts['exercises']} latihan memiliki identitas solusi native; {counts['unsupported_exercises']} tidak. Adapter tidak mengarang solusi, tidak menyalin isi latihan atau solusi, dan tidak mengklaim tujuan PDF per latihan.</div>
<h2>Bagian awal</h2><ol class="module-list compact">{front}</ol>
<h2>Bab dan modul</h2>{chapters}
<h2>Bagian akhir</h2><ol class="module-list compact">{back}</ol>
""",
    )


def render_educator(bundle: dict[str, Any]) -> str:
    educator = bundle["educator_map"]
    counts = bundle["capabilities"]["counts"]
    modules = {row["module_id"]: row for row in educator["selectable_modules"]}
    front = "".join(_module_item(row, educator=True) for row in educator["front_matter_modules"])
    chapters = "".join(_chapter_block(row, modules, educator=True) for row in educator["chapter_summaries"])
    back = "".join(_module_item(row, educator=True) for row in educator["back_matter_modules"])
    correction_rows = "".join(f"<li><code>{esc(status)}</code>: {count}</li>" for status, count in counts["correction_statuses"].items())
    segment_rows = "".join(f"<li><code>{esc(bucket)}</code>: {count}</li>" for bucket, count in counts["segment_state_bucket_counts"].items())
    return shell(
        "A30 · Peta pengajar prakalkulus",
        f"""
<p class="muted">A30 · tampilan pengajar · <code>{esc(CONTRACT)}</code></p>
<h1>Perencanaan dan tata kelola A30</h1>
<p class="lede">Pilih modul berdasarkan urutan, halaman, jumlah latihan, batas dukungan solusi, dan konsep. Semua pilihan memakai identitas native tanpa menyalin teks sumber atau target.</p>
<div class="grid"><div class="card"><span class="metric">{counts['modules']}</span>modul</div><div class="card"><span class="metric">{counts['concepts']}</span>konsep</div><div class="card"><span class="metric">{counts['terms']}</span>istilah</div><div class="card"><span class="metric">{counts['corrections']}</span>koreksi</div><div class="card"><span class="metric">{counts['component_rights']}</span>rekaman hak</div></div>
<div class="notice"><strong>Batas klaim:</strong> ini bukan panduan guru resmi, laboratorium interaktif, runtime pembelajaran, atau kunci jawaban lengkap. HTML semantik, MathML, EPUB, HTML luring portabel, PDF/UA, kepatuhan WCAG, tujuan PDF per latihan, replay mentah mandiri, dan pertukaran reversibel tidak diklaim.</div>
<h2>Indeks tata kelola</h2><ul><li><a href="../data/exercise-index.jsonl">Identitas latihan, masalah, dan solusi</a></li><li><a href="../data/concept-index.jsonl">Identitas konsep</a></li><li><a href="../data/terms-index.jsonl">Status terminologi tanpa teks istilah</a></li><li><a href="../data/corrections-index.jsonl">Status koreksi tanpa teks koreksi</a></li><li><a href="../data/rights-index.jsonl">Hak per komponen</a></li><li><a href="../data/pedagogical-relation-index.jsonl">Relasi native</a></li><li><a href="../data/segment-state-summary.json">Asimetri status segmen</a></li><li><a href="../data/claim-boundary.json">Batas klaim mesin</a></li></ul>
<h2>Status koreksi native</h2><ul>{correction_rows}</ul>
<h2>Status segmen native</h2><ul>{segment_rows}</ul>
<h2>Bagian awal</h2><ol class="module-list compact">{front}</ol>
<h2>Pemilih bab dan modul</h2>{chapters}
<h2>Bagian akhir</h2><ol class="module-list compact">{back}</ol>
""",
    )


def _fixture_bytes() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for fixture_id, path, operation, value, expected in NEGATIVE_FIXTURES:
        payload: dict[str, Any] = {
            "schema": "a30-negative-fixture/1",
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
        raise ValueError(f"A30 native projection failed: {errors}")

    public_receipt = read_json(receipt_path)
    files = {
        "input/public-native-readback.json": canonical_json_bytes(public_receipt),
        "input/source-lock.json": canonical_json_bytes(bundle["source_lock"]),
        "data/native-record-ledger.json": canonical_json_bytes(bundle["native_record_ledger"]),
        "data/segment-state-summary.json": canonical_json_bytes(bundle["segment_state_summary"]),
        "data/chapter-index.jsonl": canonical_jsonl_bytes(bundle["chapter_index"]),
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
        "views/A30.html": render_learner(bundle).encode("utf-8"),
        "views/A30-pengajar.html": render_educator(bundle).encode("utf-8"),
        "views/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "README.md": (
            "# A30 zero-copy precalculus capability adapter\n\n"
            "This adapter projects the complete public A30/R002 1.0.0 native backend into "
            "`course-learning-capability/1`. It hash-binds 220,680 canonical records and exposes "
            "87 modules, 7,250 exercise/problem identities, the exact 4,183/3,067 "
            "solution-supported/unsupported boundary, 497 concepts, 513 term-status records, "
            "703 correction-status records, 1,875 component-rights records, 149,955 segment "
            "state records as an asymmetric summary, and all 37,974 native relations.\n\n"
            "No source text, target text, textbook body, segment text, exercise/problem body, or "
            "solution body is copied. A20 is a CENTRAL curriculum prerequisite overlay only; the "
            "native A30 record asserts no prerequisite. The public 1.0.0 release and the upstream "
            "source commit/tree are proved, but no final derivative Git commit or tree is claimed.\n\n"
            "The Indonesian delivery is a module-page-routed PDF. Semantic HTML, MathML, EPUB, "
            "portable offline HTML, PDF/UA, WCAG conformance, interactive labs, a learning runtime, "
            "an official teacher manual, exhaustive exercise PDF destinations, standalone raw "
            "replay, and reversible exchange are not claimed. Full replay requires the separately "
            "preserved source companion and the public backend archive pinned by SHA-256.\n"
        ).encode("utf-8"),
        **_fixture_bytes(),
    }
    for relative, data in files.items():
        write_bytes(adapter / relative, data)

    manifest = {
        "schema": "a30-capability-manifest/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "native_family": "openstax_precalculus_2e",
        "content_policy": "native_identity_structure_status_rights_evidence_only_no_source_target_or_body_text",
        "upstream_source": {"commit": UPSTREAM_COMMIT, "tree": UPSTREAM_TREE},
        "public_release": {
            "tag": RELEASE_TAG,
            "complete": True,
            "final_derivative_commit": None,
            "final_derivative_tree": None,
            "final_derivative_revision_proved": False,
        },
        "projection": {
            "central_course_truth_rewritten": False,
            "component_rights_preserved": True,
            "exercise_solution_boundary_preserved": True,
            "segment_state_asymmetry_preserved": True,
            "external_hash_pinned_public_backend_required_for_replay": True,
            "source_companion_required_for_full_replay": True,
            "native_bodies_copied": False,
            "source_or_target_text_copied": False,
            "native_ids_preserved": True,
            "public_state_changed": False,
            "standalone_raw_replay_claimed": False,
            "reversible_exchange_claimed": False,
        },
        "canonical_jsonl_sha256": EXPECTED_CANONICAL_SHA256,
        "counts": bundle["capabilities"]["counts"],
        "inputs": bundle["source_lock"]["inputs"],
        "outputs": [identity(adapter / path, display_path=path) for path in sorted(files)],
        "tooling_scripts": [
            "scripts/a30_capability_model_v1.py",
            "scripts/build_a30_capability_v1.py",
            "scripts/validate_a30_capability_v1.py",
            "scripts/package_a30_capability_v1.py",
            "scripts/verify_a30_native_public_v1.py",
        ],
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
    print(canonical_json_bytes({
        "state": "pass",
        "course_id": COURSE_ID,
        "outputs": len(manifest["outputs"]),
        "native_records": manifest["counts"]["native_records"],
        "modules": manifest["counts"]["modules"],
        "exercises": manifest["counts"]["exercises"],
    }).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
