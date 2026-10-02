export const LEARNER_STATE_STORAGE_KEY = 'program-matematika-indonesia/learner-state/v1';

const SCHEMA_URL = 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v1/learner-state-v1.schema.json';
const SCHEMA_ID = 'interlanguage/program-matematika-indonesia-learner-state/v1';
const SCHEMA_VERSION = '1.0.0';

function assert(condition, message) {
  if (!condition) throw new TypeError(message);
}

function courseIndex(courses) {
  assert(Array.isArray(courses), 'courses must be an array');
  const byId = new Map();
  for (const course of courses) {
    assert(course && typeof course === 'object', 'course must be an object');
    assert(typeof course.id === 'string' && /^[A-D][0-9]{2,3}$/.test(course.id), 'course has an invalid ID');
    assert(!byId.has(course.id), `duplicate course ID: ${course.id}`);
    assert(Array.isArray(course.prerequisites), `${course.id}: prerequisites must be an array`);
    byId.set(course.id, course);
  }
  return byId;
}

function assertExactKeys(value, keys, label) {
  assert(value && typeof value === 'object' && !Array.isArray(value), `${label} must be an object`);
  const actual = Object.keys(value).sort();
  const expected = [...keys].sort();
  assert(JSON.stringify(actual) === JSON.stringify(expected), `${label} has unexpected or missing keys`);
}

function validTimestamp(value) {
  if (value === null) return true;
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/.test(value)) return false;
  const milliseconds = Date.parse(value);
  if (Number.isNaN(milliseconds)) return false;
  const canonical = new Date(milliseconds).toISOString();
  return canonical === value || canonical.replace('.000Z', 'Z') === value;
}

function normalizedCourseIds(values, byId, label) {
  assert(Array.isArray(values), `${label} must be an array`);
  const result = values.map((id) => {
    assert(typeof id === 'string' && byId.has(id), `${label} contains unknown course ID: ${id}`);
    return id;
  });
  assert(new Set(result).size === result.length, `${label} contains duplicates`);
  return result.sort();
}

function normalizedClaims(values, byId, label) {
  assert(Array.isArray(values), `${label} must be an array`);
  const result = values.map((claim) => {
    assertExactKeys(claim, ['courseId'], `${label} claim`);
    assert(typeof claim.courseId === 'string' && byId.has(claim.courseId), `${label} contains unknown course ID`);
    return { courseId: claim.courseId };
  }).sort((a, b) => a.courseId.localeCompare(b.courseId));
  assert(new Set(result.map(({ courseId }) => courseId)).size === result.length, `${label} contains duplicates`);
  return result;
}

function normalizedWaivers(values, byId) {
  assert(Array.isArray(values), 'waivers must be an array');
  const result = values.map((waiver) => {
    assertExactKeys(waiver, ['targetCourseId', 'prerequisiteCourseId'], 'waiver');
    const target = byId.get(waiver.targetCourseId);
    assert(target, `waiver has unknown target course: ${waiver.targetCourseId}`);
    assert(byId.has(waiver.prerequisiteCourseId), `waiver has unknown prerequisite course: ${waiver.prerequisiteCourseId}`);
    assert(target.prerequisites.includes(waiver.prerequisiteCourseId), `waiver is not a direct prerequisite edge: ${waiver.targetCourseId}<-${waiver.prerequisiteCourseId}`);
    return { targetCourseId: waiver.targetCourseId, prerequisiteCourseId: waiver.prerequisiteCourseId };
  }).sort((a, b) => a.targetCourseId.localeCompare(b.targetCourseId) || a.prerequisiteCourseId.localeCompare(b.prerequisiteCourseId));
  const keys = result.map(({ targetCourseId, prerequisiteCourseId }) => `${targetCourseId}<-${prerequisiteCourseId}`);
  assert(new Set(keys).size === keys.length, 'waivers contains duplicates');
  return result;
}

export function createEmptyLearnerState() {
  return {
    $schema: SCHEMA_URL,
    schemaId: SCHEMA_ID,
    schemaVersion: SCHEMA_VERSION,
    updatedAt: null,
    completedCourseIds: [],
    placementClaims: [],
    equivalenceClaims: [],
    waivers: [],
  };
}

export function normalizeLearnerState(value, courses) {
  const byId = courseIndex(courses);
  assertExactKeys(value, ['$schema', 'schemaId', 'schemaVersion', 'updatedAt', 'completedCourseIds', 'placementClaims', 'equivalenceClaims', 'waivers'], 'learner state');
  assert(value.$schema === SCHEMA_URL, 'learner state schema URL differs');
  assert(value.schemaId === SCHEMA_ID, 'learner state schema ID differs');
  assert(value.schemaVersion === SCHEMA_VERSION, 'learner state schema version differs');
  assert(validTimestamp(value.updatedAt), 'learner state updatedAt is invalid');
  return {
    $schema: SCHEMA_URL,
    schemaId: SCHEMA_ID,
    schemaVersion: SCHEMA_VERSION,
    updatedAt: value.updatedAt,
    completedCourseIds: normalizedCourseIds(value.completedCourseIds, byId, 'completedCourseIds'),
    placementClaims: normalizedClaims(value.placementClaims, byId, 'placementClaims'),
    equivalenceClaims: normalizedClaims(value.equivalenceClaims, byId, 'equivalenceClaims'),
    waivers: normalizedWaivers(value.waivers, byId),
  };
}

export function serializeLearnerState(value, courses) {
  return JSON.stringify(normalizeLearnerState(value, courses));
}

export function loadLearnerState(storage, courses) {
  if (!storage || typeof storage.getItem !== 'function') return { state: createEmptyLearnerState(), status: 'unavailable' };
  try {
    const raw = storage.getItem(LEARNER_STATE_STORAGE_KEY);
    if (raw === null) return { state: createEmptyLearnerState(), status: 'empty' };
    return { state: normalizeLearnerState(JSON.parse(raw), courses), status: 'loaded' };
  } catch {
    return { state: createEmptyLearnerState(), status: 'recovered_invalid' };
  }
}

export function saveLearnerState(storage, value, courses) {
  const state = normalizeLearnerState(value, courses);
  if (!storage || typeof storage.setItem !== 'function') return { state, persisted: false };
  try {
    storage.setItem(LEARNER_STATE_STORAGE_KEY, JSON.stringify(state));
    return { state, persisted: true };
  } catch {
    return { state, persisted: false };
  }
}

export function clearLearnerState(storage) {
  if (!storage || typeof storage.removeItem !== 'function') return false;
  try {
    storage.removeItem(LEARNER_STATE_STORAGE_KEY);
    return true;
  } catch {
    return false;
  }
}

function timestamp(value) {
  const result = value ?? new Date().toISOString();
  assert(validTimestamp(result), 'transition timestamp is invalid');
  return result;
}

export function setCourseCompletion(value, courses, courseId, completed, updatedAt) {
  const state = normalizeLearnerState(value, courses);
  const ids = new Set(state.completedCourseIds);
  if (completed) ids.add(courseId); else ids.delete(courseId);
  return normalizeLearnerState({ ...state, updatedAt: timestamp(updatedAt), completedCourseIds: [...ids] }, courses);
}

export function setCourseClaim(value, courses, kind, courseId, present, updatedAt) {
  assert(kind === 'placement' || kind === 'equivalence', 'claim kind must be placement or equivalence');
  const state = normalizeLearnerState(value, courses);
  const field = kind === 'placement' ? 'placementClaims' : 'equivalenceClaims';
  const ids = new Set(state[field].map((claim) => claim.courseId));
  if (present) ids.add(courseId); else ids.delete(courseId);
  return normalizeLearnerState({ ...state, updatedAt: timestamp(updatedAt), [field]: [...ids].map((id) => ({ courseId: id })) }, courses);
}

export function setPrerequisiteWaiver(value, courses, targetCourseId, prerequisiteCourseId, present, updatedAt) {
  const state = normalizeLearnerState(value, courses);
  const key = `${targetCourseId}<-${prerequisiteCourseId}`;
  const byKey = new Map(state.waivers.map((waiver) => [`${waiver.targetCourseId}<-${waiver.prerequisiteCourseId}`, waiver]));
  if (present) byKey.set(key, { targetCourseId, prerequisiteCourseId }); else byKey.delete(key);
  return normalizeLearnerState({ ...state, updatedAt: timestamp(updatedAt), waivers: [...byKey.values()] }, courses);
}

export function evaluateLearnerState(courses, value) {
  const state = normalizeLearnerState(value, courses);
  const completed = new Set(state.completedCourseIds);
  const placement = new Set(state.placementClaims.map(({ courseId }) => courseId));
  const equivalence = new Set(state.equivalenceClaims.map(({ courseId }) => courseId));
  const waivers = new Set(state.waivers.map(({ targetCourseId, prerequisiteCourseId }) => `${targetCourseId}<-${prerequisiteCourseId}`));
  return Object.fromEntries(courses.map((course) => {
    const prerequisites = course.prerequisites.map((courseId) => {
      let satisfaction = 'missing';
      if (completed.has(courseId)) satisfaction = 'completed';
      else if (placement.has(courseId)) satisfaction = 'placement';
      else if (equivalence.has(courseId)) satisfaction = 'equivalence';
      else if (waivers.has(`${course.id}<-${courseId}`)) satisfaction = 'waived';
      return { courseId, satisfaction };
    });
    const missingPrerequisiteIds = prerequisites.filter(({ satisfaction }) => satisfaction === 'missing').map(({ courseId }) => courseId);
    const hasWaiver = prerequisites.some(({ satisfaction }) => satisfaction === 'waived');
    const status = completed.has(course.id)
      ? 'completed'
      : missingPrerequisiteIds.length
        ? 'blocked'
        : hasWaiver
          ? 'eligible_with_waiver'
          : 'eligible';
    return [course.id, { courseId: course.id, status, prerequisites, missingPrerequisiteIds }];
  }));
}
