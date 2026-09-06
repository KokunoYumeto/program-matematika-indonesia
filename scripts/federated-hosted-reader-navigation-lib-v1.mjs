import { createHash } from 'node:crypto';

export const CENTRAL_PROGRAM_ORIGIN = 'https://kokunoyumeto.github.io/program-matematika-indonesia/';
export const FEDERATED_SELECTION_VERSION = 'federated-hosted-html-selection-v1';

export function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

export function stableJson(value) {
  if (Array.isArray(value)) return value.map(stableJson);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableJson(value[key])]));
  }
  return value;
}

export function stableJsonBytes(value) {
  return Buffer.from(`${JSON.stringify(stableJson(value), null, 2)}\n`, 'utf8');
}

function resourceArrays(projection) {
  const arrays = [];
  for (const [section, value] of Object.entries(projection)) {
    if (Array.isArray(value)) arrays.push([section, value]);
    else if (value && Array.isArray(value.resources)) arrays.push([section, value.resources]);
  }
  return arrays;
}

function isDefinitelyNonHtmlUrl(url) {
  const parsed = new URL(url);
  const decoded = decodeURIComponent(parsed.pathname).toLowerCase();
  return /\.(?:pdf|epub|zip|tar|tgz|gz|7z|docx?|xlsx?|pptx?)(?:\/content)?$/.test(decoded);
}

export function isFederatedHostedHtmlResource(resource) {
  if (!resource || resource.access_role !== 'hosted-reader') return false;
  if (!['program-edition', 'program-mirror', 'program-original'].includes(resource.authority_role)) return false;
  if (!['html', 'reader'].includes(String(resource.media_type).toLowerCase())) return false;
  let parsed;
  try { parsed = new URL(resource.url); } catch { return false; }
  if (!['http:', 'https:'].includes(parsed.protocol)) return false;
  if (parsed.href.startsWith(CENTRAL_PROGRAM_ORIGIN)) return false;
  if (isDefinitelyNonHtmlUrl(parsed.href)) return false;
  return true;
}

export function authoritativeOriginalUrls(projection) {
  return (projection.authoritative_original?.resources ?? [])
    .filter((row) => row?.access_role === 'authoritative-original' && typeof row.url === 'string')
    .map((row) => row.url);
}

export function programRepositoryUrls(projection) {
  return resourceArrays(projection)
    .flatMap(([, resources]) => resources)
    .filter((row) => row?.access_role === 'repository' && typeof row.url === 'string')
    .map((row) => row.url)
    .filter((url) => {
      try { return new URL(url).hostname === 'github.com'; } catch { return false; }
    });
}

export function extractFederatedHostedHtmlSurfaces(manifest) {
  const grouped = new Map();
  for (const [courseId, locales] of Object.entries(manifest.courses ?? {})) {
    for (const [locale, projection] of Object.entries(locales ?? {})) {
      const originals = authoritativeOriginalUrls(projection);
      const repositories = programRepositoryUrls(projection);
      for (const [section, resources] of resourceArrays(projection)) {
        resources.forEach((resource, index) => {
          if (!isFederatedHostedHtmlResource(resource)) return;
          const url = new URL(resource.url).href;
          if (!grouped.has(url)) grouped.set(url, {
            url,
            manifest_bindings: [],
            authoritative_original_urls: new Set(),
            program_repository_urls: new Set(),
          });
          const row = grouped.get(url);
          row.manifest_bindings.push({
            course_id: courseId,
            interface_locale: locale,
            section,
            resource_index: index,
            access_role: resource.access_role,
            authority_role: resource.authority_role,
            relation_to_source: resource.relation_to_source,
            content_language: resource.content_language,
            media_type: resource.media_type,
          });
          for (const original of originals) row.authoritative_original_urls.add(original);
          for (const repository of repositories) row.program_repository_urls.add(repository);
        });
      }
    }
  }
  return [...grouped.values()]
    .map((row) => ({
      url: row.url,
      course_ids: [...new Set(row.manifest_bindings.map((binding) => binding.course_id))].sort(),
      interface_locales: [...new Set(row.manifest_bindings.map((binding) => binding.interface_locale))].sort(),
      content_languages: [...new Set(row.manifest_bindings.map((binding) => binding.content_language))].sort(),
      manifest_bindings: row.manifest_bindings.sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b))),
      authoritative_original_urls: [...row.authoritative_original_urls].sort(),
      program_repository_urls: [...row.program_repository_urls].sort(),
    }))
    .sort((a, b) => a.url.localeCompare(b.url));
}

export function federatedSurfaceProjection(surfaces) {
  return surfaces.map((row) => ({
    url: row.url,
    course_ids: row.course_ids,
    interface_locales: row.interface_locales,
    content_languages: row.content_languages,
    manifest_bindings: row.manifest_bindings,
    authoritative_original_urls: row.authoritative_original_urls,
  }));
}

export function inferCustodian(url) {
  const parsed = new URL(url);
  if (parsed.hostname === 'kokunoyumeto.github.io') {
    const repository = parsed.pathname.split('/').filter(Boolean)[0];
    return {
      provider: 'github-pages',
      owner: 'KokunoYumeto',
      repository,
      repository_url: `https://github.com/KokunoYumeto/${repository}`,
    };
  }
  if (parsed.hostname === 'zenodo.org') {
    const recordMatch = parsed.pathname.match(/\/(?:api\/)?records\/(\d+)/);
    return {
      provider: 'zenodo',
      owner: null,
      repository: null,
      record_id: recordMatch?.[1] ?? null,
      record_url: recordMatch ? `https://zenodo.org/records/${recordMatch[1]}` : null,
    };
  }
  return { provider: parsed.hostname, owner: null, repository: null };
}

export function normalizeAnchorTargets(html, baseUrl) {
  const targets = [];
  const anchorPattern = /<a\b[^>]*?href\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))[^>]*>([\s\S]*?)<\/a\s*>/gi;
  for (const match of html.matchAll(anchorPattern)) {
    const href = match[1] ?? match[2] ?? match[3] ?? '';
    if (!href || /^(?:javascript|mailto|tel):/i.test(href)) continue;
    let resolved;
    try { resolved = new URL(href.replaceAll('&amp;', '&'), baseUrl).href; } catch { continue; }
    const label = match[4]
      .replace(/<[^>]+>/g, ' ')
      .replace(/&nbsp;|&#160;/gi, ' ')
      .replace(/&amp;/gi, '&')
      .replace(/\s+/g, ' ')
      .trim();
    targets.push({ href: resolved, label });
  }
  return targets;
}

export function centralBacklinks(anchors) {
  return [...new Map(anchors
    .filter((anchor) => anchor.href.startsWith(CENTRAL_PROGRAM_ORIGIN))
    .map((anchor) => [anchor.href, anchor])).values()]
    .sort((a, b) => a.href.localeCompare(b.href));
}

export function contentsOrStartLinks(anchors, pageUrl) {
  const page = new URL(pageUrl);
  const pageRecord = page.pathname.match(/\/(?:api\/)?records\/(\d+)/)?.[1] ?? null;
  const pageRepository = page.hostname === 'kokunoyumeto.github.io'
    ? page.pathname.split('/').filter(Boolean)[0] ?? null
    : null;
  const navigationOnly = /^(?:skip to main content|langsung ke isi utama|lewati ke isi utama|english|bahasa indonesia|source|sources|repository|github|license|licence|lisensi|download|unduh)$/i;
  const nonHtmlAsset = /\.(?:pdf|epub|zip|tar|tgz|gz|7z|docx?|xlsx?|pptx?|css|js|json|xml|png|jpe?g|gif|svg|webp|woff2?|ttf)(?:$|[?#])/i;
  const pageWithoutHash = `${page.origin}${page.pathname}${page.search}`;
  return [...new Map(anchors.filter((anchor) => {
    let target;
    try { target = new URL(anchor.href); } catch { return false; }
    if (target.origin !== page.origin) return false;
    if (target.href.startsWith(CENTRAL_PROGRAM_ORIGIN)) return false;
    if (pageRepository && target.pathname.split('/').filter(Boolean)[0] !== pageRepository) return false;
    const targetRecord = target.pathname.match(/\/(?:api\/)?records\/(\d+)/)?.[1] ?? null;
    if (pageRecord && targetRecord !== pageRecord) return false;
    if (!anchor.label || navigationOnly.test(anchor.label) || nonHtmlAsset.test(target.pathname)) return false;
    const targetWithoutHash = `${target.origin}${target.pathname}${target.search}`;
    if (targetWithoutHash !== pageWithoutHash) return true;
    return Boolean(target.hash && !/^#(?:main-content|quarto-document-content|top|navigation|nav)$/i.test(target.hash));
  }).map((anchor) => [anchor.href, anchor])).values()]
    .sort((a, b) => a.href.localeCompare(b.href))
    .slice(0, 8);
}
