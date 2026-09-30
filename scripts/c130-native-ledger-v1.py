"""Project exact C130 native metadata without rewriting or republishing book prose.

The intake independently binds released archives and their native tables. Native
approval labels and evidence prose are preserved as claims, never upgraded to a
fresh terminology or mathematical review. Generated views omit all segment text.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/c130-native-ledger-v1'
ARCHIVES = {
 'backend': ('pemrograman-matematis-dan-riset-operasi-buku-1-modular-backend-v0.zip', 6535806),
 'source': ('pemrograman-matematis-dan-riset-operasi-buku-1-source-id-ID.zip', 20087323),
 'labs': ('pemrograman-matematis-dan-riset-operasi-buku-1-o018-open-solver-labs-id-ID.zip', 527596),
}
# Exact archive identities are read from the existing independently tested map;
# literals above provide filename/extent expectations, not an alternative authority.
EXPECTED_COUNTS = {'terms': 140, 'concepts': 128, 'corrections': 94,
                   'segments': 5525, 'units': 1993, 'rights': 21, 'relations': 9545}
MONOLITH = '7c2ec930a7472021b37101f860b2b1846503fd52f4b495f863508cd91d741804'
MANIFEST = 'f800590f07fafa47c7eb900dddc8cf99bbf5cb892218fa4ab1722677b7b2efa4'
SEGMENT_FIELDS = ['id', 'unit_id', 'parent_id', 'resource_id', 'rights_component_id',
                  'concept_ids', 'prerequisite_concept_ids', 'locale', 'status',
                  'source_target_relationship', 'translation_state', 'supersedes_id',
                  *[side + suffix for side in ['source', 'target'] for suffix in
                    ['_edition_id', '_locale', '_path', '_line_start', '_line_end',
                     '_content_sha256', '_local_id', '_block_index']]]
UNIT_FIELDS = ['id', 'parent_id', 'resource_id', 'edition_id', 'rights_component_id',
               'concept_ids', 'prerequisite_concept_ids', 'locale', 'status',
               'unit_type', 'title_source', 'title_target', 'order', 'supersedes_id']

def packed(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def fact(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else packed(value))

def require(ok, message):
    if not ok:
        raise ValueError(message)

def safe_members(archive):
    names = archive.namelist()
    require(len(names) == len(set(names)), 'Duplicate ZIP member')
    for name in names:
        path = PurePosixPath(name)
        require(not path.is_absolute() and '..' not in path.parts and '\\' not in name and ':' not in name,
                'Unsafe ZIP member')
    require(archive.testzip() is None, 'ZIP CRC failure')
    return names

def normalized(raw):
    return raw.decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')

def text_location(text, content, start, end):
    """Prefer declared complete lines; never use fuzzy matching or invent a span."""
    lines = text.splitlines()
    if isinstance(start, int) and isinstance(end, int) and 1 <= start <= end <= len(lines):
        body = '\n'.join(lines[start - 1:end])
        if body == content or body.strip() == content:
            return {'state': 'declared_lines_exact_text', 'line_range': [start, end]}
    if not content:
        return {'state': 'empty_text_not_locatable'}
    position = text.find(content)
    if position < 0:
        return {'state': 'text_not_found'}
    if text.find(content, position + 1) >= 0:
        return {'state': 'ambiguous_text_occurrences'}
    return {'state': 'unique_exact_text_relocated',
            'line_range': [text.count('\n', 0, position) + 1,
                           text.count('\n', 0, position + len(content)) + 1]}

def index_by_id(rows, name):
    require(all(isinstance(r.get('id'), str) and r['id'] for r in rows), 'Missing ' + name + ' ID')
    result = {r['id']: r for r in rows}
    require(len(result) == len(rows), 'Duplicate ' + name + ' ID')
    return result

def project(native, locate):
    indices = {name: index_by_id(native[name], name) for name in EXPECTED_COUNTS}
    for name, count in EXPECTED_COUNTS.items():
        require(len(indices[name]) == count, 'Native count differs: ' + name)
    concepts, units = indices['concepts'], indices['units']
    uses = defaultdict(list)
    segments, issues = [], []
    for row in native['segments']:
        require(row['unit_id'] in units, 'Unknown segment unit')
        require(row['rights_component_id'] in indices['rights'], 'Unknown segment rights')
        for cid in row.get('concept_ids', []):
            require(cid in concepts, 'Unknown segment concept')
            uses[cid].append(row['id'])
        item = {k: row[k] for k in SEGMENT_FIELDS if k in row}
        item['canonical_native_record_sha256'] = sha(packed(row))
        item['verification'] = {}
        for side in ['source', 'target']:
            content = row.get(side + '_text')
            digest = row.get(side + '_content_sha256')
            if content is None:
                item['verification'][side] = {'state': 'no_native_text'}
                continue
            identity_ok = bool(digest) and sha(content.encode()) == digest
            check = {'native_text_digest_matches': identity_ok}
            if not identity_ok:
                issues.append({'id': row['id'], 'kind': side + '_native_text_digest_mismatch'})
            if row.get(side + '_locale') == 'en':
                check.update(state='english_source_not_rechecked_in_target_archives')
            else:
                check.update(locate(row, side, content))
            item['verification'][side] = check
        segments.append(item)
    terms = []
    for row in native['terms']:
        require(row['concept_id'] in concepts, 'Unknown term concept')
        terms.append({'native': row, 'concept_segment_ids': sorted(uses[row['concept_id']]),
                      'audit': {'semantic_canon_review': False,
                                'mapping_scope': 'native_concept_relation_not_lexical_occurrence',
                                'evidence_scope': 'verbatim_native_claim_not_independent_attestation'}})
    for row in native['corrections']:
        require(all(uid in units for uid in row['affected_unit_ids']), 'Unknown correction unit')
    return {'schema': 'c130-native-ledger-view/1', 'course_id': 'C130',
            'native_snapshot_at': native['snapshot_at'], 'terms': terms,
            'corrections': native['corrections'], 'concepts': native['concepts'],
            'rights': native['rights'],
            'units': [{**{k: row[k] for k in UNIT_FIELDS if k in row},
                       'canonical_native_record_sha256': sha(packed(row))} for row in native['units']],
            'segments': segments,
            'audit': {'issues': issues, 'semantic_canon_review': False,
                      'whole_native_rebuild': False, 'book_prose_copied': False,
                      'native_qa_states_are_claims': True,
                      'projection_policy': {'segment_fields': SEGMENT_FIELDS, 'unit_fields': UNIT_FIELDS,
                         'omitted_fields_retained_in': 'hash-bound native backend archive',
                         'reverse_whole_monolith_from_projection_claimed': False},
                      'segment_text_fields_omitted': ['source_text', 'target_text']}}

def intake(cache, dest):
    prior = json.loads((ROOT / 'backend/course-capsule-v1/adapters/c130-teacher-v1/mapping.json').read_bytes())
    locked = prior['inputs']
    archives, identities = {}, {}
    try:
        for kind, (filename, size) in ARCHIVES.items():
            raw = (cache / filename).read_bytes()
            expected = locked[kind]
            require(len(raw) == size == expected['bytes'] and sha(raw) == expected['sha256'], 'Archive identity drift: ' + kind)
            archives[kind] = zipfile.ZipFile(io.BytesIO(raw))
            safe_members(archives[kind])
            identities[kind] = {'filename': filename, **fact(raw), 'url': expected['url']}
        backend = archives['backend']
        raw = backend.read('backend/dist/backend-v0.json')
        require(sha(raw) == MONOLITH, 'Native backend identity differs')
        native = json.loads(raw)
        manifest_raw = backend.read('backend/dist/manifest.json')
        require(sha(manifest_raw) == MANIFEST, 'Native manifest differs')
        manifest = json.loads(manifest_raw)
        checked = []
        for row in manifest['artifacts']:
            data = backend.read('backend/dist/' + row['path'])
            require(fact(data) == {k: row[k] for k in ['bytes', 'sha256']}, 'Native manifest member mismatch')
            checked.append(row)
        for name in EXPECTED_COUNTS:
            table = [json.loads(line) for line in backend.read('backend/dist/jsonl/' + name + '.jsonl').splitlines() if line.strip()]
            require(table == native[name], 'Native JSONL/monolith disagreement: ' + name)
        texts = {}
        def locate(row, side, content):
            path = row.get(side + '_path') or row.get('source_path')
            options = []
            for kind in ['source', 'labs']:
                for member in [path, 'source/' + path if path else None]:
                    if member and member in archives[kind].namelist():
                        key = (kind, member)
                        if key not in texts:
                            texts[key] = normalized(archives[kind].read(member))
                        options.append((key, texts[key]))
            if not options:
                return {'state': 'path_not_in_released_target_archives', 'path': path}
            unique = {text for _, text in options}
            if len(unique) != 1:
                return {'state': 'conflicting_released_member_bytes', 'path': path}
            (kind, member), text = options[0]
            return {'archive': kind, 'member': member,
                    **text_location(text, content, row.get(side + '_line_start'), row.get(side + '_line_end'))}
        view = project(native, locate)
        lock = {'schema': 'c130-native-ledger-lock/1', 'archives': identities,
                'native_manifest': fact(manifest_raw), 'native_monolith': fact(raw),
                'native_manifest_members_checked': checked, 'native_tables_agree': sorted(EXPECTED_COUNTS),
                'native_modified': False, 'public_bytes_redownloaded_this_pass': False,
                'scope': 'Cached released bytes hash-bound to the previously verified public mapping input.'}
        snapshot = {name: native[name] for name in ['terms', 'concepts', 'corrections', 'rights']}
        lock['native_records_snapshot'] = fact(packed(snapshot))
        # Preserve complete records without the whole book's segment text.
        save(dest / 'input/native-records.json', snapshot)
        save(dest / 'input/source-lock.json', lock)
        save(dest / 'projection.json', view)
        report = {'schema': 'c130-native-ledger-audit/1', 'state': 'verified_metadata_with_explicit_gaps',
                  'projection': fact(packed(view)), 'counts': {k: len(view[k]) for k in ['terms', 'concepts', 'corrections', 'rights', 'segments', 'units']},
                  'segment_checks': {side: dict(Counter(s['verification'][side]['state'] for s in view['segments'])) for side in ['source', 'target']},
                  'native_digest_failures': len(view['audit']['issues']),
                  'native_manifest_files_verified': len(checked), 'semantic_canon_review': False,
                  'whole_native_rebuild': False, 'overall_backend_complete': False}
        save(dest / 'audit.json', report)
        print(json.dumps(report, ensure_ascii=False))
    finally:
        for archive in archives.values():
            archive.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=BASE)
    args = parser.parse_args()
    intake(args.cache, args.out)
