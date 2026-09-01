#!/usr/bin/env node

/**
 * Read-only validator for the CLP v2.3.1 successor projection (v0.62.17).
 *
 * This is deliberately a new, versioned validator.  The historical
 * validate-course-capsule-site-v1.mjs script and its v0.62.14 receipt describe
 * an immutable predecessor and must not be rewritten to absorb this overlay.
 * This validator reads the current authority/public projections and emits a
 * structured result to stdout; it never writes a receipt or changes a file.
 */

import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const docs = resolve(project, 'docs');

const EXPECTED_ROLES = ['A00', 'B10', 'B20', 'B30', 'B50', 'B60', 'C30', 'C40', 'C80', 'C130', 'D20', 'D60', 'D110'];
const CLP_ROLES = ['B20', 'B30', 'B50', 'B60'];
const CLP_ROUTE_COUNTS = { B20: 2, B30: 1, B50: 2, B60: 2 };
const CLP_ACTION_TOTALS = { actions: 7, pages: 4077, bytes: 35639691 };
const CLP_PACKAGE_ID = 'urn:uuid:8dbda99c-2e39-5fc0-a6ff-64a52cb81b26';
const SNAPSHOT_ID = 'urn:interlanguage:program-matematika-indonesia:v23-adapters:v0.62.17-clp-prepublication:2026-09-01';

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const identity = (logical, bytes) => ({ path: logical, bytes: bytes.length, sha256: sha256(bytes) });
const isHttps = (value) => {
  if (typeof value !== 'string' || !value) return false;
  try {
    const parsed = new URL(value);
    return parsed.protocol === 'https:' && !parsed.username && !parsed.password && Boolean(parsed.hostname);
  } catch {
    return false;
  }
};

// These are path-level checks.  Ordinary prose can mention a word such as
// “outputs”; only fields that purport to identify a file or URL are checked.
const unsafePath = /(?:^|[\\/])(?:04_mirrors|tmp|outputs|old stuff)(?:[\\/]|$)|^[A-Za-z]:[\\/]|^\\\\|(?:^|[\\/])(?:\.env|.*(?:token|credential|secret|password).*)(?:$|[\\/])/iu;
const unsafeUrlScheme = /^(?:javascript|data|file|vbscript):/iu;

const checks = [];
const warnings = [];
const failures = [];
const check = (label, fn) => {
  try {
    fn();
    checks.push({ label, status: 'pass' });
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    checks.push({ label, status: 'fail', detail });
    failures.push({ label, detail });
  }
};

const read = async (logical) => {
  const bytes = await readFile(resolve(project, logical));
  return { logical, bytes, value: JSON.parse(bytes.toString('utf8')) };
};

const readText = async (logical) => {
  const bytes = await readFile(resolve(project, logical));
  return { logical, bytes, text: bytes.toString('utf8') };
};

const sameBytes = (left, right, label) => {
  assert.equal(left.bytes.length, right.bytes.length, `${label}: byte count differs (${left.bytes.length} vs ${right.bytes.length})`);
  assert.equal(sha256(left.bytes), sha256(right.bytes), `${label}: SHA-256 differs`);
};

const capsuleRows = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.courses)) return payload.courses;
  throw new Error('course capsule payload is neither an array nor an object with courses[]');
};

const safeRepositoryPath = (label, value) => {
  assert.equal(typeof value, 'string', `${label}: path is not a string`);
  assert.ok(value.length > 0, `${label}: path is empty`);
  // `release-asset:` is a deliberate logical locator used by the successor
  // manifest; validate its repository path after removing the prefix/fragment.
  const stripped = value.replace(/^release-asset:/u, '').split('#', 1)[0];
  assert.ok(!stripped.startsWith('/'), `${label}: absolute path`);
  assert.ok(!stripped.includes('\\'), `${label}: backslash in path`);
  assert.ok(!stripped.split('/').includes('..'), `${label}: traversal path`);
  assert.ok(!unsafePath.test(stripped), `${label}: unsafe path ${value}`);
};

const safePublicUrl = (label, value) => {
  assert.ok(isHttps(value), `${label}: non-HTTPS or credential-bearing URL ${String(value)}`);
  const parsed = new URL(value);
  assert.notEqual(parsed.hostname, 'localhost', `${label}: localhost URL`);
  assert.notEqual(parsed.hostname, '127.0.0.1', `${label}: loopback URL`);
};

const safeHtmlLinks = (html, logical) => {
  const hrefs = [...html.matchAll(/\bhref\s*=\s*["']([^"']+)["']/giu)].map((match) => match[1]);
  assert.ok(hrefs.length > 0, `${logical}: no href links found`);
  for (const href of hrefs) {
    assert.ok(!unsafeUrlScheme.test(href), `${logical}: unsafe URL scheme ${href}`);
    assert.ok(!href.startsWith('//'), `${logical}: protocol-relative URL ${href}`);
    assert.ok(!unsafePath.test(href), `${logical}: unsafe path token in link ${href}`);
    if (href.startsWith('#')) continue;
    if (/^https:\/\//iu.test(href)) {
      safePublicUrl(`${logical} external link`, href);
      continue;
    }
    assert.ok(!/^[a-z][a-z0-9+.-]*:/iu.test(href), `${logical}: unsupported URL scheme ${href}`);
    const localPart = href.split(/[?#]/u, 1)[0];
    const target = resolve(docs, 'backend', localPart);
    assert.ok(target === docs || target.startsWith(`${docs}${sep}`), `${logical}: link escapes docs/ ${href}`);
    assert.ok(existsSync(target), `${logical}: local link target missing ${href}`);
  }
  return hrefs;
};

const main = async () => {
  const files = {};
  const jsonPaths = [
    'backend/course-capsule-v1/authority/clp-family-v231/v23-adapter-index-v2.json',
    'docs/data/clp-successor/v0.62.17/v23-adapter-index-v2.json',
    'backend/course-capsule-v1/authority/clp-family-v231/modular-backend-pattern-index-v2.1.json',
    'docs/data/modular-backend-pattern-index-v2.1.json',
    'backend/course-capsule-v1/authority/clp-family-v231/learner-reader-actions-v1.json',
    'docs/data/clp-successor/v0.62.17/learner-reader-actions-v1.json',
    'backend/course-capsule-v1/authority/clp-family-v231/clp-learner-route-input-v1.json',
    'docs/data/clp-successor/v0.62.17/clp-learner-route-input-v1.json',
    'backend/course-capsule-v1/generated/course-capsules.json',
    'docs/data/course-capsule-v1/course-capsules.json',
  ];
  const textPaths = [
    'docs/backend/index.html',
    'docs/backend/backend.js',
  ];
  const projectionPairs = [
    ['backend/course-capsule-v1/authority/clp-family-v231/v23-adapter-index-v2.json', 'docs/data/clp-successor/v0.62.17/v23-adapter-index-v2.json'],
    ['backend/course-capsule-v1/authority/clp-family-v231/modular-backend-pattern-index-v2.1.json', 'docs/data/modular-backend-pattern-index-v2.1.json'],
    ['backend/course-capsule-v1/authority/clp-family-v231/learner-reader-actions-v1.json', 'docs/data/clp-successor/v0.62.17/learner-reader-actions-v1.json'],
    ['backend/course-capsule-v1/authority/clp-family-v231/clp-learner-route-input-v1.json', 'docs/data/clp-successor/v0.62.17/clp-learner-route-input-v1.json'],
    ['backend/course-capsule-v1/generated/course-capsules.json', 'docs/data/course-capsule-v1/course-capsules.json'],
  ];
  const jsonlPairs = [
    ['backend/course-capsule-v1/generated/course-capsules.jsonl', 'docs/data/course-capsule-v1/course-capsules.jsonl'],
    ['backend/course-capsule-v1/generated/manifest.json', 'docs/data/course-capsule-v1/manifest.json'],
  ];

  for (const logical of jsonPaths) files[logical] = await read(logical);
  for (const logical of textPaths) files[logical] = await readText(logical);
  const awaitableFiles = new Map();
  for (const logical of [...jsonPaths, ...textPaths]) awaitableFiles.set(logical, files[logical]);
  for (const logical of jsonlPairs.flat()) awaitableFiles.set(logical, await readText(logical));
  const source = await readFile(fileURLToPath(import.meta.url));

  const publicIndex = files[jsonPaths[1]].value;
  const publicPattern = files[jsonPaths[3]].value;
  const publicSidecar = files[jsonPaths[5]].value;
  const publicInput = files[jsonPaths[7]].value;
  const authorityCapsules = capsuleRows(files[jsonPaths[8]].value);
  const publicCapsules = capsuleRows(files[jsonPaths[9]].value);
  const index = publicIndex;
  const pattern = publicPattern;
  const sidecar = publicSidecar;
  const routeInput = publicInput;

  check('authority/public successor projection byte parity', () => {
    for (const [authorityPath, publicPath] of projectionPairs) sameBytes(files[authorityPath], files[publicPath], `${authorityPath} ↔ ${publicPath}`);
    for (const [authorityPath, publicPath] of jsonlPairs) {
      const left = awaitableFiles.get(authorityPath);
      const right = awaitableFiles.get(publicPath);
      if (left && right) sameBytes(left, right, `${authorityPath} ↔ ${publicPath}`);
    }
  });

  check('successor adapter index identity and counts', () => {
    assert.equal(index.schema_id, 'interlanguage/program-matematika-indonesia-v23-adapter-index/v2');
    assert.equal(index.schema_version, '2.0.0');
    assert.equal(index.snapshot.snapshot_id, SNAPSHOT_ID);
    assert.equal(index.snapshot.central_release_version, 'v0.62.17');
    assert.equal(index.snapshot.snapshot_kind, 'live_successor_overlay');
    assert.equal(index.summary.curriculum_roles, 40);
    assert.equal(index.summary.role_bindings, 13);
    assert.equal(index.summary.distinct_adapter_packages, 9);
    assert.equal(index.summary.published_role_bindings, 9);
    assert.equal(index.summary.pending_role_bindings, 4);
    assert.equal(index.packages.length, 9);
    assert.equal(index.adapters.length, 13);
    assert.equal(new Set(index.adapters.map((row) => row.role_id)).size, 13);
    assert.deepEqual([...index.adapters.map((row) => row.role_id)].sort(), [...EXPECTED_ROLES].sort());
    const packageIds = new Set(index.packages.map((row) => row.package_id));
    assert.equal(packageIds.size, 9);
    assert.equal(index.packages.filter((row) => row.admission_state === 'published').length, 8);
    assert.equal(index.packages.filter((row) => row.admission_state === 'admitted_pending_release').length, 1);
    assert.equal(index.packages.filter((row) => row.public_replay_status === 'published_public_asset_readback_verified').length, 8);
    assert.equal(index.packages.filter((row) => row.public_replay_status === 'pending_release_local_seal_verified').length, 1);
    const clp = index.packages.find((row) => row.package_id === CLP_PACKAGE_ID);
    assert.ok(clp, 'CLP package row missing');
    assert.equal(clp.native_family_id, 'family-06-clp');
    assert.equal(clp.admission_state, 'admitted_pending_release');
    assert.equal(clp.reader_pages, CLP_ACTION_TOTALS.pages);
    assert.equal(clp.archive.bytes, 545418367);
    assert.equal(clp.archive.sha256, 'f2e2714c5f1349092e8cb574d6495e604086c9df3bc4bdf5bbe5974b5f61360d');
    for (const row of index.packages) {
      safeRepositoryPath(`${row.package_id} archive`, row.archive.path);
      safeRepositoryPath(`${row.package_id} manifest`, row.manifest.path);
      if (row.admission_state === 'published') {
        safePublicUrl(`${row.package_id} release_url`, row.release_url);
        safePublicUrl(`${row.package_id} public_asset_url`, row.public_asset_url);
      } else {
        assert.equal(row.release_url, null);
        assert.equal(row.public_asset_url, null);
        safePublicUrl(`${row.package_id} planned public URL`, row.planned_release.public_url_after_release);
      }
    }
    for (const row of index.adapters) {
      assert.ok(packageIds.has(row.adapter_package_id), `${row.role_id}: package reference missing`);
      safePublicUrl(`${row.role_id} learner_url`, row.learner_url);
      if (row.central_learner_projection) safeRepositoryPath(`${row.role_id} central projection`, row.central_learner_projection.path);
    }
  });

  check('successor pattern index parity and family coverage', () => {
    assert.equal(pattern.schema_id, 'interlanguage/program-matematika-indonesia-modular-backend-pattern-index/v2.1');
    assert.equal(pattern.schema_version, '2.1.0');
    assert.equal(pattern.snapshot.snapshot_id, index.snapshot.snapshot_id);
    assert.equal(pattern.adapter_snapshot.adapter_index.bytes, files[jsonPaths[0]].bytes.length);
    assert.equal(pattern.adapter_snapshot.adapter_index.sha256, sha256(files[jsonPaths[0]].bytes));
    for (const key of ['role_bindings', 'published_role_bindings', 'pending_role_bindings', 'distinct_adapter_packages', 'represented_native_families', 'unbound_roles', 'families_without_local_adapter', 'families_without_public_replay_complete_adapter']) {
      assert.equal(pattern.adapter_snapshot[key], index.summary[key], `adapter snapshot ${key} differs`);
    }
    assert.equal(pattern.families.length, 33);
    const bindings = pattern.families.flatMap((family) => family.adapter_bindings);
    assert.equal(bindings.length, 13);
    assert.deepEqual(bindings.map((row) => row.role_id).sort(), index.adapters.map((row) => row.role_id).sort());
    for (const evidence of pattern.source_evidence) safeRepositoryPath(`pattern source ${evidence.source_id}`, evidence.path);
  });

  check('CLP sidecar route totals and identities', () => {
    assert.equal(sidecar.schema_id, 'interlanguage/learner-reader-actions/v1');
    assert.equal(sidecar.schema_version, '1.0.0');
    assert.equal(sidecar.snapshot_id, index.snapshot.snapshot_id);
    assert.equal(sidecar.locale, 'id-ID');
    assert.equal(sidecar.status, 'verified_route_evidence_projection');
    assert.equal(sidecar.actions.length, CLP_ACTION_TOTALS.actions);
    assert.equal(sidecar.summary.course_count, 4);
    assert.equal(sidecar.summary.action_count, CLP_ACTION_TOTALS.actions);
    assert.equal(sidecar.summary.verified_action_count, CLP_ACTION_TOTALS.actions);
    assert.equal(sidecar.summary.pages, CLP_ACTION_TOTALS.pages);
    assert.equal(sidecar.summary.bytes, CLP_ACTION_TOTALS.bytes);
    assert.deepEqual(sidecar.actions.map((row) => row.order), [1, 2, 3, 4, 5, 6, 7]);
    assert.equal(new Set(sidecar.actions.map((row) => row.action_id)).size, CLP_ACTION_TOTALS.actions);
    assert.deepEqual(Object.fromEntries(CLP_ROLES.map((role) => [role, sidecar.actions.filter((row) => row.course_id === role).length])), CLP_ROUTE_COUNTS);
    assert.equal(sidecar.actions.reduce((total, row) => total + row.pages, 0), CLP_ACTION_TOTALS.pages);
    assert.equal(sidecar.actions.reduce((total, row) => total + row.bytes, 0), CLP_ACTION_TOTALS.bytes);
    for (const action of sidecar.actions) {
      assert.ok(CLP_ROLES.includes(action.course_id), `${action.action_id}: unexpected course`);
      assert.equal(action.state, 'verified');
      assert.equal(action.format, 'application/pdf');
      assert.equal(action.route_granularity, 'whole_file_only');
      assert.equal(action.license, 'CC BY-NC-SA 4.0');
      assert.match(action.sha256, /^[0-9a-f]{64}$/u);
      safePublicUrl(`${action.action_id} URL`, action.url);
      assert.equal(new URL(action.url).hostname, 'zenodo.org');
      assert.equal(action.evidence.status, 'pass_receipt_bound');
      safePublicUrl(`${action.action_id} evidence`, action.evidence.locator);
    }
    safeRepositoryPath('sidecar source path', sidecar.source.path);
  });

  check('CLP route-input parity', () => {
    assert.equal(routeInput.schema_id, 'interlanguage/clp-learner-route-input/v1');
    assert.equal(routeInput.schema_version, '1.0.0');
    assert.equal(routeInput.locale, 'id-ID');
    assert.equal(routeInput.status, 'sanitized_projection_of_sealed_evidence');
    assert.equal(routeInput.routes.length, CLP_ACTION_TOTALS.actions);
    assert.deepEqual(routeInput.summary, { course_count: 4, action_count: 7, pages: 4077, bytes: 35639691 });
    const byCourseOrder = new Map(routeInput.routes.map((row) => [`${row.course_id}|${row.course_reader_order}`, row]));
    for (const action of sidecar.actions) {
      const route = byCourseOrder.get(`${action.course_id}|${action.course_order}`);
      assert.ok(route, `${action.action_id}: route-input row missing`);
      for (const key of ['volume', 'format', 'pages', 'bytes', 'sha256', 'filename', 'url', 'license', 'route_granularity']) {
        assert.equal(route[key], action[key], `${action.action_id}: route-input ${key} differs`);
      }
      safePublicUrl(`${action.action_id} route-input URL`, route.url);
    }
    assert.equal(routeInput.routes.reduce((total, row) => total + row.pages, 0), CLP_ACTION_TOTALS.pages);
    assert.equal(routeInput.routes.reduce((total, row) => total + row.bytes, 0), CLP_ACTION_TOTALS.bytes);
  });

  check('40-course capsule parity and CLP semantic rows', () => {
    assert.equal(authorityCapsules.length, 40);
    assert.equal(publicCapsules.length, 40);
    assert.equal(new Set(publicCapsules.map((row) => row.course_id)).size, 40);
    assert.deepEqual(authorityCapsules.map((row) => row.course_id), publicCapsules.map((row) => row.course_id));
    const byId = new Map(publicCapsules.map((row) => [row.course_id, row]));
    const verified = publicCapsules.filter((row) => row.layers?.interoperability?.semantic_adapter?.status === 'verified');
    assert.equal(verified.length, 13);
    assert.deepEqual(verified.map((row) => row.course_id).sort(), [...EXPECTED_ROLES].sort());
    assert.deepEqual(index.adapters.map((row) => row.role_id).sort(), verified.map((row) => row.course_id).sort());
    const clpPackage = index.packages.find((row) => row.package_id === CLP_PACKAGE_ID);
    for (const role of CLP_ROLES) {
      const capsule = byId.get(role);
      const adapter = index.adapters.find((row) => row.role_id === role);
      assert.ok(capsule, `${role}: capsule missing`);
      assert.ok(adapter, `${role}: successor adapter row missing`);
      const semantic = capsule.layers.interoperability.semantic_adapter;
      assert.equal(semantic.status, 'verified');
      assert.equal(semantic.contract_version, '2.3.1');
      assert.equal(semantic.mapping_scope, 'reversible_native_course_route_adapter');
      assert.equal(capsule.course.title, adapter.course, `${role}: course title drift`);
      assert.equal(capsule.layers.learner.primary.url, adapter.learner_url, `${role}: learner URL drift`);
      assert.equal(semantic.evidence[0].bytes, clpPackage.manifest.bytes);
      assert.equal(semantic.evidence[0].sha256, clpPackage.manifest.sha256);
      assert.equal(semantic.evidence[1].bytes, files[jsonPaths[4]].bytes.length);
      assert.equal(semantic.evidence[1].sha256, sha256(files[jsonPaths[4]].bytes));
      assert.equal(semantic.evidence[2].verified_date, '2026-09-01');
      for (const evidence of semantic.evidence) {
        assert.ok(!unsafePath.test(evidence.locator), `${role}: unsafe semantic evidence locator`);
      }
    }
  });

  check('safe successor links in learner site', () => {
    const html = files['docs/backend/index.html'].text;
    const js = files['docs/backend/backend.js'].text;
    const hrefs = safeHtmlLinks(html, 'docs/backend/index.html');
    assert.ok(hrefs.includes('../data/clp-successor/v0.62.17/learner-reader-actions-v1.json'), 'successor sidecar link missing');
    assert.ok(hrefs.includes('../data/clp-successor/v0.62.17/clp-learner-route-input-v1.json'), 'successor route-input link missing');
    assert.ok(hrefs.includes('../data/clp-successor/v0.62.17/v23-adapter-index-v2.json'), 'successor adapter-index link missing');
    assert.ok(hrefs.includes('../data/modular-backend-pattern-index-v2.1.json'), 'successor pattern-index link missing');
    assert.ok(hrefs.includes('../data/course-capsule-v1/learner-reader-actions-v1.json'), 'integrated sidecar link missing');
    assert.ok(js.includes("'../data/clp-successor/v0.62.17/learner-reader-actions-v1.json'"), 'backend fallback URL missing');
    assert.ok(!unsafePath.test(js), 'backend.js contains an unsafe path token');
    // Legacy links are allowed, but make their historical nature observable
    // rather than silently treating them as the successor projection.
    if (hrefs.includes('../data/v23-adapter-index-v2.json')) {
      assert.match(html, /Indeks adapter historis v2[^<]*v0\.62\.14/u, 'legacy adapter link is not clearly labeled historical');
      warnings.push('legacy v2 adapter index link remains on the page; successor validator treats it as historical, not canonical');
    }
  });

  const fileIdentities = {};
  for (const [logical, entry] of Object.entries(files)) fileIdentities[logical] = identity(logical, entry.bytes);
  for (const logical of jsonlPairs.flat()) {
    const entry = awaitableFiles.get(logical);
    fileIdentities[logical] = identity(logical, entry.bytes);
  }
  const result = {
    status: failures.length ? 'fail' : 'pass',
    validator: 'interlanguage/course-capsule-site-successor-v231',
    validator_version: '1.0.0',
    read_only: true,
    files_written: [],
    snapshot_id: index.snapshot.snapshot_id,
    counts: {
      courses: publicCapsules.length,
      verified_semantic_adapters: publicCapsules.filter((row) => row.layers?.interoperability?.semantic_adapter?.status === 'verified').length,
      successor_role_bindings: index.summary.role_bindings,
      successor_distinct_packages: index.summary.distinct_adapter_packages,
      clp_routes: sidecar.actions.length,
      clp_pages: sidecar.summary.pages,
      clp_bytes: sidecar.summary.bytes,
    },
    checks,
    warnings,
    failures,
    artifacts: {
      validator: { path: 'scripts/validate-course-capsule-site-successor-v231.mjs', bytes: source.length, sha256: sha256(source) },
      files: fileIdentities,
    },
  };
  console.log(JSON.stringify(result, null, 2));
  if (failures.length) process.exitCode = 1;
};

try {
  await main();
} catch (error) {
  const detail = error instanceof Error ? error.stack || error.message : String(error);
  console.error(JSON.stringify({
    status: 'fail',
    validator: 'interlanguage/course-capsule-site-successor-v231',
    validator_version: '1.0.0',
    read_only: true,
    files_written: [],
    failures: [{ label: 'startup', detail }],
  }, null, 2));
  process.exitCode = 1;
}
