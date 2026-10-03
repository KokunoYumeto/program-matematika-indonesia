"""Prepare an additive public-course reader from exact, validated native exports.

No producer mutations, mathematical edits, remote writes or new course admission.
OpenAI Codex - GPT-6 Astra, Ultra effort: integration code and validation.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/course-formats-v1'))
import course_formats as f


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('intake', type=Path)
    parser.add_argument('--slug', required=True)
    args = parser.parse_args()
    f.require(args.slug == f.safe_name(args.slug) and '/' not in args.slug, 'Single canonical slug required')
    report, manifest, routes = f.validate(args.intake)
    f.require('public_source_binding' in report, 'Public-source adapter required')
    source = report['public_source_binding']
    # Anonymous bounded readback of the original public archive. Not the exports.
    response = requests.get(source['archive_url'], timeout=(15, 45), stream=True,
                            headers={'User-Agent': 'Open-Courses-format-source-readback'})
    f.require(response.status_code == 200, 'Public source archive unavailable')
    data = bytearray()
    for chunk in response.iter_content(65536):
        data.extend(chunk)
        f.require(len(data) <= source['archive_bytes'], 'Public source archive size changed')
    f.require(len(data) == source['archive_bytes'] and f.digest(data) == source['archive_sha256'],
              'Public archive differs from the delivered source witness')
    report['public_source_network_rechecked'] = True
    destination = ROOT / 'docs/editions' / args.slug
    if destination.exists():
        for row in report['files']:
            f.require(f.identity(destination / 'files' / Path(row['path']).name) ==
                      {'bytes': row['bytes'], 'sha256': row['sha256']}, 'Existing edition file differs')
        for locale in f.COPY:
            (destination / f'index.{locale}.html').write_text(
                f.reader_html(report, manifest, routes, locale), encoding='utf-8', newline='\n')
        (destination / 'index.html').write_text(
            f.reader_html(report, manifest, routes, 'en'), encoding='utf-8', newline='\n')
        (destination / 'FORMAT_VERIFICATION.json').write_bytes(f.json_bytes(report))
    else:
        f.assemble(args.intake, destination, report, manifest, routes)
    edition = {'schema': 'public-course-portable-edition/1', 'course_id': report['course_id'],
               'title': manifest['title'], 'content_language': manifest['content_language'],
               'source': source, 'source_archive_anonymous_hash_check': True,
               'source_review_status': manifest['status'], 'coverage': manifest['coverage_note'],
               'licence': manifest['export']['rights_notice'], 'authorship': manifest['source_author'],
               'format_conversion': manifest['conversion_author'],
               'integration': 'OpenAI Codex - GPT-6 Astra, Ultra effort',
               'source_mathematics_changed': False, 'new_translation': False,
               'documents': len(routes), 'lessons': report['lessons'],
               'common_readings': report['common_readings'], 'pdf_pages': report['pdf']['pages'],
               'native_locations': len(report['native_locations']), 'pdf_tagged': report['pdf']['tagged'],
               'files': [{**row, 'path': 'files/' + Path(row['path']).name} for row in report['files']],
               'online_navigation': report['online_navigation'],
               'limits': ['Integration and formatting do not add mathematical or human review.',
                          'Local source verification is not public verification of these new exports.']}
    (destination / 'EDITION.json').write_bytes(f.json_bytes(edition))
    print(json.dumps({'state': 'source_verified_reader_prepared',
                      'path': destination.relative_to(ROOT).as_posix(),
                      'documents': len(routes), 'native_locations': len(report['native_locations']),
                      'download_bytes': sum(row['bytes'] for row in report['files'])}))


if __name__ == '__main__':
    main()
