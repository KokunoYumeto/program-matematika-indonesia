#!/usr/bin/env python3
"""Project the admitted A10 reader into a portable, source-bound web reader."""
from __future__ import annotations

import argparse
import collections
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OWNER = ROOT.parent.parent / '01a01f41-26f0-7e63-952c-de86c2f9155e' / 'elementary_algebra_2e_id'
ARCHIVE = ROOT / 'tmp/a10-html-source-v1.0.3/elementary-algebra-2e-id-ID-1.0.3-source.zip'
ARCHIVE_SHA = '77a6ecfa22c4a5b58b0b7f72e5ec9db11ac4656bc7fc9c4944a4a7916a2472f3'
HTML_MEMBER = 'reader/elementary-algebra-2e-bahasa-indonesia-EA2-C0082-reader.html'
HTML_SHA = 'ba073b12406138f76e4282471e79cfa9111a23bfa92004be75f96100696d0d11'
DEST = ROOT / 'docs/id-ID/courses/A10/reader'
MANIFEST = DEST.parent / 'A10_READER_MIRROR_MANIFEST_V1.json'
HOSTING_CSS = '''
/* Central screen presentation; print rules and mathematical content retained. */
@media screen {
  :root { font-size: 16px; }
  .front { min-height: 0; padding-block: 2rem; }
  .cover { padding-block: 2rem; }
  .module-header { min-height: 0; padding-block: 1.5rem; }
  .module-id, .semantic-source-ids, .coverage-gap-ids { font-size: .8rem; }
  .authors, .adaptation, .edition-date, .media-transcription,
  .semantic-media-table, table, figcaption, .cnx-label, .solution-kicker,
  .source-raster-witness { font-size: .9rem; }
  .contents { scroll-margin-top: 1rem; }
  img { max-inline-size: 100%; }
}
'''


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fact(data: bytes) -> dict:
    return {'bytes': len(data), 'sha256': sha(data)}


class Document(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.images = []
        self.links = []
        self.modules = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'img':
            self.images.append(a)
        if tag == 'a':
            self.links.append(a.get('href', ''))
        if tag == 'article' and 'reader-module' in a.get('class', '').split():
            self.modules.append(a.get('id'))
        if tag in ('script', 'iframe', 'object'):
            raise ValueError('Unexpected active dependency in frozen reader: ' + tag)


def put(path: Path, data: bytes, check: bool):
    if path.is_file() and path.read_bytes() == data:
        return
    if check:
        raise ValueError('Missing or changed mirror file: ' + path.relative_to(ROOT).as_posix())
    if path.exists():
        raise ValueError('Refusing to replace an unverified existing file: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def run(check: bool):
    archive_bytes = ARCHIVE.read_bytes()
    assert len(archive_bytes) == 7264274 and sha(archive_bytes) == ARCHIVE_SHA
    with zipfile.ZipFile(ARCHIVE) as z:
        source_bytes = z.read(HTML_MEMBER)
        assert sha(source_bytes) == HTML_SHA
        source = source_bytes.decode('utf-8')
        doc = Document(source)
        assert len(doc.modules) == 82 and len(doc.ids) == 55690
        assert len(doc.ids) == len(set(doc.ids))
        assert len(doc.images) == 4024
        build = json.loads(z.read('documentation/reader-build-manifest.json'))
        assert build['coverage']['complete_book'] is True
        assets = {}
        for a in build['render']['assets']:
            key = a['authority_or_overlay_path']
            identity = {k: a[k] for k in ('bytes', 'sha256')}
            if key in assets:
                assert assets[key] == identity
            assets[key] = identity
        refs = {}
        payloads = {}
        asset_rows = []
        for image in doc.images:
            uri = image['src']
            assert uri.startswith('file:///') and image.get('alt', '').strip()
            native = Path(unquote(urlsplit(uri).path.lstrip('/'))).resolve()
            assert native.is_relative_to(OWNER.resolve())
            rel = native.relative_to(OWNER.resolve()).as_posix()
            expected = assets[rel]
            if uri not in refs:
                data = native.read_bytes()
                assert fact(data) == expected, 'Asset changed: ' + rel
                target = 'media/' + expected['sha256'] + native.suffix.lower()
                if target in payloads:
                    assert payloads[target] == data
                payloads[target] = data
                refs[uri] = target
                asset_rows.append({'owner_relative_path': rel, 'hosted_path': target, **expected})
        projected = re.sub(r'src="(file:[^"]+)"',
                           lambda m: 'src="' + refs[html.unescape(m[1])] + '"', source)
        projected, font_faces = re.subn(r'@font-face\s*\{[^}]*\}\s*', '', projected)
        assert font_faces == 4
        assert projected.count('CHECKPOINT PARSIAL EA2-C0082-v1.0.3-final') == 1
        projected = projected.replace('CHECKPOINT PARSIAL EA2-C0082-v1.0.3-final', 'EDISI LENGKAP — 82 MODUL')
        projected = projected.replace('</style>', HOSTING_CSS + '</style>', 1)
        # All intrinsic mathematics, IDs, exercises, alt text, and source links remain.
        math_re = r'<math\b[^>]*?/>|<math\b[^>]*>[\s\S]*?</math>'
        source_math = re.findall(math_re, source)
        target_math = re.findall(math_re, projected)
        assert source_math == target_math and len(target_math) == 20979
        target_doc = Document(projected)
        assert target_doc.ids == doc.ids and target_doc.modules == doc.modules
        assert target_doc.links == doc.links
        assert [a['alt'] for a in target_doc.images] == [a['alt'] for a in doc.images]
        assert {a['src'] for a in target_doc.images} == set(payloads)
        assert not re.search(r'file:|[A-Za-z]:[/\\]Users[/\\]', projected)
        assert not {unquote(x[1:]) for x in target_doc.links if x.startswith('#')} - set(target_doc.ids)
        payloads['index.html'] = projected.encode('utf-8')
        for name in ('LICENSE.txt', 'NOTICE.txt'):
            payloads[name] = z.read(name)
        for name in z.namelist():
            if name.startswith('documentation/rights/') and not name.endswith('/'):
                payloads['rights/' + name.rsplit('/', 1)[-1]] = z.read(name)
        for name, data in sorted(payloads.items()):
            path = DEST / name
            if name == 'index.html' and path.is_file():
                # The shared navigation stage adds a separately bound removable shell.
                from central_surface_navigation_overlay_v1 import strip_central_surface_overlay
                current = strip_central_surface_overlay(path.read_bytes(), path.relative_to(ROOT).as_posix())
                if current == data:
                    continue
            put(path, data, check)
        result = {
            'schema': 'a10-portable-reader-mirror/1', 'course_id': 'A10', 'locale': 'id-ID',
            'status': 'validated_local', 'public_readback': 'pending',
            'source_archive': {'url': 'https://zenodo.org/records/22236314/files/' + ARCHIVE.name,
                               **fact(archive_bytes)},
            'source_reader': {'member': HTML_MEMBER, **fact(source_bytes)},
            'source_build_manifest': fact(z.read('documentation/reader-build-manifest.json')),
            'source_repository': 'https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id',
            'original_source': 'https://openstax.org/details/books/elementary-algebra-2e',
            'rights': 'CC-BY-NC-SA-4.0; component credits and notices retained; no endorsement implied.',
            'modifications': ['Machine-local asset URLs replaced with hash-addressed local files.',
                              'Machine-local font declarations removed; CSS font fallback retained.',
                              'Screen typography enlarged; print stylesheet retained.',
                              'Stale partial cover label corrected using admitted 82/82 coverage.',
                              'Shared central navigation is applied separately and reversibly.'],
            'reader_entrypoint': 'docs/id-ID/courses/A10/reader/index.html',
            'reader_body': fact(payloads['index.html']),
            'validation': {'modules': 82, 'mathml_regions_preserved': len(target_math),
                           'stable_ids_preserved': len(doc.ids), 'image_uses': len(doc.images),
                           'image_alts_preserved': True, 'unique_asset_references': len(refs),
                           'unique_asset_payloads': len(asset_rows), 'local_asset_hashes': 'pass',
                           'internal_links': 624, 'missing_internal_links': 0,
                           'math_requires_network': False, 'external_runtime_dependencies': 0},
            'files': [{'path': name, **fact(data)} for name, data in sorted(payloads.items())],
            'asset_bindings': sorted(asset_rows, key=lambda row: row['owner_relative_path']),
            'replay': 'python -B scripts/stage_a10_public_html_v1.py --check',
        }
        rendered = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        put(MANIFEST, rendered, check)
        print(json.dumps({'status': 'pass', 'manifest': fact(rendered),
                          'files': len(payloads), 'total_bytes': sum(map(len, payloads.values())),
                          'reader': fact(payloads['index.html'])}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    run(parser.parse_args().check)
