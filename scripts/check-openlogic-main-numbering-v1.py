"""Check candidate exercise numbering against independent canonical AUX labels."""
import argparse
from collections import Counter
import importlib.util
import io
import json
from pathlib import Path
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('map_main',ROOT/'scripts/map-openlogic-problems-v1.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


def labels(text):
    rows={}
    for match in re.finditer(r'\\newlabel\b',text):
        a,b,p=mod.group(text,match.end());key=text[a:b]
        a,b,p=mod.group(text,p);body=text[a:b];values=[];pos=0
        if not body.lstrip().startswith('{'):
            values=[body];pos=len(body)
        while pos<len(body) and body[pos:].strip():
            a,b,pos=mod.group(body,pos);values.append(body[a:b])
        assert key not in rows,('Duplicate AUX key',key)
        rows[key]=values
    return rows


def check_numbering(native,data,table):
    by_id={p['id']:p for p in native['problems']}
    counts=Counter();errors=[];matches=[]
    for row in data['comparisons']:
        source=by_id[row['source_problem_id']];contexts=source['file_id_contexts']
        if len(contexts)>1:
            contexts=[c for c in contexts if c.startswith('fol:' if row['fol_context'] else 'pl:')]
        if len(contexts)!=1:
            errors.append({'id':source['id'],'contexts':contexts});continue
        chapter_key=contexts[0]+':sec'
        if chapter_key not in table:
            chapter_key=':'.join(contexts[0].split(':')[:2])+'::chap'
        if chapter_key not in table:
            errors.append({'id':source['id'],'missing_chapter_key':chapter_key});continue
        chapter=table[chapter_key][0].split('.')[0]
        if not chapter.isdigit():
            errors.append({'id':source['id'],'chapter':chapter});continue
        counts[chapter]+=1
        expected=chapter+'.'+str(counts[chapter])
        if expected!=row['printed_number']:
            errors.append({'id':source['id'],'expected':expected,'actual':row['printed_number'],'chapter_key':chapter_key})
        else:matches.append({'id':source['id'],'chapter_key':chapter_key,'number':expected,
                             'context':contexts[0],'chapter_label':table[chapter_key],
                             'destination':row['destination']})
    return {'matching':len(matches),'errors':errors,'chapter_counts':dict(counts),'matches':matches}


def main():
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True)
    a=p.parse_args()
    native=json.loads((ROOT/'backend/course-capsule-v1/adapters/openlogic-teacher-v1/source-problems.json').read_bytes())
    data=json.loads((a.cache/'reader-reconciliation-candidate.json').read_bytes())
    archive=mod.intake.checked_file(a.cache/'05_OPENLOGIC_id_SUPPLEMENT_SOURCES_80_20260904.zip',{
        'bytes':920390,'sha256':'5f7831ac48de88ff41f6f9170bba8eda00de9216f817de6e804be441652674cd'})
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        aux=z.read('openlogic/locale/id/supplement-80-20260904/canonical-main-labels.aux')
    table=labels(aux.decode('utf-8-sig'));result=check_numbering(native,data,table)
    print(json.dumps({'state':'diagnostic','aux':mod.intake.identity(aux),**{k:v for k,v in result.items() if k!='matches'}},ensure_ascii=False))


if __name__=='__main__':main()
