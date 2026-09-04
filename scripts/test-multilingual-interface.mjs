import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { gzipSync } from 'node:zlib';
import vm from 'node:vm';
import { courses as canonicalCourses } from '../docs/courses.js';
import { interfaceCourses, interfaceTopics, coursePresentation, resourceBindings, renderCourseCard, renderResourceLinks, safeResourceUrl, isOriginalSource, contentLanguageName } from '../docs/interface/view.js';
import { additionalOriginalSources } from '../docs/interface/original-sources.js';
import { supportedLocales, englishResources, englishBindingExceptions, siteOrigin } from '../docs/interface/locales.js';
import { verifiedReaderActions, readerActionSource } from '../docs/interface/reader-actions.js';
import { projectReaderActions, readerActionInput } from './interface-reader-actions.mjs';
import { finalEditions, finalEditionSource } from '../docs/interface/final-editions.js';
import { validateFinalEditions, finalEditionInput } from './interface-final-editions.mjs';
import {capabilityTools, capabilityToolSource} from '../docs/interface/capability-tools.js';
import {supplementalReaders} from '../docs/interface/supplemental-readers.js';
import {projectCapabilityTools, capabilityInput} from './interface-capability-tools.mjs';
import { LEARNER_STATE_STORAGE_KEY, createEmptyLearnerState, evaluateLearnerState, setCourseCompletion, setCourseClaim, setPrerequisiteWaiver, normalizeLearnerState } from '../docs/learner-state.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ids = canonicalCourses.map((c) => c.id);
for (const course of interfaceCourses) for (const locale of supportedLocales) {
  const bindings = resourceBindings(course, locale);
  const sources = bindings.filter(isOriginalSource);
  assert.ok(sources.length, course.id + ': original source must be available in every interface language');
  const visible = renderResourceLinks(course, locale).split('<details class="resource-details">')[0];
  for (const source of sources) {
    assert.ok(visible.includes('href="'+source.href.replaceAll('&','&amp;')+'"'), 'Source must not be collapsed: '+course.id);
    assert.ok(visible.includes('data-original-source="'+source.origin+'"'));
  }
  for (const source of additionalOriginalSources[course.id] ?? []) {
    assert.equal(sources.filter(r=>r.href===safeResourceUrl(source.href) && r.contentLanguage===source.contentLanguage).length,1);
  }
  for (const source of (englishResources[course.id] ?? []).filter(isOriginalSource)) {
    assert.ok(sources.some(r=>r.href===source.href && r.contentLanguage==='en'));
  }
}
assert.notEqual(contentLanguageName('zh','en'),'shared metadata');
assert.notEqual(contentLanguageName('de','id'),'metadata bersama');
assert.ok(contentLanguageName('bn','en'));
assert.equal(isOriginalSource({origin:'published-translation'}),false);
assert.equal(isOriginalSource({origin:'published-english-component'}),false);
assert.deepEqual(['B80','D120'].map(id=>additionalOriginalSources[id][0].origin),['program-original','program-original']);
assert.equal(new Set(supplementalReaders.map(row=>row.id)).size,supplementalReaders.length);
for (const row of supplementalReaders) {
  assert.ok(ids.includes(row.courseId) && row.id.startsWith(row.courseId+':'));
  assert.equal(row.contentLanguage,'id');
  assert.ok(row.labels.id && row.labels.en && row.notes.id && row.notes.en);
  assert.ok(['companion','portable_html','html_download'].includes(row.kind));
  assert.ok(['HTML','HTML ZIP'].includes(row.format));
  assert.equal(new URL(row.href).protocol,'https:');
  assert.ok(['zenodo.org','kokunoyumeto.github.io'].includes(new URL(row.href).hostname));
  assert.match(row.sha256,/^[a-f0-9]{64}$/);
  assert.match(row.evidenceFile,/^docs\/interface\/evidence\/[a-z0-9-]+\.json$/);
  const proof=JSON.parse(await readFile(resolve(root,row.evidenceFile),'utf8'));
  const fact=proof.public_readback.find(item=>item.url===row.href);
  assert.ok(fact,'Reader must have actual public-byte evidence');
  assert.equal(fact.bytes,row.bytes); assert.equal(fact.sha256,row.sha256);
  if(row.offlineAfterDownload) {
    assert.equal(row.kind,'portable_html');
    assert.equal(proof.offline_dependency_replay.external_runtime_dependencies,0);
    assert.equal(proof.offline_dependency_replay.missing_local_references,0);
    assert.equal(proof.offline_dependency_replay.unresolved_fragments,0);
    assert.equal(proof.offline_dependency_replay.scripts,0);
    assert.ok(row.notes.en.includes('Extract'));
  } else assert.notEqual(row.kind,'portable_html');
  for (const locale of supportedLocales) {
    const rows=resourceBindings(interfaceCourses.find(c=>c.id===row.courseId),locale);
    const actual=rows.filter(item=>item.href===row.href);
    assert.equal(actual.length,1); assert.equal(actual[0].primary,false);
    assert.equal(actual[0].contentLanguage,'id'); assert.equal(actual[0].note,row.notes[locale]);
  }
}
assert.deepEqual(supplementalReaders.map(row=>row.id),['D20:complete-companion-html','D20:complete-offline-html','B10:complete-html-download']);
const b10Download=supplementalReaders.find(row=>row.courseId==='B10');
assert.equal(b10Download.offlineAfterDownload,false);
assert.equal(b10Download.kind,'html_download');
assert.ok(b10Download.notes.en.includes('MathJax and online features require internet'));
const b10Proof=JSON.parse(await readFile(resolve(root,b10Download.evidenceFile),'utf8'));
assert.equal(b10Proof.fully_offline_claim_supported,false);
assert.equal(b10Proof.mathjax_dependency,'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js');
assert.equal(resourceBindings(interfaceCourses.find(c=>c.id==='B10'),'id').find(row=>row.primary).href,'https://kokunoyumeto.github.io/discrete-mathematics-open-introduction-id/');
assert.equal(resourceBindings(interfaceCourses.find(c=>c.id==='D20'),'id').find(row=>row.primary).href,'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/D20/');
const capsuleBytes = await readFile(resolve(root,capabilityInput));
const capsules = JSON.parse(capsuleBytes);
assert.deepEqual(projectCapabilityTools(capsules,ids),capabilityTools);
assert.equal(capabilityToolSource.sha256,createHash('sha256').update(capsuleBytes).digest('hex'));
assert.equal(capabilityToolSource.bytes,capsuleBytes.length);
for (const corrupt of [
  c=>{c.find(r=>r.course_id==='B80').locale='en';},
  c=>{c.find(r=>r.course_id==='B80').layers.learner.tools[0].state='planned';},
  c=>{c.find(r=>r.course_id==='B80').layers.learner.tools[0].href='backend/b80/learning-map.json';},
  c=>{c.find(r=>r.course_id==='B80').layers.learner.tools[0].primary=true;},
  c=>{c.find(r=>r.course_id==='B80').layers.learner.tools[0].machine_data_is_learner_destination=true;},
  c=>{c.find(r=>r.course_id==='B80').layers.learner.tools[0].page.path='../../secret';},
  c=>{c.find(r=>r.course_id==='B80').layers.learner.tools.pop();},
  c=>{c.find(r=>r.course_id==='A00').layers.learner.tools[0].label='changed';},
]) { const changed=structuredClone(capsules); corrupt(changed); assert.throws(()=>projectCapabilityTools(changed,ids)); }
assert.equal(Object.values(englishResources).filter(rows=>rows.length).length,39);
assert.equal(englishResources.B80.find(r=>r.pages).pages,161);
assert.equal(englishResources.D50.find(r=>r.pages).pages,658);
assert.ok(!englishBindingExceptions.B80 && !englishBindingExceptions.D50);
assert.equal(englishResources.B80[0].kind,'HTML');
assert.equal(englishResources.D50[0].kind,'PDF');
assert.equal(englishResources.D50.find(r=>r.kind==='HTML ZIP').offlineAfterDownload,undefined);
assert.ok(englishResources.D50.find(r=>r.kind==='HTML ZIP').label.includes('MathJax requires internet'));
assert.deepEqual(englishResources.D70.filter(r=>r.pages).map(r=>r.pages),[457,102,68,7]);
assert.equal(englishResources.D80.find(r=>r.pages).pages,820);
assert.ok(!englishBindingExceptions.D70 && !englishBindingExceptions.D80);
for (const locale of supportedLocales) {
  const tools=resourceBindings(interfaceCourses.find(c=>c.id==='B80'),locale).filter(r=>r.capabilityToolId);
  assert.equal(tools.length,2);
  for(const tool of tools) {assert.equal(tool.contentLanguage,'id');assert.equal(tool.primary,false);assert.ok(tool.note.includes('72') && tool.note.includes('3'));}
  for(const courseId of ['B80','D50','D70','D80']) {
    const resources=resourceBindings(interfaceCourses.find(c=>c.id===courseId),locale);
    for(const target of englishResources[courseId]) assert.equal(resources.filter(r=>r.href===target.href && r.contentLanguage==='en').length,1);
    if(locale==='en') assert.equal(resources.filter(r=>r.primary).length,1);
  }
}
const editionBytes = await readFile(resolve(root, finalEditionInput));
const editionInput = JSON.parse(editionBytes);
assert.deepEqual(validateFinalEditions(editionInput, ids), finalEditions);
assert.equal(finalEditionSource.bytes, editionBytes.length);
assert.equal(finalEditionSource.sha256, createHash('sha256').update(editionBytes).digest('hex'));
assert.deepEqual(finalEditions.map(r=>r.courseId), ['A20','A30','B95','C140','D100']);
const finalResources = finalEditions.flatMap(r=>r.resources);
assert.equal(finalResources.length,13);
assert.equal(finalResources.reduce((n,r)=>n+(r.pages??0),0),8259);
for (const corrupt of [
  input=>{input.editions[0].courseId='Z999';},
  input=>{input.editions[0].prerequisites=[];},
  input=>{input.editions[0].resources[0].contentLanguage='en';},
  input=>{input.editions[0].resources[0].evidence.actual_sha256='0'.repeat(64);},
  input=>{input.editions[0].resources[0].href='javascript:alert(1)';},
  input=>{input.editions[0].resources[0].primary=false;},
  input=>{input.editions[0].resources[0].pages=-1;},
]) {const input=structuredClone(editionInput);corrupt(input);assert.throws(()=>validateFinalEditions(input,ids));}
for (const edition of finalEditions) for(const locale of supportedLocales) {
  const course=interfaceCourses.find(r=>r.id===edition.courseId);
  assert.equal(course.state,'published');
  const bindings=resourceBindings(course,locale);
  assert.deepEqual(bindings.filter(r=>r.editionResourceId).map(r=>r.editionResourceId),edition.resources.map(r=>r.id));
  assert.ok(bindings.some(r=>r.href===edition.archive));
  for(const id of edition.supersededSupplementIds) assert.ok(!bindings.some(r=>r.supplementId===id));
  for(const old of ['22142022','22184511','22192066','22164344','22164552']) assert.ok(!bindings.some(r=>r.href.includes(old)));
  for(const row of bindings.filter(r=>r.editionResourceId)) assert.equal(row.contentLanguage,'id');
}
for(const locale of supportedLocales) {
  const stats=resourceBindings(interfaceCourses.find(r=>r.id==='C140'),locale);
  for(const id of ['random-mathematical-statistics-html','random-mathematical-statistics-pdf','random-mathematical-statistics-doi']) assert.ok(stats.some(r=>r.supplementId===id));
  const geo=resourceBindings(interfaceCourses.find(r=>r.id==='D100'),locale).filter(r=>r.editionResourceId);
  assert.equal(geo.length,6); assert.equal(geo.reduce((n,r)=>n+(editionInput.editions[4].resources.find(e=>e.id===r.editionResourceId)?.pages??0),0),975);
  assert.ok(!resourceBindings(interfaceCourses.find(r=>r.id==='B95'),locale).some(r=>r.href.includes('/id-ID/courses/B95/')));
  for(const id of ['A20','A30','B95']) assert.ok(!resourceBindings(interfaceCourses.find(r=>r.id===id),locale).some(r=>r.editionResourceId && r.format !== 'PDF'));
}
const actionBytes = await readFile(resolve(root, readerActionInput));
const actionInput = JSON.parse(actionBytes);
assert.deepEqual(projectReaderActions(actionInput, ids), verifiedReaderActions);
assert.equal(readerActionSource.bytes, actionBytes.length);
assert.equal(readerActionSource.sha256, createHash('sha256').update(actionBytes).digest('hex'));
assert.equal(verifiedReaderActions.length, 7);
assert.equal(verifiedReaderActions.reduce((sum, action) => sum + action.pages, 0), 4077);
for (const corrupt of [
  (input) => { input.actions[0].evidence.status = 'pending'; },
  (input) => { input.actions[1].action_id = input.actions[0].action_id; },
  (input) => { input.actions[0].sha256 = 'not-a-hash'; },
  (input) => { input.actions[0].url = 'javascript:alert(1)'; },
  (input) => { input.summary.pages += 1; },
]) { const changed = structuredClone(actionInput); corrupt(changed); assert.throws(() => projectReaderActions(changed, ids)); }
assert.equal(ids.length, 40);
assert.equal(new Set(ids).size, 40);
assert.equal(canonicalCourses.reduce((n, c) => n + c.prerequisites.length, 0), 83);
assert.deepEqual(interfaceCourses.map((c) => [c.id, c.level, c.topic, c.prerequisites]), canonicalCourses.map((c) => [c.id, c.level, c.topic, c.prerequisites]));
assert.deepEqual(Object.keys(englishResources).sort(), [...ids].sort());
for (const bad of ['javascript:alert(1)', 'data:text/html,foo', 'http://example.org/', '//example.org/evil\npath']) assert.throws(() => safeResourceUrl(bad));
assert.equal(safeResourceUrl('backend/index.html'), siteOrigin + 'backend/index.html');
assert.equal(LEARNER_STATE_STORAGE_KEY, 'program-matematika-indonesia/learner-state/v1');
let state = createEmptyLearnerState();
state = setCourseCompletion(state, canonicalCourses, 'A00', true);
state = setCourseClaim(state, canonicalCourses, 'placement', 'A10', true);
state = setPrerequisiteWaiver(state, canonicalCourses, 'B10', 'A30', true);
assert.deepEqual(evaluateLearnerState(canonicalCourses, state), evaluateLearnerState(interfaceCourses, state));
assert.deepEqual(normalizeLearnerState(JSON.parse(JSON.stringify(state)), canonicalCourses), state);
for (const course of interfaceCourses) for (const locale of supportedLocales) {
  const copy = coursePresentation(course, locale);
  assert.ok(copy.title && copy.purpose && copy.outcome && copy.topic, course.id + ' copy ' + locale);
  const bindings = resourceBindings(course, locale);
  assert.ok(bindings.length);
  assert.equal(new Set(bindings.map((row) => row.href)).size, bindings.length, 'No duplicate resource URL');
  const projected = bindings.filter((row) => row.actionId);
  const expected = verifiedReaderActions.filter((row) => row.courseId === course.id);
  assert.deepEqual(projected.map((row) => row.actionId), expected.map((row) => row.actionId));
  for (const row of projected) {
    assert.equal(row.contentLanguage, 'id', 'Interface language does not translate a book');
    assert.ok(row.label.endsWith(locale === 'id' ? ' halaman' : ' pages'), 'Localized reader labels');
    assert.ok(row.offlineAfterDownload);
  }
  for (const row of bindings) {
    assert.equal(Intl.getCanonicalLocales(row.contentLanguage)[0],row.contentLanguage, 'Actual BCP 47 material language');
    assert.equal(new URL(row.href).protocol, 'https:');
  }
  const card = renderCourseCard(course, locale);
  for (const prereq of course.prerequisites) assert.ok(card.includes('data-course-link="' + prereq + '"'));
  for (const next of canonicalCourses.filter((row) => row.prerequisites.includes(course.id))) assert.ok(card.includes('data-course-link="' + next.id + '"'));
  if (locale === 'en' && !englishResources[course.id].length) {
    assert.ok(englishBindingExceptions[course.id]);
    assert.ok(card.includes('An edition link for this language has not yet been mapped'));
    assert.ok(!bindings.some((row) => row.primary));
  }
}

// Unit-execute the built offline script against a minimal document model.
// No browser, screenshot, network, or user-visible window is launched.
function executeOffline(html, locale, sharedStorage = new Map(), options = {}) {
  const nodes = new Map(), documentEvents = new Map(), windowEvents = new Map();
  let address = new URL(options.url ?? 'https://example.test/hub/' + locale + '/?level=C#course-C30');
  const historyRows = [address.href];
  const fakeNode = (id, value = '') => ({
    id, value, innerHTML: '', textContent: '', hidden: false, disabled: false, checked: false, dataset: {}, files: [],
    events: new Map(), addEventListener(type, fn) { this.events.set(type, fn); },
    scrollIntoView() {}, focus() { this.focused = true; }, click() {}, getAttribute(name) { return this[name]; },
  });
  for (const id of ['search','topic','level','show','course-grid','result-count','empty-state','progress-summary','claims','storage-message','placement-course','equivalence-course','waiver-target','waiver-prereq','add-placement','add-equivalence','add-waiver','reset-filters','clear-progress','export-progress','import-progress']) {
    nodes.set('#' + id, fakeNode(id, ['topic','level','show'].includes(id) ? 'all' : id.endsWith('-course') || id === 'waiver-target' ? 'A00' : ''));
  }
  const localeLinks = [...html.matchAll(/<a data-locale-link="([^"]+)" data-locale-base="([^"]+)" href="([^"]+)"/g)].map((match) => ({ ...fakeNode(match[1]), 'data-locale-base': match[2], href: match[3] }));
  assert.deepEqual(localeLinks.map(link => link.id), supportedLocales, 'Use actual generated language anchors');
  const classNames = new Set();
  const doc = {
    documentElement: { lang: locale, classList: { add: (name) => classNames.add(name) } },
    querySelector(selector) {
      if (nodes.has(selector)) return nodes.get(selector);
      if (/^#course-[A-D]\d{2,3}$/.test(selector) && nodes.get('#course-grid').innerHTML.includes('id="' + selector.slice(1) + '"')) return fakeNode(selector);
      return null;
    },
    querySelectorAll: (selector) => selector === '[data-locale-link]' ? localeLinks : [],
    addEventListener: (type, fn) => documentEvents.set(type, fn),
    createElement: () => fakeNode('temporary'),
  };
  const fakeStorage = {
    getItem: (key) => sharedStorage.get(key) ?? null,
    setItem: (key, value) => { if (options.failWrites) throw new Error('Quota exceeded'); sharedStorage.set(key, value); },
    removeItem: (key) => sharedStorage.delete(key),
  };
  const win = { localStorage: fakeStorage, confirm: () => true, addEventListener: (type, fn) => windowEvents.set(type, fn) };
  if (options.noStorage) Object.defineProperty(win, 'localStorage', { get() { throw new Error('Unavailable'); } });
  const context = vm.createContext({
    console, URL, URLSearchParams, Blob, Intl, document: doc, window: win,
    get location() { return address; },
    history: {
      replaceState(_state, _title, url) { if (options.failHistory) throw new Error('History unavailable'); address = new URL(url, address); historyRows[historyRows.length - 1] = address.href; },
      pushState(_state, _title, url) { if (options.failHistory) throw new Error('History unavailable'); address = new URL(url, address); historyRows.push(address.href); },
    },
    requestAnimationFrame: (fn) => fn(), setTimeout: () => 0,
  });
  const code = html.match(/<script>\n([\s\S]*)\n<\/script>/)?.[1];
  assert.ok(code, 'Offline inline script');
  new vm.Script(code, { filename: locale + '-offline.js' }).runInContext(context, { timeout: 5000 });
  assert.ok(classNames.has('js'), 'Initialization completed');
  return { doc, nodes, documentEvents, windowEvents, localeLinks, historyRows, sharedStorage, fakeStorage, context, address: () => address };
}
const sizes = [];
const receipt = JSON.parse(await readFile(resolve(root, 'docs/interface/build-receipt.json'), 'utf8'));
for (const item of [...receipt.inputs, ...receipt.outputs]) {
  const bytes = await readFile(resolve(root, item.path));
  assert.equal(bytes.length, item.bytes, item.path);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), item.sha256, item.path);
}
for (const locale of supportedLocales) for (const file of ['index.html', 'learning-map.html', 'learning-map-paired.html']) {
  const html = await readFile(resolve(root, 'docs', locale, file), 'utf8');
  assert.ok(html.includes('<html lang="' + locale + '">'));
  const staticHtml = html.replace(/<script[\s\S]*?<\/script>/g, '');
  const cardIds = [...staticHtml.matchAll(/<article class="course-card" id="course-([^"]+)"/g)].map((m) => m[1]);
  assert.deepEqual(cardIds, ids, locale + '/' + file + ' static coverage');
  assert.equal([...staticHtml.matchAll(/data-reader-action="([^"]+)"/g)].length, 7, 'Seven verified CLP actions visible in static markup');
  for (const action of verifiedReaderActions) assert.ok(staticHtml.includes(action.href.replaceAll('&', '&amp;')));
  assert.equal([...staticHtml.matchAll(/data-edition-resource="([^"]+)"/g)].length,13);
  for (const resource of finalResources) assert.ok(staticHtml.includes(resource.href.replaceAll('&','&amp;')));
  assert.equal([...staticHtml.matchAll(/data-capability-tool="([^"]+)"/g)].length,2);
  assert.equal([...staticHtml.matchAll(/data-supplemental-reader="([^"]+)"/g)].length,supplementalReaders.length);
  for (const row of supplementalReaders) assert.ok(staticHtml.includes(row.href.replaceAll('&','&amp;')));
  for(const courseId of ['B80','D50','D70','D80']) for(const row of englishResources[courseId]) assert.ok(staticHtml.includes(row.href.replaceAll('&','&amp;')));
  const elementIds = [...staticHtml.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]);
  assert.equal(new Set(elementIds).size, elementIds.length, 'No duplicate DOM ids');
  for (const match of staticHtml.matchAll(/href="#([^"]+)"/g)) assert.ok(elementIds.includes(match[1]), 'Resolvable fragment: ' + match[1]);
  for (const code of supportedLocales) assert.ok(html.includes('data-locale-link="' + code + '"'));
  assert.ok(html.includes('hreflang="x-default"'));
  assert.ok(html.includes('No') || locale === 'id');
  for (const match of staticHtml.matchAll(/(?:src|href)="([^"]+)"/g)) {
    if (match[1].startsWith('#')) continue;
    if (/^https:\/\//.test(match[1])) continue;
    if (file === 'learning-map-paired.html') {
      assert.ok(supportedLocales.some(code => match[1] === '../' + code + '/learning-map-paired.html'), 'Only paired language anchors may be relative');
    } else assert.equal(file, 'index.html', 'Standalone document must have no relative dependency: ' + match[1]);
    const target = resolve(root, 'docs', locale, match[1], match[1].endsWith('/') ? 'index.html' : '');
    await readFile(target);
  }
  sizes.push({ locale, file, bytes: Buffer.byteLength(html), gzipBytes: gzipSync(html).length });
  if (file !== 'index.html') {
    assert.ok(!/<script[^>]+src=|<link[^>]+rel="stylesheet"/.test(html), 'Self-contained executable/style');
    assert.ok(Buffer.byteLength(html) < 350000, 'Offline map size budget');
    assert.ok(gzipSync(html).length < 70000, 'Compressed map size budget');
    const run = executeOffline(html, locale);
    // Compact payload must preserve all effective data, not just course counts.
    assert.deepEqual(JSON.parse(vm.runInContext('JSON.stringify(interfaceCourses)',run.context)),JSON.parse(JSON.stringify(interfaceCourses)));
    for (const c of interfaceCourses) {
      const actual=JSON.parse(vm.runInContext('JSON.stringify(resourceBindings(interfaceCourses.find(c=>c.id==='+JSON.stringify(c.id)+'),'+JSON.stringify(locale)+'))',run.context));
      assert.deepEqual(actual,resourceBindings(c,locale),'Online/offline binding equality: '+c.id);
    }
    assert.ok(run.nodes.get('#course-grid').innerHTML.includes('id="course-C30"'));
    for (const link of run.localeLinks) { assert.ok(link.href.endsWith('?level=C#course-C30')); }
    run.nodes.get('#search').value = 'zzzz-no-matches';
    run.nodes.get('#search').events.get('input')();
    assert.equal(run.nodes.get('#course-grid').innerHTML, '');
    assert.equal(run.nodes.get('#empty-state').hidden, false);
    assert.equal(run.address().hash, '', 'Changing a filter clears a stale course fragment');
    const reload = executeOffline(html, locale, run.sharedStorage, { url: run.address().href });
    assert.equal(reload.nodes.get('#course-grid').innerHTML, '', 'Reload preserves zero-match filter');
    for (const link of run.localeLinks) assert.ok(link.href.includes('q=zzzz-no-matches') && !link.href.includes('#course-'));
    run.nodes.get('#reset-filters').events.get('click')();
    assert.equal((run.nodes.get('#course-grid').innerHTML.match(/<article /g) ?? []).length, 40);
    const event = { target: { closest: (selector) => selector === '[data-course-link]' ? { dataset: { courseLink: 'A00' } } : null }, button: 0, preventDefault() {} };
    run.documentEvents.get('click')(event);
    assert.equal(run.historyRows.length, 2, 'Course navigation creates history, not replace-only');
    assert.equal(run.address().hash, '#course-A00');
    assert.ok(run.windowEvents.has('popstate') && run.windowEvents.has('hashchange'));
    run.documentEvents.get('change')({ target: { matches: () => true, dataset: { completion: 'A00' }, checked: true } });
    const stored = JSON.parse(run.sharedStorage.get(LEARNER_STATE_STORAGE_KEY));
    assert.ok(stored.completedCourseIds.includes('A00'));
    const otherLocale = locale === 'id' ? 'en' : 'id';
    const otherHtml = await readFile(resolve(root, 'docs', otherLocale, 'learning-map.html'), 'utf8');
    const next = executeOffline(otherHtml, otherLocale, run.sharedStorage, { url: 'https://example.test/hub/' + otherLocale + '/' });
    assert.ok(next.nodes.get('#course-grid').innerHTML.includes('data-completion="A00" checked'), 'Progress crosses locales');
    next.nodes.get('#show').value = 'completed';
    next.nodes.get('#show').events.get('change')();
    next.doc.activeElement = { dataset: { completion: 'A00' } };
    next.documentEvents.get('change')({ target: { matches: () => true, dataset: { completion: 'A00' }, checked: false } });
    assert.equal(next.nodes.get('#result-count').focused, true, 'Removing a visible completed card restores focus to results');
    next.nodes.get('#show').value = 'eligible';
    next.nodes.get('#show').events.get('change')();
    next.nodes.get('#result-count').focused = false;
    next.doc.activeElement = { dataset: { completion: 'A00' } };
    next.documentEvents.get('change')({ target: { matches: () => true, dataset: { completion: 'A00' }, checked: true } });
    assert.equal(next.nodes.get('#result-count').focused, true, 'Completing an eligible card restores focus to results');
    for (const base of ['file:///C:/Learning%20folder/Matematika%20%E6%95%B0%E5%AD%A6/docs/', 'https://example.test/unpacked/docs/']) {
      const fileUrl = base + locale + '/' + file;
      const unknown = executeOffline(html, locale, new Map(), { url: fileUrl + '?progress=QUERY_SENTINEL#completedCourseIds=FRAGMENT_SENTINEL', failHistory: true });
      for (const action of [() => {}, () => unknown.windowEvents.get('hashchange')(), () => unknown.windowEvents.get('popstate')()]) {
        action();
        for (const link of unknown.localeLinks) assert.ok(!link.href.includes('SENTINEL') && !new URL(link.href).hash, 'Only known navigation fragments propagate');
      }
      for (const fragment of ['#top', '#katalog', '#progress', '#about']) {
        unknown.address().hash = fragment; unknown.windowEvents.get('hashchange')();
        for (const link of unknown.localeLinks) assert.equal(new URL(link.href).hash, fragment);
      }
      const offline = executeOffline(html, locale, new Map(), { noStorage: true, failHistory: true, url: fileUrl + '?level=C&progress=private&claims=private#course-C30' });
      for (const link of offline.localeLinks) {
        const actual = new URL(link.href);
        const expected = file === 'learning-map-paired.html' ? base + link.id + '/learning-map-paired.html' : siteOrigin + link.id + '/';
        assert.equal(actual.origin + actual.pathname, new URL(expected).origin + new URL(expected).pathname);
        assert.equal(actual.search, '?level=C');
        assert.equal(actual.hash, '#course-C30');
        assert.ok(!actual.href.includes('private'), 'Do not propagate unknown/progress query data');
      }
      offline.nodes.get('#search').value = 'new search';
      offline.nodes.get('#search').events.get('input')();
      assert.ok(offline.address().href.includes('#course-C30'), 'Throwing history leaves old address unchanged');
      for (const link of offline.localeLinks) {
        assert.equal(new URL(link.href).searchParams.get('q'), 'new search', 'Current filters survive rejected history write');
        assert.equal(new URL(link.href).hash, '', 'Stale course fragment is cleared in navigation despite rejected history');
      }
      offline.nodes.get('#reset-filters').events.get('click')();
      offline.documentEvents.get('click')(event);
      for (const link of offline.localeLinks) assert.equal(new URL(link.href).hash, '#course-A00', 'Course navigation fallback retains current fragment');
      const imported = JSON.stringify(state);
      await offline.nodes.get('#import-progress').events.get('change')({ target: { files: [{ size: imported.length, text: async () => imported }], value: 'record.json' } });
      assert.ok(offline.nodes.get('#course-grid').innerHTML.includes('data-completion="A00" checked'), 'Import moves progress into isolated/offline context');
      offline.nodes.get('#show').value = 'completed';
      offline.nodes.get('#show').events.get('change')();
      for (const link of offline.localeLinks) {
        assert.equal(new URL(link.href).search, '?show=completed');
        assert.equal(new URL(link.href).hash, '');
        assert.ok(!link.href.includes('placement') && !link.href.includes('waiver') && !link.href.includes('completedCourseIds'));
      }
    }
    const quota = executeOffline(html, locale, new Map(), { failWrites: true, url: 'https://example.test/' + locale + '/' });
    quota.documentEvents.get('change')({ target: { matches: () => true, dataset: { completion: 'A00' }, checked: true } });
    for (const event of [{ key: 'unrelated-preference', storageArea: quota.fakeStorage }, { key: LEARNER_STATE_STORAGE_KEY, storageArea: quota.fakeStorage }, { key: null, storageArea: quota.fakeStorage }]) {
      quota.windowEvents.get('storage')(event);
      assert.ok(quota.nodes.get('#course-grid').innerHTML.includes('data-completion="A00" checked'), 'Failed-write progress survives cross-tab events');
    }
    const sync = executeOffline(html, locale, new Map(), { url: 'https://example.test/' + locale + '/' });
    sync.sharedStorage.set(LEARNER_STATE_STORAGE_KEY, JSON.stringify(setCourseCompletion(createEmptyLearnerState(), canonicalCourses, 'A00', true)));
    sync.windowEvents.get('storage')({ key: 'unrelated-preference', storageArea: sync.fakeStorage });
    assert.ok(!sync.nodes.get('#course-grid').innerHTML.includes('data-completion="A00" checked'));
    sync.windowEvents.get('storage')({ key: LEARNER_STATE_STORAGE_KEY, storageArea: {} });
    assert.ok(!sync.nodes.get('#course-grid').innerHTML.includes('data-completion="A00" checked'));
    sync.windowEvents.get('storage')({ key: LEARNER_STATE_STORAGE_KEY, storageArea: sync.fakeStorage });
    assert.ok(sync.nodes.get('#course-grid').innerHTML.includes('data-completion="A00" checked'), 'Matching persisted progress event still synchronizes');
  }
}
console.log(JSON.stringify({ status: 'pass', courses: ids.length, edges: 83, locales: supportedLocales, tests: ['graph-identity','explicit-language-bindings','static-40-course-catalogs','all-internal-fragments','safe-https-links','offline-script-execution','search-and-reset','course-history','shared-progress','storage-unavailable','receipt-hashes','rendered-language-anchors','paired-static-local-closure','standalone-online-fallback','file-and-unicode-paths','history-rejection-current-view','navigation-no-progress-data','isolated-progress-import'], sizes }));
