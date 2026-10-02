"""Preserve the exact public 32-section source without rewriting native files."""
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile
import requests

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/b40-projplane-public-20261002/preservation'
URL = 'https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/b40-original-en-2026.10.02-32-sections/COMPLETE_SOURCE.zip'
EXPECTED = {'bytes': 85326033, 'sha256': '856459bb306bdb9b0278c94795689b5072350f3d13313b21fc8b1b9ba7de2118'}
DIRECT = {'bytes': 2348855, 'sha256': '27f776cb77b22c39790054081765c102123436d01dbdfdbc0222d080b363afd5'}
MANIFEST = {'bytes': 87300, 'sha256': '38f788e5600ddbda3f299628689f0fe8fba96a7961b4489af6beb5dc71a04ab0'}
spec = importlib.util.spec_from_file_location('b40_archive_safety', ROOT / 'scripts/intake-b40-public-preservation-v1.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def fact(path):
    with path.open('rb') as stream:
        return guard.identity(stream)


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    path = BASE / 'COMPLETE_SOURCE.zip'
    receipt_path = BASE / 'INTAKE_RECEIPT.json'
    if not path.exists():
        partial = BASE / 'COMPLETE_SOURCE.zip.partial'
        assert not partial.exists(), 'Inspect previous partial transfer before retrying'
        session = requests.Session()
        session.trust_env = False
        session.auth = None
        session.headers.clear()
        session.headers['User-Agent'] = 'PMI-exact-source-preservation/1'
        size, digest = 0, hashlib.sha256()
        with session.get(URL, stream=True, timeout=(20, 120)) as response, partial.open('xb') as out:
            response.raise_for_status()
            assert 'Authorization' not in response.request.headers
            for block in response.iter_content(1024 * 1024):
                size += len(block)
                assert size <= EXPECTED['bytes'], 'Unexpected download size'
                digest.update(block)
                out.write(block)
        assert {'bytes': size, 'sha256': digest.hexdigest()} == EXPECTED
        partial.rename(path)
    assert fact(path) == EXPECTED
    with zipfile.ZipFile(path) as archive:
        inventory = json.loads(archive.read('SOURCE_PACKAGE_INVENTORY.json'))
        assert inventory['schema'] == 'exact-source-package-inventory/1' and inventory['self_excluded'] is True
        rows = inventory['files']
        names = {row['path'] for row in rows}
        assert len(rows) == len(names)
        assert set(archive.namelist()) == names | {'SOURCE_PACKAGE_INVENTORY.json'}
        for row in rows:
            guard.safe(row['path'])
            with archive.open(row['path']) as stream:
                assert guard.identity(stream) == {k: row[k] for k in ('bytes', 'sha256')}, row['path']
        reader_root = ROOT / 'docs/en/readers/hefferon-linear-algebra'
        assert fact(reader_root / 'READER_MANIFEST.json') == MANIFEST
        manifest = json.loads((reader_root / 'READER_MANIFEST.json').read_bytes())
        assert len(manifest['sections']) == 32 and manifest['sections'][-1]['section'] == 'projplane'
        for row in manifest['public_files']:
            guard.safe(row['path'])
            expected = {k: row[k] for k in ('bytes', 'sha256')}
            with archive.open('public/' + row['path']) as stream:
                assert guard.identity(stream) == expected
            assert fact(reader_root / row['path']) == expected
        assert fact(reader_root / 'sources/00-linear-algebra-cumulative.tex') == DIRECT
        checks = guard.scan(archive)
    result = {'schema': 'b40-projplane-public-preservation-intake/1', 'state': 'pass',
              'public_url': URL, 'anonymous': True,
              'archive': {'path': path.relative_to(ROOT).as_posix(), **EXPECTED},
              'direct_cumulative_source': DIRECT, 'reader_manifest': MANIFEST,
              'manifest_distributed_separately': True,
              'current_public_files_verified': len(manifest['public_files']),
              'members': len(names) + 1, 'hashed_inventory_members': len(rows), 'archive_checks': checks,
              'source_bytes_changed': False, 'native_tex_rebuilt': False,
              'scope': 'Exact already-public 32-section English reading/source edition through Projective Geometry; not the whole textbook or a new mathematical review.',
              'integration_provenance': 'OpenAI Codex gpt-6-astra, Ultra'}
    payload = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if receipt_path.exists():
        assert receipt_path.read_bytes() == payload, 'Different existing preservation receipt'
    else:
        receipt_path.write_bytes(payload)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
