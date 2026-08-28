import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const defaultProject = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const version = '0.61.0';
const federationVersion = '0.4.3';
const authorityRelative = 'backend/authority/curriculum-authority-v1.json';
const historyRelative = 'backend/authority/history/curriculum-authority-v0.60.0.json';
const seedRelative = `backend/authority/catalogs/program-matematika-indonesia-catalog-v${version}.json`;

const predecessorIdentity = Object.freeze({
  bytes: 75653,
  sha256: '974749cf2890dc841d933e07ce453a09fdc5746a07383d61d48d178f8ed38a73',
  version: '0.60.0',
  recordId: 22143506,
});
const admissionIdentity = Object.freeze({
  relativeToWorkspace: 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/130_CENTRAL_V061_ADMISSION_MANIFEST_20260828.json',
  bytes: 3224,
  sha256: 'f74ae06959e2b1da2a32ad302fdd5fad822c4cc5d711c858669f865628ab8013',
});
const ownerReaderIdentity = Object.freeze({
  relativeToWorkspace: 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/131_PUBLIC_OWNER_HTML_ROUTE_READBACK_20260828.json',
  bytes: 3893,
  sha256: '8a358848050523fd39df24afdb2bcbb8e38a0218490073c73dab4ac82108d57a',
});
const reservationIdentity = Object.freeze({
  relativeToWorkspace: 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/129_CENTRAL_V061_ZENODO_DRAFT_RESERVATION_20260828.json',
  bytes: 1440,
  sha256: 'c6a1c1f22e37340157126abe2e354929c1a5668e54e29bfc1f9d2d45fc613f40',
});

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');

function optionalOption(name) {
  const index = process.argv.indexOf(name);
  return index === -1 ? null : process.argv[index + 1] ?? null;
}

function option(name) {
  const value = optionalOption(name);
  if (!value) throw new Error(`Missing required option ${name}.`);
  return value;
}

function integerOption(name) {
  const value = Number(option(name));
  assert.ok(Number.isInteger(value) && value > 0, `${name} must be a positive integer.`);
  return value;
}

function flag(name) { return process.argv.includes(name); }
function workspaceRoot(project) { return resolve(project, '../../..'); }

function inputPath(project, identity) {
  return resolve(workspaceRoot(project), identity.relativeToWorkspace);
}

async function loadBoundJson(project, identity, label) {
  const path = inputPath(project, identity);
  const bytes = await readFile(path);
  assert.equal(bytes.length, identity.bytes, `${label} byte count changed.`);
  assert.equal(sha256(bytes), identity.sha256, `${label} SHA-256 changed.`);
  return { path, bytes, value: JSON.parse(bytes.toString('utf8')) };
}

function commonOptions() {
  const sourceCommit = option('--source-commit');
  const snapshotDate = option('--snapshot-date');
  assert.match(sourceCommit, /^[0-9a-f]{40}$/);
  assert.match(snapshotDate, /^\d{4}-\d{2}-\d{2}$/);
  return {
    recordId: integerOption('--record-id'), sourceCommit, snapshotDate,
    recordCount: integerOption('--record-count'),
    datasetCount: integerOption('--dataset-count'),
    courseCount: integerOption('--course-count'),
    readerSurfaces: integerOption('--reader-surfaces'),
    webRoutes: integerOption('--web-routes'),
    identityCrosswalks: integerOption('--identity-crosswalks'),
    publicationEvents: integerOption('--publication-events'),
    qaEvents: integerOption('--qa-events'),
  };
}

function rewriteCentralReleaseUrls(value, recordId) {
  if (typeof value === 'string') {
    return value
      .replaceAll('22143506', String(recordId))
      .replaceAll('v0.60.0', `v${version}`);
  }
  if (Array.isArray(value)) return value.map((item) => rewriteCentralReleaseUrls(item, recordId));
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, rewriteCentralReleaseUrls(item, recordId)]));
  }
  return value;
}

function buildCatalog(predecessor, admission, options) {
  const catalog = structuredClone(predecessor.catalog);
  catalog.program = rewriteCentralReleaseUrls(catalog.program, options.recordId);
  catalog.program.version = version;
  catalog.program.snapshotDate = options.snapshotDate;
  catalog.program.zenodo = `https://doi.org/10.5281/zenodo.${options.recordId}`;
  catalog.program.repositories.github.lastConfirmedAt = options.snapshotDate;
  catalog.program.backend.federationV2.version = federationVersion;
  catalog.program.backend.federationV2.recordCount = options.recordCount;
  catalog.program.backend.federationV2.datasetCount = options.datasetCount;
  catalog.program.backend.federationV2.courseCount = options.courseCount;
  catalog.program.backend.federationV2.learnerSurfaceCount = options.readerSurfaces;
  catalog.program.backend.federationV2.webRouteCount = options.webRoutes;
  catalog.program.backend.federationV2.identityCrosswalkCount = options.identityCrosswalks;
  catalog.program.backend.federationV2.publicationEventCount = options.publicationEvents;
  catalog.program.backend.federationV2.qaEventCount = options.qaEvents;

  const d60Admission = admission.admissions.find((row) => row.course_id === 'D60');
  assert.ok(d60Admission);
  const d60 = catalog.courses.find((course) => course.id === 'D60');
  assert.ok(d60);
  d60.edition = `https://zenodo.org/records/${d60Admission.record}/files/${d60Admission.pdf_artifact.path}?download=1`;
  d60.zenodo = `https://doi.org/${d60Admission.doi}`;
  d60.reader = d60Admission.learner_route;
  d60.note = 'Checkpoint publik v0.31.4 memuat Roberts 30/30, Fomberg §§1.1–1.13, penguasaan wajib 108/108, dan laboratorium komputasi 2/4. Laboratorium 3–4, penutupan metadata bukti, dan capstone masih diproduksi.';

  catalog.$schema = `https://zenodo.org/records/${options.recordId}/files/program-matematika-indonesia-catalog-v1.schema.json`;
  catalog.snapshotDate = options.snapshotDate;
  catalog.sourceCommit = options.sourceCommit;
  assert.equal(catalog.counts.completedPublicCourseRoles, 19);
  assert.equal(catalog.counts.completedPublicRecords, 18);
  assert.equal(catalog.courses.length, 40);
  return catalog;
}

async function loadInputs(project) {
  let predecessorBytes = await readFile(resolve(project, authorityRelative));
  if (predecessorBytes.length !== predecessorIdentity.bytes || sha256(predecessorBytes) !== predecessorIdentity.sha256) {
    const live = JSON.parse(predecessorBytes.toString('utf8'));
    assert.equal(live.catalog?.program?.version, version, 'Live authority is neither the bound predecessor nor this transition output.');
    predecessorBytes = await readFile(resolve(project, historyRelative));
  }
  assert.equal(predecessorBytes.length, predecessorIdentity.bytes, 'Predecessor authority byte count changed.');
  assert.equal(sha256(predecessorBytes), predecessorIdentity.sha256, 'Predecessor authority SHA-256 changed.');
  const predecessor = JSON.parse(predecessorBytes.toString('utf8'));
  assert.equal(predecessor.catalog.program.version, predecessorIdentity.version);
  assert.equal(predecessor.catalog.program.zenodo, `https://doi.org/10.5281/zenodo.${predecessorIdentity.recordId}`);

  const admission = await loadBoundJson(project, admissionIdentity, 'Admission manifest');
  const readers = await loadBoundJson(project, ownerReaderIdentity, 'Owner-reader manifest');
  const reservation = await loadBoundJson(project, reservationIdentity, 'Zenodo reservation');
  assert.equal(admission.value.target_release, version);
  assert.equal(admission.value.admissions.length, 1);
  assert.equal(admission.value.admissions[0].course_id, 'D60');
  assert.equal(readers.value.result, 'pass');
  assert.equal(readers.value.route_count, 7);
  assert.equal(reservation.value.program_version, version);
  assert.equal(reservation.value.reserved_version.draft_record_id, 22148050);
  return { predecessor, predecessorBytes, admission: admission.value, readers: readers.value, reservation: reservation.value };
}

async function seed(project) {
  const options = commonOptions();
  const { predecessor, admission, reservation } = await loadInputs(project);
  assert.equal(options.recordId, reservation.reserved_version.draft_record_id);
  const bytes = canonical(buildCatalog(predecessor, admission, options));
  if (!flag('--dry-run')) {
    await mkdir(dirname(resolve(project, seedRelative)), { recursive: true });
    await writeFile(resolve(project, seedRelative), bytes);
  }
  console.log(JSON.stringify({ mode: 'seed', dry_run: flag('--dry-run'), path: seedRelative, bytes: bytes.length, sha256: sha256(bytes) }, null, 2));
}

function portableRelative(project, value, name) {
  const normalized = value.replaceAll('\\', '/');
  const segments = normalized.split('/');
  assert.ok(normalized && normalized !== '.' && !isAbsolute(value) && !normalized.includes(':'), `${name} must be project-relative.`);
  assert.ok(segments.every((segment) => segment && segment !== '.' && segment !== '..'), `${name} contains an unsafe segment.`);
  const resolved = resolve(project, normalized);
  assert.equal(relative(project, resolved).replaceAll('\\', '/'), normalized, `${name} escapes the project root.`);
  return normalized;
}

function parseRecords(bytes) {
  const text = bytes.toString('utf8').trimEnd();
  return text ? text.split('\n').map(JSON.parse) : [];
}

async function promote(project) {
  const options = commonOptions();
  const federationRelative = portableRelative(project, option('--federation-relative'), '--federation-relative');
  const { predecessor, predecessorBytes, admission, readers, reservation } = await loadInputs(project);
  assert.equal(options.recordId, reservation.reserved_version.draft_record_id);
  const seedBytes = await readFile(resolve(project, seedRelative));
  assert.deepEqual(JSON.parse(seedBytes.toString('utf8')), buildCatalog(predecessor, admission, options), 'Seed catalog differs from deterministic transition output.');

  const recordsRelative = `${federationRelative}/records.jsonl`;
  const validationRelative = `${federationRelative}/validation_report.json`;
  const [recordsBytes, manifestBytes, validationBytes] = await Promise.all([
    readFile(resolve(project, recordsRelative)),
    readFile(resolve(project, `${federationRelative}/manifest.json`)),
    readFile(resolve(project, validationRelative)),
  ]);
  const manifest = JSON.parse(manifestBytes);
  const validation = JSON.parse(validationBytes);
  assert.equal(manifest.dataset_version, `program-matematika-indonesia-federation-v${federationVersion}`);
  assert.equal(validation.result, 'pass');
  assert.equal(manifest.record_count, options.recordCount);
  const expectedCounts = {
    datasets: options.datasetCount, courses: options.courseCount, reader_surfaces: options.readerSurfaces,
    web_routes: options.webRoutes, identity_crosswalks: options.identityCrosswalks,
    publication_events: options.publicationEvents, qa_events: options.qaEvents,
  };
  for (const [key, value] of Object.entries(expectedCounts)) assert.equal(manifest.record_counts[key], value, `${key} count differs.`);

  const d60Reader = readers.routes.find((row) => row.course_id === 'D60');
  assert.ok(d60Reader);
  const surfaces = parseRecords(recordsBytes).filter((record) => record.record_type === 'reader_surface'
    && record.payload.url === d60Reader.url
    && record.payload.course_ids.includes('D60')
    && record.payload.actions.includes('html'));
  assert.equal(surfaces.length, 1, 'Expected exactly one D60 HTML reader surface.');
  const overlay = {
    course_id: 'D60',
    surface_id: surfaces[0].id,
    url: d60Reader.url,
    source_publication_state: surfaces[0].payload.publication_state,
    effective_publication_state: 'public',
    evidence_kind: 'anonymous_public_byte_readback',
    bytes: d60Reader.bytes,
    sha256: d60Reader.sha256,
    verified_at: new Date(readers.recorded_at).toISOString(),
    evidence_sha256: ownerReaderIdentity.sha256,
  };

  const authority = structuredClone(predecessor);
  authority.seed_catalog = { path: seedRelative, bytes: seedBytes.length, sha256: sha256(seedBytes) };
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
  authority.catalog = JSON.parse(seedBytes.toString('utf8'));
  authority.lineage = {
    bootstrap_release_version: predecessor.lineage.bootstrap_release_version,
    predecessor_authority: { path: historyRelative, bytes: predecessorBytes.length, sha256: sha256(predecessorBytes) },
    transition: {
      from_version: predecessorIdentity.version,
      to_version: version,
      snapshot_date: options.snapshotDate,
      zenodo_record_id: options.recordId,
      method: 'verified_d60_mastery_complete_two_lab_checkpoint_and_student_reader_admission',
    },
  };
  authority.public_readback_overlays = [...predecessor.public_readback_overlays, overlay];
  assert.equal(new Set(authority.public_readback_overlays.map((row) => row.surface_id)).size, authority.public_readback_overlays.length);

  const outputBytes = canonical(authority);
  const candidateOption = optionalOption('--candidate-output');
  let candidateRelative = null;
  if (candidateOption) {
    candidateRelative = portableRelative(project, candidateOption, '--candidate-output');
    await mkdir(dirname(resolve(project, candidateRelative)), { recursive: true });
    await writeFile(resolve(project, candidateRelative), outputBytes);
  }
  if (!flag('--dry-run')) {
    await mkdir(dirname(resolve(project, historyRelative)), { recursive: true });
    await writeFile(resolve(project, historyRelative), predecessorBytes);
    await writeFile(resolve(project, authorityRelative), outputBytes);
  }
  console.log(JSON.stringify({
    mode: 'promote', dry_run: flag('--dry-run'), path: authorityRelative,
    bytes: outputBytes.length, sha256: sha256(outputBytes), federation: federationRelative,
    new_overlays: 1, total_overlays: authority.public_readback_overlays.length,
    candidate_output: candidateRelative,
  }, null, 2));
}

const mode = process.argv[2];
const project = resolve(optionalOption('--project-root') ?? defaultProject);
if (mode === 'seed') await seed(project);
else if (mode === 'promote') await promote(project);
else throw new Error('Usage: node scripts/advance-curriculum-authority-v061.mjs <seed|promote> --record-id N --source-commit SHA --snapshot-date YYYY-MM-DD --record-count N --dataset-count N --course-count N --reader-surfaces N --web-routes N --identity-crosswalks N --publication-events N --qa-events N [--federation-relative PATH] [--candidate-output PATH] [--project-root PATH] [--dry-run]');
