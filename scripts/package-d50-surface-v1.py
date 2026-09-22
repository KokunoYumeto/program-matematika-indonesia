"""Deterministic editable source package for the D50 metadata consumer only."""
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
base = Path('backend/course-capsule-v1/adapters/d50-surface-v1')
receipt = json.loads((root / base / 'tests.json').read_text(encoding='utf-8'))
assert receipt['state'] == 'pass'
files = [Path('scripts') / name for name in [
    'intake-d50-surface-v1.py', 'build-d50-surface-v1.mjs',
    'd50-study-plan-ui-v1.js', 'test-d50-surface-v1.mjs',
    'preview-d50-surface-v1.py', 'package-d50-surface-v1.py']]
files += [base / name for name in ['README.md', 'tests.json', 'browser-qa.json']]
files += [p.relative_to(root) for p in (root / base / 'input').iterdir() if p.is_file()]
files += [base / 'portable' / fact['path'] for fact in receipt['deterministic_replay']['outputs']]
lock = json.loads((root / base / 'input/source-lock.json').read_text(encoding='utf-8'))
files.append(Path(lock['authority']['path']))
for fact in receipt['deterministic_replay']['outputs']:
    b = (root / base / 'portable' / fact['path']).read_bytes()
    assert len(b) == fact['bytes'] and hashlib.sha256(b).hexdigest() == fact['sha256']
out = root / base / 'd50-selector-editable-source-v1.zip'
inventory = []
with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for path in sorted(set(files)):
        data = (root / path).read_bytes()
        info = zipfile.ZipInfo(path.as_posix(), (2026, 9, 22, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        z.writestr(info, data, compresslevel=9)
        inventory.append({'path': path.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for fact in inventory:
        b = z.read(fact['path'])
        assert len(b) == fact['bytes'] and hashlib.sha256(b).hexdigest() == fact['sha256']
b = out.read_bytes()
report = {'schema': 'd50-selector-source-package/1', 'state': 'pass', 'path': out.relative_to(root).as_posix(),
          'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(), 'members': inventory,
          'scope_id': 'Sumber lengkap alat dan metadata; bukan salinan buku. Bacaan asli adalah dependensi publik terpisah yang terikat hash.',
          'scope_en': 'Complete tool source and metadata, not a copy of the book. The original reader is a separate hash-bound public dependency.'}
(root / base / 'source-package.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({k: v for k, v in report.items() if k != 'members'}))
