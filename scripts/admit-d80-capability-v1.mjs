import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/d80-capability-v1';
const load = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const identity = async path => {
  const data = await readFile(resolve(root, path));
  return {path, bytes: data.length, sha256: createHash('sha256').update(data).digest('hex')};
};

const manifest = await load(`${base}/manifest.json`);
const validation = await load(`${base}/validation.json`);
assert.equal(manifest.course_id, 'D80');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(validation.state, 'pass');
assert.equal(validation.contract, manifest.contract);
assert.equal(validation.manifest_sha256, (await identity(`${base}/manifest.json`)).sha256);
assert.equal(validation.translation_targets_verified, 146);
assert.equal(validation.independent_mastery_bridges, 2);
assert.equal(validation.mastery_fragments_verified, 32);
assert.equal(validation.superseded_checkpoint_target_hashes_preserved, 50);
assert.equal(validation.malformed_superseded_checkpoint_hashes_preserved, 1);
assert.equal(validation.native_mathml_claimed, false);
assert.equal(validation.learner_educator_shared_identity, true);
assert.equal(validation.isolated_two_build_byte_identity.byte_identical, true);
for (const item of manifest.outputs) assert.deepEqual(await identity(`${base}/${item.path}`), {path: `${base}/${item.path}`, bytes: item.bytes, sha256: item.sha256});

const publicMappings = [
  [`${base}/views/D80.html`, 'docs/backend/d80/D80.html'],
  [`${base}/views/D80-pengajar.html`, 'docs/backend/d80/D80-pengajar.html'],
  [`${base}/data/learning-map.json`, 'docs/backend/d80/learning-map.json'],
  [`${base}/validation.json`, 'docs/backend/d80/validation.json'],
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
  ['native_metadata_intake', `${base}/input/source-lock.json`],
]) {
  const {bytes, sha256} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256, verified_date: '2026-09-04'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
assert.ok(!overrides.semantic_adapters.D80 || overrides.semantic_adapters.D80.contract_version === manifest.contract);
overrides.semantic_adapters.D80 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'reconciled_146_unit_navigation_with_separate_independent_mastery_bridges_and_preserved_native_ledger_boundaries',
  evidence,
};
overrides.native_capabilities.D80 = {
  ...overrides.native_capabilities.D80,
  unit_identity: {status: 'verified', evidence},
  educator_unit_alignment: {status: 'verified', evidence},
};

const scope = '146 unit sumber + 2 jembatan mandiri; 148 rute dan 16 latihan/16 solusi jembatan dengan identitas bersama.';
const limitations = [
  'Isi berbahasa Indonesia; antarmuka Inggris tidak menerjemahkan isi.',
  'Unit sumber dan jembatan mandiri tetap dipisahkan; sumber memiliki 194 latihan dan 117 petunjuk, tetapi tidak menyediakan jawaban atau solusi.',
  'Pembaca memakai MathJax runtime; MathML native dan klaim WCAG tidak tersedia.',
  'Ledger native dirujuk tanpa disalin; 50 hash target checkpoint lama dan satu nilai malformed dipertahankan sebagai bukti historis.',
];
const tool = {
  tool_id: 'd80.open_learner_hub',
  label: 'D80 · Metode kategori dan homologi',
  href: 'backend/d80/D80.html',
  action_kind: 'course_reader',
  scope,
  state: 'verified',
  primary: false,
  machine_data_is_learner_destination: false,
  page: await identity('docs/backend/d80/D80.html'),
  resource: await identity('docs/backend/d80/learning-map.json'),
  evidence: await identity('docs/backend/d80/validation.json'),
  limitations,
};
assert.ok(!overrides.learner_tools.D80 || overrides.learner_tools.D80.every(old => old.tool_id === tool.tool_id), 'Preserve unrelated D80 tools');
overrides.learner_tools.D80 = [tool];

const old = overrides.educator_evidence.D80;
const teacher = await identity('docs/backend/d80/D80-pengajar.html');
const url = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d80/D80-pengajar.html';
const resources = (old?.resources ?? []).filter(resource => !['D80:native-educator-observation', 'D80:educator-hub-v1'].includes(resource.id));
if (old?.locator) resources.push({
  id: 'D80:native-educator-observation',
  title: 'Materi pendukung native metode aljabar',
  resource_type: 'teacher-guide',
  status: old.status ?? 'available_unverified',
  url: old.locator,
  scope: 'Observasi historis pada edisi native; status fitur lama tetap belum diverifikasi.',
});
resources.push({
  id: 'D80:educator-hub-v1',
  title: 'Keselarasan unit, provenans, latihan, dan solusi D80 untuk pengajar',
  resource_type: 'teacher-guide',
  status: 'verified',
  url,
  scope,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
});
overrides.educator_evidence.D80 = {
  status: 'verified',
  verified_date: '2026-09-04',
  locator: url,
  bytes: teacher.bytes,
  sha256: teacher.sha256,
  features: ['lesson_sequences', 'exercise_bank', 'staged_hints_answers_solutions', 'solution_provenance', 'accessibility_accommodations'],
  resources,
};

await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);
console.log(JSON.stringify({state: 'pass', admitted_roles: ['D80'], contract: manifest.contract, public_release_verified: false}));
