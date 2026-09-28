"""Package complete editable CLP planner source and verify an offline rebuild."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/clp-teacher-v1'
REL = BASE.relative_to(ROOT).as_posix()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pack(path, files):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 27, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            z.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main():
    scripts = ['intake-clp-teacher-v1.py', 'build-clp-teacher-v1.py', 'test-clp-teacher-v1.py',
               'test-clp-teacher-ui-v1.mjs', 'package-clp-teacher-v1.py', 'build-clp-teacher-hosted-v1.py']
    paths = [ROOT/'scripts'/name for name in scripts]
    paths += [BASE/p for p in ('input/native-exercises.json', 'input/source-lock.json', 'ui/teacher.js', 'ui/teacher.css', 'README.md')]
    # Retain the exact license texts from the frozen producer editions; no new
    # internet lookup or alteration of legal wording is needed.
    license_inputs = [
        ('CLP1', ROOT.parents[2]/'04_mirrors/id/clp1-differential-calculus-id/LICENSE-CC-by-nc-sa.md', '751431b663663e16259724ffecc04f1d5e1501ead3eb2d7dbb4dbe20dfc2bf52'),
        ('CLP2-4', ROOT.parents[2]/'04_mirrors/id/clp2-integral-calculus-id/repo/LICENSE-CC-by-nc-sa.md', '3e976176dec037ecb34de78f6b67040dee8d015915d702854c6c8b2308fcb557')]
    for name, source, expected in license_inputs:
        target = BASE/'input'/f'LICENSE-{name}-CC-BY-NC-SA-4.0.txt'
        data = target.read_bytes() if target.exists() else source.read_bytes()
        assert sha(data) == expected
        if not target.exists():
            target.write_bytes(data)
        paths.append(target)
    files = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in paths}
    tests = json.loads((BASE/'tests.json').read_bytes())
    assert tests['state'] == 'pass' and tests['native_exercises_individually_checked'] == 2198
    output = BASE/'clp-teacher-editable-source-v1.zip'
    pack(output, files)
    with tempfile.TemporaryDirectory(prefix='clp-teacher-source-replay-') as temp:
        temp = Path(temp)
        with zipfile.ZipFile(output) as z:
            assert z.testzip() is None and z.namelist() == sorted(files)
            assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
            z.extractall(temp)
        run = subprocess.run([sys.executable, '-B', str(temp/'scripts/build-clp-teacher-v1.py')], cwd=temp, capture_output=True, text=True, timeout=45)
        assert run.returncode == 0, run.stderr
        receipt = json.loads((BASE/'site/teacher-build.json').read_bytes())
        for f in receipt['files']:
            data = (temp/REL/'site'/f['path']).read_bytes()
            assert len(data) == f['bytes'] and sha(data) == f['sha256'], f['path']
        assert (temp/REL/'site/teacher-build.json').read_bytes() == (BASE/'site/teacher-build.json').read_bytes()
        pack(temp/'repack.zip', {n: (temp/n).read_bytes() for n in files})
        assert (temp/'repack.zip').read_bytes() == output.read_bytes()
    data = output.read_bytes()
    result = {'schema': 'clp-teacher-source-replay/1', 'state': 'pass', 'source_members': len(files), 'replayed_outputs': len(receipt['files'])+1,
              'package': {'path': output.name, 'bytes': len(data), 'sha256': sha(data)}, 'byte_identical_repack': True,
              'offline_rebuild_exact': receipt['files'], 'scope': 'complete planner source, not a textbook archive', 'published': False}
    (BASE/'source-package.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(json.dumps({'state': 'pass', 'members': len(files), 'package': result['package']}))


if __name__ == '__main__':
    main()
