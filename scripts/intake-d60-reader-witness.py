"""Freeze exact native IDs/HTML anchors, without copying book bodies.

Run once against the pinned native checkout. Normal surface replay uses the
small committed witness and the already admitted v2.3 tables, without network.
"""
import argparse
import hashlib
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d60-surface-v1'
TABLES = 'backend/v2.3/extensions/d60-algebraic-topology-v0.1.0/tables'


def identity(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = Counter()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == 'id':
                self.ids[value] += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-root', type=Path, required=True)
    parser.add_argument('--verify-public', action='store_true')
    args = parser.parse_args()
    authority_path = 'backend/v2.3/authorities/D60_FINAL_OWNER_AUTHORITY_20260830.json'
    authority_bytes = (ROOT / authority_path).read_bytes()
    authority = json.loads(authority_bytes)
    native = args.native_root.resolve()
    spec = authority['public_owner']['learner_html']
    slug = spec['url'].rstrip('/').rsplit('/', 1)[1]
    html = (native / 'output/html' / slug / 'index.html').read_bytes()
    local_html_identity = identity(html)
    # The public navigation wrapper has changed since the old authority.
    # Admit current bytes only after comparing the complete course body.
    assert args.verify_public, 'Freezing a new witness requires public readback'
    with urlopen(spec['url'], timeout=60) as response:
        public = response.read(20_000_001)
        assert response.status == 200
    body_marker = b'<header id="title-block-header">'
    assert html.count(body_marker) == public.count(body_marker) == 1
    normalized_body = lambda b: b.split(body_marker, 1)[1].replace(b'\r\n', b'\n')
    assert normalized_body(html) == normalized_body(public), 'Public course body changed'
    html = public
    raw = (native / 'backend/units.jsonl').read_bytes()
    fact = next(x for x in authority['owner_native']['table_facts'] if x['path'] == 'backend/units.jsonl')
    assert identity(raw) == {k: fact[k] for k in ('bytes', 'sha256')}, 'Native units changed'
    units = [json.loads(x) for x in raw.decode('utf-8').splitlines() if x]
    by_id = {u['id']: u for u in units}
    assert len(by_id) == len(units), 'Duplicate native ID'
    anchors = Anchors()
    anchors.feed(html.decode('utf-8'))
    inputs = [{'path': authority_path, **identity(authority_bytes)}]
    for name in ('units', 'relations'):
        path = f'{TABLES}/{name}.jsonl'
        inputs.append({'path': path, **identity((ROOT / path).read_bytes())})
    projected = [json.loads(x) for x in (ROOT / TABLES / 'units.jsonl').read_text(encoding='utf-8').splitlines()]
    routes = []
    for row in projected:
        p = row['payload']
        u = by_id[p['native_unit_id']]
        assert p['target_locator'] == u['target_locator'], u['id']
        assert p['native_unit_kind'] == u['unit_kind'], u['id']
        assert p['title'] == u['display_title'], u['id']
        anchor = u.get('source_local_id')
        routes.append({'id': u['id'], 'anchor': anchor, 'occurrences': anchors.ids[anchor]})
    witness = {
        'schema': 'd60-reader-witness/1',
        'reader': {'url': spec['url'], **identity(html), 'language': 'id-ID'},
        'historical_reader': {k: spec[k] for k in ('bytes', 'sha256')},
        'local_reader': local_html_identity,
        'public_body_matches_local_after_crlf_normalization': True,
        'public_change_boundary': 'Navigation prefix plus line endings; the full course body matches after CRLF-to-LF normalization only.',
        'native_units': {'path': fact['path'], **identity(raw)},
        'inputs': inputs,
        'anchor_count': len(anchors.ids),
        'duplicate_anchor_count': sum(n > 1 for n in anchors.ids.values()),
        'unit_routes': sorted(routes, key=lambda x: x['id']),
        'policy': 'Exact source_local_id only; zero or repeated anchors retain course-level fallback. No guessed ID suffix removal.',
    }
    BASE.mkdir(parents=True, exist_ok=True)
    (BASE / 'reader-witness.json').write_text(json.dumps(witness, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'state': 'pass', 'units': len(routes), 'exact_routes': sum(r['occurrences'] == 1 for r in routes), 'public_readback': args.verify_public, 'reader': identity(html)}))


if __name__ == '__main__':
    main()
