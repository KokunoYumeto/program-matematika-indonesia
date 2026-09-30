"""Read-only, exact lexical concordance; never certifies native terminology."""
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

CN = 'http://cnx.rice.edu/cnxml'
MATH = 'http://www.w3.org/1998/Math/MathML'
BLOCKS = {'para', 'title', 'caption', 'item', 'term', 'label', 'entry'}
METHOD = 'NFC-whitespace-collapse-unicode-ignorecase-whole-word-literal-v1'
BOUNDARY = 'CNXML content prose blocks plus every residual text/tail slot; MathML bodies and metadata excluded; no cross-cell or cross-residual-slot phrase joining'


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def normalized(text):
    return ' '.join(unicodedata.normalize('NFC', text).split())


def variants(record):
    # Only the native explicit slash delimiter. Do not invent stems or synonyms.
    return list(dict.fromkeys(normalized(s) for s in record['preferred_term'].split(' / ')))


def pattern(term):
    return re.compile(r'(?<!\w)' + re.escape(term) + r'(?!\w)', re.IGNORECASE)


def qualified(tag):
    require(tag.startswith('{' + CN + '}'), 'Unexpected prose namespace')
    return 'cnxml:' + tag.split('}', 1)[1]


def prose(node):
    if node.tag.startswith('{' + MATH + '}'):
        return ' '
    if node.tag == '{' + CN + '}newline':
        return ' '
    return (node.text or '') + ''.join(prose(child) + (child.tail or '') for child in node)


def text_blocks(root):
    require(root.tag == '{' + CN + '}document', 'Not a CNXML document')
    contents = [node for node in root if node.tag == '{' + CN + '}content']
    require(len(contents) == 1, 'Missing or duplicated content')
    blocks, unwrapped = [], []

    def visit(node, path):
        if node.tag.startswith('{' + MATH + '}'):
            return
        local = node.tag.split('}', 1)[-1]
        if node.tag.startswith('{' + CN + '}') and local in BLOCKS:
            text = normalized(prose(node))
            if text:
                blocks.append({'xpath': path, 'xml_id': node.get('id'), 'text': text})
            return  # No ancestor/descendant double counting.
        if normalized(node.text or ''):
            unwrapped.append({'xpath': path + '/text()[1]', 'xml_id': node.get('id'), 'text': normalized(node.text), 'sha256': digest(normalized(node.text).encode())})
        counts = {}
        for child in node:
            counts[child.tag] = counts.get(child.tag, 0) + 1
            if not child.tag.startswith('{' + MATH + '}'):
                visit(child, path + '/' + qualified(child.tag) + '[' + str(counts[child.tag]) + ']')
            if normalized(child.tail or ''):
                unwrapped.append({'xpath': path + '/' + ('mathml:' + child.tag.split('}', 1)[1] if child.tag.startswith('{' + MATH + '}') else qualified(child.tag)) + '[' + str(counts[child.tag]) + ']/following-sibling::text()[1]',
                                  'xml_id': node.get('id'), 'text': normalized(child.tail), 'sha256': digest(normalized(child.tail).encode())})

    visit(contents[0], '/cnxml:document[1]/cnxml:content[1]')
    return blocks, unwrapped


def collect(ledger, native):
    choices = [row for row in ledger['terms'] if row.get('source_record_id')]
    require(len(choices) == 20, 'Wrong lexical choice scope')
    result = {'schema': 'a00-term-locations/1', 'course_id': 'A00', 'method': METHOD,
              'boundary': BOUNDARY, 'source_content_reread': False,
              'semantic_canon_review': False, 'scope_application_checked': False,
              'native_files_modified': False, 'modules': [], 'choices': [],
              'provenance': {'model': 'OpenAI Codex gpt-6.1-sol', 'effort': 'Ultra', 'work': 'Exact lexical target-text concordance, not translation or semantic canon review'}}
    indexed = []
    for module in ledger['modules']:
        mid = module['module_id']
        relative = 'modules/' + mid + '/index.cnxml'
        path = (native / relative).resolve()
        path.relative_to(native.resolve())
        require(path.is_file() and not path.is_symlink(), 'Missing or linked target witness')
        body = path.read_bytes()
        require({'bytes': len(body), 'sha256': digest(body)} == {k: module['target'][k] for k in ('bytes', 'sha256')}, 'Target bytes drift: ' + mid)
        require(b'<!DOCTYPE' not in body and b'<!ENTITY' not in body, 'External XML definitions forbidden')
        blocks, unwrapped = text_blocks(ET.fromstring(body))
        result['modules'].append({'module_id': mid, 'path': relative, 'bytes': len(body), 'sha256': digest(body),
                                  'prose_blocks': len(blocks), 'unwrapped_text_slots': [{k: slot[k] for k in ('xpath', 'sha256')} for slot in unwrapped]})
        indexed.append((mid, relative, blocks + unwrapped))
    for choice in choices:
        entry = {'choice_id': choice['id'], 'source_record_id': choice['source_record_id'],
                 'preferred_term': choice['preferred_term'], 'native_scope': choice['scope'],
                 'variants': variants(choice), 'matches': []}
        for term in entry['variants']:
            regex = pattern(term)
            for mid, relative, blocks in indexed:
                for block in blocks:
                    for match in regex.finditer(block['text']):
                        start, end = match.span()
                        excerpt_start = max(0, start - 65)
                        excerpt_end = min(len(block['text']), end + 65)
                        entry['matches'].append({'module_id': mid, 'path': relative, 'xpath': block['xpath'], 'xml_id': block['xml_id'],
                                                 'block_text_sha256': digest(block['text'].encode()), 'block_characters': len(block['text']),
                                                 'variant': term, 'start': start, 'end': end,
                                                 'excerpt_start': excerpt_start, 'excerpt': block['text'][excerpt_start:excerpt_end]})
        entry['match_count'] = len(entry['matches'])
        entry['module_count'] = len({r['module_id'] for r in entry['matches']})
        result['choices'].append(entry)
    result['summary'] = {'target_modules': len(result['modules']), 'lexical_choices': len(choices),
                         'choice_variant_matches': sum(r['match_count'] for r in result['choices']),
                         'distinct_text_ranges': len({(h['module_id'], h['xpath'], h['start'], h['end']) for r in result['choices'] for h in r['matches']}),
                         'zero_match_choice_ids': [r['choice_id'] for r in result['choices'] if not r['matches']],
                         'unwrapped_text_slots': sum(len(r['unwrapped_text_slots']) for r in result['modules'])}
    validate(result, ledger)
    return result


def validate(proof, ledger):
    require(proof['schema'] == 'a00-term-locations/1' and proof['course_id'] == 'A00', 'Wrong concordance identity')
    require(proof['method'] == METHOD and proof['boundary'] == BOUNDARY, 'Concordance method drift')
    for key in ('source_content_reread', 'semantic_canon_review', 'scope_application_checked', 'native_files_modified'):
        require(proof[key] is False, 'Unsupported concordance approval')
    expected = {r['module_id']: r for r in ledger['modules']}
    require(len(proof['modules']) == len(expected) == 75 and {r['module_id'] for r in proof['modules']} == set(expected), 'Concordance module coverage drift')
    for row in proof['modules']:
        require(row['path'] == 'modules/' + row['module_id'] + '/index.cnxml', 'Unsafe concordance target path')
        require({k: row[k] for k in ('bytes', 'sha256')} == {k: expected[row['module_id']]['target'][k] for k in ('bytes', 'sha256')}, 'Concordance target identity drift')
        require(isinstance(row['prose_blocks'], int) and row['prose_blocks'] >= 0, 'Invalid block count')
        require(len({r['xpath'] for r in row['unwrapped_text_slots']}) == len(row['unwrapped_text_slots']), 'Duplicate unwrapped text slot')
    choices = {r['id']: r for r in ledger['terms'] if r.get('source_record_id')}
    require(len(proof['choices']) == len(choices) == 20 and {r['choice_id'] for r in proof['choices']} == set(choices), 'Concordance choice coverage drift')
    for entry in proof['choices']:
        choice = choices[entry['choice_id']]
        require(entry['source_record_id'] == choice['source_record_id'] and entry['preferred_term'] == choice['preferred_term'] and entry['native_scope'] == choice['scope'] and entry['variants'] == variants(choice), 'Concordance native choice changed')
        seen = set()
        for hit in entry['matches']:
            require(hit['module_id'] in expected and hit['path'] == 'modules/' + hit['module_id'] + '/index.cnxml', 'Concordance match target drift')
            require(re.fullmatch(r'/cnxml:document\[1\]/cnxml:content\[1\](?:/cnxml:[A-Za-z][A-Za-z0-9_-]*\[[1-9][0-9]*\])*(?:(?:/mathml:[A-Za-z][A-Za-z0-9_-]*\[[1-9][0-9]*\])?/following-sibling::text\(\)\[1\]|/text\(\)\[1\])?', hit['xpath']) is not None, 'Invalid CNXML location')
            require(hit['xml_id'] is None or isinstance(hit['xml_id'], str), 'Invalid native XML identifier')
            require(re.fullmatch('[0-9a-f]{64}', hit['block_text_sha256']) is not None, 'Invalid block digest')
            require(hit['variant'] in entry['variants'] and 0 <= hit['start'] < hit['end'] <= hit['block_characters'], 'Invalid match range')
            require(hit['excerpt_start'] == max(0, hit['start'] - 65) and len(hit['excerpt']) <= len(hit['variant']) + 130, 'Invalid bounded excerpt')
            local_start, local_end = hit['start'] - hit['excerpt_start'], hit['end'] - hit['excerpt_start']
            matches = [m.span() for m in pattern(hit['variant']).finditer(hit['excerpt'])]
            require((local_start, local_end) in matches, 'Excerpt does not witness literal choice')
            identity = (hit['module_id'], hit['xpath'], hit['start'], hit['end'], hit['variant'])
            require(identity not in seen, 'Duplicate concordance match')
            seen.add(identity)
        require(entry['match_count'] == len(entry['matches']) and entry['module_count'] == len({r['module_id'] for r in entry['matches']}), 'Concordance counts drift')
    summary = {'target_modules': 75, 'lexical_choices': 20,
               'choice_variant_matches': sum(r['match_count'] for r in proof['choices']),
               'distinct_text_ranges': len({(h['module_id'], h['xpath'], h['start'], h['end']) for r in proof['choices'] for h in r['matches']}),
               'zero_match_choice_ids': [r['choice_id'] for r in proof['choices'] if not r['matches']],
               'unwrapped_text_slots': sum(len(r['unwrapped_text_slots']) for r in proof['modules'])}
    require(proof['summary'] == summary, 'Concordance summary drift')
    return proof
