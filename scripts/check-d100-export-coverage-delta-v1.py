"""Integrate companion-export evidence without changing other roles or completion."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'backend/course-capsule-v1/generated/program-backend-coverage-v1.json'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    output = args.receipt.resolve()
    assert output.is_relative_to((ROOT / 'outputs').resolve()) and not output.exists()
    before_bytes = MODEL.read_bytes()
    before = json.loads(before_bytes)
    subprocess.run(['node', 'scripts/build-program-backend-coverage-v1.mjs'], cwd=ROOT,
                   check=True, timeout=120)
    after_bytes = MODEL.read_bytes()
    after = json.loads(after_bytes)
    old = {r['role_id']: r for r in before['roles']}
    new = {r['role_id']: r for r in after['roles']}
    assert len(old) == len(new) == 40 and old.keys() == new.keys()
    assert before['summary'] == after['summary']
    for key in old:
        if key != 'D100':
            assert old[key] == new[key], 'Unrelated role changed: ' + key
    for key in ('native_capability_parity_completion', 'whole_course_backend_completion', 'common_exchange_layer_completion'):
        assert old['D100'][key] == new['D100'][key]
    assert old['D100']['native_html_replay'] == new['D100']['native_html_replay']
    for key in ('build', 'replay', 'native_data_export_replay', 'fresh_pdf_replay'):
        assert old['D100']['dimensions']['reproducible_production'][key] == new['D100']['dimensions']['reproducible_production'][key]
    proof = new['D100']['native_original_data_replay']
    assert proof['state'] == 'pass' and proof['isolated_runs'] == 2
    assert sum(proof['record_counts'].values()) == 1064
    report = {'schema': 'd100-companion-export-coverage-delta/1', 'state': 'pass',
              'roles': 40, 'other_roles_preserved': 39, 'summary_unchanged': True,
              'native_parity_promoted': False, 'companion_records_reproduced': 1064,
              'before_sha256': hashlib.sha256(before_bytes).hexdigest(),
              'after_sha256': hashlib.sha256(after_bytes).hexdigest()}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))
