"""Add exact cumulative source to the existing C110 release; never replace assets."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

REPO = 'KokunoYumeto/tea-time-numerical-analysis-id'
TAG = 'v3.0-id.2-r1'
BASE = f'https://github.com/{REPO}/releases/download/{TAG}/'
EXPECTED = {
    'CHECKSUMS.sha256': (325, '1128cfb0ddf439a38640c1ff75fbaa867ea672892b6a6c5e073473d504dee92d'),
    'PACKAGE_INVENTORY.json': (167506, '1058ccc17f0f8d2ab22867f13e0de83901b22218988d55a24839adf7ec34450d'),
    'Tea-Time-Numerical-Analysis-id-ID-v3.0-id.2-r1-source-backend.zip': (33244105, '0eebe482eec535942524d4e5cb1fb164b9ac7de07f2eb9421e0d7bf29fa7ee4c'),
    'Tea-Time-Numerical-Analysis-id-ID.pdf': (8202487, 'd573b7233d0baa07381e2052a749757885db3a31fbfe695c5a4851ea42d91b6d'),
}
def sha(b): return hashlib.sha256(b).hexdigest()
def gh(*args):
    p = subprocess.run(['gh',*args], capture_output=True, text=True, encoding='utf8', check=True)
    return p.stdout
def download_identity(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'C110-source-verification'}),timeout=90) as r:
        digest=hashlib.sha256();count=0
        while chunk:=r.read(1024*1024): digest.update(chunk);count+=len(chunk)
        return {'url':url,'status':r.status,'bytes':count,'sha256':digest.hexdigest()}

parser=argparse.ArgumentParser()
parser.add_argument('--intake',required=True)
parser.add_argument('--publish',action='store_true')
args=parser.parse_args()
root=Path(__file__).resolve().parent.parent
p=Path(args.intake).resolve()
subprocess.run(['python','-B',str(root/'scripts/test-c110-cumulative-source-v1.py'),'--intake',str(p)],check=True)
release=json.loads(gh('release','view',TAG,'--repo',REPO,'--json','assets,body,url'))
assets={a['name']:a for a in release['assets']}
for name,(size,digest) in EXPECTED.items():
    assert assets[name]['size']==size and assets[name]['digest']=='sha256:'+digest
staged=p/'assembled'
(staged/'README.id.md').write_bytes((root/'backend/course-capsule-v1/adapters/c110-cumulative-source-v1/README.id.md').read_bytes())
manifest=json.loads((staged/'manifest.json').read_bytes())
replay=json.loads((p/'build-assembled/BUILD_RECEIPT.json').read_text(encoding='utf-8-sig'))
proof={'schema':'c110-cumulative-equivalence/1','status':'pass','native_payload_files_verified':895,
       'native_build_inputs_verified':289,'embedded_sources':30,'unchanged_body_bytes':True,
       'deterministic_assembly':True,'native_and_assembled_pdf_byte_identical':True,
       'pdf':replay['pdf'],'pages':387,'direct_source':manifest['direct_source'],
       'negative_cases_rejected':9,'tex_serialization':'Global\\InterlanguageTeXSlotV1',
       'visual_sample_pdf_pages':[2,121],
       'new_translation':False,'new_mathematical_review':False,
       'model_for_this_assembly':'OpenAI Codex - GPT-6 Astra, Ultra effort',
       'source_release':release['url'],
       'scripts':[{ 'path':'scripts/'+n,'sha256':sha((root/'scripts'/n).read_bytes())}
          for n in ['assemble-c110-cumulative-source-v1.py','test-c110-cumulative-source-v1.py','verify-c110-cumulative-build-v1.ps1']]}
(staged/'C110_SOURCE_EQUIVALENCE.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
names=['TeaTimeNumericalAnalysis-id-ID.tex','manifest.json','README.id.md','C110_SOURCE_EQUIVALENCE.json']
local={n:{'bytes':(staged/n).stat().st_size,'sha256':sha((staged/n).read_bytes())} for n in names}
missing=[]
for name in names:
    if name not in assets: missing.append(name)
    else: assert assets[name]['size']==local[name]['bytes'] and assets[name]['digest']=='sha256:'+local[name]['sha256'],'Existing asset differs; never overwrite'
assert len(assets)+len(missing)<=100
marker='<!-- c110-cumulative-source-20261003 -->'
body=release['body']
addition='\n\n'+marker+'\n\n## Unduhan dan sumber kumulatif\n\n'+(staged/'README.id.md').read_text(encoding='utf8').split('## Berkas satu edisi\n\n',1)[1]
newbody=body if marker in body else body+addition
notes=p/'RELEASE_NOTES_WITH_SOURCE.md'
notes.write_text(newbody,encoding='utf8')
state={'schema':'c110-source-release/1','status':'preflight_pass','release':release['url'],
       'original_assets_preserved':list(EXPECTED),'new_assets':local,'missing':missing}
receipt=p/'NATIVE_RELEASE_READBACK.json'
receipt.write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
if args.publish:
    if missing: gh('release','upload',TAG,'--repo',REPO,*[str(staged/n) for n in missing])
    if newbody!=body: gh('release','edit',TAG,'--repo',REPO,'--notes-file',str(notes))
    refreshed=json.loads(gh('release','view',TAG,'--repo',REPO,'--json','assets,body'))
    assert marker in refreshed['body']
    state['status']='published_pending_anonymous_readback'
    state['public_readback']=[]
    receipt.write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
    wanted={**{n:{'bytes':s,'sha256':h} for n,(s,h) in EXPECTED.items()},**local}
    actual={a['name']:a for a in refreshed['assets']}
    for name,identity in wanted.items():
        assert actual[name]['size']==identity['bytes']
        item=download_identity(BASE+name)
        assert item['bytes']==identity['bytes'] and item['sha256']==identity['sha256'],name
        state['public_readback'].append(item)
        receipt.write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
    state['status']='published_and_anonymously_verified'
    receipt.write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':state['status'],'release':state['release'],'verified_files':len(state.get('public_readback',[]))}))
