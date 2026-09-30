"""Render the admitted native term/correction metadata, with explicit audit scope."""
import argparse
from collections import Counter, defaultdict
import hashlib
from html import escape
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/c130-native-ledger-v1'

def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()

def fact(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

WORDS = {
 'id': {'title': 'Riset Operasi: istilah dan catatan koreksi',
        'lead': 'Cari padanan istilah buku dan lihat catatan koreksi beserta identitas sumbernya.',
        'search': 'Cari istilah, koreksi, konsep, atau ID', 'all': 'Semua bahan', 'terms': 'Istilah',
        'corrections': 'Koreksi', 'program': 'Kembali ke program', 'teacher': 'Pilih latihan dan bahan pengajar',
        'read': 'Buka buku Bahasa Indonesia', 'source': 'Sumber asli', 'preferred': 'Pilihan dalam buku',
        'evidence': 'Bukti yang dicatat pembuat buku', 'concept': 'Konsep', 'nativeStatus': 'Status asli',
        'contexts': 'Konteks menurut ID konsep', 'units': 'Unit yang terkait', 'records': 'catatan',
        'count': 'Hasil yang ditampilkan', 'details': 'Rujukan dan identitas', 'data': 'Unduh metadata lengkap',
        'zip': 'Unduh sumber halaman', 'audit': 'Lihat hasil pemeriksaan',
        'gap': 'Belum ada rujukan teks yang dipastikan',
        'quote': 'Kutipan asli dari catatan pembuat buku; bahasa asli dipertahankan',
        'skip': 'Lewati navigasi dan buka isi halaman',
        'contextLimit': 'Sepuluh rujukan pertama ditampilkan; metadata lengkap memuat semua ID. Hubungan konsep tidak menyatakan bahwa istilah muncul secara harfiah di setiap bagian.',
        'scope': '140 pilihan istilah dan 94 catatan koreksi disalin dari backend asli. Kata “approved” dan bukti di bawah adalah catatan pembuat buku. Pemeriksaan ini membuktikan identitas metadata dan kaitan sumber; penggunaan kanon Bahasa Indonesia dan kebenaran setiap koreksi belum dinilai ulang.',
        'locations': 'Seluruh 5.186 catatan dengan teks target cocok dengan teks yang dirilis: 5.184 pada baris yang dinyatakan dan dua melalui penggabungan bagian asli. Sebanyak 21 rujukan yang sebelumnya belum pasti telah diperiksa. Seluruh 5.525 identitas segmen tetap dipertahankan.',
        'review': 'Periksa 21 rujukan yang diperbaiki', 'before': 'Hasil sebelumnya', 'after': 'Hasil sekarang',
        'fileGuard': 'Identitas berkas utuh', 'match': 'Cocok', 'mismatch': 'Berbeda',
        'fileLimit': 'Satu dari dua berkas yang memakai penggabungan bagian mempunyai SHA-256 berbeda dari identitas berkas utuh yang dicatat pembuat buku. Bagian teks yang ditunjuk cocok persis, tetapi kecocokan seluruh berkas belum terbukti. Ini bukan persetujuan kanon atau bukti pembangunan ulang buku.',
        'reviewData': 'Unduh bukti pemeriksaan rujukan', 'nativeHash': 'SHA-256 catatan asli',
        'declared_lines_exact_text': 'Teks cocok pada baris yang dinyatakan',
        'declared_native_alignment_parts_exact_text': 'Teks cocok melalui penggabungan bagian asli',
        'ambiguous_text_occurrences': 'Beberapa kemunculan teks; rujukan belum pasti',
        'text_not_found': 'Teks belum ditemukan oleh pemeriksaan sebelumnya',
        'offline': 'Pencarian dapat dipakai tanpa jaringan setelah halaman dan berkas JS/CSS disimpan. Buku diunduh terpisah. Tidak ada akun, pelacakan, atau penyimpanan peramban.',
        'credit': 'Audit dan proyeksi awal: OpenAI Codex — gpt-6-astra, Ultra effort. Halaman dan penyempurnaan integrasi: OpenAI Codex — gpt-6.1-sol, Ultra effort. Riwayat AI dan atribusi buku tetap mengikuti edisi aslinya.'},
 'en': {'title': 'Operations Research: terminology and correction records',
        'lead': 'Find the book’s terminology choices and inspect correction records with their source identities.',
        'search': 'Search terms, corrections, concepts or IDs', 'all': 'All materials', 'terms': 'Terminology',
        'corrections': 'Corrections', 'program': 'Return to program', 'teacher': 'Choose exercises and teacher materials',
        'read': 'Open the Indonesian book', 'source': 'Original term', 'preferred': 'Choice in the book',
        'evidence': 'Evidence recorded by the book producer', 'concept': 'Concept', 'nativeStatus': 'Native status',
        'contexts': 'Contexts associated by concept ID', 'units': 'Related units', 'records': 'records',
        'count': 'Displayed results', 'details': 'References and identities', 'data': 'Download complete metadata',
        'zip': 'Download page source', 'audit': 'Inspect audit results',
        'gap': 'No confirmed text reference yet',
        'quote': 'Original quotation from the producer’s record; original language retained',
        'skip': 'Skip navigation and open page content',
        'contextLimit': 'The first ten references are shown; complete metadata retains every ID. A concept relationship does not establish a literal occurrence of the term in each passage.',
        'scope': 'The 140 terminology choices and 94 correction records come from the native backend. Labels such as “approved” and the evidence below are producer records. This audit checks metadata identity and source relationships; it has not repeated the Indonesian canon review or verified every correction mathematically.',
        'locations': 'All 5,186 records containing target text match the released text: 5,184 at declared lines and two through native multi-part alignment. The 21 formerly unresolved references have been checked. All 5,525 segment identities remain intact.',
        'review': 'Inspect the 21 repaired references', 'before': 'Previous result', 'after': 'Current result',
        'fileGuard': 'Whole-file identity', 'match': 'Matches', 'mismatch': 'Differs',
        'fileLimit': 'One of the two alignment files has a different SHA-256 from the producer’s declared whole-file identity. The referenced text parts reconstruct exactly, but whole-file equality is not proved. This is not canon approval or a native book rebuild.',
        'reviewData': 'Download reference-review evidence', 'nativeHash': 'Native record SHA-256',
        'declared_lines_exact_text': 'Exact text at declared lines',
        'declared_native_alignment_parts_exact_text': 'Exact text through native multi-part alignment',
        'ambiguous_text_occurrences': 'Multiple text occurrences; reference unresolved',
        'text_not_found': 'Text not found by the previous check',
        'offline': 'Search works without a network after saving the page and its JS/CSS files. Download the book separately. No account, tracking or browser storage is used.',
        'credit': 'Initial audit and projection: OpenAI Codex — gpt-6-astra, Ultra effort. Page and integration refinements: OpenAI Codex — gpt-6.1-sol, Ultra effort. The book retains its own AI history and attribution.'}
}

def render(view, lock, reader, lang, review):
    w = WORDS[lang]
    e = lambda value: escape(str(value), quote=True)
    segments = {r['id']: r for r in view['segments']}
    units = {r['id']: r for r in view['units']}
    cards = []
    for term in view['terms']:
        row = term['native']
        refs = []
        for sid in term['concept_segment_ids'][:10]:
            segment = segments[sid]
            loc = segment['verification']['target']
            location = (loc.get('member', segment.get('target_path', segment.get('source_path', '')))
                        + ' · ' + str(loc.get('line_range', '')))
            if loc['state'] not in {'declared_lines_exact_text', 'unique_exact_text_relocated', 'declared_native_alignment_parts_exact_text'}:
                location += ' · ' + w['gap']
            refs.append(f'<li><code>{e(sid)}</code><p>{e(location)}</p></li>')
        search = ' '.join([row['source_term'], row['preferred'], row['id'], row['concept_id'], str(row.get('evidence', ''))])
        cards.append(f'''<article class="record" data-kind="term" data-search="{e(search.casefold())}">
<h3>{e(row['preferred'])}</h3><dl><dt>{w['source']}</dt><dd lang="en">{e(row['source_term'])}</dd>
<dt>{w['concept']}</dt><dd><code>{e(row['concept_id'])}</code></dd><dt>{w['nativeStatus']}</dt><dd><code>{e(row['status'])}</code></dd></dl>
<details><summary>{w['details']}</summary><p><code>{e(row['id'])}</code></p><h4>{w['evidence']}</h4><p class="quotation-label">{w['quote']}</p><blockquote lang="en">{e(row.get('evidence', ''))}</blockquote>
<p>{w['contexts']}: {len(term['concept_segment_ids'])} {w['records']}</p><ul>{''.join(refs)}</ul><p>{w['contextLimit']}</p></details></article>''')
    correction_languages = Counter()
    for row in view['corrections']:
        # The frozen o018 chapter records are Indonesian; its chronology record
        # and the r017 rationales are English. This is a bounded witnessed map,
        # not automatic language detection or a translation of the quotations.
        quote_lang = 'id' if row['id'].startswith('correction.o018.') and row['id'] != 'correction.o018.result-order-chronology' else 'en'
        correction_languages[quote_lang] += 1
        linked = ''.join(f'<li><code>{e(uid)}</code> · {e(units[uid].get("title_target") or units[uid].get("title_source") or uid)}</li>' for uid in row['affected_unit_ids'])
        evidence = json.dumps(row['evidence'], ensure_ascii=False, indent=2)
        search = ' '.join([row['id'], row.get('rationale', ''), row.get('correction_type', ''), evidence])
        cards.append(f'''<article class="record" data-kind="correction" data-search="{e(search.casefold())}">
<h3><code>{e(row['id'])}</code></h3><p class="quotation-label">{w['quote']}</p><blockquote lang="{quote_lang}">{e(row.get('rationale', ''))}</blockquote><details><summary>{w['details']}</summary>
<h4>{w['units']}</h4><ul>{linked}</ul><h4>{w['evidence']}</h4><pre>{e(evidence)}</pre></details></article>''')
    assert correction_languages == {'id': 17, 'en': 77}, 'Native quotation language scope changed'
    reviewed = []
    for row in review['records']:
        before, after = row['before_target_verification'], row['after_target_verification']
        guard = after.get('alignment', {}).get('target_file_guard')
        file_proof = ''
        if guard:
            state = w['match'] if guard['whole_file_guard_matches'] else w['mismatch']
            file_proof = f'<dt>{w["fileGuard"]}</dt><dd>{state}<p><code>{e(guard["native_expected_sha256"])}</code> → <code>{e(guard["released_file"]["sha256"])}</code></p></dd>'
        reviewed.append(f'''<li class="location-proof" data-segment-id="{e(row['id'])}"><details>
<summary><code>{e(row['id'])}</code></summary><p><code>{e(after['member'])}</code> · {e(after['line_range'])}</p>
<dl><dt>{w['before']}</dt><dd>{w[before['state']]}</dd><dt>{w['after']}</dt><dd>{w[after['state']]}</dd>
<dt>{w['nativeHash']}</dt><dd><code>{e(row['native_record_sha256'])}</code></dd>{file_proof}</dl></details></li>''')
    source = lock['archives']['source']['url']
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{w['title']}</title><link rel="stylesheet" href="ledger.css"></head><body>
<a class="skip" href="#main">{w['skip']}</a><header><a href="../../{lang}/index.html#course-C130">{w['program']}</a>
<nav aria-label="{'Bahasa' if lang == 'id' else 'Language'}"><a href="ledger.html" lang="id" {'aria-current="page"' if lang == 'id' else ''}>Bahasa Indonesia</a> · <a href="ledger.en.html" lang="en" {'aria-current="page"' if lang == 'en' else ''}>English</a></nav></header>
<main id="main"><p>C130 · 140 {w['terms']} · 94 {w['corrections']}</p><h1>{w['title']}</h1><p class="lead">{w['lead']}</p>
<p><a href="{e(reader)}">{w['read']}</a> · <a href="../c130-teacher/C130.teacher{'.en' if lang == 'en' else ''}.html">{w['teacher']}</a></p>
<p class="scope">{w['scope']}</p><p>{w['locations']}</p><p class="scope">{w['fileLimit']}</p>
<p><a href="#location-review">{w['review']}</a></p>
<div class="filters"><label>{w['search']}<input id="query" type="search"></label><label>{w['all']}<select id="kind"><option value="">{w['all']}</option><option value="term">{w['terms']}</option><option value="correction">{w['corrections']}</option></select></label></div>
<p id="count" aria-live="polite" data-label="{w['count']}">234 / 234</p><section aria-label="{w['all']}">{''.join(cards)}</section>
<section id="location-review" aria-labelledby="review-heading"><h2 id="review-heading">{w['review']}</h2><ul>{''.join(reviewed)}</ul><p><a href="location-review.json">{w['reviewData']}</a></p></section>
<p>{w['offline']}</p><p><a href="projection.json">{w['data']}</a> · <a href="audit.json">{w['audit']}</a> · <a href="c130-native-ledger-source-v1.zip">{w['zip']}</a> · <a href="{e(source)}">{'Sumber buku' if lang == 'id' else 'Book source'}</a></p></main>
<footer><p>{w['credit']}</p></footer><script src="ledger.js" defer></script></body></html>'''

def validate(view, snapshot, audit, review, lock, baseline):
    assert view['schema'] == 'c130-native-ledger-view/1' and view['course_id'] == 'C130'
    assert [row['native'] for row in view['terms']] == snapshot['terms'], 'Native term claims changed'
    for name in ['concepts', 'corrections', 'rights']:
        assert view[name] == snapshot[name], 'Native records changed: ' + name
    indices = {}
    for name, count in {'terms': 140, 'concepts': 128, 'corrections': 94, 'rights': 21, 'segments': 5525, 'units': 1993}.items():
        rows = [r['native'] for r in view[name]] if name == 'terms' else view[name]
        assert all(isinstance(r.get('id'), str) and r['id'] for r in rows), 'Missing identity: ' + name
        indices[name] = {r['id']: r for r in rows}
        assert len(indices[name]) == len(rows) == count, 'Duplicate or missing identities: ' + name
        assert audit['counts'][name] == count, 'Audit count differs: ' + name
    uses = defaultdict(list)
    for row in view['segments']:
        assert 'source_text' not in row and 'target_text' not in row, 'Book prose copied'
        assert row['unit_id'] in indices['units'], 'Unknown segment unit'
        assert row['rights_component_id'] in indices['rights'], 'Unknown segment rights'
        for cid in row.get('concept_ids', []):
            assert cid in indices['concepts'], 'Unknown segment concept'
            uses[cid].append(row['id'])
    for term in view['terms']:
        assert term['native']['concept_id'] in indices['concepts'], 'Unknown term concept'
        assert term['concept_segment_ids'] == sorted(uses[term['native']['concept_id']]), 'Invented term occurrence mapping'
        assert term['audit']['semantic_canon_review'] is False, 'Invented term canon review'
        assert term['audit']['mapping_scope'] == 'native_concept_relation_not_lexical_occurrence'
    for row in view['corrections']:
        assert all(uid in indices['units'] for uid in row['affected_unit_ids']), 'Unknown correction unit'
    for side in ['source', 'target']:
        actual = dict(Counter(r['verification'][side]['state'] for r in view['segments']))
        assert audit['segment_checks'][side] == actual, 'Location audit counts differ'
    assert not view['audit']['issues'] and audit['native_digest_failures'] == 0
    for field in ['semantic_canon_review', 'whole_native_rebuild', 'book_prose_copied']:
        assert view['audit'][field] is False, 'Unsupported validation claim'
    assert view['audit']['native_qa_states_are_claims'] is True
    assert view['audit']['projection_policy']['reverse_whole_monolith_from_projection_claimed'] is False
    assert audit['segment_checks']['target'] == {'declared_lines_exact_text': 5184,
        'declared_native_alignment_parts_exact_text': 2, 'no_native_text': 339}
    assert audit['segment_checks']['source'] == {'declared_lines_exact_text': 339,
        'english_source_not_rechecked_in_target_archives': 2293, 'no_native_text': 2893}
    assert review['schema'] == 'c130-location-review/1' and review['course_id'] == 'C130'
    assert fact(encoded(review)) == audit['location_review']
    assert fact(encoded(baseline)) == review['baseline'] == lock['location_review_baseline']
    assert review['baseline']['sha256'] == 'bfb6fb2832a2659c24ba67576edc7a9373ae0f7d80e024ba921c88b481945a4f'
    assert review['native_alignment_authority'] == lock['native_alignment_authority']
    assert lock['native_alignment_authority']['input']['sha256'] == 'c70da303e2feade5dd52092b8e15b722d0ea8cd5e26be63d8cb001739b55daba'
    assert lock['native_alignment_authority']['exporter']['sha256'] == '3edee807a41c766c84efbda2a67b209b3d41a8afa7dbf00252ee3cdd846eedb9'
    assert len(review['records']) == len({r['id'] for r in review['records']}) == 21
    assert [{k: v for k, v in r.items() if k != 'after_target_verification'} for r in review['records']] == baseline['records']
    for row in review['records']:
        current = indices['segments'][row['id']]
        assert row['native_record_sha256'] == current['canonical_native_record_sha256']
        assert row['after_target_verification'] == current['verification']['target']
        assert row['before_target_verification']['state'] in {'text_not_found', 'ambiguous_text_occurrences'}
        assert row['after_target_verification']['state'] in {'declared_lines_exact_text', 'declared_native_alignment_parts_exact_text'}
    mismatches = 0
    for row in view['segments']:
        loc = row['verification']['target']
        if loc['state'] != 'declared_native_alignment_parts_exact_text':
            continue
        aligned = loc['alignment']
        assert aligned['authority'] == lock['native_alignment_authority']
        assert aligned['reconstructed_content_sha256'] == row['target_content_sha256']
        assert len(aligned['parts']) >= 2
        assert [min(p['line_range'][0] for p in aligned['parts']), max(p['line_range'][1] for p in aligned['parts'])] == loc['line_range']
        guard = aligned['target_file_guard']
        equal = guard['native_expected_sha256'] == guard['released_file']['sha256']
        assert guard['whole_file_guard_matches'] is equal, 'Whole-file mismatch hidden'
        mismatches += not equal
    assert mismatches == audit['native_alignment_whole_file_guard_mismatches'] == 1
    assert audit['resolved_previously_unresolved_target_locations'] == 21 and audit['unresolved_target_locations'] == 0
    for field in ['native_records_changed', 'semantic_canon_review', 'whole_native_rebuild', 'overall_backend_complete']:
        assert review[field] is False
    assert audit['semantic_canon_review'] is False and audit['whole_native_rebuild'] is False and audit['overall_backend_complete'] is False

def build(base, out):
    raw = (base / 'projection.json').read_bytes()
    audit_raw = (base / 'audit.json').read_bytes()
    audit = json.loads(audit_raw)
    assert fact(raw) == audit['projection'], 'Projection audit identity differs'
    assert audit['native_digest_failures'] == 0 and audit['counts']['terms'] == 140
    view = json.loads(raw)
    lock = json.loads((base / 'input/source-lock.json').read_bytes())
    snapshot_raw = (base / 'input/native-records.json').read_bytes()
    assert fact(snapshot_raw) == lock['native_records_snapshot'], 'Native record snapshot identity differs'
    snapshot = json.loads(snapshot_raw)
    review_raw = (base / 'location-review.json').read_bytes()
    review = json.loads(review_raw)
    baseline = json.loads((base / 'input/location-review-baseline.json').read_bytes())
    validate(view, snapshot, audit, review, lock, baseline)
    reader = json.loads((ROOT / 'backend/course-capsule-v1/adapters/c130-teacher-v1/mapping.json').read_bytes())['reader']['url']
    files = {'projection.json': raw, 'audit.json': audit_raw, 'location-review.json': review_raw}
    for lang, suffix in [('id', ''), ('en', '.en')]:
        files['ledger' + suffix + '.html'] = render(view, lock, reader, lang, review).encode()
    for name in ['ledger.js', 'ledger.css']:
        files[name] = (base / 'ui' / name).read_bytes()
    source = {str(path.relative_to(ROOT)).replace('\\', '/'): path.read_bytes() for path in
              [ROOT / 'scripts/c130-native-ledger-v1.py', Path(__file__),
               ROOT / 'scripts/test-c130-native-ledger-v1.py', ROOT / 'scripts/test-c130-native-ledger-ui-v1.mjs', base / 'README.txt',
               base / 'projection.json', base / 'audit.json', base / 'input/source-lock.json',
               base / 'input/native-records.json', base / 'input/location-review-baseline.json', base / 'location-review.json',
               base / 'ui/ledger.js', base / 'ui/ledger.css',
               ROOT / 'backend/course-capsule-v1/adapters/c130-teacher-v1/mapping.json']}
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(source.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    files['c130-native-ledger-source-v1.zip'] = buffer.getvalue()
    for name, data in files.items():
        out.mkdir(parents=True, exist_ok=True)
        (out / name).write_bytes(data)
    receipt = {'schema': 'c130-native-ledger-build/1', 'state': 'built_local_not_admitted',
               'projection': fact(raw), 'files': {name: fact(data) for name, data in sorted(files.items())},
               'source_members': {name: fact(data) for name, data in sorted(source.items())},
               'terms': 140, 'corrections': 94, 'semantic_canon_review': False,
               'overall_backend_complete': False}
    (out / 'build-receipt.json').write_bytes(encoded(receipt))
    print(json.dumps({'state': receipt['state'], 'files': len(files), 'source_zip': fact(buffer.getvalue())}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, default=BASE)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    build(args.base, args.out or args.base / 'site')
