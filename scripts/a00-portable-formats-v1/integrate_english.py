"""Project verified English A00 formats into the existing bilingual interface.

Only four additive resource bindings and their public evidence are generated.
Native books, Indonesian bindings and all other course data remain untouched.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/a00-english-portable-formats-v1'
EVIDENCE = 'docs/interface/evidence/a00-english-portable-formats.json'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
identity = lambda b: {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def main():
    final = read(OUT / 'FINAL_FORMAT_VALIDATION.json')
    github = read(OUT / 'GITHUB_FORMAT_PUBLICATION.json')
    baseline = read(OUT / 'hub-parent/BASELINE.json')
    assert final['status'] == 'validated_local_not_publication'
    assert final['clean_pdf_and_epub_byte_identical']
    assert github['status'] == 'published_and_anonymously_verified'
    assert github['release'] == 'https://github.com/KokunoYumeto/openstax-prealgebra-2e-original-en/releases/tag/v1.0.0'
    edition = final['editions']['en']
    assert edition['modules'] == 75 and edition['pdf_pages'] == 1591
    files = edition['files_in_reading_order']
    assert [f['file'] for f in files] == ['00-a00-en.pdf', '01-a00-en.tex', '02-a00-en-source.zip', '03-a00-en.epub']
    labels = {
        'id': ['PDF Praljabar bahasa Inggris — 1.591 halaman',
               'LaTeX kumulatif untuk PDF Praljabar bahasa Inggris',
               'Sumber lengkap PDF dan EPUB Praljabar bahasa Inggris',
               'EPUB Praljabar bahasa Inggris'],
        'en': ['English Prealgebra PDF — 1,591 pages',
               'Cumulative LaTeX for the English Prealgebra PDF',
               'Complete English Prealgebra PDF and EPUB source',
               'English Prealgebra EPUB'],
    }
    notes = {
        'id': 'Edisi format 5 Oktober 2026, teks asli bahasa Inggris: 75 modul. PDF, LaTeX kumulatif, ZIP sumber dan EPUB merupakan satu set yang cocok; PDF dan EPUB dibangun ulang byte-identik dari paket sumber. Sumber utama CNXML/MathML dan HTML terdahulu tetap tersedia. Penulis: Lynn Marecek, MaryAnne Anthony-Smith dan Andrea Honeycutt Mathis, OpenStax. Penyiapan HTML: OpenAI Codex gpt-5.6-sol, upaya Ultra. Ekspor dan integrasi format: OpenAI Codex — GPT-6 Astra, upaya Ultra. Bukan terjemahan baru atau peninjauan matematika/manusia. Lisensi dan kredit setiap komponen tersedia dalam paket sumber. Tautan eksternal memerlukan internet.',
        'en': 'Format edition 5 October 2026, original English text: 75 modules. PDF, cumulative LaTeX, source ZIP and EPUB form one matching set; PDF and EPUB rebuild byte-identically from the source package. The CNXML/MathML master and earlier HTML remain available. Authors: Lynn Marecek, MaryAnne Anthony-Smith and Andrea Honeycutt Mathis, OpenStax. HTML preparation: OpenAI Codex gpt-5.6-sol, Ultra effort. Format exports and integration: OpenAI Codex — GPT-6 Astra, Ultra effort. Not a new translation, mathematical review or human review. Component licences and credits are included in the source package. External links need internet.',
    }
    rows, public = [], []
    for index, file in enumerate(files):
        assert identity((OUT / 'output' / file['file']).read_bytes()) == {k: file[k] for k in ('bytes', 'sha256')}
        matches = [r for r in github['anonymous_readback'] if r['file'] == file['file']]
        assert len(matches) == 1
        fact = matches[0]
        assert all(fact[k] == file[k] for k in ('bytes', 'sha256'))
        assert fact['url'] == github['release'].replace('/tag/', '/download/') + '/' + file['file']
        public.append(fact)
        rows.append({
            'courseId': 'A00', 'id': 'A00:en-format-' + ['pdf', 'tex', 'source', 'epub'][index],
            'href': fact['url'], 'labels': {lang: labels[lang][index] for lang in labels},
            'notes': notes, 'kind': ['companion', 'editable_source', 'source_archive', 'companion'][index],
            'format': ['PDF', 'TEX', 'ZIP', 'EPUB'][index], 'offlineAfterDownload': index in (0, 3),
            'evidenceFile': EVIDENCE, 'contentLanguage': 'en',
            'bytes': file['bytes'], 'sha256': file['sha256'],
        })
    path = 'docs/interface/supplemental-readers.js'
    target = ROOT / path
    text = target.read_text(encoding='utf-8')
    old = (OUT / 'hub-parent' / path).read_text(encoding='utf-8')
    start, end = '  // BEGIN A00 ENGLISH FORMAT PAIRS\n', '  // END A00 ENGLISH FORMAT PAIRS\n'
    block = start + ',\n'.join('  ' + json.dumps(r, ensure_ascii=False, indent=2).replace('\n', '\n  ') for r in rows) + ',\n' + end
    if start in text:
        a = text.index(start)
        b = text.index(end, a) + len(end)
        assert text[:a] + text[b:] == old, 'Unrelated or concurrent resource edit'
        text = text[:a] + block + text[b:]
    else:
        assert text == old, 'Resources changed after baseline'
        anchor = '  // END A00 FORMAT PAIRS\n'
        assert text.count(anchor) == 1
        text = text.replace(anchor, anchor + block, 1)
    target.write_text(text, encoding='utf-8', newline='\n')
    proof = {
        'schema': 'central-supplemental-reader-evidence/1', 'course_id': 'A00',
        'status': 'published_and_anonymously_verified', 'content_language': 'en',
        'edition': edition, 'public_readback': public, 'parent': baseline['parent'],
        'preservation': {'github_release': github['release'], 'inherited_assets_preserved': 4,
                         'all_eight_release_files_anonymously_hash_verified': len(github['anonymous_readback']) == 8,
                         'zenodo_english_record': None, 'zenodo_status': 'lineage_not_yet_resolved'},
        'checks': {'source_archive_files_verified': final['source_archive_files_verified'],
                   'pdf_and_epub_byte_identical_rebuild': True, 'epubcheck': final['epubcheck'],
                   'visual_scope': final['visual_scope']},
        'source_model': 'CNXML/MathML remains the native master; LaTeX is the editable print export.',
        'scope': 'English A00 resources in both interfaces; no native replacement, new translation, mathematical review or programme completion.',
        'provenance': {'original_authors': ['Lynn Marecek', 'MaryAnne Anthony-Smith', 'Andrea Honeycutt Mathis'],
                       'original_publisher': 'OpenStax',
                       'html_preparation': {'model': 'gpt-5.6-sol', 'effort': 'ultra'},
                       'format_and_integration': {'model': 'gpt-6-astra', 'effort': 'ultra'}},
        'evidence_receipts': {p: identity((OUT / p).read_bytes()) for p in
                              ['FINAL_FORMAT_VALIDATION.json', 'GITHUB_FORMAT_PUBLICATION.json']},
    }
    (ROOT / EVIDENCE).write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'state': 'integrated', 'language': 'en', 'links': len(rows)}))


if __name__ == '__main__':
    main()
