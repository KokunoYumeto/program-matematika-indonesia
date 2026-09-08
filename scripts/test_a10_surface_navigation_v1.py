"""Bounded A10 mixed-language shell/body replay; no browser or source writes."""
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


verify = module('surface_verify', 'validate-central-reader-navigation-v1.py')
shell = module('surface_shell', 'apply-central-course-surface-navigation-v1.py')
contract = json.loads(verify.CONTRACT.read_text(encoding='utf-8'))
surface, = [x for x in contract['course_surfaces'] if x['root'] == 'docs/backend/a10']
assert len(surface['documents']) == 4
for row in surface['documents']:
    p = ROOT / surface['root'] / row['path']
    actual = p.read_text(encoding='utf-8')
    parser = verify.html_parser(p)
    verify.validate_document_locale(p, parser, row, contract['interfaces'])
    expected = (ROOT / 'backend/course-capsule-v1/adapters/a10-capability-v1/views' / row['path']).read_text(encoding='utf-8')
    expected = expected.replace('../data/', 'data/').replace('../validation.json', 'validation.json')
    assert shell.strip_owned_overlay(actual, str(p)) == expected, f'{p}: non-shell source changed'
    assert parser.surface_navigation_placements == ['top', 'bottom']
    # Hosted pages must return to both language course cards at each placement.
    actual_edges = {(x['interface_locale'], x['course_id'], x['placement']) for x in parser.home_links if x['course_card']}
    assert actual_edges == {(lang, 'A10', placement) for lang in ['id', 'en'] for placement in ['top', 'bottom']}

sample = surface['documents'][0]
p = ROOT / surface['root'] / sample['path']
negative_cases = ['wrong_html_language', 'wrong_shell_language', 'missing_shell', 'unknown_locale']
for case in negative_cases:
    row = dict(sample)
    parser = verify.html_parser(p)
    if case == 'wrong_html_language': parser.html_language = 'en'
    if case == 'wrong_shell_language': parser.surface_navigation_names = ['incorrect'] * 2
    if case == 'missing_shell': parser.surface_navigation_names.pop()
    if case == 'unknown_locale': row['locale'] = 'unknown'
    try:
        verify.validate_document_locale(p, parser, row, contract['interfaces'])
    except ValueError:
        pass
    else:
        raise AssertionError(f'Accepted negative case: {case}')
print(json.dumps({'result':'pass', 'a10_documents':4, 'exact_body_replays':4,
                  'locale_bound_shells':4, 'negative_cases_rejected':negative_cases,
                  'browser_testing_claimed':False}))
