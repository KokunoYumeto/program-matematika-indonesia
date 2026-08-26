import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const authorityRelative = 'backend/authority/curriculum-authority-v1.json';
const predecessorRelative = 'backend/authority/history/curriculum-authority-v0.55.0.json';
const nextCatalogRelative = 'backend/authority/catalogs/program-matematika-indonesia-catalog-v0.56.0.json';
const version = '0.56.0';

function option(name) {
  const index = process.argv.indexOf(name);
  if (index === -1 || !process.argv[index + 1]) throw new Error(`Missing required option ${name}.`);
  return process.argv[index + 1];
}

const recordId = Number(option('--record-id'));
const sourceCommit = option('--source-commit');
const snapshotDate = option('--snapshot-date');
assert.ok(Number.isInteger(recordId) && recordId > 0);
assert.match(sourceCommit, /^[0-9a-f]{40}$/);
assert.match(snapshotDate, /^\d{4}-\d{2}-\d{2}$/);

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
const authorityPath = resolve(project, authorityRelative);
const predecessorPath = resolve(project, predecessorRelative);
const currentBytes = await readFile(authorityPath);
const predecessor = JSON.parse(currentBytes.toString('utf8'));
assert.equal(predecessor.schema_id, 'interlanguage/program-matematika-indonesia-curriculum-authority/v1');
assert.equal(predecessor.catalog.program.version, '0.55.0');
assert.equal(predecessor.catalog.program.zenodo, 'https://doi.org/10.5281/zenodo.22102685');
assert.equal(predecessor.catalog.program.zenodoConcept, 'https://doi.org/10.5281/zenodo.22059707');

await mkdir(dirname(predecessorPath), { recursive: true });
await copyFile(authorityPath, predecessorPath);

const authority = structuredClone(predecessor);
const program = authority.catalog.program;
program.version = version;
program.snapshotDate = snapshotDate;
program.zenodo = `https://doi.org/10.5281/zenodo.${recordId}`;
program.repositories.github.lastConfirmedAt = snapshotDate;
program.backend.schema = `https://zenodo.org/records/${recordId}/files/interlanguage-math-backend-v1.schema.json?download=1`;
program.backend.sourceFormatProfile = `https://zenodo.org/records/${recordId}/files/interlanguage-source-format-profile-v1.schema.json?download=1`;
program.backend.package = `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-backend-v1-v${version}.zip?download=1`;
program.backend.federationV2.package = `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-backend-v2-v${version}.zip?download=1`;
program.backend.federationV2.packageSchema = `https://zenodo.org/records/${recordId}/files/federation-package-v2.schema.json?download=1`;
program.backend.federationV2.recordSchema = `https://zenodo.org/records/${recordId}/files/federation-record-v2.schema.json?download=1`;
program.backend.federationV2.validationReceipt = `https://zenodo.org/records/${recordId}/files/GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v${version}.json?download=1`;
program.backend.federationV21 = {
  version: '2.1.0',
  status: 'pilot_validated',
  pilot_courses: ['A00', 'B10', 'D20'],
  pilot_units: 255,
  pilot_relations: 1171,
  route_wrapper_course: 'D20',
  packageSchema: `https://zenodo.org/records/${recordId}/files/federation-unit-package-v2.1.schema.json?download=1`,
  recordSchema: `https://zenodo.org/records/${recordId}/files/federation-unit-record-v2.1.schema.json?download=1`,
  package: `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-backend-v2.1-pilots-v${version}.zip?download=1`,
};
Object.assign(program.backend.learnerReadModelV1, {
  authority: `https://zenodo.org/records/${recordId}/files/curriculum-authority-v1.json?download=1`,
  authoritySchema: `https://zenodo.org/records/${recordId}/files/curriculum-authority-v1.schema.json?download=1`,
  readModel: `https://zenodo.org/records/${recordId}/files/learner-read-model-v1.json?download=1`,
  readModelSchema: `https://zenodo.org/records/${recordId}/files/learner-read-model-v1.schema.json?download=1`,
  validationReceipt: `https://zenodo.org/records/${recordId}/files/LOCAL_RELEASE_VALIDATION_v${version}.json?download=1`,
});
authority.lineage = {
  bootstrap_release_version: '0.53.0',
  predecessor_authority: {
    path: predecessorRelative,
    bytes: currentBytes.length,
    sha256: sha256(currentBytes),
  },
  transition: {
    from_version: '0.55.0',
    to_version: version,
    snapshot_date: snapshotDate,
    zenodo_record_id: recordId,
    method: 'additive_v2.1_pilot_and_d20_learner_route_successor',
  },
};
authority.catalog.program = program;
authority.seed_catalog = {
  path: nextCatalogRelative,
  bytes: 0,
  sha256: '',
};
const catalog = {
  ...authority.catalog,
  $schema: `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-catalog-v1.schema.json`,
  snapshotDate,
  sourceCommit,
};
const catalogBytes = canonical(catalog);
authority.seed_catalog.bytes = catalogBytes.length;
authority.seed_catalog.sha256 = sha256(catalogBytes);
authority.catalog = catalog;
const authorityBytes = canonical(authority);
await mkdir(resolve(project, dirname(nextCatalogRelative)), { recursive: true });
await writeFile(resolve(project, nextCatalogRelative), catalogBytes);
await writeFile(authorityPath, authorityBytes);
console.log(JSON.stringify({
  version,
  record_id: recordId,
  authority: {path: authorityRelative, bytes: authorityBytes.length, sha256: sha256(authorityBytes)},
  predecessor: {path: predecessorRelative, bytes: currentBytes.length, sha256: sha256(currentBytes)},
  catalog: {path: nextCatalogRelative, bytes: catalogBytes.length, sha256: sha256(catalogBytes)},
}, null, 2));
