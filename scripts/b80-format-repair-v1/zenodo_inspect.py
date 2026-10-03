"""Read only exact existing Zenodo lineages; never emit authentication or names."""
import json
import re
from pathlib import Path
import requests
from finalize import OUT

TOKEN_FILE = Path.home() / 'Documents/Obsidian notes/New zenodo token.md'


def client_for(record):
    candidates = re.findall(r'(?<![A-Za-z0-9._~-])([A-Za-z0-9._~-]{40,})(?![A-Za-z0-9._~-])', TOKEN_FILE.read_text(encoding='utf-8'))
    for candidate in sorted(set(candidates), key=len, reverse=True):
        session = requests.Session()
        session.headers.update({'Authorization': 'Bearer ' + candidate, 'User-Agent': 'B80-format-preservation'})
        r = session.get(f'https://zenodo.org/api/deposit/depositions/{record}', timeout=(15,45))
        if r.status_code == 200 and r.json().get('id') == record:
            return session, r.json()
    raise RuntimeError('No usable credential for exact existing lineage')


if __name__ == '__main__':
    for lang, record in [('id',22053905), ('en',22210474)]:
        session, data = client_for(record)
        public = requests.get(f'https://zenodo.org/api/records/{record}/versions/latest', timeout=(15,45)).json()
        result = {'record': record, 'latest_public': public['id'], 'concept': data['conceptrecid'],
                  'state': data['state'], 'submitted': data['submitted'], 'links': data['links'],
                  'version': data['metadata'].get('version'),
                  'metadata_fields': list(data['metadata']),
                  'file_count': len(data['files'])}
        # Links may contain no credentials: reject before saving a sanitized receipt.
        assert not re.search(r'access_token|Bearer ', json.dumps(result), re.I)
        (OUT/lang/'ZENODO_PREFLIGHT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(result))
