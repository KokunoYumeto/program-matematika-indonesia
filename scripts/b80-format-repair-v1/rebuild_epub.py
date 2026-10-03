"""Rebuild the supplied EPUB from editable XHTML/CSS/assets using only Python's standard library."""
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'EPUB_MANIFEST.json').read_text(encoding='utf-8'))
target = root / manifest['file']
assert target.resolve().parent == root
with zipfile.ZipFile(target, 'w') as archive:
    archive.comment = bytes.fromhex(manifest['comment_hex'])
    for item in manifest['members']:
        path = (root / 'epub' / item['name']).resolve()
        assert path.is_relative_to((root / 'epub').resolve())
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item['sha256'], item['name']
        info = zipfile.ZipInfo(item['name'], tuple(item['date_time']))
        for attribute in ('compress_type', 'create_system', 'create_version', 'extract_version',
                          'external_attr', 'internal_attr', 'flag_bits', 'volume'):
            setattr(info, attribute, item[attribute])
        info.extra = bytes.fromhex(item['extra_hex'])
        info.comment = bytes.fromhex(item['comment_hex'])
        archive.writestr(info, raw)
actual = hashlib.sha256(target.read_bytes()).hexdigest()
receipt = {'schema': 'b80-epub-replay/1', 'file': target.name, 'sha256': actual,
           'byte_identical': actual == manifest['sha256']}
(root / 'EPUB_REPLAY_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt))
assert receipt['byte_identical'], 'Recreated EPUB differs from the recorded release'
