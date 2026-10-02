"""Narrow additive publication against a pinned public parent; no Git scan.

Default: seal an explicit plan. --publish uses the supplied credential file only
for that in-scope transaction. There is no force update, deletion, source-owner
mutation, release-asset replacement, private-access change or author contact.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from datetime import datetime, timezone
import requests

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'backend/cross-programme-v1'
API = 'https://api.github.com/repos/KokunoYumeto/program-matematika-indonesia'
RAW = 'https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia'
PLAN = PACKAGE / 'GITHUB_PUBLICATION_PLAN.json'
RECEIPT = PACKAGE / 'GITHUB_PUBLICATION_RECEIPT.json'

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def fact(path):
    b = path.read_bytes()
    return {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def seal_plan():
    reconciliation = read_json(PACKAGE / 'PUBLIC_BASELINE_RECONCILIATION.json')
    qa = read_json(PACKAGE / 'VALIDATION.json')
    browser = read_json(PACKAGE / 'BROWSER_VALIDATION.json')
    assert qa['status'] == browser['status'] == 'pass'
    files = []
    for path in reconciliation['explicit_changed_paths']:
        source = PACKAGE / 'public-staging' / path
        files.append({'path': path, 'source': source.relative_to(ROOT).as_posix(), **fact(source)})
    extra = [
        'backend/cross-programme-v1/bridge.json',
        'backend/cross-programme-v1/PRODUCTION_PROVENANCE.json',
        'backend/cross-programme-v1/PROOF_SCOPE_FINDINGS.json',
        'backend/cross-programme-v1/BUILD_RECEIPT.json',
        'backend/cross-programme-v1/VALIDATION.json',
        'backend/cross-programme-v1/BROWSER_VALIDATION.json',
        'backend/cross-programme-v1/VISUAL_INSPECTION.json',
        'backend/cross-programme-v1/PUBLIC_BASELINE_RECONCILIATION.json',
        'scripts/build-cross-programme-integration-v1.mjs',
        'scripts/stage-cross-programme-public-baseline-v1.mjs',
        'scripts/capture-cross-programme-proof-sample-v1.mjs',
        'scripts/test-cross-programme-integration-v1.mjs',
        'scripts/check-cross-programme-browser-v1.mjs',
        'scripts/publish-cross-programme-github-v1.py',
    ]
    baseline = read_json(PACKAGE / 'current-public-baseline/MANIFEST.json')
    extra += ['backend/cross-programme-v1/current-public-baseline/MANIFEST.json']
    extra += ['backend/cross-programme-v1/current-public-baseline/' + x['path'] for x in baseline['files']]
    freeze = read_json(PACKAGE / 'inputs/20261002/MANIFEST.json')
    extra += ['backend/cross-programme-v1/inputs/20261002/MANIFEST.json']
    extra += ['backend/cross-programme-v1/' + x['path'] for x in freeze['inputs']]
    sample = read_json(PACKAGE / 'proof-sample/MANIFEST.json')
    extra += ['backend/cross-programme-v1/proof-sample/MANIFEST.json','backend/cross-programme-v1/proof-sample/core/LICENSE']
    extra += ['backend/cross-programme-v1/proof-sample/' + x['path'] for x in sample['files']]
    extra += ['backend/cross-programme-v1/' + x['path'] for x in browser['captures']]
    for path in extra:
        files.append({'path': path, 'source': path, **fact(ROOT / path)})
    assert len({x['path'] for x in files}) == len(files)
    assert sum(x['bytes'] for x in files) < 24 * 1024 * 1024
    for row in files:
        assert '..' not in Path(row['path']).parts
        b = (ROOT / row['source']).read_bytes()
        if not row['path'].endswith('.png'):
            assert not re.search(rb'(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|Bearer\s+[A-Za-z0-9._-]{25,})', b)
    visual = read_json(PACKAGE / 'VISUAL_INSPECTION.json')
    assert visual['status'] == 'pass'
    for row in visual['captures']:
        assert fact(PACKAGE / row['path']) == {'bytes': row['bytes'], 'sha256': row['sha256']}
    plan = {'schema': 'cross-programme-narrow-github-plan/1', 'base_commit': reconciliation['base_commit'], 'base_tree': reconciliation['base_tree'], 'files': files, 'scope': 'Add bilingual reading routes and exact source-bound dependency sidecar, not completed proof closure', 'force': False, 'deletions': [], 'new_corpus_owner': False, 'model': 'gpt-6.1-sol', 'effort': 'ultra'}
    save(PLAN, plan)
    print(json.dumps({'state': 'explicit_plan_sealed', 'files': len(files), 'bytes': sum(x['bytes'] for x in files), 'base_commit': plan['base_commit']}), flush=True)
    return plan

def request_json(session, method, suffix, **kwargs):
    response = session.request(method, API + suffix, timeout=(15, 120), **kwargs)
    if not response.ok:
        raise RuntimeError(f'GitHub {method} {suffix}: HTTP {response.status_code}; no broad retry')
    return response.json()

def publish(plan, credential_file):
    if RECEIPT.exists():
        receipt = read_json(RECEIPT)
        assert receipt['plan_sha256'] == fact(PLAN)['sha256'], 'Never reuse a receipt for changed bytes'
        assert receipt.get('commit'), 'Incomplete transaction must be reconciled explicitly, not restarted'
        verify(plan, receipt)
        return
    if credential_file and Path(credential_file).is_file():
        text = Path(credential_file).read_text(encoding='utf-8-sig')
        candidates = list(dict.fromkeys(re.findall(r'github_pat_[A-Za-z0-9_]+|ghp_[A-Za-z0-9]+', text)))
    else:
        # Read the already authenticated CLI's token quietly in this process.
        # Never call auth login, open a browser, print the token, or save it.
        gh = shutil.which('gh')
        assert gh, 'No existing GitHub CLI authentication route is available'
        process = subprocess.run([gh, 'auth', 'token', '--hostname', 'github.com'], capture_output=True, text=True, timeout=30, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        assert process.returncode == 0, 'Existing CLI credential retrieval failed; no remote write'
        candidates = [process.stdout.strip()]
    assert candidates, 'No GitHub credential candidate; no value is exposed'
    session = requests.Session()
    session.headers.update({'Accept': 'application/vnd.github+json', 'User-Agent': 'Open-Courses-source-preserving-integration'})
    selected = False
    for token in candidates[:2]:
        session.headers['Authorization'] = 'Bearer ' + token
        response = session.get('https://api.github.com/user', timeout=30)
        if response.ok and response.json().get('login') == 'KokunoYumeto':
            selected = True
            break
    assert selected, 'Credential authentication/account check failed; no remote write made'
    head = request_json(session, 'GET', '/git/ref/heads/main')['object']['sha']
    assert head == plan['base_commit'], 'Main changed: rebase the bounded additive plan, never force'
    tree_rows = []
    for i, row in enumerate(plan['files'], 1):
        path = ROOT / row['source']
        assert fact(path) == {'bytes': row['bytes'], 'sha256': row['sha256']}
        b = path.read_bytes()
        blob = request_json(session, 'POST', '/git/blobs', json={'content': base64.b64encode(b).decode('ascii'), 'encoding': 'base64'})
        tree_rows.append({'path': row['path'], 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
        if i % 20 == 0:
            print(json.dumps({'state': 'creating_exact_blobs', 'files': i, 'total': len(plan['files'])}), flush=True)
    tree = request_json(session, 'POST', '/git/trees', json={'base_tree': plan['base_tree'], 'tree': tree_rows})
    now = datetime.now(timezone.utc).isoformat()
    actor = {'name': 'OpenAI Codex', 'email': 'codex@users.noreply.github.com', 'date': now}
    commit = request_json(session, 'POST', '/git/commits', json={'message': 'Add bilingual core-to-advanced learning routes and source-bound dependency adapter\n\nIntegration: OpenAI Codex — GPT-6.1 Sol, Ultra effort. Preserve source authors and existing readers. Course routes are not proof certification.', 'tree': tree['sha'], 'parents': [plan['base_commit']], 'author': actor, 'committer': actor})
    receipt = {'schema': 'cross-programme-github-transaction/1', 'state': 'commit_created_ref_not_yet_updated', 'plan_sha256': fact(PLAN)['sha256'], 'parent': plan['base_commit'], 'commit': commit['sha'], 'tree': tree['sha'], 'published_paths': [x['path'] for x in plan['files']], 'deleted_paths': [], 'forced_update': False, 'model': 'gpt-6.1-sol', 'effort': 'ultra'}
    save(RECEIPT, receipt)
    assert request_json(session, 'GET', '/git/ref/heads/main')['object']['sha'] == plan['base_commit'], 'Main advanced during upload; preserve the new owner changes'
    result = request_json(session, 'PATCH', '/git/refs/heads/main', json={'sha': commit['sha'], 'force': False})
    assert result['object']['sha'] == commit['sha']
    receipt['state'] = 'public_main_updated_anonymous_readback_pending'
    save(RECEIPT, receipt)
    verify(plan, receipt)

def verify(plan, receipt):
    anonymous = requests.Session()
    anonymous.headers['User-Agent'] = 'Open-Courses-anonymous-byte-readback'
    rows = []
    for row in plan['files']:
        response = anonymous.get(RAW + '/' + receipt['commit'] + '/' + row['path'], timeout=(15, 90))
        assert response.status_code == 200, f'Anonymous readback HTTP {response.status_code}: {row["path"]}'
        b = response.content
        assert len(b) == row['bytes'] and hashlib.sha256(b).hexdigest() == row['sha256'], row['path']
        rows.append({'path': row['path'], 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(), 'http': 200})
    receipt['state'] = 'public_commit_anonymously_byte_verified_pages_pending'
    receipt['anonymous_source_readback'] = rows
    save(RECEIPT, receipt)
    print(json.dumps({'state': receipt['state'], 'commit': receipt['commit'], 'tree': receipt['tree'], 'files': len(rows)}), flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--credential-file')
    args = parser.parse_args()
    plan = seal_plan()
    if args.publish:
        publish(plan, args.credential_file)

if __name__ == '__main__':
    main()
