import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const canonical = resolve(project, 'backend/course-capsule-v1');
const original = JSON.parse(await readFile(join(canonical, 'generated/course-capsules.json'), 'utf8'));
const manifest = await readFile(join(canonical, 'generated/manifest.json'));
const tempParent = resolve(tmpdir());
const root = await mkdtemp(join(tempParent, 'capsule-educator-mutation-'));
assert.ok(root.startsWith(tempParent + sep));
const sort = (value) => Array.isArray(value) ? value.map(sort)
  : value && typeof value === 'object'
    ? Object.fromEntries(Object.keys(value).sort().map((key) => [key, sort(value[key])])) : value;
const tests = [
  { name: 'b80_educator_resource_cannot_be_removed', id: 'B80', mutate: row=>{row.layers.educator.resources=[];}, error: /missing\/duplicate educator resource/ },
  { name: 'b80_educator_hash_cannot_drift', id: 'B80', mutate: row=>{row.layers.educator.resources[0].sha256='0'.repeat(64);}, error: /educator resource evidence drift/ },
  { name: 'c100_geometry_educator_resource_cannot_be_removed', id: 'C100', mutate: row=>{row.layers.educator.resources=row.layers.educator.resources.filter(resource=>resource.id!=='C100:geometry-educator-v1');}, error: /missing\/duplicate educator resource/ },
  { name: 'c100_geometry_educator_hash_cannot_drift', id: 'C100', mutate: row=>{row.layers.educator.resources.find(resource=>resource.id==='C100:geometry-educator-v1').sha256='0'.repeat(64);}, error: /educator resource evidence drift/ },
  { name: 'c90_topology_educator_resource_cannot_be_removed', id: 'C90', mutate: row=>{row.layers.educator.resources=row.layers.educator.resources.filter(resource=>resource.id!=='C90:topology-educator-v1');}, error: /missing\/duplicate educator resource/ },
  { name: 'c90_topology_educator_hash_cannot_drift', id: 'C90', mutate: row=>{row.layers.educator.resources.find(resource=>resource.id==='C90:topology-educator-v1').sha256='0'.repeat(64);}, error: /educator resource evidence drift/ },
  { name: 'd40_educator_resource_cannot_be_removed', id: 'D40', mutate: row=>{row.layers.educator.resources=row.layers.educator.resources.filter(resource=>resource.id!=='D40:educator-hub-v1');}, error: /missing\/duplicate educator resource/ },
  { name: 'd40_educator_hash_cannot_drift', id: 'D40', mutate: row=>{row.layers.educator.resources.find(resource=>resource.id==='D40:educator-hub-v1').sha256='0'.repeat(64);}, error: /educator resource evidence drift/ },
  { name: 'd40_educator_alignment_cannot_drift', id: 'D40', mutate: row=>{row.layers.educator.unit_alignment_status='unknown';}, error: /native status needs capability-specific evidence/ },
  { name: 'd40_static_mathml_cannot_be_downgraded', id: 'D40', mutate: row=>{row.layers.learner.capabilities.mathml='available_unverified';}, error: /learner capability authority drift/ },
  { name: 'd80_educator_resource_cannot_be_removed', id: 'D80', mutate: row=>{row.layers.educator.resources=row.layers.educator.resources.filter(resource=>resource.id!=='D80:educator-hub-v1');}, error: /missing\/duplicate educator resource/ },
  { name: 'd80_educator_hash_cannot_drift', id: 'D80', mutate: row=>{row.layers.educator.resources.find(resource=>resource.id==='D80:educator-hub-v1').sha256='0'.repeat(64);}, error: /educator resource evidence drift/ },
  { name: 'd80_educator_alignment_cannot_drift', id: 'D80', mutate: row=>{row.layers.educator.unit_alignment_status='unknown';}, error: /native status needs capability-specific evidence/ },
  { name: 'd80_runtime_mathml_cannot_be_retyped_as_native_verified', id: 'D80', mutate: row=>{row.layers.learner.capabilities.mathml='verified';}, error: /learner capability authority drift/ },
  { name: 'unindexed_is_not_proof_of_nonproduction', id: 'B10', status: 'not_yet_produced', error: /educator status must preserve authority or honest indexing uncertainty/ },
  { name: 'explicit_in_progress_authority_is_preserved', id: 'C140', status: 'available_unverified', error: /educator status must preserve authority or honest indexing uncertainty/ },
  { name: 'invalid_capsule_status_cannot_escape_schema', id: 'B10', status: 'invented_status', error: /JSON Schema validation failed/ },
  ...[
    ['curriculum', 'unit_identity_status'],
    ['translation', 'ledger_status'],
    ['production', 'deterministic_replay_status'],
    ['educator', 'unit_alignment_status'],
  ].map(([layer, key]) => ({ name: `adapter_cannot_verify_native_${key}`, id: 'B10', mutate: (row) => { row.layers[layer][key] = 'verified'; }, error: /native status needs capability-specific evidence/ })),
  { name: 'learner_url_must_match_authority', id: 'B10', mutate: (row) => { row.layers.learner.primary.url = 'https://example.org/wrong-edition/'; }, error: /learner delivery authority drift/ },
  { name: 'aggregate_learner_status_must_match_authority', id: 'B10', mutate: (row) => { row.layers.learner.status = 'unknown'; }, error: /aggregate learner authority drift/ },
  { name: 'learner_capability_must_match_authority', id: 'B10', mutate: (row) => { row.layers.learner.capabilities.semantic_html = 'unknown'; }, error: /learner capability authority drift/ },
  { name: 'component_rights_cannot_be_omitted', id: 'B10', mutate: (row) => { delete row.layers.federation.components[0].rights_status; }, error: /component rights uncertainty missing or overstated/ },
  { name: 'component_provenance_cannot_be_omitted', id: 'B10', mutate: (row) => { row.layers.federation.components[0].provenance = []; }, error: /component provenance reference drift/ },
  { name: 'native_package_reference_must_match_evidence', id: 'B30', mutate: (row) => { row.layers.federation.components.find((component) => component.id === 'B30:clp-native-source-and-modular-backend').sha256 = '0'.repeat(64); }, error: /native package reference drift/ },
];
try {
  for (const test of tests) {
    const mutationRoot = join(root, test.name);
    const generated = join(mutationRoot, 'generated');
    await mkdir(generated, { recursive: true });
    const rows = structuredClone(original);
    const row = rows.find((row) => row.course_id === test.id);
    if (test.mutate) test.mutate(row);
    else row.layers.educator.status = test.status;
    await writeFile(join(generated, 'course-capsules.jsonl'), rows.map((row) => JSON.stringify(sort(row))).join('\n') + '\n');
    await writeFile(join(generated, 'course-capsules.json'), JSON.stringify(sort(rows), null, 2) + '\n');
    await writeFile(join(generated, 'manifest.json'), manifest);
    const result = spawnSync(process.execPath, [join(project, 'scripts/validate-course-capsules-v1.mjs'), '--output-root=' + mutationRoot, '--peer-output-root=' + canonical], { cwd: project, encoding: 'utf8' });
    assert.notEqual(result.status, 0, `${test.name}: invalid claim was accepted`);
    assert.match(result.stderr + result.stdout, test.error, `${test.name}: must fail for semantic/schema truth, not an unrelated missing file or hash`);
  }
  console.log(JSON.stringify({ state: 'pass', rejected_mutations: tests.map(({ name }) => name), canonical_files_modified: false }, null, 2));
} finally {
  assert.ok(root.startsWith(tempParent + sep));
  await rm(root, { recursive: true, force: true });
}
