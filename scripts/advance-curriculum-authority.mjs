import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const predecessorRelative = 'backend/authority/history/curriculum-authority-v0.53.0.json';
const outputRelative = 'backend/authority/curriculum-authority-v1.json';
const predecessorExpected = {
  bytes: 50085,
  sha256: '0eaa292eb79244332a64591a54e88943832b98142f6cf0b422f2a63d9b8e671f',
};

function option(name) {
  const index = process.argv.indexOf(name);
  if (index === -1 || !process.argv[index + 1]) throw new Error(`Missing required option ${name}.`);
  return process.argv[index + 1];
}

const version = option('--version');
const recordId = option('--record-id');
const snapshotDate = option('--snapshot-date');
const readbackAt = option('--readback-at');

assert.match(version, /^\d+\.\d+\.\d+$/, 'Version must be semantic x.y.z.');
assert.match(recordId, /^\d+$/, 'Zenodo record ID must be numeric.');
assert.match(snapshotDate, /^\d{4}-\d{2}-\d{2}$/, 'Snapshot date must be YYYY-MM-DD.');
assert.match(readbackAt, /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/, 'Readback time must be canonical UTC.');

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const predecessorPath = resolve(project, predecessorRelative);
const predecessorBytes = await readFile(predecessorPath);
assert.equal(predecessorBytes.length, predecessorExpected.bytes, 'Predecessor authority byte count changed.');
assert.equal(sha256(predecessorBytes), predecessorExpected.sha256, 'Predecessor authority SHA-256 changed.');

const predecessor = JSON.parse(predecessorBytes.toString('utf8'));
assert.equal(predecessor.schema_id, 'interlanguage/program-matematika-indonesia-curriculum-authority/v1');
assert.equal(predecessor.catalog.program.version, '0.53.0');
assert.equal(predecessor.catalog.program.zenodo, 'https://doi.org/10.5281/zenodo.22097431');
assert.equal(predecessor.authority_policy.docs_courses_js_is_authority, false);
assert.equal(predecessor.authority_policy.owner_native_backends_remain_canonical, true);

const authority = structuredClone(predecessor);
authority.$schema = 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v1/curriculum-authority-v1.schema.json';
authority.authority_state = 'active_versioned_successor';
authority.lineage = {
  bootstrap_release_version: '0.53.0',
  predecessor_authority: {
    path: predecessorRelative,
    bytes: predecessorBytes.length,
    sha256: sha256(predecessorBytes),
  },
  transition: {
    from_version: predecessor.catalog.program.version,
    to_version: version,
    snapshot_date: snapshotDate,
    zenodo_record_id: Number(recordId),
    method: 'deterministic_release_overlay_preserving_curriculum_and_native_backend_authority',
  },
};

authority.public_readback_overlays = [
  {
    course_id: 'C80',
    surface_id: 'urn:uuid:4092d0b1-1fed-5ef3-adc6-943dbf7dad30',
    url: 'https://zenodo.org/records/21932787/files/00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf?download=1',
    source_publication_state: 'catalog_declared',
    effective_publication_state: 'public',
    evidence_kind: 'anonymous_public_byte_readback',
    bytes: 5593664,
    sha256: 'bf538d5e1994a7a7600703c9d24616696f77e43e9312fb51078095ff0c963c0a',
    verified_at: readbackAt,
  },
  {
    course_id: 'C110',
    surface_id: 'urn:uuid:f179f444-d4ad-5623-957b-9ce8e917c7be',
    url: 'https://zenodo.org/records/22054086/files/Tea-Time-Numerical-Analysis-id-ID.pdf?download=1',
    source_publication_state: 'catalog_declared',
    effective_publication_state: 'public',
    evidence_kind: 'anonymous_public_byte_readback',
    bytes: 8202476,
    sha256: 'cbc31e9e27fdee96845d78fa6a625bf956196001b7941ddf0f1232f5def46b45',
    verified_at: readbackAt,
  },
];

const program = authority.catalog.program;
program.version = version;
program.snapshotDate = snapshotDate;
program.zenodo = `https://doi.org/10.5281/zenodo.${recordId}`;
program.repositories.github.lastConfirmedAt = snapshotDate;
program.backend.schema = `https://zenodo.org/records/${recordId}/files/interlanguage-math-backend-v1.schema.json?download=1`;
program.backend.sourceFormatProfile = `https://zenodo.org/records/${recordId}/files/interlanguage-source-format-profile-v1.schema.json?download=1`;
program.backend.package = `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-backend-v1-v${version}.zip?download=1`;
program.backend.federationV2.package = `https://zenodo.org/records/${recordId}/files/program-matematika-indonesia-backend-v2-v${version}.zip?download=1`;
program.backend.federationV2.packageSchema = `https://zenodo.org/records/${recordId}/files/federation-package-v2.schema.json?download=1`;
program.backend.federationV2.recordSchema = `https://zenodo.org/records/${recordId}/files/federation-record-v2.schema.json?download=1`;
program.backend.federationV2.validationReceipt = `https://zenodo.org/records/${recordId}/files/GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v${version}.json?download=1`;
program.backend.learnerReadModelV1 = {
  version: '1.0.0',
  status: 'validated',
  courseCount: 40,
  prerequisiteEdgeCount: 82,
  authority: `https://zenodo.org/records/${recordId}/files/curriculum-authority-v1.json?download=1`,
  authoritySchema: `https://zenodo.org/records/${recordId}/files/curriculum-authority-v1.schema.json?download=1`,
  readModel: `https://zenodo.org/records/${recordId}/files/learner-read-model-v1.json?download=1`,
  readModelSchema: `https://zenodo.org/records/${recordId}/files/learner-read-model-v1.schema.json?download=1`,
  validationReceipt: `https://zenodo.org/records/${recordId}/files/LOCAL_RELEASE_VALIDATION_v${version}.json?download=1`,
  publicEndpoint: 'https://kokunoyumeto.github.io/program-matematika-indonesia/data/learner-read-model.json',
};

assert.deepEqual(authority.catalog.courses, predecessor.catalog.courses, 'A release successor may not silently change course authority.');
assert.deepEqual(authority.catalog.topics, predecessor.catalog.topics, 'A release successor may not silently change topic authority.');
assert.equal(program.zenodoConcept, predecessor.catalog.program.zenodoConcept, 'The existing Zenodo concept DOI must be preserved.');

const outputPath = resolve(project, outputRelative);
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(authority, null, 2)}\n`, 'utf8');
const outputBytes = await readFile(outputPath);
console.log(JSON.stringify({
  output: outputRelative,
  version,
  record_id: Number(recordId),
  bytes: outputBytes.length,
  sha256: sha256(outputBytes),
  overlays: authority.public_readback_overlays.length,
}, null, 2));
