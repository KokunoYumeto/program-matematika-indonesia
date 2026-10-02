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
from c130_source_spans import normalize, mask_comments, brace_end, fixtures
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
    questions={q['id']:q for q in data['questions']}
    heading_count=composite_count=example_count=0
    normalized_pages={page:letters(content) for page,content in pages.items()}
    for s in support.values():
        assert s['source_span']==spans[s['id']]
        text=normalize(files[s['source_span']['path']]);a,b=s['source_span']['normalized_character_range']
        for witness in s['witnesses']+s.get('visualization_titles',[]):
            x,y=witness['source_character_range'];assert a<=x<y<=b
            assert text[x:y]==witness['source_text']
            assert sha(text[x:y].encode())==witness['source_sha256']
            assert letters(text[x:y])==witness['normalized_witness']
            assert witness['normalized_witness'] in letters(pages[witness['page']])
        if s['page'] is not None:assert sha(pages[s['page']].encode())==s['page_text_sha256']
        if 'solution_reference' in s:
            heading_count+=1;reference=s['solution_reference'];source=reference['source_reference']
            x,y=source['normalized_character_range'];assert a<=x<y<=b
            assert text[x:y]==source['text'] and sha(text[x:y].encode())==source['sha256']
            label=re.fullmatch(r'\s*\\begin\{solution\}\s*\(Latihan~\\ref\{([^{}]+)\}\)',source['text'])
            assert label
            q=questions[reference['question_id']]
            assert q['source_span']['label']==label[1] and q['number']==reference['printed_number']
            edges=[r for r in data['native_support_relations'] if r['relation_type']=='solves' and r['from_id']==s['id']]
            assert len(edges)==1 and edges[0]['id']==reference['native_relation_id'] and edges[0]['to_id']==q['id']
            pattern=re.compile(r'Penyelesaian\.\s*\(Latihan\s+'+re.escape(q['number'])+r'\)')
            matches=[(page,m) for page,content in pages.items() for m in pattern.finditer(content)]
            assert len(matches)==1
            page,match=matches[0];w=reference['printed_witness']
            assert page==reference['page']==s['page']
            assert [match.start(),match.end()]==w['character_range'] and match[0]==w['text']
            assert sha(pages[page].encode())==w['page_text_sha256']
            assert s['printed_state']=='native-reference-and-unique-solution-heading'
        if 'composite_reference' in s:
            composite_count+=1;reference=s['composite_reference']
            assert s['kind']=='solution' and s['printed_state']=='ordered-composite-literal-passages'
            assert reference['page']==s['page'] and reference['witnesses']==s['witnesses']
            keys=[w['normalized_witness'] for w in s['witnesses']]
            assert len(set(keys))>=2 and sum(map(len,keys))>=50 and min(map(len,keys))>=12
            # Independently reconstruct all eligible source fragments: omission
            # must not make an ambiguous source look like a unique PDF match.
            body=mask_comments(text[a:b])
            body=re.sub(r'\$\$.*?\$\$|\$[^$]*\$|\\\(.*?\\\)|\\\[.*?\\\]',lambda m:'|'*len(m[0]),body,flags=re.S)
            body=re.sub(r'\\[A-Za-z@]+\*?(?:\s*\{[^{}]*\})?',lambda m:'|'*len(m[0]),body)
            body=re.sub(r'[.!?]','|',body)
            ranges=[[a+m.start(),a+m.end()] for m in re.finditer(r"[A-Za-zÀ-ž][A-Za-zÀ-ž\s,;:()'`–—-]+",body)
                    if len(letters(text[a+m.start():a+m.end()]))>=12]
            assert ranges==[w['source_character_range'] for w in s['witnesses']]
            hits=[]
            for page,content in normalized_pages.items():
                cursor=0;locations=[]
                for key in keys:
                    position=content.find(key,cursor)
                    if position<0:break
                    locations.append([position,position+len(key)]);cursor=position+len(key)
                else:hits.append((page,locations))
            assert len(hits)==1 and hits[0][0]==s['page']
            assert hits[0][1]==[w['normalized_page_range'] for w in s['witnesses']]
        if 'example_reference' in s:
            example_count+=1;reference=s['example_reference'];example=reference['source_example']
            assert s['kind']=='solution' and s['printed_state']=='adjacent-example-and-solution-opening'
            x,y=example['normalized_character_range'];u,v=example['title_character_range']
            assert 0<=x<u<v<y<=a and sha(text[x:y].encode())==example['sha256']
            assert text[u:v]==example['title'] and len(letters(text[u:v]))>=20
            assert text[x:u]==r'\begin{example}{' and brace_end(text,u-1)-1==v
            assert text[x:y].endswith(r'\end{example}') and not mask_comments(text[y:a]).strip()
            assert mask_comments(text[:a]).rfind(r'\begin{example}{')==x
            opening=reference['source_opening'];u,v=opening['source_character_range']
            assert a<=u<v<=b and text[u:v]==opening['source_text']
            assert sha(text[u:v].encode())==opening['source_sha256']
            assert re.fullmatch(r'\s*\\begin\{solution\}\s*',mask_comments(text[a:u]))
            assert len(letters(text[u:v]))>=20 and letters(text[u:v])==opening['normalized_witness']
            pattern=re.compile(r'Contoh\s+([A-Z0-9]+(?:\.[0-9]+)+)\.\s+'+
                               r'\s+'.join(re.escape(word) for word in example['title'].split())+r'\b')
            hits=[(page,m) for page,content in pages.items() for m in pattern.finditer(content)]
            assert len(hits)==1
            page,heading=hits[0];printed=reference['printed_heading'];content=pages[page]
            assert page==s['page']==reference['page'] and heading[1]==reference['printed_number']
            assert heading[0]==printed['text'] and [heading.start(),heading.end()]==printed['character_range']
            assert sha(content.encode())==reference['page_text_sha256']
            immediate=re.search(r'Penyelesaian\.\s*',content[heading.end():]);assert immediate
            assert heading.end()+immediate.start()==reference['printed_solution_start']
            assert not re.search(r'Contoh\s+[A-Z0-9]+\.[0-9]+',content[heading.end():reference['printed_solution_start']])
            assert letters(content[heading.end()+immediate.end():]).startswith(opening['normalized_witness'])
        if s['kind']=='learningcheckpoint':
            answer=support[s['answer']['id']]
            assert s['source_span']['label']==answer['source_span']['label']
            assert s['answer']['page']==answer['page']
            assert answer['printed_number']==s['reader']['printed_number']
            pattern=r'Cek\s+Pemahaman\s+'+re.escape(answer['printed_number'])+r'\b'
            assert re.search(pattern,pages[s['page']]) and re.search(pattern,pages[answer['page']])
    assert (heading_count,composite_count,example_count)==(12,14,2)
    assert sum(s['kind']=='solution' for s in support.values())==132
    assert sum(s['page'] is None for s in support.values())==0
    counts=data['support_navigation']['counts']
    assert counts['explicit_solution_heading_mappings']==12
    assert counts['ordered_composite_mappings']==14 and counts['adjacent_example_mappings']==2
    assert counts['unique_passage_or_anchor_mappings']==168 and counts['source_bound_without_printed_mapping']==0


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
    def solution(d):return next(s for s in d['support_navigation']['materials'] if 'solution_reference' in s)
    rejected(lambda d:solution(d)['solution_reference']['source_reference'].__setitem__('text','wrong'))
    rejected(lambda d:solution(d)['solution_reference'].__setitem__('question_id','wrong'))
    rejected(lambda d:solution(d)['solution_reference'].__setitem__('native_relation_id','wrong'))
    rejected(lambda d:solution(d)['solution_reference']['printed_witness'].__setitem__('text','wrong'))
    rejected(lambda d:solution(d).__setitem__('page',1))
    def composite(d):return next(s for s in d['support_navigation']['materials'] if 'composite_reference' in s)
    rejected(lambda d:composite(d)['witnesses'].reverse())
    rejected(lambda d:composite(d)['witnesses'].pop())
    rejected(lambda d:composite(d)['witnesses'][0]['normalized_page_range'].__setitem__(0,0))
    rejected(lambda d:composite(d)['composite_reference'].__setitem__('page',1))
    rejected(lambda d:composite(d).__setitem__('printed_state','unique-literal-passage'))
    def example(d):return next(s for s in d['support_navigation']['materials'] if 'example_reference' in s)['example_reference']
    rejected(lambda d:example(d)['source_example'].__setitem__('sha256','0'*64))
    rejected(lambda d:example(d)['source_example'].__setitem__('title','Wrong title'))
    rejected(lambda d:example(d)['source_opening'].__setitem__('source_text','Wrong opening'))
    rejected(lambda d:example(d).__setitem__('printed_number','D.999'))
    rejected(lambda d:example(d).__setitem__('printed_solution_start',0))
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
