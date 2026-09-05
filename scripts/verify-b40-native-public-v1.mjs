import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const output = resolve(project, 'backend/course-capsule-v1/adapters/b40-capability-v1/input/public-native-readback.json');
const repository = 'https://github.com/KokunoYumeto/hefferon-linear-algebra-id';
const api = 'https://api.github.com/repos/KokunoYumeto/hefferon-linear-algebra-id';
const rawBase = 'https://raw.githubusercontent.com/KokunoYumeto/hefferon-linear-algebra-id';
const currentHead = 'e84ce2956a7304830c42eba70106f940fefee7c4';
const currentTree = 'b434745225bb3931d51d107d8d8e5c0c8707af5d';
const releaseTag = 'v2026.08.22';
const zenodoRecordId = 22070458;
const zenodoDoi = '10.5281/zenodo.22070458';
const zenodoConceptRecordId = 22070457;
const zenodoConceptDoi = '10.5281/zenodo.22070457';

const releaseAssets = {
  '01_HEFFERON_LINEAR_ALGEBRA_ID_TEXTBOOK_2026.08.22.pdf': {
    bytes: 8984459,
    sha256: '0462ddc8ffcc901efbc81205f79a249ae716e838a6ec32eda033444a90b8755e',
    pages: 580,
  },
  '02_HEFFERON_LINEAR_ALGEBRA_ID_WORKED_ANSWERS_2026.08.22.pdf': {
    bytes: 2672266,
    sha256: '61f8a344cade529249d4f165bb62bce17579b6a4408b11634999e9f73ec9c01b',
    pages: 435,
  },
  '03_HEFFERON_LINEAR_ALGEBRA_ID_SAGE_LAB_2026.08.22.pdf': {
    bytes: 13164259,
    sha256: 'adb78966020355a90442c7ae68c734f1fd6b44b5d935a3f75e531ea666eeee4a',
    pages: 109,
  },
  'HEFFERON_LINEAR_ALGEBRA_ID_EDITABLE_SOURCE_2026.08.22.zip': {
    bytes: 117074300,
    sha256: '33f679be85fe1af6eb97e7d203a8389fd51beced9d41facc453e6162ad90a2c1',
  },
  'HEFFERON_LINEAR_ALGEBRA_ID_MODULAR_BACKEND_2026.08.22.zip': {
    bytes: 6118023,
    sha256: 'e3d66b5d19c79bb10243ac552f16165da897d40615467696452e3a64d0b92df2',
  },
  'HEFFERON_LINEAR_ALGEBRA_ID_PROVENANCE_QA_2026.08.22.zip': {
    bytes: 17025794,
    sha256: 'b76e7eeff732661691e33e07735022aaef7b825dfee3e7c6565aa6697cfc1ada',
  },
  'README_RELEASE_2026.08.22.md': {
    bytes: 2075,
    sha256: 'b35010b03ce4d37ff4f8f8d6d699c49e19df32366ac26eae10c2ca23480a51fe',
  },
  'release-manifest.json': {
    bytes: 5665,
    sha256: 'e1e9f1cec122d6a29d0dd90d507b0447d5c047b8720e8f62f59722657af80dde',
  },
  SHA256SUMS: {
    bytes: 919,
    sha256: '09bcdfe11272dea3b8916e59ef9dece50c666f68b5c00468795bfe8e568bfc8c',
  },
};

const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const canonical = value => `${JSON.stringify(value, null, 2)}\n`;
const decode = bytes => new TextDecoder().decode(bytes);
const jsonLines = bytes => decode(bytes).split(/\r?\n/u).filter(Boolean).map(line => JSON.parse(line));

async function fetchBytes(url, {method = 'GET', accept = '*/*'} = {}) {
  const response = await fetch(url, {
    method,
    redirect: 'follow',
    cache: 'no-store',
    signal: AbortSignal.timeout(180000),
    headers: {'accept': accept, 'user-agent': 'interlanguage-b40-public-verifier/1'},
  });
  assert.equal(response.status, 200, `${method} ${url} returned ${response.status}`);
  const bytes = method === 'HEAD' ? new Uint8Array() : new Uint8Array(await response.arrayBuffer());
  return {response, bytes};
}

async function fetchJson(url) {
  const {response, bytes} = await fetchBytes(url, {accept: 'application/vnd.github+json, application/json'});
  return {response, value: JSON.parse(decode(bytes)), bytes};
}

const commitFetch = await fetchJson(`${api}/commits/main`);
assert.equal(commitFetch.value.sha, currentHead, 'B40 public main moved; audit before changing the lock');
assert.equal(commitFetch.value.commit.tree.sha, currentTree, 'B40 public tree moved; audit before changing the lock');

const repositoryFetch = await fetchJson(api);
assert.equal(repositoryFetch.value.private, false);
assert.equal(repositoryFetch.value.visibility, 'public');
assert.equal(repositoryFetch.value.default_branch, 'main');

const fetchRaw = async path => {
  const url = `${rawBase}/${currentHead}/${path}`;
  const {bytes} = await fetchBytes(url);
  return {path, url, bytes, identity: {path, url, status: 200, bytes: bytes.length, sha256: sha256(bytes)}};
};

const manifestRaw = await fetchRaw('backend/manifest.json');
const manifest = JSON.parse(decode(manifestRaw.bytes));
assert.equal(manifest.schema, 'hefferon-modular-backend');
assert.equal(manifest.schema_version, '0.5.2');
assert.equal(manifest.generated_file_count, 15);
assert.equal(manifest.files.length, 15);
assert.equal(new Set(manifest.files.map(row => row.path)).size, 15);

const nativeFiles = [];
const rawValues = new Map();
for (const expected of manifest.files) {
  const fetched = await fetchRaw(`backend/${expected.path}`);
  assert.equal(fetched.bytes.length, expected.bytes, `${expected.path}: public byte count drift`);
  assert.equal(sha256(fetched.bytes), expected.sha256, `${expected.path}: public SHA-256 drift`);
  nativeFiles.push(fetched.identity);
  rawValues.set(expected.path, fetched.bytes);
}

const supportingRawPaths = [
  'README.md',
  'backend/README.md',
  'publication/README_RELEASE_2026.08.22.md',
  'publication/release-manifest.json',
  'publication/SHA256SUMS',
];
const supportingRaw = [];
for (const path of supportingRawPaths) supportingRaw.push((await fetchRaw(path)).identity);

const units = jsonLines(rawValues.get('units.jsonl'));
const concepts = jsonLines(rawValues.get('concepts.jsonl'));
const terms = jsonLines(rawValues.get('terminology.jsonl'));
const corrections = jsonLines(rawValues.get('corrections.jsonl'));
const rights = jsonLines(rawValues.get('rights.jsonl'));
const artifacts = jsonLines(rawValues.get('artifacts.jsonl'));
const courses = jsonLines(rawValues.get('courses.jsonl'));
const programs = jsonLines(rawValues.get('programs.jsonl'));
const authorities = jsonLines(rawValues.get('authority.jsonl'));
const segments = jsonLines(rawValues.get('segments.jsonl'));
const assets = jsonLines(rawValues.get('assets.jsonl'));
const qaEvents = jsonLines(rawValues.get('qa_events.jsonl'));
const interoperability = JSON.parse(decode(rawValues.get('interoperability.json')));
const sourceClosure = JSON.parse(decode(rawValues.get('source_closure.json')));

assert.equal(courses.length, 1);
assert.equal(courses[0].course_role, 'B40');
assert.equal(courses[0].target_title, 'Aljabar Linear');
assert.equal(programs.length, 1);
assert.equal(authorities.length, 3);
assert.equal(units.length, 3541);
assert.equal(segments.length, 3528);
assert.equal(concepts.length, 114);
assert.equal(terms.length, 114);
assert.equal(corrections.length, 307);
assert.equal(rights.length, 11);
assert.equal(artifacts.length, 8);
assert.equal(assets.length, 432);
assert.equal(qaEvents.length, 72);
assert.equal(sourceClosure.files.length, 64);
assert.equal(sourceClosure.assets.length, 432);
assert.equal(interoperability.exercise_answer_model.deliverable_answer_count, 1037);
assert.equal(interoperability.exercise_answer_model.deliverable_unanswered_exercise_count, 0);
assert.equal(interoperability.exercise_answer_model.native_upstream_answer_count, 1035);
assert.equal(interoperability.exercise_answer_model.target_supplied_answer_count, 2);

const unitsById = new Map(units.map(row => [row.id, row]));
assert.equal(unitsById.size, 3541);
const exerciseUnits = units.filter(row => row.unit_kind === 'exercise');
const answerUnits = units.filter(row => row.unit_kind === 'answer');
assert.equal(exerciseUnits.length, 1037);
assert.equal(answerUnits.length, 1037);
assert.equal(new Set(answerUnits.map(row => row.answers_unit_id)).size, 1037);
assert.ok(answerUnits.every(row => unitsById.get(row.answers_unit_id)?.unit_kind === 'exercise'));
const targetSupplied = answerUnits.filter(row => row.provenance_kind === 'indonesian_edition_supplied');
assert.equal(targetSupplied.length, 2);
assert.ok(targetSupplied.every(row => row.answer_link_status === 'linked_target_supplied'));
assert.ok(targetSupplied.every(row => row.authority_answer_status === 'absent_from_pinned_source_and_official_answer_book'));

const relationCounts = {};
const answerRelations = [];
const relationLines = decode(rawValues.get('relations.csv')).split(/\r?\n/u).filter(Boolean);
assert.equal(relationLines.shift(), 'relation_id,relation_type,source_id,target_id,order,source_locator,edition_id,rights_id,schema,schema_version,status,recorded_on,responsible_workflow,supersedes');
for (const line of relationLines) {
  const [relationId, relationType, sourceId, targetId] = line.split(',', 4);
  relationCounts[relationType] = (relationCounts[relationType] ?? 0) + 1;
  if (relationType === 'answers') answerRelations.push({relation_id: relationId, source_id: sourceId, target_id: targetId});
}
assert.equal(relationLines.length, 13999);
assert.deepEqual(relationCounts, {
  adapts: 3,
  answers: 1037,
  contains: 7178,
  corrects: 324,
  'depends-on': 368,
  exercises: 2208,
  precedes: 2273,
  translates: 114,
  xref: 494,
});
assert.equal(new Set(answerRelations.map(row => row.source_id)).size, 1037);
assert.equal(new Set(answerRelations.map(row => row.target_id)).size, 1037);
assert.ok(answerRelations.every(row => unitsById.get(row.source_id)?.unit_kind === 'answer'));
assert.ok(answerRelations.every(row => unitsById.get(row.target_id)?.unit_kind === 'exercise'));
assert.ok(answerRelations.every(row => unitsById.get(row.source_id)?.answers_unit_id === row.target_id));

const expectedReaders = [
  ['main-textbook', 580, releaseAssets['01_HEFFERON_LINEAR_ALGEBRA_ID_TEXTBOOK_2026.08.22.pdf']],
  ['answer-book-shell', 435, releaseAssets['02_HEFFERON_LINEAR_ALGEBRA_ID_WORKED_ANSWERS_2026.08.22.pdf']],
  ['sage-lab', 109, releaseAssets['03_HEFFERON_LINEAR_ALGEBRA_ID_SAGE_LAB_2026.08.22.pdf']],
];
for (const [component, pages, released] of expectedReaders) {
  const artifact = artifacts.find(row => row.locale === 'id-ID' && row.corpus_component === component && row.artifact_kind === 'reader_pdf');
  assert.ok(artifact, `missing native ${component} reader`);
  assert.equal(artifact.page_count, pages);
  assert.equal(artifact.bytes, released.bytes);
  assert.equal(artifact.sha256, released.sha256);
  assert.equal(artifact.build_status, 'success');
  assert.equal(artifact.build_receipt.reproducibility_verified, true);
}

const releaseFetch = await fetchJson(`${api}/releases/tags/${releaseTag}`);
assert.equal(releaseFetch.value.draft, false);
assert.equal(releaseFetch.value.prerelease, false);
const actualAssets = Object.fromEntries(releaseFetch.value.assets.map(asset => [asset.name, asset]));
assert.deepEqual(Object.keys(actualAssets).sort(), Object.keys(releaseAssets).sort());
const releaseRows = [];
for (const [name, expected] of Object.entries(releaseAssets).sort(([a], [b]) => a.localeCompare(b))) {
  const asset = actualAssets[name];
  assert.equal(asset.size, expected.bytes, `${name}: GitHub release size drift`);
  releaseRows.push({name, bytes: asset.size, sha256: expected.sha256, pages: expected.pages ?? null, url: asset.browser_download_url});
}

const headOnlyNames = ['HEFFERON_LINEAR_ALGEBRA_ID_EDITABLE_SOURCE_2026.08.22.zip'];
const fullReleaseReadbacks = [];
const headReleaseReadbacks = [];
for (const [name, expected] of Object.entries(releaseAssets)) {
  if (headOnlyNames.includes(name)) {
    const {response} = await fetchBytes(actualAssets[name].browser_download_url, {method: 'HEAD'});
    headReleaseReadbacks.push({name, status: response.status, final_url_host: new URL(response.url).host, expected_bytes: expected.bytes, expected_sha256: expected.sha256});
    continue;
  }
  const {bytes} = await fetchBytes(actualAssets[name].browser_download_url);
  assert.equal(bytes.length, expected.bytes, `${name}: public bytes drift`);
  assert.equal(sha256(bytes), expected.sha256, `${name}: public SHA-256 drift`);
  fullReleaseReadbacks.push({name, status: 200, bytes: bytes.length, sha256: sha256(bytes)});
}

const zenodoFetch = await fetchJson(`https://zenodo.org/api/records/${zenodoRecordId}`);
assert.equal(zenodoFetch.value.id, zenodoRecordId);
assert.equal(zenodoFetch.value.doi, zenodoDoi);
assert.equal(Number(zenodoFetch.value.conceptrecid), zenodoConceptRecordId);
assert.equal(zenodoFetch.value.conceptdoi, zenodoConceptDoi);
assert.equal(zenodoFetch.value.metadata.access_right, 'open');
assert.equal(zenodoFetch.value.status, 'published');
const zenodoFiles = zenodoFetch.value.files.map(file => ({name: file.key, bytes: file.size, checksum: file.checksum})).sort((a, b) => a.name.localeCompare(b.name));
assert.deepEqual(
  zenodoFiles.map(row => row.name),
  Object.keys(releaseAssets).sort((a, b) => a.localeCompare(b)),
);
for (const [name, expected] of Object.entries(releaseAssets)) {
  const file = zenodoFiles.find(row => row.name === name);
  assert.equal(file.bytes, expected.bytes, `${name}: Zenodo size drift`);
}

const pagesUrl = 'https://kokunoyumeto.github.io/hefferon-linear-algebra-id/';
const pagesFetch = await fetchBytes(pagesUrl, {accept: 'text/html'});
const pagesText = decode(pagesFetch.bytes).toLowerCase();
assert.match(pagesText.slice(0, 1200), /<!doctype html|<html/u);
assert.match(pagesText, /aljabar linear|linear algebra/u);

const receipt = {
  schema: 'b40-native-public-readback/1',
  course_id: 'B40',
  native_role_id: 'R005',
  verified_date: '2026-09-05',
  access_mode: 'anonymous_no_credentials',
  github: {
    repository,
    current_head: currentHead,
    current_tree: currentTree,
    repository_public: true,
    current_commit_api: {status: 200, bytes: commitFetch.bytes.length, sha256: sha256(commitFetch.bytes)},
    native_backend_manifest: manifestRaw.identity,
    native_backend_files: nativeFiles,
    supporting_raw_files: supportingRaw,
    release: {
      tag: releaseTag,
      url: releaseFetch.value.html_url,
      assets: releaseRows,
      fully_downloaded_and_sha256_verified: fullReleaseReadbacks,
      large_asset_anonymous_head_checks: headReleaseReadbacks,
    },
  },
  zenodo: {
    record_id: zenodoRecordId,
    doi: zenodoDoi,
    concept_record_id: zenodoConceptRecordId,
    concept_doi: zenodoConceptDoi,
    status: 'published',
    access_right: 'open',
    files: zenodoFiles,
  },
  reader: {
    url: pagesUrl,
    status: 200,
    bytes: pagesFetch.bytes.length,
    sha256: sha256(pagesFetch.bytes),
    scope: 'release_landing_page_not_full_html_textbook',
  },
  native_backend: {
    schema: manifest.schema,
    schema_version: manifest.schema_version,
    manifest_members_verified: nativeFiles.length,
    counts: {
      native_records_total: 22131,
      entity_records_excluding_csv_relations: 8132,
      units: units.length,
      segments: segments.length,
      concepts: concepts.length,
      terms: terms.length,
      corrections: corrections.length,
      relations: relationLines.length,
      relation_types: relationCounts,
      assets: assets.length,
      rights: rights.length,
      artifacts: artifacts.length,
      qa_events: qaEvents.length,
      exercises: exerciseUnits.length,
      answers: answerUnits.length,
      native_upstream_answers: answerUnits.length - targetSupplied.length,
      indonesian_edition_supplied_answers: targetSupplied.length,
      unanswered_exercises: exerciseUnits.length - new Set(answerRelations.map(row => row.target_id)).size,
      source_files: sourceClosure.files.length,
    },
    source_closure_sha256: sourceClosure.closure_sha256,
    interoperability_sha256: sha256(rawValues.get('interoperability.json')),
    stable_identity_contract: interoperability.identity_contract,
    target_supplied_answer_units: targetSupplied.map(row => ({
      unit_id: row.id,
      exercise_unit_id: row.answers_unit_id,
      provenance_kind: row.provenance_kind,
      authority_answer_status: row.authority_answer_status,
      authorization_event_id: row.authorization_event_id,
      authorization_correction_id: row.authorization_correction_id,
      authorization_ledger_locator: row.authorization_ledger_locator,
      authorization_ledger_sha256: row.authorization_ledger_sha256,
      target_locator: row.target_locator,
      target_sha256: row.target_sha256,
    })),
  },
  checks: {
    exact_commit_and_tree: true,
    native_backend_manifest_hash_closure: true,
    immutable_native_files_fetched: nativeFiles.length,
    github_release_asset_inventory_exact: true,
    full_release_artifacts_sha256_verified: fullReleaseReadbacks.length,
    large_release_artifacts_anonymously_available: headReleaseReadbacks.length,
    zenodo_record_open_and_inventory_exact: true,
    exercise_answer_bijection_verified: true,
    target_supplied_answer_provenance_preserved: true,
    reader_landing_page_fetched: true,
    external_state_changed: false,
  },
  credentials_recorded: false,
};

await mkdir(dirname(output), {recursive: true});
await writeFile(output, canonical(receipt));
console.log(JSON.stringify({
  state: 'pass',
  output,
  bytes: Buffer.byteLength(canonical(receipt)),
  sha256: sha256(Buffer.from(canonical(receipt))),
  native_files: nativeFiles.length,
  release_files_fully_verified: fullReleaseReadbacks.length,
  release_files_head_verified: headReleaseReadbacks.length,
  exercise_answer_pairs: answerRelations.length,
}));
