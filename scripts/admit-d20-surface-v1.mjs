import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {base, json, project, sha256} from './build-d20-surface-v1.mjs';

const load = async path => JSON.parse(await readFile(resolve(project, path), 'utf8'));
const identity = async path => {const b = await readFile(resolve(project, path)); return {path, bytes: b.length, sha256: sha256(b)};};
const tests = await load(`${base}/tests.json`);
assert.equal(tests.state, 'pass');
assert.equal(tests.counts.units, 1960);
assert.equal(tests.negative_fixtures.length, 14);
for (const item of tests.deterministic_replay.outputs) {
  assert.deepEqual(await identity(`docs/backend/d20/${item.path}`), {...item, path: `docs/backend/d20/${item.path}`});
}
const validation = await load('docs/backend/d20/validation.json');
assert.equal(validation.state, 'pass');
const map = await load('docs/backend/d20/learning-map.json');
const evidence = [];
for (const [kind, path] of [['d20_surface_tests', `${base}/tests.json`], ['d20_reader_witness', `${base}/input/reader-witness.json`], ['d20_surface_validation', 'docs/backend/d20/validation.json']]) {
  const {bytes, sha256: hash} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256: hash, verified_date: '2026-09-21'});
}
const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target), before = structuredClone(overrides);
const scope = '1.960 unit dengan tautan tepat, 52 latihan dan 10 hasil terpilih, 62 solusi pendamping serta 184 relasi bahan pendukung; pemilih rencana belajar dan mengajar.';
const tool = {tool_id: 'd20.open_learner_hub', label: 'D20 · Analisis Fungsional', href: 'backend/d20/D20.html',
  action_kind: 'course_reader', scope, state: 'verified', primary: false, machine_data_is_learner_destination: false,
  page: await identity('docs/backend/d20/D20.html'), resource: await identity('docs/backend/d20/learning-map.json'),
  evidence: await identity('docs/backend/d20/validation.json'), limitations: map.limitations};
overrides.learner_tools.D20 = [...(overrides.learner_tools.D20 ?? []).filter(t => t.tool_id !== tool.tool_id), tool];
overrides.native_capabilities.D20 = {...overrides.native_capabilities.D20,
  unit_identity: {status: 'verified', evidence}, educator_unit_alignment: {status: 'verified', evidence}};
const old = overrides.educator_evidence.D20 ?? {}, resources = (old.resources ?? []).filter(r => !['D20:educator-hub-v1', 'D20:educator-hub-en-v1'].includes(r.id));
for (const lang of ['id', 'en']) {
  const file = `D20-pengajar${lang === 'en' ? '.en' : ''}.html`, fact = await identity(`docs/backend/d20/${file}`);
  resources.push({id: lang === 'en' ? 'D20:educator-hub-en-v1' : 'D20:educator-hub-v1',
    title: lang === 'en' ? 'D20 teaching-plan selector — English interface, Indonesian reading' : 'Pemilih unit dan latihan D20 untuk pengajar',
    resource_type: 'teacher-guide', status: 'verified', url: `https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d20/${file}`,
    scope, bytes: fact.bytes, sha256: fact.sha256});
}
const teacher = await identity('docs/backend/d20/D20-pengajar.html');
overrides.educator_evidence.D20 = {...old, status: 'verified', verified_date: '2026-09-21',
  locator: resources.find(r => r.id === 'D20:educator-hub-v1').url, bytes: teacher.bytes, sha256: teacher.sha256,
  features: [...new Set([...(old.features ?? []), 'exercise_bank', 'remix_selectors', 'staged_hints_answers_solutions'])], resources};
for (const section of Object.keys(before)) {
  const a = structuredClone(before[section]), b = structuredClone(overrides[section]);
  if (['learner_tools', 'native_capabilities', 'educator_evidence'].includes(section)) {delete a.D20; delete b.D20;}
  assert.deepEqual(a, b, `Unrelated override changed: ${section}`);
}
await writeFile(resolve(project, target), json(overrides));
console.log(json({state: 'admitted', course_id: 'D20', capabilities: ['unit_identity', 'educator_unit_alignment'], unrelated_overrides_preserved: true}));
