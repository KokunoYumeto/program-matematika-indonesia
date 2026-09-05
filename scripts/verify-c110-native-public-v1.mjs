import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const nativeRoot = resolve(root, '..', 'tea-time-numerical-analysis-id');
const output = resolve(root, 'backend/course-capsule-v1/adapters/c110-capability-v1/input/public-native-readback.json');
const repository = 'https://github.com/KokunoYumeto/tea-time-numerical-analysis-id';
const ownerRepo = 'KokunoYumeto/tea-time-numerical-analysis-id';
const commit = 'cf4a425918b6555d3157001bfa7c18acc1f97026';
const treeSha = '32004a75627e8cd0401fec5c855663c37a0848fe';
const zenodoRecordId = 22075088;
const sha256 = data => createHash('sha256').update(data).digest('hex');
const identity = async (path, displayPath = path) => {
  const data = await readFile(resolve(nativeRoot, path));
  return {path: displayPath, bytes: data.length, sha256: sha256(data)};
};
const fetchBytes = async url => {
  const response = await fetch(url, {headers: {'User-Agent': 'Codex-C110-public-byte-verifier/1'}});
  assert.equal(response.status, 200, `${url}: HTTP ${response.status}`);
  return Buffer.from(await response.arrayBuffer());
};
const fetchJson = async url => JSON.parse((await fetchBytes(url)).toString('utf8'));
const encodePath = path => path.split('/').map(encodeURIComponent).join('/');

const lane = JSON.parse(await readFile(resolve(nativeRoot, 'backend/manifests/lane_manifest.json'), 'utf8'));
const releaseReceipt = JSON.parse(await readFile(resolve(nativeRoot, 'publication/RELEASE_PUBLICATION_RECEIPT_v3.0-id.2-r1.json'), 'utf8'));
const publicToLocal = new Map([
  ...lane.files.map(row => [`backend/${row.path}`, `backend/${row.path}`]),
  ['backend/manifests/lane_manifest.json', 'backend/manifests/lane_manifest.json'],
  ['backend/exports/interoperability-v0/manifest.json', 'backend/exports/interoperability-v0/manifest.json'],
  ['backend/exports/interoperability-v0/records.jsonl', 'backend/exports/interoperability-v0/records.jsonl'],
  ['backend/exports/interoperability-v0/records.csv', 'backend/exports/interoperability-v0/records.csv'],
  ['backend/schema/record.schema.json', 'backend/schema/record.schema.json'],
  ['output/pdf/Tea-Time-Numerical-Analysis-id-ID.pdf', 'output/pdf/Tea-Time-Numerical-Analysis-id-ID.pdf'],
  ['COMPONENT_RIGHTS_AND_PROVENANCE.md', 'publication/COMPONENT_RIGHTS_AND_PROVENANCE.md'],
]);
assert.equal(publicToLocal.size, 26);

const commitRecord = await fetchJson(`https://api.github.com/repos/${ownerRepo}/commits/main`);
assert.equal(commitRecord.sha, commit, 'C110 public main changed; audit the new head before integration');
assert.equal(commitRecord.commit.tree.sha, treeSha, 'C110 public tree changed');
const treeRecord = await fetchJson(`https://api.github.com/repos/${ownerRepo}/git/trees/${treeSha}?recursive=1`);
assert.equal(treeRecord.truncated, false);
const publicTree = new Map(treeRecord.tree.filter(row => row.type === 'blob').map(row => [row.path, row]));

const githubFiles = [];
for (const [publicPath, localPath] of [...publicToLocal].sort(([left], [right]) => left.localeCompare(right))) {
  const local = await identity(localPath, publicPath);
  const treeEntry = publicTree.get(publicPath);
  assert.ok(treeEntry, `${publicPath}: absent from public tree`);
  assert.equal(treeEntry.size, local.bytes, `${publicPath}: Git tree byte count drift`);
  const rawUrl = `https://raw.githubusercontent.com/${ownerRepo}/${commit}/${encodePath(publicPath)}`;
  const publicBytes = await fetchBytes(rawUrl);
  const actual = {path: publicPath, bytes: publicBytes.length, sha256: sha256(publicBytes), raw_url: rawUrl};
  assert.deepEqual({path: actual.path, bytes: actual.bytes, sha256: actual.sha256}, local, `${publicPath}: public bytes differ from native evidence`);
  githubFiles.push(actual);
}
const githubInventory = Buffer.from(githubFiles.map(row => `${row.path}\t${row.bytes}\t${row.sha256}\n`).join(''), 'utf8');

const zenodo = await fetchJson(`https://zenodo.org/api/records/${zenodoRecordId}`);
assert.equal(zenodo.id, zenodoRecordId);
assert.equal(zenodo.doi, '10.5281/zenodo.22075088');
assert.equal(zenodo.conceptdoi, '10.5281/zenodo.22054085');
assert.equal(zenodo.metadata.access_right, 'open');
const expectedZenodo = new Map(releaseReceipt.artifacts.map(row => [row.name, row]));
assert.equal(expectedZenodo.size, 4);
assert.equal(zenodo.files.length, 4);
const zenodoFiles = [];
for (const file of [...zenodo.files].sort((left, right) => left.key.localeCompare(right.key))) {
  const expected = expectedZenodo.get(file.key);
  assert.ok(expected, `${file.key}: unexpected Zenodo file`);
  assert.equal(file.size, expected.bytes, `${file.key}: Zenodo metadata byte drift`);
  const data = await fetchBytes(file.links.self);
  const actual = {name: file.key, bytes: data.length, sha256: sha256(data), download_url: file.links.self};
  assert.equal(actual.bytes, expected.bytes, `${file.key}: Zenodo byte count drift`);
  assert.equal(actual.sha256, expected.sha256, `${file.key}: Zenodo SHA-256 drift`);
  zenodoFiles.push(actual);
}
const zenodoInventory = Buffer.from(zenodoFiles.map(row => `${row.name}\t${row.bytes}\t${row.sha256}\n`).join(''), 'utf8');

const receipt = {
  schema: 'c110-native-public-readback/1',
  course_id: 'C110',
  verified_date: '2026-09-05',
  access_mode: 'anonymous_no_credentials',
  github: {
    repository,
    release: `${repository}/releases/tag/v3.0-id.2-r1`,
    commit,
    tree: treeSha,
    tree_truncated: false,
    public_blob_count: publicTree.size,
    files: githubFiles,
    verified_files: githubFiles.length,
    verified_bytes: githubFiles.reduce((sum, row) => sum + row.bytes, 0),
    inventory_bytes: githubInventory.length,
    inventory_sha256: sha256(githubInventory),
  },
  zenodo: {
    record_id: zenodoRecordId,
    url: `https://zenodo.org/records/${zenodoRecordId}`,
    doi: zenodo.doi,
    concept_doi: zenodo.conceptdoi,
    access_right: zenodo.metadata.access_right,
    files: zenodoFiles,
    verified_files: zenodoFiles.length,
    verified_bytes: zenodoFiles.reduce((sum, row) => sum + row.bytes, 0),
    inventory_bytes: zenodoInventory.length,
    inventory_sha256: sha256(zenodoInventory),
  },
  checks: {
    public_main_and_tree_exact: true,
    github_all_expected_files_byte_and_sha256_exact: true,
    zenodo_open_access: true,
    zenodo_all_files_byte_and_sha256_exact: true,
    credentials_used: false,
    external_state_changed: false,
  },
};
await mkdir(dirname(output), {recursive: true});
await writeFile(output, `${JSON.stringify(receipt, null, 2)}\n`);
console.log(JSON.stringify({
  state: 'pass',
  github_files: receipt.github.verified_files,
  github_bytes: receipt.github.verified_bytes,
  github_inventory_sha256: receipt.github.inventory_sha256,
  zenodo_files: receipt.zenodo.verified_files,
  zenodo_bytes: receipt.zenodo.verified_bytes,
  zenodo_inventory_sha256: receipt.zenodo.inventory_sha256,
  output: 'backend/course-capsule-v1/adapters/c110-capability-v1/input/public-native-readback.json',
}, null, 2));
