import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, extname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { courses as authorityCourses } from '../docs/courses.js';
import { materializeLiveCourses } from '../docs/live-course-publications.js';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const paths = {
  courses: 'docs/courses.js',
  overlay: 'docs/live-course-publications.js',
  overrides: 'backend/authority/learner-delivery-overrides-v1.json',
  schema: 'schemas/v1/learner-delivery-v1.schema.json',
  authority: 'backend/authority/learner-delivery-v1.json',
  publicJson: 'docs/data/learner-delivery-v1.json',
  publicModule: 'docs/learner-delivery.js',
};
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const canonical = (value) => `${JSON.stringify(value, null, 2)}\n`;
const fileIdentity = (path, bytes) => ({ path, bytes: bytes.length, sha256: sha256(bytes) });
const absent = () => ({ status: 'absent' });
const available = (url, format) => ({ status: 'available_unverified', format, url });
const resourceExtension = (url) => extname(new URL(url).pathname).toLowerCase();
const resourceFormat = (url, htmlUrl = null) => {
  if (url === htmlUrl) return 'text/html';
  const extension = resourceExtension(url);
  if (extension === '.pdf') return 'application/pdf';
  if (extension === '.epub') return 'application/epub+zip';
  if (extension === '.json') return 'application/json';
  if (extension === '.jsonl') return 'application/x-ndjson';
  if (extension === '.zip') return 'application/zip';
  return 'application/octet-stream';
};

const [coursesBytes, overlayBytes, overridesBytes, schemaBytes] = await Promise.all([
  readFile(resolve(project, paths.courses)),
  readFile(resolve(project, paths.overlay)),
  readFile(resolve(project, paths.overrides)),
  readFile(resolve(project, paths.schema)),
]);
const overrides = JSON.parse(overridesBytes.toString('utf8'));
assert.equal(overrides.schema_version, '1.0.0');
const effectiveCourses = materializeLiveCourses(authorityCourses);
assert.equal(effectiveCourses.length, 40, 'Learner delivery requires exactly 40 effective courses.');
assert.equal(new Set(effectiveCourses.map(({ id }) => id)).size, 40, 'Course IDs must be unique.');
for (const id of Object.keys(overrides.courses)) {
  assert.ok(effectiveCourses.some((course) => course.id === id), `Unknown delivery override ${id}.`);
}

const rows = effectiveCourses.map((course) => {
  const primaryUrl = course.learner ?? course.reader ?? course.edition ?? null;
  const onlineHtmlUrl = course.reader ?? course.learner ?? null;
  const editionExtension = course.edition ? resourceExtension(course.edition) : '';
  const base = {
    course_id: course.id,
    primary: primaryUrl ? available(primaryUrl, resourceFormat(primaryUrl, onlineHtmlUrl)) : absent(),
    online_html: onlineHtmlUrl ? available(onlineHtmlUrl, 'text/html') : absent(),
    pdf: editionExtension === '.pdf' ? available(course.edition, 'application/pdf') : absent(),
    epub: absent(),
    portable_html: absent(),
    capabilities: {
      semantic_html: { status: 'available_unverified' },
      mathml: { status: 'available_unverified' },
      print_profile: { status: 'available_unverified' },
      chapter_downloads: { status: 'absent' },
    },
    missing_capabilities: [],
  };
  if (!onlineHtmlUrl) {
    base.capabilities.semantic_html = { status: 'absent' };
    base.capabilities.mathml = { status: 'absent' };
    base.capabilities.print_profile = { status: 'absent' };
  }
  const override = overrides.courses[course.id] ?? {};
  for (const key of ['primary', 'online_html', 'pdf', 'epub', 'portable_html']) {
    if (override[key]) base[key] = structuredClone(override[key]);
  }
  if (override.capabilities) base.capabilities = { ...base.capabilities, ...structuredClone(override.capabilities) };
  base.missing_capabilities = [
    ['online_html', base.online_html],
    ['pdf', base.pdf],
    ['epub', base.epub],
    ['portable_html', base.portable_html],
    ...Object.entries(base.capabilities),
  ].filter(([, value]) => value.status === 'absent').map(([name]) => name).sort();
  return base;
});

for (const row of rows) {
  for (const key of ['primary', 'online_html', 'pdf', 'epub', 'portable_html']) {
    const resource = row[key];
    assert.ok(['verified', 'available_unverified', 'absent', 'not_applicable'].includes(resource.status), `${row.course_id}/${key}: invalid status.`);
    if (resource.status === 'verified') {
      assert.ok(resource.url && Number.isInteger(resource.bytes) && /^[0-9a-f]{64}$/.test(resource.sha256), `${row.course_id}/${key}: incomplete verified identity.`);
    }
  }
  if (row.portable_html.status === 'verified') {
    assert.match(row.portable_html.format, /zip\+html/);
    assert.equal(row.portable_html.dependency_free, true);
    assert.ok(row.portable_html.entry_point && Number.isInteger(row.portable_html.inventory_count));
  }
  if (row.primary.url && row.pdf.url && row.primary.url === row.pdf.url) {
    assert.equal(row.primary.format, 'application/pdf', `${row.course_id}/primary: PDF utama memiliki MIME yang salah.`);
  }
}

const sidecar = {
  $schema: 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v1/learner-delivery-v1.schema.json',
  schema_id: 'interlanguage/program-matematika-indonesia-learner-delivery/v1',
  schema_version: '1.0.0',
  locale: 'id-ID',
  provenance: {
    courses_js: fileIdentity(paths.courses, coursesBytes),
    live_overlay_js: fileIdentity(paths.overlay, overlayBytes),
    overrides_json: fileIdentity(paths.overrides, overridesBytes),
    schema_json: fileIdentity(paths.schema, schemaBytes),
  },
  policy: {
    machine_data_is_secondary: true,
    pdf_is_not_portable_html: true,
    source_archive_is_not_learner_package: true,
    unknown_is_not_verified: true,
    status_values: ['verified', 'available_unverified', 'absent', 'not_applicable'],
  },
  courses: rows,
  summary: {
    course_count: rows.length,
    online_html_available: rows.filter(({ online_html }) => online_html.status !== 'absent').length,
    verified_portable_html: rows.filter(({ portable_html }) => portable_html.status === 'verified').length,
    verified_epub: rows.filter(({ epub }) => epub.status === 'verified').length,
  },
};
const sidecarBytes = Buffer.from(canonical(sidecar));
const compactRows = JSON.stringify(rows.map((row) => ({
  course_id: row.course_id,
  online_html: { status: row.online_html.status },
  epub: row.epub,
  portable_html: row.portable_html,
  capabilities: { mathml: row.capabilities.mathml },
})));
const moduleText = `// Generated by scripts/build-learner-delivery-v1.mjs. Machine detail stays secondary to the learner interface.\nexport const learnerDeliveryRows = Object.freeze(${compactRows});\nexport const learnerDeliveryByCourseId = Object.freeze(Object.fromEntries(learnerDeliveryRows.map((row) => [row.course_id, row])));\n`;

await Promise.all([
  mkdir(dirname(resolve(project, paths.authority)), { recursive: true }),
  mkdir(dirname(resolve(project, paths.publicJson)), { recursive: true }),
  mkdir(dirname(resolve(project, paths.publicModule)), { recursive: true }),
]);
await Promise.all([
  writeFile(resolve(project, paths.authority), sidecarBytes),
  writeFile(resolve(project, paths.publicJson), sidecarBytes),
  writeFile(resolve(project, paths.publicModule), moduleText, 'utf8'),
]);
const [authorityWritten, publicWritten] = await Promise.all([
  readFile(resolve(project, paths.authority)),
  readFile(resolve(project, paths.publicJson)),
]);
assert.deepEqual(publicWritten, authorityWritten, 'Public learner-delivery sidecar differs from authority bytes.');
console.log(JSON.stringify({ status: 'pass', bytes: sidecarBytes.length, sha256: sha256(sidecarBytes), ...sidecar.summary }, null, 2));
