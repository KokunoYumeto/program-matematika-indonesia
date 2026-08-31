import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { courses as authorityCourses } from '../docs/courses.js';
import { materializeLiveCourses } from '../docs/live-course-publications.js';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const valueOf = (name, fallback = null) => process.argv.find((value) => value.startsWith(`--${name}=`))?.slice(name.length + 3) ?? fallback;
const resolveArgument = (value) => isAbsolute(value) ? value : resolve(project, value);
const outputRoot = resolveArgument(valueOf('output-root', 'backend/course-capsule-v1'));
const peerRootValue = valueOf('peer-output-root');
const peerRoot = peerRootValue ? resolveArgument(peerRootValue) : null;
const paths = {
  schema: resolve(project, 'schemas/course-capsule-v1/course-capsule-v1.schema.json'),
  overrides: resolve(project, 'backend/course-capsule-v1/authority/integration-overrides-v1.json'),
  jsonl: resolve(outputRoot, 'generated/course-capsules.jsonl'),
  json: resolve(outputRoot, 'generated/course-capsules.json'),
  manifest: resolve(outputRoot, 'generated/manifest.json'),
  receipt: resolve(outputRoot, 'validation/VALIDATION_RECEIPT.json'),
};
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const identity = (path, bytes) => ({ path, bytes: bytes.length, sha256: sha256(bytes) });
const sortValue = (value) => {
  if (Array.isArray(value)) return value.map(sortValue);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sortValue(value[key])]));
  return value;
};
const canonicalLine = (value) => JSON.stringify(sortValue(value));
const canonicalJson = (value) => `${JSON.stringify(sortValue(value), null, 2)}\n`;
const courseSort = (left, right) => left.id.localeCompare(right.id, 'en', { numeric: true });
const statusValues = new Set(['verified', 'legacy_verified', 'available_unverified', 'in_progress', 'not_yet_produced', 'not_applicable', 'unknown']);
const layerNames = ['curriculum', 'translation', 'production', 'learner', 'educator', 'federation', 'interoperability'];

const [schemaBytes, overrideBytes, jsonlBytes, jsonBytes, manifestBytes] = await Promise.all([
  readFile(paths.schema),
  readFile(paths.overrides),
  readFile(paths.jsonl),
  readFile(paths.json),
  readFile(paths.manifest),
]);
const overrides = JSON.parse(overrideBytes.toString('utf8'));
const manifest = JSON.parse(manifestBytes.toString('utf8'));
const text = jsonlBytes.toString('utf8');
assert.ok(text.endsWith('\n'), 'JSONL must end with LF.');
const lines = text.trimEnd().split('\n');
const capsules = lines.map((line, index) => {
  const capsule = JSON.parse(line);
  assert.equal(line, canonicalLine(capsule), `Line ${index + 1} is not canonical JSON.`);
  return capsule;
});
assert.equal(jsonBytes.toString('utf8'), canonicalJson(capsules), 'JSON projection is not the canonical capsule array.');
assert.deepEqual(JSON.parse(jsonBytes.toString('utf8')), capsules, 'JSON projection differs from canonical JSONL.');

const pythonValidation = String.raw`
import json, sys
from jsonschema import Draft202012Validator, FormatChecker
schema_path, jsonl_path = sys.argv[1], sys.argv[2]
with open(schema_path, encoding='utf-8') as handle:
    schema = json.load(handle)
validator = Draft202012Validator(schema, format_checker=FormatChecker())
errors = []
with open(jsonl_path, encoding='utf-8') as handle:
    for line_number, line in enumerate(handle, 1):
        if not line.strip():
            continue
        value = json.loads(line)
        for error in validator.iter_errors(value):
            errors.append({'line': line_number, 'path': list(error.absolute_path), 'message': error.message})
if errors:
    print(json.dumps(errors[:50], ensure_ascii=False, indent=2))
    raise SystemExit(1)
print(json.dumps({'status': 'pass', 'instances': line_number}, sort_keys=True))
`;
const schemaRun = spawnSync('python', ['-c', pythonValidation, paths.schema, paths.jsonl], { encoding: 'utf8' });
assert.equal(schemaRun.status, 0, `JSON Schema validation failed:\n${schemaRun.stdout}\n${schemaRun.stderr}`);

assert.equal(capsules.length, 40, 'Exactly forty course capsules required.');
assert.equal(new Set(capsules.map(({ course_id }) => course_id)).size, 40, 'Course IDs must be unique.');
const sortedIds = capsules.map(({ course_id }) => course_id).sort((a, b) => a.localeCompare(b, 'en', { numeric: true }));
assert.deepEqual(capsules.map(({ course_id }) => course_id), sortedIds, 'Capsules must be course-sorted.');

const effective = materializeLiveCourses(authorityCourses)
  .map((course) => {
    const truth = overrides.course_truth[course.id];
    if (!truth) return structuredClone(course);
    const { publication_evidence: _publicationEvidence, ...fields } = truth;
    return { ...structuredClone(course), ...fields };
  })
  .sort(courseSort);
assert.deepEqual(capsules.map(({ course_id }) => course_id), effective.map(({ id }) => id));

const byId = Object.fromEntries(capsules.map((capsule) => [capsule.course_id, capsule]));
for (const [index, capsule] of capsules.entries()) {
  const source = effective[index];
  assert.equal(capsule.course.title, source.title);
  assert.equal(capsule.course.state, source.state);
  assert.deepEqual(capsule.course.prerequisites, source.prerequisites);
  assert.equal(capsule.learner_directed, true);
  assert.deepEqual(Object.keys(capsule.layers).sort(), [...layerNames].sort());
  assert.ok(Object.values(capsule.open_access_policy).every((value) => value === true), `${capsule.course_id}: open policy must be all true.`);
  assert.equal(capsule.layers.curriculum.course_identity, capsule.course_id);
  assert.equal(capsule.layers.curriculum.route_id, `route:${capsule.course_id}`);
  assert.deepEqual(capsule.layers.curriculum.prerequisites, capsule.course.prerequisites);
  assert.equal(capsule.layers.educator.shared_identity_scope, 'learner_and_educator_views_share_course_unit_concept_exercise_ids');
  assert.equal(capsule.layers.federation.zero_copy, true);
  assert.equal(capsule.layers.interoperability.status, 'verified');
  assert.equal(capsule.layers.interoperability.native_identity_preserved, true);
  for (const layer of layerNames) assert.ok(statusValues.has(capsule.layers[layer].status), `${capsule.course_id}/${layer}: invalid status.`);
  for (const component of capsule.layers.federation.components) assert.ok(['public', 'unknown'].includes(component.access));
  for (const resource of capsule.layers.educator.resources) {
    assert.match(resource.url, /^https:\/\//);
    assert.ok(statusValues.has(resource.status));
  }
  assert.equal(new Set(capsule.layers.educator.features).size, capsule.layers.educator.features.length);
}

const edges = [];
const indegree = Object.fromEntries(sortedIds.map((id) => [id, 0]));
const outgoing = Object.fromEntries(sortedIds.map((id) => [id, []]));
for (const capsule of capsules) {
  for (const prerequisite of capsule.course.prerequisites) {
    assert.ok(byId[prerequisite], `${capsule.course_id}: missing prerequisite ${prerequisite}.`);
    assert.notEqual(prerequisite, capsule.course_id, `${capsule.course_id}: self prerequisite.`);
    edges.push([prerequisite, capsule.course_id]);
    outgoing[prerequisite].push(capsule.course_id);
    indegree[capsule.course_id] += 1;
  }
}
assert.equal(edges.length, 83, 'Expected exact 83-edge curriculum DAG.');
const queue = sortedIds.filter((id) => indegree[id] === 0);
let visited = 0;
while (queue.length) {
  const id = queue.shift();
  visited += 1;
  for (const next of outgoing[id]) {
    indegree[next] -= 1;
    if (indegree[next] === 0) queue.push(next);
  }
}
assert.equal(visited, 40, 'Prerequisite graph contains a cycle.');

assert.equal(capsules.filter(({ course }) => course.state === 'published').length, 32);
assert.equal(capsules.filter(({ course }) => course.state === 'production').length, 8);
const leblFamily = {
  B70: { bytes: 5135134, sha256: '1c18dfc1572d22ef7fc5d8ad25be18f3b91f1bffea5b9f9d521ff4e56ca969d4' },
  C10: { bytes: 2870909, sha256: '38743ea0e7ce52bdadf5233fc9d6e79e00717f9ba55a393f2bf46ea21c65ef56' },
  C20: { bytes: 2427379, sha256: 'e70c74bb7edc466a7cb6ff0eff0de33dfcc7b3bc63010d018aff758a14d2dea3' },
  C50: { bytes: 2822132, sha256: '87e4810abdedbdd8121995a8e53936891135037f03054dce76a06beebc3cfaae' },
};
for (const [id, expected] of Object.entries(leblFamily)) {
  const capsule = byId[id];
  assert.equal(capsule.course.state, 'published');
  assert.equal(capsule.course_native.zenodo, 'https://doi.org/10.5281/zenodo.22182427');
  assert.equal(capsule.layers.learner.pdf.status, 'verified');
  assert.equal(capsule.layers.learner.pdf.bytes, expected.bytes);
  assert.equal(capsule.layers.learner.pdf.sha256, expected.sha256);
}
assert.equal(byId.A00.layers.interoperability.semantic_adapter.status, 'legacy_verified');
assert.notEqual(byId.A00.layers.interoperability.semantic_adapter.contract_version, '2.3.1');
for (const id of ['B10', 'D20', 'D60', 'D110']) {
  assert.equal(byId[id].layers.interoperability.semantic_adapter.status, 'verified');
  assert.equal(byId[id].layers.interoperability.semantic_adapter.contract_version, '2.3.1');
}

assert.equal(manifest.schema_version, '1.0.0');
assert.deepEqual(manifest.output, identity('generated/course-capsules.jsonl', jsonlBytes));
assert.deepEqual(manifest.projections.course_capsules_json, identity('generated/course-capsules.json', jsonBytes));
assert.equal(manifest.summary.course_count, 40);
assert.equal(manifest.summary.published_count, 32);
assert.equal(manifest.summary.production_count, 8);
assert.equal(manifest.summary.prerequisite_edge_count, 83);
for (const input of manifest.inputs) {
  const bytes = await readFile(resolve(project, input.path));
  assert.deepEqual(input, { key: input.key, ...identity(input.path, bytes) }, `${input.path}: manifest identity drift.`);
}

const forbiddenPatterns = [
  /C:\\\\Users\\\\/i,
  /Authorization:\s*Bearer/i,
  /access[_-]?token/i,
  /api[_-]?token/i,
  /"access"\s*:\s*"(?:private|restricted|embargoed|blocked)"/i,
];
for (const pattern of forbiddenPatterns) assert.doesNotMatch(text, pattern, `Forbidden public-capsule content: ${pattern}.`);
assert.doesNotMatch(text, /"owner(?:ship)?"\s*:/i, 'Capsule must not encode owner-control semantics.');

let peerReplay = { compared: false, byte_identical: null };
if (peerRoot) {
  const [peerJsonl, peerJson, peerManifest] = await Promise.all([
    readFile(resolve(peerRoot, 'generated/course-capsules.jsonl')),
    readFile(resolve(peerRoot, 'generated/course-capsules.json')),
    readFile(resolve(peerRoot, 'generated/manifest.json')),
  ]);
  assert.deepEqual(peerJsonl, jsonlBytes, 'Peer JSONL build differs.');
  assert.deepEqual(peerJson, jsonBytes, 'Peer JSON projection differs.');
  assert.deepEqual(peerManifest, manifestBytes, 'Peer manifest build differs.');
  peerReplay = { compared: true, byte_identical: true };
}

const educatorCourses = capsules.filter((capsule) => capsule.layers.educator.features.length || capsule.layers.educator.resources.length);
const receipt = {
  schema_id: 'interlanguage/open-course-capsule-validation-receipt/v1',
  schema_version: '1.0.0',
  state: 'pass',
  checks: {
    schema_instances: 40,
    unique_course_ids: 40,
    seven_layer_rows: 40,
    prerequisite_edges: edges.length,
    prerequisite_dag_visited: visited,
    published_count: 32,
    production_count: 8,
    public_access_policy_rows: 40,
    educator_course_count: educatorCourses.length,
    educator_resource_count: capsules.reduce((count, capsule) => count + capsule.layers.educator.resources.length, 0),
    lebl_family_truth_overrides: 'pass',
    semantic_adapter_truth: 'pass',
    canonical_jsonl: 'pass',
    manifest_input_replay: 'pass',
    credential_profile_scan: 'pass',
  },
  artifacts: {
    course_capsules_jsonl: identity('generated/course-capsules.jsonl', jsonlBytes),
    course_capsules_json: identity('generated/course-capsules.json', jsonBytes),
    manifest_json: identity('generated/manifest.json', manifestBytes),
    schema_json: identity('schemas/course-capsule-v1/course-capsule-v1.schema.json', schemaBytes),
  },
  peer_replay: peerReplay,
};
const receiptBytes = Buffer.from(canonicalJson(receipt));
await mkdir(dirname(paths.receipt), { recursive: true });
await writeFile(paths.receipt, receiptBytes);
console.log(JSON.stringify({ status: 'pass', output_root: outputRoot, receipt: identity('validation/VALIDATION_RECEIPT.json', receiptBytes), ...receipt.checks, peer_replay: peerReplay }, null, 2));
