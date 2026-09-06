"""Build the C60 learner/educator capability adapter from pinned R014 evidence."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from c60_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    CURRENT_PUBLIC_HEAD,
    LOCALE,
    NATIVE_ROLE_ID,
    PAGES_URL,
    RELEASE_VERSION,
    REPOSITORY,
    canonical_json_bytes,
    derive_projection,
    identity,
    projection_errors,
    write_json,
)


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
DEFAULT_NATIVE = WORKSPACE / "04_mirrors/id/yet-another-introductory-number-theory-textbook-id/publication/github-pages-sync"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/c60-capability-v1"

STYLE = """
:root{color-scheme:light;--ink:#17222c;--muted:#586776;--paper:#f2f4f2;--card:#fff;--line:#cbd5d0;--accent:#175c4b;--link:#135d7a;--warn:#8a4b12}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}main{max-width:1180px;margin:auto;padding:28px 20px 70px}
nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.4rem}a{color:var(--link);text-underline-offset:3px}h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.06;margin:.2rem 0 1rem}h2{margin-top:2.1rem}.lede{font-size:1.14rem;max-width:82ch}.muted{color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:1.5rem 0}.card,details,.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{display:block;font-size:1.8rem;font-weight:780}
details{margin:.75rem 0}summary{cursor:pointer;font-weight:740}.block-head{display:flex;justify-content:space-between;gap:1rem;align-items:baseline;flex-wrap:wrap}.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:.1rem .55rem;font-size:.85rem}.notice{border-left:6px solid var(--warn);background:#fff8ef;padding:1rem 1.2rem;border-radius:8px}
.controls{display:flex;gap:.7rem;flex-wrap:wrap;align-items:end;margin:1rem 0}.controls label{display:grid;gap:.25rem;font-weight:650}.controls input[type=search]{min-width:min(32rem,82vw);padding:.7rem;border:1px solid #87938d;border-radius:7px;font:inherit}button{padding:.65rem .9rem;border:1px solid #124b3e;border-radius:7px;background:var(--accent);color:#fff;font:inherit;font-weight:700;cursor:pointer}button.secondary{background:#fff;color:var(--accent)}
.select-row{display:grid;grid-template-columns:auto minmax(0,1fr) minmax(12rem,auto);gap:.8rem;align-items:start;border-bottom:1px solid var(--line);padding:.72rem 0}.select-row:last-child{border-bottom:0}.select-row input{width:1.2rem;height:1.2rem}.right{text-align:right}.hidden{display:none!important}code{overflow-wrap:anywhere}.small{font-size:.9rem}.section-list{columns:2;column-gap:2rem}.section-list li{break-inside:avoid;margin:.35rem 0}
a:focus-visible,summary:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #d58c2d;outline-offset:3px}@media(max-width:700px){.select-row{grid-template-columns:auto 1fr}.select-row .right{grid-column:2;text-align:left}.section-list{columns:1}}
""".strip()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>'
        '<nav><a href="../../id/#course-C60">Program matematika</a>'
        '<a href="../index.html">Pusat backend</a>'
        '<a href="C60.html">Pelajar</a><a href="C60-pengajar.html">Pengajar</a></nav>'
        f"{body}</main></body></html>\n"
    )


def render_learner(bundle: dict) -> str:
    counts = bundle["capabilities"]["counts"]
    chapters = bundle["educator_map"]["chapter_routes"]
    blocks = []
    for chapter in chapters:
        sections = "".join(
            f'<li><a href="{esc(section["public_reader_url"])}">{esc(section["number"])} {esc(section["title"])}</a> '
            f'<span class="small"><code>{esc(section["native_unit_id"])}</code></span></li>'
            for section in chapter["sections"]
        )
        blocks.append(
            f'<details class="chapter" data-search="{esc((chapter["title"] + " " + " ".join(row["title"] for row in chapter["sections"])).lower())}">'
            f'<summary><span class="block-head"><span>Bab {esc(chapter["chapter_number"])} · {esc(chapter["title"])}</span>'
            f'<span class="pill">{chapter["unit_count"]} unit · {chapter["concept_count"]} konsep</span></span></summary>'
            f'<p><a href="{esc(chapter["public_reader_url"])}">Baca bab pada pembaca reflow</a> · <code>{esc(chapter["native_unit_id"])}</code></p>'
            f'<ul class="section-list">{sections}</ul></details>'
        )
    body = f"""
<p class="muted">C60 · <code>{NATIVE_ROLE_ID}</code> · rilis native {RELEASE_VERSION} · pembaca publik <code>{CURRENT_PUBLIC_HEAD[:12]}</code></p>
<h1>Teori Bilangan dan Kriptologi</h1>
<p class="lede">Jalur zero-copy ke edisi Bahasa Indonesia <em>Satu Lagi Buku Teks Pengantar Teori Bilangan</em>. Lima bab dan 27 bagian membuka pembaca HTML reflow secara langsung; indeks mesin mempertahankan seluruh 5.272 ID native tanpa menggandakan badan buku.</p>
<div class="grid" aria-label="Ringkasan kursus">
<div class="card"><span class="metric">{counts['learner_chapters']}</span>bab</div>
<div class="card"><span class="metric">{counts['learner_sections']}</span>bagian</div>
<div class="card"><span class="metric">{counts['units']}</span>ID unit</div>
<div class="card"><span class="metric">{counts['native_exercise_units']}</span>unit latihan native</div>
<div class="card"><span class="metric">{counts['concepts']}</span>konsep</div>
<div class="card"><span class="metric">{counts['reader_pdf_pages']}</span>halaman PDF</div>
</div>
<p><a href="{PAGES_URL}reader/index.html">Buka pembaca HTML</a> · <a href="{PAGES_URL}YAINTT_ID.pdf">Buka PDF</a> · <a href="learning-map.json">Peta kapabilitas common</a> · <a href="concept-index.json">Indeks konsep</a></p>
<div class="notice"><strong>Batas kebenaran:</strong> 101 identitas latihan berasal dari backend native. Adapter tidak membuat soal baru, petunjuk, pemeriksaan, solusi, asesmen, hasil pelajar, atau eksekusi langsung. Setiap dukungan pada peta common ditandai <code>not_present</code>/<code>source_has_none</code>.</div>
<div class="controls"><label>Cari bab atau bagian<input id="chapter-filter" type="search" placeholder="contoh: kongruensi, RSA, akar primitif"></label><span id="match-count" aria-live="polite">5 bab</span></div>
<h2>Rute belajar</h2>{''.join(blocks)}
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in bundle['learning_map']['limitations'])}</ul>
<script>const f=document.getElementById('chapter-filter'),rows=[...document.querySelectorAll('.chapter')],n=document.getElementById('match-count');f.addEventListener('input',()=>{{const q=f.value.trim().toLowerCase();let c=0;for(const row of rows){{const show=!q||row.dataset.search.includes(q);row.classList.toggle('hidden',!show);if(show)c++;}}n.textContent=c+' bab';}});</script>
"""
    return shell("C60 · Teori Bilangan dan Kriptologi", body)


def render_educator(bundle: dict) -> str:
    educator = bundle["educator_map"]
    counts = educator["counts"]
    units = educator["selector"]["units"]
    rows = []
    for unit in units:
        title = unit.get("title_id") or unit.get("title_en") or unit["unit_id"]
        state = "efektif" if unit["effective"] else f'disupersesi oleh {unit["superseded_by"]}'
        search = " ".join([unit["unit_id"], title, unit["kind"], " ".join(unit["concept_ids"])]).lower()
        rows.append(
            f'<label class="select-row unit-row" data-search="{esc(search)}"><input class="unit-select" type="checkbox" value="{esc(unit["unit_id"])}" aria-label="Pilih {esc(title)}">'
            f'<span><strong>{esc(title)}</strong><br><code>{esc(unit["unit_id"])}</code><br><span class="small">{esc(state)}</span></span>'
            f'<span class="right">{esc(unit["kind"])} · {len(unit["segment_ids"])} segmen<br>{len(unit["concept_ids"])} konsep · <a href="{esc(unit["reader_route"]["url"])}">buka konteks</a></span></label>'
        )
    selection_data = json.dumps({"units": units}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).replace("</", "<\\/")
    body = f"""
<p class="muted">C60 · tampilan pengajar · <code>{CONTRACT}</code></p>
<h1>Pemilih unit native</h1>
<p class="lede">Pilih dari seluruh 548 unit native. Ekspor JSON membawa ID, hierarki, hash, konsep, koreksi, status supersesi, dan rute pembaca—tanpa badan buku.</p>
<div class="grid" aria-label="Ringkasan bukti">
<div class="card"><span class="metric">{counts['native_records']:,}</span>ID native</div>
<div class="card"><span class="metric">{counts['effective_units']}</span>unit efektif</div>
<div class="card"><span class="metric">{counts['superseded_units']}</span>unit disupersesi</div>
<div class="card"><span class="metric">{counts['unit_direct_reader_routes']}</span>rute unit eksak</div>
<div class="card"><span class="metric">{counts['terms']}</span>istilah</div>
<div class="card"><span class="metric">{counts['corrections']}</span>koreksi</div>
</div>
<div class="notice"><strong>Tidak ada dukungan yang direka:</strong> backend memuat 101 unit latihan tetapi tidak memiliki rekaman solusi native. Peta common mempertahankan keadaan <code>source_has_none</code> untuk petunjuk, pemeriksaan, dan solusi.</div>
<div class="controls"><label>Saring unit<input id="teacher-filter" type="search" placeholder="judul, ID, jenis, atau konsep"></label><button id="select-visible" type="button">Pilih yang terlihat</button><button id="clear" class="secondary" type="button">Kosongkan</button><button id="export" type="button">Ekspor JSON</button><span id="selected-count" aria-live="polite">0 dipilih</span></div>
<div class="panel" id="unit-list">{''.join(rows)}</div>
<h2>Bukti dan data</h2><p><a href="educator-map.json">Peta pengajar</a> · <a href="native-id-index.json">5.272 ID native</a> · <a href="concept-index.json">223 konsep</a> · <a href="relation-index.json">3.297 relasi</a> · <a href="rights-and-terms.json">Hak, istilah, dan koreksi</a> · <a href="validation.json">Validasi</a></p>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in educator['limitations'])}</ul>
<script id="selection-data" type="application/json">{selection_data}</script>
<script>const data=JSON.parse(document.getElementById('selection-data').textContent),byId=new Map(data.units.map(x=>[x.unit_id,x])),rows=[...document.querySelectorAll('.unit-row')],boxes=[...document.querySelectorAll('.unit-select')],filter=document.getElementById('teacher-filter'),count=document.getElementById('selected-count');function update(){{count.textContent=boxes.filter(x=>x.checked).length+' dipilih';}}filter.addEventListener('input',()=>{{const q=filter.value.trim().toLowerCase();for(const row of rows)row.classList.toggle('hidden',!!q&&!row.dataset.search.includes(q));}});for(const box of boxes)box.addEventListener('change',update);document.getElementById('select-visible').addEventListener('click',()=>{{for(const row of rows)if(!row.classList.contains('hidden'))row.querySelector('input').checked=true;update();}});document.getElementById('clear').addEventListener('click',()=>{{for(const box of boxes)box.checked=false;update();}});document.getElementById('export').addEventListener('click',()=>{{const selected=boxes.filter(x=>x.checked).map(x=>byId.get(x.value));const payload={{schema:'c60-educator-selection/1',course_id:'C60',locale:'id-ID',native_bodies_copied:false,assessment_functionality:false,live_execution:false,selected_units:selected}};const blob=new Blob([JSON.stringify(payload,null,2)+'\\n'],{{type:'application/json'}}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='C60-rencana-pengajar.json';a.click();URL.revokeObjectURL(url);}});</script>
"""
    return shell("C60 · Pemilih pengajar", body)


NEGATIVE_FIXTURES = [
    "source_head_change", "backend_tree_change", "source_input_loss", "source_hash_change",
    "native_id_loss", "native_id_duplicate", "native_class_count_change", "unit_loss",
    "unit_order_change", "supersession_loss", "chapter_loss", "section_loss",
    "unit_route_loss", "exact_route_loss", "common_unit_loss", "native_exercise_loss",
    "exercise_support_invention", "concept_loss", "concept_route_loss", "relation_loss",
    "relation_type_change", "derived_relation_invention", "terminology_loss", "correction_loss",
    "rights_loss", "blanket_license_claim", "migration_replay_loss", "migration_mapping_change",
    "migration_roundtrip_change", "native_body_copy", "assessment_invention", "learner_result_invention",
    "live_execution_claim", "accessibility_conformance_claim", "offline_dependency_overclaim",
    "central_truth_rewrite", "historical_receipt_rewrite", "virtual_backend_materialization",
    "excluded_destination_activation", "public_state_change", "attribution_value_copy",
]


def build(native_root: Path, hub_root: Path, adapter: Path) -> dict:
    bundle = derive_projection(native_root, hub_root)
    errors = projection_errors(bundle)
    if errors:
        raise ValueError(f"C60 projection failed: {errors}")
    files = {
        "input/source-lock.json": canonical_json_bytes(bundle["source_lock"]),
        "data/learning-map.json": canonical_json_bytes(bundle["learning_map"]),
        "data/educator-map.json": canonical_json_bytes(bundle["educator_map"]),
        "data/native-id-index.json": canonical_json_bytes(bundle["native_id_index"]),
        "data/concept-index.json": canonical_json_bytes(bundle["concept_index"]),
        "data/relation-index.json": canonical_json_bytes(bundle["relation_index"]),
        "data/rights-and-terms.json": canonical_json_bytes(bundle["rights_and_terms"]),
        "data/ledger-references.json": canonical_json_bytes(bundle["ledger_references"]),
        "data/public-evidence.json": canonical_json_bytes(bundle["public_evidence"]),
        "data/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "data/claim-boundary.json": canonical_json_bytes(bundle["claim_boundary"]),
        "views/C60.html": render_learner(bundle).encode("utf-8"),
        "views/C60-pengajar.html": render_educator(bundle).encode("utf-8"),
        "fixtures/negative-fixtures.json": canonical_json_bytes({
            "schema": "c60-negative-fixture-index/1", "course_id": COURSE_ID, "fixtures": NEGATIVE_FIXTURES,
        }),
        "README.md": (
            "# C60 common capability adapter\n\n"
            "A deterministic, zero-copy `course-learning-capability/1` projection of the public R014 Indonesian number-theory and cryptology backend. "
            "It binds current public main `66df945d1e5281bfc4758b733c13ac9254f00410`, proves the native backend/source unchanged from release commit `11e27180632af3b90202ad38c063807c0d057766`, and independently replays the existing reversible migration receipt.\n\n"
            "The adapter preserves all 5,272 native IDs in a hash-only index, routes all 548 unit IDs and all 223 concepts to the public reflowable reader, and projects five chapter units containing the 101 native exercise identities. "
            "Every hint/check/solution support object is truthfully `not_present` with label `source_has_none`; no textbook bodies, invented exercises, solutions, assessments, learner results, live execution, accessibility conformance, or full offline dependency closure are claimed. "
            "Rights remain component-specific, and 239 terms plus 141 corrections remain source-locked.\n"
        ).encode("utf-8"),
    }
    for relative, data in files.items():
        target = adapter / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    outputs = [identity(adapter / path, display_path=path) for path in sorted(files)]
    manifest = {
        "schema": "c60-capability-manifest/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "contract": CONTRACT,
        "strict_contract_schema_verified": True,
        "locale": LOCALE,
        "native_family": "yaintt_r014_latex_backend_and_public_reflowable_reader",
        "native_release": RELEASE_VERSION,
        "content_policy": "stable_native_ids_selected_metadata_routes_and_evidence_only",
        "projection": {
            "zero_copy_native_bodies": True,
            "all_native_ids_preserved": True,
            "all_native_units_routed": True,
            "all_native_concepts_routed": True,
            "existing_reversible_migration_reused": True,
            "exercise_support_invented": False,
            "assessment_functionality_claimed": False,
            "live_execution_claimed": False,
            "accessibility_conformance_claimed": False,
            "full_offline_dependency_closure_claimed": False,
            "central_course_truth_rewritten": False,
            "historical_migration_receipt_rewritten": False,
            "common_virtual_backend_materialized": False,
            "excluded_destination_used": False,
            "public_state_changed": False,
        },
        "counts": bundle["capabilities"]["counts"],
        "inputs": bundle["source_lock"]["inputs"],
        "outputs": outputs,
        "validation_path": "validation.json",
    }
    write_json(adapter / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--hub-root", type=Path, default=PROJECT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    args = parser.parse_args()
    manifest = build(args.native_root.resolve(), args.hub_root.resolve(), args.adapter.resolve())
    print(json.dumps({"state": "pass", "course_id": COURSE_ID, "outputs": len(manifest["outputs"]), "native_ids": manifest["counts"]["native_records"]}, sort_keys=True))


if __name__ == "__main__":
    main()
