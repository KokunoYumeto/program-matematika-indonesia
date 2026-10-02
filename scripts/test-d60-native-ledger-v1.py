"""Independent identity, preservation, refusal and isolated projection replay checks."""
import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile
import zipfile
from io import BytesIO

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('d60_ledger', ROOT / 'scripts/d60-native-ledger-v1.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
lock, audit, shards, raw = module.load_inputs(ROOT)
projection, original = module.project(ROOT)
checks = []
def check(name, condition):
    assert condition, name
    checks.append(name)

check('exact_current_scope', projection['summary']['counts'] == {'terms': 528, 'segments': 2174, 'corrections': 564, 'rights': 96})
check('distinct_count_boundaries', [projection['summary'][k] for k in ['all_native_records', 'current_native_heads', 'existing_materialized_subset', 'visible_current_records']] == [8338, 7996, 6279, 3362])
for kind in ['terms', 'segments', 'corrections', 'rights']:
    expected = {r['id']: r for r in module.heads(shards[kind])}
    actual = {r['id']: r['native'] for r in projection['rows'] if r['kind'] == kind}
    check('unchanged_current_' + kind, actual == expected)
check('no_canon_or_book_rebuild_claim', projection['semantic_canon_approval'] is False and projection['native_book_rebuilt'] is False)
check('references_closed', projection['summary']['reference_gaps'] == 0)
check('all_unit_contexts', len(projection['unit_contexts']) == 2204)
units = {r['id']: r for r in shards['units']}
for identifier, context in projection['unit_contexts'].items():
    assert context['native_path'] == units[identifier]['path']
    assert context['semantic_applicability_asserted'] is False
    assert context['rights_component_ids'] == [units[identifier]['rights_component_id']]
    assert context['path_identity_resolution'][-1]['current_native_id'] == identifier
    for entry in context['path_identity_resolution']:
        for candidate in entry['matched_native_ids']:
            if entry['evidence'] == 'exact_native_id':
                assert candidate == entry['native_path_value']
            else:
                assert units[candidate]['source_local_id'] == entry['native_path_value']
        assert {leaf for candidate in entry['matched_native_ids'] for leaf in module.leaves(candidate, units)} == {entry['current_native_id']}
checks.append('all_native_paths_and_exact_local_alias_witnesses')
check('seventy_three_original_local_id_paths_preserved', projection['summary']['unit_paths_with_recorded_local_ids'] == 73)
mismatches = [r for r in projection['rows'] if 'target_file_identity_differs' in r['flags']]
check('target_mismatch_not_silently_repaired', len(mismatches) == 73 and {r['target_identity']['path'] for r in mismatches} == {'source/id-ID/units/unit-020-lecture-020.md'})
check('all_terms_explicitly_unverified', all('canon_not_independently_checked' in r['flags'] for r in projection['rows'] if r['kind'] == 'terms'))
for kind, branches in audit['supersession_branches'].items():
    for branch in branches:
        current_ids = {r['id'] for r in module.heads(shards[kind])}
        indexed = {r['id']: r for r in shards[kind]}
        assert set(branch['child_ids']).issubset(indexed), 'Every historical branch child is retained'
        assert {leaf for child in branch['child_ids'] for leaf in module.leaves(child, indexed)}.issubset(current_ids), 'Every branch resolves to retained current leaves'
checks.append('original_supersession_branches_retained')
binary = module.metadata_zip(ROOT, raw)
with zipfile.ZipFile(BytesIO(binary)) as archive:
    check('exact_metadata_archive_inventory', len(archive.infolist()) == 13 and archive.testzip() is None)
    for name, data in raw.items():
        assert archive.read('backend/' + name + '.jsonl') == data
    assert archive.read('source-lock.json') == (ROOT / module.BASE / 'source-lock.json').read_bytes()
checks.append('all_eleven_streams_byte_identical_in_zip')
private = re.compile(r'(?<![A-Za-z])[A-Za-z]:[\\/]|file://|github_pat_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9_-]{20,}', re.I)
check('native_metadata_privacy', not any(private.search(data.decode()) for data in raw.values()))
check('projection_privacy', private.search(module.json_bytes(projection).decode()) is None)
refusals = []
def reject(name, operation):
    try:
        operation()
    except (ValueError, AssertionError):
        refusals.append(name)
    else:
        raise AssertionError('Accepted negative fixture: ' + name)
reject('missing_supersession_parent', lambda: module.leaves('a', {'a': {'id': 'a', 'supersedes': 'unknown'}}))
reject('cyclic_supersession', lambda: module.leaves('a', {'a': {'id': 'a', 'supersedes': 'b'}, 'b': {'id': 'b', 'supersedes': 'a'}}))
reject('unknown_unit', lambda: module.leaves('unknown', units))
branch = {'a': {'id': 'a'}, 'b': {'id': 'b', 'supersedes': 'a'}, 'c': {'id': 'c', 'supersedes': 'a'}}
check('branch_has_both_leaves', module.leaves('a', branch) == ['b', 'c'])
with tempfile.TemporaryDirectory(prefix='d60-native-replay-') as temp:
    isolated = Path(temp) / 'source'
    relative_files = [module.BASE / n for n in ['intake-seal.json', 'intake-audit.json', 'source-lock.json']]
    relative_files += [module.BASE / 'input' / (name + '.jsonl') for name in raw]
    relative_files += [Path(item['path']) for item in lock['inputs']]
    relative_files += [module.ASSETS / n for n in ['ledger-ui.js', 'ledger.css']]
    for relative in relative_files:
        target = isolated / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    _, a = module.build(isolated, Path(temp) / 'a')
    _, b = module.build(isolated, Path(temp) / 'b')
    check('two_isolated_metadata_only_replays', a == b)
    for name, expected in a.items():
        assert module.identity((ROOT / module.OUT / name).read_bytes()) == expected
    checks.append('isolated_outputs_match_current_outputs')
    shard = isolated / module.BASE / 'input' / 'terms.jsonl'
    original_bytes = shard.read_bytes()
    shard.write_bytes(original_bytes + b'\n')
    reject('tampered_native_stream', lambda: module.load_inputs(isolated))
    shard.write_bytes(original_bytes)
    authority = isolated / lock['inputs'][0]['path']
    authority.write_bytes(authority.read_bytes() + b'\n')
    reject('tampered_central_authority', lambda: module.load_inputs(isolated))
receipt = {'schema': 'd60-native-ledger-independent-tests/1', 'state': 'pass', 'checks': checks,
           'negative_fixtures': refusals, 'summary': projection['summary'], 'outputs': a,
           'source_archive': lock['source_archive'], 'semantic_canon_approval': False, 'native_book_rebuilt': False,
           'scope': 'Metadata identity, raw-history preservation, exact path aliases, privacy and isolated projection replay. Browser and full-book checks are separate.'}
(ROOT / module.BASE / 'tests.json').write_bytes(module.json_bytes(receipt))
print(json.dumps({'state': 'pass', 'checks': len(checks), 'refusals': len(refusals), 'isolated_outputs': len(a)}), flush=True)
