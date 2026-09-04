"""Build the C90 topology learner and educator capability over frozen metadata."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from topology_capability_v1 import BASE, DOCS, READER_URL, ROOT, build_model, encoded, fact, read_inputs


E = lambda value: html.escape(str(value if value is not None else ""), quote=True)
A = lambda url, label: f'<a href="{E(url)}">{E(label)}</a>'
SITE_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/backend/topology/"
CSS = """*{box-sizing:border-box}:root{color-scheme:light;--ink:#17364a;--paper:#f7f5ee;--edge:#c8d5d9;--accent:#075f7d;--warn:#814d00}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.62 system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:28px 24px 64px}a{color:var(--accent);text-underline-offset:3px}nav,.links,.stages{display:flex;gap:16px;flex-wrap:wrap}h1{font-size:clamp(1.9rem,4vw,3rem);line-height:1.12}h2{margin-top:36px}p{max-width:88ch}.muted,small{color:#526d77}.warning{border-left:5px solid var(--warn);padding:10px 16px;background:#fff7e8}.skip{position:absolute;left:-9999px}.skip:focus{left:16px;top:8px;background:white;padding:8px}:focus-visible{outline:3px solid #db8b17;outline-offset:3px}.filters{display:flex;gap:16px;flex-wrap:wrap;border-block:1px solid var(--edge);padding:18px 0}label{display:block}input,select,textarea,button{font:inherit;padding:8px;max-width:100%}textarea{width:100%;min-height:260px}article{padding:16px 0;border-bottom:1px solid var(--edge)}article h3{margin:.2rem 0}details{margin:12px 0}summary{cursor:pointer}code,pre{overflow-wrap:anywhere;white-space:pre-wrap}.badge{display:inline-block;border:1px solid var(--edge);border-radius:1rem;padding:.05rem .55rem;margin-right:.4rem}[hidden]{display:none!important}footer{margin-top:44px;border-top:1px solid var(--edge)}@media print{nav,.filters,button,.skip{display:none}main{padding:0}body{background:white;font-size:10pt}article{break-inside:avoid}}"""


def build(output_root=ROOT):
    source = read_inputs()
    model = build_model(source)
    outputs = {}

    def put(relative, value):
        outputs[str(relative).replace("\\", "/")] = value.encode("utf-8") if isinstance(value, str) else encoded(value)

    nav = "".join(A(file, label) for file, label in [
        ("C90.html", "Peta bacaan"), ("latihan.html", "Latihan bertahap"),
        ("pengajar.html", "Untuk pengajar"), ("istilah.html", "Istilah"),
        ("catatan.html", "Koreksi & hak"),
    ])

    def shell(title, body):
        release = model["native_edition"]["public_release"]
        return f'''<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} — Program matematika</title><meta name="description" content="Topologi: peta bacaan, latihan bertahap, dukungan pengajar, istilah, koreksi dan provenance edisi Indonesia."><style>{CSS}</style></head><body><a class="skip" href="#main">Lewati ke isi</a><main id="main"><nav>{A('../../id/','Program matematika')}{A('../index.html','Pusat belajar')}</nav><nav aria-label="Alat topologi">{nav}</nav><h1>{E(title)}</h1>{body}<footer><p>Lapisan ini tidak menyalin atau menulis ulang buku. Ia menghubungkan 20 bab, 20 pendamping, delapan modul penyempurnaan, dan 1.227 rekaman latihan ke pembaca PreTeXt asli.</p><details><summary>Provenans, rilis, dan batas klaim</summary><p>Git: <code>{E(model['native_edition']['commit'])}</code>, pohon <code>{E(model['native_edition']['tree'])}</code>. Rilis publik saat ini: {A('https://doi.org/'+release['record_doi'],release['record_doi'])}; konsep: {A('https://doi.org/'+release['concept_doi'],release['concept_doi'])}. Paket sumber/backend pada rilis adalah cuplikan tersegel yang lebih lama daripada metadata Git yang dibekukan untuk integrasi ini; keduanya tidak dinyatakan identik.</p><p>HTML semantik adalah permukaan aksesibel utama. PDF belum bertag. Dua koreksi sumber tetap belum terselesaikan dan satu istilah tetap provisional; status itu sengaja terlihat. Tidak ada klaim round-trip umum ke format native atau sertifikasi pembelajaran manusia.</p><p>{A('learning-map.json','Data integrasi')} · {A('validation.json','Hasil pemeriksaan')} · {A(model['native_edition']['repository'],'Repositori buku')}</p></details></footer></main><script src="topology.js"></script></body></html>\n'''

    def filters(include_context=True, include_kind=True):
        context = ''
        if include_context:
            options = ''.join(f'<option value="chapter_{n:02d}">Bab {n}</option>' for n in range(1, 21))
            options += ''.join(f'<option value="{E(module["module_id"])}">Penyempurnaan: {E(module["title"])}</option>' for module in model["completion_modules"])
            context = f'<label>Konteks <select id="context"><option value="">Semua</option>{options}</select></label>'
        kind = '<label>Jenis <select id="kind"><option value="">Semua</option><option value="source_support">Dukungan tugas sumber</option><option value="mastery">Penguasaan tambahan</option></select></label>' if include_kind else ''
        return f'<div class="filters"><label>Cari judul atau identitas <input id="query" type="search"></label>{context}{kind}</div><p id="count" role="status" aria-live="polite"></p>'

    def entry_rows(teacher=False):
        result = []
        for entry in model["entries"]:
            context_label = f'Bab {entry["chapter"]}' if entry["chapter"] else next(m["title"] for m in model["completion_modules"] if m["module_id"] == entry["completion_module"])
            stages = ''.join(A(entry["stage_urls"][name], label) for name, label in [
                ("statement", "Pernyataan"), ("hint", "Petunjuk"),
                ("answer", "Jawaban ringkas"), ("solution", "Solusi"),
            ])
            plan = {
                "jenis": entry["classification"], "id": entry["id"], "judul": entry["title"],
                "konteks": entry["context_id"], "jenis_native": entry["kind"],
                "sumber_anchor": entry["source_anchor"], "sumber_locator": entry["source_locator"],
                "hak_komponen": entry["component_rights"], "tahap": entry["stage_urls"],
                "identitas_byte": entry["stage_facts"], "pelajar": SITE_URL + "latihan.html#" + entry["id"],
            }
            heading = E(entry["title"])
            if teacher:
                heading = f'<label><input class="choose" type="checkbox" aria-label="Pilih {E(entry["title"])}"> {heading}</label>'
            provenance = E(json.dumps({"source_locator": entry["source_locator"], "stage_facts": entry["stage_facts"]}, ensure_ascii=False, indent=2))
            plan_attr = f' data-plan="{E(json.dumps(plan,ensure_ascii=False,separators=(",",":")))}"' if teacher else ''
            result.append(f'<article class="entry" id="{E(entry["id"])}" data-context="{E(entry["context_id"])}" data-kind="{E(entry["classification"])}"{plan_attr}><p class="muted">{E(context_label)} · <span class="badge">{E(entry["classification"])}</span> <span class="badge">{E(entry["kind"])}</span></p><h3>{heading}</h3><p class="stages">{stages}</p><p><code>{E(entry["id"])}</code>{" · anchor sumber <code>"+E(entry["source_anchor"])+"</code>" if entry["source_anchor"] else ""}</p><details><summary>Identitas byte dan lokasi sumber</summary><pre>{provenance}</pre><p>Metadata native lengkap tetap tersedia di <a href="learning-map.json">data integrasi</a>.</p></details></article>')
        return ''.join(result)

    chapter_rows = []
    for chapter in model["chapters"]:
        chapter_rows.append(f'<article id="chapter-{chapter["sequence"]:02d}"><p class="muted">Bab {chapter["sequence"]} · {chapter["entry_count"]} rekaman bertahap</p><h2>{E(chapter["source_title"])}</h2><p class="links">{A(chapter["source_url"],"Buka bab sumber")}{A(chapter["companion_url"],"Buka pendamping mandiri")}{A("latihan.html?context=chapter_"+f"{chapter['sequence']:02d}","Lihat dukungan dan penguasaan")}</p><details><summary>Identitas sumber</summary><pre>{E(json.dumps({"source":chapter["source_file"],"companion":chapter["companion_file"],"component_manifest":chapter["component_manifest"]},ensure_ascii=False,indent=2))}</pre></details></article>')
    completion_rows = ''.join(f'<article id="{E(module["module_id"])}"><p class="muted">Modul penyempurnaan · {len(module["entry_ids"])} latihan penguasaan</p><h2>{E(module["title"])}</h2><p>{A(module["reader_url"],"Buka modul")}{" · " + A("latihan.html?context="+module["module_id"],"Buka latihan bertahap")}</p><p>Status native: <code>{E(module["status"])}</code></p></article>' for module in model["completion_modules"])
    intro = f'<p>Jalur C90 menghubungkan buku topologi berbasis inkuiri dengan dukungan mandiri tanpa meratakan format native. Ada {model["counts"]["chapters"]} bab, {model["counts"]["chapter_companions"]} pendamping, {model["counts"]["completion_modules"]} modul penyempurnaan, dan {model["counts"]["staged_records"]} rekaman yang masing-masing memiliki pernyataan, petunjuk, jawaban ringkas, dan solusi.</p><p class="warning">Jumlah 1.227 adalah rekaman dukungan/penguasaan kanonik, bukan jumlah soal mentah buku. Sumber memiliki 252 wadah latihan dan 1.142 tugas; angka tersebut tidak boleh dipertukarkan.</p>'
    put(DOCS / "C90.html", shell("C90 · Topologi", intro + '<h2>Bab dan pendamping</h2>' + ''.join(chapter_rows) + '<h2>Modul penyempurnaan</h2>' + completion_rows))
    put(DOCS / "latihan.html", shell("C90 · Latihan bertahap", '<p>Semua 1.227 identitas kanonik ditampilkan. Setiap tautan menuju byte HTML native yang sudah diindeks; pernyataan, petunjuk, jawaban, dan solusi tetap terpisah.</p>' + filters() + entry_rows()))
    planner = '<h2>Susun paket pertemuan</h2><p>Pilih rekaman yang akan dipakai. Ekspor mempertahankan konteks, identitas, lokasi sumber, hak komponen, empat tujuan tahap, dan identitas byte. Ini alat penyusunan; bukan klaim bahwa urutan dipelajari atau dinilai manusia.</p><button id="make-plan" type="button">Susun JSON</button><button id="clear-plan" type="button">Bersihkan pilihan</button><label for="plan">Paket kegiatan untuk disalin</label><textarea id="plan" readonly></textarea><p id="plan-status" role="status" aria-live="polite"></p>'
    put(DOCS / "pengajar.html", shell("C90 · Alat pengajar", planner + filters() + entry_rows(True)))

    term_rows = ''.join(f'<article class="entry" id="{E(term["id"])}" data-kind="{E(term["native"].get("status"))}"><h2>{E(term["native"].get("id_ID"))}</h2><p lang="en">{E(term["native"].get("en"))}</p><p>Status: <code>{E(term["native"].get("status"))}</code> · {E(term["native"].get("note"))}</p><code>{E(term["id"])}</code></article>' for term in model["terms"])
    put(DOCS / "istilah.html", shell("C90 · Register istilah", '<p>299 keputusan istilah dipertahankan: 298 disetujui dan satu provisional. Status provisional bukan persetujuan diam-diam.</p>' + filters(False, False) + term_rows))

    correction_rows = ''.join(f'<article class="entry" id="{E(item["id"])}" data-kind="{E(item["native"].get("status"))}"><h2><code>{E(item["id"])}</code></h2><p><span class="badge">{E(item["native"].get("status"))}</span> {E(item["native"].get("target_action"))}</p><details><summary>Rekaman koreksi asli</summary><pre>{E(json.dumps(item["native"],ensure_ascii=False,indent=2))}</pre></details></article>' for item in model["corrections"])
    rights = '<ul><li>Spine terjemahan: CC BY-NC-SA 3.0 (penetapan konservatif).</li><li>Pendamping, penyempurnaan, dan laboratorium asli: CC BY 4.0.</li><li>Komponen lain: ikuti pemberitahuan komponennya; tidak ada lisensi blanket baru.</li></ul>'
    put(DOCS / "catatan.html", shell("C90 · Koreksi, hak, dan aksesibilitas", f'<p>272 rekaman koreksi: 268 terverifikasi, dua belum terselesaikan, dan dua sudah digantikan. Ini bukan klaim bahwa 272 kesalahan masih ada.</p>{rights}<p>HTML primer diperiksa tanpa xref yang hilang, tanpa alt gambar yang hilang atau kosong, dan tanpa iframe tanpa nama. PDF tidak bertag.</p>' + filters(False, False) + correction_rows))
    put(DOCS / "learning-map.json", model)
    outputs[(DOCS / "topology.js").as_posix()] = (ROOT / "scripts/topology-capability-controls-v1.js").read_bytes()

    dependencies = [fact(BASE / "input/source-lock.json", (ROOT / BASE / "input/source-lock.json").read_bytes())]
    dependencies += [fact(BASE / "input" / item["path"], (ROOT / BASE / "input" / item["path"]).read_bytes()) for item in source["lock"]["native_files"]]
    dependencies.append(fact(BASE / "input/reader-destination-index.json", (ROOT / BASE / "input/reader-destination-index.json").read_bytes()))
    for path in ["scripts/topology_capability_v1.py", "scripts/build-topology-capability-v1.py", "scripts/topology-capability-controls-v1.js", "scripts/test-topology-controls-v1.mjs", "scripts/validate-topology-capability-v1.py", "schemas/course-capsule-v1/topology-learning-capability-v1.schema.json"]:
        dependencies.append(fact(path, (ROOT / path).read_bytes()))
    manifest = {
        "contract": model["contract"], "roles": ["C90"], "inputs": dependencies,
        "outputs": [fact(path, data) for path, data in outputs.items()], "counts": model["counts"],
        "projection_policy": model["projection_policy"], "limitations": model["limitations"],
        "reader_preserved": True, "publication_state": "not_yet_verified",
        "full_native_roundtrip_claimed": False,
    }
    put(BASE / "manifest.json", manifest)
    for relative, data in outputs.items():
        destination = Path(output_root) / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = build(args.output_root)
    print(json.dumps({"state": "built_not_validated", "counts": result["counts"]}, ensure_ascii=False))
