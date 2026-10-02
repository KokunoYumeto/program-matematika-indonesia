"""Preserve the exact public 28-section source package, with bounded streamed I/O."""
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile
import requests

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/b40-expanded-public-20261002/preservation'
URL = 'https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/b40-original-en-2026.10.02-28-sections/COMPLETE_SOURCE.zip'
EXPECTED = {'bytes': 68117715, 'sha256': '2d015e393396ccba342c4e62c9c1c3d30ece1acaf9bce2c29634a6cf2958e903'}
DIRECT = {'bytes': 2266186, 'sha256': '9eb12dbbf5e98f0d1fae0b23eed074a4e14e74cfd68d288ae6cfde3e9b2b4ed5'}
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
        assert len(rows) == len(names) == 811
        assert set(archive.namelist()) == names | {'SOURCE_PACKAGE_INVENTORY.json'}
        for row in rows:
            guard.safe(row['path'])
            with archive.open(row['path']) as stream:
                assert guard.identity(stream) == {k: row[k] for k in ('bytes', 'sha256')}, row['path']
        source = 'public/sources/00-linear-algebra-cumulative.tex'
        with archive.open(source) as stream:
            assert guard.identity(stream) == DIRECT
        assert fact(ROOT / 'docs/en/readers/hefferon-linear-algebra/sources/00-linear-algebra-cumulative.tex') == DIRECT
        checks = guard.scan(archive)
    result = {'schema': 'b40-expanded-public-preservation-intake/1', 'state': 'pass',
              'public_url': URL, 'anonymous': True, 'archive': {'path': path.relative_to(ROOT).as_posix(), **EXPECTED},
              'direct_cumulative_source': DIRECT, 'members': 812, 'hashed_inventory_members': 811,
              'archive_checks': checks, 'source_bytes_changed': False, 'native_tex_rebuilt': False,
              'scope': 'Exact already-public 28-section English reading/source edition; not the whole textbook or a new mathematical review.',
              'integration_provenance': 'OpenAI Codex gpt-6-astra, Ultra'}
    payload = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if receipt_path.exists():
        assert receipt_path.read_bytes() == payload, 'Different existing preservation receipt'
    else:
        receipt_path.write_bytes(payload)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
