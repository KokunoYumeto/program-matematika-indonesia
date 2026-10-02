"""Reproduce BGK data with historical-registry and existing-reader dependencies.

Current corrected backend outputs are forbidden inputs. The native independent
validator checks the complete historical export inventory, not just its three
core files. Existing reader/QA bytes are dependencies, not freshly rebuilt PDFs
or new semantic review. Producer source remains read-only.
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
EXPORTER = 'export_backend_bgk_units_01_30_corr1'
VALIDATOR = 'qa_backend_bgk_units_01_30_corr1'
BASE = 'backend/bgk-units-01-30'
NAMESPACE = 'backend/bgk-units-01-30-corr1'
QA = 'qa/BGK_UNITS_01_30_CORR1_BACKEND_QA.json'
QA_SHA = '0c7468e59087a77342b7dbef98c8bb5dc9f29691cc2c708000693324c686a61e'
PINS = {
    'scripts/' + EXPORTER + '.py': '1f2926cf73ccef922f3389edcfff63e29e4a96dc7d38a3719f04de80e3bfb297',
    'scripts/' + VALIDATOR + '.py': '89429b97e1c7202fbc755300a6a59fed5c3a32c3cd0acbbddfeb7b487345edfe',
    BASE + '/MANIFEST.json': 'a01c84343e69f9ad262d73d0614d6df5b8a02c5ce3eca74eb18a796e8e00a3bc',
    BASE + '/records.jsonl': '9fc848bcac695dd3293fe9296a5f59d19d3c428a0c8eb52f1a6106d5b2a8ae66',
    BASE + '/record.schema.json': '519c7dd00f944b513323de3bbc78da45191228b90a1536775cb9b0f9352a6b3d',
}


def historical_registry(root):
    for path, sha in PINS.items():
        require(fact(exact(root, path))['sha256'] == sha, 'Native identity drift: ' + path)
    manifest = json.loads(exact(root, BASE + '/MANIFEST.json').read_bytes())
    result = {BASE + '/MANIFEST.json': fact(exact(root, BASE + '/MANIFEST.json'))}
    for row in manifest['files']:
        path = row['path']
        require(path.startswith(BASE + '/') and Path(path).parent.as_posix() == BASE
                and path not in result, 'Historical inventory boundary or duplicate')
        expected = {k: row[k] for k in ('bytes', 'sha256')}
        require(fact(exact(root, path)) == expected, 'Historical inventory bytes differ')
        result[path] = expected
    require(len(result) == 19, 'Historical inventory scope differs')
    return result


class BgkReadOnly(common.ReadOnlyNative):
    def __init__(self, root, registry):
        super().__init__(root, forbidden_prefixes=(NAMESPACE + '/',))
        self.registry = registry

    def observe(self, event, args):
        super().observe(event, args)
        if self.enabled and not self.hashing and event == 'open':
            path = Path(args[0]).resolve()
            if path.is_relative_to(self.root):
                relative = path.relative_to(self.root).as_posix()
                require(not relative.startswith('backend/') or relative in self.registry,
                        'Only the exact historical BGK inventory is an allowed backend input')


def check_validation(manifest, validation):
    require(manifest['through_unit'] == 30 and manifest['record_count'] == 21690,
            'BGK course scope differs')
    require(validation['record_count'] == validation['schema_validated_records'] == 21690,
            'Independent schema coverage incomplete')
    require(manifest['historical_baseline']['record_count'] == 21686
            and len(manifest['historical_baseline']['additive_stable_ids']) == 4,
            'Historical stable-ID scope differs')
    require(validation['source_projection']['record_backed_source_file_count'] == 99
            and validation['source_projection']['current_source_file_count'] == 90,
            'Independent source projection incomplete')
    require(validation['counts']['segment'] == 7506 and validation['counts']['exercise'] == 495
            and validation['counts']['solution'] == 25, 'Source/solution scope differs')
    require(manifest['reader_binding']['ready'] is True
            and manifest['validation']['current_source_closure_and_unit_07_two_hop_exact'] is True
            and manifest['validation']['current_reader_and_reader_qa_exact'] is True,
            'Strict current-source/reader validation missing')


def generate(root):
    registry = historical_registry(root)
    guard = BgkReadOnly(root, registry)
    sys.addaudithook(guard.observe)
    guard.enabled = True
    try:
        with common.native_modules(root, EXPORTER, VALIDATOR) as (exporter, validator):
            raw, manifest = exporter.build_export(require_reader=True)
            validation = validator.validate_payload(raw, root, exporter_manifest=manifest,
                                                    require_full_gates=True)
            check_validation(manifest, validation)
            witness = validator.build_receipt(validation, root)
            files = validator.normalize_payload(raw)
    finally:
        guard.enabled = False
    for path, expected in guard.reads.items():
        require(fact(exact(root, path)) == expected, 'Input changed during execution: ' + path)
    require({p: v for p, v in guard.reads.items() if p.startswith('backend/')} == registry,
            'Historical inventory not completely and exactly recorded')
    inputs = [{'path': p, **guard.reads[p]} for p in sorted(guard.reads)]
    return files, manifest, validation, inputs, witness


def scope(manifest):
    return {'source_course_units': 30, 'source_files': 99, 'current_source_closure_files': 90,
            'source_segments': 7506, 'record_count': manifest['record_count'],
            'preserved_baseline_ids': 21686, 'added_ids': 4,
            'exercises': 495, 'public_solutions': 25,
            'historical_registry_files': 19, 'existing_reader_bytes_used': True}


def bind(native_root):
    receipt_path = exact(native_root, QA)
    require(fact(receipt_path)['sha256'] == QA_SHA, 'Native QA witness changed')
    receipt = json.loads(receipt_path.read_bytes())
    require(receipt['status'] == 'PASS' and receipt['namespace'] == NAMESPACE, 'Wrong native QA')
    expected = []
    for row in receipt['backend']['files']:
        require(row['path'].startswith(NAMESPACE + '/'), 'Foreign current output in native QA')
        require(fact(exact(native_root, row['path'])) == {k: row[k] for k in ('bytes', 'sha256')},
                'Current native output differs from QA')
        expected.append({**row, 'path': row['path'][len(NAMESPACE) + 1:]})
    require(len(expected) == 19, 'Current output inventory differs')
    files, manifest, validation, inputs, witness = generate(native_root)
    require(common.output_facts(files) == sorted(expected, key=lambda r: r['path']),
            'Fresh export differs from current native outputs')
    require(witness == receipt, 'Fresh independent QA differs from frozen native witness')
    return {'schema': 'd100-bgk-native-export-inputs/1', 'state': 'bound',
            'course_id': 'D100', 'lane': 'bgk', 'locale': 'id-ID',
            'native_qa': {'path': QA, **fact(receipt_path)},
            'historical_registry': manifest['historical_baseline'],
            'historical_registry_role': 'Stable IDs, schema, inherited non-source metadata and all historical class projections; 99 current Markdown files independently reparsed.',
            'inputs': inputs, 'outputs': common.output_facts(files),
            'scope_counts': scope(manifest), 'record_counts': manifest['counts'],
            'validation': validation, 'historical_registry_used': True,
            'existing_reader_bytes_used': True, 'fresh_pdf_build': False,
            'current_backend_used_as_input': False, 'producer_writes': False,
            'evidence_timing': 'retrospective_actual_runtime_read_binding',
            'new_semantic_review': False, 'whole_backend_complete': False,
            'integration_provenance': 'OpenAI Codex gpt-6-astra, Ultra'}


def replay(native_root, binding_path, output):
    binding = json.loads(binding_path.read_bytes())
    require(binding['schema'] == 'd100-bgk-native-export-inputs/1'
            and binding['state'] == 'bound' and binding['native_qa']['sha256'] == QA_SHA,
            'Wrong frozen contract')
    require(output.is_relative_to((ROOT / 'work').resolve()) and not output.exists(),
            'Fresh integration work directory required')
    inputs = binding['inputs']
    require(len({r['path'] for r in inputs}) == len(inputs), 'Duplicate input identity')
    output.mkdir(parents=True)
    report = {'schema': 'd100-bgk-native-export-replay/1', 'state': 'in_progress',
              'input_binding': {'path': binding_path.relative_to(ROOT).as_posix(), **fact(binding_path)},
              'runs': [], 'historical_registry_used': True, 'existing_reader_bytes_used': True,
              'fresh_pdf_build': False, 'current_backend_used_as_input': False,
              'producer_writes': False, 'tex_launched': False, 'network_used': False,
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
            files, manifest, validation, observed, _witness = generate(stage)
            require(observed == inputs, 'Isolated dependency closure differs')
            require(common.output_facts(files) == binding['outputs'], 'Output identity differs')
            require(scope(manifest) == binding['scope_counts']
                    and manifest['counts'] == binding['record_counts']
                    and validation == binding['validation'], 'Independent scope/validation differs')
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
