"""Independent field, identity, native-graph, destination and replay checks for C100."""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import tempfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import jsonschema
from geometry_capability_v1 import ROOT, BASE, READER, READER_URL, SITE_URL, read_inputs, load_json, fact, encoded, Anchors


def verify_projection(model, source):
    original_concepts = [row for _, row in source['concepts']]
    assert [c['native'] for c in model['concepts']] == original_concepts
    assert [t['native'] for t in model['terms']] == source['terms']
    assert [t['id'] for t in model['terms']] == [t['term_id'] for t in source['terms']]
    assert len({t['id'] for t in model['terms']})==len(model['terms'])
    assert [f['native'] for f in model['figures']] == source['figures']
    assert model['corrections'] == [r for r in source['catalog']['records'] if r['entity_type']=='correction']
    assert model['rights_accessibility'] == source['rights_accessibility']
    assert model['native_edition'] == next(r for r in source['catalog']['records'] if r['id']=='o004-petrunin-current-0b0858e')
    units = {u['stable_unit_id']:u for u in source['units']}
    concepts = {c['id']:c for c in model['concepts']}
    assert len(concepts) == 491
    graph={}
    for c, (path, native) in zip(model['concepts'],source['concepts'],strict=True):
        assert c['id']==native['concept_id'] and c['source_file']==path
        required=[x.strip() for x in native['prerequisite_concept_ids'].split(';') if x.strip()]
        assert c['prerequisites']==[{'id':x,'resolved':x in concepts} for x in required]
        assert all(x in concepts for x in required) and len(set(required))==len(required)
        graph[c['id']]=required
        if native['first_unit_id'] in units:
            assert c['reading']==units[native['first_unit_id']]['learner_route']['url']
            assert c['reading_state']=='exact_native_unit' and c['fallback_evidence']==[]
        else:
            assert c['id'] in {'o004.concept.orthocentric-system','o004.concept.homothety','o004.concept.excenter'}
            assert native['first_unit_id']=='o004.petrunin.seg.hints-ch08'
            evidence=next(r for r in source['catalog']['relations'] if r['id']=='rel-seg-hints-ch08')
            assert evidence['type']=='contains' and evidence['to']==native['first_unit_id']
            assert c['reading_state']=='chapter_fallback' and c['fallback_evidence']==[evidence]
            assert c['reading']==units[evidence['from']]['learner_route']['url']
        lexical=[t['term_id'] for t in source['terms'] if (t['source_term'],t['preferred_id_ID'])==(native['source_term'],native['preferred_id_ID'])]
        assert c['lexical_term_matches']==lexical
    visiting,visited=set(),set()
    def visit(key):
        assert key not in visiting, 'Concept prerequisite cycle'
        if key in visited:return
        visiting.add(key)
        for target in graph[key]:visit(target)
        visiting.remove(key);visited.add(key)
    for key in graph:visit(key)
    assert sum(map(len,graph.values()))==994
    assert Counter(c['native']['status'] for c in model['concepts'])=={'admitted':18,'mapped-admitted':125,'mapped-pending-qa':348}
    assert Counter(len(c['lexical_term_matches']) for c in model['concepts'])[0]==265
    reader=Anchors();reader.feed(source['reader'])
    for f in model['figures']:
        assert f['id']==f['native']['asset_id']
        present=f['id'] in reader.figures
        assert f['reading']==(READER_URL+'#'+f['id'] if present else None)
        assert f['reading_state']==('exact_figure_description' if present else 'not_present_in_reader')
        assert f['native_illustrates_relations']==[r for r in source['catalog']['relations'] if r['type']=='illustrates' and r['from']==f['id']]
        if not present:
            assert f['id']=='o004.petrunin.fig.ch19.05' and f['native']['status']=='source-disabled-preserved'
    exercise_units=[u for u in source['units'] if 'exercise' in u['native_unit_kind']]
    assert [e['unit'] for e in model['exercises']]==exercise_units
    native_rows={r['exercise_id']:r for r in source['exercise_rows']}
    for e in model['exercises']:
        uid=e['id'];assert uid==e['unit']['stable_unit_id']
        assert e['learner_url']==SITE_URL+'C100.html#'+uid
        assert e['native_exercise_row']==native_rows.get(uid)
        expected=[]
        parents=[]
        for r in source['relations']:
            if r['relation_type']=='guided_by' and r['from_id']==uid:expected.append(('hint',r['to_id'],r))
            if r['relation_type']=='solves' and r['to_id']==uid:expected.append(('independently_authored_solution',r['from_id'],r))
            if r['relation_type']=='part_of_exercise' and r['from_id']==uid:parents.append(r['to_id'])
        assert e['parents']==parents
        assert [(s['kind'],s['unit']['stable_unit_id'],s['relation']) for s in e['support']]==expected
        assert all(s['unit']==units[s['unit']['stable_unit_id']] for s in e['support'])
        assert e['support_state']==('linked_support' if expected else 'no_direct_support_recorded')
        assert e['chapter']==re.search(r'\.ch(\d{2})',uid).group(1)
    assert model['chapter_dependencies']==[r for r in source['relations'] if r['relation_type']=='depends_on']
    assert model['chapters']==[u for u in source['units'] if u['native_unit_kind']=='chapter']
    assert model['counts']=={'stable_units':939,'exercise_surfaces':285,'parent_exercises':253,'concepts':491,
      'terms':432,'figure_records':214,'figures_in_reader':213,'corrections':207,'relations':994,
      'unmapped_concept_readings':0,'chapter_fallback_readings':3,'unresolved_prerequisites':0,
      'concept_statuses':{'admitted':18,'mapped-admitted':125,'mapped-pending-qa':348}}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.ids=set();self.links=[];self.plans=[];self.choices=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:assert a['id'] not in self.ids;self.ids.add(a['id'])
        for field in ['href','src']:
            if a.get(field):self.links.append(a[field])
        if 'data-plan' in a:self.plans.append(json.loads(a['data-plan']))
        if tag=='input' and a.get('type')=='checkbox':self.choices+=1;assert a.get('aria-label')


def validate(output_root, write_receipt=True):
    source=read_inputs();model=load_json(output_root/'docs/backend/geometry/learning-map.json')
    schema=load_json(ROOT/'schemas/course-capsule-v1/geometry-learning-capability-v1.schema.json')
    jsonschema.Draft202012Validator(schema).validate(model)
    verify_projection(model,source)
    manifest=load_json(output_root/BASE/'manifest.json')
    for item in manifest['inputs']:assert fact(item['path'],(ROOT/item['path']).read_bytes())==item
    for item in manifest['outputs']:assert fact(item['path'],(output_root/item['path']).read_bytes())==item
    negative=[]
    mutants=[('promoted_pending',lambda x:x['concepts'][100]['native'].__setitem__('status','admitted')),
             ('lost_term_context',lambda x:x['terms'][0]['native'].__setitem__('rejected_or_contextual','')),
             ('wrong_unique_term_id',lambda x:x['terms'][1].__setitem__('id','O004-TERM-WRONG-IDENTITY')),
             ('wrong_figure_destination',lambda x:x['figures'][0].__setitem__('reading',READER_URL+'#wrong')),
             ('lost_correction',lambda x:x['corrections'].pop()),
             ('lost_prerequisite',lambda x:next(c for c in x['concepts'] if c['prerequisites'])['prerequisites'].pop()),
             ('false_solution_page',lambda x:next(s for e in x['exercises'] for s in e['support'] if s['kind']=='independently_authored_solution')['unit']['learner_route'].__setitem__('url','https://example.invalid/#page=9')),
             ('lost_source_identity',lambda x:x['exercises'][0]['unit'].__setitem__('source_sha256','0'*64)),
             ('fallback_as_exact',lambda x:next(c for c in x['concepts'] if c['reading_state']=='chapter_fallback').__setitem__('reading_state','exact_native_unit'))]
    for name,mutate in mutants:
        candidate=copy.deepcopy(model);mutate(candidate)
        try:verify_projection(candidate,source)
        except (AssertionError,KeyError):negative.append(name)
        else:raise AssertionError('Mutation accepted: '+name)
    pages={}
    for item in manifest['outputs']:
        if item['path'].endswith('.html'):
            page=Page();page.feed((output_root/item['path']).read_text('utf-8'));pages[item['path']]=page
    verified_links=0
    anchor_cache={}
    for relative,page in pages.items():
        for url in page.links:
            parsed=urlsplit(url)
            if parsed.scheme and parsed.netloc!='kokunoyumeto.github.io':continue
            if parsed.netloc:
                prefix='/program-matematika-indonesia/'
                assert parsed.path.startswith(prefix)
                target=ROOT/'docs'/unquote(parsed.path[len(prefix):])
            else:target=(output_root/relative).parent/unquote(parsed.path)
            if parsed.path.endswith('/') or target.is_dir():target=target/'index.html'
            if parsed.path=='':target=output_root/relative
            if not target.exists():
                relative_target=target.resolve().relative_to(output_root.resolve())
                target=ROOT/relative_target
            if target.name=='validation.json':continue # Emitted after validation, not a content source.
            assert target.is_file(),url
            if parsed.fragment and target.suffix=='.html':
                key=target.resolve()
                if key not in anchor_cache:
                    dest=Anchors();dest.feed(target.read_text('utf-8'));anchor_cache[key]=dest.ids
                assert unquote(parsed.fragment) in anchor_cache[key],url
            verified_links+=1
    teacher=pages['docs/backend/geometry/pengajar.html']
    assert teacher.choices==776 and len(teacher.plans)==776
    concept_map={c['id']:c for c in model['concepts']};exercise_map={e['id']:e for e in model['exercises']}
    for plan in teacher.plans:
        if plan['jenis']=='konsep':
            c=concept_map[plan['id']]
            assert plan['bacaan']==c['reading'] and plan['ketepatan_lokasi']==c['reading_state']
            assert plan['prasyarat']==[p['id'] for p in c['prerequisites']]
        else:
            e=exercise_map[plan['id']]
            assert plan['pelajar']==e['learner_url'] and plan['bacaan']==e['unit']['learner_route']['url']
            assert plan['sumber']['sha256']==e['unit']['source_sha256']
            assert plan['terjemahan']['sha256']==e['unit']['target_sha256']
    with tempfile.TemporaryDirectory(prefix='geometry-replay-') as temp:
        tmp=Path(temp)
        for name in ['a','b']:
            subprocess.run(['python','-B',str(ROOT/'scripts/build-geometry-capability-v1.py'),'--output-root',str(tmp/name)],check=True,capture_output=True)
        for item in manifest['outputs']+[fact(BASE/'manifest.json',(output_root/BASE/'manifest.json').read_bytes())]:
            assert (tmp/'a'/item['path']).read_bytes()==(tmp/'b'/item['path']).read_bytes()==(output_root/item['path']).read_bytes(),item['path']
    controls=subprocess.run(['node',str(ROOT/'scripts/test-geometry-controls-v1.mjs')],check=True,capture_output=True,text=True)
    receipt={'state':'pass','contract':model['contract'],'roles':['C100'],
             'manifest_sha256':fact('',(output_root/BASE/'manifest.json').read_bytes())['sha256'],
             'schema_validation':True,'all_native_projected_fields_preserved':True,'source_and_pilot_bindings_verified':True,
             'concept_graph_acyclic':True,'native_pending_states_preserved':True,'learner_teacher_shared_identity':True,
             'isolated_two_build_byte_identity':True,'reader_byte_identity_preserved':True,
             'negative_fixtures_rejected':negative,'teacher_selections_checked':776,'local_links_checked':verified_links,
             'controls':json.loads(controls.stdout),'counts':model['counts'],
             'scope':'Metadata, native graph, existing destinations, selected-plan data and deterministic adapter; no new book-build or visual/linguistic certification.'}
    if write_receipt:
        for path in [BASE/'validation.json',Path('docs/backend/geometry/validation.json')]:
            (output_root/path).write_bytes(encoded(receipt))
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-root',type=Path,default=ROOT)
    args=parser.parse_args();print(json.dumps(validate(args.output_root)))
