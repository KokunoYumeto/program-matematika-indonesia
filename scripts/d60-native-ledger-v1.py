"""Reproduce a useful bilingual D60 native-record consumer from frozen metadata.

Replays this projection, not the native textbook. Raw records, IDs, historical
branches and source rights remain unchanged. No producer, network or TeX used.
"""
import argparse
import hashlib
import html
import io
import json
from pathlib import Path
from urllib.parse import quote
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('backend/course-capsule-v1/adapters/d60-native-ledger-v1')
OUT = BASE / 'site'
ASSETS = Path('docs/backend/d60/native-ledger')


def identity(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()


def heads(rows):
    superseded = {r['supersedes'] for r in rows if r.get('supersedes')}
    return [r for r in rows if r['id'] not in superseded]


def leaves(identifier, indexed):
    children = {}
    for row in indexed.values():
        if row.get('supersedes'):
            require(row['supersedes'] in indexed, 'Missing supersession parent')
            children.setdefault(row['supersedes'], []).append(row['id'])
    require(identifier in indexed, 'Unknown native unit')
    result, stack, seen = [], [identifier], set()
    while stack:
        current = stack.pop()
        require(current not in seen, 'Cyclic native supersession')
        seen.add(current)
        if children.get(current):
            stack.extend(children[current])
        else:
            result.append(current)
    return sorted(result)


def load_inputs(root):
    folder = root / BASE
    seal = json.loads((folder / 'intake-seal.json').read_bytes())
    require(seal['schema'] == 'd60-native-ledger-intake-seal/1', 'Wrong intake seal')
    for name, expected in seal['files'].items():
        require(name in {'source-lock.json', 'intake-audit.json'}, 'Foreign seal input')
        require(identity((folder / name).read_bytes()) == expected, 'Intake witness changed')
    require(set(seal['files']) == {'source-lock.json', 'intake-audit.json'}, 'Incomplete seal')
    lock = json.loads((folder / 'source-lock.json').read_bytes())
    audit = json.loads((folder / 'intake-audit.json').read_bytes())
    require(lock['course_id'] == audit['course_id'] == 'D60', 'Wrong course scope')
    for expected in lock['inputs']:
        require(identity((root / expected['path']).read_bytes()) == {k: expected[k] for k in ('bytes', 'sha256')}, 'Central authority changed')
    shards, raw = {}, {}
    for expected in lock['source_tables']:
        name = Path(expected['path']).stem
        require(name not in shards, 'Duplicate native stream')
        data = (folder / 'input' / (name + '.jsonl')).read_bytes()
        require(identity(data) == {k: expected[k] for k in ('bytes', 'sha256')}, 'Native shard changed')
        rows = [json.loads(line) for line in data.decode().splitlines() if line]
        require(len(rows) == expected['records'] and len({r['id'] for r in rows}) == len(rows), 'Native ID/count drift')
        shards[name], raw[name] = rows, data
    require(len(shards) == 11 and sum(map(len, shards.values())) == 8338, 'Native stream scope differs')
    require({name: len(heads(rows)) for name, rows in shards.items()} == audit['current_counts'], 'Current-head scope differs')
    return lock, audit, shards, raw


def project(root):
    lock, audit, shards, raw = load_inputs(root)
    units = {r['id']: r for r in shards['units']}
    witness = json.loads((root / audit['route_witness']['path']).read_bytes())
    routes = {r['id']: r for r in witness['unit_routes']}
    require(set(routes) == {r['id'] for r in heads(shards['units'])}, 'Reader witness/current unit scope differs')
    checked = {r['id']: r for r in audit['target_file_checks']}
    require(set(checked) == {r['id'] for r in heads(shards['segments'])}, 'Target witness/segment scope differs')
    reader = witness['reader']['url']
    require(reader.startswith('https://kokunoyumeto.github.io/algebraic-topology-id/'), 'Foreign reader destination')
    unit_routes = {}
    unit_contexts = {}
    local_ids = {}
    for record in units.values():
        if record.get('source_local_id'):
            local_ids.setdefault(record['source_local_id'], []).append(record['id'])
    for identity_id, fact in routes.items():
        exact = fact['occurrences'] == 1
        unit_routes[identity_id] = {'id': identity_id, 'title': units[identity_id]['display_title'],
                                    'url': reader + ('#' + quote(fact['anchor'], safe='') if exact else ''),
                                    'state': 'exact_anchor' if exact else 'course_fallback'}
        path = units[identity_id]['path']
        require(isinstance(path, list) and path, 'Missing original native path')
        resolution = []
        for value in path:
            candidates = [value] if value in units else local_ids.get(value, [])
            resolved = sorted({leaf for candidate in candidates for leaf in leaves(candidate, units)})
            require(len(resolved) == 1, 'Unknown or ambiguous original path identity: ' + value)
            resolution.append({'native_path_value': value, 'matched_native_ids': sorted(candidates), 'current_native_id': resolved[0],
                               'evidence': 'exact_native_id' if value in units else 'exact_recorded_source_local_id'})
        require(resolution[-1]['current_native_id'] == identity_id, 'Native path endpoint does not resolve to its unit')
        unit_contexts[identity_id] = {'native_path': path, 'path_identity_resolution': resolution,
                                      'discovery_scope_ids': sorted({identity_id, *path, *(item['current_native_id'] for item in resolution)}),
                                      'rights_component_ids': [units[identity_id]['rights_component_id']],
                                      'semantic_applicability_asserted': False}
    rows = []
    for kind in ['terms', 'segments', 'corrections', 'rights']:
        for record in sorted(heads(shards[kind]), key=lambda r: r['id']):
            raw_units = []
            for field in ['unit_id', 'scope_unit_id']:
                if record.get(field):
                    raw_units.append(record[field])
            raw_units += record.get('affected_unit_ids', [])
            raw_units += [value for value in record.get('component_scope', []) if value in units]
            current_units = sorted({leaf for value in raw_units for leaf in leaves(value, units)})
            require(all(value in unit_routes for value in current_units), 'Unroutable current unit')
            flags = []
            if kind == 'terms':
                flags.append('canon_not_independently_checked')
                if not record.get('schema') or not record.get('schema_version'):
                    flags.append('native_envelope_missing')
                if not record.get('terminology_status'):
                    flags.append('native_terminology_status_missing')
            target = checked.get(record['id'])
            if kind == 'segments':
                require(target['path'] == record['target_locator']['path'] and target['declared_file_sha256'] == record['target_locator'].get('file_sha256'), 'Target witness/native locator differs')
                if target['state'] != 'exact_file_identity':
                    flags.append('target_file_identity_differs')
            branch_parents = {r['parent_id'] for r in audit['supersession_branches'].get(kind, [])}
            if record.get('supersedes') in branch_parents:
                flags.append('supersession_branch_preserved')
            rows.append({'kind': kind, 'id': record['id'], 'native': record,
                         'native_scope_ids': sorted(set(raw_units)), 'current_unit_ids': current_units,
                         'routes': [unit_routes[value] for value in current_units],
                         'target_identity': target, 'flags': flags})
    summary = {'all_native_records': 8338, 'current_native_heads': audit['current_native_heads'],
               'unit_paths_with_recorded_local_ids': sum(any(item['evidence'] == 'exact_recorded_source_local_id' for item in context['path_identity_resolution']) for context in unit_contexts.values()),
               'existing_materialized_subset': audit['existing_adapter_materialized_record_count'],
               'visible_current_records': len(rows), 'counts': {kind: sum(r['kind'] == kind for r in rows) for kind in ['terms', 'segments', 'corrections', 'rights']},
               'target_file_checks': audit['target_check_counts'], 'reference_gaps': len(audit['reference_gaps'])}
    return {'schema': 'd60-native-ledger-projection/1', 'course_id': 'D60', 'summary': summary,
            'source_archive': lock['source_archive'], 'reader': witness['reader'], 'rows': rows, 'unit_contexts': unit_contexts,
            'native_records_changed': False, 'bodies_copied': False, 'semantic_canon_approval': False,
            'native_book_rebuilt': False, 'independent_canon_review': 'not_checked',
            'intake_seal': identity((root / BASE / 'intake-seal.json').read_bytes()),
            'provenance': {'work': 'Native-metadata intake, projection, interface and QA', 'model': 'OpenAI Codex — gpt-6.1-sol', 'effort': 'Ultra'}}, raw


def metadata_zip(root, raw):
    notice = ('Metadata asli D60: sebelas aliran JSONL yang tidak diubah.\n'
              'Hak, atribusi dan batas komponen tetap mengikuti rights.jsonl.\n'
              'Ini bukan arsip buku atau klaim pengesahan kanon/produksi ulang buku.\n'
              'Native D60 metadata: unchanged original JSONL streams; component rights remain distinct.\n')
    items = {'NOTICE.txt': notice.encode(), 'source-lock.json': (root / BASE / 'source-lock.json').read_bytes()}
    items.update({'backend/' + name + '.jsonl': data for name, data in raw.items()})
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(items.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    return memory.getvalue()


def page(locale, summary):
    en = locale == 'en'
    def t(indonesian, english):
        return english if en else indonesian
    title = t('D60 · Sumber, istilah dan koreksi asli', 'D60 · Native sources, terminology and corrections')
    return ('<!doctype html><html lang="' + locale + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>' + title + '</title><link rel="stylesheet" href="ledger.css"><script src="data.js" defer></script><script src="ledger-ui.js" defer></script></head>'
            '<body data-interface="' + locale + '"><a class="skip" href="#records">' + t('Langsung ke catatan', 'Skip to records') + '</a><main>'
            '<nav aria-label="' + t('Navigasi D60', 'D60 navigation') + '"><a href="../D60' + ('.en' if en else '') + '.html">' + t('Belajar', 'Study') + '</a> · '
            '<a href="../D60-pengajar' + ('.en' if en else '') + '.html">' + t('Mengajar', 'Teach') + '</a> · '
            '<a href="../../index' + ('-en' if en else '') + '.html">' + t('Program', 'Program') + '</a> · '
            '<a id="language" href="ledger' + ('' if en else '-en') + '.html" lang="' + ('id' if en else 'en') + '">' + ('Bahasa Indonesia' if en else 'English') + '</a></nav>'
            '<h1>' + title + '</h1><p>' + t('Periksa istilah, lokasi sumber/terjemahan dan koreksi untuk unit yang sedang dipelajari atau diajarkan.', 'Inspect terminology, source/target locations and corrections for the unit you are studying or teaching.') + '</p>'
            '<p class="notice">' + t('Catatan asli dikutip tanpa perubahan; sebagian metadata aslinya berbahasa Inggris. Status asli “admitted” atau “built” bukan pengesahan baru. Belum ada pemeriksaan kanon independen atau produksi ulang seluruh buku.', 'Original records are quoted unchanged; native metadata mixes Indonesian and English. Native “admitted” or “built” states are not new certification. Independent canon review and full native-book replay are not established.') + '</p>'
            '<p>' + t('8.338 rekaman asli · 7.996 kepala versi asli · 6.279 rekaman dalam subset adapter lama. Angka ini memiliki cakupan berbeda.', '8,338 original records · 7,996 native current heads · 6,279 records in the existing materialized adapter subset. These counts have different scopes.') + '</p>'
            '<p class="notice">' + t('2.101 identitas berkas target cocok; 73 berbeda pada satu berkas Kuliah 20. Perbedaan hash seluruh berkas tidak membuktikan paragrafnya rusak. Riwayat dan semua cabang tetap tersedia; tidak diperbaiki diam-diam.', '2,101 target-file identities match; 73 differ in one Lecture 20 file. A whole-file hash difference does not prove paragraph damage. History and every branch remain available; nothing is silently repaired.') + '</p>'
            '<section class="filters" aria-label="' + t('Saring catatan', 'Filter records') + '"><label for="kind">' + t('Jenis catatan', 'Record type') + '</label><select id="kind">'
            '<option value="terms">' + t('Istilah', 'Terms') + ' (528)</option><option value="segments">' + t('Sumber dan terjemahan', 'Source and translation') + ' (2174)</option>'
            '<option value="corrections">' + t('Koreksi', 'Corrections') + ' (564)</option><option value="rights">' + t('Hak komponen', 'Component rights') + ' (96)</option></select>'
            '<label for="search">' + t('Cari kata atau ID', 'Search text or ID') + '</label><input id="search" type="search">'
            '<label for="unit">' + t('ID unit asli (opsional)', 'Exact native unit ID (optional)') + '</label><input id="unit" type="search" autocomplete="off">'
            '<label for="flag">' + t('Temuan', 'Finding') + '</label><select id="flag"><option value="">' + t('Semua', 'All') + '</option>'
            '<option value="target_file_identity_differs">' + t('Hash berkas target berbeda', 'Target-file hash differs') + '</option><option value="native_terminology_status_missing">' + t('Status istilah asli tidak ada', 'Native terminology status missing') + '</option>'
            '<option value="supersession_branch_preserved">' + t('Cabang riwayat dipertahankan', 'History branch preserved') + '</option></select></section>'
            '<p id="count" aria-live="polite"></p><section id="records" aria-label="' + t('Catatan asli', 'Native records') + '" tabindex="-1"></section>'
            '<p class="paging"><button id="previous" type="button">' + t('Sebelumnya', 'Previous') + '</button><button id="next" type="button">' + t('Berikutnya', 'Next') + '</button></p>'
            '<noscript><p>' + t('Unduh JSON atau ZIP di bawah untuk mengakses semua catatan tanpa JavaScript.', 'Download JSON or ZIP below to access all records without JavaScript.') + '</p></noscript>'
            '<h2>' + t('Unduhan dan bukti', 'Downloads and evidence') + '</h2><ul><li><a href="projection.json" download>' + t('Data pencarian lengkap (JSON)', 'Complete searchable projection (JSON)') + '</a></li>'
            '<li><a href="native-metadata.zip" download>' + t('Semua sebelas aliran metadata asli, termasuk riwayat (ZIP)', 'All eleven original metadata streams, including history (ZIP)') + '</a></li>'
            '<li><a href="intake-audit.json">' + t('Bukti pemeriksaan dan batasnya', 'Audit evidence and its limits') + '</a></li><li><a href="source-lock.json">' + t('Identitas sumber dan lisensinya', 'Source identities and rights') + '</a></li></ul>'
            '<footer><p>' + t('Antarmuka, integrasi metadata dan pemeriksaan: ', 'Interface, metadata integration and QA: ') + 'OpenAI Codex — gpt-6.1-sol, Ultra. '
            + t('Tidak diklaim ada penyuntingan manusia. Hak tiap catatan mengikuti edisi asli; antarmuka tidak mengubah lisensinya.', 'No human editing is claimed. Each record retains its native-edition rights; the interface does not relicense it.') + '</p></footer></main></body></html>\n').encode()


def build(root=ROOT, destination=None):
    projection, raw = project(root)
    destination = destination or root / OUT
    files = {'projection.json': json_bytes(projection),
             'data.js': ('globalThis.D60_NATIVE_LEDGER=' + json.dumps(projection, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029') + ';\n').encode(),
             'native-metadata.zip': metadata_zip(root, raw),
             'ledger.html': page('id', projection['summary']), 'ledger-en.html': page('en', projection['summary']),
             'source-lock.json': (root / BASE / 'source-lock.json').read_bytes(),
             'intake-audit.json': (root / BASE / 'intake-audit.json').read_bytes()}
    for name in ['ledger-ui.js', 'ledger.css']:
        files[name] = (root / ASSETS / name).read_bytes()
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (destination / name).write_bytes(data)
    return projection, {name: identity(data) for name, data in files.items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    projection, output = build(destination=args.out)
    if args.out is None:
        (ROOT / ASSETS).mkdir(parents=True, exist_ok=True)
        for name in output:
            (ROOT / ASSETS / name).write_bytes((ROOT / OUT / name).read_bytes())
    print(json.dumps({'state': 'pass', 'summary': projection['summary'], 'outputs': output}), flush=True)
