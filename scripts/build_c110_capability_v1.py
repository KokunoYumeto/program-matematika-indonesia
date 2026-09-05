"""Build the C110 learner and educator surfaces from exact native evidence."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from c110_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    LOCALE,
    NATIVE_ROLE_ID,
    NATIVE_VERSION,
    PUBLIC_READBACK,
    canonical_json_bytes,
    derive_projection,
    identity,
    projection_errors,
    write_json,
)


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
DEFAULT_NATIVE = WORKSPACE / "04_mirrors/id/tea-time-numerical-analysis-id"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/c110-capability-v1"

STYLE = """
:root{color-scheme:light;--ink:#122b39;--muted:#536b77;--paper:#eef3f5;--card:#fff;--line:#c7d6dc;--accent:#075c75;--warm:#9b541c;--ok:#246648;--support:#684596}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}main{max-width:1180px;margin:auto;padding:28px 20px 64px}
nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.4rem}a{color:var(--accent);text-underline-offset:3px}h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.05;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.14rem;max-width:84ch}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:1.5rem 0}.card,details,.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{font-size:1.8rem;font-weight:760;display:block}.muted{color:var(--muted)}details{margin:.72rem 0}summary{cursor:pointer;font-weight:720}.head{display:flex;justify-content:space-between;gap:1rem;align-items:baseline;flex-wrap:wrap}.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:.1rem .55rem;font-size:.84rem}.pill.support{border-color:var(--support);color:var(--support)}
.notice{border-left:6px solid var(--warm);background:#fff8ef;padding:1rem 1.2rem;border-radius:8px}.good{border-left-color:var(--ok);background:#f3fbf6}.controls{display:flex;gap:.7rem;flex-wrap:wrap;align-items:end;margin:1rem 0}.controls label{display:grid;gap:.25rem;font-weight:650}.controls input[type=search]{min-width:min(30rem,82vw);padding:.7rem;border:1px solid #8197a0;border-radius:7px;font:inherit}button{padding:.65rem .9rem;border:1px solid #064b60;border-radius:7px;background:var(--accent);color:white;font:inherit;font-weight:700;cursor:pointer}button.secondary{background:white;color:var(--accent)}
.select-row{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:.8rem;align-items:start;border-bottom:1px solid var(--line);padding:.72rem 0}.select-row:last-child{border-bottom:0}.select-row input{width:1.2rem;height:1.2rem}.right{text-align:right}.hidden{display:none!important}code{overflow-wrap:anywhere}.small{font-size:.9rem}.tree{margin:.7rem 0 0;padding-left:1.3rem}.tree li{margin:.25rem 0}a:focus-visible,summary:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #d58522;outline-offset:3px}@media(max-width:650px){.select-row{grid-template-columns:auto 1fr}.select-row .right{grid-column:2;text-align:left}}
""".strip()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, body: str) -> str:
    return (
        "<!doctype html><html lang=\"id\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>"
        "<nav><a href=\"../../id/#course-C110\">Program matematika</a>"
        "<a href=\"../index.html\">Pusat backend</a>"
        "<a href=\"C110.html\">Pelajar</a>"
        "<a href=\"C110-pengajar.html\">Pengajar</a></nav>"
        f"{body}</main></body></html>\n"
    )


def render_learner(bundle: dict) -> str:
    learning = bundle["learning_map"]
    counts = bundle["capabilities"]["counts"]
    blocks = []
    for module in learning["modules"]:
        pill_class = "pill support" if module["role"] in {"solutions", "answers"} else "pill"
        role = {"solutions": "modul solusi", "answers": "modul jawaban", "preface": "prakata", "teaching": "materi"}[module["role"]]
        search = " ".join(filter(None, [module["module_id"], module["title_id"], module["source_title"], module["source_path"]])).lower()
        blocks.append(
            f"<details class=\"module\" data-search=\"{esc(search)}\"><summary><span class=\"head\">"
            f"<span>{module['ordinal']}. {esc(module['title_id'])}</span><span class=\"{pill_class}\">{role} · {module['unit_count']} unit</span>"
            f"</span></summary><p><code>{esc(module['module_id'])}</code></p>"
            f"<p>{module['segment_count']:,} segmen/alignment · sumber: <em>{esc(module['source_title'] or module['source_path'])}</em>.</p>"
            f"<p><a href=\"{esc(module['public_target_source'])}\">Buka sumber target tepat</a> · "
            f"<a href=\"learning-map.json\">Lihat hierarki unit lengkap</a></p></details>"
        )
    body = f"""
<p class="muted">C110 · <code>{NATIVE_ROLE_ID}</code> · {esc(NATIVE_VERSION)}</p>
<h1>Analisis Numerik</h1>
<p class="lede">Navigator zero-copy untuk edisi lengkap <em>Analisis Numerik Saat Minum Teh</em>. Dua puluh sembilan modul dan seluruh 281 unit native tetap memakai identitas aslinya; teks buku berada pada PDF dan sumber publik yang hash-nya telah dibaca balik secara anonim.</p>
<div class="grid" aria-label="Ringkasan kursus">
<div class="card"><span class="metric">{counts['pdf_pages']}</span>halaman PDF</div>
<div class="card"><span class="metric">{counts['file_modules']}</span>modul berkas</div>
<div class="card"><span class="metric">{counts['units']}</span>unit native</div>
<div class="card"><span class="metric">{counts['alignments']:,}</span>alignment terjemahan</div>
<div class="card"><span class="metric">{counts['terms']}</span>keputusan istilah</div>
<div class="card"><span class="metric">{counts['experiments']}</span>eksperimen/tantangan</div>
</div>
<p><a href="{esc(learning['public_pdf'])}">Unduh PDF lengkap</a> · <a href="{esc(learning['portable_source_archive'])}">Unduh sumber + backend</a> · <a href="{esc(learning['public_backend'])}">Buka backend native</a> · <a href="learning-map.json">Data navigasi</a></p>
<div class="notice"><strong>Batas kebenaran:</strong> sumber menyediakan modul solusi dan jawaban, tetapi bukan entitas latihan atau pasangan latihan-solusi yang dapat dibuktikan. Navigator tidak menciptakan pasangan tersebut. Repo native juga belum menyediakan pembaca HTML semantik penuh; halaman ini menavigasi metadata, PDF, dan sumber.</div>
<div class="controls"><label>Cari modul<input id="module-filter" type="search" placeholder="contoh: Newton, splin, solusi"></label><span id="match-count" aria-live="polite">29 modul</span></div>
<h2>Urutan belajar</h2>{''.join(blocks)}
<p class="notice good"><strong>Prasyarat program:</strong> B30, B40, B80, dan C10. Ini relasi tingkat kursus dari kurikulum pusat, bukan klaim prasyarat per unit native.</p>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in learning['limitations'])}</ul>
<script>
const filter=document.getElementById('module-filter');const modules=[...document.querySelectorAll('.module')];const count=document.getElementById('match-count');
function applyFilter(){{const q=filter.value.trim().toLowerCase();let shown=0;for(const item of modules){{const visible=!q||item.dataset.search.includes(q);item.classList.toggle('hidden',!visible);if(visible)shown++;}}count.textContent=shown+' modul';}}
filter.addEventListener('input',applyFilter);
</script>
"""
    return shell("C110 · Analisis Numerik", body)


def render_educator(bundle: dict) -> str:
    educator = bundle["educator_map"]
    counts = educator["counts"]
    modules = educator["selector"]["modules"]
    units = educator["selector"]["units"]
    experiments = educator["selector"]["experiments"]
    module_rows = []
    for module in modules:
        search = " ".join(filter(None, [module["module_id"], module["title_id"], module["source_title"], module["role"]])).lower()
        module_rows.append(
            f"<label class=\"select-row selectable\" data-search=\"{esc(search)}\"><input class=\"module-select\" type=\"checkbox\" value=\"{esc(module['module_id'])}\">"
            f"<span><strong>{module['ordinal']}. {esc(module['title_id'])}</strong><br><code>{esc(module['module_id'])}</code> · {esc(module['role'])}</span>"
            f"<span class=\"right\">{module['unit_count']} unit<br>{module['segment_count']:,} segmen</span></label>"
        )
    unit_rows = []
    for unit in units:
        title = (unit.get("localized_title") or {}).get("target") or unit.get("source_title") or unit["kind"]
        search = " ".join(filter(None, [unit["unit_id"], title, unit.get("source_title"), unit["kind"]])).lower()
        unit_rows.append(
            f"<label class=\"select-row selectable unit-row\" data-search=\"{esc(search)}\"><input class=\"unit-select\" type=\"checkbox\" value=\"{esc(unit['unit_id'])}\">"
            f"<span><strong>{esc(title)}</strong><br><code>{esc(unit['unit_id'])}</code> · {esc(unit['kind'])}</span>"
            f"<span class=\"right\">{unit['segment_count']} segmen<br>{len(unit['child_unit_ids'])} anak</span></label>"
        )
    experiment_rows = []
    for experiment in experiments:
        search = f"{experiment['experiment_id']} {experiment['experiment_key']} {experiment['kind']}".lower()
        experiment_rows.append(
            f"<label class=\"select-row selectable\" data-search=\"{esc(search)}\"><input class=\"experiment-select\" type=\"checkbox\" value=\"{esc(experiment['experiment_id'])}\">"
            f"<span><strong>{esc(experiment['experiment_key'])}</strong><br><code>{esc(experiment['experiment_id'])}</code></span>"
            f"<span class=\"right\">{esc(experiment['kind'])}</span></label>"
        )
    compact = {
        "modules": modules,
        "units": units,
        "experiments": experiments,
    }
    data = json.dumps(compact, ensure_ascii=False, sort_keys=True, separators=(",", ":")).replace("</", "<\\/")
    body = f"""
<p class="muted">C110 · tampilan pengajar · <code>{CONTRACT}</code></p>
<h1>Pemilih modul, unit, dan eksperimen</h1>
<p class="lede">Susun rencana ajar dari 29 modul, 281 unit struktural, dan dua eksperimen native. Ekspor mempertahankan ID, parent, hash sumber/target, dan batas bukti tanpa menyalin badan buku.</p>
<div class="grid" aria-label="Ringkasan bukti"><div class="card"><span class="metric">29</span>modul</div><div class="card"><span class="metric">281</span>unit</div><div class="card"><span class="metric">4.621</span>alignment</div><div class="card"><span class="metric">2</span>eksperimen</div><div class="card"><span class="metric">593</span>istilah</div><div class="card"><span class="metric">325</span>koreksi</div></div>
<div class="notice"><strong>Batas solusi:</strong> pilih modul <em>Solusi untuk Latihan Terpilih</em> dan <em>Jawaban untuk Latihan Terpilih</em> secara eksplisit bila diperlukan. Backend tidak membuktikan pasangan per-latihan, sehingga ekspor tidak menciptakannya.</div>
<div class="controls"><label>Saring semua pilihan<input id="teacher-filter" type="search" placeholder="judul, ID, jenis unit"></label><button id="select-visible" type="button">Pilih yang terlihat</button><button id="clear" class="secondary" type="button">Kosongkan</button><button id="export" type="button">Ekspor JSON</button><span id="selected-count" aria-live="polite">0 dipilih</span></div>
<h2>Modul</h2><div class="panel">{''.join(module_rows)}</div>
<details><summary>Unit struktural lengkap (281)</summary><div class="panel">{''.join(unit_rows)}</div></details>
<h2>Eksperimen dan tantangan</h2><div class="panel">{''.join(experiment_rows)}</div>
<h2>Bukti dan ledger</h2><p><a href="educator-map.json">Peta pengajar</a> · <a href="translation-alignments.json">Indeks alignment</a> · <a href="rights-and-terms.json">Hak, istilah, dan koreksi</a> · <a href="ledger-references.json">Ledger dan migrasi</a> · <a href="C110.html">Jalur pelajar</a></p>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in educator['limitations'])}</ul>
<script id="selection-data" type="application/json">{data}</script>
<script>
const data=JSON.parse(document.getElementById('selection-data').textContent);const moduleById=new Map(data.modules.map(x=>[x.module_id,x]));const unitById=new Map(data.units.map(x=>[x.unit_id,x]));const experimentById=new Map(data.experiments.map(x=>[x.experiment_id,x]));const rows=[...document.querySelectorAll('.selectable')];const boxes=[...document.querySelectorAll('.selectable input')];const filter=document.getElementById('teacher-filter');const count=document.getElementById('selected-count');
function updateCount(){{count.textContent=boxes.filter(x=>x.checked).length+' dipilih';}}function applyFilter(){{const q=filter.value.trim().toLowerCase();for(const row of rows)row.classList.toggle('hidden',!!q&&!row.dataset.search.includes(q));}}
filter.addEventListener('input',applyFilter);for(const box of boxes)box.addEventListener('change',updateCount);document.getElementById('select-visible').addEventListener('click',()=>{{for(const row of rows)if(!row.classList.contains('hidden'))row.querySelector('input').checked=true;updateCount();}});document.getElementById('clear').addEventListener('click',()=>{{for(const box of boxes)box.checked=false;updateCount();}});
document.getElementById('export').addEventListener('click',()=>{{const selectedModules=[...document.querySelectorAll('.module-select:checked')].map(x=>moduleById.get(x.value));const selectedUnits=[...document.querySelectorAll('.unit-select:checked')].map(x=>unitById.get(x.value));const selectedExperiments=[...document.querySelectorAll('.experiment-select:checked')].map(x=>experimentById.get(x.value));const payload={{schema:'c110-educator-selection/1',course_id:'C110',locale:'id-ID',program_prerequisites:['B30','B40','B80','C10'],prerequisite_scope:'central_course_level_only',native_bodies_copied:false,exercise_solution_joins_inferred:false,selected_modules:selectedModules,selected_units:selectedUnits,selected_experiments:selectedExperiments}};const blob=new Blob([JSON.stringify(payload,null,2)+'\\n'],{{type:'application/json'}});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='C110-rencana-pengajar.json';a.click();URL.revokeObjectURL(url);}});
</script>
"""
    return shell("C110 · Pemilih pengajar", body)


def build(native_root: Path, hub_root: Path, adapter: Path) -> dict:
    bundle = derive_projection(native_root, hub_root)
    errors = projection_errors(bundle)
    if errors:
        raise ValueError(f"C110 projection failed: {errors}")
    files = {
        "input/public-native-readback.json": (hub_root / PUBLIC_READBACK).read_bytes(),
        "input/source-lock.json": canonical_json_bytes(bundle["source_lock"]),
        "data/learning-map.json": canonical_json_bytes(bundle["learning_map"]),
        "data/educator-map.json": canonical_json_bytes(bundle["educator_map"]),
        "data/translation-alignments.json": canonical_json_bytes(bundle["translation_alignments"]),
        "data/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "data/ledger-references.json": canonical_json_bytes(bundle["ledger_references"]),
        "data/public-evidence.json": canonical_json_bytes(bundle["public_evidence"]),
        "data/rights-and-terms.json": canonical_json_bytes(bundle["rights_and_terms"]),
        "data/claim-boundary.json": canonical_json_bytes(bundle["claim_boundary"]),
        "views/C110.html": render_learner(bundle).encode("utf-8"),
        "views/C110-pengajar.html": render_educator(bundle).encode("utf-8"),
        "fixtures/negative-fixtures.json": canonical_json_bytes({
            "schema": "c110-negative-fixture-index/1",
            "course_id": COURSE_ID,
            "fixtures": [
                "duplicate_module", "missing_module", "module_order_change", "unit_loss", "unit_parent_change",
                "alignment_loss", "alignment_unit_break", "term_loss", "correction_loss", "experiment_loss",
                "solution_answer_collapse", "exercise_solution_join_invention", "native_outcome_invention",
                "native_prerequisite_invention", "semantic_html_invention", "tagged_pdf_invention",
                "segment_state_promotion", "backend_hash_downgrade", "github_identity_change",
                "zenodo_access_downgrade", "blanket_license_claim", "native_body_copy",
                "virtual_backend_materialization", "historical_receipt_rewrite", "public_state_change",
                "input_hash_change",
            ],
        }),
        "README.md": (
            "# C110 common capability adapter\n\n"
            "Zero-copy learner and educator projection of the complete public R015 numerical-analysis backend into `course-learning-capability/1`. "
            "It preserves 29 file modules, all 281 native units, 4,621 source/localization alignments, 593 terminology records, 325 correction records, two experiment identities, 31 source/target file identities, component rights, deterministic migration evidence, and exact anonymous GitHub/Zenodo readback.\n\n"
            "The learner surface navigates modules and exact public artifacts. The educator surface exports selected module, unit, and experiment identities. "
            "The native solutions and answers files remain separate selectable modules; because the native backend has no exercise entity, the adapter does not invent per-exercise joins. "
            "No book body, virtual 53,055-record common stream, native HTML reader, tagged-PDF claim, or segment-level release-state promotion is created.\n"
        ).encode("utf-8"),
    }
    for relative, data in files.items():
        target = adapter / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    outputs = [identity(adapter / path, display_path=path) for path in sorted(files)]
    manifest = {
        "schema": "c110-capability-manifest/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "contract": CONTRACT,
        "contract_2_3_1_conformance": "not_claimed",
        "locale": LOCALE,
        "native_family": "numerical_analysis_lyx_backend",
        "native_release": NATIVE_VERSION,
        "content_policy": "stable_native_ids_selected_metadata_and_evidence_only",
        "projection": {
            "zero_copy_native_bodies": True,
            "native_ids_preserved": True,
            "all_alignment_ids_preserved": True,
            "solution_and_answer_modules_distinct": True,
            "exercise_solution_joins_inferred": False,
            "existing_reversible_migration_reused": True,
            "historical_migration_receipt_rewritten": False,
            "common_virtual_backend_materialized": False,
            "central_course_truth_rewritten": False,
            "public_state_changed": False,
        },
        "counts": bundle["capabilities"]["counts"],
        "inputs": bundle["source_lock"]["native_inputs"] + [bundle["source_lock"]["migration_input"], bundle["source_lock"]["public_readback_input"]],
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
    print(canonical_json_bytes(manifest).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
