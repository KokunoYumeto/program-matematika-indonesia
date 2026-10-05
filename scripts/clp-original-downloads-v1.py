"""Additive CLP original-download intake; never rebuild or edit the books.

Downloads are streamed for identity checks, not copied into the hub. Public
publisher URLs are mutable; their hashes record an observation, not a promise
that an independently observed source commit reproduces them.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/clp-original-downloads-v1'
OVERLAY = 'backend/authority/central-course-surface-navigation-overlay-v1.json'
PROOF = 'docs/interface/evidence/clp-original-downloads-v1.json'
MODULE = 'docs/interface/clp-original-downloads.js'
OWN = 'scripts/clp-original-downloads-v1.py'
REPO = 'KokunoYumeto/program-matematika-indonesia'
API = 'https://api.github.com/repos/' + REPO
RAW = 'https://raw.githubusercontent.com/' + REPO + '/'
ROLES = [('B20', 1), ('B30', 2), ('B50', 3), ('B60', 4)]
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def fetch(url):
    r = requests.get(url, timeout=(15, 60))
    r.raise_for_status()
    return r


def capture():
    dest = OUT / 'hub-parent'
    assert not (dest / 'BASELINE.json').exists(), 'Do not replace an existing baseline'
    parent = fetch(API + '/git/ref/heads/main').json()['object']['sha']
    paths = sorted(set([r['path'] for r in read(ROOT / 'docs/interface/build-receipt.json')['outputs']] + [
        OVERLAY, 'docs/interface/build-receipt.json', 'docs/interface/original-sources.js',
        'docs/interface/view.js', 'docs/interface/supplemental-readers.js',
        'docs/interface/reader-actions.js', 'docs/interface/final-editions.js',
        'docs/interface/capability-tools.js', 'scripts/build-multilingual-interface.mjs',
        'scripts/test-multilingual-interface.mjs', 'scripts/test-course-downloads-v1.mjs']))
    rows = []
    for path in paths:
        local = (ROOT / path).read_bytes()
        public = fetch(RAW + parent + '/' + path).content
        assert local.replace(b'\r\n', b'\n') == public.replace(b'\r\n', b'\n'), 'Concurrent edit: ' + path
        target = dest / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(local)
        rows.append({'path':path, 'bytes':len(local), 'sha256':sha(local),
                     'public_parent_bytes':len(public), 'public_parent_sha256':sha(public)})
    save(dest / 'BASELINE.json', {'parent':parent, 'files':rows})
    print(json.dumps({'state':'captured', 'parent':parent, 'files':len(rows)}), flush=True)


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.hrefs = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href')
            if href: self.hrefs.append(href)


def intake():
    assert not (ROOT / PROOF).exists(), 'Reuse the existing intake; do not redownload unchanged books'
    books = []
    for course, volume in ROLES:
        url = f'https://personal.math.ubc.ca/~CLP/CLP{volume}/'
        page = fetch(url)
        links = Links(); links.feed(page.text)
        urls = [urljoin(url, h) for h in links.hrefs]
        pdfs = [u for u in urls if u.endswith('.pdf') and any(s in u for s in ('_text.pdf', '_problems.pdf'))]
        assert len(pdfs) == 2 and len(set(pdfs)) == 2, (course, pdfs)
        repository = f'https://github.com/arechnitzer/CLP{volume}'
        assert any(u.rstrip('/') == repository for u in urls), 'Publisher source-repository link missing'
        assert 'combined PDF' in page.text and 'BY-NC-SA 4.0' in page.text
        source = fetch(f'https://api.github.com/repos/arechnitzer/CLP{volume}/commits?per_page=1').json()[0]
        facts = []
        for pdf in pdfs:
            digest = hashlib.sha256(); length = 0; prefix = b''; tail = b''
            with requests.get(pdf, stream=True, timeout=(15, 60)) as r:
                r.raise_for_status()
                assert r.url.startswith('https://personal.math.ubc.ca/'), 'Unexpected publisher redirect'
                for chunk in r.iter_content(1024 * 1024):
                    if not chunk: continue
                    if not prefix: prefix = chunk[:8]
                    tail = (tail + chunk)[-2048:]
                    length += len(chunk); assert length <= 64 * 1024 * 1024
                    digest.update(chunk)
                assert prefix.startswith(b'%PDF-') and b'%%EOF' in tail, 'Not a complete PDF response'
                if r.headers.get('Content-Length'): assert length == int(r.headers['Content-Length'])
                facts.append({'role':'textbook' if '_text.pdf' in pdf else 'problembook',
                    'url':pdf, 'bytes':length, 'sha256':digest.hexdigest(), 'http':r.status_code,
                    'last_modified':r.headers.get('Last-Modified')})
            print(json.dumps({'course':course, **facts[-1]}), flush=True)
        assert {f['role'] for f in facts} == {'textbook','problembook'}
        books.append({'course_id':course, 'volume':volume, 'publisher_page':url,
            'publisher_page_sha256':sha(page.content), 'repository':repository,
            'observed_source_commit':source['sha'], 'files':facts,
            'combined_pdf_claimed':False, 'pdf_source_reproduction_verified':False})
    proof = {'schema':'clp-original-download-intake/1', 'state':'anonymous_byte_readback_passed',
        'observed_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Eight existing author-hosted English textbook/problem-book PDFs for four CLP roles; no republication, new translation or combined PDF.',
        'authors':['Joel Feldman','Andrew Rechnitzer','Elyse Yeager'],
        'licence':'CC-BY-NC-SA-4.0', 'books':books,
        'integration_provenance':{'model':'gpt-6-astra','effort':'ultra','role':'link integration and byte-identity checks only'},
        'limits':['Publisher URLs are mutable; hashes record the observation time.',
                  'Source repositories are separately identified; exact PDF/source reproduction has not been verified.',
                  'No new EPUB, direct cumulative LaTeX, full-source ZIP or complete backend claim.']}
    save(ROOT / PROOF, proof)
    generate(proof)


def generate(proof):
    # Data-only generated module: the existing adapter owns presentation.
    rows = {}
    for book in proof['books']:
        v = book['volume']; items = []
        for f in book['files']:
            text = f['role'] == 'textbook'
            items.append({'href':f['url'], 'contentLanguage':'en', 'kind':'PDF', 'format':'PDF',
                'bytes':f['bytes'], 'sha256':f['sha256'],
                'labels':{'en':f'CLP-{v} — '+('textbook' if text else 'problem book')+' (original English PDF)',
                          'id':f'CLP-{v} — '+('buku teks' if text else 'buku latihan')+' (PDF asli bahasa Inggris)'},
                'notes':{'en':'Author-hosted English original; textbook and problem book are separate PDFs. The publisher may update these files.',
                         'id':'Sumber asli bahasa Inggris di situs penulis; buku teks dan buku latihan berupa PDF terpisah. Penulis dapat memperbarui berkas ini.'}})
        items.append({'href':book['repository'], 'contentLanguage':'en', 'kind':'repository',
            'labels':{'en':f'CLP-{v} — authors’ editable sources', 'id':f'CLP-{v} — sumber suntingan dari penulis'},
            'notes':{'en':'Original LaTeX and PreTeXt sources. The repository is not a verified matching source package for the linked PDFs.',
                     'id':'Sumber asli LaTeX dan PreTeXt. Repositori ini belum diverifikasi sebagai paket sumber yang cocok persis dengan PDF tertaut.'}})
        rows[book['course_id']] = [{**r, 'origin':'upstream-original', 'accessRole':'authoritative-original',
            'authorityRole':'upstream-authority', 'relationToSource':'source'} for r in items]
    notes = []
    for items in rows.values():
        for item in items:
            if item['notes'] not in notes: notes.append(item['notes'])
            item['notes'] = notes.index(item['notes'])
    compact = lambda value: json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    (ROOT / MODULE).write_text('// Generated from the CLP publisher intake; original books remain unchanged.\n'
        + 'const clpOriginalNotes = ' + compact(notes) + ';\n'
        + 'export const clpOriginalSources = Object.fromEntries(Object.entries(' + compact(rows)
        + ').map(([id,rows])=>[id,rows.map(row=>({...row,notes:clpOriginalNotes[row.notes]}))]));\n', encoding='utf-8')


def navigation():
    sys.path.insert(0, str(ROOT / 'scripts'))
    spec = importlib.util.spec_from_file_location('surface_nav', ROOT / 'scripts/apply-central-course-surface-navigation-v1.py')
    nav = importlib.util.module_from_spec(spec); spec.loader.exec_module(nav)
    baseline = read(OUT / 'hub-parent/BASELINE.json')
    old = (OUT / 'hub-parent' / OVERLAY).read_bytes()
    overlay = read(OUT / 'hub-parent' / OVERLAY)
    current = read(ROOT / OVERLAY)
    refresh = current.get('clp_original_download_refresh')
    if current != overlay:
        assert refresh and refresh['parent_overlay_sha256'] == sha(old), 'Concurrent navigation edit'
        restored = json.loads(json.dumps(current)); del restored['clp_original_download_refresh']
        restored['files'] = overlay['files']
        restored['authority']['learner_access_manifest'] = overlay['authority']['learner_access_manifest']
        assert restored == overlay
        for a,b in zip(current['files'],overlay['files']):
            if a['document'] not in refresh['documents']: assert a == b
    contract = read(nav.CONTRACT_PATH)
    targets = [(v['public_url'],k,v['navigation']['program_root']) for k,v in sorted(contract['interfaces'].items())]
    updated = []
    for fact in baseline['files']:
        path = fact['path']
        if not path.endswith('.html'): continue
        payload = (ROOT / path).read_bytes()
        if payload == (OUT / 'hub-parent' / path).read_bytes(): continue
        row = next((r for r in overlay['files'] if r['document'] == path), None)
        if row is None:
            assert nav.MARKER not in payload.decode('utf-8'); continue
        assert row['role'] == 'generic' and row['course_ids'] == []
        source, hosted = nav.inject_overlay(path,payload,[],targets,[],[],contract['interfaces'][row['locale']]['navigation'])
        (ROOT / path).write_bytes(hosted)
        row['source_body'] = nav.fact(path,source); row['hosted_surface'] = nav.fact(path,hosted)
        assert nav.strip_owned_overlay(hosted.decode('utf-8'),path).encode('utf-8') == source
        updated.append(path)
    manifest = 'docs/interface/learner-access-manifest.json'
    overlay['authority']['learner_access_manifest'] = nav.fact(manifest,(ROOT / manifest).read_bytes())
    overlay['clp_original_download_refresh'] = {'parent_overlay_sha256':sha(old),
        'script':nav.fact(OWN,Path(__file__).read_bytes()), 'documents':updated,
        'scope':'Existing English CLP textbook and problem-book links; original editions and all other course resources preserved.'}
    save(ROOT / OVERLAY, overlay)
    print(json.dumps({'state':'navigation_restored','documents':updated}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=['capture','intake','generate','navigation'])
    {'capture':capture, 'intake':intake, 'generate':lambda:generate(read(ROOT / PROOF)), 'navigation':navigation}[parser.parse_args().action]()
