import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/b90-capability-v1';
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

assert.equal(manifest.schema, 'b90-capability-manifest/1');
assert.equal(manifest.course_id, 'B90');
assert.equal(manifest.native_course_id, 'urn:interlanguage:r010:course:b90');
assert.equal(manifest.native_family, 'grinstead_snell_probability');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.content_policy, 'identity_structure_terminology_rights_evidence_only');
assert.equal(manifest.outputs.length, 30);
assert.deepEqual(manifest.inputs, sourceLock.inputs);
assert.deepEqual(manifest.projection, {
  central_course_truth_rewritten: false,
  component_rights_preserved: true,
  excluded_supplement_boundary_preserved: true,
  external_pinned_native_checkout_required_for_replay: true,
  native_bodies_copied: false,
  native_ids_preserved: true,
  public_state_changed: false,
  reversible_exchange_claimed: false,
});

const counts = manifest.counts;
assert.equal(counts.native_records, 4716);
assert.equal(counts.units, 800);
assert.equal(counts.chapters, 12);
assert.equal(counts.sections, 33);
assert.equal(counts.exercises, 711);
assert.equal(counts.pdf_pages, 554);
assert.equal(counts.concepts, 91);
assert.equal(counts.relations, 1694);
assert.equal(counts.terms, 119);
assert.equal(counts.corrections, 152);
assert.equal(counts.component_rights, 4);
assert.equal(counts.excluded_supplement_records, 1159);
assert.equal(counts.excluded_answer_records, 287);
assert.deepEqual(counts.correction_statuses, {
  corrected_in_translation: 4,
  open: 144,
  partially_corrected_in_translation: 1,
  partly_corrected_in_translation: 1,
  resolved: 2,
});
assert.deepEqual(counts.term_statuses, {admitted: 117, superseded: 2});
assert.deepEqual(counts.unit_kinds, {
  backmatter: 1,
  'book-shell': 1,
  chapter: 12,
  exercise: 711,
  'exercise-set': 33,
  frontmatter: 1,
  modified_edition_history: 1,
  preface: 1,
  publication_notice: 1,
  section: 33,
  'section-fragment': 5,
});
assert.deepEqual(counts.relation_kinds, {
  contains: 787,
  has_target_expression: 2,
  translates: 786,
  uses_asset: 119,
});
for (const item of manifest.outputs) {
  assert.deepEqual(
    await identity(`${base}/${item.path}`),
    {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256},
  );
}

assert.equal(validation.schema, 'b90-capability-validation/1');
assert.equal(validation.result, 'pass');
assert.equal(validation.course_id, 'B90');
assert.deepEqual(validation.counts, counts);
assert.equal(validation.negative_fixtures.length, 12);
assert.ok(validation.negative_fixtures.every(row => row.result === 'rejected'));
assert.equal(validation.checks.canonical_machine_files, true);
assert.equal(validation.checks.committed_projection_matches_native, true);
assert.equal(validation.checks.component_specific_rights_preserved, true);
assert.equal(validation.checks.excluded_supplement_boundary_preserved, true);
assert.equal(validation.checks.native_segment_bodies_absent, true);
assert.equal(validation.checks.public_hash_receipts_preserved, 9);
assert.equal(validation.checks.public_reader_kind, 'page_based_pdfjs');
assert.equal(validation.checks.unit_identities_rendered_for_educator, 800);
assert.equal(validation.checks.two_run_build_identity.file_count, 31);
assert.equal(validation.checks.two_run_build_identity.tree_sha256, 'e20d19553ea519152df88671135d4259c518005966fea4f59ceaec910bfdbf2f');

assert.equal(packageReceipt.schema, 'b90-capability-thin-packet-build-receipt/1');
assert.equal(packageReceipt.result, 'PASS');
assert.equal(packageReceipt.two_build_byte_identity, true);
assert.equal(packageReceipt.negative_fixtures_included, 12);
assert.equal(packageReceipt.native_inputs_included, 0);
assert.equal(packageReceipt.native_content_bodies_included, false);
assert.equal(packageReceipt.answer_supplement_included, false);
assert.equal(packageReceipt.forbidden_payloads_included, false);
assert.equal(packageReceipt.local_profile_data_included, false);
assert.equal(packageReceipt.external_pinned_native_checkout_required_for_replay, true);
assert.equal(packageReceipt.reversible_exchange_claimed, false);
assert.equal(packageReceipt.public_state_changed, false);
assert.deepEqual(packageReceipt.adapter_manifest, {...(await identity(`${base}/manifest.json`)), path: 'manifest.json'});
assert.deepEqual(packageReceipt.adapter_validation, {...(await identity(`${base}/validation.json`)), path: 'validation.json'});
assert.deepEqual(packageReceipt.archive, {...(await identity(`${base}/build/B90_THIN_CAPABILITY_METADATA_V1.zip`)), path: 'build/B90_THIN_CAPABILITY_METADATA_V1.zip'});
assert.deepEqual(packageReceipt.zip_checks, {
  crc_and_full_entry_readback: true,
  fixed_member_metadata: true,
  member_count: 39,
  payload_bytes: 6098824,
  sorted_member_order: true,
});

assert.equal(sourceLock.schema, 'b90-capability-source-lock/1');
assert.equal(sourceLock.course_id, 'B90');
assert.equal(sourceLock.repository, 'https://github.com/KokunoYumeto/introduction-to-probability-id');
assert.deepEqual(sourceLock.release, {
  commit: '5d1cfc55eecb678b0b4074160bc4f2d8bb2da5b6',
  tag: 'v2026.08.22.1',
  tree: '21df3b2c0fab6827a21854bdcc41667a93edf749',
});
assert.equal(sourceLock.inputs.length, 10);
assert.equal(publicReadback.state, 'pass');
assert.equal(publicReadback.anonymous, true);
assert.equal(publicReadback.credentials_used, false);
assert.equal(publicReadback.failures.length, 0);
assert.equal(publicReadback.record_backend.records, 4716);
assert.equal(publicReadback.github_release.assets.length, 3);
assert.equal(publicReadback.zenodo.assets.length, 3);
assert.equal(publicReadback.pages_files.length, 4);

assert.equal(capabilities.schema, 'b90-capabilities/1');
assert.equal(capabilities.contract, manifest.contract);
assert.equal(capabilities.native_role_id, 'R010');
assert.deepEqual(capabilities.counts, counts);
assert.deepEqual(capabilities.curriculum_graph.native_prerequisite_ids, ['urn:interlanguage:r010:course:b30']);
assert.deepEqual(capabilities.curriculum_graph.prerequisite_course_ids, ['B30']);
assert.equal(capabilities.learner_delivery.answers_or_solutions, false);
assert.equal(capabilities.learner_delivery.page_based_pdf_reader, true);
assert.equal(capabilities.educator_delivery.teacher_manual, false);
assert.equal(capabilities.federation.stable_native_ids_preserved, true);
assert.equal(capabilities.federation.body_content_embedded, false);

assert.equal(learningMap.schema, 'b90-learner-map/1');
assert.equal(learningMap.course_id, 'B90');
assert.equal(learningMap.locale, 'id-ID');
assert.equal(learningMap.chapters.length, 12);
assert.equal(learningMap.exercise_identity_count, 711);
assert.equal(learningMap.reader.kind, 'page_based_pdfjs');
assert.equal(learningMap.reader.pdf_pages, 554);
assert.equal(learningMap.reader.semantic_html, false);
assert.equal(learningMap.answers_or_solutions_available_in_public_backend, false);
assert.equal(learningMap.body_content_embedded, false);

assert.equal(educatorMap.schema, 'b90-educator-map/1');
assert.equal(educatorMap.course_id, 'B90');
assert.equal(educatorMap.locale, 'id-ID');
assert.equal(educatorMap.selectable_units.length, 800);
assert.equal(educatorMap.chapter_summaries.length, 12);
assert.equal(educatorMap.teacher_manual_claimed, false);
assert.equal(educatorMap.answer_key_claimed, false);
assert.equal(educatorMap.body_content_embedded, false);

assert.equal(publicEvidence.schema, 'b90-public-evidence/1');
assert.equal(publicEvidence.course_id, 'B90');
assert.equal(publicEvidence.repository.commit, sourceLock.release.commit);
assert.equal(publicEvidence.repository.tree, sourceLock.release.tree);
assert.equal(publicEvidence.reader.observed_kind, 'page_based_pdfjs');
assert.equal(publicEvidence.reader.pdf_pages, 554);
assert.equal(publicEvidence.reader.semantic_html_established, false);
assert.equal(publicEvidence.reader.mathml_established, false);
assert.equal(publicEvidence.reader.wcag_conformance_established, false);
assert.equal(publicEvidence.reader.epub_established, false);
assert.equal(publicEvidence.reader.offline_portability_established, false);
assert.equal(publicEvidence.zenodo.record_id, 22062144);
assert.equal(publicEvidence.zenodo.concept_id, 22048654);
assert.equal(publicEvidence.zenodo.access_right, 'open');
assert.ok(publicEvidence.zenodo.assets.every(row => row.github_release_byte_identity === true));

assert.equal(claimBoundary.schema, 'b90-claim-boundary/1');
assert.equal(claimBoundary.course_id, 'B90');
for (const key of [
  'native_bodies_copied', 'answers_or_solutions_claimed', 'teacher_manual_claimed',
  'semantic_html_claimed', 'mathml_claimed', 'wcag_conformance_claimed',
  'epub_claimed', 'offline_portability_claimed', 'reversible_exchange_claimed',
  'public_access_state_changed',
]) assert.equal(claimBoundary[key], false);
for (const key of ['source_segment_text_copied', 'target_segment_text_copied', 'excluded_supplement_records_exposed', 'learner_result_instances']) {
  assert.equal(claimBoundary[key], 0);
}
assert.equal(claimBoundary.explicit_exclusion.excluded_record_count, 1159);
assert.equal(claimBoundary.explicit_exclusion.excluded_record_type_counts.exercise_answer, 287);

const publicMappings = [
  [`${base}/views/B90.html`, 'docs/backend/b90/B90.html'],
  [`${base}/views/B90-pengajar.html`, 'docs/backend/b90/B90-pengajar.html'],
  [`${base}/views/capabilities.json`, 'docs/backend/b90/capabilities.json'],
  [`${base}/data/learner-map.json`, 'docs/backend/b90/learning-map.json'],
  [`${base}/data/educator-map.json`, 'docs/backend/b90/educator-map.json'],
  [`${base}/data/public-evidence.json`, 'docs/backend/b90/public-evidence.json'],
  [`${base}/data/claim-boundary.json`, 'docs/backend/b90/claim-boundary.json'],
  [`${base}/data/unit-index.jsonl`, 'docs/backend/b90/data/unit-index.jsonl'],
  [`${base}/data/concept-index.jsonl`, 'docs/backend/b90/data/concept-index.jsonl'],
  [`${base}/data/relation-index.jsonl`, 'docs/backend/b90/data/relation-index.jsonl'],
  [`${base}/data/terms-index.jsonl`, 'docs/backend/b90/data/terms-index.jsonl'],
  [`${base}/data/corrections-index.jsonl`, 'docs/backend/b90/data/corrections-index.jsonl'],
  [`${base}/data/rights-index.jsonl`, 'docs/backend/b90/data/rights-index.jsonl'],
  [`${base}/input/source-lock.json`, 'docs/backend/b90/source-lock.json'],
  [`${base}/input/public-native-readback.json`, 'docs/backend/b90/public-native-readback.json'],
  [`${base}/validation.json`, 'docs/backend/b90/validation.json'],
];
for (const [source, target] of publicMappings) {
  let bytes = await readFile(resolve(root, source));
  if (target === 'docs/backend/b90/B90-pengajar.html') {
    const original = bytes.toString('utf8');
    assert.equal((original.match(/\.\.\/data\//g) ?? []).length, 6);
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
  ['unit_identity_index', `${base}/data/unit-index.jsonl`],
  ['concept_index', `${base}/data/concept-index.jsonl`],
  ['relation_index', `${base}/data/relation-index.jsonl`],
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
  !overrides.semantic_adapters.B90
    || !overrides.semantic_adapters.B90.contract_version
    || overrides.semantic_adapters.B90.contract_version === manifest.contract,
  'Preserve a different admitted B90 contract',
);
overrides.semantic_adapters.B90 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_4716_public_native_records_800_units_711_exercises_91_concepts_119_terms_152_corrections_and_4_component_rights_with_explicit_answer_supplement_exclusion',
  evidence,
};
overrides.native_capabilities.B90 = {...(overrides.native_capabilities.B90 ?? {})};
for (const capability of [
  'unit_identity', 'terminology', 'translation_rights', 'corrections',
  'build', 'deterministic_replay', 'educator_unit_alignment', 'translation_ledger',
]) overrides.native_capabilities.B90[capability] = {status: 'verified', evidence};

const scope = 'Sebanyak 4.716 rekaman native publik, 800 unit, 12 bab, 33 bagian, 711 identitas latihan, 91 konsep, 119 istilah, 152 koreksi, dan empat rekaman hak komponen.';
const limitations = [
  'Adapter adalah proyeksi identitas, struktur, istilah, status, hak, dan bukti zero-copy; badan buku dan segmen tetap pada edisi native publik.',
  'Suplemen 1.159 rekaman, termasuk 287 jawaban, sengaja tidak berada dalam ekspor publik; jawaban atau solusi tidak diklaim.',
  'Dua belas rute bab menunjuk tepat ke halaman pembuka; rute bagian dan latihan hanya menunjuk konteks bab, bukan jangkar semantik per unit.',
  'Pembaca native berbasis PDF.js. HTML semantik, MathML, EPUB, paket luring portabel, dan kepatuhan WCAG tidak diklaim.',
  'Empat rekaman hak dan 152 status koreksi dipertahankan terpisah; koreksi terbuka tidak dinyatakan selesai.',
  'Pertukaran reversibel tidak diklaim dan replay memerlukan checkout native yang dipatok.',
];
const tool = {
  tool_id: 'b90.open_learner_hub',
  label: 'B90 · Probabilitas Berbasis Kalkulus',
  href: 'backend/b90/B90.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/b90/B90.html'),
  resource: await identity('docs/backend/b90/learning-map.json'),
  evidence: await identity('docs/backend/b90/validation.json'),
  limitations,
};
assert.ok(
  !overrides.learner_tools.B90
    || overrides.learner_tools.B90.every(old => old.tool_id === tool.tool_id),
  'Preserve unrelated B90 learner tools',
);
overrides.learner_tools.B90 = [tool];

const oldEducator = overrides.educator_evidence.B90;
const teacher = await identity('docs/backend/b90/B90-pengajar.html');
const educatorMapIdentity = await identity('docs/backend/b90/educator-map.json');
const unitIdentity = await identity('docs/backend/b90/data/unit-index.jsonl');
const conceptIdentity = await identity('docs/backend/b90/data/concept-index.jsonl');
const relationIdentity = await identity('docs/backend/b90/data/relation-index.jsonl');
const termIdentity = await identity('docs/backend/b90/data/terms-index.jsonl');
const rightsIdentity = await identity('docs/backend/b90/data/rights-index.jsonl');
const correctionsIdentity = await identity('docs/backend/b90/data/corrections-index.jsonl');
const educatorUrl = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/b90/B90-pengajar.html';
const managedResourceIds = new Set([
  'B90:educator-hub-v1', 'B90:educator-map-v1', 'B90:unit-index-v1',
  'B90:concept-index-v1', 'B90:relation-index-v1', 'B90:terms-index-v1',
  'B90:rights-index-v1', 'B90:corrections-index-v1',
]);
const resources = (oldEducator?.resources ?? []).filter(resource => !managedResourceIds.has(resource.id));
resources.push({
  id: 'B90:educator-hub-v1',
  title: 'Pemilih bab, bagian, unit, dan latihan B90 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url: educatorUrl,
  scope,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
resources.push({
  id: 'B90:educator-map-v1',
  title: 'Peta pengajar atas 800 unit native B90',
  resource_type: 'educator-data',
  status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/b90/educator-map.json',
  scope: 'Peta zero-copy atas hierarki unit, rute bab, konsep, istilah, koreksi, hak, dan batas suplemen jawaban.',
  bytes: educatorMapIdentity.bytes,
  sha256: educatorMapIdentity.sha256,
});
for (const row of [
  ['B90:unit-index-v1', 'Indeks 800 unit B90', 'unit-index.jsonl', unitIdentity, 'identity-index'],
  ['B90:concept-index-v1', 'Indeks 91 konsep B90', 'concept-index.jsonl', conceptIdentity, 'educator-data'],
  ['B90:relation-index-v1', 'Indeks 1.694 relasi B90', 'relation-index.jsonl', relationIdentity, 'educator-data'],
  ['B90:terms-index-v1', 'Indeks 119 istilah B90', 'terms-index.jsonl', termIdentity, 'terminology-register'],
  ['B90:rights-index-v1', 'Indeks empat rekaman hak B90', 'rights-index.jsonl', rightsIdentity, 'rights-ledger'],
  ['B90:corrections-index-v1', 'Indeks 152 koreksi B90', 'corrections-index.jsonl', correctionsIdentity, 'correction-ledger'],
]) {
  const [id, title, filename, fact, resourceType] = row;
  resources.push({
    id,
    title,
    resource_type: resourceType,
    status: 'verified',
    url: `https://kokunoyumeto.github.io/program-matematika-indonesia/backend/b90/data/${filename}`,
    scope: 'Indeks metadata native dengan identitas dan hash stabil; badan buku dan segmen tidak disalin.',
    bytes: fact.bytes,
    sha256: fact.sha256,
  });
}
overrides.educator_evidence.B90 = {
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
const pageFile = path => {
  const matches = publicEvidence.pages_files.filter(row => row.path === path);
  assert.equal(matches.length, 1, `Missing or duplicate native Pages file: ${path}`);
  return matches[0];
};
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
const indexFile = pageFile('index.html');
const pdfFile = zenodoFile('PENGANTAR_PELUANG_GRINSTEAD_SNELL_ID.pdf');
const online = {
  status: 'verified',
  format: 'text/html',
  url: publicEvidence.repository.pages_url,
  bytes: indexFile.bytes,
  sha256: indexFile.sha256,
  entry_point: 'index.html',
  scope: 'whole_course_page_based_pdf_reader',
  evidence: publicReceipt,
};
const pdf = {
  status: 'verified',
  format: 'application/pdf',
  url: pdfFile.url,
  bytes: pdfFile.bytes,
  sha256: pdfFile.sha256,
  scope: 'whole_course',
  evidence: publicReceipt,
};
learner.courses.B90 = {
  ...(learner.courses.B90 ?? {}),
  primary: online,
  online_html: online,
  pdf,
  epub: {status: 'not_yet_produced'},
  portable_html: {status: 'not_yet_produced'},
  capabilities: {
    ...(learner.courses.B90?.capabilities ?? {}),
    semantic_html: {status: 'not_yet_produced'},
    mathml: {status: 'not_yet_produced'},
    print_profile: {status: 'verified', evidence: {...publicReceipt, pdf_pages: 554}},
    chapter_downloads: {status: 'not_yet_produced'},
  },
};
await writeFile(resolve(root, learnerTarget), `${JSON.stringify(learner, null, 2)}\n`);

console.log(JSON.stringify({
  state: 'pass',
  admitted_roles: ['B90'],
  contract: manifest.contract,
  native_locale: manifest.locale,
  public_files_staged: publicMappings.length,
  native_records: counts.native_records,
  units: counts.units,
  exercises: counts.exercises,
  excluded_answer_records: counts.excluded_answer_records,
  public_state_changed: false,
}));
