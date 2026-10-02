"""Admit the identity-tested D20 native consumer; no new semantic canon claim."""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'backend/course-capsule-v1/adapters/d20-native-ledger-v1'
SITE = 'docs/backend/d20/native-ledger'

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
    assert tests['state'] == browser['state'] == 'pass'
    assert len(tests['checks']) == 14 and len(tests['negative_fixtures']) == 3
    assert tests['semantic_canon_review'] is False and tests['native_book_rebuilt'] is False
    assert tests['summary']['segments'] == 2196 and tests['summary']['terms'] == 425
    assert tests['summary']['source_fragment_states'] == {'exact_fragment': 2196}
    assert tests['summary']['target_fragment_states'] == {'exact_fragment': 2196}
    assert tests['summary']['unit_file_states'] == {'exact_file': 36}
    assert len(browser['cases']) == 6 and not browser['errors']
    assert browser['external_network_blocked'] and not browser['personal_browser_used']
    for item in browser['input_files']:
        filename = Path(item['path']).name
        assert filename in tests['outputs'], 'Foreign browser input'
        assert fact(BASE + '/site/' + filename) == {k:item[k] for k in ('bytes','sha256')}, 'Stale raw browser evidence'
    for name, identity in tests['outputs'].items():
        assert '/' not in name and '\\\\' not in name
        assert fact(BASE + '/site/' + name) == identity, 'Raw replay output changed'
        if hosted_refresh and name.endswith('.html'):
            text = (ROOT / SITE / name).read_text(encoding='utf-8')
            assert text.count('data-central-surface-navigation="v1"') == 2, 'Missing managed navigation'
            for placement, pattern in [
                ('top', r'(?:\n[ \t]*)?<nav\b(?=[^>]*data-central-surface-navigation="v1")(?=[^>]*data-placement="top")[^>]*>.*?</nav>'),
                ('bottom', r'<nav\b(?=[^>]*data-central-surface-navigation="v1")(?=[^>]*data-placement="bottom")[^>]*>.*?</nav>(?:\n[ \t]*)?'),
            ]:
                text, removed = re.subn(pattern, '', text, count=1, flags=re.DOTALL | re.IGNORECASE)
                assert removed == 1, 'Managed navigation not reversible: ' + placement
            assert {'bytes':len(text.encode('utf-8')), 'sha256':hashlib.sha256(text.encode('utf-8')).hexdigest()} == identity, 'Hosted body differs from replay'
        else:
            assert fact(SITE + '/' + name) == identity, 'Hosted projection differs before admission'

    target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json'
    nav_path = 'backend/authority/central-reader-navigation-v1.json'
    old_raw = (ROOT / target).read_bytes()
    nav_raw = (ROOT / nav_path).read_bytes()
    over, nav = json.loads(old_raw), json.loads(nav_raw)
    before, nav_before = copy.deepcopy(over), copy.deepcopy(nav)
    evidence = [{'kind': kind, 'locator': BASE + '/' + name, **fact(BASE + '/' + name),
                 'verified_date': '2026-10-02'}
                for kind, name in [('d20_native_metadata_lock', 'source-lock.json'),
                                   ('d20_native_intake_audit', 'intake-audit.json'),
                                   ('d20_native_ledger_tests', 'tests.json'),
                                   ('d20_native_browser_tests', 'browser-tests.json')]]
    adapter = over['semantic_adapters']['D20']
    adapter['evidence'] = [r for r in adapter['evidence'] if r['kind'] not in {e['kind'] for e in evidence}] + evidence
    for capability in ['translation_ledger', 'terminology', 'corrections']:
        over['native_capabilities']['D20'][capability] = {'status': 'available_unverified', 'evidence': evidence}
    resources = over['educator_evidence']['D20']['resources']
    resources[:] = [r for r in resources if not r['id'].startswith('D20:native-ledger-')]
    scope_id = '425 istilah, 2.196 pasangan fragmen sumber/terjemahan yang cocok, 286 koreksi, 7 catatan QA istilah dan 4 catatan hak; tujuh tabel asli dipertahankan. Kecocokan hash bukan pengesahan makna atau kanon. Bacaan bab berbahasa Indonesia; sumber asli bahasa Inggris ditautkan terpisah.'
    scope_en = '425 terms, 2,196 matched source/translation fragment pairs, 286 corrections, 7 terminology-QA records and 4 rights records; seven native streams preserved. Hash agreement is not semantic or canon approval. Chapter reading is Indonesian; original English source is linked separately.'
    for locale, page in [('id', 'ledger.html'), ('en', 'ledger-en.html')]:
        resources.append({'id': 'D20:native-ledger-' + locale,
            'title': 'D20 · Istilah, sumber, koreksi dan hak asli' if locale == 'id' else 'D20 · Native terms, sources, corrections and rights',
            'resource_type': 'educator-data', 'status': 'verified',
            'url': 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d20/native-ledger/' + page,
            'scope': scope_id if locale == 'id' else scope_en, **fact(SITE + '/' + page)})
    tool = {'tool_id': 'd20.native_ledger', 'label': 'D20 · Cari istilah, sumber dan koreksi',
        'href': 'backend/d20/native-ledger/ledger.html', 'action_kind': 'reference', 'scope': scope_id,
        'state': 'verified', 'primary': False, 'machine_data_is_learner_destination': False,
        'limitations': ['Identitas 2.196 pasangan fragmen dan 36 berkas cocok; ketepatan terjemahan dan penerapan kanon belum diperiksa ulang.',
                       'Penelusuran bab mengikuti induk unit asli; bukan bukti penerapan istilah pada setiap kalimat.',
                       'Antarmuka Inggris tidak mengubah bahasa bacaan Indonesia. Arsip metadata bukan buku atau produksi ulang buku.'],
        'page': {'path': SITE + '/ledger.html', **fact(SITE + '/ledger.html')},
        'resource': {'path': SITE + '/projection.json', **fact(SITE + '/projection.json')},
        'evidence': {'path': BASE + '/tests.json', **fact(BASE + '/tests.json')}}
    over['learner_tools']['D20'] = [r for r in over['learner_tools']['D20'] if r['tool_id'] != tool['tool_id']] + [tool]
    for key in before:
        left, right = copy.deepcopy(before[key]), copy.deepcopy(over[key])
        if key in ['native_capabilities', 'educator_evidence', 'semantic_adapters', 'learner_tools']:
            left.pop('D20', None); right.pop('D20', None)
        assert left == right, 'Unrelated override changed: ' + key

    surface = {'root': SITE, 'locale': 'id', 'state': 'current-shared-corpus-capability', 'documents': []}
    for locale, page, opposite in [('id', 'ledger.html', 'ledger-en.html'), ('en', 'ledger-en.html', 'ledger.html')]:
        suffix = '.en' if locale == 'en' else ''
        surface['documents'].append({'path': page, 'locale': locale, 'course_ids': ['D20'],
            'contents_paths': [opposite], 'related_course_surface_paths': [
                'docs/backend/d20/D20' + suffix + '.html', 'docs/backend/d20/D20-pengajar' + suffix + '.html']})
    nav['course_surfaces'] = [r for r in nav['course_surfaces'] if r['root'] != SITE] + [surface]
    for prior in nav['course_surfaces']:
        if prior['root'] != 'docs/backend/d20':
            continue
        prior['exclude_subtrees'] = list(dict.fromkeys([*prior.get('exclude_subtrees', []), 'native-ledger']))
        for document in prior['documents']:
            page = 'ledger-en.html' if document['locale'] == 'en' else 'ledger.html'
            document['related_course_surface_paths'] = list(dict.fromkeys([*document.get('related_course_surface_paths', []), SITE + '/' + page]))
    for original in nav_before['course_surfaces']:
        if original['root'] not in [SITE, 'docs/backend/d20']:
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
    report = {'schema': 'd20-native-ledger-admission/1', 'state': 'locally_admitted_pending_publication',
              'hosted_navigation_overlay_verified': hosted_refresh,
              'role': 'D20', 'summary': tests['summary'], 'semantic_canon_review': False,
              'native_book_rebuilt': False, 'overall_backend_complete': False,
              'other_role_overrides_unchanged': True, 'unrelated_navigation_preserved': True,
              'inputs': evidence, 'overrides': fact(target), 'navigation': fact(nav_path)}
    save(BASE + '/admission.json', report)
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__':
    main()
