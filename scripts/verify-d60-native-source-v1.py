"""One bounded anonymous readback of the exact released D60 editable source."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d60-native-ledger-v1'
source = json.loads((BASE / 'source-lock.json').read_bytes())['source_archive']
receipt_path = BASE / 'public-source-readback.json'
assert source['url'].startswith('https://zenodo.org/records/22168033/files/')
if receipt_path.exists():
    prior = json.loads(receipt_path.read_bytes())
    assert prior['state'] == 'pass' and prior['source_archive'] == source and prior['anonymous'] is True
    print(json.dumps({'state': 'already_verified', 'bytes': prior['bytes'], 'sha256': prior['sha256']}), flush=True)
else:
    request = urllib.request.Request(source['url'], headers={'User-Agent': 'D60-native-source-byte-check/1', 'Accept': 'application/zip'})
    digest, total = hashlib.sha256(), 0
    with urllib.request.urlopen(request, timeout=60) as response:
        assert response.status == 200
        while block := response.read(1024 * 1024):
            total += len(block)
            assert total <= source['bytes'], 'Public source is larger than frozen authority'
            digest.update(block)
    assert total == source['bytes'] and digest.hexdigest() == source['sha256'], 'Public source differs from frozen archive'
    receipt = {'schema': 'd60-native-source-public-readback/1', 'state': 'pass', 'anonymous': True,
               'source_archive': source, 'bytes': total, 'sha256': digest.hexdigest(),
               'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'credentials_used': False,
               'producer_files_changed': False, 'semantic_canon_approval': False, 'native_book_rebuilt': False}
    with receipt_path.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'state': 'pass', 'anonymous': True, 'bytes': total, 'sha256': digest.hexdigest()}), flush=True)
