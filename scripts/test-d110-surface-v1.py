"""Independent native-count, semantic-join and negative tests; no Lean engine."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile

SCRIPT = Path(__file__).with_name('build-d110-surface-v1.py')
spec = importlib.util.spec_from_file_location('d110_builder', SCRIPT)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def run():
    data = b.load()
    m = b.project(data)
    units = {u['id']: u for u in m['units']}
    native = {u['record_id']: u for u in data['unit.jsonl']}
    assert set(units) == set(native) and len(units) == 2177
    assert all(units[k]['source_record'] == v for k, v in native.items())
    assert m['relations'] == data['relation.jsonl']
    flagged = {k for k, v in native.items() if v['data'].get('is_exercise') is True}
    assert len(flagged) == 243
    missing = {k for k in flagged if not units[k]['supports']}
    assert missing == {
        'urn:mil:unit:c02:s01:exercise:007', 'urn:mil:unit:c02:s01:exercise:008', 'urn:mil:unit:c02:s01:exercise:009',
        'urn:mil:unit:c03:s01:exercise:my-lemma', 'urn:mil:unit:c03:s01:exercise:my-lemma2', 'urn:mil:unit:c03:s01:exercise:my-lemma3'}
    support = [r for r in data['relation.jsonl'] if r['data']['relation_type'] in ('solves', 'supports')]
    assert sum(len(u['supports']) for u in units.values()) == len(support) == 330
    for r in support:
        d = r['data']
        match = [x for x in units[d['object_id']]['supports'] if x['relation_id'] == r['record_id']]
        assert len(match) == 1 and match[0]['source_record'] == r and match[0]['id'] == d['subject_id']
    holes = units['urn:mil:unit:c08:s03:instance:005']['supports']
    assert len(holes) == 4
    assert {r['source_record']['data']['hole_rank'] for r in holes} == {1, 2, 3, 4}
    assert all(not r['source_record']['data']['is_alternative'] for r in holes)
    for u in units.values():
        if u['code']:
            for lang in ('id', 'en'):
                if u['code'].get(lang) is not None:
                    assert b.sha(u['code'][lang].encode()) == u['code']['sha256'][lang]
        if u['section_id'] and u['kind'] != 'section':
            assert u['reader_routes']['id']['state'] == 'enclosing_section'
    assert sum(u['companion'] for u in units.values()) == 2
    assert m['counts']['solution_fragments_with_both_texts'] == 330
    assert not units['urn:mil:unit:c08:s01:declaration:abgrpmodule']['practice']
    negative = []

    def reject(name, mutate):
        changed = deepcopy(data)
        mutate(changed)
        try:
            b.project(changed)
        except (AssertionError, KeyError, ValueError):
            negative.append(name)
        else:
            raise AssertionError('Mutation accepted: ' + name)

    reject('duplicate_native_id', lambda d: d['unit.jsonl'].append(deepcopy(d['unit.jsonl'][0])))
    reject('unverified_public_reader', lambda d: d['reader-witness.json'].update(public_verified=False))
    reject('unsafe_reader_origin', lambda d: d['reader-witness.json']['readers'].update(id='javascript:alert(1)'))
    reject('missing_section_route', lambda d: d['reader-witness.json']['routes'].pop('urn:mil:unit:c02:s01'))
    reject('invented_reader_anchor', lambda d: d['reader-witness.json']['routes']['urn:mil:unit:c02:s01']['id'].update(anchor='invented'))
    reject('wrong_reader_page_hash', lambda d: d['reader-witness.json']['routes']['urn:mil:unit:c02:s01']['id'].update(page_sha256='0' * 64))
    reject('unknown_rights', lambda d: d['unit.jsonl'][0].update(rights_id='missing'))
    reject('parent_cycle', lambda d: d['unit.jsonl'][1].update(parent_id=d['unit.jsonl'][1]['record_id']))
    reject('learner_code_corruption', lambda d: next(a for a in d['asset.jsonl'] if a['record_id'] == 'urn:mil:asset:c02:s01:code:002')['data'].update(target_text='wrong'))
    reject('wrong_solution_target', lambda d: next(r for r in d['relation.jsonl'] if r['data']['relation_type'] == 'solves')['data'].update(object_id='urn:mil:unit:c01:s01'))
    reject('missing_support_edge', lambda d: d['relation.jsonl'].remove(next(r for r in d['relation.jsonl'] if r['data']['relation_type'] == 'supports')))
    reject('rewired_support_edge', lambda d: next(r for r in d['relation.jsonl'] if r['data']['relation_type'] == 'supports')['data'].update(object_id='urn:mil:unit:c02:s01:solution:001'))
    reject('false_exercise_flag', lambda d: next(u for u in d['unit.jsonl'] if u['record_id'] == 'urn:mil:unit:c08:s01:declaration:abgrpmodule')['data'].update(is_exercise=True))
    reject('solution_code_corruption', lambda d: next(r for r in d['solution-witness.json']['units'] if r['id'] == 'urn:mil:unit:c02:s01:solution:001')['texts']['id'].update(text='invented proof'))
    reject('missing_solution_language', lambda d: next(r for r in d['solution-witness.json']['units'] if r['id'] == 'urn:mil:unit:c02:s01:solution:001')['texts'].pop('id'))
    reject('solution_language_swap', lambda d: next(r for r in d['solution-witness.json']['units'] if r['texts'].get('id', {}).get('sha256') != r['texts'].get('en', {}).get('sha256'))['texts'].update(id={'state': 'exact_hash_span', 'sha256':'0'*64, 'text':'wrong'}))
    # Temporary outputs are narrowly owned by this test; no production source changes.
    with tempfile.TemporaryDirectory(prefix='d110-consumer-test-') as temp:
        _, first = b.build(Path(temp))
        _, second = b.build(Path(temp))
        assert first == second
    report = {'schema': 'd110-independent-consumer-tests/1', 'state': 'pass', 'counts': m['counts'],
              'native_units_all_accounted': True, 'all_native_support_payloads_preserved': True,
              'six_missing_relations_explicit': sorted(missing), 'negative_fixtures': negative,
              'deterministic_replays': 2, 'outputs': [{'path': p, 'bytes': len(v), 'sha256': b.sha(v)} for p, v in first.items()],
              'browser_verified': False, 'published': False, 'new_lean_build': False}
    (b.BASE / 'tests.json').write_bytes(b.encoded(report))
    print(json.dumps({'state': 'pass', 'counts': m['counts'], 'negative_fixtures': len(negative)}))


if __name__ == '__main__':
    run()
