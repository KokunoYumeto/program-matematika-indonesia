"""Add this validated reader to the existing public programme; no Git scans.

Fresh exact-parent plan, additive path whitelist, no force or deletions. Existing
reader bytes and unrelated public navigation remain unchanged. Credentials never
enter plans, receipts, URLs or output. --verify resumes an existing transaction.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import requests

BASE = Path(__file__).resolve().parent.parent
WORK = BASE / 'b40-foundations-public-20261002'
CORE = BASE / 'd100-capability-v1-worktree'
API = 'https://api.github.com/repos/KokunoYumeto/program-matematika-indonesia'
RAW = 'https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia'
ORIGIN = 'https://kokunoyumeto.github.io/program-matematika-indonesia/'
PREFIX = 'docs/en/readers/hefferon-foundations/'
RELEASE_TAG = 'b40-foundations-2026.10.02'
ARCHIVE_URL = 'https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/'+RELEASE_TAG+'/COMPLETE_SOURCE.zip'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def jb(o):
    return (json.dumps(o, ensure_ascii=False, indent=2) + '\n').encode()


def fact(b):
    return {'bytes': len(b), 'sha256': sha(b)}


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(jb(obj))


def get(url):
    r = requests.get(url, headers={'User-Agent': 'Open-Courses-source-bound-reader'}, timeout=(15, 90))
    assert r.status_code == 200, 'anonymous read HTTP ' + str(r.status_code) + ': ' + url
    return r.content


def stage():
    assert not (WORK / 'PUBLICATION_RECEIPT.json').exists(), 'resume transaction; never create a duplicate'
    seal = json.loads((WORK / 'SOURCE_SEAL.json').read_bytes())
    browser = json.loads((WORK / 'BROWSER_QA.json').read_bytes())
    visual = json.loads((WORK / 'VISUAL_INSPECTION.json').read_bytes())
    assert seal['state'] == browser['state'] == visual['state'] == 'PASS'
    commit = json.loads(get(API + '/commits/main'))
    parent, tree = commit['sha'], commit['commit']['tree']['sha']
    entries = {}
    def add(path, b):
        assert path not in entries
        target = WORK / 'publication-staging' / path
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(b)
        entries[path] = {'path': path, 'local': str(target.relative_to(WORK)).replace('\\', '/'), **fact(b)}
    manifest = json.loads((WORK / 'public/FOUNDATIONS_MANIFEST.json').read_bytes())
    for row in manifest['public_files']:
        b = (WORK / 'public' / row['path']).read_bytes()
        assert fact(b) == {'bytes': row['bytes'], 'sha256': row['sha256']}
        add(PREFIX + row['path'], b)
    add(PREFIX + 'FOUNDATIONS_MANIFEST.json', (WORK / 'public/FOUNDATIONS_MANIFEST.json').read_bytes())
    baselines = []
    def public_input(path):
        b = get(RAW + '/' + parent + '/' + path)
        dest = WORK / 'public-baseline' / path
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(b)
        baselines.append({'path': path, **fact(b)})
        return b
    url = ORIGIN + 'en/readers/hefferon-foundations/'
    index_fact = fact((WORK / 'public/index.html').read_bytes())
    zip_fact = fact((WORK / 'public/COMPLETE_SOURCE.zip').read_bytes())
    locales_path = 'docs/interface/locales.js'
    original = public_input(locales_path).decode()
    needle = "B40: [english('Hefferon: Linear Algebra, answers, and Sage lab', 'https://hefferon.net/linearalgebra/')],"
    assert original.count(needle) == 1, 'reconcile changed native B40 entry; do not guess'
    replacement = "B40: [\n    englishMirror('English foundations — six linked sections, not the full book', '"+url+"', 'HTML', "+json.dumps(index_fact)+"),\n    englishMirror('Offline English foundations and complete editable source', '"+ARCHIVE_URL+"', 'HTML ZIP', "+json.dumps({**zip_fact,'offlineAfterDownload':True})+"),\n    english('Hefferon: complete Linear Algebra, answers, and Sage lab', 'https://hefferon.net/linearalgebra/'),\n  ],"
    add(locales_path, original.replace(needle, replacement).encode())
    anchor = '<a class="resource-link primary" href="'+url+'" data-content-language="en" hreflang="en" data-access-role="hosted-reader" data-original-source="program-mirror"><span lang="en">English foundations — six linked sections, not the full book</span><small>HTML · English</small></a>'
    offline = '<a class="resource-link" href="'+ARCHIVE_URL+'" data-content-language="en" hreflang="en" data-access-role="offline-copy" data-original-source="program-mirror"><span lang="en">Offline English foundations and complete editable source</span><small>HTML ZIP · English</small></a>'
    for name in ['index.html', 'learning-map.html', 'learning-map-paired.html']:
        path = 'docs/en/' + name; original = public_input(path).decode()
        match = re.search(r'<article\b[^>]*id="course-B40".*?</article>', original, re.S)
        assert match, path
        block = match.group()
        hosted = re.search(r'<section class="resource-group" data-access-group="hosted-reader">.*?</section>', block, re.S)
        assert hosted and 'No program-hosted reader is available yet' in hosted.group(), path
        changed = block[:hosted.start()] + '<section class="resource-group" data-access-group="hosted-reader"><h4>Program-hosted reader</h4>'+anchor+offline+'</section>' + block[hosted.end():]
        result = original[:match.start()] + changed + original[match.end():]
        assert result.replace(changed, block, 1) == original
        add(path, result.encode())
    for locale in ['en', 'id']:
        path = 'docs/' + locale + '/programme/index.html'; original = public_input(path).decode()
        match = re.search(r'<section id="core-B40">.*?</section>', original, re.S)
        assert match
        label = 'Read the English foundation sections — systems, vector spaces and bases (partial book)' if locale == 'en' else 'Baca bagian fondasi berbahasa Inggris — sistem linear, ruang vektor, dan basis (sebagian buku)'
        link = '<p><a data-b40-foundations="v1" href="'+url+'" hreflang="en">'+label+'</a></p>'
        block = match.group(); assert 'data-b40-foundations=' not in block
        changed = block.replace('</h3>', '</h3>'+link, 1)
        add(path, (original[:match.start()]+changed+original[match.end():]).encode())
    access_path = 'docs/interface/learner-access-manifest.json'
    access = json.loads(public_input(access_path))
    old_courses = jb({k:v for k,v in access['courses'].items() if k != 'B40'})
    english = access['courses']['B40']['en']
    assert english['program_hosted_reader'] == {'status':'not-yet-hosted','resources':[]}
    def resource(label, href, role, kind, facts):
        return {'access_role': role,'authority_role':'program-mirror','relation_to_source':'offline-copy-of' if role=='offline-copy' else 'mirror-of','content_language':'en','media_type':kind,'url':href,'label':label,'label_language':'en','primary':role=='hosted-reader','offline_after_download':role=='offline-copy',**facts,'source_body_bytes':None,'source_body_sha256':None,'hosted_navigation_overlay':None,'coverage':'six selected foundation sections; not the whole book'}
    english['program_hosted_reader'] = {'status':'available','resources':[resource('English foundations — six linked sections, not the full book',url,'hosted-reader','HTML',index_fact)]}
    english['offline_copies'].append(resource('Offline English foundations and complete editable source',ARCHIVE_URL,'offline-copy','HTML ZIP',zip_fact))
    assert jb({k:v for k,v in access['courses'].items() if k != 'B40'}) == old_courses
    add(access_path, jb(access))
    # Additive current adapter; do not overwrite the earlier published bridge.
    overlay_root = CORE / 'backend/cross-programme-v1/phone-current-20261002'
    frozen = json.loads((overlay_root / 'INPUTS.json').read_bytes())
    names = ['INPUTS.json','DEPENDENCY_OVERLAY.json','VALIDATION.json','HANDOFF.json'] + [r['path'] for r in frozen['inputs']]
    for name in names:
        add('backend/cross-programme-v1/phone-current-20261002/'+name, (overlay_root / name).read_bytes())
    add('scripts/build-phone-dependency-overlay-v1.py', (CORE / 'scripts/build-phone-dependency-overlay-v1.py').read_bytes())
    for name in ['build_b40_foundations_public_20261002.py','seal_b40_foundations_public_20261002.py','test_b40_foundations_public_20261002.mjs',Path(__file__).name]:
        add('scripts/b40-foundations/'+name, (BASE / 'curriculum_logbook' / name).read_bytes())
    for name in ['BUILD_RECEIPT.json','SOURCE_SEAL.json','BROWSER_QA.json','VISUAL_INSPECTION.json']:
        add('backend/b40-foundations-public-20261002/'+name, (WORK / name).read_bytes())
    plan = {'schema':'b40-foundations-publication-plan/1','base_commit':parent,'base_tree':tree,'files':list(entries.values()),'public_baselines':baselines,'deleted_paths':[],'force':False,'model':'gpt-6-astra','effort':'ultra'}
    save(WORK / 'PUBLICATION_PLAN.json', plan)
    print(json.dumps({'state':'plan_staged','files':len(entries),'bytes':sum(x['bytes'] for x in entries.values()),'base':parent}),flush=True)
    return plan


def authenticate(credential_file):
    if credential_file:
        candidates = list(dict.fromkeys(re.findall(r'github_pat_[A-Za-z0-9_]+|ghp_[A-Za-z0-9]+', Path(credential_file).read_text(encoding='utf-8-sig'))))
    else:
        gh = shutil.which('gh'); assert gh, 'existing GitHub CLI unavailable'
        p = subprocess.run([gh,'auth','token','--hostname','github.com'],capture_output=True,text=True,timeout=30,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        assert p.returncode == 0, 'existing CLI authentication unavailable'
        candidates = [p.stdout.strip()]
    session = requests.Session();session.headers.update({'User-Agent':'Open-Courses-source-preserving-integration','Accept':'application/vnd.github+json'})
    for token in candidates[:2]:
        session.headers['Authorization'] = 'Bearer '+token
        r = session.get('https://api.github.com/user',timeout=30)
        if r.status_code == 200 and r.json().get('login') == 'KokunoYumeto':
            return session
    raise AssertionError('authenticated account check failed; no values exposed')


def api(session, method, suffix, **kwargs):
    r = session.request(method, API+suffix, timeout=(15,120), **kwargs)
    if not r.ok:
        try:
            data = r.json()
        except ValueError:
            data = {}
        error = {'method':method,'endpoint':suffix,'http':r.status_code,
                 'message':str(data.get('message',''))[:1200],
                 'errors':[({k:x[k] for k in ('resource','field','code','message') if k in x} if isinstance(x,dict) else str(x)[:300]) for x in data.get('errors',[])][:5],
                 'retry_after':r.headers.get('Retry-After'),
                 'rate_remaining':r.headers.get('X-RateLimit-Remaining')}
        save(WORK/'LAST_API_ERROR.json',error)
        raise AssertionError(json.dumps(error))
    return r.json()


def verify(plan, receipt, pages=False):
    rows=[]
    for row in plan['files']:
        if pages and not row['path'].startswith('docs/'):
            continue
        url = ORIGIN + row['path'][5:] if pages else RAW+'/'+receipt['commit']+'/'+row['path']
        b=get(url);assert fact(b)=={'bytes':row['bytes'],'sha256':row['sha256']}, row['path']
        rows.append({'path':row['path'],'url':url,'http':200,**fact(b)})
    receipt['pages_readback' if pages else 'anonymous_commit_readback']=rows
    receipt['state']='public_pages_and_sources_anonymously_verified' if pages else 'public_commit_verified_pages_pending'
    save(WORK/'PUBLICATION_RECEIPT.json',receipt)
    print(json.dumps({'state':receipt['state'],'commit':receipt['commit'],'files':len(rows)}),flush=True)


def ensure_source_release(session, plan):
    """Preserve full source as release assets, without the Git-blob size limit."""
    receipt_path=WORK/'SOURCE_RELEASE_RECEIPT.json'
    existing=session.get(API+'/releases/tags/'+RELEASE_TAG,timeout=30)
    assert existing.status_code in (200,404)
    if existing.status_code==200:
        release=existing.json()
        assert receipt_path.exists(), 'unowned existing release tag; no modification'
        prior=json.loads(receipt_path.read_bytes())
        assert prior['release_id']==release['id']
    else:
        assert not receipt_path.exists(), 'prior release is missing; do not duplicate'
        body=('Six linked original-English foundation sections from Jim Hefferon’s Linear Algebra: linear systems, reduced echelon form, vector spaces, independence, bases and fields. This is a partial reading edition, not the whole book.\n\n'
              'Read online: '+ORIGIN+'en/readers/hefferon-foundations/\n\n'
              'Download the complete cumulative editable LaTeX first, then COMPLETE_SOURCE.zip. The ZIP contains all six offline HTML readers, the complete original editable source archive (including styles, figures and bibliography), exact frozen generation inputs and deterministic rebuild instructions. HTML is the reading format; no new PDF or native TeX build is claimed. The original author’s site remains https://hefferon.net/linearalgebra/.\n\n'
              'Original mathematics: Jim Hefferon. CC BY-SA 2.5 option, with all native component credits and rights retained. Source-preserving rebuild, indexing, navigation and packaging: OpenAI Codex — GPT-6 Astra, Ultra effort. Earlier intermediate model identity is unverified and not reattributed. No human review or exhaustive proof certification is claimed.\n\n'
              'Bahasa Indonesia: Enam bagian fondasi berbahasa Inggris ini bukan keseluruhan buku dan bukan terjemahan baru. Unduh sumber LaTeX lengkap, lalu ZIP sumber dan pembaca luring. Matematika asli: Jim Hefferon; opsi lisensi CC BY-SA 2.5 beserta kredit komponen tetap berlaku. Pembangunan ulang, pengindeksan, navigasi, dan pengemasan: OpenAI Codex — GPT-6 Astra, tingkat upaya Ultra. Tidak ada klaim peninjauan manusia.')
        release=api(session,'POST','/releases',json={'tag_name':RELEASE_TAG,'target_commitish':plan['base_commit'],'name':'Linear algebra foundations — original English and complete editable source','body':body,'draft':True,'prerelease':False,'make_latest':'false'})
        save(receipt_path,{'schema':'b40-foundations-source-release/1','state':'draft_assets_pending','release_id':release['id'],'tag':RELEASE_TAG,'assets':[]})
    receipt=json.loads(receipt_path.read_bytes())
    required=[('00-foundations-cumulative.tex',WORK/'public/sources/00-foundations-cumulative.tex','application/x-tex'),('COMPLETE_SOURCE.zip',WORK/'public/COMPLETE_SOURCE.zip','application/zip'),('FOUNDATIONS_MANIFEST.json',WORK/'public/FOUNDATIONS_MANIFEST.json','application/json')]
    assets=api(session,'GET','/releases/'+str(release['id'])+'/assets?per_page=100')
    for name,path,kind in required:
        b=path.read_bytes();matches=[x for x in assets if x['name']==name]
        assert len(matches)<=1
        if matches:
            asset=matches[0]
            assert asset['state']=='uploaded' and asset['size']==len(b) and asset.get('digest')=='sha256:'+sha(b), 'existing asset mismatch; never overwrite'
        else:
            endpoint=release['upload_url'].split('{')[0]
            assert endpoint.startswith('https://uploads.github.com/repos/KokunoYumeto/program-matematika-indonesia/releases/')
            r=session.post(endpoint,params={'name':name},data=b,headers={'Content-Type':kind},timeout=(20,180))
            assert r.status_code==201,'source asset upload HTTP '+str(r.status_code)
            asset=r.json();assert asset['size']==len(b) and asset.get('digest')=='sha256:'+sha(b)
            assets.append(asset)
        receipt['assets']=[x for x in receipt['assets'] if x['name']!=name]+[{'name':name,'id':asset['id'],'url':asset['browser_download_url'],**fact(b)}]
        save(receipt_path,receipt)
        print(json.dumps({'source_asset_ready':name,'bytes':len(b)}),flush=True)
    if release['draft']:
        release=api(session,'PATCH','/releases/'+str(release['id']),json={'draft':False,'make_latest':'false'})
    assert not release['draft']
    public_assets=api(session,'GET','/releases/'+str(release['id'])+'/assets?per_page=100')
    for row in receipt['assets']:
        published=next(x for x in public_assets if x['id']==row['id'])
        assert published['name']==row['name'] and published['size']==row['bytes'] and published['digest']=='sha256:'+row['sha256']
        row['url']=published['browser_download_url']
    save(receipt_path,receipt)
    for row in receipt['assets']:
        b=get(row['url']);assert fact(b)=={'bytes':row['bytes'],'sha256':row['sha256']}
        row['anonymous_readback']='PASS'
        save(receipt_path,receipt)
    receipt['state']='public_all_assets_anonymously_verified';receipt['url']=release['html_url'];save(receipt_path,receipt)
    print(json.dumps({'source_release':receipt['state'],'assets':len(receipt['assets'])}),flush=True)


def publish(plan, credential_file):
    if (WORK/'PUBLICATION_RECEIPT.json').exists():
        receipt=json.loads((WORK/'PUBLICATION_RECEIPT.json').read_bytes());verify(plan,receipt);return
    session=authenticate(credential_file)
    assert api(session,'GET','/git/ref/heads/main')['object']['sha']==plan['base_commit'],'main changed; no force'
    ensure_source_release(session,plan)
    checkpoint_path=WORK/'BLOB_UPLOAD_CHECKPOINT.json'
    checkpoint=json.loads(checkpoint_path.read_bytes()) if checkpoint_path.exists() else {'schema':'github-content-addressed-upload/1','blobs':{}}
    nodes=[]
    for i,row in enumerate(plan['files'],1):
        b=(WORK/row['local']).read_bytes();assert fact(b)=={'bytes':row['bytes'],'sha256':row['sha256']}
        expected=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        saved=checkpoint['blobs'].get(expected)
        if saved:
            assert saved['bytes']==len(b) and saved['sha256']==sha(b)
        else:
            checkpoint['current']={'path':row['path'],'git_blob_sha':expected,**fact(b)}
            save(checkpoint_path,checkpoint)
            # Recover objects from an interrupted attempt without downloading the
            # base64 body or submitting their bytes again. Final raw readback is
            # still mandatory after the branch update.
            with session.get(API+'/git/blobs/'+expected,stream=True,timeout=(15,30)) as probe:
                status=probe.status_code
            assert status in (200,404), 'blob existence check HTTP '+str(status)
            if status==200:
                state='recovered_existing_content_addressed_blob'
            else:
                print(json.dumps({'uploading':row['path'],'bytes':len(b),'ordinal':i}),flush=True)
                blob=api(session,'POST','/git/blobs',json={'content':base64.b64encode(b).decode(),'encoding':'base64'})
                assert blob['sha']==expected
                state='uploaded'
            checkpoint['blobs'][expected]={'state':state,**fact(b)}
            save(checkpoint_path,checkpoint)
        nodes.append({'path':row['path'],'mode':'100644','type':'blob','sha':expected})
        if i%10==0:print(json.dumps({'checkpointed_blobs':i,'total':len(plan['files'])}),flush=True)
    tree=api(session,'POST','/git/trees',json={'base_tree':plan['base_tree'],'tree':nodes})
    actor={'name':'OpenAI Codex','email':'codex@users.noreply.github.com','date':datetime.now(timezone.utc).isoformat()}
    commit=api(session,'POST','/git/commits',json={'message':'Publish original-English linear algebra foundations with editable source and exact dependency adapter\n\nSix selected sections, not the whole book. Preserve Jim Hefferon and all component rights. Current rebuild/integration: OpenAI Codex — GPT-6 Astra, Ultra effort.','tree':tree['sha'],'parents':[plan['base_commit']],'author':actor,'committer':actor})
    receipt={'schema':'b40-foundations-publication/1','state':'commit_created_ref_not_updated','parent':plan['base_commit'],'commit':commit['sha'],'tree':tree['sha'],'plan_sha256':sha((WORK/'PUBLICATION_PLAN.json').read_bytes()),'deleted_paths':[],'force':False}
    save(WORK/'PUBLICATION_RECEIPT.json',receipt)
    assert api(session,'GET','/git/ref/heads/main')['object']['sha']==plan['base_commit'],'main advanced; preserve concurrent work'
    result=api(session,'PATCH','/git/refs/heads/main',json={'sha':commit['sha'],'force':False})
    assert result['object']['sha']==commit['sha']
    receipt['state']='main_updated_readback_pending';save(WORK/'PUBLICATION_RECEIPT.json',receipt)
    verify(plan,receipt)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--stage',action='store_true');ap.add_argument('--publish',action='store_true');ap.add_argument('--verify',action='store_true');ap.add_argument('--pages',action='store_true');ap.add_argument('--credential-file');a=ap.parse_args()
    plan=stage() if a.stage else json.loads((WORK/'PUBLICATION_PLAN.json').read_bytes())
    if a.publish:publish(plan,a.credential_file)
    if a.verify or a.pages:
        receipt=json.loads((WORK/'PUBLICATION_RECEIPT.json').read_bytes());assert receipt['plan_sha256']==sha((WORK/'PUBLICATION_PLAN.json').read_bytes());verify(plan,receipt,pages=a.pages)


if __name__=='__main__':main()
