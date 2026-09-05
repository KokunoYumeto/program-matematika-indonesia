import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { courses as canonicalCourses } from '../docs/courses.js';
import { syncReaderActions, readerActionInput } from './interface-reader-actions.mjs';
import { syncFinalEditions, finalEditionInput } from './interface-final-editions.mjs';
import { syncCapabilityTools, capabilityInput, clpCapabilityInput, clpCapabilityValidationInput } from './interface-capability-tools.mjs';
import { supportedLocales, localeMetadata, interfaceCopy, localizedTopic, siteOrigin, englishBindingExceptions } from '../docs/interface/locales.js';
import { supplementalReaders } from '../docs/interface/supplemental-readers.js';

const interfaceRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const docsRoot = resolve(interfaceRoot, 'docs');
const localeRoots = new Map();
for (const locale of supportedLocales) {
  const routeSegment = localeMetadata[locale].routeSegment;
  const localeRoot = resolve(docsRoot, routeSegment);
  if (dirname(localeRoot).toLowerCase() !== docsRoot.toLowerCase()) {
    throw new Error('Locale route escapes or nests outside the docs root: ' + locale);
  }
  const key = localeRoot.toLowerCase();
  if (localeRoots.has(key)) throw new Error('Locale routes collide: ' + localeRoots.get(key) + ' and ' + locale);
  localeRoots.set(key, locale);
}
await syncReaderActions(interfaceRoot, canonicalCourses.map((course) => course.id));
await syncFinalEditions(interfaceRoot, canonicalCourses.map((course) => course.id));
const capabilityFiles = await syncCapabilityTools(interfaceRoot, canonicalCourses.map((course) => course.id));
const centralNavigationContractBytes = await readFile(resolve(interfaceRoot, 'backend/authority/central-reader-navigation-v1.json'));
const centralNavigationOverlayBytes = await readFile(resolve(interfaceRoot, 'backend/authority/central-course-surface-navigation-overlay-v1.json'));
const centralNavigationContract = JSON.parse(centralNavigationContractBytes);
const centralNavigationOverlay = JSON.parse(centralNavigationOverlayBytes);
if (centralNavigationContract.schema !== 'central-reader-navigation-v1' || centralNavigationOverlay.schema !== 'central-course-surface-navigation-overlay-v1' || centralNavigationOverlay.status !== 'pass') {
  throw new Error('Central hosted-surface authority is incomplete');
}
const hostedIdentityDocuments = new Set([
  ...centralNavigationContract.course_surfaces.flatMap(group => group.documents.map(row => group.root + '/' + row.path)),
  ...centralNavigationContract.readers.flatMap(reader => reader.landing_required_paths.map(suffix => reader.root + '/' + (suffix || 'index.html'))),
  ...centralNavigationContract.gateways.map(gateway => gateway.root + '/' + gateway.entry_path),
]);
const hostedSurfaceIdentities = {};
for (const row of centralNavigationOverlay.files) {
  // Interface/generic documents embed this module in their offline forms.
  // Excluding those presentation pages prevents a self-referential hash cycle;
  // only course-scoped learner destinations need runtime source/hosted mapping.
  if (!hostedIdentityDocuments.has(row.document)) continue;
  if (!row.document.startsWith('docs/')) throw new Error('Hosted surface escapes docs: ' + row.document);
  const logical = row.document.slice('docs/'.length);
  const route = logical === 'index.html' ? '' : logical.endsWith('/index.html') ? logical.slice(0, -'index.html'.length) : logical;
  const urls = new Set([new URL(route, siteOrigin).href, new URL(logical, siteOrigin).href]);
  const identity = { sourceBody: row.source_body, hostedSurface: row.hosted_surface };
  for (const url of urls) {
    if (hostedSurfaceIdentities[url] && JSON.stringify(hostedSurfaceIdentities[url]) !== JSON.stringify(identity)) {
      throw new Error('Conflicting hosted-surface identity: ' + url);
    }
    hostedSurfaceIdentities[url] = identity;
  }
}
const overlayDocuments = new Set(centralNavigationOverlay.files.map(row => row.document));
for (const document of hostedIdentityDocuments) {
  if (!overlayDocuments.has(document)) throw new Error('Hosted identity document is absent from the navigation overlay: ' + document);
}
const hostedSurfaceIdentityModulePath = 'docs/interface/hosted-surface-identities.js';
const hostedSurfaceIdentityModuleBytes = Buffer.from(
  '// Generated from the reversible central navigation overlay; do not hand-edit.\n'
  + 'export const hostedSurfaceIdentities = Object.freeze(' + JSON.stringify(hostedSurfaceIdentities) + ');\n',
);
await writeFile(resolve(interfaceRoot, hostedSurfaceIdentityModulePath), hostedSurfaceIdentityModuleBytes);
const centralGatewayResources = centralNavigationContract.gateways.map((gateway) => {
  if (!gateway.root.startsWith('docs/') || gateway.entry_path.includes('..') || gateway.entry_path.startsWith('/')) {
    throw new Error('Unsafe central gateway entry: ' + gateway.course_id);
  }
  const logical = gateway.root.slice('docs/'.length).replace(/\/$/u, '') + '/' + gateway.entry_path;
  const href = new URL(gateway.entry_path === 'index.html' ? logical.slice(0, -'index.html'.length) : logical, siteOrigin).href;
  return {
    courseId: gateway.course_id,
    contentLanguage: centralNavigationContract.interfaces[gateway.locale].language_tag,
    href,
  };
});
if (new Set(centralGatewayResources.map(row => row.courseId + '\0' + row.href)).size !== centralGatewayResources.length) {
  throw new Error('Duplicate central gateway resource');
}
const centralGatewayModulePath = 'docs/interface/central-gateway-resources.js';
const centralGatewayModuleBytes = Buffer.from(
  '// Generated from backend/authority/central-reader-navigation-v1.json; do not hand-edit.\n'
  + 'export const centralGatewayResources = Object.freeze(' + JSON.stringify(centralGatewayResources) + ');\n',
);
await writeFile(resolve(interfaceRoot, centralGatewayModulePath), centralGatewayModuleBytes);
const { interfaceCourses, interfaceTopics, coursePresentation, renderCourseCard, escapeMarkup, resourceBindings, learnerAccessProjection, learnerAccessRoles } = await import('../docs/interface/view.js');
const { capabilityTools: admittedCapabilityTools } = await import('../docs/interface/capability-tools.js');
const read = (path) => readFile(resolve(interfaceRoot, path), 'utf8');
const css = await read('docs/interface/styles.css');
const stripExports = (code) => code.replace(/^export (const|function) /gm, '$1 ');
const stripImports = (code) => code.replace(/^import[\s\S]*?from ['"][^'"]+['"];\r?\n/gm, '');
// Keep the complete admitted objects and file inventory in the hash-bound source,
// but embed only fields consumed by resourceBindings in the offline document.
// This is a lossless runtime projection: online/offline binding equality below
// proves that omitted build-only evidence fields cannot alter learner links.
const capabilityRuntimeTools = admittedCapabilityTools.map((tool) => ({
  courseId: tool.courseId,
  contentLanguage: tool.contentLanguage,
  labelLanguage: tool.labelLanguage ?? tool.contentLanguage,
  href: tool.href,
  label: tool.label,
  limitations: tool.limitations,
  page: { bytes: tool.page.bytes, sha256: tool.page.sha256 },
  scope: tool.scope,
  tool_id: tool.tool_id,
}));
const capabilityRuntime = 'const capabilityTools = ' + JSON.stringify(capabilityRuntimeTools) + ';';
const sources = [
  // Carry the effective catalog once in the offline payload; native inputs are
  // still hash-bound below. No course source or backend is changed.
  'const authorityCourses = ' + JSON.stringify(interfaceCourses) + ';\nconst topics = ' + JSON.stringify(interfaceTopics) + ';\nconst materializeLiveCourses = rows => rows;',
  await read('docs/learner-delivery.js'), await read('docs/learner-tools.js'),
  await read('docs/learner-state.js'), await read('docs/interface/locales.js'), await read('docs/interface/reader-actions.js'), await read('docs/interface/final-editions.js'), capabilityRuntime, await read('docs/interface/supplemental-readers.js'), await read('docs/interface/original-sources.js'), await read(hostedSurfaceIdentityModulePath), await read(centralGatewayModulePath), await read('docs/interface/view.js'), await read('docs/interface/app.js'),
];
const inlineScript = sources.map((code) => stripExports(stripImports(code))).join('\n').replace(/<\/script/gi, '<\\/script');
if (/^\s*(import|export)\s/m.test(inlineScript)) throw new Error('Unresolved module dependency in offline map');

function renderDocument(locale, offline, paired = false) {
  const t = interfaceCopy[locale], esc = escapeMarkup;
  const localeConfig = localeMetadata[locale];
  const languageLinks = supportedLocales.map((code) => {
    const meta = localeMetadata[code];
    const href = paired ? '../' + meta.routeSegment + '/learning-map-paired.html' : offline ? siteOrigin + meta.routeSegment + '/' : '../' + meta.routeSegment + '/';
    return '<a data-locale-link="' + code + '" data-locale-base="' + href + '" href="' + href + '" lang="' + meta.languageTag + '" hreflang="' + meta.languageTag + '"' + (code === locale ? ' aria-current="page"' : '') + '>' + esc(meta.label) + '</a>';
  }).join('');
  const options = interfaceCourses.map((course) => '<option value="' + course.id + '">' + course.id + ' — ' + esc(coursePresentation(course, locale).title) + '</option>').join('');
  const claimForm = (kind) => '<div class="claim-form"><label for="' + kind + '-course">' + t[kind] + '</label><select id="' + kind + '-course">' + options + '</select><button id="add-' + kind + '" type="button">' + t.add + '</button></div>';
  const canonical = siteOrigin + localeMetadata[locale].routeSegment + '/';
  const bindingExceptionSets = { en: englishBindingExceptions };
  const exceptionRows = localeConfig.bindingExceptions ? bindingExceptionSets[localeConfig.bindingExceptions] : null;
  if (localeConfig.bindingExceptions && !exceptionRows) throw new Error('Unknown binding-exception set: ' + localeConfig.bindingExceptions);
  const exceptions = exceptionRows
    ? '<details><summary>' + esc(t.bindingExceptionsTitle) + '</summary><p>' + esc(t.bindingExceptionsText) + '</p><ul>'
      + Object.entries(exceptionRows).map(([id, note]) => '<li><a href="#course-' + id + '">' + id + '</a> — ' + esc(note) + '</li>').join('') + '</ul></details>'
    : '';
  return '<!doctype html>\n<html lang="' + localeConfig.languageTag + '" data-interface-locale="' + locale + '">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    + '<title>' + esc(t.title) + '</title>\n<meta name="description" content="' + esc(t.description) + '">\n<meta name="theme-color" content="#15302e">\n'
    + '<link rel="canonical" href="' + canonical + '">\n'
    + '<link rel="alternate" type="application/json" title="Learner access manifest" href="' + siteOrigin + 'interface/learner-access-manifest.json">\n'
    + supportedLocales.map((code) => '<link rel="alternate" hreflang="' + localeMetadata[code].languageTag + '" href="' + siteOrigin + localeMetadata[code].routeSegment + '/">').join('\n')
    + '\n<link rel="alternate" hreflang="x-default" href="' + siteOrigin + '">\n'
    + '<meta property="og:title" content="' + esc(t.title) + '">\n<meta property="og:description" content="' + esc(t.description) + '">\n'
    + '<meta property="og:type" content="website">\n<meta property="og:url" content="' + canonical + '">\n'
    + '<meta property="og:image" content="' + siteOrigin + 'og.png">\n<meta name="twitter:card" content="summary_large_image">\n'
    + '<meta name="twitter:title" content="' + esc(t.title) + '">\n<meta name="twitter:description" content="' + esc(t.description) + '">\n<meta name="twitter:image" content="' + siteOrigin + 'og.png">\n'
    + (offline ? '<style>\n' + css + '\n</style>' : '<link rel="stylesheet" href="../interface/styles.css">')
    + '\n</head>\n<body>\n<a class="skip-link" href="#katalog">' + t.skip + '</a>'
    + '<header class="site-header"><div class="header-inner"><a class="brand" href="#top">' + esc(t.shortTitle) + '</a>'
    + '<nav class="primary-nav" aria-label="' + t.nav + '"><a href="#katalog">' + t.catalog + '</a><a class="js-only" href="#progress">' + t.progress + '</a><a href="#about">' + t.about + '</a></nav>'
    + '<nav class="locale-switcher" aria-label="' + t.language + '"><span>' + t.language + '</span>' + languageLinks + '</nav></div></header>'
    + '<main id="top"><section class="intro"><h1>' + esc(t.title) + '</h1><p>' + esc(t.description) + '</p></section>'
    + '<div class="offline-bar"><a href="' + (offline ? '#katalog' : 'learning-map.html') + '"' + (offline ? '' : ' download') + '>' + (offline ? t.catalog : t.offlineMap) + '</a><a href="https://doi.org/10.5281/zenodo.22059707">' + t.offlineBundle + '</a></div><p class="footnote">' + t.offlineHelp + '</p>'
    + '<p class="footnote">' + (paired ? t.pairedHelp : t.standaloneHelp) + '</p>'
    + '<details class="progress-panel js-only" id="progress"><summary>' + t.progress + ' — <span id="progress-summary"></span></summary><p>' + t.progressHelp + '</p>'
    + '<div class="progress-controls">' + claimForm('placement') + claimForm('equivalence')
    + '<div class="claim-form"><label for="waiver-target">' + t.target + '</label><select id="waiver-target">' + options + '</select><label for="waiver-prereq">' + t.prerequisite + '</label><select id="waiver-prereq"></select><button id="add-waiver" type="button">' + t.add + '</button></div></div>'
    + '<div id="claims"></div><p id="storage-message" role="status"></p><div class="progress-actions"><button id="export-progress" type="button">' + t.exportProgress + '</button><label>' + t.importProgress + '<input id="import-progress" type="file" accept=".json,application/json"></label><button id="clear-progress" type="button">' + t.resetProgress + '</button></div></details>'
    + '<section id="katalog" aria-labelledby="catalog-title"><h2 id="catalog-title">' + t.catalog + '</h2><p class="no-js-note">' + t.noJs + '</p>'
    + '<div class="filters js-only"><label>' + t.search + '<input type="search" id="search" placeholder="' + esc(t.placeholder) + '" autocomplete="off"></label>'
    + '<label>' + t.topic + '<select id="topic"><option value="all">' + t.allTopics + '</option>' + interfaceTopics.map((topic, i) => '<option value="' + i + '">' + esc(localizedTopic(topic, locale)) + '</option>').join('') + '</select></label>'
    + '<label>' + t.level + '<select id="level"><option value="all">' + t.allLevels + '</option>' + Object.entries(t.levels).map(([key, value]) => '<option value="' + key + '">' + key + ' · ' + value + '</option>').join('') + '</select></label>'
    + '<label>' + t.filter + '<select id="show"><option value="all">' + t.all + '</option><option value="eligible">' + t.eligible + '</option><option value="completed">' + t.completed + '</option><option value="offline">' + t.offline + '</option></select></label></div>'
    + '<div class="filter-footer js-only"><p id="result-count" role="status" aria-live="polite" tabindex="-1"></p><button id="reset-filters" type="button">' + t.clear + '</button></div>'
    + '<p id="empty-state" hidden>' + t.none + '</p><div class="course-grid" id="course-grid">' + interfaceCourses.map((c) => renderCourseCard(c, locale)).join('\n') + '</div></section>'
    + '<section id="about"><h2>' + t.about + '</h2><p>' + t.aboutText + '</p><p class="footnote">' + t.bindingNote + '</p>'
    + exceptions
    + '</section></main><footer><nav><a href="' + siteOrigin + 'backend/index.html">' + t.sharedBackend + '</a><a href="https://kokunoyumeto.github.io/OpenLogic-translations/">' + t.openLogicHub + '</a><a href="' + siteOrigin + '">' + t.legacy + '</a><a href="https://github.com/KokunoYumeto/program-matematika-indonesia">GitHub</a></nav><p>' + t.footer + '</p></footer>'
    + (offline ? '<script>\n' + inlineScript + '\n</script>' : '<script type="module" src="../interface/app.js"></script>') + '\n</body>\n</html>\n';
}
const outputFiles = [{
  path: hostedSurfaceIdentityModulePath,
  bytes: hostedSurfaceIdentityModuleBytes.length,
  sha256: createHash('sha256').update(hostedSurfaceIdentityModuleBytes).digest('hex'),
}, {
  path: centralGatewayModulePath,
  bytes: centralGatewayModuleBytes.length,
  sha256: createHash('sha256').update(centralGatewayModuleBytes).digest('hex'),
}];
for (const locale of supportedLocales) {
  const routeSegment = localeMetadata[locale].routeSegment;
  await mkdir(resolve(docsRoot, routeSegment), { recursive: true });
  for (const [file, offline, paired] of [['index.html', false, false], ['learning-map.html', true, false], ['learning-map-paired.html', true, true]]) {
    const relative = 'docs/' + routeSegment + '/' + file;
    const bytes = Buffer.from(renderDocument(locale, offline, paired));
    await writeFile(resolve(docsRoot, routeSegment, file), bytes);
    outputFiles.push({ path: relative, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') });
  }
}
const rootLocaleStart = '<!-- GENERATED-INTERFACE-LOCALES-START -->';
const rootLocaleEnd = '<!-- GENERATED-INTERFACE-LOCALES-END -->';
const rootIndexPath = resolve(interfaceRoot, 'docs/index.html');
const rootIndexSource = await readFile(rootIndexPath, 'utf8');
const rootLocaleLinks = supportedLocales.map((locale) => {
  const meta = localeMetadata[locale];
  return '      <a href="' + meta.routeSegment + '/" hreflang="' + meta.languageTag + '" lang="' + meta.languageTag
    + '" data-interface-locale="' + locale + '">' + escapeMarkup(meta.label) + '</a>';
}).join('\n');
const rootLocalePattern = new RegExp(rootLocaleStart + '[\\s\\S]*?' + rootLocaleEnd);
if (!rootLocalePattern.test(rootIndexSource)) throw new Error('Root locale chooser markers are missing');
const rootIndexTarget = rootIndexSource.replace(rootLocalePattern, rootLocaleStart + '\n' + rootLocaleLinks + '\n      ' + rootLocaleEnd);
await writeFile(rootIndexPath, rootIndexTarget, 'utf8');
const rootLocaleChooser = {
  path: 'docs/index.html',
  locales: supportedLocales,
  bytes: Buffer.byteLength(rootIndexTarget),
  sha256: createHash('sha256').update(rootIndexTarget).digest('hex'),
};
const learnerAccessManifest = {
  schema_name: 'learner-access-presentation', schema_version: '1.0.0',
  authority_note: 'Presentation sidecar only; canonical edition, rights, provenance, and translation records remain authoritative in the modular backend.',
  locale_route_template: '/{route_segment}/', supported_interface_locales: supportedLocales,
  locale_metadata: localeMetadata,
  access_roles: learnerAccessRoles,
  invariants: [
    'interface_locale_does_not_imply_content_language',
    'authoritative_original_remains_prominent_when_a_hosted_reader_exists',
    'missing_hosted_reader_is_explicit_and_never_fabricated',
    'offline_status_is_evidence_bound',
  ],
  courses: Object.fromEntries(interfaceCourses.map(course => [course.id, Object.fromEntries(supportedLocales.map(locale => [locale, learnerAccessProjection(course, locale)]))])),
};
const learnerAccessManifestBytes = Buffer.from(JSON.stringify(learnerAccessManifest, null, 2) + '\n');
await writeFile(resolve(interfaceRoot, 'docs/interface/learner-access-manifest.json'), learnerAccessManifestBytes);
outputFiles.push({path:'docs/interface/learner-access-manifest.json', bytes:learnerAccessManifestBytes.length, sha256:createHash('sha256').update(learnerAccessManifestBytes).digest('hex')});
const receipt = {
  schema: 'multilingual-interface-build/v1', locales: supportedLocales, canonicalCourseCount: interfaceCourses.length,
  canonicalEdgeCount: interfaceCourses.reduce((n, c) => n + c.prerequisites.length, 0),
  inputs: await Promise.all(['backend/authority/central-reader-navigation-v1.json', 'backend/authority/central-course-surface-navigation-overlay-v1.json', hostedSurfaceIdentityModulePath, centralGatewayModulePath, 'docs/interface/supplemental-readers.js', ...new Set(supplementalReaders.map(row=>row.evidenceFile)), 'docs/courses.js', 'docs/live-course-publications.js', 'docs/learner-state.js', 'docs/learner-delivery.js', 'docs/learner-tools.js', readerActionInput, finalEditionInput, capabilityInput, clpCapabilityInput, clpCapabilityValidationInput, 'docs/interface/capability-tools.js', 'scripts/interface-capability-tools.mjs', ...capabilityFiles.map(f=>f.path), 'docs/interface/final-editions.js', 'scripts/interface-final-editions.mjs', 'docs/interface/reader-actions.js', 'docs/interface/locales.js', 'docs/interface/view.js', 'docs/interface/app.js', 'docs/interface/styles.css', 'scripts/build-multilingual-interface.mjs', 'scripts/interface-reader-actions.mjs'].map(async (path) => {
    const bytes = await readFile(resolve(interfaceRoot, path));
    return { path, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') };
  })),
  outputs: outputFiles,
  rootLocaleChooser,
  resourceBindingScope: 'Presentation/resource URLs only; no corpus or backend mutation.',
  learnerAccessContract: {
    schema: learnerAccessManifest.schema_name + '/' + learnerAccessManifest.schema_version,
    manifest: outputFiles.find(row => row.path === 'docs/interface/learner-access-manifest.json'),
    roles: learnerAccessRoles,
    perLocale: Object.fromEntries(supportedLocales.map(locale => {
      const projections = interfaceCourses.map(course => learnerAccessProjection(course, locale));
      return [locale, {
        availableHostedReaders: projections.filter(row => row.program_hosted_reader.status === 'available').length,
        unavailableHostedReaders: projections.filter(row => row.program_hosted_reader.status === 'not-yet-hosted').length,
        authoritativeOriginals: projections.reduce((count, row) => count + row.authoritative_original.resources.length, 0),
      }];
    })),
  },
  resourceBindings: Object.fromEntries(supportedLocales.map((locale) => [locale, Object.fromEntries(interfaceCourses.map((course) => [course.id, resourceBindings(course, locale)]))])),
};
const originalSourceBytes = await readFile(resolve(interfaceRoot, 'docs/interface/original-sources.js'));
receipt.inputs.push({path:'docs/interface/original-sources.js', bytes:originalSourceBytes.length, sha256:createHash('sha256').update(originalSourceBytes).digest('hex')});
const sourceAccessBytes = await readFile(resolve(interfaceRoot, 'docs/interface/evidence/original-source-access-review.json'));
receipt.inputs.push({path:'docs/interface/evidence/original-source-access-review.json', bytes:sourceAccessBytes.length, sha256:createHash('sha256').update(sourceAccessBytes).digest('hex')});
const a00MirrorEvidenceBytes = await readFile(resolve(interfaceRoot, 'docs/interface/evidence/a00-original-english-mirror.json'));
receipt.inputs.push({path:'docs/interface/evidence/a00-original-english-mirror.json', bytes:a00MirrorEvidenceBytes.length, sha256:createHash('sha256').update(a00MirrorEvidenceBytes).digest('hex')});
const a10MirrorEvidenceBytes = await readFile(resolve(interfaceRoot, 'docs/interface/evidence/a10-original-english-mirror.json'));
receipt.inputs.push({path:'docs/interface/evidence/a10-original-english-mirror.json', bytes:a10MirrorEvidenceBytes.length, sha256:createHash('sha256').update(a10MirrorEvidenceBytes).digest('hex')});
const a20MirrorEvidenceBytes = await readFile(resolve(interfaceRoot, 'docs/interface/evidence/a20-original-english-mirror.json'));
receipt.inputs.push({path:'docs/interface/evidence/a20-original-english-mirror.json', bytes:a20MirrorEvidenceBytes.length, sha256:createHash('sha256').update(a20MirrorEvidenceBytes).digest('hex')});
await writeFile(resolve(interfaceRoot, 'docs/interface/build-receipt.json'), JSON.stringify(receipt, null, 2) + '\n');
console.log(JSON.stringify({ locales: supportedLocales, courses: receipt.canonicalCourseCount, edges: receipt.canonicalEdgeCount, outputs: outputFiles }));
