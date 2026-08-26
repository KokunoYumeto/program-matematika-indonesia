import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const version = '0.58.0';
const recordId = 22105611;
const releaseDir = resolve(project, `releases/v${version}`);
const docs = resolve(project, 'docs');
const output = resolve(project, `PUBLICATION_RECEIPT_v${version}.json`);
const learnerSite = 'https://kokunoyumeto.github.io/program-matematika-indonesia/';
const githubRepository = 'https://github.com/KokunoYumeto/program-matematika-indonesia';
const githubRelease = `${githubRepository}/releases/tag/v${version}`;
const githubAssetBase = `${githubRepository}/releases/download/v${version}/`;
const zenodoApi = `https://zenodo.org/api/records/${recordId}`;

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
const delay = (milliseconds) => new Promise((resolveDelay) => setTimeout(resolveDelay, milliseconds));

async function fetchBytes(url, label) {
  let response;
  for (let attempt = 1; attempt <= 5; attempt += 1) {
    response = await fetch(url, {
      cache: 'no-store',
      headers: { 'user-agent': 'Program-Matematika-Indonesia-public-readback' },
    });
    if (response.status === 200) return Buffer.from(await response.arrayBuffer());
    await response.arrayBuffer();
    if (![429, 500, 502, 503, 504].includes(response.status) || attempt === 5) break;
    await delay(attempt * 1000);
  }
  assert.equal(response?.status, 200, `${label}: HTTP ${response?.status ?? 'no response'}`);
}

async function fetchJson(url, label) {
  const bytes = await fetchBytes(url, label);
  return JSON.parse(bytes.toString('utf8'));
}

const names = (await readdir(releaseDir, { withFileTypes: true }))
  .filter((entry) => entry.isFile())
  .map((entry) => entry.name)
  .sort();
assert.equal(names.length, 48, 'release inventory must contain exactly 48 files');

const localInventory = [];
for (const name of names) {
  const bytes = await readFile(resolve(releaseDir, name));
  localInventory.push({ name, bytes: bytes.length, sha256: sha256(bytes), body: bytes });
}

const d20Routes = JSON.parse(await readFile(resolve(docs, 'data/unit-route-D20-v2.1.json'), 'utf8'));
const siteNames = [
  'index.html', 'styles.css', 'app.js', 'courses.js', 'og.png', 'robots.txt', '.nojekyll',
  'data/curriculum-authority-v1.json', 'data/learner-read-model.json',
  'data/educational-access.json', 'schema/educational-access-federation-v1.schema.json',
  'data/unit-route-C100-v2.1.json', 'data/unit-route-D20-v2.1.json', 'data/unit-route-v2.1.json', 'data/unit-routes-v2.1.json',
  'id-ID/courses/C100/index.html', 'id-ID/courses/C100/reader/index.html', 'id-ID/courses/C100/reader/style.css',
  'id-ID/courses/C100/solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf',
  ...Array.from({ length: 20 }, (_, index) => `id-ID/courses/C100/units/bab-${String(index + 1).padStart(2, '0')}/index.html`),
  'id-ID/courses/D20/index.html',
  ...d20Routes.units.map(({ slug }) => `id-ID/courses/D20/units/${slug}/index.html`),
];
assert.equal(siteNames.length, 57);
const siteInventory = [];
for (const name of siteNames) {
  const local = await readFile(resolve(docs, name));
  const url = new URL(name === 'index.html' ? './' : name, learnerSite).href;
  const remote = await fetchBytes(url, `GitHub Pages ${name}`);
  assert.equal(remote.length, local.length, `${name}: GitHub Pages byte count differs`);
  assert.equal(sha256(remote), sha256(local), `${name}: GitHub Pages SHA-256 differs`);
  siteInventory.push({ name, bytes: local.length, sha256: sha256(local), url });
}
const siteBytes = siteInventory.reduce((sum, row) => sum + row.bytes, 0);
const siteAggregateSha256 = sha256(Buffer.from(siteInventory
  .map((row) => `${row.sha256}  ${row.name}`)
  .sort()
  .join('\n') + '\n', 'utf8'));

const zenodo = await fetchJson(zenodoApi, 'Zenodo public record');
assert.equal(zenodo.id, recordId);
assert.equal(zenodo.doi, `10.5281/zenodo.${recordId}`);
assert.equal(zenodo.conceptdoi, '10.5281/zenodo.22059707');
assert.equal(zenodo.metadata.version, version);
assert.equal(zenodo.metadata.access_right, 'open');
assert.equal(zenodo.files.length, 48);
const firstDescriptionHref = /href=["']([^"']+)["']/i.exec(zenodo.metadata.description)?.[1];
assert.equal(firstDescriptionHref, learnerSite);
assert.match(zenodo.metadata.description, /OpenAI Codex gpt-5\.6-sol, Ultra/);

const zenodoFiles = new Map(zenodo.files.map((file) => [file.key, file]));
assert.deepEqual([...zenodoFiles.keys()].sort(), names);

const payloadInventory = [];
for (const local of localInventory) {
  const githubUrl = `${githubAssetBase}${encodeURIComponent(local.name)}`;
  const zenodoFile = zenodoFiles.get(local.name);
  const [githubBytes, zenodoBytes] = await Promise.all([
    fetchBytes(githubUrl, `GitHub ${local.name}`),
    fetchBytes(zenodoFile.links.self, `Zenodo ${local.name}`),
  ]);
  assert.equal(githubBytes.length, local.bytes, `${local.name}: GitHub byte count differs`);
  assert.equal(zenodoBytes.length, local.bytes, `${local.name}: Zenodo byte count differs`);
  assert.equal(sha256(githubBytes), local.sha256, `${local.name}: GitHub SHA-256 differs`);
  assert.equal(sha256(zenodoBytes), local.sha256, `${local.name}: Zenodo SHA-256 differs`);
  payloadInventory.push({
    name: local.name,
    bytes: local.bytes,
    sha256: local.sha256,
    github_url: githubUrl,
    zenodo_url: zenodoFile.links.self,
    github_anonymous_byte_identity: true,
    zenodo_anonymous_byte_identity: true,
  });
}

const checksumManifest = localInventory.find((entry) => entry.name === 'CHECKSUMS.sha256');
const validationReceipt = localInventory.find((entry) => entry.name === 'LOCAL_RELEASE_VALIDATION_v0.58.0.json');
const sourcePackage = localInventory.find((entry) => entry.name === 'program-matematika-indonesia-source-v0.58.0.zip');
const backendV1 = localInventory.find((entry) => entry.name === 'program-matematika-indonesia-backend-v1-v0.58.0.zip');
const backendV2 = localInventory.find((entry) => entry.name === 'program-matematika-indonesia-backend-v2-v0.58.0.zip');
const backendV21 = localInventory.find((entry) => entry.name === 'program-matematika-indonesia-backend-v2.1-pilots-v0.58.0.zip');
const replayReceipt = localInventory.find((entry) => entry.name === 'GLOBAL_BACKEND_V21_DETERMINISTIC_REPLAY_RECEIPT_v0.58.0.json');
for (const required of [checksumManifest, validationReceipt, sourcePackage, backendV1, backendV2, backendV21, replayReceipt]) assert.ok(required);

const totalBytes = localInventory.reduce((sum, row) => sum + row.bytes, 0);
const aggregateSha256 = sha256(Buffer.from(payloadInventory
  .map((row) => `${row.sha256}  ${row.name}`)
  .sort()
  .join('\n') + '\n', 'utf8'));

const gh = JSON.parse(execFileSync('gh', [
  'release', 'view', `v${version}`,
  '--repo', 'KokunoYumeto/program-matematika-indonesia',
  '--json', 'url,publishedAt,isDraft,isPrerelease,tagName',
], { cwd: project, encoding: 'utf8' }));
assert.equal(gh.url, githubRelease);
assert.equal(gh.tagName, `v${version}`);
assert.equal(gh.isDraft, false);
assert.equal(gh.isPrerelease, false);

const authoritySourceCommit = execFileSync('git', ['rev-parse', 'HEAD~1'], { cwd: project, encoding: 'utf8' }).trim();
const taggedCommit = execFileSync('git', ['rev-parse', 'v0.58.0^{}'], { cwd: project, encoding: 'utf8' }).trim();
const tagObject = execFileSync('git', ['rev-parse', 'v0.58.0'], { cwd: project, encoding: 'utf8' }).trim();
assert.equal(taggedCommit, '135ca36d87885ee5eba1ee7f4e8f62d934925c0f');
assert.equal(authoritySourceCommit, '0c99da627df49e73a919b2383fcd75bd40f5af8b');

const receipt = {
  schema_id: 'program-matematika-indonesia/combined-publication-receipt/v14',
  title: 'Program Matematika Indonesia — Mulai Belajar dan Peta Kurikulum Terbuka',
  version,
  recorded_at: new Date().toISOString(),
  state: 'published_current_release_authority',
  release_state: 'published_and_anonymously_verified_on_required_public_destinations',
  overall_program_complete: false,
  credentials_recorded: false,
  model_provenance: 'OpenAI Codex gpt-5.6-sol, Ultra',
  student_entry: {
    primary_url: learnerSite,
    zenodo_description_first_href: firstDescriptionHref,
    learner_preview_pdf: '00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.58.0.pdf',
    standalone_learner_html: '01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.58.0.html',
    machine_surfaces_are_secondary: true,
    public_byte_readback: {
      result: 'pass', files: siteInventory.length, bytes: siteBytes,
      aggregate_sha256: siteAggregateSha256,
      coverage: 'Complete 57-file learner-site inventory including C100 and D20 materialized course and unit routes.',
    },
  },
  curriculum_state: {
    course_roles: 40,
    selected_source_architectures: 40,
    unresolved_roles_in_release_catalog: 0,
    completed_public_course_roles: 18,
    completed_public_records: 17,
    published_html_readers: 14,
    completion_scope_note: 'This release does not claim that all forty course editions are translated or complete; each canonical corpus owner retains its production, integration, and publication authority.',
  },
  learner_admissions: {
    B60: 'Complete CLP Calculus 4 textbook (316 pages) and complete problem book (486 pages), both exposed to learners.',
    C100: 'Complete rights-clean main geometry course, semantic HTML reader, 253 solutions, and a separately licensed Unit 001–010 workbook exposed as a supplement.',
    production_overlays: ['A10', 'A30', 'B70', 'C10', 'C20', 'D10', 'D40'],
  },
  backend_state: {
    architecture: 'owner-native lossless backends -> common-v1 adapters -> compact federation-v2 -> stable-unit federation-v2.1 -> learner read model -> generated student routes',
    v1: { records: 2122, package_bytes: backendV1.bytes, package_sha256: backendV1.sha256, preservation_mode: 'immutable_predecessor' },
    v2: {
      version: '0.4.0', records: 2463, datasets: 34, programs: 1, courses: 40,
      reader_surfaces: 144, web_routes: 43, publication_events: 63, qa_events: 16,
      identity_crosswalks: 2122, package_bytes: backendV2.bytes, package_sha256: backendV2.sha256,
      deterministic_replay: 'pass_two_byte_identical_builds',
    },
    v2_1: {
      status: 'four_pilots_deterministically_validated_and_publicly_routed',
      courses: ['A00', 'B10', 'C100', 'D20'], units: 1194, relations: 2165,
      package_bytes: backendV21.bytes, package_sha256: backendV21.sha256,
      replay_receipt_sha256: replayReceipt.sha256,
      replay_aggregate_sha256: 'c01423404fdbbea311df4663ce3f38f818ae14d7f967d4110b9f2105f6385993',
      learner_routes: 956, chapter_wrappers: 37,
    },
    design_boundary: 'The common backend carries identities, hashes, relations, rights, routes, search projections, QA evidence, and additive supplement relations; it does not duplicate textbook prose or replace owner-native representations.',
  },
  local_validation: {
    release_directory: 'releases/v0.58.0',
    files: 48,
    bytes: totalBytes,
    checksum_manifest_entries: 47,
    checksum_manifest_bytes: checksumManifest.bytes,
    checksum_manifest_sha256: checksumManifest.sha256,
    validation_receipt_bytes: validationReceipt.bytes,
    validation_receipt_sha256: validationReceipt.sha256,
    validation_result: 'pass',
    source_package_bytes: sourcePackage.bytes,
    source_package_sha256: sourcePackage.sha256,
  },
  release: {
    authority_source_commit: authoritySourceCommit,
    tag: 'v0.58.0', tag_kind: 'annotated', tag_object: tagObject, tag_target: taggedCommit,
    payload_files: 48, payload_bytes: totalBytes,
    payload_inventory_aggregate_sha256: aggregateSha256,
    receipt_commit_boundary: 'This post-publication receipt is committed after the immutable release tag and is not itself a tagged payload.',
  },
  github: {
    repository: githubRepository, release: githubRelease, branch: 'main', published_at: gh.publishedAt,
    draft: false, prerelease: false,
    anonymous_asset_readback: 'pass_48_of_48_filename_size_sha256',
    release_asset_bytes: totalBytes,
    pages: learnerSite,
    pages_readback: 'pass_57_of_57_http_200_local_byte_identity',
  },
  zenodo: {
    record_id: recordId,
    version_doi: zenodo.doi,
    concept_doi: zenodo.conceptdoi,
    public_record: `https://zenodo.org/records/${recordId}`,
    publication_date: zenodo.metadata.publication_date,
    version: zenodo.metadata.version,
    access_right: zenodo.metadata.access_right,
    file_count: zenodo.files.length,
    total_bytes: zenodo.files.reduce((sum, file) => sum + file.size, 0),
    anonymous_filename_size_sha256_readback: 'pass_48_of_48',
    description_first_href: firstDescriptionHref,
    description_boundary: 'student_site_first_machine_layer_explicitly_secondary',
    source_credit_preserved: true,
  },
  payload_inventory: payloadInventory,
  sites: {
    role: 'optional_mirror_not_the_public_learner_entry',
    configured_project_id: 'appgprj_6a8e08f7802481918baf4f5c8d1e7900',
    get_site_result: 'project_not_found_http_404',
    duplicate_site_created: false,
    public_hub_surface: learnerSite,
  },
  publication_boundary_result: {
    required_public_github_release: 'pass',
    required_public_zenodo: 'pass',
    required_public_github_pages: 'pass',
    optional_sites_refresh: 'operationally_unavailable_project_not_found',
    overall_public_release: 'pass',
  },
  privacy: { credentials_recorded: false, credential_values_in_public_artifacts: false },
  next_action: 'Continue canonical-owner QA and stable-ID integration of sealed helper packets, admit future complete owner handoffs into the common federation, and regenerate learner-first routes without transferring corpus ownership.',
};

const bytes = canonical(receipt);
await writeFile(output, bytes);
console.log(JSON.stringify({
  output,
  bytes: bytes.length,
  sha256: sha256(bytes),
  payload_files: payloadInventory.length,
  payload_bytes: totalBytes,
  aggregate_sha256: aggregateSha256,
}, null, 2));
