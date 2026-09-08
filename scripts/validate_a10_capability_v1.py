"""Independent A10 native-field/graph/PDF replay and adversarial checks.

Does not import the production model. No mathematical content is rewritten.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/a10-capability-v1'
NATIVE = ROOT / 'work/a10-native-inputs-v1'
ZIP_SHA = '6dc5ddafb3178d82308819ced69f724919dcb388168c5c63ec39db9e99777b13'
PDF_SHA = 'e4bc958edeb60a41604862dd0b67692bbfbcbb85b5de906c92af1f6c93bda505'
MANIFEST_SHA = 'f15ef8af0fec60c316896d0c60d8c01b1924b826eb1e8f4c62c883b8c59dd564'
AUTHORITY_SHA = '5ae589b75842923a0ebc530d649498bec9bb962ae0d14ab1cb44a9aedb573678'


def check(ok, code):
    if not ok: raise ValueError(code)


def digest(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def jsonl(path):
    with path.open(encoding='utf-8') as stream: return [json.loads(line) for line in stream]


def source_replay(native):
    check(digest(native/'backend-core.zip')==ZIP_SHA,'SOURCE-ZIP')
    check(digest(native/'reader.pdf')==PDF_SHA,'SOURCE-PDF')
    result={}; ledgers=[]
    with zipfile.ZipFile(native/'backend-core.zip') as archive:
        content=archive.read('exports/manifest.json');check(hashlib.sha256(content).hexdigest()==MANIFEST_SHA,'SOURCE-MANIFEST')
        manifest=json.loads(content)
        for spec in manifest['files']:
            if spec['format']!='jsonl':continue
            kind=spec['record_type'];rows={}; h=hashlib.sha256();size=0;ids=hashlib.sha256();count=0
            with archive.open('exports/'+spec['path']) as stream:
                for line in stream:
                    h.update(line);size+=len(line);count+=1
                    row=json.loads(line);ids.update((row['id']+'\n').encode())
                    if kind in {'unit','placement','relation','term','correction','rights','concept','segment','translation'}:
                        # Hash the exact source row before excluding prose payloads.
                        row['native_record_sha256']=hashlib.sha256(line).hexdigest()
                        for field in ('source_text','target_text','before_text','after_text','summary','rationale','disposition'):
                            if not (kind=='term' and field=='source_text'): row.pop(field,None)
                        check(row['id'] not in rows,'SOURCE-DUPLICATE'); rows[row['id']]=row
            check((count,size,h.hexdigest())==(spec['rows'],spec['bytes'],spec['sha256']),'SOURCE-STREAM:'+kind)
            ledgers.append({**spec,'path':'exports/'+spec['path'],'id_sequence_sha256':ids.hexdigest()})
            result[kind]=rows
    result['manifest']=manifest;result['ledgers']=ledgers
    return result


def compare_native_fields(output, source, additions=()):
    check(len(output)==len(source) and {r['id'] for r in output}==set(source),'PROJECTED-ID-SET')
    for row in output:
        original=source[row['id']]
        for key,value in row.items():
            if key in additions: continue
            check(key in original and value==original[key],'NATIVE-FIELD:'+key)
        check(row['native_record_sha256']==original['native_record_sha256'],'NATIVE-ROW-HASH')
        check(not ({'target_text','before_text','after_text','summary','rationale'} & set(row)),'NATIVE-BODY-COPY')


def exercise_check(rows, source, authority):
    units=source['unit']; ps={p['unit_id']:p for p in source['placement'].values()}
    ex={k:v for k,v in units.items() if v['kind']=='exercise'}
    check(len(rows)==9406 and {r['id'] for r in rows}==set(ex),'EXERCISE-COVERAGE')
    children=defaultdict(list); relations=defaultdict(list)
    for u in units.values():children[u['parent_unit_id']].append(u)
    for r in source['relation'].values():relations[r['subject_id'],r['predicate']].append(r)
    paths={}
    for eid in ex:
        chain=[];uid=eid;seen=set()
        while uid is not None:
            check(uid not in seen,'NATIVE-CYCLE');seen.add(uid)
            p=ps[uid];check(p['parent_unit_id']==units[uid]['parent_unit_id'],'NATIVE-PARENT')
            chain.append(p['ordinal']);uid=p['parent_unit_id']
        paths[eid]=list(reversed(chain))
    module_order={m['module_id']:m['ordinal'] for m in authority['modules']}
    expected_order=sorted(ex,key=lambda i:(module_order[ex[i]['source_module_id']],paths[i]))
    check([r['id'] for r in rows]==expected_order,'EXERCISE-ORDER')
    ordinal=defaultdict(int)
    for row in rows:
        eid=row['id'];unit=ex[eid];mid=unit['source_module_id'];ordinal[mid]+=1
        check(row['module_id']==mid and row['source_element_id']==unit['source_element_id'],'EXERCISE-SCOPE')
        check(row['ordinal_within_module']==ordinal[mid] and row['placement_order']==paths[eid],'EXERCISE-POSITION')
        check(row['ordinal_is_printed_exercise_number'] is False,'PRINTED-NUMBER-CLAIM')
        problem=[u for u in children[eid] if u['kind']=='problem']
        solution=[u for u in children[eid] if u['kind']=='solution']
        check(len(problem)==1 and len(solution)<=1,'NATIVE-CHILD-COUNTS')
        check(row['problem_id']==problem[0]['id'],'PROBLEM-JOIN')
        expected_solution=solution[0]['id'] if solution else None
        check(row['solution_id']==expected_solution,'SOLUTION-JOIN')
        check(row['problem_source_sha256']==problem[0]['source_fragment_sha256'],'PROBLEM-HASH')
        check(row['solution_source_sha256']==(solution[0]['source_fragment_sha256'] if solution else None),'SOLUTION-HASH')
        check(row['solution_status']==unit['solution_status'],'SOLUTION-STATUS')
        check(row['exercise_reading_route_verified'] is False,'FALSE-EXERCISE-ROUTE')
        problem_link=relations[eid,'has_problem']
        check(len(problem_link)==1 and problem_link[0]['object_id']==row['problem_id'] and
              row['has_problem_relation_id']==problem_link[0]['id'],'HAS-PROBLEM')
        state_link=relations[eid,'has_solution' if solution else 'solution_status']
        check(len(state_link)==1 and row['solution_state_relation_id']==state_link[0]['id'],'SOLUTION-STATE-RELATION')
        if solution:
            check(unit['solution_status']=='provided' and state_link[0]['qualifier']=='provided_upstream','PROVIDED-STATUS-DISTINCTION')
            inverse=relations[expected_solution,'solves']
            check(len(inverse)==1 and inverse[0]['object_id']==eid,'SOLVES-EXERCISE')
        else:
            check(unit['solution_status']=='not_provided_upstream' and state_link[0]['object_id'] is None,'EXPLICIT-MISSING')


def raw_pdf_destinations(native):
    from pypdf import PdfReader
    reader=PdfReader(native/'reader.pdf',strict=True)
    page_objects={(p.indirect_reference.idnum,p.indirect_reference.generation):i+1 for i,p in enumerate(reader.pages)}
    destinations={}
    def walk(node):
        node=node.get_object()
        for kid in node.get('/Kids',[]):walk(kid)
        names=node.get('/Names',[])
        check(len(names)%2==0,'PDF-NAMES-PAIRING')
        for i in range(0,len(names),2):
            value=names[i+1].get_object()
            array=value.get('/D') if isinstance(value,dict) else value
            ref=array[0];destinations[str(names[i])]=(page_objects[(ref.idnum,ref.generation)],ref.idnum,ref.generation)
    root=reader.trailer['/Root']
    if '/Dests' in root:
        # This reader uses the older direct catalog destination dictionary.
        for name,entry in root['/Dests'].items():
            value=entry.get_object();array=value.get('/D') if isinstance(value,dict) else value
            ref=array[0];destinations[str(name)]=(page_objects[(ref.idnum,ref.generation)],ref.idnum,ref.generation)
    else:
        walk(root['/Names']['/Dests'])
    return destinations


def validate(base, native):
    manifest=load(base/'manifest.json')
    for generator in manifest['generators']:
        check(digest(ROOT/generator['path'])==generator['sha256'] and (ROOT/generator['path']).stat().st_size==generator['bytes'],'GENERATOR-IDENTITY')
    for item in manifest['outputs']:
        path=base/item['path'];check(path.stat().st_size==item['bytes'] and digest(path)==item['sha256'],'OUTPUT-IDENTITY:'+item['path'])
    source=source_replay(native)
    authority_path=ROOT/'backend/v2.3/authorities/A10_ELEMENTARY_ALGEBRA_PUBLIC_RELEASE_AUTHORITY_20260906.json'
    check(digest(authority_path)==AUTHORITY_SHA,'AUTHORITY-IDENTITY');authority=load(authority_path)
    mapping={'unit-reference':'unit','placement':'placement','pedagogical-relation':'relation','concept':'concept','terms':'term','corrections':'correction','rights':'rights'}
    output={}
    for stem,kind in mapping.items():
        rows=jsonl(base/f'data/{stem}-index.jsonl'); output[kind]=rows
        expected=source[kind]
        if kind=='relation':expected={k:v for k,v in expected.items() if v['predicate'] in {'has_problem','has_solution','solves','solution_status','defines','denotes'}}
        additions={'unit':['native_module_title'],'term':['module_id','provenance_module_id','evidence_kind','superseded_by','supersedes','current_use_status'],'correction':['module_id','target_record_type']}.get(kind,[])
        compare_native_fields(rows,expected,additions)
    units=source['unit']
    history=jsonl(base/'data/terminology-history-index.jsonl')
    expected_history={k:r for k,r in source['relation'].items() if r['predicate']=='supersedes'}
    compare_native_fields(history,expected_history)
    for row in output['term']:
        expected=source['term'][row['id']]
        check(row['evidence_kind']==('curated_designation' if expected['ledger_id'] else 'source_occurrence_not_target_decision'),'TERM-PROMOTION')
        u=units.get(expected['owner_unit_id']) or units.get(expected['module_unit_id'])
        check(row['module_id']==(u['source_module_id'] if u else None),'TERM-MODULE')
        check(row['provenance_module_id']==row['module_id'],'TERM-PROVENANCE-MODULE')
        successors=sorted(r['subject_id'] for r in expected_history.values() if r['object_id']==row['id'])
        predecessors=sorted(r['object_id'] for r in expected_history.values() if r['subject_id']==row['id'])
        check(row['superseded_by']==successors and row['supersedes']==predecessors,'TERM-SUPERSESSION')
        check(row['current_use_status']==('superseded_in_native_ledger' if successors else 'native_record_not_superseded'),'TERM-SUPERSESSION-STATE')
    for row in output['correction']:
        u=units.get(source['correction'][row['id']]['target_id'])
        segment=source['segment'].get(row['target_id'])
        check(row['module_id']==(u['source_module_id'] if u else (segment['source_module_id'] if segment else None)),'CORRECTION-MODULE')
        check(row['target_record_type']==('unit' if u else ('segment' if segment else 'other_native_record')),'CORRECTION-TARGET-TYPE')
    target=jsonl(base/'data/translation-index.jsonl')
    compare_native_fields([r['segment'] for r in target],source['segment'])
    compare_native_fields([r['translation'] for r in target],source['translation'])
    for row in target:
        check(row['translation']['segment_id']==row['segment']['id'] and row['translation']['source_segment_sha256']==row['segment']['source_fragment_sha256'],'TRANSLATION-PAIR')
    exercises=jsonl(base/'data/exercise-index.jsonl');exercise_check(exercises,source,authority)
    modules=jsonl(base/'data/module-index.jsonl');check(len(modules)==82,'MODULE-COUNT')
    destinations=raw_pdf_destinations(native)
    pdf_url=next(i['url'] for i in load(base/'input/source-lock.json')['inputs'] if i['name']=='reader.pdf')
    for m,a in zip(modules,authority['modules'],strict=True):
        check(all(m.get(k)==v for k,v in a.items()),'MODULE-AUTHORITY-FIELDS')
        raw=destinations[m['named_destination']]
        check((m['physical_page'],*m['pdf_page_object'])==raw,'MODULE-PDF-OBJECT')
        check(m['url']==pdf_url+'#page='+str(raw[0]) and m['route_scope']=='module_start_not_exercise_or_solution','MODULE-ROUTE-SCOPE')
        native_module=units[m['module_unit_id']]
        check(native_module['kind']=='module' and native_module['source_module_id']==m['module_id'] and native_module['title']==m['title_en'],'MODULE-NATIVE-TITLE')
        selected=[r for r in exercises if r['module_id']==m['module_id']]
        check((m['exercise_count'],m['solution_count'],m['missing_solution_count'])==(len(selected),sum(bool(r['solution_id']) for r in selected),sum(not r['solution_id'] for r in selected)),'MODULE-COUNTS')
    module_urls={m['module_id']:m['url'] for m in modules}
    check(all(r['module_reading_url']==module_urls[r['module_id']] for r in exercises),'EXERCISE-MODULE-URL')
    ledger=load(base/'data/native-record-ledger.json')
    check(ledger['streams']==source['ledgers'] and ledger['record_counts']==source['manifest']['record_counts'] and ledger['records']==561994,'LEDGER-REPLAY')
    boundary=load(base/'data/claim-boundary.json')
    for key,value in boundary.items():
        if key.endswith('_claimed') or key in {'native_text_copied','native_source_formats_changed','complete_native_backend_reconstructed','component_rights_flattened','source_occurrences_are_target_term_decisions'}:
            check(value is False,'FALSE-CLAIM:'+key)
    negatives=[]
    def reject(name, operation):
        try:operation()
        except ValueError as error:negatives.append({'case':name,'result':'rejected','error':str(error)})
        else:raise ValueError('NEGATIVE-ACCEPTED:'+name)
    def exercise_mutation(index,key,value):
        altered=list(exercises);altered[index]={**altered[index],key:value};exercise_check(altered,source,authority)
    missing=next(i for i,r in enumerate(exercises) if not r['solution_id'])
    reject('invented-solution',lambda:exercise_mutation(missing,'solution_id','invented'))
    reject('wrong-problem',lambda:exercise_mutation(0,'problem_id',exercises[1]['problem_id']))
    reject('unscoped-source-id',lambda:exercise_mutation(0,'module_id',exercises[-1]['module_id']))
    reject('false-printed-number',lambda:exercise_mutation(0,'ordinal_is_printed_exercise_number',True))
    reject('erased-missing-state',lambda:exercise_mutation(missing,'solution_status','provided'))
    reject('false-exercise-route',lambda:exercise_mutation(0,'exercise_reading_route_verified',True))
    reject('wrong-order',lambda:exercise_check(list(reversed(exercises)),source,authority))
    reject('dropped-exercise',lambda:exercise_check(exercises[:-1],source,authority))
    reject('flattened-rights',lambda:compare_native_fields(output['rights'][:1],source['rights']))
    reject('dropped-correction',lambda:compare_native_fields(output['correction'][:-1],source['correction'],['module_id','target_record_type']))
    bad_terms=copy.deepcopy(output['term']);bad_terms[0]['preferred_target_text']='unattested'
    reject('invented-target-term',lambda:compare_native_fields(bad_terms,source['term'],['module_id','provenance_module_id','evidence_kind','superseded_by','supersedes','current_use_status']))
    bad_targets=copy.deepcopy(target[:1]);bad_targets[0]['translation']['target_text']='copied body'
    reject('copied-translation-body',lambda:compare_native_fields([bad_targets[0]['translation']],{bad_targets[0]['translation']['id']:source['translation'][bad_targets[0]['translation']['id']]}))
    return {'schema':'a10-capability-validation/1','result':'pass','course_id':'A10',
        'counts':manifest['counts'],'negative_fixtures':negatives,
        'checks':{'generator_source_hashes_verified':True,'independent_native_field_replay':True,'all_19_native_streams_verified':True,
            'exercise_child_and_relation_replay':True,'placement_ancestry_replayed':True,
            'pdf_raw_name_tree_page_objects_replayed':True,'term_decision_classes_preserved':True,
            'component_rights_preserved':True,'translation_segment_hashes_preserved':True,
            'browser_visual_qa_claimed':False,'whole_program_completion_claimed':False},
        'manifest_sha256':digest(base/'manifest.json')}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter',type=Path,default=BASE)
    parser.add_argument('--native',type=Path,default=NATIVE)
    parser.add_argument('--rebuild',action='store_true')
    args=parser.parse_args();result=validate(args.adapter,args.native)
    node=subprocess.run(['node',str(ROOT/'scripts/test_a10_navigator_v1.mjs'),str(args.adapter)],check=True,capture_output=True,text=True)
    result['navigation_tests']=json.loads(node.stdout)
    if args.rebuild:
        replay=ROOT/'work/a10-independent-rebuild-v1'
        subprocess.run([sys.executable,str(ROOT/'scripts/build_a10_capability_v1.py'),'--native',str(args.native),'--destination',str(replay)],check=True,capture_output=True,text=True)
        manifest=load(args.adapter/'manifest.json')
        for item in manifest['outputs']:
            check(digest(replay/item['path'])==item['sha256'],'NONDETERMINISTIC:'+item['path'])
        check(digest(replay/'manifest.json')==digest(args.adapter/'manifest.json'),'NONDETERMINISTIC-MANIFEST')
        result['checks']['independent_second_build_byte_identical']=True
        result['deterministic_output_count']=len(manifest['outputs'])+1
    result['validator_sha256']=digest(Path(__file__))
    content=(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
    (args.adapter/'validation.json').write_bytes(content)
    print(json.dumps(result,ensure_ascii=True))
