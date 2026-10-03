"""Freeze a newer public edition for the existing source-preserving exporter.

Read-only upstream access; only a new directory in this checkout's integration
staging is written. No source-owner mutations or inherited QA claims.
OpenAI Codex - GPT-6 Astra, Ultra effort: refresh adapter and validation.
"""
import argparse
import copy
import io
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

import requests
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/course-formats-v1'))
import course_formats as f


def fetch(url, limit=8 * 1024 * 1024):
    with requests.get(url, timeout=(15, 45), stream=True,
                      headers={'User-Agent': 'Open-Courses-source-refresh/1'}) as response:
        response.raise_for_status()
        data = bytearray()
        for chunk in response.iter_content(65536):
            data.extend(chunk)
            f.require(len(data) <= limit, 'Bounded response exceeded: ' + url)
    return bytes(data)


def prepare(prior, work, commit):
    prior = prior.resolve()
    work = work.resolve()
    boundary = (ROOT / 'outputs/course-format-integration-v1').resolve()
    f.require(work.is_relative_to(boundary) and work != boundary and not work.exists(),
              'Require a new owned integration-staging directory')
    # Validate the previous delivered source and its exact editable ZIP before
    # using its parsing/build closure. Its final QA does NOT transfer forward.
    old_report, old, _ = f.validate(prior)
    public = old['public_source']
    match = re.fullmatch(r'https://github.com/([\w.-]+)/([\w.-]+)', public['repository'])
    f.require(match, 'Explicit GitHub public repository required')
    owner, repo = match.groups()
    info = json.loads(fetch(f'https://api.github.com/repos/{owner}/{repo}/commits/{commit}'))
    commit = info['sha']
    f.require(re.fullmatch('[0-9a-f]{40}', commit), 'Full immutable source commit required')
    archive_path = 'docs/downloads/' + old['export']['slug'] + '.zip'
    pinned_url = f'https://raw.githubusercontent.com/{owner}/{repo}/{commit}/{archive_path}'
    raw = fetch(pinned_url)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = f.archive_inventory(archive)
        f.require(sum(x.file_size for x in archive.infolist()) <= 24 * 1024 * 1024,
                  'Unpacked source exceeds bound')
        f.require(archive.testzip() is None, 'Source archive CRC failure')
        bundle = {name: archive.read(name) for name in names}
    cid = old['course_id']
    prefix = 'courses/' + cid + '/'

    def exact(relative):
        return bundle[prefix + f.safe_name(relative)]

    course_raw = exact('course.json')
    course = json.loads(course_raw)
    provenance_raw = exact('provenance.json')
    provenance = json.loads(provenance_raw)
    rows = [dict(row, kind='lesson') for row in course['lessons']]
    rows += [dict(row, id=PurePosixPath(row['portable_source']).stem,
                  source=row['portable_source'], kind='prerequisite')
             for row in course.get('dependencies', [])]
    rows += [dict(row, id=PurePosixPath(row['source']).stem, kind='supplement')
             for row in course.get('supplements', [])]
    f.require([(r['id'], r['kind']) for r in rows] ==
              [(u['id'], u['selection_kind']) for u in old['units']],
              'Course selection changed; admit the new scope explicitly before refresh')
    data = {}
    for record in old['files']:
        data[record['path']] = f.checked_file(prior, record).read_bytes()
    for key in ('pdf_layout', 'epub_inline_layout', 'export_compatibility'):
        if old.get(key):
            record = old[key]
            data[record['path']] = f.checked_file(prior, record).read_bytes()
    data['authority/public-course.json'] = course_raw
    data['authority/public-provenance.json'] = provenance_raw
    units = []
    changes = []
    for row, previous in zip(rows, old['units']):
        source = exact(row['source'])
        f.require(f.digest(source) == row['sha256'], 'Native source/metadata mismatch')
        reader = exact(row['reader'])
        page = html.document_fromstring(reader)
        articles = page.xpath('//article[contains(concat(" ",normalize-space(@class)," ")," lesson ")]')
        f.require(len(articles) == 1, 'One complete public lesson article required')
        headings = articles[0].xpath('./h1')
        f.require(len(headings) == 1 and headings[0].get('id'), 'Native title and ID missing')
        unit = copy.deepcopy(previous)
        unit.update(title=headings[0].text_content(), source_origin=row['source'],
                    source_sha256=f.digest(source), bytes=len(source),
                    heading_anchors=row.get('heading_anchors', []), component_licence=row['license'])
        witness = unit['published_html']
        witness.update(bytes=len(reader), sha256=f.digest(reader),
                       reader_path='docs/' + prefix + row['reader'], native_h1_id=headings[0].get('id'))
        data[unit['source']] = source
        data[witness['path']] = reader
        units.append(unit)
        changes.append({'id': unit['id'], 'kind': unit['selection_kind'],
                        'previous_sha256': previous['source_sha256'],
                        'current_sha256': unit['source_sha256'],
                        'changed': previous['source_sha256'] != unit['source_sha256']})
    # The exact component licence is current public source, never a generated
    # substitute or inherited assertion about all components being CC0.
    for appendix in old.get('reading_appendices', []):
        if appendix['path'] == 'licences/design-science-license.txt':
            data[appendix['path']] = exact('src/licenses/design-science-license.txt')
    manifest = copy.deepcopy(old)
    manifest['state'] = 'source_frozen_not_export_validated'
    manifest['edition_id'] = cid + '.public.' + commit[:12] + '.20261003'
    manifest['units'] = units
    manifest['upstream_declared_licence'] = provenance['licensing']
    manifest['public_source'].update(commit=commit, archive_url=pinned_url,
                                     current_archive_url=public.get('current_archive_url', public['archive_url']),
                                     archive_bytes=len(raw), archive_sha256=f.digest(raw),
                                     anonymous_same_bytes=True)
    manifest['published_collection']['published_files'] = sorted('docs/' + n for n in bundle if n.startswith('courses/'))
    manifest['files'] = [{**row, 'bytes': len(data[row['path']]), 'sha256': f.digest(data[row['path']])}
                         for row in old['files']]
    manifest['refresh'] = {'previous_manifest_sha256': f.digest((prior / 'SOURCE_MANIFEST.json').read_bytes()),
                           'previous_source_commit': public['commit'],
                           'source_commit': commit, 'source_commit_date': info['commit']['committer']['date'],
                           'changes': changes,
                           'validation': 'Fresh prose/math, layout, EPUB, PDF and replay checks required; previous receipts do not apply.'}
    # Reuse only the self-contained build closure, not prior rendered exports
    # or checks. Existing ZIP entries are hash-validated by f.validate above.
    source_zip = next(r for r in old_report['files'] if r['path'].endswith('-source.zip'))
    with zipfile.ZipFile(prior / source_zip['path']) as archive:
        for name in f.archive_inventory(archive):
            if name.startswith(('scripts/', 'vendor/')):
                data[name] = archive.read(name)
    build = (prior / 'BUILD.txt').read_text(encoding='utf-8')
    build = build.replace(public['commit'], commit)
    build += '\nSource refresh: exact public commit ' + commit + '. All format validation is rerun for this edition; earlier edition receipts are not inherited.\n'
    data['BUILD.txt'] = build.encode('utf-8')
    data['SOURCE_MANIFEST.json'] = f.json_bytes(manifest)
    receipt = {'schema': 'public-course-source-refresh/1', 'source_frozen': True,
               'source_commit': commit, 'source_archive_url': pinned_url,
               'source_archive_bytes': len(raw), 'source_archive_sha256': f.digest(raw),
               'selected_units': len(units), 'changed_units': sum(x['changed'] for x in changes),
               'changes': changes, 'previous_qa_inherited': False,
               'source_manifest_sha256': f.digest(data['SOURCE_MANIFEST.json'])}
    data['REFRESH_INTAKE.json'] = f.json_bytes(receipt)
    work.mkdir(parents=True)
    for name, contents in data.items():
        target = f.confined(work, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(contents)
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prior', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--commit', default='main')
    args = parser.parse_args()
    print(json.dumps(prepare(args.prior, args.work, args.commit)))
