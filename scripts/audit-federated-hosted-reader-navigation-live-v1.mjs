import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  CENTRAL_PROGRAM_ORIGIN,
  FEDERATED_SELECTION_VERSION,
  centralBacklinks,
  contentsOrStartLinks,
  extractFederatedHostedHtmlSurfaces,
  federatedSurfaceProjection,
  inferCustodian,
  normalizeAnchorTargets,
  sha256,
  stableJsonBytes,
} from './federated-hosted-reader-navigation-lib-v1.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const manifestPath = 'docs/interface/learner-access-manifest.json';
const contractPath = 'backend/authority/universal-reader-navigation-contract-v1.json';
const [manifestBytes, contractBytes] = await Promise.all([
  readFile(resolve(root, manifestPath)),
  readFile(resolve(root, contractPath)),
]);
const manifest = JSON.parse(manifestBytes);
const contract = JSON.parse(contractBytes);
const surfaces = extractFederatedHostedHtmlSurfaces(manifest);
const supportedInterfaceLocales = [...new Set(manifest.supported_interface_locales ?? [])].sort();
if (supportedInterfaceLocales.length === 0) throw new Error('The interface locale registry is empty.');
const semanticBytes = stableJsonBytes(federatedSurfaceProjection(surfaces));
const startedAt = new Date().toISOString();

async function observe(surface) {
  const response = await fetch(surface.url, {
    redirect: 'follow',
    headers: {
      'user-agent': 'program-matematika-indonesia-federated-navigation-audit/1.0',
      accept: 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.1',
    },
    signal: AbortSignal.timeout(45_000),
  });
  const body = Buffer.from(await response.arrayBuffer());
  const text = body.toString('utf8');
  const anchors = normalizeAnchorTargets(text, response.url || surface.url);
  const backlinks = centralBacklinks(anchors);
  const startLinks = contentsOrStartLinks(anchors, response.url || surface.url);
  const normalizedAnchorTargets = new Set(anchors.map((anchor) => new URL(anchor.href).href));
  const requiredCentralTargets = [...new Set(surface.course_ids.flatMap((courseId) =>
    supportedInterfaceLocales.map((locale) =>
      `${CENTRAL_PROGRAM_ORIGIN}${locale}/#course-${courseId}`)))].sort();
  const requiredOriginalTargets = surface.authoritative_original_urls
    .map((url) => new URL(url).href).sort();
  const normalizedCentralTargets = requiredCentralTargets.map((url) => new URL(url).href);
  const missingCentralTargets = normalizedCentralTargets
    .filter((url) => !normalizedAnchorTargets.has(url));
  const missingOriginalTargets = requiredOriginalTargets
    .filter((url) => !normalizedAnchorTargets.has(url));
  const navigationLandmarks = [...text.matchAll(/<nav\b([^>]*)>([\s\S]*?)<\/nav>/gi)].map((match) => {
    const openingAttributes = match[1] ?? '';
    const landmarkAnchors = normalizeAnchorTargets(match[0], response.url || surface.url);
    const targets = new Set(landmarkAnchors.map((anchor) => new URL(anchor.href).href));
    const accessibleNamePresent = /\baria-label(?:ledby)?\s*=\s*(?:"[^"]+"|'[^']+'|[^\s>]+)/i.test(openingAttributes);
    const marker = openingAttributes.match(/\b(?:id|class|data-[\w:-]+)\s*=\s*(?:"([^"]+)"|'([^']+)'|([^\s>]+))/i);
    return {
      accessible_name_present: accessibleNamePresent,
      marker: marker ? (marker[1] ?? marker[2] ?? marker[3]) : null,
      anchor_count: landmarkAnchors.length,
      has_all_central_targets: normalizedCentralTargets.every((url) => targets.has(url)),
      has_all_authoritative_original_targets: requiredOriginalTargets.every((url) => targets.has(url)),
    };
  });
  const qualifyingNavigationLandmarks = navigationLandmarks.filter((row) =>
    row.accessible_name_present
    && row.has_all_central_targets
    && row.has_all_authoritative_original_targets);
  const navigationMarkerCount = qualifyingNavigationLandmarks.length;
  const responseUrl = new URL(response.url || surface.url);
  const sameSiteAnchorCount = anchors.filter((anchor) => {
    try { return new URL(anchor.href).origin === responseUrl.origin; } catch { return false; }
  }).length;
  const state = response.status === 200
    && navigationMarkerCount === 1
    && missingCentralTargets.length === 0
    && missingOriginalTargets.length === 0
    ? 'verified' : 'remediation-required';
  const remediationParts = [];
  if (response.status !== 200) remediationParts.push(`restore anonymous HTTP 200 access (observed ${response.status})`);
  if (navigationMarkerCount !== 1) remediationParts.push(`expose exactly one accessible navigation landmark containing every required central and authoritative-original target (observed ${navigationMarkerCount})`);
  if (missingCentralTargets.length) remediationParts.push(`add ${missingCentralTargets.length} missing central course link(s)`);
  if (missingOriginalTargets.length) remediationParts.push(`add ${missingOriginalTargets.length} missing authoritative-original link(s)`);
  return {
    url: surface.url,
    course_ids: surface.course_ids,
    interface_locales: supportedInterfaceLocales,
    content_languages: surface.content_languages,
    custodian: inferCustodian(surface.url),
    http_observation: {
      requested_url: surface.url,
      final_url: response.url || surface.url,
      status: response.status,
      content_type: response.headers.get('content-type'),
      bytes: body.length,
      sha256: sha256(body),
    },
    navigation_observation: {
      anchor_count: anchors.length,
      same_site_anchor_count: sameSiteAnchorCount,
      landing_path_is_root_or_index: responseUrl.pathname.endsWith('/') || /\/index\.html?$/i.test(responseUrl.pathname),
      navigation_marker_count: navigationMarkerCount,
      qualifying_navigation_landmarks: qualifyingNavigationLandmarks,
      required_central_course_targets: requiredCentralTargets,
      missing_central_course_targets: missingCentralTargets,
      required_authoritative_original_targets: requiredOriginalTargets,
      missing_authoritative_original_targets: missingOriginalTargets,
      central_program_backlink_targets: backlinks,
      contents_or_start_targets: startLinks,
      contents_or_start_observed: startLinks.length > 0,
    },
    state,
    remediation: state === 'verified'
      ? null
      : `${remediationParts.join('; ')}.`,
  };
}

const observations = [];
for (let offset = 0; offset < surfaces.length; offset += 4) {
  observations.push(...await Promise.all(surfaces.slice(offset, offset + 4).map(observe)));
}
observations.sort((a, b) => a.url.localeCompare(b.url));
const finishedAt = new Date().toISOString();
const summary = {
  expected_surfaces: surfaces.length,
  observed_surfaces: observations.length,
  http_200: observations.filter((row) => row.http_observation.status === 200).length,
  verified: observations.filter((row) => row.state === 'verified').length,
  remediation_required: observations.filter((row) => row.state === 'remediation-required').length,
};

process.stdout.write(stableJsonBytes({
  schema_name: 'federated-hosted-reader-navigation-audit',
  schema_version: '1.1.0',
  audit_id: `federated-navigation-${startedAt.replace(/[-:.TZ]/g, '').slice(0, 14)}Z`,
  checked_at_started: startedAt,
  checked_at_finished: finishedAt,
  source_method: {
    kind: 'bounded-headless-http-html-anchor-audit',
    script: 'scripts/audit-federated-hosted-reader-navigation-live-v1.mjs',
    browser_used: false,
    concurrency: 4,
    timeout_ms_per_request: 45000,
    selection_version: FEDERATED_SELECTION_VERSION,
    central_program_origin: CENTRAL_PROGRAM_ORIGIN,
    conformance_rule: 'http-200-plus-exactly-one-accessible-semantic-navigation-landmark-plus-all-central-course-and-authoritative-original-links; lineage-specific concrete marker is bound by its deterministic tool and publication receipt',
  },
  navigation_contract: {
    path: contractPath,
    bytes: contractBytes.length,
    sha256: sha256(contractBytes),
    schema_version: contract.schema_version,
  },
  source_manifest: {
    path: manifestPath,
    bytes: manifestBytes.length,
    sha256: sha256(manifestBytes),
    semantic_projection_sha256: sha256(semanticBytes),
  },
  summary,
  observations,
}));
