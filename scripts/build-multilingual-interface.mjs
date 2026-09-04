import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { courses as canonicalCourses } from '../docs/courses.js';
import { syncReaderActions, readerActionInput } from './interface-reader-actions.mjs';
import { syncFinalEditions, finalEditionInput } from './interface-final-editions.mjs';
import { syncCapabilityTools, capabilityInput } from './interface-capability-tools.mjs';
import { supportedLocales, interfaceCopy, topicCopy, siteOrigin, englishBindingExceptions } from '../docs/interface/locales.js';
import { supplementalReaders } from '../docs/interface/supplemental-readers.js';

const interfaceRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
await syncReaderActions(interfaceRoot, canonicalCourses.map((course) => course.id));
await syncFinalEditions(interfaceRoot, canonicalCourses.map((course) => course.id));
const capabilityFiles = await syncCapabilityTools(interfaceRoot, canonicalCourses.map((course) => course.id));
const { interfaceCourses, interfaceTopics, coursePresentation, renderCourseCard, escapeMarkup, resourceBindings } = await import('../docs/interface/view.js');
const read = (path) => readFile(resolve(interfaceRoot, path), 'utf8');
const css = await read('docs/interface/styles.css');
const stripExports = (code) => code.replace(/^export (const|function) /gm, '$1 ');
const stripImports = (code) => code.replace(/^import[\s\S]*?from ['"][^'"]+['"];\r?\n/gm, '');
const capabilityRuntime = (await read('docs/interface/capability-tools.js'))
  // The file inventory is build evidence, not runtime state. It remains hashed
  // in the build receipt but must not consume the bounded offline payload.
  .replace(/^export const capabilityToolFiles = .*;\r?\n/m, '');
const sources = [
  // Carry the effective catalog once in the offline payload; native inputs are
  // still hash-bound below. No course source or backend is changed.
  'const authorityCourses = ' + JSON.stringify(interfaceCourses) + ';\nconst topics = ' + JSON.stringify(interfaceTopics) + ';\nconst materializeLiveCourses = rows => rows;',
  await read('docs/learner-delivery.js'), await read('docs/learner-tools.js'),
  await read('docs/learner-state.js'), await read('docs/interface/locales.js'), await read('docs/interface/reader-actions.js'), await read('docs/interface/final-editions.js'), capabilityRuntime, await read('docs/interface/supplemental-readers.js'), await read('docs/interface/original-sources.js'), await read('docs/interface/view.js'), await read('docs/interface/app.js'),
];
const inlineScript = sources.map((code) => stripExports(stripImports(code))).join('\n').replace(/<\/script/gi, '<\\/script');
if (/^\s*(import|export)\s/m.test(inlineScript)) throw new Error('Unresolved module dependency in offline map');

function renderDocument(locale, offline, paired = false) {
  const t = interfaceCopy[locale], esc = escapeMarkup;
  const languageLinks = supportedLocales.map((code) => {
    const href = paired ? '../' + code + '/learning-map-paired.html' : offline ? siteOrigin + code + '/' : '../' + code + '/';
    return '<a data-locale-link="' + code + '" data-locale-base="' + href + '" href="' + href + '" lang="' + code + '" hreflang="' + code + '"' + (code === locale ? ' aria-current="page"' : '') + '>' + (code === 'id' ? 'Bahasa Indonesia' : 'English') + '</a>';
  }).join('');
  const options = interfaceCourses.map((course) => '<option value="' + course.id + '">' + course.id + ' — ' + esc(coursePresentation(course, locale).title) + '</option>').join('');
  const claimForm = (kind) => '<div class="claim-form"><label for="' + kind + '-course">' + t[kind] + '</label><select id="' + kind + '-course">' + options + '</select><button id="add-' + kind + '" type="button">' + t.add + '</button></div>';
  const canonical = siteOrigin + locale + '/';
  return '<!doctype html>\n<html lang="' + locale + '">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    + '<title>' + esc(t.title) + '</title>\n<meta name="description" content="' + esc(t.description) + '">\n<meta name="theme-color" content="#15302e">\n'
    + '<link rel="canonical" href="' + canonical + '">\n'
    + supportedLocales.map((code) => '<link rel="alternate" hreflang="' + code + '" href="' + siteOrigin + code + '/">').join('\n')
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
    + '<label>' + t.topic + '<select id="topic"><option value="all">' + t.allTopics + '</option>' + interfaceTopics.map((topic, i) => '<option value="' + i + '">' + esc(locale === 'id' ? topic : topicCopy[topic]) + '</option>').join('') + '</select></label>'
    + '<label>' + t.level + '<select id="level"><option value="all">' + t.allLevels + '</option>' + Object.entries(t.levels).map(([key, value]) => '<option value="' + key + '">' + key + ' · ' + value + '</option>').join('') + '</select></label>'
    + '<label>' + t.filter + '<select id="show"><option value="all">' + t.all + '</option><option value="eligible">' + t.eligible + '</option><option value="completed">' + t.completed + '</option><option value="offline">' + t.offline + '</option></select></label></div>'
    + '<div class="filter-footer js-only"><p id="result-count" role="status" aria-live="polite" tabindex="-1"></p><button id="reset-filters" type="button">' + t.clear + '</button></div>'
    + '<p id="empty-state" hidden>' + t.none + '</p><div class="course-grid" id="course-grid">' + interfaceCourses.map((c) => renderCourseCard(c, locale)).join('\n') + '</div></section>'
    + '<section id="about"><h2>' + t.about + '</h2><p>' + t.aboutText + '</p><p class="footnote">' + t.bindingNote + '</p>'
    + (locale === 'en' ? '<details><summary>English resource-binding exceptions</summary><p>These are missing link bindings, not a claim that Indonesian translation is unfinished. English upstream spines do not include the program’s original Indonesian supplements.</p><ul>' + Object.entries(englishBindingExceptions).map(([id, note]) => '<li><a href="#course-' + id + '">' + id + '</a> — ' + esc(note) + '</li>').join('') + '</ul></details>' : '')
    + '</section></main><footer><nav><a href="' + siteOrigin + 'backend/index.html">' + t.sharedBackend + '</a><a href="' + siteOrigin + '">' + t.legacy + '</a><a href="https://github.com/KokunoYumeto/program-matematika-indonesia">GitHub</a></nav><p>' + t.footer + '</p></footer>'
    + (offline ? '<script>\n' + inlineScript + '\n</script>' : '<script type="module" src="../interface/app.js"></script>') + '\n</body>\n</html>\n';
}
const outputFiles = [];
for (const locale of supportedLocales) {
  await mkdir(resolve(interfaceRoot, 'docs', locale), { recursive: true });
  for (const [file, offline, paired] of [['index.html', false, false], ['learning-map.html', true, false], ['learning-map-paired.html', true, true]]) {
    const relative = 'docs/' + locale + '/' + file;
    const bytes = Buffer.from(renderDocument(locale, offline, paired));
    await writeFile(resolve(interfaceRoot, relative), bytes);
    outputFiles.push({ path: relative, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') });
  }
}
const receipt = {
  schema: 'multilingual-interface-build/v1', locales: supportedLocales, canonicalCourseCount: interfaceCourses.length,
  canonicalEdgeCount: interfaceCourses.reduce((n, c) => n + c.prerequisites.length, 0),
  inputs: await Promise.all(['docs/interface/supplemental-readers.js', ...new Set(supplementalReaders.map(row=>row.evidenceFile)), 'docs/courses.js', 'docs/live-course-publications.js', 'docs/learner-state.js', 'docs/learner-delivery.js', 'docs/learner-tools.js', readerActionInput, finalEditionInput, capabilityInput, 'docs/interface/capability-tools.js', 'scripts/interface-capability-tools.mjs', ...capabilityFiles.map(f=>f.path), 'docs/interface/final-editions.js', 'scripts/interface-final-editions.mjs', 'docs/interface/reader-actions.js', 'docs/interface/locales.js', 'docs/interface/view.js', 'docs/interface/app.js', 'docs/interface/styles.css', 'scripts/build-multilingual-interface.mjs', 'scripts/interface-reader-actions.mjs'].map(async (path) => {
    const bytes = await readFile(resolve(interfaceRoot, path));
    return { path, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') };
  })),
  outputs: outputFiles,
  resourceBindingScope: 'Presentation/resource URLs only; no corpus or backend mutation.',
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
