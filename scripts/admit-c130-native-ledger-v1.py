"""Admit the tested C130 metadata consumer; preserve every other course object."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = 'backend/course-capsule-v1/adapters/c130-native-ledger-v1'
SITE = 'docs/backend/c130-native'

def load(path):
    return json.loads((ROOT / path).read_bytes())

def fact(path):
    data = (ROOT / path).read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def save(path, data):
    (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

def main(cache):
    for command in [[sys.executable, '-B', 'scripts/test-c130-native-ledger-v1.py', '--cache', str(cache)],
                    ['node', 'scripts/test-c130-native-ledger-ui-v1.mjs']]:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
        assert result.returncode == 0, result.stderr
    validation, audit = load(BASE + '/validation.json'), load(BASE + '/audit.json')
    receipt = load(BASE + '/site/build-receipt.json')
    assert validation['state'] == 'pass' and validation['consumer_negative_cases'] == 11
    assert validation['semantic_canon_review'] is False and validation['unresolved_target_locations'] == 21
    assert audit['native_digest_failures'] == 0 and audit['projection'] == fact(BASE + '/projection.json')
    assert receipt['projection'] == audit['projection']
    assert receipt['semantic_canon_review'] is False and receipt['overall_backend_complete'] is False
    copies = list(receipt['files']) + ['build-receipt.json']
    for name in copies:
        assert '/' not in name and '\\' not in name and name not in {'.', '..'}
        if name in receipt['files']:
            assert fact(BASE + '/site/' + name) == receipt['files'][name], 'Unvalidated consumer bytes'
        destination = ROOT / SITE / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / BASE / 'site' / name).read_bytes())
    for name in ['validation.json', 'input/source-lock.json']:
        destination = ROOT / SITE / Path(name).name
        destination.write_bytes((ROOT / BASE / name).read_bytes())

    override_path = 'backend/course-capsule-v1/authority/integration-overrides-v1.json'
    override_raw = (ROOT / override_path).read_bytes()
    over = json.loads(override_raw)
    before = copy.deepcopy(over)
    evidence = [{'kind': kind, 'locator': BASE + '/' + name, **fact(BASE + '/' + name), 'verified_date': '2026-09-30'}
                for kind, name in [('c130_native_metadata_audit', 'audit.json'),
                                   ('c130_native_ledger_validation', 'validation.json'),
                                   ('c130_native_metadata_lock', 'input/source-lock.json')]]
    adapter = over['semantic_adapters']['C130']
    adapter['evidence'] = [r for r in adapter['evidence'] if r['kind'] not in {e['kind'] for e in evidence}] + evidence
    for capability in ['translation_ledger', 'terminology', 'corrections']:
        over['native_capabilities']['C130'][capability] = {'status': 'available_unverified', 'evidence': evidence}
    resources = over['educator_evidence']['C130']['resources']
    resources[:] = [r for r in resources if not r['id'].startswith('C130:native-ledger-')]
    for locale, suffix in [('id', ''), ('en', '.en')]:
        page = 'ledger' + suffix + '.html'
        resources.append({'id': 'C130:native-ledger-' + locale,
            'title': 'C130 · Native terminology and correction records' if locale == 'en' else 'C130 · Istilah dan catatan koreksi asli',
            'resource_type': 'educator-data', 'status': 'verified',
            'url': 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c130-native/' + page,
            'scope': '140 term choices and 94 correction records; 5,525 segment identities. Producer claims retained, not new semantic canon approval. Twenty-one target locations remain unresolved.' if locale == 'en' else '140 pilihan istilah dan 94 catatan koreksi; 5.525 identitas segmen. Klaim pembuat buku dipertahankan, bukan persetujuan kanon baru. Sebanyak 21 lokasi teks target belum pasti.',
            **fact(SITE + '/' + page)})
    tool = {'tool_id': 'c130.native_ledger', 'label': 'C130 · Cari istilah dan catatan koreksi',
        'href': 'backend/c130-native/ledger.html', 'action_kind': 'reference',
        'scope': '140 pilihan istilah dan 94 catatan koreksi asli dengan pencarian luring serta rujukan konsep dan sumber.',
        'state': 'verified', 'primary': False, 'machine_data_is_learner_destination': False,
        'limitations': ['Catatan asli bukan bukti peninjauan kanon baru; 21 lokasi teks target belum pasti. Hubungan konsep bukan daftar kemunculan kata. Buku diunduh terpisah.'],
        'page': {'path': SITE + '/ledger.html', **fact(SITE + '/ledger.html')},
        'resource': {'path': SITE + '/projection.json', **fact(SITE + '/projection.json')},
        'evidence': {'path': SITE + '/build-receipt.json', **fact(SITE + '/build-receipt.json')}}
    over['learner_tools']['C130'] = [r for r in over['learner_tools']['C130'] if r['tool_id'] != tool['tool_id']] + [tool]
    for key in before:
        left, right = copy.deepcopy(before[key]), copy.deepcopy(over[key])
        if key in ['native_capabilities', 'educator_evidence', 'semantic_adapters', 'learner_tools']:
            left.pop('C130', None)
            right.pop('C130', None)
        assert left == right, 'Unrelated role changed: ' + key
    assert (ROOT / override_path).read_bytes() == override_raw, 'Concurrent override edit'
    save(override_path, over)

    nav_path = 'backend/authority/central-reader-navigation-v1.json'
    nav_raw = (ROOT / nav_path).read_bytes()
    nav = json.loads(nav_raw)
    surface = {'root': SITE, 'locale': 'id', 'state': 'current-shared-corpus-capability', 'documents': []}
    for locale, suffix, opposite in [('id', '', '.en'), ('en', '.en', '')]:
        surface['documents'].append({'path': 'ledger' + suffix + '.html', 'locale': locale, 'course_ids': ['C130'],
            'contents_paths': ['ledger' + opposite + '.html'],
            'related_course_surface_paths': ['docs/backend/c130/C130.html', 'docs/backend/c130-teacher/C130.teacher' + suffix + '.html']})
    nav['course_surfaces'] = [s for s in nav['course_surfaces'] if s['root'] != SITE] + [surface]
    for prior in nav['course_surfaces']:
        if prior['root'] not in ['docs/backend/c130', 'docs/backend/c130-teacher']:
            continue
        for doc in prior['documents']:
            suffix = '.en' if doc.get('locale') == 'en' else ''
            doc['contents_paths'] = [value for value in doc.get('contents_paths', []) if not value.startswith('../c130-native/')]
            doc['related_course_surface_paths'] = list(dict.fromkeys([*doc.get('related_course_surface_paths', []), SITE + '/ledger' + suffix + '.html']))
    nav['summary']['course_surface_roots'] = len(nav['course_surfaces'])
    nav['summary']['course_surface_html_documents'] = sum(len(s['documents']) for s in nav['course_surfaces'])
    nav['summary']['classified_html_documents'] = sum(nav['summary'][k] for k in ['reader_html_documents', 'gateway_html_documents', 'course_surface_html_documents', 'generic_html_documents'])
    nav['summary']['navigation_overlay_documents'] = sum(nav['summary'][k] for k in ['reader_html_documents', 'gateway_html_documents', 'course_surface_html_documents']) + sum(bool(s['navigation_required']) for s in nav['generic_surfaces'])
    assert (ROOT / nav_path).read_bytes() == nav_raw, 'Concurrent navigation edit'
    save(nav_path, nav)
    print(json.dumps({'state': 'locally_admitted_pending_publication', 'role': 'C130', 'terms': 140,
        'corrections': 94, 'unresolved_locations': 21, 'semantic_canon_review': False, 'other_roles_unchanged': True}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path, required=True)
    main(parser.parse_args().cache)
