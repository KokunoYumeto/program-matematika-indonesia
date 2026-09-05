import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const output = resolve(project, 'backend/course-capsule-v1/adapters/c70-capability-v1/input/public-native-readback.json');
const repository = 'https://github.com/KokunoYumeto/applied-combinatorics-id';
const api = 'https://api.github.com/repos/KokunoYumeto/applied-combinatorics-id';
const currentHead = '8c9615969a4c4e9316166f38ac827a932a87a919';
const currentTree = 'c538dacb6bb51f15cdacefffd473ec8899f677f3';
const releaseVersion = '2026.08.22.2';
const maintenanceVersion = '2026.09.04.1';
const releaseAssets = {
  '00_KOMBINATORIKA_TERAPAN_ID-ID_COMPLETE_LINKED_READER_2026.08.22.2.pdf': {
    bytes: 7487263,
    sha256: '6e0e3c0e3b42f283b551fc6c993acc4101d850edc0f350cbfe3c3e408f271e30',
  },
  '01_KOMBINATORIKA_TERAPAN_ID-ID_CORRESPONDING_SOURCE_2026.08.22.2.zip': {
    bytes: 236912440,
    sha256: '9e4dbdffc9878f97c69ff75e5a9de6e4607529e0390815380be090445f51d6bd',
  },
  '02_KOMBINATORIKA_TERAPAN_ID-ID_EVIDENCE_AND_PROVENANCE_2026.08.22.2.zip': {
    bytes: 3955527,
    sha256: 'e0ee361301d21b95e90dc73a2cf192849c37e883221efcfc75ca9e8dc5759b3f',
  },
  '03_KOMBINATORIKA_TERAPAN_ID-ID_HTML_READER_2026.08.22.2.zip': {
    bytes: 227102546,
    sha256: 'c6f1ace9b5c720421f1769dc3f92b0d692f067c15eb2950317092e24035e8c55',
  },
  '04_KOMBINATORIKA_TERAPAN_ID-ID_SHA256_MANIFEST_2026.08.22.2.txt': {
    bytes: 590,
    sha256: 'fd57577bd3fac0398251778142e6b93e69bfae9a3aa50b736729e9dacd519801',
  },
};
const rawPaths = [
  'README.md',
  'RELEASE_MANIFEST.json',
  'backend/exports/BACKEND_EXPORT_MANIFEST.csv',
  'evidence/QA_STATE.json',
  'evidence/SOURCE_AUTHORITY.json',
  'evidence/UNRESOLVED_ITEMS.tsv',
  'qa/FINAL_PUBLIC_HTML_BROWSER_QA_20260822_2.json',
  'qa/FINAL_PUBLIC_PDF_QA_20260822_2.json',
  'qa/FINAL_RIGHTS_PUBLICATION_READINESS_20260822_2.json',
  'terminology/TERMINOLOGY_DECISION_REVIEW_LOG.csv',
  'terminology/TERMINOLOGY_DECISION_REVIEW_GUIDE.md',
  'terminology/TERMINOLOGY_DECISION_REVIEW_VALIDATION.json',
];
const readerPaths = [
  '', 'ch_intro.html', 'ch_strings.html', 'ch_induction.html', 'ch_basics.html',
  'ch_graphs.html', 'ch_posets.html', 'ch_inclusion-exclusion.html',
  'ch_genfunction.html', 'ch_recurrence.html', 'ch_probability.html',
  'ch_probmeth.html', 'ch_graphalgorithms.html', 'ch_networkflow.html',
  'ch_flowapplications.html', 'ch_polya.html', 'ch_kitchensink.html',
  'ch_epilogue.html', 'app_background.html',
];
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const canonical = value => `${JSON.stringify(value, null, 2)}\n`;

async function fetchBytes(url, {method = 'GET', accept = '*/*'} = {}) {
  const response = await fetch(url, {
    method,
    redirect: 'follow',
    cache: 'no-store',
    headers: {'accept': accept, 'user-agent': 'interlanguage-c70-public-verifier/1'},
  });
  assert.equal(response.status, 200, `${method} ${url} returned ${response.status}`);
  const bytes = method === 'HEAD' ? new Uint8Array() : new Uint8Array(await response.arrayBuffer());
  return {response, bytes};
}

async function fetchJson(url) {
  const {bytes} = await fetchBytes(url, {accept: 'application/vnd.github+json, application/json'});
  return {value: JSON.parse(new TextDecoder().decode(bytes)), bytes};
}

const commitFetch = await fetchJson(`${api}/commits/main`);
assert.equal(commitFetch.value.sha, currentHead);
assert.equal(commitFetch.value.commit.tree.sha, currentTree);

const rawFiles = [];
const rawValues = new Map();
for (const path of rawPaths) {
  const url = `https://raw.githubusercontent.com/KokunoYumeto/applied-combinatorics-id/${currentHead}/${path}`;
  const {bytes} = await fetchBytes(url);
  rawFiles.push({path, url, bytes: bytes.length, sha256: sha256(bytes), status: 200});
  rawValues.set(path, bytes);
}

const releaseManifest = JSON.parse(new TextDecoder().decode(rawValues.get('RELEASE_MANIFEST.json')));
const qaState = JSON.parse(new TextDecoder().decode(rawValues.get('evidence/QA_STATE.json')));
const terminologyValidation = JSON.parse(new TextDecoder().decode(rawValues.get('terminology/TERMINOLOGY_DECISION_REVIEW_VALIDATION.json')));
assert.equal(releaseManifest.version, releaseVersion);
assert.equal(releaseManifest.coverage.known_partial_or_missing_scope.length, 0);
assert.equal(releaseManifest.coverage.translation_boundaries, 167);
assert.equal(releaseManifest.coverage.admitted_source_files, 171);
assert.equal(qaState.release_closed, true);
assert.equal(qaState.gates.backend_export_and_validation, 'pass');
assert.equal(terminologyValidation.result, 'pass');
assert.equal(terminologyValidation.coverage.registry_records, 633);
assert.equal(terminologyValidation.coverage.review_log_records, 633);
assert.equal(terminologyValidation.coverage.empty_required_cells, 0);
assert.equal(terminologyValidation.coverage.field_checked_rows, 12);

const releaseFetch = await fetchJson(`${api}/releases/tags/${releaseVersion}`);
assert.equal(releaseFetch.value.draft, false);
assert.equal(releaseFetch.value.prerelease, false);
const actualAssets = Object.fromEntries(releaseFetch.value.assets.map(asset => [asset.name, asset]));
assert.deepEqual(Object.keys(actualAssets).sort(), Object.keys(releaseAssets).sort());
const releaseRows = [];
for (const [name, expected] of Object.entries(releaseAssets).sort(([a], [b]) => a.localeCompare(b))) {
  const asset = actualAssets[name];
  assert.equal(asset.size, expected.bytes, `${name}: GitHub release size drift`);
  releaseRows.push({name, bytes: asset.size, sha256: expected.sha256, url: asset.browser_download_url});
}

const fullReadbackNames = [
  '00_KOMBINATORIKA_TERAPAN_ID-ID_COMPLETE_LINKED_READER_2026.08.22.2.pdf',
  '02_KOMBINATORIKA_TERAPAN_ID-ID_EVIDENCE_AND_PROVENANCE_2026.08.22.2.zip',
  '04_KOMBINATORIKA_TERAPAN_ID-ID_SHA256_MANIFEST_2026.08.22.2.txt',
];
const fullReleaseReadbacks = [];
for (const name of fullReadbackNames) {
  const {bytes} = await fetchBytes(actualAssets[name].browser_download_url);
  assert.equal(bytes.length, releaseAssets[name].bytes, `${name}: public bytes drift`);
  assert.equal(sha256(bytes), releaseAssets[name].sha256, `${name}: public SHA-256 drift`);
  fullReleaseReadbacks.push({name, bytes: bytes.length, sha256: sha256(bytes), status: 200});
}

const largeAssetAvailability = [];
for (const name of Object.keys(releaseAssets).filter(name => !fullReadbackNames.includes(name))) {
  const {response} = await fetchBytes(actualAssets[name].browser_download_url, {method: 'HEAD'});
  largeAssetAvailability.push({name, status: response.status, final_url_host: new URL(response.url).host});
}

const maintenanceFetch = await fetchJson(`${api}/releases/tags/${maintenanceVersion}`);
assert.equal(maintenanceFetch.value.draft, false);
assert.equal(maintenanceFetch.value.prerelease, false);

const zenodoRecords = [];
for (const id of [22062005, 22308618]) {
  const {value} = await fetchJson(`https://zenodo.org/api/records/${id}`);
  assert.equal(value.id, id);
  assert.equal(value.metadata.access_right, 'open');
  const files = value.files.map(file => ({name: file.key, bytes: file.size, checksum: file.checksum})).sort((a, b) => a.name.localeCompare(b.name));
  for (const [name, expected] of Object.entries(releaseAssets)) {
    const file = files.find(row => row.name === name);
    assert.ok(file, `${id}: missing ${name}`);
    assert.equal(file.bytes, expected.bytes, `${id}: ${name} size drift`);
  }
  if (id === 22308618) {
    assert.ok(files.some(row => row.name === '05_TERMINOLOGY_DECISION_REVIEW_LOG_2026.09.04.1.csv' && row.bytes === 1037985));
    assert.ok(files.some(row => row.name === '07_TERMINOLOGY_DECISION_REVIEW_VALIDATION_2026.09.04.1.json' && row.bytes === 1580));
  }
  zenodoRecords.push({id, doi: value.doi, access_right: value.metadata.access_right, files});
}

const readerPages = [];
for (const path of readerPaths) {
  const url = `https://kokunoyumeto.github.io/applied-combinatorics-id/${path}`;
  const {bytes} = await fetchBytes(url, {accept: 'text/html'});
  const text = new TextDecoder().decode(bytes);
  assert.match(text.slice(0, 1000).toLowerCase(), /<!doctype html|<html/u, `${url}: not HTML`);
  readerPages.push({path: path || 'index', url, status: 200, bytes: bytes.length, sha256: sha256(bytes)});
}

const receipt = {
  schema: 'c70-native-public-readback/1',
  course_id: 'C70',
  native_role_id: 'R012',
  verified_date: '2026-09-05',
  access_mode: 'anonymous_no_credentials',
  github: {
    repository,
    current_head: currentHead,
    current_tree: currentTree,
    current_commit_api: {status: 200, bytes: commitFetch.bytes.length, sha256: sha256(commitFetch.bytes)},
    raw_files: rawFiles,
    release: {version: releaseVersion, assets: releaseRows, fully_downloaded_and_sha256_verified: fullReleaseReadbacks, large_asset_anonymous_head_checks: largeAssetAvailability},
    maintenance_release: {version: maintenanceVersion, asset_count: maintenanceFetch.value.assets.length, status: 200},
  },
  zenodo: {records: zenodoRecords, all_open: true},
  reader: {base_url: 'https://kokunoyumeto.github.io/applied-combinatorics-id/', pages: readerPages},
  checks: {
    exact_commit_and_tree: true,
    immutable_raw_files_fetched: rawFiles.length,
    github_release_asset_inventory_exact: true,
    full_release_artifacts_sha256_verified: fullReleaseReadbacks.length,
    large_release_artifacts_anonymously_available: largeAssetAvailability.length,
    zenodo_records_open: zenodoRecords.length,
    reader_routes_fetched: readerPages.length,
    terminology_review_rows: 633,
    external_state_changed: false,
  },
  credentials_recorded: false,
};
await mkdir(dirname(output), {recursive: true});
await writeFile(output, canonical(receipt));
console.log(JSON.stringify({state: 'pass', output, bytes: Buffer.byteLength(canonical(receipt)), sha256: sha256(Buffer.from(canonical(receipt))), reader_routes: readerPages.length, raw_files: rawFiles.length}));
