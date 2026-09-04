"""Independent checks for the capability projection (not full native replay)."""
from collections import defaultdict
from copy import deepcopy

UNIT_FIELDS = ['id', 'semantic_key', 'source_local_id', 'resource_id', 'edition_id',
               'rights_id', 'parent_id', 'order_key', 'concept_ids']
TERM_FIELDS = ['id', 'concept_id', 'preferred', 'variants', 'rejected_forms',
               'scope_ids', 'evidence', 'ledger_binding', 'rights_id']


def validate_support(native, relations, projected):
    by_id = {row['id']: row for row in native}
    expected = defaultdict(dict)
    kinds = {'hints': 'hint', 'answers': 'answer', 'solves': 'solution'}
    for relation in relations:
        if relation['predicate'] not in kinds:
            continue
        child, exercise = by_id[relation['subject_id']], by_id[relation['object_id']]
        assert exercise['unit_kind'] == 'exercise'
        assert child['unit_kind'] == kinds[relation['predicate']]
        edge = expected[exercise['id']].setdefault(child['id'],
            {'id': child['id'], 'kind': child['unit_kind'], 'evidence': []})
        edge['evidence'].append({'basis': 'explicit_native_relation', 'relation_id': relation['id']})
    for child in native:
        parent = by_id.get(child.get('parent_id'))
        if parent and parent['unit_kind'] == 'exercise' and child['unit_kind'] in kinds.values():
            edge = expected[parent['id']].setdefault(child['id'],
                {'id': child['id'], 'kind': child['unit_kind'], 'evidence': []})
            edge['evidence'].append({'basis': 'native_parent_id'})
    assert len(projected) == len(native)
    assert {row['id'] for row in projected} == set(by_id)
    for row in projected:
        edges = {edge['id']: edge for edge in row['support']}
        assert len(edges) == len(row['support']), 'Duplicate support edge'
        assert edges == expected[row['id']], 'Support IDs/kinds/evidence union differs'
        assert row['support_state'] == by_id[row['id']].get('exercise_metadata', {}).get('solution_status')


def validate_projection(input_data, model):
    native = input_data['units']
    validate_support(native, input_data['relations'], model['units'])
    for key in ('resources', 'editions', 'rights', 'relations'):
        assert model[key] == input_data[key], key
    policy = model['projection_policy']
    assert policy['whole_records_preserved'] == ['resources', 'editions', 'rights', 'relations']
    for kind, copied in [('units', UNIT_FIELDS), ('terms', TERM_FIELDS)]:
        source = {row['id']: row for row in input_data[kind]}
        assert len(model[kind]) == len(source)
        assert {row['id'] for row in model[kind]} == set(source)
        assert policy[kind]['copied_fields'] == copied
        expected_loss = sorted(set().union(*(row.keys() for row in source.values())) - set(copied))
        assert policy[kind]['not_copied_whole'] == expected_loss
        for row in model[kind]:
            for field in copied:
                assert row[field] == source[row['id']][field], (kind, row['id'], field)
    by_id = {row['id']: row for row in model['units']}
    for row in native:
        result = by_id[row['id']]
        assert result['target_components'] == row['manifest_binding']['target_components']
        assert result['source_components'] == row['manifest_binding']['source_components']


def support_fixture_checks():
    native = [
        {'id': 'e', 'unit_kind': 'exercise', 'parent_id': None, 'exercise_metadata': {'solution_status': 'unknown'}},
        {'id': 'section', 'unit_kind': 'section', 'parent_id': None},
        {'id': 'relation-only', 'unit_kind': 'solution', 'parent_id': 'section'},
        {'id': 'child-only', 'unit_kind': 'hint', 'parent_id': 'e'},
        {'id': 'both', 'unit_kind': 'answer', 'parent_id': 'e'},
    ]
    relations = [
        {'id': 'r1', 'predicate': 'solves', 'subject_id': 'relation-only', 'object_id': 'e'},
        {'id': 'r2', 'predicate': 'solves', 'subject_id': 'relation-only', 'object_id': 'e'},
        {'id': 'r3', 'predicate': 'answers', 'subject_id': 'both', 'object_id': 'e'},
    ]
    output = [{'id': row['id'], 'support_state': 'unknown' if row['id'] == 'e' else None, 'support': []} for row in native]
    output[0]['support'] = [
        {'id': 'relation-only', 'kind': 'solution', 'evidence': [{'basis': 'explicit_native_relation', 'relation_id': 'r1'}, {'basis': 'explicit_native_relation', 'relation_id': 'r2'}]},
        {'id': 'both', 'kind': 'answer', 'evidence': [{'basis': 'explicit_native_relation', 'relation_id': 'r3'}, {'basis': 'native_parent_id'}]},
        {'id': 'child-only', 'kind': 'hint', 'evidence': [{'basis': 'native_parent_id'}]},
    ]
    validate_support(native, relations, output)
    def wrong_kind(rows): rows[0]['support'][0]['kind'] = 'hint'
    def false_completeness(rows): rows[0]['support_state'] = 'full_solution'
    mutations = [lambda rows: rows[0]['support'].pop(),
                 lambda rows: rows[0]['support'][0]['evidence'].pop(),
                 lambda rows: rows[0]['support'][0]['evidence'].append({'basis': 'native_parent_id'}),
                 lambda rows: rows[0]['support'].append(deepcopy(rows[0]['support'][0])),
                 wrong_kind, false_completeness]
    for mutate in mutations:
        changed = deepcopy(output)
        mutate(changed)
        try:
            validate_support(native, relations, changed)
        except AssertionError:
            continue
        raise AssertionError('Invalid support fixture accepted')
    return len(mutations)
