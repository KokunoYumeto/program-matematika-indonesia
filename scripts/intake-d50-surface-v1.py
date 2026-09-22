"""Bind D50 native identities to the already released portable reader.

This does not modify the producer, enable Pages, invent hosted URLs, or copy
book bodies into the common metadata layer. Downloads are bounded and checked
against the public release and the independently admitted native authorities.
"""
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path, PurePosixPath
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d50-surface-v1'
RELEASE = 'https://github.com/KokunoYumeto/brenner-differentialgeometrie-id/releases/download/v1.0.1/'
ARCHIVE = 'geometri-diferensial-manifold-mulus-edisi-lengkap-html-20260829.zip'
ADMISSION = 'backend/v2.3/admissions/d50-smooth-manifolds-v0.1.0/manifest.json'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def get(url, maximum):
    with urlopen(url, timeout=40) as response:
        assert response.status == 200
        b = response.read(maximum + 1)
    assert len(b) <= maximum, 'Download boundary exceeded'
    return b


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.counts, self.attrs = Counter(), {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.counts[a['id']] += 1
            self.attrs[a['id']] = {'tag': tag, **a}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-root', required=True, type=Path)
    args = parser.parse_args()
    native = args.native_root.resolve()
    authority_bytes = (ROOT / ADMISSION).read_bytes()
    admitted = {x['path']: x for x in json.loads(authority_bytes)['authorities'] if x['path_base'] == 'owner_package_root'}
    paths = {'records.jsonl': 'backend/records.jsonl',
             'native-manifest.json': 'backend/MANIFEST.json',
             'reader-manifest.json': 'output/html/complete/manifest.json'}
    frozen, facts = {}, []
    for output, path in paths.items():
        b = (native / path).read_bytes()
        expected = admitted[path]
        assert (len(b), sha(b)) == (expected['bytes'], expected['sha256']), f'Admitted input drift: {path}'
        frozen[output] = b
        facts.append({'path': (BASE / 'input' / output).relative_to(ROOT).as_posix(),
                      'native_path': path, 'bytes': len(b), 'sha256': sha(b)})
    records = [json.loads(line) for line in frozen['records.jsonl'].decode('utf-8').splitlines()]
    assert len(records) == len({r['id'] for r in records}) == 6912
    manifest = json.loads(frozen['reader-manifest.json'])
    release_bytes = get(RELEASE + 'FILE_MANIFEST.json', 50_000)
    release = json.loads(release_bytes)
    expected_zip = next(x for x in release['files'] if x['path'] == ARCHIVE)
    b = get(RELEASE + ARCHIVE, 10_000_000)
    assert (len(b), sha(b)) == (expected_zip['bytes'], expected_zip['sha256'])
    z = zipfile.ZipFile(io.BytesIO(b))
    names = z.namelist()
    assert len(names) == len(set(names)) == 44
    assert not any(PurePosixPath(n).is_absolute() or '..' in PurePosixPath(n).parts or '\\' in n for n in names)
    assert z.testzip() is None
    expected_files = {x['path']: x for x in manifest['files']}
    assert set(names) == set(expected_files) | {'manifest.json'}
    members = []
    for name in sorted(names):
        data = z.read(name)
        if name == 'manifest.json':
            assert data == frozen['reader-manifest.json']
        else:
            fact = expected_files[name]
            assert (len(data), sha(data)) == (fact['bytes'], fact['sha256']), name
        assert data == (native / 'output/html/complete' / name).read_bytes(), f'Public/local difference: {name}'
        members.append({'path': name, 'bytes': len(data), 'sha256': sha(data)})
    html = z.read('index.html')
    expected = admitted['output/html/complete/index.html']
    assert (len(html), sha(html)) == (expected['bytes'], expected['sha256'])
    anchors = Anchors()
    anchors.feed(html.decode('utf-8'))
    assert all(n == 1 for n in anchors.counts.values()), 'Duplicate rendered anchors'
    # The producer renderer defines the nonidentity exam anchor convention.
    # Preserve its exact identity as evidence; never execute or modify it here.
    rules = []
    for path in ['scripts/export_html_complete.py', 'scripts/verify_html_complete.py']:
        data = (native / path).read_bytes()
        rules.append({'native_path': path, 'bytes': len(data), 'sha256': sha(data)})
    witness = {'schema': 'd50-portable-reader-witness/1', 'content_locale': 'id-ID',
               'release_url': RELEASE, 'archive': {'url': RELEASE + ARCHIVE, **expected_zip},
               'hosted_reader_url': None, 'delivery': 'verified_public_portable_archive',
               'reader': {'path': 'index.html', 'bytes': len(html), 'sha256': sha(html)},
               'members': members, 'anchors': anchors.attrs, 'anchor_counts': anchors.counts,
               'renderer_rules': rules, 'source_model_identification': manifest['model_identification'],
               'verification': {'anonymous_download': True, 'crc': 'pass', 'all_public_members_match_native': True,
                                'admitted_reader_identity': True, 'checked_on': '2026-09-22'}}
    input_dir = BASE / 'input'
    input_dir.mkdir(parents=True, exist_ok=True)
    for name, data in frozen.items():
        (input_dir / name).write_bytes(data)
    dump(input_dir / 'reader-witness.json', witness)
    witness_bytes = (input_dir / 'reader-witness.json').read_bytes()
    dump(input_dir / 'source-lock.json', {'schema': 'd50-consumer-input-lock/1', 'content_locale': 'id-ID',
         'inputs': facts, 'authority': {'path': ADMISSION, 'bytes': len(authority_bytes), 'sha256': sha(authority_bytes)},
         'witness': {'path': (input_dir / 'reader-witness.json').relative_to(ROOT).as_posix(),
                     'bytes': len(witness_bytes), 'sha256': sha(witness_bytes)},
         'book_bodies_copied': False, 'native_files_modified': False})
    print(json.dumps({'state': 'pass', 'native_records': len(records), 'public_archive_members': len(members),
                      'rendered_anchors': len(anchors.counts), 'hosted_reader_claimed': False}))


if __name__ == '__main__':
    main()
