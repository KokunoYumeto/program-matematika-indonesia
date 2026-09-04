import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { gzipSync } from 'node:zlib';
import vm from 'node:vm';
import { courses as canonicalCourses } from '../docs/courses.js';
import { interfaceCourses, interfaceTopics, coursePresentation, resourceBindings, renderCourseCard, safeResourceUrl } from '../docs/interface/view.js';
import { supportedLocales, englishResources, englishBindingExceptions, siteOrigin } from '../docs/interface/locales.js';
import { LEARNER_STATE_STORAGE_KEY, createEmptyLearnerState, evaluateLearnerState, setCourseCompletion, setCourseClaim, setPrerequisiteWaiver, normalizeLearnerState } from '../docs/learner-state.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ids = canonicalCourses.map((c) => c.id);
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
  for (const row of bindings) {
    assert.ok(['en', 'id', 'und'].includes(row.contentLanguage));
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
  const localeLinks = supportedLocales.map((code) => ({ ...fakeNode(code), 'data-locale-base': siteOrigin + code + '/' }));
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
    setItem: (key, value) => sharedStorage.set(key, value),
    removeItem: (key) => sharedStorage.delete(key),
  };
  const win = { localStorage: fakeStorage, confirm: () => true, addEventListener: (type, fn) => windowEvents.set(type, fn) };
  if (options.noStorage) Object.defineProperty(win, 'localStorage', { get() { throw new Error('Unavailable'); } });
  const context = vm.createContext({
    console, URL, URLSearchParams, Blob, Intl, document: doc, window: win,
    get location() { return address; },
    history: {
      replaceState(_state, _title, url) { address = new URL(url, address); historyRows[historyRows.length - 1] = address.href; },
      pushState(_state, _title, url) { address = new URL(url, address); historyRows.push(address.href); },
    },
    requestAnimationFrame: (fn) => fn(), setTimeout: () => 0,
  });
  const code = html.match(/<script>\n([\s\S]*)\n<\/script>/)?.[1];
  assert.ok(code, 'Offline inline script');
  new vm.Script(code, { filename: locale + '-offline.js' }).runInContext(context, { timeout: 5000 });
  assert.ok(classNames.has('js'), 'Initialization completed');
  return { doc, nodes, documentEvents, windowEvents, localeLinks, historyRows, sharedStorage, context, address: () => address };
}
const sizes = [];
const receipt = JSON.parse(await readFile(resolve(root, 'docs/interface/build-receipt.json'), 'utf8'));
for (const item of [...receipt.inputs, ...receipt.outputs]) {
  const bytes = await readFile(resolve(root, item.path));
  assert.equal(bytes.length, item.bytes, item.path);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), item.sha256, item.path);
}
for (const locale of supportedLocales) for (const file of ['index.html', 'learning-map.html']) {
  const html = await readFile(resolve(root, 'docs', locale, file), 'utf8');
  assert.ok(html.includes('<html lang="' + locale + '">'));
  const staticHtml = html.replace(/<script[\s\S]*?<\/script>/g, '');
  const cardIds = [...staticHtml.matchAll(/<article class="course-card" id="course-([^"]+)"/g)].map((m) => m[1]);
  assert.deepEqual(cardIds, ids, locale + '/' + file + ' static coverage');
  const elementIds = [...staticHtml.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]);
  assert.equal(new Set(elementIds).size, elementIds.length, 'No duplicate DOM ids');
  for (const match of staticHtml.matchAll(/href="#([^"]+)"/g)) assert.ok(elementIds.includes(match[1]), 'Resolvable fragment: ' + match[1]);
  for (const code of supportedLocales) assert.ok(html.includes('data-locale-link="' + code + '"'));
  assert.ok(html.includes('hreflang="x-default"'));
  assert.ok(html.includes('No') || locale === 'id');
  for (const match of staticHtml.matchAll(/(?:src|href)="([^"]+)"/g)) {
    if (match[1].startsWith('#')) continue;
    if (/^https:\/\//.test(match[1])) continue;
    assert.equal(file, 'index.html', 'Offline document must have no relative dependency: ' + match[1]);
    const target = resolve(root, 'docs', locale, match[1], match[1].endsWith('/') ? 'index.html' : '');
    await readFile(target);
  }
  sizes.push({ locale, file, bytes: Buffer.byteLength(html), gzipBytes: gzipSync(html).length });
  if (file === 'learning-map.html') {
    assert.ok(!/<script[^>]+src=|<link[^>]+rel="stylesheet"/.test(html), 'Self-contained executable/style');
    assert.ok(Buffer.byteLength(html) < 350000, 'Offline map size budget');
    assert.ok(gzipSync(html).length < 70000, 'Compressed map size budget');
    const run = executeOffline(html, locale);
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
    executeOffline(html, locale, new Map(), { noStorage: true, url: 'file:///tmp/learning-map.html' });
  }
}
console.log(JSON.stringify({ status: 'pass', courses: ids.length, edges: 83, locales: supportedLocales, tests: ['graph-identity','explicit-language-bindings','static-40-course-catalogs','all-internal-fragments','safe-https-links','offline-script-execution','search-and-reset','course-history','shared-progress','storage-unavailable','receipt-hashes'], sizes }));
