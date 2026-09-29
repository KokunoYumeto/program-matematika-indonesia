"""Read-only audit of the exact C120 native reader; writes central evidence only.

No producer mutation, book copy, credential use or concurrent network calls.
The online pass compares every deployed reader file, not just its landing page.
"""
import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import time
import runpy
from urllib.parse import unquote, urljoin, urlsplit

from bs4 import BeautifulSoup
import requests

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT.parent / 'mathematical-modeling-nonlinear-dynamics-id'
BASE = ROOT / 'backend/course-capsule-v1/adapters/c120-delivery-v1'
READER = 'https://kokunoyumeto.github.io/mathematical-modeling-nonlinear-dynamics-id/'
PDF = '01_Pengantar_Pemodelan_Matematika_Edisi_Bahasa_Indonesia_Lengkap.pdf'
MAP = 'backend/course-capsule-v1/adapters/c120-capability-v1/data/learning-map.json'


def identity(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def collect():
    """Mirror the native Pages workflow without copying any source files."""
    paths = {p.relative_to(NATIVE / 'build/reader').as_posix(): p
             for p in sorted((NATIVE / 'build/reader').rglob('*')) if p.is_file()}
    paths.update({'index.html': NATIVE / 'site/index.html',
                  'site.css': NATIVE / 'site/site.css',
                  'LICENSE.md': NATIVE / 'LICENSE.md',
                  PDF.removeprefix('01_'): NATIVE / 'output/pdf' / PDF})
    assert len(paths) == 253, 'Changed deployment boundary requires investigation'
    assert all(p.resolve().is_relative_to(NATIVE.resolve()) for p in paths.values())
    return paths


def analyze(paths, learning_map):
    html = {key: BeautifulSoup(path.read_bytes(), 'html.parser')
            for key, path in paths.items() if key.endswith('.html')}
    expected = learning_map['route']['unit_ids']
    assert len(expected) == len(set(expected)) == 26
    assert set(html) == {'index.html', *(unit + '/index.html' for unit in expected)}
    ids = {key: [tag['id'] for tag in soup.select('[id]')] for key, soup in html.items()}
    faults, pages, external_resources = [], [], []
    links = 0
    for key, soup in html.items():
        metrics = {'path': key, 'lang': soup.html.get('lang'),
                   'main': len(soup.select('main')), 'h1': len(soup.select('h1')),
                   'mathml': len(soup.select('math')), 'images': len(soup.select('img'))}
        if metrics['lang'] != 'id-ID' or metrics['main'] != 1 or metrics['h1'] != 1:
            faults.append({'path': key, 'kind': 'language_or_landmark'})
        duplicates = [v for v, count in Counter(ids[key]).items() if count > 1]
        if duplicates:
            faults.append({'path': key, 'kind': 'duplicate_ids', 'ids': duplicates})
        for image in soup.select('img'):
            if not image.has_attr('alt'):
                faults.append({'path': key, 'kind': 'missing_alt', 'src': image.get('src')})
        for math in soup.select('math'):
            if not math.select_one('annotation[encoding="application/x-tex"]'):
                faults.append({'path': key, 'kind': 'math_source_annotation_missing'})
        for tag in soup.select('[href], [src]'):
            for attr in ('href', 'src'):
                if not tag.has_attr(attr):
                    continue
                href = tag[attr]
                absolute = urljoin(READER + key, href)
                if not absolute.startswith(READER):
                    if attr == 'src' or tag.name in ('script', 'link') and 'stylesheet' in tag.get('rel', []):
                        external_resources.append({'path': key, 'tag': tag.name, 'url': absolute})
                    continue
                target = urlsplit(absolute)
                relative = unquote(target.path[len(urlsplit(READER).path):])
                if not relative or relative.endswith('/'):
                    relative += 'index.html'
                links += 1
                if relative not in paths:
                    faults.append({'path': key, 'kind': 'missing_local_target', 'href': href})
                elif target.fragment and relative in ids and unquote(target.fragment) not in ids[relative]:
                    faults.append({'path': key, 'kind': 'missing_fragment', 'href': href})
        pages.append(metrics)
    landing_units = {urlsplit(a.get('href', '')).path.rstrip('/')
                     for a in html['index.html'].select('a[href]')}
    assert set(expected).issubset(landing_units)
    styles = [key for key in paths if key.endswith('.css')]
    print_styles = [key for key in styles if '@media print' in paths[key].read_text(encoding='utf-8')]
    return {'state': 'pass' if not faults else 'findings', 'unit_ids': expected,
            'pages': pages, 'html_count': len(html), 'unit_count': 26,
            'local_links_checked': links, 'mathml_count': sum(p['mathml'] for p in pages),
            'image_count': sum(p['images'] for p in pages),
            'css_count': len(styles), 'print_css_paths': print_styles,
            'external_runtime_resources': external_resources, 'findings': faults,
            'scope': 'Structural HTML, source MathML annotations and local-link checks; not WCAG certification, rendered PDF QA or a semantic translation audit.'}


class BytesWitness:
    def __init__(self, data):
        self.data = data

    def read_bytes(self):
        return self.data

    def read_text(self, encoding='utf-8'):
        return self.data.decode(encoding)


def blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def online_pinned(paths, manifest, learning_map):
    """Published Git blobs govern delivery; local/native differences stay explicit."""
    commit = 'cf1f7b2d7374818d2f0f48c899addc7c83db3083'
    tree_sha = '5c568732d20a6d21813c2d0afa2a3377b334a8f0'
    session = requests.Session()
    session.trust_env = False
    session.auth = None
    session.headers['User-Agent'] = 'C120-reader-integrity-audit/1'
    last = [0.0]

    def fetch(url):
        time.sleep(max(0, 2.05 - (time.monotonic() - last[0])))
        last[0] = time.monotonic()
        response = session.get(url, timeout=(15, 60))
        response.raise_for_status()
        return response.content

    tree_path = BASE / 'published-tree.json'
    tree_url = f'https://api.github.com/repos/KokunoYumeto/mathematical-modeling-nonlinear-dynamics-id/git/trees/{tree_sha}?recursive=1'
    if not tree_path.exists():
        tree = json.loads(fetch(tree_url))
        assert tree['sha'] == tree_sha and tree['truncated'] is False
        selected = [r for r in tree['tree'] if r['type'] == 'blob' and (
            r['path'].startswith('build/reader/') or r['path'] in {
                'site/index.html', 'site/site.css', 'LICENSE.md', 'output/pdf/' + PDF})]
        write(tree_path, {'commit': commit, 'tree': tree_sha, 'url': tree_url,
                          'anonymous': True, 'files': selected})
    tree = json.loads(tree_path.read_bytes())
    assert tree['commit'] == commit and tree['tree'] == tree_sha
    git_files = {r['path']: r for r in tree['files']}
    assert set(git_files) == {r['native_path'] for r in manifest['files']}
    old = json.loads((BASE / 'public-readback.json').read_bytes()) if (BASE / 'public-readback.json').exists() else {'files': []}
    reuse = {r['path']: r for r in old['files']}
    target = BASE / 'public-git-readback.json'
    receipt = {'schema': 'c120-delivery-public-git-readback/1', 'state': 'in_progress',
               'commit': commit, 'tree': tree_sha, 'anonymous': True,
               'ambient_credentials_disabled': True, 'files': [], 'failures': [],
               'input_manifest': identity((BASE / 'input-manifest.json').read_bytes()),
               'published_tree': identity(tree_path.read_bytes())}
    if target.exists():
        receipt = json.loads(target.read_bytes())
        assert receipt['input_manifest'] == identity((BASE / 'input-manifest.json').read_bytes())
        assert receipt['commit'] == commit and receipt['tree'] == tree_sha
        reuse.update({r['path']: r for r in receipt['files']})
    confirmed = {r['path']: r for r in receipt['files']}
    attempts = Counter(r['path'] for r in receipt['failures'])
    witnesses = dict(paths)
    html_deltas = []
    for row in manifest['files']:
        key = row['path']
        git = git_files[row['native_path']]
        local = paths[key].read_bytes()
        if key in reuse and blob_sha(local) == git['sha'] and identity(local) == {k: reuse[key][k] for k in ['bytes', 'sha256']}:
            confirmed[key] = {**reuse[key], 'git_blob': git['sha'], 'local_relation': 'exact_bytes'}
            continue
        if key in confirmed and not key.endswith(('.html', '.css')):
            continue
        if attempts[key] >= 2:
            continue
        try:
            body = fetch(READER + key)
            assert len(body) == git['size'] and blob_sha(body) == git['sha'], 'Pages differs from pinned Git blob'
            witnesses[key] = BytesWitness(body)
            relation = 'exact_bytes' if body == local else 'different_bytes'
            if body != local and body.replace(b'\r\n', b'\n') == local.replace(b'\r\n', b'\n'):
                relation = 'line_endings_only'
            if key.endswith('.html'):
                live_dom, local_dom = [BeautifulSoup(b, 'html.parser') for b in [body, local]]
                main_equal = str(live_dom.select_one('main')) == str(local_dom.select_one('main'))
                html_deltas.append({'path': key, 'main_dom_equal': main_equal,
                                    'local': identity(local), 'published': identity(body)})
                assert main_equal, 'Published/local mathematical main DOM differs'
                if body != local:
                    relation = 'same_main_dom_different_wrapper_or_line_endings'
            confirmed[key] = {'path': key, 'url': READER + key, **identity(body),
                              'status': 200, 'git_blob': git['sha'], 'local_relation': relation,
                              'verified_at': datetime.now(timezone.utc).isoformat()}
        except (requests.RequestException, AssertionError) as error:
            receipt['failures'].append({'path': key, 'error': str(error), 'attempt': attempts[key] + 1})
        receipt['files'] = sorted(confirmed.values(), key=lambda r: r['path'])
        write(target, receipt)
        if len(confirmed) % 25 == 0:
            print(f'Pinned public files verified: {len(confirmed)}/253', flush=True)
    receipt['files'] = sorted(confirmed.values(), key=lambda r: r['path'])
    receipt['remaining'] = sorted(set(paths) - set(confirmed))
    if not receipt['remaining']:
        audit = analyze(witnesses, learning_map)
        audit['html_comparisons'] = html_deltas
        audit['commit'] = commit
        audit['tree'] = tree_sha
        write(BASE / 'public-structural-audit.json', audit)
        assert audit['state'] == 'pass', 'Public structural findings need repair'
        receipt['structural_audit'] = identity((BASE / 'public-structural-audit.json').read_bytes())
    receipt['state'] = 'pass' if not receipt['remaining'] else 'incomplete'
    receipt['verified_bytes'] = sum(r['bytes'] for r in receipt['files'])
    receipt['finished_at'] = datetime.now(timezone.utc).isoformat()
    write(target, receipt)
    print(json.dumps({'state': receipt['state'], 'files': len(confirmed), 'remaining': receipt['remaining']}), flush=True)
    if receipt['remaining']:
        raise SystemExit(1)


def deployed_seed(pinned, manifest_identity, previous=None):
    """Optional verified cache, never a prerequisite for a fresh public audit."""
    if previous is None:
        return {'state': 'fresh', 'commit': pinned['commit'], 'tree': pinned['tree'], 'files': []}
    assert previous['state'] in ('pass', 'incomplete'), 'Never overlap a live predecessor audit'
    assert previous['commit'] == pinned['commit'] and previous['tree'] == pinned['tree']
    assert previous['input_manifest'] == manifest_identity, 'Do not reuse evidence after native input drift'
    assert previous['anonymous'] and previous['ambient_credentials_disabled']
    return previous


def online_deployed(paths, manifest, learning_map):
    """Replay the inspected native deployment's navigation and manifest transforms."""
    pinned = json.loads((BASE / 'published-tree.json').read_bytes())
    previous_path = BASE / 'public-git-readback.json'
    previous = json.loads(previous_path.read_bytes()) if previous_path.exists() else None
    old = deployed_seed(pinned, identity((BASE / 'input-manifest.json').read_bytes()), previous)
    commit, tree_sha = old['commit'], old['tree']
    native = {r['path']: r for r in pinned['files']}
    local_index = {r['path']: r for r in manifest['files']}
    session = requests.Session()
    session.trust_env = False
    session.auth = None
    last = [0.0]

    def fetch(url):
        time.sleep(max(0, 2.05 - (time.monotonic() - last[0])))
        last[0] = time.monotonic()
        response = session.get(url, timeout=(15, 60))
        response.raise_for_status()
        return response.content

    raw_base = f'https://raw.githubusercontent.com/KokunoYumeto/mathematical-modeling-nonlinear-dynamics-id/{commit}/'
    full_tree = json.loads(fetch(pinned['url']))
    assert full_tree['sha'] == tree_sha and full_tree['truncated'] is False
    git = {r['path']: r for r in full_tree['tree'] if r['type'] == 'blob'}
    deployment_sources = []
    for path in ['.github/workflows/pages.yml', 'program-navigation.json', 'scripts/program_navigation.py', 'scripts/reseal_reader_manifests.py']:
        body = fetch(raw_base + path)
        assert blob_sha(body) == git[path]['sha'] and len(body) == git[path]['size']
        out = BASE / 'deployment' / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(body)
        deployment_sources.append({'path': path, 'git_blob': git[path]['sha'], **identity(body)})
    # This pinned, completely inspected script only defines a pure fragment
    # builder and a guarded CLI. No CLI is run and no producer path is passed.
    nav = runpy.run_path(str(BASE / 'deployment/scripts/program_navigation.py'), run_name='c120_pinned_navigation_reference')
    config = json.loads((BASE / 'deployment/program-navigation.json').read_bytes())
    fragment = nav['fragment'](config)
    confirmed = {r['path']: dict(r) for r in old['files']}
    witnesses = dict(paths)
    comparisons, transformations, packages = [], [], []
    receipt = {'schema': 'c120-delivery-deployed-readback/1', 'state': 'in_progress',
               'commit': commit, 'tree': tree_sha, 'anonymous': True, 'ambient_credentials_disabled': True,
               'input_manifest': identity((BASE / 'input-manifest.json').read_bytes()),
               'published_tree': identity((BASE / 'published-tree.json').read_bytes()),
               'deployment_sources': deployment_sources, 'files': [], 'failures': []}
    target = BASE / 'deployed-readback.json'
    for row in manifest['files']:
        key = row['path']
        if key in confirmed and not key.endswith(('.html', '.css')):
            if confirmed[key]['local_relation'] == 'different_bytes':
                confirmed[key]['local_relation'] = 'published_source_version'
            continue
        try:
            body = fetch(READER + key)
            witnesses[key] = BytesWitness(body)
            source = native[row['native_path']]
            transform = None
            if key.endswith('.html') or key.endswith('PACKAGE_MANIFEST.tsv'):
                source_body = fetch(raw_base + row['native_path'])
                assert blob_sha(source_body) == source['sha'] and len(source_body) == source['size']
                if key.endswith('.html'):
                    text = source_body.decode('utf-8-sig')
                    if nav['BLOCK_RE'].search(text):
                        expected = nav['BLOCK_RE'].sub(fragment, text, count=1)
                    else:
                        match = nav['BODY_RE'].search(text)
                        assert match
                        expected = text[:match.end()] + '\n' + fragment + text[match.end():]
                    assert body == expected.encode(), 'Native deployment HTML replay differs'
                    main_same = str(BeautifulSoup(body, 'html.parser').select_one('main')) == str(BeautifulSoup(paths[key].read_bytes(), 'html.parser').select_one('main'))
                    comparisons.append({'path': key, 'main_dom_equal': main_same,
                                        'local': identity(paths[key].read_bytes()), 'published': identity(body)})
                    assert main_same, 'Mathematical main DOM differs from integrated native witness'
                    transform = 'native_navigation_injection'
                else:
                    packages.append((key, source_body, body))
                    transform = 'native_manifest_reseal_pending'
                transformations.append({'path': key, 'source_git_blob': source['sha'],
                                        'source': identity(source_body), 'deployed': identity(body), 'transform': transform})
            else:
                assert blob_sha(body) == source['sha'] and len(body) == source['size'], 'Non-transformed file differs from pinned Git'
            relation = 'exact_bytes' if body == paths[key].read_bytes() else 'published_source_version'
            if key.endswith('.html'):
                relation = 'same_main_dom_native_deployment_replay'
            confirmed[key] = {'path': key, 'url': READER + key, **identity(body),
                              'status': 200, 'git_blob': source['sha'], 'local_relation': relation,
                              'deployment_transform': transform or 'identity',
                              'verified_at': datetime.now(timezone.utc).isoformat()}
        except (requests.RequestException, AssertionError) as error:
            receipt['failures'].append({'path': key, 'error': str(error)})
        receipt['files'] = sorted(confirmed.values(), key=lambda r: r['path'])
        write(target, receipt)
    for key, source_body, body in packages:
        rows = list(csv.DictReader(io.StringIO(source_body.decode('utf-8-sig')), delimiter='\t'))
        rebuilt = []
        for row in rows:
            path = (PurePosixPath(key).parent / row['path']).as_posix()
            assert '..' not in PurePosixPath(path).parts and path in confirmed
            value = confirmed[path]
            rebuilt.append({'path': row['path'], 'bytes': str(value['bytes']), 'sha256': value['sha256']})
        buf = io.StringIO(newline='')
        writer = csv.DictWriter(buf, fieldnames=('path', 'bytes', 'sha256'), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rebuilt)
        assert body == buf.getvalue().encode(), f'Manifest does not bind exact deployed bytes: {key}'
        confirmed[key]['deployment_transform'] = 'native_manifest_reseal'
        for transform in transformations:
            if transform['path'] == key:
                transform['transform'] = 'native_manifest_reseal'
                transform['bound_files'] = len(rows)
    audit = analyze(witnesses, learning_map)
    audit.update({'html_comparisons': comparisons, 'commit': commit, 'tree': tree_sha})
    write(BASE / 'deployed-structural-audit.json', audit)
    write(BASE / 'deployment-replay.json', {'state': 'pass' if not receipt['failures'] else 'incomplete',
          'commit': commit, 'tree': tree_sha, 'sources': deployment_sources, 'transformations': transformations})
    receipt['files'] = sorted(confirmed.values(), key=lambda r: r['path'])
    receipt['remaining'] = sorted(set(paths) - set(confirmed))
    receipt['structural_audit'] = identity((BASE / 'deployed-structural-audit.json').read_bytes())
    receipt['deployment_replay'] = identity((BASE / 'deployment-replay.json').read_bytes())
    receipt['state'] = 'pass' if not receipt['remaining'] and not receipt['failures'] and audit['state'] == 'pass' else 'incomplete'
    receipt['verified_bytes'] = sum(r['bytes'] for r in receipt['files'])
    receipt['finished_at'] = datetime.now(timezone.utc).isoformat()
    write(target, receipt)
    print(json.dumps({'state': receipt['state'], 'files': len(confirmed), 'failures': receipt['failures'], 'remaining': receipt['remaining']}), flush=True)
    if receipt['state'] != 'pass':
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--online', action='store_true')
    parser.add_argument('--public-pinned', action='store_true')
    parser.add_argument('--deployed', action='store_true')
    args = parser.parse_args()
    paths = collect()
    map_bytes = (ROOT / MAP).read_bytes()
    result = analyze(paths, json.loads(map_bytes))
    manifest = {'schema': 'c120-delivery-input/1', 'course_id': 'C120',
                'native_root': '04_mirrors/id/mathematical-modeling-nonlinear-dynamics-id',
                'reader': READER, 'learning_map': {'path': MAP, **identity(map_bytes)},
                'files': [{'path': key, 'native_path': value.relative_to(NATIVE).as_posix(),
                           **identity(value.read_bytes())} for key, value in sorted(paths.items())]}
    write(BASE / 'input-manifest.json', manifest)
    write(BASE / 'structural-audit.json', result)
    print(json.dumps({k: result[k] for k in ['state', 'unit_count', 'html_count', 'local_links_checked', 'mathml_count', 'image_count', 'findings']}, ensure_ascii=False), flush=True)
    if args.deployed:
        online_deployed(paths, manifest, json.loads(map_bytes))
        return
    if args.public_pinned:
        online_pinned(paths, manifest, json.loads(map_bytes))
        return
    if not args.online:
        return
    manifest_id = identity((BASE / 'input-manifest.json').read_bytes())
    receipt_path = BASE / 'public-readback.json'
    receipt = {'schema': 'c120-delivery-public-readback/1', 'state': 'in_progress',
               'anonymous': True, 'ambient_credentials_disabled': True,
               'input_manifest': manifest_id, 'files': [], 'failures': []}
    if receipt_path.exists():
        previous = json.loads(receipt_path.read_bytes())
        assert previous['input_manifest'] == manifest_id, 'Do not reuse evidence after native input drift'
        receipt = previous
    done = {row['path'] for row in receipt['files']}
    attempts = Counter(row['path'] for row in receipt['failures'])
    session = requests.Session()
    session.trust_env = False
    session.auth = None
    session.headers['User-Agent'] = 'C120-reader-integrity-audit/1'
    last_start = 0
    for row in manifest['files']:
        if row['path'] in done or attempts[row['path']] >= 2:
            continue
        time.sleep(max(0, 2.05 - (time.monotonic() - last_start)))
        last_start = time.monotonic()
        url = READER + row['path']
        try:
            response = session.get(url, timeout=(15, 60))
            response.raise_for_status()
            actual = identity(response.content)
            assert actual == {k: row[k] for k in ['bytes', 'sha256']}, 'public/local byte mismatch'
            receipt['files'].append({'path': row['path'], 'url': url, **actual,
                                     'status': response.status_code,
                                     'verified_at': datetime.now(timezone.utc).isoformat()})
            done.add(row['path'])
        except (requests.RequestException, AssertionError) as error:
            receipt['failures'].append({'path': row['path'], 'error': str(error),
                                        'attempt': attempts[row['path']] + 1})
        write(receipt_path, receipt)
        if len(done) % 25 == 0:
            print(f'Public files verified: {len(done)}/{len(paths)}', flush=True)
    receipt['remaining'] = [row['path'] for row in manifest['files'] if row['path'] not in done]
    receipt['state'] = 'pass' if not receipt['remaining'] else 'incomplete'
    receipt['finished_at'] = datetime.now(timezone.utc).isoformat()
    receipt['verified_bytes'] = sum(row['bytes'] for row in receipt['files'])
    write(receipt_path, receipt)
    print(json.dumps({'state': receipt['state'], 'files': len(done), 'remaining': receipt['remaining']}), flush=True)
    if receipt['remaining']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
