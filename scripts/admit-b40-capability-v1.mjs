import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/b40-capability-v1';
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
const conceptIndex = await load(`${base}/data/concept-index.json`);
const relationIndex = await load(`${base}/data/relation-index.json`);
const ledgers = await load(`${base}/data/ledger-references.json`);
const publicEvidence = await load(`${base}/data/public-evidence.json`);
const rightsAndTerms = await load(`${base}/data/rights-and-terms.json`);
const claimBoundary = await load(`${base}/data/claim-boundary.json`);

assert.equal(manifest.schema, 'b40-capability-manifest/1');
assert.equal(manifest.course_id, 'B40');
assert.equal(manifest.native_role_id, 'R005');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.contract_2_3_1_conformance, 'not_claimed');
assert.equal(manifest.native_family, 'hefferon_modular_latex_backend');
assert.equal(manifest.content_policy, 'stable_native_ids_selected_metadata_locators_hashes_and_receipt_urls_only');
assert.deepEqual(manifest.counts, capabilities.counts);
assert.deepEqual(manifest.counts, {
  answers: 1037,
  artifacts: 8,
  assets: 432,
  chapters: 17,
  common_crosswalk_records: 22131,
  common_virtual_records: 22131,
  components: 3,
  concepts: 114,
  corrections: 307,
  entity_records_excluding_csv_relations: 8132,
  exercises: 1037,
  github_native_backend_files_verified: 15,
  github_release_assets: 9,
  github_release_assets_fully_hash_verified: 8,
  indonesian_edition_supplied_answers: 2,
  native_backend_manifest_members: 15,
  native_records_total: 22131,
  native_upstream_answers: 1035,
  qa_events: 72,
  relations: 13999,
  rights_components: 11,
  sections: 57,
  segments: 3528,
  source_files: 64,
  target_reader_pages: 1124,
  target_reader_pdfs: 3,
  terms: 114,
  unanswered_exercises: 0,
  units: 3541,
  zenodo_files: 9,
});
assert.deepEqual(manifest.projection, {
  accessibility_conformance_claimed: false,
  all_relation_ids_indexed: true,
  all_unit_ids_indexed: true,
  common_virtual_backend_materialized: false,
  exercise_answer_bijection_preserved: true,
  existing_reversible_migration_reused: true,
  native_epub_claimed: false,
  native_ids_preserved: true,
  native_outcomes_invented: false,
  native_prerequisites_invented: false,
  native_segments_copied: false,
  native_semantic_html_claimed: false,
  public_state_changed: false,
  target_supplied_answer_provenance_preserved: true,
  zero_copy_native_bodies: true,
});
assert.equal(manifest.inputs.length, 18);
assert.deepEqual(manifest.inputs, [
  sourceLock.manifest_input,
  ...sourceLock.native_inputs,
  sourceLock.migration_input,
  sourceLock.public_readback_input,
]);
assert.deepEqual(manifest.outputs.map(({path}) => path).sort(), [
  'README.md',
  'data/capabilities.json',
  'data/claim-boundary.json',
  'data/concept-index.json',
  'data/educator-map.json',
  'data/learning-map.json',
  'data/ledger-references.json',
  'data/public-evidence.json',
  'data/relation-index.json',
  'data/rights-and-terms.json',
  'fixtures/negative-fixtures.json',
  'input/source-lock.json',
  'views/B40-pengajar.html',
  'views/B40.html',
].sort());
for (const item of manifest.outputs) {
  assert.deepEqual(await identity(`${base}/${item.path}`), {
    path: `${base}/${item.path}`,
    bytes: item.bytes,
    sha256: item.sha256,
  });
}

assert.equal(validation.schema, 'b40-capability-validation/1');
assert.equal(validation.state, 'pass');
assert.equal(validation.contract, manifest.contract);
assert.deepEqual(validation.counts, manifest.counts);
assert.equal(validation.source_hashes_verified, 18);
assert.equal(validation.native_manifest_hashes_verified, 15);
assert.equal(validation.negative_fixtures.length, 62);
assert.ok(validation.negative_fixtures.every(row => row.state === 'rejected'));
assert.equal(validation.isolated_two_build_byte_identity.byte_identical, true);
assert.equal(validation.isolated_two_build_byte_identity.file_count, 15);
assert.deepEqual(validation.manifest, {
  ...(await identity(`${base}/manifest.json`)),
  path: 'manifest.json',
});
assert.deepEqual(validation.public_readback, {
  ...(await identity(`${base}/input/public-native-readback.json`)),
  path: sourceLock.public_readback_input.path,
});
assert.deepEqual(validation.migration_receipt, {
  ...(await identity('releases/v0.59.0/hefferon-linear-algebra-id-backend-v1-migration-receipt.json')),
  path: sourceLock.migration_input.path,
});

assert.equal(sourceLock.schema, 'b40-source-lock/1');
assert.equal(sourceLock.native_repository.current_public_head, 'e84ce2956a7304830c42eba70106f940fefee7c4');
assert.equal(sourceLock.native_repository.current_public_tree, 'b434745225bb3931d51d107d8d8e5c0c8707af5d');
assert.equal(sourceLock.native_repository.source_commit, 'df2262e089a02651c127f1dd12649c4622ee1383');
assert.equal(sourceLock.native_repository.source_tree, '30340725aa2641b3c617b1584c59f6df83e1fdf3');
assert.deepEqual(sourceLock.public_readback_input, {
  ...(await identity(`${base}/input/public-native-readback.json`)),
  path: sourceLock.public_readback_input.path,
});
assert.deepEqual(sourceLock.migration_input, {
  ...(await identity('releases/v0.59.0/hefferon-linear-algebra-id-backend-v1-migration-receipt.json')),
  path: sourceLock.migration_input.path,
});
assert.equal(sourceLock.source_closure_descriptor_sha256, 'e60fe57bd3117b9e31b6b7bd0568a4e8b1fbb007bb36d576df724bbfe607d88f');

assert.equal(learningMap.schema, 'b40-learning-map/1');
assert.equal(learningMap.components.length, 3);
assert.equal(learningMap.components.reduce((total, row) => total + row.chapter_count, 0), 17);
assert.equal(learningMap.components.reduce((total, row) => total + row.section_count, 0), 57);
assert.equal(learningMap.route.all_unit_ids.length, 3541);
assert.equal(new Set(learningMap.route.all_unit_ids).size, 3541);
assert.deepEqual(learningMap.program_prerequisites, []);
assert.equal(learningMap.prerequisite_status, 'not asserted without curriculum evidence');
assert.equal(learningMap.outcomes_available, false);

assert.equal(educatorMap.schema, 'b40-educator-map/1');
assert.equal(educatorMap.selector.units.length, 3541);
assert.equal(educatorMap.selector.exercise_answers.length, 1037);
assert.equal(educatorMap.selector.body_content_embedded, false);
assert.equal(educatorMap.selector.answer_selector.relation_type, 'answers');
assert.equal(educatorMap.selector.answer_selector.relation_direction, 'answer_to_exercise');
assert.equal(educatorMap.answer_provenance.native_upstream_answer_count, 1035);
assert.equal(educatorMap.answer_provenance.indonesian_edition_supplied_answer_count, 2);
assert.equal(educatorMap.answer_provenance.target_supplied_answers.length, 2);
assert.ok(educatorMap.answer_provenance.target_supplied_answers.every(row =>
  row.provenance_kind === 'indonesian_edition_supplied'
  && row.authorization_event_id === 'HLA-A0300'));

assert.equal(conceptIndex.schema, 'b40-concept-index/1');
assert.equal(conceptIndex.concepts.length, 114);
assert.equal(conceptIndex.term_count, 114);
assert.equal(conceptIndex.body_content_embedded, false);
assert.equal(relationIndex.schema, 'b40-relation-index/1');
assert.equal(relationIndex.relations.length, 13999);
assert.equal(relationIndex.exercise_answer_projection_rows, 1037);
assert.equal(relationIndex.specialized_projection_duplicate_rows_materialized, 0);
assert.deepEqual(relationIndex.relation_type_counts, {
  adapts: 3, answers: 1037, contains: 7178, corrects: 324,
  'depends-on': 368, exercises: 2208, precedes: 2273, translates: 114, xref: 494,
});

assert.equal(ledgers.schema, 'b40-ledger-references/1');
assert.equal(ledgers.common_projection.native_record_count, 22131);
assert.equal(ledgers.common_projection.entity_records_excluding_csv_relations, 8132);
assert.equal(ledgers.common_projection.relation_records, 13999);
assert.equal(ledgers.common_projection.crosswalk_records, 22131);
assert.equal(ledgers.common_projection.exact_reverse_extraction, 22131);
assert.equal(ledgers.common_projection.native_files_modified, 0);
assert.equal(ledgers.common_projection.deterministic_transform_runs, 2);
assert.equal(ledgers.common_projection.deterministic_virtual_assembly_equal, true);
assert.equal(ledgers.common_projection.virtual_records_materialized, false);
assert.equal(ledgers.common_projection.crosswalk_sha256, '0bf86d6ee55d4b906139df44cb4d4a50881aa0664f6e3a464479cebf2eb46a5a');
assert.equal(ledgers.common_projection.virtual_records_jsonl_sha256, 'fa42e1d8adf3516afa9fa7c31cfe4144d1ff40e1d9e2230e139810a2b161c049');

assert.equal(rightsAndTerms.schema, 'b40-rights-and-terms/1');
assert.equal(rightsAndTerms.component_rights.length, 11);
assert.equal(conceptIndex.term_count, 114);
assert.equal(ledgers.corrections.length, 307);
assert.deepEqual(rightsAndTerms.terminology_reference, {
  canonical_adapter_path: 'data/concept-index.json',
  public_documentation_path: 'docs/backend/b40/concept-index.json',
  schema: 'b40-concept-index/1',
  term_count: 114,
});
assert.deepEqual(rightsAndTerms.corrections_reference, {
  canonical_adapter_path: 'data/ledger-references.json',
  correction_count: 307,
  public_documentation_path: 'docs/backend/b40/ledger-references.json',
  schema: 'b40-ledger-references/1',
});
assert.equal(rightsAndTerms.redundant_terminology_rows_materialized, 0);
assert.equal(rightsAndTerms.redundant_correction_rows_materialized, 0);
assert.equal(rightsAndTerms.blanket_license_claimed, false);
assert.equal(rightsAndTerms.body_content_embedded, false);
assert.deepEqual(claimBoundary, capabilities.claim_boundary);
for (const key of ['learner_attempt_instances', 'learner_submission_instances', 'learner_result_instances', 'credential_assertion_instances']) {
  assert.equal(claimBoundary[key], 0);
}
for (const key of [
  'accessibility_conformance_claimed', 'blanket_license_claimed',
  'common_virtual_backend_materialized', 'exercise_answer_joins_inferred',
  'mathml_claimed', 'native_bodies_copied', 'native_epub_claimed',
  'native_segments_copied', 'native_semantic_html_claimed',
  'native_unit_outcomes_invented', 'native_unit_prerequisites_invented',
  'public_state_changed', 'tagged_pdf_claimed',
  'target_supplied_answers_retyped_as_upstream', 'target_supplied_authorization_omitted',
]) assert.equal(claimBoundary[key], false);

assert.equal(publicReadback.schema, 'b40-native-public-readback/1');
assert.equal(publicReadback.access_mode, 'anonymous_no_credentials');
assert.equal(publicReadback.github.current_head, sourceLock.native_repository.current_public_head);
assert.equal(publicReadback.github.current_tree, sourceLock.native_repository.current_public_tree);
assert.equal(publicReadback.github.native_backend_files.length, 15);
assert.equal(publicReadback.github.release.assets.length, 9);
assert.equal(publicReadback.github.release.fully_downloaded_and_sha256_verified.length, 8);
assert.equal(publicReadback.github.release.large_asset_anonymous_head_checks.length, 1);
assert.equal(publicReadback.zenodo.record_id, 22070458);
assert.equal(publicReadback.zenodo.concept_record_id, 22070457);
assert.equal(publicReadback.zenodo.access_right, 'open');
assert.equal(publicReadback.zenodo.status, 'published');
assert.equal(publicReadback.zenodo.files.length, 9);
assert.equal(publicReadback.checks.external_state_changed, false);
assert.equal(publicEvidence.schema, 'b40-public-evidence/1');
assert.equal(publicEvidence.reader.scope, 'release_landing_page_not_full_html_textbook');
assert.equal(publicEvidence.native_semantic_html_claimed, false);
assert.equal(publicEvidence.native_epub_claimed, false);
assert.equal(publicEvidence.mathml_claimed, false);
assert.equal(publicEvidence.tagged_pdf_claimed, false);
assert.equal(publicEvidence.accessibility_conformance_claimed, false);
assert.equal(publicEvidence.public_state_changed, false);

const publicMappings = [
  [`${base}/manifest.json`, 'docs/backend/b40/manifest.json'],
  [`${base}/views/B40.html`, 'docs/backend/b40/B40.html'],
  [`${base}/views/B40-pengajar.html`, 'docs/backend/b40/B40-pengajar.html'],
  [`${base}/data/learning-map.json`, 'docs/backend/b40/learning-map.json'],
  [`${base}/data/educator-map.json`, 'docs/backend/b40/educator-map.json'],
  [`${base}/data/concept-index.json`, 'docs/backend/b40/concept-index.json'],
  [`${base}/data/relation-index.json`, 'docs/backend/b40/relation-index.json'],
  [`${base}/data/rights-and-terms.json`, 'docs/backend/b40/rights-and-terms.json'],
  [`${base}/data/ledger-references.json`, 'docs/backend/b40/ledger-references.json'],
  [`${base}/data/public-evidence.json`, 'docs/backend/b40/public-evidence.json'],
  [`${base}/validation.json`, 'docs/backend/b40/validation.json'],
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
  ['native_migration_and_public_source_lock', `${base}/input/source-lock.json`],
  ['anonymous_native_public_readback', `${base}/input/public-native-readback.json`],
  ['component_rights_terminology_and_corrections', `${base}/data/rights-and-terms.json`],
  ['native_and_reversible_migration_ledgers', `${base}/data/ledger-references.json`],
  ['complete_concept_index', `${base}/data/concept-index.json`],
  ['complete_relation_index', `${base}/data/relation-index.json`],
]) {
  const {bytes, sha256} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-05'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
assert.ok(
  !overrides.semantic_adapters.B40
    || !overrides.semantic_adapters.B40.contract_version
    || overrides.semantic_adapters.B40.contract_version === manifest.contract,
  'Preserve a different admitted B40 contract',
);
overrides.semantic_adapters.B40 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_3541_native_units_13999_relations_114_concepts_1037_exact_exercise_answer_pairs_114_terms_307_corrections_11_rights_records_and_existing_22131_record_reversible_migration',
  evidence,
};
overrides.native_capabilities.B40 = {...(overrides.native_capabilities.B40 ?? {})};
for (const capability of [
  'unit_identity', 'terminology', 'translation_rights', 'corrections',
  'build', 'deterministic_replay', 'educator_unit_alignment', 'translation_ledger',
]) overrides.native_capabilities.B40[capability] = {status: 'verified', evidence};

const scope = 'Tiga pembaca, 17 bab, 57 bagian, seluruh 3.541 unit dan 13.999 relasi native, 1.037 pasangan latihan-jawaban eksak, 114 konsep/istilah, 307 koreksi, 11 rekaman hak komponen, dan proyeksi common-v1 reversibel 22.131 rekaman.';
const limitations = [
  'Adapter adalah proyeksi metadata dan bukti zero-copy; segmen, badan buku, sumber LaTeX, dan PDF tetap pada edisi publik native.',
  'Halaman publik native adalah halaman arahan rilis, bukan buku teks HTML; format pembaca yang terbukti adalah tiga PDF.',
  'Dua jawaban dipasok oleh edisi Indonesia dan diotorisasi oleh HLA-A0300; keduanya tidak dinyatakan sebagai terjemahan jawaban hulu.',
  'Backend native tidak menyatakan hasil belajar atau prasyarat. Prasyarat program A30 dan B10 tetap milik pembungkus kurikulum pusat.',
  'Sebanyak 302 aset dinyatakan dihasilkan saat build dan delapan bergantung pada toolchain eksternal; adapter tidak menjanjikan berkas unduhan yang tidak ada.',
  'Hak tetap pada 11 rekaman komponen; adapter tidak menerapkan satu lisensi payung.',
  'EPUB, HTML semantik buku, PDF bertag, MathML, runtime interaktif terhost, dan kesesuaian aksesibilitas tidak diklaim.',
];
const tool = {
  tool_id: 'b40.open_learner_hub',
  label: 'B40 · Aljabar Linear',
  href: 'backend/b40/B40.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/b40/B40.html'),
  resource: await identity('docs/backend/b40/learning-map.json'),
  evidence: await identity('docs/backend/b40/validation.json'),
  limitations,
};
assert.ok(
  !overrides.learner_tools.B40
    || overrides.learner_tools.B40.every(old => old.tool_id === tool.tool_id),
  'Preserve unrelated B40 tools',
);
overrides.learner_tools.B40 = [tool];

const old = overrides.educator_evidence.B40;
const teacher = await identity('docs/backend/b40/B40-pengajar.html');
const educatorMapIdentity = await identity('docs/backend/b40/educator-map.json');
const conceptIdentity = await identity('docs/backend/b40/concept-index.json');
const relationIdentity = await identity('docs/backend/b40/relation-index.json');
const educatorUrl = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/b40/B40-pengajar.html';
const resources = (old?.resources ?? []).filter(resource => ![
  'B40:educator-hub-v1', 'B40:educator-map-v1',
  'B40:concept-index-v1', 'B40:relation-index-v1',
].includes(resource.id));
resources.push({
  id: 'B40:educator-hub-v1',
  title: 'Pemilih unit, latihan, jawaban, konsep, dan provenans B40 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url: educatorUrl,
  scope,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
resources.push({
  id: 'B40:educator-map-v1',
  title: 'Peta 3.541 unit dan 1.037 pasangan latihan-jawaban B40',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/b40/educator-map.json',
  scope: 'Data pemilih unit dengan ID, hierarki, lokator, konsep, dan provenans jawaban tanpa badan buku.',
  bytes: educatorMapIdentity.bytes,
  sha256: educatorMapIdentity.sha256,
});
resources.push({
  id: 'B40:concept-index-v1',
  title: 'Indeks 114 konsep dan istilah B40',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/b40/concept-index.json',
  scope: 'Indeks konsep locale-neutral dan istilah Bahasa Indonesia dengan identitas native stabil.',
  bytes: conceptIdentity.bytes,
  sha256: conceptIdentity.sha256,
});
resources.push({
  id: 'B40:relation-index-v1',
  title: 'Indeks 13.999 relasi native B40',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/b40/relation-index.json',
  scope: 'Seluruh relasi native dan proyeksi nonduplikatif 1.037 pasangan latihan-jawaban.',
  bytes: relationIdentity.bytes,
  sha256: relationIdentity.sha256,
});
overrides.educator_evidence.B40 = {
  status: 'verified',
  verified_date: '2026-09-05',
  locator: educatorUrl,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: [
    'lesson_sequences', 'exercise_bank', 'remix_selectors',
    'staged_hints_answers_solutions', 'activities_labs',
    'solution_provenance', 'accessibility_accommodations',
  ],
  resources,
};
await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);

const learnerTarget = 'backend/authority/learner-delivery-overrides-v1.json';
const learner = await load(learnerTarget);
const pdf = {
  status: 'verified',
  format: 'application/pdf',
  url: 'https://zenodo.org/records/22070458/files/01_HEFFERON_LINEAR_ALGEBRA_ID_TEXTBOOK_2026.08.22.pdf?download=1',
  bytes: 8984459,
  sha256: '0462ddc8ffcc901efbc81205f79a249ae716e838a6ec32eda033444a90b8755e',
  scope: 'whole_course',
  evidence: {
    kind: 'anonymous_public_byte_readback',
    locator: `https://github.com/KokunoYumeto/program-matematika-indonesia/blob/main/${base}/input/public-native-readback.json`,
    verified_date: '2026-09-05',
  },
};
learner.courses.B40 = {
  primary: pdf,
  online_html: {
    status: 'available_unverified',
    format: 'text/html',
    url: 'https://kokunoyumeto.github.io/hefferon-linear-algebra-id/',
    scope: 'release_landing_page_not_full_html_textbook',
  },
  pdf,
  epub: {status: 'not_yet_produced'},
  portable_html: {status: 'not_yet_produced'},
  capabilities: {
    semantic_html: {status: 'not_yet_produced'},
    mathml: {status: 'not_yet_produced'},
    print_profile: {status: 'verified'},
    chapter_downloads: {status: 'not_yet_produced'},
  },
};
await writeFile(resolve(root, learnerTarget), `${JSON.stringify(learner, null, 2)}\n`);

console.log(JSON.stringify({
  state: 'pass',
  admitted_roles: ['B40'],
  contract: manifest.contract,
  native_locale: manifest.locale,
  public_state_changed: false,
}));
