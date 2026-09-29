"""Extract identity-bound OpenLogic problems without changing or executing TeX.

This is a source inventory, not a TeX interpreter or a claim that every source
problem is present exactly once in a given PDF. Rendered occurrences are a
separate join. Comments and verbatim bodies are masked with positions retained.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'backend/course-capsule-v1/adapters/openlogic-v231'
OUT = ROOT / 'backend/course-capsule-v1/adapters/openlogic-teacher-v1'
UPSTREAM = '9620cc73f9c8e0ad003c514a5d3748f29611c4c0'
ENV = re.compile(r'\\(begin|end)\s*\{([^{}]+)\}')
PROBLEMS = {'prob', 'probtag'}


def identity(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def clean_tex(text):
    """Mask TeX comments/literal text, preserving all character offsets.

    Escaped control symbols consume their next character, so \\% is literal
    whereas an even run of backslashes followed by % starts a comment.
    Unsupported literal environments are rejected rather than silently parsed.
    """
    result = list(text)
    i = 0
    while i < len(text):
        if text[i] == '%':
            end = text.find('\n', i)
            end = len(text) if end < 0 else end
            result[i:end] = ' ' * (end-i)
            i = end
        elif text[i] == '\\':
            literal = re.match(r'\\verb\*?([^A-Za-z\s])', text[i:])
            if literal:
                start = i + literal.end()
                end = text.find(literal[1], start)
                if end < 0 or '\n' in text[start:end]:
                    raise ValueError('Unclosed inline verbatim')
                result[i:end+1] = ' ' * (end+1-i)
                i = end+1
            elif text.startswith('\\begin{verbatim}', i) or text.startswith('\\begin{verbatim*}', i):
                marker = '\\end{verbatim*}' if text.startswith('\\begin{verbatim*}', i) else '\\end{verbatim}'
                end = text.find(marker, i)
                if end < 0:
                    raise ValueError('Unclosed verbatim environment')
                end += len(marker)
                result[i:end] = ['\n' if c == '\n' else ' ' for c in text[i:end]]
                i = end
            else:
                i += 2
        else:
            i += 1
    masked = ''.join(result)
    if re.search(r'\\begin\s*\{(?:Verbatim|lstlisting|minted|comment)\}', masked):
        raise ValueError('Unsupported literal environment; add an explicit parser rule')
    return masked


def blocks(data):
    text = data.decode('utf-8-sig')
    masked = clean_tex(text)
    stack = []
    found = []
    for token in ENV.finditer(masked):
        kind, env = token.groups()
        # Only track problem blocks: unrelated environments can be opened and
        # closed in different imported files, but problems must be self-contained.
        if env not in PROBLEMS:
            continue
        if kind == 'begin':
            if stack:
                raise ValueError('Nested problem environment')
            stack.append(token)
        else:
            if not stack or stack[-1][2] != env:
                raise ValueError('Unbalanced problem environment')
            start = stack.pop()
            body = text[start.end():token.start()]
            clean_body = masked[start.end():token.start()]
            offset0 = len(text[:start.start()].encode('utf-8')) + (3 if data.startswith(b'\xef\xbb\xbf') else 0)
            offset1 = len(text[:token.end()].encode('utf-8')) + (3 if data.startswith(b'\xef\xbb\xbf') else 0)
            found.append({
                'environment': env,
                'ordinal': len(found)+1,
                'start_line': text.count('\n', 0, start.start())+1,
                'end_line': text.count('\n', 0, token.end())+1,
                'byte_start': offset0,
                'byte_end_exclusive': offset1,
                'block': identity(data[offset0:offset1]),
                'labels': re.findall(r'\\ollabel\s*\{([^{}]+)\}', clean_body),
                'literal_labels': re.findall(r'\\label\s*\{([^{}]+)\}', clean_body),
                'environments': [e[1] for e in re.findall(r'\\(begin)\s*\{([^{}]+)\}', clean_body)],
                # For evidence matching only; no translated prose is changed.
                '_body': body,
                '_clean_body': clean_body,
            })
    if stack:
        raise ValueError('Unclosed problem environment')
    return found


def checked_file(path, expected):
    data = path.read_bytes()
    assert identity(data) == {k: expected[k] for k in ['bytes', 'sha256']}, str(path)
    return data


def materialized_source(raw, expected):
    if identity(raw) == expected:
        return raw, 'exact_archive_bytes'
    crlf = raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    assert identity(crlf) == expected, 'Source differs beyond the recorded LF/CRLF materialization'
    return crlf, 'frozen_CRLF_materialization'


def collect(workspace):
    authority_path = NATIVE/'INPUT_AUTHORITIES.json'
    authority = json.loads(authority_path.read_bytes())
    by_role = {a['role']: a for a in authority['authorities']}
    archive_bodies = {}
    for role in ['frozen_upstream_zip', 'frozen_localized_zip']:
        ref = by_role[role]
        archive_bodies[role] = checked_file(workspace/ref['path'], ref)
    units_path = NATIVE/'tables/units.jsonl'
    units = [json.loads(line) for line in units_path.read_bytes().splitlines()]
    assert len(units) == 722
    rows = []
    identities = []
    byte_modes = Counter()
    target_prefix = 'source/'
    upstream_prefix = f'OpenLogic-{UPSTREAM}/'
    with zipfile.ZipFile(workspace/by_role['frozen_upstream_zip']['path']) as source_zip, zipfile.ZipFile(workspace/by_role['frozen_localized_zip']['path']) as target_zip:
        for unit in sorted(units, key=lambda u: u['payload']['native_unit_id']):
            p = unit['payload']
            loc = p['native_locator']
            source_raw = source_zip.read(upstream_prefix+loc['source_path'])
            source, mode = materialized_source(source_raw, {'bytes': p['source_bytes'], 'sha256': p['source_sha256']})
            target = target_zip.read(target_prefix+loc['target_path'])
            assert identity(target) == {'bytes': p['target_bytes'], 'sha256': p['target_sha256']}
            byte_modes[mode] += 1
            source_blocks, target_blocks = blocks(source), blocks(target)
            signature = lambda bs: [(b['environment'], b['environments']) for b in bs]
            assert signature(source_blocks) == signature(target_blocks), ('Problem structure drift', p['native_unit_id'])
            file_id = re.findall(r'\\olfileid(?:\[[^\]]*\])?\s*\{([^{}]+)\}\s*\{([^{}]+)\}\s*\{([^{}]+)\}', clean_tex(source.decode('utf-8-sig')))
            target_file_id = re.findall(r'\\olfileid(?:\[[^\]]*\])?\s*\{([^{}]+)\}\s*\{([^{}]+)\}\s*\{([^{}]+)\}', clean_tex(target.decode('utf-8-sig')))
            assert file_id == target_file_id
            if source_blocks:
                assert file_id, (p['native_unit_id'], file_id)
            unit_record = {
                'native_unit_id': p['native_unit_id'], 'projected_unit_id': unit['id'],
                'source_path': loc['source_path'], 'target_path': loc['target_path'],
                'source': identity(source), 'source_archive_member': identity(source_raw),
                'source_byte_mode': mode, 'target': identity(target),
                'problem_count': len(source_blocks),
                'in_frozen_main_reader': p['canonical_reader_reachable'],
                'canonical_reader_order': p['canonical_reader_order'],
            }
            identities.append(unit_record)
            for sb, tb in zip(source_blocks, target_blocks):
                row = {
                    'id': f"c80:{p['native_unit_id']}:problem:{sb['ordinal']:03d}",
                    'course_id': 'C80', 'native_unit_id': p['native_unit_id'],
                    'projected_unit_id': unit['id'],
                    'source_path': loc['source_path'], 'target_path': loc['target_path'],
                    'file_id_contexts': [':'.join(f) for f in file_id],
                    'in_frozen_main_reader': p['canonical_reader_reachable'],
                    'source': {k: v for k, v in sb.items() if not k.startswith('_')},
                    'target': {k: v for k, v in tb.items() if not k.startswith('_')},
                    'fully_qualified_label_candidates': sorted(set(tb['literal_labels']+[':'.join(f)+':'+label for f in target_file_id for label in tb['labels']])),
                    'source_target_labels_identical': (sb['labels'], sb['literal_labels']) == (tb['labels'], tb['literal_labels']),
                    'reader_occurrences': [],
                    'reader_mapping_state': 'not_yet_reconciled',
                    'solution_state': 'not_inferred_from_problem_or_example',
                }
                rows.append(row)
    assert len({r['id'] for r in rows}) == len(rows)
    return {
        'schema': 'openlogic-source-problems/1', 'course_id': 'C80',
        'upstream_commit': UPSTREAM,
        'scope': 'All problem/probtag blocks in the 722 frozen source/target content files; not examples, not inferred rendered counts.',
        'authorities': {
            'native_units': {'path': 'backend/course-capsule-v1/adapters/openlogic-v231/tables/units.jsonl', **identity(units_path.read_bytes())},
            'native_input_authorities': {'path': 'backend/course-capsule-v1/adapters/openlogic-v231/INPUT_AUTHORITIES.json', **identity(authority_path.read_bytes())},
            'source_archive': {k: by_role['frozen_upstream_zip'][k] for k in ['bytes', 'sha256']},
            'target_archive': {k: by_role['frozen_localized_zip'][k] for k in ['bytes', 'sha256']},
        },
        'counts': {
            'source_target_files': len(units), 'source_problems': len(rows),
            'source_problems_main': sum(r['in_frozen_main_reader'] for r in rows),
            'source_problems_supplement': sum(not r['in_frozen_main_reader'] for r in rows),
            'labelled_source_problems': sum(bool(r['fully_qualified_label_candidates']) for r in rows),
            'source_target_label_changes': sum(not r['source_target_labels_identical'] for r in rows),
            'byte_modes': dict(byte_modes),
        },
        'units': identities, 'problems': rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--out', type=Path, default=OUT/'source-problems.json')
    args = parser.parse_args()
    result = collect(args.workspace)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'pass', **result['counts'], 'output': identity(args.out.read_bytes())}))


if __name__ == '__main__':
    main()
