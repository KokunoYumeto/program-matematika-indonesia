import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { courses } from '../docs/courses.js';

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
const pdf = {
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
assert.equal(reader.pages, pdf.pages);
assert.equal(reader.unit_anchor_coverage, 0);
const readerArtifact = artifacts.find((row) => row.payload?.filename === pdf.filename);
assert.ok(readerArtifact);
assert.deepEqual(
  { url: readerArtifact.payload.public_url, bytes: readerArtifact.payload.bytes, sha256: readerArtifact.payload.sha256 },
  { url: pdf.url, bytes: pdf.bytes, sha256: pdf.sha256 },
);

const course = courses.find((row) => row.id === 'C80');
assert.ok(course);
assert.equal(course.state, 'published');
assert.equal(course.edition, pdf.url);
assert.equal(course.repository, owner.repository);

const route = {
  schema_id: 'interlanguage/openlogic-c80-learner-route/v1',
  recorded_at: '2026-08-31',
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
  adapter: {
    state: 'locally_admitted_central_release_pending',
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
};
const routeBytes = Buffer.from(stable(route));
const title = `C80 — ${course.title}`;
const html = `<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)}</title><meta name="description" content="Pembaca Bahasa Indonesia Open Logic lengkap dan bukti pemetaan 722 unit."><link rel="stylesheet" href="../backend.css"><style>main{max-width:860px;margin:2rem auto;padding:0 1rem}.primary{display:inline-flex;min-height:44px;align-items:center;padding:.65rem 1rem;border:2px solid currentColor;border-radius:.5rem;font-weight:700}.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(12rem,1fr));gap:.75rem}.facts div,details,.notice{padding:1rem;border:1px solid currentColor;border-radius:.5rem}.facts strong{display:block;font-size:1.35rem}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}a:focus-visible,summary:focus-visible{outline:3px solid currentColor;outline-offset:4px}</style></head><body><main><nav aria-label="Navigasi"><a data-program-home href="../../id/#course-C80">← Kembali ke mata kuliah C80</a> · <a href="../index.html">Indeks backend</a> · <a href="https://kokunoyumeto.github.io/OpenLogic-translations/">Pilih bahasa Open Logic</a></nav><h1>${escape(title)}</h1><p>Open Logic Project lengkap dalam Bahasa Indonesia. Mulai dari pembaca, bukan dari data mesin.</p><div class="learner-actions"><a class="primary" href="${escape(pdf.url)}">Baca PDF Bahasa Indonesia — 1.116 halaman<span class="sr-only"> (dibuka di tab yang sama)</span></a></div><p class="notice">PDF publik telah dibaca ulang secara anonim: ${pdf.bytes.toLocaleString('id-ID')} byte, SHA-256 <code>${pdf.sha256}</code>. Pembaca dapat ditelusuri, tetapi PDF belum diklaim sepenuhnya aksesibel.</p><section aria-labelledby="closure-title"><h2 id="closure-title">Cakupan yang dipetakan</h2><div class="facts"><div><strong>722/722</strong>unit terjemahan lengkap</div><div><strong>725</strong>relasi impor berurutan</div><div><strong>642 + 80</strong>unit pembaca + unit tersimpan</div><div><strong>0</strong>jangkar unit/halaman yang ditebak</div></div></section><details class="machine-evidence"><summary>Data mesin dan bukti pemetaan</summary><p>Adapter v2.3.1 telah diterima secara lokal dan lulus dua validator, tetapi publikasi adapter pusat masih menunggu rilis penerus. Status ini tidak mengubah status buku yang sudah publik.</p><ul><li><a href="learner-route.json">Rute pelajar dan batas klaim</a></li><li><a href="validation.json">Bukti validasi proyeksi ini</a></li><li><a href="../../data/v23-adapter-index-v2.json">Indeks adapter penerus</a></li><li><a href="${escape(owner.repository)}">Repositori sumber Indonesia<span class="sr-only"> (dibuka di situs lain)</span></a></li><li><a href="https://doi.org/${escape(owner.version_doi)}">DOI versi ${escape(owner.version_doi)}</a></li><li><a href="https://doi.org/${escape(owner.concept_doi)}">DOI konsep ${escape(owner.concept_doi)}</a></li></ul><p>Tidak ada pembaca HTML native, jangkar unit, jangkar halaman, atau mesin asesmen yang diklaim.</p></details></main></body></html>
`;
const htmlBytes = Buffer.from(html);
assert.ok(html.indexOf(pdf.url) < html.indexOf('machine-evidence'), 'PDF must precede machine evidence');
assert.equal((html.match(new RegExp(pdf.filename, 'g')) ?? []).length, 1, 'PDF learner URL must not be duplicated');
assert.ok(!/<script\b/i.test(html), 'C80 page must work without JavaScript');

const validation = {
  schema_id: 'interlanguage/openlogic-c80-learner-route-validation/v1',
  state: 'pass',
  recorded_at: '2026-08-31',
  admission: { path: admissionPath, ...identify(admissionBytes) },
  archive: admission.archive,
  manifest: { path: `${inputRoot}/manifest.json`, ...identify(inputs['manifest.json']), files_verified: 64 },
  verified_admitted_inputs: inputEntries.length,
  generic_and_course_validators: admission.authority_validators,
  semantic_counts: route.adapter,
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
