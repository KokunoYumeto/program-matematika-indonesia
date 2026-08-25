import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawn } from 'node:child_process';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const authorityPath = resolve(project, 'backend/authority/curriculum-authority-v1.json');
const readModelPath = resolve(project, 'docs/data/learner-read-model.json');
const coursesPath = resolve(project, 'docs/courses.js');
const publicAuthorityPath = resolve(project, 'docs/data/curriculum-authority-v1.json');
const builderPath = resolve(project, 'scripts/build-learner-read-model.mjs');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');

const [authorityBytes, modelBytes, coursesBytes, publicAuthorityBytes] = await Promise.all([
  readFile(authorityPath),
  readFile(readModelPath),
  readFile(coursesPath),
  readFile(publicAuthorityPath),
]);
const authority = JSON.parse(authorityBytes.toString('utf8'));
const model = JSON.parse(modelBytes.toString('utf8'));
const generated = await import(`${pathToFileURL(coursesPath).href}?sha=${sha256(coursesBytes)}`);

assert.equal(model.schema_id, 'interlanguage/program-matematika-indonesia-learner-read-model/v1');
assert.equal(model.$schema, 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v1/learner-read-model-v1.schema.json');
assert.deepEqual(publicAuthorityBytes, authorityBytes, 'Public authority copy differs from canonical authority.');
assert.equal(model.provenance.authority_sha256, sha256(authorityBytes));
assert.equal(model.provenance.federation_records_sha256, authority.federation.records_sha256);
assert.equal(model.provenance.federation_validation_report_sha256, authority.federation.validation_report_sha256);
assert.equal(model.provenance.federation_validation_result, 'pass');
assert.equal(model.policy.raw_json_is_learner_start, false);
assert.equal(model.policy.internal_workflow_locators_are_public_authority, false);
assert.equal(model.policy.source_and_effective_publication_states_are_distinct, true);
assert.equal(model.provenance.readback_overlay_count, authority.public_readback_overlays.length);

const uiCourses = model.courses.map(({ federation, ...course }) => course);
assert.deepEqual(uiCourses, authority.catalog.courses, 'Read-model UI projection differs from curriculum authority.');
assert.deepEqual([...generated.courses], authority.catalog.courses, 'Generated courses.js differs from curriculum authority.');
assert.deepEqual([...generated.topics], authority.catalog.topics, 'Generated topics differ from curriculum authority.');
assert.deepEqual(generated.program, authority.catalog.program, 'Generated program metadata differs from curriculum authority.');
assert.deepEqual(generated.nextCourseIdsById, model.nextCourseIdsById, 'Generated next-course map differs from read-model.');

assert.equal(uiCourses.length, 40);
assert.equal(new Set(uiCourses.map((course) => course.id)).size, 40);
assert.deepEqual(uiCourses.map((course) => course.id), authority.catalog.courses.map((course) => course.id));

const byId = new Map(uiCourses.map((course) => [course.id, course]));
const expectedNext = Object.fromEntries(uiCourses.map((course) => [course.id, []]));
for (const course of uiCourses) {
  assert.equal(course.level, course.id[0], `${course.id}: level/id mismatch.`);
  for (const prerequisite of course.prerequisites) {
    assert.ok(byId.has(prerequisite), `${course.id}: missing prerequisite ${prerequisite}.`);
    expectedNext[prerequisite].push(course.id);
  }
}
assert.deepEqual(model.nextCourseIdsById, expectedNext, 'Prerequisite reverse graph is not exact.');
const publishedIds = uiCourses.filter((course) => course.state === 'published').map((course) => course.id);
assert.deepEqual(publishedIds, authority.catalog.program.completedPublicCourseRoleIds, 'Published course set differs from authority.');

const recordsPath = resolve(project, authority.federation.records_path);
const recordsBytes = await readFile(recordsPath);
assert.equal(recordsBytes.length, authority.federation.records_bytes);
assert.equal(sha256(recordsBytes), authority.federation.records_sha256);
const records = recordsBytes.toString('utf8').trimEnd().split('\n').map((line) => JSON.parse(line));
const byRecordId = new Map(records.map((record) => [record.id, record]));
const forbiddenLearner = /(?:\.jsonl?(?:[?#]|$)|\/backend(?:[/?#]|$))/i;

for (const course of model.courses) {
  const fed = course.federation;
  const courseRecord = byRecordId.get(fed.course_record_id);
  const dataset = byRecordId.get(fed.owner_dataset_id);
  const primary = byRecordId.get(fed.primary_surface_id);
  assert.equal(courseRecord?.record_type, 'course', `${course.id}: invalid course record binding.`);
  assert.equal(dataset?.record_type, 'dataset', `${course.id}: invalid dataset binding.`);
  assert.equal(primary?.record_type, 'reader_surface', `${course.id}: invalid primary surface binding.`);
  assert.ok(dataset.payload.reader_surface_ids.includes(primary.id), `${course.id}: primary surface is not dataset-bound.`);
  assert.ok(primary.payload.course_ids.includes(course.id), `${course.id}: primary surface is not course-bound.`);
  assert.ok(primary.payload.actions.includes('learn'), `${course.id}: primary surface lacks learn action.`);
  assert.equal(primary.payload.url, courseRecord.payload.learner_start_url, `${course.id}: primary URL mismatch.`);
  assert.ok(!forbiddenLearner.test(primary.payload.url), `${course.id}: primary URL points to raw JSON/backend.`);
  assert.equal(fed.primary_source_publication_state, primary.payload.publication_state, `${course.id}: source publication state mismatch.`);
  if (course.state === 'published') {
    assert.equal(fed.primary_effective_publication_state, 'public', `${course.id}: published primary is not effectively public.`);
  }
  if (fed.primary_readback) {
    const overlay = authority.public_readback_overlays.find((entry) => entry.surface_id === primary.id);
    assert.ok(overlay, `${course.id}: readback lacks authority overlay.`);
    assert.equal(overlay.url, primary.payload.url, `${course.id}: overlay URL mismatch.`);
    assert.equal(fed.primary_readback.sha256, overlay.sha256, `${course.id}: overlay SHA-256 mismatch.`);
    assert.equal(fed.primary_effective_publication_state, overlay.effective_publication_state);
  }

  for (const surfaces of Object.values(fed.action_surfaces)) {
    for (const surface of surfaces) {
      const live = byRecordId.get(surface.surface_id);
      assert.equal(live?.record_type, 'reader_surface', `${course.id}: invalid action surface.`);
      assert.ok(dataset.payload.reader_surface_ids.includes(live.id), `${course.id}: action surface is not dataset-bound.`);
      assert.ok(live.payload.course_ids.includes(course.id), `${course.id}: action surface is not course-bound.`);
      assert.equal(live.payload.url, surface.url, `${course.id}: action-surface URL mismatch.`);
    }
  }
}

for (const [name, bytes] of [['learner-read-model.json', modelBytes], ['courses.js', coursesBytes]]) {
  const text = bytes.toString('utf8');
  assert.ok(!text.includes('codex://'), `${name}: internal workflow locator leaked.`);
  assert.ok(!text.includes('C:\\Users\\'), `${name}: local absolute path leaked.`);
}

function runBuilder(readModel, courses, publicAuthority) {
  return new Promise((accept, reject) => {
    const child = spawn(process.execPath, [builderPath, '--read-model', readModel, '--courses', courses, '--public-authority', publicAuthority], {
      cwd: project,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', reject);
    child.on('close', (code) => code === 0 ? accept(stdout) : reject(new Error(`Builder failed (${code}): ${stderr}`)));
  });
}

const scratch = await mkdtemp(join(tmpdir(), 'pmi-learner-read-model-'));
assert.ok(scratch.startsWith(`${tmpdir()}${sep}`), 'Temporary replay root escaped the system temp directory.');
try {
  const paths = {
    aModel: join(scratch, 'a', 'learner-read-model.json'),
    aCourses: join(scratch, 'a', 'courses.js'),
    aAuthority: join(scratch, 'a', 'curriculum-authority-v1.json'),
    bModel: join(scratch, 'b', 'learner-read-model.json'),
    bCourses: join(scratch, 'b', 'courses.js'),
    bAuthority: join(scratch, 'b', 'curriculum-authority-v1.json'),
  };
  await runBuilder(paths.aModel, paths.aCourses, paths.aAuthority);
  await runBuilder(paths.bModel, paths.bCourses, paths.bAuthority);
  const [aModel, aCourses, aAuthority, bModel, bCourses, bAuthority] = await Promise.all([
    readFile(paths.aModel), readFile(paths.aCourses), readFile(paths.aAuthority),
    readFile(paths.bModel), readFile(paths.bCourses), readFile(paths.bAuthority),
  ]);
  assert.deepEqual(aModel, bModel, 'A/B learner read-model replay differs.');
  assert.deepEqual(aCourses, bCourses, 'A/B generated courses.js replay differs.');
  assert.deepEqual(aAuthority, bAuthority, 'A/B public authority replay differs.');
  assert.deepEqual(aModel, modelBytes, 'Checked-in learner read-model differs from replay.');
  assert.deepEqual(aCourses, coursesBytes, 'Checked-in courses.js differs from replay.');
  assert.deepEqual(aAuthority, authorityBytes, 'Checked-in public authority differs from replay.');
} finally {
  await rm(scratch, { recursive: true, force: true });
}

console.log(JSON.stringify({
  status: 'pass',
  course_count: uiCourses.length,
  prerequisite_edges: Object.values(expectedNext).reduce((sum, values) => sum + values.length, 0),
  learner_read_model: { bytes: modelBytes.length, sha256: sha256(modelBytes) },
  generated_courses_js: { bytes: coursesBytes.length, sha256: sha256(coursesBytes) },
  public_curriculum_authority: { bytes: publicAuthorityBytes.length, sha256: sha256(publicAuthorityBytes) },
  published_course_count: publishedIds.length,
  public_readback_overlay_count: authority.public_readback_overlays.length,
  internal_workflow_locator_count: 0,
  primary_json_or_backend_violation_count: 0,
  deterministic_replay: 'byte-identical',
}, null, 2));
