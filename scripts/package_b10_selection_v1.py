"""Deterministic B10 selector archive; readback mode verifies all member bytes."""
from pathlib import Path
import hashlib
import io
import json
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/b10-selection-v1'
digest = lambda b: hashlib.sha256(b).hexdigest()
assert sys.argv[1:] in ([], ['--verify-only'])
verify = sys.argv[1:] == ['--verify-only']
manifest_bytes = (BASE / 'manifest.json').read_bytes()
manifest = json.loads(manifest_bytes)
validation = json.loads((BASE / 'validation.json').read_bytes())
assert validation['result'] == 'pass'
assert validation['manifest']['sha256'] == digest(manifest_bytes)
members = {}
for r in manifest['outputs']:
    b = (BASE / r['path']).read_bytes()
    assert len(b) == r['bytes'] and digest(b) == r['sha256']
    members[r['path']] = b
for path in ('manifest.json', 'validation.json'):
    members[path] = (BASE / path).read_bytes()
members['MULAI-START.txt'] = (
    'Buka views/B10.html atau views/B10-pengajar.html.\n'
    'English: open views/B10-en.html or views/B10-pengajar-en.html.\n'
    'Pemilih bekerja luring. Teks buku tidak disertakan.\n'
    'The selectors work offline. Textbooks are not included; readings are English.\n'
).encode('utf-8')
def build():
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, b in sorted(members.items()):
            assert not name.startswith('/') and '..' not in Path(name).parts
            i = zipfile.ZipInfo(name, (2026, 9, 8, 0, 0, 0))
            i.compress_type = zipfile.ZIP_DEFLATED
            i.create_system = 3
            i.external_attr = 0o100644 << 16
            z.writestr(i, b, compresslevel=9)
    return out.getvalue()
payload = build()
assert payload == build()
target = BASE / 'B10-selection-offline.zip'
if verify:
    assert target.read_bytes() == payload
else:
    target.write_bytes(payload)
with zipfile.ZipFile(io.BytesIO(target.read_bytes())) as z:
    assert z.testzip() is None and set(z.namelist()) == set(members)
    for name, b in members.items():
        assert z.read(name) == b
receipt = {'schema':'b10-selection-package/1','result':'pass','path':target.name,
           'bytes':len(payload),'sha256':digest(payload),'members':len(members),
           'textbook_bodies_included':False,'deterministic':True}
if verify:
    assert json.loads((BASE / 'package.json').read_bytes()) == receipt
else:
    (BASE / 'package.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(receipt))
