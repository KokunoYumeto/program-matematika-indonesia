import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const defaultProject = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const version = '0.62.0';
const federationVersion = '0.4.4';
const authorityRelative = 'backend/authority/curriculum-authority-v1.json';
const historyRelative = 'backend/authority/history/curriculum-authority-v0.61.0.json';
const seedRelative = `backend/authority/catalogs/program-matematika-indonesia-catalog-v${version}.json`;

const predecessorIdentity = Object.freeze({
  bytes: 76437,
  sha256: '1060038a84af909ccf84df17d8a15ea63255865037ce06e156f07e26982257e6',
  version: '0.61.0',
  recordId: 22148050,
});
const admissionIdentity = Object.freeze({
  relativeToWorkspace: 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/141_CENTRAL_V062_ADMISSION_MANIFEST_20260828.json',
  bytes: 8848,
  sha256: '35fec1858a38a49a94f873c60685254ac015230e69faaf8743e52a3ed181e7b4',
});
const ownerReaderIdentity = Object.freeze({
  relativeToWorkspace: 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/142_PUBLIC_OWNER_HTML_ROUTE_READBACK_V062_20260828.json',
  bytes: 4108,
  sha256: 'c5bddd8c0d5d2452d9a9391c3fd484ce9ac0e5d415fa659cda87586ec3234885',
});
const reservationIdentity = Object.freeze({
  relativeToWorkspace: 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/140_CENTRAL_V062_ZENODO_DRAFT_RESERVATION_20260828.json',
  bytes: 1440,
  sha256: 'f287ea3fa8db6a6b01197eadd3b777394e2f9b83e47b4027635b4e7d21ca2724',
});

const expectedCompletedRoleIds = Object.freeze([
  'A00', 'B10', 'B20', 'B40', 'B60', 'B80', 'B90', 'C10', 'C30', 'C40',
  'C60', 'C70', 'C80', 'C100', 'C110', 'C120', 'C130', 'D20', 'D90', 'D110', 'D120',
]);

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
  const values = {
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
  assert.equal(values.courseCount, 40, 'The v0.62 catalog must retain exactly 40 course roles.');
  return values;
}

function rewriteCentralReleaseUrls(value, recordId) {
  if (typeof value === 'string') {
    return value
      .replaceAll(String(predecessorIdentity.recordId), String(recordId))
      .replaceAll(`v${predecessorIdentity.version}`, `v${version}`);
  }
  if (Array.isArray(value)) return value.map((item) => rewriteCentralReleaseUrls(item, recordId));
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, rewriteCentralReleaseUrls(item, recordId)]));
  }
  return value;
}

function byCourse(catalog, courseId) {
  const course = catalog.courses.find((row) => row.id === courseId);
  assert.ok(course, `Missing course ${courseId}.`);
  return course;
}

function admissionByCourse(admission, courseId) {
  const rows = admission.admissions.filter((row) => row.course_id === courseId);
  assert.equal(rows.length, 1, `Expected exactly one ${courseId} admission.`);
  return rows[0];
}

function publicRecord(admission, recordId) {
  const rows = admission.public_record_rechecks.filter((row) => row.record_id === recordId);
  assert.equal(rows.length, 1, `Expected exactly one public record ${recordId}.`);
  const row = rows[0];
  assert.equal(row.status, 'published');
  assert.equal(row.access, 'open');
  return row;
}

function publicFile(record, name) {
  const rows = record.verified_files.filter((row) => row.name === name);
  assert.equal(rows.length, 1, `Expected exactly one ${name} file fact.`);
  const row = rows[0];
  assert.ok(Number.isInteger(row.bytes) && row.bytes > 0);
  assert.match(row.sha256, /^[0-9a-f]{64}$/);
  return row;
}

function downloadUrl(recordId, name) {
  return `https://zenodo.org/records/${recordId}/files/${name}?download=1`;
}

function doiUrl(doi) { return `https://doi.org/${doi}`; }

function supplement({ id, title, resourceType, scope, license, pages, file, record }) {
  return {
    id, title, resourceType, state: 'complete', scope, license, pages,
    url: downloadUrl(record.record_id, file.name),
    zenodo: doiUrl(record.doi),
    bytes: file.bytes,
    sha256: file.sha256,
  };
}

function recomputeCompletion(catalog) {
  const completedRoles = catalog.courses.filter((course) => course.state === 'published').map((course) => course.id);
  assert.deepEqual(completedRoles, expectedCompletedRoleIds);
  const completedDois = [];
  const seen = new Set();
  for (const course of catalog.courses.filter((row) => row.state === 'published')) {
    assert.match(course.zenodo ?? '', /^https:\/\/doi\.org\/10\.5281\/zenodo\.[0-9]+$/, `${course.id}: published course lacks a version DOI.`);
    const doi = course.zenodo.replace('https://doi.org/', '');
    if (!seen.has(doi)) {
      seen.add(doi);
      completedDois.push(doi);
    }
  }
  assert.equal(completedDois.length, 20);
  assert.ok(completedDois.includes('10.5281/zenodo.21938930'));
  assert.ok(completedDois.includes('10.5281/zenodo.22142120'));
  catalog.program.completedPublicCourseRoleIds = completedRoles;
  catalog.program.completedPublicRecordDois = completedDois;
  catalog.counts.completedPublicCourseRoles = completedRoles.length;
  catalog.counts.completedPublicRecords = completedDois.length;
}

function assertV062Semantics(catalog) {
  assert.equal(catalog.counts.courseRoles, 40);
  assert.equal(catalog.counts.selectedCorpusRoles, 40);
  assert.equal(catalog.counts.unresolvedRoles, 0);
  assert.equal(catalog.counts.completedPublicCourseRoles, 21);
  assert.equal(catalog.counts.completedPublicRecords, 20);
  assert.deepEqual(catalog.program.completedPublicCourseRoleIds, expectedCompletedRoleIds);
  assert.equal(new Set(catalog.program.completedPublicRecordDois).size, 20);

  const a10 = byCourse(catalog, 'A10');
  assert.equal(a10.state, 'production');
  assert.match(a10.note, /32 dari 82 modul/);
  assert.match(a10.edition, /\/records\/22143518\//);
  assert.equal(a10.zenodo, 'https://doi.org/10.5281/zenodo.22143518');

  const a30 = byCourse(catalog, 'A30');
  assert.equal(a30.state, 'production');
  assert.equal(a30.repository, 'https://github.com/KokunoYumeto/openstax-precalculus-2e-id');
  assert.ok(a30.edition, 'A30 partial learner edition must remain reachable.');

  const b20 = byCourse(catalog, 'B20');
  assert.equal(b20.state, 'published');
  assert.equal(b20.zenodo, 'https://doi.org/10.5281/zenodo.21938930');
  assert.equal(b20.supplements.length, 1);
  assert.equal(b20.supplements[0].resourceType, 'problem-book');

  const b40 = byCourse(catalog, 'B40');
  assert.equal(b40.state, 'published');
  assert.equal(b40.supplements.length, 2);
  assert.deepEqual(b40.supplements.map((row) => row.resourceType), ['solutions', 'workbook']);
  assert.equal(1 + b40.supplements.length, 3, 'B40 must expose three distinct learner materials.');

  const d80 = byCourse(catalog, 'D80');
  assert.equal(d80.state, 'production');
  assert.deepEqual(d80.prerequisites, ['C30', 'C80', 'D70']);
  assert.equal(d80.zenodo, 'https://doi.org/10.5281/zenodo.22143171');

  const d90 = byCourse(catalog, 'D90');
  assert.equal(d90.state, 'published');
  assert.equal(d90.zenodo, 'https://doi.org/10.5281/zenodo.22142120');
  assert.match(d90.reader, /\/records\/22142120\/.+\.html\?download=1$/);
  assert.match(d90.edition, /\/records\/22142120\/.+\.pdf\?download=1$/);

  assert.deepEqual(catalog.program.backend.learnerStateV1, {
    version: '1.0.0',
    status: 'validated',
    schema: `https://zenodo.org/records/${catalog.program.zenodo.split('.').at(-1)}/files/learner-state-v1.schema.json`,
    storage: 'browser-local',
    privacy: 'not-transmitted',
    derivedEligibilityPersisted: false,
  });
  assert.equal(catalog.program.backend.federationV2.version, federationVersion);
  assert.equal(catalog.program.backend.learnerReadModelV1.prerequisiteEdgeCount, 83);
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
  catalog.program.backend.learnerReadModelV1.prerequisiteEdgeCount = 83;
  catalog.program.backend.learnerStateV1 = {
    version: '1.0.0', status: 'validated',
    schema: `https://zenodo.org/records/${options.recordId}/files/learner-state-v1.schema.json`,
    storage: 'browser-local', privacy: 'not-transmitted', derivedEligibilityPersisted: false,
  };

  const a10Admission = admissionByCourse(admission, 'A10');
  const a10Record = publicRecord(admission, a10Admission.record);
  const a10File = publicFile(a10Record, '00-elementary-algebra-2e-bahasa-indonesia-EA2-S0032-reader.pdf');
  Object.assign(byCourse(catalog, 'A10'), {
    state: 'production',
    note: 'Checkpoint publik v0.11.0-wip EA2-S0032 memuat 32 dari 82 modul sebagai snapshot modular nonkontigu dan pembaca 1.011 halaman. Cakupan tidak dinyatakan sebagai awalan buku yang berurutan; buku tetap diproduksi.',
    edition: downloadUrl(a10Record.record_id, a10File.name),
    zenodo: doiUrl(a10Record.doi),
  });

  const a30Admission = admissionByCourse(admission, 'A30');
  Object.assign(byCourse(catalog, 'A30'), {
    state: 'production', repository: a30Admission.repository,
  });

  const b20Admission = admissionByCourse(admission, 'B20');
  const b20Record = publicRecord(admission, b20Admission.record);
  const b20Textbook = publicFile(b20Record, '00_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_BUKU_TEKS.pdf');
  const b20Problems = publicFile(b20Record, '01_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_SOAL_DAN_PENYELESAIAN.pdf');
  Object.assign(byCourse(catalog, 'B20'), {
    state: 'published',
    corpus: 'CLP Calculus 1 — buku teks serta buku soal dan penyelesaian lengkap',
    note: 'Edisi Bahasa Indonesia lengkap dan terverifikasi publik: buku teks 442 halaman serta buku soal dan penyelesaian 646 halaman.',
    edition: downloadUrl(b20Record.record_id, b20Textbook.name),
    repository: 'https://github.com/KokunoYumeto/clp1-differential-calculus-id',
    zenodo: doiUrl(b20Record.doi),
    supplements: [supplement({
      id: 'clp1-soal-dan-penyelesaian',
      title: 'Soal dan Penyelesaian CLP Kalkulus Diferensial',
      resourceType: 'problem-book',
      scope: 'Buku soal dan penyelesaian lengkap, 646 halaman.',
      license: 'CC BY-NC-SA 4.0', pages: b20Admission.problem_book_pages,
      file: b20Problems, record: b20Record,
    })],
  });

  const b40Admission = admissionByCourse(admission, 'B40');
  const b40Record = publicRecord(admission, b40Admission.record);
  const b40Textbook = publicFile(b40Record, '01_HEFFERON_LINEAR_ALGEBRA_ID_TEXTBOOK_2026.08.22.pdf');
  const b40Answers = publicFile(b40Record, '02_HEFFERON_LINEAR_ALGEBRA_ID_WORKED_ANSWERS_2026.08.22.pdf');
  const b40Lab = publicFile(b40Record, '03_HEFFERON_LINEAR_ALGEBRA_ID_SAGE_LAB_2026.08.22.pdf');
  Object.assign(byCourse(catalog, 'B40'), {
    state: 'published',
    note: 'Edisi Bahasa Indonesia lengkap dan terverifikasi publik sebagai tiga bahan belajar terpisah: buku teks 580 halaman, jawaban bekerja 435 halaman, dan laboratorium Sage 109 halaman.',
    edition: downloadUrl(b40Record.record_id, b40Textbook.name),
    zenodo: doiUrl(b40Record.doi),
    supplements: [
      supplement({
        id: 'hefferon-jawaban-bekerja', title: 'Jawaban Bekerja Aljabar Linear',
        resourceType: 'solutions', scope: 'Jawaban bekerja lengkap, 435 halaman.',
        license: 'CC BY-SA 2.5', pages: b40Admission.worked_answers_pages,
        file: b40Answers, record: b40Record,
      }),
      supplement({
        id: 'hefferon-laboratorium-sage', title: 'Laboratorium Sage Aljabar Linear',
        resourceType: 'workbook', scope: 'Laboratorium komputasi Sage lengkap, 109 halaman.',
        license: 'CC BY-SA 2.5', pages: b40Admission.sage_lab_pages,
        file: b40Lab, record: b40Record,
      }),
    ],
  });

  const d80Admission = admissionByCourse(admission, 'D80');
  const d80Record = publicRecord(admission, d80Admission.record);
  const d80File = publicFile(d80Record, '00_METODE_DALAM_ALJABAR_JILID_2_ID_UNIT_050.pdf');
  Object.assign(byCourse(catalog, 'D80'), {
    state: 'production', prerequisites: ['C30', 'C80', 'D70'],
    note: 'Checkpoint publik memuat Unit 001–050; pendahuluan dan Bab 1–3 lengkap dalam pembaca 320 halaman. Korpus tetap diproduksi. D70 atau penguasaan setara diperlukan sebelum metode homologis lanjut.',
    edition: downloadUrl(d80Record.record_id, d80File.name),
    repository: d80Admission.repository,
    zenodo: doiUrl(d80Record.doi),
  });

  const d90Admission = admissionByCourse(admission, 'D90');
  const d90Record = publicRecord(admission, d90Admission.record);
  const d90Html = publicFile(d90Record, 'D90-O015-optimisasi-lanjut-analisis-konveks-id.html');
  const d90Pdf = publicFile(d90Record, 'D90-O015-optimisasi-lanjut-analisis-konveks-id.pdf');
  Object.assign(byCourse(catalog, 'D90'), {
    state: 'published',
    note: 'Edisi terintegrasi terminal Bahasa Indonesia lengkap dan terverifikasi publik: pembaca 141 halaman dan backend modular 4.877 rekaman.',
    reader: downloadUrl(d90Record.record_id, d90Html.name),
    edition: downloadUrl(d90Record.record_id, d90Pdf.name),
    zenodo: doiUrl(d90Record.doi),
  });

  recomputeCompletion(catalog);
  catalog.$schema = `https://zenodo.org/records/${options.recordId}/files/program-matematika-indonesia-catalog-v1.schema.json`;
  catalog.snapshotDate = options.snapshotDate;
  catalog.sourceCommit = options.sourceCommit;
  assertV062Semantics(catalog);
  return catalog;
}

function assertAdmissionEvidence(admission, readers, reservation) {
  assert.equal(admission.schema_id, 'program-matematika-indonesia/central-release-admission-manifest/v1');
  assert.equal(admission.target_release, version);
  assert.equal(admission.target_record_id, 22150264);
  assert.deepEqual(admission.summary.newly_completed_course_roles, ['B20', 'D90']);
  assert.equal(admission.summary.completed_public_course_roles_after, 21);
  assert.equal(admission.summary.distinct_completed_public_records_after, 20);
  assert.equal(admission.summary.prerequisite_edges_after, 83);
  assert.equal(admission.summary.learner_state_contract, 'browser-local completion, placement, equivalence, and edge-scoped waiver state; derived eligibility is not persisted');
  assert.deepEqual(admission.admissions.map((row) => row.course_id), ['A10', 'A30', 'B20', 'B40', 'D80', 'D90']);
  assert.equal(admissionByCourse(admission, 'A10').modules, '32/82');
  assert.equal(admissionByCourse(admission, 'A30').repository, 'https://github.com/KokunoYumeto/openstax-precalculus-2e-id');
  assert.equal(admissionByCourse(admission, 'B20').record, 21938930);
  assert.equal(admissionByCourse(admission, 'B40').record, 22070458);
  assert.equal(admissionByCourse(admission, 'D80').record, 22143171);
  assert.equal(admissionByCourse(admission, 'D90').record, 22142120);

  assert.equal(readers.schema_id, 'program-matematika-indonesia/owner-reader-public-readback/v1');
  assert.equal(readers.result, 'pass');
  assert.equal(readers.route_count, 7);
  assert.equal(readers.total_bytes, 41584175);
  assert.deepEqual(readers.source_admission_manifest, {
    path: '141_CENTRAL_V062_ADMISSION_MANIFEST_20260828.json',
    bytes: admissionIdentity.bytes,
    sha256: admissionIdentity.sha256,
  });
  const d90Routes = readers.routes.filter((row) => row.course_id === 'D90');
  assert.equal(d90Routes.length, 1);
  assert.equal(d90Routes[0].url, 'https://zenodo.org/records/22142120/files/D90-O015-optimisasi-lanjut-analisis-konveks-id.html?download=1');
  assert.equal(d90Routes[0].bytes, 2485595);
  assert.equal(d90Routes[0].sha256, '028e026033bc60bba1aff282f34b2e550a9f9358a3bdecd16b74e3442f743c89');

  assert.equal(reservation.schema_id, 'program-matematika-indonesia/zenodo-version-reservation/v1');
  assert.equal(reservation.result, 'pass');
  assert.equal(reservation.program_version, version);
  assert.equal(reservation.existing_concept.predecessor_record_id, predecessorIdentity.recordId);
  assert.equal(reservation.reserved_version.draft_record_id, 22150264);
  assert.equal(reservation.reserved_version.visibility_intent, 'public_open');
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
  assertAdmissionEvidence(admission.value, readers.value, reservation.value);
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

function findSurface(records, courseId, url, action) {
  const matches = records.filter((record) => record.record_type === 'reader_surface'
    && record.payload.url === url
    && record.payload.course_ids.includes(courseId)
    && record.payload.actions.includes(action));
  assert.equal(matches.length, 1, `${courseId}: expected exactly one ${action} surface for ${url}.`);
  return matches[0];
}

function makeOverlay({ courseId, surface, evidence, verifiedAt }) {
  return {
    course_id: courseId,
    surface_id: surface.id,
    url: surface.payload.url,
    source_publication_state: surface.payload.publication_state,
    effective_publication_state: 'public',
    evidence_kind: 'anonymous_public_byte_readback',
    bytes: evidence.bytes,
    sha256: evidence.sha256,
    verified_at: new Date(verifiedAt).toISOString(),
    evidence_sha256: evidence.evidenceSha256,
  };
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
  const records = parseRecords(recordsBytes);
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

  const recordFacts = new Map(admission.public_record_rechecks.map((row) => [row.record_id, row]));
  const evidenceRows = [
    ['A10', 22143518, '00-elementary-algebra-2e-bahasa-indonesia-EA2-S0032-reader.pdf', 'offline', admissionIdentity.sha256, admission.recorded_at],
    ['B20', 21938930, '00_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_BUKU_TEKS.pdf', 'offline', admissionIdentity.sha256, admission.recorded_at],
    ['B40', 22070458, '01_HEFFERON_LINEAR_ALGEBRA_ID_TEXTBOOK_2026.08.22.pdf', 'offline', admissionIdentity.sha256, admission.recorded_at],
    ['D80', 22143171, '00_METODE_DALAM_ALJABAR_JILID_2_ID_UNIT_050.pdf', 'offline', admissionIdentity.sha256, admission.recorded_at],
    ['D90', 22142120, 'D90-O015-optimisasi-lanjut-analisis-konveks-id.pdf', 'offline', admissionIdentity.sha256, admission.recorded_at],
  ];
  const newOverlays = evidenceRows.map(([courseId, recordId, name, action, evidenceSha256, verifiedAt]) => {
    const record = recordFacts.get(recordId);
    assert.ok(record);
    const file = publicFile(record, name);
    const url = downloadUrl(recordId, name);
    return makeOverlay({
      courseId,
      surface: findSurface(records, courseId, url, action),
      evidence: { ...file, evidenceSha256 },
      verifiedAt,
    });
  });
  const d90Route = readers.routes.find((row) => row.course_id === 'D90');
  assert.ok(d90Route);
  newOverlays.push(makeOverlay({
    courseId: 'D90',
    surface: findSurface(records, 'D90', d90Route.url, 'html'),
    evidence: { ...d90Route, evidenceSha256: ownerReaderIdentity.sha256 },
    verifiedAt: readers.recorded_at,
  }));

  const replacedCourseIds = new Set(['A10', 'B20', 'B40', 'D80', 'D90']);
  const preservedOverlays = predecessor.public_readback_overlays.filter((row) => !replacedCourseIds.has(row.course_id));
  const overlays = [...preservedOverlays, ...newOverlays];
  assert.equal(new Set(overlays.map((row) => row.surface_id)).size, overlays.length, 'Duplicate public-readback surface ID.');

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
      method: 'verified_v062_semantic_currency_complete_course_routes_and_learner_state_admission',
    },
  };
  authority.public_readback_overlays = overlays;
  assertV062Semantics(authority.catalog);

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
    new_overlays: newOverlays.length, total_overlays: overlays.length,
    candidate_output: candidateRelative,
  }, null, 2));
}

const mode = process.argv[2];
const project = resolve(optionalOption('--project-root') ?? defaultProject);
if (mode === 'seed') await seed(project);
else if (mode === 'promote') await promote(project);
else throw new Error('Usage: node scripts/advance-curriculum-authority-v062.mjs <seed|promote> --record-id N --source-commit SHA --snapshot-date YYYY-MM-DD --record-count N --dataset-count N --course-count N --reader-surfaces N --web-routes N --identity-crosswalks N --publication-events N --qa-events N [--federation-relative PATH] [--candidate-output PATH] [--project-root PATH] [--dry-run]');
