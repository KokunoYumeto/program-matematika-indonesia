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
import re
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
NATIVE_INPUT = 'c70da303e2feade5dd52092b8e15b722d0ea8cd5e26be63d8cb001739b55daba'
NATIVE_EXPORTER = '3edee807a41c766c84efbda2a67b209b3d41a8afa7dbf00252ee3cdd846eedb9'
LOCATION_BASELINE = 'bfb6fb2832a2659c24ba67576edc7a9373ae0f7d80e024ba921c88b481945a4f'
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
    # Native locations count LF, not every Unicode boundary recognized by
    # str.splitlines(). A form feed inside graph source is not another LF.
    lines = text.split('\n')
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

def native_blocks(text):
    """Exact nonempty_blocks contract in the hash-bound native exporter."""
    blocks, cursor = [], 0
    for raw in re.split(r'\n[ \t]*\n+', text):
        stripped = raw.strip()
        if not stripped:
            cursor += len(raw)
            continue
        start = text.find(raw, cursor)
        if start < 0:
            start = cursor
        end = start + len(raw)
        blocks.append({'text': stripped, 'line_start': text.count('\n', 0, start) + 1,
                       'line_end': text.count('\n', 0, end) + 1})
        cursor = end
    return blocks

def native_alignment_location(row, text, content, seed, authority):
    """Reconstruct declared native parts; never guess a whitespace alignment."""
    if not seed or seed.get('id') != row.get('unit_id') or seed.get('target_path') != row.get('target_path'):
        return None
    matches = [rule for rule in seed.get('target_block_alignment_overrides', [])
               if rule.get('source_block_index') == row.get('source_block_index')]
    if not matches:
        return None
    require(len(matches) == 1, 'Duplicate native alignment authority')
    rule = matches[0]
    parts = rule['target_parts']
    require(parts and parts[0]['target_block_index'] == row.get('target_block_index'), 'Native alignment first index differs')
    blocks, lines = native_blocks(text), text.splitlines()
    witnesses, contents = [], []
    for part in parts:
        index = part['target_block_index']
        require(isinstance(index, int) and 1 <= index <= len(blocks), 'Native alignment index out of bounds')
        block = blocks[index - 1]
        first, last = part.get('line_start', block['line_start']), part.get('line_end', block['line_end'])
        require(isinstance(first, int) and isinstance(last, int) and
                block['line_start'] <= first <= last <= block['line_end'], 'Native alignment slice out of bounds')
        raw = '\n'.join(lines[first - 1:last])
        contents.append(raw.strip())
        witnesses.append({'target_block_index': index, 'line_range': [first, last],
                          'raw_line_slice_sha256': sha(raw.encode()), 'stripped_part_sha256': sha(raw.strip().encode())})
    extent = [min(part['line_range'][0] for part in witnesses), max(part['line_range'][1] for part in witnesses)]
    require(extent == [row.get('target_line_start'), row.get('target_line_end')], 'Native alignment declared extent differs')
    reconstructed = '\n\n'.join(contents)
    if reconstructed != content:
        return None
    return {'state': 'declared_native_alignment_parts_exact_text', 'line_range': extent,
            'alignment': {'authority': authority, 'source_block_index': rule['source_block_index'],
                          'parts': witnesses, 'reconstructed_content_sha256': sha(reconstructed.encode()),
                          'contract': 'frozen-native-exporter-strip-each-declared-part-then-double-LF-join'}}

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
        input_raw = backend.read('backend/input/backend-input.json')
        exporter_raw = backend.read('scripts/export_backend.py')
        require(sha(input_raw) == NATIVE_INPUT and sha(exporter_raw) == NATIVE_EXPORTER, 'Native alignment authority differs')
        native_input = json.loads(input_raw)
        file_units = index_by_id(native_input['file_units'], 'native file unit')
        alignment_authority = {'input': {'member': 'backend/input/backend-input.json', **fact(input_raw)},
                               'exporter': {'member': 'scripts/export_backend.py', **fact(exporter_raw),
                                            'function_lines': {'nonempty_blocks': [1292, 1308], 'alignment_parts': [1793, 1832]}}}
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
            location = text_location(text, content, row.get(side + '_line_start'), row.get(side + '_line_end'))
            if side == 'target' and location['state'] == 'text_not_found':
                seed = file_units.get(row.get('unit_id'))
                if seed and seed.get('target_block_alignment_overrides'):
                    aligned = native_alignment_location(row, text, content, seed, alignment_authority)
                    if aligned:
                        # A source-bound segment can still reconstruct exactly
                        # when another part of the released file has changed.
                        # Preserve that whole-file mismatch; do not certify it.
                        expected = seed.get('expected_target_sha256')
                        require(isinstance(expected, str) and len(expected) == 64, 'Missing native target-file guard')
                        actual = fact(archives[kind].read(member))
                        aligned['alignment']['target_file_guard'] = {
                            'native_expected_sha256': expected, 'released_file': actual,
                            'whole_file_guard_matches': expected == actual['sha256']}
                        location = aligned
            return {'archive': kind, 'member': member, **location}
        view = project(native, locate)
        baseline_raw = (BASE / 'input/location-review-baseline.json').read_bytes()
        require(sha(baseline_raw) == LOCATION_BASELINE, 'Location review baseline differs')
        baseline = json.loads(baseline_raw)
        segment_index = index_by_id(view['segments'], 'projected segment')
        review_records = []
        for prior_record in baseline['records']:
            current = segment_index[prior_record['id']]
            require(prior_record['native_record_sha256'] == current['canonical_native_record_sha256'], 'Native record changed during location repair')
            review_records.append({**prior_record, 'after_target_verification': current['verification']['target']})
        review = {'schema': 'c130-location-review/1', 'course_id': 'C130',
                  'baseline': fact(baseline_raw), 'records': review_records,
                  'native_alignment_authority': alignment_authority,
                  'native_records_changed': False, 'semantic_canon_review': False,
                  'whole_native_rebuild': False, 'overall_backend_complete': False}
        save(dest / 'input/location-review-baseline.json', baseline_raw)
        save(dest / 'location-review.json', review)
        lock = {'schema': 'c130-native-ledger-lock/1', 'archives': identities,
                'native_manifest': fact(manifest_raw), 'native_monolith': fact(raw),
                'native_manifest_members_checked': checked, 'native_tables_agree': sorted(EXPECTED_COUNTS),
                'native_modified': False, 'public_bytes_redownloaded_this_pass': False,
                'native_alignment_authority': alignment_authority,
                'location_review_baseline': fact(baseline_raw),
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
                  'location_review': fact(packed(review)),
                  'resolved_previously_unresolved_target_locations': len(review_records),
                  'unresolved_target_locations': sum(r['verification']['target']['state'] not in
                      {'no_native_text', 'declared_lines_exact_text', 'unique_exact_text_relocated', 'declared_native_alignment_parts_exact_text'} for r in view['segments']),
                  'native_alignment_whole_file_guard_mismatches': sum(
                      r['verification']['target'].get('alignment', {}).get('target_file_guard', {}).get('whole_file_guard_matches') is False for r in view['segments']),
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
