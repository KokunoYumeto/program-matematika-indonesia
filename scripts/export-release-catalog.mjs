import { writeFile } from 'node:fs/promises';
import { courses, program, topics } from '../docs/courses.js';

const outputPath = process.argv[2];
const sourceCommit = process.argv[3];

if (!outputPath || !sourceCommit) {
  throw new Error('Pemakaian: node scripts/export-release-catalog.mjs <output.json> <source-commit>');
}

const catalog = {
  $schema: 'https://zenodo.org/records/22061915/files/program-matematika-indonesia-catalog-v1.schema.json',
  schemaVersion: 1,
  snapshotDate: '2026-08-22',
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
