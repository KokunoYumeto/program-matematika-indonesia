"""Build bilingual A10 learning/teaching navigation from exact native metadata."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from a10_capability_model_v1 import ADAPTER, NATIVE, ROOT, INPUTS, derive_projection, json_bytes, sha
from a10_html_routes_v1 import attach_html_routes

STYLE = """
:root{color-scheme:light;--ink:#172d36;--muted:#53666d;--paper:#f3f0e7;--card:#fff;--line:#cad3d5;--accent:#086d78}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:1rem/1.55 system-ui,Segoe UI,sans-serif}main{max-width:1160px;margin:auto;padding:24px 20px 64px}a{color:var(--accent);text-underline-offset:3px}nav,.controls,.pagination{display:flex;flex-wrap:wrap;gap:1rem;align-items:end}nav{margin-bottom:1rem}h1{font-size:clamp(2rem,5vw,3rem);line-height:1.1}h2{margin-top:2rem}.lede{max-width:78ch}.panel,details{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:1rem 0}.muted{color:var(--muted)}label{display:block}select,input,button{font:inherit;padding:.6rem;border:1px solid var(--line);border-radius:5px;max-width:100%;background:#fff;color:var(--ink)}button{cursor:pointer}button:disabled{opacity:.5;cursor:default}summary{cursor:pointer;font-weight:650}code{font-size:.875rem;overflow-wrap:anywhere}ul{padding-left:1.4rem}li{margin:1rem 0}li details{margin:.5rem 0}details p{margin:.5rem 0}.badge{display:inline-block;margin-left:.7rem;font-size:.875rem;color:var(--muted)}:focus-visible{outline:3px solid #d58a25;outline-offset:3px}.skip{position:absolute;left:-10000px}.skip:focus{left:1rem;top:1rem;background:white;padding:1rem}.module-item{border-top:1px solid var(--line);padding-top:.75rem}.controls>div{min-width:180px;flex:1}input[type=checkbox]{width:1.2rem;height:1.2rem;vertical-align:middle}.warning{border-left:5px solid #9d542c;padding-left:1rem}.pagination{align-items:center}.governance{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:1rem}
""".strip()

COPY = {
    "id": {"title":"Aljabar Elementer", "learner":"Pelajar", "teacher":"Pengajar", "program":"Kembali ke program", "english":"Buku sumber bahasa Inggris", "reader":"Baca PDF Bahasa Indonesia", "module":"Modul", "filter":"Cakupan solusi", "all":"Semua latihan", "provided":"Solusi tersedia pada sumber", "notProvided":"Solusi tidak disediakan sumber", "search":"Cari ID latihan atau sumber", "previous":"Sebelumnya", "next":"Berikutnya", "exercise":"Latihan", "exercises":"latihan", "problem":"Soal", "solution":"Solusi", "source":"Sumber", "sourceOrder":"Urutan sumber", "page":"hlm.", "identities":"Identitas soal dan solusi", "empty":"Tidak ada latihan yang cocok.", "curated":"Pilihan istilah dalam buku", "occurrence":"Kemunculan sumber, bukan keputusan terjemahan", "refine":"Gunakan pencarian untuk mempersempit daftar", "mapOnly":"Rekonsiliasi peta", "correctionState":"Status dari catatan sumber", "selectFirst":"Pilih setidaknya satu modul.", "selectionReady":"Pilihan modul diunduh. Isi buku tetap pada edisi sumber.", "intro":"Pilih modul dan temukan latihan dengan atau tanpa solusi yang disediakan sumber. Tautan PDF membuka awal modul; daftar ini tidak menyediakan kunci jawaban baru.", "boundary":"Nomor urutan di sini mengikuti posisi latihan dalam sumber, bukan nomor soal tercetak. Keberadaan identitas solusi tidak membuktikan tautan langsung ke halaman solusi.", "modules":"Daftar modul", "terms":"Istilah dan bukti sumber", "termSearch":"Cari istilah", "corrections":"Catatan koreksi modul", "select":"Pilih modul untuk dipakai kembali", "download":"Unduh pilihan modul", "selectionNote":"Unduhan berisi identitas, urutan, cakupan solusi, tautan, dan hash sumber. Ini bukan salinan buku atau silabus baru.", "governanceNote":"Catatan teknis mempertahankan status sumber, termasuk keputusan istilah dan hak per komponen. Tampilan ini bukan panduan guru resmi. Unduh indeks lengkap di bawah untuk semua rekaman.", "indices":"Indeks lengkap dan asal-usul", "offline":"Navigasi dan pencarian tersedia dalam halaman ini. Membuka atau mengunduh buku memerlukan jaringan; PDF yang telah diunduh dapat dibaca luring.", "noscript":"Pencarian memerlukan JavaScript. Daftar modul dan tautan buku di bawah tetap dapat digunakan.", "skip":"Langsung ke pemilih modul"},
    "en": {"title":"Elementary Algebra", "learner":"Learner", "teacher":"Educator", "program":"Back to the program", "english":"Original English textbook", "reader":"Read the Indonesian PDF", "module":"Module", "filter":"Solution coverage", "all":"All exercises", "provided":"Solution supplied upstream", "notProvided":"No solution supplied upstream", "search":"Find an exercise or source ID", "previous":"Previous", "next":"Next", "exercise":"Exercise", "exercises":"exercises", "problem":"Problem", "solution":"Solution", "source":"Source", "sourceOrder":"Source-order position", "page":"page", "identities":"Problem and solution identities", "empty":"No matching exercises.", "curated":"Book terminology decision", "occurrence":"Source occurrence, not a translation decision", "refine":"Use search to narrow the list", "mapOnly":"Map reconciliation", "correctionState":"Native correction status", "selectFirst":"Select at least one module.", "selectionReady":"Module selection downloaded. Book text remains in its source edition.", "intro":"Choose a module and find exercises with or without supplied solutions. PDF links open the start of a module; this index does not create an answer key.", "boundary":"Positions here follow exercise order in the source, not printed exercise numbers. A solution identity does not establish a direct link to its PDF page.", "modules":"Module list", "terms":"Terminology and source evidence", "termSearch":"Find a term", "corrections":"Module correction records", "select":"Select modules for reuse", "download":"Download module selection", "selectionNote":"The download contains identities, ordering, solution coverage, links and source hashes. It is not a copy of the book or a new syllabus.", "governanceNote":"Technical records retain native statuses, terminology decisions and component-scoped rights. This is not an official teacher manual. Complete indexes are available below.", "indices":"Complete indexes and provenance", "offline":"Navigation and search are contained in this page. Opening or downloading books requires a connection; downloaded PDFs can be read offline.", "noscript":"Search needs JavaScript. The module list and textbook links below remain available.", "skip":"Skip to module selection"}}


COPY['id']['superseded'] = 'Istilah historis; telah digantikan oleh'
COPY['en']['superseded'] = 'Historical term; superseded by'
COPY['id'].update(htmlReader='Baca HTML Bahasa Indonesia', readExercise='Baca latihan', readProblem='Baca soal', readSolution='Baca solusi',
    intro='Pilih modul, buka latihan dan solusi sumber langsung dalam buku HTML Bahasa Indonesia, atau gunakan PDF. Tidak ada kunci jawaban baru yang ditambahkan.',
    boundary='Nomor urutan mengikuti posisi dalam sumber, bukan nomor soal tercetak. Tautan HTML menuju butir yang tepat; tautan PDF membuka awal modul.')
COPY['en'].update(htmlReader='Read the Indonesian HTML', readExercise='Read exercise', readProblem='Read problem', readSolution='Read solution',
    intro='Choose a module and open exercises and supplied solutions directly in the Indonesian HTML textbook, or use the PDF. This navigator does not create an answer key.',
    boundary='Positions follow source order, not printed exercise numbers. HTML links open exact items; PDF links open the start of a module.')


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def consumer_data(bundle: dict, language: str) -> dict:
    keys = "id module_id source_element_id problem_id solution_id solution_status ordinal_within_module exercise_html_url problem_html_url solution_html_url".split()
    def display_title(row):
        label=row['label']
        title=row['title_en'] if language=='en' else row['title']
        if language=='en':
            label='Preface' if label=='Prakata' else label.replace('Bab ','Chapter ',1)
        return label if label==title else label+' · '+title
    return {"schema":"a10-navigator-data/1", "locale":language, "labels":COPY[language],
        "edition_id":bundle["native_record_ledger"]["stable_identifiers"]["edition_id"],
        "native_release_sha256":INPUTS["backend-core.zip"]["sha256"], "pdf_sha256":INPUTS["reader.pdf"]["sha256"],
        "html_reader":bundle['html_route_evidence'],
        "modules":[{**row,"display_title":display_title(row)} for row in bundle["module_index"]],
        "exercises":[{key:row[key] for key in keys} for row in bundle["exercise_index"]],
        "terms":bundle["terms_index"], "corrections":bundle["corrections_index"]}


def render(bundle: dict, language: str, educator: bool) -> str:
    text = COPY[language]; data = consumer_data(bundle,language)
    suffix = "-en" if language=="en" else ""
    other_suffix = "" if suffix else "-en"
    title = text["title"]+" · "+text["teacher" if educator else "learner"]
    separator='.' if language=='id' else ','
    selected = next(row["module_id"] for row in data["modules"] if row["exercise_count"])
    options = "".join(f'<option value="{m["module_id"]}"'+(' selected' if m['module_id']==selected else '')+f'>{esc(m["display_title"])}</option>' for m in data["modules"])
    items = []
    for module in data["modules"]:
        check = f'<label><input type="checkbox" name="selected-module" value="{module["module_id"]}"> {esc(module["display_title"])}</label>' if educator else f'<strong>{esc(module["display_title"])}</strong>'
        items.append(f'<li class="module-item">{check} · <a href="{esc(module["html_url"])}" lang="id">HTML (id)</a> · <a href="{esc(module["url"])}">PDF (id), {text["page"]} {module["physical_page"]}</a><br>{module["exercise_count"]} {text["exercises"]} · {module["solution_count"]} {text["provided"]} · <code>{module["module_id"]}</code></li>')
    governance = ""
    if educator:
        governance = f'''<h2>{text['terms']}</h2><p>{text['governanceNote']}</p><div class="governance"><section class="panel"><label for="term-query">{text['termSearch']}</label><input id="term-query" type="search"><p id="term-count" role="status"></p><ul id="terms"></ul></section><section class="panel"><h3>{text['corrections']} (<span id="correction-count"></span>)</h3><ul id="corrections"></ul></section></div>'''
    selection = f'<p>{text["selectionNote"]}</p><button id="download-selection" type="button">{text["download"]}</button><p id="selection-status" role="status"></p>' if educator else ''
    index_links = "".join(f'<li><a href="../data/{name}-index.jsonl">{label}</a></li>' for name,label in [('exercise',text['exercises']),('terms',text['terms']),('corrections',text['corrections']),('rights','Hak per komponen / component rights'),('translation','Catatan terjemahan / translation ledger'),('concept','Konsep / concepts')])
    js = (ROOT/'scripts/a10_navigator_v1.js').read_text(encoding='utf-8')
    embedded = json_bytes(data).decode().replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return f'''<!doctype html><html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>A10 · {esc(title)}</title><style>{STYLE}</style></head><body><a class="skip" href="#module">{text['skip']}</a><main>
<nav aria-label="A10"><a href="https://kokunoyumeto.github.io/program-matematika-indonesia/">{text['program']}</a><a href="A10{suffix}.html">{text['learner']}</a><a href="A10-pengajar{suffix}.html">{text['teacher']}</a><a href="A10{'-pengajar' if educator else ''}{other_suffix}.html" lang="{'id' if language=='en' else 'en'}">{'Bahasa Indonesia' if language=='en' else 'English'}</a></nav>
<h1>A10 · {esc(title)}</h1><p class="lede">{text['intro']}</p>
<p>82 {text['module'].lower()} · 9{separator}406 {text['exercises']} · 6{separator}106 {text['provided']}</p>
<p><a href="{esc(bundle['english_source_mirror']['program_mirror']['reader_url'])}" lang="en">{text['english']}</a> · <a href="{esc(INPUTS['reader.pdf']['url'])}" lang="id">{text['reader']}</a></p>
<section class="panel" aria-label="{text['module']}"><div class="controls"><div><label for="module">{text['module']}</label><select id="module">{options}</select></div><div><label for="availability">{text['filter']}</label><select id="availability"><option value="all">{text['all']}</option><option value="provided">{text['provided']}</option><option value="missing">{text['notProvided']}</option></select></div><div><label for="query">{text['search']}</label><input id="query" type="search"></div></div>
<p id="module-summary"></p><p><a id="module-html-reader" href="{esc(next(m['html_url'] for m in data['modules'] if m['module_id']==selected))}" lang="id">{text['htmlReader']}</a> · <a id="module-reader" href="{esc(next(m['url'] for m in data['modules'] if m['module_id']==selected))}">{text['reader']}</a></p><p class="warning">{text['boundary']}</p><p id="result-count" role="status"></p><ul id="exercises"></ul><div class="pagination"><button type="button" id="previous">{text['previous']}</button><button type="button" id="next">{text['next']}</button></div><noscript><p>{text['noscript']}</p></noscript></section>
{governance}<h2>{text['select'] if educator else text['modules']}</h2>{selection}<details><summary>82 {text['modules'].lower()}</summary><ol>{''.join(items)}</ol></details>
<details><summary>{text['indices']}</summary><ul>{index_links}<li><a href="capabilities.json">Capabilities</a></li><li><a href="claim-boundary.json">Scope and limitations</a></li><li><a href="../validation.json">Validation</a></li></ul></details><p class="muted">{text['offline']}</p>
</main><script type="application/json" id="a10-data">{embedded}</script><script>{js}</script></body></html>\n'''


def build(native: Path=NATIVE, destination: Path=ADAPTER) -> dict:
    bundle = attach_html_routes(derive_projection(native))
    bundle['learning_map'] = {'schema':'a10-learning-map/1','course_id':'A10','counts':bundle['capabilities']['counts'],
        'modules':bundle['module_index'],'exercise_index':'data/exercise-index.jsonl',
        'view_languages':['id','en'],'reading_routes_are_module_start_only':False,
        'pdf_routes_are_module_start_only':True,'html_routes_are_exact_items':True,
        'html_route_evidence':'data/html-route-evidence.json',
        'native_edition_id':bundle['native_record_ledger']['stable_identifiers']['edition_id']}
    files = {}
    for key,value in bundle.items():
        filename = key.replace('_','-')
        if key.endswith('_index'):
            files['data/'+filename+'.jsonl'] = b''.join(json_bytes(row) for row in value)
        else:
            files[('input/' if key=='source_lock' else 'data/')+filename+'.json'] = json_bytes(value)
    for language in ('id','en'):
        suffix = '-en' if language=='en' else ''
        files[f'views/A10{suffix}.html'] = render(bundle,language,False).encode('utf-8')
        files[f'views/A10-pengajar{suffix}.html'] = render(bundle,language,True).encode('utf-8')
    for name in ('capabilities','claim-boundary'):
        files['views/'+name+'.json'] = files['data/'+name+'.json']
    files['README.md'] = ("# A10 native learning capability\n\n"
        "Metadata-only projection of the pinned complete A10 native release. The navigator exposes 82 module PDF routes, "
        "9,406 ordered exercise/problem identities, 6,106 supplied solutions and 3,300 explicit source-solution gaps. "
        "Indonesian and English interfaces share the same identity model; the English book link preserves the existing original-source mirror.\n\n"
        "All 19 native JSONL streams are independently hash/count/ID checked during construction. Native bodies and historical "
        "translation payloads remain in the original public package. Raw IDs must be scoped by module. Module-start links "
        "are not PDF exercise/solution links. Four PDF exercise declarations exist but no PDF exercise route is claimed verified. "
        "Separate HTML evidence binds all 82 module, 9,406 exercise/problem and 6,106 supplied solution destinations "
        "to exact module-scoped IDs in the existing Indonesian reader. The English interface does not relabel Indonesian content.\n\n"
        "The educator selection is a portable identity manifest, not an official manual or a new syllabus. "
        "Curated terminology and source occurrences remain different evidence classes. Component rights and correction states are retained.\n").encode()
    for name,content in files.items():
        path=destination/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
    manifest={"schema":"a10-capability-manifest/1","course_id":"A10","contract":"course-learning-capability/1",
        "counts":bundle['capabilities']['counts'],"input_lock":bundle['source_lock'],
        "generators":[{'path':'scripts/'+name,'bytes':(ROOT/'scripts'/name).stat().st_size,'sha256':sha((ROOT/'scripts'/name).read_bytes())}
            for name in ['acquire_a10_capability_inputs_v1.py','a10_capability_model_v1.py','a10_html_routes_v1.py','central_surface_navigation_overlay_v1.py','build_a10_capability_v1.py','a10_navigator_v1.js']],
        "outputs":[{"path":name,"bytes":len(content),"sha256":sha(content)} for name,content in sorted(files.items())],
        "validation_path":"validation.json","consumer_views":[f'views/A10{suffix}.html' for suffix in ('','-en','-pengajar','-pengajar-en')]}
    (destination/'manifest.json').write_bytes(json_bytes(manifest))
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native',type=Path,default=NATIVE)
    parser.add_argument('--destination',type=Path,default=ADAPTER)
    args=parser.parse_args()
    manifest=build(args.native,args.destination)
    print(json.dumps({'state':'built_not_yet_independently_validated','counts':manifest['counts'],'outputs':len(manifest['outputs'])}))
