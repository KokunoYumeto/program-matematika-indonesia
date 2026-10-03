"""Bind final bytes to source preservation, isolated replays and recorded visual checks."""
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/b80-format-repair-v1'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    raw = path.read_bytes()
    return {'file': path.name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def finalize():
    subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('test_build_b80.py'))], check=True)
    visual = read(OUT / 'VISUAL_REVIEW.json')
    result = {'schema': 'b80-paired-format-validation/1', 'status': 'validated_local_not_publication',
              'new_translation': False, 'new_mathematical_review': False,
              'native_master_replaced': False, 'model_for_format_work': 'OpenAI Codex - GPT-6 Astra, Ultra effort',
              'regression_tests': 11, 'editions': {}}
    for lang in ('id', 'en'):
        work = OUT / lang
        source, build, package = [read(work / f) for f in
                                  ('SOURCE_EXPORT_RECEIPT.json', 'PDF_BUILD_RECEIPT.json', 'PACKAGE_RECEIPT.json')]
        geometry = read(work / 'qa/GEOMETRY.json')
        replay_root = OUT / 'isolated-replay' / lang
        replay, epub_replay = [read(replay_root / f) for f in ('REPLAY_RECEIPT.json', 'EPUB_REPLAY_RECEIPT.json')]
        names = [f'00-b80-{lang}.pdf', f'01-b80-{lang}.tex', f'02-b80-{lang}-source.zip', f'03-b80-{lang}.epub']
        files = [identity(work / n) for n in names]
        pdf, tex, archive, epub = files
        assert source['original_epub_semantics_unchanged'] and all(source['semantic_roundtrip'].values())
        assert tex['sha256'] == source['tex_sha256'] == build['source_sha256']
        assert pdf['sha256'] == build['pdf']['sha256'] == replay['pdf_sha256'] == geometry['pdf_sha256']
        assert replay['status'] == 'byte_identical' and replay['byte_identical']
        assert epub['sha256'] == source['epub_repair']['corrected_sha256'] == epub_replay['sha256']
        assert epub_replay['byte_identical']
        assert archive['sha256'] == package['source_zip']['sha256']
        assert build['overfull_hboxes'] == build['overfull_vboxes'] == 0
        assert not any(geometry[k] for k in ('text_outside_page_safety_margin', 'bad_internal_links',
                                             'replacement_character_pages', 'blank_pages'))
        assert visual[lang]['pdf_sha256'] == pdf['sha256']
        assert visual[lang]['all_page_contact_review'] == geometry['pages']
        assert visual[lang]['found_layout_defects'] == []
        epubcheck = read(work / 'EPUBCHECK.json')['checker']
        assert all(epubcheck[k] == 0 for k in ('nFatal', 'nError', 'nWarning'))
        with zipfile.ZipFile(work / archive['file']) as z:
            assert z.testzip() is None
            manifest = json.loads(z.read('SOURCE_MANIFEST.json'))
            assert manifest['expected_pdf_sha256'] == pdf['sha256']
            expected = {f['path'] for f in manifest['files']} | {'SOURCE_MANIFEST.json'}
            assert set(z.namelist()) == expected and len(expected) == len(z.namelist()) == 39
            for row in manifest['files']:
                data = z.read(row['path'])
                assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
                assert (replay_root / row['path']).read_bytes() == data
            assert z.read(tex['file']) == (work / tex['file']).read_bytes()
        for n in (pdf['file'], epub['file']):
            assert (replay_root / n).read_bytes() == (work / n).read_bytes()
        result['editions'][lang] = {'files_in_reading_order': files, 'pdf_pages': geometry['pages'],
            'bookmarks': geometry['bookmarks'], 'formulas': source['formulas'], 'code_blocks': source['code_blocks'],
            'native_epub_sha256': source['epub_repair']['source_sha256'],
            'semantic_roundtrip': source['semantic_roundtrip'], 'source_zip_members': 39,
            'pdf_and_epub_replay': 'byte_identical', 'epubcheck': {'version': '5.4.0', 'errors': 0, 'warnings': 0},
            'visual_review': visual[lang], 'geometry_checks': 'pass',
            'native_release': manifest['native_release']}
    for file in ('FINAL_FORMAT_VALIDATION.json',):
        (OUT / file).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'editions': 2, 'files': 8, 'tests': 11}))


if __name__ == '__main__':
    finalize()
