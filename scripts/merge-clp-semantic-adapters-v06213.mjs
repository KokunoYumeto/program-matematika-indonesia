#!/usr/bin/env node
/**
 * Merge the four CLP course-link semantic-adapter rows into a v0.62.13
 * integration projection.
 *
 * The command is read-only by default.  `--write --output <dir>` writes only
 * narrow staged copies below a caller-selected `tmp/` or `staging/` folder;
 * it never edits an authority file in place.  Existing target rows are either
 * byte-equivalent (and preserved) or cause a fail-closed mismatch error.
 *
 * The manifest evidence deliberately uses the public release-asset member
 * identity.  The local sanitized identity envelope and deterministic receipt
 * are checked before that public locator is emitted; no workspace/tmp path is
 * placed in the resulting authority projection.
 */

import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, realpath, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptFile = fileURLToPath(import.meta.url);
const scriptRoot = resolve(dirname(scriptFile), '..');

const TARGETS = Object.freeze(['B20', 'B30', 'B50', 'B60']);
const EXPECTED_PACKAGE_ID = 'urn:uuid:8dbda99c-2e39-5fc0-a6ff-64a52cb81b26';
const EXPECTED_MANIFEST_BYTES = 31266;
const EXPECTED_MANIFEST_SHA256 = '54b600004e6ce4d903f6890a0a9a5c7c0d03120da896ea57d3c85edf674f00e5';
const EXPECTED_VALIDATION_BYTES = 5077;
const EXPECTED_VALIDATION_SHA256 = 'f52416f69079ce277e2a76db1fc94d3cbd6455b7288773f2f3df77348e88812e';
const EXPECTED_ROUTE_ACTIONS = Object.freeze([
  ['B20', 'textbook'],
  ['B20', 'problembook'],
  ['B30', 'combined_textbook_problembook'],
  ['B50', 'textbook'],
  ['B50', 'problembook'],
  ['B60', 'textbook'],
  ['B60', 'problembook'],
]);
const MANIFEST_RELEASE_LOCATOR =
  'release-asset:releases/v0.62.17/CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip#manifest.json';

const DEFAULTS = Object.freeze({
  integration: 'backend/course-capsule-v1/authority/integration-overrides-v1.json',
  learnerOverrides: 'backend/authority/learner-delivery-overrides-v1.json',
  route: 'backend/course-capsule-v1/authority/clp-family-v231/learner-reader-actions-v1.json',
  manifestIdentity: 'backend/course-capsule-v1/authority/clp-family-v231/evidence/CLP_PACKAGE_MANIFEST.identity.json',
  validation: 'backend/course-capsule-v1/authority/clp-family-v231/evidence/CLP_DETERMINISTIC_AB_VALIDATION_20260901.json',
  output: null,
  receipt: null,
  write: false,
  allowUnverified: false,
});

const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const clone = (value) => structuredClone(value);
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const slash = (value) => value.split('\\').join('/');
const canonicalJson = (value) => `${JSON.stringify(value, null, 2)}\n`;

function skipJsonString(text, start) {
  assert.equal(text[start], '"');
  for (let index = start + 1; index < text.length; index += 1) {
    if (text[index] === '\\') {
      index += 1;
      continue;
    }
    if (text[index] === '"') return index + 1;
  }
  throw new Error('Unterminated JSON string while locating semantic_adapters.');
}

function matchingObjectEnd(text, open) {
  let depth = 0;
  for (let index = open; index < text.length; index += 1) {
    if (text[index] === '"') {
      index = skipJsonString(text, index) - 1;
      continue;
    }
    if (text[index] === '{') depth += 1;
    else if (text[index] === '}') {
      depth -= 1;
      if (depth === 0) return index;
    }
  }
  throw new Error('Unterminated semantic_adapters object.');
}

function semanticAdaptersSpan(text) {
  const needle = '"semantic_adapters"';
  for (let index = 0; index <= text.length - needle.length; index += 1) {
    if (text[index] === '"') {
      if (text.startsWith(needle, index)) {
        let cursor = index + needle.length;
        while (/\s/.test(text[cursor] ?? '')) cursor += 1;
        if (text[cursor] !== ':') continue;
        cursor += 1;
        while (/\s/.test(text[cursor] ?? '')) cursor += 1;
        if (text[cursor] !== '{') continue;
        return { open: cursor, close: matchingObjectEnd(text, cursor) };
      }
      index = skipJsonString(text, index) - 1;
    }
  }
  throw new Error('Could not locate semantic_adapters object in integration overrides.');
}

function sourcePreservingIntegrationBytes(sourceBytes, before, after) {
  const missing = TARGETS.filter((courseId) => !Object.prototype.hasOwnProperty.call(before.semantic_adapters, courseId));
  if (!missing.length) return sourceBytes;
  const source = sourceBytes.toString('utf8');
  const { open, close } = semanticAdaptersSpan(source);
  const newline = source.includes('\r\n') ? '\r\n' : '\n';
  const inner = source.slice(open + 1, close);
  const trailingMatch = inner.match(/[\s]*$/);
  const trailing = trailingMatch?.[0] ?? '';
  const body = inner.slice(0, inner.length - trailing.length);
  const rowText = missing.map((courseId, index) => {
    const serialized = JSON.stringify({ [courseId]: after.semantic_adapters[courseId] }, null, 2);
    const row = serialized.split('\n').slice(1, -1).map((line) => '  ' + line).join(newline);
    return `${row}${index < missing.length - 1 ? ',' : ''}`;
  }).join(newline);
  const patchedText = `${source.slice(0, open + 1)}${body}${body.trim() ? ',' : ''}${newline}${rowText}${trailing}${source.slice(close)}`;
  let reparsed;
  try {
    reparsed = JSON.parse(patchedText);
  } catch (error) {
    throw new Error(`Source-preserving semantic adapter insertion produced invalid JSON: ${error.message}`);
  }
  assert.ok(equivalent(reparsed, after), 'Source-preserving semantic adapter insertion changed unexpected values.');
  return Buffer.from(patchedText, 'utf8');
}

function normalized(value) {
  if (Array.isArray(value)) return value.map(normalized);
  if (isObject(value)) return Object.fromEntries(Object.keys(value).sort().map((key) => [key, normalized(value[key])]));
  return value;
}

function equivalent(left, right) {
  return JSON.stringify(normalized(left)) === JSON.stringify(normalized(right));
}

function changedPointers(before, after, pointer = '') {
  if (equivalent(before, after)) return [];
  if (isObject(before) && isObject(after)) {
    const keys = [...new Set([...Object.keys(before), ...Object.keys(after)])].sort();
    return keys.flatMap((key) => changedPointers(
      before[key],
      after[key],
      `${pointer}/${key.replaceAll('~', '~0').replaceAll('/', '~1')}`,
    ));
  }
  if (Array.isArray(before) && Array.isArray(after)) {
    const length = Math.max(before.length, after.length);
    return Array.from({ length }, (_, index) => changedPointers(before[index], after[index], `${pointer}/${index}`)).flat();
  }
  return [pointer || '/'];
}

function inside(root, candidate) {
  const rootAbs = resolve(root).toLowerCase();
  const candidateAbs = resolve(candidate).toLowerCase();
  return candidateAbs === rootAbs || candidateAbs.startsWith(`${rootAbs}${sep}`);
}

function usage() {
  return `Usage: node scripts/merge-clp-semantic-adapters-v06213.mjs [options]

Read-only by default.  --write requires --output and writes staged copies only.

  --repo <dir>                  repository root (default: script repository)
  --integration <path>          integration-overrides-v1.json
  --learner-overrides <path>    learner-delivery-overrides-v1.json
  --route <path>                canonical CLP learner-reader-actions sidecar
  --manifest-identity <path>    sanitized package-manifest identity envelope
  --validation <path>           canonical 5,077-byte deterministic AB receipt
  --dry-run                     explicit read-only mode (the default)
  --allow-unverified            allow a row with route/manifest evidence only
  --write                       write staged copies (never in place)
  --output <dir>                narrow tmp/ or staging/ output root
  --receipt <path>              receipt path inside --output
  --help                        show this help
`;
}

function parseArgs(argv) {
  const args = { ...DEFAULTS };
  const valueFor = (index, option) => {
    const value = argv[index + 1];
    if (!value || value.startsWith('--')) throw new Error(`${option} requires a value.`);
    return value;
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--help') {
      console.log(usage());
      process.exit(0);
    }
    if (arg === '--write') {
      args.write = true;
      args._writeExplicit = true;
    }
    else if (arg === '--dry-run') args._dryRunExplicit = true;
    else if (arg === '--allow-unverified') args.allowUnverified = true;
    else if (arg === '--repo') args.repo = valueFor(index++, arg);
    else if (arg === '--integration') args.integration = valueFor(index++, arg);
    else if (arg === '--learner-overrides') args.learnerOverrides = valueFor(index++, arg);
    else if (arg === '--route') args.route = valueFor(index++, arg);
    else if (arg === '--manifest-identity') args.manifestIdentity = valueFor(index++, arg);
    else if (arg === '--validation') args.validation = valueFor(index++, arg);
    else if (arg === '--output') args.output = valueFor(index++, arg);
    else if (arg === '--receipt') args.receipt = valueFor(index++, arg);
    else throw new Error(`Unknown option: ${arg}\n\n${usage()}`);
  }
  if (args._writeExplicit && args._dryRunExplicit) throw new Error('--write and --dry-run are mutually exclusive.');
  delete args._writeExplicit;
  delete args._dryRunExplicit;
  return args;
}

function repoRelative(repo, supplied, label, { allowUnsafe = false } = {}) {
  const abs = isAbsolute(supplied) ? resolve(supplied) : resolve(repo, supplied);
  if (!inside(repo, abs)) throw new Error(`${label} must resolve inside the repository.`);
  const rel = slash(relative(repo, abs));
  if (!rel || rel === '.' || rel.startsWith('../') || rel.includes('/../')) {
    throw new Error(`${label} must be a repository-relative file path.`);
  }
  if (!allowUnsafe) {
    const segments = rel.toLowerCase().split('/');
    const forbidden = new Set(['tmp', 'outputs', 'candidate', '04_mirrors', '.git']);
    if (segments.some((segment) => forbidden.has(segment) || /candidate|token|credential|secret/.test(segment))) {
      throw new Error(`${label} is not a public-safe authority path: ${rel}`);
    }
  }
  return { abs, rel };
}

async function identityAt(repo, supplied, label, options = {}) {
  const pathInfo = repoRelative(repo, supplied, label, options);
  let real;
  try {
    real = await realpath(pathInfo.abs);
  } catch (error) {
    if (error?.code === 'ENOENT') throw new Error(`${label} is missing: ${pathInfo.rel}`);
    throw error;
  }
  if (!inside(repo, real)) throw new Error(`${label} resolves outside the repository.`);
  let bytes;
  try {
    bytes = await readFile(pathInfo.abs);
  } catch (error) {
    if (error?.code === 'ENOENT') throw new Error(`${label} is missing: ${pathInfo.rel}`);
    throw error;
  }
  return { ...pathInfo, bytes, byteCount: bytes.length, sha256: sha256(bytes) };
}

async function jsonAt(repo, supplied, label, options = {}) {
  const info = await identityAt(repo, supplied, label, options);
  let value;
  try {
    value = JSON.parse(info.bytes.toString('utf8'));
  } catch (error) {
    throw new Error(`${label} is not valid UTF-8 JSON: ${error.message}`);
  }
  return { ...info, value };
}

function assertIntegrationShape(integration) {
  assert.equal(integration.schema_id, 'interlanguage/open-course-capsule-integration-overrides/v1');
  assert.equal(integration.schema_version, '1.0.0');
  assert.ok(isObject(integration.course_truth), 'integration course_truth must be an object');
  assert.ok(isObject(integration.semantic_adapters), 'integration semantic_adapters must be an object');
  for (const courseId of TARGETS) assert.ok(integration.course_truth[courseId], `Missing course_truth ${courseId}.`);
}

function assertManifestIdentity(identity) {
  assert.equal(identity.value.schema_id, 'interlanguage/clp-successor-source-identity/v1');
  assert.equal(identity.value.kind, 'sealed_build_manifest');
  assert.equal(identity.value.claims?.package_id, EXPECTED_PACKAGE_ID);
  assert.equal(identity.value.source_identity?.bytes, EXPECTED_MANIFEST_BYTES);
  assert.equal(identity.value.source_identity?.sha256, EXPECTED_MANIFEST_SHA256);
}

function routeDate(route) {
  const match = String(route.snapshot_id ?? '').match(/(20\d{2}-\d{2}-\d{2})$/);
  return match?.[1] ?? '2026-09-01';
}

function assertRoute(route) {
  assert.equal(route.schema_id, 'interlanguage/learner-reader-actions/v1');
  assert.equal(route.schema_version, '1.0.0');
  assert.equal(route.locale, 'id-ID');
  assert.equal(route.status, 'verified_route_evidence_projection');
  const expectedSummary = {
    action_count: 7,
    bytes: 35639691,
    course_count: 4,
    pages: 4077,
    verified_action_count: 7,
  };
  for (const [key, value] of Object.entries(expectedSummary)) assert.equal(route.summary?.[key], value, `route summary ${key} mismatch`);
  assert.ok(Array.isArray(route.actions) && route.actions.length === 7);
  const actualPairs = route.actions.map((row) => [row.course_id, row.role]);
  assert.deepEqual(actualPairs, EXPECTED_ROUTE_ACTIONS);
  for (const row of route.actions) {
    assert.ok(TARGETS.includes(row.course_id), `${row.action_id}: unexpected course.`);
    assert.equal(row.state, 'verified');
    assert.equal(row.format, 'application/pdf');
    assert.equal(row.route_granularity, 'whole_file_only');
    assert.ok(Number.isInteger(row.pages) && row.pages > 0);
    assert.ok(Number.isInteger(row.bytes) && row.bytes > 0);
    assert.match(row.sha256 ?? '', /^[0-9a-f]{64}$/);
    assert.match(row.url ?? '', /^https:\/\//);
  }
}

function assertValidation(validation) {
  assert.equal(validation.byteCount, EXPECTED_VALIDATION_BYTES, `deterministic validation receipt must be exactly ${EXPECTED_VALIDATION_BYTES} bytes.`);
  assert.equal(validation.sha256, EXPECTED_VALIDATION_SHA256, 'deterministic validation receipt hash is not the canonical receipt.');
  assert.equal(validation.value.schema_id, 'program-matematika-indonesia/clp-calculus-family-v231-validation/1.0.0');
  assert.equal(validation.value.status, 'PASS');
  assert.equal(validation.value.generic?.status, 'PASS');
  assert.equal(validation.value.clp_family_semantics?.status, 'PASS');
  assert.equal(validation.value.generic?.package_id, EXPECTED_PACKAGE_ID);
  assert.equal(validation.value.generic?.manifest?.bytes, EXPECTED_MANIFEST_BYTES);
  assert.equal(validation.value.generic?.manifest?.sha256, EXPECTED_MANIFEST_SHA256);
  assert.equal(validation.value.package?.manifest_bytes, EXPECTED_MANIFEST_BYTES);
  assert.equal(validation.value.package?.manifest_sha256, EXPECTED_MANIFEST_SHA256);
  assert.equal(validation.value.generic?.deterministic_ab?.byte_identical, true);
  assert.equal(validation.value.generic?.deterministic_ab?.supplied, true);
}

function buildEvidence(routeInfo, validationInfo, route, verified) {
  const date = routeDate(route);
  const evidence = [
    {
      kind: 'central_adapter_manifest',
      locator: MANIFEST_RELEASE_LOCATOR,
      verified_date: date,
      bytes: EXPECTED_MANIFEST_BYTES,
      sha256: EXPECTED_MANIFEST_SHA256,
    },
    {
      kind: 'learner_route_validation',
      locator: routeInfo.rel,
      verified_date: date,
      bytes: routeInfo.byteCount,
      sha256: routeInfo.sha256,
    },
  ];
  if (verified) {
    evidence.push({
      kind: 'deterministic_validation_receipt',
      locator: validationInfo.rel,
      verified_date: date,
      bytes: validationInfo.byteCount,
      sha256: validationInfo.sha256,
    });
  }
  return evidence;
}

function buildAdapter(evidence, status = 'verified') {
  return {
    status,
    contract_version: '2.3.1',
    mapping_scope: 'reversible_native_course_route_adapter',
    evidence,
  };
}

function assertOnlyTargetRowsChanged(before, after) {
  const changed = changedPointers(before, after);
  const allowed = TARGETS.map((id) => `/semantic_adapters/${id}`);
  for (const pointer of changed) {
    assert.ok(allowed.some((prefix) => pointer === prefix || pointer.startsWith(`${prefix}/`)), `Unexpected integration mutation at ${pointer}`);
  }
}

function b60RouteAction(route) {
  const action = route.actions.find((row) => row.course_id === 'B60' && row.role === 'textbook');
  assert.ok(action, 'Missing B60 textbook route action.');
  return action;
}

function learnerIdentity(resource) {
  return {
    status: resource?.status,
    format: resource?.format,
    url: resource?.url,
    bytes: resource?.bytes,
    sha256: resource?.sha256,
    scope: resource?.scope,
  };
}

function expectedLearnerResource(action, date) {
  return {
    status: 'verified',
    format: action.format,
    url: action.url,
    bytes: action.bytes,
    sha256: action.sha256,
    scope: action.scope,
    evidence: {
      kind: 'anonymous_public_release_readback',
      locator: action.record_url ?? action.evidence?.locator,
      verified_date: date,
    },
  };
}

function prepareLearnerOverride(overrides, route, date) {
  assert.equal(overrides.schema_version, '1.0.0');
  assert.ok(isObject(overrides.courses), 'learner-delivery overrides courses must be an object');
  const action = b60RouteAction(route);
  const expected = {
    primary: expectedLearnerResource(action, date),
    pdf: expectedLearnerResource(action, date),
  };
  const hasCurrent = Object.prototype.hasOwnProperty.call(overrides.courses, 'B60');
  const current = overrides.courses.B60;
  if (hasCurrent) {
    if (!isObject(current)) throw new Error('learner-delivery-overrides.courses.B60 exists but is not an object; refusing overwrite.');
    for (const key of ['primary', 'pdf']) {
      if (!equivalent(learnerIdentity(current[key]), learnerIdentity(expected[key]))) {
        throw new Error(`learner-delivery-overrides.courses.B60.${key} identity mismatch; refusing overwrite.`);
      }
    }
    return { value: clone(overrides), action: 'unchanged', changedPointers: [], expected };
  }
  const patched = clone(overrides);
  patched.courses.B60 = expected;
  return {
    value: patched,
    action: 'add',
    changedPointers: ['/courses/B60'],
    expected,
  };
}

async function writeIfNeeded(path, bytes) {
  try {
    const existing = await readFile(path);
    if (!existing.equals(bytes)) throw new Error(`Refusing to overwrite a different staged file: ${path}`);
    return 'unchanged';
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
  }
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, bytes, { flag: 'wx' });
  return 'written';
}

async function outputPath(repo, supplied) {
  if (!supplied) throw new Error('--write requires --output; in-place writes are never supported.');
  const abs = isAbsolute(supplied) ? resolve(supplied) : resolve(repo, supplied);
  if (!inside(repo, abs) || resolve(abs) === resolve(repo)) throw new Error('--output must be a narrow directory inside the repository.');
  const rel = slash(relative(repo, abs));
  const first = rel.toLowerCase().split('/')[0];
  if (!['tmp', 'staging'].includes(first)) throw new Error('--output must be under tmp/ or staging/.');
  // Check the nearest existing ancestor after resolving symlinks.  A lexical
  // inside-repository path must not become an escape hatch to an external
  // directory through a pre-existing junction/symlink.
  let probe = abs;
  while (true) {
    try {
      const real = await realpath(probe);
      if (!inside(repo, real)) throw new Error('--output resolves through a symlink outside the repository.');
      break;
    } catch (error) {
      if (error?.code !== 'ENOENT') throw error;
      const parent = dirname(probe);
      if (parent === probe) throw new Error('--output has no resolvable repository ancestor.');
      probe = parent;
    }
  }
  return { abs, rel };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const repo = resolve(args.repo ?? scriptRoot);
  const integrationInfo = await jsonAt(repo, args.integration, 'integration overrides');
  const learnerInfo = await jsonAt(repo, args.learnerOverrides, 'learner-delivery overrides');
  const routeInfo = await jsonAt(repo, args.route, 'CLP learner route sidecar');
  const manifestIdentityInfo = await jsonAt(repo, args.manifestIdentity, 'CLP manifest identity envelope');
  let validationInfo = null;
  try {
    validationInfo = await jsonAt(repo, args.validation, 'CLP deterministic validation receipt');
  } catch (error) {
    if (!args.allowUnverified || !/ is missing: /.test(error.message)) throw error;
  }

  assertIntegrationShape(integrationInfo.value);
  assertManifestIdentity(manifestIdentityInfo);
  assertRoute(routeInfo.value);
  if (validationInfo) assertValidation(validationInfo);

  const date = routeDate(routeInfo.value);
  const verified = Boolean(validationInfo);
  const evidence = buildEvidence(routeInfo, validationInfo, routeInfo.value, verified);
  const desiredAdapter = buildAdapter(evidence, verified ? 'verified' : 'available_unverified');
  const patchedIntegration = clone(integrationInfo.value);
  const adapterActions = [];
  for (const courseId of TARGETS) {
    const hasCurrent = Object.prototype.hasOwnProperty.call(patchedIntegration.semantic_adapters, courseId);
    const current = patchedIntegration.semantic_adapters[courseId];
    if (hasCurrent && (!isObject(current) || !equivalent(current, desiredAdapter))) {
      const pointers = changedPointers(current, desiredAdapter, `/semantic_adapters/${courseId}`);
      throw new Error(`semantic_adapters.${courseId} exists but mismatches CLP evidence; refusing overwrite (${pointers.join(', ')}).`);
    }
    if (hasCurrent) adapterActions.push({ course_id: courseId, action: 'unchanged', changed_pointers: [] });
    else {
      patchedIntegration.semantic_adapters[courseId] = clone(desiredAdapter);
      adapterActions.push({ course_id: courseId, action: 'add', changed_pointers: [`/semantic_adapters/${courseId}`] });
    }
  }
  assertOnlyTargetRowsChanged(integrationInfo.value, patchedIntegration);
  const integrationChanged = !equivalent(integrationInfo.value, patchedIntegration);
  // Preserve the exact source bytes when no semantic row needs changing.  In
  // particular, a no-op audit must not report a formatting-only projection or
  // create a staged write that rewrites unrelated fields.
  const patchedIntegrationBytes = integrationChanged
    ? sourcePreservingIntegrationBytes(integrationInfo.bytes, integrationInfo.value, patchedIntegration)
    : integrationInfo.bytes;

  const learnerPlan = prepareLearnerOverride(learnerInfo.value, routeInfo.value, date);
  const learnerChanged = learnerPlan.action === 'add';
  // As above, retain the original bytes for an unchanged learner override;
  // canonical serialization is only needed for an actual staged addition.
  const patchedLearnerBytes = learnerChanged
    ? Buffer.from(canonicalJson(learnerPlan.value))
    : learnerInfo.bytes;
  if (args.write && !args.allowUnverified) {
    // The strict default is intentionally explicit even though the canonical
    // validation receipt is checked above.  This guards future callers that
    // add an alternate validation mode without silently downgrading a row.
    assert.equal(desiredAdapter.status, 'verified');
  }

  const writeRoot = args.write ? await outputPath(repo, args.output) : null;
  // Always derive staged destinations from the validated repository-relative
  // identities.  Resolving a caller-supplied absolute path against output
  // would otherwise permit an accidental in-place authority write.
  const integrationDestination = writeRoot ? resolve(writeRoot.abs, integrationInfo.rel) : null;
  const learnerDestination = writeRoot ? resolve(writeRoot.abs, learnerInfo.rel) : null;
  const plannedWrites = [];
  if (integrationChanged) plannedWrites.push({ path: integrationInfo.rel, bytes: patchedIntegrationBytes.length, sha256: sha256(patchedIntegrationBytes) });
  if (learnerChanged) plannedWrites.push({ path: learnerInfo.rel, bytes: patchedLearnerBytes.length, sha256: sha256(patchedLearnerBytes) });

  const receipt = {
    schema_id: 'interlanguage/clp-semantic-adapter-merge-receipt/v1',
    schema_version: '1.0.0',
    recorded_at: `${date}T00:00:00Z`,
    mode: args.write ? 'staging_write' : 'dry_run_read_only',
    target_courses: TARGETS,
    evidence: {
      central_adapter_manifest: { locator: MANIFEST_RELEASE_LOCATOR, bytes: EXPECTED_MANIFEST_BYTES, sha256: EXPECTED_MANIFEST_SHA256 },
      learner_route_validation: { locator: routeInfo.rel, bytes: routeInfo.byteCount, sha256: routeInfo.sha256 },
      ...(validationInfo ? {
        deterministic_validation_receipt: { locator: validationInfo.rel, bytes: validationInfo.byteCount, sha256: validationInfo.sha256 },
      } : {}),
    },
    source_identities: {
      integration_overrides: { path: integrationInfo.rel, bytes: integrationInfo.byteCount, sha256: integrationInfo.sha256 },
      learner_delivery_overrides: { path: learnerInfo.rel, bytes: learnerInfo.byteCount, sha256: learnerInfo.sha256 },
      route_sidecar: { path: routeInfo.rel, bytes: routeInfo.byteCount, sha256: routeInfo.sha256 },
      manifest_identity_envelope: { path: manifestIdentityInfo.rel, bytes: manifestIdentityInfo.byteCount, sha256: manifestIdentityInfo.sha256 },
      ...(validationInfo ? {
        validation_receipt: { path: validationInfo.rel, bytes: validationInfo.byteCount, sha256: validationInfo.sha256 },
      } : {}),
    },
    semantic_adapters: {
      status: desiredAdapter.status,
      contract_version: desiredAdapter.contract_version,
      mapping_scope: desiredAdapter.mapping_scope,
      rows: adapterActions,
      projected: { path: integrationInfo.rel, bytes: patchedIntegrationBytes.length, sha256: sha256(patchedIntegrationBytes) },
    },
    learner_delivery_overrides: {
      B60: { action: learnerPlan.action, changed_pointers: learnerPlan.changedPointers },
      projected: { path: learnerInfo.rel, bytes: patchedLearnerBytes.length, sha256: sha256(patchedLearnerBytes) },
    },
    writes: plannedWrites,
    generated_projections: 'Not written by this script; regenerate course-capsules and manifest after applying a staged integration copy.',
    safety: {
      in_place_authority_mutation: false,
      public_access_changed: false,
      publication_performed: false,
      unrelated_fields_overwritten: false,
    },
  };

  if (args.write) {
    const writeResults = [];
    if (integrationChanged) writeResults.push({ path: slash(relative(repo, integrationDestination)), result: await writeIfNeeded(integrationDestination, patchedIntegrationBytes) });
    if (learnerChanged) writeResults.push({ path: slash(relative(repo, learnerDestination)), result: await writeIfNeeded(learnerDestination, patchedLearnerBytes) });
    const receiptPath = args.receipt
      ? resolve(writeRoot.abs, args.receipt)
      : resolve(writeRoot.abs, 'CLP_SEMANTIC_ADAPTER_MERGE_RECEIPT_20260901.json');
    if (!inside(writeRoot.abs, receiptPath) || resolve(receiptPath) === resolve(writeRoot.abs)) throw new Error('--receipt must remain inside --output.');
    const receiptBytes = Buffer.from(canonicalJson({ ...receipt, write_results: writeResults }));
    const receiptResult = await writeIfNeeded(receiptPath, receiptBytes);
    receipt.write_results = writeResults;
    receipt.receipt = { path: slash(relative(repo, receiptPath)), bytes: receiptBytes.length, sha256: sha256(receiptBytes), result: receiptResult };
  }

  console.log(canonicalJson(receipt));
}

main().catch((error) => {
  console.error(`ERROR: ${error.message}`);
  process.exitCode = 1;
});
