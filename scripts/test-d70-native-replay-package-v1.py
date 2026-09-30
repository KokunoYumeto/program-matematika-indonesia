"""Execute packaged sources twice with only two archive inputs available."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d70-native-replay-v1'
spec = importlib.util.spec_from_file_location('replay', Path(__file__).with_name('replay-d70-native-metadata-v1.py'))
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-archive', type=Path, default=ROOT.parent / 'metode-aljabar-jilid-1-id/publication/o013-aggregate-1.0.0/05_o013-sumber-backend-1.0.0.zip')
    args = parser.parse_args()
    bundle = BASE / 'build/D70_NATIVE_METADATA_REPLAY_V1.zip'
    replay.verified_bundle(bundle)
    work = ROOT / 'work/d70-packaged-replay-v1'
    work.mkdir(parents=True, exist_ok=True)
    isolated = Path(tempfile.mkdtemp(prefix='packaged-', dir=work)).resolve()
    shutil.copyfile(bundle, isolated / bundle.name)
    native_copy = isolated / replay.audit.ARCHIVE
    shutil.copyfile(args.source_archive, native_copy)
    assert replay.audit.identity(native_copy) == replay.audit.EXPECTED_ARCHIVE
    with zipfile.ZipFile(bundle) as archive:
        names = replay.checked_members(archive, 6 * 1024 * 1024)
        for name in names:
            target = isolated / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as output:
                output.write(archive.read(name))
    reports = []
    for index in range(2):
        command = [sys.executable, '-B', 'scripts/replay-d70-native-metadata-v1.py',
                   '--bundle', bundle.name, '--source-archive', native_copy.name,
                   '--work-dir', f'run-{index}', '--output', f'replay-{index}.json']
        process = subprocess.run(command, cwd=isolated, capture_output=True, text=True, timeout=90)
        assert process.returncode == 0, 'Packaged source replay failed; inspect isolated output'
        value = json.loads((isolated / f'replay-{index}.json').read_bytes())
        assert value['state'] == 'pass' and value['producer_tree_required'] is False
        assert len(value['artifact_comparisons']) == 13 and all(row['matches_shipped_bytes'] for row in value['artifact_comparisons'])
        reports.append(value)
    assert reports[0] == reports[1], 'Two packaged-source replays differ'
    report = reports[0]
    report.update(packaged_sources_executed=True, two_isolated_replays_identical=True,
                  native_source_copied_before_execution=True, supplied_input_archives=2,
                  input_archive_bytes=replay.audit.identity(bundle)['bytes'] + replay.audit.EXPECTED_ARCHIVE['bytes'])
    (BASE / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'state': 'pass', 'two_isolated_replays_identical': True,
                      'packaged_sources_executed': True, 'native_metadata_artifacts': 13,
                      'producer_tree_required': False, 'whole_native_parity_proven': False}))


if __name__ == '__main__':
    main()
