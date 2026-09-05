import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/d100-capability-v1';
const load = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const identity = async path => {
  const data = await readFile(resolve(root, path));
  return {path, bytes: data.length, sha256: createHash('sha256').update(data).digest('hex')};
};

const manifest = await load(`${base}/manifest.json`);
const validation = await load(`${base}/validation.json`);
const sourceLock = await load(`${base}/input/source-lock.json`);
const capabilities = await load(`${base}/data/capabilities.json`);
const publicEvidence = await load(`${base}/data/public-evidence.json`);
const learningMap = await load(`${base}/data/learning-map.json`);

assert.equal(manifest.schema, 'd100-capability-manifest/1');
assert.equal(manifest.course_id, 'D100');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.contract_2_3_1_conformance, 'not_claimed');
assert.equal(manifest.locale, 'en');
assert.equal(manifest.central_course_truth_locale, 'id-ID');
assert.equal(manifest.native_family, 'algebraic_geometry');
assert.equal(manifest.native_release, 'en-v1.0.0');
assert.equal(manifest.public_release_status, 'unchanged_verified_github_pages_reference_only');
assert.deepEqual(manifest.projection, {
  aggregate_unit_ids_are_adapter_collection_identities: true,
  central_id_id_truth_rewritten: false,
  native_bodies_copied: false,
  native_ids_preserved: true,
  public_state_changed: false,
  strict_source_profile_reversibility_claimed: false,
  zero_copy: true,
});
assert.deepEqual(manifest.counts, {
  companion_exercise_solutions: 13,
  companion_exercises: 13,
  companion_units: 32,
  existing_public_mastery_source_solutions: 13,
  mastery_route_items: 57,
  native_record_rows: 46624,
  native_unit_records: 2154,
  negative_source_solutions: 1041,
  new_editorial_mastery_solutions: 44,
  projected_units: 92,
  source_course_units: 60,
  source_exercises: 1188,
  source_solutions: 147,
});

assert.equal(sourceLock.schema, 'd100-capability-source-lock/1');
assert.equal(sourceLock.course_id, 'D100');
assert.equal(sourceLock.locale, 'en');
assert.equal(sourceLock.native_release, 'en-v1.0.0');
assert.equal(sourceLock.inputs.length, 19);
assert.deepEqual(sourceLock.inputs, manifest.inputs);

assert.equal(validation.schema, 'd100-capability-validation/1');
assert.equal(validation.state, 'pass');
assert.equal(validation.course_id, 'D100');
assert.equal(validation.contract, manifest.contract);
assert.equal(validation.contract_2_3_1_conformance, 'not_claimed');
assert.equal(validation.locale, 'en');
assert.equal(validation.central_course_truth_locale, 'id-ID');
assert.equal(validation.central_id_id_truth_rewritten, false);
assert.equal(validation.input_hashes_verified, 19);
assert.equal(validation.projected_units, 92);
assert.equal(validation.source_exercises, 1188);
assert.equal(validation.source_solutions, 147);
assert.equal(validation.negative_source_solution_states, 1041);
assert.equal(validation.companion_exercises_and_solutions, 13);
assert.equal(validation.mastery_route.items, 57);
assert.equal(validation.mastery_route.new_editorial_solutions, 44);
assert.equal(validation.mastery_route.existing_public_source_solution_references, 13);
assert.equal(validation.native_record_rows_streamed, 46624);
assert.equal(validation.native_bodies_copied, false);
assert.equal(validation.strict_shared_contract_shape, true);
assert.equal(validation.learner_educator_shared_identity, true);
assert.equal(validation.public_state_changed, false);
assert.equal(validation.zenodo_public_readback_claimed, false);
assert.equal(validation.wcag_claimed, false);
assert.equal(validation.native_mathml_claimed, false);
assert.equal(validation.negative_fixtures.length, 14);
assert.ok(validation.negative_fixtures.every(row => row.state === 'rejected'));
assert.deepEqual(validation.isolated_two_build_byte_identity, {
  byte_identical: true,
  file_count: 11,
  tree_sha256: '463de8649239980e67e5cf446a5ca63bac87d1caaac9640cbfd475b541723808',
});

assert.equal(capabilities.schema, 'd100-capability-summary/1');
assert.equal(capabilities.course_id, 'D100');
assert.equal(capabilities.locale, 'en');
assert.equal(capabilities.unit_navigation.source_course_units, 60);
assert.equal(capabilities.unit_navigation.companion_units, 32);
assert.equal(capabilities.unit_navigation.concentrated_route_units, 19);
assert.equal(capabilities.exercise_bank.total_exercises, 1201);
assert.equal(capabilities.solution_coverage.source_solutions, 147);
assert.equal(capabilities.solution_coverage.negative_source_solution_states, 1041);
assert.equal(capabilities.mastery_route.items, 57);
assert.equal(capabilities.terms, 905);
assert.equal(capabilities.rights.records, 149);
assert.equal(capabilities.rights.blanket_license_claimed, false);
assert.equal(capabilities.corrections, 371);
assert.equal(capabilities.deterministic_adapter_replay, true);
assert.equal(capabilities.deterministic_native_translation_qa, true);
assert.equal(capabilities.accessibility.native_mathml, false);
assert.equal(capabilities.accessibility.wcag_conformance_claimed, false);
assert.equal(capabilities.human_review_claimed, false);
assert.deepEqual(capabilities.labs, {count: 0, runtime_environments: 0});

assert.equal(learningMap.contract, manifest.contract);
assert.equal(learningMap.course_id, 'D100');
assert.equal(learningMap.locale, 'en');
assert.equal(learningMap.units.length, 92);
assert.deepEqual(learningMap.labs, []);
assert.deepEqual(learningMap.environments, []);
assert.ok(learningMap.limitations.some(text => /does not rewrite or complete the central id-ID course truth/u.test(text)));
assert.ok(learningMap.limitations.some(text => /1,041 source exercises/u.test(text)));

assert.equal(publicEvidence.schema, 'd100-capability-public-evidence/1');
assert.equal(publicEvidence.course_id, 'D100');
assert.equal(publicEvidence.locale, 'en');
assert.equal(publicEvidence.github.commit, '93dbf3b19907e9e13d42c8e342b449ebd0afc635');
assert.equal(publicEvidence.github.release_tag, 'en-v1.0.0');
assert.equal(publicEvidence.github.anonymous_verification, 'verified');
assert.equal(publicEvidence.github.raw_files, '768/768');
assert.equal(publicEvidence.github.pages_resources, '474/474');
assert.equal(publicEvidence.github.release_assets, '13/13');
assert.equal(publicEvidence.readers.length, 3);
assert.deepEqual(publicEvidence.readers.map(row => row.page_count), [504, 381, 89]);
assert.equal(publicEvidence.readers.reduce((sum, row) => sum + row.page_count, 0), 974);
assert.equal(publicEvidence.release_assets.length, 13);
assert.equal(publicEvidence.zenodo.anonymous_public_readback, false);

for (const item of manifest.outputs) {
  assert.deepEqual(
    await identity(`${base}/${item.path}`),
    {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256},
  );
}

const publicMappings = [
  [`${base}/views/D100.html`, 'docs/backend/d100/D100.html'],
  [`${base}/views/D100-pengajar.html`, 'docs/backend/d100/D100-pengajar.html'],
  [`${base}/data/learning-map.json`, 'docs/backend/d100/learning-map.json'],
  [`${base}/validation.json`, 'docs/backend/d100/validation.json'],
];
for (const [source, target] of publicMappings) {
  const bytes = await readFile(resolve(root, source));
  await mkdir(dirname(resolve(root, target)), {recursive: true});
  await writeFile(resolve(root, target), bytes);
  assert.deepEqual(
    await identity(target),
    {path: target, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')},
  );
}

const evidence = [];
for (const [kind, path] of [
  ['central_adapter_manifest', `${base}/manifest.json`],
  ['deterministic_validation_receipt', `${base}/validation.json`],
  ['native_metadata_intake', `${base}/input/source-lock.json`],
  ['verified_english_public_release', `${base}/data/public-evidence.json`],
]) {
  const {bytes, sha256} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-05'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
assert.ok(
  !overrides.semantic_adapters.D100
    || !overrides.semantic_adapters.D100.contract_version
    || overrides.semantic_adapters.D100.contract_version === manifest.contract,
  'Preserve a different admitted D100 contract',
);
overrides.semantic_adapters.D100 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'english_en_v1_release_zero_copy_projection_of_92_navigation_units_1201_exercises_57_mastery_items_and_native_ledgers_without_rewriting_central_id_id_truth',
  evidence,
};

const oldNative = overrides.native_capabilities.D100 ?? {};
const admittedEvidenceLocators = new Set(evidence.map(row => row.locator));
const legacyTerminologyLocator = 'backend/course-capsule-v1/authority/native-terminology-qa/unib-teori-bilangan-20260831/terminology_concordance.json';
for (const key of ['terminology', 'corrections']) {
  const locators = (oldNative[key]?.evidence ?? []).map(row => row.locator);
  const isCurrentD100Evidence = locators.length === admittedEvidenceLocators.size
    && new Set(locators).size === admittedEvidenceLocators.size
    && locators.every(locator => admittedEvidenceLocators.has(locator));
  assert.ok(
    locators.length === 0
      || locators.every(locator => locator === legacyTerminologyLocator)
      || isCurrentD100Evidence,
    `Preserve unexpected current D100 ${key} evidence`,
  );
}
overrides.native_capabilities.D100 = {};
for (const capability of [
  'unit_identity',
  'translation_ledger',
  'terminology',
  'translation_rights',
  'corrections',
  'educator_unit_alignment',
]) {
  overrides.native_capabilities.D100[capability] = {status: 'verified', evidence};
}
for (const capability of ['build', 'deterministic_replay']) {
  overrides.native_capabilities.D100[capability] = {status: 'available_unverified', evidence};
}

const scope = 'English en-v1.0.0 capability view: 60 source-course aggregates, 32 separate companion units, 1,201 exercises, exact solution provenance, and a 57-item concentrated mastery route.';
const limitations = [
  'This learner and educator capability is in English; it does not replace or rewrite the central Indonesian course truth.',
  'The adapter is a zero-copy navigation and evidence layer; it does not contain the mathematical bodies, TeX, PDFs, or native archives.',
  'The 44 new mastery solutions are editorial material; 13 mastery items instead reference existing public source solutions.',
  'Exactly 1,041 source exercises have an explicit no-public-source-solution state.',
  'Rights remain component-specific; no umbrella licence is claimed.',
  'Native MathML, tagged PDF, WCAG conformance, assistive-technology testing, human review, executable labs, strict source-profile reversibility, and Zenodo public-byte readback are not claimed by this adapter.',
  'The Stacks Project is a downstream reference, not translated source material.',
];
const tool = {
  tool_id: 'd100.open_learner_hub',
  label: 'D100 · Algebraic Geometry capability (English)',
  href: 'backend/d100/D100.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/d100/D100.html'),
  resource: await identity('docs/backend/d100/learning-map.json'),
  evidence: await identity('docs/backend/d100/validation.json'),
  limitations,
};
assert.ok(
  !overrides.learner_tools.D100
    || overrides.learner_tools.D100.every(old => old.tool_id === tool.tool_id),
  'Preserve unrelated D100 tools',
);
overrides.learner_tools.D100 = [tool];

const oldEducator = overrides.educator_evidence.D100;
const teacher = await identity('docs/backend/d100/D100-pengajar.html');
const url = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d100/D100-pengajar.html';
const resources = (oldEducator?.resources ?? []).filter(
  resource => resource.id !== 'D100:educator-hub-en-v1',
);
resources.push({
  id: 'D100:educator-hub-en-v1',
  title: 'D100 educator hub — English capability',
  resource_type: 'teacher-guide',
  status: 'verified',
  url,
  scope: `${scope} This is explicitly English-language support, not a claim of Indonesian educator prose.`,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
overrides.educator_evidence.D100 = {
  status: 'verified',
  verified_date: '2026-09-05',
  locator: url,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: [
    'exercise_bank',
    'solution_provenance',
  ],
  resources,
};

await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);
console.log(JSON.stringify({
  state: 'pass',
  admitted_roles: ['D100'],
  contract: manifest.contract,
  adapter_locale: manifest.locale,
  central_course_truth_locale: manifest.central_course_truth_locale,
  public_state_changed: false,
}));
