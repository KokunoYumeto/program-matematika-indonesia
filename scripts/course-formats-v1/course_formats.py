"""Verify a native course-format handoff and assemble an offline reader directory.

No source execution, PDF/EPUB conversion, network access, or publication occurs.
Original course, review and language states remain unchanged. Python 3.11+;
pypdf and lxml are needed for actual PDF/EPUB navigation checks.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import posixpath
import re
import shutil
import stat
import zipfile
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from lxml import etree
from pypdf import PdfReader


class InvalidPackage(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidPackage(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(path):
    result = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
            size += len(chunk)
    return {'bytes': size, 'sha256': result.hexdigest()}


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def safe_name(value):
    require(isinstance(value, str) and value, 'Empty path')
    require(not re.search(r'[\\:\x00-\x1f]', value), 'Unsafe path: ' + value)
    parts = value.split('/')
    require(all(p not in ('', '.', '..') and p == p.rstrip(' .') for p in parts),
            'Noncanonical path: ' + value)
    require(not any(re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', p, re.I)
                    for p in parts), 'Reserved path: ' + value)
    return value


def confined(root, name):
    path = root / safe_name(name)
    cursor = path
    while cursor != root:
        require(not cursor.is_symlink() and not getattr(cursor, 'is_junction', lambda: False)(),
                'Reparse entry in input: ' + name)
        cursor = cursor.parent
    require(path.resolve().is_relative_to(root.resolve()), 'Path outside package: ' + name)
    return path


def checked_file(root, record):
    path = confined(root, record['path'])
    actual = identity(path)
    require(type(record.get('bytes')) is int and record['bytes'] == actual['bytes'],
            'Size mismatch: ' + record['path'])
    require(isinstance(record.get('sha256'), str) and
            re.fullmatch(r'[a-fA-F0-9]{64}', record['sha256']) and
            actual['sha256'] == record['sha256'].lower(), 'Hash mismatch: ' + record['path'])
    return path


def archive_inventory(archive):
    names = {}
    for entry in archive.infolist():
        require(not entry.is_dir(), 'Archive has directory entry; expected file-only inventory')
        name = safe_name(entry.filename)
        require(name.casefold() not in names, 'Duplicate/case-colliding archive path: ' + name)
        require(not entry.flag_bits & 1, 'Encrypted ZIP member: ' + name)
        mode = entry.external_attr >> 16
        require(stat.S_IFMT(mode) in (0, stat.S_IFREG), 'Non-regular ZIP member: ' + name)
        names[name.casefold()] = name
    return set(names.values())


def checked_member(archive, record):
    name = safe_name(record['path'])
    info = archive.getinfo(name)
    require(type(record.get('bytes')) is int and info.file_size == record['bytes'],
            'ZIP size mismatch: ' + name)
    hash_value = hashlib.sha256()
    with archive.open(name) as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            hash_value.update(chunk)
    require(hash_value.hexdigest() == record['sha256'].lower(), 'ZIP hash mismatch: ' + name)


def source_closure(archive_path, manifest_raw, formats, units):
    with zipfile.ZipFile(archive_path) as archive:
        names = archive_inventory(archive)
        closure = decode(archive.read('PACKAGE_CONTENTS.json'))
        require(closure.get('schema') == 'course-editable-source-closure/1', 'Unknown source closure')
        records = closure['files']
        declared = [r['path'] for r in records]
        require(len(declared) == len(set(declared)), 'Duplicate source closure record')
        require(set(declared) | {'PACKAGE_CONTENTS.json'} == names, 'Undeclared/missing ZIP payload')
        for record in records:
            checked_member(archive, record)
        require(archive.read('SOURCE_MANIFEST.json') == manifest_raw, 'ZIP manifest differs from intake')
        tex = next(f for f in formats if f['path'].endswith('.tex'))
        checked_member(archive, tex)
        manifest = decode(manifest_raw)
        for record in manifest['files']:
            checked_member(archive, record)
        for unit in units:
            checked_member(archive, {'path': unit['source'], 'bytes': unit['bytes'],
                                     'sha256': unit['source_sha256']})
        return {'members': len(names), 'payloads_verified': len(records),
                'manifest_payloads_verified': len(manifest['files']),
                'direct_tex_matches_source_zip': True,
                'rebuild_executed': False, 'source_code_executed': False}


NS = {'h': 'http://www.w3.org/1999/xhtml', 'm': 'http://www.w3.org/1998/Math/MathML',
      'o': 'http://www.idpf.org/2007/opf', 'dc': 'http://purl.org/dc/elements/1.1/',
      'c': 'urn:oasis:names:tc:opendocument:xmlns:container'}


def xml(raw):
    require(b'<!ENTITY' not in raw.upper(), 'XML entities are not permitted')
    return etree.fromstring(raw, etree.XMLParser(resolve_entities=False, no_network=True))


def local_reference(member, href):
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        require(parsed.scheme in ('https', 'http', 'mailto'), 'Unsafe external reference')
        return None
    require(not parsed.query and not parsed.path.startswith('/'), 'Nonportable internal reference')
    decoded = unquote(parsed.path)
    require(not re.search(r'[\\:\x00-\x1f]', decoded), 'Unsafe internal reference')
    target = posixpath.normpath(posixpath.join(posixpath.dirname(member), decoded)) if decoded else member
    return safe_name(target), unquote(parsed.fragment)


def epub_evidence(epub_path, routes, language, expected_math=None, native_locations=None):
    with zipfile.ZipFile(epub_path) as archive:
        names = archive_inventory(archive)
        first = archive.infolist()[0]
        require(first.filename == 'mimetype' and first.compress_type == zipfile.ZIP_STORED,
                'EPUB mimetype must be first and uncompressed')
        require(archive.read('mimetype') == b'application/epub+zip', 'Wrong EPUB mimetype')
        container = xml(archive.read('META-INF/container.xml'))
        roots = container.xpath('./c:rootfiles/c:rootfile', namespaces=NS)
        require(len(roots) == 1, 'Expected one EPUB package document')
        opf_name = safe_name(roots[0].get('full-path'))
        opf = xml(archive.read(opf_name))
        languages = opf.xpath('./o:metadata/dc:language/text()', namespaces=NS)
        require(languages == [language], 'EPUB language differs from source language')
        items = {}
        nav = []
        for item in opf.xpath('./o:manifest/o:item', namespaces=NS):
            item_id = item.get('id')
            require(item_id not in items, 'Duplicate EPUB item ID')
            target = local_reference(opf_name, item.get('href'))
            require(target is not None and target[0] in names, 'Missing/external EPUB resource')
            require(not target[1], 'Manifest resource includes fragment')
            items[item_id] = target[0]
            if 'nav' in item.get('properties', '').split():
                nav.append(target[0])
        require(len(nav) == 1, 'EPUB must have one navigation document')
        spine = []
        for item in opf.xpath('./o:spine/o:itemref', namespaces=NS):
            require(item.get('idref') in items, 'Missing EPUB spine item')
            if item.get('linear', 'yes') != 'no':
                spine.append(items[item.get('idref')])
        require(len(spine) == len(set(spine)), 'Duplicate EPUB reading-order entry')
        documents = {}
        for member in names:
            if member.endswith('.xhtml'):
                tree = xml(archive.read(member))
                require(not tree.xpath('.//h:script', namespaces=NS), 'Scripted EPUB is not supported')
                require(not tree.xpath('.//m:merror', namespaces=NS), 'EPUB contains MathML errors')
                ids = tree.xpath('//@id')
                require(len(ids) == len(set(ids)), 'Duplicate EPUB fragment')
                documents[member] = (tree, set(ids))
        checked_links = 0
        external_links = 0
        for member, (tree, _) in documents.items():
            for href in tree.xpath('//@href | //@src'):
                target = local_reference(member, href)
                if target is None:
                    external_links += 1
                    continue
                require(target[0] in names, 'Broken EPUB resource link: ' + target[0])
                if target[1]:
                    require(target[0] in documents and target[1] in documents[target[0]][1],
                            'Broken EPUB fragment: ' + str(target))
                checked_links += 1
        ordered_positions = []
        nav_targets = [local_reference(nav[0], href) for href in
                       documents[nav[0]][0].xpath('.//h:nav[@*[local-name()="type"]="toc"]//h:a/@href', namespaces=NS)]
        for route in routes:
            location = route['epub']
            member, fragment = location['member'], location['fragment']
            require(member in spine, 'Lesson absent from EPUB reading order')
            require(fragment in documents[member][1], 'Lesson EPUB fragment missing')
            require((member, fragment) in nav_targets, 'Lesson absent from EPUB navigation')
            ordered_positions.append(spine.index(member))
        require(ordered_positions == sorted(set(ordered_positions)), 'EPUB lesson order differs')
        for location in native_locations or []:
            member, fragment = location['epub']['member'], location['epub']['fragment']
            require(member in spine and member in documents and fragment in documents[member][1],
                    'Native EPUB anchor does not resolve: ' + str(location.get('id')))
        formulas = []
        for member in spine:
            # EPUB navigation can be a linear spine item and repeat formula
            # headings. It is navigation, not another occurrence in source text.
            if member not in documents or member in nav:
                continue
            for math in documents[member][0].xpath('.//m:math', namespaces=NS):
                annotations = math.xpath('.//m:annotation[@encoding="application/x-tex"]', namespaces=NS)
                require(len(annotations) == 1, 'Formula lacks unique editable TeX annotation')
                formulas.append(annotations[0].text or '')
        result = {'spine_items': len(spine), 'local_links_verified': checked_links,
                  'external_links_not_fetched': external_links, 'formula_regions': len(formulas),
                  'navigation_formula_regions': sum(len(documents[n][0].xpath('.//m:math', namespaces=NS)) for n in nav),
                  'language': language, 'document_routes_verified': len(routes),
                  'native_locations_verified': len(native_locations or []),
                  'epubcheck_run': False, 'visual_inspection_performed': False}
        if expected_math is not None:
            # Compare order, not just a multiset: swapped formula occurrences must fail.
            canonical = lambda s: re.sub(r'\s+', '', s)
            require([canonical(s) for s in formulas] == [canonical(r['tex']) for r in expected_math],
                    'EPUB formula reading order differs from supplied formula ledger')
            for row in expected_math:
                require(digest(row['tex'].encode()) == row['tex_sha256'], 'Formula ledger hash mismatch')
            result['ordered_formula_ledger_comparison'] = 'pass_whitespace_normalized'
            result['formula_ledger_is_independent_source_parse'] = False
        return result


def pdf_evidence(pdf_path, routes, native_locations=None):
    reader = PdfReader(pdf_path)
    require(not reader.is_encrypted, 'Encrypted PDF')
    destinations = reader.named_destinations
    for row in [*routes, *(native_locations or [])]:
        location = row['pdf']
        require(location['named_destination'] in destinations, 'Missing PDF destination')
        page = reader.get_destination_page_number(destinations[location['named_destination']]) + 1
        require(type(location['page']) is int and page == location['page'] and 1 <= page <= len(reader.pages),
                'Wrong PDF lesson page')
        if 'page_index' in location:
            require(location['page_index'] == page - 1, 'PDF page-index mismatch')
    mark_info = reader.trailer['/Root'].get('/MarkInfo', {})
    metadata = reader.metadata or {}
    return {'pages': len(reader.pages), 'document_routes_verified': len(routes),
            'native_locations_verified': len(native_locations or []),
            'tagged': bool(mark_info.get('/Marked', False)),
            'title_present': bool(metadata.get('/Title')), 'author_present': bool(metadata.get('/Author')),
            'visual_inspection_performed': False}


def handoff_contract(root, handoff):
    """Adapt a public-source packet explicitly, without rewriting its witnesses.

    Source publication and local export validation are not permission to publish.
    Every evidence mapping is checked before using the producer's counts.
    """
    schema = handoff.get('schema')
    if schema in ('programme-course-format-handoff/1', 'programme-course-format-handoff/2'):
        return handoff
    require(schema == 'programme-current-public-course-format-handoff/1', 'Unsupported handoff schema')
    evidence = handoff['evidence']
    records = {row['path']: row for row in evidence}
    require(len(records) == len(evidence), 'Duplicate public handoff evidence')
    for row in evidence:
        checked_file(root, row)
    required = ('FINAL_EXPORT_RECEIPT.json', 'SOURCE_MANIFEST.json', 'FORMAT_LOCATORS.json',
                'FORMAT_LOCATORS_VALIDATION.json', 'ISOLATED_REPLAY_RECEIPT.json')
    require(all(name in records for name in required), 'Missing public handoff evidence binding')
    receipt = decode(checked_file(root, records['FINAL_EXPORT_RECEIPT.json']).read_bytes())
    require(receipt.get('schema') == 'programme-course-export-acceptance/2', 'Unsupported export receipt')
    require(receipt['course_id'] == handoff['course_id'], 'Public receipt course differs')
    require(receipt['public_source_binding'] == handoff['source'], 'Public source binding differs')
    source = handoff['source']
    require(re.fullmatch(r'[a-f0-9]{40}', source['commit']) is not None, 'Unpinned public source')
    require(re.fullmatch(r'[a-f0-9]{64}', source['archive_sha256']) is not None, 'Missing public archive hash')
    for key in ('repository', 'archive_url'):
        parsed = urlsplit(source[key])
        require(parsed.scheme == 'https' and parsed.netloc and not parsed.username and not parsed.password,
                'Unsafe public source URL')
    receipt_evidence = receipt['evidence']
    package_records = [r for r in receipt_evidence if r['path'] == 'SOURCE_PACKAGE_RECEIPT.json']
    require(len(package_records) == 1, 'Missing source package count witness')
    package = decode(checked_file(root, package_records[0]).read_bytes())
    require(package.get('schema') == 'course-source-package-check/1', 'Unsupported source package witness')
    formats = handoff['files_in_public_order']
    source_zip = next((r for r in formats if r['path'].endswith('.zip')), None)
    require(source_zip is not None and package['zip']['sha256'] == source_zip['sha256']
            and package['zip']['bytes'] == source_zip['bytes'], 'Package witness describes different ZIP')
    coverage = handoff['coverage']
    require(coverage['main_lessons'] + coverage['common_readings'] == receipt['source_lessons'],
            'Public reading-unit count differs')
    require(coverage['formula_regions'] == receipt['math_regions'], 'Public formula count differs')
    require(coverage['pdf_pages'] == receipt['pdf_pages'], 'Public PDF count differs')
    return {**handoff, 'receipt': records['FINAL_EXPORT_RECEIPT.json'],
            'locators': records['FORMAT_LOCATORS.json'], 'source_manifest': records['SOURCE_MANIFEST.json'],
            'locator_validation': records['FORMAT_LOCATORS_VALIDATION.json'],
            'pdf_pages': coverage['pdf_pages'], 'ordered_formula_regions': coverage['formula_regions'],
            'native_format_locators': coverage['native_format_locators'], 'source_zip_members': package['members']}


def validate(root):
    root = root.resolve(strict=True)
    handoff_raw = (root / 'HANDOFF.json').read_bytes()
    handoff = handoff_contract(root, decode(handoff_raw))
    receipt_path = checked_file(root, handoff['receipt'])
    locator_path = checked_file(root, handoff['locators'])
    receipt, locators = decode(receipt_path.read_bytes()), decode(locator_path.read_bytes())
    require(locators.get('schema') in ('native-course-format-entry-locators/1', 'course-format-locator-index/1'),
            'Unsupported locator schema')
    require(handoff['course_id'] == locators['course_id'] == receipt['course_id'], 'Course identity mismatch')
    require(locators['export_receipt'] == handoff['receipt'], 'Receipt binding mismatch')
    manifest_path = checked_file(root, locators['source_manifest'])
    manifest_raw = manifest_path.read_bytes()
    manifest = decode(manifest_raw)
    require(manifest.get('schema') == 'course-format-source/2', 'Unsupported source schema')
    require(manifest['course_id'] == handoff['course_id'], 'Source course mismatch')
    units = manifest['units']
    require(units and len({u['id'] for u in units}) == len(units), 'Empty/duplicate lesson selection')
    if handoff['schema'] == 'programme-current-public-course-format-handoff/1':
        require(manifest['public_source'] == handoff['source'], 'Manifest public source differs')
        require(len(units) == receipt['source_lessons'], 'Manifest reading-unit count differs')
        require(sum(u.get('selection_kind', 'lesson') == 'lesson' for u in units) == handoff['coverage']['main_lessons'],
                'Manifest main-lesson count differs')
        require(sum(u.get('selection_kind') == 'common reading' for u in units) == handoff['coverage']['common_readings'],
                'Manifest common-reading count differs')
    formats = handoff['files_in_public_order']
    require(formats == receipt['files_in_public_order'], 'Format bindings differ')
    if locators['schema'] == 'native-course-format-entry-locators/1':
        require(formats == locators['format_files'], 'Locator file bindings differ')
    else:
        # Native-anchor sidecars bind rendered routes and TeX, not the source ZIP.
        require(len(locators['format_files']) == 3 and
                {f['path'] for f in locators['format_files']} ==
                {f['path'] for f in formats if not f['path'].endswith('.zip')}, 'Incomplete locator bindings')
        require(all(f in formats for f in locators['format_files']), 'Locator edition differs')
    require([Path(f['path']).suffix for f in formats] == ['.pdf', '.tex', '.zip', '.epub'],
            'Expected PDF, direct cumulative TeX, complete source ZIP, EPUB in that order')
    files = {Path(f['path']).suffix: checked_file(root, f) for f in formats}
    for evidence in receipt.get('evidence', []):
        checked_file(root, evidence)
    for key in ('source_manifest', 'locator_validation', 'source_currency'):
        if key in handoff:
            checked_file(root, handoff[key])
    for record in manifest['files']:
        checked_file(root, record)
    native_locations = None
    if locators['schema'] == 'course-format-locator-index/1':
        native_locations = locators['locators']
        by_id = {r['id']: r for r in native_locations}
        require(len(by_id) == len(native_locations), 'Duplicate native locator ID')
        unit_map = {u['id']: u for u in units}
        require([u['lesson_id'] for u in locators['units']] == [u['id'] for u in units], 'Native unit order differs')
        for row in native_locations:
            require(row['course_id'] == handoff['course_id'] and row['lesson_id'] in unit_map,
                    'Foreign native locator')
            unit = unit_map[row['lesson_id']]
            require(row['source']['file'] == unit['source'] and row['source']['bytes'] == unit['bytes'] and
                    row['source']['sha256'].lower() == unit['source_sha256'].lower(), 'Native source binding differs')
            for key, suffix in [('pdf', '.pdf'), ('epub', '.epub')]:
                record = next(f for f in formats if f['path'].endswith(suffix))
                require(row[key]['file'] == record['path'] and row[key]['sha256'].lower() == record['sha256'].lower(),
                        'Native locator format binding differs')
        routes = []
        for native_unit, unit in zip(locators['units'], units):
            require(native_unit['entry_locator_id'] in by_id, 'Missing unit-entry native locator')
            row = by_id[native_unit['entry_locator_id']]
            require(row['lesson_id'] == unit['id'], 'Unit entry belongs to another source')
            require(native_unit['pdf_start_page'] == row['pdf']['page'] and
                    native_unit['epub_member'] == row['epub']['member'], 'Unit entry conflicts with native locator')
            routes.append({'course_id': handoff['course_id'], 'lesson_id': unit['id'], 'title': unit['title'],
                           'source': {'path': row['source']['file'], 'bytes': row['source']['bytes'],
                                      'sha256': row['source']['sha256']},
                           'pdf': row['pdf'], 'epub': row['epub'], 'language': manifest['content_language'],
                           'kind': 'lesson_entry_not_proof_correspondence',
                           'selection_kind': unit.get('selection_kind', 'lesson')})
        require(locators['counts']['native_anchors'] == len(native_locations) == handoff['native_format_locators'],
                'Native locator-count mismatch')
    else:
        routes = locators['locators']
    require([r['lesson_id'] for r in routes] == [u['id'] for u in units], 'Lesson selection/order mismatch')
    for row, unit in zip(routes, units):
        require(row['course_id'] == handoff['course_id'], 'Route course mismatch')
        require(row['language'] == manifest['content_language'], 'Route content-language mismatch')
        require(row['kind'] == 'lesson_entry_not_proof_correspondence', 'Unsupported route semantics')
        require(row['source']['path'] == unit['source'] and row['source']['sha256'].lower() == unit['source_sha256'].lower()
                and row['source']['bytes'] == unit['bytes'], 'Lesson source binding mismatch')
        checked_file(root, row['source'])
        require(row['pdf']['file'] == formats[0]['path'] and row['epub']['file'] == formats[3]['path'],
                'Route names a different edition')
    closure = source_closure(files['.zip'], manifest_raw, formats, units)
    formula_path = root / 'output/FORMULA_INDEX.json'
    formula_ledger = decode(formula_path.read_bytes()) if formula_path.is_file() else None
    epub = epub_evidence(files['.epub'], routes, manifest['content_language'], formula_ledger, native_locations)
    if formula_ledger is not None:
        epub['supplied_formula_ledger'] = {'path': 'output/FORMULA_INDEX.json', **identity(formula_path)}
    pdf = pdf_evidence(files['.pdf'], routes, native_locations)
    require(pdf['pages'] == handoff['pdf_pages'] == receipt['pdf_pages'], 'PDF page-count mismatch')
    require(epub['formula_regions'] == handoff.get('ordered_formula_regions', handoff.get('formulas')), 'Formula-count mismatch')
    require(closure['members'] == handoff['source_zip_members'], 'Source ZIP member-count mismatch')
    warnings = []
    if not pdf['tagged']:
        warnings.append('pdf_not_tagged')
    if not pdf['title_present']:
        warnings.append('pdf_title_metadata_empty')
    report = {'schema': 'verified-course-format-intake/1', 'state': 'byte_and_navigation_checks_pass',
              'course_id': handoff['course_id'], 'content_language': manifest['content_language'],
              'handoff_sha256': digest(handoff_raw), 'manifest_sha256': digest(manifest_raw),
              'source_status_unchanged': manifest['status'], 'selected_documents': len(units),
              'lessons': sum(u.get('selection_kind', 'lesson') == 'lesson' for u in units),
              'common_readings': sum(u.get('selection_kind') == 'common reading' for u in units),
              'editorial_supplements': sum(u.get('selection_kind') == 'supplement' for u in units),
              'entry_routes': routes,
              'native_locations': [{key: row[key] for key in
                                    ('id', 'lesson_id', 'native_anchor', 'label', 'kind', 'source', 'pdf', 'epub')}
                                   for row in native_locations or []],
              'source_closure': closure, 'pdf': pdf, 'epub': epub, 'warnings': warnings,
              'files': formats, 'publication_performed': False, 'source_mathematics_modified': False,
              'limits': ['Not a mathematical, linguistic, or independent source-to-formula audit.',
                         'Not EPUBCheck or a visual rendering check; those are separate.',
                         'Not course admission, full dependency coverage, or publication permission.']}
    if handoff['schema'] == 'programme-current-public-course-format-handoff/1':
        report['public_source_binding'] = handoff['source']
        report['public_source_network_rechecked'] = False
        for key in ('upstream_reader', 'programme'):
            parsed = urlsplit(manifest[key])
            require(parsed.scheme == 'https' and parsed.netloc and not parsed.username and not parsed.password,
                    'Unsafe online navigation URL')
        report['online_navigation'] = {key: manifest[key] for key in ('upstream_reader', 'programme')}
    return report, manifest, routes


COPY = {
    'en': {
        'title': 'Offline course edition', 'nav': 'Interface language', 'downloads': 'Read and download',
        'pdf': 'Read PDF', 'tex': 'Editable cumulative LaTeX', 'zip': 'Complete editable source package',
        'epub': 'Download EPUB', 'lessons': 'Lessons', 'page': 'PDF page', 'source': 'Edition and sources',
        'language': 'Course text language', 'language_names': {'en': 'English', 'id': 'Bahasa Indonesia'},
        'separate': 'Changing this interface does not translate the course. Lesson titles and quoted source notices remain in the course language.',
        'epub_help': 'Open the EPUB in a compatible reading app and use its table of contents. Internal chapter filenames are recorded below; they are not browser deep links.',
        'boundary': 'Lesson navigation, not a map of proofs or a claim that prerequisites are complete.',
        'offline': 'The downloads work offline from this directory. The source ZIP contains the native files and rebuild instructions.',
        'quoted': 'Original source notice', 'provenance': 'Original attribution and format-conversion attribution',
        'checks': 'Verified file identities', 'unreviewed': 'Byte and navigation checks do not add mathematical, linguistic or human review.',
        'credit': 'Offline navigation and intake tooling: OpenAI Codex - GPT-6 Astra, Ultra effort. Course authorship and source licences are unchanged.',
        'tagging': 'The PDF is not tagged for assistive reading. The EPUB has a structured reading order and MathML; assistive-technology performance is not certified.',
        'size': 'bytes', 'copy': 'Copied unchanged', 'content': 'Course content', 'supplement': 'Editorial supplement',
        'locations': 'Named locations in this document', 'exact': 'Open exact PDF location',
        'common': 'Common reading',
        'online': 'Original online course', 'programme': 'Return to the programme (English)',
    },
    'id': {
        'title': 'Edisi luring mata kuliah', 'nav': 'Bahasa antarmuka', 'downloads': 'Baca dan unduh',
        'pdf': 'Baca PDF', 'tex': 'LaTeX kumulatif yang dapat disunting', 'zip': 'Paket lengkap sumber yang dapat disunting',
        'epub': 'Unduh EPUB', 'lessons': 'Pelajaran', 'page': 'Halaman PDF', 'source': 'Edisi dan sumber',
        'language': 'Bahasa isi mata kuliah', 'language_names': {'en': 'Inggris', 'id': 'Bahasa Indonesia'},
        'separate': 'Mengganti bahasa antarmuka tidak menerjemahkan isi mata kuliah. Judul pelajaran dan kutipan keterangan sumber tetap dalam bahasa isi mata kuliah.',
        'epub_help': 'Buka EPUB dengan aplikasi pembaca yang mendukungnya, lalu gunakan daftar isi. Nama berkas bab di dalam EPUB dicantumkan di bawah; nama tersebut bukan tautan langsung peramban.',
        'boundary': 'Navigasi pelajaran, bukan peta bukti atau pernyataan bahwa semua prasyarat telah lengkap.',
        'offline': 'Berkas unduhan dapat dibuka tanpa internet dari direktori ini. ZIP sumber memuat berkas asli dan petunjuk pembuatan ulang.',
        'quoted': 'Kutipan keterangan sumber asli', 'provenance': 'Atribusi asli dan atribusi konversi format',
        'checks': 'Identitas berkas yang telah diverifikasi', 'unreviewed': 'Pemeriksaan bita dan navigasi tidak menambahkan penelaahan matematika, bahasa, atau penelaahan oleh manusia.',
        'credit': 'Navigasi luring dan alat pemeriksaan paket: OpenAI Codex - GPT-6 Astra, upaya Ultra. Kepengarangan mata kuliah dan lisensi sumber tidak berubah.',
        'tagging': 'PDF belum memiliki tag untuk teknologi bantu. EPUB memiliki urutan baca terstruktur dan MathML; kinerjanya dengan teknologi bantu belum disertifikasi.',
        'size': 'bita', 'copy': 'Disalin tanpa perubahan', 'content': 'Isi mata kuliah', 'supplement': 'Suplemen editorial',
        'locations': 'Lokasi berlabel dalam dokumen ini', 'exact': 'Buka lokasi PDF yang tepat',
        'common': 'Bacaan bersama',
        'online': 'Mata kuliah daring asli', 'programme': 'Kembali ke program (bahasa Inggris)',
    },
}


STYLE = '''*{box-sizing:border-box}html{font:18px/1.6 system-ui,sans-serif;color:#203831;background:#f3f6f1}body{margin:0}header,main,footer{max-width:1000px;margin:auto;padding:1.4rem}header{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;border-bottom:1px solid #becbbb}h1{font-size:clamp(1.8rem,5vw,3rem);line-height:1.2}h2{line-height:1.3}a{color:#155e42;overflow-wrap:anywhere}a:focus{outline:3px solid #c87625;outline-offset:4px}.downloads{display:flex;gap:.75rem;flex-wrap:wrap}.downloads a{border:1px solid #7b927f;padding:.7rem 1rem;border-radius:.4rem;background:white}.notice{border-left:4px solid #a57227;background:#fff4df;padding:1rem}li{padding:.65rem 0}code{font-size:.84rem;overflow-wrap:anywhere}blockquote{margin:1rem 0;padding:1rem;background:white;border-left:3px solid #889e8d}summary{cursor:pointer}article{border-top:1px solid #becbbb;margin-top:1rem}footer{font-size:.88rem;border-top:1px solid #becbbb}@media(max-width:500px){html{font-size:16px}header,main,footer{padding:1rem}.downloads a{width:100%}}'''


def reader_html(report, manifest, routes, locale):
    c = COPY[locale]
    esc = lambda s: html.escape(str(s), quote=True)
    content_language = manifest['content_language']
    language_name = c['language_names'].get(content_language.split('-')[0], content_language)
    files = report['files']
    file_link = lambda record: 'files/' + quote(Path(record['path']).name)
    downloads = ''.join(f'<a href="{file_link(f)}"' + (' download' if i else '') +
                        f'>{esc(c[k])}</a>' for i, (f, k) in enumerate(zip(files, ['pdf', 'tex', 'zip', 'epub'])))
    def native_links(lesson):
        rows = [r for r in report.get('native_locations', []) if r['lesson_id'] == lesson]
        if not rows:
            return ''
        items = ''.join(f'<li><span lang="{esc(content_language)}">{esc(r["label"] or r["native_anchor"])}</span><br>'
                        f'<code>{esc(r["native_anchor"])}</code><br>'
                        f'<a href="{file_link(files[0])}#nameddest={quote(r["pdf"]["named_destination"], safe="")}">{esc(c["exact"])}</a>'
                        f' · <a href="{file_link(files[0])}#page={r["pdf"]["page"]}">{esc(c["page"])} {r["pdf"]["page"]}</a>'
                        f'<br>EPUB: <code>{esc(r["epub"]["member"])}#{esc(r["epub"]["fragment"])}</code></li>' for r in rows)
        return f'<details><summary>{esc(c["locations"])} ({len(rows)})</summary><ul>{items}</ul></details>'
    lessons = ''.join(f'<li id="{esc(r["lesson_id"])}"><strong>{esc(r["lesson_id"])}: '
                      f'<span lang="{esc(content_language)}">{esc(r["title"])}</span></strong><br>'
                      + (f'<em>{esc(c["supplement"])}</em><br>' if r.get('selection_kind') == 'supplement' else '') +
                      (f'<em>{esc(c["common"])}</em><br>' if r.get('selection_kind') == 'common reading' else '') +
                      f'<a href="{file_link(files[0])}#page={r["pdf"]["page"]}">{esc(c["page"])} {r["pdf"]["page"]}</a>'
                      f' · EPUB: <code>{esc(r["epub"]["member"])}#{esc(r["epub"]["fragment"])}</code>{native_links(r["lesson_id"])}</li>' for r in routes)
    hashes = ''.join(f'<li><a href="{file_link(f)}" download>{esc(Path(f["path"]).name)}</a><br>'
                     f'{f["bytes"]:,} {esc(c["size"])} · SHA-256 <code>{f["sha256"]}</code></li>' for f in files)
    original_notice = manifest['coverage_note'] + '\n\n' + manifest['export']['rights_notice']
    author = manifest['source_author']
    if isinstance(author, dict):
        author = json.dumps(author, ensure_ascii=False)
    provenance = str(author) + '\n\n' + str(manifest['conversion_author'])
    warning = f'<p class="notice">{esc(c["tagging"])}</p>' if not report['pdf']['tagged'] else ''
    online = report.get('online_navigation', {})
    online_links = ('<p>' + ' · '.join(f'<a href="{esc(online[key])}">{esc(c[label])}</a>'
                    for key, label in [('upstream_reader', 'online'), ('programme', 'programme')]) + '</p>') if online else ''
    return f'''<!doctype html>
<html lang="{locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'"><title>{esc(manifest['title'])} - {esc(c['title'])}</title><style>{STYLE}</style></head><body>
<header><span>{esc(c['title'])}</span><nav aria-label="{esc(c['nav'])}"><a href="index.en.html" lang="en">English</a> · <a href="index.id.html" lang="id">Bahasa Indonesia</a></nav></header>
<main><h1 lang="{esc(content_language)}">{esc(manifest['title'])}</h1>{online_links}<p>{esc(c['language'])}: <strong>{esc(language_name)}</strong></p><p>{esc(c['separate'])}</p><p>{esc(c['boundary'])}</p>
<h2>{esc(c['downloads'])}</h2><div class="downloads">{downloads}</div><p>{esc(c['offline'])}</p>{warning}<p>{esc(c['epub_help'])}</p>
<h2>{esc(c['lessons'])}</h2><ol>{lessons}</ol><article><h2>{esc(c['source'])}</h2><h3>{esc(c['quoted'])}</h3><blockquote lang="{esc(content_language)}" style="white-space:pre-wrap">{esc(original_notice)}</blockquote>
<h3>{esc(c['provenance'])}</h3><blockquote lang="{esc(content_language)}" style="white-space:pre-wrap">{esc(provenance)}</blockquote><p>{esc(c['unreviewed'])}</p><details><summary>{esc(c['checks'])}</summary><ul>{hashes}</ul></details></article></main><footer><p>{esc(c['credit'])}</p></footer></body></html>
'''


def assemble(root, destination, report, manifest, routes):
    root, destination = root.resolve(), destination.resolve()
    require(not destination.is_relative_to(root) and not root.is_relative_to(destination),
            'Reader output must be separate from producer intake')
    require(not destination.exists(), 'Output exists; refuse to overwrite')
    # Validate all destinations before creating anything; copied filenames are distinct.
    names = [Path(f['path']).name for f in report['files']]
    require(len({n.casefold() for n in names}) == len(names), 'Colliding output filenames')
    destination.mkdir(parents=True)
    (destination / 'files').mkdir()
    for record in report['files']:
        source = checked_file(root, record)
        target = destination / 'files' / Path(record['path']).name
        with source.open('rb') as src, target.open('xb') as dst:
            shutil.copyfileobj(src, dst, 1024 * 1024)
        require(identity(target) == {'bytes': record['bytes'], 'sha256': record['sha256'].lower()},
                'Copied bytes changed')
    for locale in COPY:
        (destination / f'index.{locale}.html').write_text(reader_html(report, manifest, routes, locale), encoding='utf-8')
    default = 'id' if manifest['content_language'].startswith('id') else 'en'
    (destination / 'index.html').write_text(reader_html(report, manifest, routes, default), encoding='utf-8')
    (destination / 'FORMAT_VERIFICATION.json').write_bytes(json_bytes(report))
    return {'directory': str(destination), 'reader_files': 3, 'unchanged_downloads': len(report['files']),
            'total_bytes': sum(p.stat().st_size for p in destination.rglob('*') if p.is_file()),
            'publication_performed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('intake', type=Path, help='Exact directory containing HANDOFF.json')
    parser.add_argument('--reader', type=Path, help='New offline reader directory; must not exist')
    parser.add_argument('--report', type=Path, help='New private validation receipt; must not exist')
    args = parser.parse_args()
    report, manifest, routes = validate(args.intake)
    if args.reader:
        report['reader'] = assemble(args.intake, args.reader, report, manifest, routes)
    if args.report:
        report_path = args.report.resolve()
        require(not report_path.is_relative_to(args.intake.resolve()), 'Do not write producer intake')
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open('xb') as stream:
            stream.write(json_bytes(report))
    # Full native-location arrays belong in the explicit report, not the console.
    print(json.dumps({key: value for key, value in report.items()
                      if key not in ('entry_routes', 'native_locations')}, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
