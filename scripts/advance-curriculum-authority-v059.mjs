import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const defaultProject = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const version = '0.59.0';
const federationVersion = '0.4.1';
const authorityRelative = 'backend/authority/curriculum-authority-v1.json';
const historyRelative = 'backend/authority/history/curriculum-authority-v0.58.0.json';
const seedRelative = `backend/authority/catalogs/program-matematika-indonesia-catalog-v${version}.json`;
const transitionMethod = 'owner_publication_refresh_hash_bound_learner_routes_and_complete_course_admission';

const predecessorIdentity = Object.freeze({
  bytes: 63118,
  sha256: '8b7b948c9a1b410ab48ee6829b148da7179d78e7cfb4d45b71fdaf4a7c272e61',
  version: '0.58.0',
  recordId: 22105611,
});

const admissionIdentity = Object.freeze({
  relativeToWorkspace: 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/113_CENTRAL_V059_ADMISSION_MANIFEST_20260827.json',
  bytes: 11284,
  sha256: 'e32049ef5fdeac98d784e5813b58cd1ff1826acd83a1a41d17db63f397b56a8c',
});

const ownerReaderIdentity = Object.freeze({
  relativeToWorkspace: 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/114_PUBLIC_OWNER_HTML_ROUTE_READBACK_20260827.json',
  bytes: 3369,
  sha256: 'e16d1a28ad973593edf44dfbce081f636cd3df4febdd097c0b29cd8eed5ed04e',
});

const v22Identity = Object.freeze({
  relativeToProject: 'backend/v2.2/packages/a00-openstax-prealgebra-v0.1.0',
  packageId: 'urn:uuid:023b0035-f385-5188-920b-2130aa61f815',
  fileCount: 36,
  packageBytes: 1720752,
  manifest: Object.freeze({
    path: 'manifest.json',
    bytes: 27131,
    sha256: 'b196d0b851fa0f6b3b7972ab33b762898f3d577fbc26b6214542d6a5b10009af',
  }),
  validationReport: Object.freeze({
    path: 'validation-report.json',
    bytes: 3515,
    sha256: '13a82463853bc8fc6705cd9fb95a23647679bd5bc945a3f2358e243a7bd9c918',
  }),
  seal: Object.freeze({
    path: 'seal.json',
    bytes: 6805,
    sha256: 'fb0696a3f38509468076c4fff374106127e092f3b70b4c1536f7c611009dc855',
    sealedFileCount: 35,
    sealedBytes: 1713947,
    sealedDigestSha256: '49c4272f2b48f311429575814bf23acef02bcd9f5e96033b2d618be88678a9e8',
  }),
  nativeRecordsReferenced: 519678,
  nativeRecordsCopied: 0,
  nativeViews: 17,
  projectedRecords: 1313,
  recordTables: 19,
  visibleUnits: 75,
  learnerRoutes: 75,
  identityMapRows: 92,
  replayRuns: 2,
  replaySha256: '8a2bf0eb8cc68f538867695d5d7d88cbf5874751576ee304e1328f3e4b163861',
});

const admittedCourseIds = Object.freeze([
  'A20', 'B30', 'C140', 'D30', 'D50', 'D60', 'D80', 'D90', 'D100', 'D120',
]);
const htmlReaderCourseIds = Object.freeze(['C140', 'D30', 'D60', 'D90', 'D100', 'D120']);

const courseNotes = Object.freeze({
  A20: 'Checkpoint publik v0.2.0-wip memuat 41 dari 83 modul berurutan sampai akhir Bab 6 dalam pembaca 1.732 halaman. Buku tetap diproduksi.',
  B30: 'Checkpoint publik WIP.16 mencapai akhir Bagian 3.5 dalam pembaca 1.102 halaman dengan 165.925 rekaman backend. CLP Kalkulus 2 tetap diproduksi.',
  C140: 'Komponen Penn State STAT 415 lengkap pada 14 dari 14 dokumen publik dan tersedia sebagai pembaca HTML. Korpus gabungan C140, termasuk komponen Random dan pendamping rigor, tetap diproduksi dan tidak dinyatakan lengkap.',
  D30: 'Checkpoint publik 32 memuat QuantEcon 8 dari 8 bab, 27 halaman Random terpilih, dua laboratorium, dan jembatan asli dalam pembaca PDF 313 halaman serta rute HTML. Kursus tetap diproduksi.',
  D50: 'Checkpoint publik memuat Kuliah dan Lembar Kerja 1–16: 261 halaman, 342 latihan, dan tepat 48 solusi yang tersedia pada sumber. Kursus tetap diproduksi.',
  D60: 'Checkpoint publik v0.31.1 memuat Roberts 30 dari 30, Fomberg §§1.1–1.13, dan penguasaan biasa 84 dari 84; total 92 dari 108 butir wajib. Kursus tetap diproduksi.',
  D80: 'Checkpoint publik memuat Unit 001–047; pendahuluan dan Bab 1–3 lengkap dalam pembaca 308 halaman. Korpus tetap diproduksi.',
  D90: 'Checkpoint publik Original Tranche 02 memuat delapan segmen, enam latihan, petunjuk bertahap, dan solusi lengkap; MIT L11 juga telah terbit. Kursus tetap diproduksi.',
  D100: 'Checkpoint publik memuat Unit 1–28 dari 30: 476 halaman, 671 latihan, 118 solusi sumber publik yang dibekukan, dan 21.358 rekaman backend asli. Kursus tetap diproduksi.',
  D120: 'Edisi sembilan unit O017/D120 lengkap, terbuka, dan terverifikasi publik dalam PDF, HTML, serta paket luring. Kursus dinyatakan selesai.',
});

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
const jsonClone = (value) => JSON.parse(JSON.stringify(value));

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

function portableRelative(value, name) {
  const normalized = value.replaceAll('\\', '/');
  assert.ok(!normalized.startsWith('/') && !normalized.includes('..'), `${name} must be a portable project-relative path.`);
  return normalized;
}

function expectedCountOptions() {
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
  const rows = [];
  for (const entry of await readdir(resolve(root, prefix), { withFileTypes: true })) {
    const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
    if (entry.isDirectory()) rows.push(...await listFiles(root, relative));
    else if (entry.isFile()) rows.push(relative);
  }
  return rows.sort();
}

function v22PackagePath(project) {
  const supplied = optionalOption('--v22-package');
  if (!supplied) return resolve(project, v22Identity.relativeToProject);
  return isAbsolute(supplied) ? resolve(supplied) : resolve(project, supplied);
}

async function assertV22Package(project) {
  const packageRoot = v22PackagePath(project);
  const paths = await listFiles(packageRoot);
  assert.equal(paths.length, v22Identity.fileCount, 'Backend v2.2 package file count changed.');
  const facts = new Map();
  let packageBytes = 0;
  for (const relative of paths) {
    const bytes = await readFile(resolve(packageRoot, relative));
    packageBytes += bytes.length;
    facts.set(relative, { bytes: bytes.length, sha256: sha256(bytes) });
  }
  assert.equal(packageBytes, v22Identity.packageBytes, 'Backend v2.2 package byte count changed.');
  for (const identity of [v22Identity.manifest, v22Identity.validationReport, v22Identity.seal]) {
    assert.deepEqual(facts.get(identity.path), { bytes: identity.bytes, sha256: identity.sha256 }, `Backend v2.2 ${identity.path} identity changed.`);
  }

  const manifest = JSON.parse((await readFile(resolve(packageRoot, v22Identity.manifest.path))).toString('utf8'));
  const validation = JSON.parse((await readFile(resolve(packageRoot, v22Identity.validationReport.path))).toString('utf8'));
  const seal = JSON.parse((await readFile(resolve(packageRoot, v22Identity.seal.path))).toString('utf8'));
  assert.equal(manifest.schema_id, 'interlanguage/global-modular-mathematics-backend-manifest/2.2.0');
  assert.equal(manifest.schema_version, '2.2.0');
  assert.equal(manifest.package_id, v22Identity.packageId);
  assert.equal(manifest.record_count, v22Identity.projectedRecords);
  assert.equal(manifest.record_order.length, v22Identity.recordTables);
  assert.equal(manifest.build.deterministic_replay, 'byte_identical');
  assert.equal(manifest.build.build_a_sha256, v22Identity.replaySha256);
  assert.equal(manifest.build.build_b_sha256, v22Identity.replaySha256);
  assert.equal(manifest.shards.find((row) => row.shard_kind === 'native_semantic')?.record_count, v22Identity.nativeRecordsReferenced);
  assert.equal(manifest.shards.find((row) => row.shard_kind === 'identity_map')?.record_count, v22Identity.identityMapRows);

  assert.equal(validation.schema_id, 'interlanguage/global-modular-mathematics-validation-report/2.2.0');
  assert.equal(validation.package_id, v22Identity.packageId);
  assert.equal(validation.result, 'pass');
  assert.equal(validation.counts.errors, 0);
  assert.equal(validation.errors.length, 0);
  assert.equal(validation.counts.native_records_referenced, v22Identity.nativeRecordsReferenced);
  assert.equal(validation.counts.native_views, v22Identity.nativeViews);
  assert.equal(validation.counts.projected_records, v22Identity.projectedRecords);
  assert.equal(validation.counts.record_tables, v22Identity.recordTables);
  assert.equal(validation.counts.visible_units, v22Identity.visibleUnits);
  assert.equal(validation.counts.routes, v22Identity.learnerRoutes);
  assert.equal(validation.counts.identity_map_rows, v22Identity.identityMapRows);
  assert.equal(validation.hashes.manifest_sha256, v22Identity.manifest.sha256);
  assert.equal(validation.hashes.two_run_replay_sha256, v22Identity.replaySha256);

  assert.equal(seal.schema_id, 'interlanguage/global-modular-mathematics-package-seal/2.2.0');
  assert.equal(seal.package_id, v22Identity.packageId);
  assert.equal(seal.file_count, v22Identity.seal.sealedFileCount);
  assert.equal(seal.total_bytes, v22Identity.seal.sealedBytes);
  assert.equal(seal.sealed_digest_sha256, v22Identity.seal.sealedDigestSha256);
  const sealedFacts = new Map(seal.files.map((row) => [row.path, { bytes: row.bytes, sha256: row.sha256 }]));
  const actualSealedPaths = paths.filter((path) => path !== v22Identity.seal.path);
  assert.deepEqual([...sealedFacts.keys()].sort(), actualSealedPaths, 'Backend v2.2 seal inventory changed.');
  for (const relative of actualSealedPaths) {
    assert.deepEqual(sealedFacts.get(relative), facts.get(relative), `Backend v2.2 sealed file changed: ${relative}.`);
  }
  const digestLines = [...sealedFacts.keys()].sort()
    .map((path) => `${sealedFacts.get(path).sha256}  ${sealedFacts.get(path).bytes}  ${path}\n`)
    .join('');
  assert.equal(sha256(Buffer.from(digestLines, 'utf8')), v22Identity.seal.sealedDigestSha256, 'Backend v2.2 sealed aggregate changed.');
  const projection = JSON.parse((await readFile(resolve(packageRoot, 'projection-inventory.json'))).toString('utf8'));
  assert.equal(projection.zero_copy, true);
  assert.equal(projection.native_record_count, v22Identity.nativeRecordsReferenced);
  const nativeIndex = JSON.parse((await readFile(resolve(packageRoot, 'native-shard-index.json'))).toString('utf8'));
  assert.equal(nativeIndex.record_count, v22Identity.nativeRecordsReferenced);
  assert.equal(nativeIndex.view_count, v22Identity.nativeViews);
  return { packageRoot, manifest, validation, seal };
}

function assertHttps(value, label) {
  assert.equal(typeof value, 'string', `${label} must be a string.`);
  assert.match(value, /^https:\/\//, `${label} must use HTTPS.`);
}

function assertSha(value, label) {
  assert.match(value, /^[0-9a-f]{64}$/, `${label} must be a lowercase SHA-256 digest.`);
}

function assertPredecessor(predecessor, bytes) {
  assert.equal(bytes.length, predecessorIdentity.bytes, 'Predecessor authority byte count changed.');
  assert.equal(sha256(bytes), predecessorIdentity.sha256, 'Predecessor authority SHA-256 changed.');
  assert.equal(predecessor.schema_id, 'interlanguage/program-matematika-indonesia-curriculum-authority/v1');
  assert.equal(predecessor.catalog.program.version, predecessorIdentity.version);
  assert.equal(predecessor.catalog.program.zenodo, `https://doi.org/10.5281/zenodo.${predecessorIdentity.recordId}`);
  assert.equal(predecessor.catalog.program.zenodoConcept, 'https://doi.org/10.5281/zenodo.22059707');
  assert.equal(predecessor.catalog.counts.completedPublicCourseRoles, 18);
  assert.equal(predecessor.catalog.counts.completedPublicRecords, 17);
}

function assertAdmissionManifest(manifest) {
  assert.equal(manifest.schema_id, 'program-matematika-indonesia/central-release-admission-manifest/v1');
  assert.equal(manifest.target_release, version);
  assert.equal(manifest.summary.admitted_primary_course_routes, 10);
  assert.equal(manifest.summary.admitted_partial_courses, 9);
  assert.equal(manifest.summary.admitted_newly_complete_courses, 1);
  assert.equal(manifest.summary.admitted_separate_supplements, 1);
  assert.equal(manifest.summary.completed_public_course_roles_after, 19);
  assert.equal(manifest.summary.completed_public_records_after, 18);
  assert.deepEqual(manifest.admissions.map((row) => row.course_id), admittedCourseIds);
  assert.equal(manifest.admissions.length, admittedCourseIds.length);
  for (const row of manifest.admissions) {
    assert.equal(row.state_after, row.course_id === 'D120' ? 'published' : 'production');
    assertHttps(row.learner_route, `${row.course_id} learner route`);
    assert.match(row.doi, /^10\.5281\/zenodo\.[0-9]+$/);
    assert.match(row.concept_doi, /^10\.5281\/zenodo\.[0-9]+$/);
    assert.ok(Number.isInteger(row.bytes) && row.bytes > 0, `${row.course_id} bytes must be positive.`);
    assert.equal(row.checksum.algorithm, 'sha256');
    assertSha(row.checksum.value, `${row.course_id} checksum`);
    assert.equal(typeof row.boundary, 'string');
    assert.ok(row.boundary.length > 0);
  }
  assert.equal(manifest.supplements.length, 1);
  const supplement = manifest.supplements[0];
  assert.equal(supplement.course_id, 'C100');
  assert.equal(supplement.supplement_id, 'clemens-snapp-workbook-u011');
  assert.equal(supplement.main_course_lineage_unchanged, true);
  assert.equal(supplement.checksum.algorithm, 'sha256');
  assertSha(supplement.checksum.value, 'C100 supplement checksum');
  assert.ok(manifest.exclusions.some((row) => row.course_id === 'B95' && row.decision === 'exclude_from_v0.59'));
}

function assertOwnerReaderManifest(manifest) {
  assert.equal(manifest.schema_id, 'program-matematika-indonesia/owner-reader-public-readback/v1');
  assert.equal(manifest.result, 'pass');
  assert.equal(manifest.source_admission_manifest.bytes, admissionIdentity.bytes);
  assert.equal(manifest.source_admission_manifest.sha256, admissionIdentity.sha256);
  assert.equal(manifest.route_count, 6);
  assert.deepEqual(manifest.routes.map((row) => row.course_id), htmlReaderCourseIds);
  for (const row of manifest.routes) {
    assert.equal(row.http_status, 200);
    assert.equal(row.content_type, 'text/html');
    assertHttps(row.url, `${row.course_id} HTML reader`);
    assert.ok(Number.isInteger(row.bytes) && row.bytes > 0);
    assertSha(row.sha256, `${row.course_id} HTML reader checksum`);
    assert.ok(!/\.(?:json|jsonl)(?:[?#]|$)/i.test(row.url), `${row.course_id} HTML route points to machine data.`);
  }
}

function updateCourse(catalog, id, update) {
  const course = catalog.courses.find((item) => item.id === id);
  assert.ok(course, `Missing course ${id}.`);
  Object.assign(course, update);
}

function applyAdmissions(catalog, admissionManifest, ownerReaderManifest) {
  const predecessorCourses = new Map(catalog.courses.map((course) => [course.id, jsonClone(course)]));
  const readers = new Map(ownerReaderManifest.routes.map((row) => [row.course_id, row]));

  for (const admission of admissionManifest.admissions) {
    const update = {
      state: admission.state_after,
      note: courseNotes[admission.course_id],
      edition: admission.learner_route,
      zenodo: `https://doi.org/${admission.doi}`,
    };
    const reader = readers.get(admission.course_id);
    if (reader) update.reader = reader.url;
    updateCourse(catalog, admission.course_id, update);
  }

  const supplement = admissionManifest.supplements[0];
  const c100 = catalog.courses.find((course) => course.id === 'C100');
  assert.ok(c100, 'Missing course C100.');
  assert.equal(c100.state, 'published');
  assert.equal(c100.zenodo, 'https://doi.org/10.5281/zenodo.22102628');
  c100.note = 'Kursus utama tetap lengkap dan tidak berubah: tulang punggung Petrunin yang bersih hak, 253 solusi, pendamping konektif asli enam unit beserta solusi, empat pemeriksaan kumulatif, dua capstone, backend, HTML semantik, dan EPUB. Workbook Clemens/Snapp berada pada lini CC BY-NC-SA terpisah; checkpoint Unit 001–011 tersedia sebagai sumber tambahan parsial.';
  c100.supplements = [{
    id: supplement.supplement_id,
    title: 'Buku kerja geometri dua dimensi, Unit 001–011',
    resourceType: 'workbook',
    state: 'partial',
    scope: 'Unit 001–011, pembaca 123 halaman; lini lisensi terpisah dari kursus utama.',
    license: supplement.license,
    pages: 123,
    url: supplement.learner_route,
    zenodo: `https://doi.org/${supplement.doi}`,
    conceptDoi: `https://doi.org/${supplement.concept_doi}`,
    bytes: supplement.bytes,
    sha256: supplement.checksum.value,
  }];

  const changedIds = new Set([...admittedCourseIds, 'C100']);
  for (const course of catalog.courses) {
    if (!changedIds.has(course.id)) {
      assert.deepEqual(course, predecessorCourses.get(course.id), `Unadmitted course ${course.id} changed.`);
    }
  }
  assert.deepEqual(catalog.courses.find((course) => course.id === 'B95'), predecessorCourses.get('B95'), 'B95 must remain untouched and excluded.');

  const program = catalog.program;
  program.completedPublicCourseRoleIds = [...new Set([...program.completedPublicCourseRoleIds, 'D120'])]
    .sort((a, b) => a.localeCompare(b, 'en', { numeric: true }));
  program.completedPublicRecordDois = [...new Set([
    ...program.completedPublicRecordDois,
    '10.5281/zenodo.22073823',
  ])];
  assert.equal(program.completedPublicCourseRoleIds.length, 19);
  assert.equal(program.completedPublicRecordDois.length, 18);
}

function federationV22Metadata(recordId) {
  return {
    version: '2.2.0',
    status: 'pilot_validated_zero_copy',
    pilotCourseId: 'A00',
    packageId: v22Identity.packageId,
    canonicalPackage: {
      path: v22Identity.relativeToProject,
      fileCount: v22Identity.fileCount,
      bytes: v22Identity.packageBytes,
      manifest: { ...v22Identity.manifest },
      validationReport: {
        ...v22Identity.validationReport,
        result: 'pass',
        errors: 0,
      },
      seal: {
        path: v22Identity.seal.path,
        bytes: v22Identity.seal.bytes,
        sha256: v22Identity.seal.sha256,
        sealedFileCount: v22Identity.seal.sealedFileCount,
        sealedBytes: v22Identity.seal.sealedBytes,
        sealedDigestSha256: v22Identity.seal.sealedDigestSha256,
      },
    },
    zeroCopy: {
      nativeRecordsReferenced: v22Identity.nativeRecordsReferenced,
      nativeRecordsCopied: v22Identity.nativeRecordsCopied,
      nativeViews: v22Identity.nativeViews,
    },
    projection: {
      records: v22Identity.projectedRecords,
      recordTables: v22Identity.recordTables,
      visibleUnits: v22Identity.visibleUnits,
      learnerRoutes: v22Identity.learnerRoutes,
      identityMapRows: v22Identity.identityMapRows,
    },
    deterministicReplay: {
      runs: v22Identity.replayRuns,
      sha256: v22Identity.replaySha256,
    },
    package: `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-backend-v2.2-pilot-v${version}.zip?download=1`,
    validationReceipt: `https://zenodo.org/records/${recordId}/files/GLOBAL_BACKEND_V22_VALIDATION_RECEIPT_v${version}.json?download=1`,
    archiveReceipt: `https://zenodo.org/records/${recordId}/files/GLOBAL_BACKEND_V22_ARCHIVE_RECEIPT_v${version}.json?download=1`,
    githubPackage: `https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v${version}/program-matematika-indonesia-backend-v2.2-pilot-v${version}.zip`,
    githubValidationReceipt: `https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v${version}/GLOBAL_BACKEND_V22_VALIDATION_RECEIPT_v${version}.json`,
    githubArchiveReceipt: `https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v${version}/GLOBAL_BACKEND_V22_ARCHIVE_RECEIPT_v${version}.json`,
  };
}

function updateProgram(catalog, {
  recordId,
  snapshotDate,
  recordCount,
  datasetCount,
  courseCount,
  readerSurfaces,
  webRoutes,
  identityCrosswalks,
  publicationEvents,
  qaEvents,
}) {
  const program = catalog.program;
  program.version = version;
  program.snapshotDate = snapshotDate;
  program.zenodo = `https://doi.org/10.5281/zenodo.${recordId}`;
  program.repositories.github.lastConfirmedAt = snapshotDate;
  program.backend.schema = `https://zenodo.org/records/${recordId}/files/interlanguage-math-backend-v1.schema.json?download=1`;
  program.backend.sourceFormatProfile = `https://zenodo.org/records/${recordId}/files/interlanguage-source-format-profile-v1.schema.json?download=1`;
  program.backend.package = `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-backend-v1-v${version}.zip?download=1`;
  Object.assign(program.backend.federationV2, {
    version: federationVersion,
    recordCount,
    datasetCount,
    courseCount,
    learnerSurfaceCount: readerSurfaces,
    webRouteCount: webRoutes,
    identityCrosswalkCount: identityCrosswalks,
    publicationEventCount: publicationEvents,
    qaEventCount: qaEvents,
    package: `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-backend-v2-v${version}.zip?download=1`,
    packageSchema: `https://zenodo.org/records/${recordId}/files/federation-package-v2.schema.json?download=1`,
    recordSchema: `https://zenodo.org/records/${recordId}/files/federation-record-v2.schema.json?download=1`,
    validationReceipt: `https://zenodo.org/records/${recordId}/files/GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v${version}.json?download=1`,
  });
  Object.assign(program.backend.learnerReadModelV1, {
    authority: `https://zenodo.org/records/${recordId}/files/curriculum-authority-v1.json?download=1`,
    authoritySchema: `https://zenodo.org/records/${recordId}/files/curriculum-authority-v1.schema.json?download=1`,
    readModel: `https://zenodo.org/records/${recordId}/files/learner-read-model-v1.json?download=1`,
    readModelSchema: `https://zenodo.org/records/${recordId}/files/learner-read-model-v1.schema.json?download=1`,
    validationReceipt: `https://zenodo.org/records/${recordId}/files/LOCAL_RELEASE_VALIDATION_v${version}.json?download=1`,
  });
  program.backend.federationV21.packageSchema = `https://zenodo.org/records/${recordId}/files/federation-unit-package-v2.1.schema.json?download=1`;
  program.backend.federationV21.recordSchema = `https://zenodo.org/records/${recordId}/files/federation-unit-record-v2.1.schema.json?download=1`;
  program.backend.federationV21.package = `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-backend-v2.1-pilots-v${version}.zip?download=1`;
  program.backend.federationV22 = federationV22Metadata(recordId);
  program.backend.educationalAccessResearch.sourcePackage = `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-source-v${version}.zip?download=1`;
}

function buildSeed(predecessor, admissionManifest, ownerReaderManifest, options) {
  const catalog = structuredClone(predecessor.catalog);
  applyAdmissions(catalog, admissionManifest, ownerReaderManifest);
  updateProgram(catalog, options);
  catalog.$schema = `https://zenodo.org/records/${options.recordId}/files/program-matematika-indonesia-catalog-v1.schema.json`;
  catalog.snapshotDate = options.snapshotDate;
  catalog.sourceCommit = options.sourceCommit;
  catalog.counts = {
    courseRoles: 40,
    selectedCorpusRoles: 40,
    unresolvedRoles: 0,
    completedPublicCourseRoles: catalog.program.completedPublicCourseRoleIds.length,
    completedPublicRecords: catalog.program.completedPublicRecordDois.length,
  };
  assert.equal(catalog.counts.completedPublicCourseRoles, 19);
  assert.equal(catalog.counts.completedPublicRecords, 18);
  return catalog;
}

function commonOptions() {
  const sourceCommit = option('--source-commit');
  const snapshotDate = option('--snapshot-date');
  assert.match(sourceCommit, /^[0-9a-f]{40}$/);
  assert.match(snapshotDate, /^\d{4}-\d{2}-\d{2}$/);
  return {
    recordId: integerOption('--record-id'),
    sourceCommit,
    snapshotDate,
    ...expectedCountOptions(),
  };
}

async function loadInputs(project) {
  const authorityPath = resolve(project, authorityRelative);
  const predecessorBytes = await readFile(authorityPath);
  const predecessor = JSON.parse(predecessorBytes.toString('utf8'));
  assertPredecessor(predecessor, predecessorBytes);
  const admission = await loadBoundJson(
    inputPath(project, '--admission-manifest', admissionIdentity),
    admissionIdentity,
    'Admission manifest',
  );
  assertAdmissionManifest(admission.value);
  const ownerReaders = await loadBoundJson(
    inputPath(project, '--owner-reader-manifest', ownerReaderIdentity),
    ownerReaderIdentity,
    'Owner-reader manifest',
  );
  assertOwnerReaderManifest(ownerReaders.value);
  const v22 = await assertV22Package(project);
  return { predecessor, predecessorBytes, admission: admission.value, ownerReaders: ownerReaders.value, v22 };
}

function assertCatalogEvidence(catalog, predecessor, admissionManifest, ownerReaderManifest, options) {
  assert.equal(catalog.program.version, version);
  assert.equal(catalog.program.zenodo, `https://doi.org/10.5281/zenodo.${options.recordId}`);
  assert.equal(catalog.sourceCommit, options.sourceCommit);
  assert.equal(catalog.snapshotDate, options.snapshotDate);
  assert.equal(catalog.program.snapshotDate, options.snapshotDate);
  assert.equal(catalog.counts.completedPublicCourseRoles, 19);
  assert.equal(catalog.counts.completedPublicRecords, 18);
  assert.equal(catalog.program.completedPublicCourseRoleIds.length, 19);
  assert.equal(catalog.program.completedPublicRecordDois.length, 18);
  assert.deepEqual(catalog.program.backend.federationV22, federationV22Metadata(options.recordId));
  assert.ok(catalog.program.completedPublicCourseRoleIds.includes('D120'));
  assert.ok(catalog.program.completedPublicRecordDois.includes('10.5281/zenodo.22073823'));
  assert.deepEqual(
    catalog.courses.find((course) => course.id === 'B95'),
    predecessor.catalog.courses.find((course) => course.id === 'B95'),
    'B95 must remain byte-semantically unchanged in the seed catalog.',
  );
  const readerById = new Map(ownerReaderManifest.routes.map((row) => [row.course_id, row]));
  for (const admission of admissionManifest.admissions) {
    const course = catalog.courses.find((item) => item.id === admission.course_id);
    assert.ok(course);
    assert.equal(course.state, admission.state_after);
    assert.equal(course.edition, admission.learner_route);
    assert.equal(course.zenodo, `https://doi.org/${admission.doi}`);
    if (readerById.has(admission.course_id)) {
      assert.equal(course.reader, readerById.get(admission.course_id).url);
    }
  }
  const supplement = admissionManifest.supplements[0];
  const c100 = catalog.courses.find((course) => course.id === 'C100');
  assert.equal(c100.zenodo, predecessor.catalog.courses.find((course) => course.id === 'C100').zenodo);
  assert.equal(c100.supplements.length, 1);
  assert.equal(c100.supplements[0].id, supplement.supplement_id);
  assert.equal(c100.supplements[0].url, supplement.learner_route);
  assert.equal(c100.supplements[0].sha256, supplement.checksum.value);
}

async function seed(project) {
  const options = commonOptions();
  const { predecessor, admission, ownerReaders } = await loadInputs(project);
  const catalog = buildSeed(predecessor, admission, ownerReaders, options);
  assertCatalogEvidence(catalog, predecessor, admission, ownerReaders, options);
  const bytes = canonical(catalog);
  if (!flag('--dry-run')) {
    await mkdir(resolve(project, dirname(seedRelative)), { recursive: true });
    await writeFile(resolve(project, seedRelative), bytes);
  }
  console.log(JSON.stringify({
    mode: 'seed',
    dry_run: flag('--dry-run'),
    path: seedRelative,
    bytes: bytes.length,
    sha256: sha256(bytes),
    admissions: admittedCourseIds.length,
    completed_roles: 19,
    completed_records: 18,
  }, null, 2));
}

function primaryRouteFacts(admissionManifest, ownerReaderManifest) {
  const readers = new Map(ownerReaderManifest.routes.map((row) => [row.course_id, row]));
  return admissionManifest.admissions.map((admission) => {
    const reader = readers.get(admission.course_id);
    if (reader) {
      return {
        courseId: admission.course_id,
        url: reader.url,
        bytes: reader.bytes,
        digest: reader.sha256,
        verifiedAt: new Date(ownerReaderManifest.recorded_at).toISOString(),
        evidenceSha256: ownerReaderIdentity.sha256,
        evidenceKind: 'owner_reader_manifest',
        expectedAction: 'learn',
      };
    }
    return {
      courseId: admission.course_id,
      url: admission.learner_route,
      bytes: admission.bytes,
      digest: admission.checksum.value,
      verifiedAt: new Date(admissionManifest.recorded_at).toISOString(),
      evidenceSha256: admissionIdentity.sha256,
      evidenceKind: 'admission_manifest',
      expectedAction: admission.format === 'pdf' ? 'learn' : 'offline',
    };
  });
}

function findSurface(records, fact) {
  const candidates = records.filter((record) => record.record_type === 'reader_surface'
    && record.payload.url === fact.url
    && record.payload.course_ids.includes(fact.courseId)
    && record.payload.actions.includes(fact.expectedAction));
  assert.equal(candidates.length, 1, `${fact.courseId}: expected exactly one ${fact.expectedAction} surface for ${fact.url}.`);
  return candidates[0];
}

async function promote(project) {
  const options = commonOptions();
  const federationRelative = portableRelative(option('--federation-relative'), '--federation-relative');
  const { predecessor, predecessorBytes, admission, ownerReaders } = await loadInputs(project);
  const seedBytes = await readFile(resolve(project, seedRelative));
  const catalog = JSON.parse(seedBytes.toString('utf8'));
  assertCatalogEvidence(catalog, predecessor, admission, ownerReaders, options);

  const recordsRelative = `${federationRelative}/records.jsonl`;
  const manifestRelative = `${federationRelative}/manifest.json`;
  const validationRelative = `${federationRelative}/validation_report.json`;
  const recordsBytes = await readFile(resolve(project, recordsRelative));
  const manifestBytes = await readFile(resolve(project, manifestRelative));
  const manifest = JSON.parse(manifestBytes.toString('utf8'));
  const validationBytes = await readFile(resolve(project, validationRelative));
  const validation = JSON.parse(validationBytes.toString('utf8'));
  assert.equal(validation.result, 'pass');
  assert.equal(manifest.dataset_version, `program-matematika-indonesia-federation-v${federationVersion}`);

  const expectedCounts = {
    records: options.recordCount,
    datasets: options.datasetCount,
    courses: options.courseCount,
    reader_surfaces: options.readerSurfaces,
    web_routes: options.webRoutes,
    identity_crosswalks: options.identityCrosswalks,
    publication_events: options.publicationEvents,
    qa_events: options.qaEvents,
  };
  assert.equal(catalog.program.backend.federationV2.recordCount, expectedCounts.records);
  assert.equal(catalog.program.backend.federationV2.datasetCount, expectedCounts.datasets);
  assert.equal(catalog.program.backend.federationV2.courseCount, expectedCounts.courses);
  assert.equal(catalog.program.backend.federationV2.learnerSurfaceCount, expectedCounts.reader_surfaces);
  assert.equal(catalog.program.backend.federationV2.webRouteCount, expectedCounts.web_routes);
  assert.equal(catalog.program.backend.federationV2.identityCrosswalkCount, expectedCounts.identity_crosswalks);
  assert.equal(catalog.program.backend.federationV2.publicationEventCount, expectedCounts.publication_events);
  assert.equal(catalog.program.backend.federationV2.qaEventCount, expectedCounts.qa_events);
  assert.equal(manifest.record_count, expectedCounts.records);
  for (const [key, value] of Object.entries(expectedCounts)) {
    if (key !== 'records') assert.equal(manifest.record_counts[key], value, `Federation count mismatch: ${key}.`);
  }

  const recordsManifestEntry = manifest.files.find((entry) => entry.path === 'records.jsonl');
  assert.ok(recordsManifestEntry, 'Federation manifest does not bind records.jsonl.');
  assert.equal(recordsManifestEntry.bytes, recordsBytes.length);
  assert.equal(recordsManifestEntry.sha256, sha256(recordsBytes));
  assert.equal(validation.checks.record_count, expectedCounts.records);
  assert.equal(validation.checks.records_jsonl_sha256, sha256(recordsBytes));
  assert.equal(validation.checks.manifest_sha256, sha256(manifestBytes));

  const records = recordsBytes.toString('utf8').trim().split('\n').map(JSON.parse);
  assert.equal(records.length, expectedCounts.records, 'records.jsonl row count does not match the declared record count.');
  const newOverlays = primaryRouteFacts(admission, ownerReaders).map((fact) => {
    const surface = findSurface(records, fact);
    assert.ok(['catalog_declared', 'public'].includes(surface.payload.publication_state));
    if (fact.evidenceKind === 'owner_reader_manifest') {
      assert.equal(surface.payload.publication_state, 'public');
      assert.equal(surface.payload.evidence_kind, 'public_readback');
      assert.equal(surface.payload.evidence_sha256, fact.evidenceSha256);
    }
    return {
      course_id: fact.courseId,
      surface_id: surface.id,
      url: fact.url,
      source_publication_state: surface.payload.publication_state,
      effective_publication_state: 'public',
      evidence_kind: 'anonymous_public_byte_readback',
      bytes: fact.bytes,
      sha256: fact.digest,
      verified_at: fact.verifiedAt,
    };
  });
  assert.equal(newOverlays.length, 10);
  assert.equal(new Set(newOverlays.map((item) => item.course_id)).size, 10);
  assert.ok(!newOverlays.some((item) => item.course_id === 'B95'));

  const historyPath = resolve(project, historyRelative);
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
    predecessor_authority: {
      path: historyRelative,
      bytes: predecessorBytes.length,
      sha256: sha256(predecessorBytes),
    },
    transition: {
      from_version: predecessorIdentity.version,
      to_version: version,
      snapshot_date: options.snapshotDate,
      zenodo_record_id: options.recordId,
      method: transitionMethod,
    },
  };
  authority.public_readback_overlays = [...predecessor.public_readback_overlays, ...newOverlays];
  assert.equal(authority.public_readback_overlays.length, predecessor.public_readback_overlays.length + 10);
  assert.equal(new Set(authority.public_readback_overlays.map((item) => item.surface_id)).size, authority.public_readback_overlays.length);
  const outputBytes = canonical(authority);

  if (!flag('--dry-run')) {
    await mkdir(dirname(historyPath), { recursive: true });
    await writeFile(historyPath, predecessorBytes);
    await writeFile(resolve(project, authorityRelative), outputBytes);
  }
  console.log(JSON.stringify({
    mode: 'promote',
    dry_run: flag('--dry-run'),
    path: authorityRelative,
    bytes: outputBytes.length,
    sha256: sha256(outputBytes),
    predecessor_history: historyRelative,
    predecessor_bytes: predecessorBytes.length,
    predecessor_sha256: sha256(predecessorBytes),
    federation: federationRelative,
    overlays: authority.public_readback_overlays.length,
    new_overlays: newOverlays.length,
  }, null, 2));
}

const mode = process.argv[2];
const project = resolve(optionalOption('--project-root') ?? defaultProject);
if (mode === 'seed') await seed(project);
else if (mode === 'promote') await promote(project);
else throw new Error('Usage: node scripts/advance-curriculum-authority-v059.mjs <seed|promote> --record-id N --source-commit SHA --snapshot-date YYYY-MM-DD --record-count N --dataset-count N --course-count N --reader-surfaces N --web-routes N --identity-crosswalks N --publication-events N --qa-events N [--federation-relative PATH] [--admission-manifest PATH] [--owner-reader-manifest PATH] [--v22-package PATH] [--project-root PATH] [--dry-run]');
