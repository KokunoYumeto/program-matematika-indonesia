"""Read sealed CLP evidence; export only exercise identities and source locators.

No producer file is changed. This is an explicit intake, not a build prerequisite:
the portable consumer replays from the resulting small input capsule.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/clp-teacher-v1'
WORKSPACE = ROOT.parents[2]
CANDIDATE = WORKSPACE / 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/backend_adapters/clp_family_v231_candidate'
DESIGN_SHA = '1ecd40d1d560bbdde903a5c90cd911463812ffb729ddb6316d5c167280532a3b'
MANIFEST_SHA = '54b600004e6ce4d903f6890a0a9a5c7c0d03120da896ea57d3c85edf674f00e5'
KINDS = {'exercise', 'statement', 'question', 'hint', 'answer', 'solution'}
RELATIONS = {'has_hint', 'has_answer', 'has_solution', 'question_for', 'hints', 'answers', 'solves'}
UNIT_KEYS = set('id unit_type unit_class parent_id order source_order source_type_order source_document_order source_local_id native_id collection attributes topology_path rights_id source target source_file source_path source_locator target_file target_path target_locator source_content_sha256 target_content_sha256 source_file_sha256 target_sha256 source_line_start source_line_end source_edition_id edition_id translation_state target_relationship topology_state topology_delta_id concept_ids correction_ids prerequisite_unit_ids'.split())
CLOSURE_KEYS = set('id semantic_exercise_id semantic_unit_id exercise_id target_exercise_id source_local_id source_locator parent_id pair_id surface_kind serialization order path_within_source rights_id edition_id translation_state source_content_sha256 target_content_sha256 delta_issue_ids closure_complete statement_ids hint_ids answer_ids solution_ids target_statement_ids target_hint_ids target_answer_ids target_solution_ids'.split())


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()


def digest(stream):
    h, n = hashlib.sha256(), 0
    for b in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(b)
        n += len(b)
    return {'bytes': n, 'sha256': h.hexdigest()}


def file_fact(path):
    with path.open('rb') as f:
        return digest(f)


def decode_cell(value):
    if value == '':
        return None
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value


def rows(z, member, sha):
    with z.open(member) as f:
        fact = digest(f)
    assert fact['sha256'] == sha, ('Member drift', member)
    with z.open(member) as f:
        if member.endswith('.csv'):
            for row in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig', newline='')):
                yield {k: decode_cell(v) for k, v in row.items()}
        else:
            for line in f:
                yield json.loads(line)


def intake(workspace, candidate):
    design_path, manifest_path = candidate / 'research/CLP_NATIVE_PROFILE_DESIGN.json', candidate / 'build_a/manifest.json'
    assert file_fact(design_path)['sha256'] == DESIGN_SHA
    assert file_fact(manifest_path)['sha256'] == MANIFEST_SHA
    design, manifest = json.loads(design_path.read_bytes()), json.loads(manifest_path.read_bytes())
    capsule = {'schema': 'clp-teacher-native-input/1', 'design_sha256': DESIGN_SHA,
               'common_manifest_sha256': MANIFEST_SHA, 'profiles': {}, 'zero_book_prose': True}
    for profile, cfg in design['profiles'].items():
        archive = next(a for a in design['authority_capsule']['frozen_archives'] if a['archive_id'] == cfg['archive_bindings'][-1])
        path = workspace / archive['path']
        assert file_fact(path) == {k: archive[k] for k in ('bytes', 'sha256')}, profile
        selected = {'course_id': cfg['course_id'], 'archive': {k: archive[k] for k in ('archive_id', 'bytes', 'sha256')},
                    'archive_filename': path.name, 'members': [], 'units': [], 'relations': [], 'closures': []}
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            assert len(names) == len(set(names))
            assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and '\\' not in n for n in names)
            tables = ['units', 'relations'] if profile != 'CLP3' else ['units', 'exercise_closure', 'relations']
            for table in tables:
                suffix = '.csv' if profile == 'CLP2' else '.jsonl'
                name = table + suffix
                member = cfg['member_root'] + '/' + name
                sha = cfg.get('table_member_sha256', {}).get(name) or cfg['table_pair_sha256'][table]['jsonl']
                count, retained = 0, 0
                for row in rows(z, member, sha):
                    count += 1
                    if table == 'units' and (row.get('unit_type') in KINDS or profile == 'CLP3'):
                        # Preserve source/target locator objects; never carry indexed book prose.
                        selected['units'].append({k: v for k, v in row.items() if k in UNIT_KEYS})
                    elif table == 'exercise_closure':
                        item = {k: v for k, v in row.items() if k in CLOSURE_KEYS}
                        item['native_row_sha256'] = hashlib.sha256(encoded(row).rstrip(b'\n')).hexdigest()
                        selected['closures'].append(item)
                    elif table == 'relations' and row.get('relation_type', row.get('relation')) in RELATIONS:
                        selected['relations'].append({k: row.get(k) for k in ('id', 'relation_type', 'relation', 'source_id', 'target_id', 'from_id', 'to_id', 'rights_id') if k in row})
                    else:
                        continue
                    retained += 1
                expected = cfg['table_rows'].get(table)
                if expected is not None:
                    assert count == expected, (profile, table, count, expected)
                selected['members'].append({'path': member, 'sha256': sha, 'rows': count, 'selected_rows': retained})
        capsule['profiles'][profile] = selected
    # Common IDs are copied from the already admitted sealed adapter, never regenerated.
    expected = next(f for f in manifest['files'] if f['path'] == 'tables/units.jsonl')
    unit_path = candidate / 'build_a/tables/units.jsonl'
    assert file_fact(unit_path) == {k: expected[k] for k in ('bytes', 'sha256')}
    wanted = {(profile, u['id']) for profile, p in capsule['profiles'].items() for u in p['units'] if u.get('unit_type') == 'exercise'}
    wanted.update(('CLP3', c['semantic_exercise_id']) for c in capsule['profiles']['CLP3']['closures'])
    capsule['common_units_authority'] = expected
    capsule['common_exercises'] = []
    with unit_path.open(encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            p = r['payload']
            if (p['profile_id'], p['native_id']) in wanted:
                capsule['common_exercises'].append({'id': r['id'], 'profile': p['profile_id'], 'native_id': p['native_id'],
                    'course_id': p['course_id'], 'surface_native_ids': p.get('surface_native_ids', []),
                    'qhas_state': p['native_metadata'].get('qhas_state', {})})
    assert len(capsule['common_exercises']) == len(wanted) == 2198
    assert len({r['id'] for r in capsule['common_exercises']}) == 2198
    # Reuse admitted reader/original routes; do not construct guessed exercise URLs.
    reader_path = ROOT / 'docs/backend/clp/learning-map.json'
    reader_bytes = reader_path.read_bytes()
    readers = json.loads(reader_bytes)
    assert readers['schema'] == 'clp-family-learner-capability/1'
    assert readers['summary']['pages'] == 4077 and readers['summary']['action_count'] == 7
    capsule['reader_routes_authority'] = {'path': 'docs/backend/clp/learning-map.json', 'bytes': len(reader_bytes), 'sha256': hashlib.sha256(reader_bytes).hexdigest()}
    capsule['readers'] = readers['courses']
    return capsule


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=WORKSPACE)
    parser.add_argument('--candidate', type=Path, default=CANDIDATE)
    parser.add_argument('--output', type=Path, default=BASE / 'input/native-exercises.json')
    args = parser.parse_args()
    capsule = intake(args.workspace, args.candidate)
    data = encoded(capsule)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    lock = {'schema': 'clp-teacher-input-lock/1', 'path': args.output.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'design_sha256': DESIGN_SHA, 'manifest_sha256': MANIFEST_SHA}
    args.output.with_name('source-lock.json').write_bytes(encoded(lock))
    print(json.dumps({'state': 'intake-complete', **lock, 'exercises': len(capsule['common_exercises'])}))


if __name__ == '__main__':
    main()
