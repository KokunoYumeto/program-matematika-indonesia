"""Build the B90 zero-copy learner/educator capability adapter."""

from __future__ import annotations

import argparse
import html
from pathlib import Path
from typing import Any

from b90_capability_model_v1 import (
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
h1{font-size:clamp(2rem,5vw,3.4rem);line-height:1.06;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.12rem;max-width:78ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:1.5rem 0}.card,details,.notice{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{display:block;font-size:1.8rem;font-weight:760}.muted{color:var(--muted)}details{margin:.75rem 0}summary{cursor:pointer;font-weight:700}.notice{border-left:6px solid var(--warn)}code{overflow-wrap:anywhere}.index{columns:2;column-width:330px}.index li{break-inside:avoid;margin:.35rem 0}.compact{font-size:.92rem}a:focus-visible,summary:focus-visible{outline:3px solid #d58a25;outline-offset:3px}
""".strip()


NEGATIVE_FIXTURES = (
    ("hash-drift", "source_lock.inputs[0].sha256", "replace", "00" * 32, "B90-SOURCE-LOCK"),
    ("altered-native-id", "native_record_index[0].id", "replace", "urn:interlanguage:r010:changed", "B90-NATIVE-ID-SEQUENCE"),
    ("dropped-native-id", "native_record_index[-1]", "remove", None, "B90-NATIVE-ID-COUNT"),
    ("copied-body", "learner_map.body", "add", "forbidden native body", "B90-COPIED-NATIVE-BODY"),
    ("copied-segment-text", "claim_boundary.target_segment_text_copied", "replace", 1, "B90-SEGMENT-TEXT-COPIED"),
    ("false-solutions", "claim_boundary.answers_or_solutions_claimed", "replace", True, "B90-FALSE-CLAIM:answers_or_solutions_claimed"),
    ("false-semantic-html", "public_evidence.reader.semantic_html_established", "replace", True, "B90-FALSE-SEMANTIC-HTML"),
    ("false-wcag", "claim_boundary.wcag_conformance_claimed", "replace", True, "B90-FALSE-WCAG"),
    ("false-reversibility", "claim_boundary.reversible_exchange_claimed", "replace", True, "B90-FALSE-REVERSIBILITY"),
    ("flattened-rights", "rights_index", "replace", [{"id": "all"}], "B90-RIGHTS-FLATTENED"),
    ("exposed-supplement", "claim_boundary.excluded_supplement_records_exposed", "replace", 1, "B90-EXCLUDED-SUPPLEMENT-EXPOSED"),
    ("bad-chapter-route", "learner_map.chapters[0].public_route", "replace", "https://example.invalid/", "B90-CHAPTER-ROUTE"),
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>"
        '<nav><a href="B90.html">Pelajar</a><a href="B90-pengajar.html">Pengajar</a>'
        '<a href="capabilities.json">Kapabilitas JSON</a></nav>'
        f"{body}</main></body></html>\n"
    )


def _section_block(section: dict[str, Any]) -> str:
    exercises = "".join(
        f'<li><a href="{esc(section["public_route"])}"><code>{esc(exercise_id)}</code></a></li>'
        for exercise_id in section["exercise_ids"]
    )
    fragments = "".join(f"<li><code>{esc(item)}</code></li>" for item in section["section_fragment_ids"])
    extra = f"<p>Fragmen bagian:</p><ul>{fragments}</ul>" if fragments else ""
    return (
        f'<details><summary>Bagian {esc(section["section"])} · {len(section["exercise_ids"])} latihan</summary>'
        f'<p><a href="{esc(section["public_route"])}">Buka konteks bab di pembaca native</a> · '
        '<span class="muted">tautan ini menuju awal bab; bukan jangkar semantik per latihan.</span></p>'
        f'<ol class="index compact">{exercises}</ol>{extra}</details>'
    )


def render_learner(bundle: dict[str, Any]) -> str:
    learning = bundle["learner_map"]
    counts = bundle["capabilities"]["counts"]
    chapters = "".join(
        f'<details><summary>Bab {row["chapter"]} · {esc(row["title_id"])} · {row["exercise_count"]} latihan</summary>'
        f'<p><a href="{esc(row["public_route"])}">Buka halaman {row["start_page"]}</a></p>'
        + "".join(_section_block(section) for section in row["sections"])
        + "</details>"
        for row in learning["chapters"]
    )
    return shell(
        "B90 · Peta belajar peluang",
        f"""
<p class="muted">B90 · <code>{esc(CONTRACT)}</code> · <code>{esc(NATIVE_COURSE_ID)}</code></p>
<h1>Peta belajar B90</h1>
<p class="lede">Adapter tipis ini menghubungkan struktur bab, bagian, dan identitas latihan ke pembaca peluang Bahasa Indonesia. Isi buku tetap berada di edisi native.</p>
<div class="grid"><div class="card"><span class="metric">{counts['chapters']}</span>bab</div><div class="card"><span class="metric">{counts['sections']}</span>bagian</div><div class="card"><span class="metric">{counts['exercises']}</span>identitas latihan</div><div class="card"><span class="metric">0</span>jawaban/solusi publik diklaim</div></div>
<p>Prasyarat: <code>B30</code>. <a href="{esc(learning['reader']['home'])}">Buka pembaca native</a> · <a href="{esc(learning['reader']['pdf'])}">Unduh PDF</a> · <a href="{esc(learning['reader']['index_route'])}">Indeks, halaman 547</a></p>
<div class="notice"><strong>Batas klaim:</strong> ekspor publik sengaja tidak memuat suplemen jawaban. Adapter tidak menyalin isi segmen dan tidak mengklaim HTML semantik, MathML, EPUB, kepatuhan WCAG, atau paket luring portabel.</div>
<h2>Bab, bagian, dan latihan</h2>{chapters}
""",
    )


def render_educator(bundle: dict[str, Any]) -> str:
    educator = bundle["educator_map"]
    counts = bundle["capabilities"]["counts"]
    correction_rows = "".join(
        f"<li><code>{esc(status)}</code>: {count}</li>"
        for status, count in educator["correction_status_counts"].items()
    )
    units = "".join(
        f'<li><a href="{esc(row["public_route"])}"><code>{esc(row["id"])}</code></a> · {esc(row["kind"])} · {esc(row["route_precision"])}</li>'
        for row in educator["selectable_units"]
    )
    return shell(
        "B90 · Peta pengajar peluang",
        f"""
<p class="muted">B90 · tampilan pengajar · <code>{esc(CONTRACT)}</code></p>
<h1>Perencanaan dan tata kelola B90</h1>
<p class="lede">Pilih identitas unit yang sama dengan peta pelajar, lalu buka konteks bab native. Indeks konsep, istilah, koreksi, relasi, dan hak tetap terpisah dan dapat diproses mesin.</p>
<div class="grid"><div class="card"><span class="metric">{counts['units']}</span>unit</div><div class="card"><span class="metric">{counts['concepts']}</span>konsep</div><div class="card"><span class="metric">{counts['terms']}</span>istilah</div><div class="card"><span class="metric">{counts['corrections']}</span>koreksi</div><div class="card"><span class="metric">{counts['component_rights']}</span>rekaman hak</div></div>
<div class="notice"><strong>Batas klaim:</strong> ini bukan panduan guru atau kunci jawaban. Sebanyak {counts['excluded_answer_records']} rekaman jawaban berada dalam suplemen yang sengaja dikeluarkan dari ekspor publik; status itu dipertahankan, bukan diisi atau disamarkan.</div>
<h2>Status koreksi native</h2><ul>{correction_rows}</ul>
<h2>Indeks tata kelola</h2><ul><li><a href="../data/concept-index.jsonl">Konsep</a></li><li><a href="../data/terms-index.jsonl">Terminologi</a></li><li><a href="../data/corrections-index.jsonl">Koreksi</a></li><li><a href="../data/rights-index.jsonl">Hak per komponen</a></li><li><a href="../data/relation-index.jsonl">Relasi</a></li><li><a href="../data/claim-boundary.json">Batas klaim mesin</a></li></ul>
<h2>Semua identitas unit</h2><ol class="index compact">{units}</ol>
""",
    )


def _fixture_bytes() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for fixture_id, path, operation, value, expected in NEGATIVE_FIXTURES:
        payload: dict[str, Any] = {
            "schema": "b90-negative-fixture/1",
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
        raise ValueError(f"B90 native projection failed: {errors}")

    public_receipt = read_json(receipt_path)
    files = {
        "input/public-native-readback.json": canonical_json_bytes(public_receipt),
        "input/source-lock.json": canonical_json_bytes(bundle["source_lock"]),
        "data/native-record-index.jsonl": canonical_jsonl_bytes(bundle["native_record_index"]),
        "data/unit-index.jsonl": canonical_jsonl_bytes(bundle["unit_index"]),
        "data/concept-index.jsonl": canonical_jsonl_bytes(bundle["concept_index"]),
        "data/relation-index.jsonl": canonical_jsonl_bytes(bundle["relation_index"]),
        "data/terms-index.jsonl": canonical_jsonl_bytes(bundle["terms_index"]),
        "data/corrections-index.jsonl": canonical_jsonl_bytes(bundle["corrections_index"]),
        "data/rights-index.jsonl": canonical_jsonl_bytes(bundle["rights_index"]),
        "data/learner-map.json": canonical_json_bytes(bundle["learner_map"]),
        "data/educator-map.json": canonical_json_bytes(bundle["educator_map"]),
        "data/public-evidence.json": canonical_json_bytes(bundle["public_evidence"]),
        "data/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "data/claim-boundary.json": canonical_json_bytes(bundle["claim_boundary"]),
        "views/B90.html": render_learner(bundle).encode("utf-8"),
        "views/B90-pengajar.html": render_educator(bundle).encode("utf-8"),
        "views/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "README.md": (
            "# B90 zero-copy probability capability adapter\n\n"
            "This adapter projects the pinned B90/R010 public-safe native backend into "
            "`course-learning-capability/1`. It preserves all 4,716 public native identities, "
            "the 800-unit hierarchy, 711 exercise identities, B30 prerequisite, terminology, "
            "correction states, component rights, and exact public evidence.\n\n"
            "No source or Indonesian segment body is copied. The excluded 1,159-record "
            "supplement boundary, including 287 answer records, remains excluded. The native "
            "reader is page-based PDF.js; semantic HTML, MathML, EPUB, portable offline use, "
            "WCAG conformance, teacher-manual status, solutions, learner results, and reversible "
            "exchange are not claimed.\n"
        ).encode("utf-8"),
        **_fixture_bytes(),
    }
    for relative, data in files.items():
        write_bytes(adapter / relative, data)

    manifest = {
        "schema": "b90-capability-manifest/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "native_family": "grinstead_snell_probability",
        "content_policy": "identity_structure_terminology_rights_evidence_only",
        "native_release": {"commit": RELEASE_COMMIT, "tree": RELEASE_TREE},
        "projection": {
            "central_course_truth_rewritten": False,
            "component_rights_preserved": True,
            "excluded_supplement_boundary_preserved": True,
            "external_pinned_native_checkout_required_for_replay": True,
            "native_bodies_copied": False,
            "native_ids_preserved": True,
            "public_state_changed": False,
            "reversible_exchange_claimed": False,
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
        canonical_json_bytes(
            {
                "state": "pass",
                "course_id": COURSE_ID,
                "outputs": len(manifest["outputs"]),
                "native_records": manifest["counts"]["native_records"],
                "units": manifest["counts"]["units"],
                "exercises": manifest["counts"]["exercises"],
            }
        ).decode("utf-8"),
        end="",
    )


if __name__ == "__main__":
    main()
