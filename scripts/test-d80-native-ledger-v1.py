"""Independent D80 record preservation, exact joins, refusals and isolated replay."""
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('d80_ledger', ROOT/'scripts/d80-native-ledger-v1.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
p, lock, raw = m.project(ROOT)
checks, rejected = [], []

def check(name, value):
    assert value, name
    checks.append(name)

def reject(name, operation):
    try:
        operation()
    except (ValueError, FileNotFoundError, KeyError):
        rejected.append(name)
    else:
        raise AssertionError('Accepted invalid fixture: '+name)

sources = {
    'segments': (m.lines(raw['segment_ledger_reference']), 'segment_id'),
    'terms': (m.csv_rows(raw['term_ledger_reference']), 'concept_id'),
    'corrections': (m.csv_rows(raw['source_correction_ledger_reference']), 'correction_id'),
    'diagrams': (m.csv_rows(raw['figure_alt_ledger_reference']), 'diagram_id'),
}
for kind, (rows, key) in sources.items():
    actual = {row['id']:row['native'] for row in p['rows'] if row['kind'] == kind}
    check('all_original_'+kind+'_records_preserved', actual == {row[key]:row for row in rows})
check('7760_visible_records', len(p['rows']) == 7760)
check('8430_native_records_separately_accounted', sum(len(rows) for rows,key in sources.values()) +
      len(m.lines(raw['native_units'])) + len(m.csv_rows(raw['terminology_control_reference'])) +
      len(json.loads(raw['diagram_override_ledger_reference'])['overrides']) == p['summary']['native_records'] == 8430)
check('no_false_completion_or_canon_approval', not any(p[k] for k in ['native_records_changed','book_bodies_copied','semantic_canon_approval','native_book_rebuilt']))
check('segment_locator_precision', p['summary']['flags']['unit_slice'] == 1736 and p['summary']['flags']['exact_source_span'] == 4611)
terms = [row for row in p['rows'] if row['kind'] == 'terms']
check('88_provisional_terms_not_promoted', sum('provisional' in row['flags'] for row in terms) == 88)
check('two_term_disagreements_retained', {row['id'] for row in terms if 'term_disagreement' in row['flags']} ==
      {'math.homological.cup_product','math.set_theory.regular_small_cardinal'})
unresolved = [row for row in terms if row['discovery_scope'] == 'unresolved_recorded_first_introduction']
check('two_broad_prelude_locators_not_guessed', len(unresolved) == 2 and {row['id'] for row in unresolved} ==
      {'math.category.category','math.category.functor'} and all(row['related_native']['terminology_control']['first_o014_unit'] ==
      'o014.aljabr2.prelude' and not row['unit_links'] and row['discovery_scope'] == 'unresolved_recorded_first_introduction' for row in unresolved))
check('nine_terms_have_no_recorded_first_introduction', len([r for r in terms if r['discovery_scope'] == 'no_first_introduction_recorded']) == 9)
controls = {row['concept_id']:row for row in m.csv_rows(raw['terminology_control_reference'])}
check('all_511_control_records_preserved', {row['id']:row['related_native']['terminology_control'] for row in terms} == controls)
overrides = {row['diagram_id']:row for row in json.loads(raw['diagram_override_ledger_reference'])['overrides']}
check('13_overrides_and_originals_both_retained', {row['id']:row['related_native']['reader_override'] for row in p['rows']
      if 'reader_override' in row['related_native']} == overrides)
pending = next(row for row in p['rows'] if row['id'] == 'O014-O001')
check('pending_correction_remains_pending', pending['native']['status'] == 'observed_not_modified_pending_consolidated_review')
check('all_73_corrections_have_exact_unit_joins', len([r for r in p['rows'] if r['kind'] == 'corrections' and r['unit_links']]) == 73)
route_index = {row['unit_id']:row for row in m.lines((ROOT/m.OLD/'data/routes.jsonl').read_bytes())}
for row in p['rows']:
    assert [r['unit_id'] for r in row['unit_links']] == row['unit_ids']
    for link in row['unit_links']:
        assert link['url'] == route_index[link['unit_id']]['target_url']
check('every_link_matches_exact_pinned_reader_route', True)
archive_bytes = m.archive_metadata(lock, raw)
with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
    check('exact_archive_inventory', set(archive.namelist()) == {'NOTICE.txt','source-lock.json'} | {r['native_path'] for r in lock['inputs']} and archive.testzip() is None)
    for entry in lock['inputs']:
        assert archive.read(entry['native_path']) == raw[entry['role']]
    check('eight_native_files_byte_identical_in_archive', True)
    check('archive_lock_byte_identical', archive.read('source-lock.json') == (ROOT/m.BASE/'source-lock.json').read_bytes())
private = re.compile(r'(?<![A-Za-z])[A-Za-z]:[\\/]|file://|github_pat_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9_-]{20,}', re.I)
def privacy_hit(text):
    # This exact published diagram phrase is a quotient-map LaTeX label, not a Q: drive.
    # Accept neither arbitrary LaTeX commands nor arbitrary q: paths as exceptions.
    return private.search(re.sub(r'q:\\+text\{ morfisme kuosien', 'quotient-map-label', text))
check('native_metadata_privacy', not any(privacy_hit(data.decode()) for data in raw.values()))
check('projection_privacy', privacy_hit(m.encode(p).decode()) is None)
check('privacy_exception_does_not_hide_drive_paths', all(privacy_hit(s) for s in ['C:/private/file',r'q:\secret.txt','file:///private']))
for bad in ['../outside.json','/absolute.json','C:/private.json','folder\\outside.json']:
    reject('unsafe_path_'+bad, lambda bad=bad:m.safe_path(bad))

with tempfile.TemporaryDirectory(prefix='d80-native-replay-') as temp:
    isolated = Path(temp)/'source'
    files = [m.BASE/'source-lock.json'] + [m.BASE/entry['path'] for entry in lock['inputs']]
    files += [Path(entry['path']) for entry in lock['authorities']]
    files += [Path('scripts/d80-native-ui.js'),Path('docs/backend/d60/native-ledger/ledger.css')]
    for relative in files:
        dest = isolated/relative
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/relative,dest)
    _, first = m.build(isolated,Path(temp)/'a')
    _, second = m.build(isolated,Path(temp)/'b')
    check('two_isolated_metadata_only_builds_identical', first == second)
    for name, value in first.items():
        assert m.identity((ROOT/m.BASE/'site'/name).read_bytes()) == value
    check('isolated_outputs_match_working_outputs', True)
    entry = lock['inputs'][2]
    target = isolated/m.BASE/entry['path']
    original = target.read_bytes()
    target.write_bytes(original+b'\n')
    reject('changed_native_bytes', lambda:m.load(isolated))
    # Altering the intake hash as well must not override the original native pin.
    changed_lock = json.loads((isolated/m.BASE/'source-lock.json').read_bytes())
    changed_lock['inputs'][2].update(m.identity(target.read_bytes()))
    (isolated/m.BASE/'source-lock.json').write_bytes(m.encode(changed_lock))
    reject('forged_intake_hash', lambda:m.load(isolated))
    (isolated/m.BASE/'source-lock.json').write_bytes(m.encode(lock))
    target.unlink()
    reject('missing_native_file', lambda:m.load(isolated))
    target.write_bytes(original)
    authority = isolated/lock['authorities'][0]['path']
    authority.write_bytes(authority.read_bytes()+b'\n')
    reject('changed_central_authority', lambda:m.load(isolated))
result = subprocess.run(['node',str(ROOT/'scripts/test-d80-native-ui.cjs')],cwd=ROOT,check=True,capture_output=True,text=True)
api = json.loads(result.stdout)
check('independent_javascript_filter_tests', api['state'] == 'pass' and api['checks'] == 9)
receipt = {'schema':'d80-native-ledger-tests/1','state':'pass','checks':checks,'negative_fixtures':rejected,
           'summary':p['summary'],'outputs':first,'source_archive':m.identity(archive_bytes),
           'source_lock':m.identity((ROOT/m.BASE/'source-lock.json').read_bytes()),'javascript':api,
           'semantic_canon_approval':False,'native_book_rebuilt':False,'scope':'Native metadata preservation and isolated replay; browser checks, publication and mathematical/canon review are separate.'}
(ROOT/m.BASE/'tests.json').write_bytes(m.encode(receipt))
print(json.dumps({'state':'pass','checks':len(checks),'negative_fixtures':len(rejected),'outputs':len(first)}))
