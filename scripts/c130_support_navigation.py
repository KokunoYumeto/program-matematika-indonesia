"""Literal source witnesses for checkpoints, answers and visual activities.

Comparison normalizes spacing, punctuation and Unicode decomposition only.
No fuzzy matching, formula reconstruction, source rewriting or remote calls.
Source-only evidence is retained for solutions without a unique prose witness.
"""
import hashlib
import re
import unicodedata
from c130_source_spans import normalize, mask_comments, brace_end


def sha(raw):return hashlib.sha256(raw).hexdigest()
def letters(text):
    return ''.join(c.lower() for c in unicodedata.normalize('NFKD',text) if c.isalnum())


def literal_witnesses(text,start,end,pages):
    body=mask_comments(text[start:end])
    body=re.sub(r'\$\$.*?\$\$|\$[^$]*\$|\\\(.*?\\\)|\\\[.*?\\\]',lambda m:'|'*len(m[0]),body,flags=re.S)
    body=re.sub(r'\\[A-Za-z@]+\*?(?:\s*\{[^{}]*\})?',lambda m:'|'*len(m[0]),body)
    witnesses=[]
    for m in re.finditer(r"[A-Za-zÀ-ž][A-Za-zÀ-ž\s,.;:!?()'`–—-]+",body):
        # Preserve exact source characters and ranges; don't trim the witness.
        fragment=text[start+m.start():start+m.end()]
        key=letters(fragment)
        if len(key)<45:continue
        hits=[page for page,normalized in pages.items() if key in normalized]
        if len(hits)==1:
            witnesses.append({'page':hits[0],'source_character_range':[start+m.start(),start+m.end()],
                'source_text':fragment,'source_sha256':sha(fragment.encode()),'normalized_witness':key})
    return witnesses


def composite_witnesses(text,start,end,pages):
    """Locate short prose separated by mathematics using an ordered conjunction.

    Every eligible fragment must occur, in source order without overlap, on
    one and only one PDF page. Repeated source phrases require repeated PDF
    occurrences. This does not compare or certify the intervening formulas.
    """
    body=mask_comments(text[start:end])
    body=re.sub(r'\$\$.*?\$\$|\$[^$]*\$|\\\(.*?\\\)|\\\[.*?\\\]',lambda m:'|'*len(m[0]),body,flags=re.S)
    body=re.sub(r'\\[A-Za-z@]+\*?(?:\s*\{[^{}]*\})?',lambda m:'|'*len(m[0]),body)
    body=re.sub(r'[.!?]', '|', body)
    fragments=[]
    for match in re.finditer(r"[A-Za-zÀ-ž][A-Za-zÀ-ž\s,;:()'`–—-]+",body):
        fragment=text[start+match.start():start+match.end()]
        key=letters(fragment)
        if len(key)<12:continue
        fragments.append({'source_character_range':[start+match.start(),start+match.end()],
            'source_text':fragment,'source_sha256':sha(fragment.encode()),'normalized_witness':key})
    keys=[f['normalized_witness'] for f in fragments]
    if len(set(keys))<2 or sum(map(len,keys))<50:return None
    hits=[]
    for page,content in pages.items():
        cursor=0;ranges=[]
        for key in keys:
            position=content.find(key,cursor)
            if position<0:break
            ranges.append([position,position+len(key)])
            cursor=position+len(key)
        else:hits.append((page,ranges))
    if len(hits)!=1:return None
    page,ranges=hits[0]
    return {'page':page,'witnesses':[{**f,'page':page,'normalized_page_range':r}
        for f,r in zip(fragments,ranges)],
        'mapping_method':'unique-page-with-all-short-prose-fragments-in-source-order',
        'scope':'Matched prose location only; not full solution extent or mathematical verification.'}


def example_solution_heading(text,start,end,pages):
    """Exact adjacent source example + unique printed title + solution opening."""
    scan=mask_comments(text)
    beginnings=list(re.compile(r'\\begin\{example\}\{').finditer(scan,0,start))
    if not beginnings:return None
    match=beginnings[-1];title_start=match.end();title_end=brace_end(text,title_start-1)-1
    title=text[title_start:title_end]
    if re.search(r'[\\{}]',title) or len(letters(title))<20:return None
    closing=scan.find(r'\end{example}',title_end,start)
    if closing<0:return None
    example_end=closing+len(r'\end{example}')
    if scan[example_end:start].strip():return None
    opening=re.match(r'\s*\\begin\{solution\}\s*([A-Za-zÀ-ž][A-Za-zÀ-ž\s,;:]+)',scan[start:end])
    if not opening or len(letters(opening[1]))<20:return None
    heading_pattern=re.compile(r'Contoh\s+([A-Z0-9]+(?:\.[0-9]+)+)\.\s+'+
                               r'\s+'.join(re.escape(s) for s in title.split())+r'\b')
    headings=[(page,m) for page,content in pages.items() for m in heading_pattern.finditer(content)]
    if len(headings)!=1:return None
    page,heading=headings[0];content=pages[page]
    solution=re.search(r'Penyelesaian\.\s*',content[heading.end():])
    if not solution:return None
    solution_start=heading.end()+solution.start()
    prose_start=heading.end()+solution.end()
    if re.search(r'Contoh\s+[A-Z0-9]+\.[0-9]+',content[heading.end():solution_start]):return None
    opening_key=letters(opening[1])
    if not letters(content[prose_start:]).startswith(opening_key):return None
    source_opening=[start+opening.start(1),start+opening.end(1)]
    return {'page':page,'printed_number':heading[1],
        'source_example':{'normalized_character_range':[match.start(),example_end],
            'sha256':sha(text[match.start():example_end].encode()),'title':title,
            'title_character_range':[title_start,title_end]},
        'source_opening':{'source_character_range':source_opening,'source_text':text[slice(*source_opening)],
            'source_sha256':sha(text[slice(*source_opening)].encode()),'normalized_witness':opening_key},
        'printed_heading':{'text':heading[0],'character_range':[heading.start(),heading.end()]},
        'printed_solution_start':solution_start,'page_text_sha256':sha(content.encode()),
        'mapping_method':'adjacent-source-example-unique-printed-title-and-immediate-solution-opening',
        'scope':'Solution start page only; the body can continue on following pages. No mathematical verification.'}


def visualization_titles(text,start,end,pages):
    titles=[]
    for match in re.compile(r'\\vizlink\{([^{}]+)\}\{').finditer(mask_comments(text),start,end):
        opening=match.end()-1;closing=brace_end(text,opening)
        if closing>end:raise ValueError('Visualization title escapes source span')
        title=text[opening+1:closing-1]
        if '\\' in title or '{' in title or '}' in title:raise ValueError('Unsupported visualization title markup')
        key=letters(title)
        if len(key)<8:raise ValueError('Visualization title too short for reference mapping')
        hits=[page for page,normalized in pages.items() if key in normalized and 'cobalahsecaravisual' in normalized]
        titles.append({'slug':match.group(1),'candidate_pages':hits,'source_character_range':[opening+1,closing-1],
            'source_text':title,'source_sha256':sha(title.encode()),'normalized_witness':key})
    if titles:
        common=set.intersection(*(set(t['candidate_pages']) for t in titles))
        if len(common)!=1 or max(len(t['normalized_witness']) for t in titles)<12:
            raise ValueError('Ambiguous or missing visualization title group')
        for title in titles:
            title.pop('candidate_pages');title['page']=next(iter(common))
    return titles


def solution_heading(text,span,relations,questions,pages):
    """Join an explicit source reference, native edge and unique printed heading.

    The page is the start of the solution, not its full extent. Unlike a plain
    exercise-number match, the printed prefix distinguishes repeated manual
    headings and references in the question text. No fuzzy text matching.
    """
    start,end=span['normalized_character_range']
    source=text[start:end]
    match=re.match(r'\s*\\begin\{solution\}\s*\(Latihan~\\ref\{([^{}]+)\}\)',source)
    if not match:return None
    edges=[r for r in relations if r['relation_type']=='solves' and r['from_id']==span['id']]
    if len(edges)!=1:raise ValueError('Missing or ambiguous native solution edge')
    edge=edges[0];question=questions[edge['to_id']]
    if question['kind']!='numbered-exercise' or question['source_span']['label']!=match.group(1):
        raise ValueError('Exact solution source reference and question label disagree')
    pattern=re.compile(r'Penyelesaian\.\s*\(Latihan\s+'+re.escape(question['number'])+r'\)')
    matches=[(page,m) for page,content in pages.items() for m in pattern.finditer(content)]
    if len(matches)!=1:raise ValueError('Printed solution heading missing or ambiguous')
    page,witness=matches[0]
    return {'question_id':question['id'],'native_relation_id':edge['id'],
        'printed_number':question['number'],'page':page,
        'source_reference':{'text':match[0],'sha256':sha(match[0].encode()),
            'normalized_character_range':[start+match.start(),start+match.end()]},
        'printed_witness':{'text':witness[0],'character_range':[witness.start(),witness.end()],
            'page_text_sha256':sha(pages[page].encode())},
        'mapping_method':'native-solves-edge-exact-source-reference-and-unique-printed-solution-heading',
        'scope':'Start page only; not full solution extent or mathematical verification.'}


def map_support(files,native_spans,units,relations,pdf,questions):
    page_text={i+1:page.get_text() for i,page in enumerate(pdf)}
    pages={i:letters(text) for i,text in page_text.items()}
    question_by_id={q['id']:q for q in questions}
    names=pdf.resolve_names()
    checkpoint_anchors=sorted([{'destination':k,'page':v['page']+1} for k,v in names.items()
                              if k.startswith('tcb@cnt@learningcheckpoint*.')],key=lambda r:r['page'])
    cp=sorted([s for s in native_spans if s['type']=='learningcheckpoint'],key=lambda s:units[s['id']]['topology_order_path'])
    if len(cp)!=12 or len(checkpoint_anchors)!=12:raise ValueError('Checkpoint inventory drift')
    checkpoint_dest={}
    for s,d in zip(cp,checkpoint_anchors):
        headings=re.findall(r'Cek\s+Pemahaman\s+(\d+\.\d+\.\d+)',page_text[d['page']])
        if len(headings)!=1:raise ValueError('Ambiguous checkpoint printed number')
        checkpoint_dest[s['id']]={**d,'printed_number':headings[0]}
    rows=[]
    for s in native_spans:
        if s['type'] not in ['learningcheckpoint','tryit','answer','solution'] or s['environment']=='manualsolution':continue
        text=normalize(files[s['path']]['raw']);start,end=s['normalized_character_range']
        witnesses=literal_witnesses(text,start,end,pages)
        row={'id':s['id'],'kind':s['type'],'source_span':s,'witnesses':witnesses,
             'printed_state':'unique-literal-passage' if witnesses else 'source-bound-unmapped',
             'page':witnesses[0]['page'] if witnesses else None}
        if s['type']=='learningcheckpoint':
            dest=checkpoint_dest[s['id']]
            if not any(w['page']==dest['page'] for w in witnesses):raise ValueError('Checkpoint anchor/prose mismatch: '+s['id'])
            row.update(reader=dest,page=dest['page'],printed_state='checkpoint-anchor-and-literal-passage')
        elif s['type']=='tryit':
            titles=visualization_titles(text,start,end,pages)
            if not titles or len({t['page'] for t in titles})!=1:raise ValueError('Activity titles cross unmatched pages')
            row.update(visualization_titles=titles,page=titles[0]['page'],printed_state='exact-visualization-titles')
        elif s['type']=='answer' and not witnesses:
            raise ValueError('Checkpoint answer has no unique literal witness: '+s['id'])
        elif s['type']=='solution' and not witnesses:
            heading=solution_heading(text,s,relations,question_by_id,page_text)
            if heading:
                row.update(page=heading['page'],printed_state='native-reference-and-unique-solution-heading',
                           solution_reference=heading)
            else:
                composite=composite_witnesses(text,start,end,pages)
                if composite:
                    row.update(page=composite['page'],printed_state='ordered-composite-literal-passages',
                               witnesses=composite['witnesses'],composite_reference=composite)
                else:
                    example=example_solution_heading(text,start,end,page_text)
                    if example:
                        row.update(page=example['page'],printed_state='adjacent-example-and-solution-opening',
                                   example_reference=example)
        if row['page']:row['page_text_sha256']=sha(page_text[row['page']].encode())
        rows.append(row)
    by_id={r['id']:r for r in rows}
    toc=pdf.get_toc();answer_sections=[(i,t) for i,t in enumerate(toc) if t[1]=='Jawaban Cek Pemahaman']
    if len(answer_sections)!=1:raise ValueError('Answer appendix not uniquely identified')
    toc_index,entry=answer_sections[0]
    next_page=next((t[2] for t in toc[toc_index+1:] if t[0]<=entry[0]),len(pdf)+1)
    for s in cp:
        links=[r for r in relations if r['relation_type']=='answers' and r['to_id']==s['id']]
        if len(links)!=1:raise ValueError('Checkpoint answer association missing or ambiguous')
        link=links[0];answer=by_id[link['from_id']]
        if answer['kind']!='answer' or answer['source_span']['label']!=s['label']:raise ValueError('Checkpoint label mismatch')
        printed=by_id[s['id']]['reader']['printed_number']
        headings=[page for page in range(entry[2],next_page) if re.search(r'Cek\s+Pemahaman\s+'+re.escape(printed)+r'\b',page_text[page])]
        if len(headings)!=1 or not headings[0]<=answer['page']<=headings[0]+1:
            raise ValueError('Answer heading and literal body witness disagree')
        answer.update(page=headings[0],printed_state='exact-checkpoint-answer-heading-and-literal-body',
                      printed_number=printed,page_text_sha256=sha(page_text[headings[0]].encode()))
        by_id[s['id']]['answer']={'id':answer['id'],'page':answer['page'],'native_relation_id':link['id'],
            'relation_basis':'native-answers-edge-and-exact-source-label'}
    if len(rows)!=168:raise ValueError('Support inventory drift')
    return {'schema':'c130-support-navigation/1','materials':rows,
        'counts':{'checkpoints':12,'checkpoint_answers':12,'visual_activities':12,'other_native_solutions':132,
                  'unique_passage_or_anchor_mappings':sum(r['page'] is not None for r in rows),
                  'explicit_solution_heading_mappings':sum('solution_reference' in r for r in rows),
                  'ordered_composite_mappings':sum('composite_reference' in r for r in rows),
                  'adjacent_example_mappings':sum('example_reference' in r for r in rows),
                  'source_bound_without_printed_mapping':sum(r['page'] is None for r in rows)},
        'limits':['A literal passage link locates the matched part, not necessarily the start or full extent of a solution.',
                  'Explicit solution-reference links locate a unique solution heading; the body may continue on following pages.',
                  'No external visualization availability, solver execution or mathematical correctness is established by these links.',
                  'Unmapped solution sources are retained explicitly; absent navigation is not a claim of absent mathematical content.']}


def fixtures():
    text='Unique source explanation that has enough letters to avoid short accidental matches.'
    key=letters(text)
    assert len(literal_witnesses(text,0,len(text),{1:key}))==1
    assert not literal_witnesses(text,0,len(text),{1:key,2:key})
    assert not literal_witnesses('% '+text,0,len(text)+2,{1:key})
    assert not literal_witnesses('$'+text+'$',0,len(text)+2,{1:key})
    assert not literal_witnesses(text,0,len(text),{1:key.replace('enough','different')})
    source=r'\begin{solution}(Latihan~\ref{ex:a})Some solution body.\end{solution}'
    span={'id':'s','normalized_character_range':[0,len(source)]}
    edge={'id':'r','relation_type':'solves','from_id':'s','to_id':'q'}
    questions={'q':{'id':'q','kind':'numbered-exercise','number':'2.7','source_span':{'label':'ex:a'}}}
    pages={1:'Latihan 2.7 (question)',2:'Penyelesaian. (Latihan 2.7) body',3:'Latihan 2.7 (manual)'}
    result=solution_heading(source,span,[edge],questions,pages)
    assert result['page']==2 and result['printed_number']=='2.7'
    cases=[(source.replace('ex:a','ex:z'),[edge],pages),
           (source,[edge,edge],pages),(source,[],pages),
           (source,[edge],{**pages,4:pages[2]}),
           (source,[edge],{1:pages[1],3:pages[3]})]
    for body,edges,content in cases:
        current={**span,'normalized_character_range':[0,len(body)]}
        try:solution_heading(body,current,edges,questions,content)
        except ValueError:pass
        else:raise AssertionError('Invalid solution-heading mapping accepted')
    first='The first sufficiently distinctive phrase'
    second='Another independently identifiable phrase'
    composite_source=first+' $x$ '+second
    good=letters(first)+'x'+letters(second)
    assert composite_witnesses(composite_source,0,len(composite_source),{2:good})['page']==2
    for bad in [{1:good,2:good},{1:letters(second)+letters(first)},
                {1:letters(first),2:letters(second)},{1:letters(first)}]:
        assert composite_witnesses(composite_source,0,len(composite_source),bad) is None
    repeated=composite_source+' $y$ '+second
    assert composite_witnesses(repeated,0,len(repeated),{2:good}) is None
    assert composite_witnesses('% '+composite_source,0,len(composite_source)+2,{2:good}) is None
    prefix=r'\begin{example}{A sufficiently distinctive example title}Question.\end{example}'
    solution=r'\begin{solution}A distinctive opening phrase $x$.\end{solution}'
    example_source=prefix+'\n'+solution
    page='Contoh D.8. A sufficiently distinctive example title Question.\nPenyelesaian. A distinctive opening phrase x.'
    assert example_solution_heading(example_source,len(prefix)+1,len(example_source),{2:page})['page']==2
    for bad in [{1:page,2:page},{1:page.replace('example title','wrong title')},
                {1:page.replace('A distinctive opening','A wrong opening')},
                {1:page.replace('Penyelesaian.','Other text.')}]:
        assert example_solution_heading(example_source,len(prefix)+1,len(example_source),bad) is None
    separated=prefix+'Unrelated source.\n'+solution
    assert example_solution_heading(separated,len(prefix)+18,len(separated),{2:page}) is None
    return ['literal-unique','ambiguous-rejected','comments-excluded','math-excluded','changed-witness-rejected',
            'solution-heading-excludes-manual-and-question','wrong-solution-label-rejected',
            'duplicate-solution-edge-rejected','missing-solution-edge-rejected',
            'ambiguous-solution-heading-rejected','missing-solution-heading-rejected',
            'ordered-composite-unique','composite-duplicate-page-rejected','composite-reordering-rejected',
            'composite-cross-page-rejected','composite-missing-fragment-rejected',
            'composite-repeated-occurrence-required','composite-comments-excluded',
            'adjacent-example-unique','duplicate-example-heading-rejected','wrong-example-title-rejected',
            'wrong-solution-opening-rejected','missing-example-solution-heading-rejected',
            'nonadjacent-source-example-rejected']
