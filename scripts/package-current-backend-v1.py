"""Preserve the current shared backend, with bounded, streaming ZIP I/O.

This packages existing integration snapshots, not the producer book corpora.
The historical v1 package builder and ZIP are intentionally left untouched.
"""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CAPSULES = 'backend/course-capsule-v1/generated/course-capsules.json'
POLICY = 'backend/course-capsule-v1/authority/current-package-scope-v1.json'
MANIFEST = 'CURRENT_BACKEND_PACKAGE_MANIFEST.json'
STAMP = (1980, 1, 1, 0, 0, 0)
CHUNK = 1024 * 1024


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def identity(path):
    digest = hashlib.sha256()
    size = 0
    with path.open('rb') as source:
        while block := source.read(CHUNK):
            size += len(block)
            digest.update(block)
    return {'bytes': size, 'sha256': digest.hexdigest()}


def safe_name(name):
    path = PurePosixPath(name)
    if not name or '\\' in name or ':' in name or path.is_absolute() or '..' in path.parts:
        raise ValueError('Unsafe package path: ' + name)
    if str(path) != name or any(part in {'.git', 'node_modules', '__pycache__'} for part in path.parts):
        raise ValueError('Non-canonical or excluded package path: ' + name)
    return name


def local_path(root, name):
    safe_name(name)
    target = (root / name).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Path escapes package root: ' + name)
    if not target.is_file():
        raise FileNotFoundError(name)
    return target


def walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def local_facts(value):
    for item in walk(value):
        if not isinstance(item, dict):
            continue
        path = item.get('path', item.get('locator'))
        if isinstance(path, str) and path.startswith(('backend/', 'docs/', 'schemas/', 'scripts/')):
            if isinstance(item.get('sha256'), str) and isinstance(item.get('bytes'), int):
                yield path, {'bytes': item['bytes'], 'sha256': item['sha256']}


def native_script_dependency(root, referrer, dependency, declarations):
    """Resolve only an explicitly declared, hash-bound command in a native ZIP."""
    safe_name(referrer)
    safe_name(dependency)
    matches = [r for r in declarations if r['referrer'] == referrer
               and dependency in r['archive_script_paths']]
    if len(matches) != 1:
        raise FileNotFoundError(dependency)
    declaration = matches[0]
    evidence = declaration['evidence']
    path = local_path(root, evidence['path'])
    if identity(path) != {k: evidence[k] for k in ['bytes', 'sha256']}:
        raise ValueError('External native script evidence identity differs')
    audit = json.loads(path.read_bytes())
    assert audit['state'] == 'pass' and audit['all_source_checksums_verified'] is True
    archive = audit['source_archive']
    assert archive['anonymous'] is True and archive['url'].startswith('https://')
    assert archive['bytes'] > 0 and re.fullmatch('[0-9a-f]{64}', archive['sha256'])
    commands = audit['fresh_html_backend_replay']['commands']
    assert any(c['exit_code'] == 0 and dependency in c['command'] for c in commands), 'Native command not evidenced'
    return {'referrer': referrer, 'archive_script_path': dependency,
            'source_archive': archive, 'evidence': evidence,
            'scope': 'Optional native audit input, not a shared-capsule build dependency; download the exact native source ZIP separately.'}


def collect(root):
    scope = json.loads((root / POLICY).read_bytes())
    assert scope['schema'] == 'current-backend-package-scope/1'
    reasons = defaultdict(set)

    def add(name, reason):
        local_path(root, name)
        reasons[name].add(reason)

    # ls-files is explicitly path-limited: no workspace status/diff/untracked scan.
    tracked = subprocess.check_output(
        ['git', 'ls-files', '-z', '--', *scope['tracked_roots']], cwd=root
    ).decode().split('\0')
    for name in filter(None, tracked):
        add(name, 'bounded-current-integration-root')
    for name in scope['exact_files']:
        add(name, 'explicit-runtime-or-replay-input')
        # Newly authored, explicitly allowed members keep the same inventory
        # reasons before and after their first Git commit.
        if any(name == prefix or name.startswith(prefix + '/') for prefix in scope['tracked_roots']):
            add(name, 'bounded-current-integration-root')
    rows = json.loads((root / CAPSULES).read_bytes())
    assert len(rows) == len({r['course_id'] for r in rows}) == 40
    per_role = []
    for row in rows:
        facts = []
        for name, expected in local_facts(row):
            actual = identity(local_path(root, name))
            if actual != expected:
                raise ValueError(f"Current capsule identity mismatch: {row['course_id']} {name}")
            add(name, 'capsule:' + row['course_id'])
            facts.append(name)
        tools = row['layers']['learner'].get('tools', [])
        if not tools:
            raise ValueError('No functioning tool is declared for ' + row['course_id'])
        per_role.append({'course_id': row['course_id'], 'local_facts': sorted(set(facts)),
                         'learner_pages': sorted({t['page']['path'] for t in tools})})

    # Shared builders read these exact public evidence receipts by their declared names.
    refs = json.loads((root / 'backend/course-capsule-v1/authority/native-package-references-v1.json').read_bytes())
    add('backend/course-capsule-v1/validation/' + refs['evidence']['name'], 'native-package-evidence')
    for item in walk(refs):
        if isinstance(item, dict) and 'evidence_file' in item:
            add('backend/course-capsule-v1/validation/' + item['evidence_file'], 'native-package-operation')

    # Preserve source generators cited by adapter manifests. Native book identities
    # remain citations: arbitrary paths inside producer locks are not copied.
    for name in list(reasons):
        if not name.startswith('backend/course-capsule-v1/adapters/') or not name.endswith('.json'):
            continue
        if not any(term in Path(name).name.lower() for term in ['manifest', 'validation', 'source-lock']):
            continue
        if (root / name).stat().st_size > 8 * CHUNK:
            continue
        data = json.loads((root / name).read_bytes())
        for value in walk(data):
            if isinstance(value, str) and re.fullmatch(r'scripts/[A-Za-z0-9_.\-/]+', value):
                if (root / value).is_file():
                    add(value, 'manifest-source:' + name)

    # Follow local code imports and explicitly named helper scripts. This is not
    # claimed to discover arbitrary dynamic file reads: isolated replay is required.
    checked = set()
    native_dependencies = []
    while pending := [p for p in reasons if p not in checked and p.endswith(('.mjs', '.js', '.py'))]:
        for name in pending:
            checked.add(name)
            text = (root / name).read_text(encoding='utf-8-sig')
            candidates = set(re.findall(r'''["'](scripts/[\w./-]+\.(?:py|mjs|js))["']''', text))
            for match in re.findall(r'''(?:from\s*|import\s*\(\s*|import\s*)["'](\.[^"']+)["']''', text):
                target = (root / name).parent / match
                if target.is_file():
                    candidates.add(target.resolve().relative_to(root.resolve()).as_posix())
            if name.endswith('.py'):
                for node in ast.walk(ast.parse(text)):
                    mods = []
                    if isinstance(node, ast.Import):
                        mods = [alias.name for alias in node.names]
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        mods = [node.module]
                    for mod in mods:
                        target = (root / name).parent / (mod.replace('.', '/') + '.py')
                        if target.is_file():
                            candidates.add(target.relative_to(root).as_posix())
            for dep in sorted(candidates):
                if (root / dep).is_file():
                    add(dep, 'source-dependency:' + name)
                else:
                    external = native_script_dependency(root, name, dep,
                        scope.get('native_archive_script_references', []))
                    add(external['evidence']['path'], 'native-archive-command-evidence:' + name)
                    native_dependencies.append(external)

    files = []
    for name in sorted(reasons):
        files.append({'path': name, **identity(root / name), 'reasons': sorted(reasons[name])})
    manifest = {'schema': 'current-backend-package/1', 'scope': scope['preservation_scope'],
            'roles': per_role, 'files': files,
            'file_count': len(files), 'uncompressed_bytes': sum(f['bytes'] for f in files),
            'whole_program_complete': False,
            'producer_corpora_included': False,
            'full_native_source_rebuild_claimed': False,
            'external_native_script_dependencies': sorted(native_dependencies,
                key=lambda r: (r['referrer'], r['archive_script_path'])),
            'verification_required': ['exact-member-readback', 'isolated-capsule-replay', 'runtime-tests']}
    spec = importlib.util.spec_from_file_location('runtime_audit', root / 'scripts/audit-current-backend-runtime-v1.py')
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    report = runtime.audit(root, manifest)
    if report['missing_static_assets']:
        raise ValueError('Runtime assets missing from package: ' + ', '.join(r['path'] for r in report['missing_static_assets']))
    if report['privacy_findings']:
        raise ValueError('Package privacy check failed; inspect audit before publication')
    manifest['runtime_boundary'] = report
    return manifest


def write_archive(root, output, manifest):
    if output.exists():
        raise FileExistsError('Refusing to overwrite an existing archive: ' + output.name)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for row in manifest['files']:
            local_path(root, row['path'])
            info = zipfile.ZipInfo(row['path'], STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            digest, size = hashlib.sha256(), 0
            with (root / row['path']).open('rb') as source, archive.open(info, 'w', force_zip64=True) as dest:
                while block := source.read(CHUNK):
                    dest.write(block)
                    digest.update(block)
                    size += len(block)
            if {'bytes': size, 'sha256': digest.hexdigest()} != {k: row[k] for k in ['bytes', 'sha256']}:
                raise ValueError('Source changed while packaging: ' + row['path'])
        info = zipfile.ZipInfo(MANIFEST, STAMP)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        info.create_system = 3
        archive.writestr(info, canonical(manifest))


def verify_archive(path):
    with zipfile.ZipFile(path) as archive:
        manifest = json.loads(archive.read(MANIFEST))
        expected = [r['path'] for r in manifest['files']] + [MANIFEST]
        if len(expected) != len(set(expected)) or archive.namelist() != expected:
            raise ValueError('Duplicate, missing, extra or reordered archive members')
        for row in manifest['files']:
            safe_name(row['path'])
            digest, size = hashlib.sha256(), 0
            with archive.open(row['path']) as stream:
                while block := stream.read(CHUNK):
                    size += len(block)
                    digest.update(block)
            if size != row['bytes'] or digest.hexdigest() != row['sha256']:
                raise ValueError('Archive identity mismatch: ' + row['path'])
    return manifest


def replay(path, node):
    manifest = verify_archive(path)
    checks = []
    required = manifest['uncompressed_bytes'] + path.stat().st_size + 512 * CHUNK
    if shutil.disk_usage(tempfile.gettempdir()).free < required:
        raise OSError('Insufficient free space for isolated extraction and exact ZIP replay')
    with tempfile.TemporaryDirectory(prefix='current-backend-replay-') as temp:
        root = Path(temp).resolve()
        with zipfile.ZipFile(path) as archive:
            # Names verified before extraction; this is a private, fresh temp root.
            archive.extractall(root)
        commands = [
            ['build-course-capsules-v1.mjs', '--output-root=replay/a'],
            ['build-course-capsules-v1.mjs', '--output-root=replay/b'],
            ['validate-course-capsules-v1.mjs', '--output-root=replay/a', '--peer-output-root=replay/b'],
            ['test-course-capsule-ui-v1.mjs'],
        ]
        for parts in commands:
            result = subprocess.run([node, str(root / 'scripts' / parts[0]), *parts[1:]],
                                    cwd=root, capture_output=True, text=True, timeout=600,
                                    encoding='utf-8', errors='replace')
            if result.returncode:
                raise RuntimeError(parts[0] + '\n' + (result.stderr + result.stdout)[-6000:])
            checks.append({'script': parts[0], 'arguments': parts[1:], 'exit_code': 0})
        for name in ['course-capsules.json', 'course-capsules.jsonl', 'manifest.json']:
            expected = identity(root / 'backend/course-capsule-v1/generated' / name)
            assert identity(root / 'replay/a/generated' / name) == expected, 'Replay differs: ' + name
            assert identity(root / 'replay/b/generated' / name) == expected, 'Peer differs: ' + name
        repacked = root / 'repacked-current-backend.zip'
        write_archive(root, repacked, manifest)
        assert identity(repacked) == identity(path), 'Extracted source ZIP replay differs'
    return {'state': 'pass', 'roles': len(manifest['roles']), 'isolated_replay': checks,
            'shipped_outputs_reproduced': True, 'source_zip_repacked_byte_identically': True,
            'producer_sources_used': False,
            'limits': 'Capsule and shared UI replay; not a full book rebuild, browser accessibility audit or fresh canon review.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--build', type=Path)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--replay', type=Path)
    parser.add_argument('--node', default='node')
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    if args.plan:
        manifest = collect(ROOT)
        args.plan.parent.mkdir(parents=True, exist_ok=True)
        args.plan.write_bytes(canonical(manifest))
        print(json.dumps({'state': 'planned', 'files': manifest['file_count'], 'bytes': manifest['uncompressed_bytes'], 'roles': 40}))
    elif args.build:
        manifest = collect(ROOT)
        write_archive(ROOT, args.build, manifest)
        verify_archive(args.build)
        result = {'state': 'archive-verified', 'archive': identity(args.build), 'files': manifest['file_count'], 'roles': 40}
        if args.receipt:
            args.receipt.write_bytes(canonical(result))
        print(json.dumps(result))
    elif args.replay:
        result = replay(args.replay, args.node)
        if args.receipt:
            args.receipt.write_bytes(canonical(result))
        print(json.dumps(result))
    elif args.verify:
        manifest = verify_archive(args.verify)
        print(json.dumps({'state': 'verified', 'files': manifest['file_count'], 'roles': len(manifest['roles'])}))
    else:
        parser.error('Choose --plan, --build, --verify, or --replay')


if __name__ == '__main__':
    main()
