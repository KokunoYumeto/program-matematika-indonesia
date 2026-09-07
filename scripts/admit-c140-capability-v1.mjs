import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { liveCoursePublications } from '../docs/live-course-publications.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/c140-capability-v1';
const publicBase = 'docs/backend/c140';
const publicOrigin = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c140';
const nativeOrigin = 'https://kokunoyumeto.github.io/penn-state-stat-415-id/';
const verifiedDate = '2026-09-07';
const zenodoPrimaryPdfUrl = 'https://zenodo.org/records/22208527/files/00_00_stat415-pengantar-statistika-matematis-id.pdf?download=1';

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
  companion_assessment_documents: 4,
  companion_capstone_documents: 2,
  companion_documents: 39,
  companion_entities: 1523,
  companion_mastery_documents: 13,
  companion_relations: 1949,
  companion_rubrics: 62,
  companion_simulation_documents: 6,
  companion_solved_problems: 146,
  companion_theory_documents: 13,
  component_rights: 9,
  correction_and_adverse_rows: 261,
  penn_corrections: 242,
  penn_documents: 14,
  penn_math_surfaces: 3156,
  penn_segments: 4932,
  penn_terms: 192,
  penn_units: 6510,
  public_documents: 54,
  random_adverse_records: 19,
  random_documents: 1,
  random_entities: 325,
  random_relations: 474,
  random_terms: 42,
  stable_entity_ids: 8358,
  structural_relations: 2423,
  terminology_rows: 234,
};

const paths = {
  manifest: `${base}/manifest.json`,
  validation: `${base}/validation.json`,
  packetReceipt: `${base}/build/PACKET_BUILD_RECEIPT.json`,
  packet: `${base}/build/C140_COMPLETE_THIN_CAPABILITY_METADATA_V1.zip`,
  sourceLock: `${base}/input/source-lock.json`,
  githubRelease: `${base}/input/github-release-readback.json`,
  githubPages: `${base}/input/github-pages-readback.json`,
  zenodo: `${base}/input/zenodo-readback.json`,
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
  githubRelease,
  githubPages,
  zenodoReadback,
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
  load(paths.githubRelease),
  load(paths.githubPages),
  load(paths.zenodo),
  load(paths.capabilities),
  load(paths.learnerMap),
  load(paths.educatorMap),
  load(paths.publicEvidence),
  load(paths.claimBoundary),
]);

assert.deepEqual({
  state: liveCoursePublications.C140?.state,
  reader: liveCoursePublications.C140?.reader,
  edition: liveCoursePublications.C140?.edition,
  zenodo: liveCoursePublications.C140?.zenodo,
  repository: liveCoursePublications.C140?.repository,
  release: liveCoursePublications.C140?.release,
  version: liveCoursePublications.C140?.version,
  publicUnits: liveCoursePublications.C140?.progress?.publicUnits,
}, {
  state: 'published',
  reader: nativeOrigin,
  edition: zenodoPrimaryPdfUrl,
  zenodo: 'https://doi.org/10.5281/zenodo.22208527',
  repository: 'https://github.com/KokunoYumeto/penn-state-stat-415-id',
  release: 'https://github.com/KokunoYumeto/penn-state-stat-415-id/releases/tag/v2026.08.31.c140-companion-c5',
  version: '2026.08.31.c140-companion-c5',
  publicUnits: 54,
}, 'The learner-facing C140 publication overlay is not the complete verified C5 boundary.');

// Admission is fail-closed against any regenerated or substituted packet.
assert.deepEqual(await identity(paths.manifest), {
  path: paths.manifest,
  bytes: 28428,
  sha256: '6573e4aa1e0a2909ced29229929aff00d6d9a5feb37ca1bde2a0989295fae37b',
});
assert.deepEqual(await identity(paths.validation), {
  path: paths.validation,
  bytes: 10355,
  sha256: '531d1d33c05846d032ef17e59be87a9c2e542f152181ce3b12a10f477bf7edae',
});
assert.deepEqual(await identity(paths.packetReceipt), {
  path: paths.packetReceipt,
  bytes: 1263,
  sha256: '560b8976595f038dbc71c12c6b89d8a99006d3135888dc4d5dba32471f2cc6d1',
});
assert.deepEqual(await identity(paths.packet), {
  path: paths.packet,
  bytes: 1017886,
  sha256: '6c7745f1b999d72a517ec000259f1b230a922b56cf002a27f6506dea85baa296',
});

assert.equal(manifest.schema, 'c140-capability-manifest/1');
assert.equal(manifest.course_id, 'C140');
assert.equal(manifest.native_role_id, 'O006');
assert.equal(manifest.native_family, 'penn_stat415_random_completeness_original_companion');
assert.equal(manifest.locale, 'id-ID');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.boundary_id, 'C140-C5-54');
assert.equal(manifest.content_policy, 'identity_structure_terminology_corrections_rights_and_public_routes_only');
assert.equal(manifest.negative_fixture_count, 12);
assert.equal(manifest.validation_path, 'validation.json');
assert.equal(manifest.package_receipt_path, 'build/PACKET_BUILD_RECEIPT.json');
assert.deepEqual(manifest.counts, expectedCounts);
assert.deepEqual(manifest.authority, {
  content_commit: '40acd8e846a4603ac5a90d311794b7e9c9db7bb9',
  pages_commit: '903d54c0971d3c14ec8f6fa0961136b881a73b82',
  release_id: 379767406,
  release_tag: 'v2026.08.31.c140-companion-c5',
  repository: 'https://github.com/KokunoYumeto/penn-state-stat-415-id',
  zenodo_concept_id: 22077422,
  zenodo_doi: '10.5281/zenodo.22208527',
  zenodo_record_id: 22208527,
});
assert.deepEqual(manifest.projection, {
  component_rights_preserved: true,
  external_native_backend_required_for_replay: true,
  native_bodies_copied: false,
  native_ids_preserved: true,
  public_access_state_changed: false,
  reversible_content_exchange_claimed: false,
  whole_course_component_boundary_proven: true,
});
assert.equal(manifest.inputs.length, 99);
assert.equal(manifest.outputs.length, 37);
assert.equal(new Set(manifest.outputs.map(({ path }) => path)).size, 37);
assert.deepEqual(manifest.output_paths, manifest.outputs.map(({ path }) => path));
for (const output of manifest.outputs) {
  assert.deepEqual(await identity(`${base}/${output.path}`), {
    path: `${base}/${output.path}`,
    bytes: output.bytes,
    sha256: output.sha256,
  }, `C140 adapter output drift: ${output.path}`);
}

assert.equal(validation.schema, 'c140-capability-validation/1');
assert.equal(validation.course_id, 'C140');
assert.equal(validation.boundary_id, 'C140-C5-54');
assert.equal(validation.result, 'pass');
assert.deepEqual(validation.counts, expectedCounts);
assert.equal(validation.negative_fixtures.length, 12);
assert.ok(validation.negative_fixtures.every(({ result }) => result === 'rejected'));
assert.deepEqual(validation.negative_fixtures.map(({ fixture_id }) => fixture_id), [
  'altered-penn-unit-id',
  'bad-public-route',
  'collapsed-random-witness',
  'copied-native-body-count',
  'copied-solution-body',
  'copied-source-text',
  'dropped-document',
  'false-uniform-pdf',
  'false-wcag',
  'flattened-rights',
  'restricted-public-access',
  'source-lock-drift',
]);
for (const key of [
  'all_54_public_routes_have_anonymous_http_200_hash_evidence',
  'canonical_machine_files',
  'complete_54_document_boundary',
  'component_rights_preserved_without_flattening',
  'fresh_projection_matches_native',
  'learner_and_educator_views_complete',
  'native_bodies_absent',
  'stable_entity_id_closure',
  'three_primary_public_receipts_preserved_byte_for_byte',
]) assert.equal(validation.checks[key], true, `C140 validation check failed: ${key}`);
assert.equal(validation.checks.negative_fixtures_rejected, 12);
assert.equal(validation.checks.two_run_build_identity.file_count, 38);
assert.equal(validation.checks.two_run_build_identity.tree_sha256, '8983788c83539c5f1450a3a2d57ad94ccf448ba1496b96ef384f76c6c314797b');

assert.equal(packetReceipt.schema, 'c140-capability-thin-packet-build-receipt/1');
assert.equal(packetReceipt.course_id, 'C140');
assert.equal(packetReceipt.result, 'PASS');
assert.deepEqual(packetReceipt.adapter_manifest, {
  path: 'manifest.json',
  bytes: 28428,
  sha256: '6573e4aa1e0a2909ced29229929aff00d6d9a5feb37ca1bde2a0989295fae37b',
});
assert.deepEqual(packetReceipt.adapter_validation, {
  path: 'validation.json',
  bytes: 10355,
  sha256: '531d1d33c05846d032ef17e59be87a9c2e542f152181ce3b12a10f477bf7edae',
});
assert.deepEqual(packetReceipt.archive, {
  path: 'build/C140_COMPLETE_THIN_CAPABILITY_METADATA_V1.zip',
  bytes: 1017886,
  sha256: '6c7745f1b999d72a517ec000259f1b230a922b56cf002a27f6506dea85baa296',
});
assert.equal(packetReceipt.content_policy, 'adapter_metadata_only_external_native_replay_dependency');
assert.equal(packetReceipt.external_hash_pinned_native_checkout_required_for_replay, true);
assert.equal(packetReceipt.two_build_byte_identity, true);
for (const key of [
  'exercise_answer_or_solution_bodies_included',
  'forbidden_payloads_included',
  'local_profile_data_included',
  'native_content_bodies_included',
  'public_state_changed',
]) assert.equal(packetReceipt[key], false, `C140 packet exclusion failed: ${key}`);
assert.equal(packetReceipt.native_inputs_included, 0);
assert.equal(packetReceipt.negative_fixtures_included, 12);
assert.deepEqual(packetReceipt.zip_checks, {
  crc_and_full_entry_readback: true,
  fixed_member_metadata: true,
  member_count: 45,
  payload_bytes: 8849174,
  sorted_member_order: true,
});

assert.equal(sourceLock.schema, 'c140-source-lock/1');
assert.equal(sourceLock.course_id, 'C140');
assert.equal(sourceLock.boundary_id, 'C140-C5-54');
assert.equal(sourceLock.input_count, 99);
assert.equal(sourceLock.inputs.length, 99);
assert.deepEqual(sourceLock.inputs, manifest.inputs);
assert.equal(sourceLock.repository, manifest.authority.repository);
assert.equal(sourceLock.public_content_commit, manifest.authority.content_commit);
assert.equal(sourceLock.public_pages_commit, manifest.authority.pages_commit);
assert.equal(sourceLock.release_tag, manifest.authority.release_tag);

assert.equal(githubRelease.schema, 'o006.c140.companion-c5.github-release-readback.v1');
assert.equal(githubRelease.status, 'pass');
assert.equal(githubRelease.mode, 'public-byte-verification');
assert.equal(githubRelease.tag, manifest.authority.release_tag);
assert.equal(githubRelease.local_files, 65);
assert.equal(githubRelease.local_bytes, 134904267);
assert.equal(githubRelease.component_separated_rights, true);
assert.equal(githubRelease.aggregate_uniform_relicense, false);
assert.equal(githubRelease.credential_access, false);
assert.equal(githubRelease.public_asset_readback_anonymous, true);
assert.equal(githubRelease.translation_provenance, 'OpenAI Codex gpt-5.6-sol, Ultra');
assert.equal(githubRelease.release_scope.c140_course, 'complete on admitted boundary');
assert.equal(githubRelease.release_scope.remaining, 'none within admitted C140 boundary');

assert.equal(githubPages.schema, 'o006.c140.companion-c5.github-pages-readback.v1');
assert.equal(githubPages.status, 'pass');
assert.equal(githubPages.public_base_url, nativeOrigin);
assert.equal(githubPages.files.length, 259);
assert.equal(githubPages.anonymous_content_readback, true);
assert.equal(githubPages.committed_content_readback.all_match, true);
assert.equal(githubPages.network_runtime_dependencies_tested, 0);

assert.equal(zenodoReadback.schema, 'o006.c140.zenodo-c140-companion-c5-publication.v1');
assert.equal(zenodoReadback.version, '2026.08.31.c140-companion-c5');
assert.equal(zenodoReadback.required_concept_record_id, '22077422');
assert.equal(zenodoReadback.required_concept_doi, '10.5281/zenodo.22077422');
assert.equal(zenodoReadback.credential_access, false);
assert.equal(zenodoReadback.translation_provenance, 'OpenAI Codex gpt-5.6-sol, Ultra');
assert.equal(zenodoReadback.local_files, 65);
assert.equal(zenodoReadback.local_bytes, 134904267);
assert.equal(zenodoReadback.inherited_files_untouched, true);
assert.equal(zenodoReadback.public.anonymous_readback, true);
assert.equal(zenodoReadback.public.file_count, 65);
assert.equal(zenodoReadback.public.record_id, '22208527');

assert.equal(publicEvidence.schema, 'c140-public-evidence/1');
assert.equal(publicEvidence.status, 'pass');
assert.equal(publicEvidence.translation_provenance, 'OpenAI Codex gpt-5.6-sol, Ultra');
assert.equal(publicEvidence.pages.anonymous_readback, true);
assert.equal(publicEvidence.pages.base_url, nativeOrigin);
assert.equal(publicEvidence.pages.collection_files, 259);
assert.equal(publicEvidence.pages.collection_bytes, 35170536);
assert.equal(publicEvidence.pages.course_document_files.length, 54);
assert.ok(publicEvidence.pages.course_document_files.every(({ http_status }) => http_status === 200));
assert.equal(new Set(publicEvidence.pages.course_document_files.map(({ path }) => path)).size, 54);
assert.equal(publicEvidence.repository.anonymous_asset_readback, true);
assert.equal(publicEvidence.repository.content_commit, manifest.authority.content_commit);
assert.equal(publicEvidence.repository.file_count, 65);
assert.equal(publicEvidence.repository.release_id, 379767406);
assert.equal(publicEvidence.repository.release_tag, manifest.authority.release_tag);
assert.equal(publicEvidence.repository.total_bytes, 134904267);
assert.equal(publicEvidence.zenodo.access_right, 'open');
assert.equal(publicEvidence.zenodo.anonymous_readback, true);
assert.equal(publicEvidence.zenodo.doi, manifest.authority.zenodo_doi);
assert.equal(publicEvidence.zenodo.record_id, 22208527);
assert.equal(publicEvidence.zenodo.file_count, 65);
assert.equal(publicEvidence.zenodo.total_bytes, 134904267);
assert.deepEqual(publicEvidence.reader.primary_pdf, {
  bytes: 20170549,
  download_url: 'https://github.com/KokunoYumeto/penn-state-stat-415-id/releases/download/v2026.08.31.c140-companion-c5/00_00_stat415-pengantar-statistika-matematis-id.pdf',
  http_status: 200,
  name: '00_00_stat415-pengantar-statistika-matematis-id.pdf',
  sha256: 'f39c1c438cc3e793fe9522eb11f5b02704d89fcdc7aecb2207a599087d458964',
});
assert.deepEqual(publicEvidence.reader.epub, {
  bytes: 12301415,
  download_url: 'https://github.com/KokunoYumeto/penn-state-stat-415-id/releases/download/v2026.08.31.c140-companion-c5/00_01_stat415-pengantar-statistika-matematis-id.epub',
  http_status: 200,
  name: '00_01_stat415-pengantar-statistika-matematis-id.epub',
  sha256: 'e122d65348971b91a5ac0c7a8219e0fa3e0eabedb92d130c661648e399e3c574',
});
assert.equal(publicEvidence.reader.native_html_document_count, 54);
assert.equal(publicEvidence.reader.single_uniform_pdf_for_all_components_claimed, false);

assert.equal(capabilities.schema, 'course-learning-capability/1');
assert.equal(capabilities.course_id, 'C140');
assert.equal(capabilities.boundary_id, 'C140-C5-54');
assert.equal(capabilities.status, 'verified');
assert.deepEqual(capabilities.counts, expectedCounts);
assert.equal(capabilities.features.unit_identity, 'verified');
assert.equal(capabilities.features.terminology, 'verified');
assert.equal(capabilities.features.corrections, 'verified');
assert.equal(capabilities.features.component_rights, 'verified-distinct');
assert.equal(capabilities.features.native_html_delivery, 'verified');
assert.equal(capabilities.features.educator_unit_alignment, 'verified');
assert.equal(capabilities.features.native_body_centralization, 'not-performed');

assert.equal(learnerMap.schema, 'c140-learner-map/1');
assert.equal(learnerMap.course_id, 'C140');
assert.equal(learnerMap.boundary_id, 'C140-C5-54');
assert.equal(learnerMap.document_count, 54);
assert.equal(learnerMap.components.penn_spine.length, 14);
assert.equal(learnerMap.components.random_completeness.length, 1);
assert.equal(learnerMap.components.companion_index.length, 1);
assert.equal(learnerMap.components.companion_theory.length, 13);
assert.equal(learnerMap.components.companion_simulations.length, 6);
assert.equal(learnerMap.components.companion_mastery.length, 13);
assert.equal(learnerMap.components.companion_assessments.length, 4);
assert.equal(learnerMap.components.companion_capstones.length, 2);

assert.equal(educatorMap.schema, 'c140-educator-map/1');
assert.equal(educatorMap.course_id, 'C140');
assert.equal(educatorMap.boundary_id, 'C140-C5-54');
assert.equal(educatorMap.documents.length, 54);
assert.equal(educatorMap.solved_problems.length, 146);
assert.equal(educatorMap.rubrics.length, 62);
assert.equal(educatorMap.simulations.length, 6);
assert.equal(educatorMap.assessments.length, 4);
assert.equal(educatorMap.capstones.length, 2);
assert.equal(new Set(educatorMap.solved_problems.map(({ id }) => id)).size, 146);
assert.equal(new Set(educatorMap.rubrics.map(({ id }) => id)).size, 62);

assert.deepEqual(claimBoundary, {
  boundary_id: 'C140-C5-54',
  central_html_reauthors_native_content: false,
  component_count: 3,
  component_rights_flattened: false,
  course_id: 'C140',
  exercise_answer_or_solution_bodies_copied: 0,
  fully_solved_problem_identities: 146,
  native_bodies_copied: 0,
  native_html_available: true,
  pdf_ua_claimed: false,
  public_access_state_changed: false,
  public_documents: 54,
  reversible_content_exchange_claimed: false,
  schema: 'c140-claim-boundary/1',
  single_uniform_pdf_claimed: false,
  source_text_copied: 0,
  uniform_license_claimed: false,
  wcag_conformance_claimed: false,
  whole_course_component_boundary_proven: true,
});

const indexNames = [
  'document-index.jsonl',
  'penn-unit-index.jsonl',
  'penn-segment-index.jsonl',
  'penn-terms-index.jsonl',
  'penn-corrections-index.jsonl',
  'random-entity-index.jsonl',
  'random-relation-index.jsonl',
  'random-terms-index.jsonl',
  'random-adverse-index.jsonl',
  'companion-entity-index.jsonl',
  'companion-relation-index.jsonl',
  'rights-index.jsonl',
];
const publicMappings = [
  [`${base}/manifest.json`, `${publicBase}/manifest.json`],
  [`${base}/views/C140.html`, `${publicBase}/C140.html`],
  [`${base}/views/C140-pengajar.html`, `${publicBase}/C140-pengajar.html`],
  [`${base}/views/capabilities.json`, `${publicBase}/capabilities.json`],
  [`${base}/data/learner-map.json`, `${publicBase}/learning-map.json`],
  [`${base}/data/educator-map.json`, `${publicBase}/educator-map.json`],
  [`${base}/data/public-evidence.json`, `${publicBase}/public-evidence.json`],
  [`${base}/data/claim-boundary.json`, `${publicBase}/claim-boundary.json`],
  ...indexNames.map((name) => [`${base}/data/${name}`, `${publicBase}/data/${name}`]),
  [`${base}/input/source-lock.json`, `${publicBase}/source-lock.json`],
  [`${base}/input/github-release-readback.json`, `${publicBase}/github-release-readback.json`],
  [`${base}/input/github-pages-readback.json`, `${publicBase}/github-pages-readback.json`],
  [`${base}/input/zenodo-readback.json`, `${publicBase}/zenodo-readback.json`],
  [`${base}/validation.json`, `${publicBase}/validation.json`],
];

const staged = new Map();
for (const [source, target] of publicMappings) {
  let bytes = await readFile(resolve(root, source));
  const expectedRelativeLinks = new Map([
    [`${publicBase}/C140.html`, 2],
    [`${publicBase}/C140-pengajar.html`, 11],
  ]).get(target);
  if (expectedRelativeLinks !== undefined) {
    const original = bytes.toString('utf8');
    assert.equal((original.match(/\.\.\/data\//g) ?? []).length, expectedRelativeLinks, `${source}: adapter-relative data-link count drift.`);
    let projected = original.replaceAll('../data/', 'data/');
    if (target === `${publicBase}/C140.html`) {
      assert.equal(
        (projected.match(/data\/learner-map\.json/g) ?? []).length,
        1,
        `${source}: learner-map link count drift.`,
      );
      projected = projected.replace('data/learner-map.json', 'learning-map.json');
    }
    assert.equal(projected.includes('../data/'), false, `${target}: adapter-relative data link survived projection.`);
    bytes = Buffer.from(projected, 'utf8');
  }
  staged.set(target, bytes);
}
assert.equal(staged.size, 25);
const stagedIdentity = (path) => {
  const bytes = staged.get(path);
  assert.ok(bytes, `Missing staged C140 file: ${path}`);
  return bufferIdentity(path, bytes);
};
for (const target of [`${publicBase}/C140.html`, `${publicBase}/C140-pengajar.html`]) {
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
  ['anonymous_github_release_readback', paths.githubRelease],
  ['anonymous_github_pages_readback', paths.githubPages],
  ['anonymous_zenodo_readback', paths.zenodo],
  ['verified_native_public_release', paths.publicEvidence],
  ['learner_document_map', paths.learnerMap],
  ['educator_identity_map', paths.educatorMap],
  ['claim_boundary', paths.claimBoundary],
  ...indexNames.map((name) => [`native_${name.replace(/\.jsonl$/, '').replaceAll('-', '_')}`, `${base}/data/${name}`]),
]) {
  const fact = await identity(path);
  evidence.push({ kind, locator: path, bytes: fact.bytes, sha256: fact.sha256, verified_date: verifiedDate });
}

const scope = 'Batas C5 lengkap: 54 dokumen publik (14 dokumen tulang punggung Penn, satu donor Random, dan 39 dokumen pendamping), 8.358 identitas entitas stabil, 2.423 relasi struktural, 234 rekaman istilah, 261 koreksi atau rekaman adverse, 146 masalah terselesaikan, 62 rubrik, dan sembilan proyeksi hak komponen.';
const limitations = [
  'Adapter adalah proyeksi zero-copy atas identitas, struktur, istilah, koreksi, hak, rute, dan bukti; badan sumber, soal, jawaban, dan solusi tetap pada edisi native publik.',
  'Hak Penn, chrome atau mark yang dikecualikan, dua saksi Random, MathJax, pendamping, serta dua dataset capstone tetap sembilan proyeksi terpisah dan tidak diberi satu lisensi payung.',
  'Koleksi HTML native mencakup 54 dokumen. PDF dan EPUB terverifikasi hanya untuk tulang punggung Penn, bukan satu berkas seragam untuk ketiga komponen.',
  'PDF/UA, kepatuhan WCAG, paket HTML luring tunggal, dan pertukaran konten reversibel tidak diklaim.',
  'Replay penuh memerlukan checkout native eksternal yang dipatok pada 99 identitas input.',
];

const integrationTarget = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(integrationTarget);
const toolId = 'c140.open_learner_hub';
const oldSemantic = overrides.semantic_adapters?.C140;
const oldEducator = overrides.educator_evidence?.C140;
const sealedSecondaryLocators = new Set([
  'backend/course-capsule-v1/adapters/c140-v231/manifest.json',
  'backend/course-capsule-v1/validation/20260907/C140_TWIN.json',
  'backend/v2.3/specs/20260907/C140.json',
]);
const sealedSecondaryEvidence = [];
for (const row of oldSemantic?.evidence ?? []) {
  if (!sealedSecondaryLocators.has(row.locator)) continue;
  assert.equal(typeof row.locator, 'string', 'Incoming C140 sealed evidence lacks a locator.');
  const fact = await identity(row.locator);
  assert.equal(fact.bytes, row.bytes, `${row.locator}: incoming C140 evidence byte drift.`);
  assert.equal(fact.sha256, row.sha256, `${row.locator}: incoming C140 evidence hash drift.`);
  sealedSecondaryEvidence.push(clone(row));
}
assert.equal(sealedSecondaryEvidence.length, 3, 'C140 sealed secondary evidence inventory drift.');
const integrationToolValue = overrides.learner_tools?.C140;
const integrationToolRows = integrationToolValue == null
  ? []
  : Array.isArray(integrationToolValue)
    ? integrationToolValue
    : [integrationToolValue];
assert.ok(integrationToolRows.length <= 1, 'Duplicate C140 tools already exist in integration-overrides.');
assert.ok(
  integrationToolRows.every((row) => row?.tool_id === toolId),
  'Refusing to remove an unrelated C140 tool from integration-overrides.',
);
const stripManagedIntegration = (value) => {
  const result = clone(value);
  for (const key of ['course_truth', 'semantic_adapters', 'native_capabilities', 'educator_evidence', 'learner_tools']) {
    if (result[key]) delete result[key].C140;
  }
  return result;
};
const unrelatedIntegration = stripManagedIntegration(overrides);
overrides.course_truth ??= {};
overrides.semantic_adapters ??= {};
overrides.native_capabilities ??= {};
overrides.educator_evidence ??= {};
if (overrides.learner_tools) delete overrides.learner_tools.C140;

overrides.course_truth.C140 = {
  state: 'published',
  version: '2026.08.31.c140-companion-c5',
  corpus: 'Statistika Matematis C140 — tulang punggung Penn, donor kelengkapan Random, dan pendamping orisinal',
  note: 'Batas C5 lengkap dan terbuka: 54 dokumen HTML publik, 8.358 identitas entitas stabil, 2.423 relasi, 146 masalah terselesaikan, 62 rubrik, serta sembilan proyeksi hak yang tetap terpisah.',
  reader: nativeOrigin,
  edition: zenodoPrimaryPdfUrl,
  repository: publicEvidence.repository.url,
  release: publicEvidence.repository.release_url,
  zenodo: `https://doi.org/${publicEvidence.zenodo.doi}`,
  progress: {
    unitLabel: 'dokumen kursus C140',
    totalUnits: 54,
    translationBearingUnits: 54,
    integrationReadyUnits: 54,
    canonicalUnits: 54,
    publicUnits: 54,
    publicBoundary: '14 Penn + 1 Random + 39 pendamping',
    updatedAt: '2026-08-31',
  },
};
const mergedSemanticEvidence = [...evidence, ...sealedSecondaryEvidence]
  .filter((row, index, rows) => rows.findIndex((candidate) => (
    candidate.kind === row.kind
      && candidate.locator === row.locator
      && candidate.sha256 === row.sha256
  )) === index);
overrides.semantic_adapters.C140 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_complete_54_document_three_component_boundary_8358_stable_entity_ids_2423_structural_relations_234_terminology_rows_261_correction_or_adverse_rows_146_solved_problem_identities_62_rubrics_and_9_distinct_rights_projections',
  evidence: mergedSemanticEvidence,
};
overrides.native_capabilities.C140 = {};
for (const capability of [
  'unit_identity',
  'terminology',
  'translation_rights',
  'corrections',
  'build',
  'deterministic_replay',
  'educator_unit_alignment',
  'translation_ledger',
]) overrides.native_capabilities.C140[capability] = { status: 'verified', evidence };

const teacher = stagedIdentity(`${publicBase}/C140-pengajar.html`);
const managedEducatorIds = new Set([
  'C140:educator-hub-v1',
  'C140:educator-map-v1',
  ...indexNames.map((name) => `C140:${name.replace(/\.jsonl$/, '')}-v1`),
]);
const educatorResources = (oldEducator?.resources ?? []).filter(({ id }) => !managedEducatorIds.has(id));
const educatorMapFact = stagedIdentity(`${publicBase}/educator-map.json`);
educatorResources.push({
  id: 'C140:educator-hub-v1',
  title: 'Peta pengajar untuk tiga komponen C140',
  resource_type: 'teacher-guide',
  status: 'verified',
  url: `${publicOrigin}/C140-pengajar.html`,
  scope,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
educatorResources.push({
  id: 'C140:educator-map-v1',
  title: 'Peta pengajar C140 atas 54 dokumen dan identitas asesmen',
  resource_type: 'educator-data',
  status: 'verified',
  url: `${publicOrigin}/educator-map.json`,
  scope: 'Peta zero-copy atas dokumen, 146 masalah terselesaikan, 62 rubrik, enam simulasi, empat asesmen, dua capstone, serta sebelas indeks tata kelola.',
  bytes: educatorMapFact.bytes,
  sha256: educatorMapFact.sha256,
});
const educatorIndexMetadata = [
  ['document-index.jsonl', 'Indeks 54 dokumen C140', 'identity-index'],
  ['penn-unit-index.jsonl', 'Indeks 6.510 unit Penn', 'identity-index'],
  ['penn-segment-index.jsonl', 'Indeks 4.932 segmen Penn', 'translation-ledger'],
  ['penn-terms-index.jsonl', 'Indeks 192 istilah Penn', 'terminology-register'],
  ['penn-corrections-index.jsonl', 'Indeks 242 koreksi Penn', 'correction-ledger'],
  ['random-entity-index.jsonl', 'Indeks 325 entitas Random', 'identity-index'],
  ['random-relation-index.jsonl', 'Indeks 474 relasi Random', 'educator-data'],
  ['random-terms-index.jsonl', 'Indeks 42 istilah Random', 'terminology-register'],
  ['random-adverse-index.jsonl', 'Indeks 19 rekaman adverse Random', 'correction-ledger'],
  ['companion-entity-index.jsonl', 'Indeks 1.523 entitas pendamping', 'identity-index'],
  ['companion-relation-index.jsonl', 'Indeks 1.949 relasi pendamping', 'educator-data'],
  ['rights-index.jsonl', 'Sembilan proyeksi hak komponen C140', 'rights-ledger'],
];
for (const [filename, title, resourceType] of educatorIndexMetadata) {
  const fact = stagedIdentity(`${publicBase}/data/${filename}`);
  educatorResources.push({
    id: `C140:${filename.replace(/\.jsonl$/, '')}-v1`,
    title,
    resource_type: resourceType,
    status: 'verified',
    url: `${publicOrigin}/data/${filename}`,
    scope: 'Indeks metadata native dengan identitas dan hash stabil; badan sumber, soal, jawaban, dan solusi tidak disalin.',
    bytes: fact.bytes,
    sha256: fact.sha256,
  });
}
assert.equal(new Set(educatorResources.map(({ id }) => id)).size, educatorResources.length, 'Duplicate C140 educator resource ID.');
overrides.educator_evidence.C140 = {
  status: 'verified',
  verified_date: verifiedDate,
  locator: `${publicOrigin}/C140-pengajar.html`,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: [
    'activities_labs',
    'exercise_bank',
    'lesson_sequences',
    'remix_selectors',
    'rubrics',
    'solution_provenance',
    'staged_hints_answers_solutions',
  ],
  resources: educatorResources,
};
assert.deepEqual(stripManagedIntegration(overrides), unrelatedIntegration, 'Admission changed an unrelated integration override.');
assert.deepEqual(overrides.native_capabilities.D30, unrelatedIntegration.native_capabilities?.D30, 'D30 native capabilities changed.');
assert.deepEqual(overrides.semantic_adapters.D30, unrelatedIntegration.semantic_adapters?.D30, 'D30 semantic adapter changed.');
assert.deepEqual(overrides.educator_evidence.D30, unrelatedIntegration.educator_evidence?.D30, 'D30 educator evidence changed.');
assert.deepEqual(overrides.learner_tools?.D30, unrelatedIntegration.learner_tools?.D30, 'D30 learner tools changed.');

const pagesEntry = publicEvidence.pages.course_document_files.find(({ path }) => path === 'index.html');
assert.ok(pagesEntry, 'C140 public course entry is missing.');
const pagesReceipt = {
  kind: 'anonymous_public_pages_readback',
  locator: publicEvidence.pages.base_url,
  verified_date: verifiedDate,
};
const nativeHtml = {
  status: 'verified',
  format: 'text/html',
  url: nativeOrigin,
  bytes: pagesEntry.bytes,
  sha256: pagesEntry.sha256,
  scope: 'whole_course_54_document_three_component_collection',
  evidence: pagesReceipt,
};
const releaseReceipt = {
  kind: 'anonymous_public_release_asset_readback',
  locator: publicEvidence.repository.release_url,
  verified_date: verifiedDate,
};
const pdf = {
  status: 'verified',
  format: 'application/pdf',
  url: publicEvidence.reader.primary_pdf.download_url,
  bytes: publicEvidence.reader.primary_pdf.bytes,
  sha256: publicEvidence.reader.primary_pdf.sha256,
  scope: 'penn_spine_component_only_not_uniform_whole_course',
  evidence: releaseReceipt,
};
const epub = {
  status: 'verified',
  format: 'application/epub+zip',
  url: publicEvidence.reader.epub.download_url,
  bytes: publicEvidence.reader.epub.bytes,
  sha256: publicEvidence.reader.epub.sha256,
  scope: 'penn_spine_component_only_not_uniform_whole_course',
  evidence: releaseReceipt,
};
const learnerDeliveryTarget = 'backend/authority/learner-delivery-overrides-v1.json';
const learnerDelivery = await load(learnerDeliveryTarget);
assert.equal(learnerDelivery.schema_version, '1.0.0');
assert.ok(learnerDelivery.courses && !Array.isArray(learnerDelivery.courses));
const unrelatedLearnerDelivery = clone(learnerDelivery);
delete unrelatedLearnerDelivery.courses.C140;
learnerDelivery.courses.C140 = {
  primary: clone(nativeHtml),
  online_html: clone(nativeHtml),
  pdf: clone(pdf),
  epub: clone(epub),
  portable_html: { status: 'not_yet_produced' },
  capabilities: {
    semantic_html: { status: 'verified', evidence: pagesReceipt },
    mathml: { status: 'available_unverified', evidence: pagesReceipt },
    print_profile: {
      status: 'verified',
      scope: 'penn_spine_component_only_not_uniform_whole_course',
      evidence: { ...releaseReceipt, pdf_bytes: pdf.bytes, pdf_sha256: pdf.sha256 },
    },
    chapter_downloads: { status: 'not_yet_produced' },
  },
};
const learnerDeliveryAfter = clone(learnerDelivery);
delete learnerDeliveryAfter.courses.C140;
assert.deepEqual(learnerDeliveryAfter, unrelatedLearnerDelivery, 'Admission changed an unrelated learner-delivery override.');
assert.deepEqual(learnerDelivery.courses.D30, unrelatedLearnerDelivery.courses.D30, 'D30 learner delivery changed.');

const learnerToolInput = {
  tool_id: toolId,
  label: 'C140 · Statistika Matematis',
  href: 'backend/c140/C140.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page_path: `${publicBase}/C140.html`,
  resource_path: `${publicBase}/learning-map.json`,
  evidence_path: `${publicBase}/validation.json`,
  limitations,
};
const learnerToolsTarget = 'backend/authority/learner-tools-overrides-v1.json';
const learnerTools = await load(learnerToolsTarget);
assert.ok(Array.isArray(learnerTools.courses), 'Learner-tool override courses must be an array.');
const unrelatedLearnerTools = clone(learnerTools);
unrelatedLearnerTools.courses = unrelatedLearnerTools.courses.filter(({ course_id }) => course_id !== 'C140');
const c140Rows = learnerTools.courses.filter(({ course_id }) => course_id === 'C140');
assert.ok(c140Rows.length <= 1, 'Duplicate C140 rows already exist in learner-tool overrides.');
const oldTools = c140Rows[0]?.tools ?? [];
assert.ok(Array.isArray(oldTools), 'C140 learner tools must be an array.');
const mergedTools = [...oldTools.filter(({ tool_id }) => tool_id !== toolId), learnerToolInput]
  .sort((left, right) => left.tool_id.localeCompare(right.tool_id));
const c140ToolRow = { course_id: 'C140', tools: mergedTools };
const existingIndex = learnerTools.courses.findIndex(({ course_id }) => course_id === 'C140');
if (existingIndex >= 0) learnerTools.courses[existingIndex] = c140ToolRow;
else learnerTools.courses.push(c140ToolRow);
const learnerToolsAfter = clone(learnerTools);
learnerToolsAfter.courses = learnerToolsAfter.courses.filter(({ course_id }) => course_id !== 'C140');
assert.deepEqual(learnerToolsAfter, unrelatedLearnerTools, 'Admission changed an unrelated learner-tool override.');
assert.equal(new Set(learnerTools.courses.map(({ course_id }) => course_id)).size, learnerTools.courses.length, 'Duplicate learner-tool course ID.');
assert.equal(
  new Set(learnerTools.courses.flatMap(({ tools }) => tools.map(({ tool_id }) => tool_id))).size,
  learnerTools.courses.flatMap(({ tools }) => tools).length,
  'Duplicate learner-tool ID.',
);
assert.ok(!Object.hasOwn(overrides.learner_tools ?? {}, 'C140'), 'Managed C140 tool must exist only in dedicated learner-tool authority.');

const authorityWrites = new Map([
  [integrationTarget, jsonBytes(overrides)],
  [learnerDeliveryTarget, jsonBytes(learnerDelivery)],
  [learnerToolsTarget, jsonBytes(learnerTools)],
]);
const mutationTargets = [...staged.keys(), ...authorityWrites.keys()];
assert.equal(new Set(mutationTargets).size, mutationTargets.length, 'Duplicate C140 admission target.');
for (const target of mutationTargets) {
  assert.ok(!target.split('/').includes('..'), `Unsafe admission target: ${target}`);
  assert.doesNotMatch(target, /(?:^|\/)d30(?:\/|$)/i, `D30 target is forbidden: ${target}`);
  assert.ok(
    target.startsWith(`${publicBase}/`)
      || target === integrationTarget
      || target === learnerDeliveryTarget
      || target === learnerToolsTarget,
    `Out-of-scope C140 admission target: ${target}`,
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
  admitted_roles: ['C140'],
  contract: manifest.contract,
  boundary_id: manifest.boundary_id,
  native_locale: manifest.locale,
  public_files_staged: staged.size,
  public_documents: expectedCounts.public_documents,
  stable_entity_ids: expectedCounts.stable_entity_ids,
  structural_relations: expectedCounts.structural_relations,
  component_rights: expectedCounts.component_rights,
  learner_tool_authority: learnerToolsTarget,
  public_state_changed: false,
  producer_root_modified: false,
  d30_modified: false,
}, null, 2));
