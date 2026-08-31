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
  { name: 'unindexed_is_not_proof_of_nonproduction', id: 'B10', status: 'not_yet_produced', error: /educator status must preserve authority or honest indexing uncertainty/ },
  { name: 'explicit_in_progress_authority_is_preserved', id: 'C140', status: 'available_unverified', error: /educator status must preserve authority or honest indexing uncertainty/ },
  { name: 'invalid_capsule_status_cannot_escape_schema', id: 'B10', status: 'invented_status', error: /JSON Schema validation failed/ },
];
try {
  for (const test of tests) {
    const mutationRoot = join(root, test.name);
    const generated = join(mutationRoot, 'generated');
    await mkdir(generated, { recursive: true });
    const rows = structuredClone(original);
    rows.find((row) => row.course_id === test.id).layers.educator.status = test.status;
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
