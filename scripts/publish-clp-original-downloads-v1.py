"""Parent-guarded additive publication of existing CLP original links.

Uses the already verified hub API/readback helper; no book upload, deletion,
force update, private-repository access, or change to upstream materials.
"""
import argparse
import base64
import importlib.util
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/clp-original-downloads-v1'
PROOF = 'docs/interface/evidence/clp-original-downloads-v1.json'
VALIDATION = 'docs/interface/evidence/clp-original-downloads-validation-v1.json'
EXTRAS = [PROOF, VALIDATION, 'docs/interface/clp-original-downloads.js',
          'scripts/clp-original-downloads-v1.py', 'scripts/test-clp-original-downloads-v1.mjs',
          'scripts/publish-clp-original-downloads-v1.py']
spec = importlib.util.spec_from_file_location('hub_publication', ROOT / 'scripts/a00-portable-formats-v1/publish_hub.py')
hub = importlib.util.module_from_spec(spec); spec.loader.exec_module(hub)
hub.ROOT = ROOT; hub.OUT = OUT
hub.PLAN = OUT / 'PUBLICATION_PLAN.json'; hub.RECEIPT = OUT / 'PUBLICATION_RECEIPT.json'
baseline = hub.read(OUT / 'hub-parent/BASELINE.json')
hub.PARENT = baseline['parent']


def seal():
    if hub.PLAN.exists():
        plan = hub.read(hub.PLAN)
        assert plan['parent'] == hub.PARENT
        for row in plan['files']: assert hub.fact(row['path']) == row, 'Sealed file changed'
        return plan
    validation = hub.read(OUT / 'VALIDATION.json')
    assert validation['state'] == 'pass' and validation['parent'] == hub.PARENT
    assert validation['all_prior_resource_bindings_preserved'] and validation['unchanged_other_course_cards'] == 36
    assert len(validation['checks']) == 32 and len(validation['captures']) == 2
    for row in validation['changed']:
        assert hub.fact(row['path']) == {k:row[k] for k in ('path','bytes','sha256')}
    for row in validation['captures']:
        raw = (OUT / row['path']).read_bytes()
        assert len(raw) == row['bytes'] and hub.sha(raw) == row['sha256']
    tests = []
    for path in ['scripts/test-course-downloads-v1.mjs', 'scripts/test-multilingual-interface.mjs']:
        run = subprocess.run(['node',path], cwd=ROOT, capture_output=True, text=True,
            encoding='utf-8', timeout=180, creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        assert run.returncode == 0, 'Regression failed: '+path
        tests.append({'command':['node',path], 'exit_code':0,
                      'results':[json.loads(line) for line in run.stdout.splitlines() if line]})
    validation['regression_tests'] = tests
    validation['visual_review'] = 'Both saved 390-pixel CLP-1 original-source groups personally inspected: labels legible, links wrap, textbook and problem book remain separate, source-package uncertainty visible in both interface languages.'
    validation['publisher_intake'] = hub.fact(PROOF)
    validation['publication_helper'] = hub.fact('scripts/a00-portable-formats-v1/publish_hub.py')
    hub.save(ROOT / VALIDATION, validation)
    paths = [r['path'] for r in validation['changed']] + EXTRAS
    assert len(paths) == len(set(paths))
    files = [hub.fact(path) for path in paths]
    assert sum(r['bytes'] for r in files) < 10 * 1024 * 1024
    for path in paths:
        assert not re.search(rb'(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|Bearer\s+[A-Za-z0-9._-]{25,})',(ROOT/path).read_bytes())
    plan = {'schema':'clp-additive-hub-publication/1','parent':hub.PARENT,'files':files,'deletions':[],'force':False}
    hub.save(hub.PLAN, plan)
    return plan


def publish(plan):
    receipt = hub.read(hub.RECEIPT) if hub.RECEIPT.exists() else None
    if receipt:
        assert receipt['plan_sha256'] == hub.sha(hub.PLAN.read_bytes())
        if receipt['state'] != 'commit_created_ref_pending':
            hub.verify(plan,receipt); return
    auth = subprocess.run(['gh','auth','token','--hostname','github.com'],capture_output=True,
        text=True,timeout=30,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    assert auth.returncode == 0 and auth.stdout.strip(), 'Existing authentication unavailable'
    session = requests.Session()
    session.headers.update({'Authorization':'Bearer '+auth.stdout.strip(),
        'Accept':'application/vnd.github+json','User-Agent':'Open-Courses-CLP-link-integration'})
    head = hub.api(session,'GET','/git/ref/heads/main')['object']['sha']
    if receipt and head == receipt['commit']:
        receipt['state'] = 'public_main_updated_readback_pending';hub.save(hub.RECEIPT,receipt)
        hub.verify(plan,receipt);return
    assert head == hub.PARENT, 'Public main changed; reconcile instead of overwriting'
    if not receipt:
        old = {r['path']:r for r in baseline['files']}
        for row in plan['files']:
            r = requests.get(hub.RAW+head+'/'+row['path'],timeout=(15,60))
            if row['path'] in old:
                assert r.status_code == 200 and len(r.content) == old[row['path']]['public_parent_bytes']
                assert hub.sha(r.content) == old[row['path']]['public_parent_sha256']
            else:
                assert r.status_code == 404 or (r.status_code == 200 and hub.sha(r.content) == row['sha256']), 'Conflicting new path'
        parent = hub.api(session,'GET','/git/commits/'+head)
        blobs = []
        for row in plan['files']:
            assert hub.fact(row['path']) == row
            blob = hub.api(session,'POST','/git/blobs',json={'content':base64.b64encode((ROOT/row['path']).read_bytes()).decode('ascii'),'encoding':'base64'})
            blobs.append({'path':row['path'],'mode':'100644','type':'blob','sha':blob['sha']})
        tree = hub.api(session,'POST','/git/trees',json={'base_tree':parent['tree']['sha'],'tree':blobs})
        actor = {'name':'OpenAI Codex','email':'codex@users.noreply.github.com','date':datetime.now(timezone.utc).isoformat()}
        commit = hub.api(session,'POST','/git/commits',json={
            'message':'Tambahkan PDF asli dan sumber CLP 1–4 untuk pembaca bahasa Inggris\n\nDelapan PDF buku teks dan latihan dari penulis, beserta empat repositori sumber. Edisi Indonesia dan semua akses terdahulu tetap tersedia. Integrasi tautan oleh OpenAI Codex — GPT-6 Astra, upaya Ultra; tanpa penerjemahan atau perubahan buku.',
            'tree':tree['sha'],'parents':[head],'author':actor,'committer':actor})
        receipt = {'schema':'clp-additive-hub-publication-receipt/1','state':'commit_created_ref_pending',
            'parent':head,'commit':commit['sha'],'tree':tree['sha'],
            'plan_sha256':hub.sha(hub.PLAN.read_bytes()),'deletions':[],'forced_update':False}
        hub.save(hub.RECEIPT,receipt)
    assert hub.api(session,'GET','/git/ref/heads/main')['object']['sha'] == hub.PARENT
    result = hub.api(session,'PATCH','/git/refs/heads/main',json={'sha':receipt['commit'],'force':False})
    assert result['object']['sha'] == receipt['commit']
    receipt['state'] = 'public_main_updated_readback_pending';hub.save(hub.RECEIPT,receipt)
    hub.verify(plan,receipt)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    if args.verify:hub.verify(hub.read(hub.PLAN),hub.read(hub.RECEIPT))
    else:
        plan=seal()
        if args.publish:publish(plan)
        else:print(json.dumps({'state':'sealed','files':len(plan['files'])}))
