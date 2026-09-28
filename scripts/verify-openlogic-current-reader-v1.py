"""Verify the combined public reader against both unchanged PDF components."""
import argparse
import hashlib
import json
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
BASE='https://github.com/KokunoYumeto/OpenLogic-id/releases/download/id-olp-0722-20260814/'
FILES={
    'main':('00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf',5593664,'bf538d5e1994a7a7600703c9d24616696f77e43e9312fb51078095ff0c963c0a',1116),
    'supplement':('04_OPENLOGIC_id_READER_SUPPLEMENT_80_20260904.pdf',857775,'bad0b8a0e22652cccab782e6e159868e00e137796d41578b3dd649b8a1831bae',139),
    'combined':('08_OPENLOGIC_id_STANDALONE_READER_ALL_722_20260905.pdf',5754676,'1b763b8b15c9f28a1212d81ee3e3a3f60ee3212fe1ffa4620c947caf43c89930',1255),
}


def verify(cache):
    pdfs={};identities={}
    for key,(name,size,digest,pages) in FILES.items():
        data=(cache/name).read_bytes()
        assert len(data)==size and hashlib.sha256(data).hexdigest()==digest,name
        pdfs[key]=fitz.open(stream=data,filetype='pdf')
        assert len(pdfs[key])==pages
        identities[key]={'filename':name,'url':BASE+name,'bytes':size,'sha256':digest,'pages':pages}
    main,supp,combined=(pdfs[k] for k in ['main','supplement','combined'])
    ordered=hashlib.sha256()
    for i in range(len(combined)):
        origin=main[i] if i<len(main) else supp[i-len(main)]
        current=combined[i]
        assert origin.rect==current.rect and origin.rotation==current.rotation,('geometry',i+1)
        assert origin.get_text()==current.get_text(),('text',i+1)
        ordered.update(current.get_text().encode('utf-8'))
    # Compare the actual public unit-source coverage rather than importing the
    # producer's completion prose as an independent certification.
    native=ROOT/'backend/course-capsule-v1/adapters/openlogic-v231/tables/units.jsonl'
    units=[json.loads(line) for line in native.read_bytes().splitlines()]
    assert len(units)==722 and sum(u['payload']['canonical_reader_reachable'] for u in units)==642
    qa_data=(cache/'STANDALONE_READER_QA.json').read_bytes()
    assert hashlib.sha256(qa_data).hexdigest()=='c3b872029babb13822835edae90c08bfce52d6d799c8e6de07e3765d9fe6bc47'
    qa=json.loads(qa_data)
    assert qa['accepted_inventory']['sha256']=='964a274b418c06c99130ad33e8326629d5c35bf677d7c9a6166c19a6f91a033b'
    assert qa['component_units']=={'main_reader':642,'supplement':80,'combined':722}
    main_names=main.resolve_names(); combined_names=combined.resolve_names()
    assert main_names=={k:v for k,v in combined_names.items() if k in main_names}
    result={
        'schema_id':'interlanguage/openlogic-current-reader/v1','recorded_at':'2026-09-28',
        'status':'pass','course_id':'C80','primary_reader':identities['combined'],
        'predecessor_reader':identities['main'],'supplement_reader':identities['supplement'],
        'release':'https://github.com/KokunoYumeto/OpenLogic-id/releases/tag/id-olp-0722-20260814',
        'concept_doi':'10.5281/zenodo.21932786',
        'components':{'main_units':642,'supplement_units':80,'combined_units':722,'supplement_starts_at_physical_page':1117},
        'verification':{'all_three_artifact_hashes_checked':True,'page_geometry_equal':1255,
                        'ordered_page_text_equal':1255,'ordered_text_sha256':ordered.hexdigest(),
                        'main_named_destinations_preserved':len(main_names),
                        'new_translation_quality_audit':False,'exercise_alignment_complete':False,
                        'supplement_unit_coverage_basis':'Hash-bound producer QA linked to the accepted 722-unit inventory; not a new semantic completeness audit.'},
        'producer_qa':{'url':BASE+'STANDALONE_READER_QA.json','bytes':len(qa_data),'sha256':hashlib.sha256(qa_data).hexdigest()},
        'native_units':{'bytes':native.stat().st_size,'sha256':hashlib.sha256(native.read_bytes()).hexdigest()},
    }
    for doc in pdfs.values():doc.close()
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--out',type=Path,default=ROOT/'backend/course-capsule-v1/authority/openlogic-current-reader-v1.json')
    args=p.parse_args();result=verify(args.cache)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':result['status'],'pages':result['primary_reader']['pages'],'verification':result['verification']}))


if __name__=='__main__':main()
