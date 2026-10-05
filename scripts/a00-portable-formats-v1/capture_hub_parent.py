"""Capture exact selected hub files, refusing to overwrite a divergent local edit."""
import hashlib
import json
import os
import sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/a00-portable-formats-v1'
PARENT = '540e24a71d351c2573d81ab33632b1bb5d1d7384'
REPO = 'KokunoYumeto/program-matematika-indonesia'
LANGUAGE = os.environ.get('A00_HUB_LANGUAGE', 'id')
assert LANGUAGE in ('id', 'en')
OWN_TOOLS = []
if LANGUAGE == 'en':
    OUT = ROOT / 'outputs/a00-english-portable-formats-v1'
    head = requests.get(f'https://api.github.com/repos/{REPO}/git/ref/heads/main', timeout=(15,45))
    head.raise_for_status()
    PARENT = head.json()['object']['sha']
    OWN_TOOLS = ['scripts/a00-portable-formats-v1/'+name for name in (
        'capture_hub_parent.py', 'restore_hub_navigation.py', 'check_hub_additive.mjs',
        'check_hub_browser.mjs', 'publish_hub.py')]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda b: hashlib.sha256(b).hexdigest()
receipt = read(ROOT / 'docs/interface/build-receipt.json')
paths = sorted(set([r['path'] for r in receipt['outputs']] + [
    'docs/index.html', 'docs/interface/build-receipt.json',
    'docs/interface/supplemental-readers.js', 'docs/interface/reader-actions.js',
    'docs/interface/final-editions.js', 'docs/interface/capability-tools.js',
    'scripts/test-course-downloads-v1.mjs', 'scripts/build-multilingual-interface.mjs',
    'backend/authority/central-course-surface-navigation-overlay-v1.json']))
if LANGUAGE == 'en':
    paths = sorted(set(paths + OWN_TOOLS + ['scripts/test-multilingual-interface.mjs',
                                           'docs/interface/view.js', 'docs/interface/locales.js']))
target = OUT / 'hub-parent'
if sys.argv[1:] in (['--extend-interface-test'],['--extend-format-view']):
    existing=read(target/'BASELINE.json')
    assert existing['parent']==PARENT
    rows=existing['files']
    paths=['scripts/test-multilingual-interface.mjs'] if sys.argv[1:] == ['--extend-interface-test'] else ['docs/interface/view.js','docs/interface/locales.js']
    assert not any(r['path'] in paths for r in rows),'Already captured'
else:
    assert not sys.argv[1:]
    assert not (target / 'BASELINE.json').exists(), 'Existing baseline: inspect, do not replace'
    rows = []
for path in paths:
    local = (ROOT / path).read_bytes()
    response = requests.get(f'https://raw.githubusercontent.com/{REPO}/{PARENT}/{path}', timeout=(15,45))
    assert response.status_code == 200, (path, response.status_code)
    remote = response.content
    if path not in OWN_TOOLS:
        assert local.replace(b'\r\n', b'\n') == remote.replace(b'\r\n', b'\n'), 'Divergent local file: ' + path
    else:
        # Only these task-owned helpers may be under preparation. Preserve the
        # exact public parent as their diff baseline; never overwrite local work.
        local = remote
    saved = target / path
    saved.parent.mkdir(parents=True, exist_ok=True)
    saved.write_bytes(local)
    rows.append({'path':path, 'bytes':len(local), 'sha256':sha(local),
                 'public_parent_bytes':len(remote), 'public_parent_sha256':sha(remote),
                 'equal_except_possible_line_endings':True})
record = {'parent':PARENT, 'files':rows, 'remote_content_preserved':True}
(target / 'BASELINE.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'state':'baseline_verified','parent':PARENT,'files':len(rows)}))
