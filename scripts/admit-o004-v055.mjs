import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const authorityRelative = 'backend/authority/curriculum-authority-v1.json';
const historyRelative = 'backend/authority/history/curriculum-authority-v0.54.0.json';
const changeRelative = 'backend/authority/changes/o004-c100-complete-20260825.json';
const seedRelative = 'backend/authority/catalogs/program-matematika-indonesia-catalog-v0.55.0.json';
const version = '0.55.0';
const federationVersion = '0.3.0';
const expectedAuthority = {
  bytes: 52712,
  sha256: '23f8ecd0211fd1963dc6974ea9772df27011761b76e6e2447574cbece1d3ab17',
};

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');

function option(name) {
  const index = process.argv.indexOf(name);
  if (index === -1 || !process.argv[index + 1]) throw new Error(`Missing required option ${name}.`);
  return process.argv[index + 1];
}

function requireRecordId(value) {
  assert.match(value, /^\d+$/, 'Zenodo record ID must be numeric.');
  return Number(value);
}

async function loadJson(relative) {
  return JSON.parse((await readFile(resolve(project, relative))).toString('utf8'));
}

async function readCurrentAuthority() {
  const bytes = await readFile(resolve(project, authorityRelative));
  assert.equal(bytes.length, expectedAuthority.bytes, 'Unexpected predecessor authority byte count.');
  assert.equal(sha256(bytes), expectedAuthority.sha256, 'Unexpected predecessor authority SHA-256.');
  const authority = JSON.parse(bytes.toString('utf8'));
  assert.equal(authority.catalog.program.version, '0.54.0');
  return { authority, bytes };
}

function applyCourseChange(catalog, change, recordId, sourceCommit, snapshotDate) {
  const course = catalog.courses.find(({ id }) => id === change.course_id);
  assert.ok(course, 'C100 is absent from the predecessor catalog.');
  assert.equal(course.ownerLane, change.owner_lane);
  assert.equal(course.state, change.predecessor.expected_course_state);
  assert.equal(course.edition, undefined);
  assert.equal(course.zenodo, undefined);
  Object.assign(course, change.course_update);

  const program = catalog.program;
  program.version = version;
  program.snapshotDate = snapshotDate;
  program.zenodo = `https://doi.org/10.5281/zenodo.${recordId}`;
  program.completedPublicCourseRoleIds = catalog.courses
    .filter(({ state }) => state === 'published')
    .map(({ id }) => id);
  program.completedPublicRecordDois = [
    ...program.completedPublicRecordDois.filter((doi) => doi !== change.public_evidence.doi),
    change.public_evidence.doi,
  ];
  program.backend.schema =
    `https://zenodo.org/records/${recordId}/files/interlanguage-math-backend-v1.schema.json?download=1`;
  program.backend.sourceFormatProfile =
    `https://zenodo.org/records/${recordId}/files/interlanguage-source-format-profile-v1.schema.json?download=1`;
  program.backend.package =
    `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-backend-v1-v${version}.zip?download=1`;
  Object.assign(program.backend.federationV2, {
    version: federationVersion,
    status: 'validated',
    recordCount: 2434,
    datasetCount: 34,
    courseCount: 40,
    learnerSurfaceCount: 128,
    webRouteCount: 41,
    identityCrosswalkCount: 2122,
    package:
      `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-backend-v2-v${version}.zip?download=1`,
    packageSchema:
      `https://zenodo.org/records/${recordId}/files/federation-package-v2.schema.json?download=1`,
    recordSchema:
      `https://zenodo.org/records/${recordId}/files/federation-record-v2.schema.json?download=1`,
    validationReceipt:
      `https://zenodo.org/records/${recordId}/files/GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v${version}.json?download=1`,
  });
  Object.assign(program.backend.learnerReadModelV1, {
    courseCount: 40,
    prerequisiteEdgeCount: 82,
    authority:
      `https://zenodo.org/records/${recordId}/files/curriculum-authority-v1.json?download=1`,
    authoritySchema:
      `https://zenodo.org/records/${recordId}/files/curriculum-authority-v1.schema.json?download=1`,
    readModel:
      `https://zenodo.org/records/${recordId}/files/learner-read-model-v1.json?download=1`,
    readModelSchema:
      `https://zenodo.org/records/${recordId}/files/learner-read-model-v1.schema.json?download=1`,
    validationReceipt:
      `https://zenodo.org/records/${recordId}/files/LOCAL_RELEASE_VALIDATION_v${version}.json?download=1`,
  });
  catalog.$schema =
    `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-catalog-v1.schema.json`;
  catalog.snapshotDate = snapshotDate;
  catalog.sourceCommit = sourceCommit;
  catalog.counts = {
    courseRoles: catalog.courses.length,
    selectedCorpusRoles: catalog.courses.filter(({ state }) => state !== 'unresolved').length,
    unresolvedRoles: catalog.courses.filter(({ state }) => state === 'unresolved').length,
    completedPublicCourseRoles: program.completedPublicCourseRoleIds.length,
    completedPublicRecords: program.completedPublicRecordDois.length,
  };
  assert.equal(catalog.counts.completedPublicCourseRoles, 17);
  assert.equal(catalog.counts.completedPublicRecords, 16);
  return catalog;
}

async function seed() {
  const recordId = requireRecordId(option('--record-id'));
  const sourceCommit = option('--source-commit');
  const snapshotDate = option('--snapshot-date');
  assert.match(sourceCommit, /^[0-9a-f]{40}$/);
  assert.match(snapshotDate, /^\d{4}-\d{2}-\d{2}$/);
  const { authority } = await readCurrentAuthority();
  const change = await loadJson(changeRelative);
  assert.equal(change.central_transition.reserved_zenodo_record_id, recordId);
  const catalog = applyCourseChange(
    structuredClone(authority.catalog),
    change,
    recordId,
    sourceCommit,
    snapshotDate,
  );
  const output = resolve(project, seedRelative);
  await mkdir(dirname(output), { recursive: true });
  const bytes = canonical(catalog);
  await writeFile(output, bytes);
  console.log(JSON.stringify({
    mode: 'seed',
    output: seedRelative,
    bytes: bytes.length,
    sha256: sha256(bytes),
    completed_public_course_roles: catalog.counts.completedPublicCourseRoles,
    completed_public_records: catalog.counts.completedPublicRecords,
  }, null, 2));
}

async function promote() {
  const recordId = requireRecordId(option('--record-id'));
  const snapshotDate = option('--snapshot-date');
  const readbackAt = option('--readback-at');
  const federationRelative = option('--federation-relative').replaceAll('\\', '/');
  assert.match(snapshotDate, /^\d{4}-\d{2}-\d{2}$/);
  assert.match(readbackAt, /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/);
  assert.ok(!federationRelative.startsWith('/') && !federationRelative.includes('..'));

  const { authority: predecessor, bytes: predecessorBytes } = await readCurrentAuthority();
  const seedBytes = await readFile(resolve(project, seedRelative));
  const seedCatalog = JSON.parse(seedBytes.toString('utf8'));
  assert.equal(seedCatalog.program.version, version);
  assert.equal(seedCatalog.program.zenodo, `https://doi.org/10.5281/zenodo.${recordId}`);

  const recordsRelative = `${federationRelative}/records.jsonl`;
  const validationRelative = `${federationRelative}/validation_report.json`;
  const manifestRelative = `${federationRelative}/manifest.json`;
  const recordsBytes = await readFile(resolve(project, recordsRelative));
  const validationBytes = await readFile(resolve(project, validationRelative));
  const manifest = await loadJson(manifestRelative);
  const validation = JSON.parse(validationBytes.toString('utf8'));
  assert.equal(validation.result, 'pass');
  assert.equal(manifest.dataset_version, `program-matematika-indonesia-federation-v${federationVersion}`);
  assert.equal(manifest.record_count, 2434);
  assert.equal(manifest.record_counts.reader_surfaces, 128);
  assert.equal(manifest.record_counts.publication_events, 52);

  const records = recordsBytes.toString('utf8').trim().split('\n').map(JSON.parse);
  const change = await loadJson(changeRelative);
  const primary = records.find((record) =>
    record.record_type === 'reader_surface'
      && record.payload.url === change.primary_learner_surface.url
      && record.payload.course_ids.includes(change.course_id)
      && record.payload.actions.includes('learn')
  );
  assert.ok(primary, 'The O004 primary PDF surface is absent from the new federation.');
  assert.equal(primary.payload.publication_state, 'catalog_declared');

  const historyPath = resolve(project, historyRelative);
  await mkdir(dirname(historyPath), { recursive: true });
  await writeFile(historyPath, predecessorBytes);

  const authority = structuredClone(predecessor);
  authority.seed_catalog = {
    path: seedRelative,
    bytes: seedBytes.length,
    sha256: sha256(seedBytes),
  };
  authority.federation = {
    package_path: federationRelative,
    records_path: recordsRelative,
    records_bytes: recordsBytes.length,
    records_sha256: sha256(recordsBytes),
    validation_report_path: validationRelative,
    validation_report_bytes: validationBytes.length,
    validation_report_sha256: sha256(validationBytes),
    validation_result: validation.result,
  };
  authority.catalog = seedCatalog;
  authority.lineage = {
    bootstrap_release_version: '0.53.0',
    predecessor_authority: {
      path: historyRelative,
      bytes: predecessorBytes.length,
      sha256: sha256(predecessorBytes),
    },
    transition: {
      from_version: '0.54.0',
      to_version: version,
      snapshot_date: snapshotDate,
      zenodo_record_id: recordId,
      method: 'controlled_owner_handoff_admission_with_hash_bound_public_readback',
    },
  };
  authority.public_readback_overlays = [
    ...predecessor.public_readback_overlays,
    {
      course_id: change.course_id,
      surface_id: primary.id,
      url: change.primary_learner_surface.url,
      source_publication_state: primary.payload.publication_state,
      effective_publication_state: 'public',
      evidence_kind: 'anonymous_public_byte_readback',
      bytes: change.primary_learner_surface.bytes,
      sha256: change.primary_learner_surface.sha256,
      verified_at: readbackAt,
    },
  ];
  assert.equal(new Set(authority.public_readback_overlays.map(({ surface_id }) => surface_id)).size,
    authority.public_readback_overlays.length);

  const outputBytes = canonical(authority);
  await writeFile(resolve(project, authorityRelative), outputBytes);
  console.log(JSON.stringify({
    mode: 'promote',
    output: authorityRelative,
    bytes: outputBytes.length,
    sha256: sha256(outputBytes),
    predecessor: historyRelative,
    federation: federationRelative,
    o004_primary_surface_id: primary.id,
    overlays: authority.public_readback_overlays.length,
  }, null, 2));
}

const mode = process.argv[2];
if (mode === 'seed') {
  await seed();
} else if (mode === 'promote') {
  await promote();
} else {
  throw new Error('Usage: node scripts/admit-o004-v055.mjs seed|promote [options]');
}
