"""Read rendered PDF bookmark titles using exact canonical section destinations."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'backend/course-capsule-v1/adapters/openlogic-teacher-v1'


def identity(body):return {'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}


def extract(cache):
    raw=(BASE/'main-exercises.json').read_bytes()
    assert identity(raw)=={'bytes':909122,'sha256':'f9e58e8f649f4fedc240a21719b55efdce535592d073d65a8aaa1996c47bab16'}
    mapping=json.loads(raw)
    data=(cache/'08_OPENLOGIC_id_STANDALONE_READER_ALL_722_20260905.pdf').read_bytes()
    assert identity(data)=={k:mapping['pdf'][k] for k in ['bytes','sha256']}
    sections={r['canonical_section_value'][3] for r in mapping['exercises']}
    rows={};by_destination=defaultdict(list)
    with fitz.open(stream=data,filetype='pdf') as pdf:
        names=pdf.resolve_names()
        for level,title,page,dest in pdf.get_toc(simple=False):
            if dest.get('nameddest') in sections:
                by_destination[dest['nameddest']].append({'title':title,'physical_page':page,'outline_level':level})
        for key in sorted(sections):
            assert len(by_destination[key])==1,('Missing/ambiguous title',key,by_destination[key])
            row=by_destination[key][0]
            assert names[key]['page']+1==row['physical_page']
            assert row['title'] and not any(c in row['title'] for c in ['\\','{','}','$'])
            rows[key]=row
    return {'schema':'openlogic-rendered-section-titles/1','state':'pass','reader':mapping['pdf'],
        'main_map':identity(raw),'section_count':len(rows),'covered_occurrences':411,
        'method':'Exact canonical section named destination joined to PDF outline entry; no TeX macro guessing.',
        'sections':rows}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);a=p.parse_args()
    result=extract(a.cache);body=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
    (BASE/'section-titles.json').write_bytes(body)
    print(json.dumps({'sections':result['section_count'],'covered_occurrences':411,**identity(body)}))
