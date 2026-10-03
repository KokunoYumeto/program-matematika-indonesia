"""Source-preserving B80 EPUB repair and cumulative LaTeX export; no experiment execution."""
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import re
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/course-formats-v1'))
from course_formats import archive_inventory, xml, NS

SOURCE_HASHES = {
    'id': '8e9e35dd54be8524a8b7752df0a7285749db4c80fc5a10271eb841c01c0c748d',
    'en': 'ed1f8b3e93e56313f27f03f93d1941e39a5485af9975d26f53deef454285e0d8',
}
TEXT = {
    'id': {
        'title': 'Tentang ekspor format ini', 'contributors': 'Kontributor proyek O002',
        'notice': 'Perbaikan dan ekspor format: OpenAI Codex - GPT-6 Astra, upaya Ultra. Teks pelajaran, latihan, solusi, kode dan rumus dipertahankan dari edisi rilis asli; eksperimen tidak dijalankan ulang. Ini bukan penerjemahan atau peninjauan matematika baru.',
        'repair': 'Satu atribut alt yang tidak sah dan berulang dihapus dari wadah gambar. Teks alternatif pada gambar tetap utuh. Kredit metadata pribadi diganti dengan kredit kontributor proyek. Sumber asli tetap Quarto; LaTeX kumulatif adalah ekspor turunan, bukan pengganti sumber asli.',
        'scope': 'Cakupan: dua primer dan dua belas unit utama, dengan 75 latihan. Lisensi teks CC BY-SA 4.0 dan kode MIT tetap berlaku. Edisi PDF turunan dapat mempunyai tata letak dan nomor halaman berbeda dari PDF lama.',
        'source': 'Rilis sumber', 'latex': 'Sumber LaTeX lengkap disertakan bersama paket sumber dan berkas pendukung untuk mereproduksi ekspor ini.',
    },
    'en': {
        'title': 'About this format export', 'contributors': 'O002 project contributors',
        'notice': 'Format repair and export: OpenAI Codex - GPT-6 Astra, Ultra effort. Lesson text, exercises, solutions, code and formulas are preserved from the original released edition; experiments were not rerun. This is not a new translation or mathematical review.',
        'repair': 'One invalid repeated alt attribute was removed from a figure container. The image alternative text is unchanged. Personal metadata credit is standardized to the project-contributor credit. Quarto remains the native source; cumulative LaTeX is a derived export, not a replacement master.',
        'scope': 'Scope: two primers and twelve main units, with 75 exercises. Text remains CC BY-SA 4.0 and code remains MIT. The derived PDF may have different layout and page numbers from the old PDF.',
        'source': 'Source release', 'latex': 'Complete cumulative LaTeX accompanies the source package and dependencies needed to reproduce this export.',
    },
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def pandoc(executable, args, data=None):
    run = subprocess.run([str(executable), *args], input=data, capture_output=True, timeout=90, check=True)
    if run.stderr.strip():
        raise ValueError('Pandoc diagnostic: ' + run.stderr.decode('utf-8', errors='replace'))
    return run.stdout


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def content_signature(blocks):
    nodes = list(walk(blocks))
    return {
        'prose': [node['c'] for node in nodes if node.get('t') == 'Str'],
        'math': [re.sub(r'\s+', '', node['c'][1]) for node in nodes if node.get('t') == 'Math'],
        'code_blocks': [node['c'][1] for node in nodes if node.get('t') == 'CodeBlock'],
        'inline_code': [node['c'][1] for node in nodes if node.get('t') == 'Code'],
        'images': [node['c'][2] for node in nodes if node.get('t') == 'Image'],
    }


def visible_text(value):
    """Ignore presentation/attributes, not words, punctuation, or quote scope."""
    if isinstance(value, list):
        return ''.join(visible_text(item) for item in value)
    if not isinstance(value, dict):
        return ''
    kind, content = value.get('t'), value.get('c')
    if kind == 'Str':
        return content
    if kind in ('Space', 'SoftBreak', 'LineBreak'):
        return ' '
    if kind in ('Code', 'CodeBlock'):
        text = content[1].replace('\u00a0', ' ')
        return '\n' + text + '\n' if kind == 'CodeBlock' else text
    if kind == 'Math':
        return ' MATH[' + re.sub(r'\s+', '', content[1]) + '] '
    if kind == 'Quoted':
        left, right = ('\u2018', '\u2019') if content[0]['t'] == 'SingleQuote' else ('\u201c', '\u201d')
        return left + visible_text(content[1]) + right
    if kind in ('Link', 'Image'):
        return visible_text(content[1])
    text = visible_text(content)
    return text + '\n' if kind in ('Para', 'Plain', 'Header', 'Div', 'Table', 'Figure') else text


def text_tokens(value):
    # Whitespace/wrapping is presentational; word and punctuation boundaries are not.
    return re.findall(r'\w+|[^\w\s]', visible_text(value), re.UNICODE)


def inline_code_runs(value):
    """Pandoc splits brackets inside texttt into adjacent Code nodes; coalesce only those."""
    result = []
    if isinstance(value, dict):
        return inline_code_runs(value.get('c'))
    if isinstance(value, list):
        run = None
        def unwrap(items):
            for item in items:
                if isinstance(item, dict) and item.get('t') == 'Span' and item['c'][0] == ['', [], []]:
                    yield from unwrap(item['c'][1])
                else:
                    yield item
        for child in unwrap(value):
            if isinstance(child, dict) and child.get('t') == 'Code':
                run = (run or '') + child['c'][1].replace('\u00a0', ' ')
            else:
                if run is not None:
                    result.append(run)
                    run = None
                result.extend(inline_code_runs(child))
        if run is not None:
            result.append(run)
    return result


def table_cells(blocks):
    result = []
    for node in walk(blocks):
        if node.get('t') != 'Table':
            continue
        _, _, columns, head, bodies, foot = node['c']
        rows = list(head[1])
        for body in bodies:
            rows.extend(body[2])
            rows.extend(body[3])
        rows.extend(foot[1])
        result.append({'columns': len(columns), 'rows': [
            [(cell[2], cell[3], text_tokens(cell[4])) for cell in row[1]] for row in rows]})
    return result


def semantic_signature(blocks):
    raw = content_signature(blocks)
    return {
        'text_tokens': text_tokens(blocks), 'math': raw['math'],
        'code_blocks': raw['code_blocks'], 'inline_code_runs': inline_code_runs(blocks),
        'tables': table_cells(blocks), 'images': raw['images'],
        'headings': [(node['c'][0], text_tokens(node['c'][2]))
                     for node in walk(blocks) if node.get('t') == 'Header'],
        'links': [node['c'][2] for node in walk(blocks) if node.get('t') == 'Link'],
    }


def group_numeric_cells(tex):
    """Protect bare numbers from Pandoc's LaTeX-reader dimension scanning.

    Only numeric cells inside emitted longtable environments are grouped. An
    mbox changes neither the digits nor decimal punctuation. This makes their
    independent readback testable instead of waiving missing table values.
    """
    total = 0
    def table(match):
        nonlocal total
        text, count = re.subn(r'(?m)(^|&)(\s*)([+-]?\d+(?:[.,]\d+)*)(\s*)(?=&|\\\\)',
                             lambda m: m[1] + m[2] + '\\mbox{' + m[3] + '}' + m[4], match[0])
        total += count
        return text
    result = re.sub(r'\\begin\{longtable\}.*?\\end\{longtable\}', table, tex.decode('utf-8'), flags=re.S)
    return result.encode('utf-8'), total


def print_document(value):
    """Add nonprinting break opportunities to long inline code, never to its text."""
    if isinstance(value, dict):
        return {key: print_document(item) for key, item in value.items()}
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, dict) and item.get('t') == 'Code' and len(item['c'][1]) > 10:
                text = item['c'][1]
                for offset in range(0, len(text), 8):
                    if offset:
                        result.append({'t': 'RawInline', 'c': ['latex', r'\allowbreak{}']})
                    result.append({'t': 'Code', 'c': [copy.deepcopy(item['c'][0]), text[offset:offset + 8]]})
            else:
                # Native exercise mini-headings are bold paragraphs, not Header
                # nodes. Keep each with the following answer/hint paragraph.
                if (isinstance(item, dict) and item.get('t') == 'Para' and item.get('c')
                        and any(node.get('t') == 'Strong' for node in item['c'])
                        and all(node.get('t') in ('Strong', 'Space') for node in item['c'])):
                    result.append({'t': 'RawBlock', 'c': ['latex', r'\Needspace{6\baselineskip}']})
                result.append(print_document(item))
        return result
    return value


def repair_epub(source, destination, language):
    assert digest(source.read_bytes()) == SOURCE_HASHES[language]
    with zipfile.ZipFile(source) as original:
        names = archive_inventory(original)
        data = {name: original.read(name) for name in names}
        old_data = dict(data)
        figure_member = 'EPUB/text/ch007.xhtml'
        before = xml(data[figure_member])
        container = before.xpath('.//h:div[@alt]', namespaces=NS)
        assert len(container) == 1 and container[0].get('id') == 'fig-o002-u04-progressive'
        image = container[0].xpath('.//h:img', namespaces=NS)
        assert len(image) == 1 and image[0].get('alt') == container[0].get('alt')
        pattern = rb'(<div\b[^>]*\bid="fig-o002-u04-progressive"[^>]*?)\s+alt="[^"]*"([^>]*>)'
        data[figure_member], edits = re.subn(pattern, rb'\1\2', data[figure_member])
        assert edits == 1
        after = xml(data[figure_member])
        assert not after.xpath('.//h:div[@alt]', namespaces=NS)
        assert before.xpath('.//h:img/@alt', namespaces=NS) == after.xpath('.//h:img/@alt', namespaces=NS)
        opf = xml(data['EPUB/content.opf'])
        creators = opf.xpath('./o:metadata/dc:creator', namespaces=NS)
        assert len(creators) == 1
        old_creator = creators[0].text
        creators[0].text = TEXT[language]['contributors']
        if old_creator != creators[0].text:
            page = data['EPUB/text/title_page.xhtml']
            old = html.escape(old_creator).encode()
            assert page.count(old) == 1
            data['EPUB/text/title_page.xhtml'] = page.replace(old, html.escape(creators[0].text).encode())
        metadata = opf.find('o:metadata', NS)
        contribution = etree.SubElement(metadata, '{' + NS['dc'] + '}contributor')
        contribution.text = ('OpenAI Codex - GPT-6 Astra, upaya Ultra (integrasi format)' if language == 'id'
                             else 'OpenAI Codex - GPT-6 Astra, Ultra effort (format integration)')
        edition_id = 'urn:uuid:' + str(uuid.uuid5(uuid.NAMESPACE_URL, 'B80/' + language + '/format-export-2026-10-03'))
        for item in metadata.xpath('dc:identifier', namespaces=NS):
            item.text = edition_id
        for item in metadata.xpath('o:meta[@property="dcterms:modified"]', namespaces=NS):
            item.text = '2026-10-03T00:00:00Z'
        manifest = opf.find('o:manifest', NS)
        etree.SubElement(manifest, '{' + NS['o'] + '}item', id='format-note', href='text/format-note.xhtml', attrib={'media-type': 'application/xhtml+xml'})
        spine = opf.find('o:spine', NS)
        spine.insert(2, etree.Element('{' + NS['o'] + '}itemref', idref='format-note'))
        data['EPUB/content.opf'] = etree.tostring(opf, xml_declaration=True, encoding='utf-8')
        tag = 'v2026.08.22.1' if language == 'id' else 'v2026.08.31.en1'
        url = f'https://github.com/KokunoYumeto/mathematical-computing-reproducible-experiments-{language}/releases/tag/{tag}'
        t = TEXT[language]
        note = '<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" lang="' + language + '"><head><title>' + t['title'] + '</title></head><body><section id="format-note"><h1>' + t['title'] + '</h1>'
        note += ''.join('<p>' + html.escape(t[key]) + '</p>' for key in ('notice', 'repair', 'scope', 'latex'))
        note += '<p><a href="' + url + '">' + t['source'] + '</a></p></section></body></html>'
        data['EPUB/text/format-note.xhtml'] = note.encode()
        nav = xml(data['EPUB/nav.xhtml'])
        toc = nav.xpath('.//h:nav[@*[local-name()="type"]="toc"]/h:ol', namespaces=NS)
        assert len(toc) == 1
        li = etree.Element('{' + NS['h'] + '}li')
        a = etree.SubElement(li, '{' + NS['h'] + '}a', href='text/format-note.xhtml#format-note')
        a.text = t['title']
        toc[0].insert(0, li)
        data['EPUB/nav.xhtml'] = etree.tostring(nav, xml_declaration=True, encoding='utf-8')
        ncx = xml(data['EPUB/toc.ncx'])
        ncx_ns = {'n': 'http://www.daisy.org/z3986/2005/ncx/'}
        uid = ncx.xpath('./n:head/n:meta[@name="dtb:uid"]', namespaces=ncx_ns)
        assert len(uid) == 1
        uid[0].set('content', edition_id)
        navmap = ncx.find('n:navMap', ncx_ns)
        point = etree.Element('{' + ncx_ns['n'] + '}navPoint', id='format-note')
        label = etree.SubElement(point, '{' + ncx_ns['n'] + '}navLabel')
        etree.SubElement(label, '{' + ncx_ns['n'] + '}text').text = t['title']
        etree.SubElement(point, '{' + ncx_ns['n'] + '}content', src='text/format-note.xhtml#format-note')
        navmap.insert(1, point)
        data['EPUB/toc.ncx'] = etree.tostring(ncx, xml_declaration=True, encoding='utf-8')
        changed = [name for name in old_data if old_data[name] != data[name]]
        assert set(changed) <= {figure_member, 'EPUB/content.opf', 'EPUB/nav.xhtml', 'EPUB/toc.ncx', 'EPUB/text/title_page.xhtml'}
        assert all(data[name] == old_data[name] for name in names if name.startswith('EPUB/text/ch') and name != figure_member)
        with zipfile.ZipFile(destination, 'w') as target:
            for entry in original.infolist():
                target.writestr(entry, data[entry.filename])
            extra = zipfile.ZipInfo('EPUB/text/format-note.xhtml', (2026, 10, 3, 0, 0, 0))
            extra.compress_type = zipfile.ZIP_DEFLATED
            target.writestr(extra, data[extra.filename])
    return {'source_sha256': SOURCE_HASHES[language], 'corrected_sha256': digest(destination.read_bytes()),
            'changed_members': sorted(changed), 'added_members': ['EPUB/text/format-note.xhtml'],
            'course_content_rewritten': False, 'figure_alternative_text_preserved': True}


def course_blocks(doc):
    # Pandoc's EPUB reader imports hidden navigation as raw HTML and a landmarks
    # list. Preserve every chapter and its filename anchor, not this UI-only list.
    start = next(i for i, block in enumerate(doc['blocks'])
                 if block.get('t') == 'Para' and 'ch001.xhtml' in json.dumps(block))
    blocks = doc['blocks'][start:]
    assert sum(block.get('t') == 'Div' for block in blocks) == 15
    return blocks


def export_source(inputs, output, language, executable):
    work = output / language
    work.mkdir(parents=True, exist_ok=True)
    original = inputs / (language + '.epub')
    repaired = work / f'03-b80-{language}.epub'
    repair = repair_epub(original, repaired, language)
    original_ast = json.loads(pandoc(executable, ['-f', 'epub', '-t', 'json', str(original)]))
    repaired_ast = json.loads(pandoc(executable, ['-f', 'epub', '-t', 'json', str(repaired)]))
    source_blocks = course_blocks(original_ast)
    target_blocks = course_blocks(repaired_ast)
    signature = content_signature(source_blocks)
    assert signature == content_signature(target_blocks), 'EPUB body semantics changed'
    assert len(signature['math']) == 272
    doc = copy.deepcopy(repaired_ast)
    doc['blocks'] = target_blocks
    # Include the same localized format note in the print/TeX version.
    note_blocks = json.loads(pandoc(executable, ['-f', 'html', '-t', 'json'],
        ('<h1>' + TEXT[language]['title'] + '</h1>' + ''.join('<p>' + html.escape(TEXT[language][key]) + '</p>' for key in ('notice', 'repair', 'scope', 'latex'))).encode()))['blocks']
    doc['blocks'] = note_blocks + doc['blocks']
    doc['meta']['author'] = {'t': 'MetaList', 'c': [{'t': 'MetaString', 'c': TEXT[language]['contributors']}]}
    doc['meta']['date'] = {'t': 'MetaString', 'c': '2026-10-03'}
    doc['meta']['lang'] = {'t': 'MetaString', 'c': language}
    # Preserve long code and paths without running them or clipping at the margin.
    # No discretionary hyphens are inserted into code. Native Quarto remains master.
    doc['meta']['header-includes'] = {'t': 'MetaBlocks', 'c': [{'t': 'RawBlock', 'c': ['latex',
        r'\usepackage{fvextra}' + '\n' +
        r'\DefineVerbatimEnvironment{verbatim}{Verbatim}{breaklines=true,breakanywhere=true,fontsize=\small}' + '\n' +
        r'\usepackage{caption}' + '\n' +
        r'\usepackage{needspace}' + '\n' +
        r'\captionsetup{labelformat=empty}' + '\n' +
        r'\DeclareTOCStyleEntries[pagenumberwidth=3em]{tocline}{chapter,section,subsection}' + '\n' +
        r'\setlength{\emergencystretch}{5em}'
    ]}]}
    # Materialize the unchanged figure rather than leaving it in Pandoc's media bag.
    with zipfile.ZipFile(repaired) as archive:
        for name in archive.namelist():
            if name.startswith('EPUB/media/'):
                relative = name.removeprefix('EPUB/')
                target = work / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))
    for node in walk(doc['blocks']):
        if node.get('t') == 'Image':
            assert node['c'][2][0] == 'media/file0.png'
    write_json(work / 'FROZEN_DOCUMENT.json', doc)
    tex_args = ['-f', 'json', '-t', 'latex', '--standalone', '--toc', '--top-level-division=chapter',
                '--syntax-highlighting=none', '-V', 'documentclass=scrreprt', '-V', 'papersize=a4',
                '-V', 'geometry:margin=25mm', '-V', 'fontsize=11pt', '-V', 'mainfont=DejaVu Serif',
                '-V', 'monofont=DejaVu Sans Mono']
    tex, numeric_cells = group_numeric_cells(pandoc(executable, tex_args, json.dumps(print_document(doc), ensure_ascii=False).encode()))
    (work / f'01-b80-{language}.tex').write_bytes(tex)
    # Inspect a metadata-free round-trip before declaring the source suitable.
    body_tex = pandoc(executable, ['-f', 'json', '-t', 'latex', '--syntax-highlighting=none'],
                      json.dumps(print_document({**doc, 'meta': {}, 'blocks': target_blocks}), ensure_ascii=False).encode())
    body_tex, body_numeric_cells = group_numeric_cells(body_tex)
    assert numeric_cells == body_numeric_cells
    roundtrip = json.loads(pandoc(executable, ['-f', 'latex', '-t', 'json'], body_tex))
    roundtrip_sig = content_signature(roundtrip['blocks'])
    comparisons = {key: signature[key] == roundtrip_sig[key] for key in signature}
    write_json(work / 'ROUNDTRIP_DIAGNOSTIC.json', {'comparison': comparisons,
               'original': signature, 'latex_roundtrip': roundtrip_sig})
    original_semantics = semantic_signature(source_blocks)
    roundtrip_semantics = semantic_signature(roundtrip['blocks'])
    semantic_comparisons = {key: original_semantics[key] == roundtrip_semantics[key] for key in original_semantics}
    write_json(work / 'SEMANTIC_ROUNDTRIP.json', {'comparison': semantic_comparisons,
               'numeric_cells_grouped': numeric_cells, 'original': original_semantics,
               'latex_roundtrip': roundtrip_semantics})
    summary = {'schema': 'b80-format-repair/1', 'language': language, 'epub_repair': repair,
               'original_epub_semantics_unchanged': True, 'formulas': len(signature['math']),
               'code_blocks': len(signature['code_blocks']), 'raw_ast_roundtrip': comparisons,
               'semantic_roundtrip': semantic_comparisons, 'numeric_cells_grouped': numeric_cells,
               'tex_sha256': digest(tex), 'pdf_built': False, 'publication_performed': False}
    write_json(work / 'SOURCE_EXPORT_RECEIPT.json', summary)
    assert all(semantic_comparisons.values()), 'Semantic round-trip incomplete; inspect SEMANTIC_ROUNDTRIP.json'
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pandoc', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(ROOT / 'outputs')
    assert args.inputs.resolve() != args.output.resolve()
    result = [export_source(args.inputs, args.output, language, args.pandoc) for language in ('id', 'en')]
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
