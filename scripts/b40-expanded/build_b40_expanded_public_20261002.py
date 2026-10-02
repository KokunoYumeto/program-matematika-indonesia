"""Freeze and export the explicitly selected admitted original-English readers.

No owner edits, TeX execution, network requests or publication. The public
projection preserves every existing main-body byte, source note and native ID.
Frozen Pandoc AST/MathML/SVG inputs reproduce the selected readers first.
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
SECTIONS = ['gr1','gr2','gr3','cas','leontief','ppivot','network','vs1','vs2','vs3','fields','crystal','voting','dimen','map1','map2','map3','map4','map5','map6','lstsqs','homogeom','magicsqs','markov','erlang','det1','det2','det3']
TITLES = {}
FILES = {s: 'src/'+('det' if s.startswith('det') else 'map' if s in SECTIONS[14:25] else 'vs' if s in SECTIONS[7:14] else 'gr')+'/'+s+'.tex' for s in SECTIONS}
NOTES = {}
ORIGIN = 'https://kokunoyumeto.github.io/program-matematika-indonesia/'
SOURCE_URL = 'https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/b40-original-en-2026.10.02-28-sections/COMPLETE_SOURCE.zip'
REVISION = 'df2262e089a02651c127f1dd12649c4622ee1383'
ARCHIVE_SHA = 'b409fc82a8323578e71d8095b9ab4bc9ca814d5a0d9cc6d125dd6b4d81dc23d0'
REFRESH = False
REGISTRY_SHA = '363b005437b4d36e364ed72408b0328188191f574221aca7c6a34176f34b2956'
EXPECTED = {'readers':28,'native_units':2503,'exercises':836,'exercise_answer_pairs':834,'absent_original_answers':2}
LAST_TITLE = 'Laplace’s Formula'


def configure(path):
    global SECTIONS, FILES, SOURCE_URL, REGISTRY_SHA, EXPECTED, LAST_TITLE
    if not path.exists():
        return
    c = json.loads(path.read_bytes())
    assert c['schema'] == 'b40-public-export-selection/1'
    assert len(c['sections']) == len(set(c['sections'])) == c['counts']['readers']
    assert all(re.fullmatch(r'[a-z][a-z0-9]*', s) for s in c['sections'])
    assert c['source_archive_url'].startswith('https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/')
    SECTIONS = c['sections']
    FILES = {s:'src/'+('jc' if s.startswith('jc') else 'det' if s.startswith('det') or s in ('cramer','chio','projplane','compgraphics') else 'map' if s in SECTIONS[14:25] else 'vs' if s in SECTIONS[7:14] else 'gr')+'/'+s+'.tex' for s in SECTIONS}
    SOURCE_URL, REGISTRY_SHA, EXPECTED, LAST_TITLE = c['source_archive_url'], c['registry_sha256'], c['counts'], c['last_section_title']


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
    selection = destination.parent / 'EXPORT_SELECTION.json'
    configure(selection)
    originals = {}
    def add(rel, source=None):
        data = (source or (BASE / rel)).read_bytes()
        key = str(rel).replace('\\', '/')
        assert key not in originals or originals[key] == data
        originals[key] = data
    registry_bytes = (BASE / B40_REL / 'rendered-section-registry.json').read_bytes()
    assert sha(registry_bytes) == REGISTRY_SHA
    registry = json.loads(registry_bytes)
    assert [x['section'] for x in registry['sections']] == SECTIONS
    add(B40_REL / 'rendered-section-registry.json')
    if selection.exists():
        originals['EXPORT_SELECTION.json'] = selection.read_bytes()
        admission = json.loads(selection.read_bytes())['admission_receipt']
        data = safe(BASE, admission['path']).read_bytes()
        assert fact(admission['path'], data) == admission
        admitted = json.loads(data)
        assert admitted['registry']['sha256'] == REGISTRY_SHA
        assert admitted['admitted_sections'] == EXPECTED['readers']
        assert admitted['state'] == 'local_admitted_source_reader_context_consumer_pass_partial_corpus'
        originals['SOURCE_ADMISSION.json'] = jb({'schema':'b40-public-source-admission-summary/1', 'private_receipt_identity':admission, 'state':admitted['state'], 'source':admitted['source'], 'registry':admitted['registry'], 'admitted_sections':admitted['admitted_sections'], 'cumulative_counts':admitted['cumulative_counts'], 'new_scope':admitted['new_scope'], 'source_bytes_changed':admitted['source_bytes_changed'], 'source_correctness_certified':admitted['source_correctness_certified'], 'private_command_transcripts_omitted':True})
    for lane in registry['sections']:
        for f in (lane['reader_fact'], lane['index_fact']):
            b = safe(BASE / B40_REL, f['path']).read_bytes()
            assert fact(f['path'], b) == f
    for s in SECTIONS:
        directory = B40_REL / ('semantic-pilot-' + s)
        names = [s+'.semantic.json', 'math-source-index.json', 'mathml-regions.json', 'MATH_RENDER_REPORT.json', 'MATH_RENDER_CONFIG.json', s+'.reader-pilot.html', 'rendered-unit-index.json', 'SEMANTIC_PILOT_REPORT.json', 'PRESENTATION_BINDINGS.json', 'PROSE_LEXICAL_REPLAY.json']
        optional = ['FIGURE_CONVERSION_RECEIPT.json', 'RICH_CONTENT_CLOSURE.json', 'SOURCE_TABLE_CELL_GRID.json', 'ASSET_INDEX.json', 'RENDERED_CONTEXT_CONTRACT.json', 'RENDERED_SOURCE_CONTEXT_RELATIONS.json', 'SOURCE_CONTEXT_REQUIREMENTS.json', 'SOURCE_FIGURE_DISCREPANCY_NOTES.json', 'SOURCE_NOTE_EXTRACTION_OVERLAY.json', 'SOURCE_MODEL_REPLAY.json', 'CHIO_SOURCE_ADJUDICATION.json', 'PROJPLANE_SOURCE_INTAKE.json', 'COMPGRAPHICS_SOURCE_INTAKE.json', 'JC1_SOURCE_INTAKE.json', 'COMPONENT_RIGHTS.json']
        for p in (BASE / directory).glob('*.json'):
            if p.name in optional or p.name.endswith(('_SOURCE_NOTES.json', '_MATHEMATICAL_REPLAY.json')):
                names.append(p.name)
        for name in ('FIGURE_CONVERSION_RECEIPT.json', 'RICH_CONTENT_CLOSURE.json'):
            if name in names:
                meta = json.loads((BASE / directory / name).read_bytes())
                for kind in ('figures','assets','pictures','code_blocks'):
                    for row in meta.get(kind, []):
                        if row.get('output'):
                            f = row['output']; b = safe(BASE / directory, f['path']).read_bytes()
                            assert len(b) == f['bytes'] and sha(b) == f['sha256']
                            names.append(f['path'])
        for name in sorted(set(names)):
            add(directory / name)
        add(B40_REL / 'authority' / FILES[s])
    scripts = ['build_b40_reader_pilot_20260921.mjs','extract_b40_rendered_unit_20260921.mjs',Path(__file__).name]
    seen = set()
    while scripts:
        name = scripts.pop()
        if name in seen:
            continue
        seen.add(name)
        script = BASE / 'curriculum_logbook' / name
        add(Path('curriculum_logbook') / name)
        for imported in re.findall(r"(?:from\s*|import\s*)['\"]\./([^'\"]+)['\"]", script.read_text(encoding='utf-8')):
            assert '/' not in imported and imported.endswith('.mjs'), imported
            scripts.append(imported)
    add(B40_REL / 'original-english-backend-v1/catalog.json')
    for name in ['LICENSE','README.md','src/book.tex']:
        add(B40_REL / 'authority' / name)
    add(B40_REL / 'source-intake/SOURCE_TREE_MANIFEST.json')
    provider = BASE / 'd100-capability-v1-worktree/backend/cross-programme-v1/provider-handoffs/B40-basis-extension-20261002'
    add(B40_REL / 'authority/Acknowledgements', provider / 'source/Acknowledgements')
    archive = BASE.parents[1] / '04_mirrors/id/hefferon-linear-algebra-id/authority/archives' / ('linear-algebra-'+REVISION+'.zip')
    data = archive.read_bytes()
    assert sha(data) == ARCHIVE_SHA and len(data) == 42547343
    originals['native-authority.zip'] = data
    provenance = destination.parent / 'RUNTIME_PROVENANCE.json'
    p = json.loads(provenance.read_bytes())
    assert p['state'] == 'verified_current_turn' and p['model'] == 'gpt-6-astra' and p['effort'] == 'ultra'
    originals['RUNTIME_PROVENANCE.json'] = provenance.read_bytes()
    for name, data in originals.items():
        existing = destination / name
        if existing.exists():
            assert existing.read_bytes() == data or (REFRESH and name == 'curriculum_logbook/'+Path(__file__).name), 'frozen input changed: ' + name
        write(existing, data)
    write(destination / 'FROZEN_INPUTS.json', jb({'schema':'b40-public-expanded-inputs/1','source_revision':REVISION,'files':[fact(k,v) for k,v in sorted(originals.items())]}))


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
    configure(frozen / 'EXPORT_SELECTION.json')
    manifest, replays = load_and_replay(frozen)
    b40 = frozen / B40_REL
    for section in SECTIONS:
        reader = (b40 / ('semantic-pilot-'+section) / (section+'.reader-pilot.html')).read_text(encoding='utf-8')
        heading = re.search(r'<h1[^>]*>(.*?)</h1>', reader, re.S)
        if section == 'jc1':
            # The source begins with the chapter introduction "Similarity";
            # its selected section is "Complex Vector Spaces". Keep both in
            # the body and use the actual section title in the contents.
            heading = re.search(r'<h2[^>]*>(.*?)</h2>', reader, re.S)
        assert heading, section
        TITLES[section] = html.unescape(re.sub(r'<[^>]+>', '', heading.group(1)))
    products = {}
    proofs = []
    original_indexes = {}
    note_tex = []
    cumulative_parts = []
    cumulative = r'''% Jim Hefferon, Linear Algebra, pinned source revision ''' + REVISION + r'''
% 28 validated sections with all supplied answers in their native source.
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
\usepackage{makeidx}\makeindex
% The bibliography remains a native dependency inside native-authority.zip.
\AtEndDocument{\input{bib/bib}}
\begin{document}
\mainmatter
\pagestyle{bookbody}
'''
    cumulative = cumulative.replace('% 28 validated sections', '% '+str(len(SECTIONS))+' validated sections')
    archive_url = SOURCE_URL
    for s in SECTIONS:
        d = b40 / ('semantic-pilot-' + s)
        original = (d / (s + '.reader-pilot.html')).read_bytes()
        old_start, body = main_part(original)
        text = original.decode('utf-8')
        new_notice = '<p class="notice"><strong>Original English by Jim Hefferon — 28 validated sections.</strong> The original mathematics and supplied answers below are preserved. This is a partial-book reading edition, not the complete book or an Everyday-English rewrite.</p>'
        new_notice = new_notice.replace('28 validated sections', str(len(SECTIONS))+' validated sections')
        text, n = re.subn(r'<p class="notice">.*?</p>', lambda m: new_notice, text, count=1, flags=re.S)
        assert n == 1
        text = text.replace(' — local conversion pilot', ' — original English reading edition')
        text = text.replace('required for this local reading file.', 'required for this reading file.')
        # Only construction-status metadata is superseded. Never rewrite the
        # original mathematical body, source findings or limitation statements.
        h = re.search(r'<header>.*?</header>', text, re.S)
        old_header = h.group()
        header = old_header
        for stale in [
            'Exact runtime-model identification remains unverified and must be bound before publication.',
            'Exact runtime-model identity remains unverified and must be bound before publication.',
            'Exact runtime-model identification remains unverified.',
            'exact runtime-model identity must be bound before publication.',
        ]:
            header = header.replace(stale, 'Current rebuild runtime is documented in the credit below; earlier intermediate work is not reattributed.')
        header = header.replace('Modular-context extraction and final layout QA remain unfinished.', 'Modular-context extraction and local layout checks are complete for this section; whole-book integration remains incomplete.')
        header = header.replace('Reader admission and whole-book integration remain unfinished.', 'Local reader admission is complete; whole-book integration remains unfinished.')
        header = header.replace('The modular extraction contract is not yet admitted.', 'The modular extraction contract is admitted for this section; whole-book integration remains incomplete.')
        text = text[:h.start()] + header + text[h.end():]
        navigation = '<nav aria-label="Book reader navigation"><a href="../index.html">Book contents</a> · <a href="'+ORIGIN+'en/programme/">Full mathematics programme</a> · <a href="../sources/00-linear-algebra-cumulative.tex" download>Complete editable LaTeX</a> · <a href="'+SOURCE_URL+'" download>Full source and offline reader ZIP</a> · <a href="../sources/'+s+'.tex" download>This section’s original LaTeX</a></nav>'
        disclosure = '<p class="conversion-credit">Source-preserving rebuild, navigation, source packaging and current deterministic checks: OpenAI Codex — GPT-6 Astra, Ultra effort. Jim Hefferon remains the author of the mathematics. Earlier intermediate-conversion runtime identity is not established by its retained receipts and is not reassigned to this rebuild. No human review or exhaustive proof certification is claimed.</p>'
        text = text.replace('<header>', '<header>'+navigation, 1).replace('</header>', disclosure+'</header>', 1)
        text = text.replace('<footer>', '<footer>'+navigation, 1)
        text = text.replace('</style>', '.proof>p:first-child>em:first-child{margin-inline-end:.25em}\n</style>', 1)
        data = text.encode()
        start, new_body = main_part(data)
        assert body == new_body
        index = json.loads((d / 'rendered-unit-index.json').read_bytes())
        original_indexes[s] = index
        # A modular consumer may request a prior diagram independently of the
        # HTML body. Export those exact bytes, not merely an embedded screenshot
        # or a metadata path that only resolves in the private staging tree.
        for asset in index.get('rich_assets', {}).get('assets', []):
            if asset.get('output'):
                f = asset['output']; data_asset = safe(d, f['path']).read_bytes()
                assert len(data_asset) == f['bytes'] and sha(data_asset) == f['sha256']
                asset_path = 'semantic-pilot-'+s+'/'+f['path']
                safe(public, asset_path)
                assert asset_path not in products or products[asset_path] == data_asset
                products[asset_path] = data_asset
        for rule in index.get('source_context_contract', {}).get('rules', []):
            for asset in rule['origin'].get('assets', []):
                f = asset['output']; data_asset = safe(b40, f['path']).read_bytes()
                assert len(data_asset) == f['bytes'] and sha(data_asset) == f['sha256']
                safe(public, f['path'])
                assert f['path'] not in products or products[f['path']] == data_asset
                products[f['path']] = data_asset
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
        projection = {**copy.deepcopy(index), 'schema': 'course-rendered-unit-projection/1',
                      'state': 'public_export_validated_deployment_receipt_is_separate',
                      'language': 'en', 'source_revision': REVISION,
                      'reader': {**index['reader'], **fact(s+'.reader-pilot.html', data)},
                      'original_reader': index['reader'],
                      'original_index': fact('original-rendered-unit-index.json', (d / 'rendered-unit-index.json').read_bytes()),
                      'original_body_sha256': sha(body), 'body_bytes_unchanged': True,
                      'native_unit_ids_preserved': True, 'units': units, 'exercises': exercises,
                      'modular_asset_resolution': {'inherited_context_output_paths_relative_to':'reader-edition-root', 'rich_asset_output_paths_relative_to':'section-directory', 'all_declared_asset_outputs_exported':True},
                      'historical_receipts_are_not_rebound_public_validation': True}
        products['semantic-pilot-' + s + '/public-unit-index.json'] = jb(projection)
        src = (b40 / 'authority' / FILES[s]).read_bytes()
        report = json.loads((d / 'SEMANTIC_PILOT_REPORT.json').read_bytes())
        prefix = src[:report['conversion_prefix_bytes']]
        assert sha(prefix) == report['conversion_prefix_sha256']
        # A faithful single-file assembly embeds the active source bodies rather
        # than leaving a thin master pointing to missing chapter inputs.
        cumulative_parts.append(('\n% BEGIN NATIVE SOURCE '+FILES[s]+'\n').encode() + prefix + ('\n% END NATIVE SOURCE '+FILES[s]+'\n').encode())
        products['sources/' + s + '.tex'] = src
        proofs.append({'section': s, 'title': TITLES[s], 'scope': index['reader']['source_scope'], 'reader': fact(path, data),
                       'public_index': fact('semantic-pilot-'+s+'/public-unit-index.json', products['semantic-pilot-'+s+'/public-unit-index.json']),
                       'units': len(units), 'exercises': len(exercises), 'exercise_answer_pairs': sum(bool(e['answer_ids']) for e in exercises), 'absent_original_answers': sum(not e['answer_ids'] for e in exercises), 'active_source': fact(FILES[s], prefix),
                       'complete_original_source': fact('sources/'+s+'.tex', src)})
        notes = []
        for p in sorted(d.glob('*.json')):
            if p.name.endswith(('_SOURCE_NOTES.json','_MATHEMATICAL_REPLAY.json')) or p.name in ('SOURCE_MODEL_REPLAY.json','SOURCE_FIGURE_DISCREPANCY_NOTES.json') or (s in ('cramer','detspeed','chio','projplane','compgraphics','jc1') and p.name == 'SOURCE_CONTEXT_REQUIREMENTS.json'):
                nr = json.loads(p.read_bytes()); notes.extend(nr.get('source_issues', nr.get('source_findings', [])))
        if notes:
            note_tex.append('\\section*{'+tex_escape(TITLES[s])+': source notes}\n\\begin{enumerate}\n'+''.join('\\item '+tex_escape(n.get('finding', n.get('description', 'See the exact source-note record in the archive.')))+'\n' for n in notes)+'\\end{enumerate}\n')
    cumulative_bytes = cumulative.encode() + b''.join(cumulative_parts) + b'\n\\appendix\n\\chapter{Separate editorial source notes}\n' + ''.join(note_tex).encode() + b'\n\\end{document}\n'
    assert not re.search(rb'^\s*\\endinput\b', cumulative_bytes, re.M), 'active assembly unexpectedly stops early'
    products['sources/00-linear-algebra-cumulative.tex'] = cumulative_bytes
    products['sources/editorial-source-notes.tex'] = ''.join(note_tex).encode()
    products['LICENSE.txt'] = (b40 / 'authority/LICENSE').read_bytes()
    products['ACKNOWLEDGEMENTS.txt'] = (b40 / 'authority/Acknowledgements').read_bytes()
    rows = ''.join('<li><a href="'+p['reader']['path']+'">'+html.escape(p['title'])+'</a> — '+str(p['exercise_answer_pairs'])+' exercises with supplied answers</li>' for p in proofs)
    proof_anchor = 'semantic-pilot-vs3/vs3.reader-pilot.html#r005.hefferon-linear-algebra.unit.file.src.vs.vs3.tex.corollary.label.b186ad4cc75572f666a6'
    products['index.html'] = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Linear algebra — original English — Jim Hefferon</title><style>body{max-width:72ch;margin:auto;padding:1.25rem;font:18px/1.65 system-ui,sans-serif;color:#18232f;background:#f8fafb}a{color:#075a92;overflow-wrap:anywhere}nav{display:flex;gap:1rem;flex-wrap:wrap}li{margin:.7rem 0}.notice{border-left:4px solid #276b8f;padding:1rem;background:#edf4f8}</style></head><body><nav><a href="'+ORIGIN+'en/programme/">Full mathematics programme</a><a href="'+ORIGIN+'id/programme/" lang="id">Program matematika — Bahasa Indonesia</a><a href="https://hefferon.net/linearalgebra/">Author’s original website</a></nav><main><h1>Linear algebra — original English</h1><p>Original English mathematics by Jim Hefferon, from <em>Linear Algebra</em>.</p><p class="notice">28 linked sections through Laplace’s Formula, not the complete book. The original explanations, proofs, exercises and supplied answers are preserved. Separate source notes explain specific findings without silently changing the original mathematics.</p><h2>Read</h2><ol>'+rows+'</ol><p><a href="'+proof_anchor+'">Extending a linearly independent set to a basis</a> — read the preceding independence, exchange and dimension arguments as needed. This link is not certification of another course’s proof dependencies.</p><h2>Editable source and offline reading</h2><ol><li><a href="sources/00-linear-algebra-cumulative.tex" download>Complete cumulative editable LaTeX</a></li><li><a href="COMPLETE_SOURCE.zip" download>Complete source and offline readers ZIP</a></li></ol><p>The archive preserves the original source tree and component credits, exact frozen editable HTML-generation inputs, the 28 readers and replay instructions. The HTML rebuild is verified; a new PDF or native TeX compilation is not claimed. No scripts, web fonts or network connection are required to read the downloaded HTML.</p><h2>Sources, rights and checks</h2><p>Source revision '+REVISION+'. <a href="LICENSE.txt">CC BY-SA 2.5 option</a>; <a href="ACKNOWLEDGEMENTS.txt">original component credits</a> are retained. This material is not relicensed as CC0. This is not an Everyday-English rewrite.</p><p>Source-preserving rebuild, navigation, indexing and current deterministic checks: OpenAI Codex — GPT-6 Astra, Ultra effort. Earlier intermediate-conversion model identity is unverified; historical work is not reattributed. No human review or exhaustive mathematical certification is claimed.</p><p><a href="READER_MANIFEST.json">Source and modular-index manifest</a></p></main><footer><a href="'+ORIGIN+'en/programme/">Return to the full mathematics programme</a></footer></body></html>\n').encode()
    products['index.html'] = products['index.html'].replace('28 linked sections through Laplace’s Formula'.encode(), (str(len(SECTIONS))+' linked sections through '+LAST_TITLE).encode()).replace(b'the 28 readers', ('the '+str(len(SECTIONS))+' readers').encode())
    products['index.html'] = products['index.html'].replace(b'href="COMPLETE_SOURCE.zip"', ('href="'+SOURCE_URL+'"').encode())
    # Long source-revision identities must wrap on narrow screens too.
    products['index.html'] = products['index.html'].replace(b'body{max-width:', b'body{overflow-wrap:anywhere;max-width:')
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
            if target in ('COMPLETE_SOURCE.zip', 'READER_MANIFEST.json'):
                continue
            assert target in products, 'missing local target: ' + path + ' -> ' + url
            if anchor:
                assert anchor in parsers[target].ids, 'missing anchor: ' + url
            checked_links += 1
    assert sum(p['units'] for p in proofs) == EXPECTED['native_units']
    assert sum(p['exercises'] for p in proofs) == EXPECTED['exercises']
    assert sum(p['exercise_answer_pairs'] for p in proofs) == EXPECTED['exercise_answer_pairs']
    for path, b in products.items():
        write(public / path, b, check)
    receipt = {'schema': 'b40-public-expanded-reader-build/1', 'state': 'local_public_export_validated_not_deployed',
               'source_revision': REVISION, 'sections': proofs, 'counts': {**EXPECTED, 'local_links_checked': checked_links},
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
    ap.add_argument('--work', type=Path, default=BASE / 'b40-expanded-public-20261002')
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
