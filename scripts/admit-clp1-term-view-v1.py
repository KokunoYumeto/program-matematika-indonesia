"""Add the tested CLP-1 term lookup to B20 only, preserving all other roles."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def load(path):return json.loads((ROOT/path).read_bytes())
def save(path,data):(ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def fact(path):
    body=(ROOT/path).read_bytes();return {'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}

def main():
    for exe,script in [(sys.executable,'test-clp1-native-terminology-v1.py'),(sys.executable,'test-clp1-term-view-v1.py'),('node','test-clp1-term-ui-v1.mjs')]:
        r=subprocess.run([exe,*(['-B'] if exe==sys.executable else []),str(ROOT/'scripts'/script)],cwd=ROOT,capture_output=True,text=True,timeout=40)
        assert r.returncode==0,r.stderr
    base='docs/backend/clp'
    validation=load(base+'/B20.terms.validation.json')
    assert validation['state']=='pass' and validation['terms']==24 and validation['semantic_canon_review'] is False
    for row in validation['files']:
        assert fact(base+'/'+row['path'])=={k:row[k] for k in ['bytes','sha256']},'Source consumer changed before admission'
    nav_path='backend/authority/central-reader-navigation-v1.json';nav=load(nav_path)
    surface=next(r for r in nav['course_surfaces'] if r['root']==base)
    for lang,suffix in [('id',''),('en','.en')]:
        name=f'B20.terms{suffix}.html'; other=f'B20.terms{".en" if lang=="id" else ""}.html'
        entry={'path':name,'locale':lang,'course_ids':['B20'],'contents_paths':['B20.html',f'B20.teacher{suffix}.html',other]}
        found=next((i for i,r in enumerate(surface['documents']) if r['path']==name),None)
        if found is None:surface['documents'].append(entry)
        else:surface['documents'][found]=entry
    for r in surface['documents']:
        if r['path'] in ['B20.html','B20.teacher.html','B20.teacher.en.html']:
            target='B20.terms.en.html' if '.en.' in r['path'] else 'B20.terms.html'
            r['contents_paths']=list(dict.fromkeys([*r['contents_paths'],target]))
    nav['summary']['course_surface_html_documents']=sum(len(s['documents']) for s in nav['course_surfaces'])
    nav['summary']['classified_html_documents']=sum(nav['summary'][k] for k in ['reader_html_documents','gateway_html_documents','course_surface_html_documents','generic_html_documents'])
    nav['summary']['navigation_overlay_documents']=sum(nav['summary'][k] for k in ['reader_html_documents','gateway_html_documents','course_surface_html_documents'])+sum(bool(s['navigation_required']) for s in nav['generic_surfaces'])
    save(nav_path,nav)
    override_path='backend/course-capsule-v1/authority/integration-overrides-v1.json';over=load(override_path);before=copy.deepcopy(over)
    evidence=[{'kind':'clp1_terminology_consumer','locator':base+'/B20.terms.validation.json',**fact(base+'/B20.terms.validation.json'),'verified_date':'2026-09-30'}]
    over['native_capabilities']['B20']['terminology']={'status':'available_unverified','evidence':evidence}
    resources=over['educator_evidence']['B20']['resources']
    resources[:]=[r for r in resources if not r['id'].startswith('B20:clp1-terms-')]
    for lang,suffix in [('id',''),('en','.en')]:
        page=f'B20.terms{suffix}.html'
        resources.append({'id':'B20:clp1-terms-'+lang,'title':'B20 · CLP-1 terminology and provenance' if lang=='en' else 'B20 · Istilah dan asal-usul CLP-1',
          'resource_type':'educator-data','status':'verified','url':'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/clp/'+page,
          'scope':'24 term/concept identities; three reversible metadata-label repairs. Native terminology claims retained, not a new semantic canon review.' if lang=='en' else '24 identitas istilah/konsep; tiga perbaikan label metadata yang reversibel. Klaim istilah asli dipertahankan, bukan pemeriksaan baru terhadap makna atau kanon.',**fact(base+'/'+page)})
    for key in before:
        a,c=copy.deepcopy(before[key]),copy.deepcopy(over[key])
        if key in ['native_capabilities','educator_evidence']:a.pop('B20',None);c.pop('B20',None)
        assert a==c,'Unrelated role changed: '+key
    save(override_path,over)
    print(json.dumps({'state':'admitted_locally','role':'B20','terms':24,'native_semantic_review':False,'other_roles_unchanged':True}))

if __name__=='__main__':main()
