import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/a30-capability-v1';
const load = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const identity = async path => {
  const bytes = await readFile(resolve(root, path));
  return {path, bytes: bytes.length, sha256: digest(bytes)};
};
const bufferIdentity = (path, bytes) => ({path, bytes: bytes.length, sha256: digest(bytes)});

const manifest = await load(`${base}/manifest.json`);
const validation = await load(`${base}/validation.json`);
const packageReceipt = await load(`${base}/build/PACKET_BUILD_RECEIPT.json`);
const sourceLock = await load(`${base}/input/source-lock.json`);
const publicReadback = await load(`${base}/input/public-native-readback.json`);
const capabilities = await load(`${base}/data/capabilities.json`);
const learningMap = await load(`${base}/data/learner-map.json`);
const educatorMap = await load(`${base}/data/educator-map.json`);
const publicEvidence = await load(`${base}/data/public-evidence.json`);
const claimBoundary = await load(`${base}/data/claim-boundary.json`);

assert.equal(manifest.schema, 'a30-capability-manifest/1');
assert.equal(manifest.course_id, 'A30');
assert.equal(manifest.native_course_id, 'urn:interlanguage:course:A30');
assert.equal(manifest.native_family, 'openstax_precalculus_2e');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.content_policy, 'native_identity_structure_status_rights_evidence_only_no_source_target_or_body_text');
assert.equal(manifest.canonical_jsonl_sha256, '4f2f51457adde0516c17b1633327a3bfbbf273a67925514bbb6c390f5e58a054');
assert.equal(manifest.outputs.length, 48);
assert.deepEqual(manifest.inputs, sourceLock.inputs);
assert.deepEqual(manifest.projection, {
  central_course_truth_rewritten: false,
  component_rights_preserved: true,
  exercise_solution_boundary_preserved: true,
  external_hash_pinned_public_backend_required_for_replay: true,
  native_bodies_copied: false,
  native_ids_preserved: true,
  public_state_changed: false,
  reversible_exchange_claimed: false,
  segment_state_asymmetry_preserved: true,
  source_companion_required_for_full_replay: true,
  source_or_target_text_copied: false,
  standalone_raw_replay_claimed: false,
});
assert.deepEqual(manifest.public_release, {
  complete: true,
  final_derivative_commit: null,
  final_derivative_revision_proved: false,
  final_derivative_tree: null,
  tag: 'v1.0.0',
});
assert.deepEqual(manifest.upstream_source, {
  commit: '789b54099106b071d1d32bfcee454fed72eb4768',
  tree: '05b39123f698772482c0c33a43fa2d2d4ea562ae',
});

const counts = manifest.counts;
for (const [key, expected] of Object.entries({
  native_records: 220680,
  units: 26965,
  chapters: 12,
  modules: 87,
  pdf_pages: 3165,
  segments: 149955,
  exercises: 7250,
  problems: 7250,
  solution_identities: 4183,
  unsupported_exercises: 3067,
  concepts: 497,
  terms: 513,
  corrections: 703,
  component_rights: 1875,
  relations: 37974,
})) assert.equal(counts[key], expected, `A30 count drift: ${key}`);
assert.deepEqual(counts.native_record_entities, {
  artifact: 14, asset: 2162, concept: 497, correction: 703, course: 1,
  edition: 1, program: 1, qa_event: 18, relation: 37974, resource: 1,
  rights: 1875, segment: 149955, term: 513, unit: 26965,
});
assert.deepEqual(counts.unit_kinds, {
  chapter: 12, collection: 1, commentary: 181, definition: 318,
  equation: 2037, example: 725, exercise: 7250, figure: 868, list: 1094,
  module: 87, note: 1174, problem: 7250, section: 1340, solution: 4183,
  table: 445,
});
assert.deepEqual(counts.relation_kinds, {
  contains: 26865, 'depends-on': 2174, 'derived-from': 278,
  'derived-from-source-data': 1, describes: 2611,
  'rights-replacement': 10, solves: 4183, xref: 1852,
});
assert.deepEqual(counts.segment_state_counts, {source_frozen: 99938, superseded: 6, translated: 50011});
assert.deepEqual(counts.segment_state_bucket_counts, {
  'en|source_frozen|active': 49969,
  'en|superseded|retired': 2,
  'id-ID|superseded|retired': 2,
  'id-ID|translated|active': 49990,
  'und|source_frozen|active': 49969,
  'und|superseded|retired': 2,
  'und|translated|active': 21,
});
assert.deepEqual(counts.term_decision_statuses, {
  accepted: 498, accepted_initial: 9, provisional: 4, superseded: 2,
});
assert.deepEqual(counts.correction_statuses, {
  accepted: 19,
  blocked_out_of_scope: 1,
  candidate_preserved: 32,
  corrected_in_partial_target: 11,
  corrected_in_target: 443,
  excluded_inactive_comment_only: 1,
  frozen: 10,
  normalized_in_translation: 186,
});
assert.deepEqual(counts.rights_admission_counts, {None: 2, admitted: 1835, quarantined: 38});
for (const item of manifest.outputs) {
  assert.deepEqual(
    await identity(`${base}/${item.path}`),
    {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256},
  );
}

assert.equal(validation.schema, 'a30-capability-validation/1');
assert.equal(validation.result, 'pass');
assert.equal(validation.course_id, 'A30');
assert.deepEqual(validation.counts, counts);
assert.equal(validation.negative_fixtures.length, 27);
assert.ok(validation.negative_fixtures.every(row => row.result === 'rejected'));
assert.equal(validation.final_derivative_revision_proved, false);
assert.equal(validation.checks.canonical_machine_files, true);
assert.equal(validation.checks.committed_projection_matches_public_native, true);
assert.equal(validation.checks.component_specific_rights_preserved, true);
assert.equal(validation.checks.exercise_problem_identity_bijection, 7250);
assert.equal(validation.checks.exercise_pdf_destinations_not_indexed, true);
assert.equal(validation.checks.final_derivative_git_commit_or_tree_not_claimed, true);
assert.deepEqual(validation.checks.solution_identity_boundary_preserved, {
  with_solution_identity: 4183,
  without_native_solution_support: 3067,
});
assert.deepEqual(validation.checks.segment_state_asymmetry_preserved, counts.segment_state_bucket_counts);
assert.equal(validation.checks.source_target_and_body_text_absent, true);
assert.equal(validation.checks.standalone_raw_replay_not_claimed, true);
assert.equal(validation.checks.public_source_receipt_state, 'pass');
assert.equal(validation.checks.public_source_assets, 7);
assert.equal(validation.checks.public_zenodo_assets, 7);
assert.equal(validation.checks.module_identities_rendered_for_learner, 87);
assert.equal(validation.checks.module_identities_rendered_for_educator, 87);
assert.equal(validation.checks.two_run_build_identity.file_count, 49);
assert.equal(validation.checks.two_run_build_identity.tree_sha256, '51b3c1cf9f3709a540fe59c9df63b186968ceb6c41fccce265c504bf970244cd');

assert.equal(packageReceipt.schema, 'a30-capability-thin-packet-build-receipt/1');
assert.equal(packageReceipt.result, 'PASS');
assert.equal(packageReceipt.two_build_byte_identity, true);
assert.equal(packageReceipt.negative_fixtures_included, 27);
assert.equal(packageReceipt.native_inputs_included, 0);
assert.equal(packageReceipt.native_content_bodies_included, false);
assert.equal(packageReceipt.exercise_or_solution_bodies_included, false);
assert.equal(packageReceipt.exercise_pdf_destinations_included, false);
assert.equal(packageReceipt.source_or_target_text_included, false);
assert.equal(packageReceipt.forbidden_payloads_included, false);
assert.equal(packageReceipt.local_profile_data_included, false);
assert.equal(packageReceipt.external_hash_pinned_public_backend_required_for_replay, true);
assert.equal(packageReceipt.source_companion_required_for_full_replay, true);
assert.equal(packageReceipt.standalone_raw_replay_claimed, false);
assert.equal(packageReceipt.final_derivative_revision_proved, false);
assert.equal(packageReceipt.reversible_exchange_claimed, false);
assert.equal(packageReceipt.public_state_changed, false);
assert.deepEqual(packageReceipt.adapter_manifest, {...(await identity(`${base}/manifest.json`)), path: 'manifest.json'});
assert.deepEqual(packageReceipt.adapter_validation, {...(await identity(`${base}/validation.json`)), path: 'validation.json'});
assert.deepEqual(packageReceipt.archive, {...(await identity(`${base}/build/A30_THIN_CAPABILITY_METADATA_V1.zip`)), path: 'build/A30_THIN_CAPABILITY_METADATA_V1.zip'});
assert.deepEqual(packageReceipt.zip_checks, {
  crc_and_full_entry_readback: true,
  fixed_member_metadata: true,
  member_count: 57,
  payload_bytes: 26656051,
  sorted_member_order: true,
});

assert.equal(sourceLock.schema, 'a30-capability-source-lock/1');
assert.equal(sourceLock.course_id, 'A30');
assert.equal(sourceLock.native_course_id, 'urn:interlanguage:course:A30');
assert.equal(sourceLock.inputs.length, 8);
assert.equal(sourceLock.native_export.record_count, 220680);
assert.equal(sourceLock.native_export.jsonl_sha256, manifest.canonical_jsonl_sha256);
assert.equal(sourceLock.native_export.canonical_member.bytes, 426073883);
assert.equal(sourceLock.native_export.container.bytes, 97424500);
assert.equal(sourceLock.native_export.source_companion_required_for_full_replay, true);
assert.equal(sourceLock.native_export.standalone_full_raw_replay_claimed, false);
assert.deepEqual(sourceLock.indonesian_release, {
  complete_public_edition: true,
  final_derivative_commit: null,
  final_derivative_revision_proved: false,
  final_derivative_tree: null,
  repository: 'https://github.com/KokunoYumeto/openstax-precalculus-2e-id',
  tag: 'v1.0.0',
  zenodo_concept_id: 22059757,
  zenodo_record_id: 22290180,
});
assert.deepEqual(sourceLock.upstream_source, {
  commit: '789b54099106b071d1d32bfcee454fed72eb4768',
  repository: 'https://github.com/openstax/osbooks-college-algebra-bundle',
  tree: '05b39123f698772482c0c33a43fa2d2d4ea562ae',
});

assert.equal(publicReadback.schema, 'a30-native-public-readback/1');
assert.equal(publicReadback.state, 'pass');
assert.equal(publicReadback.anonymous, true);
assert.equal(publicReadback.credentials_used, false);
assert.deepEqual(publicReadback.failures, []);
assert.equal(publicReadback.native_backend.records, 220680);
assert.equal(publicReadback.native_backend.unique_ids, 220680);
assert.equal(publicReadback.native_backend.modules, 87);
assert.equal(publicReadback.native_backend.chapters, 12);
assert.equal(publicReadback.native_backend.pages, 3165);
assert.equal(publicReadback.repository.public, true);
assert.equal(publicReadback.repository.tag, 'v1.0.0');
assert.equal(publicReadback.repository.final_derivative_revision_proved, false);
assert.equal(publicReadback.repository.final_derivative_commit, null);
assert.equal(publicReadback.repository.final_derivative_tree, null);
assert.equal(publicReadback.github_release.assets.length, 7);
assert.equal(publicReadback.zenodo.assets.length, 7);
assert.equal(publicReadback.github_release.total_bytes, 499884557);
assert.equal(publicReadback.zenodo.total_bytes, 499884557);
assert.equal(publicReadback.zenodo.access_right, 'open');

assert.equal(capabilities.schema, 'a30-capabilities/1');
assert.equal(capabilities.contract, manifest.contract);
assert.equal(capabilities.native_role_id, 'R002');
assert.deepEqual(capabilities.counts, counts);
assert.deepEqual(capabilities.curriculum_graph.prerequisite_course_ids, ['A20']);
assert.deepEqual(capabilities.curriculum_graph.native_prerequisite_ids, []);
assert.equal(capabilities.curriculum_graph.prerequisite_authority, 'central_curriculum_overlay');
assert.equal(capabilities.curriculum_graph.chapter_module_count, 85);
assert.equal(capabilities.curriculum_graph.collection_level_front_matter_module_count, 1);
assert.equal(capabilities.curriculum_graph.collection_level_back_matter_module_count, 1);
assert.equal(capabilities.learner_delivery.module_navigation, true);
assert.equal(capabilities.learner_delivery.partial_solution_identity_coverage, true);
assert.equal(capabilities.learner_delivery.exercise_pdf_destinations_indexed, false);
assert.equal(capabilities.learner_delivery.indonesian_semantic_html, false);
assert.equal(capabilities.educator_delivery.module_selector, true);
assert.equal(capabilities.educator_delivery.segment_state_asymmetry_summary, true);
assert.equal(capabilities.educator_delivery.official_teacher_manual, false);
assert.equal(capabilities.federation.stable_native_ids_preserved, true);
assert.equal(capabilities.federation.body_content_embedded, false);
assert.equal(capabilities.federation.source_or_target_text_embedded, false);
assert.equal(capabilities.federation.source_companion_required_for_full_replay, true);
assert.equal(capabilities.federation.standalone_raw_replay_claimed, false);
assert.equal(capabilities.federation.reversible_exchange_claimed, false);

assert.equal(learningMap.schema, 'a30-learner-map/1');
assert.equal(learningMap.course_id, 'A30');
assert.equal(learningMap.locale, 'id-ID');
assert.equal(learningMap.modules.length, 87);
assert.equal(learningMap.front_matter_modules.length, 1);
assert.equal(learningMap.back_matter_modules.length, 1);
assert.equal(learningMap.chapters.length, 12);
assert.equal(learningMap.exercise_identity_count, 7250);
assert.equal(learningMap.solution_identity_count, 4183);
assert.equal(learningMap.unsupported_exercise_count, 3067);
assert.equal(learningMap.indonesian_reader.pdf_pages, 3165);
assert.equal(learningMap.indonesian_reader.module_page_routes, true);
assert.equal(learningMap.indonesian_reader.exercise_pdf_destinations_indexed, false);
assert.equal(learningMap.indonesian_reader.semantic_html, false);
assert.equal(learningMap.indonesian_reader.mathml, false);
assert.equal(learningMap.prerequisite.authority, 'central_curriculum_overlay');
assert.equal(learningMap.prerequisite.native_source_assertion, false);
assert.equal(learningMap.body_content_embedded, false);
assert.equal(learningMap.source_or_target_text_embedded, false);

assert.equal(educatorMap.schema, 'a30-educator-map/1');
assert.equal(educatorMap.course_id, 'A30');
assert.equal(educatorMap.locale, 'id-ID');
assert.equal(educatorMap.selectable_modules.length, 87);
assert.equal(educatorMap.front_matter_modules.length, 1);
assert.equal(educatorMap.back_matter_modules.length, 1);
assert.equal(educatorMap.chapter_summaries.length, 12);
assert.equal(educatorMap.exercise_identity_count, 7250);
assert.equal(educatorMap.solution_identity_count, 4183);
assert.equal(educatorMap.unsupported_exercise_count, 3067);
assert.equal(educatorMap.official_teacher_manual_claimed, false);
assert.equal(educatorMap.solution_bodies_embedded, false);
assert.equal(educatorMap.body_content_embedded, false);
assert.equal(educatorMap.source_or_target_text_embedded, false);

assert.equal(publicEvidence.schema, 'a30-public-evidence/1');
assert.equal(publicEvidence.course_id, 'A30');
assert.equal(publicEvidence.anonymous_readback, true);
assert.equal(publicEvidence.credentials_used, false);
assert.equal(publicEvidence.repository.tag, 'v1.0.0');
assert.equal(publicEvidence.repository.final_derivative_revision_proved, false);
assert.equal(publicEvidence.indonesian_reader.pdf_pages, 3165);
assert.equal(publicEvidence.indonesian_reader.semantic_html, false);
assert.equal(publicEvidence.indonesian_reader.mathml, false);
assert.equal(publicEvidence.indonesian_reader.pdf_ua_certified, false);
assert.equal(publicEvidence.indonesian_reader.exercise_pdf_destinations_indexed, false);
assert.equal(publicEvidence.zenodo.record_id, 22290180);
assert.equal(publicEvidence.zenodo.concept_id, 22059757);
assert.equal(publicEvidence.zenodo.access_right, 'open');

assert.equal(claimBoundary.schema, 'a30-claim-boundary/1');
assert.equal(claimBoundary.course_id, 'A30');
for (const key of [
  'native_bodies_copied', 'all_exercises_claimed_solved',
  'native_course_prerequisites_invented', 'exhaustive_exercise_pdf_destinations_claimed',
  'final_derivative_git_revision_claimed', 'indonesian_semantic_html_claimed',
  'indonesian_mathml_claimed', 'epub_claimed', 'portable_offline_html_claimed',
  'pdf_ua_claimed', 'wcag_conformance_claimed', 'interactive_labs_claimed',
  'learning_runtime_claimed', 'official_teacher_manual_claimed',
  'standalone_raw_replay_claimed', 'reversible_exchange_claimed',
  'public_access_state_changed',
]) assert.equal(claimBoundary[key], false, `A30 false-claim boundary drift: ${key}`);
for (const key of [
  'source_segment_text_copied', 'target_segment_text_copied',
  'term_source_text_copied', 'term_target_text_copied',
  'correction_source_or_target_text_copied', 'exercise_or_problem_bodies_copied',
  'solution_bodies_copied', 'learner_result_instances',
]) assert.equal(claimBoundary[key], 0, `A30 zero-copy boundary drift: ${key}`);
assert.equal(claimBoundary.unsupported_exercises_preserved, 3067);
assert.equal(claimBoundary.central_a20_prerequisite_is_overlay, true);
assert.equal(claimBoundary.segment_state_asymmetry_preserved, true);

const publicMappings = [
  [`${base}/views/A30.html`, 'docs/backend/a30/A30.html'],
  [`${base}/views/A30-pengajar.html`, 'docs/backend/a30/A30-pengajar.html'],
  [`${base}/views/capabilities.json`, 'docs/backend/a30/capabilities.json'],
  [`${base}/data/learner-map.json`, 'docs/backend/a30/learning-map.json'],
  [`${base}/data/educator-map.json`, 'docs/backend/a30/educator-map.json'],
  [`${base}/data/public-evidence.json`, 'docs/backend/a30/public-evidence.json'],
  [`${base}/data/claim-boundary.json`, 'docs/backend/a30/claim-boundary.json'],
  [`${base}/data/native-record-ledger.json`, 'docs/backend/a30/data/native-record-ledger.json'],
  [`${base}/data/chapter-index.jsonl`, 'docs/backend/a30/data/chapter-index.jsonl'],
  [`${base}/data/module-index.jsonl`, 'docs/backend/a30/data/module-index.jsonl'],
  [`${base}/data/exercise-index.jsonl`, 'docs/backend/a30/data/exercise-index.jsonl'],
  [`${base}/data/concept-index.jsonl`, 'docs/backend/a30/data/concept-index.jsonl'],
  [`${base}/data/pedagogical-relation-index.jsonl`, 'docs/backend/a30/data/pedagogical-relation-index.jsonl'],
  [`${base}/data/terms-index.jsonl`, 'docs/backend/a30/data/terms-index.jsonl'],
  [`${base}/data/corrections-index.jsonl`, 'docs/backend/a30/data/corrections-index.jsonl'],
  [`${base}/data/rights-index.jsonl`, 'docs/backend/a30/data/rights-index.jsonl'],
  [`${base}/data/segment-state-summary.json`, 'docs/backend/a30/data/segment-state-summary.json'],
  [`${base}/input/source-lock.json`, 'docs/backend/a30/source-lock.json'],
  [`${base}/input/public-native-readback.json`, 'docs/backend/a30/public-native-readback.json'],
  [`${base}/validation.json`, 'docs/backend/a30/validation.json'],
];
const staged = new Map();
for (const [source, target] of publicMappings) {
  let bytes = await readFile(resolve(root, source));
  if (target === 'docs/backend/a30/A30-pengajar.html') {
    const original = bytes.toString('utf8');
    assert.equal((original.match(/\.\.\/data\//g) ?? []).length, 8);
    const projected = original.replaceAll('../data/', 'data/');
    assert.equal(projected.includes('../data/'), false);
    bytes = Buffer.from(projected, 'utf8');
  }
  staged.set(target, bytes);
}
const stagedIdentity = path => {
  const bytes = staged.get(path);
  assert.ok(bytes, `Missing staged A30 file: ${path}`);
  return bufferIdentity(path, bytes);
};

const evidence = [];
for (const [kind, path] of [
  ['central_adapter_manifest', `${base}/manifest.json`],
  ['deterministic_validation_receipt', `${base}/validation.json`],
  ['native_source_lock', `${base}/input/source-lock.json`],
  ['anonymous_native_public_readback', `${base}/input/public-native-readback.json`],
  ['verified_native_public_release', `${base}/data/public-evidence.json`],
  ['native_record_ledger', `${base}/data/native-record-ledger.json`],
  ['chapter_identity_index', `${base}/data/chapter-index.jsonl`],
  ['module_identity_index', `${base}/data/module-index.jsonl`],
  ['exercise_solution_identity_index', `${base}/data/exercise-index.jsonl`],
  ['concept_index', `${base}/data/concept-index.jsonl`],
  ['pedagogical_relation_index', `${base}/data/pedagogical-relation-index.jsonl`],
  ['component_rights_index', `${base}/data/rights-index.jsonl`],
  ['correction_index', `${base}/data/corrections-index.jsonl`],
  ['terminology_index', `${base}/data/terms-index.jsonl`],
  ['segment_state_summary', `${base}/data/segment-state-summary.json`],
]) {
  const {bytes, sha256} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-07'});
}

const scope = 'Sebanyak 220.680 rekaman native, 87 modul, 7.250 identitas latihan/masalah, 4.183 identitas solusi, 497 konsep, 513 istilah, 703 koreksi, dan 1.875 rekaman hak komponen.';
const limitations = [
  'Adapter adalah proyeksi identitas, struktur, status, hak, dan bukti zero-copy; badan buku, segmen sumber/target, latihan, masalah, dan solusi tetap pada edisi native publik.',
  'Hanya 4.183 dari 7.250 latihan memiliki identitas solusi; 3.067 kasus tanpa dukungan solusi native dipertahankan dan tidak diisi atau disamarkan.',
  'Rute 87 modul menunjuk halaman pembuka PDF; tujuan PDF per latihan tidak tersedia dan tidak diklaim.',
  'Pembaca Bahasa Indonesia berbasis PDF. HTML semantik, MathML, EPUB, paket HTML luring, PDF/UA, dan kepatuhan WCAG tidak diklaim.',
  'Prasyarat A20 adalah lapisan kurikulum pusat, bukan klaim prasyarat dari ekspor native.',
  'Komponen hak tetap terpisah: 1.835 admitted, 38 quarantined, dan dua tanpa status admission; tidak ada lisensi selimut yang diciptakan.',
  'Status segmen bahasa dan status istilah/koreksi dipertahankan apa adanya; teks sumber, teks target, dan badan koreksi tidak disalin.',
  'Paket sumber pendamping diperlukan untuk replay raw penuh. Pertukaran reversibel, replay raw mandiri, revisi Git final derivatif, laboratorium, runtime, dan manual pengajar resmi tidak diklaim.',
];

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
overrides.semantic_adapters ??= {};
overrides.native_capabilities ??= {};
overrides.learner_tools ??= {};
overrides.educator_evidence ??= {};
assert.ok(
  !overrides.semantic_adapters.A30
    || !overrides.semantic_adapters.A30.contract_version
    || overrides.semantic_adapters.A30.contract_version === manifest.contract,
  'Preserve a different admitted A30 contract',
);
overrides.semantic_adapters.A30 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_220680_native_records_87_modules_7250_exercise_problem_identities_4183_solution_identities_497_concepts_513_terms_703_corrections_1875_component_rights_and_segment_state_asymmetry_with_3067_unsupported_solution_cases_preserved',
  evidence,
};
overrides.native_capabilities.A30 = {...(overrides.native_capabilities.A30 ?? {})};
for (const capability of [
  'unit_identity', 'terminology', 'translation_rights', 'corrections',
  'build', 'deterministic_replay', 'educator_unit_alignment', 'translation_ledger',
]) overrides.native_capabilities.A30[capability] = {status: 'verified', evidence};

const tool = {
  tool_id: 'a30.open_learner_hub',
  label: 'A30 · Prakalkulus dan Trigonometri',
  href: 'backend/a30/A30.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: stagedIdentity('docs/backend/a30/A30.html'),
  resource: stagedIdentity('docs/backend/a30/learning-map.json'),
  evidence: stagedIdentity('docs/backend/a30/validation.json'),
  limitations,
};
assert.ok(
  !overrides.learner_tools.A30
    || overrides.learner_tools.A30.every(old => old.tool_id === tool.tool_id),
  'Preserve unrelated A30 learner tools',
);
overrides.learner_tools.A30 = [tool];

const educatorUrl = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/a30/A30-pengajar.html';
const managedResourceIds = new Set([
  'A30:educator-hub-v1', 'A30:educator-map-v1', 'A30:chapter-index-v1',
  'A30:module-index-v1', 'A30:exercise-index-v1', 'A30:concept-index-v1',
  'A30:relation-index-v1', 'A30:terms-index-v1', 'A30:rights-index-v1',
  'A30:corrections-index-v1', 'A30:segment-state-summary-v1',
  'A30:native-record-ledger-v1',
]);
const resources = (overrides.educator_evidence.A30?.resources ?? [])
  .filter(resource => !managedResourceIds.has(resource.id));
const teacher = stagedIdentity('docs/backend/a30/A30-pengajar.html');
resources.push({
  id: 'A30:educator-hub-v1',
  title: 'Pemilih bab, modul, latihan, dan cakupan solusi A30 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url: educatorUrl,
  scope,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
resources.push({
  id: 'A30:educator-map-v1',
  title: 'Peta pengajar atas 87 modul native A30',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/a30/educator-map.json',
  scope: 'Peta zero-copy atas modul, rute halaman, latihan, konsep, istilah, koreksi, hak, status segmen, dan batas cakupan solusi.',
  bytes: stagedIdentity('docs/backend/a30/educator-map.json').bytes,
  sha256: stagedIdentity('docs/backend/a30/educator-map.json').sha256,
});
for (const [id, title, filename, resourceType] of [
  ['A30:chapter-index-v1', 'Indeks 12 bab A30', 'chapter-index.jsonl', 'identity-index'],
  ['A30:module-index-v1', 'Indeks 87 modul A30', 'module-index.jsonl', 'identity-index'],
  ['A30:exercise-index-v1', 'Indeks 7.250 latihan/masalah dan 4.183 solusi A30', 'exercise-index.jsonl', 'exercise-bank'],
  ['A30:concept-index-v1', 'Indeks 497 konsep A30', 'concept-index.jsonl', 'educator-data'],
  ['A30:relation-index-v1', 'Indeks 37.974 relasi pedagogis/native A30', 'pedagogical-relation-index.jsonl', 'educator-data'],
  ['A30:terms-index-v1', 'Indeks status 513 istilah A30', 'terms-index.jsonl', 'terminology-register'],
  ['A30:rights-index-v1', 'Indeks 1.875 rekaman hak komponen A30', 'rights-index.jsonl', 'rights-ledger'],
  ['A30:corrections-index-v1', 'Indeks status 703 koreksi A30', 'corrections-index.jsonl', 'correction-ledger'],
  ['A30:segment-state-summary-v1', 'Ringkasan status 149.955 segmen A30', 'segment-state-summary.json', 'translation-ledger'],
  ['A30:native-record-ledger-v1', 'Ledger 220.680 identitas native A30', 'native-record-ledger.json', 'identity-index'],
]) {
  const publicPath = `docs/backend/a30/data/${filename}`;
  const fact = stagedIdentity(publicPath);
  resources.push({
    id,
    title,
    resource_type: resourceType,
    status: 'verified',
    url: `https://kokunoyumeto.github.io/program-matematika-indonesia/backend/a30/data/${filename}`,
    scope: 'Indeks metadata native dengan identitas dan hash stabil; badan buku serta teks sumber/target tidak disalin.',
    bytes: fact.bytes,
    sha256: fact.sha256,
  });
}
overrides.educator_evidence.A30 = {
  status: 'verified',
  verified_date: '2026-09-07',
  locator: educatorUrl,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: ['lesson_sequences', 'exercise_bank', 'prerequisite_diagnostics', 'remix_selectors'],
  resources,
};

const learnerTarget = 'backend/authority/learner-delivery-overrides-v1.json';
const learner = await load(learnerTarget);
learner.courses ??= {};
const pdfAssets = publicEvidence.zenodo.assets.filter(({name}) => name === 'OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf');
assert.equal(pdfAssets.length, 1);
const pdfAsset = pdfAssets[0];
assert.equal(pdfAsset.bytes, 305654938);
assert.equal(pdfAsset.sha256, '3cfd5294b91252cc766992f158b6601e80aa31b719b0b8bf69e1ff6d08a4fa3e');
assert.equal(publicEvidence.indonesian_reader.url, 'https://zenodo.org/records/22290180/files/OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf?download=1');
const publicReceipt = {
  kind: 'anonymous_public_byte_readback',
  locator: `https://github.com/KokunoYumeto/program-matematika-indonesia/blob/main/${base}/data/public-evidence.json`,
  verified_date: '2026-09-07',
};
const pdf = {
  status: 'verified',
  format: 'application/pdf',
  url: publicEvidence.indonesian_reader.url,
  bytes: pdfAsset.bytes,
  sha256: pdfAsset.sha256,
  scope: 'whole_course_3165_pages_with_exact_module_page_routes_and_no_per_exercise_destinations',
  evidence: publicReceipt,
};
learner.courses.A30 = {
  ...(learner.courses.A30 ?? {}),
  primary: pdf,
  online_html: {status: 'not_yet_produced'},
  pdf,
  epub: {status: 'not_yet_produced'},
  portable_html: {status: 'not_yet_produced'},
  capabilities: {
    ...(learner.courses.A30?.capabilities ?? {}),
    semantic_html: {status: 'not_yet_produced'},
    mathml: {status: 'not_yet_produced'},
    print_profile: {status: 'verified', evidence: {...publicReceipt, pdf_pages: 3165}},
    chapter_downloads: {status: 'not_yet_produced'},
  },
};

for (const [path, bytes] of staged) {
  await mkdir(dirname(resolve(root, path)), {recursive: true});
  await writeFile(resolve(root, path), bytes);
  assert.deepEqual(await identity(path), bufferIdentity(path, bytes));
}
await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);
await writeFile(resolve(root, learnerTarget), `${JSON.stringify(learner, null, 2)}\n`);

console.log(JSON.stringify({
  state: 'pass',
  admitted_roles: ['A30'],
  contract: manifest.contract,
  native_locale: manifest.locale,
  public_files_staged: publicMappings.length,
  native_records: counts.native_records,
  modules: counts.modules,
  exercises: counts.exercises,
  solution_identities: counts.solution_identities,
  unsupported_exercises: counts.unsupported_exercises,
  public_state_changed: false,
}));
