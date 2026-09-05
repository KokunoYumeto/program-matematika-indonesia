import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// Deterministic DOM-stub regression tests, not a browser/rendering audit.
// Exercise the actual shipped module against the actual forty-card fallback.
const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const html = await readFile(resolve(project, 'docs/backend/index.html'), 'utf8');
const source = await readFile(resolve(project, 'docs/backend/backend.js'), 'utf8');
const courses = JSON.parse(await readFile(resolve(project, 'docs/data/course-capsule-v1/course-capsules.json'), 'utf8'));
const catalogUrl = '../data/course-capsule-v1/course-capsules.json';
const canonicalReaderActionsUrl = '../data/course-capsule-v1/learner-reader-actions-v1.json';
const canonicalReaderActions = JSON.parse(await readFile(resolve(project, 'docs/data/course-capsule-v1/learner-reader-actions-v1.json'), 'utf8'));
assert.equal(canonicalReaderActions.schema_id, 'interlanguage/learner-reader-actions/v1');
assert.equal(canonicalReaderActions.actions.length, 7);
const fallback = html.split('<!-- COURSE-FALLBACK:START -->')[1].split('<!-- COURSE-FALLBACK:END -->')[0];
const staticIds = [...fallback.matchAll(/data-static-course-id="([^"]+)"/g)].map((match) => match[1]);
assert.equal(staticIds.length, 40);
assert.equal(new Set(staticIds).size, 40);
assert.equal((fallback.match(/Kesiapan akses/g) ?? []).length, 40);
assert.equal((fallback.match(/Bahan pengajar terindeks/g) ?? []).length, 0);
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const runModule = new AsyncFunction('document', 'fetch', 'console', source);

function fixture() {
  const elements = new Map();
  const element = (id) => {
    if (!elements.has(id)) elements.set(id, {
      value: id === '#course-search' ? '' : 'all',
      dataset: {}, textContent: '', innerHTML: '', disabled: true,
      events: new Map(), attrs: new Map(),
      addEventListener(event, callback) { this.events.set(event, callback); },
      setAttribute(name, value) { this.attrs.set(name, value); },
      querySelectorAll() { return []; },
    });
    return elements.get(id);
  };
  const buttons = ['learner', 'educator', 'production', 'interop'].map((view) => {
    const button = element('#view-' + view);
    button.dataset.view = view;
    button.attrs.set('aria-pressed', String(view === 'learner'));
    return button;
  });
  element('#course-grid').innerHTML = fallback;
  const document = {
    querySelector: element,
    querySelectorAll(selector) { assert.equal(selector, '[data-view]'); return buttons; },
  };
  const controls = [...buttons, ...['#course-search', '#level-filter', '#state-filter', '#reset-filters'].map(element)];
  const fire = (control, event) => {
    assert.ok(control.events.has(event));
    control.events.get(event)();
  };
  const preserveFallback = () => {
    assert.equal(element('#course-grid').innerHTML, fallback);
    assert.doesNotMatch(element('#result-count').textContent, /0 dari 0/);
    assert.ok(controls.every((control) => control.disabled));
  };
  const exerciseUnavailable = () => {
    for (const button of buttons) { fire(button, 'click'); preserveFallback(); }
    for (const [id, event, value] of [
      ['#course-search', 'input', 'geometri'],
      ['#level-filter', 'change', 'D'],
      ['#state-filter', 'change', 'production'],
      ['#reset-filters', 'click', ''],
    ]) {
      element(id).value = value;
      fire(element(id), event);
      preserveFallback();
    }
  };
  return { document, element, buttons, controls, fire, preserveFallback, exerciseUnavailable };
}

const quietConsole = { error() {} };
const scenarios = [];
{
  const f = fixture();
  let rejectFetch;
  const loading = runModule(f.document, () => new Promise((_, reject) => { rejectFetch = reject; }), quietConsole);
  f.exerciseUnavailable();
  rejectFetch(new Error('simulated offline'));
  await loading;
  f.exerciseUnavailable();
  assert.match(f.element('#result-count').textContent, /daftar dasar tetap tersedia/);
  scenarios.push('pending_then_rejected_fetch_preserves_all_40_cards_and_controls');
}
for (const [name, fetch] of [
  ['immediate_rejection', async () => { throw new Error('offline'); }],
  ['http_503', async () => ({ ok: false, status: 503 })],
  ['invalid_json', async () => ({ ok: true, json: async () => { throw new Error('invalid JSON'); } })],
  ['wrong_course_count', async () => ({ ok: true, json: async () => [] })],
  ['malformed_course', async () => ({ ok: true, json: async () => Array.from({ length: 40 }, () => ({})) })],
]) {
  const f = fixture();
  await runModule(f.document, fetch, quietConsole);
  f.exerciseUnavailable();
  scenarios.push(name + '_preserves_all_40_cards');
}
{
  const f = fixture();
  const requestedUrls = [];
  const fetchSuccessFixture = async (url) => {
    requestedUrls.push(url);
    if (url === catalogUrl) return { ok: true, json: async () => structuredClone(courses) };
    if (url === canonicalReaderActionsUrl) return { ok: true, json: async () => structuredClone(canonicalReaderActions) };
    throw new Error('unexpected fixture URL: ' + url);
  };
  await runModule(f.document, fetchSuccessFixture, quietConsole);
  assert.deepEqual(requestedUrls, [catalogUrl, canonicalReaderActionsUrl]);
  assert.ok(f.controls.every((control) => !control.disabled));
  const visibleCount = () => (f.element('#course-grid').innerHTML.match(/data-course-id=/g) ?? []).length;
  assert.equal(visibleCount(), 40);
  assert.match(f.element('#course-grid').innerHTML, />Baca daring — [A-D][0-9]{2,3} — bagian kursus /);
  const learnerCards = [...f.element('#course-grid').innerHTML.matchAll(/<article class="course-card"[^>]*>([\s\S]*?)<\/article>/g)];
  assert.equal(learnerCards.length, 40);
  const clpReaderLinksByCourse = Object.fromEntries(['B20', 'B30', 'B50', 'B60'].map((courseId) => [courseId, 0]));
  for (const [, cardHtml] of learnerCards) {
    const courseId = cardHtml.match(/<span class="course-code">(B20|B30|B50|B60)<\/span>/)?.[1];
    if (courseId) clpReaderLinksByCourse[courseId] = (cardHtml.match(/class="reader-action"/g) ?? []).length;
  }
  assert.deepEqual(clpReaderLinksByCourse, { B20: 2, B30: 1, B50: 2, B60: 2 });
  assert.equal(Object.values(clpReaderLinksByCourse).reduce((total, count) => total + count, 0), 7);
  for (const [, cardHtml] of learnerCards) {
    const hrefs = [...cardHtml.matchAll(/href="([^"]+)"/g)].map((match) => match[1]);
    assert.equal(new Set(hrefs).size, hrefs.length, 'Learner card contains a duplicate destination.');
  }
  for (const button of f.buttons) {
    f.fire(button, 'click');
    assert.equal(visibleCount(), 40);
    assert.equal(button.attrs.get('aria-pressed'), 'true');
    assert.equal(f.buttons.filter((item) => item.attrs.get('aria-pressed') === 'true').length, 1);
    assert.doesNotMatch(f.element('#course-grid').innerHTML, /href="(?:04_mirrors|javascript:)/);
    assert.doesNotMatch(f.element('#course-grid').innerHTML, />course-native-primary</);
  }
  const adapterCount = courses.filter((course) => ['verified', 'legacy_verified', 'available_unverified'].includes(course.layers.interoperability.semantic_adapter.status)).length;
  assert.equal(adapterCount, 29); // Prior 28 verified adapters plus C70 Applied Combinatorics.
  const topology=courses.find(c=>c.course_id==='C90');
  assert.equal(topology.layers.interoperability.semantic_adapter.contract_version,'topology-learning-capability/1');
  assert.equal(topology.layers.learner.tools.length,1);
  assert.equal(topology.layers.educator.unit_alignment_status,'verified');
  assert.ok(topology.layers.educator.resources.some(r=>r.id==='C90:native-reader-observation'));
  assert.ok(topology.layers.educator.resources.some(r=>r.id==='C90:topology-educator-v1'&&r.status==='verified'));
  const geometry=courses.find(c=>c.course_id==='C100');
  assert.equal(geometry.layers.interoperability.semantic_adapter.contract_version,'geometry-learning-capability/1');
  assert.equal(geometry.layers.learner.tools.length,2);
  assert.equal(geometry.layers.educator.unit_alignment_status,'verified');
  assert.ok(geometry.layers.educator.resources.some(r=>r.id==='C100:native-educator-observation'&&r.status==='available_unverified'));
  assert.ok(geometry.layers.educator.resources.some(r=>r.id==='C100:geometry-educator-v1'&&r.status==='verified'));
  const d40=courses.find(c=>c.course_id==='D40');
  assert.equal(d40.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(d40.layers.learner.tools.length,1);
  assert.equal(d40.layers.learner.tools[0].tool_id,'d40.open_learner_hub');
  assert.equal(d40.layers.learner.tools[0].href,'backend/d40/D40.html');
  assert.equal(d40.layers.curriculum.unit_identity_status,'verified');
  assert.equal(d40.layers.translation.ledger_status,'verified');
  assert.equal(d40.layers.translation.terminology_status,'verified');
  assert.equal(d40.layers.translation.rights_status,'verified');
  assert.equal(d40.layers.translation.corrections_status,'verified');
  assert.equal(d40.layers.production.build_status,'verified');
  assert.equal(d40.layers.production.deterministic_replay_status,'verified');
  assert.equal(d40.layers.educator.status,'verified');
  assert.equal(d40.layers.educator.unit_alignment_status,'verified');
  assert.ok(d40.layers.educator.resources.some(r=>r.id==='D40:native-educator-observation'&&r.status==='available_unverified'));
  assert.ok(d40.layers.educator.resources.some(r=>r.id==='D40:educator-hub-v1'&&r.status==='verified'));
  assert.equal(d40.layers.learner.capabilities.mathml,'verified');
  assert.equal(d40.layers.learner.capabilities.semantic_html,'verified');
  const d70=courses.find(c=>c.course_id==='D70');
  assert.equal(d70.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(d70.layers.learner.tools.length,1);
  assert.equal(d70.layers.learner.tools[0].tool_id,'d70.open_learner_hub');
  assert.equal(d70.layers.learner.tools[0].href,'backend/d70/D70.html');
  assert.equal(d70.layers.curriculum.unit_identity_status,'verified');
  assert.equal(d70.layers.translation.ledger_status,'verified');
  assert.equal(d70.layers.translation.terminology_status,'verified');
  assert.equal(d70.layers.translation.rights_status,'verified');
  assert.equal(d70.layers.translation.corrections_status,'verified');
  assert.equal(d70.layers.production.build_status,'available_unverified');
  assert.equal(d70.layers.production.deterministic_replay_status,'available_unverified');
  assert.equal(d70.layers.educator.status,'verified');
  assert.equal(d70.layers.educator.unit_alignment_status,'verified');
  assert.ok(d70.layers.educator.resources.some(r=>r.id==='D70:native-educator-observation'&&r.status==='available_unverified'&&r.url==='https://zenodo.org/records/22160944'));
  assert.ok(d70.layers.educator.resources.some(r=>r.id==='D70:educator-hub-v1'&&r.status==='verified'));
  const d80=courses.find(c=>c.course_id==='D80');
  assert.equal(d80.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(d80.layers.learner.tools.length,1);
  assert.equal(d80.layers.learner.tools[0].tool_id,'d80.open_learner_hub');
  assert.equal(d80.layers.learner.tools[0].href,'backend/d80/D80.html');
  assert.equal(d80.layers.curriculum.unit_identity_status,'verified');
  assert.equal(d80.layers.educator.status,'verified');
  assert.equal(d80.layers.educator.unit_alignment_status,'verified');
  assert.ok(d80.layers.educator.resources.some(r=>r.id==='D80:native-educator-observation'&&r.status==='available_unverified'));
  assert.ok(d80.layers.educator.resources.some(r=>r.id==='D80:educator-hub-v1'&&r.status==='verified'));
  assert.equal(d80.layers.learner.capabilities.mathml,'available_unverified');
  assert.equal(d80.layers.learner.capabilities.semantic_html,'verified');
  const d100=courses.find(c=>c.course_id==='D100');
  assert.equal(d100.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(d100.layers.learner.tools.length,1);
  assert.equal(d100.layers.learner.tools[0].tool_id,'d100.open_learner_hub');
  assert.equal(d100.layers.learner.tools[0].href,'backend/d100/D100.html');
  assert.match(d100.layers.learner.tools[0].scope,/English en-v1\.0\.0 capability view/);
  assert.equal(d100.layers.curriculum.unit_identity_status,'verified');
  assert.equal(d100.layers.translation.ledger_status,'verified');
  assert.equal(d100.layers.translation.terminology_status,'verified');
  assert.equal(d100.layers.translation.rights_status,'verified');
  assert.equal(d100.layers.translation.corrections_status,'verified');
  assert.equal(d100.layers.production.build_status,'available_unverified');
  assert.equal(d100.layers.production.deterministic_replay_status,'available_unverified');
  assert.equal(d100.layers.educator.status,'verified');
  assert.equal(d100.layers.educator.unit_alignment_status,'verified');
  assert.ok(d100.layers.educator.resources.some(r=>r.id==='D100:educator-hub-en-v1'&&r.status==='verified'));
  const d10=courses.find(c=>c.course_id==='D10');
  assert.equal(d10.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(d10.layers.learner.tools.length,1);
  assert.equal(d10.layers.learner.tools[0].tool_id,'d10.open_learner_hub');
  assert.equal(d10.layers.learner.tools[0].href,'backend/d10/D10.html');
  assert.equal(d10.layers.curriculum.unit_identity_status,'verified');
  assert.equal(d10.layers.translation.ledger_status,'verified');
  assert.equal(d10.layers.translation.terminology_status,'verified');
  assert.equal(d10.layers.translation.rights_status,'verified');
  assert.equal(d10.layers.translation.corrections_status,'verified');
  assert.equal(d10.layers.production.build_status,'verified');
  assert.equal(d10.layers.production.deterministic_replay_status,'verified');
  assert.equal(d10.layers.educator.status,'verified');
  assert.equal(d10.layers.educator.unit_alignment_status,'verified');
  assert.ok(d10.layers.educator.resources.some(r=>r.id==='D10:educator-hub-v1'&&r.status==='verified'));
  assert.ok(d10.layers.educator.resources.some(r=>r.id==='D10:educator-map-v1'&&r.status==='verified'));
  assert.equal(d10.layers.learner.capabilities.semantic_html,'verified');
  assert.equal(d10.layers.learner.capabilities.mathml,'verified');
  const d120=courses.find(c=>c.course_id==='D120');
  assert.equal(d120.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(d120.layers.learner.tools.length,1);
  assert.equal(d120.layers.learner.tools[0].tool_id,'d120.open_learner_hub');
  assert.equal(d120.layers.learner.tools[0].href,'backend/d120/D120.html');
  assert.equal(d120.layers.curriculum.unit_identity_status,'verified');
  assert.equal(d120.layers.translation.ledger_status,'not_applicable');
  assert.equal(d120.layers.translation.terminology_status,'verified');
  assert.equal(d120.layers.translation.rights_status,'verified');
  assert.equal(d120.layers.translation.corrections_status,'verified');
  assert.equal(d120.layers.production.build_status,'verified');
  assert.equal(d120.layers.production.deterministic_replay_status,'verified');
  assert.equal(d120.layers.educator.status,'verified');
  assert.equal(d120.layers.educator.unit_alignment_status,'verified');
  assert.ok(d120.layers.educator.resources.some(r=>r.id==='D120:native-delivery-wrapper'&&r.status==='verified'));
  assert.ok(d120.layers.educator.resources.some(r=>r.id==='D120:educator-hub-v1'&&r.status==='verified'));
  assert.equal(d120.layers.learner.capabilities.semantic_html,'verified');
  assert.equal(d120.layers.learner.capabilities.mathml,'available_unverified');
  const c120=courses.find(c=>c.course_id==='C120');
  assert.equal(c120.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(c120.layers.learner.tools.length,1);
  assert.equal(c120.layers.learner.tools[0].tool_id,'c120.open_learner_hub');
  assert.equal(c120.layers.learner.tools[0].href,'backend/c120/C120.html');
  assert.equal(c120.layers.curriculum.unit_identity_status,'verified');
  assert.equal(c120.layers.translation.ledger_status,'verified');
  assert.equal(c120.layers.translation.terminology_status,'verified');
  assert.equal(c120.layers.translation.rights_status,'verified');
  assert.equal(c120.layers.translation.corrections_status,'verified');
  assert.equal(c120.layers.production.build_status,'verified');
  assert.equal(c120.layers.production.deterministic_replay_status,'verified');
  assert.equal(c120.layers.educator.status,'verified');
  assert.equal(c120.layers.educator.unit_alignment_status,'verified');
  assert.ok(c120.layers.educator.resources.some(r=>r.id==='C120:educator-hub-v1'&&r.status==='verified'));
  assert.ok(c120.layers.educator.resources.some(r=>r.id==='C120:educator-map-v1'&&r.status==='verified'));
  assert.equal(c120.layers.learner.capabilities.semantic_html,'available_unverified');
  assert.equal(c120.layers.learner.capabilities.mathml,'available_unverified');
  const c110=courses.find(c=>c.course_id==='C110');
  assert.equal(c110.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(c110.layers.learner.tools.length,1);
  assert.equal(c110.layers.learner.tools[0].tool_id,'c110.open_learner_hub');
  assert.equal(c110.layers.learner.tools[0].href,'backend/c110/C110.html');
  assert.equal(c110.layers.curriculum.unit_identity_status,'verified');
  assert.equal(c110.layers.translation.ledger_status,'verified');
  assert.equal(c110.layers.translation.terminology_status,'verified');
  assert.equal(c110.layers.translation.rights_status,'verified');
  assert.equal(c110.layers.translation.corrections_status,'verified');
  assert.equal(c110.layers.production.build_status,'verified');
  assert.equal(c110.layers.production.deterministic_replay_status,'verified');
  assert.equal(c110.layers.educator.status,'verified');
  assert.equal(c110.layers.educator.unit_alignment_status,'verified');
  assert.ok(c110.layers.educator.resources.some(r=>r.id==='C110:educator-hub-v1'&&r.status==='verified'));
  assert.ok(c110.layers.educator.resources.some(r=>r.id==='C110:educator-map-v1'&&r.status==='verified'));
  assert.equal(c110.layers.learner.capabilities.semantic_html,'unknown');
  assert.equal(c110.layers.learner.capabilities.mathml,'unknown');
  const c70=courses.find(c=>c.course_id==='C70');
  assert.equal(c70.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(c70.layers.learner.tools.length,1);
  assert.equal(c70.layers.learner.tools[0].tool_id,'c70.open_learner_hub');
  assert.equal(c70.layers.learner.tools[0].href,'backend/c70/C70.html');
  assert.equal(c70.layers.curriculum.unit_identity_status,'verified');
  assert.equal(c70.layers.translation.ledger_status,'verified');
  assert.equal(c70.layers.translation.terminology_status,'verified');
  assert.equal(c70.layers.translation.rights_status,'verified');
  assert.equal(c70.layers.translation.corrections_status,'verified');
  assert.equal(c70.layers.production.build_status,'verified');
  assert.equal(c70.layers.production.deterministic_replay_status,'verified');
  assert.equal(c70.layers.educator.status,'verified');
  assert.equal(c70.layers.educator.unit_alignment_status,'verified');
  assert.ok(c70.layers.educator.resources.some(r=>r.id==='C70:educator-hub-v1'&&r.status==='verified'));
  assert.ok(c70.layers.educator.resources.some(r=>r.id==='C70:concept-index-v1'&&r.status==='verified'));
  assert.equal(c70.layers.learner.pdf.status,'verified');
  assert.equal(c70.layers.learner.online_html.status,'available_unverified');
  assert.equal(c70.layers.learner.capabilities.semantic_html,'verified');
  assert.equal(c70.layers.learner.capabilities.mathml,'unknown');
  for(const role of ['B70','C10','C20','C50']){
    const capsule=courses.find(c=>c.course_id===role);
    assert.equal(capsule.layers.interoperability.semantic_adapter.contract_version,'lebl-learning-capability/1');
    assert.equal(capsule.layers.learner.tools.length,3);
    assert.equal(capsule.layers.educator.unit_alignment_status,'verified');
  }
  const b80 = courses.find(course=>course.course_id==='B80');
  assert.equal(b80.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(b80.layers.curriculum.unit_identity_status,'verified');
  assert.equal(b80.layers.educator.unit_alignment_status,'verified');
  assert.equal(b80.layers.learner.tools.length,2);
  assert.equal(b80.layers.educator.resources[0].id,'B80:educator-map-v1');
  for (const [value, count] of [['published', 37], ['production', 3], ['educator', 29], ['adapter', adapterCount]]) {
    f.element('#state-filter').value = value;
    f.fire(f.element('#state-filter'), 'change');
    assert.equal(visibleCount(), count);
    if (value === 'adapter') assert.match(f.element('#course-grid').innerHTML, /data-course-id="D40"/);
  }
  f.fire(f.element('#reset-filters'), 'click');
  f.element('#level-filter').value = 'D';
  f.fire(f.element('#level-filter'), 'change');
  assert.equal(visibleCount(), courses.filter((course) => course.course.level === 'D').length);
  assert.equal(visibleCount(), 12);
  f.fire(f.element('#reset-filters'), 'click');
  f.element('#course-search').value = 'A20';
  f.fire(f.element('#course-search'), 'input');
  assert.equal(visibleCount(), 1);
  f.fire(f.element('#view-learner'), 'click');
  f.element('#course-search').value = 'C80';
  f.fire(f.element('#course-search'), 'input');
  assert.equal(visibleCount(), 1);
  assert.match(f.element('#course-grid').innerHTML, /href="\.\.\/backend\/openlogic\/C80\.html"/);
  assert.match(f.element('#course-grid').innerHTML, /Buka Open Logic lengkap/);
  assert.match(f.element('#course-grid').innerHTML, /class="learner-tool primary"/);
  f.element('#course-search').value = 'C130';
  f.fire(f.element('#course-search'), 'input');
  assert.equal(visibleCount(), 1);
  assert.match(f.element('#course-grid').innerHTML, /href="\.\.\/backend\/c130\/C130\.html"/);
  assert.match(f.element('#course-grid').innerHTML, /Buka Riset Operasi — Buku 1/);
  assert.match(f.element('#course-grid').innerHTML, /class="learner-tool primary"/);
  f.element('#course-search').value = 'zzzz_no_matching_course';
  f.fire(f.element('#course-search'), 'input');
  assert.equal(visibleCount(), 0);
  assert.match(f.element('#course-grid').innerHTML, /Tidak ada mata kuliah/);
  f.fire(f.element('#reset-filters'), 'click');
  assert.equal(visibleCount(), 40);
  for (const [name, count] of Object.entries({ total: 40, published: 37, production: 3, educator: 29 })) {
    assert.equal(Number(f.element('#summary-' + name).textContent), count);
    assert.match(html, new RegExp(`<strong id="summary-${name}">${count}</strong>`));
  }
  scenarios.push('success_all_views_filters_search_reset_and_public_evidence_links');
}
const educatorCounts = Object.fromEntries(['verified', 'available_unverified', 'in_progress', 'unknown'].map((status) => [status, courses.filter((course) => course.layers.educator.status === status).length]));
assert.deepEqual(educatorCounts, { verified: 16, available_unverified: 12, in_progress: 1, unknown: 11 });
console.log(JSON.stringify({
  state: 'pass', test_kind: 'actual_module_dom_stub_not_browser',
  source_sha256: createHash('sha256').update(source).digest('hex'),
  fallback_cards: 40, scenarios, educator_status_counts: educatorCounts,
}, null, 2));
