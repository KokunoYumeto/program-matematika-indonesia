"""Build a bilingual C130 reference planner from the verified source/PDF map."""
import argparse
from html import escape
import hashlib
import json
from pathlib import Path
import re
import io
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'backend/course-capsule-v1/adapters/c130-teacher-v1'
MAPPING_IDENTITY={'bytes':2407293,'sha256':'c9fa1a2630510fb0719086b69c741d6e75b076d321e65cc6009a40180c0f8ca8'}


def encoded(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
def fact(data):return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def display_title(title):
    """Only known title typography; canonical source text stays in mapping.json."""
    title=title.replace("\\'e",'é').replace('``','“').replace("''",'”')
    title=re.sub(r'\\texttt\{([^{}]*)\}',r'\1',title)
    title=title.replace(r'\varepsilon','ε').replace('$','')
    if '\\' in title or '{' in title or '}' in title:
        raise ValueError('Unaccounted title markup: '+title)
    return title


def project(data, mapping_sha256):
    assert data['schema']=='c130-teacher-mapping/1' and data['counts']['selectable_reader_exercises']==203
    assert len(data['questions'])==203 and len({q['id'] for q in data['questions']})==203
    assert data['reader']['sha256']=='daa9b79df3684729cc204b563669f400866d8fbd12c0977d32ff9897276a7a49'
    questions=[]
    for row in data['questions']:
        assert type(row['reader']['page']) is int and 1<=row['reader']['page']<=666
        assert type(row['chapter']) is int and 1<=row['chapter']<=15
        assert re.fullmatch('[0-9a-f]{64}',row['source_span']['content_sha256'])
        manual=[];labs={}
        for support in row['supports']:
            if 'page' in support:
                assert type(support['page']) is int and 1<=support['page']<=666
                manual.append({k:support[k] for k in ['id','page','kind']})
            else:
                source=support['source'];paths=source.get('code_data_refs') or []
                if source.get('content_path'):paths=[source['content_path'],*paths]
                labs[support['id']]={'id':support['id'],'kind':support['kind'],'paths':sorted(set(paths))}
        s=row['source_span']
        questions.append({'id':row['id'],'native_id':row['native_id'],'chapter':row['chapter'],
            'number':row['number'],'display_number':row['number'] if row['kind']=='numbered-exercise' else '14 / G'+row['number'],
            'kind':row['kind'],'title':display_title(row['title_id']),
            'page':row['reader']['page'],'manual':manual,'labs':list(labs.values()),
            'source':{'path':s['path'],'lines':s['line_range'],'sha256':s['content_sha256']}})
    assert sum(q['native_id'] is None for q in questions)==13
    assert sum(bool(q['manual']) for q in questions)==191
    support=data['support_navigation'];solutions=[]
    for row in support['materials']:
        s=row['source_span'];source={'path':s['path'],'lines':s['line_range'],'sha256':s['content_sha256']}
        if row['kind']=='solution':
            solutions.append({'id':row['id'],'page':row['page'],'printed_state':row['printed_state'],'source':source})
        if row['kind'] not in ['learningcheckpoint','tryit']:continue
        chapter=int(re.search(r'\.ch(\d+)',row['id']).group(1))
        if row['kind']=='learningcheckpoint':
            number=row['reader']['printed_number'];title='Cek Pemahaman '+number
            manual=[{'id':row['answer']['id'],'page':row['answer']['page'],'kind':'checkpoint-answer'}]
        else:
            number=str(int(row['id'].rsplit('-',1)[1]));title=' / '.join(t['source_text'] for t in row['visualization_titles']);manual=[]
        questions.append({'id':row['id'],'native_id':row['id'],'chapter':chapter,'number':number,
            'display_number':f'{chapter} / '+('C' if row['kind']=='learningcheckpoint' else 'V')+number,
            'kind':row['kind'],'title':title,'page':row['page'],'manual':manual,'labs':[],'source':source})
    questions.sort(key=lambda q:(q['chapter'],q['page'],{'numbered-exercise':0,'graph-practice':1,'learningcheckpoint':2,'tryit':3}[q['kind']],int(q['number'].split('.')[-1])))
    assert len(questions)==227 and len(solutions)==132
    return {'schema':'c130-teacher-planner/1','course_id':'C130','mapping_sha256':mapping_sha256,
        'reader':data['reader'],'labs':data['inputs']['labs'],'chapters':data['chapters'],
        'counts':{**data['counts'],'selectable_learning_items':227,**support['counts']},'questions':questions,
        'supplementary_solutions':solutions,
        'source_only':[{'id':r['id'],'reason':r['reason'],'source':r['source_span']['path']} for r in data['source_only']],
        'provenance':{'agent':'OpenAI Codex','model':'gpt-6-astra','effort':'ultra',
            'scope':'Central mapping and reference planner; no book translation or independent mathematical correctness certification.'}}


WORDS={
'id':{'title':'Perencana tugas Riset Operasi','lead':'Pilih latihan, buka halaman buku yang tepat, dan temukan bagian manual atau praktikum yang mendukungnya.',
 'chapter':'Bab','page':'Halaman PDF','all':'Semua','support':'Bahan pendukung','manualFilter':'Dengan manual','labsFilter':'Dengan praktikum','noManualFilter':'Tanpa pemetaan manual',
 'search':'Cari nomor, judul, atau ID sumber','chooseVisible':'Pilih yang ditampilkan','clear':'Hapus pilihan','export':'Ekspor tugas JSON','import':'Impor tugas JSON','print':'Cetak rujukan',
 'selectedOnly':'Hanya pilihan','solutions':'Tampilkan tautan penyelesaian','local':'Gunakan reader.pdf lokal','choose':'Pilih','identity':'Identitas dan lokasi sumber','lines':'baris',
 'manual':'Buka bagian manual','rubric':'Buka panduan dan rubrik','manualAvailable':'Bagian manual tersedia','noManual':'Belum ada pemetaan manual untuk soal ini',
 'lab':'Rujukan praktikum','downloadLabs':'Unduh paket praktikum','labLimit':'Keterkaitan berasal dari backend buku; hasil komputasi belum dijalankan ulang dalam perencana ini.',
 'chosen':'Dipilih','imported':'Tugas berhasil diimpor.','invalid':'Tugas ditolak: edisi, identitas, atau rujukannya berubah. Pilihan lama tetap dipertahankan.',
 'static':'Semua rujukan tanpa JavaScript','exercise':'Latihan','count':'203 latihan dalam PDF · 191 dengan pemetaan manual · 13 butir graf yang kini terindeks',
 'boundary':'Kedua antarmuka membuka buku Bahasa Indonesia yang sama. G1–G19 adalah daftar latihan graf tersendiri, bukan Latihan 14.1–14.4. Dua bagian eksplorasi berisi panduan dan rubrik, bukan satu jawaban tunggal. Empat latihan dalam cabang sumber lama tidak dicetak dalam PDF ini dan tidak ditawarkan sebagai latihan pembaca.',
 'offline':'Untuk pemakaian luring, simpan PDF buku sebagai reader.pdf di samping halaman ini, lalu aktifkan tautan lokal. Penyaringan dan pertukaran tugas tidak menggunakan peladen, pelacakan, atau penyimpanan peramban. Buku dan paket praktikum harus diunduh terpisah.',
 'evidence':'Bukti pemetaan','data':'Data perencana','limits':'Pemetaan ini memeriksa identitas sumber dan tujuan pembaca; bukan audit ulang kebenaran matematika, mutu terjemahan, atau hasil solver. Tidak semua penyelesaian, cek pemahaman, dan kegiatan mandiri dari backend asli sudah memiliki navigasi cetak dalam perencana ini.',
 'credit':'Pemetaan dan perencana rujukan dibuat oleh OpenAI Codex — gpt-6-astra, Ultra effort. Buku mempertahankan atribusi dan riwayat penerbitannya sendiri.',
 'read':'Buka buku','program':'Kembali ke program'},
'en':{'title':'Operations Research assignment planner','lead':'Choose exercises, open the exact reader page, and find the supporting manual sections or laboratory references.',
 'chapter':'Chapter','page':'PDF page','all':'All','support':'Supporting material','manualFilter':'With manual material','labsFilter':'With laboratory references','noManualFilter':'Without a manual mapping',
 'search':'Search number, Indonesian title or source ID','chooseVisible':'Select displayed exercises','clear':'Clear selection','export':'Export assignment JSON','import':'Import assignment JSON','print':'Print references',
 'selectedOnly':'Selected only','solutions':'Show solution links','local':'Use local reader.pdf','choose':'Select','identity':'Source identity and location','lines':'lines',
 'manual':'Open manual section','rubric':'Open guidance and rubric','manualAvailable':'Manual section available','noManual':'No manual mapping for this exercise yet',
 'lab':'Laboratory references','downloadLabs':'Download laboratory package','labLimit':'Relationships come from the native book backend; computation has not been re-executed in this planner.',
 'chosen':'Selected','imported':'Assignment imported.','invalid':'Assignment rejected: the edition, identity or references changed. Your previous selection is unchanged.',
 'static':'All references without JavaScript','exercise':'Exercise','count':'203 reader exercises · 191 with manual mappings · 13 newly indexed graph items',
 'boundary':'Both interfaces open the same Indonesian book. G1–G19 are a separate graph practice list, not Exercises 14.1–14.4. Two exploration sections provide guidance and rubrics, not a single answer. Four exercises in a legacy source branch are absent from this PDF and are not offered as reader exercises.',
 'offline':'For offline use, save the linked book PDF as reader.pdf beside this page, then enable local links. Filtering and assignment exchange use no server, tracking or browser storage. Download the book and laboratory package separately.',
 'evidence':'Mapping evidence','data':'Planner data','limits':'This checks source identity and reader destinations, not mathematical correctness, translation quality or solver results. Other native solutions, checkpoints and try-it activities do not yet all have printed navigation in this planner.',
 'credit':'Reference mapping and planner produced by OpenAI Codex — gpt-6-astra, Ultra effort. The book retains its own attribution and publication history.',
 'read':'Open book','program':'Return to program'}
}

WORDS['id'].update({
 'count':'203 latihan · 12 cek pembelajaran beserta jawaban · 12 kegiatan visual',
 'exchange':'Teks tugas JSON (salin atau tempel)','loadText':'Impor teks JSON','exchangeNote':'Gunakan teks ini jika peramban tidak menyimpan unduhan. Nomor halaman dan identitas sumber akan diperiksa saat diimpor.',
 'exercise':'Latihan atau kegiatan','kind':'Jenis bahan','numbered-exercise':'Latihan bernomor','graph-practice':'Daftar latihan graf',
 'learningcheckpoint':'Cek pembelajaran','tryit':'Kegiatan visual','manualFilter':'Dengan manual atau jawaban',
 'manual':'Buka bagian manual','checkpoint-answer':'Buka bagian jawaban','noManual':'Tidak ada manual atau jawaban yang dipetakan untuk bahan ini',
 'static':'Semua rujukan tanpa JavaScript','chooseVisible':'Pilih semua bahan yang ditampilkan',
 'extra':'Penyelesaian lain dari buku dan lampiran','passage':'Buka bagian teks yang cocok',
 'unmapped':'Identitas sumber terverifikasi; halaman PDF belum dipetakan',
 'extraNote':'132 penyelesaian lainnya tetap dicatat: 104 mempunyai tautan bagian teks yang cocok, dan 12 kini mempunyai tautan awal penyelesaian berdasarkan rujukan sumber, relasi asli, serta judul tercetak yang unik. Sebanyak 16 belum mempunyai pemetaan halaman. Isi penyelesaian dapat berlanjut ke halaman berikutnya. Ini bukan 132 soal tambahan.',
 'solutionStart':'Buka awal penyelesaian',
 'limits':'Pemetaan ini memeriksa identitas sumber dan tujuan pembaca; bukan audit ulang kebenaran matematika, mutu terjemahan, atau hasil solver. Kegiatan visual diarahkan ke penjelasan dalam buku; ketersediaan situs interaktif luar belum diperiksa. Sebanyak 16 penyelesaian lain masih memerlukan pemetaan halaman.'})
WORDS['en'].update({
 'count':'203 exercises · 12 checkpoints with answers · 12 visual activities',
 'exchange':'Assignment JSON text (copy or paste)','loadText':'Import JSON text','exchangeNote':'Use this text if your browser does not save the download. Import checks page references and source identities.',
 'exercise':'Exercise or activity','kind':'Material type','numbered-exercise':'Numbered exercises','graph-practice':'Graph practice list',
 'learningcheckpoint':'Checkpoints','tryit':'Visual activities','manualFilter':'With manual material or an answer',
 'checkpoint-answer':'Open answer passage','noManual':'No manual or answer mapping for this item',
 'chooseVisible':'Select displayed items','extra':'Other solutions in the book and appendix','passage':'Open matching passage',
 'unmapped':'Source identity verified; PDF page not yet mapped',
 'extraNote':'All 132 other solution sources are retained: 104 have matching-passage links, and 12 now link to the solution start using an exact source reference, native relation and unique printed heading. Another 16 lack a page mapping. A solution may continue on the following page. These are not 132 additional questions.',
 'solutionStart':'Open solution start',
 'limits':'This checks source identity and reader destinations, not mathematical correctness, translation quality or solver results. Visual activities link to their explanations in the book; external interactive sites have not been checked. Another 16 solution sources still need page mapping.'})


def render(model,lang):
    w=WORDS[lang];e=lambda value:escape(str(value),quote=True)
    payload=encoded({'model':model,'words':w}).decode().replace('<','\\u003c').replace('&','\\u0026')
    chapter_options=''.join(f'<option value="{k}">{k} · {e(v)}</option>' for k,v in sorted(model['chapters'].items(),key=lambda x:int(x[0])))
    static=''.join(f'<tr><td>{e(q["display_number"])}</td><td><a class="reader-reference" data-page="{q["page"]}" href="{e(model["reader"]["url"])}#page={q["page"]}">{e(q["title"])}</a></td><td>{q["page"]}</td></tr>' for q in model['questions'])
    kinds=''.join(f'<option value="{kind}">{w[kind]}</option>' for kind in ['numbered-exercise','graph-practice','learningcheckpoint','tryit'])
    supplementary=''.join('<li>'+('<a class="reader-reference" data-page="'+str(s['page'])+'" href="'+e(model['reader']['url'])+'#page='+str(s['page'])+'">'+w['solutionStart' if s['printed_state']=='native-reference-and-unique-solution-heading' else 'passage']+' · '+str(s['page'])+'</a>' if s['page'] else w['unmapped'])+'<details><summary>'+w['identity']+'</summary><code>'+e(s['id'])+'</code><p>'+e(s['source']['path'])+' · '+w['lines']+' '+e(s['source']['lines'])+'</p><code>'+s['source']['sha256']+'</code></details></li>' for s in model['supplementary_solutions'])
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{w['title']}</title><link rel="stylesheet" href="teacher.css"></head>
<body><a class="skip" href="#main">{w['title']}</a><header><a href="../../{lang}/index.html#course-C130">{w['program']}</a><nav aria-label="{'Bahasa' if lang=='id' else 'Language'}"><a href="C130.teacher.html" lang="id" {'aria-current="page"' if lang=='id' else ''}>Bahasa Indonesia</a><a href="C130.teacher.en.html" lang="en" {'aria-current="page"' if lang=='en' else ''}>English</a></nav></header>
<main id="main"><p class="eyebrow">C130 · R017 / O018 · {'Rujukan belajar dan mengajar' if lang=='id' else 'Learning and teaching references'}</p><h1>{w['title']}</h1><p class="lead">{w['lead']}</p><p><strong>{w['count']}</strong></p><p class="note">{w['boundary']}</p>
<p><a class="reader-reference" data-page="1" href="{model['reader']['url']}">{w['read']}</a> · <a href="planner-model.json">{w['data']}</a> · <a href="mapping.json">{w['evidence']}</a> · <a href="c130-teacher-source-v1.zip">{'Sumber perencana lengkap' if lang=='id' else 'Complete planner source'}</a></p>
<section id="interactive" hidden aria-label="{w['title']}"><div class="filters"><label>{w['chapter']}<select id="chapter"><option value="">{w['all']}</option>{chapter_options}</select></label><label>{w['kind']}<select id="kind"><option value="">{w['all']}</option>{kinds}</select></label><label>{w['support']}<select id="support"><option value="">{w['all']}</option><option value="manual">{w['manualFilter']}</option><option value="labs">{w['labsFilter']}</option><option value="none">{w['noManualFilter']}</option></select></label><label>{w['search']}<input id="search" type="search"></label></div>
<div class="options"><label><input id="selected-only" type="checkbox">{w['selectedOnly']}</label><label><input id="solutions" type="checkbox">{w['solutions']}</label><label><input id="local" type="checkbox">{w['local']}</label></div>
<div class="actions"><button class="primary" id="choose-visible">{w['chooseVisible']}</button><button id="clear">{w['clear']}</button><button id="export">{w['export']}</button><label class="file-label">{w['import']} <input id="import" type="file" accept=".json,application/json"></label><button id="print">{w['print']}</button></div><details id="exchange"><summary>{w['exchange']}</summary><p>{w['exchangeNote']}</p><label for="exchange-text">{w['exchange']}</label><textarea id="exchange-text" rows="6" spellcheck="false"></textarea><button id="load-json">{w['loadText']}</button></details><p id="count" aria-live="polite"></p><p id="message" role="status"></p><div class="table-wrap"><table><thead><tr><th>{w['choose']}</th><th>{w['exercise']}</th><th>{w['support']}</th></tr></thead><tbody id="questions"></tbody></table></div></section>
<details class="static"><summary>{w['static']} ({len(model['questions'])})</summary><div class="table-wrap"><table><thead><tr><th>{w['exercise']}</th><th>{w['search']}</th><th>{w['page']}</th></tr></thead><tbody>{static}</tbody></table></div></details><details><summary>{w['extra']} (132)</summary><p>{w['extraNote']}</p><ul>{supplementary}</ul></details><p class="note">{w['offline']}</p><p>{w['limits']}</p></main>
<footer><p>{w['credit']}</p><p>SHA-256: <code>{model['mapping_sha256']}</code></p></footer><script id="planner-data" type="application/json">{payload}</script><script src="teacher.js" defer></script></body></html>'''


def main():
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,default=BASE);p.add_argument('--out',type=Path)
    args=p.parse_args();out=args.out or args.base/'site';out.mkdir(parents=True,exist_ok=True)
    raw=(args.base/'mapping.json').read_bytes();assert fact(raw)==MAPPING_IDENTITY,'Mapping input drift'
    model=project(json.loads(raw),fact(raw)['sha256'])
    files={'mapping.json':raw,'planner-model.json':encoded(model)}
    for lang,suffix in [('id',''),('en','.en')]:files[f'C130.teacher{suffix}.html']=render(model,lang).encode()
    for name in ['teacher.js','teacher.css']:files[name]=(args.base/'ui'/name).read_bytes()
    source_files={str(p.relative_to(ROOT)).replace('\\','/'):p.read_bytes() for p in [
        ROOT/'scripts/build-c130-teacher-v1.py',ROOT/'scripts/map-c130-teacher-v1.py',
        ROOT/'scripts/c130_source_spans.py',ROOT/'scripts/c130_support_navigation.py',
        ROOT/'scripts/test-c130-teacher-v1.py',ROOT/'scripts/test-c130-teacher-ui-v1.cjs',
        args.base/'README.md',args.base/'mapping.json',args.base/'ui/teacher.js',args.base/'ui/teacher.css']}
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path,content in sorted(source_files.items()):
            info=zipfile.ZipInfo(path,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16;archive.writestr(info,content)
    files['c130-teacher-source-v1.zip']=buffer.getvalue()
    for name,data in files.items():(out/name).write_bytes(data)
    receipt={'schema':'c130-teacher-build/1','state':'built-local-not-admitted','mapping':fact(raw),
        'files':{name:fact(data) for name,data in sorted(files.items())},'counts':model['counts'],
        'source_members':{name:fact(content) for name,content in sorted(source_files.items())}}
    (out/'build-receipt.json').write_bytes(encoded(receipt))
    print(json.dumps({'state':receipt['state'],'files':len(files),'questions':len(model['questions']),
        'mapping':receipt['mapping'],'model':fact(files['planner-model.json'])}))


if __name__=='__main__':main()
