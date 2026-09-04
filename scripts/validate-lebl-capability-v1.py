"""Independent native projection, schema, HTML identity, and deterministic checks."""
import collections
import hashlib
import json
import subprocess
import tempfile
import importlib.util
import shutil
import copy
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from jsonschema import Draft202012Validator, FormatChecker
from lebl_projection_checks_v1 import validate_projection, support_fixture_checks

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/lebl-capability-v1'
PUBLIC = ROOT / 'docs/backend/lebl'
load = lambda path: json.loads(path.read_text(encoding='utf-8'))
digest = lambda data: hashlib.sha256(data).hexdigest()
model = load(PUBLIC / 'learning-map.json')
manifest = load(BASE / 'manifest.json')
spec = importlib.util.spec_from_file_location('lebl_binding', ROOT / 'scripts/bind-lebl-native-evidence-v1.py')
binding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binding)
source_binding = binding.verify()
dataset = load(BASE / 'input/dataset.json')
assert model['native_dataset_id'] == dataset['dataset_id']
assert model['native_records'] == source_binding['source_stream']['records']
assert model['native_commit'] == source_binding['native_commit']
schema = load(ROOT / 'schemas/course-capsule-v1/lebl-learning-capability-v1.schema.json')
Draft202012Validator.check_schema(schema)
Draft202012Validator(schema, format_checker=FormatChecker()).validate(model)
for fact in manifest['inputs'] + manifest['outputs']:
    data = (ROOT / fact['path']).read_bytes()
    assert len(data) == fact['bytes'] and digest(data) == fact['sha256'], fact['path']
input_data = {key: load(BASE / ('input/' + key + '.json')) for key in ('units', 'terms', 'resources', 'editions', 'rights', 'relations')}
validate_projection(input_data, model)
support_mutations = support_fixture_checks()
assert manifest['projection_policy'] == model['projection_policy']
assert collections.Counter(x['support_state'] for x in model['units'] if x['kind'] == 'exercise') == {'unknown': 2169, 'none': 20, 'hint_only': 14}
for key in ('resources', 'editions', 'rights', 'relations'):
    assert model[key] == load(BASE / ('input/' + key + '.json'))
native_terms = {t['id']: t for t in load(BASE / 'input/terms.json')}
for term in model['terms']:
    for key in ('concept_id', 'preferred', 'variants', 'rejected_forms', 'scope_ids', 'evidence', 'rights_id', 'ledger_binding'):
        assert term[key] == native_terms[term['id']][key]

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.entries, self.links, self.lang, self.scripts, self.entry_attrs = [], [], [], None, [], {}
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'html':
            self.lang = attrs.get('lang')
        if tag == 'article':
            self.entries.append(attrs['id'])
            self.entry_attrs[attrs['id']] = attrs
        if tag == 'a':
            self.links.append(attrs['href'])
        if tag == 'script':
            self.scripts.append(attrs.get('src'))

pages = {p.name: Page(p.read_text('utf-8')) for p in PUBLIC.glob('*.html')}
for role, profile in model['roles'].items():
    expected = {u['id'] for u in model['units'] if u['kind'] == 'exercise' and set(u['books']).intersection(profile['books'])}
    for suffix in ('', '-pengajar'):
        page = pages[role + suffix + '.html']
        assert set(page.entries) == expected
        assert page.lang == 'id'
        assert page.scripts == ['filters.js']
    assert pages[role + '.html'].entries == pages[role + '-pengajar.html'].entries
    projected = {unit['id']: unit for unit in model['units']}
    for identifier, attrs in pages[role + '-pengajar.html'].entry_attrs.items():
        unit = projected[identifier]
        assert attrs['data-learner'] == 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/lebl/' + role + '.html#' + identifier
        assert attrs['data-source-local-id'] == unit['source_local_id']
        assert json.loads(attrs['data-source']) == unit['source_components']
        assert json.loads(attrs['data-target']) == unit['target_components']
        assert attrs['data-state'] == unit['support_state']
        assert attrs['data-support-label'] and attrs['data-support-label'] != unit['support_state']
        destination = next(d for d in unit['destinations'] if d['book_id'] in profile['books'])
        assert attrs['data-destination-scope'] == destination['scope']
        assert attrs['data-href'] == destination['href']
assert set(pages['istilah.html'].ids).issuperset(native_terms)
checked_links = 0
for name, page in pages.items():
    assert len(set(page.ids)) == len(page.ids), 'Duplicate HTML IDs: ' + name
    for link in page.links:
        parsed = urlsplit(link)
        if parsed.scheme:
            assert parsed.scheme == 'https', link
            continue
        destination = (PUBLIC / (parsed.path or name)).resolve()
        assert destination.is_relative_to(ROOT / 'docs'), link
        if destination.is_dir():
            destination = destination / 'index.html'
        if destination.name == 'validation.json':
            continue  # This validator creates the output after passing all checks.
        assert destination.is_file(), str(destination)
        if parsed.fragment and destination.parent == PUBLIC:
            assert unquote(parsed.fragment) in pages[destination.name].ids, link
        checked_links += 1

result = subprocess.run(['node', 'scripts/test-lebl-capability-v1.mjs'], cwd=ROOT, text=True, capture_output=True)
assert result.returncode == 0, result.stdout + result.stderr
tests = json.loads(result.stdout)
with tempfile.TemporaryDirectory(prefix='lebl-adapter-replay-') as temporary:
    directory = Path(temporary).resolve()
    assert directory.parent == Path(tempfile.gettempdir()).resolve()
    mutated = directory / 'binding-fixture'
    shutil.copytree(BASE / 'input', mutated / 'input')
    shutil.copyfile(BASE / 'native-evidence-binding.json', mutated / 'native-evidence-binding.json')
    binding_cases = [
        ('dataset_id', 'dataset.json', lambda value: value.update(dataset_id='urn:incorrect')),
        ('stream_count', 'dataset.json', lambda value: value['record_streams'][0].update(record_count=1)),
        ('index_hash', 'native-record-index.jsonl', lambda value: value[0].update(sha256='0' * 64)),
        ('index_line', 'native-record-index.jsonl', lambda value: value[0].update(line=2)),
        ('term_metadata', 'terms.json', lambda value: value[0].update(preferred='incorrect')),
    ]
    for case, filename, mutate in binding_cases:
        original = (mutated / 'input' / filename).read_bytes()
        rows = [json.loads(line) for line in original.splitlines()] if filename.endswith('.jsonl') else json.loads(original)
        mutate(rows)
        changed = b'\n'.join(binding.compact(row) for row in rows) + b'\n' if filename.endswith('.jsonl') else binding.pretty(rows)
        (mutated / 'input' / filename).write_bytes(changed)
        # Even a regenerated ordinary manifest cannot authorize changed intake.
        forged = copy.deepcopy(manifest)
        for fact in forged['inputs']:
            if fact['path'].endswith('/input/' + filename):
                fact.update(bytes=len(changed), sha256=digest(changed))
        (mutated / 'manifest.json').write_bytes(binding.pretty(forged))
        try:
            binding.verify(mutated)
        except AssertionError:
            pass
        else:
            raise AssertionError('Accepted changed source binding: ' + case)
        (mutated / 'input' / filename).write_bytes(original)
    binding.verify(mutated)
    replays = [directory / 'a', directory / 'b']
    for replay in replays:
        run = subprocess.run(['node', 'scripts/build-lebl-capability-v1.mjs', '--output-root=' + str(replay)], cwd=ROOT, text=True, capture_output=True)
        assert run.returncode == 0, run.stdout + run.stderr
    for fact in manifest['outputs'] + [{'path': str((BASE / 'manifest.json').relative_to(ROOT)).replace('\\', '/')}]:
        original = (ROOT / fact['path']).read_bytes()
        assert original == (replays[0] / fact['path']).read_bytes() == (replays[1] / fact['path']).read_bytes(), fact['path']

receipt = {'contract': model['contract'], 'state': 'pass', 'native_commit': model['native_commit'],
    'manifest_sha256': digest((BASE / 'manifest.json').read_bytes()), 'counts': model['counts'],
    'schema_validation': True, 'native_identity_and_selected_values_preserved': True,
    'native_support_state_preserved': True, 'typed_child_evidence_separate_from_solution_completeness': True,
    'learner_teacher_shared_identity': True, 'isolated_two_build_byte_identity': True,
    'checked_local_links': checked_links, 'generated_html_pages': len(pages), **{k:v for k,v in tests.items() if k != 'state'},
    'public_release_verified': False, 'full_native_roundtrip_claimed': False,
    'source_span_replay_claimed': False, 'book_build_replay_claimed': False,
    'visual_layout_reviewed': False, 'independent_support_mutations_rejected': support_mutations,
    'frozen_intake_matches_pinned_native_stream': True,
    'binding_mutations_rejected': [case for case, _, _ in binding_cases],
    'generated_teacher_plan_attributes_checked': True,
    'intake_projection_policy': load(BASE / 'input/native-summary.json')['projection_policy'],
    'capability_projection_policy': model['projection_policy']}
text = json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
for path in (BASE / 'validation.json', PUBLIC / 'validation.json'):
    path.write_text(text, encoding='utf-8', newline='\n')
print(json.dumps(receipt, ensure_ascii=False))
