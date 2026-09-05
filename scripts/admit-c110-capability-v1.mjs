import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/c110-capability-v1';
const load = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const identity = async path => {
  const data = await readFile(resolve(root, path));
  return {path, bytes: data.length, sha256: createHash('sha256').update(data).digest('hex')};
};

const manifest = await load(`${base}/manifest.json`);
const validation = await load(`${base}/validation.json`);
const sourceLock = await load(`${base}/input/source-lock.json`);
const publicReadback = await load(`${base}/input/public-native-readback.json`);
const capabilities = await load(`${base}/data/capabilities.json`);
const learningMap = await load(`${base}/data/learning-map.json`);
const educatorMap = await load(`${base}/data/educator-map.json`);
const alignments = await load(`${base}/data/translation-alignments.json`);
const ledgers = await load(`${base}/data/ledger-references.json`);
const publicEvidence = await load(`${base}/data/public-evidence.json`);
const rightsAndTerms = await load(`${base}/data/rights-and-terms.json`);
const claimBoundary = await load(`${base}/data/claim-boundary.json`);

assert.equal(manifest.schema, 'c110-capability-manifest/1');
assert.equal(manifest.course_id, 'C110');
assert.equal(manifest.native_role_id, 'R015');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.contract_2_3_1_conformance, 'not_claimed');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.native_family, 'numerical_analysis_lyx_backend');
assert.equal(manifest.native_release, '3.0-id.2-r1');
assert.equal(manifest.content_policy, 'stable_native_ids_selected_metadata_and_evidence_only');
assert.deepEqual(manifest.projection, {
  all_alignment_ids_preserved: true,
  central_course_truth_rewritten: false,
  common_virtual_backend_materialized: false,
  exercise_solution_joins_inferred: false,
  existing_reversible_migration_reused: true,
  historical_migration_receipt_rewritten: false,
  native_ids_preserved: true,
  public_state_changed: false,
  solution_and_answer_modules_distinct: true,
  zero_copy_native_bodies: true,
});
assert.equal(manifest.inputs.length, 14);
assert.equal(manifest.outputs.length, 14);
assert.deepEqual(manifest.counts, capabilities.counts);
assert.deepEqual(manifest.counts, {
  alignments: 4621,
  answer_module_segments: 529,
  answer_module_units: 26,
  answer_modules: 1,
  artifacts: 2,
  common_generated_records: 24883,
  common_tables: 25,
  common_virtual_records: 53055,
  concepts: 12,
  corrections: 325,
  experiments: 2,
  file_modules: 29,
  formula_pairs: 12641,
  github_verified_bytes: 78131265,
  github_verified_files: 26,
  inset_pairs: 21271,
  layout_pairs: 11216,
  localizations: 4621,
  native_backend_bytes: 22101516,
  native_backend_files: 19,
  native_record_types: 19,
  native_records: 28172,
  pdf_pages: 387,
  relations: 17614,
  rights_components: 4,
  segments: 4621,
  solution_module_segments: 953,
  solution_module_units: 26,
  solution_modules: 1,
  source_bytes: 2791045,
  source_files: 31,
  target_bytes: 2844828,
  target_files: 31,
  teaching_modules: 27,
  terms: 593,
  units: 281,
  zenodo_verified_bytes: 41614423,
  zenodo_verified_files: 4,
});

assert.equal(validation.schema, 'c110-capability-validation/1');
assert.equal(validation.state, 'pass');
assert.equal(validation.source_hashes_verified, 14);
assert.equal(validation.native_backend_hashes_verified, 19);
assert.equal(validation.negative_fixtures.length, 26);
assert.ok(validation.negative_fixtures.every(row => row.state === 'rejected'));
assert.deepEqual(validation.counts, manifest.counts);
assert.equal(validation.isolated_two_build_byte_identity.byte_identical, true);
assert.equal(validation.isolated_two_build_byte_identity.file_count, 15);

assert.equal(sourceLock.schema, 'c110-source-lock/1');
assert.equal(sourceLock.native_repository.current_public_head, 'cf4a425918b6555d3157001bfa7c18acc1f97026');
assert.equal(sourceLock.native_repository.current_public_tree, '32004a75627e8cd0401fec5c855663c37a0848fe');
assert.equal(sourceLock.backend_integrity.files, 19);
assert.equal(sourceLock.backend_integrity.all_file_hashes_verified, true);
assert.equal(sourceLock.native_inputs.length, 12);
assert.equal(sourceLock.migration_input.path, 'backend/migrations/tea-time-id-v1/MIGRATION_RECEIPT.json');
assert.equal(sourceLock.public_readback_input.path, `${base}/input/public-native-readback.json`);
assert.deepEqual([...sourceLock.native_inputs, sourceLock.migration_input, sourceLock.public_readback_input], manifest.inputs);

assert.equal(learningMap.schema, 'c110-learning-map/1');
assert.equal(learningMap.modules.length, 29);
assert.equal(learningMap.units.length, 281);
assert.equal(new Set(learningMap.route.module_ids).size, 29);
assert.deepEqual(learningMap.program_prerequisites, ['B30', 'B40', 'B80', 'C10']);
assert.equal(learningMap.prerequisite_scope, 'central_course_level_only_not_native_per_unit_claims');
assert.equal(learningMap.modules.filter(row => row.role === 'solutions').length, 1);
assert.equal(learningMap.modules.filter(row => row.role === 'answers').length, 1);

assert.equal(educatorMap.schema, 'c110-educator-map/1');
assert.equal(educatorMap.selector.modules.length, 29);
assert.equal(educatorMap.selector.units.length, 281);
assert.equal(educatorMap.selector.experiments.length, 2);
assert.equal(educatorMap.selector.body_content_embedded, false);
assert.equal(educatorMap.claim_boundary.native_exercise_entity_records, 0);
assert.equal(educatorMap.claim_boundary.exercise_solution_joins_inferred, false);

assert.equal(alignments.schema, 'c110-translation-alignment-index/1');
assert.equal(alignments.alignment_count, 4621);
assert.equal(alignments.alignments.length, 4621);
assert.equal(new Set(alignments.alignments.map(row => row.alignment_id)).size, 4621);
assert.equal(alignments.body_content_embedded, false);

assert.equal(ledgers.schema, 'c110-ledger-references/1');
assert.equal(ledgers.backend_integrity.files, 19);
assert.equal(ledgers.backend_integrity.bytes, 22101516);
assert.equal(ledgers.common_projection.record_count, 53055);
assert.equal(ledgers.common_projection.native_ids_preserved, 28172);
assert.equal(ledgers.common_projection.native_payload_fields_changed, 0);
assert.equal(ledgers.projection.native_bodies_copied, false);
assert.equal(ledgers.projection.common_virtual_backend_materialized, false);

assert.equal(publicReadback.schema, 'c110-native-public-readback/1');
assert.equal(publicReadback.access_mode, 'anonymous_no_credentials');
assert.equal(publicReadback.github.verified_files, 26);
assert.equal(publicReadback.github.verified_bytes, 78131265);
assert.equal(publicReadback.zenodo.verified_files, 4);
assert.equal(publicReadback.zenodo.verified_bytes, 41614423);
assert.equal(publicReadback.zenodo.access_right, 'open');
assert.equal(publicReadback.checks.external_state_changed, false);

assert.equal(publicEvidence.schema, 'c110-public-evidence/1');
assert.equal(publicEvidence.github.commit, sourceLock.native_repository.current_public_head);
assert.equal(publicEvidence.github.tree, sourceLock.native_repository.current_public_tree);
assert.equal(publicEvidence.zenodo.record_id, 22075088);
assert.equal(publicEvidence.zenodo.doi, '10.5281/zenodo.22075088');
assert.equal(publicEvidence.zenodo.concept_doi, '10.5281/zenodo.22054085');
assert.equal(publicEvidence.reader.pdf_pages, 387);
assert.equal(publicEvidence.reader.native_semantic_html, false);
assert.equal(publicEvidence.reader.tagged_pdf_claimed, false);
assert.equal(publicEvidence.public_state_changed, false);

assert.equal(rightsAndTerms.schema, 'c110-rights-and-terms/1');
assert.equal(rightsAndTerms.component_boundaries.length, 4);
assert.equal(rightsAndTerms.terminology.length, 593);
assert.equal(rightsAndTerms.concepts.length, 12);
assert.equal(rightsAndTerms.corrections.length, 325);
assert.equal(rightsAndTerms.blanket_license_claimed, false);
assert.deepEqual(claimBoundary, capabilities.claim_boundary);
for (const key of ['learner_attempt_instances', 'learner_submission_instances', 'learner_result_instances', 'credential_assertion_instances', 'native_exercise_entity_records']) assert.equal(claimBoundary[key], 0);
assert.equal(claimBoundary.exercise_solution_joins_inferred, false);
assert.equal(claimBoundary.native_bodies_copied, false);
assert.equal(claimBoundary.common_virtual_backend_materialized, false);

for (const item of manifest.outputs) {
  assert.deepEqual(await identity(`${base}/${item.path}`), {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256});
}

const publicMappings = [
  [`${base}/views/C110.html`, 'docs/backend/c110/C110.html'],
  [`${base}/views/C110-pengajar.html`, 'docs/backend/c110/C110-pengajar.html'],
  [`${base}/data/learning-map.json`, 'docs/backend/c110/learning-map.json'],
  [`${base}/data/educator-map.json`, 'docs/backend/c110/educator-map.json'],
  [`${base}/data/translation-alignments.json`, 'docs/backend/c110/translation-alignments.json'],
  [`${base}/data/rights-and-terms.json`, 'docs/backend/c110/rights-and-terms.json'],
  [`${base}/data/ledger-references.json`, 'docs/backend/c110/ledger-references.json'],
  [`${base}/validation.json`, 'docs/backend/c110/validation.json'],
];
for (const [source, target] of publicMappings) {
  const bytes = await readFile(resolve(root, source));
  await mkdir(dirname(resolve(root, target)), {recursive: true});
  await writeFile(resolve(root, target), bytes);
  assert.deepEqual(await identity(target), {path: target, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')});
}

const evidence = [];
for (const [kind, path] of [
  ['central_adapter_manifest', `${base}/manifest.json`],
  ['deterministic_validation_receipt', `${base}/validation.json`],
  ['native_migration_and_public_source_lock', `${base}/input/source-lock.json`],
  ['anonymous_native_public_readback', `${base}/input/public-native-readback.json`],
  ['component_rights_terminology_and_corrections', `${base}/data/rights-and-terms.json`],
  ['native_and_reversible_migration_ledgers', `${base}/data/ledger-references.json`],
  ['complete_translation_alignment_index', `${base}/data/translation-alignments.json`],
]) {
  const {bytes, sha256} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-05'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
assert.ok(!overrides.semantic_adapters.C110 || !overrides.semantic_adapters.C110.contract_version || overrides.semantic_adapters.C110.contract_version === manifest.contract, 'Preserve a different admitted C110 contract');
overrides.semantic_adapters.C110 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_29_file_modules_281_native_units_4621_translation_alignments_593_terms_325_corrections_two_experiments_and_existing_28172_record_native_backend',
  evidence,
};
overrides.native_capabilities.C110 = {...(overrides.native_capabilities.C110 ?? {})};
for (const capability of ['unit_identity', 'terminology', 'translation_rights', 'corrections', 'build', 'deterministic_replay', 'educator_unit_alignment', 'translation_ledger']) {
  overrides.native_capabilities.C110[capability] = {status: 'verified', evidence};
}

const scope = 'Dua puluh sembilan modul berkas, seluruh 281 unit native, 4.621 alignment terjemahan, 593 istilah, 325 koreksi, dua eksperimen, 31 pasangan berkas sumber/target, dan proyeksi common-v1 reversibel 53.055 rekaman.';
const limitations = [
  'Adapter adalah proyeksi metadata dan bukti zero-copy; badan buku, PDF, sumber, dan backend lengkap tetap pada edisi publik native.',
  'Backend native tidak memiliki entitas latihan tersendiri; hubungan latihan-ke-solusi atau latihan-ke-jawaban tidak diciptakan.',
  'Modul solusi dan jawaban tetap terpisah dan dapat dipilih, tanpa klaim pasangan satu-ke-satu per latihan.',
  'Status not_built dan unpublished pada rekaman lokalisasi adalah status tingkat segmen, bukan status artefak akhir.',
  'Dua ratus koreksi open_recorded adalah temuan sumber yang dipertahankan dan bukan kegagalan rilis.',
  'Prasyarat B30, B40, B80, dan C10 adalah relasi tingkat kursus pusat, bukan graf prasyarat per unit native.',
  'Repo native tidak menyediakan pembaca HTML semantik lengkap; hub pusat menavigasi metadata, PDF, dan sumber.',
  'Proyeksi common-v1 53.055 rekaman tetap virtual dan tidak dimaterialisasi ulang.',
];
const tool = {
  tool_id: 'c110.open_learner_hub',
  label: 'C110 · Analisis Numerik',
  href: 'backend/c110/C110.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/c110/C110.html'),
  resource: await identity('docs/backend/c110/learning-map.json'),
  evidence: await identity('docs/backend/c110/validation.json'),
  limitations,
};
assert.ok(!overrides.learner_tools.C110 || overrides.learner_tools.C110.every(old => old.tool_id === tool.tool_id), 'Preserve unrelated C110 tools');
overrides.learner_tools.C110 = [tool];

const teacher = await identity('docs/backend/c110/C110-pengajar.html');
const educatorMapIdentity = await identity('docs/backend/c110/educator-map.json');
const alignmentIdentity = await identity('docs/backend/c110/translation-alignments.json');
const educatorUrl = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c110/C110-pengajar.html';
const resources = (overrides.educator_evidence.C110?.resources ?? []).filter(resource => !['C110:educator-hub-v1', 'C110:educator-map-v1', 'C110:alignment-index-v1'].includes(resource.id));
resources.push({
  id: 'C110:educator-hub-v1',
  title: 'Pemilih modul, unit, dan eksperimen C110 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url: educatorUrl,
  scope: `${scope} Ekspor JSON mempertahankan batas modul solusi/jawaban tanpa menciptakan pasangan latihan.`,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
resources.push({
  id: 'C110:educator-map-v1',
  title: 'Peta 29 modul dan 281 unit native C110',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c110/educator-map.json',
  scope: 'Data pemilih modul, unit, dan eksperimen dengan identitas native dan batas klaim eksplisit.',
  bytes: educatorMapIdentity.bytes,
  sha256: educatorMapIdentity.sha256,
});
resources.push({
  id: 'C110:alignment-index-v1',
  title: 'Indeks 4.621 alignment terjemahan C110',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c110/translation-alignments.json',
  scope: 'Indeks tanpa badan teks yang mempertahankan ID segmen, lokalisasi, unit, modul, hash, dan status alur.',
  bytes: alignmentIdentity.bytes,
  sha256: alignmentIdentity.sha256,
});
overrides.educator_evidence.C110 = {
  status: 'verified',
  verified_date: '2026-09-05',
  locator: educatorUrl,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: ['lesson_sequences', 'activities_labs', 'remix_selectors', 'solution_provenance', 'accessibility_accommodations'],
  resources,
};
await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);

const learnerTarget = 'backend/authority/learner-delivery-overrides-v1.json';
const learner = await load(learnerTarget);
const pdf = {
  status: 'verified',
  format: 'application/pdf',
  url: 'https://zenodo.org/records/22075088/files/Tea-Time-Numerical-Analysis-id-ID.pdf?download=1',
  bytes: 8202487,
  sha256: 'd573b7233d0baa07381e2052a749757885db3a31fbfe695c5a4851ea42d91b6d',
  scope: 'whole_course',
  evidence: {
    kind: 'anonymous_public_byte_readback',
    locator: `https://github.com/KokunoYumeto/program-matematika-indonesia/blob/main/${base}/input/public-native-readback.json`,
    verified_date: '2026-09-05',
  },
};
learner.courses.C110 = {
  ...(learner.courses.C110 ?? {}),
  primary: pdf,
  pdf,
  capabilities: {
    semantic_html: {status: 'not_yet_produced'},
    mathml: {status: 'not_yet_produced'},
    print_profile: {status: 'verified'},
    chapter_downloads: {status: 'available_unverified'},
  },
};
await writeFile(resolve(root, learnerTarget), `${JSON.stringify(learner, null, 2)}\n`);

console.log(JSON.stringify({state: 'pass', admitted_roles: ['C110'], contract: manifest.contract, native_locale: manifest.locale, public_state_changed: false}));
