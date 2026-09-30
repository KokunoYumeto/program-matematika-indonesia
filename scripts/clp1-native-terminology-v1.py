"""Preserve CLP-1 terminology witnesses and expand three truncated metadata labels.

This repairs mechanical slash expansion, not the book or its chosen terminology.
It does not promote producer review claims to independently verified canon use.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUTS={
 'decisions':('TRANSLATION_DECISIONS.id-ID.md','262d930c7552d8843e918585cb751ebc501d170fbfe5697167e613f377ee954f'),
 'terms':('modular_backend/backend/terms.jsonl','1f16ed2a3c76ec2812e3033c3396fd312401633c2f41457863648bdcd722d03e'),
 'concepts':('modular_backend/backend/concepts.jsonl','66174d3bdd6a206cbd6f5a0ad9271caea5229e4ba350740176a48a368e0da33c'),
}
RULES=[
 ('absolute_maximum','absolute maximum','absolut','absolute maximum','maksimum absolut',37,
  '| local/absolute maximum | maksimum lokal/absolut |'),
 ('local','local','maksimum lokal','local maximum','maksimum lokal',37,
  '| local/absolute maximum | maksimum lokal/absolut |'),
 ('down','down','ke bawah','concave down','cekung ke bawah',35,
  '| concave up/down | cekung ke atas/ke bawah |'),
]

def fact(body):
    return {'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}

def canonical(obj):
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')

def project(terms,concepts,decisions):
    assert len(terms)==len(concepts)==24
    assert len({r['id'] for r in terms})==len({r['id'] for r in concepts})==24
    original_terms,original_concepts=copy.deepcopy(terms),copy.deepcopy(concepts)
    projected_terms,projected_concepts=copy.deepcopy(terms),copy.deepcopy(concepts)
    by_term={r['id']:r for r in projected_terms}
    by_concept={r['id']:r for r in projected_concepts}
    corrections=[]
    lines=decisions.splitlines()
    for key,old_source,old_target,new_source,new_target,line,quote in RULES:
        assert lines[line-1].strip()==quote, 'Native decision-table locator drift'
        term=by_term['clp1.term.'+key]
        concept=by_concept[term['concept_id']]
        assert (term['source_term'],term['target_term'])==(old_source,old_target), 'Native term drift'
        assert (concept['label'],concept['localized_labels']['id-ID'])==(old_source,old_target), 'Native concept drift'
        corrections.append({'native_term_id':term['id'],'native_concept_id':concept['id'],
          'before':{'source':old_source,'target':old_target},
          'after':{'source':new_source,'target':new_target},
          'evidence':{'path':INPUTS['decisions'][0],'sha256':INPUTS['decisions'][1],'line':line,'quote':quote},
          'reason_id':'Melengkapi unsur bersama yang hilang ketika sel bertanda garis miring dipecah; bukan memilih istilah baru.',
          'reason_en':'Restore shared words lost by splitting a slash-separated table cell; not a new terminology choice.'})
        term['source_term'],term['target_term']=new_source,new_target
        concept['label'],concept['localized_labels']['id-ID']=new_source,new_target
    # Round-trip the semantic objects; raw source bytes are separately retained.
    restored_terms,restored_concepts=copy.deepcopy(projected_terms),copy.deepcopy(projected_concepts)
    rt={r['id']:r for r in restored_terms}; rc={r['id']:r for r in restored_concepts}
    for c in corrections:
        rt[c['native_term_id']]['source_term']=c['before']['source']
        rt[c['native_term_id']]['target_term']=c['before']['target']
        rc[c['native_concept_id']]['label']=c['before']['source']
        rc[c['native_concept_id']]['localized_labels']['id-ID']=c['before']['target']
    assert restored_terms==original_terms and restored_concepts==original_concepts
    return {'schema':'clp1-native-terminology-projection/1','status':'metadata_projection_validated',
       'native_status_fields_are_quoted_claims':True,'semantic_canon_review':'not_established',
       'native_ids_preserved':True,'reversible_object_projection':True,
       'source_table_rows':2,'corrected_term_records':3,'corrected_concept_records':3,
       'terms':projected_terms,'concepts':projected_concepts,'corrections':corrections,
       'native_book_modified':False,'course_capability_admitted':False,
       'consumer_integration':'pending','whole_program_backend_complete':False}

def build(native_root,output):
    raw={}
    for key,(path,expected) in INPUTS.items():
        raw[key]=(native_root/path).read_bytes()
        assert fact(raw[key])['sha256']==expected, 'Input identity differs: '+key
    rows=lambda key:[json.loads(line) for line in raw[key].decode('utf-8').splitlines() if line.strip()]
    projection=project(rows('terms'),rows('concepts'),raw['decisions'].decode('utf-8'))
    output.mkdir(parents=True,exist_ok=True)
    artifacts={
      'input/TRANSLATION_DECISIONS.id-ID.md':raw['decisions'],
      'input/terms.jsonl':raw['terms'],
      'input/concepts.jsonl':raw['concepts'],
      'projection.json':canonical(projection),
    }
    for name,body in artifacts.items():
        path=output/name
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():
            assert path.read_bytes()==body, 'Refusing to replace changed projection evidence'
        else:
            path.write_bytes(body)
    manifest={'schema':'clp1-native-terminology-manifest/1','state':'pass',
              'files':[{'path':name,**fact(body)} for name,body in sorted(artifacts.items())],
              'scope':'Reversible metadata projection only; learner/teacher integration pending; native canon review not claimed.'}
    target=output/'manifest.json'
    if target.exists():
        assert target.read_bytes()==canonical(manifest)
    else:
        target.write_bytes(canonical(manifest))
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--native-root',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    assert args.output.resolve().is_relative_to(ROOT.resolve())
    manifest=build(args.native_root.resolve(),args.output.resolve())
    print(json.dumps({'state':'pass','terms':24,'concepts':24,'corrected_terms':3,
        'corrected_concepts':3,'native_ids_preserved':True,'consumer_integration':'pending',
        'manifest':fact(canonical(manifest))}))
