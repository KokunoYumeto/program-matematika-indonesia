"""Build the C100 learner, concept, terminology, description and teaching views."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from geometry_capability_v1 import ROOT, BASE, PILOT, READER, READER_STYLE, SOLUTION_PDF, SITE_URL, build_model, read_inputs, encoded, fact

E = lambda text: html.escape(str(text if text is not None else ''), quote=True)
A = lambda url, label: f'<a href="{E(url)}">{E(label)}</a>'
STATES = {'admitted': 'Diperiksa dalam sumber', 'mapped-admitted': 'Pemetaan diperiksa dalam sumber',
          'mapped-pending-qa': 'Pemetaan sumber belum selesai diperiksa',
          'source-disabled-preserved': 'Metadata gambar nonaktif dipertahankan'}
CSS = '''*{box-sizing:border-box}:root{color-scheme:light;--ink:#183a35;--paper:#f5f5ed;--edge:#c8d7d1;--accent:#07665f}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:28px 24px 60px}a{color:var(--accent);text-underline-offset:3px}nav,.links{display:flex;gap:18px;flex-wrap:wrap}h1{font-size:clamp(1.9rem,4vw,3rem);line-height:1.15}h2{margin-top:36px}p{max-width:85ch}small,.muted{color:#476568}.skip{position:absolute;left:-9999px}.skip:focus{left:16px;top:8px;background:white;padding:8px}:focus-visible{outline:3px solid #c77e21;outline-offset:3px}.filters{display:flex;gap:18px;flex-wrap:wrap;border-block:1px solid var(--edge);padding:18px 0}label{display:block}input,select,textarea,button{font:inherit;padding:8px;max-width:100%}textarea{width:100%;min-height:240px}article{padding:16px 0;border-bottom:1px solid var(--edge)}article h3{margin:0}details{margin:14px 0}footer{margin-top:40px;border-top:1px solid var(--edge)}code{overflow-wrap:anywhere}[hidden]{display:none!important}@media print{nav,.filters,button,.skip{display:none}main{padding:0}body{background:white;font-size:10pt}article{break-inside:avoid}}'''


def build(output_root=ROOT):
    source = read_inputs()
    model = build_model(source)
    concepts = {c['id']: c for c in model['concepts']}
    terms = {t['id']: t for t in model['terms']}
    units = {u['stable_unit_id']: u for u in source['units']}
    outputs = {}
    def put(path, value):
        outputs[path] = value.encode('utf-8') if isinstance(value, str) else encoded(value)
    nav = ''.join(A(file, label) for file, label in [('C100.html', 'Bacaan & latihan'), ('konsep.html', 'Konsep & prasyarat'),
                    ('istilah.html', 'Istilah'), ('gambar.html', 'Deskripsi gambar'), ('pengajar.html', 'Untuk pengajar')])
    def shell(title, body):
        return f'''<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} — Program matematika</title><meta name="description" content="Geometri: bacaan, latihan, konsep, istilah, deskripsi gambar dan rencana pengajaran dengan identitas sumber."><style>{CSS}</style></head><body><a class="skip" href="#main">Lewati ke isi</a><main id="main"><nav>{A('../../id/','Program matematika')}{A('../index.html','Pusat belajar')}</nav><nav aria-label="Alat geometri">{nav}</nav><h1>{E(title)}</h1>{body}<footer><p>Halaman ini memakai metadata asli buku <em>Bidang Euklides dan Kerabatnya</em>. Pembaca utama dan solusi tetap pada edisi yang sama. Pilihan rencana hanya tersimpan pada halaman ini; tidak ada data pelajar yang dikirim.</p><details><summary>Provenans, sumber, dan batas pemeriksaan</summary><p>Edisi sumber: <code>{E(model['native_edition']['id'])}</code>. Identitas, status, dan catatan asli dipertahankan. Pemetaan konsep bukan pengujian kemampuan pelajar. Sebagian pemetaan masih menunggu QA sumber; tautan tetap tersedia dengan statusnya. Tidak ada klaim baru tentang tata letak PDF atau sertifikasi aksesibilitas. Halaman navigasi dapat disimpan luring; unduh bacaan dan PDF secara terpisah.</p><p>{A('catatan.html','Koreksi dan hak komponen')} · {A('learning-map.json','Data integrasi')} · {A('validation.json','Hasil pemeriksaan')} · {A('https://github.com/KokunoYumeto/bidang-euklides-dan-kerabatnya-id','Repositori buku')}</p></details></footer></main><script src="geometry.js"></script></body></html>\n'''
    def filters(chapters=False, kinds=False):
        chapter = '<label>Bab <select id="chapter"><option value="">Semua</option>' + ''.join(f'<option value="{n:02d}">{n}</option>' for n in range(1,21)) + '</select></label>' if chapters else ''
        kind = '<label>Jenis <select id="kind"><option value="">Semua</option><option value="concept">Konsep</option><option value="exercise">Latihan</option></select></label>' if kinds else ''
        return f'<div class="filters"><label>Cari judul, istilah, atau identitas <input id="query" type="search"></label>{chapter}{kind}</div><p id="count" role="status" aria-live="polite"></p>'
    def concept_rows(teacher=False):
        rows = []
        for c in model['concepts']:
            n = c['native']
            chapter = c['source_file'].split('ch')[1][:2]
            prereqs = [A('konsep.html#' + p['id'], concepts[p['id']]['native']['preferred_id_ID']) if p['resolved'] else E(p['id']) + ' (belum dipetakan)' for p in c['prerequisites']]
            precision = 'Lokasi unit sumber persis.' if c['reading_state'] == 'exact_native_unit' else 'Tautan menuju bab induk, bukan lokasi persis konsep; segmen asli tetap dicatat.'
            lexical = ' · '.join(A('istilah.html#'+tid, terms[tid]['native']['preferred_id_ID']+' — '+terms[tid]['native']['scope']) for tid in c['lexical_term_matches'])
            plan = {'jenis': 'konsep', 'id': c['id'], 'judul': n['preferred_id_ID'], 'status_sumber': n['status'],
                    'bacaan': c['reading'], 'ketepatan_lokasi': c['reading_state'], 'unit_sumber': n['first_unit_id'],
                    'prasyarat': [p['id'] for p in c['prerequisites']], 'pelajar': SITE_URL+'konsep.html#'+c['id']}
            choice = f'<label><input type="checkbox" class="choose" aria-label="Pilih {E(n["preferred_id_ID"])}"> {E(n["preferred_id_ID"])}</label>' if teacher else E(n['preferred_id_ID'])
            rows.append(f'<article id="{E(c["id"])}" class="entry" data-kind="concept" data-chapter="{chapter}" data-plan="{E(json.dumps(plan,ensure_ascii=False))}"><h3>{choice}</h3><p><span lang="en">{E(n["source_term"])}</span> · {E(STATES.get(n["status"],n["status"]))}</p><p>Prasyarat metadata: {" · ".join(prereqs) or "Tidak ada yang dicatat."}</p><p>{A(c["reading"],"Buka bacaan") if c["reading"] else "Lokasi bacaan belum dipetakan."} {E(precision)}</p>' + (f'<p>Padanan leksikal dalam register (bukan kesamaan identitas): {lexical}</p>' if lexical else '') + f'<details><summary>Identitas sumber</summary><p><code>{E(c["id"])}</code> · <code>{E(n["first_unit_id"])}</code> · <code>{E(c["source_file"])}</code></p></details></article>')
        return ''.join(rows)
    def exercise_rows(teacher=False):
        rows = []
        for e in model['exercises']:
            u = e['unit']
            support_links = []
            for s in e['support']:
                label = 'Petunjuk sumber' if s['kind']=='hint' else 'Solusi tambahan mandiri — PDF lengkap'
                support_links.append(A(s['unit']['learner_route']['url'],label))
            parent_links = [A('C100.html#'+p,'Soal induk dan dukungannya') for p in e['parents']]
            descriptor = 'Bagian soal' if e['parents'] else 'Soal induk'
            if 'advanced' in u['native_unit_kind']:
                descriptor += ' · lanjutan menurut sumber'
            if 'classroom' in u['native_unit_kind']:
                descriptor += ' · kegiatan kelas menurut sumber'
            plan = {'jenis':'latihan','id':e['id'],'judul':u['title'],'jenis_sumber':u['native_unit_kind'],
                    'bacaan':u['learner_route']['url'],'pelajar':e['learner_url'],
                    'sumber':{'path':u['source_path'],'sha256':u['source_sha256']},
                    'terjemahan':{'path':u['target_path'],'sha256':u['target_sha256']},
                    'soal_induk':e['parents'], 'dukungan':[{'id':s['unit']['stable_unit_id'],'jenis':s['kind'],'url':s['unit']['learner_route']['url']} for s in e['support']],
                    'batas_solusi':'PDF lengkap, bukan halaman solusi tertentu; solusi ditulis terpisah dari buku sumber.'}
            choice = f'<label><input type="checkbox" class="choose" aria-label="Pilih {E(u["title"])}"> {E(u["title"])}</label>' if teacher else E(u['title'])
            rows.append(f'<article id="{E(e["id"])}" class="entry" data-kind="exercise" data-chapter="{E(e["chapter"])}" data-plan="{E(json.dumps(plan,ensure_ascii=False))}"><p class="muted">Bab {int(e["chapter"])} · {E(descriptor)}</p><h3>{choice}</h3><p>{A(u["learner_route"]["url"],"Buka soal dalam pembaca")}</p><p>{" · ".join(support_links) or "Tidak ada dukungan langsung yang dicatat untuk unit ini."}</p><p>{" · ".join(parent_links)}</p><details><summary>Identitas dan batas dukungan</summary><p><code>{E(e["id"])}</code>. {E(u["native_unit_kind"])}</p><p>Solusi tambahan ditulis secara mandiri, bukan oleh penulis buku sumber. Tujuannya PDF lengkap, bukan halaman solusi tertentu. Bagian soal dapat memakai dukungan pada soal induk.</p></details></article>')
        return ''.join(rows)
    chapters = '<ol>'+''.join('<li>'+A(c['learner_route']['url'],c['title'])+'</li>' for c in model['chapters'])+'</ol>'
    put('docs/backend/geometry/C100.html',shell('C100 · Geometri: bacaan dan latihan',
        '<p>Gunakan pembaca buku yang sudah tersedia, lalu temukan soal dan dukungannya. 285 permukaan latihan mencakup 253 soal induk dan 32 bagian soal; ini bukan 285 tugas independen.</p><details><summary>Buka 20 bab</summary>'+chapters+'</details>'+filters(True)+exercise_rows()))
    put('docs/backend/geometry/konsep.html',shell('C100 · Konsep dan prasyarat',
        '<p>491 konsep dengan 994 hubungan prasyarat dari metadata asli. 18 rekaman berstatus diperiksa, 125 pemetaan diperiksa, dan 348 pemetaan masih menunggu QA sumber. Tiga konsep memakai tautan bab induk yang ditandai secara eksplisit.</p>'+filters(True)+concept_rows()))
    planner = '<h2>Susun rencana kegiatan</h2><p>Pilih konsep dan latihan sesuai pertemuan. Pilihan tersembunyi oleh filter tetap disertakan. Rencana mempertahankan prasyarat, identitas dan batas lokasi; ini alat penyusunan kegiatan, bukan silabus atau asesmen yang telah divalidasi.</p><button id="make-plan" type="button">Susun rencana dari pilihan</button><button id="clear-plan" type="button">Bersihkan pilihan</button><label for="plan">Rencana untuk disalin</label><textarea id="plan" readonly></textarea><p id="plan-status" role="status" aria-live="polite"></p>'
    put('docs/backend/geometry/pengajar.html',shell('C100 · Rencana mengajar',planner+filters(True,True)+'<h2>Konsep untuk pertemuan</h2>'+concept_rows(True)+'<h2>Latihan untuk pertemuan</h2>'+exercise_rows(True)))
    term_rows = ''.join(f'<article class="entry" id="{E(t["id"])}"><h2>{E(t["native"]["preferred_id_ID"])}</h2><p lang="en">{E(t["native"]["source_term"])}</p><p>Alternatif, bentuk ditolak, atau catatan konteks sumber: {E(t["native"]["rejected_or_contextual"]) or "—"}</p><p>Cakupan: {E(t["native"]["scope"])} · {E(STATES.get(t["native"]["status"],t["native"]["status"]))}</p><code>{E(t["id"])}</code></article>' for t in model['terms'])
    put('docs/backend/geometry/istilah.html',shell('C100 · Istilah dan pilihan kontekstual','<p>432 rekaman istilah. Catatan alternatif mencampur bentuk yang ditolak dan bentuk yang hanya sesuai dalam konteks tertentu; semuanya tidak dianggap sinonim yang diterima. Rekaman yang tampak sama tetap terpisah menurut identitas dan cakupan.</p>'+filters()+term_rows))
    figure_rows = ''.join(f'<article class="entry" id="{E(f["id"])}"><h2>{E(f["native"]["short_description"])}</h2><p>{E(f["native"]["long_description"])}</p><p>{A(f["reading"],"Buka deskripsi dalam pembaca") if f["reading"] else "Gambar nonaktif pada sumber; metadata dipertahankan, tanpa tautan gambar aktif."}</p><details><summary>Identitas gambar dan sumber</summary><p><code>{E(f["id"])}</code> · <code>{E(f["native"]["source_locator"])}</code> · {E(f["native"]["status"])}</p></details></article>' for f in model['figures'])
    put('docs/backend/geometry/gambar.html',shell('C100 · Deskripsi gambar','<p>214 rekaman deskripsi, 213 dengan tujuan aktif dalam pembaca. Deskripsi membantu pembacaan nonvisual; halaman ini tidak mengklaim menggambar ulang atau memvalidasi semua ilustrasi.</p>'+filters()+figure_rows))
    correction_rows = ''.join(f'<article class="entry" id="{E(c["id"])}"><h2><code>{E(c["id"])}</code></h2><p>Status sumber: {E(c.get("status",""))}</p><details><summary>Catatan sumber lengkap</summary><pre lang="en">{E(json.dumps(c,ensure_ascii=False,indent=2))}</pre></details></article>' for c in model['corrections'])
    rights = '<ul>'+''.join('<li><code>'+E(r['id'])+'</code> · '+E(r.get('license','Status komponen terpisah'))+'</li>' for r in model['rights_accessibility']['rights']['components'])+'</ul>'
    put('docs/backend/geometry/catatan.html',shell('C100 · Catatan koreksi dan hak komponen','<p>207 rekaman asli, termasuk perubahan yang diterapkan, catatan sumber, contoh kesalahan yang disengaja, dan status historis. Daftar ini bukan 207 kesalahan yang belum diperbaiki. Hubungan ketergantungan catatan tidak diubah menjadi prasyarat pedagogis.</p>'+rights+filters()+correction_rows))
    put('docs/backend/geometry/learning-map.json',model)
    js = (ROOT/'scripts/geometry-capability-controls-v1.js').read_bytes()
    outputs['docs/backend/geometry/geometry.js'] = js
    dependencies = [fact(BASE/'input/source-lock.json',(ROOT/BASE/'input/source-lock.json').read_bytes())]
    dependencies += [fact(BASE/'input'/r['path'],(ROOT/BASE/'input'/r['path']).read_bytes()) for r in source['lock']['native_files']]
    dependencies += source['lock']['central_dependencies']
    dependencies += [fact(p,(ROOT/p).read_bytes()) for p in [READER_STYLE,SOLUTION_PDF]]
    for path in ['scripts/geometry_capability_v1.py','scripts/build-geometry-capability-v1.py','scripts/geometry-capability-controls-v1.js','scripts/test-geometry-controls-v1.mjs','scripts/validate-geometry-capability-v1.py','schemas/course-capsule-v1/geometry-learning-capability-v1.schema.json']:
        dependencies.append(fact(path,(ROOT/path).read_bytes()))
    manifest = {'contract':model['contract'],'roles':['C100'],'inputs':dependencies,
                'outputs':[fact(p,b) for p,b in outputs.items()], 'counts':model['counts'],
                'projection_policy':model['projection_policy'],'limitations':model['limitations'],
                'reader_preserved':True,'publication_state':'not_yet_verified','full_native_roundtrip_claimed':False}
    put(str(BASE/'manifest.json').replace('\\','/'),manifest)
    for path,data in outputs.items():
        destination=Path(output_root)/path
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(data)
    return manifest


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-root',type=Path,default=ROOT)
    args=parser.parse_args()
    result=build(args.output_root)
    print(json.dumps({'state':'built_not_validated','counts':result['counts']}))
