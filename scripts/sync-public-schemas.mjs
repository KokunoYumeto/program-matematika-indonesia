import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const mappings = [
  ['schemas/catalog-v1.schema.json', 'docs/schema/v1/program-matematika-indonesia-catalog-v1.schema.json'],
  ['schemas/backend-v1.schema.json', 'docs/schema/v1/interlanguage-math-backend-v1.schema.json'],
  ['schemas/backend-migration-receipt-v1.schema.json', 'docs/schema/v1/interlanguage-backend-migration-receipt-v1.schema.json'],
  ['schemas/profiles/source-format-profile-v1.schema.json', 'docs/schema/v1/interlanguage-source-format-profile-v1.schema.json'],
  ['schemas/v1/curriculum-authority-v1.schema.json', 'docs/schema/v1/curriculum-authority-v1.schema.json'],
  ['schemas/v1/learner-read-model-v1.schema.json', 'docs/schema/v1/learner-read-model-v1.schema.json'],
  ['schemas/v2/backend-migration-receipt-v2.schema.json', 'docs/schema/v2/backend-migration-receipt-v2.schema.json'],
  ['schemas/v2/federation-package-v2.schema.json', 'docs/schema/v2/federation-package-v2.schema.json'],
  ['schemas/v2/federation-record-v2.schema.json', 'docs/schema/v2/federation-record-v2.schema.json'],
  ['schemas/v2/namespace-v2.json', 'docs/schema/v2/namespace-v2.json'],
  ['schemas/v2/pmi-release-policy-v2.json', 'docs/schema/v2/pmi-release-policy-v2.json'],
];

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const results = [];
for (const [sourceRelative, targetRelative] of mappings) {
  const source = resolve(project, sourceRelative);
  const target = resolve(project, targetRelative);
  const bytes = await readFile(source);
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, bytes);
  const written = await readFile(target);
  assert.deepEqual(written, bytes, `${targetRelative}: public schema copy differs.`);
  results.push({ path: targetRelative, bytes: bytes.length, sha256: sha256(bytes) });
}

console.log(JSON.stringify({ status: 'pass', schema_count: results.length, files: results }, null, 2));
