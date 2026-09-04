"""Create once, then verify offline, the frozen intake's pinned-stream binding.

Does not regenerate intake, copy book prose, replay TeX, or certify PDF layout.
"""
import argparse
import collections
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/lebl-capability-v1'
COMMIT = 'a83fc15fed51e339379767a53970878579877287'
URL = 'https://raw.githubusercontent.com/KokunoYumeto/lebl-mathematics-family-id/' + COMMIT + '/backend/production/v0.4-complete-2026.08.31-tqa-release-a/'
DATASET_HASH = '149a6457786e54051afff370d93d534e4b954879ca37bf7481eec2b0ba94ce88'
STREAM_HASH = '60ea5afad065a29d5d2ffca8bc0ac0fec3998bb1c0e9fff9ac6302769171e7b9'
NAMES = ['dataset.json', 'resources.json', 'editions.json', 'rights.json', 'terms.json',
         'relations.json', 'units.json', 'native-record-index.jsonl', 'native-summary.json',
         'reader-destinations.json', 'volume-entrypoints.json', 'public-readback.json']
UNIT = ['id', 'semantic_key', 'semantic_aliases', 'resource_id', 'edition_id', 'parent_id',
        'source_local_id', 'order_key', 'unit_kind', 'label', 'title', 'prerequisite_ids',
        'concept_ids', 'rights_id', 'locale_states', 'exercise_metadata', 'source_binding', 'status', 'supersedes_id']
BINDING = ['resource_key', 'edition_key', 'rights_key', 'source_components', 'target_components',
           'state', 'title_target', 'locale', 'input_schema']
sha = lambda data: hashlib.sha256(data).hexdigest()
pretty = lambda value: (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
compact = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
load = lambda path: json.loads(path.read_bytes())


def verify(base=BASE):
    receipt = load(base / 'native-evidence-binding.json')
    assert receipt['state'] == 'pass' and receipt['native_commit'] == COMMIT
    assert receipt['source_stream'] == {'url': URL + 'records.jsonl', 'bytes': 36414746, 'sha256': STREAM_HASH, 'records': 20401}
    assert receipt['source_dataset'] == {'url': URL + 'dataset.json', 'bytes': 1913, 'sha256': DATASET_HASH}
    assert receipt['reconstructed_stream_projections'] == NAMES[:8]
    assert [fact['name'] for fact in receipt['inputs']] == NAMES
    for fact in receipt['inputs']:
        data = (base / 'input' / fact['name']).read_bytes()
        assert len(data) == fact['bytes'] and sha(data) == fact['sha256'], 'Frozen input changed: ' + fact['name']
    dataset = load(base / 'input/dataset.json')
    assert sha((base / 'input/dataset.json').read_bytes()) == DATASET_HASH
    stream = dataset['record_streams'][0]
    assert stream == {'path': 'records.jsonl', 'bytes': 36414746, 'sha256': 'sha256:' + STREAM_HASH, 'record_count': 20401}
    summary = load(base / 'input/native-summary.json')
    assert summary['dataset_id'] == dataset['dataset_id']
    assert summary['native_commit'] == COMMIT and summary['native_record_count'] == stream['record_count']
    index = [json.loads(row) for row in (base / 'input/native-record-index.jsonl').read_bytes().splitlines()]
    assert len(index) == len({row['id'] for row in index}) == stream['record_count']
    assert [row['line'] for row in index] == list(range(1, len(index) + 1))
    assert sum(row['bytes_without_newline'] + 1 for row in index) == stream['bytes']
    assert dict(collections.Counter(row['type'] for row in index)) == summary['record_types']
    return receipt


def bind():
    import requests
    target = BASE / 'native-evidence-binding.json'
    assert not target.exists(), 'Binding exists; verify it, do not overwrite.'
    session = requests.Session()
    session.trust_env = False
    session.headers['User-Agent'] = 'lebl-projection-source-binding'
    def fetch(name, size, expected):
        data = bytearray()
        with session.get(URL + name, stream=True, timeout=(15, 60)) as response:
            response.raise_for_status()
            assert 'Authorization' not in response.request.headers
            for chunk in response.iter_content(65536):
                data.extend(chunk)
                assert len(data) <= size
        assert len(data) == size and sha(data) == expected
        return bytes(data)
    dataset_bytes = fetch('dataset.json', 1913, DATASET_HASH)
    raw = fetch('records.jsonl', 36414746, STREAM_HASH)
    lines = raw.splitlines()
    assert b'\n'.join(lines) + b'\n' == raw, 'Unexpected line-ending contract'
    records = [json.loads(line) for line in lines]
    assert len(records) == len({r['id'] for r in records}) == 20401
    def match(name, data):
        assert (BASE / 'input' / name).read_bytes() == data, 'Source reconstruction mismatch: ' + name
    match('dataset.json', pretty(json.loads(dataset_bytes)))
    for name, kind in [('resources', 'resource'), ('editions', 'edition'), ('rights', 'rights'), ('terms', 'term'), ('relations', 'relation')]:
        match(name + '.json', pretty([r for r in records if r['record_type'] == kind]))
    units = []
    for row in records:
        if row['record_type'] != 'unit':
            continue
        unit = {key: row[key] for key in UNIT if key in row}
        if 'manifest_binding' in row:
            unit['manifest_binding'] = {key: row['manifest_binding'][key] for key in BINDING if key in row['manifest_binding']}
        units.append(unit)
    match('units.json', pretty(units))
    index = [{'id': row['id'], 'type': row['record_type'], 'semantic_key': row['semantic_key'],
              'line': n, 'bytes_without_newline': len(line), 'sha256': sha(line)}
             for n, (row, line) in enumerate(zip(records, lines), 1)]
    match('native-record-index.jsonl', b'\n'.join(compact(row) for row in index) + b'\n')
    summary = load(BASE / 'input/native-summary.json')
    assert summary['record_types'] == dict(collections.Counter(row['record_type'] for row in records))
    assert summary['native_unit_count'] == len(units)
    assert summary['manifest_bound_units'] == sum('manifest_binding' in row for row in units)
    assert summary['unit_kinds'] == dict(collections.Counter(row['unit_kind'] for row in units))
    assert summary['exercise_support_states'] == dict(collections.Counter(row.get('exercise_metadata', {}).get('solution_status', 'not_declared') for row in units if row['unit_kind'] == 'exercise'))
    expressions = [expression for row in records for expression in row.get('expressions', [])]
    assert len(expressions) == len({e['expression_id'] for e in expressions}) == summary['expression_hashes_checked']
    assert not {e['expression_id'] for e in expressions}.intersection(row['id'] for row in records)
    for expression in expressions:
        assert expression['content_sha256'] == 'sha256:' + sha(expression['content'].encode('utf-8'))
    facts = []
    for name in NAMES:
        data = (BASE / 'input' / name).read_bytes()
        facts.append({'name': name, 'bytes': len(data), 'sha256': sha(data)})
    receipt = {'schema': 'lebl-native-evidence-binding/1', 'state': 'pass', 'native_commit': COMMIT,
        'checked_utc': datetime.now(timezone.utc).isoformat(), 'anonymous': True,
        'source_dataset': {'url': URL + 'dataset.json', 'bytes': 1913, 'sha256': DATASET_HASH},
        'source_stream': {'url': URL + 'records.jsonl', 'bytes': len(raw), 'sha256': sha(raw), 'records': len(records)},
        'inputs': facts, 'reconstructed_stream_projections': NAMES[:8],
        'expression_hashes_checked': len(expressions),
        'reconstruction_script_sha256': sha(Path(__file__).read_bytes()),
        'original_importer_sha256': sha((ROOT / 'scripts/import-lebl-capability-v1.py').read_bytes()),
        'limitations': ['PDF navigation and TeX entrypoint observations retain the separate historical public-readback receipt; not rederived from the record stream.',
                       'No book source-span/build replay or native schema certification; metadata extraction equality only.']}
    with target.open('xb') as output:
        output.write(pretty(receipt))
    verify()
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', action='store_true')
    parser.add_argument('--base', type=Path, default=BASE)
    args = parser.parse_args()
    result = bind() if args.bind else verify(args.base)
    print(json.dumps({'state': 'pass', 'native_commit': COMMIT, 'source_records': result['source_stream']['records'], 'bound_inputs': len(result['inputs'])}))
