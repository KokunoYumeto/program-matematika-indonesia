"""Publish the additive A00 reading/download links against their exact parent.

No native book changes, repository scan, deletion, force push or access change.
The two modes are an idempotent publication transaction and anonymous readback.
"""
import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/a00-portable-formats-v1'
PARENT = '540e24a71d351c2573d81ab33632b1bb5d1d7384'
LANGUAGE = os.environ.get('A00_HUB_LANGUAGE', 'id')
assert LANGUAGE in ('id', 'en')
if LANGUAGE == 'en':
    OUT = ROOT / 'outputs/a00-english-portable-formats-v1'
    PARENT = json.loads((OUT / 'hub-parent/BASELINE.json').read_text(encoding='utf-8'))['parent']
API = 'https://api.github.com/repos/KokunoYumeto/program-matematika-indonesia'
RAW = 'https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia/'
PAGES = 'https://kokunoyumeto.github.io/program-matematika-indonesia/'
PLAN = OUT / 'HUB_PUBLICATION_PLAN.json'
RECEIPT = OUT / 'HUB_PUBLICATION_RECEIPT.json'
VALIDATION = 'docs/interface/evidence/a00-hub-integration-validation.json'
EDITION_EVIDENCE = 'docs/interface/evidence/a00-portable-formats.json'
EXTRAS = [
    'docs/interface/evidence/a00-portable-formats.json', VALIDATION,
    'scripts/a00-portable-formats-v1/integrate.py',
    'scripts/a00-portable-formats-v1/restore_hub_navigation.py',
    'scripts/a00-portable-formats-v1/check_hub_additive.mjs',
    'scripts/a00-portable-formats-v1/check_hub_browser.mjs',
    'scripts/a00-portable-formats-v1/capture_hub_parent.py',
    'scripts/a00-portable-formats-v1/publish_hub.py',
]
if LANGUAGE == 'en':
    VALIDATION = 'docs/interface/evidence/a00-english-hub-integration-validation.json'
    EDITION_EVIDENCE = 'docs/interface/evidence/a00-english-portable-formats.json'
    EXTRAS = [EDITION_EVIDENCE, VALIDATION,
              'scripts/a00-portable-formats-v1/integrate_english.py']


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fact(path):
    raw = (ROOT / path).read_bytes()
    return {'path': path, 'bytes': len(raw), 'sha256': sha(raw)}


def seal():
    if PLAN.exists():
        plan = read(PLAN)
        assert plan['parent'] == PARENT
        for row in plan['files']:
            assert fact(row['path']) == row, 'Changed sealed file: ' + row['path']
        return plan
    additive = read(OUT / 'HUB_ADDITIVE_CHECK.json')
    browser = read(OUT / 'HUB_BROWSER_CHECK.json')
    assert additive['state'] == browser['state'] == 'pass'
    assert additive['parent'] == PARENT
    if LANGUAGE == 'id':
        assert len(additive['changed']) == 16
    else:
        assert {'docs/en/index.html', 'docs/en/downloads/index.html',
                'docs/interface/learner-access-manifest.json',
                'docs/interface/supplemental-readers.js'}.issubset({row['path'] for row in additive['changed']})
    assert len(browser['checks']) == 32
    for row in additive['changed']:
        assert fact(row['path']) == {k: row[k] for k in ('path', 'bytes', 'sha256')}
    for row in browser['captures']:
        raw = (OUT / row['path']).read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    proof = read(ROOT / EDITION_EVIDENCE)
    for name, identity in proof['evidence_receipts'].items():
        raw = (OUT / name).read_bytes()
        assert identity == {'bytes': len(raw), 'sha256': sha(raw)}
    tests = []
    for path in ['scripts/test-course-downloads-v1.mjs', 'scripts/test-multilingual-interface.mjs',
                 'scripts/a00-portable-formats-v1/check_hub_additive.mjs']:
        result = subprocess.run(['node', path], cwd=ROOT, capture_output=True, text=True,
                                encoding='utf-8', timeout=180,
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        assert result.returncode == 0, 'Validation failed: ' + path
        tests.append({'command': ['node', path], 'exit_code': 0,
                      'outputs': [json.loads(line) for line in result.stdout.splitlines() if line]})
    assert read(OUT / 'HUB_ADDITIVE_CHECK.json') == additive
    report = {
        'schema': 'a00-additive-hub-validation/1', 'state': 'pass', 'parent': PARENT,
        'model': 'gpt-6-astra', 'effort': 'ultra',
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'scope': ('Original English A00 formats in both interfaces; existing Indonesian resources preserved; no new translation or programme completion.' if LANGUAGE == 'en' else 'Indonesian A00 formats in both language interfaces; not an English translation or whole-program completion.'),
        'changed_file_identities': additive['changed'],
        'preservation': {k: additive[k] for k in ['resource_data', 'cardChecks', 'unchanged_other_navigation_rows']},
        'regression_tests': tests, 'browser_validation': browser,
        'visual_review': ('Both saved 390-pixel English A00 format groups inspected: readable links, PDF/LaTeX/ZIP/EPUB order and explicit English content labels in both interfaces.' if LANGUAGE == 'en' else 'Both saved 390-pixel A00 format groups inspected: readable links, correct format order and explicit Indonesian content labels in both interfaces.'),
        'source_edition_evidence': fact(EDITION_EVIDENCE),
        'limitations': ['Browser checks cover the prepared local pages.',
                       'No new mathematical or linguistic review of the textbook.',
                       'Anonymous deployed-byte verification is a separate publication receipt.'],
    }
    save(ROOT / VALIDATION, report)
    paths = [row['path'] for row in additive['changed']] + EXTRAS
    assert len(paths) == len(set(paths))
    rows = [fact(path) for path in paths]
    assert sum(row['bytes'] for row in rows) < 10 * 1024 * 1024
    for path in paths:
        raw = (ROOT / path).read_bytes()
        assert not re.search(rb'(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|Bearer\s+[A-Za-z0-9._-]{25,})', raw)
    plan = {'schema': 'a00-additive-hub-publication/1', 'parent': PARENT,
            'files': rows, 'deletions': [], 'force': False}
    save(PLAN, plan)
    return plan


def api(session, method, suffix, **kwargs):
    response = session.request(method, API + suffix, timeout=(15, 60), **kwargs)
    if not response.ok:
        raise RuntimeError(f'GitHub {method} {suffix}: HTTP {response.status_code}')
    return response.json()


def verify(plan, receipt):
    anonymous = requests.Session()
    anonymous.headers['User-Agent'] = 'Open-Courses-A00-public-readback'
    receipt['anonymous_source_readback'] = []
    for row in plan['files']:
        response = anonymous.get(RAW + receipt['commit'] + '/' + row['path'], timeout=(15, 60))
        assert response.status_code == 200, 'Source readback failed: ' + row['path']
        assert len(response.content) == row['bytes'] and sha(response.content) == row['sha256'], row['path']
        receipt['anonymous_source_readback'].append({**row, 'http': 200})
        save(RECEIPT, receipt)
    pages = []
    for row in plan['files']:
        if not row['path'].startswith('docs/'):
            continue
        url = PAGES + row['path'][5:]
        response = anonymous.get(url, headers={'Cache-Control': 'no-cache'}, timeout=(15, 60))
        pages.append({'url': url, 'http': response.status_code, 'bytes': len(response.content),
                      'sha256': sha(response.content),
                      'matches': response.status_code == 200 and len(response.content) == row['bytes']
                                 and sha(response.content) == row['sha256']})
    receipt['pages_readback'] = pages
    receipt['state'] = ('public_source_and_pages_verified' if all(row['matches'] for row in pages)
                        else 'public_source_verified_pages_deployment_pending')
    receipt['checked_utc'] = datetime.now(timezone.utc).isoformat()
    save(RECEIPT, receipt)
    print(json.dumps({'state': receipt['state'], 'commit': receipt['commit'],
                      'source_files': len(plan['files']), 'pages_verified': sum(row['matches'] for row in pages)}), flush=True)


def publish(plan):
    receipt = read(RECEIPT) if RECEIPT.exists() else None
    if receipt:
        assert receipt['plan_sha256'] == sha(PLAN.read_bytes())
        if receipt['state'] != 'commit_created_ref_pending':
            verify(plan, receipt)
            return
    auth = subprocess.run(['gh', 'auth', 'token', '--hostname', 'github.com'],
                          capture_output=True, text=True, timeout=30,
                          creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    assert auth.returncode == 0 and auth.stdout.strip(), 'Existing authentication unavailable'
    session = requests.Session()
    session.headers.update({'Authorization': 'Bearer ' + auth.stdout.strip(),
                            'Accept': 'application/vnd.github+json', 'User-Agent': 'Open-Courses-A00-hub-integration'})
    head = api(session, 'GET', '/git/ref/heads/main')['object']['sha']
    if receipt and head == receipt['commit']:
        receipt['state'] = 'public_main_updated_readback_pending'
        save(RECEIPT, receipt)
        verify(plan, receipt)
        return
    assert head == PARENT, 'Public main changed; reconcile instead of overwriting'
    if not receipt:
        baseline = {row['path']: row for row in read(OUT / 'hub-parent/BASELINE.json')['files']}
        for row in plan['files']:
            response = requests.get(RAW + PARENT + '/' + row['path'], timeout=(15, 60))
            if row['path'] in baseline:
                old = baseline[row['path']]
                assert response.status_code == 200
                assert len(response.content) == old['public_parent_bytes']
                assert sha(response.content) == old['public_parent_sha256']
            else:
                assert response.status_code == 404 or (response.status_code == 200 and sha(response.content) == row['sha256']), 'New path already has different content: ' + row['path']
        parent = api(session, 'GET', '/git/commits/' + head)
        blobs = []
        for row in plan['files']:
            assert fact(row['path']) == row, 'Changed after seal: ' + row['path']
            blob = api(session, 'POST', '/git/blobs', json={
                'content': base64.b64encode((ROOT / row['path']).read_bytes()).decode('ascii'), 'encoding': 'base64'})
            blobs.append({'path': row['path'], 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
        tree = api(session, 'POST', '/git/trees', json={'base_tree': parent['tree']['sha'], 'tree': blobs})
        actor = {'name': 'OpenAI Codex', 'email': 'codex@users.noreply.github.com', 'date': datetime.now(timezone.utc).isoformat()}
        commit = api(session, 'POST', '/git/commits', json={
            'message': ('Tambahkan edisi Praljabar bahasa Inggris dalam PDF, LaTeX dan EPUB\n\n75 modul dengan sumber lengkap yang dapat dibangun ulang. Edisi Bahasa Indonesia dan akses terdahulu tetap tersedia. Integrasi oleh OpenAI Codex — GPT-6 Astra, upaya Ultra.' if LANGUAGE == 'en' else 'Tambahkan unduhan PDF, LaTeX, sumber, dan EPUB Praljabar\n\nFormat Bahasa Indonesia tersedia dari kedua antarmuka. Integrasi oleh OpenAI Codex — GPT-6 Astra, upaya Ultra; sumber asli dan akses terdahulu dipertahankan.'),
            'tree': tree['sha'], 'parents': [head], 'author': actor, 'committer': actor})
        receipt = {'schema': 'a00-additive-hub-publication-receipt/1', 'state': 'commit_created_ref_pending',
                   'parent': head, 'commit': commit['sha'], 'tree': tree['sha'],
                   'plan_sha256': sha(PLAN.read_bytes()), 'deletions': [], 'forced_update': False}
        save(RECEIPT, receipt)
    assert api(session, 'GET', '/git/ref/heads/main')['object']['sha'] == PARENT
    result = api(session, 'PATCH', '/git/refs/heads/main', json={'sha': receipt['commit'], 'force': False})
    assert result['object']['sha'] == receipt['commit']
    receipt['state'] = 'public_main_updated_readback_pending'
    save(RECEIPT, receipt)
    verify(plan, receipt)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        verify(read(PLAN), read(RECEIPT))
    else:
        plan = seal()
        if args.publish:
            publish(plan)
        else:
            print(json.dumps({'state': 'plan_sealed', 'files': len(plan['files'])}), flush=True)


if __name__ == '__main__':
    main()
