"""Publish only the new reader and exact B40 navigation, preserving prior routes.

No Git scan, force push, path deletion, existing reader replacement or Zenodo draft.
The preserved foundation deployer supplies authentication and read-only helpers.
"""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import zipfile

LOG = Path(__file__).resolve().parent
BASE = LOG.parent
WORK = BASE / 'b40-expanded-public-20261002'
spec = importlib.util.spec_from_file_location('b40_prior_deploy', LOG / 'deploy_b40_foundations_public_20261002.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
prior.WORK = WORK
sha, jb, fact, save, get, api = prior.sha, prior.jb, prior.fact, prior.save, prior.get, prior.api
API, RAW, ORIGIN = prior.API, prior.RAW, prior.ORIGIN
PREFIX = 'docs/en/readers/hefferon-linear-algebra/'
URL = ORIGIN + 'en/readers/hefferon-linear-algebra/'
TAG = 'b40-original-en-2026.10.02-28-sections'
ASSET_ROOT = 'https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/' + TAG + '/'
LABEL = 'Original English — 28 sections through Laplace’s Formula (partial book)'


def json_read(path):
    return json.loads(path.read_bytes())


def audit_package():
    seal = json_read(WORK / 'SOURCE_SEAL.json')
    qa = json_read(WORK / 'BROWSER_QA.json')
    visual = json_read(WORK / 'VISUAL_INSPECTION.json')
    assert seal['state'] == qa['state'] == visual['state'] == 'PASS'
    assert qa['build_receipt_sha256'] == sha((WORK / 'BUILD_RECEIPT.json').read_bytes())
    assert visual['browser_qa_sha256'] == sha((WORK / 'BROWSER_QA.json').read_bytes())
    for row in qa['captures']:
        assert fact((WORK / row['path']).read_bytes()) == {k: row[k] for k in ['bytes', 'sha256']}
    for field in ['source_zip', 'manifest']:
        row = seal[field]
        assert fact((WORK / row['path']).read_bytes()) == {k: row[k] for k in ['bytes', 'sha256']}
    bad_paths, secrets = [], []
    with zipfile.ZipFile(WORK / seal['source_zip']['path']) as archive:
        assert archive.testzip() is None
        for name in archive.namelist():
            if Path(name).suffix.lower() not in ['.json', '.py', '.mjs', '.js', '.txt', '.html', '.md', '.tex']:
                continue
            raw = archive.read(name)
            if re.search(rb'(?:[A-Za-z]:[\\/]+Users[\\/]|/home/|/mnt/c/Users/)', raw, re.I):
                bad_paths.append(name)
            if re.search(rb'(?:github_pat_[A-Za-z0-9_]{35,}|ghp_[A-Za-z0-9]{30,})', raw):
                secrets.append(name)
    report = {'state': 'PASS' if not bad_paths and not secrets else 'FAIL', 'private_path_files': bad_paths, 'credential_pattern_files': secrets, 'source_zip_sha256': seal['source_zip']['sha256'], 'native_authority_zip_not_rewritten': True}
    save(WORK / 'PACKAGE_PRIVACY_CHECK.json', report)
    assert report['state'] == 'PASS', 'source package privacy check failed; see sanitized file-only report'
    return seal


def stage():
    assert not (WORK / 'PUBLICATION_RECEIPT.json').exists(), 'resume recorded transaction'
    audit_package()
    latest = json.loads(get(API + '/commits/main'))
    parent, tree = latest['sha'], latest['commit']['tree']['sha']
    entries, baselines = {}, []

    def add(path, data):
        assert path not in entries
        target = WORK / 'publication-staging' / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        entries[path] = {'path': path, 'local': target.relative_to(WORK).as_posix(), **fact(data)}

    def baseline(path):
        raw = get(RAW + '/' + parent + '/' + path)
        target = WORK / 'public-baseline' / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        baselines.append({'path': path, **fact(raw)})
        return raw

    manifest = json_read(WORK / 'public/READER_MANIFEST.json')
    for row in manifest['public_files']:
        if row['path'] == 'COMPLETE_SOURCE.zip':
            continue
        raw = (WORK / 'public' / row['path']).read_bytes()
        assert fact(raw) == {k: row[k] for k in ['bytes', 'sha256']}
        add(PREFIX + row['path'], raw)
    add(PREFIX + 'READER_MANIFEST.json', (WORK / 'public/READER_MANIFEST.json').read_bytes())
    # Refuse a collision with another existing release at this route.
    with prior.requests.get(RAW + '/' + parent + '/' + PREFIX + 'index.html', timeout=30) as response:
        assert response.status_code == 404, 'expanded route already exists: reconcile, never overwrite'
    index_fact = fact((WORK / 'public/index.html').read_bytes())
    zip_fact = fact((WORK / 'public/COMPLETE_SOURCE.zip').read_bytes())
    locales = 'docs/interface/locales.js'
    original = baseline(locales).decode()
    start = original.index('export const englishResources = {')
    match = re.search(r'  B40: \[.*?\n  \],', original[start:], re.S)
    assert match and 'hefferon-foundations/' in match.group()
    block = match.group()
    assert 'hefferon-linear-algebra/' not in block
    new_rows = "\n    englishMirror(" + json.dumps(LABEL, ensure_ascii=False) + ", '" + URL + "', 'HTML', " + json.dumps(index_fact) + "),\n    englishMirror('Offline original English — 28 sections and complete editable source', '" + ASSET_ROOT + "COMPLETE_SOURCE.zip', 'HTML ZIP', " + json.dumps({**zip_fact, 'offlineAfterDownload': True}) + "),"
    replacement = block.replace('B40: [', 'B40: [' + new_rows, 1)
    changed = original[:start+match.start()] + replacement + original[start+match.end():]
    assert changed.replace(replacement, block, 1) == original
    add(locales, changed.encode())

    hosted = '<a class="resource-link primary" href="'+URL+'" data-content-language="en" hreflang="en" data-access-role="hosted-reader" data-original-source="program-mirror"><span lang="en">'+LABEL+'</span><small>HTML · English</small></a>'
    offline = '<a class="resource-link" href="'+ASSET_ROOT+'COMPLETE_SOURCE.zip" data-content-language="en" hreflang="en" data-access-role="offline-copy" data-original-source="program-mirror"><span lang="en">Offline original English — 28 sections and complete editable source</span><small>HTML ZIP · English</small></a>'
    for name in ['index.html', 'learning-map.html', 'learning-map-paired.html']:
        path = 'docs/en/' + name
        original = baseline(path).decode()
        match = re.search(r'<article\b[^>]*id="course-B40".*?</article>', original, re.S)
        assert match
        block = match.group()
        group = re.search(r'<section class="resource-group" data-access-group="hosted-reader">.*?</section>', block, re.S)
        assert group and 'hefferon-foundations/' in group.group() and 'hefferon-linear-algebra/' not in block
        current = group.group().replace('resource-link primary', 'resource-link')
        header = '<h4>Program-hosted reader</h4>'
        assert current.count(header) == 1
        new_group = current.replace(header, header+hosted+offline, 1)
        new_block = block[:group.start()] + new_group + block[group.end():]
        changed = original[:match.start()] + new_block + original[match.end():]
        assert changed.replace(new_block, block, 1) == original
        add(path, changed.encode())
    for language in ['en', 'id']:
        path = 'docs/'+language+'/programme/index.html'
        original = baseline(path).decode()
        match = re.search(r'<section id="core-B40">.*?</section>', original, re.S)
        assert match
        block = match.group()
        assert 'data-b40-expanded=' not in block
        label = 'Read original English — 28 sections through Laplace’s Formula (partial book)' if language == 'en' else 'Baca teks asli berbahasa Inggris — 28 bagian hingga Rumus Laplace (sebagian buku)'
        link = '<p><a data-b40-expanded="v1" href="'+URL+'" hreflang="en">'+label+'</a></p>'
        new_block = block.replace('</h3>', '</h3>'+link, 1)
        changed = original[:match.start()] + new_block + original[match.end():]
        assert changed.replace(new_block, block, 1) == original
        add(path, changed.encode())
    path = 'docs/interface/learner-access-manifest.json'
    access = json.loads(baseline(path))
    other_courses = jb({k:v for k,v in access['courses'].items() if k != 'B40'})
    id_record = jb(access['courses']['B40']['id'])
    english = access['courses']['B40']['en']
    assert any('hefferon-foundations/' in r['url'] for r in english['program_hosted_reader']['resources'])
    assert not any(r['url'] == URL for r in english['program_hosted_reader']['resources'])
    def resource(label, url, role, kind, identity):
        return {'access_role':role,'authority_role':'program-mirror','relation_to_source':'offline-copy-of' if role=='offline-copy' else 'mirror-of','content_language':'en','media_type':kind,'url':url,'label':label,'label_language':'en','primary':role=='hosted-reader','offline_after_download':role=='offline-copy',**identity,'source_body_bytes':None,'source_body_sha256':None,'hosted_navigation_overlay':None,'coverage':'28 linked sections through Laplace’s Formula; not the whole book'}
    for row in english['program_hosted_reader']['resources']:
        row['primary'] = False
    english['program_hosted_reader']['resources'].insert(0, resource(LABEL,URL,'hosted-reader','HTML',index_fact))
    english['offline_copies'].insert(0,resource('Offline original English — 28 sections and complete editable source',ASSET_ROOT+'COMPLETE_SOURCE.zip','offline-copy','HTML ZIP',zip_fact))
    assert jb({k:v for k,v in access['courses'].items() if k != 'B40'}) == other_courses
    assert jb(access['courses']['B40']['id']) == id_record
    add(path,jb(access))
    for name in ['BUILD_RECEIPT.json','SOURCE_SEAL.json','BROWSER_QA.json','VISUAL_INSPECTION.json','PUBLIC_EXTRACTION_QA.json','PACKAGE_PRIVACY_CHECK.json','RUNTIME_PROVENANCE.json']:
        add('backend/b40-expanded-public-20261002/'+name, (WORK/name).read_bytes())
    for name in ['build_b40_expanded_public_20261002.py','seal_b40_expanded_public_20261002.py','test_b40_expanded_public_20261002.mjs',Path(__file__).name,'deploy_b40_foundations_public_20261002.py']:
        add('scripts/b40-expanded/'+name, (LOG/name).read_bytes())
    plan = {'schema':'b40-expanded-publication-plan/1','base_commit':parent,'base_tree':tree,'files':list(entries.values()),'public_baselines':baselines,'deleted_paths':[],'force':False,'preserved_prior_reader_prefix':'docs/en/readers/hefferon-foundations/','scope':'28 selected sections, not full book','model':'gpt-6-astra','effort':'ultra'}
    save(WORK/'PUBLICATION_PLAN.json',plan)
    print(json.dumps({'state':'staged','base':parent,'files':len(entries),'bytes':sum(r['bytes'] for r in entries.values())}),flush=True)
    return plan


def release(session, plan):
    path = WORK/'SOURCE_RELEASE_RECEIPT.json'
    response = session.get(API+'/releases/tags/'+TAG,timeout=30)
    assert response.status_code in [200,404]
    if response.status_code == 200:
        obj = response.json()
        assert path.exists() and json_read(path)['release_id'] == obj['id'], 'unowned tag collision'
    else:
        assert not path.exists(), 'do not duplicate a prior release'
        body = ('Read Jim Hefferon’s original English Linear Algebra in 28 linked sections, from linear systems through Laplace’s Formula. This is a partial-book reading edition, not the complete textbook and not an Everyday-English rewrite.\n\nRead online: '+URL+'\nOriginal author’s complete book, answers and Sage lab: https://hefferon.net/linearalgebra/\n\nThe reader preserves 836 exercises, 834 supplied answers and two explicit original-answer absences. Download the cumulative editable LaTeX first, then the complete source/offline-reader ZIP. Each section’s original LaTeX is also directly downloadable. The ZIP includes the complete original editable source tree and exact HTML replay inputs. The HTML reads offline without JavaScript or downloaded fonts. No new PDF or native TeX build is claimed.\n\nOriginal mathematics: Jim Hefferon; CC BY-SA 2.5 option with all component credits and terms retained. Source-preserving rebuild, navigation, indexing, packaging and current deterministic checks: OpenAI Codex — GPT-6 Astra, Ultra effort. Earlier intermediate runtime identity is unverified and is not reassigned. No human review or exhaustive proof certification is claimed.\n\nBahasa Indonesia: Edisi bacaan ini memuat 28 bagian teks asli berbahasa Inggris, bukan keseluruhan buku atau terjemahan baru. Tersedia sumber LaTeX kumulatif, sumber tiap bagian, dan ZIP sumber lengkap beserta pembaca luring. Matematika asli: Jim Hefferon; opsi lisensi CC BY-SA 2.5 dan ketentuan setiap komponen tetap berlaku. Pembangunan ulang, navigasi, pengindeksan, pengemasan, dan pemeriksaan deterministik: OpenAI Codex — GPT-6 Astra, tingkat upaya Ultra. Tidak ada klaim peninjauan manusia.')
        obj = api(session,'POST','/releases',json={'tag_name':TAG,'target_commitish':plan['base_commit'],'name':'Linear algebra — original English: 28 sections and editable source','body':body,'draft':True,'prerelease':False,'make_latest':'false'})
        save(path,{'schema':'b40-expanded-source-release/1','state':'draft_assets_pending','release_id':obj['id'],'tag':TAG,'assets':[]})
    receipt = json_read(path)
    required = [('00-linear-algebra-cumulative.tex',WORK/'public/sources/00-linear-algebra-cumulative.tex','application/x-tex'),('COMPLETE_SOURCE.zip',WORK/'public/COMPLETE_SOURCE.zip','application/zip')]
    build = json_read(WORK/'BUILD_RECEIPT.json')
    required += [(f'{i:02d}-{r["section"]}.tex',WORK/'public/sources'/f'{r["section"]}.tex','application/x-tex') for i,r in enumerate(build['sections'],1)]
    required += [('READER_MANIFEST.json',WORK/'public/READER_MANIFEST.json','application/json')]
    assets = api(session,'GET','/releases/'+str(obj['id'])+'/assets?per_page=100')
    assert set(a['name'] for a in assets) <= {r[0] for r in required}, 'unexpected assets; preserve and reconcile'
    for name, source, mime in required:
        raw = source.read_bytes()
        same = [a for a in assets if a['name'] == name]
        assert len(same) <= 1
        if same:
            asset = same[0]
        else:
            url = obj['upload_url'].split('{')[0]
            assert url.startswith('https://uploads.github.com/repos/KokunoYumeto/program-matematika-indonesia/releases/')
            response = session.post(url,params={'name':name},data=raw,headers={'Content-Type':mime},timeout=(20,180))
            assert response.status_code == 201, 'asset upload HTTP '+str(response.status_code)
            asset = response.json()
            assets.append(asset)
        assert asset['state'] == 'uploaded' and asset['size'] == len(raw) and asset.get('digest') == 'sha256:'+sha(raw)
        receipt['assets'] = [a for a in receipt['assets'] if a['name'] != name] + [{'name':name,'id':asset['id'],'url':asset['browser_download_url'],**fact(raw)}]
        save(path,receipt)
        print(json.dumps({'asset_ready':name,'bytes':len(raw)}),flush=True)
    assert len(assets) == len(required) <= 100
    if obj['draft']:
        obj = api(session,'PATCH','/releases/'+str(obj['id']),json={'draft':False,'make_latest':'false'})
    assert not obj['draft']
    # Draft asset URLs use an untagged placeholder; bind their public URLs by ID.
    published_assets = api(session,'GET','/releases/'+str(obj['id'])+'/assets?per_page=100')
    for row in receipt['assets']:
        published = next(a for a in published_assets if a['id'] == row['id'])
        assert published['name'] == row['name'] and published['size'] == row['bytes']
        assert published.get('digest') == 'sha256:'+row['sha256']
        row['url'] = published['browser_download_url']
    receipt.update(state='public_anonymous_readback_pending',url=obj['html_url'])
    save(path,receipt)
    def check(row):
        raw = get(row['url'])
        assert fact(raw) == {k:row[k] for k in ['bytes','sha256']}
        return {**row,'anonymous_readback':'PASS'}
    with ThreadPoolExecutor(max_workers=3) as pool:
        receipt['assets'] = list(pool.map(check,receipt['assets']))
    receipt.update(state='public_all_assets_anonymously_verified',url=obj['html_url'])
    save(path,receipt)
    print(json.dumps({'release':receipt['url'],'verified_assets':len(receipt['assets'])}),flush=True)


def refresh_parent(session, plan):
    head = api(session,'GET','/git/ref/heads/main')['object']['sha']
    if head == plan['base_commit']:
        return plan
    for row in plan['public_baselines']:
        assert fact(get(RAW+'/'+head+'/'+row['path'])) == {k:row[k] for k in ['bytes','sha256']}, 'selected navigation changed: restage after inspection'
    latest = api(session,'GET','/git/commits/'+head)
    previous = plan['base_commit']
    plan['base_commit'], plan['base_tree'] = head, latest['tree']['sha']
    plan.setdefault('preserved_concurrent_parent_advances',[]).append({'from':previous,'to':head,'all_scoped_baselines_unchanged':True})
    save(WORK/'PUBLICATION_PLAN.json',plan)
    return plan


def verify(plan, receipt, pages=False):
    rows = [r for r in plan['files'] if not pages or r['path'].startswith('docs/')]
    def check(row):
        url = ORIGIN+row['path'][5:] if pages else RAW+'/'+receipt['commit']+'/'+row['path']
        raw = get(url)
        assert fact(raw) == {k:row[k] for k in ['bytes','sha256']}, 'public byte mismatch: '+row['path']
        return {'path':row['path'],'url':url,'http':200,**fact(raw)}
    with ThreadPoolExecutor(max_workers=4) as pool:
        checked = list(pool.map(check,rows))
    receipt['pages_readback' if pages else 'anonymous_commit_readback'] = checked
    receipt['state'] = 'public_pages_and_sources_anonymously_verified' if pages else 'public_commit_verified_pages_pending'
    save(WORK/'PUBLICATION_RECEIPT.json',receipt)
    print(json.dumps({'state':receipt['state'],'commit':receipt['commit'],'files':len(checked)}),flush=True)


def publish(plan, credential_file):
    session = prior.authenticate(credential_file)
    path = WORK/'PUBLICATION_RECEIPT.json'
    if path.exists():
        receipt = json_read(path)
        assert receipt['plan_sha256'] == sha((WORK/'PUBLICATION_PLAN.json').read_bytes())
        if receipt['state'] == 'commit_created_ref_not_updated':
            head = api(session,'GET','/git/ref/heads/main')['object']['sha']
            assert head in [receipt['parent'],receipt['commit']], 'concurrent head changed; reconcile recorded commit'
            if head == receipt['parent']:
                api(session,'PATCH','/git/refs/heads/main',json={'sha':receipt['commit'],'force':False})
        verify(plan,receipt)
        return
    plan = refresh_parent(session,plan)
    release(session,plan)
    cp_path = WORK/'BLOB_UPLOAD_CHECKPOINT.json'
    checkpoint = json_read(cp_path) if cp_path.exists() else {'schema':'github-content-addressed-upload/1','blobs':{}}
    nodes = []
    for i,row in enumerate(plan['files'],1):
        raw = (WORK/row['local']).read_bytes()
        assert fact(raw) == {k:row[k] for k in ['bytes','sha256']}
        blob_id = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if blob_id not in checkpoint['blobs']:
            with session.get(API+'/git/blobs/'+blob_id,stream=True,timeout=(15,30)) as response:
                code = response.status_code
            assert code in [200,404]
            if code == 404:
                result = api(session,'POST','/git/blobs',json={'content':base64.b64encode(raw).decode(),'encoding':'base64'})
                assert result['sha'] == blob_id
            checkpoint['blobs'][blob_id] = fact(raw)
            save(cp_path,checkpoint)
        nodes.append({'path':row['path'],'mode':'100644','type':'blob','sha':blob_id})
        if i%10 == 0:
            print(json.dumps({'uploaded_or_recovered':i,'total':len(plan['files'])}),flush=True)
    plan = refresh_parent(session,plan)
    tree = api(session,'POST','/git/trees',json={'base_tree':plan['base_tree'],'tree':nodes})
    actor = {'name':'OpenAI Codex','email':'codex@users.noreply.github.com','date':datetime.now(timezone.utc).isoformat()}
    commit = api(session,'POST','/git/commits',json={'message':'Publish 28-section original-English linear algebra reader and exact modular source\n\nPreserve existing proof URLs and all unrelated course navigation. Original mathematics: Jim Hefferon. Rebuild and integration: OpenAI Codex — GPT-6 Astra, Ultra effort.','tree':tree['sha'],'parents':[plan['base_commit']],'author':actor,'committer':actor})
    receipt = {'schema':'b40-expanded-publication/1','state':'commit_created_ref_not_updated','parent':plan['base_commit'],'commit':commit['sha'],'tree':tree['sha'],'plan_sha256':sha((WORK/'PUBLICATION_PLAN.json').read_bytes()),'deleted_paths':[],'force':False}
    save(path,receipt)
    assert api(session,'GET','/git/ref/heads/main')['object']['sha'] == plan['base_commit'],'concurrent change; recorded commit retained'
    api(session,'PATCH','/git/refs/heads/main',json={'sha':commit['sha'],'force':False})
    receipt['state'] = 'main_updated_readback_pending'
    save(path,receipt)
    verify(plan,receipt)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stage',action='store_true')
    ap.add_argument('--publish',action='store_true')
    ap.add_argument('--verify',action='store_true')
    ap.add_argument('--pages',action='store_true')
    ap.add_argument('--credential-file')
    args = ap.parse_args()
    plan = stage() if args.stage else json_read(WORK/'PUBLICATION_PLAN.json')
    if args.publish:
        publish(plan,args.credential_file)
    if args.verify or args.pages:
        verify(plan,json_read(WORK/'PUBLICATION_RECEIPT.json'),args.pages)


if __name__ == '__main__':
    main()
