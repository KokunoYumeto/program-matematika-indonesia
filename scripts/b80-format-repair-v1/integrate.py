"""Project only anonymously verified native assets into the bilingual hub."""
import json
from finalize import ROOT, OUT, read
from publish_github import public_identity

final = read(OUT / 'FINAL_FORMAT_VALIDATION.json')
rows, public = [], []
labels = {
    'id': ['PDF turunan — 135 halaman', 'LaTeX kumulatif untuk PDF turunan', 'Sumber lengkap PDF dan EPUB', 'EPUB yang diperbaiki'],
    'en': ['Derived PDF — 133 pages', 'Cumulative LaTeX for the derived PDF', 'Complete PDF and EPUB source', 'Repaired EPUB']}
formats = ['PDF', 'TEX', 'ZIP', 'EPUB']
slugs = ['format-pdf', 'format-tex', 'format-source', 'format-epub']
for lang in ('id', 'en'):
    release = read(OUT / lang / 'GITHUB_FORMAT_PUBLICATION.json')
    assert release['status'] == 'published_and_anonymously_verified'
    public.extend(release['anonymous_readback'])
    files = final['editions'][lang]['files_in_reading_order']
    for i, f in enumerate(files):
        fact = next(row for row in release['anonymous_readback'] if row['file'] == f['file'])
        assert all(fact[k] == f[k] for k in ('bytes', 'sha256'))
        lid = labels['id'][i] + (' — bahasa Inggris' if lang == 'en' else ' — Bahasa Indonesia')
        len_ = labels['en'][i] + (' — Indonesian' if lang == 'id' else ' — English')
        if i == 0:
            lid = lid.replace('135', str(final['editions'][lang]['pdf_pages']))
            len_ = len_.replace('133', str(final['editions'][lang]['pdf_pages']))
        rows.append({'courseId': 'B80', 'id': 'B80:' + lang + '-' + slugs[i], 'href': fact['url'],
                     'labels': {'id': lid, 'en': len_},
                     'notes': {
                         'id': 'Edisi format 3 Oktober 2026: PDF, LaTeX, ZIP sumber dan EPUB membentuk satu set yang cocok. PDF dan EPUB direproduksi byte-identik; EPUBCheck tanpa kesalahan/peringatan. Teks asli tetap; Quarto tetap sumber utama. Bukan penerjemahan atau peninjauan matematika baru. Rujukan eksternal memerlukan internet.',
                         'en': 'Format edition 3 October 2026: PDF, LaTeX, source ZIP and EPUB form one matching set. PDF and EPUB rebuild byte-identically; EPUBCheck has no errors/warnings. Original text is preserved; Quarto remains the native master. Not a new translation or mathematical review. External references need internet.'},
                     'kind': ['companion', 'editable_source', 'source_archive', 'companion'][i],
                     'format': formats[i], 'offlineAfterDownload': i == 3,
                     'evidenceFile': 'docs/interface/evidence/b80-repaired-formats.json',
                     'contentLanguage': lang, 'bytes': f['bytes'], 'sha256': f['sha256']})
    zenodo = read(OUT / lang / 'ZENODO_FORMAT_PUBLICATION.json')
    assert zenodo['status'] == 'published_and_anonymously_verified'
    record_url = 'https://zenodo.org/records/' + str(zenodo['draft_id'])
    record_fact = {'url':record_url, **public_identity(record_url)}
    public.append(record_fact)
    public.extend(zenodo['public_readback'])
    final['editions'][lang]['preservation'] = {
        'doi':zenodo['doi'], 'url':record_url, 'preview':zenodo['preview'],
        'rendered_file_order':zenodo['rendered_file_order_verified'],
        'original_records_unchanged':True, 'all_files_anonymously_hash_verified':True}
    rows.append({'courseId':'B80', 'id':'B80:'+lang+'-format-record', 'href':record_url,
                 'labels':{'id':'Arsip Zenodo — edisi format '+('Bahasa Indonesia' if lang=='id' else 'bahasa Inggris'),
                           'en':'Zenodo archive — '+('Indonesian' if lang=='id' else 'English')+' format edition'},
                 'notes':rows[-1]['notes'], 'kind':'companion', 'format':'HTML', 'offlineAfterDownload':False,
                 'evidenceFile':'docs/interface/evidence/b80-repaired-formats.json',
                 'contentLanguage':lang, 'bytes':record_fact['bytes'], 'sha256':record_fact['sha256']})
target = ROOT / 'docs/interface/supplemental-readers.js'
text = target.read_text(encoding='utf-8')
start, end = '  // BEGIN B80 FORMAT PAIRS\n', '  // END B80 FORMAT PAIRS\n'
block = start + ',\n'.join('  ' + json.dumps(r, ensure_ascii=False, indent=2).replace('\n', '\n  ') for r in rows) + ',\n' + end
if start in text:
    a = text.index(start); b = text.index(end, a) + len(end)
    text = text[:a] + block + text[b:]
else:
    text = text.replace('export const supplementalReaders = [\n', 'export const supplementalReaders = [\n' + block, 1)
text = text.replace('Perbaikan format masih diperlukan.', 'Berkas historis ini dipertahankan; EPUB yang diperbaiki tersedia pada set format 3 Oktober 2026.')
text = text.replace('Format repair is still needed.', 'This historical file is retained; a repaired EPUB is available in the 3 October 2026 format set.')
text = text.replace('Tidak memuat LaTeX kumulatif; persyaratan itu belum terpenuhi.', 'Paket Quarto historis tidak memuat LaTeX kumulatif; LaTeX untuk PDF turunan tersedia pada set format 3 Oktober 2026.')
text = text.replace('No cumulative LaTeX is included; that requirement remains open.', 'This historical Quarto package contains no cumulative LaTeX; LaTeX for the derived PDF is available in the 3 October 2026 format set.')
target.write_text(text, encoding='utf-8', newline='\n')
proof = {**final, 'schema': 'central-supplemental-reader-evidence/1',
         'status': 'published_and_anonymously_verified', 'course_id': 'B80', 'public_readback': public,
         'scope': 'Paired derived format exports; original native releases and source masters preserved.'}
(ROOT / 'docs/interface/evidence/b80-repaired-formats.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({'new_links': len(rows), 'public_files_verified': len(public)}))
