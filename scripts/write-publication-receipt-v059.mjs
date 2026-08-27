import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const version = '0.59.0';
const recordId = 22133203;
const conceptId = 22059707;
const releaseDir = resolve(project, `releases/v${version}`);
const docs = resolve(project, 'docs');
const output = resolve(project, `PUBLICATION_RECEIPT_v${version}.json`);
const learnerSite = 'https://kokunoyumeto.github.io/program-matematika-indonesia/';
const githubRepository = 'https://github.com/KokunoYumeto/program-matematika-indonesia';
const githubRelease = `${githubRepository}/releases/tag/v${version}`;
const githubAssetBase = `${githubRepository}/releases/download/v${version}/`;
const zenodoApi = `https://zenodo.org/api/records/${recordId}`;
const expectedTagTarget = '140323bb23e16c5e64235ebec69a7bfc290276a4';
const expectedAuthoritySourceCommit = '6212337e077bf2fe16315ab47fd1d618a8c8c434';
const modelProvenance = 'OpenAI Codex gpt-5.6-sol, Ultra';

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
const delay = (milliseconds) => new Promise((resolveDelay) => setTimeout(resolveDelay, milliseconds));
const asUrlPath = (path) => path.replaceAll('\\', '/');

async function fetchBytes(url, label) {
  let response;
  for (let attempt = 1; attempt <= 5; attempt += 1) {
    response = await fetch(url, {
      cache: 'no-store',
      headers: {
        accept: '*/*',
        'user-agent': 'Program-Matematika-Indonesia-public-readback',
      },
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

async function mapLimit(items, concurrency, operation) {
  const results = new Array(items.length);
  let cursor = 0;
  async function worker() {
    while (cursor < items.length) {
      const index = cursor;
      cursor += 1;
      results[index] = await operation(items[index], index);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, worker));
  return results;
}

async function enumerateFiles(root) {
  const paths = [];
  async function walk(directory) {
    const entries = await readdir(directory, { withFileTypes: true });
    for (const entry of entries.sort((left, right) => left.name.localeCompare(right.name))) {
      const absolute = resolve(directory, entry.name);
      if (entry.isDirectory()) await walk(absolute);
      else if (entry.isFile()) paths.push(asUrlPath(relative(root, absolute)));
      else assert.fail(`Unsupported docs-tree entry: ${absolute}`);
    }
  }
  await walk(root);
  return paths.sort();
}

function requiredLocal(localInventory, name) {
  const value = localInventory.find((entry) => entry.name === name);
  assert.ok(value, `missing required release file: ${name}`);
  return value;
}

const names = (await readdir(releaseDir, { withFileTypes: true }))
  .filter((entry) => entry.isFile())
  .map((entry) => entry.name)
  .sort();
assert.equal(names.length, 54, 'release inventory must contain exactly 54 files');

const localInventory = [];
for (const name of names) {
  const bytes = await readFile(resolve(releaseDir, name));
  localInventory.push({ name, bytes: bytes.length, sha256: sha256(bytes), body: bytes });
}
const totalBytes = localInventory.reduce((sum, row) => sum + row.bytes, 0);
assert.equal(totalBytes, 13070437, 'release inventory byte total differs');

const checksumManifest = requiredLocal(localInventory, 'CHECKSUMS.sha256');
const checksumRows = checksumManifest.body.toString('utf8').trimEnd().split(/\r?\n/).map((line) => {
  const match = /^([0-9a-f]{64})  (.+)$/.exec(line);
  assert.ok(match, `malformed CHECKSUMS row: ${line}`);
  return { sha256: match[1], name: match[2] };
});
assert.equal(checksumRows.length, 53, 'CHECKSUMS must bind 53 payload files');
assert.deepEqual(checksumRows.map((row) => row.name).sort(), names.filter((name) => name !== 'CHECKSUMS.sha256'));
for (const row of checksumRows) {
  assert.equal(requiredLocal(localInventory, row.name).sha256, row.sha256, `${row.name}: CHECKSUMS SHA-256 differs`);
}

const validationReceipt = requiredLocal(localInventory, `LOCAL_RELEASE_VALIDATION_v${version}.json`);
const sourcePackage = requiredLocal(localInventory, `program-matematika-indonesia-source-v${version}.zip`);
const backendV1 = requiredLocal(localInventory, `program-matematika-indonesia-backend-v1-v${version}.zip`);
const backendV2 = requiredLocal(localInventory, `program-matematika-indonesia-backend-v2-v${version}.zip`);
const backendV21 = requiredLocal(localInventory, `program-matematika-indonesia-backend-v2.1-pilots-v${version}.zip`);
const backendV22 = requiredLocal(localInventory, `program-matematika-indonesia-backend-v2.2-pilot-v${version}.zip`);
const replayReceipt = requiredLocal(localInventory, `GLOBAL_BACKEND_V21_DETERMINISTIC_REPLAY_RECEIPT_v${version}.json`);
const v2ReceiptFile = requiredLocal(localInventory, `GLOBAL_BACKEND_V2_PHASE1_VALIDATION_RECEIPT_v${version}.json`);
const v22ValidationFile = requiredLocal(localInventory, `GLOBAL_BACKEND_V22_VALIDATION_RECEIPT_v${version}.json`);
const v22ArchiveFile = requiredLocal(localInventory, `GLOBAL_BACKEND_V22_ARCHIVE_RECEIPT_v${version}.json`);
const catalogFile = requiredLocal(localInventory, `program-matematika-indonesia-catalog-v${version}.json`);

const localValidation = JSON.parse(validationReceipt.body.toString('utf8'));
const v2Receipt = JSON.parse(v2ReceiptFile.body.toString('utf8'));
const v22Validation = JSON.parse(v22ValidationFile.body.toString('utf8'));
const v22Archive = JSON.parse(v22ArchiveFile.body.toString('utf8'));
const catalog = JSON.parse(catalogFile.body.toString('utf8'));
const v22SealBytes = await readFile(resolve(project, 'backend/v2.2/packages/a00-openstax-prealgebra-v0.1.0/seal.json'));
const v22Seal = JSON.parse(v22SealBytes.toString('utf8'));

assert.equal(localValidation.result, 'pass');
assert.equal(localValidation.version, version);
assert.equal(localValidation.checks.source_commit_binding, expectedAuthoritySourceCommit);
assert.deepEqual(catalog.counts, {
  courseRoles: 40,
  selectedCorpusRoles: 40,
  unresolvedRoles: 0,
  completedPublicCourseRoles: 19,
  completedPublicRecords: 18,
});
assert.equal(catalog.sourceCommit, expectedAuthoritySourceCommit);
assert.equal(localValidation.checks.static_site.publishedHtmlReaders, 20);

assert.equal(v2Receipt.result, 'pass');
assert.equal(v2Receipt.canonical_package.record_count, 2478);
assert.deepEqual(v2Receipt.canonical_package.table_counts, {
  courses: 40,
  datasets: 34,
  identity_crosswalks: 2122,
  programs: 1,
  publication_events: 67,
  qa_events: 17,
  reader_surfaces: 154,
  web_routes: 43,
});

assert.equal(v22Validation.result, 'pass');
assert.equal(v22Validation.counts.projected_records, 1313);
assert.equal(v22Validation.counts.native_records_referenced, 519678);
assert.equal(v22Validation.counts.routes, 75);
assert.equal(v22Validation.counts.visible_units, 75);
assert.equal(v22Archive.result, 'pass');
assert.equal(v22Archive.source_commit, expectedAuthoritySourceCommit);
assert.equal(v22Archive.archive.bytes, backendV22.bytes);
assert.equal(v22Archive.archive.sha256, backendV22.sha256);
assert.equal(sha256(v22SealBytes), 'fb0696a3f38509468076c4fff374106127e092f3b70b4c1536f7c611009dc855');
assert.equal(v22Seal.sealed_digest_sha256, '49c4272f2b48f311429575814bf23acef02bcd9f5e96033b2d618be88678a9e8');

const docsNames = await enumerateFiles(docs);
assert.ok(docsNames.includes('readers/d90/original-02/index.html'), 'complete docs inventory must include the D90 reader');
const siteInventory = await mapLimit(docsNames, 6, async (name) => {
  const local = await readFile(resolve(docs, name));
  const url = new URL(name === 'index.html' ? './' : name, learnerSite).href;
  const remote = await fetchBytes(url, `GitHub Pages ${name}`);
  assert.equal(remote.length, local.length, `${name}: GitHub Pages byte count differs`);
  assert.equal(sha256(remote), sha256(local), `${name}: GitHub Pages SHA-256 differs`);
  return { name, bytes: local.length, sha256: sha256(local), url };
});
const siteBytes = siteInventory.reduce((sum, row) => sum + row.bytes, 0);
const siteAggregateSha256 = sha256(Buffer.from(siteInventory
  .map((row) => `${row.sha256}  ${row.name}`)
  .sort()
  .join('\n') + '\n', 'utf8'));

const zenodo = await fetchJson(zenodoApi, 'Zenodo public record');
const githubPublicRelease = JSON.parse(execFileSync('gh', [
  'release', 'view', `v${version}`,
  '--repo', 'KokunoYumeto/program-matematika-indonesia',
  '--json', 'url,publishedAt,isDraft,isPrerelease,tagName,assets',
], { cwd: project, encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 }));
assert.equal(zenodo.id, recordId);
assert.equal(zenodo.doi, `10.5281/zenodo.${recordId}`);
assert.equal(zenodo.conceptdoi, `10.5281/zenodo.${conceptId}`);
assert.equal(zenodo.metadata.version, version);
assert.equal(zenodo.metadata.access_right, 'open');
assert.equal(zenodo.files.length, 54);
const firstDescriptionHref = /href=["']([^"']+)["']/i.exec(zenodo.metadata.description)?.[1];
assert.equal(firstDescriptionHref, learnerSite);
assert.match(zenodo.metadata.description, /OpenAI Codex gpt-5\.6-sol, Ultra/);
assert.match(zenodo.metadata.description, /masih diproduksi|belum selesai|belum lengkap|not complete/i, 'Zenodo description must preserve the incomplete-program boundary');

assert.equal(githubPublicRelease.url, githubRelease);
assert.equal(githubPublicRelease.tagName, `v${version}`);
assert.equal(githubPublicRelease.isDraft, false);
assert.equal(githubPublicRelease.isPrerelease, false);
assert.equal(githubPublicRelease.assets.length, 54);
assert.deepEqual(githubPublicRelease.assets.map((asset) => asset.name).sort(), names);
for (const asset of githubPublicRelease.assets) {
  assert.equal(asset.size, requiredLocal(localInventory, asset.name).bytes, `${asset.name}: GitHub API byte count differs`);
}

const zenodoFiles = new Map(zenodo.files.map((file) => [file.key, file]));
assert.deepEqual([...zenodoFiles.keys()].sort(), names);
for (const local of localInventory) {
  assert.equal(zenodoFiles.get(local.name).size, local.bytes, `${local.name}: Zenodo API byte count differs`);
}

const payloadInventory = await mapLimit(localInventory, 4, async (local) => {
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
  return {
    name: local.name,
    bytes: local.bytes,
    sha256: local.sha256,
    github_url: githubUrl,
    zenodo_url: zenodoFile.links.self,
    github_anonymous_byte_identity: true,
    zenodo_anonymous_byte_identity: true,
  };
});

const aggregateSha256 = sha256(Buffer.from(payloadInventory
  .map((row) => `${row.sha256}  ${row.name}`)
  .sort()
  .join('\n') + '\n', 'utf8'));

const taggedCommit = execFileSync('git', ['rev-parse', `v${version}^{}`], { cwd: project, encoding: 'utf8' }).trim();
const tagObject = execFileSync('git', ['rev-parse', `v${version}`], { cwd: project, encoding: 'utf8' }).trim();
const authoritySourceCommit = execFileSync('git', ['rev-parse', `${taggedCommit}~2`], { cwd: project, encoding: 'utf8' }).trim();
assert.equal(taggedCommit, expectedTagTarget);
assert.equal(authoritySourceCommit, expectedAuthoritySourceCommit);
assert.equal(execFileSync('git', ['cat-file', '-t', tagObject], { cwd: project, encoding: 'utf8' }).trim(), 'tag');

const receipt = {
  schema_id: 'program-matematika-indonesia/combined-publication-receipt/v15',
  title: 'Program Matematika Indonesia — Mulai Belajar dan Peta Kurikulum Terbuka',
  version,
  recorded_at: new Date().toISOString(),
  state: 'published_current_release_authority',
  release_state: 'published_and_anonymously_verified_on_required_public_destinations',
  overall_program_complete: false,
  credentials_recorded: false,
  model_provenance: modelProvenance,
  student_entry: {
    primary_url: learnerSite,
    zenodo_description_first_href: firstDescriptionHref,
    learner_preview_pdf: `00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v${version}.pdf`,
    standalone_learner_html: `01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v${version}.html`,
    machine_surfaces_are_secondary: true,
    public_byte_readback: {
      result: 'pass',
      files: siteInventory.length,
      bytes: siteBytes,
      aggregate_sha256: siteAggregateSha256,
      coverage: `Complete recursively enumerated ${siteInventory.length}-file current docs tree, including the D90 reader at readers/d90/original-02/index.html.`,
    },
  },
  curriculum_state: {
    course_roles: 40,
    selected_source_architectures: 40,
    unresolved_roles_in_release_catalog: 0,
    completed_public_course_roles: 19,
    completed_public_records: 18,
    published_html_readers: 20,
    completion_scope_note: 'This release does not claim that all forty course editions are translated or complete; each canonical corpus owner retains its production, integration, and publication authority.',
  },
  backend_state: {
    architecture: 'owner-native lossless backends -> common-v1 adapters -> compact federation-v2 -> stable-unit federation-v2.1 -> zero-copy modular federation-v2.2 -> learner read model -> generated student routes',
    v1: {
      records: 2122,
      package_bytes: backendV1.bytes,
      package_sha256: backendV1.sha256,
      preservation_mode: 'immutable_predecessor',
    },
    v2: {
      version: '0.4.1',
      records: 2478,
      datasets: 34,
      programs: 1,
      courses: 40,
      reader_surfaces: 154,
      web_routes: 43,
      publication_events: 67,
      qa_events: 17,
      identity_crosswalks: 2122,
      package_bytes: backendV2.bytes,
      package_sha256: backendV2.sha256,
      deterministic_replay: 'pass_two_byte_identical_builds',
    },
    v2_1: {
      status: 'four_pilots_deterministically_validated_and_publicly_routed',
      courses: ['A00', 'B10', 'C100', 'D20'],
      units: 1194,
      relations: 2165,
      package_bytes: backendV21.bytes,
      package_sha256: backendV21.sha256,
      replay_receipt_sha256: replayReceipt.sha256,
      replay_aggregate_sha256: 'c01423404fdbbea311df4663ce3f38f818ae14d7f967d4110b9f2105f6385993',
      learner_routes: 956,
      chapter_wrappers: 37,
    },
    v2_2: {
      status: 'a00_zero_copy_modular_pilot_sealed_validated_and_publicly_preserved',
      projected_records: 1313,
      native_records_referenced: 519678,
      visible_units: 75,
      routes: 75,
      native_views: 17,
      record_tables: 19,
      identity_map_rows: 92,
      package_bytes: backendV22.bytes,
      package_sha256: backendV22.sha256,
      validation_receipt_sha256: v22ValidationFile.sha256,
      archive_receipt_sha256: v22ArchiveFile.sha256,
      seal_sha256: sha256(v22SealBytes),
      sealed_digest_sha256: v22Seal.sealed_digest_sha256,
      deterministic_replay_sha256: v22Validation.hashes.two_run_replay_sha256,
    },
    design_boundary: 'The common backend carries identities, hashes, relations, rights, routes, search projections, QA evidence, and additive supplement relations; it references rather than duplicates owner-native textbook prose and representations.',
  },
  local_validation: {
    release_directory: `releases/v${version}`,
    files: 54,
    bytes: totalBytes,
    checksum_manifest_entries: checksumRows.length,
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
    tag: `v${version}`,
    tag_kind: 'annotated',
    tag_object: tagObject,
    tag_target: taggedCommit,
    payload_files: payloadInventory.length,
    payload_bytes: totalBytes,
    payload_inventory_aggregate_sha256: aggregateSha256,
    receipt_commit_boundary: 'This post-publication receipt is committed after the immutable release tag and is not itself a tagged payload.',
  },
  github: {
    repository: githubRepository,
    release: githubRelease,
    branch: 'main',
    published_at: githubPublicRelease.publishedAt,
    draft: false,
    prerelease: false,
    anonymous_asset_readback: 'pass_54_of_54_filename_size_sha256',
    release_asset_bytes: totalBytes,
    pages: learnerSite,
    pages_readback: `pass_${siteInventory.length}_of_${siteInventory.length}_complete_docs_tree_http_200_local_byte_identity`,
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
    anonymous_filename_size_sha256_readback: 'pass_54_of_54',
    description_first_href: firstDescriptionHref,
    description_boundary: 'student_site_first_machine_layer_explicitly_secondary_program_incomplete_truth_preserved',
    model_provenance_exact: modelProvenance,
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
  payload_aggregate_sha256: aggregateSha256,
  docs_files: siteInventory.length,
  docs_bytes: siteBytes,
  docs_aggregate_sha256: siteAggregateSha256,
}, null, 2));
