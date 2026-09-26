"""Deterministic, complete editable source for the D110 selector, not a book ZIP."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d110-surface-v1'
REL = BASE.relative_to(ROOT).as_posix()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pack(destination, files):
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 26, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main():
    script_names = ['intake-d110-surface-v1.py', 'build-d110-surface-v1.py', 'test-d110-surface-v1.py', 'package-d110-surface-v1.py',
                    'build-d110-hosted-v1.py', 'd110-surface/d110-ui.js', 'd110-surface/d110.css', 'd110-surface/test-d110-ui.mjs']
    paths = [ROOT / 'scripts' / name for name in script_names]
    paths += [BASE / 'input' / name for name in ['unit.jsonl', 'asset.jsonl', 'relation.jsonl', 'rights.jsonl', 'source-lock.json', 'reader-witness.json', 'solution-witness.json']]
    paths += [BASE / 'input' / name for name in ('LICENSE-APACHE-2.0.txt', 'LICENSE-CC-BY-4.0.txt')]
    paths += [ROOT / 'backend/v2.3/extensions/d110-mathematics-in-lean-v0.1.0/INPUT_AUTHORITIES.json', BASE / 'README.md']
    files = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in paths}
    output = BASE / 'd110-selector-editable-source-v1.zip'
    pack(output, files)
    with tempfile.TemporaryDirectory(prefix='d110-source-replay-') as temp:
        temp = Path(temp)
        with zipfile.ZipFile(output) as z:
            assert z.testzip() is None
            assert z.namelist() == sorted(files)
            assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
            z.extractall(temp)
        # Rebuild uses only bundled witnesses; no network, native checkout or Lean.
        completed = subprocess.run([sys.executable, '-B', str(temp / 'scripts/build-d110-surface-v1.py')],
                                   cwd=temp, capture_output=True, text=True, timeout=45)
        assert completed.returncode == 0, completed.stderr
        replayed = temp / REL / 'portable'
        expected = sorted((BASE / 'portable').iterdir())
        assert {p.name for p in expected} == {p.name for p in replayed.iterdir()}
        identities = []
        for p in expected:
            data = p.read_bytes()
            assert (replayed / p.name).read_bytes() == data, p.name
            identities.append({'path': p.name, 'bytes': len(data), 'sha256': sha(data)})
        repack = temp / 'repacked.zip'
        pack(repack, {name: (temp / name).read_bytes() for name in files})
        assert repack.read_bytes() == output.read_bytes()
    payload = output.read_bytes()
    report = {'schema': 'd110-source-package-replay/1', 'state': 'pass', 'source_members': len(files),
              'package': {'path': output.name, 'bytes': len(payload), 'sha256': sha(payload)},
              'offline_rebuild_exact': identities, 'byte_identical_repack': True,
              'scope': 'selector code, pinned native metadata and hash-bound witnesses; not a complete offline textbook',
              'published': False}
    (BASE / 'source-package.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'state': 'pass', 'source_members': len(files), 'replayed_outputs': len(identities), 'package': report['package']}))


if __name__ == '__main__':
    main()
