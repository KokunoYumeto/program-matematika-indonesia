"""Anonymous, bounded readback of a scoped integration commit and its Pages files."""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
REPO = 'KokunoYumeto/program-matematika-indonesia'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def fact(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--commit', required=True)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--source-only', action='store_true')
    args = p.parse_args()
    commit = git('rev-parse', '--verify', args.commit + '^{commit}').decode().strip()
    paths = git('diff-tree', '--no-commit-id', '--name-only', '-r', commit).decode().splitlines()
    assert 1 <= len(paths) <= 100, 'Unexpected publication boundary'
    receipt = {'schema': 'backend-increment-public-readback/1', 'commit': commit,
               'repository': f'https://github.com/{REPO}', 'anonymous': True,
               'credentials_used': False, 'source_only': args.source_only,
               'observed_at': datetime.now(timezone.utc).isoformat(), 'files': [], 'failures': [], 'state': 'in_progress'}

    def save():
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')

    with urlopen(f'https://api.github.com/repos/{REPO}', timeout=40) as response:
        inventory = json.load(response)
    assert inventory['private'] is False
    receipt['public_repository_inventory'] = {'full_name': inventory['full_name'], 'private': inventory['private']}
    save()
    for path in paths:
        assert '..' not in Path(path).parts and not Path(path).is_absolute()
        expected = fact(git('show', f'{commit}:{path}'))
        urls = [f'https://raw.githubusercontent.com/{REPO}/{commit}/{quote(path)}']
        if path.startswith('docs/') and not args.source_only:
            urls.append('https://kokunoyumeto.github.io/program-matematika-indonesia/' + quote(path[5:]))
        for url in urls:
            try:
                with urlopen(url, timeout=40) as response:
                    actual = fact(response.read(expected['bytes'] + 1))
                    assert response.status == 200
                assert actual == expected, 'Public byte/hash mismatch'
                receipt['files'].append({'path': path, 'url': url, **actual})
            except Exception as error:
                receipt['failures'].append({'path': path, 'url': url, 'error': str(error)})
            save()
        if len(receipt['files']) % 10 == 0:
            print(json.dumps({'checked': len(receipt['files']), 'failures': len(receipt['failures'])}), flush=True)
    receipt['state'] = 'pass' if not receipt['failures'] else 'failed'
    receipt['verified_bytes'] = sum(row['bytes'] for row in receipt['files'])
    save()
    print(json.dumps({'state': receipt['state'], 'objects': len(receipt['files']), 'bytes': receipt['verified_bytes'], 'failures': len(receipt['failures'])}), flush=True)
    return bool(receipt['failures'])


if __name__ == '__main__':
    raise SystemExit(main())
