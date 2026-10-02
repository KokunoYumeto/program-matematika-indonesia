"""Freeze exact published native metadata, never book bodies or producer edits.

The archive is only an intake witness. Normal replay uses the eleven frozen
JSONL shards and the small audit/lock; no producer checkout or network needed.
No native scripts, TeX engine or publication transaction are executed here.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d60-native-ledger-v1'
AUTHORITY = 'backend/v2.3/authorities/D60_FINAL_OWNER_AUTHORITY_20260830.json'
INPUT_AUTHORITY = 'backend/v2.3/extensions/d60-algebraic-topology-v0.1.0/INPUT_AUTHORITIES.json'


def identity(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def frozen(path, data):
    if path.exists():
        require(path.read_bytes() == data, 'Frozen intake differs: ' + path.name)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(data)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()


def current_heads(rows):
    superseded = {r['supersedes'] for r in rows if r.get('supersedes')}
    return [r for r in rows if r['id'] not in superseded]


def table_rows(data, expected):
    rows = [json.loads(line) for line in data.decode('utf-8').splitlines() if line]
    ids = [r.get('id') for r in rows]
    require(len(rows) == expected, 'Native record count differs')
    require(all(isinstance(i, str) and i for i in ids) and len(set(ids)) == len(ids), 'Native identity is missing or duplicated')
    return rows


def safe_members(archive):
    members = archive.infolist()
    names = [m.filename for m in members]
    require(len(names) == len(set(names)), 'Duplicate archive name')
    require(sum(m.file_size for m in members) <= 64 * 1024**2, 'Archive expansion exceeds exact bounded intake')
    for member in members:
        name = member.filename
        path = PurePosixPath(name)
        require(not path.is_absolute() and '..' not in path.parts and '\\' not in name and ':' not in name, 'Unsafe archive member')
        require(not member.flag_bits & 1 and (member.external_attr >> 16) & 0o170000 != 0o120000, 'Encrypted or symlink member')
    require(archive.testzip() is None, 'Archive CRC failure')
    return set(names)


def analyze(shards, archive, members, witness):
    current = {name: current_heads(rows) for name, rows in shards.items()}
    indexed = {name: {r['id']: r for r in rows} for name, rows in shards.items()}
    global_ids = [r['id'] for rows in shards.values() for r in rows]
    require(len(global_ids) == len(set(global_ids)), 'Native identity collides across streams')
    for name, rows in shards.items():
        parent_ids = [r['supersedes'] for r in rows if r.get('supersedes')]
        require(all(i in indexed[name] for i in parent_ids), 'Missing supersession parent: ' + name)
        for row in rows:
            seen = set()
            value = row
            while value.get('supersedes'):
                require(value['id'] not in seen, 'Supersession cycle: ' + name)
                seen.add(value['id'])
                value = indexed[name][value['supersedes']]
    branches = {}
    for name, rows in shards.items():
        group = defaultdict(list)
        for row in rows:
            if row.get('supersedes'):
                group[row['supersedes']].append(row['id'])
        branches[name] = [{'parent_id': parent, 'child_ids': sorted(children)}
                          for parent, children in sorted(group.items()) if len(children) > 1]
    reference_fields = {
        'terms': {'concept_id': 'concepts', 'scope_unit_id': 'units', 'evidence_segment_id': 'segments', 'rights_component_id': 'rights'},
        'segments': {'unit_id': 'units', 'rights_component_id': 'rights'},
        'corrections': {'unit_id': 'units', 'evidence_segment_id': 'segments'},
    }
    reference_gaps = []
    for name, fields in reference_fields.items():
        for row in current[name]:
            for field, destination in fields.items():
                value = row.get(field)
                if value and value not in indexed[destination]:
                    reference_gaps.append({'id': row['id'], 'field': field, 'value': value, 'stream': destination})
            if name == 'corrections':
                for value in row.get('affected_unit_ids', []):
                    if value not in indexed['units']:
                        reference_gaps.append({'id': row['id'], 'field': 'affected_unit_ids', 'value': value, 'stream': 'units'})
    target_checks = []
    files = {}
    for row in current['segments']:
        loc = row.get('target_locator')
        if not isinstance(loc, dict):
            target_checks.append({'id': row['id'], 'state': 'no_native_target_locator'})
            continue
        path = loc.get('path')
        expected = loc.get('file_sha256')
        check = {'id': row['id'], 'path': path, 'declared_file_sha256': expected,
                 'line_start': loc.get('line_start'), 'line_end': loc.get('line_end')}
        if path not in members:
            check['state'] = 'file_absent_from_released_source'
        else:
            if path not in files:
                data = archive.read(path)
                files[path] = {**identity(data), 'lines': len(data.decode('utf-8').splitlines())}
            actual = files[path]
            check['actual_file_sha256'] = actual['sha256']
            start, end = loc.get('line_start'), loc.get('line_end')
            check['line_range_in_bounds'] = isinstance(start, int) and isinstance(end, int) and 1 <= start <= end <= actual['lines']
            check['state'] = ('exact_file_identity' if expected == actual['sha256'] else
                              'declared_file_hash_missing' if not expected else 'declared_file_hash_differs')
        target_checks.append(check)
    return {
        'schema': 'd60-native-ledger-intake-audit/1', 'course_id': 'D60',
        'current_head_policy': 'Preserve the existing native adapter policy: IDs not superseded by another row. Preserve every branch and historical row.',
        'all_counts': {name: len(rows) for name, rows in shards.items()},
        'current_counts': {name: len(rows) for name, rows in current.items()},
        'supersession_branches': {name: value for name, value in branches.items() if value},
        'reference_gaps': reference_gaps,
        'current_terms_missing_schema_envelope': [r['id'] for r in current['terms'] if not r.get('schema') or not r.get('schema_version')],
        'current_terms_missing_native_terminology_status': [r['id'] for r in current['terms'] if not r.get('terminology_status')],
        'target_file_checks': target_checks,
        'target_check_counts': dict(Counter(r['state'] for r in target_checks)),
        'target_file_witnesses': {name: value for name, value in sorted(files.items())},
        'route_witness': witness,
        'limits': ['Exact metadata identity and reference checks, not semantic/canon approval.',
                   'Native admitted/built states are original recorded claims, not new certification.',
                   'Target whole-file identity checks do not prove translation correctness or each content-hash convention.',
                   'No native scripts executed and no complete native-book rebuild claimed.',
                   'Historical records, missing fields and supersession branches remain unchanged.'],
    }


def intake(source):
    authority_data = (ROOT / AUTHORITY).read_bytes()
    authority = json.loads(authority_data)
    input_data = (ROOT / INPUT_AUTHORITY).read_bytes()
    inputs = json.loads(input_data)
    source_fact = next(r for r in inputs['authorities'] if r['role'] == 'final_source_backend')
    data = source.read_bytes()
    require(identity(data) == {key: source_fact[key] for key in ('bytes', 'sha256')}, 'Released archive byte identity differs')
    witness_path = 'backend/course-capsule-v1/adapters/d60-surface-v1/reader-witness.json'
    witness_data = (ROOT / witness_path).read_bytes()
    shards, raws = {}, {}
    with zipfile.ZipFile(source) as archive:
        members = safe_members(archive)
        for fact in authority['owner_native']['table_facts']:
            raw = archive.read(fact['path'])
            require(identity(raw) == {key: fact[key] for key in ('bytes', 'sha256')}, 'Native shard identity differs: ' + fact['path'])
            name = Path(fact['path']).stem
            raws[name] = raw
            shards[name] = table_rows(raw, fact['records'])
        audit = analyze(shards, archive, members, {'path': witness_path, **identity(witness_data)})
    require(audit['current_counts'] == inputs['owner_native_closure']['current_head_counts'], 'Current native-head scope differs')
    require(sum(audit['all_counts'].values()) == 8338, 'Full native scope differs')
    audit['current_native_heads'] = sum(audit['current_counts'].values())
    audit['existing_adapter_materialized_record_count'] = inputs['owner_native_closure']['materialized_current_native_records']
    audit['count_domains'] = 'All original native rows, all current native heads, and the existing adapter materialized subset are distinct counts; never substitute one for another.'
    url = 'https://zenodo.org/records/22168033/files/' + Path(source_fact['path']).name + '?download=1'
    lock = {'schema': 'd60-native-ledger-source-lock/1', 'course_id': 'D60',
            'source_archive': {'url': url, **identity(data), 'members': len(members)},
            'source_tables': authority['owner_native']['table_facts'],
            'inputs': [{'path': AUTHORITY, **identity(authority_data)}, {'path': INPUT_AUTHORITY, **identity(input_data)},
                       {'path': witness_path, **identity(witness_data)}],
            'native_records_unchanged': True, 'book_bodies_copied': False,
            'semantic_canon_approval': False, 'whole_native_book_rebuilt': False}
    for name, raw in sorted(raws.items()):
        frozen(BASE / 'input' / (name + '.jsonl'), raw)
    frozen(BASE / 'source-lock.json', json_bytes(lock))
    frozen(BASE / 'intake-audit.json', json_bytes(audit))
    seal = {'schema': 'd60-native-ledger-intake-seal/1',
            'files': {'source-lock.json': identity(json_bytes(lock)), 'intake-audit.json': identity(json_bytes(audit))}}
    frozen(BASE / 'intake-seal.json', json_bytes(seal))
    print(json.dumps({'state': 'pass', 'native_streams': len(shards), 'native_records': 8338,
                      'current_native_heads': audit['current_native_heads'],
                      'existing_adapter_materialized_records': audit['existing_adapter_materialized_record_count'],
                      'metadata_bytes': sum(len(x) for x in raws.values()),
                      'reference_gaps': len(audit['reference_gaps']), 'target_files': audit['target_check_counts'],
                      'native_book_rebuilt': False}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, required=True)
    intake(parser.parse_args().archive)
