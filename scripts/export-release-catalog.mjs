import { writeFile } from 'node:fs/promises';
import { courses, program, topics } from '../docs/courses.js';

const outputPath = process.argv[2];
const sourceCommit = process.argv[3];

if (!outputPath || !sourceCommit) {
  throw new Error('Pemakaian: node scripts/export-release-catalog.mjs <output.json> <source-commit>');
}

const recordId = new URL(program.zenodo).pathname.split('.').at(-1);
if (!/^\d+$/.test(recordId ?? '')) {
  throw new Error(`DOI Zenodo program tidak memiliki record ID yang sah: ${program.zenodo}`);
}

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
