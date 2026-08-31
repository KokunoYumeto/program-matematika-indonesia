import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { courses as authorityCourses } from '../docs/courses.js';
import { learnerDeliveryByCourseId } from '../docs/learner-delivery.js';
import { learnerToolsByCourseId } from '../docs/learner-tools.js';
import { materializeLiveCourses } from '../docs/live-course-publications.js';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const path = resolve(project, 'docs/index.html');
const start = '<!-- STATIC-COURSE-FALLBACK:START -->';
const end = '<!-- STATIC-COURSE-FALLBACK:END -->';
const escapeHtml = (value) => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;');
const formatBytes = (bytes) => new Intl.NumberFormat('id-ID', { maximumFractionDigits: 1 }).format(bytes / 1_000_000);
const courses = materializeLiveCourses(authorityCourses);
assert.equal(courses.length, 40);

const cards = courses.map((course) => {
  const delivery = learnerDeliveryByCourseId[course.id];
  assert.ok(delivery, `${course.id}: delivery row missing.`);
  const primary = course.learner ?? course.reader ?? course.edition ?? `#course-${course.id}`;
  const prerequisites = course.prerequisites.length ? course.prerequisites.join(', ') : 'tidak ada';
  const offline = delivery.portable_html.status === 'verified'
    ? `<a href="${escapeHtml(delivery.portable_html.url)}" target="_blank" rel="noreferrer">Unduh HTML luring (${formatBytes(delivery.portable_html.bytes)} MB)</a>`
    : '<span>Belum ada paket HTML luring terverifikasi</span>';
  const tools = (learnerToolsByCourseId[course.id] ?? [])
    .filter(({ state }) => state !== 'planned')
    .map(({ href, label }) => `<a href="${escapeHtml(href)}">${escapeHtml(label)}</a>`)
    .join('');
  return `<article class="static-course-card" data-static-course-id="${course.id}"><p><b>${course.id}</b> · ${escapeHtml(course.topic)}</p><h3>${escapeHtml(course.title)}</h3><p><strong>Prasyarat:</strong> ${escapeHtml(prerequisites)}</p><div><a href="${escapeHtml(primary)}">Buka jalur belajar</a>${tools}${offline}</div></article>`;
}).join('');
const block = `${start}\n      <noscript><section class="static-catalog" aria-labelledby="static-catalog-title"><h2 id="static-catalog-title">Katalog 40 mata kuliah tanpa JavaScript</h2><p>Daftar dasar ini tetap dapat digunakan ketika skrip gagal atau dinonaktifkan. Saringan dan catatan kemajuan memerlukan JavaScript.</p><div class="static-course-grid">${cards}</div></section></noscript>\n      ${end}`;
const source = await readFile(path, 'utf8');
const pattern = new RegExp(`${start}[\\s\\S]*?${end}`);
assert.match(source, pattern, 'Static fallback markers are missing from docs/index.html.');
const output = source.replace(pattern, block);
assert.equal((output.match(/data-static-course-id=/g) ?? []).length, 40);
await writeFile(path, output, 'utf8');
console.log('Static no-JavaScript catalog generated for 40 courses.');
