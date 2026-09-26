"""Freeze native D110 metadata and verify real bilingual section destinations.

No producer mutation, translation, Lean compilation or inferred code-level
equivalence between the separately versioned English and Indonesian readers.
"""
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d110-surface-v1/input'
AUTHORITY = ROOT / 'backend/v2.3/extensions/d110-mathematics-in-lean-v0.1.0/INPUT_AUTHORITIES.json'
READERS = {'id': 'https://kokunoyumeto.github.io/mathematics-in-lean-id/',
           'en': 'https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/D110/'}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


class Headings(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.sections, self.headings = Counter(), [], []
        self.current, self.skip = None, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids[a['id']] += 1
        if tag == 'section':
            self.sections.append(a.get('id'))
        if tag in ('h1', 'h2'):
            self.current = {'level': int(tag[1]), 'anchor': self.sections[-1] if self.sections else None, 'text': ''}
        if tag == 'a' and self.current and 'headerlink' in a.get('class', '').split():
            self.skip = True

    def handle_data(self, data):
        if self.current and not self.skip:
            self.current['text'] += data

    def handle_endtag(self, tag):
        if tag == 'a':
            self.skip = False
        if tag in ('h1', 'h2') and self.current:
            self.current['text'] = ' '.join(self.current['text'].split())
            self.headings.append(self.current)
            self.current = None
        if tag == 'section' and self.sections:
            self.sections.pop()


def get(url, maximum=2_000_000):
    with urlopen(url, timeout=35) as response:
        assert response.status == 200, url
        data = response.read(maximum + 1)
    assert len(data) <= maximum, url
    return data


def extract_solutions(native, units):
    """Find exact hash-bound spans; never reuse English line numbers as ID lines."""
    wanted = {}
    for u in units:
        if u['data']['unit_type'] in ('solution', 'solution_support'):
            for lang, key in [('id', 'target_text_sha256'), ('en', 'source_text_sha256')]:
                if u['data'].get(key):
                    wanted.setdefault((lang, u['source_path']), {})[u['data'][key]] = True
    found, sources = {}, []
    for (lang, path), hashes in wanted.items():
        root = native / ('source-id' if lang == 'id' else 'baseline/source-working')
        p = root / path
        assert p.is_file(), path
        body = p.read_bytes()
        normalized = unicodedata.normalize('NFC', body.decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n'))
        lines = normalized.splitlines()
        sources.append({'language': lang, 'path': path, 'bytes': len(body), 'sha256': sha(body)})
        candidates = [i for i, line in enumerate(lines)
                      if re.match(r'^\s*(?:(?:noncomputable|private|protected)\s+)*(?:example|instance|theorem|lemma|def|class|structure|inductive)\b', line)]
        matches = {}
        def accept(text, line, method, source_region=None):
            digest = sha(text.encode())
            if digest in hashes:
                matches.setdefault(digest, {'text': text, 'line_start': line,
                                           'file_sha256': sha(body), 'method': method,
                                           **({'source_region': source_region} if source_region is not None else {})})

        # Native build_backend.py conditional_solution_chunks removes only the
        # first EXAMPLES control block, then rstrips; it retains -- BOTH:.
        marker = re.compile(r'(?ms)/- EXAMPLES:\n.*?\nSOLUTIONS: -/\n')
        for quote in re.finditer(r'(?ms)^-- QUOTE:\n(.*?)\n-- QUOTE\.$', normalized):
            value = quote.group(1)
            for pattern in (r'(?m)^(def|theorem|example)\b',
                            r'(?m)^(?:@\[[^\]\n]+\][ \t]+)?(?:(?:protected|private)\s+)?(?:noncomputable\s+)?(inductive|structure|class|instance|lemma|def|theorem|example)\b'):
                starts = list(re.finditer(pattern, value))
                for n, start in enumerate(starts):
                    end = starts[n + 1].start() if n + 1 < len(starts) else len(value)
                    chunk = value[start.start():end].rstrip()
                    control = marker.search(chunk)
                    if control:
                        projected = (chunk[:control.start()] + chunk[control.end():]).rstrip()
                        line = normalized.count('\n', 0, quote.start(1) + start.start()) + 1
                        accept(projected, line, 'native_conditional_first_marker_projection', chunk)
        for region in re.finditer(r'(?ms)^/- SOLUTIONS:\n(.*?)(?=^(?:BOTH|EXAMPLES): -/)', normalized):
            accept(region.group(1).rstrip(), normalized.count('\n', 0, region.start(1)) + 1,
                   'native_commented_solution_region_rstrip', region.group(1))
        for start in candidates:
            for end in range(start + 1, min(start + 300, len(lines)) + 1):
                raw = '\n'.join(lines[start:end])
                for text in {raw, raw.rstrip(), raw.strip()}:
                    accept(text, start + 1, 'exact_contiguous_span')
        # Inline proof-hole solutions need not begin with a declaration. Search
        # remaining spans exactly; no fuzzy matching or guessed proof repair.
        if set(hashes) - set(matches):
            for start, line in enumerate(lines):
                if not line.strip() or start in candidates:
                    continue
                for end in range(start + 1, min(start + 160, len(lines)) + 1):
                    raw = '\n'.join(lines[start:end])
                    for text in {raw, raw.rstrip(), raw.strip()}:
                        accept(text, start + 1, 'exact_contiguous_span')
                if set(hashes) <= set(matches):
                    break
        for digest, item in matches.items():
            found[(lang, path, digest)] = item
    result = []
    for u in units:
        if u['data']['unit_type'] not in ('solution', 'solution_support'):
            continue
        texts = {}
        for lang, key in [('id', 'target_text_sha256'), ('en', 'source_text_sha256')]:
            digest = u['data'].get(key)
            if digest:
                match = found.get((lang, u['source_path'], digest))
                texts[lang] = {'state': 'exact_hash_projection' if match and match.get('source_region') is not None else ('exact_hash_span' if match else 'not_extracted'), 'sha256': digest, **(match or {})}
        result.append({'id': u['record_id'], 'texts': texts})
    recipe = native / 'scripts/build_backend.py'
    return {'units': result, 'source_files': sources,
            'native_recipe': {'path': 'scripts/build_backend.py', 'sha256': sha(recipe.read_bytes()), 'bytes': recipe.stat().st_size},
            'method': 'native NFC/LF hashes and conditional/commented solution projections; no guessed target lines'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-root', type=Path, required=True)
    parser.add_argument('--verify-public', action='store_true')
    parser.add_argument('--reuse-reader-witness', action='store_true')
    args = parser.parse_args()
    native = args.native_root.resolve()
    authority_bytes = AUTHORITY.read_bytes()
    admitted = {r['path']: r for r in json.loads(authority_bytes)['authorities'] if r['path_base'] == 'owner_package_root'}
    buffers, rows, facts = {}, {}, []
    for name in ('unit', 'asset', 'relation', 'rights'):
        path = f'backend/exports/entities/{name}.jsonl'
        data = (native / path).read_bytes()
        assert (len(data), sha(data)) == (admitted[path]['bytes'], admitted[path]['sha256']), f'Native drift: {path}'
        buffers[name] = data
        rows[name] = [json.loads(line) for line in data.decode('utf-8').splitlines()]
        assert len(rows[name]) == len({r['record_id'] for r in rows[name]})
        facts.append({'path': f'{name}.jsonl', 'native_path': path, 'bytes': len(data), 'sha256': sha(data)})
    chapters = [u for u in rows['unit'] if u['data']['unit_type'] == 'chapter']
    sections = [u for u in rows['unit'] if u['data']['unit_type'] == 'section']
    assert (len(chapters), len(sections), len(rows['unit'])) == (13, 43, 2177)
    routes, pages = {}, []
    previous_witness = None
    if args.reuse_reader_witness:
        prior_lock = json.loads((BASE / 'source-lock.json').read_text(encoding='utf-8'))
        expected = next(r for r in prior_lock['files'] if r['path'] == 'reader-witness.json')
        data = (BASE / 'reader-witness.json').read_bytes()
        assert (len(data), sha(data)) == (expected['bytes'], expected['sha256'])
        previous_witness = json.loads(data)
        assert previous_witness['public_verified']
        assert set(previous_witness['routes']) == {u['record_id'] for u in chapters + sections}
    for chapter in ([] if previous_witness else chapters):
        stem = chapter['source_local_id']
        assert re.fullmatch(r'C\d{2}_[A-Za-z_]+', stem)
        chapter_sections = sorted((u for u in sections if u['parent_id'] == chapter['record_id']), key=lambda u: u['order_index'])
        for lang in ('id', 'en'):
            html_root = native / 'output/html' if lang == 'id' else ROOT / 'docs/en/courses/D110'
            includes_body = (html_root / '_sources' / f'{stem}.rst.txt').read_bytes()
            includes = re.findall(r'^\.\. include:: (.+)\.inc\s*$', includes_body.decode('utf-8'), re.M)
            assert includes == [f"{stem}/{u['source_local_id']}" for u in chapter_sections], f'Include order drift: {stem}/{lang}'
            url = READERS[lang] + stem + '.html'
            body = get(url) if args.verify_public else (html_root / f'{stem}.html').read_bytes()
            doc = Headings()
            doc.feed(body.decode('utf-8'))
            top = [h for h in doc.headings if h['level'] == 1]
            headings = [h for h in doc.headings if h['level'] == 2]
            assert len(top) == 1 and len(headings) == len(chapter_sections), f'Heading count: {url}'
            for unit, h in [(chapter, top[0]), *zip(chapter_sections, headings)]:
                assert h['anchor'] and doc.ids[h['anchor']] == 1, f'Unique heading: {url}'
                if unit in chapter_sections:
                    ordinal = chapter_sections.index(unit) + 1
                    assert h['text'].startswith(f'{int(stem[1:3])}.{ordinal}. '), (url, h)
                routes.setdefault(unit['record_id'], {})[lang] = {
                    'url': url + '#' + h['anchor'], 'anchor': h['anchor'],
                    'title': re.sub(r'^\d+(?:\.\d+)*\.\s*', '', h['text']),
                    'state': 'verified_heading', 'page_sha256': sha(body)}
            pages.append({'language': lang, 'url': url, 'bytes': len(body), 'sha256': sha(body),
                          'source_include_sha256': sha(includes_body), 'source_include_bytes': len(includes_body),
                          'source_includes': includes, 'headings': doc.headings})
    solutions = extract_solutions(native, rows['unit'])
    witness = previous_witness or {'schema': 'd110-reader-witness/1', 'public_verified': args.verify_public,
               'readers': READERS, 'pages': pages, 'routes': routes,
               'english_route_scope': 'same named chapter/section in separately versioned original English reader; NOT per-code equivalence',
               'indonesian_metadata_source_revision': '8e112cd63ff1bf2a1020ff88f22f77288e42b9a9',
               'english_reader_revision': 'dd6d752fedb14082f557913c2dccb2d4851e5173'}
    BASE.mkdir(parents=True, exist_ok=True)
    for name, body in buffers.items():
        (BASE / f'{name}.jsonl').write_bytes(body)
    dump(BASE / 'reader-witness.json', witness)
    dump(BASE / 'solution-witness.json', solutions)
    for name in ('reader-witness.json', 'solution-witness.json'):
        data = (BASE / name).read_bytes()
        facts.append({'path': name, 'bytes': len(data), 'sha256': sha(data)})
    dump(BASE / 'source-lock.json', {'schema': 'd110-consumer-input/1', 'files': facts,
                                   'admission_authority': {'path': AUTHORITY.relative_to(ROOT).as_posix(), 'sha256': sha(authority_bytes), 'bytes': len(authority_bytes)}})
    missing = [(r['id'], lang) for r in solutions['units'] for lang, item in r['texts'].items() if item['state'] not in ('exact_hash_span', 'exact_hash_projection')]
    print(json.dumps({'state': 'pass', 'units': 2177, 'chapters': 13, 'sections': 43, 'reader_pages': len(witness['pages']),
                      'public_verified': witness['public_verified'], 'solution_texts_not_extracted_count': len(missing),
                      'solution_texts_not_extracted_sample': missing[:4]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
