"""Read committed bytes and anonymously verify the exact public increment."""
import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import requests

root = Path(__file__).resolve().parents[1]
arguments = argparse.ArgumentParser()
arguments.add_argument('--commit', required=True)
options = arguments.parse_args()
assert re.fullmatch('[0-9a-f]{40}', options.commit)
base_url = 'https://kokunoyumeto.github.io/program-matematika-indonesia/'
raw_url = 'https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia/' + options.commit + '/'
pages = ['backend/coverage.html', 'backend/program-backend-coverage.json', 'backend/index.html',
         'backend/b80/B80.html', 'backend/b80/B80-pengajar.html', 'backend/b80/learning-map.json', 'backend/b80/validation.json']
sources = ['.gitattributes', 'package.json', 'scripts/build-program-backend-coverage-v1.mjs',
           'scripts/test-program-backend-coverage-v1.py', 'scripts/package-b80-capability-v1.py',
           'scripts/verify-b80-public-v1.py', 'scripts/verify-program-backend-public-v1.py',
           'scripts/validate-course-capsule-site-v1.mjs', 'docs/backend/index.template.html',
           'backend/course-capsule-v1/generated/program-backend-coverage-v1.json',
           'backend/course-capsule-v1/validation/SITE_VALIDATION_RECEIPT.json',
           'backend/course-capsule-v1/validation/PROGRAM_BACKEND_COVERAGE_VALIDATION.json',
           'backend/course-capsule-v1/adapters/b80-capability-v1/publication/GITHUB_SOURCE_AND_PAGES_READBACK_20260904.json',
           'releases/b80-learning-capability-v1/PACKET_BUILD_RECEIPT.json',
           'releases/b80-learning-capability-v1/B80_NATIVE_LEARNING_CAPABILITY_V1.zip']
targets = [('docs/' + path, base_url + path, 'pages') for path in pages]
targets += [(path, raw_url + path, 'immutable_source') for path in sources]
session = requests.Session()
session.trust_env = False  # Do not obtain ambient credentials from netrc.
session.headers['User-Agent'] = 'program-backend-anonymous-readback'
results = []
for path, url, kind in targets:
    expected = subprocess.check_output(['git', 'show', options.commit + ':' + path], cwd=root)
    digest, count = hashlib.sha256(), 0
    with session.get(url, stream=True, timeout=(15, 45)) as response:
        response.raise_for_status()
        assert 'Authorization' not in response.request.headers
        for chunk in response.iter_content(65536):
            count += len(chunk)
            assert count <= len(expected), path + ': larger than committed artifact'
            digest.update(chunk)
    assert count == len(expected), path + ': size differs'
    assert digest.hexdigest() == hashlib.sha256(expected).hexdigest(), path + ': hash differs'
    results.append({'path': path, 'url': url, 'kind': kind, 'http_status': 200,
                    'bytes': count, 'sha256': digest.hexdigest()})
receipt = {'schema': 'program-backend-public-readback/1', 'state': 'pass',
           'recorded_at': datetime.now(timezone.utc).isoformat(), 'source_commit': options.commit,
           'anonymous': True, 'ambient_credentials_disabled': True, 'files': results,
           'zenodo_preservation_verified': False, 'overall_program_backend_complete': False}
target = root / 'backend/course-capsule-v1/validation' / ('PROGRAM_BACKEND_PUBLIC_READBACK_20260904_' + options.commit[:8] + '.json')
target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({'state': 'pass', 'files': len(results), 'bytes': sum(row['bytes'] for row in results),
                  'source_commit': options.commit, 'receipt': target.name}))
