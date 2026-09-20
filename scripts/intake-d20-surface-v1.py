"""Freeze existing D20 metadata and verify every consumed public HTML route.

No book bodies are copied and the native tree is never modified. Normal builds
use the frozen inputs offline; this deliberately bounded intake is separate.
"""
import argparse
import collections
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'backend/course-capsule-v1/adapters/d20-surface-v1/input'
ORIGIN = 'https://kokunoyumeto.github.io/functional-analysis-erdman-id/'
TABLES = ['units', 'semantic_units', 'relations', 'exercise_support', 'o001_mastery',
          'o001_status', 'bridge_units', 'companion_relations', 'html_routes',
          'companion_html_routes', 'concepts', 'concept_relations', 'rights',
          'companion_components']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.counts, self.numbers = collections.Counter(), {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.counts[a['id']] += 1
            if 'data-number' in a:
                self.numbers[a['id']] = a['data-number']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--native-root', type=Path, required=True)
    args = p.parse_args()
    native = args.native_root.resolve()
    authority = ROOT / 'backend/v2.3/extensions/d20-functional-analysis-v0.1.0/INPUT_AUTHORITIES.json'
    authority_bytes = authority.read_bytes()
    locked = {r['path']: r for r in json.loads(authority_bytes)['authorities'] if r['path_base'] == 'owner_package_root'}
    tables, inputs = {}, []
    for name in TABLES:
        rel = 'backend/' + name + '.jsonl'
        data = (native / rel).read_bytes()
        expected = locked.get(rel)
        if expected:
            assert (len(data), sha(data)) == (expected['bytes'], expected['sha256']), f'Admitted input drift: {rel}'
        rows = [json.loads(line) for line in data.decode('utf-8-sig').splitlines()]
        assert len({r['id'] for r in rows}) == len(rows), f'Duplicate IDs: {rel}'
        tables[name] = rows
        target = DEST / (name + '.jsonl')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        inputs.append({'path': target.relative_to(ROOT).as_posix(), 'native_path': rel,
                       'bytes': len(data), 'sha256': sha(data), 'records': len(rows),
                       'admitted_input_identity_matched': bool(expected)})

    candidates = []
    for name, prefix in [('html_routes', 'output/html/'), ('companion_html_routes', 'output/html-companion/')]:
        for row in tables[name]:
            part = urlsplit(row['href'])
            assert not part.scheme and not part.netloc and not part.query
            assert '..' not in PurePosixPath(part.path).parts and not part.path.startswith('/')
            assert part.path == row['output_path'] and part.path.endswith('.html')
            candidates.append({'native_route_id': row['id'], 'target_id': row.get('target_stable_id', row['id']),
                               'native_table': name, 'path': prefix + part.path, 'anchor': part.fragment})
    pages, parsers = [], {}
    for path in sorted({r['path'] for r in candidates}):
        local = (native / path).read_bytes()
        assert len(local) < 5_000_000, 'Unexpected per-page boundary'
        with urlopen(ORIGIN + path, timeout=40) as response:
            public = response.read(len(local) + 1)
            assert response.status == 200
        assert local == public, f'Public/local HTML mismatch: {path}'
        parser = Anchors()
        parser.feed(public.decode('utf-8'))
        parsers[path] = parser
        pages.append({'path': path, 'url': ORIGIN + path, 'bytes': len(public), 'sha256': sha(public),
                      'public_equals_native_bytes': True})
        print(json.dumps({'checked_public_html': len(pages), 'path': path}), flush=True)
    for row in candidates:
        parser = parsers[row['path']]
        row['occurrences'] = parser.counts[row['anchor']] if row['anchor'] else None
        row['number'] = parser.numbers.get(row['anchor'])
        row['url'] = ORIGIN + row['path'] + ('#' + row['anchor'] if row['anchor'] else '')
    witness = {'schema': 'd20-public-reader-witness/1', 'observed_date': '2026-09-21',
               'anonymous': True, 'origin': ORIGIN, 'pages': pages, 'routes': candidates,
               'scope': 'Every registered source and companion HTML route; exact local/public byte comparison, not a new mathematical proof review.'}
    dump(DEST / 'reader-witness.json', witness)
    data = (DEST / 'reader-witness.json').read_bytes()
    inputs.append({'path': (DEST / 'reader-witness.json').relative_to(ROOT).as_posix(), 'bytes': len(data), 'sha256': sha(data)})
    lock = {'schema': 'd20-consumer-input-lock/1', 'course_id': 'D20', 'content_locale': 'id-ID',
            'authority': {'path': authority.relative_to(ROOT).as_posix(), 'bytes': len(authority_bytes), 'sha256': sha(authority_bytes)},
            'inputs': inputs, 'body_content_copied': False, 'native_files_modified': False}
    dump(DEST / 'source-lock.json', lock)
    print(json.dumps({'state': 'pass', 'tables': len(TABLES), 'public_html': len(pages), 'routes': len(candidates)}))


if __name__ == '__main__':
    main()
