import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { gzipSync } from 'node:zlib';
import { courses, nextCourseIdsById, program, topics } from '../docs/courses.js';
import { learnerDeliveryByCourseId, learnerDeliveryRows } from '../docs/learner-delivery.js';
import {
  deriveNextCourseIdsById,
  liveCoursePublications,
  materializeLiveCourses,
} from '../docs/live-course-publications.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const readJson = async (relative) => JSON.parse(await readFile(resolve(root, relative), 'utf8'));
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const escapeRegex = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const effectiveCourses = materializeLiveCourses(courses);
const effectiveCoursesById = new Map(effectiveCourses.map((course) => [course.id, course]));
const effectiveNextCourseIdsById = deriveNextCourseIdsById(effectiveCourses);
const effectivePublishedCourses = effectiveCourses.filter(({ state }) => state === 'published');
const effectivePublishedRecordDois = new Set(effectivePublishedCourses.map(({ zenodo }) => zenodo).filter(Boolean));

const [
  html,
  app,
  livePublicationsModule,
  learnerStateModule,
  catalogSchema,
  authorityBytes,
  publicAuthorityBytes,
  learnerReadModelBytes,
  educationalAccess,
  educationalAccessSchemaBytes,
  learnerStateSchemaBytes,
  publicLearnerStateSchemaBytes,
  b95Landing,
  d40ReaderIndexBytes,
  d30Landing,
  c100Landing,
  c100ReaderBytes,
  c100ReaderStyleBytes,
  c100SolutionBytes,
  c100RouteManifest,
  d20RouteManifest,
  legacyD20RouteBytes,
  d20RouteBytes,
  routeManifestV21,
  rootReadme,
  backendV23Readme,
  schemaV23Index,
] = await Promise.all([
  readFile(resolve(root, 'docs/index.html'), 'utf8'),
  readFile(resolve(root, 'docs/app.js'), 'utf8'),
  readFile(resolve(root, 'docs/live-course-publications.js'), 'utf8'),
  readFile(resolve(root, 'docs/learner-state.js'), 'utf8'),
  readJson('schemas/catalog-v1.schema.json'),
  readFile(resolve(root, 'backend/authority/curriculum-authority-v1.json')),
  readFile(resolve(root, 'docs/data/curriculum-authority-v1.json')),
  readFile(resolve(root, 'docs/data/learner-read-model.json')),
  readJson('docs/data/educational-access.json'),
  readFile(resolve(root, 'docs/schema/educational-access-federation-v1.schema.json')),
  readFile(resolve(root, 'schemas/v1/learner-state-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/v1/learner-state-v1.schema.json')),
  readFile(resolve(root, 'docs/id-ID/courses/B95/index.html'), 'utf8'),
  readFile(resolve(root, 'docs/readers/d40/unit14/index.html')),
  readFile(resolve(root, 'docs/id-ID/courses/D30/index.html'), 'utf8'),
  readFile(resolve(root, 'docs/id-ID/courses/C100/index.html'), 'utf8'),
  readFile(resolve(root, 'docs/id-ID/courses/C100/reader/index.html')),
  readFile(resolve(root, 'docs/id-ID/courses/C100/reader/style.css')),
  readFile(resolve(root, 'docs/id-ID/courses/C100/solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf')),
  readJson('docs/data/unit-route-C100-v2.1.json'),
  readJson('docs/data/unit-route-D20-v2.1.json'),
  readFile(resolve(root, 'docs/data/unit-route-v2.1.json')),
  readFile(resolve(root, 'docs/data/unit-route-D20-v2.1.json')),
  readJson('docs/data/unit-routes-v2.1.json'),
  readFile(resolve(root, 'README.md'), 'utf8'),
  readFile(resolve(root, 'backend/v2.3/README.md'), 'utf8'),
  readFile(resolve(root, 'docs/schema/v2.3/index.html'), 'utf8'),
]);

const [
  stylesBytes,
  coursesModuleBytes,
  deliveryModuleBytes,
  learnerDeliveryAuthorityBytes,
  learnerDeliveryPublicBytes,
  learnerDeliverySchemaBytes,
  publicLearnerDeliverySchemaBytes,
  modularBackendPatternAuthorityBytes,
  modularBackendPatternPublicBytes,
  v23AdapterIndexAuthorityBytes,
  v23AdapterIndexPublicBytes,
  v23AdapterIndexSchemaBytes,
  v23AdapterIndexPublicSchemaBytes,
  standaloneBytes,
] = await Promise.all([
  readFile(resolve(root, 'docs/styles.css')),
  readFile(resolve(root, 'docs/courses.js')),
  readFile(resolve(root, 'docs/learner-delivery.js')),
  readFile(resolve(root, 'backend/authority/learner-delivery-v1.json')),
  readFile(resolve(root, 'docs/data/learner-delivery-v1.json')),
  readFile(resolve(root, 'schemas/v1/learner-delivery-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/v1/learner-delivery-v1.schema.json')),
  readFile(resolve(root, 'backend/authority/modular-backend-pattern-index-v1.json')),
  readFile(resolve(root, 'docs/data/modular-backend-pattern-index-v1.json')),
  readFile(resolve(root, 'backend/authority/v23-adapter-index-v1.json')),
  readFile(resolve(root, 'docs/data/v23-adapter-index-v1.json')),
  readFile(resolve(root, 'schemas/v1/v23-adapter-index-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/v1/v23-adapter-index-v1.schema.json')),
  readFile(resolve(root, 'docs/peta-belajar-luring.html')),
]);

const authority = JSON.parse(authorityBytes.toString('utf8'));
const catalog = authority.catalog;
const learnerReadModel = JSON.parse(learnerReadModelBytes.toString('utf8'));
const learnerDelivery = JSON.parse(learnerDeliveryAuthorityBytes.toString('utf8'));
const modularBackendPatternIndex = JSON.parse(modularBackendPatternAuthorityBytes.toString('utf8'));
const v23AdapterIndex = JSON.parse(v23AdapterIndexAuthorityBytes.toString('utf8'));
assert.ok(catalog && typeof catalog === 'object', 'Otoritas tidak memuat katalog kanonik.');
assert.deepEqual(publicAuthorityBytes, authorityBytes, 'Salinan otoritas publik harus identik byte demi byte.');
assert.deepEqual(courses, catalog.courses, 'Proyeksi courses.js berbeda dari katalog otoritas.');
assert.deepEqual(topics, catalog.topics, 'Topik courses.js berbeda dari katalog otoritas.');
assert.deepEqual(program, catalog.program, 'Metadata program courses.js berbeda dari katalog otoritas.');
assert.deepEqual(
  learnerReadModel.courses.map(({ federation, ...course }) => course),
  catalog.courses,
  'Model baca pelajar berbeda dari katalog otoritas.',
);
assert.deepEqual(learnerReadModel.program, catalog.program, 'Program model baca berbeda dari otoritas.');
assert.deepEqual(learnerReadModel.topics, catalog.topics, 'Topik model baca berbeda dari otoritas.');
assert.equal(learnerReadModel.provenance.authority_sha256, sha256(authorityBytes));
assert.deepEqual(learnerDeliveryPublicBytes, learnerDeliveryAuthorityBytes, 'Salinan publik learner-delivery harus identik byte demi byte.');
assert.deepEqual(publicLearnerDeliverySchemaBytes, learnerDeliverySchemaBytes, 'Salinan skema learner-delivery harus identik byte demi byte.');
assert.deepEqual(modularBackendPatternPublicBytes, modularBackendPatternAuthorityBytes, 'Salinan publik indeks pola backend harus identik byte demi byte.');
assert.equal(modularBackendPatternIndex.methodology.denominator.native_implementation_families, 33);
assert.equal(modularBackendPatternIndex.methodology.denominator.program_roles, 40);
assert.equal(modularBackendPatternIndex.post_audit_updates.d20_adapter.canonical_records, 138894);
assert.deepEqual(v23AdapterIndexPublicBytes, v23AdapterIndexAuthorityBytes, 'Salinan publik indeks adapter v2.3 harus identik byte demi byte.');
assert.deepEqual(v23AdapterIndexPublicSchemaBytes, v23AdapterIndexSchemaBytes, 'Salinan publik skema indeks adapter v2.3 harus identik byte demi byte.');
assert.equal(v23AdapterIndex.$schema, JSON.parse(v23AdapterIndexSchemaBytes.toString('utf8')).$id);
assert.deepEqual(v23AdapterIndex.summary, {
  curriculum_roles: 40,
  proof_roles: 5,
  legacy_proofs: 1,
  contract_2_3_1_adapters: 4,
  unbound_roles: 35,
});
assert.deepEqual(v23AdapterIndex.adapters.map(({ role_id }) => role_id), ['A00', 'B10', 'D20', 'D60', 'D110']);
for (const adapter of v23AdapterIndex.adapters) {
  for (const identity of [adapter.archive, adapter.manifest].filter(Boolean)) {
    const bytes = await readFile(resolve(root, identity.path));
    assert.equal(bytes.length, identity.bytes, `${adapter.role_id}: byte count indeks adapter berubah untuk ${identity.path}.`);
    assert.equal(sha256(bytes), identity.sha256, `${adapter.role_id}: SHA-256 indeks adapter berubah untuk ${identity.path}.`);
  }
}
assert.equal(learnerDelivery.$schema, JSON.parse(learnerDeliverySchemaBytes.toString('utf8')).$id);
assert.equal(learnerDelivery.courses.length, 40);
assert.equal(new Set(learnerDelivery.courses.map(({ course_id }) => course_id)).size, 40);
assert.deepEqual(learnerDelivery.courses.map(({ course_id }) => course_id), courses.map(({ id }) => id));
assert.deepEqual(learnerDeliveryRows.map(({ course_id }) => course_id), courses.map(({ id }) => id));
assert.deepEqual(Object.keys(learnerDeliveryByCourseId), courses.map(({ id }) => id));

const ids = courses.map(({ id }) => id);
const idSet = new Set(ids);
assert.equal(ids.length, idSet.size, 'Kode mata kuliah harus unik.');
assert.equal(catalog.counts.courseRoles, courses.length, 'Jumlah peran katalog tidak cocok.');
assert.equal(program.totalCourseRoles, courses.length, 'Jumlah peran program tidak cocok.');
const selectedIds = courses.filter(({ state }) => state !== 'unresolved').map(({ id }) => id);
const unresolvedIds = courses.filter(({ state }) => state === 'unresolved').map(({ id }) => id);
const publishedIds = courses.filter(({ state }) => state === 'published').map(({ id }) => id);
if (program.version === '0.62.0') {
  assert.equal(publishedIds.length, 21, 'v0.62 must expose exactly 21 completed roles.');
  assert.equal(program.completedPublicRecordDois.length, 20, 'v0.62 must expose exactly 20 distinct completed records.');
  assert.ok(publishedIds.includes('B20') && publishedIds.includes('D90'));
  assert.match(courses.find(({ id }) => id === 'A10').zenodo, /22143518$/);
  assert.equal(courses.find(({ id }) => id === 'A30').repository, 'https://github.com/KokunoYumeto/openstax-precalculus-2e-id');
  assert.equal(courses.find(({ id }) => id === 'B20').supplements.length, 1);
  assert.equal(courses.find(({ id }) => id === 'B40').supplements.length, 2);
  assert.match(courses.find(({ id }) => id === 'D90').zenodo, /22142120$/);
  assert.equal(program.backend.learnerStateV1.storage, 'browser-local');
  assert.equal(program.backend.learnerStateV1.derivedEligibilityPersisted, false);
}
const publishedHtmlReaderIds = courses.filter(({ reader }) => reader).map(({ id }) => id);
assert.equal(catalog.counts.selectedCorpusRoles, selectedIds.length);
assert.equal(catalog.counts.unresolvedRoles, unresolvedIds.length);
assert.equal(catalog.counts.completedPublicCourseRoles, publishedIds.length);
assert.equal(catalog.counts.completedPublicRecords, program.completedPublicRecordDois.length);
assert.deepEqual(program.unresolvedRoleIds, unresolvedIds);
assert.deepEqual(program.completedPublicCourseRoleIds, publishedIds);
assert.equal(new Set(program.completedPublicRecordDois).size, program.completedPublicRecordDois.length);
assert.equal(program.website, 'https://kokunoyumeto.github.io/program-matematika-indonesia/');
assert.match(program.zenodo, /^https:\/\/doi\.org\/10\.5281\/zenodo\.\d+$/);
assert.match(program.zenodoConcept, /^https:\/\/doi\.org\/10\.5281\/zenodo\.\d+$/);
const centralRecordId = program.zenodo.match(/zenodo\.(\d+)$/)[1];
assert.equal(program.provenance.model, 'OpenAI Codex gpt-5.6-sol, Ultra');
assert.equal(program.backend.status, 'validated');
assert.equal(program.repositories.github.status, 'available');
assert.equal(catalogSchema.$id, catalog.$schema, 'Identitas schema katalog berbeda dari rujukan katalog.');

const allowedStates = new Set(['published', 'near', 'production', 'unresolved']);
for (const course of courses) {
  assert.ok(allowedStates.has(course.state), `${course.id}: status tidak dikenal.`);
  assert.ok(topics.includes(course.topic), `${course.id}: bidang tidak tercantum.`);
  assert.equal(course.level, course.id[0], `${course.id}: tingkat tidak cocok dengan kode.`);
  assert.ok(typeof course.ownerLane === 'string' && course.ownerLane.trim(), `${course.id}: pemilik kosong.`);
  for (const prerequisite of course.prerequisites) {
    assert.ok(idSet.has(prerequisite), `${course.id}: prasyarat ${prerequisite} tidak ditemukan.`);
    assert.notEqual(prerequisite, course.id, `${course.id}: prasyarat tidak boleh menunjuk dirinya sendiri.`);
  }
  for (const field of ['title', 'purpose', 'outcome', 'corpus', 'note']) {
    assert.ok(typeof course[field] === 'string' && course[field].trim(), `${course.id}: ${field} kosong.`);
  }
  for (const field of ['reader', 'edition', 'repository', 'zenodo']) {
    if (course[field]) assert.match(course[field], /^https:\/\//, `${course.id}: ${field} harus memakai HTTPS.`);
  }
  if (course.state === 'published') {
    assert.ok(course.edition, `${course.id}: edisi selesai tidak memiliki rute baca/unduh.`);
  }
}

const liveOverlayRequiredRoleIds = ['A10', 'A20', 'A30', 'B20', 'B30', 'B50', 'B95', 'C10', 'C20', 'C90', 'C100', 'C140', 'D10', 'D20', 'D30', 'D40', 'D50', 'D60', 'D70', 'D100'];
for (const id of liveOverlayRequiredRoleIds) {
  assert.ok(liveCoursePublications[id], `${id}: baris lama belum memiliki overlay publikasi langsung.`);
}
assert.deepEqual(effectiveCourses.map(({ id }) => id), courses.map(({ id }) => id), 'Overlay mengubah urutan atau identitas mata kuliah.');
assert.equal(effectiveCourses.length, courses.length, 'Overlay mengubah jumlah mata kuliah.');
assert.equal(effectivePublishedCourses.length, 29, 'Overlay harus menampilkan tepat 29 peran dengan edisi selesai.');
assert.equal(effectivePublishedRecordDois.size, 28, 'Dua puluh sembilan peran selesai harus memakai tepat 28 rekaman edisi berbeda.');
const progressStageKeys = ['translationBearingUnits', 'integrationReadyUnits', 'canonicalUnits', 'publicUnits'];
for (const course of effectiveCourses) {
  assert.ok(allowedStates.has(course.state), `${course.id}: status efektif tidak dikenal.`);
  for (const prerequisite of course.prerequisites) {
    assert.ok(idSet.has(prerequisite), `${course.id}: prasyarat efektif ${prerequisite} tidak ditemukan.`);
  }
  for (const field of ['learner', 'reader', 'edition', 'repository', 'zenodo', 'release']) {
    if (course[field] !== undefined && course[field] !== null) {
      assert.match(course[field], /^https:\/\//, `${course.id}: ${field} efektif harus memakai HTTPS atau null.`);
    }
  }
  assert.ok(!Object.hasOwn(course, 'additionalSupplements'), `${course.id}: additionalSupplements bocor ke baris efektif.`);
  for (const supplement of course.supplements ?? []) {
    assert.ok(typeof supplement.title === 'string' && supplement.title.trim(), `${course.id}: judul suplemen kosong.`);
    assert.match(supplement.url, /^https:\/\//, `${course.id}: URL suplemen harus memakai HTTPS.`);
  }
  if (!course.progress) continue;
  const progress = course.progress;
  assert.ok(typeof progress.unitLabel === 'string' && progress.unitLabel.trim(), `${course.id}: unitLabel progres kosong.`);
  assert.ok(!Number.isNaN(Date.parse(progress.updatedAt)), `${course.id}: updatedAt progres tidak valid.`);
  for (const key of [...progressStageKeys, 'totalUnits', 'totalPages', 'publicPages']) {
    if (progress[key] === undefined) continue;
    assert.ok(Number.isInteger(progress[key]) && progress[key] >= 0, `${course.id}: ${key} harus bilangan bulat nonnegatif.`);
    if (key.endsWith('Units') && key !== 'totalUnits' && progress.totalUnits !== undefined) {
      assert.ok(progress[key] <= progress.totalUnits, `${course.id}: ${key} melebihi totalUnits.`);
    }
  }
  const stages = progressStageKeys.map((key) => progress[key]).filter(Number.isInteger);
  for (let index = 1; index < stages.length; index += 1) {
    assert.ok(stages[index - 1] >= stages[index], `${course.id}: urutan tahap progres tidak monoton.`);
  }
}
assert.deepEqual(
  effectiveNextCourseIdsById,
  Object.fromEntries(effectiveCourses.map(({ id }) => [id, effectiveCourses.filter(({ prerequisites }) => prerequisites.includes(id)).map(({ id: nextId }) => nextId)])),
  'Peta lanjut efektif bukan pembalikan prasyarat efektif.',
);

const syntheticAuthority = [
  { id: 'A00', state: 'production', prerequisites: [], supplements: [{ title: 'lama', url: 'https://example.org/old' }] },
  { id: 'A10', state: 'production', prerequisites: ['A00'] },
];
const syntheticBefore = JSON.stringify(syntheticAuthority);
const syntheticEffective = materializeLiveCourses(syntheticAuthority, {
  A00: { state: 'published', edition: null, supplements: [] },
  A10: { prerequisites: [], additionalSupplements: [{ title: 'baru', url: 'https://example.org/new' }] },
});
assert.equal(syntheticEffective[0].state, 'published');
assert.equal(syntheticEffective[0].edition, null, 'Null eksplisit harus membersihkan URL lama.');
assert.deepEqual(syntheticEffective[0].supplements, [], 'Daftar suplemen eksplisit harus menggantikan daftar lama.');
assert.deepEqual(syntheticEffective[1].supplements.map(({ title }) => title), ['baru'], 'Suplemen tambahan tidak digabungkan.');
assert.deepEqual(deriveNextCourseIdsById(syntheticEffective), { A00: [], A10: [] }, 'Prasyarat efektif tidak mengubah peta lanjut.');
assert.equal(JSON.stringify(syntheticAuthority), syntheticBefore, 'Materialisasi memutasi otoritas masukan.');

assert.equal(effectiveCoursesById.get('A10').progress.translationBearingUnits, 82);
assert.equal(effectiveCoursesById.get('A10').progress.canonicalUnits, 82);
assert.equal(effectiveCoursesById.get('A10').progress.publicUnits, 82);
assert.equal(effectiveCoursesById.get('A10').progress.publicPages, 2154);
assert.equal(effectiveCoursesById.get('A10').state, 'published');
assert.match(effectiveCoursesById.get('A10').zenodo, /22163663$/);
assert.equal(effectiveCoursesById.get('A20').progress.translationBearingUnits, 66);
assert.equal(effectiveCoursesById.get('A10').supplements.length, 2);
assert.equal(effectiveCoursesById.get('A20').progress.canonicalUnits, 51);
assert.equal(effectiveCoursesById.get('A20').progress.publicUnits, 48);
assert.equal(effectiveCoursesById.get('A30').progress.translationBearingUnits, 87);
assert.ok(!Object.hasOwn(effectiveCoursesById.get('A30').progress, 'integrationReadyUnits'));
assert.equal(effectiveCoursesById.get('A30').progress.canonicalUnits, 49);
assert.equal(effectiveCoursesById.get('A30').progress.publicUnits, 49);
assert.equal(effectiveCoursesById.get('A30').progress.publicPages, 1501);
assert.match(effectiveCoursesById.get('A30').zenodo, /22163371$/);
assert.equal(effectiveCoursesById.get('B20').progress.publicUnits, 5178);
assert.equal(effectiveCoursesById.get('B20').supplements.length, 2);
assert.match(effectiveCoursesById.get('B20').zenodo, /22164136$/);
assert.match(effectiveCoursesById.get('B30').zenodo, /22151145$/);
assert.equal(effectiveCoursesById.get('B50').progress.publicUnits, 138);
assert.equal(effectiveCoursesById.get('B50').supplements.length, 2);
assert.match(effectiveCoursesById.get('B50').zenodo, /22163372$/);
assert.match(effectiveCoursesById.get('B95').zenodo, /22166545$/);
assert.equal(effectiveCoursesById.get('B95').version, 'R011-B025');
assert.match(effectiveCoursesById.get('B95').release, /r011-b025-2026\.08\.29\.4$/);
assert.equal(effectiveCoursesById.get('B95').progress.publicPages, 260);
assert.equal(effectiveCoursesById.get('B95').progress.publicBoundary, 'B025 — Bab 6, Bagian 6.4');
assert.match(effectiveCoursesById.get('B95').edition, /00_STATISTIKA_BERBASIS_DATA_ID_R011-B025_WORKING_READER\.pdf\?download=1$/);
assert.deepEqual(effectiveCoursesById.get('B95').verification, {
  readerBytes: 12440420,
  readerSha256: 'b154484d2d2ddf0a49f0ee9925854f45e86b6e0fb17d241607db9fc27051e99d',
  backendRecords: 9119,
  publicAssets: 9,
});
assert.equal(effectiveCoursesById.get('C90').state, 'published');
assert.equal(effectiveCoursesById.get('C90').progress.publicUnits, 20);
assert.equal(effectiveCoursesById.get('C90').progress.publicPages, 645);
assert.match(effectiveCoursesById.get('C90').zenodo, /22164668$/);
assert.equal(effectiveCoursesById.get('C20').state, 'published');
assert.equal(effectiveCoursesById.get('C20').version, '6.3-id-wip.2026.08.30.u429');
assert.equal(effectiveCoursesById.get('C20').progress.publicPages, 241);
assert.match(effectiveCoursesById.get('C20').edition, /22172396\/files\/Analisis_Dasar_II_Bahasa_Indonesia_v6\.3\.pdf\?download=1$/);
assert.match(effectiveCoursesById.get('C20').release, /lebl-family-id-wip\.2026\.08\.30\.u429$/);
assert.deepEqual(effectiveCoursesById.get('C20').verification, {
  readerBytes: 2427379,
  readerSha256: 'e70c74bb7edc466a7cb6ff0eff0de33dfcc7b3bc63010d018aff758a14d2dea3',
  publicReadback: 'pass',
});
assert.equal(effectiveCoursesById.get('B50').progress.publicPages, 410);
assert.equal(effectiveCoursesById.get('B50').state, 'published');
assert.equal(effectiveCoursesById.get('C100').supplements.length, 1);
assert.equal(effectiveCoursesById.get('C100').supplements[0].id, 'clemens-snapp-workbook-u022');
assert.match(effectiveCoursesById.get('C140').zenodo, /22164344$/);
assert.equal(effectiveCoursesById.get('C140').supplements[0].id, 'c140-companion-reader');
assert.equal(effectiveCoursesById.get('D10').progress.translationBearingUnits, 520);
assert.equal(effectiveCoursesById.get('D10').progress.integrationReadyUnits, 520);
assert.equal(effectiveCoursesById.get('D10').progress.canonicalUnits, 509);
assert.equal(effectiveCoursesById.get('D10').progress.publicUnits, 509);
assert.equal(effectiveCoursesById.get('D10').progress.publicPages, 545);
assert.match(effectiveCoursesById.get('D10').zenodo, /22163307$/);
assert.equal(effectiveCoursesById.get('D20').state, 'published');
assert.equal(effectiveCoursesById.get('D20').progress.publicUnits, 17);
assert.match(effectiveCoursesById.get('D20').zenodo, /22088947$/);
assert.equal(effectiveCoursesById.get('D30').progress.publicPages, 345);
assert.match(effectiveCoursesById.get('D30').zenodo, /22172641$/);
assert.equal(effectiveCoursesById.get('D30').version, '2026.08.29-checkpoint.36');
assert.match(effectiveCoursesById.get('D30').edition, /READER_CHECKPOINT_36\.pdf\?download=1$/);
assert.equal(effectiveCoursesById.get('D40').state, 'production');
assert.equal(effectiveCoursesById.get('D40').progress.translationBearingUnits, 14);
assert.equal(effectiveCoursesById.get('D40').progress.integrationReadyUnits, 14);
assert.equal(effectiveCoursesById.get('D40').progress.canonicalUnits, 14);
assert.equal(effectiveCoursesById.get('D40').progress.publicUnits, 14);
assert.equal(effectiveCoursesById.get('D40').progress.publicPages, 230);
assert.match(effectiveCoursesById.get('D40').reader, /readers\/d40\/unit14\/$/);
assert.match(effectiveCoursesById.get('D40').edition, /PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_UNIT_14\.pdf\?download=1$/);
assert.match(effectiveCoursesById.get('D40').zenodo, /22161412$/);
assert.equal(effectiveCoursesById.get('D40').supplements.length, 1);
assert.equal(effectiveCoursesById.get('D40').supplements[0].id, 'dionne-unit14-source');
assert.equal(effectiveCoursesById.get('D40').supplements[0].bytes, 12141309);
assert.equal(effectiveCoursesById.get('D40').supplements[0].sha256, '248b65a225e96f0a342ab2f6288aa303d28bfd2a8e108db14f7e125ef5401f0e');
assert.equal(sha256(d40ReaderIndexBytes), 'c6785811f86cb96cc3d9a2ce81e094c511937f6d304ba78bab0973928ebcbbcf');
assert.equal(effectiveCoursesById.get('D50').state, 'published');
assert.match(effectiveCoursesById.get('D50').zenodo, /22161090$/);
assert.equal(effectiveCoursesById.get('D60').state, 'published');
assert.equal(effectiveCoursesById.get('D60').progress.publicUnits, 4);
assert.equal(effectiveCoursesById.get('D60').progress.publicPages, 564);
assert.match(effectiveCoursesById.get('D60').reader, /lab01-lab02-lab03-lab04-capstone\/$/);
assert.match(effectiveCoursesById.get('D60').edition, /22168033\/files\/00_TOPOLOGI_ALJABAR_ID_.*_CAPSTONE_READER\.pdf\?download=1$/);
assert.match(effectiveCoursesById.get('D60').zenodo, /22168033$/);
assert.equal(effectiveCoursesById.get('D60').version, '0.31.7');
assert.match(effectiveCoursesById.get('D60').note, /108\/108 butir penguasaan bersolusi/);
assert.match(effectiveCoursesById.get('D60').note, /empat graf perbaikan bukti/);
assert.match(effectiveCoursesById.get('D60').note, /capstone D60/);
assert.match(effectiveCoursesById.get('D60').note, /sembilan berkas Zenodo/);
assert.match(effectiveCoursesById.get('D60').note, /27\.642 rekaman kanonik/);
assert.match(effectiveCoursesById.get('D60').note, /2\.204 unit/);
assert.match(effectiveCoursesById.get('D60').note, /6\.279 pemetaan reversibel/);
assert.match(effectiveCoursesById.get('D60').note, /19 tabel JSONL\/CSV/);
assert.match(effectiveCoursesById.get('D60').note, /8\.338 rekaman native/);
assert.equal(effectiveCoursesById.get('D60').supplements.length, 1);
assert.equal(effectiveCoursesById.get('D60').supplements[0].id, 'd60-editable-source-backend-complete');
assert.equal(effectiveCoursesById.get('D60').supplements[0].resourceType, 'reference');
assert.match(effectiveCoursesById.get('D60').supplements[0].scope, /bukan pembaca utama/i);
assert.equal(effectiveCoursesById.get('D60').supplements[0].bytes, 8406450);
assert.equal(effectiveCoursesById.get('D60').supplements[0].sha256, 'f7670f6e6ad9a95ff808a1ddf4c2fdd8b41c6bce1916d33ac6fe5063be184b1b');
assert.match(effectiveCoursesById.get('D60').supplements[0].url, /22168033\/files\/TOPOLOGI_ALJABAR_ID_.*_CAPSTONE_EDITABLE_SOURCE_BACKEND\.zip\?download=1$/);
assert.doesNotMatch(effectiveCoursesById.get('D60').reader, /\.(?:json|jsonl|csv|zip)(?:[?#]|$)/i, 'Rute utama D60 harus tetap pembaca HTML.');
assert.equal(effectiveCoursesById.get('D70').state, 'published');
assert.equal(effectiveCoursesById.get('D70').progress.publicUnits, 4);
assert.equal(effectiveCoursesById.get('D70').progress.publicPages, 716);
assert.match(effectiveCoursesById.get('D70').zenodo, /22160944$/);
assert.equal(effectiveCoursesById.get('D80').state, 'published');
assert.equal(effectiveCoursesById.get('D80').progress.totalUnits, 146);
assert.equal(effectiveCoursesById.get('D80').progress.translationBearingUnits, 146);
assert.equal(effectiveCoursesById.get('D80').progress.integrationReadyUnits, 146);
assert.equal(effectiveCoursesById.get('D80').progress.canonicalUnits, 146);
assert.equal(effectiveCoursesById.get('D80').progress.publicUnits, 146);
assert.equal(effectiveCoursesById.get('D80').progress.publicPages, 864);
assert.equal(effectiveCoursesById.get('D80').reader, 'https://kokunoyumeto.github.io/metode-aljabar-jilid-2-id/');
assert.match(effectiveCoursesById.get('D80').edition, /22167691\/files\/00_metode-dalam-aljabar-jilid-2-edisi-bahasa-indonesia\.pdf\?download=1$/);
assert.match(effectiveCoursesById.get('D80').zenodo, /22167691$/);
assert.equal(effectiveCoursesById.get('D80').version, 'complete-edition-html-reader-correction-2026-08-30');
assert.equal(effectiveCoursesById.get('D80').supplements.length, 2);
assert.equal(effectiveCoursesById.get('D80').supplements[0].id, 'metode-aljabar-jilid-2-backend');
assert.match(effectiveCoursesById.get('D80').supplements[0].url, /22167691\/files\/02_backend-semantik\.zip\?download=1$/);
assert.equal(effectiveCoursesById.get('D80').supplements[1].id, 'metode-aljabar-jilid-2-html-offline-corrected');
assert.equal(effectiveCoursesById.get('D80').supplements[1].bytes, 1373063);
assert.equal(effectiveCoursesById.get('D80').supplements[1].sha256, '064dc97e9ae58217622a768f1a989eb316892a607d219211f4be17e6cf44d03c');
assert.match(effectiveCoursesById.get('D80').supplements[1].url, /22167691\/files\/03_pembaca-html-offline\.zip\?download=1$/);
assert.match(effectiveCoursesById.get('D80').note, /27\.308 formula/);
assert.match(effectiveCoursesById.get('D80').note, /nol kesalahan MathJax/);
assert.match(effectiveCoursesById.get('D80').note, /Paket HTML luring terkoreksi telah diterbitkan/);
assert.equal(effectiveCoursesById.get('D100').progress.totalUnits, 60);
assert.equal(effectiveCoursesById.get('D100').progress.translationBearingUnits, 36);
assert.equal(effectiveCoursesById.get('D100').progress.integrationReadyUnits, 36);
assert.equal(effectiveCoursesById.get('D100').progress.canonicalUnits, 36);
assert.equal(effectiveCoursesById.get('D100').progress.publicUnits, 36);
assert.equal(effectiveCoursesById.get('D100').progress.publicPages, 586);
assert.match(effectiveCoursesById.get('D100').zenodo, /22164552$/);
assert.equal(effectiveCoursesById.get('D100').supplements.length, 1);
assert.equal(effectiveCoursesById.get('D100').supplements[0].id, 'bgk-units-01-06');
assert.equal(effectiveCoursesById.get('D100').supplements[0].pages, 82);
assert.equal(effectiveCoursesById.get('D100').supplements[0].sha256, 'feb45d21d6168feaedf35719fdcb0b7f5532687846041d9fd75573c6d66fc5e9');

const expectedNextCourseIdsById = Object.fromEntries(
  courses.map(({ id }) => [
    id,
    courses.filter(({ prerequisites }) => prerequisites.includes(id)).map(({ id: nextId }) => nextId),
  ]),
);
assert.deepEqual(nextCourseIdsById, expectedNextCourseIdsById, 'Peta “Lanjut ke” bukan pembalikan deterministik prasyarat.');
assert.deepEqual(learnerReadModel.nextCourseIdsById, expectedNextCourseIdsById);
const prerequisiteEdgeCount = Object.values(expectedNextCourseIdsById).flat().length;
if (program.version === '0.62.0') {
  assert.equal(prerequisiteEdgeCount, 83);
  assert.deepEqual([...courses.find(({ id }) => id === 'D80').prerequisites].sort(), ['C30', 'C80', 'D70']);
}
assert.equal(learnerReadModel.summary.course_count, courses.length);
assert.equal(learnerReadModel.summary.published_course_count, publishedIds.length);
assert.equal(learnerReadModel.summary.readback_overlay_count, authority.public_readback_overlays.length);
assert.equal(program.backend.learnerReadModelV1.courseCount, courses.length);
assert.equal(program.backend.learnerReadModelV1.prerequisiteEdgeCount, prerequisiteEdgeCount);

const visiting = new Set();
const visited = new Set();
function visitCourse(id) {
  assert.ok(!visiting.has(id), `Siklus prasyarat terdeteksi pada ${id}.`);
  if (visited.has(id)) return;
  visiting.add(id);
  for (const nextId of nextCourseIdsById[id]) visitCourse(nextId);
  visiting.delete(id);
  visited.add(id);
}
for (const id of ids) visitCourse(id);

const federationManifest = await readJson(`${authority.federation.package_path}/manifest.json`);
const v2 = program.backend.federationV2;
assert.equal(v2.status, 'validated');
assert.equal(v2.recordCount, federationManifest.record_count);
assert.equal(v2.datasetCount, federationManifest.record_counts.datasets);
assert.equal(v2.courseCount, federationManifest.record_counts.courses);
assert.equal(v2.learnerSurfaceCount, federationManifest.record_counts.reader_surfaces);
assert.equal(v2.webRouteCount, federationManifest.record_counts.web_routes);
assert.equal(v2.identityCrosswalkCount, federationManifest.record_counts.identity_crosswalks);
assert.equal(v2.publicationEventCount, federationManifest.record_counts.publication_events);
assert.equal(v2.qaEventCount, federationManifest.record_counts.qa_events);
assert.equal(federationManifest.record_count, Object.values(federationManifest.record_counts).reduce((sum, value) => sum + value, 0));
for (const field of ['package', 'packageSchema', 'recordSchema', 'validationReceipt']) {
  assert.match(v2[field], /\/records\/\d+\/files\//, `federationV2.${field} tidak terikat ke arsip.`);
}
if (program.backend.federationV22) {
  assert.match(String(program.backend.federationV22.status), /validated/);
  for (const field of ['package', 'validationReceipt', 'archiveReceipt']) {
    if (program.backend.federationV22[field]) {
      assert.match(
        program.backend.federationV22[field],
        new RegExp(`^https://zenodo\\.org/records/${centralRecordId}/files/`),
      );
    }
  }
}

const v21 = program.backend.federationV21;
assert.equal(v21.status, 'pilot_validated');
assert.deepEqual(
  [...v21.route_wrapper_courses].sort(),
  routeManifestV21.courses.map(({ course_id }) => course_id).sort(),
);
assert.ok(v21.pilot_units >= routeManifestV21.courses.reduce((sum, course) => sum + course.units.length, 0));
assert.equal(v21.pilot_courses.length >= routeManifestV21.courses.length, true);
assert.equal(routeManifestV21.summary.course_count, routeManifestV21.courses.length);
assert.equal(routeManifestV21.summary.unit_count, routeManifestV21.courses.reduce((sum, course) => sum + course.units.length, 0));
assert.deepEqual(routeManifestV21.courses, [d20RouteManifest, c100RouteManifest]);
assert.deepEqual(legacyD20RouteBytes, d20RouteBytes, 'Alias rute D20 lama tidak identik dengan manifest kanonik.');

assert.equal(educationalAccess.datasetVersion, program.backend.educationalAccessResearch.version);
assert.equal(educationalAccess.summary.curriculum_resources, courses.length);
assert.equal(
  JSON.parse(educationalAccessSchemaBytes.toString('utf8')).$id,
  program.backend.educationalAccessResearch.schema,
);

assert.match(html, /<html lang="id">/);
assert.match(html, /href="styles\.css"/);
assert.match(html, /src="app\.js"/);
assert.match(html, /href="peta-belajar-luring\.html"/);
assert.match(html, /Unduh peta belajar — HTML satu berkas/);
assert.match(html, /STATIC-COURSE-FALLBACK:START/);
assert.match(html, /STATIC-COURSE-FALLBACK:END/);
const staticCourseIds = [...html.matchAll(/data-static-course-id="([A-D]\d{2,3})"/g)].map((match) => match[1]);
assert.equal(staticCourseIds.length, 40, 'Fallback tanpa JavaScript harus memuat tepat 40 mata kuliah.');
assert.deepEqual(staticCourseIds, effectiveCourses.map(({ id }) => id));
assert.match(html, /<noscript><section class="static-catalog"/);
assert.match(html, /id="progres"/);
assert.match(html, /id="learner-summary"/);
assert.match(html, /id="learner-storage-status"/);
assert.match(html, /Data ini tetap di browser ini dan tidak dikirim\./);
assert.match(html, /class="english-note" lang="en"/);
assert.match(html, new RegExp(escapeRegex(program.website)));
// The learner-facing page points at the current concept/landing archive, while
// `program.zenodo` may remain the immutable backend-authority record.  Require
// the public concept link (or the authority link for older snapshots) without
// coupling the static reader to one historical record number.
assert.ok(
  html.includes(program.zenodoConcept) || html.includes(program.zenodo),
  'Halaman siswa harus menautkan arsip Zenodo konsep atau otoritas.',
);
assert.match(html, new RegExp(`${courses.length} korpus terpilih`));
assert.match(html, /produksi yang belum selesai tetap dilabeli dengan jelas/i);
assert.match(html, new RegExp(`<strong id="live-completed-role-count">${effectiveCourses.filter(({ state }) => state === 'published').length}<\\/strong><span>peran dengan edisi selesai<\\/span>`));
assert.match(html, /29 peran melalui 28 rekaman edisi lengkap/);
assert.match(html, /A00, B10, D20, D60, dan D110/);
assert.match(html, /35 peran lain/);
assert.match(rootReadme, /D60 kini merupakan edisi komposit lengkap v0\.31\.7/);
assert.match(rootReadme, /Backend v2\.3 kini memiliki lima bukti jalur yang diterima: A00, B10, D20, D60, dan D110/);
assert.match(rootReadme, /rilis pusat v0\.62\.10/);
assert.match(rootReadme, /41\.460 rekaman kanonik/);
assert.match(rootReadme, /rilis pusat v0\.62\.11/);
assert.match(backendV23Readme, /27,642 canonical records/);
assert.match(backendV23Readme, /2,204 stable units/);
assert.match(backendV23Readme, /6,279 reversible materialized-native/);
assert.match(backendV23Readme, /8,338 native backend records/);
assert.match(backendV23Readme, /41,460 canonical records/);
assert.match(backendV23Readme, /10,978 native/);
assert.match(backendV23Readme, /138,894 canonical records/);
assert.match(backendV23Readme, /32,383 native records/);
assert.match(backendV23Readme, /other 35 course roles/);
assert.match(schemaV23Index, /A00, B10, D20, D60, dan D110/);
assert.match(schemaV23Index, /27\.642 rekaman kanonik/);
assert.match(schemaV23Index, /41\.460 rekaman kanonik/);
assert.match(schemaV23Index, /rilis pusat v0\.62\.11/);
assert.match(html, new RegExp(`Mulai belajar — buka ${courses.length} mata kuliah`));
assert.match(html, new RegExp(escapeRegex(program.repositories.github.url)));
assert.match(html, /melanjutkan ke mana/);
assert.match(html, /“Lanjut ke”.*prasyarat langsung.*prasyarat lain/s);
assert.match(app, /Mulai belajar — HTML/);
assert.match(app, /Buka pembaca kerja — HTML/);
assert.match(app, /stateLabels\[nextCourse\.state\]/);
assert.match(app, /from '\.\/learner-delivery\.js'/);
assert.match(app, /Unduh HTML luring/);
assert.match(app, /statusSelect\.value === 'offline'/);
assert.match(app, /course\.repository/);
assert.match(app, /course\.supplements/);
assert.match(app, /nextCourseIdsById/);
assert.match(app, /Lanjut ke/);
assert.match(app, /data-course-link/);
assert.match(app, /from '\.\/learner-state\.js'/);
assert.deepEqual(publicLearnerStateSchemaBytes, learnerStateSchemaBytes, 'Salinan schema keadaan pelajar harus identik byte demi byte.');
assert.match(learnerStateModule, /program-matematika-indonesia\/learner-state\/v1/);
assert.doesNotMatch(learnerStateModule, /\bfetch\s*\(/);

assert.match(app, /courses as authorityCourses/);
assert.match(app, /materializeLiveCourses\(authorityCourses\)/);
assert.match(app, /deriveNextCourseIdsById\(courses\)/);
assert.match(app, /publicationProgress\(course\)/);
assert.match(app, /effectivePublishedCourses/);
assert.match(app, /livePublicationSummary\.textContent/);
assert.doesNotMatch(app, /liveCoursePublications\[/);

const deliveryById = new Map(learnerDelivery.courses.map((row) => [row.course_id, row]));
for (const row of learnerDelivery.courses) {
  assert.ok(['verified', 'available_unverified', 'absent', 'not_applicable'].includes(row.portable_html.status));
  if (row.portable_html.status === 'verified') {
    assert.match(row.portable_html.format, /zip\+html/);
    assert.equal(row.portable_html.dependency_free, true);
    assert.ok(Number.isInteger(row.portable_html.bytes) && row.portable_html.bytes > 0);
    assert.match(row.portable_html.sha256, /^[0-9a-f]{64}$/);
    assert.ok(row.portable_html.entry_point && Number.isInteger(row.portable_html.inventory_count));
    assert.doesNotMatch(row.portable_html.format, /pdf/i, `${row.course_id}: PDF tidak boleh dihitung sebagai HTML luring.`);
  }
}
assert.equal(learnerDelivery.summary.online_html_available, effectiveCourses.filter((course) => course.learner || course.reader).length);
assert.equal(learnerDelivery.summary.online_html_available, 24);
assert.equal(learnerDelivery.summary.verified_portable_html, 3);
assert.equal(learnerDelivery.summary.verified_epub, 1);
assert.deepEqual(
  [...learnerDelivery.courses.filter(({ portable_html }) => portable_html.status === 'verified').map(({ course_id }) => course_id)].sort(),
  ['C100', 'D120', 'D80'].sort(),
);
assert.equal(deliveryById.get('C100').portable_html.sha256, 'ee26d6e1228b7b66ca7ea156081c673dd1c8ab8b3488d87f7ee35cc354c091ae');
assert.equal(deliveryById.get('C100').epub.sha256, '5eb6773cc036015e8eb9e6f1791c6ec2f2b83812f43c8340c66aaafd91b12d99');
assert.equal(deliveryById.get('D80').portable_html.sha256, '064dc97e9ae58217622a768f1a989eb316892a607d219211f4be17e6cf44d03c');
assert.equal(deliveryById.get('D120').portable_html.sha256, 'c47fb636c821d574cc987a39d512f608bc4796fe2c737d8d7d02b5d0540df7e9');

const styles = stylesBytes.toString('utf8');
assert.match(styles, /\.card-action \{[^}]*min-height: 44px/s);
assert.match(styles, /@media print/);
assert.doesNotMatch(styles, /@media \(max-width: 820px\)[\s\S]{0,300}nav \{ display: none;/);
assert.match(styles, /p a:not\(\.button\):not\(\.card-action\)/);
const shellFiles = [Buffer.from(html), stylesBytes, Buffer.from(app), coursesModuleBytes, Buffer.from(livePublicationsModule), Buffer.from(learnerStateModule), deliveryModuleBytes];
const shellRawBytes = shellFiles.reduce((sum, bytes) => sum + bytes.length, 0);
const shellGzipBytes = shellFiles.reduce((sum, bytes) => sum + gzipSync(bytes, { level: 9 }).length, 0);
assert.ok(shellRawBytes <= 200_000, `Shell melewati 200.000 byte: ${shellRawBytes}.`);
assert.ok(shellGzipBytes <= 50_000, `Shell gzip melewati 50.000 byte: ${shellGzipBytes}.`);
const runtimeAssetUrls = [
  ...[...html.matchAll(/<script\b[^>]*src="([^"]+)"[^>]*>/g)].map((match) => match[1]),
  ...[...html.matchAll(/<link\b(?=[^>]*rel="stylesheet")[^>]*href="([^"]+)"[^>]*>/g)].map((match) => match[1]),
].filter((url) => /^(?:https?:)?\/\//.test(url));
assert.deepEqual(runtimeAssetUrls, [], 'Shell tidak boleh memerlukan CSS atau JavaScript jarak jauh.');
const standalone = standaloneBytes.toString('utf8');
assert.equal((standalone.match(/data-static-course-id=/g) ?? []).length, 40);
assert.doesNotMatch(standalone, /href="styles\.css"|src="app\.js"|^\s*import\s/m);
assert.match(standalone, /const learnerDeliveryByCourseId = Object\.freeze\(/);
assert.match(standalone, /href="#katalog">Unduh peta belajar — HTML satu berkas/);
for (const name of ['index.html', 'styles.css', 'app.js', 'courses.js', 'live-course-publications.js', 'learner-state.js', 'learner-delivery.js', 'peta-belajar-luring.html']) {
  const [docsBytes, hostedBytes] = await Promise.all([
    readFile(resolve(root, 'docs', name)),
    readFile(resolve(root, 'public/hub', name)),
  ]);
  assert.deepEqual(hostedBytes, docsBytes, `${name}: mirror Sites berbeda dari docs.`);
}
assert.match(livePublicationsModule, /id-ID\/courses\/B95\//);
assert.match(livePublicationsModule, /22166545/);
assert.match(livePublicationsModule, /22161412/);
assert.match(livePublicationsModule, /22164552/);
assert.match(livePublicationsModule, /22161090/);
assert.match(livePublicationsModule, /22164668/);
assert.match(livePublicationsModule, /22163663/);
assert.match(livePublicationsModule, /22164136/);
assert.match(livePublicationsModule, /22163372/);
assert.match(livePublicationsModule, /clemens-snapp-workbook-u022/);
assert.match(b95Landing, /Statistika Berbasis Data/);
assert.match(b95Landing, /22166545/);
assert.match(b95Landing, /statistika-berbasis-data-id/);
assert.match(b95Landing, /260 halaman/);
assert.match(b95Landing, /GitHub \(B025\)/);
assert.match(b95Landing, /byte-identik di Zenodo serta GitHub/);
assert.match(b95Landing, /produksi berlanjut ke B026/);
assert.doesNotMatch(b95Landing, /href="[^"]+\.(?:json|jsonl|csv)(?:[?#"])/i);

assert.match(livePublicationsModule, /id-ID\/courses\/D30\//);
assert.match(livePublicationsModule, /22172641/);
assert.match(livePublicationsModule, /CHECKPOINT_36/);
assert.match(livePublicationsModule, /22168033/);
assert.match(livePublicationsModule, /laboratorium komputasi 4\/4/);
assert.match(livePublicationsModule, /capstone D60/);
assert.match(livePublicationsModule, /22076539/);
assert.match(d30Landing, /Probabilitas Teoretis-Ukuran dan Proses Stokastik/);
assert.match(d30Landing, /345 halaman/);
assert.match(d30Landing, /14 rangkaian penguasaan/);
assert.match(d30Landing, /4 laboratorium publik/);
assert.match(d30Landing, /22172641/);
assert.match(d30Landing, /measure-theoretic-probability-stochastic-processes-id/);
assert.doesNotMatch(d30Landing, /href="[^"]+\.(?:json|jsonl|csv)(?:[?#"])/i);

assert.equal(c100ReaderBytes.length, c100RouteManifest.reader.source_html.bytes);
assert.equal(sha256(c100ReaderBytes), c100RouteManifest.reader.source_html.sha256);
assert.equal(c100ReaderStyleBytes.length, c100RouteManifest.reader.source_style.bytes);
assert.equal(sha256(c100ReaderStyleBytes), c100RouteManifest.reader.source_style.sha256);
assert.equal(c100SolutionBytes.length, c100RouteManifest.reader.solution_pdf.bytes);
assert.equal(sha256(c100SolutionBytes), c100RouteManifest.reader.solution_pdf.sha256);
assert.match(c100Landing, /Mulai membaca HTML/);
assert.doesNotMatch(c100Landing, /href="[^"]+\.(?:json|jsonl|csv)(?:[?#"])/i);

for (const unit of d20RouteManifest.units) {
  const wrapper = await readFile(resolve(root, `docs/id-ID/courses/D20/units/${unit.slug}/index.html`), 'utf8');
  assert.ok(wrapper.includes(`rel="canonical" href="${unit.central_url}"`), `${unit.id}: URL kanonis D20 tidak cocok.`);
  assert.ok(wrapper.includes(`href="${unit.native_html_url}"`), `${unit.id}: tautan pembaca D20 tidak cocok.`);
}
for (const unit of c100RouteManifest.units.filter(({ kind }) => kind === 'chapter')) {
  const chapter = unit.id.match(/\.ch(\d{2})$/)?.[1];
  if (!chapter) continue;
  const wrapper = await readFile(resolve(root, `docs/id-ID/courses/C100/units/bab-${chapter}/index.html`), 'utf8');
  assert.ok(wrapper.includes(`rel="canonical" href="${unit.central_url}"`), `${unit.id}: URL kanonis C100 tidak cocok.`);
  assert.ok(wrapper.includes(`reader/#${unit.id}`), `${unit.id}: fragmen pembaca C100 hilang.`);
}

const blankTargets = [...html.matchAll(/<a\b[^>]*target="_blank"[^>]*>/g)].map(([tag]) => tag);
for (const tag of blankTargets) assert.match(tag, /rel="[^"]*noreferrer[^"]*"/);

console.log(JSON.stringify({
  status: 'pass',
  version: program.version,
  zenodo: program.zenodo,
  courses: courses.length,
  selected: selectedIds.length,
  unresolved: unresolvedIds.length,
  publishedCanonRoles: publishedIds.length,
  effectivePublishedRoles: effectivePublishedCourses.length,
  effectiveDistinctPublishedRecords: effectivePublishedRecordDois.size,
  liveOverlayRows: Object.keys(liveCoursePublications).length,
  completedPublicCourseRoles: publishedIds.length,
  completedPublicRecords: program.completedPublicRecordDois.length,
  publishedHtmlReaders: publishedHtmlReaderIds.length,
  effectiveHtmlLearnerEntries: learnerDelivery.summary.online_html_available,
  verifiedPortableHtmlPackages: learnerDelivery.summary.verified_portable_html,
  verifiedEpubPackages: learnerDelivery.summary.verified_epub,
  staticNoJsCourseEntries: staticCourseIds.length,
  shellRawBytes,
  shellGzipBytes,
  prerequisiteEdges: prerequisiteEdgeCount,
  federationV2Records: federationManifest.record_count,
  publicReadbackOverlays: authority.public_readback_overlays.length,
  topics: topics.length,
  levelCounts: Object.fromEntries([...new Set(courses.map(({ level }) => level))].map((level) => [level, courses.filter((course) => course.level === level).length])),
}, null, 2));
