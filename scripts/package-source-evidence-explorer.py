"""Package the exact standalone tool and reproducible source, never private data."""
from pathlib import Path
import hashlib, io, json, subprocess, sys, zipfile
ROOT = Path(__file__).resolve().parents[1]
FILES = [
    'LICENSE',
    'docs/en/source-evidence.html', 'docs/id/source-evidence.html',
    'docs/interface/source-evidence-model.js', 'docs/interface/source-evidence-ui.js',
    'scripts/build-source-evidence-explorer.mjs',
    'scripts/package-source-evidence-explorer.py', 'scripts/test-source-evidence-explorer.mjs',
    'scripts/source-evidence-v1/source_use_projection.py',
    'scripts/source-evidence-v1/project_evidence.py',
    'scripts/source-evidence-v1/freeze_inputs.py',
    'scripts/source-evidence-v1/README.txt', 'scripts/source-evidence-v1/README.id.txt',
]
def package():
    payloads = {name: (ROOT / name).read_bytes() for name in FILES}
    rows = [{'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()} for name, raw in payloads.items()]
    manifest = {'schema': 'source-evidence-tools-package/1', 'scope': 'Standalone bilingual software and exact source; no mathematical text or private evidence included', 'reproduce': 'node scripts/build-source-evidence-explorer.mjs', 'model': 'gpt-6-astra', 'effort': 'ultra', 'files': rows}
    payloads['MANIFEST.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode()
    # Node treats the standalone source modules as ES modules, as in the programme.
    payloads['package.json'] = b'{"private":true,"type":"module"}\n'
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, raw in payloads.items():
            info = zipfile.ZipInfo(name, (2026, 10, 3, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, raw)
    raw = stream.getvalue()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        assert set(archive.namelist()) == set(payloads)
        for name, expected in payloads.items():
            assert archive.read(name) == expected, name
    destination = ROOT / 'docs/downloads/source-evidence-tools-v1.zip'
    if '--check' in sys.argv:
        assert destination.read_bytes() == raw, 'Source archive changed'
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    print(json.dumps({'state': 'pass', 'path': destination.relative_to(ROOT).as_posix(), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'members': len(payloads), 'private_data': False}))
if __name__ == '__main__': package()
