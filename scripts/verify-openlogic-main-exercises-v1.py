"""Source-order, canonical-label and rendered-number proof for main exercises.

This establishes the positional exercise join, not mathematical/translation QA.
Selective TeX projection is bounded to the pinned corpus and its tested tags.
"""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import zipfile

import fitz

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('numbering',ROOT/'scripts/check-openlogic-main-numbering-v1.py')
numbering=importlib.util.module_from_spec(spec);spec.loader.exec_module(numbering)
mapping=numbering.mod;intake=mapping.intake
BASE='https://github.com/KokunoYumeto/OpenLogic-id/releases/download/id-olp-0722-20260814/'


def verify(workspace,cache):
    native=intake.collect(workspace)
    native_bytes=json.dumps(native,ensure_ascii=False,indent=2).encode()+b'\n'
    assert intake.identity(native_bytes)=={
        'bytes':1312777,'sha256':'655d56f4ea8535e4424902b693fcc393e7e0bdcb4a245835f63bd5ae761e4199'}
    # Recompute, never promote a previously written candidate report directly.
    candidate=mapping.collect(workspace,cache)
    assert candidate['source_inventory']==intake.identity(native_bytes)
    assert candidate['projection_errors']==[] and candidate['equal_main_cardinality'] is True
    archive=intake.checked_file(cache/'05_OPENLOGIC_id_SUPPLEMENT_SOURCES_80_20260904.zip',{
        'bytes':920390,'sha256':'5f7831ac48de88ff41f6f9170bba8eda00de9216f817de6e804be441652674cd'})
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        aux=z.read('openlogic/locale/id/supplement-80-20260904/canonical-main-labels.aux')
    label_table=numbering.labels(aux.decode('utf-8-sig'))
    proof=numbering.check_numbering(native,candidate,label_table)
    assert proof['errors']==[] and proof['matching']==411
    pdf_name='08_OPENLOGIC_id_STANDALONE_READER_ALL_722_20260905.pdf'
    pdf_bytes=intake.checked_file(cache/pdf_name,{
        'bytes':5754676,'sha256':'1b763b8b15c9f28a1212d81ee3e3a3f60ee3212fe1ffa4620c947caf43c89930'})
    by_id={p['id']:p for p in native['problems']};units={u['native_unit_id']:u for u in native['units']}
    rows=[];labelled=0
    with fitz.open(stream=pdf_bytes,filetype='pdf') as pdf:
        names=pdf.resolve_names()
        assert len(pdf)==1255
        for candidate_row,number_row in zip(candidate['comparisons'],proof['matches'],strict=True):
            assert number_row['id']==candidate_row['source_problem_id']
            problem=by_id[number_row['id']];unit=units[problem['native_unit_id']]
            section_destination=number_row['chapter_label'][3]
            assert section_destination in names
            assert names[section_destination]['page']+1<=candidate_row['heading_combined_page']
            destination=candidate_row['destination']
            assert names[destination]['page']+1==candidate_row['combined_page']
            # Labels present in the source are an independent exact anchor join.
            checked_labels=[]
            for key in problem['target']['literal_labels']:
                if key in label_table and label_table[key][3].startswith('probd*.'):
                    assert label_table[key][3]==destination,(problem['id'],key,destination)
                    assert label_table[key][0]==candidate_row['printed_number']
                    checked_labels.append(key)
            for key in problem['target']['labels']:
                full=number_row['context']+':'+key
                if full in label_table and label_table[full][3].startswith('probd*.'):
                    assert label_table[full][3]==destination,(problem['id'],full,destination)
                    checked_labels.append(full)
            labelled+=bool(checked_labels)
            rows.append({
                'occurrence_id':problem['id']+(':main-fol' if candidate_row['fol_context'] else ':main-propositional'),
                'source_problem_id':problem['id'],'native_unit_id':problem['native_unit_id'],
                'source_path':problem['source_path'],'target_path':problem['target_path'],
                'source':problem['source'],'target':problem['target'],
                'source_file':unit['source'],'target_file':unit['target'],
                'observed_import_path':candidate_row['observed_path'],
                'fol_context':candidate_row['fol_context'],'source_occurrence_order':candidate_row['ordered_index'],
                'printed_number':candidate_row['printed_number'],'destination':destination,
                'combined_page':candidate_row['heading_combined_page'],
                'combined_href':BASE+pdf_name+'#page='+str(candidate_row['heading_combined_page']),
                'canonical_section_label':number_row['chapter_key'],
                'canonical_section_value':number_row['chapter_label'],
                'exact_problem_labels':checked_labels,
                'state':'verified_source_order_section_and_printed_number',
            })
    assert len(rows)==len({r['occurrence_id'] for r in rows})==len({r['destination'] for r in rows})==411
    mapped={r['source_problem_id'] for r in rows};assert len(mapped)==396
    absent={p['id'] for p in native['problems'] if p['in_frozen_main_reader']}-mapped
    source_only={r['source_problem_id'] for r in candidate['source_only_occurrences']}
    excluded={r['source_problem_id'] for r in candidate['excluded']}-mapped
    assert absent==source_only|excluded and not source_only&excluded
    assert len(source_only)==1 and len(excluded)==10
    return {
        'schema':'openlogic-main-exercise-map/1','state':'pass',
        'scope':'411 printed occurrences of 396 source problems; ten source problems disabled by edition tags and one unflushed source problem retained separately.',
        'source_inventory':intake.identity(native_bytes),'recorder':candidate['recorder'],
        'canonical_aux':intake.identity(aux),'pdf':{'url':BASE+pdf_name,**intake.identity(pdf_bytes)},
        'proof':'Fresh hash-bound source extraction and recorded import sequence, positional tag projection, canonical section-number lookup, per-chapter exercise counter, every printed heading and destination checked; explicit source labels cross-checked when supplied.',
        'counts':{'occurrences':411,'source_problems':396,'explicit_label_occurrences':labelled,'tag_disabled_source_problems':10,'unflushed_source_problems':1},
        'chapter_counts':proof['chapter_counts'],'exercises':rows,
        'tag_disabled_source_problems':sorted(excluded),
        'source_only_findings':candidate['source_only_occurrences'],
        'limits':'A structural identity map, not a general TeX interpreter or renewed proof/translation-quality audit. The unflushed exercise is not marked rendered; disabled source blocks are not discarded.',
    }


def main():
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True)
    p.add_argument('--cache',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();result=verify(a.workspace,a.cache)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='exercises'}))


if __name__=='__main__':main()
