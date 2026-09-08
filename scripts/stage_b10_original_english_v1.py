#!/usr/bin/env python3
"""Stage the verified original-English B10 reader without editing native owners."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'docs/en/courses/B10/reader'
def sha(b):return hashlib.sha256(b).hexdigest()
def fact(b):return {'bytes':len(b),'sha256':sha(b)}
def put(p,b):
    if p.exists() and p.read_bytes()==b:return
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def run(mirror):
    proof=mirror/'output-complete';receipt_bytes=(proof/'B10_FINAL_LOCAL_VALIDATION.json').read_bytes()
    receipt=json.loads(receipt_bytes)
    assert receipt['state']=='pass' and receipt['replay']['state']=='pass'
    assert receipt['coverage']['selected_exercises']==768 and receipt['coverage']['source_provided_solutions']==520
    spec=importlib.util.spec_from_file_location('overlay',ROOT/'scripts/apply-central-course-surface-navigation-v1.py')
    overlay=importlib.util.module_from_spec(spec);spec.loader.exec_module(overlay)
    for row in receipt['files']:
        rel=Path(row['path']);assert not rel.is_absolute() and '..' not in rel.parts
        b=(proof/'reader'/rel).read_bytes();assert fact(b)=={k:row[k] for k in ('bytes','sha256')}
        target=DEST/rel
        if target.is_file() and target.suffix=='.html':
            stripped=overlay.strip_owned_overlay(target.read_text(encoding='utf-8'),target.relative_to(ROOT).as_posix()).encode()
            if stripped==b:continue
        put(target,b)
    for name in ['B10_FINAL_LOCAL_VALIDATION.json',*receipt['checks']]:
        b=(proof/name).read_bytes()
        if name in receipt['checks']:assert fact(b)==receipt['checks'][name]
        put(ROOT/'docs/en/courses/B10/evidence'/name,b)
    admission={'schema':'central-original-reader-admission/1','course_id':'B10','language':'en',
        'source_revision':receipt['source_commit'],'source_tree':receipt['source_tree'],
        'original':'https://discrete.openmathbooks.org/dmoi4/',
        'reader':'https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/B10/reader/',
        'native_source_unchanged':True,'translation_performed':False,'source_license':'CC BY-NC-SA 4.0',
        'coverage':receipt['coverage'],'source_unit_route_sidecar_is_not_native_capability_parity':True,
        'local_validation':fact(receipt_bytes),'source_projection_files':receipt['files'],
        'public_readback':'pending','owner_mutation':False,
        'navigation':'Reversible program/original/contents shell; popup loader removes only this shell from embedded clones.',
        'remote_services':'SageCell, GeoGebra and remote exercise-checking services still need internet access.'}
    put(ROOT/'docs/en/courses/B10/B10_ORIGINAL_ENGLISH_ADMISSION_V1.json',(json.dumps(admission,indent=2)+'\n').encode())
    contract_path=ROOT/'backend/authority/central-reader-navigation-v1.json'
    contract=json.loads(contract_path.read_bytes())
    assert not any(r['root']=='docs/en/courses/B10/reader' for r in contract['readers'])
    fragments=sorted(p.relative_to(DEST).as_posix() for p in (DEST/'knowl').rglob('*.html'))
    assert len(fragments)==470
    contract['readers'].append({'course_id':'B10','locale':'en','root':'docs/en/courses/B10/reader',
        'html_documents':553,'standalone_reader_pages':83,'embedded_fragment_paths':fragments,
        'state':'current','source_navigation':'central-overlay-only','landing_document':'docs/en/index.html',
        'course_fragment':'course-B10','public_root':admission['reader'],'landing_required_paths':[''],
        'navigation_closure':{'entry_path':'index.html','contents_paths':['index.html','frontmatter.html'],
            'overlay_links':{'sec_seq_intro.html':['interactive-hanoi-2.html','knowl/xref/interactive-hanoi-2.html']}}})
    contract['summary']['reader_roots']+=1
    for key in ['reader_html_documents','navigation_overlay_documents','classified_html_documents']:contract['summary'][key]+=553
    contract['policy']['embedded_excerpt_navigation']='Typed PreTeXt excerpt routes are reached through their native data-knowl controls. Standalone excerpts retain return navigation; the reader removes that shell from the embedded clone only.'
    put(contract_path,(json.dumps(contract,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'state':'staged_pending_publication','files':len(receipt['files']),'coverage':receipt['coverage']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mirror',required=True,type=Path);a=p.parse_args();run(a.mirror.resolve())
