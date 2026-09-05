"""Build D10 learner and educator views from the exact native public backend."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from d10_capability_model_v1 import (
    ARCHIVE_HTML_ROOT,
    ARCHIVE_ROOT,
    CONTRACT,
    COURSE_ID,
    LOCALE,
    NATIVE_ROLE_ID,
    RELEASE_VERSION,
    canonical_json_bytes,
    derive_projection,
    identity,
    projection_errors,
    write_json,
)


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
DEFAULT_NATIVE = WORKSPACE / "04_mirrors/id/measure-integration-id-v1.0.0-audit"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/d10-capability-v1"


STYLE = """
:root{color-scheme:light;--ink:#172b35;--muted:#536973;--paper:#f4f1e8;--card:#fff;--line:#ccd8dc;--accent:#12617a;--warm:#a85622;--ok:#2b7050}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1180px;margin:auto;padding:28px 20px 64px}nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.4rem}a{color:var(--accent);text-underline-offset:3px}
h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.05;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.15rem;max-width:78ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:12px;margin:1.5rem 0}.card,details,.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{font-size:1.8rem;font-weight:760;display:block}.muted{color:var(--muted)}details{margin:.75rem 0}summary{cursor:pointer;font-weight:720}.unit-head{display:flex;justify-content:space-between;gap:1rem;align-items:baseline;flex-wrap:wrap}.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:.1rem .55rem;font-size:.85rem}.notice{border-left:6px solid var(--warm);background:#fff8ef;padding:1rem 1.2rem;border-radius:8px}.good{border-left-color:var(--ok);background:#f3fbf6}.exercise-list{display:flex;gap:.4rem;flex-wrap:wrap;padding:0;list-style:none}.exercise-list code{background:#edf4f6;padding:.12rem .35rem;border-radius:4px}.controls{display:flex;gap:.7rem;flex-wrap:wrap;align-items:end;margin:1rem 0}.controls label{display:grid;gap:.25rem;font-weight:650}.controls input[type=search]{min-width:min(28rem,82vw);padding:.7rem;border:1px solid #81979f;border-radius:7px;font:inherit}button{padding:.65rem .9rem;border:1px solid #0d5067;border-radius:7px;background:#12617a;color:white;font:inherit;font-weight:700;cursor:pointer}button.secondary{background:white;color:#12617a}.unit-row{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:.8rem;align-items:start;border-bottom:1px solid var(--line);padding:.8rem 0}.unit-row:last-child{border-bottom:0}.unit-row input{width:1.2rem;height:1.2rem}.right{text-align:right}.hidden{display:none!important}code{overflow-wrap:anywhere}.small{font-size:.9rem}.archive{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.84rem;overflow-wrap:anywhere}a:focus-visible,summary:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #d58522;outline-offset:3px}@media(max-width:650px){.unit-row{grid-template-columns:auto 1fr}.unit-row .right{grid-column:2;text-align:left}}
""".strip()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, body: str) -> str:
    return (
        "<!doctype html><html lang=\"id\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>"
        "<nav><a href=\"../../id/#course-D10\">Program matematika</a>"
        "<a href=\"../index.html\">Pusat backend</a>"
        "<a href=\"D10.html\">Pelajar</a>"
        "<a href=\"D10-pengajar.html\">Pengajar</a></nav>"
        f"{body}</main></body></html>\n"
    )


def _unit_search_text(unit: dict) -> str:
    return " ".join([
        unit["unit_id"], str(unit["source_anchor"]), unit["source_title"],
        unit["title_id"], " ".join(unit["exercise_ids"]),
    ]).lower()


def render_learner(bundle: dict) -> str:
    learning = bundle["learning_map"]
    counts = bundle["capabilities"]["counts"]
    volume_names = {row["id"]: f"Jilid {row['ordinal']} · {row['subtitle']}" for row in learning["volumes"]}
    blocks = []
    for volume_id in [row["id"] for row in sorted(learning["volumes"], key=lambda row: row["ordinal"])]:
        units = []
        for unit in [row for row in learning["units"] if row["volume_id"] == volume_id]:
            routes = "".join(
                f"<li><strong>{esc(route['title'])}</strong><br><span class=\"archive\">{esc(route['archive_entry'])}</span></li>"
                for route in unit["portable_reader_routes"]
            ) or "<li>Tidak ada klaim pemetaan rute satu-ke-satu; gunakan sumber dan pembaca lengkap.</li>"
            exercises = "".join(f"<li><code>{esc(item)}</code></li>" for item in unit["exercise_ids"])
            units.append(
                f"<details class=\"unit\" data-search=\"{esc(_unit_search_text(unit))}\">"
                f"<summary><span class=\"unit-head\"><span>{unit['ordinal']}. {esc(unit['title_id'])}</span>"
                f"<span class=\"pill\">{unit['exercise_count']} latihan · {unit['explicit_hint_count']} petunjuk</span></span></summary>"
                f"<p><code>{esc(unit['unit_id'])}</code> · {esc(unit['unit_kind'])} · halaman sumber {esc(unit['source_pages'])}</p>"
                f"<p><a href=\"{esc(unit['public_source'])}\">Buka sumber terjemahan tepat</a> · "
                f"SHA-256 target <code>{esc(unit['target_sha256'])}</code></p>"
                f"<p>{unit['formula_count']:,} kemunculan formula · {unit['correction_count']} koreksi ledger.</p>"
                f"<h3>Rute dalam arsip HTML luring</h3><ul>{routes}</ul>"
                f"<h3>Identitas latihan</h3><ul class=\"exercise-list\">{exercises or '<li>Tidak ada latihan bertipe.</li>'}</ul>"
                "</details>"
            )
        blocks.append(f"<section><h2>{esc(volume_names[volume_id])}</h2>{''.join(units)}</section>")

    supplemental = "".join(
        f"<li><strong>{esc(row['title'])}</strong> · <span class=\"archive\">{esc(row['archive_entry'])}</span></li>"
        for row in learning["supplemental_reader_surfaces"]
    )
    body = f"""
<p class="muted">D10 · <code>{NATIVE_ROLE_ID}</code> · edisi {RELEASE_VERSION}</p>
<h1>Ukuran dan Integrasi</h1>
<p class="lede">Navigasi zero-copy untuk dua jilid <em>Fondasi Teori Ukuran</em>. Gunakan pencarian untuk menemukan unit, judul, jangkar sumber, atau ID latihan; badan buku tetap pada edisi publik native.</p>
<div class="grid" aria-label="Ringkasan kursus">
<div class="card"><span class="metric">{counts['official_pages']}</span>halaman sumber resmi</div>
<div class="card"><span class="metric">{counts['units']}</span>unit katalog</div>
<div class="card"><span class="metric">{counts['typed_exercises']:,}</span>latihan bertipe</div>
<div class="card"><span class="metric">{counts['explicit_hints']}</span>petunjuk sumber</div>
<div class="card"><span class="metric">{counts['formula_occurrences']:,}</span>kemunculan formula</div>
<div class="card"><span class="metric">{counts['correction_rows']}</span>koreksi terlacak</div>
</div>
<p><a href="{esc(learning['public_pdf'])}">Unduh PDF lengkap</a> · <a href="{esc(learning['portable_reader'])}">Unduh sumber, backend, dan pembaca HTML luring</a> · <a href="learning-map.json">Data navigasi terbuka</a></p>
<div class="notice"><strong>Batas kebenaran:</strong> 1.096 ID latihan dipertahankan. Angka 1.094 adalah sensus header standar; <code>243Xo</code> dan <code>274Xf</code> memakai header varian yang sah. Hanya 276 petunjuk eksplisit tersedia—tidak ada bank solusi lengkap.</div>
<div class="controls"><label>Cari unit atau latihan<input id="unit-filter" type="search" placeholder="contoh: Radon, 243Xo, probabilitas"></label><span id="match-count" aria-live="polite">94 unit</span></div>
{''.join(blocks)}
<h2>Permukaan pembaca tanpa ikatan unit satu-ke-satu</h2><ul>{supplemental}</ul>
<p class="notice good"><strong>Prasyarat program:</strong> C20 dan C90. Ini adalah relasi tingkat kursus dari kurikulum pusat, bukan klaim graf prasyarat unit native.</p>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in learning['limitations'])}</ul>
<script>
const filter=document.getElementById('unit-filter');const units=[...document.querySelectorAll('.unit')];const count=document.getElementById('match-count');
function applyFilter(){{const q=filter.value.trim().toLowerCase();let shown=0;for(const unit of units){{const visible=!q||unit.dataset.search.includes(q);unit.classList.toggle('hidden',!visible);if(visible)shown++;}}count.textContent=shown+' unit';}}
filter.addEventListener('input',applyFilter);
</script>
"""
    return shell("D10 · Ukuran dan Integrasi", body)


def render_educator(bundle: dict) -> str:
    educator = bundle["educator_map"]
    counts = educator["counts"]
    units = educator["selector"]["selected_units"]
    rows = []
    for unit in units:
        rows.append(
            f"<label class=\"unit-row\" data-search=\"{esc(_unit_search_text(unit))}\">"
            f"<input class=\"unit-select\" type=\"checkbox\" value=\"{esc(unit['unit_id'])}\" aria-label=\"Pilih {esc(unit['title_id'])}\">"
            f"<span><strong>{unit['ordinal']}. {esc(unit['title_id'])}</strong><br><code>{esc(unit['unit_id'])}</code> · {esc(unit['unit_kind'])}<br>"
            f"<span class=\"small muted\">{esc(unit['source_title'])}</span></span>"
            f"<span class=\"right\">{unit['exercise_count']} latihan<br>{unit['explicit_hint_count']} petunjuk · {unit['correction_count']} koreksi</span></label>"
        )
    data = json.dumps(units, ensure_ascii=False, sort_keys=True, separators=(",", ":")).replace("</", "<\\/")
    body = f"""
<p class="muted">D10 · tampilan pengajar · <code>{CONTRACT}</code></p>
<h1>Pemilih unit dan latihan</h1>
<p class="lede">Susun rencana bacaan dari 94 identitas unit native. Ekspor menyimpan ID, judul, halaman, latihan, petunjuk, formula, koreksi, dan tautan sumber tepat—tanpa menyalin badan buku atau menciptakan hasil belajar dan solusi.</p>
<div class="grid" aria-label="Ringkasan bukti">
<div class="card"><span class="metric">{counts['units']}</span>unit yang dapat dipilih</div>
<div class="card"><span class="metric">{counts['typed_exercises']:,}</span>ID latihan eksak</div>
<div class="card"><span class="metric">{counts['terminology_rows']}</span>keputusan istilah</div>
<div class="card"><span class="metric">{counts['correction_rows']}</span>koreksi sumber/target</div>
</div>
<div class="notice"><strong>Jangan dibaca sebagai bank jawaban:</strong> hasil dan bukti matematis dalam backend akhir adalah struktur buku. Adapter mengakui nol solusi lengkap dan hanya {counts['explicit_hints']} petunjuk eksplisit.</div>
<div class="controls"><label>Saring unit<input id="teacher-filter" type="search" placeholder="judul, jangkar, atau ID latihan"></label><button id="select-visible" type="button">Pilih yang terlihat</button><button id="clear" class="secondary" type="button">Kosongkan</button><button id="export" type="button">Ekspor JSON</button><span id="selected-count" aria-live="polite">0 dipilih</span></div>
<div class="panel" id="unit-list">{''.join(rows)}</div>
<h2>Bukti dan data</h2><p><a href="educator-map.json">Peta pengajar</a> · <a href="rights-and-terms.json">Istilah, koreksi, dan hak komponen</a> · <a href="ledger-references.json">Ledger dan provenance</a> · <a href="D10.html">Jalur pelajar</a></p>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in educator['limitations'])}</ul>
<script id="unit-data" type="application/json">{data}</script>
<script>
const units=JSON.parse(document.getElementById('unit-data').textContent);const byId=new Map(units.map(x=>[x.unit_id,x]));const rows=[...document.querySelectorAll('.unit-row')];const boxes=[...document.querySelectorAll('.unit-select')];const filter=document.getElementById('teacher-filter');const selectedCount=document.getElementById('selected-count');
function updateCount(){{selectedCount.textContent=boxes.filter(x=>x.checked).length+' dipilih';}}
function applyFilter(){{const q=filter.value.trim().toLowerCase();for(const row of rows)row.classList.toggle('hidden',!!q&&!row.dataset.search.includes(q));}}
filter.addEventListener('input',applyFilter);for(const box of boxes)box.addEventListener('change',updateCount);
document.getElementById('select-visible').addEventListener('click',()=>{{for(const row of rows)if(!row.classList.contains('hidden'))row.querySelector('input').checked=true;updateCount();}});
document.getElementById('clear').addEventListener('click',()=>{{for(const box of boxes)box.checked=false;updateCount();}});
document.getElementById('export').addEventListener('click',()=>{{const chosen=boxes.filter(x=>x.checked).map(x=>byId.get(x.value));const payload={{schema:'d10-educator-selection/1',course_id:'D10',locale:'id-ID',program_prerequisites:['C20','C90'],prerequisite_scope:'central_course_level_only',native_bodies_copied:false,complete_solution_layer_claimed:false,selected_units:chosen}};const blob=new Blob([JSON.stringify(payload,null,2)+'\\n'],{{type:'application/json'}});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='D10-rencana-pengajar.json';a.click();URL.revokeObjectURL(url);}});
</script>
"""
    return shell("D10 · Pemilih pengajar", body)


def build(native_root: Path, adapter: Path) -> dict:
    bundle = derive_projection(native_root)
    errors = projection_errors(bundle)
    if errors:
        raise ValueError(f"Native projection failed: {errors}")
    files = {
        "input/source-lock.json": canonical_json_bytes(bundle["source_lock"]),
        "data/learning-map.json": canonical_json_bytes(bundle["learning_map"]),
        "data/educator-map.json": canonical_json_bytes(bundle["educator_map"]),
        "data/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "data/ledger-references.json": canonical_json_bytes(bundle["ledger_references"]),
        "data/public-evidence.json": canonical_json_bytes(bundle["public_evidence"]),
        "data/rights-and-terms.json": canonical_json_bytes(bundle["rights_and_terms"]),
        "data/claim-boundary.json": canonical_json_bytes(bundle["claim_boundary"]),
        "views/D10.html": render_learner(bundle).encode("utf-8"),
        "views/D10-pengajar.html": render_educator(bundle).encode("utf-8"),
        "fixtures/negative-fixtures.json": canonical_json_bytes({
            "schema": "d10-negative-fixture-index/1",
            "course_id": COURSE_ID,
            "fixtures": [
                "duplicate_unit", "missing_unit", "exercise_loss", "variant_header_loss",
                "wrong_hint_count", "wrong_formula_count", "wrong_page_total",
                "terminology_loss", "correction_loss", "catalog_manifest_downgrade",
                "nonanonymous_github", "nonanonymous_zenodo", "public_asset_loss",
                "blanket_license_claim", "native_body_copy", "solution_invention",
                "native_outcome_invention", "native_prerequisite_invention",
                "online_native_html_invention", "tagged_pdf_invention",
                "public_state_change", "input_hash_change",
            ],
        }),
        "README.md": (
            "# D10 common capability adapter\n\n"
            "Zero-copy projection of the complete public O007/Fremlin Volumes I–II backend "
            "into `course-learning-capability/1`. It preserves 94 ordered unit identities, "
            "1,096 typed exercise IDs, 276 explicit source hints, 53,491 formula occurrences, "
            "420 correction rows, 132 structured terminology decisions, all 506 catalog-manifest "
            "members, and the exact GitHub/Zenodo release lineage.\n\n"
            "The learner view provides searchable unit/source/archive navigation. The educator "
            "view exports selected native unit and exercise identities. No native bodies, outcomes, "
            "per-unit prerequisites, learner records, complete solutions, online-native-HTML claim, "
            "tagged-PDF claim, or blanket license are created.\n"
        ).encode("utf-8"),
    }
    for relative, data_bytes in files.items():
        target = adapter / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data_bytes)
    outputs = [identity(adapter / path, display_path=path) for path in sorted(files)]
    manifest = {
        "schema": "d10-capability-manifest/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "contract": CONTRACT,
        "contract_2_3_1_conformance": "not_claimed",
        "locale": LOCALE,
        "native_family": "fremlin_measure_theory_volumes_1_2",
        "native_release": RELEASE_VERSION,
        "content_policy": "selected_localized_metadata_and_evidence_only",
        "projection": {
            "zero_copy_native_bodies": True,
            "native_ids_preserved": True,
            "catalog_manifest_replayed": True,
            "reader_routes_distinct_from_catalog_units": True,
            "source_hints_not_retyped_as_full_solutions": True,
            "central_course_truth_rewritten": False,
            "public_state_changed": False,
            "strict_native_roundtrip_claimed": False,
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
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    args = parser.parse_args()
    manifest = build(args.native_root.resolve(), args.adapter.resolve())
    print(canonical_json_bytes({
        "state": "pass", "course_id": COURSE_ID,
        "outputs": len(manifest["outputs"]),
        "units": manifest["counts"]["units"],
        "typed_exercises": manifest["counts"]["typed_exercises"],
        "terminology_rows": manifest["counts"]["terminology_rows"],
    }).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
