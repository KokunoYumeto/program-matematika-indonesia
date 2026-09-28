"""Bounded anonymous checks of exact existing exercise routes; no retries or writes to books."""
from collections import defaultdict
from datetime import datetime,timezone
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'backend/course-capsule-v1/adapters/judson-teacher-v1'


class Exercises(HTMLParser):
    def __init__(self):super().__init__();self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ['article','section','div'] and 'exercise' in a.get('class','').split() and a.get('id'):
            assert a['id'] not in self.ids,'Duplicate exercise ID'
            self.ids.add(a['id'])


def main():
    raw=(BASE/'input/native-exercise-intake.json').read_bytes();native=json.loads(raw)
    prefix=native['chapters'][0]['public_url'].rsplit('/',1)[0]+'/'
    assert prefix=='https://kokunoyumeto.github.io/abstract-algebra-theory-and-applications-id/'
    grouped=defaultdict(list)
    for e in native['exercises']:grouped[e['reader_member']].append(e['reader_fragment'])
    observations=[]
    for member,anchors in sorted(grouped.items()):
        assert '/' not in member and len(anchors)==len(set(anchors))
        row={'member':member,'url':prefix+member,'expected_anchors':sorted(anchors),
             'observed_utc':datetime.now(timezone.utc).isoformat()}
        try:
            with urlopen(row['url'],timeout=15) as r:body=r.read(4*1024*1024+1);row['status']=r.status
            assert len(body)<=4*1024*1024,'Unexpectedly large page'
            page=Exercises();page.feed(body.decode('utf-8'))
            row.update(bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),
                       missing_anchors=sorted(set(anchors)-page.ids))
            row['verified']=row['status']==200 and not row['missing_anchors']
        except Exception as error:row.update(verified=False,error=type(error).__name__+': '+str(error))
        observations.append(row)
        print(json.dumps({'member':member,'verified':row['verified'],'anchors':len(anchors)}),flush=True)
        if sum(not x['verified'] for x in observations)>=3:break
    result={'schema':'judson-current-reader-access/1','input_sha256':hashlib.sha256(raw).hexdigest(),
            'scope':'current online Indonesian anchor availability; not frozen-edition identity or language review',
            'observations':observations,'requested_pages':len(grouped),
            'complete':len(observations)==len(grouped) and all(x['verified'] for x in observations),
            'verified_exercises':sum(len(x['expected_anchors']) for x in observations if x['verified'])}
    (BASE/'input/reader-access.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='observations'}))


if __name__=='__main__':main()
