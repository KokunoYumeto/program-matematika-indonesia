import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const code = readFileSync(new URL('./topology-capability-controls-v1.js', import.meta.url), 'utf8');

function control(value = '') {
  return {
    value,
    textContent: '',
    events: {},
    addEventListener(name, listener) { this.events[name] = listener; },
  };
}

const names = [
  'query', 'chapter', 'module', 'kind', 'classification', 'status', 'record-type',
  'count', 'clear-filters', 'export-visible', 'export', 'export-status',
  'make-plan', 'clear-plan', 'plan', 'plan-status',
];
const controls = Object.fromEntries(names.map(name => [`#${name}`, control()]));

const stageUrls = {
  statement: 'https://example.test/knowl/theorem-a.html',
  hint: 'https://example.test/knowl/theorem-a-hint.html',
  answer: 'https://example.test/knowl/theorem-a-answer.html',
  solution: 'https://example.test/knowl/theorem-a-solution.html',
};

function row({id, text, dataset, plan, exported}) {
  const checkbox = {checked: false};
  const result = {
    id,
    textContent: text,
    hidden: false,
    dataset: {...dataset},
    checkbox,
    scrolls: 0,
    querySelector(selector) { return selector === '.choose' ? checkbox : null; },
    scrollIntoView() { this.scrolls += 1; },
  };
  if (plan !== undefined) result.dataset.plan = plan;
  if (exported !== undefined) result.dataset.export = exported;
  return result;
}

const rows = [
  row({
    id: 'theorem-a',
    text: 'Ruang terhubung dan lintasan',
    dataset: {chapter: '2', kind: 'theorem', classification: 'mastery', status: 'verified', recordType: 'entry'},
    plan: JSON.stringify({stage_urls: stageUrls, judul: 'Teorema A', id: 'theorem-a'}),
  }),
  row({
    id: 'completion-a',
    text: 'Latihan penyelesaian kompak',
    dataset: {completionModule: 'o003-module-1', kind: 'completion_mastery', classification: 'mastery', status: 'current', recordType: 'entry'},
    plan: JSON.stringify({title: 'Latihan penyelesaian', completion_module: 'o003-module-1', id: 'completion-a', stage_urls: {...stageUrls, statement: 'https://example.test/knowl/completion-a.html'}}),
  }),
  row({
    id: 'term-a',
    text: 'ruang topologis topology space',
    dataset: {status: 'verified', recordType: 'term'},
    exported: JSON.stringify({native: {status: 'verified', preferred_id_ID: 'ruang topologis'}, id: 'term-a'}),
  }),
  row({
    id: 'correction-a',
    text: 'Koreksi sumber belum terselesaikan',
    dataset: {status: 'unresolved', recordType: 'correction'},
    exported: '{"id":',
  }),
  row({
    id: 'broken-plan',
    text: 'Rekaman rencana rusak',
    dataset: {chapter: '3', kind: 'exercise', classification: 'source_support', status: 'current', recordType: 'entry'},
    plan: '[]',
  }),
];

const location = {hash: ''};
const globalEvents = {};
const document = {
  querySelector(selector) { return controls[selector] ?? null; },
  querySelectorAll(selector) { return selector === '.entry' ? rows : []; },
};

vm.runInNewContext(code, {
  document,
  location,
  addEventListener(name, listener) { globalEvents[name] = listener; },
});

assert.equal(rows.filter(item => !item.hidden).length, 5);
assert.equal(controls['#count'].textContent, '5 dari 5 rekaman ditampilkan.');

controls['#query'].value = 'RUANG';
controls['#query'].events.input();
assert.deepEqual(rows.map(item => item.hidden), [false, true, false, true, true]);

controls['#query'].value = '';
controls['#chapter'].value = '02';
controls['#chapter'].events.change();
assert.deepEqual(rows.map(item => item.hidden), [false, true, true, true, true]);

controls['#kind'].value = 'theorem';
controls['#kind'].events.input();
assert.equal(rows.filter(item => !item.hidden).length, 1);

controls['#clear-filters'].events.click();
controls['#module'].value = 'o003-module-1';
controls['#module'].events.input();
assert.deepEqual(rows.map(item => item.hidden), [true, false, true, true, true]);

controls['#clear-filters'].events.click();
controls['#record-type'].value = 'term';
controls['#status'].value = 'VERIFIED';
controls['#status'].events.change();
assert.deepEqual(rows.map(item => item.hidden), [true, true, false, true, true]);

controls['#export-visible'].events.click();
assert.deepEqual(JSON.parse(controls['#export'].value), [{id: 'term-a', native: {preferred_id_ID: 'ruang topologis', status: 'verified'}}]);
assert.match(controls['#export'].value, /^\[\n  \{\n    "id":/);
assert.match(controls['#export-status'].textContent, /^1 rekaman terlihat/);

controls['#record-type'].value = 'correction';
controls['#status'].value = 'unresolved';
controls['#status'].events.input();
controls['#export-visible'].events.click();
assert.deepEqual(JSON.parse(controls['#export'].value), []);
assert.match(controls['#export-status'].textContent, /1 rekaman rusak diabaikan/);

controls['#clear-filters'].events.click();
controls['#chapter'].value = '02';
controls['#chapter'].events.input();
rows[0].checkbox.checked = true;
rows[1].checkbox.checked = true;
controls['#make-plan'].events.click();
const plan = JSON.parse(controls['#plan'].value);
assert.deepEqual(plan.map(item => item.id), ['theorem-a', 'completion-a']);
assert.deepEqual(Object.keys(plan[0].stage_urls), ['answer', 'hint', 'solution', 'statement']);
assert.deepEqual(Object.values(plan[0].stage_urls).sort(), Object.values(stageUrls).sort());
assert.match(controls['#plan-status'].textContent, /1 tersembunyi oleh filter/);

rows[4].checkbox.checked = true;
controls['#make-plan'].events.click();
assert.deepEqual(JSON.parse(controls['#plan'].value).map(item => item.id), ['theorem-a', 'completion-a']);
assert.match(controls['#plan-status'].textContent, /1 pilihan tanpa rekaman rencana yang sah diabaikan/);

controls['#clear-plan'].events.click();
assert.ok(rows.every(item => !item.checkbox.checked));
assert.equal(controls['#plan'].value, '');

controls['#query'].value = 'tidak cocok';
controls['#query'].events.input();
location.hash = '#completion-a';
globalEvents.hashchange();
assert.equal(controls['#query'].value, '');
assert.ok(!rows[1].hidden);
assert.equal(rows[1].scrolls, 1);

location.hash = '#%broken';
globalEvents.hashchange();
assert.equal(rows[1].scrolls, 1);

assert.doesNotMatch(code, /\b(?:fetch|XMLHttpRequest|localStorage|sessionStorage|innerHTML|eval)\b/);

vm.runInNewContext(code, {
  document: {querySelector: () => null, querySelectorAll: () => []},
});

console.log(JSON.stringify({state: 'pass', scenarios: 16, real_shipped_script: true, browser_qa: false}));
