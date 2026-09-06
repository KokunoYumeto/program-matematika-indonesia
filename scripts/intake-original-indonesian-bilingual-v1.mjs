import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {copyFile, mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const option = name => process.argv.find(value => value.startsWith(`--${name}=`))?.slice(name.length + 3);
const workspaceRoot = resolve(project, '..', '..', '..');
const b80Root = resolve(option('b80-root') ?? process.env.PMI_B80_EN_ROOT ?? resolve(workspaceRoot, '04_mirrors/en/mathematical-computing-reproducible-experiments-en'));
const d120Root = resolve(option('d120-root') ?? process.env.PMI_D120_EN_ROOT ?? resolve(workspaceRoot, 'outputs/01a0216a-4b9f-7d30-a376-60e4e3859979/english-edition'));
const base = 'backend/course-capsule-v1/localizations/original-indonesian-bilingual-v1';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const json = value => `${JSON.stringify(value, null, 2)}\n`;
const loadJson = async path => JSON.parse(await readFile(path, 'utf8'));
const fact = async path => {
  const bytes = await readFile(path);
  return {bytes: bytes.length, sha256: hash(bytes)};
};
const projectFact = async path => ({path, ...await fact(resolve(project, path))});
const countAnchor = (html, id) => {
  const escaped = id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return [...html.matchAll(new RegExp(`(?:^|\\s)id=["']${escaped}["']`, 'g'))].length;
};
const copyInput = async (source, destination) => {
  const target = resolve(project, destination);
  await mkdir(dirname(target), {recursive: true});
  await copyFile(source, target);
  return projectFact(destination);
};

const b80Inputs = [
  ['backend/catalog.json', `${base}/input/b80/catalog.en.json`],
  ['backend/catalog.schema.json', `${base}/input/b80/catalog.en.schema.json`],
  ['00_control/ENGLISH_GITHUB_PUBLICATION.json', `${base}/input/b80/github-publication.json`],
  ['00_control/SOURCE_WITNESS.json', `${base}/input/b80/source-witness.json`],
  ['LANGUAGE_LINKS.json', `${base}/input/b80/language-links.json`],
];
const d120Inputs = [
  ['backend/core-localizations.en.jsonl', `${base}/input/d120/core-localizations.en.jsonl`],
  ['backend/semantic-wrapper-v1.localizations.en.jsonl', `${base}/input/d120/semantic-wrapper-v1.localizations.en.jsonl`],
  ['backend/english-access-locators.jsonl', `${base}/input/d120/english-access-locators.jsonl`],
  ['backend/english-backend.dataset.json', `${base}/input/d120/english-backend.dataset.json`],
  ['backend/languages.json', `${base}/input/d120/languages.json`],
  ['qa/ENGLISH_BACKEND_QA.json', `${base}/input/d120/english-backend-qa.json`],
  ['release/GITHUB_PUBLICATION_RECEIPT.json', `${base}/input/d120/github-publication.json`],
];
const inputs = [];
for (const [source, destination] of b80Inputs) inputs.push(await copyInput(resolve(b80Root, source), destination));
for (const [source, destination] of d120Inputs) inputs.push(await copyInput(resolve(d120Root, source), destination));

const b80Catalog = await loadJson(resolve(b80Root, 'backend/catalog.json'));
const b80Receipt = await loadJson(resolve(b80Root, '00_control/ENGLISH_GITHUB_PUBLICATION.json'));
assert.equal(b80Catalog.course.id, 'B80');
assert.equal(b80Catalog.language, 'en');
assert.equal(b80Receipt.status, 'public_verified');
assert.equal(b80Receipt.repository.commit, b80Receipt.pages.build_commit);
const b80PageByPath = new Map(b80Receipt.pages.files.map(row => [row.path, row]));
const b80Exercises = new Map(b80Catalog.exercises.map(row => [row.id, row]));
const b80Pages = [];
for (const unit of b80Catalog.units) {
  const path = unit.reader_path.replace(/\.qmd$/, '.html');
  const receipt = b80PageByPath.get(path);
  assert.ok(receipt, `Missing B80 public page receipt: ${path}`);
  const bytes = await readFile(resolve(b80Root, 'output', path));
  assert.deepEqual({bytes: bytes.length, sha256: hash(bytes)}, {bytes: receipt.bytes, sha256: receipt.sha256});
  const required = new Set(unit.sections);
  for (const id of unit.exercises) {
    const exercise = b80Exercises.get(id);
    assert.ok(exercise);
    required.add(id);
    for (const kind of ['hint', 'check', 'solution']) if (exercise[kind]?.source_anchor) required.add(exercise[kind].source_anchor);
  }
  const html = bytes.toString('utf8');
  const anchors = Object.fromEntries([...required].sort().map(id => [id, countAnchor(html, id)]));
  for (const [id, count] of Object.entries(anchors)) assert.equal(count, 1, `B80 anchor ${path}#${id}`);
  b80Pages.push({unit_id: unit.id, path, url: receipt.url, bytes: receipt.bytes, sha256: receipt.sha256, anchors});
}

const d120Receipt = await loadJson(resolve(d120Root, 'release/GITHUB_PUBLICATION_RECEIPT.json'));
const d120Qa = await loadJson(resolve(d120Root, 'qa/ENGLISH_BACKEND_QA.json'));
assert.equal(d120Receipt.status, 'PASS');
assert.equal(d120Qa.status, 'pass');
const d120PageByPath = new Map(d120Receipt.pages_files.map(row => [row.path, row]));
const accessRows = (await readFile(resolve(d120Root, 'backend/english-access-locators.jsonl'), 'utf8'))
  .trim().split(/\r?\n/).map(line => JSON.parse(line));
assert.equal(accessRows.length, 529);
const accessBySubject = new Map();
for (const row of accessRows) {
  assert.equal(row.locale, 'en');
  assert.ok(!accessBySubject.has(row.subject_id), `Duplicate D120 English locator ${row.subject_id}`);
  accessBySubject.set(row.subject_id, row);
}
const d120Learning = await loadJson(resolve(project, 'backend/course-capsule-v1/adapters/d120-capability-v1/data/learning-map.json'));
const usedSubjects = new Set(d120Learning.units.flatMap(unit => [unit.unit_id, ...unit.practice.flatMap(item => [item.exercise_id, item.guidance_id])]));
const d120PagesByPath = new Map();
const d120Access = [];
for (const subjectId of [...usedSubjects].sort()) {
  const row = accessBySubject.get(subjectId);
  assert.ok(row, `Missing D120 English locator ${subjectId}`);
  const publicPath = row.reader_path.replace(/^build\/html\//, 'en/');
  const receipt = d120PageByPath.get(publicPath);
  assert.ok(receipt, `Missing D120 public page receipt: ${publicPath}`);
  let page = d120PagesByPath.get(row.reader_path);
  if (!page) {
    const bytes = await readFile(resolve(d120Root, row.reader_path));
    assert.deepEqual({bytes: bytes.length, sha256: hash(bytes)}, {bytes: receipt.bytes, sha256: receipt.sha256});
    page = {reader_path: row.reader_path, public_path: publicPath, url: receipt.url, bytes: receipt.bytes, sha256: receipt.sha256};
    d120PagesByPath.set(row.reader_path, page);
  }
  const html = await readFile(resolve(d120Root, row.reader_path), 'utf8');
  const anchor_count = row.fragment ? countAnchor(html, row.fragment) : 0;
  if (row.fragment) assert.equal(anchor_count, 1, `D120 anchor ${publicPath}#${row.fragment}`);
  d120Access.push({subject_id: subjectId, reader_path: row.reader_path, public_path: publicPath, fragment: row.fragment, anchor_count});
}
for (const path of ['en/index.html', 'en/wrapper/index.html']) {
  const receipt = d120PageByPath.get(path);
  assert.ok(receipt);
  const localPath = `build/html/${path.slice(3)}`;
  const bytes = await readFile(resolve(d120Root, localPath));
  assert.deepEqual({bytes: bytes.length, sha256: hash(bytes)}, {bytes: receipt.bytes, sha256: receipt.sha256});
  d120PagesByPath.set(localPath, {reader_path: localPath, public_path: path, url: receipt.url, bytes: receipt.bytes, sha256: receipt.sha256});
}

const centralInputs = await Promise.all([
  'backend/course-capsule-v1/adapters/b80-capability-v1/input/catalog.json',
  'backend/course-capsule-v1/adapters/b80-capability-v1/validation.json',
  'backend/course-capsule-v1/adapters/b80-capability-v1/publication/GITHUB_SOURCE_AND_PAGES_READBACK_20260904.json',
  'backend/course-capsule-v1/adapters/d120-capability-v1/data/learning-map.json',
  'backend/course-capsule-v1/adapters/d120-capability-v1/data/educator-map.json',
  'backend/course-capsule-v1/adapters/d120-capability-v1/validation.json',
].map(projectFact));

const lock = {
  schema: 'original-indonesian-bilingual-source-lock/1',
  status: 'verified_public_inputs',
  policy: {
    additive_localization_only: true,
    central_course_identity_duplicated: false,
    native_ids_preserved: true,
    producer_files_changed: false,
    textbook_bodies_copied: false,
  },
  inputs: inputs.sort((a, b) => a.path.localeCompare(b.path)),
  central_inputs: centralInputs.sort((a, b) => a.path.localeCompare(b.path)),
  courses: {
    B80: {
      repository: b80Receipt.repository.full_name,
      commit: b80Receipt.repository.commit,
      tree: b80Receipt.repository.docs_tree_sha,
      release_tag: b80Receipt.release.tag,
      verified_at_utc: b80Receipt.verified_at_utc,
      public_pages: b80Pages,
    },
    D120: {
      repository: 'KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id',
      commit: d120Receipt.commit,
      tree: d120Receipt.tree,
      release_tag: 'en-v2026.08.31',
      verified_at_utc: d120Receipt.verified_at_utc,
      public_pages: [...d120PagesByPath.values()].sort((a, b) => a.public_path.localeCompare(b.public_path)),
      used_access_locators: d120Access,
    },
  },
};
await writeFile(resolve(project, base, 'source-lock.json'), json(lock));
console.log(JSON.stringify({state: 'pass', inputs: inputs.length, b80_pages: b80Pages.length, d120_pages: d120PagesByPath.size, d120_access_locators: d120Access.length}));
