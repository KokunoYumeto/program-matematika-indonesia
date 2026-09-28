"""Inspect frozen Judson exercise/response identities before teacher delivery.

Does not modify the producer package or assert live-reader byte identity.
Only the exact frozen public WEB archive may be fetched, once, into a cache.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import csv
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
from urllib.request import urlopen
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT/'backend/course-capsule-v1/adapters/judson-v231'
OUTPUT = ROOT/'backend/course-capsule-v1/adapters/judson-teacher-v1/input'


def fact(data):
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def dump(data):
    return (json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8')


def canonical_hash(element):
    # Same documented canonicalization as the frozen native producer.
    standalone = deepcopy(element)
    standalone.tail = None
    text = ET.canonicalize(ET.tostring(standalone,encoding='unicode'),
                           strip_text=False,rewrite_prefixes=False)
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def xml_at(root, xpath):
    parts = xpath.lstrip('/').split('/')
    assert parts[0] == root.tag+'[1]', (root.tag,xpath)
    found = root.findall('./'+'/'.join(parts[1:])) if len(parts)>1 else [root]
    assert len(found) == 1, xpath
    return found[0]


def xml_identifier(node):
    return node.get('{http://www.w3.org/XML/1998/namespace}id') or node.get('label')


def structural_identifier(root, node):
    """PreTeXt's nearest-labelled-ancestor + element-child indexes; checked in HTML."""
    parents = {c:p for p in root.iter() for c in p}
    steps = []
    while not xml_identifier(node):
        parent = parents[node]
        steps.append(str(list(parent).index(node)+1))
        node = parent
    return '-'.join([xml_identifier(node),*reversed(steps)])


def prose_fragments(node):
    # Only direct prose outside math/index wrappers; never rewrite mathematics.
    out = []
    if node.tag in ['m','me','men','md','mdn','mrow','idx']:
        return out
    if node.text:
        out.append(' '.join(node.text.split()))
    for child in node:
        out.extend(prose_fragments(child))
        if child.tail:
            out.append(' '.join(child.tail.split()))
    return [s for s in out if len(s)>=30]


class Reader(HTMLParser):
    """Record actual HTML identities and nesting, never infer a target anchor."""
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.stack = []
        self.ids = {}
        self.duplicates = []
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang')
        parent = next((n['id'] for n in reversed(self.stack) if n['id']),None)
        row = {'tag':tag,'id':a.get('id'),'class':a.get('class',''),'parent_id':parent,
               'source_order':len(self.nodes),'ancestor_ids':[n['id'] for n in self.stack if n['id']]}
        self.nodes.append(row)
        if 'exercise' in row['class'].split():
            row['text'] = ''
        if row['id']:
            if row['id'] in self.ids:
                self.duplicates.append(row['id'])
            self.ids[row['id']] = row
        if tag not in {'meta','link','br','hr','img','input','source','wbr','area','base','embed','param','col','track'}:
            self.stack.append(row)

    def handle_data(self, data):
        for node in self.stack:
            if 'text' in node:
                node['text'] += data

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache',type=Path,required=True)
    parser.add_argument('--source-archive',type=Path,required=True)
    parser.add_argument('--sage-archive',type=Path,required=True)
    args = parser.parse_args()
    admission = json.loads((NATIVE/'ADMISSION.json').read_bytes())
    names = ['manifest.json','course-views.json','tables/units.jsonl','tables/relations.jsonl',
             'tables/content_bindings.jsonl','tables/rights.jsonl',
             'frozen-inputs/JUDSON_TWO_COURSE_LEARNER_ROUTES.json']
    raw = {}
    for name in names:
        body = (NATIVE/name).read_bytes()
        assert fact(body) == admission['inputs'][name], name
        raw[name] = body
    views = json.loads(raw['course-views.json'])['views']
    route_evidence = json.loads(raw['frozen-inputs/JUDSON_TWO_COURSE_LEARNER_ROUTES.json'])
    archive = route_evidence['offline']['web_archive']
    args.cache.mkdir(parents=True,exist_ok=True)
    cached = args.cache/archive['name']
    if not cached.exists():
        with urlopen(archive['public_url'],timeout=45) as response:
            body = response.read(archive['bytes']+1)
        assert fact(body) == {'bytes':archive['bytes'],'sha256':archive['sha256']}
        cached.write_bytes(body)
    else:
        assert fact(cached.read_bytes()) == {'bytes':archive['bytes'],'sha256':archive['sha256']}
    units = [json.loads(line) for line in raw['tables/units.jsonl'].splitlines()]
    relations = [json.loads(line) for line in raw['tables/relations.jsonl'].splitlines()]
    by_native = {u['payload']['native_id']:u for u in units}
    assert len(units) == len(by_native) == 3323
    chapters = {c['native_unit_id']:{**c,'course_id':v['curriculum_role_id']}
                for v in views for c in v['chapters']}
    assert len(chapters) == 23
    role_sets = {v['curriculum_role_id']:set(v['native_unit_ids']) for v in views}
    assert len(role_sets['C30']) == 2014 and len(role_sets['C40']) == 1279
    assert not role_sets['C30'] & role_sets['C40']
    outside = set(by_native)-role_sets['C30']-role_sets['C40']
    assert len(outside) == 30
    supports = defaultdict(list)
    for r in relations:
        p = r['payload']
        if p['type'] not in ['has_hint','has_response']:
            continue
        assert p['from_id'] in by_native and p['to_id'] in by_native
        assert by_native[p['from_id']]['payload']['kind'] == 'exercise'
        expected_kind = 'hint' if p['type'] == 'has_hint' else 'response'
        assert by_native[p['to_id']]['payload']['kind'] == expected_kind
        assert p['from_projected_unit_id'] == by_native[p['from_id']]['id']
        assert p['to_projected_unit_id'] == by_native[p['to_id']]['id']
        supports[p['from_id']].append({'relation_id':r['id'],'native_relation_id':p['native_id'],
                                     'type':p['type'],'native_unit_id':p['to_id'],
                                     'projected_unit_id':p['to_projected_unit_id']})

    def chapter_for(native):
        seen = set()
        while native not in chapters:
            assert native not in seen, 'Cycle in native ancestry'
            seen.add(native)
            native = by_native[native]['payload']['parent_id']
            assert native in by_native
        return chapters[native]

    source_archive = route_evidence['authority']['owner_native_source_package']
    assert fact(args.source_archive.read_bytes()) == {k:source_archive[k] for k in ['bytes','sha256']}
    release_fact = route_evidence['offline']['source_release_manifest']
    release_bytes = (args.source_archive.parent/release_fact['name']).read_bytes()
    assert fact(release_bytes) == {k:release_fact[k] for k in ['bytes','sha256']}
    release = json.loads(release_bytes)
    sage_archive = next(a for a in release['artifacts'] if a['name'].endswith('_SAGE.zip'))
    assert fact(args.sage_archive.read_bytes()) == {k:sage_archive[k] for k in ['bytes','sha256']}
    sage_archive['public_url'] = archive['public_url'].replace(archive['name'],sage_archive['name'])
    source_witnesses = {}
    source_trees, target_trees = {}, {}
    with zipfile.ZipFile(args.source_archive) as z:
        native_manifest = z.read('backend/v1/manifest.json')
        assert native_manifest == (NATIVE/'authority/native-manifest.json').read_bytes()
        source_witnesses['backend/v1/manifest.json'] = fact(native_manifest)
        members = {r['path']:r for r in csv.DictReader(io.StringIO(z.read('PACKAGE_MANIFEST.csv').decode('utf-8')))}
        license_files = {}
        for member in ['COPYING','src/gfdl.xml']:
            body = z.read(member)
            assert fact(body) == {'bytes':int(members[member]['bytes']),'sha256':members[member]['sha256']}
            source_witnesses[member] = fact(body)
            license_files[Path(member).name] = body
        prefix = 'authority/upstream-043274d5/aata-043274d5dead03ff007a461ffe4c2b8477be1248/src/'
        for name in sorted({u['payload']['source_path'] for u in units if u['payload']['kind']=='exercise'}):
            for member, trees in [(prefix+name,source_trees),('src/'+name,target_trees)]:
                body = z.read(member)
                assert fact(body) == {'bytes':int(members[member]['bytes']),'sha256':members[member]['sha256']}, member
                source_witnesses[member] = fact(body)
                trees[name] = ET.fromstring(body)
        for chapter in chapters.values():
            source_path = by_native[chapter['native_unit_id']]['payload']['source_path']
            chapter['english_title'] = ' '.join(''.join(source_trees[source_path].find('title').itertext()).split())

    html_witnesses = {}
    exercise_anchors = defaultdict(list)
    for edition,path in [('web',cached),('sage',args.sage_archive)]:
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            for name in sorted(n for n in z.namelist() if n.endswith('.html') and '/' not in n):
                body = z.read(name)
                doc = Reader()
                doc.feed(body.decode('utf-8'))
                assert not doc.duplicates, name
                selected = {}
                for key,node in doc.ids.items():
                    if 'ptx-content' in node['ancestor_ids'] and 'exercise' in node['class'].split():
                        assert node['tag'] in ['article','div','section']
                        exercise_anchors[key].append({'edition':edition,'member':name,'fragment':key,
                            'text':node.get('text',''),
                            'node':{k:v for k,v in node.items() if k not in ['id','text']}})
                        selected[key] = {k:v for k,v in node.items() if k not in ['id','text']}
                html_witnesses[edition+'/'+name] = {**fact(body),'language':doc.lang,'exercise_nodes':selected}
    with zipfile.ZipFile(cached) as z:
        for native, chapter in chapters.items():
            member = chapter['offline_member']
            body = z.read(member['path'])
            assert fact(body) == {'bytes':member['bytes'],'sha256':member['sha256']}
            doc = Reader()
            doc.feed(body.decode('utf-8'))
            assert not doc.duplicates, member['path']
            chapter_xml_id = by_native[native]['payload']['source_xml_id']
            assert chapter_xml_id in doc.ids
            chapter['offline_html_chapter_id'] = chapter_xml_id

    exercises, unresolved = [], []
    counts = Counter()
    for unit in sorted(units,key=lambda u:u['payload']['preorder_index']):
        p = unit['payload']
        if p['kind'] != 'exercise':
            continue
        chapter = chapter_for(p['native_id'])
        role = chapter['course_id']
        assert p['curriculum_role_ids'] == [role] and p['native_id'] in role_sets[role]
        source = xml_at(source_trees[p['source_path']],p['source_xpath'])
        assert source.tag == 'exercise' and canonical_hash(source) == p['source_c14n_sha256'], p['native_id']
        ident = xml_identifier(source)
        if ident:
            candidates = [n for n in target_trees[p['source_path']].iter('exercise') if xml_identifier(n)==ident]
            assert len(candidates) == 1, ('Ambiguous target',p['native_id'],ident)
            target = candidates[0]
            method = 'explicit_xml_id_or_label'
        else:
            target = xml_at(target_trees[p['source_path']],p['source_xpath'])
            assert target.tag == 'exercise' and xml_identifier(target) is None
            ident = structural_identifier(target_trees[p['source_path']],target)
            assert ident == structural_identifier(source_trees[p['source_path']],source)
            method = 'hash_verified_xpath_and_pretext_structural_identifier'
        # Both source and target locators must select the same identity; no ordinal-only guess.
        assert xml_at(target_trees[p['source_path']],p['source_xpath']) is target
        row = {'id':unit['id'],'native_id':p['native_id'],'course_id':role,
               'chapter_id':chapter['native_unit_id'],'source_path':p['source_path'],
               'source_xpath':p['source_xpath'],'source_xml_id':p['source_xml_id'],
               'source_c14n_sha256':p['source_c14n_sha256'],
               'preorder_index':p['preorder_index'],'parent_native_id':p['parent_id'],
               'source_label':source.get('label'),'target_identifier':ident,
               'identifier_method':method,
               'target_c14n_sha256':canonical_hash(target),'target_xpath':p['source_xpath'],
               'source_number':source.get('number'),
               'exercise_group_kind':by_native[p['parent_id']]['payload']['kind'],
               'support':supports[p['native_id']], 'reader_fragment':None}
        for support in row['support']:
            sp = by_native[support['native_unit_id']]['payload']
            sn = xml_at(source_trees[sp['source_path']],sp['source_xpath'])
            tn = xml_at(target_trees[sp['source_path']],sp['source_xpath'])
            assert canonical_hash(sn) == sp['source_c14n_sha256']
            assert sn in list(source) and tn in list(target) and sn.tag == tn.tag == sp['kind']
            support.update({'source_xpath':sp['source_xpath'], 'target_xpath':sp['source_xpath'],
                'source_c14n_sha256':canonical_hash(sn),'target_c14n_sha256':canonical_hash(tn),
                'source_has_content':bool(''.join(sn.itertext()).strip() or len(sn)),
                'target_has_content':bool(''.join(tn.itertext()).strip() or len(tn))})
            support['availability'] = 'provided_content' if support['target_has_content'] else 'empty_response_slot'
        hits = exercise_anchors[ident]
        assert len(hits) == len({h['edition'] for h in hits}), ('Ambiguous HTML identity',ident)
        if hits:
            hit = next((h for h in hits if h['edition']=='web'),hits[0])
            if method != 'explicit_xml_id_or_label':
                actual_text = ' '.join(hit['text'].split())
                matches = [s for s in prose_fragments(target.find('statement')) if s in actual_text]
                assert matches, ('No independent rendered-prose witness',p['native_id'],ident)
                row['unlabelled_rendered_prose_witnesses'] = [fact(s.encode('utf-8')) for s in matches]
                row['rendered_text_sha256'] = hashlib.sha256(actual_text.encode('utf-8')).hexdigest()
            row['reader_fragment'] = hit['fragment']
            row['reader_member'] = hit['member']
            row['reader_edition'] = hit['edition']
            row['reader_targets'] = [{k:h[k] for k in ['edition','member','fragment']} for h in hits]
            row['reader_mapping'] = 'hash_verified_native_xml_identity_matched_frozen_exercise_node'
            row['reader_node'] = hit['node']
        else:
            row['reader_mapping'] = 'unresolved'
            row['candidate_reader_count'] = len(hits)
            unresolved.append({**row,'parent':by_native[p['parent_id']]['payload']})
        counts[role] += 1
        exercises.append(row)
    assert counts == {'C30':610,'C40':303} and len(exercises) == 913
    result = {'schema':'judson-teacher-intake/1','status':'native_mappings_verified' if not unresolved else 'mapping_in_progress',
              'input_identities':{k:fact(v) for k,v in raw.items()}, 'web_archive':archive,
              'source_archive':source_archive,'source_member_identities':source_witnesses,
              'sage_archive':sage_archive,'release_manifest_identity':fact(release_bytes),
              'chapters':list(chapters.values()),'exercise_counts':dict(counts),
              'exercises':exercises,'outside_course_native_ids':sorted(outside),
              'support_counts':dict(Counter(r['type'] for rows in supports.values() for r in rows)),
              'exact_identity_mappings':sum(bool(r['reader_fragment']) for r in exercises),
              'identifier_methods':dict(Counter(e['identifier_method'] for e in exercises)),
              'reader_edition_counts':dict(Counter(e.get('reader_edition','unresolved') for e in exercises)),
              'support_availability_counts':dict(Counter(r['type']+':'+r['availability'] for e in exercises for r in e['support'])),
              'unresolved_mappings':len(unresolved),'reader_witnesses':html_witnesses,
              'rights':[json.loads(line) for line in raw['tables/rights.jsonl'].splitlines()],
              'book_prose_copied':False,'live_reader_byte_identity_claimed':False,
              'new_translation':False,'teacher_delivery_complete':False}
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/'native-exercise-intake.json').write_bytes(dump(result))
    (OUTPUT/'source-lock.json').write_bytes(dump({'path':'native-exercise-intake.json',**fact(dump(result))}))
    for name,body in license_files.items():
        (OUTPUT/name).write_bytes(body)
    (args.cache/'UNRESOLVED_EXERCISE_MAPPINGS.json').write_bytes(dump(unresolved))
    print(json.dumps({'status':result['status'],'counts':dict(counts),'support_counts':result['support_counts'],
                      'mapped':result['exact_identity_mappings'],'unresolved':len(unresolved),
                      'support_availability_counts':result['support_availability_counts'],
                      'input_bytes':(OUTPUT/'native-exercise-intake.json').stat().st_size}))


if __name__ == '__main__':
    main()
