import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/c120-capability-v1';
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

assert.equal(manifest.schema, 'c120-capability-manifest/1');
assert.equal(manifest.course_id, 'C120');
assert.equal(manifest.native_role_id, 'O005');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.contract_2_3_1_conformance, 'not_claimed');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.native_family, 'modeling_and_nonlinear_dynamics');
assert.equal(manifest.native_release, 'v1.01-id-complete-reader-20260823-r5');
assert.equal(manifest.content_policy, 'selected_localized_metadata_and_evidence_only');
assert.deepEqual(manifest.projection, {
  central_course_truth_rewritten: false,
  common_virtual_backend_materialized: false,
  existing_reversible_migration_reused: true,
  historical_migration_receipt_rewritten: false,
  mastery_support_types_preserved: true,
  native_ids_preserved: true,
  project_result_reproduction_claimed: false,
  public_state_changed: false,
  source_and_bridge_units_distinct: true,
  zero_copy_native_bodies: true,
});
assert.equal(manifest.inputs.length, 16);
assert.equal(manifest.outputs.length, 12);
assert.deepEqual(manifest.counts, capabilities.counts);
assert.deepEqual(manifest.counts, {
  backend_bytes: 3270308,
  backend_files: 81,
  bridge_notebooks: 4,
  bridge_segments: 657,
  bridge_units: 4,
  chapter_notebooks: 10,
  common_nonempty_tables: 13,
  common_tables: 38,
  common_virtual_records: 16029,
  correction_rows: 160,
  corrections_resolved: 160,
  derived_segment_variants: 7553,
  derived_translation_alignments: 3448,
  mastery_files: 16,
  mastery_problems: 141,
  native_records: 4941,
  problems_with_hints: 141,
  project_notebooks: 12,
  project_packet_files: 72,
  projects: 12,
  public_pages_bytes: 56411468,
  public_pages_files: 253,
  qualitative_rubrics: 14,
  reader_outline_entries: 28,
  reader_pages: 355,
  reader_routes: 26,
  release_assets: 6,
  segments: 4105,
  source_lock_inputs: 16,
  source_segments: 3448,
  source_units: 22,
  terminology_admitted: 320,
  terminology_csv_normalized_rows: 1,
  terminology_provisional: 1,
  terminology_rows: 321,
  total_notebooks: 26,
  units: 26,
  worked_classifications: 1,
  worked_solutions: 126,
});

assert.equal(validation.schema, 'c120-capability-validation/1');
assert.equal(validation.state, 'pass');
assert.equal(validation.course_id, 'C120');
assert.equal(validation.contract, manifest.contract);
assert.equal(validation.source_hashes_verified, 16);
assert.equal(validation.native_backend_hashes_verified, 81);
assert.equal(validation.negative_fixtures.length, 25);
assert.ok(validation.negative_fixtures.every(row => row.state === 'rejected'));
assert.deepEqual(validation.counts, manifest.counts);
assert.equal(validation.isolated_two_build_byte_identity.byte_identical, true);
assert.equal(validation.isolated_two_build_byte_identity.file_count, 13);

assert.equal(sourceLock.schema, 'c120-source-lock/1');
assert.equal(sourceLock.course_id, 'C120');
assert.equal(sourceLock.native_role_id, 'O005');
assert.equal(sourceLock.native_repository.frozen_backend_commit, '1f7e7c9a180f450d91352d1b117094f07f1158ae');
assert.equal(sourceLock.native_repository.current_public_head, '1a5958db5d04eef5fba23af69913b6b1272939a9');
assert.equal(sourceLock.native_repository.current_public_tree, '487ac640e12680039d6e80faca7366240f748065');
assert.equal(sourceLock.native_repository.current_backend_tree, 'b19efc503a4544135337ff75cf622b1daac4eefa');
assert.equal(sourceLock.backend_integrity.files, 81);
assert.equal(sourceLock.backend_integrity.all_file_hashes_verified, true);
assert.equal(sourceLock.native_inputs.length, 15);
assert.equal(sourceLock.migration_input.path, 'backend/migrations/o005-c120-id-v1/MIGRATION_RECEIPT.json');
assert.deepEqual([...sourceLock.native_inputs, sourceLock.migration_input], manifest.inputs);

assert.equal(learningMap.schema, 'c120-learning-map/1');
assert.equal(learningMap.contract, manifest.contract);
assert.equal(learningMap.course_id, 'C120');
assert.equal(learningMap.locale, 'id-ID');
assert.equal(learningMap.units.length, 26);
assert.equal(new Set(learningMap.route.unit_ids).size, 26);
assert.equal(learningMap.units.filter(row => row.origin_kind === 'source_derived_translation').length, 22);
assert.equal(learningMap.units.filter(row => row.origin_kind === 'independent_supplement').length, 4);
assert.equal(learningMap.units.flatMap(row => row.problem_ids).length, 141);
assert.equal(new Set(learningMap.units.flatMap(row => row.problem_ids)).size, 141);
assert.deepEqual(learningMap.program_prerequisites, ['B70', 'B80', 'C10']);
assert.equal(learningMap.prerequisite_scope, 'central_course_level_only_not_native_per_unit_claims');

assert.equal(educatorMap.schema, 'c120-educator-map/1');
assert.equal(educatorMap.course_id, 'C120');
assert.equal(educatorMap.selector.selected_units.length, 26);
assert.equal(educatorMap.selector.projects.length, 12);
assert.equal(educatorMap.selector.body_content_embedded, false);
assert.equal(educatorMap.claim_boundary.mastery_problem_support_records, 141);
assert.equal(educatorMap.claim_boundary.worked_solution_records, 126);
assert.equal(educatorMap.claim_boundary.qualitative_rubrics, 14);
assert.equal(educatorMap.claim_boundary.worked_classifications, 1);
assert.equal(educatorMap.claim_boundary.project_result_reproduction_claimed, false);

assert.equal(ledgers.schema, 'c120-ledger-references/1');
assert.equal(ledgers.backend_integrity.files, 81);
assert.equal(ledgers.backend_integrity.bytes, 3270308);
assert.equal(ledgers.backend_integrity.all_file_hashes_verified, true);
assert.equal(ledgers.common_projection.record_count, 16029);
assert.equal(ledgers.common_projection.exact_native_logical_record_reverse_extraction, 4941);
assert.equal(ledgers.common_projection.two_independent_assemblies, 'byte-identical');
assert.equal(ledgers.historical_control_boundary.backend_tree_unchanged, true);
assert.equal(ledgers.source_target_unit_hashes.length, 26);
assert.equal(ledgers.projects.length, 12);
assert.equal(ledgers.projection.native_bodies_copied, false);
assert.equal(ledgers.projection.common_virtual_backend_materialized, false);

assert.equal(publicEvidence.schema, 'c120-public-evidence/1');
assert.equal(publicEvidence.github.current_public_head, sourceLock.native_repository.current_public_head);
assert.equal(publicEvidence.github.current_backend_tree, sourceLock.native_repository.current_backend_tree);
assert.equal(publicEvidence.github.anonymous_verification, 'verified_by_frozen_handoff');
assert.equal(publicEvidence.zenodo.record_id, 22070943);
assert.equal(publicEvidence.zenodo.doi, '10.5281/zenodo.22070943');
assert.equal(publicEvidence.zenodo.concept_doi, '10.5281/zenodo.22059939');
assert.equal(publicEvidence.zenodo.anonymous_verification, 'verified');
assert.equal(publicEvidence.zenodo.release_assets.length, 6);
assert.equal(publicEvidence.reader.online_html, true);
assert.equal(publicEvidence.reader.online_routes, 26);
assert.equal(publicEvidence.reader.pdf_pages, 355);
assert.equal(publicEvidence.reader.tagged_pdf, true);
assert.equal(publicEvidence.public_state_changed, false);

assert.equal(rightsAndTerms.schema, 'c120-rights-and-terms/1');
assert.equal(rightsAndTerms.component_boundaries.length, 4);
assert.equal(rightsAndTerms.terminology.length, 321);
assert.equal(rightsAndTerms.terminology_status_counts.admitted, 320);
assert.equal(rightsAndTerms.terminology_status_counts.provisional, 1);
assert.deepEqual(rightsAndTerms.terminology_csv_normalizations, [
  {action: 'joined_unquoted_comma_into_final_field', term_id: 'O005-TERM-0271'},
]);
assert.equal(rightsAndTerms.corrections.length, 160);
assert.equal(rightsAndTerms.blanket_license_claimed, false);
assert.deepEqual(claimBoundary, capabilities.claim_boundary);
for (const key of ['learner_attempt_instances', 'learner_submission_instances', 'learner_result_instances', 'credential_assertion_instances']) {
  assert.equal(claimBoundary[key], 0);
}
assert.equal(claimBoundary.mastery_problem_support_records, 141);
assert.equal(claimBoundary.project_result_reproduction_claimed, false);
assert.equal(claimBoundary.native_bodies_copied, false);
assert.equal(claimBoundary.common_virtual_backend_materialized, false);

for (const item of manifest.outputs) {
  assert.deepEqual(await identity(`${base}/${item.path}`), {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256});
}

const publicMappings = [
  [`${base}/views/C120.html`, 'docs/backend/c120/C120.html'],
  [`${base}/views/C120-pengajar.html`, 'docs/backend/c120/C120-pengajar.html'],
  [`${base}/data/learning-map.json`, 'docs/backend/c120/learning-map.json'],
  [`${base}/data/educator-map.json`, 'docs/backend/c120/educator-map.json'],
  [`${base}/data/rights-and-terms.json`, 'docs/backend/c120/rights-and-terms.json'],
  [`${base}/data/ledger-references.json`, 'docs/backend/c120/ledger-references.json'],
  [`${base}/validation.json`, 'docs/backend/c120/validation.json'],
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
  ['native_and_migration_source_lock', `${base}/input/source-lock.json`],
  ['verified_native_public_release', `${base}/data/public-evidence.json`],
  ['component_rights_terminology_and_corrections', `${base}/data/rights-and-terms.json`],
  ['native_and_reversible_migration_ledgers', `${base}/data/ledger-references.json`],
]) {
  const {bytes, sha256} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-05'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
assert.ok(!overrides.semantic_adapters.C120 || !overrides.semantic_adapters.C120.contract_version || overrides.semantic_adapters.C120.contract_version === manifest.contract, 'Preserve a different admitted C120 contract');
overrides.semantic_adapters.C120 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_26_native_units_4105_segments_141_mastery_problems_26_notebooks_12_projects_321_terms_160_corrections_and_existing_4941_record_reversible_migration',
  evidence,
};

overrides.native_capabilities.C120 = {...(overrides.native_capabilities.C120 ?? {})};
for (const capability of ['unit_identity', 'terminology', 'translation_rights', 'corrections', 'build', 'deterministic_replay', 'educator_unit_alignment', 'translation_ledger']) {
  overrides.native_capabilities.C120[capability] = {status: 'verified', evidence};
}

const scope = 'Dua puluh enam unit, 4.105 segmen, 141 masalah penguasaan, 26 notebook, 12 paket proyek, 321 baris istilah, 160 koreksi, dan proyeksi reversibel 4.941 rekaman native.';
const limitations = [
  'Adapter adalah proyeksi metadata dan bukti zero-copy; isi buku, notebook, proyek, PDF, dan pembaca HTML tetap pada edisi publik native.',
  'Dua puluh dua unit terjemahan sumber dan empat modul jembatan orisinal tetap dibedakan.',
  'Dukungan 141 masalah terdiri dari 126 solusi tertulis, 14 rubrik kualitatif, dan satu klasifikasi terbimbing; tipe dukungan tidak diratakan.',
  'Dua belas notebook proyek adalah paket awal dan tidak mengklaim reproduksi hasil artikel yang dirujuk.',
  'Prasyarat B70, B80, dan C10 adalah relasi tingkat kursus pusat, bukan graf prasyarat per unit native.',
  'Proyeksi umum 16.029 rekaman tetap virtual; backend native 81 berkas tidak disalin ke badan kapsul.',
  'Satu catatan TERMINOLOGY.csv dengan koma tanpa kutip dinormalisasi deterministik pada adapter; berkas native dan hash-nya tidak diubah.',
];
const tool = {
  tool_id: 'c120.open_learner_hub',
  label: 'C120 · Pemodelan dan Dinamika Nonlinear',
  href: 'backend/c120/C120.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/c120/C120.html'),
  resource: await identity('docs/backend/c120/learning-map.json'),
  evidence: await identity('docs/backend/c120/validation.json'),
  limitations,
};
assert.ok(!overrides.learner_tools.C120 || overrides.learner_tools.C120.every(old => old.tool_id === tool.tool_id), 'Preserve unrelated C120 tools');
overrides.learner_tools.C120 = [tool];

const teacher = await identity('docs/backend/c120/C120-pengajar.html');
const educatorMapIdentity = await identity('docs/backend/c120/educator-map.json');
const educatorUrl = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c120/C120-pengajar.html';
const resources = (overrides.educator_evidence.C120?.resources ?? []).filter(resource => !['C120:educator-hub-v1', 'C120:educator-map-v1'].includes(resource.id));
resources.push({
  id: 'C120:educator-hub-v1',
  title: 'Pemilih unit, masalah, dan proyek C120 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url: educatorUrl,
  scope: `${scope} Ekspor JSON mempertahankan tipe dukungan dan batas proyek tanpa menyalin badan buku.`,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
resources.push({
  id: 'C120:educator-map-v1',
  title: 'Peta unit, penguasaan, notebook, dan proyek C120',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c120/educator-map.json',
  scope: 'Data pemilih 26 unit, 141 masalah, dan 12 proyek dengan identitas native serta batas klaim eksplisit.',
  bytes: educatorMapIdentity.bytes,
  sha256: educatorMapIdentity.sha256,
});
overrides.educator_evidence.C120 = {
  status: 'verified',
  verified_date: '2026-09-05',
  locator: educatorUrl,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: ['lesson_sequences', 'exercise_bank', 'activities_labs', 'remix_selectors', 'solution_provenance', 'accessibility_accommodations'],
  resources,
};

await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);
console.log(JSON.stringify({state: 'pass', admitted_roles: ['C120'], contract: manifest.contract, native_locale: manifest.locale, public_state_changed: false}));
