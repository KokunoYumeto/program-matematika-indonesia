"""Build a small deterministic preservation packet without native reader copies."""
import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
base = Path('backend/course-capsule-v1/adapters/b80-capability-v1')
manifest = json.loads((root / base / 'manifest.json').read_bytes())
validation = json.loads((root / base / 'validation.json').read_bytes())
assert validation['state'] == 'pass'
paths = {row['path'] for row in manifest['inputs'] + manifest['outputs']}
paths.update((base / filename).as_posix() for filename in ('manifest.json', 'validation.json', 'README.md'))
paths.update('scripts/' + filename for filename in (
    'native-catalog-exchange-v1.mjs', 'build-b80-capability-v1.mjs',
    'validate-b80-capability-v1.py', 'test-b80-capability-v1.mjs',
    'import-b80-capability-v1.mjs', 'html-anchor-facts.py', 'package-b80-capability-v1.py'))
paths.update(('docs/backend/b80/validation.json', 'docs/id/index.html'))
files = {path: (root / path).read_bytes() for path in sorted(paths)}
files['START_HERE.md'] = b'''# B80 learning capability preservation packet

Open docs/backend/b80/B80.html for the Indonesian exercise map, or
docs/backend/b80/B80-pengajar.html for the teacher view. The lesson links open
the public native book; this is not a copy of that book or its Python runtime.

Rebuild from this archive root with Node 22 and Python plus jsonschema 4.26.0:

    node scripts/build-b80-capability-v1.mjs
    python -B scripts/validate-b80-capability-v1.py

All frozen metadata, schemas and tests needed for the adapter are included.
docs/id/index.html is the central course-link fixture, not a complete offline
copy of the multilingual program. The adapter is course-learning-capability/1,
not an assertion of contract-2.3.1 conformance or new textbook translation.

The full program-wide modular backend remains unfinished. This packet is one
verified increment in its existing GitHub and Zenodo preservation lineages.
'''
identity = lambda path, data: {'path': path, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
inventory = [identity(path, data) for path, data in sorted(files.items())]
files['PACKET_INVENTORY.json'] = (json.dumps({'schema': 'b80-preservation-packet/1', 'files': inventory}, indent=2) + '\n').encode()


def build():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, data in sorted(files.items()):
            assert not Path(path).is_absolute() and '..' not in Path(path).parts
            info = zipfile.ZipInfo(path, (2026, 9, 4, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)
    return stream.getvalue()


payload = build()
assert payload == build()
with zipfile.ZipFile(io.BytesIO(payload)) as archive:
    assert archive.testzip() is None
    for path, data in files.items():
        assert archive.read(path) == data
target = root / 'releases/b80-learning-capability-v1'
target.mkdir(parents=True, exist_ok=True)
filename = 'B80_NATIVE_LEARNING_CAPABILITY_V1.zip'
(target / filename).write_bytes(payload)
receipt = {'schema': 'b80-capability-packet-build/1', 'state': 'pass',
           'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
           'archive': identity(filename, payload), 'entries': len(files),
           'deterministic_zip_replay': True, 'crc_and_full_entry_readback': True,
           'adapter_manifest_sha256': validation['manifest_sha256'], 'public_release_verified': False}
(target / 'PACKET_BUILD_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt, indent=2))
