import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { englishResources } from '../docs/interface/locales.js';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const outputArgument = process.argv.find((value) => value.startsWith('--output-root='));
const outputRoot = outputArgument ? resolve(outputArgument.slice('--output-root='.length)) : project;
const sourcePath = 'backend/course-capsule-v1/authority/clp-family-v231/learner-reader-actions-v1.json';
const adapterIndexPath = 'docs/data/clp-successor/v0.62.17/v23-adapter-index-v2.json';
const originalSourcePath = 'docs/interface/locales.js';
const outputDirectory = resolve(outputRoot, 'docs/backend/clp');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const fact = (path, bytes) => ({ path, bytes: bytes.length, sha256: sha256(bytes) });
const json = (value) => Buffer.from(JSON.stringify(value, null, 2) + '\n');
const esc = (value) => String(value).replace(/[&<>"']/gu, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[character]);

const [sourceBytes, adapterIndexBytes, originalSourceBytes] = await Promise.all([
  readFile(resolve(project, sourcePath)),
  readFile(resolve(project, adapterIndexPath)),
  readFile(resolve(project, originalSourcePath)),
]);
const source = JSON.parse(sourceBytes);
const adapterIndex = JSON.parse(adapterIndexBytes);
assert.equal(source.schema_id, 'interlanguage/learner-reader-actions/v1');
assert.equal(source.status, 'verified_route_evidence_projection');
assert.deepEqual(source.summary, {
  action_count: 7,
  bytes: 35639691,
  chapter_or_unit_routes_claimed: false,
  course_count: 4,
  native_html_claimed: false,
  pages: 4077,
  route_granularity: 'whole_file_only',
  verified_action_count: 7,
});

const expectedCourses = ['B20', 'B30', 'B50', 'B60'];
assert.equal(adapterIndex.schema_id, 'interlanguage/program-matematika-indonesia-v23-adapter-index/v2');
const sharedAdapter = adapterIndex.packages.find((row) => row.native_family_id === 'family-06-clp');
assert.ok(sharedAdapter);
assert.equal(sharedAdapter.admission_state, 'published');
assert.equal(sharedAdapter.public_replay_status, 'published_public_asset_readback_verified');
assert.equal(sharedAdapter.archive.bytes, 545418367);
assert.equal(sharedAdapter.archive.sha256, 'f2e2714c5f1349092e8cb574d6495e604086c9df3bc4bdf5bbe5974b5f61360d');
assert.equal(sharedAdapter.canonical_records, 1201557);
assert.equal(sharedAdapter.unit_records, 53676);
assert.equal(sharedAdapter.relation_records, 138673);
assert.equal(sharedAdapter.reversible_native_mappings, 285630);
assert.match(sharedAdapter.public_asset_url, /^https:\/\/github\.com\/KokunoYumeto\/program-matematika-indonesia\/releases\/download\//u);
const actionIds = new Set();
const actionsByCourse = new Map(expectedCourses.map((courseId) => [courseId, []]));
for (const action of source.actions) {
  assert.ok(actionsByCourse.has(action.course_id), `Unexpected CLP course: ${action.course_id}`);
  assert.ok(!actionIds.has(action.action_id), `Duplicate action: ${action.action_id}`);
  actionIds.add(action.action_id);
  assert.equal(action.state, 'verified');
  assert.equal(action.route_granularity, 'whole_file_only');
  assert.equal(action.format, 'application/pdf');
  assert.equal(action.license, 'CC BY-NC-SA 4.0');
  assert.equal(action.offline.dependency_free_after_download, true);
  assert.equal(action.offline.post_download_reading_is_offline, true);
  assert.match(action.url, /^https:\/\/zenodo\.org\/records\/[0-9]+\/files\//u);
  assert.match(action.sha256, /^[a-f0-9]{64}$/u);
  assert.ok(Number.isSafeInteger(action.bytes) && action.bytes > 0);
  assert.ok(Number.isSafeInteger(action.pages) && action.pages > 0);
  actionsByCourse.get(action.course_id).push(action);
}
assert.equal(actionIds.size, 7);
assert.equal(source.actions.reduce((sum, action) => sum + action.bytes, 0), source.summary.bytes);
assert.equal(source.actions.reduce((sum, action) => sum + action.pages, 0), source.summary.pages);
for (const courseId of expectedCourses) assert.ok(actionsByCourse.get(courseId).length > 0);

const courseTitles = {
  B20: 'Kalkulus Diferensial',
  B30: 'Kalkulus Integral',
  B50: 'Kalkulus Multivariabel',
  B60: 'Kalkulus Vektor',
};
const courses = expectedCourses.map((courseId) => {
  const actions = actionsByCourse.get(courseId).sort((left, right) => left.course_order - right.course_order);
  const originals = (englishResources[courseId] ?? []).filter((row) => row.accessRole === 'authoritative-original');
  assert.equal(originals.length, 1, `${courseId} must have one authoritative CLP original`);
  assert.match(originals[0].href, /^https:\/\//u);
  return {
    course_id: courseId,
    title: courseTitles[courseId],
    entry_route: `${courseId}.html`,
    pages: actions.reduce((sum, action) => sum + action.pages, 0),
    bytes: actions.reduce((sum, action) => sum + action.bytes, 0),
    authoritative_original: {
      label: originals[0].label,
      url: originals[0].href,
      content_language: originals[0].contentLanguage,
    },
    actions,
  };
});
const model = {
  schema: 'clp-family-learner-capability/1',
  status: 'verified-presentation-projection',
  locale: 'id-ID',
  source: fact(sourcePath, sourceBytes),
  inputs: {
    reader_actions: fact(sourcePath, sourceBytes),
    shared_adapter_index: fact(adapterIndexPath, adapterIndexBytes),
    authoritative_original_registry: fact(originalSourcePath, originalSourceBytes),
  },
  evidence_boundary: {
    content_copy_included: false,
    route_granularity: 'whole_file_only',
    chapter_or_unit_routes_claimed: false,
    native_html_claimed: false,
    offline_claim: 'Each PDF is dependency-free after a separate network download.',
    authority_note: 'This learner view presents the frozen CLP v2.3.1 route evidence without changing the books or their native backend.',
  },
  summary: source.summary,
  shared_adapter: {
    counted_packages: 1,
    package_id: sharedAdapter.package_id,
    contract_version: sharedAdapter.contract_version,
    archive: sharedAdapter.archive,
    public_asset_url: sharedAdapter.public_asset_url,
    release_url: sharedAdapter.release_url,
    canonical_records: sharedAdapter.canonical_records,
    unit_records: sharedAdapter.unit_records,
    relation_records: sharedAdapter.relation_records,
    reversible_native_mappings: sharedAdapter.reversible_native_mappings,
    owner_native_authoritative: sharedAdapter.owner_native_authoritative,
    learner_relationship: 'The central view consumes the verified route projection; the PDF readers themselves are not claimed to consume this adapter.',
  },
  courses,
};
const modelBytes = json(model);

const actionCard = (action) => `<article class="resource"><h3>${esc(action.role === 'problembook' ? 'Buku soal dan penyelesaian' : action.role === 'combined_textbook_problembook' ? 'Buku gabungan teks dan soal' : 'Buku teks')}</h3><p>${action.pages.toLocaleString('id-ID')} halaman · ${esc(action.license)} · PDF</p><p><a class="button" href="${esc(action.url)}" data-reader-action="${esc(action.action_id)}">Buka atau unduh PDF</a> <a href="${esc(action.evidence.locator)}">Rekaman dan berkas publik</a></p><details><summary>Identitas berkas</summary><dl><dt>Nama</dt><dd><code>${esc(action.filename)}</code></dd><dt>Byte</dt><dd>${action.bytes}</dd><dt>SHA-256</dt><dd><code>${action.sha256}</code></dd><dt>Granularitas</dt><dd>Seluruh berkas; tidak ada jangkar bab atau unit yang diklaim.</dd></dl></details></article>`;
const section = (course) => `<section class="course" id="course-${course.course_id}" data-course="${course.course_id}" tabindex="-1"><p class="eyebrow">${course.course_id}</p><h2>${esc(course.title)}</h2><p>${course.pages.toLocaleString('id-ID')} halaman dalam ${course.actions.length} berkas terverifikasi.</p><p><strong>Sumber asli berbahasa Inggris:</strong> <a data-authoritative-original href="${esc(course.authoritative_original.url)}">${esc(course.authoritative_original.label)}</a>. Mirror Bahasa Indonesia dan sumber asli sengaja dipertahankan sebagai dua pilihan yang berbeda.</p><div class="resources">${course.actions.map(actionCard).join('')}</div><p><a href="#top">Kembali ke atas</a></p></section>`;
const navigation = courses.map((course) => `<a href="${course.course_id}.html">${course.course_id} · ${esc(course.title)}</a>`).join('');
const renderPage = (selectedCourse = null) => {
  const selected = selectedCourse ? courses.find((course) => course.course_id === selectedCourse) : null;
  assert.ok(!selectedCourse || selected);
  const title = selected ? `${selected.course_id} · ${selected.title}` : 'Keluarga CLP — rute baca terverifikasi';
  const lead = selected
    ? `${selected.pages.toLocaleString('id-ID')} halaman dalam ${selected.actions.length} PDF seluruh berkas yang telah diverifikasi.`
    : `Empat mata kuliah kalkulus, tujuh PDF, ${source.summary.pages.toLocaleString('id-ID')} halaman. Pilih mata kuliah lalu buka buku yang sudah diverifikasi.`;
  const body = selected ? section(selected) : courses.map(section).join('\n');
  return `<!doctype html>\n<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><link rel="stylesheet" href="../backend.css"><style>.course{margin:2rem 0;padding:1.25rem;border:1px solid #cad6d0;border-radius:.8rem;background:#fff}.resources{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem}.resource{padding:1rem;border:1px solid #dfe7e2;border-radius:.6rem}.button{display:inline-block;padding:.55rem .75rem;background:#086b63;color:#fff;border-radius:.35rem}.course-picker{display:flex;flex-wrap:wrap;gap:.7rem}.course-picker a{padding:.35rem .55rem;background:#e0eae3;border-radius:.35rem}code{overflow-wrap:anywhere}.eyebrow{font-weight:700;color:#086b63}</style></head><body><main id="top"><nav><a href="../index.html">Indeks backend</a> · <a href="../../id/">Program Matematika</a>${selected ? ' · <a href="CLP.html">Seluruh keluarga CLP</a>' : ''}</nav><h1>${esc(title)}</h1><p>${esc(lead)}</p><nav class="course-picker" aria-label="Pilih mata kuliah">${navigation}<a href="CLP.html">Tampilkan semua</a></nav><aside><h2>Batas bukti</h2><p>Halaman ini hanya mengindeks rute PDF seluruh berkas yang terikat pada bukti publik. Halaman ini tidak mengklaim pembaca HTML native, jangkar bab atau unit, atau penyalinan isi buku ke backend pusat. Setelah PDF diunduh, pembacaannya tidak memerlukan jaringan.</p></aside>${body}<details><summary>Data mesin bersama (sekunder)</summary><p>Keempat mata kuliah memakai satu paket adapter bersama—bukan empat salinan—dengan ${sharedAdapter.canonical_records.toLocaleString('id-ID')} rekaman kanonis, ${sharedAdapter.unit_records.toLocaleString('id-ID')} rekaman unit, ${sharedAdapter.relation_records.toLocaleString('id-ID')} relasi, dan ${sharedAdapter.reversible_native_mappings.toLocaleString('id-ID')} pemetaan reversibel. Backend native pemilik tetap menjadi otoritas; PDF tidak diklaim mengonsumsi adapter ini.</p><p><a href="${esc(sharedAdapter.public_asset_url)}">Unduh paket adapter CLP v2.3.1</a> · <a href="${esc(sharedAdapter.release_url)}">Rilis dan bukti publik</a></p></details><p><a href="learning-map.json">Data terbuka untuk tampilan ini</a> · <a href="../../data/course-capsule-v1/learner-reader-actions-v1.json">Proyeksi tindakan baca kanonis</a></p></main></body></html>\n`;
};
const htmlBytes = Buffer.from(renderPage());
const courseEntryBytes = Object.fromEntries(expectedCourses.map((courseId) => [courseId, Buffer.from(renderPage(courseId))]));
const validation = {
  schema: 'clp-family-capability-validation/1',
  state: 'pass',
  source: fact(sourcePath, sourceBytes),
  inputs: model.inputs,
  outputs: {
    family_index_source_body: fact('docs/backend/clp/CLP.html', htmlBytes),
    course_entry_source_bodies: Object.fromEntries(expectedCourses.map((courseId) => [courseId, fact(`docs/backend/clp/${courseId}.html`, courseEntryBytes[courseId])])),
    learning_map: fact('docs/backend/clp/learning-map.json', modelBytes),
  },
  assertions: {
    exact_course_ids: expectedCourses,
    action_count: 7,
    total_pages: 4077,
    total_bytes: 35639691,
    all_actions_receipt_bound: true,
    all_actions_whole_file_only: true,
    all_actions_offline_after_download: true,
    all_courses_link_authoritative_original: true,
    shared_adapter_counted_once: true,
    shared_adapter_public_readback_verified: true,
    pdf_runtime_adapter_consumption_claimed: false,
    no_native_html_claim: true,
    no_chapter_or_unit_route_claim: true,
    mathematical_content_rewritten: false,
  },
};
const validationBytes = json(validation);
await mkdir(outputDirectory, { recursive: true });
await Promise.all([
  writeFile(resolve(outputDirectory, 'CLP.html'), htmlBytes),
  ...expectedCourses.map((courseId) => writeFile(resolve(outputDirectory, `${courseId}.html`), courseEntryBytes[courseId])),
  writeFile(resolve(outputDirectory, 'learning-map.json'), modelBytes),
  writeFile(resolve(outputDirectory, 'validation.json'), validationBytes),
]);
console.log(JSON.stringify({ state: 'pass', courses: expectedCourses.length, actions: 7, pages: 4077, bytes: 35639691 }));
