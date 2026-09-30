"""Independent native-record comparison and isolated page-source reproduction."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/c130-native-ledger-v1'

def module(filename):
    spec = importlib.util.spec_from_file_location(filename, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def main(cache):
    intake = module('c130-native-ledger-v1.py')
    builder = module('build-c130-native-ledger-v1.py')
    view = json.loads((BASE / 'projection.json').read_bytes())
    with zipfile.ZipFile(cache / intake.ARCHIVES['backend'][0]) as archive:
        native = json.loads(archive.read('backend/dist/backend-v0.json'))
    for name in ['terms', 'concepts', 'corrections', 'rights']:
        actual = [row['native'] for row in view['terms']] if name == 'terms' else view[name]
        assert actual == native[name], name
    for name in ['segments', 'units']:
        original = {r['id']: r for r in native[name]}
        assert {r['id'] for r in view[name]} == set(original)
        for row in view[name]:
            assert row['canonical_native_record_sha256'] == intake.sha(intake.packed(original[row['id']]))
            assert all(row[k] == original[row['id']][k] for k in row if k not in {'verification', 'canonical_native_record_sha256'})
            assert 'source_text' not in row and 'target_text' not in row
    assert len(view['audit']['issues']) == 0
    assert not view['audit']['semantic_canon_review'] and not view['audit']['whole_native_rebuild']
    target_gaps = {r['id'] for r in view['segments'] if r['verification']['target']['state'] in {'text_not_found', 'ambiguous_text_occurrences'}}
    assert len(target_gaps) == 21
    assert intake.text_location('same\nsame\n', 'same', 1, 1)['state'] == 'declared_lines_exact_text'
    assert intake.text_location('same\nsame\n', 'same', 99, 99)['state'] == 'ambiguous_text_occurrences'
    assert intake.text_location('changed\n', 'original', 1, 1)['state'] == 'text_not_found'
    assert intake.text_location('a\r\nb\n', 'missing', -1, 1)['state'] == 'text_not_found'
    negative = 0
    def rejected(mutation):
        nonlocal negative
        altered = copy.deepcopy(native)
        mutation(altered)
        try:
            intake.project(altered, lambda *args: {'state': 'fixture'})
        except (ValueError, KeyError):
            negative += 1
            return
        raise AssertionError('Corrupt native linkage accepted')
    rejected(lambda data: data['terms'].__setitem__(1, data['terms'][0]))
    rejected(lambda data: data['terms'][0].__setitem__('concept_id', 'missing'))
    rejected(lambda data: data['segments'][0].__setitem__('unit_id', 'missing'))
    rejected(lambda data: data['segments'][0].__setitem__('rights_component_id', 'missing'))
    rejected(lambda data: data['corrections'][0].__setitem__('affected_unit_ids', ['missing']))
    changed = copy.deepcopy(native)
    changed['segments'][0]['source_text'] += 'changed'
    assert intake.project(changed, lambda *args: {'state': 'fixture'})['audit']['issues']
    negative += 1
    snapshot = json.loads((BASE / 'input/native-records.json').read_bytes())
    audit = json.loads((BASE / 'audit.json').read_bytes())
    builder_checks = 0
    def reject_view(mutation):
        nonlocal builder_checks
        altered = copy.deepcopy(view)
        mutation(altered)
        try:
            builder.validate(altered, snapshot, audit)
        except (AssertionError, KeyError):
            builder_checks += 1
            return
        raise AssertionError('Unsupported consumer metadata accepted')
    reject_view(lambda d: d['segments'].__setitem__(1, d['segments'][0]))
    reject_view(lambda d: d['segments'][0].__setitem__('unit_id', 'missing'))
    reject_view(lambda d: d['segments'][0].__setitem__('rights_component_id', 'missing'))
    reject_view(lambda d: d['segments'][0].__setitem__('concept_ids', ['missing']))
    reject_view(lambda d: d['segments'][0].__setitem__('target_text', 'whole book prose'))
    reject_view(lambda d: d['terms'][0]['native'].__setitem__('preferred', 'unverified replacement'))
    reject_view(lambda d: d['terms'][0].__setitem__('concept_segment_ids', ['invented']))
    reject_view(lambda d: d['terms'][0]['audit'].__setitem__('semantic_canon_review', True))
    reject_view(lambda d: d['audit'].__setitem__('whole_native_rebuild', True))
    reject_view(lambda d: d['segments'][0]['verification']['target'].__setitem__('state', 'invented_exact_match'))
    reject_view(lambda d: d['corrections'][0].__setitem__('affected_unit_ids', ['missing']))
    with tempfile.TemporaryDirectory(prefix='c130-native-ledger-check-') as temp:
        tmp = Path(temp)
        intake.intake(cache, tmp / 'intake')
        for relative in ['projection.json', 'audit.json', 'input/source-lock.json', 'input/native-records.json']:
            assert (tmp / 'intake' / relative).read_bytes() == (BASE / relative).read_bytes(), relative
        for suffix in ['a', 'b']:
            builder.build(BASE, tmp / suffix)
            for shipped in (BASE / 'site').iterdir():
                if shipped.is_file():
                    assert (tmp / suffix / shipped.name).read_bytes() == shipped.read_bytes(), shipped.name
        with zipfile.ZipFile(BASE / 'site/c130-native-ledger-source-v1.zip') as archive:
            intake.safe_members(archive)
            archive.extractall(tmp / 'source')
        result = subprocess.run([sys.executable, '-B', str(tmp / 'source/scripts/build-c130-native-ledger-v1.py')],
                                capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stderr
        rebuilt = tmp / 'source/backend/course-capsule-v1/adapters/c130-native-ledger-v1/site'
        for shipped in (BASE / 'site').iterdir():
            assert (rebuilt / shipped.name).read_bytes() == shipped.read_bytes(), shipped.name
    report = {'state': 'pass', 'native_tables_compared': 6, 'segment_identities': 5525,
              'unit_identities': 1993, 'negative_cases': negative, 'consumer_negative_cases': builder_checks, 'location_fixtures': 4,
              'intake_replay': True, 'site_replays': 2, 'isolated_source_zip_replay': True,
              'unresolved_target_locations': 21, 'semantic_canon_review': False}
    (BASE / 'validation.json').write_bytes(intake.packed(report))
    print(json.dumps(report))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path, required=True)
    args = parser.parse_args()
    main(args.cache)
