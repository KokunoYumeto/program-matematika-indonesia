import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const output = resolve(process.argv[2] || '../../../outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/106_STUDENT_SITE_V058_PUBLIC_READBACK_20260826.json');
const baseUrl = new URL('https://kokunoyumeto.github.io/program-matematika-indonesia/');
const docs = resolve(project, 'docs');
const authority = JSON.parse(await readFile(resolve(project, 'backend/authority/curriculum-authority-v1.json'), 'utf8'));
const publicationReceiptPath = resolve(project, 'PUBLICATION_RECEIPT_v0.58.0.json');
const publicationReceiptBytes = await readFile(publicationReceiptPath);
const publicationReceipt = JSON.parse(publicationReceiptBytes.toString('utf8'));
const [d20, c100] = await Promise.all([
  readFile(resolve(docs, 'data/unit-route-D20-v2.1.json'), 'utf8').then(JSON.parse),
  readFile(resolve(docs, 'data/unit-route-C100-v2.1.json'), 'utf8').then(JSON.parse),
]);

assert.equal(publicationReceipt.version, '0.58.0');
assert.equal(publicationReceipt.github.pages_readback, 'pass_57_of_57_http_200_local_byte_identity');
assert.equal(publicationReceipt.zenodo.record_id, 22105611);
assert.equal(c100.units.length, 939);
assert.equal(d20.units.length, 17);

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
assert.equal(names.length, 57);

const publicByteIdentity = [];
for (const name of names) {
  const local = await readFile(resolve(docs, name));
  const url = new URL(name === 'index.html' ? './' : name, baseUrl);
  const response = await fetchWithRetry(url, name);
  const remote = Buffer.from(await response.arrayBuffer());
  assert.equal(remote.length, local.length, `${name}: public byte count differs`);
  assert.equal(sha256(remote), sha256(local), `${name}: public hash differs`);
  publicByteIdentity.push({ file: name, url: url.href, bytes: local.length, sha256: sha256(local), local_equals_public: true });
}

const externalReaderRows = [];
const seenExternal = new Set();
for (const course of authority.catalog.courses) {
  if (typeof course.reader !== 'string' || seenExternal.has(course.reader)) continue;
  seenExternal.add(course.reader);
  const response = await fetchWithRetry(course.reader, `${course.id}: reader`);
  const body = Buffer.from(await response.arrayBuffer());
  externalReaderRows.push({
    role: course.id,
    url: course.reader,
    status: 200,
    bytes: body.length,
    sha256: sha256(body),
    evidence_kind: 'fresh_anonymous_http_readback',
  });
}

const centralReaderRows = publicByteIdentity
  .filter((row) => /^id-ID\/courses\/(?:C100|D20)\/.+index\.html$/.test(row.file) || /^id-ID\/courses\/(?:C100|D20)\/index\.html$/.test(row.file))
  .map((row) => ({
    role: row.file.includes('/C100/') ? 'C100' : 'D20',
    url: row.url.replace(/index\.html$/, ''),
    status: 200,
    bytes: row.bytes,
    sha256: row.sha256,
    evidence_kind: 'local_public_byte_identity',
  }));

const totalBytes = publicByteIdentity.reduce((sum, row) => sum + row.bytes, 0);
const aggregate = sha256(Buffer.from(publicByteIdentity
  .map((row) => `${row.sha256}  ${row.file}`)
  .sort()
  .join('\n') + '\n', 'utf8'));
const root = publicByteIdentity.find((row) => row.file === 'index.html');
assert.ok(root);

const receipt = {
  schema_id: 'program-matematika-indonesia/student-html-hub-public-readback/v3',
  recorded_at: new Date().toISOString(),
  manager_thread_id: '01a01ec1-e685-70d0-b022-211396334723',
  program_version: '0.58.0',
  result: 'pass',
  scope: 'Fresh anonymous HTTP 200 and byte-identity verification of the complete v0.58 learner-site inventory, including materialized C100 and D20 central routes, plus fresh HTTP readback of every catalog-declared external HTML reader.',
  central_public_site: {
    url: baseUrl.href,
    http_status: 200,
    bytes: root.bytes,
    sha256: root.sha256,
    content_classification: 'student-facing HTML landing page',
    not_json_dump: true,
    zenodo_link: 'https://doi.org/10.5281/zenodo.22105611',
  },
  public_byte_identity: publicByteIdentity,
  public_byte_identity_summary: { files: publicByteIdentity.length, bytes: totalBytes, aggregate_sha256: aggregate },
  public_html_readers: [...externalReaderRows, ...centralReaderRows],
  route_coverage: {
    C100: { stable_units: 939, chapter_wrappers: 20, course_root: `${baseUrl.href}id-ID/courses/C100/`, semantic_reader: `${baseUrl.href}id-ID/courses/C100/reader/` },
    D20: { stable_units: 17, chapter_wrappers: 17, course_root: `${baseUrl.href}id-ID/courses/D20/` },
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
    path: 'PUBLICATION_RECEIPT_v0.58.0.json',
    bytes: publicationReceiptBytes.length,
    sha256: sha256(publicationReceiptBytes),
  },
  conclusion: 'All 57 learner-site files are byte-identical in public readback; every catalog-declared external HTML reader returns HTTP 200; the public entry is a learner-facing application while JSON and backend packages remain secondary machine surfaces.',
};

await mkdir(dirname(output), { recursive: true });
const bytes = canonical(receipt);
await writeFile(output, bytes);
console.log(JSON.stringify({ output, bytes: bytes.length, sha256: sha256(bytes), files: publicByteIdentity.length, public_html_readers: receipt.public_html_readers.length }, null, 2));
