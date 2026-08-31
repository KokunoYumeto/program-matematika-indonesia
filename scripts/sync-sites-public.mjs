import assert from 'node:assert/strict';
import { cp, mkdir, readFile, readdir, rm } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, relative, resolve, sep } from 'node:path';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const source = resolve(project, 'docs');
const publicRoot = resolve(project, 'public');
const target = resolve(publicRoot, 'hub');
assert.ok(target.startsWith(`${publicRoot}${sep}`), 'Target sinkronisasi keluar dari public/.');

await rm(target, { recursive: true, force: true });
await mkdir(target, { recursive: true });
const approvedTopLevelFiles = new Set([
  'app.js',
  'courses.js',
  'index.html',
  'learner-delivery.js',
  'learner-tools.js',
  'learner-state.js',
  'live-course-publications.js',
  'og.png',
  'robots.txt',
  'styles.css',
  'peta-belajar-luring.html',
]);
const approvedDataFiles = new Set([
  'data/course-capsule-v1',
  'data/curriculum-authority-v1.json',
  'data/educational-access.json',
  'data/learner-read-model.json',
  'data/learner-delivery-v1.json',
  'data/learner-tools-v1.json',
  'data/educational-access.json',
  'schema/educational-access-federation-v1.schema.json',
  'data/unit-route-C100-v2.1.json',
  'data/unit-route-D20-v2.1.json',
  'data/unit-route-v2.1.json',
  'data/unit-routes-v2.1.json',
  'data/course-capsule-v1/course-capsules.jsonl',
  'data/course-capsule-v1/course-capsules.json',
  'data/course-capsule-v1/manifest.json',
  'data/course-capsule-v1/validation-receipt.json',
  'data/course-capsule-v1/README.md',
  'data/course-capsule-v1/backend-design-policy-v1.json',
  'data/course-capsule-v1/public-baseline-v0.62.12.json',
]);
const approvedReaderParents = new Set(['readers', 'readers/d40', 'readers/d40/unit14']);
const approvedReaderPrefix = 'readers/d40/unit14/';
await cp(source, target, {
  recursive: true,
  filter: (path) => {
    if (path === source) return true;
    const name = relative(source, path).split(sep).join('/');
    if (name === 'data' || name === 'schema' || name.startsWith('schema/')) return true;
    if (name === 'backend' || name.startsWith('backend/')) return true;
    // Preserve central learner route wrappers for the hosted mirror.  These
    // pages contain navigation and links only; owner-native prose remains on
    // the canonical course reader.
    if (name === 'id-ID' || name.startsWith('id-ID/')) return true;
    // Preserve only the admitted D40 Unit 14 portable reader closure.  Other
    // owner-native reader trees remain outside this generated Sites mirror.
    if (approvedReaderParents.has(name) || name.startsWith(approvedReaderPrefix)) return true;
    return approvedTopLevelFiles.has(name) || approvedDataFiles.has(name);
  },
});

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
for (const name of [
  'index.html',
  'styles.css',
  'app.js',
  'learner-delivery.js',
  'learner-tools.js',
  'learner-state.js',
  'live-course-publications.js',
  'courses.js',
  'data/curriculum-authority-v1.json',
  'data/learner-read-model.json',
  'data/learner-delivery-v1.json',
  'data/learner-tools-v1.json',
  'peta-belajar-luring.html',
  'schema/v1/curriculum-authority-v1.schema.json',
  'schema/v1/learner-read-model-v1.schema.json',
  'schema/v1/learner-delivery-v1.schema.json',
  'schema/v1/learner-tools-v1.schema.json',
  'schema/v1/a00-assessment-map-v1.schema.json',
  'schema/v1/learner-state-v1.schema.json',
  'schema/v2/federation-package-v2.schema.json',
  'schema/v2/federation-record-v2.schema.json',
  'og.png',
  'robots.txt',
  'id-ID/courses/D20/index.html',
  'id-ID/courses/D20/units/bab-01/index.html',
  'id-ID/courses/D20/units/bab-17/index.html',
  'id-ID/courses/B95/index.html',
  'id-ID/courses/A00/latihan/index.html',
  'id-ID/courses/A00/latihan/latihan.css',
  'id-ID/courses/A00/latihan/latihan.js',
  'id-ID/courses/A00/latihan/assessment-map-v1.json',
  'id-ID/courses/A00/latihan/anchor-audit-v1.json',
  'id-ID/courses/D30/index.html',
  'id-ID/courses/D40/index.html',
  'readers/d40/unit14/index.html',
  'id-ID/courses/C100/index.html',
  'id-ID/courses/C100/reader/index.html',
  'id-ID/courses/C100/reader/style.css',
  'id-ID/courses/C100/solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf',
  'id-ID/courses/C100/units/bab-01/index.html',
  'id-ID/courses/C100/units/bab-20/index.html',
  'data/unit-route-C100-v2.1.json',
  'data/unit-route-D20-v2.1.json',
  'data/unit-route-v2.1.json',
  'data/unit-routes-v2.1.json',
  'backend/index.html',
  'backend/backend.css',
  'backend/backend.js',
  'data/course-capsule-v1/course-capsules.jsonl',
  'data/course-capsule-v1/course-capsules.json',
  'data/course-capsule-v1/manifest.json',
  'data/course-capsule-v1/validation-receipt.json',
  'data/course-capsule-v1/README.md',
  'data/course-capsule-v1/backend-design-policy-v1.json',
  'data/course-capsule-v1/public-baseline-v0.62.12.json',
  'schema/course-capsule-v1/course-capsule-v1.schema.json',
  'schema/course-capsule-v1/backend-design-policy-v1.schema.json',
  'schema/course-capsule-v1/public-baseline-v1.schema.json',
]) {
  const [left, right] = await Promise.all([
    readFile(resolve(source, name)),
    readFile(resolve(target, name)),
  ]);
  assert.equal(right.length, left.length, `${name}: jumlah byte sinkron berbeda.`);
  assert.equal(sha256(right), sha256(left), `${name}: hash sinkron berbeda.`);
}

const readerRoot = 'readers/d40/unit14';
const listFiles = async (root, current = root) => {
  const rows = [];
  for (const entry of await readdir(resolve(source, current), { withFileTypes: true })) {
    const logical = `${current}/${entry.name}`;
    if (entry.isDirectory()) rows.push(...await listFiles(root, logical));
    else if (entry.isFile()) rows.push(logical.slice(root.length + 1));
  }
  return rows.sort();
};
const readerFiles = await listFiles(readerRoot);
assert.equal(readerFiles.length, 71, 'Penutupan pembaca D40 Unit 14 harus tepat 71 berkas.');
for (const name of readerFiles) {
  const logical = `${readerRoot}/${name}`;
  const [left, right] = await Promise.all([
    readFile(resolve(source, logical)),
    readFile(resolve(target, logical)),
  ]);
  assert.equal(right.length, left.length, `${logical}: jumlah byte sinkron berbeda.`);
  assert.equal(sha256(right), sha256(left), `${logical}: hash sinkron berbeda.`);
}

console.log('Static hub synchronized to public/hub with exact bytes.');
