"""Publish only the additive access bindings and final sanitized receipts."""
import base64
from datetime import datetime,timezone
import hashlib
import io
import json
from pathlib import Path
import zipfile
import deploy_b40_foundations_public_20261002 as deploy

WORK=deploy.WORK

def main():
    receipt=json.loads((WORK/'PUBLICATION_RECEIPT.json').read_bytes())
    assert receipt['state']=='public_pages_and_sources_anonymously_verified'
    bindings=json.loads((WORK/'PUBLIC_PROOF_BINDINGS.json').read_bytes())
    assert bindings['public_commit']==receipt['commit'] and not bindings['states']['owner_admitted']
    plan=json.loads((WORK/'PUBLICATION_PLAN.json').read_bytes())
    files={r['path']:(WORK/r['local']).read_bytes() for r in plan['files']}
    for row in plan['files']:assert deploy.fact(files[row['path']])=={k:row[k] for k in ('bytes','sha256')}
    sidecars={
        'backend/cross-programme-v1/provider-public/B40-public-proof-bindings-20261002.json':(WORK/'PUBLIC_PROOF_BINDINGS.json').read_bytes(),
        'backend/b40-foundations-public-20261002/PUBLICATION_RECEIPT.json':(WORK/'PUBLICATION_RECEIPT.json').read_bytes(),
        'backend/b40-foundations-public-20261002/SOURCE_RELEASE_RECEIPT.json':(WORK/'SOURCE_RELEASE_RECEIPT.json').read_bytes(),
        'scripts/b40-foundations/bind_b40_public_proofs_20261002.py':(Path(__file__).parent/'bind_b40_public_proofs_20261002.py').read_bytes(),
        'scripts/b40-foundations/finalize_b40_integration_20261002.py':Path(__file__).read_bytes()}
    assert not (set(files)&set(sidecars))
    files.update(sidecars)
    files['preservation/B40_COMPLETE_SOURCE.zip']=(WORK/'public/COMPLETE_SOURCE.zip').read_bytes()
    files['README.txt']=('OPEN COURSES — FOUNDATION READERS AND DEPENDENCY ADAPTER\n\n'
      'Read docs/en/readers/hefferon-foundations/index.html. Extract preservation/B40_COMPLETE_SOURCE.zip for the exact original source tree, editable cumulative LaTeX, offline readers and deterministic HTML replay. No PDF or native TeX build is newly claimed. Jim Hefferon and component authors retain their credits and CC BY-SA 2.5/component terms.\n\n'
      'From this archive root, python -B scripts/build-phone-dependency-overlay-v1.py --check reproduces the frozen dependency overlay offline. The 184 preparation edges and 48 exact reading edges are not mathematical admission. B40 public proof bindings preserve the five checked statement/proof pairs, with owner admission still false. The phone selection is 75 courses/1179 lessons; pinned public preparation catalogue is 72/1002, different editions. Historical snapshots remain historical.\n\n'
      'Current integration: OpenAI Codex — GPT-6 Astra, Ultra effort. Source authorship and historical provenance are unchanged. This is not an Everyday-English rewrite or human review.\n\n'
      'Bahasa Indonesia: Paket ini menyediakan pembaca fondasi berbahasa Inggris, sumber yang dapat disunting, dan adaptor hubungan prasyarat. Hubungan persiapan belajar tidak sama dengan pengesahan pembuktian. Kredit dan lisensi setiap sumber tetap berlaku. Integrasi: OpenAI Codex — GPT-6 Astra, tingkat upaya Ultra; tidak ada klaim peninjauan manusia.\n').encode()
    inv={'schema':'additive-programme-preservation-inventory/1','files':[{'path':p,**deploy.fact(b)} for p,b in sorted(files.items())],'self_excluded':True}
    files['PRESERVATION_INVENTORY.json']=deploy.jb(inv)
    sink=io.BytesIO()
    with zipfile.ZipFile(sink,'w') as z:
        for p,b in sorted(files.items()):
            zi=zipfile.ZipInfo(p,(2026,10,2,0,0,0));zi.compress_type=zipfile.ZIP_STORED if p.endswith('.zip') else zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16;z.writestr(zi,b)
    package=sink.getvalue()
    with zipfile.ZipFile(io.BytesIO(package)) as z:
        assert z.testzip() is None and len(z.namelist())==len(files)
        for p,b in files.items():assert z.read(p)==b
    target=WORK/'PUBLIC_DEPENDENCY_INTEGRATION_SOURCE.zip'
    if target.exists():assert target.read_bytes()==package
    else:target.write_bytes(package)
    session=deploy.authenticate(None)
    release=json.loads((WORK/'SOURCE_RELEASE_RECEIPT.json').read_bytes())
    assets=deploy.api(session,'GET','/releases/'+str(release['release_id'])+'/assets?per_page=100')
    matches=[a for a in assets if a['name']==target.name]
    assert len(matches)<=1
    if matches:
        asset=matches[0];assert asset['size']==len(package) and asset['digest']=='sha256:'+deploy.sha(package)
    else:
        endpoint='https://uploads.github.com/repos/KokunoYumeto/program-matematika-indonesia/releases/'+str(release['release_id'])+'/assets'
        r=session.post(endpoint,params={'name':target.name},data=package,headers={'Content-Type':'application/zip'},timeout=(20,180))
        assert r.status_code==201,'integration archive upload HTTP '+str(r.status_code)
        asset=r.json();assert asset['size']==len(package) and asset['digest']=='sha256:'+deploy.sha(package)
    assert deploy.get(asset['browser_download_url'])==package
    package_fact={'path':target.name,**deploy.fact(package),'members':len(files),'url':asset['browser_download_url'],'anonymous_readback':'PASS','all_members_verified':True}
    deploy.save(WORK/'INTEGRATION_PACKAGE_RECEIPT.json',package_fact)
    sidecars['backend/b40-foundations-public-20261002/INTEGRATION_PACKAGE_RECEIPT.json']=deploy.jb(package_fact)
    finalpath=WORK/'FINAL_PUBLIC_RECEIPT.json'
    if finalpath.exists():
        final=json.loads(finalpath.read_bytes())
    else:
        head=deploy.api(session,'GET','/commits/main');parent=head['sha'];nodes=[]
        # Only additive, uniquely named sidecars. Never replace another task's data.
        for p,b in sidecars.items():
            r=session.get(deploy.API+'/contents/'+p,params={'ref':parent},timeout=30)
            assert r.status_code==404,'sidecar path already exists; reconcile instead of overwrite: '+p
            blob=deploy.api(session,'POST','/git/blobs',json={'content':base64.b64encode(b).decode(),'encoding':'base64'})
            assert blob['sha']==hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
            nodes.append({'path':p,'mode':'100644','type':'blob','sha':blob['sha']})
        tree=deploy.api(session,'POST','/git/trees',json={'base_tree':head['commit']['tree']['sha'],'tree':nodes})
        actor={'name':'OpenAI Codex','email':'codex@users.noreply.github.com','date':datetime.now(timezone.utc).isoformat()}
        commit=deploy.api(session,'POST','/git/commits',json={'message':'Bind published foundation proofs to exact source units and preserve verified access receipts\n\nAccess identity, not downstream proof admission. OpenAI Codex — GPT-6 Astra, Ultra effort.','tree':tree['sha'],'parents':[parent],'author':actor,'committer':actor})
        final={'schema':'b40-additive-proof-bindings-publication/1','state':'commit_created','parent':parent,'commit':commit['sha'],'tree':tree['sha'],'package':package_fact,'files':[{'path':p,**deploy.fact(b)} for p,b in sidecars.items()]}
        deploy.save(finalpath,final)
    live=deploy.api(session,'GET','/git/ref/heads/main')['object']['sha']
    if live==final['parent']:
        deploy.api(session,'PATCH','/git/refs/heads/main',json={'sha':final['commit'],'force':False})
    else:assert live==final['commit'],'main advanced; no force or unverified overwrite'
    for row in final['files']:
        b=deploy.get(deploy.RAW+'/'+final['commit']+'/'+row['path']);assert deploy.fact(b)=={k:row[k] for k in ('bytes','sha256')}
        row['anonymous_readback']='PASS'
    final['state']='public_all_sidecars_and_package_anonymously_verified';deploy.save(finalpath,final)
    print(json.dumps({'state':final['state'],'commit':final['commit'],'files':len(final['files']),'package':package_fact}),flush=True)

if __name__=='__main__':main()
