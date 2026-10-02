"""Preserve and render one source-bound prerequisite bridge; never edit its producer."""
from pathlib import Path
import hashlib
import html
import io
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'backend/cross-programme-v1/providers/b40-basis-projection-r2'
PUBLIC = ROOT / 'docs/en/readers/basis-projection-bridge'
PINS = {
    'from-bases-to-projections-r2.md': '131f01c7611a96c60a0dfdaf08c7b17e0f1a864dd371968ecd858b19f4e49652',
    'ADAPTATION_R2.json': 'f37193aa82ce900393c210e2a9da3d90b8bcc7f0b6e86bab2de847b58741c609',
    'HEFFERON-PROOFS.tex': 'e5fa2ab9aecd831eeca4e1d30e3b4f6d39a7700925be18eed36ad039394c8480',
    'HEFFERON-LICENSE.txt': '45e69a5115ce82fb4566271045b1777d4c506929f866fa12c2ca0ef9b23bb140',
    'HEFFERON-ACKNOWLEDGEMENTS.txt': '318c43872901d4ed822778be6ee3b36f0332b968b8bac84b63d56c027f07174b',
    'SOURCE_BINDINGS.json': '8e7a223707e59b43198c4d7bfe88bfd86cdea8491ae64af9197947373f1f0024',
}
CONSUMER = 'https://kokunoyumeto.github.io/open-mathematics-courses/courses/RT-FIN/representations-and-complete-reducibility.html'
sha = lambda value: hashlib.sha256(value).hexdigest()
encode = lambda value: (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
if '--intake' in sys.argv:
    native = ROOT.parents[2] / 'kerodon_to_stacks_extension_20260906/reader/course_inputs/CORE-B40-PROOFS-20261002'
    SOURCE.mkdir(parents=True, exist_ok=True)
    for name, expected in PINS.items():
        value = (native / name).read_bytes()
        assert sha(value) == expected, name
        if (SOURCE / name).exists():
            assert (SOURCE / name).read_bytes() == value, name
        else:
            with (SOURCE / name).open('xb') as stream:
                stream.write(value)
inputs = {name: (SOURCE / name).read_bytes() for name in PINS}
assert all(sha(value) == PINS[name] for name, value in inputs.items())
pandoc = os.environ.get('PANDOC') or shutil.which('pandoc')
assert pandoc, 'Use an existing Pandoc installation; do not install during replay'
def convert(value, *args):
    result = subprocess.run([pandoc, *args], input=value, capture_output=True, check=True, timeout=30)
    assert not result.stderr.strip(), result.stderr.decode(errors='replace')
    return result.stdout.replace(b'\r\n', b'\n')
ast = json.loads(convert(inputs['from-bases-to-projections-r2.md'], '-f', 'markdown+tex_math_single_backslash', '-t', 'json'))
def nodes(value):
    if isinstance(value, dict):
        if 't' in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)
math = [n['c'][1].strip() for n in nodes(ast) if n['t'] == 'Math']
assert len(math) > 100
resolved_links = 0
for node in nodes(ast):
    if node['t'] == 'Link' and node['c'][-1][0].startswith('course:'):
        assert node['c'][-1][0] == 'course:RT-FIN/representations-and-complete-reducibility'
        node['c'][-1][0] = CONSUMER
        resolved_links += 1
assert resolved_links == 1
ast_bytes = encode(ast)
fragment = convert(ast_bytes, '-f', 'json', '-t', 'html5', '--mathml').decode()
annotations = re.findall(r'<annotation encoding="application/x-tex">(.*?)</annotation>', fragment, re.S)
assert [html.unescape(v).strip() for v in annotations] == math, 'Every HTML formula must preserve its source TeX'
tex = convert(ast_bytes, '-f', 'json', '-t', 'latex', '--standalone', '--metadata=lang:en', '--metadata=title:From bases to projections')
tex_ast = json.loads(convert(tex, '-f', 'latex', '-t', 'json'))
assert [n['c'][1].strip() for n in nodes(tex_ast) if n['t'] == 'Math'] == math, 'Direct LaTeX must preserve every formula'
style = 'body{max-width:54rem;margin:auto;padding:1rem;font:18px/1.65 system-ui;color:#172338;background:#fbfcfe}a{color:#075aaa}nav{display:flex;flex-wrap:wrap;gap:1rem}math[display="block"]{display:block;overflow-x:auto;margin:1rem 0}p,li{overflow-wrap:anywhere}code{overflow-wrap:anywhere}h2{margin-top:2rem}aside{padding:1rem;border:1px solid #cbd8e5;border-radius:.6rem}'
programme = 'https://kokunoyumeto.github.io/program-matematika-indonesia/'
nav = '<nav aria-label="Programme navigation"><a href="'+programme+'en/programme/#core-B40">Linear-algebra foundation</a><a href="'+programme+'en/programme/#advanced-RT-FIN">Representation theory</a><a href="'+programme+'id/programme/#core-B40" hreflang="id">Bahasa Indonesia — peta program</a></nav>'
download = '<aside><h2>Read, edit and reuse</h2><p>This English-only bridge supplies one finite-dimensional prerequisite, not the full linear-algebra or representation-theory course. The complex Hermitian prerequisite is separate and remains unverified in this integration.</p><ol><li><a href="00-basis-projection.tex">Complete editable LaTeX</a></li><li><a href="01-editable-source.zip">Complete source and reproducible build ZIP</a></li><li><a href="from-bases-to-projections-r2.md">Unchanged native Markdown</a></li></ol><p>HTML-only reading edition with native MathML; no PDF is claimed. The source licence and exact AI attribution are retained below.</p></aside>'
page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>From bases to projections — prerequisite bridge</title><style>' + style + '</style></head><body>' + nav + download + '<main id="proof-body">' + fragment + '</main>' + nav + '</body></html>\n').encode()
assert b'course:' not in page and b'<script' not in page
PUBLIC.mkdir(parents=True, exist_ok=True)
outputs = {**inputs, '00-basis-projection.tex': tex, 'index.html': page}
readme = '''# From bases to projections — source-preserving reading edition

CC BY-SA 2.5. Jim Hefferon's exact source grant, acknowledgements and selected
proofs accompany the unchanged r2 adaptation. The adaptation identifies its
actual authoring model: OpenAI GPT-6 Astra in Codex, Ultra reasoning effort.
Rendering and programme integration: OpenAI Codex GPT-6 Astra, Ultra effort.
No human or independent proof audit is claimed. This is a finite-dimensional
prerequisite bridge, not closure of the entire representation-theory course.

Use Python 3 and the Pandoc version recorded in BUILD_INPUTS.json. From the
extracted root run: python -B scripts/build-b40-proof-bridge-v1.py
No network, external source tree, TeX engine or PDF is needed for this build.
The direct cumulative LaTeX contains the complete lesson; it uses the standard
packages declared in its preamble. Its compilation was not part of this HTML
build. Every formula is checked against both MathML annotations and parsed LaTeX.
Only the one course: link is resolved for delivery; original Markdown is retained.
'''.encode()
outputs['README.md'] = readme
outputs['BUILD_INPUTS.json'] = encode({'pandoc': subprocess.check_output([pandoc, '--version'], text=True).splitlines()[0], 'source_sha256': PINS, 'newline_policy': 'Generated text uses LF; native source bytes remain unchanged.'})
for name, value in outputs.items():
    (PUBLIC / name).write_bytes(value)
archive = io.BytesIO()
members = {str(Path(__file__).relative_to(ROOT)).replace('\\', '/'): Path(__file__).read_bytes()}
members.update({(SOURCE / name).relative_to(ROOT).as_posix(): value for name, value in inputs.items()})
members.update({(PUBLIC / name).relative_to(ROOT).as_posix(): value for name, value in outputs.items()})
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
    for name, value in sorted(members.items()):
        info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        bundle.writestr(info, value)
outputs['01-editable-source.zip'] = archive.getvalue()
(PUBLIC / '01-editable-source.zip').write_bytes(outputs['01-editable-source.zip'])
receipt = {'schema': 'b40-basis-projection-reader/1', 'state': 'local_rendering_pass', 'language': 'en', 'native_course': 'CORE-B40', 'programme_course': 'B40', 'source_sha256': PINS['from-bases-to-projections-r2.md'], 'licence': 'CC-BY-SA-2.5', 'formula_count': len(math), 'html_mathml_source_tex_exact': True, 'direct_latex_formula_replay_exact': True, 'resolved_course_links': resolved_links, 'whole_course_verified': False, 'hermitian_dependency_closed': False, 'independent_proof_review': False, 'public_byte_readback': False, 'pdf_exception': 'HTML-only with native MathML, direct complete LaTeX and full source ZIP', 'pandoc': subprocess.check_output([pandoc, '--version'], text=True).splitlines()[0], 'files': [{'path': name, 'bytes': len(value), 'sha256': sha(value)} for name, value in outputs.items()]}
(PUBLIC / 'READER_MANIFEST.json').write_bytes(encode(receipt))
print(json.dumps({'state': receipt['state'], 'formulas': len(math), 'source_files': len(inputs), 'archive_members': len(members)}))
