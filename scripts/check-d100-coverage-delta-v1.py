"""Integrate D100 HTML proof and verify exact preservation of the other 39 roles."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'backend/course-capsule-v1/generated/program-backend-coverage-v1.json'


if __name__ == '__main__':
    before_bytes = PATH.read_bytes()
    before = json.loads(before_bytes)
    subprocess.run(['node', 'scripts/build-program-backend-coverage-v1.mjs'], cwd=ROOT, check=True, timeout=120)
    after_bytes = PATH.read_bytes()
    after = json.loads(after_bytes)
    assert len(before['roles']) == len(after['roles']) == 40
    old = {row['role_id']: row for row in before['roles']}
    new = {row['role_id']: row for row in after['roles']}
    assert old.keys() == new.keys()
    for key in old:
        if key != 'D100':
            assert old[key] == new[key], 'Unrelated role changed: ' + key
    assert before['summary'] == after['summary'], 'Partial HTML proof changed overall completion counts'
    for key in ('native_capability_parity_completion', 'whole_course_backend_completion', 'common_exchange_layer_completion'):
        assert old['D100'][key] == new['D100'][key], 'Unsupported D100 completion promotion'
    assert new['D100']['native_html_replay']['isolated_builds'] == 6
    for lane in ('build', 'replay'):
        assert old['D100']['dimensions']['reproducible_production'][lane] == new['D100']['dimensions']['reproducible_production'][lane]
    receipt = {'schema': 'd100-html-coverage-delta/1', 'state': 'pass', 'roles': 40,
        'other_roles_preserved': 39, 'summary_unchanged': True, 'native_parity_promoted': False,
        'six_native_html_builds_integrated': True,
        'before_sha256': hashlib.sha256(before_bytes).hexdigest(),
        'after_sha256': hashlib.sha256(after_bytes).hexdigest()}
    output = ROOT / 'outputs/d100-native-production-104269173/coverage-delta.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        assert json.loads(output.read_bytes()) == receipt, 'Preserve earlier different delta receipt'
    else:
        output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt))
