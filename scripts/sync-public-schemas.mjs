import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const mappings = [
  ['schemas/catalog-v1.schema.json', 'docs/schema/v1/program-matematika-indonesia-catalog-v1.schema.json'],
  ['schemas/educational-access-federation-v1.schema.json', 'docs/schema/educational-access-federation-v1.schema.json'],
  ['schemas/backend-v1.schema.json', 'docs/schema/v1/interlanguage-math-backend-v1.schema.json'],
  ['schemas/backend-migration-receipt-v1.schema.json', 'docs/schema/v1/interlanguage-backend-migration-receipt-v1.schema.json'],
  ['schemas/profiles/source-format-profile-v1.schema.json', 'docs/schema/v1/interlanguage-source-format-profile-v1.schema.json'],
  ['schemas/v1/curriculum-authority-v1.schema.json', 'docs/schema/v1/curriculum-authority-v1.schema.json'],
  ['schemas/v1/learner-read-model-v1.schema.json', 'docs/schema/v1/learner-read-model-v1.schema.json'],
  ['schemas/v1/learner-delivery-v1.schema.json', 'docs/schema/v1/learner-delivery-v1.schema.json'],
  ['schemas/v1/learner-state-v1.schema.json', 'docs/schema/v1/learner-state-v1.schema.json'],
  ['releases/v0.62.13/v23-adapter-index-v1.schema.json', 'docs/schema/v1/v23-adapter-index-v1.schema.json'],
  ['schemas/v1/a00-assessment-map-v1.schema.json', 'docs/schema/v1/a00-assessment-map-v1.schema.json'],
  ['schemas/v1/learner-tools-v1.schema.json', 'docs/schema/v1/learner-tools-v1.schema.json'],
  ['schemas/v2/backend-migration-receipt-v2.schema.json', 'docs/schema/v2/backend-migration-receipt-v2.schema.json'],
  ['schemas/v2/federation-package-v2.schema.json', 'docs/schema/v2/federation-package-v2.schema.json'],
  ['schemas/v2/federation-record-v2.schema.json', 'docs/schema/v2/federation-record-v2.schema.json'],
  ['schemas/v2/namespace-v2.json', 'docs/schema/v2/namespace-v2.json'],
  ['schemas/v2/pmi-release-policy-v2.json', 'docs/schema/v2/pmi-release-policy-v2.json'],
  ['backend/v2.2/schema/global-capability-contract-v0.1.schema.json', 'docs/schema/v2.2/global-capability-contract-v0.1.schema.json'],
  ['backend/v2.3/schema/lane-adapter-v2.3.1.schema.json', 'docs/schema/v2.3/lane-adapter-v2.3.1.schema.json'],
  ['backend/v2.3/schema/capability-declarations-v0.2.schema.json', 'docs/schema/v2.3/capability-declarations-v0.2.schema.json'],
  ['backend/v2.3/schema/namespace-crosswalk-v0.2.schema.json', 'docs/schema/v2.3/namespace-crosswalk-v0.2.schema.json'],
  ['backend/v2.3/schema/translation-state-index-v0.2.schema.json', 'docs/schema/v2.3/translation-state-index-v0.2.schema.json'],
  ['backend/v2.3/schema/csv-projection-manifest-v0.2.schema.json', 'docs/schema/v2.3/csv-projection-manifest-v0.2.schema.json'],
  ['backend/v2.3/schema/scope-declaration-v0.2.schema.json', 'docs/schema/v2.3/scope-declaration-v0.2.schema.json'],
  ['releases/v0.62.13/modular-backend-pattern-index-v1.json', 'docs/data/modular-backend-pattern-index-v1.json'],
  ['releases/v0.62.13/v23-adapter-index-v1.json', 'docs/data/v23-adapter-index-v1.json'],
  ['backend/course-capsule-v1/authority/modular-backend-pattern-index-v2.json', 'docs/data/modular-backend-pattern-index-v2.json'],
  ['backend/course-capsule-v1/authority/v23-adapter-index-v2.json', 'docs/data/v23-adapter-index-v2.json'],
  ['backend/course-capsule-v1/authority/feature-adoption-provenance-v1.json', 'docs/data/feature-adoption-provenance-v1.json'],
  ['backend/course-capsule-v1/authority/comparison-evidence-manifest-v1.json', 'docs/data/comparison-evidence-manifest-v1.json'],
  ['backend/course-capsule-v1/validation/MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json', 'docs/data/modular-backend-snapshot-v2-validation-receipt.json'],
  ['schemas/course-capsule-v1/v2/v23-adapter-index-v2.schema.json', 'docs/schema/v2/v23-adapter-index-v2.schema.json'],
  ['schemas/course-capsule-v1/v2/modular-backend-pattern-index-v2.schema.json', 'docs/schema/v2/modular-backend-pattern-index-v2.schema.json'],
  ['schemas/course-capsule-v1/v2/feature-adoption-provenance-v1.schema.json', 'docs/schema/v2/feature-adoption-provenance-v1.schema.json'],
  ['schemas/course-capsule-v1/v2/comparison-evidence-manifest-v1.schema.json', 'docs/schema/v2/comparison-evidence-manifest-v1.schema.json'],
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
