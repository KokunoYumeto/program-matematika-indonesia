import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/d30-capability-v1';
const apply = process.argv.includes('--apply');
const load = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const identity = async path => {
  const bytes = await readFile(resolve(root, path));
  return {path, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')};
};

const manifest = await load(`${base}/manifest.json`);
const validation = await load(`${base}/validation.json`);
const capabilities = await load(`${base}/data/capabilities.json`);
assert.equal(manifest.course_id, 'D30');
assert.equal(manifest.contract, 'course-learning-capability/1');
assert.equal(manifest.zero_copy_native_bodies, true);
assert.equal(manifest.native_bodies_copied, false);
assert.equal(manifest.zero_copy, true);
assert.equal(manifest.component_rights_preserved, true);
assert.equal(manifest.public_state_changed, false);
assert.equal(validation.result, 'PASS');
assert.ok(Object.values(validation.checks).every(Boolean));
assert.equal(capabilities.scope.mastery_problems, 36);
assert.equal(capabilities.scope.assessment_forms, 2);
for (const row of manifest.outputs) {
  const observed = await identity(`${base}/${row.path}`);
  assert.equal(observed.bytes, row.bytes);
  assert.equal(observed.sha256, row.sha256);
}

if (!apply) {
  console.log(JSON.stringify({state: 'pass', mode: 'check-only', course_id: 'D30', contract: manifest.contract, writes: false}));
  process.exit(0);
}

const publicMappings = [
  [`${base}/views/D30.html`, 'docs/backend/d30/D30.html'],
  [`${base}/views/D30-pengajar.html`, 'docs/backend/d30/D30-pengajar.html'],
  [`${base}/data/capabilities.json`, 'docs/backend/d30/capabilities.json'],
  [`${base}/data/learning-map.json`, 'docs/backend/d30/learning-map.json'],
  [`${base}/data/learner-map.json`, 'docs/backend/d30/learner-map.json'],
  [`${base}/data/educator-map.json`, 'docs/backend/d30/educator-map.json'],
  [`${base}/data/public-evidence.json`, 'docs/backend/d30/public-evidence.json'],
  [`${base}/data/claim-boundary.json`, 'docs/backend/d30/claim-boundary.json'],
  [`${base}/data/rights-index.jsonl`, 'docs/backend/d30/data/rights-index.jsonl'],
  [`${base}/data/corrections-index.jsonl`, 'docs/backend/d30/data/corrections-index.jsonl'],
  [`${base}/data/terms-index.jsonl`, 'docs/backend/d30/data/terms-index.jsonl'],
  [`${base}/data/relations-index.jsonl`, 'docs/backend/d30/data/relations-index.jsonl'],
  [`${base}/validation.json`, 'docs/backend/d30/validation.json'],
];
for (const [source, target] of publicMappings) {
  const bytes = await readFile(resolve(root, source));
  await mkdir(dirname(resolve(root, target)), {recursive: true});
  await writeFile(resolve(root, target), bytes);
}

const evidence = [];
for (const [kind, path] of [
  ['central_adapter_manifest', `${base}/manifest.json`],
  ['deterministic_validation_receipt', `${base}/validation.json`],
  ['native_metadata_intake', `${base}/input/source-lock.json`],
  ['verified_native_public_release', `${base}/data/public-evidence.json`],
]) {
  const row = await identity(path);
  evidence.push({kind, locator: path, bytes: row.bytes, sha256: row.sha256, verified_date: '2026-09-06'});
}

const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target);
assert.ok(!overrides.semantic_adapters.D30?.contract_version || overrides.semantic_adapters.D30.contract_version === manifest.contract, 'Preserve a different admitted D30 contract');
overrides.semantic_adapters.D30 = {
  status: 'verified',
  contract_version: manifest.contract,
  mapping_scope: 'zero_copy_projection_of_2538_entities_6333_segments_3256_relations_57_high_level_surfaces_5_labs_36_solved_mastery_problems_and_2_equivalent_assessments',
  evidence,
};

overrides.native_capabilities.D30 = {...overrides.native_capabilities.D30};
for (const capability of ['unit_identity', 'translation_ledger', 'terminology', 'translation_rights', 'corrections', 'educator_unit_alignment', 'build', 'deterministic_replay']) {
  overrides.native_capabilities.D30[capability] = {status: 'verified', evidence};
}

const limitations = capabilities.accessibility;
const learnerPage = await identity('docs/backend/d30/D30.html');
const learnerResource = await identity('docs/backend/d30/learning-map.json');
const learnerEvidence = await identity('docs/backend/d30/validation.json');
const tool = {
  tool_id: 'd30.open_learner_hub',
  label: 'D30 · Probabilitas Teoretis-Ukuran dan Proses Stokastik',
  href: 'backend/d30/D30.html',
  action_kind: 'course_reader',
  scope: '57 permukaan tingkat-atas, lima laboratorium, 36 masalah penguasaan terpecahkan, dan dua formulir penilaian ekuivalen.',
  state: 'verified', primary: false, machine_data_is_learner_destination: false,
  page: learnerPage, resource: learnerResource, evidence: learnerEvidence,
  limitations: [
    'Adapter hanya memuat metadata dan tautan zero-copy; isi tetap berada di pembaca native publik.',
    'Hak campuran dipertahankan per komponen tanpa lisensi payung.',
    'Prasyarat O006/C140 ditautkan tanpa menyalin byte lintas jalur.',
    `Tidak ada klaim WCAG, uji teknologi bantu, atau PDF bertag: ${JSON.stringify(limitations)}.`,
  ],
};
assert.ok(!overrides.learner_tools.D30 || overrides.learner_tools.D30.every(old => old.tool_id === tool.tool_id), 'Preserve unrelated D30 tools');
overrides.learner_tools.D30 = [tool];

const teacher = await identity('docs/backend/d30/D30-pengajar.html');
const oldEducator = overrides.educator_evidence.D30;
const managedResourceIds = new Set([
  'D30:educator-hub-v1',
  'D30:educator-map-v1',
  'D30:terms-index-v1',
  'D30:rights-index-v1',
  'D30:corrections-index-v1',
  'D30:relations-index-v1',
]);
const resources = (oldEducator?.resources ?? []).filter(resource => !managedResourceIds.has(resource.id));
if (!resources.some(resource => resource.id === 'D30:native-educator-observation')) {
  resources.unshift({
    id: 'D30:native-educator-observation',
    title: 'Observasi pengajar pada rilis native D30',
    resource_type: 'teacher-guide',
    status: oldEducator?.status ?? 'available_unverified',
    url: oldEducator?.locator ?? 'https://zenodo.org/records/22182655',
    scope: 'Bukti pengajar historis pada rilis native dipertahankan sebagai sumber tambahan; lapisan pusat tidak menghapus atau menggantikannya.',
  });
}
resources.push({
  id: 'D30:educator-hub-v1', title: 'Peta hak, relasi, asesmen, laboratorium, dan provenans D30',
  resource_type: 'teacher-guide', status: 'verified',
  url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d30/D30-pengajar.html',
  scope: tool.scope, bytes: teacher.bytes, sha256: teacher.sha256,
});
for (const [id, title, relative, resourceType] of [
  ['D30:educator-map-v1', 'Peta mesin pengajar D30', 'educator-map.json', 'teacher-guide'],
  ['D30:terms-index-v1', 'Indeks istilah D30', 'data/terms-index.jsonl', 'terminology-index'],
  ['D30:rights-index-v1', 'Indeks hak komponen D30', 'data/rights-index.jsonl', 'rights-index'],
  ['D30:corrections-index-v1', 'Indeks koreksi D30', 'data/corrections-index.jsonl', 'corrections-index'],
  ['D30:relations-index-v1', 'Indeks relasi native D30', 'data/relations-index.jsonl', 'relations-index'],
]) {
  const mapped = await identity(`docs/backend/d30/${relative}`);
  resources.push({
    id, title, resource_type: resourceType, status: 'verified',
    url: `https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d30/${relative}`,
    scope: 'Proyeksi metadata zero-copy yang terikat pada sumber native checkpoint 38.',
    bytes: mapped.bytes, sha256: mapped.sha256,
  });
}
overrides.educator_evidence.D30 = {
  status: 'verified', verified_date: '2026-09-06',
  locator: 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d30/D30-pengajar.html',
  bytes: teacher.bytes, sha256: teacher.sha256,
  features: [...new Set([
    ...(oldEducator?.features ?? []),
    'prerequisite_diagnostics', 'lesson_sequences', 'exercise_bank',
    'staged_hints_answers_solutions', 'assessment_blueprints',
    'solution_provenance', 'remix_selectors',
    'accessibility_accommodations',
  ])].sort(),
  resources,
};

await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);
console.log(JSON.stringify({state: 'pass', mode: 'apply', admitted_roles: ['D30'], contract: manifest.contract}));
