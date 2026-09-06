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
const universalContractPath = 'backend/authority/universal-reader-navigation-contract-v1.json';
const [manifestBytes, registryBytes, centralNavigationBytes, universalContractBytes] = await Promise.all([
  readFile(resolve(root, manifestPath)),
  readFile(resolve(root, registryPath)),
  readFile(resolve(root, centralNavigationPath)),
  readFile(resolve(root, universalContractPath)),
]);
const manifest = JSON.parse(manifestBytes);
const registry = JSON.parse(registryBytes);
const centralNavigation = JSON.parse(centralNavigationBytes);
const universalContract = JSON.parse(universalContractBytes);
const receiptPath = registry.current_audit_receipt.path;
const receiptBytes = await readFile(resolve(root, receiptPath));
const receipt = JSON.parse(receiptBytes);
const supportedInterfaceLocales = [...new Set(manifest.supported_interface_locales ?? [])].sort();
assert.ok(supportedInterfaceLocales.length > 0);

assert.equal(registry.schema_name, 'federated-hosted-reader-navigation-registry');
assert.ok(['1.0.0', '1.1.0'].includes(registry.schema_version));
const universalAudit = registry.schema_version === '1.1.0';
assert.equal(registry.central_program_origin, CENTRAL_PROGRAM_ORIGIN);
assert.equal(universalContract.schema_name, 'universal-reader-navigation-contract');
assert.equal(universalContract.schema_version, '1.1.0');
assert.deepEqual(universalContract.scope.current_language_namespaces, ['en', 'id']);
assert.equal(universalContract.scope.html_documents,
  'every-published-learner-html-document-not-only-the-landing-page');
assert.match(universalContract.html_navigation.absolute_https_links_required,
  /^central-language course anchors and authoritative-original targets must use absolute HTTPS/);
assert.match(universalContract.html_navigation.idempotence_marker, /^one stable lineage-owned marker/);
assert.deepEqual(universalContract.html_navigation.landmark_cardinality, {
  federated_hosted_html: { count: 1, placements: ['prominent-top'] },
  central_program_hosted_html: { count: 2, placements: ['top', 'bottom'] },
});
assert.equal(universalContract.central_interface.json_may_not_be_the_only_learner_entrypoint, true);
assert.equal(universalContract.central_interface.hosted_copy_and_original_source_must_remain_distinct, true);
assert.equal(universalContract.validation_gates.nested_documents,
  'validate-every-published-HTML-document-not-a-single-landing-page-sample');
assert.equal(universalContract.authority_boundaries.public_access_must_not_be_reduced, true);
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
assert.equal(receipt.schema_version, universalAudit ? '1.1.0' : '1.0.0');
if (universalAudit) {
  assert.deepEqual(registry.navigation_contract, receipt.navigation_contract);
  assert.equal(receipt.navigation_contract.path, universalContractPath);
  assert.equal(receipt.navigation_contract.bytes, universalContractBytes.length);
  assert.equal(receipt.navigation_contract.sha256, sha256(universalContractBytes));
  assert.equal(receipt.navigation_contract.schema_version, universalContract.schema_version);
  assert.equal(receipt.source_method.conformance_rule,
    'http-200-plus-exactly-one-accessible-semantic-navigation-landmark-plus-all-central-course-and-authoritative-original-links; lineage-specific concrete marker is bound by its deterministic tool and publication receipt');
}
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
  assert.deepEqual(row.interface_locales, supportedInterfaceLocales);
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
  assert.equal(row.central_navigation_validated, universalAudit ? row.state === 'verified' : false);
  assert.equal(row.validation_scope, universalAudit
    ? 'federated-public-navigation-contract' : 'federated-observation-only');
  assert.ok(!row.url.startsWith(CENTRAL_PROGRAM_ORIGIN));
  assert.equal(row.http_observation.requested_url, row.url);
  assert.equal(row.http_observation.status, 200);
  assert.ok(Number.isInteger(row.http_observation.bytes) && row.http_observation.bytes > 0);
  assert.match(row.http_observation.sha256, /^[0-9a-f]{64}$/);
  assert.ok(Number.isInteger(row.contents_or_start_observation.anchor_count));
  assert.ok(Number.isInteger(row.contents_or_start_observation.same_site_anchor_count));
  assert.ok(row.contents_or_start_observation.same_site_anchor_count <= row.contents_or_start_observation.anchor_count);
  let expectedState;
  if (universalAudit) {
    assert.equal(row.navigation_marker_count, observation.navigation_observation.navigation_marker_count);
    assert.deepEqual(row.required_authoritative_original_targets,
      observation.navigation_observation.required_authoritative_original_targets);
    const observedBacklinks = new Set(
      observation.navigation_observation.central_program_backlink_targets.map(({ href }) => href),
    );
    assert.deepEqual(row.missing_central_return_targets,
      row.required_central_return_targets.filter((target) => !observedBacklinks.has(target)));
    assert.deepEqual(row.missing_authoritative_original_targets,
      observation.navigation_observation.missing_authoritative_original_targets);
    expectedState = row.http_observation.status === 200
      && row.navigation_marker_count === 1
      && row.missing_central_return_targets.length === 0
      && row.missing_authoritative_original_targets.length === 0
      ? 'verified' : 'remediation-required';
  } else {
    expectedState = row.http_observation.status === 200 && row.backlink_targets_observed.length > 0
      ? 'verified' : 'remediation-required';
  }
  assert.equal(row.state, expectedState);
  if (expectedState === 'verified') assert.equal(observation.state, 'verified');
  if (expectedState === 'verified') assert.equal(row.remediation, null);
  else assert.match(row.remediation, universalAudit ? /\.$/ : /Add a prominent clickable link/);
  for (const backlink of row.backlink_targets_observed) {
    assert.ok(backlink.href.startsWith(CENTRAL_PROGRAM_ORIGIN));
    if (!universalAudit) assert.ok(row.required_central_return_targets.includes(backlink.href));
  }
  const expectedTargets = [...new Set(universalAudit
    ? surface.course_ids.flatMap((courseId) => supportedInterfaceLocales.map((locale) =>
      `${CENTRAL_PROGRAM_ORIGIN}${locale}/#course-${courseId}`))
    : surface.manifest_bindings.flatMap((binding) => [
      `${CENTRAL_PROGRAM_ORIGIN}${binding.interface_locale}/`,
      `${CENTRAL_PROGRAM_ORIGIN}${binding.interface_locale}/#course-${binding.course_id}`,
    ]))].sort();
  assert.deepEqual(row.required_central_return_targets, expectedTargets);
  if (universalAudit) {
    const observedBacklinks = new Set(row.backlink_targets_observed.map(({ href }) => href));
    for (const target of expectedTargets) assert.ok(observedBacklinks.has(target));
    assert.deepEqual(row.required_authoritative_original_targets,
      surface.authoritative_original_urls.map((url) => new URL(url).href).sort());
  }
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
assert.equal(calculatedSummary.surfaces, surfaces.length);
assert.ok(calculatedSummary.surfaces > 0);
assert.equal(calculatedSummary.http_200, calculatedSummary.surfaces);
assert.equal(calculatedSummary.verified, universalAudit ? calculatedSummary.surfaces : 3);
assert.equal(calculatedSummary.remediation_required, universalAudit ? 0 : 24);
assert.equal(calculatedSummary.central_navigation_validated, universalAudit ? calculatedSummary.surfaces : 0);

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
