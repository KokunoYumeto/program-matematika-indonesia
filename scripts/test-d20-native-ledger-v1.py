"""Independent byte-witness, raw-record preservation and replay checks."""
import hashlib
import importlib.util
import io
import json
import re
from pathlib import Path
import shutil
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('d20_ledger',ROOT/'scripts/d20-native-ledger-v1.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
lock,audit,tables,raw=m.load_inputs()
projection,_=m.project()
checks=[]
def check(name,value):
    assert value,name
    checks.append(name)

check('exact_native_scope',len(projection['rows'])==2196+425+286+7+4)
for kind in ['segments','terminology','corrections','terminology_qa','rights']:
    check('unchanged_'+kind,[r['native'] for r in projection['rows'] if r['kind']==kind]==tables[kind])
check('no_semantic_or_book_replay_claim',not projection['semantic_canon_review'] and not projection['native_book_rebuilt'])
private=re.compile(r'(?<![A-Za-z])[A-Za-z]:[\\/]|file://|github_pat_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9_-]{20,}',re.I)
check('native_metadata_and_projection_privacy',not private.search(m.encode(projection).decode()) and not any(private.search(b.decode()) for b in raw.values()))
check('no_empty_segment_chapter_binding',all(len(r['chapter_ids'])==1 for r in projection['rows'] if r['kind']=='segments'))
with zipfile.ZipFile(ROOT/m.CACHE/'PUBLIC_SOURCE.zip') as target,zipfile.ZipFile(ROOT/m.CACHE/'OFFICIAL_SOURCE.zip') as source:
    original={Path(n).name:source.read(n) for n in source.namelist() if not n.endswith('/')}
    for row in audit['segment_checks']:
        for side in ['source','target']:
            witness=row[side]
            assert witness['state']=='exact_fragment' and len(witness['matches'])==1
            match=witness['matches'][0]
            data=original[Path(row[side+'_path']).name] if side=='source' else target.read(m.PREFIX+row[side+'_path'])
            span=data[match['raw_byte_start']:match['raw_byte_end']]
            if match['view']=='universal_newlines':
                span=span.replace(b'\r\n',b'\n').replace(b'\r',b'\n')
            assert len(span)==witness['declared_bytes']
            assert hashlib.sha256(span).hexdigest()==witness['declared_sha256']
            view=data if match['view']=='raw' else data.replace(b'\r\n',b'\n').replace(b'\r',b'\n')
            assert view[match['byte_start']:match['byte_end']]==span
            assert view[:match['byte_start']].count(b'\n')+1==witness['declared_line_start']
            assert view[:max(match['byte_start'],match['byte_end']-1)].count(b'\n')+1==witness['declared_line_end']
checks.append('4392_fragment_hashes_and_line_intervals_replayed_independently')
check('36_whole_file_identities',len(audit['unit_file_checks'])==36 and all(r['declared']==r['observed'] for r in audit['unit_file_checks']))
with tempfile.TemporaryDirectory(prefix='d20-metadata-replay-') as temporary:
    isolated=Path(temporary)/'isolated'
    paths=[m.BASE/n for n in ['source-lock.json','intake-audit.json','intake-seal.json']]
    paths += [m.BASE/'input'/(name+'.jsonl') for name in raw]
    paths += [Path(r['path']) for r in lock['inputs']]
    paths += [m.SITE/n for n in ['ledger-ui.js','ledger.css']]
    for path in paths:
        destination=isolated/path;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/path,destination)
    _,first=m.build(isolated,Path(temporary)/'first')
    _,second=m.build(isolated,Path(temporary)/'second')
    check('isolated_replay_identical',first==second)
    check('replay_matches_current',all(m.fact((ROOT/m.BASE/'site'/n).read_bytes())==f for n,f in first.items()))
    with zipfile.ZipFile(io.BytesIO((Path(temporary)/'first/native-metadata.zip').read_bytes())) as archive:
        check('all_seven_raw_streams_in_zip',all(archive.read('backend/'+n+'.jsonl')==b for n,b in raw.items()))
    negative=[]
    for label,path in [('table',m.BASE/'input/terminology.jsonl'),('audit',m.BASE/'intake-audit.json'),('authority',m.AUTHORITY)]:
        target=isolated/path;original=target.read_bytes();target.write_bytes(original+b'\n')
        try:
            m.project(isolated)
        except ValueError:
            negative.append(label)
        else:
            raise AssertionError('Accepted changed '+label)
        finally:
            target.write_bytes(original)
receipt={'schema':'d20-native-ledger-tests/1','state':'pass','checks':checks,'negative_fixtures':negative,
         'outputs':first,'summary':audit['summary'],'semantic_canon_review':False,'native_book_rebuilt':False}
(ROOT/m.BASE/'tests.json').write_bytes(m.encode(receipt))
print(json.dumps({'state':'pass','checks':len(checks),'negative_fixtures':len(negative),'fragment_witnesses':4392}))
