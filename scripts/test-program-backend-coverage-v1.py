"""Independent all-role claim accounting, HTML-link checks and mutation tests."""
import copy
import hashlib
import json
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
    'b80': 'backend/course-capsule-v1/adapters/b80-capability-v1/publication/GITHUB_SOURCE_AND_PAGES_READBACK_20260904.json',
    'lebl': 'backend/course-capsule-v1/adapters/lebl-capability-v1/publication/GITHUB_READBACK_97960cc12b34.json',
    'geometry': 'backend/course-capsule-v1/adapters/geometry-capability-v1/publication/GITHUB_READBACK_a2584b9448c9.json',
    'topology': 'backend/course-capsule-v1/adapters/topology-capability-v1/publication/GITHUB_READBACK_d7141489fe34.json',
    'd80': 'backend/course-capsule-v1/adapters/d80-capability-v1/publication/GITHUB_READBACK_b22cd627901c.json',
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
assert model['summary']['zenodo_evidenced_roles'] == len(inputs['published']['adapters'])
assert roles['B80']['common_adapter']['zenodo_preservation'] == 'assigned_to_central_manager_not_yet_verified'
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
assert roles['D80']['common_adapter']['contract'] == 'course-learning-capability/1'
assert roles['D80']['learner']['relationship'] == 'directly_consumes_adapter_outputs'
assert len(roles['D80']['learner']['tools']) == 1
assert roles['D80']['educator']['unit_alignment'] == 'verified'
assert roles['D80']['common_adapter']['github_public_evidence'] == 'new_anonymous_source_and_pages_readback'
assert roles['D80']['common_adapter']['zenodo_preservation'] == 'not_established'
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
            assert (sandbox / path).read_bytes() == (ROOT / path).read_bytes(), path

    cases = [
        ('duplicate_role', 'capsules', lambda value: value.__setitem__(1, copy.deepcopy(value[0]))),
        ('missing_role', 'capsules', lambda value: value.pop()),
        ('duplicate_family_role', 'families', lambda value: value['families'][1]['roles'].append('A00')),
        ('missing_public_packet', 'published', lambda value: value['packages'].clear()),
        ('unverified_public_packet', 'published', lambda value: value['packages'][0].update(admission_state='draft')),
        ('b80_nonanonymous', 'b80', lambda value: value.update(anonymous=False)),
        ('b80_missing_teacher_readback', 'b80', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/b80/B80-pengajar.html'])),
        ('lebl_nonanonymous', 'lebl', lambda value: value.update(anonymous=False)),
        ('lebl_missing_teacher_readback', 'lebl', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/lebl/C20-pengajar.html'])),
        ('geometry_nonanonymous', 'geometry', lambda value: value.update(anonymous=False)),
        ('geometry_missing_teacher_readback', 'geometry', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/geometry/pengajar.html'])),
        ('topology_nonanonymous', 'topology', lambda value: value.update(anonymous=False)),
        ('topology_missing_teacher_readback', 'topology', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/topology/pengajar.html'])),
        ('d80_nonanonymous', 'd80', lambda value: value.update(anonymous=False)),
        ('d80_missing_teacher_readback', 'd80', lambda value: value.update(files=[row for row in value['files'] if row['path'] != 'docs/backend/d80/D80-pengajar.html'])),
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
