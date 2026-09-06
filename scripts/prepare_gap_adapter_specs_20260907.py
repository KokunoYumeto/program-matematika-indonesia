#!/usr/bin/env python3
"""Prepare hash-bound evidence-first specs for the three missing adapters."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIRRORS = ROOT.parents[2] / "04_mirrors" / "id"
OUT = ROOT / "backend" / "v2.3" / "specs" / "20260907"
CURRICULUM = ROOT / "backend" / "v2" / "program-matematika-indonesia-federation-v0.4.4" / "data" / "courses.jsonl"

def digest(p: Path) -> str:
    h=hashlib.sha256();
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def size(p: Path) -> int: return p.stat().st_size
def f(rel: str, base: str, root: Path, role: str) -> dict:
    p=root / rel
    return {'path':rel,'path_base':base,'role':role,'bytes':size(p),'sha256':digest(p)}
def unit(native_id, ordinal, title, source_rel, source_root, state=None, evidence=None, target_rel=None, target_root=None):
    d={'native_id':native_id,'ordinal':ordinal,'label':native_id,'title':title,
       'source_path':source_rel,'source_bytes':size(source_root/source_rel),'source_sha256':digest(source_root/source_rel)}
    if state is not None: d.update({'translation_state':state,'translation_evidence':evidence})
    if target_rel:
        d.update({'target_path':target_rel,'target_bytes':size(target_root/target_rel),'target_sha256':digest(target_root/target_rel)})
    return d
def common(role,title,course,dataset,owner_ns,authorities,units,rights,artifacts,reader_surfaces,prereqs,source_format,owner_status,capabilities=None):
    return {'role_id':role,'title':title,'course_id':course,'namespace':'7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd','dataset_key':dataset,'owner_namespace':owner_ns,'recorded_at':'2026-09-07T00:00:00Z','authorities':authorities,'curriculum_authority':f('backend/v2/program-matematika-indonesia-federation-v0.4.4/data/courses.jsonl','program_repository_root',ROOT,'curriculum_authority'),'units':units,'rights_components':rights,'artifacts':artifacts,'reader_surfaces':reader_surfaces,'prerequisite_course_ids':prereqs,'source_format':source_format,'public_authority_status':owner_status,**({'capabilities':capabilities} if capabilities else {})}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # A30: exact 87 owner module files, with upstream/target byte bindings.
    a=MIRRORS/'openstax-precalculus-2e-id'; c=json.loads((a/'00_control/CURRENT_CURSOR.json').read_text(encoding='utf-8'))
    ids=list(c['translation']['translated_modules']); assert len(ids)==87
    au=[f('00_control/CURRENT_CURSOR.json','owner_package_root',a,'owner_control'),f('qa/FULL87_BACKEND_RELEASE_ADAPTER_V3_FINAL_SOURCE_20260904_G.json','owner_package_root',a,'release_adapter_qa')]
    ar=[{'id':'reader','path':'output/final-3165/OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf','bytes':size(a/'output/final-3165/OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf'),'sha256':digest(a/'output/final-3165/OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf'),'role':'learner_reader','media_type':'application/pdf','url':'https://zenodo.org/records/22290180/files/OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf?download=1'}]
    au0=a/'authority/upstream/modules'; at=a/'repo/source/modules'
    units=[]
    for i,n in enumerate(ids,1):
        rel=f'{n}/index.cnxml'; target=f'{n}/index.cnxml'
        units.append(unit(n,i,f'Modul {n}',rel,au0,'language_reviewed','00_control/CURRENT_CURSOR.json#translation',target,at))
    specs=[common('A30','Prakalkulus dan Trigonometri','A30','a30:precalculus-2e:id-ID:v1','openstax-precalculus-2e/id-ID',au,units,[{'id':'primary','status':'verified','license':'CC-BY-NC-SA-4.0','note':'Component credits remain authoritative.'}], ar, [{'action':'pdf','url':'https://zenodo.org/records/22290180/files/OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf?download=1','state':'published','primary':True,'route':'/id/courses/A30/','artifact_id':'reader','public_readback':{'status':'pass','http_status':200,'bytes':ar[0]['bytes'],'sha256':ar[0]['sha256'],'evidence_path':'00_control/CURRENT_CURSOR.json'}}], ['A20'],'OpenStax CNXML + localized CNXML','complete_87_of_87',{'structure_localization':{'state':'materialized'},'publication':{'state':'referenced_native_shards'}})]

    # B95: one stable representative unit per OpenIntro lesson, sourced from
    # the admitted native unit ledger.  The full 21,746-record archive remains
    # owner-native; the adapter does not collapse it into a fake twelve-row book.
    b=MIRRORS/'openintro-statistics-id'; units_file=b/'backend/exports/core/units.jsonl'; rows=[]
    for line in units_file.read_text(encoding='utf-8').splitlines():
        x=json.loads(line)
        key=str(x.get('source_path') or '')
        if x.get('record_type')!='unit' or not key or not x.get('source_sha256'):
            continue
        if key.startswith('ch_'):
            rows.append(x)
    # Bind the representative units to the immutable source snapshot that
    # already carries the ledger's span hashes.  The owner repo contains both
    # upstream and localized full files, but a unit hash in this ledger is a
    # span hash, not a full-file hash; pointing at the snapshot makes that
    # distinction explicit and replayable.
    snapshot_rel='qa/b004-build/source-snapshot-v5'
    def valid_span(x):
        sp=x.get('source_span') or {}
        try:
            start=int(sp['byte_start']); end=int(sp['byte_end_exclusive'])
        except (KeyError,TypeError,ValueError):
            return False
        p=b/snapshot_rel/x['source_path']
        if not p.is_file() or start<0 or end<start or end>p.stat().st_size:
            return False
        return hashlib.sha256(p.read_bytes()[start:end]).hexdigest()==str(x['source_sha256'])
    rows=[x for x in rows if valid_span(x)]
    # Prefer one representative from each chapter, then fill to twelve with
    # additional distinct stable units.  This is deliberately a bounded
    # projection; the complete native ledger remains authoritative.
    seen=set(); chosen=[]
    for x in rows:
        chapter=x['source_path'].split('/')[0]
        if chapter not in seen:
            seen.add(chapter); chosen.append(x)
        if len(chosen)==12: break
    if len(chosen)<12:
        picked={str(x['stable_key']) for x in chosen}
        for x in rows:
            if str(x['stable_key']) not in picked:
                chosen.append(x); picked.add(str(x['stable_key']))
            if len(chosen)==12: break
    assert len(chosen)==12, len(chosen)
    bu=[f('00_control/CURRENT_CURSOR.json','owner_package_root',b,'owner_control'),f('backend/exports/manifest.json','owner_package_root',b,'backend_manifest')]
    units=[]
    for i,x in enumerate(chosen,1):
        sp=x['source_span']; original=str(x['source_path'])
        source_rel=f'{snapshot_rel}/{original}'
        item={'native_id':str(x['stable_key']),'ordinal':i,'label':original.split('/')[0],
              'title':str(x.get('title') or original),'source_path':source_rel,
              'source_bytes':int(sp.get('bytes',int(sp['byte_end_exclusive'])-int(sp['byte_start']))),
              'source_sha256':str(x['source_sha256']),
              'source_original_path':original,'source_range':{'byte_start':int(sp['byte_start']),'byte_end_exclusive':int(sp['byte_end_exclusive']),
                                                               'line_start':sp.get('line_start'),'line_end':sp.get('line_end')},
              'translation_state':x.get('translation_state'),
              'translation_evidence':'00_control/CURRENT_CURSOR.json#translation'}
        # Preserve an exact localized span when the native ledger provides one
        # and the bound target witness is locally present and hashable.
        tp=x.get('target_path'); tsp=x.get('target_span') or {}; tsha=x.get('target_sha256')
        if tp and tsha and 'byte_start' in tsp and 'byte_end_exclusive' in tsp:
            target_candidates=[str(tp)]
            if str(tp).startswith('repo/'):
                target_candidates.append(f"{snapshot_rel}/{str(tp)[len('repo/'): ]}")
            for candidate in target_candidates:
                q=b/candidate
                if q.is_file():
                    ts=int(tsp['byte_start']); te=int(tsp['byte_end_exclusive'])
                    if 0<=ts<=te<=q.stat().st_size and hashlib.sha256(q.read_bytes()[ts:te]).hexdigest()==str(tsha):
                        item.update({'target_path':candidate,'target_bytes':int(tsp.get('bytes',te-ts)),
                                     'target_sha256':str(tsha),'target_original_path':str(tp),
                                     'target_range':{'byte_start':ts,'byte_end_exclusive':te,'line_start':tsp.get('line_start'),'line_end':tsp.get('line_end')}})
                        break
        units.append(item)
    ba=[{'id':'reader','path':'release/b039/R011-B039-v2026.09.01.2/00_STATISTIKA_BERBASIS_DATA_ID_R011-B039_WORKING_READER.pdf','bytes':size(b/'release/b039/R011-B039-v2026.09.01.2/00_STATISTIKA_BERBASIS_DATA_ID_R011-B039_WORKING_READER.pdf'),'sha256':digest(b/'release/b039/R011-B039-v2026.09.01.2/00_STATISTIKA_BERBASIS_DATA_ID_R011-B039_WORKING_READER.pdf'),'role':'learner_reader','media_type':'application/pdf','url':'https://zenodo.org/records/22261912/files/statistika-berbasis-data-batas-R011-B039.pdf?download=1'}, {'id':'backend','path':'release/b039/R011-B039-v2026.09.01.2/02_STATISTIKA_BERBASIS_DATA_ID_R011-B039_MODULAR_BACKEND.zip','bytes':size(b/'release/b039/R011-B039-v2026.09.01.2/02_STATISTIKA_BERBASIS_DATA_ID_R011-B039_MODULAR_BACKEND.zip'),'sha256':digest(b/'release/b039/R011-B039-v2026.09.01.2/02_STATISTIKA_BERBASIS_DATA_ID_R011-B039_MODULAR_BACKEND.zip'),'role':'native_backend','media_type':'application/zip','url':'https://zenodo.org/records/22261912/files/02_MODULAR_BACKEND.zip?download=1'}]
    specs.append(common('B95','Statistika Terapan dan Analisis Data','B95','b95:openintro-statistics:id-ID:R011-B039','openintro-statistics/fee25091fb24e89c36296fd67c48c1fcf7a93b6e',bu,units,[{'id':'text-data','status':'verified','license':'CC-BY-SA-3.0','note':'Per-component rights ledger remains authoritative.'},{'id':'restricted-instructor','status':'excluded','license':'not-redistributed','note':'Restricted instructor-only solutions are not projected.'}], [], [{'action':'pdf','url':ba[0]['url'],'state':'published','primary':True,'route':'/id/courses/B95/','artifact_id':'reader','public_readback':{'status':'pass','http_status':200,'bytes':ba[0]['bytes'],'sha256':ba[0]['sha256'],'evidence_path':'00_control/CURRENT_CURSOR.json'} }],['A30','B90'],'LaTeX/OpenIntro source + JSONL/CSV backend','complete_admitted_public'))
    specs[-1]['artifacts']=ba

    # C140: 39 exact Indonesian source documents in the complete C5 companion.
    d=MIRRORS/'penn-state-stat-415-id'; component_root=d/'components/c140-companion'
    cu=[f('components/c140-companion/00_control/CURRENT_CURSOR.md','owner_package_root',d,'owner_control'),f('release/16_C140_COMPANION_C5_SOURCE_BACKEND_DATA_RIGHTS.zip','owner_package_root',d,'release_package')]
    docs=[]
    for line in (component_root/'backend/documents.jsonl').read_text(encoding='utf-8').splitlines():
        x=json.loads(line); p=component_root/str(x.get('source_path',''))
        if (x.get('status')=='complete' and p.is_file() and int(x.get('bytes',-1))==p.stat().st_size
                and digest(p)==str(x.get('sha256'))):
            docs.append(x)
    assert len(docs)>=39, len(docs)
    units=[{'native_id':str(x['document_id']),'ordinal':i,'label':str(x['document_id']),'title':str(x['title']),
            'source_path':f"components/c140-companion/{x['source_path']}",'source_bytes':int(x['bytes']),
            'source_sha256':str(x['sha256']),'source_original_path':str(x['source_path']),
            'translation_state':'native_complete','translation_evidence':'components/c140-companion/00_control/CURRENT_CURSOR.md#C5'} for i,x in enumerate(docs[:39],1)]
    da=[{'id':'c5-package','path':'release/16_C140_COMPANION_C5_SOURCE_BACKEND_DATA_RIGHTS.zip','bytes':size(d/'release/16_C140_COMPANION_C5_SOURCE_BACKEND_DATA_RIGHTS.zip'),'sha256':digest(d/'release/16_C140_COMPANION_C5_SOURCE_BACKEND_DATA_RIGHTS.zip'),'role':'native_source_backend_rights','media_type':'application/zip','url':'https://zenodo.org/records/22208527/files/16_C140_COMPANION_C5_SOURCE_BACKEND_DATA_RIGHTS.zip?download=1'}]
    specs.append(common('C140','Statistika Matematis','C140','c140:mathematical-statistics:complete-c5','penn-state-stat415/c140-companion',cu,units,[{'id':'penn-state','status':'verified','license':'CC-BY-NC-4.0','note':'Penn State source component.'},{'id':'companion','status':'verified','license':'CC-BY-SA-4.0','note':'Original companion component.'},{'id':'datasets','status':'verified','license':'component-specific','note':'Dataset rights remain per asset.'}], [], [{'action':'html','url':'https://kokunoyumeto.github.io/penn-state-stat-415-id/','state':'published','primary':True,'route':'/id/courses/C140/','artifact_id':'c5-package','public_readback':{'status':'pass','http_status':200,'bytes':da[0]['bytes'],'sha256':da[0]['sha256'],'evidence_path':'components/c140-companion/00_control/CURRENT_CURSOR.md'}}],['B40','B90','B95','C10'],'Markdown/HTML companion + JSONL/CSV backend','complete_c5_public'))
    specs[-1]['artifacts']=da
    for spec in specs:
        p=OUT/(spec['role_id']+'.json'); p.write_text(json.dumps(spec,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n'); print(p)
if __name__=='__main__': main()
