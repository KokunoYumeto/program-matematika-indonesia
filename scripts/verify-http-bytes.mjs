import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const baseUrl = new URL(process.argv[2] || 'http://127.0.0.1:8765/');
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'docs');
const [d20, c100] = await Promise.all([
  readFile(resolve(root, 'data/unit-route-D20-v2.1.json'), 'utf8').then(JSON.parse),
  readFile(resolve(root, 'data/unit-route-C100-v2.1.json'), 'utf8').then(JSON.parse),
]);
const names = [
  'index.html', 'styles.css', 'app.js', 'courses.js', 'og.png', 'robots.txt', '.nojekyll',
  'data/curriculum-authority-v1.json', 'data/learner-read-model.json',
  'data/educational-access.json', 'schema/educational-access-federation-v1.schema.json',
  'data/unit-route-C100-v2.1.json', 'data/unit-route-D20-v2.1.json', 'data/unit-route-v2.1.json', 'data/unit-routes-v2.1.json',
  'id-ID/courses/C100/index.html', 'id-ID/courses/C100/reader/index.html', 'id-ID/courses/C100/reader/style.css',
  'id-ID/courses/C100/solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf',
  ...Array.from({ length: 20 }, (_, index) => `id-ID/courses/C100/units/bab-${String(index + 1).padStart(2, '0')}/index.html`),
  'id-ID/courses/D20/index.html',
  ...d20.units.map(({ slug }) => `id-ID/courses/D20/units/${slug}/index.html`),
];
assert.equal(c100.units.length, 939, 'C100 public route inventory changed.');
assert.equal(d20.units.length, 17, 'D20 public route inventory changed.');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const results = [];

for (const name of names) {
  const local = await readFile(resolve(root, name));
  const response = await fetch(new URL(name === 'index.html' ? './' : name, baseUrl));
  assert.equal(response.status, 200, `${name}: HTTP ${response.status}`);
  const remote = Buffer.from(await response.arrayBuffer());
  assert.equal(remote.length, local.length, `${name}: jumlah byte publik berbeda.`);
  assert.equal(sha256(remote), sha256(local), `${name}: hash publik berbeda.`);
  results.push({ name, bytes: local.length, sha256: sha256(local) });
}

console.log(JSON.stringify({ status: 'pass', baseUrl: baseUrl.href, files: results }, null, 2));
