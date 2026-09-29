"""Verify explicit, source-grounded supplement exercise identity decisions."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import re
import zipfile

import fitz

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('supp',ROOT/'scripts/map-openlogic-supplement-v1.py')
supp=importlib.util.module_from_spec(spec)
spec.loader.exec_module(supp)
intake=supp.intake
PDF='04_OPENLOGIC_id_READER_SUPPLEMENT_80_20260904.pdf'
BASE='https://github.com/KokunoYumeto/OpenLogic-id/releases/download/id-olp-0722-20260814/'


def normalized(text):
    """Only layout normalization, never math/operator substitution."""
    text=text.replace('\u00ad','').replace('ﬁ','fi').replace('ﬂ','fl')
    text=re.sub(r'(?<=[A-Za-z])-\s*\n\s*(?=[a-z])','',text)
    return ' '.join(text.split())


def verify_choice(choice, source_body, candidates, destinations):
    assert choice['source_exact'] and choice['pdf_exact'],'Empty witness'
    source=normalized(source_body)
    for witness in choice['source_exact']:
        assert normalized(witness) in source,('Source witness absent',choice['id'],witness)
    matches=[d for d in destinations if d['printed_number']==choice['number']]
    assert len(matches)==1,('Duplicate/missing printed exercise number',choice['number'])
    match=matches[0]
    assert match['destination'] in {d['destination'] for d in candidates},'Outside source file span'
    # Start at the exercise heading: a named destination may precede it by a
    # line or page break. Never use text preceding the heading as a witness.
    marker=re.search(r'(?m)^\s*Soal\s+'+re.escape(choice['number'])+r'\.',match['_text'])
    assert marker,'Missing heading'
    text=normalized(match['_text'][marker.start():])
    for witness in choice['pdf_exact']:
        assert normalized(witness) in text,('Rendered witness absent',choice['id'],witness)
    # The distinguishing witnesses must identify only this candidate, even
    # where the chapter prints several almost identical exercises together.
    witnesses=[normalized(x) for x in choice['pdf_exact']]
    all_matches=[]
    candidate_ids={d['destination'] for d in candidates}
    for other in destinations:
        if other['destination'] in candidate_ids and all(w in normalized(other['_text']) for w in witnesses):
            all_matches.append(other['destination'])
    assert all_matches==[match['destination']],('Ambiguous witnesses',choice['id'],all_matches)
    return {
        'source_problem_id':choice['id'], 'printed_number':choice['number'],
        'component_destination':match['destination'],
        'component_page':match['heading_combined_page']-1116,
        'combined_page':match['heading_combined_page'],
        'pdf_text_window':intake.identity(match['_text'].encode('utf-8')),
        'witnesses':{'source':choice['source_exact'],'rendered':choice['pdf_exact']},
        'decision_rule':choice['rule'],
        'state':'verified_source_to_rendered_identity',
    }


def verify(workspace,cache):
    native_bytes=intake.checked_file(ROOT/'backend/course-capsule-v1/adapters/openlogic-teacher-v1/source-problems.json',{
        'bytes':1312777,'sha256':'655d56f4ea8535e4424902b693fcc393e7e0bdcb4a245835f63bd5ae761e4199'})
    native=json.loads(native_bytes)
    choices_path=ROOT/'backend/course-capsule-v1/authority/openlogic-supplement-exercise-choices-v1.json'
    choices_bytes=choices_path.read_bytes(); choices=json.loads(choices_bytes)
    assert choices['schema']=='openlogic-supplement-exercise-choices/1'
    problems={p['id']:p for p in native['problems'] if not p['in_frozen_main_reader']}
    assert len(choices['choices'])==31 and {c['id'] for c in choices['choices']}==set(problems)
    assert len({c['number'] for c in choices['choices']})==31
    refs=json.loads((intake.NATIVE/'INPUT_AUTHORITIES.json').read_bytes())['authorities']
    target_ref=next(r for r in refs if r['role']=='frozen_localized_zip')
    target_bytes=intake.checked_file(workspace/target_ref['path'],target_ref)
    qa_bytes=intake.checked_file(cache/'06_OPENLOGIC_id_SUPPLEMENT_COVERAGE_AND_QA_20260904.zip',{
        'bytes':272337,'sha256':'a74ddffccac99b434abcc4ea2e2a73819a01a286400e9a63b6fb15d55cf9c082'})
    pdf_bytes=intake.checked_file(cache/PDF,{
        'bytes':857775,'sha256':'bad0b8a0e22652cccab782e6e159868e00e137796d41578b3dd649b8a1831bae'})
    units={u['source_path']:u for u in native['units']}
    with zipfile.ZipFile(io.BytesIO(qa_bytes)) as qa:
        coverage_bytes=qa.read('audit/rendered-coverage-80.csv')
        coverage={r['source_path']:r for r in supp.csv.DictReader(io.StringIO(coverage_bytes.decode('utf-8-sig')))}
    rows=[]
    with fitz.open(stream=pdf_bytes,filetype='pdf') as pdf, zipfile.ZipFile(io.BytesIO(target_bytes)) as target:
        ds=supp.mapping.destinations(pdf,'prob*.',1116)
        assert len(ds)==31
        for choice in choices['choices']:
            assert choice['rule'] in choices['rules']
            problem=problems[choice['id']];unit=units[problem['source_path']]
            raw=target.read('source/'+unit['target_path'])
            assert intake.identity(raw)==unit['target']
            options=supp.candidates(problem,unit,coverage[unit['source_path']],ds,raw)
            block=raw[problem['target']['byte_start']:problem['target']['byte_end_exclusive']]
            row=verify_choice(choice,block.decode('utf-8-sig'),options['candidates'],ds)
            row.update(native_unit_id=problem['native_unit_id'],source_path=problem['source_path'],
                       target_path=problem['target_path'],source=problem['source'],target=problem['target'],
                       source_file=unit['source'],target_file=unit['target'],
                       component_href=BASE+PDF+'#page='+str(row['component_page']),
                       combined_href=BASE+'08_OPENLOGIC_id_STANDALONE_READER_ALL_722_20260905.pdf#page='+str(row['combined_page']))
            rows.append(row)
    assert {r['component_destination'] for r in rows}=={d['destination'] for d in ds}
    return {
        'schema':'openlogic-supplement-exercise-map/1','state':'pass',
        'scope':'All 31 source problem blocks and 31 printed supplement occurrences; main-reader mapping remains unfinished.',
        'overall_course_teacher_alignment_complete':False,
        'source_inventory':intake.identity(native_bytes),'choices':intake.identity(choices_bytes),
        'target_archive':intake.identity(target_bytes),'coverage_csv':intake.identity(coverage_bytes),
        'pdf':{'url':BASE+PDF,**intake.identity(pdf_bytes)},
        'review':choices['review'],'decision_rules':choices['rules'],
        'counts':{'source_problems':31,'printed_occurrences':31,'unique_destinations':31},
        'exercises':sorted(rows,key=lambda r:tuple(map(int,r['printed_number'].split('.')))),
        'limits':'Exact association, not a new translation certification. Uses physical pages for combined PDF; supplement-only named destinations are not copied into the combined name tree.',
    }


def main():
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True)
    p.add_argument('--cache',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();result=verify(a.workspace,a.cache)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='exercises'},ensure_ascii=False))


if __name__=='__main__':main()
