import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadC120Delivery,validateC120Delivery,validateC120DeliveryOverride} from './c120-delivery-evidence-v1.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const evidence = await loadC120Delivery(root);
const cases = [
  ['unfinished_readback', d => {d.values[2].state = 'in_progress';}],
  ['missing_file', d => {d.values[2].files.pop();}],
  ['duplicate_file', d => {d.values[2].files[1] = d.values[2].files[0];}],
  ['wrong_public_hash', d => {d.values[2].files.find(r => r.path === 'index.html').sha256 = '0'.repeat(64);}],
  ['wrong_git_blob', d => {d.values[2].files[0].git_blob = '0'.repeat(40);}],
  ['missing_unit', d => {d.values[3].unit_ids.pop();}],
  ['math_loss', d => {d.values[3].mathml_count -= 1;}],
  ['main_content_drift', d => {d.values[3].html_comparisons[0].main_dom_equal = false;}],
  ['missing_reseal', d => {d.values[5].transformations.pop();}],
  ['wrong_native_script', d => {d.deployment['scripts/program_navigation.py'] = Buffer.from('changed');}],
  ['network_runtime_dependency', d => {d.values[3].external_runtime_resources.push({url: 'https://example.invalid/math.js'});}],
  ['missing_print_profile', d => {d.values[3].print_css_paths.pop();}],
];
for (const [name, change] of cases) {
  const data = {values: structuredClone(evidence.data.values), bytes: evidence.data.bytes, deployment: {...evidence.data.deployment}};
  change(data);
  assert.throws(() => validateC120Delivery(data), undefined, name);
}
const overrides = JSON.parse(await readFile(resolve(root, 'backend/authority/learner-delivery-overrides-v1.json')));
validateC120DeliveryOverride(overrides.courses.C120, evidence);
for (const key of ['epub', 'portable_html']) {
  const row = structuredClone(overrides.courses.C120);
  row[key] = {status: 'verified'};
  assert.throws(() => validateC120DeliveryOverride(row, evidence), undefined, key);
}
const wrong = structuredClone(overrides.courses.C120);
wrong.primary.sha256 = '0'.repeat(64);
assert.throws(() => validateC120DeliveryOverride(wrong, evidence));
console.log(JSON.stringify({state: 'pass', public_files: evidence.files.size, units: 26, evidence_negatives: cases.length, admission_negatives: 3}));
