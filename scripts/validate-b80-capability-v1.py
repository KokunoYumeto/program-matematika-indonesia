"""Independent semantic/HTML checks and isolated, deterministic adapter replay."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

from jsonschema import Draft202012Validator, FormatChecker

PROJECT = Path(__file__).resolve().parents[1]
BASE = Path('backend/course-capsule-v1/adapters/b80-capability-v1')


def load(path):
    return json.loads((PROJECT / path).read_bytes())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check(condition, message):
    if not condition:
        raise AssertionError(message)


class Page(HTMLParser):
    def __init__(self, data):
        super().__init__(convert_charrefs=True)
        self.ids = Counter()
        self.hrefs = []
        self.lang = None
        self.feed(data)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids[attrs['id']] += 1
        if tag == 'html':
            self.lang = attrs.get('lang')
        if tag == 'a':
            self.hrefs.append(attrs.get('href', ''))


catalog = load(BASE / 'input/catalog.json')
schema = load(BASE / 'input/catalog.schema.json')
Draft202012Validator.check_schema(schema)
Draft202012Validator(schema).validate(catalog)
manifest = load(BASE / 'manifest.json')
intake = load(BASE / 'input/public-intake.json')
for row in manifest['inputs'] + manifest['outputs']:
    data = (PROJECT / row['path']).read_bytes()
    check(len(data) == row['bytes'] and digest(data) == row['sha256'], 'File drift: ' + row['path'])

records = [json.loads(line) for line in (PROJECT / BASE / 'exchange/records.jsonl').read_text('utf-8').splitlines()]
record_schema = load('schemas/course-capsule-v1/native-catalog-record-v1.schema.json')
for row in records:
    Draft202012Validator(record_schema).validate(row)
shape = load(BASE / 'exchange/shape.json')
reconstructed = {}
for table in shape:
    rows = sorted((row for row in records if row['table'] == table['table']), key=lambda row: row['ordinal'])
    check([row['ordinal'] for row in rows] == list(range(table['count'])), 'Lost/duplicate ordinals')
    for row in rows:
        value = row['payload']
        check(row['native_id'] == (value.get('id') if isinstance(value, dict) else None), 'Native ID changed')
    reconstructed[table['table']] = [row['payload'] for row in rows] if table['kind'] == 'array' else rows[0]['payload']
check(reconstructed == catalog, 'Native JSON values not preserved')
check(load(BASE / 'exchange/reconstructed-catalog.json') == catalog, 'Reconstruction differs')

resource = load('docs/backend/b80/learning-map.json')
capability_schema = load('schemas/course-capsule-v1/course-learning-capability-v1.schema.json')
Draft202012Validator(capability_schema, format_checker=FormatChecker()).validate(resource)
check(resource['sources'] == catalog['sources'], 'Source provenance or rights changed')
check(resource['labs'] == catalog['labs'] and resource['environments'] == catalog['environments'], 'Lab/environment binding changed')
check(resource['artifacts'] == catalog['artifacts'], 'Artifact or accessibility binding changed')
native_exercises = {row['id']: row for row in catalog['exercises']}
mapped = [row for unit in resource['units'] for row in unit['exercises']]
check(len(mapped) == len(native_exercises) == 75, 'Exercise coverage')
page_by_url = {row['url']: row for row in intake['pages']}
for row in mapped:
    native = native_exercises[row['id']]
    check(row['curriculum_status'] == native['curriculum_status'], 'Core/extension status changed')
    for kind in ('hint', 'check', 'solution'):
        check({key: value for key, value in row[kind].items() if key != 'href'} == native[kind], 'Support state changed')
        available = row[kind]['status'] in ('complete', 'executable')
        check(bool(row[kind]['href']) == available, 'Missing support misrepresented')
check(Counter(row['curriculum_status'] for row in mapped) == {'complete': 72, 'prerequisite_deferred': 3}, 'Core boundary changed')
check(sum(route['required_for_b80'] for route in resource['prerequisite_routes']) == 1, 'Optional routes became required')

learner = Page((PROJECT / 'docs/backend/b80/B80.html').read_text('utf-8'))
teacher = Page((PROJECT / 'docs/backend/b80/B80-pengajar.html').read_text('utf-8'))
check(learner.lang == teacher.lang == 'id', 'Wrong language declaration')
for page in (learner, teacher):
    check(max(page.ids.values()) == 1, 'Duplicate local HTML id')
    for href in page.hrefs:
        parsed = urlparse(href)
        if parsed.scheme:
            check(parsed.scheme == 'https', 'Unsafe link scheme')
            no_fragment = href.split('#')[0]
            if no_fragment in page_by_url and parsed.fragment:
                check(page_by_url[no_fragment]['anchor_counts'].get(unquote(parsed.fragment)) == 1, 'Public anchor missing')
        elif href.startswith('B80.html#'):
            check(learner.ids[unquote(href.split('#')[1])] == 1, 'Teacher/learner identity mismatch')
        elif href.startswith('../../id/#'):
            target = Page((PROJECT / 'docs/id/index.html').read_text('utf-8'))
            check(target.ids[unquote(href.split('#')[1])] == 1, 'Central prerequisite route missing')
for exercise in mapped:
    check(learner.ids[exercise['id']] == 1, 'Exercise absent from learner page')
    check('B80.html#' + exercise['id'] in teacher.hrefs, 'Exercise absent from teacher page')
for unit in resource['units']:
    check(unit['href'] in learner.hrefs and unit['href'] in teacher.hrefs, 'Unit absent from shared views')

# No private producer roots are copied or consulted by these two clean builds.
with tempfile.TemporaryDirectory(prefix='b80-isolated-replay-') as name:
    root = Path(name).resolve()
    check(root.parent == Path(tempfile.gettempdir()).resolve(), 'Unexpected temporary root')
    for relative in ['scripts/build-b80-capability-v1.mjs', 'scripts/native-catalog-exchange-v1.mjs'] + [row['path'] for row in manifest['inputs']]:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT / relative, destination)
    fingerprints = []
    for run in (1, 2):
        result = subprocess.run(['node', str(root / 'scripts/build-b80-capability-v1.mjs'), '--output-root=' + str(root / f'run{run}')],
                                cwd=root, capture_output=True, text=True, timeout=60)
        check(result.returncode == 0, result.stderr)
        hashes = {}
        for row in manifest['outputs'] + [{'path': str(BASE / 'manifest.json')}]:
            data = (root / f'run{run}' / row['path']).read_bytes()
            check(data == (PROJECT / row['path']).read_bytes(), 'Isolated replay changed output: ' + row['path'])
            hashes[row['path']] = digest(data)
        fingerprints.append(hashes)
    check(fingerprints[0] == fingerprints[1], 'Two builds differ')

ui = subprocess.run(['node', str(PROJECT / 'scripts/test-b80-capability-v1.mjs')], capture_output=True, text=True, timeout=60)
check(ui.returncode == 0, ui.stderr)
receipt = {'schema': 'b80-capability-validation/1', 'state': 'pass',
           'native_catalog_sha256': intake['catalog']['sha256'],
           'manifest_sha256': digest((PROJECT / BASE / 'manifest.json').read_bytes()),
           'native_schema_validation': True, 'json_value_roundtrip': True,
           'isolated_two_build_byte_identity': True, 'private_native_roots_required': False,
           'units': 14, 'exercises': 75, 'core_exercises': 72, 'prerequisite_deferred_exercises': 3,
           'laboratories': 4, 'native_records': len(records), 'reader_pages': len(intake['pages']),
           'learner_teacher_shared_identity': True, 'ui_tests': json.loads(ui.stdout),
           'scientific_experiments_rerun': False, 'public_adapter_release_verified': False}
data = (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode()
for relative in [BASE / 'validation.json', Path('docs/backend/b80/validation.json')]:
    (PROJECT / relative).write_bytes(data)
print(json.dumps(receipt, indent=2))
