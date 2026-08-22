import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { courses, topics } from '../docs/courses.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const html = await readFile(resolve(root, 'docs/index.html'), 'utf8');

const expectedIds = [
  'A00', 'A10', 'A20', 'A30',
  'B10', 'B20', 'B30', 'B40', 'B50', 'B60', 'B70', 'B80', 'B90', 'B95',
  'C10', 'C20', 'C30', 'C40', 'C50', 'C60', 'C70', 'C80', 'C90', 'C100', 'C110', 'C120', 'C130', 'C140',
  'D10', 'D20', 'D30', 'D40', 'D50', 'D60', 'D70', 'D80', 'D90', 'D100', 'D110', 'D120',
];
const unresolvedIds = ['B80', 'D30', 'D40', 'D50', 'D60', 'D90', 'D100', 'D120'];
const publishedIds = ['B10', 'B90', 'C30', 'C40', 'C80'];
const levelCounts = { A: 4, B: 10, C: 14, D: 12 };
const allowedStates = new Set(['published', 'near', 'production', 'unresolved']);

assert.equal(courses.length, 40, 'Katalog harus memuat tepat 40 mata kuliah.');
assert.deepEqual(courses.map(({ id }) => id), expectedIds, 'Urutan atau identitas kode mata kuliah berubah.');
assert.equal(new Set(courses.map(({ id }) => id)).size, 40, 'Kode mata kuliah harus unik.');
assert.deepEqual(courses.filter(({ state }) => state === 'unresolved').map(({ id }) => id), unresolvedIds, 'Daftar delapan peran yang belum dibekukan berubah.');
assert.deepEqual(courses.filter(({ state }) => state === 'published').map(({ id }) => id), publishedIds, 'Daftar lima peran dengan edisi publik selesai berubah.');

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
  for (const field of ['edition', 'zenodo']) {
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
assert.match(html, /property="og:image" content="https:\/\/kokunoyumeto\.github\.io\/program-matematika-indonesia\/og\.png"/, 'Kartu sosial publik tidak terhubung.');
assert.match(html, /rel="canonical" href="https:\/\/kokunoyumeto\.github\.io\/program-matematika-indonesia\/"/, 'URL kanonis tidak tepat.');
assert.match(html, /32 korpus terpilih/, 'Ringkasan 32 korpus terpilih hilang.');
assert.match(html, /Delapan peran/, 'Ringkasan delapan peran terbuka hilang.');

const blankTargets = [...html.matchAll(/<a\b[^>]*target="_blank"[^>]*>/g)].map(([tag]) => tag);
for (const tag of blankTargets) assert.match(tag, /rel="[^"]*noreferrer[^"]*"/, `Tautan tab baru tanpa rel=noreferrer: ${tag}`);

console.log(JSON.stringify({
  status: 'pass',
  courses: courses.length,
  selected: courses.filter(({ state }) => state !== 'unresolved').length,
  unresolved: unresolvedIds.length,
  published: publishedIds.length,
  topics: topics.length,
  levelCounts,
}, null, 2));
