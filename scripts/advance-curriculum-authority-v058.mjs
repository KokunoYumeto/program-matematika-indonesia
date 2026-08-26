import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const version = '0.58.0';
const federationVersion = '0.4.0';
const authorityRelative = 'backend/authority/curriculum-authority-v1.json';
const historyRelative = 'backend/authority/history/curriculum-authority-v0.57.0.json';
const seedRelative = `backend/authority/catalogs/program-matematika-indonesia-catalog-v${version}.json`;

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');

function option(name) {
  const index = process.argv.indexOf(name);
  if (index === -1 || !process.argv[index + 1]) throw new Error(`Missing required option ${name}.`);
  return process.argv[index + 1];
}

function integerOption(name) {
  const value = Number(option(name));
  assert.ok(Number.isInteger(value) && value > 0, `${name} must be a positive integer.`);
  return value;
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

function assertPredecessor(predecessor) {
  assert.equal(predecessor.schema_id, 'interlanguage/program-matematika-indonesia-curriculum-authority/v1');
  assert.equal(predecessor.catalog.program.version, '0.57.0');
  assert.equal(predecessor.catalog.program.zenodo, 'https://doi.org/10.5281/zenodo.22104174');
  assert.equal(predecessor.catalog.program.zenodoConcept, 'https://doi.org/10.5281/zenodo.22059707');
}

function updateCourse(catalog, id, update) {
  const course = catalog.courses.find((item) => item.id === id);
  assert.ok(course, `Missing course ${id}.`);
  Object.assign(course, update);
}

function applyOwnerPublications(catalog) {
  const program = catalog.program;
  program.completedPublicCourseRoleIds = [...new Set([...program.completedPublicCourseRoleIds, 'B60'])]
    .sort((a, b) => a.localeCompare(b, 'en', { numeric: true }));
  const refreshedCompletedRecordDois = program.completedPublicRecordDois
    .map((doi) => doi === '10.5281/zenodo.22082567' ? '10.5281/zenodo.22105195' : doi);
  program.completedPublicRecordDois = [...new Set([
    ...refreshedCompletedRecordDois,
    '10.5281/zenodo.22105443',
  ])];
  assert.ok(!program.completedPublicRecordDois.includes('10.5281/zenodo.22082567'));

  updateCourse(catalog, 'A10', {
    state: 'production',
    note: 'Checkpoint publik v0.10.0-wip EA2-S0031 memuat 31 dari 82 modul sebagai snapshot modular nonkontigu dan pembaca 984 halaman. Cakupan tidak dinyatakan sebagai awalan buku yang berurutan; buku tetap diproduksi.',
    edition: 'https://zenodo.org/records/22105421/files/00-elementary-algebra-2e-bahasa-indonesia-EA2-S0031-reader.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22105421',
  });
  updateCourse(catalog, 'A30', {
    state: 'production',
    note: 'Checkpoint publik alpha.32 memuat 32 dari 87 modul secara berurutan sampai m49367, Model Eksponensial dan Logaritma. Pembaca A4 947 halaman lolos dua build identik-byte dan inspeksi visual; 16 media yang belum lolos gerbang hak tetap dikarantina. Buku tetap diproduksi.',
    edition: 'https://zenodo.org/records/22105534/files/OpenStax-Precalculus-2e-id-ID-0.1.0-alpha.32-reader.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22105534',
  });
  updateCourse(catalog, 'B60', {
    state: 'published',
    note: 'CLP Calculus 4 lengkap dan terverifikasi publik: buku teks 316 halaman, buku latihan 486 halaman, seluruh permukaan PreTeXt/LaTeX, aset, hak, sumber, backend, dan build deterministik. Buku latihan ditampilkan sebagai sumber belajar tambahan, bukan disembunyikan di backend.',
    edition: 'https://zenodo.org/records/22105443/files/CLP-4-Kalkulus-Vektor-Bahasa-Indonesia.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/clp4-vector-calculus-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22105443',
    supplements: [{
      id: 'clp4-problem-book-complete',
      title: 'Buku latihan CLP4 lengkap',
      resourceType: 'problem-book',
      state: 'complete',
      scope: 'Seluruh buku latihan kalkulus vektor, 486 halaman.',
      license: 'CC BY-NC-SA 4.0',
      pages: 486,
      url: 'https://zenodo.org/records/22105443/files/CLP-4-Latihan-Kalkulus-Vektor-Bahasa-Indonesia.pdf?download=1',
      zenodo: 'https://doi.org/10.5281/zenodo.22105443',
      conceptDoi: 'https://doi.org/10.5281/zenodo.22105442',
      bytes: 3939483,
      sha256: 'a6253809eaa4a465d5efcc4372b1321ad828aa4964ec45042aab9130a358835b',
    }],
  });

  const leblCommon = {
    repository: 'https://github.com/KokunoYumeto/lebl-mathematics-family-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22105195',
  };
  updateCourse(catalog, 'B70', {
    ...leblCommon,
    state: 'production',
    note: 'Checkpoint publik U397 memuat 35 unit R007 dan pembaca 40 halaman untuk bab sistem nonlinear yang sudah lengkap. Jalur PDB orde pertama tetap aktif pada baris sumber mentah 89; pembaca ini bukan korpus B70 lengkap.',
    edition: 'https://zenodo.org/records/22105195/files/Notes_on_Diffy_Qs_Bab_8_Sistem_Nonlinear_Bahasa_Indonesia_v6.11_PARSIAL.pdf?download=1',
  });
  updateCourse(catalog, 'C10', {
    ...leblCommon,
    state: 'published',
    note: 'Analisis Dasar Jilid I lengkap, 334 halaman, dan terverifikasi publik pada U397. Keluarga Lebl memuat 397 unit: R006 312, R007 35, dan R008 50.',
    edition: 'https://zenodo.org/records/22105195/files/Analisis_Dasar_I_Bahasa_Indonesia_v6.3.pdf?download=1',
  });
  updateCourse(catalog, 'C20', {
    ...leblCommon,
    state: 'production',
    note: 'Checkpoint publik U397 memuat pembaca Jilid II terpusat 226 halaman sampai akhir Subbagian 11.8.1, Polinom Trigonometrik. C20 tetap pekerjaan berjalan.',
    edition: 'https://zenodo.org/records/22105195/files/Analisis_Dasar_II_Bahasa_Indonesia_v6.3_WIP_sampai_11.8.1_Polinom_Trigonometrik.pdf?download=1',
  });
  updateCourse(catalog, 'C50', {
    ...leblCommon,
    state: 'production',
    note: 'Checkpoint publik U397 mempertahankan 50 unit R008 sampai akhir bagian bola Riemann. Korpus Analisis Kompleks tetap diproduksi dan belum mempunyai pembaca mandiri.',
    edition: 'https://github.com/KokunoYumeto/lebl-mathematics-family-id/releases/tag/lebl-family-id-wip.2026.08.26.u397',
  });

  updateCourse(catalog, 'C100', {
    reader: 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/reader/',
    note: 'Kursus utama selesai dan terverifikasi publik: tulang punggung Petrunin yang bersih hak, 253 solusi, pendamping konektif asli enam unit beserta solusi, empat pemeriksaan kumulatif, dua capstone, backend, HTML semantik, dan EPUB. Workbook Clemens/Snapp tetap pada lini CC BY-NC-SA terpisah; checkpoint Unit 001–010 tersedia sebagai sumber tambahan parsial.',
    supplements: [{
      id: 'clemens-snapp-workbook-u010',
      title: 'Buku kerja geometri dua dimensi, Unit 001–010',
      resourceType: 'workbook',
      state: 'partial',
      scope: 'Unit 001–010, pembaca 110 halaman; lini lisensi terpisah dari kursus utama.',
      license: 'CC BY-NC-SA 4.0',
      pages: 110,
      url: 'https://zenodo.org/records/22105520/files/buku-kerja-geometri-dua-dimensi-id-unit001-010.pdf?download=1',
      zenodo: 'https://doi.org/10.5281/zenodo.22105520',
      conceptDoi: 'https://doi.org/10.5281/zenodo.22105519',
      bytes: 595201,
      sha256: '5cc3f36cf9b01e6d0bc568f54f7170ae4dde71d16d3b55d26739ed1f8d9201a7',
    }],
  });

  updateCourse(catalog, 'D10', {
    state: 'production',
    note: 'Checkpoint publik v0.17.0 memuat 338 dari 672 halaman: Jilid I lengkap dan Jilid II halaman 1–236 sampai Bagian 252. Bab 25 masih parsial dan korpus tetap diproduksi.',
    edition: 'https://zenodo.org/records/22105474/files/00_READ_FIRST_FONDASI_TEORI_UKURAN_V1_DAN_V2_HINGGA_BAGIAN_252.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/fremlin-measure-theory-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22105474',
  });
  updateCourse(catalog, 'D40', {
    state: 'production',
    note: 'Unit 12 Dionne telah terbit sebagai pembaca kumulatif 154 halaman, 8.722.345 byte, SHA-256 7733f5f4d264ced9fc7a8404f5570522442a2ae5c25a4c6b4188dd2f50c2d735. Bab fungsi khusus selesai pada batas ini; distribusi, irisan FEniCSx, dan penutupan asli tetap diproduksi.',
    edition: 'https://zenodo.org/records/22103731/files/PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_UNIT_12.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22103731',
  });
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
  program.backend.educationalAccessResearch.sourcePackage = `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-source-v${version}.zip?download=1`;
}

function buildSeed(predecessor, options) {
  const catalog = structuredClone(predecessor.catalog);
  applyOwnerPublications(catalog);
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
  assert.equal(catalog.counts.completedPublicCourseRoles, 18);
  assert.equal(catalog.counts.completedPublicRecords, 17);
  return catalog;
}

async function seed() {
  const options = {
    recordId: integerOption('--record-id'),
    sourceCommit: option('--source-commit'),
    snapshotDate: option('--snapshot-date'),
    ...expectedCountOptions(),
  };
  assert.match(options.sourceCommit, /^[0-9a-f]{40}$/);
  assert.match(options.snapshotDate, /^\d{4}-\d{2}-\d{2}$/);
  const predecessor = JSON.parse(await readFile(resolve(project, authorityRelative), 'utf8'));
  assertPredecessor(predecessor);
  const catalog = buildSeed(predecessor, options);
  const bytes = canonical(catalog);
  await mkdir(resolve(project, dirname(seedRelative)), { recursive: true });
  await writeFile(resolve(project, seedRelative), bytes);
  console.log(JSON.stringify({ mode: 'seed', path: seedRelative, bytes: bytes.length, sha256: sha256(bytes) }, null, 2));
}

const overlayFacts = [
  ['A10', 'https://zenodo.org/records/22105421/files/00-elementary-algebra-2e-bahasa-indonesia-EA2-S0031-reader.pdf?download=1', 41677159, 'adb18d25ecde88868e58f75c0d3b366121e499d5f1c44df71e048ee4f6482744', '2026-08-26T04:49:37Z'],
  ['A30', 'https://zenodo.org/records/22105534/files/OpenStax-Precalculus-2e-id-ID-0.1.0-alpha.32-reader.pdf?download=1', 107019966, 'a50644d6e14bea0a9bc18ce52f4052deb2830397bc78e98dc03a75dacb0dc788', '2026-08-26T04:49:37Z'],
  ['B60', 'https://zenodo.org/records/22105443/files/CLP-4-Kalkulus-Vektor-Bahasa-Indonesia.pdf?download=1', 3758521, '5ecf6047b63afd4a456cc230f69016aea59d80cd0bd2be73ce24b0000df98b87', '2026-08-26T04:49:37Z'],
  ['B70', 'https://zenodo.org/records/22105195/files/Notes_on_Diffy_Qs_Bab_8_Sistem_Nonlinear_Bahasa_Indonesia_v6.11_PARSIAL.pdf?download=1', 1524418, '8d392ef36104027fd680d1bfd73a153ea3e69ead1d4c6867143ab9d2f8f6c3ad', '2026-08-26T04:49:37Z'],
  ['C10', 'https://zenodo.org/records/22105195/files/Analisis_Dasar_I_Bahasa_Indonesia_v6.3.pdf?download=1', 2870909, '38743ea0e7ce52bdadf5233fc9d6e79e00717f9ba55a393f2bf46ea21c65ef56', '2026-08-26T04:49:37Z'],
  ['C20', 'https://zenodo.org/records/22105195/files/Analisis_Dasar_II_Bahasa_Indonesia_v6.3_WIP_sampai_11.8.1_Polinom_Trigonometrik.pdf?download=1', 2292242, '40b2e2cb27dd59d288ef76453ae293558fcd1ae8efb96e1e87a646f8f0b8f73d', '2026-08-26T04:49:37Z'],
  ['D10', 'https://zenodo.org/records/22105474/files/00_READ_FIRST_FONDASI_TEORI_UKURAN_V1_DAN_V2_HINGGA_BAGIAN_252.pdf?download=1', 2500114, '6ba03a3dd30f4172cd3f2a4949ac5ef37ac27931f7b302b961ae888c17b875f4', '2026-08-26T04:49:37Z'],
  ['D40', 'https://zenodo.org/records/22103731/files/PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_UNIT_12.pdf?download=1', 8722345, '7733f5f4d264ced9fc7a8404f5570522442a2ae5c25a4c6b4188dd2f50c2d735', '2026-08-26T04:49:37Z'],
];

async function promote() {
  const recordId = integerOption('--record-id');
  const snapshotDate = option('--snapshot-date');
  const federationRelative = option('--federation-relative').replaceAll('\\', '/');
  const expectedCounts = expectedCountOptions();
  assert.match(snapshotDate, /^\d{4}-\d{2}-\d{2}$/);
  assert.ok(!federationRelative.startsWith('/') && !federationRelative.includes('..'));
  const authorityPath = resolve(project, authorityRelative);
  const predecessorBytes = await readFile(authorityPath);
  const predecessor = JSON.parse(predecessorBytes.toString('utf8'));
  assertPredecessor(predecessor);
  const seedBytes = await readFile(resolve(project, seedRelative));
  const catalog = JSON.parse(seedBytes.toString('utf8'));
  assert.equal(catalog.program.version, version);
  assert.equal(catalog.program.zenodo, `https://doi.org/10.5281/zenodo.${recordId}`);

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
  assert.equal(catalog.program.backend.federationV2.recordCount, expectedCounts.recordCount);
  assert.equal(catalog.program.backend.federationV2.datasetCount, expectedCounts.datasetCount);
  assert.equal(catalog.program.backend.federationV2.courseCount, expectedCounts.courseCount);
  assert.equal(catalog.program.backend.federationV2.learnerSurfaceCount, expectedCounts.readerSurfaces);
  assert.equal(catalog.program.backend.federationV2.webRouteCount, expectedCounts.webRoutes);
  assert.equal(catalog.program.backend.federationV2.identityCrosswalkCount, expectedCounts.identityCrosswalks);
  assert.equal(catalog.program.backend.federationV2.publicationEventCount, expectedCounts.publicationEvents);
  assert.equal(catalog.program.backend.federationV2.qaEventCount, expectedCounts.qaEvents);
  assert.equal(manifest.record_count, expectedCounts.recordCount);
  assert.equal(manifest.record_counts.datasets, expectedCounts.datasetCount);
  assert.equal(manifest.record_counts.courses, expectedCounts.courseCount);
  assert.equal(manifest.record_counts.reader_surfaces, expectedCounts.readerSurfaces);
  assert.equal(manifest.record_counts.web_routes, expectedCounts.webRoutes);
  assert.equal(manifest.record_counts.identity_crosswalks, expectedCounts.identityCrosswalks);
  assert.equal(manifest.record_counts.publication_events, expectedCounts.publicationEvents);
  assert.equal(manifest.record_counts.qa_events, expectedCounts.qaEvents);
  const recordsManifestEntry = manifest.files.find((entry) => entry.path === 'records.jsonl');
  assert.ok(recordsManifestEntry, 'Federation manifest does not bind records.jsonl.');
  assert.equal(recordsManifestEntry.bytes, recordsBytes.length);
  assert.equal(recordsManifestEntry.sha256, sha256(recordsBytes));
  assert.equal(validation.checks.record_count, expectedCounts.recordCount);
  assert.equal(validation.checks.records_jsonl_sha256, sha256(recordsBytes));
  assert.equal(validation.checks.manifest_sha256, sha256(manifestBytes));

  const records = recordsBytes.toString('utf8').trim().split('\n').map(JSON.parse);
  const newOverlays = overlayFacts.map(([courseId, url, bytes, digest, verifiedAt]) => {
    const surface = records.find((record) => record.record_type === 'reader_surface'
      && record.payload.url === url
      && record.payload.course_ids.includes(courseId));
    assert.ok(surface, `${courseId}: public PDF surface is missing.`);
    assert.equal(surface.payload.publication_state, 'catalog_declared');
    return {
      course_id: courseId,
      surface_id: surface.id,
      url,
      source_publication_state: 'catalog_declared',
      effective_publication_state: 'public',
      evidence_kind: 'anonymous_public_byte_readback',
      bytes,
      sha256: digest,
      verified_at: verifiedAt,
    };
  });
  assert.equal(newOverlays.length, 8);
  assert.equal(predecessor.public_readback_overlays.length, 3);
  assert.deepEqual(
    predecessor.public_readback_overlays.map((item) => item.course_id).sort(),
    ['C100', 'C110', 'C80'].sort(),
  );

  const historyPath = resolve(project, historyRelative);
  await mkdir(dirname(historyPath), { recursive: true });
  await writeFile(historyPath, predecessorBytes);
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
    bootstrap_release_version: '0.53.0',
    predecessor_authority: { path: historyRelative, bytes: predecessorBytes.length, sha256: sha256(predecessorBytes) },
    transition: {
      from_version: '0.57.0',
      to_version: version,
      snapshot_date: snapshotDate,
      zenodo_record_id: recordId,
      method: 'controlled_owner_handoff_admission_with_hash_bound_public_readback',
    },
  };
  authority.public_readback_overlays = [...predecessor.public_readback_overlays, ...newOverlays];
  assert.equal(new Set(authority.public_readback_overlays.map((item) => item.surface_id)).size, authority.public_readback_overlays.length);
  assert.equal(authority.public_readback_overlays.length, 11);
  const outputBytes = canonical(authority);
  await writeFile(authorityPath, outputBytes);
  console.log(JSON.stringify({
    mode: 'promote',
    path: authorityRelative,
    bytes: outputBytes.length,
    sha256: sha256(outputBytes),
    federation: federationRelative,
    overlays: authority.public_readback_overlays.length,
  }, null, 2));
}

const mode = process.argv[2];
if (mode === 'seed') await seed();
else if (mode === 'promote') await promote();
else throw new Error('Usage: node scripts/advance-curriculum-authority-v058.mjs <seed|promote> ...');
