import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/c70-capability-v1';
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

assert.equal(manifest.schema, 'c70-capability-manifest/1');
assert.equal(manifest.course_id, 'C70');
assert.equal(manifest.native_role_id, 'R012');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.contract_2_3_1_conformance, 'not_claimed');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.native_family, 'applied_combinatorics_pretext_backend');
assert.equal(manifest.native_release, '2026.08.22.2');
assert.equal(manifest.maintenance_release, '2026.09.04.1');
assert.equal(manifest.content_policy, 'stable_native_ids_selected_metadata_and_evidence_only');
assert.deepEqual(manifest.projection, {
  all_relation_ids_indexed: true,
  all_unit_ids_indexed: true,
  central_course_truth_rewritten: false,
  common_virtual_backend_materialized: false,
  exercise_support_projection_double_counted: false,
  existing_reversible_migration_reused: true,
  figshare_active_destination_used: false,
  historical_migration_receipt_rewritten: false,
  native_ids_preserved: true,
  native_target_edition_promoted: false,
  public_state_changed: false,
  unlinked_solution_units_inferred: false,
  zero_copy_native_bodies: true,
});
assert.equal(manifest.inputs.length, 37);
assert.equal(manifest.outputs.length, 15);
assert.deepEqual(manifest.counts, capabilities.counts);
assert.equal(manifest.counts.units, 1408);
assert.equal(manifest.counts.relations, 6334);
assert.equal(manifest.counts.concepts, 701);
assert.equal(manifest.counts.exercises, 407);
assert.equal(manifest.counts.explicit_support_relations, 82);
assert.equal(manifest.counts.explicit_solves_relations, 57);
assert.equal(manifest.counts.explicit_answers_relations, 9);
assert.equal(manifest.counts.explicit_hints_relations, 16);
assert.equal(manifest.counts.solution_units, 84);
assert.equal(manifest.counts.terminology_registry_rows, 633);
assert.equal(manifest.counts.terminology_review_rows, 633);
assert.equal(manifest.counts.corrections, 354);
assert.equal(manifest.counts.native_canonical_records, 19048);
assert.equal(manifest.counts.native_physical_jsonl_rows, 19130);
assert.equal(manifest.counts.common_virtual_records, 19049);
assert.equal(manifest.counts.reader_pages, 350);
assert.equal(manifest.counts.public_reader_routes_verified, 19);

assert.equal(validation.schema, 'c70-capability-validation/1');
assert.equal(validation.state, 'pass');
assert.equal(validation.source_hashes_verified, 37);
assert.equal(validation.native_export_hashes_verified, 23);
assert.equal(validation.negative_fixtures.length, 32);
assert.ok(validation.negative_fixtures.every(row => row.state === 'rejected'));
assert.deepEqual(validation.counts, manifest.counts);
assert.equal(validation.isolated_two_build_byte_identity.byte_identical, true);
assert.equal(validation.isolated_two_build_byte_identity.file_count, 16);

assert.equal(sourceLock.schema, 'c70-source-lock/1');
assert.equal(sourceLock.native_repository.current_public_head, '8c9615969a4c4e9316166f38ac827a932a87a919');
assert.equal(sourceLock.native_repository.current_public_tree, 'c538dacb6bb51f15cdacefffd473ec8899f677f3');
assert.equal(sourceLock.native_repository.source_commit, '33b20df670d1f8d98266cd2f4a287a79b01649ea');
assert.equal(sourceLock.native_repository.source_tree, 'a8e604cc80fbb5e1a312fa26baab2b17d2975b77');
assert.equal(sourceLock.export_inputs.length, 23);
assert.equal(sourceLock.control_inputs.length, 11);
assert.equal(sourceLock.migration_input.path, 'backend/migrations/applied-combinatorics-id-v1/MIGRATION_RECEIPT.json');
assert.equal(sourceLock.public_readback_input.path, `${base}/input/public-native-readback.json`);
assert.deepEqual([
  sourceLock.export_manifest_input,
  ...sourceLock.export_inputs,
  ...sourceLock.control_inputs,
  sourceLock.migration_input,
  sourceLock.public_readback_input,
], manifest.inputs);

assert.equal(learningMap.schema, 'c70-learning-map/1');
assert.equal(learningMap.blocks.length, 19);
assert.equal(learningMap.route.all_unit_ids.length, 1408);
assert.equal(new Set(learningMap.route.all_unit_ids).size, 1408);
assert.equal(learningMap.route.block_ids.length, 19);
assert.deepEqual(learningMap.program_prerequisites, ['B10']);
assert.equal(learningMap.prerequisite_scope, 'native_course_level_external_B10_anchor_not_per_unit_invention');

assert.equal(educatorMap.schema, 'c70-educator-map/1');
assert.equal(educatorMap.selector.units.length, 1408);
assert.equal(educatorMap.selector.exercise_support.length, 82);
assert.equal(educatorMap.selector.body_content_embedded, false);
assert.equal(educatorMap.claim_boundary.unlinked_solution_units_present, 27);
assert.equal(educatorMap.claim_boundary.unlinked_solution_units_inferred, false);

assert.equal(conceptIndex.schema, 'c70-concept-index/1');
assert.equal(conceptIndex.concepts.length, 701);
assert.equal(relationIndex.schema, 'c70-relation-index/1');
assert.equal(relationIndex.relations.length, 6334);
assert.equal(relationIndex.exercise_support_projection.length, 82);
assert.equal(relationIndex.exercise_support_projection_rows, 82);
assert.equal(relationIndex.specialized_projection_duplicate_rows_materialized, 0);

assert.equal(ledgers.schema, 'c70-ledger-references/1');
assert.equal(ledgers.export_members.length, 23);
assert.equal(ledgers.common_projection.record_count, 19049);
assert.equal(ledgers.common_projection.exact_reverse_extraction, 19048);
assert.equal(ledgers.common_projection.projection_rows_verified_not_migrated_twice, 82);
assert.equal(ledgers.native_target_edition.status, 'draft');
assert.equal(ledgers.projection.native_bodies_copied, false);
assert.equal(ledgers.projection.common_virtual_backend_materialized, false);

assert.equal(publicReadback.schema, 'c70-native-public-readback/1');
assert.equal(publicReadback.access_mode, 'anonymous_no_credentials');
assert.equal(publicReadback.github.current_head, sourceLock.native_repository.current_public_head);
assert.equal(publicReadback.github.current_tree, sourceLock.native_repository.current_public_tree);
assert.equal(publicReadback.github.raw_files.length, 12);
assert.equal(publicReadback.github.release.fully_downloaded_and_sha256_verified.length, 3);
assert.equal(publicReadback.zenodo.records.length, 2);
assert.equal(publicReadback.zenodo.all_open, true);
assert.equal(publicReadback.reader.pages.length, 19);
assert.equal(publicReadback.checks.external_state_changed, false);

assert.equal(publicEvidence.schema, 'c70-public-evidence/1');
assert.equal(publicEvidence.github.current_public_head, sourceLock.native_repository.current_public_head);
assert.equal(publicEvidence.github.current_public_tree, sourceLock.native_repository.current_public_tree);
assert.equal(publicEvidence.github.release_assets.length, 5);
assert.equal(publicEvidence.zenodo.reader_record_id, 22062005);
assert.equal(publicEvidence.zenodo.maintenance_record_id, 22308618);
assert.equal(publicEvidence.zenodo.all_records_open, true);
assert.equal(publicEvidence.reader.pdf_pages, 350);
assert.equal(publicEvidence.reader.online_html, true);
assert.equal(publicEvidence.reader.tagged_pdf_claimed, false);
assert.equal(publicEvidence.reader.mathml_claimed, false);
assert.equal(publicEvidence.public_state_changed, false);

assert.equal(rightsAndTerms.schema, 'c70-rights-and-terms/1');
assert.equal(rightsAndTerms.component_rights.length, 6);
assert.equal(rightsAndTerms.terminology.length, 633);
assert.equal(rightsAndTerms.terminology_registry.length, 633);
assert.equal(rightsAndTerms.terminology_review_log.length, 633);
assert.equal(rightsAndTerms.corrections.length, 354);
assert.equal(rightsAndTerms.blanket_license_claimed, false);
assert.deepEqual(claimBoundary, capabilities.claim_boundary);
for (const key of ['learner_attempt_instances', 'learner_submission_instances', 'learner_result_instances', 'credential_assertion_instances']) assert.equal(claimBoundary[key], 0);
assert.equal(claimBoundary.native_target_edition_state, 'draft');
assert.equal(claimBoundary.native_unit_outcomes_invented, false);
assert.equal(claimBoundary.native_unit_prerequisites_invented, false);
assert.equal(claimBoundary.unlinked_solution_units_inferred, false);
assert.equal(claimBoundary.native_bodies_copied, false);
assert.equal(claimBoundary.common_virtual_backend_materialized, false);

for (const item of manifest.outputs) {
  assert.deepEqual(await identity(`${base}/${item.path}`), {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256});
}

const publicMappings = [
  [`${base}/views/C70.html`, 'docs/backend/c70/C70.html'],
  [`${base}/views/C70-pengajar.html`, 'docs/backend/c70/C70-pengajar.html'],
  [`${base}/data/learning-map.json`, 'docs/backend/c70/learning-map.json'],
  [`${base}/data/educator-map.json`, 'docs/backend/c70/educator-map.json'],
  [`${base}/data/concept-index.json`, 'docs/backend/c70/concept-index.json'],
  [`${base}/data/relation-index.json`, 'docs/backend/c70/relation-index.json'],
  [`${base}/data/rights-and-terms.json`, 'docs/backend/c70/rights-and-terms.json'],
  [`${base}/data/ledger-references.json`, 'docs/backend/c70/ledger-references.json'],
  [`${base}/data/public-evidence.json`, 'docs/backend/c70/public-evidence.json'],
  [`${base}/validation.json`, 'docs/backend/c70/validation.json'],
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
  ['complete_concept_index', `${base}/data/concept-index.json`],
  ['complete_relation_index', `${base}/data/relation-index.json`],
]) {
  const {bytes, sha256} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-05'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
assert.ok(!overrides.semantic_adapters.C70 || !overrides.semantic_adapters.C70.contract_version || overrides.semantic_adapters.C70.contract_version === manifest.contract, 'Preserve a different admitted C70 contract');
overrides.semantic_adapters.C70 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_1408_native_units_6334_relations_701_concepts_407_exercises_82_explicit_support_relations_633_terms_354_corrections_and_existing_19048_record_reversible_migration',
  evidence,
};
overrides.native_capabilities.C70 = {...(overrides.native_capabilities.C70 ?? {})};
for (const capability of ['unit_identity', 'terminology', 'translation_rights', 'corrections', 'build', 'deterministic_replay', 'educator_unit_alignment', 'translation_ledger']) {
  overrides.native_capabilities.C70[capability] = {status: 'verified', evidence};
}

const scope = 'Sembilan belas blok belajar, seluruh 1.408 unit native, 6.334 relasi, 701 konsep, 407 latihan, 82 pasangan dukungan eksplisit, 633 istilah, 354 koreksi, dan proyeksi common-v1 reversibel 19.049 rekaman.';
const limitations = [
  'Adapter adalah proyeksi metadata dan bukti zero-copy; badan buku, PDF, sumber PreTeXt, dan pembaca HTML lengkap tetap pada edisi publik native.',
  'Status native edisi target tetap draft; klaim publiknya adalah draf Bahasa Indonesia lengkap yang diperiksa mesin tanpa klaim tinjauan manusia.',
  'Dari 84 unit solusi, hanya 57 relasi solves eksplisit dipetakan. Dua puluh tujuh unit solusi lainnya tidak dipasangkan secara rekaan.',
  'Sembilan relasi jawaban dan 16 relasi petunjuk dipertahankan terpisah; proyeksi 82 baris tidak dihitung lagi sebagai relasi native baru.',
  'Satu xref yang tidak terselesaikan berada pada sumber hulu beku; target Bahasa Indonesia memiliki nol xref tidak terselesaikan.',
  'Prasyarat B10 adalah jangkar eksternal tingkat kursus; adapter tidak menciptakan hasil belajar atau prasyarat per unit.',
  'Pembaca native tidak mengklaim PDF bertanda atau MathML; adapter tidak menaikkan klaim aksesibilitas itu.',
];
const tool = {
  tool_id: 'c70.open_learner_hub',
  label: 'C70 · Kombinatorika Terapan',
  href: 'backend/c70/C70.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/c70/C70.html'),
  resource: await identity('docs/backend/c70/learning-map.json'),
  evidence: await identity('docs/backend/c70/validation.json'),
  limitations,
};
assert.ok(!overrides.learner_tools.C70 || overrides.learner_tools.C70.every(old => old.tool_id === tool.tool_id), 'Preserve unrelated C70 tools');
overrides.learner_tools.C70 = [tool];

const teacher = await identity('docs/backend/c70/C70-pengajar.html');
const educatorMapIdentity = await identity('docs/backend/c70/educator-map.json');
const conceptIdentity = await identity('docs/backend/c70/concept-index.json');
const relationIdentity = await identity('docs/backend/c70/relation-index.json');
const educatorUrl = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c70/C70-pengajar.html';
const resources = (overrides.educator_evidence.C70?.resources ?? []).filter(resource => ![
  'C70:educator-hub-v1',
  'C70:educator-map-v1',
  'C70:concept-index-v1',
  'C70:relation-index-v1',
].includes(resource.id));
resources.push({
  id: 'C70:educator-hub-v1',
  title: 'Pemilih unit, konsep, dan dukungan latihan C70 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url: educatorUrl,
  scope: `${scope} Ekspor JSON mempertahankan hanya relasi dukungan yang dinyatakan native.`,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
resources.push({
  id: 'C70:educator-map-v1',
  title: 'Peta 1.408 unit native dan 82 dukungan latihan C70',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c70/educator-map.json',
  scope: 'Data pemilih unit dengan hierarki, hash, konsep, dan pasangan dukungan eksplisit tanpa badan buku.',
  bytes: educatorMapIdentity.bytes,
  sha256: educatorMapIdentity.sha256,
});
resources.push({
  id: 'C70:concept-index-v1',
  title: 'Indeks 701 konsep C70',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c70/concept-index.json',
  scope: 'Indeks konsep native dengan penggunaan unit dan istilah terkait.',
  bytes: conceptIdentity.bytes,
  sha256: conceptIdentity.sha256,
});
resources.push({
  id: 'C70:relation-index-v1',
  title: 'Indeks 6.334 relasi native C70',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c70/relation-index.json',
  scope: 'Seluruh relasi native dan proyeksi nonduplikatif 82 dukungan latihan.',
  bytes: relationIdentity.bytes,
  sha256: relationIdentity.sha256,
});
overrides.educator_evidence.C70 = {
  status: 'verified',
  verified_date: '2026-09-05',
  locator: educatorUrl,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: ['lesson_sequences', 'exercise_bank', 'remix_selectors', 'solution_provenance', 'accessibility_accommodations'],
  resources,
};
await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);

const learnerTarget = 'backend/authority/learner-delivery-overrides-v1.json';
const learner = await load(learnerTarget);
const pdf = {
  status: 'verified',
  format: 'application/pdf',
  url: 'https://zenodo.org/records/22062005/files/00_KOMBINATORIKA_TERAPAN_ID-ID_COMPLETE_LINKED_READER_2026.08.22.2.pdf?download=1',
  bytes: 7487263,
  sha256: '6e0e3c0e3b42f283b551fc6c993acc4101d850edc0f350cbfe3c3e408f271e30',
  scope: 'whole_course',
  evidence: {
    kind: 'anonymous_public_byte_readback',
    locator: `https://github.com/KokunoYumeto/program-matematika-indonesia/blob/main/${base}/input/public-native-readback.json`,
    verified_date: '2026-09-05',
  },
};
learner.courses.C70 = {
  ...(learner.courses.C70 ?? {}),
  primary: pdf,
  online_html: {
    status: 'available_unverified',
    format: 'text/html',
    url: 'https://kokunoyumeto.github.io/applied-combinatorics-id/',
    scope: 'whole_course',
  },
  pdf,
  portable_html: {
    status: 'available_unverified',
    format: 'application/zip+html',
    url: 'https://zenodo.org/records/22062005/files/03_KOMBINATORIKA_TERAPAN_ID-ID_HTML_READER_2026.08.22.2.zip?download=1',
    bytes: 227102546,
    sha256: 'c6f1ace9b5c720421f1769dc3f92b0d692f067c15eb2950317092e24035e8c55',
    entry_point: 'index.html',
    inventory_count: 1500,
    scope: 'whole_course',
    dependency_free: false,
    evidence: {
      kind: 'anonymous_public_inventory_and_head_readback',
      locator: `https://github.com/KokunoYumeto/program-matematika-indonesia/blob/main/${base}/input/public-native-readback.json`,
      verified_date: '2026-09-05',
    },
  },
  capabilities: {
    semantic_html: {status: 'verified'},
    mathml: {status: 'not_yet_produced'},
    print_profile: {status: 'verified'},
    chapter_downloads: {status: 'not_yet_produced'},
  },
};
await writeFile(resolve(root, learnerTarget), `${JSON.stringify(learner, null, 2)}\n`);

console.log(JSON.stringify({state: 'pass', admitted_roles: ['C70'], contract: manifest.contract, native_locale: manifest.locale, public_state_changed: false}));
