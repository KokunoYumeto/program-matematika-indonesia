"""Rebuild the corrected classical data export with explicit registry provenance.

The historical export supplies stable IDs, schemas and inherited non-source
metadata. Current Markdown and ledgers are reparsed by the unchanged native
exporter and independently checked by its native validator. The current corrected
export is forbidden as an input. This proves structural reproduction, not a new
translation, semantic review, PDF build or whole-course capability completion.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location('d100_export_common', Path(__file__).with_name('replay-d100-original-backend-v1.py'))
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
ROOT, require, fact, exact = common.ROOT, common.require, common.fact, common.exact
EXPORTER = 'export_backend_units_01_30_corr1'
VALIDATOR = 'qa_backend_units_01_30_corr1'
NAMESPACE = 'backend/units-01-30-corr1'
QA = 'qa/UNITS_01_30_CORR1_BACKEND_QA.json'
QA_SHA = '2b23e04200f16fb9c2522656f6f8ecf87799f64ecdd2c1f44825df43e899bcfc'
PINS = {
    'scripts/' + EXPORTER + '.py': '9f319be4f3112519f6bfd3b797780c820b5fbf7cfa446e0c568bca26f4fd017e',
    'scripts/' + VALIDATOR + '.py': '7239e4052317a20ac798de733dc9596762f948eb3b9c1496e3027aa3da58e1f9',
}
REGISTRY = {
    'backend/units-01-30/MANIFEST.json': '007c1d120a132b9a8b0c8c8ba9349b36d46cd472aa7ec2d217bce335dd666c0d',
    'backend/units-01-30/records.jsonl': 'dfdaebfa185c09b5e96ee4834b8b52f1c52329477eae0b48c5e8950b1b228dd7',
    'backend/units-01-30/record.schema.json': '3158825c0bd1c0da54c1c670630e7a8a2299b2b0d82e0f905042e76d7630906a',
}


class ClassicalReadOnly(common.ReadOnlyNative):
    def __init__(self, root):
        super().__init__(root, forbidden_prefixes=(NAMESPACE + '/',))

    def observe(self, event, args):
        super().observe(event, args)
        if self.enabled and not self.hashing and event == 'open':
            path = Path(args[0]).resolve()
            if path.is_relative_to(self.root):
                relative = path.relative_to(self.root).as_posix()
                require(not relative.startswith('backend/') or relative in REGISTRY,
                        'Only the exact historical registry is an allowed backend dependency')


def check_validation(manifest, validation):
    require(manifest['through_unit'] == 30 and manifest['record_count'] == 23869,
            'Classical scope drift')
    require(validation['record_count'] == validation['json_schema_validated_records'] == 23869,
            'Independent schema coverage incomplete')
    require(validation['baseline_stable_ids_preserved'] == 22752
            and validation['added_stable_id_count'] == 1117, 'Stable-ID preservation differs')
    require(validation['source_projection']['source_file_count'] == 120
            and validation['source_projection']['segment_record_count'] == 8056,
            'Independent current-source projection incomplete')
    require(validation['ledger_projection']['terminology_record_count'] == 276
            and validation['ledger_projection']['correction_record_count'] == 159,
            'Ledger coverage differs')


def generate(root):
    for path, sha in {**PINS, **REGISTRY}.items():
        require(fact(exact(root, path))['sha256'] == sha, 'Native identity drift: ' + path)
    guard = ClassicalReadOnly(root)
    sys.addaudithook(guard.observe)
    guard.enabled = True
    try:
        with common.native_modules(root, EXPORTER, VALIDATOR) as (exporter, validator):
            files, manifest = exporter.render_export()
            validation = validator.validate_rendered(files, manifest, exporter)
            check_validation(manifest, validation)
    finally:
        guard.enabled = False
    for path, expected in guard.reads.items():
        require(fact(exact(root, path)) == expected, 'Input changed during execution: ' + path)
    inputs = [{'path': p, **guard.reads[p]} for p in sorted(guard.reads)]
    require(set(p for p in guard.reads if p.startswith('backend/')) == set(REGISTRY),
            'Historical registry dependency not exactly recorded')
    require(all(guard.reads[p]['sha256'] == sha for p, sha in REGISTRY.items()),
            'Runtime registry identity changed')
    return files, manifest, validation, inputs


def scope(manifest):
    return {'source_course_units': 30, 'source_files': 120,
            'source_segments': manifest['source_projection']['segment_record_count'],
            'record_count': manifest['record_count'],
            'preserved_baseline_ids': manifest['stable_id_contract']['preserved_baseline_count'],
            'added_ids': manifest['stable_id_contract']['added_count']}


def bind(native_root):
    receipt_path = exact(native_root, QA)
    require(fact(receipt_path)['sha256'] == QA_SHA, 'Native QA witness changed')
    receipt = json.loads(receipt_path.read_bytes())
    require(receipt['status'] == 'PASS' and receipt['mode'] == 'materialized', 'Wrong native QA')
    expected = []
    for row in receipt['expected_output']:
        require(row['path'].startswith(NAMESPACE + '/'), 'Foreign output in native QA')
        require(fact(exact(native_root, row['path'])) == {k: row[k] for k in ('bytes', 'sha256')},
                'Current native output differs from QA')
        expected.append({**row, 'path': row['path'][len(NAMESPACE) + 1:]})
    require(len(expected) == 19, 'Native output inventory drift')
    files, manifest, validation, inputs = generate(native_root)
    require(common.output_facts(files) == sorted(expected, key=lambda r: r['path']),
            'Fresh export differs from exact current outputs')
    require(validation == receipt['evidence'], 'Independent QA differs from native witness')
    return {'schema': 'd100-classical-native-export-inputs/1', 'state': 'bound',
            'course_id': 'D100', 'lane': 'classical', 'locale': 'id-ID',
            'native_qa': {'path': QA, **fact(receipt_path)},
            'historical_registry': manifest['identity_registry'],
            'historical_registry_role': 'Stable IDs, schema and inherited non-source metadata; all 120 current source files independently reparsed.',
            'inputs': inputs, 'outputs': common.output_facts(files),
            'scope_counts': scope(manifest), 'record_counts': manifest['counts'],
            'validation': validation, 'historical_registry_used': True,
            'current_backend_used_as_input': False, 'producer_writes': False,
            'evidence_timing': 'retrospective_actual_runtime_read_binding',
            'new_semantic_review': False, 'whole_backend_complete': False,
            'integration_provenance': 'OpenAI Codex gpt-6-astra, Ultra'}


def replay(native_root, binding_path, output):
    binding = json.loads(binding_path.read_bytes())
    require(binding['schema'] == 'd100-classical-native-export-inputs/1'
            and binding['state'] == 'bound' and binding['native_qa']['sha256'] == QA_SHA,
            'Wrong frozen contract')
    require(output.is_relative_to((ROOT / 'work').resolve()) and not output.exists(),
            'Fresh integration work directory required')
    inputs = binding['inputs']
    require(len({r['path'] for r in inputs}) == len(inputs), 'Duplicate input identity')
    output.mkdir(parents=True)
    report = {'schema': 'd100-classical-native-export-replay/1', 'state': 'in_progress',
              'input_binding': {'path': binding_path.relative_to(ROOT).as_posix(), **fact(binding_path)},
              'runs': [], 'historical_registry_used': True,
              'current_backend_used_as_input': False, 'producer_writes': False,
              'tex_launched': False, 'network_used': False,
              'new_semantic_review': False, 'whole_backend_complete': False}
    try:
        for label in ('a', 'b'):
            stage = output / label
            stage.mkdir()
            for row in inputs:
                source, target = exact(native_root, row['path']), exact(stage, row['path'])
                expected = {k: row[k] for k in ('bytes', 'sha256')}
                require(fact(source) == expected, 'Native input drift')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
                require(fact(source) == fact(target) == expected, 'Copy identity drift')
            files, manifest, validation, observed = generate(stage)
            require(observed == inputs, 'Isolated dependency closure differs')
            require(common.output_facts(files) == binding['outputs'], 'Output identity differs')
            require(scope(manifest) == binding['scope_counts']
                    and manifest['counts'] == binding['record_counts']
                    and validation == binding['validation'], 'Independent scope or validation differs')
            generated = stage / 'isolated-export'
            generated.mkdir()
            for name, data in files.items():
                exact(generated, name).write_bytes(data)
            for row in inputs:
                require(fact(exact(stage, row['path'])) == {k: row[k] for k in ('bytes', 'sha256')},
                        'Copied input changed')
            report['runs'].append({'label': label, 'inputs': len(inputs),
                                  'outputs': common.output_facts(files), 'validation': validation})
            (output / 'REPLAY.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            print(json.dumps({'run': label, 'state': 'pass', 'records': manifest['record_count']}), flush=True)
            del files
        require(report['runs'][0]['outputs'] == report['runs'][1]['outputs'], 'Replays differ')
        report.update(state='pass', native_outputs_reproduced=True, isolated_runs=2,
                      scope_counts=binding['scope_counts'], record_counts=binding['record_counts'])
    except Exception as error:
        report.update(state='failed', failure_type=type(error).__name__,
                      reason=str(error).replace(str(native_root), '<native>').replace(str(ROOT), '<integration>'))
        raise
    finally:
        (output / 'REPLAY.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['bind', 'replay'])
    parser.add_argument('--native-root', type=Path, default=ROOT.parent / 'algebraic-geometry-bridge-id')
    parser.add_argument('--binding', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    native_root, binding_path = args.native_root.resolve(), args.binding.resolve()
    require(binding_path.is_relative_to((ROOT / 'backend/course-capsule-v1/authority').resolve()),
            'Binding must be integration authority data')
    if args.operation == 'bind':
        require(not binding_path.exists(), 'Preserve frozen binding')
        result = bind(native_root)
        binding_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'state': result['state'], 'inputs': len(result['inputs']),
                          'outputs': len(result['outputs']), 'records': result['scope_counts']['record_count']}))
    else:
        require(args.output is not None, 'Replay output required')
        result = replay(native_root, binding_path, args.output.resolve())
        print(json.dumps({'state': result['state'], 'runs': result['isolated_runs'],
                          'records': result['scope_counts']['record_count']}))
