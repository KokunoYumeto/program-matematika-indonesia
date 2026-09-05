"""Build C70 learner and educator views from exact R012 native evidence."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from c70_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    CURRENT_PUBLIC_HEAD,
    LOCALE,
    MAINTENANCE_VERSION,
    NATIVE_ROLE_ID,
    PAGES_URL,
    PUBLIC_READBACK,
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
DEFAULT_NATIVE = WORKSPACE / "04_mirrors/id/applied-combinatorics-id"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/c70-capability-v1"

STYLE = """
:root{color-scheme:light;--ink:#1e2530;--muted:#5e6877;--paper:#f2f0e9;--card:#fff;--line:#d7d0c2;--accent:#6b3f16;--blue:#185c75;--ok:#2f6b42;--warn:#8a4b12}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}main{max-width:1220px;margin:auto;padding:28px 20px 70px}
nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.4rem}a{color:var(--blue);text-underline-offset:3px}h1{font-size:clamp(2rem,5vw,3.6rem);line-height:1.05;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.15rem;max-width:84ch}.muted{color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:1.5rem 0}.card,details,.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{display:block;font-size:1.8rem;font-weight:780}
details{margin:.75rem 0}summary{cursor:pointer;font-weight:740}.block-head{display:flex;justify-content:space-between;gap:1rem;align-items:baseline;flex-wrap:wrap}.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:.1rem .55rem;font-size:.85rem}.notice{border-left:6px solid var(--warn);background:#fff8ef;padding:1rem 1.2rem;border-radius:8px}.good{border-left-color:var(--ok);background:#f3fbf6}
.controls{display:flex;gap:.7rem;flex-wrap:wrap;align-items:end;margin:1rem 0}.controls label{display:grid;gap:.25rem;font-weight:650}.controls input[type=search]{min-width:min(32rem,82vw);padding:.7rem;border:1px solid #88919c;border-radius:7px;font:inherit}button{padding:.65rem .9rem;border:1px solid #57320f;border-radius:7px;background:var(--accent);color:#fff;font:inherit;font-weight:700;cursor:pointer}button.secondary{background:#fff;color:var(--accent)}
.select-row{display:grid;grid-template-columns:auto minmax(0,1fr) minmax(11rem,auto);gap:.8rem;align-items:start;border-bottom:1px solid var(--line);padding:.72rem 0}.select-row:last-child{border-bottom:0}.select-row input{width:1.2rem;height:1.2rem}.right{text-align:right}.hidden{display:none!important}code{overflow-wrap:anywhere}.small{font-size:.9rem}.counts{display:flex;gap:.4rem;flex-wrap:wrap}.counts span{background:#f3ede3;border-radius:4px;padding:.12rem .35rem}
a:focus-visible,summary:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #d58c2d;outline-offset:3px}@media(max-width:680px){.select-row{grid-template-columns:auto 1fr}.select-row .right{grid-column:2;text-align:left}}
""".strip()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>'
        '<nav><a href="../../id/#course-C70">Program matematika</a>'
        '<a href="../index.html">Pusat backend</a>'
        '<a href="C70.html">Pelajar</a>'
        '<a href="C70-pengajar.html">Pengajar</a></nav>'
        f'{body}</main></body></html>\n'
    )


def _block_search(block: dict) -> str:
    return " ".join([
        block["block_id"], block["title_id"], block.get("source_title") or "",
        block["kind"], block["source_path"], " ".join(block["concept_ids"]),
    ]).lower()


def _unit_search(unit: dict) -> str:
    return " ".join([
        unit["unit_id"], unit.get("title_id") or "", unit.get("source_title") or "",
        unit["kind"], unit["source_path"], " ".join(unit["concept_ids"]),
    ]).lower()


def render_learner(bundle: dict) -> str:
    learning = bundle["learning_map"]
    counts = bundle["capabilities"]["counts"]
    blocks = []
    for block in learning["blocks"]:
        kinds = "".join(
            f'<span>{esc(kind)} {amount}</span>'
            for kind, amount in block["unit_type_counts"].items()
            if kind in {"section", "subsection", "exercise", "example", "theorem", "definition", "solution"}
        )
        blocks.append(
            f'<details class="study-block" data-search="{esc(_block_search(block))}">'
            f'<summary><span class="block-head"><span>{block["ordinal"]}. {esc(block["title_id"])}</span>'
            f'<span class="pill">{block["unit_count"]} unit · {block["exercise_count"]} latihan</span></span></summary>'
            f'<p><code>{esc(block["block_id"])}</code> · {esc(block["kind"])} · {block["concept_count"]} konsep · '
            f'{block["explicit_support_count"]} relasi dukungan eksplisit.</p>'
            f'<p><a href="{esc(block["public_reader_url"])}">Baca bagian ini</a> · '
            f'<a href="{esc(REPOSITORY)}/blob/{CURRENT_PUBLIC_HEAD}/source/{esc(block["source_path"])}">Sumber PreTeXt Bahasa Indonesia</a></p>'
            f'<div class="counts small">{kinds}</div></details>'
        )
    body = f"""
<p class="muted">C70 · <code>{NATIVE_ROLE_ID}</code> · pembaca {RELEASE_VERSION} · pemeliharaan {MAINTENANCE_VERSION}</p>
<h1>Kombinatorika Terapan</h1>
<p class="lede">Jalur belajar menuju edisi Bahasa Indonesia lengkap <em>Applied Combinatorics</em>. Sembilan belas blok membuka pembaca HTML native secara langsung; peta ini mempertahankan semua 1.408 ID unit dan 701 konsep tanpa membuat salinan kedua dari buku.</p>
<div class="grid" aria-label="Ringkasan kursus">
<div class="card"><span class="metric">{counts['reader_pages']}</span>halaman PDF</div>
<div class="card"><span class="metric">{counts['learner_blocks']}</span>blok belajar</div>
<div class="card"><span class="metric">{counts['units']:,}</span>unit stabil</div>
<div class="card"><span class="metric">{counts['exercises']}</span>unit latihan</div>
<div class="card"><span class="metric">{counts['concepts']}</span>konsep</div>
<div class="card"><span class="metric">{counts['terms']}</span>keputusan istilah</div>
</div>
<p><a href="{esc(learning['public_reader'])}">Buka pembaca HTML lengkap</a> · <a href="{esc(learning['public_pdf'])}">Unduh PDF</a> · <a href="{esc(learning['portable_html_archive'])}">Unduh HTML luring</a> · <a href="{esc(learning['portable_source_archive'])}">Unduh sumber PreTeXt</a> · <a href="learning-map.json">Data jalur</a></p>
<div class="notice"><strong>Batas kebenaran:</strong> edisi native berstatus <code>draft</code>; rilisnya adalah draf Bahasa Indonesia lengkap yang diperiksa mesin, bukan edisi yang diklaim telah ditinjau manusia. Dari 407 unit latihan, peta hanya menampilkan 82 relasi dukungan yang dinyatakan native—57 solusi, 9 jawaban, dan 16 petunjuk.</div>
<div class="controls"><label>Cari bab, lampiran, konsep, atau ID<input id="block-filter" type="search" placeholder="contoh: teori graf, fungsi pembangkit, r012:concept"></label><span id="match-count" aria-live="polite">19 blok</span></div>
<h2>Rute belajar</h2>{''.join(blocks)}
<p class="notice good"><strong>Prasyarat:</strong> B10. Ini adalah jangkar tingkat kursus dari backend native, bukan prasyarat per unit yang dibuat oleh hub.</p>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in learning['limitations'])}</ul>
<script>
const filter=document.getElementById('block-filter');const blocks=[...document.querySelectorAll('.study-block')];const count=document.getElementById('match-count');
function applyFilter(){{const q=filter.value.trim().toLowerCase();let shown=0;for(const block of blocks){{const visible=!q||block.dataset.search.includes(q);block.classList.toggle('hidden',!visible);if(visible)shown++;}}count.textContent=shown+' blok';}}
filter.addEventListener('input',applyFilter);
</script>
"""
    return shell("C70 · Kombinatorika Terapan", body)


def render_educator(bundle: dict) -> str:
    educator = bundle["educator_map"]
    counts = educator["counts"]
    units = educator["selector"]["units"]
    support = educator["selector"]["exercise_support"]
    rows = []
    for unit in units:
        support_counts: dict[str, int] = {}
        for item in unit["exercise_support"]:
            support_counts[item["support_kind"]] = support_counts.get(item["support_kind"], 0) + 1
        support_label = " · ".join(f"{amount} {kind}" for kind, amount in sorted(support_counts.items())) or "tanpa pasangan eksplisit"
        title = unit.get("title_id") or unit.get("source_title") or unit["unit_id"]
        rows.append(
            f'<label class="select-row unit-row" data-search="{esc(_unit_search(unit))}">'
            f'<input class="unit-select" type="checkbox" value="{esc(unit["unit_id"])}" aria-label="Pilih {esc(title)}">'
            f'<span><strong>{esc(title)}</strong><br><code>{esc(unit["unit_id"])}</code><br><span class="small">{esc(unit["source_path"])}</span></span>'
            f'<span class="right">{esc(unit["kind"])} · {unit["segment_count"]} segmen<br>{len(unit["concept_ids"])} konsep · {esc(support_label)}</span></label>'
        )
    selection_data = json.dumps(
        {"units": units, "exercise_support": support},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    body = f"""
<p class="muted">C70 · tampilan pengajar · <code>{CONTRACT}</code></p>
<h1>Pemilih unit native</h1>
<p class="lede">Cari dan pilih dari seluruh 1.408 unit native. Ekspor JSON mempertahankan hierarki, hash fragmen, konsep, dan tepat 82 relasi petunjuk/jawaban/solusi yang dinyatakan—tanpa menyalin isi buku atau menebak pasangan yang tidak tercatat.</p>
<div class="grid" aria-label="Ringkasan bukti">
<div class="card"><span class="metric">{counts['units']:,}</span>unit terindeks</div>
<div class="card"><span class="metric">{counts['exercises']}</span>latihan</div>
<div class="card"><span class="metric">{counts['explicit_solves_relations']}</span>relasi solusi</div>
<div class="card"><span class="metric">{counts['explicit_answers_relations']}</span>relasi jawaban</div>
<div class="card"><span class="metric">{counts['explicit_hints_relations']}</span>relasi petunjuk</div>
<div class="card"><span class="metric">{counts['corrections']}</span>koreksi terlacak</div>
</div>
<div class="notice"><strong>Jangan isi celah secara rekaan:</strong> backend memiliki 84 unit solusi, tetapi hanya 57 relasi <code>solves</code> eksplisit. Dua puluh tujuh unit solusi yang tersisa tetap tidak dipasangkan oleh adapter.</div>
<div class="controls"><label>Saring unit<input id="teacher-filter" type="search" placeholder="judul, ID, jenis, berkas, atau konsep"></label><button id="select-visible" type="button">Pilih yang terlihat</button><button id="clear" class="secondary" type="button">Kosongkan</button><button id="export" type="button">Ekspor JSON</button><span id="selected-count" aria-live="polite">0 dipilih</span></div>
<div class="panel" id="unit-list">{''.join(rows)}</div>
<h2>Bukti dan data</h2><p><a href="educator-map.json">Peta pengajar</a> · <a href="concept-index.json">Indeks konsep</a> · <a href="relation-index.json">Seluruh 6.334 relasi</a> · <a href="rights-and-terms.json">Istilah, koreksi, dan hak</a> · <a href="ledger-references.json">Ledger dan migrasi</a> · <a href="C70.html">Jalur pelajar</a></p>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in educator['limitations'])}</ul>
<script id="selection-data" type="application/json">{selection_data}</script>
<script>
const data=JSON.parse(document.getElementById('selection-data').textContent);const unitById=new Map(data.units.map(x=>[x.unit_id,x]));const supportByExercise=new Map();for(const row of data.exercise_support){{const list=supportByExercise.get(row.exercise_unit_id)||[];list.push(row);supportByExercise.set(row.exercise_unit_id,list);}}
const rows=[...document.querySelectorAll('.unit-row')];const boxes=[...document.querySelectorAll('.unit-select')];const filter=document.getElementById('teacher-filter');const count=document.getElementById('selected-count');
function updateCount(){{count.textContent=boxes.filter(x=>x.checked).length+' dipilih';}}function applyFilter(){{const q=filter.value.trim().toLowerCase();for(const row of rows)row.classList.toggle('hidden',!!q&&!row.dataset.search.includes(q));}}
filter.addEventListener('input',applyFilter);for(const box of boxes)box.addEventListener('change',updateCount);document.getElementById('select-visible').addEventListener('click',()=>{{for(const row of rows)if(!row.classList.contains('hidden'))row.querySelector('input').checked=true;updateCount();}});document.getElementById('clear').addEventListener('click',()=>{{for(const box of boxes)box.checked=false;updateCount();}});
document.getElementById('export').addEventListener('click',()=>{{const selectedUnits=boxes.filter(x=>x.checked).map(x=>unitById.get(x.value));const selectedIds=new Set(selectedUnits.map(x=>x.unit_id));const selectedSupport=data.exercise_support.filter(x=>selectedIds.has(x.exercise_unit_id)||selectedIds.has(x.support_unit_id));const payload={{schema:'c70-educator-selection/1',course_id:'C70',locale:'id-ID',program_prerequisites:['B10'],prerequisite_scope:'native_course_level_external_anchor',native_bodies_copied:false,unlinked_solution_units_inferred:false,selected_units:selectedUnits,explicit_support_relations:selectedSupport}};const blob=new Blob([JSON.stringify(payload,null,2)+'\\n'],{{type:'application/json'}});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='C70-rencana-pengajar.json';a.click();URL.revokeObjectURL(url);}});
</script>
"""
    return shell("C70 · Pemilih pengajar", body)


def build(native_root: Path, hub_root: Path, adapter: Path) -> dict:
    bundle = derive_projection(native_root, hub_root)
    errors = projection_errors(bundle)
    if errors:
        raise ValueError(f"C70 projection failed: {errors}")
    files = {
        "input/public-native-readback.json": (hub_root / PUBLIC_READBACK).read_bytes(),
        "input/source-lock.json": canonical_json_bytes(bundle["source_lock"]),
        "data/learning-map.json": canonical_json_bytes(bundle["learning_map"]),
        "data/educator-map.json": canonical_json_bytes(bundle["educator_map"]),
        "data/concept-index.json": canonical_json_bytes(bundle["concept_index"]),
        "data/relation-index.json": canonical_json_bytes(bundle["relation_index"]),
        "data/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "data/ledger-references.json": canonical_json_bytes(bundle["ledger_references"]),
        "data/public-evidence.json": canonical_json_bytes(bundle["public_evidence"]),
        "data/rights-and-terms.json": canonical_json_bytes(bundle["rights_and_terms"]),
        "data/claim-boundary.json": canonical_json_bytes(bundle["claim_boundary"]),
        "views/C70.html": render_learner(bundle).encode("utf-8"),
        "views/C70-pengajar.html": render_educator(bundle).encode("utf-8"),
        "fixtures/negative-fixtures.json": canonical_json_bytes({
            "schema": "c70-negative-fixture-index/1",
            "course_id": COURSE_ID,
            "fixtures": [
                "duplicate_unit", "missing_unit", "unit_order_change", "block_loss",
                "chapter_appendix_collapse", "prerequisite_change", "support_loss",
                "support_type_collapse", "relation_loss", "relation_count_change",
                "projection_double_count", "concept_loss", "terminology_loss",
                "terminology_review_loss", "correction_loss", "target_state_promotion",
                "backend_roundtrip_downgrade", "nonanonymous_github", "closed_zenodo",
                "reader_route_loss", "accessibility_overclaim", "blanket_license_claim",
                "native_body_copy", "unit_outcome_invention", "unit_prerequisite_invention",
                "unlinked_solution_inference", "source_defect_retyping",
                "virtual_backend_materialization", "figshare_reactivation",
                "historical_receipt_rewrite", "public_state_change", "input_hash_change",
            ],
        }),
        "README.md": (
            "# C70 common capability adapter\n\n"
            "Zero-copy learner and educator projection of the complete public R012 Applied Combinatorics backend into `course-learning-capability/1`. "
            "It reuses the exact reversible 19,048-to-19,049-record migration, preserves all 1,408 unit identities, 3,806 segment mappings, 701 concepts, 6,334 relations, 633 terminology entries, 354 corrections, and the public GitHub/Zenodo/HTML evidence.\n\n"
            "The learner view exposes 16 chapters and three appendices. The educator view selects any native unit and exports only explicit support relations. "
            "The 82-row exercise-support file is verified as a projection of the canonical relation table and is never counted twice. The native target edition remains a complete machine-checked draft; no human review, tagged-PDF, MathML, invented unit outcomes, invented unit prerequisites, inferred solution links, copied book bodies, active Figshare use, or materialized duplicate backend is claimed.\n"
        ).encode("utf-8"),
    }
    for relative, data in files.items():
        target = adapter / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    outputs = [identity(adapter / path, display_path=path) for path in sorted(files)]
    source_lock = bundle["source_lock"]
    manifest = {
        "schema": "c70-capability-manifest/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "contract": CONTRACT,
        "contract_2_3_1_conformance": "not_claimed",
        "locale": LOCALE,
        "native_family": "applied_combinatorics_pretext_backend",
        "native_release": RELEASE_VERSION,
        "maintenance_release": MAINTENANCE_VERSION,
        "content_policy": "stable_native_ids_selected_metadata_and_evidence_only",
        "projection": {
            "zero_copy_native_bodies": True,
            "native_ids_preserved": True,
            "existing_reversible_migration_reused": True,
            "all_unit_ids_indexed": True,
            "all_relation_ids_indexed": True,
            "exercise_support_projection_double_counted": False,
            "unlinked_solution_units_inferred": False,
            "native_target_edition_promoted": False,
            "central_course_truth_rewritten": False,
            "historical_migration_receipt_rewritten": False,
            "common_virtual_backend_materialized": False,
            "figshare_active_destination_used": False,
            "public_state_changed": False,
        },
        "counts": bundle["capabilities"]["counts"],
        "inputs": [source_lock["export_manifest_input"], *source_lock["export_inputs"], *source_lock["control_inputs"], source_lock["migration_input"], source_lock["public_readback_input"]],
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
    print(canonical_json_bytes({
        "state": "pass", "course_id": COURSE_ID, "outputs": len(manifest["outputs"]),
        "units": manifest["counts"]["units"], "relations": manifest["counts"]["relations"],
        "concepts": manifest["counts"]["concepts"], "support_relations": manifest["counts"]["explicit_support_relations"],
    }).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
