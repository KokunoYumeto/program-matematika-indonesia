"""Admit and verify the sealed, four-file additive Library directory.

This is an artifact copier, not a book converter. The source/QA ZIP is preserved
outside docs/library; every deployed byte remains identical to the handoff.
"""
import argparse
import hashlib
import io
import json
import subprocess
import tempfile
import zipfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'backend/authority/library-handoff-v1.json'
PUBLIC = ROOT / 'docs/library'
FILES = {'index.html', 'library.js', 'registry.json', 'styles.css'}
ORIGIN = 'https://kokunoyumeto.github.io/program-matematika-indonesia/'


def fact(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def check_fact(data, expected):
    if fact(data) != {'bytes': expected['bytes'], 'sha256': expected['sha256'].lower()}:
        raise ValueError('Byte/hash identity mismatch: ' + expected.get('path', expected.get('file', 'object')))


def zip_members(data, inventory):
    expected = {row['path']: row for row in inventory}
    if len(expected) != len(inventory):
        raise ValueError('Duplicate inventory entries')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(expected):
            raise ValueError('Archive inventory differs from the sealed allowlist')
        if sum(entry.file_size for entry in archive.infolist()) > 2_000_000:
            raise ValueError('Unexpected Library package size')
        result = {}
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
                raise ValueError('Unsafe archive path')
            result[name] = archive.read(name)  # ZIP CRC is checked by read().
            check_fact(result[name], expected[name])
        return result


class LibraryNavigation(HTMLParser):
    def __init__(self):
        super().__init__()
        self.landmarks = []
        self.active = None
        self.anchor = None
        self.ids = []
        self.links = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag == 'nav' and 'data-library-navigation' in attrs:
            self.active = {'placement': attrs['data-library-navigation'], 'label': attrs.get('aria-label'), 'links': []}
            self.landmarks.append(self.active)
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
            if self.active is not None:
                self.anchor = {'href': attrs.get('href', ''), 'text': ''}
                self.active['links'].append(self.anchor)

    def handle_data(self, data):
        if self.anchor is not None:
            self.anchor['text'] += data

    def handle_endtag(self, tag):
        if tag == 'a':
            self.anchor = None
        if tag == 'nav':
            self.active = None


def validate_html(html, registry):
    parser = LibraryNavigation()
    parser.feed(html)
    if sorted(row['placement'] for row in parser.landmarks) != ['bottom', 'top']:
        raise ValueError('Need exactly one supplied top and bottom program landmark')
    for row in parser.landmarks:
        if not row['label']:
            raise ValueError('Missing navigation landmark label')
        for locale in ('en', 'id'):
            links = [link for link in row['links'] if link['href'] == ORIGIN + locale + '/']
            if len(links) != 1 or not links[0]['text'].strip():
                raise ValueError('Missing exact visible ' + locale + ' program return')
    if len(parser.ids) != len(set(parser.ids)):
        raise ValueError('Duplicate Library HTML IDs')
    for href in parser.links:
        if href.startswith('#') and href[1:] not in parser.ids:
            raise ValueError('Broken local Library anchor')
    if parser.links.count('./index.html') != 3 or './' in parser.links:
        raise ValueError('Library home must work both locally and under a subdirectory')
    if 'href="./styles.css"' not in html or 'src="./library.js"' not in html:
        raise ValueError('Missing portable Library assets')
    if len(registry['items']) != 13 or len(registry['collections']) != 5:
        raise ValueError('Unexpected sealed Library scope')
    for item in registry['items']:
        if item['id'] not in parser.ids:
            raise ValueError('Catalogue entry missing from static HTML')
        for edition in item['editions']:
            if edition.get('url') and edition['url'] not in parser.links:
                raise ValueError('Edition link missing without JavaScript')
    if 'data-central-surface-navigation=' in html:
        raise ValueError('Do not inject a second shell into the sealed Library')


def validate(root=ROOT):
    manifest = json.loads((root / MANIFEST.relative_to(ROOT)).read_text(encoding='utf-8'))
    public = root / 'docs/library'
    actual_paths = {path.relative_to(public).as_posix() for path in public.rglob('*') if path.is_file()}
    if actual_paths != FILES or {row['path'] for row in manifest['deploy_only']} != FILES:
        raise ValueError('Library public directory must contain exactly the four approved assets')
    for row in manifest['deploy_only']:
        check_fact((public / row['path']).read_bytes(), row)
    source = (root / manifest['preserved_source_archive']['path']).read_bytes()
    check_fact(source, manifest['preserved_source_archive'])
    source_members = zip_members(source, manifest['source_inventory'])
    for name in FILES:
        if source_members[name] != (public / name).read_bytes():
            raise ValueError('Source archive/deployment mismatch')
    html = (public / 'index.html').read_text(encoding='utf-8')
    registry = json.loads((public / 'registry.json').read_text(encoding='utf-8'))
    validate_html(html, registry)
    return manifest


def stage(receipt_path):
    raw_receipt = receipt_path.read_bytes()
    receipt = json.loads(raw_receipt)
    if receipt.get('revision') != 'R2' or {row['path'] for row in receipt['deploy_only']} != FILES:
        raise ValueError('Expected the reviewed R2 four-file handoff')
    packages = receipt['packages']
    deploy_record = next(row for row in packages if '-deploy-' in row['file'])
    source_record = next(row for row in packages if '-source-and-qa-' in row['file'])
    deploy = (receipt_path.parent / deploy_record['file']).read_bytes()
    source = (receipt_path.parent / source_record['file']).read_bytes()
    check_fact(deploy, deploy_record)
    check_fact(source, source_record)
    payload = zip_members(deploy, receipt['deploy_only'])
    source_members = zip_members(source, receipt['source_inventory'])
    if any(payload[name] != source_members[name] for name in FILES):
        raise ValueError('Source and deployment ZIPs disagree')
    validate_html(payload['index.html'].decode('utf-8'), json.loads(payload['registry.json']))
    # Independently replay the producer's deterministic generator and static tests.
    with tempfile.TemporaryDirectory(prefix='math-library-r2-') as tmp:
        for name, data in source_members.items():
            target = Path(tmp) / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        subprocess.run(['node', 'scripts/validate.mjs'], cwd=tmp, check=True)
    source_path = 'backend/library-portal/' + source_record['file']
    manifest = {'schema': 'central-library-handoff/1', 'revision': 'R2',
                'public_url': receipt['intended_additive_route'],
                'handoff_receipt': fact(raw_receipt), 'deploy_archive': deploy_record,
                'preserved_source_archive': {'path': source_path, **fact(source)},
                'deploy_only': receipt['deploy_only'], 'source_inventory': receipt['source_inventory'],
                'navigation': 'native top/bottom English and Indonesian program returns; no central overlay',
                'scope': 'Additive discovery directory; not a course canon or completion claim.'}
    writes = {PUBLIC / name: data for name, data in payload.items()}
    writes[ROOT / source_path] = source
    writes[MANIFEST] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    for path, data in writes.items():
        if path.exists() and path.read_bytes() != data:
            raise ValueError('Refusing to overwrite a different existing artifact: ' + path.relative_to(ROOT).as_posix())
    for path, data in writes.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    validate()


def self_test():
    html = (PUBLIC / 'index.html').read_text(encoding='utf-8')
    registry = json.loads((PUBLIC / 'registry.json').read_text(encoding='utf-8'))
    mutations = [html.replace('data-library-navigation="bottom"', 'data-library-navigation="top"'),
                 html.replace(ORIGIN + 'en/', ORIGIN + 'missing/'),
                 html.replace('href="./index.html"', 'href="./"'),
                 html.replace('src="./library.js"', 'src="missing.js"')]
    for mutation in mutations:
        try:
            validate_html(mutation, registry)
        except ValueError:
            continue
        raise ValueError('Negative navigation fixture unexpectedly passed')
    print('PASS: four malformed navigation/portability fixtures rejected')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', type=Path, help='Exact sealed HANDOFF_RECEIPT.json')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.stage:
        stage(args.stage.resolve())
    validate()
    if args.self_test:
        self_test()
    print('PASS: exact four-file Library, source/QA archive, static catalogue and bilingual return navigation')
