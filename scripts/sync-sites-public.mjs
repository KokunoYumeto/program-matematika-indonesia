import assert from 'node:assert/strict';
import { cp, mkdir, readFile, rm } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, resolve, sep } from 'node:path';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const source = resolve(project, 'docs');
const publicRoot = resolve(project, 'public');
const target = resolve(publicRoot, 'hub');
assert.ok(target.startsWith(`${publicRoot}${sep}`), 'Target sinkronisasi keluar dari public/.');

await rm(target, { recursive: true, force: true });
await mkdir(target, { recursive: true });
await cp(source, target, {
  recursive: true,
  filter: (path) => !path.endsWith(`${sep}.nojekyll`),
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
]) {
  const [left, right] = await Promise.all([
    readFile(resolve(source, name)),
    readFile(resolve(target, name)),
  ]);
  assert.equal(right.length, left.length, `${name}: jumlah byte sinkron berbeda.`);
  assert.equal(sha256(right), sha256(left), `${name}: hash sinkron berbeda.`);
}

console.log('Static hub synchronized to public/hub with exact bytes.');
