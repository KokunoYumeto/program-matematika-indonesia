"""Check the frozen D70 native source boundary without touching its producer.

This is not a translation/canon audit, TeX build or full-native parity claim.
The optional isolated replay runs only the two shipped stdlib JSON validators.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d70-capability-v1'
LOCK_SHA = 'c9c17e670b9be3dd3da51d97f781b95ae8fca26a445ca85a72369482d7873f8d'
ARCHIVE = '05_o013-sumber-backend-1.0.0.zip'
EXPECTED_ARCHIVE = {'bytes': 1295518, 'sha256': '6273206ffb42277f3040d638e1a0f0870596b823a239fa9d3947d964aa094ef9'}

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def identity(path):
    digest, count = hashlib.sha256(), 0
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
            count += len(block)
    return {'bytes': count, 'sha256': digest.hexdigest()}

def safe_name(name):
    path = PurePosixPath(name)
    require(bool(name) and name not in {'.', '..'} and path.as_posix() == name
            and not path.is_absolute() and '..' not in path.parts
            and ':' not in name and '\\' not in name, 'Unsafe source member')

def replay_validators(isolated):
    attempts = []
    for component in ['duncan', 'cring']:
        script = isolated / f'repo/components/{component}/backend/validate_{component}_backend.py'
        result = subprocess.run([sys.executable, '-B', str(script), '--regenerate'],
                                cwd=isolated, capture_output=True, text=True, timeout=90)
        raw = result.stdout + result.stderr
        try:
            value = json.loads(raw)
            for key in ['error', 'reason']:
                if isinstance(value.get(key), str):
                    value[key] = value[key].replace(str(isolated).replace('\\', '\\\\'), '<isolated-root>').replace(str(isolated), '<isolated-root>')
            text = json.dumps(value, ensure_ascii=False)
        except ValueError:
            text = raw.replace(str(isolated).replace('\\', '\\\\'), '<isolated-root>').replace(str(isolated), '<isolated-root>')
        attempts.append({'component': component,
                         'command': f'python -B repo/components/{component}/backend/validate_{component}_backend.py --regenerate',
                         'exit_code': result.returncode, 'output': text[-6000:],
                         'scope': 'Native metadata regeneration; not TeX or semantic canon review.'})
    return attempts

def provision_native_dependencies(native, isolated):
    """Copy only the explicit frozen inputs needed by these two validators."""
    rows = []
    def copy(rel, expected=None):
        safe_name(rel)
        source, target = native / rel, isolated / rel
        actual = identity(source)
        if expected:
            require(actual == expected, 'External frozen dependency differs: ' + rel)
        require(not target.exists(), 'Dependency would overwrite a shipped member')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        require(identity(target) == actual, 'Dependency copy differs')
        rows.append({'path': rel, **actual, 'method': 'exact_local_frozen_input'})
    def extract_selected(rel, prefix, destination, selected):
        with zipfile.ZipFile(native / rel) as original:
            require(original.testzip() is None, 'Authority archive CRC failure')
            for name in selected:
                member = prefix + '/' + name
                safe_name(member)
                data = original.read(member)
                target = isolated / destination / member
                require(len(data) < 1024 * 1024 and not target.exists(), 'Authority member boundary differs')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                rows.append({'path': target.relative_to(isolated).as_posix(), 'bytes': len(data),
                             'sha256': hashlib.sha256(data).hexdigest(), 'method': 'from_pinned_authority_archive',
                             'source_archive': rel, 'source_member': member})
    duncan = 'authority/duncan-representation-theory-notes-c62d36f41189da4bd3da4671668f68720df54ff7'
    duncan_zip = duncan + '/representation-theory-notes-c62d36f41189da4bd3da4671668f68720df54ff7.zip'
    copy(duncan_zip, {'bytes': 92763, 'sha256': '60dd9679c9ebe0c28f31794a7b2cb8552f4b7d68038061024972257280a1852c'})
    copy(duncan + '/DUNCAN_SOURCE_FREEZE.json')
    extract_selected(duncan_zip, 'representation-theory-notes-c62d36f41189da4bd3da4671668f68720df54ff7',
                     duncan + '/source', [stem + '.tex' for stem in ['rep_intro', 'lin_alg', 'modules', 'characters', 'induction', 'symmetric', 'nonclosed']] + ['rep_theory.bib', 'LICENSE'])
    cring = 'authority/cring-project-official-20260828'
    copy(cring + '/CRing.zip', {'bytes': 442843, 'sha256': '151cdf5498622251db9999b082c4b756a5a7e22b07ddd79538c0057472a4234d'})
    copy(cring + '/CRing.pdf', {'bytes': 2973918, 'sha256': '9d228183f549ab4a64dcacfa49884c0f7ef4d5d5f8c535f9066070bf909b580c'})
    spans = json.loads((isolated / 'repo/components/cring/support/CRING_SELECTED_SPANS.json').read_bytes())
    selected = ['other/references.bib', 'other/intro.tex', 'other/contributors.tex', 'chapters/license.tex']
    selected += ['chapters/' + name for name in sorted({row['source_file'] for row in spans['segments']})]
    extract_selected(cring + '/CRing.zip', 'cring', cring + '/source', selected)
    copy('qa/cring-selected-evidence/cring-selected-aggregate-validation.json',
         {'bytes': 5249, 'sha256': '88d517bce56e50d090bce039c1786cd1dc75d0da5aa5644c87c8e585bcc344cb'})
    copy('qa/cring-selected-evidence/validate-cring-selected.ps1',
         {'bytes': 12650, 'sha256': '3c6a8a1a10197c58fd65694d0b2eb61916fec710862113864320f0dc3989964e'})
    for name in ['translate_cring_segments.py', 'retranslate_cring_context.py']:
        copy('repo/components/cring/support/' + name)
    require(sum(row['bytes'] for row in rows) < 6 * 1024 * 1024, 'Dependency overlay exceeds bounded scope')
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-root', type=Path, default=ROOT.parent / 'metode-aljabar-jilid-1-id')
    parser.add_argument('--replay', action='store_true')
    parser.add_argument('--with-native-dependencies', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT / 'work/d70-native-source-closure-v1/audit.json')
    args = parser.parse_args()
    require(not args.with_native_dependencies or args.replay, 'Dependency replay requires --replay')
    native = args.native_root.resolve(strict=True)
    lock_bytes = (BASE / 'input/source-lock.json').read_bytes()
    require(hashlib.sha256(lock_bytes).hexdigest() == LOCK_SHA, 'Frozen native lock changed')
    lock = json.loads(lock_bytes)
    rows = []
    require(len(lock['inputs']) == lock['input_count'] == 57, 'Native input scope changed')
    for row in lock['inputs']:
        safe_name(row['path'])
        actual = identity(native / row['path'])
        require(actual == {key: row[key] for key in actual}, 'Native input identity differs: ' + row['path'])
        rows.append({'path': row['path'], 'role': row['role'], **actual})
    evidence = json.loads((BASE / 'data/evidence.json').read_bytes())
    publication = native / 'publication/o013-aggregate-1.0.0'
    public_rows = []
    for row in evidence['public_files']:
        safe_name(row['name'])
        actual = identity(publication / row['name'])
        require(actual == {key: row[key] for key in actual}, 'Frozen public artifact differs: ' + row['name'])
        public_rows.append({'name': row['name'], **actual})
    require(len(public_rows) == evidence['file_count'] == 9, 'Frozen public artifact boundary differs')
    require(identity(publication / ARCHIVE) == EXPECTED_ARCHIVE, 'Native source archive differs')
    report = {'schema': 'd70-native-source-closure-audit/1', 'state': 'identity_pass',
              'source_lock': {'path': 'input/source-lock.json', 'bytes': len(lock_bytes), 'sha256': LOCK_SHA},
              'native_inputs': rows, 'frozen_public_artifacts': public_rows,
              'source_archive': {'name': ARCHIVE, **EXPECTED_ARCHIVE},
              'fresh_semantic_canon_review': False, 'fresh_tex_build': False,
              'whole_native_parity_proven': False, 'producer_files_modified': False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(publication / ARCHIVE) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        require(len(names) == len(set(names)) == 68, 'Source archive inventory changed')
        require(sum(item.file_size for item in infos) <= 10 * 1024 * 1024, 'Source expanded-size cap exceeded')
        for item in infos:
            safe_name(item.filename)
            require((item.external_attr >> 16) & 0o170000 != 0o120000, 'Source archive symlink forbidden')
        require(archive.testzip() is None, 'Source archive CRC failure')
        manifest = json.loads(archive.read('SOURCE_ARCHIVE_MANIFEST.json'))
        entries = {row['path']: row for row in manifest['entries']}
        require(len(entries) == len(manifest['entries']) == 67, 'Manifest uniqueness differs')
        require(set(entries) == set(names) - {'SOURCE_ARCHIVE_MANIFEST.json'}, 'Source manifest closure differs')
        for name, row in entries.items():
            data = archive.read(name)
            require(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], 'Source member differs: ' + name)
            witness = publication / name if name == 'LICENSES.md' else native / 'repo' / name
            require(data == witness.read_bytes(), 'Packaged source differs from native source: ' + name)
        # The inspected native packager uses sha256, two spaces, path and LF,
        # in its own manifest order (PowerShell's culture-aware path sort).
        canonical = ''.join(f"{row['sha256']}  {row['path']}\n" for row in manifest['entries'])
        require(hashlib.sha256(canonical.encode()).hexdigest() == manifest['canonical_entry_list_sha256'], 'Canonical manifest digest differs')
        require(sum(row['bytes'] for row in entries.values()) == manifest['content_uncompressed_bytes'] == 9392140, 'Content byte scope differs')
        report['source_archive'].update(members=68, content_members=67, content_bytes=9392140,
                                        manifest_sha256=hashlib.sha256(archive.read('SOURCE_ARCHIVE_MANIFEST.json')).hexdigest(),
                                        canonical_digest_verified=True,
                                        every_member_matches_native=True)
        report['source_archive']['scope'] = 'Components O013-K02 to O013-K04; Li Volume I is deliberately separately preserved.'
        if args.replay:
            # Preserve this bounded replay directory as current evidence; do not
            # run a foreign validator in the producer tree or invoke TeX here.
            isolated = Path(tempfile.mkdtemp(prefix='d70-isolated-', dir=args.output.parent))
            for name in names:
                target = isolated / 'repo' / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(name) as incoming, target.open('xb') as outgoing:
                    while block := incoming.read(1024 * 1024):
                        outgoing.write(block)
            attempts = replay_validators(isolated)
            report['isolated_backend_replay'] = attempts
            report['shipped_archive_backend_replay_complete'] = all(row['exit_code'] == 0 for row in attempts)
            report['isolated_directory'] = str(isolated.relative_to(ROOT)).replace('\\', '/')
            if args.with_native_dependencies:
                report['explicit_external_dependencies'] = provision_native_dependencies(native, isolated)
                extended = replay_validators(isolated)
                report['extended_isolated_backend_replay'] = extended
                comparisons = []
                for name, row in entries.items():
                    if name.startswith(('components/duncan/backend/', 'components/cring/backend/')) and name.endswith(('.csv', '.json')):
                        actual = identity(isolated / 'repo' / name)
                        comparisons.append({'path': name, 'matches_shipped_bytes': actual == {key: row[key] for key in actual}, **actual})
                report['extended_backend_artifact_comparisons'] = comparisons
                report['extended_metadata_replay_pass'] = all(row['exit_code'] == 0 for row in extended) and all(row['matches_shipped_bytes'] for row in comparisons)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'state': report['state'], 'native_inputs': len(rows), 'public_artifacts': len(public_rows),
                      'source_members': 68, 'isolated_backend_replay': report.get('isolated_backend_replay'),
                      'extended_metadata_replay_pass': report.get('extended_metadata_replay_pass'),
                      'whole_native_parity_proven': False}, ensure_ascii=False))

if __name__ == '__main__':
    main()
