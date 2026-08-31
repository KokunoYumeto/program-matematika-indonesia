import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const mappings = [
  ['backend/course-capsule-v1/generated/course-capsules.jsonl', 'docs/data/course-capsule-v1/course-capsules.jsonl'],
  ['backend/course-capsule-v1/generated/course-capsules.json', 'docs/data/course-capsule-v1/course-capsules.json'],
  ['backend/course-capsule-v1/generated/manifest.json', 'docs/data/course-capsule-v1/manifest.json'],
  ['backend/course-capsule-v1/validation/VALIDATION_RECEIPT.json', 'docs/data/course-capsule-v1/validation-receipt.json'],
  ['backend/course-capsule-v1/README.md', 'docs/data/course-capsule-v1/README.md'],
  ['backend/course-capsule-v1/authority/backend-design-policy-v1.json', 'docs/data/course-capsule-v1/backend-design-policy-v1.json'],
  ['backend/course-capsule-v1/authority/public-baseline-v0.62.12.json', 'docs/data/course-capsule-v1/public-baseline-v0.62.12.json'],
  ['schemas/course-capsule-v1/course-capsule-v1.schema.json', 'docs/schema/course-capsule-v1/course-capsule-v1.schema.json'],
  ['schemas/course-capsule-v1/backend-design-policy-v1.schema.json', 'docs/schema/course-capsule-v1/backend-design-policy-v1.schema.json'],
  ['schemas/course-capsule-v1/public-baseline-v1.schema.json', 'docs/schema/course-capsule-v1/public-baseline-v1.schema.json'],
];

const sourceEntries = await Promise.all(mappings.map(async ([source, target]) => [
  source,
  target,
  await readFile(resolve(project, source)),
]));
const sourceBytesByPath = new Map(sourceEntries.map(([source, , bytes]) => [source, bytes]));
const jsonlBytes = sourceBytesByPath.get('backend/course-capsule-v1/generated/course-capsules.jsonl');
const jsonBytes = sourceBytesByPath.get('backend/course-capsule-v1/generated/course-capsules.json');
const manifestBytes = sourceBytesByPath.get('backend/course-capsule-v1/generated/manifest.json');
const receiptBytes = sourceBytesByPath.get('backend/course-capsule-v1/validation/VALIDATION_RECEIPT.json');
const rows = JSON.parse(jsonBytes.toString('utf8'));
const jsonlText = jsonlBytes.toString('utf8');
assert.ok(jsonlText.endsWith('\n'), 'Canonical JSONL must end with LF.');
const jsonlLines = jsonlText.slice(0, -1).split('\n');
assert.ok(jsonlLines.every((line) => line && line.trimEnd() === line), 'Canonical JSONL contains a blank line or trailing whitespace.');
const lines = jsonlLines.map(JSON.parse);
const manifest = JSON.parse(manifestBytes.toString('utf8'));
const receipt = JSON.parse(receiptBytes.toString('utf8'));
assert.equal(rows.length, 40);
assert.deepEqual(rows, lines, 'Public JSON and canonical JSONL differ.');
assert.equal(new Set(rows.map(({ course_id }) => course_id)).size, 40);
const layerNames = ['curriculum', 'translation', 'production', 'learner', 'educator', 'federation', 'interoperability'];
for (const row of rows) assert.deepEqual(Object.keys(row.layers).sort(), [...layerNames].sort(), `${row.course_id}: seven-layer contract drift.`);
assert.equal(rows.filter(({ course }) => course.state === 'published').length, 35);
assert.deepEqual(
  rows.filter(({ course }) => course.state === 'production').map(({ course_id }) => course_id),
  ['A20', 'A30', 'B95', 'C140', 'D100'],
);
const d40 = rows.find(({ course_id }) => course_id === 'D40');
assert.equal(d40.course.state, 'published');
assert.equal(d40.course_native.version, '2026.08.31-d40-complete');
assert.equal(d40.course_native.zenodo, 'https://doi.org/10.5281/zenodo.22184259');
assert.equal(d40.course_native.repository, undefined, 'D40 must not invent a producer repository.');
assert.equal(d40.layers.learner.pdf.sha256, 'c4e4f470eeb096129e7bf7306422d316c93aaeed99d2b12890e08f15777ac13f');
assert.equal(d40.layers.learner.portable_html.sha256, 'a370bba5ddb54081387a484a304b24af92691c3bc167db964c486625a79add59');
assert.equal(manifest.output.bytes, jsonlBytes.length);
assert.equal(manifest.output.sha256, sha256(jsonlBytes));
assert.equal(manifest.projections.course_capsules_json.bytes, jsonBytes.length);
assert.equal(manifest.projections.course_capsules_json.sha256, sha256(jsonBytes));
assert.equal(manifest.summary.course_count, 40);
assert.equal(manifest.summary.published_count, 35);
assert.equal(manifest.summary.production_count, 5);
assert.equal(receipt.state, 'pass');
assert.equal(receipt.checks.schema_instances, 40);
assert.equal(receipt.checks.seven_layer_rows, 40);
assert.equal(receipt.checks.published_count, 35);
assert.equal(receipt.checks.production_count, 5);
assert.deepEqual(receipt.peer_replay, { byte_identical: true, compared: true });
assert.deepEqual(receipt.artifacts.course_capsules_jsonl, {
  bytes: jsonlBytes.length,
  path: 'generated/course-capsules.jsonl',
  sha256: sha256(jsonlBytes),
});
assert.deepEqual(receipt.artifacts.course_capsules_json, {
  bytes: jsonBytes.length,
  path: 'generated/course-capsules.json',
  sha256: sha256(jsonBytes),
});
assert.deepEqual(receipt.artifacts.manifest_json, {
  bytes: manifestBytes.length,
  path: 'generated/manifest.json',
  sha256: sha256(manifestBytes),
});

for (const [, target, sourceBytes] of sourceEntries) {
  const targetPath = resolve(project, target);
  await mkdir(dirname(targetPath), { recursive: true });
  await writeFile(targetPath, sourceBytes);
  const publicBytes = await readFile(targetPath);
  assert.equal(publicBytes.length, sourceBytes.length, `${target}: byte count drift.`);
  assert.equal(sha256(publicBytes), sha256(sourceBytes), `${target}: hash drift.`);
}

const escapeHtml = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');
const fallbackCards = rows.map((capsule) => {
  const primary = capsule.layers.learner.primary?.url ?? capsule.course_native.edition;
  const prerequisites = capsule.course.prerequisites.length ? capsule.course.prerequisites.join(', ') : 'tidak ada';
  const educatorCount = capsule.layers.educator.features.length + capsule.layers.educator.resources.length;
  const learnerTools = capsule.layers.learner.tools
    .filter((tool) => tool.state !== 'planned' && tool.machine_data_is_learner_destination === false)
    .map((tool) => `<a class="learner-tool" href="../${escapeHtml(tool.href.replace(/^\/+/, ''))}" title="${escapeHtml(tool.scope)}">${escapeHtml(tool.label)}</a>`)
    .join('');
  const stateLabel = capsule.course.state === 'published' ? 'Edisi selesai' : 'Sedang diproduksi';
  return `<article class="course-card" data-static-course-id="${escapeHtml(capsule.course_id)}"><div class="card-top"><span class="course-code">${escapeHtml(capsule.course_id)}</span><span class="state-badge ${escapeHtml(capsule.course.state)}">${stateLabel}</span></div><h3>${escapeHtml(capsule.course.title)}</h3><p class="topic">${escapeHtml(capsule.course.topic)}</p><p class="outcome">${escapeHtml(capsule.course.outcome)}</p><p class="prerequisites"><strong>Prasyarat</strong>${escapeHtml(prerequisites)}</p><div class="view-panel"><div class="status-line"><span>Bahan pengajar terindeks</span><strong>${educatorCount}</strong></div>${learnerTools ? `<div class="status-line"><span>Alat belajar terverifikasi</span><strong>${capsule.layers.learner.tools.length}</strong></div>` : ''}<div class="card-actions">${learnerTools}<a class="primary" href="${escapeHtml(primary)}" target="_blank" rel="noreferrer">Buka sumber utama ↗</a></div></div></article>`;
}).join('');
const templatePath = resolve(project, 'docs/backend/index.template.html');
const outputPath = resolve(project, 'docs/backend/index.html');
const template = await readFile(templatePath, 'utf8');
const start = '<!-- COURSE-FALLBACK:START -->';
const end = '<!-- COURSE-FALLBACK:END -->';
assert.equal(template.split(start).length - 1, 1);
assert.equal(template.split(end).length - 1, 1);
let rendered = template.replace(`${start}\n        ${end}`, `${start}\n        ${fallbackCards}\n        ${end}`);
const summaryValues = {
  total: rows.length,
  published: rows.filter((row) => row.course.state === 'published').length,
  production: rows.filter((row) => row.course.state === 'production').length,
  educator: rows.filter((row) => row.layers.educator.features.length || row.layers.educator.resources.length).length,
};
for (const [name, count] of Object.entries(summaryValues)) {
  const pattern = new RegExp(`(<strong id="summary-${name}">)\\d+(</strong>)`, 'g');
  assert.equal([...rendered.matchAll(pattern)].length, 1, `Missing or duplicated ${name} summary.`);
  rendered = rendered.replace(pattern, (_, before, after) => `${before}${count}${after}`);
}
assert.equal((rendered.match(/data-static-course-id=/g) ?? []).length, 40);
await writeFile(outputPath, rendered);
const publicText = Buffer.concat([jsonlBytes, jsonBytes, manifestBytes, receiptBytes]).toString('utf8');
for (const pattern of [
  /C:\\\\Users\\\\/i,
  /Authorization:\s*Bearer/i,
  /access[_-]?token/i,
  /api[_-]?token/i,
  /"access"\s*:\s*"(?:private|restricted|embargoed|blocked)"/i,
]) assert.doesNotMatch(publicText, pattern);

console.log(JSON.stringify({
  status: 'pass',
  public_course_rows: rows.length,
  copied_files: mappings.length,
  static_fallback_rows: 40,
  jsonl: { bytes: jsonlBytes.length, sha256: sha256(jsonlBytes) },
  json: { bytes: jsonBytes.length, sha256: sha256(jsonBytes) },
}, null, 2));
