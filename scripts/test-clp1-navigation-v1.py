"""Verify the B20 navigation overlay without editing any native artifact."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('clp1_navigation',ROOT/'scripts/map-clp1-navigation-v1.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def validate_structure(data, native):
    assert data['schema'] == 'clp1-exact-navigation/1' and data['state'] == 'mapped-not-admitted'
    assert data['reader']['sha256'] == m.EXPECTED['pdf'] and data['reader']['pages'] == 646
    assert data['inputs']['native']['sha256'] == m.EXPECTED['native']
    assert data['counts'] == {'questions':695,'hints':620,'answers':695,'solutions':695,
                             'questions_without_recorded_hint':75,'reparented_questions':30}
    q_by_id = {q['native_id']:q for q in data['questions']}
    units = {u['id']:u for u in native['profiles']['CLP1']['units']}
    originals = {u['id']:u for u in units.values() if u['unit_type']=='exercise'}
    assert len(q_by_id) == len(data['questions']) == 695 and set(q_by_id) == set(originals)
    common = {r['native_id']:r['id'] for r in native['common_exercises'] if r['profile']=='CLP1'}
    edges = {(r['source_id'],r['target_id'],r['relation_type']) for r in native['profiles']['CLP1']['relations']}
    observed_edges, printed_keys, locations, support_ids = set(), set(), set(), set()
    for ident,q in q_by_id.items():
        u = originals[ident]
        assert q['common_id'] == common[ident]
        assert q['source_content_sha256'] == u['source']['content_sha256']
        assert q['source_xpath'] == u['source']['locator']['xpath'] and q['source_path'] == u['source']['locator']['path']
        assert q['native_translation_state'] == u['translation_state']
        a,b = q['target_range']
        assert type(a) is int and type(b) is int and 0 <= a < b
        location = (q['target_path'],a,b)
        assert location not in locations
        locations.add(location)
        p = q['printed']
        suffix = '.'.join(map(str,p['counter_context']+[q['target_ordinal']]))
        assert p['destination'] == 'GlobalQCounter.'+suffix and p['backlink_destination'] == 'QCounter.'+suffix
        assert p['counter_context'] == data['contexts'][q['target_path']]
        assert p['question_number'] == q['target_ordinal']
        assert 15 <= p['page'] <= 120 and p['fragment'] == 'page='+str(p['page'])
        assert p['destination'] not in printed_keys
        printed_keys.add(p['destination'])
        for s in q['supports']:
            assert s['native_id'] not in support_ids
            support_ids.add(s['native_id'])
            component = units[s['native_id']]
            assert component['parent_id'] == ident and component['unit_type'] == s['kind']
            assert s['source_content_sha256'] == component['source']['content_sha256']
            assert s['source_xpath'] == component['source']['locator']['xpath']
            observed_edges.add((ident,s['native_id'],'has_'+s['kind']))
            loc = s['printed']
            lo,hi = {'hint':(121,173),'answer':(173,262),'solution':(262,647)}[s['kind']]
            assert lo <= loc['page'] < hi and loc['fragment'] == 'page='+str(loc['page'])
            assert loc['destination'] == p['backlink_destination'] and loc['target_page'] == p['page']
            assert loc['label'] == m.LABELS[s['kind']]+' '+str(q['target_ordinal'])+':'
    assert observed_edges == edges and len(observed_edges) == 2010
    assert sum(q['mapping_kind']=='source-child-translated-in-parent-file' for q in q_by_id.values()) == 30
    assert sum(not any(s['kind']=='hint' for s in q['supports']) for q in q_by_id.values()) == 75


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-zip',type=Path)
    parser.add_argument('--backend-zip',type=Path)
    parser.add_argument('--pdf',type=Path)
    parser.add_argument('--independent-backlinks',type=Path)
    args = parser.parse_args()
    raw = (m.BASE/'clp1-navigation.json').read_bytes()
    data = json.loads(raw)
    native = json.loads((m.BASE/'input/native-exercises.json').read_bytes())
    validate_structure(data,native)
    negatives = []
    def reject(name, change):
        bad = copy.deepcopy(data)
        change(bad)
        try:
            validate_structure(bad,native)
        except (AssertionError,KeyError,ValueError):
            negatives.append(name)
        else:
            raise AssertionError('Accepted corrupt mapping: '+name)
    reject('duplicate-question',lambda d:d['questions'].append(d['questions'][0]))
    reject('changed-source-identity',lambda d:d['questions'][0].update(source_content_sha256='0'*64))
    reject('wrong-common-id',lambda d:d['questions'][0].update(common_id='B30:wrong'))
    reject('wrong-source-xpath',lambda d:d['questions'][0].update(source_xpath='/wrong'))
    reject('erased-native-state',lambda d:d['questions'][0].update(native_translation_state='invented'))
    reject('wrong-question-page',lambda d:d['questions'][0]['printed'].update(page=500))
    reject('wrong-question-counter',lambda d:d['questions'][0]['printed'].update(destination='GlobalQCounter.9.9.9.9'))
    reject('wrong-question-fragment',lambda d:d['questions'][0]['printed'].update(fragment='page=2'))
    reject('missing-support',lambda d:d['questions'][0]['supports'].pop())
    reject('duplicate-support',lambda d:d['questions'][0]['supports'].append(d['questions'][0]['supports'][0]))
    reject('wrong-support-page',lambda d:d['questions'][0]['supports'][0]['printed'].update(page=1))
    reject('wrong-support-backlink',lambda d:d['questions'][0]['supports'][0]['printed'].update(destination='QCounter.9.9.9.9'))
    reject('wrong-support-number',lambda d:d['questions'][0]['supports'][0]['printed'].update(label='Jawaban 999:'))
    reject('wrong-pdf-edition',lambda d:d['reader'].update(sha256='0'*64))
    for name,text in [('unbalanced',r'\begin{question}x\end{answer}'),('nested',r'\begin{question}\begin{answer}x\end{answer}\end{question}')]:
        try:
            m.environments(text)
        except AssertionError:
            negatives.append(name)
        else:
            raise AssertionError(name)
    assert m.support_label('\ufffd\nPetunjuk 24: \n2 +') == ('hint',24)
    assert m.support_label('Jawaban 12: x') == ('answer',12)
    assert m.support_label('Penyelesaian 9:') == ('solution',9)
    assert m.support_label('Lihat Soal 9.') is None
    try:
        m.support_label('Jawaban 2: Penyelesaian 3:')
    except AssertionError:
        negatives.append('ambiguous-label')
    else:
        raise AssertionError('ambiguous-label')
    literal = r'\begin{question}x\%y%ignored'+ '\n'+r'\end{question}'
    assert m.mask_comments(literal).index('\n') == literal.index('\n')
    assert len(m.environments(literal)) == 1
    independent = None
    if args.independent_backlinks:
        other_raw = args.independent_backlinks.read_bytes()
        other = json.loads(other_raw)
        assert other['pdf_sha256'] == data['reader']['sha256']
        observed = set()
        for row in other['links']:
            label = m.support_label(row['label'])
            if label:
                observed.add((row['destination'],label[0],label[1],row['page'],row['xref'],row['to_page']))
        expected = {(s['printed']['destination'],s['kind'],q['target_ordinal'],s['printed']['page'],s['printed']['annotation_xref'],q['printed']['page'])
                    for q in data['questions'] for s in q['supports']}
        assert len(observed) == len(expected) == 2010 and observed == expected
        independent = {'input':m.identity(other_raw),'matched_supports':2010,
                       'method':'Earlier direct Page.get_links extraction compared with raw annotation dictionary mapping.'}
    replay = []
    if any([args.source_zip,args.backend_zip,args.pdf]):
        assert all([args.source_zip,args.backend_zip,args.pdf])
        with tempfile.TemporaryDirectory(prefix='clp1-navigation-replay-') as tmp:
            for index in range(2):
                dest = Path(tmp)/f'replay-{index}.json'
                subprocess.run([sys.executable,'-B',str(ROOT/'scripts/map-clp1-navigation-v1.py'),
                    '--source-zip',str(args.source_zip.resolve()),'--backend-zip',str(args.backend_zip.resolve()),
                    '--pdf',str(args.pdf.resolve()),'--output',str(dest)],check=True,timeout=180)
                assert dest.read_bytes() == raw, 'Non-deterministic or stale map'
                replay.append(m.identity(dest.read_bytes()))
    result = {'schema':'clp1-navigation-validation/1','state':'pass','mapping':m.identity(raw),
              'counts':data['counts'],'negative_fixtures':negatives,'label_and_comment_fixtures':5,
              'independent_annotation_comparison':independent,'source_pdf_replays':replay,
              'consumer_integrated':False,'public_deployment_claimed':False,'whole_program_complete':False}
    if len(replay) == 2 and independent:
        (m.BASE/'clp1-navigation-validation.json').write_bytes(m.encode(result))
        lock = {'schema':'clp1-navigation-lock/1','mapping':m.identity(raw),
                'validation':m.identity(m.encode(result)),'native_sha256':m.EXPECTED['native']}
        (m.BASE/'input/clp1-navigation-lock.json').write_bytes(m.encode(lock))
    # An offline structural check must not replace the stronger full-source
    # replay receipt or leave its lock pointing to overwritten evidence.
    print(json.dumps(result))


if __name__ == '__main__':
    main()
