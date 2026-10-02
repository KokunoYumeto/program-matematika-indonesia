"""Admit companion export evidence only after rehashing actual isolated files."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('native_export_replay', Path(__file__).with_name('replay-d100-original-backend-v1.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def bind(directory):
    directory = directory.resolve()
    m.require(directory.is_relative_to((ROOT / 'work').resolve()), 'Integration replay only')
    raw = (directory / 'REPLAY.json').read_bytes()
    report = json.loads(raw)
    m.require(report['state'] == 'pass' and report['isolated_runs'] == 2
              and report['native_outputs_reproduced'] is True, 'Missing two successful isolated runs')
    for key in ('producer_writes', 'existing_backend_used_as_input', 'tex_launched',
                'network_used', 'new_semantic_review', 'whole_backend_complete'):
        m.require(report[key] is False, 'Unsupported claim: ' + key)
    binding_path = m.exact(ROOT, report['input_binding']['path'])
    m.require(m.fact(binding_path) == {k: report['input_binding'][k] for k in ('bytes', 'sha256')},
              'Frozen dependency contract changed')
    binding = json.loads(binding_path.read_bytes())
    m.require(len(binding['inputs']) == 213 and len(binding['outputs']) == 23
              and sum(binding['record_counts'].values()) == 1064, 'Companion scope changed')
    m.require([r['label'] for r in report['runs']] == ['a', 'b'], 'Distinct runs required')
    for run in report['runs']:
        m.require(run['inputs'] == 213 and run['outputs'] == binding['outputs'], 'Run scope changed')
        for item in binding['inputs']:
            m.require(m.fact(m.exact(directory / run['label'], item['path'])) ==
                      {k: item[k] for k in ('bytes', 'sha256')}, 'Isolated input differs')
        for item in run['outputs']:
            m.require(m.fact(m.exact(directory / run['label'] / 'isolated-export', item['path'])) ==
                      {k: item[k] for k in ('bytes', 'sha256')}, 'Actual output differs from evidence')
    m.require(b'Users/' not in raw and b'Users\\' not in raw, 'Private path in public evidence')
    destination = ROOT / 'backend/course-capsule-v1/adapters/d100-native-production-v1/original-backend-replay.json'
    m.require(not destination.exists() or destination.read_bytes() == raw, 'Preserve different admitted evidence')
    if not destination.exists():
        destination.write_bytes(raw)
    return {'state': 'pass', 'actual_outputs_rehashed': 46, 'actual_inputs_rehashed': 426,
            'proof': m.fact(destination), 'binding': m.fact(binding_path), 'native_parity_promoted': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(bind(args.replay)))
