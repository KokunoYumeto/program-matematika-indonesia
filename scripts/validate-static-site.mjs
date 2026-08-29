import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { courses, nextCourseIdsById, program, topics } from '../docs/courses.js';
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
]);

const authority = JSON.parse(authorityBytes.toString('utf8'));
const catalog = authority.catalog;
const learnerReadModel = JSON.parse(learnerReadModelBytes.toString('utf8'));
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

const liveOverlayRequiredRoleIds = ['A10', 'A20', 'A30', 'B30', 'B50', 'B95', 'C10', 'C90', 'C100', 'C140', 'D10', 'D30', 'D50', 'D70', 'D100'];
for (const id of liveOverlayRequiredRoleIds) {
  assert.ok(liveCoursePublications[id], `${id}: baris lama belum memiliki overlay publikasi langsung.`);
}
assert.deepEqual(effectiveCourses.map(({ id }) => id), courses.map(({ id }) => id), 'Overlay mengubah urutan atau identitas mata kuliah.');
assert.equal(effectiveCourses.length, courses.length, 'Overlay mengubah jumlah mata kuliah.');
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
assert.equal(effectiveCoursesById.get('A10').progress.publicUnits, 32);
assert.equal(effectiveCoursesById.get('A20').progress.canonicalUnits, 51);
assert.equal(effectiveCoursesById.get('A20').progress.publicUnits, 48);
assert.equal(effectiveCoursesById.get('A30').progress.translationBearingUnits, 87);
assert.equal(effectiveCoursesById.get('A30').progress.canonicalUnits, 49);
assert.equal(effectiveCoursesById.get('A30').progress.publicUnits, 38);
assert.match(effectiveCoursesById.get('A30').zenodo, /22160769$/);
assert.match(effectiveCoursesById.get('B30').zenodo, /22151145$/);
assert.equal(effectiveCoursesById.get('B50').progress.publicUnits, 0);
assert.equal(effectiveCoursesById.get('C90').progress.publicUnits, 17);
assert.equal(effectiveCoursesById.get('C100').supplements.length, 1);
assert.equal(effectiveCoursesById.get('C100').supplements[0].id, 'clemens-snapp-workbook-u022');
assert.match(effectiveCoursesById.get('C140').zenodo, /22151570$/);
assert.equal(effectiveCoursesById.get('D10').progress.translationBearingUnits, 509);
assert.equal(effectiveCoursesById.get('D10').progress.canonicalUnits, 444);
assert.equal(effectiveCoursesById.get('D10').progress.publicUnits, 444);
assert.equal(effectiveCoursesById.get('D10').progress.publicPages, 477);
assert.match(effectiveCoursesById.get('D10').zenodo, /22161046$/);
assert.equal(effectiveCoursesById.get('D50').state, 'published');
assert.match(effectiveCoursesById.get('D50').zenodo, /22160677$/);
assert.match(effectiveCoursesById.get('D60').zenodo, /22151513$/);
assert.match(effectiveCoursesById.get('D70').zenodo, /22151447$/);
assert.equal(effectiveCoursesById.get('D100').progress.publicUnits, 30);

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
assert.match(html, /id="progres"/);
assert.match(html, /id="learner-summary"/);
assert.match(html, /id="learner-storage-status"/);
assert.match(html, /Data ini tetap di browser ini dan tidak dikirim\./);
assert.match(html, /class="english-note" lang="en"/);
assert.match(html, new RegExp(escapeRegex(program.website)));
assert.match(html, new RegExp(escapeRegex(program.zenodo)));
assert.match(html, new RegExp(`${courses.length} korpus terpilih`));
assert.match(html, /produksi yang belum selesai tetap dilabeli dengan jelas/i);
assert.match(html, new RegExp(`<strong id="live-completed-role-count">${effectiveCourses.filter(({ state }) => state === 'published').length}<\\/strong><span>peran dengan edisi selesai<\\/span>`));
assert.match(html, new RegExp(`Mulai belajar — buka ${courses.length} mata kuliah`));
assert.match(html, new RegExp(escapeRegex(program.repositories.github.url)));
assert.match(html, /melanjutkan ke mana/);
assert.match(html, /“Lanjut ke”.*prasyarat langsung.*prasyarat lain/s);
assert.match(app, /Mulai belajar — HTML/);
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
assert.match(livePublicationsModule, /id-ID\/courses\/B95\//);
assert.match(livePublicationsModule, /22148827/);
assert.match(livePublicationsModule, /22160677/);
assert.match(livePublicationsModule, /clemens-snapp-workbook-u022/);
assert.match(b95Landing, /Statistika Berbasis Data/);
assert.match(b95Landing, /22148827/);
assert.match(b95Landing, /statistika-berbasis-data-id/);
assert.match(b95Landing, /216 halaman/);
assert.doesNotMatch(b95Landing, /href="[^"]+\.(?:json|jsonl|csv)(?:[?#"])/i);

assert.match(livePublicationsModule, /id-ID\/courses\/D30\//);
assert.match(livePublicationsModule, /22148902/);
assert.match(livePublicationsModule, /CHECKPOINT_33/);
assert.match(livePublicationsModule, /22151513/);
assert.match(livePublicationsModule, /laboratorium komputasi 3\/4/);
assert.match(livePublicationsModule, /22076539/);
assert.match(d30Landing, /Probabilitas Teoretis-Ukuran dan Proses Stokastik/);
assert.match(d30Landing, /321 halaman/);
assert.match(d30Landing, /8\.022 catatan backend/);
assert.match(d30Landing, /22148902/);
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
  effectivePublishedRoles: effectiveCourses.filter(({ state }) => state === 'published').length,
  liveOverlayRows: Object.keys(liveCoursePublications).length,
  completedPublicCourseRoles: publishedIds.length,
  completedPublicRecords: program.completedPublicRecordDois.length,
  publishedHtmlReaders: publishedHtmlReaderIds.length,
  prerequisiteEdges: prerequisiteEdgeCount,
  federationV2Records: federationManifest.record_count,
  publicReadbackOverlays: authority.public_readback_overlays.length,
  topics: topics.length,
  levelCounts: Object.fromEntries([...new Set(courses.map(({ level }) => level))].map((level) => [level, courses.filter((course) => course.level === level).length])),
}, null, 2));
