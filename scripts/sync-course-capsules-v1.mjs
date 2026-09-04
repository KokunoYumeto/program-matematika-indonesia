import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const successorSidecarSource = 'backend/course-capsule-v1/authority/clp-family-v231/learner-reader-actions-v1.json';
const successorSidecarSchemaSource = 'schemas/v1/learner-reader-actions-v1.schema.json';
const successorSidecarTargets = [
  'backend/course-capsule-v1/generated/learner-reader-actions-v1.json',
  'docs/data/course-capsule-v1/learner-reader-actions-v1.json',
];
const successorSidecarAvailable = existsSync(resolve(project, successorSidecarSource));
const mappings = [
  ['backend/course-capsule-v1/generated/course-capsules.jsonl', 'docs/data/course-capsule-v1/course-capsules.jsonl'],
  ['backend/course-capsule-v1/generated/course-capsules.json', 'docs/data/course-capsule-v1/course-capsules.json'],
  ['backend/course-capsule-v1/generated/manifest.json', 'docs/data/course-capsule-v1/manifest.json'],
  ['backend/course-capsule-v1/validation/VALIDATION_RECEIPT.json', 'docs/data/course-capsule-v1/validation-receipt.json'],
  ['backend/course-capsule-v1/README.md', 'docs/data/course-capsule-v1/README.md'],
  ['backend/course-capsule-v1/authority/backend-design-policy-v1.json', 'docs/data/course-capsule-v1/backend-design-policy-v1.json'],
  ['backend/course-capsule-v1/authority/public-baseline-v0.62.12.json', 'docs/data/course-capsule-v1/public-baseline-v0.62.12.json'],
  ['backend/course-capsule-v1/authority/native-package-references-v1.json', 'docs/data/course-capsule-v1/native-package-references-v1.json'],
  ['backend/course-capsule-v1/authority/native-terminology-qa/unib-teori-bilangan-20260831/README.md', 'docs/data/course-capsule-v1/native-terminology-qa/unib-teori-bilangan-20260831/README.md'],
  ['backend/course-capsule-v1/authority/native-terminology-qa/unib-teori-bilangan-20260831/terminology_concordance.json', 'docs/data/course-capsule-v1/native-terminology-qa/unib-teori-bilangan-20260831/terminology_concordance.json'],
  ['backend/course-capsule-v1/authority/native-terminology-qa/unib-teori-bilangan-20260831/checksums.sha256', 'docs/data/course-capsule-v1/native-terminology-qa/unib-teori-bilangan-20260831/checksums.sha256'],
  ['backend/course-capsule-v1/authority/terminology-policy-v1/README.md', 'docs/data/course-capsule-v1/terminology-policy-v1/README.md'],
  ['backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json', 'docs/data/course-capsule-v1/terminology-policy-v1/canonical-register-policy.json'],
  ['backend/course-capsule-v1/authority/terminology-policy-v1/checksums.sha256', 'docs/data/course-capsule-v1/terminology-policy-v1/checksums.sha256'],
  ['backend/course-capsule-v1/validation/manager-followthrough/NATIVE_FAMILY_PUBLIC_EVIDENCE_INDEX_V06213_20260831.json', 'docs/data/course-capsule-v1/native-family-public-evidence-v1.json'],
  ['backend/course-capsule-v1/validation/manager-followthrough/NATIVE_FAMILY_PUBLIC_EVIDENCE_NOTE_V06213_20260831.md', 'docs/data/course-capsule-v1/native-family-public-evidence-note-v1.md'],
  ['schemas/course-capsule-v1/course-capsule-v1.schema.json', 'docs/schema/course-capsule-v1/course-capsule-v1.schema.json'],
  ['schemas/course-capsule-v1/native-catalog-record-v1.schema.json', 'docs/schema/course-capsule-v1/native-catalog-record-v1.schema.json'],
  ['schemas/course-capsule-v1/course-learning-capability-v1.schema.json', 'docs/schema/course-capsule-v1/course-learning-capability-v1.schema.json'],
  ['schemas/course-capsule-v1/backend-design-policy-v1.schema.json', 'docs/schema/course-capsule-v1/backend-design-policy-v1.schema.json'],
  ['schemas/course-capsule-v1/public-baseline-v1.schema.json', 'docs/schema/course-capsule-v1/public-baseline-v1.schema.json'],
  ['schemas/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json', 'docs/schema/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json'],
  ['schemas/course-capsule-v1/v2/terminology-concept-record-v1.schema.json', 'docs/schema/course-capsule-v1/v2/terminology-concept-record-v1.schema.json'],
  ['backend/course-capsule-v1/adapters/d80-capability-v1/views/D80.html', 'docs/backend/d80/D80.html'],
  ['backend/course-capsule-v1/adapters/d80-capability-v1/views/D80-pengajar.html', 'docs/backend/d80/D80-pengajar.html'],
  ['backend/course-capsule-v1/adapters/d80-capability-v1/data/learning-map.json', 'docs/backend/d80/learning-map.json'],
  ['backend/course-capsule-v1/adapters/d80-capability-v1/validation.json', 'docs/backend/d80/validation.json'],
  ...(existsSync(resolve(project, successorSidecarSchemaSource)) ? [[successorSidecarSchemaSource, 'docs/schema/v1/learner-reader-actions-v1.schema.json']] : []),
  ...(successorSidecarAvailable ? successorSidecarTargets.map((target) => [successorSidecarSource, target]) : []),
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
const successorSidecarBytes = sourceBytesByPath.get(successorSidecarSource);
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
const c80 = rows.find(({ course_id }) => course_id === 'C80');
assert.equal(c80.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(c80.layers.interoperability.semantic_adapter.contract_version, '2.3.1');
assert.equal(c80.layers.interoperability.semantic_adapter.mapping_scope, 'reversible_native_course_route_adapter');
assert.equal(c80.layers.learner.tools.length, 1);
assert.equal(c80.layers.learner.tools[0].href, 'backend/openlogic/C80.html');
assert.equal(c80.layers.learner.tools[0].primary, true);
const c130 = rows.find(({ course_id }) => course_id === 'C130');
assert.equal(c130.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(c130.layers.interoperability.semantic_adapter.contract_version, '2.3.1');
assert.equal(c130.layers.interoperability.semantic_adapter.mapping_scope, 'reversible_native_course_route_adapter');
assert.equal(c130.layers.learner.tools.length, 1);
assert.equal(c130.layers.learner.tools[0].href, 'backend/c130/C130.html');
assert.equal(c130.layers.learner.tools[0].primary, true);
for (const id of ['A10', 'D100']) {
  const row = rows.find(({ course_id }) => course_id === id);
  assert.equal(row.layers.translation.terminology_status, 'in_progress');
  assert.equal(row.layers.translation.corrections_status, 'in_progress');
}
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

// The CLP successor reader routes are intentionally a separate, additive
// projection.  Keep this old capsule sync runnable when the successor
// authority is not present, but validate every successor row whenever it is
// available so a malformed sidecar can never become a learner link.
let readerActionsByCourseId = new Map();
let successorSidecarSummary = null;
if (successorSidecarBytes) {
  const sidecar = JSON.parse(successorSidecarBytes.toString('utf8'));
  assert.equal(sidecar.schema_id, 'interlanguage/learner-reader-actions/v1');
  assert.equal(sidecar.schema_version, '1.0.0');
  assert.equal(sidecar.locale, 'id-ID');
  assert.equal(sidecar.status, 'verified_route_evidence_projection');
  const actions = Array.isArray(sidecar.actions) ? sidecar.actions : [];
  assert.equal(actions.length, 7, 'CLP successor sidecar must contain seven reader actions.');
  assert.deepEqual([...new Set(actions.map(({ action_id }) => action_id))].length, 7);
  assert.deepEqual([...new Set(actions.map(({ course_id }) => course_id))].sort(), ['B20', 'B30', 'B50', 'B60']);
  assert.deepEqual(actions.map(({ order }) => order), [1, 2, 3, 4, 5, 6, 7]);
  for (const action of actions) {
    assert.match(action.action_id, /^(B20|B30|B50|B60):reader:[a-z]+$/u);
    assert.match(action.course_id, /^(B20|B30|B50|B60)$/u);
    assert.equal(action.state, 'verified');
    assert.equal(action.format, 'application/pdf');
    assert.equal(action.route_granularity, 'whole_file_only');
    assert.equal(action.scope === 'whole_course' || action.scope === 'whole_course_companion' || action.scope === 'whole_course_combined_reader', true);
    assert.equal(Number.isInteger(action.pages) && action.pages > 0, true);
    assert.equal(Number.isInteger(action.bytes) && action.bytes > 0, true);
    assert.match(action.sha256, /^[0-9a-f]{64}$/iu);
    assert.match(action.url, /^https:\/\/[^\s]+$/u);
    assert.equal(typeof action.label, 'string');
  }
  const summary = sidecar.summary ?? {};
  assert.deepEqual(
    {
      course_count: summary.course_count,
      action_count: summary.action_count,
      pages: summary.pages,
      bytes: summary.bytes,
      verified_action_count: summary.verified_action_count,
    },
    { course_count: 4, action_count: 7, pages: 4077, bytes: 35639691, verified_action_count: 7 },
  );
  assert.equal(actions.reduce((total, action) => total + action.pages, 0), summary.pages);
  assert.equal(actions.reduce((total, action) => total + action.bytes, 0), summary.bytes);
  readerActionsByCourseId = new Map(
    ['B20', 'B30', 'B50', 'B60'].map((courseId) => [
      courseId,
      actions.filter((action) => action.course_id === courseId).sort((left, right) => left.order - right.order),
    ]),
  );
  successorSidecarSummary = {
    bytes: successorSidecarBytes.length,
    sha256: sha256(successorSidecarBytes),
    action_count: actions.length,
    pages: summary.pages,
    reader_bytes: summary.bytes,
  };
}
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
const deliverableStatuses = new Set(['verified', 'available_unverified']);
const learnerDeliveryFormats = new Set(['text/html', 'application/pdf', 'application/epub+zip', 'application/zip+html']);
const statusLabels = {
  verified: 'terverifikasi',
  legacy_verified: 'terverifikasi — kontrak lama',
  available_unverified: 'tersedia; belum diverifikasi penuh',
  in_progress: 'sedang dibuat',
  not_yet_produced: 'belum dibuat',
  not_applicable: 'tidak berlaku',
  unknown: 'belum diketahui',
};
const statusLabel = (status) => statusLabels[status] ?? status;
const publicEvidenceUrl = (url) => typeof url === 'string' && /^https:\/\/[^/\s]+\//.test(url);
const eligibleDelivery = (resource, allowedFormats) => deliverableStatuses.has(resource?.status)
  && allowedFormats.has(resource?.format)
  && publicEvidenceUrl(resource?.url);
const fallbackCards = rows.map((capsule) => {
  const layer = capsule.layers.learner;
  const primary = capsule.locale === 'id-ID' ? [
    [layer.primary, learnerDeliveryFormats],
    [layer.online_html, new Set(['text/html'])],
    [layer.pdf, new Set(['application/pdf'])],
    [layer.epub, new Set(['application/epub+zip'])],
    [layer.portable_html, new Set(['application/zip+html'])],
  ].find(([resource, formats]) => eligibleDelivery(resource, formats))?.[0] : undefined;
  const prerequisites = capsule.course.prerequisites.length ? capsule.course.prerequisites.join(', ') : 'tidak ada';
  const learnerTools = capsule.layers.learner.tools
    .filter((tool) => tool.state === 'verified' && tool.machine_data_is_learner_destination === false)
    .map((tool) => `<a class="learner-tool${tool.primary ? ' primary' : ''}" href="../${escapeHtml(tool.href.replace(/^\/+/, ''))}" title="${escapeHtml(tool.scope)}">${escapeHtml(tool.label)}<span class="sr-only"> — ${escapeHtml(capsule.course_id)}</span></a>`)
    .join('');
  const readerActions = (readerActionsByCourseId.get(capsule.course_id) ?? [])
    .map((action) => `<a class="reader-action" href="${escapeHtml(action.url)}" target="_blank" rel="noreferrer">${escapeHtml(action.label)} <span aria-hidden="true">↗</span><span class="sr-only"> (terbuka di tab baru)</span></a>`)
    .join('');
  const readerActionHrefs = new Set((readerActionsByCourseId.get(capsule.course_id) ?? []).map((action) => action.url));
  const primaryAction = primary && !readerActionHrefs.has(primary.url)
    ? `<a class="primary" href="${escapeHtml(primary.url)}" target="_blank" rel="noreferrer">Buka sumber utama — ${escapeHtml(capsule.course_id)} <span aria-hidden="true">↗</span><span class="sr-only"> (terbuka di tab baru)</span></a>`
    : readerActions
      ? ''
      : '<span class="empty-note">Rute sumber utama belum memenuhi bukti format dan akses publik.</span>';
  const stateLabel = capsule.course.state === 'published' ? 'Edisi selesai' : 'Sedang diproduksi';
  return `<article class="course-card" data-static-course-id="${escapeHtml(capsule.course_id)}"><div class="card-top"><span class="course-code">${escapeHtml(capsule.course_id)}</span><span class="state-badge ${escapeHtml(capsule.course.state)}">${stateLabel}</span></div><h3>${escapeHtml(capsule.course.title)}</h3><p class="topic">${escapeHtml(capsule.course.topic)}</p><p class="outcome">${escapeHtml(capsule.course.outcome)}</p><p class="prerequisites"><strong>Prasyarat</strong>${escapeHtml(prerequisites)}</p><div class="view-panel"><div class="status-line"><span>Kesiapan akses</span><strong>${escapeHtml(statusLabel(layer.status))}</strong></div>${readerActions ? `<div class="status-line"><span>Rute pembaca CLP</span><strong>${readerActionsByCourseId.get(capsule.course_id).length}</strong></div>` : ''}${learnerTools ? `<div class="status-line"><span>Alat belajar terverifikasi</span><strong>${capsule.layers.learner.tools.filter((tool) => tool.state === 'verified').length}</strong></div>` : ''}<div class="status-line"><span>HTML semantik</span><strong>${escapeHtml(statusLabel(layer.capabilities.semantic_html))}</strong></div><div class="status-line"><span>Format cetak</span><strong>${escapeHtml(statusLabel(layer.capabilities.print_profile))}</strong></div><div class="card-actions">${readerActions}${learnerTools}${primaryAction}</div></div></article>`;
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
const publicText = Buffer.concat([jsonlBytes, jsonBytes, manifestBytes, receiptBytes, ...(successorSidecarBytes ? [successorSidecarBytes] : [])]).toString('utf8');
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
  successor_sidecar: successorSidecarSummary,
  jsonl: { bytes: jsonlBytes.length, sha256: sha256(jsonlBytes) },
  json: { bytes: jsonBytes.length, sha256: sha256(jsonBytes) },
}, null, 2));
