"""Admit the identity-tested D60 native consumer; no new semantic canon claim."""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'backend/course-capsule-v1/adapters/d60-native-ledger-v1'
SITE = 'docs/backend/d60/native-ledger'

def load(path):
    return json.loads((ROOT / path).read_bytes())

def fact(path):
    raw = (ROOT / path).read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def save(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

def main():
    assert sys.argv[1:] in ([], ['--refresh-hosted-evidence']), 'Unknown admission operation'
    hosted_refresh = bool(sys.argv[1:])
    tests = load(BASE + '/tests.json')
    browser = load(BASE + '/browser-tests.json')
    readback = load(BASE + '/public-source-readback.json')
    assert tests['state'] == browser['state'] == readback['state'] == 'pass'
    assert len(tests['checks']) == 21 and len(tests['negative_fixtures']) == 5
    assert tests['semantic_canon_approval'] is False and tests['native_book_rebuilt'] is False
    assert tests['summary']['all_native_records'] == 8338
    assert tests['summary']['current_native_heads'] == 7996
    assert tests['summary']['counts'] == {'terms': 528, 'segments': 2174, 'corrections': 564, 'rights': 96}
    assert tests['summary']['reference_gaps'] == 0
    assert readback['anonymous'] and not readback['credentials_used']
    assert readback['source_archive'] == tests['source_archive']
    assert readback['bytes'] == tests['source_archive']['bytes']
    assert readback['sha256'] == tests['source_archive']['sha256']
    assert len(browser['cases']) == 8 and not browser['errors']
    assert browser['external_network_blocked'] and not browser['desktop_interaction']
    for item in browser['input_files']:
        assert fact(item['path']) == {k: item[k] for k in ('bytes', 'sha256')}, 'Stale browser evidence'
    for name, identity in tests['outputs'].items():
        assert '/' not in name and '\\' not in name
        assert fact(BASE + '/site/' + name) == identity, 'Raw replay output changed'
        if hosted_refresh and name.endswith('.html'):
            text = (ROOT / SITE / name).read_text(encoding='utf-8')
            assert text.count('data-central-surface-navigation="v1"') == 2, 'Missing managed navigation'
            for placement, pattern in [
                ('top', r'(?:\n[ \t]*)?<nav\b(?=[^>]*data-central-surface-navigation="v1")(?=[^>]*data-placement="top")[^>]*>.*?</nav>'),
                ('bottom', r'<nav\b(?=[^>]*data-central-surface-navigation="v1")(?=[^>]*data-placement="bottom")[^>]*>.*?</nav>(?:\n[ \t]*)?'),
            ]:
                text, removed = re.subn(pattern, '', text, count=1, flags=re.DOTALL | re.IGNORECASE)
                assert removed == 1, 'Managed navigation is not reversible: ' + placement
            original = text.encode('utf-8')
            assert {'bytes': len(original), 'sha256': hashlib.sha256(original).hexdigest()} == identity, 'Hosted body differs from raw replay'
        else:
            assert fact(SITE + '/' + name) == identity, 'Hosted projection differs before admission'

    target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json'
    nav_path = 'backend/authority/central-reader-navigation-v1.json'
    old_raw = (ROOT / target).read_bytes()
    nav_raw = (ROOT / nav_path).read_bytes()
    over, nav = json.loads(old_raw), json.loads(nav_raw)
    before, nav_before = copy.deepcopy(over), copy.deepcopy(nav)
    evidence = [{'kind': kind, 'locator': BASE + '/' + name, **fact(BASE + '/' + name),
                 'verified_date': '2026-10-02' if kind == 'd60_native_browser_tests' else '2026-10-01'}
                for kind, name in [('d60_native_metadata_lock', 'source-lock.json'),
                                   ('d60_native_intake_audit', 'intake-audit.json'),
                                   ('d60_native_ledger_tests', 'tests.json'),
                                   ('d60_native_browser_tests', 'browser-tests.json'),
                                   ('d60_native_source_public_readback', 'public-source-readback.json')]]
    adapter = over['semantic_adapters']['D60']
    adapter['evidence'] = [r for r in adapter['evidence'] if r['kind'] not in {e['kind'] for e in evidence}] + evidence
    for capability in ['translation_ledger', 'terminology', 'corrections']:
        over['native_capabilities']['D60'][capability] = {'status': 'available_unverified', 'evidence': evidence}
    resources = over['educator_evidence']['D60']['resources']
    resources[:] = [r for r in resources if not r['id'].startswith('D60:native-ledger-')]
    scope_id = '528 istilah, 2.174 segmen sumber/terjemahan, 564 koreksi dan 96 catatan hak asli; pencarian per unit serta arsip metadata yang mempertahankan 8.338 rekaman asli. Penemuan lewat unit induk bukan bukti penerapan pada setiap kalimat. Kanon belum ditinjau secara independen; 73 identitas berkas target berbeda.'
    scope_en = '528 terms, 2,174 source/target segments, 564 corrections and 96 native rights records; unit discovery and a metadata archive preserving 8,338 original records. Parent-unit discovery is not sentence-level applicability. No independent canon approval; 73 target-file identities differ.'
    for locale, page in [('id', 'ledger.html'), ('en', 'ledger-en.html')]:
        resources.append({'id': 'D60:native-ledger-' + locale,
            'title': 'D60 · Istilah, sumber, koreksi dan hak asli' if locale == 'id' else 'D60 · Native terms, sources, corrections and rights',
            'resource_type': 'educator-data', 'status': 'verified',
            'url': 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d60/native-ledger/' + page,
            'scope': scope_id if locale == 'id' else scope_en, **fact(SITE + '/' + page)})
    tool = {'tool_id': 'd60.native_ledger', 'label': 'D60 · Cari istilah, sumber dan koreksi',
        'href': 'backend/d60/native-ledger/ledger.html', 'action_kind': 'reference', 'scope': scope_id,
        'state': 'verified', 'primary': False, 'machine_data_is_learner_destination': False,
        'limitations': ['Catatan asli dipertahankan, bukan persetujuan kanon baru. Penemuan melalui unit induk bukan bukti penerapan pada setiap kalimat.',
                       'Sebanyak 73 identitas berkas target berbeda; perbedaan ini tidak membuktikan kerusakan setiap segmen.',
                       'Antarmuka Inggris tetap menuju isi buku berbahasa Indonesia. Arsip metadata bukan buku lengkap atau pembangunan ulang buku.'],
        'page': {'path': SITE + '/ledger.html', **fact(SITE + '/ledger.html')},
        'resource': {'path': SITE + '/projection.json', **fact(SITE + '/projection.json')},
        'evidence': {'path': BASE + '/tests.json', **fact(BASE + '/tests.json')}}
    over['learner_tools']['D60'] = [r for r in over['learner_tools']['D60'] if r['tool_id'] != tool['tool_id']] + [tool]
    for key in before:
        left, right = copy.deepcopy(before[key]), copy.deepcopy(over[key])
        if key in ['native_capabilities', 'educator_evidence', 'semantic_adapters', 'learner_tools']:
            left.pop('D60', None); right.pop('D60', None)
        assert left == right, 'Unrelated override changed: ' + key

    surface = {'root': SITE, 'locale': 'id', 'state': 'current-shared-corpus-capability', 'documents': []}
    for locale, page, opposite in [('id', 'ledger.html', 'ledger-en.html'), ('en', 'ledger-en.html', 'ledger.html')]:
        suffix = '.en' if locale == 'en' else ''
        surface['documents'].append({'path': page, 'locale': locale, 'course_ids': ['D60'],
            'contents_paths': [opposite], 'related_course_surface_paths': [
                'docs/backend/d60/D60' + suffix + '.html', 'docs/backend/d60/D60-pengajar' + suffix + '.html']})
    nav['course_surfaces'] = [r for r in nav['course_surfaces'] if r['root'] != SITE] + [surface]
    for prior in nav['course_surfaces']:
        if prior['root'] != 'docs/backend/d60':
            continue
        prior['exclude_subtrees'] = list(dict.fromkeys([*prior.get('exclude_subtrees', []), 'native-ledger']))
        for document in prior['documents']:
            page = 'ledger-en.html' if document['locale'] == 'en' else 'ledger.html'
            document['related_course_surface_paths'] = list(dict.fromkeys([*document.get('related_course_surface_paths', []), SITE + '/' + page]))
    for original in nav_before['course_surfaces']:
        if original['root'] not in [SITE, 'docs/backend/d60']:
            assert original == next(r for r in nav['course_surfaces'] if r['root'] == original['root']), 'Unrelated navigation surface changed'
    for key in nav_before:
        if key not in ['course_surfaces', 'summary']:
            assert nav_before[key] == nav[key], 'Unrelated navigation section changed'
    nav['summary']['course_surface_roots'] = len(nav['course_surfaces'])
    nav['summary']['course_surface_html_documents'] = sum(len(s['documents']) for s in nav['course_surfaces'])
    nav['summary']['classified_html_documents'] = sum(nav['summary'][k] for k in ['reader_html_documents', 'gateway_html_documents', 'course_surface_html_documents', 'generic_html_documents'])
    nav['summary']['navigation_overlay_documents'] = sum(nav['summary'][k] for k in ['reader_html_documents', 'gateway_html_documents', 'course_surface_html_documents']) + sum(bool(s['navigation_required']) for s in nav['generic_surfaces'])
    assert (ROOT / target).read_bytes() == old_raw, 'Concurrent override edit'
    assert (ROOT / nav_path).read_bytes() == nav_raw, 'Concurrent navigation edit'
    save(target, over); save(nav_path, nav)
    report = {'schema': 'd60-native-ledger-admission/1', 'state': 'locally_admitted_pending_publication',
              'hosted_navigation_overlay_verified': hosted_refresh,
              'role': 'D60', 'summary': tests['summary'], 'semantic_canon_approval': False,
              'native_book_rebuilt': False, 'overall_backend_complete': False,
              'other_role_overrides_unchanged': True, 'unrelated_navigation_preserved': True,
              'inputs': evidence, 'overrides': fact(target), 'navigation': fact(nav_path)}
    save(BASE + '/admission.json', report)
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__':
    main()
