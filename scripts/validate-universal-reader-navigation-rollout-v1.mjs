import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { liveCoursePublications } from '../docs/live-course-publications.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const rolloutPath = 'backend/authority/federated-navigation-publications/universal-reader-navigation-rollout-20260906.json';
const contractPath = 'backend/authority/universal-reader-navigation-contract-v1.json';
const finalEditionsPath = 'docs/interface/final-editions.json';

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
async function readJson(path) {
  const bytes = await readFile(resolve(root, path));
  return { bytes, value: JSON.parse(bytes) };
}
async function verifyBinding(binding) {
  const bytes = await readFile(resolve(root, binding.path));
  assert.equal(bytes.length, binding.bytes, `${binding.path}: bytes`);
  assert.equal(sha256(bytes), binding.sha256, `${binding.path}: sha256`);
}

function validateBatchReceipt(batch, receipt) {
  if (batch.id === 'batch1') {
    assert.equal(receipt.result, 'pass');
    assert.equal(receipt.totals.repositories_published, batch.repository_count);
    assert.equal(receipt.totals.repositories_publicly_verified, batch.repository_count);
    assert.equal(receipt.totals.published_html_documents, batch.published_html_documents);
    assert.equal(receipt.totals.failed_results, 0);
  } else if (batch.id === 'batch2') {
    assert.equal(receipt.status, 'pass');
    assert.equal(receipt.browser_used, false);
    assert.equal(receipt.author_contact, false);
    assert.equal(receipt.repositories.length, batch.repository_count);
    assert.equal(receipt.repositories.reduce(
      (total, row) => total + row.published_html_documents, 0,
    ), batch.published_html_documents);
  } else if (batch.id === 'batch3') {
    assert.equal(receipt.browser_used, false);
    assert.equal(receipt.summary.all_pass, true);
    assert.equal(receipt.summary.failures, 0);
    assert.equal(receipt.summary.repositories, batch.repository_count);
    assert.equal(receipt.summary.html_documents_anonymously_verified,
      batch.published_html_documents);
  } else if (batch.id === 'batch4') {
    assert.equal(receipt.status, 'verified');
    assert.equal(receipt.repositories, batch.repository_count);
    assert.equal(receipt.published_html_documents, batch.published_html_documents);
  } else if (batch.id === 'original-english-openstax') {
    assert.equal(receipt.status, 'complete_public_and_independently_sampled');
    assert.equal(receipt.credentials_recorded, false);
    assert.equal(receipt.author_contact, false);
    assert.equal(receipt.aggregate.repositories, batch.repository_count);
    assert.equal(receipt.aggregate.html_documents_under_navigation_contract,
      batch.published_html_documents);
    assert.equal(receipt.aggregate.public_sample_failures, 0);
  } else if (batch.id === 'd90-live-html') {
    assert.equal(receipt.summary.status, 'pass');
    assert.equal(receipt.summary.total_html_pages_verified,
      batch.published_html_documents);
    assert.equal(receipt.summary.http_200, batch.published_html_documents);
    assert.equal(receipt.summary.exact_byte_matches, batch.published_html_documents);
    assert.equal(receipt.summary.navigation_contract_passes,
      batch.published_html_documents);
    assert.equal(receipt.credential_material_present, false);
  } else {
    assert.fail(`Unvalidated navigation batch schema: ${batch.id}`);
  }
}

const [{ bytes: rolloutBytes, value: rollout }, { value: contract }, { value: finalEditions }] = await Promise.all([
  readJson(rolloutPath),
  readJson(contractPath),
  readJson(finalEditionsPath),
]);

assert.equal(rollout.schema_name, 'universal-reader-navigation-rollout');
assert.equal(rollout.schema_version, '1.0.0');
assert.equal(rollout.status, 'public-and-verified');
assert.equal(rollout.contract.path, contractPath);
assert.equal(contract.scope.html_documents, 'every-published-learner-html-document-not-only-the-landing-page');
assert.deepEqual(rollout.contract.current_languages, ['id', 'en']);
assert.equal(rollout.contract.language_route_pattern, '/{language_id}/');

const batches = rollout.github_pages_rollout.batches;
assert.equal(batches.reduce((total, row) => total + row.repository_count, 0),
  rollout.github_pages_rollout.repository_count);
assert.equal(batches.reduce((total, row) => total + row.published_html_documents, 0),
  rollout.github_pages_rollout.published_html_documents);
assert.equal(rollout.github_pages_rollout.repository_count, 25);
assert.equal(rollout.github_pages_rollout.published_html_documents, 42255);
assert.equal(new Set(batches.flatMap((row) => row.course_roles)).size,
  rollout.github_pages_rollout.distinct_course_roles);
assert.equal(rollout.github_pages_rollout.distinct_course_roles, 23);

const zenodoRecords = rollout.zenodo_preservation_rollout.records;
assert.equal(zenodoRecords.reduce((total, row) => total + row.html_documents, 0),
  rollout.zenodo_preservation_rollout.preserved_html_documents);
assert.equal(rollout.zenodo_preservation_rollout.preserved_html_documents, 21);
assert.match(rollout.zenodo_preservation_rollout.browser_delivery_rule, /offline preservation copy/);

const referencedBindings = [
  ...batches.map((row) => row.receipt),
  ...zenodoRecords.flatMap((row) => [row.receipt, row.independent_qa].filter(Boolean)),
  rollout.central_selected_surface_audit.receipt,
  rollout.central_selected_surface_audit.registry,
  ...rollout.course_entrypoint_bindings.flatMap((row) => [row.live_html, row.preservation]),
];
for (const binding of referencedBindings) await verifyBinding(binding);
for (const batch of batches) {
  const { value: receipt } = await readJson(batch.receipt.path);
  validateBatchReceipt(batch, receipt);
}

const { value: publicAudit } = await readJson(rollout.central_selected_surface_audit.receipt.path);
const { value: publicRegistry } = await readJson(rollout.central_selected_surface_audit.registry.path);
assert.deepEqual(publicAudit.summary, {
  expected_surfaces: 28,
  http_200: 28,
  observed_surfaces: 28,
  remediation_required: 0,
  verified: 28,
});
assert.deepEqual(publicRegistry.summary, {
  central_navigation_validated: 28,
  http_200: 28,
  remediation_required: 0,
  surfaces: 28,
  verified: 28,
});
assert.equal(publicRegistry.schema_version, '1.1.0');

const d100 = finalEditions.editions.find((row) => row.courseId === 'D100');
assert.ok(d100);
assert.equal(d100.archive, 'https://doi.org/10.5281/zenodo.22543825');
assert.equal(d100.resources.length, 8);
for (const id of ['D100:curves-html', 'D100:bgk-html']) {
  const resource = d100.resources.find((row) => row.id === id);
  assert.ok(resource.href.startsWith('https://kokunoyumeto.github.io/algebraic-geometry-bridge-id/'));
  assert.equal(resource.kind, 'reader');
  assert.equal(resource.offlineAfterDownload, false);
}
for (const id of ['D100:curves-html-download', 'D100:bgk-html-download', 'D100:bridge-html']) {
  const resource = d100.resources.find((row) => row.id === id);
  assert.equal(resource.kind, 'portable_html');
  assert.equal(resource.offlineAfterDownload, true);
}

assert.equal(liveCoursePublications.D90.reader,
  'https://kokunoyumeto.github.io/advanced-optimization-convex-analysis-id/');
assert.equal(liveCoursePublications.D90.zenodo, 'https://doi.org/10.5281/zenodo.22543810');
assert.equal(liveCoursePublications.D100.reader,
  'https://kokunoyumeto.github.io/algebraic-geometry-bridge-id/');
assert.equal(liveCoursePublications.D100.zenodo, 'https://doi.org/10.5281/zenodo.22543825');

assert.equal(rollout.integrity_and_limits.mathematical_content_changed_by_navigation_rollout, false);
assert.equal(rollout.integrity_and_limits.authoritative_originals_replaced_by_mirrors, false);
assert.equal(rollout.integrity_and_limits.offline_downloads_claimed_as_live_html, false);

process.stdout.write(`${JSON.stringify({
  status: 'pass',
  rollout: { path: rolloutPath, bytes: rolloutBytes.length, sha256: sha256(rolloutBytes) },
  github_pages: rollout.github_pages_rollout,
  zenodo_preserved_html_documents: rollout.zenodo_preservation_rollout.preserved_html_documents,
  selected_public_surfaces: publicRegistry.summary,
  referenced_bindings_verified: referencedBindings.length,
})}\n`);
