#!/usr/bin/env python3
"""Stage independently replayed CLP-1 English bytes; native corpus remains untouched."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'docs/en/courses/B20/reader'
def fact(b):return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def put(p,b):
    if p.exists():assert p.read_bytes()==b,'Existing different B20 bytes: '+str(p.relative_to(ROOT))
    else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def run(mirror):
    proof=mirror/'output';raw=(proof/'B20_FINAL_LOCAL_VALIDATION.json').read_bytes();receipt=json.loads(raw)
    assert receipt['state']=='pass' and receipt['replay']['normalized_reader_byte_equality']
    assert receipt['coverage']['exercise']==695 and receipt['coverage']['solution']==695
    for row in receipt['files']:
        rel=Path(row['path']);assert not rel.is_absolute() and '..' not in rel.parts
        data=(proof/'reader'/rel).read_bytes();assert fact(data)=={k:row[k] for k in ['bytes','sha256']}
        put(DEST/rel,data)
    checks=['B20_FINAL_LOCAL_VALIDATION.json','B20_PRE_ADMISSION_AUDIT.json','B20_NAVIGATION_REPAIR.json','B20_FRAGMENT_NAVIGATION.json','B20_LOCALIZATION_RECEIPT.json']
    for name in checks:put(ROOT/'docs/en/courses/B20/evidence'/name,(proof/name).read_bytes())
    admission={'schema':'central-original-reader-admission/1','course_id':'B20','language':'en',
        'source_revision':receipt['source_commit'],'source_tree':receipt['source_tree'],
        'original':'https://personal.math.ubc.ca/~CLP/CLP1/',
        'reader':'https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/B20/reader/',
        'native_source_unchanged':True,'translation_performed':False,'source_license':'CC BY-NC-SA 4.0; runtime/tooling notices separate',
        'coverage':receipt['coverage'],'main_reader_pages':83,'standalone_excerpts':323,'generated_diagrams':320,
        'source_unit_routes':45821,'source_unit_route_sidecar_is_not_native_capability_parity':True,
        'local_validation':fact(raw),'source_projection_files':receipt['files'],'public_readback':'pending',
        'navigation':'Program/original/contents shell; standalone excerpt runtime and shell excluded from embedded clones.',
        'replay':receipt['replay'],'owner_mutation':False}
    put(ROOT/'docs/en/courses/B20/B20_ORIGINAL_ENGLISH_ADMISSION_V1.json',(json.dumps(admission,indent=2)+'\n').encode())
    p=ROOT/'backend/authority/central-reader-navigation-v1.json';contract=json.loads(p.read_bytes())
    existing=[r for r in contract['readers'] if r['root']=='docs/en/courses/B20/reader']
    assert not existing,'B20 already registered; inspect before any repeat staging'
    fragments=sorted(p.relative_to(DEST).as_posix() for p in (DEST/'knowl').rglob('*.html'));assert len(fragments)==323
    contract['readers'].append({'course_id':'B20','locale':'en','root':'docs/en/courses/B20/reader',
        'html_documents':406,'standalone_reader_pages':83,'embedded_fragment_paths':fragments,'state':'current',
        'source_navigation':'central-overlay-only','landing_document':'docs/en/index.html','course_fragment':'course-B20',
        'public_root':admission['reader'],'landing_required_paths':[''],
        'navigation_closure':{'entry_path':'index.html','contents_paths':['index.html','front.html'],
            'overlay_links':{'sec_chain_rule.html':['knowl/xref/eg_DIFFcampfire.html']}}})
    contract['summary']['reader_roots']+=1
    for key in ['reader_html_documents','navigation_overlay_documents','classified_html_documents']:contract['summary'][key]+=406
    p.write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'state':'staged_pending_publication','files':len(receipt['files']),'reader_html':406}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mirror',type=Path,required=True);run(parser.parse_args().mirror.resolve())
