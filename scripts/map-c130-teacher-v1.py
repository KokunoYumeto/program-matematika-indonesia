"""Map C130 teaching references to exact published source and PDF bytes.

No source rewriting, native-ID replacement, TeX execution or network calls.
The new graph-list identities repair a demonstrated projection omission;
original native IDs, records, relationships and scope remain distinguishable.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import zipfile
import fitz
from c130_source_spans import normalize, mask_comments, structural_spans, locate, graph_list_spans, brace_end, fixtures
from c130_support_navigation import map_support, fixtures as support_fixtures

ROOT = Path(__file__).resolve().parents[1]
PINS = {
 'source':('pemrograman-matematis-dan-riset-operasi-buku-1-source-id-ID.zip',20087323,'55d62c53401938eb5dbc12d3f4116ce68181bd90c9f94fda1434fe20f5196914'),
 'labs':('pemrograman-matematis-dan-riset-operasi-buku-1-o018-open-solver-labs-id-ID.zip',527596,'99628dcdd4984c8a3b763862dc88b06bca8bf15d47dbf1db863cfe46b2a1e592'),
 'backend':('pemrograman-matematis-dan-riset-operasi-buku-1-modular-backend-v0.zip',6535806,'7cd76333b3433518f4d983d6775412aba9fd99e1f6b9a35a89528e6994830c56'),
 'reader':('pemrograman-matematis-dan-riset-operasi-buku-1-id-ID.pdf',26425739,'daa9b79df3684729cc204b563669f400866d8fbd12c0977d32ff9897276a7a49'),
}
DOWNLOAD = 'https://kokunoyumeto.github.io/open-optimization-or-book-id/downloads/'
COMMIT = 'a639b69cf84c4d4f60f7dcdb62dbeb5cfb153adc'
GRAPH = 'Intro-Math-Programming/baseText/book/part2-discrete-algorithms/ch10-graph-theory/graphtheory-dor1.tex'


def sha(data): return hashlib.sha256(data).hexdigest()
def encoded(value): return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def canonical(value): return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()


def norm(text):
    """Comparison-only normalization, never a rewrite of mathematical content."""
    text=unicodedata.normalize('NFKD',text)
    text=re.sub(r'\\[A-Za-z@]+\*?','',text)
    return ''.join(c.lower() for c in text if c.isalnum())


def identity(raw): return {'bytes':len(raw),'sha256':sha(raw)}


def require_one(rows, message):
    if len(rows)!=1: raise ValueError(f'{message}: expected one match, got {len(rows)}')
    return rows[0]


def map_all(cache):
    inputs={}
    archives={}
    for kind,(filename,count,digest) in PINS.items():
        data=(cache/filename).read_bytes()
        assert identity(data)=={'bytes':count,'sha256':digest},('Input drift',kind)
        inputs[kind]={'filename':filename,'url':DOWNLOAD+filename,**identity(data)}
        if kind!='reader':
            archives[kind]=zipfile.ZipFile(cache/filename)
            assert archives[kind].testzip() is None
    native_bytes=archives['backend'].read('backend/dist/backend-v0.json')
    assert sha(native_bytes)=='7c2ec930a7472021b37101f860b2b1846503fd52f4b495f863508cd91d741804'
    native=json.loads(native_bytes)
    units={u['id']:u for u in native['units']}
    assert len(units)==1993 and len(native['relations'])==9545
    files={}
    for kind in ['source','labs']:
        for member in archives[kind].namelist():
            if member.startswith('source/') and not member.endswith('/'):
                path=member[7:]
                raw=archives[kind].read(member)
                if path in files: assert raw==files[path]['raw']
                else: files[path]={'raw':raw,'archive':kind,'member':member}
    parsed={}
    native_spans=[]
    for unit in units.values():
        if unit['unit_type'] not in ['exercise','solution','answer','learningcheckpoint','tryit']:continue
        path=unit['target_path']
        if path not in parsed:parsed[path]=structural_spans(files[path]['raw'])
        result=locate(unit,parsed[path])
        assert result['state']=='exact_native_span',unit['id']
        native_spans.append({'id':unit['id'],'type':unit['unit_type'],'path':path,
            'native_record_sha256':sha(canonical(unit)),
            'source_file':{'archive':files[path]['archive'],'member':files[path]['member'],**identity(files[path]['raw'])},
            **result['span']})
    assert len(native_spans)==530
    spans={r['id']:r for r in native_spans}

    with fitz.open(cache/PINS['reader'][0]) as pdf:
        assert len(pdf)==666
        destinations=pdf.resolve_names()
        pages={i:pdf[i].get_text() for i in range(len(pdf))}
        blocks={i:pdf[i].get_text('blocks') for i in range(468,570)}
        anchors=[]
        for name,dest in destinations.items():
            if not name.startswith('bookex*.'):continue
            page=pdf[dest['page']];y=page.rect.height-dest['to'][1]
            witness=page.get_text(clip=fitz.Rect(0,max(0,y-4),page.rect.width,min(page.rect.height,y+50)))
            number=re.match(r'^Latihan\s+(\d+\.\d+)\b',witness)
            assert number,('Missing exercise heading',name)
            anchors.append({'destination':name,'page':dest['page']+1,'number':number.group(1),
                            'heading_witness':witness,'heading_witness_sha256':sha(witness.encode())})
        assert len(anchors)==184 and len({a['number'] for a in anchors})==184
        questions=[]; source_only=[];counts=defaultdict(int)
        graph_text=normalize(files[GRAPH]['raw']);graph_scan=mask_comments(graph_text)
        legacy_start=graph_scan.index(r'\ifdefined \old')
        legacy_end=graph_scan.rindex(r'\fi')
        assert legacy_end>legacy_start
        for r in sorted([r for r in native_spans if r['environment']=='ex'],key=lambda r:units[r['id']]['topology_order_path']):
            if r['path']==GRAPH and legacy_start<r['normalized_character_range'][0]<legacy_end:
                source_only.append({'id':r['id'],'reason':'legacy-conditional-not-in-pinned-reader','source_span':r})
                continue
            ch=int(re.search(r'\.ch(\d+)',r['id']).group(1));counts[ch]+=1
            number=f'{ch}.{counts[ch]}'
            dest=require_one([a for a in anchors if a['number']==number],r['id'])
            title=units[r['id']]['title_target']
            assert norm(title) and norm(title) in norm(dest['heading_witness']),('Title mismatch',r['id'])
            questions.append({'id':r['id'],'native_id':r['id'],'chapter':ch,'number':number,
                'kind':'numbered-exercise','title_id':title,'source_span':r,
                'reader':{**dest,'mapping_method':'native-topology-and-chapter-counter-plus-exact-normalized-title'},'supports':[]})
        assert len(source_only)==4 and len(questions)==184

        graph_items=graph_list_spans(files[GRAPH]['raw'])
        assert [r['number'] for r in graph_items]==list(range(1,20))
        derived=0
        for item in graph_items:
            native_match=[r for r in native_spans if r['environment']=='itemexercise' and r['label']==item['label']] if item['label'] else []
            r=require_one(native_match,'Label join') if native_match else None
            if r:assert r['content_sha256']==item['content_sha256']
            ident=r['id'] if r else 'c130:graph-practice:'+str(item['number']).zfill(2)
            if not r:derived+=1
            body=graph_text[item['body_start']:item['end']]
            body=re.sub(r'^\s*\\label\{[^}]+\}','',body)
            prose=re.split(r'\\begin|\\\\|\\altincludegraphics|\\captionof',body)[0]
            phrase=norm(prose)[:70]
            assert len(phrase)>=25
            page=require_one([i+1 for i in range(406,413) if str(item['number'])+phrase in norm(pages[i])],ident)
            current_span={'path':GRAPH,'source_file':{'archive':'source','member':'source/'+GRAPH,**identity(files[GRAPH]['raw'])},
                'normalized_character_range':[item['start'],item['end']],'line_range':item['line_range'],
                'content_sha256':item['content_sha256'],'label':item['label']}
            questions.append({'id':ident,'native_id':r['id'] if r else None,'chapter':14,
                'number':str(item['number']),'kind':'graph-practice','title_id':f'Latihan graf {item["number"]}',
                'source_span':r or current_span,'reader':{'page':page,'mapping_method':'top-level-enumeration-number-and-exact-normalized-opening',
                    'normalized_opening':phrase,'page_text_sha256':sha(pages[page-1].encode())},'supports':[]})
        assert derived==13 and len(questions)==203

        manuals=[]
        for unit in units.values():
            path=unit.get('target_path') or ''
            if '/solutions-manual/' not in path:continue
            if unit['id'] in spans and spans[unit['id']]['environment']=='manualsolution':
                s=spans[unit['id']]
                number=s['label'].split(':',1)[1]
                candidates=[{'page':i+1,'bbox':list(b[:4]),'heading_witness':b[4]}
                    for i,bs in blocks.items() for b in bs if re.match(r'^Latihan\s+'+re.escape(number)+r'\b',b[4])]
                dest=require_one(candidates,unit['id'])
                assert norm(unit['title_target']) in norm(dest['heading_witness'])
                question=require_one([q for q in questions if q['kind']=='numbered-exercise' and q['number']==number],number)
                manuals.append({'id':unit['id'],'source_header':s,'reader':dest,'question_id':question['id'],
                    'relation_basis':'explicit-manual-exercise-number','material_kind':'solution'})
            elif path.endswith('/ch14.tex') and unit['unit_type']=='subsection':
                raw=files[path]['raw'];text=normalize(raw)
                line=unit['target_line'];start=sum(len(s) for s in text.splitlines(keepends=True)[:line-1])
                assert text[start:].startswith(r'\subsection*{')
                end=brace_end(text,start+len(r'\subsection*'))
                assert sha(text[start:end].encode())==unit['target_content_sha256']
                title=unit['title_target']
                # Long headings may wrap; the full text block must contain it.
                candidates=[{'page':i+1,'bbox':list(b[:4]),'heading_witness':b[4]}
                    for i,bs in blocks.items() for b in bs if norm(title) in norm(b[4])]
                dest=require_one(candidates,unit['id'])
                match=re.match(r'Latihan (14\.\d+):',title)
                item=re.match(r'(Keterampilan|Konsep|Eksplorasi) (\d+):',title)
                if match:
                    q=require_one([q for q in questions if q['kind']=='numbered-exercise' and q['number']==match.group(1)],title)
                elif item:
                    q=require_one([q for q in questions if q['kind']=='graph-practice' and q['number']==item.group(2)],title)
                else:
                    assert title=='Cek pembelajaran (graf harga tiket pesawat lima kota)'
                    q={'id':'unit.r017.book1.ch14.text.learningcheckpoint-001'}
                    assert q['id'] in spans
                header={'path':path,'source_file':{'archive':'source','member':'source/'+path,**identity(raw)},
                    'normalized_character_range':[start,end],'content_sha256':unit['target_content_sha256'],
                    'native_record_sha256':sha(canonical(unit))}
                manuals.append({'id':unit['id'],'source_header':header,'reader':dest,'question_id':q['id'],
                    'relation_basis':'explicit-manual-heading-and-distinct-numbering-family',
                    'material_kind':'guide-and-rubric' if item and item.group(1)=='Eksplorasi' else 'solution'})
        assert len(manuals)==192
        by_path=defaultdict(list)
        for m in manuals:by_path[m['source_header']['path']].append(m)
        for path,rows in by_path.items():
            text=normalize(files[path]['raw'])
            rows.sort(key=lambda m:m['source_header']['normalized_character_range'][0])
            for index,m in enumerate(rows):
                start=m['source_header']['normalized_character_range'][0]
                end=rows[index+1]['source_header']['normalized_character_range'][0] if index+1<len(rows) else len(text)
                header_end=m['source_header']['normalized_character_range'][1]
                assert end>header_end and text[header_end:end].strip()
                m['complete_material_span']={'normalized_character_range':[start,end],
                    'body_after_header_range':[header_end,end],'sha256':sha(text[start:end].encode()),
                    'body_sha256':sha(text[header_end:end].encode()),
                    'line_range':[text.count('\n',0,start)+1,text.count('\n',0,end)+1],
                    'boundary_rule':'next-manual-heading-or-member-end'}
                m['reader']['page_text_sha256']=sha(pages[m['reader']['page']-1].encode())

        question_by_id={q['id']:q for q in questions}
        assert len(question_by_id)==203
        manual_native={(r['from_id'],r['to_id']):r['id'] for r in native['relations'] if r['relation_type']=='solves'}
        for m in manuals:
            if m['question_id'] in question_by_id:
                q=question_by_id[m['question_id']]
                q['supports'].append({'id':m['id'],'kind':m['material_kind'],'page':m['reader']['page'],
                    'native_relation_id':manual_native.get((m['id'],q['id'])),
                    'relation_basis':m['relation_basis']})
        lab_relations=[]
        for r in native['relations']:
            left=units.get(r.get('from_id'));right=units.get(r.get('to_id'))
            if not left or not right or 'lab' not in left['unit_type'] or r['relation_type'] not in ['solves','adapts']:continue
            lab_relations.append(r)
            if r['to_id'] in question_by_id:
                question_by_id[r['to_id']]['supports'].append({'id':left['id'],'kind':left['unit_type'],
                    'native_relation_id':r['id'],'relation_basis':r['relation_type'],
                    'source':{k:left.get(k) for k in ['content_path','code_data_refs','asset_ids','parent_id','title_target']}})
        support_navigation=map_support(files,native_spans,units,native['relations'],pdf,questions)
        counts={'native_units':1993,'native_relations':9545,'exact_individual_native_spans':530,
            'native_exercise_nodes':194,'source_only_legacy_exercises':4,'numbered_reader_exercises':184,
            'graph_practice_items':19,'graph_practice_native_ids':6,'additive_graph_practice_ids':13,
            'selectable_reader_exercises':203,'manual_materials':192,'manual_solution_headers':168,
            'graph_manual_sections':24,'questions_with_manual_material':sum(any('page' in s for s in q['supports']) for q in questions),
            'questions_without_manual_material':sum(not any('page' in s for s in q['supports']) for q in questions)}
        report={'schema':'c130-teacher-mapping/1','state':'exact-source-and-reader-reference-mapping',
            'course_id':'C130','reader':{**inputs['reader'],'pages':666,'locale':'id-ID'},'inputs':inputs,
            'native_backend':{'member':'backend/dist/backend-v0.json',**identity(native_bytes)},
            'source_commit':COMMIT,'source_normalization':'UTF-8-sig; CRLF and CR to LF; exact half-open character ranges',
            'title_comparison':'NFKD; omit TeX control words, punctuation, whitespace and combining marks; lowercase alphanumerics; exact containment, no fuzzy scoring',
            'counts':counts,'questions':questions,'manual_materials':manuals,'native_individual_spans':native_spans,
            'source_only':source_only,'native_lab_relations':lab_relations,
            'native_support_relations':[r for r in native['relations'] if r['relation_type'] in ['solves','answers','adapts']],
            'support_navigation':support_navigation,
            'chapters':{int(re.search(r'ch(\d+)$',u['id']).group(1)):u['title_target'] for u in units.values() if re.fullmatch(r'unit\.r017\.book1\.ch\d+',u['id'])},
            'fixtures':fixtures()+support_fixtures(),
            'findings':['Thirteen unlabelled graph practice questions were absent as individual native exercise records; current overlay preserves native IDs and adds distinct source-bound IDs.',
                'Native manualsolution spans hash headings, not complete answer bodies; current overlay hashes the full material separately.',
                'Graph manual uses distinct numbered practice families and includes guidance/rubrics; do not treat it as an undifferentiated answer key.',
                'Four graph ex environments are inside the legacy ifdefined old branch and are absent from the pinned reader exercise counter sequence.'],
            'limits':['This is structural reference mapping, not an independent proof of mathematical correctness.',
                'English and Indonesian controls use the same Indonesian reader; no English book mapping is claimed.',
                'Laboratory relations are native assertions; numerical results have not been re-executed here.',
                'All twelve checkpoints, their twelve answers and twelve visual activities have printed navigation. Other solution sources without unique printed witnesses remain explicitly unmapped.',
                'This does not prove whole-program or whole-C130 capability completion.']}
    for archive in archives.values():archive.close()
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();report=map_all(args.cache)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(encoded(report))
    print(json.dumps({'state':report['state'],'counts':report['counts'],'output':identity(args.output.read_bytes())}))


if __name__=='__main__':main()
