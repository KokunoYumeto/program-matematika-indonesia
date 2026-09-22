"""Replay the portable and hosted D50 tools from their distributed source ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
from central_surface_navigation_overlay_v1 import strip_central_surface_overlay

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('backend/course-capsule-v1/adapters/d50-surface-v1')
p = argparse.ArgumentParser()
p.add_argument('--release-dir', type=Path, required=True)
args = p.parse_args()
release = args.release_dir.resolve()
source = ROOT / BASE / 'd50-selector-editable-source-v1.zip'
with tempfile.TemporaryDirectory(prefix='d50-source-replay-') as directory:
    replay = Path(directory).resolve()
    assert replay.parent == Path(tempfile.gettempdir()).resolve()
    with zipfile.ZipFile(source) as z:
        assert z.testzip() is None
        assert sum(i.file_size for i in z.infolist()) < 30_000_000
        for member in z.namelist():
            assert (replay / member).resolve().is_relative_to(replay)
        z.extractall(replay)
    commands = [
        ['node','scripts/test-d50-surface-v1.mjs'],
        [sys.executable,'-B','scripts/stage-d50-reader-v1.py','--release-dir',str(release)],
        ['node','scripts/build-d50-hosted-v1.mjs'],
        [sys.executable,'-B','scripts/test-d50-hosted-v1.py'],
        [sys.executable,'-B','scripts/package-d50-surface-v1.py'],
    ]
    for command in commands:
        result = subprocess.run(command,cwd=replay,capture_output=True,text=True,encoding='utf-8')
        assert result.returncode == 0, result.stdout[-500:]+result.stderr[-1500:]
    checked = []
    for file in (replay / 'docs/backend/d50').rglob('*'):
        if not file.is_file():
            continue
        rel = file.relative_to(replay)
        expected = (ROOT / rel).read_bytes()
        if file.suffix == '.html':
            expected = strip_central_surface_overlay(expected,rel.as_posix())
        assert file.read_bytes() == expected, rel
        checked.append(rel.as_posix())
    assert (replay / BASE / source.name).read_bytes() == source.read_bytes()
receipt = {'schema':'d50-isolated-source-replay/1','state':'pass','files_compared':len(checked),
           'tool_source_zip':{'bytes':source.stat().st_size,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()},
           'archive_repacked_identically':True,'hosted_source_bodies_identical':True,
           'independent_native_book_retranslation':False,'tex_compilation_replayed':False}
(ROOT / BASE / 'source-replay.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(receipt))
