import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/d90-capability-v1';
const load = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const identity = async path => {
  const data = await readFile(resolve(root, path));
  return {path, bytes: data.length, sha256: createHash('sha256').update(data).digest('hex')};
};

const manifest = await load(`${base}/manifest.json`);
const validation = await load(`${base}/validation.json`);
const packageReceipt = await load(`${base}/build/PACKET_BUILD_RECEIPT.json`);
const sourceLock = await load(`${base}/input/source-lock.json`);
const capabilities = await load(`${base}/data/capabilities.json`);
const learningMap = await load(`${base}/data/learner-map.json`);
const educatorMap = await load(`${base}/data/educator-map.json`);
const publicEvidence = await load(`${base}/data/public-evidence.json`);
const claimBoundary = await load(`${base}/data/claim-boundary.json`);

const counts = {
  case_sensitive_key_collisions: 1,
  component_rights: 93,
  corrections: 248,
  dangling_references: 0,
  educator_rubrics: 7,
  entity_counts: {
    artifact: 489,
    asset: 24,
    concept: 176,
    correction: 248,
    course: 1,
    edition: 17,
    learning_surface: 1247,
    program: 1,
    qa_event: 323,
    relation: 1837,
    resource: 10,
    rights: 93,
    segment: 248,
    term: 127,
    unit: 36,
  },
  explicit_state_marker_records: 178,
  learner_assessment_containers: 54,
  learner_computational_lab_surfaces: 2,
  native_records: 4877,
  native_references: 13777,
  original03_anchor_matches: 438,
  original03_surface_counts: {
    assessment_prompt: 54,
    capstone_milestone: 7,
    capstone_project: 1,
    capstone_project_unit: 1,
    complete_solution: 86,
    computational_lab: 2,
    exercise: 29,
    exercise_group: 25,
    hint: 32,
    hint_stage_1: 54,
    hint_stage_2: 54,
    proof_rubric: 7,
    short_answer: 86,
  },
  original03_surfaces: 438,
  practice_chains: 32,
  prompt_chains: 54,
  staged_relations: 312,
  terms: 127,
};

assert.equal(manifest.schema, 'd90-capability-manifest/1');
assert.equal(manifest.course_id, 'D90');
assert.equal(manifest.native_course_id, 'course.d90.advanced-optimization-convex-analysis');
assert.equal(manifest.native_family, 'advanced_optimization_convex_analysis');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.content_policy, 'identity_state_rights_evidence_only');
assert.deepEqual(manifest.counts, counts);
assert.deepEqual(manifest.inputs, sourceLock.inputs);
assert.equal(manifest.outputs.length, 29);
assert.deepEqual(manifest.projection, {
  central_course_truth_rewritten: false,
  component_rights_preserved: true,
  external_pinned_native_checkout_required_for_replay: true,
  native_bodies_copied: false,
  native_ids_preserved: true,
  public_state_changed: false,
  reversible_exchange_claimed: false,
});
for (const item of manifest.outputs) {
  assert.deepEqual(
    await identity(`${base}/${item.path}`),
    {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256},
  );
}

assert.equal(validation.schema, 'd90-capability-validation/1');
assert.equal(validation.result, 'pass');
assert.equal(validation.course_id, 'D90');
assert.deepEqual(validation.counts, counts);
assert.equal(validation.negative_fixtures.length, 13);
assert.ok(validation.negative_fixtures.every(row => row.result === 'rejected'));
assert.equal(validation.checks.committed_projection_matches_native, true);
assert.equal(validation.checks.canonical_machine_files, true);
assert.equal(validation.checks.component_specific_rights_preserved, true);
assert.equal(validation.checks.content_bodies_absent, true);
assert.equal(validation.checks.csv_jsonl_lossless_native_receipt_preserved, true);
assert.equal(validation.checks.public_anchor_observations, 438);
assert.equal(validation.checks.public_hash_receipts_preserved, 6);
assert.equal(validation.checks.two_run_build_identity.file_count, 30);
assert.equal(validation.checks.two_run_build_identity.tree_sha256, '9a8d8a68342c3bb0ebbd1fbe7cbe39695ffa1763ba006cfc84b337e8453543de');

assert.equal(packageReceipt.schema, 'd90-capability-thin-packet-build-receipt/1');
assert.equal(packageReceipt.result, 'PASS');
assert.equal(packageReceipt.two_build_byte_identity, true);
assert.equal(packageReceipt.negative_fixtures_included, 13);
assert.equal(packageReceipt.native_inputs_included, 0);
assert.equal(packageReceipt.native_content_bodies_included, false);
assert.equal(packageReceipt.forbidden_payloads_included, false);
assert.equal(packageReceipt.local_profile_data_included, false);
assert.equal(packageReceipt.external_pinned_native_checkout_required_for_replay, true);
assert.equal(packageReceipt.reversible_exchange_claimed, false);
assert.equal(packageReceipt.public_state_changed, false);
assert.deepEqual(packageReceipt.adapter_manifest, {
  ...(await identity(`${base}/manifest.json`)),
  path: 'manifest.json',
});
assert.deepEqual(packageReceipt.adapter_validation, {
  ...(await identity(`${base}/validation.json`)),
  path: 'validation.json',
});
assert.deepEqual(packageReceipt.archive, {
  ...(await identity(`${base}/build/D90_THIN_CAPABILITY_METADATA_V1.zip`)),
  path: 'build/D90_THIN_CAPABILITY_METADATA_V1.zip',
});
assert.deepEqual(packageReceipt.zip_checks, {
  crc_and_full_entry_readback: true,
  fixed_member_metadata: true,
  member_count: 37,
  payload_bytes: 3021290,
  sorted_member_order: true,
});

assert.equal(sourceLock.schema, 'd90-source-lock/1');
assert.equal(sourceLock.course_id, 'D90');
assert.equal(sourceLock.locale, 'id-ID');
assert.deepEqual(sourceLock.native_repository, {
  commit: 'eb6b25cb6d2c84d32c5b0a30b0feea9e97efefab',
  repository: 'https://github.com/KokunoYumeto/advanced-optimization-convex-analysis-id',
  tree: 'f3cd6fb20a1dc8f157c6072ff398d0fc03167e84',
});
assert.equal(sourceLock.inputs.length, 11);

assert.equal(capabilities.schema, 'd90-capabilities/1');
assert.equal(capabilities.contract, manifest.contract);
assert.equal(capabilities.course_id, 'D90');
assert.deepEqual(capabilities.counts, counts);
assert.deepEqual(capabilities.observed_capabilities, {
  assessment_prompt_chains: true,
  component_specific_rights: true,
  educator_proof_rubrics: true,
  html_mathml: true,
  native_jsonl_csv_lossless: true,
  native_reference_closure: true,
  original03_public_anchors: true,
  public_epub: true,
  public_html: true,
  public_pdf: true,
});
assert.deepEqual(capabilities.case_sensitive_key_caveat.collisions[0].keys, [
  'Cref_occurrences_preserved',
  'cref_occurrences_preserved',
]);
assert.equal(capabilities.case_sensitive_key_caveat.collisions[0].native_line, 4152);
assert.equal(capabilities.limitations.non_original03_unresolved_label.included_in_shared_slice, false);
assert.equal(capabilities.limitations.reversible_exchange_claimed, false);

assert.equal(learningMap.schema, 'd90-learner-map/1');
assert.equal(learningMap.contract, manifest.contract);
assert.equal(learningMap.course_id, 'D90');
assert.equal(learningMap.locale, 'id-ID');
assert.equal(learningMap.prompt_chains.length, 54);
assert.equal(learningMap.practice_chains.length, 32);
assert.equal(learningMap.assessment_containers.length, 54);
assert.equal(learningMap.labs.length, 2);
assert.equal(learningMap.capstone.milestones.length, 7);
assert.equal(learningMap.claim_boundary.content_bodies_copied, false);
assert.equal(learningMap.claim_boundary.learner_attempt_instances, 0);
assert.equal(learningMap.claim_boundary.learner_submission_instances, 0);
assert.equal(learningMap.claim_boundary.learner_result_instances, 0);
assert.ok(learningMap.prompt_chains.every(chain => chain.stages.length === 5));
assert.ok(learningMap.practice_chains.every(chain => chain.stages.length === 4));

assert.equal(educatorMap.schema, 'd90-educator-map/1');
assert.equal(educatorMap.contract, manifest.contract);
assert.equal(educatorMap.course_id, 'D90');
assert.equal(educatorMap.locale, 'id-ID');
assert.equal(educatorMap.prompt_chains.length, 54);
assert.equal(educatorMap.assessment_containers.length, 54);
assert.equal(educatorMap.labs.length, 2);
assert.equal(educatorMap.rubrics.length, 7);
assert.equal(educatorMap.capstone.milestones.length, 7);
assert.equal(educatorMap.claim_boundary.all_native_surfaces_have_complete_solutions_claimed, false);
assert.equal(educatorMap.claim_boundary.lab_completion_claimed, false);
assert.equal(educatorMap.claim_boundary.live_learner_results_claimed, false);

assert.equal(publicEvidence.schema, 'd90-public-evidence/1');
assert.equal(publicEvidence.course_id, 'D90');
assert.equal(publicEvidence.github.commit, sourceLock.native_repository.commit);
assert.equal(publicEvidence.github.tree, sourceLock.native_repository.tree);
assert.equal(publicEvidence.native_backend_validation.result, 'pass');
assert.equal(publicEvidence.native_backend_validation.records, 4877);
assert.equal(publicEvidence.native_backend_validation.deterministic_runs, 2);
assert.equal(publicEvidence.accessibility.html.mathml_count, 4535);
assert.equal(publicEvidence.accessibility.html.unresolved_internal_fragments.length, 0);
assert.equal(publicEvidence.accessibility.epub.epubcheck_errors, 0);
assert.equal(publicEvidence.accessibility.wcag_conformance_claimed, false);
assert.equal(publicEvidence.zenodo.record_id, 22142120);
assert.equal(publicEvidence.zenodo.concept_id, 22059741);
assert.equal(publicEvidence.zenodo.status, 'published');
assert.equal(publicEvidence.zenodo.result, 'pass');
assert.equal(publicEvidence.zenodo.files.length, 6);
assert.ok(publicEvidence.zenodo.files.every(row => row.public_byte_identity === 'pass'));

assert.equal(claimBoundary.schema, 'd90-claim-boundary/1');
assert.equal(claimBoundary.course_id, 'D90');
for (const key of [
  'central_course_truth_rewritten', 'component_rights_flattened',
  'content_bodies_copied', 'datasets_copied', 'epub_copied',
  'full_solution_coverage_beyond_observed_records_claimed', 'html_copied',
  'lab_completion_claimed', 'pdf_copied', 'public_state_changed',
  'reversible_exchange_claimed', 'solution_bodies_copied',
  'source_tex_copied', 'wcag_conformance_claimed',
]) assert.equal(claimBoundary[key], false);
for (const key of ['learner_attempt_instances', 'learner_result_instances', 'learner_submission_instances']) {
  assert.equal(claimBoundary[key], 0);
}
assert.equal(claimBoundary.native_backend_authoritative, true);
assert.equal(claimBoundary.native_ids_preserved, true);

const publicMappings = [
  [`${base}/views/D90.html`, 'docs/backend/d90/D90.html'],
  [`${base}/views/D90-pengajar.html`, 'docs/backend/d90/D90-pengajar.html'],
  [`${base}/views/capabilities.json`, 'docs/backend/d90/capabilities.json'],
  [`${base}/data/learner-map.json`, 'docs/backend/d90/learning-map.json'],
  [`${base}/data/educator-map.json`, 'docs/backend/d90/educator-map.json'],
  [`${base}/data/public-evidence.json`, 'docs/backend/d90/public-evidence.json'],
  [`${base}/data/claim-boundary.json`, 'docs/backend/d90/claim-boundary.json'],
  [`${base}/data/rights-index.jsonl`, 'docs/backend/d90/data/rights-index.jsonl'],
  [`${base}/data/corrections-index.jsonl`, 'docs/backend/d90/data/corrections-index.jsonl'],
  [`${base}/data/terms-index.jsonl`, 'docs/backend/d90/data/terms-index.jsonl'],
  [`${base}/validation.json`, 'docs/backend/d90/validation.json'],
];
for (const [source, target] of publicMappings) {
  const bytes = await readFile(resolve(root, source));
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
  ['verified_native_public_release', `${base}/data/public-evidence.json`],
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
  !overrides.semantic_adapters.D90
    || !overrides.semantic_adapters.D90.contract_version
    || overrides.semantic_adapters.D90.contract_version === manifest.contract,
  'Preserve a different admitted D90 contract',
);
overrides.semantic_adapters.D90 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_4877_native_records_438_original03_public_learning_surfaces_54_five_stage_prompt_chains_32_four_stage_practice_chains_93_rights_248_corrections_and_127_terms',
  evidence,
};
overrides.native_capabilities.D90 = {...(overrides.native_capabilities.D90 ?? {})};
for (const capability of [
  'unit_identity', 'terminology', 'translation_rights', 'corrections',
  'build', 'deterministic_replay', 'educator_unit_alignment', 'translation_ledger',
]) overrides.native_capabilities.D90[capability] = {status: 'verified', evidence};

const scope = 'Sebanyak 4.877 rekaman native dan 438 permukaan belajar Original-03: 54 rantai prompt lima tahap, 32 rantai latihan empat tahap, 54 wadah asesmen, dua lab, tujuh rubrik, tujuh milestone, 93 rekaman hak, 248 koreksi, dan 127 istilah.';
const limitations = [
  'Adapter adalah proyeksi identitas, status, hak, dan bukti zero-copy; badan kursus, prompt, petunjuk, jawaban, solusi, TeX, HTML, PDF, EPUB, dan dataset tetap pada edisi native publik.',
  'Cakupan bersama dibatasi pada 438 permukaan Original-03 yang mempunyai jangkar publik; satu label non-Original-03 yang belum terselesaikan sengaja tidak dimasukkan.',
  'Tidak ada percobaan, kiriman, hasil pelajar, atau penyelesaian lab yang diklaim.',
  'Solusi lengkap hanya dinyatakan untuk rekaman yang teramati; cakupan solusi universal tidak diklaim.',
  'Hak tetap dipertahankan sebagai 93 rekaman spesifik; tidak ada lisensi payung yang direka.',
  'HTML dan EPUB native mempunyai MathML menurut kuitansi native; kesesuaian WCAG tidak diklaim.',
  'Pertukaran reversibel tidak diklaim dan replay memerlukan checkout native yang dipatok.',
];
const tool = {
  tool_id: 'd90.open_learner_hub',
  label: 'D90 · Optimisasi Lanjut dan Analisis Konveks',
  href: 'backend/d90/D90.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/d90/D90.html'),
  resource: await identity('docs/backend/d90/learning-map.json'),
  evidence: await identity('docs/backend/d90/validation.json'),
  limitations,
};
assert.ok(
  !overrides.learner_tools.D90
    || overrides.learner_tools.D90.every(old => old.tool_id === tool.tool_id),
  'Preserve unrelated D90 learner tools',
);
overrides.learner_tools.D90 = [tool];

const oldEducator = overrides.educator_evidence.D90;
const teacher = await identity('docs/backend/d90/D90-pengajar.html');
const educatorMapIdentity = await identity('docs/backend/d90/educator-map.json');
const termIdentity = await identity('docs/backend/d90/data/terms-index.jsonl');
const rightsIdentity = await identity('docs/backend/d90/data/rights-index.jsonl');
const correctionsIdentity = await identity('docs/backend/d90/data/corrections-index.jsonl');
const educatorUrl = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d90/D90-pengajar.html';
const resources = (oldEducator?.resources ?? []).filter(resource => ![
  'D90:native-educator-observation', 'D90:educator-hub-v1',
  'D90:educator-map-v1', 'D90:terms-index-v1', 'D90:rights-index-v1',
  'D90:corrections-index-v1',
].includes(resource.id));
resources.push({
  id: 'D90:native-educator-observation',
  title: 'Rekaman rilis native D90 untuk asesmen, rubrik, dan lab',
  resource_type: 'assessment-blueprints',
  status: 'available_unverified',
  url: 'https://zenodo.org/records/22142120',
  scope: 'Rekaman native yang mendahului adapter pusat; dipertahankan terpisah dari bukti konsumsi bersama.',
});
resources.push({
  id: 'D90:educator-hub-v1',
  title: 'Pemilih asesmen, petunjuk, jawaban, solusi, rubrik, lab, dan capstone D90 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url: educatorUrl,
  scope,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
resources.push({
  id: 'D90:educator-map-v1',
  title: 'Peta asesmen dan dukungan bertahap D90',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d90/educator-map.json',
  scope: 'Peta zero-copy atas identitas asesmen, rubrik, lab, capstone, dan rantai dukungan native.',
  bytes: educatorMapIdentity.bytes,
  sha256: educatorMapIdentity.sha256,
});
for (const resource of [
  ['D90:terms-index-v1', 'Indeks 127 istilah D90', 'terms-index.jsonl', termIdentity, 'terminology-register'],
  ['D90:rights-index-v1', 'Indeks 93 rekaman hak D90', 'rights-index.jsonl', rightsIdentity, 'rights-ledger'],
  ['D90:corrections-index-v1', 'Indeks 248 koreksi D90', 'corrections-index.jsonl', correctionsIdentity, 'correction-ledger'],
]) {
  const [id, title, filename, fact, resourceType] = resource;
  resources.push({
    id,
    title,
    resource_type: resourceType,
    status: 'verified',
    url: `https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d90/data/${filename}`,
    scope: 'Indeks metadata native yang dipertahankan tanpa menyalin badan materi kursus.',
    bytes: fact.bytes,
    sha256: fact.sha256,
  });
}
overrides.educator_evidence.D90 = {
  status: 'verified',
  verified_date: '2026-09-06',
  locator: educatorUrl,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: [
    'lesson_sequences',
    'exercise_bank',
    'staged_hints_answers_solutions',
    'assessment_blueprints',
    'rubrics',
    'activities_labs',
    'accessibility_accommodations',
    'remix_selectors',
    'solution_provenance',
  ],
  resources,
};
await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);

const learnerTarget = 'backend/authority/learner-delivery-overrides-v1.json';
const learner = await load(learnerTarget);
const nativeFile = filename => {
  const matches = publicEvidence.zenodo.files.filter(row => row.filename === filename);
  assert.equal(matches.length, 1, `Missing or duplicate native public file: ${filename}`);
  return matches[0];
};
const publicReceipt = {
  kind: 'anonymous_public_byte_readback',
  locator: `https://github.com/KokunoYumeto/program-matematika-indonesia/blob/main/${base}/data/public-evidence.json`,
  verified_date: '2026-09-06',
};
const pdfFile = nativeFile('D90-O015-optimisasi-lanjut-analisis-konveks-id.pdf');
const epubFile = nativeFile('D90-O015-optimisasi-lanjut-analisis-konveks-id.epub');
const htmlFile = nativeFile('D90-O015-optimisasi-lanjut-analisis-konveks-id.html');
const pdf = {
  status: 'verified',
  format: 'application/pdf',
  url: pdfFile.url,
  bytes: pdfFile.bytes,
  sha256: pdfFile.sha256,
  scope: 'whole_course',
  evidence: publicReceipt,
};
learner.courses.D90 = {
  ...(learner.courses.D90 ?? {}),
  primary: pdf,
  pdf,
  epub: {
    status: 'verified',
    format: 'application/epub+zip',
    url: epubFile.url,
    bytes: epubFile.bytes,
    sha256: epubFile.sha256,
    scope: 'whole_course',
    evidence: publicReceipt,
  },
  capabilities: {
    ...(learner.courses.D90?.capabilities ?? {}),
    semantic_html: {status: 'verified', evidence: {...publicReceipt, bytes: htmlFile.bytes, sha256: htmlFile.sha256}},
    mathml: {status: 'verified', evidence: {...publicReceipt, mathml_count: 4535, bytes: htmlFile.bytes, sha256: htmlFile.sha256}},
    print_profile: {status: 'verified', evidence: {...publicReceipt, pdf_pages: 141, marked: true, structure_tree: true}},
    chapter_downloads: {status: 'absent'},
  },
};
await writeFile(resolve(root, learnerTarget), `${JSON.stringify(learner, null, 2)}\n`);

console.log(JSON.stringify({
  state: 'pass',
  admitted_roles: ['D90'],
  contract: manifest.contract,
  native_locale: manifest.locale,
  public_files_staged: publicMappings.length,
  existing_supplemental_reader_preserved: true,
  public_state_changed: false,
}));
