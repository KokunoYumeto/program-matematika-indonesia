import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { courses } from '../docs/courses.js';
import { materializeLiveCourses } from '../docs/live-course-publications.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const inputRoot = 'backend/course-capsule-v1/adapters/openlogic-v231';
const outputRoot = 'docs/backend/openlogic';
const archivePath = 'backend/course-capsule-v1/builds/program-matematika-indonesia-openlogic-c80-v2.3.1.zip';
const admissionPath = `${inputRoot}/ADMISSION.json`;
const expectedArchive = {
  bytes: 2409875,
  sha256: 'eb4293a9745dd7c6f98f7c94c05d214e4dfc904ef5dda3afea571e0ee1363673',
};
const expectedManifest = {
  bytes: 22315,
  sha256: '01974670c902a50d3e0166214f665286e0030a270a781a56413976be52ca4b01',
};
const legacyPdf = {
  filename: '00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf',
  url: 'https://zenodo.org/records/21932787/files/00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf?download=1',
  preview_url: 'https://zenodo.org/records/21932787/preview/00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf',
  pages: 1116,
  bytes: 5593664,
  sha256: 'bf538d5e1994a7a7600703c9d24616696f77e43e9312fb51078095ff0c963c0a',
};
const owner = {
  repository: 'https://github.com/KokunoYumeto/OpenLogic-id',
  release: 'https://github.com/KokunoYumeto/OpenLogic-id/releases/tag/id-olp-0722-20260814',
  version_doi: '10.5281/zenodo.21932787',
  concept_doi: '10.5281/zenodo.21932786',
};

const hash = (bytes) => createHash('sha256').update(bytes).digest('hex');
const identify = (bytes) => ({ bytes: bytes.length, sha256: hash(bytes) });
const stable = (value) => `${JSON.stringify(value, null, 2)}\n`;
const escape = (value) => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
const safeInput = (path) => {
  assert.ok(path && !path.startsWith('/') && !path.includes('..') && !path.includes('\\'));
  return path;
};
const jsonl = (bytes) => {
  const text = bytes.toString('utf8').trimEnd();
  return text ? text.split('\n').map(JSON.parse) : [];
};

const currentReaderPath = 'backend/course-capsule-v1/authority/openlogic-current-reader-v1.json';
const currentReaderBytes = await readFile(resolve(root, currentReaderPath));
const currentReader = JSON.parse(currentReaderBytes);
assert.equal(currentReader.schema_id, 'interlanguage/openlogic-current-reader/v1');
assert.equal(currentReader.status, 'pass');
assert.equal(currentReader.course_id, 'C80');
assert.equal(currentReader.verification.page_geometry_equal, 1255);
assert.equal(currentReader.verification.ordered_page_text_equal, 1255);
assert.equal(currentReader.verification.main_named_destinations_preserved, 8762);
assert.equal(currentReader.verification.exercise_alignment_complete, false);
const pdf = currentReader.primary_reader;
assert.deepEqual({ pages: pdf.pages, bytes: pdf.bytes, sha256: pdf.sha256 }, {
  pages: 1255, bytes: 5754676,
  sha256: '1b763b8b15c9f28a1212d81ee3e3a3f60ee3212fe1ffa4620c947caf43c89930',
});
assert.equal(currentReader.predecessor_reader.sha256, legacyPdf.sha256);

const admissionBytes = await readFile(resolve(root, admissionPath));
const admission = JSON.parse(admissionBytes);
assert.equal(admission.schema_id, 'interlanguage/openlogic-course-capsule-admission/v1');
assert.equal(admission.state, 'locally_admitted_central_release_pending');
assert.equal(admission.course_id, 'C80');
assert.equal(admission.package_tree_sha256, '068abef4fbcb2062443dc7fce1f219cdcf64aabd3e2474076667a65cd6ebf94a');
assert.equal(admission.archive_members, 67);
assert.equal(admission.archive_member_bytes, 20614428);
assert.equal(admission.manifest_bound_files_verified, 64);
assert.equal(admission.seal_bound_files_verified, 65);
assert.equal(admission.checksum_rows_verified, 66);
assert.equal(admission.public_package_excludes_manager_coordination_files, true);
assert.equal(admission.textbook_body_centralized, false);
assert.deepEqual(admission.archive, { path: archivePath, ...expectedArchive });
assert.deepEqual(identify(await readFile(resolve(root, archivePath))), expectedArchive);
assert.deepEqual(admission.authority_validators.map(({ status }) => status), ['pass', 'pass']);

const inputEntries = Object.entries(admission.inputs);
assert.equal(inputEntries.length, 67);
const inputs = {};
for (const [path, identity] of inputEntries) {
  safeInput(path);
  const bytes = await readFile(resolve(root, inputRoot, path));
  assert.deepEqual(identify(bytes), identity, `Open Logic admitted input drift: ${path}`);
  inputs[path] = bytes;
}
assert.deepEqual(identify(inputs['manifest.json']), expectedManifest);
const manifest = JSON.parse(inputs['manifest.json']);
assert.equal(manifest.files.length, 64);
assert.equal(manifest.csv_projection.record_count, 5807);
assert.equal(manifest.build.deterministic_replay, 'byte_identical');
for (const row of manifest.files) {
  assert.equal(row.path_base, 'package_root');
  assert.ok(inputs[row.path]);
  assert.deepEqual(identify(inputs[row.path]), { bytes: row.bytes, sha256: row.sha256 });
}

const readerSurfaces = jsonl(inputs['tables/reader_surfaces.jsonl']);
const artifacts = jsonl(inputs['tables/artifacts.jsonl']);
const units = jsonl(inputs['tables/units.jsonl']);
const relations = jsonl(inputs['tables/relations.jsonl']);
const rightsAssignments = jsonl(inputs['tables/rights_assignments.jsonl']);
const translationState = JSON.parse(inputs['translation-state-index-v0.2.0.json']);
assert.equal(readerSurfaces.length, 1);
assert.equal(units.length, 722);
assert.equal(translationState.records.length, 722);
assert.equal(translationState.records.every((row) => row.state === 'complete'), true);
assert.equal(translationState.no_inference, true);
assert.equal(rightsAssignments.length, 728);
assert.equal(relations.filter((row) => row.payload?.relation_type === 'imports').length, 725);
const reader = readerSurfaces[0].payload;
assert.equal(reader.primary, true);
assert.equal(reader.format, 'linked_pdf');
assert.equal(reader.pages, legacyPdf.pages);
assert.equal(reader.unit_anchor_coverage, 0);
const readerArtifact = artifacts.find((row) => row.payload?.filename === legacyPdf.filename);
assert.ok(readerArtifact);
assert.deepEqual(
  { url: readerArtifact.payload.public_url, bytes: readerArtifact.payload.bytes, sha256: readerArtifact.payload.sha256 },
  { url: legacyPdf.url, bytes: legacyPdf.bytes, sha256: legacyPdf.sha256 },
);

const course = materializeLiveCourses(courses).find((row) => row.id === 'C80');
assert.ok(course);
assert.equal(course.state, 'published');
assert.equal(course.edition, pdf.url);
assert.equal(course.repository, owner.repository);

const route = {
  schema_id: 'interlanguage/openlogic-c80-learner-route/v1',
  recorded_at: '2026-09-28',
  course_id: 'C80',
  title: course.title,
  authority: {
    owner_native_authoritative: true,
    repository: owner.repository,
    release: owner.release,
    version_doi: owner.version_doi,
    concept_doi: owner.concept_doi,
  },
  primary_learner_action: { kind: 'linked_pdf', locale: 'id-ID', ...pdf },
  current_reader_coverage: currentReader.components,
  current_reader_evidence: { path: currentReaderPath, ...identify(currentReaderBytes), ...currentReader.verification },
  predecessor_learner_action: { kind: 'linked_pdf', locale: 'id-ID', ...legacyPdf },
  adapter: {
    state: 'published_shared_projection',
    historical_admission_state: admission.state,
    reader_counts_scope: 'frozen_2026-08-31_adapter_not_current_combined_reader',
    contract_version: '2.3.1',
    native_units: 722,
    reversible_prior_v1_mappings: 722,
    translation_complete_rows: 722,
    ordered_import_relations: 725,
    rights_assignments: 728,
    reader_reachable_units: 642,
    retained_non_reader_units: 80,
    native_html: false,
    unit_or_page_anchors: false,
    machine_data_is_primary_learner_destination: false,
    admission: { path: admissionPath, ...identify(admissionBytes) },
    manifest: { path: `${inputRoot}/manifest.json`, ...identify(inputs['manifest.json']) },
    archive: admission.archive,
  },
  limitations: admission.limits,
  limitations_scope: 'frozen_native_adapter; current reader additionally includes the 80-unit supplement',
};
const routeBytes = Buffer.from(stable(route));
const title = `C80 — ${course.title}`;
const html = `<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)}</title><meta name="description" content="Pembaca gabungan Open Logic Bahasa Indonesia: 1.255 halaman, termasuk 80 unit suplemen."><link rel="stylesheet" href="../backend.css"><style>body{overflow-wrap:anywhere}main{max-width:860px;margin:2rem auto;padding:0 1rem}nav{flex-wrap:wrap;gap:.4rem .8rem}nav[data-central-surface-navigation]{max-width:860px;margin:0 auto;padding:1rem;font-size:.82rem}h1{font-size:clamp(1.9rem,4vw,2.9rem);margin:1.3rem 0}.primary{display:inline-flex;min-height:44px;align-items:center;padding:.65rem 1rem;border:2px solid currentColor;border-radius:.5rem;font-weight:700}.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(12rem,1fr));gap:.75rem}.facts div,details,.notice{padding:1rem;border:1px solid currentColor;border-radius:.5rem}.facts strong{display:block;font-size:1.35rem}a:focus-visible,summary:focus-visible{outline:3px solid currentColor;outline-offset:4px}</style></head>
<body><main><nav aria-label="Navigasi"><a data-program-home href="../../id/#course-C80">← Kembali ke mata kuliah C80</a> · <a href="../index.html">Indeks backend</a> · <a href="https://kokunoyumeto.github.io/OpenLogic-translations/">Pilih bahasa Open Logic</a></nav>
<h1>${escape(title)}</h1><p>Baca edisi gabungan Bahasa Indonesia: pembaca utama dan suplemen berada dalam satu PDF.</p>
<div class="learner-actions"><a class="primary" href="${escape(pdf.url)}">Baca PDF Bahasa Indonesia — 1.255 halaman</a></div>
<p class="notice">1.116 halaman pembaca utama + 139 halaman suplemen. Seluruh teks dan geometri halaman PDF gabungan telah dibandingkan dengan kedua komponennya. Ini bukan pemeriksaan ulang mutu terjemahan atau klaim aksesibilitas PDF yang lengkap.</p>
<section aria-labelledby="closure-title"><h2 id="closure-title">Apa yang tersedia</h2><div class="facts"><div><strong>722</strong>unit sumber: 642 utama + 80 suplemen</div><div><strong>1.255</strong>halaman dalam satu pembaca</div><div><strong>1.117</strong>halaman fisik awal suplemen</div></div>
<p>Pemetaan latihan ke perangkat pengajar masih dikerjakan. Jumlah blok latihan dalam sumber tidak disamakan dengan jumlah kemunculannya dalam PDF: beberapa berkas digunakan kembali dan sebagian isi bersyarat.</p></section>
<section aria-labelledby="source-title"><h2 id="source-title">Sumber yang dapat disunting</h2><ul>
<li><a href="https://github.com/KokunoYumeto/OpenLogic-id/releases/download/id-olp-0722-20260814/01_OPENLOGIC_id_EDITABLE_SOURCES_OLP-0722.zip">Unduh sumber terjemahan utama (ZIP)</a></li>
<li><a href="https://github.com/KokunoYumeto/OpenLogic-id/releases/download/id-olp-0722-20260814/05_OPENLOGIC_id_SUPPLEMENT_SOURCES_80_20260904.zip">Unduh sumber dan penggerak suplemen (ZIP)</a></li>
<li><a href="${escape(owner.release)}">Buka rilis lengkap, atribusi, lisensi, dan catatan perubahan</a></li>
</ul><p>Hak cipta dan atribusi Open Logic Project serta pemberitahuan komponen tetap berlaku. Halaman ini tidak menyalin atau menerjemahkan ulang buku.</p><p>Integrasi dan penyuntingan halaman ini dikerjakan oleh OpenAI Codex — gpt-6-astra, Ultra effort. Riwayat terjemahan buku tetap mengikuti catatan rilisnya; integrasi ini bukan tinjauan manusia.</p></section>
<details class="machine-evidence"><summary>Bukti, versi terdahulu, dan batas pemetaan</summary>
<p>Adapter v2.3.1 yang dibekukan pada 31 Agustus tetap dipertahankan. Catatan lamanya mencakup pembaca 642 unit dan 80 unit sumber tersimpan. Lapisan rute saat ini menambahkan pembaca gabungan yang telah diterbitkan tanpa mengubah sumber atau identitas unit.</p>
<p>Identitas PDF gabungan: ${pdf.bytes.toLocaleString("id-ID")} byte; SHA-256 <code>${pdf.sha256}</code>.</p><ul>
<li><a href="learner-route.json">Rute pelajar, identitas versi, dan batas klaim</a></li><li><a href="validation.json">Hasil validasi rute</a></li>
<li><a href="../../data/v23-adapter-index-v2.json">Indeks adapter bersama</a></li>
<li><a href="${escape(legacyPdf.url)}">Pembaca utama terdahulu — 1.116 halaman</a></li>
<li><a href="https://doi.org/${escape(owner.version_doi)}">Arsip versi terdahulu (${escape(owner.version_doi)})</a></li>
<li><a href="https://doi.org/${escape(owner.concept_doi)}">Seluruh versi pada Zenodo</a></li>
</ul><p>Pembaca HTML native, pemetaan semua latihan, mesin asesmen, dan kepatuhan PDF/UA belum diklaim. Pembaca utama terdahulu tetap dapat diakses.</p></details></main></body></html>
`;
const htmlBytes = Buffer.from(html);
assert.ok(html.indexOf(pdf.url) < html.indexOf('machine-evidence'), 'PDF must precede machine evidence');
assert.equal((html.match(new RegExp(pdf.filename, 'g')) ?? []).length, 1, 'PDF learner URL must not be duplicated');
assert.ok(!/<script\b/i.test(html), 'C80 page must work without JavaScript');

const validation = {
  schema_id: 'interlanguage/openlogic-c80-learner-route-validation/v1',
  state: 'pass',
  recorded_at: '2026-09-28',
  admission: { path: admissionPath, ...identify(admissionBytes) },
  archive: admission.archive,
  manifest: { path: `${inputRoot}/manifest.json`, ...identify(inputs['manifest.json']), files_verified: 64 },
  verified_admitted_inputs: inputEntries.length,
  generic_and_course_validators: admission.authority_validators,
  semantic_counts: route.adapter,
  current_reader_evidence: route.current_reader_evidence,
  current_reader_coverage: route.current_reader_coverage,
  pdf_is_first_learner_action: true,
  machine_data_is_secondary: true,
  javascript_required: false,
  native_html_claimed: false,
  guessed_descendant_anchors: 0,
  outputs: {
    'C80.html': identify(htmlBytes),
    'learner-route.json': identify(routeBytes),
  },
};
const validationBytes = Buffer.from(stable(validation));

await mkdir(resolve(root, outputRoot), { recursive: true });
await Promise.all([
  writeFile(resolve(root, outputRoot, 'C80.html'), htmlBytes),
  writeFile(resolve(root, outputRoot, 'learner-route.json'), routeBytes),
  writeFile(resolve(root, outputRoot, 'validation.json'), validationBytes),
]);
console.log(JSON.stringify({
  state: 'pass',
  course_id: 'C80',
  admitted_inputs: inputEntries.length,
  outputs: {
    'C80.html': identify(htmlBytes),
    'learner-route.json': identify(routeBytes),
    'validation.json': identify(validationBytes),
  },
}, null, 2));
