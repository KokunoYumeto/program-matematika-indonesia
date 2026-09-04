import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/d70-capability-v1';
const load = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const identity = async path => {
  const data = await readFile(resolve(root, path));
  return {path, bytes: data.length, sha256: createHash('sha256').update(data).digest('hex')};
};

const manifest = await load(`${base}/manifest.json`);
const validation = await load(`${base}/validation.json`);
const sourceLock = await load(`${base}/input/source-lock.json`);
const capabilities = await load(`${base}/data/capabilities.json`);
const publicEvidence = await load(`${base}/data/evidence.json`);

assert.equal(manifest.course_id, 'D70');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.content_policy, 'metadata_and_evidence_only');
assert.equal(manifest.zero_copy_native_bodies, true);
assert.equal(manifest.full_native_roundtrip_claimed, false);
assert.equal(manifest.public_state_changed, false);
assert.equal(validation.result, 'PASS');
assert.equal(validation.contract, manifest.contract);
const manifestIdentity = await identity(`${base}/manifest.json`);
assert.deepEqual(validation.manifest, {
  path: 'manifest.json',
  bytes: manifestIdentity.bytes,
  sha256: manifestIdentity.sha256,
});
assert.deepEqual(validation.source_lock, manifest.source_lock);
assert.equal(validation.content_policy, manifest.content_policy);
assert.equal(validation.public_state_changed, false);
assert.deepEqual(validation.counts, manifest.counts);

const expectedCounts = {
  components: 4,
  corrections: 80,
  cring_repairs: 9,
  cring_roots: 6,
  diagnostic_expected_answers: 8,
  diagnostic_points: 8,
  diagnostic_targets: 14,
  diagnostics: 8,
  duncan_roots: 7,
  li_adjustments: 71,
  li_roots: 41,
  mastery: 8,
  mastery_answers: 8,
  mastery_hints: 16,
  mastery_targets: 13,
  native_roots: 54,
  original_bridges: 3,
  pages: 716,
  relations: 36,
  rights: 9,
  stage_memberships: 36,
  stages: 7,
  terms: 690,
  terms_admitted: 689,
  terms_provisional: 1,
  units: 20,
};
assert.deepEqual(manifest.counts, expectedCounts);
assert.equal(sourceLock.course_id, 'D70');
assert.equal(sourceLock.input_count, 57);
assert.equal(sourceLock.inputs.length, 57);
assert.equal(sourceLock.native_repository.repository, 'https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id');
assert.equal(sourceLock.native_repository.content_commit, '91b76d0381aa0d4c6614ad6556fe779fe8039f93');
assert.equal(sourceLock.native_repository.content_tree, 'a017f0a2efc016d1a2b6b422577de77e0db9b6ac');
assert.equal(sourceLock.native_repository.receipt_commit, '26e6f531e9309e83998325a8c7b705e92d293287');
assert.equal(sourceLock.native_repository.receipt_tree, 'cd1006dd85248c6b76d3cb1623c7049837a91cd1');
assert.equal(validation.negative_fixtures.length, 33);
assert.ok(validation.negative_fixtures.every(row => row.result === 'PASS'));
assert.ok(Object.values(validation.checks).every(Boolean));
assert.equal(validation.replay.two_builds_identical, true);
assert.equal(validation.replay.committed_bytes_identical, true);
assert.equal(validation.replay.files, 54);
assert.equal(capabilities.reproducibility.full_native_roundtrip, false);
assert.equal(capabilities.reproducibility.li_whole_reader_byte_replay, false);
assert.equal(capabilities.reproducibility.pdf_byte_replay, false);
assert.deepEqual(capabilities.source_support, {answers: 0, exercises: 229, hints: 53, solutions: 0});
assert.equal(capabilities.edition_original_support.diagnostics, 8);
assert.equal(capabilities.edition_original_support.mastery_tasks, 8);
assert.equal(capabilities.edition_original_support.mastery_hints, 16);
assert.equal(capabilities.edition_original_support.mastery_answers, 8);
assert.equal(capabilities.accessibility.native_semantic_html, false);
assert.equal(capabilities.accessibility.native_mathml, false);
assert.equal(capabilities.accessibility.native_epub, false);
assert.equal(capabilities.accessibility.tagged_pdf_claimed, false);
assert.equal(capabilities.accessibility.wcag_conformance_claimed, false);
assert.equal(capabilities.accessibility.assistive_technology_testing_claimed, false);
assert.equal(publicEvidence.record_id, 22160944);
assert.equal(publicEvidence.doi, '10.5281/zenodo.22160944');
assert.equal(publicEvidence.concept_doi, '10.5281/zenodo.22160943');
assert.equal(publicEvidence.repository, sourceLock.native_repository.repository);
assert.equal(publicEvidence.file_count, 9);
assert.equal(publicEvidence.public_files.length, 9);
assert.equal(publicEvidence.total_bytes, 5155778);
assert.equal(publicEvidence.anonymous_full_file_readback, true);
assert.equal(publicEvidence.public_readback_result, 'PASS');
assert.equal(publicEvidence.content_commit, sourceLock.native_repository.content_commit);
assert.equal(publicEvidence.content_tree, sourceLock.native_repository.content_tree);
assert.equal(publicEvidence.receipt_commit, sourceLock.native_repository.receipt_commit);
assert.equal(publicEvidence.receipt_tree, sourceLock.native_repository.receipt_tree);
assert.equal(publicEvidence.public_files.reduce((sum, row) => sum + row.bytes, 0), publicEvidence.total_bytes);
for (const row of publicEvidence.public_files) {
  assert.ok(row.name);
  assert.ok(Number.isSafeInteger(row.bytes) && row.bytes > 0);
  assert.match(row.sha256, /^[a-f0-9]{64}$/);
  assert.match(row.url, /^https:\/\/zenodo\.org\/api\/records\/22160944\/files\//);
}
for (const item of manifest.outputs) {
  assert.deepEqual(
    await identity(`${base}/${item.path}`),
    {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256},
  );
}

const publicMappings = [
  [`${base}/views/D70.html`, 'docs/backend/d70/D70.html'],
  [`${base}/views/D70-pengajar.html`, 'docs/backend/d70/D70-pengajar.html'],
  [`${base}/data/learning-map.json`, 'docs/backend/d70/learning-map.json'],
  [`${base}/validation.json`, 'docs/backend/d70/validation.json'],
];
for (const [source, target] of publicMappings) {
  const bytes = await readFile(resolve(root, source));
  await mkdir(dirname(resolve(root, target)), {recursive: true});
  await writeFile(resolve(root, target), bytes);
  assert.deepEqual(
    await identity(target),
    {path: target, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')},
  );
}

const evidence = [];
for (const [kind, path] of [
  ['central_adapter_manifest', `${base}/manifest.json`],
  ['deterministic_validation_receipt', `${base}/validation.json`],
  ['native_metadata_intake', `${base}/input/source-lock.json`],
]) {
  const {bytes, sha256} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-05'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
assert.ok(
  !overrides.semantic_adapters.D70
    || !overrides.semantic_adapters.D70.contract_version
    || overrides.semantic_adapters.D70.contract_version === manifest.contract,
  'Preserve a different admitted D70 contract',
);
overrides.semantic_adapters.D70 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_four_component_716_page_projection_of_54_native_roots_20_routes_36_relations_8_diagnostics_and_8_edition_original_mastery_tasks',
  evidence,
};

overrides.native_capabilities.D70 = {...overrides.native_capabilities.D70};
for (const capability of [
  'unit_identity',
  'translation_ledger',
  'terminology',
  'translation_rights',
  'corrections',
  'educator_unit_alignment',
]) {
  overrides.native_capabilities.D70[capability] = {status: 'verified', evidence};
}
// The adapter and locked metadata replay deterministically, but the four-part
// native edition and its PDFs do not yet have a complete byte replay.
overrides.native_capabilities.D70.build = {status: 'available_unverified', evidence};
overrides.native_capabilities.D70.deterministic_replay = {status: 'available_unverified', evidence};

const scope = 'Empat komponen/716 halaman; 54 akar native, 20 rute, 36 prasyarat, 8 diagnostik, dan 8 tugas penguasaan dengan 16 petunjuk/8 jawaban edisi-asli.';
const limitations = [
  'Isi pembelajaran berbahasa Indonesia; antarmuka Inggris tidak menerjemahkan isi.',
  'Adapter adalah navigasi metadata zero-copy dan tidak memuat badan buku, rumus, TeX, PDF, atau arsip sumber native.',
  'Empat komponen mempertahankan bahasa sumber dan hak masing-masing; tidak ada lisensi payung yang direka.',
  'P01-P06 hanya dipetakan pada tingkat komponen Li karena rute native tidak menunjuk akar unit Li yang persis.',
  'Komponen CRing hanya mencakup enam rentang terpilih, bukan seluruh karya CRing.',
  'Enam lembar tugas Duncan, 49 soal, dan satu solusi parsial berada di luar repositori CC BY yang dipatok dan tidak disertakan.',
  'Komponen sumber menyediakan 229 latihan dan 53 petunjuk, tetapi nol jawaban/solusi; delapan jawaban di sini adalah materi edisi-asli yang terpisah.',
  'Tidak ada HTML semantik native, MathML native, EPUB native, PDF bertag, klaim WCAG, atau uji pengguna teknologi bantu.',
  'Replay penuh pembaca Li dan byte PDF belum terbukti; replay terverifikasi hanya untuk adapter dan metadata yang dikunci.',
];
const tool = {
  tool_id: 'd70.open_learner_hub',
  label: 'D70 · Aljabar Pascasarjana',
  href: 'backend/d70/D70.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/d70/D70.html'),
  resource: await identity('docs/backend/d70/learning-map.json'),
  evidence: await identity('docs/backend/d70/validation.json'),
  limitations,
};
assert.ok(
  !overrides.learner_tools.D70
    || overrides.learner_tools.D70.every(old => old.tool_id === tool.tool_id),
  'Preserve unrelated D70 tools',
);
overrides.learner_tools.D70 = [tool];

const old = overrides.educator_evidence.D70;
const teacher = await identity('docs/backend/d70/D70-pengajar.html');
const url = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d70/D70-pengajar.html';
const resources = (old?.resources ?? []).filter(
  resource => !['D70:native-educator-observation', 'D70:educator-hub-v1'].includes(resource.id),
);
resources.push({
  id: 'D70:native-educator-observation',
  title: 'Materi pendukung native aljabar pascasarjana',
  resource_type: 'teacher-guide',
  status: 'available_unverified',
  url: 'https://zenodo.org/records/22160944',
  scope: 'Observasi historis pada rilis native; fitur lama tetap belum diverifikasi oleh lapisan pusat.',
});
resources.push({
  id: 'D70:educator-hub-v1',
  title: 'Rute, diagnostik, mastery, istilah, hak, koreksi, dan provenans D70 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url,
  scope: `${scope} Materi sumber tidak memiliki jawaban/solusi; hanya delapan jawaban edisi-asli yang ditampilkan bertahap.`,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
overrides.educator_evidence.D70 = {
  status: 'verified',
  verified_date: '2026-09-05',
  locator: url,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: [
    'prerequisite_diagnostics',
    'lesson_sequences',
    'exercise_bank',
    'staged_hints_answers_solutions',
    'assessment_blueprints',
    'solution_provenance',
    'remix_selectors',
    'accessibility_accommodations',
  ],
  resources,
};

await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);
console.log(JSON.stringify({
  state: 'pass',
  admitted_roles: ['D70'],
  contract: manifest.contract,
  public_release_verified: false,
  native_full_roundtrip_verified: false,
}));
