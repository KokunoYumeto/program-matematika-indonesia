"""Thin, locale-bound intake of the existing D100 Indonesian native ledgers.

No book bodies are copied or translated. Full native-stream identities are pinned;
metadata witnesses and segment identities retain their native IDs and states.
This validates an inventory, not the linguistic quality of its entries.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('backend/course-capsule-v1/adapters/d100-indonesian-evidence-v1')
LANES = [
    ('classical', 'units-01-30-corr1', 38025813,
     '90d4e621bde73f34e5487156c61f51aa6788d7ffb37644febd82f7d392b4b1e2',
     'd66c0ec6d22d9cff75442613a7572e0238a7558c395306e90009908fa904a1a1', 23869),
    ('bgk', 'bgk-units-01-30-corr1', 25933440,
     'e30f72fbcadd7ca9f9ad4b295bdb3f0a3ce2ec1071532553dad11256557cb9b0',
     'a5fe8881d8039b1545613e3711fd1d71196b9ce19aa7f2caa4809a96d33df374', 21690),
    ('original', 'original-bridge-corr1', 4815165,
     'fc074bb8bf4d80c1d63f74522a531f0aae752b1c112ee869a8dca7218cd3532e',
     'ce2c2a2429c7c5cb7bf5281900cbb47d670265817076bca1d036fe70a3cabcce', 1064),
]
CLASSES = {'term', 'correction', 'rights'}
SCOPE = 'native_ledger_structure_and_identity_only'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value, pretty=False):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       indent=2 if pretty else None,
                       separators=None if pretty else (',', ':')) + '\n').encode('utf-8')


def fact(path, data):
    return {'path': path, 'bytes': len(data), 'sha256': digest(data)}


def validate_record(row):
    require(row['schema'] == 'ag-bridge-backend-record' and row['schema_version'] == '1.0.0',
            'Native schema changed')
    require(isinstance(row['stable_id'], str) and row['stable_id'], 'Missing native ID')
    if row['entity_class'] in {'segment', 'term', 'correction'}:
        require(row['language'] == 'id-ID', 'Wrong-language translation evidence')
    if row['entity_class'] == 'term':
        payload = row['payload'].get('ledger_row', row['payload'])
        require(payload.get('preferred_target'), 'Missing native target term')
        require(payload.get('target_language', 'id-ID') == 'id-ID', 'Wrong-language term payload')


def build(native):
    native = native.resolve()
    sources, witnesses, segments, inventories = [], [], [], []
    for lane, directory, size, sha, manifest_sha, expected_count in LANES:
        relative = Path('backend') / directory
        manifest_path = relative / 'MANIFEST.json'
        manifest_bytes = (native / manifest_path).read_bytes()
        require(digest(manifest_bytes) == manifest_sha, 'Native manifest drift: ' + lane)
        manifest = json.loads(manifest_bytes)
        entries = [r for r in manifest['files'] if r['path'].endswith('records.jsonl')]
        require(len(entries) == 1, 'Ambiguous native record stream')
        entry = entries[0]
        require(entry['bytes'] == size and entry['sha256'] == sha, 'Native stream manifest mismatch')
        stream_path = relative / 'records.jsonl'
        require((native / stream_path).resolve().is_relative_to(native), 'Native path escaped root')
        source = {'lane': lane, 'records': {'path': stream_path.as_posix(), 'bytes': size, 'sha256': sha},
                  'manifest': fact(manifest_path.as_posix(), manifest_bytes)}
        sources.append(source)
        hasher, byte_count, ids, counts, states = hashlib.sha256(), 0, set(), Counter(), Counter()
        with (native / stream_path).open('rb') as stream:
            for number, line in enumerate(stream, 1):
                hasher.update(line)
                byte_count += len(line)
                row = json.loads(line)
                validate_record(row)
                require(row['stable_id'] not in ids, 'Duplicate native ID: ' + row['stable_id'])
                ids.add(row['stable_id'])
                counts[row['entity_class'], row['language']] += 1
                if row['entity_class'] == 'term':
                    states[row['status']] += 1
                location = {'lane': lane, 'source_line': number, 'source_line_sha256': digest(line)}
                if row['entity_class'] in CLASSES:
                    # Preserve exact raw record serialization for independent line-hash checks.
                    witnesses.append({**location, 'native_record': line.decode('utf-8')})
                elif row['entity_class'] == 'segment':
                    segments.append({**location, **{key: row[key] for key in (
                        'stable_id', 'language', 'parent_id', 'resource_id', 'edition_id',
                        'rights_id', 'source_locator', 'content_sha256', 'translation_state', 'status')}})
        require(byte_count == size and hasher.hexdigest() == sha, 'Native stream byte drift: ' + lane)
        require(len(ids) == expected_count, 'Native record count drift')
        inventories.append({'lane': lane, 'records': len(ids), 'term_states': dict(sorted(states.items())),
                            'entity_locales': [{'entity': c, 'language': lang, 'count': n}
                                               for (c, lang), n in sorted(counts.items())]})
    total = Counter()
    for inventory in inventories:
        for row in inventory['entity_locales']:
            total[row['entity']] += row['count']
    require({key: total[key] for key in ['segment', 'term', 'correction', 'rights']} ==
            {'segment': 15829, 'term': 905, 'correction': 371, 'rights': 149}, 'D100 scope drift')
    lock = {'schema': 'd100-indonesian-source-lock/1', 'course_id': 'D100', 'target_locale': 'id-ID',
            'repository': 'https://github.com/KokunoYumeto/algebraic-geometry-bridge-id',
            'sources': sources}
    files = {'source-lock.json': encoded(lock, True),
             'metadata-witnesses.jsonl': b''.join(encoded(r) for r in witnesses),
             'segment-index.jsonl': b''.join(encoded(r) for r in segments)}
    report = {'schema': 'd100-indonesian-ledger-evidence/1', 'state': 'pass', 'course_id': 'D100',
              'target_locale': 'id-ID', 'verification_scope': SCOPE, 'semantic_canon_review': 'not_established',
              'native_edited': False, 'book_bodies_copied': False, 'inventories': inventories,
              'counts': {key: total[key] for key in ['segment', 'term', 'correction', 'rights']},
              'record_rows': sum(r['records'] for r in inventories),
              'files': [fact(name, data) for name, data in sorted(files.items())],
              'limitations': [
                  'Pemeriksaan ini memverifikasi identitas dan struktur daftar asli Bahasa Indonesia, bukan mutu terjemahan.',
                  'Istilah dan status sementara dipertahankan; pembacaan ulang sumber kanon per pilihan belum dibuktikan oleh pemeriksaan ini.',
                  'Catatan hak penggunaan tetap khusus per komponen; bahasa catatan lisensi tidak disamakan dengan bahasa terjemahan.',
                  'Indeks segmen memuat identitas dan lokasi, bukan salinan isi buku atau bukti kesetaraan makna.',
                  'Teks asli dalam saksi metadata dipertahankan apa adanya, termasuk alasan yang ditulis dalam bahasa Inggris.',
              ]}
    files['evidence.json'] = encoded(report, True)
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-root', type=Path, default=ROOT.parent / 'algebraic-geometry-bridge-id')
    parser.add_argument('--output-root', type=Path, default=ROOT / BASE)
    args = parser.parse_args()
    files = build(args.native_root)
    args.output_root.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (args.output_root / name).write_bytes(data)
    print(json.dumps({'state': 'pass', 'files': len(files), 'target_locale': 'id-ID',
                      'scope': SCOPE, 'book_bodies_copied': False}))


if __name__ == '__main__':
    main()
