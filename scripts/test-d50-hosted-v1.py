"""Independent content, source, route and non-inflation checks for D50 delivery."""
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

from central_surface_navigation_overlay_v1 import strip_central_surface_overlay

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d50-surface-v1'
OUT = ROOT / 'docs/backend/d50'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def fact(b):
    return {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.links = [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.append(a['id'])
        for key in ['href', 'src']:
            if a.get(key):
                self.links.append(a[key])


def validate(mapping, native, delivery, payloads):
    assert mapping['content_locale'] == 'id-ID'
    assert mapping['hosted_reader_url'] == delivery['reader_url']
    assert mapping['counts'] == native['counts']
    for key in ['semantic_exam_groups', 'placeholder_slots', 'concepts', 'concept_relations',
                'prerequisites', 'occurrence_relations', 'support_relations', 'rights', 'source_witness']:
        assert mapping[key] == native[key], key
    assert len(mapping['units']) == len(native['units'])
    for a, b in zip(mapping['units'], native['units']):
        a = deepcopy(a)
        assert a['route'].pop('hosted_url') == delivery['reader_url'] + '#' + b['route']['anchor']
        assert a == b, b['id']
    for member in delivery['reader_members']:
        data = payloads['reader/' + member['path']]
        if member['path'].endswith('.html'):
            data = strip_central_surface_overlay(data, member['path'])
        assert fact(data) == {k: member[k] for k in ['bytes', 'sha256']}, member['path']
    assert fact(payloads[delivery['direct_tex']['path']]) == {k: delivery['direct_tex'][k] for k in ['bytes', 'sha256']}
    reader = Links(payloads['reader/index.html'].decode('utf-8'))
    assert len(reader.ids) == len(set(reader.ids))
    assert all(u['route']['anchor'] in reader.ids for u in mapping['units'])
    for page in ['index.html', 'index.en.html', 'teacher.html', 'teacher.en.html']:
        t = payloads[page].decode('utf-8')
        p = Links(t)
        assert delivery['pdf']['url'] in p.links
        assert delivery['complete_source_archive']['url'] in p.links
        assert delivery['direct_tex']['path'] in p.links
        assert p.links.index(delivery['pdf']['url']) < p.links.index(delivery['direct_tex']['path']) < p.links.index(delivery['complete_source_archive']['url'])
        assert 'reader/index.html' in p.links
        assert 'source package' in t if '.en.' in page else 'ZIP sumber' in t
        assert "style-src 'self' 'unsafe-inline'" in t
    # Check media and internal reader destinations without executing the page.
    for link in reader.links:
        u = urlsplit(link)
        if u.scheme or u.netloc:
            continue
        path = 'reader/' + unquote(u.path) if u.path else 'reader/index.html'
        # Global programme navigation may legitimately leave this subtree.
        if '..' in Path(path).parts:
            continue
        assert path in payloads, link
        if u.fragment and path == 'reader/index.html':
            assert unquote(u.fragment) in reader.ids, link


def main():
    mapping = load(OUT / 'learning-map.json')
    native = load(BASE / 'portable/learning-map.json')
    delivery = load(BASE / 'delivery/reader-delivery.json')
    paths = [p for p in OUT.rglob('*') if p.is_file()]
    payloads = {p.relative_to(OUT).as_posix(): p.read_bytes() for p in paths}
    validate(mapping, native, delivery, payloads)
    negatives = []
    def reject(name, alter):
        m, p = deepcopy(mapping), payloads.copy()
        alter(m, p)
        try:
            validate(m, native, delivery, p)
        except (AssertionError, KeyError):
            negatives.append(name)
            return
        raise AssertionError('Accepted mutation: ' + name)
    reject('false_english_reading', lambda m,p: m.update(content_locale='en'))
    reject('wrong_hosted_route', lambda m,p: m['units'][0]['route'].update(hosted_url='https://example.com/'))
    reject('omitted_native_unit', lambda m,p: m['units'].pop())
    reject('invented_solution_count', lambda m,p: m['counts'].update(worksheet_source_solutions=576))
    reject('changed_reader_body', lambda m,p: p.update({'reader/index.html':p['reader/index.html']+b'changed'}))
    reject('missing_editable_tex', lambda m,p: p.pop(delivery['direct_tex']['path']))
    reject('missing_source_archive_link', lambda m,p: p.update({'index.html':p['index.html'].replace(delivery['complete_source_archive']['url'].encode(),b'https://example.com/')}))
    report = {'schema':'d50-hosted-independent-tests/1','state':'pass','native_units_preserved':len(mapping['units']),
        'reader_files':len(delivery['reader_members']),'native_anchor_routes':len(mapping['units']),
        'negative_fixtures':negatives,'content_locale':'id-ID','interface_locales':['id','en'],
        'body_and_source_identity_verified':True,'new_translation':False,'tex_compilation_replayed':False}
    (BASE / 'delivery/tests.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
