"""Independent all-role claim accounting, HTML-link checks and mutation tests."""
import copy
import hashlib
import json
import re
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = 'scripts/build-program-backend-coverage-v1.mjs'
INPUTS = {
    'capsules': 'backend/course-capsule-v1/generated/course-capsules.json',
    'families': 'backend/course-capsule-v1/authority/clp-family-v231/modular-backend-pattern-index-v2.1.json',
    'published': 'backend/course-capsule-v1/authority/clp-family-v231/v23-adapter-index-v2.json',
    'clpRoutes': 'backend/course-capsule-v1/authority/clp-family-v231/learner-reader-actions-v1.json',
    'clpView': 'docs/backend/clp/validation.json',
    'a20': 'backend/course-capsule-v1/adapters/a20-capability-v1/publication/GITHUB_READBACK_a2729467c523.json',
    'a30Manifest': 'backend/course-capsule-v1/adapters/a30-capability-v1/manifest.json',
    'a30Validation': 'backend/course-capsule-v1/adapters/a30-capability-v1/validation.json',
    'a30Public': 'backend/course-capsule-v1/adapters/a30-capability-v1/data/public-evidence.json',
    'a30NativeReadback': 'backend/course-capsule-v1/adapters/a30-capability-v1/input/public-native-readback.json',
    'a30Integration': 'backend/course-capsule-v1/adapters/a30-capability-v1/publication/GITHUB_READBACK_74b208108a25.json',
    'b40': 'backend/course-capsule-v1/adapters/b40-capability-v1/publication/GITHUB_READBACK_35b2e2bd34d0.json',
    'b80': 'backend/course-capsule-v1/adapters/b80-capability-v1/publication/GITHUB_SOURCE_AND_PAGES_READBACK_20260904.json',
    'lebl': 'backend/course-capsule-v1/adapters/lebl-capability-v1/publication/GITHUB_READBACK_97960cc12b34.json',
    'geometry': 'backend/course-capsule-v1/adapters/geometry-capability-v1/publication/GITHUB_READBACK_a2584b9448c9.json',
    'topology': 'backend/course-capsule-v1/adapters/topology-capability-v1/publication/GITHUB_READBACK_d7141489fe34.json',
    'c70': 'backend/course-capsule-v1/adapters/c70-capability-v1/publication/GITHUB_READBACK_4eb34c5d866a.json',
    'c110': 'backend/course-capsule-v1/adapters/c110-capability-v1/publication/GITHUB_READBACK_c7ccbcc9a27a.json',
    'c120': 'backend/course-capsule-v1/adapters/c120-capability-v1/publication/GITHUB_READBACK_5cef326a811b.json',
    'c60': 'backend/course-capsule-v1/adapters/c60-capability-v1/publication/GITHUB_READBACK_306c9e080f89.json',
    'b90': 'backend/course-capsule-v1/adapters/b90-capability-v1/publication/GITHUB_READBACK_37dfd587bac2.json',
    'd10': 'backend/course-capsule-v1/adapters/d10-capability-v1/publication/GITHUB_READBACK_a290054a4e16.json',
    'd30Manifest': 'backend/course-capsule-v1/adapters/d30-capability-v1/manifest.json',
    'd30Validation': 'backend/course-capsule-v1/adapters/d30-capability-v1/validation.json',
    'd30Public': 'backend/course-capsule-v1/adapters/d30-capability-v1/data/public-evidence.json',
    'd40': 'backend/course-capsule-v1/adapters/d40-capability-v1/publication/GITHUB_READBACK_4f7d6c825751.json',
    'd70': 'backend/course-capsule-v1/adapters/d70-capability-v1/publication/GITHUB_READBACK_2ce9fbb5dacd.json',
    'd80': 'backend/course-capsule-v1/adapters/d80-capability-v1/publication/GITHUB_READBACK_b22cd627901c.json',
    'd90': 'backend/course-capsule-v1/adapters/d90-capability-v1/publication/GITHUB_READBACK_1ec3ed4846c8.json',
    'd100': 'backend/course-capsule-v1/adapters/d100-capability-v1/publication/GITHUB_READBACK_9b9480ff5b2c.json',
    'd120': 'backend/course-capsule-v1/adapters/d120-capability-v1/publication/GITHUB_READBACK_a42650f4815a.json',
    'd50Publication': 'backend/v2.3/admissions/d50-smooth-manifolds-v0.1.0/publication/PUBLICATION_BINDING_v0.63.21.json',
}
OUTPUTS = ['backend/course-capsule-v1/generated/program-backend-coverage-v1.json',
           'docs/backend/program-backend-coverage.json', 'docs/backend/coverage.html']
inputs = {key: json.loads((ROOT / path).read_bytes()) for key, path in INPUTS.items()}
model = json.loads((ROOT / OUTPUTS[0]).read_bytes())
assert (ROOT / OUTPUTS[0]).read_bytes() == (ROOT / OUTPUTS[1]).read_bytes()
roles = {row['role_id']: row for row in model['roles']}
assert len(model['roles']) == len(roles) == 40
assert set(roles) == {row['course_id'] for row in inputs['capsules']}
assert model['summary']['overall_program_backend_complete'] is False
assert model['summary']['locally_validated_adapter_roles'] == sum(
    row['layers']['interoperability']['semantic_adapter']['status'] in ('verified', 'legacy_verified')
    for row in inputs['capsules'])
assert model['summary']['roles_without_validated_common_adapter'] + model['summary']['locally_validated_adapter_roles'] == 40
assert model['summary']['zenodo_evidenced_roles'] == len(inputs['published']['adapters']) + 1
assert model['summary']['locally_validated_adapter_roles'] == 38
assert model['summary']['roles_without_validated_common_adapter'] == 2
assert model['summary']['locally_represented_families'] == 31
assert model['summary']['github_evidenced_roles'] == 37
assert {
    role for role, row in roles.items()
    if row['common_adapter']['status'] not in ('verified', 'legacy_verified')
} == {'B95', 'C140'}
assert roles['B80']['common_adapter']['zenodo_preservation'] == 'assigned_to_central_manager_not_yet_verified'
assert roles['A10']['common_adapter']['status'] == 'verified'
assert roles['A10']['common_adapter']['contract'] == '2.3.1'
assert roles['A10']['common_adapter']['mapping_scope'] == 'capsule_only'
assert roles['A10']['common_adapter']['github_public_evidence'] == 'not_established'
assert roles['A10']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['A10']['common_adapter']['public_package'] is None
assert [row['kind'] for row in roles['A10']['common_adapter']['local_evidence']] == [
    'central_adapter_manifest',
    'package_seal',
    'deterministic_generic_validation_receipt',
    'a10_semantic_validation_receipt',
    'public_release_authority',
]
assert roles['A10']['learner']['relationship'] == 'no_common_adapter_consumption_proven'
assert roles['A10']['learner']['tools'] == []
assert roles['A10']['dimensions']['curriculum']['unit_identity'] == 'unknown'
assert roles['A10']['dimensions']['source_translation_ledger'] == {
    'corrections': 'in_progress',
    'ledger': 'unknown',
}
assert roles['A10']['dimensions']['terminology']['register'] == 'in_progress'
assert roles['A10']['dimensions']['reproducible_production'] == {
    'build': 'unknown',
    'replay': 'unknown',
}
assert roles['A10']['dimensions']['educator']['unit_alignment'] == 'unknown'
assert roles['A20']['common_adapter']['status'] == 'verified'
assert roles['A20']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['A20']['common_adapter']['mapping_scope'] == (
    'zero_copy_projection_of_174535_native_records_83_modules_8209_exercise_'
    'problem_identities_5238_solution_identities_236_concepts_340_terms_1614_'
    'corrections_and_17_component_rights_with_2971_unsolved_exercises_preserved'
)
assert roles['A20']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['A20']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['A20']['common_adapter']['public_package'] is None
assert [row['kind'] for row in roles['A20']['common_adapter']['local_evidence']] == [
    'central_adapter_manifest',
    'deterministic_validation_receipt',
    'native_source_lock',
    'anonymous_native_public_readback',
    'verified_native_public_release',
    'native_record_ledger',
    'module_identity_index',
    'exercise_solution_identity_index',
    'concept_index',
    'pedagogical_relation_index',
    'component_rights_index',
    'correction_index',
    'terminology_index',
]
assert roles['A20']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert roles['A20']['learner']['tools'] == [{
    'href': '../backend/a20/A20.html',
    'label': 'A20 · Aljabar Menengah',
}]
assert roles['A20']['educator']['unit_alignment'] == 'verified'
assert len(roles['A20']['educator']['resources']) == 10
assert roles['A20']['dimensions']['source_translation_ledger'] == {
    'corrections': 'verified',
    'ledger': 'verified',
}
assert roles['A20']['dimensions']['terminology']['register'] == 'verified'
assert roles['A20']['dimensions']['reproducible_production'] == {
    'build': 'verified',
    'replay': 'verified',
}
assert roles['A20']['dimensions']['accessibility'] == {
    'mathml': 'not_yet_produced',
    'semantic_html': 'not_yet_produced',
}
assert roles['A30']['common_adapter']['status'] == 'verified'
assert roles['A30']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['A30']['common_adapter']['mapping_scope'] == (
    'zero_copy_projection_of_220680_native_records_87_modules_7250_'
    'exercise_problem_identities_4183_solution_identities_497_concepts_'
    '513_terms_703_corrections_1875_component_rights_and_segment_state_'
    'asymmetry_with_3067_unsupported_solution_cases_preserved'
)
assert roles['A30']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['A30']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['A30']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert roles['A30']['learner']['tools'] == [{
    'href': '../backend/a30/A30.html',
    'label': 'A30 · Prakalkulus dan Trigonometri',
}]
assert roles['A30']['educator']['unit_alignment'] == 'verified'
assert len(roles['A30']['educator']['resources']) == 12
assert roles['A30']['dimensions']['source_translation_ledger'] == {
    'corrections': 'verified',
    'ledger': 'verified',
}
assert roles['A30']['dimensions']['terminology']['register'] == 'verified'
assert roles['A30']['dimensions']['reproducible_production'] == {
    'build': 'verified',
    'replay': 'verified',
}
assert roles['A30']['dimensions']['accessibility'] == {
    'mathml': 'not_yet_produced',
    'semantic_html': 'not_yet_produced',
}
for key, schema in (
    ('a30Manifest', 'a30-capability-manifest/1'),
    ('a30Validation', 'a30-capability-validation/1'),
    ('a30Public', 'a30-public-evidence/1'),
    ('a30NativeReadback', 'a30-native-public-readback/1'),
    ('a30Integration', 'a30-integration-public-readback/1'),
):
    assert inputs[key]['schema'] == schema
for key in ('a30Manifest', 'a30Validation', 'a30Public', 'a30NativeReadback'):
    payload = (ROOT / INPUTS[key]).read_bytes()
    assert any(row['path'] == INPUTS[key] and row['bytes'] == len(payload)
               and row['sha256'] == hashlib.sha256(payload).hexdigest()
               for row in model['evidence'])
assert inputs['a30Validation']['result'] == 'pass'
assert inputs['a30NativeReadback']['anonymous'] is True
assert inputs['a30NativeReadback']['credentials_used'] is False
assert inputs['a30Integration']['state'] == 'pass'
assert inputs['a30Integration']['source_commit'] == '74b208108a258916eb160ac5b8d3b72f2844809b'
assert inputs['a30Integration']['base_commit'] == '1edaf095c63b79b1f2d83fa6062f13bbdf2e4203'
assert inputs['a30Integration']['anonymous'] is True
assert inputs['a30Integration']['credentials_used'] is False
assert inputs['a30Integration']['expected_files'] == inputs['a30Integration']['verified_files'] == 13
assert inputs['a30Integration']['failures'] == []
assert all(row['http_status'] == 200 for row in inputs['a30Integration']['files'])
assert any(row['surface'] == 'pages' and row['url'].endswith('/backend/a30/A30.html')
           and row['bytes'] == 35638
           and row['sha256'] == '4bbbb2649be4aa7c604c8859563e607090ff3a536eedf83d81d7254ac28843c6'
           for row in inputs['a30Integration']['files'])
assert any(row['surface'] == 'pages' and row['url'].endswith('/backend/a30/A30-pengajar.html')
           and row['bytes'] == 44560
           and row['sha256'] == 'a889b80e460ae44d53054a82128ce1833716fe4d527a07eef82683d3e5b4636c'
           for row in inputs['a30Integration']['files'])
assert any(row['surface'] == 'pages' and row['url'].endswith('/backend/coverage.html')
           and row['bytes'] == 116735
           and row['sha256'] == 'e27dcb29be41a93b5d7bfa176cf2bb08f1a5102c29bc33f391629d103d48e1cf'
           for row in inputs['a30Integration']['files'])
assert inputs['a30Public']['repository']['url'] == 'https://github.com/KokunoYumeto/openstax-precalculus-2e-id'
assert inputs['a30Public']['repository']['tag'] == 'v1.0.0'
assert inputs['a30Public']['zenodo']['access_right'] == 'open'
assert len(inputs['a30Public']['github_release']['assets']) == 7
assert len(inputs['a30Public']['zenodo']['assets']) == 7
assert inputs['a30Public']['indonesian_reader']['bytes'] == 305654938
assert inputs['a30Public']['indonesian_reader']['sha256'] == '3cfd5294b91252cc766992f158b6601e80aa31b719b0b8bf69e1ff6d08a4fa3e'
assert roles['B40']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['B40']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['B40']['learner']['tools']) == 1
assert roles['B40']['educator']['unit_alignment'] == 'verified'
assert roles['B40']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['B40']['common_adapter']['zenodo_preservation'] == 'not_established'
clp_route_path = INPUTS['clpRoutes']
clp_route_bytes = (ROOT / clp_route_path).read_bytes()
clp_route_identity = {
    'bytes': len(clp_route_bytes),
    'sha256': hashlib.sha256(clp_route_bytes).hexdigest(),
}
for role in ('B20', 'B30', 'B50', 'B60'):
    assert roles[role]['common_adapter']['contract'] == '2.3.1'
    assert roles[role]['learner']['relationship'] == (
        'central_view_consumes_verified_route_projection_'
        'pdf_runtime_adapter_consumption_not_claimed'
    )
    assert len(roles[role]['learner']['tools']) == 1
    assert roles[role]['learner']['tools'][0]['href'] == '../backend/clp/' + role + '.html'
    assert roles[role]['dimensions']['learner']['central_tools'] == 1
    same_locator = [
        row for row in roles[role]['common_adapter']['local_evidence']
        if row.get('locator') == clp_route_path
    ]
    assert len(same_locator) == 1
    assert {key: same_locator[0][key] for key in ('bytes', 'sha256')} == clp_route_identity
for role in ('B70', 'C10', 'C20', 'C50'):
    assert roles[role]['common_adapter']['contract'] == 'lebl-learning-capability/1'
    assert roles[role]['learner']['relationship'] == 'directly_consumes_adapter_outputs'
    assert len(roles[role]['learner']['tools']) == 3
    assert roles[role]['educator']['unit_alignment'] == 'verified'
    assert roles[role]['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['C100']['common_adapter']['contract'] == 'geometry-learning-capability/1'
assert roles['C100']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['C100']['learner']['tools']) == 2
assert roles['C100']['educator']['unit_alignment'] == 'verified'
assert roles['C100']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['C90']['common_adapter']['contract'] == 'topology-learning-capability/1'
assert roles['C90']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['C90']['learner']['tools']) == 1
assert roles['C90']['educator']['unit_alignment'] == 'verified'
assert roles['C90']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['C70']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['C70']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['C70']['learner']['tools']) == 1
assert roles['C70']['educator']['unit_alignment'] == 'verified'
assert len(roles['C70']['educator']['resources']) == 4
assert roles['C70']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['C70']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['C70']['dimensions']['source_translation_ledger']['ledger'] == 'verified'
assert roles['C70']['dimensions']['terminology']['register'] == 'verified'
assert roles['C70']['dimensions']['reproducible_production']['build'] == 'verified'
assert roles['C70']['dimensions']['reproducible_production']['replay'] == 'verified'
assert roles['C110']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['C110']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['C110']['learner']['tools']) == 1
assert roles['C110']['educator']['unit_alignment'] == 'verified'
assert roles['C110']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['C110']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['C110']['dimensions']['source_translation_ledger']['ledger'] == 'verified'
assert roles['C110']['dimensions']['terminology']['register'] == 'verified'
assert roles['C110']['dimensions']['reproducible_production']['build'] == 'verified'
assert roles['C110']['dimensions']['reproducible_production']['replay'] == 'verified'
assert roles['C120']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['C120']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['C120']['learner']['tools']) == 1
assert roles['C120']['educator']['unit_alignment'] == 'verified'
assert roles['C120']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['C120']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['C120']['dimensions']['source_translation_ledger']['ledger'] == 'verified'
assert roles['C120']['dimensions']['terminology']['register'] == 'verified'
assert roles['C120']['dimensions']['reproducible_production']['build'] == 'verified'
assert roles['C120']['dimensions']['reproducible_production']['replay'] == 'verified'
assert roles['C60']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['C60']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['C60']['learner']['tools']) == 1
assert roles['C60']['educator']['unit_alignment'] == 'verified'
assert len(roles['C60']['educator']['resources']) == 7
assert roles['C60']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['C60']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['C60']['dimensions']['source_translation_ledger']['ledger'] == 'verified'
assert roles['C60']['dimensions']['terminology']['register'] == 'verified'
assert roles['C60']['dimensions']['reproducible_production']['build'] == 'verified'
assert roles['C60']['dimensions']['reproducible_production']['replay'] == 'verified'
assert roles['C60']['dimensions']['accessibility']['semantic_html'] == 'verified'
assert roles['C60']['dimensions']['accessibility']['mathml'] == 'verified'
assert roles['B90']['common_adapter']['status'] == 'verified'
assert roles['B90']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['B90']['common_adapter']['mapping_scope'] == (
    'zero_copy_projection_of_4716_public_native_records_800_units_711_exercises_'
    '91_concepts_119_terms_152_corrections_and_4_component_rights_with_explicit_'
    'answer_supplement_exclusion'
)
assert roles['B90']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['B90']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['B90']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert roles['B90']['learner']['tools'] == [{
    'href': '../backend/b90/B90.html',
    'label': 'B90 · Probabilitas Berbasis Kalkulus',
}]
assert roles['B90']['educator']['unit_alignment'] == 'verified'
assert len(roles['B90']['educator']['resources']) == 8
assert roles['B90']['dimensions']['source_translation_ledger']['ledger'] == 'verified'
assert roles['B90']['dimensions']['source_translation_ledger']['corrections'] == 'verified'
assert roles['B90']['dimensions']['terminology']['register'] == 'verified'
assert roles['B90']['dimensions']['reproducible_production']['build'] == 'verified'
assert roles['B90']['dimensions']['reproducible_production']['replay'] == 'verified'
assert roles['B90']['dimensions']['accessibility']['semantic_html'] == 'not_yet_produced'
assert roles['B90']['dimensions']['accessibility']['mathml'] == 'not_yet_produced'
assert roles['D40']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['D40']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['D40']['learner']['tools']) == 1
assert roles['D40']['educator']['unit_alignment'] == 'verified'
assert roles['D40']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['D40']['common_adapter']['zenodo_preservation'] == 'not_established'
for dimension in ('curriculum', 'source_translation_ledger', 'terminology', 'reproducible_production', 'educator', 'interoperability'):
    assert 'unknown' not in roles['D40']['dimensions'][dimension].values()
assert roles['D50']['common_adapter']['status'] == 'verified'
assert roles['D50']['common_adapter']['contract'] == '2.3.1'
assert roles['D50']['common_adapter']['mapping_scope'].startswith('zero_copy_projection_of_6912_owner_native_rows')
assert roles['D50']['common_adapter']['github_public_evidence'] == 'new_anonymous_release_asset_readback'
assert roles['D50']['common_adapter']['zenodo_preservation'] == 'new_embedded_successor_readback'
assert roles['D50']['common_adapter']['public_package'] == {
    'url': inputs['d50Publication']['github']['asset_url'],
    'bytes': 15385668,
    'sha256': 'dedcc369a482295677ee2763690b92c08fddec85cb40fe89f4542b833138052d',
    'central_record': 'https://doi.org/10.5281/zenodo.22542577',
    'zenodo_container': 'peta-belajar-multilingual-v0.63.21.zip',
    'zenodo_member': 'backend/v2.3/packages/program-matematika-indonesia-backend-v2.3.1-d50-smooth-manifolds-adapter-v0.1.0.zip',
}
assert [row['kind'] for row in roles['D50']['common_adapter']['local_evidence']] == [
    'central_adapter_manifest',
    'central_admission_validation',
    'sealed_zero_copy_adapter_package',
    'fail_closed_negative_probe_report',
    'independent_package_audit',
    'central_publication_binding',
]
assert roles['D50']['learner']['relationship'] == 'no_common_adapter_consumption_proven'
assert roles['D50']['learner']['tools'] == []
assert roles['D50']['dimensions']['curriculum']['unit_identity'] == 'verified'
assert roles['D50']['dimensions']['source_translation_ledger'] == {
    'corrections': 'verified',
    'ledger': 'verified',
}
assert roles['D50']['dimensions']['terminology']['register'] == 'verified'
assert roles['D50']['dimensions']['reproducible_production'] == {
    'build': 'unknown',
    'replay': 'unknown',
}
assert roles['D50']['dimensions']['educator']['unit_alignment'] == 'unknown'
assert roles['D70']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['D70']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['D70']['learner']['tools']) == 1
assert roles['D70']['educator']['unit_alignment'] == 'verified'
assert roles['D70']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['D70']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['D70']['dimensions']['reproducible_production']['replay'] == 'available_unverified'
assert roles['D80']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['D80']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['D80']['learner']['tools']) == 1
assert roles['D80']['educator']['unit_alignment'] == 'verified'
assert roles['D80']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['D80']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['D90']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['D90']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['D90']['learner']['tools']) == 1
assert roles['D90']['educator']['unit_alignment'] == 'verified'
assert roles['D90']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['D90']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['D90']['dimensions']['source_translation_ledger']['ledger'] == 'verified'
assert roles['D90']['dimensions']['terminology']['register'] == 'verified'
assert roles['D90']['dimensions']['reproducible_production']['build'] == 'verified'
assert roles['D90']['dimensions']['reproducible_production']['replay'] == 'verified'
assert roles['D90']['dimensions']['accessibility']['semantic_html'] == 'verified'
assert roles['D90']['dimensions']['accessibility']['mathml'] == 'verified'
assert roles['D10']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['D10']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['D10']['learner']['tools']) == 1
assert roles['D10']['educator']['unit_alignment'] == 'verified'
assert roles['D10']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['D10']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['D10']['dimensions']['source_translation_ledger']['ledger'] == 'verified'
assert roles['D10']['dimensions']['terminology']['register'] == 'verified'
assert roles['D10']['dimensions']['reproducible_production']['build'] == 'verified'
assert roles['D10']['dimensions']['reproducible_production']['replay'] == 'verified'
d30 = roles['D30']
d30_capsule = next(row for row in inputs['capsules'] if row['course_id'] == 'D30')
assert d30['common_adapter']['status'] == 'verified'
assert d30['common_adapter']['contract'] == 'course-learning-capability/1'
assert d30['common_adapter']['mapping_scope'] == (
    'zero_copy_projection_of_2538_entities_6333_segments_3256_relations_'
    '57_high_level_surfaces_5_labs_36_solved_mastery_problems_and_2_equivalent_assessments'
)
assert d30['common_adapter']['github_public_evidence'] == 'native_anonymous_source_and_pages_readback'
assert d30['common_adapter']['zenodo_preservation'] == 'not_established'
assert d30['common_adapter']['public_package'] is None
assert d30['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(d30['learner']['tools']) == 1
assert d30['learner']['tools'][0]['href'] == '../backend/d30/D30.html'
assert d30['educator']['unit_alignment'] == 'verified'
assert {'D30:native-educator-observation', 'D30:educator-hub-v1'} <= {
    row['id'] for row in d30['educator']['resources']
}
assert d30['dimensions']['source_translation_ledger'] == {
    'corrections': 'verified',
    'ledger': 'verified',
}
assert d30['dimensions']['terminology']['register'] == 'verified'
assert d30['dimensions']['reproducible_production'] == {
    'build': 'verified',
    'replay': 'verified',
}
assert d30['dimensions']['accessibility'] == {
    'mathml': 'available_unverified',
    'semantic_html': 'verified',
}
for kind, key in (
    ('central_adapter_manifest', 'd30Manifest'),
    ('deterministic_validation_receipt', 'd30Validation'),
    ('verified_native_public_release', 'd30Public'),
):
    path = INPUTS[key]
    payload = (ROOT / path).read_bytes()
    found = [row for row in d30['common_adapter']['local_evidence']
             if row['kind'] == kind and row['locator'] == path]
    assert len(found) == 1
    assert found[0]['bytes'] == len(payload)
    assert found[0]['sha256'] == hashlib.sha256(payload).hexdigest()
public = inputs['d30Public']
assert public['content_commit'] == inputs['d30Manifest']['native_release']['commit']
assert public['content_tree'] == inputs['d30Manifest']['native_release']['tree']
assert d30_capsule['course_native']['repository'] == public['repository']
assert d30_capsule['course_native']['zenodo'] == 'https://doi.org/' + public['doi']
assert d30_capsule['layers']['production']['repository'] == public['repository']
assert d30_capsule['layers']['production']['zenodo'] == 'https://doi.org/' + public['doi']
assert d30_capsule['layers']['production']['release_status'] == 'verified'
assert d30_capsule['layers']['learner']['online_html']['url'] == public['reader']
assert d30_capsule['layers']['learner']['primary']['url'] == public['reader']
public_files = {row['filename']: row for row in public['files']}
for layer, filename in (
    ('pdf', '00_PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_READER_CHECKPOINT_38.pdf'),
    ('portable_html', 'PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_READER_CHECKPOINT_38.zip'),
):
    assert d30_capsule['layers']['learner'][layer]['bytes'] == public_files[filename]['bytes']
    assert d30_capsule['layers']['learner'][layer]['sha256'] == public_files[filename]['sha256']
assert roles['D100']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['D100']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['D100']['learner']['tools']) == 1
assert roles['D100']['educator']['unit_alignment'] == 'verified'
assert roles['D100']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['D100']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['D120']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['D120']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['D120']['learner']['tools']) == 1
assert roles['D120']['educator']['unit_alignment'] == 'verified'
assert roles['D120']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['D120']['common_adapter']['zenodo_preservation'] == 'not_established'
assert roles['D120']['dimensions']['source_translation_ledger']['ledger'] == 'not_applicable'
assert roles['D120']['dimensions']['reproducible_production']['build'] == 'verified'
assert roles['D120']['dimensions']['reproducible_production']['replay'] == 'verified'
dimensions = {'curriculum', 'source_translation_ledger', 'terminology', 'reproducible_production',
              'accessibility', 'learner', 'educator', 'federation', 'interoperability'}
for row in inputs['capsules']:
    projected = roles[row['course_id']]
    assert set(projected['dimensions']) == dimensions
    assert projected['whole_course_backend_completion'] == 'not_yet_proven'
    assert len(projected['next_required_work']) > 0
    assert projected['dimensions']['terminology']['register'] == row['layers']['translation']['terminology_status']
    assert projected['dimensions']['reproducible_production']['replay'] == row['layers']['production']['deterministic_replay_status']
    assert projected['native_design_audit']['status'] == 'historical_comparison_not_new_native_reaudit'
for fact in model['evidence']:
    data = (ROOT / fact['path']).read_bytes()
    assert len(data) == fact['bytes'] and hashlib.sha256(data).hexdigest() == fact['sha256']


class Page(HTMLParser):
    def __init__(self, data):
        super().__init__()
        self.ids, self.links, self.language, self.row_ids = [], [], None, []
        self.feed(data)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'html':
            self.language = values.get('lang')
        if 'id' in values:
            self.ids.append(values['id'])
            if tag == 'tr':
                self.row_ids.append(values['id'])
        if tag == 'a':
            self.links.append(values.get('href'))


html_path = ROOT / 'docs/backend/coverage.html'
html = html_path.read_text(encoding='utf-8')
page = Page(html)
assert page.language == 'id'
assert len(page.ids) == len(set(page.ids))
assert set(page.row_ids) == {'role-' + role for role in roles}
assert html.count('Sembilan bidang kemampuan') == 40
assert 'bukan' in html and 'persentase penerjemahan' in html
local_links = 0
for href in page.links:
    assert href and href not in ('undefined', 'null')
    parsed = urlsplit(href)
    assert parsed.scheme in ('', 'https'), href
    if parsed.scheme:
        continue
    target = (html_path.parent / unquote(parsed.path)).resolve()
    if target.is_dir():
        target = target / 'index.html'
    assert target.is_relative_to(ROOT / 'docs') and target.is_file(), href
    if parsed.fragment:
        assert unquote(parsed.fragment) in Page(target.read_text(encoding='utf-8')).ids, href
    local_links += 1


_TOP_OVERLAY = re.compile(
    r'\n<nav data-central-surface-navigation="v1" data-placement="top"'
    r' aria-label="[^"]+">.*?</nav>', re.DOTALL
)
_BOTTOM_OVERLAY = re.compile(
    r'<nav data-central-surface-navigation="v1" data-placement="bottom"'
    r' aria-label="[^"]+">.*?</nav>\n', re.DOTALL
)


def coverage_without_surface_overlay(payload: bytes) -> bytes:
    """The builder emits the base page; the production pipeline then adds a reversible overlay."""
    text = payload.decode('utf-8')
    text = _TOP_OVERLAY.sub('', text)
    text = _BOTTOM_OVERLAY.sub('', text)
    return text.encode('utf-8')

mutations = []
with tempfile.TemporaryDirectory(prefix='backend-coverage-test-') as temporary:
    sandbox = Path(temporary)
    for path in [GENERATOR, 'scripts/native-catalog-exchange-v1.mjs'] + list(INPUTS.values()):
        target = sandbox / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / path).read_bytes())

    def run():
        return subprocess.run(['node', GENERATOR], cwd=sandbox, capture_output=True, text=True)

    for _ in range(2):
        process = run()
        assert process.returncode == 0, process.stderr
        for path in OUTPUTS:
            candidate = (sandbox / path).read_bytes()
            actual = (ROOT / path).read_bytes()
            if path == 'docs/backend/coverage.html':
                actual = coverage_without_surface_overlay(actual)
            assert candidate == actual, path

    cases = [
        ('duplicate_role', 'capsules', lambda value: value.__setitem__(1, copy.deepcopy(value[0]))),
        ('missing_role', 'capsules', lambda value: value.pop()),
        ('duplicate_family_role', 'families', lambda value: value['families'][1]['roles'].append('A00')),
        ('missing_public_packet', 'published', lambda value: value['packages'].clear()),
        ('clp_route_count', 'clpRoutes', lambda value: value['summary'].update(action_count=6)),
        ('clp_view_not_pass', 'clpView', lambda value: value.update(state='fail')),
        ('unverified_public_packet', 'published', lambda value: value['packages'][0].update(admission_state='draft')),
        ('a20_nonanonymous', 'a20', lambda value: value.update(anonymous=False)),
        ('a20_missing_teacher_readback', 'a20', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/a20/A20-pengajar.html'])),
        ('a30_manifest_contract', 'a30Manifest', lambda value: value.update(contract='wrong-contract/0')),
        ('a30_validation_not_pass', 'a30Validation', lambda value: value.update(result='FAIL')),
        ('a30_native_nonanonymous', 'a30NativeReadback', lambda value: value.update(anonymous=False)),
        ('a30_public_asset_omission', 'a30Public', lambda value: value['github_release']['assets'].pop()),
        ('b40_nonanonymous', 'b40', lambda value: value.update(anonymous=False)),
        ('b40_missing_teacher_readback', 'b40', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/b40/B40-pengajar.html'])),
        ('b80_nonanonymous', 'b80', lambda value: value.update(anonymous=False)),
        ('b80_missing_teacher_readback', 'b80', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/b80/B80-pengajar.html'])),
        ('lebl_nonanonymous', 'lebl', lambda value: value.update(anonymous=False)),
        ('lebl_missing_teacher_readback', 'lebl', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/lebl/C20-pengajar.html'])),
        ('geometry_nonanonymous', 'geometry', lambda value: value.update(anonymous=False)),
        ('geometry_missing_teacher_readback', 'geometry', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/geometry/pengajar.html'])),
        ('topology_nonanonymous', 'topology', lambda value: value.update(anonymous=False)),
        ('topology_missing_teacher_readback', 'topology', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/topology/pengajar.html'])),
        ('c70_nonanonymous', 'c70', lambda value: value.update(anonymous=False)),
        ('c70_missing_teacher_readback', 'c70', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/c70/C70-pengajar.html'])),
        ('c110_nonanonymous', 'c110', lambda value: value.update(anonymous=False)),
        ('c110_missing_teacher_readback', 'c110', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/c110/C110-pengajar.html'])),
        ('c120_nonanonymous', 'c120', lambda value: value.update(anonymous=False)),
        ('c120_missing_teacher_readback', 'c120', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/c120/C120-pengajar.html'])),
        ('c60_nonanonymous', 'c60', lambda value: value.update(anonymous=False)),
        ('c60_missing_teacher_readback', 'c60', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/c60/C60-pengajar.html'])),
        ('b90_nonanonymous', 'b90', lambda value: value.update(anonymous=False)),
        ('b90_missing_teacher_readback', 'b90', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/b90/B90-pengajar.html'])),
        ('d40_nonanonymous', 'd40', lambda value: value.update(anonymous=False)),
        ('d40_missing_teacher_readback', 'd40', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/d40/D40-pengajar.html'])),
        ('d70_nonanonymous', 'd70', lambda value: value.update(anonymous=False)),
        ('d70_missing_teacher_readback', 'd70', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/d70/D70-pengajar.html'])),
        ('d80_nonanonymous', 'd80', lambda value: value.update(anonymous=False)),
        ('d80_missing_teacher_readback', 'd80', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/d80/D80-pengajar.html'])),
        ('d90_nonanonymous', 'd90', lambda value: value.update(anonymous=False)),
        ('d90_missing_teacher_readback', 'd90', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/d90/D90-pengajar.html'])),
        ('d10_nonanonymous', 'd10', lambda value: value.update(anonymous=False)),
        ('d10_missing_teacher_readback', 'd10', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/d10/D10-pengajar.html'])),
        ('d30_manifest_contract', 'd30Manifest', lambda value: value.update(contract='wrong-contract/0')),
        ('d30_validation_not_pass', 'd30Validation', lambda value: value.update(result='FAIL')),
        ('d30_public_file_omission', 'd30Public', lambda value: value['files'].pop()),
        ('d100_nonanonymous', 'd100', lambda value: value.update(anonymous=False)),
        ('d100_missing_teacher_readback', 'd100', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/d100/D100-pengajar.html'])),
        ('d120_nonanonymous', 'd120', lambda value: value.update(anonymous=False)),
        ('d120_missing_teacher_readback', 'd120', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/d120/D120-pengajar.html'])),
        ('d50_publication_access_downgrade', 'd50Publication', lambda value: value['zenodo'].update(access='restricted')),
        ('d50_publication_asset_hash_change', 'd50Publication', lambda value: value['adapter'].update(sha256='0' * 64)),
        ('d50_publication_authenticated_readback', 'd50Publication', lambda value: value['github'].update(anonymous_asset_readback='authenticated_only')),
    ]
    for name, key, mutate in cases:
        altered = copy.deepcopy(inputs[key])
        mutate(altered)
        path = sandbox / INPUTS[key]
        path.write_text(json.dumps(altered), encoding='utf-8')
        assert run().returncode != 0, 'Accepted invalid coverage inputs: ' + name
        path.write_bytes((ROOT / INPUTS[key]).read_bytes())
        mutations.append(name)

receipt = {'schema': 'program-backend-coverage-validation/1', 'state': 'pass', 'roles': 40,
           'capability_dimensions_per_role': 9, 'exact_input_hashes': True, 'local_links_checked': local_links,
           'isolated_two_build_byte_identity': True, 'rejected_mutations': mutations,
           'translation_progress_inferred': False, 'whole_program_completion_claimed': False}
target = ROOT / 'backend/course-capsule-v1/validation/PROGRAM_BACKEND_COVERAGE_VALIDATION.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(receipt))
