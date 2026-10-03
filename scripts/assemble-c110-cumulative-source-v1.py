"""Assemble the pinned C110 book without changing any included source bytes."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import zipfile

ARCHIVE_SHA = '0eebe482eec535942524d4e5cb1fb164b9ac7de07f2eb9421e0d7bf29fa7ee4c'
INVENTORY_SHA = '1058ccc17f0f8d2ab22867f13e0de83901b22218988d55a24839adf7ec34450d'
MASTER = 'TeaTimeNumericalAnalysis-id-ID.tex'
SOURCE = 'source/latex-id-ID/'
DIRECTIVES = re.compile(rb'\\(include)\{([A-Za-z0-9_-]+)\}|\\(input) +([A-Za-z0-9_-]+)')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_name(name):
    p = PurePosixPath(name)
    require(name and not p.is_absolute() and '\\' not in name and ':' not in name
            and '..' not in p.parts and str(p) == name, 'Unsafe archive path')
    return name


def load_archive(archive, inventory):
    raw_inventory = Path(inventory).read_bytes()
    require(sha(raw_inventory) == INVENTORY_SHA, 'Inventory hash mismatch')
    meta = json.loads(raw_inventory)
    require(sha(Path(archive).read_bytes()) == ARCHIVE_SHA, 'Archive hash mismatch')
    prefix = meta['archive_root'] + '/'
    files = {}
    with zipfile.ZipFile(archive) as z:
        names = [i.filename for i in z.infolist() if not i.is_dir()]
        require(len(set(names)) == len(names), 'Duplicate ZIP entry')
        for name in names:
            safe_name(name)
            require(name.startswith(prefix), 'Unexpected archive root')
            files[name[len(prefix):]] = z.read(name)
    indexed = {row['path']: row for row in meta['files']}
    require(len(indexed) == len(meta['files']) == meta['payload_file_count'], 'Invalid native inventory')
    require(set(files) == set(indexed), 'Native archive inventory differs')
    for name, entry in indexed.items():
        require(len(files[name]) == entry['bytes'] and sha(files[name]) == entry['sha256'], 'Native member mismatch: ' + name)
    build = json.loads(files['build/manifests/id-ID-build.json'])
    closure = build['lyx_export']['input_inventory']
    require(len(closure) == build['lyx_export']['input_files'] == 289, 'Unexpected source closure')
    for entry in closure:
        content = files[SOURCE + entry['path']]
        require(len(content) == entry['bytes'] and sha(content) == entry['sha256'], 'Build input mismatch: ' + entry['path'])
    return files, meta, build


def assemble(files):
    master = files[SOURCE + MASTER]
    pieces = [b'% Sumber kumulatif C110; isi edisi 3.0-id.2-r1 tidak diubah.\n'
              b'% Gambar, bibliografi dan gaya: gunakan source/latex-id-ID/ dalam ZIP edisi.\n'
              b'% Petunjuk dan bukti perakitan: README.id.md dan manifest.json.\n']
    mappings = []
    cursor = 0
    seen = set()
    for match in DIRECTIVES.finditer(master):
        # The pinned master uses only literal top-level input/include commands.
        require(b'%' not in master[master.rfind(b'\n', 0, match.start()) + 1:match.start()], 'Commented directive')
        kind = (match[1] or match[3]).decode('ascii')
        name = (match[2] or match[4]).decode('ascii') + '.tex'
        require(name not in seen and name != MASTER, 'Duplicate or cyclic input')
        seen.add(name)
        content = files[SOURCE + name]
        require(not re.search(rb'\\(?:input|include|includeonly|endinput)\b', content), 'Nested or dynamic input unsupported')
        pieces.append(master[cursor:match.start()])
        # LaTeX include clears the page before and after its body. The sources
        # have no includeonly, part-aux dependence or nested inputs.
        pieces.append((b'\\clearpage%' if kind == 'include' else b'%') + b'\n')
        pieces.append(('% BEGIN ' + SOURCE + name + '\n').encode('ascii'))
        offset = sum(map(len, pieces))
        pieces.append(content)
        pieces.append(b'\n% END ' + (SOURCE + name).encode('ascii') + b'\n')
        if kind == 'include':
            pieces.append(b'\\clearpage{}')
        mappings.append({'path': SOURCE + name, 'directive': kind,
                         'master_start': match.start(), 'master_end': match.end(),
                         'output_start': offset, 'output_end': offset + len(content),
                         'bytes': len(content), 'sha256': sha(content)})
        cursor = match.end()
    pieces.append(master[cursor:])
    result = b''.join(pieces)
    expected = {k[len(SOURCE):] for k in files if k.startswith(SOURCE) and k.endswith('.tex')} - {MASTER}
    require(seen == expected, 'Not every native TeX body is included')
    require(len(mappings) == 30, 'Unexpected include count')
    for row in mappings:
        require(result[row['output_start']:row['output_end']] == files[row['path']], 'Embedded bytes changed')
    require(not re.search(rb'\\(?:input|include|includeonly)\b', result), 'Unexpanded body reference')
    return result, mappings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', required=True)
    parser.add_argument('--inventory', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--prepare-build', help='New private directory for exact dependencies and assembled master')
    args = parser.parse_args()
    files, meta, build = load_archive(args.archive, args.inventory)
    cumulative, mappings = assemble(files)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / MASTER).write_bytes(cumulative)
    manifest = {
        'schema': 'c110-cumulative-source/1', 'course_id': 'C110', 'language': 'id',
        'edition': meta['version'], 'native_payload_files_verified': meta['payload_file_count'],
        'source_closure_files_verified': len(build['lyx_export']['input_inventory']),
        'native_source_archive': {'url': 'https://github.com/KokunoYumeto/tea-time-numerical-analysis-id/releases/download/v3.0-id.2-r1/Tea-Time-Numerical-Analysis-id-ID-v3.0-id.2-r1-source-backend.zip', 'sha256': ARCHIVE_SHA},
        'native_inventory': {'sha256': INVENTORY_SHA},
        'released_pdf': build['pdf'],
        'direct_source': {'path': MASTER, 'bytes': len(cumulative), 'sha256': sha(cumulative)},
        'native_master': {'path': SOURCE + MASTER, 'bytes': len(files[SOURCE + MASTER]), 'sha256': sha(files[SOURCE + MASTER])},
        'embedded_sources': mappings,
        'assembly': {'included_body_bytes_preserved': True, 'native_document_order_preserved': True,
                     'include_boundaries': 'clearpage before and after each native include',
                     'source_encoding': 'latin9 as declared by native master; raw bytes retained',
                     'render_equivalence': 'requires separate checked build receipt'},
        'boundaries': {'new_translation': False, 'new_mathematical_review': False,
                       'complete_standalone_dependency_free_tex': False,
                       'figures_bibliography_and_styles': 'original source ZIP, source/latex-id-ID/'}}
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    if args.prepare_build:
        target = Path(args.prepare_build).resolve()
        require(not target.exists(), 'Build directory must be new; no source overwrite')
        target.mkdir(parents=True)
        for entry in build['lyx_export']['input_inventory']:
            name = safe_name(entry['path'])
            # Do not copy the original bodies: compilation must consume the
            # assembled text, not accidentally find a residual native chapter.
            if name.endswith('.tex'):
                continue
            dest = target.joinpath(*PurePosixPath(name).parts)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(files[SOURCE + name])
        (target / MASTER).write_bytes(cumulative)
    print(json.dumps({'status': 'assembled', 'native_payload_files_verified': len(meta['files']),
                      'embedded_tex_bodies': len(mappings), 'direct_source': manifest['direct_source']}))


if __name__ == '__main__':
    main()
