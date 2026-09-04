#!/usr/bin/env node

/*
 * Project the CLP v2.3.1 successor into explicitly versioned public paths.
 *
 * This mapper is intentionally separate from sync-public-schemas.mjs.  The
 * latter owns the historical v2 mirrors and must continue to reproduce the
 * v0.62.16/v0.62.14 snapshot.  This program never targets those paths.  It is
 * read-only by default; --write is required to materialise successor mirrors.
 * Existing successor targets may only be replaced with the explicit
 * --allow-replace-successor flag, and every write is followed by a byte/hash
 * read-back.
 */

import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { access, mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const defaultSourceRoot = projectRoot;
const successorVersion = 'v0.62.17';
const successorAuthority = 'backend/course-capsule-v1/authority/clp-family-v231';
const publicSuccessorRoot = `docs/data/clp-successor/${successorVersion}`;
const patternSchemaUrl =
  'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v2.1/' +
  'modular-backend-pattern-index-v2.1.schema.json';
const clpPackageId = 'urn:uuid:8dbda99c-2e39-5fc0-a6ff-64a52cb81b26';
const clpArchivePath = `releases/${successorVersion}/CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip`;
const clpArchiveIdentity = {
  bytes: 545_418_367,
  sha256: 'f2e2714c5f1349092e8cb574d6495e604086c9df3bc4bdf5bbe5974b5f61360d',
};
const clpManifestIdentity = {
  bytes: 31_266,
  sha256: '54b600004e6ce4d903f6890a0a9a5c7c0d03120da896ea57d3c85edf674f00e5',
};

// Keep the source schema in the canonical schemas tree.  Generated successor
// files are read from --source-root, which can be a narrow builder staging
// directory or the repository root after an integrator has admitted it.
const mappings = [
  {
    id: 'pattern_schema',
    source: 'schemas/course-capsule-v1/v2.1/modular-backend-pattern-index-v2.1.schema.json',
    sourceBase: 'project',
    target: 'docs/schema/v2.1/modular-backend-pattern-index-v2.1.schema.json',
  },
  {
    id: 'pattern_index',
    source: `${successorAuthority}/modular-backend-pattern-index-v2.1.json`,
    sourceBase: 'source',
    target: 'docs/data/modular-backend-pattern-index-v2.1.json',
  },
  {
    id: 'adapter_index',
    source: `${successorAuthority}/v23-adapter-index-v2.json`,
    sourceBase: 'source',
    target: `${publicSuccessorRoot}/v23-adapter-index-v2.json`,
  },
  {
    id: 'feature_ledger',
    source: `${successorAuthority}/feature-adoption-provenance-v1.json`,
    sourceBase: 'source',
    target: `${publicSuccessorRoot}/feature-adoption-provenance-v1.json`,
  },
  {
    id: 'comparison_manifest',
    source: `${successorAuthority}/comparison-evidence-manifest-v1.json`,
    sourceBase: 'source',
    target: `${publicSuccessorRoot}/comparison-evidence-manifest-v1.json`,
  },
  {
    id: 'reader_actions',
    source: `${successorAuthority}/learner-reader-actions-v1.json`,
    sourceBase: 'source',
    target: `${publicSuccessorRoot}/learner-reader-actions-v1.json`,
  },
  {
    id: 'route_input',
    source: `${successorAuthority}/clp-learner-route-input-v1.json`,
    sourceBase: 'source',
    target: `${publicSuccessorRoot}/clp-learner-route-input-v1.json`,
  },
  {
    id: 'handoff_identity',
    source: `${successorAuthority}/evidence/HANDOFF_FILE_INVENTORY.identity.json`,
    sourceBase: 'source',
    target: `${publicSuccessorRoot}/evidence/HANDOFF_FILE_INVENTORY.identity.json`,
  },
  {
    id: 'manifest_identity',
    source: `${successorAuthority}/evidence/CLP_PACKAGE_MANIFEST.identity.json`,
    sourceBase: 'source',
    target: `${publicSuccessorRoot}/evidence/CLP_PACKAGE_MANIFEST.identity.json`,
  },
  {
    id: 'route_identity',
    source: `${successorAuthority}/evidence/CLP_LEARNER_ROUTE_EVIDENCE.identity.json`,
    sourceBase: 'source',
    target: `${publicSuccessorRoot}/evidence/CLP_LEARNER_ROUTE_EVIDENCE.identity.json`,
  },
  {
    id: 'profile_identity',
    source: `${successorAuthority}/evidence/CLP_NATIVE_PROFILE_DESIGN.identity.json`,
    sourceBase: 'source',
    target: `${publicSuccessorRoot}/evidence/CLP_NATIVE_PROFILE_DESIGN.identity.json`,
  },
];

const protectedHistoricalTargets = new Set([
  'docs/data/v23-adapter-index-v2.json',
  'docs/data/modular-backend-pattern-index-v2.json',
  'docs/data/feature-adoption-provenance-v1.json',
  'docs/data/comparison-evidence-manifest-v1.json',
  'docs/schema/v2/v23-adapter-index-v2.schema.json',
  'docs/schema/v2/modular-backend-pattern-index-v2.schema.json',
  'docs/schema/v2/feature-adoption-provenance-v1.schema.json',
  'docs/schema/v2/comparison-evidence-manifest-v1.schema.json',
]);

function parseArgs(argv) {
  const args = {
    sourceRoot: defaultSourceRoot,
    targetRoot: projectRoot,
    write: false,
    allowReplaceSuccessor: false,
    receipt: null,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--write') args.write = true;
    else if (arg === '--allow-replace-successor') args.allowReplaceSuccessor = true;
    else if (arg === '--source-root') args.sourceRoot = argv[++i];
    else if (arg === '--target-root') args.targetRoot = argv[++i];
    else if (arg === '--receipt') args.receipt = argv[++i];
    else if (arg === '--help' || arg === '-h') {
      console.log(
        'Usage: node scripts/sync-clp-v231-successor-public.mjs [options]\n\n' +
        'Read-only by default; historical v2 paths are never targets.\n' +
        '  --source-root <dir>             narrow builder staging/repository root\n' +
        '  --target-root <dir>             root receiving public mirrors (default project)\n' +
        '  --write                         write successor mirrors\n' +
        '  --allow-replace-successor       permit differing existing successor targets\n' +
        '  --receipt <path>                write an optional JSON mapping receipt\n',
      );
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
const sourceRoot = resolve(args.sourceRoot);
const targetRoot = resolve(args.targetRoot);

function assertInside(child, parent, label) {
  const childAbs = resolve(child);
  const parentAbs = resolve(parent);
  const rel = relative(parentAbs, childAbs);
  assert.ok(
    rel === '' || (rel !== '..' && !rel.startsWith(`..${sep}`) && !isAbsolute(rel)),
    `${label} escapes its parent`,
  );
  return childAbs;
}

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function identity(bytes) {
  return { bytes: bytes.length, sha256: sha256(bytes) };
}

function parseJson(bytes, label) {
  try {
    return JSON.parse(bytes.toString('utf8'));
  } catch (error) {
    throw new Error(`${label}: invalid JSON: ${error.message}`);
  }
}

async function exists(path) {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

function rejectPublicPathLeak(bytes, target) {
  const text = bytes.toString('utf8');
  assert.ok(!/(?:^|["'])outputs[\\/]/m.test(text), `${target}: workspace outputs path leaked`);
  assert.ok(!/(?:[A-Za-z]:\\|\\\\)[^\r\n"']+/m.test(text), `${target}: absolute Windows path leaked`);
  assert.ok(!/(?:^|["'])\/(?:Users|home|mnt|tmp|var|private|workspace)(?:\/|["'])/m.test(text), `${target}: absolute Unix/private path leaked`);
}

function safeRootLabel(path, role) {
  const rel = relative(projectRoot, path).replaceAll('\\', '/');
  // Receipts may be mirrored into public evidence.  Treat transient and
  // workspace-only roots as external even when they happen to sit below the
  // repository (for example tmp/ or a copied 04_mirrors/ tree).
  const privateSegment = /(?:^|\/)(?:tmp|outputs|04_mirrors|candidate|staging|private)(?:\/|$)/i;
  if (
    (rel === '' || (!rel.startsWith('..') && !isAbsolute(rel)))
    && !privateSegment.test(rel)
  ) return rel || '.';
  return `external-${role}-root`;
}

function validateSchema(schemaBytes) {
  const schema = parseJson(schemaBytes, 'v2.1 pattern schema');
  assert.equal(schema.$id, patternSchemaUrl, 'v2.1 schema $id drift');
  assert.equal(schema.$schema, 'https://json-schema.org/draft/2020-12/schema', 'v2.1 schema dialect drift');
  assert.equal(schema.properties?.$schema?.const, patternSchemaUrl, 'v2.1 schema $schema const drift');
  assert.equal(
    schema.properties?.schema_id?.const,
    'interlanguage/program-matematika-indonesia-modular-backend-pattern-index/v2.1',
    'v2.1 schema_id const drift',
  );
  assert.equal(schema.properties?.schema_version?.const, '2.1.0', 'v2.1 schema version const drift');
  assert.ok(
    String(schema.properties?.snapshot?.$ref ?? '').startsWith(
      'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v2/',
    ),
    'v2.1 snapshot reference must be an absolute canonical v2 URL',
  );
  return { schema_id: schema.properties.schema_id.const, schema_version: schema.properties.schema_version.const };
}

function validatePattern(patternBytes, schemaMeta) {
  const pattern = parseJson(patternBytes, 'successor pattern index');
  assert.equal(pattern.$schema, patternSchemaUrl, 'successor pattern $schema drift');
  assert.equal(pattern.schema_id, schemaMeta.schema_id, 'successor pattern schema_id drift');
  assert.equal(pattern.schema_version, schemaMeta.schema_version, 'successor pattern schema_version drift');
  assert.equal(pattern.locale, 'id-ID', 'successor pattern locale drift');
  assert.equal(pattern.families?.length, 33, 'successor pattern family denominator drift');
  assert.equal(pattern.adapter_snapshot?.role_bindings, 13, 'successor pattern binding count drift');
  const published = pattern.snapshot?.public_replay_state === 'postpublication_release_assets_readback_complete';
  assert.equal(pattern.adapter_snapshot?.pending_role_bindings, published ? 0 : 4, 'successor pattern pending count drift');
  assert.equal(pattern.adapter_snapshot?.published_role_bindings, published ? 13 : 9, 'successor pattern published count drift');
  assert.equal(pattern.adapter_snapshot?.distinct_adapter_packages, 9, 'successor pattern package count drift');
  assert.equal(pattern.snapshot?.central_release_version, successorVersion, 'successor pattern release drift');
  return {
    schema_id: pattern.schema_id,
    schema_version: pattern.schema_version,
    snapshot_id: pattern.snapshot?.snapshot_id,
    role_bindings: pattern.adapter_snapshot?.role_bindings,
    pending_role_bindings: pattern.adapter_snapshot?.pending_role_bindings,
    distinct_adapter_packages: pattern.adapter_snapshot?.distinct_adapter_packages,
  };
}

function validateAdapter(adapterBytes) {
  const adapter = parseJson(adapterBytes, 'successor adapter index');
  assert.equal(adapter.snapshot?.central_release_version, successorVersion, 'successor adapter release drift');
  const clpPackage = (adapter.packages ?? []).find(
    (row) => row.package_id === clpPackageId,
  );
  assert.ok(clpPackage, 'CLP successor package is missing');
  assert.ok(['admitted_pending_release', 'published'].includes(clpPackage.admission_state), 'CLP package state drift');
  if (clpPackage.admission_state === 'published') {
    assert.equal(clpPackage.public_replay_status, 'published_public_asset_readback_verified');
    assert.equal(clpPackage.release_url, 'https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.17');
    assert.equal(clpPackage.public_asset_url, 'https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v0.62.17/CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip');
    assert.equal(adapter.snapshot.public_replay_state, 'postpublication_release_assets_readback_complete');
    assert.equal(adapter.snapshot.central_release_record_doi, '10.5281/zenodo.22303203');
    assert.equal('planned_release' in clpPackage, false);
  } else {
    assert.equal(clpPackage.public_replay_status, 'pending_release_local_seal_verified');
    assert.equal(clpPackage.release_url, null);
    assert.equal(clpPackage.public_asset_url, null);
  }
  assert.deepEqual(
    clpPackage.archive,
    { path: clpArchivePath, ...clpArchiveIdentity },
    'CLP archive locator/identity drift',
  );
  // The raw manifest is intentionally not staged in the public projection.
  // Bind its sealed identity to the root member of the exact successor ZIP so
  // a missing/dangling filesystem path cannot silently pass mapping.
  assert.deepEqual(
    clpPackage.manifest,
    {
      path: `release-asset:${clpArchivePath}#manifest.json`,
      ...clpManifestIdentity,
    },
    'CLP manifest archive-member locator/identity drift',
  );
  const clpAdapters = (adapter.adapters ?? []).filter(
    (row) => row.adapter_package_id === clpPackageId,
  );
  assert.deepEqual(
    clpAdapters.map((row) => row.role_id).sort(),
    ['B20', 'B30', 'B50', 'B60'],
    'CLP successor role set drift',
  );
  return {
    package_id: clpPackage.package_id,
    admission_state: clpPackage.admission_state,
    archive: clpPackage.archive,
    manifest: clpPackage.manifest,
    role_ids: clpAdapters.map((row) => row.role_id).sort(),
  };
}

function validateSidecar(sidecarBytes) {
  const sidecar = parseJson(sidecarBytes, 'successor reader-action sidecar');
  assert.equal(sidecar.schema_id, 'interlanguage/learner-reader-actions/v1', 'sidecar schema_id drift');
  assert.equal(sidecar.summary?.action_count, 7, 'sidecar action count drift');
  assert.equal(sidecar.summary?.course_count, 4, 'sidecar course count drift');
  assert.equal(sidecar.actions?.length, 7, 'sidecar action array drift');
  return { action_count: sidecar.actions.length, course_count: sidecar.summary.course_count, snapshot_id: sidecar.snapshot_id };
}

async function readMapping(mapping) {
  const base = mapping.sourceBase === 'project' ? projectRoot : sourceRoot;
  const source = assertInside(resolve(base, mapping.source), base, `${mapping.id} source`);
  assert.ok(await exists(source), `${mapping.id}: source missing: ${mapping.source}`);
  const bytes = await readFile(source);
  const target = assertInside(resolve(targetRoot, mapping.target), targetRoot, `${mapping.id} target`);
  assert.ok(!protectedHistoricalTargets.has(mapping.target), `${mapping.id}: historical v2 target is protected`);
  rejectPublicPathLeak(bytes, mapping.target);
  let existing = null;
  if (await exists(target)) existing = await readFile(target);
  // Keep the declared relative locator in `source`; retain the resolved path
  // separately for local I/O so receipts never expose a host filesystem path.
  return { ...mapping, sourcePath: source, target, bytes, existing };
}

async function main() {
  const rows = [];
  for (const mapping of mappings) rows.push(await readMapping(mapping));
  const schemaRow = rows.find((row) => row.id === 'pattern_schema');
  const patternRow = rows.find((row) => row.id === 'pattern_index');
  const adapterRow = rows.find((row) => row.id === 'adapter_index');
  const sidecarRow = rows.find((row) => row.id === 'reader_actions');
  const schemaMeta = validateSchema(schemaRow.bytes);
  const patternMeta = validatePattern(patternRow.bytes, schemaMeta);
  const adapterMeta = validateAdapter(adapterRow.bytes);
  const sidecarMeta = validateSidecar(sidecarRow.bytes);
  assert.equal(sidecarMeta.snapshot_id, patternMeta.snapshot_id, 'reader-action snapshot differs from adapter snapshot');
  if (adapterMeta.admission_state === 'published') {
    for (const [name, expectedBytes, expectedSha] of [
      ['GITHUB_PUBLICATION_RECEIPT_v0.62.17.json', 23105, '1a8d3733c1bda0094c9f30ab94cacf2bd67de213038c4a46f2c2f933b74e1f41'],
      ['ZENODO_PUBLICATION_RECEIPT_v0.62.17.json', 35615, 'b439eef9dcd23b6c39dcf902f04de7e22f30ad1de3189c6c8c50fefe3ec52738'],
    ]) {
      const bytes = await readFile(resolve(projectRoot, name));
      assert.equal(bytes.length, expectedBytes, `${name}: publication receipt size differs`);
      assert.equal(sha256(bytes), expectedSha, `${name}: publication receipt hash differs`);
      assert.equal(parseJson(bytes, name).status, 'pass');
    }
  }

  for (const row of rows) {
    if (row.existing && !row.existing.equals(row.bytes) && !args.allowReplaceSuccessor) {
      throw new Error(`${row.target}: differs; pass --allow-replace-successor for an explicit successor replacement`);
    }
  }

  if (args.write) {
    for (const row of rows) {
      await mkdir(dirname(row.target), { recursive: true });
      await writeFile(row.target, row.bytes);
      const written = await readFile(row.target);
      assert.deepEqual(written, row.bytes, `${row.target}: public mirror byte drift`);
    }
  }

  const files = rows.map((row) => ({
    id: row.id,
    // `mapping.source` is already the deterministic repository/staging
    // locator.  Never serialize the resolved host path (which may point into
    // a private workspace or an `outputs/` handoff directory).
    source: row.source,
    target: relative(targetRoot, row.target).replaceAll('\\', '/'),
    ...identity(row.bytes),
    action: args.write ? 'written_or_verified' : 'would_write',
  }));
  const report = {
    schema_id: 'interlanguage/clp-successor-public-mapping/v1',
    schema_version: '1.0.0',
    status: 'pass',
    mode: args.write ? 'write' : 'dry_run_read_only',
    successor_version: successorVersion,
    // Do not put host-specific absolute paths in a receipt that may be
    // copied into the public evidence tree.  Relative project paths remain
    // useful for local replay; roots outside the project are deliberately
    // represented only by a role label.
    source_root: safeRootLabel(sourceRoot, 'source'),
    target_root: safeRootLabel(targetRoot, 'target'),
    historical_v2_paths_untouched: true,
    successor_pattern: patternMeta,
    successor_adapter: adapterMeta,
    reader_sidecar: sidecarMeta,
    files,
  };
  const output = `${JSON.stringify(report, null, 2)}\n`;
  if (args.receipt) {
    const receipt = assertInside(resolve(projectRoot, args.receipt), projectRoot, 'mapping receipt');
    await mkdir(dirname(receipt), { recursive: true });
    await writeFile(receipt, output, 'utf8');
  }
  console.log(output);
}

main().catch((error) => {
  console.error(`sync-clp-v231-successor-public: FAIL: ${error.stack ?? error.message ?? error}`);
  process.exitCode = 1;
});
