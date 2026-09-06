import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/a20-capability-v1';
const load = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const identity = async path => {
  const data = await readFile(resolve(root, path));
  return {path, bytes: data.length, sha256: createHash('sha256').update(data).digest('hex')};
};

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

assert.equal(manifest.schema, 'a20-capability-manifest/1');
assert.equal(manifest.course_id, 'A20');
assert.equal(manifest.native_course_id, 'urn:uuid:ad0b27d0-84f4-5451-92f6-94872587ae53');
assert.equal(manifest.native_family, 'openstax_intermediate_algebra_2e');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.content_policy, 'identity_structure_terminology_rights_evidence_only');
assert.equal(manifest.outputs.length, 34);
assert.deepEqual(manifest.inputs, sourceLock.inputs);
assert.deepEqual(manifest.projection, {
  central_course_truth_rewritten: false,
  component_rights_preserved: true,
  exercise_solution_boundary_preserved: true,
  external_hash_pinned_native_export_required_for_replay: true,
  native_bodies_copied: false,
  native_ids_preserved: true,
  public_state_changed: false,
  reversible_exchange_claimed: false,
  stale_repository_landing_used_as_complete_authority: false,
});

const counts = manifest.counts;
assert.equal(counts.native_records, 174535);
assert.equal(counts.units, 57136);
assert.equal(counts.chapters, 12);
assert.equal(counts.modules, 83);
assert.equal(counts.pdf_pages, 3438);
assert.equal(counts.exercises, 8209);
assert.equal(counts.problems, 8209);
assert.equal(counts.solution_identities, 5238);
assert.equal(counts.unsolved_exercises, 2971);
assert.equal(counts.concepts, 236);
assert.equal(counts.terms, 340);
assert.equal(counts.corrections, 1614);
assert.equal(counts.component_rights, 17);
assert.equal(counts.relations, 77109);
assert.equal(counts.selected_pedagogical_relations, 32393);
assert.deepEqual(counts.correction_statuses, {applied: 1611, recorded_unmodified: 3});
assert.deepEqual(counts.term_statuses, {admitted: 340});
assert.deepEqual(counts.selected_pedagogical_relation_kinds, {
  contains: 21752,
  'has-solution': 5238,
  precedes: 82,
  solves: 5238,
  teaches: 83,
});
for (const item of manifest.outputs) {
  assert.deepEqual(
    await identity(`${base}/${item.path}`),
    {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256},
  );
}

assert.equal(validation.schema, 'a20-capability-validation/1');
assert.equal(validation.result, 'pass');
assert.equal(validation.course_id, 'A20');
assert.deepEqual(validation.counts, counts);
assert.equal(validation.negative_fixtures.length, 15);
assert.ok(validation.negative_fixtures.every(row => row.result === 'rejected'));
assert.equal(validation.checks.canonical_machine_files, true);
assert.equal(validation.checks.committed_projection_matches_native, true);
assert.equal(validation.checks.component_specific_rights_preserved, true);
assert.equal(validation.checks.exercise_problem_identity_bijection, 8209);
assert.deepEqual(validation.checks.solution_identity_boundary_preserved, {
  with_solution_identity: 5238,
  without_solution_identity: 2971,
});
assert.equal(validation.checks.native_bodies_absent, true);
assert.equal(validation.checks.public_source_receipt_state, 'pass');
assert.equal(validation.checks.public_source_assets, 8);
assert.equal(validation.checks.public_zenodo_assets, 8);
assert.equal(validation.checks.stale_repository_landing_bounded, true);
assert.equal(validation.checks.module_identities_rendered_for_learner, 83);
assert.equal(validation.checks.module_identities_rendered_for_educator, 83);
assert.equal(validation.checks.two_run_build_identity.file_count, 35);
assert.equal(validation.checks.two_run_build_identity.tree_sha256, 'c901a9fed2835538094b552b571c886ebe66c2b5519e30bfc32ad8afea818667');

assert.equal(packageReceipt.schema, 'a20-capability-thin-packet-build-receipt/1');
assert.equal(packageReceipt.result, 'PASS');
assert.equal(packageReceipt.two_build_byte_identity, true);
assert.equal(packageReceipt.negative_fixtures_included, 15);
assert.equal(packageReceipt.native_inputs_included, 0);
assert.equal(packageReceipt.native_content_bodies_included, false);
assert.equal(packageReceipt.exercise_or_solution_bodies_included, false);
assert.equal(packageReceipt.forbidden_payloads_included, false);
assert.equal(packageReceipt.local_profile_data_included, false);
assert.equal(packageReceipt.external_hash_pinned_native_export_required_for_replay, true);
assert.equal(packageReceipt.reversible_exchange_claimed, false);
assert.equal(packageReceipt.public_state_changed, false);
assert.deepEqual(packageReceipt.adapter_manifest, {...(await identity(`${base}/manifest.json`)), path: 'manifest.json'});
assert.deepEqual(packageReceipt.adapter_validation, {...(await identity(`${base}/validation.json`)), path: 'validation.json'});
assert.deepEqual(packageReceipt.archive, {...(await identity(`${base}/build/A20_THIN_CAPABILITY_METADATA_V1.zip`)), path: 'build/A20_THIN_CAPABILITY_METADATA_V1.zip'});
assert.deepEqual(packageReceipt.zip_checks, {
  crc_and_full_entry_readback: true,
  fixed_member_metadata: true,
  member_count: 43,
  payload_bytes: 21295460,
  sorted_member_order: true,
});

assert.equal(sourceLock.schema, 'a20-capability-source-lock/1');
assert.equal(sourceLock.course_id, 'A20');
assert.equal(sourceLock.inputs.length, 14);
assert.deepEqual(sourceLock.native_export, {
  schema: 'interlanguage.interoperability-v0-full-manifest.v1',
  record_count: 174535,
  jsonl_sha256: 'f8536e60b6e6fde9855da51e9d1d9037e5772190a1fd2e6ee4189c1f024172d3',
});
assert.deepEqual(sourceLock.indonesian_release, {
  repository: 'https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id',
  commit: 'b293e167477c8fe2e8885c6f6d79d12cbb2e0e89',
  tree: '9ee25a0fa6eb336cbd40f3aa61587797b2bf4f27',
  tag: 'v1.0.0',
  repository_landing_is_complete_authority: false,
  complete_authority: 'v1.0.0 release assets and exact producer receipts',
});
assert.equal(publicReadback.state, 'pass');
assert.equal(publicReadback.anonymous, true);
assert.equal(publicReadback.credentials_used, false);
assert.equal(publicReadback.failures.length, 0);
assert.equal(publicReadback.native_backend.records, 174535);
assert.equal(publicReadback.github_release.assets.length, 8);
assert.equal(publicReadback.zenodo.assets.length, 8);
assert.equal(publicReadback.github_release.total_bytes, 1102054925);
assert.equal(publicReadback.zenodo.total_bytes, 1102054925);

assert.equal(capabilities.schema, 'a20-capabilities/1');
assert.equal(capabilities.contract, manifest.contract);
assert.equal(capabilities.native_role_id, 'R001');
assert.deepEqual(capabilities.counts, counts);
assert.deepEqual(capabilities.curriculum_graph.prerequisite_course_ids, ['A10']);
assert.deepEqual(capabilities.curriculum_graph.native_prerequisite_course_ids, []);
assert.equal(capabilities.curriculum_graph.prerequisite_authority, 'central_curriculum_overlay');
assert.equal(capabilities.curriculum_graph.chapter_module_count, 82);
assert.equal(capabilities.curriculum_graph.book_level_front_matter_module_count, 1);
assert.equal(capabilities.learner_delivery.module_navigation, true);
assert.equal(capabilities.learner_delivery.partial_solution_identity_coverage, true);
assert.equal(capabilities.learner_delivery.indonesian_semantic_html, false);
assert.equal(capabilities.educator_delivery.module_selector, true);
assert.equal(capabilities.educator_delivery.official_teacher_manual, false);
assert.equal(capabilities.federation.stable_native_ids_preserved, true);
assert.equal(capabilities.federation.body_content_embedded, false);
assert.equal(capabilities.federation.reversible_exchange_claimed, false);

assert.equal(learningMap.schema, 'a20-learner-map/1');
assert.equal(learningMap.course_id, 'A20');
assert.equal(learningMap.locale, 'id-ID');
assert.equal(learningMap.modules.length, 83);
assert.equal(learningMap.front_matter_modules.length, 1);
assert.equal(learningMap.chapters.length, 12);
assert.equal(learningMap.exercise_identity_count, 8209);
assert.equal(learningMap.solution_identity_count, 5238);
assert.equal(learningMap.unsolved_exercise_count, 2971);
assert.equal(learningMap.indonesian_reader.pdf_pages, 3438);
assert.equal(learningMap.indonesian_reader.semantic_html, false);
assert.equal(learningMap.indonesian_reader.mathml, false);
assert.equal(learningMap.english_source_mirror.translation_claimed, false);
assert.equal(learningMap.english_source_mirror.common_adapter_consumption_claimed, false);
assert.equal(learningMap.body_content_embedded, false);

assert.equal(educatorMap.schema, 'a20-educator-map/1');
assert.equal(educatorMap.course_id, 'A20');
assert.equal(educatorMap.locale, 'id-ID');
assert.equal(educatorMap.selectable_modules.length, 83);
assert.equal(educatorMap.front_matter_modules.length, 1);
assert.equal(educatorMap.chapter_summaries.length, 12);
assert.equal(educatorMap.exercise_identity_count, 8209);
assert.equal(educatorMap.solution_identity_count, 5238);
assert.equal(educatorMap.unsolved_exercise_count, 2971);
assert.equal(educatorMap.official_teacher_manual_claimed, false);
assert.equal(educatorMap.solution_bodies_embedded, false);
assert.equal(educatorMap.body_content_embedded, false);

assert.equal(publicEvidence.schema, 'a20-public-evidence/1');
assert.equal(publicEvidence.course_id, 'A20');
assert.equal(publicEvidence.repository.commit, sourceLock.indonesian_release.commit);
assert.equal(publicEvidence.repository.tree, sourceLock.indonesian_release.tree);
assert.equal(publicEvidence.repository.landing_readme.stale_28_of_83_checkpoint, true);
assert.equal(publicEvidence.repository.landing_readme.authority_for_complete_release, false);
assert.equal(publicEvidence.indonesian_reader.pdf_pages, 3438);
assert.equal(publicEvidence.indonesian_reader.semantic_html, false);
assert.equal(publicEvidence.indonesian_reader.mathml, false);
assert.equal(publicEvidence.zenodo.record_id, 22229860);
assert.equal(publicEvidence.zenodo.concept_id, 22060225);
assert.equal(publicEvidence.zenodo.access_right, 'open');
assert.equal(publicEvidence.english_source_mirror.translation_claimed, false);

assert.equal(claimBoundary.schema, 'a20-claim-boundary/1');
assert.equal(claimBoundary.course_id, 'A20');
for (const key of [
  'native_bodies_copied', 'all_exercises_claimed_solved',
  'native_course_prerequisites_invented', 'stale_repository_landing_used_as_complete_authority',
  'indonesian_semantic_html_claimed', 'indonesian_mathml_claimed', 'epub_claimed',
  'portable_offline_indonesian_html_claimed', 'pdf_ua_claimed',
  'wcag_conformance_claimed', 'reversible_exchange_claimed',
  'english_source_mirror_translation_claimed',
  'english_source_mirror_common_adapter_consumption_claimed',
  'official_teacher_manual_claimed', 'public_access_state_changed',
]) assert.equal(claimBoundary[key], false);
for (const key of [
  'source_segment_text_copied', 'target_segment_text_copied',
  'exercise_or_problem_bodies_copied', 'solution_bodies_copied', 'learner_result_instances',
]) assert.equal(claimBoundary[key], 0);
assert.equal(claimBoundary.unsolved_exercises_preserved, 2971);
assert.equal(claimBoundary.central_a10_prerequisite_is_overlay, true);

const publicMappings = [
  [`${base}/views/A20.html`, 'docs/backend/a20/A20.html'],
  [`${base}/views/A20-pengajar.html`, 'docs/backend/a20/A20-pengajar.html'],
  [`${base}/views/capabilities.json`, 'docs/backend/a20/capabilities.json'],
  [`${base}/data/learner-map.json`, 'docs/backend/a20/learning-map.json'],
  [`${base}/data/educator-map.json`, 'docs/backend/a20/educator-map.json'],
  [`${base}/data/public-evidence.json`, 'docs/backend/a20/public-evidence.json'],
  [`${base}/data/claim-boundary.json`, 'docs/backend/a20/claim-boundary.json'],
  [`${base}/data/native-record-ledger.json`, 'docs/backend/a20/data/native-record-ledger.json'],
  [`${base}/data/module-index.jsonl`, 'docs/backend/a20/data/module-index.jsonl'],
  [`${base}/data/exercise-index.jsonl`, 'docs/backend/a20/data/exercise-index.jsonl'],
  [`${base}/data/concept-index.jsonl`, 'docs/backend/a20/data/concept-index.jsonl'],
  [`${base}/data/pedagogical-relation-index.jsonl`, 'docs/backend/a20/data/pedagogical-relation-index.jsonl'],
  [`${base}/data/terms-index.jsonl`, 'docs/backend/a20/data/terms-index.jsonl'],
  [`${base}/data/corrections-index.jsonl`, 'docs/backend/a20/data/corrections-index.jsonl'],
  [`${base}/data/rights-index.jsonl`, 'docs/backend/a20/data/rights-index.jsonl'],
  [`${base}/input/source-lock.json`, 'docs/backend/a20/source-lock.json'],
  [`${base}/input/public-native-readback.json`, 'docs/backend/a20/public-native-readback.json'],
  [`${base}/validation.json`, 'docs/backend/a20/validation.json'],
];
for (const [source, target] of publicMappings) {
  let bytes = await readFile(resolve(root, source));
  if (target === 'docs/backend/a20/A20-pengajar.html') {
    const original = bytes.toString('utf8');
    assert.equal((original.match(/\.\.\/data\//g) ?? []).length, 7);
    const projected = original.replaceAll('../data/', 'data/');
    assert.equal(projected.includes('../data/'), false);
    bytes = Buffer.from(projected, 'utf8');
  }
  await mkdir(dirname(resolve(root, target)), {recursive: true});
  await writeFile(resolve(root, target), bytes);
  assert.deepEqual(await identity(target), {
    path: target,
    bytes: bytes.length,
    sha256: createHash('sha256').update(bytes).digest('hex'),
  });
}

const evidence = [];
for (const [kind, path] of [
  ['central_adapter_manifest', `${base}/manifest.json`],
  ['deterministic_validation_receipt', `${base}/validation.json`],
  ['native_source_lock', `${base}/input/source-lock.json`],
  ['anonymous_native_public_readback', `${base}/input/public-native-readback.json`],
  ['verified_native_public_release', `${base}/data/public-evidence.json`],
  ['native_record_ledger', `${base}/data/native-record-ledger.json`],
  ['module_identity_index', `${base}/data/module-index.jsonl`],
  ['exercise_solution_identity_index', `${base}/data/exercise-index.jsonl`],
  ['concept_index', `${base}/data/concept-index.jsonl`],
  ['pedagogical_relation_index', `${base}/data/pedagogical-relation-index.jsonl`],
  ['component_rights_index', `${base}/data/rights-index.jsonl`],
  ['correction_index', `${base}/data/corrections-index.jsonl`],
  ['terminology_index', `${base}/data/terms-index.jsonl`],
]) {
  const {bytes, sha256} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-06'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
assert.ok(
  !overrides.semantic_adapters.A20
    || !overrides.semantic_adapters.A20.contract_version
    || overrides.semantic_adapters.A20.contract_version === manifest.contract,
  'Preserve a different admitted A20 contract',
);
overrides.semantic_adapters.A20 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_174535_native_records_83_modules_8209_exercise_problem_identities_5238_solution_identities_236_concepts_340_terms_1614_corrections_and_17_component_rights_with_2971_unsolved_exercises_preserved',
  evidence,
};
overrides.native_capabilities.A20 = {...(overrides.native_capabilities.A20 ?? {})};
for (const capability of [
  'unit_identity', 'terminology', 'translation_rights', 'corrections',
  'build', 'deterministic_replay', 'educator_unit_alignment', 'translation_ledger',
]) overrides.native_capabilities.A20[capability] = {status: 'verified', evidence};

const scope = 'Sebanyak 174.535 rekaman native, 83 modul, 8.209 identitas latihan/masalah, 5.238 identitas solusi, 236 konsep, 340 istilah, 1.614 koreksi, dan 17 rekaman hak komponen.';
const limitations = [
  'Adapter adalah proyeksi identitas, struktur, istilah, status, hak, dan bukti zero-copy; badan buku, segmen, latihan, masalah, dan solusi tetap pada edisi native publik.',
  'Hanya 5.238 dari 8.209 latihan memiliki identitas solusi; 2.971 latihan tanpa identitas solusi dipertahankan dan tidak diisi atau disamarkan.',
  'Delapan puluh tiga rute modul menunjuk tepat ke halaman pembuka PDF, bukan jangkar HTML semantik per unit.',
  'Pembaca Bahasa Indonesia berbasis PDF. HTML semantik, MathML, EPUB, paket HTML luring, PDF/UA, dan kepatuhan WCAG tidak diklaim.',
  'Prasyarat A10 adalah lapisan kurikulum pusat, bukan klaim prasyarat dari ekspor native.',
  'Cermin HTML bahasa Inggris adalah presentasi sumber asli, bukan terjemahan atau bukti konsumsi adapter bersama.',
  'Tujuh belas rekaman hak dan 1.614 status koreksi dipertahankan terpisah; pertukaran reversibel tidak diklaim.',
];
const tool = {
  tool_id: 'a20.open_learner_hub',
  label: 'A20 · Aljabar Menengah',
  href: 'backend/a20/A20.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/a20/A20.html'),
  resource: await identity('docs/backend/a20/learning-map.json'),
  evidence: await identity('docs/backend/a20/validation.json'),
  limitations,
};
assert.ok(
  !overrides.learner_tools.A20
    || overrides.learner_tools.A20.every(old => old.tool_id === tool.tool_id),
  'Preserve unrelated A20 learner tools',
);
overrides.learner_tools.A20 = [tool];

const oldEducator = overrides.educator_evidence.A20;
const teacher = await identity('docs/backend/a20/A20-pengajar.html');
const educatorMapIdentity = await identity('docs/backend/a20/educator-map.json');
const moduleIdentity = await identity('docs/backend/a20/data/module-index.jsonl');
const exerciseIdentity = await identity('docs/backend/a20/data/exercise-index.jsonl');
const conceptIdentity = await identity('docs/backend/a20/data/concept-index.jsonl');
const relationIdentity = await identity('docs/backend/a20/data/pedagogical-relation-index.jsonl');
const termIdentity = await identity('docs/backend/a20/data/terms-index.jsonl');
const rightsIdentity = await identity('docs/backend/a20/data/rights-index.jsonl');
const correctionsIdentity = await identity('docs/backend/a20/data/corrections-index.jsonl');
const ledgerIdentity = await identity('docs/backend/a20/data/native-record-ledger.json');
const educatorUrl = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/a20/A20-pengajar.html';
const managedResourceIds = new Set([
  'A20:educator-hub-v1', 'A20:educator-map-v1', 'A20:module-index-v1',
  'A20:exercise-index-v1', 'A20:concept-index-v1', 'A20:relation-index-v1',
  'A20:terms-index-v1', 'A20:rights-index-v1', 'A20:corrections-index-v1',
  'A20:native-record-ledger-v1',
]);
const resources = (oldEducator?.resources ?? []).filter(resource => !managedResourceIds.has(resource.id));
resources.push({
  id: 'A20:educator-hub-v1',
  title: 'Pemilih bab, modul, latihan, dan cakupan solusi A20 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url: educatorUrl,
  scope,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
resources.push({
  id: 'A20:educator-map-v1',
  title: 'Peta pengajar atas 83 modul native A20',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/a20/educator-map.json',
  scope: 'Peta zero-copy atas modul, rute halaman, latihan, konsep, istilah, koreksi, hak, dan batas cakupan solusi.',
  bytes: educatorMapIdentity.bytes,
  sha256: educatorMapIdentity.sha256,
});
for (const row of [
  ['A20:module-index-v1', 'Indeks 83 modul A20', 'module-index.jsonl', moduleIdentity, 'identity-index'],
  ['A20:exercise-index-v1', 'Indeks 8.209 latihan/masalah dan 5.238 solusi A20', 'exercise-index.jsonl', exerciseIdentity, 'exercise-bank'],
  ['A20:concept-index-v1', 'Indeks 236 konsep A20', 'concept-index.jsonl', conceptIdentity, 'educator-data'],
  ['A20:relation-index-v1', 'Indeks 32.393 relasi pedagogis A20', 'pedagogical-relation-index.jsonl', relationIdentity, 'educator-data'],
  ['A20:terms-index-v1', 'Indeks 340 istilah A20', 'terms-index.jsonl', termIdentity, 'terminology-register'],
  ['A20:rights-index-v1', 'Indeks 17 rekaman hak A20', 'rights-index.jsonl', rightsIdentity, 'rights-ledger'],
  ['A20:corrections-index-v1', 'Indeks 1.614 koreksi A20', 'corrections-index.jsonl', correctionsIdentity, 'correction-ledger'],
  ['A20:native-record-ledger-v1', 'Ledger 174.535 identitas native A20', 'native-record-ledger.json', ledgerIdentity, 'identity-index'],
]) {
  const [id, title, filename, fact, resourceType] = row;
  resources.push({
    id,
    title,
    resource_type: resourceType,
    status: 'verified',
    url: `https://kokunoyumeto.github.io/program-matematika-indonesia/backend/a20/data/${filename}`,
    scope: 'Indeks metadata native dengan identitas dan hash stabil; badan buku dan segmen tidak disalin.',
    bytes: fact.bytes,
    sha256: fact.sha256,
  });
}
overrides.educator_evidence.A20 = {
  status: 'verified',
  verified_date: '2026-09-06',
  locator: educatorUrl,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: ['lesson_sequences', 'exercise_bank', 'prerequisite_diagnostics', 'remix_selectors'],
  resources,
};
await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);

const learnerTarget = 'backend/authority/learner-delivery-overrides-v1.json';
const learner = await load(learnerTarget);
const zenodoFile = name => {
  const matches = publicEvidence.zenodo.assets.filter(row => row.name === name);
  assert.equal(matches.length, 1, `Missing or duplicate native Zenodo file: ${name}`);
  return matches[0];
};
const publicReceipt = {
  kind: 'anonymous_public_byte_readback',
  locator: `https://github.com/KokunoYumeto/program-matematika-indonesia/blob/main/${base}/data/public-evidence.json`,
  verified_date: '2026-09-06',
};
const pdfFile = zenodoFile('openstax-intermediate-algebra-2e-id-ID-1.0.0-reader.pdf');
const pdf = {
  status: 'verified',
  format: 'application/pdf',
  url: pdfFile.url,
  bytes: pdfFile.bytes,
  sha256: pdfFile.sha256,
  scope: 'whole_course_3438_pages_with_exact_module_page_routes_in_adapter',
  evidence: publicReceipt,
};
learner.courses.A20 = {
  ...(learner.courses.A20 ?? {}),
  primary: pdf,
  online_html: {status: 'not_yet_produced'},
  pdf,
  epub: {status: 'not_yet_produced'},
  portable_html: {status: 'not_yet_produced'},
  capabilities: {
    ...(learner.courses.A20?.capabilities ?? {}),
    semantic_html: {status: 'not_yet_produced'},
    mathml: {status: 'not_yet_produced'},
    print_profile: {status: 'verified', evidence: {...publicReceipt, pdf_pages: 3438}},
    chapter_downloads: {status: 'not_yet_produced'},
  },
};
await writeFile(resolve(root, learnerTarget), `${JSON.stringify(learner, null, 2)}\n`);

console.log(JSON.stringify({
  state: 'pass',
  admitted_roles: ['A20'],
  contract: manifest.contract,
  native_locale: manifest.locale,
  public_files_staged: publicMappings.length,
  native_records: counts.native_records,
  modules: counts.modules,
  exercises: counts.exercises,
  solution_identities: counts.solution_identities,
  unsolved_exercises: counts.unsolved_exercises,
  public_state_changed: false,
}));
