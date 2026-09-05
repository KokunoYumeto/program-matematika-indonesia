import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/d120-capability-v1';
const load = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const identity = async path => {
  const data = await readFile(resolve(root, path));
  return {path, bytes: data.length, sha256: createHash('sha256').update(data).digest('hex')};
};

const manifest = await load(`${base}/manifest.json`);
const validation = await load(`${base}/validation.json`);
const sourceLock = await load(`${base}/input/source-lock.json`);
const capabilities = await load(`${base}/data/capabilities.json`);
const learningMap = await load(`${base}/data/learning-map.json`);
const educatorMap = await load(`${base}/data/educator-map.json`);
const ledgers = await load(`${base}/data/ledger-references.json`);
const publicEvidence = await load(`${base}/data/public-evidence.json`);
const rightsAndTerms = await load(`${base}/data/rights-and-terms.json`);
const claimBoundary = await load(`${base}/data/claim-boundary.json`);

assert.equal(manifest.schema, 'd120-capability-manifest/1');
assert.equal(manifest.course_id, 'D120');
assert.equal(manifest.native_course_id, 'O017-D120');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.contract_2_3_1_conformance, 'not_claimed');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.native_family, 'research_practice');
assert.equal(manifest.native_release, '2026.08.24');
assert.equal(manifest.content_policy, 'selected_localized_metadata_and_evidence_only');
assert.deepEqual(manifest.projection, {
  base_and_wrapper_ledgers_distinct: true,
  central_course_truth_rewritten: false,
  native_ids_preserved: true,
  public_state_changed: false,
  renderer_fragments_are_locators_only: true,
  strict_native_roundtrip_claimed: false,
  zero_copy_native_bodies: true,
});
assert.equal(manifest.inputs.length, 21);
assert.equal(manifest.outputs.length, 12);
assert.deepEqual(manifest.counts, capabilities.counts);
assert.deepEqual(manifest.counts, {
  assessments: 14,
  competencies: 9,
  correction_records: 11,
  credential_state_definitions: 6,
  criteria: 79,
  evaluator_roles: 5,
  evidence_specs: 79,
  exercises: 54,
  guidance_records: 54,
  guided_by_relations: 54,
  learning_outcomes: 71,
  localized_text_records: 581,
  native_records: 1787,
  native_relations_active: 1105,
  native_relations_issued: 1107,
  native_relations_superseded: 2,
  native_rights_records: 6,
  rubrics: 14,
  semantic_records: 319,
  semantic_relations_issued: 1704,
  source_lock_inputs: 21,
  source_rights_components: 7,
  terminology_entries: 19,
  units: 9,
});

assert.equal(validation.schema, 'd120-capability-validation/1');
assert.equal(validation.state, 'pass');
assert.equal(validation.course_id, 'D120');
assert.equal(validation.contract, manifest.contract);
assert.equal(validation.locale, 'id-ID');
assert.equal(validation.source_hashes_verified, 21);
assert.equal(validation.negative_fixtures.length, 24);
assert.ok(validation.negative_fixtures.every(row => row.state === 'rejected'));
assert.deepEqual(validation.counts, manifest.counts);
assert.equal(validation.isolated_two_build_byte_identity.byte_identical, true);
assert.equal(validation.isolated_two_build_byte_identity.file_count, 13);

assert.equal(sourceLock.schema, 'd120-source-lock/1');
assert.equal(sourceLock.course_id, 'D120');
assert.equal(sourceLock.native_course_id, 'O017-D120');
assert.equal(sourceLock.locale, 'id-ID');
assert.equal(sourceLock.release_version, '2026.08.24');
assert.equal(sourceLock.native_repository.release_commit, 'cea42b799b038fcac6f9762386d2e8eecd5b1372');
assert.equal(sourceLock.native_repository.release_tree, '01af08fa5170a128c19962b72c7bf6a96428a65e');
assert.deepEqual(sourceLock.inputs, manifest.inputs);

assert.equal(learningMap.schema, 'd120-learning-map/1');
assert.equal(learningMap.contract, manifest.contract);
assert.equal(learningMap.course_id, 'D120');
assert.equal(learningMap.locale, 'id-ID');
assert.deepEqual(learningMap.route.unit_ids, Array.from({length: 9}, (_, index) => `O017-U${String(index + 1).padStart(2, '0')}`));
assert.equal(learningMap.units.length, 9);
assert.equal(learningMap.units.flatMap(row => row.practice).length, 54);
assert.equal(learningMap.units.flatMap(row => row.outcomes).length, 71);
assert.ok(learningMap.units.every(row => row.practice.every(item => item.guidance_kind === 'source_guidance_not_full_solution')));

assert.equal(educatorMap.schema, 'd120-educator-map/1');
assert.equal(educatorMap.course_id, 'D120');
assert.equal(educatorMap.locale, 'id-ID');
assert.equal(educatorMap.assessments.length, 14);
assert.equal(educatorMap.assessments.flatMap(row => row.rubric.criteria).length, 79);
assert.equal(educatorMap.credential_state_definitions.length, 6);
assert.equal(educatorMap.evaluator_roles.length, 5);
assert.equal(educatorMap.claim_boundary.contains_learner_completion_evidence, false);
assert.equal(educatorMap.claim_boundary.contains_learner_credential_claims, false);

assert.equal(ledgers.schema, 'd120-ledger-references/1');
assert.equal(ledgers.base_backend.record_count, 1787);
assert.equal(ledgers.base_backend.relations_issued, 1107);
assert.equal(ledgers.base_backend.relations_active, 1105);
assert.equal(ledgers.base_backend.relations_superseded, 2);
assert.equal(ledgers.semantic_wrapper.semantic_records, 319);
assert.equal(ledgers.semantic_wrapper.localized_text_records, 581);
assert.equal(ledgers.semantic_wrapper.relations_issued, 1704);
assert.equal(ledgers.semantic_wrapper.append_only_separate_from_base, true);
assert.equal(ledgers.projection.base_and_wrapper_ledgers_collapsed, false);

assert.equal(publicEvidence.schema, 'd120-public-evidence/1');
assert.equal(publicEvidence.github.release_commit, sourceLock.native_repository.release_commit);
assert.equal(publicEvidence.github.release_tree, sourceLock.native_repository.release_tree);
assert.equal(publicEvidence.github.anonymous_verification, 'verified');
assert.equal(publicEvidence.github.raw_files, '130/130');
assert.equal(publicEvidence.github.pages_files, '60/60');
assert.equal(publicEvidence.github.release_assets, '9/9');
assert.equal(publicEvidence.zenodo.record_id, 22073823);
assert.equal(publicEvidence.zenodo.doi, '10.5281/zenodo.22073823');
assert.equal(publicEvidence.zenodo.concept_doi, '10.5281/zenodo.22051866');
assert.equal(publicEvidence.zenodo.anonymous_verification, 'verified');
assert.equal(publicEvidence.zenodo.files.length, 9);
assert.equal(publicEvidence.reader.pdf_pages, 133);
assert.equal(publicEvidence.reader.semantic_html, true);
assert.equal(publicEvidence.reader.native_mathml, true);
assert.equal(publicEvidence.reader.tagged_pdf, false);
assert.equal(publicEvidence.public_state_changed, false);

assert.equal(rightsAndTerms.schema, 'd120-rights-and-terms/1');
assert.equal(rightsAndTerms.rights_records.length, 6);
assert.equal(rightsAndTerms.source_components.length, 7);
assert.equal(rightsAndTerms.terminology.length, 19);
assert.equal(rightsAndTerms.corrections.length, 11);
assert.equal(rightsAndTerms.blanket_license_claimed, false);
assert.deepEqual(claimBoundary, capabilities.claim_boundary);
for (const key of ['learner_attempt_instances', 'learner_submission_instances', 'learner_result_instances', 'credential_assertion_instances']) {
  assert.equal(claimBoundary[key], 0);
}
assert.equal(claimBoundary.native_bodies_copied, false);
assert.equal(claimBoundary.central_course_truth_rewritten, false);
assert.equal(claimBoundary.public_state_changed, false);

for (const item of manifest.outputs) {
  assert.deepEqual(
    await identity(`${base}/${item.path}`),
    {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256},
  );
}

const publicMappings = [
  [`${base}/views/D120.html`, 'docs/backend/d120/D120.html'],
  [`${base}/views/D120-pengajar.html`, 'docs/backend/d120/D120-pengajar.html'],
  [`${base}/data/learning-map.json`, 'docs/backend/d120/learning-map.json'],
  [`${base}/data/educator-map.json`, 'docs/backend/d120/educator-map.json'],
  [`${base}/validation.json`, 'docs/backend/d120/validation.json'],
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
  ['verified_native_public_release', `${base}/data/public-evidence.json`],
  ['component_rights_and_terminology', `${base}/data/rights-and-terms.json`],
]) {
  const {bytes, sha256} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-05'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
assert.ok(
  !overrides.semantic_adapters.D120
    || !overrides.semantic_adapters.D120.contract_version
    || overrides.semantic_adapters.D120.contract_version === manifest.contract,
  'Preserve a different admitted D120 contract',
);
overrides.semantic_adapters.D120 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_9_native_units_54_exercise_guidance_pairs_71_outcomes_14_assessments_79_criteria_and_distinct_base_and_semantic_ledgers',
  evidence,
};

overrides.native_capabilities.D120 = {...(overrides.native_capabilities.D120 ?? {})};
for (const capability of [
  'unit_identity',
  'terminology',
  'translation_rights',
  'corrections',
  'build',
  'deterministic_replay',
  'educator_unit_alignment',
]) {
  overrides.native_capabilities.D120[capability] = {status: 'verified', evidence};
}
// D120 is natively authored in Indonesian. Its source/provenance ledger is
// verified, but a source-to-target translation ledger is genuinely inapplicable.
overrides.native_capabilities.D120.translation_ledger = {status: 'not_applicable', evidence};

const scope = 'Sembilan unit native, 54 pasangan latihan–panduan, 71 hasil belajar, 14 penilaian, 14 rubrik, 79 kriteria, dan bukti penyampaian yang memakai identitas bersama.';
const limitations = [
  'Adapter adalah proyeksi metadata dan bukti zero-copy; badan kursus, QMD, HTML native, PDF, dan arsip tetap berada pada edisi publik native.',
  'Semua 54 rekaman pendamping latihan adalah panduan sumber, bukan solusi lengkap.',
  'D120 ditulis native dalam Bahasa Indonesia; ledger penerjemahan sumber-ke-target tidak berlaku, sedangkan ledger sumber/provenance tetap dipertahankan.',
  'Backend semantik hanya berisi definisi dan templat: nol percobaan, kiriman, hasil, partisipasi komunitas, atau kredensial pelajar diklaim.',
  'Fragmen HTML adalah penunjuk lokasi nonkanonis, bukan identitas semantik.',
  'Hak bersifat spesifik per komponen; tidak ada lisensi payung yang direka.',
  'HTML semantik dan MathML native tersedia; PDF 133 halaman tidak bertag.',
  'Replay konten/struktur dan paket deterministik dibuktikan, tetapi identitas byte PDF lintas mesin/engine tidak diklaim.',
];
const tool = {
  tool_id: 'd120.open_learner_hub',
  label: 'D120 · Kerja Matematika yang Dapat Ditelusuri',
  href: 'backend/d120/D120.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/d120/D120.html'),
  resource: await identity('docs/backend/d120/learning-map.json'),
  evidence: await identity('docs/backend/d120/validation.json'),
  limitations,
};
assert.ok(
  !overrides.learner_tools.D120
    || overrides.learner_tools.D120.every(old => old.tool_id === tool.tool_id),
  'Preserve unrelated D120 tools',
);
overrides.learner_tools.D120 = [tool];

const oldEducator = overrides.educator_evidence.D120;
const teacher = await identity('docs/backend/d120/D120-pengajar.html');
const url = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d120/D120-pengajar.html';
const resources = (oldEducator?.resources ?? []).filter(
  resource => !['D120:native-delivery-wrapper', 'D120:educator-hub-v1'].includes(resource.id),
);
resources.push({
  id: 'D120:native-delivery-wrapper',
  title: 'Perangkat penyampaian dan penilaian autentik O017',
  resource_type: 'assessment-blueprints',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/kerja-matematika-yang-dapat-ditelusuri-id/wrapper/',
  scope: 'Lima jalur autentik, definisi bukti, gerbang, templat, dan contoh kalibrasi yang tetap berlabel sintetis.',
});
resources.push({
  id: 'D120:educator-hub-v1',
  title: 'Peta hasil, penilaian, rubrik, bukti, dan kredensial D120 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url,
  scope: `${scope} Rekaman pelajar tetap nol; status kredensial adalah definisi, bukan klaim pencapaian.`,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
overrides.educator_evidence.D120 = {
  status: 'verified',
  verified_date: '2026-09-05',
  locator: url,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: [
    'outcome_evidence_map',
    'lesson_sequences',
    'exercise_bank',
    'staged_hints_answers_solutions',
    'assessment_blueprints',
    'rubrics',
    'accessibility_accommodations',
    'remix_selectors',
    'solution_provenance',
  ],
  resources,
};

await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);
console.log(JSON.stringify({
  state: 'pass',
  admitted_roles: ['D120'],
  contract: manifest.contract,
  native_locale: manifest.locale,
  public_state_changed: false,
}));
