import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const baseUrl = new URL(process.argv[2] || 'http://127.0.0.1:8765/');
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'docs');
const names = ['index.html', 'styles.css', 'app.js', 'courses.js', 'og.png', 'robots.txt', '.nojekyll'];
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
