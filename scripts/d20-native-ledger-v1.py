"""D20 source-bound metadata intake. Never executes native archive code.

The hash replay proves recorded byte identities, not translation accuracy or
canon applicability. It retains original records and reports stale locators.
"""
import argparse
from bisect import bisect_right
from collections import Counter
from functools import lru_cache
import hashlib
import html
from html.parser import HTMLParser
import io
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('backend/course-capsule-v1/adapters/d20-native-ledger-v1')
SITE = Path('docs/backend/d20/native-ledger')
CACHE = Path('outputs/d20-native-audit-109945924')
AUTHORITY = Path('backend/v2.3/extensions/d20-functional-analysis-v0.1.0/INPUT_AUTHORITIES.json')
MIGRATION = Path('backend/migrations/erdman-functional-analysis-id-v1/MIGRATION_RECEIPT.json')
SOURCE_URL = 'https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_web.zip'
SOURCE_FACT = {'bytes': 262556, 'sha256': '0c667cfa7420b61dda8f8cb4ed9d619db8abbd1b53d17eafe7d4a2e153342e53'}
NATIVE_FACT = {'bytes': 3793368, 'sha256': 'ac5b3ec1fe7c2cf0a17eacce29c920ca5976c0c7d15e37f0ba0476afe9c48e32'}
PREFIX = 'functional-analysis-erdman-id-2026.08.25-backend-artifact-reconciliation/'
TABLES = ('units', 'semantic_units', 'segments', 'terminology', 'terminology_qa', 'corrections', 'rights')


class IdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = Counter()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == 'id':
                self.ids[value] += 1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fact(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')


def safe_zip(data, expected, max_expanded):
    require(fact(data) == expected, 'Archive differs from the selected authority')
    archive = zipfile.ZipFile(io.BytesIO(data))
    names = archive.namelist()
    require(len(names) == len(set(names)), 'Duplicate ZIP member')
    for info in archive.infolist():
        path = PurePosixPath(info.filename)
        require(not path.is_absolute() and '..' not in path.parts and '\\' not in info.filename
                and ':' not in info.filename, 'Unsafe ZIP member')
        require(info.file_size <= 40 * 1024 * 1024, 'Oversized ZIP member')
    require(sum(i.file_size for i in archive.infolist()) <= max_expanded, 'Expanded ZIP exceeds bound')
    require(archive.testzip() is None, 'Invalid ZIP CRC')
    return archive


def recover_source(root=ROOT):
    """One anonymous bounded request; no retries or replacement of existing bytes."""
    destination = root / CACHE / 'OFFICIAL_SOURCE.zip'
    if destination.exists():
        require(fact(destination.read_bytes()) == SOURCE_FACT, 'Cached original differs')
        return destination
    import requests
    session = requests.Session()
    session.trust_env = False
    session.headers.clear()
    session.headers['User-Agent'] = 'PMI-D20-source-replay/1'
    with session.get(SOURCE_URL, stream=True, timeout=(20, 60)) as response:
        response.raise_for_status()
        require('Authorization' not in response.request.headers, 'Authenticated source request')
        data = bytearray()
        for chunk in response.iter_content(65536):
            data.extend(chunk)
            require(len(data) <= SOURCE_FACT['bytes'], 'Unexpected original download size')
    require(fact(data) == SOURCE_FACT, 'Official source identity changed')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as output:
        output.write(data)
    return destination


def views(data, encoding):
    """Native generators use both raw decode and Python universal-newline reads."""
    text = data.decode(encoding)
    raw = text.encode(encoding)
    normalized = text.replace('\r\n', '\n').replace('\r', '\n').encode(encoding)
    result = [('raw', raw)]
    if normalized != raw:
        result.append(('universal_newlines', normalized))
    return result


def recover_inputs(root=ROOT):
    """Recover the two pinned public archives for independent fragment replay."""
    recover_source(root)
    destination = root / CACHE / 'PUBLIC_SOURCE.zip'
    if destination.exists():
        require(fact(destination.read_bytes()) == NATIVE_FACT, 'Cached translated archive differs')
        return
    migration = json.loads((root / MIGRATION).read_bytes())
    item = next(r for r in migration['public_artifacts'] if r['kind'] == 'source, backend, and semantic HTML release archive')
    require({k:item[k] for k in NATIVE_FACT} == NATIVE_FACT, 'Translated archive authority changed')
    require(item['url'].startswith('https://zenodo.org/records/22088947/files/'), 'Unexpected selected archive destination')
    import requests
    session = requests.Session(); session.trust_env = False; session.headers.clear()
    session.headers['User-Agent'] = 'PMI-D20-source-replay/1'
    with session.get(item['url'], stream=True, timeout=(20,60)) as response:
        response.raise_for_status()
        require('Authorization' not in response.request.headers, 'Authenticated archive request')
        data = bytearray()
        for chunk in response.iter_content(65536):
            data.extend(chunk)
            require(len(data) <= NATIVE_FACT['bytes'], 'Translated archive exceeds bound')
    require(fact(data) == NATIVE_FACT, 'Translated archive identity changed')
    with destination.open('xb') as output:
        output.write(data)


@lru_cache(maxsize=48)
def prepared_views(data, encoding):
    result = []
    for mode, candidate in views(data, encoding):
        boundary = None
        if mode == 'universal_newlines':
            boundary, cursor = [0], 0
            while cursor < len(data):
                cursor += 2 if data[cursor:cursor+2] == b'\r\n' else 1
                boundary.append(cursor)
            require(len(boundary) == len(candidate) + 1, 'Newline offset map differs')
        starts = [0] + [i + 1 for i, char in enumerate(candidate) if char == 10]
        result.append((mode, candidate, starts, boundary))
    return result


def locate_fragment(data, record, side):
    size = record.get(side + '_bytes')
    digest = record.get(side + '_sha256')
    first, last = record.get(side + '_line_start'), record.get(side + '_line_end')
    require(type(size) is int and size >= 0 and isinstance(digest, str)
            and re.fullmatch('[a-f0-9]{64}', digest), 'Invalid fragment identity')
    require(type(first) is int and type(last) is int and 1 <= first <= last, 'Invalid line interval')
    physical_matches = {}
    for mode, candidate, starts, boundary in prepared_views(data, 'ascii' if side == 'source' else 'utf-8'):
        if last > len(starts):
            continue
        low = starts[first - 1]
        high = starts[first] if first < len(starts) else len(candidate) + 1
        require(high - low <= 100000, 'Fragment candidate line exceeds bounded search')
        for start in range(low, high):
            end = start + size
            if end > len(candidate) or bisect_right(starts, max(start, end - 1)) != last:
                continue
            if hashlib.sha256(candidate[start:end]).hexdigest() == digest:
                raw_start, raw_end = (boundary[start], boundary[end]) if boundary is not None else (start, end)
                key = (raw_start, raw_end)
                if key not in physical_matches:
                    physical_matches[key] = {'view': mode, 'byte_start': start, 'byte_end': end,
                                             'raw_byte_start': raw_start, 'raw_byte_end': raw_end, 'equivalent_views': []}
                physical_matches[key]['equivalent_views'].append(mode)
    matches = list(physical_matches.values())
    return {'state': 'exact_fragment' if len(matches) == 1 else 'ambiguous_fragment' if matches else 'fragment_not_found',
            'matches': matches, 'declared_bytes': size, 'declared_sha256': digest,
            'declared_line_start': first, 'declared_line_end': last,
            'file_identity': fact(data)}


def intake(root=ROOT):
    authority_bytes = (root / AUTHORITY).read_bytes()
    migration_bytes = (root / MIGRATION).read_bytes()
    authority, migration = json.loads(authority_bytes), json.loads(migration_bytes)
    declared = {r['path']: r for r in authority['authorities']}
    require({k: declared['authority/functional_analysis_operator_algebras_web.zip'][k]
             for k in ('bytes', 'sha256')} == SOURCE_FACT, 'Central original authority changed')
    native_source = next(r for r in migration['public_artifacts']
                         if r['kind'] == 'source, backend, and semantic HTML release archive')
    require({k: native_source[k] for k in NATIVE_FACT} == NATIVE_FACT, 'Central translated authority changed')
    streams, tables, source_files, target_files = {}, {}, {}, {}
    with safe_zip((root / CACHE / 'PUBLIC_SOURCE.zip').read_bytes(), NATIVE_FACT, 100*1024*1024) as native, \
            safe_zip((root / CACHE / 'OFFICIAL_SOURCE.zip').read_bytes(), SOURCE_FACT, 2*1024*1024) as original:
        source_index = {}
        for name in original.namelist():
            if not name.endswith('/'):
                basename = PurePosixPath(name).name
                require(basename not in source_index, 'Ambiguous original basename')
                source_index[basename] = name
        for name in TABLES:
            path = 'backend/' + name + '.jsonl'
            data = native.read(PREFIX + path)
            require(fact(data) == {k: declared[path][k] for k in ('bytes', 'sha256')}, 'Native table identity drift')
            rows = [json.loads(line) for line in data.decode('utf-8-sig').splitlines() if line.strip()]
            require(len(rows) == migration['source']['native_record_counts_by_file'][name + '.jsonl'], 'Native count drift')
            require(len({r['id'] for r in rows}) == len(rows), 'Duplicate native ID in table')
            streams[name], tables[name] = data, rows
        require(len(tables['segments']) == 2196 and len(tables['terminology']) == 425, 'Wrong edition scope')
        for row in tables['segments']:
            source_path, target_path = row['source_path'], row['target_path']
            require(source_path.startswith('source/upstream/'), 'Foreign original path')
            require(target_path.startswith('source/id-ID/'), 'Foreign target path')
            source_files.setdefault(source_path, original.read(source_index[PurePosixPath(source_path).name]))
            target_files.setdefault(target_path, native.read(PREFIX + target_path))
        checks = []
        for row in tables['segments']:
            checks.append({'id': row['id'], 'unit_id': row['parent_id'],
                           'source_path': row['source_path'], 'target_path': row['target_path'],
                           'source': locate_fragment(source_files[row['source_path']], row, 'source'),
                           'target': locate_fragment(target_files[row['target_path']], row, 'target')})
        file_checks = []
        for row in tables['units']:
            for side, files in [('source', source_files), ('target', target_files)]:
                path = row.get(side + '_path')
                if not path or not row.get(side + '_sha256'):
                    continue
                key = 'source/upstream/' + path if side == 'source' and not path.startswith('source/') else path
                data = files.get(key)
                if data is None:
                    continue
                expected = {'bytes': row.get(side + '_bytes'), 'sha256': row[side + '_sha256']}
                file_checks.append({'unit_id': row['id'], 'side': side, 'path': key, 'declared': expected,
                                    'observed': fact(data), 'state': 'exact_file' if expected == fact(data) else 'file_identity_differs'})
        generator_facts = []
        for name in native.namelist():
            if name.startswith(PREFIX + 'backend/generate_') and name.endswith('.py'):
                generator_facts.append({'path': name[len(PREFIX):], **fact(native.read(name))})
        route_data = native.read(PREFIX + 'backend/html_routes.jsonl')
        require(fact(route_data) == {k: declared['backend/html_routes.jsonl'][k] for k in ('bytes', 'sha256')}, 'Native route table changed')
        route_rows = [json.loads(line) for line in route_data.decode().splitlines() if line.strip()]
        routes, parsed = {}, {}
        for unit in tables['units']:
            matches = [r for r in route_rows if r['id'] == unit['id']]
            if not matches:
                continue
            require(len(matches) == 1, 'Ambiguous chapter route')
            row = matches[0]
            path = PurePosixPath(row['output_path'])
            require(not path.is_absolute() and '..' not in path.parts and ':' not in row['href']
                    and row['href'] == row['output_path'] + '#' + unit['id'], 'Unsafe or unbound chapter route')
            if row['output_path'] not in parsed:
                content = native.read(PREFIX + 'output/html/' + row['output_path'])
                parser = IdParser()
                parser.feed(content.decode('utf-8'))
                parsed[row['output_path']] = (parser.ids, fact(content))
            ids, html_fact = parsed[row['output_path']]
            require(ids[unit['id']] == 1, 'Chapter HTML anchor is missing or ambiguous')
            routes[unit['id']] = {'native_route': row, 'html': html_fact,
                                 'url': 'https://kokunoyumeto.github.io/functional-analysis-erdman-id/output/html/' + row['href']}
    summary = {'segments': len(checks), 'terms': len(tables['terminology']), 'corrections': len(tables['corrections']),
               'source_fragment_states': dict(Counter(r['source']['state'] for r in checks)),
               'target_fragment_states': dict(Counter(r['target']['state'] for r in checks)),
               'unit_file_states': dict(Counter(r['state'] for r in file_checks))}
    audit = {'schema': 'd20-native-source-fragment-audit/1', 'course_id': 'D20', 'summary': summary,
             'segment_checks': checks, 'unit_file_checks': file_checks,
             'native_generator_files': generator_facts, 'chapter_routes': routes,
             'native_route_table': fact(route_data), 'native_code_executed': False,
             'semantic_canon_review': False, 'native_book_rebuilt': False,
             'interpretation': 'Exact hash and line-interval matches establish recorded fragment identities. Missing matches remain findings, not inferred translation corruption. No wording has been changed.'}
    lock = {'schema': 'd20-native-ledger-source-lock/1', 'course_id': 'D20',
            'source_archive': {'url': SOURCE_URL, **SOURCE_FACT}, 'translation_archive': native_source,
            'inputs': [{'path': AUTHORITY.as_posix(), **fact(authority_bytes)}, {'path': MIGRATION.as_posix(), **fact(migration_bytes)}],
            'source_tables': [{'path': 'backend/' + name + '.jsonl', 'records': len(tables[name]), **fact(data)} for name, data in streams.items()]}
    folder = root / BASE
    (folder / 'input').mkdir(parents=True, exist_ok=True)
    for name, data in streams.items():
        (folder / 'input' / (name + '.jsonl')).write_bytes(data)
    (folder / 'source-lock.json').write_bytes(encode(lock))
    (folder / 'intake-audit.json').write_bytes(encode(audit))
    seal = {'schema': 'd20-native-ledger-intake-seal/1',
            'files': {name: fact((folder/name).read_bytes()) for name in ['source-lock.json', 'intake-audit.json']}}
    (folder / 'intake-seal.json').write_bytes(encode(seal))
    return audit


def load_inputs(root=ROOT):
    folder = root / BASE
    seal = json.loads((folder/'intake-seal.json').read_bytes())
    require(seal['schema'] == 'd20-native-ledger-intake-seal/1', 'Wrong intake seal')
    require(set(seal['files']) == {'source-lock.json', 'intake-audit.json'}, 'Incomplete intake seal')
    for name, expected in seal['files'].items():
        require(fact((folder/name).read_bytes()) == expected, 'Intake witness changed')
    lock, audit = [json.loads((folder/name).read_bytes()) for name in ['source-lock.json', 'intake-audit.json']]
    require(lock['course_id'] == audit['course_id'] == 'D20', 'Foreign course')
    for item in lock['inputs']:
        require(item['path'] in {AUTHORITY.as_posix(), MIGRATION.as_posix()}, 'Foreign central authority')
        require(fact((root/item['path']).read_bytes()) == {k:item[k] for k in ('bytes','sha256')}, 'Central authority changed')
    tables, raw = {}, {}
    for item in lock['source_tables']:
        name = PurePosixPath(item['path']).stem
        require(name in TABLES and name not in tables, 'Foreign or duplicate stream')
        data = (folder/'input'/(name+'.jsonl')).read_bytes()
        require(fact(data) == {k:item[k] for k in ('bytes','sha256')}, 'Native stream changed')
        rows = [json.loads(line) for line in data.decode('utf-8-sig').splitlines() if line.strip()]
        require(len(rows) == item['records'] and len({r['id'] for r in rows}) == len(rows), 'Native stream scope changed')
        tables[name], raw[name] = rows, data
    require(set(tables) == set(TABLES), 'Missing native stream')
    return lock, audit, tables, raw


def project(root=ROOT):
    lock, audit, tables, raw = load_inputs(root)
    segments = {r['id']:r for r in tables['segments']}
    checks = {r['id']:r for r in audit['segment_checks']}
    require(len(checks) == len(audit['segment_checks']) == len(segments) == 2196 and set(checks) == set(segments), 'Fragment coverage changed')
    for identifier, row in segments.items():
        witness = checks[identifier]
        require(witness['unit_id'] == row['parent_id'], 'Wrong segment parent witness')
        for side in ['source','target']:
            require(witness[side+'_path'] == row[side+'_path'], 'Wrong witness path')
            for suffix in ['bytes','sha256','line_start','line_end']:
                require(witness[side]['declared_'+suffix] == row[side+'_'+suffix], 'Fragment witness differs from native record')
    units = {r['id']:r for r in tables['units']}
    semantic = {r['id']:r for r in tables['semantic_units']}
    require(not set(semantic) & set(units), 'Conflicting native unit IDs')
    def chapter_for(identifier):
        seen = set()
        while identifier not in units:
            require(identifier not in seen and identifier in semantic, 'Missing or cyclic native ancestry: '+identifier)
            seen.add(identifier)
            identifier = semantic[identifier]['parent_id']
        return identifier
    rows = []
    for kind in ['terminology','segments','corrections','terminology_qa','rights']:
        for row in tables[kind]:
            if kind == 'segments':
                scope = [chapter_for(row['parent_id'])]
            elif kind == 'corrections':
                scope = [chapter_for(row['unit_id'])] if row.get('unit_id') else []
            elif kind == 'terminology':
                scope = sorted(set(re.findall(r'FAOA-2015-CH\d{2}(?!\d)', str(row.get('evidence','')))) & set(units))
            else:
                scope = []
            require(all(value in units for value in scope), 'Unknown native chapter')
            rows.append({'kind':kind, 'id':row['id'], 'native':row, 'chapter_ids':scope,
                         'chapter_discovery_is_semantic_applicability':False,
                         'fragment_check':checks.get(row['id']),
                         'reader_routes':[audit['chapter_routes'][value] for value in scope if value in audit['chapter_routes']]})
    return {'schema':'d20-native-ledger-projection/1', 'course_id':'D20', 'summary':audit['summary'],
            'rows':rows, 'chapters':[{'id':u['id'], 'title_id':u.get('target_title',u['id']),
                                   'title_en':u.get('source_title',u['id'])} for u in tables['units']],
            'semantic_canon_review':False, 'native_book_rebuilt':False, 'native_records_changed':False,
            'source_archive':lock['source_archive'], 'translation_archive':lock['translation_archive'],
            'provenance':{'work':'metadata integration, fragment verification and bilingual interface',
                          'model':'OpenAI Codex — gpt-6-astra', 'effort':'Ultra'}}, raw


def page(locale):
    en = locale == 'en'
    def t(id_text, en_text):
        return html.escape(en_text if en else id_text)
    title = t('D20 · Telusuri sumber dan istilah', 'D20 · Explore sources and terminology')
    other = 'ledger.html' if en else 'ledger-en.html'
    return (f'<!doctype html><html lang="{locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; script-src \'self\'; style-src \'self\'; connect-src \'none\'; object-src \'none\'; base-uri \'none\'">'
        f'<title>{title}</title><link rel="stylesheet" href="ledger.css"><script src="data.js" defer></script><script src="ledger-ui.js" defer></script></head>'
        f'<body data-locale="{locale}"><a class="skip" href="#records">{t("Langsung ke catatan","Skip to records")}</a><main><nav>'
        f'<a href="../D20{ ".en" if en else ""}.html">{t("Belajar","Study")}</a> · '
        f'<a href="../D20-pengajar{ ".en" if en else ""}.html">{t("Mengajar","Teach")}</a> · '
        f'<a id="language" href="{other}" lang="{"id" if en else "en"}">{"Bahasa Indonesia" if en else "English"}</a></nav>'
        f'<h1>{title}</h1><p>{t("Temukan istilah, bagian sumber dan terjemahan, serta koreksi yang relevan untuk bacaan atau pengajaran Anda.","Find terminology, source/translation locations and corrections relevant to your reading or teaching.")}</p>'
        f'<p class="notice">{t("2.196 pasangan fragmen sumber–terjemahan cocok dengan hash dan lokasi yang dicatat. Ini membuktikan identitas teks, bukan ketepatan terjemahan atau persetujuan kanon. Pilihan istilah belum diperiksa ulang secara independen.","2,196 source–translation fragment pairs match their recorded hashes and locations. This establishes text identity, not translation accuracy or canon approval. Terminology choices have not been independently re-examined.")}</p>'
        f'<p>{t("Antarmuka tersedia dalam bahasa Indonesia dan Inggris. Istilah terjemahan dan tautan bab tetap berbahasa Indonesia; metadata asli dikutip tanpa perubahan.","The interface is available in Indonesian and English. Translated terminology and chapter links remain Indonesian; original metadata is quoted unchanged.")}</p>'
        f'<p>{t("Catatan ini berasal dari edisi 2026.08.25-backend-artifact-reconciliation. Tautan bacaan daring dapat menampilkan edisi yang lebih baru; identitas arsip terpilih tetap dicatat dalam unduhan bukti.","These records belong to edition 2026.08.25-backend-artifact-reconciliation. Live reading links may serve a newer edition; the selected archive identities remain in the evidence downloads.")}</p>'
        f'<p><a href="https://web.pdx.edu/~erdman/FAOA/functional_analysis_operator_algebras_pdf.pdf" hreflang="en">{t("Buku asli bahasa Inggris (PDF)","Original English book (PDF)")}</a></p>'
        f'<section class="filters"><label for="kind">{t("Jenis catatan","Record type")}</label><select id="kind">'
        f'<option value="terminology">{t("Istilah","Terminology")}</option><option value="segments">{t("Sumber dan terjemahan","Source and translation")}</option>'
        f'<option value="corrections">{t("Koreksi","Corrections")}</option><option value="terminology_qa">{t("Catatan pemeriksaan istilah asli","Original terminology QA")}</option><option value="rights">{t("Hak komponen","Component rights")}</option></select>'
        f'<label for="search">{t("Cari kata atau ID","Search text or ID")}</label><input type="search" id="search">'
        f'<label for="chapter">{t("Bab yang disebut dalam catatan","Chapter mentioned in the record")}</label><select id="chapter"><option value="">{t("Semua bab","All chapters")}</option></select></section>'
        f'<p>{t("Penyaringan bab mengikuti ID yang benar-benar dicatat; ini bukan penilaian bahwa istilah berlaku pada setiap kalimat. Catatan tanpa ID bab tetap tersedia melalui Semua bab.","Chapter filtering follows explicitly recorded IDs; it does not establish a term’s applicability to every sentence. Records without chapter IDs remain under All chapters.")}</p>'
        '<p id="count" role="status"></p><section id="records" tabindex="-1"></section>'
        f'<p class="paging"><button id="previous">{t("Sebelumnya","Previous")}</button><button id="next">{t("Berikutnya","Next")}</button></p>'
        f'<noscript><p>{t("Untuk membaca tanpa JavaScript, gunakan unduhan JSON atau arsip metadata di bawah.","To read without JavaScript, use the JSON or metadata download below.")}</p></noscript>'
        f'<h2>{t("Unduhan dan bukti","Downloads and evidence")}</h2><ul>'
        f'<li><a href="projection.json" download>{t("Data pencarian lengkap","Complete searchable data")}</a></li>'
        f'<li><a href="native-metadata.zip" download>{t("Tujuh tabel metadata asli beserta identitas sumber (ZIP; bukan buku)","Seven original metadata tables with source identities (ZIP; not the book)")}</a></li>'
        f'<li><a href="intake-audit.json">{t("Bukti perbandingan fragmen dan berkas","Fragment and file comparison evidence")}</a></li>'
        f'<li><a href="source-lock.json">{t("Edisi, identitas dan lokasi sumber","Editions, identities and source locations")}</a></li></ul>'
        f'<footer><p>{t("Integrasi metadata, pemeriksaan fragmen dan antarmuka:","Metadata integration, fragment verification and interface:")} OpenAI Codex — gpt-6-astra, Ultra. '
        f'{t("Tidak diklaim ada peninjauan manusia. Hak dan atribusi buku mengikuti edisi aslinya.","No human review is claimed. Book rights and attribution follow the original edition.")}</p></footer></main></body></html>\n').encode('utf-8')


def build(root=ROOT, destination=None):
    projection, raw = project(root)
    require(projection['summary']['source_fragment_states'] == {'exact_fragment':2196}
            and projection['summary']['target_fragment_states'] == {'exact_fragment':2196}, 'Page summary requires exact scope')
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        items = {'backend/'+name+'.jsonl':data for name,data in raw.items()}
        items['source-lock.json'] = (root/BASE/'source-lock.json').read_bytes()
        for name,data in sorted(items.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,data,compresslevel=9)
    files = {'projection.json':encode(projection),
             'data.js':('globalThis.D20_LEDGER='+json.dumps(projection,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')+';\n').encode(),
             'ledger.html':page('id'), 'ledger-en.html':page('en'), 'native-metadata.zip':memory.getvalue()}
    for name in ['source-lock.json','intake-audit.json']:
        files[name]=(root/BASE/name).read_bytes()
    for name in ['ledger-ui.js','ledger.css']:
        files[name]=(root/SITE/name).read_bytes()
    destination=destination or root/BASE/'site'
    destination.mkdir(parents=True,exist_ok=True)
    for name,data in files.items():
        (destination/name).write_bytes(data)
    return projection, {name:fact(data) for name,data in files.items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['recover-source', 'recover-inputs', 'intake', 'build'])
    args = parser.parse_args()
    if args.command == 'recover-source':
        recover_source()
        print(json.dumps({'state': 'verified', 'source': SOURCE_FACT}))
    elif args.command == 'recover-inputs':
        recover_inputs()
        print(json.dumps({'state':'verified','source':SOURCE_FACT,'translation':NATIVE_FACT}))
    elif args.command == 'intake':
        result = intake()
        print(json.dumps({'state': 'intake_complete', 'summary': result['summary']}))
    else:
        projection, outputs = build()
        for name in outputs:
            (ROOT/SITE/name).write_bytes((ROOT/BASE/'site'/name).read_bytes())
        print(json.dumps({'state':'built','summary':projection['summary'],'outputs':outputs}))
