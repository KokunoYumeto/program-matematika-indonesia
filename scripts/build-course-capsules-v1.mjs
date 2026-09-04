import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { courses as authorityCourses } from '../docs/courses.js';
import { materializeLiveCourses } from '../docs/live-course-publications.js';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const outputOption = process.argv.find((value) => value.startsWith('--output-root='));
const outputValue = outputOption?.slice('--output-root='.length) ?? 'backend/course-capsule-v1';
const outputRoot = isAbsolute(outputValue) ? outputValue : resolve(project, outputValue);
const relative = {
  courses: 'docs/courses.js',
  overlay: 'docs/live-course-publications.js',
  learnerDelivery: 'backend/authority/learner-delivery-v1.json',
  learnerTools: 'backend/authority/learner-tools-v1.json',
  overrides: 'backend/course-capsule-v1/authority/integration-overrides-v1.json',
  nativePackages: 'backend/course-capsule-v1/authority/native-package-references-v1.json',
  designPolicy: 'backend/course-capsule-v1/authority/backend-design-policy-v1.json',
  publicBaseline: 'backend/course-capsule-v1/authority/public-baseline-v0.62.12.json',
  terminologyPolicy: 'backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json',
  schema: 'schemas/course-capsule-v1/course-capsule-v1.schema.json',
  designPolicySchema: 'schemas/course-capsule-v1/backend-design-policy-v1.schema.json',
  publicBaselineSchema: 'schemas/course-capsule-v1/public-baseline-v1.schema.json',
  terminologyPolicySchema: 'schemas/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json',
  terminologyConceptSchema: 'schemas/course-capsule-v1/v2/terminology-concept-record-v1.schema.json',
};
const output = {
  jsonl: 'generated/course-capsules.jsonl',
  json: 'generated/course-capsules.json',
  manifest: 'generated/manifest.json',
};
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const fileIdentity = (path, bytes) => ({ path, bytes: bytes.length, sha256: sha256(bytes) });
const publicReference = (path, bytes) => ({
  locator: `https://kokunoyumeto.github.io/program-matematika-indonesia/${path}`,
  bytes: bytes.length,
  sha256: sha256(bytes),
});
const sortValue = (value) => {
  if (Array.isArray(value)) return value.map(sortValue);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sortValue(value[key])]));
  }
  return value;
};
const canonicalJson = (value) => `${JSON.stringify(sortValue(value), null, 2)}\n`;
const canonicalLine = (value) => JSON.stringify(sortValue(value));
const courseSort = (left, right) => left.id.localeCompare(right.id, 'en', { numeric: true });
const clean = (value) => Object.fromEntries(Object.entries(value).filter(([, item]) => item !== undefined && item !== null));
const clone = (value) => structuredClone(value);
const normalizeStatus = (status) => ({
  absent: 'not_yet_produced',
  verified: 'verified',
  available_unverified: 'available_unverified',
  not_applicable: 'not_applicable',
  in_progress: 'in_progress',
  unknown: 'unknown',
}[status] ?? 'unknown');
const courseStateStatus = (state) => state === 'published' ? 'available_unverified' : 'in_progress';
const supplementStatus = (supplement) => {
  if (supplement.state === 'complete' && supplement.sha256) return 'verified';
  if (supplement.state === 'complete') return 'available_unverified';
  return 'in_progress';
};
const resourceTypeFeatures = {
  'problem-book': ['exercise_bank'],
  solutions: ['exercise_bank', 'staged_hints_answers_solutions', 'solution_provenance'],
  workbook: ['exercise_bank', 'activities_labs'],
  'companion-reader': ['exercise_bank'],
};

const inputBytes = Object.fromEntries(await Promise.all(Object.entries(relative).map(async ([key, path]) => [key, await readFile(resolve(project, path))])));
const learnerDelivery = JSON.parse(inputBytes.learnerDelivery.toString('utf8'));
const learnerTools = JSON.parse(inputBytes.learnerTools.toString('utf8'));
const overrides = JSON.parse(inputBytes.overrides.toString('utf8'));
const nativePackages = JSON.parse(inputBytes.nativePackages.toString('utf8'));
assert.equal(nativePackages.schema_id, 'interlanguage/course-native-package-references/v1');
const designPolicy = JSON.parse(inputBytes.designPolicy.toString('utf8'));
const publicBaseline = JSON.parse(inputBytes.publicBaseline.toString('utf8'));
const terminologyPolicy = JSON.parse(inputBytes.terminologyPolicy.toString('utf8'));
assert.equal(overrides.schema_version, '1.0.0');
assert.equal(learnerDelivery.schema_version, '1.0.0');
assert.equal(learnerTools.schema_id, 'interlanguage/program-matematika-indonesia/learner-tools/v1');
assert.equal(learnerTools.schema_version, '1.0.0');
assert.equal(designPolicy.schema_id, 'interlanguage/backend-design-policy/v1');
assert.equal(designPolicy.schema_version, '1.0.0');
assert.equal(designPolicy.profile, 'thin_format_neutral_zero_copy');
assert.equal(designPolicy.authority.course_native_authoritative, true);
assert.equal(designPolicy.authority.capsule_additive, true);
assert.equal(designPolicy.authority.native_identity_preserved, true);
assert.equal(designPolicy.authority.full_corpus_copied_into_capsule, false);
assert.equal(designPolicy.exchange.canonical_capsule_format, 'application/x-ndjson');
assert.equal(designPolicy.adapters.absence_blocks_release, false);
assert.equal(publicBaseline.schema_id, 'interlanguage/course-capsule-public-baseline/v1');
assert.equal(publicBaseline.schema_version, '1.0.0');
assert.equal(publicBaseline.release.tag, 'v0.62.12');
assert.equal(publicBaseline.release.asset_count, 100);
assert.equal(publicBaseline.zenodo.record_id, 22182000);
assert.equal(publicBaseline.zenodo.access, 'open');
assert.equal(terminologyPolicy.schema_id, 'interlanguage/program-matematika-indonesia-canonical-terminology-register-policy/v1');
assert.equal(terminologyPolicy.locale, 'id-ID');
assert.equal(terminologyPolicy.probability_family_audit.status, 'evidence_required');
assert.equal(terminologyPolicy.probability_family_audit.automatic_replacement_allowed, false);
assert.equal(terminologyPolicy.probability_family_audit.concepts.length, 9);
const designPolicyRef = {
  profile: designPolicy.profile,
  course_native_authoritative: designPolicy.authority.course_native_authoritative,
  capsule_additive: designPolicy.authority.capsule_additive,
  native_identity_preserved: designPolicy.authority.native_identity_preserved,
  content_copied_into_capsule: designPolicy.authority.full_corpus_copied_into_capsule,
  canonical_capsule_format: designPolicy.exchange.canonical_capsule_format,
  optional_adapters: [...designPolicy.adapters.optional],
  adapter_absence_blocks_release: designPolicy.adapters.absence_blocks_release,
  policy: publicReference('data/course-capsule-v1/backend-design-policy-v1.json', inputBytes.designPolicy),
  public_baseline: publicReference('data/course-capsule-v1/public-baseline-v0.62.12.json', inputBytes.publicBaseline),
};
const deliveryByCourse = Object.fromEntries(learnerDelivery.courses.map((row) => [row.course_id, row]));
assert.equal(new Set(learnerTools.courses.map(({ course_id }) => course_id)).size, learnerTools.courses.length, 'Learner-tool course IDs must be unique.');
const toolsByCourse = Object.fromEntries(learnerTools.courses.map((row) => [row.course_id, clone(row.tools)]));
for (const [courseId, tools] of Object.entries(overrides.learner_tools ?? {}).sort(([left], [right]) => left.localeCompare(right))) {
  assert.ok(Array.isArray(tools) && tools.length, `${courseId}: integration learner tools must be a non-empty array.`);
  toolsByCourse[courseId] ??= [];
  for (const tool of tools) {
    assert.equal(tool.machine_data_is_learner_destination, false, `${courseId}/${tool.tool_id}: machine data cannot be the learner destination.`);
    assert.equal(tool.page?.path, `docs/${tool.href}`, `${courseId}/${tool.tool_id}: learner href must identify its exact page.`);
    for (const key of ['page', 'resource', 'evidence']) {
      const fact = tool[key];
      assert.ok(fact && typeof fact.path === 'string' && !isAbsolute(fact.path), `${courseId}/${tool.tool_id}/${key}: invalid evidence path.`);
      assert.ok(!fact.path.split(/[\\/]/).includes('..'), `${courseId}/${tool.tool_id}/${key}: parent traversal is forbidden.`);
      const bytes = await readFile(resolve(project, fact.path));
      assert.deepEqual(fileIdentity(fact.path, bytes), fact, `${courseId}/${tool.tool_id}/${key}: file identity drift.`);
    }
    toolsByCourse[courseId].push(clone(tool));
  }
  toolsByCourse[courseId].sort((left, right) => left.tool_id.localeCompare(right.tool_id));
}
const allToolIds = Object.values(toolsByCourse).flatMap((tools) => tools.map(({ tool_id }) => tool_id));
assert.equal(new Set(allToolIds).size, allToolIds.length, 'Learner-tool IDs must be globally unique.');

const effectiveCourses = materializeLiveCourses(authorityCourses)
  .map((course) => {
    const truth = overrides.course_truth[course.id];
    if (!truth) return clone(course);
    const { publication_evidence: _publicationEvidence, ...fields } = truth;
    return { ...clone(course), ...fields };
  })
  .sort(courseSort);
assert.equal(effectiveCourses.length, 40);
assert.equal(new Set(effectiveCourses.map(({ id }) => id)).size, 40);
const effectiveCourseIds = new Set(effectiveCourses.map(({ id }) => id));
for (const courseId of Object.keys(toolsByCourse)) assert.ok(effectiveCourseIds.has(courseId), `Learner-tool authority refers to unknown course ${courseId}.`);

const normalizeDeliveryResource = (resource) => {
  if (!resource) return { status: 'not_yet_produced' };
  const result = clone(resource);
  result.status = normalizeStatus(result.status);
  return clean(result);
};

const capsules = effectiveCourses.map((course) => {
  const truth = overrides.course_truth[course.id];
  const adapter = overrides.semantic_adapters[course.id];
  // Adapter validation proves its mapping, not a course-native ledger,
  // build replay, educator alignment, or complete unit inventory.
  const nativeCapabilities = overrides.native_capabilities?.[course.id] ?? {};
  const nativeStatus = (key) => {
    const claim = nativeCapabilities[key];
    if (!claim) return 'unknown';
    assert.ok(['verified', 'legacy_verified', 'available_unverified', 'in_progress', 'not_yet_produced', 'not_applicable', 'unknown'].includes(claim.status), `${course.id}/${key}: invalid native capability status.`);
    assert.ok(claim.status === 'unknown' || claim.evidence?.length, `${course.id}/${key}: native capability needs specific evidence.`);
    return claim.status;
  };
  const deliverySource = deliveryByCourse[course.id];
  assert.ok(deliverySource, `Missing learner-delivery row ${course.id}.`);
  const tools = toolsByCourse[course.id] ?? [];
  const delivery = {
    primary: normalizeDeliveryResource(deliverySource.primary),
    online_html: normalizeDeliveryResource(deliverySource.online_html),
    pdf: normalizeDeliveryResource(deliverySource.pdf),
    epub: normalizeDeliveryResource(deliverySource.epub),
    portable_html: normalizeDeliveryResource(deliverySource.portable_html),
  };
  if (truth?.publication_evidence) {
    const verifiedPdf = {
      status: 'verified',
      format: 'application/pdf',
      url: truth.edition,
      bytes: truth.publication_evidence.bytes,
      sha256: truth.publication_evidence.sha256,
      scope: 'whole_course',
      evidence: clean(clone(truth.publication_evidence)),
    };
    // A verified semantic HTML route remains the learner-first entry when one
    // exists. Publication evidence still seals the PDF as the edition artifact.
    if (delivery.primary.status !== 'verified') delivery.primary = clone(verifiedPdf);
    delivery.pdf = clone(verifiedPdf);
  }
  const learnerStatuses = Object.values(delivery).map(({ status }) => status);
  const learnerStatus = learnerStatuses.includes('verified')
    ? 'verified'
    : learnerStatuses.includes('available_unverified')
      ? 'available_unverified'
      : course.state === 'production' ? 'in_progress' : 'not_yet_produced';

  const supplements = [...(course.supplements ?? [])].sort((left, right) => left.id.localeCompare(right.id));
  const educatorOverride = overrides.educator_evidence[course.id];
  const educatorResources = supplements
    .filter((supplement) => Object.hasOwn(resourceTypeFeatures, supplement.resourceType))
    .map((supplement) => clean({
      id: supplement.id,
      title: supplement.title,
      resource_type: supplement.resourceType,
      status: supplementStatus(supplement),
      url: supplement.url,
      scope: supplement.scope,
      license: supplement.license,
      pages: supplement.pages,
      bytes: supplement.bytes,
      sha256: supplement.sha256,
    }));
  educatorResources.push(...clone(educatorOverride?.resources ?? []));
  assert.equal(new Set(educatorResources.map(row=>row.id)).size,educatorResources.length,`${course.id}: duplicate educator resource identity.`);
  const educatorFeatures = new Set(educatorOverride?.features ?? []);
  for (const supplement of supplements) {
    for (const feature of resourceTypeFeatures[supplement.resourceType] ?? []) educatorFeatures.add(feature);
    if (/petunjuk|hint|jawaban|solution|penyelesaian/i.test(`${supplement.title} ${supplement.scope ?? ''}`)) {
      educatorFeatures.add('staged_hints_answers_solutions');
      educatorFeatures.add('solution_provenance');
    }
  }
  const educatorEvidence = educatorOverride ? [{
    kind: 'course_native_educator_material',
    locator: educatorOverride.locator,
    verified_date: educatorOverride.verified_date ?? overrides.recorded_date,
    note: 'Capability evidence is indexed without copying the course-native content.',
    ...(Number.isInteger(educatorOverride.bytes) && educatorOverride.bytes > 0
      ? { bytes: educatorOverride.bytes }
      : {}),
    ...(typeof educatorOverride.sha256 === 'string' && /^[0-9a-f]{64}$/.test(educatorOverride.sha256)
      ? { sha256: educatorOverride.sha256 }
      : {}),
  }] : [];
  const educatorStatus = educatorOverride?.status
    ?? (educatorFeatures.size || educatorResources.length
      ? 'available_unverified'
      : 'unknown');

  const primaryUrl = course.edition ?? course.zenodo ?? course.repository ?? course.reader;
  const courseNativeStatus = truth?.publication_evidence
    ? 'verified'
    : courseStateStatus(course.state);
  const components = [clean({
    id: `${course.id}:primary`,
    title: course.corpus,
    kind: 'course-native-primary',
    status: courseNativeStatus,
    access: primaryUrl ? 'public' : 'unknown',
    url: primaryUrl,
  })];
  for (const supplement of supplements) {
    components.push(clean({
      id: `${course.id}:${supplement.id}`,
      title: supplement.title,
      kind: supplement.resourceType,
      status: supplementStatus(supplement),
      access: supplement.url?.startsWith('http') ? 'public' : 'unknown',
      url: supplement.url,
      license: supplement.license,
      sha256: supplement.sha256,
    }));
  }
  for (const operation of nativePackages.operations.filter((item) => item.course_id === course.id)) {
    const replacement = clone(operation.expected_component);
    const index = components.findIndex((item) => item.id === replacement.id);
    if (operation.base_component) {
      assert.ok(index >= 0, `${course.id}: native package base component missing.`);
      assert.deepEqual(components[index], operation.base_component, `${course.id}: native package source changed; reconcile before replacing.`);
      components[index] = replacement;
    } else {
      assert.equal(index, -1, `${course.id}: native package reference collision.`);
      components.push(replacement);
    }
  }
  for (const component of components) {
    component.rights_status = component.license ? 'available_unverified' : 'unknown';
    component.provenance = component.url ? [{
      kind: 'course_native_component_reference',
      locator: component.url,
      note: 'Reference provenance; independent rights verification is not implied.',
    }] : [];
  }

  const semanticAdapter = adapter ? clone(adapter) : {
    status: 'not_yet_produced',
    mapping_scope: 'capsule_only',
    evidence: [],
  };
  const capsuleEvidence = truth?.publication_evidence ? [clean(clone(truth.publication_evidence))] : [];
  for (const claim of Object.values(nativeCapabilities)) capsuleEvidence.push(...clone(claim.evidence ?? []));

  return {
    $schema: 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/course-capsule-v1/course-capsule-v1.schema.json',
    schema_id: 'interlanguage/open-course-capsule/v1',
    schema_version: '1.0.0',
    course_id: course.id,
    locale: 'id-ID',
    learner_directed: true,
    open_access_policy: {
      public_access_required: true,
      private_access_forbidden: true,
      download_restriction_forbidden: true,
      educator_materials_public: true,
      rights_are_not_access_gates: true,
    },
    course: {
      title: course.title,
      level: course.level,
      topic: course.topic,
      state: course.state,
      purpose: course.purpose,
      outcome: course.outcome,
      prerequisites: [...course.prerequisites],
    },
    course_native: clean({
      status: courseNativeStatus,
      version: course.version,
      corpus: course.corpus,
      repository: course.repository,
      zenodo: course.zenodo,
      edition: course.edition,
      note: course.note,
    }),
    layers: {
      curriculum: {
        status: 'verified',
        course_identity: course.id,
        unit_identity_status: nativeStatus('unit_identity'),
        route_id: `route:${course.id}`,
        prerequisites: [...course.prerequisites],
        outcomes: [course.outcome],
      },
      translation: {
        status: courseStateStatus(course.state),
        source_locale: 'und',
        target_locale: 'id-ID',
        ledger_status: nativeStatus('translation_ledger'),
        terminology_status: nativeStatus('terminology'),
        rights_status: nativeStatus('translation_rights'),
        corrections_status: nativeStatus('corrections'),
      },
      production: clean({
        status: courseStateStatus(course.state),
        build_status: nativeStatus('build'),
        deterministic_replay_status: nativeStatus('deterministic_replay'),
        release_status: truth?.publication_evidence ? 'verified' : courseStateStatus(course.state),
        repository: course.repository,
        zenodo: course.zenodo,
        edition: course.edition,
      }),
      learner: {
        status: learnerStatus,
        ...delivery,
        capabilities: Object.fromEntries(Object.entries(deliverySource.capabilities).map(([key, value]) => [key, normalizeStatus(value.status)])),
        tools,
      },
      educator: {
        status: educatorStatus,
        shared_identity_scope: 'learner_and_educator_views_share_course_unit_concept_exercise_ids',
        unit_alignment_status: nativeStatus('educator_unit_alignment'),
        unlisted_features_status: 'unknown',
        features: [...educatorFeatures].sort(),
        resources: educatorResources,
        evidence: educatorEvidence,
      },
      federation: {
        status: 'verified',
        zero_copy: true,
        components,
      },
      interoperability: {
        status: 'verified',
        capsule_contract: 'open-course-capsule/1.0.0',
        native_identity_preserved: true,
        mapping_scope: 'course_level_without_content_copy',
        semantic_adapter: semanticAdapter,
        design_policy: clone(designPolicyRef),
      },
    },
    evidence: capsuleEvidence,
  };
});

const jsonlBytes = Buffer.from(`${capsules.map(canonicalLine).join('\n')}\n`);
const jsonBytes = Buffer.from(canonicalJson(capsules));
const edges = capsules.flatMap((capsule) => capsule.course.prerequisites.map((prerequisite) => [prerequisite, capsule.course_id]));
const educatorCourseCount = capsules.filter((capsule) => capsule.layers.educator.features.length || capsule.layers.educator.resources.length).length;
const learnerToolCourses = capsules.filter((capsule) => capsule.layers.learner.tools.length);
const manifest = {
  schema_id: 'interlanguage/open-course-capsule-manifest/v1',
  schema_version: '1.0.0',
  inputs: Object.entries(relative).map(([key, path]) => ({ key, ...fileIdentity(path, inputBytes[key]) })).sort((left, right) => left.path.localeCompare(right.path)),
  output: fileIdentity(output.jsonl, jsonlBytes),
  projections: {
    course_capsules_json: fileIdentity(output.json, jsonBytes),
  },
  design_policy: {
    profile: designPolicy.profile,
    authority: fileIdentity(relative.designPolicy, inputBytes.designPolicy),
    schema: fileIdentity(relative.designPolicySchema, inputBytes.designPolicySchema),
    public_projection: designPolicyRef.policy,
  },
  public_baseline: {
    version: publicBaseline.release.tag,
    authority: fileIdentity(relative.publicBaseline, inputBytes.publicBaseline),
    schema: fileIdentity(relative.publicBaselineSchema, inputBytes.publicBaselineSchema),
    public_projection: designPolicyRef.public_baseline,
  },
  terminology_policy: {
    status: terminologyPolicy.status,
    authority: fileIdentity(relative.terminologyPolicy, inputBytes.terminologyPolicy),
    policy_schema: fileIdentity(relative.terminologyPolicySchema, inputBytes.terminologyPolicySchema),
    concept_schema: fileIdentity(relative.terminologyConceptSchema, inputBytes.terminologyConceptSchema),
    public_projection: publicReference('data/course-capsule-v1/terminology-policy-v1/canonical-register-policy.json', inputBytes.terminologyPolicy),
    probability_family_state: terminologyPolicy.probability_family_audit.status,
    probability_family_concept_count: terminologyPolicy.probability_family_audit.concepts.length,
  },
  summary: {
    course_count: capsules.length,
    published_count: capsules.filter(({ course }) => course.state === 'published').length,
    production_count: capsules.filter(({ course }) => course.state === 'production').length,
    prerequisite_edge_count: edges.length,
    educator_course_count: educatorCourseCount,
    educator_resource_count: capsules.reduce((count, capsule) => count + capsule.layers.educator.resources.length, 0),
    learner_tool_course_count: learnerToolCourses.length,
    learner_tool_count: capsules.reduce((count, capsule) => count + capsule.layers.learner.tools.length, 0),
    verified_semantic_adapter_count: capsules.filter((capsule) => capsule.layers.interoperability.semantic_adapter.status === 'verified').length,
    legacy_semantic_adapter_count: capsules.filter((capsule) => capsule.layers.interoperability.semantic_adapter.status === 'legacy_verified').length,
  },
  policy: {
    learner_directed: true,
    open_access_required: true,
    course_native_canonical: true,
    content_copied_into_capsule: false,
    seven_layers_required: true,
    profile: designPolicy.profile,
    native_formats_constrained: designPolicy.exchange.course_native_formats_constrained,
    optional_adapters: [...designPolicy.adapters.optional],
    adapter_absence_blocks_release: designPolicy.adapters.absence_blocks_release,
  },
};
const manifestBytes = Buffer.from(canonicalJson(manifest));

await mkdir(resolve(outputRoot, 'generated'), { recursive: true });
await Promise.all([
  writeFile(resolve(outputRoot, output.jsonl), jsonlBytes),
  writeFile(resolve(outputRoot, output.json), jsonBytes),
  writeFile(resolve(outputRoot, output.manifest), manifestBytes),
]);

console.log(JSON.stringify({
  status: 'pass',
  output_root: outputRoot,
  jsonl: fileIdentity(output.jsonl, jsonlBytes),
  json: fileIdentity(output.json, jsonBytes),
  manifest: fileIdentity(output.manifest, manifestBytes),
  ...manifest.summary,
}, null, 2));
