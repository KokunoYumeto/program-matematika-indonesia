import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/adapters/topology-capability-v1';
const load = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const identity = async path => {
  const data = await readFile(resolve(root, path));
  return {path, bytes: data.length, sha256: createHash('sha256').update(data).digest('hex')};
};
const manifest = await load(`${base}/manifest.json`);
const validation = await load(`${base}/validation.json`);
assert.equal(validation.state, 'pass');
assert.equal(validation.manifest_sha256, (await identity(`${base}/manifest.json`)).sha256);
for (const key of [
  'schema_validation', 'complete_native_projection_equality',
  'all_4908_native_destinations_byte_bound', 'native_pending_states_preserved',
  'learner_teacher_shared_identity', 'isolated_two_build_byte_identity',
  'reader_bytes_zero_copy',
]) assert.equal(validation[key], true, key);
for (const item of [...manifest.inputs, ...manifest.outputs]) assert.deepEqual(await identity(item.path), item);

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
assert.ok(!overrides.semantic_adapters.C90 || overrides.semantic_adapters.C90.contract_version === manifest.contract);
overrides.semantic_adapters.C90 = {
  status: 'verified', contract_version: manifest.contract,
  mapping_scope: 'complete_native_chapter_companion_completion_and_staged_support_metadata_with_zero_copy_reader_destinations_and_preserved_pending_states',
  evidence,
};
overrides.native_capabilities.C90 = {
  ...overrides.native_capabilities.C90,
  unit_identity: {status: 'verified', evidence},
  educator_unit_alignment: {status: 'verified', evidence},
  terminology: {status: 'verified', evidence},
};

const scope = '1.227 rekaman/4.908 tujuan; 20 bab + 8 modul.';
const tools = [];
for (const [suffix, label, filename, actionKind] of [
  ['course-map', 'C90', 'C90.html', 'reference'],
]) {
  tools.push({
    tool_id: `c90-topology-${suffix}-v1`, label,
    href: `backend/topology/${filename}`, action_kind: actionKind, scope,
    state: 'verified', primary: false, machine_data_is_learner_destination: false,
    page: await identity(`docs/backend/topology/${filename}`),
    resource: await identity('docs/backend/topology/learning-map.json'),
    evidence: await identity('docs/backend/topology/validation.json'),
    limitations: ['Isi Indonesia; status asli tampak.'],
  });
}
assert.ok(!overrides.learner_tools.C90 || overrides.learner_tools.C90.every(old => old.tool_id.startsWith('c90-topology-')), 'Preserve unrelated tools');
overrides.learner_tools.C90 = tools;

const old = overrides.educator_evidence.C90;
const teacher = await identity('docs/backend/topology/pengajar.html');
const url = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/topology/pengajar.html';
const resources = (old?.resources ?? []).filter(resource => resource.id !== 'C90:topology-educator-v1');
if (old?.locator && !resources.some(resource => resource.id === 'C90:native-reader-observation')) {
  resources.push({id: 'C90:native-reader-observation', title: 'Pembaca dan dukungan native topologi', resource_type: 'teacher-guide', status: old.status ?? 'available_unverified', url: old.locator, scope: 'Permukaan native yang mendasari adapter; status historis dipertahankan.'});
}
resources.push({id: 'C90:topology-educator-v1', title: 'Penyusun paket kegiatan topologi', resource_type: 'teacher-guide', status: 'verified', url, scope, bytes: teacher.bytes, sha256: teacher.sha256});
overrides.educator_evidence.C90 = {status: 'verified', verified_date: '2026-09-04', locator: url, bytes: teacher.bytes, sha256: teacher.sha256, features: ['exercise_bank', 'staged_hints_answers_solutions', 'prerequisite_diagnostics', 'solution_provenance'], resources};

await writeFile(resolve(root, target), `${JSON.stringify(overrides, null, 2)}\n`);
console.log(JSON.stringify({state: 'pass', admitted_roles: ['C90'], contract: manifest.contract, public_release_verified: false}));
