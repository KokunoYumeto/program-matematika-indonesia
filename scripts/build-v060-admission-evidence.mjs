import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const workspace = resolve(project, '../../..');
const logbook = resolve(workspace, 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook');

function option(name) {
  const index = process.argv.indexOf(name);
  assert.ok(index !== -1 && process.argv[index + 1], `Missing required option ${name}.`);
  return process.argv[index + 1];
}

const recordedAt = option('--recorded-at');
assert.ok(!Number.isNaN(Date.parse(recordedAt)), 'Recorded-at must be an ISO-8601 timestamp.');

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');

const predecessorReader = {
  path: resolve(logbook, '114_PUBLIC_OWNER_HTML_ROUTE_READBACK_20260827.json'),
  bytes: 3371,
  sha256: '85bf2ffe9b0e82802f28f9e8780e92f7a239bf71fbae5627e651a3e5ee1e515e',
};
const d40ReadbackIdentity = {
  path: resolve(logbook, '117_D40_UNIT13_CENTRAL_HTML_PUBLIC_READBACK_20260828.json'),
  bytes: 21184,
  sha256: 'ef196d1424ff583b75dff8da99bf3bd8628080eab276ed39977365f9984ef45c',
};
const o001Root = resolve(project, 'backend/v2.2/owner-native-shards/o001-a00-assessments-v0.1.0');
const admissionPath = resolve(logbook, '118_CENTRAL_V060_ADMISSION_MANIFEST_20260828.json');
const ownerReaderPath = resolve(logbook, '119_PUBLIC_OWNER_HTML_ROUTE_READBACK_20260828.json');

async function loadBoundJson(identity, label) {
  const bytes = await readFile(identity.path);
  assert.equal(bytes.length, identity.bytes, `${label} bytes changed.`);
  assert.equal(sha256(bytes), identity.sha256, `${label} SHA-256 changed.`);
  return JSON.parse(bytes.toString('utf8'));
}

async function listFiles(root, prefix = '') {
  const rows = [];
  const entries = await readdir(resolve(root, prefix), { withFileTypes: true });
  entries.sort((left, right) => left.name.localeCompare(right.name, 'en'));
  for (const entry of entries) {
    const portable = prefix ? `${prefix}/${entry.name}` : entry.name;
    if (entry.isDirectory()) rows.push(...await listFiles(root, portable));
    else if (entry.isFile()) rows.push(portable);
  }
  return rows;
}

const [predecessor, d40Readback] = await Promise.all([
  loadBoundJson(predecessorReader, 'Predecessor owner-reader receipt'),
  loadBoundJson(d40ReadbackIdentity, 'D40 central-reader receipt'),
]);
assert.equal(predecessor.schema_id, 'program-matematika-indonesia/owner-reader-public-readback/v1');
assert.equal(predecessor.result, 'pass');
assert.equal(predecessor.route_count, 6);
assert.equal(d40Readback.schema_id, 'program-matematika-indonesia/public-directory-readback/v1');
assert.equal(d40Readback.result, 'pass');
assert.equal(d40Readback.public_route, 'https://kokunoyumeto.github.io/program-matematika-indonesia/readers/d40/unit13/');
assert.equal(d40Readback.totals.files, 57);
assert.equal(d40Readback.totals.bytes, 4131469);
assert.equal(d40Readback.index.bytes, 5587);
assert.equal(d40Readback.index.sha256, '222de82b5d2848736863e749e6fff8cb06093b0846bbb4312307a75ac746b49f');

const o001Files = [];
let o001Bytes = 0;
for (const path of await listFiles(o001Root)) {
  const bytes = await readFile(resolve(o001Root, path));
  o001Bytes += bytes.length;
  o001Files.push({ path, bytes: bytes.length, sha256: sha256(bytes) });
}
assert.equal(o001Files.length, 12);
assert.equal(o001Bytes, 19057785);
const o001Digest = sha256(Buffer.from(o001Files.map((row) => `${row.sha256}  ${row.bytes}  ${row.path}\n`).join(''), 'utf8'));
assert.equal(o001Digest, '5d7c3da1a1b3c33b4f79306fec08a31ebc8f557188f1ec0c088e267e0d9ce222');
const o001Manifest = JSON.parse((await readFile(resolve(o001Root, 'manifest.json'))).toString('utf8'));
assert.deepEqual(o001Manifest.counts, {
  assessment_components: 13345,
  assessments: 8105,
  modules: 75,
  problems: 8105,
  solution_gaps: 2865,
  solutions: 5240,
});

const admission = {
  schema_id: 'program-matematika-indonesia/central-release-admission-manifest/v1',
  target_release: '0.60.0',
  recorded_at: new Date(recordedAt).toISOString(),
  predecessor: {
    version: '0.59.0',
    authority_bytes: 71468,
    authority_sha256: '980ced12bddcddef1eaccb030316e0dafc3dc43079df721c497f7a761f43d5e6',
    git_commit: '63b918e8c75bbd64c3a2e582cc9cdace9f542959',
  },
  admissions: [
    {
      course_id: 'C110',
      decision: 'refresh_complete_route_to_latest_public_version',
      state_after: 'published',
      predecessor_record: 22054086,
      record: 22075088,
      concept_record: 22054085,
      doi: '10.5281/zenodo.22075088',
      version: '3.0-id.2-r1',
      access_right: 'open',
      license: 'cc-by-sa-4.0',
      learner_route: 'https://zenodo.org/records/22075088/files/Tea-Time-Numerical-Analysis-id-ID.pdf?download=1',
      primary_artifact: {
        path: 'Tea-Time-Numerical-Analysis-id-ID.pdf',
        format: 'pdf',
        pages: 387,
        bytes: 8202487,
        sha256: 'd573b7233d0baa07381e2052a749757885db3a31fbfe695c5a4851ea42d91b6d',
      },
      source_backend_archive: {
        path: 'Tea-Time-Numerical-Analysis-id-ID-v3.0-id.2-r1-source-backend.zip',
        bytes: 33244105,
        sha256: '0eebe482eec535942524d4e5cb1fb164b9ac7de07f2eb9421e0d7bf29fa7ee4c',
      },
      common_v1_migration_receipt: {
        path: 'backend/migrations/tea-time-id-v1/MIGRATION_RECEIPT.json',
        bytes: 9457,
        sha256: '53230dc3294cbcfc83f643a4b8056abc3ec6a1d3799c3e0e27d01ba64c734a4f',
      },
    },
    {
      course_id: 'D40',
      decision: 'refresh_partial_route_and_add_central_html_reader',
      state_after: 'production',
      predecessor_record: 22103731,
      record: 22132688,
      concept_record: 22059503,
      doi: '10.5281/zenodo.22132688',
      version: '2026.08.26-unit13',
      access_right: 'open',
      license: 'cc-by-nc-sa-4.0',
      learner_route: 'https://zenodo.org/records/22132688/files/PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_UNIT_13.pdf?download=1',
      primary_artifact: {
        path: 'PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_UNIT_13.pdf',
        format: 'pdf',
        pages: 193,
        bytes: 11003371,
        sha256: '6830d2f9bc1350cd28dfae143b25003e7ee32758e791c6205d166dabb85808f2',
      },
      preservation_archive: {
        path: 'persamaan-diferensial-parsial-dionne-id-unit13-20260827.zip',
        bytes: 8276864,
        sha256: '5b8feb9ddd25579cbfbf8554ee79d2a96fb0fcc956ea1d8b14f01733dba14c0e',
        entries: 290,
      },
      central_html_reader: {
        url: d40Readback.public_route,
        files: d40Readback.totals.files,
        bytes: d40Readback.totals.bytes,
        inventory_digest_sha256: d40Readback.totals.inventory_digest_sha256,
        index_bytes: d40Readback.index.bytes,
        index_sha256: d40Readback.index.sha256,
        public_readback: {
          path: relative(logbook, d40ReadbackIdentity.path).split(sep).join('/'),
          bytes: d40ReadbackIdentity.bytes,
          sha256: d40ReadbackIdentity.sha256,
        },
      },
      backend_state: 'owner_native_only_not_common_v1_or_v2_2_migrated',
    },
  ],
  infrastructure_admissions: [
    {
      role_id: 'O001',
      course_id: 'A00',
      decision: 'add_owner_native_assessment_and_solution_gap_shard',
      package: 'backend/v2.2/owner-native-shards/o001-a00-assessments-v0.1.0',
      package_id: o001Manifest.package_id,
      files: o001Files.length,
      bytes: o001Bytes,
      aggregate_sha256: o001Digest,
      manifest: {
        bytes: (await readFile(resolve(o001Root, 'manifest.json'))).length,
        sha256: sha256(await readFile(resolve(o001Root, 'manifest.json'))),
      },
      counts: o001Manifest.counts,
      zero_prose: true,
      common_v2_2_projection_state: 'owner_native_shard_ready_adapter_not_materialized',
    },
  ],
  summary: {
    refreshed_course_routes: 2,
    new_html_readers: 1,
    new_owner_native_backend_shards: 1,
    completed_public_course_roles_before: 19,
    completed_public_course_roles_after: 19,
    honest_global_backend_state: 'phase_release_not_global_migration_complete',
  },
};

const admissionBytes = canonical(admission);
await mkdir(dirname(admissionPath), { recursive: true });
await writeFile(admissionPath, admissionBytes);

const d40Route = {
  course_id: 'D40',
  url: d40Readback.public_route,
  http_status: 200,
  bytes: d40Readback.index.bytes,
  sha256: d40Readback.index.sha256,
  content_type: 'text/html',
  scope: 'Cumulative Unit 13 reader mirrored byte-for-byte by the central learner site; course remains production.',
};
const routes = [...predecessor.routes, d40Route].sort((left, right) => left.course_id.localeCompare(right.course_id, 'en'));
assert.equal(new Set(routes.map((row) => row.course_id)).size, 7);
const ownerReader = {
  schema_id: predecessor.schema_id,
  recorded_at: new Date(recordedAt).toISOString(),
  result: 'pass',
  purpose: 'Bind exact public human-readable routes used by the central v0.60 learner projection. These routes are learner surfaces, not backend or JSON endpoints.',
  source_admission_manifest: {
    path: relative(logbook, admissionPath).split(sep).join('/'),
    bytes: admissionBytes.length,
    sha256: sha256(admissionBytes),
  },
  policy: predecessor.policy,
  routes,
  route_count: routes.length,
  total_bytes: routes.reduce((total, row) => total + row.bytes, 0),
  terminal_assessment: 'All seven routes are public, readable HTML and may be used as primary learner actions. JSON, source, repository, DOI, and backend links remain secondary.',
};
const ownerReaderBytes = canonical(ownerReader);
await writeFile(ownerReaderPath, ownerReaderBytes);

console.log(JSON.stringify({
  admission: { path: admissionPath, bytes: admissionBytes.length, sha256: sha256(admissionBytes) },
  owner_reader: { path: ownerReaderPath, bytes: ownerReaderBytes.length, sha256: sha256(ownerReaderBytes), routes: routes.length },
}, null, 2));
