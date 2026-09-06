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
const manifestBytes = await readFile(resolve(root, manifestPath));
const manifest = JSON.parse(manifestBytes);
const surfaces = extractFederatedHostedHtmlSurfaces(manifest);
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
  const responseUrl = new URL(response.url || surface.url);
  const sameSiteAnchorCount = anchors.filter((anchor) => {
    try { return new URL(anchor.href).origin === responseUrl.origin; } catch { return false; }
  }).length;
  const state = response.status === 200 && backlinks.length > 0 ? 'verified' : 'remediation-required';
  return {
    url: surface.url,
    course_ids: surface.course_ids,
    interface_locales: surface.interface_locales,
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
      central_program_backlink_targets: backlinks,
      contents_or_start_targets: startLinks,
      contents_or_start_observed: startLinks.length > 0,
    },
    state,
    remediation: state === 'verified'
      ? null
      : 'Add a prominent clickable link from the hosted reader to the matching central course anchor or language-program root.',
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
  schema_version: '1.0.0',
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
