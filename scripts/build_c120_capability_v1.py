"""Build the C120 learner and educator views from exact native evidence."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from c120_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    LOCALE,
    NATIVE_ROLE_ID,
    NATIVE_VERSION,
    canonical_json_bytes,
    derive_projection,
    identity,
    projection_errors,
    write_json,
)


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
DEFAULT_NATIVE = WORKSPACE / "04_mirrors/id/mathematical-modeling-nonlinear-dynamics-id"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/c120-capability-v1"

STYLE = """
:root{color-scheme:light;--ink:#142c34;--muted:#536a72;--paper:#eef3ed;--card:#fff;--line:#c9d8d2;--accent:#126b5b;--warm:#a95720;--bridge:#5e3c92;--ok:#286848}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1180px;margin:auto;padding:28px 20px 64px}nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.4rem}a{color:var(--accent);text-underline-offset:3px}
h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.05;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.15rem;max-width:82ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:12px;margin:1.5rem 0}.card,details,.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{font-size:1.8rem;font-weight:760;display:block}.muted{color:var(--muted)}details{margin:.75rem 0}summary{cursor:pointer;font-weight:720}.unit-head{display:flex;justify-content:space-between;gap:1rem;align-items:baseline;flex-wrap:wrap}.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:.1rem .55rem;font-size:.85rem}.pill.bridge{border-color:var(--bridge);color:var(--bridge)}.notice{border-left:6px solid var(--warm);background:#fff8ef;padding:1rem 1.2rem;border-radius:8px}.good{border-left-color:var(--ok);background:#f3fbf6}.controls{display:flex;gap:.7rem;flex-wrap:wrap;align-items:end;margin:1rem 0}.controls label{display:grid;gap:.25rem;font-weight:650}.controls input[type=search]{min-width:min(28rem,82vw);padding:.7rem;border:1px solid #81979f;border-radius:7px;font:inherit}button{padding:.65rem .9rem;border:1px solid #0d574a;border-radius:7px;background:#126b5b;color:white;font:inherit;font-weight:700;cursor:pointer}button.secondary{background:white;color:#126b5b}.select-row{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:.8rem;align-items:start;border-bottom:1px solid var(--line);padding:.8rem 0}.select-row:last-child{border-bottom:0}.select-row input{width:1.2rem;height:1.2rem}.right{text-align:right}.hidden{display:none!important}code{overflow-wrap:anywhere}.small{font-size:.9rem}.ids{display:flex;gap:.4rem;flex-wrap:wrap;padding:0;list-style:none}.ids code{background:#edf5f2;padding:.12rem .35rem;border-radius:4px}a:focus-visible,summary:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #d58522;outline-offset:3px}@media(max-width:650px){.select-row{grid-template-columns:auto 1fr}.select-row .right{grid-column:2;text-align:left}}
""".strip()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, body: str) -> str:
    return (
        "<!doctype html><html lang=\"id\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>"
        "<nav><a href=\"../../id/#course-C120\">Program matematika</a>"
        "<a href=\"../index.html\">Pusat backend</a>"
        "<a href=\"C120.html\">Pelajar</a>"
        "<a href=\"C120-pengajar.html\">Pengajar</a></nav>"
        f"{body}</main></body></html>\n"
    )


def _search_text(unit: dict) -> str:
    return " ".join([
        unit["unit_id"], unit["label"], unit["title_id"], unit.get("source_title") or "",
        unit["unit_kind"], " ".join(unit["problem_ids"]),
    ]).lower()


def _support_label(unit: dict) -> str:
    counts: dict[str, int] = {}
    for row in unit["problem_support"]:
        counts[row["support_type"]] = counts.get(row["support_type"], 0) + 1
    labels = []
    for key, label in (("worked_solution", "solusi"), ("qualitative_rubric", "rubrik"), ("worked_classification", "klasifikasi")):
        if counts.get(key):
            labels.append(f"{counts[key]} {label}")
    return " · ".join(labels) if labels else "tanpa rekaman penguasaan"


def render_learner(bundle: dict) -> str:
    learning = bundle["learning_map"]
    counts = bundle["capabilities"]["counts"]
    source_blocks: list[str] = []
    bridge_blocks: list[str] = []
    for unit in learning["units"]:
        ids = "".join(f"<li><code>{esc(item)}</code></li>" for item in unit["problem_ids"])
        notebook = (
            f"<p><a href=\"https://github.com/KokunoYumeto/mathematical-modeling-nonlinear-dynamics-id/blob/"
            f"1a5958db5d04eef5fba23af69913b6b1272939a9/{esc(unit['unit_notebook_path'])}\">Notebook unit</a></p>"
            if unit["unit_notebook_path"] else ""
        )
        origin = "Jembatan orisinal" if unit["origin_kind"] == "independent_supplement" else "Terjemahan sumber"
        pill_class = "pill bridge" if unit["origin_kind"] == "independent_supplement" else "pill"
        block = (
            f"<details class=\"unit\" data-search=\"{esc(_search_text(unit))}\">"
            f"<summary><span class=\"unit-head\"><span>{unit['ordinal']}. {esc(unit['title_id'])}</span>"
            f"<span class=\"{pill_class}\">{esc(origin)} · {unit['problem_count']} masalah</span></span></summary>"
            f"<p><code>{esc(unit['unit_id'])}</code> · {esc(unit['label'])} · PDF hlm. {unit['pdf_page_start']}–{unit['pdf_page_end']}</p>"
            f"<p>{unit['segment_count']:,} segmen stabil · {_support_label(unit)}.</p>"
            f"<p><a href=\"{esc(unit['reader_url'])}\">Buka pembaca unit</a> · "
            f"<a href=\"{esc(unit['public_target_source'])}\">Sumber target tepat</a> · "
            f"<a href=\"{esc(unit['public_unit_record'])}\">Rekaman unit</a></p>{notebook}"
            f"<h3>Identitas masalah penguasaan</h3><ul class=\"ids\">{ids or '<li>Tidak ada rekaman penguasaan untuk unit ini.</li>'}</ul>"
            "</details>"
        )
        (bridge_blocks if unit["origin_kind"] == "independent_supplement" else source_blocks).append(block)

    body = f"""
<p class="muted">C120 · <code>{NATIVE_ROLE_ID}</code> · {esc(NATIVE_VERSION)}</p>
<h1>Pemodelan Matematis dan Dinamika Nonlinear</h1>
<p class="lede">Jalur zero-copy menuju edisi lengkap <em>Pengantar Pemodelan Matematika</em>. Cari unit, judul, atau ID masalah; isi, notebook, dan paket proyek tetap pada edisi native publik yang hash-nya dikunci.</p>
<div class="grid" aria-label="Ringkasan kursus">
<div class="card"><span class="metric">{counts['reader_pages']}</span>halaman PDF bertag</div>
<div class="card"><span class="metric">{counts['units']}</span>unit pembaca</div>
<div class="card"><span class="metric">{counts['mastery_problems']}</span>masalah penguasaan</div>
<div class="card"><span class="metric">{counts['total_notebooks']}</span>notebook terbuka</div>
<div class="card"><span class="metric">{counts['projects']}</span>paket proyek</div>
<div class="card"><span class="metric">{counts['terminology_rows']}</span>keputusan istilah</div>
</div>
<p><a href="{esc(learning['public_reader'])}">Buka pembaca HTML lengkap</a> · <a href="{esc(learning['public_pdf'])}">Unduh PDF lengkap</a> · <a href="{esc(learning['portable_source_archive'])}">Unduh paket sumber dan pembaca</a> · <a href="learning-map.json">Data navigasi terbuka</a></p>
<div class="notice"><strong>Batas kebenaran:</strong> empat modul jembatan adalah tambahan orisinal dan tidak diklaim sebagai bagian karya sumber. Dukungan 141 masalah terdiri dari 126 solusi tertulis, 14 rubrik kualitatif, dan satu klasifikasi terbimbing. Dua belas notebook proyek adalah paket awal, bukan klaim reproduksi hasil artikel.</div>
<div class="controls"><label>Cari unit atau masalah<input id="unit-filter" type="search" placeholder="contoh: bifurkasi, epidemiologi, O005-BRIDGE-C3-P04"></label><span id="match-count" aria-live="polite">26 unit</span></div>
<h2>Terjemahan sumber</h2>{''.join(source_blocks)}
<h2>Modul jembatan orisinal</h2>{''.join(bridge_blocks)}
<p class="notice good"><strong>Prasyarat program:</strong> B70, B80, dan C10. Ini adalah relasi tingkat kursus dari kurikulum pusat, bukan klaim prasyarat per unit native.</p>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in learning['limitations'])}</ul>
<script>
const filter=document.getElementById('unit-filter');const units=[...document.querySelectorAll('.unit')];const count=document.getElementById('match-count');
function applyFilter(){{const q=filter.value.trim().toLowerCase();let shown=0;for(const unit of units){{const visible=!q||unit.dataset.search.includes(q);unit.classList.toggle('hidden',!visible);if(visible)shown++;}}count.textContent=shown+' unit';}}
filter.addEventListener('input',applyFilter);
</script>
"""
    return shell("C120 · Pemodelan dan Dinamika", body)


def render_educator(bundle: dict) -> str:
    educator = bundle["educator_map"]
    counts = educator["counts"]
    units = educator["selector"]["selected_units"]
    projects = educator["selector"]["projects"]
    unit_rows = []
    for unit in units:
        unit_rows.append(
            f"<label class=\"select-row unit-row\" data-search=\"{esc(_search_text(unit))}\">"
            f"<input class=\"unit-select\" type=\"checkbox\" value=\"{esc(unit['unit_id'])}\" aria-label=\"Pilih {esc(unit['title_id'])}\">"
            f"<span><strong>{unit['ordinal']}. {esc(unit['title_id'])}</strong><br><code>{esc(unit['unit_id'])}</code> · {esc(unit['origin_kind'])}</span>"
            f"<span class=\"right\">{unit['problem_count']} masalah<br>{unit['segment_count']:,} segmen · PDF {unit['pdf_page_start']}–{unit['pdf_page_end']}</span></label>"
        )
    project_rows = []
    for project in projects:
        search = f"{project['project_id']} {project['title_id']} {project['mathematical_core_id']}".lower()
        project_rows.append(
            f"<label class=\"select-row project-row\" data-search=\"{esc(search)}\">"
            f"<input class=\"project-select\" type=\"checkbox\" value=\"{esc(project['project_id'])}\" aria-label=\"Pilih {esc(project['title_id'])}\">"
            f"<span><strong>{esc(project['title_id'])}</strong><br><code>{esc(project['project_id'])}</code></span>"
            f"<span class=\"right\">{project['file_count']} berkas<br>notebook awal</span></label>"
        )
    data = json.dumps({"units": units, "projects": projects}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).replace("</", "<\\/")
    body = f"""
<p class="muted">C120 · tampilan pengajar · <code>{CONTRACT}</code></p>
<h1>Pemilih unit, masalah, dan proyek</h1>
<p class="lede">Susun paket ajar dari 26 unit native, 141 masalah penguasaan, dan 12 proyek. Ekspor menyimpan identitas, tipe dukungan, halaman, hash, serta tautan—tanpa menyalin badan buku atau mengubah rubrik menjadi jawaban tertutup.</p>
<div class="grid" aria-label="Ringkasan bukti">
<div class="card"><span class="metric">{counts['units']}</span>unit yang dapat dipilih</div>
<div class="card"><span class="metric">{counts['worked_solutions']}</span>solusi tertulis</div>
<div class="card"><span class="metric">{counts['qualitative_rubrics']}</span>rubrik kualitatif</div>
<div class="card"><span class="metric">{counts['projects']}</span>proyek dengan notebook awal</div>
<div class="card"><span class="metric">{counts['correction_rows']}</span>koreksi terlacak</div>
<div class="card"><span class="metric">{counts['terminology_rows']}</span>baris istilah</div>
</div>
<div class="notice"><strong>Batas proyek:</strong> paket proyek memuat notebook awal, pemeriksaan, rubrik, dan provenance, tetapi secara eksplisit tidak mengklaim reproduksi hasil penelitian yang dirujuk.</div>
<div class="controls"><label>Saring unit atau proyek<input id="teacher-filter" type="search" placeholder="judul, ID, atau konsep"></label><button id="select-visible" type="button">Pilih yang terlihat</button><button id="clear" class="secondary" type="button">Kosongkan</button><button id="export" type="button">Ekspor JSON</button><span id="selected-count" aria-live="polite">0 dipilih</span></div>
<h2>Unit dan masalah penguasaan</h2><div class="panel" id="unit-list">{''.join(unit_rows)}</div>
<h2>Proyek pemodelan</h2><div class="panel" id="project-list">{''.join(project_rows)}</div>
<h2>Bukti dan data</h2><p><a href="educator-map.json">Peta pengajar</a> · <a href="rights-and-terms.json">Istilah, koreksi, dan hak komponen</a> · <a href="ledger-references.json">Ledger dan migrasi</a> · <a href="C120.html">Jalur pelajar</a></p>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in educator['limitations'])}</ul>
<script id="selection-data" type="application/json">{data}</script>
<script>
const data=JSON.parse(document.getElementById('selection-data').textContent);const unitById=new Map(data.units.map(x=>[x.unit_id,x]));const projectById=new Map(data.projects.map(x=>[x.project_id,x]));const rows=[...document.querySelectorAll('.select-row')];const boxes=[...document.querySelectorAll('.select-row input')];const filter=document.getElementById('teacher-filter');const count=document.getElementById('selected-count');
function updateCount(){{count.textContent=boxes.filter(x=>x.checked).length+' dipilih';}}function applyFilter(){{const q=filter.value.trim().toLowerCase();for(const row of rows)row.classList.toggle('hidden',!!q&&!row.dataset.search.includes(q));}}
filter.addEventListener('input',applyFilter);for(const box of boxes)box.addEventListener('change',updateCount);document.getElementById('select-visible').addEventListener('click',()=>{{for(const row of rows)if(!row.classList.contains('hidden'))row.querySelector('input').checked=true;updateCount();}});document.getElementById('clear').addEventListener('click',()=>{{for(const box of boxes)box.checked=false;updateCount();}});
document.getElementById('export').addEventListener('click',()=>{{const selectedUnits=[...document.querySelectorAll('.unit-select:checked')].map(x=>unitById.get(x.value));const selectedProjects=[...document.querySelectorAll('.project-select:checked')].map(x=>projectById.get(x.value));const payload={{schema:'c120-educator-selection/1',course_id:'C120',locale:'id-ID',program_prerequisites:['B70','B80','C10'],prerequisite_scope:'central_course_level_only',native_bodies_copied:false,project_result_reproduction_claimed:false,selected_units:selectedUnits,selected_projects:selectedProjects}};const blob=new Blob([JSON.stringify(payload,null,2)+'\\n'],{{type:'application/json'}});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='C120-rencana-pengajar.json';a.click();URL.revokeObjectURL(url);}});
</script>
"""
    return shell("C120 · Pemilih pengajar", body)


def build(native_root: Path, hub_root: Path, adapter: Path) -> dict:
    bundle = derive_projection(native_root, hub_root)
    errors = projection_errors(bundle)
    if errors:
        raise ValueError(f"C120 projection failed: {errors}")
    files = {
        "input/source-lock.json": canonical_json_bytes(bundle["source_lock"]),
        "data/learning-map.json": canonical_json_bytes(bundle["learning_map"]),
        "data/educator-map.json": canonical_json_bytes(bundle["educator_map"]),
        "data/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "data/ledger-references.json": canonical_json_bytes(bundle["ledger_references"]),
        "data/public-evidence.json": canonical_json_bytes(bundle["public_evidence"]),
        "data/rights-and-terms.json": canonical_json_bytes(bundle["rights_and_terms"]),
        "data/claim-boundary.json": canonical_json_bytes(bundle["claim_boundary"]),
        "views/C120.html": render_learner(bundle).encode("utf-8"),
        "views/C120-pengajar.html": render_educator(bundle).encode("utf-8"),
        "fixtures/negative-fixtures.json": canonical_json_bytes({
            "schema": "c120-negative-fixture-index/1",
            "course_id": COURSE_ID,
            "fixtures": [
                "duplicate_unit", "missing_unit", "unit_order_change", "source_bridge_collapse",
                "problem_loss", "support_type_collapse", "hint_loss", "project_loss",
                "project_result_claim", "notebook_count_change", "segment_count_change",
                "terminology_loss", "correction_loss", "backend_hash_downgrade",
                "nonanonymous_github", "nonanonymous_zenodo", "reader_access_downgrade",
                "blanket_license_claim", "native_body_copy", "native_outcome_invention",
                "native_prerequisite_invention", "virtual_backend_materialization",
                "historical_receipt_rewrite", "public_state_change", "input_hash_change",
            ],
        }),
        "README.md": (
            "# C120 common capability adapter\n\n"
            "Zero-copy human-facing projection of the complete public O005 modeling and nonlinear-dynamics backend into `course-learning-capability/1`. "
            "It reuses the exact 81-file reversible migration, preserves 26 ordered unit identities, 4,105 segments, 141 mastery problem IDs with their support types, "
            "26 notebooks, 12 project packets, 321 terminology rows, 160 correction rows, and the verified GitHub/Zenodo/Pages lineage.\n\n"
            "The learner view navigates the public native reader. The educator view exports selected unit, problem, and project identities. The four independently authored bridge units remain distinct from the 22 source-derived units. "
            "No native bodies, per-unit outcomes or prerequisites, learner records, project-result reproduction claims, rewritten historical receipts, or materialized duplicate virtual backend are created.\n"
        ).encode("utf-8"),
    }
    for relative, data_bytes in files.items():
        target = adapter / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data_bytes)
    outputs = [identity(adapter / path, display_path=path) for path in sorted(files)]
    manifest = {
        "schema": "c120-capability-manifest/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "contract": CONTRACT,
        "contract_2_3_1_conformance": "not_claimed",
        "locale": LOCALE,
        "native_family": "modeling_and_nonlinear_dynamics",
        "native_release": NATIVE_VERSION,
        "content_policy": "selected_localized_metadata_and_evidence_only",
        "projection": {
            "zero_copy_native_bodies": True,
            "native_ids_preserved": True,
            "existing_reversible_migration_reused": True,
            "source_and_bridge_units_distinct": True,
            "mastery_support_types_preserved": True,
            "project_result_reproduction_claimed": False,
            "central_course_truth_rewritten": False,
            "historical_migration_receipt_rewritten": False,
            "common_virtual_backend_materialized": False,
            "public_state_changed": False,
        },
        "counts": bundle["capabilities"]["counts"],
        "inputs": bundle["source_lock"]["native_inputs"] + [bundle["source_lock"]["migration_input"]],
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
        "units": manifest["counts"]["units"], "mastery_problems": manifest["counts"]["mastery_problems"],
        "projects": manifest["counts"]["projects"], "terminology_rows": manifest["counts"]["terminology_rows"],
    }).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
