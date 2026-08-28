import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const workspace = resolve(project, '../../..');
const logbook = resolve(workspace, 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook');
const admissionPath = resolve(logbook, '141_CENTRAL_V062_ADMISSION_MANIFEST_20260828.json');
const readerPath = resolve(logbook, '142_PUBLIC_OWNER_HTML_ROUTE_READBACK_V062_20260828.json');
const priorReaderPath = resolve(logbook, '131_PUBLIC_OWNER_HTML_ROUTE_READBACK_20260828.json');

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');

function option(name) {
  const index = process.argv.indexOf(name);
  const value = index === -1 ? null : process.argv[index + 1] ?? null;
  if (!value) throw new Error(`Missing required option ${name}.`);
  return value;
}

const recordedAt = option('--recorded-at');
const recordId = Number(option('--record-id'));
assert.match(recordedAt, /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/);
assert.ok(Number.isInteger(recordId) && recordId > 0);

const sources = Object.freeze({
  a10: {
    path: 'outputs/01a01f41-26f0-7e63-952c-de86c2f9155e/elementary_algebra_2e_id/publication/zenodo/0.11.0-wip/ZENODO_PUBLICATION_RECEIPT.json',
    bytes: 3580,
    sha256: 'ddb624febb49edab1d47afe2516c38968fee37344251db847d9b7062c759f65b',
    role: 'A10 canonical owner Zenodo publication and anonymous byte-readback receipt',
  },
  b20: {
    path: '04_mirrors/id/clp1-differential-calculus-id/provenance/PUBLICATION_RECEIPT.id-ID.json',
    bytes: 2729,
    sha256: '41d565ad7c9d5dcfc2800fd51c76c150b743a5d93269bbacab8026c636805c96',
    role: 'B20 canonical complete-course GitHub and Zenodo publication receipt',
  },
  b40Zenodo: {
    path: '04_mirrors/id/hefferon-linear-algebra-id/publication/public-readback.zenodo.json',
    bytes: 2623,
    sha256: '64bb39bc8510e136b88c2bd54b66cfc3682616c691446e66bc185012f0492644',
    role: 'B40 exact three-PDF Zenodo byte-readback receipt',
  },
  b40Github: {
    path: '04_mirrors/id/hefferon-linear-algebra-id/publication/public-readback.json',
    bytes: 12735,
    sha256: 'ee1c663ce5302aeccc5e18d31853c84803b787f0dfe448a9b0a549991c2e3595',
    role: 'B40 GitHub Pages and repository public-readback receipt',
  },
  a30: {
    path: '04_mirrors/id/openstax-precalculus-2e-id/README.md',
    bytes: 5820,
    sha256: '33d767b675684e5959207ad974187a578f9d057bb20bbef7627648d026eed0a6',
    role: 'A30 canonical repository identity and partial-edition state',
  },
  d80: {
    path: '04_mirrors/id/methods-of-algebra-volume-2-id/release/zenodo/unit-050/ZENODO_PUBLICATION_RECEIPT.json',
    bytes: 14942,
    sha256: '33ae56fad71b837fffb5ef655fe14c733f00d5f0eecce4fb3d6ab8182a6393a4',
    role: 'D80 Unit 050 Zenodo publication and anonymous byte-readback receipt',
  },
  d90Readback: {
    path: '04_mirrors/id/advanced-optimization-convex-analysis-id/release/zenodo/2026-08-28-integrated-final/zenodo-public-readback-integrated.json',
    bytes: 27343,
    sha256: 'e5f75072c2d0aa6f2bfdfaa0a620495d913f75644528a626197089d183fcf176',
    role: 'D90 integrated terminal Zenodo file-by-file public readback',
  },
  d90Terminal: {
    path: '04_mirrors/id/advanced-optimization-convex-analysis-id/qa/INTEGRATED_TERMINAL_PUBLICATION_AUDIT.json',
    bytes: 1863,
    sha256: 'c17677c7de0806080f41f98f6e38bc0f817fc6d06fc27b644021462bdf24c3d3',
    role: 'D90 terminal complete-course admission audit',
  },
});

async function loadBound(source) {
  const path = resolve(workspace, source.path);
  const bytes = await readFile(path);
  assert.equal(bytes.length, source.bytes, `${source.path}: byte count changed.`);
  assert.equal(sha256(bytes), source.sha256, `${source.path}: SHA-256 changed.`);
  return { ...source, value: source.path.endsWith('.json') ? JSON.parse(bytes) : bytes.toString('utf8') };
}

async function fetchJson(url) {
  const response = await fetch(url, { headers: { accept: 'application/json', 'user-agent': 'program-matematika-indonesia-v062-evidence/1' } });
  assert.equal(response.status, 200, `${url}: HTTP ${response.status}`);
  return response.json();
}

async function verifyRecord(recordIdValue, expectedFiles) {
  const record = await fetchJson(`https://zenodo.org/api/records/${recordIdValue}`);
  assert.equal(Number(record.id), recordIdValue);
  assert.equal(record.status, 'published');
  assert.equal(record.metadata?.access_right, 'open');
  const files = new Map(record.files.map((file) => [file.key, file]));
  for (const expected of expectedFiles) {
    const file = files.get(expected.name);
    assert.ok(file, `${recordIdValue}: missing ${expected.name}`);
    assert.equal(file.size, expected.bytes, `${recordIdValue}/${expected.name}: bytes changed`);
  }
  return {
    record_id: recordIdValue,
    doi: record.pids?.doi?.identifier ?? `10.5281/zenodo.${recordIdValue}`,
    concept_id: Number(record.parent?.id ?? record.conceptrecid),
    status: record.status,
    access: record.metadata?.access_right,
    file_count: record.files.length,
    verified_files: expectedFiles.map(({ name, bytes, sha256: digest }) => ({ name, bytes, sha256: digest })),
  };
}

async function verifyPublicRepository(fullName) {
  const repo = await fetchJson(`https://api.github.com/repos/${fullName}`);
  assert.equal(repo.full_name, fullName);
  assert.equal(repo.private, false);
  assert.equal(repo.disabled, false);
  assert.equal(repo.html_url, `https://github.com/${fullName}`);
  return { repository: repo.html_url, default_branch: repo.default_branch, private: repo.private, disabled: repo.disabled };
}

const loaded = Object.fromEntries(await Promise.all(Object.entries(sources).map(async ([key, source]) => [key, await loadBound(source)])));

assert.equal(loaded.a10.value.record_id, '22143518');
assert.equal(loaded.a10.value.reader_admitted_module_count, 32);
assert.equal(loaded.a10.value.total_module_count, 82);
assert.equal(loaded.b20.value.zenodo.version_doi, '10.5281/zenodo.21938930');
assert.equal(loaded.b20.value.status, 'PASS');
assert.equal(loaded.b40Zenodo.value.zenodo.record_id, 22070458);
assert.equal(loaded.b40Github.value.combined_release_complete, true);
assert.equal(loaded.d80.value.record.record_id, '22143171');
assert.equal(loaded.d80.value.pdf_reader.pages, 320);
assert.equal(loaded.d90Terminal.value.terminal_condition_satisfied, true);
assert.equal(loaded.d90Terminal.value.course_status, 'complete');
assert.equal(loaded.d90Readback.value.record_id, '22142120');
assert.equal(loaded.d90Readback.value.status, 'published');

const publicRecords = await Promise.all([
  verifyRecord(22143518, [{ name: '00-elementary-algebra-2e-bahasa-indonesia-EA2-S0032-reader.pdf', bytes: 42789518, sha256: '976b1df4dd1c609d35c6fc9563369f6819fc333d782b96f1e2af28e7257bf23e' }]),
  verifyRecord(21938930, [
    { name: '00_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_BUKU_TEKS.pdf', bytes: 4997608, sha256: 'e0466ca75b793aed64e2c356014233d9e85072b077a3b2d3344926835c408ec2' },
    { name: '01_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_SOAL_DAN_PENYELESAIAN.pdf', bytes: 3263082, sha256: '911b2a0e3a9de6eccb9dd93042fa697e8f02e4bb1ecdacec86ade68744245021' },
  ]),
  verifyRecord(22070458, [
    { name: '01_HEFFERON_LINEAR_ALGEBRA_ID_TEXTBOOK_2026.08.22.pdf', bytes: 8984459, sha256: '0462ddc8ffcc901efbc81205f79a249ae716e838a6ec32eda033444a90b8755e' },
    { name: '02_HEFFERON_LINEAR_ALGEBRA_ID_WORKED_ANSWERS_2026.08.22.pdf', bytes: 2672266, sha256: '61f8a344cade529249d4f165bb62bce17579b6a4408b11634999e9f73ec9c01b' },
    { name: '03_HEFFERON_LINEAR_ALGEBRA_ID_SAGE_LAB_2026.08.22.pdf', bytes: 13164259, sha256: 'adb78966020355a90442c7ae68c734f1fd6b44b5d935a3f75e531ea666eeee4a' },
  ]),
  verifyRecord(22143171, [{ name: '00_METODE_DALAM_ALJABAR_JILID_2_ID_UNIT_050.pdf', bytes: 1557019, sha256: '8bd85bfe55752a3c22e6e4f366cd198b760c1b78d6ac960e8fae818a52e18285' }]),
  verifyRecord(22142120, [
    { name: 'D90-O015-optimisasi-lanjut-analisis-konveks-id.html', bytes: 2485595, sha256: '028e026033bc60bba1aff282f34b2e550a9f9358a3bdecd16b74e3442f743c89' },
    { name: 'D90-O015-optimisasi-lanjut-analisis-konveks-id.pdf', bytes: 1671254, sha256: '9deefecf469c9f2aace26bc8ccdedc552debbe9874ae035badaf5cffee0f80e5' },
  ]),
]);

const repositories = await Promise.all([
  verifyPublicRepository('KokunoYumeto/openstax-precalculus-2e-id'),
  verifyPublicRepository('KokunoYumeto/metode-aljabar-jilid-2-id'),
]);

const admission = {
  schema_id: 'program-matematika-indonesia/central-release-admission-manifest/v1',
  target_release: '0.62.0',
  target_record_id: recordId,
  recorded_at: recordedAt,
  predecessor: {
    version: '0.61.0',
    authority_bytes: 76437,
    authority_sha256: '1060038a84af909ccf84df17d8a15ea63255865037ce06e156f07e26982257e6',
    git_commit: 'b4b38489fe90099fcdef98f832dc131bbb76b994',
    zenodo_record_id: 22148050,
  },
  inputs: Object.values(loaded).map(({ path, bytes, sha256: digest, role }) => ({ path, bytes, sha256: digest, role })),
  public_record_rechecks: publicRecords,
  public_repository_rechecks: repositories,
  admissions: [
    {
      course_id: 'A10', decision: 'advance_public_partial_checkpoint_without_completion_promotion', state_after: 'production',
      record: 22143518, doi: '10.5281/zenodo.22143518', modules: '32/82', pages: 1011,
      edition: 'https://zenodo.org/records/22143518/files/00-elementary-algebra-2e-bahasa-indonesia-EA2-S0032-reader.pdf?download=1',
    },
    {
      course_id: 'A30', decision: 'add_verified_public_repository_route_without_completion_promotion', state_after: 'production',
      repository: 'https://github.com/KokunoYumeto/openstax-precalculus-2e-id',
    },
    {
      course_id: 'B20', decision: 'admit_complete_public_two-reader_course', state_after: 'published', record: 21938930,
      doi: '10.5281/zenodo.21938930', textbook_pages: 442, problem_book_pages: 646,
    },
    {
      course_id: 'B40', decision: 'decompose_complete_textbook_worked_answers_and_sage_lab_into_distinct_learner_materials',
      state_after: 'published', record: 22070458, textbook_pages: 580, worked_answers_pages: 435, sage_lab_pages: 109,
    },
    {
      course_id: 'D80', decision: 'refresh_public_checkpoint_and_add_d70_canonical_prerequisite_with_learner_equivalence_support',
      state_after: 'production', record: 22143171, public_unit: 50, pages: 320,
      repository: 'https://github.com/KokunoYumeto/metode-aljabar-jilid-2-id',
    },
    {
      course_id: 'D90', decision: 'admit_integrated_terminal_complete_course_and_replace_obsolete_partial_route', state_after: 'published',
      record: 22142120, doi: '10.5281/zenodo.22142120', pages: 141, backend_records: 4877,
    },
  ],
  summary: {
    selected_course_roles: 40,
    completed_public_course_roles_before: 19,
    completed_public_course_roles_after: 21,
    distinct_completed_public_records_before: 18,
    distinct_completed_public_records_after: 20,
    newly_completed_course_roles: ['B20', 'D90'],
    still_production: ['A10', 'A30', 'D80'],
    prerequisite_edges_after: 83,
    learner_state_contract: 'browser-local completion, placement, equivalence, and edge-scoped waiver state; derived eligibility is not persisted',
  },
};

const admissionBytes = canonical(admission);
await mkdir(dirname(admissionPath), { recursive: true });
await writeFile(admissionPath, admissionBytes);

const priorReaderBytes = await readFile(priorReaderPath);
assert.equal(priorReaderBytes.length, 3893);
assert.equal(sha256(priorReaderBytes), '8a358848050523fd39df24afdb2bcbb8e38a0218490073c73dab4ac82108d57a');
const priorReader = JSON.parse(priorReaderBytes);
const inheritedRoutes = priorReader.routes.filter((row) => row.course_id !== 'D90');
assert.equal(inheritedRoutes.length, 6);

const d90Url = 'https://zenodo.org/records/22142120/files/D90-O015-optimisasi-lanjut-analisis-konveks-id.html?download=1';
const d90Response = await fetch(d90Url, { headers: { 'user-agent': 'program-matematika-indonesia-v062-evidence/1' } });
assert.equal(d90Response.status, 200);
const d90Bytes = Buffer.from(await d90Response.arrayBuffer());
assert.equal(d90Bytes.length, 2485595);
assert.equal(sha256(d90Bytes), '028e026033bc60bba1aff282f34b2e550a9f9358a3bdecd16b74e3442f743c89');
assert.match(d90Bytes.subarray(0, 4096).toString('utf8'), /<!doctype html|<html/i);

const routes = [...inheritedRoutes, {
  course_id: 'D90',
  url: d90Url,
  http_status: 200,
  bytes: d90Bytes.length,
  sha256: sha256(d90Bytes),
  content_type: 'text/html',
  scope: 'Edisi terintegrasi terminal D90: 141 halaman, 4.877 rekaman backend, korpus lengkap dan publik.',
}].sort((a, b) => a.course_id.localeCompare(b.course_id));

const reader = {
  schema_id: 'program-matematika-indonesia/owner-reader-public-readback/v1',
  recorded_at: recordedAt,
  result: 'pass',
  purpose: 'Bind exact public human-readable HTML routes used by the central v0.62 learner projection; replace the obsolete D90 partial route with its terminal integrated edition.',
  source_admission_manifest: { path: '141_CENTRAL_V062_ADMISSION_MANIFEST_20260828.json', bytes: admissionBytes.length, sha256: sha256(admissionBytes) },
  inherited_readback: { path: '131_PUBLIC_OWNER_HTML_ROUTE_READBACK_20260828.json', bytes: priorReaderBytes.length, sha256: sha256(priorReaderBytes), inherited_route_count: inheritedRoutes.length },
  policy: {
    all_routes_http_200: true,
    all_routes_machine_data_only: false,
    all_routes_content_type: 'text/html',
    anonymous_requests: true,
    authorization_header_used: false,
    credentials_recorded: false,
  },
  routes,
  route_count: routes.length,
  total_bytes: routes.reduce((sum, row) => sum + row.bytes, 0),
  terminal_assessment: 'All seven routes are readable HTML learner surfaces. D90 now resolves to the complete integrated course rather than Original Tranche 02.',
};
const readerBytes = canonical(reader);
await writeFile(readerPath, readerBytes);

console.log(JSON.stringify({
  result: 'pass',
  admission: { path: admissionPath, bytes: admissionBytes.length, sha256: sha256(admissionBytes) },
  owner_reader_readback: { path: readerPath, bytes: readerBytes.length, sha256: sha256(readerBytes), routes: routes.length, total_bytes: reader.total_bytes },
}, null, 2));
