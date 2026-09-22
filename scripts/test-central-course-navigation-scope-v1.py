"""Reject hidden/unclassified subtrees and cross-course reader return links."""
from copy import deepcopy
import json
from pathlib import Path
from central_course_navigation_scope_v1 import course_surface_exclusions, reader_course_targets

root = Path(__file__).resolve().parents[1]
contract = json.loads((root / 'backend/authority/central-reader-navigation-v1.json').read_text(encoding='utf-8'))
surface = next(s for s in contract['course_surfaces'] if s['root'] == 'docs/backend/d50')
reader = next(r for r in contract['readers'] if r['root'] == 'docs/backend/d50/reader')
assert course_surface_exclusions(surface, contract) == ['reader']
assert len(reader_course_targets(reader, contract, root)) == 2
tests = 0
for values in [['missing'], ['reader', 'reader'], ['../d20'], ['/reader'], ['reader/../reader'], ['reader\\index.html']]:
    row = deepcopy(surface)
    row['exclude_subtrees'] = values
    try:
        course_surface_exclusions(row, contract)
    except ValueError:
        tests += 1
    else:
        raise AssertionError(values)
for values in [['docs/backend/d20/D20.html'], ['docs/missing.html'], ['../docs/backend/d50/index.html'], ['docs/backend/d50/index.html'] * 2]:
    row = deepcopy(reader)
    row['related_course_surface_paths'] = values
    try:
        reader_course_targets(row, contract, root)
    except ValueError:
        tests += 1
    else:
        raise AssertionError(values)
print(json.dumps({'status': 'pass', 'negative_fixtures': tests, 'reader_role': 'D50', 'unclassified_exclusions_allowed': False}))
