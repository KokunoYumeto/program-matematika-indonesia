"""Bind fresh export checks; never inherit acceptance from the prior edition.

OpenAI Codex - GPT-6 Astra, Ultra effort: integration checks and packaging.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/course-formats-v1'))
import course_formats as f


def seal(work, phase, qa_root=None):
    work = work.resolve()
    f.require(work.is_relative_to(ROOT / 'outputs/course-format-integration-v1'), 'Owned staging required')
    load = lambda name: f.decode((work / name).read_bytes())
    fact = lambda name: {'path': name, **f.identity(work / name)}
    m = load('SOURCE_MANIFEST.json')
    slug = m['export']['slug']
    names = [f'output/00-{slug}.pdf', f'output/01-{slug}.tex',
             f'output/02-{slug}-source.zip', f'output/03-{slug}.epub']
    files = [fact(name) for name in names]
    if phase == 'integration':
        f.require(qa_root is not None, 'Reader/programme browser evidence required')
        qa_root = qa_root.resolve()
        f.require(qa_root.is_relative_to(ROOT / 'outputs/course-format-integration-v1'), 'Owned QA directory required')
        edition = ROOT / 'docs/editions' / slug
        browser = f.decode((qa_root / 'reader-browser/browser-check.json').read_bytes())
        downloads = f.decode((qa_root / 'download-browser/BROWSER.json').read_bytes())
        f.require(browser['state'] == downloads['state'] == 'pass' and len(browser['cases']) == 6
                  and len(downloads['cases']) == 12, 'Browser cases failed or incomplete')
        f.require(browser['network_requests'] == 0 and browser['script_errors'] == [] and downloads['errors'] == [], 'Browser errors')
        for row in downloads['files']:
            f.checked_file(ROOT, row)
        record = f.decode((edition / 'EDITION.json').read_bytes())
        for row in record['files']:
            f.checked_file(edition, row)
        f.require([r['sha256'] for r in record['files']] == [r['sha256'] for r in files], 'Hosted exports differ')
        report, _, _ = f.validate(work)
        evidence = [edition / 'EDITION.json', edition / 'FORMAT_VERIFICATION.json',
                    qa_root / 'reader-browser/browser-check.json', qa_root / 'download-browser/BROWSER.json',
                    *[work / name for name in ('FINAL_EXPORT_RECEIPT.json', 'VISUAL_REVIEW.json',
                      'ISOLATED_REPLAY_RECEIPT.json', 'FORMAT_LOCATORS_VALIDATION.json')]]
        proof = {'schema': 'public-course-format-integration-validation/1',
                 'state': 'local_checks_pass_public_readback_pending', 'course_id': m['course_id'],
                 'source_commit': m['public_source']['commit'], 'documents': len(m['units']),
                 'main_lessons': report['lessons'], 'prerequisite_chapters': report['prerequisite_chapters'],
                 'supplements': report['editorial_supplements'], 'pdf_pages': report['pdf']['pages'],
                 'named_locations': len(report['native_locations']),
                 'ordered_formula_regions': report['epub']['formula_regions'],
                 'source_zip_members': report['source_closure']['members'],
                 'reader_browser_cases': 6, 'programme_download_browser_cases': 12,
                 'rebuild_scope': 'Fresh isolated rebuild of this refreshed source ZIP: PDF, TeX and EPUB byte-identical.',
                 'source_prose_or_mathematics_changed': False, 'core_course_counts_changed': False,
                 'evidence': [{'path': p.relative_to(ROOT).as_posix(), **f.identity(p)} for p in evidence]}
        (edition / 'INTEGRATION_VALIDATION.json').write_bytes(f.json_bytes(proof))
        return {key: value for key, value in proof.items() if key != 'evidence'}
    if phase == 'receipt':
        qa, epub, replay, check, visual = [load(name) for name in
            ('EXPORT_CONTENT_QA.json', 'EPUB_RENDER_QA.json', 'ISOLATED_REPLAY_RECEIPT.json',
             'qa/EPUBCHECK_FINAL.json', 'VISUAL_REVIEW.json')]
        f.require(qa['source_manifest']['sha256'] == fact('SOURCE_MANIFEST.json')['sha256'], 'Stale content QA')
        f.require(qa['pdf']['sha256'] == files[0]['sha256'] and qa['epub']['sha256'] == files[3]['sha256'], 'Stale format QA')
        f.require(epub['epub']['sha256'] == files[3]['sha256'], 'Stale EPUB geometry check')
        f.require(all(check['checker'][key] == 0 for key in ('nFatal', 'nError', 'nWarning')), 'EPUBCheck failed')
        f.require(len(epub['chapter_checks']) == 2 * len(m['units']) and all(
            r['document_width'] <= r['viewport'] and r['zero_height_math'] == r['mathml_errors'] == 0
            for r in epub['chapter_checks']), 'EPUB geometry incomplete or failed')
        f.require(replay['state'] == 'PASS' and replay['source_zip_sha256'] == files[2]['sha256'], 'Source replay failed or stale')
        f.require(len(replay['outputs']) == 3 and all(row['byte_identical'] and
            row['original_sha256'] == row['replay_sha256'] == next(
                r['sha256'] for r in files if Path(r['path']).name == row['name'])
            for row in replay['outputs']), 'Replay does not bind final outputs')
        f.require(visual['pdf_sha256'] == files[0]['sha256'] and visual['epub_sha256'] == files[3]['sha256']
                  and visual['result'] == 'pass_for_inspected_scope', 'Visual evidence absent or stale')
        comparison = load('PUBLISHED_SOURCE_COMPARISON.json')
        f.require(comparison['pass'] and len(comparison['units']) == len(m['units']), 'Published/source comparison incomplete')
        for u, row in zip(m['units'], comparison['units']):
            f.require(row['unit_id'] == u['id'] and row['editable_source_sha256'] == u['source_sha256'], 'Source comparison mismatch')
        evidence = ['SOURCE_MANIFEST.json', 'REFRESH_INTAKE.json', 'PUBLISHED_SOURCE_COMPARISON.json',
                    'PDF_BUILD_RECEIPT.json', 'EPUB_MATH_SEAL.json', 'EXPORT_CONTENT_QA.json',
                    'EPUB_RENDER_QA.json', 'ISOLATED_REPLAY_RECEIPT.json', 'SOURCE_PACKAGE_RECEIPT.json',
                    'qa/EPUBCHECK_FINAL.json', 'VISUAL_REVIEW.json']
        receipt = {'schema': 'programme-course-export-acceptance/2', 'course_id': m['course_id'],
                   'title': m['title'], 'content_language': m['content_language'],
                   'state': 'exports_validated_preservation_not_yet_verified',
                   'public_source_binding': m['public_source'], 'source_selection_status': m['coverage_note'],
                   'source_lessons': len(m['units']), 'pdf_pages': qa['pdf_pages'],
                   'math_regions': qa['epub_checks']['math_regions'], 'files_in_public_order': files,
                   'rights_notice': m['export']['rights_notice'], 'online_reader': m['upstream_reader'],
                   'programme': m['programme'], 'source_mathematics_changed': False,
                   'format_conversion_ai': 'OpenAI Codex - GPT-6 Astra, Ultra effort',
                   'human_review_claimed': False, 'visual_review': visual,
                   'checks': {'ordered_source_prose_and_math': 'PASS for every selected unit',
                              'epubcheck': '5.4.0: zero fatal/error/warning',
                              'offline_internal_links': qa['epub_checks']['internal_links'],
                              'pdf_embedded_fonts': qa['pdf_fonts_embedded'],
                              'pdf_bookmarks': qa['pdf_bookmarks'],
                              'isolated_source_replay': 'PDF, complete TeX and EPUB byte-identical',
                              'epub_geometry_cases': len(epub['chapter_checks'])},
                   'evidence': [fact(name) for name in evidence],
                   'limits': ['Source-preserving format conversion, not new mathematical or linguistic review.',
                              'PDF is untagged; MathML EPUB has structural checks, not assistive-technology certification.',
                              'This is the exact pinned source edition; the online course may continue changing.',
                              'Public preservation is separately verified after publication.']}
        (work / 'FINAL_EXPORT_RECEIPT.json').write_bytes(f.json_bytes(receipt))
        return {'state': receipt['state'], 'pdf_pages': qa['pdf_pages'], 'receipt': fact('FINAL_EXPORT_RECEIPT.json')}
    receipt, locators, validation = [load(name) for name in
        ('FINAL_EXPORT_RECEIPT.json', 'FORMAT_LOCATORS.json', 'FORMAT_LOCATORS_VALIDATION.json')]
    f.require(validation['result'] == 'PASS' and validation['index'] == fact('FORMAT_LOCATORS.json'), 'Locator validation stale')
    f.require(receipt['files_in_public_order'] == files, 'Acceptance no longer binds current exports')
    evidence = [fact(name) for name in ('SOURCE_MANIFEST.json', 'REFRESH_INTAKE.json',
        'PUBLISHED_SOURCE_COMPARISON.json', 'FINAL_EXPORT_RECEIPT.json', 'FORMAT_LOCATORS.json',
        'FORMAT_LOCATORS_VALIDATION.json', 'ISOLATED_REPLAY_RECEIPT.json', 'BUILD.txt')]
    counts = {key: sum(u['selection_kind'] == kind for u in m['units']) for key, kind in f.COVERAGE_KINDS.items()}
    handoff = {'schema': 'programme-current-public-course-format-handoff/1', 'course_id': m['course_id'],
               'title': m['title'], 'state': 'format_validated_for_existing_integrator_publication',
               'source': m['public_source'],
               'coverage': {**counts, 'pdf_pages': receipt['pdf_pages'], 'formula_regions': receipt['math_regions'],
                            'native_format_locators': locators['counts']['native_anchors']},
               'rights': m['export']['rights_notice'], 'files_in_public_order': files,
               'pdf_preview': files[0]['path'], 'evidence': evidence,
               'reading_url': m['upstream_reader'], 'programme_url': m['programme'],
               'limits': receipt['limits']}
    (work / 'HANDOFF.json').write_bytes(f.json_bytes(handoff))
    report, _, _ = f.validate(work)
    return {'state': 'refreshed_formats_validated', 'pdf_pages': report['pdf']['pages'],
            'documents': len(report['entry_routes']), 'native_locations': len(report['native_locations']),
            'handoff': fact('HANDOFF.json')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--phase', choices=('receipt', 'handoff', 'integration'), required=True)
    parser.add_argument('--qa', type=Path)
    args = parser.parse_args()
    print(json.dumps(seal(args.work, args.phase, args.qa)))
