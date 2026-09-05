import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/d10-capability-v1';
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

assert.equal(manifest.schema, 'd10-capability-manifest/1');
assert.equal(manifest.course_id, 'D10');
assert.equal(manifest.native_role_id, 'O007');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.contract_2_3_1_conformance, 'not_claimed');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.native_family, 'fremlin_measure_theory_volumes_1_2');
assert.equal(manifest.native_release, '1.0.0');
assert.equal(manifest.content_policy, 'selected_localized_metadata_and_evidence_only');
assert.deepEqual(manifest.projection, {
  catalog_manifest_replayed: true,
  central_course_truth_rewritten: false,
  native_ids_preserved: true,
  public_state_changed: false,
  reader_routes_distinct_from_catalog_units: true,
  source_hints_not_retyped_as_full_solutions: true,
  strict_native_roundtrip_claimed: false,
  zero_copy_native_bodies: true,
});
assert.equal(manifest.inputs.length, 22);
assert.equal(manifest.outputs.length, 12);
assert.deepEqual(manifest.counts, capabilities.counts);
assert.deepEqual(manifest.counts, {
  catalog_files: 507,
  catalog_manifest_rows: 506,
  corpora: 1,
  correction_rows: 420,
  explicit_hints: 276,
  formula_occurrences: 53491,
  math_source_assistive_pairs: 53255,
  native_rights_records: 2,
  official_pages: 672,
  reader_files: 138,
  reader_routes: 98,
  reader_viewport_observations: 196,
  release_assets: 3,
  resources: 349,
  schema_valid_records: 16096,
  source_lock_inputs: 22,
  standard_header_exercises: 1094,
  terminology_rows: 132,
  terminology_tables: 14,
  typed_exercises: 1096,
  units: 94,
  variant_header_exercises: 2,
  volumes: 2,
});

assert.equal(validation.schema, 'd10-capability-validation/1');
assert.equal(validation.state, 'pass');
assert.equal(validation.course_id, 'D10');
assert.equal(validation.contract, manifest.contract);
assert.equal(validation.locale, 'id-ID');
assert.equal(validation.source_hashes_verified, 22);
assert.equal(validation.catalog_manifest_hashes_verified, 506);
assert.equal(validation.negative_fixtures.length, 22);
assert.ok(validation.negative_fixtures.every(row => row.state === 'rejected'));
assert.deepEqual(validation.counts, manifest.counts);
assert.equal(validation.isolated_two_build_byte_identity.byte_identical, true);
assert.equal(validation.isolated_two_build_byte_identity.file_count, 13);

assert.equal(sourceLock.schema, 'd10-source-lock/1');
assert.equal(sourceLock.course_id, 'D10');
assert.equal(sourceLock.native_role_id, 'O007');
assert.equal(sourceLock.native_repository.release_commit, '49ed814fc02283df826c4c6c3a9d860888bfec29');
assert.equal(sourceLock.native_repository.release_tree, '334f7902af37d331387041b186b4e1470cd60e7e');
assert.equal(sourceLock.native_repository.current_public_head_observed_separately, '1cb0f67dcc75a5100e3aa3ca4f9b8f3fb8fb25cc');
assert.equal(sourceLock.catalog_manifest.listed_files, 506);
assert.equal(sourceLock.catalog_manifest.tree_files_including_manifest, 507);
assert.deepEqual(sourceLock.inputs, manifest.inputs);

assert.equal(learningMap.schema, 'd10-learning-map/1');
assert.equal(learningMap.contract, manifest.contract);
assert.equal(learningMap.course_id, 'D10');
assert.equal(learningMap.locale, 'id-ID');
assert.equal(learningMap.units.length, 94);
assert.equal(new Set(learningMap.route.unit_ids).size, 94);
assert.equal(learningMap.units.flatMap(row => row.exercise_ids).length, 1096);
assert.equal(new Set(learningMap.units.flatMap(row => row.exercise_ids)).size, 1096);
assert.ok(learningMap.units.flatMap(row => row.exercise_ids).includes('243Xo'));
assert.ok(learningMap.units.flatMap(row => row.exercise_ids).includes('274Xf'));
assert.equal(learningMap.units.reduce((sum, row) => sum + row.explicit_hint_count, 0), 276);
assert.equal(learningMap.units.reduce((sum, row) => sum + row.formula_count, 0), 53491);
assert.deepEqual(learningMap.program_prerequisites, ['C20', 'C90']);
assert.equal(learningMap.prerequisite_scope, 'central_course_level_only_not_native_per_unit_claims');
assert.equal(learningMap.supplemental_reader_surfaces.length, 4);

assert.equal(educatorMap.schema, 'd10-educator-map/1');
assert.equal(educatorMap.course_id, 'D10');
assert.equal(educatorMap.selector.selected_units.length, 94);
assert.equal(educatorMap.selector.body_content_embedded, false);
assert.equal(educatorMap.claim_boundary.complete_solution_layer_available, false);
assert.equal(educatorMap.claim_boundary.explicit_source_hints_available, 276);
assert.equal(educatorMap.claim_boundary.proof_and_result_records_are_exercise_solutions, false);

assert.equal(ledgers.schema, 'd10-ledger-references/1');
assert.equal(ledgers.catalog_integrity.listed_files, 506);
assert.equal(ledgers.catalog_integrity.tree_files_including_manifest, 507);
assert.equal(ledgers.catalog_integrity.all_listed_hashes_verified, true);
assert.equal(ledgers.resources.length, 349);
assert.equal(ledgers.source_target_unit_hashes.length, 94);
assert.equal(ledgers.projection.native_bodies_copied, false);

assert.equal(publicEvidence.schema, 'd10-public-evidence/1');
assert.equal(publicEvidence.github.release_commit, sourceLock.native_repository.release_commit);
assert.equal(publicEvidence.github.release_tree, sourceLock.native_repository.release_tree);
assert.equal(publicEvidence.github.anonymous_verification, 'verified');
assert.equal(publicEvidence.github.release_assets.length, 3);
assert.equal(publicEvidence.zenodo.record_id, 22181780);
assert.equal(publicEvidence.zenodo.doi, '10.5281/zenodo.22181780');
assert.equal(publicEvidence.zenodo.concept_doi, '10.5281/zenodo.22059798');
assert.equal(publicEvidence.zenodo.anonymous_verification, 'verified');
assert.equal(publicEvidence.zenodo.release_assets.length, 3);
assert.equal(publicEvidence.reader.official_source_pages, 672);
assert.equal(publicEvidence.reader.pdf_reflow_pages, 715);
assert.equal(publicEvidence.reader.portable_routes, 98);
assert.equal(publicEvidence.reader.math_assistive_pairs, 53255);
assert.equal(publicEvidence.reader.online_native_html, false);
assert.equal(publicEvidence.reader.tagged_pdf, false);
assert.equal(publicEvidence.public_state_changed, false);

assert.equal(rightsAndTerms.schema, 'd10-rights-and-terms/1');
assert.equal(rightsAndTerms.rights_records.length, 2);
assert.equal(rightsAndTerms.third_party_components.length, 1);
assert.equal(rightsAndTerms.terminology.table_count, 14);
assert.equal(rightsAndTerms.terminology.data_row_count, 132);
assert.equal(rightsAndTerms.corrections.length, 420);
assert.equal(rightsAndTerms.blanket_license_claimed, false);
assert.deepEqual(claimBoundary, capabilities.claim_boundary);
for (const key of ['learner_attempt_instances', 'learner_submission_instances', 'learner_result_instances', 'credential_assertion_instances', 'complete_solution_records']) {
  assert.equal(claimBoundary[key], 0);
}
assert.equal(claimBoundary.explicit_source_hints, 276);
assert.equal(claimBoundary.proof_and_result_records_retyped_as_solutions, false);
assert.equal(claimBoundary.native_bodies_copied, false);
assert.equal(claimBoundary.online_native_html_claimed, false);
assert.equal(claimBoundary.tagged_pdf_claimed, false);

for (const item of manifest.outputs) {
  assert.deepEqual(await identity(`${base}/${item.path}`), {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256});
}

const publicMappings = [
  [`${base}/views/D10.html`, 'docs/backend/d10/D10.html'],
  [`${base}/views/D10-pengajar.html`, 'docs/backend/d10/D10-pengajar.html'],
  [`${base}/data/learning-map.json`, 'docs/backend/d10/learning-map.json'],
  [`${base}/data/educator-map.json`, 'docs/backend/d10/educator-map.json'],
  [`${base}/data/rights-and-terms.json`, 'docs/backend/d10/rights-and-terms.json'],
  [`${base}/data/ledger-references.json`, 'docs/backend/d10/ledger-references.json'],
  [`${base}/validation.json`, 'docs/backend/d10/validation.json'],
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
  ['native_metadata_intake', `${base}/input/source-lock.json`],
  ['verified_native_public_release', `${base}/data/public-evidence.json`],
  ['component_rights_terminology_and_corrections', `${base}/data/rights-and-terms.json`],
  ['catalog_and_source_target_ledgers', `${base}/data/ledger-references.json`],
]) {
  const {bytes, sha256} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-05'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
assert.ok(!overrides.semantic_adapters.D10 || !overrides.semantic_adapters.D10.contract_version || overrides.semantic_adapters.D10.contract_version === manifest.contract, 'Preserve a different admitted D10 contract');
overrides.semantic_adapters.D10 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_94_native_units_1096_typed_exercises_276_source_hints_53491_formulas_420_corrections_132_terminology_decisions_and_506_manifest_bound_catalog_files',
  evidence,
};

overrides.native_capabilities.D10 = {...(overrides.native_capabilities.D10 ?? {})};
for (const capability of ['unit_identity', 'terminology', 'translation_rights', 'corrections', 'build', 'deterministic_replay', 'educator_unit_alignment', 'translation_ledger']) {
  overrides.native_capabilities.D10[capability] = {status: 'verified', evidence};
}

const scope = 'Dua jilid, 94 unit native, 1.096 ID latihan, 276 petunjuk sumber, 53.491 kemunculan formula, 420 koreksi, 132 keputusan istilah, dan rute pembaca luring yang memakai identitas bersama.';
const limitations = [
  'Adapter adalah proyeksi metadata dan bukti zero-copy; badan buku, sumber TeX, PDF, dan arsip HTML tetap berada pada edisi publik native.',
  'Sensus 1.094 hanya menghitung header standar; 1.096 identitas latihan bertipe dipertahankan, termasuk dua header varian yang sah.',
  'Hanya 276 petunjuk sumber eksplisit tersedia; tidak ada jawaban atau solusi lengkap yang direka.',
  'Bukti dan hasil matematis native tidak diretip sebagai solusi latihan.',
  'Prasyarat C20 dan C90 adalah relasi tingkat kursus pusat, bukan graf prasyarat per unit native.',
  'Pembaca HTML native tersedia sebagai arsip luring dan tidak diklaim sebagai situs native per-unit daring.',
  'Hak tetap spesifik per komponen: Design Science, CC0-1.0, dan Apache-2.0 tidak diratakan menjadi satu lisensi.',
  'PDF reflow 715 halaman tersedia, tetapi PDF bertag tidak diklaim.',
];
const tool = {
  tool_id: 'd10.open_learner_hub',
  label: 'D10 · Ukuran dan Integrasi',
  href: 'backend/d10/D10.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/d10/D10.html'),
  resource: await identity('docs/backend/d10/learning-map.json'),
  evidence: await identity('docs/backend/d10/validation.json'),
  limitations,
};
assert.ok(!overrides.learner_tools.D10 || overrides.learner_tools.D10.every(old => old.tool_id === tool.tool_id), 'Preserve unrelated D10 tools');
overrides.learner_tools.D10 = [tool];

const teacher = await identity('docs/backend/d10/D10-pengajar.html');
const educatorMapIdentity = await identity('docs/backend/d10/educator-map.json');
const educatorUrl = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d10/D10-pengajar.html';
const resources = (overrides.educator_evidence.D10?.resources ?? []).filter(resource => !['D10:educator-hub-v1', 'D10:educator-map-v1'].includes(resource.id));
resources.push({
  id: 'D10:educator-hub-v1',
  title: 'Pemilih unit dan latihan D10 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url: educatorUrl,
  scope: `${scope} Ekspor JSON menyimpan pilihan ID native tanpa menyalin badan buku atau menciptakan solusi.`,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
resources.push({
  id: 'D10:educator-map-v1',
  title: 'Peta unit, latihan, petunjuk, formula, dan koreksi D10',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d10/educator-map.json',
  scope: 'Data pemilih 94 unit dengan ID latihan eksak dan batas eksplisit bahwa tidak ada bank solusi lengkap.',
  bytes: educatorMapIdentity.bytes,
  sha256: educatorMapIdentity.sha256,
});
overrides.educator_evidence.D10 = {
  status: 'verified',
  verified_date: '2026-09-05',
  locator: educatorUrl,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: ['lesson_sequences', 'exercise_bank', 'accessibility_accommodations', 'remix_selectors', 'solution_provenance'],
  resources,
};

await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);
console.log(JSON.stringify({state: 'pass', admitted_roles: ['D10'], contract: manifest.contract, native_locale: manifest.locale, public_state_changed: false}));
