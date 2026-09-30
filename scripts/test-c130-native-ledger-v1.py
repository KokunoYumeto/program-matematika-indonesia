"""Independent native-record comparison and isolated page-source reproduction."""
import argparse
import ast
import copy
import importlib.util
import json
import re
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

def main(cache, base=BASE, metadata_only=False):
    intake = module('c130-native-ledger-v1.py')
    builder = module('build-c130-native-ledger-v1.py')
    view = json.loads((base / 'projection.json').read_bytes())
    with zipfile.ZipFile(cache / intake.ARCHIVES['backend'][0]) as archive:
        native = json.loads(archive.read('backend/dist/backend-v0.json'))
        input_raw = archive.read('backend/input/backend-input.json')
        exporter_raw = archive.read('scripts/export_backend.py')
    assert intake.sha(input_raw) == intake.NATIVE_INPUT and intake.sha(exporter_raw) == intake.NATIVE_EXPORTER
    native_input = json.loads(input_raw)
    function = next(n for n in ast.parse(exporter_raw.decode()).body if isinstance(n, ast.FunctionDef) and n.name == 'nonempty_blocks')
    scope = {'re': re, 'Any': object}
    exec(compile(ast.Module(body=[function], type_ignores=[]), '<hash-bound-native-block-function>', 'exec'), scope)
    reference_blocks = scope['nonempty_blocks']
    block_fixtures = ['a\n\nb\n', '\n \n a\n\n b\n', 'a\finside\n\nb\n', 'same\n\nsame\n', 'a\n\t\n\nb\n', '']
    for text in block_fixtures:
        assert intake.native_blocks(text) == reference_blocks(text)
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
    assert len(target_gaps) == 0
    assert intake.text_location('same\nsame\n', 'same', 1, 1)['state'] == 'declared_lines_exact_text'
    assert intake.text_location('same\nsame\n', 'same', 99, 99)['state'] == 'ambiguous_text_occurrences'
    assert intake.text_location('changed\n', 'original', 1, 1)['state'] == 'text_not_found'
    assert intake.text_location('a\r\nb\n', 'missing', -1, 1)['state'] == 'text_not_found'
    assert intake.text_location('a\finside\nb\n', 'b', 2, 2)['line_range'] == [2, 2]
    assert intake.text_location('a\vinside\nb\n', 'b', 2, 2)['line_range'] == [2, 2]
    assert intake.text_location('a\u2028inside\nb\n', 'b', 2, 2)['line_range'] == [2, 2]
    assert intake.text_location('same\n\nsame\n', 'same', 3, 3)['line_range'] == [3, 3]
    aligned_rows = [r for r in view['segments'] if r['verification']['target']['state'] == 'declared_native_alignment_parts_exact_text']
    assert {r['id'] for r in aligned_rows} == {'segment.r017.book1.ch04.interactive.block-044', 'segment.r017.book1.ch07.text.block-133'}
    original_segments = {r['id']: r for r in native['segments']}
    seeds = {r['id']: r for r in native_input['file_units']}
    alignment_negative = 0
    for projected in aligned_rows:
        row = original_segments[projected['id']]
        loc = projected['verification']['target']
        seed = seeds[row['unit_id']]
        with zipfile.ZipFile(cache / intake.ARCHIVES[loc['archive']][0]) as archive:
            member_raw = archive.read(loc['member'])
        text = intake.normalized(member_raw)
        blocks = reference_blocks(text)
        assert blocks == intake.native_blocks(text)
        override = next(r for r in seed['target_block_alignment_overrides'] if r['source_block_index'] == row['source_block_index'])
        chunks, expected_parts = [], []
        for part in override['target_parts']:
            block = blocks[part['target_block_index'] - 1]
            first, last = part.get('line_start', block['line_start']), part.get('line_end', block['line_end'])
            raw = '\n'.join(text.splitlines()[first - 1:last])
            chunks.append(raw.strip())
            expected_parts.append({'target_block_index': part['target_block_index'], 'line_range': [first, last],
                                   'raw_line_slice_sha256': intake.sha(raw.encode()), 'stripped_part_sha256': intake.sha(raw.strip().encode())})
        assert '\n\n'.join(chunks) == row['target_text']
        assert loc['alignment']['parts'] == expected_parts
        assert loc['alignment']['reconstructed_content_sha256'] == intake.sha(row['target_text'].encode())
        guard = loc['alignment']['target_file_guard']
        assert guard['released_file'] == intake.fact(member_raw)
        assert guard['native_expected_sha256'] == seed['expected_target_sha256']
        assert guard['whole_file_guard_matches'] is (seed['expected_target_sha256'] == intake.sha(member_raw))
        assert guard['whole_file_guard_matches'] is ('interactive' in row['id'])
        authority = loc['alignment']['authority']
        assert intake.native_alignment_location(row, text, row['target_text'], seed, authority)
        bad_cases = [
            (dict(row, unit_id='not-the-native-unit'), text, row['target_text'], seed),
            (dict(row, target_path='not-the-native-file'), text, row['target_text'], seed),
            (dict(row, target_line_end=row['target_line_end'] + 1), text, row['target_text'], seed),
            (row, text, row['target_text'] + 'changed', seed),
        ]
        for altered, target, content, source_seed in bad_cases:
            try:
                result = intake.native_alignment_location(altered, target, content, source_seed, authority)
            except (ValueError, KeyError):
                result = None
            assert result is None, 'Invented alignment accepted'
            alignment_negative += 1
        bad_seed = copy.deepcopy(seed)
        rule = next(r for r in bad_seed['target_block_alignment_overrides'] if r['source_block_index'] == row['source_block_index'])
        rule['target_parts'][0]['line_start'] = 0
        try:
            intake.native_alignment_location(row, text, row['target_text'], bad_seed, authority)
        except ValueError:
            alignment_negative += 1
        else:
            raise AssertionError('Invalid native part bounds accepted')
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
    snapshot = json.loads((base / 'input/native-records.json').read_bytes())
    audit = json.loads((base / 'audit.json').read_bytes())
    review = json.loads((base / 'location-review.json').read_bytes())
    lock = json.loads((base / 'input/source-lock.json').read_bytes())
    baseline = json.loads((base / 'input/location-review-baseline.json').read_bytes())
    builder.validate(view, snapshot, audit, review, lock, baseline)
    builder_checks = 0
    def reject_view(mutation):
        nonlocal builder_checks
        altered = copy.deepcopy(view)
        mutation(altered)
        try:
            builder.validate(altered, snapshot, audit, review, lock, baseline)
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
    def reject_bundle(mutation):
        nonlocal builder_checks
        data = {'view': copy.deepcopy(view), 'audit': copy.deepcopy(audit), 'review': copy.deepcopy(review),
                'lock': copy.deepcopy(lock), 'baseline': copy.deepcopy(baseline)}
        mutation(data)
        data['audit']['location_review'] = intake.fact(intake.packed(data['review']))
        try:
            builder.validate(data['view'], snapshot, data['audit'], data['review'], data['lock'], data['baseline'])
        except (AssertionError, KeyError):
            builder_checks += 1
            return
        raise AssertionError('Fabricated location proof accepted')
    reject_bundle(lambda d: d['audit'].__setitem__('unresolved_target_locations', 21))
    reject_bundle(lambda d: d['audit'].__setitem__('native_alignment_whole_file_guard_mismatches', 0))
    reject_bundle(lambda d: d['review'].__setitem__('semantic_canon_review', True))
    reject_bundle(lambda d: d['baseline']['records'][0].__setitem__('id', 'invented'))
    reject_bundle(lambda d: d['review'].__setitem__('native_records_changed', True))
    reject_bundle(lambda d: d['lock']['native_alignment_authority']['input'].__setitem__('sha256', '0' * 64))
    def hide_guard(data):
        for row in data['view']['segments']:
            guard = row['verification']['target'].get('alignment', {}).get('target_file_guard')
            if guard and guard['whole_file_guard_matches'] is False:
                guard['whole_file_guard_matches'] = True
                current = next(r for r in data['review']['records'] if r['id'] == row['id'])
                current['after_target_verification'] = copy.deepcopy(row['verification']['target'])
    reject_bundle(hide_guard)
    reject_bundle(lambda d: d['review']['records'][0].__setitem__('native_record_sha256', '0' * 64))
    with tempfile.TemporaryDirectory(prefix='c130-native-ledger-check-') as temp:
        tmp = Path(temp)
        intake.intake(cache, tmp / 'intake')
        for relative in ['projection.json', 'audit.json', 'input/source-lock.json', 'input/native-records.json', 'location-review.json', 'input/location-review-baseline.json']:
            assert (tmp / 'intake' / relative).read_bytes() == (base / relative).read_bytes(), relative
        saved_input_pin = intake.NATIVE_INPUT
        intake.NATIVE_INPUT = '0' * 64
        try:
            intake.intake(cache, tmp / 'bad-pin')
        except ValueError:
            alignment_negative += 1
        else:
            raise AssertionError('Wrong native input pin accepted')
        finally:
            intake.NATIVE_INPUT = saved_input_pin
        if metadata_only:
            report = {'state': 'pass', 'mode': 'isolated_metadata_only', 'native_tables_compared': 6,
                      'segment_identities': 5525, 'unit_identities': 1993, 'consumer_negative_cases': builder_checks,
                      'native_alignment_negative_cases': alignment_negative, 'location_fixtures': 8,
                      'frozen_native_block_contract_fixtures': len(block_fixtures), 'review_records': 21,
                      'unresolved_target_locations': 0, 'native_alignment_whole_file_guard_mismatches': 1,
                      'semantic_canon_review': False, 'whole_native_rebuild': False, 'overall_backend_complete': False}
            (base / 'validation.json').write_bytes(intake.packed(report))
            print(json.dumps(report))
            return
        for suffix in ['a', 'b']:
            builder.build(base, tmp / suffix)
            for shipped in (base / 'site').iterdir():
                if shipped.is_file():
                    assert (tmp / suffix / shipped.name).read_bytes() == shipped.read_bytes(), shipped.name
        with zipfile.ZipFile(base / 'site/c130-native-ledger-source-v1.zip') as archive:
            intake.safe_members(archive)
            archive.extractall(tmp / 'source')
        result = subprocess.run([sys.executable, '-B', str(tmp / 'source/scripts/build-c130-native-ledger-v1.py')],
                                capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stderr
        rebuilt = tmp / 'source/backend/course-capsule-v1/adapters/c130-native-ledger-v1/site'
        for shipped in (base / 'site').iterdir():
            assert (rebuilt / shipped.name).read_bytes() == shipped.read_bytes(), shipped.name
    report = {'state': 'pass', 'native_tables_compared': 6, 'segment_identities': 5525,
              'unit_identities': 1993, 'negative_cases': negative, 'consumer_negative_cases': builder_checks, 'location_fixtures': 8,
              'native_alignment_negative_cases': alignment_negative, 'frozen_native_block_contract_fixtures': len(block_fixtures),
              'review_records': 21, 'native_alignment_whole_file_guard_mismatches': 1,
              'intake_replay': True, 'site_replays': 2, 'isolated_source_zip_replay': True,
              'unresolved_target_locations': 0, 'semantic_canon_review': False,
              'whole_native_rebuild': False, 'overall_backend_complete': False}
    (base / 'validation.json').write_bytes(intake.packed(report))
    print(json.dumps(report))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--base', type=Path, default=BASE)
    parser.add_argument('--metadata-only', action='store_true')
    args = parser.parse_args()
    main(args.cache, args.base, args.metadata_only)
