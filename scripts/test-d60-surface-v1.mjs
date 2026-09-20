import assert from 'node:assert/strict';
import {mkdtemp, readFile, readdir, rm, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve, sep} from 'node:path';
import vm from 'node:vm';
import {base, build, json, loadInputs, project, projectMap, sha256} from './build-d60-surface-v1.mjs';

const inputs = await loadInputs(), map = projectMap(inputs);
assert.equal(map.units.length, 2204);
assert.equal(map.counts.exact_routes, 2166);
assert.equal(map.counts.fallback_routes, 38);
assert.equal(map.counts.practice_units, 278);
assert.equal(map.counts.support_relations, 480);
assert.equal(map.counts.unresolved_support_relations, 0);
assert.deepEqual(map.prerequisites, ['C30', 'C90']);
const byId = new Map(map.units.map(u => [u.id, u]));
const sourceById = new Map(inputs.units.map(r => [r.payload.native_unit_id, r]));
for (const u of map.units) {
  const source = sourceById.get(u.id);
  assert.equal(u.projected_id, source.id);
  assert.deepEqual(u.source_locator, source.payload.target_locator);
  assert.deepEqual(u.rights_ids, source.payload.current_rights_native_ids);
  assert.equal(u.title, source.payload.title);
  assert.equal(u.translation_state, source.payload.translation_state);
  const witness = inputs.witness.unit_routes.find(r => r.id === u.id);
  assert.equal(u.route.url, inputs.witness.reader.url + (witness.occurrences === 1 ? '#' + witness.anchor : ''));
  for (const [type, rows] of Object.entries(u.support)) for (const row of rows) {
    const relation = inputs.relations.find(r => r.id === row.relation_id).payload;
    assert.equal(relation.relation_type, type);
    assert.equal(relation.from_native_id, row.unit_id);
    assert.equal(relation.to_native_id, u.id);
    assert.ok(byId.has(row.unit_id));
  }
}
assert.equal(byId.get('unit:o012-d60-capstone-rev3').route.anchor, 'o012-d60-capstone');
assert.equal(map.units.filter(u => /^unit:o012-d60-lab0[1-4]$/.test(u.id)).length, 4);
assert.equal(map.units.some(u => u.id === 'unit:o012-d60-capstone-rev2'), false);
const negative = [];
function reject(name, mutate) {
  const changed = structuredClone(inputs); mutate(changed);
  assert.throws(() => projectMap(changed), undefined, name); negative.push({name, result: 'rejected'});
}
reject('duplicate_projected_id', x => {x.units[1].id = x.units[0].id;});
reject('duplicate_native_id', x => {x.units[1].payload.native_unit_id = x.units[0].payload.native_unit_id;});
reject('missing_witness', x => {x.witness.unit_routes.pop();});
reject('duplicate_witness', x => {x.witness.unit_routes[1] = x.witness.unit_routes[0];});
reject('unsafe_anchor', x => {x.witness.unit_routes[0].anchor = 'x" onclick="alert(1)';});
reject('wrong_content_language', x => {x.witness.reader.language = 'en';});
reject('wrong_support_identity', x => {x.relations.find(r => r.payload.relation_type === 'solves').payload.from_projected_id = 'wrong';});
reject('unproven_support', x => {x.relations.find(r => r.payload.relation_type === 'hints').payload.evidence_state = 'guessed';});
const ambiguous = structuredClone(inputs); ambiguous.witness.unit_routes[0].occurrences = 2;
assert.equal(projectMap(ambiguous).units.find(u => u.id === ambiguous.witness.unit_routes[0].id).route.state, 'course_fallback');
const missing = structuredClone(inputs); missing.relations.find(r => r.payload.relation_type === 'solves').payload.to_native_id = 'missing';
assert.equal(projectMap(missing).unresolved_support_relations.length, 1);

const uiSource = await readFile(resolve(project, 'scripts/d60-surface/d60-ui.js'), 'utf8');
const context = vm.createContext({}); vm.runInContext(uiSource, context);
const api = context.D60_PLAN_API;
assert.equal(api.filterUnits(map, '', 'practice').length, 278);
assert.equal(api.filterUnits(map, 'klein').length > 0, true);
assert.equal(api.filterUnits(map, 'impossible-no-such-unit').length, 0);
const selected = map.units.filter(u => u.practice).map(u => u.id);
const plan = JSON.parse(JSON.stringify(api.makePlan(map, selected, 'en')));
assert.deepEqual(plan.units.map(u => u.id), selected);
assert.equal(plan.units.length, 278);
assert.equal(plan.content_locale, 'id-ID');
assert.equal(plan.interface_locale, 'en');
assert.equal(plan.offline_book_included, false);
const supportIds = new Set(plan.units.flatMap(u => Object.values(u.support).flat().map(r => r.unit_id)));
assert.deepEqual(new Set(plan.supporting_units.map(u => u.id)), supportIds);
assert.throws(() => api.makePlan(map, ['unknown'], 'id'));
assert.equal(api.makePlan(map, [], 'id').units.length, 0);
assert.equal(api.makePlan(map, [selected[0], selected[0]], 'id').units.length, 1);
const canonical = resolve(project, 'docs/backend/d60');
const tempParent = resolve(tmpdir()), tmp = await mkdtemp(join(tempParent, 'd60-replay-'));
assert.ok(tmp.startsWith(tempParent + sep));
const replay = [];
try {
  await build(join(tmp, 'a')); await build(join(tmp, 'b'));
  for (const file of await readdir(join(tmp, 'a'))) {
    const a = await readFile(join(tmp, 'a', file)), b = await readFile(join(tmp, 'b', file)), c = await readFile(join(canonical, file));
    assert.deepEqual(a, b, `Replay ${file}`); assert.deepEqual(a, c, `Canonical drift ${file}`);
    replay.push({path: file, bytes: a.length, sha256: sha256(a)});
  }
} finally {
  assert.ok(tmp.startsWith(tempParent + sep)); await rm(tmp, {recursive: true, force: true});
}
for (const file of ['D60.html', 'D60.en.html', 'D60-pengajar.html', 'D60-pengajar.en.html']) {
  const html = await readFile(join(canonical, file), 'utf8');
  assert.ok(html.includes('<noscript>'));
  assert.equal(html.includes('data-program-home'), false, 'Source view must not impersonate the shared navigation shell');
  assert.ok(html.includes('id="workbench" hidden'));
  assert.ok(html.includes('connect-src &#') === false);
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]); assert.equal(ids.length, new Set(ids).size);
  assert.equal(html.includes('#o012-d60-ca02-ca03-status">Capstone'), false);
  assert.ok(html.includes('#o012-d60-capstone'));
}
const receipt = {schema: 'd60-independent-tests/1', state: 'pass', counts: map.counts,
  negative_fixtures: negative, ambiguous_anchor_fallback: true, missing_support_kept_explicit: true,
  all_practice_plan_roundtrip: {units: plan.units.length, supporting_units: plan.supporting_units.length},
  deterministic_replay: {builds: 2, canonical_comparison: true, outputs: replay},
  scope: 'Data joins, plan/filter behavior and deterministic output. Browser checks recorded separately.'};
await writeFile(resolve(project, base, 'tests.json'), json(receipt));
console.log(json({state: 'pass', units: map.units.length, practice_plan: receipt.all_practice_plan_roundtrip, negative_fixtures: negative.length, replay_files: replay.length}));
