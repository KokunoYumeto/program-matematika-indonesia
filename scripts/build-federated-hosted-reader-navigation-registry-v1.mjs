import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  CENTRAL_PROGRAM_ORIGIN,
  FEDERATED_SELECTION_VERSION,
  extractFederatedHostedHtmlSurfaces,
  federatedSurfaceProjection,
  sha256,
  stableJsonBytes,
} from './federated-hosted-reader-navigation-lib-v1.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const manifestPath = 'docs/interface/learner-access-manifest.json';
const receiptPath = 'docs/interface/evidence/federated-hosted-reader-navigation-audit-20260906.json';
const manifestBytes = await readFile(resolve(root, manifestPath));
const receiptBytes = await readFile(resolve(root, receiptPath));
const manifest = JSON.parse(manifestBytes);
const receipt = JSON.parse(receiptBytes);
const supportedInterfaceLocales = [...new Set(manifest.supported_interface_locales ?? [])].sort();
assert.ok(supportedInterfaceLocales.length > 0, 'The interface locale registry is empty.');
assert.equal(receipt.schema_version, '1.1.0', 'The universal navigation registry requires a v1.1 live audit receipt.');
const surfaces = extractFederatedHostedHtmlSurfaces(manifest);
const semanticSha256 = sha256(stableJsonBytes(federatedSurfaceProjection(surfaces)));
assert.equal(semanticSha256, receipt.source_manifest.semantic_projection_sha256,
  'The audited federated URL/binding projection changed; run a new bounded live audit before rebuilding the registry.');
const observations = new Map(receipt.observations.map((row) => [row.url, row]));
assert.equal(observations.size, surfaces.length);

const rows = surfaces.map((surface) => {
  const observation = observations.get(surface.url);
  assert.ok(observation, `Audit receipt is missing ${surface.url}`);
  const requiredTargets = [...new Set(surface.course_ids.flatMap((courseId) =>
    supportedInterfaceLocales.map((locale) =>
      `${CENTRAL_PROGRAM_ORIGIN}${locale}/#course-${courseId}`)))].sort();
  const observedTargets = new Set(
    observation.navigation_observation.central_program_backlink_targets.map(({ href }) => href),
  );
  const missingCentralTargets = requiredTargets.filter((target) => !observedTargets.has(target));
  const state = observation.http_observation.status === 200
    && observation.navigation_observation.navigation_marker_count === 1
    && missingCentralTargets.length === 0
    && observation.navigation_observation.missing_authoritative_original_targets.length === 0
    ? 'verified' : 'remediation-required';
  return {
    surface_id: `fhr-${sha256(Buffer.from(surface.url, 'utf8')).slice(0, 16)}`,
    course_ids: surface.course_ids,
    interface_locales: supportedInterfaceLocales,
    content_languages: surface.content_languages,
    url: surface.url,
    custodian: observation.custodian,
    associated_program_repositories: surface.program_repository_urls.map((repositoryUrl) => {
      const parsed = new URL(repositoryUrl);
      const [owner, repository] = parsed.pathname.split('/').filter(Boolean);
      return { owner, repository, repository_url: repositoryUrl };
    }),
    manifest_bindings: surface.manifest_bindings,
    authoritative_original_urls: surface.authoritative_original_urls,
    required_central_return_targets: requiredTargets,
    required_authoritative_original_targets: observation.navigation_observation.required_authoritative_original_targets,
    missing_central_return_targets: missingCentralTargets,
    missing_authoritative_original_targets: observation.navigation_observation.missing_authoritative_original_targets,
    navigation_marker_count: observation.navigation_observation.navigation_marker_count,
    http_observation: observation.http_observation,
    backlink_targets_observed: observation.navigation_observation.central_program_backlink_targets,
    contents_or_start_observation: {
      observed: observation.navigation_observation.contents_or_start_observed,
      targets: observation.navigation_observation.contents_or_start_targets,
      landing_path_is_root_or_index: observation.navigation_observation.landing_path_is_root_or_index,
      anchor_count: observation.navigation_observation.anchor_count,
      same_site_anchor_count: observation.navigation_observation.same_site_anchor_count,
    },
    state,
    remediation: state === 'verified' ? null : (
      observation.remediation
      ?? 'Add the missing central-language course and authoritative-original links.'
    ),
    checked_at: receipt.checked_at_finished,
    source_method: receipt.source_method.kind,
    central_navigation_validated: state === 'verified',
    validation_scope: 'federated-public-navigation-contract',
  };
});

const registry = {
  schema_name: 'federated-hosted-reader-navigation-registry',
  schema_version: '1.1.0',
  generated_at: receipt.checked_at_finished,
  authority_note: 'Current presentation/access registry for program-controlled hosted HTML surfaces outside the central Pages origin. It does not claim that remediation-required readers have a program return link, and it never replaces authoritative-original source bindings.',
  central_program_origin: CENTRAL_PROGRAM_ORIGIN,
  source_manifest: {
    path: manifestPath,
    semantic_projection_sha256: semanticSha256,
    selection_version: FEDERATED_SELECTION_VERSION,
  },
  current_audit_receipt: {
    path: receiptPath,
    bytes: receiptBytes.length,
    sha256: sha256(receiptBytes),
    audit_id: receipt.audit_id,
    checked_at_started: receipt.checked_at_started,
    checked_at_finished: receipt.checked_at_finished,
    source_method: receipt.source_method,
  },
  navigation_contract: receipt.navigation_contract,
  policy: {
    universal_scope: 'Apply the same hosted-copy plus prominent authoritative-original plus reciprocal central-program navigation contract to every current and future course and language namespace.',
    truthful_state: 'A surface is verified only when the dated response is HTTP 200, contains exactly one idempotent navigation landmark, and exposes every required central course and authoritative-original link. HTTP availability alone is insufficient.',
    external_scope: 'These off-origin surfaces are validated through the federated public-navigation contract and remain distinct from the central-reader byte overlay.',
    remediation_rule: 'A remediation-required row stays explicit until a new dated audit proves the complete required link set.',
    no_live_build_dependency: 'Normal builds and offline tests consume this frozen receipt; they do not fetch the network.',
    authoritative_original_separation: 'Hosted-reader rows and authoritative-original URLs remain distinct typed relations even when both are available for one course.',
  },
  summary: {
    surfaces: rows.length,
    http_200: rows.filter((row) => row.http_observation.status === 200).length,
    verified: rows.filter((row) => row.state === 'verified').length,
    remediation_required: rows.filter((row) => row.state === 'remediation-required').length,
    central_navigation_validated: rows.filter((row) => row.central_navigation_validated).length,
  },
  rows,
};

process.stdout.write(stableJsonBytes(registry));
