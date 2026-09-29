"""Stage the tested CLP planner additively; keep all existing book routes."""
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('clp', Path(__file__).with_name('build-clp-teacher-v1.py'))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def main():
    tests = json.loads((b.BASE/'tests.json').read_bytes())
    package = json.loads((b.BASE/'source-package.json').read_bytes())
    built = json.loads((b.BASE/'site/teacher-build.json').read_bytes())
    assert tests['state'] == package['state'] == 'pass'
    assert tests['input_identity'] == built['input_identity']
    navigation, nav_lock = b.load_navigation()
    assert tests['b20_navigation_identity'] == nav_lock['mapping']
    assert tests['b20_printed_reader_links'] == 2705
    assert tests['other_clp_profiles_unchanged'] is True
    b20 = json.loads((b.BASE/'site/B20.teacher.json').read_bytes())
    assert b20['navigation_identity'] == nav_lock['mapping']
    assert b20['navigation_reader'] == navigation['reader']
    assert {q['native_id']:q['navigation'] for q in b20['questions']} == {q['native_id']:q for q in navigation['questions']}
    outputs = {}
    for f in built['files']:
        data = (b.BASE/'site'/f['path']).read_bytes()
        assert len(data) == f['bytes'] and b.sha(data) == f['sha256']
        if f['path'].endswith('.html'):
            label = 'Complete editable planner source ZIP' if '.en.' in f['path'] else 'ZIP sumber lengkap perencana yang dapat disunting'
            data = data.decode().replace('</footer>', f'<p><a href="{package["package"]["path"]}" download>{label}</a></p></footer>').encode()
        outputs[f['path']] = data
    zipped = package['package']
    payload = (b.BASE/zipped['path']).read_bytes()
    assert len(payload) == zipped['bytes'] and b.sha(payload) == zipped['sha256']
    outputs[zipped['path']] = payload
    report = {'schema': 'clp-teacher-hosted/1', 'state': 'pass', 'course_counts': b.COUNTS,
              'interface_locales': ['id', 'en'], 'source_translation_created': False,
              'book_prose_copied': False, 'precise_target_exercise_alignment': {'B20': True, 'B30': True, 'B50': True, 'B60': True},
              'b20_navigation': {'mapping':nav_lock['mapping'],'validation':nav_lock['validation'],
                  'counts':navigation['counts'],'reader':navigation['reader'],
                  'printed_reader_links':2705,'native_states_preserved':True,
                  'scope':'source_target_structural_spans_and_pdf_start_pages_not_semantic_review'},
              'files': [{'path': p, 'bytes': len(v), 'sha256': b.sha(v)} for p, v in sorted(outputs.items())],
              'input_identity': built['input_identity'], 'public_deployment_verified': False}
    outputs['teacher-validation.json'] = b.encoded(report)
    out = b.ROOT/'docs/backend/clp'
    out.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (out/name).write_bytes(data)
    print(json.dumps({'state': 'staged', 'files': len(outputs), 'course_counts': b.COUNTS}))


if __name__ == '__main__':
    main()
