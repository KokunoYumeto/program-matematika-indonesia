"""Bind and reproduce the D100 companion data export without producer writes.

Discovery records actual read-only source dependencies. Replay uses two fresh
isolated trees containing only those inputs; existing export bytes are never
available to the native exporter. This is structural replay, not semantic review.
"""
import argparse
from contextlib import contextmanager
import hashlib
import importlib
import json
import os
from pathlib import Path
import site
import sys

import yaml  # Load runtime libraries before restricting native execution.
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
EXPORTER = 'export_backend_original_bridge_corr1'
VALIDATOR = 'qa_backend_original_bridge_corr1'
NAMESPACE = 'backend/original-bridge-corr1'
QA = 'qa/ORIGINAL_BRIDGE_CORR1_BACKEND_QA.json'
QA_SHA = 'fcf117014cd3a1b3c8e5f08ea0a545211964c1c37ad01b164250e06dd85ff69e'
PINS = {
    'scripts/' + EXPORTER + '.py': '64e2411d39768c5c00ba5786ce9e281a7ff5bc2d8fdf946203b9115516d5f1a2',
    'scripts/' + VALIDATOR + '.py': '59a4f89fef9cb929100705373d208ad7034e772c193d439a8332f4d79dc5a059',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fact(path):
    digest, count = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
            count += len(chunk)
    return {'bytes': count, 'sha256': digest.hexdigest()}


def exact(root, relative):
    require(isinstance(relative, str) and relative and '\\' not in relative
            and ':' not in relative and not Path(relative).is_absolute()
            and '..' not in Path(relative).parts, 'Unsafe relative path')
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), 'Path escapes exact root')
    return path


class ReadOnlyNative:
    def __init__(self, root):
        self.root = root.resolve()
        self.enabled = False
        self.hashing = False
        self.reads = {}
        self.runtime_roots = [Path(sys.base_prefix).resolve(), Path(sys.prefix).resolve()]
        self.runtime_roots += [Path(p).resolve() for p in site.getsitepackages()]
        self.runtime_roots.append(Path(site.getusersitepackages()).resolve())

    def observe(self, event, args):
        if not self.enabled:
            return
        if event.startswith(('subprocess.', 'socket.', 'os.remove', 'os.rename',
                             'os.mkdir', 'os.rmdir', 'os.link', 'os.symlink',
                             'os.truncate', 'os.chmod', 'os.utime', 'os.system')):
            raise ValueError('Native replay forbids processes, network and mutations')
        if event != 'open' or self.hashing:
            return
        mode, flags = args[1], args[2]
        require(not (isinstance(mode, str) and any(c in mode for c in 'wax+'))
                and not (isinstance(flags, int) and flags &
                         (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)),
                'Native replay forbids writes')
        require(isinstance(args[0], (str, bytes, os.PathLike)), 'Unbound native file descriptor')
        path = Path(os.fsdecode(args[0])).resolve()
        if path.is_relative_to(self.root):
            relative = path.relative_to(self.root).as_posix()
            require(not relative.startswith(('backend/original-bridge/', NAMESPACE + '/')),
                    'Existing original backend output cannot be a replay input')
            if path.suffix == '.pyc':
                raise FileNotFoundError('Exact native source required, not cached bytecode')
            if path.is_file() and relative not in self.reads:
                self.hashing = True
                try:
                    self.reads[relative] = fact(path)
                finally:
                    self.hashing = False
        else:
            require(any(path.is_relative_to(p) for p in self.runtime_roots),
                    'Native read escaped isolated inputs and Python runtime')


@contextmanager
def native_modules(root):
    old_path, old_modules = list(sys.path), dict(sys.modules)
    names = {p.stem for p in (root / 'scripts').glob('*.py')}
    for name in names:
        sys.modules.pop(name, None)
    sys.path.insert(0, str(root / 'scripts'))
    try:
        exporter, validator = importlib.import_module(EXPORTER), importlib.import_module(VALIDATOR)
        require(exporter.ROOT.resolve() == validator.ROOT.resolve() == root.resolve(),
                'Native exporter/validator not isolated')
        yield exporter, validator
    finally:
        sys.path[:] = old_path
        for name in names:
            sys.modules.pop(name, None)
            if name in old_modules:
                sys.modules[name] = old_modules[name]


def generate(root):
    for path, sha in PINS.items():
        require(fact(exact(root, path))['sha256'] == sha, 'Native tool identity drift')
    guard = ReadOnlyNative(root)
    sys.addaudithook(guard.observe)
    guard.enabled = True
    try:
        with native_modules(root) as (exporter, validator):
            files, manifest = exporter.build_export(root)
            validation = validator.validate_payload(files, root)
            require(validation['status'] == 'PASS', 'Independent native QA failed')
    finally:
        guard.enabled = False
    for path, expected in guard.reads.items():
        require(fact(exact(root, path)) == expected, 'Input changed during native execution: ' + path)
    return files, manifest, validation, [{'path': p, **guard.reads[p]} for p in sorted(guard.reads)]


def output_facts(files):
    return [{'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
            for name, data in sorted(files.items())]


def bind(native_root):
    receipt_path = exact(native_root, QA)
    require(fact(receipt_path)['sha256'] == QA_SHA, 'Native QA witness changed')
    receipt = json.loads(receipt_path.read_bytes())
    require(receipt['status'] == 'PASS', 'Native QA witness failed')
    expected = []
    for row in receipt['backend_files']:
        require(row['path'].startswith(NAMESPACE + '/'), 'Foreign output in native receipt')
        require(fact(exact(native_root, row['path'])) == {k: row[k] for k in ('bytes', 'sha256')},
                'Existing native output differs from witness')
        expected.append({**row, 'path': row['path'][len(NAMESPACE) + 1:]})
    files, manifest, validation, inputs = generate(native_root)
    require(output_facts(files) == sorted(expected, key=lambda r: r['path']),
            'Fresh native export differs from existing exact outputs')
    return {'schema': 'd100-original-native-export-inputs/1', 'state': 'bound',
            'course_id': 'D100', 'lane': 'original', 'locale': 'id-ID',
            'native_qa': {'path': QA, **fact(receipt_path)}, 'inputs': inputs,
            'outputs': output_facts(files), 'scope_counts': manifest['scope_counts'],
            'record_counts': manifest['counts'], 'validation': validation,
            'evidence_timing': 'retrospective_actual_runtime_read_binding',
            'producer_writes': False, 'existing_backend_used_as_input': False,
            'new_semantic_review': False, 'whole_backend_complete': False,
            'integration_provenance': 'OpenAI Codex gpt-6-astra, Ultra'}


def replay(native_root, binding_path, output):
    binding = json.loads(binding_path.read_bytes())
    require(binding['schema'] == 'd100-original-native-export-inputs/1'
            and binding['state'] == 'bound' and binding['native_qa']['sha256'] == QA_SHA,
            'Wrong frozen input contract')
    require(output.is_relative_to((ROOT / 'work').resolve()) and not output.exists(),
            'Fresh output below integration work required')
    inputs = binding['inputs']
    require(len({r['path'] for r in inputs}) == len(inputs), 'Duplicate input identity')
    output.mkdir(parents=True)
    report = {'schema': 'd100-original-native-export-replay/1', 'state': 'in_progress',
              'input_binding': {'path': binding_path.relative_to(ROOT).as_posix(), **fact(binding_path)},
              'runs': [], 'producer_writes': False, 'existing_backend_used_as_input': False,
              'tex_launched': False, 'network_used': False, 'new_semantic_review': False,
              'whole_backend_complete': False}
    try:
        for label in ('a', 'b'):
            stage = output / label
            stage.mkdir()
            for row in inputs:
                source, target = exact(native_root, row['path']), exact(stage, row['path'])
                require(fact(source) == {k: row[k] for k in ('bytes', 'sha256')}, 'Native input drift')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
                require(fact(source) == fact(target) == {k: row[k] for k in ('bytes', 'sha256')},
                        'Copy or source identity drift')
            files, manifest, validation, observed = generate(stage)
            require(observed == inputs, 'Isolated dependency closure differs from binding')
            require(output_facts(files) == binding['outputs'], 'Rebuilt output bytes differ')
            require(manifest['scope_counts'] == binding['scope_counts']
                    and manifest['counts'] == binding['record_counts'], 'Native scope differs')
            generated = stage / 'isolated-export'
            generated.mkdir()
            for name, data in files.items():
                exact(generated, name).write_bytes(data)
            for row in inputs:
                require(fact(exact(stage, row['path'])) == {k: row[k] for k in ('bytes', 'sha256')},
                        'Copied input changed')
            report['runs'].append({'label': label, 'inputs': len(inputs),
                                  'outputs': output_facts(files), 'validation': validation})
            (output / 'REPLAY.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        require(report['runs'][0]['outputs'] == report['runs'][1]['outputs'], 'Two runs differ')
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
        require(not binding_path.exists(), 'Preserve existing frozen binding')
        result = bind(native_root)
        binding_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'state': result['state'], 'inputs': len(result['inputs']),
                          'outputs': len(result['outputs']), 'records': sum(result['record_counts'].values())}))
    else:
        require(args.output is not None, 'Replay output required')
        result = replay(native_root, binding_path, args.output.resolve())
        print(json.dumps({'state': result['state'], 'runs': result['isolated_runs'],
                          'records': sum(result['record_counts'].values())}))
