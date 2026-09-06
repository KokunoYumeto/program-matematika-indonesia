import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/c60-capability-v1';
const load = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const identity = async path => {
  const bytes = await readFile(resolve(root, path));
  return {path, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')};
};

const manifest = await load(`${base}/manifest.json`);
const validation = await load(`${base}/validation.json`);
const packet = await load(`${base}/build/PACKET_BUILD_RECEIPT.json`);
const sourceLock = await load(`${base}/input/source-lock.json`);
const capabilities = await load(`${base}/data/capabilities.json`);
const learningMap = await load(`${base}/data/learning-map.json`);
const educatorMap = await load(`${base}/data/educator-map.json`);
const publicEvidence = await load(`${base}/data/public-evidence.json`);
const claimBoundary = await load(`${base}/data/claim-boundary.json`);
const rightsAndTerms = await load(`${base}/data/rights-and-terms.json`);

assert.equal(manifest.schema, 'c60-capability-manifest/1');
assert.equal(manifest.course_id, 'C60');
assert.equal(manifest.native_role_id, 'R014');
assert.equal(manifest.native_release, '1.0.0');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.content_policy, 'stable_native_ids_selected_metadata_routes_and_evidence_only');
assert.equal(manifest.strict_contract_schema_verified, true);
assert.equal(manifest.inputs.length, 77);
assert.equal(manifest.outputs.length, 15);
assert.deepEqual(manifest.projection, {
  accessibility_conformance_claimed: false,
  all_native_concepts_routed: true,
  all_native_ids_preserved: true,
  all_native_units_routed: true,
  assessment_functionality_claimed: false,
  central_course_truth_rewritten: false,
  common_virtual_backend_materialized: false,
  excluded_destination_used: false,
  exercise_support_invented: false,
  existing_reversible_migration_reused: true,
  full_offline_dependency_closure_claimed: false,
  historical_migration_receipt_rewritten: false,
  live_execution_claimed: false,
  public_state_changed: false,
  zero_copy_native_bodies: true,
});
for (const [key, value] of Object.entries({
  native_records: 5272,
  native_unique_ids: 5272,
  units: 548,
  effective_units: 544,
  unit_context_reader_routes: 548,
  unit_direct_reader_routes: 187,
  effective_unit_direct_reader_routes: 183,
  native_exercise_units: 101,
  native_solution_records: 0,
  concepts: 223,
  concepts_with_reader_routes: 223,
  terms: 239,
  corrections: 141,
  rights_components: 15,
  relations: 3297,
  learner_chapters: 5,
  learner_sections: 27,
  reader_mathml_elements: 2791,
  reader_pdf_pages: 138,
  common_virtual_records: 6967,
})) assert.equal(manifest.counts[key], value, `C60 count drift: ${key}`);
for (const item of manifest.outputs) {
  assert.deepEqual(await identity(`${base}/${item.path}`), {
    path: `${base}/${item.path}`,
    bytes: item.bytes,
    sha256: item.sha256,
  });
}

assert.equal(validation.schema, 'c60-capability-validation/1');
assert.equal(validation.state, 'pass');
assert.equal(validation.course_id, 'C60');
assert.equal(validation.contract, manifest.contract);
assert.deepEqual(validation.counts, manifest.counts);
assert.deepEqual(validation.projection_errors, []);
assert.equal(validation.strict_common_schema, 'pass');
assert.equal(validation.native_ids_verified, 5272);
assert.equal(validation.source_hashes_verified, 77);
assert.equal(validation.migration_receipt_replay_checks, 18);
assert.equal(validation.negative_fixtures.length, 41);
assert.ok(validation.negative_fixtures.every(row => row.state === 'rejected'));
assert.equal(validation.isolated_two_build_byte_identity.byte_identical, true);
assert.equal(validation.isolated_two_build_byte_identity.file_count, 16);

assert.equal(packet.schema, 'c60-capability-thin-packet-build-receipt/1');
assert.equal(packet.result, 'PASS');
assert.equal(packet.course_id, 'C60');
assert.equal(packet.two_build_byte_identity, true);
assert.equal(packet.native_inputs_included, 0);
assert.equal(packet.native_content_bodies_included, false);
assert.equal(packet.forbidden_payloads_included, false);
assert.equal(packet.local_profile_data_included, false);
assert.equal(packet.external_pinned_native_checkout_required_for_replay, true);
assert.equal(packet.public_state_changed, false);
assert.equal(packet.negative_fixtures_included, 41);
assert.deepEqual(packet.adapter_manifest, {...(await identity(`${base}/manifest.json`)), path: 'manifest.json'});
assert.deepEqual(packet.adapter_validation, {...(await identity(`${base}/validation.json`)), path: 'validation.json'});
assert.deepEqual(packet.archive, {...(await identity(`${base}/build/C60_THIN_CAPABILITY_METADATA_V1.zip`)), path: 'build/C60_THIN_CAPABILITY_METADATA_V1.zip'});
assert.deepEqual(packet.zip_checks, {
  crc_and_full_entry_readback: true,
  fixed_member_metadata: true,
  member_count: 23,
  payload_bytes: 6005680,
  sorted_member_order: true,
});

assert.equal(sourceLock.schema, 'c60-source-lock/1');
assert.equal(sourceLock.course_id, 'C60');
assert.equal(sourceLock.locale, 'id-ID');
assert.equal(sourceLock.native_role_id, 'R014');
assert.equal(sourceLock.input_count, 77);
assert.equal(sourceLock.inputs.length, 77);
assert.deepEqual(sourceLock.repository, {
  current_backend_tree: 'a5a8a7a3e010e6372c2c22051d1f922327f2f763',
  current_docs_tree: 'db6215012c8ff4b00a55668bbe7860fd57717e91',
  current_public_head: '66df945d1e5281bfc4758b733c13ac9254f00410',
  current_public_tree: '5132900227e1b1a06cdc3facac691e18a7bdb10f',
  current_source_tree: '5d0949f7917967079b11288180646ea83c0e0b1b',
  native_backend_unchanged_from_release_commit: true,
  native_release_commit: '11e27180632af3b90202ad38c063807c0d057766',
  native_source_unchanged_from_release_commit: true,
  release_backend_tree: 'a5a8a7a3e010e6372c2c22051d1f922327f2f763',
  release_source_tree: '5d0949f7917967079b11288180646ea83c0e0b1b',
  url: 'https://github.com/KokunoYumeto/yet-another-introductory-number-theory-textbook-id',
});
assert.deepEqual(sourceLock.migration_input, {
  bytes: 16003,
  path: 'backend/migrations/yaintt-id-v1/MIGRATION_RECEIPT.json',
  sha256: 'fa6d4636d61edee38969f39dd7f0e472cdffbfd74835c90e2a3159fa41721008',
});

assert.equal(capabilities.schema, 'c60-capability-summary/1');
assert.equal(capabilities.contract, manifest.contract);
assert.equal(capabilities.course_id, 'C60');
assert.deepEqual(capabilities.counts, manifest.counts);
assert.equal(capabilities.learner.all_native_unit_ids_routed, true);
assert.equal(capabilities.learner.all_concepts_routed, true);
assert.equal(capabilities.learner.direct_public_reflowable_reader, true);
assert.equal(capabilities.educator.all_native_unit_selector, true);
assert.equal(capabilities.educator.assessment_functionality, false);
assert.equal(capabilities.educator.live_execution, false);
assert.equal(capabilities.reproducibility.existing_reversible_migration_replayed, true);
assert.equal(capabilities.reproducibility.existing_exact_reverse_extraction_records, 5272);
assert.equal(capabilities.rights.component_specific, true);
assert.equal(capabilities.rights.blanket_license_claimed, false);

assert.equal(learningMap.contract, manifest.contract);
assert.equal(learningMap.course_id, 'C60');
assert.equal(learningMap.locale, 'id-ID');
assert.equal(learningMap.units.length, 5);
assert.equal(learningMap.prerequisite_routes.length, 2);
assert.equal(learningMap.labs.length, 0);
assert.equal(learningMap.environments.length, 0);
assert.equal(learningMap.units.flatMap(row => row.exercises).length, 101);
assert.ok(learningMap.units.flatMap(row => row.exercises).every(row =>
  ['hint', 'check', 'solution'].every(key => row[key].status === 'not_present' && row[key].label === 'source_has_none')
));

assert.equal(educatorMap.schema, 'c60-educator-map/1');
assert.equal(educatorMap.contract, manifest.contract);
assert.equal(educatorMap.course_id, 'C60');
assert.equal(educatorMap.locale, 'id-ID');
assert.equal(educatorMap.selector.units.length, 548);
assert.equal(educatorMap.chapter_routes.length, 5);
assert.equal(educatorMap.section_routes.length, 27);
assert.equal(educatorMap.selector.body_content_embedded, false);
assert.equal(educatorMap.claim_boundary.assessment_functionality_available, false);
assert.equal(educatorMap.claim_boundary.live_execution_available, false);

assert.equal(publicEvidence.schema, 'c60-public-evidence/1');
assert.equal(publicEvidence.course_id, 'C60');
assert.equal(publicEvidence.github.current_public_head, sourceLock.repository.current_public_head);
assert.equal(publicEvidence.github.current_public_tree, sourceLock.repository.current_public_tree);
assert.equal(publicEvidence.github.native_release_commit, sourceLock.repository.native_release_commit);
assert.equal(publicEvidence.reader.reflowable_html, true);
assert.equal(publicEvidence.reader.reader_pages, 10);
assert.equal(publicEvidence.reader.chapters, 5);
assert.equal(publicEvidence.reader.sections, 27);
assert.equal(publicEvidence.reader.mathml_elements_observed, 2791);
assert.equal(publicEvidence.reader.pdf_pages, 138);
assert.equal(publicEvidence.reader.pdf_bytes, 962527);
assert.equal(publicEvidence.reader.pdf_sha256, '1ded3c6844b656347259b464bf21526fdc32dc2246c73ac58ab76ed28688eefc');
assert.equal(publicEvidence.release.zenodo_record, 'https://zenodo.org/records/22052196');
assert.equal(publicEvidence.release.zenodo_version_doi, '10.5281/zenodo.22052196');
assert.equal(publicEvidence.release.release_artifacts.length, 4);
assert.equal(publicEvidence.public_state_changed, false);

assert.deepEqual(claimBoundary, capabilities.claim_boundary);
for (const key of [
  'accessibility_conformance_claimed', 'central_course_truth_rewritten',
  'common_virtual_backend_materialized', 'excluded_destination_used',
  'exercise_bodies_copied', 'full_offline_dependency_closure_claimed',
  'historical_migration_receipt_rewritten', 'live_execution_claimed',
  'mathml_presence_treated_as_conformance', 'native_bodies_copied',
  'native_unit_outcomes_invented', 'native_unit_prerequisites_invented',
  'public_state_changed', 'source_attribution_values_embedded',
]) assert.equal(claimBoundary[key], false);
for (const key of [
  'assessment_instances', 'credential_assertion_instances', 'invented_exercise_instances',
  'learner_attempt_instances', 'learner_result_instances', 'learner_submission_instances',
  'native_solution_records',
]) assert.equal(claimBoundary[key], 0);
assert.equal(rightsAndTerms.component_rights.length, 15);
assert.equal(rightsAndTerms.terminology.length, 239);
assert.equal(rightsAndTerms.corrections.length, 141);
assert.equal(rightsAndTerms.body_content_embedded, false);
assert.equal(rightsAndTerms.blanket_license_claimed, false);

const publicMappings = [
  [`${base}/manifest.json`, 'docs/backend/c60/manifest.json'],
  [`${base}/views/C60.html`, 'docs/backend/c60/C60.html'],
  [`${base}/views/C60-pengajar.html`, 'docs/backend/c60/C60-pengajar.html'],
  [`${base}/data/capabilities.json`, 'docs/backend/c60/capabilities.json'],
  [`${base}/data/learning-map.json`, 'docs/backend/c60/learning-map.json'],
  [`${base}/data/educator-map.json`, 'docs/backend/c60/educator-map.json'],
  [`${base}/data/concept-index.json`, 'docs/backend/c60/concept-index.json'],
  [`${base}/data/relation-index.json`, 'docs/backend/c60/relation-index.json'],
  [`${base}/data/rights-and-terms.json`, 'docs/backend/c60/rights-and-terms.json'],
  [`${base}/data/ledger-references.json`, 'docs/backend/c60/ledger-references.json'],
  [`${base}/data/native-id-index.json`, 'docs/backend/c60/native-id-index.json'],
  [`${base}/data/public-evidence.json`, 'docs/backend/c60/public-evidence.json'],
  [`${base}/data/claim-boundary.json`, 'docs/backend/c60/claim-boundary.json'],
  [`${base}/validation.json`, 'docs/backend/c60/validation.json'],
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
  ['dual_revision_native_source_lock', `${base}/input/source-lock.json`],
  ['verified_native_public_evidence', `${base}/data/public-evidence.json`],
  ['component_rights_terminology_and_corrections', `${base}/data/rights-and-terms.json`],
  ['native_and_reversible_migration_ledgers', `${base}/data/ledger-references.json`],
  ['complete_native_id_index', `${base}/data/native-id-index.json`],
  ['complete_concept_index', `${base}/data/concept-index.json`],
  ['complete_relation_index', `${base}/data/relation-index.json`],
]) {
  const {bytes, sha256} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-06'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
assert.ok(
  !overrides.semantic_adapters.C60
    || !overrides.semantic_adapters.C60.contract_version
    || overrides.semantic_adapters.C60.contract_version === manifest.contract,
  'Preserve a different admitted C60 contract',
);
overrides.semantic_adapters.C60 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_5272_native_ids_548_units_223_concepts_3297_relations_101_exercises_239_terms_141_corrections_15_rights_and_existing_6967_record_reversible_migration',
  evidence,
};
overrides.native_capabilities.C60 = {...(overrides.native_capabilities.C60 ?? {})};
for (const capability of [
  'unit_identity', 'terminology', 'translation_rights', 'corrections',
  'build', 'deterministic_replay', 'educator_unit_alignment', 'translation_ledger',
]) overrides.native_capabilities.C60[capability] = {status: 'verified', evidence};

const scope = 'Seluruh 5.272 ID native, 548 unit, 223 konsep, 3.297 relasi, 101 latihan, 239 istilah, 141 koreksi, 15 rekaman hak, lima bab, dan 27 bagian; proyeksi common 6.967 rekaman tetap reversibel dan zero-copy.';
const limitations = [
  'Adapter memproyeksikan identitas, struktur, istilah, koreksi, hak, dan bukti; badan buku dan prompt latihan tetap pada edisi native publik.',
  'Semua 101 latihan adalah identitas native. Sumber tidak menyediakan petunjuk, cek, jawaban, solusi, penilaian otomatis, atau buku panduan pengajar.',
  'Sembilan puluh lima latihan tidak memiliki jangkar HTML tersendiri; rute menggunakan bagian induk yang telah diverifikasi dan tidak membuat deep link palsu.',
  'Empat unit yang disupersesi tetap dipertahankan; 544 unit efektif tidak menggantikan inventaris native 548 unit.',
  'Prasyarat B10 dan C30 adalah jangkar tingkat kursus native; hasil belajar dan prasyarat per unit tidak direka.',
  'Pembaca memiliki MathML dan PDF 138 halaman, tetapi kesesuaian WCAG, PDF bertanda, EPUB, dan penutupan dependensi luring penuh tidak diklaim.',
];
const tool = {
  tool_id: 'c60.open_learner_hub',
  label: 'C60 · Teori Bilangan dan Kriptologi',
  href: 'backend/c60/C60.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/c60/C60.html'),
  resource: await identity('docs/backend/c60/learning-map.json'),
  evidence: await identity('docs/backend/c60/validation.json'),
  limitations,
};
assert.ok(
  !overrides.learner_tools.C60
    || overrides.learner_tools.C60.every(old => old.tool_id === tool.tool_id),
  'Preserve unrelated C60 learner tools',
);
overrides.learner_tools.C60 = [tool];

const educatorUrl = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c60/C60-pengajar.html';
const resources = (overrides.educator_evidence.C60?.resources ?? []).filter(resource => ![
  'C60:educator-hub-v1', 'C60:educator-map-v1', 'C60:concept-index-v1',
  'C60:relation-index-v1', 'C60:rights-and-terms-v1', 'C60:ledger-references-v1',
  'C60:native-id-index-v1',
].includes(resource.id));
for (const row of [
  ['C60:educator-hub-v1', 'Pemilih unit, konsep, latihan, istilah, dan koreksi C60', 'teacher-guide', educatorUrl, 'docs/backend/c60/C60-pengajar.html', scope],
  ['C60:educator-map-v1', 'Peta pengajar atas seluruh 548 unit native C60', 'educator-data', 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c60/educator-map.json', 'docs/backend/c60/educator-map.json', 'Peta zero-copy atas hierarki unit, konsep, latihan, koreksi, supersesi, dan rute pembaca.'],
  ['C60:concept-index-v1', 'Indeks 223 konsep C60', 'educator-data', 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c60/concept-index.json', 'docs/backend/c60/concept-index.json', 'Indeks konsep native dan rute pembaca tanpa menyalin badan buku.'],
  ['C60:relation-index-v1', 'Indeks 3.297 relasi native C60', 'educator-data', 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c60/relation-index.json', 'docs/backend/c60/relation-index.json', 'Seluruh relasi native, termasuk 192 prasyarat konsep dan 398 relasi latihan-konsep.'],
  ['C60:rights-and-terms-v1', 'Hak komponen, 239 istilah, dan 141 koreksi C60', 'terminology-register', 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c60/rights-and-terms.json', 'docs/backend/c60/rights-and-terms.json', 'Hak, istilah, dan koreksi dipertahankan pada identitas native tanpa lisensi payung.'],
  ['C60:ledger-references-v1', 'Rujukan ledger dan migrasi reversibel C60', 'provenance-ledger', 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c60/ledger-references.json', 'docs/backend/c60/ledger-references.json', 'Rujukan sumber, target, build, dan migrasi; badan materi tidak disalin.'],
  ['C60:native-id-index-v1', 'Indeks hash seluruh 5.272 ID native C60', 'identity-index', 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c60/native-id-index.json', 'docs/backend/c60/native-id-index.json', 'Indeks identitas dan hash native lengkap untuk replay dan pemeriksaan silang.'],
]) {
  const [id, title, resource_type, url, path, resourceScope] = row;
  const fact = await identity(path);
  resources.push({id, title, resource_type, status: 'verified', url, scope: resourceScope, bytes: fact.bytes, sha256: fact.sha256});
}
const teacher = await identity('docs/backend/c60/C60-pengajar.html');
overrides.educator_evidence.C60 = {
  status: 'verified',
  verified_date: '2026-09-06',
  locator: educatorUrl,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: ['lesson_sequences', 'exercise_bank', 'prerequisite_diagnostics', 'remix_selectors', 'accessibility_accommodations'],
  resources,
};
await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);

const learnerTarget = 'backend/authority/learner-delivery-overrides-v1.json';
const learner = await load(learnerTarget);
const receipt = {
  kind: 'pinned_native_public_evidence',
  locator: `https://github.com/KokunoYumeto/program-matematika-indonesia/blob/main/${base}/data/public-evidence.json`,
  verified_date: '2026-09-06',
};
const pdf = {
  status: 'verified',
  format: 'application/pdf',
  url: 'https://kokunoyumeto.github.io/yet-another-introductory-number-theory-textbook-id/YAINTT_ID.pdf',
  bytes: 962527,
  sha256: '1ded3c6844b656347259b464bf21526fdc32dc2246c73ac58ab76ed28688eefc',
  scope: 'whole_course',
  evidence: receipt,
};
learner.courses.C60 = {
  ...(learner.courses.C60 ?? {}),
  primary: {
    status: 'verified',
    format: 'text/html',
    url: 'https://kokunoyumeto.github.io/yet-another-introductory-number-theory-textbook-id/reader/index.html',
    bytes: 11613,
    sha256: '59bf257234975ccad7314ce442da296cedaaa347fc80aae1e63bf17c2d01d77b',
    scope: 'whole_course',
    evidence: receipt,
  },
  online_html: {
    status: 'verified',
    format: 'text/html',
    url: 'https://kokunoyumeto.github.io/yet-another-introductory-number-theory-textbook-id/reader/index.html',
    bytes: 11613,
    sha256: '59bf257234975ccad7314ce442da296cedaaa347fc80aae1e63bf17c2d01d77b',
    entry_point: 'index.html',
    inventory_count: 10,
    scope: 'whole_course',
    evidence: receipt,
  },
  pdf,
  capabilities: {
    semantic_html: {status: 'verified', evidence: {...receipt, html_pages: 10, local_links_checked: 657}},
    mathml: {status: 'verified', evidence: {...receipt, mathml_count: 2791}},
    print_profile: {status: 'verified', evidence: {...receipt, pdf_pages: 138, tagged: false}},
    chapter_downloads: {status: 'not_yet_produced'},
  },
};
await writeFile(resolve(root, learnerTarget), `${JSON.stringify(learner, null, 2)}\n`);

console.log(JSON.stringify({
  state: 'pass',
  admitted_roles: ['C60'],
  contract: manifest.contract,
  native_locale: manifest.locale,
  public_files_staged: publicMappings.length,
  public_state_changed: false,
}));
