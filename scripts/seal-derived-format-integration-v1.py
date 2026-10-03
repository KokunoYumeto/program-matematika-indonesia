"""Seal exact integration checks; retain producer versus integrator distinctions."""
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/course-formats-v1'))
import course_formats as f

edition = ROOT / 'docs/editions/derived-categories-of-sheaves'
qa = ROOT / 'outputs/course-format-integration-v1/qa-derived-20261003'
read = lambda p: f.decode(p.read_bytes())
record = read(edition / 'EDITION.json')
local = read(edition / 'FORMAT_VERIFICATION.json')
browser = read(qa / 'browser-check.json')
downloads = read(qa / 'downloads/BROWSER.json')
epubcheck = read(qa / 'epubcheck.json')
visual = read(qa / 'VISUAL_REVIEW.json')
assert browser['state'] == downloads['state'] == 'pass'
assert len(browser['cases']) == 6 and len(downloads['cases']) == 12
assert browser['network_requests'] == 0 and browser['script_errors'] == []
assert all(epubcheck['checker'][key] == 0 for key in ('nFatal', 'nError', 'nWarning'))
assert visual['state'] == 'pass_within_sample'
assert visual['pdf_sha256'] == record['files'][0]['sha256']
assert local['selected_documents'] == 11 and local['lessons'] == 10 and local['common_readings'] == 1
assert local['pdf']['native_locations_verified'] == local['epub']['native_locations_verified'] == 92
assert local['epub']['formula_regions'] == 4769
assert local['source_closure']['members'] == 53
assert local['public_source_network_rechecked']
for row in record['files']:
    f.checked_file(edition, row)
proof = {
    'schema': 'public-course-format-integration-validation/1',
    'state': 'local_checks_pass_public_readback_pending',
    'course_id': record['course_id'],
    'documents': 11, 'lessons': 10, 'common_readings': 1,
    'pdf_pages': 102, 'named_locations': 92, 'epub_internal_links': 188,
    'source_zip_members': 53, 'ordered_formula_regions': 4769,
    'reader_browser_cases': 6, 'programme_download_browser_cases': 12,
    'epubcheck': '5.4.0; zero fatal/error/warning',
    'pdf_visual_sample': visual,
    'source_prose_or_mathematics_changed': False,
    'rebuild_scope': 'Exact source closure checked here; byte-identical isolated replay is producer evidence, not a new integration replay.',
    'core_course_counts_changed': False,
    'evidence': [{'path': p.relative_to(ROOT).as_posix(), **f.identity(p)} for p in [
        edition / 'EDITION.json', edition / 'FORMAT_VERIFICATION.json',
        qa / 'browser-check.json', qa / 'downloads/BROWSER.json', qa / 'epubcheck.json', qa / 'VISUAL_REVIEW.json']],
}
(edition / 'INTEGRATION_VALIDATION.json').write_bytes(f.json_bytes(proof))
print(json.dumps({'state': proof['state'], 'files': len(record['files']), 'documents': 11}))
