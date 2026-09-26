"""Finite shared-site projection/validation after tested D110 admission."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d110-surface-v1'
STEPS = [
    ['node', 'scripts/build-multilingual-interface.mjs'],
    [sys.executable, '-B', 'scripts/apply-central-course-surface-navigation-v1.py'],
    ['node', 'scripts/finalize-multilingual-interface-receipt-v1.mjs'],
    ['node', 'scripts/refresh-course-capsule-hosted-page-identities-v1.mjs'],
    ['node', 'scripts/test-course-capsule-ui-v1.mjs'],
    ['node', 'scripts/test-course-capsule-educator-truth-v1.mjs'],
    ['node', 'scripts/build-static-course-fallback.mjs'],
    ['node', 'scripts/export-single-file-site.mjs', 'docs/peta-belajar-luring.html'],
    [sys.executable, '-B', 'scripts/apply-central-course-surface-navigation-v1.py'],
    ['node', 'scripts/finalize-multilingual-interface-receipt-v1.mjs'],
    ['node', 'scripts/refresh-course-capsule-hosted-page-identities-v1.mjs'],
    ['node', 'scripts/test-multilingual-interface.mjs'],
    ['node', 'scripts/validate-universal-reader-navigation-rollout-v1.mjs'],
    [sys.executable, '-B', 'scripts/validate-central-reader-navigation-v1.py'],
    ['node', 'scripts/sync-sites-public.mjs'],
    ['node', 'scripts/validate-course-capsule-site-v1.mjs', '--public'],
    ['node', 'scripts/validate-static-site.mjs'],
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=0)
    args = parser.parse_args()
    assert 0 <= args.start < len(STEPS)
    report = {'schema': 'd110-combined-integration/1', 'start_step': args.start, 'steps': [], 'state': 'running'}
    report_path = BASE / 'integration-tests.json'
    log = BASE / ('integration-build-' + str(args.start) + '.log')
    with log.open('w', encoding='utf-8') as stream:
        for i in range(args.start, len(STEPS)):
            command = STEPS[i]
            stream.write('\nSTEP ' + str(i) + ' ' + ' '.join(command) + '\n')
            stream.flush()
            result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=600)
            report['steps'].append({'index': i, 'script': command[-1], 'exit_code': result.returncode})
            report['state'] = 'running' if result.returncode == 0 else 'failed'
            report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            print(json.dumps({'step': i, 'command': command[1:], 'exit_code': result.returncode}), flush=True)
            if result.returncode:
                return result.returncode
    report['state'] = 'pass'
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
