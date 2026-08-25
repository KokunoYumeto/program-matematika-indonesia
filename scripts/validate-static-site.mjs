import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { courses, program, topics } from '../docs/courses.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const html = await readFile(resolve(root, 'docs/index.html'), 'utf8');
const app = await readFile(resolve(root, 'docs/app.js'), 'utf8');
const catalogSchema = JSON.parse(await readFile(resolve(root, 'schemas/catalog-v1.schema.json'), 'utf8'));

const expectedIds = [
  'A00', 'A10', 'A20', 'A30',
  'B10', 'B20', 'B30', 'B40', 'B50', 'B60', 'B70', 'B80', 'B90', 'B95',
  'C10', 'C20', 'C30', 'C40', 'C50', 'C60', 'C70', 'C80', 'C90', 'C100', 'C110', 'C120', 'C130', 'C140',
  'D10', 'D20', 'D30', 'D40', 'D50', 'D60', 'D70', 'D80', 'D90', 'D100', 'D110', 'D120',
];
const unresolvedIds = [];
const publishedIds = ['A00', 'B10', 'B40', 'B80', 'B90', 'C10', 'C30', 'C40', 'C60', 'C70', 'C80', 'C110', 'C120', 'C130', 'D110'];
const completedPublicEditionIds = ['A00', 'B10', 'B40', 'B80', 'B90', 'C10', 'C30', 'C40', 'C60', 'C70', 'C80', 'C110', 'C120', 'C130', 'D110'];
const publishedHtmlReaderIds = ['A00', 'B10', 'B40', 'B80', 'B90', 'C30', 'C40', 'C60', 'C70', 'C120', 'C130', 'D110'];
const completedPublicRecordDois = [
  '10.5281/zenodo.22070683',
  '10.5281/zenodo.22060439',
  '10.5281/zenodo.22070458',
  '10.5281/zenodo.22053905',
  '10.5281/zenodo.22062144',
  '10.5281/zenodo.22082567',
  '10.5281/zenodo.22062449',
  '10.5281/zenodo.22052196',
  '10.5281/zenodo.22062005',
  '10.5281/zenodo.21932787',
  '10.5281/zenodo.22054086',
  '10.5281/zenodo.22070943',
  '10.5281/zenodo.22070653',
  '10.5281/zenodo.22062017',
];
const expectedOwnerLanes = {
  A00: 'R001', A10: 'OPENSTAX-ELEMENTARY', A20: 'OPENSTAX-INTERMEDIATE', A30: 'R002',
  B10: 'R004', B20: 'R003', B30: 'R003', B40: 'R005', B50: 'R003', B60: 'R003', B70: 'R006-R008', B80: 'O002', B90: 'R010', B95: 'R011',
  C10: 'R006-R008', C20: 'R006-R008', C30: 'R009', C40: 'R009', C50: 'R006-R008', C60: 'R014', C70: 'R012', C80: 'R013', C90: 'O003', C100: 'O004', C110: 'R015', C120: 'O005', C130: 'O018', C140: 'O006',
  D10: 'O007', D20: 'O008', D30: 'O009', D40: 'O010', D50: 'O011', D60: 'O012', D70: 'O013', D80: 'O014', D90: 'O015', D100: 'O016', D110: 'LEAN', D120: 'O017',
};
const levelCounts = { A: 4, B: 10, C: 14, D: 12 };
const allowedStates = new Set(['published', 'near', 'production', 'unresolved']);

assert.equal(courses.length, 40, 'Katalog harus memuat tepat 40 mata kuliah.');
assert.deepEqual(courses.map(({ id }) => id), expectedIds, 'Urutan atau identitas kode mata kuliah berubah.');
assert.equal(new Set(courses.map(({ id }) => id)).size, 40, 'Kode mata kuliah harus unik.');
assert.deepEqual(
  Object.fromEntries(courses.map(({ id, ownerLane }) => [id, ownerLane])),
  expectedOwnerLanes,
  'Pemetaan semantik peran ke pemilik produksi berubah atau terpermutasi.'
);
assert.deepEqual(courses.filter(({ state }) => state === 'unresolved').map(({ id }) => id), unresolvedIds, 'Daftar peran yang belum dibekukan berubah.');
assert.deepEqual(courses.filter(({ state }) => state === 'published').map(({ id }) => id), publishedIds, 'Daftar lima belas peran kanon dengan edisi publik selesai berubah.');
assert.equal(program.version, '0.52.0', 'Versi snapshot pusat harus 0.52.0.');
assert.equal(program.website, 'https://kokunoyumeto.github.io/program-matematika-indonesia/', 'Situs belajar publik tidak tepat.');
assert.equal(program.zenodo, 'https://doi.org/10.5281/zenodo.22088577', 'DOI snapshot Zenodo pusat tidak tepat.');
assert.equal(program.backend.schemaVersion, '1.0.0', 'Versi backend bersama tidak tepat.');
assert.equal(program.backend.status, 'validated', 'Backend bersama harus berada pada batas validasi yang sudah terbukti.');
assert.equal(program.backend.centralRecordCount, 2122, 'Jumlah rekaman paket backend pusat berubah tanpa pembaruan kanon.');
assert.equal(program.provenance.model, 'OpenAI Codex gpt-5.6-sol, Ultra', 'Identitas model provenance pusat harus eksplisit dan tepat.');
assert.deepEqual(
  program.backend.completeCorpusMigrations,
  [
    {
      corpus: 'Discrete Mathematics: An Open Introduction 4 — Bahasa Indonesia',
      recordCount: 163583,
      result: 'lossless-zero-copy-pass'
    },
    {
      corpus: 'Hefferon — Linear Algebra, Bahasa Indonesia v2026.08.22',
      recordCount: 22131,
      result: 'lossless-zero-copy-one-to-one-native-backend-adapter-pass'
    },
    {
      corpus: 'Komputasi Matematis dan Eksperimen yang Dapat Direproduksi — Bahasa Indonesia',
      recordCount: 339,
      result: 'lossless-zero-copy-one-to-one-native-catalog-adapter-pass'
    },
    {
      corpus: 'Open Logic Project — OLP-0722, Bahasa Indonesia',
      recordCount: 6522,
      result: 'deterministic-zero-copy-pass'
    },
    {
      corpus: 'Judson — Abstract Algebra: Theory and Applications, Bahasa Indonesia',
      recordCount: 36978,
      result: 'additive-zero-copy-pass'
    },
    {
      corpus: 'Yet Another Introductory Number Theory Textbook, Bahasa Indonesia',
      recordCount: 6967,
      result: 'lossless-additive-adapter-pass'
    },
    {
      corpus: 'Keller–Trotter — Applied Combinatorics, Bahasa Indonesia',
      recordCount: 19049,
      result: 'lossless-additive-one-common-record-per-native-record-pass'
    },
    {
      corpus: 'Mathematics in Lean — Bahasa Indonesia v4.30.0-id.3',
      recordCount: 10978,
      result: 'lossless-zero-copy-one-to-one-pass'
    },
    {
      corpus: 'OpenStax Prealgebra 2e — Bahasa Indonesia v0.2.7',
      recordCount: 523046,
      result: 'lossless-streaming-zero-copy-adapter-pass'
    },
    {
      corpus: 'Lega v1.01 — Pemodelan Matematis, Bahasa Indonesia',
      recordCount: 16029,
      result: 'lossless-replayable-zero-copy-adapter-pass'
    },
    {
      corpus: 'Open Optimization Book 1 + laboratorium Pyomo/HiGHS O018, Bahasa Indonesia',
      recordCount: 25805,
      result: 'lossless-zero-copy-one-to-one-plus-segment-variant-projection-pass'
    },
    {
      corpus: 'Tea Time Numerical Analysis — Bahasa Indonesia v3.0-id.2-r1',
      recordCount: 53055,
      result: 'additive-zero-copy-virtual-adapter-pass'
    }
  ],
  'Bukti migrasi korpus lengkap berubah tanpa pembaruan kanon.'
);
assert.equal(program.backend.completeCorpusMigrations.length, 12, 'Harus ada tepat 12 bukti migrasi korpus lengkap.');
assert.equal(
  program.backend.completeCorpusMigrations.reduce((sum, row) => sum + row.recordCount, 0),
  884482,
  'Jumlah rekaman target pada 12 migrasi korpus lengkap harus tepat 884.482.'
);
assert.deepEqual(
  program.backend.federationV2,
  {
    version: '0.1.0',
    status: 'validated',
    recordCount: 2439,
    datasetCount: 34,
    courseCount: 40,
    learnerSurfaceCount: 136,
    webRouteCount: 41,
    identityCrosswalkCount: 2122,
    package: 'https://zenodo.org/records/22088577/files/program-matematika-indonesia-backend-v2-v0.52.0.zip?download=1',
    packageSchema: 'https://zenodo.org/records/22088577/files/federation-package-v2.schema.json?download=1',
    recordSchema: 'https://zenodo.org/records/22088577/files/federation-record-v2.schema.json?download=1',
    validationReceipt: 'https://zenodo.org/records/22088577/files/GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v0.52.0.json?download=1'
  },
  'Backend federasi v2 harus cocok dengan batas validasi publik v0.52.0.'
);
assert.equal(program.repositories.github.status, 'available', 'Status transport GitHub harus mencatat pemulihan akses.');
assert.equal(catalogSchema.$id, 'https://zenodo.org/records/22088577/files/program-matematika-indonesia-catalog-v1.schema.json', 'Identitas schema katalog harus terikat ke rekaman v0.52.0 yang dicadangkan.');
assert.deepEqual(program.unresolvedRoleIds, unresolvedIds, 'Metadata program harus memakai daftar peran terbuka yang sama.');
assert.deepEqual(program.completedPublicCourseRoleIds, completedPublicEditionIds, 'Metadata program harus memakai daftar peran edisi selesai yang sama.');
assert.deepEqual(program.completedPublicRecordDois, completedPublicRecordDois, 'Daftar empat belas DOI edisi publik selesai berubah atau tidak lagi memakai versi terkini.');
assert.equal(new Set(program.completedPublicRecordDois).size, 14, 'Lima belas peran edisi selesai harus memetakan ke empat belas rekaman publik berbeda.');
assert.deepEqual(courses.filter(({ reader }) => reader).map(({ id }) => id), publishedHtmlReaderIds, 'Daftar pembaca HTML publik yang diverifikasi berubah.');
for (const id of completedPublicEditionIds) {
  const course = courses.find((candidate) => candidate.id === id);
  assert.ok(course?.edition, `${id}: edisi publik selesai harus memiliki tautan pembaca atau repositori.`);
}
assert.equal(courses.find(({ id }) => id === 'B80')?.state, 'published', 'B80 harus menunjuk edisi 14-unit lengkap yang terverifikasi publik.');
assert.equal(courses.find(({ id }) => id === 'B80')?.zenodo, 'https://doi.org/10.5281/zenodo.22053905', 'B80 harus menunjuk DOI versi lengkap yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'B40')?.state, 'published', 'B40 harus menunjuk edisi Hefferon lengkap yang terverifikasi publik.');
assert.equal(courses.find(({ id }) => id === 'B40')?.zenodo, 'https://doi.org/10.5281/zenodo.22070458', 'B40 harus menunjuk DOI Hefferon yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'B40')?.repository, 'https://github.com/KokunoYumeto/hefferon-linear-algebra-id', 'B40 harus menunjuk repositori Hefferon yang tepat.');
assert.match(courses.find(({ id }) => id === 'B40')?.note ?? '', /580 halaman.*435 halaman.*109 halaman/, 'B40 harus mencatat tiga keluaran Hefferon yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'A00')?.state, 'published', 'A00 harus menunjuk edisi Prealgebra 2e lengkap yang terverifikasi publik.');
assert.equal(courses.find(({ id }) => id === 'A00')?.zenodo, 'https://doi.org/10.5281/zenodo.22070683', 'A00 harus menunjuk DOI Prealgebra 2e v0.2.7 yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'A00')?.repository, 'https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID', 'A00 harus menunjuk repositori Prealgebra 2e yang tepat.');
assert.match(courses.find(({ id }) => id === 'A00')?.note ?? '', /75\/75.*3\.016 halaman.*519\.678 rekaman/, 'A00 harus mencatat batas lengkap pembaca dan backend yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'C120')?.state, 'published', 'C120 harus menunjuk edisi pemodelan matematis lengkap yang terverifikasi publik.');
assert.equal(courses.find(({ id }) => id === 'C120')?.zenodo, 'https://doi.org/10.5281/zenodo.22070943', 'C120 harus menunjuk DOI pemodelan matematis yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'C120')?.repository, 'https://github.com/KokunoYumeto/mathematical-modeling-nonlinear-dynamics-id', 'C120 harus menunjuk repositori pemodelan matematis yang tepat.');
assert.match(courses.find(({ id }) => id === 'C120')?.note ?? '', /22 unit sumber.*4 jembatan.*355 halaman/, 'C120 harus mencatat batas lengkap pemodelan matematis yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'C130')?.state, 'published', 'C130 harus menunjuk edisi riset operasi lengkap yang terverifikasi publik.');
assert.equal(courses.find(({ id }) => id === 'C130')?.zenodo, 'https://doi.org/10.5281/zenodo.22070653', 'C130 harus menunjuk DOI riset operasi yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'C130')?.repository, 'https://github.com/KokunoYumeto/open-optimization-or-book-id', 'C130 harus menunjuk repositori riset operasi yang tepat.');
assert.match(courses.find(({ id }) => id === 'C130')?.note ?? '', /666 halaman.*1\.993 unit.*9\.545 relasi/, 'C130 harus mencatat batas lengkap riset operasi yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'C70')?.state, 'published', 'C70 harus menunjuk edisi Applied Combinatorics lengkap yang terverifikasi publik.');
assert.equal(courses.find(({ id }) => id === 'C70')?.zenodo, 'https://doi.org/10.5281/zenodo.22062005', 'C70 harus menunjuk DOI versi lengkap yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'A30')?.state, 'production', 'A30 harus tetap dalam produksi selama paket pembantu belum diintegrasikan pemilik.');
assert.match(courses.find(({ id }) => id === 'A30')?.note ?? '', /HP-A30-001.*m49369.*m49371.*m49372.*m49374.*m49384.*owner-QA.*belum terintegrasi atau diterbitkan/s, 'A30 harus mencatat cakupan manager-clean HP-A30-001 tanpa mengklaim integrasi atau publikasi.');
assert.equal(courses.find(({ id }) => id === 'B30')?.state, 'production', 'B30 harus tetap dalam produksi sampai R003 lengkap.');
assert.equal(courses.find(({ id }) => id === 'B30')?.zenodo, 'https://doi.org/10.5281/zenodo.22077325', 'B30 harus menunjuk checkpoint CLP WIP.9 yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'B30')?.edition, 'https://zenodo.org/records/22077325/files/CLP-2_Kalkulus_Integral_Bahasa_Indonesia_checkpoint_2026-08-24_s2.1.pdf?download=1', 'B30 harus menunjuk pembaca WIP.9 674 halaman yang tepat.');
assert.match(courses.find(({ id }) => id === 'B30')?.note ?? '', /WIP\.9\/CP0047-R1.*674 halaman.*863e9c5709ff961b3ba09f93da973a8188849d81a4e9680900e1d66a58232bd6.*105\.047.*HP-CLP2-001\/002.*belum lengkap/s, 'B30 harus mencatat batas WIP.9, replay backend, penerimaan paket, dan ketidaklengkapan R003.');
assert.equal(courses.find(({ id }) => id === 'C10')?.state, 'published', 'C10 harus menunjuk Jilid I Lebl lengkap yang terverifikasi publik.');
assert.equal(courses.find(({ id }) => id === 'C10')?.zenodo, 'https://doi.org/10.5281/zenodo.22082567', 'C10 harus menunjuk DOI U336 yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'C10')?.edition, 'https://github.com/KokunoYumeto/lebl-mathematics-family-id/releases/tag/lebl-family-id-wip.2026.08.24.u336', 'C10 harus menunjuk rilis U336 keluarga Lebl.');
assert.equal(courses.find(({ id }) => id === 'C10')?.repository, 'https://github.com/KokunoYumeto/lebl-mathematics-family-id', 'C10 harus menunjuk repositori keluarga Lebl yang tepat.');
assert.match(courses.find(({ id }) => id === 'C10')?.note ?? '', /Jilid I lengkap.*334 halaman.*U336.*336 unit.*R006 271.*R007 15.*R008 50/s, 'C10 harus mencatat Jilid I lengkap dan komposisi U336.');
assert.equal(courses.find(({ id }) => id === 'C20')?.state, 'production', 'C20 harus tetap ditandai sedang diproduksi.');
assert.equal(courses.find(({ id }) => id === 'C20')?.zenodo, 'https://doi.org/10.5281/zenodo.22082567', 'C20 harus menunjuk cuplikan publik U336.');
assert.equal(courses.find(({ id }) => id === 'C20')?.edition, 'https://github.com/KokunoYumeto/lebl-mathematics-family-id/releases/tag/lebl-family-id-wip.2026.08.24.u336', 'C20 harus menunjuk rilis U336 keluarga Lebl.');
assert.equal(courses.find(({ id }) => id === 'C20')?.repository, 'https://github.com/KokunoYumeto/lebl-mathematics-family-id', 'C20 harus menunjuk repositori keluarga Lebl yang tepat.');
assert.match(courses.find(({ id }) => id === 'C20')?.note ?? '', /U336.*198 halaman.*Bagian 11\.4.*semua 11 latihan.*78543d4e8087e68589e8f15d0a3a969b3282247c7c9c2cdcb6f658dfa4b68e4f.*bukan edisi lengkap/s, 'C20 harus mencatat batas U336 Jilid II, latihan, hash, dan ketidaklengkapannya.');
assert.equal(courses.find(({ id }) => id === 'B70')?.state, 'production', 'B70 harus tetap dalam produksi karena korpus ODE belum lengkap.');
assert.equal(courses.find(({ id }) => id === 'B70')?.edition, 'https://github.com/KokunoYumeto/lebl-mathematics-family-id/releases/tag/lebl-family-id-wip.2026.08.24.u336', 'B70 harus menunjuk rilis U336 keluarga Lebl.');
assert.equal(courses.find(({ id }) => id === 'B70')?.zenodo, 'https://doi.org/10.5281/zenodo.22082567', 'B70 harus menunjuk checkpoint U336 yang memuat unit R007.');
assert.equal(courses.find(({ id }) => id === 'B70')?.repository, 'https://github.com/KokunoYumeto/lebl-mathematics-family-id', 'B70 harus menunjuk repositori keluarga Lebl.');
assert.match(courses.find(({ id }) => id === 'B70')?.note ?? '', /U336.*15 unit.*rumus integral tentu.*belum lengkap/s, 'B70 harus menyatakan batas U336 dan ketidaklengkapannya.');
assert.equal(courses.find(({ id }) => id === 'C50')?.state, 'production', 'C50 harus tetap dalam produksi karena korpus analisis kompleks belum lengkap.');
assert.equal(courses.find(({ id }) => id === 'C50')?.edition, 'https://github.com/KokunoYumeto/lebl-mathematics-family-id/releases/tag/lebl-family-id-wip.2026.08.24.u336', 'C50 harus menunjuk rilis U336 keluarga Lebl.');
assert.equal(courses.find(({ id }) => id === 'C50')?.zenodo, 'https://doi.org/10.5281/zenodo.22082567', 'C50 harus menunjuk checkpoint U336 yang memuat unit R008.');
assert.equal(courses.find(({ id }) => id === 'C50')?.repository, 'https://github.com/KokunoYumeto/lebl-mathematics-family-id', 'C50 harus menunjuk repositori keluarga Lebl.');
assert.match(courses.find(({ id }) => id === 'C50')?.note ?? '', /U336.*50 unit.*belum lengkap/s, 'C50 harus menyatakan batas U336 dan ketidaklengkapannya.');
assert.equal(courses.find(({ id }) => id === 'C100')?.state, 'production', 'C100 harus tetap dalam produksi sampai sintesis dan penutupan asli selesai.');
assert.match(courses.find(({ id }) => id === 'C100')?.corpus ?? '', /Petrunin.*donor utama.*CC BY-SA.*Clemens\/Snapp.*pendamping terpisah.*CC BY-NC-SA\/GPL/s, 'C100 harus membedakan donor utama Petrunin dan pendamping Clemens/Snapp dengan hak terpisah.');
assert.match(courses.find(({ id }) => id === 'C100')?.note ?? '', /sintesis asli.*afin.*projektif.*non-Euklides.*rigor.*aset.*solusi.*asesmen.*masih harus diselesaikan/is, 'C100 harus mencatat pekerjaan sintesis dan penutupan yang belum selesai.');
assert.equal(courses.find(({ id }) => id === 'C140')?.state, 'production', 'C140 harus tetap dalam produksi karena spine dan pendampingnya belum lengkap.');
assert.equal(courses.find(({ id }) => id === 'C140')?.zenodo, 'https://doi.org/10.5281/zenodo.22071140', 'C140 harus menunjuk checkpoint pendukung Random 16/29.');
assert.equal(courses.find(({ id }) => id === 'C140')?.repository, 'https://github.com/KokunoYumeto/mathematical-statistics-id', 'C140 harus menunjuk repositori Statistika Matematis.');
assert.equal(courses.find(({ id }) => id === 'C140')?.edition, 'https://zenodo.org/records/22071140/files/00_statistika-matematis-id-reader-2026.08.23.16.pdf?download=1', 'C140 harus menunjuk pembaca checkpoint 16 yang tepat.');
assert.match(courses.find(({ id }) => id === 'C140')?.note ?? '', /16 dari 29.*tidak diklaim sebagai edisi lengkap/, 'C140 harus menyatakan batas checkpoint dan ketidaklengkapannya.');
assert.equal(courses.find(({ id }) => id === 'D20')?.state, 'production', 'D20 harus tetap dalam produksi karena korpus Erdman belum lengkap.');
assert.equal(courses.find(({ id }) => id === 'D20')?.zenodo, 'https://doi.org/10.5281/zenodo.22072541', 'D20 harus menunjuk rekaman publik Bab 12.');
assert.equal(courses.find(({ id }) => id === 'D20')?.repository, 'https://github.com/KokunoYumeto/functional-analysis-erdman-id', 'D20 harus menunjuk repositori Erdman.');
assert.equal(courses.find(({ id }) => id === 'D20')?.edition, 'https://zenodo.org/records/22072541/files/analisis-fungsional-dan-aljabar-operator-id-bab-1-12.pdf?download=1', 'D20 harus menunjuk pembaca Bab 1–12 yang tepat.');
assert.match(courses.find(({ id }) => id === 'D20')?.note ?? '', /Bab 1–12.*Bab 13.*belum selesai/, 'D20 harus menyatakan batas publik dan kelanjutan produksinya.');
assert.equal(courses.find(({ id }) => id === 'D30')?.state, 'production', 'D30 harus terpilih dan tetap ditandai sedang diproduksi sampai korpus selesai.');
assert.equal(courses.find(({ id }) => id === 'D30')?.repository, 'https://github.com/KokunoYumeto/measure-theoretic-probability-stochastic-processes-id', 'D30 harus menunjuk repositori kerja publik yang tepat tanpa melabelinya sebagai edisi selesai.');
assert.equal(courses.find(({ id }) => id === 'D30')?.zenodo, 'https://doi.org/10.5281/zenodo.22074332', 'D30 harus menunjuk checkpoint Zenodo 20 yang terverifikasi.');
assert.match(courses.find(({ id }) => id === 'D30')?.note ?? '', /checkpoint publik 20.*223 halaman.*Tiga dari delapan/i, 'D30 harus menyatakan batas publik dan sisa produksi dengan tepat.');
assert.equal(courses.find(({ id }) => id === 'D40')?.state, 'production', 'D40 harus terpilih dan tetap ditandai sedang diproduksi sampai korpus selesai.');
assert.match(courses.find(({ id }) => id === 'D40')?.corpus ?? '', /Dionne.*8 simpul FEniCSx \(7 wajib \+ 1 pengayaan\)/, 'D40 harus mencatat delapan simpul Dionne/FEniCSx yang dipilih.');
assert.equal(courses.find(({ id }) => id === 'D40')?.zenodo, 'https://doi.org/10.5281/zenodo.22086227', 'D40 harus menunjuk Unit 09 Zenodo yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'D40')?.edition, 'https://zenodo.org/records/22086227/files/PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_UNIT_09.pdf?download=1', 'D40 harus menunjuk pembaca Unit 09 yang tepat.');
assert.match(courses.find(({ id }) => id === 'D40')?.note ?? '', /Unit 09.*77 halaman.*4\.414\.297 byte.*f2869bc0c38153d2223a03e8dccc85c306cefdc4eea15f9fe6a560a6d1f7ce91.*klasifikasi selesai.*tetap diproduksi/s, 'D40 harus menyatakan batas publik Unit 09 dan sisa produksi.');
assert.equal(courses.find(({ id }) => id === 'D50')?.state, 'production', 'D50 harus terpilih dan tetap ditandai sedang diproduksi sampai korpus selesai.');
assert.match(courses.find(({ id }) => id === 'D50')?.corpus ?? '', /Brenner.*jembatan.*ujian/, 'D50 harus mencatat arsitektur Brenner, jembatan asli, dan bank ujian resmi.');
assert.equal(courses.find(({ id }) => id === 'D50')?.zenodo, 'https://doi.org/10.5281/zenodo.22073928', 'D50 harus menunjuk Unit 10 Zenodo yang terverifikasi.');
assert.match(courses.find(({ id }) => id === 'D50')?.note ?? '', /Unit 10.*165 halaman.*Unit 11–13.*belum diterbitkan/, 'D50 harus menyatakan batas publik Unit 10 dan kemajuan lokal Unit 11–13.');
assert.equal(courses.find(({ id }) => id === 'D60')?.state, 'production', 'D60 harus terpilih dan ditandai sedang diproduksi sampai korpus selesai.');
assert.match(courses.find(({ id }) => id === 'D60')?.corpus ?? '', /Roberts.*Fomberg.*penutupan/, 'D60 harus mencatat arsitektur Roberts/Fomberg/penutupan asli yang dipilih.');
assert.equal(courses.find(({ id }) => id === 'D60')?.repository, 'https://github.com/KokunoYumeto/algebraic-topology-id', 'D60 harus menunjuk repositori kerja publik yang tepat.');
assert.equal(courses.find(({ id }) => id === 'D60')?.zenodo, 'https://doi.org/10.5281/zenodo.22084021', 'D60 harus menunjuk batas Roberts 1–30 dan Fomberg §§1.1–1.2 yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'D60')?.edition, 'https://zenodo.org/api/records/22084021/files/00_TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_READER.pdf/content', 'D60 harus menunjuk pembaca komposit 362 halaman yang tepat.');
assert.match(courses.find(({ id }) => id === 'D60')?.note ?? '', /Roberts Kuliah 1–30 lengkap.*Fomberg §§1\.1–1\.2.*362 halaman.*2\.322\.978 byte.*fb81f2b2c0f73c17c4e3be4eaae164eaeaeb0c4ff0661580acfc7aa9b6d5f749.*masih diproduksi/s, 'D60 harus mencatat batas publik komposit terbaru dan sisa penutupannya.');
assert.equal(courses.find(({ id }) => id === 'D70')?.state, 'production', 'D70 harus tetap dalam produksi sampai korpus pascasarjana selesai.');
assert.match(courses.find(({ id }) => id === 'D70')?.corpus ?? '', /Wen-Wei Li.*Alexander Duncan.*CC BY 4\.0.*CRing\/GFDL.*penghubung dan solusi asli/s, 'D70 harus memakai arsitektur Li/Duncan/CRing dan lapisan asli yang dipilih.');
assert.match(courses.find(({ id }) => id === 'D70')?.note ?? '', /Etingof\/MIT tetap referensi saja.*lembar tugas eksternal dikecualikan/s, 'D70 harus menjaga Etingof sebagai referensi dan mengecualikan lembar tugas eksternal.');
assert.equal(courses.find(({ id }) => id === 'D90')?.state, 'production', 'D90 harus terpilih dan ditandai sedang diproduksi sampai korpus selesai.');
assert.match(courses.find(({ id }) => id === 'D90')?.corpus ?? '', /Habring arXiv 2607\.11664v1.*CC BY 4\.0.*Becker.*MIT.*KKT.*stokastik.*variasional.*solusi asli/s, 'D90 harus mencatat spine Habring, modul Becker, dan penutupan asli yang dipilih.');
assert.match(courses.find(({ id }) => id === 'D90')?.note ?? '', /MIT 6\.253 dan Royer.*pendamping.*bukan spine kanonik.*MIT L10.*10 halaman.*3b01d57e8e8a7d7887f36cfdc205d1b68d1d007a152bd8e0cd75479628e1abc0.*L11 masih lokal/s, 'D90 harus memisahkan spine editabel dari checkpoint pendamping publik dan kemajuan lokal.');
assert.equal(courses.find(({ id }) => id === 'D90')?.repository, 'https://github.com/KokunoYumeto/advanced-optimization-convex-analysis-id', 'D90 harus menunjuk repositori kerja publik yang tepat.');
assert.equal(courses.find(({ id }) => id === 'D90')?.zenodo, 'https://doi.org/10.5281/zenodo.22077419', 'D90 harus menunjuk checkpoint pendamping MIT L10 yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'D90')?.edition, 'https://zenodo.org/records/22077419/files/D90-MIT-10-kuliah-6-irisan-tertutup-dan-hiperbidang-id.pdf?download=1', 'D90 harus menunjuk PDF pendamping MIT L10 yang tepat.');
assert.equal(courses.find(({ id }) => id === 'D100')?.state, 'production', 'D100 harus terpilih dan ditandai sedang diproduksi sampai korpus selesai.');
assert.match(courses.find(({ id }) => id === 'D100')?.corpus ?? '', /Brenner Algebraische Kurven.*Bündel, Garben und Kohomologie/, 'D100 harus mencatat dua volume Brenner yang dipilih.');
assert.equal(courses.find(({ id }) => id === 'D100')?.zenodo, 'https://doi.org/10.5281/zenodo.22077441', 'D100 harus menunjuk batas publik Unit 15.');
assert.equal(courses.find(({ id }) => id === 'D100')?.repository, 'https://github.com/KokunoYumeto/algebraic-geometry-bridge-id', 'D100 harus menunjuk repositori jembatan geometri aljabar yang tepat.');
assert.equal(courses.find(({ id }) => id === 'D100')?.edition, 'https://zenodo.org/records/22077441/files/kurva-aljabar-id-unit-15.pdf?download=1', 'D100 harus menunjuk pembaca Unit 15 yang tepat.');
assert.match(courses.find(({ id }) => id === 'D100')?.note ?? '', /Unit 1–15.*267 halaman.*6\.502\.255 byte.*e56aae414a9d7e252485d06e7da790fae9bf972514c8fe47fc31d26eddd3699c.*Unit 16–18.*bukan rilis publik.*Unit 19.*belum didispatch/s, 'D100 harus membedakan batas publik Unit 15, checkpoint lokal, dan paket Unit 19 yang belum didispatch.');
assert.equal(courses.find(({ id }) => id === 'C110')?.zenodo, 'https://doi.org/10.5281/zenodo.22054086', 'C110 harus menunjuk DOI edisi lengkap yang terverifikasi.');

const ids = new Set(courses.map(({ id }) => id));
for (const course of courses) {
  assert.ok(allowedStates.has(course.state), `${course.id}: status tidak dikenal.`);
  assert.ok(topics.includes(course.topic), `${course.id}: bidang tidak tercantum.`);
  assert.equal(course.level, course.id[0], `${course.id}: tingkat tidak cocok dengan kode.`);
  for (const prerequisite of course.prerequisites) {
    assert.ok(ids.has(prerequisite), `${course.id}: prasyarat ${prerequisite} tidak ditemukan.`);
    assert.notEqual(prerequisite, course.id, `${course.id}: prasyarat tidak boleh menunjuk dirinya sendiri.`);
  }
  for (const field of ['title', 'purpose', 'outcome', 'corpus', 'note']) {
    assert.ok(typeof course[field] === 'string' && course[field].trim(), `${course.id}: ${field} kosong.`);
  }
  assert.equal(course.ownerLane, expectedOwnerLanes[course.id], `${course.id}: pemilik produksi tidak cocok dengan registri semantik.`);
  for (const field of ['reader', 'edition', 'repository', 'zenodo']) {
    if (course[field]) assert.match(course[field], /^https:\/\//, `${course.id}: ${field} harus memakai HTTPS.`);
  }
}

for (const [level, expected] of Object.entries(levelCounts)) {
  assert.equal(courses.filter((course) => course.level === level).length, expected, `Jumlah tingkat ${level} salah.`);
}

assert.equal(new Set(topics).size, topics.length, 'Bidang harus unik.');
assert.match(html, /<html lang="id">/, 'Bahasa dokumen harus Bahasa Indonesia.');
assert.match(html, /href="styles\.css"/, 'Stylesheet statis tidak terhubung.');
assert.match(html, /src="app\.js"/, 'Aplikasi katalog tidak terhubung.');
assert.match(html, /class="english-note" lang="en"/, 'Catatan Inggris sekunder di footer tidak ditemukan.');
assert.match(html, /property="og:image" content="https:\/\/kokunoyumeto\.github\.io\/program-matematika-indonesia\/og\.png"/, 'Kartu sosial situs belajar tidak terhubung.');
assert.match(html, /rel="canonical" href="https:\/\/kokunoyumeto\.github\.io\/program-matematika-indonesia\/"/, 'URL kanonis situs belajar tidak tepat.');
assert.match(html, /40 korpus terpilih/, 'Ringkasan 40 korpus terpilih hilang.');
assert.match(html, /Produksi yang belum selesai tetap dilabeli dengan jelas/, 'Ringkasan batas produksi hilang.');
assert.match(html, /<strong>15<\/strong><span>peran dengan edisi selesai<\/span>/, 'Ringkasan lima belas peran dengan edisi selesai hilang.');
assert.match(html, /https:\/\/doi\.org\/10\.5281\/zenodo\.22088577/, 'Tautan snapshot Zenodo pusat hilang dari HTML.');
assert.match(html, /Mulai belajar — buka 40 mata kuliah/, 'Aksi utama untuk pelajar tidak terlihat.');
assert.match(html, /https:\/\/github\.com\/KokunoYumeto\/program-matematika-indonesia/, 'Tautan repositori GitHub pusat hilang dari HTML.');
assert.match(app, /editionIsSuspendedGithub/, 'Aplikasi harus menahan tautan repositori GitHub yang sementara tidak tersedia.');
assert.match(app, /Mulai belajar — HTML/, 'Aplikasi harus menempatkan pembaca HTML sebagai aksi utama bila tersedia.');
assert.match(app, /course\.repository/, 'Aplikasi harus menampilkan tautan repositori korpus pada kartu edisi.');

const blankTargets = [...html.matchAll(/<a\b[^>]*target="_blank"[^>]*>/g)].map(([tag]) => tag);
for (const tag of blankTargets) assert.match(tag, /rel="[^"]*noreferrer[^"]*"/, `Tautan tab baru tanpa rel=noreferrer: ${tag}`);

console.log(JSON.stringify({
  status: 'pass',
  courses: courses.length,
  selected: courses.filter(({ state }) => state !== 'unresolved').length,
  unresolved: unresolvedIds.length,
  publishedCanonRoles: publishedIds.length,
  completedPublicCourseRoles: completedPublicEditionIds.length,
  completedPublicRecords: completedPublicRecordDois.length,
  publishedHtmlReaders: publishedHtmlReaderIds.length,
  topics: topics.length,
  levelCounts,
}, null, 2));
