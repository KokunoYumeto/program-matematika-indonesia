import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises';
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
  ['schemas/course-capsule-v1/course-capsule-v1.schema.json', 'docs/schema/course-capsule-v1/course-capsule-v1.schema.json'],
];

for (const [source, target] of mappings) {
  const sourcePath = resolve(project, source);
  const targetPath = resolve(project, target);
  await mkdir(dirname(targetPath), { recursive: true });
  await copyFile(sourcePath, targetPath);
  const [left, right] = await Promise.all([readFile(sourcePath), readFile(targetPath)]);
  assert.equal(right.length, left.length, `${target}: byte count drift.`);
  assert.equal(sha256(right), sha256(left), `${target}: hash drift.`);
}

const [jsonlBytes, jsonBytes, manifestBytes, receiptBytes] = await Promise.all([
  readFile(resolve(project, 'docs/data/course-capsule-v1/course-capsules.jsonl')),
  readFile(resolve(project, 'docs/data/course-capsule-v1/course-capsules.json')),
  readFile(resolve(project, 'docs/data/course-capsule-v1/manifest.json')),
  readFile(resolve(project, 'docs/data/course-capsule-v1/validation-receipt.json')),
]);
const rows = JSON.parse(jsonBytes.toString('utf8'));
const lines = jsonlBytes.toString('utf8').trimEnd().split('\n').map(JSON.parse);
const manifest = JSON.parse(manifestBytes.toString('utf8'));
const receipt = JSON.parse(receiptBytes.toString('utf8'));
assert.equal(rows.length, 40);
assert.deepEqual(rows, lines, 'Public JSON and canonical JSONL differ.');
assert.equal(new Set(rows.map(({ course_id }) => course_id)).size, 40);
assert.equal(manifest.output.bytes, jsonlBytes.length);
assert.equal(manifest.output.sha256, sha256(jsonlBytes));
assert.equal(manifest.projections.course_capsules_json.bytes, jsonBytes.length);
assert.equal(manifest.projections.course_capsules_json.sha256, sha256(jsonBytes));
assert.equal(receipt.state, 'pass');
assert.equal(receipt.checks.schema_instances, 40);

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
  const stateLabel = capsule.course.state === 'published' ? 'Edisi selesai' : 'Sedang diproduksi';
  return `<article class="course-card" data-static-course-id="${escapeHtml(capsule.course_id)}"><div class="card-top"><span class="course-code">${escapeHtml(capsule.course_id)}</span><span class="state-badge ${escapeHtml(capsule.course.state)}">${stateLabel}</span></div><h3>${escapeHtml(capsule.course.title)}</h3><p class="topic">${escapeHtml(capsule.course.topic)}</p><p class="outcome">${escapeHtml(capsule.course.outcome)}</p><p class="prerequisites"><strong>Prasyarat</strong>${escapeHtml(prerequisites)}</p><div class="view-panel"><div class="status-line"><span>Bahan pengajar terindeks</span><strong>${educatorCount}</strong></div><div class="card-actions"><a class="primary" href="${escapeHtml(primary)}" target="_blank" rel="noreferrer">Buka sumber utama ↗</a></div></div></article>`;
}).join('');
const templatePath = resolve(project, 'docs/backend/index.template.html');
const outputPath = resolve(project, 'docs/backend/index.html');
const template = await readFile(templatePath, 'utf8');
const start = '<!-- COURSE-FALLBACK:START -->';
const end = '<!-- COURSE-FALLBACK:END -->';
assert.equal(template.split(start).length - 1, 1);
assert.equal(template.split(end).length - 1, 1);
const rendered = template.replace(`${start}\n        ${end}`, `${start}\n        ${fallbackCards}\n        ${end}`);
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
