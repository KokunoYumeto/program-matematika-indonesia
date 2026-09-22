"""Stage the frozen D50 reader and assemble its complete editable TeX.

No producer file is edited. Source/reader downloads are opt-in, bounded and
verified; normal rebuilds use the exact public release files supplied locally.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from urllib.request import urlopen
import zipfile

from central_surface_navigation_overlay_v1 import strip_central_surface_overlay

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d50-surface-v1'
OUT = ROOT / 'docs/backend/d50'
RELEASE = 'https://github.com/KokunoYumeto/brenner-differentialgeometrie-id/releases/download/v1.0.1/'
SOURCE = 'geometri-diferensial-manifold-mulus-edisi-lengkap-source-backend-r1-20260829.zip'
SOURCE_FACT = {'bytes': 69154138, 'sha256': '94bdc7c1f9ceec599daf59c0d303721be009a140d5a7bd5f794ac8887b935ae3'}
PDF = 'geometri-diferensial-manifold-mulus-edisi-lengkap-id.pdf'
PDF_FACT = {'bytes': 10524618, 'sha256': 'e0b416d91dfa8de4d5fbf7d84add34cfb3b57adde4645f60c4bc0a0609f5bd2f'}
TEX = 'geometri-diferensial-lengkap.id.tex'
STAGE = 'build/complete-stage/build/'
DRIVER = STAGE + 'generated/complete-reader-driver.tex'
INPUT = re.compile(rb'(?m)^\\input\{([^{}\r\n]+)\}[^\S\r\n]*(?:\r?\n|$)')


def fact(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def public_fact(url, expected):
    digest, size = hashlib.sha256(), 0
    with urlopen(url, timeout=45) as response:
        assert response.status == 200
        while data := response.read(1024 * 1024):
            size += len(data)
            assert size <= expected['bytes'], 'Oversized download'
            digest.update(data)
    actual = {'bytes': size, 'sha256': digest.hexdigest()}
    assert actual == expected, url
    return {'url': url, **actual, 'anonymous': True}


def archive(path, maximum):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    assert len(names) == len(set(names))
    assert sum(i.file_size for i in z.infolist()) <= maximum
    assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts
               and '\\' not in n and ':' not in n for n in names)
    assert z.testzip() is None
    return z


def assemble(z):
    used = []

    def expand(name, parents=()):
        assert name not in parents, 'Recursive TeX input'
        data = z.read(name)
        used.append({'path': name, **fact(data)})
        def replace(match):
            target = STAGE + match[1].decode('utf-8')
            assert target in z.namelist(), target
            body = expand(target, (*parents, name))
            # Standalone input lines only: preserve line-end semantics without
            # adding TeX tokens, definitions, annotations or rewritten prose.
            return body if body.endswith(b'\n') else body + b'\n'
        out = INPUT.sub(replace, data)
        uncommented = re.sub(rb'(?<!\\)%[^\r\n]*', b'', out)
        assert not re.search(rb'\\(?:input|include)\s*\{', uncommented), name
        return out

    data = expand(DRIVER)
    assert data.count(b'\\begin{document}') == data.count(b'\\end{document}') == 1
    assert len(used) == len({x['path'] for x in used})
    assert len(used) > 190 and len(data) > 1_000_000
    return data, used


def stage(release_dir, verify_public=False):
    witness = json.loads((BASE / 'input/reader-witness.json').read_text(encoding='utf-8'))
    archive_fact = {k: witness['archive'][k] for k in ['bytes', 'sha256']}
    reader_path, source_path = release_dir / witness['archive']['path'], release_dir / SOURCE
    assert fact(reader_path.read_bytes()) == archive_fact
    assert fact(source_path.read_bytes()) == SOURCE_FACT
    rz, sz = archive(reader_path, 15_000_000), archive(source_path, 110_000_000)
    tex, inputs = assemble(sz)
    public = []
    if verify_public:
        for name, expected in [(witness['archive']['path'], archive_fact), (SOURCE, SOURCE_FACT), (PDF, PDF_FACT)]:
            public.append(public_fact(RELEASE + name, expected))
    else:
        prior = json.loads((BASE / 'delivery/public-dependencies.json').read_text(encoding='utf-8'))
        assert [(x['url'], x['bytes'], x['sha256']) for x in prior['files']] == [
            (RELEASE + n, f['bytes'], f['sha256']) for n, f in
            [(witness['archive']['path'], archive_fact), (SOURCE, SOURCE_FACT), (PDF, PDF_FACT)]]
        public = prior['files']
    expected = {f['path']: f for f in witness['members']}
    assert set(rz.namelist()) == set(expected)
    bindings = json.loads(sz.read('PACKAGE_MANIFEST.json'))['reader_and_backend_bindings']
    assert {k: bindings['html_entry'][k] for k in ['bytes', 'sha256']} == {k: witness['reader'][k] for k in ['bytes', 'sha256']}
    assert {k: bindings['pdf'][k] for k in ['bytes', 'sha256']} == PDF_FACT
    assert sz.read('backend/records.jsonl') == (BASE / 'input/records.jsonl').read_bytes()
    assert sz.read('scripts/export_html_complete.py')
    # All validation precedes any output write.
    for name, row in expected.items():
        assert fact(rz.read(name)) == {k: row[k] for k in ['bytes', 'sha256']}
        target = OUT / 'reader' / name
        if target.exists():
            actual = target.read_bytes()
            if name.endswith('.html'):
                actual = strip_central_surface_overlay(actual, name)
            assert actual == rz.read(name), f'Unowned reader change: {name}'
    for name in sorted(expected):
        target = OUT / 'reader' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(rz.read(name))
    (OUT / TEX).write_bytes(tex)
    (OUT / 'LICENSE.md').write_bytes(sz.read('LICENSE.md'))
    source = {'url': RELEASE + SOURCE, **SOURCE_FACT}
    receipt = {'schema': 'd50-central-reader-delivery/1', 'state': 'pass', 'locale': 'id-ID',
        'reader_url': 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d50/reader/index.html',
        'reader': witness['reader'], 'reader_members': witness['members'],
        'pdf': {'url': RELEASE + PDF, **PDF_FACT}, 'complete_source_archive': source,
        'direct_tex': {'path': TEX, **fact(tex)}, 'assembly_inputs': inputs,
        'assembly': 'recursive expansion of standalone input lines; source text unchanged; dependencies remain in original source ZIP',
        'tex_build_replayed': False, 'source_package_crc': 'pass', 'source_package_members': len(sz.namelist()),
        'source_html_pdf_bindings_match': True, 'native_files_modified': False,
        'integration_model': 'OpenAI Codex — GPT-6 Astra, Ultra effort',
        'source_model': witness['source_model_identification']}
    dump(BASE / 'delivery/public-dependencies.json', {'schema': 'd50-public-delivery-dependencies/1', 'observed_date': '2026-09-22', 'files': public})
    dump(BASE / 'delivery/reader-delivery.json', receipt)
    dump(OUT / 'reader-delivery.json', receipt)
    print(json.dumps({'state': 'pass', 'reader_files': len(expected), 'tex': fact(tex), 'source_files': len(inputs), 'expanded_input_commands': len(inputs)-1, 'public_downloads': 3 if verify_public else 0}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--release-dir', type=Path, required=True)
    p.add_argument('--verify-public', action='store_true')
    args = p.parse_args()
    stage(args.release_dir.resolve(), args.verify_public)
