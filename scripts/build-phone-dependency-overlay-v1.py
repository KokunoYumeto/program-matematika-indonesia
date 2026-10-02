"""Source-bound, zero-copy integration with the existing phone reader.

Capture only explicit inputs; never edit the producer. Offline replay is the
default. The output distinguishes preparation, reading and reported proof uses.
No graph edge is mathematical certification or authority to publish a lesson.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / 'backend/cross-programme-v1'
OUT = BRIDGE / 'phone-current-20261002'
PHONE = ROOT.parents[2] / 'kerodon_to_stacks_extension_20260906/reader/course_inputs'
PUBLIC_COMMIT = '604f883c03e5564ecd351514fa22b08f322488b2'
PUBLIC_URL = 'https://raw.githubusercontent.com/KokunoYumeto/open-mathematics-courses/' + PUBLIC_COMMIT + '/docs/courses.json'
CATALOG = 'COMPLETE_SELECTION_SUPPORTED_CATALOG_20261002.json'
RECIPE = 'COMPLETE_SELECTION_SUPPORTED_INPUTS_20261002.json'
PROVIDER = BRIDGE / 'provider-handoffs/B40-basis-extension-20261002/PROVIDER_HANDOFF.json'
HEX = re.compile(r'^[0-9a-fA-F]{64}$')


def digest(b):
    return hashlib.sha256(b).hexdigest()


def dump(o):
    return (json.dumps(o, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def fact(name, b):
    return {'path': name, 'bytes': len(b), 'sha256': digest(b)}


def relative(root, name):
    assert isinstance(name, str) and '\\' not in name and ':' not in name
    target = (root / name).resolve()
    assert target.is_relative_to(root.resolve()), 'path escapes source root'
    return target


def frozen_write(p, b):
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        assert p.read_bytes() == b, 'refuse replacement of frozen input: ' + str(p)
    else:
        with p.open('xb') as f:
            f.write(b)


def unit_map(catalog):
    result = {}
    for c in catalog['courses']:
        for u in c['units']:
            key = c['id'] + '/' + u['id']
            assert key not in result, 'duplicate native unit ID'
            assert HEX.fullmatch(u['source_sha256'])
            result[key] = u
    return result


def capture():
    inputs = {
        'phone-catalog.json': (PHONE / CATALOG).read_bytes(),
        'phone-recipe.json': (PHONE / RECIPE).read_bytes(),
        'published-bridge.json': (BRIDGE / 'bridge.json').read_bytes(),
        'previous-phone-catalog.json': (BRIDGE / 'inputs/20261002/phone-catalog.json').read_bytes(),
        'B40-PROVIDER_HANDOFF.json': PROVIDER.read_bytes(),
    }
    req = urllib.request.Request(PUBLIC_URL, headers={'User-Agent': 'Open-Courses-bounded-dependency-integration'})
    with urllib.request.urlopen(req, timeout=30) as response:
        assert response.status == 200
        inputs['public-advanced-courses.json'] = response.read()
    catalog = json.loads(inputs['phone-catalog.json'])
    recipe = json.loads(inputs['phone-recipe.json'])
    assert digest(inputs['phone-catalog.json']) == recipe['catalog_sha256'].lower()
    observed = []
    # Only explicit catalogue paths, never a directory or repository scan.
    declarations = [('lesson', key, u['source'], u['source_sha256']) for key, u in unit_map(catalog).items()]
    declarations += [('licence_descriptor', r['course_id'], r['source'], r['sha256']) for r in recipe['course_license_provenance']]
    for r in catalog.get('reference_editions', []):
        declarations.append(('reference_edition', r['id'], r['source'], r['source_sha256']))
        if r.get('license_source'):
            declarations.append(('reference_licence', r['id'], r['license_source'], r['license_sha256']))
    for kind, key, path, sha in declarations:
        data = relative(PHONE, path).read_bytes()
        assert digest(data) == sha.lower(), 'live source identity mismatch: ' + key
        observed.append({'kind': kind, 'native_id': key, **fact(path, data)})
    # Fail if the producer moved the selected input during the read.
    assert (PHONE / CATALOG).read_bytes() == inputs['phone-catalog.json']
    assert (PHONE / RECIPE).read_bytes() == inputs['phone-recipe.json']
    inputs['SOURCE_IDENTITY_READBACK.json'] = dump({'schema': 'explicit-source-readback/1', 'scope': 'file identity only, not proof or rights adjudication', 'files': observed})
    for name, data in inputs.items():
        frozen_write(OUT / 'inputs' / name, data)
    frozen_write(OUT / 'INPUTS.json', dump({
        'schema': 'phone-dependency-overlay-inputs/1',
        'public_advanced_commit': PUBLIC_COMMIT,
        'public_advanced_url': PUBLIC_URL,
        'phone_catalog_logical_path': 'reader/course_inputs/' + CATALOG,
        'phone_recipe_logical_path': 'reader/course_inputs/' + RECIPE,
        'inputs': [fact('inputs/' + k, v) for k, v in inputs.items()],
        'scope': 'two distinct edition snapshots, not additive lesson counts',
    }))


def load():
    manifest = json.loads((OUT / 'INPUTS.json').read_bytes())
    inputs = {}
    for row in manifest['inputs']:
        data = relative(OUT, row['path']).read_bytes()
        assert len(data) == row['bytes'] and digest(data) == row['sha256']
        inputs[Path(row['path']).name] = json.loads(data)
    assert inputs['phone-recipe.json']['catalog_sha256'].lower() == digest((OUT / 'inputs/phone-catalog.json').read_bytes())
    return manifest, inputs


def build(inputs):
    current = inputs['phone-catalog.json']
    old = inputs['previous-phone-catalog.json']
    bridge = inputs['published-bridge.json']
    public = inputs['public-advanced-courses.json']
    provider = inputs['B40-PROVIDER_HANDOFF.json']
    recipe = inputs['phone-recipe.json']
    units, previous = unit_map(current), unit_map(old)
    core = {c['id']: c for c in bridge['courses']['core']}
    selected = {c['id']: c for c in current['courses']}
    published = {c['id']: c for c in public['courses']}
    assert len(selected) == len(current['courses'])
    assert len(published) == len(public['courses'])
    preparation = []
    unknown = []
    for c in public['courses']:
        for target in c.get('take_first', {}).get('core', []):
            if target not in core:
                unknown.append({'course': c['id'], 'core_id': target})
                continue
            preparation.append({
                'from': 'advanced:' + c['id'], 'to': 'core:' + target,
                'relation': 'preparation_course', 'source_field': 'take_first.core',
                'source_commit': PUBLIC_COMMIT,
                'phone_course_selected': c['id'] in selected,
                'same_course_id_is_not_same_lesson_edition': True,
                'proof_closed': False,
            })
    exact = []
    for edge in current['dependency_locators']:
        assert edge['from'] in units and edge['target'] in units, 'missing native endpoint'
        assert units[edge['from']]['source_sha256'].lower() == edge['from_source_sha256'].lower(), 'consumer hash mismatch'
        assert units[edge['target']]['source_sha256'].lower() == edge['target_source_sha256'].lower(), 'provider hash mismatch'
        exact.append({**edge, 'relation': 'lesson_reading', 'proof_closed': False})
    proofs = []
    for row in current['foundation_proof_records']:
        p = row['proof']
        assert p['unit'] in units
        assert p['source_sha256'].lower() == units[p['unit']]['source_sha256'].lower()
        anchors = units[p['unit']].get('heading_anchors')
        if anchors is not None:
            assert any(p['anchor'] in h['ids'] for h in anchors)
        proofs.append({'native_record': row, 'state': 'producer_reported_not_independently_admitted', 'proof_closed': False})
    assert not provider['states']['phone_comparison_admitted']
    comparisons = []
    for c in provider['consumers']:
        key = c['course'] + '/' + c['lesson']
        assert key in units
        matches = units[key]['source_sha256'].lower() == c['source']['sha256'].lower()
        comparisons.append({
            'core_id': provider['course'], 'provider_id': provider['id'],
            'consumer_unit': key, 'use_locators': c['uses'],
            'consumer_sha256': units[key]['source_sha256'],
            'compared_consumer_sha256': c['source']['sha256'],
            'source_identity_matches_checked_packet': matches,
            'comparison': provider['mathematical_comparison'] if matches else None,
            'state': 'producer_checked_owner_integration_pending' if matches else 'source_changed_reconciliation_required',
            'conditions': provider['conditions'], 'proof_units': provider['complete_proof_units'],
            'rights': provider['rights'], 'scope_exclusions': provider['scope_exclusions'],
            'public_reader': None, 'owner_admitted': False, 'proof_closed': False,
        })
    changes = []
    for key in sorted(set(units) | set(previous)):
        before, after = previous.get(key), units.get(key)
        kind = 'added' if before is None else 'removed' if after is None else 'source_changed' if before['source_sha256'].lower() != after['source_sha256'].lower() else 'metadata_changed' if before != after else 'unchanged'
        if kind != 'unchanged':
            changes.append({'unit': key, 'change': kind, 'before_sha256': before['source_sha256'] if before else None, 'after_sha256': after['source_sha256'] if after else None,
                            'affected_declared_consumers': sorted({e['from'] for e in exact if e['target'] == key}),
                            'mathematical_invalidation_inferred': False})
    source_readback = inputs['SOURCE_IDENTITY_READBACK.json']['files']
    assert sum(x['kind'] == 'lesson' for x in source_readback) == len(units)
    for key, u in units.items():
        assert any(x['native_id'] == key and x['kind'] == 'lesson' and x['sha256'] == u['source_sha256'].lower() for x in source_readback)
    rights = recipe['course_license_provenance']
    for r in rights:
        assert r['course_id'] in selected
        for uid in r.get('unit_ids', []):
            assert r['course_id'] + '/' + uid in units, 'licence descriptor refers to absent unit'
    return {
        'schema': 'open-courses-phone-dependency-overlay/1',
        'state': 'validated_metadata_integration_not_proof_admission',
        'counts': {'core_courses': len(core), 'public_advanced_courses': len(published),
                   'public_advanced_lessons': sum(len(c['lessons']) for c in public['courses']),
                   'phone_selected_courses': len(selected), 'phone_selected_lessons': len(units),
                   'cross_programme_preparation_edges': len(preparation), 'native_reading_edges': len(exact),
                   'reported_providers': len(proofs), 'local_producer_comparisons': len(comparisons),
                   'owner_admitted_core_proof_matches': 0, 'source_identity_readbacks': len(source_readback)},
        'core': [{'id': c['id'], 'title': c['title'], 'routes': c['routes']} for c in core.values()],
        'phone_courses': [{k: v for k, v in c.items() if k != 'units'} for c in current['courses']],
        'native_units': units,
        'rights_binding_descriptors': rights,
        'reference_editions': current.get('reference_editions', []),
        'preparation_edges': preparation,
        'reverse_core_dependencies': {key: sorted({e['from'][9:] for e in preparation if e['to'] == 'core:' + key}) for key in sorted(core)},
        'lesson_reading_edges': exact,
        'reverse_lesson_dependencies': {key: sorted({e['from'] for e in exact if e['target'] == key}) for key in sorted({e['target'] for e in exact})},
        'reported_providers': proofs, 'core_producer_comparisons': comparisons,
        'changes_since_frozen_R36': changes,
        'unresolved_core_ids': unknown,
        'phone_courses_without_public_preparation_map': sorted(set(selected) - set(published)),
        'public_courses_not_in_phone_selection': sorted(set(published) - set(selected)),
        'boundaries': {
            'local_phone_selection_not_claimed_published': True,
            'no_source_rights_or_language_relabelling': True,
            'no_owner_mutation_or_transfer': True,
            'course_preparation_is_not_proof_use': True,
            'source_hash_change_requires_reconciliation_not_automatic_invalidation': True,
            'missing_implicit_dependencies_not_claimed_absent': True,
            'existing_public_bridge_not_overwritten': True,
            'phone_exchange_schema': 'stacks-foundation-proof-exchange/v1',
        },
        'unfinished': [
            'Publish the complete B40 foundation proof reader/source route; its existing local provider packet is not public reading access.',
            'Phone retains authority to select provider text and bind consumer-local comparison evidence; no admission is manufactured here.',
            'Resolve unmatched course identities from owner-declared aliases, not title similarity; map remaining actual proof requirements with exact statements and conditions.',
            'Reconcile future source deltas only for their actual known consumers; the preparation graph is not a complete proof graph.',
        ],
    }


def impact(overlay, native_id, proposed_sha256=None):
    if native_id.startswith('core:'):
        key = native_id[5:]
        assert key in overlay['reverse_core_dependencies']
        return {'id': native_id, 'preparation_consumers': overlay['reverse_core_dependencies'][key],
                'exact_use_records': [r for r in overlay['core_producer_comparisons'] if r['core_id'] == key],
                'mathematical_invalidation_inferred': False}
    assert native_id in overlay['native_units'], 'unknown native unit ID'
    old_hash = overlay['native_units'][native_id]['source_sha256'].lower()
    if proposed_sha256 is not None:
        assert HEX.fullmatch(proposed_sha256), 'invalid proposed SHA-256'
    changed = proposed_sha256 is not None and proposed_sha256.lower() != old_hash
    return {'id': native_id, 'bound_sha256': old_hash, 'changed': changed,
            'direct_reading_consumers': overlay['reverse_lesson_dependencies'].get(native_id, []),
            'action': 'reconcile_actual_statement_proof_and_consumer_uses' if changed else 'no_source_change_recheck_requested',
            'mathematical_invalidation_inferred': False}


def tests(inputs, overlay):
    count = 0
    for core in overlay['core']:
        q = impact(overlay, 'core:' + core['id'])
        assert q['preparation_consumers'] == sorted({e['from'][9:] for e in overlay['preparation_edges'] if e['to'] == 'core:' + core['id']})
        count += 1
    for edge in overlay['lesson_reading_edges']:
        assert edge['from'] in impact(overlay, edge['target'])['direct_reading_consumers']
        assert not impact(overlay, edge['target'], edge['target_source_sha256'])['changed']
        changed = impact(overlay, edge['target'], '0' * 64)
        assert changed['changed'] and not changed['mathematical_invalidation_inferred']
        count += 3
    assert overlay['native_units'] == unit_map(inputs['phone-catalog.json'])
    assert overlay['rights_binding_descriptors'] == inputs['phone-recipe.json']['course_license_provenance']
    assert all(not r['owner_admitted'] for r in overlay['core_producer_comparisons'])
    assert all(r['public_reader'] is None for r in overlay['core_producer_comparisons'])
    negative = []
    def rejects(label, fn):
        try:
            fn()
        except (AssertionError, KeyError):
            negative.append(label)
            return
        raise AssertionError('negative case accepted: ' + label)
    for field in ['from_source_sha256', 'target_source_sha256']:
        bad = copy.deepcopy(inputs)
        bad['phone-catalog.json']['dependency_locators'][0][field] = '0' * 64
        rejects(field, lambda: build(bad))
    bad = copy.deepcopy(inputs)
    bad['phone-catalog.json']['courses'][0]['units'].append(copy.deepcopy(bad['phone-catalog.json']['courses'][0]['units'][0]))
    rejects('duplicate_native_unit', lambda: build(bad))
    bad = copy.deepcopy(inputs)
    bad['B40-PROVIDER_HANDOFF.json']['states']['phone_comparison_admitted'] = True
    rejects('invented_owner_admission', lambda: build(bad))
    rejects('source_path_escape', lambda: relative(OUT, '../foreign'))
    rejects('unknown_unit', lambda: impact(overlay, 'invented/unit'))
    rejects('invalid_source_hash', lambda: impact(overlay, next(iter(overlay['native_units'])), 'bad'))
    bad = copy.deepcopy(inputs)
    consumer = bad['B40-PROVIDER_HANDOFF.json']['consumers'][0]
    consumer['source']['sha256'] = '0' * 64
    mismatch = build(bad)['core_producer_comparisons'][0]
    assert mismatch['comparison'] is None and mismatch['state'] == 'source_changed_reconciliation_required'
    return {'state': 'PASS', 'positive_assertions': count + 6, 'negative_cases': negative,
            'native_unit_records_preserved': len(overlay['native_units']),
            'mathematical_proof_validation_claimed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--impact')
    parser.add_argument('--new-sha256')
    args = parser.parse_args()
    if args.capture:
        capture()
    manifest, inputs = load()
    overlay = build(inputs)
    if args.impact:
        print(json.dumps(impact(overlay, args.impact, args.new_sha256), ensure_ascii=False))
        return
    result = tests(inputs, overlay)
    products = {'DEPENDENCY_OVERLAY.json': dump(overlay), 'VALIDATION.json': dump(result)}
    for name, data in products.items():
        if args.check:
            assert (OUT / name).read_bytes() == data, 'deterministic replay differs: ' + name
        else:
            frozen_write(OUT / name, data)
    print(json.dumps({'counts': overlay['counts'], 'validation': result,
                      'unmapped_phone_courses': overlay['phone_courses_without_public_preparation_map'],
                      'outputs': [fact(k, v) for k, v in products.items()]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
