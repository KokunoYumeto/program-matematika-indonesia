"""Prove local concordance downloads and isolated A00 metadata replay in the current ZIP.

Not a native-book rebuild or semantic/canon review; no producer input is used.
"""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

PREFIX = 'backend/course-capsule-v1/adapters/a00-native-ledger-v1/'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if href.startswith('native-ledger/'):
                self.links.append('docs/backend/a00/' + href)


def sha(body):
    return hashlib.sha256(body).hexdigest()


archive_path = Path(sys.argv[1])
with zipfile.ZipFile(archive_path) as archive:
    manifest = json.loads(archive.read('CURRENT_BACKEND_PACKAGE_MANIFEST.json'))
    facts = {r['path']: r for r in manifest['files']}
    required = set()
    for filename in ['ledger.html', 'ledger-en.html']:
        parser = Links()
        parser.feed(archive.read('docs/backend/a00/' + filename).decode('utf-8'))
        required.update(parser.links)
    assert 'docs/backend/a00/native-ledger/term-locations.json' in required
    for name in sorted(required):
        body = archive.read(name)
        assert name in facts and len(body) == facts[name]['bytes'] and sha(body) == facts[name]['sha256']
    proof = archive.read('docs/backend/a00/native-ledger/term-locations.json')
    assert proof == archive.read(PREFIX + 'input/term-locations.json')
    lock = json.loads(archive.read(PREFIX + 'input/source-lock.json'))
    assert lock['term_locations']['bytes'] == len(proof)
    assert lock['term_locations']['sha256'] == sha(proof)
    data = json.loads(proof)
    assert len(data['choices']) == 20 and data['summary']['choice_variant_matches'] == 3419
    replay_members = [name for name in archive.namelist() if name.startswith(PREFIX)]
    replay_members += ['scripts/a00-native-ledger-v1.py', 'scripts/a00_term_locations_v1.py',
                       'scripts/test-a00-native-ledger-v1.py', 'scripts/test-a00-native-ledger-ui-v1.mjs', 'LICENSE']
    with tempfile.TemporaryDirectory(prefix='a00-current-package-replay-') as temp:
        root = Path(temp).resolve()
        for name in replay_members:
            path = (root / name).resolve()
            assert path.is_relative_to(root) and not path.is_symlink()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.read(name))
        result = subprocess.run([sys.executable, '-B', 'scripts/a00-native-ledger-v1.py'], cwd=root,
                                capture_output=True, encoding='utf-8', timeout=60)
        assert result.returncode == 0, result.stderr[-1500:]
        for name in ['data/ledger.json', 'data/source.zip', 'views/ledger.html', 'views/ledger-en.html', 'manifest.json']:
            assert (root / (PREFIX + name)).read_bytes() == archive.read(PREFIX + name), 'Isolated A00 output differs: ' + name
print(json.dumps({'state': 'pass', 'local_downloads_in_package': len(required),
                  'choice_variant_matches': 3419, 'isolated_a00_outputs_reproduced': 5,
                  'producer_input_used': False, 'semantic_canon_review': False,
                  'whole_program_complete': False}))
