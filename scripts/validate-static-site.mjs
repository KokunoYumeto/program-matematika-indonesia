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
const completedPublicRecordDois = [
  '10.5281/zenodo.22070683',
  '10.5281/zenodo.22060439',
  '10.5281/zenodo.22070458',
  '10.5281/zenodo.22053905',
  '10.5281/zenodo.22062144',
  '10.5281/zenodo.22073827',
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
assert.equal(program.version, '0.50.0', 'Versi snapshot pusat harus 0.50.0.');
assert.equal(program.zenodo, 'https://doi.org/10.5281/zenodo.22074701', 'DOI snapshot Zenodo pusat tidak tepat.');
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
    }
  ],
  'Bukti migrasi korpus lengkap berubah tanpa pembaruan kanon.'
);
assert.equal(program.repositories.github.status, 'available', 'Status transport GitHub harus mencatat pemulihan akses.');
assert.equal(catalogSchema.$id, 'https://zenodo.org/records/22074701/files/program-matematika-indonesia-catalog-v1.schema.json', 'Identitas schema katalog harus terikat ke rekaman v0.50.0 yang dicadangkan.');
assert.deepEqual(program.unresolvedRoleIds, unresolvedIds, 'Metadata program harus memakai daftar peran terbuka yang sama.');
assert.deepEqual(program.completedPublicCourseRoleIds, completedPublicEditionIds, 'Metadata program harus memakai daftar peran edisi selesai yang sama.');
assert.deepEqual(program.completedPublicRecordDois, completedPublicRecordDois, 'Daftar empat belas DOI edisi publik selesai berubah atau tidak lagi memakai versi terkini.');
assert.equal(new Set(program.completedPublicRecordDois).size, 14, 'Lima belas peran edisi selesai harus memetakan ke empat belas rekaman publik berbeda.');
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
assert.equal(courses.find(({ id }) => id === 'C10')?.state, 'published', 'C10 harus menunjuk Jilid I Lebl lengkap yang terverifikasi publik.');
assert.equal(courses.find(({ id }) => id === 'C10')?.zenodo, 'https://doi.org/10.5281/zenodo.22073827', 'C10 harus menunjuk DOI U319 yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'C10')?.edition, 'https://zenodo.org/records/22073827/files/Analisis_Dasar_I_Bahasa_Indonesia_v6.3.pdf?download=1', 'C10 harus menunjuk pembaca lengkap Jilid I yang tepat.');
assert.equal(courses.find(({ id }) => id === 'C10')?.repository, 'https://github.com/KokunoYumeto/lebl-mathematics-family-id', 'C10 harus menunjuk repositori keluarga Lebl yang tepat.');
assert.match(courses.find(({ id }) => id === 'C10')?.note ?? '', /334 halaman/, 'C10 harus mencatat panjang pembaca lengkap yang terverifikasi.');
assert.equal(courses.find(({ id }) => id === 'C20')?.state, 'production', 'C20 harus tetap ditandai sedang diproduksi.');
assert.equal(courses.find(({ id }) => id === 'C20')?.zenodo, 'https://doi.org/10.5281/zenodo.22073827', 'C20 harus menunjuk cuplikan publik U319.');
assert.equal(courses.find(({ id }) => id === 'C20')?.edition, 'https://zenodo.org/records/22073827/files/Analisis_Dasar_II_Bahasa_Indonesia_v6.3_WIP_sampai_11.2_Latihan.pdf?download=1', 'C20 harus menunjuk pembaca WIP Jilid II U319 yang tepat.');
assert.equal(courses.find(({ id }) => id === 'C20')?.repository, 'https://github.com/KokunoYumeto/lebl-mathematics-family-id', 'C20 harus menunjuk repositori keluarga Lebl yang tepat.');
assert.match(courses.find(({ id }) => id === 'C20')?.note ?? '', /180 halaman.*bukan edisi lengkap/, 'C20 harus menyatakan batas cuplikan dan ketidaklengkapannya.');
assert.equal(courses.find(({ id }) => id === 'B70')?.state, 'production', 'B70 harus tetap dalam produksi karena korpus ODE belum lengkap.');
assert.equal(courses.find(({ id }) => id === 'B70')?.edition, undefined, 'B70 belum memiliki pembaca ODE mandiri.');
assert.equal(courses.find(({ id }) => id === 'B70')?.zenodo, 'https://doi.org/10.5281/zenodo.22073827', 'B70 harus menunjuk checkpoint U319 yang memuat unit R007.');
assert.equal(courses.find(({ id }) => id === 'B70')?.repository, 'https://github.com/KokunoYumeto/lebl-mathematics-family-id', 'B70 harus menunjuk repositori keluarga Lebl.');
assert.match(courses.find(({ id }) => id === 'B70')?.note ?? '', /15 unit.*belum lengkap/, 'B70 harus menyatakan batas U319 dan ketidaklengkapannya.');
assert.equal(courses.find(({ id }) => id === 'C50')?.state, 'production', 'C50 harus tetap dalam produksi karena korpus analisis kompleks belum lengkap.');
assert.equal(courses.find(({ id }) => id === 'C50')?.edition, undefined, 'C50 belum memiliki pembaca Analisis Kompleks mandiri.');
assert.equal(courses.find(({ id }) => id === 'C50')?.zenodo, 'https://doi.org/10.5281/zenodo.22073827', 'C50 harus menunjuk checkpoint U319 yang memuat unit R008.');
assert.equal(courses.find(({ id }) => id === 'C50')?.repository, 'https://github.com/KokunoYumeto/lebl-mathematics-family-id', 'C50 harus menunjuk repositori keluarga Lebl.');
assert.match(courses.find(({ id }) => id === 'C50')?.note ?? '', /50 unit.*belum lengkap/, 'C50 harus menyatakan batas U319 dan ketidaklengkapannya.');
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
assert.equal(courses.find(({ id }) => id === 'D40')?.zenodo, 'https://doi.org/10.5281/zenodo.22074306', 'D40 harus menunjuk Unit 07 Zenodo yang terverifikasi.');
assert.match(courses.find(({ id }) => id === 'D40')?.note ?? '', /Unit 07.*46 halaman.*belum dipublikasikan/, 'D40 harus menyatakan batas publik dan kemajuan lokal tanpa mencampurkannya.');
assert.equal(courses.find(({ id }) => id === 'D50')?.state, 'production', 'D50 harus terpilih dan tetap ditandai sedang diproduksi sampai korpus selesai.');
assert.match(courses.find(({ id }) => id === 'D50')?.corpus ?? '', /Brenner.*jembatan.*ujian/, 'D50 harus mencatat arsitektur Brenner, jembatan asli, dan bank ujian resmi.');
assert.equal(courses.find(({ id }) => id === 'D50')?.zenodo, 'https://doi.org/10.5281/zenodo.22073928', 'D50 harus menunjuk Unit 10 Zenodo yang terverifikasi.');
assert.match(courses.find(({ id }) => id === 'D50')?.note ?? '', /Unit 10.*165 halaman.*Unit 11–12/, 'D50 harus menyatakan batas publik Unit 10 dan kemajuan lokal berikutnya.');
assert.equal(courses.find(({ id }) => id === 'D60')?.state, 'production', 'D60 harus terpilih dan ditandai sedang diproduksi sampai korpus selesai.');
assert.match(courses.find(({ id }) => id === 'D60')?.corpus ?? '', /Roberts.*Fomberg.*penutupan/, 'D60 harus mencatat arsitektur Roberts/Fomberg/penutupan asli yang dipilih.');
assert.equal(courses.find(({ id }) => id === 'D60')?.repository, 'https://github.com/KokunoYumeto/algebraic-topology-id', 'D60 harus menunjuk repositori kerja publik yang tepat.');
assert.equal(courses.find(({ id }) => id === 'D60')?.zenodo, 'https://doi.org/10.5281/zenodo.22074233', 'D60 harus menunjuk batas preservasi Zenodo Unit 24.');
assert.match(courses.find(({ id }) => id === 'D60')?.note ?? '', /Unit 25 \(298 halaman\).*Unit 24 \(286 halaman\).*Unit 26/, 'D60 harus membedakan batas GitHub/Pages, Zenodo, dan kemajuan lokal.');
assert.equal(courses.find(({ id }) => id === 'D90')?.state, 'production', 'D90 harus terpilih dan ditandai sedang diproduksi sampai korpus selesai.');
assert.match(courses.find(({ id }) => id === 'D90')?.corpus ?? '', /MIT OCW 6\.253.*Royer.*empat unit/, 'D90 harus mencatat arsitektur MIT/Royer/penutupan asli yang dipilih.');
assert.equal(courses.find(({ id }) => id === 'D100')?.state, 'production', 'D100 harus terpilih dan ditandai sedang diproduksi sampai korpus selesai.');
assert.match(courses.find(({ id }) => id === 'D100')?.corpus ?? '', /Brenner Algebraische Kurven.*Bündel, Garben und Kohomologie/, 'D100 harus mencatat dua volume Brenner yang dipilih.');
assert.equal(courses.find(({ id }) => id === 'D100')?.zenodo, 'https://doi.org/10.5281/zenodo.22070936', 'D100 harus menunjuk batas publik Unit 08.');
assert.match(courses.find(({ id }) => id === 'D100')?.note ?? '', /Unit 1–8.*161 halaman.*Unit 9.*bukan rilis publik/, 'D100 harus membedakan batas publik Unit 08 dari checkpoint internal Unit 09.');
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
  for (const field of ['edition', 'repository', 'zenodo']) {
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
assert.match(html, /property="og:image" content="https:\/\/zenodo\.org\/records\/22074701\/files\/program-matematika-indonesia-og-v0\.50\.0\.png"/, 'Kartu sosial Zenodo tidak terhubung.');
assert.match(html, /rel="canonical" href="https:\/\/doi\.org\/10\.5281\/zenodo\.22074701"/, 'URL kanonis Zenodo tidak tepat.');
assert.match(html, /40 korpus terpilih/, 'Ringkasan 40 korpus terpilih hilang.');
assert.match(html, /Produksi yang belum selesai tetap dilabeli dengan jelas/, 'Ringkasan batas produksi hilang.');
assert.match(html, /<strong>15<\/strong><span>peran dengan edisi selesai<\/span>/, 'Ringkasan lima belas peran dengan edisi selesai hilang.');
assert.match(html, /https:\/\/doi\.org\/10\.5281\/zenodo\.22074701/, 'Tautan snapshot Zenodo pusat hilang dari HTML.');
assert.match(html, /https:\/\/github\.com\/KokunoYumeto\/program-matematika-indonesia/, 'Tautan repositori GitHub pusat hilang dari HTML.');
assert.match(app, /editionIsSuspendedGithub/, 'Aplikasi harus menahan tautan repositori GitHub yang sementara tidak tersedia.');
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
  topics: topics.length,
  levelCounts,
}, null, 2));
