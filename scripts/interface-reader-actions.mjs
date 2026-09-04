import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';

export const readerActionInput = 'docs/data/course-capsule-v1/learner-reader-actions-v1.json';
export function projectReaderActions(source, knownCourseIds) {
  assert.equal(source.schema_id, 'interlanguage/learner-reader-actions/v1');
  assert.equal(source.status, 'verified_route_evidence_projection');
  assert.equal(source.locale, 'id-ID');
  assert.ok(Array.isArray(source.actions));
  const seen = new Set();
  const actions = source.actions.map((row) => {
    assert.ok(knownCourseIds.includes(row.course_id), 'Unknown course');
    assert.ok(row.action_id && !seen.has(row.action_id), 'Duplicate action');
    seen.add(row.action_id);
    assert.equal(row.state, 'verified');
    assert.equal(row.evidence?.status, 'pass_receipt_bound');
    assert.equal(row.format, 'application/pdf');
    assert.equal(row.route_granularity, 'whole_file_only');
    assert.ok(['textbook', 'problembook', 'combined_textbook_problembook'].includes(row.role));
    assert.ok(['default_primary', 'learner_primary_companion'].includes(row.learner_surface_role));
    assert.equal(new URL(row.url).protocol, 'https:');
    assert.ok(/^[a-f0-9]{64}$/.test(row.sha256));
    for (const key of ['pages', 'bytes', 'course_order', 'order']) assert.ok(Number.isSafeInteger(row[key]) && row[key] > 0, key);
    return { actionId: row.action_id, courseId: row.course_id, order: row.course_order, label: row.label,
      role: row.role, surfaceRole: row.learner_surface_role, href: row.url, contentLanguage: 'id',
      pages: row.pages, bytes: row.bytes, sha256: row.sha256,
      offlineAfterDownload: row.offline?.dependency_free_after_download === true && row.offline?.post_download_reading_is_offline === true,
      evidenceLocator: row.evidence.locator };
  }).sort((a, b) => knownCourseIds.indexOf(a.courseId) - knownCourseIds.indexOf(b.courseId) || a.order - b.order);
  assert.equal(actions.length, source.summary.action_count);
  assert.equal(actions.length, source.summary.verified_action_count);
  assert.equal(new Set(actions.map((row) => row.courseId)).size, source.summary.course_count);
  assert.equal(actions.reduce((sum, row) => sum + row.pages, 0), source.summary.pages);
  assert.equal(actions.reduce((sum, row) => sum + row.bytes, 0), source.summary.bytes);
  return actions;
}
export async function syncReaderActions(root, knownCourseIds) {
  const bytes = await readFile(resolve(root, readerActionInput));
  const actions = projectReaderActions(JSON.parse(bytes), knownCourseIds);
  const identity = { path: readerActionInput, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') };
  await writeFile(resolve(root, 'docs/interface/reader-actions.js'),
    '// Generated interface projection; the integrated backend input remains authoritative.\n'
    + 'export const readerActionSource = Object.freeze(' + JSON.stringify(identity) + ');\n'
    + 'export const verifiedReaderActions = Object.freeze(' + JSON.stringify(actions) + ');\n');
}
