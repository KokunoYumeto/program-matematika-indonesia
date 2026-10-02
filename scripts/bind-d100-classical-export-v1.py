"""Admit classical replay only after rehashing both actual isolated trees."""
import argparse
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('classical_replay', Path(__file__).with_name('replay-d100-classical-backend-v1.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def admit(directory):
    directory = directory.resolve()
    m.require(directory.is_relative_to((m.ROOT / 'work').resolve()), 'Integration replay required')
    raw = (directory / 'REPLAY.json').read_bytes()
    proof = json.loads(raw)
    m.require(proof['schema'] == 'd100-classical-native-export-replay/1'
              and proof['state'] == 'pass' and proof['isolated_runs'] == 2
              and proof['native_outputs_reproduced'] is True, 'Missing isolated proof')
    m.require(proof['historical_registry_used'] is True, 'Registry dependency must be disclosed')
    for key in ('current_backend_used_as_input', 'producer_writes', 'tex_launched',
                'network_used', 'new_semantic_review', 'whole_backend_complete'):
        m.require(proof[key] is False, 'Unsupported claim: ' + key)
    binding_path = m.exact(m.ROOT, proof['input_binding']['path'])
    m.require(m.fact(binding_path) == {k: proof['input_binding'][k] for k in ('bytes', 'sha256')},
              'Frozen binding differs')
    binding = json.loads(binding_path.read_bytes())
    m.require(m.fact(binding_path)['sha256'] == '6d3811b7138aeff8cdeaafcd9dbc5246988dead5f52a200dd44004f20d7938a4',
              'Wrong bound native source')
    m.require(len(binding['inputs']) == 129 and len(binding['outputs']) == 19,
              'Classical dependency/output scope differs')
    m.require(proof['scope_counts'] == binding['scope_counts']
              and proof['record_counts'] == binding['record_counts'], 'Scope differs')
    m.require([r['label'] for r in proof['runs']] == ['a', 'b'], 'Distinct runs required')
    for run in proof['runs']:
        m.require(run['inputs'] == 129 and run['outputs'] == binding['outputs']
                  and run['validation'] == binding['validation'], 'Run differs from native evidence')
        for row in binding['inputs']:
            m.require(m.fact(m.exact(directory / run['label'], row['path'])) ==
                      {k: row[k] for k in ('bytes', 'sha256')}, 'Copied input changed')
        for row in run['outputs']:
            m.require(m.fact(m.exact(directory / run['label'] / 'isolated-export', row['path'])) ==
                      {k: row[k] for k in ('bytes', 'sha256')}, 'Actual output changed')
    m.require(b'Users/' not in raw and b'Users\\' not in raw, 'Private path in public proof')
    target = m.ROOT / 'backend/course-capsule-v1/adapters/d100-native-production-v1/classical-backend-replay.json'
    m.require(not target.exists() or target.read_bytes() == raw, 'Preserve different admitted evidence')
    if not target.exists():
        target.write_bytes(raw)
    return {'state': 'pass', 'actual_inputs_rehashed': 258, 'actual_outputs_rehashed': 38,
            'proof': m.fact(target), 'binding': m.fact(binding_path), 'native_parity_promoted': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay', type=Path, required=True)
    print(json.dumps(admit(parser.parse_args().replay)))
