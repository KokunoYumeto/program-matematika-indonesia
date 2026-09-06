import { createHash } from 'node:crypto';
import { readFile, readdir, stat, writeFile, mkdir } from 'node:fs/promises';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const oldPath = join(root, 'backend/course-capsule-v1/authority/clp-family-v231/v23-adapter-index-v2.json');
const admissionPath = join(root, 'backend/course-capsule-v1/validation/20260907/GAP_ADMISSION.json');
const outputPath = join(root, 'backend/course-capsule-v1/authority/clp-family-v231/v23-adapter-index-v2.3.1.json');
const bytes = value => Buffer.isBuffer(value) ? value : Buffer.from(value);
const sha256 = value => createHash('sha256').update(bytes(value)).digest('hex');
const identity = async path => { const data = await readFile(path); return { path: relative(root, path).replaceAll('\\','/'), bytes: data.length, sha256: sha256(data) }; };
const treeIdentity = async dir => {
  const rows = [];
  const walk = async current => {
    for (const entry of (await readdir(current, { withFileTypes: true })).sort((a,b) => a.name.localeCompare(b.name))) {
      const path = join(current, entry.name);
      if (entry.isDirectory()) await walk(path);
      else { const data = await readFile(path); rows.push(`${relative(dir, path).replaceAll('\\','/')}\0${data.length}\0${sha256(data)}\n`); }
    }
  };
  await walk(dir);
  const material = Buffer.from(rows.join(''), 'utf8');
  return { files: rows.length, bytes: rows.reduce((n,row) => n + Number(row.split('\0')[1]), 0), sha256: sha256(material) };
};
const old = JSON.parse(await readFile(oldPath, 'utf8'));
const admission = JSON.parse(await readFile(admissionPath, 'utf8'));
const roles = ['A30', 'B95', 'C140'];
const additions = [];
for (const role_id of roles) {
  const entry = admission.roles[role_id];
  const packageDir = join(root, entry.package.path);
  const manifest = await identity(join(packageDir, 'manifest.json'));
  const tree = await treeIdentity(packageDir);
  const twin = await identity(join(root, entry.twin.path));
  const twinDocument = JSON.parse(await readFile(join(root, entry.twin.path), 'utf8'));
  const spec = await identity(join(root, entry.spec.path));
  const role = {
    role_id,
    package_id: entry.package.package_id,
    native_family_id: `family-gap-${role_id.toLowerCase()}`,
    contract_version: '2.3.1',
    adapter_version: '0.1.0',
    manifest,
    package_tree: {
      files: tree.files,
      bytes: tree.bytes,
      sha256: twinDocument.deterministic_ab.tree_sha256,
      local_replay_sha256: tree.sha256,
      authority: 'deterministic_twin_validation',
    },
    twin,
    specification: spec,
    package_payload_sha256: entry.common_adapter.payload_sha256,
    canonical_records: entry.common_adapter.record_count,
    bound_units: entry.common_adapter.bound_unit_count,
    owner_native_authoritative: true,
    zero_copy: true,
    admission_state: 'admitted_pending_release',
    public_replay_status: 'pending_release_local_seal_verified',
    learner_route: entry.learner_tools.href,
    learner_page: {
      path: entry.learner_tools.page.path,
      bytes: entry.learner_tools.page.bytes,
      sha256: entry.learner_tools.page.sha256,
    },
    course_truth: {
      state: entry.course_truth.state,
      version: entry.course_truth.version,
      corpus: entry.course_truth.corpus,
      repository: entry.course_truth.repository,
      zenodo: entry.course_truth.zenodo,
      reader: entry.course_truth.reader,
    },
  };
  additions.push(role);
}
const oldBytes = await readFile(oldPath);
const result = {
  schema: 'interlanguage/program-matematika-indonesia-v23-adapter-index-additive-overlay/1',
  schema_version: '1.0.0',
  status: 'local_seal_verified_pending_public_release',
  recorded_at: '2026-09-07T00:00:00Z',
  base_index: { ...await identity(oldPath), schema: old.schema_id, schema_version: old.schema_version, immutable: true },
  additions,
  policy: {
    additive_only: true,
    owner_native_authoritative: true,
    zero_copy: true,
    machine_data_secondary: true,
    public_access_required: true,
    publication_transition: 'After central v0.63.24 public readback, change only admission_state/public_replay_status in a superseding receipt; never mutate the frozen v2 index.',
  },
  summary: {
    base_published_adapter_packages: old.summary.published_adapter_packages,
    base_published_role_bindings: old.summary.published_role_bindings,
    additive_pending_adapter_packages: additions.length,
    additive_pending_role_bindings: additions.length,
    effective_adapter_packages: old.summary.published_adapter_packages + additions.length,
    effective_role_bindings: old.summary.published_role_bindings + additions.length,
    effective_represented_native_families: old.summary.represented_native_families + additions.length,
    effective_unbound_roles: old.summary.unbound_roles - additions.length,
  },
};
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, JSON.stringify(result, null, 2) + '\n', 'utf8');
console.log(JSON.stringify({ status: 'pass', output: await identity(outputPath), base: { bytes: oldBytes.length, sha256: sha256(oldBytes) }, additions: additions.map(({ role_id, package_id, package_tree }) => ({ role_id, package_id, package_tree })) }, null, 2));
