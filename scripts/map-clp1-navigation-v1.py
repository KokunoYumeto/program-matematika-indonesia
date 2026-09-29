"""Replay exact CLP1 source spans and printed Q/H/A/S navigation.

Only additive metadata is emitted. Native records and released books stay
unchanged. External ZIP/PDF inputs are supplied explicitly and hash pinned.
This proves structural identity/navigation, not a new translation review.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import posixpath
import re
import zipfile

import fitz
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'backend/course-capsule-v1/adapters/clp-teacher-v1'
EXPECTED = {
    'native': 'a4984d3d980a47a61dd4bff963b1b65f12327ab8abffefbf2f0407442ccfe83a',
    'source': 'c61976a35837a92b5278eba21b52802cee5396278ca86b87258e7cd62ae8e7e0',
    'backend': '813fc553f52e0d6d4463c1ee8732a921f51180734acca8d3c2822c573999360f',
    'pdf': '911b2a0e3a9de6eccb9dd93042fa697e8f02e4bb1ecdacec86ade68744245021',
}
REPARENTED = {
    'pretext/problems/prob_s3.3.4.xml': ('pretext/problems/prob_s3.3.xml', 'latex/problembook/problems/prob_s3.3.tex'),
    'pretext/problems/prob_s3.4.9.xml': ('pretext/problems/prob_s3.4.xml', 'latex/problembook/problems/prob_s3.4.tex'),
}
LABELS = {'hint':'Petunjuk', 'answer':'Jawaban', 'solution':'Penyelesaian'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(raw):
    return {'bytes':len(raw), 'sha256':sha(raw)}


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode('utf-8')


def normal(raw):
    return raw.decode('utf-8-sig').replace('\r\n','\n').replace('\r','\n')


def xml(raw):
    return etree.fromstring(raw, etree.XMLParser(remove_comments=True, remove_pis=True,
                           resolve_entities=False, no_network=True))


def canonical(node):
    local = lambda tag: tag.rsplit('}',1)[-1]
    tag = local(node.tag)
    attrs = [local(k)+'="'+v.replace('&','&amp;').replace('"','&quot;')+'"'
             for k,v in sorted(node.attrib.items(), key=lambda p:local(p[0]))]
    opening = '<'+tag+(' '+' '.join(attrs) if attrs else '')
    if not len(node) and not node.text:
        return opening+'/>'
    return opening+'>'+(node.text or '')+''.join(canonical(c)+(c.tail or '') for c in node)+'</'+tag+'>'


def mask_comments(text):
    chars = list(text)
    for match in re.finditer('%[^\n]*', text):
        previous = match.start()-1
        while previous >= 0 and text[previous] == '\\':
            previous -= 1
        if (match.start()-previous-1)%2 == 0:
            chars[match.start():match.end()] = ' '*(match.end()-match.start())
    return ''.join(chars)


def environments(text):
    stack, spans = [], []
    selected = {'question','Mquestion','hint','answer','solution'}
    for match in re.finditer(r'\\(begin|end)\s*\{([A-Za-z*]+)\}', mask_comments(text)):
        action, name = match.groups()
        if action == 'begin':
            stack.append((name,match.start(),match.end()))
        else:
            assert stack and stack[-1][0] == name, ('Unbalanced environment',name)
            _, start, body_start = stack.pop()
            if name in selected:
                assert not any(s[0] in selected for s in stack), 'Nested assessment'
                spans.append({'kind':name, 'range':[start,match.end()], 'body_range':[body_start,match.start()]})
    assert not stack, 'Unclosed environment'
    return sorted(spans, key=lambda s:s['range'][0])


def reconstruct_native(released, bridge):
    assert identity(released) == bridge['released'], 'Released file drift'
    payload = normal(released).encode()
    assert identity(payload) == bridge['normalized_utf8_lf']
    lines = payload.split(b'\n')
    endings = []
    for kind, count in bridge['native_line_endings_rle']:
        assert kind in {'LF','CRLF','CR'} and type(count) is int and 0 < count <= len(lines)
        endings.extend([{'LF':b'\n','CRLF':b'\r\n','CR':b'\r'}[kind]]*count)
    assert len(lines) == len(endings)+1, 'Invalid EOL reconstruction'
    raw = b''.join(line+end for line,end in zip(lines,endings))+lines[-1]
    if bridge['native_utf8_bom']:
        raw = b'\xef\xbb\xbf'+raw
    assert identity(raw) == bridge['native_file'], 'Native byte identity mismatch'
    return raw


def checked_node(tree, unit):
    found = tree.getroottree().xpath(unit['source']['locator']['xpath'])
    assert len(found) == 1, ('Source XPath',unit['id'])
    assert sha(canonical(found[0]).encode()) == unit['source']['content_sha256'], ('Source identity',unit['id'])
    return found[0]


def source_mapping(native, source_path, backend_path, bridges):
    profile = native['profiles']['CLP1']
    units = {u['id']:u for u in profile['units']}
    assert len(units) == len(profile['units'])
    support_ids = defaultdict(lambda:defaultdict(list))
    for relation in profile['relations']:
        kind = {'has_hint':'hint','has_answer':'answer','has_solution':'solution'}[relation['relation_type']]
        component = units[relation['target_id']]
        assert component['parent_id'] == relation['source_id'] and component['unit_type'] == kind
        support_ids[relation['source_id']][kind].append(component)
    common = {r['native_id']:r['id'] for r in native['common_exercises'] if r['profile'] == 'CLP1'}
    grouped = defaultdict(list)
    for unit in units.values():
        if unit['unit_type'] == 'exercise':
            grouped[unit['source']['locator']['path']].append(unit)
    assert set(grouped) == {r['source_path'] for r in bridges['files']}
    bridge_by_source = {r['source_path']:r for r in bridges['files']}
    with zipfile.ZipFile(backend_path) as backend:
        member = next(m for m in profile['members'] if m['path'].endswith('/units.jsonl'))
        raw = backend.read(member['path'])
        assert sha(raw) == member['sha256']
        native_files = {u['source']['locator']['path']:u for u in map(json.loads,raw.splitlines()) if u['unit_type']=='source_file'}
    questions, files, reachable, edges = [], [], {}, []
    with zipfile.ZipFile(source_path) as source:
        assert source.testzip() is None
        todo = ['pretext/clp_1_dc.xml']
        while todo:
            path = todo.pop()
            if path in reachable:
                continue
            raw = source.read(path)
            reachable[path] = identity(raw)
            for include in xml(raw).findall('.//{http://www.w3.org/2001/XInclude}include'):
                assert include.get('xpointer') is None
                dest = posixpath.normpath(posixpath.join(posixpath.dirname(path),include.get('href')))
                assert dest.startswith('pretext/') and ':' not in dest
                edges.append({'from':path,'to':dest})
                todo.append(dest)
        for path, rows in sorted(grouped.items()):
            assert path in reachable
            rows.sort(key=lambda u:u['order'])
            bridge = bridge_by_source[path]
            target_path = bridge['target_path']
            mapping_kind = 'native-file-link'
            if path in REPARENTED:
                parent, expected_target = REPARENTED[path]
                assert target_path == expected_target and {'from':parent,'to':path} in edges
                assert all(u['target']['locators'] == [] for u in rows)
                binding = native_files[parent]['target']
                mapping_kind = 'source-child-translated-in-parent-file'
            else:
                binding = rows[0]['target']
                assert all(u['target'] == binding for u in rows)
            assert binding['locators'] == [target_path]
            source_raw, target_raw = source.read(path), source.read(target_path)
            assert identity(source_raw) == bridge['source']
            original_raw = reconstruct_native(target_raw,bridge['target_identity_bridge'])
            assert binding['file_sha256'] == [sha(original_raw)]
            text, tree = normal(target_raw), xml(source_raw)
            spans = environments(text)
            targets = [s for s in spans if s['kind'] in {'question','Mquestion'}]
            children = tree.xpath('./exercisegroup/exercise | ./exercise')
            assert len(targets) == len(rows) == len(children)
            files.append({'source_path':path, 'source':identity(source_raw), 'target_path':target_path,
                          'target':identity(target_raw), 'normalized_target':identity(text.encode()),
                          'native_target':identity(original_raw), 'mapping_kind':mapping_kind})
            for ordinal, (unit, target, child) in enumerate(zip(rows,targets,children),1):
                assert checked_node(tree,unit) == child
                assert unit['source']['sha256'] == sha(source_raw)
                assert (child.get('purpose') == 'RQS') == (target['kind'] == 'Mquestion')
                next_start = targets[ordinal]['range'][0] if ordinal < len(targets) else len(text)
                supports = [s for s in spans if target['range'][1] <= s['range'][0] < next_start]
                assert Counter(s['kind'] for s in supports) == Counter({k:len(v) for k,v in support_ids[unit['id']].items()})
                mapped_supports = []
                for kind in LABELS:
                    native_supports = sorted(support_ids[unit['id']][kind],key=lambda u:u['order'])
                    target_supports = [s for s in supports if s['kind'] == kind]
                    for support, span in zip(native_supports,target_supports):
                        assert checked_node(tree,support).getparent() == child
                        a,b = span['range']
                        mapped_supports.append({'native_id':support['id'], 'kind':kind,
                            'source_xpath':support['source']['locator']['xpath'],
                            'source_content_sha256':support['source']['content_sha256'],
                            'target_range':[a,b], 'target_body_range':span['body_range'],
                            'target_span_sha256':sha(text[a:b].encode())})
                a,b = target['range']
                questions.append({'native_id':unit['id'], 'common_id':common[unit['id']],
                    'source_path':path, 'source_xpath':unit['source']['locator']['xpath'],
                    'source_content_sha256':unit['source']['content_sha256'],
                    'target_path':target_path, 'target_range':[a,b], 'target_body_range':target['body_range'],
                    'target_span_sha256':sha(text[a:b].encode()), 'target_ordinal':ordinal,
                    'mapping_kind':mapping_kind, 'native_translation_state':unit['translation_state'],
                    'supports':mapped_supports})
        master = source.read('latex/problembook/clp_1_dc_problems.tex')
        style = source.read('latex/problembook/qhas.sty')
    assert len(questions) == len(common) == 695
    assert Counter(s['kind'] for q in questions for s in q['supports']) == {'hint':620,'answer':695,'solution':695}
    return {'questions':questions,'files':files,'include_edges':edges,'reachable_sources':reachable,
            'master':master,'style':style}


def counter_contexts(master, questions):
    paths = {q['target_path'] for q in questions}
    contexts = {}
    chapter = section = subsection = 0
    mainmatter = False
    pattern = r'\\(chapter|section|subsection|frontmatter|mainmatter|backmatter)(?![A-Za-z*])|\\input\s*\{(problems/[^{}]+)\}'
    for match in re.finditer(pattern,mask_comments(normal(master))):
        heading, member = match.groups()
        if heading in {'frontmatter','backmatter'}:
            mainmatter = False
        elif heading == 'mainmatter':
            mainmatter = True
        elif heading == 'chapter':
            if mainmatter:
                chapter += 1
                section = subsection = 0
        elif heading == 'section':
            section += 1
            subsection = 0
        elif heading == 'subsection':
            subsection += 1
        else:
            path = 'latex/problembook/'+member+('.tex' if not member.endswith('.tex') else '')
            assert path in paths and path not in contexts, ('Unexpected master input',path)
            contexts[path] = [chapter,section,subsection]
    assert set(contexts) == paths
    return contexts


def support_label(text):
    matches = list(re.finditer(r'(?<!\w)(Petunjuk|Jawaban|Penyelesaian)\s+(\d+)\s*:',text))
    assert len(matches) <= 1, 'Ambiguous support label'
    if not matches:
        return None
    match = matches[0]
    return {v:k for k,v in LABELS.items()}[match[1]], int(match[2])


def bind_supports(questions, records):
    by_destination = {q['printed']['backlink_destination']:q for q in questions}
    assert len(by_destination) == len(questions)
    seen = set()
    for record in records:
        assert record['destination'] in by_destination, 'Unknown support destination'
        question = by_destination[record['destination']]
        assert record['number'] == question['target_ordinal'], 'Printed support number mismatch'
        assert record['target_page'] == question['printed']['page'], 'Support backlink page mismatch'
        key = (question['native_id'],record['kind'])
        assert key not in seen, 'Duplicate printed support'
        seen.add(key)
        supports = [s for s in question['supports'] if s['kind'] == record['kind']]
        assert len(supports) == 1, 'Invented or ambiguous support'
        supports[0]['printed'] = {k:v for k,v in record.items() if k not in {'kind','number'}}
    assert len(seen) == sum(len(q['supports']) for q in questions) == 2010, 'Missing printed support'
    assert all('printed' in s for q in questions for s in q['supports'])


def printed_mapping(pdf_path, mapped, contexts):
    with fitz.open(pdf_path) as doc:
        assert len(doc) == 646
        names = doc.resolve_names()
        used = set()
        for question in mapped['questions']:
            context = contexts[question['target_path']]
            suffix = '.'.join(map(str,[*context,question['target_ordinal']]))
            global_name, local_name = 'GlobalQCounter.'+suffix, 'QCounter.'+suffix
            assert global_name not in used and global_name in names and local_name in names
            used.add(global_name)
            assert names[global_name]['page'] == names[local_name]['page']
            page = names[global_name]['page']+1
            question['printed'] = {'page':page, 'destination':global_name,
                'backlink_destination':local_name, 'counter_context':context,
                'question_number':question['target_ordinal'], 'fragment':'page='+str(page)}
        excluded = sorted(n for n in names if n.startswith('GlobalQCounter.') and n not in used)
        assert excluded == ['GlobalQCounter.0.0.0.1','GlobalQCounter.0.0.0.2']
        parts = [row for row in doc.get_toc() if row[0] == 1]
        bounds = {}
        for kind, title in [('hint','II Petunjuk untuk Soal'),('answer','III Jawaban Soal'),('solution','IV Penyelesaian Soal')]:
            matches = [p for p in parts if p[1] == title]
            assert len(matches) == 1
            bounds[kind] = matches[0][2]
        assert bounds['hint'] < bounds['answer'] < bounds['solution']
        records, page_evidence = [], []
        for page in doc:
            if page.number+1 < bounds['hint']:
                continue
            assert page.rotation == 0
            textpage = page.get_textpage()
            found_here = 0
            for xref, annotation_kind, _ in page.annot_xrefs():
                if annotation_kind != 1 or doc.xref_get_key(xref,'A/S') != ('name','/GoTo'):
                    continue
                dtype, destination = doc.xref_get_key(xref,'A/D')
                if dtype != 'string' or not destination.startswith('QCounter.'):
                    continue
                rect_type, rect_text = doc.xref_get_key(xref,'Rect')
                assert rect_type == 'array'
                coordinates = [float(n) for n in re.findall(r'-?\d+(?:\.\d+)?',rect_text)]
                assert len(coordinates) == 4
                rect = fitz.Rect(coordinates)*page.transformation_matrix
                snippet = page.get_textbox(rect+(-2,-2,2,2),textpage=textpage).strip()
                label = support_label(snippet)
                if label is None:
                    continue  # Ordinary cross-references are not support headings.
                kind, number = label
                lo = bounds[kind]
                hi = {'hint':bounds['answer'],'answer':bounds['solution'],'solution':len(doc)+1}[kind]
                assert lo <= page.number+1 < hi, ('Wrong printed part',kind,page.number+1)
                assert destination in names
                records.append({'kind':kind, 'number':number, 'page':page.number+1,
                    'fragment':'page='+str(page.number+1), 'label':LABELS[kind]+' '+str(number)+':',
                    'destination':destination, 'target_page':names[destination]['page']+1,
                    'annotation_xref':xref, 'annotation_sha256':sha(doc.xref_object(xref).encode()),
                    'rectangle_pdf_points':coordinates,
                    'label_region_text_sha256':sha(snippet.encode())})
                found_here += 1
            if found_here:
                page_evidence.append({'page':page.number+1, 'support_headings':found_here,
                                      'text_sha256':sha(page.get_text(textpage=textpage).encode())})
        assert Counter(r['kind'] for r in records) == {'hint':620,'answer':695,'solution':695}
        bind_supports(mapped['questions'],records)
        return {'support_part_first_pages':bounds,'support_pages':page_evidence,
                'excluded_preface_examples':excluded,
                'method':'Source counters + named question destinations + printed support labels and their actual PDF GoTo backlinks. PDF links navigate to the verified start page, not the full solution extent.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-zip',type=Path,required=True)
    parser.add_argument('--backend-zip',type=Path,required=True)
    parser.add_argument('--pdf',type=Path,required=True)
    parser.add_argument('--bridges',type=Path,default=BASE/'input/clp1-file-bridges.json')
    parser.add_argument('--output',type=Path,default=BASE/'clp1-navigation.json')
    args = parser.parse_args()
    raw_inputs = {'native':(BASE/'input/native-exercises.json').read_bytes(),
                  'source':args.source_zip.read_bytes(), 'backend':args.backend_zip.read_bytes(),
                  'pdf':args.pdf.read_bytes()}
    for key,raw in raw_inputs.items():
        assert sha(raw) == EXPECTED[key], ('Pinned input mismatch',key)
    bridge_raw = args.bridges.read_bytes()
    bridges = json.loads(bridge_raw)
    assert bridges['schema'] == 'clp1-native-eol-bridges/1'
    native = json.loads(raw_inputs['native'])
    mapped = source_mapping(native,args.source_zip,args.backend_zip,bridges)
    contexts = counter_contexts(mapped['master'],mapped['questions'])
    print('Source identities and spans passed; checking printed navigation.',flush=True)
    printed = printed_mapping(args.pdf,mapped,contexts)
    reader = next(r for c in native['readers'] if c['course_id']=='B20' for r in c['actions'] if r['role']=='problembook')
    assert reader['sha256'] == EXPECTED['pdf']
    result = {'schema':'clp1-exact-navigation/1', 'state':'mapped-not-admitted',
              'inputs':{k:identity(v) for k,v in raw_inputs.items()}, 'bridges':identity(bridge_raw),
              'master':identity(mapped.pop('master')), 'qhas_style':identity(mapped.pop('style')),
              'reader':{'url':reader['url'],'filename':reader['filename'],'pages':646,'sha256':reader['sha256']},
              'contexts':contexts, **mapped, 'printed_evidence':printed,
              'counts':{'questions':695,'hints':620,'answers':695,'solutions':695,
                        'questions_without_recorded_hint':75,'reparented_questions':30},
              'scope':'Exact native XML identities and released translated structural spans and printed start pages; no new translation or semantic-review claim.',
              'limitations':[
                  'Native records, rights and historical translation states are unchanged; new locators are an additive correction overlay.',
                  'Matched by complete per-file order, assessment kind, exact native source content and support relationships; not a fresh proof of mathematical or translation equivalence.',
                  'Question and support page links apply only to the SHA-256-pinned Indonesian problem PDF, not other editions or English books.',
                  'A support start page does not claim the complete multi-page solution extent. Seventy-five exercises have no recorded hint.'
              ]}
    args.output.write_bytes(encode(result))
    print(json.dumps({'state':result['state'],'questions':len(result['questions']),
                      'supports':sum(len(q['supports']) for q in result['questions']),
                      'output':identity(args.output.read_bytes())}))


if __name__ == '__main__':
    main()
