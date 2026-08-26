import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
await import('./build-d20-learner-routes.mjs');
await import('./build-c100-learner-routes.mjs');

const load = async (name) => JSON.parse(await readFile(resolve(project, 'docs', 'data', name), 'utf8'));
const [d20, c100] = await Promise.all([
  load('unit-route-D20-v2.1.json'),
  load('unit-route-C100-v2.1.json'),
]);
assert.equal(d20.course_id, 'D20');
assert.equal(d20.units.length, 17);
assert.equal(c100.course_id, 'C100');
assert.equal(c100.units.length, 939);
const routeManifest = {
  schema_id: 'program-matematika-indonesia/unit-route-v2.1/v2',
  recorded_at: '2026-08-26T00:00:00+02:00',
  summary: {
    course_count: 2,
    unit_count: 956,
    chapter_wrapper_count: 37,
    exact_hosted_reader_count: 1,
    exact_hosted_solution_pdf_count: 1,
  },
  courses: [d20, c100],
};
await writeFile(resolve(project, 'docs', 'data', 'unit-routes-v2.1.json'), `${JSON.stringify(routeManifest, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({ result: 'pass', courses: ['D20', 'C100'], units: 956, chapter_wrappers: 37, exact_hosted_solution_pdfs: 1 }));
