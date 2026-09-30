"""Replay two pinned native metadata builders, never a producer tree or TeX.

The unchanged native source ZIP is supplied separately from its existing public
lineage. The small dependency bundle closes its otherwise missing frozen inputs.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import zipfile

spec = importlib.util.spec_from_file_location('d70_audit', Path(__file__).with_name('audit-d70-native-source-closure-v1.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
MANIFEST = 'D70_METADATA_REPLAY_MANIFEST.json'


def checked_members(archive, cap):
    infos = archive.infolist()
    names = [row.filename for row in infos]
    audit.require(len(names) == len(set(names)) and len(names) <= 100, 'Duplicate or excessive ZIP members')
    audit.require(sum(row.file_size for row in infos) <= cap, 'ZIP expanded-size cap exceeded')
    for row in infos:
        # ZipInfo normalizes Windows separators while reading; check the wire
        # name as well so normalization cannot hide an aliased member.
        audit.safe_name(row.orig_filename)
        audit.require(row.orig_filename == row.filename, 'Unsafe aliased ZIP member')
        audit.safe_name(row.filename)
        audit.require(not row.is_dir() and (row.external_attr >> 16) & 0o170000 != 0o120000,
                      'Non-file ZIP member forbidden')
    audit.require(archive.testzip() is None, 'ZIP CRC failure')
    return names


def verified_bundle(path):
    with zipfile.ZipFile(path) as archive:
        names = checked_members(archive, 6 * 1024 * 1024)
        manifest = json.loads(archive.read(MANIFEST))
        audit.require(manifest['schema'] == 'd70-native-metadata-replay-bundle/1', 'Bundle schema differs')
        audit.require(manifest['source_archive'] == {'name': audit.ARCHIVE, **audit.EXPECTED_ARCHIVE}, 'Native identity differs')
        files = manifest['files']
        audit.require(len(files) == len({row['path'] for row in files}) and
                      {row['path'] for row in files} == set(names) - {MANIFEST}, 'Bundle manifest closure differs')
        for row in files:
            data = archive.read(row['path'])
            audit.require({'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()} ==
                          {key: row[key] for key in ['bytes', 'sha256']}, 'Bundle member identity differs')
        dependencies = [row for row in files if row['path'].startswith('dependencies/')]
        audit.require(len(dependencies) == 26 and sum(row['bytes'] for row in dependencies) == 4322608,
                      'Dependency boundary differs')
        for name in ['replay-d70-native-metadata-v1.py', 'audit-d70-native-source-closure-v1.py']:
            row = next(row for row in files if row['path'] == 'scripts/' + name)
            audit.require(audit.identity(Path(__file__).with_name(name)) ==
                          {key: row[key] for key in ['bytes', 'sha256']}, 'Running replay source differs from bundle')
        return manifest


def run(bundle, source_archive, work_dir):
    manifest = verified_bundle(bundle)
    audit.require(audit.identity(source_archive) == audit.EXPECTED_ARCHIVE, 'Native source archive identity differs')
    work_dir.mkdir(parents=True, exist_ok=True)
    isolated = Path(tempfile.mkdtemp(prefix='d70-portable-', dir=work_dir)).resolve()
    with zipfile.ZipFile(source_archive) as original:
        names = checked_members(original, 10 * 1024 * 1024)
        audit.require(len(names) == 68, 'Native source member count differs')
        native_manifest = json.loads(original.read('SOURCE_ARCHIVE_MANIFEST.json'))
        entries = native_manifest['entries']
        audit.require(len(entries) == len({row['path'] for row in entries}) == 67 and
                      {row['path'] for row in entries} == set(names) - {'SOURCE_ARCHIVE_MANIFEST.json'},
                      'Native manifest closure differs')
        canonical = ''.join(f"{row['sha256']}  {row['path']}\n" for row in entries)
        audit.require(hashlib.sha256(canonical.encode()).hexdigest() == native_manifest['canonical_entry_list_sha256'],
                      'Native manifest digest differs')
        for row in entries:
            data = original.read(row['path'])
            audit.require({'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()} ==
                          {key: row[key] for key in ['bytes', 'sha256']}, 'Native member identity differs')
        for name in names:
            target = isolated / 'repo' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as output:
                output.write(original.read(name))
    with zipfile.ZipFile(bundle) as dependencies:
        for row in manifest['files']:
            if not row['path'].startswith('dependencies/'):
                continue
            name = row['path'].removeprefix('dependencies/')
            audit.safe_name(name)
            target = isolated / name
            audit.require(target.is_relative_to(isolated) and not target.exists(), 'Dependency would overwrite source')
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as output:
                output.write(dependencies.read(row['path']))
    commands = audit.replay_validators(isolated)
    comparisons = []
    expected = [row for row in entries if row['path'].startswith(('components/duncan/backend/', 'components/cring/backend/'))
                and row['path'].endswith(('.json', '.csv'))]
    audit.require(len(expected) == 13, 'Metadata output scope differs')
    for row in expected:
        actual = audit.identity(isolated / 'repo' / row['path'])
        comparisons.append({'path': row['path'], **actual,
                            'matches_shipped_bytes': actual == {key: row[key] for key in actual}})
    passed = all(row['exit_code'] == 0 for row in commands) and all(row['matches_shipped_bytes'] for row in comparisons)
    return {'schema': 'd70-portable-native-metadata-replay/1', 'state': 'pass' if passed else 'fail',
            'source_archive': manifest['source_archive'], 'dependency_bundle': audit.identity(bundle),
            'dependency_files': 26, 'dependency_bytes': 4322608, 'source_members': 68,
            'commands': commands, 'artifact_comparisons': comparisons,
            'producer_tree_required': False, 'network_required_for_replay': False,
            'fresh_tex_build': False, 'fresh_semantic_canon_review': False,
            'whole_native_parity_proven': False, 'producer_files_modified': False,
            'attribution': 'OpenAI Codex — gpt-6.1-sol, Ultra effort: dependency integration and isolated verification; native translation attribution is unchanged.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--source-archive', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = run(args.bundle, args.source_archive, args.work_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'state': report['state'], 'metadata_artifacts': len(report['artifact_comparisons']),
                      'producer_tree_required': False, 'whole_native_parity_proven': False}))
    audit.require(report['state'] == 'pass', 'Native metadata replay failed; inspect receipt')


if __name__ == '__main__':
    main()
