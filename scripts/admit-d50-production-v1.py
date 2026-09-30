"""Bind verified D50 native production and actual delivery, preserving other roles."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
from urllib.request import urlopen

spec = importlib.util.spec_from_file_location('d50_production', Path(__file__).with_name('audit-d50-native-production-v1.py'))
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
from central_surface_navigation_overlay_v1 import strip_central_surface_overlay

ROOT, BASE = a.ROOT, a.BASE


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def validate_audit(audit, native):
    a.validate_receipt(native, a.EXPECTED_ZIP)
    a.require(audit['state'] == 'pass' and audit['source_members'] == 1282
              and audit['all_source_checksums_verified'] and audit['native_receipt_two_cycles_validated'],
              'Native source audit missing')
    fresh = audit['fresh_html_backend_replay']
    a.require(fresh and fresh['matches_frozen_native_outputs'] and fresh['tex_executed'] is False,
              'Fresh non-TeX replay proof missing')
    a.require(len(fresh['commands']) == 4 and all(c['exit_code'] == 0 for c in fresh['commands']),
              'Four successful fresh replay commands required')
    a.require(set(fresh['outputs']) == set(a.OUTPUTS), 'Fresh output inventory incomplete')
    for key, value in fresh['outputs'].items():
        a.require(value == native['clean_rebuilds'][0]['outputs'][key], 'Fresh/native replay mismatch')
    a.require(audit['historical_pdf_replay']['pdf'] == native['clean_rebuilds'][0]['outputs']['pdf']
              and audit['fresh_pdf_build'] is False, 'PDF evidence must remain historical')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-root', required=True, type=Path)
    parser.add_argument('--audit', required=True, type=Path)
    args = parser.parse_args()
    native_bytes = (args.native_root.resolve() / 'qa/complete/SOURCE_PACKAGE_INTEGRITY_R1.json').read_bytes()
    native = json.loads(native_bytes)
    audit_bytes = args.audit.resolve().read_bytes()
    audit = json.loads(audit_bytes)
    validate_audit(audit, native)
    a.require(a.fact(native_bytes) == a.core(audit['native_receipt']), 'Native receipt identity changed')
    delivery = json.loads((BASE / 'delivery/reader-delivery.json').read_bytes())
    witness = json.loads((BASE / 'input/reader-witness.json').read_bytes())
    html_path = ROOT / 'docs/backend/d50/reader/index.html'
    html_bytes = html_path.read_bytes()
    a.require(a.fact(strip_central_surface_overlay(html_bytes, 'D50')) == a.core(witness['reader']),
              'Hosted reader changed outside removable navigation')
    url = delivery['reader_url']
    production = BASE / 'production'
    cached = production / 'current-reader-readback.json'
    if cached.exists():
        public = json.loads(cached.read_bytes())
        a.require(public['state'] == 'pass' and public['anonymous'] and public['url'] == url
                  and a.core(public) == a.fact(html_bytes), 'Cached reader proof differs; re-audit explicitly')
    else:
        with urlopen(url, timeout=45) as response:
            a.require(response.status == 200, 'Reader is not publicly readable')
            public_bytes = response.read(len(html_bytes) + 1)
        a.require(public_bytes == html_bytes, 'Public D50 reader differs from current local bytes')
        public = {'schema': 'd50-current-reader-readback/1', 'state': 'pass', 'url': url,
                  **a.fact(public_bytes), 'anonymous': True,
                  'verified_at': datetime.now(timezone.utc).isoformat(),
                  'native_body_sha256': witness['reader']['sha256'],
                  'navigation_reversibly_removed': True}
    production.mkdir(parents=True, exist_ok=True)
    (production / 'native-rebuild-receipt.json').write_bytes(native_bytes)
    (production / 'native-production-audit.json').write_bytes(audit_bytes)
    save(production / 'current-reader-readback.json', public)
    evidence = []
    for kind, name in [('d50_frozen_two_cycle_native_rebuild', 'native-rebuild-receipt.json'),
                       ('d50_independent_native_replay', 'native-production-audit.json')]:
        path = production / name
        evidence.append({'kind': kind, 'locator': path.relative_to(ROOT).as_posix(),
                         **a.identity(path), 'verified_date': '2026-09-30'})
    override_path = ROOT / 'backend/course-capsule-v1/authority/integration-overrides-v1.json'
    overrides = json.loads(override_path.read_bytes())
    before = copy.deepcopy(overrides)
    note = ('HTML dan backend dibangun ulang dari ZIP sumber yang dirilis; PDF '
            'diikat ke dua pembangunan bersih terdahulu. Tidak ada kompilasi PDF baru '
            'atau klaim peninjauan semantik baru.')
    for key in ['build', 'deterministic_replay']:
        overrides['native_capabilities']['D50'][key] = {'status': 'verified', 'evidence': evidence, 'note': note}
    before['native_capabilities'].pop('D50')
    preserved = copy.deepcopy(overrides)
    preserved['native_capabilities'].pop('D50')
    a.require(preserved == before, 'Unrelated integration override changed')
    learner_path = ROOT / 'backend/authority/learner-delivery-overrides-v1.json'
    learner = json.loads(learner_path.read_bytes())
    learner_before = copy.deepcopy(learner)
    public_evidence = {
        'kind': 'anonymous_public_readback_and_native_source_replay',
        'locator': 'https://github.com/KokunoYumeto/program-matematika-indonesia/blob/main/'
                   'backend/course-capsule-v1/adapters/d50-surface-v1/production/current-reader-readback.json',
        'verified_date': '2026-09-30',
        'note': 'Bacaan lengkap berbahasa Indonesia; antarmuka Inggris bukan terjemahan buku. Isi sama dengan edisi native setelah navigasi pusat dilepas. Bukan sertifikasi WCAG.'}
    html = {'status': 'verified', 'format': 'text/html', 'url': url,
            **a.fact(html_bytes), 'scope': 'whole_course', 'dependency_free': False, 'evidence': public_evidence}
    dependency_evidence = {**public_evidence,
        'locator': 'https://github.com/KokunoYumeto/program-matematika-indonesia/blob/main/'
                   'backend/course-capsule-v1/adapters/d50-surface-v1/delivery/public-dependencies.json',
        'verified_date': '2026-09-22',
        'note': 'Identitas publik beku dicocokkan dengan ZIP sumber dan dua pembangunan native; bukan unduhan ulang baru.'}
    learner['courses']['D50'] = {
        **learner['courses'].get('D50', {}), 'primary': html, 'online_html': html,
        'pdf': {'status': 'verified', 'format': 'application/pdf', **delivery['pdf'],
                'scope': 'whole_course', 'evidence': dependency_evidence},
        'portable_html': {'status': 'available_unverified', 'format': 'application/zip+html',
                          'url': witness['archive']['url'], **a.core(witness['archive']),
                          'scope': 'whole_course', 'entry_point': 'index.html', 'inventory_count': 44,
                          'dependency_free': False, 'evidence': {**dependency_evidence,
                              'note': 'ZIP dapat diunduh dan identitas berkas telah diperiksa. Perenderan matematika masih menggunakan MathJax CDN; paket ini belum bebas dependensi jaringan.'}},
        'capabilities': {
            **learner['courses'].get('D50', {}).get('capabilities', {}),
            'semantic_html': {'status': 'verified', 'evidence': {**public_evidence,
                'note': 'Struktur dan penanda HTML asli lulus verifikasi native; MathJax masih memakai CDN. Tidak mengklaim semua pembaca layar telah diuji.'}},
        },
    }
    learner_before['courses'].pop('D50', None)
    preserved = copy.deepcopy(learner)
    preserved['courses'].pop('D50')
    a.require(preserved == learner_before, 'Unrelated learner override changed')
    save(override_path, overrides)
    save(learner_path, learner)
    save(production / 'admission.json', {'schema': 'd50-production-admission/1', 'state': 'pass',
         'role': 'D50', 'native_book_modified': False, 'other_roles_unchanged': True,
         'fresh_pdf_build': False, 'evidence': evidence, 'reader': public,
         'overall_program_backend_complete': False})
    print(json.dumps({'state': 'admitted', 'role': 'D50', 'other_roles_unchanged': True,
                      'fresh_html_backend_replay': True, 'fresh_pdf_build': False}))


if __name__ == '__main__':
    main()
