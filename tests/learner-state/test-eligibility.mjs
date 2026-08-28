import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

import {
  LEARNER_STATE_STORAGE_KEY,
  createEmptyLearnerState,
  evaluateLearnerState,
  loadLearnerState,
  normalizeLearnerState,
  serializeLearnerState,
  setCourseClaim,
  setCourseCompletion,
  setPrerequisiteWaiver,
} from '../../docs/learner-state.js';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const authority = JSON.parse(await readFile(resolve(project, 'backend/authority/curriculum-authority-v1.json'), 'utf8'));
const courses = structuredClone(authority.catalog.courses);
const d80 = courses.find(({ id }) => id === 'D80');
if (!d80.prerequisites.includes('D70')) d80.prerequisites.push('D70');
const edges = courses.reduce((sum, course) => sum + course.prerequisites.length, 0);

test('v0.62 graph fixture is exact', () => {
  assert.equal(courses.length, 40);
  assert.equal(new Set(courses.map(({ id }) => id)).size, 40);
  assert.equal(edges, 83);
  assert.deepEqual([...d80.prerequisites].sort(), ['C30', 'C80', 'D70']);
  if (authority.catalog.program.version === '0.62.0') {
    assert.deepEqual([...authority.catalog.courses.find(({ id }) => id === 'D80').prerequisites].sort(), ['C30', 'C80', 'D70']);
  }
});

test('D80 eligibility respects completion, claims, and edge-scoped waiver', () => {
  const empty = createEmptyLearnerState();
  assert.equal(evaluateLearnerState(courses, empty).D80.status, 'blocked');
  assert.deepEqual(evaluateLearnerState(courses, empty).D80.missingPrerequisiteIds.sort(), ['C30', 'C80', 'D70']);

  let state = empty;
  for (const id of ['C30', 'C80', 'D70']) state = setCourseCompletion(state, courses, id, true, '2026-08-28T20:00:00Z');
  assert.equal(evaluateLearnerState(courses, state).D80.status, 'eligible');

  state = setCourseCompletion(empty, courses, 'D70', true, '2026-08-28T20:00:00Z');
  state = setCourseClaim(state, courses, 'placement', 'C30', true, '2026-08-28T20:00:00Z');
  state = setCourseClaim(state, courses, 'equivalence', 'C80', true, '2026-08-28T20:00:00Z');
  assert.equal(evaluateLearnerState(courses, state).D80.status, 'eligible');

  state = setCourseCompletion(empty, courses, 'C30', true, '2026-08-28T20:00:00Z');
  state = setCourseCompletion(state, courses, 'C80', true, '2026-08-28T20:00:00Z');
  state = setPrerequisiteWaiver(state, courses, 'D80', 'D70', true, '2026-08-28T20:00:00Z');
  const evaluation = evaluateLearnerState(courses, state);
  assert.equal(evaluation.D80.status, 'eligible_with_waiver');
  assert.equal(evaluation.D100.status, 'blocked');
  assert.equal(evaluation.D100.prerequisites.find(({ courseId }) => courseId === 'D70').satisfaction, 'missing');
});

test('completion never fabricates ancestor completion', () => {
  const state = setCourseCompletion(createEmptyLearnerState(), courses, 'D80', true, '2026-08-28T20:00:00Z');
  const evaluation = evaluateLearnerState(courses, state);
  assert.equal(evaluation.D80.status, 'completed');
  for (const id of ['C30', 'C80', 'D70']) assert.notEqual(evaluation[id].status, 'completed');
});

test('invalid state is rejected and corrupt storage recovers safely', () => {
  const base = createEmptyLearnerState();
  assert.throws(() => normalizeLearnerState({ ...base, completedCourseIds: ['Z99'] }, courses));
  assert.throws(() => normalizeLearnerState({ ...base, updatedAt: 'yesterday' }, courses));
  assert.throws(() => normalizeLearnerState({ ...base, updatedAt: '2026-02-30T12:00:00Z' }, courses));
  assert.throws(() => normalizeLearnerState({ ...base, waivers: [{ targetCourseId: 'D80', prerequisiteCourseId: 'A00' }] }, courses));
  const storage = { getItem(key) { assert.equal(key, LEARNER_STATE_STORAGE_KEY); return '{bad'; } };
  const recovered = loadLearnerState(storage, courses);
  assert.equal(recovered.status, 'recovered_invalid');
  assert.deepEqual(recovered.state, base);
});

test('serialization is deterministic', () => {
  const a = {
    ...createEmptyLearnerState(),
    updatedAt: '2026-08-28T20:00:00Z',
    completedCourseIds: ['D70', 'C30'],
    placementClaims: [{ courseId: 'C80' }, { courseId: 'A00' }],
    equivalenceClaims: [{ courseId: 'B10' }, { courseId: 'A20' }],
    waivers: [
      { targetCourseId: 'D80', prerequisiteCourseId: 'D70' },
      { targetCourseId: 'D100', prerequisiteCourseId: 'D70' },
    ],
  };
  const b = {
    ...a,
    completedCourseIds: [...a.completedCourseIds].reverse(),
    placementClaims: [...a.placementClaims].reverse(),
    equivalenceClaims: [...a.equivalenceClaims].reverse(),
    waivers: [...a.waivers].reverse(),
  };
  assert.equal(serializeLearnerState(a, courses), serializeLearnerState(b, courses));
});
