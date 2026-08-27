import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { copyFile, cp, mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const workspace = resolve(project, '../../..');
const transition = resolve(project, 'scripts/advance-curriculum-authority-v059.mjs');
const admissionPath = resolve(workspace, 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/113_CENTRAL_V059_ADMISSION_MANIFEST_20260827.json');
const readersPath = resolve(workspace, 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/114_PUBLIC_OWNER_HTML_ROUTE_READBACK_20260827.json');
const authoritySource = resolve(project, 'backend/authority/curriculum-authority-v1.json');
const v22Package = resolve(project, 'backend/v2.2/packages/a00-openstax-prealgebra-v0.1.0');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');

function run(args) {
  const result = spawnSync(process.execPath, [transition, ...args], { encoding: 'utf8' });
  assert.equal(result.status, 0, `${result.stderr}\n${result.stdout}`);
  return JSON.parse(result.stdout);
}

function runFail(args) {
  const result = spawnSync(process.execPath, [transition, ...args], { encoding: 'utf8' });
  assert.notEqual(result.status, 0, 'Expected transition command to fail closed.');
  return `${result.stderr}\n${result.stdout}`;
}

function validateJson(schemaPath, dataPath) {
  const code = "import json,jsonschema,sys; schema=json.load(open(sys.argv[1],encoding='utf-8')); data=json.load(open(sys.argv[2],encoding='utf-8')); jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).validate(data)";
  const result = spawnSync('python', ['-c', code, schemaPath, dataPath], { encoding: 'utf8' });
  assert.equal(result.status, 0, `${result.stderr}\n${result.stdout}`);
}

function validateJsonFail(schemaPath, dataPath) {
  const code = "import json,jsonschema,sys; schema=json.load(open(sys.argv[1],encoding='utf-8')); data=json.load(open(sys.argv[2],encoding='utf-8')); jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).validate(data)";
  const result = spawnSync('python', ['-c', code, schemaPath, dataPath], { encoding: 'utf8' });
  assert.notEqual(result.status, 0, 'Expected JSON Schema validation to fail closed.');
}

const tempProject = await mkdtemp(resolve(tmpdir(), 'pmi-v059-transition-'));
try {
  const authorityTarget = resolve(tempProject, 'backend/authority/curriculum-authority-v1.json');
  await mkdir(dirname(authorityTarget), { recursive: true });
  await copyFile(authoritySource, authorityTarget);
  const predecessorBytes = await readFile(authorityTarget);
  const predecessor = JSON.parse(predecessorBytes.toString('utf8'));
  const sourceCommit = predecessor.catalog.sourceCommit;
  const common = [
    '--project-root', tempProject,
    '--admission-manifest', admissionPath,
    '--owner-reader-manifest', readersPath,
    '--v22-package', v22Package,
    '--record-id', '22133203',
    '--source-commit', sourceCommit,
    '--snapshot-date', '2026-08-27',
    '--record-count', '2463',
    '--dataset-count', '34',
    '--course-count', '40',
    '--reader-surfaces', '144',
    '--web-routes', '43',
    '--identity-crosswalks', '2122',
    '--publication-events', '63',
    '--qa-events', '16',
  ];

  const seedResult = run(['seed', ...common]);
  assert.equal(seedResult.completed_roles, 19);
  assert.equal(seedResult.completed_records, 18);
  const seedPath = resolve(tempProject, 'backend/authority/catalogs/program-matematika-indonesia-catalog-v0.59.0.json');
  const seededCatalog = JSON.parse(await readFile(seedPath, 'utf8'));
  const v22 = seededCatalog.program.backend.federationV22;
  assert.equal(v22.canonicalPackage.fileCount, 36);
  assert.equal(v22.canonicalPackage.bytes, 1720752);
  assert.equal(v22.zeroCopy.nativeRecordsReferenced, 519678);
  assert.equal(v22.zeroCopy.nativeRecordsCopied, 0);
  assert.equal(v22.projection.records, 1313);
  assert.equal(v22.projection.identityMapRows, 92);
  assert.equal(v22.deterministicReplay.sha256, '8a2bf0eb8cc68f538867695d5d7d88cbf5874751576ee304e1328f3e4b163861');
  assert.equal(v22.package, 'https://zenodo.org/records/22133203/files/program-matematika-indonesia-backend-v2.2-pilot-v0.59.0.zip?download=1');
  assert.equal(v22.githubPackage, 'https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v0.59.0/program-matematika-indonesia-backend-v2.2-pilot-v0.59.0.zip');

  const tamperedPackage = resolve(tempProject, 'tampered-v22');
  await cp(v22Package, tamperedPackage, { recursive: true });
  const tamperedManifestPath = resolve(tamperedPackage, 'manifest.json');
  await writeFile(tamperedManifestPath, Buffer.concat([await readFile(tamperedManifestPath), Buffer.from(' ')]));
  const tamperedOptions = [...common];
  tamperedOptions[tamperedOptions.indexOf('--v22-package') + 1] = tamperedPackage;
  const failure = runFail(['seed', ...tamperedOptions, '--dry-run']);
  assert.match(failure, /Backend v2\.2 package byte count changed|Backend v2\.2 manifest\.json identity changed/);

  const admission = JSON.parse(await readFile(admissionPath, 'utf8'));
  const ownerReaders = JSON.parse(await readFile(readersPath, 'utf8'));
  const readerByCourse = new Map(ownerReaders.routes.map((row) => [row.course_id, row]));
  const records = admission.admissions.map((row, index) => {
    const reader = readerByCourse.get(row.course_id);
    const url = reader?.url ?? row.learner_route;
    const expectedAction = reader || row.format === 'pdf' ? 'learn' : 'offline';
    return {
      id: `urn:uuid:00000000-0000-4000-8000-${String(index + 1).padStart(12, '0')}`,
      record_type: 'reader_surface',
      payload: {
        url,
        course_ids: [row.course_id],
        actions: [expectedAction],
        publication_state: reader ? 'public' : 'catalog_declared',
        evidence_kind: reader ? 'public_readback' : 'catalog_declared',
        evidence_sha256: reader
          ? 'e16d1a28ad973593edf44dfbce081f636cd3df4febdd097c0b29cd8eed5ed04e'
          : seedResult.sha256,
      },
    };
  });
  for (let index = records.length; index < 2463; index += 1) {
    records.push({
      id: `urn:uuid:10000000-0000-4000-8000-${String(index + 1).padStart(12, '0')}`,
      record_type: 'qa_event',
      payload: { synthetic_transition_test_fixture: true },
    });
  }

  const federationRelative = 'backend/v2/program-matematika-indonesia-federation-v0.4.1-test';
  const federationRoot = resolve(tempProject, federationRelative);
  await mkdir(federationRoot, { recursive: true });
  const recordsBytes = Buffer.from(`${records.map((row) => JSON.stringify(row)).join('\n')}\n`, 'utf8');
  await writeFile(resolve(federationRoot, 'records.jsonl'), recordsBytes);
  const manifest = {
    dataset_version: 'program-matematika-indonesia-federation-v0.4.1',
    record_count: 2463,
    record_counts: {
      datasets: 34,
      courses: 40,
      reader_surfaces: 144,
      web_routes: 43,
      identity_crosswalks: 2122,
      publication_events: 63,
      qa_events: 16,
    },
    files: [{ path: 'records.jsonl', bytes: recordsBytes.length, sha256: sha256(recordsBytes) }],
  };
  const manifestBytes = canonical(manifest);
  await writeFile(resolve(federationRoot, 'manifest.json'), manifestBytes);
  const validation = {
    result: 'pass',
    checks: {
      record_count: 2463,
      records_jsonl_sha256: sha256(recordsBytes),
      manifest_sha256: sha256(manifestBytes),
    },
  };
  await writeFile(resolve(federationRoot, 'validation_report.json'), canonical(validation));

  const promoteResult = run(['promote', ...common, '--federation-relative', federationRelative]);
  assert.equal(promoteResult.new_overlays, 10);
  assert.equal(promoteResult.overlays, predecessor.public_readback_overlays.length + 10);

  const historyBytes = await readFile(resolve(tempProject, 'backend/authority/history/curriculum-authority-v0.58.0.json'));
  assert.deepEqual(historyBytes, predecessorBytes);
  const successor = JSON.parse(await readFile(authorityTarget, 'utf8'));
  assert.equal(successor.catalog.program.version, '0.59.0');
  assert.equal(successor.catalog.counts.completedPublicCourseRoles, 19);
  assert.equal(successor.catalog.counts.completedPublicRecords, 18);
  assert.deepEqual(
    successor.catalog.courses.find((row) => row.id === 'B95'),
    predecessor.catalog.courses.find((row) => row.id === 'B95'),
  );
  assert.equal(successor.public_readback_overlays.length, predecessor.public_readback_overlays.length + 10);
  assert.equal(successor.lineage.predecessor_authority.sha256, sha256(predecessorBytes));
  validateJson(
    resolve(project, 'schemas/catalog-v1.schema.json'),
    seedPath,
  );
  validateJson(resolve(project, 'schemas/v1/curriculum-authority-v1.schema.json'), authorityTarget);
  const invalidCatalog = structuredClone(successor.catalog);
  invalidCatalog.program.backend.federationV22.zeroCopy.nativeRecordsCopied = 1;
  const invalidCatalogPath = resolve(tempProject, 'invalid-v22-catalog.json');
  await writeFile(invalidCatalogPath, canonical(invalidCatalog));
  validateJsonFail(resolve(project, 'schemas/catalog-v1.schema.json'), invalidCatalogPath);
  const invalidAuthority = structuredClone(successor);
  invalidAuthority.catalog.program.backend.federationV22.canonicalPackage.manifest.sha256 = '0'.repeat(64);
  const invalidAuthorityPath = resolve(tempProject, 'invalid-v22-authority.json');
  await writeFile(invalidAuthorityPath, canonical(invalidAuthority));
  validateJsonFail(resolve(project, 'schemas/v1/curriculum-authority-v1.schema.json'), invalidAuthorityPath);
  console.log(JSON.stringify({
    result: 'pass',
    seed_sha256: seedResult.sha256,
    successor_sha256: promoteResult.sha256,
    predecessor_history_sha256: sha256(historyBytes),
    new_overlays: promoteResult.new_overlays,
  }, null, 2));
} finally {
  await rm(tempProject, { recursive: true, force: true });
}
