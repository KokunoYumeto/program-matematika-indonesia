"""Exercise-by-exercise source comparison, hostile fixtures and deterministic replay."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('clp_teacher_builder', ROOT / 'scripts/build-clp-teacher-v1.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def check_exact(native, model):
    common = {(r['profile'], r['native_id']): r for r in native['common_exercises']}
    visited = set()
    for course in model['courses']:
        profile = course['profile']
        p = native['profiles'][profile]
        units = {u['id']: u for u in p['units']}
        closures = {c['id']: c for c in p['closures']}
        for q in course['questions']:
            key = (profile, q['native_id'])
            assert key not in visited
            visited.add(key)
            assert common[key]['id'] == q['id']
            for s in q['surfaces']:
                if profile == 'CLP3':
                    c = closures[s['closure_id']]
                    assert c['semantic_exercise_id'] == q['native_id']
                    assert s['native_id'] == c['exercise_id'] and s['target_native_id'] == c['target_exercise_id']
                    assert s['source']['content_sha256'] == c['source_content_sha256']
                    assert s['target']['content_sha256'] == c['target_content_sha256']
                    assert s['target']['file'] == units[c['parent_id']]['target_path']
                    for kind in b.KINDS:
                        native_kind = 'statement' if kind == 'question' else kind
                        assert s['components'][kind] == c[native_kind + '_ids']
                        assert s['target_components'][kind] == c['target_' + native_kind + '_ids']
                    assert s['delta_issue_ids'] == c['delta_issue_ids']
                else:
                    u = units[q['native_id']]
                    assert s['id'] == u['id']
                    assert s['translation_state'] == u['translation_state']
                    for items in s['components'].values():
                        for item in items:
                            unit = units[item['id']]
                            assert item['rights_id'] == unit['rights_id']
                            assert item['translation_state'] == unit['translation_state']
                            if profile == 'CLP1':
                                assert item['source']['path'] == unit['source']['locator']['xpath']
                                assert item['source']['file'] == unit['source']['locator']['path']
                                assert item['target']['files'] == unit['target']['locators']
                                assert item['target']['alignment'] == 'file-level'
                            else:
                                assert item['source']['content_sha256'] == unit['source_content_sha256']
                                assert item['target']['content_sha256'] == unit['target_content_sha256']
                                assert item['target']['path'] == unit['target_path']
                    relation_ids = {r['id'] for r in s['relations']}
                    expected = {r['id'] for r in p['relations'] if (r.get('source_id') if profile == 'CLP1' else r.get('to_id')) == q['native_id']}
                    assert relation_ids == expected
        assert course['component_vectors'] == b.VECTORS[course['course_id']]
    assert visited == set(common)
    assert model['book_prose_copied'] is False and model['pdf_page_or_html_anchors_claimed'] is False
    assert 'Korpus beku' in model['limitations']['id']
    assert 'does not assert coverage or numbering of other English editions' in model['limitations']['en']


def main():
    native, lock = b.load()
    model = b.project(native)
    check_exact(native, model)
    fixtures = []
    def rejects(name, edit):
        altered = copy.deepcopy(native)
        edit(altered)
        try:
            b.project(altered)
        except (AssertionError, KeyError, ValueError):
            fixtures.append(name)
        else:
            raise AssertionError('Hostile fixture accepted: ' + name)
    rejects('duplicate-common-ID', lambda n: n['common_exercises'][1].update(id=n['common_exercises'][0]['id']))
    rejects('wrong-common-role', lambda n: n['common_exercises'][0].update(course_id='D100'))
    rejects('wrong-profile-role', lambda n: n['profiles']['CLP1'].update(course_id='B30'))
    rejects('missing-unit', lambda n: n['profiles']['CLP1']['units'].pop(0))
    rejects('duplicate-native-unit', lambda n: n['profiles']['CLP1']['units'].append(n['profiles']['CLP1']['units'][0]))
    rejects('missing-edge', lambda n: n['profiles']['CLP1']['relations'].pop(0))
    rejects('duplicate-edge', lambda n: n['profiles']['CLP4']['relations'].append(n['profiles']['CLP4']['relations'][0]))
    rejects('rewired-support', lambda n: n['profiles']['CLP2']['relations'][0].update(to_id=n['profiles']['CLP2']['relations'][1]['to_id']))
    rejects('missing-format', lambda n: n['profiles']['CLP3']['closures'].pop(0))
    rejects('changed-format', lambda n: n['profiles']['CLP3']['closures'][0].update(surface_kind='pdf'))
    rejects('lost-target-solution', lambda n: n['profiles']['CLP3']['closures'][0]['target_solution_ids'].pop())
    rejects('invented-hint', lambda n: n['profiles']['CLP3']['closures'][0]['hint_ids'].append('invented'))
    rejects('false-closure', lambda n: n['profiles']['CLP3']['closures'][0].update(closure_complete=False))
    with tempfile.TemporaryDirectory(prefix='clp-teacher-replay-') as temp:
        a, c = Path(temp)/'a', Path(temp)/'b'
        first, second = b.build(a), b.build(c)
        assert first == second
        for name in [x['path'] for x in first['files']] + ['teacher-build.json']:
            assert (a/name).read_bytes() == (c/name).read_bytes(), name
            assert (a/name).read_bytes() == (b.BASE/'site'/name).read_bytes(), ('Stale local output', name)
        for role in b.COUNTS:
            for lang in ('id', 'en'):
                name = f'{role}.teacher' + ('.en' if lang == 'en' else '') + '.html'
                html = (a/name).read_text(encoding='utf-8')
                assert f'<html lang="{lang}">' in html and 'type="application/json"' in html
                assert 'aria-live="polite"' in html and 'type="search"' in html
                assert 'gpt-6-astra' in html and 'Ultra' in html
                assert '<script src="http' not in html and 'fetch(' not in html
                payload = html.split('<script id="planner-data" type="application/json">')[1].split('</script>')[0]
                embedded = json.loads(payload)['model']
                assert embedded['questions'] == next(c for c in model['courses'] if c['course_id'] == role)['questions']
                assert embedded['input_identity'] == lock
    subprocess.run(['node', str(ROOT/'scripts/test-clp-teacher-ui-v1.mjs')], cwd=ROOT, check=True)
    result = {'schema': 'clp-teacher-tests/1', 'state': 'pass', 'native_exercises_individually_checked': 2198,
              'course_counts': b.COUNTS, 'component_vectors': b.VECTORS, 'hostile_fixtures': fixtures,
              'two_clean_builds_byte_identical': True, 'input_identity': lock,
              'public_deployment_claimed': False, 'whole_program_complete': False}
    (b.BASE/'tests.json').write_bytes(b.encoded(result))
    print(json.dumps(result))


if __name__ == '__main__':
    main()
