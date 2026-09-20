import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {base, json, project, sha256} from './build-d60-surface-v1.mjs';

const load = async path => JSON.parse(await readFile(resolve(project, path), 'utf8'));
const identity = async path => {const b = await readFile(resolve(project, path)); return {path, bytes: b.length, sha256: sha256(b)};};
const tests = await load(`${base}/tests.json`);
assert.equal(tests.state, 'pass');
assert.equal(tests.counts.units, 2204);
assert.equal(tests.negative_fixtures.length, 8);
for (const item of tests.deterministic_replay.outputs) {
  assert.deepEqual(await identity(`docs/backend/d60/${item.path}`), {...item, path: `docs/backend/d60/${item.path}`});
}
const validation = await load('docs/backend/d60/validation.json');
assert.equal(validation.state, 'pass');
const map = await load('docs/backend/d60/learning-map.json');
const evidence = [];
for (const [kind, path] of [['d60_surface_tests', `${base}/tests.json`], ['d60_reader_witness', `${base}/reader-witness.json`], ['d60_surface_validation', 'docs/backend/d60/validation.json']]) {
  const {bytes, sha256: hash} = await identity(path);
  evidence.push({kind, locator: path, bytes, sha256: hash, verified_date: '2026-09-21'});
}
const target = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides = await load(target), before = structuredClone(overrides);
const scope = '2.204 unit native, 278 latihan/pertanyaan/pemeriksaan bukti, dan 480 relasi bahan pendukung; pencarian serta ekspor rencana tanpa menyalin badan buku.';
const tool = {tool_id: 'd60.open_learner_hub', label: 'D60 · Topologi Aljabar', href: 'backend/d60/D60.html',
  action_kind: 'course_reader', scope, state: 'verified', primary: false, machine_data_is_learner_destination: false,
  page: await identity('docs/backend/d60/D60.html'), resource: await identity('docs/backend/d60/learning-map.json'),
  evidence: await identity('docs/backend/d60/validation.json'), limitations: map.limitations};
overrides.learner_tools.D60 = [...(overrides.learner_tools.D60 ?? []).filter(t => t.tool_id !== tool.tool_id), tool];
overrides.native_capabilities.D60 = {...overrides.native_capabilities.D60,
  unit_identity: {status: 'verified', evidence}, educator_unit_alignment: {status: 'verified', evidence}};
const old = overrides.educator_evidence.D60 ?? {}, resources = (old.resources ?? []).filter(r => !['D60:educator-hub-v1', 'D60:educator-hub-en-v1'].includes(r.id));
for (const lang of ['id', 'en']) {
  const file = `D60-pengajar${lang === 'en' ? '.en' : ''}.html`, fact = await identity(`docs/backend/d60/${file}`);
  resources.push({id: lang === 'en' ? 'D60:educator-hub-en-v1' : 'D60:educator-hub-v1',
    title: lang === 'en' ? 'D60 teaching-plan selector — English interface, Indonesian reading' : 'Pemilih unit dan latihan D60 untuk pengajar',
    resource_type: 'teacher-guide', status: 'verified', url: `https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d60/${file}`,
    scope, bytes: fact.bytes, sha256: fact.sha256});
}
const teacher = await identity('docs/backend/d60/D60-pengajar.html');
overrides.educator_evidence.D60 = {...old, status: 'verified', verified_date: '2026-09-21',
  locator: resources.find(r => r.id === 'D60:educator-hub-v1').url, bytes: teacher.bytes, sha256: teacher.sha256,
  features: [...new Set([...(old.features ?? []), 'exercise_bank', 'remix_selectors', 'staged_hints_answers_solutions'])], resources};
for (const section of Object.keys(before)) {
  const a = structuredClone(before[section]), b = structuredClone(overrides[section]);
  if (['learner_tools', 'native_capabilities', 'educator_evidence'].includes(section)) {delete a.D60; delete b.D60;}
  assert.deepEqual(a, b, `Unrelated override changed: ${section}`);
}
await writeFile(resolve(project, target), json(overrides));
console.log(json({state: 'admitted', course_id: 'D60', capabilities: ['unit_identity', 'educator_unit_alignment'], unrelated_overrides_preserved: true}));
