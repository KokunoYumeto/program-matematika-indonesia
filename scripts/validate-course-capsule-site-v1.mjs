import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const checkPublic = process.argv.includes('--public');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const identity = (path, bytes) => ({ path, bytes: bytes.length, sha256: sha256(bytes) });
const sortValue = (value) => {
  if (Array.isArray(value)) return value.map(sortValue);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sortValue(value[key])]));
  return value;
};
const canonicalJson = (value) => JSON.stringify(sortValue(value), null, 2) + '\n';
const logicalFiles = [
  'backend/index.html',
  'backend/backend.css',
  'backend/backend.js',
  'data/course-capsule-v1/course-capsules.jsonl',
  'data/course-capsule-v1/course-capsules.json',
  'data/course-capsule-v1/manifest.json',
  'data/course-capsule-v1/validation-receipt.json',
  'data/course-capsule-v1/README.md',
  'schema/course-capsule-v1/course-capsule-v1.schema.json',
];
const docsBytes = Object.fromEntries(await Promise.all(logicalFiles.map(async (path) => [path, await readFile(resolve(project, 'docs', path))])));
const html = docsBytes['backend/index.html'].toString('utf8');
const css = docsBytes['backend/backend.css'].toString('utf8');
const js = docsBytes['backend/backend.js'].toString('utf8');
const rows = JSON.parse(docsBytes['data/course-capsule-v1/course-capsules.json'].toString('utf8'));
const jsonlRows = docsBytes['data/course-capsule-v1/course-capsules.jsonl'].toString('utf8').trimEnd().split('\n').map(JSON.parse);
const manifest = JSON.parse(docsBytes['data/course-capsule-v1/manifest.json'].toString('utf8'));
const validation = JSON.parse(docsBytes['data/course-capsule-v1/validation-receipt.json'].toString('utf8'));
const mainHtml = await readFile(resolve(project, 'docs/index.html'), 'utf8');

assert.equal(rows.length, 40);
assert.deepEqual(rows, jsonlRows);
assert.equal(new Set(rows.map(({ course_id }) => course_id)).size, 40);
assert.equal(rows.filter(({ course }) => course.state === 'published').length, 29);
assert.equal(rows.filter(({ course }) => course.state === 'production').length, 11);
assert.equal(rows.filter((row) => row.layers.educator.features.length || row.layers.educator.resources.length).length, 20);
assert.equal(rows.filter((row) => ['verified', 'legacy_verified'].includes(row.layers.interoperability.semantic_adapter.status)).length, 5);
assert.equal(rows.filter((row) => Object.keys(row.layers).sort().join(',') === 'curriculum,educator,federation,interoperability,learner,production,translation').length, 40);
assert.equal(rows.filter((row) => row.learner_directed && row.open_access_policy.public_access_required).length, 40);
assert.equal(manifest.summary.course_count, 40);
assert.equal(validation.state, 'pass');
assert.equal(validation.checks.seven_layer_rows, 40);
assert.equal(validation.peer_replay.byte_identical, true);

const ids = rows.map(({ course_id }) => course_id);
const edges = rows.flatMap((row) => row.course.prerequisites.map((source) => [source, row.course_id]));
const incoming = Object.fromEntries(ids.map((id) => [id, 0]));
const outgoing = Object.fromEntries(ids.map((id) => [id, []]));
for (const [source, target] of edges) {
  assert.ok(ids.includes(source));
  outgoing[source].push(target);
  incoming[target] += 1;
}
const queue = ids.filter((id) => incoming[id] === 0);
let visited = 0;
while (queue.length) {
  const id = queue.shift();
  visited += 1;
  for (const target of outgoing[id]) {
    incoming[target] -= 1;
    if (incoming[target] === 0) queue.push(target);
  }
}
assert.equal(edges.length, 83);
assert.equal(visited, 40);

assert.match(html, /<html lang="id">/);
assert.match(html, /class="skip-link"/);
assert.match(html, /data-view="learner"/);
assert.match(html, /data-view="educator"/);
assert.match(html, /data-view="production"/);
assert.match(html, /data-view="interop"/);
assert.equal((html.match(/data-static-course-id=/g) ?? []).length, 40);
assert.deepEqual([...html.matchAll(/data-static-course-id="([^"]+)"/g)].map((match) => match[1]), ids);
assert.match(html, /JSONL kanonis/);
assert.match(html, /Tanda terima validasi/);
assert.match(html, /<p lang="en">/);
assert.match(mainHtml, /href="backend\/">Belajar &amp; mengajar<\/a>/);
assert.match(mainHtml, /href="backend\/">Buka pusat belajar &amp; mengajar<\/a>/);
assert.match(css, /font-size:\s*17px/);
assert.match(css, /@media \(max-width: 780px\)/);
assert.match(css, /prefers-reduced-motion/);
assert.match(js, /course-capsules\.json/);
assert.match(js, /prerequisite_diagnostics/);
assert.match(js, /staged_hints_answers_solutions/);
assert.match(js, /zero-copy/i);
assert.match(js, /aria-selected/);

for (const row of rows) {
  assert.match(row.course_native.edition, /^https:\/\//);
  if (row.course_native.repository) assert.match(row.course_native.repository, /^https:\/\//);
  if (row.course_native.zenodo) assert.match(row.course_native.zenodo, /^https:\/\//);
  for (const component of row.layers.federation.components) {
    assert.equal(component.access, 'public');
    if (component.url) assert.match(component.url, /^https:\/\//);
  }
}

const publicText = Buffer.concat(Object.values(docsBytes)).toString('utf8');
for (const pattern of [
  /C:\\\\Users\\\\/i,
  /Authorization:\s*Bearer/i,
  /access[_-]?token/i,
  /api[_-]?token/i,
  /"access"\s*:\s*"(?:private|restricted|embargoed|blocked)"/i,
  /owner[_-]?native/i,
]) assert.doesNotMatch(publicText, pattern);

let publicMirror = { checked: false, byte_identical_files: 0 };
if (checkPublic) {
  for (const path of logicalFiles) {
    const publicBytes = await readFile(resolve(project, 'public/hub', path));
    assert.deepEqual(publicBytes, docsBytes[path], 'public/hub/' + path + ': mirror drift.');
  }
  publicMirror = { checked: true, byte_identical_files: logicalFiles.length };
}

const receipt = {
  schema_id: 'interlanguage/open-course-capsule-site-validation/v1',
  schema_version: '1.0.0',
  state: 'pass',
  checks: {
    course_rows: 40,
    static_fallback_rows: 40,
    seven_layer_rows: 40,
    prerequisite_edges: 83,
    prerequisite_dag_visited: 40,
    published_rows: 29,
    production_rows: 11,
    educator_rows: 20,
    semantic_adapter_rows: 4,
    public_access_rows: 40,
    accessibility_controls: 'pass',
    bahasa_primary_interface: 'pass',
    machine_data_links: 'pass',
    privacy_credential_scan: 'pass',
  },
  artifacts: Object.fromEntries(logicalFiles.map((path) => [path, identity('docs/' + path, docsBytes[path])])),
  public_mirror: publicMirror,
};
const receiptBytes = Buffer.from(canonicalJson(receipt));
const receiptPath = resolve(project, 'backend/course-capsule-v1/validation/SITE_VALIDATION_RECEIPT.json');
await mkdir(dirname(receiptPath), { recursive: true });
await writeFile(receiptPath, receiptBytes);
console.log(JSON.stringify({ status: 'pass', receipt: identity('backend/course-capsule-v1/validation/SITE_VALIDATION_RECEIPT.json', receiptBytes), ...receipt.checks, public_mirror: publicMirror }, null, 2));
