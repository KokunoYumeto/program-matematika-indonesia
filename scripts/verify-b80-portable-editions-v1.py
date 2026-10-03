"""Read public native editions; verify bytes and routes without executing source code."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parent / 'course-formats-v1'))
from course_formats import archive_inventory, checked_member, decode, epub_evidence, xml, NS

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    'id': ('v2026.08.22.1', 'Komputasi-Matematis-dan-Eksperimen-yang-Dapat-Direproduksi',
           'O002_B80_ID_EDITABLE_SOURCE_2026-08-22-1.zip', [754845, 291212, 316923],
           ['f9d3df201c03107be3a3e6f61dd6798485cf20bc35ae14f2911ab212789b5038',
            '8e9e35dd54be8524a8b7752df0a7285749db4c80fc5a10271eb841c01c0c748d',
            'a9dcdc18481b3dc88beee3006d46f1b8187815623534df523bbc70e3e011b9f9']),
    'en': ('v2026.08.31.en1', 'Mathematical-Computing-and-Reproducible-Experiments',
           'O002_B80_EN_EDITABLE_SOURCE_2026-08-31.zip', [774069, 295164, 438288],
           ['12aedcef4d00df81f4d269ac14eb7fc545fbfc057572b6942f15303506e604b2',
            'ed1f8b3e93e56313f27f03f93d1941e39a5485af9975d26f53deef454285e0d8',
            '79005c4717b834ea8b53a292ce01eae293e46528310aff0d86d5ebf36ba2e697']),
}


def identity(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def acquire(url, target, expected_bytes, expected_sha256):
    # No account, cookies or API token. Do not retain signed redirect URLs.
    request = urllib.request.Request(url, headers={'User-Agent': 'Course-format-readback/1'})
    with urllib.request.urlopen(request, timeout=30) as response:
        assert response.status == 200
        raw = response.read(expected_bytes + 1)
    assert len(raw) == expected_bytes, 'Public file size differs: ' + url
    assert identity(raw)['sha256'] == expected_sha256, 'Public file hash differs: ' + url
    if target.exists():
        assert target.read_bytes() == raw, 'Existing local witness differs: ' + target.name
    else:
        target.write_bytes(raw)
    return {'url': url, 'status': 200, **identity(raw)}


def source_evidence(path):
    with zipfile.ZipFile(path) as source:
        names = archive_inventory(source)
        manifest = decode(source.read('BUNDLE_MANIFEST.json'))
        rows = manifest.get('entries', manifest.get('files'))
        assert isinstance(rows, list)
        assert len({row['path'] for row in rows}) == len(rows)
        assert {row['path'] for row in rows} | {'BUNDLE_MANIFEST.json'} == names
        for row in rows:
            checked_member(source, row)
        catalog = decode(source.read('backend/catalog.json'))
        units = catalog['units']
        assert len(units) == 14 and len({row['id'] for row in units}) == 14
        assert {row['reader_path'] for row in units} == {
            name for name in names if name.startswith('source/units/') and name.endswith('.qmd')}
        for unit in units:
            text = source.read(unit['reader_path']).decode('utf-8')
            assert all(section in text for section in unit['sections'])
            assert all(exercise in text for exercise in unit['exercises'])
        for required in ('_quarto.yml', 'index.qmd', 'README.md', 'LICENSE-TEXT.md', 'LICENSE-CODE.md'):
            assert required in names
        return units, {
            'members': len(names), 'manifest_payloads_verified': len(rows),
            'unit_sources_verified': len(units),
            'exercises': sum(len(unit['exercises']) for unit in units),
            'catalogue': identity(source.read('backend/catalog.json')),
            'native_format': 'Quarto Markdown (.qmd)',
            'cumulative_latex_present': any(name.endswith('.tex') for name in names),
            'source_code_executed': False, 'independent_rebuild': False,
            'proof_of_build_reproducibility': False,
        }


def inspect_edition(directory, language):
    units, source = source_evidence(directory / f'{language}-source.zip')
    epub = directory / f'{language}.epub'
    anchors = {}
    documents = {}
    with zipfile.ZipFile(epub) as package:
        for name in sorted(archive_inventory(package)):
            if name.endswith('.xhtml'):
                tree = xml(package.read(name))
                documents[name] = tree
                for anchor in tree.xpath('//@id'):
                    anchors.setdefault(anchor, []).append(name)
    pdf = PdfReader(directory / f'{language}.pdf')
    assert not pdf.is_encrypted
    bookmarks = [row for row in pdf.outline if isinstance(row, dict)]
    assert len(bookmarks) == 15
    routes = []
    for unit in units:
        anchor = unit['sections'][0]
        assert len(anchors.get(anchor, [])) == 1, 'Unit anchor missing/ambiguous in EPUB: ' + anchor
        member = anchors[anchor][0]
        element = documents[member].xpath('//*[@id=$anchor]', anchor=anchor)[0]
        chapters = [node for node in [element, *element.iterancestors()]
                    if 'level1' in node.get('class', '').split()]
        assert len(chapters) == 1 and chapters[0].get('id')
        heading = chapters[0].find('h:h1', NS)
        assert heading is not None
        title = re.sub(r'^\d+\s+', '', ' '.join(''.join(heading.itertext()).split()))
        assert title == unit['title'], 'EPUB chapter title differs from native catalogue'
        matching = [row for row in bookmarks if str(row.get('/Title')) == unit['title']]
        assert len(matching) == 1, 'Native title missing/ambiguous in PDF bookmarks: ' + unit['id']
        page = pdf.get_destination_page_number(matching[0]) + 1
        assert 1 <= page <= len(pdf.pages)
        routes.append({'id': unit['id'], 'source': unit['reader_path'],
                       'source_anchor': anchor,
                       'epub': {'member': member, 'fragment': chapters[0].get('id')},
                       'pdf': {'bookmark_title': unit['title'], 'page': page,
                               'mapping': 'exact_native_catalogue_title_to_pdf_outline'}})
    assert [row['pdf']['page'] for row in routes] == sorted(set(row['pdf']['page'] for row in routes))
    native_locations = [{'id': row['id'], 'epub': {'member': row['epub']['member'],
                                                  'fragment': row['source_anchor']}} for row in routes]
    evidence = epub_evidence(epub, routes, language, native_locations=native_locations)
    checker_path = directory / (language + '-epubcheck.json')
    if checker_path.exists():
        checker_raw = checker_path.read_bytes()
        checked = decode(checker_raw)
        counts = {key: checked['checker'][key] for key in ('nFatal', 'nError', 'nWarning')}
        messages = [{'code': row['ID'], 'severity': row['severity'],
                     'locations': [{'path': loc['path'], 'line': loc.get('line'), 'column': loc.get('column')}
                                   for loc in row.get('locations', [])]}
                    for row in checked['messages']]
        evidence['epubcheck_run'] = True
        evidence['epubcheck'] = {'version': checked['checker']['checkerVersion'], **counts,
                                'status': 'pass' if not any(counts.values()) else 'existing_edition_has_findings',
                                'report_identity': identity(checker_raw), 'messages': messages}
        if counts['nError']:
            assert counts == {'nFatal': 0, 'nError': 1, 'nWarning': 0}, 'Unexpected EPUBCheck result'
            assert messages[0]['code'] == 'RSC-005'
            assert messages[0]['locations'][0]['path'] == 'EPUB/text/ch007.xhtml'
            assert 'attribute "alt" not allowed here' in checked['messages'][0]['message']
            containers = documents['EPUB/text/ch007.xhtml'].xpath('.//h:div[@alt]', namespaces=NS)
            assert len(containers) == 1
            images = containers[0].xpath('.//h:img[@alt]', namespaces=NS)
            assert len(images) == 1 and images[0].get('alt') == containers[0].get('alt')
            evidence['epubcheck']['finding'] = 'One invalid duplicated alt attribute on the figure container; identical alternative text exists on its image. Native edition unchanged; repair remains open.'
    # These are independent route/byte checks, not proof that all prose was translated correctly.
    return {'source_archive': source, 'pdf': {'pages': len(pdf.pages),
            'unit_destinations_verified': len(routes), 'tagged': bool(pdf.trailer['/Root'].get('/StructTreeRoot'))},
            'epub': evidence, 'routes': routes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    directory = args.directory.resolve()
    assert directory.is_relative_to(ROOT / 'outputs')
    directory.mkdir(parents=True, exist_ok=True)
    facts, editions = [], {}
    for language, (tag, stem, source_name, sizes, hashes) in SPECS.items():
        repository = 'https://github.com/KokunoYumeto/mathematical-computing-reproducible-experiments-' + language
        for name, target, size, sha256 in zip([stem + '.pdf', stem + '.epub', source_name],
                                     [language + '.pdf', language + '.epub', language + '-source.zip'], sizes, hashes):
            facts.append(acquire(repository + '/releases/download/' + tag + '/' + name,
                                 directory / target, size, sha256))
        editions[language] = {'release': repository + '/releases/tag/' + tag,
                              'version': tag, **inspect_edition(directory, language)}
    assert [row['id'] for row in editions['id']['routes']] == [row['id'] for row in editions['en']['routes']]
    report = {'schema': 'central-supplemental-reader-evidence/1',
              'status': 'published_and_anonymously_verified', 'course_id': 'B80',
              'verified_at_utc': datetime.now(timezone.utc).isoformat(),
              'public_readback': facts, 'editions': editions,
              'limitations': ['No independent book rebuild or mathematical/linguistic review.',
                              'EPUBCheck finds one invalid figure-container alt attribute in each original EPUB; these are not advertised as fully conformant EPUBs.',
                              'No cumulative LaTeX found in either native source archive; this requirement remains open.',
                              'EPUB local links checked; external references are not downloaded.',
                              'Published editions unchanged; source archives are not claimed to satisfy all current delivery requirements.'],
              'provenance': {'en': 'Edition integration and checks: OpenAI Codex - GPT-6 Astra, Ultra effort. Original edition credits and licences remain unchanged.',
                             'id': 'Integrasi edisi dan pemeriksaan: OpenAI Codex - GPT-6 Astra, upaya Ultra. Atribusi dan lisensi edisi asli tidak diubah.'},
              'verifier': {'path': 'scripts/verify-b80-portable-editions-v1.py', **identity(Path(__file__).read_bytes())}}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'state': 'pass', 'public_files': len(facts), 'bytes': sum(row['bytes'] for row in facts),
                      'editions': {lang: {'units': len(row['routes']), 'pages': row['pdf']['pages'],
                                           'epub': row['epub'], 'source': row['source_archive']}
                                   for lang, row in editions.items()}}))


if __name__ == '__main__':
    main()
