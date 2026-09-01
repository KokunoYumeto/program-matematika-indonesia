import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { inflateRawSync } from 'node:zlib';
import { courses } from '../docs/courses.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const inputRoot = 'backend/course-capsule-v1/adapters/c130-v231';
const outputRoot = 'docs/backend/c130';
const archivePath = 'backend/course-capsule-v1/builds/program-matematika-indonesia-c130-operations-research-v2.3.1.zip';
const admissionPath = `${inputRoot}/ADMISSION.json`;
const authorityReplayPath = 'backend/course-capsule-v1/validation/C130_AUTHORITY_REPLAY_RECEIPT_20260901.json';
const recordedAt = '2026-09-01';

const expected = {
  archive: {
    bytes: 21213937,
    sha256: 'eb195d1aa555e9d5e639c1e35a08b6f4425be24cc93b7f1f633161e9cacee865',
  },
  authorityReplay: {
    bytes: 2977,
    sha256: '7cf3be9570c59f8fa1f35ea83b54e6ca2add842a19c65da3751a5a609dcdc09b',
  },
  checksums: {
    bytes: 6054,
    sha256: '34c93c23d7b93af06ff0df7fd9af34d906e8e8a2a29df4439e66001a26f12d82',
  },
  manifest: {
    bytes: 22488,
    sha256: 'cad2922d9bd1facb33cc9d54a9836bb168fe0b8d996d9d4ef2e5d8c26053f239',
  },
  package: {
    bytes: 253579914,
    files: 65,
    tree_sha256: '242e130059b40717fccf7499fdd7c66dcf411cb4dd1ad15d747c8f4731e29b0b',
  },
  seal: {
    aggregate_sha256: '72dc9f3c0838504a4590a2e81c560b1e146d565f3baaa2018e35a00746a6fb70',
    bytes: 15054,
    sealed_bytes: 253558806,
    sealed_files: 63,
    sha256: 'bf7ad1ef9aa20fa599076df9ef927b1e18592342c121e60f2a9a49a22b8d4a59',
  },
};

const pdf = {
  bytes: 26425739,
  filename: 'pemrograman-matematis-dan-riset-operasi-buku-1-id-ID.pdf',
  format: 'linked_pdf',
  locale: 'id-ID',
  pages: 666,
  sha256: 'daa9b79df3684729cc204b563669f400866d8fbd12c0977d32ff9897276a7a49',
  url: 'https://kokunoyumeto.github.io/open-optimization-or-book-id/downloads/pemrograman-matematis-dan-riset-operasi-buku-1-id-ID.pdf',
};

const owner = {
  concept_doi: '10.5281/zenodo.22059794',
  landing: 'https://kokunoyumeto.github.io/open-optimization-or-book-id/',
  release: 'https://github.com/KokunoYumeto/open-optimization-or-book-id/releases/tag/v2026.08.23-id.5',
  release_commit: 'a639b69cf84c4d4f60f7dcdb62dbeb5cfb153adc',
  release_tree: '1ab559b3540d9362bc0333caf017acd9fe540a9c',
  repository: 'https://github.com/KokunoYumeto/open-optimization-or-book-id',
  version_doi: '10.5281/zenodo.22070653',
  version_record: 'https://zenodo.org/records/22070653',
};

const exactRoutePayloads = [
  {
    course_id: 'C130', learner_priority: 1, machine_secondary: false,
    native_html: false, native_html_available: false, page_anchor: null,
    route_kind: 'pages_learner_landing', unit_anchor: null, url: owner.landing,
  },
  {
    bytes: pdf.bytes, course_id: 'C130', filename: pdf.filename, learner_priority: 2,
    machine_secondary: false, native_html: false, native_html_available: false,
    page_anchor: null, route_kind: 'linked_pdf', sha256: pdf.sha256,
    unit_anchor: null, url: pdf.url,
  },
  {
    course_id: 'C130', learner_priority: 3, machine_secondary: false,
    native_html: false, native_html_available: false, page_anchor: null,
    route_kind: 'source_repository', unit_anchor: null, url: owner.repository,
  },
  {
    course_id: 'C130', learner_priority: 4, machine_secondary: false,
    native_html: false, native_html_available: false, page_anchor: null,
    route_kind: 'zenodo_preservation_record', unit_anchor: null, url: owner.version_record,
  },
  {
    bytes: 20087323, course_id: 'C130',
    filename: 'pemrograman-matematis-dan-riset-operasi-buku-1-source-id-ID.zip',
    learner_priority: 5, machine_secondary: true, native_html: false,
    native_html_available: false, page_anchor: null, route_kind: 'editable_source_download',
    sha256: '55d62c53401938eb5dbc12d3f4116ce68181bd90c9f94fda1434fe20f5196914',
    unit_anchor: null,
    url: 'https://kokunoyumeto.github.io/open-optimization-or-book-id/downloads/pemrograman-matematis-dan-riset-operasi-buku-1-source-id-ID.zip',
  },
  {
    bytes: 527596, course_id: 'C130',
    filename: 'pemrograman-matematis-dan-riset-operasi-buku-1-o018-open-solver-labs-id-ID.zip',
    learner_priority: 6, machine_secondary: true, native_html: false,
    native_html_available: false, page_anchor: null, route_kind: 'computational_labs_download',
    sha256: '99628dcdd4984c8a3b763862dc88b06bca8bf15d47dbf1db863cfe46b2a1e592',
    unit_anchor: null,
    url: 'https://kokunoyumeto.github.io/open-optimization-or-book-id/downloads/pemrograman-matematis-dan-riset-operasi-buku-1-o018-open-solver-labs-id-ID.zip',
  },
  {
    bytes: 6535806, course_id: 'C130',
    filename: 'pemrograman-matematis-dan-riset-operasi-buku-1-modular-backend-v0.zip',
    learner_priority: 7, machine_secondary: true, native_html: false,
    native_html_available: false, page_anchor: null, route_kind: 'owner_backend_download',
    sha256: '7cd76333b3433518f4d983d6775412aba9fd99e1f6b9a35a89528e6994830c56',
    unit_anchor: null,
    url: 'https://kokunoyumeto.github.io/open-optimization-or-book-id/downloads/pemrograman-matematis-dan-riset-operasi-buku-1-modular-backend-v0.zip',
  },
];

const semanticCounts = {
  canonical_records: 51704,
  identity_crosswalks: 17273,
  native_html_claimed: false,
  native_rights_total: 7989,
  pdf_ua_claimed: false,
  reader_pages: 666,
  reader_surfaces: 1,
  relations: 9545,
  rights_assignments: 7634,
  routes: 7,
  segments: 5525,
  unit_or_page_anchors_claimed: false,
  units: 1993,
};

const expectedTableCounts = {
  adapter_profiles: 1,
  adapter_runs: 1,
  artifacts: 83,
  build_recipes: 0,
  content_bindings: 5525,
  course_unit_memberships: 1993,
  datasets: 1,
  editions: 5,
  identity_crosswalks: 17273,
  native_bindings: 5525,
  owner_authorities: 1,
  qa_events: 102,
  reader_surfaces: 1,
  relations: 9545,
  rights: 21,
  rights_assignments: 7634,
  routes: 7,
  search_documents: 1993,
  units: 1993,
};

const hash = (bytes) => createHash('sha256').update(bytes).digest('hex');
const identify = (bytes) => ({ bytes: bytes.length, sha256: hash(bytes) });
const stable = (value) => `${JSON.stringify(value, null, 2)}\n`;
const ordinal = (left, right) => (left < right ? -1 : left > right ? 1 : 0);
const escape = (value) => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
const formatInteger = (value) => String(value).replace(/\B(?=(\d{3})+(?!\d))/g, '.');

const safeInput = (path) => {
  assert.equal(typeof path, 'string');
  assert.ok(path && !path.startsWith('/') && !path.includes('\\') && !path.includes('\0'));
  const parts = path.split('/');
  assert.ok(parts.every((part) => part && part !== '.' && part !== '..'), `Unsafe input path: ${path}`);
  return path;
};

const jsonl = (bytes) => {
  const text = bytes.toString('utf8').trimEnd();
  return text ? text.split('\n').map(JSON.parse) : [];
};

const samePaths = (actual, wanted, message) => {
  assert.deepEqual([...actual].sort(ordinal), [...wanted].sort(ordinal), message);
};

const treeIdentity = (identities) => {
  const rows = [...identities.entries()].sort(([left], [right]) => ordinal(left, right))
    .map(([path, identity]) => `${path}\0${identity.bytes}\0${identity.sha256}\n`).join('');
  return hash(Buffer.from(rows));
};

const collectFiles = async (relativeDirectory = '') => {
  const directory = resolve(root, inputRoot, relativeDirectory);
  const rows = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = safeInput(relativeDirectory ? `${relativeDirectory}/${entry.name}` : entry.name);
    assert.equal(entry.isSymbolicLink(), false, `Symlink is forbidden in admitted package: ${path}`);
    if (entry.isDirectory()) rows.push(...await collectFiles(path));
    else {
      assert.equal(entry.isFile(), true, `Unsupported package entry: ${path}`);
      rows.push(path);
    }
  }
  return rows;
};

const parseChecksumLedger = (bytes, identities) => {
  assert.equal(bytes.toString('utf8').endsWith('\n'), true, 'Checksum ledger must end in LF');
  const lines = bytes.toString('utf8').trimEnd().split('\n');
  assert.equal(lines.length, 64, 'C130 checksum row count drift');
  const rows = new Map();
  for (const line of lines) {
    const match = /^([0-9a-f]{64})  (.+)$/.exec(line);
    assert.ok(match, `Malformed checksum row: ${line}`);
    const [, sha256, rawPath] = match;
    const path = safeInput(rawPath);
    assert.equal(rows.has(path), false, `Duplicate checksum path: ${path}`);
    const identity = identities.get(path);
    assert.ok(identity, `Checksum path absent from admitted package: ${path}`);
    assert.equal(identity.sha256, sha256, `Checksum mismatch: ${path}`);
    rows.set(path, identity);
  }
  assert.deepEqual([...rows.keys()], [...rows.keys()].sort(ordinal), 'Checksum rows are not in ordinal path order');
  return rows;
};

const findEndOfCentralDirectory = (bytes) => {
  const minimum = Math.max(0, bytes.length - 65557);
  for (let offset = bytes.length - 22; offset >= minimum; offset -= 1) {
    if (bytes.readUInt32LE(offset) === 0x06054b50) return offset;
  }
  assert.fail('ZIP end-of-central-directory record not found');
};

const readZipIdentities = (bytes) => {
  const end = findEndOfCentralDirectory(bytes);
  assert.equal(bytes.readUInt16LE(end + 4), 0, 'Multi-disk ZIP is forbidden');
  assert.equal(bytes.readUInt16LE(end + 6), 0, 'Multi-disk ZIP is forbidden');
  const diskEntries = bytes.readUInt16LE(end + 8);
  const totalEntries = bytes.readUInt16LE(end + 10);
  const centralSize = bytes.readUInt32LE(end + 12);
  const centralOffset = bytes.readUInt32LE(end + 16);
  const commentLength = bytes.readUInt16LE(end + 20);
  assert.equal(diskEntries, totalEntries);
  assert.equal(totalEntries, expected.package.files);
  assert.equal(end + 22 + commentLength, bytes.length, 'Trailing ZIP bytes are forbidden');
  assert.equal(centralOffset + centralSize, end, 'ZIP central-directory extent drift');

  const identities = new Map();
  const names = [];
  let offset = centralOffset;
  let totalBytes = 0;
  for (let index = 0; index < totalEntries; index += 1) {
    assert.equal(bytes.readUInt32LE(offset), 0x02014b50, `ZIP central entry ${index} is malformed`);
    const flags = bytes.readUInt16LE(offset + 8);
    const method = bytes.readUInt16LE(offset + 10);
    const compressedSize = bytes.readUInt32LE(offset + 20);
    const uncompressedSize = bytes.readUInt32LE(offset + 24);
    const nameLength = bytes.readUInt16LE(offset + 28);
    const extraLength = bytes.readUInt16LE(offset + 30);
    const entryCommentLength = bytes.readUInt16LE(offset + 32);
    const diskStart = bytes.readUInt16LE(offset + 34);
    const externalAttributes = bytes.readUInt32LE(offset + 38);
    const localOffset = bytes.readUInt32LE(offset + 42);
    const name = safeInput(bytes.subarray(offset + 46, offset + 46 + nameLength).toString('utf8'));
    assert.equal(flags & 1, 0, `Encrypted ZIP member is forbidden: ${name}`);
    assert.ok(method === 0 || method === 8, `Unsupported ZIP compression method for ${name}`);
    assert.equal(diskStart, 0, `Multi-disk ZIP member is forbidden: ${name}`);
    assert.notEqual((externalAttributes >>> 16) & 0o170000, 0o120000, `ZIP symlink is forbidden: ${name}`);
    assert.equal(identities.has(name), false, `Duplicate ZIP member: ${name}`);

    assert.equal(bytes.readUInt32LE(localOffset), 0x04034b50, `Malformed local ZIP header: ${name}`);
    assert.equal(bytes.readUInt16LE(localOffset + 8), method, `ZIP compression mismatch: ${name}`);
    const localNameLength = bytes.readUInt16LE(localOffset + 26);
    const localExtraLength = bytes.readUInt16LE(localOffset + 28);
    const localName = bytes.subarray(localOffset + 30, localOffset + 30 + localNameLength).toString('utf8');
    assert.equal(localName, name, `ZIP local/central name mismatch: ${name}`);
    const dataOffset = localOffset + 30 + localNameLength + localExtraLength;
    const compressed = bytes.subarray(dataOffset, dataOffset + compressedSize);
    assert.equal(compressed.length, compressedSize, `Truncated ZIP member: ${name}`);
    const content = method === 0 ? Buffer.from(compressed) : inflateRawSync(compressed);
    assert.equal(content.length, uncompressedSize, `ZIP member size mismatch: ${name}`);
    identities.set(name, identify(content));
    names.push(name);
    totalBytes += content.length;
    offset += 46 + nameLength + extraLength + entryCommentLength;
  }
  assert.equal(offset, centralOffset + centralSize, 'ZIP central-directory parse did not close');
  assert.equal(totalBytes, expected.package.bytes, 'ZIP member byte total drift');
  assert.deepEqual(names, [...names].sort(ordinal), 'ZIP members are not in ordinal path order');
  return identities;
};

const args = process.argv.slice(2);
assert.ok(args.every((arg) => arg === '--check'), `Unknown argument: ${args.find((arg) => arg !== '--check')}`);
assert.ok(args.length <= 1, 'Duplicate --check argument');
const checkOnly = args.includes('--check');

const admissionBytes = await readFile(resolve(root, admissionPath));
const admission = JSON.parse(admissionBytes);
assert.equal(admission.schema_id, 'interlanguage/c130-course-capsule-admission/v1');
assert.equal(admission.recorded_at, recordedAt);
assert.equal(admission.state, 'locally_admitted_central_release_pending');
assert.equal(admission.course_id, 'C130');
assert.deepEqual(admission.courses, ['C130']);
assert.equal(admission.package_id, 'urn:uuid:a84539b5-455b-5baf-89a4-f4c0336e33ab');
assert.equal(admission.dataset_id, 'urn:uuid:2e16c60d-7ee3-52f4-9c05-2c4dea0b07ca');
assert.equal(admission.extension_id, 'urn:uuid:d46eb7f0-cab9-5646-89cb-e4e82394c344');
assert.equal(admission.extension_version, '0.1.0');
assert.equal(admission.independent_trees_identical, true);
assert.equal(admission.admitted_inputs, expected.package.files);
assert.equal(admission.package_files, expected.package.files);
assert.equal(admission.package_bytes, expected.package.bytes);
assert.equal(admission.package_tree_sha256, expected.package.tree_sha256);
assert.equal(admission.archive_members, expected.package.files);
assert.equal(admission.archive_member_bytes, expected.package.bytes);
assert.deepEqual(admission.archive, { path: archivePath, ...expected.archive });
assert.equal(admission.manifest_bound_files_verified, 62);
assert.equal(admission.seal_bound_files_verified, expected.seal.sealed_files);
assert.equal(admission.checksum_rows_verified, 64);
assert.equal(admission.public_package_excludes_admission, true);
assert.equal(admission.textbook_body_centralized, false);
assert.deepEqual(admission.semantic_counts, semanticCounts);
assert.deepEqual(admission.owner_authority, {
  concept_doi: owner.concept_doi,
  landing: owner.landing,
  owner_native_authoritative: true,
  owner_tree_mutated: false,
  publication_verified_at: '2026-08-23T17:50:28+00:00',
  release: owner.release,
  release_commit: owner.release_commit,
  release_tree: owner.release_tree,
  repository: owner.repository,
  version_doi: owner.version_doi,
  version_record: owner.version_record,
});
assert.equal(admission.validation_scope.python_authority_validators_replayed, false);

// ADMISSION.json is the preserved prepublication intake receipt. The bounded
// postpublication authority replay is additive evidence and must not rewrite
// that historical byte.
const authorityReplayBytes = await readFile(resolve(root, authorityReplayPath));
assert.deepEqual(identify(authorityReplayBytes), expected.authorityReplay);
const authorityReplay = JSON.parse(authorityReplayBytes);
assert.equal(authorityReplay.schema_id, 'interlanguage/c130-postpublication-authority-replay/v1');
assert.equal(authorityReplay.state, 'pass_postpublication_authority_replay');
assert.equal(authorityReplay.scope.course_id, 'C130');
assert.equal(authorityReplay.scope.require_authorities, true);
assert.equal(authorityReplay.scope.package_or_owner_bytes_mutated, false);
assert.deepEqual(authorityReplay.package_archive, {
  bytes: expected.archive.bytes,
  sha256: expected.archive.sha256,
  members: expected.package.files,
  member_bytes: expected.package.bytes,
  tree_sha256: expected.package.tree_sha256,
});
assert.equal(authorityReplay.input_authorities.declared, 14);
assert.equal(authorityReplay.input_authorities.locally_replayed, 14);
assert.equal(authorityReplay.validator.exit_code, 0);
assert.equal(authorityReplay.validator.stderr_bytes, 0);
assert.equal(authorityReplay.generic_replay.status, 'PASS');
assert.equal(authorityReplay.generic_replay.canonical_records, semanticCounts.canonical_records);
assert.equal(authorityReplay.generic_replay.credential_or_local_path_hits, 0);
assert.equal(authorityReplay.c130_semantic_replay.status, 'PASS');
assert.equal(authorityReplay.c130_semantic_replay.identity_crosswalks, semanticCounts.identity_crosswalks);
assert.equal(authorityReplay.c130_semantic_replay.rights_assignments, semanticCounts.rights_assignments);
assert.equal(authorityReplay.claim_boundaries.authority_gate_closed, true);
const currentLimitations = admission.limits
  .filter((item) => !item.includes("does not replay the package's Python authority validators"))
  .concat('The packaged generic and C130 semantic validators were replayed postpublication with all 14 declared external authorities; this does not enlarge the package scope or rewrite owner-native bytes.');

const allInputPaths = (await collectFiles()).sort(ordinal);
assert.deepEqual(allInputPaths.filter((path) => path === 'ADMISSION.json'), ['ADMISSION.json']);
const importedPaths = allInputPaths.filter((path) => path !== 'ADMISSION.json');
assert.equal(importedPaths.length, expected.package.files, 'Imported package file count drift');
const directoryIdentities = new Map();
for (const path of importedPaths) {
  directoryIdentities.set(path, identify(await readFile(resolve(root, inputRoot, path))));
}
assert.equal([...directoryIdentities.values()].reduce((sum, row) => sum + row.bytes, 0), expected.package.bytes);
assert.equal(treeIdentity(directoryIdentities), expected.package.tree_sha256, 'Imported package tree identity drift');

const checksumBytes = await readFile(resolve(root, inputRoot, 'PACKAGE_CHECKSUMS.sha256'));
assert.deepEqual(identify(checksumBytes), expected.checksums);
assert.deepEqual(admission.checksums, {
  bytes: expected.checksums.bytes,
  path: `${inputRoot}/PACKAGE_CHECKSUMS.sha256`,
  rows: 64,
  sha256: expected.checksums.sha256,
});
const checksumRows = parseChecksumLedger(checksumBytes, directoryIdentities);
samePaths(checksumRows.keys(), importedPaths.filter((path) => path !== 'PACKAGE_CHECKSUMS.sha256'),
  'Checksum coverage drift');

const manifestBytes = await readFile(resolve(root, inputRoot, 'manifest.json'));
assert.deepEqual(identify(manifestBytes), expected.manifest);
const manifest = JSON.parse(manifestBytes);
assert.equal(manifest.schema_id, 'interlanguage/global-modular-mathematics-lane-adapter/2.3.1');
assert.equal(manifest.schema_version, '2.3.1');
assert.equal(manifest.package_id, admission.package_id);
assert.equal(manifest.dataset_id, admission.dataset_id);
assert.equal(manifest.extension_id, admission.extension_id);
assert.equal(manifest.extension_version, admission.extension_version);
assert.equal(manifest.files.length, 62);
assert.equal(manifest.authorities.length, 14);
assert.equal(manifest.sidecars.length, 6);
assert.equal(manifest.build.deterministic_replay, 'byte_identical');
assert.equal(manifest.csv_projection.record_count, semanticCounts.canonical_records);
assert.equal(manifest.csv_projection.table_csv_count, 19);
assert.equal(manifest.csv_projection.aggregate_csv_count, 1);
assert.equal(manifest.csv_projection.roundtrip_state, 'pass');
assert.equal(manifest.zero_copy_policy.aggregate_conformance_claim, false);
assert.equal(manifest.zero_copy_policy.full_prose_centralized, false);
assert.equal(manifest.zero_copy_policy.machine_data_is_learner_destination, false);
assert.equal(manifest.zero_copy_policy.owner_ids_reminted, false);
const manifestPaths = new Set();
for (const row of manifest.files) {
  const path = safeInput(row.path);
  assert.equal(row.path_base, 'package_root', `${path}: unsupported manifest path base`);
  assert.equal(manifestPaths.has(path), false, `Duplicate manifest path: ${path}`);
  manifestPaths.add(path);
  assert.deepEqual(directoryIdentities.get(path), { bytes: row.bytes, sha256: row.sha256 },
    `Manifest identity drift: ${path}`);
}
samePaths(manifestPaths, importedPaths.filter((path) => !['PACKAGE_CHECKSUMS.sha256', 'manifest.json', 'seal.json'].includes(path)),
  'Manifest payload coverage drift');
assert.equal([...manifestPaths].reduce((sum, path) => sum + directoryIdentities.get(path).bytes, 0), 253536318);
assert.deepEqual(admission.manifest, {
  aggregate_csv_count: 1,
  authorities: 14,
  bound_files: 62,
  bytes: expected.manifest.bytes,
  path: `${inputRoot}/manifest.json`,
  projected_records: semanticCounts.canonical_records,
  sha256: expected.manifest.sha256,
  sidecars: 6,
  table_csv_count: 19,
});

const sealBytes = await readFile(resolve(root, inputRoot, 'seal.json'));
assert.deepEqual(identify(sealBytes), { bytes: expected.seal.bytes, sha256: expected.seal.sha256 });
const seal = JSON.parse(sealBytes);
assert.equal(seal.algorithm, 'sha256-sorted-path-bytes-v1');
assert.equal(seal.aggregate_sha256, expected.seal.aggregate_sha256);
assert.equal(seal.file_count, expected.seal.sealed_files);
assert.equal(seal.files.length, expected.seal.sealed_files);
assert.equal(seal.bytes, expected.seal.sealed_bytes);
assert.equal(seal.seal_excluded_from_own_digest, true);
const sealPaths = new Set();
for (const row of seal.files) {
  const path = safeInput(row.path);
  assert.equal(row.path_base, 'package_root', `${path}: unsupported seal path base`);
  assert.equal(sealPaths.has(path), false, `Duplicate seal path: ${path}`);
  sealPaths.add(path);
  assert.deepEqual(directoryIdentities.get(path), { bytes: row.bytes, sha256: row.sha256 },
    `Seal identity drift: ${path}`);
}
samePaths(sealPaths, [...manifestPaths, 'manifest.json'], 'Seal coverage drift');
assert.equal(seal.files.reduce((sum, row) => sum + row.bytes, 0), expected.seal.sealed_bytes);
const sealIdentityRows = new Map(seal.files.map((row) => [row.path, { bytes: row.bytes, sha256: row.sha256 }]));
assert.equal(treeIdentity(sealIdentityRows), expected.seal.aggregate_sha256, 'Seal aggregate identity drift');
assert.deepEqual(admission.seal, {
  aggregate_sha256: expected.seal.aggregate_sha256,
  algorithm: 'sha256-sorted-path-bytes-v1',
  bytes: expected.seal.bytes,
  path: `${inputRoot}/seal.json`,
  seal_excluded_from_own_digest: true,
  sealed_bytes: expected.seal.sealed_bytes,
  sealed_files: expected.seal.sealed_files,
  sha256: expected.seal.sha256,
});

const archiveBytes = await readFile(resolve(root, archivePath));
assert.deepEqual(identify(archiveBytes), expected.archive, 'C130 archive identity drift');
const archiveIdentities = readZipIdentities(archiveBytes);
samePaths(archiveIdentities.keys(), directoryIdentities.keys(), 'Archive/directory member coverage drift');
for (const [path, identity] of directoryIdentities) {
  assert.deepEqual(archiveIdentities.get(path), identity, `Archive/directory byte identity drift: ${path}`);
}
assert.equal(treeIdentity(archiveIdentities), expected.package.tree_sha256, 'Archive tree identity drift');

const csvProjection = JSON.parse(await readFile(resolve(root, inputRoot, 'csv-projection-manifest-v0.2.0.json')));
assert.equal(csvProjection.records_csv.records, semanticCounts.canonical_records);
assert.equal(csvProjection.tables.length, 19);
assert.equal(csvProjection.tables.every((row) => row.roundtrip_state === 'pass'), true);
const tableCounts = Object.fromEntries(csvProjection.tables.map((row) => [row.table, row.records]));
assert.deepEqual(tableCounts, expectedTableCounts);
assert.equal(Object.values(tableCounts).reduce((sum, value) => sum + value, 0), semanticCounts.canonical_records);

const datasetRows = jsonl(await readFile(resolve(root, inputRoot, 'tables/datasets.jsonl')));
assert.equal(datasetRows.length, 1);
assert.equal(datasetRows[0].payload.course_id, 'C130');
assert.equal(datasetRows[0].payload.title, 'Pemrograman Matematis dan Riset Operasi — Buku 1');
assert.equal(datasetRows[0].payload.locale, 'id-ID');
assert.equal(datasetRows[0].payload.zero_copy, true);
assert.equal(datasetRows[0].payload.owner_counts.segments, semanticCounts.segments);
assert.equal(datasetRows[0].payload.owner_counts.units, semanticCounts.units);
assert.equal(datasetRows[0].payload.owner_counts.relations, semanticCounts.relations);

const adapterRuns = jsonl(await readFile(resolve(root, inputRoot, 'tables/adapter_runs.jsonl')));
assert.equal(adapterRuns.length, 1);
assert.equal(adapterRuns[0].normalized_state, 'validated');
assert.deepEqual(adapterRuns[0].payload.table_counts, expectedTableCounts);
assert.equal(adapterRuns[0].payload.source_reports_trusted_without_replay, false);
assert.equal(adapterRuns[0].payload.owner_tree_mutated, false);

const rightsClosure = JSON.parse(await readFile(resolve(root, inputRoot, 'rights-assignment-closure-v0.1.0.json')));
assert.equal(rightsClosure.counts.materialized_total, semanticCounts.rights_assignments);
assert.equal(rightsClosure.counts.referenced_only_total, 355);
assert.equal(rightsClosure.counts.total, semanticCounts.native_rights_total);
assert.equal(rightsClosure.flattened_license_claim, false);

const translationState = JSON.parse(await readFile(resolve(root, inputRoot, 'translation-state-index-v0.2.0.json')));
assert.equal(translationState.records.length, semanticCounts.units);
assert.equal(translationState.no_inference, true);

const scope = JSON.parse(await readFile(resolve(root, inputRoot, 'scope-declaration-v0.2.0.json')));
assert.deepEqual(scope.course_ids, ['C130']);
assert.equal(scope.aggregate_conformance_claim, false);
assert.ok(scope.limitations.some((value) => value.includes('R017 Book 2')));
assert.ok(scope.limitations.some((value) => value.includes('native HTML')));
assert.ok(scope.limitations.some((value) => value.includes('PDF/UA')));

const capabilityDeclarations = JSON.parse(await readFile(resolve(root, inputRoot, 'capability-declarations-v0.2.0.json')));
const capabilityByName = new Map(capabilityDeclarations.capabilities.map((row) => [row.name, row]));
assert.ok(capabilityByName.get('accessibility').loss_gap_report.reason.includes('PDF/UA'));
assert.ok(capabilityByName.get('computational_interactives').loss_gap_report.reason.includes('not independently recomputed'));
assert.ok(capabilityByName.get('mathematical_preservation').loss_gap_report.reason.includes('aggregate-only'));
assert.ok(capabilityByName.get('publication').closure_rules[0].includes('seven truthful'));

const routeRows = jsonl(await readFile(resolve(root, inputRoot, 'tables/routes.jsonl')))
  .sort((left, right) => left.payload.learner_priority - right.payload.learner_priority);
assert.equal(routeRows.length, semanticCounts.routes);
assert.equal(routeRows.every((row) => row.normalized_state === 'verified_public_route'), true);
assert.equal(routeRows.every((row) => row.owner_native_state === 'published_and_anonymously_verified'), true);
assert.deepEqual(routeRows.map((row) => row.payload), exactRoutePayloads);
for (const row of routeRows) {
  const url = new URL(row.payload.url);
  assert.equal(url.protocol, 'https:');
  assert.equal(url.username + url.password, '');
  assert.equal(url.hash, '', `Guessed descendant anchor is forbidden: ${row.payload.url}`);
}

const readerRows = jsonl(await readFile(resolve(root, inputRoot, 'tables/reader_surfaces.jsonl')));
assert.equal(readerRows.length, semanticCounts.reader_surfaces);
const reader = readerRows[0].payload;
assert.equal(reader.primary, true);
assert.equal(reader.format, pdf.format);
assert.equal(reader.locale, pdf.locale);
assert.equal(reader.public_url, pdf.url);
assert.equal(reader.pages, pdf.pages);
assert.equal(reader.bytes, pdf.bytes);
assert.equal(reader.sha256, pdf.sha256);
assert.equal(reader.machine_data_primary, false);
assert.equal(reader.native_html, false);
assert.equal(reader.page_anchors, false);
assert.equal(reader.page_anchor_coverage, 0);
assert.equal(reader.unit_anchors, false);
assert.equal(reader.unit_anchor_coverage, 0);
assert.equal(reader.tagged_pdf, false);
assert.equal(reader.pdf_ua_claimed, false);
assert.equal(reader.pdf_ua_verified, false);
assert.equal(reader.landing_route_id, routeRows[0].id);
assert.equal(reader.route_id, routeRows[1].id);

const ownerRows = jsonl(await readFile(resolve(root, inputRoot, 'tables/owner_authorities.jsonl')));
assert.equal(ownerRows.length, 1);
assert.equal(ownerRows[0].payload.owner_native_authoritative, true);
assert.equal(ownerRows[0].payload.owner_tree_mutated, false);
assert.equal(ownerRows[0].payload.pages, owner.landing);
assert.equal(ownerRows[0].payload.repository, owner.repository);
assert.equal(ownerRows[0].payload.version_doi, owner.version_doi);
assert.equal(ownerRows[0].payload.concept_doi, owner.concept_doi);

const course = courses.find((row) => row.id === 'C130');
assert.ok(course, 'C130 is absent from the central course catalog');
assert.equal(course.state, 'published');
assert.equal(course.title, 'Optimisasi Linear dan Integer / Riset Operasi');
assert.equal(course.reader, owner.landing);
assert.equal(course.repository, owner.repository);
assert.equal(course.zenodo, `https://doi.org/${owner.version_doi}`);
assert.equal(course.edition, `https://zenodo.org/records/22070653/files/${pdf.filename}?download=1`);

const learnerRoutes = routeRows.map((row) => ({
  route_id: row.id,
  normalized_state: row.normalized_state,
  owner_native_state: row.owner_native_state,
  ...row.payload,
}));
const route = {
  schema_id: 'interlanguage/c130-course-capsule-learner-route/v1',
  recorded_at: recordedAt,
  course_id: 'C130',
  title: course.title,
  reader_title: datasetRows[0].payload.title,
  authority: {
    owner_native_authoritative: true,
    repository: owner.repository,
    landing: owner.landing,
    release: owner.release,
    release_commit: owner.release_commit,
    release_tree: owner.release_tree,
    version_doi: owner.version_doi,
    concept_doi: owner.concept_doi,
  },
  primary_learner_action: {
    kind: exactRoutePayloads[0].route_kind,
    priority: 1,
    locale: pdf.locale,
    url: owner.landing,
  },
  primary_reader: {
    ...pdf,
    tagged_pdf: false,
    pdf_ua_claimed: false,
    unit_anchors: false,
    page_anchors: false,
  },
  routes: learnerRoutes,
  adapter: {
    state: admission.state,
    contract_version: '2.3.1',
    ...semanticCounts,
    machine_data_is_primary_learner_destination: false,
    textbook_body_centralized: false,
    independent_trees_identical: true,
    admitted_inputs: expected.package.files,
    admission: { path: admissionPath, ...identify(admissionBytes) },
    manifest: { path: `${inputRoot}/manifest.json`, ...expected.manifest, files_verified: 62 },
    seal: {
      path: `${inputRoot}/seal.json`, bytes: expected.seal.bytes,
      sha256: expected.seal.sha256, files_verified: expected.seal.sealed_files,
      aggregate_sha256: expected.seal.aggregate_sha256,
    },
    checksums: { path: `${inputRoot}/PACKAGE_CHECKSUMS.sha256`, ...expected.checksums, rows_verified: 64 },
    archive: admission.archive,
  },
  authority_replay: { path: authorityReplayPath, ...expected.authorityReplay, state: authorityReplay.state },
  limitations: currentLimitations,
};
const routeBytes = Buffer.from(stable(route));

const byKind = new Map(exactRoutePayloads.map((row) => [row.route_kind, row]));
const title = `C130 — ${course.title}`;
let html = `<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)}</title><meta name="description" content="Buku 1 optimisasi linear dan integer Bahasa Indonesia, PDF 666 halaman, laboratorium solver terbuka, serta bukti adapter C130."><link rel="stylesheet" href="../backend.css"><style>main{max-width:900px;margin:2rem auto;padding:0 1rem}.actions{display:flex;flex-wrap:wrap;gap:.75rem;margin:1.25rem 0}.primary,.secondary{display:inline-flex;min-height:44px;align-items:center;padding:.65rem 1rem;border:2px solid currentColor;border-radius:.5rem;font-weight:700}.secondary{border-width:1px}.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(12rem,1fr));gap:.75rem}.facts div,details,.notice{padding:1rem;border:1px solid currentColor;border-radius:.5rem}.facts strong{display:block;font-size:1.35rem}.notice{border-left-width:4px}.machine-evidence li{margin:.65rem 0}code{overflow-wrap:anywhere}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}a:focus-visible,summary:focus-visible{outline:3px solid currentColor;outline-offset:4px}</style></head><body><main><nav aria-label="Navigasi"><a href="../index.html">← Kembali ke katalog program</a></nav><h1>${escape(title)}</h1><p><cite>Pemrograman Matematis dan Riset Operasi — Buku 1</cite> adalah edisi Bahasa Indonesia lengkap dengan laboratorium Pyomo dan HiGHS yang diatribusikan terpisah.</p><div class="actions"><a class="primary" data-route-kind="pages_learner_landing" href="${escape(byKind.get('pages_learner_landing').url)}">Buka halaman pembaca Bahasa Indonesia</a><a class="secondary" data-route-kind="linked_pdf" href="${escape(byKind.get('linked_pdf').url)}">Buka PDF langsung — 666 halaman</a></div><p class="notice">Identitas PDF yang diikat bukti publikasi pemilik: ${formatInteger(pdf.bytes)} byte, SHA-256 <code>${pdf.sha256}</code>. PDF memiliki teks Unicode, bookmark, dan tautan, tetapi belum bertag dan tidak diklaim sesuai PDF/UA.</p><section aria-labelledby="closure-title"><h2 id="closure-title">Cakupan adapter yang diterima</h2><div class="facts"><div><strong>${formatInteger(semanticCounts.units)}</strong>unit owner-native</div><div><strong>${formatInteger(semanticCounts.segments)}</strong>segmen zero-copy</div><div><strong>${formatInteger(semanticCounts.relations)}</strong>relasi bertipe</div><div><strong>${semanticCounts.routes}</strong>rute publik terurut</div></div></section><details><summary>Sumber dan preservasi</summary><ul><li><a data-route-kind="source_repository" href="${escape(byKind.get('source_repository').url)}">Repositori sumber Indonesia</a></li><li><a data-route-kind="zenodo_preservation_record" href="${escape(byKind.get('zenodo_preservation_record').url)}">Rekaman preservasi Zenodo versi ini</a></li></ul><p>GitHub Pages dan repositori adalah alamat yang dapat berubah; adapter mengikat commit <code>${owner.release_commit}</code>, tree <code>${owner.release_tree}</code>, dan rekaman Zenodo versi tetap.</p></details><details class="machine-evidence"><summary>Unduhan sekunder dan bukti mesin</summary><p>Mulai dari pembaca di atas. Sumber, laboratorium, dan backend berikut adalah unduhan sekunder.</p><ul><li><a data-route-kind="editable_source_download" href="${escape(byKind.get('editable_source_download').url)}">Unduh sumber edisi</a></li><li><a data-route-kind="computational_labs_download" href="${escape(byKind.get('computational_labs_download').url)}">Unduh laboratorium O018</a></li><li><a data-route-kind="owner_backend_download" href="${escape(byKind.get('owner_backend_download').url)}">Unduh backend modular pemilik</a></li><li><a href="learner-route.json">Rute pelajar dan batas klaim</a></li><li><a href="validation.json">Bukti validasi penerimaan lokal</a></li></ul><p>Adapter pusat memverifikasi ${expected.package.files} berkas direktori dan anggota ZIP secara identik-byte. Validator Python pemilik tidak diputar ulang oleh halaman ini. Tidak ada HTML bab native, jangkar unit/halaman, mesin asesmen, atau kebenaran semantik hasil laboratorium yang diklaim ulang.</p></details></main></body></html>
`;
const staleAuthoritySentence = 'Validator Python pemilik tidak diputar ulang oleh halaman ini.';
assert.equal(html.split(staleAuthoritySentence).length - 1, 1, 'Historical C130 validator wording drift');
html = html.replace(
  staleAuthoritySentence,
  'Validator generik dan semantik C130 telah diputar ulang terhadap seluruh 14 otoritas eksternal dan lulus tanpa mengubah byte paket atau sumber pemilik.',
);
const htmlBytes = Buffer.from(html);
const machineEvidenceOffset = html.indexOf('<details class="machine-evidence">');
assert.ok(machineEvidenceOffset > 0, 'Machine-evidence section is absent');
assert.ok(html.indexOf(owner.landing) < machineEvidenceOffset, 'Learner landing must precede machine evidence');
assert.ok(html.indexOf(pdf.url) < machineEvidenceOffset, 'PDF must precede machine evidence');
assert.equal((html.match(/data-route-kind=/g) ?? []).length, semanticCounts.routes);
for (const row of exactRoutePayloads) {
  assert.equal(html.split(`href="${escape(row.url)}"`).length - 1, 1, `HTML route duplication/drift: ${row.url}`);
}
assert.ok(!/<script\b/i.test(html), 'C130 page must work without JavaScript');

const coursesBytes = await readFile(resolve(root, 'docs/courses.js'));
const generatorBytes = await readFile(fileURLToPath(import.meta.url));
const validation = {
  schema_id: 'interlanguage/c130-course-capsule-learner-route-validation/v1',
  state: 'pass',
  recorded_at: recordedAt,
  admission: { path: admissionPath, ...identify(admissionBytes) },
  source_bindings: {
    course_catalog: { path: 'docs/courses.js', ...identify(coursesBytes) },
    generator: { path: 'scripts/build-c130-course-capsule-v1.mjs', ...identify(generatorBytes) },
  },
  imported_package: {
    admitted_inputs: expected.package.files,
    admitted_input_bytes: expected.package.bytes,
    package_tree_sha256: expected.package.tree_sha256,
    independent_trees_identical: true,
    archive: { ...admission.archive, members_verified: expected.package.files, member_bytes_verified: expected.package.bytes },
    archive_members_decompressed_and_sha256_matched: true,
    manifest: { path: `${inputRoot}/manifest.json`, ...expected.manifest, files_verified: 62 },
    seal: {
      path: `${inputRoot}/seal.json`, bytes: expected.seal.bytes, sha256: expected.seal.sha256,
      files_verified: expected.seal.sealed_files, sealed_bytes: expected.seal.sealed_bytes,
      aggregate_sha256: expected.seal.aggregate_sha256,
    },
    checksums: { path: `${inputRoot}/PACKAGE_CHECKSUMS.sha256`, ...expected.checksums, rows_verified: 64 },
  },
  semantic_counts: semanticCounts,
  learner_routes: {
    count: semanticCounts.routes,
    ordered_route_kinds: exactRoutePayloads.map((row) => row.route_kind),
    exact_urls: exactRoutePayloads.map((row) => row.url),
    pages_landing_is_priority_one: true,
    linked_pdf_is_only_primary_reader: true,
    pdf: { ...pdf, tagged_pdf: false, pdf_ua_claimed: false },
    machine_downloads_are_secondary: true,
    guessed_descendant_anchors: 0,
  },
  authority_replay: { path: authorityReplayPath, ...expected.authorityReplay, state: authorityReplay.state },
  claim_boundaries: {
    aggregate_program_conformance_claimed: false,
    native_html_claimed: false,
    pdf_ua_claimed: false,
    python_authority_validators_replayed: true,
    textbook_body_centralized: false,
    current_mutable_url_availability_claimed: false,
  },
  javascript_required: false,
  limitations: currentLimitations,
  outputs: {
    'C130.html': identify(htmlBytes),
    'learner-route.json': identify(routeBytes),
  },
};
const validationBytes = Buffer.from(stable(validation));
const outputs = new Map([
  ['C130.html', htmlBytes],
  ['learner-route.json', routeBytes],
  ['validation.json', validationBytes],
]);

if (!checkOnly) {
  await mkdir(resolve(root, outputRoot), { recursive: true });
  for (const [name, bytes] of outputs) await writeFile(resolve(root, outputRoot, name), bytes);
}
for (const [name, bytes] of outputs) {
  const written = await readFile(resolve(root, outputRoot, name));
  assert.equal(written.equals(bytes), true, `Generated output drift: ${name}`);
}

console.log(JSON.stringify({
  state: 'pass',
  mode: checkOnly ? 'check' : 'write',
  course_id: 'C130',
  admitted_inputs: expected.package.files,
  independent_trees_identical: true,
  outputs: Object.fromEntries([...outputs].map(([name, bytes]) => [name, identify(bytes)])),
}, null, 2));
