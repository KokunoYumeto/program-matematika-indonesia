import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { access, mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const authorityRoot = 'backend/course-capsule-v1/authority';
const snapshotInputRoot = `${authorityRoot}/snapshot-inputs/live-v1-overlay-20260831`;
const schemaRoot = 'schemas/course-capsule-v1/v2';
const publicDataRoot = 'docs/data';
const publicSchemaRoot = 'docs/schema/v2';
const recordedAt = '2026-09-01';
const snapshotId = 'urn:interlanguage:program-matematika-indonesia:v23-adapters:v0.62.14-postpublication:2026-09-01';
const predecessorSnapshotId = 'urn:interlanguage:program-matematika-indonesia:v23-adapters:v0.62.14-prepublication:2026-08-31';

const paths = {
  releaseAdapter: 'releases/v0.62.13/v23-adapter-index-v1.json',
  releasePattern: 'releases/v0.62.13/modular-backend-pattern-index-v1.json',
  releaseSchema: 'releases/v0.62.13/v23-adapter-index-v1.schema.json',
  releaseMethod: 'releases/v0.62.13/MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md',
  releasedV2Snapshot: 'releases/v0.62.14/v23-adapter-index-v2.json',
  githubV06214Receipt: 'GITHUB_PUBLICATION_RECEIPT_v0.62.14.json',
  zenodoV06214Receipt: 'PUBLICATION_RECEIPT_v0.62.14.json',
  liveAdapter: `${snapshotInputRoot}/v23-adapter-index-v1.live-overlay-source.json`,
  livePattern: `${snapshotInputRoot}/modular-backend-pattern-index-v1.live-overlay-source.json`,
  liveSchema: `${snapshotInputRoot}/v23-adapter-index-v1.live-overlay-schema-source.json`,
  judsonAdmission: 'backend/course-capsule-v1/adapters/judson-v231/ADMISSION.json',
  judsonManifest: 'backend/course-capsule-v1/adapters/judson-v231/manifest.json',
  judsonChapters: 'docs/backend/judson/chapters.json',
  openLogicAdmission: 'backend/course-capsule-v1/adapters/openlogic-v231/ADMISSION.json',
  openLogicManifest: 'backend/course-capsule-v1/adapters/openlogic-v231/manifest.json',
  openLogicRoute: 'docs/backend/openlogic/learner-route.json',
  openLogicValidation: 'docs/backend/openlogic/validation.json',
  c130Admission: 'backend/course-capsule-v1/adapters/c130-v231/ADMISSION.json',
  c130Manifest: 'backend/course-capsule-v1/adapters/c130-v231/manifest.json',
  c130Route: 'docs/backend/c130/learner-route.json',
  c130Validation: 'docs/backend/c130/validation.json',
  c130AuthorityReplay: 'backend/course-capsule-v1/validation/C130_AUTHORITY_REPLAY_RECEIPT_20260901.json',
  terminology: `${authorityRoot}/native-terminology-qa/unib-teori-bilangan-20260831/terminology_concordance.json`,
  terminologyPolicy: `${authorityRoot}/terminology-policy-v1/canonical-register-policy.json`,
  designPolicy: `${authorityRoot}/backend-design-policy-v1.json`,
  capsuleManifest: 'backend/course-capsule-v1/generated/manifest.json',
  learnerDelivery: 'backend/authority/learner-delivery-v1.json',
  adapterSchema: `${schemaRoot}/v23-adapter-index-v2.schema.json`,
  patternSchema: `${schemaRoot}/modular-backend-pattern-index-v2.schema.json`,
  featureSchema: `${schemaRoot}/feature-adoption-provenance-v1.schema.json`,
  comparisonSchema: `${schemaRoot}/comparison-evidence-manifest-v1.schema.json`,
};

const expected = new Map([
  [paths.releaseAdapter, { bytes: 11370, sha256: '31e45fc3a852b1d1b7742ac66d5d919aa1d229feff408913951018451f755381' }],
  [paths.releasePattern, { bytes: 41452, sha256: '89436f3c319057a87aef82aae7e53f5a0c484193cd92a9c8e293f1b52198f391' }],
  [paths.releaseSchema, { bytes: 4933, sha256: 'c84b160115f6b8e45e7b466899e4081fac02947df93934bcd50e6dedc3559fa7' }],
  [paths.releaseMethod, { bytes: 32070, sha256: 'c30745104ae42a0f29aa3399bb4ef3415c413dba241b1ac494525759214e5536' }],
  [paths.releasedV2Snapshot, { bytes: 29806, sha256: '99d7ee51454981a29f2d03ed493ea400520c605141fe20b58d3c4aea64aedf78' }],
  [paths.githubV06214Receipt, { bytes: 88060, sha256: '8a3883c811574864f0d40f029d1f48ca13870327feb0e9048cd3cad1d1abf390' }],
  [paths.zenodoV06214Receipt, { bytes: 58227, sha256: 'e34bdc951961bf6c18d4ffacfb80fc2fda411f02cba7de001c05ae6898229ad8' }],
  [paths.liveAdapter, { bytes: 18002, sha256: 'ec20bc7e9f0637f5b7b3af0d86698b697b70e66eca34cdb7330e4cdf16d705e0' }],
  [paths.livePattern, { bytes: 41704, sha256: 'af92591838cbe949fa52e5f23d8b57478b1bd649d9a8f56bf47c9fb866d08bb8' }],
  [paths.liveSchema, { bytes: 5029, sha256: '0c25d6f83a293a58f30ba64ac16a50a6effed583368cb88e1a73d59a8642b1a6' }],
  [paths.judsonAdmission, { bytes: 20715, sha256: '0c73d1be90d3a0318b70293eccf7b5ec58b41f323fbb2639b5c12b4451783e74' }],
  [paths.judsonManifest, { bytes: 28845, sha256: '00b80a3f7406c96b375ddb390981dbd0a1f1e3d41e0d240c93b194694521c28a' }],
  [paths.judsonChapters, { bytes: 33323, sha256: '5e806d9866a619e381d37058288aa95e6af841252f66d9106aa7d5a265a11200' }],
  [paths.openLogicAdmission, { bytes: 13623, sha256: '2a86c41e92f9c9ef7e215448967998504bd4c16e7ba8e680d795d155aebef9a7' }],
  [paths.openLogicManifest, { bytes: 22315, sha256: '01974670c902a50d3e0166214f665286e0030a270a781a56413976be52ca4b01' }],
  [paths.openLogicRoute, { bytes: 2485, sha256: 'e4a859bae966c0cc6272a814273c882b79cb7136f83ae83c147559c530921414' }],
  [paths.openLogicValidation, { bytes: 2867, sha256: '4774d889bf52244ef22181b0c90cfa2826ee4da401193d8229d2ac67181be6bc' }],
  [paths.c130Admission, { bytes: 4889, sha256: 'b311ab7d2a6a86af40174d051fbd8ef273a8536b34f0af77b76e5a1ce9b3397e' }],
  [paths.c130Manifest, { bytes: 22488, sha256: 'cad2922d9bd1facb33cc9d54a9836bb168fe0b8d996d9d4ef2e5d8c26053f239' }],
  [paths.c130Route, { bytes: 9930, sha256: '8114562c963295577d8f845719061febed5993b5cbbe5fc4beb8ba235d7fd709' }],
  [paths.c130Validation, { bytes: 6636, sha256: '6d9fa92226d7eee2ab29aba647d3cca0cee80b6cc2ee0bb0e14642216f9c8ae7' }],
  [paths.c130AuthorityReplay, { bytes: 2977, sha256: '7cf3be9570c59f8fa1f35ea83b54e6ca2add842a19c65da3751a5a609dcdc09b' }],
  [paths.terminology, { bytes: 12407, sha256: 'd36a33be7b2dbd5d3a921f32f2b2f5dff81bc8e98d9ff66781314d9251167aa8' }],
  [paths.terminologyPolicy, { bytes: 20125, sha256: 'c3bc63376dfeac2427703cc53635c50418c1a5db93abe3074ad65aa760b1acaa' }],
  [paths.designPolicy, { bytes: 2816, sha256: '2369d55d6faa699139b830e68ab317f9961f23e329e004408622726eb1c776d2' }],
]);

const hash = (bytes) => createHash('sha256').update(bytes).digest('hex');
const identity = (bytes) => ({ bytes: bytes.length, sha256: hash(bytes) });
const sortValue = (value) => {
  if (Array.isArray(value)) return value.map(sortValue);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sortValue(value[key])]));
  }
  return value;
};
const stable = (value) => Buffer.from(`${JSON.stringify(sortValue(value), null, 2)}\n`);
const slug = (value) => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
  .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const fileRow = (path, bytes) => ({ path, ...identity(bytes) });

const sourceBytes = new Map();
const load = async (path) => {
  if (!sourceBytes.has(path)) sourceBytes.set(path, await readFile(resolve(root, path)));
  return sourceBytes.get(path);
};
const loadJson = async (path) => JSON.parse((await load(path)).toString('utf8'));
const exists = async (path) => {
  try { await access(resolve(root, path)); return true; } catch { return false; }
};

for (const path of Object.values(paths)) await load(path);
for (const [path, expectedIdentity] of expected) {
  assert.deepEqual(identity(await load(path)), expectedIdentity, `${path}: pinned identity drift`);
}

const releaseAdapter = await loadJson(paths.releaseAdapter);
const releasePattern = await loadJson(paths.releasePattern);
const releasedV2Snapshot = await loadJson(paths.releasedV2Snapshot);
const githubV06214Receipt = await loadJson(paths.githubV06214Receipt);
const zenodoV06214Receipt = await loadJson(paths.zenodoV06214Receipt);
const liveAdapter = await loadJson(paths.liveAdapter);
const livePattern = await loadJson(paths.livePattern);
const judsonAdmission = await loadJson(paths.judsonAdmission);
const judsonManifest = await loadJson(paths.judsonManifest);
const judsonChapters = await loadJson(paths.judsonChapters);
const openLogicAdmission = await loadJson(paths.openLogicAdmission);
const openLogicManifest = await loadJson(paths.openLogicManifest);
const openLogicRoute = await loadJson(paths.openLogicRoute);
const c130Admission = await loadJson(paths.c130Admission);
const c130Manifest = await loadJson(paths.c130Manifest);
const c130Route = await loadJson(paths.c130Route);
const c130AuthorityReplay = await loadJson(paths.c130AuthorityReplay);

assert.deepEqual(releaseAdapter.adapters.map((row) => row.role_id), ['A00', 'B10', 'D20', 'D60', 'D110']);
assert.deepEqual(liveAdapter.adapters.map((row) => row.role_id), ['A00', 'B10', 'C30', 'C40', 'D20', 'D60', 'D110']);
assert.equal(livePattern.families.length, 33);
assert.deepEqual(livePattern.families.map((row) => row.ordinal), Array.from({ length: 33 }, (_, index) => index + 1));
const allRoles = livePattern.families.flatMap((family) => family.roles);
assert.equal(allRoles.length, 40);
assert.equal(new Set(allRoles).size, 40);
assert.equal(releasedV2Snapshot.snapshot.snapshot_id, predecessorSnapshotId);
assert.equal(githubV06214Receipt.state, 'published_public_verified');
assert.equal(githubV06214Receipt.version, '0.62.14');
assert.equal(githubV06214Receipt.repository_public, true);
assert.equal(githubV06214Receipt.release.tag, 'v0.62.14');
assert.equal(githubV06214Receipt.release.draft, false);
assert.equal(githubV06214Receipt.release.prerelease, false);
assert.equal(githubV06214Receipt.anonymous_asset_readback.result, 'pass_112_of_112');
assert.equal(githubV06214Receipt.anonymous_asset_readback.entries.length, 112);
assert.equal(zenodoV06214Receipt.state, 'published_open_modular_backend_successor');
assert.equal(zenodoV06214Receipt.version, '0.62.14');
assert.equal(zenodoV06214Receipt.zenodo.version_doi, '10.5281/zenodo.22217240');
assert.equal(zenodoV06214Receipt.zenodo.access_right, 'open');
assert.equal(zenodoV06214Receipt.zenodo.anonymous_readback, 'pass_100_of_100');
assert.equal(zenodoV06214Receipt.github_authority.anonymous_readback, 'pass_112_of_112');
assert.equal(c130AuthorityReplay.state, 'pass_postpublication_authority_replay');
assert.equal(c130AuthorityReplay.input_authorities.declared, 14);
assert.equal(c130AuthorityReplay.input_authorities.locally_replayed, 14);
assert.equal(c130AuthorityReplay.scope.package_or_owner_bytes_mutated, false);

const familyIdByRole = new Map();
for (const family of livePattern.families) {
  const nativeFamilyId = `family-${String(family.ordinal).padStart(2, '0')}-${slug(family.family_name)}`;
  for (const roleId of family.roles) familyIdByRole.set(roleId, nativeFamilyId);
}

const snapshot = {
  snapshot_id: snapshotId,
  snapshot_kind: 'live_successor_overlay',
  as_of: zenodoV06214Receipt.recorded_at_utc,
  central_release_version: 'v0.62.14',
  central_release_record_doi: zenodoV06214Receipt.zenodo.version_doi,
  mutable_overlay: true,
  supersedes: {
    snapshot_id: predecessorSnapshotId,
    central_release_version: 'v0.62.14-prepublication',
    central_release_record_doi: zenodoV06214Receipt.zenodo.version_doi,
    source: fileRow(paths.releasedV2Snapshot, await load(paths.releasedV2Snapshot)),
  },
  public_replay_state: 'postpublication_release_assets_readback_complete',
};

const v06214AssetByName = new Map(githubV06214Receipt.anonymous_asset_readback.entries.map((row) => [row.name, row]));
const publishedV06214Asset = (archive) => {
  const asset = v06214AssetByName.get(basename(archive.path));
  assert.ok(asset, `${archive.path}: missing from v0.62.14 anonymous GitHub readback`);
  assert.equal(asset.anonymous_http_status, 200);
  assert.equal(asset.anonymous_byte_identity, true);
  assert.deepEqual({ bytes: asset.bytes, sha256: asset.sha256 }, { bytes: archive.bytes, sha256: archive.sha256 });
  return {
    admission_state: 'published',
    release_url: githubV06214Receipt.release.url,
    public_asset_url: asset.url,
    public_replay_status: 'published_public_asset_readback_verified',
  };
};

const numericFields = [
  'native_records_preserved', 'reversible_native_mappings', 'additional_native_index_rows',
  'assessment_records_preserved', 'exact_html_anchor_routes', 'explicit_solution_gaps',
  'navigation_units_promoted', 'component_rights_exceptions',
];
const packageFromPublishedRow = async (row) => {
  const archivePath = await exists(row.archive.path)
    ? row.archive.path
    : `releases/v0.62.13/${basename(row.archive.path)}`;
  const archiveBytes = await load(archivePath);
  const manifestBytes = await load(row.manifest.path);
  assert.deepEqual(identity(archiveBytes), { bytes: row.archive.bytes, sha256: row.archive.sha256 }, `${row.role_id}: archive drift`);
  assert.deepEqual(identity(manifestBytes), { bytes: row.manifest.bytes, sha256: row.manifest.sha256 }, `${row.role_id}: manifest drift`);
  const manifest = JSON.parse(manifestBytes);
  const result = {
    package_id: manifest.package_id ?? `urn:sha256:${row.archive.sha256}`,
    native_family_id: familyIdByRole.get(row.role_id),
    proof_kind: row.proof_kind,
    contract_version: row.contract_version,
    adapter_version: row.adapter_version,
    admission_state: 'published',
    release_url: row.release_url,
    public_asset_url: row.public_asset_url,
    public_replay_status: 'published_public_asset_readback_verified',
    adopted_capabilities: row.adopted_capabilities,
    known_limitations: row.known_limitations,
    archive: { path: archivePath, bytes: row.archive.bytes, sha256: row.archive.sha256 },
    manifest: row.manifest,
    canonical_records: row.canonical_records,
    jsonl_csv_table_pairs: row.jsonl_csv_table_pairs,
    owner_native_authoritative: true,
    zero_copy: true,
    scope_note: row.scope_note ?? `Paket ${row.role_id} mempertahankan otoritas native; cakupan rinci dan batas klaim berada pada manifest serta daftar kemampuan.`,
  };
  for (const field of numericFields) if (Object.hasOwn(row, field)) result[field] = row[field];
  if (manifest.dataset_id) result.dataset_id = manifest.dataset_id;
  if (manifest.extension_id) result.extension_id = manifest.extension_id;
  return result;
};

const packages = [];
const adapters = [];
const packageByRole = new Map();
for (const row of releaseAdapter.adapters) {
  const packageRow = await packageFromPublishedRow(row);
  packages.push(packageRow);
  packageByRole.set(row.role_id, packageRow);
  adapters.push({
    role_id: row.role_id,
    course: row.course,
    native_family_id: packageRow.native_family_id,
    adapter_package_id: packageRow.package_id,
    learner_url: row.learner_url,
    ...(row.role_id === 'A00' ? { central_learner_projection: { path: 'docs/id-ID/courses/A00/latihan/index.html', status: 'published', locale: 'id-ID' } } : {}),
    learner_runtime_relationship: row.learner_runtime_relationship,
    scope_note: row.scope_note ?? `Ikatan ${row.role_id} membuka permukaan belajar course-native tanpa menganggap pembaca menggunakan tabel adapter di luar hubungan runtime yang dinyatakan.`,
  });
}

assert.deepEqual(judsonAdmission.archive, (liveAdapter.adapters.find((row) => row.role_id === 'C30')).archive);
assert.equal(judsonManifest.package_id, 'urn:uuid:f2d0324c-322c-5f7b-a9e6-8beccf50656c');
assert.equal(judsonManifest.dataset_id, 'urn:uuid:d96f3a23-1002-5be5-bff2-bb035a386a3c');
assert.equal(judsonManifest.extension_id, 'urn:uuid:54463e63-19cd-5859-b252-93e0a4d516be');
const judsonBase = liveAdapter.adapters.find((row) => row.role_id === 'C30');
const judsonPackage = {
  package_id: judsonManifest.package_id,
  native_family_id: familyIdByRole.get('C30'),
  proof_kind: 'reversible_lane_adapter',
  contract_version: '2.3.1',
  adapter_version: judsonBase.adapter_version,
  ...publishedV06214Asset(judsonAdmission.archive),
  adopted_capabilities: judsonBase.adopted_capabilities,
  known_limitations: judsonBase.known_limitations,
  archive: judsonAdmission.archive,
  manifest: fileRow(paths.judsonManifest, await load(paths.judsonManifest)),
  canonical_records: 17745,
  native_records_preserved: 3323,
  reversible_native_mappings: 3323,
  unit_records: 3323,
  relation_records: 6505,
  source_translation_pairs: 4466,
  jsonl_csv_table_pairs: 19,
  owner_native_authoritative: true,
  zero_copy: true,
  dataset_id: judsonManifest.dataset_id,
  extension_id: judsonManifest.extension_id,
  scope_note: 'Satu graf Judson berisi 17.745 rekaman dan melayani C30 serta C40 tanpa menggandakan unit atau prosa. Total paket tidak boleh dijumlahkan per peran.',
};
packages.push(judsonPackage);
const judsonCourses = new Map(judsonChapters.courses.map((course) => [course.course_id, course]));
for (const roleId of ['C30', 'C40']) {
  const row = liveAdapter.adapters.find((candidate) => candidate.role_id === roleId);
  const course = judsonCourses.get(roleId);
  assert.ok(row && course);
  packageByRole.set(roleId, judsonPackage);
  adapters.push({
    role_id: roleId,
    course: row.course,
    native_family_id: judsonPackage.native_family_id,
    adapter_package_id: judsonPackage.package_id,
    learner_url: course.chapters[0].public_url,
    central_learner_projection: { path: `docs/backend/judson/${roleId}.html`, status: 'published', locale: 'id-ID' },
    learner_runtime_relationship: 'directly_consumes_adapter_outputs',
    course_specific_route_count: course.chapters.length,
    scope_note: `${roleId} memilih ${course.chapters.length} rute bab dari satu graf Judson bersama; hitungan paket tidak diulang.`,
  });
}

assert.equal(openLogicManifest.package_id, openLogicAdmission.package_id);
assert.equal(openLogicManifest.dataset_id, openLogicAdmission.dataset_id);
assert.equal(openLogicManifest.extension_id, openLogicAdmission.extension_id);
assert.deepEqual(openLogicAdmission.archive, openLogicRoute.adapter.archive);
assert.equal(openLogicRoute.primary_learner_action.pages, 1116);
assert.equal(openLogicAdmission.semantic_counts.units, 722);
assert.equal(openLogicAdmission.semantic_counts.native_html_claimed, false);
assert.equal(openLogicAdmission.semantic_counts.unit_or_page_anchors_claimed, false);
const historicalOpenLogicPublicationLimit =
  'Central adapter publication remains pending until GitHub and Zenodo readback of the successor release.';
assert.ok(openLogicAdmission.limits.includes(historicalOpenLogicPublicationLimit));
const currentOpenLogicLimitations = openLogicAdmission.limits.filter(
  (item) => item !== historicalOpenLogicPublicationLimit,
);
assert.equal(currentOpenLogicLimitations.length, openLogicAdmission.limits.length - 1);
const openLogicPackage = {
  package_id: openLogicManifest.package_id,
  native_family_id: familyIdByRole.get('C80'),
  proof_kind: 'reversible_lane_adapter',
  contract_version: '2.3.1',
  adapter_version: openLogicAdmission.extension_version,
  ...publishedV06214Asset(openLogicAdmission.archive),
  adopted_capabilities: [
    'stable_owner_module_identity', 'reversible_prior_v1_mappings', 'ordered_import_graph',
    'translation_state_evidence', 'component_rights', 'lossless_jsonl_csv_projection',
    'learner_pdf_authority',
  ],
  // Preserve only still-current limitations. The sealed admission's former
  // publication-pending note was resolved and publicly read back in v0.62.14.
  known_limitations: currentOpenLogicLimitations,
  archive: openLogicAdmission.archive,
  manifest: fileRow(paths.openLogicManifest, await load(paths.openLogicManifest)),
  canonical_records: 5807,
  native_records_preserved: 722,
  reversible_native_mappings: 722,
  ordered_import_relations: 725,
  rights_assignments: 728,
  reader_reachable_units: 642,
  retained_non_reader_units: 80,
  reader_pages: 1116,
  unit_records: 722,
  relation_records: 725,
  source_translation_pairs: 722,
  namespace_mappings: 1445,
  public_artifacts: 4,
  native_html_claimed: false,
  unit_or_page_anchors_claimed: false,
  jsonl_csv_table_pairs: 19,
  owner_native_authoritative: true,
  zero_copy: true,
  owner_authority: {
    public_repository: openLogicAdmission.owner_authority.public_repository,
    public_release: openLogicAdmission.owner_authority.public_release,
    release_commit: openLogicAdmission.owner_authority.release_commit,
    release_tree: openLogicAdmission.owner_authority.release_tree,
    version_doi: openLogicAdmission.owner_authority.version_doi,
    concept_doi: openLogicAdmission.owner_authority.concept_doi,
  },
  dataset_id: openLogicManifest.dataset_id,
  extension_id: openLogicManifest.extension_id,
  scope_note: 'Adapter mempertahankan 722 identitas OLP dan menautkan PDF Indonesia 1.116 halaman sebagai permukaan belajar utama; tidak ada HTML atau jangkar turunan yang ditebak.',
};
packages.push(openLogicPackage);
packageByRole.set('C80', openLogicPackage);
adapters.push({
  role_id: 'C80',
  course: openLogicRoute.title,
  native_family_id: openLogicPackage.native_family_id,
  adapter_package_id: openLogicPackage.package_id,
  learner_url: openLogicRoute.primary_learner_action.url,
  central_learner_projection: { path: 'docs/backend/openlogic/C80.html', status: 'published', locale: 'id-ID' },
  learner_runtime_relationship: 'course_link_only_no_adapter_consumption_claim',
  course_specific_route_count: 0,
  scope_note: 'Buka PDF Indonesia yang telah dibaca balik; data adapter tetap sekunder dan paket pusat telah dibaca balik pada rilis v0.62.14.',
});

assert.equal(c130Manifest.package_id, c130Admission.package_id);
assert.equal(c130Manifest.dataset_id, c130Admission.dataset_id);
assert.equal(c130Manifest.extension_id, c130Admission.extension_id);
assert.deepEqual(c130Admission.archive, c130Route.adapter.archive);
assert.equal(c130Route.primary_learner_action.kind, 'pages_learner_landing');
assert.equal(c130Route.primary_reader.format, 'linked_pdf');
assert.equal(c130Route.primary_reader.pages, 666);
assert.equal(c130Admission.semantic_counts.canonical_records, 51704);
assert.equal(c130Admission.semantic_counts.units, 1993);
assert.equal(c130Admission.semantic_counts.relations, 9545);
assert.equal(c130Admission.semantic_counts.rights_assignments, 7634);
assert.equal(c130Admission.semantic_counts.identity_crosswalks, 17273);
assert.equal(c130Admission.semantic_counts.native_html_claimed, false);
assert.equal(c130Admission.semantic_counts.unit_or_page_anchors_claimed, false);
assert.equal(c130Admission.semantic_counts.pdf_ua_claimed, false);
assert.equal(c130Admission.state, 'locally_admitted_central_release_pending');
assert.equal(c130Admission.admitted_inputs, 65);
const c130Package = {
  package_id: c130Manifest.package_id,
  native_family_id: familyIdByRole.get('C130'),
  proof_kind: 'reversible_lane_adapter',
  contract_version: '2.3.1',
  adapter_version: c130Admission.extension_version,
  ...publishedV06214Asset(c130Admission.archive),
  adopted_capabilities: [
    'stable_owner_native_identity', 'typed_curriculum_graph', 'reversible_identity_crosswalks',
    'component_rights_assignments', 'lossless_jsonl_csv_projection', 'learner_pdf_authority',
    'executable_lab_routes',
  ],
  known_limitations: c130Admission.limits,
  archive: c130Admission.archive,
  manifest: fileRow(paths.c130Manifest, await load(paths.c130Manifest)),
  canonical_records: 51704,
  native_records_preserved: 17987,
  reversible_native_mappings: 17273,
  rights_assignments: 7634,
  reader_pages: 666,
  unit_records: 1993,
  relation_records: 9545,
  namespace_mappings: 17273,
  public_artifacts: 83,
  native_html_claimed: false,
  unit_or_page_anchors_claimed: false,
  jsonl_csv_table_pairs: 19,
  owner_native_authoritative: true,
  zero_copy: true,
  owner_authority: {
    public_repository: c130Admission.owner_authority.repository,
    public_release: c130Admission.owner_authority.release,
    release_commit: c130Admission.owner_authority.release_commit,
    release_tree: c130Admission.owner_authority.release_tree,
    version_doi: c130Admission.owner_authority.version_doi,
    concept_doi: c130Admission.owner_authority.concept_doi,
  },
  dataset_id: c130Manifest.dataset_id,
  extension_id: c130Manifest.extension_id,
  scope_note: 'Adapter C130 mempertahankan graf course-native dan 51.704 baris proyeksi tanpa memusatkan prosa; halaman landing dan PDF Indonesia 666 halaman tetap menjadi permukaan belajar.',
};
packages.push(c130Package);
packageByRole.set('C130', c130Package);
adapters.push({
  role_id: 'C130',
  course: c130Route.title,
  native_family_id: c130Package.native_family_id,
  adapter_package_id: c130Package.package_id,
  learner_url: c130Route.primary_learner_action.url,
  central_learner_projection: { path: 'docs/backend/c130/C130.html', status: 'published', locale: 'id-ID' },
  learner_runtime_relationship: 'course_link_only_no_adapter_consumption_claim',
  course_specific_route_count: 7,
  scope_note: 'Buka landing course-native lalu PDF Indonesia; tujuh rute publik dipertahankan dan data mesin tetap sekunder.',
});

const roleOrder = ['A00', 'B10', 'C30', 'C40', 'C80', 'C130', 'D20', 'D60', 'D110'];
adapters.sort((a, b) => roleOrder.indexOf(a.role_id) - roleOrder.indexOf(b.role_id));
packages.sort((a, b) => {
  const firstA = Math.min(...adapters.filter((row) => row.adapter_package_id === a.package_id).map((row) => roleOrder.indexOf(row.role_id)));
  const firstB = Math.min(...adapters.filter((row) => row.adapter_package_id === b.package_id).map((row) => roleOrder.indexOf(row.role_id)));
  return firstA - firstB;
});

assert.deepEqual(adapters.map((row) => row.role_id), roleOrder);
assert.equal(new Set(adapters.map((row) => row.role_id)).size, 9);
assert.equal(new Set(packages.map((row) => row.package_id)).size, 8);
assert.equal(new Set(adapters.map((row) => row.native_family_id)).size, 8);
assert.deepEqual(adapters.filter((row) => row.adapter_package_id === judsonPackage.package_id).map((row) => row.role_id), ['C30', 'C40']);
for (const packageRow of packages) {
  assert.ok(adapters.some((row) => row.adapter_package_id === packageRow.package_id), `${packageRow.package_id}: unreferenced package`);
  if (packageRow.admission_state === 'published') {
    assert.equal(packageRow.public_replay_status, 'published_public_asset_readback_verified');
    assert.equal(typeof packageRow.release_url, 'string');
    assert.equal(typeof packageRow.public_asset_url, 'string');
    assert.ok(!Object.hasOwn(packageRow, 'planned_release'));
  } else {
    assert.equal(packageRow.public_replay_status, 'pending_release_local_seal_verified');
    assert.equal(packageRow.release_url, null);
    assert.equal(packageRow.public_asset_url, null);
    assert.equal(packageRow.planned_release.state, 'planned_not_public');
  }
}

const publishedPackageIds = new Set(packages.filter((row) => row.admission_state === 'published').map((row) => row.package_id));
const summary = {
  curriculum_roles: 40,
  role_bindings: adapters.length,
  published_role_bindings: adapters.filter((row) => publishedPackageIds.has(row.adapter_package_id)).length,
  pending_role_bindings: adapters.filter((row) => !publishedPackageIds.has(row.adapter_package_id)).length,
  distinct_adapter_packages: packages.length,
  published_adapter_packages: packages.filter((row) => row.admission_state === 'published').length,
  pending_adapter_packages: packages.filter((row) => row.admission_state !== 'published').length,
  represented_native_families: new Set(packages.map((row) => row.native_family_id)).size,
  unbound_roles: 40 - adapters.length,
  families_without_local_adapter: 33 - new Set(packages.map((row) => row.native_family_id)).size,
  families_without_public_replay_complete_adapter: 33 - new Set(packages.filter((row) => row.admission_state === 'published').map((row) => row.native_family_id)).size,
  package_deduplicated_canonical_records: packages.reduce((sum, row) => sum + row.canonical_records, 0),
};
assert.deepEqual(summary, {
  curriculum_roles: 40, role_bindings: 9, published_role_bindings: 9, pending_role_bindings: 0,
  distinct_adapter_packages: 8, published_adapter_packages: 8, pending_adapter_packages: 0,
  represented_native_families: 8, unbound_roles: 31, families_without_local_adapter: 25,
  families_without_public_replay_complete_adapter: 25, package_deduplicated_canonical_records: 285829,
});

const adapterIndex = {
  $schema: 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v2/v23-adapter-index-v2.schema.json',
  schema_id: 'interlanguage/program-matematika-indonesia-v23-adapter-index/v2',
  schema_version: '2.0.0',
  snapshot,
  policy: releaseAdapter.policy,
  summary,
  packages,
  adapters,
};
const adapterBytes = stable(adapterIndex);
const adapterOutputPath = `${authorityRoot}/v23-adapter-index-v2.json`;
const adapterOutputIdentity = fileRow(adapterOutputPath, adapterBytes);

const methodologyStages = [
  { sequence: 1, stage_id: 'inventory_native_designs', description_id: 'Inventarisasi setiap rancangan backend native tanpa memaksakan bentuk pusat.' },
  { sequence: 2, stage_id: 'compare_common_axes', description_id: 'Bandingkan identitas, relasi, provenance, replay, akses belajar, dan biaya pemeliharaan pada sumbu yang sama.' },
  { sequence: 3, stage_id: 'adopt_evidenced_features', description_id: 'Adopsi hanya fitur yang dibuktikan oleh artefak dan nyatakan batas yang belum ditutup.' },
  { sequence: 4, stage_id: 'publish_validate_reaudit', description_id: 'Bangun deterministik, validasi, publikasikan, baca balik anonim, lalu audit ulang snapshot berikutnya.' },
];
const sourceEvidence = [
  { source_id: 'immutable_pattern_v1', purpose: 'Temuan 33 keluarga pada rilis beku v0.62.13.', ...fileRow(paths.releasePattern, await load(paths.releasePattern)) },
  { source_id: 'live_pattern_overlay_input', purpose: 'Koreksi overlay yang dipertahankan sebagai input penerus, bukan v1 publik.', ...fileRow(paths.livePattern, await load(paths.livePattern)) },
  { source_id: 'methodology_v1', purpose: 'Metode perbandingan dan konvergensi yang sudah dipreservasi publik.', ...fileRow(paths.releaseMethod, await load(paths.releaseMethod)) },
  { source_id: 'v06214_github_publication', purpose: 'Bukti baca-balik anonim 112 aset GitHub pada rilis v0.62.14.', ...fileRow(paths.githubV06214Receipt, await load(paths.githubV06214Receipt)) },
  { source_id: 'v06214_zenodo_publication', purpose: 'Bukti rilis terbuka dan baca-balik anonim 100 berkas Zenodo v0.62.14.', ...fileRow(paths.zenodoV06214Receipt, await load(paths.zenodoV06214Receipt)) },
];
const patternIndex = {
  $schema: 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v2/modular-backend-pattern-index-v2.schema.json',
  schema_id: 'interlanguage/program-matematika-indonesia-modular-backend-pattern-index/v2',
  schema_version: '2.0.0',
  recorded_at: recordedAt,
  locale: 'id-ID',
  snapshot,
  methodology: {
    design_premise: livePattern.methodology.design_premise,
    comparison_policy: livePattern.methodology.comparison_policy,
    denominator: {
      program_roles: 40,
      native_implementation_families: 33,
      manager_federation_is_separate_synthesis_candidate: true,
    },
    stages: methodologyStages,
    evidence_basis: ['owner-native manifests', 'owner-native validators', 'owner-native learner surfaces', 'immutable central releases', 'dated public-byte readback'],
  },
  audit_axes: livePattern.audit_axes,
  canonical_recommendation: livePattern.canonical_recommendation,
  adapter_snapshot: { adapter_index: adapterOutputIdentity, ...summary },
  source_evidence: sourceEvidence,
  families: livePattern.families.map((family) => {
    const nativeFamilyId = familyIdByRole.get(family.roles[0]);
    return {
      ...family,
      native_family_id: nativeFamilyId,
      adapter_bindings: adapters.filter((row) => family.roles.includes(row.role_id)).map((row) => {
        const packageRow = packages.find((candidate) => candidate.package_id === row.adapter_package_id);
        return {
          role_id: row.role_id,
          adapter_package_id: row.adapter_package_id,
          admission_state: packageRow.admission_state,
          public_replay_status: packageRow.public_replay_status,
        };
      }),
    };
  }),
};
delete patternIndex.adapter_snapshot.curriculum_roles;
delete patternIndex.adapter_snapshot.published_adapter_packages;
delete patternIndex.adapter_snapshot.pending_adapter_packages;
delete patternIndex.adapter_snapshot.package_deduplicated_canonical_records;
const patternBytes = stable(patternIndex);

const evidenceFromInput = (evidenceId, kind, path, claimScope) => ({
  evidence_id: evidenceId,
  kind,
  ...fileRow(path, sourceBytes.get(path)),
  claim_scope: claimScope,
});
const featureEvidence = [
  evidenceFromInput('methodology_v1', 'methodology_record', paths.releaseMethod, 'Metode empat tahap dan temuan keluarga backend.'),
  evidenceFromInput('immutable_adapter_v1', 'immutable_release', paths.releaseAdapter, 'Lima paket adapter yang sudah dibaca balik publik.'),
  evidenceFromInput('live_adapter_overlay_input', 'live_overlay_input', paths.liveAdapter, 'Dua peran Judson yang diterima lokal sebelum pemisahan snapshot.'),
  evidenceFromInput('judson_admission', 'adapter_admission', paths.judsonAdmission, 'Satu graf Judson untuk C30 dan C40.'),
  evidenceFromInput('judson_manifest', 'adapter_manifest', paths.judsonManifest, 'Identitas dan tabel paket Judson.'),
  evidenceFromInput('openlogic_admission', 'adapter_admission', paths.openLogicAdmission, 'Penerimaan lokal C80 dengan batas klaim.'),
  evidenceFromInput('openlogic_manifest', 'adapter_manifest', paths.openLogicManifest, 'Identitas dan tabel paket Open Logic.'),
  evidenceFromInput('c130_admission', 'adapter_admission', paths.c130Admission, 'Penerimaan lokal C130 dengan batas klaim.'),
  evidenceFromInput('c130_manifest', 'adapter_manifest', paths.c130Manifest, 'Identitas, tabel, dan proyeksi paket C130.'),
  evidenceFromInput('c130_authority_replay', 'adapter_validation', paths.c130AuthorityReplay, 'Replay lokal 14/14 otoritas C130 setelah publikasi tanpa mutasi paket atau sumber native.'),
  evidenceFromInput('v06214_github_publication', 'immutable_release', paths.githubV06214Receipt, 'Baca-balik anonim 112/112 aset GitHub v0.62.14.'),
  evidenceFromInput('v06214_zenodo_publication', 'immutable_release', paths.zenodoV06214Receipt, 'Rilis terbuka Zenodo v0.62.14 dan baca-balik anonim 100/100 berkas.'),
  evidenceFromInput('terminology_concordance', 'terminology_evidence', paths.terminology, 'Bukti istilah Indonesia teratribusi; bukan verifikasi global.'),
  evidenceFromInput('terminology_policy', 'design_policy', paths.terminologyPolicy, 'Kebijakan konsep dan register Indonesia; keputusan peluang/probabilitas tetap menunggu bukti.'),
  evidenceFromInput('design_policy', 'design_policy', paths.designPolicy, 'Kebijakan kapsul tipis, netral-format, dan zero-copy.'),
  evidenceFromInput('capsule_manifest', 'generated_snapshot', paths.capsuleManifest, 'Manifest pembangunan kapsul 40 peran saat ini.'),
  evidenceFromInput('learner_delivery', 'generated_snapshot', paths.learnerDelivery, 'Rute dan format penyampaian pelajar yang tervalidasi.'),
  { evidence_id: 'adapter_snapshot_v2', kind: 'generated_snapshot', ...adapterOutputIdentity, claim_scope: 'Snapshot penerus sembilan peran melalui delapan paket.' },
];
const feature = (featureId, descriptionId, sourcePatternIds, evidenceIds, implementationStatus, limitations = []) => ({
  feature_id: featureId, description_id: descriptionId, source_pattern_ids: sourcePatternIds,
  evidence_ids: evidenceIds, implementation_status: implementationStatus, limitations,
});
const featureLedger = {
  $schema: 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v2/feature-adoption-provenance-v1.schema.json',
  schema_id: 'interlanguage/program-matematika-indonesia-feature-adoption-provenance/v1',
  schema_version: '1.0.0',
  recorded_at: recordedAt,
  snapshot_id: snapshotId,
  policy: { course_native_authoritative: true, zero_copy: true, unsupported_claims_forbidden: true, human_evidence_is_not_a_release_gate: true },
  evidence: featureEvidence,
  layers: [
    { sequence: 1, layer_id: 'curriculum', label_id: 'Kurikulum', status: 'adopted_and_implemented', features: [
      feature('typed_curriculum_graph', 'Identitas 40 peran, prasyarat bertipe, hasil belajar, dan rute pusat.', ['manager-federation', 'family-12-judson'], ['methodology_v1', 'capsule_manifest'], 'implemented'),
    ] },
    { sequence: 2, layer_id: 'translation', label_id: 'Terjemahan dan provenance', status: 'adopted_partial', features: [
      feature('source_attributed_translation_ledger', 'Status terjemahan, hak, koreksi, kebijakan konsep/register, dan bukti istilah tetap teratribusi ke sumber.', ['family-15-open-logic', 'family-01-prealgebra'], ['openlogic_manifest', 'terminology_concordance', 'terminology_policy'], 'partially_implemented', ['Segmentasi universal dan QA istilah seluruh 40 peran belum tersedia.', 'Keluarga peluang/probabilitas masih memerlukan bukti pemakaian Indonesia pada tingkat konsep.']),
    ] },
    { sequence: 3, layer_id: 'production', label_id: 'Produksi dan rilis', status: 'adopted_and_implemented', features: [
      feature('deterministic_manifested_builds', 'Paket deterministik, manifest, validasi, dan bukti baca-balik.', ['family-12-judson', 'family-15-open-logic', 'family-20-operations-research'], ['judson_admission', 'openlogic_admission', 'c130_admission', 'capsule_manifest'], 'implemented'),
    ] },
    { sequence: 4, layer_id: 'learner', label_id: 'Pelajar dan aksesibilitas', status: 'adopted_partial', features: [
      feature('learner_first_routes', 'Permukaan belajar didahulukan; data mesin berada di belakang rincian.', ['family-01-prealgebra', 'family-12-judson', 'family-15-open-logic', 'family-20-operations-research'], ['learner_delivery', 'openlogic_admission', 'judson_admission', 'c130_admission'], 'partially_implemented', ['Rute tingkat unit dan aksesibilitas penuh belum merata di semua keluarga.']),
    ] },
    { sequence: 5, layer_id: 'educator', label_id: 'Pengajar dan bukti', status: 'adopted_partial', features: [
      feature('shared_educator_evidence', 'Materi pengajar memakai identitas kursus/unit yang sama dengan tampilan pelajar.', ['manager-federation', 'family-05-discrete-mathematics'], ['methodology_v1', 'capsule_manifest'], 'partially_implemented', ['Paket rencana pelajaran, rubrik, dan intervensi belum lengkap untuk semua peran.']),
    ] },
    { sequence: 6, layer_id: 'federation', label_id: 'Federasi zero-copy', status: 'adopted_and_implemented', features: [
      feature('zero_copy_component_federation', 'Buku utama, donor, suplemen, edisi, dan tampilan kursus ditautkan tanpa menyalin prosa.', ['manager-federation', 'family-12-judson', 'family-20-operations-research'], ['design_policy', 'judson_manifest', 'c130_manifest', 'capsule_manifest'], 'implemented'),
    ] },
    { sequence: 7, layer_id: 'interoperability', label_id: 'Interoperabilitas dan adapter', status: 'adopted_partial', features: [
      feature('reversible_native_identity_adapters', 'Adapter mempertahankan identitas native dan menyediakan proyeksi JSONL/CSV reversibel.', ['family-12-judson', 'family-15-open-logic', 'family-20-operations-research', 'family-32-mathematics-in-lean'], ['immutable_adapter_v1', 'judson_manifest', 'openlogic_manifest', 'c130_manifest', 'c130_authority_replay', 'v06214_github_publication', 'v06214_zenodo_publication', 'adapter_snapshot_v2'], 'partially_implemented', ['Delapan dari 33 keluarga memiliki paket yang telah dibaca balik publik; 25 keluarga belum memiliki adapter umum.']),
    ] },
  ],
};
const evidenceIds = new Set(featureLedger.evidence.map((row) => row.evidence_id));
assert.equal(evidenceIds.size, featureLedger.evidence.length);
assert.deepEqual(featureLedger.layers.map((row) => row.layer_id), ['curriculum', 'translation', 'production', 'learner', 'educator', 'federation', 'interoperability']);
for (const layer of featureLedger.layers) for (const row of layer.features) for (const evidenceId of row.evidence_ids) assert.ok(evidenceIds.has(evidenceId), `Unknown evidence reference: ${evidenceId}`);
const featureBytes = stable(featureLedger);

const comparisonEvidence = [
  ['immutable_adapter_v1', 'immutable_release', paths.releaseAdapter, 'Lima bukti adapter pada rilis v0.62.13.', 'immutable_release_byte'],
  ['immutable_pattern_v1', 'immutable_release', paths.releasePattern, 'Temuan 33 keluarga pada rilis v0.62.13.', 'immutable_release_byte'],
  ['methodology_v1', 'methodology_record', paths.releaseMethod, 'Metode perbandingan yang dipreservasi publik.', 'immutable_release_byte'],
  ['live_adapter_overlay_input', 'live_overlay_input', paths.liveAdapter, 'Overlay pra-rilis yang dipisahkan dari v1.', 'preserved_overlay_input'],
  ['live_pattern_overlay_input', 'live_overlay_input', paths.livePattern, 'Koreksi temuan pra-rilis yang dipisahkan dari v1.', 'preserved_overlay_input'],
  ['judson_admission', 'adapter_admission', paths.judsonAdmission, 'Penerimaan lokal paket bersama C30/C40.', 'sealed_admission_byte'],
  ['judson_manifest', 'adapter_manifest', paths.judsonManifest, 'Manifest paket bersama C30/C40.', 'sealed_admission_byte'],
  ['openlogic_admission', 'adapter_admission', paths.openLogicAdmission, 'Penerimaan lokal paket C80.', 'sealed_admission_byte'],
  ['openlogic_manifest', 'adapter_manifest', paths.openLogicManifest, 'Manifest paket C80.', 'sealed_admission_byte'],
  ['c130_admission', 'adapter_admission', paths.c130Admission, 'Penerimaan lokal paket C130.', 'sealed_admission_byte'],
  ['c130_manifest', 'adapter_manifest', paths.c130Manifest, 'Manifest paket C130.', 'sealed_admission_byte'],
  ['c130_authority_replay', 'adapter_validation', paths.c130AuthorityReplay, 'Replay 14/14 otoritas C130 setelah publikasi.', 'current_authority_byte'],
  ['v06214_github_publication', 'immutable_release', paths.githubV06214Receipt, 'Baca-balik anonim 112/112 aset GitHub v0.62.14.', 'immutable_release_byte'],
  ['v06214_zenodo_publication', 'immutable_release', paths.zenodoV06214Receipt, 'Rilis Zenodo terbuka dan baca-balik anonim 100/100 berkas.', 'immutable_release_byte'],
  ['terminology_concordance', 'terminology_evidence', paths.terminology, 'Bukti istilah sumber-native untuk QA terarah.', 'current_authority_byte'],
  ['terminology_policy', 'design_policy', paths.terminologyPolicy, 'Kebijakan normatif istilah dan register Indonesia berbasis konsep.', 'current_authority_byte'],
  ['design_policy', 'design_policy', paths.designPolicy, 'Kebijakan normatif kapsul tipis dan zero-copy.', 'current_authority_byte'],
].map(([evidence_id, kind, path, claim_scope, immutability]) => ({ evidence_id, kind, ...fileRow(path, sourceBytes.get(path)), claim_scope, immutability }));
const comparisonManifest = {
  $schema: 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v2/comparison-evidence-manifest-v1.schema.json',
  schema_id: 'interlanguage/program-matematika-indonesia-comparison-evidence-manifest/v1',
  schema_version: '1.0.0',
  recorded_at: recordedAt,
  snapshot_id: snapshotId,
  methodology: { native_designs_compared_before_convergence: true, stages: methodologyStages },
  decision_rules: [
    'Pertahankan backend dan sumber course-native sebagai otoritas.',
    'Adopsi fitur hanya bila artefak primer membuktikan perilakunya.',
    'Jangan hitung satu paket bersama lebih dari sekali.',
    'Pisahkan status buku publik dari status adapter pusat.',
    'Nyatakan kemampuan yang hilang sebagai belum diproduksi, tidak berlaku, atau belum diverifikasi.',
  ],
  evidence: comparisonEvidence,
  outputs: [
    { path: adapterOutputPath, schema_id: adapterIndex.schema_id, purpose: 'Paket dan ikatan peran adapter pada overlay penerus.' },
    { path: `${authorityRoot}/modular-backend-pattern-index-v2.json`, schema_id: patternIndex.schema_id, purpose: 'Temuan 33 keluarga dengan status adapter per snapshot.' },
    { path: `${authorityRoot}/feature-adoption-provenance-v1.json`, schema_id: featureLedger.schema_id, purpose: 'Asal-usul keputusan pada tujuh lapisan kapsul.' },
  ],
  sanitization: { credentials_excluded: true, absolute_local_paths_excluded: true, coordination_transcripts_excluded: true, public_safe_repository_relative_paths_only: true },
};
const comparisonBytes = stable(comparisonManifest);

for (const [path, bytes] of sourceBytes) {
  assert.deepEqual(identity(await readFile(resolve(root, path))), identity(bytes), `${path}: input changed during generation`);
}

const outputs = new Map([
  [adapterOutputPath, adapterBytes],
  [`${authorityRoot}/modular-backend-pattern-index-v2.json`, patternBytes],
  [`${authorityRoot}/feature-adoption-provenance-v1.json`, featureBytes],
  [`${authorityRoot}/comparison-evidence-manifest-v1.json`, comparisonBytes],
  [`${publicDataRoot}/v23-adapter-index-v2.json`, adapterBytes],
  [`${publicDataRoot}/modular-backend-pattern-index-v2.json`, patternBytes],
  [`${publicDataRoot}/feature-adoption-provenance-v1.json`, featureBytes],
  [`${publicDataRoot}/comparison-evidence-manifest-v1.json`, comparisonBytes],
  [`${publicSchemaRoot}/v23-adapter-index-v2.schema.json`, await load(paths.adapterSchema)],
  [`${publicSchemaRoot}/modular-backend-pattern-index-v2.schema.json`, await load(paths.patternSchema)],
  [`${publicSchemaRoot}/feature-adoption-provenance-v1.schema.json`, await load(paths.featureSchema)],
  [`${publicSchemaRoot}/comparison-evidence-manifest-v1.schema.json`, await load(paths.comparisonSchema)],
]);
for (const bytes of outputs.values()) {
  const text = bytes.toString('utf8');
  assert.ok(!/[A-Za-z]:\\/.test(text), 'Absolute Windows path leaked into public snapshot');
  assert.ok(!/ghp_[A-Za-z0-9]+|access_token|api[_-]?key/i.test(text), 'Credential-like text leaked into public snapshot');
}
for (const [path, bytes] of outputs) {
  await mkdir(dirname(resolve(root, path)), { recursive: true });
  await writeFile(resolve(root, path), bytes);
}

for (const [canonical, projection] of [
  [adapterOutputPath, `${publicDataRoot}/v23-adapter-index-v2.json`],
  [`${authorityRoot}/modular-backend-pattern-index-v2.json`, `${publicDataRoot}/modular-backend-pattern-index-v2.json`],
  [`${authorityRoot}/feature-adoption-provenance-v1.json`, `${publicDataRoot}/feature-adoption-provenance-v1.json`],
  [`${authorityRoot}/comparison-evidence-manifest-v1.json`, `${publicDataRoot}/comparison-evidence-manifest-v1.json`],
]) assert.deepEqual(await readFile(resolve(root, canonical)), await readFile(resolve(root, projection)), `${projection}: projection drift`);

console.log(JSON.stringify({
  status: 'pass',
  snapshot_id: snapshotId,
  summary,
  outputs: [...outputs].map(([path, bytes]) => ({ path, ...identity(bytes) })),
}, null, 2));
