"""Build small source-complete derived-format packages; never mutate native releases."""
import hashlib
import json
import re
import zipfile
from pathlib import Path

from build_b80 import archive_inventory, xml, NS

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'outputs/b80-format-repair-v1'
INPUT = ROOT / 'outputs/b80-formats-20261003'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def package(language, private_credit):
    work = OUTPUT / language
    source = json.loads((work / 'SOURCE_EXPORT_RECEIPT.json').read_text(encoding='utf-8'))
    build = json.loads((work / 'PDF_BUILD_RECEIPT.json').read_text(encoding='utf-8-sig'))
    assert all(source['semantic_roundtrip'].values())
    assert build['source_sha256'] == source['tex_sha256']
    assert build['status'] == 'compiled_pending_visual_review'
    assert build['overfull_hboxes'] == build['overfull_vboxes'] == 0
    payload = {f'01-b80-{language}.tex': (work / f'01-b80-{language}.tex').read_bytes(),
               'media/file0.png': (work / 'media/file0.png').read_bytes(),
               'FROZEN_DOCUMENT.json': (work / 'FROZEN_DOCUMENT.json').read_bytes(),
               'SOURCE_EXPORT_RECEIPT.json': (work / 'SOURCE_EXPORT_RECEIPT.json').read_bytes(),
               'REPRODUCE.ps1': (ROOT / 'scripts/b80-format-repair-v1/reproduce.ps1').read_bytes()}
    payload['REBUILD_EPUB.py'] = (ROOT / 'scripts/b80-format-repair-v1/rebuild_epub.py').read_bytes()
    epub_path = work / f'03-b80-{language}.epub'
    with zipfile.ZipFile(epub_path) as epub:
        archive_inventory(epub)
        epub_manifest = {'file': epub_path.name, 'sha256': sha(epub_path.read_bytes()),
                         'comment_hex': epub.comment.hex(), 'members': []}
        for info in epub.infolist():
            raw = epub.read(info.filename)
            payload['epub/' + info.filename] = raw
            record = {'name': info.filename, 'date_time': list(info.date_time),
                      'sha256': sha(raw), 'extra_hex': info.extra.hex(), 'comment_hex': info.comment.hex()}
            for key in ('compress_type', 'create_system', 'create_version', 'extract_version',
                        'external_attr', 'internal_attr', 'flag_bits', 'volume'):
                record[key] = getattr(info, key)
            epub_manifest['members'].append(record)
    payload['EPUB_MANIFEST.json'] = encoded(epub_manifest)
    with zipfile.ZipFile(INPUT / f'{language}-source.zip') as native:
        archive_inventory(native)
        for name in ('LICENSE-TEXT.md', 'LICENSE-CODE.md', 'THIRD_PARTY.md', 'backend/catalog.json'):
            payload[name] = native.read(name)
    native_tag = 'v2026.08.22.1' if language == 'id' else 'v2026.08.31.en1'
    native_url = f'https://github.com/KokunoYumeto/mathematical-computing-reproducible-experiments-{language}/releases/tag/{native_tag}'
    if language == 'id':
        readme = f'''B80 - paket sumber ekspor format, 2026-10-03

Ini adalah sumber lengkap PDF turunan yang menyertai paket ini, bukan
rekonstruksi tata letak PDF lama. LaTeX kumulatif memuat semua teks, 272
rumus dan 195 blok kode dari EPUB sumber. Gambar asli disertakan. Tidak ada
eksperimen Python/Sage yang dijalankan ulang. Sumber asli tetap Quarto.

Rilis asli dan sumber Quarto yang tidak diubah: {native_url}
Catatan lisensi dan katalog sumber asli dipertahankan untuk atribusi;
jalur komponen dalam katalog tersebut merujuk pada paket asli, bukan pada
paket ekspor ini. Lihat LICENSE-TEXT.md, LICENSE-CODE.md dan THIRD_PARTY.md.

Perbaikan/ekspor format: OpenAI Codex - GPT-6 Astra, upaya Ultra.
Ini bukan peninjauan matematika atau penerjemahan baru. Edisi asli tetap ada.

Untuk membangun PDF: pasang dependensi dalam BUILD_REQUIREMENTS.json,
ekstrak semua berkas, lalu jalankan pwsh -NoProfile -File REPRODUCE.ps1.
Skrip memeriksa hash sumber, mengambil satu mutex TeX global, menonaktifkan
shell escape dan pemasangan paket otomatis, lalu menjalankan paling banyak
tiga lintasan XeLaTeX. Slot sibuk tidak memulai kompilasi. PDF hasil diperiksa
terhadap hash yang diharapkan; byte dapat berbeda pada perangkat lain.
Semua berkas LaTeX lokal yang diperlukan sudah disertakan. Paket TeX umum
dan fon adalah dependensi sistem; lingkungan Python/Sage tidak diperlukan.
EPUB yang diperbaiki adalah berkas rilis terpisah; bukan hasil kompilasi TeX.
XHTML, CSS dan aset lengkapnya tersedia dalam epub/. Jalankan python REBUILD_EPUB.py
untuk mereproduksi EPUB dan memeriksa hash; hanya pustaka standar Python diperlukan.
'''
    else:
        readme = f'''B80 - format-export source package, 2026-10-03

This is the complete source of the accompanying derived PDF, not a
reconstruction of the old PDF layout. Cumulative LaTeX includes all text,
272 formulas and 195 code blocks from the released EPUB, with the original
figure. No Python/Sage experiments were rerun. Quarto remains the native master.

Unchanged native edition and Quarto sources: {native_url}
Original licensing and component catalogue are retained for attribution;
component paths in that catalogue refer to the native package, not this export.
See LICENSE-TEXT.md, LICENSE-CODE.md and THIRD_PARTY.md.

Format repair/export: OpenAI Codex - GPT-6 Astra, Ultra effort.
This is not a new translation or mathematical review. Native editions remain.

To rebuild: install dependencies listed in BUILD_REQUIREMENTS.json, extract
all files, and run pwsh -NoProfile -File REPRODUCE.ps1. The script verifies
source hashes, acquires one global TeX mutex, disables shell escape and automatic
package installation, and performs at most three XeLaTeX passes. An occupied
slot does not launch TeX. It compares the PDF against the recorded hash;
bytes may differ with a different toolchain. All project-specific LaTeX inputs
are included. Standard TeX packages and fonts are system dependencies;
the Python/Sage runtime is unnecessary. The repaired EPUB is a separate release
file, not a TeX compilation product.
Complete editable XHTML, CSS and assets are in epub/. Run python REBUILD_EPUB.py
to reconstruct and hash-check the EPUB using only Python's standard library.
'''
    payload['README.txt'] = readme.encode('utf-8')
    tex = payload[f'01-b80-{language}.tex'].decode('utf-8')
    requirements = {'engine': 'XeLaTeX (MiKTeX tested)', 'shell': 'PowerShell 7 on Windows for REPRODUCE.ps1',
                    'fonts': ['DejaVu Serif', 'DejaVu Sans Mono', 'Latin Modern Math'],
                    'document_class': 'scrreprt', 'SOURCE_DATE_EPOCH': '1790985600',
                    'packages': sorted(set(','.join(re.findall(r'\\usepackage(?:\[[^]]*\])?\{([^}]+)\}', tex)).split(',')))}
    payload['BUILD_REQUIREMENTS.json'] = encoded(requirements)
    for name, raw in payload.items():
        if name.endswith(('.txt','.md','.json','.tex','.ps1','.py','.xhtml','.opf','.ncx','.css')):
            assert private_credit.casefold() not in raw.decode('utf-8-sig').casefold(), f'Legacy private credit in {name}'
    assert not re.findall(r'\\(?:input|include)\{', tex), 'Unbundled source input'
    manifest = {'schema': 'b80-derived-source/1', 'language': language,
                'native_release': native_url, 'native_epub_sha256': source['epub_repair']['source_sha256'],
                'expected_pdf_sha256': build['pdf']['sha256'],
                'files': [{'path': name, 'bytes': len(raw), 'sha256': sha(raw)} for name, raw in sorted(payload.items())]}
    payload['SOURCE_MANIFEST.json'] = encoded(manifest)
    target = work / f'02-b80-{language}-source.zip'
    with zipfile.ZipFile(target, 'w') as archive:
        for name, raw in sorted(payload.items()):
            info = zipfile.ZipInfo(name, (2026,10,3,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, raw)
    replay = OUTPUT / 'isolated-replay' / language
    assert replay.resolve().is_relative_to(OUTPUT.resolve())
    replay.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target) as archive:
        assert archive_inventory(archive) == set(payload)
        assert archive.testzip() is None
        for name, raw in payload.items():
            assert archive.read(name) == raw
            dest = replay / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
    receipt = {'language': language, 'source_zip': {'file': target.name, 'bytes': target.stat().st_size,
               'sha256': sha(target.read_bytes()), 'members': len(payload)},
               'native_sources_unchanged': True, 'native_master_replaced': False,
               'source_archive_verified': True, 'independent_replay': 'pending', 'published': False}
    (work / 'PACKAGE_RECEIPT.json').write_bytes(encoded(receipt))
    print(json.dumps(receipt))


if __name__ == '__main__':
    with zipfile.ZipFile(INPUT / 'id.epub') as original:
        private = xml(original.read('EPUB/content.opf')).xpath('./o:metadata/dc:creator/text()', namespaces=NS)[0]
    for language in ('id','en'):
        package(language, private)
