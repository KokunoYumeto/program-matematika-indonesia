import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const authorityPath = resolve(project, 'backend/authority/curriculum-authority-v1.json');

const outputPath = process.argv[2];
const sourceCommit = process.argv[3];

if (!outputPath || !sourceCommit) {
  throw new Error('Pemakaian: node scripts/export-release-catalog.mjs <output.json> <source-commit>');
}

const authorityBytes = await readFile(authorityPath);
const authority = JSON.parse(authorityBytes.toString('utf8'));
assert.equal(authority.schema_id, 'interlanguage/program-matematika-indonesia-curriculum-authority/v1');
assert.equal(authority.authority_state, 'active_versioned_successor');
assert.equal(authority.authority_policy.docs_courses_js_is_authority, false);
const seedBytes = await readFile(resolve(project, authority.seed_catalog.path));
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
assert.equal(seedBytes.length, authority.seed_catalog.bytes, 'Authority seed byte count changed.');
assert.equal(sha256(seedBytes), authority.seed_catalog.sha256, 'Authority seed SHA-256 changed.');
const seedCatalog = JSON.parse(seedBytes.toString('utf8'));
assert.deepEqual(authority.catalog.courses, seedCatalog.courses, 'Successor course authority differs from its frozen seed.');
assert.deepEqual(authority.catalog.topics, seedCatalog.topics, 'Successor topic authority differs from its frozen seed.');
assert.equal(authority.catalog.program.id, seedCatalog.program.id);
assert.equal(authority.catalog.program.zenodoConcept, seedCatalog.program.zenodoConcept);

const { courses, program, topics } = authority.catalog;
const recordId = new URL(program.zenodo).pathname.split('.').at(-1);
if (!/^\d+$/.test(recordId ?? '')) {
  throw new Error(`DOI Zenodo program tidak memiliki record ID yang sah: ${program.zenodo}`);
}
assert.equal(Number(recordId), authority.lineage.transition.zenodo_record_id, 'Authority transition and release DOI record IDs differ.');
assert.equal(program.version, authority.lineage.transition.to_version, 'Authority transition and program versions differ.');

const catalog = {
  $schema: `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-catalog-v1.schema.json`,
  schemaVersion: 1,
  snapshotDate: program.snapshotDate,
  sourceCommit,
  program,
  topics,
  counts: {
    courseRoles: courses.length,
    selectedCorpusRoles: courses.filter(({ state }) => state !== 'unresolved').length,
    unresolvedRoles: courses.filter(({ state }) => state === 'unresolved').length,
    completedPublicCourseRoles: program.completedPublicCourseRoleIds.length,
    completedPublicRecords: program.completedPublicRecordDois.length
  },
  courses
};

await writeFile(outputPath, `${JSON.stringify(catalog, null, 2)}\n`, 'utf8');
