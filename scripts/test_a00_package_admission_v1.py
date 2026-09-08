"""Isolated rejection tests for the exact read-only A00 package admission gate."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REL = Path('backend/course-capsule-v1/adapters/a00-concept-teacher-v1')
SCRIPT = Path('scripts/package_a00_concept_teacher_v1.py')
cases = [
    ('changed_output', 'views/A00.html'),
    ('changed_snapshot', 'input/concept-rights.json'),
    ('changed_source_lock', 'input/source-lock.json'),
    ('changed_manifest', 'manifest.json'),
    ('changed_zip', 'A00-concept-teacher-offline.zip'),
    ('changed_package_receipt', 'package.json'),
]
with tempfile.TemporaryDirectory(prefix='a00-admission-test-') as directory:
    root = Path(directory).resolve()
    (root / SCRIPT).parent.mkdir(parents=True)
    shutil.copyfile(ROOT / SCRIPT, root / SCRIPT)
    shutil.copytree(ROOT / REL, root / REL)
    command = [sys.executable, '-B', str(root / SCRIPT), '--verify-only']
    good = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert good.returncode == 0, good.stderr
    rejected = []
    for name, path in cases:
        target = root / REL / path
        original = target.read_bytes()
        if path == 'package.json':
            changed = json.loads(original)
            changed['sha256'] = '0' * 64
            target.write_text(json.dumps(changed), encoding='utf-8')
        else:
            target.write_bytes(original + b'\n')
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            assert result.returncode != 0 and 'AssertionError' in result.stderr, name
            rejected.append(name)
        finally:
            target.write_bytes(original)
    print(json.dumps({'state': 'pass', 'positive_current_packet': True,
                      'rejected_mutations': rejected, 'production_files_modified': False}))
