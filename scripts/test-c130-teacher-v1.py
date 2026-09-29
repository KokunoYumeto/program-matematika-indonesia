"""Independent source/reader assertions, negative cases and deterministic replay."""
import argparse
from collections import defaultdict
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile
import fitz
from c130_source_spans import normalize, fixtures
from c130_support_navigation import letters, fixtures as support_fixtures

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'backend/course-capsule-v1/adapters/c130-teacher-v1'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load_script(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def audit_primary(data,files,pages):
    assert len(data['questions'])==203 and len({q['id'] for q in data['questions']})==203
    spans={s['id']:s for s in data['native_individual_spans']};assert len(spans)==530
    for s in spans.values():
        raw=files[s['path']];text=normalize(raw);a,b=s['normalized_character_range']
        assert 0<=a<b<=len(text)
        assert sha(raw)==s['source_file']['sha256'] and len(raw)==s['source_file']['bytes']
        assert sha(text[a:b].encode())==s['content_sha256']
        assert [text.count('\n',0,a)+1,text.count('\n',0,b)+1]==s['line_range']
    grouped=defaultdict(list)
    for m in data['manual_materials']:grouped[m['source_header']['path']].append(m)
    for path,rows in grouped.items():
        text=normalize(files[path]);rows.sort(key=lambda r:r['source_header']['normalized_character_range'][0])
        for i,m in enumerate(rows):
            a,b=m['source_header']['normalized_character_range'];complete=m['complete_material_span']
            end=rows[i+1]['source_header']['normalized_character_range'][0] if i+1<len(rows) else len(text)
            assert sha(text[a:b].encode())==m['source_header']['content_sha256']
            assert complete['normalized_character_range']==[a,end]
            assert complete['body_after_header_range']==[b,end] and text[b:end].strip()
            assert sha(text[a:end].encode())==complete['sha256']
            assert sha(text[b:end].encode())==complete['body_sha256']
    support={s['id']:s for s in data['support_navigation']['materials']};assert len(support)==168
    for s in support.values():
        text=normalize(files[s['source_span']['path']]);a,b=s['source_span']['normalized_character_range']
        for witness in s['witnesses']+s.get('visualization_titles',[]):
            x,y=witness['source_character_range'];assert a<=x<y<=b
            assert text[x:y]==witness['source_text']
            assert sha(text[x:y].encode())==witness['source_sha256']
            assert letters(text[x:y])==witness['normalized_witness']
            assert witness['normalized_witness'] in letters(pages[witness['page']])
        if s['page'] is not None:assert sha(pages[s['page']].encode())==s['page_text_sha256']
        if s['kind']=='learningcheckpoint':
            answer=support[s['answer']['id']]
            assert s['source_span']['label']==answer['source_span']['label']
            assert s['answer']['page']==answer['page']
            assert answer['printed_number']==s['reader']['printed_number']
            pattern=r'Cek\s+Pemahaman\s+'+re.escape(answer['printed_number'])+r'\b'
            assert re.search(pattern,pages[s['page']]) and re.search(pattern,pages[answer['page']])
    assert sum(s['page'] is None for s in support.values())==28


def main():
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);args=p.parse_args()
    mapping=load_script('map-c130-teacher-v1.py');builder=load_script('build-c130-teacher-v1.py')
    raw=(BASE/'mapping.json').read_bytes();data=json.loads(raw)
    assert builder.fact(raw)==builder.MAPPING_IDENTITY
    # Two independent replays of pinned source and reader bytes, no network.
    for _ in range(2):assert mapping.encoded(mapping.map_all(args.cache))==raw
    files={}
    for kind in ['source','labs']:
        with zipfile.ZipFile(args.cache/data['inputs'][kind]['filename']) as z:
            for member in z.namelist():
                if member.startswith('source/') and not member.endswith('/'):
                    content=z.read(member)
                    if member[7:] in files:assert files[member[7:]]==content
                    files[member[7:]]=content
    with fitz.open(args.cache/data['reader']['filename']) as pdf:pages={i+1:page.get_text() for i,page in enumerate(pdf)}
    audit_primary(data,files,pages)
    negative=0
    def rejected(mutate):
        nonlocal negative
        copy_data=copy.deepcopy(data);mutate(copy_data)
        try:audit_primary(copy_data,files,pages)
        except (AssertionError,KeyError,IndexError,ValueError):negative+=1;return
        raise AssertionError('Corrupt mapping accepted')
    rejected(lambda d:d['questions'].__setitem__(1,d['questions'][0]))
    rejected(lambda d:d['native_individual_spans'][0].__setitem__('content_sha256','0'*64))
    rejected(lambda d:d['native_individual_spans'][0]['normalized_character_range'].__setitem__(0,0))
    rejected(lambda d:d['native_individual_spans'][0]['source_file'].__setitem__('sha256','0'*64))
    rejected(lambda d:d['manual_materials'][0]['complete_material_span']['body_after_header_range'].__setitem__(1,999999))
    rejected(lambda d:d['manual_materials'][0]['complete_material_span'].__setitem__('body_sha256','0'*64))
    def witness(d):return next(s['witnesses'][0] for s in d['support_navigation']['materials'] if s['witnesses'])
    rejected(lambda d:witness(d).__setitem__('source_text','wrong'))
    rejected(lambda d:witness(d).__setitem__('page',1))
    def checkpoint(d):return next(s for s in d['support_navigation']['materials'] if s['kind']=='learningcheckpoint')
    rejected(lambda d:checkpoint(d)['answer'].__setitem__('page',1))
    rejected(lambda d:checkpoint(d)['reader'].__setitem__('printed_number','999.1.1'))
    for rows in [[],[{},{}]]:
        try:mapping.require_one(rows,'negative')
        except ValueError:negative+=1
        else:raise AssertionError('Ambiguous/missing match accepted')
    assert builder.display_title(r'Gunakan \texttt{solve} pada $z$ dan $\varepsilon$')=='Gunakan solve pada z dan ε'
    try:builder.display_title(r'Unmapped \macro{x}')
    except ValueError:negative+=1
    else:raise AssertionError('Unknown title markup silently discarded')
    with tempfile.TemporaryDirectory(prefix='c130-teacher-replay-') as tmp:
        output=Path(tmp)/'site'
        for _ in range(2):
            result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/build-c130-teacher-v1.py'),'--out',str(output)],capture_output=True,text=True,timeout=30)
            assert result.returncode==0,result.stderr
            for lang,suffix in [('id',''),('en','.en')]:
                rendered=(output/f'C130.teacher{suffix}.html').read_text(encoding='utf-8')
                assert f'href="../../{lang}/index.html#course-C130"' in rendered
                assert 'index.html#C130"' not in rendered
            for path in (BASE/'site').iterdir():
                if path.is_file():assert (output/path.name).read_bytes()==path.read_bytes(),path.name
        with zipfile.ZipFile(output/'c130-teacher-source-v1.zip') as z:
            assert z.testzip() is None
            replay=Path(tmp)/'source';z.extractall(replay)
        result=subprocess.run([sys.executable,'-B',str(replay/'scripts/build-c130-teacher-v1.py')],capture_output=True,text=True,timeout=30)
        assert result.returncode==0,result.stderr
        rebuilt=replay/'backend/course-capsule-v1/adapters/c130-teacher-v1/site'
        for path in output.iterdir():assert (rebuilt/path.name).read_bytes()==path.read_bytes(),path.name
    receipt={'state':'pass','source_mapping_replays':2,'site_build_replays':2,'offline_source_zip_replay':True,
             'negative_cases':negative,'fixtures':fixtures()+support_fixtures(),'native_spans':530,
             'complete_manual_materials':192,'selectable_items':227,'support_inventory':data['support_navigation']['counts'],
             'mapping':builder.fact(raw),'build':json.loads((BASE/'site/build-receipt.json').read_bytes())}
    (BASE/'validation.json').write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(receipt))


if __name__=='__main__':main()
