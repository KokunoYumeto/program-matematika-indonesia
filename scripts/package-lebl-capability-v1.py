"""Deterministic, independently replayed Lebl capability preservation packet."""
import hashlib
import io
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('backend/course-capsule-v1/adapters/lebl-capability-v1')
sha = lambda data: hashlib.sha256(data).hexdigest()
manifest = json.loads((ROOT / BASE / 'manifest.json').read_bytes())
validation = json.loads((ROOT / BASE / 'validation.json').read_bytes())
assert validation['state'] == 'pass'
assert validation['manifest_sha256'] == sha((ROOT / BASE / 'manifest.json').read_bytes())
paths = {fact['path'] for fact in manifest['inputs'] + manifest['outputs']}
for fact in manifest['inputs'] + manifest['outputs']:
    data = (ROOT / fact['path']).read_bytes()
    assert len(data) == fact['bytes'] and sha(data) == fact['sha256']
paths.update((BASE / name).as_posix() for name in ['manifest.json', 'validation.json', 'README.md'])
paths.update(['scripts/import-lebl-capability-v1.py', 'scripts/package-lebl-capability-v1.py',
              'docs/backend/lebl/validation.json', 'docs/backend/index.html', 'docs/id/index.html'])
files = {path: (ROOT / path).read_bytes() for path in sorted(paths)}
files['START_HERE.md'] = b'''# Lebl learner and teacher capability packet

Open docs/backend/lebl/B70.html, C10.html, C20.html or C50.html.
Use the matching -pengajar.html page for teacher plans, and istilah.html for
terminology. Books remain external; download linked PDFs separately.

Rebuild with Node 22 and Python plus jsonschema from this archive root:

    node scripts/build-lebl-capability-v1.mjs
    python -B scripts/validate-lebl-capability-v1.py

Frozen metadata, source binding, schemas and tests are included. The two parent
navigation HTML files are link fixtures, not a complete offline curriculum.
See the adapter README for scope, provenance, design and preserved limitations.
This does not claim full native replay or completion of the 40-role backend.
'''
identity = lambda path, data: {'path': path, 'bytes': len(data), 'sha256': sha(data)}
files['PACKET_INVENTORY.json'] = (json.dumps({'schema': 'lebl-capability-packet/1',
    'files': [identity(path, data) for path, data in sorted(files.items())]}, indent=2) + '\n').encode()


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
with tempfile.TemporaryDirectory(prefix='lebl-packet-replay-') as temporary:
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        assert archive.testzip() is None
        for path, data in files.items():
            assert archive.read(path) == data
        archive.extractall(temporary)  # Every path above is explicitly relative and traversal-free.
    for command in [['node', 'scripts/build-lebl-capability-v1.mjs'], ['python', '-B', 'scripts/validate-lebl-capability-v1.py']]:
        run = subprocess.run(command, cwd=temporary, capture_output=True, text=True)
        assert run.returncode == 0, run.stdout + run.stderr
    for fact in manifest['outputs']:
        assert (Path(temporary) / fact['path']).read_bytes() == files[fact['path']]
target = ROOT / 'releases/lebl-learning-capability-v1'
target.mkdir(parents=True, exist_ok=True)
filename = 'LEBL_NATIVE_LEARNING_CAPABILITY_V1.zip'
(target / filename).write_bytes(payload)
receipt = {'schema': 'lebl-capability-packet-build/1', 'state': 'pass',
    'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'archive': identity(filename, payload), 'entries': len(files), 'deterministic_zip_replay': True,
    'crc_and_full_entry_readback': True, 'extracted_packet_build_and_validation': True,
    'adapter_manifest_sha256': validation['manifest_sha256'], 'public_release_verified': False}
(target / 'PACKET_BUILD_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt))
