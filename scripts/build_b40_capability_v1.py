"""Build B40 learner/educator capability data from exact native R005 evidence."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from b40_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    LOCALE,
    NATIVE_ROLE_ID,
    PUBLIC_READBACK,
    canonical_json_bytes,
    derive_projection,
    identity,
    projection_errors,
    write_json,
)


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
DEFAULT_NATIVE = WORKSPACE / "04_mirrors/id/hefferon-linear-algebra-id/backend"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/b40-capability-v1"
DEFAULT_DOCS = PROJECT / "docs/backend/b40"

STYLE = """
:root{color-scheme:light;--ink:#17242d;--muted:#5b6870;--paper:#f3f0e8;--card:#fff;--line:#d8d0bf;--blue:#145d73;--deep:#173e54;--warm:#a65324;--good:#2f6a45}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}main{max-width:1240px;margin:auto;padding:28px 20px 72px}
nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.4rem}a{color:var(--blue);text-underline-offset:3px}h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.05;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.12rem;max-width:88ch}.muted{color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:1.5rem 0}.card,.panel,details{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{display:block;font-size:1.8rem;font-weight:790}
.component{border-top:6px solid var(--deep);margin:1rem 0}.component:nth-of-type(2){border-top-color:var(--warm)}.component:nth-of-type(3){border-top-color:var(--good)}details{margin:.75rem 0}summary{cursor:pointer;font-weight:740}.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:.1rem .55rem;font-size:.85rem}
.notice{border-left:6px solid var(--warm);background:#fff8ef;padding:1rem 1.2rem;border-radius:8px}.good{border-left-color:var(--good);background:#f3fbf6}.controls{display:flex;gap:.65rem;flex-wrap:wrap;align-items:end;margin:1rem 0}.controls label{display:grid;gap:.25rem;font-weight:650}.controls input[type=search],.controls select{min-width:min(28rem,80vw);padding:.67rem;border:1px solid #83909a;border-radius:7px;font:inherit}.controls select{min-width:12rem}button{padding:.65rem .9rem;border:1px solid #0d3c52;border-radius:7px;background:var(--deep);color:#fff;font:inherit;font-weight:700;cursor:pointer}button.secondary{background:#fff;color:var(--deep)}
.select-row{display:grid;grid-template-columns:auto minmax(0,1fr) minmax(14rem,auto);gap:.8rem;align-items:start;border-bottom:1px solid var(--line);padding:.72rem 0}.select-row:last-child{border-bottom:0}.select-row input{width:1.2rem;height:1.2rem}.right{text-align:right}.hidden{display:none!important}code{overflow-wrap:anywhere}.small{font-size:.9rem}.sections{columns:2;column-gap:2rem}.sections li{break-inside:avoid;margin:.25rem 0}
a:focus-visible,summary:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #d58c2d;outline-offset:3px}@media(max-width:720px){.select-row{grid-template-columns:auto 1fr}.select-row .right{grid-column:2;text-align:left}.sections{columns:1}}
""".strip()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def presentation_title(record: dict[str, Any]) -> object:
    return record.get("presentation_title_id") or record.get("title_id") or record.get("source_title")


def native_title_note(record: dict[str, Any]) -> str:
    raw = record.get("native_title_id") or record.get("title_id")
    shown = presentation_title(record)
    if raw and shown != raw:
        return f' <span class="muted">(judul native mentah: <code>{esc(raw)}</code>)</span>'
    return ""


def shell(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>'
        '<nav><a href="../../id/#course-B40">Program matematika</a>'
        '<a href="../index.html">Pusat backend</a>'
        '<a href="B40.html">Pelajar</a>'
        '<a href="B40-pengajar.html">Pengajar</a></nav>'
        f'{body}</main></body></html>\n'
    )


def _chapter_search(component: dict[str, Any], chapter: dict[str, Any]) -> str:
    return " ".join([
        component["component"], component["component_id"], component["component_label_id"], chapter["chapter_id"],
        str(presentation_title(chapter) or ""), chapter.get("title_id") or "", chapter.get("source_title") or "",
        " ".join(
            " ".join([
                section["section_id"],
                str(presentation_title(section) or ""),
                section.get("title_id") or "",
                section.get("source_title") or "",
            ])
            for section in chapter["sections"]
        ),
    ]).lower()


def _unit_search(unit: dict[str, Any], answer: dict[str, Any] | None) -> str:
    return " ".join([
        unit["unit_id"], str(presentation_title(unit) or ""), unit.get("title_id") or "", unit.get("source_title") or "",
        unit.get("kind") or "", unit.get("native_kind") or "", unit.get("source_locator") or "",
        unit.get("target_locator") or "", " ".join(unit.get("concept_ids", [])),
        answer.get("provenance_class", "") if answer else "",
    ]).lower()


def render_learner(bundle: dict[str, Any]) -> str:
    learning = bundle["learning_map"]
    counts = bundle["capabilities"]["counts"]
    component_cards = []
    for component in learning["components"]:
        artifact = component["reader_artifact"]
        release = artifact["public_release"]
        chapters = []
        for chapter in component["chapters"]:
            sections = "".join(
                f'<li><strong>{esc(presentation_title(section) or section["section_id"])}</strong>{native_title_note(section)} '
                f'<span class="muted">· {esc(section["section_id"])}</span></li>'
                for section in chapter["sections"]
            ) or '<li class="muted">Tidak ada unit bagian native di bawah bab ini.</li>'
            chapters.append(
                f'<details class="chapter" data-search="{esc(_chapter_search(component, chapter))}">'
                f'<summary>{esc(presentation_title(chapter) or chapter["chapter_id"])} '
                f'<span class="pill">{len(chapter["sections"])} bagian</span></summary>'
                f'<p class="small"><code>{esc(chapter["chapter_id"])}</code><br>'
                f'{native_title_note(chapter)}<br>'
                f'Lokator target: <code>{esc(chapter.get("target_locator"))}</code> · hash <code>{esc(chapter.get("target_sha256"))}</code></p>'
                f'<ul class="sections">{sections}</ul></details>'
            )
        component_cards.append(
            f'<section class="card component"><h2>{esc(component["component_label_id"])} — {esc(presentation_title(component))}</h2>'
            f'<p class="small"><code>{esc(component["component_id"])}</code></p>'
            f'<p>{component["unit_count"]:,} unit · {component["chapter_count"]} bab · {component["section_count"]} bagian · '
            f'{component["closure_file_count"]} berkas dalam penutupan komponen.</p>'
            f'<p><a href="{esc(release["url"])}">Unduh PDF ({artifact["page_count"]} halaman)</a> · '
            f'<a href="public-evidence.json">Periksa hash artefak</a></p>'
            f'<p class="small">Status publik saat ini: <strong>{esc(artifact["current_public_status"])}</strong> '
            f'(diverifikasi {esc(artifact["current_public_status_verified_on"])}). '
            f'Catatan native historis: <code>{esc(artifact["native_publication_status"])}</code> '
            f'pada {esc(artifact["native_status_recorded_on"])}.</p>'
            f'<p class="small">SHA-256 PDF: <code>{esc(artifact["sha256"])}</code></p>'
            f'{"".join(chapters)}</section>'
        )
    landing = learning["public_reader_landing_page"]
    body = f"""
<p class="muted">B40 · <code>{NATIVE_ROLE_ID}</code> · <code>{CONTRACT}</code></p>
<h1>Aljabar Linear</h1>
<p class="lede">Jalur terverifikasi untuk edisi Bahasa Indonesia karya Hefferon: buku teks, buku jawaban, dan laboratorium Sage. Peta mempertahankan semua {counts['units']:,} ID unit native, 17 bab, 57 bagian, serta hash dan lokatornya tanpa menyalin isi buku.</p>
<div class="grid" aria-label="Ringkasan kursus">
<div class="card"><span class="metric">{counts['target_reader_pages']:,}</span>halaman pada 3 PDF</div>
<div class="card"><span class="metric">{counts['components']}</span>komponen</div>
<div class="card"><span class="metric">{counts['units']:,}</span>unit stabil</div>
<div class="card"><span class="metric">{counts['exercises']:,}</span>latihan dengan jawaban</div>
<div class="card"><span class="metric">{counts['concepts']}</span>konsep dan istilah</div>
<div class="card"><span class="metric">{counts['corrections']}</span>koreksi terlacak</div>
</div>
<p><a href="{esc(landing['url'])}">Buka halaman arahan rilis</a> · <a href="learning-map.json">Data jalur lengkap</a> · <a href="concept-index.json">Indeks konsep</a></p>
<div class="notice"><strong>Batas format:</strong> URL pembaca publik yang diverifikasi adalah halaman arahan rilis, bukan buku teks HTML. Artefak pembelajaran native yang dibuktikan di sini adalah tiga PDF; adapter tidak mengklaim EPUB, HTML semantik buku, PDF bertag, MathML, atau kesesuaian aksesibilitas.</div>
<div class="notice good"><strong>Hak penggunaan:</strong> sebelas catatan hak native dipertahankan per komponen dan artefak; adapter tidak meratakan semuanya menjadi satu lisensi. <a href="rights-and-terms.json">Baca catatan hak dan rujukan istilah/koreksi</a>.</div>
<div class="controls"><label>Cari komponen, bab, bagian, atau ID<input id="chapter-filter" type="search" placeholder="contoh: ruang vektor, metode Gauss, r005..."></label><span id="match-count" aria-live="polite">17 bab</span></div>
{''.join(component_cards)}
<p class="notice good"><strong>Prasyarat dan hasil belajar:</strong> backend native menandai prasyarat kursus sebagai “{esc(learning['prerequisite_status'])}” dan tidak menyediakan hasil belajar. Adapter mempertahankan batas itu.</p>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in learning['limitations'])}</ul>
<script>
const filter=document.getElementById('chapter-filter');const chapters=[...document.querySelectorAll('.chapter')];const count=document.getElementById('match-count');
function applyFilter(){{const q=filter.value.trim().toLowerCase();let shown=0;for(const row of chapters){{const visible=!q||row.dataset.search.includes(q);row.classList.toggle('hidden',!visible);if(visible)shown++;}}count.textContent=shown+' bab';}}
filter.addEventListener('input',applyFilter);
</script>
"""
    return shell("B40 · Aljabar Linear", body)


def render_educator(bundle: dict[str, Any]) -> str:
    educator = bundle["educator_map"]
    counts = educator["counts"]
    units = educator["selector"]["units"]
    answer_rows = educator["selector"]["exercise_answers"]
    answer_by_exercise = {row["exercise_unit_id"]: row for row in answer_rows}
    answer_by_unit = {row["answer_unit_id"]: row for row in answer_rows}
    rows = []
    for unit in units:
        answer = answer_by_exercise.get(unit["unit_id"]) or answer_by_unit.get(unit["unit_id"])
        title = presentation_title(unit) or unit["unit_id"]
        if answer:
            answer_label = (
                "jawaban edisi Indonesia · HLA-A0300"
                if answer["provenance_class"] == "indonesian_edition_supplied"
                else "jawaban hulu native"
            )
        else:
            answer_label = "bukan unit latihan"
        rows.append(
            f'<label class="select-row unit-row" data-kind="{esc(unit["kind"])}" data-search="{esc(_unit_search(unit, answer))}">'
            f'<input class="unit-select" type="checkbox" value="{esc(unit["unit_id"])}" aria-label="Pilih {esc(title)}">'
            f'<span><strong>{esc(title)}</strong><br><code>{esc(unit["unit_id"])}</code><br>'
            f'<span class="small">{esc(unit.get("target_locator"))}</span></span>'
            f'<span class="right">{esc(unit["kind"])} · {unit["segment_count"]} segmen<br>{len(unit["concept_ids"])} konsep · {esc(answer_label)}</span></label>'
        )
    export_data = json.dumps(
        {"units": units, "exercise_answers": answer_rows},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    body = f"""
<p class="muted">B40 · tampilan pengajar · <code>{CONTRACT}</code></p>
<h1>Pemilih unit dan jawaban</h1>
<p class="lede">Cari seluruh {counts['units']:,} unit native dan ekspor pilihan sebagai JSON metadata. Semua {counts['exercises']:,} latihan dipasangkan secara bijektif dengan tepat satu jawaban native, tanpa menyertakan isi latihan atau jawaban.</p>
<div class="grid" aria-label="Ringkasan bukti">
<div class="card"><span class="metric">{counts['units']:,}</span>unit terindeks</div>
<div class="card"><span class="metric">{counts['exercises']:,}</span>latihan</div>
<div class="card"><span class="metric">{counts['answers']:,}</span>jawaban</div>
<div class="card"><span class="metric">{counts['native_upstream_answers']:,}</span>jawaban hulu</div>
<div class="card"><span class="metric">{counts['indonesian_edition_supplied_answers']}</span>jawaban edisi Indonesia</div>
<div class="card"><span class="metric">{counts['relations']:,}</span>relasi native</div>
</div>
<div class="notice"><strong>Asal jawaban tidak diratakan:</strong> 1.035 jawaban berasal dari lingkungan jawaban hulu native. Dua jawaban untuk latihan Leontief dipasok oleh edisi Indonesia karena tidak ada pada sumber terpancang maupun buku jawaban resmi; keduanya mempertahankan otorisasi <code>HLA-A0300</code>, ID koreksi, lokator ledger, dan hash ledger.</div>
<div class="controls"><label>Saring unit<input id="teacher-filter" type="search" placeholder="judul, ID, jenis, lokator, konsep, atau asal jawaban"></label><label>Jenis<select id="kind-filter"><option value="">Semua jenis</option><option value="exercise">Latihan</option><option value="answer">Jawaban</option><option value="chapter">Bab</option><option value="section">Bagian</option><option value="interactive">Interaktif</option><option value="program">Program</option></select></label><button id="select-visible" type="button">Pilih yang terlihat</button><button id="clear" class="secondary" type="button">Kosongkan</button><button id="export" type="button">Ekspor JSON</button><span id="selected-count" aria-live="polite">0 dipilih</span></div>
<div class="panel" id="unit-list">{''.join(rows)}</div>
<h2>Bukti dan data</h2><p><a href="educator-map.json">Peta pengajar</a> · <a href="learning-map.json">Peta pelajar</a> · <a href="concept-index.json">Konsep dan istilah</a> · <a href="relation-index.json">Seluruh 13.999 relasi</a> · <a href="rights-and-terms.json">Hak dan ledger</a> · <a href="public-evidence.json">Bukti publik</a></p>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in educator['limitations'])}</ul>
<script id="selection-data" type="application/json">{export_data}</script>
<script>
const data=JSON.parse(document.getElementById('selection-data').textContent);const unitById=new Map(data.units.map(x=>[x.unit_id,x]));
const rows=[...document.querySelectorAll('.unit-row')];const boxes=[...document.querySelectorAll('.unit-select')];const filter=document.getElementById('teacher-filter');const kind=document.getElementById('kind-filter');const count=document.getElementById('selected-count');
function updateCount(){{count.textContent=boxes.filter(x=>x.checked).length+' dipilih';}}function applyFilter(){{const q=filter.value.trim().toLowerCase();for(const row of rows){{const visible=(!q||row.dataset.search.includes(q))&&(!kind.value||row.dataset.kind===kind.value);row.classList.toggle('hidden',!visible);}}}}
filter.addEventListener('input',applyFilter);kind.addEventListener('change',applyFilter);for(const box of boxes)box.addEventListener('change',updateCount);document.getElementById('select-visible').addEventListener('click',()=>{{for(const row of rows)if(!row.classList.contains('hidden'))row.querySelector('input').checked=true;updateCount();}});document.getElementById('clear').addEventListener('click',()=>{{for(const box of boxes)box.checked=false;updateCount();}});
document.getElementById('export').addEventListener('click',()=>{{const selectedUnits=boxes.filter(x=>x.checked).map(x=>unitById.get(x.value));const selectedIds=new Set(selectedUnits.map(x=>x.unit_id));const selectedAnswers=data.exercise_answers.filter(x=>selectedIds.has(x.exercise_unit_id)||selectedIds.has(x.answer_unit_id));const payload={{schema:'b40-educator-selection/1',course_id:'B40',locale:'id-ID',native_bodies_copied:false,native_unit_outcomes_invented:false,native_unit_prerequisites_invented:false,selected_units:selectedUnits,exact_exercise_answers:selectedAnswers}};const blob=new Blob([JSON.stringify(payload,null,2)+'\\n'],{{type:'application/json'}});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='B40-rencana-pengajar.json';a.click();URL.revokeObjectURL(url);}});
</script>
"""
    return shell("B40 · Pemilih pengajar", body)


def _readme() -> bytes:
    return (
        "# B40 common capability adapter\n\n"
        "Thin zero-copy learner and educator capability index derived from the R005 Hefferon Linear Algebra backend for `course-learning-capability/1`. "
        "It is not a second full backend: it selects identifiers, navigation metadata, locators, hashes, rights, and receipt evidence while preserving all 3,541 stable unit IDs, all 13,999 native relation IDs, the 1,037-by-1,037 exercise-answer bijection, 114 concepts and terms, 307 corrections, 11 component-specific rights records, and eight exact native artifact identities.\n\n"
        "The learner route spans the textbook, answer-book shell, and Sage lab with their 17 chapters and 57 sections. The educator selector distinguishes 1,035 native upstream answers from two Indonesian-edition-supplied answers authorized by HLA-A0300. "
        "Three damaged extracted headings have transparent presentation-only normalizations; their native titles, locators, and hashes remain alongside them. Historical native publication status is dated separately from current status reported by the locked anonymous readback. No segment or book body is copied, and no prerequisites, outcomes, semantic textbook HTML, EPUB, tagged-PDF, MathML, or accessibility conformance are invented or claimed.\n\n"
        "Terms are canonical in `data/concept-index.json`; corrections are canonical in `data/ledger-references.json`; `data/rights-and-terms.json` references those stores rather than duplicating their rows. The 11 native rights records remain component-specific and are not collapsed into a blanket license.\n\n"
        "The existing lossless common migration receipt is referenced, not replayed into an 83.9 MB duplicate. Run `python -B scripts/build_b40_capability_v1.py` and then `python -B scripts/validate_b40_capability_v1.py` from the central project root.\n"
    ).encode("utf-8")


NEGATIVE_FIXTURES = [
    ("duplicate_unit", "B40-UNIT-IDENTITY"),
    ("missing_unit", "B40-UNIT-IDENTITY"),
    ("unit_order_change", "B40-UNIT-ORDER"),
    ("component_loss", "B40-LEARNER-ROUTE"),
    ("chapter_loss", "B40-LEARNER-ROUTE"),
    ("presentation_title_loss", "B40-PRESENTATION-TITLES"),
    ("route_assignment_loss", "B40-ROUTE-COVERAGE"),
    ("prerequisite_invention", "B40-COURSE-PREREQUISITE"),
    ("outcome_invention", "B40-COURSE-OUTCOME"),
    ("answer_mapping_loss", "B40-ANSWER-BIJECTION"),
    ("duplicate_answer_mapping", "B40-ANSWER-BIJECTION"),
    ("ordinal_answer_selector", "B40-ANSWER-ID-SELECTOR"),
    ("answer_direction_reverse", "B40-ANSWER-DIRECTION"),
    ("answer_backpointer_corrupt", "B40-ANSWER-BACKPOINTER"),
    ("answer_order_path_corrupt", "B40-ANSWER-ORDER-PATH"),
    ("answer_locator_hash_corrupt", "B40-ANSWER-LOCATOR-HASH"),
    ("answer_provenance_collapse", "B40-ANSWER-PROVENANCE"),
    ("answer_provenance_symmetric_swap", "B40-ANSWER-PROVENANCE"),
    ("answer_authorization_loss", "B40-ANSWER-AUTHORIZATION"),
    ("concept_loss", "B40-CONCEPTS"),
    ("term_loss", "B40-TERMS"),
    ("relation_loss", "B40-RELATIONS"),
    ("relation_type_change", "B40-RELATION-TYPES"),
    ("relation_endpoint_change", "B40-RELATION-PROJECTION"),
    ("projection_double_count", "B40-PROJECTION-DOUBLE-COUNT"),
    ("terminology_loss", "B40-LEDGER-CLOSURE"),
    ("correction_loss", "B40-LEDGER-CLOSURE"),
    ("redundant_terminology_materialization", "B40-PROJECTION-REDUNDANCY"),
    ("redundant_correction_materialization", "B40-PROJECTION-REDUNDANCY"),
    ("rights_loss", "B40-RIGHTS"),
    ("artifact_page_change", "B40-ARTIFACTS"),
    ("artifact_status_conflation", "B40-ARTIFACT-STATUS"),
    ("migration_roundtrip_downgrade", "B40-MIGRATION-ROUNDTRIP"),
    ("capability_summary_change", "B40-CAPABILITIES"),
    ("closed_public_access", "B40-PUBLIC-ACCESS"),
    ("public_checks_change", "B40-PUBLIC-EVIDENCE"),
    ("credentials_recorded", "B40-PUBLIC-EVIDENCE"),
    ("reader_identity_change", "B40-PUBLIC-EVIDENCE"),
    ("public_payload_injection", "B40-PUBLIC-ALLOWLIST"),
    ("reader_payload_injection", "B40-PUBLIC-ALLOWLIST"),
    ("closed_zenodo", "B40-ZENODO-ACCESS"),
    ("reader_scope_overclaim", "B40-READER-SCOPE"),
    ("semantic_html_overclaim", "B40-FORMAT-OVERCLAIM"),
    ("epub_overclaim", "B40-FORMAT-OVERCLAIM"),
    ("accessibility_overclaim", "B40-FORMAT-OVERCLAIM"),
    ("native_body_copy", "B40-BOUNDARY-NATIVE_BODIES_COPIED"),
    ("body_field_injection", "B40-DATA-BODY-COPY"),
    ("native_segment_copy", "B40-BOUNDARY-NATIVE_SEGMENTS_COPIED"),
    ("answer_join_inference", "B40-BOUNDARY-EXERCISE_ANSWER_JOINS_INFERRED"),
    ("supplied_answer_retyping", "B40-BOUNDARY-TARGET_SUPPLIED_ANSWERS_RETYPED_AS_UPSTREAM"),
    ("authorization_omission", "B40-BOUNDARY-TARGET_SUPPLIED_AUTHORIZATION_OMITTED"),
    ("blanket_license_claim", "B40-RIGHTS"),
    ("common_backend_materialization", "B40-BOUNDARY-COMMON_VIRTUAL_BACKEND_MATERIALIZED"),
    ("public_state_change", "B40-PUBLIC-ACCESS"),
    ("unqualified_source_path", "B40-SOURCE-ROOT"),
    ("source_lock_native_role_change", "B40-SOURCE-LOCK-IDENTITY"),
    ("source_repository_change", "B40-SOURCE-LOCK-REPOSITORY"),
    ("input_hash_change", "B40-SOURCE-HASH:units.jsonl"),
    ("manifest_count_change", "B40-MANIFEST-COUNTS"),
    ("stale_receipt_survival", "B40-STALE-RECEIPT"),
    ("publication_noise_in_replay", "B40-REPLAY-INVENTORY"),
    ("paired_receipt_partial_publish", "B40-RECEIPT-ROLLBACK"),
]


def _documentation_files(files: dict[str, bytes]) -> dict[str, bytes]:
    mappings = {
        "views/B40.html": "B40.html",
        "views/B40-pengajar.html": "B40-pengajar.html",
        "data/learning-map.json": "learning-map.json",
        "data/educator-map.json": "educator-map.json",
        "data/concept-index.json": "concept-index.json",
        "data/relation-index.json": "relation-index.json",
        "data/rights-and-terms.json": "rights-and-terms.json",
        "data/ledger-references.json": "ledger-references.json",
        "data/public-evidence.json": "public-evidence.json",
    }
    return {target: files[source] for source, target in mappings.items()}


def _documentation_output_names() -> list[str]:
    return sorted((*_documentation_files({key: b"" for key in (
        "views/B40.html",
        "views/B40-pengajar.html",
        "data/learning-map.json",
        "data/educator-map.json",
        "data/concept-index.json",
        "data/relation-index.json",
        "data/rights-and-terms.json",
        "data/ledger-references.json",
        "data/public-evidence.json",
    )}), "manifest.json", "validation.json"))


def _invalidate_validation_receipts(adapter: Path, docs_root: Path | None) -> None:
    paths = [adapter / "validation.json"]
    if docs_root is not None:
        paths.append(docs_root / "validation.json")
    for path in paths:
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"B40 validation receipt target is not a regular file: {path}")
            path.unlink()


def build(native_root: Path, hub_root: Path, adapter: Path, docs_root: Path | None = None) -> dict[str, Any]:
    _invalidate_validation_receipts(adapter, docs_root)
    bundle = derive_projection(native_root, hub_root)
    errors = projection_errors(bundle)
    if errors:
        raise ValueError(f"B40 projection failed: {errors}")
    files = {
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
        "views/B40.html": render_learner(bundle).encode("utf-8"),
        "views/B40-pengajar.html": render_educator(bundle).encode("utf-8"),
        "fixtures/negative-fixtures.json": canonical_json_bytes({
            "schema": "b40-negative-fixture-index/1",
            "course_id": COURSE_ID,
            "fixtures": [{"name": name, "expected_error": error} for name, error in NEGATIVE_FIXTURES],
        }),
        "README.md": _readme(),
    }
    for relative, data in files.items():
        target = adapter / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    outputs = [identity(adapter / path, display_path=path) for path in sorted(files)]
    source_lock = bundle["source_lock"]
    manifest = {
        "schema": "b40-capability-manifest/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "contract": CONTRACT,
        "contract_2_3_1_conformance": "not_claimed",
        "locale": LOCALE,
        "native_family": "hefferon_modular_latex_backend",
        "content_policy": "stable_native_ids_selected_metadata_locators_hashes_and_receipt_urls_only",
        "projection": {
            "zero_copy_native_bodies": True,
            "native_segments_copied": False,
            "native_ids_preserved": True,
            "existing_reversible_migration_reused": True,
            "all_unit_ids_indexed": True,
            "all_relation_ids_indexed": True,
            "exercise_answer_bijection_preserved": True,
            "target_supplied_answer_provenance_preserved": True,
            "native_prerequisites_invented": False,
            "native_outcomes_invented": False,
            "native_semantic_html_claimed": False,
            "native_epub_claimed": False,
            "accessibility_conformance_claimed": False,
            "common_virtual_backend_materialized": False,
            "public_state_changed": False,
        },
        "counts": bundle["capabilities"]["counts"],
        "inputs": [
            source_lock["manifest_input"],
            *source_lock["native_inputs"],
            source_lock["migration_input"],
            source_lock["public_readback_input"],
        ],
        "outputs": outputs,
        "documentation_outputs": _documentation_output_names(),
        "validation_path": "validation.json",
        "public_documentation": {
            "base_path": "docs/backend/b40",
            "learner_path": "docs/backend/b40/B40.html",
            "educator_path": "docs/backend/b40/B40-pengajar.html",
            "manifest_path": "docs/backend/b40/manifest.json",
            "validation_path": "docs/backend/b40/validation.json",
        },
    }
    write_json(adapter / "manifest.json", manifest)
    if docs_root is not None:
        documentation = _documentation_files(files)
        documentation["manifest.json"] = canonical_json_bytes(manifest)
        for relative, data in documentation.items():
            target = docs_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--hub-root", type=Path, default=PROJECT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--docs-root", type=Path, default=DEFAULT_DOCS)
    parser.add_argument("--no-docs", action="store_true")
    args = parser.parse_args()
    docs = None if args.no_docs else args.docs_root.resolve()
    manifest = build(args.native_root.resolve(), args.hub_root.resolve(), args.adapter.resolve(), docs)
    print(canonical_json_bytes({
        "state": "pass",
        "course_id": COURSE_ID,
        "outputs": len(manifest["outputs"]),
        "units": manifest["counts"]["units"],
        "relations": manifest["counts"]["relations"],
        "exercises": manifest["counts"]["exercises"],
        "answers": manifest["counts"]["answers"],
    }).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
