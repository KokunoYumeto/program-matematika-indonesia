import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const coordinator = resolve(project, '../../../outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook');
const output = resolve(process.argv[2] || resolve(coordinator, '120_CENTRAL_ROUTE_WRAPPERS_PUBLIC_READBACK_20260828.json'));
const baseUrl = new URL('https://kokunoyumeto.github.io/program-matematika-indonesia/');
const docs = resolve(project, 'docs');
const authorityPath = resolve(project, 'backend/authority/curriculum-authority-v1.json');
const predecessorReaderPath = resolve(coordinator, '116_STUDENT_SITE_V059_PUBLIC_READBACK_20260827.json');

const wrapperRoutes = Object.freeze([
  { role: 'PROGRAM', file: 'index.html', url: baseUrl.href },
  { role: 'C100', file: 'id-ID/courses/C100/index.html', url: new URL('id-ID/courses/C100/', baseUrl).href },
  { role: 'D20', file: 'id-ID/courses/D20/index.html', url: new URL('id-ID/courses/D20/', baseUrl).href },
]);

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
const delay = (milliseconds) => new Promise((resolveDelay) => setTimeout(resolveDelay, milliseconds));

async function fetchWithRetry(url, label) {
  let response;
  for (let attempt = 1; attempt <= 5; attempt += 1) {
    response = await fetch(url, { cache: 'no-store' });
    if (response.status === 200) return response;
    await response.arrayBuffer();
    if (![429, 500, 502, 503, 504].includes(response.status) || attempt === 5) break;
    await delay(attempt * 750);
  }
  assert.equal(response?.status, 200, `${label}: HTTP ${response?.status ?? 'no response'}`);
  return response;
}

const [authorityBytes, predecessorReaderBytes] = await Promise.all([
  readFile(authorityPath),
  readFile(predecessorReaderPath),
]);
const authority = JSON.parse(authorityBytes.toString('utf8'));
const predecessorReader = JSON.parse(predecessorReaderBytes.toString('utf8'));
assert.equal(authority.catalog.program.version, '0.59.0');
assert.equal(predecessorReader.result, 'pass');
const predecessorPins = new Map(predecessorReader.public_html_readers.map((row) => [row.url, row]));

const routeMap = new Map(wrapperRoutes.map((row) => [row.url, row]));
for (const course of authority.catalog.courses) {
  if (typeof course.reader !== 'string' || routeMap.has(course.reader)) continue;
  const url = new URL(course.reader);
  let file = null;
  if (url.origin === baseUrl.origin && url.pathname.startsWith(baseUrl.pathname)) {
    const relativePath = url.pathname.slice(baseUrl.pathname.length);
    file = relativePath.endsWith('/') ? `${relativePath}index.html` : relativePath;
  }
  routeMap.set(course.reader, { role: course.id, file, url: course.reader });
}
const routes = [...routeMap.values()];

const rows = [];
for (const route of routes) {
  const response = await fetchWithRetry(route.url, route.file);
  const remote = Buffer.from(await response.arrayBuffer());
  const contentType = response.headers.get('content-type') || '';
  assert.ok(contentType.toLowerCase().includes('text/html'), `${route.file}: not HTML`);
  const row = {
    role: route.role,
    file: route.file,
    url: route.url,
    status: 200,
    bytes: remote.length,
    sha256: sha256(remote),
    content_type: contentType,
    evidence_kind: 'fresh_anonymous_http_readback',
  };
  if (route.file) {
    const local = await readFile(resolve(docs, route.file));
    assert.equal(remote.length, local.length, `${route.file}: public byte count differs`);
    assert.equal(sha256(remote), sha256(local), `${route.file}: public hash differs`);
    row.local_equals_public = true;
    row.evidence_kind = 'fresh_anonymous_http_exact_byte_readback';
  }
  const pinned = predecessorPins.get(route.url);
  if (pinned) {
    assert.equal(row.bytes, pinned.bytes, `${route.role}: predecessor reader byte count differs`);
    assert.equal(row.sha256, pinned.sha256, `${route.role}: predecessor reader hash differs`);
    row.predecessor_readback_match = true;
  }
  rows.push(row);
}

const receipt = {
  ...predecessorReader,
  schema_id: 'program-matematika-indonesia/student-html-hub-route-wrapper-readback/v1',
  recorded_at: new Date().toISOString(),
  program_version: authority.catalog.program.version,
  result: 'pass',
  scope: 'Current learner-facing program root, every catalog HTML reader, and both materialized central course-wrapper roots; central files have exact local/public byte identity and prior-reader bytes are replayed where applicable.',
  central_public_site: rows[0],
  public_html_readers: rows.slice(1),
  route_count: rows.length,
  total_bytes: rows.reduce((sum, row) => sum + row.bytes, 0),
  aggregate_sha256: sha256(Buffer.from(rows.map((row) => `${row.sha256}  ${row.file}\n`).join(''), 'utf8')),
  source_authority: {
    path: 'backend/authority/curriculum-authority-v1.json',
    bytes: authorityBytes.length,
    sha256: sha256(authorityBytes),
  },
  predecessor_reader_pin: {
    path: '116_STUDENT_SITE_V059_PUBLIC_READBACK_20260827.json',
    bytes: predecessorReaderBytes.length,
    sha256: sha256(predecessorReaderBytes),
    matched_routes: rows.filter((row) => row.predecessor_readback_match).length,
  },
  credentials_recorded: false,
};

await mkdir(dirname(output), { recursive: true });
const bytes = canonical(receipt);
await writeFile(output, bytes);
console.log(JSON.stringify({ output, bytes: bytes.length, sha256: sha256(bytes), routes: rows.length }, null, 2));
