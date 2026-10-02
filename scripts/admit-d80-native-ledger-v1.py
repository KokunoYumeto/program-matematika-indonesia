"""Admit the tested D80 metadata consumer without claiming semantic canon review."""
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE='backend/course-capsule-v1/adapters/d80-native-ledger-v1'
SITE='docs/backend/d80/native-ledger'
def load(p): return json.loads((ROOT/p).read_bytes())
def fact(p):
    raw=(ROOT/p).read_bytes()
    return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def save(p,value):
    target=ROOT/p
    # An evidence-only refresh must not invalidate shared identities by changing
    # newline style when the actual JSON value has not changed.
    if target.exists() and json.loads(target.read_bytes())==value:return
    target.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    assert sys.argv[1:] in ([],['--refresh-hosted-evidence'])
    refresh=bool(sys.argv[1:])
    tests,browser=load(BASE+'/tests.json'),load(BASE+'/browser-tests.json')
    assert tests['state']==browser['state']=='pass'
    assert len(tests['checks'])==26 and len(tests['negative_fixtures'])==8
    assert tests['summary']['visible_records']==7760 and tests['summary']['native_records']==8430
    assert not tests['semantic_canon_approval'] and not tests['native_book_rebuilt']
    assert len(browser['cases'])==4 and not browser['errors']
    assert browser['external_network_blocked'] and browser['offline_file_scheme'] and browser['record_html_injection_refused']
    assert not browser['desktop_interaction']
    for item in browser['input_files']:
        name=Path(item['path']).name
        assert fact(BASE+'/site/'+name)=={k:item[k] for k in ('bytes','sha256')}, 'Stale browser body evidence'
    for name,identity in tests['outputs'].items():
        assert fact(BASE+'/site/'+name)==identity
        if refresh and name.endswith('.html'):
            text=(ROOT/SITE/name).read_text(encoding='utf-8')
            for placement,pattern in [
                ('top',r'(?:\n[ \t]*)?<nav\b(?=[^>]*data-central-surface-navigation="v1")(?=[^>]*data-placement="top")[^>]*>.*?</nav>'),
                ('bottom',r'<nav\b(?=[^>]*data-central-surface-navigation="v1")(?=[^>]*data-placement="bottom")[^>]*>.*?</nav>(?:\n[ \t]*)?')]:
                text,count=re.subn(pattern,'',text,count=1,flags=re.DOTALL|re.IGNORECASE)
                assert count==1,'Missing managed '+placement+' navigation'
            raw=text.encode()
            assert {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}==identity,'Changed hosted body'
        else: assert fact(SITE+'/'+name)==identity
    over_path='backend/course-capsule-v1/authority/integration-overrides-v1.json'
    nav_path='backend/authority/central-reader-navigation-v1.json'
    old_raw,nav_raw=(ROOT/over_path).read_bytes(),(ROOT/nav_path).read_bytes()
    over,nav=json.loads(old_raw),json.loads(nav_raw)
    before,nav_before=copy.deepcopy(over),copy.deepcopy(nav)
    evidence=[{'kind':kind,'locator':BASE+'/'+name,**fact(BASE+'/'+name),'verified_date':'2026-10-02'} for kind,name in
              [('d80_native_metadata_lock','source-lock.json'),('d80_native_ledger_tests','tests.json'),('d80_native_browser_tests','browser-tests.json')]]
    adapter=over['semantic_adapters']['D80']
    adapter['evidence']=[row for row in adapter['evidence'] if row['kind'] not in {e['kind'] for e in evidence}]+evidence
    for capability in ['translation_ledger','terminology','corrections']:
        over['native_capabilities']['D80'][capability]={'status':'available_unverified','evidence':evidence}
    scope_id='6.347 segmen, 511 istilah, 73 koreksi dan 829 deskripsi diagram; pencarian dan tautan unit eksak, dengan 8.430 rekaman asli dalam arsip metadata. Sebelas istilah tidak memiliki pemetaan unit eksak. Kanon belum ditinjau secara independen; buku tidak dibangun ulang.'
    scope_en='6,347 segments, 511 terms, 73 corrections and 829 diagram descriptions; search and exact unit links, with 8,430 original records in the metadata archive. Eleven terms lack exact unit mappings. No independent canon approval or native-book rebuild.'
    resources=over['educator_evidence']['D80']['resources']
    resources[:]=[r for r in resources if not r['id'].startswith('D80:native-ledger-')]
    for locale,page in [('id','ledger.html'),('en','ledger-en.html')]:
        resources.append({'id':'D80:native-ledger-'+locale,'title':'D80 · Istilah, sumber, koreksi dan diagram' if locale=='id' else 'D80 · Terms, sources, corrections and diagrams',
          'resource_type':'educator-data','status':'verified','url':'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d80/native-ledger/'+page,
          'scope':scope_id if locale=='id' else scope_en,**fact(SITE+'/'+page)})
    tool={'tool_id':'d80.native_ledger','label':'D80 · Cari istilah, sumber, koreksi dan diagram',
      'href':'backend/d80/native-ledger/ledger.html','action_kind':'reference','scope':scope_id,'state':'verified','primary':False,
      'machine_data_is_learner_destination':False,'limitations':[
        'Catatan asli tidak diubah; 88 istilah sementara dan dua perbedaan pilihan tetap terlihat. Ini bukan pengesahan kanon.',
        'Sebanyak 1.736 lokasi hanya pada tingkat unit, bukan rentang sumber eksak per segmen. Pengenalan pertama bukan semua kemunculan istilah.',
        'Sebelas istilah tidak memiliki pemetaan unit eksak; tidak ada tautan yang ditebak. Deskripsi pengganti tetap terpisah dari catatan diagram asli.',
        'Antarmuka Inggris menuju buku Indonesia. Arsip hanya metadata, bukan buku lengkap atau pembangunan ulang buku.'],
      'page':{'path':SITE+'/ledger.html',**fact(SITE+'/ledger.html')},
      'resource':{'path':SITE+'/projection.json',**fact(SITE+'/projection.json')},
      'evidence':{'path':BASE+'/tests.json',**fact(BASE+'/tests.json')}}
    over['learner_tools']['D80']=[r for r in over['learner_tools']['D80'] if r['tool_id']!=tool['tool_id']]+[tool]
    for key in before:
        left,right=copy.deepcopy(before[key]),copy.deepcopy(over[key])
        if key in ['native_capabilities','educator_evidence','semantic_adapters','learner_tools']:
            left.pop('D80',None);right.pop('D80',None)
        assert left==right,'Unrelated override changed: '+key
    surface={'root':SITE,'locale':'id','state':'current-shared-corpus-capability','documents':[]}
    for locale,page,other in [('id','ledger.html','ledger-en.html'),('en','ledger-en.html','ledger.html')]:
        surface['documents'].append({'path':page,'locale':locale,'course_ids':['D80'],'contents_paths':[other],
          'related_course_surface_paths':['docs/backend/d80/D80.html','docs/backend/d80/D80-pengajar.html']})
    nav['course_surfaces']=[r for r in nav['course_surfaces'] if r['root']!=SITE]+[surface]
    for row in nav['course_surfaces']:
        if row['root']!='docs/backend/d80':continue
        row['exclude_subtrees']=list(dict.fromkeys([*row.get('exclude_subtrees',[]),'native-ledger']))
        for doc in row['documents']:
            doc['related_course_surface_paths']=list(dict.fromkeys([*doc.get('related_course_surface_paths',[]),SITE+'/ledger.html']))
    for original in nav_before['course_surfaces']:
        if original['root'] not in [SITE,'docs/backend/d80']:
            assert original==next(r for r in nav['course_surfaces'] if r['root']==original['root'])
    for key in nav_before:
        if key not in ['course_surfaces','summary']:assert nav_before[key]==nav[key]
    nav['summary']['course_surface_roots']=len(nav['course_surfaces'])
    nav['summary']['course_surface_html_documents']=sum(len(s['documents']) for s in nav['course_surfaces'])
    nav['summary']['classified_html_documents']=sum(nav['summary'][k] for k in ['reader_html_documents','gateway_html_documents','course_surface_html_documents','generic_html_documents'])
    nav['summary']['navigation_overlay_documents']=sum(nav['summary'][k] for k in ['reader_html_documents','gateway_html_documents','course_surface_html_documents'])+sum(bool(s['navigation_required']) for s in nav['generic_surfaces'])
    assert (ROOT/over_path).read_bytes()==old_raw and (ROOT/nav_path).read_bytes()==nav_raw,'Concurrent shared edit'
    save(over_path,over);save(nav_path,nav)
    receipt={'schema':'d80-native-ledger-admission/1','state':'locally_admitted_pending_publication','role':'D80',
      'summary':tests['summary'],'semantic_canon_approval':False,'native_book_rebuilt':False,'overall_backend_complete':False,
      'other_role_overrides_unchanged':True,'unrelated_navigation_preserved':True,'hosted_navigation_overlay_verified':refresh,
      'inputs':evidence,'overrides':fact(over_path),'navigation':fact(nav_path)}
    save(BASE+'/admission.json',receipt)
    print(json.dumps({'state':receipt['state'],'other39_preserved':True,'hosted_refresh':refresh}))

if __name__=='__main__':main()
