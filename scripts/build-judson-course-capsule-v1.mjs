import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { courses } from '../docs/courses.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const inputRoot = 'backend/course-capsule-v1/adapters/judson-v231';
const outputRoot = 'docs/backend/judson';
const admissionPath = `${inputRoot}/ADMISSION.json`;
const manifestPath = `${inputRoot}/manifest.json`;
const archivePath = 'backend/course-capsule-v1/builds/program-matematika-indonesia-judson-c30-c40-v2.3.1.zip';
const routeEvidenceInputPath = 'frozen-inputs/JUDSON_TWO_COURSE_LEARNER_ROUTES.json';
const archiveUrl = 'https://zenodo.org/records/22062449/files/ALJABAR_ABSTRAK_TEORI_DAN_PENERAPAN_ID_2026.08.22.2_WEB.zip?download=1';
const readerOrigin = 'https://kokunoyumeto.github.io';
const readerPath = /^\/abstract-algebra-theory-and-applications-id\/[A-Za-z0-9._-]+\.html$/;
const expected = {
  admission: { bytes: 20715, sha256: '0c73d1be90d3a0318b70293eccf7b5ec58b41f323fbb2639b5c12b4451783e74' },
  archive: { bytes: 16905857, sha256: '177eda23cf07dd7d1225a176466f8686bbcdb91c233309f81252dd897a024700' },
  manifest: { bytes: 28845, sha256: '00b80a3f7406c96b375ddb390981dbd0a1f1e3d41e0d240c93b194694521c28a' },
  courses: { bytes: 52352, sha256: '05136e1d675bdac0d1674f3b95f7bf6e87b98d5ef5cb9f52a2ad00c375bcaebc' },
  routeEvidence: { bytes: 47314, sha256: '3f22e70fff457fc96dc44c2cb4930ae25a0ab401fb6ad0a3387ed8d98e2d84c4' },
};
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex');
const identify = (bytes) => ({ bytes: bytes.length, sha256: hash(bytes) });
const stable = (value) => `${JSON.stringify(value, null, 2)}\n`;
const escape = (value) => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');

const admissionBytes = await readFile(resolve(root, admissionPath));
assert.deepEqual(identify(admissionBytes), expected.admission, 'Judson admission identity drift');
const admission = JSON.parse(admissionBytes);
assert.equal(admission.state, 'locally_admitted_public_release_pending');
assert.equal(admission.package_tree_sha256, '4a9deaab4d97455917453ea1af2a357763d9222ba25b4571e2a9444e5bd226d0');
assert.equal(admission.independent_trees_identical, true);
assert.equal(admission.manager_handoff.sha256, '03fad8f0fba97de85e133908ae5129f2cfc18ffb5ae39145a8c16e191da2721e');
assert.equal(admission.manifest_bound_files_verified, 62);
assert.equal(admission.package_files, 65);
assert.equal(admission.package_bytes, 111681966);
assert.deepEqual(admission.archive, { path: archivePath, ...expected.archive });
assert.deepEqual(identify(await readFile(resolve(root, archivePath))), expected.archive, 'Judson archive identity drift');

const inputEntries = Object.entries(admission.inputs);
assert.equal(inputEntries.length, 65, 'Judson admitted public-file count drift');
const inputs = {};
for (const [path, expectedIdentity] of inputEntries) {
  assert.ok(!path.startsWith('/') && !path.includes('..') && !path.includes('\\'), `Unsafe Judson input path: ${path}`);
  const bytes = await readFile(resolve(root, inputRoot, path));
  assert.deepEqual(identify(bytes), expectedIdentity, `Judson input drift: ${path}`);
  inputs[path] = bytes;
}

assert.deepEqual(identify(inputs['manifest.json']), expected.manifest, 'Judson manifest identity drift');
const manifest = JSON.parse(inputs['manifest.json']);
assert.equal(manifest.files.length, 62);
for (const row of manifest.files) {
  assert.equal(row.path_base, 'package_root', `${row.path}: unsupported manifest path base`);
  assert.ok(inputs[row.path], `${row.path}: manifest file absent from admitted package`);
  assert.deepEqual(identify(inputs[row.path]), { bytes: row.bytes, sha256: row.sha256 }, `${row.path}: manifest identity drift`);
}
const manifestPaths = new Set(manifest.files.map((row) => row.path));
assert.equal(manifestPaths.size, 62, 'Duplicate Judson manifest path');
assert.deepEqual(
  Object.keys(inputs).filter((path) => !manifestPaths.has(path)).sort(),
  ['PACKAGE_CHECKSUMS.sha256', 'manifest.json', 'seal.json'],
  'Unexpected files outside the manifest-bound payload',
);

const coursesBytes = await readFile(resolve(root, 'docs/courses.js'));
assert.deepEqual(identify(coursesBytes), expected.courses, 'Course-catalog input drift');
const generatorBytes = await readFile(fileURLToPath(import.meta.url));
const sourceBindings = {
  course_catalog: { path: 'docs/courses.js', ...identify(coursesBytes) },
  generator: { path: 'scripts/build-judson-course-capsule-v1.mjs', ...identify(generatorBytes) },
};

const routeEvidenceBytes = inputs[routeEvidenceInputPath];
assert.deepEqual(identify(routeEvidenceBytes), expected.routeEvidence, 'Judson route-evidence identity drift');
const routeEvidence = JSON.parse(routeEvidenceBytes);
const views = JSON.parse(inputs['course-views.json']);
const routes = inputs['tables/routes.jsonl'].toString('utf8').trimEnd().split('\n').map(JSON.parse);
const byRoute = new Map(routes.map((row) => [row.id, row]));
assert.equal(byRoute.size, 25);
assert.deepEqual(views.views.map((view) => view.curriculum_role_id), ['C30', 'C40']);

const pointerValue = (document, pointer) => {
  assert.match(pointer, /^\/(?:[^/]+(?:\/[^/]+)*)?$/);
  return pointer.slice(1).split('/').reduce((value, token) => {
    const key = token.replaceAll('~1', '/').replaceAll('~0', '~');
    assert.ok(value !== null && value !== undefined && Object.hasOwn(value, key), `Unresolved evidence pointer: ${pointer}`);
    return value[key];
  }, document);
};
const safeUrl = (url) => {
  const parsed = new URL(url);
  assert.equal(parsed.protocol, 'https:');
  assert.equal(parsed.username + parsed.password, '');
  assert.equal(parsed.hash, '', 'No guessed descendant anchors');
  if (parsed.origin === readerOrigin) {
    assert.match(parsed.pathname, readerPath, `Reader path outside admitted Judson surface: ${url}`);
    assert.equal(parsed.search, '');
  } else {
    assert.equal(url, archiveUrl, `URL outside exact admitted Judson endpoints: ${url}`);
  }
  return escape(url);
};

const courseRows = [];
const seen = new Set();
for (const view of views.views) {
  const courseId = view.curriculum_role_id;
  const expectedCount = courseId === 'C30' ? 15 : 8;
  assert.equal(view.chapters.length, expectedCount);
  assert.equal(view.unit_count, courseId === 'C30' ? 2014 : 1279);
  const course = courses.find((row) => row.id === courseId);
  assert.ok(course);
  for (const [index, chapter] of view.chapters.entries()) {
    assert.equal(chapter.sequence, index + 1);
    assert.ok(!seen.has(chapter.route_id));
    seen.add(chapter.route_id);
    const route = byRoute.get(chapter.route_id);
    assert.ok(route, `${courseId}: missing route`);
    const payload = route.payload;
    assert.equal(payload.curriculum_role_id, courseId);
    assert.equal(payload.native_course_id, view.native_course_id);
    for (const field of ['native_unit_id', 'native_membership_id', 'projected_unit_id', 'sequence', 'localized_title', 'offline_member', 'offline_archive', 'live_frozen_byte_identity']) {
      assert.deepEqual(payload[field], chapter[field], `${courseId}/${chapter.sequence}: ${field} join drift`);
    }
    assert.equal(payload.url, chapter.public_url);
    assert.equal(chapter.current_live_edition_identity, 'not_verified');
    assert.equal(payload.live_observation.http_status, 200);
    assert.equal(payload.live_observation.matches_frozen_html, false);
    assert.equal(payload.live_observation.observed_utc.slice(0, 10), '2026-08-31');
    assert.equal(pointerValue(routeEvidence, chapter.offline_evidence_json_pointer).native_unit_id, chapter.native_unit_id);
    const liveEvidence = pointerValue(routeEvidence, chapter.live_evidence_json_pointer);
    assert.equal(liveEvidence.requested_url, chapter.public_url);
    assert.equal(liveEvidence.final_url, chapter.public_url);
    safeUrl(chapter.public_url);
    safeUrl(chapter.offline_archive.public_url);
  }
  courseRows.push({
    course_id: courseId,
    title: course.title,
    native_course_id: view.native_course_id,
    unit_count: view.unit_count,
    chapters: view.chapters,
  });
}
assert.equal(seen.size, 23);

const evidenceDocument = {
  path: 'route-evidence.json',
  source_path: `${inputRoot}/${routeEvidenceInputPath}`,
  verbatim_copy: true,
  ...identify(routeEvidenceBytes),
};
const projection = {
  schema_id: 'interlanguage/judson-chapter-navigation/v1',
  recorded_at: '2026-08-31',
  admission: { path: admissionPath, ...identify(admissionBytes) },
  evidence_document: evidenceDocument,
  courses: courseRows,
  limitations: admission.limits,
  one_native_graph_two_course_views: true,
};
const files = new Map([
  ['chapters.json', Buffer.from(stable(projection))],
  ['route-evidence.json', routeEvidenceBytes],
]);

for (const course of courseRows) {
  const archive = course.chapters[0].offline_archive;
  const sibling = courseRows.find((row) => row.course_id !== course.course_id);
  assert.ok(sibling);
  const items = course.chapters.map((chapter) => `<li data-route-id="${escape(chapter.route_id)}" data-native-unit-id="${escape(chapter.native_unit_id)}"><a href="${safeUrl(chapter.public_url)}">${escape(chapter.localized_title)}</a><small>Berkas edisi arsip: <code>${escape(chapter.offline_member.path)}</code></small></li>`).join('\n');
  const title = `${course.course_id} — ${course.title}: peta bab`;
  const description = `${course.chapters.length} bab berurutan dengan tautan pembaca Bahasa Indonesia dan edisi WEB yang diarsipkan.`;
  const html = `<!doctype html>\n<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)}</title><meta name="description" content="${escape(description)}"><meta property="og:title" content="${escape(title)}"><meta property="og:description" content="${escape(description)}"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="${escape(title)}"><meta name="twitter:description" content="${escape(description)}"><link rel="stylesheet" href="../backend.css"><style>main{max-width:850px;margin:2rem auto;padding:0 1rem}ol{padding-left:1.5rem}li{margin:1rem 0}li a{font-size:1.1rem}small{display:block;margin:.35rem 0;overflow-wrap:anywhere}code{overflow-wrap:anywhere}.notice{padding:1rem;border-left:4px solid currentColor;margin:1.5rem 0}details{margin:1.5rem 0}a:focus-visible,summary:focus-visible{outline:3px solid currentColor;outline-offset:4px}</style></head><body><main><nav aria-label="Navigasi"><a href="../index.html">← Kembali ke katalog program</a> · <a href="${sibling.course_id}.html">${escape(`${sibling.course_id} — ${sibling.title}`)}</a></nav><h1>${escape(title)}</h1><p>${escape(description)}</p><p>Pilih bab untuk membaca. Urutan mengikuti pembagian kursus asli, bukan hasil pengelompokan ulang otomatis.</p><ol>${items}</ol><section class="notice" aria-labelledby="edition-note"><h2 id="edition-note">Pembaca terkini dan edisi arsip</h2><p>Tautan bab membuka situs pembaca terkini. Pemeriksaan 31 Agustus 2026 menemukan semua 23 halaman dapat diakses, tetapi isinya tidak identik dengan berkas edisi arsip. Keduanya tidak dianggap edisi yang sama.</p><p><a href="${safeUrl(archive.public_url)}">Unduh edisi WEB yang diarsipkan</a> (${archive.bytes.toLocaleString('id-ID')} byte). Setelah ekstraksi, gunakan nama berkas yang tercantum di bawah setiap bab. Kelengkapan dependensi untuk penggunaan tanpa jaringan belum diverifikasi oleh peta ini.</p></section><details><summary>Untuk pengajar dan pengguna backend</summary><p>Dua tampilan kursus memakai satu graf sumber, tanpa menggandakan unit atau teks buku. Peta ini tidak menyediakan penilaian otomatis atau jangkar latihan yang belum dibuktikan.</p><p><a href="chapters.json">Data peta bab</a> · <a href="route-evidence.json">Bukti rute sumber</a> · <a href="validation.json">Bukti pemeriksaan sambungan bab</a> · <a href="contribution.md">Kontribusi rancangan backend</a></p><p>SHA-256 edisi WEB: <code>${escape(archive.sha256)}</code></p></details></main></body></html>\n`;
  assert.equal((html.match(/data-route-id=/g) ?? []).length, course.chapters.length);
  assert.ok(!/<script\b/i.test(html), 'Chapter navigation must work without JavaScript');
  files.set(`${course.course_id}.html`, Buffer.from(html));
}

const contribution = `# Kontribusi adapter Judson ke backend program\n\nAdapter v2.3.1 ini sekarang dipakai langsung oleh katalog pelajar untuk dua peran kurikulum: C30 dan C40. Satu graf native diproyeksikan menjadi dua peta bab tanpa menggandakan unit atau teks buku.\n\nBerkas \`chapters.json\` mengikat urutan kursus, identitas native, rute publik, anggota arsip, dan batas klaim. Berkas \`route-evidence.json\` adalah salinan byte-identik dari bukti rute yang diterima. Halaman C30 dan C40 bekerja tanpa JavaScript dan membedakan pembaca terkini dari edisi WEB yang diarsipkan.\n\nIntegrasi ini tidak mengklaim jangkar latihan, penilaian otomatis, kesetaraan byte antara pembaca terkini dan arsip, atau kemandirian semua dependensi luring.\n`;
files.set('contribution.md', Buffer.from(contribution));

const validation = {
  schema_id: 'interlanguage/judson-chapter-navigation-validation/v1',
  state: 'pass',
  admission: { path: admissionPath, ...identify(admissionBytes) },
  manifest: { path: manifestPath, ...identify(inputs['manifest.json']), files_verified: manifest.files.length },
  checked_public_package_inputs: inputEntries.length,
  source_bindings: sourceBindings,
  evidence_document: evidenceDocument,
  archive: admission.archive,
  admitted_courses: ['C30', 'C40'],
  native_chapter_joins: 23,
  chapter_counts: { C30: 15, C40: 8 },
  unique_route_ids: 23,
  duplicate_units_created: 0,
  javascript_required: false,
  guessed_descendant_anchors: 0,
  frozen_live_identity_matches_at_recorded_observation: 0,
  artifacts: Object.fromEntries([...files].map(([path, bytes]) => [path, identify(bytes)])),
};
files.set('validation.json', Buffer.from(stable(validation)));

assert.deepEqual([...files.keys()].sort(), ['C30.html', 'C40.html', 'chapters.json', 'contribution.md', 'route-evidence.json', 'validation.json']);
await mkdir(resolve(root, outputRoot), { recursive: true });
for (const [path, bytes] of files) await writeFile(resolve(root, outputRoot, path), bytes);
console.log(JSON.stringify({
  state: 'pass',
  course_views: 2,
  native_chapter_joins: 23,
  verified_public_package_inputs: inputEntries.length,
  outputs: [...files.keys()],
  admission_sha256: hash(admissionBytes),
  generator_sha256: sourceBindings.generator.sha256,
}, null, 2));
