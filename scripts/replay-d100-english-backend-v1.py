"""Rebuild a published D100 English backend in isolated, read-only input trees.

No translation, mathematical review, TeX, network or producer mutation occurs.
The upstream review claim is reproduced as historical metadata, not endorsed.
"""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

import yaml
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
EXPORTER = 'scripts/english/export_backend_en.py'
QA = 'qa/english/TRANSLATION_INTEGRATION_QA.json'
LIMIT = 2 * 1024 ** 3


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def file_fact(path):
    h, size = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
            size += len(block)
    return {'bytes': size, 'sha256': h.hexdigest()}


def exact(root, relative):
    require(isinstance(relative, str) and relative and '\\' not in relative
            and ':' not in relative and not Path(relative).is_absolute()
            and '..' not in Path(relative).parts, 'Unsafe relative input path')
    result = (root / relative).resolve()
    require(result.is_relative_to(root.resolve()), 'Input escaped its root')
    return result


def memory_cap():
    """Hard Windows job commit limit for this process; native execution has no children."""
    require(os.name == 'nt', 'This replay requires the tested Windows memory guard')
    class Basic(ctypes.Structure):
        _fields_ = [('PerProcessUserTimeLimit', ctypes.c_int64),
                    ('PerJobUserTimeLimit', ctypes.c_int64), ('LimitFlags', wintypes.DWORD),
                    ('MinimumWorkingSetSize', ctypes.c_size_t), ('MaximumWorkingSetSize', ctypes.c_size_t),
                    ('ActiveProcessLimit', wintypes.DWORD), ('Affinity', ctypes.c_size_t),
                    ('PriorityClass', wintypes.DWORD), ('SchedulingClass', wintypes.DWORD)]
    class IO(ctypes.Structure):
        _fields_ = [(n, ctypes.c_uint64) for n in ('ReadOperationCount', 'WriteOperationCount',
                    'OtherOperationCount', 'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]
    class Extended(ctypes.Structure):
        _fields_ = [('BasicLimitInformation', Basic), ('IoInfo', IO),
                    ('ProcessMemoryLimit', ctypes.c_size_t), ('JobMemoryLimit', ctypes.c_size_t),
                    ('PeakProcessMemoryUsed', ctypes.c_size_t), ('PeakJobMemoryUsed', ctypes.c_size_t)]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p]
    handle = kernel.CreateJobObjectW(None, None)
    require(bool(handle), 'Could not create replay memory guard')
    info = Extended()
    info.BasicLimitInformation.LimitFlags = 0x100 | 0x8  # PROCESS_MEMORY and ACTIVE_PROCESS
    info.BasicLimitInformation.ActiveProcessLimit = 1
    info.ProcessMemoryLimit = LIMIT
    require(bool(kernel.SetInformationJobObject(handle, 9, ctypes.byref(info), ctypes.sizeof(info))), 'Could not set hard replay memory limit')
    require(bool(kernel.AssignProcessToJobObject(handle, kernel.GetCurrentProcess())), 'Could not attach hard memory guard')
    def peak():
        observed = Extended()
        require(bool(kernel.QueryInformationJobObject(handle, 9, ctypes.byref(observed), ctypes.sizeof(observed), None)), 'Memory peak unavailable')
        return observed.PeakProcessMemoryUsed
    return peak


def load_local_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sealed_inputs(native, lane):
    evidence = json.loads((ROOT / 'backend/course-capsule-v1/adapters/d100-capability-v1/data/public-evidence.json').read_bytes())
    assets = {r['name']: r for r in evidence['release_assets']}
    archives = {}
    for name in ('07_English-Edition_source.zip', '08_English-Edition_native-backend.zip'):
        row = assets[name]
        path = exact(native, 'release/english/en-v1.0.0/' + name)
        require(file_fact(path) == {k: row[k] for k in ('bytes', 'sha256')}, 'Published archive identity drift: ' + name)
        archives[name] = path
    with zipfile.ZipFile(archives['08_English-Edition_native-backend.zip']) as archive:
        prefix = 'english-backend/' + lane + '/'
        expected_manifest_bytes = archive.read(prefix + 'MANIFEST.json')
        manifest = json.loads(expected_manifest_bytes)
        for name in ('records.jsonl', 'record.schema.json'):
            expected = next(r for r in manifest['files'] if r['path'] == name)
            require(digest(archive.read(prefix + name)) == {k: expected[k] for k in ('bytes', 'sha256')}, 'Native archive internal identity mismatch')
    require(manifest['lane'] == lane and manifest['language'] == 'en', 'Wrong English lane')
    config_path = 'backend/english/inputs/' + lane + '.json'
    config_data = exact(native, config_path).read_bytes()
    config = json.loads(config_data)
    canonical = json.dumps(config, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
    require(hashlib.sha256(canonical).hexdigest() == manifest['input_sha256'], 'Config differs from published manifest')
    qa_data = exact(native, QA).read_bytes()
    require(digest(qa_data) == {k: manifest['translation_integration_qa'][k] for k in ('bytes', 'sha256')}, 'Historical QA witness drift')
    qa = json.loads(qa_data)
    require(len(qa['facts']['current_sources']) == 274, 'English source closure changed')
    with zipfile.ZipFile(archives['07_English-Edition_source.zip']) as archive:
        names = set(archive.namelist())
        require(len(names) == len(archive.namelist()), 'Duplicate source ZIP member')
        for row in qa['facts']['current_sources']:
            data = archive.read('english-source-control-rights/' + row['path'])
            require(digest(data) == {k: row[k] for k in ('bytes', 'sha256')}, 'Published English source differs: ' + row['path'])
    rows = [*manifest['implementation_inputs'], *manifest['native_inputs'],
            *qa['facts']['current_sources'], {'path': QA, **digest(qa_data)},
            {'path': config_path, **digest(config_data)}]
    for row in config.get('supplemental_sources', []):
        rows.append({'path': row['native_path'], 'bytes': row['native_bytes'], 'sha256': row['native_sha256']})
    unique = {}
    for row in rows:
        key = row['path']
        fact = {k: row[k] for k in ('bytes', 'sha256')}
        require(key not in unique or unique[key] == fact, 'Conflicting input identities')
        require(file_fact(exact(native, key)) == fact, 'Declared native input drift: ' + key)
        unique[key] = fact
    expected = {r['path']: {k: r[k] for k in ('bytes', 'sha256')} for r in manifest['files']}
    expected['MANIFEST.json'] = digest(expected_manifest_bytes)
    return unique, expected, manifest, {name: {k: assets[name][k] for k in ('bytes', 'sha256', 'url')} for name in archives}


def replay(native, stage, lane, inputs, expected, suffix):
    require(not stage.exists(), 'Replay stage already exists')
    stage.mkdir(parents=True)
    for name, fact in inputs.items():
        source, target = exact(native, name), exact(stage, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        require(file_fact(source) == fact, 'Producer changed during intake')
        shutil.copyfile(source, target)
        require(file_fact(target) == fact, 'Copy identity drift')
    guard_module = load_local_module(ROOT / 'scripts/replay-d100-original-backend-v1.py', 'd100_english_guard_' + suffix)
    guard = guard_module.ReadOnlyNative(stage, forbidden_prefixes=('backend/english/release-', 'backend/english/final/'))
    sys.addaudithook(guard.observe)
    guard.enabled = True
    try:
        exporter = load_local_module(stage / EXPORTER, 'd100_native_english_' + suffix)
        require(exporter.ROOT.resolve() == stage, 'Exporter root escaped isolation')
        config = json.loads((stage / ('backend/english/inputs/' + lane + '.json')).read_bytes())
        files, manifest = exporter.run(config, root=stage, finalize=True)
    finally:
        guard.enabled = False
    actual = {name: digest(data) for name, data in sorted(files.items())}
    require(actual == expected, 'Rebuilt English output differs from public witness')
    require(set(guard.reads) <= set(inputs), 'Undeclared runtime dependency')
    for name, fact in inputs.items():
        require(file_fact(exact(stage, name)) == fact and file_fact(exact(native, name)) == fact, 'Input changed during replay')
    return {'output_files': actual, 'runtime_reads': [{'path': p, **f} for p, f in sorted(guard.reads.items())],
            'counts': manifest['counts'], 'exact_public_manifest_match': True,
            'native_reverse_equal': manifest['common']['native_reverse_equal'], 'inputs_unchanged': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lane', choices=('original', 'classical', 'bgk'), required=True)
    parser.add_argument('--native-root', type=Path, default=ROOT.parent / 'algebraic-geometry-bridge-id')
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    native, output = args.native_root.resolve(), args.output_root.resolve()
    require(output.is_relative_to((ROOT / 'work').resolve()) and output != ROOT / 'work', 'Output must be a child of integration work')
    require(not output.exists(), 'Inspect an existing run; do not overwrite it')
    peak = memory_cap()
    inputs, expected, manifest, assets = sealed_inputs(native, args.lane)
    output.mkdir(parents=True)
    binding = {'schema':'d100-english-backend-inputs/1', 'lane':args.lane, 'archives':assets,
               'inputs':[{'path':p, **f} for p,f in sorted(inputs.items())], 'expected_outputs':expected}
    (output / 'INPUT_BINDING.json').write_text(json.dumps(binding, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    runs = []
    for label in ('first', 'second'):
        runs.append(replay(native, output / label, args.lane, inputs, expected, label))
        print(json.dumps({'state':'reproduced', 'lane':args.lane, 'run':label, 'files':len(expected)}), flush=True)
    require(runs[0] == runs[1], 'Independent replay runs differ')
    report = {'schema':'d100-english-backend-replay/1', 'state':'pass', 'lane':args.lane, 'language':'en',
              'input_binding':file_fact(output / 'INPUT_BINDING.json'), 'public_archives':assets,
              'declared_input_files':len(inputs), 'native_english_source_files':len(manifest['english_source_order']),
              'historical_qa_source_closure':274, 'runs':runs, 'hard_memory_limit_bytes':LIMIT,
              'peak_process_commit_bytes':peak(), 'network_used_by_replay':False, 'producer_files_changed':False,
              'tex_or_pdf_build':False, 'new_translation_or_semantic_canon_review':False,
              'historical_review_claim_reproduced_not_independently_endorsed':True,
              'overall_backend_complete':False}
    (output / 'REPLAY.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k:report[k] for k in ('state','lane','declared_input_files','native_english_source_files','peak_process_commit_bytes')}))


if __name__ == '__main__':
    main()
