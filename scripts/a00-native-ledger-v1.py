"""Small, reproducible view of native A00 ledgers; never rewrites the producer.

Intake checks native target modules and the selected native metadata against
their exact manifest. Subsequent builds operate only on frozen metadata, not
on book bodies. Native review labels remain source claims, not our certification.
"""
import argparse
import csv
import hashlib
import html
import io
import json
from pathlib import Path
import re
import zipfile
import a00_term_locations_v1 as term_locations

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/a00-native-ledger-v1'
GENERATED = 'modular_backend/generated/prealgebra2e-volume'
SNAPSHOTS = {
    'native-LICENSE.txt': 'LICENSE',
    'source-map.csv': 'SOURCE_SEGMENT_MAP.id-ID.csv',
    'choices.csv': 'TERMINOLOGY_AND_ADVERSE_LEDGER.id-ID.csv',
    'native-manifest.json': GENERATED + '/backend.volume.manifest.json',
    **{name: GENERATED + '/' + path for name, path in {
        'modules.tsv': 'metadata/modules.tsv',
        'source-witnesses.tsv': 'metadata/source-witness-manifest.tsv',
        'target-witnesses.tsv': 'metadata/target-witness-manifest.tsv',
        'artifacts.jsonl': 'workflow/artifacts.jsonl',
        'corrections.jsonl': 'workflow/corrections.jsonl',
        'terms.jsonl': 'locales/id-ID/terms.jsonl',
        'toolchain.json': 'metadata/toolchain.json',
        'rights.jsonl': 'registry/rights.jsonl',
        'resources.jsonl': 'registry/resources.jsonl',
    }.items()},
}


def sha(body):
    return hashlib.sha256(body).hexdigest()


def packed(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else packed(value))


def fact(path):
    digest, count = hashlib.sha256(), 0
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
            count += len(block)
    return {'bytes': count, 'sha256': digest.hexdigest()}


def checked_path(root, relative):
    if not re.fullmatch(r'[A-Za-z0-9_./-]+', relative) or '..' in Path(relative).parts:
        raise ValueError('Unsafe native path')
    path = (root / relative).resolve()
    path.relative_to(root.resolve())
    return path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def table(body, delimiter=','):
    return list(csv.DictReader(io.StringIO(body.decode('utf-8-sig')), delimiter=delimiter))


def jsonl(body):
    return [json.loads(line) for line in body.splitlines() if line.strip()]


def intake(native, dest):
    # Freeze only these exact metadata files, not the native books or database.
    raw = {name: checked_path(native, path).read_bytes() for name, path in SNAPSHOTS.items()}
    manifest = json.loads(raw['native-manifest.json'])
    require(manifest['course_role'] == 'R001-prealgebra-2e' and manifest['module_count'] == 75,
            'Wrong native course or scope')
    listed = {row['path']: row for row in manifest['files']}
    for name, path in SNAPSHOTS.items():
        if path.startswith(GENERATED + '/') and name != 'native-manifest.json':
            row = listed[path[len(GENERATED) + 1:]]
            require(len(raw[name]) == row['bytes'] and 'sha256:' + sha(raw[name]) == row['sha256'],
                    'Native metadata differs from manifest: ' + name)
    require('sha256:' + sha(raw['choices.csv']) == manifest['terminology_and_adverse_ledger']['sha256'],
            'Native terminology ledger hash differs')
    probes = []
    for row in manifest['modules']:
        relative = f"modules/{row['module_id']}/index.cnxml"
        identity = fact(checked_path(native, relative))
        require(identity['bytes'] == row['target_bytes'] and 'sha256:' + identity['sha256'] == row['target_sha256'],
                'Native target differs: ' + row['module_id'])
        probes.append({'module_id': row['module_id'], 'path': relative, **identity})
    require(len(probes) == len({r['module_id'] for r in probes}) == 75, 'Duplicate/missing native module')
    lock = {'schema': 'a00-native-ledger-input/1', 'observed_date': '2026-09-30',
            'native_root_locator': '04_mirrors/id/openstax-prealgebra',
            'native_modified': False, 'target_probe': probes,
            'snapshots': [{'path': name, 'native_path': path, 'bytes': len(raw[name]), 'sha256': sha(raw[name])}
                          for name, path in sorted(SNAPSHOTS.items())]}
    # All checks finish before changing the central snapshot.
    for name, body in raw.items():
        save(dest / 'input' / name, body)
    save(dest / 'input/source-lock.json', lock)


def freeze_term_locations(native, dest):
    lock = json.loads((dest / 'input/source-lock.json').read_bytes())
    raw = {r['path']: checked_path(dest / 'input', r['path']).read_bytes() for r in lock['snapshots']}
    # Revalidate the original metadata before reading any native content.
    for row in lock['snapshots']:
        require(len(raw[row['path']]) == row['bytes'] and sha(raw[row['path']]) == row['sha256'], 'Snapshot identity differs')
    prior = dict(lock)
    prior.pop('term_locations', None)
    data = normalize(raw, prior)
    proof = term_locations.collect(data, native)
    body = packed(proof)
    lock['term_locations'] = {'path': 'term-locations.json', 'bytes': len(body), 'sha256': sha(body),
                              'generator': fact(ROOT / 'scripts/a00_term_locations_v1.py')}
    save(dest / 'input/term-locations.json', body)
    save(dest / 'input/source-lock.json', lock)


def normalize(raw, lock):
    manifest = json.loads(raw['native-manifest.json'])
    modules = manifest['modules']
    require(len(modules) == len({r['module_id'] for r in modules}) == 75, 'Bad module cardinality')
    require(sorted(r['ordinal'] for r in modules) == list(range(1, 76)), 'Bad module order')
    probes = {r['module_id']: r for r in lock['target_probe']}
    artifact_rows = jsonl(raw['artifacts.jsonl'])
    require(len(artifact_rows) == 75 and len({r['id'] for r in artifact_rows}) == 75, 'Duplicate artifact record')
    artifacts = {r['module_id']: r for r in artifact_rows}
    source = {r['module']: r for r in table(raw['source-witnesses.tsv'], '\t')}
    target = {r['module']: r for r in table(raw['target-witnesses.tsv'], '\t')}
    module_table = {r['module']: r for r in table(raw['modules.tsv'], '\t')}
    require(all(set(v) == {r['module_id'] for r in modules} for v in [probes, artifacts, source, target, module_table]),
            'A native projection omits or adds modules')
    csv_rows = list(csv.reader(io.StringIO(raw['source-map.csv'].decode('utf-8-sig'))))
    header, old_rows = csv_rows[0], csv_rows[1:]
    require(len(header) == 15 and len(old_rows) == 75, 'Unexpected source map structure')
    old, discrepancies = {}, []
    for row in old_rows:
        if len(row) == 14:
            require(row[2] == 'm81272' and row[8:10] == ['111105', 'e2846b8f98cf8443d80407d0904c608a06f49b5eb9e931891f6b274ca9749998'],
                    'Unrecognized malformed source-map row')
            discrepancies.append({'module_id': row[2], 'kind': 'omitted_target_path',
                                  'original_cells': row[:], 'inserted_field': 'target_path',
                                  'inserted_value': 'modules/m81272/index.cnxml'})
            row = row[:8] + ['modules/m81272/index.cnxml'] + row[8:]
        require(len(row) == 15, 'Malformed source-map row')
        require(row[2] not in old, 'Duplicate source-map module')
        old[row[2]] = dict(zip(header, row))
    output = []
    for module in modules:
        mid = module['module_id']
        current = {'bytes': module['target_bytes'], 'sha256': module['target_sha256'].removeprefix('sha256:')}
        require({k: probes[mid][k] for k in current} == current, 'Target probe does not match native manifest')
        a, s, t, mt, before = artifacts[mid], source[mid], target[mid], module_table[mid], old[mid]
        for r in [a, mt]:
            require(int(r['target_bytes']) == current['bytes'] and r['target_sha256'].removeprefix('sha256:') == current['sha256'], 'Target projection mismatch')
            require(int(r['source_bytes']) == module['source_bytes'] and r['source_sha256'].removeprefix('sha256:') == module['source_sha256'].removeprefix('sha256:'), 'Source projection mismatch')
        require(int(t['bytes']) == current['bytes'] and t['sha256'] == current['sha256'], 'Target witness mismatch')
        require(int(s['bytes']) == module['source_bytes'] and 'sha256:' + s['sha256'] == module['source_sha256'], 'Source witness mismatch')
        require(before['source_sha256'] == s['sha256'] and int(before['source_bytes']) == int(s['bytes']), 'Older source identity changed')
        require(s['url'] == before['source_url'] and s['url'].startswith('https://raw.githubusercontent.com/openstax/osbooks-prealgebra-bundle/'), 'Unexpected source URL')
        if int(before['target_bytes']) != current['bytes'] or before['target_sha256'] != current['sha256']:
            discrepancies.append({'module_id': mid, 'kind': 'stale_target_identity',
                                  'earlier': {'bytes': int(before['target_bytes']), 'sha256': before['target_sha256']}, 'current': current})
        output.append({'module_id': mid, 'ordinal': module['ordinal'],
                       'source': {'bytes': int(s['bytes']), 'sha256': s['sha256'], 'url': s['url']},
                       'target': {'path': t['path'], **current}, 'unit_id': module['module_unit_id'],
                       'localized_unit_id': module['localized_module_unit_id'], 'artifact_id': a['id'],
                       'producer_status': a['status'], 'semantic_review_by_this_adapter': False})
    terms, corrections = jsonl(raw['terms.jsonl']), jsonl(raw['corrections.jsonl'])
    require(len({r['id'] for r in terms + corrections}) == len(terms + corrections), 'Duplicate choice ID')
    ledger = {r['record_id']: r for r in table(raw['choices.csv'])}
    require(len(ledger) == 95 and len(terms) == 56 and len(corrections) == 75, 'Native ledger cardinality changed')
    lexical = [r for r in terms if r.get('source_record_id')]
    require(len(lexical) == 20, 'Expected 20 lexical term choices')
    require({r['source_record_id'] for r in lexical + corrections} == set(ledger), 'Missing native ledger record')
    for record in lexical + corrections:
        witness = ledger[record['source_record_id']]
        require(record['ledger_sha256'] == 'sha256:' + sha(raw['choices.csv']), 'Choice ledger identity drift')
        require(record['scope'] == witness['scope'] and record['evidence_basis'] == witness['evidence_basis'], 'Choice evidence drift')
        require(record.get('preferred_term', record.get('target_decision')) == witness['target_decision'], 'Choice changed')
    data = {'schema': 'a00-native-ledger-view/1', 'course_id': 'A00', 'scope': 'module_identity_and_native_choice_metadata',
            'modules': output, 'terms': terms, 'corrections': corrections, 'source_map_discrepancies': discrepancies,
            'verification': {'target_files_byte_verified': 75, 'source_content_reread': False,
                             'semantic_canon_review': False, 'whole_native_rebuild': False,
                             'segment_level_choice_coverage': 'not_established', 'native_files_modified': False},
            'source_lock_sha256': sha(packed(lock))}
    if lock.get('term_locations'):
        witness = lock['term_locations']
        require(witness['path'] == 'term-locations.json', 'Unsafe term proof path')
        body = raw[witness['path']]
        require(len(body) == witness['bytes'] and sha(body) == witness['sha256'], 'Term proof identity differs')
        data['term_locations'] = term_locations.validate(json.loads(body), data)
        data['verification']['lexical_target_location_matches'] = data['term_locations']['summary']['choice_variant_matches']
        data['verification']['lexical_location_unwrapped_text_slots'] = data['term_locations']['summary']['unwrapped_text_slots']
    return data


def render(data, english=False):
    e = html.escape
    lang = 'en' if english else 'id'
    title = 'A00 · Source map and terminology' if english else 'A00 · Peta sumber dan istilah'
    other = 'ledger.html' if english else 'ledger-en.html'
    course = 'A00-en.html' if english else 'A00.html'
    teacher = 'A00-pengajar-en.html' if english else 'A00-pengajar.html'
    boundary = ('All 75 target module files match the native manifest. One older CSV row omits a path; three have stale target hashes. The original records are preserved. This is an identity and metadata check, not a new semantic translation review or a native book rebuild.' if english else
                'Berkas terjemahan untuk seluruh 75 modul cocok dengan manifest backend asli. Satu baris CSV lama kehilangan kolom jalur; tiga baris menyimpan hash lama. Catatan asli tetap dipertahankan. Ini pemeriksaan identitas dan metadata, bukan pemeriksaan baru terhadap makna terjemahan atau pembangunan ulang buku.')
    rows = []
    for r in data['modules']:
        mid = e(r['module_id'])
        details = f"<details><summary>SHA-256</summary><p>EN: <code>{r['source']['sha256']}</code></p><p>ID: <code>{r['target']['sha256']}</code></p><p>Unit: <code>{r['unit_id']}</code></p></details>"
        source_label = 'CNXML (English)' if english else 'CNXML (bahasa Inggris)'
        rows.append(f'<tr data-search="{mid}"><td>{r["ordinal"]}</td><th scope="row">{mid}</th><td>{r["source"]["bytes"]:,}</td><td>{r["target"]["bytes"]:,}</td><td><a href="{e(r["source"]["url"], quote=True)}">{source_label}</a>{details}</td></tr>')
    termrows = []
    location_records = {row['choice_id']: row for row in data.get('term_locations', {}).get('choices', [])}
    for r in data['terms']:
        if not r.get('source_record_id'):
            continue
        proof = location_records.get(r['id'])
        details, module_search = '', ''
        if proof:
            module_search = ' '.join(sorted({hit['module_id'] for hit in proof['matches']}))
            label = (f"{proof['match_count']} literal matches in {proof['module_count']} modules" if english else
                     f"{proof['match_count']} kecocokan harfiah dalam {proof['module_count']} modul")
            examples = []
            for hit in proof['matches'][:8]:
                anchor = hit['module_id'] + ('#' + hit['xml_id'] if hit['xml_id'] else '')
                examples.append(f'<li><code>{e(anchor)}</code> · <code>{e(hit["xpath"])}</code><br><q lang="id">{e(hit["excerpt"])}</q><br><small>SHA-256: <code>{hit["block_text_sha256"]}</code></small></li>')
            note = ('Up to eight contexts shown here; the JSON includes every matched range. Raw native scope is preserved, not approved. Zero matches do not prove a translation error.' if english else
                    'Paling banyak delapan konteks ditampilkan di sini; JSON mencakup semua rentang yang cocok. Cakupan asli dipertahankan, bukan disetujui. Tidak adanya kecocokan bukan bukti kesalahan terjemahan.')
            details = f'<details class="term-locations" data-choice-id="{e(r["id"], quote=True)}"><summary>{label}</summary><p>{note}</p><ol>{"".join(examples)}</ol></details>'
        termrows.append(f'<tr data-search="{e(r["preferred_term"]+" "+r["source_term"]+" "+r["scope"]+" "+module_search, quote=True)}"><th scope="row" data-label="Bahasa Indonesia">{e(r["preferred_term"])}</th><td data-label="{"English" if english else "Bahasa Inggris"}">{e(r["source_term"])}</td><td data-label="{"Scope" if english else "Cakupan"}">{e(r["scope"])}</td><td data-label="ID"><code>{e(r["source_record_id"])}</code>{details}</td></tr>')
    termsnote = ('The 20 lexical choices are quoted from the native ledger. Its 36 other terms name concepts/course metadata. Bibliographic descriptions do not prove exact canon-passage consultation or occurrence-level verification. Those checks remain unfinished.' if english else
                 'Dua puluh pilihan istilah berikut dikutip dari ledger asli. Sebanyak 36 istilah lainnya merupakan label konsep/metadata mata kuliah. Keterangan bibliografi belum membuktikan pembacaan bagian kanon tertentu atau pemeriksaan setiap kemunculan istilah; pemeriksaan tersebut masih belum selesai.')
    if location_records:
        count = data['term_locations']['summary']['choice_variant_matches']
        unwrapped = data['term_locations']['summary']['unwrapped_text_slots']
        termsnote += (' ' + (f'The byte-bound concordance maps {count} choice/variant matches over the prose of 75 translated CNXML modules. It excludes metadata and MathML bodies; {unwrapped} residual text slots are also searched separately. Phrases are not joined across table cells or residual slots. Matching and raw scope do not establish semantic or canon approval; overlapping variants and the two distinct native sum choices are retained separately.' if english else
                            f'Konkordansi yang terikat pada identitas byte memetakan {count} kecocokan pilihan/varian pada prosa dalam 75 modul CNXML terjemahan. Metadata dan isi MathML tidak disertakan; {unwrapped} slot teks di luar blok juga diperiksa secara terpisah. Frasa tidak digabungkan melintasi sel tabel atau slot sisa. Kecocokan dan cakupan asli bukan persetujuan makna atau kanon; varian yang bertumpang tindih serta dua pilihan asli untuk sum tetap dihitung terpisah.'))
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>
<style>body{{max-width:76rem;margin:auto;padding:1.4rem;font:1rem/1.55 system-ui;background:#fafbf8;color:#172d29}}a{{color:#075e66}}nav{{display:flex;gap:1.2rem;flex-wrap:wrap}}.note{{padding:1rem;background:#e7eee7;border-left:4px solid #32756a}}input{{font:inherit;padding:.6rem;max-width:95%}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;border-bottom:1px solid #cbd6ce;padding:.65rem;vertical-align:top}}code{{overflow-wrap:anywhere}}.table{{overflow-x:auto}}summary{{cursor:pointer}}:focus-visible{{outline:3px solid #9f5e00;outline-offset:3px}}@media(max-width:700px){{.choices table,.choices tbody{{display:block}}.choices thead{{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}}.choices tr:not([hidden]){{display:block;border:1px solid #cbd6ce;border-radius:.4rem;margin:1rem 0;background:white}}.choices th,.choices td{{display:block;border:0;overflow-wrap:anywhere}}.choices th::before,.choices td::before{{content:attr(data-label);display:block;font-size:.8rem;font-weight:600;color:#46655f}}.choices ol{{padding-left:1.4rem}}.term-locations{{margin-top:.6rem}}}}</style></head><body>
<nav aria-label="{'Navigation' if english else 'Navigasi'}"><a href="{course}">{'Learning map' if english else 'Peta belajar'}</a><a href="{teacher}">{'For teachers' if english else 'Untuk pengajar'}</a><a href="{other}">{'Bahasa Indonesia' if english else 'English'}</a></nav>
<main><h1>{title}</h1><p class="note">{boundary}</p><p>{'75 modules · 20 lexical choices · 36 metadata terms · 75 correction/adverse records' if english else '75 modul · 20 pilihan istilah · 36 istilah metadata · 75 catatan koreksi/masalah'}</p>
<label for="search">{'Find a module or term' if english else 'Cari modul atau istilah'}</label> <input id="search" type="search" placeholder="m81272 / bilangan"><p id="count" aria-live="polite"></p>
<h2>{'Source and translation identities' if english else 'Identitas sumber dan terjemahan'}</h2><div class="table"><table><thead><tr><th>#</th><th>{'Module' if english else 'Modul'}</th><th>{'Source bytes (EN)' if english else 'Byte sumber (EN)'}</th><th>{'Translation bytes (ID)' if english else 'Byte terjemahan (ID)'}</th><th>{'Source and identity' if english else 'Sumber dan identitas'}</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<h2>{'Native terminology choices' if english else 'Pilihan istilah asli'}</h2><p>{termsnote}</p><div class="table choices"><table><thead><tr><th>Bahasa Indonesia</th><th>{'English' if english else 'Bahasa Inggris'}</th><th>{'Scope' if english else 'Cakupan'}</th><th>ID</th></tr></thead><tbody>{''.join(termrows)}</tbody></table></div>
<h2>{'Data and provenance' if english else 'Data dan asal-usul'}</h2><p><a href="native-ledger/ledger.json">{'Complete mapped ledger (JSON)' if english else 'Ledger lengkap (JSON)'}</a> · <a href="native-ledger/term-locations.json">{'All lexical locations (JSON)' if english else 'Semua lokasi harfiah (JSON)'}</a> · <a href="native-ledger/source-lock.json">{'Input identities' if english else 'Identitas masukan'}</a> · <a href="native-ledger/source.zip">{'Complete editable source (ZIP)' if english else 'Sumber lengkap yang dapat diedit (ZIP)'}</a></p><p>{'Native correction rationales and evidence descriptions are preserved verbatim in their original language in the JSON. No new approval of those claims is implied.' if english else 'Alasan koreksi dan uraian bukti asli disimpan persis dalam bahasa asalnya di JSON. Penyimpanan ini bukan persetujuan baru atas klaim tersebut.'}</p>
<p>{'Original interface and metadata integration: OpenAI Codex — gpt-6-astra, Ultra effort. Lexical concordance and contextual review interface: OpenAI Codex — gpt-6.1-sol, Ultra effort. Not a new translation of the book; no human review claimed.' if english else 'Antarmuka asli dan integrasi metadata: OpenAI Codex — gpt-6-astra, Ultra effort. Konkordansi harfiah dan antarmuka pemeriksaan konteks: OpenAI Codex — gpt-6.1-sol, Ultra effort. Bukan terjemahan baru buku; tidak diklaim ada pemeriksaan manusia.'}</p></main>
<footer><p>OpenStax · Prealgebra 2e · <a href="native-ledger/native-LICENSE.txt">CC BY-NC-SA 4.0</a> · <a href="native-ledger/rights.jsonl">{'Native component rights' if english else 'Hak setiap komponen asli'}</a>. {'Original rights records are preserved; the interface code licence does not relicense the native material.' if english else 'Catatan hak asli tetap dipertahankan; lisensi kode antarmuka tidak mengubah lisensi bahan asli.'}</p></footer>
<script>const input=document.getElementById('search'), rows=[...document.querySelectorAll('[data-search]')]; function filter(){{const q=input.value.toLocaleLowerCase();let n=0;for(const row of rows){{row.hidden=!row.dataset.search.toLocaleLowerCase().includes(q);if(!row.hidden)n++;}}document.getElementById('count').textContent=n+' / '+rows.length;}}input.addEventListener('input',filter);filter();</script></body></html>'''.encode('utf-8')


def build(dest):
    lock = json.loads((dest / 'input/source-lock.json').read_bytes())
    if lock.get('term_locations'):
        require(lock['term_locations']['generator'] == fact(ROOT / 'scripts/a00_term_locations_v1.py'), 'Concordance generator identity differs')
    raw = {}
    for r in lock['snapshots'] + ([lock['term_locations']] if lock.get('term_locations') else []):
        body = checked_path(dest / 'input', r['path']).read_bytes()
        require(len(body) == r['bytes'] and sha(body) == r['sha256'], 'Snapshot identity differs')
        raw[r['path']] = body
    data = normalize(raw, lock)
    save(dest / 'data/ledger.json', data)
    save(dest / 'views/ledger.html', render(data))
    save(dest / 'views/ledger-en.html', render(data, True))
    outputs = ['data/ledger.json', 'views/ledger.html', 'views/ledger-en.html']
    archive = dest / 'data/source.zip'
    prefix = BASE.relative_to(ROOT).as_posix() + '/'
    members = {prefix + name: (dest / name).read_bytes() for name in outputs}
    members.update({prefix + 'input/' + name: body for name, body in raw.items()})
    members[prefix + 'input/source-lock.json'] = (dest / 'input/source-lock.json').read_bytes()
    for name in ['a00-native-ledger-v1.py','a00_term_locations_v1.py','test-a00-native-ledger-v1.py','test-a00-native-ledger-ui-v1.mjs']:
        members['scripts/' + name] = (ROOT / 'scripts' / name).read_bytes()
    members['LICENSE'] = (ROOT / 'LICENSE').read_bytes()
    members['README.txt'] = ('Bangun ulang / Rebuild: python -B scripts/a00-native-ledger-v1.py\n'
                            'Uji / Test: python -B scripts/test-a00-native-ledger-v1.py\n'
                            'Python 3 dan Node.js diperlukan / Python 3 and Node.js required.\n'
                            'Paket berisi metadata, cuplikan konkordansi terbatas dan sumber antarmuka, bukan buku lengkap.\n'
                            'Metadata, bounded concordance excerpts and interface sources, not whole books.\n').encode('utf-8')
    members['README.txt'] += ('MIT: kode antarmuka / interface code. Catatan hak bahan asli / native material rights:\n'
                              + prefix + 'input/native-LICENSE.txt\n' + prefix + 'input/rights.jsonl\n').encode('utf-8')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, body in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(2026,9,30,0,0,0))
            info.external_attr = 0o100644 << 16
            z.writestr(info, body, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    outputs.append('data/source.zip')
    save(dest / 'manifest.json', {'schema': 'a00-native-ledger-adapter/1', 'course_id': 'A00',
          'source_lock': fact(dest / 'input/source-lock.json'), 'generator': fact(Path(__file__)),
          'outputs': [{'path': p, **fact(dest / p)} for p in outputs],
          'scope': data['verification'], 'native_discrepancies': len(data['source_map_discrepancies'])})
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--intake', type=Path)
    parser.add_argument('--term-intake', type=Path)
    parser.add_argument('--destination', type=Path, default=BASE)
    args = parser.parse_args()
    if args.intake:
        intake(args.intake.resolve(), args.destination)
        freeze_term_locations(args.intake.resolve(), args.destination)
    elif args.term_intake:
        freeze_term_locations(args.term_intake.resolve(), args.destination)
    result = build(args.destination)
    print(json.dumps({'status': 'pass', 'modules': len(result['modules']), 'terms': len(result['terms']),
                      'corrections': len(result['corrections']), 'discrepancies': len(result['source_map_discrepancies']),
                      'semantic_review': False}))
