"""Read exact C130 assessment spans without executing the native exporter.

The released exporter (scripts/export_backend.py:1288-1515,1931,1948)
normalizes CRLF/CR to LF, removes a UTF-8 BOM, masks comments for scanning,
and hashes exact character slices. Line locators are descriptive, not slice
boundaries. This reader implements only the relevant structural grammar;
neither source text nor the frozen native records are changed.
"""
import hashlib
import re


ENVIRONMENTS = re.compile(r'\\begin\{(ex|solution|learningcheckpoint|tryit)\}')
ITEM = re.compile(r'\\item(?:\s*\[[^\]]*\])?\s*\\label\{(ex:[^}]+)\}')
ANSWER = re.compile(r'\\noindent\s*\\textbf\{\\Cref\{([^}]+)\}\}')
MANUAL = re.compile(r'\\exsol\{')
LABEL = re.compile(r'\\label\{([^}]+)\}')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def normalize(raw):
    return raw.decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')


def mask_comments(text):
    """Preserve every character offset, including escaped percent signs."""
    result = list(text)
    cursor = 0
    while cursor < len(text):
        if text[cursor] == '%':
            preceding = cursor - 1
            while preceding >= 0 and text[preceding] == '\\':
                preceding -= 1
            if (cursor - 1 - preceding) % 2 == 0:
                end = text.find('\n', cursor)
                if end < 0:
                    end = len(text)
                result[cursor:end] = ' ' * (end - cursor)
                cursor = end
                continue
        cursor += 1
    return ''.join(result)


def brace_end(text, opening):
    if opening < 0 or opening >= len(text) or text[opening] != '{':
        raise ValueError('Expected opening brace')
    depth, escaped = 0, False
    for position in range(opening, len(text)):
        char = text[position]
        if escaped:
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return position + 1
    raise ValueError('Unclosed command argument')


def structural_spans(raw):
    text = normalize(raw)
    scan = mask_comments(text)
    found = []

    def add(kind, start, end, label):
        body = text[start:end].encode('utf-8')
        found.append({
            'environment': kind, 'label': label,
            'normalized_character_range': [start, end],
            'normalized_utf8_byte_range': [len(text[:start].encode('utf-8')),
                                           len(text[:end].encode('utf-8'))],
            'line_range': [text.count('\n', 0, start) + 1,
                           text.count('\n', 0, end) + 1],
            'content_sha256': digest(body), 'content_bytes': len(body),
        })

    for match in ENVIRONMENTS.finditer(scan):
        kind = match.group(1)
        end_token = '\\end{' + kind + '}'
        end = scan.find(end_token, match.end())
        if end < 0:
            raise ValueError('Missing closing environment: ' + kind)
        end += len(end_token)
        body = scan[match.start():end]
        label = re.search(r'label=\{([^}]+)\}', body[:400]) if kind == 'learningcheckpoint' else None
        label = label or LABEL.search(body)
        add(kind, match.start(), end, label.group(1) if label else None)

    for match in MANUAL.finditer(scan):
        end = brace_end(text, match.end() - 1)
        number = text[match.end():end - 1].strip()
        for _ in range(2):
            opening = scan.find('{', end)
            end = brace_end(text, opening)
        add('manualsolution', match.start(), end, 'exsol:' + number)

    for match in ITEM.finditer(scan):
        next_item = re.search(r'\\item\b', scan[match.end():])
        end = match.end() + next_item.start() if next_item else len(text)
        close = scan.find(r'\end{enumerate}', match.end())
        if close >= 0:
            end = min(end, close)
        add('itemexercise', match.start(), end, match.group(1))

    answers = list(ANSWER.finditer(scan))
    for index, match in enumerate(answers):
        end = answers[index + 1].start() if index + 1 < len(answers) else len(text)
        add('checkpointanswer', match.start(), end, match.group(1))
    return sorted(found, key=lambda x: (x['normalized_character_range'], x['environment']))


def locate(unit, spans):
    """A label alone cannot authorize a match; the native hash is mandatory."""
    environment = unit.get('target_environment')
    expected = unit['target_content_sha256']
    matches = [s for s in spans if s['content_sha256'] == expected
               and (environment is None or s['environment'] == environment)]
    label = unit.get('target_local_id') or unit.get('source_local_id')
    if label is not None:
        matches = [s for s in matches if s['label'] == label]
    recorded = [unit['target_line'], unit['target_line_end']]
    exact = [s for s in matches if s['line_range'] == recorded]
    if len(exact) == 1:
        return {'state': 'exact_native_span', 'span': exact[0]}
    if len(matches) == 1:
        return {'state': 'unique_hash_relocated_native_span', 'span': matches[0]}
    return {'state': 'ambiguous_native_span' if matches else 'unmatched_native_span',
            'candidate_count': len(matches)}


def graph_list_spans(raw):
    """Top-level graph practice items, including previously unlabelled items.

    A nested list is part of its enclosing question, not a new question. The
    three explicitly numbered lists belong to the existing practice section.
    This is an additive current projection, not a change to native identities.
    """
    text = normalize(raw)
    scan = mask_comments(text)
    start = scan.index(r'\textbf{Keterampilan}')
    end = scan.index(r'\subsubsection*{Solusi Terpilih}', start)
    pattern = re.compile(r'\\begin\{enumerate\}(?:\[([^\]]*)\])?|\\end\{enumerate\}|\\item\b(?:\s*\[[^\]]*\])?')
    depth, number, current = 0, 0, None
    rows = []

    def close(position):
        nonlocal current
        if current is not None:
            body = text[current['start']:position]
            current.update(end=position, content_sha256=digest(body.encode()),
                line_range=[text.count('\n',0,current['start'])+1,text.count('\n',0,position)+1],
                label=(LABEL.search(body).group(1) if LABEL.search(body) else None))
            # A figure label inside a question is not an exercise label.
            if current['label'] and not current['label'].startswith('ex:'):
                current['label'] = None
            rows.append(current)
            current = None

    for match in pattern.finditer(scan, start, end):
        token = match.group()
        if token.startswith(r'\begin'):
            depth += 1
            if depth == 1:
                options = match.group(1) or ''
                option = re.fullmatch(r'start=(\d+)',options)
                if options and not option:
                    raise ValueError('Unsupported outer enumeration options')
                number = int(option.group(1))-1 if option else 0
        elif token.startswith(r'\end'):
            if depth == 1:
                close(match.start())
            depth -= 1
            if depth < 0:
                raise ValueError('Unbalanced enumeration')
        elif depth == 1:
            close(match.start())
            number += 1
            current={'number':number,'start':match.start(),'body_start':match.end()}
    if depth or current is not None:
        raise ValueError('Unclosed graph practice enumeration')
    if len({r['number'] for r in rows}) != len(rows):
        raise ValueError('Duplicate graph exercise numbers')
    return rows


def fixtures():
    fixtures_run = []
    raw = b'% \\begin{ex}fake\\end{ex}\r\n\\begin{ex}A \\% B\\end{ex}\r\n'
    spans = structural_spans(raw)
    assert len(spans) == 1 and spans[0]['content_sha256'] == digest(b'\\begin{ex}A \\% B\\end{ex}')
    fixtures_run.append('comments-escaped-percent-and-CRLF')
    raw = ('\\noindent\\textbf{\\Cref{a}}\nfirst\n\n'
           '\\noindent\\textbf{\\Cref{b}}\nlast\n').encode()
    spans = structural_spans(raw)
    assert spans[0]['content_sha256'] == digest(b'\\noindent\\textbf{\\Cref{a}}\nfirst\n\n')
    assert spans[1]['content_sha256'] == digest(b'\\noindent\\textbf{\\Cref{b}}\nlast\n')
    fixtures_run.append('answer-trailing-newlines-and-EOF')
    raw = b'\\item \\label{ex:a}A\n% \\item ignored\n\\item unlabelled sibling\n\\end{enumerate}'
    spans = structural_spans(raw)
    assert len(spans) == 1 and spans[0]['content_sha256'] == digest(b'\\item \\label{ex:a}A\n% \\item ignored\n')
    fixtures_run.append('labelled-item-stops-before-unlabelled-sibling')
    raw = b'\\exsol{2.3}{title {nested}}{answer \\{escaped\\}} trailing'
    span = structural_spans(raw)[0]
    assert span['label'] == 'exsol:2.3'
    assert span['content_sha256'] == digest(raw[:-9])
    fixtures_run.append('manual-nested-and-escaped-braces')
    raw = b'\\begin{ex}same\\end{ex}\n'
    span = structural_spans(raw)[0]
    unit = {'target_content_sha256': span['content_sha256'], 'target_line': 99, 'target_line_end': 99}
    assert locate(unit, [span])['state'] == 'unique_hash_relocated_native_span'
    assert locate(unit, structural_spans(raw + raw))['state'] == 'ambiguous_native_span'
    assert locate(unit, structural_spans(raw.replace(b'same', b'changed')))['state'] == 'unmatched_native_span'
    fixtures_run.extend(['unique-relocation', 'ambiguous-relocation-rejected', 'changed-content-rejected'])
    unit['target_local_id'] = 'wrong'
    assert locate(unit, [span])['state'] == 'unmatched_native_span'
    fixtures_run.append('wrong-label-rejected')
    for bad in [b'\\begin{ex}unclosed', b'\\exsol{1}{unclosed']:
        try:
            structural_spans(bad)
        except ValueError:
            continue
        raise AssertionError('Malformed source accepted')
    fixtures_run.append('malformed-structures-rejected')
    raw = '\ufeff\\begin{ex}中文 α\\end{ex}'.encode('utf-8')
    span = structural_spans(raw)[0]
    assert span['normalized_utf8_byte_range'][1] > span['normalized_character_range'][1]
    assert span['normalized_utf8_byte_range'][1] == span['content_bytes']
    fixtures_run.append('BOM-and-multibyte-offsets')
    raw=(r'\textbf{Keterampilan}\begin{enumerate}\item first'
         r'\begin{enumerate}\item child\end{enumerate}\item second\end{enumerate}'
         r'\begin{enumerate}[start=3]\item third\end{enumerate}'
         r'\subsubsection*{Solusi Terpilih}').encode()
    rows=graph_list_spans(raw)
    assert [r['number'] for r in rows]==[1,2,3]
    assert b'child' in raw[rows[0]['start']:rows[0]['end']]
    fixtures_run.append('graph-top-level-numbering-and-nested-parts')
    return fixtures_run


if __name__ == '__main__':
    import json
    print(json.dumps({'state': 'pass', 'fixtures': fixtures()}))
