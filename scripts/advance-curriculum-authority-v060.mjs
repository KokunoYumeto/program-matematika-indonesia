import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const defaultProject = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const version = '0.60.0';
const federationVersion = '0.4.2';
const authorityRelative = 'backend/authority/curriculum-authority-v1.json';
const historyRelative = 'backend/authority/history/curriculum-authority-v0.59.0.json';
const seedRelative = `backend/authority/catalogs/program-matematika-indonesia-catalog-v${version}.json`;

const predecessorIdentity = Object.freeze({
  bytes: 71468,
  sha256: '980ced12bddcddef1eaccb030316e0dafc3dc43079df721c497f7a761f43d5e6',
  version: '0.59.0',
  recordId: 22133203,
});
const admissionIdentity = Object.freeze({
  relativeToWorkspace: 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/118_CENTRAL_V060_ADMISSION_MANIFEST_20260828.json',
  bytes: 4602,
  sha256: '3232d60bf8233a7ab872c615b7d6c59a80a9ccebb915e8ebef01df58acac4aa7',
});
const ownerReaderIdentity = Object.freeze({
  relativeToWorkspace: 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/119_PUBLIC_OWNER_HTML_ROUTE_READBACK_20260828.json',
  bytes: 3788,
  sha256: 'db5c8afdcda4003b841b657635db2ecd3f8859eb5c1efc52cb2607051376ddec',
});
const assessmentIdentity = Object.freeze({
  relativeToProject: 'backend/v2.2/owner-native-shards/o001-a00-assessments-v0.1.0',
  packageId: 'urn:uuid:0b253fa5-067e-55b5-8248-cc528b0b4bd1',
  files: 12,
  bytes: 19057785,
  aggregateSha256: '5d7c3da1a1b3c33b4f79306fec08a31ebc8f557188f1ec0c088e267e0d9ce222',
  manifest: Object.freeze({ path: 'manifest.json', bytes: 3995, sha256: '5ed7b558ae1f621bef52b59be64df90dbf52c967c7e12e2fc9fc296309e2b19e' }),
  checksum: Object.freeze({ path: 'CHECKSUMS.sha256', bytes: 930, sha256: '7d313ed06023a90a28882c25e8942bf9feda270b1c75cbaced38674a1ae9cd57' }),
  seal: Object.freeze({ path: 'seal.json', bytes: 743, sha256: 'a97c1cad9cfbd72fe7bbc44cf59050dc1adbf238d07afdd6337fd0d3c8f74b49' }),
  counts: Object.freeze({
    assessment_components: 13345,
    assessments: 8105,
    modules: 75,
    problems: 8105,
    solution_gaps: 2865,
    solutions: 5240,
  }),
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

function flag(name) {
  return process.argv.includes(name);
}

function workspaceRoot(project) {
  return resolve(project, '../../..');
}

function inputPath(project, cliName, identity) {
  const supplied = optionalOption(cliName);
  if (!supplied) return resolve(workspaceRoot(project), identity.relativeToWorkspace);
  return isAbsolute(supplied) ? resolve(supplied) : resolve(workspaceRoot(project), supplied);
}

async function loadBoundJson(path, identity, label) {
  const bytes = await readFile(path);
  assert.equal(bytes.length, identity.bytes, `${label} byte count changed.`);
  assert.equal(sha256(bytes), identity.sha256, `${label} SHA-256 changed.`);
  return { bytes, value: JSON.parse(bytes.toString('utf8')) };
}

async function listFiles(root, prefix = '') {
  const { readdir } = await import('node:fs/promises');
  const rows = [];
  const entries = await readdir(resolve(root, prefix), { withFileTypes: true });
  entries.sort((left, right) => left.name.localeCompare(right.name, 'en'));
  for (const entry of entries) {
    const portable = prefix ? `${prefix}/${entry.name}` : entry.name;
    if (entry.isDirectory()) rows.push(...await listFiles(root, portable));
    else if (entry.isFile()) rows.push(portable);
  }
  return rows;
}

async function assertAssessmentShard(project) {
  const root = resolve(project, assessmentIdentity.relativeToProject);
  const files = [];
  let totalBytes = 0;
  for (const path of await listFiles(root)) {
    const bytes = await readFile(resolve(root, path));
    totalBytes += bytes.length;
    files.push({ path, bytes: bytes.length, sha256: sha256(bytes) });
  }
  assert.equal(files.length, assessmentIdentity.files);
  assert.equal(totalBytes, assessmentIdentity.bytes);
  const digest = sha256(Buffer.from(files.map((row) => `${row.sha256}  ${row.bytes}  ${row.path}\n`).join(''), 'utf8'));
  assert.equal(digest, assessmentIdentity.aggregateSha256);
  for (const [path, identity] of [
    ['manifest.json', assessmentIdentity.manifest],
    ['CHECKSUMS.sha256', assessmentIdentity.checksum],
    ['seal.json', assessmentIdentity.seal],
  ]) {
    const row = files.find((item) => item.path === path);
    assert.deepEqual(row && { path: row.path, bytes: row.bytes, sha256: row.sha256 }, identity, `${path} identity changed.`);
  }
  const manifest = JSON.parse((await readFile(resolve(root, 'manifest.json'))).toString('utf8'));
  assert.equal(manifest.package_id, assessmentIdentity.packageId);
  assert.deepEqual(manifest.counts, assessmentIdentity.counts);
  assert.equal(manifest.zero_prose_policy.copied_formula_bodies, false);
  assert.equal(manifest.zero_prose_policy.copied_mathematical_prose, false);
  return { root, manifest };
}

function counts() {
  return {
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

function commonOptions() {
  const sourceCommit = option('--source-commit');
  const snapshotDate = option('--snapshot-date');
  assert.match(sourceCommit, /^[0-9a-f]{40}$/);
  assert.match(snapshotDate, /^\d{4}-\d{2}-\d{2}$/);
  return { recordId: integerOption('--record-id'), sourceCommit, snapshotDate, ...counts() };
}

function replaceOne(rows, oldValue, newValue, label) {
  const index = rows.indexOf(oldValue);
  assert.ok(index !== -1, `${label}: predecessor value is missing.`);
  assert.ok(!rows.includes(newValue), `${label}: successor value is already present.`);
  rows[index] = newValue;
}

function assessmentMetadata(recordId) {
  return {
    version: '0.1.0',
    status: 'owner_native_validated_zero_prose',
    roleId: 'O001',
    courseId: 'A00',
    packageId: assessmentIdentity.packageId,
    canonicalPackage: {
      path: assessmentIdentity.relativeToProject,
      fileCount: assessmentIdentity.files,
      bytes: assessmentIdentity.bytes,
      aggregateSha256: assessmentIdentity.aggregateSha256,
      manifest: assessmentIdentity.manifest,
      checksum: assessmentIdentity.checksum,
      seal: assessmentIdentity.seal,
    },
    counts: assessmentIdentity.counts,
    projectionState: 'owner_native_shard_ready_adapter_not_materialized',
    package: `https://zenodo.org/records/${recordId}/files/o001-a00-assessments-v0.1.0.zip?download=1`,
    githubPackage: `https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v${version}/o001-a00-assessments-v0.1.0.zip`,
  };
}

function updateProgram(catalog, options, admission) {
  const program = catalog.program;
  program.version = version;
  program.snapshotDate = options.snapshotDate;
  program.zenodo = `https://doi.org/10.5281/zenodo.${options.recordId}`;
  program.repositories.github.lastConfirmedAt = options.snapshotDate;
  const c110Admission = admission.admissions.find((row) => row.course_id === 'C110');
  assert.ok(c110Admission);
  assert.match(c110Admission.doi, /^10\.5281\/zenodo\.[0-9]+$/);
  replaceOne(program.completedPublicRecordDois, '10.5281/zenodo.22054086', c110Admission.doi, 'C110 complete DOI');

  const backend = program.backend;
  backend.schema = `https://zenodo.org/records/${options.recordId}/files/interlanguage-math-backend-v1.schema.json?download=1`;
  backend.sourceFormatProfile = `https://zenodo.org/records/${options.recordId}/files/interlanguage-source-format-profile-v1.schema.json?download=1`;
  backend.package = `https://zenodo.org/records/${options.recordId}/files/program-matematika-indonesia-backend-v1-v${version}.zip?download=1`;
  backend.federationV2 = {
    ...backend.federationV2,
    version: federationVersion,
    recordCount: options.recordCount,
    datasetCount: options.datasetCount,
    courseCount: options.courseCount,
    learnerSurfaceCount: options.readerSurfaces,
    webRouteCount: options.webRoutes,
    identityCrosswalkCount: options.identityCrosswalks,
    publicationEventCount: options.publicationEvents,
    qaEventCount: options.qaEvents,
    package: `https://zenodo.org/records/${options.recordId}/files/program-matematika-indonesia-backend-v2-v${version}.zip?download=1`,
    packageSchema: `https://zenodo.org/records/${options.recordId}/files/federation-package-v2.schema.json?download=1`,
    recordSchema: `https://zenodo.org/records/${options.recordId}/files/federation-record-v2.schema.json?download=1`,
    validationReceipt: `https://zenodo.org/records/${options.recordId}/files/GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v${version}.json?download=1`,
  };
  backend.federationV21.packageSchema = `https://zenodo.org/records/${options.recordId}/files/federation-unit-package-v2.1.schema.json?download=1`;
  backend.federationV21.recordSchema = `https://zenodo.org/records/${options.recordId}/files/federation-unit-record-v2.1.schema.json?download=1`;
  backend.federationV21.package = `https://zenodo.org/records/${options.recordId}/files/program-matematika-indonesia-backend-v2.1-pilots-v${version}.zip?download=1`;
  backend.federationV22.package = `https://zenodo.org/records/${options.recordId}/files/program-matematika-indonesia-backend-v2.2-v${version}.zip?download=1`;
  backend.federationV22.validationReceipt = `https://zenodo.org/records/${options.recordId}/files/GLOBAL_BACKEND_V22_VALIDATION_RECEIPT_v${version}.json?download=1`;
  backend.federationV22.archiveReceipt = `https://zenodo.org/records/${options.recordId}/files/GLOBAL_BACKEND_V22_ARCHIVE_RECEIPT_v${version}.json?download=1`;
  backend.federationV22.githubPackage = `https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v${version}/program-matematika-indonesia-backend-v2.2-v${version}.zip`;
  backend.federationV22.githubValidationReceipt = `https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v${version}/GLOBAL_BACKEND_V22_VALIDATION_RECEIPT_v${version}.json`;
  backend.federationV22.githubArchiveReceipt = `https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v${version}/GLOBAL_BACKEND_V22_ARCHIVE_RECEIPT_v${version}.json`;
  backend.capabilityContractV1 = {
    version: '0.1.0',
    status: 'schema_validated_federated_zero_copy',
    contract: `https://zenodo.org/records/${options.recordId}/files/global-capability-contract-v0.1.0.json?download=1`,
    schema: `https://zenodo.org/records/${options.recordId}/files/global-capability-contract-v0.1.schema.json?download=1`,
    githubContract: `https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v${version}/global-capability-contract-v0.1.0.json`,
    githubSchema: `https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v${version}/global-capability-contract-v0.1.schema.json`,
  };
  backend.assessmentInventoryV1 = assessmentMetadata(options.recordId);
  backend.educationalAccessResearch.sourcePackage = `https://zenodo.org/records/${options.recordId}/files/program-matematika-indonesia-source-v${version}.zip?download=1`;
  backend.learnerReadModelV1 = {
    ...backend.learnerReadModelV1,
    authority: `https://zenodo.org/records/${options.recordId}/files/curriculum-authority-v1.json?download=1`,
    authoritySchema: `https://zenodo.org/records/${options.recordId}/files/curriculum-authority-v1.schema.json?download=1`,
    readModel: `https://zenodo.org/records/${options.recordId}/files/learner-read-model-v1.json?download=1`,
    readModelSchema: `https://zenodo.org/records/${options.recordId}/files/learner-read-model-v1.schema.json?download=1`,
    validationReceipt: `https://zenodo.org/records/${options.recordId}/files/LOCAL_RELEASE_VALIDATION_v${version}.json?download=1`,
  };
}

function updateCourses(catalog, admission, ownerReaders) {
  const byId = new Map(catalog.courses.map((course) => [course.id, course]));
  const admissions = new Map(admission.admissions.map((row) => [row.course_id, row]));
  const c110 = byId.get('C110');
  const c110Admission = admissions.get('C110');
  c110.edition = c110Admission.learner_route;
  c110.zenodo = `https://doi.org/${c110Admission.doi}`;
  c110.note = 'Selesai dan terverifikasi publik pada versi 3.0-id.2-r1: 31/31 unit dan pembaca 387 halaman. Edisi ini juga merupakan sumber migrasi common-v1 tanpa penyalinan yang tervalidasi.';

  const d40 = byId.get('D40');
  const d40Admission = admissions.get('D40');
  const d40Reader = ownerReaders.routes.find((row) => row.course_id === 'D40');
  assert.ok(d40Reader);
  d40.edition = d40Admission.learner_route;
  d40.zenodo = `https://doi.org/${d40Admission.doi}`;
  d40.reader = d40Reader.url;
  d40.note = 'Checkpoint publik Unit 13 memuat pembaca PDF 193 halaman dan pembaca HTML/MathML 42 halaman yang dimirror dengan 57 berkas identik. Kursus tetap diproduksi.';
}

async function loadInputs(project) {
  const predecessorBytes = await readFile(resolve(project, authorityRelative));
  assert.equal(predecessorBytes.length, predecessorIdentity.bytes, 'Predecessor authority byte count changed.');
  assert.equal(sha256(predecessorBytes), predecessorIdentity.sha256, 'Predecessor authority SHA-256 changed.');
  const predecessor = JSON.parse(predecessorBytes.toString('utf8'));
  assert.equal(predecessor.catalog.program.version, predecessorIdentity.version);
  assert.equal(predecessor.catalog.program.zenodo, `https://doi.org/10.5281/zenodo.${predecessorIdentity.recordId}`);
  const admission = await loadBoundJson(inputPath(project, '--admission-manifest', admissionIdentity), admissionIdentity, 'Admission manifest');
  const readers = await loadBoundJson(inputPath(project, '--owner-reader-manifest', ownerReaderIdentity), ownerReaderIdentity, 'Owner-reader manifest');
  assert.equal(admission.value.target_release, version);
  assert.equal(admission.value.summary.refreshed_course_routes, 2);
  assert.equal(readers.value.result, 'pass');
  assert.equal(readers.value.route_count, 7);
  await assertAssessmentShard(project);
  return { predecessor, predecessorBytes, admission: admission.value, readers: readers.value };
}

function buildCatalog(predecessor, admission, readers, options) {
  const catalog = structuredClone(predecessor.catalog);
  updateProgram(catalog, options, admission);
  updateCourses(catalog, admission, readers);
  assert.ok(catalog.program.completedPublicRecordDois.includes(catalog.courses.find((course) => course.id === 'C110').zenodo.replace('https://doi.org/', '')));
  catalog.$schema = `https://zenodo.org/records/${options.recordId}/files/program-matematika-indonesia-catalog-v1.schema.json`;
  catalog.snapshotDate = options.snapshotDate;
  catalog.sourceCommit = options.sourceCommit;
  assert.equal(catalog.counts.completedPublicCourseRoles, 19);
  assert.equal(catalog.counts.completedPublicRecords, 18);
  assert.equal(catalog.courses.length, 40);
  return catalog;
}

async function seed(project) {
  const options = commonOptions();
  const { predecessor, admission, readers } = await loadInputs(project);
  const catalog = buildCatalog(predecessor, admission, readers, options);
  const bytes = canonical(catalog);
  if (!flag('--dry-run')) {
    await mkdir(dirname(resolve(project, seedRelative)), { recursive: true });
    await writeFile(resolve(project, seedRelative), bytes);
  }
  console.log(JSON.stringify({ mode: 'seed', dry_run: flag('--dry-run'), path: seedRelative, bytes: bytes.length, sha256: sha256(bytes) }, null, 2));
}

function portableRelative(project, value, name) {
  const normalized = value.replaceAll('\\', '/');
  const segments = normalized.split('/');
  assert.ok(normalized && normalized !== '.', `${name} must not be empty or dot.`);
  assert.ok(!isAbsolute(value) && !normalized.includes(':'), `${name} must be project-relative.`);
  assert.ok(segments.every((segment) => segment && segment !== '.' && segment !== '..'), `${name} contains an unsafe path segment.`);
  const resolved = resolve(project, normalized);
  const fromProject = relative(project, resolved).replaceAll('\\', '/');
  assert.ok(fromProject === normalized && !fromProject.startsWith('../'), `${name} escapes the project root.`);
  return normalized;
}

function parseRecords(bytes) {
  const text = bytes.toString('utf8').trimEnd();
  return text ? text.split('\n').map(JSON.parse) : [];
}

function findSurface(records, courseId, url, action) {
  const candidates = records.filter((record) => record.record_type === 'reader_surface'
    && record.payload.url === url
    && record.payload.course_ids.includes(courseId)
    && record.payload.actions.includes(action));
  assert.equal(candidates.length, 1, `${courseId}: expected exactly one ${action} surface for ${url}.`);
  return candidates[0];
}

async function promote(project) {
  const options = commonOptions();
  const federationRelative = portableRelative(project, option('--federation-relative'), '--federation-relative');
  const { predecessor, predecessorBytes, admission, readers } = await loadInputs(project);
  const seedBytes = await readFile(resolve(project, seedRelative));
  const catalog = JSON.parse(seedBytes.toString('utf8'));
  assert.deepEqual(catalog, buildCatalog(predecessor, admission, readers, options), 'Seed catalog differs from deterministic transition output.');

  const recordsRelative = `${federationRelative}/records.jsonl`;
  const manifestRelative = `${federationRelative}/manifest.json`;
  const validationRelative = `${federationRelative}/validation_report.json`;
  const [recordsBytes, manifestBytes, validationBytes] = await Promise.all([
    readFile(resolve(project, recordsRelative)),
    readFile(resolve(project, manifestRelative)),
    readFile(resolve(project, validationRelative)),
  ]);
  const manifest = JSON.parse(manifestBytes.toString('utf8'));
  const validation = JSON.parse(validationBytes.toString('utf8'));
  assert.equal(manifest.dataset_version, `program-matematika-indonesia-federation-v${federationVersion}`);
  assert.equal(validation.result, 'pass');
  assert.equal(manifest.record_count, options.recordCount);
  const expected = {
    datasets: options.datasetCount,
    courses: options.courseCount,
    reader_surfaces: options.readerSurfaces,
    web_routes: options.webRoutes,
    identity_crosswalks: options.identityCrosswalks,
    publication_events: options.publicationEvents,
    qa_events: options.qaEvents,
  };
  for (const [key, value] of Object.entries(expected)) assert.equal(manifest.record_counts[key], value, `${key} count differs.`);
  const records = parseRecords(recordsBytes);
  assert.equal(records.length, options.recordCount);

  const admissionById = new Map(admission.admissions.map((row) => [row.course_id, row]));
  const c110 = admissionById.get('C110');
  const d40 = admissionById.get('D40');
  const d40Reader = readers.routes.find((row) => row.course_id === 'D40');
  const surfaceFacts = [
    {
      courseId: 'C110', url: c110.learner_route, action: 'learn', bytes: c110.primary_artifact.bytes,
      digest: c110.primary_artifact.sha256, evidenceSha: admissionIdentity.sha256,
    },
    {
      courseId: 'D40', url: d40.learner_route, action: 'pdf', bytes: d40.primary_artifact.bytes,
      digest: d40.primary_artifact.sha256, evidenceSha: admissionIdentity.sha256,
    },
    {
      courseId: 'D40', url: d40Reader.url, action: 'html', bytes: d40Reader.bytes,
      digest: d40Reader.sha256, evidenceSha: ownerReaderIdentity.sha256,
    },
  ];
  const newOverlays = surfaceFacts.map((fact) => {
    const surface = findSurface(records, fact.courseId, fact.url, fact.action);
    return {
      course_id: fact.courseId,
      surface_id: surface.id,
      url: fact.url,
      source_publication_state: surface.payload.publication_state,
      effective_publication_state: 'public',
      evidence_kind: 'anonymous_public_byte_readback',
      bytes: fact.bytes,
      sha256: fact.digest,
      verified_at: new Date(fact.action === 'html' ? readers.recorded_at : admission.recorded_at).toISOString(),
      evidence_sha256: fact.evidenceSha,
    };
  });
  assert.equal(new Set(newOverlays.map((row) => row.surface_id)).size, 3);

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
  authority.catalog = catalog;
  authority.lineage = {
    bootstrap_release_version: predecessor.lineage.bootstrap_release_version,
    predecessor_authority: { path: historyRelative, bytes: predecessorBytes.length, sha256: sha256(predecessorBytes) },
    transition: {
      from_version: predecessorIdentity.version,
      to_version: version,
      snapshot_date: options.snapshotDate,
      zenodo_record_id: options.recordId,
      method: 'verified_owner_successor_admission_d40_html_reader_and_o001_assessment_inventory',
    },
  };
  authority.public_readback_overlays = [...predecessor.public_readback_overlays, ...newOverlays];
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
    new_overlays: newOverlays.length, total_overlays: authority.public_readback_overlays.length,
    candidate_output: candidateRelative,
  }, null, 2));
}

const mode = process.argv[2];
const project = resolve(optionalOption('--project-root') ?? defaultProject);
if (mode === 'seed') await seed(project);
else if (mode === 'promote') await promote(project);
else throw new Error('Usage: node scripts/advance-curriculum-authority-v060.mjs <seed|promote> --record-id N --source-commit SHA --snapshot-date YYYY-MM-DD --record-count N --dataset-count N --course-count N --reader-surfaces N --web-routes N --identity-crosswalks N --publication-events N --qa-events N [--federation-relative PATH] [--candidate-output PATH] [--admission-manifest PATH] [--owner-reader-manifest PATH] [--project-root PATH] [--dry-run]');
