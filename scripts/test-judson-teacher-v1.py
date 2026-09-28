"""Exercise-level native/consumer checks, mutation rejection, deterministic builds."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'backend/course-capsule-v1/adapters/judson-teacher-v1'
spec=importlib.util.spec_from_file_location('judson_builder',ROOT/'scripts/build-judson-teacher-v1.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)


def canonical(node):
    copy=deepcopy(node);copy.tail=None
    return hashlib.sha256(ET.canonicalize(ET.tostring(copy,encoding='unicode'),strip_text=False,rewrite_prefixes=False).encode()).hexdigest()


def node_at(tree,xpath):
    return tree.find('./'+xpath.split('/',2)[2])


def independent_native_check(native,source_archive):
    old=ROOT/'backend/course-capsule-v1/adapters/judson-v231'
    units=[json.loads(l) for l in (old/'tables/units.jsonl').read_bytes().splitlines()]
    rels=[json.loads(l) for l in (old/'tables/relations.jsonl').read_bytes().splitlines()]
    expected={u['id']:u['payload'] for u in units if u['payload']['kind']=='exercise'}
    by_native={u['payload']['native_id']:u['payload'] for u in units}
    assert set(expected)=={r['id'] for r in native['exercises']}
    assert len(expected)==913
    expected_edges={r['id']:r['payload'] for r in rels if r['payload']['type'] in ['has_hint','has_response']}
    supplied_edges={s['relation_id']:s for e in native['exercises'] for s in e['support']}
    assert expected_edges.keys()==supplied_edges.keys()
    body=source_archive.read_bytes()
    assert b.fact(body)=={k:native['source_archive'][k] for k in ['bytes','sha256']}
    counts=Counter();support_counts=Counter();source_trees={};target_trees={}
    with zipfile.ZipFile(source_archive) as z:
        for member,identity in native['source_member_identities'].items(): assert b.fact(z.read(member))==identity
        prefix='authority/upstream-043274d5/aata-043274d5dead03ff007a461ffe4c2b8477be1248/src/'
        for path in {e['source_path'] for e in native['exercises']}:
            source_trees[path]=ET.fromstring(z.read(prefix+path));target_trees[path]=ET.fromstring(z.read('src/'+path))
    for e in native['exercises']:
        p=expected[e['id']]
        for key in ['native_id','source_path','source_xpath','source_xml_id','source_c14n_sha256','parent_native_id','preorder_index']:
            assert e[key]==p['parent_id' if key=='parent_native_id' else key],(e['id'],key)
        assert p['curriculum_role_ids']==[e['course_id']]
        sn=node_at(source_trees[e['source_path']],e['source_xpath'])
        tn=node_at(target_trees[e['source_path']],e['target_xpath'])
        assert sn.tag==tn.tag=='exercise' and canonical(sn)==e['source_c14n_sha256']
        assert canonical(tn)==e['target_c14n_sha256']
        label=tn.get('{http://www.w3.org/XML/1998/namespace}id') or tn.get('label')
        if label: assert label==e['target_identifier']
        else: assert e['identifier_method']=='hash_verified_xpath_and_pretext_structural_identifier' and e['unlabelled_rendered_prose_witnesses']
        for support in e['support']:
            edge=expected_edges[support['relation_id']]
            assert edge['from_id']==e['native_id'] and edge['to_id']==support['native_unit_id']
            assert edge['to_projected_unit_id']==support['projected_unit_id']
            np=by_native[support['native_unit_id']]
            s=node_at(source_trees[np['source_path']],np['source_xpath'])
            t=node_at(target_trees[np['source_path']],np['source_xpath'])
            assert s in list(sn) and t in list(tn)
            assert canonical(s)==np['source_c14n_sha256']==support['source_c14n_sha256']
            assert canonical(t)==support['target_c14n_sha256']
            assert support['target_has_content']==bool(''.join(t.itertext()).strip() or len(t))
            support_counts[(t.tag,support['target_has_content'])]+=1
        counts[e['course_id']]+=1
    assert counts=={'C30':610,'C40':303}
    assert support_counts=={('hint',True):213,('response',False):116}
    return {'all_native_exercises':913,'all_native_support_edges':329,'all_source_target_subtrees':1242,'source_archive_rehashed':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-archive',type=Path)
    parser.add_argument('--report',type=Path,default=BASE/'tests.json')
    args=parser.parse_args();native,lock=b.load();model=b.project(native,lock)
    native_evidence=independent_native_check(native,args.source_archive) if args.source_archive else {'native_archive_replay':'not_run'}
    fixtures=[]
    def reject(name,mutate):
        altered=deepcopy(native);mutate(altered)
        try:b.project(altered,lock)
        except (AssertionError,KeyError,ValueError,TypeError):fixtures.append(name)
        else:raise AssertionError('Mutation passed: '+name)
    reject('duplicate common identity',lambda n:n['exercises'].append(n['exercises'][0]))
    reject('duplicate native identity',lambda n:n['exercises'][1].update(native_id=n['exercises'][0]['native_id']))
    reject('wrong course',lambda n:n['exercises'][0].update(course_id='C40'))
    reject('chapter crosswire',lambda n:n['chapters'][0].update(course_id='C40'))
    reject('target path drift',lambda n:n['exercises'][0].update(target_xpath='/wrong'))
    reject('fragment drift',lambda n:n['exercises'][0].update(reader_fragment='wrong'))
    reject('unresolved mapping',lambda n:n.update(unresolved_mappings=1))
    reject('false answer presence',lambda n:n['exercises'][0]['support'][0].update(target_has_content=True))
    reject('response slot called content',lambda n:n['exercises'][0]['support'][0].update(availability='provided_content'))
    reject('primary reader missing',lambda n:n['exercises'][0].update(reader_edition='other'))
    reject('duplicate reader profile',lambda n:n['exercises'][0]['reader_targets'].append(n['exercises'][0]['reader_targets'][0]))
    reject('path escape',lambda n:n['exercises'][0]['reader_targets'][0].update(member='../outside.html'))
    reject('invalid profile',lambda n:n['exercises'][0]['reader_targets'][0].update(edition='other'))
    def break_node(n):
        e=n['exercises'][0];t=e['reader_targets'][0]
        n['reader_witnesses'][t['edition']+'/'+t['member']]['exercise_nodes'][t['fragment']]['class']='example'
    reject('nonexercise target',break_node)
    access=json.loads((BASE/'input/reader-access.json').read_bytes())
    b.attach_current_routes(deepcopy(model),access)
    def reject_route(name,mutate):
        altered=deepcopy(access);mutate(altered)
        try:b.attach_current_routes(deepcopy(model),altered)
        except (AssertionError,KeyError,ValueError,TypeError):fixtures.append(name)
        else:raise AssertionError('Route mutation passed: '+name)
    reject_route('unverified live route',lambda a:a.update(complete=False))
    reject_route('missing live anchor',lambda a:a['observations'][0]['expected_anchors'].pop())
    reject_route('injected live URL',lambda a:a['observations'][0].update(url='javascript:alert(1)'))
    reject_route('live source drift',lambda a:a.update(input_sha256='wrong'))
    with tempfile.TemporaryDirectory(prefix='judson-replay-') as scratch:
        one=b.build(Path(scratch)/'one');two=b.build(Path(scratch)/'two')
        assert one==two
        for f in one['files']:
            assert (Path(scratch)/'one'/f['path']).read_bytes()==(Path(scratch)/'two'/f['path']).read_bytes()
        deterministic_files=len(one['files'])
    report={'schema':'judson-teacher-tests/1','state':'pass','input_identity':lock,
        'native_checks':native_evidence,'negative_fixtures':fixtures,'deterministic_files':deterministic_files,
        'counts':{c['course_id']:c['exercise_count'] for c in model['courses']},
        'limits':'No shared admission, public delivery, current-live reader identity, or independent whole-book language review asserted.'}
    args.report.write_bytes(b.encoded(report));print(json.dumps(report))


if __name__=='__main__':main()
