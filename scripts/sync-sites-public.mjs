import assert from 'node:assert/strict';
import { cp, mkdir, readFile, rm } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, relative, resolve, sep } from 'node:path';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const source = resolve(project, 'docs');
const publicRoot = resolve(project, 'public');
const target = resolve(publicRoot, 'hub');
assert.ok(target.startsWith(`${publicRoot}${sep}`), 'Target sinkronisasi keluar dari public/.');

await rm(target, { recursive: true, force: true });
await mkdir(target, { recursive: true });
const approvedTopLevelFiles = new Set([
  'app.js',
  'courses.js',
  'index.html',
  'og.png',
  'robots.txt',
  'styles.css',
]);
const approvedDataFiles = new Set([
  'data/curriculum-authority-v1.json',
  'data/learner-read-model.json',
  'data/unit-route-v2.1.json',
]);
await cp(source, target, {
  recursive: true,
  filter: (path) => {
    if (path === source) return true;
    const name = relative(source, path).split(sep).join('/');
    if (name === 'data' || name === 'schema' || name.startsWith('schema/')) return true;
    // Preserve central learner route wrappers for the hosted mirror.  These
    // pages contain navigation and links only; owner-native prose remains on
    // the canonical course reader.
    if (name === 'id-ID' || name.startsWith('id-ID/')) return true;
    return approvedTopLevelFiles.has(name) || approvedDataFiles.has(name);
  },
});

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
for (const name of [
  'index.html',
  'styles.css',
  'app.js',
  'courses.js',
  'data/curriculum-authority-v1.json',
  'data/learner-read-model.json',
  'schema/v1/curriculum-authority-v1.schema.json',
  'schema/v1/learner-read-model-v1.schema.json',
  'schema/v2/federation-package-v2.schema.json',
  'schema/v2/federation-record-v2.schema.json',
  'og.png',
  'robots.txt',
  'id-ID/courses/D20/index.html',
  'id-ID/courses/D20/units/bab-01/index.html',
  'id-ID/courses/D20/units/bab-17/index.html',
  'data/unit-route-v2.1.json',
]) {
  const [left, right] = await Promise.all([
    readFile(resolve(source, name)),
    readFile(resolve(target, name)),
  ]);
  assert.equal(right.length, left.length, `${name}: jumlah byte sinkron berbeda.`);
  assert.equal(sha256(right), sha256(left), `${name}: hash sinkron berbeda.`);
}

console.log('Static hub synchronized to public/hub with exact bytes.');
