import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { basename, dirname, resolve } from 'node:path';
import { gzipSync } from 'node:zlib';
import { courses, nextCourseIdsById, program, topics } from '../docs/courses.js';
import { learnerDeliveryByCourseId, learnerDeliveryRows } from '../docs/learner-delivery.js';
import { learnerToolsByCourseId, learnerToolsRows } from '../docs/learner-tools.js';
import {
  deriveNextCourseIdsById,
  liveCoursePublications,
  materializeLiveCourses,
} from '../docs/live-course-publications.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const readJson = async (relative) => JSON.parse(await readFile(resolve(root, relative), 'utf8'));
const readOptionalJson = async (relative) => {
  try {
    return JSON.parse(await readFile(resolve(root, relative), 'utf8'));
  } catch (error) {
    if (error?.code === 'ENOENT') return null;
    throw error;
  }
};
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const escapeRegex = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const effectiveCourses = materializeLiveCourses(courses);
const effectiveCoursesById = new Map(effectiveCourses.map((course) => [course.id, course]));
const effectiveNextCourseIdsById = deriveNextCourseIdsById(effectiveCourses);
const effectivePublishedCourses = effectiveCourses.filter(({ state }) => state === 'published');
const effectivePublishedRecordDois = new Set(effectivePublishedCourses.map(({ zenodo }) => zenodo).filter(Boolean));

const [
  html,
  app,
  livePublicationsModule,
  learnerStateModule,
  catalogSchema,
  authorityBytes,
  publicAuthorityBytes,
  learnerReadModelBytes,
  educationalAccess,
  educationalAccessSchemaBytes,
  learnerStateSchemaBytes,
  publicLearnerStateSchemaBytes,
  b95Landing,
  d40ReaderIndexBytes,
  d30Landing,
  d40Landing,
  c100Landing,
  c100ReaderBytes,
  c100ReaderStyleBytes,
  c100SolutionBytes,
  c100RouteManifest,
  d20RouteManifest,
  legacyD20RouteBytes,
  d20RouteBytes,
  routeManifestV21,
  rootReadme,
  backendV23Readme,
  schemaV23Index,
] = await Promise.all([
  readFile(resolve(root, 'docs/index.html'), 'utf8'),
  readFile(resolve(root, 'docs/app.js'), 'utf8'),
  readFile(resolve(root, 'docs/live-course-publications.js'), 'utf8'),
  readFile(resolve(root, 'docs/learner-state.js'), 'utf8'),
  readJson('schemas/catalog-v1.schema.json'),
  readFile(resolve(root, 'backend/authority/curriculum-authority-v1.json')),
  readFile(resolve(root, 'docs/data/curriculum-authority-v1.json')),
  readFile(resolve(root, 'docs/data/learner-read-model.json')),
  readJson('docs/data/educational-access.json'),
  readFile(resolve(root, 'docs/schema/educational-access-federation-v1.schema.json')),
  readFile(resolve(root, 'schemas/v1/learner-state-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/v1/learner-state-v1.schema.json')),
  readFile(resolve(root, 'docs/id-ID/courses/B95/index.html'), 'utf8'),
  readFile(resolve(root, 'docs/readers/d40/unit14/index.html')),
  readFile(resolve(root, 'docs/id-ID/courses/D30/index.html'), 'utf8'),
  readFile(resolve(root, 'docs/id-ID/courses/D40/index.html'), 'utf8'),
  readFile(resolve(root, 'docs/id-ID/courses/C100/index.html'), 'utf8'),
  readFile(resolve(root, 'docs/id-ID/courses/C100/reader/index.html')),
  readFile(resolve(root, 'docs/id-ID/courses/C100/reader/style.css')),
  readFile(resolve(root, 'docs/id-ID/courses/C100/solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf')),
  readJson('docs/data/unit-route-C100-v2.1.json'),
  readJson('docs/data/unit-route-D20-v2.1.json'),
  readFile(resolve(root, 'docs/data/unit-route-v2.1.json')),
  readFile(resolve(root, 'docs/data/unit-route-D20-v2.1.json')),
  readJson('docs/data/unit-routes-v2.1.json'),
  readFile(resolve(root, 'README.md'), 'utf8'),
  readFile(resolve(root, 'backend/v2.3/README.md'), 'utf8'),
  readFile(resolve(root, 'docs/schema/v2.3/index.html'), 'utf8'),
]);

const [
  stylesBytes,
  coursesModuleBytes,
  deliveryModuleBytes,
  learnerToolsModuleBytes,
  learnerDeliveryAuthorityBytes,
  learnerDeliveryPublicBytes,
  learnerDeliverySchemaBytes,
  publicLearnerDeliverySchemaBytes,
  learnerToolsAuthorityBytes,
  learnerToolsPublicBytes,
  learnerToolsSchemaBytes,
  publicLearnerToolsSchemaBytes,
  designPolicyAuthorityBytes,
  designPolicyPublicBytes,
  designPolicySchemaBytes,
  designPolicyPublicSchemaBytes,
  publicBaselineAuthorityBytes,
  publicBaselinePublicBytes,
  publicBaselineSchemaBytes,
  publicBaselinePublicSchemaBytes,
  a00AssessmentMapBytes,
  a00AnchorAuditBytes,
  a00AssessmentHtmlBytes,
  a00AssessmentStyleBytes,
  a00AssessmentScriptBytes,
  a00AssessmentSchemaBytes,
  modularBackendPatternAuthorityBytes,
  modularBackendPatternPublicBytes,
  v23AdapterIndexAuthorityBytes,
  v23AdapterIndexPublicBytes,
  v23AdapterIndexSchemaBytes,
  v23AdapterIndexPublicSchemaBytes,
  standaloneBytes,
] = await Promise.all([
  readFile(resolve(root, 'docs/styles.css')),
  readFile(resolve(root, 'docs/courses.js')),
  readFile(resolve(root, 'docs/learner-delivery.js')),
  readFile(resolve(root, 'docs/learner-tools.js')),
  readFile(resolve(root, 'backend/authority/learner-delivery-v1.json')),
  readFile(resolve(root, 'docs/data/learner-delivery-v1.json')),
  readFile(resolve(root, 'schemas/v1/learner-delivery-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/v1/learner-delivery-v1.schema.json')),
  readFile(resolve(root, 'backend/authority/learner-tools-v1.json')),
  readFile(resolve(root, 'docs/data/learner-tools-v1.json')),
  readFile(resolve(root, 'schemas/v1/learner-tools-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/v1/learner-tools-v1.schema.json')),
  readFile(resolve(root, 'backend/course-capsule-v1/authority/backend-design-policy-v1.json')),
  readFile(resolve(root, 'docs/data/course-capsule-v1/backend-design-policy-v1.json')),
  readFile(resolve(root, 'schemas/course-capsule-v1/backend-design-policy-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/course-capsule-v1/backend-design-policy-v1.schema.json')),
  readFile(resolve(root, 'backend/course-capsule-v1/authority/public-baseline-v0.62.12.json')),
  readFile(resolve(root, 'docs/data/course-capsule-v1/public-baseline-v0.62.12.json')),
  readFile(resolve(root, 'schemas/course-capsule-v1/public-baseline-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/course-capsule-v1/public-baseline-v1.schema.json')),
  readFile(resolve(root, 'docs/id-ID/courses/A00/latihan/assessment-map-v1.json')),
  readFile(resolve(root, 'docs/id-ID/courses/A00/latihan/anchor-audit-v1.json')),
  readFile(resolve(root, 'docs/id-ID/courses/A00/latihan/index.html')),
  readFile(resolve(root, 'docs/id-ID/courses/A00/latihan/latihan.css')),
  readFile(resolve(root, 'docs/id-ID/courses/A00/latihan/latihan.js')),
  readFile(resolve(root, 'schemas/v1/a00-assessment-map-v1.schema.json')),
  readFile(resolve(root, 'backend/authority/modular-backend-pattern-index-v1.json')),
  readFile(resolve(root, 'docs/data/modular-backend-pattern-index-v1.json')),
  readFile(resolve(root, 'backend/authority/v23-adapter-index-v1.json')),
  readFile(resolve(root, 'docs/data/v23-adapter-index-v1.json')),
  readFile(resolve(root, 'schemas/v1/v23-adapter-index-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/v1/v23-adapter-index-v1.schema.json')),
  readFile(resolve(root, 'docs/peta-belajar-luring.html')),
]);

const authority = JSON.parse(authorityBytes.toString('utf8'));
const catalog = authority.catalog;
const learnerReadModel = JSON.parse(learnerReadModelBytes.toString('utf8'));
const learnerDelivery = JSON.parse(learnerDeliveryAuthorityBytes.toString('utf8'));
const learnerTools = JSON.parse(learnerToolsAuthorityBytes.toString('utf8'));
const designPolicy = JSON.parse(designPolicyAuthorityBytes.toString('utf8'));
const publicBaseline = JSON.parse(publicBaselineAuthorityBytes.toString('utf8'));
const a00AssessmentMap = JSON.parse(a00AssessmentMapBytes.toString('utf8'));
const a00AnchorAudit = JSON.parse(a00AnchorAuditBytes.toString('utf8'));
const modularBackendPatternIndex = JSON.parse(modularBackendPatternAuthorityBytes.toString('utf8'));
const v23AdapterIndex = JSON.parse(v23AdapterIndexAuthorityBytes.toString('utf8'));
const [
  integrationOverrideBytes,
  courseCapsulePublicBytes,
  v23AdapterIndexV2AuthorityBytes,
  v23AdapterIndexV2PublicBytes,
  modularBackendPatternV2AuthorityBytes,
  modularBackendPatternV2PublicBytes,
  featureAdoptionAuthorityBytes,
  featureAdoptionPublicBytes,
  comparisonEvidenceAuthorityBytes,
  comparisonEvidencePublicBytes,
  snapshotV2ReceiptAuthorityBytes,
  snapshotV2ReceiptPublicBytes,
  v23AdapterIndexV2SchemaBytes,
  v23AdapterIndexV2PublicSchemaBytes,
  modularBackendPatternV2SchemaBytes,
  modularBackendPatternV2PublicSchemaBytes,
  featureAdoptionSchemaBytes,
  featureAdoptionPublicSchemaBytes,
  comparisonEvidenceSchemaBytes,
  comparisonEvidencePublicSchemaBytes,
  openLogicHtmlBytes,
  openLogicRouteBytes,
  openLogicValidationBytes,
  c130HtmlBytes,
  c130RouteBytes,
  c130ValidationBytes,
  terminologyReadmeAuthorityBytes,
  terminologyReadmePublicBytes,
  terminologyConcordanceAuthorityBytes,
  terminologyConcordancePublicBytes,
  terminologyChecksumsAuthorityBytes,
  terminologyChecksumsPublicBytes,
  terminologyPolicyReadmeAuthorityBytes,
  terminologyPolicyReadmePublicBytes,
  terminologyPolicyAuthorityBytes,
  terminologyPolicyPublicBytes,
  terminologyPolicyChecksumsAuthorityBytes,
  terminologyPolicyChecksumsPublicBytes,
  terminologyPolicySchemaBytes,
  terminologyPolicyPublicSchemaBytes,
  terminologyConceptSchemaBytes,
  terminologyConceptPublicSchemaBytes,
] = await Promise.all([
  readFile(resolve(root, 'backend/course-capsule-v1/authority/integration-overrides-v1.json')),
  readFile(resolve(root, 'docs/data/course-capsule-v1/course-capsules.json')),
  readFile(resolve(root, 'backend/course-capsule-v1/authority/v23-adapter-index-v2.json')),
  readFile(resolve(root, 'docs/data/v23-adapter-index-v2.json')),
  readFile(resolve(root, 'backend/course-capsule-v1/authority/modular-backend-pattern-index-v2.json')),
  readFile(resolve(root, 'docs/data/modular-backend-pattern-index-v2.json')),
  readFile(resolve(root, 'backend/course-capsule-v1/authority/feature-adoption-provenance-v1.json')),
  readFile(resolve(root, 'docs/data/feature-adoption-provenance-v1.json')),
  readFile(resolve(root, 'backend/course-capsule-v1/authority/comparison-evidence-manifest-v1.json')),
  readFile(resolve(root, 'docs/data/comparison-evidence-manifest-v1.json')),
  readFile(resolve(root, 'backend/course-capsule-v1/validation/MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json')),
  readFile(resolve(root, 'docs/data/modular-backend-snapshot-v2-validation-receipt.json')),
  readFile(resolve(root, 'schemas/course-capsule-v1/v2/v23-adapter-index-v2.schema.json')),
  readFile(resolve(root, 'docs/schema/v2/v23-adapter-index-v2.schema.json')),
  readFile(resolve(root, 'schemas/course-capsule-v1/v2/modular-backend-pattern-index-v2.schema.json')),
  readFile(resolve(root, 'docs/schema/v2/modular-backend-pattern-index-v2.schema.json')),
  readFile(resolve(root, 'schemas/course-capsule-v1/v2/feature-adoption-provenance-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/v2/feature-adoption-provenance-v1.schema.json')),
  readFile(resolve(root, 'schemas/course-capsule-v1/v2/comparison-evidence-manifest-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/v2/comparison-evidence-manifest-v1.schema.json')),
  readFile(resolve(root, 'docs/backend/openlogic/C80.html')),
  readFile(resolve(root, 'docs/backend/openlogic/learner-route.json')),
  readFile(resolve(root, 'docs/backend/openlogic/validation.json')),
  readFile(resolve(root, 'docs/backend/c130/C130.html')),
  readFile(resolve(root, 'docs/backend/c130/learner-route.json')),
  readFile(resolve(root, 'docs/backend/c130/validation.json')),
  readFile(resolve(root, 'backend/course-capsule-v1/authority/native-terminology-qa/unib-teori-bilangan-20260831/README.md')),
  readFile(resolve(root, 'docs/data/course-capsule-v1/native-terminology-qa/unib-teori-bilangan-20260831/README.md')),
  readFile(resolve(root, 'backend/course-capsule-v1/authority/native-terminology-qa/unib-teori-bilangan-20260831/terminology_concordance.json')),
  readFile(resolve(root, 'docs/data/course-capsule-v1/native-terminology-qa/unib-teori-bilangan-20260831/terminology_concordance.json')),
  readFile(resolve(root, 'backend/course-capsule-v1/authority/native-terminology-qa/unib-teori-bilangan-20260831/checksums.sha256')),
  readFile(resolve(root, 'docs/data/course-capsule-v1/native-terminology-qa/unib-teori-bilangan-20260831/checksums.sha256')),
  readFile(resolve(root, 'backend/course-capsule-v1/authority/terminology-policy-v1/README.md')),
  readFile(resolve(root, 'docs/data/course-capsule-v1/terminology-policy-v1/README.md')),
  readFile(resolve(root, 'backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json')),
  readFile(resolve(root, 'docs/data/course-capsule-v1/terminology-policy-v1/canonical-register-policy.json')),
  readFile(resolve(root, 'backend/course-capsule-v1/authority/terminology-policy-v1/checksums.sha256')),
  readFile(resolve(root, 'docs/data/course-capsule-v1/terminology-policy-v1/checksums.sha256')),
  readFile(resolve(root, 'schemas/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json')),
  readFile(resolve(root, 'schemas/course-capsule-v1/v2/terminology-concept-record-v1.schema.json')),
  readFile(resolve(root, 'docs/schema/course-capsule-v1/v2/terminology-concept-record-v1.schema.json')),
]);
const integrationOverrides = JSON.parse(integrationOverrideBytes.toString('utf8'));
const courseCapsules = JSON.parse(courseCapsulePublicBytes.toString('utf8'));
const v23AdapterIndexV2 = JSON.parse(v23AdapterIndexV2AuthorityBytes.toString('utf8'));
const modularBackendPatternV2 = JSON.parse(modularBackendPatternV2AuthorityBytes.toString('utf8'));
const featureAdoption = JSON.parse(featureAdoptionAuthorityBytes.toString('utf8'));
const comparisonEvidence = JSON.parse(comparisonEvidenceAuthorityBytes.toString('utf8'));
const snapshotV2Receipt = JSON.parse(snapshotV2ReceiptAuthorityBytes.toString('utf8'));
const openLogicRoute = JSON.parse(openLogicRouteBytes.toString('utf8'));
const openLogicValidation = JSON.parse(openLogicValidationBytes.toString('utf8'));
const c130Route = JSON.parse(c130RouteBytes.toString('utf8'));
const c130Validation = JSON.parse(c130ValidationBytes.toString('utf8'));
const terminologyConcordance = JSON.parse(terminologyConcordanceAuthorityBytes.toString('utf8'));
const terminologyPolicy = JSON.parse(terminologyPolicyAuthorityBytes.toString('utf8'));
const publicationReceipts = (await Promise.all([
  readJson('PUBLICATION_RECEIPT_v0.62.12.json'),
  readOptionalJson('PUBLICATION_RECEIPT_v0.62.13.json'),
])).filter(Boolean);
assert.ok(catalog && typeof catalog === 'object', 'Otoritas tidak memuat katalog kanonik.');
assert.deepEqual(publicAuthorityBytes, authorityBytes, 'Salinan otoritas publik harus identik byte demi byte.');
assert.deepEqual(courses, catalog.courses, 'Proyeksi courses.js berbeda dari katalog otoritas.');
assert.deepEqual(topics, catalog.topics, 'Topik courses.js berbeda dari katalog otoritas.');
assert.deepEqual(program, catalog.program, 'Metadata program courses.js berbeda dari katalog otoritas.');
assert.deepEqual(
  learnerReadModel.courses.map(({ federation, ...course }) => course),
  catalog.courses,
  'Model baca pelajar berbeda dari katalog otoritas.',
);
assert.deepEqual(learnerReadModel.program, catalog.program, 'Program model baca berbeda dari otoritas.');
assert.deepEqual(learnerReadModel.topics, catalog.topics, 'Topik model baca berbeda dari otoritas.');
assert.equal(learnerReadModel.provenance.authority_sha256, sha256(authorityBytes));
assert.deepEqual(learnerDeliveryPublicBytes, learnerDeliveryAuthorityBytes, 'Salinan publik learner-delivery harus identik byte demi byte.');
assert.deepEqual(publicLearnerDeliverySchemaBytes, learnerDeliverySchemaBytes, 'Salinan skema learner-delivery harus identik byte demi byte.');
assert.deepEqual(learnerToolsPublicBytes, learnerToolsAuthorityBytes, 'Salinan publik learner-tools harus identik byte demi byte.');
assert.deepEqual(publicLearnerToolsSchemaBytes, learnerToolsSchemaBytes, 'Salinan skema learner-tools harus identik byte demi byte.');
assert.deepEqual(modularBackendPatternPublicBytes, modularBackendPatternAuthorityBytes, 'Snapshot backend v1 publik harus identik dengan otoritas immutable.');
assert.deepEqual(v23AdapterIndexPublicBytes, v23AdapterIndexAuthorityBytes, 'Indeks adapter v1 publik harus identik dengan otoritas immutable.');
assert.deepEqual(v23AdapterIndexV2PublicBytes, v23AdapterIndexV2AuthorityBytes, 'Indeks adapter v2 publik harus identik dengan otoritas.');
assert.deepEqual(modularBackendPatternV2PublicBytes, modularBackendPatternV2AuthorityBytes, 'Pola backend v2 publik harus identik dengan otoritas.');
assert.deepEqual(featureAdoptionPublicBytes, featureAdoptionAuthorityBytes, 'Ledger adopsi fitur publik harus identik dengan otoritas.');
assert.deepEqual(comparisonEvidencePublicBytes, comparisonEvidenceAuthorityBytes, 'Manifest bukti perbandingan publik harus identik dengan otoritas.');
assert.deepEqual(snapshotV2ReceiptPublicBytes, snapshotV2ReceiptAuthorityBytes, 'Receipt snapshot v2 publik harus identik dengan receipt validasi.');
assert.deepEqual(v23AdapterIndexV2PublicSchemaBytes, v23AdapterIndexV2SchemaBytes, 'Skema adapter v2 publik harus identik.');
assert.deepEqual(modularBackendPatternV2PublicSchemaBytes, modularBackendPatternV2SchemaBytes, 'Skema pola backend v2 publik harus identik.');
assert.deepEqual(featureAdoptionPublicSchemaBytes, featureAdoptionSchemaBytes, 'Skema adopsi fitur publik harus identik.');
assert.deepEqual(comparisonEvidencePublicSchemaBytes, comparisonEvidenceSchemaBytes, 'Skema bukti perbandingan publik harus identik.');
assert.deepEqual(terminologyReadmePublicBytes, terminologyReadmeAuthorityBytes, 'README terminologi publik harus identik.');
assert.deepEqual(terminologyConcordancePublicBytes, terminologyConcordanceAuthorityBytes, 'Konkordansi terminologi publik harus identik.');
assert.deepEqual(terminologyChecksumsPublicBytes, terminologyChecksumsAuthorityBytes, 'Checksum terminologi publik harus identik.');
assert.deepEqual(terminologyPolicyReadmePublicBytes, terminologyPolicyReadmeAuthorityBytes, 'README kebijakan terminologi publik harus identik.');
assert.deepEqual(terminologyPolicyPublicBytes, terminologyPolicyAuthorityBytes, 'Kebijakan terminologi publik harus identik.');
assert.deepEqual(terminologyPolicyChecksumsPublicBytes, terminologyPolicyChecksumsAuthorityBytes, 'Checksum kebijakan terminologi publik harus identik.');
assert.deepEqual(terminologyPolicyPublicSchemaBytes, terminologyPolicySchemaBytes, 'Skema kebijakan terminologi publik harus identik.');
assert.deepEqual(terminologyConceptPublicSchemaBytes, terminologyConceptSchemaBytes, 'Skema rekaman konsep terminologi publik harus identik.');
assert.equal(v23AdapterIndex.adapters.length, 5);
assert.equal(v23AdapterIndex.summary.proof_roles, 5);
assert.deepEqual(v23AdapterIndexV2.summary, {
  curriculum_roles: 40,
  role_bindings: 9,
  published_role_bindings: 9,
  pending_role_bindings: 0,
  distinct_adapter_packages: 8,
  published_adapter_packages: 8,
  pending_adapter_packages: 0,
  represented_native_families: 8,
  unbound_roles: 31,
  families_without_local_adapter: 25,
  families_without_public_replay_complete_adapter: 25,
  package_deduplicated_canonical_records: 285829,
});
assert.equal(modularBackendPatternV2.families.length, 33);
assert.equal(featureAdoption.layers.length, 7);
assert.equal(featureAdoption.snapshot_id, v23AdapterIndexV2.snapshot.snapshot_id);
assert.equal(comparisonEvidence.snapshot_id, v23AdapterIndexV2.snapshot.snapshot_id);
assert.equal(snapshotV2Receipt.status, 'pass');
assert.deepEqual(snapshotV2Receipt.summary, v23AdapterIndexV2.summary);
assert.equal(openLogicRoute.course_id, 'C80');
assert.equal(openLogicRoute.primary_learner_action.kind, 'linked_pdf');
assert.equal(openLogicRoute.primary_learner_action.pages, 1116);
assert.equal(openLogicValidation.state, 'pass');
assert.equal(openLogicValidation.semantic_counts.native_units, 722);
assert.equal(openLogicValidation.native_html_claimed, false);
assert.doesNotMatch(openLogicHtmlBytes.toString('utf8'), /<script\b/i);
assert.equal(c130Route.course_id, 'C130');
assert.equal(c130Route.primary_learner_action.kind, 'pages_learner_landing');
assert.equal(c130Route.primary_reader.format, 'linked_pdf');
assert.equal(c130Route.primary_reader.pages, 666);
assert.equal(c130Route.routes.length, 7);
assert.equal(c130Route.adapter.canonical_records, 51704);
assert.equal(c130Route.adapter.units, 1993);
assert.equal(c130Route.adapter.relations, 9545);
assert.equal(c130Route.adapter.rights_assignments, 7634);
assert.equal(c130Route.adapter.identity_crosswalks, 17273);
assert.equal(c130Route.adapter.machine_data_is_primary_learner_destination, false);
assert.equal(c130Validation.state, 'pass');
assert.equal(c130Validation.imported_package.admitted_inputs, 65);
assert.equal(c130Validation.imported_package.archive.members_verified, 65);
assert.equal(c130Validation.semantic_counts.canonical_records, 51704);
assert.equal(c130Validation.learner_routes.count, 7);
assert.equal(c130Validation.learner_routes.pages_landing_is_priority_one, true);
assert.equal(c130Validation.learner_routes.linked_pdf_is_only_primary_reader, true);
assert.equal(c130Validation.claim_boundaries.native_html_claimed, false);
assert.equal(c130Validation.claim_boundaries.pdf_ua_claimed, false);
assert.doesNotMatch(c130HtmlBytes.toString('utf8'), /<script\b/i);
assert.equal(terminologyConcordance.qa_result.result, 'complete_with_manager_correction_queue');
assert.equal(terminologyPolicy.schema_id, 'interlanguage/program-matematika-indonesia-canonical-terminology-register-policy/v1');
assert.equal(terminologyPolicy.decision_procedure.length, 9);
assert.deepEqual(terminologyPolicy.decision_procedure.map(({ sequence }) => sequence), [1, 2, 3, 4, 5, 6, 7, 8, 9]);
assert.equal(terminologyPolicy.termbase_contract.schema_id, 'interlanguage/program-matematika-indonesia-terminology-concept/v1');
assert.equal(terminologyPolicy.probability_family_audit.status, 'evidence_required');
assert.equal(terminologyPolicy.probability_family_audit.automatic_replacement_allowed, false);
assert.equal(terminologyPolicy.probability_family_audit.concepts.length, 9);
assert.equal(terminologyPolicy.probability_family_audit.concepts.every(({ decision_state }) => decision_state === 'evidence_required'), true);
assert.match(terminologyPolicy.scope.methodology_boundary, /program's explicit synthesis/);
const terminologyPolicyChecksums = Object.fromEntries(terminologyPolicyChecksumsAuthorityBytes.toString('utf8').trim().split(/\r?\n/).map((line) => {
  const match = /^([a-f0-9]{64})  (.+)$/.exec(line);
  assert.ok(match, `Baris checksum kebijakan terminologi tidak sah: ${line}`);
  return [match[2], match[1]];
}));
assert.deepEqual(Object.keys(terminologyPolicyChecksums).sort(), ['README.md', 'canonical-register-policy.json']);
assert.equal(terminologyPolicyChecksums['README.md'], sha256(terminologyPolicyReadmeAuthorityBytes));
assert.equal(terminologyPolicyChecksums['canonical-register-policy.json'], sha256(terminologyPolicyAuthorityBytes));
assert.equal(integrationOverrides.native_capabilities.A10.terminology.status, 'in_progress');
assert.equal(integrationOverrides.native_capabilities.D100.terminology.status, 'verified');
const c80Capsule = courseCapsules.find(({ course_id }) => course_id === 'C80');
assert.ok(c80Capsule, 'Kapsul C80 harus tersedia.');
assert.equal(c80Capsule.layers.interoperability.semantic_adapter.status, 'verified');
assert.deepEqual(c80Capsule.layers.learner.tools.map(({ tool_id }) => tool_id), ['c80-openlogic-course-map-v1']);
const c130Capsule = courseCapsules.find(({ course_id }) => course_id === 'C130');
assert.ok(c130Capsule, 'Kapsul C130 harus tersedia.');
assert.equal(c130Capsule.layers.interoperability.semantic_adapter.status, 'verified');
assert.deepEqual(c130Capsule.layers.learner.tools.map(({ tool_id }) => tool_id), ['c130-operations-research-course-map-v1']);
for (const courseId of ['A10']) {
  const capsule = courseCapsules.find(({ course_id }) => course_id === courseId);
  assert.equal(capsule.layers.translation.terminology_status, 'in_progress');
  assert.equal(capsule.layers.translation.corrections_status, 'in_progress');
}
const d100Capsule = courseCapsules.find(({ course_id }) => course_id === 'D100');
assert.equal(d100Capsule.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(d100Capsule.layers.learner.tools.map(({ tool_id }) => tool_id), ['d100.open_learner_hub']);
assert.equal(d100Capsule.layers.translation.terminology_status, 'verified');
assert.equal(d100Capsule.layers.translation.corrections_status, 'verified');
assert.ok(!d100Capsule.evidence.some(({ locator }) => locator.includes('unib-teori-bilangan')));
const d120Capsule = courseCapsules.find(({ course_id }) => course_id === 'D120');
assert.equal(d120Capsule.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(d120Capsule.layers.learner.tools.map(({ tool_id }) => tool_id), ['d120.open_learner_hub']);
assert.equal(d120Capsule.layers.translation.ledger_status, 'not_applicable');
assert.equal(d120Capsule.layers.educator.unit_alignment_status, 'verified');
assert.equal(d120Capsule.layers.learner.capabilities.semantic_html, 'verified');
const c120Capsule = courseCapsules.find(({ course_id }) => course_id === 'C120');
assert.equal(c120Capsule.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(c120Capsule.layers.learner.tools.map(({ tool_id }) => tool_id), ['c120.open_learner_hub']);
assert.equal(c120Capsule.layers.translation.ledger_status, 'verified');
assert.equal(c120Capsule.layers.educator.unit_alignment_status, 'verified');
assert.equal(c120Capsule.layers.learner.capabilities.semantic_html, 'available_unverified');
assert.deepEqual(designPolicyPublicBytes, designPolicyAuthorityBytes, 'Salinan publik kebijakan desain backend harus identik byte demi byte.');
assert.deepEqual(designPolicyPublicSchemaBytes, designPolicySchemaBytes, 'Salinan publik skema kebijakan desain backend harus identik byte demi byte.');
assert.deepEqual(publicBaselinePublicBytes, publicBaselineAuthorityBytes, 'Salinan publik baseline v0.62.12 harus identik byte demi byte.');
assert.deepEqual(publicBaselinePublicSchemaBytes, publicBaselineSchemaBytes, 'Salinan publik skema baseline harus identik byte demi byte.');
assert.equal(designPolicy.$schema, JSON.parse(designPolicySchemaBytes.toString('utf8')).$id);
assert.equal(publicBaseline.$schema, JSON.parse(publicBaselineSchemaBytes.toString('utf8')).$id);
assert.equal(designPolicy.profile, 'thin_format_neutral_zero_copy');
assert.equal(designPolicy.authority.course_native_authoritative, true);
assert.equal(designPolicy.authority.capsule_additive, true);
assert.equal(designPolicy.authority.native_identity_preserved, true);
assert.equal(designPolicy.authority.full_corpus_copied_into_capsule, false);
assert.equal(designPolicy.exchange.generated_json_projection_authoritative, false);
assert.equal(designPolicy.exchange.course_native_formats_constrained, false);
assert.deepEqual(designPolicy.adapters.optional, ['myst', 'quarto', 'xliff']);
assert.equal(designPolicy.adapters.activation_condition, 'concrete_consumer_and_verified_round_trip');
assert.equal(designPolicy.adapters.absence_blocks_release, false);
assert.deepEqual(designPolicy.nonrequirements, {
  universal_normalized_master: false,
  program_wide_source_rewrite: false,
  mandatory_myst_or_quarto: false,
  mandatory_xliff: false,
});
assert.equal(publicBaseline.release.tag, 'v0.62.12');
assert.equal(publicBaseline.repository.public, true);
assert.equal(publicBaseline.release.draft, false);
assert.equal(publicBaseline.release.prerelease, false);
assert.equal(publicBaseline.release.asset_count, 100);
assert.equal(publicBaseline.zenodo.record_id, 22182000);
assert.equal(publicBaseline.zenodo.status, 'published');
assert.equal(publicBaseline.zenodo.access, 'open');
assert.equal(publicBaseline.zenodo.file_count, 100);
assert.deepEqual(publicBaseline.artifacts.map(({ name }) => name), [
  '194_GLOBAL_MODULAR_BACKEND_LEARNER_DELIVERY_INTEGRATION_20260831.json',
  'modular-backend-pattern-index-v1.json',
  'course-capsule-v1.schema.json',
  'course-capsules-v1.jsonl',
  'program-matematika-indonesia-course-capsule-v1.zip',
]);
assert.deepEqual(publicBaseline.successor, {
  version: 'v0.62.13',
  exact_ancestor_required: true,
  nonduplicate_release_required: true,
});
assert.equal(learnerTools.$schema, JSON.parse(learnerToolsSchemaBytes.toString('utf8')).$id);
assert.deepEqual(learnerTools.courses, learnerToolsRows);
assert.deepEqual(Object.keys(learnerToolsByCourseId), ['A00', 'C30', 'C40', 'C80', 'C130']);
assert.equal(learnerTools.courses.length, 5);
const a00LearnerTool = learnerToolsByCourseId.A00?.[0];
assert.ok(a00LearnerTool, 'A00 harus memiliki alat latihan pelajar.');
assert.equal(a00LearnerTool.tool_id, 'a00-assessment-map-v1');
assert.equal(a00LearnerTool.label, 'Latihan & diagnosis');
assert.equal(a00LearnerTool.href, 'id-ID/courses/A00/latihan/index.html');
assert.equal(a00LearnerTool.state, 'verified');
assert.equal(a00LearnerTool.primary, false);
assert.equal(a00LearnerTool.machine_data_is_learner_destination, false);
for (const identity of [a00LearnerTool.page, a00LearnerTool.resource, a00LearnerTool.evidence]) {
  const bytes = await readFile(resolve(root, identity.path));
  assert.equal(bytes.length, identity.bytes, `Identitas learner-tool berubah untuk ${identity.path}.`);
  assert.equal(sha256(bytes), identity.sha256, `SHA-256 learner-tool berubah untuk ${identity.path}.`);
}
for (const [courseId, toolId, href] of [
  ['C30', 'judson-c30-chapter-map-v1', 'backend/judson/C30.html'],
  ['C40', 'judson-c40-chapter-map-v1', 'backend/judson/C40.html'],
  ['C80', 'c80-openlogic-course-map-v1', 'backend/openlogic/C80.html'],
  ['C130', 'c130-operations-research-course-map-v1', 'backend/c130/C130.html'],
]) {
  const tool = learnerToolsByCourseId[courseId]?.[0];
  assert.ok(tool, `${courseId} harus memiliki alat belajar terverifikasi.`);
  assert.equal(tool.tool_id, toolId);
  assert.equal(tool.href, href);
  assert.equal(tool.state, 'verified');
  assert.equal(tool.machine_data_is_learner_destination, false);
  for (const identity of [tool.page, tool.resource, tool.evidence]) {
    const bytes = await readFile(resolve(root, identity.path));
    assert.equal(bytes.length, identity.bytes, `Identitas learner-tool berubah untuk ${identity.path}.`);
    assert.equal(sha256(bytes), identity.sha256, `SHA-256 learner-tool berubah untuk ${identity.path}.`);
  }
}
assert.equal(a00AssessmentMap.$schema, JSON.parse(a00AssessmentSchemaBytes.toString('utf8')).$id);
assert.equal(a00AssessmentMap.course_id, 'A00');
assert.equal(a00AssessmentMap.locale, 'id-ID');
assert.deepEqual(a00AssessmentMap.counts, {
  modules: 75,
  modules_with_assessments: 60,
  assessments: 8105,
  components: 13345,
  explicit_solutions: 5240,
  without_explicit_solution: 2865,
});
assert.equal(a00AssessmentMap.modules.length, 75);
assert.equal(a00AssessmentMap.modules.flatMap(({ assessments }) => assessments).length, 8105);
assert.equal(a00AnchorAudit.status, 'PASS');
assert.deepEqual(a00AnchorAudit.counts, {
  modules: 75,
  assessment_anchors: 8105,
  component_anchors: 13345,
  expected_anchors: 21450,
  matched_exactly_once: 21450,
  missing: 0,
  duplicate: 0,
});
const a00AssessmentHtml = a00AssessmentHtmlBytes.toString('utf8');
const a00AssessmentStyle = a00AssessmentStyleBytes.toString('utf8');
const a00AssessmentScript = a00AssessmentScriptBytes.toString('utf8');
assert.match(a00AssessmentHtml, /<h1>Latihan &amp; diagnosis<\/h1>/);
assert.match(a00AssessmentHtml, /8\.105/);
assert.match(a00AssessmentHtml, /tanpa solusi eksplisit dalam sumber/i);
assert.doesNotMatch(a00AssessmentHtml, /href="[^"]*\.(?:json|jsonl|csv)(?:[?#"])/i);
assert.match(a00AssessmentStyle, /:focus-visible\s*\{[^}]*outline:\s*3px solid #82ad5b/s);
assert.match(a00AssessmentScript, /assessment-map-v1\.json/);
assert.deepEqual(modularBackendPatternPublicBytes, modularBackendPatternAuthorityBytes, 'Salinan publik indeks pola backend harus identik byte demi byte.');
assert.equal(modularBackendPatternIndex.methodology.denominator.native_implementation_families, 33);
assert.equal(modularBackendPatternIndex.methodology.denominator.program_roles, 40);
assert.equal(modularBackendPatternIndex.post_audit_updates.d20_adapter.canonical_records, 138894);
assert.deepEqual(v23AdapterIndexPublicBytes, v23AdapterIndexAuthorityBytes, 'Salinan publik indeks adapter v2.3 harus identik byte demi byte.');
assert.deepEqual(v23AdapterIndexPublicSchemaBytes, v23AdapterIndexSchemaBytes, 'Salinan publik skema indeks adapter v2.3 harus identik byte demi byte.');
assert.equal(v23AdapterIndex.$schema, JSON.parse(v23AdapterIndexSchemaBytes.toString('utf8')).$id);
assert.deepEqual(v23AdapterIndex.summary, {
  curriculum_roles: 40,
  proof_roles: 5,
  legacy_proofs: 0,
  contract_2_3_1_adapters: 5,
  unbound_roles: 35,
});
assert.deepEqual(v23AdapterIndex.adapters.map(({ role_id }) => role_id), ['A00', 'B10', 'D20', 'D60', 'D110']);
assert.equal(new Set(v23AdapterIndex.adapters.map(({ archive }) => `${archive.bytes}:${archive.sha256}`)).size, 5);
assert.equal(v23AdapterIndex.adapters.find(({ role_id }) => role_id === 'A00').learner_runtime_relationship, 'directly_consumes_adapter_outputs');
for (const adapter of v23AdapterIndex.adapters) {
  assert.ok(adapter.adopted_capabilities.length > 0, `${adapter.role_id}: capability adoption must be explicit.`);
  assert.ok(adapter.known_limitations.length > 0, `${adapter.role_id}: limitations must remain explicit.`);
  assert.equal(basename(new URL(adapter.public_asset_url).pathname), basename(adapter.archive.path), `${adapter.role_id}: public asset URL filename drift.`);
  if (adapter.admission_state === 'published') {
    assert.equal(adapter.public_replay_status, 'published_public_asset_readback_verified', `${adapter.role_id}: published adapter lacks public replay status.`);
  }
  if (adapter.learner_runtime_relationship === 'course_link_only_no_adapter_consumption_claim') {
    assert.notEqual(adapter.role_id, 'A00');
  }
}
let locallyVerifiedAdapterFiles = 0;
let releasedArchiveReferences = 0;
for (const adapter of v23AdapterIndex.adapters) {
  for (const identity of [adapter.archive, adapter.manifest].filter(Boolean)) {
    try {
      const bytes = await readFile(resolve(root, identity.path));
      assert.equal(bytes.length, identity.bytes, `${adapter.role_id}: byte count indeks adapter berubah untuk ${identity.path}.`);
      assert.equal(sha256(bytes), identity.sha256, `${adapter.role_id}: SHA-256 indeks adapter berubah untuk ${identity.path}.`);
      locallyVerifiedAdapterFiles += 1;
    } catch (error) {
      if (error?.code !== 'ENOENT' || identity !== adapter.archive) throw error;
      assert.equal(adapter.admission_state, 'published', `${adapter.role_id}: arsip yang tidak ada di pohon sumber harus sudah diterbitkan.`);
      const released = publicationReceipts
        .flatMap(({ payload_inventory = [] }) => payload_inventory)
        .find((item) => item.name === basename(identity.path)
          && item.bytes === identity.bytes
          && item.sha256 === identity.sha256
          && item.anonymous_byte_identity === true);
      assert.ok(released, `${adapter.role_id}: arsip tanpa byte lokal tidak terikat oleh tanda terima publik pendahulu.`);
      assert.equal(released.anonymous_byte_identity, true, `${adapter.role_id}: readback anonim arsip tidak PASS.`);
      assert.equal(released.bytes, identity.bytes, `${adapter.role_id}: byte arsip publik berbeda dari indeks.`);
      assert.equal(released.sha256, identity.sha256, `${adapter.role_id}: SHA-256 arsip publik berbeda dari indeks.`);
      assert.match(released.anonymous_url, /^https:\/\/zenodo\.org\/api\/records\/\d+\/files\//);
      releasedArchiveReferences += 1;
    }
  }
}
assert.equal(learnerDelivery.$schema, JSON.parse(learnerDeliverySchemaBytes.toString('utf8')).$id);
assert.equal(learnerDelivery.courses.length, 40);
assert.equal(new Set(learnerDelivery.courses.map(({ course_id }) => course_id)).size, 40);
assert.deepEqual(learnerDelivery.courses.map(({ course_id }) => course_id), courses.map(({ id }) => id));
const expectedLearnerDeliveryRows = learnerDelivery.courses.map((row) => ({
  course_id: row.course_id,
  online_html: { status: row.online_html.status },
  epub: row.epub,
  portable_html: row.portable_html,
  capabilities: { mathml: { status: row.capabilities.mathml.status } },
}));
assert.deepEqual(learnerDeliveryRows, expectedLearnerDeliveryRows, 'Proyeksi runtime learner-delivery berbeda dari otoritas.');
assert.deepEqual(Object.keys(learnerDeliveryByCourseId), courses.map(({ id }) => id));

const ids = courses.map(({ id }) => id);
const idSet = new Set(ids);
assert.equal(ids.length, idSet.size, 'Kode mata kuliah harus unik.');
assert.equal(catalog.counts.courseRoles, courses.length, 'Jumlah peran katalog tidak cocok.');
assert.equal(program.totalCourseRoles, courses.length, 'Jumlah peran program tidak cocok.');
const selectedIds = courses.filter(({ state }) => state !== 'unresolved').map(({ id }) => id);
const unresolvedIds = courses.filter(({ state }) => state === 'unresolved').map(({ id }) => id);
const publishedIds = courses.filter(({ state }) => state === 'published').map(({ id }) => id);
if (program.version === '0.62.0') {
  assert.equal(publishedIds.length, 21, 'v0.62 must expose exactly 21 completed roles.');
  assert.equal(program.completedPublicRecordDois.length, 20, 'v0.62 must expose exactly 20 distinct completed records.');
  assert.ok(publishedIds.includes('B20') && publishedIds.includes('D90'));
  assert.match(courses.find(({ id }) => id === 'A10').zenodo, /22143518$/);
  assert.equal(courses.find(({ id }) => id === 'A30').repository, 'https://github.com/KokunoYumeto/openstax-precalculus-2e-id');
  assert.equal(courses.find(({ id }) => id === 'B20').supplements.length, 1);
  assert.equal(courses.find(({ id }) => id === 'B40').supplements.length, 2);
  assert.match(courses.find(({ id }) => id === 'D90').zenodo, /22142120$/);
  assert.equal(program.backend.learnerStateV1.storage, 'browser-local');
  assert.equal(program.backend.learnerStateV1.derivedEligibilityPersisted, false);
}
const publishedHtmlReaderIds = courses.filter(({ reader }) => reader).map(({ id }) => id);
assert.equal(catalog.counts.selectedCorpusRoles, selectedIds.length);
assert.equal(catalog.counts.unresolvedRoles, unresolvedIds.length);
assert.equal(catalog.counts.completedPublicCourseRoles, publishedIds.length);
assert.equal(catalog.counts.completedPublicRecords, program.completedPublicRecordDois.length);
assert.deepEqual(program.unresolvedRoleIds, unresolvedIds);
assert.deepEqual(program.completedPublicCourseRoleIds, publishedIds);
assert.equal(new Set(program.completedPublicRecordDois).size, program.completedPublicRecordDois.length);
assert.equal(program.website, 'https://kokunoyumeto.github.io/program-matematika-indonesia/');
assert.match(program.zenodo, /^https:\/\/doi\.org\/10\.5281\/zenodo\.\d+$/);
assert.match(program.zenodoConcept, /^https:\/\/doi\.org\/10\.5281\/zenodo\.\d+$/);
const centralRecordId = program.zenodo.match(/zenodo\.(\d+)$/)[1];
assert.equal(program.provenance.model, 'OpenAI Codex gpt-5.6-sol, Ultra');
assert.equal(program.backend.status, 'validated');
assert.equal(program.repositories.github.status, 'available');
assert.equal(catalogSchema.$id, catalog.$schema, 'Identitas schema katalog berbeda dari rujukan katalog.');

const allowedStates = new Set(['published', 'near', 'production', 'unresolved']);
for (const course of courses) {
  assert.ok(allowedStates.has(course.state), `${course.id}: status tidak dikenal.`);
  assert.ok(topics.includes(course.topic), `${course.id}: bidang tidak tercantum.`);
  assert.equal(course.level, course.id[0], `${course.id}: tingkat tidak cocok dengan kode.`);
  assert.ok(typeof course.ownerLane === 'string' && course.ownerLane.trim(), `${course.id}: pemilik kosong.`);
  for (const prerequisite of course.prerequisites) {
    assert.ok(idSet.has(prerequisite), `${course.id}: prasyarat ${prerequisite} tidak ditemukan.`);
    assert.notEqual(prerequisite, course.id, `${course.id}: prasyarat tidak boleh menunjuk dirinya sendiri.`);
  }
  for (const field of ['title', 'purpose', 'outcome', 'corpus', 'note']) {
    assert.ok(typeof course[field] === 'string' && course[field].trim(), `${course.id}: ${field} kosong.`);
  }
  for (const field of ['reader', 'edition', 'repository', 'zenodo']) {
    if (course[field]) assert.match(course[field], /^https:\/\//, `${course.id}: ${field} harus memakai HTTPS.`);
  }
  if (course.state === 'published') {
    assert.ok(course.edition, `${course.id}: edisi selesai tidak memiliki rute baca/unduh.`);
  }
}

const liveOverlayRequiredRoleIds = ['A10', 'A20', 'A30', 'B20', 'B30', 'B50', 'B70', 'B95', 'C10', 'C20', 'C50', 'C90', 'C100', 'C140', 'D10', 'D20', 'D30', 'D40', 'D50', 'D60', 'D70', 'D100', 'D120'];
for (const id of liveOverlayRequiredRoleIds) {
  assert.ok(liveCoursePublications[id], `${id}: baris lama belum memiliki overlay publikasi langsung.`);
}
assert.deepEqual(effectiveCourses.map(({ id }) => id), courses.map(({ id }) => id), 'Overlay mengubah urutan atau identitas mata kuliah.');
assert.equal(effectiveCourses.length, courses.length, 'Overlay mengubah jumlah mata kuliah.');
assert.equal(effectivePublishedCourses.length, 37, 'Overlay harus menampilkan tepat 37 peran dengan edisi selesai.');
assert.equal(effectivePublishedRecordDois.size, 33, 'Tiga puluh tujuh peran selesai harus memakai tepat 33 rekaman DOI edisi berbeda.');
assert.equal(
  effectiveCourses.filter(({ state }) => state === 'production').length,
  3,
  'Overlay harus menampilkan tepat 3 peran yang masih diproduksi.',
);
assert.deepEqual(
  effectiveCourses.filter(({ state }) => state === 'production').map(({ id }) => id),
  ['A30', 'B95', 'C140'],
  'Daftar tiga peran produksi berubah.',
);
const progressStageKeys = ['translationBearingUnits', 'integrationReadyUnits', 'canonicalUnits', 'publicUnits'];
for (const course of effectiveCourses) {
  assert.ok(allowedStates.has(course.state), `${course.id}: status efektif tidak dikenal.`);
  for (const prerequisite of course.prerequisites) {
    assert.ok(idSet.has(prerequisite), `${course.id}: prasyarat efektif ${prerequisite} tidak ditemukan.`);
  }
  for (const field of ['learner', 'reader', 'edition', 'repository', 'zenodo', 'release']) {
    if (course[field] !== undefined && course[field] !== null) {
      assert.match(course[field], /^https:\/\//, `${course.id}: ${field} efektif harus memakai HTTPS atau null.`);
    }
  }
  assert.ok(!Object.hasOwn(course, 'additionalSupplements'), `${course.id}: additionalSupplements bocor ke baris efektif.`);
  for (const supplement of course.supplements ?? []) {
    assert.ok(typeof supplement.title === 'string' && supplement.title.trim(), `${course.id}: judul suplemen kosong.`);
    assert.match(supplement.url, /^https:\/\//, `${course.id}: URL suplemen harus memakai HTTPS.`);
  }
  if (!course.progress) continue;
  const progress = course.progress;
  assert.ok(typeof progress.unitLabel === 'string' && progress.unitLabel.trim(), `${course.id}: unitLabel progres kosong.`);
  assert.ok(!Number.isNaN(Date.parse(progress.updatedAt)), `${course.id}: updatedAt progres tidak valid.`);
  for (const key of [...progressStageKeys, 'totalUnits', 'totalPages', 'publicPages']) {
    if (progress[key] === undefined) continue;
    assert.ok(Number.isInteger(progress[key]) && progress[key] >= 0, `${course.id}: ${key} harus bilangan bulat nonnegatif.`);
    if (key.endsWith('Units') && key !== 'totalUnits' && progress.totalUnits !== undefined) {
      assert.ok(progress[key] <= progress.totalUnits, `${course.id}: ${key} melebihi totalUnits.`);
    }
  }
  const stages = progressStageKeys.map((key) => progress[key]).filter(Number.isInteger);
  for (let index = 1; index < stages.length; index += 1) {
    assert.ok(stages[index - 1] >= stages[index], `${course.id}: urutan tahap progres tidak monoton.`);
  }
}
assert.deepEqual(
  effectiveNextCourseIdsById,
  Object.fromEntries(effectiveCourses.map(({ id }) => [id, effectiveCourses.filter(({ prerequisites }) => prerequisites.includes(id)).map(({ id: nextId }) => nextId)])),
  'Peta lanjut efektif bukan pembalikan prasyarat efektif.',
);

const syntheticAuthority = [
  { id: 'A00', state: 'production', prerequisites: [], supplements: [{ title: 'lama', url: 'https://example.org/old' }] },
  { id: 'A10', state: 'production', prerequisites: ['A00'] },
];
const syntheticBefore = JSON.stringify(syntheticAuthority);
const syntheticEffective = materializeLiveCourses(syntheticAuthority, {
  A00: { state: 'published', edition: null, supplements: [] },
  A10: { prerequisites: [], additionalSupplements: [{ title: 'baru', url: 'https://example.org/new' }] },
});
assert.equal(syntheticEffective[0].state, 'published');
assert.equal(syntheticEffective[0].edition, null, 'Null eksplisit harus membersihkan URL lama.');
assert.deepEqual(syntheticEffective[0].supplements, [], 'Daftar suplemen eksplisit harus menggantikan daftar lama.');
assert.deepEqual(syntheticEffective[1].supplements.map(({ title }) => title), ['baru'], 'Suplemen tambahan tidak digabungkan.');
assert.deepEqual(deriveNextCourseIdsById(syntheticEffective), { A00: [], A10: [] }, 'Prasyarat efektif tidak mengubah peta lanjut.');
assert.equal(JSON.stringify(syntheticAuthority), syntheticBefore, 'Materialisasi memutasi otoritas masukan.');

assert.equal(effectiveCoursesById.get('A10').progress.translationBearingUnits, 82);
assert.equal(effectiveCoursesById.get('A10').progress.canonicalUnits, 82);
assert.equal(effectiveCoursesById.get('A10').progress.publicUnits, 82);
assert.equal(effectiveCoursesById.get('A10').progress.publicPages, 1627);
assert.equal(effectiveCoursesById.get('A10').state, 'published');
assert.match(effectiveCoursesById.get('A10').zenodo, /22236314$/);
assert.equal(effectiveCoursesById.get('A20').progress.translationBearingUnits, 83);
assert.equal(effectiveCoursesById.get('A10').supplements.length, 2);
assert.equal(effectiveCoursesById.get('A20').progress.integrationReadyUnits, 83);
assert.equal(effectiveCoursesById.get('A20').progress.canonicalUnits, 83);
assert.equal(effectiveCoursesById.get('A20').progress.publicUnits, 83);
assert.equal(effectiveCoursesById.get('A20').progress.publicPages, 3438);
assert.equal(effectiveCoursesById.get('A20').state, 'published');
assert.equal(effectiveCoursesById.get('A20').version, '1.0.0');
assert.match(effectiveCoursesById.get('A20').zenodo, /22229860$/);
assert.equal(effectiveCoursesById.get('A30').progress.translationBearingUnits, 87);
assert.ok(!Object.hasOwn(effectiveCoursesById.get('A30').progress, 'integrationReadyUnits'));
assert.equal(effectiveCoursesById.get('A30').progress.canonicalUnits, 67);
assert.equal(effectiveCoursesById.get('A30').progress.publicUnits, 67);
assert.equal(effectiveCoursesById.get('A30').progress.publicPages, 2031);
assert.equal(effectiveCoursesById.get('A30').state, 'production');
assert.match(effectiveCoursesById.get('A30').zenodo, /22184511$/);
assert.equal(effectiveCoursesById.get('B20').progress.publicUnits, 5178);
assert.equal(effectiveCoursesById.get('B20').supplements.length, 2);
assert.match(effectiveCoursesById.get('B20').zenodo, /(?:22164136|22183943)$/);
assert.equal(effectiveCoursesById.get('B30').state, 'published');
assert.equal(effectiveCoursesById.get('B30').version, '2026.08.31');
assert.equal(effectiveCoursesById.get('B30').progress.publicPages, 1243);
assert.match(effectiveCoursesById.get('B30').zenodo, /22182941$/);
assert.match(effectiveCoursesById.get('B30').edition, /CLP-2_Kalkulus_Integral_Bahasa_Indonesia_edisi_lengkap_2026-08-30\.pdf\?download=1$/);
assert.equal(effectiveCoursesById.get('B50').progress.publicUnits, 138);
assert.equal(effectiveCoursesById.get('B50').supplements.length, 2);
assert.match(effectiveCoursesById.get('B50').zenodo, /(?:22163372|22184443)$/);
assert.match(effectiveCoursesById.get('B95').zenodo, /22192066$/);
assert.equal(effectiveCoursesById.get('B95').version, '2026.08.31.1-R011-B030');
assert.equal(effectiveCoursesById.get('B95').state, 'production');
assert.match(effectiveCoursesById.get('B95').release, /r011-b030-2026\.08\.31\.1$/);
assert.equal(effectiveCoursesById.get('B95').progress.publicPages, 322);
assert.equal(effectiveCoursesById.get('B95').progress.publicBoundary, 'B030 — Bab 7, Bagian 7.5');
assert.match(effectiveCoursesById.get('B95').edition, /00_STATISTIKA_BERBASIS_DATA_ID_R011-B030_WORKING_READER\.pdf\?download=1$/);
assert.deepEqual(effectiveCoursesById.get('B95').verification, {
  readerBytes: 13576715,
  readerSha256: '28881f11d05dca933d16960f22be9a73ef2069c96d3e00d4e612afaf3dbecfcb',
  backendRecords: 11810,
  publicAssets: 9,
});
assert.equal(effectiveCoursesById.get('C90').state, 'published');
assert.equal(effectiveCoursesById.get('C90').progress.publicUnits, 20);
assert.equal(effectiveCoursesById.get('C90').progress.publicPages, 645);
assert.match(effectiveCoursesById.get('C90').zenodo, /22164668$/);
const leblPublicationExpectations = {
  B70: { pages: 502, bytes: 5135134, sha256: '1c18dfc1572d22ef7fc5d8ad25be18f3b91f1bffea5b9f9d521ff4e56ca969d4', file: 'Catatan_tentang_Diffy_Qs_Bahasa_Indonesia_v6.11.pdf' },
  C10: { pages: 334, bytes: 2870909, sha256: '38743ea0e7ce52bdadf5233fc9d6e79e00717f9ba55a393f2bf46ea21c65ef56', file: 'Analisis_Dasar_I_Bahasa_Indonesia_v6.3.pdf' },
  C20: { pages: 241, bytes: 2427379, sha256: 'e70c74bb7edc466a7cb6ff0eff0de33dfcc7b3bc63010d018aff758a14d2dea3', file: 'Analisis_Dasar_II_Bahasa_Indonesia_v6.3.pdf' },
  C50: { pages: 338, bytes: 2822132, sha256: '87e4810abdedbdd8121995a8e53936891135037f03054dce76a06beebc3cfaae', file: 'Panduan_Mengolah_Analisis_Kompleks_Bahasa_Indonesia_v1.9.pdf' },
};
for (const [id, expected] of Object.entries(leblPublicationExpectations)) {
  const course = effectiveCoursesById.get(id);
  assert.equal(course.state, 'published');
  assert.equal(course.version, 'lebl-family-id-complete.2026.08.30');
  assert.equal(course.progress.publicPages, expected.pages);
  assert.equal(course.zenodo, 'https://doi.org/10.5281/zenodo.22182427');
  assert.match(course.edition, new RegExp(`22182427/files/${expected.file.replaceAll('.', '\\.')}\\?download=1$`));
  assert.match(course.release, /lebl-family-id\.2026\.08\.30\.complete$/);
  assert.deepEqual(course.verification, {
    readerBytes: expected.bytes,
    readerSha256: expected.sha256,
    publicReadback: 'pass',
  });
}
assert.equal(effectiveCoursesById.get('B50').progress.publicPages, 410);
assert.equal(effectiveCoursesById.get('B50').state, 'published');
assert.equal(effectiveCoursesById.get('C100').supplements.length, 1);
assert.equal(effectiveCoursesById.get('C100').supplements[0].id, 'clemens-snapp-workbook-u022');
assert.match(effectiveCoursesById.get('C140').zenodo, /22164344$/);
assert.equal(effectiveCoursesById.get('C140').supplements[0].id, 'c140-companion-reader');
assert.equal(effectiveCoursesById.get('D10').progress.translationBearingUnits, 672);
assert.equal(effectiveCoursesById.get('D10').progress.integrationReadyUnits, 672);
assert.equal(effectiveCoursesById.get('D10').progress.canonicalUnits, 672);
assert.equal(effectiveCoursesById.get('D10').progress.publicUnits, 672);
assert.equal(effectiveCoursesById.get('D10').progress.publicPages, 715);
assert.match(effectiveCoursesById.get('D10').zenodo, /22181780$/);
assert.equal(effectiveCoursesById.get('D20').state, 'published');
assert.equal(effectiveCoursesById.get('D20').progress.publicUnits, 17);
assert.match(effectiveCoursesById.get('D20').zenodo, /22088947$/);
assert.equal(effectiveCoursesById.get('D30').state, 'published');
assert.equal(effectiveCoursesById.get('D30').progress.publicPages, 447);
assert.match(effectiveCoursesById.get('D30').zenodo, /22182655$/);
assert.equal(effectiveCoursesById.get('D30').version, '2026.08.30-checkpoint.38');
assert.match(effectiveCoursesById.get('D30').edition, /READER_CHECKPOINT_38\.pdf\?download=1$/);
assert.equal(effectiveCoursesById.get('D40').state, 'published');
assert.equal(effectiveCoursesById.get('D40').progress.totalUnits, 18);
assert.equal(effectiveCoursesById.get('D40').progress.translationBearingUnits, 18);
assert.equal(effectiveCoursesById.get('D40').progress.integrationReadyUnits, 18);
assert.equal(effectiveCoursesById.get('D40').progress.canonicalUnits, 18);
assert.equal(effectiveCoursesById.get('D40').progress.publicUnits, 18);
assert.equal(effectiveCoursesById.get('D40').progress.publicPages, 679);
assert.match(effectiveCoursesById.get('D40').reader, /readers\/d40\/unit14\/$/);
assert.match(effectiveCoursesById.get('D40').edition, /PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_LENGKAP\.pdf\?download=1$/);
assert.match(effectiveCoursesById.get('D40').zenodo, /22184259$/);
assert.equal(effectiveCoursesById.get('D40').repository, undefined, 'D40 belum memiliki repositori GitHub edisi Indonesia.');
assert.equal(effectiveCoursesById.get('D40').supplements.length, 2);
assert.equal(effectiveCoursesById.get('D40').supplements[0].id, 'd40-complete-package');
assert.equal(effectiveCoursesById.get('D40').supplements[0].bytes, 9436983);
assert.equal(effectiveCoursesById.get('D40').supplements[0].sha256, 'a370bba5ddb54081387a484a304b24af92691c3bc167db964c486625a79add59');
assert.equal(effectiveCoursesById.get('D40').supplements[1].id, 'dionne-unit14-source');
assert.equal(effectiveCoursesById.get('D40').supplements[1].bytes, 12141309);
assert.equal(effectiveCoursesById.get('D40').supplements[1].sha256, '248b65a225e96f0a342ab2f6288aa303d28bfd2a8e108db14f7e125ef5401f0e');
assert.equal(sha256(d40ReaderIndexBytes), 'c6785811f86cb96cc3d9a2ce81e094c511937f6d304ba78bab0973928ebcbbcf');
assert.match(d40Landing, /edisi lengkap publik/);
assert.match(d40Landing, /679 halaman/);
assert.match(d40Landing, /22184259/);
assert.match(d40Landing, /D40_COMPLETE_ID_20260831\.zip/);
assert.match(d40Landing, /repositori GitHub khusus edisi D40 belum diproduksi/i);
assert.doesNotMatch(d40Landing, /kursus tetap diproduksi|bukan klaim bahwa seluruh kursus selesai/i);
assert.equal(effectiveCoursesById.get('D50').state, 'published');
assert.match(effectiveCoursesById.get('D50').zenodo, /22161090$/);
assert.equal(effectiveCoursesById.get('D60').state, 'published');
assert.equal(effectiveCoursesById.get('D60').progress.publicUnits, 4);
assert.equal(effectiveCoursesById.get('D60').progress.publicPages, 564);
assert.match(effectiveCoursesById.get('D60').reader, /lab01-lab02-lab03-lab04-capstone\/$/);
assert.match(effectiveCoursesById.get('D60').edition, /22168033\/files\/00_TOPOLOGI_ALJABAR_ID_.*_CAPSTONE_READER\.pdf\?download=1$/);
assert.match(effectiveCoursesById.get('D60').zenodo, /22168033$/);
assert.equal(effectiveCoursesById.get('D60').version, '0.31.7');
assert.match(effectiveCoursesById.get('D60').note, /108\/108 butir penguasaan bersolusi/);
assert.match(effectiveCoursesById.get('D60').note, /empat graf perbaikan bukti/);
assert.match(effectiveCoursesById.get('D60').note, /capstone D60/);
assert.match(effectiveCoursesById.get('D60').note, /sembilan berkas Zenodo/);
assert.match(effectiveCoursesById.get('D60').note, /27\.642 rekaman kanonik/);
assert.match(effectiveCoursesById.get('D60').note, /2\.204 unit/);
assert.match(effectiveCoursesById.get('D60').note, /6\.279 pemetaan reversibel/);
assert.match(effectiveCoursesById.get('D60').note, /19 tabel JSONL\/CSV/);
assert.match(effectiveCoursesById.get('D60').note, /8\.338 rekaman native/);
assert.equal(effectiveCoursesById.get('D60').supplements.length, 1);
assert.equal(effectiveCoursesById.get('D60').supplements[0].id, 'd60-editable-source-backend-complete');
assert.equal(effectiveCoursesById.get('D60').supplements[0].resourceType, 'reference');
assert.match(effectiveCoursesById.get('D60').supplements[0].scope, /bukan pembaca utama/i);
assert.equal(effectiveCoursesById.get('D60').supplements[0].bytes, 8406450);
assert.equal(effectiveCoursesById.get('D60').supplements[0].sha256, 'f7670f6e6ad9a95ff808a1ddf4c2fdd8b41c6bce1916d33ac6fe5063be184b1b');
assert.match(effectiveCoursesById.get('D60').supplements[0].url, /22168033\/files\/TOPOLOGI_ALJABAR_ID_.*_CAPSTONE_EDITABLE_SOURCE_BACKEND\.zip\?download=1$/);
assert.doesNotMatch(effectiveCoursesById.get('D60').reader, /\.(?:json|jsonl|csv|zip)(?:[?#]|$)/i, 'Rute utama D60 harus tetap pembaca HTML.');
assert.equal(effectiveCoursesById.get('D70').state, 'published');
assert.equal(effectiveCoursesById.get('D70').progress.publicUnits, 4);
assert.equal(effectiveCoursesById.get('D70').progress.publicPages, 716);
assert.match(effectiveCoursesById.get('D70').zenodo, /22160944$/);
assert.equal(effectiveCoursesById.get('D80').state, 'published');
assert.equal(effectiveCoursesById.get('D80').progress.totalUnits, 146);
assert.equal(effectiveCoursesById.get('D80').progress.translationBearingUnits, 146);
assert.equal(effectiveCoursesById.get('D80').progress.integrationReadyUnits, 146);
assert.equal(effectiveCoursesById.get('D80').progress.canonicalUnits, 146);
assert.equal(effectiveCoursesById.get('D80').progress.publicUnits, 146);
assert.equal(effectiveCoursesById.get('D80').progress.publicPages, 864);
assert.equal(effectiveCoursesById.get('D80').reader, 'https://kokunoyumeto.github.io/metode-aljabar-jilid-2-id/');
assert.match(effectiveCoursesById.get('D80').edition, /22167691\/files\/00_metode-dalam-aljabar-jilid-2-edisi-bahasa-indonesia\.pdf\?download=1$/);
assert.match(effectiveCoursesById.get('D80').zenodo, /22167691$/);
assert.equal(effectiveCoursesById.get('D80').version, 'complete-edition-html-reader-correction-2026-08-30');
assert.equal(effectiveCoursesById.get('D80').supplements.length, 2);
assert.equal(effectiveCoursesById.get('D80').supplements[0].id, 'metode-aljabar-jilid-2-backend');
assert.match(effectiveCoursesById.get('D80').supplements[0].url, /22167691\/files\/02_backend-semantik\.zip\?download=1$/);
assert.equal(effectiveCoursesById.get('D80').supplements[1].id, 'metode-aljabar-jilid-2-html-offline-corrected');
assert.equal(effectiveCoursesById.get('D80').supplements[1].bytes, 1373063);
assert.equal(effectiveCoursesById.get('D80').supplements[1].sha256, '064dc97e9ae58217622a768f1a989eb316892a607d219211f4be17e6cf44d03c');
assert.match(effectiveCoursesById.get('D80').supplements[1].url, /22167691\/files\/03_pembaca-html-offline\.zip\?download=1$/);
assert.match(effectiveCoursesById.get('D80').note, /27\.308 formula/);
assert.match(effectiveCoursesById.get('D80').note, /nol kesalahan MathJax/);
assert.match(effectiveCoursesById.get('D80').note, /Paket HTML luring terkoreksi telah diterbitkan/);
assert.equal(effectiveCoursesById.get('D100').progress.totalUnits, 60);
assert.equal(effectiveCoursesById.get('D100').state, 'published');
assert.equal(effectiveCoursesById.get('D100').version, 'ak-unit-30-corr1+bgk-unit-30-corr1+bridge-corr1');
assert.equal(effectiveCoursesById.get('D100').progress.translationBearingUnits, 60);
assert.equal(effectiveCoursesById.get('D100').progress.integrationReadyUnits, 60);
assert.equal(effectiveCoursesById.get('D100').progress.canonicalUnits, 60);
assert.equal(effectiveCoursesById.get('D100').progress.publicUnits, 60);
assert.equal(effectiveCoursesById.get('D100').progress.publicPages, 975);
assert.match(effectiveCoursesById.get('D100').zenodo, /22237442$/);
assert.equal(effectiveCoursesById.get('D100').supplements.length, 2);
assert.equal(effectiveCoursesById.get('D100').supplements[0].id, 'bgk-units-01-30-corr1');
assert.equal(effectiveCoursesById.get('D100').supplements[1].id, 'original-bridge-corr1');
assert.equal(effectiveCoursesById.get('D100').supplements[0].pages, 380);
assert.equal(effectiveCoursesById.get('D100').supplements[0].sha256, '34fb81e572f60e20e4dadff9f5040da7abf9882bbf5cf64a425a03297428a436');
assert.equal(effectiveCoursesById.get('D100').supplements[1].pages, 90);
assert.equal(effectiveCoursesById.get('D100').supplements[1].sha256, 'ed54f440409b2aa7beb5a1ff24be0e54de7845576f3f4d06e88fd58c9feb2131');

const expectedNextCourseIdsById = Object.fromEntries(
  courses.map(({ id }) => [
    id,
    courses.filter(({ prerequisites }) => prerequisites.includes(id)).map(({ id: nextId }) => nextId),
  ]),
);
assert.deepEqual(nextCourseIdsById, expectedNextCourseIdsById, 'Peta “Lanjut ke” bukan pembalikan deterministik prasyarat.');
assert.deepEqual(learnerReadModel.nextCourseIdsById, expectedNextCourseIdsById);
const prerequisiteEdgeCount = Object.values(expectedNextCourseIdsById).flat().length;
if (program.version === '0.62.0') {
  assert.equal(prerequisiteEdgeCount, 83);
  assert.deepEqual([...courses.find(({ id }) => id === 'D80').prerequisites].sort(), ['C30', 'C80', 'D70']);
}
assert.equal(learnerReadModel.summary.course_count, courses.length);
assert.equal(learnerReadModel.summary.published_course_count, publishedIds.length);
assert.equal(learnerReadModel.summary.readback_overlay_count, authority.public_readback_overlays.length);
assert.equal(program.backend.learnerReadModelV1.courseCount, courses.length);
assert.equal(program.backend.learnerReadModelV1.prerequisiteEdgeCount, prerequisiteEdgeCount);

const visiting = new Set();
const visited = new Set();
function visitCourse(id) {
  assert.ok(!visiting.has(id), `Siklus prasyarat terdeteksi pada ${id}.`);
  if (visited.has(id)) return;
  visiting.add(id);
  for (const nextId of nextCourseIdsById[id]) visitCourse(nextId);
  visiting.delete(id);
  visited.add(id);
}
for (const id of ids) visitCourse(id);

const federationManifest = await readJson(`${authority.federation.package_path}/manifest.json`);
const v2 = program.backend.federationV2;
assert.equal(v2.status, 'validated');
assert.equal(v2.recordCount, federationManifest.record_count);
assert.equal(v2.datasetCount, federationManifest.record_counts.datasets);
assert.equal(v2.courseCount, federationManifest.record_counts.courses);
assert.equal(v2.learnerSurfaceCount, federationManifest.record_counts.reader_surfaces);
assert.equal(v2.webRouteCount, federationManifest.record_counts.web_routes);
assert.equal(v2.identityCrosswalkCount, federationManifest.record_counts.identity_crosswalks);
assert.equal(v2.publicationEventCount, federationManifest.record_counts.publication_events);
assert.equal(v2.qaEventCount, federationManifest.record_counts.qa_events);
assert.equal(federationManifest.record_count, Object.values(federationManifest.record_counts).reduce((sum, value) => sum + value, 0));
for (const field of ['package', 'packageSchema', 'recordSchema', 'validationReceipt']) {
  assert.match(v2[field], /\/records\/\d+\/files\//, `federationV2.${field} tidak terikat ke arsip.`);
}
if (program.backend.federationV22) {
  assert.match(String(program.backend.federationV22.status), /validated/);
  for (const field of ['package', 'validationReceipt', 'archiveReceipt']) {
    if (program.backend.federationV22[field]) {
      assert.match(
        program.backend.federationV22[field],
        new RegExp(`^https://zenodo\\.org/records/${centralRecordId}/files/`),
      );
    }
  }
}

const v21 = program.backend.federationV21;
assert.equal(v21.status, 'pilot_validated');
assert.deepEqual(
  [...v21.route_wrapper_courses].sort(),
  routeManifestV21.courses.map(({ course_id }) => course_id).sort(),
);
assert.ok(v21.pilot_units >= routeManifestV21.courses.reduce((sum, course) => sum + course.units.length, 0));
assert.equal(v21.pilot_courses.length >= routeManifestV21.courses.length, true);
assert.equal(routeManifestV21.summary.course_count, routeManifestV21.courses.length);
assert.equal(routeManifestV21.summary.unit_count, routeManifestV21.courses.reduce((sum, course) => sum + course.units.length, 0));
assert.deepEqual(routeManifestV21.courses, [d20RouteManifest, c100RouteManifest]);
assert.deepEqual(legacyD20RouteBytes, d20RouteBytes, 'Alias rute D20 lama tidak identik dengan manifest kanonik.');

assert.equal(educationalAccess.datasetVersion, program.backend.educationalAccessResearch.version);
assert.equal(educationalAccess.summary.curriculum_resources, courses.length);
assert.equal(
  JSON.parse(educationalAccessSchemaBytes.toString('utf8')).$id,
  program.backend.educationalAccessResearch.schema,
);

assert.match(html, /<html lang="id">/);
assert.match(html, /href="styles\.css"/);
assert.match(html, /src="app\.js"/);
assert.match(html, /href="peta-belajar-luring\.html"/);
assert.match(html, /Unduh peta belajar — HTML satu berkas/);
assert.match(html, /STATIC-COURSE-FALLBACK:START/);
assert.match(html, /STATIC-COURSE-FALLBACK:END/);
const staticCourseIds = [...html.matchAll(/data-static-course-id="([A-D]\d{2,3})"/g)].map((match) => match[1]);
assert.equal(staticCourseIds.length, 40, 'Fallback tanpa JavaScript harus memuat tepat 40 mata kuliah.');
assert.deepEqual(staticCourseIds, effectiveCourses.map(({ id }) => id));
assert.match(html, /<noscript><section class="static-catalog"/);
assert.match(html, /id="progres"/);
assert.match(html, /id="learner-summary"/);
assert.match(html, /id="learner-storage-status"/);
assert.match(html, /Data ini tetap di browser ini dan tidak dikirim\./);
assert.match(html, /class="english-note" lang="en"/);
assert.match(html, new RegExp(escapeRegex(program.website)));
// The learner-facing page points at the current concept/landing archive, while
// `program.zenodo` may remain the immutable backend-authority record.  Require
// the public concept link (or the authority link for older snapshots) without
// coupling the static reader to one historical record number.
assert.ok(
  html.includes(program.zenodoConcept) || html.includes(program.zenodo),
  'Halaman siswa harus menautkan arsip Zenodo konsep atau otoritas.',
);
assert.match(html, new RegExp(`${courses.length} korpus terpilih`));
assert.match(html, /produksi yang belum selesai tetap dilabeli dengan jelas/i);
assert.match(html, new RegExp(`<strong id="live-completed-role-count">${effectiveCourses.filter(({ state }) => state === 'published').length}<\\/strong><span>peran dengan edisi selesai<\\/span>`));
assert.match(html, new RegExp(`${effectivePublishedCourses.length} peran melalui ${effectivePublishedRecordDois.size} rekaman DOI berbeda untuk edisi lengkap`));
assert.match(html, /A00, B10, C30, C40, C80, C130, D20, D60, dan D110/);
assert.match(html, /25 dari 40 peran/);
assert.match(html, /18 dari 33 keluarga backend native/);
assert.match(html, /sembilan ikatan peran melalui delapan paket/);
assert.match(html, /enam belas peran lainnya memakai kontrak kapabilitas keluarga yang teruji/);
assert.match(rootReadme, /D60 kini merupakan edisi komposit lengkap v0\.31\.7/);
assert.match(rootReadme, /Overlay penerus backend v2\.3 kini menerima sembilan ikatan peran melalui delapan paket kontrak 2\.3\.1: A00, B10, C30, C40, C80, C130, D20, D60, dan D110/);
assert.equal(v23AdapterIndex.adapters.find(({ role_id }) => role_id === 'D60').release_url, 'https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.10');
assert.equal(v23AdapterIndex.adapters.find(({ role_id }) => role_id === 'D110').canonical_records, 41460);
assert.equal(v23AdapterIndex.adapters.find(({ role_id }) => role_id === 'D110').release_url, 'https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.11');
assert.match(backendV23Readme, /27,642 canonical records/);
assert.match(backendV23Readme, /2,204 stable units/);
assert.match(backendV23Readme, /6,279 reversible materialized-native/);
assert.match(backendV23Readme, /8,338 native backend records/);
assert.match(backendV23Readme, /41,460 canonical records/);
assert.match(backendV23Readme, /10,978 native/);
assert.match(backendV23Readme, /138,894 canonical records/);
assert.match(backendV23Readme, /32,383 native records/);
assert.match(backendV23Readme, /other 33 course roles/);
assert.match(schemaV23Index, /A00, B10, C30, C40, C80, C130, D20, D60, dan D110/);
assert.match(schemaV23Index, /sembilan ikatan peran melalui delapan paket/);
assert.match(schemaV23Index, /722\/722 identitas sumber-terjemahan Open Logic/);
assert.match(schemaV23Index, /51\.704 rekaman kanonis dan tujuh rute publik/);
assert.match(schemaV23Index, /27\.642 rekaman kanonik/);
assert.match(schemaV23Index, /41\.460 rekaman kanonik/);
assert.match(schemaV23Index, /D110 pada v0\.62\.11/);
assert.match(html, new RegExp(`Mulai belajar — buka ${courses.length} mata kuliah`));
assert.match(html, new RegExp(escapeRegex(program.repositories.github.url)));
assert.match(html, /melanjutkan ke mana/);
assert.match(html, /“Lanjut ke”.*prasyarat langsung.*prasyarat lain/s);
assert.match(app, /Mulai belajar — HTML/);
assert.match(app, /Buka pembaca kerja — HTML/);
assert.match(app, /stateLabels\[nextCourse\.state\]/);
assert.match(app, /from '\.\/learner-delivery\.js'/);
assert.match(app, /from '\.\/learner-tools\.js'/);
assert.match(app, /learnerToolsByCourseId\[course\.id\]/);
assert.match(app, /Unduh HTML luring/);
assert.match(app, /statusSelect\.value === 'offline'/);
assert.match(app, /course\.repository/);
assert.match(app, /course\.supplements/);
assert.match(app, /nextCourseIdsById/);
assert.match(app, /Lanjut ke/);
assert.match(app, /data-course-link/);
assert.match(app, /from '\.\/learner-state\.js'/);
assert.deepEqual(publicLearnerStateSchemaBytes, learnerStateSchemaBytes, 'Salinan schema keadaan pelajar harus identik byte demi byte.');
assert.match(learnerStateModule, /program-matematika-indonesia\/learner-state\/v1/);
assert.doesNotMatch(learnerStateModule, /\bfetch\s*\(/);

assert.match(app, /courses as authorityCourses/);
assert.match(app, /materializeLiveCourses\(authorityCourses\)/);
assert.match(app, /deriveNextCourseIdsById\(courses\)/);
assert.match(app, /publicationProgress\(course\)/);
assert.match(app, /effectivePublishedCourses/);
assert.match(app, /livePublicationSummary\.textContent/);
assert.doesNotMatch(app, /liveCoursePublications\[/);

const deliveryById = new Map(learnerDelivery.courses.map((row) => [row.course_id, row]));
for (const row of learnerDelivery.courses) {
  assert.ok(['verified', 'available_unverified', 'absent', 'not_applicable'].includes(row.portable_html.status));
  if (row.portable_html.status === 'verified') {
    assert.match(row.portable_html.format, /zip\+html/);
    assert.equal(row.portable_html.dependency_free, true);
    assert.ok(Number.isInteger(row.portable_html.bytes) && row.portable_html.bytes > 0);
    assert.match(row.portable_html.sha256, /^[0-9a-f]{64}$/);
    assert.ok(row.portable_html.entry_point && Number.isInteger(row.portable_html.inventory_count));
    assert.doesNotMatch(row.portable_html.format, /pdf/i, `${row.course_id}: PDF tidak boleh dihitung sebagai HTML luring.`);
  }
}
const legacyReaderCandidatesRejectedByDeliveryAuthority = effectiveCourses
  .filter((course) => (course.learner || course.reader) && deliveryById.get(course.id)?.online_html.status === 'absent')
  .map(({ id }) => id);
assert.deepEqual(legacyReaderCandidatesRejectedByDeliveryAuthority, ['D90']);
assert.equal(
  learnerDelivery.summary.online_html_available,
  effectiveCourses.filter((course) => course.learner || course.reader).length - legacyReaderCandidatesRejectedByDeliveryAuthority.length,
);
assert.equal(learnerDelivery.summary.course_count, learnerDelivery.courses.length);
assert.equal(learnerDelivery.summary.online_html_available, learnerDelivery.courses.filter(({ online_html }) => online_html.status !== 'absent').length);
assert.equal(learnerDelivery.summary.verified_portable_html, learnerDelivery.courses.filter(({ portable_html }) => portable_html.status === 'verified').length);
assert.equal(learnerDelivery.summary.verified_epub, learnerDelivery.courses.filter(({ epub }) => epub.status === 'verified').length);
assert.equal(learnerDelivery.summary.online_html_available, 24);
assert.equal(learnerDelivery.summary.verified_portable_html, 6);
assert.equal(learnerDelivery.summary.verified_epub, 1);
assert.deepEqual(
  [...learnerDelivery.courses.filter(({ portable_html }) => portable_html.status === 'verified').map(({ course_id }) => course_id)].sort(),
  ['C100', 'D10', 'D30', 'D40', 'D120', 'D80'].sort(),
);
assert.equal(deliveryById.get('C100').portable_html.sha256, 'ee26d6e1228b7b66ca7ea156081c673dd1c8ab8b3488d87f7ee35cc354c091ae');
assert.equal(deliveryById.get('C100').epub.sha256, '5eb6773cc036015e8eb9e6f1791c6ec2f2b83812f43c8340c66aaafd91b12d99');
assert.equal(deliveryById.get('C100').online_html.status, 'verified');
assert.equal(deliveryById.get('C100').online_html.url, 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/reader/');
assert.equal(deliveryById.get('C100').online_html.bytes, 3_994_608);
assert.equal(deliveryById.get('C100').online_html.sha256, '1d3b49bc17a5956164d25b53ef6a2e79939a44f066fa87d84d00a66cca6da7ca');
assert.equal(deliveryById.get('C100').online_html.entry_point, 'index.html');
assert.equal(deliveryById.get('C100').online_html.inventory_count, 2);
assert.equal(deliveryById.get('C100').online_html.scope, 'whole_course');
assert.equal(deliveryById.get('C100').online_html.dependency_free, true);
assert.equal(deliveryById.get('D10').portable_html.sha256, 'a0333dca723085e93d472b945a03758b133b05cbe5be3022133088e5c1f5ab00');
const d10Delivery = deliveryById.get('D10');
assert.equal(d10Delivery.online_html.status, 'verified');
assert.equal(d10Delivery.online_html.url, 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/D10/reader/');
assert.equal(d10Delivery.online_html.bytes, 8571);
assert.equal(d10Delivery.online_html.sha256, '22ad13ef45160fa6bb964d600811b5141a6bcf8d23aac86790ddf652baca6737');
assert.equal(d10Delivery.online_html.entry_point, 'index.html');
assert.equal(d10Delivery.online_html.inventory_count, 138);
assert.equal(d10Delivery.online_html.scope, 'whole_course');
assert.equal(d10Delivery.online_html.dependency_free, true);
assert.equal(deliveryById.get('D30').pdf.sha256, 'dda34267df928672e03e04b4c8a36d768aab2d33bc1194b269074da0d2d24e40');
assert.equal(deliveryById.get('D30').portable_html.sha256, 'e32dba5a896fb847192bbe944e7fd3db4d95f61ee57e33751bbff3108fca214a');
assert.equal(deliveryById.get('D30').portable_html.entry_point, 'reader/index.html');
const d40Delivery = deliveryById.get('D40');
assert.equal(d40Delivery.primary.status, 'verified');
assert.equal(d40Delivery.primary.url, 'https://zenodo.org/records/22184259/files/PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_LENGKAP.pdf?download=1');
assert.deepEqual(d40Delivery.primary, d40Delivery.pdf);
assert.equal(d40Delivery.online_html.status, 'available_unverified');
assert.equal(d40Delivery.online_html.url, 'https://kokunoyumeto.github.io/program-matematika-indonesia/readers/d40/unit14/');
assert.equal(d40Delivery.pdf.status, 'verified');
assert.equal(d40Delivery.pdf.bytes, 4393637);
assert.equal(d40Delivery.pdf.url, 'https://zenodo.org/records/22184259/files/PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_LENGKAP.pdf?download=1');
assert.equal(d40Delivery.pdf.sha256, 'c4e4f470eeb096129e7bf7306422d316c93aaeed99d2b12890e08f15777ac13f');
assert.equal(d40Delivery.portable_html.status, 'verified');
assert.equal(d40Delivery.portable_html.bytes, 9436983);
assert.equal(d40Delivery.portable_html.url, 'https://zenodo.org/records/22184259/files/D40_COMPLETE_ID_20260831.zip?download=1');
assert.equal(d40Delivery.portable_html.sha256, 'a370bba5ddb54081387a484a304b24af92691c3bc167db964c486625a79add59');
assert.equal(d40Delivery.portable_html.entry_point, 'reader/html/index.html');
assert.equal(d40Delivery.portable_html.inventory_count, 273);
assert.equal(deliveryById.get('D80').portable_html.sha256, '064dc97e9ae58217622a768f1a989eb316892a607d219211f4be17e6cf44d03c');
const d120Delivery = deliveryById.get('D120');
assert.equal(d120Delivery.online_html.status, 'available_unverified');
assert.equal(d120Delivery.online_html.url, 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/D120/reader/');
assert.equal(d120Delivery.online_html.bytes, 36_311);
assert.equal(d120Delivery.online_html.sha256, '91875291e302741f442fa98ebecc9539ac3de43b4dbfdb07ea34bb559f978a42');
assert.equal(d120Delivery.online_html.entry_point, 'index.html');
assert.equal(d120Delivery.online_html.inventory_count, 60);
assert.equal(d120Delivery.online_html.scope, 'whole_course');
assert.equal(d120Delivery.online_html.dependency_free, true);
assert.equal(d120Delivery.portable_html.sha256, 'c47fb636c821d574cc987a39d512f608bc4796fe2c737d8d7d02b5d0540df7e9');
assert.equal(effectiveCoursesById.get('D120').reader, d120Delivery.online_html.url);
assert.ok(effectiveCoursesById.get('D120').supplements.some(({ id, url }) => id === 'd120-owner-html-reader' && url === 'https://kokunoyumeto.github.io/kerja-matematika-yang-dapat-ditelusuri-id/'));

const styles = stylesBytes.toString('utf8');
assert.match(styles, /\.card-action \{[^}]*min-height: 44px/s);
assert.match(styles, /@media print/);
assert.doesNotMatch(styles, /@media \(max-width: 820px\)[\s\S]{0,300}nav \{ display: none;/);
assert.match(styles, /p a:not\(\.button\):not\(\.card-action\)/);
const shellFiles = [Buffer.from(html), stylesBytes, Buffer.from(app), coursesModuleBytes, Buffer.from(livePublicationsModule), Buffer.from(learnerStateModule), deliveryModuleBytes, learnerToolsModuleBytes];
const shellRawBytes = shellFiles.reduce((sum, bytes) => sum + bytes.length, 0);
const shellGzipBytes = shellFiles.reduce((sum, bytes) => sum + gzipSync(bytes, { level: 9 }).length, 0);
// Legacy entry gained two language links, fragment-preserving handoff, and the
// hash-bound D100 learner/educator capability links. Each new language route
// has its own separately measured offline/closure budget.
assert.ok(shellRawBytes <= 203_000, `Shell melewati 203.000 byte: ${shellRawBytes}.`);
assert.ok(shellGzipBytes <= 51_000, `Shell gzip melewati 51.000 byte: ${shellGzipBytes}.`);
const runtimeAssetUrls = [
  ...[...html.matchAll(/<script\b[^>]*src="([^"]+)"[^>]*>/g)].map((match) => match[1]),
  ...[...html.matchAll(/<link\b(?=[^>]*rel="stylesheet")[^>]*href="([^"]+)"[^>]*>/g)].map((match) => match[1]),
].filter((url) => /^(?:https?:)?\/\//.test(url));
assert.deepEqual(runtimeAssetUrls, [], 'Shell tidak boleh memerlukan CSS atau JavaScript jarak jauh.');
const standalone = standaloneBytes.toString('utf8');
assert.equal((standalone.match(/data-static-course-id=/g) ?? []).length, 40);
assert.doesNotMatch(standalone, /href="styles\.css"|src="app\.js"|^\s*import\s/m);
assert.match(standalone, /const learnerDeliveryByCourseId = Object\.freeze\(/);
assert.match(standalone, /const learnerToolsByCourseId = Object\.freeze\(/);
assert.match(standalone, /Latihan & diagnosis/);
assert.match(standalone, /Peta bab & edisi arsip/);
assert.match(standalone, /"href":"https:\/\/kokunoyumeto\.github\.io\/program-matematika-indonesia\/id-ID\/courses\/A00\/latihan\/index\.html"/);
assert.doesNotMatch(standalone, /"href":"id-ID\/courses\/A00\/latihan\/index\.html"/);
for (const courseId of ['C30', 'C40']) {
  const escapedAbsolute = `https:\/\/kokunoyumeto\\.github\\.io\/program-matematika-indonesia\/backend\/judson\/${courseId}\\.html`;
  assert.match(standalone, new RegExp(`"href":"${escapedAbsolute}"`));
  assert.match(standalone, new RegExp(`href="${escapedAbsolute}"`));
  assert.doesNotMatch(standalone, new RegExp(`(?:"href":"|href=")backend/judson/${courseId}\\.html"`));
}
assert.match(standalone, /href="#katalog">Unduh peta belajar — HTML satu berkas/);
assert.match(standalone, new RegExp(`<strong id="live-completed-role-count">${effectivePublishedCourses.length}<\\/strong>`));
assert.match(standalone, /22184259/);
assert.match(standalone, /PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_LENGKAP\.pdf/);
assert.match(standalone, /D40_COMPLETE_ID_20260831\.zip/);
for (const name of ['index.html', 'styles.css', 'app.js', 'courses.js', 'live-course-publications.js', 'learner-state.js', 'learner-delivery.js', 'learner-tools.js', 'peta-belajar-luring.html', 'data/learner-delivery-v1.json', 'data/learner-tools-v1.json', 'data/course-capsule-v1/backend-design-policy-v1.json', 'data/course-capsule-v1/public-baseline-v0.62.12.json', 'data/course-capsule-v1/terminology-policy-v1/README.md', 'data/course-capsule-v1/terminology-policy-v1/canonical-register-policy.json', 'data/course-capsule-v1/terminology-policy-v1/checksums.sha256', 'data/v23-adapter-index-v2.json', 'data/modular-backend-pattern-index-v2.json', 'data/feature-adoption-provenance-v1.json', 'data/comparison-evidence-manifest-v1.json', 'data/modular-backend-snapshot-v2-validation-receipt.json', 'schema/v1/learner-delivery-v1.schema.json', 'schema/v1/learner-tools-v1.schema.json', 'schema/v1/v23-adapter-index-v1.schema.json', 'schema/v1/a00-assessment-map-v1.schema.json', 'schema/v2/v23-adapter-index-v2.schema.json', 'schema/v2/modular-backend-pattern-index-v2.schema.json', 'schema/v2/feature-adoption-provenance-v1.schema.json', 'schema/v2/comparison-evidence-manifest-v1.schema.json', 'schema/course-capsule-v1/backend-design-policy-v1.schema.json', 'schema/course-capsule-v1/public-baseline-v1.schema.json', 'schema/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json', 'schema/course-capsule-v1/v2/terminology-concept-record-v1.schema.json', 'id-ID/courses/A00/latihan/index.html', 'id-ID/courses/A00/latihan/latihan.css', 'id-ID/courses/A00/latihan/latihan.js', 'id-ID/courses/A00/latihan/assessment-map-v1.json', 'id-ID/courses/A00/latihan/anchor-audit-v1.json', 'id-ID/courses/D40/index.html', 'id-ID/courses/D120/D120_READER_MIRROR_MANIFEST_V1.json', 'id-ID/courses/D120/D120_READER_MIRROR_RECEIPT_V1.json', 'id-ID/courses/D120/README.md', 'id-ID/courses/D120/RIGHTS_AND_ATTRIBUTION.md', 'en/courses/D100/D100_ENGLISH_READER_MIRROR_MANIFEST_V1.json', 'en/courses/D100/D100_ENGLISH_READER_MIRROR_RECEIPT_V1.json', 'en/courses/D100/D100_ENGLISH_READER_PUBLIC_READBACK_V1.json', 'en/courses/D100/README.md', 'en/courses/D100/RIGHTS_AND_ATTRIBUTION.md', 'readers/d40/unit14/index.html', 'backend/judson/C30.html', 'backend/judson/C40.html', 'backend/judson/chapters.json', 'backend/judson/route-evidence.json', 'backend/judson/contribution.md', 'backend/judson/validation.json', 'backend/openlogic/C80.html', 'backend/openlogic/learner-route.json', 'backend/openlogic/validation.json', 'backend/c130/C130.html', 'backend/c130/learner-route.json', 'backend/c130/validation.json', 'backend/c120/C120.html', 'backend/c120/C120-pengajar.html', 'backend/c120/learning-map.json', 'backend/c120/educator-map.json', 'backend/c120/rights-and-terms.json', 'backend/c120/ledger-references.json', 'backend/c120/validation.json', 'backend/d10/D10.html', 'backend/d10/D10-pengajar.html', 'backend/d10/learning-map.json', 'backend/d10/educator-map.json', 'backend/d10/rights-and-terms.json', 'backend/d10/ledger-references.json', 'backend/d10/validation.json', 'backend/d100/D100.html', 'backend/d100/D100-pengajar.html', 'backend/d100/learning-map.json', 'backend/d100/validation.json', 'backend/d120/D120.html', 'backend/d120/D120-pengajar.html', 'backend/d120/learning-map.json', 'backend/d120/educator-map.json', 'backend/d120/validation.json']) {
  const [docsBytes, hostedBytes] = await Promise.all([
    readFile(resolve(root, 'docs', name)),
    readFile(resolve(root, 'public/hub', name)),
  ]);
  assert.deepEqual(hostedBytes, docsBytes, `${name}: mirror Sites berbeda dari docs.`);
}

for (const name of ['backend/c110/C110.html', 'backend/c110/C110-pengajar.html', 'backend/c110/learning-map.json', 'backend/c110/educator-map.json', 'backend/c110/translation-alignments.json', 'backend/c110/rights-and-terms.json', 'backend/c110/ledger-references.json', 'backend/c110/validation.json']) {
  const [docsBytes, hostedBytes] = await Promise.all([
    readFile(resolve(root, 'docs', name)),
    readFile(resolve(root, 'public/hub', name)),
  ]);
  assert.deepEqual(hostedBytes, docsBytes, `${name}: mirror C110 Sites berbeda dari docs.`);
}
for (const name of [
  'id-ID/courses/D10/D10_READER_MIRROR_MANIFEST_V1.json',
  'id-ID/courses/D10/D10_READER_MIRROR_RECEIPT_V1.json',
  'id-ID/courses/D10/README.md',
  'id-ID/courses/D10/RIGHTS_AND_ATTRIBUTION.md',
  'id-ID/courses/D10/licenses/CC0-1.0.txt',
  'id-ID/courses/D10/licenses/Design-Science-License.txt',
  'id-ID/courses/D10/licenses/MathJax-3.2.2-Apache-2.0.txt',
]) {
  const [docsBytes, hostedBytes] = await Promise.all([
    readFile(resolve(root, 'docs', name)),
    readFile(resolve(root, 'public/hub', name)),
  ]);
  assert.deepEqual(hostedBytes, docsBytes, `${name}: mirror Sites berbeda dari docs.`);
}
const d10MirrorManifest = await readJson('docs/id-ID/courses/D10/D10_READER_MIRROR_MANIFEST_V1.json');
assert.equal(d10MirrorManifest.schema, 'd10-reader-mirror-manifest-v1');
assert.equal(d10MirrorManifest.course_id, 'D10');
assert.equal(d10MirrorManifest.reader.file_count, 138);
assert.equal(d10MirrorManifest.reader.files.length, 138);
assert.equal(d10MirrorManifest.reader.bytes, 15_166_155);
assert.equal(d10MirrorManifest.reader.aggregate_sha256, '2af22c4a76c88ed0b8fe1f01e817f42e7354fb5b02c8c954c5a1731fac98ef53');
let d10MirrorBytes = 0;
const d10MirrorAggregate = createHash('sha256');
for (const row of d10MirrorManifest.reader.files) {
  assert.ok(!row.path.includes('\\') && !row.path.split('/').includes('..') && !row.path.startsWith('/'), `D10: jalur tidak aman ${row.path}`);
  const logical = `id-ID/courses/D10/reader/${row.path}`;
  const [docsBytes, hostedBytes] = await Promise.all([
    readFile(resolve(root, 'docs', logical)),
    readFile(resolve(root, 'public/hub', logical)),
  ]);
  assert.equal(docsBytes.length, row.bytes, `${logical}: byte manifest berbeda.`);
  assert.equal(sha256(docsBytes), row.sha256, `${logical}: hash manifest berbeda.`);
  assert.deepEqual(hostedBytes, docsBytes, `${logical}: mirror Sites berbeda dari docs.`);
  d10MirrorBytes += row.bytes;
  d10MirrorAggregate.update(`${row.sha256}\t${row.bytes}\t${row.path}\n`, 'utf8');
}
assert.equal(d10MirrorBytes, d10MirrorManifest.reader.bytes);
assert.equal(d10MirrorAggregate.digest('hex'), d10MirrorManifest.reader.aggregate_sha256);
const d120MirrorManifest = await readJson('docs/id-ID/courses/D120/D120_READER_MIRROR_MANIFEST_V1.json');
assert.equal(d120MirrorManifest.schema, 'd120-reader-mirror-manifest-v1');
assert.equal(d120MirrorManifest.course_id, 'D120');
assert.equal(d120MirrorManifest.reader.file_count, 60);
assert.equal(d120MirrorManifest.reader.files.length, 60);
assert.equal(d120MirrorManifest.reader.bytes, 2_844_307);
assert.equal(d120MirrorManifest.reader.aggregate_sha256, '4de6db10967c07574defa85e18cfabc2dec3c1019b415ef0fe5179524d6e8f6f');
let d120MirrorBytes = 0;
const d120MirrorAggregate = createHash('sha256');
for (const row of d120MirrorManifest.reader.files) {
  assert.ok(!row.path.includes('\\') && !row.path.split('/').includes('..') && !row.path.startsWith('/'), `D120: jalur tidak aman ${row.path}`);
  const logical = `id-ID/courses/D120/reader/${row.path}`;
  const [docsBytes, hostedBytes] = await Promise.all([
    readFile(resolve(root, 'docs', logical)),
    readFile(resolve(root, 'public/hub', logical)),
  ]);
  assert.equal(docsBytes.length, row.bytes, `${logical}: byte manifest berbeda.`);
  assert.equal(sha256(docsBytes), row.sha256, `${logical}: hash manifest berbeda.`);
  assert.deepEqual(hostedBytes, docsBytes, `${logical}: mirror Sites berbeda dari docs.`);
  d120MirrorBytes += row.bytes;
  d120MirrorAggregate.update(`${row.sha256}\t${row.bytes}\t${row.path}\n`, 'utf8');
}
assert.equal(d120MirrorBytes, d120MirrorManifest.reader.bytes);
assert.equal(d120MirrorAggregate.digest('hex'), d120MirrorManifest.reader.aggregate_sha256);
const d120MirrorReceipt = await readJson('docs/id-ID/courses/D120/D120_READER_MIRROR_RECEIPT_V1.json');
assert.equal(d120MirrorReceipt.schema, 'd120-reader-mirror-receipt-v1');
assert.equal(d120MirrorReceipt.status, 'pass');
assert.equal(d120MirrorReceipt.course_id, 'D120');
assert.equal(d120MirrorReceipt.destination.file_count, d120MirrorManifest.reader.file_count);
assert.equal(d120MirrorReceipt.destination.bytes, d120MirrorManifest.reader.bytes);
assert.equal(d120MirrorReceipt.destination.aggregate_sha256, d120MirrorManifest.reader.aggregate_sha256);
const d120ManifestBytes = await readFile(resolve(root, 'docs/id-ID/courses/D120/D120_READER_MIRROR_MANIFEST_V1.json'));
assert.equal(d120MirrorReceipt.manifest.bytes, d120ManifestBytes.length);
assert.equal(d120MirrorReceipt.manifest.sha256, sha256(d120ManifestBytes));
assert.equal(d120MirrorReceipt.source.archive_bytes, 787_617);
assert.equal(d120MirrorReceipt.source.archive_sha256, 'c47fb636c821d574cc987a39d512f608bc4796fe2c737d8d7d02b5d0540df7e9');
assert.equal(d120MirrorReceipt.validation.links.external_runtime_dependencies, 0);
assert.equal(d120MirrorReceipt.invariants.local_render_dependencies_complete, true);
assert.equal(d120MirrorReceipt.invariants.semantic_body_rewritten, false);
for (const row of d120MirrorReceipt.scripts) {
  const scriptBytes = await readFile(resolve(root, row.path));
  assert.equal(scriptBytes.length, row.bytes, `${row.path}: byte receipt berbeda.`);
  assert.equal(sha256(scriptBytes), row.sha256, `${row.path}: hash receipt berbeda.`);
}
const d100EnglishMirrorManifest = await readJson('docs/en/courses/D100/D100_ENGLISH_READER_MIRROR_MANIFEST_V1.json');
assert.equal(d100EnglishMirrorManifest.schema, 'd100-english-reader-mirror-manifest-v1');
assert.equal(d100EnglishMirrorManifest.course_id, 'D100');
assert.equal(d100EnglishMirrorManifest.locale, 'en');
assert.equal(d100EnglishMirrorManifest.reader.file_count, 474);
assert.equal(d100EnglishMirrorManifest.reader.files.length, 474);
assert.equal(d100EnglishMirrorManifest.reader.bytes, 50_946_101);
assert.equal(d100EnglishMirrorManifest.reader.aggregate_sha256, 'd9dd8b8c4358e38e7cd05b570899ae211fd24c39e04f746e571d1af92be59508');
let d100EnglishMirrorBytes = 0;
const d100EnglishMirrorAggregate = createHash('sha256');
for (const row of d100EnglishMirrorManifest.reader.files) {
  assert.ok(!row.path.includes('\\') && !row.path.split('/').includes('..') && !row.path.startsWith('/'), `D100 English: jalur tidak aman ${row.path}`);
  const logical = `en/courses/D100/reader/${row.path}`;
  const [docsBytes, hostedBytes] = await Promise.all([
    readFile(resolve(root, 'docs', logical)),
    readFile(resolve(root, 'public/hub', logical)),
  ]);
  assert.equal(docsBytes.length, row.bytes, `${logical}: byte manifest berbeda.`);
  assert.equal(sha256(docsBytes), row.sha256, `${logical}: hash manifest berbeda.`);
  assert.deepEqual(hostedBytes, docsBytes, `${logical}: mirror Sites berbeda dari docs.`);
  d100EnglishMirrorBytes += row.bytes;
  d100EnglishMirrorAggregate.update(`${row.sha256}\t${row.bytes}\t${row.path}\n`, 'utf8');
}
assert.equal(d100EnglishMirrorBytes, d100EnglishMirrorManifest.reader.bytes);
assert.equal(d100EnglishMirrorAggregate.digest('hex'), d100EnglishMirrorManifest.reader.aggregate_sha256);
const d100EnglishMirrorReceipt = await readJson('docs/en/courses/D100/D100_ENGLISH_READER_MIRROR_RECEIPT_V1.json');
assert.equal(d100EnglishMirrorReceipt.schema, 'd100-english-reader-mirror-receipt-v1');
assert.equal(d100EnglishMirrorReceipt.status, 'pass');
assert.equal(d100EnglishMirrorReceipt.course_id, 'D100');
assert.equal(d100EnglishMirrorReceipt.locale, 'en');
assert.equal(d100EnglishMirrorReceipt.destination.file_count, d100EnglishMirrorManifest.reader.file_count);
assert.equal(d100EnglishMirrorReceipt.destination.bytes, d100EnglishMirrorManifest.reader.bytes);
assert.equal(d100EnglishMirrorReceipt.destination.aggregate_sha256, d100EnglishMirrorManifest.reader.aggregate_sha256);
const d100EnglishManifestBytes = await readFile(resolve(root, 'docs/en/courses/D100/D100_ENGLISH_READER_MIRROR_MANIFEST_V1.json'));
assert.equal(d100EnglishMirrorReceipt.manifest.bytes, d100EnglishManifestBytes.length);
assert.equal(d100EnglishMirrorReceipt.manifest.sha256, sha256(d100EnglishManifestBytes));
assert.equal(d100EnglishMirrorReceipt.source.source_commit, '93dbf3b19907e9e13d42c8e342b449ebd0afc635');
assert.equal(d100EnglishMirrorReceipt.source.source_tree, 'bbad2aaddef6af27eb3563be2e01e252afe0edfc');
assert.equal(d100EnglishMirrorReceipt.validation.links.external_runtime_dependencies, 0);
assert.equal(d100EnglishMirrorReceipt.invariants.local_render_dependencies_complete, true);
assert.equal(d100EnglishMirrorReceipt.invariants.semantic_body_rewritten, false);
for (const row of d100EnglishMirrorReceipt.scripts) {
  const scriptBytes = await readFile(resolve(root, row.path));
  assert.equal(scriptBytes.length, row.bytes, `${row.path}: byte receipt berbeda.`);
  assert.equal(sha256(scriptBytes), row.sha256, `${row.path}: hash receipt berbeda.`);
}
const d100EnglishLanding = await readFile(resolve(root, 'docs/en/index.html'), 'utf8');
assert.match(d100EnglishLanding, /program-matematika-indonesia\/en\/courses\/D100\/reader\//);
assert.match(d100EnglishLanding, /algebraic-geometry-bridge-id\/en\//);
const d100EnglishReadback = await readJson('docs/en/courses/D100/D100_ENGLISH_READER_PUBLIC_READBACK_V1.json');
assert.equal(d100EnglishReadback.schema, 'd100-english-reader-public-readback-v1');
assert.equal(d100EnglishReadback.status, 'pass');
assert.equal(d100EnglishReadback.authentication, 'anonymous');
assert.equal(d100EnglishReadback.deployment.commit, 'a241226a492c69af94fd4668a7016da25be935c8');
assert.equal(d100EnglishReadback.deployment.tree, 'e58481d10abcdb23cdd786d42d44de27b9480a40');
assert.equal(d100EnglishReadback.scope.files_checked, 478);
assert.equal(d100EnglishReadback.scope.exact_files, 478);
assert.equal(d100EnglishReadback.scope.failures, 0);
assert.equal(d100EnglishReadback.invariants.every_course_file_http_200, true);
assert.equal(d100EnglishReadback.invariants.every_course_file_byte_and_sha256_exact, true);
assert.equal(d100EnglishReadback.invariants.central_reader_is_primary_on_english_landing, true);
assert.equal(d100EnglishReadback.invariants.owner_host_is_retained_as_alternate, true);
assert.match(livePublicationsModule, /id-ID\/courses\/B95\//);
assert.match(livePublicationsModule, /id-ID\/courses\/D10\/reader\//);
assert.match(livePublicationsModule, /id-ID\/courses\/D120\/reader\//);
assert.match(livePublicationsModule, /kerja-matematika-yang-dapat-ditelusuri-id\//);
assert.match(livePublicationsModule, /22192066/);
assert.match(livePublicationsModule, /22161412/);
assert.match(livePublicationsModule, /22184259/);
assert.match(livePublicationsModule, /PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_LENGKAP/);
assert.match(livePublicationsModule, /D40_COMPLETE_ID_20260831/);
assert.doesNotMatch(livePublicationsModule, /22164552/);
assert.match(livePublicationsModule, /22237442/);
assert.match(livePublicationsModule, /22161090/);
assert.match(livePublicationsModule, /22164668/);
assert.match(livePublicationsModule, /22236314/);
assert.match(livePublicationsModule, /(?:22164136|22183943)/);
assert.match(livePublicationsModule, /(?:22163372|22184443)/);
assert.match(livePublicationsModule, /clemens-snapp-workbook-u022/);
assert.match(b95Landing, /Statistika Berbasis Data/);
assert.match(b95Landing, /22192066/);
assert.match(b95Landing, /statistika-berbasis-data-id/);
assert.match(b95Landing, /322 halaman/);
assert.match(b95Landing, /GitHub \(B030\)/);
assert.match(b95Landing, /byte-identik di Zenodo serta GitHub/);
assert.match(b95Landing, /produksi berlanjut ke B031/);
assert.doesNotMatch(b95Landing, /href="[^"]+\.(?:json|jsonl|csv)(?:[?#"])/i);

assert.match(livePublicationsModule, /id-ID\/courses\/D30\//);
assert.match(livePublicationsModule, /22182655/);
assert.match(livePublicationsModule, /CHECKPOINT_38/);
assert.match(livePublicationsModule, /22168033/);
assert.match(livePublicationsModule, /laboratorium komputasi 4\/4/);
assert.match(livePublicationsModule, /capstone D60/);
assert.match(livePublicationsModule, /22076539/);
assert.match(d30Landing, /Probabilitas Teoretis-Ukuran dan Proses Stokastik/);
assert.match(d30Landing, /447 halaman/);
assert.match(d30Landing, /36\/36 masalah penguasaan/);
assert.match(d30Landing, /2 formulir asesmen/);
assert.match(d30Landing, /14 unit penguasaan/);
assert.match(d30Landing, /5 laboratorium/);
assert.match(d30Landing, /Mulai belajar — HTML/);
assert.match(d30Landing, /Unduh PDF 447 halaman/);
assert.match(d30Landing, /Unduh HTML luring \(3,0 MB\)/);
assert.match(d30Landing, /PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_READER_CHECKPOINT_38\.zip/);
assert.doesNotMatch(d30Landing, /4 laboratorium publik|2 irisan laboratorium/);
assert.match(d30Landing, /22182655/);
assert.match(d30Landing, /measure-theoretic-probability-stochastic-processes-id/);
assert.doesNotMatch(d30Landing, /href="[^"]+\.(?:json|jsonl|csv)(?:[?#"])/i);

assert.equal(c100ReaderBytes.length, c100RouteManifest.reader.source_html.bytes);
assert.equal(sha256(c100ReaderBytes), c100RouteManifest.reader.source_html.sha256);
assert.equal(c100ReaderStyleBytes.length, c100RouteManifest.reader.source_style.bytes);
assert.equal(sha256(c100ReaderStyleBytes), c100RouteManifest.reader.source_style.sha256);
assert.equal(c100SolutionBytes.length, c100RouteManifest.reader.solution_pdf.bytes);
assert.equal(sha256(c100SolutionBytes), c100RouteManifest.reader.solution_pdf.sha256);
assert.match(c100Landing, /Mulai membaca HTML/);
assert.doesNotMatch(c100Landing, /href="[^"]+\.(?:json|jsonl|csv)(?:[?#"])/i);

for (const unit of d20RouteManifest.units) {
  const wrapper = await readFile(resolve(root, `docs/id-ID/courses/D20/units/${unit.slug}/index.html`), 'utf8');
  assert.ok(wrapper.includes(`rel="canonical" href="${unit.central_url}"`), `${unit.id}: URL kanonis D20 tidak cocok.`);
  assert.ok(wrapper.includes(`href="${unit.native_html_url}"`), `${unit.id}: tautan pembaca D20 tidak cocok.`);
}
for (const unit of c100RouteManifest.units.filter(({ kind }) => kind === 'chapter')) {
  const chapter = unit.id.match(/\.ch(\d{2})$/)?.[1];
  if (!chapter) continue;
  const wrapper = await readFile(resolve(root, `docs/id-ID/courses/C100/units/bab-${chapter}/index.html`), 'utf8');
  assert.ok(wrapper.includes(`rel="canonical" href="${unit.central_url}"`), `${unit.id}: URL kanonis C100 tidak cocok.`);
  assert.ok(wrapper.includes(`reader/#${unit.id}`), `${unit.id}: fragmen pembaca C100 hilang.`);
}

const blankTargets = [...html.matchAll(/<a\b[^>]*target="_blank"[^>]*>/g)].map(([tag]) => tag);
for (const tag of blankTargets) assert.match(tag, /rel="[^"]*noreferrer[^"]*"/);

console.log(JSON.stringify({
  status: 'pass',
  version: program.version,
  zenodo: program.zenodo,
  courses: courses.length,
  selected: selectedIds.length,
  unresolved: unresolvedIds.length,
  publishedCanonRoles: publishedIds.length,
  effectivePublishedRoles: effectivePublishedCourses.length,
  effectiveDistinctPublishedRecords: effectivePublishedRecordDois.size,
  liveOverlayRows: Object.keys(liveCoursePublications).length,
  completedPublicCourseRoles: publishedIds.length,
  completedPublicRecords: program.completedPublicRecordDois.length,
  publishedHtmlReaders: publishedHtmlReaderIds.length,
  effectiveHtmlLearnerEntries: learnerDelivery.summary.online_html_available,
  verifiedPortableHtmlPackages: learnerDelivery.summary.verified_portable_html,
  verifiedEpubPackages: learnerDelivery.summary.verified_epub,
  learnerToolCourses: learnerTools.courses.length,
  learnerTools: learnerToolsRows.reduce((sum, row) => sum + row.tools.length, 0),
  a00Assessments: a00AssessmentMap.counts.assessments,
  a00ResolvedAnchors: a00AnchorAudit.counts.matched_exactly_once,
  staticNoJsCourseEntries: staticCourseIds.length,
  shellRawBytes,
  shellGzipBytes,
  prerequisiteEdges: prerequisiteEdgeCount,
  federationV2Records: federationManifest.record_count,
  locallyVerifiedAdapterFiles,
  releasedArchiveReferences,
  publicReadbackOverlays: authority.public_readback_overlays.length,
  topics: topics.length,
  levelCounts: Object.fromEntries([...new Set(courses.map(({ level }) => level))].map((level) => [level, courses.filter((course) => course.level === level).length])),
}, null, 2));
