import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const source = await readFile(new URL('./d110-ui.js', import.meta.url), 'utf8');
const context = vm.createContext({});
vm.runInContext(source, context);
const api = context.D110_PLAN_API;
const plain = value => JSON.parse(JSON.stringify(value));
const baseURL = 'https://kokunoyumeto.github.io/';
const unit = (id, kind, practice = false) => ({
  id, kind, practice, chapter_id: 'urn:mil:chapter:01', section_id: 'urn:mil:section:01.01',
  title: {id: 'Unit Indonesia ' + id, en: 'English unit ' + id},
  reader_routes: {
    id: {url: baseURL + 'mathematics-in-lean-id/C01.html#section', anchor: 'section', state: 'section_context'},
    en: {url: baseURL + 'program-matematika-indonesia/en/courses/D110/C01.html#section', anchor: 'section', state: 'section_context'}
  },
  source_reference: {url: 'https://github.com/leanprover-community/mathematics_in_lean/blob/f00/MIL/C01.lean#L1', state: 'pinned_file', language: 'en'},
  source_locator: {path: 'MIL/C01.lean', line_start: 1, line_end: 7, file_sha256: 'a'.repeat(64)},
  rights_ids: ['urn:mil:rights:code'], concept_ids: ['urn:mil:concept:logic'], code: null,
  supports: [], supporting: [], companion: false,
  source_record: {id, data: {statement_signature: 'PRIVATE_SIGNATURE_FOR_EXPORT_ONLY'}}
});
const chapter = {id: 'urn:mil:chapter:01', title: {id: 'Bab satu', en: 'Chapter one'}};
const section = unit('urn:mil:section:01.01', 'section');
const exercise = unit('urn:mil:exercise:C01/S01:17', 'exercise', true);
const instance = unit('urn:mil:instance:C01/S01:18', 'instance', true);
const nativeExercise = unit('urn:mil:exercise:not-practice', 'exercise', false);
const solutionA = unit('urn:mil:solution:A', 'solution');
const solutionB = unit('urn:mil:solution:B', 'solution');
const declaration = unit('urn:mil:support:lemma', 'solution_support');
solutionA.code = {id: 'exact FIRST_SOLUTION_CODE\n', en: 'exact FIRST_SOLUTION_CODE\n', sha256: {id: 'b'.repeat(64), en: 'b'.repeat(64)}};
solutionB.code = {id: 'exact SECOND_SOLUTION_CODE\n', en: 'exact SECOND_SOLUTION_CODE\n', sha256: {id: 'c'.repeat(64), en: 'c'.repeat(64)}};
exercise.code = {id: 'example := by\n  sorry\n', en: 'example := by\n  sorry\n', sha256: {id: 'd'.repeat(64), en: 'd'.repeat(64)}};
const relation = (id, support, target, kind = 'solves', data = {}) => ({
  relation_id: id, id: support.id, kind, target_id: target.id,
  source_record: {id, kind, data}
});
exercise.supports = [
  relation('rel:A:1', solutionA, exercise, 'solves', {hole_rank: 1, solved_hole_count: 1, is_alternative: false}),
  relation('rel:A:2', solutionA, exercise, 'solves', {hole_ranks: [2, 3], is_alternative: true}),
  relation('rel:B:1', solutionB, exercise)
];
exercise.supporting = [solutionA.id, solutionB.id];
instance.supports = [relation('rel:A:instance', solutionA, instance)];
instance.supporting = [solutionA.id];
solutionA.supports = [relation('rel:lemma:A', declaration, solutionA, 'supports')];
solutionA.supporting = [declaration.id];
const map = {
  schema: 'd110-study-map/1', course_id: 'D110',
  input_identity: {source: {path: 'native-units.jsonl', sha256: 'f'.repeat(64)}}, counts: {},
  chapters: [chapter], sections: [{...section, routes: section.reader_routes}],
  units: [section, exercise, instance, nativeExercise, solutionA, solutionB, declaration,
    ...Array.from({length: 35}, (_, index) => unit('urn:mil:example:' + index, 'example'))],
  limitations: {id: ['Konteks bacaan bukan kesepadanan setiap unit kode.'], en: ['Reading context is not individual code equivalence.']}
};

assert.deepEqual(Object.keys(api).sort(), ['filterUnits', 'makePlan']);
assert.deepEqual(plain(api.filterUnits(map, '', 'practice').map(row => row.id)), [exercise.id, instance.id]);
assert.equal(api.filterUnits(map, '', 'exercise').length, 2);
assert.equal(api.filterUnits(map, exercise.id).length, 1, 'A complete punctuation-rich ID must be searchable.');
assert.equal(api.filterUnits(map, 'INDONESIA').length, map.units.length);
assert.equal(api.filterUnits(map, 'logic', '', chapter.id).length, map.units.length);
assert.equal(api.filterUnits(map, '', '', 'unknown-chapter').length, 0);
assert.equal(api.filterUnits(map, 'nonexistent-needle').length, 0);
assert.throws(() => api.filterUnits(map, null), /Search must/);

const before = JSON.stringify(map);
const plan = plain(api.makePlan(map, [instance.id, exercise.id, exercise.id], 'en'));
assert.deepEqual(plan.units, [exercise, instance]);
assert.deepEqual(plan.supporting_units, [solutionA, solutionB, declaration]);
assert.deepEqual(plan.units[0].supports, exercise.supports, 'Distinct relations sharing a source must all survive.');
assert.deepEqual(plan.input_identity, map.input_identity);
assert.deepEqual(plan.limitations, map.limitations.en);
assert.equal(plan.interface_locale, 'en');
assert.equal(plan.reader_locale, 'en');
assert.equal(plan.offline_book_included, false);
assert.equal(plan.offline_lean_environment_included, false);
assert.equal(plan.answers_generated, false);
assert.equal(plan.reader_links_require_network, true);
assert.equal(plan.supporting_units[2].code, null, 'A source-only supporting declaration must survive.');
assert.equal(JSON.stringify(map), before, 'Planning and searching must not mutate source data.');
assert.equal(JSON.stringify(api.makePlan(map, [exercise.id, instance.id], 'en')), JSON.stringify(api.makePlan(map, new Set([instance.id, exercise.id]), 'en')), 'Export must not depend on selection insertion order.');
assert.equal(api.makePlan(map, exercise.id, 'id').units[0].id, exercise.id, 'A full ID string must not be split into characters.');
assert.equal(api.makePlan(map, [], 'id').units.length, 0);
assert.equal(api.makePlan(map, [exercise.id, solutionA.id], 'id').supporting_units.some(row => row.id === solutionA.id), false);
assert.throws(() => api.makePlan(map, ['unknown-id'], 'id'), /Unknown unit/);
assert.throws(() => api.makePlan(map, [exercise.id.slice(0, -1)], 'id'), /Unknown unit/);
assert.throws(() => api.makePlan(map, [null], 'id'), /Unknown unit/);
for (const locale of ['fr', 'en-US', 'id-ID', '', undefined]) assert.throws(() => api.makePlan(map, [], locale), /Unsupported interface locale/);
for (const selection of [null, {}, 3]) assert.throws(() => api.makePlan(map, selection, 'en'), /Selection must/);
assert.throws(() => api.makePlan({...map, course_id: 'D60'}, [], 'id'), /Expected the D110/);
assert.throws(() => api.makePlan({...map, units: [...map.units, exercise]}, [], 'id'), /duplicate unit/);
const missing = structuredClone(map);
missing.units[1].supporting.push('missing-support');
assert.throws(() => api.makePlan(missing, [exercise.id], 'en'), /Unknown support dependency/);
const wrongTarget = structuredClone(map);
wrongTarget.units[1].supports[0].target_id = instance.id;
assert.throws(() => api.makePlan(wrongTarget, [exercise.id], 'en'), /identity mismatch/);
const cyclic = structuredClone(map);
cyclic.units[6].supporting = [solutionA.id];
cyclic.units[6].supports = [relation('rel:cycle', solutionA, declaration, 'supports')];
assert.deepEqual(plain(api.makePlan(cyclic, [exercise.id], 'en').supporting_units.map(row => row.id)), [solutionA.id, solutionB.id, declaration.id]);

// Minimal DOM harness exercises event behavior without executing network requests.
class Element {
  constructor(tagName) {
    this.tagName = tagName; this.children = []; this.events = {}; this.attributes = {};
    this.value = ''; this._text = ''; this.className = ''; this.disabled = false;
  }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map(child => child.textContent).join(''); }
  append(...children) { this.children.push(...children); children.forEach(child => { child.parent = this; }); }
  replaceChildren(...children) { this._text = ''; this.children = []; this.append(...children); }
  setAttribute(name, value) { this.attributes[name] = value; }
  addEventListener(name, listener) { (this.events[name] ||= []).push(listener); }
  emit(name) { for (const listener of this.events[name] || []) listener(); }
  click() { this.emit('click'); }
  remove() { if (this.parent) this.parent.children = this.parent.children.filter(child => child !== this); }
}
const descendants = node => [node, ...node.children.flatMap(descendants)];
function mount(data = map, language = 'en', mode = 'teacher') {
  const nodes = new Map(['search', 'kind', 'chapter', 'unit-list', 'results-status', 'previous', 'next', 'select-page', 'clear', 'export', 'export-text', 'selection', 'workbench'].map(id => [id, new Element('div')]));
  const body = new Element('body');
  body.dataset = {language, mode};
  for (const node of nodes.values()) body.append(node);
  const downloads = [];
  class LocalURL extends URL {
    static createObjectURL(blob) { downloads.push(blob); return 'blob:test-' + downloads.length; }
    static revokeObjectURL() {}
  }
  vm.runInContext(source, vm.createContext({
    D110_DATA: data, document: {body, getElementById: id => nodes.get(id) || null, createElement: tag => new Element(tag)},
    URL: LocalURL, Blob, setTimeout: callback => callback()
  }));
  return {nodes, body, downloads};
}
const ui = mount();
assert.equal(ui.nodes.get('kind').value, 'practice');
assert.equal(ui.nodes.get('unit-list').children.length, 2, 'The instance practice unit is rendered.');
assert.equal(ui.nodes.get('export').disabled, true);
assert.equal(ui.body.textContent.includes('FIRST_SOLUTION_CODE'), false);
assert.equal(ui.body.textContent.includes('PRIVATE_SIGNATURE_FOR_EXPORT_ONLY'), false);
const firstCard = ui.nodes.get('unit-list').children[0];
const checkbox = descendants(firstCard).find(node => node.tagName === 'input');
assert.ok(checkbox.attributes['aria-label'].includes(exercise.id));
checkbox.checked = true; checkbox.emit('change');
assert.equal(ui.nodes.get('export').disabled, false);
const details = descendants(firstCard).find(node => node.className === 'solutions');
assert.ok(details);
assert.ok(!details.open);
assert.equal(ui.body.textContent.includes('FIRST_SOLUTION_CODE'), false, 'Selecting alone does not reveal solutions.');
details.open = true; details.emit('toggle');
assert.ok(details.textContent.includes('FIRST_SOLUTION_CODE'));
assert.ok(details.textContent.includes('SECOND_SOLUTION_CODE'));
assert.ok(details.textContent.includes('Proof-hole rank: 1'));
assert.ok(details.textContent.includes('Proof-hole ranks: 2, 3'));
assert.ok(details.textContent.includes('Recorded alternative: yes'));
assert.equal(ui.body.textContent.includes('PRIVATE_SIGNATURE_FOR_EXPORT_ONLY'), false, 'Raw source statements remain export-only.');
const supportCount = details.children.length;
details.open = false; details.emit('toggle'); details.open = true; details.emit('toggle');
assert.equal(details.children.length, supportCount, 'Reopening must not duplicate solution blocks.');
const englishReaderLinks = descendants(ui.body).filter(node => node.tagName === 'a' && node.textContent.includes('English reader'));
assert.ok(englishReaderLinks.length);
assert.ok(englishReaderLinks.every(node => node.href.includes('/en/courses/D110/')));
ui.nodes.get('export').click(); ui.nodes.get('export').click();
assert.equal(await ui.downloads[0].text(), await ui.downloads[1].text(), 'Repeated JSON export is byte-deterministic.');
assert.deepEqual(JSON.parse(await ui.downloads[0].text()), plain(api.makePlan(map, [exercise.id], 'en')));
ui.nodes.get('export-text').click(); ui.nodes.get('export-text').click();
const textExport = await ui.downloads[2].text();
assert.equal(textExport, await ui.downloads[3].text(), 'Repeated text export is byte-deterministic.');
assert.ok(textExport.includes('Original English source location:'));
assert.ok(textExport.includes('PRIVATE_SIGNATURE_FOR_EXPORT_ONLY'), 'The export retains the full source record.');
assert.ok(textExport.includes(declaration.id));
assert.ok(textExport.includes(solutionA.code.en), 'Exact source code including its line break survives.');

ui.nodes.get('kind').value = ''; ui.nodes.get('kind').emit('change');
assert.equal(ui.nodes.get('unit-list').children.length, 30);
assert.equal(ui.nodes.get('previous').disabled, true);
ui.nodes.get('next').click();
assert.equal(ui.nodes.get('unit-list').children.length, map.units.length - 30);
assert.equal(ui.nodes.get('next').disabled, true);
ui.nodes.get('search').value = exercise.id; ui.nodes.get('search').emit('input');
assert.equal(ui.nodes.get('unit-list').children.length, 1);
assert.equal(descendants(ui.nodes.get('unit-list')).find(node => node.tagName === 'input').checked, true, 'Selection survives filters and pagination.');
ui.nodes.get('clear').click();
assert.equal(ui.nodes.get('export').disabled, true);
assert.equal(ui.body.textContent.includes('FIRST_SOLUTION_CODE'), false, 'Clearing removes revealed solution content.');
ui.nodes.get('kind').value = 'solution'; ui.nodes.get('search').value = ''; ui.nodes.get('kind').emit('change');
assert.equal(ui.body.textContent.includes('FIRST_SOLUTION_CODE'), false, 'Browsing the native solution kind never reveals solution content.');

const idUI = mount(map, 'id', 'learner');
assert.equal(idUI.nodes.get('kind').value, 'section');
assert.ok(idUI.body.textContent.includes('Buka pembaca bahasa Indonesia'));
idUI.nodes.get('select-page').click(); idUI.nodes.get('export-text').click();
assert.ok((await idUI.downloads[0].text()).startsWith('Rencana belajar D110\n'));
const unsafe = structuredClone(map);
unsafe.units[0].reader_routes.en.url = 'javascript:alert(1)';
unsafe.units[0].source_reference.url = 'https://github.com.attacker.invalid/path';
const unsafeUI = mount(unsafe, 'en', 'learner');
assert.equal(descendants(unsafeUI.body).filter(node => node.tagName === 'a').length, 0);
assert.ok(unsafeUI.body.textContent.includes('address validation failed'));
assert.equal(/\b(fetch|XMLHttpRequest|localStorage|sessionStorage)\s*\(/.test(source), false);
assert.equal(source.includes('.innerHTML'), false);

console.log(JSON.stringify({state: 'pass', api: ['filterUnits', 'makePlan'], fixture_units: map.units.length,
  checks: ['full IDs and locale rejection', 'practice flags', 'recursive source closure and cycle safety',
    'support multiplicity and full provenance', 'deterministic JSON and text', '30-row pagination',
    'deferred solution disclosure', 'English reader routing', 'unsafe-link rejection', 'localized controls']}, null, 2));
