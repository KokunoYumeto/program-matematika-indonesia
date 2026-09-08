"""Deterministic offline consumer package; no textbook bodies or private sources."""
from pathlib import Path
import hashlib
import io
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/a00-concept-teacher-v1'
digest = lambda payload: hashlib.sha256(payload).hexdigest()
manifest = json.loads((BASE / 'manifest.json').read_bytes())
validation = json.loads((BASE / 'validation.json').read_bytes())
assert validation['result'] == 'pass'
assert validation['manifest']['sha256'] == digest((BASE / 'manifest.json').read_bytes())
members = {}
for item in manifest['outputs']:
    payload = (BASE / item['path']).read_bytes()
    assert len(payload) == item['bytes'] and digest(payload) == item['sha256']
    members[item['path']] = payload
lock = json.loads((BASE / 'input/source-lock.json').read_bytes())
for item in lock['snapshots']:
    payload = (BASE / 'input' / item['path']).read_bytes()
    assert len(payload) == item['bytes'] and digest(payload) == item['sha256']
    members['input/' + item['path']] = payload
for path in ('input/source-lock.json', 'manifest.json', 'validation.json'):
    members[path] = (BASE / path).read_bytes()
members['MULAI-START.txt'] = (
    'Buka views/A00.html atau views/A00-pengajar.html di peramban.\n'
    'English: open views/A00-en.html or views/A00-pengajar-en.html.\n'
    'Peta, prasyarat, dan pemilih bekerja tanpa jaringan. Teks buku tidak termasuk.\n'
    'The map, prerequisites and selectors need no network. Textbooks are not included.\n'
    'Reading links use public Indonesian textbook modules.\n'
).encode('utf-8')

def archive():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, payload in sorted(members.items()):
            assert not name.startswith('/') and '..' not in Path(name).parts
            item = zipfile.ZipInfo(name, (2026, 9, 8, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o100644 << 16
            item.create_system = 3
            z.writestr(item, payload, compresslevel=9)
    return stream.getvalue()

payload = archive()
assert payload == archive()
path = BASE / 'A00-concept-teacher-offline.zip'
path.write_bytes(payload)
with zipfile.ZipFile(path) as z:
    assert z.testzip() is None and z.namelist() == sorted(members)
    for name, expected in members.items():
        assert z.read(name) == expected
receipt = {'schema': 'a00-concept-teacher-package/1', 'result': 'pass',
           'path': path.name, 'bytes': len(payload), 'sha256': digest(payload),
           'members': len(members), 'deterministic_two_builds': True,
           'archive_member_readback': True, 'textbook_bodies_included': False,
           'browser_execution_tested': False,
           'scope': 'offline_navigation_and_metadata_selection; reading_requires_external_book'}
(BASE / 'package.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt))
