import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, relative, resolve, sep } from 'node:path';

function option(name) {
  const index = process.argv.indexOf(name);
  assert.ok(index !== -1 && process.argv[index + 1], `Missing required option ${name}.`);
  return process.argv[index + 1];
}

const root = resolve(option('--root'));
const baseUrl = new URL(option('--base-url'));
const output = resolve(option('--output'));
const sourceCommit = option('--source-commit');
const recordedAt = option('--recorded-at');

assert.match(sourceCommit, /^[0-9a-f]{40}$/, 'Source commit must be a lowercase Git SHA-1.');
assert.ok(!Number.isNaN(Date.parse(recordedAt)), 'Recorded-at must be an ISO-8601 timestamp.');
assert.equal(baseUrl.protocol, 'https:', 'Public base URL must use HTTPS.');

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');

async function listFiles(directory) {
  const files = [];
  async function walk(current) {
    const entries = await readdir(current, { withFileTypes: true });
    entries.sort((left, right) => left.name.localeCompare(right.name, 'en'));
    for (const entry of entries) {
      const path = resolve(current, entry.name);
      if (entry.isDirectory()) await walk(path);
      else if (entry.isFile()) files.push(path);
    }
  }
  await walk(directory);
  return files;
}

const inventory = [];
for (const path of await listFiles(root)) {
  const portable = relative(root, path).split(sep).join('/');
  const local = await readFile(path);
  const url = new URL(portable, baseUrl);
  const response = await fetch(url, { redirect: 'follow' });
  assert.equal(response.status, 200, `${portable}: public HTTP status ${response.status}.`);
  const remote = Buffer.from(await response.arrayBuffer());
  assert.equal(remote.length, local.length, `${portable}: public byte count differs.`);
  assert.equal(sha256(remote), sha256(local), `${portable}: public SHA-256 differs.`);
  inventory.push({
    path: portable,
    url: url.href,
    http_status: response.status,
    bytes: local.length,
    sha256: sha256(local),
    content_type: response.headers.get('content-type'),
  });
}

assert.ok(inventory.length > 0, 'Public directory inventory is empty.');
const digestLines = inventory
  .map((row) => `${row.sha256}  ${row.bytes}  ${row.path}\n`)
  .join('');
const receipt = {
  schema_id: 'program-matematika-indonesia/public-directory-readback/v1',
  result: 'pass',
  recorded_at: new Date(recordedAt).toISOString(),
  source: {
    root,
    git_commit: sourceCommit,
  },
  public_route: baseUrl.href,
  totals: {
    files: inventory.length,
    bytes: inventory.reduce((total, row) => total + row.bytes, 0),
    inventory_digest_sha256: sha256(Buffer.from(digestLines, 'utf8')),
  },
  index: inventory.find((row) => row.path === 'index.html') ?? null,
  inventory,
};
assert.ok(receipt.index, 'Public directory has no index.html.');

await mkdir(dirname(output), { recursive: true });
const bytes = canonical(receipt);
await writeFile(output, bytes);
console.log(JSON.stringify({
  result: receipt.result,
  output,
  bytes: bytes.length,
  sha256: sha256(bytes),
  files: receipt.totals.files,
  public_route: receipt.public_route,
}, null, 2));
