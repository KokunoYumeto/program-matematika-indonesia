"""Publish only checked additive reading-route files against an exact public parent.

Uses the existing authenticated CLI without printing credentials. Never force,
delete remote files, scan the repository, or change repository visibility.
"""
import argparse
import base64
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'backend/cross-programme-v1'
PLAN=OUT/'HUMAN_ANALYSIS_PUBLICATION_PLAN.json'
RECEIPT=OUT/'HUMAN_ANALYSIS_PUBLICATION_RECEIPT.json'
API='https://api.github.com/repos/KokunoYumeto/program-matematika-indonesia'
RAW='https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia/'
PAGES='https://kokunoyumeto.github.io/program-matematika-indonesia/'
PARENT='6c949b47e0ca75e36ebd8fe86eb699fa941e0a2e'
PATHS=[
 'scripts/human-analysis-routes-v1.mjs','scripts/test-human-analysis-routes-v1.mjs',
 'scripts/check-human-analysis-additive-v1.mjs','scripts/build-cross-programme-integration-v1.mjs',
 'scripts/test-cross-programme-current-v1.mjs','scripts/check-cross-programme-browser-v1.mjs',
 'scripts/publish-human-analysis-routes-v1.py',
 'backend/cross-programme-v1/inputs/lebl-public-20261003/REGISTRY.json',
 'backend/cross-programme-v1/inputs/lebl-public-20261003/READBACK.json',
 'backend/cross-programme-v1/bridge.json','docs/data/cross-programme-v1/bridge.json',
 'docs/en/programme/index.html','docs/id/programme/index.html',
 'backend/authority/central-course-surface-navigation-overlay-v1.json',
 'backend/cross-programme-v1/BUILD_RECEIPT.json',
 'backend/cross-programme-v1/CURRENT_INTEGRATION_VALIDATION.json',
 'backend/cross-programme-v1/HUMAN_ANALYSIS_ADDITIVE_CHECK.json',
 'backend/cross-programme-v1/HUMAN_ANALYSIS_VISUAL_REVIEW.json',
 'backend/cross-programme-v1/current-browser-captures/en-390-human-analysis.png',
 'backend/cross-programme-v1/current-browser-captures/id-390-human-analysis.png',
]

def digest(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf8'))
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def fact(path):
 raw=(ROOT/path).read_bytes();return {'path':path,'bytes':len(raw),'sha256':digest(raw)}

def seal():
 additive=read(OUT/'HUMAN_ANALYSIS_ADDITIVE_CHECK.json')
 qa=read(OUT/'CURRENT_INTEGRATION_VALIDATION.json')
 browser=read(OUT/'CURRENT_BROWSER_VALIDATION.json')
 visual=read(OUT/'HUMAN_ANALYSIS_VISUAL_REVIEW.json')
 assert additive['state']==qa['state']==browser['status']==visual['state']=='pass'
 assert additive['parent']==PARENT
 assert qa['human_analysis_readings']['sections']==7
 assert len([r for r in browser['checks'] if r.get('human_analysis_panels')==5])==6
 for row in additive['checks']:assert fact(row['path'])['sha256']==row['current_sha256']
 for row in visual['captures']:assert fact(row['path'])==row
 rows=[fact(p) for p in PATHS]
 assert len(set(PATHS))==len(PATHS) and sum(r['bytes'] for r in rows)<8*1024*1024
 for row in rows:
  if row['path'].endswith('.png'):continue
  content=(ROOT/row['path']).read_bytes()
  assert not re.search(rb'(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|Bearer\s+[A-Za-z0-9._-]{25,})',content)
 plan={'schema':'human-analysis-additive-publication/1','base_commit':PARENT,'files':rows,
       'model':'gpt-6-astra','effort':'ultra','deletions':[],'force':False}
 if PLAN.exists():assert read(PLAN)==plan,'Existing plan differs; reconcile explicitly'
 else:save(PLAN,plan)
 return plan

def api(session,method,suffix,**kwargs):
 response=session.request(method,API+suffix,timeout=(15,60),**kwargs)
 if not response.ok:raise RuntimeError(f'GitHub {method} {suffix}: HTTP {response.status_code}')
 return response.json()

def verify(plan,receipt):
 anonymous=requests.Session();anonymous.headers['User-Agent']='Open-Courses-public-byte-check'
 rows=[]
 for row in plan['files']:
  response=anonymous.get(RAW+receipt['commit']+'/'+row['path'],timeout=(15,60))
  assert response.status_code==200, f'Anonymous source HTTP {response.status_code}: {row["path"]}'
  assert len(response.content)==row['bytes'] and digest(response.content)==row['sha256'],row['path']
  rows.append({**row,'http':200})
 receipt['anonymous_source_readback']=rows
 pages=[]
 for row in plan['files']:
  if not row['path'].startswith('docs/'):continue
  url=PAGES+row['path'][5:]
  response=anonymous.get(url,timeout=(15,60),headers={'Cache-Control':'no-cache'})
  pages.append({'url':url,'status':response.status_code,'bytes':len(response.content),
    'sha256':digest(response.content),'matches':response.status_code==200 and len(response.content)==row['bytes'] and digest(response.content)==row['sha256']})
 receipt['pages_readback']=pages
 receipt['state']='public_source_and_pages_verified' if all(r['matches'] for r in pages) else 'public_source_verified_pages_deployment_pending'
 receipt['checked_utc']=datetime.now(timezone.utc).isoformat();save(RECEIPT,receipt)
 print(json.dumps({'state':receipt['state'],'commit':receipt['commit'],'files':len(rows),'pages_verified':sum(r['matches'] for r in pages)}),flush=True)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');parser.add_argument('--verify',action='store_true');args=parser.parse_args()
 if args.verify:
  verify(read(PLAN),read(RECEIPT));return
 plan=seal()
 if not args.publish:
  print(json.dumps({'state':'plan_sealed','files':len(plan['files'])}));return
 if RECEIPT.exists():
  receipt=read(RECEIPT);assert receipt['plan_sha256']==digest(PLAN.read_bytes());verify(plan,receipt);return
 credential=subprocess.run(['gh','auth','token','--hostname','github.com'],capture_output=True,text=True,timeout=30,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 assert credential.returncode==0 and credential.stdout.strip(),'Existing CLI authentication unavailable'
 session=requests.Session();session.headers.update({'Authorization':'Bearer '+credential.stdout.strip(),'Accept':'application/vnd.github+json','User-Agent':'Open-Courses-bounded-reading-integration'})
 head=api(session,'GET','/git/ref/heads/main')['object']['sha'];assert head==PARENT,'Public main changed; reconcile exact files, never force'
 parent=api(session,'GET','/git/commits/'+head)
 blobs=[]
 for row in plan['files']:
  assert fact(row['path'])==row,'Local file changed after sealing'
  raw=(ROOT/row['path']).read_bytes()
  blob=api(session,'POST','/git/blobs',json={'content':base64.b64encode(raw).decode('ascii'),'encoding':'base64'})
  blobs.append({'path':row['path'],'mode':'100644','type':'blob','sha':blob['sha']})
 tree=api(session,'POST','/git/trees',json={'base_tree':parent['tree']['sha'],'tree':blobs})
 actor={'name':'OpenAI Codex','email':'codex@users.noreply.github.com','date':datetime.now(timezone.utc).isoformat()}
 commit=api(session,'POST','/git/commits',json={'message':'Add Lebl analysis readings to English and Indonesian course navigation\n\nNavigation integration: OpenAI Codex — GPT-6 Astra, Ultra effort. Textbook authorship and component licence preserved.','tree':tree['sha'],'parents':[head],'author':actor,'committer':actor})
 receipt={'schema':'human-analysis-publication-receipt/1','state':'commit_created_ref_pending','parent':head,'commit':commit['sha'],'tree':tree['sha'],'plan_sha256':digest(PLAN.read_bytes()),'deleted_paths':[],'forced_update':False}
 save(RECEIPT,receipt)
 assert api(session,'GET','/git/ref/heads/main')['object']['sha']==head,'Main changed during upload; do not overwrite'
 result=api(session,'PATCH','/git/refs/heads/main',json={'sha':commit['sha'],'force':False})
 assert result['object']['sha']==commit['sha']
 receipt['state']='public_main_updated_readback_pending';save(RECEIPT,receipt)
 verify(plan,receipt)

if __name__=='__main__':main()
