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


def map_support(files,native_spans,units,relations,pdf):
    page_text={i+1:page.get_text() for i,page in enumerate(pdf)}
    pages={i:letters(text) for i,text in page_text.items()}
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
                  'source_bound_without_printed_mapping':sum(r['page'] is None for r in rows)},
        'limits':['A literal passage link locates the matched part, not necessarily the start or full extent of a solution.',
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
    return ['literal-unique','ambiguous-rejected','comments-excluded','math-excluded','changed-witness-rejected']
