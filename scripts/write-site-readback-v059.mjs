import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const coordinator = resolve(project, '../../../outputs/01a01ec1-e685-70d0-b022-211396334723');
const output = resolve(
  process.argv[2]
    || resolve(coordinator, 'curriculum_logbook/116_STUDENT_SITE_V059_PUBLIC_READBACK_20260827.json'),
);
const baseUrl = new URL('https://kokunoyumeto.github.io/program-matematika-indonesia/');
const docs = resolve(project, 'docs');
const authorityPath = resolve(project, 'backend/authority/curriculum-authority-v1.json');
const publicationReceiptPath = resolve(project, 'PUBLICATION_RECEIPT_v0.59.0.json');
const ownerReadbackPath = resolve(
  coordinator,
  'curriculum_logbook/114_PUBLIC_OWNER_HTML_ROUTE_READBACK_20260827.json',
);

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
const delay = (milliseconds) => new Promise((resolveDelay) => setTimeout(resolveDelay, milliseconds));

async function filesUnder(root) {
  const outputFiles = [];
  async function visit(directory) {
    const entries = await readdir(directory, { withFileTypes: true });
    for (const entry of entries.sort((left, right) => left.name.localeCompare(right.name))) {
      const path = resolve(directory, entry.name);
      if (entry.isDirectory()) await visit(path);
      else if (entry.isFile()) outputFiles.push(relative(root, path).split(sep).join('/'));
      else throw new Error(`Unsupported docs entry type: ${path}`);
    }
  }
  await visit(root);
  return outputFiles.sort();
}

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

const [authorityBytes, publicationReceiptBytes, ownerReadbackBytes] = await Promise.all([
  readFile(authorityPath),
  readFile(publicationReceiptPath),
  readFile(ownerReadbackPath),
]);
const authority = JSON.parse(authorityBytes.toString('utf8'));
const publicationReceipt = JSON.parse(publicationReceiptBytes.toString('utf8'));
const ownerReadback = JSON.parse(ownerReadbackBytes.toString('utf8'));

assert.equal(authority.catalog.program.version, '0.59.0');
assert.equal(publicationReceipt.version, '0.59.0');
assert.equal(publicationReceipt.zenodo.record_id, 22133203);
assert.match(publicationReceipt.github.pages_readback, /^pass_/);
assert.equal(ownerReadback.result, 'pass');
assert.equal(ownerReadback.route_count, 6);

const names = await filesUnder(docs);
assert.ok(names.includes('index.html'));
assert.ok(names.includes('data/curriculum-authority-v1.json'));
assert.ok(names.includes('data/learner-read-model.json'));

const publicByteIdentity = [];
for (const name of names) {
  const local = await readFile(resolve(docs, name));
  const url = new URL(name === 'index.html' ? './' : name, baseUrl);
  const response = await fetchWithRetry(url, name);
  const remote = Buffer.from(await response.arrayBuffer());
  assert.equal(remote.length, local.length, `${name}: public byte count differs`);
  assert.equal(sha256(remote), sha256(local), `${name}: public hash differs`);
  publicByteIdentity.push({
    file: name,
    url: url.href,
    bytes: local.length,
    sha256: sha256(local),
    local_equals_public: true,
  });
}

const pinnedOwnerRoutes = new Map(ownerReadback.routes.map((row) => [row.course_id, row]));
const publicHtmlReaders = [];
const seenReaders = new Set();
for (const course of authority.catalog.courses) {
  if (typeof course.reader !== 'string' || seenReaders.has(course.reader)) continue;
  seenReaders.add(course.reader);
  assert.ok(course.reader.startsWith('https://'), `${course.id}: reader must use HTTPS`);
  assert.ok(!course.reader.toLowerCase().endsWith('.json'), `${course.id}: reader may not be JSON`);
  const response = await fetchWithRetry(course.reader, `${course.id}: reader`);
  const body = Buffer.from(await response.arrayBuffer());
  const contentType = response.headers.get('content-type') || '';
  assert.ok(contentType.toLowerCase().includes('text/html'), `${course.id}: reader is not HTML`);
  const row = {
    role: course.id,
    url: course.reader,
    status: 200,
    bytes: body.length,
    sha256: sha256(body),
    content_type: contentType,
    evidence_kind: 'fresh_anonymous_http_readback',
  };
  const pinned = pinnedOwnerRoutes.get(course.id);
  if (pinned) {
    assert.equal(row.url, pinned.url, `${course.id}: current reader differs from pinned owner route`);
    assert.equal(row.bytes, pinned.bytes, `${course.id}: owner reader byte count differs`);
    assert.equal(row.sha256, pinned.sha256, `${course.id}: owner reader hash differs`);
    row.pinned_owner_readback_match = true;
  }
  publicHtmlReaders.push(row);
}
assert.deepEqual(
  [...pinnedOwnerRoutes.keys()].sort(),
  publicHtmlReaders.filter((row) => row.pinned_owner_readback_match).map((row) => row.role).sort(),
);

const totalBytes = publicByteIdentity.reduce((sum, row) => sum + row.bytes, 0);
const aggregate = sha256(Buffer.from(
  `${publicByteIdentity.map((row) => `${row.sha256}  ${row.file}`).sort().join('\n')}\n`,
  'utf8',
));
const root = publicByteIdentity.find((row) => row.file === 'index.html');
assert.ok(root);

const receipt = {
  schema_id: 'program-matematika-indonesia/student-html-hub-public-readback/v4',
  recorded_at: new Date().toISOString(),
  manager_thread_id: '01a01ec1-e685-70d0-b022-211396334723',
  program_version: '0.59.0',
  result: 'pass',
  scope: 'Fresh anonymous HTTP 200 and exact local/public byte identity for the complete generated learner site, plus fresh HTML readback of every catalog reader and exact replay of the six pinned v0.59 owner routes.',
  central_public_site: {
    url: baseUrl.href,
    http_status: 200,
    bytes: root.bytes,
    sha256: root.sha256,
    content_classification: 'student-facing HTML landing page',
    not_json_dump: true,
    zenodo_link: 'https://doi.org/10.5281/zenodo.22133203',
  },
  public_byte_identity: publicByteIdentity,
  public_byte_identity_summary: {
    files: publicByteIdentity.length,
    bytes: totalBytes,
    aggregate_sha256: aggregate,
  },
  public_html_readers: publicHtmlReaders,
  owner_reader_pin: {
    path: 'curriculum_logbook/114_PUBLIC_OWNER_HTML_ROUTE_READBACK_20260827.json',
    bytes: ownerReadbackBytes.length,
    sha256: sha256(ownerReadbackBytes),
    exact_routes_replayed: ownerReadback.route_count,
  },
  zenodo_preservation: {
    record_url: publicationReceipt.zenodo.public_record,
    doi: publicationReceipt.zenodo.version_doi,
    concept_doi: publicationReceipt.zenodo.concept_doi,
    published: publicationReceipt.zenodo.publication_date,
    version: publicationReceipt.zenodo.version,
    file_count: publicationReceipt.zenodo.file_count,
    total_bytes: publicationReceipt.zenodo.total_bytes,
    anonymous_readback: publicationReceipt.zenodo.anonymous_filename_size_sha256_readback,
    description_first_href: publicationReceipt.zenodo.description_first_href,
  },
  source_publication_receipt: {
    path: 'PUBLICATION_RECEIPT_v0.59.0.json',
    bytes: publicationReceiptBytes.length,
    sha256: sha256(publicationReceiptBytes),
  },
  source_authority: {
    path: 'backend/authority/curriculum-authority-v1.json',
    bytes: authorityBytes.length,
    sha256: sha256(authorityBytes),
  },
  conclusion: 'The public entry is a learner-facing application; every declared reader is public HTML; JSON, schema, source, and backend packages remain secondary machine surfaces.',
};

await mkdir(dirname(output), { recursive: true });
const bytes = canonical(receipt);
await writeFile(output, bytes);
console.log(JSON.stringify({
  output,
  bytes: bytes.length,
  sha256: sha256(bytes),
  files: publicByteIdentity.length,
  public_html_readers: publicHtmlReaders.length,
  pinned_owner_routes: ownerReadback.route_count,
}, null, 2));
