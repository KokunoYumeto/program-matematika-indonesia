"""Bilingual consumer of frozen CLP-1 metadata; no producer writes or new canon claim."""
import argparse
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'backend/course-capsule-v1/adapters/clp1-native-terminology-v1'
OUT = ROOT/'docs/backend/clp'
spec = importlib.util.spec_from_file_location('projection', Path(__file__).with_name('clp1-native-terminology-v1.py'))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
RIGHTS = {
 'LICENSE.md': ('LICENSE.md', '2c369e074c4cbe94e9bdde678f9a325e3aa68697c0180e8d97cf65707068ad05'),
 'LICENSE-CC-by-nc-sa.md': ('LICENSE-CC-by-nc-sa.md', '751431b663663e16259724ffecc04f1d5e1501ead3eb2d7dbb4dbe20dfc2bf52'),
 'rights.jsonl': ('modular_backend/backend/rights.jsonl', '199b4c92e4b6aff458024721b9c10948959b62065f6a674a8282b2c4490c0af2'),
}

def load():
    manifest = json.loads((BASE/'manifest.json').read_bytes())
    for row in manifest['files']:
        assert p.fact((BASE/row['path']).read_bytes()) == {k:row[k] for k in ['bytes','sha256']}
    inputs = BASE/'input'
    raw = {name:(inputs/name).read_bytes() for name in ['terms.jsonl','concepts.jsonl','TRANSLATION_DECISIONS.id-ID.md']}
    rows = lambda name: [json.loads(line) for line in raw[name].splitlines() if line.strip()]
    data = p.project(rows('terms.jsonl'),rows('concepts.jsonl'),raw['TRANSLATION_DECISIONS.id-ID.md'].decode('utf-8'))
    assert p.canonical(data) == (BASE/'projection.json').read_bytes()
    for name,(_,sha) in RIGHTS.items():
        body=(inputs/name).read_bytes(); assert p.fact(body)['sha256']==sha
    concepts={c['id']:c for c in data['concepts']}
    assert all(t['concept_id'] in concepts for t in data['terms'])
    assert all(pr in concepts for c in data['concepts'] for pr in c['prerequisite_ids'])
    return data

def render(data, en=False):
    e=html.escape
    tr=lambda id,en_text: en_text if en else id
    lang='en' if en else 'id'
    reading_origin='https://kokunoyumeto.github.io/program-matematika-indonesia/backend/clp/'
    title=tr('B20 · Istilah kalkulus dalam dua bahasa','B20 · Calculus terminology in two languages')
    corrections={c['native_term_id']:c for c in data['corrections']}
    concepts={c['id']:c for c in data['concepts']}
    terms={t['concept_id']:t for t in data['terms']}
    cards=[]
    for t in data['terms']:
        correction=corrections.get(t['id'])
        concept=concepts[t['concept_id']]
        links=' · '.join(f'<a href="#{e(terms[c]["id"])}">{e(terms[c]["source_term"] if en else terms[c]["target_term"])}</a>' for c in concept['prerequisite_ids'])
        quoted=tr('Status yang dicatat penerjemah (belum diverifikasi di sini)','Producer-recorded status (not independently verified here)')
        repair=''
        if correction:
            before=correction['before']; after=correction['after']; evidence=correction['evidence']
            repair=f'<p class="repair">{tr("Label metadata diperbaiki", "Metadata label repaired")}</p><details><summary>{tr("Lihat perubahan dan bukti", "See change and evidence")}</summary><p>{e(before["source"])} → {e(after["source"])}<br>{e(before["target"])} → {e(after["target"])}</p><p>{e(correction["reason_en" if en else "reason_id"])}</p><blockquote lang="id">{e(evidence["quote"])}</blockquote><p><a href="clp1-terms-data/TRANSLATION_DECISIONS.id-ID.md">{tr("Tabel keputusan asli, baris", "Original decision table, line")} {evidence["line"]}</a></p></details>'
        evidence=f'<p><a href="clp1-terms-data/TRANSLATION_DECISIONS.id-ID.md">{tr("Kebijakan istilah asli (Bahasa Indonesia)", "Original terminology policy (Bahasa Indonesia)")}</a></p>'
        relations=f'<p>{tr("Prasyarat yang dicatat dalam metadata asli", "Prerequisites recorded in native metadata")}: {links}</p>' if links else ''
        cards.append(f'<article id="{e(t["id"])}" data-search="{e(t["source_term"]+" "+t["target_term"]+" "+t["id"],quote=True)}" data-corrected="{str(bool(correction)).lower()}"><h2 lang="id">{e(t["target_term"])}</h2><p class="source" lang="en">{e(t["source_term"])}</p>{repair}{evidence}<details><summary>{tr("Identitas dan relasi konsep", "Concept identity and relations")}</summary><p><code>{e(t["id"])}</code><br><code>{e(t["concept_id"])}</code></p>{relations}<p>{quoted}: <code>{e(t["status"])}</code></p><p>{tr("Relasi ini dipertahankan sebagai catatan sumber, bukan urutan belajar yang telah diuji.", "These relations are retained source records, not a validated learning sequence.")}</p></details></article>')
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>body{{max-width:72rem;margin:auto;padding:1.3rem;font:1rem/1.6 system-ui;color:#19312e;background:#fafbf7}}a{{color:#075e66}}nav{{display:flex;gap:1rem;flex-wrap:wrap}}.note{{padding:1rem;background:#e4eeea;border-left:4px solid #277469}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,20rem),1fr));gap:1rem}}article{{border:1px solid #cbd7d0;border-radius:.5rem;background:white;padding:1rem}}article[hidden]{{display:none}}h2{{margin:.1rem 0}}input{{font:inherit;padding:.5rem}}.source{{font-size:1.12rem}}.repair{{font-weight:bold;color:#775006}}code,blockquote{{overflow-wrap:anywhere}}details{{margin:.7rem 0}}summary{{cursor:pointer}}:focus-visible{{outline:3px solid #b47717;outline-offset:3px}}@media print{{.controls{{display:none}}article{{break-inside:avoid}}}}</style></head><body>
<a href="#main">{tr('Langsung ke istilah','Skip to terminology')}</a><nav aria-label="{tr('Navigasi','Navigation')}"><a href="{reading_origin}B20.html">{tr('Buku dan bacaan B20','B20 books and reading')}</a><a href="{reading_origin}B20.teacher{'.en' if en else ''}.html">{tr('Perencana tugas untuk pengajar','Teacher assignment planner')}</a><a href="B20.terms{'' if en else '.en'}.html" lang="{'id' if en else 'en'}">{'Bahasa Indonesia' if en else 'English'}</a></nav>
<main id="main"><h1>{title}</h1><p>{tr('Cari 24 istilah yang sudah dipakai dalam CLP-1. Cocokkan nama Inggris dan Indonesia ketika membaca atau menyiapkan tugas.', 'Look up 24 terms already used in CLP-1. Match English and Indonesian names while reading or preparing assignments.')}</p>
<p class="note">{tr('Tiga label metadata kehilangan kata ketika tabel bergaris miring dipecah. Tampilan ini mengembalikan kata tersebut berdasarkan tabel asli; buku tidak diubah. Ini bukan pemeriksaan baru terhadap semua pilihan terjemahan atau penggunaan kanon. Cakupan setiap kemunculan istilah belum dibuktikan.', 'Three metadata labels lost words when slash-separated table cells were split. This view restores those words from the original table; the book is unchanged. This is not a new review of every translation choice or canon use. Occurrence-level coverage is not established.')}</p>
<div class="controls"><label for="search">{tr('Cari istilah atau ID','Search term or ID')}</label> <input id="search" type="search"><label><input id="corrected" type="checkbox"> {tr('Hanya tiga label yang diperbaiki','Only the three repaired labels')}</label><p id="count" aria-live="polite"></p></div><div class="cards">{''.join(cards)}</div>
<h2>{tr('Sumber dan penggunaan ulang','Sources and reuse')}</h2><p><a href="B20.terms.json">{tr('Data istilah dan perubahan (JSON)','Term and correction data (JSON)')}</a> · <a href="clp1-terms-source-v1.zip">{tr('Sumber lengkap untuk membangun ulang (ZIP)','Complete rebuildable source (ZIP)')}</a> · <a href="B20.terms.validation.json">{tr('Identitas berkas dan cakupan pemeriksaan','File identities and check scope')}</a></p>
<p>{tr('Pencarian dan bukti dalam paket ini dapat digunakan luring setelah ZIP diunduh dan diekstrak. Buku dan perencana tugas ditautkan, tidak disalin ke paket ini; tautan tersebut membutuhkan jaringan atau unduhan terpisah.', 'Search and evidence work offline after downloading and extracting the ZIP. Books and assignment planners are linked, not copied into this package; those links require a network or separate downloads.')}</p>
<p>Joel Feldman, Andrew Rechnitzer, Elyse Yeager · CLP-1 · <a href="clp1-terms-data/LICENSE-CC-by-nc-sa.md">CC BY-NC-SA 4.0</a> · <a href="clp1-terms-data/rights.jsonl">{tr('Hak dan provenance asli','Original rights and provenance')}</a>.</p>
<p>{tr('Rekaman asli menyebut OpenAI Codex gpt-5.6-sol, Ultra. Integrasi metadata dan antarmuka ini: OpenAI Codex — gpt-6-astra, Ultra effort. Tidak diklaim ada pemeriksaan manusia. Lisensi kode tidak mengubah hak bahan asli.', 'The native record credits OpenAI Codex gpt-5.6-sol, Ultra. This metadata and interface integration: OpenAI Codex — gpt-6-astra, Ultra effort. No human review is claimed. The code licence does not change native material rights.')}</p></main>
<script>const input=document.getElementById('search'), toggle=document.getElementById('corrected'), rows=[...document.querySelectorAll('[data-search]')];function filter(){{const q=input.value.toLocaleLowerCase();let n=0;for(const row of rows){{row.hidden=!row.dataset.search.toLocaleLowerCase().includes(q)||(toggle.checked&&row.dataset.corrected!=='true');if(!row.hidden)n++;}}document.getElementById('count').textContent=n+' / '+rows.length;}}input.addEventListener('input',filter);toggle.addEventListener('change',filter);filter();</script></body></html>'''.encode('utf-8')

def build(out=OUT):
    data=load()
    view_data={**data,'consumer_integration':'searchable_bilingual_view','source_projection_identity':p.fact((BASE/'projection.json').read_bytes())}
    outputs={'B20.terms.html':render(data),'B20.terms.en.html':render(data,True),'B20.terms.json':p.canonical(view_data)}
    for f in sorted((BASE/'input').iterdir()):
        outputs['clp1-terms-data/'+f.name]=f.read_bytes()
    members={f'docs/backend/clp/{name}':body for name,body in outputs.items()}
    prefix=BASE.relative_to(ROOT).as_posix()
    for name in ['projection.json','manifest.json',*[f'input/{f.name}' for f in (BASE/'input').iterdir()]]:
        members[prefix+'/'+name]=(BASE/name).read_bytes()
    for name in ['clp1-native-terminology-v1.py','test-clp1-native-terminology-v1.py','build-clp1-term-view-v1.py','test-clp1-term-view-v1.py','test-clp1-term-ui-v1.mjs']:
        members['scripts/'+name]=(ROOT/'scripts'/name).read_bytes()
    members['LICENSE']=(ROOT/'LICENSE').read_bytes()
    members['README.txt']=('Bangun ulang / Rebuild: python -B scripts/build-clp1-term-view-v1.py\nUji / Test: python -B scripts/test-clp1-term-view-v1.py --skip-replay\nUji pencarian / Test search: node scripts/test-clp1-term-ui-v1.mjs\nBuka / Open: docs/backend/clp/B20.terms.html or B20.terms.en.html\nPaket metadata dan antarmuka; tidak memuat buku atau perencana tugas.\nMetadata and interface package; books and assignment planners are not included.\nKode antarmuka / interface code: MIT. Bahan CLP / CLP material: CC BY-NC-SA 4.0, see docs/backend/clp/clp1-terms-data.\n').encode()
    # Portable entry links retain course context online; do not point at absent local books.
    origin='https://kokunoyumeto.github.io/program-matematika-indonesia/backend/clp/'
    for name in ['B20.terms.html','B20.terms.en.html']:
        body=members['docs/backend/clp/'+name].decode()
        for linked in ['B20.html','B20.teacher.html','B20.teacher.en.html','B20.terms.validation.json','clp1-terms-source-v1.zip']:
            body=body.replace('href="'+linked+'"','href="'+origin+linked+'"')
        members['docs/backend/clp/'+name]=body.encode()
    out.mkdir(parents=True,exist_ok=True)
    zip_path=out/'clp1-terms-source-v1.zip'
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,body in sorted(members.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,9,30,0,0,0)); info.external_attr=0o100644<<16
            z.writestr(info,body,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    outputs[zip_path.name]=zip_path.read_bytes()
    for name,body in outputs.items():
        path=out/name; path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    validation={'schema':'clp1-term-consumer/1','state':'pass','course_id':'B20','terms':24,'concepts':24,'corrected_terms':3,
      'locales':['id','en'],'native_ids_preserved':True,'semantic_canon_review':False,'book_modified':False,
      'source_projection':p.fact((BASE/'projection.json').read_bytes()),'files':[{'path':name,**p.fact(body)} for name,body in sorted(outputs.items())]}
    (out/'B20.terms.validation.json').write_bytes(p.canonical(validation))
    return validation

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--intake-rights',type=Path);args=parser.parse_args()
    if args.intake_rights:
        for name,(rel,sha) in RIGHTS.items():
            body=(args.intake_rights/rel).read_bytes();assert p.fact(body)['sha256']==sha
            dest=BASE/'input'/name
            if dest.exists(): assert dest.read_bytes()==body
            else: dest.write_bytes(body)
    report=build(); print(json.dumps({'state':'pass','terms':report['terms'],'locales':report['locales'],'files':len(report['files'])}))
