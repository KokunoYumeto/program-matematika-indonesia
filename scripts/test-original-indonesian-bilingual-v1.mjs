import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {
  buildOriginalIndonesianBilingual,
  localizeD120Projection,
  validateB80Identity,
} from './build-original-indonesian-bilingual-v1.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/localizations/original-indonesian-bilingual-v1';
const load = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const jsonl = async path => (await readFile(resolve(root, path), 'utf8')).trim().split(/\r?\n/).map(JSON.parse);
const identity = async path => {
  const bytes = await readFile(resolve(root, path));
  return {path, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')};
};

const b80Id = await load('backend/course-capsule-v1/adapters/b80-capability-v1/input/catalog.json');
const b80En = await load(`${base}/input/b80/catalog.en.json`);
assert.deepEqual(validateB80Identity(b80Id, b80En), {
  units: 14, exercises: 75, labs: 4, prerequisite_routes: 4,
  components: 46, artifacts: 27, environments: 2, sources: 6,
});
for (const mutate of [
  value => { value.units[0].id = 'changed-unit'; },
  value => { value.exercises.pop(); },
  value => { value.exercises[0].hint.source_anchor = 'changed-anchor'; },
  value => { value.prerequisite_routes[0].sections.pop(); },
  value => { value.components[0].id = 'changed-component'; },
  value => { value.relations.find(row => row.type === 'precedes').to = 'changed-target'; },
]) {
  const changed = structuredClone(b80En);
  mutate(changed);
  assert.throws(() => validateB80Identity(b80Id, changed));
}

const d120Learning = await load('backend/course-capsule-v1/adapters/d120-capability-v1/data/learning-map.json');
const d120Educator = await load('backend/course-capsule-v1/adapters/d120-capability-v1/data/educator-map.json');
const semantic = await jsonl(`${base}/input/d120/semantic-wrapper-v1.localizations.en.jsonl`);
const core = await jsonl(`${base}/input/d120/core-localizations.en.jsonl`);
const access = await jsonl(`${base}/input/d120/english-access-locators.jsonl`);
const sourceLock = await load(`${base}/source-lock.json`);
const publication = await load(`${base}/input/d120/github-publication.json`);
const d120 = localizeD120Projection(d120Learning, d120Educator, semantic, core, access, sourceLock, publication);
assert.equal(d120.localizedFields, 339);
assert.equal(d120.accessBindings, 117);
assert.equal(d120.learningMap.locale, 'en');
assert.equal(d120.educatorMap.locale, 'en');
assert.equal(d120.learningMap.title, 'Traceable Mathematical Work');
assert.equal(d120.learningMap.units[0].title, 'Reading Arguments as Networks of Claims');
assert.equal(d120.learningMap.units[0].unit_id, d120Learning.units[0].unit_id);
assert.deepEqual(d120.learningMap.route, d120Learning.route);
assert.deepEqual(
  d120.educatorMap.assessments.map(row => row.assessment_id),
  d120Educator.assessments.map(row => row.assessment_id),
);
assert.equal(d120.learningMap.units.flatMap(row => row.practice).length, 54);
assert.ok(d120.learningMap.units.every(row => row.public_reader.url.includes('/en/units/')));
assert.ok(d120.learningMap.units.every(row => row.practice.every(item => item.exercise_url.includes('/en/units/') && item.guidance_url.includes('/en/units/'))));

{
  const changed = structuredClone(semantic);
  const removed = changed.shift();
  changed.push({...removed, id: `${removed.id}-UNUSED`, subject_id: 'O017-UNUSED'});
  assert.throws(() => localizeD120Projection(d120Learning, d120Educator, changed, core, access, sourceLock, publication));
}
{
  const changed = structuredClone(access);
  changed[0].locale = 'id';
  assert.throws(() => localizeD120Projection(d120Learning, d120Educator, semantic, core, changed, sourceLock, publication));
}
{
  const changed = structuredClone(sourceLock);
  changed.courses.D120.used_access_locators[0].fragment = 'changed-fragment';
  assert.throws(() => localizeD120Projection(d120Learning, d120Educator, semantic, core, access, changed, publication));
}
{
  const changed = structuredClone(sourceLock);
  changed.courses.D120.used_access_locators[1].anchor_count = 0;
  assert.throws(() => localizeD120Projection(d120Learning, d120Educator, semantic, core, access, changed, publication));
}

const first = await buildOriginalIndonesianBilingual();
const firstManifestFact = await identity(`${base}/manifest.json`);
const firstOutputs = await Promise.all(first.manifest.outputs.map(row => identity(row.path)));
assert.deepEqual(firstOutputs, first.manifest.outputs);
const second = await buildOriginalIndonesianBilingual();
assert.deepEqual(second, first);
assert.deepEqual(await identity(`${base}/manifest.json`), firstManifestFact);
assert.deepEqual(await Promise.all(second.manifest.outputs.map(row => identity(row.path))), firstOutputs);
assert.equal(second.manifest.tools.length, 4);
assert.deepEqual(second.manifest.tools.map(row => [row.courseId, row.contentLanguage]), [
  ['B80', 'en'], ['B80', 'en'], ['D120', 'en'], ['D120', 'en'],
]);
for (const tool of second.manifest.tools) {
  assert.equal(tool.labelLanguage, 'en');
  assert.equal(tool.state, 'verified');
  assert.equal(tool.primary, false);
  assert.equal(tool.machine_data_is_learner_destination, false);
  assert.deepEqual(await identity(tool.page.path), tool.page);
  assert.deepEqual(await identity(tool.resource.path), tool.resource);
  assert.deepEqual(await identity(tool.evidence.path), tool.evidence);
}
for (const path of [
  'docs/backend/b80-en/B80.html', 'docs/backend/b80-en/B80-educator.html',
  'docs/backend/d120-en/D120.html', 'docs/backend/d120-en/D120-educator.html',
]) {
  const html = await readFile(resolve(root, path), 'utf8');
  assert.match(html, /^<!doctype html><html lang="en">/);
  assert.match(html, /shared course identity|same semantic IDs/);
  assert.doesNotMatch(html, /<img\b/i);
}
const publicationState = await load('docs/backend/b80/publication-state.json');
assert.equal(publicationState.current_central_adapter_status, 'public_github_verified');
assert.equal(publicationState.current_english_source_edition_status, 'public_github_verified');
assert.equal(publicationState.current_english_shared_projection_status, 'locally_verified_pending_this_increment_publication');
assert.equal(publicationState.overall_program_backend_complete, false);
assert.deepEqual(publicationState, await load('docs/backend/b80-en/publication-state.json'));

console.log(JSON.stringify({state: 'pass', negative_fixtures: 10, deterministic_builds: 2, interface_tools: 4}));
