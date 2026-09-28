"""Build reference-based Judson assignment planners; never retranslate book bodies."""
import argparse
from collections import Counter
import hashlib
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'backend/course-capsule-v1/adapters/judson-teacher-v1'
COUNTS = {'C30':610,'C40':303}


def encoded(data):
    return (json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')


def fact(body):
    return {'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}


def unique(rows,key):
    result = {r[key]:r for r in rows}
    assert len(result)==len(rows), 'Duplicate '+key
    return result


def load(base=BASE):
    lock=json.loads((base/'input/source-lock.json').read_bytes())
    assert lock['path']=='native-exercise-intake.json'
    body=(base/'input'/lock['path']).read_bytes()
    assert fact(body)=={k:lock[k] for k in ['bytes','sha256']}, 'Input drift'
    return json.loads(body),lock


def project(native,lock):
    assert native['schema']=='judson-teacher-intake/1'
    assert native['status']=='native_mappings_verified' and native['unresolved_mappings']==0
    assert native['exact_identity_mappings']==913 and native['exercise_counts']==COUNTS
    assert native['book_prose_copied'] is False and native['new_translation'] is False
    assert native['support_availability_counts']=={'has_hint:provided_content':213,'has_response:empty_response_slot':116}
    chapters=unique(native['chapters'],'native_unit_id')
    exercises=unique(native['exercises'],'id')
    assert len(exercises)==913 and len(unique(native['exercises'],'native_id'))==913
    relations=set()
    courses=[]
    for role,count in COUNTS.items():
        selected=sorted([e for e in exercises.values() if e['course_id']==role],key=lambda e:e['preorder_index'])
        assert len(selected)==count
        questions=[]
        for e in selected:
            chapter=chapters[e['chapter_id']]
            assert chapter['course_id']==role
            assert e['source_xpath']==e['target_xpath']
            assert e['target_identifier']==e['reader_fragment']
            assert e['reader_mapping']=='hash_verified_native_xml_identity_matched_frozen_exercise_node'
            assert re.fullmatch(r'[a-zA-Z0-9_.-]+',e['reader_fragment'])
            assert e['reader_edition'] in ['web','sage']
            assert e['reader_targets'] and len({t['edition'] for t in e['reader_targets']})==len(e['reader_targets'])
            assert e['reader_edition'] in {t['edition'] for t in e['reader_targets']}
            assert e['reader_edition']==('web' if any(t['edition']=='web' for t in e['reader_targets']) else 'sage')
            targets=[]
            for t in e['reader_targets']:
                assert t['edition'] in ['web','sage']
                assert t['fragment']==e['reader_fragment']
                assert re.fullmatch(r'[a-zA-Z0-9_.-]+\.html',t['member'])
                witness=native['reader_witnesses'][t['edition']+'/'+t['member']]
                node=witness['exercise_nodes'][t['fragment']]
                assert 'exercise' in node['class'].split() and 'ptx-content' in node['ancestor_ids']
                targets.append({**t,'html_identity':{k:witness[k] for k in ['bytes','sha256']},
                    'offline_href':'book-'+t['edition']+'/'+t['member']+'#'+t['fragment'],
                    'language':'id-ID'})
            support=[]
            for s in e['support']:
                assert s['relation_id'] not in relations
                relations.add(s['relation_id'])
                assert s['type'] in ['has_hint','has_response']
                populated=s['type']=='has_hint'
                assert s['source_has_content'] is populated and s['target_has_content'] is populated
                assert s['availability']==('provided_content' if populated else 'empty_response_slot')
                support.append(s)
            q={k:e[k] for k in ['id','native_id','course_id','chapter_id','source_path','source_xpath',
                 'source_xml_id','source_label','source_c14n_sha256','target_xpath','target_identifier',
                 'target_c14n_sha256','identifier_method','preorder_index','parent_native_id','exercise_group_kind']}
            q.update({'label':e['source_number'] or re.search(r'/exercise\[(\d+)\]$',e['source_xpath']).group(1),
                'group_path':e['source_xpath'].rsplit('/',1)[0],'support':support,'readers':targets,
                'primary_edition':e['reader_edition'],'rights_native_id':native['rights'][0]['payload']['native_id'],
                'hint_count':sum(s['type']=='has_hint' for s in support),
                'response_slot_count':sum(s['type']=='has_response' for s in support),
                'supplied_response_count':0,'supplied_solution_count':0})
            questions.append(q)
        courses.append({'course_id':role,'exercise_count':count,'questions':questions,
            'chapters':[{k:c[k] for k in ['native_unit_id','projected_unit_id','sequence','localized_title','english_title']}
                        for c in chapters.values() if c['course_id']==role],
            'hint_count':sum(q['hint_count'] for q in questions),
            'response_slot_count':sum(q['response_slot_count'] for q in questions),
            'reader_counts':dict(Counter(q['primary_edition'] for q in questions)),
            'input_identity':lock,'archives':{k:native[k+'_archive'] for k in ['web','sage','source']},
            'rights':native['rights'][0]['payload']})
    assert len(relations)==329
    assert dict(Counter(q['primary_edition'] for c in courses for q in c['questions']))=={'web':814,'sage':99}
    return {'schema':'judson-teacher-selection/1','courses':courses,'input_identity':lock,
        'integration_provenance':{'model':'gpt-6-astra','effort':'ultra','scope':'reference planner; no book translation'},
        'limitations':{
          'id':'Perencana ini memilih rujukan soal, bukan menyalin soal ke lembar kerja baru. Nomor lokal mengikuti kelompok soal dalam sumber, bukan nomor halaman PDF. Untuk kedua mata kuliah, 213 petunjuk berisi materi; 116 ruang respons kosong bukan jawaban atau penyelesaian yang disediakan. Sebanyak 99 soal hanya ada dalam edisi Sage. Arsip beku mengikuti edisi 2026.08.22.2. Tautan pembaca daring terkini telah diperiksa, tetapi isinya mungkin berbeda dari arsip beku. Kedua antarmuka merujuk pada buku berbahasa Indonesia.',
          'en':'This planner selects exercise references; it does not copy exercises into a new worksheet. Local numbers follow source exercise groups, not PDF page numbers. Across both courses there are 213 populated hints; 116 empty response slots are not supplied answers or solutions. 99 exercises are in the Sage edition only. Frozen references follow edition 2026.08.22.2. Current online reader links have been checked, but their content may differ from the frozen archives. Both interfaces point to Indonesian books.'}}


def attach_current_routes(model,access):
    assert access['schema']=='judson-current-reader-access/1' and access['complete'] is True
    assert access['input_sha256']==model['input_identity']['sha256'] and access['verified_exercises']==913
    rows=unique(access['observations'],'member');assert len(rows)==access['requested_pages']==79
    expected={}
    for course in model['courses']:
        for q in course['questions']:
            target=next(t for t in q['readers'] if t['edition']==q['primary_edition'])
            expected.setdefault(target['member'],set()).add(target['fragment'])
            row=rows[target['member']]
            assert row['verified'] is True and row['status']==200 and row['missing_anchors']==[]
            assert row['url']=='https://kokunoyumeto.github.io/abstract-algebra-theory-and-applications-id/'+target['member']
            q['current_reader_url']=row['url']+'#'+target['fragment']
        course['current_reader_observed_utc']=max(row['observed_utc'] for row in rows.values())
    assert rows.keys()==expected.keys()
    for member,anchors in expected.items():
        assert len(rows[member]['expected_anchors'])==len(set(rows[member]['expected_anchors']))
        assert set(rows[member]['expected_anchors'])==anchors
    model['current_reader_identity']=fact(encoded(access))
    return model


def render(course,lang,model):
    en=lang=='en'; role=course['course_id']
    words=({'title':'Abstract algebra assignment planner','chapter':'Chapter','all':'All chapters','filter':'Exercise type',
      'every':'All exercises','hint':'With a supplied hint','nohint':'No supplied hint','response':'Empty response slot','sage':'Sage edition only',
      'search':'Search identifier, source path or local number','choose':'Select','selected':'Selected exercises',
      'select':'Select displayed exercises','clear':'Clear selection','export':'Export assignment','import':'Import assignment','print':'Print references',
      'details':'Source identity and support records','back':'Book archives and offline reading','data':'Exercise data','local':'Enable local book links'} if en else {
      'title':'Perencana tugas aljabar abstrak','chapter':'Bab','all':'Semua bab','filter':'Jenis soal','every':'Semua soal',
      'hint':'Dengan petunjuk yang disediakan','nohint':'Tanpa petunjuk yang disediakan','response':'Ruang respons kosong','sage':'Hanya edisi Sage',
      'search':'Cari identitas, jalur sumber, atau nomor lokal','choose':'Pilih','selected':'Soal terpilih',
      'select':'Pilih soal yang ditampilkan','clear':'Hapus pilihan','export':'Ekspor tugas','import':'Impor tugas','print':'Cetak rujukan',
      'details':'Identitas sumber dan catatan bantuan','back':'Arsip buku dan pembacaan luring','data':'Data soal','local':'Aktifkan tautan buku lokal'})
    full={**course,'schema':model['schema'],'limitations':model['limitations']}
    payload=encoded({'model':full,'locale':lang,'words':words}).decode().replace('<','\\u003c').replace('&','\\u0026')
    options=''.join(f'<option value="{escape(c["native_unit_id"])}">{escape(c["english_title" if en else "localized_title"])}</option>' for c in course['chapters'])
    filter_options=''.join(f'<option value="{value}">{words[key]}</option>' for value,key in [('', 'every'),('hint','hint'),('nohint','nohint'),('response','response'),('sage','sage')])
    archive_links=''.join(f'<li><a href="{escape(a["public_url"],quote=True)}">{kind.upper()} · {escape(a["name"])}</a></li>' for kind,a in course['archives'].items())
    offline=('Download and extract WEB into book-web/ and SAGE into book-sage/ beside these planner pages. Then enable local book links. Book bodies are not bundled with the planner. Sage computation may require an external Sage service or a local installation; this planner does not execute code.' if en else
      'Unduh dan ekstrak WEB ke book-web/ dan SAGE ke book-sage/ di samping halaman perencana ini. Lalu aktifkan tautan buku lokal. Isi buku tidak disertakan dalam paket perencana. Perhitungan Sage mungkin memerlukan layanan Sage eksternal atau instalasi lokal; perencana ini tidak menjalankan kode.')
    nav=('Program','Courses','Learner tools') if en else ('Program','Mata kuliah','Alat belajar')
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{role} · {words['title']}</title><link rel="stylesheet" href="teacher.css"></head>
<body><a class="skip" href="#main">{'Skip to exercises' if en else 'Langsung ke soal'}</a><header><nav aria-label="{'Program navigation' if en else 'Navigasi program'}"><a href="../../{lang}/">{nav[0]}</a><a href="../../{lang}/#courses">{nav[1]}</a><a href="../{'learners.en.html' if en else 'learners.html'}">{nav[2]}</a></nav><nav aria-label="{'Language' if en else 'Bahasa'}"><a href="{role}.teacher.html" lang="id">Bahasa Indonesia</a><a href="{role}.teacher.en.html" lang="en">English</a></nav>
<h1>{role} · {words['title']}</h1><p>{course['exercise_count']} {'exercises' if en else 'soal'} · {course['hint_count']} {'supplied hints' if en else 'petunjuk yang disediakan'} · {course['response_slot_count']} {'empty response slots' if en else 'ruang respons kosong'}</p><p>{escape(model['limitations'][lang])}</p>
<p><a href="{role}.teacher.json">{words['data']}</a> · <a href="judson-teacher-editable-source-v1.zip">{'Editable planner source' if en else 'Sumber perencana yang dapat disunting'}</a></p>
<details id="books"><summary>{words['back']}</summary><p>{offline}</p><ul>{archive_links}</ul><label class="inline"><input type="checkbox" id="local-books">{words['local']}</label></details></header>
<main id="main"><section class="controls"><label>{words['chapter']}<select id="chapter"><option value="">{words['all']}</option>{options}</select></label><label>{words['filter']}<select id="support">{filter_options}</select></label><label>{words['search']}<input type="search" id="search"></label><label class="inline"><input type="checkbox" id="selected-only">{words['selected']}</label><div class="actions"><button id="select-visible">{words['select']}</button><button id="clear">{words['clear']}</button><button id="export">{words['export']}</button><label class="import">{words['import']}<input type="file" id="import" accept="application/json,.json"></label><button id="print">{words['print']}</button></div></section><p id="status" role="status" aria-live="polite"></p><p id="error" role="alert"></p><div id="exercises"></div><noscript>{'JavaScript is needed for selection. Exercise data and archives remain available above.' if en else 'JavaScript diperlukan untuk memilih soal. Data soal dan arsip tetap tersedia di atas.'}</noscript></main>
<footer><p>{'Original author: Thomas W. Judson. The modified Indonesian edition is GFDL-1.3-or-later; the original is GFDL-1.2-or-later. No invariant sections or cover texts.' if en else 'Penulis asli: Thomas W. Judson. Edisi modifikasi Bahasa Indonesia berlisensi GFDL-1.3-or-later; sumber asli GFDL-1.2-or-later. Tidak ada bagian invarian atau teks sampul.'} <a href="COPYING">{'Licence notice' if en else 'Pemberitahuan lisensi'}</a> · <a href="gfdl.xml">{'Original licence text (English XML)' if en else 'Teks lisensi asli (XML berbahasa Inggris)'}</a></p><p>{'Planner integration by OpenAI Codex — gpt-6-astra, Ultra effort. No new book translation or human review is claimed. No analytics, network requests or persistent storage are used by the planner.' if en else 'Integrasi perencana oleh OpenAI Codex — gpt-6-astra, tingkat upaya Ultra. Tidak ada klaim terjemahan buku baru atau peninjauan manusia. Perencana tidak memakai analitik, permintaan jaringan, atau penyimpanan persisten.'}</p></footer>
<script id="planner-data" type="application/json">{payload}</script><script src="teacher.js"></script></body></html>'''


def build(output,base=BASE):
    native,lock=load(base); model=project(native,lock)
    access_bytes=(base/'input/reader-access.json').read_bytes()
    model=attach_current_routes(model,json.loads(access_bytes))
    model['current_reader_identity']=fact(access_bytes)
    files={'teacher-map.json':encoded(model)}
    for c in model['courses']:
        files[c['course_id']+'.teacher.json']=encoded({**c,'schema':model['schema'],'limitations':model['limitations']})
        for lang in ['id','en']:
            files[c['course_id']+'.teacher'+('.en' if lang=='en' else '')+'.html']=render(c,lang,model).encode('utf-8')
    for name in ['teacher.js','teacher.css']:
        files[name]=(base/'ui'/name).read_bytes()
    for name in ['COPYING','gfdl.xml']:
        files[name]=(base/'input'/name).read_bytes()
    output.mkdir(parents=True,exist_ok=True)
    for name,body in files.items(): (output/name).write_bytes(body)
    receipt={'schema':'judson-teacher-build/1','state':'built-not-admitted','exercise_count':913,
             'input_identity':lock,'current_reader_identity':model['current_reader_identity'],
             'course_counts':COUNTS,'files':[{'path':n,**fact(b)} for n,b in sorted(files.items())]}
    (output/'teacher-build.json').write_bytes(encoded(receipt))
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=BASE/'site')
    args=parser.parse_args(); print(json.dumps(build(args.output)))
