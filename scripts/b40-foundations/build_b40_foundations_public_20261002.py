"""Freeze and export the six source-bound English foundation readers.

No owner edits, TeX execution, network requests or publication. The public
projection preserves every existing main-body byte, source note and native ID.
Frozen Pandoc AST/MathML/SVG inputs reproduce the six existing readers first.
"""
import argparse
import copy
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import zipfile

BASE = Path(__file__).resolve().parent.parent
B40_REL = Path('reader_mirrors/hefferon-original-en-20260909')
SECTIONS = ['gr1', 'gr3', 'vs1', 'vs2', 'vs3', 'fields']
TITLES = dict(zip(SECTIONS, ['Solving Linear Systems', 'Reduced Echelon Form', 'Vector Spaces', 'Linear Independence', 'Basis and Dimension', 'Fields']))
FILES = dict(zip(SECTIONS, ['src/gr/gr1.tex', 'src/gr/gr3.tex', 'src/vs/vs1.tex', 'src/vs/vs2.tex', 'src/vs/vs3.tex', 'src/vs/fields.tex']))
NOTES = {'vs1': 'VS1_MATHEMATICAL_REPLAY.json', 'vs2': 'VS2_MATHEMATICAL_REPLAY.json', 'vs3': 'VS3_MATHEMATICAL_REPLAY.json', 'fields': 'FIELDS_SOURCE_NOTES.json'}
ORIGIN = 'https://kokunoyumeto.github.io/program-matematika-indonesia/'
SOURCE_URL = 'https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/b40-foundations-2026.10.02/COMPLETE_SOURCE.zip'
REVISION = 'df2262e089a02651c127f1dd12649c4622ee1383'
ARCHIVE_SHA = 'b409fc82a8323578e71d8095b9ab4bc9ca814d5a0d9cc6d125dd6b4d81dc23d0'
REFRESH = False


def sha(b):
    return hashlib.sha256(b).hexdigest()


def jb(o):
    return (json.dumps(o, ensure_ascii=False, indent=2) + '\n').encode()


def fact(path, b):
    return {'path': str(path).replace('\\', '/'), 'bytes': len(b), 'sha256': sha(b)}


def write(path, data, check=False):
    if check:
        assert path.read_bytes() == data, 'byte replay mismatch: ' + str(path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            assert REFRESH, 'refuse changed sealed file: ' + str(path)
            path.write_bytes(data)
    else:
        with path.open('xb') as f:
            f.write(data)


def safe(root, rel):
    p = (root / rel).resolve()
    assert p.is_relative_to(root.resolve())
    return p


def freeze(destination):
    originals = {}
    def add(rel, source=None):
        data = (source or (BASE / rel)).read_bytes()
        originals[str(rel).replace('\\', '/')] = data
    for s in SECTIONS:
        directory = B40_REL / ('semantic-pilot-' + s)
        names = [s+'.semantic.json', 'math-source-index.json', 'mathml-regions.json', 'MATH_RENDER_REPORT.json', 'MATH_RENDER_CONFIG.json', s+'.reader-pilot.html', 'rendered-unit-index.json', 'SEMANTIC_PILOT_REPORT.json', 'PRESENTATION_BINDINGS.json', 'PROSE_LEXICAL_REPLAY.json']
        if s in ('gr1', 'gr3'):
            names.append('FIGURE_CONVERSION_RECEIPT.json')
            receipt = json.loads((BASE / directory / names[-1]).read_bytes())
            names.extend(r['output']['path'] for r in receipt['figures'])
        if s == 'vs1':
            names.append('RICH_CONTENT_CLOSURE.json')
            receipt = json.loads((BASE / directory / names[-1]).read_bytes())
            names.extend(r['output']['path'] for r in receipt['pictures'])
        if s in NOTES:
            names.append(NOTES[s])
        if s in ('vs3', 'fields'):
            names.append('RENDERED_CONTEXT_CONTRACT.json')
        for name in names:
            add(directory / name)
        add(B40_REL / 'authority' / FILES[s])
    for name in ['build_b40_reader_pilot_20260921.mjs', 'b40_det2_figure_descriptions_20261001.mjs', Path(__file__).name]:
        add(Path('curriculum_logbook') / name)
    add(B40_REL / 'authority/LICENSE')
    add(B40_REL / 'authority/README.md')
    add(B40_REL / 'source-intake/SOURCE_TREE_MANIFEST.json')
    provider = BASE / 'd100-capability-v1-worktree/backend/cross-programme-v1/provider-handoffs/B40-basis-extension-20261002'
    add(B40_REL / 'authority/Acknowledgements', provider / 'source/Acknowledgements')
    archive = BASE.parents[1] / '04_mirrors/id/hefferon-linear-algebra-id/authority/archives' / ('linear-algebra-'+REVISION+'.zip')
    data = archive.read_bytes()
    assert sha(data) == ARCHIVE_SHA and len(data) == 42547343
    originals['native-authority.zip'] = data
    for name, data in originals.items():
        existing = destination / name
        if existing.exists() and name != 'curriculum_logbook/' + Path(__file__).name:
            assert existing.read_bytes() == data, 'do not refresh frozen source authority: ' + name
        write(destination / name, data)
    write(destination / 'FROZEN_INPUTS.json', jb({'schema': 'b40-public-foundations-inputs/1', 'source_revision': REVISION, 'files': [fact(k, v) for k, v in sorted(originals.items())]}))


def load_and_replay(frozen):
    manifest = json.loads((frozen / 'FROZEN_INPUTS.json').read_bytes())
    for row in manifest['files']:
        b = safe(frozen, row['path']).read_bytes()
        assert len(b) == row['bytes'] and sha(b) == row['sha256'], row['path']
    results = []
    for section in SECTIONS:
        result = subprocess.run(['node', str(frozen / 'curriculum_logbook/build_b40_reader_pilot_20260921.mjs'), section, '--check-existing'], capture_output=True, timeout=90, check=True)
        assert not result.stderr
        results.append(json.loads(result.stdout))
    return manifest, results


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids = []; self.hrefs = []; self.remote_runtime = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a' and 'href' in a:
            self.hrefs.append(a['href'])
        if tag in ('script', 'iframe'):
            self.remote_runtime.append(tag)
        if tag in ('img', 'link'):
            url = a.get('src', a.get('href', ''))
            if url.startswith(('http:', 'https:', '//')):
                self.remote_runtime.append(url)


def main_part(b):
    m = re.search(rb'<main\b[^>]*>.*?</main>', b, re.S)
    assert m
    return m.start(), m.group()


def tex_escape(value):
    chars = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '%': r'\%', '#': r'\#', '&': r'\&', '_': r'\_', '$': r'\$', '^': r'\textasciicircum{}', '~': r'\textasciitilde{}'}
    return ''.join(chars.get(c, c) for c in value)


def export(frozen, public, check=False):
    manifest, replays = load_and_replay(frozen)
    b40 = frozen / B40_REL
    products = {}
    proofs = []
    original_indexes = {}
    note_tex = []
    cumulative_parts = []
    cumulative = r'''% Jim Hefferon, Linear Algebra, pinned source revision ''' + REVISION + r'''
% Selected foundation sections with all supplied answers in their native source.
% CC BY-SA 2.5 option; original component notices are in the full source ZIP.
% Assembly/public HTML rebuild: OpenAI Codex — GPT-6 Astra, Ultra effort.
% This is not an Everyday-English rewrite. No PDF or new TeX compilation is claimed.
% Extract native-authority.zip; put this file in the original src directory.
% Original styles, graphics, macros and make rules remain in that source archive.
% HTML byte replay uses the supplied frozen, editable Pandoc AST/MathML/SVG inputs.
\documentclass[twoside]{book}
\usepackage{verbatim}
\usepackage{xr}
\usepackage[single,write]{bookans}
\usepackage{bookjh}
% The bibliography remains a native dependency inside native-authority.zip.
\AtEndDocument{\input{bib/bib}}
\begin{document}
\mainmatter
\pagestyle{bookbody}
'''
    archive_url = SOURCE_URL
    for s in SECTIONS:
        d = b40 / ('semantic-pilot-' + s)
        original = (d / (s + '.reader-pilot.html')).read_bytes()
        old_start, body = main_part(original)
        text = original.decode('utf-8')
        new_notice = '<p class="notice"><strong>Original English by Jim Hefferon — selected foundation sections.</strong> The original mathematics and supplied answers below are preserved. This is a partial-book reading edition, not the complete book or an Everyday-English rewrite.</p>'
        text, n = re.subn(r'<p class="notice">.*?</p>', lambda m: new_notice, text, count=1, flags=re.S)
        assert n == 1
        text = text.replace(' — local conversion pilot', ' — selected foundations')
        text = text.replace('required for this local reading file.', 'required for this reading file.')
        navigation = '<nav aria-label="Foundation reader navigation"><a href="../index.html">Foundation contents</a> · <a href="'+ORIGIN+'en/programme/">Full mathematics programme</a> · <a href="../sources/00-foundations-cumulative.tex" download>Complete editable LaTeX</a> · <a href="'+SOURCE_URL+'" download>Full source and offline reader ZIP</a> · <a href="../sources/'+s+'.tex" download>This section’s original LaTeX</a></nav>'
        disclosure = '<p class="conversion-credit">Source-preserving rebuild, navigation, source packaging and current deterministic checks: OpenAI Codex — GPT-6 Astra, Ultra effort. Jim Hefferon remains the author of the mathematics. Earlier intermediate-conversion runtime identity is not established by its retained receipts and is not reassigned to this rebuild. No human review or exhaustive proof certification is claimed.</p>'
        text = text.replace('<header>', '<header>'+navigation, 1).replace('</header>', disclosure+'</header>', 1)
        text = text.replace('<footer>', '<footer>'+navigation, 1)
        text = text.replace('</style>', '.proof>p:first-child>em:first-child{margin-inline-end:.25em}\n</style>', 1)
        data = text.encode()
        start, new_body = main_part(data)
        assert body == new_body
        index = json.loads((d / 'rendered-unit-index.json').read_bytes())
        original_indexes[s] = index
        units, exercises = copy.deepcopy(index['units']), copy.deepcopy(index['exercises'])
        delta = start - old_start
        for unit in units:
            surface = unit['surface']
            surface['byte_start'] += delta; surface['byte_end'] += delta
            assert sha(data[surface['byte_start']:surface['byte_end']]) == surface['sha256']
            for fragment in unit['source_fragments']:
                src = (b40 / 'authority' / fragment['path']).read_bytes()
                assert sha(src[fragment['byte_start']:fragment['byte_end']]) == fragment['sha256']
        for exercise in exercises:
            for p in exercise['partition']:
                p['byte_start'] += delta; p['byte_end'] += delta
                assert sha(data[p['byte_start']:p['byte_end']]) == p['sha256']
        path = 'semantic-pilot-' + s + '/' + s + '.reader-pilot.html'
        products[path] = data
        products['semantic-pilot-' + s + '/original-rendered-unit-index.json'] = (d / 'rendered-unit-index.json').read_bytes()
        projection = {'schema': 'course-public-reader-export/1', 'language': 'en', 'source_revision': REVISION,
                      'reader': fact(s+'.reader-pilot.html', data),
                      'original_reader': index['reader'],
                      'original_index': fact('original-rendered-unit-index.json', (d / 'rendered-unit-index.json').read_bytes()),
                      'original_body_sha256': sha(body), 'body_bytes_unchanged': True,
                      'native_unit_ids_preserved': True, 'units': units, 'exercises': exercises,
                      'source_context_contract': index.get('source_context_contract'),
                      'historical_receipts_are_not_rebound_public_validation': True}
        products['semantic-pilot-' + s + '/public-unit-index.json'] = jb(projection)
        src = (b40 / 'authority' / FILES[s]).read_bytes()
        report = json.loads((d / 'SEMANTIC_PILOT_REPORT.json').read_bytes())
        prefix = src[:report['conversion_prefix_bytes']]
        assert sha(prefix) == report['conversion_prefix_sha256']
        # A faithful single-file assembly embeds the active source bodies rather
        # than leaving a thin master pointing to missing chapter inputs.
        if s == 'gr3':
            cumulative_parts.append(b'\n\\setcounter{section}{2}\n')
        cumulative_parts.append(('\n% BEGIN NATIVE SOURCE '+FILES[s]+'\n').encode() + prefix + ('\n% END NATIVE SOURCE '+FILES[s]+'\n').encode())
        products['sources/' + s + '.tex'] = src
        proofs.append({'section': s, 'title': TITLES[s], 'scope': index['reader']['source_scope'], 'reader': fact(path, data),
                       'public_index': fact('semantic-pilot-'+s+'/public-unit-index.json', products['semantic-pilot-'+s+'/public-unit-index.json']),
                       'units': len(units), 'exercise_answer_pairs': len(exercises), 'active_source': fact(FILES[s], prefix),
                       'complete_original_source': fact('sources/'+s+'.tex', src)})
        if s in NOTES:
            notes = json.loads((d / NOTES[s]).read_bytes())['source_issues']
            note_tex.append('\\section*{'+tex_escape(TITLES[s])+': source notes}\n\\begin{enumerate}\n'+''.join('\\item '+tex_escape(n['finding'])+'\n' for n in notes)+'\\end{enumerate}\n')
    cumulative_bytes = cumulative.encode() + b''.join(cumulative_parts) + b'\n\\appendix\n\\chapter{Separate editorial source notes}\n' + ''.join(note_tex).encode() + b'\n\\end{document}\n'
    assert not re.search(rb'^\s*\\endinput\b', cumulative_bytes, re.M), 'active assembly unexpectedly stops early'
    products['sources/00-foundations-cumulative.tex'] = cumulative_bytes
    products['sources/editorial-source-notes.tex'] = ''.join(note_tex).encode()
    products['LICENSE.txt'] = (b40 / 'authority/LICENSE').read_bytes()
    products['ACKNOWLEDGEMENTS.txt'] = (b40 / 'authority/Acknowledgements').read_bytes()
    rows = ''.join('<li><a href="'+p['reader']['path']+'">'+html.escape(p['title'])+'</a> — '+str(p['exercise_answer_pairs'])+' exercises with supplied answers</li>' for p in proofs)
    proof_anchor = 'semantic-pilot-vs3/vs3.reader-pilot.html#r005.hefferon-linear-algebra.unit.file.src.vs.vs3.tex.corollary.label.b186ad4cc75572f666a6'
    products['index.html'] = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Linear algebra foundations — Jim Hefferon</title><style>body{max-width:72ch;margin:auto;padding:1.25rem;font:18px/1.65 system-ui,sans-serif;color:#18232f;background:#f8fafb}a{color:#075a92;overflow-wrap:anywhere}nav{display:flex;gap:1rem;flex-wrap:wrap}li{margin:.7rem 0}.notice{border-left:4px solid #276b8f;padding:1rem;background:#edf4f8}</style></head><body><nav><a href="'+ORIGIN+'en/programme/">Full mathematics programme</a><a href="'+ORIGIN+'id/programme/" lang="id">Program matematika — Bahasa Indonesia</a><a href="https://hefferon.net/linearalgebra/">Author’s original website</a></nav><main><h1>Linear algebra foundations</h1><p>Original English mathematics by Jim Hefferon, from <em>Linear Algebra</em>.</p><p class="notice">Six linked foundation sections, not the complete book. The original explanations, proofs, exercises and supplied answers are preserved. Separate source notes explain specific findings without silently changing the original mathematics.</p><h2>Read</h2><ol>'+rows+'</ol><p><a href="'+proof_anchor+'">Extending a linearly independent set to a basis</a> — read the preceding independence, exchange and dimension arguments as needed. This link is not certification of another course’s proof dependencies.</p><h2>Editable source and offline reading</h2><ol><li><a href="sources/00-foundations-cumulative.tex" download>Complete cumulative editable LaTeX</a></li><li><a href="COMPLETE_SOURCE.zip" download>Complete source and offline readers ZIP</a></li></ol><p>The archive preserves the original source tree and component credits, exact frozen editable HTML-generation inputs, the six readers and replay instructions. The HTML rebuild is verified; a new PDF or native TeX compilation is not claimed. No scripts, web fonts or network connection are required to read the downloaded HTML.</p><h2>Sources, rights and checks</h2><p>Source revision '+REVISION+'. <a href="LICENSE.txt">CC BY-SA 2.5 option</a>; <a href="ACKNOWLEDGEMENTS.txt">original component credits</a> are retained. This material is not relicensed as CC0. This is not an Everyday-English rewrite.</p><p>Source-preserving rebuild, navigation, indexing and current deterministic checks: OpenAI Codex — GPT-6 Astra, Ultra effort. Earlier intermediate-conversion model identity is unverified; historical work is not reattributed. No human review or exhaustive mathematical certification is claimed.</p><p><a href="FOUNDATIONS_MANIFEST.json">Source and modular-index manifest</a></p></main><footer><a href="'+ORIGIN+'en/programme/">Return to the full mathematics programme</a></footer></body></html>\n').encode()
    products['index.html'] = products['index.html'].replace(b'href="COMPLETE_SOURCE.zip"', ('href="'+SOURCE_URL+'"').encode())
    parsers = {}
    for p, b in products.items():
        if p.endswith('.html'):
            parser = Links(); parser.feed(b.decode()); assert not parser.remote_runtime
            assert len(parser.ids) == len(set(parser.ids)), 'duplicate HTML anchors'
            parsers[p] = parser
    checked_links = 0
    for path, parser in parsers.items():
        for url in parser.hrefs:
            if re.match(r'^(https?:|mailto:)', url):
                continue
            file, _, anchor = url.partition('#')
            target = safe(public, str(Path(path).parent / file) if file else path).relative_to(public.resolve()).as_posix()
            if target in ('COMPLETE_SOURCE.zip', 'FOUNDATIONS_MANIFEST.json'):
                continue
            assert target in products, 'missing local target: ' + path + ' -> ' + url
            if anchor:
                assert anchor in parsers[target].ids, 'missing anchor: ' + url
            checked_links += 1
    assert sum(p['units'] for p in proofs) == 799
    assert sum(p['exercise_answer_pairs'] for p in proofs) == 278
    for path, b in products.items():
        write(public / path, b, check)
    receipt = {'schema': 'b40-public-foundations-build/1', 'state': 'local_public_export_validated_not_deployed',
               'source_revision': REVISION, 'sections': proofs, 'counts': {'readers': 6, 'native_units': 799, 'exercise_answer_pairs': 278, 'local_links_checked': checked_links},
               'native_replay': replays, 'frozen_inputs': fact('FROZEN_INPUTS.json', (frozen / 'FROZEN_INPUTS.json').read_bytes()),
               'outputs': [fact(p, b) for p, b in sorted(products.items())],
               'boundaries': {'no_mathematical_body_edit': True, 'source_notes_unchanged': True, 'no_TeX_or_PDF_build': True, 'not_full_book': True, 'not_phone_admission': True}}
    write(public.parent / 'BUILD_RECEIPT.json', jb(receipt), check)
    return receipt


def main():
    global REFRESH
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--freeze', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--refresh-candidate', action='store_true', help='Refresh this unpublished generated candidate only, after verifying its prior bytes')
    ap.add_argument('--work', type=Path, default=BASE / 'b40-foundations-public-20261002')
    args = ap.parse_args()
    frozen = args.work / 'frozen'
    if args.refresh_candidate:
        assert args.freeze and not args.check
        assert not (args.work / 'PUBLICATION_RECEIPT.json').exists(), 'published candidate is immutable'
        previous = json.loads((args.work / 'BUILD_RECEIPT.json').read_bytes())
        for row in previous['outputs']:
            old = safe(args.work / 'public', row['path']).read_bytes()
            assert len(old) == row['bytes'] and sha(old) == row['sha256'], 'candidate changed outside this workflow'
        REFRESH = True
    if args.freeze:
        freeze(frozen)
    result = export(frozen, args.work / 'public', args.check)
    print(json.dumps({'state': 'byte_replay_pass' if args.check else result['state'], 'counts': result['counts'], 'output_files': len(result['outputs'])}))


if __name__ == '__main__':
    main()
