"""Anonymous one-pass checks of exact pinned D80 metadata and corrected-reader anchors."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'backend/course-capsule-v1/adapters/d80-native-ledger-v1'
lock=json.loads((BASE/'source-lock.json').read_bytes())
projection=json.loads((BASE/'site/projection.json').read_bytes())
repo=urlsplit(lock['native_repository']['public_repository']).path.strip('/')
checks=[]
def get(url):
    with urlopen(Request(url,headers={'User-Agent':'D80-native-metadata-verification','Accept':'*/*'}),timeout=40) as response:
        assert response.status==200
        return response.read()
for entry in lock['inputs']:
    url='https://raw.githubusercontent.com/'+repo+'/'+lock['native_repository']['github_main_commit']+'/'+quote(entry['native_path'])
    row={'path':entry['native_path'],'url':url,'expected_bytes':entry['bytes'],'expected_sha256':entry['sha256']}
    try:
        raw=get(url);row.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        row['pass']=row['bytes']==entry['bytes'] and row['sha256']==entry['sha256']
    except (HTTPError,URLError,TimeoutError) as error:
        row.update(pass_=False,error=type(error).__name__,http_status=getattr(error,'code',None))
        row['pass']=False;row.pop('pass_',None)
    checks.append(row)
    time.sleep(2)

class Reader(HTMLParser):
    def __init__(self):super().__init__();self.ids=set()
    def handle_starttag(self,tag,attrs):
        value=dict(attrs).get('id')
        if value:self.ids.add(value)

url='https://raw.githubusercontent.com/'+repo+'/'+lock['reader']['head']+'/index.html'
# The corrected-reader commit is the Pages tree, so its entry is index.html.
row={'path':'corrected-reader/index.html','url':url,'expected_bytes':lock['reader']['entry_bytes'],'expected_sha256':lock['reader']['entry_sha256']}
try:
    raw=get(url);row.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    row['pass']=row['bytes']==row['expected_bytes'] and row['sha256']==row['expected_sha256']
    if row['pass']:
        parser=Reader();parser.feed(raw.decode('utf-8'))
        anchors={urlsplit(link['url']).fragment for record in projection['rows'] for link in record['unit_links']}
        row['referenced_unique_unit_anchors']=len(anchors)
        row['missing_anchors']=sorted(anchors-parser.ids)
        row['pass']=len(anchors)==146 and not row['missing_anchors']
except (HTTPError,URLError,TimeoutError) as error:
    row.update(error=type(error).__name__,http_status=getattr(error,'code',None));row['pass']=False
checks.append(row)
receipt={'schema':'d80-native-public-verification/1','anonymous':True,'credentials_used':False,
         'state':'pass' if all(r['pass'] for r in checks) else 'incomplete','checks':checks,
         'scope':'Exact pinned public native metadata and corrected-reader unit anchors; no live-head, semantic or canon approval claim.'}
(BASE/'public-source-readback.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'state':receipt['state'],'checks':len(checks),'passed':sum(r['pass'] for r in checks),
                  'failed':[{'path':r['path'],'http_status':r.get('http_status')} for r in checks if not r['pass']]}))
