"""Validate and register existing sealed B40 pages without rewriting their bodies."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'docs/en/readers/hefferon-linear-algebra/'
ORIGIN = 'https://kokunoyumeto.github.io/program-matematika-indonesia/'
MANIFEST_SHA = 'a5c1a28b149eac95e357fcb34231742ff4f801c1f97ce6da560ead979a3313b6'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs, self.locale = [], None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'a' and 'href' in values:
            self.hrefs.append(values['href'])
        if tag == 'html':
            self.locale = values.get('lang')


def validate(root=ROOT):
    raw_manifest = (root / PREFIX / 'READER_MANIFEST.json').read_bytes()
    assert hashlib.sha256(raw_manifest).hexdigest() == MANIFEST_SHA, 'Native manifest changed'
    manifest = json.loads(raw_manifest)
    assert manifest['schema'] == 'b40-expanded-reading-edition/1'
    assert manifest['language'] == 'en' and len(manifest['sections']) == 29
    assert manifest['sections'][-1]['section'] == 'cramer'
    rows = [r for r in manifest['public_files'] if r['path'].endswith('.html')]
    assert len(rows) == len({r['path'] for r in rows}) == 30
    result = []
    for row in rows:
        name = row['path']
        part = PurePosixPath(name)
        assert not part.is_absolute() and '..' not in part.parts and ':' not in name and '\\' not in name
        path = root / PREFIX / name
        raw = path.read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], 'Sealed B40 reader changed'
        parser = Links()
        parser.feed(raw.decode('utf-8'))
        assert parser.locale == 'en'
        public = ORIGIN + PREFIX.removeprefix('docs/') + name
        links = {urljoin(public, href) for href in parser.hrefs}
        assert ORIGIN + 'en/programme/' in links, 'Programme return missing'
        assert 'https://hefferon.net/linearalgebra/' in links, 'Author link missing'
        if name != 'index.html':
            assert ORIGIN + PREFIX.removeprefix('docs/') + 'index.html' in links, 'Contents return missing'
        for href in parser.hrefs:
            value = urlsplit(href)
            if not value.scheme and not value.netloc and value.path:
                local = (path.parent / value.path).resolve()
                assert local.is_relative_to((root / PREFIX).resolve()) and local.is_file(), 'Broken/outside native local link'
        result.append({'document': PREFIX + name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                       'english_programme_return': True, 'original_author_link': True, 'native_body_unchanged': True})
    return {'schema': 'b40-expanded-native-navigation-validation/1', 'state': 'pass', 'files': result,
            'html_documents': 30, 'sections': 29, 'scope': 'Existing partial original-English book through Cramer’s Rule; no new translation or proof admission.'}


if __name__ == '__main__':
    result = validate()
    target = ROOT / 'backend/authority/central-reader-navigation-v1.json'
    before = target.read_bytes()
    nav = json.loads(before)
    names = {r['document'] for r in result['files']}
    nav['generic_surfaces'] = [r for r in nav['generic_surfaces'] if r['document'] not in names] + [
        {'document': r['document'], 'state': 'sealed-b40-expanded-english', 'navigation_required': False,
         'navigation_provider': 'b40-expanded-native-v1', 'locale': 'en'} for r in result['files']]
    nav['summary']['generic_html_documents'] = len(nav['generic_surfaces'])
    nav['summary']['classified_html_documents'] = sum(nav['summary'][key] for key in
        ['reader_html_documents', 'gateway_html_documents', 'course_surface_html_documents', 'generic_html_documents'])
    assert target.read_bytes() == before, 'Concurrent navigation edit'
    target.write_text(json.dumps(nav, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'backend/authority/b40-expanded-navigation-validation-v1.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'state': 'pass', 'registered_native_html_pages': 30, 'native_bodies_changed': False}))
