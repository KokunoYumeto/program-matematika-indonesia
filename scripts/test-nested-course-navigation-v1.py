"""Prove explicit same-course child boundaries without permitting arbitrary exclusions."""
import copy
import hashlib
import json
from pathlib import Path
from central_course_navigation_scope_v1 import course_surface_exclusions

ROOT = Path(__file__).resolve().parents[1]
contract = {'readers': [], 'course_surfaces': [
    {'root': 'docs/backend/d60', 'documents': [{'path': 'D60.html', 'course_ids': ['D60']}],
     'exclude_subtrees': ['native-ledger']},
    {'root': 'docs/backend/d60/native-ledger',
     'documents': [{'path': 'ledger.html', 'course_ids': ['D60']}]},
]}
parent = contract['course_surfaces'][0]
assert course_surface_exclusions(parent, contract) == ['native-ledger']
negative = []

def refuse(label, change):
    sample = copy.deepcopy(contract)
    change(sample)
    try:
        course_surface_exclusions(sample['course_surfaces'][0], sample)
    except (ValueError, KeyError, TypeError):
        negative.append(label)
    else:
        raise AssertionError('Unsafe exclusion accepted: ' + label)

refuse('unregistered_subtree', lambda c: c['course_surfaces'].pop())
refuse('foreign_course_child', lambda c: c['course_surfaces'][1]['documents'][0].update(course_ids=['D70']))
refuse('empty_child_scope', lambda c: c['course_surfaces'][1].update(documents=[]))
refuse('duplicate_exclusions', lambda c: c['course_surfaces'][0].update(exclude_subtrees=['native-ledger', 'native-ledger']))
refuse('escaping_subtree', lambda c: c['course_surfaces'][0].update(exclude_subtrees=['../d70']))
refuse('duplicate_child_roots', lambda c: c['course_surfaces'].append(copy.deepcopy(c['course_surfaces'][1])))
actual_path = ROOT / 'backend/authority/central-reader-navigation-v1.json'
raw = actual_path.read_bytes()
actual = json.loads(raw)
for surface in actual['course_surfaces']:
    course_surface_exclusions(surface, actual)
assert course_surface_exclusions(next(s for s in actual['course_surfaces'] if s['root'] == 'docs/backend/d60'), actual) == ['native-ledger']
report = {'schema': 'nested-course-navigation-tests/1', 'state': 'pass',
          'registered_surface_roots': len(actual['course_surfaces']),
          'same_course_explicit_child_boundary': True, 'negative_fixtures': negative,
          'all_registered_exclusions_checked': True,
          'contract': {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()},
          'scope': 'Boundary validation; complete HTML closure and duplicate-page classification are checked by the shared navigation verifier.'}
(ROOT / 'backend/authority/nested-course-navigation-tests-v1.json').write_text(
    json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(report))
