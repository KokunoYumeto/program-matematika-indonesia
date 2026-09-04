import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/d40-capability-v1';
const load = async (path) => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const identity = async (path) => {
  const data = await readFile(resolve(root, path));
  return {path, bytes: data.length, sha256: createHash('sha256').update(data).digest('hex')};
};

const manifest = await load(`${base}/manifest.json`);
const validation = await load(`${base}/validation.json`);
const sourceLock = await load(`${base}/input/source-lock.json`);
assert.equal(manifest.course_id, 'D40');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.contract_2_3_1_conformance, 'not_claimed');
assert.equal(validation.state, 'pass');
assert.equal(validation.contract, manifest.contract);
assert.equal(validation.manifest_sha256, (await identity(`${base}/manifest.json`)).sha256);
assert.equal(validation.input_hashes_verified, 27);
assert.equal(validation.locked_input_identities_bound, 29);
assert.equal(validation.identity_only_public_artifacts, 2);
assert.equal(validation.mastery_primary_roots, 68);
assert.equal(validation.practice_problems, 48);
assert.equal(validation.assessment_items, 16);
assert.equal(validation.computational_labs, 4);
assert.equal(validation.prerequisite_relations, 108);
assert.equal(validation.dionne_imported_objects, 3920);
assert.equal(validation.rights_records, 5);
assert.equal(validation.execution.executed_notebooks, 4);
assert.equal(validation.execution.execution_surfaces, 8);
assert.equal(validation.execution.required_cells, 116);
assert.equal(validation.learner_educator_shared_identity, true);
assert.equal(validation.native_bodies_copied, false);
assert.equal(validation.archive_members_linked_as_urls, false);
assert.equal(validation.isolated_two_build_byte_identity.byte_identical, true);
assert.equal(validation.public_state_changed, false);
assert.equal(validation.accessibility.offline_html_availability, 'public_zip_member_only');
assert.equal(validation.accessibility.pdf_tagged_status, 'unknown_not_evidenced');
assert.equal(sourceLock.public_release.record_id, 22184259);
assert.equal(sourceLock.public_release.access, 'open');
assert.equal(sourceLock.public_release.concept_doi, '10.5281/zenodo.22059503');
assert.equal(manifest.inputs.length, 29);
assert.deepEqual(manifest.inputs, sourceLock.inputs);
for (const item of manifest.outputs) {
  assert.deepEqual(
    await identity(`${base}/${item.path}`),
    {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256},
  );
}

const publicMappings = [
  [`${base}/views/D40.html`, 'docs/backend/d40/D40.html'],
  [`${base}/views/D40-pengajar.html`, 'docs/backend/d40/D40-pengajar.html'],
  [`${base}/data/learning-map.json`, 'docs/backend/d40/learning-map.json'],
  [`${base}/validation.json`, 'docs/backend/d40/validation.json'],
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
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-04'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
const lockedReleaseManifest = sourceLock.inputs.find((row) => row.role === 'release_manifest');
assert.ok(lockedReleaseManifest, 'D40 release manifest is missing from the source lock');
const nativeSemanticEvidence = {
  kind: 'course_native_release_manifest',
  locator: 'https://zenodo.org/records/22184259/files/RELEASE_MANIFEST.json?download=1',
  verified_date: '2026-08-31',
  file_name: 'RELEASE_MANIFEST.json',
  bytes: lockedReleaseManifest.bytes,
  sha256: lockedReleaseManifest.sha256,
  note: 'Dua backend semantik kursus tersedia dan terikat pada rilis native; adapter pusat yang baru tetap merupakan proyeksi metadata tanpa salinan badan.',
};
assert.ok(
  !overrides.semantic_adapters.D40
    || !overrides.semantic_adapters.D40.contract_version
    || overrides.semantic_adapters.D40.contract_version === manifest.contract,
  'Preserve a different admitted D40 contract',
);
overrides.semantic_adapters.D40 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_68_root_pde_mastery_projection_with_14_theory_chapters_130_many_to_many_supports_108_prerequisites_and_execution_evidence',
  evidence: [nativeSemanticEvidence, ...evidence],
};

overrides.native_capabilities.D40 = {...overrides.native_capabilities.D40};
for (const capability of [
  'unit_identity',
  'translation_ledger',
  'terminology',
  'translation_rights',
  'corrections',
  'build',
  'deterministic_replay',
  'educator_unit_alignment',
]) {
  overrides.native_capabilities.D40[capability] = {status: 'verified', evidence};
}

const scope = '68 akar pembelajaran native: 48 latihan, 16 asesmen, dan 4 laboratorium; 14 bab teori, 130 relasi dukungan many-to-many, 108 prasyarat, dan bukti 4 notebook tereksekusi.';
const limitations = [
  'Isi pembelajaran berbahasa Indonesia; antarmuka Inggris tidak menerjemahkan isi.',
  'HTML semantik lengkap berada di dalam ZIP publik, bukan pada URL per-unit; halaman ini mengarahkan ke arsip dan mempertahankan lokasi anggota.',
  'Adapter hanya memproyeksikan metadata dan identitas native; badan teori, soal, solusi, kode, dan notebook tidak disalin.',
  'Relasi latihan ke 14 bab teori tetap many-to-many; tidak ada penetapan satu bab yang direka.',
  'Hak tetap per komponen/per rekaman tanpa lisensi payung; rekaman runtime/cache/log tidak dilisensikan ulang.',
  'HTML memiliki bukti MathML statis dan nol dependensi jaringan; tagging PDF, WCAG, dan uji pengguna teknologi bantu tidak diklaim.',
  'Satu koreksi pembaca Ivrii opsional tetap antre dan tidak menghalangi komposit D40 yang diwajibkan.',
];
const tool = {
  tool_id: 'd40.open_learner_hub',
  label: 'D40 · Persamaan Diferensial Parsial',
  href: 'backend/d40/D40.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/d40/D40.html'),
  resource: await identity('docs/backend/d40/learning-map.json'),
  evidence: await identity('docs/backend/d40/validation.json'),
  limitations,
};
assert.ok(
  !overrides.learner_tools.D40
    || overrides.learner_tools.D40.every((old) => old.tool_id === tool.tool_id),
  'Preserve unrelated D40 tools',
);
overrides.learner_tools.D40 = [tool];

const old = overrides.educator_evidence.D40;
const teacher = await identity('docs/backend/d40/D40-pengajar.html');
const url = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d40/D40-pengajar.html';
const resources = (old?.resources ?? []).filter(
  (resource) => !['D40:native-educator-observation', 'D40:educator-hub-v1'].includes(resource.id),
);
resources.push({
  id: 'D40:native-educator-observation',
  title: 'Materi pendukung native persamaan diferensial parsial',
  resource_type: 'teacher-guide',
  status: 'available_unverified',
  url: 'https://zenodo.org/records/22184259',
  scope: 'Observasi historis pada rilis native; status fitur lama tetap belum diverifikasi oleh lapisan pusat.',
});
resources.push({
  id: 'D40:educator-hub-v1',
  title: 'Peta teori, mastery, asesmen, laboratorium, eksekusi, hak, dan provenans D40 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url,
  scope,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
overrides.educator_evidence.D40 = {
  status: 'verified',
  verified_date: '2026-09-04',
  locator: url,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: [
    'lesson_sequences',
    'exercise_bank',
    'staged_hints_answers_solutions',
    'assessment_blueprints',
    'activities_labs',
    'solution_provenance',
    'accessibility_accommodations',
  ],
  resources,
};

await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);
console.log(JSON.stringify({state: 'pass', admitted_roles: ['D40'], contract: manifest.contract, public_release_verified: false}));
