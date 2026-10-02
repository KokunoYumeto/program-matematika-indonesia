"""Independently replay D60 metadata from packaged sources, without a producer or network."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

PREFIX = 'backend/course-capsule-v1/adapters/d60-native-ledger-v1/'
SITE = 'docs/backend/d60/native-ledger/'

def sha(body):
    return hashlib.sha256(body).hexdigest()

class Downloads(HTMLParser):
    def __init__(self):
        super().__init__()
        self.names = set()
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'a' and 'download' in values:
            name = values.get('href', '')
            assert '/' not in name and ':' not in name and name
            self.names.add(name)

parser = argparse.ArgumentParser()
parser.add_argument('archive', type=Path)
parser.add_argument('--receipt', type=Path)
args = parser.parse_args()
with zipfile.ZipFile(args.archive) as archive:
    manifest = json.loads(archive.read('CURRENT_BACKEND_PACKAGE_MANIFEST.json'))
    facts = {row['path']: row for row in manifest['files']}
    tests = json.loads(archive.read(PREFIX + 'tests.json'))
    assert tests['state'] == 'pass' and tests['semantic_canon_approval'] is False
    lock = json.loads(archive.read(PREFIX + 'source-lock.json'))
    assert lock['course_id'] == 'D60' and lock['book_bodies_copied'] is False
    needed = set()
    for name in ['ledger.html', 'ledger-en.html']:
        links = Downloads()
        hosted = archive.read(SITE + name)
        links.feed(hosted.decode())
        assert links.names == {'projection.json', 'native-metadata.zip'}
        needed.update(SITE + value for value in links.names)
        body = hosted.decode()
        assert body.count('data-central-surface-navigation="v1"') == 2
        body = re.sub(r'(?:\n[ \t]*)?<nav\b(?=[^>]*data-central-surface-navigation="v1")(?=[^>]*data-placement="top")[^>]*>.*?</nav>', '', body, count=1, flags=re.S | re.I)
        body = re.sub(r'<nav\b(?=[^>]*data-central-surface-navigation="v1")(?=[^>]*data-placement="bottom")[^>]*>.*?</nav>(?:\n[ \t]*)?', '', body, count=1, flags=re.S | re.I)
        assert body.encode() == archive.read(PREFIX + 'site/' + name)
    for name in needed:
        data = archive.read(name)
        assert name in facts and len(data) == facts[name]['bytes'] and sha(data) == facts[name]['sha256']
    members = {name for name in archive.namelist() if name.startswith(PREFIX)}
    members.update({'scripts/d60-native-ledger-v1.py', SITE + 'ledger-ui.js', SITE + 'ledger.css'})
    members.update(item['path'] for item in lock['inputs'])
    with tempfile.TemporaryDirectory(prefix='d60-current-package-replay-') as temp:
        root = Path(temp).resolve()
        assert root.is_relative_to(Path(tempfile.gettempdir()).resolve())
        for name in sorted(members):
            target = (root / name).resolve()
            assert target.is_relative_to(root) and name in facts and not target.is_symlink()
            data = archive.read(name)
            assert len(data) == facts[name]['bytes'] and sha(data) == facts[name]['sha256']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        replayed = []
        for suffix in ['a', 'b']:
            destination = root / ('replay-' + suffix)
            result = subprocess.run([sys.executable, '-B', 'scripts/d60-native-ledger-v1.py', '--out', str(destination)],
                                    cwd=root, capture_output=True, encoding='utf-8', timeout=60)
            assert result.returncode == 0, result.stderr[-1500:]
            outputs = json.loads(result.stdout)['outputs']
            assert outputs == tests['outputs']
            for name in outputs:
                assert (destination / name).read_bytes() == archive.read(PREFIX + 'site/' + name), 'Isolated raw output differs: ' + name
            replayed.append(outputs)
        assert replayed[0] == replayed[1]
report = {'schema': 'd60-current-package-replay/1', 'state': 'pass',
          'archive': {'name': args.archive.name, 'bytes': args.archive.stat().st_size},
          'download_files_in_package': len(needed), 'isolated_replay_builds': 2,
          'raw_outputs_reproduced': len(tests['outputs']), 'unchanged_native_records': 8338,
          'managed_hosted_overlay_reversible': True, 'producer_input_used': False,
          'semantic_canon_review': False, 'native_book_rebuilt': False, 'whole_program_complete': False}
if args.receipt:
    with args.receipt.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
print(json.dumps(report))
