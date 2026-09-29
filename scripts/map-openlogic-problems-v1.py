"""Reconcile the frozen source inventory with actual PDF problem destinations.

Bounded selective-TeX projection for this pinned corpus, not a general TeX
interpreter. Every occurrence is checked against source positions, the frozen
recorder trace and rendered text. Unmatched text remains explicit in the report.
"""
import argparse
from collections import Counter
import csv
import difflib
import importlib.util
import io
import json
from pathlib import Path
import posixpath
import re
from types import SimpleNamespace
import zipfile
import fitz

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ol_intake', ROOT/'scripts/intake-openlogic-teacher-v1.py')
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)


def group(text, start, opening='{', closing='}'):
    while start < len(text) and text[start].isspace():
        start += 1
    if start == len(text) or text[start] != opening:
        raise ValueError(('Expected group', start, text[start:start+40]))
    pos, depth = start+1, 1
    while pos < len(text):
        if text[pos] == '\\':
            pos += 2
            continue
        if text[pos] == opening:
            depth += 1
        elif text[pos] == closing:
            depth -= 1
            if depth == 0:
                return start+1, pos, pos+1
        pos += 1
    raise ValueError('Unclosed group')


def truth(names, tags):
    names = [t.strip() for t in names.split(',')]
    if any(t not in tags for t in names):
        raise ValueError(('Unknown tag', names))
    return any(tags[t] for t in names)


def argument(text,start):
    while start<len(text) and text[start].isspace():start+=1
    if start==len(text):raise ValueError('Missing TeX argument')
    if text[start]=='{':return group(text,start)
    token=re.match(r'\\(?:[A-Za-z@]+|.)|.',text[start:],re.DOTALL)
    return start,start+token.end(),start+token.end()


def project(text, tags):
    """Mask false branches with unchanged character positions."""
    result = list(text)
    # Branches are handled recursively so nested false conditions cannot revive
    # text. TeX \iftag is ANY-of, not ALL-of, according to the pinned style.
    token = re.compile(r'\\iftag\b|\\tagprob\b|\\begin\s*\{tagblock\}')
    pos = 0
    while m := token.search(text, pos):
        if m[0] == '\\iftag':
            a,b,nextpos = group(text,m.end()); yes0,yes1,nextpos = argument(text,nextpos)
            no0,no1,end = argument(text,nextpos)
            lo,hi = (yes0,yes1) if truth(text[a:b], tags) else (no0,no1)
            result[m.start():end] = ['\n' if c == '\n' else ' ' for c in text[m.start():end]]
            selected=text[lo:hi]
            # TeX removes the argument's outer braces, but a single unbraced
            # conditional token consumes its arguments from the remaining input.
            # Re-project that suffix with positions retained, not the isolated
            # token. The outer invocation is already masked, so it cannot recur.
            if re.fullmatch(r'\\[A-Za-z@]+',selected):
                result[lo:hi]=selected
                if selected in ['\\iftag','\\tagprob']:
                    result[lo:]=project(''.join(result[lo:]),tags)
                    return ''.join(result)
            else:result[lo:hi] = project(selected, tags)
        elif m[0] == '\\tagprob':
            p = m.end()
            while text[p].isspace(): p += 1
            outer = True
            if text[p] == '[':
                a,b,p = group(text,p,'[',']'); outer = truth(text[a:b],tags)
            a,b,p = group(text,p)
            ending = re.search(r'\\tagendprob\b',text[p:])
            if not ending: raise ValueError('Unclosed tagprob')
            end = p+ending.end()
            if not (outer and truth(text[a:b],tags)):
                result[m.start():end] = ['\n' if c == '\n' else ' ' for c in text[m.start():end]]
            else:
                result[p:p+ending.start()] = project(text[p:p+ending.start()],tags)
        else:
            a,b,p = group(text,m.end())
            ending = re.search(r'\\end\s*\{tagblock\}',text[p:])
            if not ending: raise ValueError('Unclosed tagblock')
            end = p+ending.end()
            if not truth(text[a:b],tags):
                result[m.start():end] = ['\n' if c == '\n' else ' ' for c in text[m.start():end]]
            else:
                result[p:p+ending.start()] = project(text[p:p+ending.start()],tags)
        pos = end
    return ''.join(result)


def tokens(text):
    # Matching witness only: no normalization is applied to released mathematics.
    text = text.replace('\u00ad','').replace('ﬁ','fi').replace('ﬂ','fl')
    text = re.sub(r'([A-Za-z])-\s*\n\s*([A-Za-z])',r'\1\2',text)
    return re.findall(r'[a-z]{3,}',text.lower())


def destinations(pdf, prefix, page_offset=0):
    names = pdf.resolve_names()
    ds = sorted([(n,d) for n,d in names.items() if n.startswith(prefix)],key=lambda r:(r[1]['page'],-r[1]['to'][1],r[0]))
    result = []
    for i,(name,d) in enumerate(ds):
        page = d['page']; top = pdf[page].rect.height-d['to'][1]-2
        # Read from the actual destination, bounded by the next problem or two
        # pages; long intervening chapter prose is not an exercise identity.
        nextd = ds[i+1][1] if i+1 < len(ds) else None
        endpage = min(page+2,len(pdf)-1,nextd['page'] if nextd else len(pdf)-1)
        chunks=[]
        heading=None
        heading_page=None
        for p in range(page,endpage+1):
            bottom=pdf[p].rect.height
            if nextd and p == nextd['page']:
                bottom=pdf[p].rect.height-nextd['to'][1]-2
            rect=fitz.Rect(0,top if p==page else 0,pdf[p].rect.width,max(bottom,top if p==page else 0))
            chunk=pdf[p].get_text(clip=rect)
            chunks.append(chunk)
            if heading is None:
                heading=re.search(r'(?m)^\s*Soal\s+([0-9]+\.[0-9]+)\b',chunk)
                if heading is not None: heading_page=p+1+page_offset
        text='\n'.join(chunks)
        result.append({'destination':name,'component_page':page+1,'combined_page':page+1+page_offset,
                       'printed_number':heading[1] if heading else None,
                       'heading_combined_page':heading_page,'_text':text})
    return result


def collect(workspace, cache):
    args=SimpleNamespace(workspace=workspace, cache=cache)
    native=intake.collect(args.workspace)
    authority=json.loads((intake.NATIVE/'INPUT_AUTHORITIES.json').read_bytes())
    refs={a['role']:a for a in authority['authorities']}
    native_by_path={u['source_path']:u for u in native['units']}
    by_unit={u['native_unit_id']:[] for u in native['units']}
    for row in native['problems']: by_unit[row['native_unit_id']].append(row)
    source=zipfile.ZipFile(args.workspace/refs['frozen_upstream_zip']['path'])
    target=zipfile.ZipFile(args.workspace/refs['frozen_localized_zip']['path'])
    evidence_path=args.workspace/refs['frozen_evidence_zip']['path']
    intake.checked_file(evidence_path,refs['frozen_evidence_zip'])
    evidence=zipfile.ZipFile(evidence_path)
    config=source.read(f'OpenLogic-{intake.UPSTREAM}/open-logic-config.sty').decode()
    tags={}
    for value,names in re.findall(r'\\tag(true|false)\s*\{([^{}]+)\}',intake.clean_tex(config)):
        for name in names.split(','):tags[name.strip()]=value=='true';tags['not'+name.strip()]=value!='true'
    recorder=evidence.read('locale/open-logic-complete-id.fls')
    files=list(dict.fromkeys(s[6:].replace('\\','/').removeprefix('./') for s in recorder.decode().splitlines()
                           if s.startswith('INPUT') and '/content/' in s.replace('\\','/') and s.endswith('.tex')))
    occurrences=[]
    masked_out=[]
    projection_errors=[]
    for observed_path in files:
        path=posixpath.normpath(observed_path)
        unit=native_by_path[path]
        if not by_unit[unit['native_unit_id']]:continue
        raw=target.read('source/'+unit['target_path'])
        text=raw.decode('utf-8-sig')
        contextual=dict(tags)
        # Provenance: propositional-logic.tex sets FOL false around these imports,
        # then restores it. Preserve the two contexts as different occurrences.
        alias='/../first-order-logic/' in observed_path
        contextual['FOL']=not alias;contextual['notFOL']=alias
        try:
            filtered=project(intake.clean_tex(text),contextual)
        except ValueError as error:
            projection_errors.append({'observed_path':observed_path,'reason':str(error),
                                      'source_problems_in_file':len(by_unit[unit['native_unit_id']])})
            continue
        for row in by_unit[unit['native_unit_id']]:
            start=len(raw[:row['target']['byte_start']].decode('utf-8-sig'))
            end=len(raw[:row['target']['byte_end_exclusive']].decode('utf-8-sig'))
            if not filtered[start:end].strip():
                masked_out.append({'source_problem_id':row['id'],'observed_path':observed_path})
                continue
            occurrences.append({'source_problem_id':row['id'],'observed_path':observed_path,
                                'fol_context':not alias,'_body':filtered[start:end]})
    combined_name='08_OPENLOGIC_id_STANDALONE_READER_ALL_722_20260905.pdf'
    supplement_name='04_OPENLOGIC_id_READER_SUPPLEMENT_80_20260904.pdf'
    release=json.loads((args.cache/'public-release.json').read_bytes())
    for name in [combined_name,supplement_name]:
        asset=next(a for a in release['assets'] if a['name']==name)
        intake.checked_file(args.cache/name,{'bytes':asset['size'],'sha256':asset['digest'].split(':')[1]})
    pdf=fitz.open(args.cache/combined_name);supp=fitz.open(args.cache/supplement_name)
    assert len(pdf)==1255 and len(supp)==139
    # Exact pinned exception, retained as source-only rather than deleted. The
    # epistemic chapter ends with OLEndPartHook, not OLEndChapterHook; the pinned
    # defer package flushes per-chapter problems only in the latter hook.
    # Text-search absence below corroborates this build-path diagnosis. This
    # diagnostic does not repair the producer or claim a general omission scan.
    chapter_member='source/locale/id/content/applied-modal-logic/epistemic-logic/epistemic-logic.tex'
    chapter_bytes=target.read(chapter_member)
    chapter_clean=intake.clean_tex(chapter_bytes.decode('utf-8-sig'))
    assert '\\OLEndPartHook' in chapter_clean and '\\OLEndChapterHook' not in chapter_clean
    defer_member=f'OpenLogic-{intake.UPSTREAM}/sty/open-logic-defer.sty'
    defer_bytes=source.read(defer_member)
    assert b'\\appto\\OLEndChapterHook' in defer_bytes
    main_text=' '.join(' '.join(page.get_text().split()) for page in pdf)
    absent_phrase='Tentukan pernyataan mana di antara pernyataan berikut'
    assert absent_phrase not in main_text
    source_only=[s for s in occurrences if s['source_problem_id']=='c80:OLP-0486:problem:001']
    assert len(source_only)==1
    source_only=[{**{k:v for k,v in source_only[0].items() if not k.startswith('_')},
                  'state':'source_only_missing_deferred_chapter_flush',
                  'chapter':{'member':chapter_member,**intake.identity(chapter_bytes)},
                  'defer_style':{'member':defer_member,**intake.identity(defer_bytes)},
                  'absent_literal_phrase':absent_phrase}]
    source_occurrences_before_deferred_check=len(occurrences)
    occurrences=[s for s in occurrences if s['source_problem_id']!='c80:OLP-0486:problem:001']
    main_ds=destinations(pdf,'probd*.')
    supp_ds=destinations(supp,'prob*.',1116)
    # Diagnostic text witnesses can reveal an insertion/deletion even when the
    # source and rendered counts differ. Never turn a similarity score into an
    # admitted identity join or silently zip two unequal sequences.
    grams={}
    for i,d in enumerate(main_ds):
        words=tokens(d['_text'])
        for j in range(len(words)-5):
            grams.setdefault(tuple(words[j:j+6]),set()).add(i)
    witnesses=[]
    for i,s in enumerate(occurrences):
        words=tokens(s['_body']); scores=Counter()
        for gram in {tuple(words[j:j+6]) for j in range(len(words)-5)}:
            scores.update(grams.get(gram,()))
        candidates=[{'pdf_index':j+1,'shared_six_word_runs':count,
                     'destination':main_ds[j]['destination'],
                     'page':main_ds[j]['combined_page']} for j,count in sorted(scores.items(),key=lambda item:(-item[1],item[0]))[:3]]
        witnesses.append({'source_index':i+1,'source_problem_id':s['source_problem_id'],
                          'observed_path':s['observed_path'],'candidates':candidates,
                          'target_preview':s['_body'][:250]})
    comparisons=[]
    aligned_pairs=zip(occurrences,main_ds) if not projection_errors and len(occurrences)==len(main_ds) else []
    for i,(s,d) in enumerate(aligned_pairs):
        st,dt=tokens(s['_body']),tokens(d['_text'])
        match=difflib.SequenceMatcher(None,st,dt,autojunk=False).find_longest_match()
        witness=' '.join(st[match.a:match.a+match.size])
        comparisons.append({**{k:v for k,v in s.items() if not k.startswith('_')},
                            **{k:v for k,v in d.items() if not k.startswith('_')},
                            'ordered_index':i+1,'longest_literal_word_run':match.size,'literal_witness':witness,
                            'target_preview':s['_body'][:220],'pdf_preview':d['_text'][:250]})
    result={'schema':'openlogic-reader-reconciliation-candidate/1','state':'diagnostic_not_admitted',
            'source_inventory':intake.identity(json.dumps(native,ensure_ascii=False,indent=2).encode()+b'\n'),
            'recorder':intake.identity(recorder),
            'source_occurrences':len(occurrences),'main_pdf_destinations':len(main_ds),
            'source_occurrences_before_deferred_check':source_occurrences_before_deferred_check,
            'source_only_occurrences':source_only,
            'supplement_pdf_destinations':len(supp_ds),'tag_excluded_occurrences':len(masked_out),
            'equal_main_cardinality':len(occurrences)==len(main_ds),
            'projection_errors':projection_errors,
            'word_run_distribution':dict(Counter(min(c['longest_literal_word_run'],8) for c in comparisons)),
            'comparisons':comparisons,'diagnostic_text_witnesses':witnesses,'excluded':masked_out,
            'supplement_destinations':[{k:v for k,v in d.items() if not k.startswith('_')} for d in supp_ds]}
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True)
    p.add_argument('--cache',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();result=collect(args.workspace,args.cache)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['comparisons','diagnostic_text_witnesses','excluded','supplement_destinations']}))


if __name__=='__main__':main()
