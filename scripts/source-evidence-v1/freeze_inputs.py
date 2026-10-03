"""Freeze bounded existing evidence, not any corpus or full workspace."""
from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
import argparse,hashlib,json
from source_use_projection import encoded,pin,relpath,need,project

WORK=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(root,name):
    relpath(name);p=(root/name).resolve();need(p.is_relative_to(root) and p.is_file(),'Missing/escaping input '+name)
    need(p.stat().st_size<4*1024*1024,'Input size exceeds bound')
    return p.read_bytes()
class Anchors(HTMLParser):
    def __init__(self):super().__init__();self.ids=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k=='id':self.ids.append(v)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core',type=Path,required=True)
    parser.add_argument('--advanced',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    CORE=args.core.resolve();ADV=args.advanced.resolve()
    target=args.output.resolve();need(not target.exists(),'Do not overwrite frozen inputs')
    bridge_raw=read(CORE,'backend/cross-programme-v1/bridge.json');bridge=json.loads(bridge_raw)
    catalog_raw=read(ADV,'courses/catalog.json');catalog=json.loads(catalog_raw)
    courses={c['id']:c for c in catalog['courses']};facts={};evidence={};observations={}
    def bound(row):
        raw=read(CORE,row['path']);actual={'path':row['path'],'bytes':len(raw),'sha256':sha(raw)}
        need(actual['bytes']==row['bytes'] and actual['sha256']==pin(row['sha256']),'Existing bound evidence changed: '+row['path'])
        facts['core/'+row['path']]=actual
        if row['path'].endswith('.json'):evidence[sha(raw)]=json.loads(raw)
        return raw
    def current(cid,uid):
        matches=[u for u in courses[cid]['units'] if u['id']==uid]
        need(len(matches)==1,'Current native ID missing or ambiguous')
        u=matches[0];raw=read(ADV,'courses/'+u['source'])
        return {'course_id':cid,'unit_id':uid,'source_path':'courses/'+u['source'],'bytes':len(raw),'sha256':sha(raw),'catalog_declared_sha256':pin(u['source_sha256']),'catalog_claim_matches_bytes':sha(raw)==pin(u['source_sha256']),'status':u.get('status'),'proof_status':u.get('proof_status'),'admission':u.get('admission'),'translation':u.get('translation'),'formalization':u.get('formalization')}
    for req in bridge['current_result_requirements']:
        for row in [req['consumer']['source'],req['provider']['source'],req['provider']['route'],req['provider']['reader_manifest'],req['author_review']]:bound(row)
        obs={'current_consumer':current(req['consumer']['course'],req['consumer']['lesson']),'provider_source':'Exact bound source identity checked in this intake'}
        reader_manifest=evidence[pin(req['provider']['reader_manifest']['sha256'])]
        base=Path(req['provider']['reader_manifest']['path']).parent
        reader=read(CORE,(base/'index.html').as_posix());a=Anchors();a.feed(reader.decode())
        obs['local_provider_reader']={'bytes':len(reader),'sha256':sha(reader),'proof_anchors':[{'anchor':key,'occurrences':a.ids.count(key)} for key in req['provider']['proof_anchors']],'network_readback_performed':False}
        need(all(r['occurrences']==1 for r in obs['local_provider_reader']['proof_anchors']),'Missing/duplicate exact provider anchor')
        observations['requirement:'+req['id']]=obs
        # Preserve the existing exact human source-binding metadata when supplied.
        for item in reader_manifest['files']:
            if item['path'] in ('SOURCE_BINDINGS.json','HEFFERON-LICENSE.txt','HEFFERON-ACKNOWLEDGEMENTS.txt'):
                bound(dict(item,path=(base/item['path']).as_posix()))
    for provider in bridge['native_phone_exchange']['reported_providers']:
        cid,uid=provider['proof']['unit'].split('/',1)
        observations['provider:'+provider['id']]={'current_source':current(cid,uid),'content_language':None,'language_note':'No per-item language assertion copied from this provider report; do not infer it from interface locale'}
    selected={'current_result_requirements':bridge['current_result_requirements'],'reported_providers':bridge['native_phone_exchange']['reported_providers'],'source_bound_lesson_routes':bridge['source_bound_lesson_routes']}
    bundle={'schema':'existing-proof-evidence-input/1','freeze_utc':datetime.now(timezone.utc).isoformat(),'bridge_identity':{'path':'backend/cross-programme-v1/bridge.json','bytes':len(bridge_raw),'sha256':sha(bridge_raw)},'catalog_identity':{'path':'courses/catalog.json','bytes':len(catalog_raw),'sha256':sha(catalog_raw)},'selected_bridge':selected,'bound_file_facts':facts,'evidence':evidence,'observations':observations,'scope':'Frozen selected existing records and explicit source checks; no full-core proof rereading or owner mutation'}
    result=project(bundle)
    with target.open('xb') as out:out.write(encoded(bundle))
    print(json.dumps({'input_bytes':target.stat().st_size,'input_sha256':sha(target.read_bytes()),'counts':result['counts'],'revision_states':{r['id']:r.get('current_revision_state') for r in result['records'] if 'current_revision_state' in r}}))
if __name__=='__main__':main()
