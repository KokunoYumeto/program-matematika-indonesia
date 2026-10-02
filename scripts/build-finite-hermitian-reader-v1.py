"""Build one elementary prerequisite reader without editing native textbooks."""
from pathlib import Path
import hashlib, html, io, json, os, re, shutil, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'backend/cross-programme-v1/providers/finite-hermitian-r1'
PUBLIC = ROOT / 'docs/en/readers/finite-hermitian-spaces'
sha = lambda value: hashlib.sha256(value).hexdigest()
encode = lambda value: (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode()
pandoc = os.environ.get('PANDOC') or shutil.which('pandoc')
assert pandoc, 'Use the existing Pandoc installation'
inputs = {name: (SOURCE/name).read_bytes() for name in ['finite-hermitian-spaces.md', 'SOURCE_REVIEW.json']}
review = json.loads(inputs['SOURCE_REVIEW.json'])
assert sha(inputs['finite-hermitian-spaces.md']) == review['lesson_sha256']
assert review['verdict'] == 'proved as written; bounded author-instance self-review'
assert review['whole_course_verified'] is False

def convert(value, *args):
    proc = subprocess.run([pandoc, *args], input=value, capture_output=True, check=True, timeout=30)
    assert not proc.stderr.strip(), proc.stderr.decode(errors='replace')
    return proc.stdout.replace(b'\r\n', b'\n')

def nodes(value):
    if isinstance(value, dict):
        if 't' in value: yield value
        for child in value.values(): yield from nodes(child)
    elif isinstance(value, list):
        for child in value: yield from nodes(child)

ast = json.loads(convert(inputs['finite-hermitian-spaces.md'], '-f', 'markdown+tex_math_single_backslash', '-t', 'json'))
formulas = [node['c'][1].strip() for node in nodes(ast) if node['t']=='Math']
assert len(formulas) > 80
fragment = convert(encode(ast), '-f', 'json', '-t', 'html5', '--mathml').decode()
annotations = re.findall(r'<annotation encoding="application/x-tex">(.*?)</annotation>', fragment, re.S)
assert [html.unescape(value).strip() for value in annotations] == formulas
tex = convert(encode(ast), '-f', 'json', '-t', 'latex', '--standalone', '--metadata=lang:en', '--metadata=title:Orthonormal bases and orthogonal projections')
reparsed = json.loads(convert(tex, '-f', 'latex', '-t', 'json'))
assert [node['c'][1].strip() for node in nodes(reparsed) if node['t']=='Math'] == formulas
origin = 'https://kokunoyumeto.github.io/program-matematika-indonesia/'
nav = '<nav aria-label="Programme navigation"><a href="'+origin+'en/programme/#core-B40">Linear algebra</a><a href="'+origin+'en/programme/#advanced-RT-FIN">Representation theory</a><a href="'+origin+'id/programme/#core-B40" hreflang="id">Bahasa Indonesia — peta program</a></nav>'
style = 'body{max-width:54rem;margin:auto;padding:1rem;font:18px/1.65 system-ui;color:#172338;background:#fbfcfe}a{color:#075aaa}nav{display:flex;flex-wrap:wrap;gap:1rem}math[display="block"]{display:block;overflow-x:auto;margin:1rem 0}p,li,code{overflow-wrap:anywhere}h2{margin-top:2rem}aside{padding:1rem;border:1px solid #cbd8e5;border-radius:.6rem}'
downloads = '<aside><h2>Read, edit and reuse</h2><p>English prerequisite lesson, with complete proofs, examples and solutions. It supplies the two stated Hermitian uses in the representation-theory opening, not whole-course certification.</p><ol><li><a href="00-finite-hermitian.tex">Complete editable LaTeX</a></li><li><a href="01-editable-source.zip">Complete source and reproducible build ZIP</a></li><li><a href="finite-hermitian-spaces.md">Editable Markdown</a></li></ol><p>HTML reading edition with native MathML; no PDF is claimed. The source ZIP builds this lesson without network access. Earlier programme lessons are linked separately.</p></aside>'
assert fragment.count('</h1>') == 1
fragment = fragment.replace('</h1>', '</h1>'+downloads, 1)
page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Orthonormal bases and orthogonal projections</title><style>'+style+'</style></head><body>'+nav+'<main id="proof-body">'+fragment+'</main>'+nav+'</body></html>\n').encode()
assert b'<script' not in page
version = subprocess.check_output([pandoc, '--version'], text=True).splitlines()[0]
readme = '''# Orthonormal bases and orthogonal projections

CC BY-SA 4.0. Develops the Gram-Schmidt and decomposition statements in John M.
Erdman's Functional Analysis and Operator Algebras, 4 October 2015, Chapter 1.
Proofs, teaching and integration: OpenAI Codex GPT-6 Astra, Ultra effort.
Author-instance AI self-review only; no human or independent review claimed.

With Python 3 and the Pandoc version in BUILD_INPUTS.json, run from the extracted
root: python -B scripts/build-finite-hermitian-reader-v1.py
No network or TeX engine is needed. The cumulative LaTeX contains the full lesson
and declares its standard package dependencies. A TeX compile is not claimed.
Every formula is compared with the MathML annotations and parsed LaTeX.
Earlier programme lessons and scholarly references are separate online links.
'''.encode()
outputs = {**inputs, 'index.html':page, '00-finite-hermitian.tex':tex, 'README.md':readme,
           'BUILD_INPUTS.json':encode({'pandoc':version,'source_sha256':{name:sha(value) for name,value in inputs.items()}})}
PUBLIC.mkdir(parents=True, exist_ok=True)
for name,value in outputs.items(): (PUBLIC/name).write_bytes(value)
members = {Path(__file__).relative_to(ROOT).as_posix():Path(__file__).read_bytes()}
members.update({(SOURCE/name).relative_to(ROOT).as_posix():value for name,value in inputs.items()})
members.update({(PUBLIC/name).relative_to(ROOT).as_posix():value for name,value in outputs.items()})
archive=io.BytesIO()
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as bundle:
    for name,value in sorted(members.items()):
        info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
        bundle.writestr(info,value)
outputs['01-editable-source.zip']=archive.getvalue()
(PUBLIC/'01-editable-source.zip').write_bytes(archive.getvalue())
manifest={'schema':'finite-hermitian-reader/1','state':'local_rendering_pass','language':'en','licence':'CC-BY-SA-4.0',
          'source_sha256':review['lesson_sha256'],'formula_count':len(formulas),'mathml_formula_identity':True,
          'direct_latex_formula_identity':True,'proof_review':'author-instance self-review','independent_review':False,
          'whole_course_verified':False,'public_byte_readback':False,'pdf_exception':'HTML/MathML reader with direct cumulative LaTeX and complete source ZIP',
          'files':[{'path':name,'bytes':len(value),'sha256':sha(value)} for name,value in outputs.items()]}
(PUBLIC/'READER_MANIFEST.json').write_bytes(encode(manifest))
print(json.dumps({'state':manifest['state'],'formulas':len(formulas),'archive_members':len(members)}))
