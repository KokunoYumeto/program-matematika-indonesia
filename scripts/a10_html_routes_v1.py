"""Bind the native A10 identity projection to its separately published HTML reader."""
from __future__ import annotations

import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote

from central_surface_navigation_overlay_v1 import strip_central_surface_overlay

ROOT = Path(__file__).resolve().parents[1]
MIRROR = 'docs/id-ID/courses/A10/A10_READER_MIRROR_MANIFEST_V1.json'
MIRROR_SHA = 'f0416955ef0f6eecf21ff86cda7f7c23a7b67140a34f206dce1005edc9217e68'
READER_URL = 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/A10/reader/index.html'


def require(ok, code):
    if not ok:
        raise ValueError(code)


class ReaderAnchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = {}
        self.modules = {}
        self.current = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'article' and 'data-module-id' in a:
            require(self.current is None, 'A10-HTML-NESTED-MODULE')
            self.current = a['data-module-id']
            require(self.current not in self.modules, 'A10-HTML-DUPLICATE-MODULE')
            self.modules[self.current] = a.get('data-target-sha256')
        if 'id' in a:
            require(a['id'] not in self.ids, 'A10-HTML-DUPLICATE-ID')
            self.ids[a['id']] = self.current

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == 'article':
            self.current = None


def attach_html_routes(bundle):
    manifest_bytes = (ROOT / MIRROR).read_bytes()
    require(hashlib.sha256(manifest_bytes).hexdigest() == MIRROR_SHA, 'A10-HTML-MANIFEST-IDENTITY')
    manifest = json.loads(manifest_bytes)
    path = manifest['reader_entrypoint']
    require(path == 'docs/id-ID/courses/A10/reader/index.html', 'A10-HTML-ENTRY')
    body = strip_central_surface_overlay((ROOT / path).read_bytes(), path)
    require({'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()} == manifest['reader_body'],
            'A10-HTML-BODY-IDENTITY')
    parser = ReaderAnchors()
    parser.feed(body.decode('utf-8'))
    parser.close()
    require(len(parser.modules) == 82 and len(parser.ids) == 55690, 'A10-HTML-INVENTORY')
    modules = bundle['module_index']
    require(parser.modules == {m['module_id']: m['sha256'] for m in modules}, 'A10-HTML-TARGET-MODULES')
    units = {u['id']: u for u in bundle['unit_reference_index']}
    anchored = 0
    for u in units.values():
        if u['source_module_id'] and u['source_element_id']:
            key = u['source_module_id'] + '--' + u['source_element_id']
            require(parser.ids.get(key) == u['source_module_id'], 'A10-HTML-SCOPED-UNIT')
            anchored += 1
    require(anchored == 55180, 'A10-HTML-ANCHORED-UNITS')

    def item_url(uid):
        if uid is None:
            return None
        u = units[uid]
        key = u['source_module_id'] + '--' + u['source_element_id']
        require(parser.ids.get(key) == u['source_module_id'], 'A10-HTML-ITEM')
        return READER_URL + '#' + quote(key, safe='')

    for m in modules:
        key = 'module-' + m['module_id']
        require(parser.ids.get(key) == m['module_id'], 'A10-HTML-MODULE-ANCHOR')
        m['html_url'] = READER_URL + '#' + key
        m['html_route_scope'] = 'exact_module_anchor'
        m['html_route_verified'] = True
    for e in bundle['exercise_index']:
        for prefix, uid in [('exercise', e['id']), ('problem', e['problem_id']), ('solution', e['solution_id'])]:
            e[prefix + '_html_url'] = item_url(uid)
        e['html_route_verified'] = True
    evidence = {'schema': 'a10-html-route-evidence/1', 'course_id': 'A10',
        'reader_url': READER_URL, 'content_language': 'id-ID',
        'source_manifest': {'path': MIRROR, 'bytes': len(manifest_bytes), 'sha256': MIRROR_SHA},
        'reader_body': {'path': path, **manifest['reader_body']},
        'route_identity_rule': 'source_module_id + -- + source_element_id',
        'module_count': 82, 'exercise_routes': 9406, 'problem_routes': 9406,
        'solution_routes': 6106, 'missing_solutions': 3300,
        'all_source_element_routes': anchored, 'html_ids_unique': True,
        'module_target_hashes_match': True, 'source_pdf_routes_unchanged': True,
        'reading_language_follows_interface': False,
        'whole_reader_accessibility_conformance_claimed': False}
    bundle['html_route_evidence'] = evidence
    bundle['source_lock']['html_reader'] = evidence['reader_body']
    bundle['source_lock']['html_manifest'] = evidence['source_manifest']
    bundle['capabilities']['counts'].update(html_module_routes=82, html_exercise_routes=9406,
        html_problem_routes=9406, html_solution_routes=6106)
    # Legacy route flags continue to describe the PDF audit, not these new HTML links.
    bundle['claim_boundary']['exact_html_item_routes_verified'] = True
    bundle['claim_boundary']['html_route_evidence'] = 'data/html-route-evidence.json'
    return bundle
