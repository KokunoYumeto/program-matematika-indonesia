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
assert.ok(peerRoot, '--peer-output-root is required; a single build cannot certify deterministic replay.');
assert.notEqual(resolve(peerRoot), resolve(outputRoot), 'Peer replay root must be distinct from the output root.');
const paths = {
  schema: resolve(project, 'schemas/course-capsule-v1/course-capsule-v1.schema.json'),
  designPolicySchema: resolve(project, 'schemas/course-capsule-v1/backend-design-policy-v1.schema.json'),
  publicBaselineSchema: resolve(project, 'schemas/course-capsule-v1/public-baseline-v1.schema.json'),
  terminologyPolicySchema: resolve(project, 'schemas/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json'),
  terminologyConceptSchema: resolve(project, 'schemas/course-capsule-v1/v2/terminology-concept-record-v1.schema.json'),
  designPolicy: resolve(project, 'backend/course-capsule-v1/authority/backend-design-policy-v1.json'),
  publicBaseline: resolve(project, 'backend/course-capsule-v1/authority/public-baseline-v0.62.12.json'),
  terminologyPolicy: resolve(project, 'backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json'),
  d40Readback: resolve(project, 'backend/course-capsule-v1/validation/D40_O010_INDEPENDENT_ANONYMOUS_READBACK.json'),
  overrides: resolve(project, 'backend/course-capsule-v1/authority/integration-overrides-v1.json'),
  nativePackages: resolve(project, 'backend/course-capsule-v1/authority/native-package-references-v1.json'),
  learnerDelivery: resolve(project, 'backend/authority/learner-delivery-v1.json'),
  learnerTools: resolve(project, 'backend/authority/learner-tools-v1.json'),
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

const [schemaBytes, designPolicySchemaBytes, publicBaselineSchemaBytes, terminologyPolicySchemaBytes, terminologyConceptSchemaBytes, designPolicyBytes, publicBaselineBytes, terminologyPolicyBytes, d40ReadbackBytes, overrideBytes, learnerToolsBytes, jsonlBytes, jsonBytes, manifestBytes] = await Promise.all([
  readFile(paths.schema),
  readFile(paths.designPolicySchema),
  readFile(paths.publicBaselineSchema),
  readFile(paths.terminologyPolicySchema),
  readFile(paths.terminologyConceptSchema),
  readFile(paths.designPolicy),
  readFile(paths.publicBaseline),
  readFile(paths.terminologyPolicy),
  readFile(paths.d40Readback),
  readFile(paths.overrides),
  readFile(paths.learnerTools),
  readFile(paths.jsonl),
  readFile(paths.json),
  readFile(paths.manifest),
]);
const overrides = JSON.parse(overrideBytes.toString('utf8'));
const designPolicy = JSON.parse(designPolicyBytes.toString('utf8'));
const publicBaseline = JSON.parse(publicBaselineBytes.toString('utf8'));
const terminologyPolicy = JSON.parse(terminologyPolicyBytes.toString('utf8'));
const d40Readback = JSON.parse(d40ReadbackBytes.toString('utf8'));
const learnerTools = JSON.parse(learnerToolsBytes.toString('utf8'));
const learnerDelivery = JSON.parse(await readFile(paths.learnerDelivery, 'utf8'));
const deliveryById = Object.fromEntries(learnerDelivery.courses.map((row) => [row.course_id, row]));
assert.equal(Object.keys(deliveryById).length, 40, 'Learner delivery must contain forty unique courses.');
const nativePackages = JSON.parse(await readFile(paths.nativePackages, 'utf8'));
const nativePackageEvidence = await readFile(resolve(project, 'backend/course-capsule-v1/validation', nativePackages.evidence.name));
assert.equal(nativePackageEvidence.length, nativePackages.evidence.bytes, 'Native package evidence byte drift.');
assert.equal(sha256(nativePackageEvidence), nativePackages.evidence.sha256, 'Native package evidence hash drift.');
const packageAddendum = JSON.parse(nativePackageEvidence);
const pointer = (value, path) => path.split('/').slice(1).reduce((at, key) => at?.[key.replaceAll('~1', '/').replaceAll('~0', '~')], value);
for (const operation of nativePackages.operations) {
  let fact;
  if (operation.evidence_file) {
    const bytes = await readFile(resolve(project, 'backend/course-capsule-v1/validation', operation.evidence_file));
    assert.equal(bytes.length, operation.evidence_bytes, 'Native package extra evidence byte drift.');
    assert.equal(sha256(bytes), operation.evidence_sha256, 'Native package extra evidence hash drift.');
    fact = pointer(JSON.parse(bytes), operation.evidence_package_pointer);
    assert.ok(fact, 'Native package evidence pointer missing.');
    const url = new URL(operation.expected_component.url);
    assert.equal(url.origin, 'https://zenodo.org', 'Native package evidence origin differs.');
    assert.equal(fact.url, url.origin + '/api' + url.pathname + '/content', 'Native package claim/evidence URL mismatch.');
    assert.equal(fact.sha256, operation.expected_component.sha256, 'Native package claim/evidence hash mismatch.');
    assert.equal(fact.bytes, operation.artifact_bytes, 'Native package claim/evidence byte mismatch.');
  } else {
    fact = pointer(packageAddendum, operation.evidence_addendum_pointer);
    assert.ok(fact, 'Native package evidence pointer missing.');
    assert.equal(fact.role, operation.artifact_role, 'Native package evidence role mismatch.');
    assert.equal(fact.public_record_file_url, operation.expected_component.url, 'Native package claim/evidence URL mismatch.');
    assert.equal(fact.sha256, operation.expected_component.sha256, 'Native package claim/evidence hash mismatch.');
    assert.equal(fact.bytes, operation.artifact_bytes, 'Native package claim/evidence byte mismatch.');
  }
  assert.equal(fact.sha256, operation.artifact_sha256, 'Native package artifact/evidence hash mismatch.');
}
const normalizedStatus = (status) => ({ absent: 'not_yet_produced', verified: 'verified', available_unverified: 'available_unverified', not_applicable: 'not_applicable', in_progress: 'in_progress', unknown: 'unknown' }[status] ?? 'unknown');
const clean = (value) => Object.fromEntries(Object.entries(value).filter(([, item]) => item !== undefined && item !== null));
const manifest = JSON.parse(manifestBytes.toString('utf8'));
assert.equal(learnerTools.schema_id, 'interlanguage/program-matematika-indonesia/learner-tools/v1');
assert.equal(learnerTools.schema_version, '1.0.0');
assert.equal(new Set(learnerTools.courses.map(({ course_id }) => course_id)).size, learnerTools.courses.length, 'Learner-tool authority contains duplicate course IDs.');
const authorityToolsByCourse = Object.fromEntries(learnerTools.courses.map(({ course_id, tools }) => [course_id, structuredClone(tools)]));
for (const [courseId, tools] of Object.entries(overrides.learner_tools ?? {}).sort(([left], [right]) => left.localeCompare(right))) {
  authorityToolsByCourse[courseId] ??= [];
  authorityToolsByCourse[courseId].push(...structuredClone(tools));
  authorityToolsByCourse[courseId].sort((left, right) => left.tool_id.localeCompare(right.tool_id));
}
const authorityToolIds = Object.values(authorityToolsByCourse).flatMap((tools) => tools.map(({ tool_id }) => tool_id));
assert.equal(new Set(authorityToolIds).size, authorityToolIds.length, 'Learner-tool authority contains duplicate tool IDs.');
const text = jsonlBytes.toString('utf8');
assert.ok(text.endsWith('\n'), 'JSONL must end with LF.');
const lines = text.trimEnd().split('\n');
assert.equal(text, `${lines.join('\n')}\n`, 'JSONL must contain exactly one terminal LF and no trailing whitespace.');
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
Draft202012Validator.check_schema(schema)
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
const schemaRun = spawnSync('python', ['-B', '-c', pythonValidation, paths.schema, paths.jsonl], { encoding: 'utf8' });
assert.equal(schemaRun.status, 0, `JSON Schema validation failed:\n${schemaRun.stdout}\n${schemaRun.stderr}`);

const documentValidation = String.raw`
import json, sys
from jsonschema import Draft202012Validator, FormatChecker
schema_path, document_path = sys.argv[1], sys.argv[2]
with open(schema_path, encoding='utf-8') as handle:
    schema = json.load(handle)
with open(document_path, encoding='utf-8') as handle:
    document = json.load(handle)
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema, format_checker=FormatChecker())
errors = list(validator.iter_errors(document))
if errors:
    print(json.dumps([{'path': list(error.absolute_path), 'message': error.message} for error in errors[:50]], ensure_ascii=False, indent=2))
    raise SystemExit(1)
print(json.dumps({'status': 'pass', 'document': document_path}, sort_keys=True))
`;
for (const [schemaPath, documentPath, label] of [
  [paths.designPolicySchema, paths.designPolicy, 'backend design policy'],
  [paths.publicBaselineSchema, paths.publicBaseline, 'public baseline'],
  [paths.terminologyPolicySchema, paths.terminologyPolicy, 'canonical terminology and register policy'],
]) {
  const run = spawnSync('python', ['-B', '-c', documentValidation, schemaPath, documentPath], { encoding: 'utf8' });
  assert.equal(run.status, 0, `${label} schema validation failed:\n${run.stdout}\n${run.stderr}`);
}
const schemaOnlyValidation = String.raw`
import json, sys
from jsonschema import Draft202012Validator
with open(sys.argv[1], encoding='utf-8') as handle:
    schema = json.load(handle)
Draft202012Validator.check_schema(schema)
print(json.dumps({'status': 'pass', 'schema': sys.argv[1]}, sort_keys=True))
`;
const terminologyConceptSchemaRun = spawnSync('python', ['-B', '-c', schemaOnlyValidation, paths.terminologyConceptSchema], { encoding: 'utf8' });
assert.equal(terminologyConceptSchemaRun.status, 0, `Terminology concept-record schema validation failed:\n${terminologyConceptSchemaRun.stdout}\n${terminologyConceptSchemaRun.stderr}`);

assert.equal(designPolicy.profile, 'thin_format_neutral_zero_copy');
assert.deepEqual(designPolicy.required_layers, layerNames);
assert.equal(designPolicy.authority.course_native_authoritative, true);
assert.equal(designPolicy.authority.capsule_additive, true);
assert.equal(designPolicy.authority.native_identity_preserved, true);
assert.equal(designPolicy.authority.full_corpus_copied_into_capsule, false);
assert.equal(designPolicy.exchange.canonical_capsule_format, 'application/x-ndjson');
assert.equal(designPolicy.exchange.course_native_formats_constrained, false);
assert.deepEqual(designPolicy.adapters.optional, ['myst', 'quarto', 'xliff']);
assert.equal(designPolicy.adapters.absence_blocks_release, false);
assert.equal(designPolicy.render_targets.length, 4);
assert.equal(designPolicy.evidence.length, 2);
assert.equal(publicBaseline.repository.commit, '15d37eea2f84ea7c4e856e81af0c4411828713b4');
assert.equal(publicBaseline.release.tag, 'v0.62.12');
assert.equal(publicBaseline.release.asset_count, 100);
assert.equal(publicBaseline.zenodo.record_id, 22182000);
assert.equal(publicBaseline.zenodo.access, 'open');
assert.equal(publicBaseline.zenodo.file_count, 100);
assert.equal(publicBaseline.zenodo.payload_bytes, 131739644);
assert.equal(publicBaseline.artifacts.length, 5);
assert.equal(terminologyPolicy.schema_id, 'interlanguage/program-matematika-indonesia-canonical-terminology-register-policy/v1');
assert.equal(terminologyPolicy.decision_procedure.length, 9);
assert.deepEqual(terminologyPolicy.decision_procedure.map(({ sequence }) => sequence), [1, 2, 3, 4, 5, 6, 7, 8, 9]);
assert.equal(terminologyPolicy.termbase_contract.schema_id, 'interlanguage/program-matematika-indonesia-terminology-concept/v1');
assert.equal(terminologyPolicy.probability_family_audit.status, 'evidence_required');
assert.equal(terminologyPolicy.probability_family_audit.automatic_replacement_allowed, false);
assert.equal(terminologyPolicy.probability_family_audit.concepts.length, 9);
assert.equal(terminologyPolicy.probability_family_audit.concepts.every(({ decision_state }) => decision_state === 'evidence_required'), true);
const expectedDesignPolicyRef = {
  profile: 'thin_format_neutral_zero_copy',
  course_native_authoritative: true,
  capsule_additive: true,
  native_identity_preserved: true,
  content_copied_into_capsule: false,
  canonical_capsule_format: 'application/x-ndjson',
  optional_adapters: ['myst', 'quarto', 'xliff'],
  adapter_absence_blocks_release: false,
  policy: {
    locator: 'https://kokunoyumeto.github.io/program-matematika-indonesia/data/course-capsule-v1/backend-design-policy-v1.json',
    bytes: designPolicyBytes.length,
    sha256: sha256(designPolicyBytes),
  },
  public_baseline: {
    locator: 'https://kokunoyumeto.github.io/program-matematika-indonesia/data/course-capsule-v1/public-baseline-v0.62.12.json',
    bytes: publicBaselineBytes.length,
    sha256: sha256(publicBaselineBytes),
  },
};

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
for (const courseId of Object.keys(authorityToolsByCourse)) assert.ok(byId[courseId], `Learner-tool authority refers to unknown course ${courseId}.`);
for (const [index, capsule] of capsules.entries()) {
  const source = effective[index];
  assert.equal(capsule.course.title, source.title);
  assert.equal(capsule.course.state, source.state);
  assert.equal(capsule.course.level, source.level);
  assert.equal(capsule.course.topic, source.topic);
  assert.equal(capsule.course.purpose, source.purpose);
  assert.equal(capsule.course.outcome, source.outcome);
  assert.deepEqual(capsule.course.prerequisites, source.prerequisites);
  assert.equal(capsule.learner_directed, true);
  assert.deepEqual(Object.keys(capsule.layers).sort(), [...layerNames].sort());
  assert.ok(Object.values(capsule.open_access_policy).every((value) => value === true), `${capsule.course_id}: open policy must be all true.`);
  assert.equal(capsule.layers.curriculum.course_identity, capsule.course_id);
  assert.equal(capsule.layers.curriculum.route_id, `route:${capsule.course_id}`);
  assert.deepEqual(capsule.layers.curriculum.prerequisites, capsule.course.prerequisites);
  assert.deepEqual(capsule.layers.curriculum.outcomes, [capsule.course.outcome]);
  assert.equal(capsule.layers.production.repository, capsule.course_native.repository);
  assert.equal(capsule.layers.production.zenodo, capsule.course_native.zenodo);
  assert.equal(capsule.layers.production.edition, capsule.course_native.edition);
  assert.equal(capsule.layers.educator.shared_identity_scope, 'learner_and_educator_views_share_course_unit_concept_exercise_ids');
  const educator = capsule.layers.educator;
  for (const expected of overrides.educator_evidence[capsule.course_id]?.resources ?? []) {
    const matches = educator.resources.filter(row=>row.id===expected.id);
    assert.equal(matches.length,1,`${capsule.course_id}: missing/duplicate educator resource.`);
    assert.deepEqual(matches[0],expected,`${capsule.course_id}: educator resource evidence drift.`);
  }
  const declaredEducatorStatus = overrides.educator_evidence[capsule.course_id]?.status;
  const expectedEducatorStatus = declaredEducatorStatus
    ?? (educator.features.length || educator.resources.length ? 'available_unverified' : 'unknown');
  assert.equal(educator.status, expectedEducatorStatus, `${capsule.course_id}: educator status must preserve authority or honest indexing uncertainty.`);
  const adapter = overrides.semantic_adapters[capsule.course_id];
  const nativeClaims = overrides.native_capabilities?.[capsule.course_id] ?? {};
  for (const [key, actual] of Object.entries({
    unit_identity: capsule.layers.curriculum.unit_identity_status,
    translation_ledger: capsule.layers.translation.ledger_status,
    terminology: capsule.layers.translation.terminology_status,
    translation_rights: capsule.layers.translation.rights_status,
    corrections: capsule.layers.translation.corrections_status,
    build: capsule.layers.production.build_status,
    deterministic_replay: capsule.layers.production.deterministic_replay_status,
    educator_unit_alignment: educator.unit_alignment_status,
  })) {
    const claim = nativeClaims[key];
    if (claim) assert.ok(statusValues.has(claim.status), `${capsule.course_id}/${key}: invalid native capability status.`);
    assert.equal(actual, claim?.status ?? 'unknown', `${capsule.course_id}/${key}: native status needs capability-specific evidence, not adapter status.`);
    if (actual !== 'unknown') assert.ok(claim.evidence?.length, `${capsule.course_id}/${key}: native evidence is missing.`);
    for (const evidence of claim?.evidence ?? []) assert.ok(capsule.evidence.some((entry) => canonicalLine(entry) === canonicalLine(evidence)), `${capsule.course_id}/${key}: native evidence not exposed.`);
  }
  assert.equal(educator.unlisted_features_status, 'unknown', `${capsule.course_id}: unlisted educator features must remain unknown.`);
  const declaredDelivery = deliveryById[capsule.course_id];
  const expectedDelivery = Object.fromEntries(['primary', 'online_html', 'pdf', 'epub', 'portable_html'].map((key) => {
    const resource = declaredDelivery[key];
    return [key, resource ? clean({ ...structuredClone(resource), status: normalizedStatus(resource.status) }) : { status: 'not_yet_produced' }];
  }));
  const publication = overrides.course_truth[capsule.course_id];
  if (publication?.publication_evidence) {
    const pdf = { status: 'verified', format: 'application/pdf', url: publication.edition, bytes: publication.publication_evidence.bytes, sha256: publication.publication_evidence.sha256, scope: 'whole_course', evidence: clean(structuredClone(publication.publication_evidence)) };
    if (expectedDelivery.primary.status !== 'verified') expectedDelivery.primary = structuredClone(pdf);
    expectedDelivery.pdf = pdf;
  }
  for (const [key, expected] of Object.entries(expectedDelivery)) assert.deepEqual(capsule.layers.learner[key], expected, `${capsule.course_id}/${key}: learner delivery authority drift.`);
  const deliveryStates = Object.values(expectedDelivery).map((entry) => entry.status);
  const aggregateDelivery = deliveryStates.includes('verified') ? 'verified' : deliveryStates.includes('available_unverified') ? 'available_unverified' : capsule.course.state === 'production' ? 'in_progress' : 'not_yet_produced';
  assert.equal(capsule.layers.learner.status, aggregateDelivery, `${capsule.course_id}: aggregate learner authority drift.`);
  assert.deepEqual(capsule.layers.learner.capabilities, Object.fromEntries(Object.entries(declaredDelivery.capabilities).map(([key, value]) => [key, normalizedStatus(value.status)])), `${capsule.course_id}: learner capability authority drift.`);
  assert.equal(capsule.layers.federation.zero_copy, true);
  assert.equal(capsule.layers.interoperability.status, 'verified');
  assert.equal(capsule.layers.interoperability.native_identity_preserved, true);
  assert.deepEqual(capsule.layers.interoperability.design_policy, expectedDesignPolicyRef, `${capsule.course_id}: design-policy binding drift.`);
  assert.deepEqual(capsule.layers.learner.tools, authorityToolsByCourse[capsule.course_id] ?? [], `${capsule.course_id}: learner tools drift from authority.`);
  for (const tool of capsule.layers.learner.tools) {
    assert.equal(tool.machine_data_is_learner_destination, false, `${capsule.course_id}/${tool.tool_id}: machine JSON cannot be the learner destination.`);
    assert.doesNotMatch(tool.href, /\.json(?:$|[?#])/i, `${capsule.course_id}/${tool.tool_id}: learner destination cannot be raw JSON.`);
    assert.match(tool.href, /(?:\/|\.html)$/, `${capsule.course_id}/${tool.tool_id}: learner route must be directory- or HTML-addressable.`);
    for (const [kind, fact] of Object.entries({ page: tool.page, resource: tool.resource, evidence: tool.evidence })) {
      const bytes = await readFile(resolve(project, fact.path));
      assert.equal(bytes.length, fact.bytes, `${capsule.course_id}/${tool.tool_id}/${kind}: byte-count drift.`);
      assert.equal(sha256(bytes), fact.sha256, `${capsule.course_id}/${tool.tool_id}/${kind}: SHA-256 drift.`);
    }
  }
  for (const layer of layerNames) assert.ok(statusValues.has(capsule.layers[layer].status), `${capsule.course_id}/${layer}: invalid status.`);
  const components = capsule.layers.federation.components;
  assert.equal(new Set(components.map(({ id }) => id)).size, components.length, `${capsule.course_id}: duplicate component identity.`);
  for (const component of components) {
    assert.ok(['public', 'unknown'].includes(component.access));
    assert.equal(component.rights_status, component.license ? 'available_unverified' : 'unknown', `${component.id}: component rights uncertainty missing or overstated.`);
    assert.deepEqual(component.provenance, component.url ? [{ kind: 'course_native_component_reference', locator: component.url, note: 'Reference provenance; independent rights verification is not implied.' }] : [], `${component.id}: component provenance reference drift.`);
  }
  for (const operation of nativePackages.operations.filter((entry) => entry.course_id === capsule.course_id)) {
    const actual = components.find((entry) => entry.id === operation.expected_component.id);
    assert.ok(actual, `${capsule.course_id}: native package reference missing.`);
    const { rights_status: _rights, provenance: _provenance, ...identity } = actual;
    assert.deepEqual(identity, operation.expected_component, `${capsule.course_id}: native package reference drift.`);
  }
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

assert.equal(capsules.filter(({ course }) => course.state === 'published').length, 35);
assert.equal(capsules.filter(({ course }) => course.state === 'production').length, 5);
assert.deepEqual(
  capsules.filter(({ course }) => course.state === 'production').map(({ course_id }) => course_id),
  ['A20', 'A30', 'B95', 'C140', 'D100'],
  'The exact five-role production set drifted.',
);
const d30 = byId.D30;
assert.equal(d30.course.state, 'published');
assert.equal(d30.course_native.status, 'verified');
assert.equal(d30.course_native.version, '2026.08.30-checkpoint.38');
assert.equal(d30.course_native.zenodo, 'https://doi.org/10.5281/zenodo.22182655');
assert.match(d30.course_native.corpus, /5 laboratorium/);
assert.doesNotMatch(d30.course_native.corpus, /2 irisan/);
assert.equal(d30.evidence.length, 1);
assert.equal(d30.evidence[0].bytes, 39843697);
assert.equal(d30.evidence[0].sha256, 'dda34267df928672e03e04b4c8a36d768aab2d33bc1194b269074da0d2d24e40');
assert.equal(d30.layers.learner.primary.status, 'verified');
assert.equal(d30.layers.learner.primary.format, 'text/html');
assert.equal(d30.layers.learner.primary.sha256, '417e580082b32178e99a9923c8d0fa13ae21fdb767edb8eb85a38d6b6a9f7bc9');
assert.deepEqual(d30.layers.learner.primary, d30.layers.learner.online_html);
assert.equal(d30.layers.learner.pdf.status, 'verified');
assert.equal(d30.layers.learner.pdf.bytes, 39843697);
assert.equal(d30.layers.learner.pdf.sha256, 'dda34267df928672e03e04b4c8a36d768aab2d33bc1194b269074da0d2d24e40');
assert.equal(d30.layers.learner.portable_html.status, 'verified');
assert.equal(d30.layers.learner.portable_html.bytes, 3029582);
assert.equal(d30.layers.learner.portable_html.sha256, 'e32dba5a896fb847192bbe944e7fd3db4d95f61ee57e33751bbff3108fca214a');
assert.equal(d30.layers.learner.portable_html.entry_point, 'reader/index.html');
assert.equal(d30.layers.learner.portable_html.inventory_count, 163);
assert.equal(d30.layers.learner.portable_html.dependency_free, true);
assert.equal(d30.layers.production.release_status, 'verified');
assert.equal(d30.layers.federation.components[0].status, 'verified');
assert.equal(d30.layers.educator.evidence[0].locator, 'https://zenodo.org/records/22182655');
const d40 = byId.D40;
assert.equal(d40.course.state, 'published');
assert.equal(d40.course_native.status, 'verified');
assert.equal(d40.course_native.version, '2026.08.31-d40-complete');
assert.equal(d40.course_native.repository, undefined, 'D40 must not invent a producer GitHub repository.');
assert.equal(d40.evidence.length, 1);
assert.equal(d40.layers.production.repository, undefined, 'D40 production layer must retain the GitHub-not-yet-produced truth.');
assert.equal(d40.layers.production.release_status, 'verified');
assert.equal(d40.layers.learner.primary.status, 'verified');
assert.equal(d40.layers.learner.primary.format, 'application/pdf');
assert.equal(d40.layers.learner.pdf.status, 'verified');
assert.equal(d40.layers.learner.portable_html.status, 'verified');
assert.equal(d40.layers.learner.portable_html.entry_point, 'reader/html/index.html');
assert.equal(d40.layers.learner.portable_html.inventory_count, 273);
assert.equal(d40.layers.learner.portable_html.dependency_free, true);
assert.equal(d40.layers.interoperability.semantic_adapter.status, 'available_unverified');
assert.equal(d40.layers.interoperability.semantic_adapter.mapping_scope, 'course_native_composite_backend_not_yet_consumed_by_global_runtime');
assert.deepEqual(
  identity('backend/course-capsule-v1/validation/D40_O010_INDEPENDENT_ANONYMOUS_READBACK.json', d40ReadbackBytes),
  {
    path: 'backend/course-capsule-v1/validation/D40_O010_INDEPENDENT_ANONYMOUS_READBACK.json',
    bytes: 7570,
    sha256: 'a34f5532208ad45c27d5c4b4108e51f5d3b76e8ded0ef5d334f31465f61e33f9',
  },
  'D40 independent public-readback receipt identity drifted.',
);
assert.equal(d40Readback.schema, 'o010-d40-complete-independent-anonymous-readback-v1');
assert.equal(d40Readback.authentication, 'none');
assert.equal(d40Readback.credential_material_recorded, false);
assert.equal(d40Readback.verdict, 'PASS_INDEPENDENT_ANONYMOUS_PUBLIC_READBACK');
assert.equal(d40Readback.record_id, 22184259);
assert.equal(d40Readback.doi, '10.5281/zenodo.22184259');
assert.equal(d40Readback.conceptdoi, '10.5281/zenodo.22059503');
assert.equal(d40Readback.public_api_url, `https://zenodo.org/api/records/${d40Readback.record_id}`);
assert.equal(d40Readback.public_record_url, `https://zenodo.org/records/${d40Readback.record_id}`);
assert.equal(d40Readback.doi, `10.5281/zenodo.${d40Readback.record_id}`);
assert.equal(d40Readback.file_count, 7);
assert.deepEqual(d40Readback.checks, {
  access_right_open: true,
  all_byte_counts_match: true,
  all_files_publicly_downloadable: true,
  all_md5_match: true,
  concept_alias_resolves_latest: true,
  concept_doi: true,
  concept_record_id: true,
  credential_recorded: false,
  credential_used: false,
  doi: true,
  exact_inventory: true,
  inventory_count: true,
  is_published_not_contradictory: true,
  latest_version_endpoint: true,
  local_vs_stream_sha256_match: true,
  primary_pdf_public_with_pdf_signature: true,
  published_status: true,
  record_id: true,
  submitted_flag: true,
  version_relation_parent: true,
});
const expectedD40Files = {
  'COMPONENT_LICENSE_BOUNDARIES.json': [2131, 'e95f98d79d5105e24d5c5808548b890dc8b14abd102bac2872a8d1519e85af4a'],
  'D40_COMPLETE_ID_20260831.zip': [9436983, 'a370bba5ddb54081387a484a304b24af92691c3bc167db964c486625a79add59'],
  'PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_LENGKAP.pdf': [4393637, 'c4e4f470eeb096129e7bf7306422d316c93aaeed99d2b12890e08f15777ac13f'],
  'RELEASE_MANIFEST.json': [92798, '3991fd2234e263134090c3686b93553dcab1215d86144509fd7937d5a4065a97'],
  'RELEASE_NOTES.md': [1233, 'b3e6678c75aced1badfe1469d9b6618cfe12899ecace14473f3acd3d2ef85da3'],
  'RELEASE_RECEIPT.json': [32377, '33287e8eefff35b7cc7362d77350e19f0ae99ed94cce5f1540c854a6f9c5df81'],
  'SHA256SUMS.txt': [30839, '14043e5c57e0e402ff2233fac9b40853fba65d30fb0962e6c964c7b38c4861c2'],
};
assert.equal(d40Readback.files.length, 7);
const d40ReadbackFiles = Object.fromEntries(d40Readback.files.map((entry) => [entry.filename, entry]));
assert.deepEqual(Object.keys(d40ReadbackFiles).sort(), Object.keys(expectedD40Files).sort());
for (const [name, [bytes, digest]] of Object.entries(expectedD40Files)) {
  const entry = d40ReadbackFiles[name];
  assert.equal(entry.verdict, 'PASS_EXACT_PUBLIC_BYTES', `${name}: D40 public-byte verdict drifted.`);
  assert.equal(
    entry.canonical_anonymous_download_url,
    `${d40Readback.public_api_url}/files/${encodeURIComponent(name)}/content`,
    `${name}: D40 canonical anonymous-download URL drifted.`,
  );
  assert.equal(entry.anonymous_download.bytes, bytes, `${name}: D40 public byte count drifted.`);
  assert.equal(entry.anonymous_download.sha256, digest, `${name}: D40 public SHA-256 drifted.`);
  assert.equal(entry.local.bytes, bytes, `${name}: D40 local byte count drifted.`);
  assert.equal(entry.local.sha256, digest, `${name}: D40 local SHA-256 drifted.`);
  assert.equal(entry.public_api_inventory.bytes, bytes, `${name}: D40 API byte count drifted.`);
  assert.equal(entry.anonymous_download.md5, entry.local.md5, `${name}: D40 public/local MD5 binding drifted.`);
  assert.equal(entry.anonymous_download.md5, entry.public_api_inventory.md5, `${name}: D40 public/API MD5 binding drifted.`);
}
assert.equal(
  d40Readback.files.reduce((total, entry) => total + entry.anonymous_download.bytes, 0),
  13989998,
  'D40 public-readback aggregate byte count drifted.',
);
const d40DoiUrl = `https://doi.org/${d40Readback.doi}`;
const d40RecordFileUrl = (fileName) => `${d40Readback.public_record_url}/files/${encodeURIComponent(fileName)}?download=1`;
const d40PdfReadback = d40ReadbackFiles['PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_LENGKAP.pdf'];
const d40ZipReadback = d40ReadbackFiles['D40_COMPLETE_ID_20260831.zip'];
const d40ManifestReadback = d40ReadbackFiles['RELEASE_MANIFEST.json'];
const d40PdfUrl = d40RecordFileUrl(d40PdfReadback.filename);
const d40ZipUrl = d40RecordFileUrl(d40ZipReadback.filename);
const d40ManifestUrl = d40RecordFileUrl(d40ManifestReadback.filename);
const d40FederationById = Object.fromEntries(d40.layers.federation.components.map((component) => [component.id, component]));

assert.equal(d40.course_native.zenodo, d40DoiUrl, 'D40 native DOI URL drifted from independent readback.');
assert.equal(d40.layers.production.zenodo, d40DoiUrl, 'D40 production DOI URL drifted from independent readback.');
assert.equal(d40.course_native.edition, d40PdfUrl, 'D40 native-edition URL drifted from independent PDF readback.');
assert.equal(d40.layers.production.edition, d40PdfUrl, 'D40 production-edition URL drifted from independent PDF readback.');

assert.equal(d40.evidence[0].file_name, d40PdfReadback.filename);
assert.equal(d40.evidence[0].bytes, d40PdfReadback.anonymous_download.bytes);
assert.equal(d40.evidence[0].sha256, d40PdfReadback.anonymous_download.sha256);
assert.equal(d40.layers.learner.primary.bytes, d40PdfReadback.anonymous_download.bytes);
assert.equal(d40.layers.learner.primary.sha256, d40PdfReadback.anonymous_download.sha256);
assert.equal(d40.layers.learner.primary.url, d40PdfUrl);
assert.equal(d40.layers.learner.pdf.evidence.file_name, d40PdfReadback.filename);
assert.equal(d40.layers.learner.pdf.evidence.bytes, d40PdfReadback.anonymous_download.bytes);
assert.equal(d40.layers.learner.pdf.evidence.sha256, d40PdfReadback.anonymous_download.sha256);
assert.equal(d40.layers.learner.pdf.bytes, d40PdfReadback.anonymous_download.bytes);
assert.equal(d40.layers.learner.pdf.sha256, d40PdfReadback.anonymous_download.sha256);
assert.equal(d40.layers.learner.pdf.url, d40PdfUrl);
assert.equal(d40FederationById['D40:primary'].url, d40PdfUrl);

assert.equal(d40.layers.learner.portable_html.bytes, d40ZipReadback.anonymous_download.bytes);
assert.equal(d40.layers.learner.portable_html.sha256, d40ZipReadback.anonymous_download.sha256);
assert.equal(d40.layers.learner.portable_html.url, d40ZipUrl);
assert.equal(d40FederationById['D40:d40-complete-package'].sha256, d40ZipReadback.anonymous_download.sha256);
assert.equal(d40FederationById['D40:d40-complete-package'].url, d40ZipUrl);

assert.equal(d40.layers.interoperability.semantic_adapter.evidence.length, 1);
assert.equal(d40.layers.interoperability.semantic_adapter.evidence[0].file_name, d40ManifestReadback.filename);
assert.equal(d40.layers.interoperability.semantic_adapter.evidence[0].bytes, d40ManifestReadback.anonymous_download.bytes);
assert.equal(d40.layers.interoperability.semantic_adapter.evidence[0].sha256, d40ManifestReadback.anonymous_download.sha256);
assert.equal(d40.layers.interoperability.semantic_adapter.evidence[0].locator, d40ManifestUrl);

for (const [label, evidence] of [
  ['course', d40.evidence[0]],
  ['educator', d40.layers.educator.evidence[0]],
  ['learner primary', d40.layers.learner.primary.evidence],
  ['learner PDF', d40.layers.learner.pdf.evidence],
  ['learner portable HTML', d40.layers.learner.portable_html.evidence],
]) {
  assert.equal(evidence.locator, d40Readback.public_record_url, `D40 ${label} evidence locator drifted from independent readback.`);
}
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
for (const id of ['A00', 'B10', 'C30', 'C40', 'C80', 'C130', 'D20', 'D60', 'D110']) {
  assert.equal(byId[id].layers.interoperability.semantic_adapter.status, 'verified');
  assert.equal(byId[id].layers.interoperability.semantic_adapter.contract_version, '2.3.1');
}
for (const id of ['C30', 'C40']) {
  const adapter = byId[id].layers.interoperability.semantic_adapter;
  assert.equal(adapter.mapping_scope, 'reversible_native_two_course_chapter_route_adapter');
  assert.deepEqual(adapter.evidence.map(({ kind }) => kind), ['central_adapter_manifest', 'canonical_admission_receipt']);
  assert.equal(adapter.evidence[0].sha256, '00b80a3f7406c96b375ddb390981dbd0a1f1e3d41e0d240c93b194694521c28a');
  assert.equal(adapter.evidence[1].sha256, '0c73d1be90d3a0318b70293eccf7b5ec58b41f323fbb2639b5c12b4451783e74');
  assert.equal(
    byId[id].layers.learner.portable_html.evidence.locator,
    'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/judson/route-evidence.json',
  );
}
const c80Adapter = byId.C80.layers.interoperability.semantic_adapter;
assert.equal(c80Adapter.mapping_scope, 'reversible_native_course_route_adapter');
assert.deepEqual(c80Adapter.evidence.map(({ kind }) => kind), ['central_adapter_manifest', 'canonical_admission_receipt', 'learner_route_validation']);
assert.equal(c80Adapter.evidence[0].sha256, '01974670c902a50d3e0166214f665286e0030a270a781a56413976be52ca4b01');
assert.equal(c80Adapter.evidence[1].sha256, '2a86c41e92f9c9ef7e215448967998504bd4c16e7ba8e680d795d155aebef9a7');
assert.equal(c80Adapter.evidence[2].sha256, '4774d889bf52244ef22181b0c90cfa2826ee4da401193d8229d2ac67181be6bc');
assert.equal(byId.C80.layers.learner.tools.length, 1);
assert.equal(byId.C80.layers.learner.tools[0].href, 'backend/openlogic/C80.html');
assert.equal(byId.C80.layers.learner.tools[0].primary, true);
assert.equal(byId.C80.layers.learner.tools[0].resource.sha256, 'e4a859bae966c0cc6272a814273c882b79cb7136f83ae83c147559c530921414');
const c130Adapter = byId.C130.layers.interoperability.semantic_adapter;
assert.equal(c130Adapter.mapping_scope, 'reversible_native_course_route_adapter');
assert.deepEqual(c130Adapter.evidence.map(({ kind }) => kind), ['central_adapter_manifest', 'canonical_admission_receipt', 'learner_route_validation']);
assert.equal(c130Adapter.evidence[0].sha256, 'cad2922d9bd1facb33cc9d54a9836bb168fe0b8d996d9d4ef2e5d8c26053f239');
assert.equal(c130Adapter.evidence[1].sha256, 'b311ab7d2a6a86af40174d051fbd8ef273a8536b34f0af77b76e5a1ce9b3397e');
assert.equal(c130Adapter.evidence[2].sha256, '6d9fa92226d7eee2ab29aba647d3cca0cee80b6cc2ee0bb0e14642216f9c8ae7');
assert.equal(byId.C130.layers.learner.tools.length, 1);
assert.equal(byId.C130.layers.learner.tools[0].href, 'backend/c130/C130.html');
assert.equal(byId.C130.layers.learner.tools[0].primary, true);
assert.equal(byId.C130.layers.learner.tools[0].resource.sha256, '8114562c963295577d8f845719061febed5993b5cbbe5fc4beb8ba235d7fd709');
for (const id of ['A10', 'D100']) {
  assert.equal(byId[id].layers.translation.terminology_status, 'in_progress');
  assert.equal(byId[id].layers.translation.corrections_status, 'in_progress');
  const evidence = byId[id].evidence.filter(({ sha256 }) => sha256 === 'd36a33be7b2dbd5d3a921f32f2b2f5dff81bc8e98d9ff66781314d9251167aa8');
  assert.ok(evidence.length >= 1, `${id}: native terminology witness is missing.`);
}

assert.equal(manifest.schema_version, '1.0.0');
assert.deepEqual(manifest.output, identity('generated/course-capsules.jsonl', jsonlBytes));
assert.deepEqual(manifest.projections.course_capsules_json, identity('generated/course-capsules.json', jsonBytes));
assert.equal(manifest.summary.course_count, 40);
assert.equal(manifest.summary.published_count, 35);
assert.equal(manifest.summary.production_count, 5);
assert.equal(manifest.summary.prerequisite_edge_count, 83);
assert.equal(manifest.summary.learner_tool_course_count, Object.keys(authorityToolsByCourse).length);
assert.equal(manifest.summary.learner_tool_count, authorityToolIds.length);
assert.equal(manifest.design_policy.profile, 'thin_format_neutral_zero_copy');
assert.deepEqual(manifest.design_policy.authority, identity('backend/course-capsule-v1/authority/backend-design-policy-v1.json', designPolicyBytes));
assert.deepEqual(manifest.design_policy.schema, identity('schemas/course-capsule-v1/backend-design-policy-v1.schema.json', designPolicySchemaBytes));
assert.deepEqual(manifest.design_policy.public_projection, expectedDesignPolicyRef.policy);
assert.equal(manifest.public_baseline.version, 'v0.62.12');
assert.deepEqual(manifest.public_baseline.authority, identity('backend/course-capsule-v1/authority/public-baseline-v0.62.12.json', publicBaselineBytes));
assert.deepEqual(manifest.public_baseline.schema, identity('schemas/course-capsule-v1/public-baseline-v1.schema.json', publicBaselineSchemaBytes));
assert.deepEqual(manifest.public_baseline.public_projection, expectedDesignPolicyRef.public_baseline);
assert.equal(manifest.terminology_policy.status, 'normative_for_central_integration');
assert.deepEqual(manifest.terminology_policy.authority, identity('backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json', terminologyPolicyBytes));
assert.deepEqual(manifest.terminology_policy.policy_schema, identity('schemas/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json', terminologyPolicySchemaBytes));
assert.deepEqual(manifest.terminology_policy.concept_schema, identity('schemas/course-capsule-v1/v2/terminology-concept-record-v1.schema.json', terminologyConceptSchemaBytes));
assert.deepEqual(manifest.terminology_policy.public_projection, {
  locator: 'https://kokunoyumeto.github.io/program-matematika-indonesia/data/course-capsule-v1/terminology-policy-v1/canonical-register-policy.json',
  bytes: terminologyPolicyBytes.length,
  sha256: sha256(terminologyPolicyBytes),
});
assert.equal(manifest.terminology_policy.probability_family_state, 'evidence_required');
assert.equal(manifest.terminology_policy.probability_family_concept_count, 9);
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
for (const pattern of forbiddenPatterns) {
  assert.doesNotMatch(text, pattern, `Forbidden public-capsule content: ${pattern}.`);
  assert.doesNotMatch(d40ReadbackBytes.toString('utf8'), pattern, `Forbidden D40 readback-receipt content: ${pattern}.`);
}
assert.doesNotMatch(text, /"owner(?:ship)?"\s*:/i, 'Capsule must not encode owner-control semantics.');

const [peerJsonl, peerJson, peerManifest] = await Promise.all([
  readFile(resolve(peerRoot, 'generated/course-capsules.jsonl')),
  readFile(resolve(peerRoot, 'generated/course-capsules.json')),
  readFile(resolve(peerRoot, 'generated/manifest.json')),
]);
assert.deepEqual(peerJsonl, jsonlBytes, 'Peer JSONL build differs.');
assert.deepEqual(peerJson, jsonBytes, 'Peer JSON projection differs.');
assert.deepEqual(peerManifest, manifestBytes, 'Peer manifest build differs.');
const peerReplay = { compared: true, byte_identical: true };

const educatorCourses = capsules.filter((capsule) => capsule.layers.educator.features.length || capsule.layers.educator.resources.length);
const learnerToolCourses = capsules.filter((capsule) => capsule.layers.learner.tools.length);
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
    published_count: 35,
    production_count: 5,
    public_access_policy_rows: 40,
    educator_course_count: educatorCourses.length,
    educator_resource_count: capsules.reduce((count, capsule) => count + capsule.layers.educator.resources.length, 0),
    learner_tool_course_count: learnerToolCourses.length,
    learner_tool_count: capsules.reduce((count, capsule) => count + capsule.layers.learner.tools.length, 0),
    learner_tool_authority_equality: 'pass',
    learner_delivery_authority_equality: 'pass',
    native_capability_specific_evidence: 'pass',
    component_rights_and_provenance: 'pass',
    native_package_evidence_bindings: nativePackages.operations.length,
    learner_tool_file_identity_replay: 'pass',
    learner_tool_html_destination_gate: 'pass',
    lebl_family_truth_overrides: 'pass',
    semantic_adapter_truth: 'pass',
    d40_completion_truth: 'pass',
    d40_independent_anonymous_readback: 'pass_7_of_7',
    design_policy_schema: 'pass',
    design_policy_bindings: 40,
    public_baseline_schema: 'pass',
    public_baseline_binding: 'pass',
    canonical_jsonl: 'pass',
    manifest_input_replay: 'pass',
    credential_profile_scan: 'pass',
  },
  artifacts: {
    native_package_references: identity('backend/course-capsule-v1/authority/native-package-references-v1.json', await readFile(paths.nativePackages)),
    course_capsules_jsonl: identity('generated/course-capsules.jsonl', jsonlBytes),
    course_capsules_json: identity('generated/course-capsules.json', jsonBytes),
    manifest_json: identity('generated/manifest.json', manifestBytes),
    schema_json: identity('schemas/course-capsule-v1/course-capsule-v1.schema.json', schemaBytes),
    design_policy_json: identity('backend/course-capsule-v1/authority/backend-design-policy-v1.json', designPolicyBytes),
    design_policy_schema_json: identity('schemas/course-capsule-v1/backend-design-policy-v1.schema.json', designPolicySchemaBytes),
    public_baseline_json: identity('backend/course-capsule-v1/authority/public-baseline-v0.62.12.json', publicBaselineBytes),
    public_baseline_schema_json: identity('schemas/course-capsule-v1/public-baseline-v1.schema.json', publicBaselineSchemaBytes),
    learner_tools_authority: identity('backend/authority/learner-tools-v1.json', learnerToolsBytes),
    d40_independent_anonymous_readback: identity('backend/course-capsule-v1/validation/D40_O010_INDEPENDENT_ANONYMOUS_READBACK.json', d40ReadbackBytes),
  },
  peer_replay: peerReplay,
};
const receiptBytes = Buffer.from(canonicalJson(receipt));
await mkdir(dirname(paths.receipt), { recursive: true });
await writeFile(paths.receipt, receiptBytes);
console.log(JSON.stringify({ status: 'pass', output_root: outputRoot, receipt: identity('validation/VALIDATION_RECEIPT.json', receiptBytes), ...receipt.checks, peer_replay: peerReplay }, null, 2));
