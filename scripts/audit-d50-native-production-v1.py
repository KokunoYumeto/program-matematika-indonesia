"""Independently bind D50's frozen rebuild evidence and replay non-TeX outputs.

Reads the exact native public source ZIP, never writes to the producer tree.
Historical PDF replay is recorded as historical, not a fresh TeX execution.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d50-surface-v1'
EXPECTED_ZIP = {'bytes': 69154138,
                'sha256': '94bdc7c1f9ceec599daf59c0d303721be009a140d5a7bd5f794ac8887b935ae3'}
SOURCE = 'geometri-diferensial-manifold-mulus-edisi-lengkap-source-backend-r1-20260829.zip'
OUTPUTS = {
    'backend_jsonl': 'backend/records.jsonl',
    'backend_csv': 'backend/records.csv',
    'backend_manifest': 'backend/MANIFEST.json',
    'html_entry': 'output/html/complete/index.html',
    'html_manifest': 'output/html/complete/manifest.json',
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def fact(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def identity(path):
    digest, size = hashlib.sha256(), 0
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            size += len(block)
            digest.update(block)
    return {'bytes': size, 'sha256': digest.hexdigest()}


def core(row):
    return {k: row[k] for k in ['bytes', 'sha256']}


def validate_receipt(receipt, source_fact):
    require(receipt['status'] == 'pass', 'Native receipt is not pass')
    require(receipt['workflow'] == 'o011-verify-source-package-complete-v1', 'Wrong replay workflow')
    require(core(receipt['source_zip']) == source_fact == EXPECTED_ZIP, 'Source identity mismatch')
    required_checks = [
        'two_independent_clean_extractions', 'pdf_rebuilt_and_independently_verified_twice',
        'html_rebuilt_and_independently_verified_twice', 'backend_rebuilt_and_independently_verified_twice',
        'all_rebuilt_artifacts_match_canonical_bytes', 'all_seven_public_files_restaged_byte_identically_twice',
        'both_clean_cycles_match_each_other', 'source_zip_crc_paths_manifest_and_checksums_pass',
    ]
    require(all(receipt['checks'].get(k) is True for k in required_checks), 'Native replay check missing')
    cycles = receipt['clean_rebuilds']
    require([c['cycle'] for c in cycles] == [1, 2], 'Expected two distinct clean cycles')
    require(cycles[0]['outputs'] == cycles[1]['outputs'], 'Native cycle outputs differ')
    require(cycles[0]['restaged_files'] == cycles[1]['restaged_files'], 'Native restaging differs')
    for cycle in cycles:
        require(cycle['extraction']['zip'] == source_fact, 'Extraction identity mismatch')
        commands = cycle['commands']
        require(len(commands) == 7 and all(c['exit_code'] == 0 for c in commands), 'Seven successful commands required')
        for script in ['export_html_complete.py', 'verify_html_complete.py', 'export_backend_complete.py',
                       'verify_backend_complete.py', 'build_complete_reader.ps1', 'verify_complete_reader.py',
                       'stage_zenodo_complete.py']:
            require(sum(any(str(arg).endswith('/' + script) for arg in c['command']) for c in commands) == 1,
                    'Missing or duplicate native command: ' + script)
    return cycles[0]


def inspect_archive(archive, cycle):
    infos = archive.infolist()
    names = [i.filename for i in infos]
    require(len(names) == len(set(names)) == 1282, 'Archive member boundary differs')
    require(sum(i.file_size for i in infos) == 97182250, 'Archive expanded size differs')
    for info in infos:
        name = info.filename
        require(not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
                and ':' not in name and '\\' not in name, 'Unsafe archive member')
        require((info.external_attr >> 16) & 0o170000 != 0o120000, 'Symlink member forbidden')
    require(archive.testzip() is None, 'Source archive CRC failure')
    manifest = json.loads(archive.read('PACKAGE_MANIFEST.json'))
    checksums = {}
    for line in archive.read('PACKAGE_CHECKSUMS.sha256').decode('utf-8').splitlines():
        digest, name = line.split(None, 1)
        name = name.lstrip('*')
        require(name not in checksums, 'Duplicate checksum path')
        checksums[name] = digest
    require(set(checksums) == set(names) - {'PACKAGE_CHECKSUMS.sha256'}, 'Checksum inventory differs')
    for name, expected in checksums.items():
        require(hashlib.sha256(archive.read(name)).hexdigest() == expected, 'Member checksum differs: ' + name)
    listed = {r['path']: r for r in manifest['files']}
    require(len(listed) == len(manifest['files']) and set(listed) == set(names) -
            {'PACKAGE_MANIFEST.json', 'PACKAGE_CHECKSUMS.sha256'}, 'Manifest inventory differs')
    for name, row in listed.items():
        require(fact(archive.read(name)) == core(row), 'Member identity differs: ' + name)
    for key, rel in OUTPUTS.items():
        if rel in names:
            require(fact(archive.read(rel)) == cycle['outputs'][key], 'Historical output binding differs: ' + rel)
    for key, name in [('manifest', 'PACKAGE_MANIFEST.json'), ('checksums', 'PACKAGE_CHECKSUMS.sha256')]:
        require(fact(archive.read(name)) == core(cycle['extraction'][key]), 'Historical extraction differs')
    return manifest


def replay(archive, work, cycle):
    copied = Path(tempfile.mkdtemp(prefix='d50-native-replay-', dir=work)).resolve()
    require(copied.parent == work.resolve(), 'Temporary extraction escaped work directory')
    try:
        archive.extractall(copied)
        native = json.loads((copied / 'backend/MANIFEST.json').read_bytes())
        checkpoint, state = native['checkpoint'], native['translation_state']
        commands = [
            ['scripts/export_html_complete.py', '--root', '.', '--output', 'output/html/complete', '--replace'],
            ['scripts/verify_html_complete.py', '--root', '.', '--output', 'output/html/complete'],
            ['scripts/export_backend_complete.py', '--root', '.', '--checkpoint', checkpoint,
             '--translation-state', state],
            ['scripts/verify_backend_complete.py', '--root', '.', '--check-only'],
        ]
        env = os.environ.copy()
        env.update(PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1', HTTP_PROXY='http://127.0.0.1:9',
                   HTTPS_PROXY='http://127.0.0.1:9', ALL_PROXY='http://127.0.0.1:9', NO_PROXY='')
        receipts = []
        for args in commands:
            done = subprocess.run([sys.executable, '-B', *args], cwd=copied, env=env,
                                  capture_output=True, timeout=240)
            output = done.stdout + done.stderr
            receipts.append({'command': ['python', '-B', *args], 'exit_code': done.returncode,
                             'output': fact(output)})
            require(done.returncode == 0, 'Replay failed: ' + args[0] + ': ' + output.decode('utf-8', errors='replace')[-1200:])
        outputs = {k: identity(copied / path) for k, path in OUTPUTS.items()}
        differences = {k: {'expected': cycle['outputs'][k], 'actual': row}
                       for k, row in outputs.items() if row != cycle['outputs'][k]}
        require(not differences, 'Fresh replay output drift: ' + json.dumps(differences))
        return {'commands': receipts, 'outputs': outputs, 'matches_frozen_native_outputs': True,
                'tex_executed': False, 'proxy_network_blocking': True}
    finally:
        require(copied.parent == work.resolve() and copied.name.startswith('d50-native-replay-'),
                'Refuse unsafe temporary cleanup')
        shutil.rmtree(copied)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--replay', action='store_true')
    args = parser.parse_args()
    native, output = args.native_root.resolve(), args.output.resolve()
    require(output.is_relative_to(ROOT / 'work') or output.is_relative_to(BASE), 'Receipt write outside central scope')
    source = native / 'output/release-complete-r1' / SOURCE
    source_fact = identity(source)
    receipt_path = native / 'qa/complete/SOURCE_PACKAGE_INTEGRITY_R1.json'
    receipt_bytes = receipt_path.read_bytes()
    receipt = json.loads(receipt_bytes)
    cycle = validate_receipt(receipt, source_fact)
    dependencies = json.loads((BASE / 'delivery/public-dependencies.json').read_bytes())
    public_source = next(f for f in dependencies['files'] if f['url'].endswith('/' + SOURCE))
    require(core(public_source) == source_fact and public_source['anonymous'], 'Published source identity missing')
    for entry in receipt['outer_release']['files']:
        require(identity(source.parent / entry['filename']) == core(entry), 'Public release cache drift')
        require(cycle['restaged_files'][entry['filename']] == core(entry), 'Restaged/public identity differs')
    for key, path in [('backend_jsonl', 'input/records.jsonl'), ('backend_manifest', 'input/native-manifest.json'),
                      ('html_manifest', 'input/reader-manifest.json')]:
        require(identity(BASE / path) == cycle['outputs'][key], 'Central/native evidence differs: ' + key)
    with zipfile.ZipFile(source) as archive:
        manifest = inspect_archive(archive, cycle)
        work = ROOT / 'work/d50-native-production-audit'
        work.mkdir(parents=True, exist_ok=True)
        fresh = replay(archive, work, cycle) if args.replay else None
    result = {
        'schema': 'd50-native-production-audit/1', 'state': 'pass', 'source_archive': public_source,
        'native_receipt': {'native_path': 'qa/complete/SOURCE_PACKAGE_INTEGRITY_R1.json', **fact(receipt_bytes)},
        'source_members': 1282, 'uncompressed_bytes': 97182250,
        'all_source_checksums_verified': True, 'native_receipt_two_cycles_validated': True,
        'cached_release_files_match_both_cycles': 7,
        'current_central_native_bindings_match': True,
        'fresh_html_backend_replay': fresh,
        'historical_pdf_replay': {'cycles': 2, 'outputs_match': True, 'pdf': cycle['outputs']['pdf']},
        'fresh_pdf_build': False, 'source_modified': False, 'new_translation_quality_claim': False,
        'overall_program_backend_complete': False,
        'limits': 'Fresh HTML/backend replay only when requested; the two complete PDF rebuilds are frozen native evidence, not a new TeX run. No fresh semantic or accessibility certification.',
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'state': 'pass', 'source_members': 1282, 'native_cycles': 2,
                      'fresh_html_backend_replay': fresh is not None, 'fresh_pdf_build': False}))


if __name__ == '__main__':
    main()
