"""Build a bilingual, source-bound OpenLogic exercise-reference planner.

No PDF generation, book translation, network access or producer writes.
The frozen mapping verification is a separate source/PDF replay.
"""
import argparse
from collections import Counter
import hashlib
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'backend/course-capsule-v1/adapters/openlogic-teacher-v1'
RELEASE = 'https://github.com/KokunoYumeto/OpenLogic-id/releases/tag/id-olp-0722-20260814'
PUBLIC = 'https://kokunoyumeto.github.io/program-matematika-indonesia/'
INPUTS = {
    'source-problems.json': {'bytes':1312777,'sha256':'655d56f4ea8535e4424902b693fcc393e7e0bdcb4a245835f63bd5ae761e4199'},
    'main-exercises.json': {'bytes':909122,'sha256':'f9e58e8f649f4fedc240a21719b55efdce535592d073d65a8aaa1996c47bab16'},
    'supplement-exercises.json': {'bytes':75441,'sha256':'f407ae05368e54393c409d3baff7f03addf1e2ecaba589f2a74bd6d266f66c9a'},
    'section-titles.json': {'bytes':27862,'sha256':'0a124fa712c79b3d251d4582436d68eb027d756907152fbf7fffa1370ef767cf'},
}
TOPICS = {
 'sets-functions-relations': ('Himpunan, fungsi, dan relasi','Sets, functions and relations'),
 'set-theory': ('Teori himpunan','Set theory'),
 'propositional-logic': ('Logika proposisional','Propositional logic'),
 'first-order-logic': ('Logika orde pertama','First-order logic'),
 'second-order-logic': ('Logika orde kedua','Second-order logic'),
 'normal-modal-logic': ('Logika modal normal','Normal modal logic'),
 'applied-modal-logic': ('Logika modal terapan','Applied modal logic'),
 'intuitionistic-logic': ('Logika intuisionistik','Intuitionistic logic'),
 'many-valued-logic': ('Logika bernilai banyak','Many-valued logic'),
 'counterfactuals': ('Kontrafaktual','Counterfactuals'),
 'computability': ('Komputabilitas','Computability'),
 'turing-machines': ('Mesin Turing','Turing machines'),
 'incompleteness': ('Ketaklengkapan','Incompleteness'),
 'lambda-calculus': ('Kalkulus lambda','Lambda calculus'),
 'model-theory': ('Teori model','Model theory'),
 'proof-theory': ('Teori bukti','Proof theory'),
 'methods': ('Metode','Methods'),
}


def encoded(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()


def fact(data):
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def load(base=BASE):
    data={}
    for name,identity in INPUTS.items():
        body=(base/name).read_bytes()
        assert fact(body)==identity,('Mapping input drift',name)
        data[name]=json.loads(body)
    tests=json.loads((base/'mapping-tests.json').read_bytes())
    assert tests['state']=='pass' and tests['identical_replays']==2
    assert tests['maps']=={'main':INPUTS['main-exercises.json'],'supplement':INPUTS['supplement-exercises.json']}
    return data


def project(data):
    native=data['source-problems.json'];main=data['main-exercises.json'];supp=data['supplement-exercises.json']
    titles=data['section-titles.json']
    assert titles['state']=='pass' and titles['main_map']==INPUTS['main-exercises.json']
    assert titles['reader']==main['pdf'] and titles['covered_occurrences']==411
    assert titles['section_count']==len(titles['sections'])==220
    assert native['course_id']=='C80' and len(native['problems'])==438
    assert main['state']==supp['state']=='pass'
    assert main['source_inventory']==supp['source_inventory']==INPUTS['source-problems.json']
    problems={p['id']:p for p in native['problems']}
    assert len(problems)==438
    units={u['native_unit_id']:u for u in native['units']}
    questions=[]
    for component,mapping in [('main',main),('supplement',supp)]:
        for row in mapping['exercises']:
            p=problems[row['source_problem_id']];u=units[p['native_unit_id']]
            for key in ['native_unit_id','source_path','target_path','source','target']:
                assert row[key]==p[key],('Source association drift',row['source_problem_id'],key)
            assert row['source_file']==u['source'] and row['target_file']==u['target']
            assert (component=='main')==p['in_frozen_main_reader']
            page=row['combined_page']
            assert isinstance(page,int) and (1<=page<=1116 if component=='main' else 1117<=page<=1255)
            assert row['combined_href']==main['pdf']['url']+'#page='+str(page)
            ident=row['occurrence_id'] if component=='main' else p['id']+':supplement'
            topic=p['source_path'].split('/')[1];assert topic in TOPICS
            section_title=None
            if component=='main':
                section=titles['sections'][row['canonical_section_value'][3]]
                assert section['physical_page']<=page
                section_title=section['title']
                assert section_title and not any(c in section_title for c in ['\\','{','}','$'])
            questions.append({'id':ident,'source_problem_id':p['id'],'unit_id':p['native_unit_id'],
                'component':component,'chapter':component+':'+row['printed_number'].split('.')[0],
                'topic':topic,'number':row['printed_number'],'physical_page':page,
                'reader_url':row['combined_href'],'local_reader_url':'reader.pdf#page='+str(page),
                'reader_language':'id','solution_state':'not_audited',
                'section_title_id':section_title,
                'mapping':row})
    assert len(questions)==442 and len({q['id'] for q in questions})==442
    assert Counter(q['component'] for q in questions)=={'main':411,'supplement':31}
    printed={q['source_problem_id'] for q in questions};assert len(printed)==427
    counts=Counter(q['source_problem_id'] for q in questions)
    for q in questions:q['source_reuse_count']=counts[q['source_problem_id']]
    assert sum(n-1 for n in counts.values())==15
    disabled=set(main['tag_disabled_source_problems'])
    findings={r['source_problem_id']:r for r in main['source_only_findings']}
    assert len(disabled)==10 and len(findings)==1 and not disabled&findings.keys()
    assert printed.isdisjoint(disabled|findings.keys()) and printed|disabled|findings.keys()==problems.keys()
    retained=[]
    for key in sorted(disabled|findings.keys()):
        p=problems[key]
        retained.append({'id':key,'reason':'edition_tag_disabled' if key in disabled else 'missing_deferred_flush',
            'source_path':p['source_path'],'target_path':p['target_path'],
            'source':p['source'],'target':p['target'],'unit_id':p['native_unit_id'],
            'reader_url':None,'finding':findings.get(key)})
    model={'schema':'openlogic-teacher-selection/1','course_id':'C80','input_identities':INPUTS,
        'reader':{**main['pdf'],'pages':1255,'language':'id','local_filename':'reader.pdf'},
        'release_url':RELEASE,'questions':questions,'source_only':retained,
        'counts':{'source_problems':438,'printed_occurrences':442,'rendered_source_problems':427,
                  'main_occurrences':411,'supplement_occurrences':31,'additional_reused_occurrences':15,
                  'tag_disabled':10,'missing_deferred_flush':1},
        'topics':{key:{'id':value[0],'en':value[1]} for key,value in TOPICS.items()},
        'provenance':{'model':'gpt-6-astra','effort':'ultra','scope':'reference planner and structural exercise mapping; no new book translation'},
        'limitations':{
            'id':'Perencana ini memilih rujukan, bukan menyalin soal. Kedua antarmuka merujuk pada buku Bahasa Indonesia yang sama. Halaman yang ditampilkan adalah nomor halaman fisik PDF, bukan nomor halaman tercetak. Satu soal sumber dapat muncul di dua konteks pembaca; setiap kemunculan memiliki identitas tersendiri. Jawaban, petunjuk, dan penyelesaian belum diaudit. Pemetaan struktural ini bukan penilaian ulang mutu terjemahan atau kebenaran bukti.',
            'en':'This planner selects references, not copied exercises. Both interfaces point to the same Indonesian book. Page numbers are physical PDF pages, not printed page labels. A source exercise can appear in two reader contexts; each occurrence has its own identity. Answers, hints and solutions have not been audited. This structural mapping is not a renewed translation-quality or mathematical-proof review.'}}
    model['edition_binding']=hashlib.sha256(encoded({'inputs':INPUTS,'reader':model['reader']})).hexdigest()
    return model


def render(model,lang):
    en=lang=='en'
    w=({'title':'OpenLogic assignment planner','main':'Main reader','supplement':'Supplement',
        'exercise':'Exercise','chapter':'Chapter','page':'PDF page','topic':'Topic','all':'All',
        'search':'Search number, section title or source identifier','select':'Select displayed exercises',
        'clear':'Clear selection','export':'Export assignment','import':'Import assignment','print':'Print references',
        'chosen':'Show selected only','reuse':'Show reused source exercises only','local':'Use local reader.pdf links',
        'choose':'Select','details':'Source identity and mapping evidence','data':'Exercise data',
        'sourceonly':'Source exercises absent from this PDF','disabled':'Disabled by edition tags',
        'unflushed':'Missing from PDF: deferred exercise printing was not triggered',
        'static':'All printable exercise references (also works without JavaScript)',
        'read':'Open this exercise','notaudited':'Answers, hints and solutions: not audited'} if en else {
        'title':'Perencana tugas OpenLogic','main':'Buku utama','supplement':'Suplemen',
        'exercise':'Soal','chapter':'Bab','page':'Halaman PDF','topic':'Topik','all':'Semua',
        'search':'Cari nomor, judul bagian, atau identitas sumber','select':'Pilih soal yang ditampilkan',
        'clear':'Hapus pilihan','export':'Ekspor tugas','import':'Impor tugas','print':'Cetak rujukan',
        'chosen':'Tampilkan pilihan saja','reuse':'Hanya soal sumber yang digunakan ulang','local':'Gunakan tautan reader.pdf lokal',
        'choose':'Pilih','details':'Identitas sumber dan bukti pemetaan','data':'Data soal',
        'sourceonly':'Soal sumber yang tidak muncul dalam PDF ini','disabled':'Dinonaktifkan oleh tag edisi',
        'unflushed':'Tidak muncul dalam PDF: pencetakan soal tertunda tidak dipicu',
        'static':'Semua rujukan soal tercetak (juga dapat dipakai tanpa JavaScript)',
        'read':'Buka soal ini','notaudited':'Jawaban, petunjuk, dan penyelesaian: belum diaudit'})
    esc=lambda x:escape(str(x),quote=True)
    topic_options=''.join(f'<option value="{key}">{esc(value[lang])}</option>' for key,value in model['topics'].items())
    chapters=list(dict.fromkeys(q['chapter'] for q in model['questions']))
    chapter_options=''.join(f'<option value="{key}">{w[key.split(":")[0]]} · {w["chapter"]} {key.split(":")[1]}</option>' for key in chapters)
    static=''.join(f'<tr><td>{w[q["component"]]}</td><td><a href="{esc(q["reader_url"])}">{w["exercise"]} {q["number"]}</a></td><td>{q["physical_page"]}</td><td>{esc(model["topics"][q["topic"]][lang])}<br><code>{esc(q["id"])}</code></td></tr>' for q in model['questions'])
    absent=''.join(f'<li><strong>{w["disabled" if q["reason"]=="edition_tag_disabled" else "unflushed"]}</strong><br><code>{esc(q["id"])}<br>{esc(q["target_path"])}</code> · {"lines" if en else "baris"} {q["target"]["start_line"]}–{q["target"]["end_line"]}</li>' for q in model['source_only'])
    payload=encoded({'model':model,'locale':lang,'words':w}).decode().replace('<','\\u003c').replace('&','\\u0026')
    offline=('Download the linked combined PDF and save it as reader.pdf beside this page. Enable local links below. Selection, filtering and JSON exchange work offline; online books and program links require a connection. The planner does not bundle book bodies.' if en else
             'Unduh PDF gabungan melalui tautan di bawah, lalu simpan sebagai reader.pdf di samping halaman ini. Aktifkan tautan lokal. Pemilihan, penyaringan, dan pertukaran JSON dapat digunakan luring; buku daring dan tautan program memerlukan koneksi. Paket perencana tidak memuat isi buku.')
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>C80 · {w['title']}</title><link rel="stylesheet" href="teacher.css"></head><body>
<a class="skip" href="#main">{'Skip to exercises' if en else 'Langsung ke soal'}</a>
<header><nav aria-label="{'Program navigation' if en else 'Navigasi program'}"><a href="{PUBLIC}{lang}/">Program</a><a href="{PUBLIC}backend/openlogic/C80.html">{'OpenLogic reader and sources' if en else 'Buku dan sumber OpenLogic'}</a></nav>
<nav aria-label="{'Language' if en else 'Bahasa'}"><a href="C80.teacher.html" lang="id" {'aria-current="page"' if not en else ''}>Bahasa Indonesia</a><a href="C80.teacher.en.html" lang="en" {'aria-current="page"' if en else ''}>English</a></nav>
<p class="eyebrow">C80 · Open Logic Project · Bahasa Indonesia</p><h1>{w['title']}</h1>
<p class="lead">{'Choose exercises, save an assignment and reopen the same references later.' if en else 'Pilih soal, simpan tugas, dan buka kembali rujukan yang sama.'}</p>
<p class="counts">442 {'printed occurrences' if en else 'kemunculan tercetak'} · 427 {'distinct source exercises' if en else 'soal sumber berbeda'} · 11 {'source-only exercises' if en else 'soal hanya dalam sumber'}</p>
<p>{esc(model['limitations'][lang])}</p><p><a href="C80.teacher.json">{w['data']}</a> · <a href="openlogic-teacher-editable-source-v1.zip">{'Complete editable planner source' if en else 'Sumber lengkap perencana yang dapat disunting'}</a></p>
<details><summary>{'Offline use and book downloads' if en else 'Pemakaian luring dan unduhan buku'}</summary><p>{offline}</p><p><a href="{esc(model['reader']['url'])}">{'Combined reader PDF' if en else 'PDF buku gabungan'} · 1,255 {'pages' if en else 'halaman'}</a> · <a href="{RELEASE}">{'All book sources and release files' if en else 'Seluruh sumber buku dan berkas rilis'}</a></p><p>SHA-256: <code>{model['reader']['sha256']}</code></p></details></header>
<main id="main"><section class="controls" aria-label="{'Assignment selection' if en else 'Pemilihan tugas'}">
<label>{w['topic']}<select id="topic"><option value="">{w['all']}</option>{topic_options}</select></label>
<label>{w['chapter']}<select id="chapter"><option value="">{w['all']}</option>{chapter_options}</select></label>
<label>{w['search']}<input type="search" id="search"></label>
<label class="inline"><input type="checkbox" id="selected-only">{w['chosen']}</label><label class="inline"><input type="checkbox" id="reused-only">{w['reuse']}</label><label class="inline"><input type="checkbox" id="local-reader">{w['local']}</label>
<div class="actions"><button id="select-visible">{w['select']}</button><button id="clear">{w['clear']}</button><button id="export">{w['export']}</button><label class="import">{w['import']}<input type="file" id="import" accept="application/json,.json"></label><button id="print">{w['print']}</button></div></section>
<details id="exchange"><summary>{'Assignment JSON: copy, download or paste' if en else 'JSON tugas: salin, unduh, atau tempel'}</summary><p>{'Export fills this box. Copy its text or use the download link. To restore a saved assignment, paste its JSON and apply it.' if en else 'Ekspor mengisi kotak ini. Salin teksnya atau gunakan tautan unduh. Untuk memulihkan tugas tersimpan, tempel JSON-nya lalu terapkan.'}</p><label>{'Assignment JSON' if en else 'JSON tugas'}<textarea id="packet" rows="7" spellcheck="false"></textarea></label><button id="apply-packet">{'Apply pasted assignment' if en else 'Terapkan tugas yang ditempel'}</button> <a id="download" hidden>{'Download assignment JSON' if en else 'Unduh JSON tugas'}</a></details>
<noscript><p>{'Selection requires JavaScript; the complete readable reference table below remains available.' if en else 'Pemilihan memerlukan JavaScript; tabel rujukan lengkap di bawah tetap dapat dibaca.'}</p></noscript>
<p id="status" role="status" aria-live="polite"></p><p id="error" role="alert"></p><div id="exercises"></div>
<details id="all-references"><summary>{w['static']}</summary><div class="table-scroll"><table><caption>{'442 references into the Indonesian reader' if en else '442 rujukan ke buku Bahasa Indonesia'}</caption><thead><tr><th>{'Part' if en else 'Bagian'}</th><th>{w['exercise']}</th><th>{w['page']}</th><th>{w['topic']} / {'identity' if en else 'identitas'}</th></tr></thead><tbody>{static}</tbody></table></div></details>
<section id="source-only"><h2>{w['sourceonly']}</h2><p>{'These 11 source exercises have no verified location in the current PDF. They cannot be selected as printed exercises. The source paths and line ranges below remain available through the book source release.' if en else 'Sebelas soal sumber ini tidak memiliki lokasi terverifikasi dalam PDF saat ini. Soal-soal ini tidak dapat dipilih sebagai soal tercetak. Jalur sumber dan rentang baris di bawah tetap tersedia melalui rilis sumber buku.'}</p><ul>{absent}</ul></section></main>
<footer><p>{'Book: Open Logic Project; Indonesian edition in its existing release lineage, CC BY 4.0. The book source and licence remain with the release linked above.' if en else 'Buku: Open Logic Project; edisi Bahasa Indonesia pada jalur rilis yang sudah ada, CC BY 4.0. Sumber dan lisensi buku tetap tersedia pada rilis yang ditautkan di atas.'}</p>
<p>{'Planner and mapping integration: OpenAI Codex — gpt-6-astra, Ultra effort. No new book translation or human review is claimed. The planner makes no background requests and uses no analytics or persistent storage. Export a file to keep your selection.' if en else 'Integrasi perencana dan pemetaan: OpenAI Codex — gpt-6-astra, tingkat upaya Ultra. Tidak ada klaim terjemahan buku baru atau peninjauan manusia. Perencana tidak membuat permintaan latar belakang dan tidak memakai analitik atau penyimpanan persisten. Ekspor berkas untuk menyimpan pilihan Anda.'}</p></footer>
<script id="planner-data" type="application/json">{payload}</script><script src="teacher.js"></script></body></html>'''


def build(output,base=BASE):
    model=project(load(base))
    files={'C80.teacher.json':encoded(model)}
    for lang in ['id','en']:
        files['C80.teacher'+('.en' if lang=='en' else '')+'.html']=render(model,lang).encode()
    for name in ['teacher.js','teacher.css']:files[name]=(base/'ui'/name).read_bytes()
    output.mkdir(parents=True,exist_ok=True)
    for name,body in files.items():(output/name).write_bytes(body)
    receipt={'schema':'openlogic-teacher-build/1','state':'built-not-admitted','counts':model['counts'],
        'edition_binding':model['edition_binding'],'input_identities':INPUTS,
        'files':[{'path':name,**fact(body)} for name,body in sorted(files.items())]}
    (output/'teacher-build.json').write_bytes(encoded(receipt))
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=BASE/'site')
    print(json.dumps(build(p.parse_args().output)))
