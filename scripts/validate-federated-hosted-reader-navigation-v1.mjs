import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  CENTRAL_PROGRAM_ORIGIN,
  FEDERATED_SELECTION_VERSION,
  extractFederatedHostedHtmlSurfaces,
  federatedSurfaceProjection,
  inferCustodian,
  sha256,
  stableJson,
  stableJsonBytes,
} from './federated-hosted-reader-navigation-lib-v1.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const manifestPath = 'docs/interface/learner-access-manifest.json';
const registryPath = 'backend/authority/federated-hosted-reader-navigation-v1.json';
const centralNavigationPath = 'backend/authority/central-reader-navigation-v1.json';
const [manifestBytes, registryBytes, centralNavigationBytes] = await Promise.all([
  readFile(resolve(root, manifestPath)),
  readFile(resolve(root, registryPath)),
  readFile(resolve(root, centralNavigationPath)),
]);
const manifest = JSON.parse(manifestBytes);
const registry = JSON.parse(registryBytes);
const centralNavigation = JSON.parse(centralNavigationBytes);
const receiptPath = registry.current_audit_receipt.path;
const receiptBytes = await readFile(resolve(root, receiptPath));
const receipt = JSON.parse(receiptBytes);

assert.equal(registry.schema_name, 'federated-hosted-reader-navigation-registry');
assert.equal(registry.schema_version, '1.0.0');
assert.equal(registry.central_program_origin, CENTRAL_PROGRAM_ORIGIN);
assert.equal(registry.source_manifest.path, manifestPath);
assert.equal(registry.source_manifest.selection_version, FEDERATED_SELECTION_VERSION);
assert.equal(registry.current_audit_receipt.bytes, receiptBytes.length);
assert.equal(registry.current_audit_receipt.sha256, sha256(receiptBytes));
assert.equal(registry.current_audit_receipt.audit_id, receipt.audit_id);
assert.equal(registry.generated_at, receipt.checked_at_finished);
assert.equal(registry.current_audit_receipt.checked_at_started, receipt.checked_at_started);
assert.equal(registry.current_audit_receipt.checked_at_finished, receipt.checked_at_finished);
assert.deepEqual(stableJson(registry.current_audit_receipt.source_method), stableJson(receipt.source_method));
assert.equal(receipt.schema_name, 'federated-hosted-reader-navigation-audit');
assert.equal(receipt.schema_version, '1.0.0');
assert.equal(receipt.source_method.browser_used, false);
assert.equal(receipt.source_method.selection_version, FEDERATED_SELECTION_VERSION);
assert.equal(receipt.source_method.central_program_origin, CENTRAL_PROGRAM_ORIGIN);
assert.equal(receipt.source_manifest.path, manifestPath);
assert.ok(!Number.isNaN(Date.parse(receipt.checked_at_started)));
assert.ok(!Number.isNaN(Date.parse(receipt.checked_at_finished)));
assert.ok(Date.parse(receipt.checked_at_finished) >= Date.parse(receipt.checked_at_started));

const surfaces = extractFederatedHostedHtmlSurfaces(manifest);
const semanticSha256 = sha256(stableJsonBytes(federatedSurfaceProjection(surfaces)));
assert.equal(registry.source_manifest.semantic_projection_sha256, semanticSha256);
assert.equal(receipt.source_manifest.semantic_projection_sha256, semanticSha256);
assert.equal(new Set(surfaces.map((row) => row.url)).size, surfaces.length);
assert.equal(new Set(registry.rows.map((row) => row.url)).size, registry.rows.length);
assert.equal(new Set(receipt.observations.map((row) => row.url)).size, receipt.observations.length);
assert.deepEqual(registry.rows.map((row) => row.url).sort(), surfaces.map((row) => row.url).sort());
assert.deepEqual(receipt.observations.map((row) => row.url).sort(), surfaces.map((row) => row.url).sort());

const registryByUrl = new Map(registry.rows.map((row) => [row.url, row]));
const receiptByUrl = new Map(receipt.observations.map((row) => [row.url, row]));
for (const surface of surfaces) {
  const row = registryByUrl.get(surface.url);
  const observation = receiptByUrl.get(surface.url);
  assert.ok(row && observation);
  assert.equal(row.surface_id, `fhr-${sha256(Buffer.from(surface.url, 'utf8')).slice(0, 16)}`);
  assert.deepEqual(row.course_ids, surface.course_ids);
  assert.deepEqual(row.interface_locales, surface.interface_locales);
  assert.deepEqual(row.content_languages, surface.content_languages);
  assert.deepEqual(row.manifest_bindings, surface.manifest_bindings);
  assert.deepEqual(row.authoritative_original_urls, surface.authoritative_original_urls);
  assert.deepEqual(row.custodian, inferCustodian(surface.url));
  assert.deepEqual(row.associated_program_repositories, surface.program_repository_urls.map((repositoryUrl) => {
    const parsed = new URL(repositoryUrl);
    const [owner, repository] = parsed.pathname.split('/').filter(Boolean);
    return { owner, repository, repository_url: repositoryUrl };
  }));
  assert.deepEqual(row.http_observation, observation.http_observation);
  assert.deepEqual(row.backlink_targets_observed, observation.navigation_observation.central_program_backlink_targets);
  assert.deepEqual(row.contents_or_start_observation, {
    observed: observation.navigation_observation.contents_or_start_observed,
    targets: observation.navigation_observation.contents_or_start_targets,
    landing_path_is_root_or_index: observation.navigation_observation.landing_path_is_root_or_index,
    anchor_count: observation.navigation_observation.anchor_count,
    same_site_anchor_count: observation.navigation_observation.same_site_anchor_count,
  });
  assert.equal(row.checked_at, receipt.checked_at_finished);
  assert.equal(row.source_method, receipt.source_method.kind);
  assert.equal(row.central_navigation_validated, false);
  assert.equal(row.validation_scope, 'federated-observation-only');
  assert.ok(!row.url.startsWith(CENTRAL_PROGRAM_ORIGIN));
  assert.equal(row.http_observation.requested_url, row.url);
  assert.equal(row.http_observation.status, 200);
  assert.ok(Number.isInteger(row.http_observation.bytes) && row.http_observation.bytes > 0);
  assert.match(row.http_observation.sha256, /^[0-9a-f]{64}$/);
  assert.ok(Number.isInteger(row.contents_or_start_observation.anchor_count));
  assert.ok(Number.isInteger(row.contents_or_start_observation.same_site_anchor_count));
  assert.ok(row.contents_or_start_observation.same_site_anchor_count <= row.contents_or_start_observation.anchor_count);
  const expectedState = row.http_observation.status === 200 && row.backlink_targets_observed.length > 0
    ? 'verified' : 'remediation-required';
  assert.equal(row.state, expectedState);
  assert.equal(observation.state, expectedState);
  assert.equal(row.remediation, observation.remediation);
  if (expectedState === 'verified') assert.equal(row.remediation, null);
  else assert.match(row.remediation, /Add a prominent clickable link/);
  for (const backlink of row.backlink_targets_observed) {
    assert.ok(backlink.href.startsWith(CENTRAL_PROGRAM_ORIGIN));
    assert.ok(row.required_central_return_targets.includes(backlink.href));
  }
  const expectedTargets = [...new Set(surface.manifest_bindings.flatMap((binding) => [
    `${CENTRAL_PROGRAM_ORIGIN}${binding.interface_locale}/`,
    `${CENTRAL_PROGRAM_ORIGIN}${binding.interface_locale}/#course-${binding.course_id}`,
  ]))].sort();
  assert.deepEqual(row.required_central_return_targets, expectedTargets);
  for (const binding of surface.manifest_bindings) {
    const projection = manifest.courses[binding.course_id][binding.interface_locale];
    const container = projection[binding.section];
    const resources = Array.isArray(container) ? container : container.resources;
    const resource = resources[binding.resource_index];
    assert.equal(resource.url, row.url);
    assert.equal(resource.access_role, 'hosted-reader');
    assert.equal(resource.hosted_navigation_overlay, null,
      `${binding.course_id}/${binding.interface_locale} off-origin reader must not claim the central overlay`);
  }
}

const calculatedSummary = {
  central_navigation_validated: registry.rows.filter((row) => row.central_navigation_validated).length,
  http_200: registry.rows.filter((row) => row.http_observation.status === 200).length,
  remediation_required: registry.rows.filter((row) => row.state === 'remediation-required').length,
  surfaces: registry.rows.length,
  verified: registry.rows.filter((row) => row.state === 'verified').length,
};
assert.deepEqual(registry.summary, calculatedSummary);
assert.deepEqual(receipt.summary, {
  expected_surfaces: surfaces.length,
  http_200: calculatedSummary.http_200,
  observed_surfaces: surfaces.length,
  remediation_required: calculatedSummary.remediation_required,
  verified: calculatedSummary.verified,
});
assert.equal(calculatedSummary.surfaces, 27);
assert.equal(calculatedSummary.http_200, 27);
assert.equal(calculatedSummary.verified, 3);
assert.equal(calculatedSummary.remediation_required, 24);
assert.equal(calculatedSummary.central_navigation_validated, 0);

assert.equal(centralNavigation.site_origin, CENTRAL_PROGRAM_ORIGIN);
for (const reader of centralNavigation.readers ?? []) {
  assert.ok(reader.public_root.startsWith(CENTRAL_PROGRAM_ORIGIN),
    `${reader.course_id}/${reader.locale} central reader must remain on the central origin`);
  assert.ok(!registryByUrl.has(reader.public_root));
}

const currentManifestSha256 = sha256(manifestBytes);
const currentManifestByteIdentity = receipt.source_manifest.bytes === manifestBytes.length
  && receipt.source_manifest.sha256 === currentManifestSha256;
console.log(JSON.stringify({
  status: 'pass',
  manifest: {
    path: manifestPath,
    bytes: manifestBytes.length,
    sha256: currentManifestSha256,
    semantic_projection_sha256: semanticSha256,
    dated_audit_byte_identity_current: currentManifestByteIdentity,
  },
  registry: { path: registryPath, bytes: registryBytes.length, sha256: sha256(registryBytes) },
  receipt: { path: receiptPath, bytes: receiptBytes.length, sha256: sha256(receiptBytes), audit_id: receipt.audit_id },
  summary: calculatedSummary,
  network_requests_during_validation: 0,
}));
