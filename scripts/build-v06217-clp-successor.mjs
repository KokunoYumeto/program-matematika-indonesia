#!/usr/bin/env node

/*
 * Build a deterministic, additive CLP-family successor projection.
 *
 * This is deliberately a versioned builder.  It never edits the historical
 * v0.62.13/v0.62.14 projections and it does not publish anything.  By default
 * it only replays the sealed handoff and prints the would-be output inventory.
 * Pass --write --out <a staging directory> to materialize a tree for the
 * parent integrator.  The output directory is never removed by this script.
 *
 * The large CLP ZIP remains an external release asset.  We record its exact
 * identity, but do not copy 545 MB into the repository during a dry run.
 */

import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { access, copyFile, mkdir, readFile, stat, writeFile } from 'node:fs/promises';
import { createReadStream } from 'node:fs';
import { dirname, isAbsolute, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const scriptRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const workspaceRoot = resolve(scriptRoot, '..', '..', '..');
const outputRelRoot = 'backend/course-capsule-v1/authority/clp-family-v231';
const successorPatternRel = `${outputRelRoot}/modular-backend-pattern-index-v2.1.json`;
const successorPatternSchemaRel = `${outputRelRoot}/modular-backend-pattern-index-v2.1.schema.json`;
const defaultCandidate = resolve(
  workspaceRoot,
  'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/backend_adapters/clp_family_v231_candidate',
);
const baseRefDefault = 'codex/v0.62.13';
const successorVersionDefault = 'v0.62.17';
const asOfDefault = '2026-09-01T15:04:10Z';
const basePaths = {
  adapter: 'backend/course-capsule-v1/authority/v23-adapter-index-v2.json',
  pattern: 'backend/course-capsule-v1/authority/modular-backend-pattern-index-v2.json',
  feature: 'backend/course-capsule-v1/authority/feature-adoption-provenance-v1.json',
  comparison: 'backend/course-capsule-v1/authority/comparison-evidence-manifest-v1.json',
};
const predecessorRelease = {
  version: 'v0.62.16',
  // v0.62.16 is the correction release, while its immutable v2 snapshot
  // retains the exact v0.62.14-postpublication snapshot identity.
  snapshot_id: 'urn:interlanguage:program-matematika-indonesia:v23-adapters:v0.62.14-postpublication:2026-09-01',
  central_release_record_doi: '10.5281/zenodo.22231858',
  concept_doi: '10.5281/zenodo.22059707',
  git_commit: '42a0656177376d5021a014f3e4d5ae6419d07ae5',
  git_tree: 'aa648184b56242f1a234c72d55e0d6d44a317b6c',
  source: {
    path: 'releases/v0.62.16/program-matematika-indonesia-source-v0.62.16.zip',
    bytes: 508950409,
    sha256: '4d1b758e4f06fab48bb8ecba63a0b85138dbec4345812d4fee8dea694a8155d0',
  },
  adapter_snapshot: {
    path: 'releases/v0.62.16/v23-adapter-index-v2.json',
    bytes: 28988,
    sha256: '779967bbc3b7d3059964183d797c2a87f3999123442e694919d54bfa08839517',
  },
  snapshot_receipt: {
    path: 'releases/v0.62.16/MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json',
    bytes: 3490,
    sha256: 'ec7020fd31ff2f960a27831b70b1ed1e1d658565e07094456bd8547384ed0593',
  },
};

const roleOrder = [
  'A00', 'A10', 'A20', 'A30', 'B10', 'B20', 'B30', 'B40', 'B50', 'B60',
  'B70', 'B80', 'B90', 'B95', 'C10', 'C20', 'C30', 'C40', 'C50', 'C60',
  'C70', 'C80', 'C90', 'C100', 'C110', 'C120', 'C130', 'C140', 'D10',
  'D20', 'D30', 'D40', 'D50', 'D60', 'D70', 'D80', 'D90', 'D100', 'D110',
  'D120',
];
const clpRoles = ['B20', 'B30', 'B50', 'B60'];
const clpFamilyId = 'family-06-clp';
const clpPackageId = 'urn:uuid:8dbda99c-2e39-5fc0-a6ff-64a52cb81b26';
const compactRouteRel = `${outputRelRoot}/clp-learner-route-input-v1.json`;
const sanitizedEvidenceRels = {
  handoff: `${outputRelRoot}/evidence/HANDOFF_FILE_INVENTORY.identity.json`,
  manifest: `${outputRelRoot}/evidence/CLP_PACKAGE_MANIFEST.identity.json`,
  route: `${outputRelRoot}/evidence/CLP_LEARNER_ROUTE_EVIDENCE.identity.json`,
  profile: `${outputRelRoot}/evidence/CLP_NATIVE_PROFILE_DESIGN.identity.json`,
};

function parseArgs(argv) {
  const args = { write: false, candidate: defaultCandidate, baseRef: baseRefDefault, version: successorVersionDefault, asOf: asOfDefault };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--write') args.write = true;
    else if (arg === '--published') args.published = true;
    else if (arg === '--copy-zip') args.copyZip = true;
    else if (arg === '--allow-repo-write') args.allowRepoWrite = true;
    else if (arg === '--skip-local-route-rehash') args.skipLocalRouteRehash = true;
    else if (arg === '--candidate') args.candidate = argv[++i];
    else if (arg === '--base-ref') args.baseRef = argv[++i];
    else if (arg === '--version') args.version = argv[++i];
    else if (arg === '--as-of') args.asOf = argv[++i];
    else if (arg === '--out') args.out = argv[++i];
    else if (arg === '--help' || arg === '-h') {
      console.log(`Usage: node scripts/build-v06217-clp-successor.mjs [options]\n\n` +
        `Default is read-only dry-run. Options:\n` +
        `  --write                         write a staging tree\n` +
        `  --out <dir>                    staging root (required for --write in CI)\n` +
        `  --candidate <dir>              sealed CLP handoff root\n` +
        `  --base-ref <git-ref>           fallback ref for missing base JSON\n` +
        `  --version <vX.Y.Z>              successor version (default v0.62.17)\n` +
        `  --as-of <ISO-date-time>         deterministic snapshot timestamp\n` +
        `  --skip-local-route-rehash      trust route-evidence local hashes\n` +
        `  --copy-zip                     copy the 545 MB ZIP (write mode only)\n` +
        `  --published                     rejected unless a later publisher adds readback evidence\n`);
      process.exit(0);
    } else throw new Error(`Unknown argument: ${arg}`);
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
if (args.published) throw new Error('This builder is prepublication-only; use the publication verifier after public readback.');
if (!/^v\d+\.\d+\.\d+$/.test(args.version)) throw new Error(`Invalid successor version: ${args.version}`);
if (Number.isNaN(Date.parse(args.asOf))) throw new Error(`Invalid --as-of timestamp: ${args.asOf}`);
const asOfDate = args.asOf.slice(0, 10);
const candidateRoot = resolve(args.candidate);
const stagingRoot = resolve(args.out ?? resolve(scriptRoot, 'tmp', 'clp-v06217-successor-staging'));

function assertInside(child, parent, label) {
  const childAbs = resolve(child);
  const parentAbs = resolve(parent);
  const rel = relative(parentAbs, childAbs);
  assert.ok(rel === '' || (rel !== '..' && !rel.startsWith(`..${sep}`) && !isAbsolute(rel)), `${label} escapes its parent`);
  return childAbs;
}

if (args.write) {
  // A caller must opt in before writing directly into the repository root.
  if (resolve(stagingRoot) === resolve(scriptRoot) || resolve(stagingRoot) === resolve(workspaceRoot)) {
    throw new Error('Refusing to write to a broad workspace root; pass a narrow staging directory.');
  }
  if (resolve(stagingRoot) === resolve(scriptRoot) && !args.allowRepoWrite) {
    throw new Error('Refusing repository-root write without --allow-repo-write.');
  }
}

const hash = (bytes) => createHash('sha256').update(bytes).digest('hex');
const identity = (bytes) => ({ bytes: bytes.length, sha256: hash(bytes) });
const stableObject = (value) => {
  const sort = (item) => {
    if (Array.isArray(item)) return item.map(sort);
    if (item && typeof item === 'object') {
      return Object.fromEntries(Object.keys(item).sort().map((key) => [key, sort(item[key])]));
    }
    return item;
  };
  return Buffer.from(`${JSON.stringify(sort(value), null, 2)}\n`, 'utf8');
};
const fileRow = (path, bytes) => ({ path, ...identity(bytes) });
const exists = async (path) => { try { await access(path); return true; } catch { return false; } };

async function hashFile(path) {
  const stream = createReadStream(path);
  const digest = createHash('sha256');
  let bytes = 0;
  for await (const chunk of stream) { bytes += chunk.length; digest.update(chunk); }
  return { bytes, sha256: digest.digest('hex') };
}

function gitBytes(ref, repoRelativePath) {
  try {
    return execFileSync('git', ['show', `${ref}:${repoRelativePath}`], {
      cwd: scriptRoot,
      maxBuffer: 64 * 1024 * 1024,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  } catch (error) {
    const detail = error?.stderr ? String(error.stderr).trim() : String(error);
    throw new Error(`Unable to read ${repoRelativePath} from filesystem or ${ref}: ${detail}`);
  }
}

async function readRepoJson(repoRelativePath) {
  const localPath = resolve(scriptRoot, repoRelativePath);
  if (await exists(localPath)) {
    return { bytes: await readFile(localPath), source: 'filesystem', path: localPath };
  }
  const bytes = gitBytes(args.baseRef, repoRelativePath);
  return { bytes, source: `git:${args.baseRef}`, path: `${args.baseRef}:${repoRelativePath}` };
}

async function verifyPredecessorRelease() {
  const sourceAbsolute = assertInside(resolve(scriptRoot, predecessorRelease.source.path), scriptRoot, 'predecessor source archive');
  assert.ok(await exists(sourceAbsolute), `Predecessor source archive is missing: ${predecessorRelease.source.path}`);
  const sourceIdentity = await hashFile(sourceAbsolute);
  assert.deepEqual(sourceIdentity, {
    bytes: predecessorRelease.source.bytes,
    sha256: predecessorRelease.source.sha256,
  }, 'v0.62.16 source archive identity drift');
  const adapterSnapshotAbsolute = assertInside(resolve(scriptRoot, predecessorRelease.adapter_snapshot.path), scriptRoot, 'predecessor v2 adapter snapshot');
  assert.ok(await exists(adapterSnapshotAbsolute), `Predecessor v2 adapter snapshot is missing: ${predecessorRelease.adapter_snapshot.path}`);
  const adapterSnapshotBytes = await readFile(adapterSnapshotAbsolute);
  assert.deepEqual(identity(adapterSnapshotBytes), {
    bytes: predecessorRelease.adapter_snapshot.bytes,
    sha256: predecessorRelease.adapter_snapshot.sha256,
  }, 'v0.62.16 immutable v2 adapter snapshot identity drift');
  const adapterSnapshot = parseJson(adapterSnapshotBytes, predecessorRelease.adapter_snapshot.path);
  assert.equal(adapterSnapshot.snapshot?.snapshot_id, predecessorRelease.snapshot_id, 'Immutable v2 adapter snapshot ID drift');
  const notesPath = resolve(scriptRoot, 'releases/v0.62.16/RELEASE_NOTES_v0.62.16.md');
  assert.ok(await exists(notesPath), 'v0.62.16 release notes are missing');
  const notes = await readFile(notesPath, 'utf8');
  for (const marker of [predecessorRelease.git_commit, predecessorRelease.git_tree, predecessorRelease.source.sha256]) {
    assert.ok(notes.includes(marker), `v0.62.16 release notes omit predecessor marker: ${marker}`);
  }
  const githubReceiptPath = resolve(scriptRoot, 'GITHUB_PUBLICATION_RECEIPT_v0.62.16.json');
  const zenodoReceiptPath = resolve(scriptRoot, 'PUBLICATION_RECEIPT_v0.62.16.json');
  const snapshotReceiptPath = assertInside(resolve(scriptRoot, predecessorRelease.snapshot_receipt.path), scriptRoot, 'predecessor v2 snapshot receipt');
  assert.ok(await exists(githubReceiptPath), 'v0.62.16 GitHub publication receipt is missing');
  assert.ok(await exists(zenodoReceiptPath), 'v0.62.16 Zenodo publication receipt is missing');
  assert.ok(await exists(snapshotReceiptPath), 'v0.62.16 v2 snapshot receipt is missing');
  const githubReceiptBytes = await readFile(githubReceiptPath);
  const zenodoReceiptBytes = await readFile(zenodoReceiptPath);
  const snapshotReceiptBytes = await readFile(snapshotReceiptPath);
  const githubReceipt = parseJson(githubReceiptBytes, 'GITHUB_PUBLICATION_RECEIPT_v0.62.16.json');
  const zenodoReceipt = parseJson(zenodoReceiptBytes, 'PUBLICATION_RECEIPT_v0.62.16.json');
  const snapshotReceipt = parseJson(snapshotReceiptBytes, 'MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json');
  assert.equal(githubReceipt.release?.tag, predecessorRelease.version);
  assert.equal(githubReceipt.release?.tag_target_commit, predecessorRelease.git_commit);
  assert.equal(githubReceipt.release?.tag_target_tree, predecessorRelease.git_tree);
  assert.equal(githubReceipt.source?.archive?.sha256, predecessorRelease.source.sha256);
  assert.equal(zenodoReceipt.zenodo?.version_doi, predecessorRelease.central_release_record_doi);
  assert.equal(zenodoReceipt.zenodo?.concept_doi, predecessorRelease.concept_doi);
  assert.equal(zenodoReceipt.zenodo?.anonymous_readback, 'pass_100_of_100');
  assert.equal(snapshotReceipt.snapshot_id, predecessorRelease.snapshot_id);
  assert.equal(snapshotReceipt.status, 'pass');
  assert.deepEqual(identity(snapshotReceiptBytes), {
    bytes: predecessorRelease.snapshot_receipt.bytes,
    sha256: predecessorRelease.snapshot_receipt.sha256,
  }, 'v0.62.16 snapshot receipt identity drift');
  const receiptAdapter = snapshotReceipt.validated_files?.find((row) => row.path === basePaths.adapter);
  assert.deepEqual(receiptAdapter, {
    bytes: predecessorRelease.adapter_snapshot.bytes,
    path: basePaths.adapter,
    sha256: predecessorRelease.adapter_snapshot.sha256,
  }, 'v0.62.16 snapshot receipt does not bind the immutable v2 adapter index');
  return {
    ...predecessorRelease,
    source: { path: predecessorRelease.source.path, ...sourceIdentity },
    release_notes: fileRow('releases/v0.62.16/RELEASE_NOTES_v0.62.16.md', Buffer.from(notes, 'utf8')),
    github_receipt: fileRow('GITHUB_PUBLICATION_RECEIPT_v0.62.16.json', githubReceiptBytes),
    zenodo_receipt: fileRow('PUBLICATION_RECEIPT_v0.62.16.json', zenodoReceiptBytes),
    adapter_snapshot: fileRow(predecessorRelease.adapter_snapshot.path, adapterSnapshotBytes),
    snapshot_receipt: fileRow(predecessorRelease.snapshot_receipt.path, snapshotReceiptBytes),
  };
}

async function readCandidateFile(relativePath) {
  const safe = relativePath.replaceAll('\\', '/');
  const absolute = assertInside(resolve(candidateRoot, safe), candidateRoot, `candidate file ${safe}`);
  return { bytes: await readFile(absolute), absolute, relativePath: safe };
}

function parseJson(bytes, label) {
  try { return JSON.parse(bytes.toString('utf8')); }
  catch (error) { throw new Error(`${label}: invalid JSON: ${error.message}`); }
}

function aggregateInventoryIdentity(rows) {
  const lines = rows
    .map((row) => ({ path: row.path.replaceAll('\\', '/'), bytes: row.bytes, sha256: row.sha256 }))
    // The sealed handoff was produced with the manager's stable lexical
    // ordering.  Byte/code-point ordering produces a different digest for
    // this inventory (the upper-case filenames sort differently), so retain
    // the exact locale ordering used by the sealed replay.
    .sort((a, b) => a.path.localeCompare(b.path, 'en-US', { numeric: false, sensitivity: 'variant' }))
    .map((row) => Buffer.from(`${row.path}\0${row.bytes}\0${row.sha256}\n`, 'utf8'));
  const digest = createHash('sha256');
  for (const line of lines) digest.update(line);
  return digest.digest('hex');
}

function noPublicPathLeak(bytes, label) {
  const text = bytes.toString('utf8');
  assert.ok(!/[A-Za-z]:\\/.test(text), `${label}: absolute Windows path leaked`);
  assert.ok(!/(?:^|[\"'])\/(?:Users|home|tmp)\//m.test(text), `${label}: absolute POSIX path leaked`);
  assert.ok(!/(?:^|[\"'])outputs\//m.test(text), `${label}: workspace outputs path leaked`);
  assert.ok(!/(?:^|[\"'])\.\.\//m.test(text), `${label}: parent-relative path leaked`);
  assert.ok(!/gh[pousr]_[A-Za-z0-9_-]{12,}|access[_-]?token|api[_-]?key/i.test(text), `${label}: credential-like text leaked`);
  assert.ok(!text.includes(candidateRoot.replaceAll('\\', '/')), `${label}: candidate absolute path leaked`);
}

async function replaySealedCandidate() {
  assert.ok(await exists(candidateRoot), `Candidate root is missing: ${candidateRoot}`);
  const handoffFile = await readCandidateFile('MANAGER_HANDOFF.json');
  const inventoryFile = await readCandidateFile('HANDOFF_FILE_INVENTORY.json');
  const handoff = parseJson(handoffFile.bytes, 'MANAGER_HANDOFF.json');
  const inventory = parseJson(inventoryFile.bytes, 'HANDOFF_FILE_INVENTORY.json');
  assert.equal(handoff.state, 'validated_sealed_candidate_ready_for_sole_integrator_not_yet_admitted_or_published');
  assert.deepEqual(handoff.course_roles, clpRoles);
  assert.equal(inventory.file_count, inventory.files.length);
  assert.equal(inventory.payload_identity_sha256, aggregateInventoryIdentity(inventory.files));
  let payloadBytes = 0;
  const rechecked = [];
  for (const row of inventory.files) {
    const source = await readCandidateFile(row.path);
    const actual = await hashFile(source.absolute);
    assert.deepEqual(actual, { bytes: row.bytes, sha256: row.sha256 }, `${row.path}: sealed identity drift`);
    payloadBytes += actual.bytes;
    rechecked.push({ path: row.path.replaceAll('\\', '/'), ...actual });
  }
  assert.equal(payloadBytes, inventory.payload_bytes);
  const pkg = handoff.adapter_package;
  assert.equal(pkg.package_id, clpPackageId);
  assert.equal(pkg.zip.bytes, 545418367);
  assert.equal(pkg.zip.sha256, 'f2e2714c5f1349092e8cb574d6495e604086c9df3bc4bdf5bbe5974b5f61360d');
  const zipRow = inventory.files.find((row) => row.path.endsWith('.zip'));
  assert.ok(zipRow, 'sealed inventory does not contain the CLP ZIP');
  assert.deepEqual({ bytes: zipRow.bytes, sha256: zipRow.sha256 }, { bytes: pkg.zip.bytes, sha256: pkg.zip.sha256 });
  return { handoff, inventory, inventoryFile, handoffFile, rechecked, payloadBytes };
}

function compactRouteFacts(rows) {
  return rows.map((row) => ({
    course_id: row.course_id,
    volume: row.volume,
    family_reader_order: row.family_reader_order,
    course_reader_order: row.course_reader_order,
    title: row.title,
    role: row.role,
    kind: row.kind,
    learner_surface_role: row.learner_surface_role,
    format: row.format,
    scope: row.scope,
    pages: row.pages,
    bytes: row.bytes,
    sha256: row.sha256,
    license: row.license,
    filename: row.public.filename,
    url: row.public.record_file_download_url,
    record_url: row.public.record_url,
    record_id: row.public.record_id,
    version_doi: row.public.version_doi,
    route_granularity: row.route_granularity,
    anchor_status: row.anchor_status,
    verification_scope: row.public.anonymous_exact_byte_readback,
  }));
}

function compactRouteComparable(value) {
  return (value ?? []).map((row) => ({
    course_id: row.course_id,
    volume: row.volume,
    family_reader_order: row.family_reader_order,
    course_reader_order: row.course_reader_order,
    title: row.title,
    role: row.role,
    kind: row.kind,
    learner_surface_role: row.learner_surface_role,
    format: row.format,
    scope: row.scope,
    pages: row.pages,
    bytes: row.bytes,
    sha256: row.sha256,
    license: row.license,
    filename: row.filename,
    url: row.url,
    route_granularity: row.route_granularity,
    anchor_status: row.anchor_status,
    verification_scope: row.verification_scope,
  }));
}

async function loadCompactRouteInput(routeEvidence, routeFile, rows) {
  const compactAbsolute = resolve(scriptRoot, compactRouteRel);
  let compactBytes;
  let compact;
  if (await exists(compactAbsolute)) {
    compactBytes = await readFile(compactAbsolute);
    compact = parseJson(compactBytes, compactRouteRel);
  } else {
    compact = {
      schema_id: 'interlanguage/clp-learner-route-input/v1',
      schema_version: '1.0.0',
      locale: 'id-ID',
      status: 'sanitized_projection_of_sealed_evidence',
      sealed_authority: {
        schema_id: routeEvidence.schema_id,
        generated_utc: routeEvidence.generated_utc,
        bytes: routeFile.bytes.length,
        sha256: identity(routeFile.bytes).sha256,
      },
      routes: compactRouteFacts(rows),
      summary: { course_count: 4, action_count: 7, pages: 4077, bytes: 35639691 },
    };
    compactBytes = stableObject(compact);
  }
  assert.equal(compact.schema_id, 'interlanguage/clp-learner-route-input/v1');
  assert.equal(compact.schema_version, '1.0.0');
  assert.equal(compact.status, 'sanitized_projection_of_sealed_evidence');
  assert.equal(compact.locale, 'id-ID');
  assert.deepEqual(compact.summary, { course_count: 4, action_count: 7, pages: 4077, bytes: 35639691 });
  assert.deepEqual(compact.sealed_authority, {
    schema_id: routeEvidence.schema_id,
    generated_utc: routeEvidence.generated_utc,
    bytes: routeFile.bytes.length,
    sha256: identity(routeFile.bytes).sha256,
  });
  for (const route of compact.routes ?? []) {
    const sealed = rows.find((candidate) => candidate.course_id === route.course_id && candidate.course_reader_order === route.course_reader_order);
    assert.ok(sealed, `${route.course_id}:${route.course_reader_order}: compact route has no sealed counterpart`);
    for (const key of ['record_url', 'record_id', 'version_doi']) {
      if (route[key] !== undefined) assert.equal(route[key], sealed.public[key], `${route.course_id}:${key}: compact publication metadata drift`);
    }
  }
  assert.deepEqual(compactRouteComparable(compact.routes), compactRouteComparable(compactRouteFacts(rows)), 'compact route input diverges from sealed route evidence');
  noPublicPathLeak(compactBytes, compactRouteRel);
  return { compact, compactBytes };
}

function sanitizedIdentityProjection({ kind, sourceRef, sourceIdentity, claims = {} }) {
  return stableObject({
    schema_id: 'interlanguage/clp-successor-source-identity/v1',
    schema_version: '1.0.0',
    kind,
    source_ref: sourceRef,
    source_identity: { bytes: sourceIdentity.bytes, sha256: sourceIdentity.sha256 },
    claims,
  });
}

async function replayRoutes(handoff, successorSnapshotId) {
  const routeFile = await readCandidateFile('research/CLP_LEARNER_ROUTE_EVIDENCE.json');
  const routeEvidence = parseJson(routeFile.bytes, 'CLP_LEARNER_ROUTE_EVIDENCE.json');
  assert.equal(routeEvidence.status, 'verified_research_input_not_adapter_consumption');
  assert.deepEqual(routeEvidence.scope.courses, clpRoles);
  assert.equal(routeEvidence.scope.locale, 'id-ID');
  const courses = routeEvidence.courses;
  assert.equal(courses.length, 4);
  const rows = courses.flatMap((course) => course.readers.map((reader) => ({
    course_id: course.course_id,
    volume: course.volume,
    title: course.title,
    prerequisites: course.prerequisites,
    family_reader_order: reader.family_reader_order,
    course_reader_order: reader.course_reader_order,
    role: reader.role,
    kind: reader.kind,
    learner_surface_role: reader.learner_surface_role,
    format: reader.format,
    scope: reader.scope,
    pages: reader.pages,
    bytes: reader.bytes,
    sha256: reader.sha256,
    license: reader.license,
    local: reader.local,
    public: {
      ...reader.public,
      record_url: course.publication?.record_url,
      record_id: course.publication?.record_id,
      version_doi: course.publication?.version_doi,
    },
    route_granularity: reader.route_granularity,
    anchor_status: reader.anchor_status,
  })));
  assert.equal(rows.length, 7);
  assert.equal(rows.reduce((sum, row) => sum + row.pages, 0), 4077);
  assert.equal(rows.reduce((sum, row) => sum + row.bytes, 0), 35639691);
  assert.deepEqual(new Set(rows.map((row) => row.course_id)), new Set(clpRoles));
  const compactRouteInput = await loadCompactRouteInput(routeEvidence, routeFile, rows);
  const localRehash = [];
  if (!args.skipLocalRouteRehash) {
    for (const row of rows) {
      const localPath = row.local?.path;
      assert.ok(typeof localPath === 'string' && !isAbsolute(localPath), `${row.course_id}: route local path must be workspace-relative`);
      const absolute = assertInside(resolve(workspaceRoot, localPath), workspaceRoot, `${row.course_id} local route`);
      assert.ok(await exists(absolute), `${row.course_id}: local reader is missing: ${localPath}`);
      const actual = await hashFile(absolute);
      assert.deepEqual(actual, { bytes: row.bytes, sha256: row.sha256 }, `${row.course_id}: reader identity drift`);
      localRehash.push({ course_id: row.course_id, order: row.course_reader_order, path: localPath, ...actual });
    }
  }
  // A dedicated sidecar builder owns the canonical v1 route projection.  If
  // it is already present, consume it as an immutable input and verify it
  // against the sealed route evidence rather than silently generating a
  // second incompatible shape.  The fallback below is only for a clean
  // checkout in which that builder has not yet run.
  const canonicalSidecarPath = resolve(scriptRoot, outputRelRoot, 'learner-reader-actions-v1.json');
  let sidecarBytes;
  let sidecar;
  if (await exists(canonicalSidecarPath)) {
    sidecarBytes = await readFile(canonicalSidecarPath);
    sidecar = parseJson(sidecarBytes, 'learner-reader-actions-v1.json');
    assert.equal(sidecar.schema_id, 'interlanguage/learner-reader-actions/v1');
    assert.equal(sidecar.summary?.action_count, 7);
    assert.equal(sidecar.summary?.verified_action_count, 7);
    assert.equal(sidecar.summary?.pages, 4077);
    assert.equal(sidecar.summary?.bytes, 35639691);
    assert.equal(sidecar.source?.sealed_authority?.sha256, identity(routeFile.bytes).sha256);
    assert.equal(sidecar.actions.length, rows.length);
    for (const action of sidecar.actions) {
      const route = rows.find((candidate) => candidate.course_id === action.course_id && candidate.course_reader_order === action.course_order);
      assert.ok(route, `${action.action_id}: sidecar action is not present in sealed route evidence`);
      assert.deepEqual({ bytes: action.bytes, sha256: action.sha256, url: action.url }, {
        bytes: route.bytes, sha256: route.sha256, url: route.public.record_file_download_url,
      }, `${action.action_id}: sidecar drift`);
    }
    // The canonical sidecar is a reusable route-facts source and carries its
    // own route snapshot.  Project those verified facts into this successor
    // without mutating the canonical authority file.  Point the staged source
    // at the sealed evidence that this builder also emits, so a staging
    // validator can replay the source without access to another checkout.
    sidecar = structuredClone(sidecar);
    sidecar.snapshot_id = successorSnapshotId;
    sidecar.source = {
      ...sidecar.source,
      path: compactRouteRel,
      bytes: compactRouteInput.compactBytes.length,
      sha256: identity(compactRouteInput.compactBytes).sha256,
      schema_id: compactRouteInput.compact.schema_id,
      generated_utc: compactRouteInput.compact.sealed_authority.generated_utc,
      sealed_authority: {
        bytes: routeFile.bytes.length,
        generated_utc: routeEvidence.generated_utc,
        schema_id: routeEvidence.schema_id,
        sha256: identity(routeFile.bytes).sha256,
      },
    };
    sidecarBytes = stableObject(sidecar);
  } else {
    const actions = rows.map((row) => ({
      action_id: `${row.course_id}:reader:${row.role === 'combined_textbook_problembook' ? 'combined' : row.role}`,
      anchor_status: row.anchor_status,
      bytes: row.bytes,
      course_id: row.course_id,
      course_order: row.course_reader_order,
      evidence: {
        kind: 'receipt_bound_anonymous_public_readback',
        locator: row.public.record_file_download_url.split('/files/')[0],
        record_id: Number(row.public.record_file_download_url.match(/records\/(\d+)/)?.[1]),
        source_json_pointer: `/routes/${row.family_reader_order - 1}`,
        status: 'pass_receipt_bound',
        version_doi: row.public.record_file_download_url.match(/records\/(\d+)/)?.[1] ? `10.5281/zenodo.${row.public.record_file_download_url.match(/records\/(\d+)/)[1]}` : null,
      },
      filename: row.public.filename,
      format: row.format,
      kind: row.kind,
      label: `${row.course_id} — ${row.role} (${row.pages} halaman)`,
      learner_surface_role: row.learner_surface_role,
      license: row.license,
      offline: { dependency_free_after_download: true, initial_fetch_requires_network: true, post_download_reading_is_offline: true },
      order: row.family_reader_order,
      pages: row.pages,
      role: row.role,
      route_granularity: row.route_granularity,
      scope: row.scope,
      sha256: row.sha256,
      state: 'verified',
      title: row.title,
      url: row.public.record_file_download_url,
      verification_scope: 'pass_receipt_bound',
      volume: row.volume,
    }));
    sidecar = {
      '$schema': 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v1/learner-reader-actions-v1.schema.json',
      actions,
      locale: 'id-ID',
      schema_id: 'interlanguage/learner-reader-actions/v1',
      schema_version: '1.0.0',
      snapshot_id: successorSnapshotId,
      source: {
        bytes: compactRouteInput.compactBytes.length,
        generated_utc: compactRouteInput.compact.sealed_authority.generated_utc,
        path: compactRouteRel,
        schema_id: compactRouteInput.compact.schema_id,
        sealed_authority: { bytes: routeFile.bytes.length, generated_utc: routeEvidence.generated_utc, schema_id: routeEvidence.schema_id, sha256: identity(routeFile.bytes).sha256 },
        sha256: identity(compactRouteInput.compactBytes).sha256,
      },
      status: 'verified_route_evidence_projection',
      summary: { action_count: 7, bytes: 35639691, chapter_or_unit_routes_claimed: false, course_count: 4, native_html_claimed: false, pages: 4077, route_granularity: 'whole_file_only', verified_action_count: 7 },
    };
    sidecarBytes = stableObject(sidecar);
  }
  return { routeFile, routeEvidence, rows, sidecar, sidecarBytes, localRehash, compactRouteInput };
}

function baseSnapshotSuccessor(baseIndex, baseBytes) {
  const baseSnapshot = baseIndex.snapshot;
  assert.ok(baseSnapshot && typeof baseSnapshot.snapshot_id === 'string', 'Base adapter index lacks snapshot');
  // The checked-in v2 index is the immutable v0.62.14 snapshot projection.
  // The v0.62.16 correction release carries that exact snapshot identity while
  // supplying the authoritative source commit/tree and Zenodo readback. Keep
  // the source identity repository-relative and point at the exact v0.62.16
  // source archive; never inherit a stale nested supersedes object.
  const priorSource = predecessorRelease.source;
  return {
    snapshot_id: `urn:interlanguage:program-matematika-indonesia:v23-adapters:${args.version}-clp-prepublication:${asOfDate}`,
    snapshot_kind: 'live_successor_overlay',
    as_of: args.asOf,
    central_release_version: args.version,
    central_release_record_doi: null,
    mutable_overlay: true,
    supersedes: {
      snapshot_id: predecessorRelease.snapshot_id,
      central_release_version: predecessorRelease.version,
      central_release_record_doi: predecessorRelease.central_release_record_doi,
      source: priorSource,
    },
    public_replay_state: 'prepublication_local_validation_only',
  };
}

function makeClpPackage(handoff, manifestIdentity) {
  const p = handoff.adapter_package;
  const archivePath = `releases/${args.version}/CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip`;
  // The sealed manifest is the root `manifest.json` member of the adapter ZIP.
  // Keep the exact sealed byte identity, but use the established public
  // release-asset archive-member locator instead of pointing at a staged file
  // that this sanitized projection intentionally does not contain.
  const manifestPath = `release-asset:${archivePath}#manifest.json`;
  return {
    package_id: clpPackageId,
    native_family_id: clpFamilyId,
    proof_kind: 'reversible_lane_adapter',
    contract_version: '2.3.1',
    adapter_version: p.extension_version,
    admission_state: 'admitted_pending_release',
    release_url: null,
    public_asset_url: null,
    planned_release: {
      central_release_version: args.version,
      artifact_path: archivePath,
      public_url_after_release: `https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/${args.version}`,
      state: 'planned_not_public',
    },
    public_replay_status: 'pending_release_local_seal_verified',
    adopted_capabilities: [
      'composite_owner_identity',
      'target_first_exact_mappings',
      'typed_lineage_only_rows',
      'profile_specific_rights',
      'deterministic_jsonl_csv_projection',
      'stream_validated_namespace_sidecar',
      'loss_accounting',
      'learner_pdf_authority',
    ],
    known_limitations: [
      'Prosa buku tidak dipusatkan; backend native pemilik tetap menjadi otoritas.',
      'Rute pembaca hanya tujuh whole-file PDF; tidak ada rute bab/unit/fragmen yang dibuktikan.',
      'Paket adapter pusat menunggu baca-balik publik successor; status ini bukan klaim bahwa PDF mengonsumsi adapter.',
      'Pemetaan lintas profil hanya diklaim pada 3.843 baris lineage_only dan 285.630 target exact sesuai seal; ekuivalensi prosa tidak diklaim.',
    ],
    archive: { path: archivePath, bytes: p.zip.bytes, sha256: p.zip.sha256 },
    manifest: { ...manifestIdentity, path: manifestPath },
    canonical_records: p.canonical_records,
    native_records_preserved: handoff.materialized_scope.native_binding_rows,
    reversible_native_mappings: handoff.materialized_scope.exact_target_first_mappings,
    additional_native_index_rows: handoff.materialized_scope.lineage_only_rows,
    rights_assignments: handoff.materialized_scope.rights_assignments,
    reader_pages: handoff.materialized_scope.reader_pages,
    unit_records: handoff.materialized_scope.units,
    relation_records: handoff.materialized_scope.typed_owner_relations,
    source_translation_pairs: handoff.materialized_scope.translation_state_rows,
    namespace_mappings: handoff.materialized_scope.namespace_sidecar_mappings,
    public_artifacts: 5059,
    native_html_claimed: false,
    unit_or_page_anchors_claimed: false,
    jsonl_csv_table_pairs: 19,
    owner_native_authoritative: true,
    zero_copy: true,
    dataset_id: p.dataset_id,
    extension_id: p.extension_id,
    scope_note: 'Adapter CLP federates empat profil kalkulus native tanpa mengganti sumber pemilik. Identitas gabungan, target-first mapping, hak, status terjemahan, loss accounting, dan rute PDF dipertahankan; machine data tetap sekunder.',
  };
}

function makeClpAdapters(routeData, snapshot) {
  const firstByCourse = new Map();
  for (const row of routeData.rows) if (!firstByCourse.has(row.course_id)) firstByCourse.set(row.course_id, row);
  const courseNames = new Map([
    ['B20', 'Kalkulus Diferensial'],
    ['B30', 'Kalkulus Integral'],
    ['B50', 'Kalkulus Multivariabel'],
    ['B60', 'Kalkulus Vektor'],
  ]);
  return clpRoles.map((roleId) => {
    const row = firstByCourse.get(roleId);
    assert.ok(row, `${roleId}: missing primary reader`);
    return {
      role_id: roleId,
      course: courseNames.get(roleId),
      native_family_id: clpFamilyId,
      adapter_package_id: clpPackageId,
      learner_url: row.public.record_file_download_url,
      learner_runtime_relationship: 'course_link_only_no_adapter_consumption_claim',
      course_specific_route_count: routeData.rows.filter((candidate) => candidate.course_id === roleId).length,
      scope_note: `${roleId} mempertahankan tampilan course-native dan ${routeData.rows.filter((candidate) => candidate.course_id === roleId).length} rute PDF learner-first; paket CLP bersama dihitung sekali dan tidak menyatakan konsumsi adapter oleh PDF.`,
    };
  });
}

function sortAdapters(adapters) {
  return [...adapters].sort((a, b) => (roleOrder.indexOf(a.role_id) - roleOrder.indexOf(b.role_id)) || a.role_id.localeCompare(b.role_id));
}

function sortPackages(packages, adapters) {
  return [...packages].sort((a, b) => {
    const first = (pkg) => Math.min(...adapters.filter((row) => row.adapter_package_id === pkg.package_id).map((row) => roleOrder.indexOf(row.role_id)));
    return first(a) - first(b) || a.package_id.localeCompare(b.package_id);
  });
}

function makeSummary(baseIndex, packages, adapters) {
  const published = new Set(packages.filter((p) => p.admission_state === 'published').map((p) => p.package_id));
  const familyCount = new Set(packages.map((p) => p.native_family_id)).size;
  const baseFamilies = baseIndex.summary?.curriculum_roles === 40 ? 33 : 33;
  return {
    curriculum_roles: 40,
    role_bindings: adapters.length,
    published_role_bindings: adapters.filter((row) => published.has(row.adapter_package_id)).length,
    pending_role_bindings: adapters.filter((row) => !published.has(row.adapter_package_id)).length,
    distinct_adapter_packages: packages.length,
    published_adapter_packages: packages.filter((p) => p.admission_state === 'published').length,
    pending_adapter_packages: packages.filter((p) => p.admission_state !== 'published').length,
    represented_native_families: familyCount,
    unbound_roles: 40 - adapters.length,
    families_without_local_adapter: baseFamilies - familyCount,
    families_without_public_replay_complete_adapter: baseFamilies - new Set(packages.filter((p) => p.admission_state === 'published').map((p) => p.native_family_id)).size,
    package_deduplicated_canonical_records: packages.reduce((sum, p) => sum + p.canonical_records, 0),
  };
}

function addEvidenceUnique(list, entries) {
  const byId = new Map(list.map((item) => [item.evidence_id, item]));
  for (const entry of entries) byId.set(entry.evidence_id, entry);
  return [...byId.values()];
}

function makeSuccessorPatternSchema(baseSchema) {
  const schema = structuredClone(baseSchema);
  const schemaId = 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v2.1/modular-backend-pattern-index-v2.1.schema.json';
  const schemaKey = 'interlanguage/program-matematika-indonesia-modular-backend-pattern-index/v2.1';
  schema.$id = schemaId;
  schema.title = 'Program Matematika Indonesia snapshot-aware backend pattern index v2.1 (successor counts)';
  schema.properties.$schema.const = schemaId;
  schema.properties.schema_id.const = schemaKey;
  schema.properties.schema_version.const = '2.1.0';
  // The successor schema lives under a new URL, but it deliberately reuses
  // the stable v2 snapshot definition.  Make that cross-version reference
  // absolute so validators do not resolve it relative to `/schema/v2.1/`.
  schema.properties.snapshot.$ref = 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v2/v23-adapter-index-v2.schema.json#/$defs/snapshot';
  const integerRange = (maximum) => ({ type: 'integer', minimum: 0, maximum });
  for (const [key, maximum] of [
    ['role_bindings', 40],
    ['published_role_bindings', 40],
    ['pending_role_bindings', 40],
    ['distinct_adapter_packages', 40],
    ['represented_native_families', 33],
    ['unbound_roles', 40],
    ['families_without_local_adapter', 33],
    ['families_without_public_replay_complete_adapter', 33],
  ]) schema.properties.adapter_snapshot.properties[key] = integerRange(maximum);
  return { schema, schemaId, schemaKey, schemaVersion: '2.1.0' };
}

function updatePattern(basePattern, snapshot, adapterIdentity, summary, adapters, patternMeta) {
  const pattern = structuredClone(basePattern);
  pattern.$schema = patternMeta.schemaId;
  pattern.schema_id = patternMeta.schemaKey;
  pattern.schema_version = patternMeta.schemaVersion;
  pattern.recorded_at = asOfDate;
  pattern.snapshot = snapshot;
  pattern.adapter_snapshot = {
    adapter_index: adapterIdentity,
    role_bindings: summary.role_bindings,
    published_role_bindings: summary.published_role_bindings,
    pending_role_bindings: summary.pending_role_bindings,
    distinct_adapter_packages: summary.distinct_adapter_packages,
    represented_native_families: summary.represented_native_families,
    unbound_roles: summary.unbound_roles,
    families_without_local_adapter: summary.families_without_local_adapter,
    families_without_public_replay_complete_adapter: summary.families_without_public_replay_complete_adapter,
  };
  const clpFamily = pattern.families.find((family) => family.native_family_id === clpFamilyId);
  assert.ok(clpFamily, 'Base pattern lacks family-06-clp');
  const bindings = adapters.filter((row) => row.native_family_id === clpFamilyId).map((row) => ({
    role_id: row.role_id,
    adapter_package_id: row.adapter_package_id,
    admission_state: 'admitted_pending_release',
    public_replay_status: 'pending_release_local_seal_verified',
  }));
  clpFamily.adapter_bindings = bindings;
  clpFamily.demonstrated_strengths = [...new Set([
    ...(clpFamily.demonstrated_strengths ?? []),
    'Komposit identity `(native_profile, native_id)` mencegah flattening lintas profil.',
    'Target-first exact mappings dan lineage_only rows mempertahankan loss accounting.',
    'Hak, marker, topology, Q/H/A/S dan status terjemahan dipertahankan per profil.',
    'JSONL/CSV deterministik, namespace sidecar stream-validated, dan negative probes fail-closed.',
    'Tujuh rute PDF whole-file learner-first dicatat dengan byte, halaman, URL, dan SHA-256.',
  ])];
  clpFamily.limitations = [
    'Prosa tidak dipusatkan; empat backend owner-native tetap menjadi otoritas.',
    'Belum ada HTML course-native, EPUB, atau rute unit/fragmen yang dibuktikan.',
    'Baca-balik publik paket adapter successor belum dilakukan pada snapshot ini.',
  ];
  clpFamily.learner_runtime_status = 'Tujuh rute PDF whole-file learner-first; data adapter sekunder dan tidak diklaim dikonsumsi PDF.';
  clpFamily.reversible_exchange_status = 'Paket common-v2.3.1 tersegel dan replay lokal lulus; publikasi successor masih pending.';
  return pattern;
}

function updateFeatureLedger(baseFeature, snapshot, evidence, adapterIdentity, learnerDeliveryIdentity) {
  const feature = structuredClone(baseFeature);
  feature.recorded_at = asOfDate;
  feature.snapshot_id = snapshot.snapshot_id;
  // The inherited v2 evidence row describes the historical nine-binding
  // snapshot.  Keep its evidence id, kind, label, byte count, and hash intact,
  // but point it at the immutable v0.62.16 release copy rather than the
  // mutable working-tree authority path (which is not staged by this builder).
  const inheritedAdapterSnapshot = feature.evidence?.find((item) => item.evidence_id === 'adapter_snapshot_v2');
  assert.ok(inheritedAdapterSnapshot, 'Feature ledger lacks adapter_snapshot_v2 evidence');
  assert.deepEqual({ bytes: inheritedAdapterSnapshot.bytes, sha256: inheritedAdapterSnapshot.sha256 }, {
    bytes: predecessorRelease.adapter_snapshot.bytes,
    sha256: predecessorRelease.adapter_snapshot.sha256,
  }, 'Inherited adapter_snapshot_v2 evidence identity drift');
  inheritedAdapterSnapshot.path = predecessorRelease.adapter_snapshot.path;
  // Rebind the inherited learner-delivery evidence to the current authority
  // bytes.  The v0.62.16 snapshot recorded an older 61,140-byte projection;
  // retaining that identity would make the successor's provenance stale even
  // though the learner-delivery source itself is unchanged by this builder.
  const learnerDeliveryEvidence = feature.evidence?.find((item) => item.evidence_id === 'learner_delivery');
  if (learnerDeliveryEvidence && learnerDeliveryIdentity) {
    learnerDeliveryEvidence.path = 'backend/authority/learner-delivery-v1.json';
    learnerDeliveryEvidence.bytes = learnerDeliveryIdentity.bytes;
    learnerDeliveryEvidence.sha256 = learnerDeliveryIdentity.sha256;
  }
  feature.evidence = addEvidenceUnique(feature.evidence ?? [], evidence);
  const byId = new Map(feature.evidence.map((item) => [item.evidence_id, item]));
  for (const layer of feature.layers) {
    for (const item of layer.features) {
      if (item.feature_id === 'typed_curriculum_graph') item.evidence_ids = [...new Set([...item.evidence_ids, 'clp_route_evidence'])];
      if (item.feature_id === 'deterministic_manifested_builds') item.evidence_ids = [...new Set([...item.evidence_ids, 'clp_package_manifest', 'clp_handoff_inventory'])];
      if (item.feature_id === 'learner_first_routes') item.evidence_ids = [...new Set([...item.evidence_ids, 'clp_route_evidence'])];
      if (item.feature_id === 'zero_copy_component_federation') item.evidence_ids = [...new Set([...item.evidence_ids, 'clp_profile_design'])];
      if (item.feature_id === 'reversible_native_identity_adapters') {
        item.evidence_ids = [...new Set([...item.evidence_ids, 'clp_package_manifest', 'clp_handoff_inventory', 'clp_successor_adapter'])];
        item.limitations = [...new Set([...(item.limitations ?? []), 'Edisi CLP1–4 asli sudah selesai dan publik; paket CLP telah diadmit dan diverifikasi lokal. Yang masih menunggu hanyalah baca-balik publik successor; empat binding bukan pekerjaan terjemahan yang tertunda.'])];
      }
    }
  }
  const interoperability = feature.layers.find((layer) => layer.layer_id === 'interoperability');
  assert.ok(interoperability, 'Feature ledger lacks interoperability layer');
  interoperability.features.push({
    feature_id: 'clp_profile_specific_loss_accounting',
    description_id: 'CLP mencatat identitas komposit, pemetaan target-first, lineage_only, hak per profil, dan rute PDF tanpa mengklaim ekuivalensi prosa.',
    source_pattern_ids: [clpFamilyId, 'manager-federation'],
    evidence_ids: ['clp_profile_design', 'clp_handoff_inventory', 'clp_successor_adapter'],
    implementation_status: 'implemented',
    limitations: ['Validasi publik successor dan route readback belum dilakukan pada snapshot prepublication.'],
  });
  // Keep the variable intentionally used: this assertion catches accidental
  // evidence-id typos before a file is staged.
  for (const layer of feature.layers) for (const item of layer.features) for (const id of item.evidence_ids) assert.ok(byId.has(id) || id === 'clp_successor_adapter', `Unknown feature evidence id: ${id}`);
  return feature;
}

function updateComparison(baseComparison, snapshot, evidence, outputRows) {
  const comparison = structuredClone(baseComparison);
  comparison.recorded_at = asOfDate;
  comparison.snapshot_id = snapshot.snapshot_id;
  comparison.evidence = addEvidenceUnique(comparison.evidence ?? [], evidence);
  comparison.decision_rules = [...new Set([
    ...(comparison.decision_rules ?? []),
    'Hitung paket CLP bersama satu kali; empat binding kursus tidak menggandakan canonical_records.',
    'Pisahkan status rute PDF learner-primary dari status konsumsi adapter pusat.',
  ])];
  comparison.outputs = outputRows;
  return comparison;
}

async function main() {
  const predecessorEvidence = await verifyPredecessorRelease();
  const sealed = await replaySealedCandidate();
  const manifestFile = await readCandidateFile('build_a/manifest.json');
  const manifestSourceIdentity = await hashFile(manifestFile.absolute);
  assert.deepEqual(manifestSourceIdentity, {
    bytes: sealed.handoff.adapter_package.manifest.bytes,
    sha256: sealed.handoff.adapter_package.manifest.sha256,
  }, 'build_a manifest identity drift');
  const profileDesignFile = await readCandidateFile('research/CLP_NATIVE_PROFILE_DESIGN.json');
  const baseFiles = {};
  for (const [key, path] of Object.entries(basePaths)) {
    baseFiles[key] = await readRepoJson(path);
  }
  const learnerDeliveryFile = await readRepoJson('backend/authority/learner-delivery-v1.json');
  const learnerDeliveryIdentity = identity(learnerDeliveryFile.bytes);
  const baseIndex = parseJson(baseFiles.adapter.bytes, basePaths.adapter);
  const basePattern = parseJson(baseFiles.pattern.bytes, basePaths.pattern);
  const baseFeature = parseJson(baseFiles.feature.bytes, basePaths.feature);
  const baseComparison = parseJson(baseFiles.comparison.bytes, basePaths.comparison);
  const patternSchemaFile = await readRepoJson('schemas/course-capsule-v1/v2/modular-backend-pattern-index-v2.schema.json');
  const basePatternSchema = parseJson(patternSchemaFile.bytes, 'modular-backend-pattern-index-v2.schema.json');
  const patternMeta = makeSuccessorPatternSchema(basePatternSchema);
  assert.equal(baseIndex.summary.curriculum_roles, 40);
  assert.equal(basePattern.families.length, 33);
  assert.equal(new Set(baseIndex.adapters.map((row) => row.role_id)).size, baseIndex.adapters.length);
  assert.equal(new Set(baseIndex.packages.map((row) => row.package_id)).size, baseIndex.packages.length);
  assert.ok(!baseIndex.adapters.some((row) => clpRoles.includes(row.role_id)), 'Base already contains a CLP role binding; refusing duplicate admission.');
  assert.ok(!baseIndex.packages.some((row) => row.package_id === clpPackageId || row.native_family_id === clpFamilyId), 'Base already contains CLP package; refusing duplicate admission.');
  const snapshot = baseSnapshotSuccessor(baseIndex, baseFiles.adapter.bytes);
  const routeData = await replayRoutes(sealed.handoff, snapshot.snapshot_id);
  const handoffIdentityBytes = sanitizedIdentityProjection({
    kind: 'sealed_handoff_inventory',
    sourceRef: 'sealed_candidate/HANDOFF_FILE_INVENTORY.json',
    sourceIdentity: identity(sealed.inventoryFile.bytes),
    claims: {
      file_count: sealed.inventory.file_count,
      payload_bytes: sealed.inventory.payload_bytes,
      payload_identity_sha256: sealed.inventory.payload_identity_sha256,
      files: sealed.rechecked.map(({ path, bytes, sha256 }) => ({ name: path.split('/').at(-1), bytes, sha256 })),
    },
  });
  const manifestIdentityBytes = sanitizedIdentityProjection({
    kind: 'sealed_build_manifest',
    sourceRef: 'sealed_candidate/build_a/manifest.json',
    sourceIdentity: manifestSourceIdentity,
    claims: {
      package_id: clpPackageId,
      adapter_version: sealed.handoff.adapter_package.extension_version,
      canonical_records: sealed.handoff.adapter_package.canonical_records,
      physical_files: sealed.handoff.adapter_package.physical_files,
      physical_bytes: sealed.handoff.adapter_package.physical_bytes,
      jsonl_csv_table_pairs: sealed.handoff.adapter_package.tables,
    },
  });
  const routeIdentityBytes = sanitizedIdentityProjection({
    kind: 'sealed_route_evidence',
    sourceRef: 'sealed_candidate/research/CLP_LEARNER_ROUTE_EVIDENCE.json',
    sourceIdentity: identity(routeData.routeFile.bytes),
    claims: {
      schema_id: routeData.routeEvidence.schema_id,
      course_roles: clpRoles,
      actions: routeData.rows.length,
      pages: 4077,
      bytes: 35639691,
      compact_projection: compactRouteRel,
    },
  });
  const profileIdentityBytes = sanitizedIdentityProjection({
    kind: 'sealed_native_profile_design',
    sourceRef: 'sealed_candidate/research/CLP_NATIVE_PROFILE_DESIGN.json',
    sourceIdentity: identity(profileDesignFile.bytes),
    claims: {
      package_id: clpPackageId,
      native_family_id: clpFamilyId,
      roles: clpRoles,
      native_records_preserved: sealed.handoff.materialized_scope.native_binding_rows,
      reversible_native_mappings: sealed.handoff.materialized_scope.exact_target_first_mappings,
      additional_native_index_rows: sealed.handoff.materialized_scope.lineage_only_rows,
      rights_assignments: sealed.handoff.materialized_scope.rights_assignments,
      unit_records: sealed.handoff.materialized_scope.units,
      relation_records: sealed.handoff.materialized_scope.typed_owner_relations,
      capabilities: [
        'composite_owner_identity',
        'target_first_exact_mappings',
        'typed_lineage_only_rows',
        'profile_specific_rights',
        'deterministic_jsonl_csv_projection',
        'stream_validated_namespace_sidecar',
        'loss_accounting',
        'learner_pdf_authority',
      ],
    },
  });
  // The package record retains the exact sealed manifest identity at the
  // conventional successor path.  Its raw bytes are intentionally *not*
  // staged here because the candidate manifest contains workspace `outputs/`
  // references; the sanitized identity envelope below is the public-safe
  // staged evidence.  A later integrator can attach the raw manifest through
  // an explicit, bounded input override.
  const manifestAuthority = { path: `${outputRelRoot}/CLP_PACKAGE_MANIFEST.json`, ...manifestSourceIdentity };
  const clpPackage = makeClpPackage(sealed.handoff, manifestAuthority);
  const clpAdapters = makeClpAdapters(routeData, snapshot);
  const adapters = sortAdapters([...baseIndex.adapters, ...clpAdapters]);
  const packages = sortPackages([...baseIndex.packages, clpPackage], adapters);
  assert.equal(new Set(adapters.map((row) => row.role_id)).size, adapters.length);
  assert.equal(new Set(packages.map((row) => row.package_id)).size, packages.length);
  assert.equal(adapters.filter((row) => row.adapter_package_id === clpPackageId).length, 4);
  const summary = makeSummary(baseIndex, packages, adapters);
  assert.deepEqual(summary, {
    curriculum_roles: 40,
    role_bindings: 13,
    published_role_bindings: 9,
    pending_role_bindings: 4,
    distinct_adapter_packages: 9,
    published_adapter_packages: 8,
    pending_adapter_packages: 1,
    represented_native_families: 9,
    unbound_roles: 27,
    families_without_local_adapter: 24,
    families_without_public_replay_complete_adapter: 25,
    package_deduplicated_canonical_records: 1487386,
  });
  const adapterIndex = {
    $schema: 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v2/v23-adapter-index-v2.schema.json',
    schema_id: 'interlanguage/program-matematika-indonesia-v23-adapter-index/v2',
    schema_version: '2.0.0',
    snapshot,
    policy: { owner_native_authoritative: true, zero_copy: true, machine_data_secondary: true, aggregate_conformance_claim: false },
    summary,
    packages,
    adapters,
  };
  const adapterBytes = stableObject(adapterIndex);
  const adapterIdentity = fileRow(`${outputRelRoot}/v23-adapter-index-v2.json`, adapterBytes);
  const pattern = updatePattern(basePattern, snapshot, adapterIdentity, summary, adapters, patternMeta);
  const patternBytes = stableObject(pattern);
  const patternIdentity = fileRow(successorPatternRel, patternBytes);
  const patternSchemaBytes = stableObject(patternMeta.schema);
  const patternSchemaIdentity = fileRow(successorPatternSchemaRel, patternSchemaBytes);
  const sourceEvidence = [
    ['clp_handoff_inventory', 'adapter_validation', sanitizedEvidenceRels.handoff, handoffIdentityBytes, 'Handoff inventory and aggregate identity replay.', 'sealed_admission_byte'],
    ['clp_package_manifest', 'adapter_manifest', sanitizedEvidenceRels.manifest, manifestIdentityBytes, 'Sanitized identity for the sealed CLP 19-table manifest.', 'sealed_admission_byte'],
    ['clp_route_evidence', 'adapter_validation', compactRouteRel, routeData.compactRouteInput.compactBytes, 'Sanitized seven-route input; sealed route identity is nested.', 'sealed_admission_byte'],
    ['clp_profile_design', 'adapter_validation', sanitizedEvidenceRels.profile, profileIdentityBytes, 'Sanitized identity and metrics for native profile design.', 'sealed_admission_byte'],
    ['clp_zip', 'adapter_validation', `releases/${args.version}/CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip`, null, 'Sealed CLP adapter ZIP identity (external release asset).', 'sealed_admission_byte'],
  ];
  const sourceEvidenceRows = sourceEvidence.map(([id, kind, publicPath, projectedBytes, purpose, immutability]) => {
    const sourceIdentity = projectedBytes
      ? identity(projectedBytes)
      : { bytes: sealed.handoff.adapter_package.zip.bytes, sha256: sealed.handoff.adapter_package.zip.sha256 };
    return { evidence_id: id, kind, path: publicPath, ...sourceIdentity, claim_scope: purpose, immutability };
  });
  const featureEvidence = sourceEvidenceRows.map(({ immutability, ...row }) => row);
  const feature = updateFeatureLedger(baseFeature, snapshot, [
    ...featureEvidence,
    { evidence_id: 'clp_successor_adapter', kind: 'generated_snapshot', ...adapterIdentity, claim_scope: 'CLP package and four additive role bindings in the successor projection.' },
  ], adapterIdentity, learnerDeliveryIdentity);
  const featureBytes = stableObject(feature);
  const featureIdentity = fileRow(`${outputRelRoot}/feature-adoption-provenance-v1.json`, featureBytes);
  const comparisonEvidence = sourceEvidenceRows.map((row) => ({ ...row }));
  const comparison = updateComparison(baseComparison, snapshot, comparisonEvidence, [
    { path: `${outputRelRoot}/v23-adapter-index-v2.json`, schema_id: adapterIndex.schema_id, purpose: 'CLP additive package and four role bindings.' },
    { path: successorPatternRel, schema_id: pattern.schema_id, purpose: '33-family pattern index with CLP binding states.' },
    { path: successorPatternSchemaRel, schema_id: patternMeta.schemaKey, purpose: 'Successor pattern schema with dynamic adapter snapshot counts.' },
    { path: `${outputRelRoot}/feature-adoption-provenance-v1.json`, schema_id: feature.schema_id, purpose: 'Feature decisions and CLP evidence provenance.' },
    { path: `${outputRelRoot}/comparison-evidence-manifest-v1.json`, schema_id: baseComparison.schema_id, purpose: 'Sanitized comparison evidence for the successor.' },
    { path: `${outputRelRoot}/learner-reader-actions-v1.json`, schema_id: routeData.sidecar.schema_id, purpose: 'Seven learner-first PDF actions with exact bytes/pages/hashes.' },
  ]);
  const comparisonBytes = stableObject(comparison);
  const comparisonIdentity = fileRow(`${outputRelRoot}/comparison-evidence-manifest-v1.json`, comparisonBytes);
  const sidecarBytes = routeData.sidecarBytes;
  const sidecarIdentity = fileRow(`${outputRelRoot}/learner-reader-actions-v1.json`, sidecarBytes);
  const outputs = new Map([
    [`${outputRelRoot}/v23-adapter-index-v2.json`, adapterBytes],
    [successorPatternRel, patternBytes],
    [successorPatternSchemaRel, patternSchemaBytes],
    [`${outputRelRoot}/feature-adoption-provenance-v1.json`, featureBytes],
    [`${outputRelRoot}/comparison-evidence-manifest-v1.json`, comparisonBytes],
    [`${outputRelRoot}/learner-reader-actions-v1.json`, sidecarBytes],
    [compactRouteRel, routeData.compactRouteInput.compactBytes],
    [sanitizedEvidenceRels.handoff, handoffIdentityBytes],
    [sanitizedEvidenceRels.manifest, manifestIdentityBytes],
    [sanitizedEvidenceRels.route, routeIdentityBytes],
    [sanitizedEvidenceRels.profile, profileIdentityBytes],
  ]);
  for (const [path, bytes] of outputs) noPublicPathLeak(bytes, path);
  assert.deepEqual(adapterIdentity, fileRow(`${outputRelRoot}/v23-adapter-index-v2.json`, outputs.get(`${outputRelRoot}/v23-adapter-index-v2.json`)));
  assert.deepEqual(patternIdentity, fileRow(successorPatternRel, outputs.get(successorPatternRel)));
  assert.deepEqual(patternSchemaIdentity, fileRow(successorPatternSchemaRel, outputs.get(successorPatternSchemaRel)));
  assert.deepEqual(featureIdentity, fileRow(`${outputRelRoot}/feature-adoption-provenance-v1.json`, outputs.get(`${outputRelRoot}/feature-adoption-provenance-v1.json`)));
  assert.deepEqual(comparisonIdentity, fileRow(`${outputRelRoot}/comparison-evidence-manifest-v1.json`, outputs.get(`${outputRelRoot}/comparison-evidence-manifest-v1.json`)));
  assert.deepEqual(sidecarIdentity, fileRow(`${outputRelRoot}/learner-reader-actions-v1.json`, outputs.get(`${outputRelRoot}/learner-reader-actions-v1.json`)));
  if (args.write) {
    for (const [path, bytes] of outputs) {
      const absolute = assertInside(resolve(stagingRoot, path), stagingRoot, `output ${path}`);
      await mkdir(dirname(absolute), { recursive: true });
      await writeFile(absolute, bytes);
    }
    if (args.copyZip) {
      const zipSource = resolve(candidateRoot, sealed.inventory.files.find((row) => row.path.endsWith('.zip')).path);
      const zipTarget = assertInside(resolve(stagingRoot, `releases/${args.version}/CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip`), stagingRoot, 'ZIP output');
      await mkdir(dirname(zipTarget), { recursive: true });
      await copyFile(zipSource, zipTarget);
      const copied = await hashFile(zipTarget);
      assert.deepEqual(copied, { bytes: sealed.handoff.adapter_package.zip.bytes, sha256: sealed.handoff.adapter_package.zip.sha256 }, 'copied ZIP drift');
    }
  }
  const report = {
    status: 'pass',
    mode: args.write ? 'staging_write' : 'dry_run_read_only',
    successor_version: args.version,
    snapshot_id: snapshot.snapshot_id,
    predecessor: {
      version: predecessorEvidence.version,
      snapshot_id: predecessorEvidence.snapshot_id,
      central_release_record_doi: predecessorEvidence.central_release_record_doi,
      concept_doi: predecessorEvidence.concept_doi,
      git_commit: predecessorEvidence.git_commit,
      git_tree: predecessorEvidence.git_tree,
      source: predecessorEvidence.source,
      adapter_snapshot: predecessorEvidence.adapter_snapshot,
      snapshot_receipt: predecessorEvidence.snapshot_receipt,
      release_notes: predecessorEvidence.release_notes,
      github_receipt: predecessorEvidence.github_receipt,
      zenodo_receipt: predecessorEvidence.zenodo_receipt,
    },
    candidate_replay: {
      root_redacted: true,
      inventory_files: sealed.rechecked.length,
      payload_bytes: sealed.payloadBytes,
      payload_identity_sha256: sealed.inventory.payload_identity_sha256,
      zip_bytes: sealed.handoff.adapter_package.zip.bytes,
      zip_sha256: sealed.handoff.adapter_package.zip.sha256,
    },
    route_replay: {
      actions: routeData.rows.length,
      pages: 4077,
      bytes: 35639691,
      local_rehash: args.skipLocalRouteRehash ? 'skipped_by_explicit_flag' : routeData.localRehash.length,
      compact_input: fileRow(compactRouteRel, routeData.compactRouteInput.compactBytes),
    },
    summary,
    outputs: [...outputs].map(([path, bytes]) => ({ path, ...identity(bytes) })),
    external_release_asset: {
      path: `releases/${args.version}/CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip`,
      bytes: sealed.handoff.adapter_package.zip.bytes,
      sha256: sealed.handoff.adapter_package.zip.sha256,
      copied: Boolean(args.write && args.copyZip),
    },
    notes: [
      'Historical outputs are read-only inputs; no old generated file was modified.',
      'Publication is intentionally not claimed. A later publisher must attach public GitHub/Zenodo readback before changing admission_state.',
      'The successor pattern uses a versioned v2.1 schema because the historical v2 schema pins the old 9-binding/8-package counts; no schema-invalid v2 instance is emitted.',
      'Raw candidate route, profile-design, and build-manifest files are intentionally omitted from staged outputs because they contain workspace outputs/ references; sanitized identity envelopes retain their exact sealed byte/hash identities.',
    ],
    omitted_raw_candidate_inputs: [
      { source_ref: 'sealed_candidate/build_a/manifest.json', bytes: manifestSourceIdentity.bytes, sha256: manifestSourceIdentity.sha256 },
      { source_ref: 'sealed_candidate/research/CLP_LEARNER_ROUTE_EVIDENCE.json', bytes: routeData.routeFile.bytes.length, sha256: identity(routeData.routeFile.bytes).sha256 },
      { source_ref: 'sealed_candidate/research/CLP_NATIVE_PROFILE_DESIGN.json', bytes: profileDesignFile.bytes.length, sha256: identity(profileDesignFile.bytes).sha256 },
    ],
  };
  console.log(JSON.stringify(report, null, 2));
}

main().catch((error) => {
  console.error(`build-v06217-clp-successor: FAIL: ${error.stack ?? error.message ?? error}`);
  process.exitCode = 1;
});
