"""Resumable anonymous readback of this bounded integration's exact public bytes."""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import requests

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--commit', required=True)
parser.add_argument('--base-commit', required=True)
args = parser.parse_args()
for value in [args.commit, args.base_commit]:
    assert len(value) == 40 and all(c in '0123456789abcdef' for c in value)
repo = 'KokunoYumeto/program-matematika-indonesia'
scope = ['scripts', 'backend/course-capsule-v1', 'docs', 'schemas/course-capsule-v1', 'releases/lebl-learning-capability-v1']
paths = subprocess.check_output(['git', 'diff', '--name-only', '--diff-filter=AM', args.base_commit, args.commit, '--', *scope], cwd=ROOT, text=True).splitlines()
assert paths and all('..' not in Path(path).parts for path in paths)
sha = lambda data: hashlib.sha256(data).hexdigest()
expected = {path: subprocess.check_output(['git', 'show', args.commit + ':' + path], cwd=ROOT) for path in paths}
target = ROOT / 'backend/course-capsule-v1/adapters/lebl-capability-v1/publication' / ('GITHUB_READBACK_' + args.commit[:12] + '.json')
target.parent.mkdir(parents=True, exist_ok=True)
receipt = json.loads(target.read_bytes()) if target.exists() else {
    'schema': 'lebl-integration-public-readback/1', 'state': 'in_progress', 'source_commit': args.commit,
    'base_commit': args.base_commit, 'anonymous': True, 'credentials_used': False, 'files': [], 'failures': [],
    'scope': 'Changed integration source files at exact commit, and every changed docs file on GitHub Pages.'}
assert receipt['source_commit'] == args.commit and receipt['base_commit'] == args.base_commit
session = requests.Session()
session.trust_env = False
session.headers['User-Agent'] = 'lebl-capability-anonymous-readback'
def save():
    target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
def read(url, data):
    result = bytearray()
    with session.get(url, stream=True, timeout=(15, 60)) as response:
        response.raise_for_status()
        assert 'Authorization' not in response.request.headers
        for chunk in response.iter_content(65536):
            result.extend(chunk)
            assert len(result) <= len(data), 'Unexpected larger response'
    assert len(result) == len(data) and sha(result) == sha(data), 'Public bytes differ'
    return {'bytes': len(result), 'sha256': sha(result), 'http_status': 200}
response = session.get('https://api.github.com/repos/' + repo, timeout=(15, 30))
response.raise_for_status()
public = response.json()
assert public['private'] is False and public['full_name'] == repo
receipt['public_repository'] = public['html_url']
complete = {(row['surface'], row['path']) for row in receipt['files']}
receipt['failures'] = []
jobs = [('source', path, 'https://raw.githubusercontent.com/' + repo + '/' + args.commit + '/' + quote(path)) for path in paths]
jobs += [('pages', path, 'https://kokunoyumeto.github.io/program-matematika-indonesia/' + quote(path[5:])) for path in paths if path.startswith('docs/')]
for surface, path, url in jobs:
    if (surface, path) in complete:
        prior = next(r for r in receipt['files'] if (r['surface'], r['path']) == (surface, path))
        assert prior['bytes'] == len(expected[path]) and prior['sha256'] == sha(expected[path])
        continue
    try:
        fact = read(url, expected[path])
    except (requests.RequestException, AssertionError) as error:
        receipt['failures'].append({'surface': surface, 'path': path, 'error': str(error), 'url': url})
        save()
        continue
    receipt['files'].append({'surface': surface, 'path': path, 'url': url,
        'checked_utc': datetime.now(timezone.utc).isoformat(), **fact})
    save()
receipt['expected_files'] = len(jobs)
receipt['verified_files'] = len(receipt['files'])
receipt['state'] = 'pass' if not receipt['failures'] and len(receipt['files']) == len(jobs) else 'incomplete'
save()
print(json.dumps({'state': receipt['state'], 'verified': len(receipt['files']), 'expected': len(jobs), 'failures': receipt['failures']}))
raise SystemExit(0 if receipt['state'] == 'pass' else 1)
