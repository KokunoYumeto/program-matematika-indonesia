import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, resolve, basename } from 'node:path';
import { homedir } from 'node:os';
import { fileURLToPath } from 'node:url';

// One bounded evidence intake. Normal builds use the resulting local inputs,
// never the external manager workspace or a live producer task.
const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const source = resolve(project, '../../../outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook');
const target = resolve(project, 'backend/course-capsule-v1/validation/manager-followthrough');
const digest = (bytes) => createHash('sha256').update(bytes).digest('hex');
const handoffBytes = await readFile(resolve(source, 'GLOBAL_BACKEND_FOLLOWTHROUGH_HANDOFF_20260831.json'));
assert.equal(digest(handoffBytes), 'fcfe50fde0b79d96af23277f154265fb38af008a864137c80703afd57ed4f98f');
const handoff = JSON.parse(handoffBytes);
const files = new Map();
for (const fact of handoff.files) {
  assert.equal(basename(fact.name), fact.name);
  const bytes = await readFile(resolve(source, fact.name));
  assert.equal(bytes.length, fact.bytes, `${fact.name}: evidence size changed`);
  assert.equal(digest(bytes), fact.sha256, `${fact.name}: evidence hash changed`);
  files.set(fact.name, bytes);
}
const selected = [
  'B10_PUBLIC_NATIVE_BACKEND_EVIDENCE_20260831.json',
  'B10_NATIVE_PUBLIC_INTEGRATION_PATCH_20260831.json',
  'ADAPTER_CAPABILITY_METADATA_CORRECTIONS_20260831.json',
  'NATIVE_FAMILY_PUBLIC_EVIDENCE_INDEX_V06213_20260831.json',
  'NATIVE_FAMILY_PUBLIC_EVIDENCE_NOTE_V06213_20260831.md',
  'OWNER_PUBLICATION_DELTA_A30_B95_20260831.json',
  'OWNER_PUBLICATION_DELTA_ROOT_RECHECK_20260831.json',
];
const excludedProfile = basename(homedir()).toLowerCase();
await mkdir(target, { recursive: true });
for (const name of selected) {
  const bytes = files.get(name);
  const text = bytes.toString('utf8');
  assert.ok(!new RegExp(`\\b${excludedProfile.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i').test(text), `${name}: private profile name`);
  assert.doesNotMatch(text, /[A-Za-z]:[\\/]+Users[\\/]|\bghp_[A-Za-z0-9]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b/);
  await writeFile(resolve(target, name), bytes);
}
const patch = JSON.parse(files.get('B10_NATIVE_PUBLIC_INTEGRATION_PATCH_20260831.json'));
const ledgerPath = resolve(project, 'backend/course-capsule-v1/authority/native-package-references-v1.json');
const ledger = JSON.parse(await readFile(ledgerPath, 'utf8'));
const operation = {
  course_id: 'B10', operation: 'append_component_reference', base_component: null,
  expected_component: patch.operation.expected_generated_component,
  artifact_role: 'native_backend_package', artifact_bytes: patch.evidence.package.bytes,
  artifact_sha256: patch.evidence.package.sha256,
  evidence_file: 'manager-followthrough/' + patch.evidence.receipt,
  evidence_sha256: patch.evidence.sha256, evidence_bytes: patch.evidence.bytes,
  evidence_package_pointer: '/public_asset',
};
const prior = ledger.operations.find((row) => row.expected_component.id === operation.expected_component.id);
if (prior) assert.deepEqual(prior, operation, 'B10 package operation collision');
else ledger.operations.push(operation);
await writeFile(ledgerPath, JSON.stringify(ledger, null, 2) + '\n');
console.log(JSON.stringify({state:'pass',bound_input_files:handoff.files.length,preserved_evidence_files:selected.length,native_reference_operations:ledger.operations.length}));
