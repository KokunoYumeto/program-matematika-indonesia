import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const workspace = resolve(project, '../../..');
const logbook = resolve(workspace, 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook');

const predecessorReaderIdentity = Object.freeze({
  path: resolve(logbook, '119_PUBLIC_OWNER_HTML_ROUTE_READBACK_20260828.json'),
  bytes: 3788,
  sha256: 'db5c8afdcda4003b841b657635db2ecd3f8859eb5c1efc52cb2607051376ddec',
});
const d60ReceiptIdentity = Object.freeze({
  path: resolve(workspace, '04_mirrors/id/algebraic-topology-id/00_control/GITHUB_PUBLICATION_RECEIPT_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02.json'),
  bytes: 31229,
  sha256: 'c6ccde700267a29dfb2246cb4f5a78428547c75709ac60a56c9a222c84865a80',
});
const admissionPath = resolve(logbook, '130_CENTRAL_V061_ADMISSION_MANIFEST_20260828.json');
const ownerReaderPath = resolve(logbook, '131_PUBLIC_OWNER_HTML_ROUTE_READBACK_20260828.json');

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');

function option(name) {
  const index = process.argv.indexOf(name);
  assert.ok(index !== -1 && process.argv[index + 1], `Missing required option ${name}.`);
  return process.argv[index + 1];
}

async function loadBoundJson(identity, label) {
  const bytes = await readFile(identity.path);
  assert.equal(bytes.length, identity.bytes, `${label} byte count changed.`);
  assert.equal(sha256(bytes), identity.sha256, `${label} SHA-256 changed.`);
  return JSON.parse(bytes.toString('utf8'));
}

const recordedAt = new Date(option('--recorded-at')).toISOString();
const [predecessorReaders, d60Receipt] = await Promise.all([
  loadBoundJson(predecessorReaderIdentity, 'v0.60 owner-reader evidence'),
  loadBoundJson(d60ReceiptIdentity, 'D60 owner publication receipt'),
]);

assert.equal(predecessorReaders.result, 'pass');
assert.equal(predecessorReaders.route_count, 7);
assert.equal(d60Receipt.status, 'PASS_PUSHED_DEPLOYED_AND_ANONYMOUSLY_BYTE_VERIFIED');
assert.equal(d60Receipt.content_commit, '8989fbd602f89d0a8d6c30bc7bac1980a74b2c99');
assert.equal(d60Receipt.publication_truth.total_required_mastery, '108/108');
assert.equal(d60Receipt.publication_truth.computation_laboratories, '2/4');
assert.equal(d60Receipt.publication_truth.course_complete, false);
assert.equal(d60Receipt.sibling_zenodo_checkpoint.record_id, 22147224);
assert.equal(d60Receipt.sibling_zenodo_checkpoint.publication_receipt_status, 'PUBLISHED_AND_TWICE_ANONYMOUSLY_VERIFIED');

const reader = d60Receipt.reader_anonymous_readback.find((row) => row.surface === 'GitHub Pages');
assert.ok(reader);
assert.deepEqual(
  { status: reader.http_status, bytes: reader.bytes, sha256: reader.sha256 },
  {
    status: 200,
    bytes: 15615104,
    sha256: 'd0c6afddfa92759d475258bf08f20ea4019eccf72b7554128b2b938bd247b375',
  },
);

const admission = {
  schema_id: 'program-matematika-indonesia/central-release-admission-manifest/v1',
  target_release: '0.61.0',
  recorded_at: recordedAt,
  predecessor: {
    version: '0.60.0',
    authority_bytes: 75653,
    authority_sha256: '974749cf2890dc841d933e07ce453a09fdc5746a07383d61d48d178f8ed38a73',
    git_commit: '6f9755be9c41380a250fbdf2d1cd342c5c111176',
  },
  inputs: [
    {
      path: relative(workspace, d60ReceiptIdentity.path).replaceAll('\\', '/'),
      bytes: d60ReceiptIdentity.bytes,
      sha256: d60ReceiptIdentity.sha256,
      role: 'canonical_owner_publication_and_anonymous_readback_receipt',
    },
  ],
  admissions: [
    {
      course_id: 'D60',
      decision: 'refresh_partial_primary_route_to_mastery_complete_two_lab_checkpoint',
      state_after: 'production',
      predecessor_record: 22106133,
      record: 22147224,
      concept_record: 22061489,
      doi: '10.5281/zenodo.22147224',
      version: '0.31.4',
      access_right: 'open',
      license: 'other-open-mixed-source-components',
      learner_route: reader.url,
      bytes: reader.bytes,
      sha256: reader.sha256,
      content_type: 'text/html',
      primary_artifact: {
        path: 'TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_READER.html',
        format: 'html',
        bytes: reader.bytes,
        sha256: reader.sha256,
      },
      pdf_artifact: {
        path: '00_TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_READER.pdf',
        bytes: 9507127,
        sha256: '1bad03f9ba031ba91967a0a0ac2af6d15a0f768882cd541fe26dcbe26c4edd0b',
      },
      repository: d60Receipt.repository,
      content_commit: d60Receipt.content_commit,
      mastery: { ordinary: '84/84', cumulative_assessments: '24/24', total_required: '108/108' },
      laboratories: { complete: 2, planned: 4 },
      backend: d60Receipt.backend,
      remaining: ['computation_laboratories_3_4', 'proof_metadata_closure', 'capstone'],
    },
  ],
  supplements: [],
  summary: {
    admitted_primary_course_routes: 1,
    admitted_partial_courses: 1,
    admitted_newly_complete_courses: 0,
    admitted_separate_supplements: 0,
    admitted_primary_selected_route_bytes: reader.bytes,
    supplement_selected_route_bytes: 0,
    honest_global_backend_state: 'federated_owner_native_authorities_common_capability_projection_in_progress',
  },
};

const admissionBytes = canonical(admission);
await mkdir(dirname(admissionPath), { recursive: true });
await writeFile(admissionPath, admissionBytes);

const replacement = {
  course_id: 'D60',
  url: reader.url,
  http_status: 200,
  bytes: reader.bytes,
  sha256: reader.sha256,
  content_type: 'text/html',
  scope: 'Roberts 30/30, Fomberg §§1.1–1.13, penguasaan wajib 108/108, dan laboratorium komputasi 2/4; kursus tetap diproduksi.',
};
const routes = predecessorReaders.routes.map((row) => row.course_id === 'D60' ? replacement : row);
assert.equal(routes.filter((row) => row.course_id === 'D60').length, 1);
assert.equal(routes.length, 7);

const ownerReaders = {
  schema_id: predecessorReaders.schema_id,
  recorded_at: recordedAt,
  result: 'pass',
  purpose: 'Bind exact public human-readable routes used by the central v0.61 learner projection. These routes are learner surfaces, not backend or JSON endpoints.',
  source_admission_manifest: {
    path: relative(logbook, admissionPath).replaceAll('\\', '/'),
    bytes: admissionBytes.length,
    sha256: sha256(admissionBytes),
  },
  policy: predecessorReaders.policy,
  routes,
  route_count: routes.length,
  total_bytes: routes.reduce((total, row) => total + row.bytes, 0),
  terminal_assessment: 'All seven routes are public readable HTML. D60 now resolves directly to the 108/108-mastery, two-laboratory checkpoint; machine JSON and source links remain secondary.',
};
const ownerReaderBytes = canonical(ownerReaders);
await writeFile(ownerReaderPath, ownerReaderBytes);

console.log(JSON.stringify({
  admission: { path: admissionPath, bytes: admissionBytes.length, sha256: sha256(admissionBytes) },
  owner_reader: { path: ownerReaderPath, bytes: ownerReaderBytes.length, sha256: sha256(ownerReaderBytes), routes: routes.length },
}, null, 2));
