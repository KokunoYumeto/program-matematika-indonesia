import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const authorityPath = resolve(project, 'backend/authority/curriculum-authority-v1.json');

function option(name, fallback) {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : resolve(process.argv[index + 1]);
}

const readModelPath = option('--read-model', resolve(project, 'docs/data/learner-read-model.json'));
const coursesPath = option('--courses', resolve(project, 'docs/courses.js'));
const publicAuthorityPath = option('--public-authority', resolve(project, 'docs/data/curriculum-authority-v1.json'));
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => `${JSON.stringify(value, null, 2)}\n`;

const authorityBytes = await readFile(authorityPath);
const authority = JSON.parse(authorityBytes.toString('utf8'));
assert.equal(authority.schema_id, 'interlanguage/program-matematika-indonesia-curriculum-authority/v1');
assert.equal(authority.$schema, 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v1/curriculum-authority-v1.schema.json');
assert.equal(authority.authority_state, 'active_versioned_successor');
assert.equal(authority.authority_policy.docs_courses_js_is_authority, false);
assert.equal(authority.authority_policy.learner_site_is_generated_output, true);

const seedPath = resolve(project, authority.seed_catalog.path);
const recordsPath = resolve(project, authority.federation.records_path);
const validationPath = resolve(project, authority.federation.validation_report_path);
const [seedBytes, recordsBytes, validationBytes] = await Promise.all([
  readFile(seedPath),
  readFile(recordsPath),
  readFile(validationPath),
]);

for (const [name, bytes, expectedBytes, expectedSha] of [
  ['seed catalog', seedBytes, authority.seed_catalog.bytes, authority.seed_catalog.sha256],
  ['federation records', recordsBytes, authority.federation.records_bytes, authority.federation.records_sha256],
  ['federation validation report', validationBytes, authority.federation.validation_report_bytes, authority.federation.validation_report_sha256],
]) {
  assert.equal(bytes.length, expectedBytes, `${name}: byte count changed.`);
  assert.equal(sha256(bytes), expectedSha, `${name}: SHA-256 changed.`);
}

const seedCatalog = JSON.parse(seedBytes.toString('utf8'));
assert.deepEqual(authority.catalog.courses, seedCatalog.courses, 'Successor course authority differs from the frozen seed.');
assert.deepEqual(authority.catalog.topics, seedCatalog.topics, 'Successor topic authority differs from the frozen seed.');
assert.equal(authority.catalog.program.id, seedCatalog.program.id);
assert.equal(authority.catalog.program.website, seedCatalog.program.website);
assert.equal(authority.catalog.program.zenodoConcept, seedCatalog.program.zenodoConcept);
assert.deepEqual(authority.catalog.program.completedPublicCourseRoleIds, seedCatalog.program.completedPublicCourseRoleIds);
assert.deepEqual(authority.catalog.program.completedPublicRecordDois, seedCatalog.program.completedPublicRecordDois);
const predecessorPath = resolve(project, authority.lineage.predecessor_authority.path);
const predecessorBytes = await readFile(predecessorPath);
assert.equal(predecessorBytes.length, authority.lineage.predecessor_authority.bytes, 'Predecessor authority byte count changed.');
assert.equal(sha256(predecessorBytes), authority.lineage.predecessor_authority.sha256, 'Predecessor authority SHA-256 changed.');
const validation = JSON.parse(validationBytes.toString('utf8'));
assert.equal(validation.result, 'pass', 'Federation validation report does not pass.');
assert.equal(validation.checks.records_jsonl_sha256, authority.federation.records_sha256);

const records = recordsBytes.toString('utf8').trimEnd().split('\n').map((line) => JSON.parse(line));
const byType = Object.groupBy(records, (record) => record.record_type);
assert.equal(byType.course.length, 40, 'Expected exactly 40 v2 course records.');
assert.equal(byType.dataset.length, 34, 'Expected exactly 34 v2 datasets.');
assert.equal(
  byType.reader_surface.length,
  validation.checks.table_counts.reader_surfaces,
  'Reader-surface count differs from the validated federation.',
);

const coursesByCode = new Map(byType.course.map((record) => [record.payload.course_id, record]));
const datasetsById = new Map(byType.dataset.map((record) => [record.id, record]));
const surfacesById = new Map(byType.reader_surface.map((record) => [record.id, record]));
const readbackBySurfaceId = new Map(authority.public_readback_overlays.map((overlay) => {
  assert.ok(!overlay.url.includes('codex://'), `${overlay.course_id}: public readback URL is internal.`);
  return [overlay.surface_id, overlay];
}));
assert.equal(readbackBySurfaceId.size, authority.public_readback_overlays.length, 'Duplicate public readback surface ID.');

const forbiddenLearner = /(?:\.jsonl?(?:[?#]|$)|\/backend(?:[/?#]|$))/i;
const actionOrder = ['learn', 'html', 'pdf', 'epub', 'offline', 'source', 'repository', 'doi', 'backend'];

function boundSurfaces(courseCode, dataset) {
  return dataset.payload.reader_surface_ids.map((id) => {
    const surface = surfacesById.get(id);
    assert.ok(surface, `${courseCode}: dataset references missing reader surface ${id}.`);
    return surface;
  }).filter((surface) => surface.payload.course_ids.includes(courseCode));
}

function oneSurface(surfaces, predicate, label, required = false) {
  const matches = surfaces.filter(predicate);
  assert.ok(matches.length <= 1, `${label}: expected at most one surface, found ${matches.length}.`);
  if (required) assert.equal(matches.length, 1, `${label}: required surface is missing.`);
  return matches[0] ?? null;
}

function surfaceSummary(surface) {
  if (!surface) return null;
  const overlay = readbackBySurfaceId.get(surface.id) ?? null;
  if (overlay) {
    assert.equal(overlay.url, surface.payload.url, `${surface.id}: readback URL differs from the source surface.`);
    assert.equal(overlay.source_publication_state, surface.payload.publication_state, `${surface.id}: readback source state differs.`);
  }
  return {
    surface_id: surface.id,
    semantic_key: surface.semantic_key,
    actions: [...surface.payload.actions],
    format: surface.payload.format,
    locale: surface.payload.locale,
    source_publication_state: surface.payload.publication_state,
    effective_publication_state: overlay?.effective_publication_state ?? surface.payload.publication_state,
    url: surface.payload.url,
    evidence_kind: surface.payload.evidence_kind,
    evidence_locator: surface.payload.evidence_locator,
    evidence_sha256: surface.payload.evidence_sha256,
    readback: overlay ? {
      evidence_kind: overlay.evidence_kind,
      bytes: overlay.bytes,
      sha256: overlay.sha256,
      verified_at: overlay.verified_at,
    } : null,
  };
}

const projectedCourses = authority.catalog.courses.map((authorityCourse) => {
  const course = coursesByCode.get(authorityCourse.id);
  assert.ok(course, `Missing v2 course ${authorityCourse.id}.`);
  const dataset = datasetsById.get(course.payload.owner_dataset_id);
  assert.ok(dataset, `${authorityCourse.id}: missing owner dataset.`);
  const surfaces = boundSurfaces(authorityCourse.id, dataset);

  const primary = oneSurface(
    surfaces,
    (surface) => surface.payload.actions.includes('learn')
      && surface.payload.url === course.payload.learner_start_url,
    `${authorityCourse.id}: primary learner surface`,
    true,
  );
  const reader = oneSurface(
    surfaces,
    (surface) => surface.payload.actions.includes('html'),
    `${authorityCourse.id}: dedicated HTML reader`,
  );
  const edition = oneSurface(
    surfaces,
    (surface) => surface.payload.actions.includes('offline'),
    `${authorityCourse.id}: offline edition`,
  );
  const repository = oneSurface(
    surfaces,
    (surface) => surface.payload.actions.includes('repository'),
    `${authorityCourse.id}: repository`,
  );
  const doi = oneSurface(
    surfaces,
    (surface) => surface.payload.actions.includes('doi'),
    `${authorityCourse.id}: DOI`,
  );

  assert.ok(!forbiddenLearner.test(primary.payload.url), `${authorityCourse.id}: learner start points to JSON/backend.`);
  const primarySummary = surfaceSummary(primary);
  if (authorityCourse.state === 'published') {
    assert.equal(primarySummary.effective_publication_state, 'public', `${authorityCourse.id}: published course lacks a public/readback-bound primary surface.`);
  }

  const ui = {
    id: course.payload.course_id,
    ownerLane: course.payload.lane,
    level: course.payload.level,
    topic: course.payload.topic,
    state: course.payload.state,
    title: course.payload.title,
    prerequisites: [...course.payload.prerequisite_course_ids],
    purpose: course.payload.purpose,
    outcome: course.payload.outcome,
    corpus: course.payload.corpus,
    note: course.payload.note,
  };
  if (reader) ui.reader = reader.payload.url;
  if (edition) ui.edition = edition.payload.url;
  if (repository) ui.repository = repository.payload.url;
  if (doi) ui.zenodo = doi.payload.url;
  if (authorityCourse.supplements?.length) ui.supplements = structuredClone(authorityCourse.supplements);

  assert.deepEqual(ui, authorityCourse, `${authorityCourse.id}: v2 projection differs from frozen curriculum authority.`);

  const actionSurfaces = {};
  for (const action of actionOrder) {
    const matches = surfaces.filter((surface) => surface.payload.actions.includes(action));
    if (matches.length) actionSurfaces[action] = matches.map(surfaceSummary);
  }

  return {
    ...ui,
    federation: {
      course_record_id: course.id,
      course_semantic_key: course.semantic_key,
      owner_dataset_id: dataset.id,
      owner_dataset_semantic_key: dataset.semantic_key,
      primary_surface_id: primary.id,
      primary_source_publication_state: primarySummary.source_publication_state,
      primary_effective_publication_state: primarySummary.effective_publication_state,
      primary_readback: primarySummary.readback,
      planned_unit_route_pattern: course.payload.planned_unit_route_pattern,
      unit_route_state: course.payload.unit_route_state,
      web_route_id: course.payload.web_route_id,
      action_surfaces: actionSurfaces,
    },
  };
});

const nextCourseIdsById = Object.fromEntries(projectedCourses.map((course) => [course.id, []]));
for (const course of projectedCourses) {
  for (const prerequisite of course.prerequisites) {
    assert.ok(nextCourseIdsById[prerequisite], `${course.id}: missing prerequisite ${prerequisite}.`);
    nextCourseIdsById[prerequisite].push(course.id);
  }
}
const prerequisiteEdgeCount = Object.values(nextCourseIdsById).reduce((sum, values) => sum + values.length, 0);
assert.equal(
  prerequisiteEdgeCount,
  authority.catalog.program.backend.learnerReadModelV1.prerequisiteEdgeCount,
  'Computed prerequisite-edge count differs from program metadata.',
);

const publishedCourseIds = projectedCourses.filter((course) => course.state === 'published').map((course) => course.id);
assert.deepEqual(publishedCourseIds, authority.catalog.program.completedPublicCourseRoleIds, 'Published course IDs differ from the completed-public authority set.');

const readModel = {
  $schema: 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v1/learner-read-model-v1.schema.json',
  schema_id: 'interlanguage/program-matematika-indonesia-learner-read-model/v1',
  schema_version: '1.0.0',
  locale: 'id-ID',
  provenance: {
    authority_path: 'backend/authority/curriculum-authority-v1.json',
    authority_bytes: authorityBytes.length,
    authority_sha256: sha256(authorityBytes),
    federation_records_path: authority.federation.records_path,
    federation_records_bytes: recordsBytes.length,
    federation_records_sha256: sha256(recordsBytes),
    federation_validation_report_path: authority.federation.validation_report_path,
    federation_validation_report_sha256: sha256(validationBytes),
    federation_validation_result: validation.result,
    readback_overlay_count: authority.public_readback_overlays.length,
  },
  policy: {
    learner_action_order: ['learn', 'html', 'pdf', 'epub', 'offline'],
    technical_action_order: ['source', 'repository', 'doi', 'backend'],
    raw_json_is_learner_start: false,
    internal_workflow_locators_are_public_authority: false,
    source_and_effective_publication_states_are_distinct: true,
  },
  program: authority.catalog.program,
  topics: authority.catalog.topics,
  courses: projectedCourses,
  nextCourseIdsById,
  summary: {
    course_count: projectedCourses.length,
    dataset_count: byType.dataset.length,
    reader_surface_count: byType.reader_surface.length,
    dedicated_html_reader_count: projectedCourses.filter((course) => course.reader).length,
    direct_edition_count: projectedCourses.filter((course) => course.edition).length,
    planned_unit_route_count: projectedCourses.filter((course) => course.federation.unit_route_state === 'planned_not_published').length,
    published_course_count: publishedCourseIds.length,
    effective_public_primary_count: projectedCourses.filter((course) => course.federation.primary_effective_publication_state === 'public').length,
    readback_overlay_count: authority.public_readback_overlays.length,
  },
};

const publicText = JSON.stringify(readModel);
assert.ok(!publicText.includes('codex://'), 'Learner read-model leaks an internal workflow locator.');

const uiCourses = projectedCourses.map(({ federation, ...course }) => course);
const coursesModule = `// Generated by scripts/build-learner-read-model.mjs from the validated v2 federation.\n// Do not edit this file by hand; advance the curriculum authority and rebuild this projection.\n\nexport const courses = Object.freeze(${JSON.stringify(uiCourses, null, 2)});\n\nexport const nextCourseIdsById = Object.freeze(${JSON.stringify(nextCourseIdsById, null, 2)});\n\nexport const topics = Object.freeze(${JSON.stringify(authority.catalog.topics, null, 2)});\n\nexport const program = Object.freeze(${JSON.stringify(authority.catalog.program, null, 2)});\n`;
assert.ok(!coursesModule.includes('codex://'), 'Generated course module leaks an internal workflow locator.');

await Promise.all([
  mkdir(dirname(readModelPath), { recursive: true }),
  mkdir(dirname(coursesPath), { recursive: true }),
  mkdir(dirname(publicAuthorityPath), { recursive: true }),
]);
await Promise.all([
  writeFile(readModelPath, canonical(readModel), 'utf8'),
  writeFile(coursesPath, coursesModule, 'utf8'),
  writeFile(publicAuthorityPath, authorityBytes),
]);

const [writtenModel, writtenCourses, writtenAuthority] = await Promise.all([
  readFile(readModelPath),
  readFile(coursesPath),
  readFile(publicAuthorityPath),
]);
assert.deepEqual(writtenAuthority, authorityBytes, 'Public curriculum-authority copy differs from the canonical authority.');
console.log(`learner_read_model bytes=${writtenModel.length} sha256=${sha256(writtenModel)}`);
console.log(`courses_js bytes=${writtenCourses.length} sha256=${sha256(writtenCourses)}`);
console.log(`public_authority bytes=${writtenAuthority.length} sha256=${sha256(writtenAuthority)}`);
