"""Seal the complete editable source/offline-reader closure, without TeX."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import argparse

BASE = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--work', type=Path, default=BASE / 'b40-expanded-public-20261002')
parser.add_argument('--refresh-candidate', action='store_true')
arguments = parser.parse_args()
WORK = arguments.work.resolve()
REFRESH = arguments.refresh_candidate


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fact(path, b):
    return {'path': path, 'bytes': len(b), 'sha256': sha(b)}


def jb(o):
    return (json.dumps(o, ensure_ascii=False, indent=2) + '\n').encode()


def exact(path, b):
    if path.exists():
        if path.read_bytes() != b:
            assert REFRESH and path.resolve().is_relative_to(WORK.resolve()), 'sealed output differs: ' + str(path)
            path.write_bytes(b)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as f:
            f.write(b)


def main():
    if REFRESH:
        assert not (WORK / 'PUBLICATION_RECEIPT.json').exists(), 'published release is immutable'
        old = json.loads((WORK / 'SOURCE_SEAL.json').read_bytes())
        archive = WORK / old['source_zip']['path']
        assert sha(archive.read_bytes()) == old['source_zip']['sha256'], 'prior candidate archive changed'
    frozen = WORK / 'frozen'
    public = WORK / 'public'
    receipt = json.loads((WORK / 'BUILD_RECEIPT.json').read_bytes())
    count = receipt['counts']['readers']
    selection_path = frozen / 'EXPORT_SELECTION.json'
    selection = json.loads(selection_path.read_bytes()) if selection_path.exists() else None
    source_url = selection['source_archive_url'] if selection else 'https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/b40-original-en-2026.10.02-28-sections/COMPLETE_SOURCE.zip'
    inputs = json.loads((frozen / 'FROZEN_INPUTS.json').read_bytes())
    members = {}
    for row in inputs['files']:
        b = (frozen / row['path']).read_bytes()
        assert len(b) == row['bytes'] and sha(b) == row['sha256']
        members['frozen/' + row['path']] = b
    members['frozen/FROZEN_INPUTS.json'] = (frozen / 'FROZEN_INPUTS.json').read_bytes()
    for row in receipt['outputs']:
        b = (public / row['path']).read_bytes()
        assert len(b) == row['bytes'] and sha(b) == row['sha256']
        members['public/' + row['path']] = b
    members['BUILD_RECEIPT.json'] = (WORK / 'BUILD_RECEIPT.json').read_bytes()
    members['check_public_units.mjs'] = (WORK / 'check_public_units.mjs').read_bytes()
    members['RUNTIME_PROVENANCE.json'] = (WORK / 'RUNTIME_PROVENANCE.json').read_bytes()
    members['PUBLIC_EXTRACTION_QA.json'] = (WORK / 'PUBLIC_EXTRACTION_QA.json').read_bytes()
    members['seal_b40_expanded_public_20261002.py'] = Path(__file__).read_bytes()
    readme = '''LINEAR ALGEBRA — ORIGINAL ENGLISH — EXACT EDITABLE SOURCE AND OFFLINE READERS

Original mathematics: Jim Hefferon, Linear Algebra, revision
df2262e089a02651c127f1dd12649c4622ee1383. Chosen text/source licence: CC BY-SA 2.5.
Retain public/LICENSE.txt, public/ACKNOWLEDGEMENTS.txt and native component terms.
This selected reading edition is not the whole book or an Everyday-English rewrite.

READ OFFLINE
Open public/index.html. The 28 linked readers contain native MathML and embedded
SVG; no JavaScript, fonts or network runtime is required. Programme-home and
author-site links are external. The ZIP-download link refers to the separately
distributed archive itself; after extraction you already have its contents.

EDITABLE LATEX
public/sources/00-linear-algebra-cumulative.tex contains every active source body
for these 28 sections, including the native supplied-answer environments, plus
separate editorial source notes. Individual source files beside it retain the
complete original files, including inactive/commented material excluded from HTML.
The gr1 source's explicit end-of-input cutoff remains part of its source record.

frozen/native-authority.zip is the byte-exact complete original repository archive.
It contains the original source tree, styles, macros, bibliography, figures and
Makefile/latexmk configuration. It is NOT a patch or evidence-only substitute.
For native-source editing, extract that archive and place the cumulative file in
the original src directory. The author's build system and font/TeX prerequisites
remain those of the pinned revision. No new native TeX/PDF compilation is claimed.
The fully verified release format here is HTML, not a newly typeset PDF.

REPRODUCE THE EXACT HTML
Prerequisites: Python 3, Node.js and Pandoc; no downloaded packages are needed for
this replay. From the unpacked archive directory run:
  python -B rebuild.py
This regenerates 28 native HTML witnesses from the frozen editable Pandoc JSON,
MathML and SVG inputs and compares them byte-for-byte. It then reconstructs the
public navigation/projection, checks all preserved main-body bytes, source-bound
unit slices and exercise/answer partitions, and compares the release outputs.
It does not overwrite the native source, run source generators, call the network,
compile TeX or pretend to have rerun the earlier raw-TeX-to-AST conversion.
The native LaTeX and the source-bound intermediate representation are both retained.

MODEL AND SCOPE
Current source-preserving rebuild, packaging and deterministic validation:
OpenAI Codex — GPT-6 Astra, Ultra effort. Earlier intermediate-conversion runtime
identity is unverified in its retained metadata and is not reassigned. Author and
component credits are preserved. No human review or exhaustive proof certification
is claimed. Mathematical-source findings are kept separate from unchanged text.
The complete public programme and phone proof-admission workflow remain separate.
'''.encode()
    readme = readme.replace(b'28 linked readers', (str(count)+' linked readers').encode()).replace(b'these 28 sections', ('these '+str(count)+' sections').encode()).replace(b'regenerates 28 native', ('regenerates '+str(count)+' native').encode())
    members['REBUILD.txt'] = readme
    members['rebuild.py'] = b'''from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parent
subprocess.run([sys.executable, '-B', str(root/'frozen/curriculum_logbook/build_b40_expanded_public_20261002.py'), '--work', str(root), '--check'], check=True)
'''
    # Check the entire original ZIP, including its styles/figures and rights.
    native_bytes = members['frozen/native-authority.zip']
    with zipfile.ZipFile(io.BytesIO(native_bytes)) as native:
        assert native.testzip() is None
        names = native.namelist()
        assert len(names) == len(set(names))
        for name in names:
            assert not name.startswith(('/', '\\')) and '..' not in Path(name).parts
        native_count = len(names)
    # The cumulative source must contain all 28 full active source bodies once.
    cumulative = members['public/sources/00-linear-algebra-cumulative.tex']
    for section in receipt['sections']:
        source = members['frozen/reader_mirrors/hefferon-original-en-20260909/authority/' + section['active_source']['path']]
        prefix = source[:section['active_source']['bytes']]
        assert sha(prefix) == section['active_source']['sha256']
        assert cumulative.count(prefix) == 1
    inventory = [fact(k, b) for k, b in sorted(members.items())]
    members['SOURCE_PACKAGE_INVENTORY.json'] = jb({'schema': 'exact-source-package-inventory/1', 'files': inventory, 'self_excluded': True})
    archive = public / 'COMPLETE_SOURCE.zip'
    sink = io.BytesIO()
    with zipfile.ZipFile(sink, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, b in sorted(members.items()):
            zi = zipfile.ZipInfo(name, date_time=(2026, 10, 2, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_STORED if name.endswith('native-authority.zip') else zipfile.ZIP_DEFLATED
            zi.external_attr = 0o100644 << 16
            z.writestr(zi, b)
    archive_bytes = sink.getvalue()
    exact(archive, archive_bytes)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and set(z.namelist()) == set(members)
        for name, b in members.items():
            assert z.read(name) == b
    # Isolated replay uses a bounded directory belonging only to this package.
    replay = WORK / 'isolated-source-replay'
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            target = (replay / name).resolve()
            assert target.is_relative_to(replay.resolve())
            exact(target, z.read(name))
    process = subprocess.run([sys.executable, '-B', str(replay/'rebuild.py')], capture_output=True, timeout=120, check=True)
    assert not process.stderr
    replay_result = json.loads(process.stdout)
    adapter = subprocess.run(['node', str(replay/'check_public_units.mjs'), '--check'], capture_output=True, timeout=180, check=True)
    assert not adapter.stderr
    adapter_result = json.loads(adapter.stdout)
    assert adapter_result['state'] == 'PASS' and adapter_result['views'] == receipt['counts']['native_units'] + 2*receipt['counts']['exercises']
    assert replay_result['state'] == 'byte_replay_pass'
    public_manifest = {
        'schema': 'b40-expanded-reading-edition/1',
        'title': 'Linear algebra — original English — original English by Jim Hefferon',
        'source_revision': receipt['source_revision'],
        'scope': str(count)+' consecutive body/topic sections, not the complete book',
        'language': 'en', 'sections': receipt['sections'], 'counts': receipt['counts'],
        'download_order': ['sources/00-linear-algebra-cumulative.tex', 'COMPLETE_SOURCE.zip'],
        'no_pdf_exception': 'HTML reading edition; do not create a PDF merely to fill a preview slot',
        'source_archive': {**fact('COMPLETE_SOURCE.zip', archive_bytes), 'url':source_url},
        'public_files': receipt['outputs'],
        'rights': {'author': 'Jim Hefferon', 'work': 'Linear Algebra', 'license': 'CC BY-SA 2.5 option; native component notices retained', 'licence_file': 'LICENSE.txt', 'component_credits': 'ACKNOWLEDGEMENTS.txt'},
        'provenance': {'current_model': 'gpt-6-astra', 'effort': 'ultra', 'work': 'source-preserving HTML rebuild, navigation, projection and source packaging', 'legacy_intermediate_runtime': 'unverified, not reattributed', 'human_review': False},
        'validation': {'offline_replay': replay_result, 'main_bodies_unchanged': True, 'native_archive_entries': native_count, 'source_package_members': len(members), 'complete_member_readback': True},
        'publication': 'candidate; deployment receipt is separate',
    }
    exact(public / 'READER_MANIFEST.json', jb(public_manifest))
    seal = {'schema': 'b40-expanded-source-seal/1', 'state': 'PASS',
            'source_zip': fact('public/COMPLETE_SOURCE.zip', archive_bytes),
            'source_zip_members': len(members), 'source_zip_uncompressed_bytes': sum(map(len, members.values())),
            'native_archive_entries': native_count, 'isolated_replay': replay_result, 'portable_extraction_replay': adapter_result,
            'publication_still_required': True,
            'manifest': fact('public/READER_MANIFEST.json', jb(public_manifest))}
    exact(WORK / 'SOURCE_SEAL.json', jb(seal))
    print(json.dumps(seal))


if __name__ == '__main__':
    main()
