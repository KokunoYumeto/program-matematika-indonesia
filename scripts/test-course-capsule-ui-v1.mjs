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
const integrationOverrides = JSON.parse(await readFile(resolve(project, 'backend/course-capsule-v1/authority/integration-overrides-v1.json'), 'utf8'));
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
  const expectedAdapterCount = Object.values(integrationOverrides.semantic_adapters)
    .filter((adapter) => ['verified', 'legacy_verified', 'available_unverified'].includes(adapter.status)).length;
  assert.equal(adapterCount, expectedAdapterCount);
  const a10 = courses.find(course => course.course_id === 'A10');
  assert.equal(a10.layers.interoperability.semantic_adapter.status, 'verified');
  assert.equal(a10.layers.interoperability.semantic_adapter.contract_version, '2.3.1');
  assert.equal(a10.layers.interoperability.semantic_adapter.mapping_scope, 'capsule_only');
  assert.deepEqual(
    a10.layers.interoperability.semantic_adapter.evidence.map(({ kind }) => kind),
    [
      'central_adapter_manifest',
      'package_seal',
      'deterministic_generic_validation_receipt',
      'a10_semantic_validation_receipt',
      'public_release_authority',
    ],
  );
  assert.equal(a10.layers.curriculum.unit_identity_status, 'unknown');
  assert.equal(a10.layers.translation.ledger_status, 'unknown');
  assert.equal(a10.layers.translation.terminology_status, 'in_progress');
  assert.equal(a10.layers.translation.rights_status, 'unknown');
  assert.equal(a10.layers.translation.corrections_status, 'in_progress');
  assert.equal(a10.layers.production.build_status, 'unknown');
  assert.equal(a10.layers.production.deterministic_replay_status, 'unknown');
  const a20 = courses.find(course => course.course_id === 'A20');
  assert.equal(a20.layers.interoperability.semantic_adapter.status, 'verified');
  assert.equal(a20.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
  assert.match(a20.layers.interoperability.semantic_adapter.mapping_scope, /174535_native_records/);
  assert.match(a20.layers.interoperability.semantic_adapter.mapping_scope, /2971_unsolved_exercises_preserved/);
  assert.equal(a20.layers.learner.tools.length, 1);
  assert.equal(a20.layers.learner.tools[0].tool_id, 'a20.open_learner_hub');
  assert.equal(a20.layers.learner.tools[0].href, 'backend/a20/A20.html');
  assert.equal(a20.layers.curriculum.unit_identity_status, 'verified');
  assert.equal(a20.layers.translation.ledger_status, 'verified');
  assert.equal(a20.layers.translation.terminology_status, 'verified');
  assert.equal(a20.layers.translation.rights_status, 'verified');
  assert.equal(a20.layers.translation.corrections_status, 'verified');
  assert.equal(a20.layers.production.build_status, 'verified');
  assert.equal(a20.layers.production.deterministic_replay_status, 'verified');
  assert.equal(a20.layers.educator.status, 'verified');
  assert.equal(a20.layers.educator.unit_alignment_status, 'verified');
  assert.equal(a20.layers.educator.resources.length, 10);
  assert.ok(a20.layers.educator.resources.some(r=>r.id==='A20:educator-hub-v1'&&r.status==='verified'));
  assert.ok(a20.layers.educator.resources.some(r=>r.id==='A20:exercise-index-v1'&&r.status==='verified'));
  assert.equal(a20.layers.learner.pdf.status, 'verified');
  assert.equal(a20.layers.learner.pdf.bytes, 412049461);
  assert.equal(a20.layers.learner.pdf.sha256, '76276eeab590cd8181fd531378c4b4860bf30289a5e8093c9af5788d1eca3a9c');
  assert.equal(a20.layers.learner.online_html.status, 'not_yet_produced');
  assert.equal(a20.layers.learner.capabilities.semantic_html, 'not_yet_produced');
  assert.equal(a20.layers.learner.capabilities.mathml, 'not_yet_produced');
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
  const d30=courses.find(c=>c.course_id==='D30');
  assert.equal(d30.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(d30.layers.interoperability.semantic_adapter.status,'verified');
  assert.equal(d30.layers.learner.tools.length,1);
  assert.equal(d30.layers.learner.tools[0].tool_id,'d30.open_learner_hub');
  assert.equal(d30.layers.learner.tools[0].href,'backend/d30/D30.html');
  assert.equal(d30.layers.learner.tools[0].page.path,'docs/backend/d30/D30.html');
  assert.equal(d30.layers.learner.tools[0].resource.path,'docs/backend/d30/learning-map.json');
  assert.equal(d30.layers.learner.tools[0].evidence.path,'docs/backend/d30/validation.json');
  assert.match(d30.layers.learner.tools[0].scope,/57/);
  assert.match(d30.layers.learner.tools[0].scope,/36/);
  assert.match(d30.layers.learner.tools[0].scope,/dua formulir/);
  assert.equal(d30.layers.curriculum.unit_identity_status,'verified');
  assert.equal(d30.layers.translation.ledger_status,'verified');
  assert.equal(d30.layers.translation.terminology_status,'verified');
  assert.equal(d30.layers.translation.rights_status,'verified');
  assert.equal(d30.layers.translation.corrections_status,'verified');
  assert.equal(d30.layers.production.build_status,'verified');
  assert.equal(d30.layers.production.deterministic_replay_status,'verified');
  assert.equal(d30.layers.educator.status,'verified');
  assert.equal(d30.layers.educator.unit_alignment_status,'verified');
  assert.equal(d30.layers.educator.resources.length,7);
  assert.ok(d30.layers.educator.resources.some(r=>r.id==='D30:native-educator-observation'&&r.status==='available_unverified'&&r.url==='https://zenodo.org/records/22182655'));
  for(const resourceId of ['D30:educator-hub-v1','D30:educator-map-v1','D30:terms-index-v1','D30:rights-index-v1','D30:corrections-index-v1','D30:relations-index-v1']) {
    assert.ok(d30.layers.educator.resources.some(r=>r.id===resourceId&&r.status==='verified'));
  }
  assert.equal(d30.layers.learner.primary.url,'https://kokunoyumeto.github.io/measure-theoretic-probability-stochastic-processes-id/');
  assert.equal(d30.layers.learner.portable_html.status,'verified');
  assert.equal(d30.layers.learner.portable_html.sha256,'e32dba5a896fb847192bbe944e7fd3db4d95f61ee57e33751bbff3108fca214a');
  assert.equal(d30.layers.learner.capabilities.semantic_html,'verified');
  assert.equal(d30.layers.learner.capabilities.mathml,'available_unverified');
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
  const c60=courses.find(c=>c.course_id==='C60');
  assert.equal(c60.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(c60.layers.learner.tools.length,1);
  assert.equal(c60.layers.learner.tools[0].tool_id,'c60.open_learner_hub');
  assert.equal(c60.layers.learner.tools[0].href,'backend/c60/C60.html');
  assert.equal(c60.layers.curriculum.unit_identity_status,'verified');
  assert.equal(c60.layers.translation.ledger_status,'verified');
  assert.equal(c60.layers.translation.terminology_status,'verified');
  assert.equal(c60.layers.translation.rights_status,'verified');
  assert.equal(c60.layers.translation.corrections_status,'verified');
  assert.equal(c60.layers.production.build_status,'verified');
  assert.equal(c60.layers.production.deterministic_replay_status,'verified');
  assert.equal(c60.layers.educator.status,'verified');
  assert.equal(c60.layers.educator.unit_alignment_status,'verified');
  assert.equal(c60.layers.educator.resources.length,7);
  assert.ok(c60.layers.educator.resources.some(r=>r.id==='C60:educator-hub-v1'&&r.status==='verified'));
  assert.ok(c60.layers.educator.resources.some(r=>r.id==='C60:native-id-index-v1'&&r.status==='verified'));
  assert.equal(c60.layers.learner.pdf.status,'verified');
  assert.equal(c60.layers.learner.pdf.sha256,'1ded3c6844b656347259b464bf21526fdc32dc2246c73ac58ab76ed28688eefc');
  assert.equal(c60.layers.learner.epub.status,'not_yet_produced');
  assert.equal(c60.layers.learner.portable_html.status,'not_yet_produced');
  assert.equal(c60.layers.learner.capabilities.semantic_html,'verified');
  assert.equal(c60.layers.learner.capabilities.mathml,'verified');
  const d90=courses.find(c=>c.course_id==='D90');
  assert.equal(d90.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(d90.layers.learner.tools.length,1);
  assert.equal(d90.layers.learner.tools[0].tool_id,'d90.open_learner_hub');
  assert.equal(d90.layers.learner.tools[0].href,'backend/d90/D90.html');
  assert.equal(d90.layers.curriculum.unit_identity_status,'verified');
  assert.equal(d90.layers.translation.ledger_status,'verified');
  assert.equal(d90.layers.translation.terminology_status,'verified');
  assert.equal(d90.layers.translation.rights_status,'verified');
  assert.equal(d90.layers.translation.corrections_status,'verified');
  assert.equal(d90.layers.production.build_status,'verified');
  assert.equal(d90.layers.production.deterministic_replay_status,'verified');
  assert.equal(d90.layers.educator.status,'verified');
  assert.equal(d90.layers.educator.unit_alignment_status,'verified');
  assert.ok(d90.layers.educator.resources.some(r=>r.id==='D90:native-educator-observation'&&r.status==='available_unverified'));
  assert.ok(d90.layers.educator.resources.some(r=>r.id==='D90:educator-hub-v1'&&r.status==='verified'));
  assert.ok(d90.layers.educator.resources.some(r=>r.id==='D90:educator-map-v1'&&r.status==='verified'));
  assert.equal(d90.layers.learner.pdf.status,'verified');
  assert.equal(d90.layers.learner.pdf.sha256,'9deefecf469c9f2aace26bc8ccdedc552debbe9874ae035badaf5cffee0f80e5');
  assert.equal(d90.layers.learner.epub.status,'verified');
  assert.equal(d90.layers.learner.epub.sha256,'1bb882a75209adb220de4ee6c6cf92355b5402538c88050e807dc161fa5d9321');
  assert.equal(d90.layers.learner.capabilities.semantic_html,'verified');
  assert.equal(d90.layers.learner.capabilities.mathml,'verified');
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
  assert.equal(c110.layers.learner.capabilities.semantic_html,'not_yet_produced');
  assert.equal(c110.layers.learner.capabilities.mathml,'not_yet_produced');
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
  assert.equal(c70.layers.learner.capabilities.mathml,'not_yet_produced');
  const b40=courses.find(c=>c.course_id==='B40');
  assert.equal(b40.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
  assert.equal(b40.layers.learner.tools.length,1);
  assert.equal(b40.layers.learner.tools[0].tool_id,'b40.open_learner_hub');
  assert.equal(b40.layers.learner.tools[0].href,'backend/b40/B40.html');
  assert.equal(b40.layers.curriculum.unit_identity_status,'verified');
  assert.equal(b40.layers.translation.ledger_status,'verified');
  assert.equal(b40.layers.translation.terminology_status,'verified');
  assert.equal(b40.layers.translation.rights_status,'verified');
  assert.equal(b40.layers.translation.corrections_status,'verified');
  assert.equal(b40.layers.production.build_status,'verified');
  assert.equal(b40.layers.production.deterministic_replay_status,'verified');
  assert.equal(b40.layers.educator.status,'verified');
  assert.equal(b40.layers.educator.unit_alignment_status,'verified');
  assert.ok(b40.layers.educator.resources.some(r=>r.id==='B40:educator-hub-v1'&&r.status==='verified'));
  assert.ok(b40.layers.educator.resources.some(r=>r.id==='B40:educator-map-v1'&&r.status==='verified'));
  assert.equal(b40.layers.learner.pdf.status,'verified');
  assert.equal(b40.layers.learner.pdf.bytes,8984459);
  assert.equal(b40.layers.learner.pdf.sha256,'0462ddc8ffcc901efbc81205f79a249ae716e838a6ec32eda033444a90b8755e');
  assert.equal(b40.layers.learner.online_html.status,'available_unverified');
  assert.equal(b40.layers.learner.online_html.scope,'release_landing_page_not_full_html_textbook');
  assert.equal(b40.layers.learner.capabilities.semantic_html,'not_yet_produced');
  assert.equal(b40.layers.learner.capabilities.mathml,'not_yet_produced');
  assert.equal(b40.layers.learner.capabilities.print_profile,'verified');
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
  for (const [value, count] of [['published', 37], ['production', 3], ['educator', 32], ['adapter', adapterCount]]) {
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
  for (const [name, count] of Object.entries({ total: 40, published: 37, production: 3, educator: 32 })) {
    assert.equal(Number(f.element('#summary-' + name).textContent), count);
    assert.match(html, new RegExp(`<strong id="summary-${name}">${count}</strong>`));
  }
  scenarios.push('success_all_views_filters_search_reset_and_public_evidence_links');
}
const educatorCounts = Object.fromEntries(['verified', 'available_unverified', 'in_progress', 'unknown'].map((status) => [status, courses.filter((course) => course.layers.educator.status === status).length]));
assert.deepEqual(educatorCounts, { verified: 22, available_unverified: 9, in_progress: 1, unknown: 8 });
console.log(JSON.stringify({
  state: 'pass', test_kind: 'actual_module_dom_stub_not_browser',
  source_sha256: createHash('sha256').update(source).digest('hex'),
  fallback_cards: 40, scenarios, educator_status_counts: educatorCounts,
}, null, 2));
