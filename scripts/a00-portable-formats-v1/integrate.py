"""Add hash-bound A00 formats without replacing native sources or old links."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/a00-portable-formats-v1'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
identity = lambda b: {'bytes':len(b), 'sha256':hashlib.sha256(b).hexdigest()}
final = read(OUT / 'FINAL_FORMAT_VALIDATION.json')
github = read(OUT / 'GITHUB_FORMAT_PUBLICATION.json')
zenodo = read(OUT / 'ZENODO_FORMAT_PUBLICATION.json')
assert final['status'] == 'validated_local_not_publication'
assert github['status'] == zenodo['status'] == 'published_and_anonymously_verified'
assert final['clean_pdf_and_epub_byte_identical'] and zenodo['original_records_unchanged']
assert zenodo['draft_id'] == 23149334
files = final['editions']['id']['files_in_reading_order']
assert [f['file'] for f in files] == ['00-a00-id.pdf','01-a00-id.tex','02-a00-id-source.zip','03-a00-id.epub']
labels = {
 'id':['PDF Praljabar — 1.638 halaman','LaTeX kumulatif untuk PDF Praljabar','Sumber lengkap PDF dan EPUB Praljabar','EPUB Praljabar'],
 'en':['Prealgebra PDF — 1,638 pages','Cumulative LaTeX for the Prealgebra PDF','Complete Prealgebra PDF and EPUB source','Prealgebra EPUB']}
notes = {
 'id':'Edisi format 5 Oktober 2026, Bahasa Indonesia: 75 modul; PDF, LaTeX, ZIP sumber dan EPUB merupakan satu set yang cocok. PDF dan EPUB dapat dibangun ulang byte-identik. Sumber utama CNXML/MathML dan edisi terdahulu tetap tersedia. Penulis asli: Lynn Marecek, MaryAnne Anthony-Smith dan Andrea Honeycutt Mathis, OpenStax. Terjemahan: OpenAI Codex gpt-5.6-sol, upaya Ultra. Ekspor dan integrasi format: OpenAI Codex — GPT-6 Astra, upaya Ultra. Bukan penerjemahan atau peninjauan matematika baru. Ketentuan lisensi setiap komponen mengikuti paket sumber. Rujukan eksternal memerlukan internet.',
 'en':'Format edition 5 October 2026, Indonesian content: 75 modules; PDF, LaTeX, source ZIP and EPUB form one matching set. PDF and EPUB rebuild byte-identically. The CNXML/MathML master and earlier editions remain available. Original authors: Lynn Marecek, MaryAnne Anthony-Smith and Andrea Honeycutt Mathis, OpenStax. Translation: OpenAI Codex gpt-5.6-sol, Ultra effort. Format exports and integration: OpenAI Codex — GPT-6 Astra, Ultra effort. Not a new translation or mathematical review. Component licence terms remain in the source package. External references need internet.'}
rows = []
public = []
for i,f in enumerate(files):
    assert identity((OUT/'output'/f['file']).read_bytes()) == {k:f[k] for k in ('bytes','sha256')}
    fact = next(r for r in github['anonymous_readback'] if r['file'] == f['file'])
    zfact = next(r for r in zenodo['public_readback'] if r['file'] == f['file'])
    for r in (fact,zfact):
        assert all(r[k] == f[k] for k in ('bytes','sha256'))
        public.append(r)
    rows.append({'courseId':'A00','id':'A00:id-format-'+['pdf','tex','source','epub'][i],
        'href':fact['url'], 'labels':{lang:labels[lang][i] for lang in labels},
        'notes':notes, 'kind':['companion','editable_source','source_archive','companion'][i],
        'format':['PDF','TEX','ZIP','EPUB'][i], 'offlineAfterDownload':i in (0,3),
        'evidenceFile':'docs/interface/evidence/a00-portable-formats.json',
        'contentLanguage':'id','bytes':f['bytes'],'sha256':f['sha256']})
record_url = 'https://zenodo.org/records/23149334'
record_identity_path=OUT/'ZENODO_RECORD_PAGE_IDENTITY.json'
if record_identity_path.exists():
    record_fact=read(record_identity_path)
    assert record_fact['url']==record_url
else:
    response=requests.get(record_url,timeout=(15,45))
    assert response.status_code==200
    record_fact={'url':record_url,**identity(response.content),'readback_at':datetime.now(timezone.utc).isoformat()}
    record_identity_path.write_text(json.dumps(record_fact,indent=2)+'\n',encoding='utf-8')
public.append(record_fact)
rows.append({'courseId':'A00','id':'A00:id-format-record','href':record_url,
    'labels':{'id':'Arsip Zenodo — edisi format Bahasa Indonesia','en':'Zenodo archive — Indonesian format edition'},
    'notes':notes,'kind':'companion','format':'HTML','offlineAfterDownload':False,
    'evidenceFile':'docs/interface/evidence/a00-portable-formats.json','contentLanguage':'id',
    'bytes':record_fact['bytes'],'sha256':record_fact['sha256']})
target = ROOT / 'docs/interface/supplemental-readers.js'
text = target.read_text(encoding='utf-8')
start,end = '  // BEGIN A00 FORMAT PAIRS\n','  // END A00 FORMAT PAIRS\n'
block = start + ',\n'.join('  '+json.dumps(r,ensure_ascii=False,indent=2).replace('\n','\n  ') for r in rows)+',\n'+end
if start in text:
    a=text.index(start);b=text.index(end,a)+len(end);text=text[:a]+block+text[b:]
else:
    assert text.count('export const supplementalReaders = [\n')==1
    text=text.replace('export const supplementalReaders = [\n','export const supplementalReaders = [\n'+block,1)
target.write_text(text,encoding='utf-8',newline='\n')
proof = {'schema':'central-supplemental-reader-evidence/1','course_id':'A00',
    'status':'published_and_anonymously_verified','content_language':'id',
    'edition':final['editions']['id'], 'public_readback':public,
    'preservation':{'url':record_url,'doi':zenodo['doi'],'preview':zenodo['preview'],
        'file_order':zenodo['rendered_file_order_verified'],'original_records_unchanged':True,
        'all_files_anonymously_hash_verified':True},
    'checks':{'source_archive_files_verified':final['source_archive_files_verified'],
        'pdf_and_epub_byte_identical_rebuild':True,'epubcheck':final['epubcheck']},
    'source_model':'CNXML/MathML remains the native master; LaTeX is the corresponding editable print export.',
    'scope':'Indonesian A00 format links only. No English translation, native replacement, mathematical review or whole-program completion.',
    'provenance':{'original_authors':['Lynn Marecek','MaryAnne Anthony-Smith','Andrea Honeycutt Mathis'],
        'original_publisher':'OpenStax','translation':{'model':'gpt-5.6-sol','effort':'ultra'},
        'format_and_integration':{'model':'gpt-6-astra','effort':'ultra'}},
    'evidence_receipts':{p:identity((OUT/p).read_bytes()) for p in ['FINAL_FORMAT_VALIDATION.json','GITHUB_FORMAT_PUBLICATION.json','ZENODO_FORMAT_PUBLICATION.json']}}
(ROOT/'docs/interface/evidence/a00-portable-formats.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'state':'integrated','links':len(rows),'paired_downloads':len(files)}))
