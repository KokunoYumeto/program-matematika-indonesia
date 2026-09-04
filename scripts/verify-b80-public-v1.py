"""Anonymous readback of the B80 increment: current Pages and immutable source."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import requests

root = Path(__file__).resolve().parents[1]
base = Path('backend/course-capsule-v1/adapters/b80-capability-v1')
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
session = requests.Session()
session.headers['User-Agent'] = 'B80-public-byte-readback'
targets = [(path, 'https://kokunoyumeto.github.io/program-matematika-indonesia/' + path.removeprefix('docs/')) for path in (
    'docs/backend/b80/B80.html', 'docs/backend/b80/B80-pengajar.html',
    'docs/backend/b80/learning-map.json', 'docs/backend/b80/validation.json',
    'docs/backend/index.html', 'docs/data/course-capsule-v1/course-capsules.json',
    'docs/data/course-capsule-v1/course-capsules.jsonl', 'docs/data/course-capsule-v1/manifest.json',
    'docs/data/course-capsule-v1/validation-receipt.json',
    'docs/schema/course-capsule-v1/native-catalog-record-v1.schema.json',
    'docs/schema/course-capsule-v1/course-learning-capability-v1.schema.json')]
manifest = json.loads((root / base / 'manifest.json').read_bytes())
source_paths = {row['path'] for row in manifest['inputs'] + manifest['outputs']}
source_paths.update((base / filename).as_posix() for filename in ('manifest.json', 'validation.json', 'README.md'))
source_paths.update('scripts/' + filename for filename in (
    'native-catalog-exchange-v1.mjs', 'build-b80-capability-v1.mjs',
    'validate-b80-capability-v1.py', 'test-b80-capability-v1.mjs',
    'admit-b80-capability-v1.mjs', 'build-and-validate-b80-capability-v1.mjs'))
targets += [(path, f'https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia/{commit}/{path}') for path in sorted(source_paths)]
files = []
for path, url in targets:
    expected = (root / path).read_bytes()
    with session.get(url, timeout=(15, 45), stream=True) as response:
        response.raise_for_status()
        count = 0
        digest = hashlib.sha256()
        for data in response.iter_content(65536):
            count += len(data)
            assert count <= len(expected), path + ': unexpected larger response'
            digest.update(data)
    assert count == len(expected), path + ': size differs'
    assert digest.hexdigest() == hashlib.sha256(expected).hexdigest(), path + ': hash differs'
    files.append({'path': path, 'url': url, 'bytes': count, 'sha256': digest.hexdigest(), 'http_status': 200})
receipt = {'schema': 'b80-source-pages-readback/1', 'state': 'pass', 'recorded_at': datetime.now(timezone.utc).isoformat(),
           'source_commit': commit, 'anonymous': True, 'credentials_used': False, 'files': files,
           'github_source_and_pages_verified': True, 'zenodo_preservation_verified': False,
           'overall_program_backend_complete': False}
target = root / base / 'publication/GITHUB_SOURCE_AND_PAGES_READBACK_20260904.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'state': 'pass', 'source_commit': commit, 'files': len(files), 'bytes': sum(row['bytes'] for row in files)}))
