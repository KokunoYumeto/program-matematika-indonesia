import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { liveCoursePublications } from '../docs/live-course-publications.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/b95-capability-v1';
const publicBase = 'docs/backend/b95';
const publicOrigin = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/b95';
const verifiedDate = '2026-09-07';

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const load = async (path) => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const identity = async (path) => {
  const bytes = await readFile(resolve(root, path));
  return { path, bytes: bytes.length, sha256: sha256(bytes) };
};
const bufferIdentity = (path, bytes) => ({ path, bytes: bytes.length, sha256: sha256(bytes) });
const clone = (value) => structuredClone(value);
const jsonBytes = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');

const expectedCounts = {
  chapters: 9,
  component_rights: 80,
  concepts: 826,
  corrections: 302,
  evidence_records: 2049,
  exercise_units: 322,
  exercises: 448,
  guided_exercises: 126,
  localizations: 2231,
  native_record_types: {
    artifact: 1565,
    asset: 947,
    concept: 826,
    correction: 302,
    course: 1,
    edition: 2,
    localization: 2231,
    program: 1,
    qa_event: 484,
    relation: 11127,
    resource: 1,
    rights: 80,
    segment: 2231,
    term: 859,
    unit: 1089,
  },
  native_records: 21746,
  o001_gap_ids: 105,
  public_answer_ids: 153,
  reader_pages: 462,
  relations: 11127,
  sections: 35,
  segments: 2231,
  source_files: 1245,
  subsections: 83,
  terms: 859,
  unit_kinds: {
    answer: 1,
    answer_layout: 2,
    answer_section: 2,
    book: 1,
    chapter: 9,
    chapter_front: 1,
    chapter_intro: 4,
    chapter_review: 1,
    companion_gap: 105,
    copyright_page: 1,
    data_appendix: 1,
    data_appendix_entry: 4,
    exercise: 322,
    guided_exercise: 126,
    guided_solution: 15,
    inline_public_answer: 28,
    mastery_companion_gap: 54,
    preface: 1,
    public_answer: 54,
    section: 35,
    section_intro: 7,
    section_review: 2,
    semantic_subunit: 40,
    solution: 138,
    source_wrapper: 2,
    subsection: 83,
    table: 2,
    title_page: 1,
    translation_bundle: 1,
    translation_range: 15,
    worked_example: 31,
  },
  units: 1089,
};

const paths = {
  manifest: `${base}/manifest.json`,
  validation: `${base}/validation.json`,
  packetReceipt: `${base}/build/PACKET_BUILD_RECEIPT.json`,
  packet: `${base}/build/B95_THIN_CAPABILITY_METADATA_V1.zip`,
  sourceLock: `${base}/input/source-lock.json`,
  publicReadback: `${base}/input/public-native-readback.json`,
  capabilities: `${base}/data/capabilities.json`,
  learnerMap: `${base}/data/learner-map.json`,
  educatorMap: `${base}/data/educator-map.json`,
  publicEvidence: `${base}/data/public-evidence.json`,
  claimBoundary: `${base}/data/claim-boundary.json`,
};

const [
  manifest,
  validation,
  packetReceipt,
  sourceLock,
  publicReadback,
  capabilities,
  learnerMap,
  educatorMap,
  publicEvidence,
  claimBoundary,
] = await Promise.all([
  load(paths.manifest),
  load(paths.validation),
  load(paths.packetReceipt),
  load(paths.sourceLock),
  load(paths.publicReadback),
  load(paths.capabilities),
  load(paths.learnerMap),
  load(paths.educatorMap),
  load(paths.publicEvidence),
  load(paths.claimBoundary),
]);

// Refuse to admit a regenerated or substituted packet without an explicit update
// to this admission contract.
assert.deepEqual(await identity(paths.manifest), {
  path: paths.manifest,
  bytes: 15919,
  sha256: '9e8b98e938a2e5b8015a2b4ede1e260a9ae5a8097cbe95c7d95d373a90d8db42',
});
assert.deepEqual(await identity(paths.validation), {
  path: paths.validation,
  bytes: 11857,
  sha256: 'c5a7802d03870943b7590a94825c24402aadc99324fa4a83e327aff2e5f211f8',
});
assert.deepEqual(await identity(paths.packetReceipt), {
  path: paths.packetReceipt,
  bytes: 1285,
  sha256: 'fbbdd57084e3903f17648d275bde327765fc2979711b5dee3b5e6cf922bba4bb',
});
assert.deepEqual(await identity(paths.packet), {
  path: paths.packet,
  bytes: 7767446,
  sha256: '420633fe6becff8874033c3c1f79fe014014ab078782fb40d8247aaed0b37f08',
});

assert.equal(manifest.schema, 'b95-capability-manifest/1');
assert.equal(manifest.course_id, 'B95');
assert.equal(manifest.native_role_id, 'R011');
assert.equal(manifest.native_course_id, 'be02bb59-5807-512c-8ba1-f5d22a702812');
assert.equal(manifest.native_edition_id, 'fd249e50-2371-5c79-88c6-70abc1222771');
assert.equal(manifest.native_family, 'openintro_statistics_fourth_edition');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.boundary_id, 'R011-B039');
assert.equal(manifest.content_policy, 'identity_structure_terminology_rights_evidence_only');
assert.equal(manifest.negative_fixture_count, 12);
assert.equal(manifest.validation_path, 'validation.json');
assert.equal(manifest.package_receipt_path, 'build/PACKET_BUILD_RECEIPT.json');
assert.deepEqual(manifest.counts, expectedCounts);
assert.deepEqual(manifest.projection, {
  central_course_truth_rewritten: false,
  component_rights_preserved: true,
  excluded_boundary_preserved: true,
  external_native_backend_required_for_replay: true,
  native_bodies_copied: false,
  native_ids_preserved: true,
  public_access_state_changed: false,
  reversible_exchange_claimed: false,
});
assert.deepEqual(manifest.authority, {
  current_export_binding: 'B039 release backend inventory plus expanded local manifest and publication receipts',
  public_release_id: 'R011-B039-v2026.09.01.2',
  public_release_tag: 'r011-b039-2026.09.01.2',
  public_release_tag_target_sha: '88ac7599a979c0f52b77b07fa3cb4f0db101f3b2',
  public_repository: 'https://github.com/KokunoYumeto/statistika-berbasis-data-id',
  tag_contains_current_working_tree_exports: false,
  upstream_commit: 'fee25091fb24e89c36296fd67c48c1fcf7a93b6e',
  upstream_repository: 'https://github.com/OpenIntroStat/openintro-statistics',
  upstream_tree: 'd61cc601e7d97759ce805900520f784d02a0489e',
});
assert.equal(manifest.outputs.length, 35);
assert.equal(new Set(manifest.outputs.map(({ path }) => path)).size, 35);
assert.deepEqual(manifest.output_paths, manifest.outputs.map(({ path }) => path));
for (const output of manifest.outputs) {
  assert.deepEqual(await identity(`${base}/${output.path}`), {
    path: `${base}/${output.path}`,
    bytes: output.bytes,
    sha256: output.sha256,
  }, `B95 adapter output drift: ${output.path}`);
}

assert.equal(validation.schema, 'b95-capability-validation/1');
assert.equal(validation.course_id, 'B95');
assert.equal(validation.boundary_id, 'R011-B039');
assert.equal(validation.result, 'pass');
assert.deepEqual(validation.counts, expectedCounts);
assert.equal(validation.negative_fixtures.length, 12);
assert.ok(validation.negative_fixtures.every(({ result }) => result === 'rejected'));
assert.deepEqual(validation.negative_fixtures.map(({ fixture_id }) => fixture_id), [
  'altered-native-id',
  'bad-chapter-route',
  'copied-body',
  'copied-segment-text',
  'dropped-native-id',
  'false-reversibility',
  'false-semantic-html',
  'false-solutions',
  'false-wcag',
  'flattened-rights',
  'hash-drift',
  'public-access-drift',
]);
for (const key of [
  'canonical_export_hashes_bound',
  'canonical_machine_files',
  'component_rights_preserved',
  'fresh_projection_matches_native',
  'native_bodies_absent',
  'public_completion_receipt_preserved_byte_for_byte',
  'public_github_zenodo_readback_preserved',
]) assert.equal(validation.checks[key], true, `B95 validation check failed: ${key}`);
assert.equal(validation.checks.negative_fixtures_rejected, 12);
assert.equal(validation.checks.public_reader_pages, 462);
assert.equal(validation.checks.two_run_build_identity.file_count, 36);
assert.equal(validation.checks.two_run_build_identity.tree_sha256, 'dd580a0af4fb9b2262489ec46e4692069b7949b3dbdd19c8206254f1c0c156ae');

assert.equal(packetReceipt.schema, 'b95-capability-thin-packet-build-receipt/1');
assert.equal(packetReceipt.course_id, 'B95');
assert.equal(packetReceipt.result, 'PASS');
assert.deepEqual(packetReceipt.adapter_manifest, {
  path: 'manifest.json',
  bytes: 15919,
  sha256: '9e8b98e938a2e5b8015a2b4ede1e260a9ae5a8097cbe95c7d95d373a90d8db42',
});
assert.deepEqual(packetReceipt.adapter_validation, {
  path: 'validation.json',
  bytes: 11857,
  sha256: 'c5a7802d03870943b7590a94825c24402aadc99324fa4a83e327aff2e5f211f8',
});
assert.deepEqual(packetReceipt.archive, {
  path: 'build/B95_THIN_CAPABILITY_METADATA_V1.zip',
  bytes: 7767446,
  sha256: '420633fe6becff8874033c3c1f79fe014014ab078782fb40d8247aaed0b37f08',
});
assert.equal(packetReceipt.content_policy, 'adapter_metadata_only_external_native_replay_dependency');
for (const key of [
  'external_hash_pinned_native_checkout_required_for_replay',
  'two_build_byte_identity',
]) assert.equal(packetReceipt[key], true, `B95 packet invariant failed: ${key}`);
for (const key of [
  'exercise_or_solution_bodies_included',
  'forbidden_payloads_included',
  'local_profile_data_included',
  'native_content_bodies_included',
  'public_state_changed',
  'reversible_exchange_claimed',
]) assert.equal(packetReceipt[key], false, `B95 packet exclusion failed: ${key}`);
assert.equal(packetReceipt.native_inputs_included, 0);
assert.equal(packetReceipt.negative_fixtures_included, 12);
assert.deepEqual(packetReceipt.zip_checks, {
  crc_and_full_entry_readback: true,
  fixed_member_metadata: true,
  member_count: 44,
  payload_bytes: 49359747,
  sorted_member_order: true,
});

assert.equal(sourceLock.schema, 'b95-capability-source-lock/1');
assert.equal(sourceLock.course_id, 'B95');
assert.equal(sourceLock.native_role_id, 'R011');
assert.equal(sourceLock.native_course_id, manifest.native_course_id);
assert.equal(sourceLock.native_edition_id, manifest.native_edition_id);
assert.equal(sourceLock.boundary_id, 'R011-B039');
assert.deepEqual(sourceLock.inputs, manifest.inputs);
assert.deepEqual(sourceLock.release, {
  release_id: 'R011-B039-v2026.09.01.2',
  tag: 'r011-b039-2026.09.01.2',
  upstream_commit: 'fee25091fb24e89c36296fd67c48c1fcf7a93b6e',
  upstream_repository: 'https://github.com/OpenIntroStat/openintro-statistics',
  upstream_tree: 'd61cc601e7d97759ce805900520f784d02a0489e',
});
assert.deepEqual(sourceLock.public_evidence_summary, {
  anonymous_readback: true,
  credentials_used: false,
  github_public: true,
  zenodo_public: true,
});

assert.equal(publicReadback.$schema, 'interlanguage.r011-b039-final-completion/v1');
assert.equal(publicReadback.boundary_id, 'R011-B039');
assert.equal(publicReadback.status, 'COMPLETE_TRANSLATED_ADMITTED_PUBLISHED_AND_PUBLICLY_READ_BACK');
assert.equal(publicReadback.complete_corpus, true);
assert.equal(publicReadback.translation.source_files, 1245);
assert.equal(publicReadback.reader.pages, 462);
assert.equal(publicReadback.reader.bytes, 57049904);
assert.equal(publicReadback.reader.sha256, '7ef1ed4390cd846cc636345d34a1ba3765f8afc32eb9446fd60c7862b7fde049');
assert.equal(publicReadback.reader.untranslated_instructional_or_exercise_prose_pages, 0);
assert.equal(publicReadback.backend.record_count, 21746);
assert.equal(publicReadback.release.asset_count, 9);
assert.equal(publicReadback.publication.github.public, true);
assert.equal(publicReadback.publication.github.all_nine_assets_read_back_by_bytes_and_sha256, true);
assert.equal(publicReadback.publication.zenodo.public, true);
assert.equal(publicReadback.publication.zenodo.all_nine_files_read_back_by_bytes_and_sha256, true);
assert.equal(publicReadback.credentials_recorded, false);

assert.equal(publicEvidence.schema, 'b95-public-evidence/1');
assert.equal(publicEvidence.course_id, 'B95');
assert.equal(publicEvidence.boundary_id, 'R011-B039');
assert.equal(publicEvidence.anonymous_readback, true);
assert.equal(publicEvidence.credentials_used, false);
assert.equal(publicEvidence.repository.public, true);
assert.equal(publicEvidence.repository.tag, 'r011-b039-2026.09.01.2');
assert.equal(publicEvidence.repository.tag_target_sha, '88ac7599a979c0f52b77b07fa3cb4f0db101f3b2');
assert.equal(publicEvidence.release.release_id, 'R011-B039-v2026.09.01.2');
assert.equal(publicEvidence.release.public, true);
assert.equal(publicEvidence.release.asset_count, 9);
assert.equal(publicEvidence.zenodo.public, true);
assert.equal(publicEvidence.zenodo.access_right, 'open');
assert.equal(publicEvidence.zenodo.doi, '10.5281/zenodo.22261912');
assert.equal(publicEvidence.zenodo.concept_doi, '10.5281/zenodo.22059801');
assert.equal(publicEvidence.reader.pdf_pages, 462);
assert.equal(publicEvidence.reader.pdf_sha256, publicReadback.reader.sha256);
assert.equal(publicEvidence.backend.record_count, 21746);
assert.equal(publicEvidence.backend.manifest_sha256, 'f4cdb5af77e1377572d7aa334ae937431cb20569ca0f7217c1ab400d9291176a');
assert.equal(publicEvidence.reader.semantic_html_established, false);
assert.equal(publicEvidence.reader.mathml_established, false);
assert.equal(publicEvidence.reader.epub_established, false);
assert.equal(publicEvidence.reader.offline_portability_established, false);

assert.equal(capabilities.schema, 'b95-capabilities/1');
assert.equal(capabilities.course_id, 'B95');
assert.equal(capabilities.contract, 'course-learning-capability/1');
assert.deepEqual(capabilities.counts, expectedCounts);
assert.equal(capabilities.federation.body_content_embedded, false);
assert.equal(capabilities.federation.stable_native_ids_preserved, true);
assert.equal(capabilities.learner_delivery.semantic_html, false);
assert.equal(capabilities.learner_delivery.answers_or_solutions, false);
assert.equal(capabilities.educator_delivery.teacher_manual, false);

assert.equal(learnerMap.schema, 'b95-learner-map/1');
assert.equal(learnerMap.course_id, 'B95');
assert.equal(learnerMap.chapters.length, 9);
assert.equal(learnerMap.exercise_identity_count, 448);
assert.equal(learnerMap.public_answer_identity_count, 153);
assert.equal(learnerMap.o001_gap_identity_count, 105);
assert.equal(learnerMap.body_content_embedded, false);
assert.equal(learnerMap.answers_or_solutions_available_as_bodies, false);
assert.equal(learnerMap.reader.pages, 462);
assert.equal(learnerMap.reader.semantic_html, false);

assert.equal(educatorMap.schema, 'b95-educator-map/1');
assert.equal(educatorMap.course_id, 'B95');
assert.equal(educatorMap.chapter_summaries.length, 9);
assert.equal(educatorMap.selectable_units.length, 1089);
assert.equal(educatorMap.body_content_embedded, false);
assert.equal(educatorMap.teacher_manual_claimed, false);
assert.equal(educatorMap.answer_key_claimed, false);

assert.deepEqual(claimBoundary, {
  answer_or_solution_bodies_copied: 0,
  boundary_id: 'R011-B039',
  chapter_routes_are_exact_reader_toc_starts: true,
  course_id: 'B95',
  epub_claimed: false,
  explicit_exclusion: [
    'restricted instructor-only solutions',
    'components lacking established redistribution rights',
    'non-rendered upstream developer comments',
  ],
  mathml_claimed: false,
  native_bodies_copied: false,
  native_prerequisites_invented: false,
  nonchapter_routes_are_context_only: true,
  o001_gap_identity_rows: 105,
  offline_portability_claimed: false,
  projection_kind: 'metadata_only_zero_copy',
  public_access_state_changed: false,
  public_answer_identity_rows: 153,
  restricted_solution_records_exposed: 0,
  reversible_exchange_claimed: false,
  schema: 'b95-claim-boundary/1',
  semantic_html_claimed: false,
  source_segment_text_copied: 0,
  target_segment_text_copied: 0,
  wcag_conformance_claimed: false,
});

// The adapter may not be admitted against the stale B030 overlay. Course-state
// promotion remains a separate decision, but every public identity must be B039.
const liveB95 = liveCoursePublications.B95;
assert.ok(liveB95, 'B95 live-publication overlay is missing.');
assert.ok(['production', 'published'].includes(liveB95.state), 'B95 course state is invalid.');
assert.equal(liveB95.version, '2026.09.01.2-R011-B039');
assert.equal(liveB95.zenodo, 'https://doi.org/10.5281/zenodo.22261912');
assert.equal(liveB95.repository, publicEvidence.repository.url);
assert.equal(liveB95.release, publicEvidence.repository.release_url);
assert.equal(liveB95.edition, publicEvidence.reader.zenodo_url);
assert.equal(liveB95.progress.publicPages, 462);
assert.equal(liveB95.verification.readerBytes, 57049904);
assert.equal(liveB95.verification.readerSha256, publicEvidence.reader.pdf_sha256);
assert.equal(liveB95.verification.backendRecords, 21746);
assert.equal(liveB95.verification.publicAssets, 9);

const publicMappings = [
  [`${base}/manifest.json`, `${publicBase}/manifest.json`],
  [`${base}/views/B95.html`, `${publicBase}/B95.html`],
  [`${base}/views/B95-pengajar.html`, `${publicBase}/B95-pengajar.html`],
  [`${base}/views/capabilities.json`, `${publicBase}/capabilities.json`],
  [`${base}/data/learner-map.json`, `${publicBase}/learning-map.json`],
  [`${base}/data/educator-map.json`, `${publicBase}/educator-map.json`],
  [`${base}/data/public-evidence.json`, `${publicBase}/public-evidence.json`],
  [`${base}/data/claim-boundary.json`, `${publicBase}/claim-boundary.json`],
  [`${base}/data/native-record-index.jsonl`, `${publicBase}/data/native-record-index.jsonl`],
  [`${base}/data/unit-index.jsonl`, `${publicBase}/data/unit-index.jsonl`],
  [`${base}/data/exercise-index.jsonl`, `${publicBase}/data/exercise-index.jsonl`],
  [`${base}/data/concept-index.jsonl`, `${publicBase}/data/concept-index.jsonl`],
  [`${base}/data/relation-index.jsonl`, `${publicBase}/data/relation-index.jsonl`],
  [`${base}/data/terms-index.jsonl`, `${publicBase}/data/terms-index.jsonl`],
  [`${base}/data/corrections-index.jsonl`, `${publicBase}/data/corrections-index.jsonl`],
  [`${base}/data/rights-index.jsonl`, `${publicBase}/data/rights-index.jsonl`],
  [`${base}/data/segment-index.jsonl`, `${publicBase}/data/segment-index.jsonl`],
  [`${base}/data/localization-index.jsonl`, `${publicBase}/data/localization-index.jsonl`],
  [`${base}/data/evidence-index.jsonl`, `${publicBase}/data/evidence-index.jsonl`],
  [`${base}/data/release-inventory.json`, `${publicBase}/data/release-inventory.json`],
  [`${base}/input/source-lock.json`, `${publicBase}/source-lock.json`],
  [`${base}/input/public-native-readback.json`, `${publicBase}/public-native-readback.json`],
  [`${base}/validation.json`, `${publicBase}/validation.json`],
];

const staged = new Map();
for (const [source, target] of publicMappings) {
  let bytes = await readFile(resolve(root, source));
  const expectedRelativeLinks = new Map([
    [`${publicBase}/B95.html`, 1],
    [`${publicBase}/B95-pengajar.html`, 8],
    [`${publicBase}/educator-map.json`, 7],
  ]).get(target);
  if (expectedRelativeLinks !== undefined) {
    const original = bytes.toString('utf8');
    assert.equal((original.match(/\.\.\/data\//g) ?? []).length, expectedRelativeLinks, `${source}: adapter-relative data-link count drift.`);
    let projected = original.replaceAll('../data/', 'data/');
    if (target === `${publicBase}/B95-pengajar.html`) {
      assert.equal(
        (projected.match(/data\/claim-boundary\.json/g) ?? []).length,
        1,
        `${source}: claim-boundary link count drift.`,
      );
      projected = projected.replace('data/claim-boundary.json', 'claim-boundary.json');
    }
    assert.equal(projected.includes('../data/'), false, `${target}: adapter-relative data link survived projection.`);
    bytes = Buffer.from(projected, 'utf8');
  }
  staged.set(target, bytes);
}
assert.equal(staged.size, publicMappings.length);
const stagedIdentity = (path) => {
  const bytes = staged.get(path);
  assert.ok(bytes, `Missing staged B95 file: ${path}`);
  return bufferIdentity(path, bytes);
};
for (const target of [`${publicBase}/B95.html`, `${publicBase}/B95-pengajar.html`]) {
  const html = staged.get(target).toString('utf8');
  for (const [, relative] of html.matchAll(/href="(data\/[^"]+)"/g)) {
    assert.ok(staged.has(`${publicBase}/${relative}`), `${target}: missing staged link target ${relative}`);
  }
}

const evidence = [];
for (const [kind, path] of [
  ['central_adapter_manifest', paths.manifest],
  ['deterministic_validation_receipt', paths.validation],
  ['deterministic_package_receipt', paths.packetReceipt],
  ['deterministic_capability_packet', paths.packet],
  ['native_source_lock', paths.sourceLock],
  ['anonymous_native_public_readback', paths.publicReadback],
  ['verified_native_public_release', paths.publicEvidence],
  ['native_record_index', `${base}/data/native-record-index.jsonl`],
  ['unit_identity_index', `${base}/data/unit-index.jsonl`],
  ['exercise_identity_index', `${base}/data/exercise-index.jsonl`],
  ['concept_index', `${base}/data/concept-index.jsonl`],
  ['relation_index', `${base}/data/relation-index.jsonl`],
  ['terminology_index', `${base}/data/terms-index.jsonl`],
  ['correction_index', `${base}/data/corrections-index.jsonl`],
  ['component_rights_index', `${base}/data/rights-index.jsonl`],
  ['segment_index', `${base}/data/segment-index.jsonl`],
  ['localization_index', `${base}/data/localization-index.jsonl`],
  ['evidence_index', `${base}/data/evidence-index.jsonl`],
  ['release_inventory', `${base}/data/release-inventory.json`],
]) {
  const fact = await identity(path);
  evidence.push({ kind, locator: path, bytes: fact.bytes, sha256: fact.sha256, verified_date: verifiedDate });
}

const scope = 'Sebanyak 21.746 rekaman native, 1.089 unit, 9 bab, 35 bagian, 448 identitas latihan, 826 konsep, 859 istilah, 302 koreksi, 80 rekaman hak komponen, serta 2.231 segmen dan lokalisasi.';
const limitations = [
  'Adapter adalah proyeksi zero-copy atas identitas, struktur, istilah, status, hak, dan bukti; badan buku, segmen, latihan, jawaban, dan solusi tetap pada edisi native publik.',
  'Sebanyak 153 identitas jawaban publik dan 105 identitas celah O001 dipertahankan, tetapi badan jawaban atau solusi tidak disalin dan kunci jawaban tidak diklaim.',
  'Sembilan rute bab menunjuk halaman awal yang tepat dari daftar isi pembaca; rute selain bab hanya memberi konteks dan tidak dinyatakan sebagai jangkar semantik per unit.',
  'Pembaca native adalah PDF 462 halaman. HTML semantik, MathML, EPUB, paket HTML luring, PDF/UA, kepatuhan WCAG, dan manual pengajar tidak diklaim.',
  'Replay penuh membutuhkan checkout native eksternal yang dipatok; tag rilis publik tidak dinyatakan memuat ekspor working-tree B039.',
];

const integrationTarget = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(integrationTarget);
const stripManagedIntegration = (value) => {
  const result = clone(value);
  for (const key of ['semantic_adapters', 'native_capabilities', 'educator_evidence']) {
    if (result[key]) delete result[key].B95;
  }
  return result;
};
const unrelatedIntegration = stripManagedIntegration(overrides);
overrides.semantic_adapters ??= {};
overrides.native_capabilities ??= {};
overrides.educator_evidence ??= {};
assert.ok(
  !overrides.semantic_adapters.B95
    || !overrides.semantic_adapters.B95.contract_version
    || overrides.semantic_adapters.B95.contract_version === manifest.contract,
  'Preserve a different admitted B95 contract.',
);
overrides.semantic_adapters.B95 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_21746_native_records_1089_units_448_exercises_826_concepts_859_terms_302_corrections_80_component_rights_and_2231_segments_and_localizations_with_153_public_answer_and_105_o001_gap_identities',
  evidence,
};
overrides.native_capabilities.B95 = { ...(overrides.native_capabilities.B95 ?? {}) };
for (const capability of [
  'unit_identity',
  'terminology',
  'translation_rights',
  'corrections',
  'build',
  'deterministic_replay',
  'educator_unit_alignment',
  'translation_ledger',
]) overrides.native_capabilities.B95[capability] = { status: 'verified', evidence };

const teacher = stagedIdentity(`${publicBase}/B95-pengajar.html`);
const managedEducatorIds = new Set([
  'B95:educator-hub-v1',
  'B95:educator-map-v1',
  'B95:native-record-index-v1',
  'B95:unit-index-v1',
  'B95:exercise-index-v1',
  'B95:concept-index-v1',
  'B95:relation-index-v1',
  'B95:terms-index-v1',
  'B95:corrections-index-v1',
  'B95:rights-index-v1',
  'B95:segment-index-v1',
  'B95:localization-index-v1',
  'B95:evidence-index-v1',
  'B95:release-inventory-v1',
]);
const oldEducator = overrides.educator_evidence.B95;
const supersededManagedFeatures = new Set([
  'terminology_register',
  'correction_ledger',
  'rights_ledger',
  'translation_alignment',
]);
const educatorResources = (oldEducator?.resources ?? []).filter(({ id }) => !managedEducatorIds.has(id));
const educatorMapFact = stagedIdentity(`${publicBase}/educator-map.json`);
educatorResources.push({
  id: 'B95:educator-hub-v1',
  title: 'Pemilih bab, unit, latihan, istilah, dan bukti B95 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url: `${publicOrigin}/B95-pengajar.html`,
  scope,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
educatorResources.push({
  id: 'B95:educator-map-v1',
  title: 'Peta pengajar atas 1.089 unit native B95',
  resource_type: 'educator-data',
  status: 'verified',
  url: `${publicOrigin}/educator-map.json`,
  scope: 'Peta zero-copy atas sembilan bab, unit yang dapat dipilih, rute PDF, latihan, istilah, koreksi, hak, segmen, dan lokalisasi.',
  bytes: educatorMapFact.bytes,
  sha256: educatorMapFact.sha256,
});
for (const [id, title, filename, resourceType] of [
  ['B95:native-record-index-v1', 'Indeks 21.746 rekaman native B95', 'native-record-index.jsonl', 'identity-index'],
  ['B95:unit-index-v1', 'Indeks 1.089 unit B95', 'unit-index.jsonl', 'identity-index'],
  ['B95:exercise-index-v1', 'Indeks 448 latihan B95', 'exercise-index.jsonl', 'exercise-bank'],
  ['B95:concept-index-v1', 'Indeks 826 konsep B95', 'concept-index.jsonl', 'educator-data'],
  ['B95:relation-index-v1', 'Indeks 11.127 relasi B95', 'relation-index.jsonl', 'educator-data'],
  ['B95:terms-index-v1', 'Indeks status 859 istilah B95', 'terms-index.jsonl', 'terminology-register'],
  ['B95:corrections-index-v1', 'Indeks status 302 koreksi B95', 'corrections-index.jsonl', 'correction-ledger'],
  ['B95:rights-index-v1', 'Indeks 80 rekaman hak komponen B95', 'rights-index.jsonl', 'rights-ledger'],
  ['B95:segment-index-v1', 'Indeks 2.231 segmen B95', 'segment-index.jsonl', 'translation-ledger'],
  ['B95:localization-index-v1', 'Indeks 2.231 lokalisasi B95', 'localization-index.jsonl', 'translation-ledger'],
  ['B95:evidence-index-v1', 'Indeks 2.049 rekaman bukti B95', 'evidence-index.jsonl', 'evidence-ledger'],
  ['B95:release-inventory-v1', 'Inventaris rilis B039 B95', 'release-inventory.json', 'release-evidence'],
]) {
  const fact = stagedIdentity(`${publicBase}/data/${filename}`);
  educatorResources.push({
    id,
    title,
    resource_type: resourceType,
    status: 'verified',
    url: `${publicOrigin}/data/${filename}`,
    scope: 'Indeks metadata native dengan identitas dan hash stabil; badan buku, segmen, latihan, jawaban, dan solusi tidak disalin.',
    bytes: fact.bytes,
    sha256: fact.sha256,
  });
}
assert.equal(new Set(educatorResources.map(({ id }) => id)).size, educatorResources.length, 'Duplicate B95 educator resource ID.');
overrides.educator_evidence.B95 = {
  ...(oldEducator ?? {}),
  status: 'verified',
  verified_date: verifiedDate,
  locator: `${publicOrigin}/B95-pengajar.html`,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: [...new Set([
    ...(oldEducator?.features ?? []).filter((feature) => !supersededManagedFeatures.has(feature)),
    'lesson_sequences',
    'exercise_bank',
    'remix_selectors',
  ])].sort(),
  resources: educatorResources,
};
assert.deepEqual(stripManagedIntegration(overrides), unrelatedIntegration, 'Admission changed an unrelated integration override.');
assert.deepEqual(overrides.native_capabilities.D30, unrelatedIntegration.native_capabilities?.D30, 'D30 native capabilities changed.');
assert.deepEqual(overrides.semantic_adapters.D30, unrelatedIntegration.semantic_adapters?.D30, 'D30 semantic adapter changed.');
assert.deepEqual(overrides.educator_evidence.D30, unrelatedIntegration.educator_evidence?.D30, 'D30 educator evidence changed.');

const publicReceipt = {
  kind: 'anonymous_public_release_asset_readback',
  locator: publicEvidence.zenodo.url,
  verified_date: verifiedDate,
};
const pdf = {
  status: 'verified',
  format: 'application/pdf',
  url: publicEvidence.reader.zenodo_url,
  bytes: publicReadback.reader.bytes,
  sha256: publicReadback.reader.sha256,
  scope: 'whole_course_462_pages_with_exact_chapter_start_routes_and_context_only_nonchapter_routes',
  evidence: publicReceipt,
};
const learnerDeliveryTarget = 'backend/authority/learner-delivery-overrides-v1.json';
const learnerDelivery = await load(learnerDeliveryTarget);
assert.equal(learnerDelivery.schema_version, '1.0.0');
assert.ok(learnerDelivery.courses && !Array.isArray(learnerDelivery.courses));
const unrelatedLearnerDelivery = clone(learnerDelivery);
delete unrelatedLearnerDelivery.courses.B95;
learnerDelivery.courses.B95 = {
  ...(learnerDelivery.courses.B95 ?? {}),
  primary: clone(pdf),
  online_html: { status: 'not_yet_produced' },
  pdf: clone(pdf),
  epub: { status: 'not_yet_produced' },
  portable_html: { status: 'not_yet_produced' },
  capabilities: {
    ...(learnerDelivery.courses.B95?.capabilities ?? {}),
    semantic_html: { status: 'not_yet_produced' },
    mathml: { status: 'not_yet_produced' },
    print_profile: { status: 'verified', evidence: { ...publicReceipt, pdf_pages: 462 } },
    chapter_downloads: { status: 'not_yet_produced' },
  },
};
const learnerDeliveryAfter = clone(learnerDelivery);
delete learnerDeliveryAfter.courses.B95;
assert.deepEqual(learnerDeliveryAfter, unrelatedLearnerDelivery, 'Admission changed an unrelated learner-delivery override.');
assert.deepEqual(learnerDelivery.courses.D30, unrelatedLearnerDelivery.courses.D30, 'D30 learner delivery changed.');

const toolId = 'b95.open_learner_hub';
const learnerToolInput = {
  tool_id: toolId,
  label: 'B95 · Statistika Terapan dan Analisis Data',
  href: 'backend/b95/B95.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page_path: `${publicBase}/B95.html`,
  resource_path: `${publicBase}/learning-map.json`,
  evidence_path: `${publicBase}/validation.json`,
  limitations,
};
const learnerToolsTarget = 'backend/authority/learner-tools-overrides-v1.json';
const learnerTools = await load(learnerToolsTarget);
assert.ok(Array.isArray(learnerTools.courses), 'Learner-tool override courses must be an array.');
const unrelatedLearnerTools = clone(learnerTools);
unrelatedLearnerTools.courses = unrelatedLearnerTools.courses.filter(({ course_id }) => course_id !== 'B95');
const b95Rows = learnerTools.courses.filter(({ course_id }) => course_id === 'B95');
assert.ok(b95Rows.length <= 1, 'Duplicate B95 rows already exist in learner-tool overrides.');
const oldTools = b95Rows[0]?.tools ?? [];
assert.ok(Array.isArray(oldTools), 'B95 learner tools must be an array.');
const mergedTools = [...oldTools.filter(({ tool_id }) => tool_id !== toolId), learnerToolInput]
  .sort((left, right) => left.tool_id.localeCompare(right.tool_id));
const b95ToolRow = { course_id: 'B95', tools: mergedTools };
const existingIndex = learnerTools.courses.findIndex(({ course_id }) => course_id === 'B95');
if (existingIndex >= 0) learnerTools.courses[existingIndex] = b95ToolRow;
else learnerTools.courses.push(b95ToolRow);
const learnerToolsAfter = clone(learnerTools);
learnerToolsAfter.courses = learnerToolsAfter.courses.filter(({ course_id }) => course_id !== 'B95');
assert.deepEqual(learnerToolsAfter, unrelatedLearnerTools, 'Admission changed an unrelated learner-tool override.');
assert.equal(new Set(learnerTools.courses.map(({ course_id }) => course_id)).size, learnerTools.courses.length, 'Duplicate learner-tool course ID.');
assert.equal(new Set(learnerTools.courses.flatMap(({ tools }) => tools.map(({ tool_id }) => tool_id))).size,
  learnerTools.courses.flatMap(({ tools }) => tools).length, 'Duplicate learner-tool ID.');

// The dedicated learner-tool array is the source for learner-tools-v1. Do not
// duplicate this managed tool in integration-overrides, whose merge would make
// the normal course-capsule builder reject the global tool ID.
assert.ok(
  !(overrides.learner_tools?.B95 ?? []).some(({ tool_id }) => tool_id === toolId),
  'Remove the duplicate managed B95 tool from integration-overrides before admission.',
);

const authorityWrites = new Map([
  [integrationTarget, jsonBytes(overrides)],
  [learnerDeliveryTarget, jsonBytes(learnerDelivery)],
  [learnerToolsTarget, jsonBytes(learnerTools)],
]);
const mutationTargets = [...staged.keys(), ...authorityWrites.keys()];
assert.equal(new Set(mutationTargets).size, mutationTargets.length, 'Duplicate B95 admission target.');
for (const target of mutationTargets) {
  assert.ok(!target.split('/').includes('..'), `Unsafe admission target: ${target}`);
  assert.doesNotMatch(target, /(?:^|\/)d30(?:\/|$)/i, `D30 target is forbidden: ${target}`);
  assert.ok(
    target.startsWith(`${publicBase}/`)
      || target === integrationTarget
      || target === learnerDeliveryTarget
      || target === learnerToolsTarget,
    `Out-of-scope B95 admission target: ${target}`,
  );
}

for (const [target, bytes] of staged) {
  await mkdir(dirname(resolve(root, target)), { recursive: true });
  await writeFile(resolve(root, target), bytes);
  assert.deepEqual(await identity(target), bufferIdentity(target, bytes), `${target}: staged identity drift.`);
}
for (const [target, bytes] of authorityWrites) {
  await writeFile(resolve(root, target), bytes);
  assert.deepEqual(await identity(target), bufferIdentity(target, bytes), `${target}: authority identity drift.`);
}

console.log(JSON.stringify({
  state: 'PASS',
  admitted_roles: ['B95'],
  contract: manifest.contract,
  boundary_id: manifest.boundary_id,
  native_locale: manifest.locale,
  public_files_staged: staged.size,
  learner_tool_authority: 'backend/authority/learner-tools-overrides-v1.json',
  native_records: expectedCounts.native_records,
  units: expectedCounts.units,
  exercises: expectedCounts.exercises,
  reader_pages: expectedCounts.reader_pages,
  public_state_changed: false,
  producer_root_modified: false,
  d30_modified: false,
}, null, 2));
