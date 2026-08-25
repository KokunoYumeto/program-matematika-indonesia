import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const seedRelative = 'releases/v0.53.0/program-matematika-indonesia-catalog-v0.53.0.json';
const recordsRelative = 'backend/v2/program-matematika-indonesia-federation-v0.2.0/records.jsonl';
const validationRelative = 'backend/v2/program-matematika-indonesia-federation-v0.2.0/validation_report.json';
const output = process.argv[2]
  ? resolve(project, process.argv[2])
  : resolve(project, 'backend/authority/history/curriculum-authority-v0.53.0.json');

assert.ok(output.startsWith(`${project}${sep}`), 'Authority output must remain inside the project.');

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const [seedBytes, recordsBytes, validationBytes] = await Promise.all([
  readFile(resolve(project, seedRelative)),
  readFile(resolve(project, recordsRelative)),
  readFile(resolve(project, validationRelative)),
]);

assert.equal(seedBytes.length, 47040, 'Unexpected v0.53 seed catalog byte count.');
assert.equal(
  sha256(seedBytes),
  'd7e6be9e0158ded1076106ce1cd10981a8e27a89e84606a6c245088d70250148',
  'Unexpected v0.53 seed catalog SHA-256.',
);
assert.equal(
  sha256(recordsBytes),
  'ee5766473f7c0f566788e363ea50fbb305ff8e037e9f73b39961be1359a817d0',
  'Unexpected federation records SHA-256.',
);
assert.equal(
  sha256(validationBytes),
  '10bc635c56c58c47de574471f8e8f875c31f98d12c25d9c83290a4365a898996',
  'Unexpected federation validation-report SHA-256.',
);

const catalog = JSON.parse(seedBytes.toString('utf8'));
const validation = JSON.parse(validationBytes.toString('utf8'));
assert.equal(validation.result, 'pass', 'The federation seed must be validated before authority is frozen.');
assert.equal(catalog.courses.length, 40, 'The authority seed must contain exactly 40 course roles.');

const authority = {
  schema_id: 'interlanguage/program-matematika-indonesia-curriculum-authority/v1',
  schema_version: '1.0.0',
  authority_state: 'frozen_seed_with_versioned_successors',
  authority_policy: {
    docs_courses_js_is_authority: false,
    owner_native_backends_remain_canonical: true,
    federation_is_reversible_projection: true,
    learner_site_is_generated_output: true,
  },
  seed_catalog: {
    path: seedRelative,
    bytes: seedBytes.length,
    sha256: sha256(seedBytes),
  },
  federation: {
    package_path: 'backend/v2/program-matematika-indonesia-federation-v0.2.0',
    records_path: recordsRelative,
    records_bytes: recordsBytes.length,
    records_sha256: sha256(recordsBytes),
    validation_report_path: validationRelative,
    validation_report_bytes: validationBytes.length,
    validation_report_sha256: sha256(validationBytes),
    validation_result: validation.result,
  },
  catalog,
};

await mkdir(dirname(output), { recursive: true });
await writeFile(output, `${JSON.stringify(authority, null, 2)}\n`, 'utf8');
console.log(`Immutable v0.53 curriculum-authority bootstrap seeded at ${output}`);
console.log(`bytes=${(await readFile(output)).length} sha256=${sha256(await readFile(output))}`);
