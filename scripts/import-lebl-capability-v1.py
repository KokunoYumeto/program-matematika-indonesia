"""Freeze public, zero-prose Lebl metadata and PDF navigation for shared adapters.

The native record stream and books remain external. This does not admit an
adapter or claim complete native production replay, visual QA, or full exchange.
"""
import argparse
import collections
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
COMMIT = 'a83fc15fed51e339379767a53970878579877287'
REPO = 'https://raw.githubusercontent.com/KokunoYumeto/lebl-mathematics-family-id/' + COMMIT + '/'
EXPORT = 'backend/production/v0.4-complete-2026.08.31-tqa-release-a/'
RELEASE = 'https://github.com/KokunoYumeto/lebl-mathematics-family-id/releases/download/lebl-family-id.2026.08.31.terminology/'
BOOKS = [
    ('R006-volume-1', 'Analisis_Dasar_I_Bahasa_Indonesia_v6.3.pdf', 2870909, '38743ea0e7ce52bdadf5233fc9d6e79e00717f9ba55a393f2bf46ea21c65ef56', 334),
    ('R006-volume-2', 'Analisis_Dasar_II_Bahasa_Indonesia_v6.3.pdf', 2427379, 'e70c74bb7edc466a7cb6ff0eff0de33dfcc7b3bc63010d018aff758a14d2dea3', 241),
    ('R007', 'Catatan_tentang_Diffy_Qs_Bahasa_Indonesia_v6.11.pdf', 5135112, '5395c01c7e1b3d170dfc5d2ecb4e55fcc7cc08890ef8706a385d6ae292a72d62', 502),
    ('R008', 'Panduan_Mengolah_Analisis_Kompleks_Bahasa_Indonesia_v1.9.pdf', 2822050, 'efe8146e7a16fc4386b4e21cfb3454e5b1684ed6dd2f19c20a83f5b6023e6106', 338),
]
arguments = argparse.ArgumentParser()
arguments.add_argument('--native-root', required=True)
options = arguments.parse_args()
native = Path(options.native_root).resolve()
target = ROOT / 'backend/course-capsule-v1/adapters/lebl-capability-v1/input'
assert not target.exists(), 'Intake already exists; reuse frozen inputs instead of silently refreshing.'
session = requests.Session()
session.trust_env = False
session.headers['User-Agent'] = 'lebl-native-metadata-intake'
facts = []
digest = lambda data: hashlib.sha256(data).hexdigest()


def download(url, expected_bytes, expected_sha256):
    data = bytearray()
    with session.get(url, timeout=(15, 60), stream=True) as response:
        response.raise_for_status()
        assert 'Authorization' not in response.request.headers
        for chunk in response.iter_content(65536):
            data.extend(chunk)
            assert len(data) <= expected_bytes, 'Unexpected larger response: ' + url
    data = bytes(data)
    assert len(data) == expected_bytes and digest(data) == expected_sha256, 'Public byte mismatch: ' + url
    facts.append({'url': url, 'bytes': len(data), 'sha256': digest(data), 'http_status': 200})
    return data


def matched_native(path):
    local = (native / path).read_bytes()
    return download(REPO + path, len(local), digest(local))


dataset_bytes = matched_native(EXPORT + 'dataset.json')
dataset = json.loads(dataset_bytes)
stream = dataset['record_streams'][0]
assert stream['path'] == 'records.jsonl'
native_bytes = matched_native(EXPORT + stream['path'])
assert len(native_bytes) == stream['bytes'] and 'sha256:' + digest(native_bytes) == stream['sha256']
raw_lines = native_bytes.splitlines()
records = [json.loads(line) for line in raw_lines]
assert len(records) == stream['record_count']
by_id = {row['id']: row for row in records}
assert len(by_id) == len(records), 'Duplicate native record IDs'
expression_ids = [expression['expression_id'] for row in records for expression in row.get('expressions', [])]
assert len(expression_ids) == len(set(expression_ids)), 'Duplicate embedded expression IDs'
assert not set(expression_ids).intersection(by_id), 'Expression/record ID collision'
all_ids = set(by_id).union(expression_ids)
counts = collections.Counter(row['record_type'] for row in records)
expression_count = 0
for row in records:
    assert re.fullmatch(r'urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', row['id'])
    for key in ('resource_id', 'edition_id', 'rights_id', 'parent_id', 'unit_id', 'concept_id', 'subject_id', 'object_id'):
        if row.get(key):
            assert row[key] in all_ids, f"{row['id']}: unresolved {key}"
    for expression in row.get('expressions', []):
        assert 'sha256:' + digest(expression['content'].encode('utf-8')) == expression['content_sha256'], expression['expression_id']
        expression_count += 1

keep_unit = ['id', 'semantic_key', 'semantic_aliases', 'resource_id', 'edition_id', 'parent_id',
             'source_local_id', 'order_key', 'unit_kind', 'label', 'title', 'prerequisite_ids',
             'concept_ids', 'rights_id', 'locale_states', 'exercise_metadata', 'source_binding', 'status', 'supersedes_id']
keep_binding = ['resource_key', 'edition_key', 'rights_key', 'source_components', 'target_components',
                'state', 'title_target', 'locale', 'input_schema']
units = []
for row in records:
    if row['record_type'] != 'unit':
        continue
    unit = {key: row[key] for key in keep_unit if key in row}
    if 'manifest_binding' in row:
        unit['manifest_binding'] = {key: row['manifest_binding'][key] for key in keep_binding if key in row['manifest_binding']}
    units.append(unit)

reader_routes = []
for book, filename, size, sha256, pages in BOOKS:
    pdf = download(RELEASE + filename, size, sha256)
    reader = PdfReader(io.BytesIO(pdf))
    assert len(reader.pages) == pages, filename + ': page count differs'
    outline = []

    def walk(items, level=0):
        for item in items:
            if isinstance(item, list):
                walk(item, level + 1)
            else:
                number = reader.get_destination_page_number(item)
                assert number is not None and 0 <= number < pages
                outline.append({'title': str(item.title), 'level': level, 'page': number + 1,
                                'href': RELEASE + filename + '#page=' + str(number + 1)})

    walk(reader.outline)
    reader_routes.append({'book_id': book, 'filename': filename, 'url': RELEASE + filename,
                          'bytes': size, 'sha256': sha256, 'pages': pages, 'outline': outline,
                          'visual_layout_reviewed': False, 'navigation_scope': 'verified_pdf_outline_page_destinations'})

entrypoints = {}
for filename in ['realanal.tex', 'realanal2.tex']:
    path = 'translation/ra/' + filename
    content = matched_native(path).decode('utf-8')
    entrypoints[filename] = {'path': path, 'source_sha256': digest(content.encode('utf-8')),
                            'inputs': re.findall(r'^\\input\{([^}]+)\}', content, re.MULTILINE)}

projection = {
    'dataset.json': dataset,
    'resources.json': [row for row in records if row['record_type'] == 'resource'],
    'editions.json': [row for row in records if row['record_type'] == 'edition'],
    'rights.json': [row for row in records if row['record_type'] == 'rights'],
    'terms.json': [row for row in records if row['record_type'] == 'term'],
    'relations.json': [row for row in records if row['record_type'] == 'relation'],
    'units.json': units,
    'reader-destinations.json': reader_routes,
    'volume-entrypoints.json': entrypoints,
}
solution_statuses = collections.Counter(row.get('exercise_metadata', {}).get('solution_status', 'not_declared')
                                      for row in units if row.get('unit_kind') == 'exercise')
summary = {'schema': 'lebl-native-capability-intake/1', 'state': 'pass', 'native_commit': COMMIT,
           'dataset_id': dataset['dataset_id'], 'native_record_count': len(records), 'record_types': dict(counts),
           'native_unit_count': len(units), 'manifest_bound_units': sum('manifest_binding' in row for row in units),
           'unit_kinds': dict(collections.Counter(row['unit_kind'] for row in units)),
           'exercise_support_states': dict(solution_statuses), 'expression_hashes_checked': expression_count,
           'reader_pages': sum(row['pages'] for row in reader_routes),
           'reader_outline_destinations': sum(len(row['outline']) for row in reader_routes),
           'native_schema_replay': 'not_performed_here', 'source_span_replay': 'not_performed_here',
           'native_production_replay': 'not_performed_here', 'native_content_copied': False,
           'common_adapter_admitted': False, 'roles': ['B70', 'C10', 'C20', 'C50'],
           'projection_policy': {
               'native_record_stream': 'External pinned source; all raw record identities and line hashes are indexed, not copied.',
               'resources_editions_rights_terms_relations': 'Whole native metadata records retained unchanged.',
               'units': {'retained_fields': keep_unit, 'manifest_binding_fields': keep_binding,
                         'omitted_fields': 'Recover from pinned native stream; no full-native roundtrip claim.'},
               'segments_assets_concepts_corrections_artifacts_qa': 'Raw-line hashes retained, payloads remain external.',
               'readers': 'External PDF bytes checked; outline/page coordinates retained, PDF bodies not copied.',
           }}
projection['native-summary.json'] = summary
projection['public-readback.json'] = {'schema': 'lebl-native-public-readback/1', 'state': 'pass',
    'recorded_at': datetime.now(timezone.utc).isoformat(), 'native_commit': COMMIT, 'files': facts,
    'anonymous': True, 'ambient_credentials_disabled': True}
index_lines = [json.dumps({'id': row['id'], 'type': row['record_type'], 'semantic_key': row['semantic_key'],
                          'line': number, 'bytes_without_newline': len(raw), 'sha256': digest(raw)},
                         ensure_ascii=False, sort_keys=True, separators=(',', ':'))
               for number, (row, raw) in enumerate(zip(records, raw_lines), 1)]
target.mkdir(parents=True)
for filename, value in projection.items():
    (target / filename).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n',
                                 encoding='utf-8', newline='\n')
(target / 'native-record-index.jsonl').write_text('\n'.join(index_lines) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(summary))
