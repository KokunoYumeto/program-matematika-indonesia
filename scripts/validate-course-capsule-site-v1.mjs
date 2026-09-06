import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const checkPublic = process.argv.includes('--public');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const identity = (path, bytes) => ({ path, bytes: bytes.length, sha256: sha256(bytes) });
const sortValue = (value) => {
  if (Array.isArray(value)) return value.map(sortValue);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sortValue(value[key])]));
  return value;
};
const canonicalJson = (value) => JSON.stringify(sortValue(value), null, 2) + '\n';
const logicalFiles = [
  'backend/coverage.html',
  'backend/program-backend-coverage.json',
  'backend/index.html',
  'backend/backend.css',
  'backend/backend.js',
  'backend/judson/C30.html',
  'backend/judson/C40.html',
  'backend/judson/chapters.json',
  'backend/judson/route-evidence.json',
  'backend/judson/contribution.md',
  'backend/judson/validation.json',
  'backend/openlogic/C80.html',
  'backend/openlogic/learner-route.json',
  'backend/openlogic/validation.json',
  'backend/c130/C130.html',
  'backend/c130/learner-route.json',
  'backend/c130/validation.json',
  'backend/a20/A20.html',
  'backend/a20/A20-pengajar.html',
  'backend/a20/capabilities.json',
  'backend/a20/claim-boundary.json',
  'backend/a20/data/concept-index.jsonl',
  'backend/a20/data/corrections-index.jsonl',
  'backend/a20/data/exercise-index.jsonl',
  'backend/a20/data/module-index.jsonl',
  'backend/a20/data/native-record-ledger.json',
  'backend/a20/data/pedagogical-relation-index.jsonl',
  'backend/a20/data/rights-index.jsonl',
  'backend/a20/data/terms-index.jsonl',
  'backend/a20/educator-map.json',
  'backend/a20/learning-map.json',
  'backend/a20/public-evidence.json',
  'backend/a20/public-native-readback.json',
  'backend/a20/source-lock.json',
  'backend/a20/validation.json',
  'backend/a30/A30.html',
  'backend/a30/A30-pengajar.html',
  'backend/a30/capabilities.json',
  'backend/a30/claim-boundary.json',
  'backend/a30/data/concept-index.jsonl',
  'backend/a30/data/corrections-index.jsonl',
  'backend/a30/data/exercise-index.jsonl',
  'backend/a30/data/chapter-index.jsonl',
  'backend/a30/data/module-index.jsonl',
  'backend/a30/data/native-record-ledger.json',
  'backend/a30/data/pedagogical-relation-index.jsonl',
  'backend/a30/data/rights-index.jsonl',
  'backend/a30/data/segment-state-summary.json',
  'backend/a30/data/terms-index.jsonl',
  'backend/a30/educator-map.json',
  'backend/a30/learning-map.json',
  'backend/a30/public-evidence.json',
  'backend/a30/public-native-readback.json',
  'backend/a30/source-lock.json',
  'backend/a30/validation.json',
  'backend/b80/B80.html',
  'backend/b80/B80-pengajar.html',
  'backend/b80/learning-map.json',
  'backend/b80/validation.json',
  'backend/b40/B40.html',
  'backend/b40/B40-pengajar.html',
  'backend/b40/learning-map.json',
  'backend/b40/educator-map.json',
  'backend/b40/concept-index.json',
  'backend/b40/relation-index.json',
  'backend/b40/rights-and-terms.json',
  'backend/b40/ledger-references.json',
  'backend/b40/public-evidence.json',
  'backend/b40/manifest.json',
  'backend/b40/validation.json',
  'backend/b90/B90.html',
  'backend/b90/B90-pengajar.html',
  'backend/b90/capabilities.json',
  'backend/b90/learning-map.json',
  'backend/b90/educator-map.json',
  'backend/b90/public-evidence.json',
  'backend/b90/claim-boundary.json',
  'backend/b90/data/unit-index.jsonl',
  'backend/b90/data/concept-index.jsonl',
  'backend/b90/data/relation-index.jsonl',
  'backend/b90/data/terms-index.jsonl',
  'backend/b90/data/corrections-index.jsonl',
  'backend/b90/data/rights-index.jsonl',
  'backend/b90/source-lock.json',
  'backend/b90/public-native-readback.json',
  'backend/b90/validation.json',
  'backend/c60/C60.html',
  'backend/c60/C60-pengajar.html',
  'backend/c60/capabilities.json',
  'backend/c60/learning-map.json',
  'backend/c60/educator-map.json',
  'backend/c60/concept-index.json',
  'backend/c60/relation-index.json',
  'backend/c60/rights-and-terms.json',
  'backend/c60/ledger-references.json',
  'backend/c60/native-id-index.json',
  'backend/c60/public-evidence.json',
  'backend/c60/claim-boundary.json',
  'backend/c60/manifest.json',
  'backend/c60/validation.json',
  'backend/d70/D70.html',
  'backend/d70/D70-pengajar.html',
  'backend/d70/learning-map.json',
  'backend/d70/validation.json',
  'backend/d90/D90.html',
  'backend/d90/D90-pengajar.html',
  'backend/d90/capabilities.json',
  'backend/d90/learning-map.json',
  'backend/d90/educator-map.json',
  'backend/d90/public-evidence.json',
  'backend/d90/claim-boundary.json',
  'backend/d90/data/rights-index.jsonl',
  'backend/d90/data/corrections-index.jsonl',
  'backend/d90/data/terms-index.jsonl',
  'backend/d90/validation.json',
  'backend/d10/D10.html',
  'backend/d10/D10-pengajar.html',
  'backend/d10/learning-map.json',
  'backend/d10/educator-map.json',
  'backend/d10/rights-and-terms.json',
  'backend/d10/ledger-references.json',
  'backend/d10/validation.json',
  'backend/d30/D30.html',
  'backend/d30/D30-pengajar.html',
  'backend/d30/capabilities.json',
  'backend/d30/learning-map.json',
  'backend/d30/learner-map.json',
  'backend/d30/educator-map.json',
  'backend/d30/public-evidence.json',
  'backend/d30/claim-boundary.json',
  'backend/d30/data/rights-index.jsonl',
  'backend/d30/data/corrections-index.jsonl',
  'backend/d30/data/terms-index.jsonl',
  'backend/d30/data/relations-index.jsonl',
  'backend/d30/validation.json',
  'backend/d100/D100.html',
  'backend/d100/D100-pengajar.html',
  'backend/d100/learning-map.json',
  'backend/d100/validation.json',
  'backend/d120/D120.html',
  'backend/d120/D120-pengajar.html',
  'backend/d120/learning-map.json',
  'backend/d120/educator-map.json',
  'backend/d120/validation.json',
  'backend/c110/C110.html',
  'backend/c110/C110-pengajar.html',
  'backend/c110/learning-map.json',
  'backend/c110/educator-map.json',
  'backend/c110/translation-alignments.json',
  'backend/c110/rights-and-terms.json',
  'backend/c110/ledger-references.json',
  'backend/c110/validation.json',
  'backend/c120/C120.html',
  'backend/c120/C120-pengajar.html',
  'backend/c120/learning-map.json',
  'backend/c120/educator-map.json',
  'backend/c120/rights-and-terms.json',
  'backend/c120/ledger-references.json',
  'backend/c120/validation.json',
  'backend/c70/C70.html',
  'backend/c70/C70-pengajar.html',
  'backend/c70/learning-map.json',
  'backend/c70/educator-map.json',
  'backend/c70/concept-index.json',
  'backend/c70/relation-index.json',
  'backend/c70/rights-and-terms.json',
  'backend/c70/ledger-references.json',
  'backend/c70/public-evidence.json',
  'backend/c70/validation.json',
  'data/course-capsule-v1/course-capsules.jsonl',
  'data/course-capsule-v1/course-capsules.json',
  'data/course-capsule-v1/manifest.json',
  'data/course-capsule-v1/validation-receipt.json',
  'data/course-capsule-v1/README.md',
  'data/course-capsule-v1/backend-design-policy-v1.json',
  'data/course-capsule-v1/public-baseline-v0.62.12.json',
  'data/course-capsule-v1/native-package-references-v1.json',
  'data/course-capsule-v1/native-family-public-evidence-v1.json',
  'data/course-capsule-v1/native-family-public-evidence-note-v1.md',
  'data/course-capsule-v1/native-terminology-qa/unib-teori-bilangan-20260831/README.md',
  'data/course-capsule-v1/native-terminology-qa/unib-teori-bilangan-20260831/terminology_concordance.json',
  'data/course-capsule-v1/native-terminology-qa/unib-teori-bilangan-20260831/checksums.sha256',
  'data/course-capsule-v1/terminology-policy-v1/README.md',
  'data/course-capsule-v1/terminology-policy-v1/canonical-register-policy.json',
  'data/course-capsule-v1/terminology-policy-v1/checksums.sha256',
  'data/learner-tools-v1.json',
  'data/modular-backend-pattern-index-v1.json',
  'data/modular-backend-pattern-index-v2.json',
  'data/v23-adapter-index-v1.json',
  'data/v23-adapter-index-v2.json',
  'data/clp-successor/v0.62.17/v23-adapter-index-v2.json',
  'data/feature-adoption-provenance-v1.json',
  'data/comparison-evidence-manifest-v1.json',
  'data/modular-backend-snapshot-v2-validation-receipt.json',
  'schema/course-capsule-v1/course-capsule-v1.schema.json',
  'schema/course-capsule-v1/backend-design-policy-v1.schema.json',
  'schema/course-capsule-v1/public-baseline-v1.schema.json',
  'schema/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json',
  'schema/course-capsule-v1/v2/terminology-concept-record-v1.schema.json',
  'schema/v1/learner-tools-v1.schema.json',
  'schema/v1/v23-adapter-index-v1.schema.json',
  'schema/v2/v23-adapter-index-v2.schema.json',
  'schema/v2/modular-backend-pattern-index-v2.schema.json',
  'schema/v2/feature-adoption-provenance-v1.schema.json',
  'schema/v2/comparison-evidence-manifest-v1.schema.json',
];
const docsBytes = Object.fromEntries(await Promise.all(logicalFiles.map(async (path) => [path, await readFile(resolve(project, 'docs', path))])));
const html = docsBytes['backend/index.html'].toString('utf8');
const css = docsBytes['backend/backend.css'].toString('utf8');
const js = docsBytes['backend/backend.js'].toString('utf8');
const rows = JSON.parse(docsBytes['data/course-capsule-v1/course-capsules.json'].toString('utf8'));
const jsonlRows = docsBytes['data/course-capsule-v1/course-capsules.jsonl'].toString('utf8').trimEnd().split('\n').map(JSON.parse);
const manifest = JSON.parse(docsBytes['data/course-capsule-v1/manifest.json'].toString('utf8'));
const validation = JSON.parse(docsBytes['data/course-capsule-v1/validation-receipt.json'].toString('utf8'));
const publicLearnerTools = JSON.parse(docsBytes['data/learner-tools-v1.json'].toString('utf8'));
const judsonC30Html = docsBytes['backend/judson/C30.html'].toString('utf8');
const judsonC40Html = docsBytes['backend/judson/C40.html'].toString('utf8');
const judsonChapters = JSON.parse(docsBytes['backend/judson/chapters.json'].toString('utf8'));
const judsonRouteEvidenceBytes = docsBytes['backend/judson/route-evidence.json'];
const judsonRouteEvidence = JSON.parse(judsonRouteEvidenceBytes.toString('utf8'));
const judsonValidation = JSON.parse(docsBytes['backend/judson/validation.json'].toString('utf8'));
const openLogicHtml = docsBytes['backend/openlogic/C80.html'].toString('utf8');
const openLogicRoute = JSON.parse(docsBytes['backend/openlogic/learner-route.json'].toString('utf8'));
const openLogicValidation = JSON.parse(docsBytes['backend/openlogic/validation.json'].toString('utf8'));
const c130Html = docsBytes['backend/c130/C130.html'].toString('utf8');
const c130Route = JSON.parse(docsBytes['backend/c130/learner-route.json'].toString('utf8'));
const c130Validation = JSON.parse(docsBytes['backend/c130/validation.json'].toString('utf8'));
const v23AdapterIndex = JSON.parse(docsBytes['data/v23-adapter-index-v1.json'].toString('utf8'));
const v23AdapterIndexV2 = JSON.parse(docsBytes['data/v23-adapter-index-v2.json'].toString('utf8'));
const clpSuccessorIndex = JSON.parse(docsBytes['data/clp-successor/v0.62.17/v23-adapter-index-v2.json'].toString('utf8'));
const clpSuccessorAuthority = await readFile(resolve(project, 'backend/course-capsule-v1/authority/clp-family-v231/v23-adapter-index-v2.json'));
assert.deepEqual(docsBytes['data/clp-successor/v0.62.17/v23-adapter-index-v2.json'], clpSuccessorAuthority, 'CLP successor public index differs from its authority.');
// The frozen CLP successor index predates the later A10 and D50 central
// admissions and must stay byte-stable. The live course capsules add both
// roles without rewriting that history.
const expectedFrozenSuccessorAdapterRoles = ['A00', 'B10', 'B20', 'B30', 'B50', 'B60', 'C30', 'C40', 'C80', 'C130', 'D20', 'D60', 'D110'];
const expectedLiveAdapterRoles = [...expectedFrozenSuccessorAdapterRoles, 'A10', 'D50'];
const expectedCapabilityAdapterRoles = ['A20', 'A30', 'B40', 'B70', 'B80', 'B90', 'C10', 'C20', 'C50', 'C60', 'C70', 'C90', 'C100', 'C110', 'C120', 'D10', 'D30', 'D40', 'D70', 'D80', 'D90', 'D100', 'D120'];
const expectedCapabilityPackageCount = 20;
const sortedIds = (ids) => [...ids].sort((a, b) => a.localeCompare(b, 'en', { numeric: true }));
assert.deepEqual(sortedIds(clpSuccessorIndex.adapters.map(({ role_id }) => role_id)), sortedIds(expectedFrozenSuccessorAdapterRoles), 'Frozen successor adapter role set differs.');
assert.equal(new Set(clpSuccessorIndex.packages.map(({ package_id }) => package_id)).size, 9);
assert.equal(clpSuccessorIndex.packages.length, 9);
const patternIndexV2 = JSON.parse(docsBytes['data/modular-backend-pattern-index-v2.json'].toString('utf8'));
const featureAdoption = JSON.parse(docsBytes['data/feature-adoption-provenance-v1.json'].toString('utf8'));
const comparisonEvidence = JSON.parse(docsBytes['data/comparison-evidence-manifest-v1.json'].toString('utf8'));
const snapshotV2Receipt = JSON.parse(docsBytes['data/modular-backend-snapshot-v2-validation-receipt.json'].toString('utf8'));
const publicDesignPolicy = JSON.parse(docsBytes['data/course-capsule-v1/backend-design-policy-v1.json'].toString('utf8'));
const publicBaseline = JSON.parse(docsBytes['data/course-capsule-v1/public-baseline-v0.62.12.json'].toString('utf8'));
const publicTerminologyPolicy = JSON.parse(docsBytes['data/course-capsule-v1/terminology-policy-v1/canonical-register-policy.json'].toString('utf8'));
const [authorityLearnerToolsBytes, authorityLearnerToolsSchemaBytes, integrationOverrideBytes, authorityDesignPolicyBytes, authorityBaselineBytes, authorityDesignPolicySchemaBytes, authorityBaselineSchemaBytes, authorityTerminologyReadmeBytes, authorityTerminologyPolicyBytes, authorityTerminologyChecksumsBytes, authorityTerminologyPolicySchemaBytes, authorityTerminologyConceptSchemaBytes] = await Promise.all([
  readFile(resolve(project, 'backend/authority/learner-tools-v1.json')),
  readFile(resolve(project, 'schemas/v1/learner-tools-v1.schema.json')),
  readFile(resolve(project, 'backend/course-capsule-v1/authority/integration-overrides-v1.json')),
  readFile(resolve(project, 'backend/course-capsule-v1/authority/backend-design-policy-v1.json')),
  readFile(resolve(project, 'backend/course-capsule-v1/authority/public-baseline-v0.62.12.json')),
  readFile(resolve(project, 'schemas/course-capsule-v1/backend-design-policy-v1.schema.json')),
  readFile(resolve(project, 'schemas/course-capsule-v1/public-baseline-v1.schema.json')),
  readFile(resolve(project, 'backend/course-capsule-v1/authority/terminology-policy-v1/README.md')),
  readFile(resolve(project, 'backend/course-capsule-v1/authority/terminology-policy-v1/canonical-register-policy.json')),
  readFile(resolve(project, 'backend/course-capsule-v1/authority/terminology-policy-v1/checksums.sha256')),
  readFile(resolve(project, 'schemas/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json')),
  readFile(resolve(project, 'schemas/course-capsule-v1/v2/terminology-concept-record-v1.schema.json')),
]);
assert.deepEqual(docsBytes['data/learner-tools-v1.json'], authorityLearnerToolsBytes, 'Public learner-tool authority mirror drift.');
assert.deepEqual(docsBytes['schema/v1/learner-tools-v1.schema.json'], authorityLearnerToolsSchemaBytes, 'Public learner-tool schema mirror drift.');
assert.deepEqual(docsBytes['data/course-capsule-v1/backend-design-policy-v1.json'], authorityDesignPolicyBytes, 'Public design-policy mirror drift.');
assert.deepEqual(docsBytes['data/course-capsule-v1/public-baseline-v0.62.12.json'], authorityBaselineBytes, 'Public baseline mirror drift.');
assert.deepEqual(docsBytes['schema/course-capsule-v1/backend-design-policy-v1.schema.json'], authorityDesignPolicySchemaBytes, 'Public design-policy schema mirror drift.');
assert.deepEqual(docsBytes['schema/course-capsule-v1/public-baseline-v1.schema.json'], authorityBaselineSchemaBytes, 'Public baseline schema mirror drift.');
assert.deepEqual(docsBytes['data/course-capsule-v1/terminology-policy-v1/README.md'], authorityTerminologyReadmeBytes, 'Public terminology-policy README mirror drift.');
assert.deepEqual(docsBytes['data/course-capsule-v1/terminology-policy-v1/canonical-register-policy.json'], authorityTerminologyPolicyBytes, 'Public terminology policy mirror drift.');
assert.deepEqual(docsBytes['data/course-capsule-v1/terminology-policy-v1/checksums.sha256'], authorityTerminologyChecksumsBytes, 'Public terminology-policy checksum mirror drift.');
assert.deepEqual(docsBytes['schema/course-capsule-v1/v2/canonical-terminology-register-policy-v1.schema.json'], authorityTerminologyPolicySchemaBytes, 'Public terminology-policy schema mirror drift.');
assert.deepEqual(docsBytes['schema/course-capsule-v1/v2/terminology-concept-record-v1.schema.json'], authorityTerminologyConceptSchemaBytes, 'Public terminology concept-record schema mirror drift.');
assert.equal(publicDesignPolicy.profile, 'thin_format_neutral_zero_copy');
assert.equal(publicBaseline.release.tag, 'v0.62.12');
assert.equal(publicBaseline.release.asset_count, 100);
assert.equal(publicBaseline.zenodo.record_id, 22182000);
assert.equal(publicTerminologyPolicy.schema_id, 'interlanguage/program-matematika-indonesia-canonical-terminology-register-policy/v1');
assert.equal(publicTerminologyPolicy.locale, 'id-ID');
assert.equal(publicTerminologyPolicy.decision_procedure.length, 9);
assert.deepEqual(publicTerminologyPolicy.decision_procedure.map(({ sequence }) => sequence), [1, 2, 3, 4, 5, 6, 7, 8, 9]);
assert.equal(publicTerminologyPolicy.termbase_contract.schema_id, 'interlanguage/program-matematika-indonesia-terminology-concept/v1');
assert.equal(publicTerminologyPolicy.probability_family_audit.status, 'evidence_required');
assert.equal(publicTerminologyPolicy.probability_family_audit.automatic_replacement_allowed, false);
assert.equal(publicTerminologyPolicy.probability_family_audit.concepts.length, 9);
assert.equal(publicTerminologyPolicy.probability_family_audit.concepts.every(({ decision_state }) => decision_state === 'evidence_required'), true);
assert.match(publicTerminologyPolicy.scope.methodology_boundary, /program's explicit synthesis/);
const terminologyPolicyChecksums = Object.fromEntries(authorityTerminologyChecksumsBytes.toString('utf8').trim().split(/\r?\n/).map((line) => {
  const match = /^([a-f0-9]{64})  (.+)$/.exec(line);
  assert.ok(match, `Malformed terminology-policy checksum row: ${line}`);
  return [match[2], match[1]];
}));
assert.deepEqual(Object.keys(terminologyPolicyChecksums).sort(), ['README.md', 'canonical-register-policy.json']);
assert.equal(terminologyPolicyChecksums['README.md'], sha256(authorityTerminologyReadmeBytes));
assert.equal(terminologyPolicyChecksums['canonical-register-policy.json'], sha256(authorityTerminologyPolicyBytes));
const authorityLearnerTools = JSON.parse(authorityLearnerToolsBytes.toString('utf8'));
const integrationOverrides = JSON.parse(integrationOverrideBytes.toString('utf8'));
assert.deepEqual(publicLearnerTools, authorityLearnerTools, 'Parsed public learner-tool authority drift.');
const authorityToolsByCourse = Object.fromEntries(authorityLearnerTools.courses.map(({ course_id, tools }) => [course_id, structuredClone(tools)]));
for (const [courseId, tools] of Object.entries(integrationOverrides.learner_tools ?? {})) {
  authorityToolsByCourse[courseId] ??= [];
  authorityToolsByCourse[courseId].push(...structuredClone(tools));
  authorityToolsByCourse[courseId].sort((left, right) => left.tool_id.localeCompare(right.tool_id));
}
const authorityToolIds = Object.values(authorityToolsByCourse).flatMap((tools) => tools.map(({ tool_id }) => tool_id));
const mainHtml = await readFile(resolve(project, 'docs/index.html'), 'utf8');

assert.equal(rows.length, 40);
assert.deepEqual(rows, jsonlRows);
assert.equal(new Set(rows.map(({ course_id }) => course_id)).size, 40);
assert.equal(rows.filter(({ course }) => course.state === 'published').length, 38);
assert.equal(rows.filter(({ course }) => course.state === 'production').length, 2);
assert.equal(rows.filter((row) => row.layers.educator.features.length || row.layers.educator.resources.length).length, 33);
// The v2 snapshot below remains immutable at nine bindings. The live capsules
// additionally admit the four CLP roles; test the exact role set, not just a count.
assert.deepEqual(sortedIds(rows.filter((row) => ['verified', 'legacy_verified'].includes(row.layers.interoperability.semantic_adapter.status) && row.layers.interoperability.semantic_adapter.contract_version === '2.3.1').map(({ course_id }) => course_id)), sortedIds(expectedLiveAdapterRoles));
assert.deepEqual(
  sortedIds(rows.filter((row) => ['verified', 'legacy_verified'].includes(row.layers.interoperability.semantic_adapter.status) && row.layers.interoperability.semantic_adapter.contract_version !== '2.3.1').map(({ course_id }) => course_id)),
  sortedIds(expectedCapabilityAdapterRoles),
);
assert.equal(manifest.summary.verified_semantic_adapter_count, expectedLiveAdapterRoles.length + expectedCapabilityAdapterRoles.length);
const b80 = rows.find(row=>row.course_id==='B80');
assert.equal(b80.layers.interoperability.semantic_adapter.contract_version,'course-learning-capability/1');
assert.equal(b80.layers.interoperability.semantic_adapter.status,'verified');
assert.equal(b80.layers.learner.tools.length,2);
assert.equal(b80.layers.educator.resources.length,1);
assert.equal(JSON.parse(docsBytes['backend/b80/validation.json']).state,'pass');
assert.equal(JSON.parse(docsBytes['backend/d70/validation.json']).result,'PASS');
assert.equal(JSON.parse(docsBytes['backend/d100/validation.json']).state,'pass');
const a20 = rows.find(row=>row.course_id==='A20');
const a20Validation = JSON.parse(docsBytes['backend/a20/validation.json']);
const a20Capabilities = JSON.parse(docsBytes['backend/a20/capabilities.json']);
const a20LearningMap = JSON.parse(docsBytes['backend/a20/learning-map.json']);
const a20EducatorMap = JSON.parse(docsBytes['backend/a20/educator-map.json']);
const a20PublicEvidence = JSON.parse(docsBytes['backend/a20/public-evidence.json']);
const a20PublicNativeReadback = JSON.parse(docsBytes['backend/a20/public-native-readback.json']);
const a20ClaimBoundary = JSON.parse(docsBytes['backend/a20/claim-boundary.json']);
const a20SourceLock = JSON.parse(docsBytes['backend/a20/source-lock.json']);
const a30 = rows.find(row => row.course_id === 'A30');
const a30Validation = JSON.parse(docsBytes['backend/a30/validation.json']);
const a30Capabilities = JSON.parse(docsBytes['backend/a30/capabilities.json']);
const a30LearningMap = JSON.parse(docsBytes['backend/a30/learning-map.json']);
const a30EducatorMap = JSON.parse(docsBytes['backend/a30/educator-map.json']);
const a30PublicEvidence = JSON.parse(docsBytes['backend/a30/public-evidence.json']);
const a30PublicNativeReadback = JSON.parse(docsBytes['backend/a30/public-native-readback.json']);
const a30ClaimBoundary = JSON.parse(docsBytes['backend/a30/claim-boundary.json']);
const a30SourceLock = JSON.parse(docsBytes['backend/a30/source-lock.json']);
const a30AdapterManifest = JSON.parse(await readFile(resolve(project, 'backend/course-capsule-v1/adapters/a30-capability-v1/manifest.json')));
const a30AdapterValidationBytes = await readFile(resolve(project, 'backend/course-capsule-v1/adapters/a30-capability-v1/validation.json'));
const d10Validation = JSON.parse(docsBytes['backend/d10/validation.json']);
const d10LearningMap = JSON.parse(docsBytes['backend/d10/learning-map.json']);
const d10EducatorMap = JSON.parse(docsBytes['backend/d10/educator-map.json']);
const d10RightsAndTerms = JSON.parse(docsBytes['backend/d10/rights-and-terms.json']);
  const d10LedgerReferences = JSON.parse(docsBytes['backend/d10/ledger-references.json']);
const d30Html = docsBytes['backend/d30/D30.html'].toString('utf8');
const d30EducatorHtml = docsBytes['backend/d30/D30-pengajar.html'].toString('utf8');
const d30Capabilities = JSON.parse(docsBytes['backend/d30/capabilities.json']);
const d30LearningMap = JSON.parse(docsBytes['backend/d30/learning-map.json']);
const d30LearnerMap = JSON.parse(docsBytes['backend/d30/learner-map.json']);
const d30EducatorMap = JSON.parse(docsBytes['backend/d30/educator-map.json']);
const d30PublicEvidence = JSON.parse(docsBytes['backend/d30/public-evidence.json']);
const d30ClaimBoundary = JSON.parse(docsBytes['backend/d30/claim-boundary.json']);
const d30Validation = JSON.parse(docsBytes['backend/d30/validation.json']);
const d30AdapterManifest = JSON.parse(await readFile(resolve(project, 'backend/course-capsule-v1/adapters/d30-capability-v1/manifest.json')));
const d30AdapterValidationBytes = await readFile(resolve(project, 'backend/course-capsule-v1/adapters/d30-capability-v1/validation.json'));
const centralNavigationOverlay = JSON.parse(await readFile(resolve(project, 'backend/authority/central-course-surface-navigation-overlay-v1.json')));
const d120Validation = JSON.parse(docsBytes['backend/d120/validation.json']);
const d120LearningMap = JSON.parse(docsBytes['backend/d120/learning-map.json']);
const d120EducatorMap = JSON.parse(docsBytes['backend/d120/educator-map.json']);
assert.equal(d120Validation.state,'pass');
const d90Validation = JSON.parse(docsBytes['backend/d90/validation.json']);
const d90LearningMap = JSON.parse(docsBytes['backend/d90/learning-map.json']);
const d90EducatorMap = JSON.parse(docsBytes['backend/d90/educator-map.json']);
const d90Capabilities = JSON.parse(docsBytes['backend/d90/capabilities.json']);
const d90PublicEvidence = JSON.parse(docsBytes['backend/d90/public-evidence.json']);
const d90ClaimBoundary = JSON.parse(docsBytes['backend/d90/claim-boundary.json']);
const c60Validation = JSON.parse(docsBytes['backend/c60/validation.json']);
const c60Capabilities = JSON.parse(docsBytes['backend/c60/capabilities.json']);
const c60LearningMap = JSON.parse(docsBytes['backend/c60/learning-map.json']);
const c60EducatorMap = JSON.parse(docsBytes['backend/c60/educator-map.json']);
const c60ConceptIndex = JSON.parse(docsBytes['backend/c60/concept-index.json']);
const c60RelationIndex = JSON.parse(docsBytes['backend/c60/relation-index.json']);
const c60RightsAndTerms = JSON.parse(docsBytes['backend/c60/rights-and-terms.json']);
const c60LedgerReferences = JSON.parse(docsBytes['backend/c60/ledger-references.json']);
const c60NativeIdIndex = JSON.parse(docsBytes['backend/c60/native-id-index.json']);
const c60PublicEvidence = JSON.parse(docsBytes['backend/c60/public-evidence.json']);
const c60ClaimBoundary = JSON.parse(docsBytes['backend/c60/claim-boundary.json']);
const c60Manifest = JSON.parse(docsBytes['backend/c60/manifest.json']);
const c120Validation = JSON.parse(docsBytes['backend/c120/validation.json']);
const c120LearningMap = JSON.parse(docsBytes['backend/c120/learning-map.json']);
const c120EducatorMap = JSON.parse(docsBytes['backend/c120/educator-map.json']);
const c120RightsAndTerms = JSON.parse(docsBytes['backend/c120/rights-and-terms.json']);
const c120LedgerReferences = JSON.parse(docsBytes['backend/c120/ledger-references.json']);
assert.equal(c120Validation.state,'pass');
const c110Validation = JSON.parse(docsBytes['backend/c110/validation.json']);
const c110LearningMap = JSON.parse(docsBytes['backend/c110/learning-map.json']);
const c110EducatorMap = JSON.parse(docsBytes['backend/c110/educator-map.json']);
const c110Alignments = JSON.parse(docsBytes['backend/c110/translation-alignments.json']);
const c110RightsAndTerms = JSON.parse(docsBytes['backend/c110/rights-and-terms.json']);
const c110LedgerReferences = JSON.parse(docsBytes['backend/c110/ledger-references.json']);
assert.equal(c110Validation.state,'pass');
const c70Validation = JSON.parse(docsBytes['backend/c70/validation.json']);
const c70LearningMap = JSON.parse(docsBytes['backend/c70/learning-map.json']);
const c70EducatorMap = JSON.parse(docsBytes['backend/c70/educator-map.json']);
const c70ConceptIndex = JSON.parse(docsBytes['backend/c70/concept-index.json']);
const c70RelationIndex = JSON.parse(docsBytes['backend/c70/relation-index.json']);
const c70RightsAndTerms = JSON.parse(docsBytes['backend/c70/rights-and-terms.json']);
const c70LedgerReferences = JSON.parse(docsBytes['backend/c70/ledger-references.json']);
const c70PublicEvidence = JSON.parse(docsBytes['backend/c70/public-evidence.json']);
assert.equal(c70Validation.state,'pass');
const b40Validation = JSON.parse(docsBytes['backend/b40/validation.json']);
const b40LearningMap = JSON.parse(docsBytes['backend/b40/learning-map.json']);
const b40EducatorMap = JSON.parse(docsBytes['backend/b40/educator-map.json']);
const b40ConceptIndex = JSON.parse(docsBytes['backend/b40/concept-index.json']);
const b40RelationIndex = JSON.parse(docsBytes['backend/b40/relation-index.json']);
const b40RightsAndTerms = JSON.parse(docsBytes['backend/b40/rights-and-terms.json']);
const b40LedgerReferences = JSON.parse(docsBytes['backend/b40/ledger-references.json']);
const b40PublicEvidence = JSON.parse(docsBytes['backend/b40/public-evidence.json']);
const b40Manifest = JSON.parse(docsBytes['backend/b40/manifest.json']);
assert.equal(b40Validation.state,'pass');
assert.equal(rows.filter((row) => Object.keys(row.layers).sort().join(',') === 'curriculum,educator,federation,interoperability,learner,production,translation').length, 40);
assert.equal(rows.filter((row) => row.learner_directed && row.open_access_policy.public_access_required).length, 40);
for (const row of rows) assert.deepEqual(row.layers.learner.tools, authorityToolsByCourse[row.course_id] ?? [], `${row.course_id}: public capsule learner-tool drift.`);
assert.equal(rows.filter((row) => row.layers.interoperability.design_policy?.profile === 'thin_format_neutral_zero_copy').length, 40);
assert.equal(manifest.summary.course_count, 40);
assert.equal(Object.keys(authorityToolsByCourse).length, 28);
assert.equal(authorityToolIds.length, 38);
assert.equal(manifest.summary.learner_tool_course_count, Object.keys(authorityToolsByCourse).length);
assert.equal(manifest.summary.learner_tool_count, authorityToolIds.length);
assert.equal(manifest.summary.published_count, 38);
assert.equal(manifest.summary.production_count, 2);
assert.equal(manifest.design_policy.profile, 'thin_format_neutral_zero_copy');
assert.equal(manifest.design_policy.authority.sha256, sha256(authorityDesignPolicyBytes));
assert.equal(manifest.design_policy.schema.sha256, sha256(authorityDesignPolicySchemaBytes));
assert.equal(manifest.public_baseline.version, 'v0.62.12');
assert.equal(manifest.public_baseline.authority.sha256, sha256(authorityBaselineBytes));
assert.equal(manifest.public_baseline.schema.sha256, sha256(authorityBaselineSchemaBytes));
assert.equal(validation.state, 'pass');
assert.equal(validation.checks.seven_layer_rows, 40);
assert.equal(validation.checks.learner_tool_authority_equality, 'pass');
assert.equal(validation.peer_replay.byte_identical, true);

const ids = rows.map(({ course_id }) => course_id);
const edges = rows.flatMap((row) => row.course.prerequisites.map((source) => [source, row.course_id]));
const incoming = Object.fromEntries(ids.map((id) => [id, 0]));
const outgoing = Object.fromEntries(ids.map((id) => [id, []]));
for (const [source, target] of edges) {
  assert.ok(ids.includes(source));
  outgoing[source].push(target);
  incoming[target] += 1;
}
const queue = ids.filter((id) => incoming[id] === 0);
let visited = 0;
while (queue.length) {
  const id = queue.shift();
  visited += 1;
  for (const target of outgoing[id]) {
    incoming[target] -= 1;
    if (incoming[target] === 0) queue.push(target);
  }
}
assert.equal(edges.length, 83);
assert.equal(visited, 40);

assert.match(html, /<html lang="id">/);
assert.match(html, /class="skip-link"/);
assert.match(html, /data-view="learner"/);
assert.match(html, /data-view="educator"/);
assert.match(html, /data-view="production"/);
assert.match(html, /data-view="interop"/);
assert.equal((html.match(/data-static-course-id=/g) ?? []).length, 40);
assert.deepEqual([...html.matchAll(/data-static-course-id="([^"]+)"/g)].map((match) => match[1]), ids);
for (const [name, expected] of Object.entries({
  total: rows.length,
  published: rows.filter((row) => row.course.state === 'published').length,
  production: rows.filter((row) => row.course.state === 'production').length,
  educator: rows.filter((row) => row.layers.educator.features.length || row.layers.educator.resources.length).length,
})) {
  const match = html.match(new RegExp(`<strong id="summary-${name}">(\\d+)</strong>`));
  assert.ok(match, `${name}: static summary is missing.`);
  assert.equal(Number(match[1]), expected, `${name}: static summary differs from data.`);
}
assert.match(html, /JSONL kanonis/);
assert.match(html, /Tanda terima validasi/);
assert.match(html, /Kebijakan backend tipis, netral-format, zero-copy/);
assert.match(html, /Baseline publik v0\.62\.12/);
assert.match(html, /href="\.\.\/data\/v23-adapter-index-v2\.json"/);
assert.match(html, /href="\.\.\/data\/clp-successor\/v0\.62\.17\/v23-adapter-index-v2\.json"/);
assert.match(html, /Ledger adopsi fitur tujuh lapis/);
assert.match(html, /overlay pascapublikasi v0\.62\.14/i);
assert.match(html, /sembilan ikatan peran memakai delapan paket yang telah terbit dan dibaca balik/);
assert.doesNotMatch(html, /publikasi paket pusat masih tertunda|pending_successor_release/);
assert.match(html, /href="\.\.\/id-ID\/courses\/A00\/latihan\/index\.html"/);
assert.match(html, /Latihan &amp; diagnosis/);
assert.match(html, /href="\.\.\/backend\/openlogic\/C80\.html"/);
assert.match(html, /Buka Open Logic lengkap/);
assert.match(html, /<p lang="en">/);
assert.match(mainHtml, /href="backend\/index\.html">Belajar &amp; mengajar<\/a>/);
assert.match(mainHtml, /href="backend\/index\.html">Buka pusat belajar &amp; mengajar<\/a>/);
assert.match(css, /font-size:\s*17px/);
assert.match(css, /@media \(max-width: 780px\)/);
assert.match(css, /prefers-reduced-motion/);
assert.match(css, /\.sr-only\s*\{[\s\S]*?clip:\s*rect\(0, 0, 0, 0\)/);
assert.match(js, /course-capsules\.json/);
assert.match(js, /prerequisite_diagnostics/);
assert.match(js, /staged_hints_answers_solutions/);
assert.match(js, /zero-copy/i);
assert.match(js, /aria-pressed/);
assert.match(html, /role="group" aria-label="Sudut pandang katalog"/);
assert.match(html, /class="filters" role="group" aria-label="Saringan katalog"/);
assert.match(html, /class="summary-strip" role="group" aria-label="Ringkasan program"/);
assert.match(html, /id="cara-baca" aria-labelledby="status-reading-title"/);
assert.match(html, /id="data-terbuka" aria-labelledby="open-data-title"/);
assert.doesNotMatch(html, /role="tab(?:list)?"/);
assert.match(js, /layer\.tools/);
assert.match(js, /machine_data_is_learner_destination/);
assert.doesNotMatch(js, /link\(tool\.resource/i, 'Backend UI must not expose raw machine data as a learner action.');
assert.match(js, /available_unverified/);
assert.match(js, /Buka sumber utama —/);
assert.match(js, /terbuka di tab baru/);
assert.match(css, /\.topbar nav\s*\{\s*display:\s*none/);
assert.doesNotMatch(css, /@media[^}]+\}\s*nav\s*\{\s*display:\s*none/i);
assert.doesNotMatch(html, />Buka sumber utama ↗</);
const staticPrimaryLabels = [...html.matchAll(/Buka sumber utama — ([A-D][0-9]{2,3}) ↗/g)].map((match) => match[1]);
assert.equal(new Set(staticPrimaryLabels).size, staticPrimaryLabels.length, 'Static primary-link accessible labels are duplicated.');
assert.ok(staticPrimaryLabels.every((id) => ids.includes(id)), 'Static primary-link label names an unknown course.');
const c80StaticStart = html.indexOf('data-static-course-id="C80"');
const c80StaticEnd = html.indexOf('data-static-course-id="C90"');
assert.ok(c80StaticStart >= 0 && c80StaticEnd > c80StaticStart);
assert.match(html.slice(c80StaticStart, c80StaticEnd), /Kesiapan akses<\/span><strong>tersedia; belum diverifikasi penuh<\/strong>/);
assert.equal((html.match(/Kesiapan akses/g) ?? []).length, 40);
assert.equal((html.match(/Bahan pengajar terindeks/g) ?? []).length, 0);

for (const row of rows) {
  assert.match(row.course_native.edition, /^https:\/\//);
  if (row.course_native.repository) assert.match(row.course_native.repository, /^https:\/\//);
  if (row.course_native.zenodo) assert.match(row.course_native.zenodo, /^https:\/\//);
  for (const component of row.layers.federation.components) {
    assert.equal(component.access, 'public');
    if (component.url) assert.match(component.url, /^https:\/\//);
  }
}
assert.equal(a20.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(a20.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(a20.layers.learner.tools.map(({ tool_id, href }) => ({ tool_id, href })), [
  { tool_id: 'a20.open_learner_hub', href: 'backend/a20/A20.html' },
]);
assert.equal(a20.layers.curriculum.unit_identity_status, 'verified');
assert.equal(a20.layers.translation.ledger_status, 'verified');
assert.equal(a20.layers.translation.terminology_status, 'verified');
assert.equal(a20.layers.translation.rights_status, 'verified');
assert.equal(a20.layers.translation.corrections_status, 'verified');
assert.equal(a20.layers.production.build_status, 'verified');
assert.equal(a20.layers.production.deterministic_replay_status, 'verified');
assert.equal(a20.layers.educator.status, 'verified');
assert.equal(a20.layers.educator.unit_alignment_status, 'verified');
assert.equal(a20.layers.educator.resources.length, 10);
assert.equal(a20.layers.learner.pdf.bytes, 412049461);
assert.equal(a20.layers.learner.pdf.sha256, '76276eeab590cd8181fd531378c4b4860bf30289a5e8093c9af5788d1eca3a9c');
assert.equal(a20.layers.learner.online_html.status, 'not_yet_produced');
assert.equal(a20.layers.learner.capabilities.semantic_html, 'not_yet_produced');
assert.equal(a20.layers.learner.capabilities.mathml, 'not_yet_produced');
assert.equal(a20Validation.result, 'pass');
assert.equal(a20Validation.counts.native_records, 174535);
assert.equal(a20Validation.counts.modules, 83);
assert.equal(a20Validation.counts.exercises, 8209);
assert.equal(a20Validation.counts.solution_identities, 5238);
assert.equal(a20Validation.counts.unsolved_exercises, 2971);
assert.equal(a20Validation.negative_fixtures.length, 15);
assert.equal(a20Capabilities.counts.component_rights, 17);
assert.equal(a20Capabilities.counts.terms, 340);
assert.equal(a20Capabilities.counts.corrections, 1614);
assert.equal(a20LearningMap.chapters.length, 12);
assert.equal(a20LearningMap.modules.length, 83);
assert.equal(a20LearningMap.front_matter_modules.length, 1);
assert.equal(a20LearningMap.body_content_embedded, false);
assert.equal(a20LearningMap.prerequisite.authority, 'central_curriculum_overlay');
assert.equal(a20LearningMap.prerequisite.native_source_assertion, false);
assert.equal(a20LearningMap.english_source_mirror.translation_claimed, false);
assert.equal(a20LearningMap.english_source_mirror.common_adapter_consumption_claimed, false);
assert.equal(a20EducatorMap.selectable_modules.length, 83);
assert.equal(a20EducatorMap.solution_bodies_embedded, false);
assert.equal(a20EducatorMap.official_teacher_manual_claimed, false);
assert.equal(a20PublicEvidence.anonymous_readback, true);
assert.equal(a20PublicEvidence.credentials_used, false);
assert.equal(a20PublicEvidence.github_release.total_bytes, 1102054925);
assert.equal(a20PublicEvidence.zenodo.total_bytes, 1102054925);
assert.equal(a20PublicEvidence.zenodo.access_right, 'open');
assert.equal(a20PublicNativeReadback.state, 'pass');
assert.equal(a20PublicNativeReadback.anonymous, true);
assert.equal(a20PublicNativeReadback.credentials_used, false);
assert.deepEqual(a20PublicNativeReadback.failures, []);
assert.equal(a20SourceLock.native_export.record_count, 174535);
assert.equal(a20SourceLock.native_export.jsonl_sha256, 'f8536e60b6e6fde9855da51e9d1d9037e5772190a1fd2e6ee4189c1f024172d3');
assert.equal(a20SourceLock.indonesian_release.repository_landing_is_complete_authority, false);
assert.equal(a20ClaimBoundary.native_bodies_copied, false);
assert.equal(a20ClaimBoundary.exercise_or_problem_bodies_copied, 0);
assert.equal(a20ClaimBoundary.solution_bodies_copied, 0);
assert.equal(a20ClaimBoundary.unsolved_exercises_preserved, 2971);
assert.equal(a20ClaimBoundary.all_exercises_claimed_solved, false);
assert.equal(a20ClaimBoundary.indonesian_semantic_html_claimed, false);
assert.equal(a20ClaimBoundary.indonesian_mathml_claimed, false);
assert.equal(a20ClaimBoundary.public_access_state_changed, false);
assert.equal(docsBytes['backend/a20/data/module-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 83);
assert.equal(docsBytes['backend/a20/data/exercise-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 8209);
assert.equal(docsBytes['backend/a20/data/concept-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 236);
assert.equal(docsBytes['backend/a20/data/pedagogical-relation-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 32393);
assert.equal(docsBytes['backend/a20/data/rights-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 17);
assert.equal(docsBytes['backend/a20/data/corrections-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 1614);
assert.equal(docsBytes['backend/a20/data/terms-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 340);
assert.equal(a30.course.state, 'published');
assert.equal(a30.course_native.status, 'available_unverified');
assert.equal(a30.course_native.version, '1.0.0');
assert.equal(a30.course_native.repository, 'https://github.com/KokunoYumeto/openstax-precalculus-2e-id');
assert.equal(a30.course_native.zenodo, 'https://doi.org/10.5281/zenodo.22290180');
assert.equal(a30.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(a30.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.equal(
  a30.layers.interoperability.semantic_adapter.mapping_scope,
  'zero_copy_projection_of_220680_native_records_87_modules_7250_exercise_problem_identities_4183_solution_identities_497_concepts_513_terms_703_corrections_1875_component_rights_and_segment_state_asymmetry_with_3067_unsupported_solution_cases_preserved',
);
assert.deepEqual(a30.layers.learner.tools.map(({ tool_id, href }) => ({ tool_id, href })), [
  { tool_id: 'a30.open_learner_hub', href: 'backend/a30/A30.html' },
]);
assert.equal(a30.layers.learner.tools[0].page.path, 'docs/backend/a30/A30.html');
assert.equal(a30.layers.learner.tools[0].resource.path, 'docs/backend/a30/learning-map.json');
assert.equal(a30.layers.learner.tools[0].evidence.path, 'docs/backend/a30/validation.json');
assert.equal(a30.layers.learner.pdf.status, 'verified');
assert.equal(a30.layers.learner.pdf.bytes, 305654938);
assert.equal(a30.layers.learner.pdf.sha256, '3cfd5294b91252cc766992f158b6601e80aa31b719b0b8bf69e1ff6d08a4fa3e');
assert.equal(a30.layers.learner.online_html.status, 'not_yet_produced');
assert.equal(a30.layers.learner.portable_html.status, 'not_yet_produced');
assert.equal(a30.layers.learner.epub.status, 'not_yet_produced');
assert.equal(a30.layers.learner.capabilities.semantic_html, 'not_yet_produced');
assert.equal(a30.layers.learner.capabilities.mathml, 'not_yet_produced');
assert.equal(a30.layers.learner.capabilities.chapter_downloads, 'not_yet_produced');
assert.equal(a30.layers.learner.capabilities.print_profile, 'verified');
assert.equal(a30.layers.curriculum.unit_identity_status, 'verified');
assert.equal(a30.layers.translation.ledger_status, 'verified');
assert.equal(a30.layers.translation.terminology_status, 'verified');
assert.equal(a30.layers.translation.rights_status, 'verified');
assert.equal(a30.layers.translation.corrections_status, 'verified');
assert.equal(a30.layers.production.build_status, 'verified');
assert.equal(a30.layers.production.deterministic_replay_status, 'verified');
assert.equal(a30.layers.educator.status, 'verified');
assert.equal(a30.layers.educator.unit_alignment_status, 'verified');
assert.deepEqual(a30.layers.educator.resources.map(({ id, status }) => ({ id, status })), [
  { id: 'A30:educator-hub-v1', status: 'verified' },
  { id: 'A30:educator-map-v1', status: 'verified' },
  { id: 'A30:chapter-index-v1', status: 'verified' },
  { id: 'A30:module-index-v1', status: 'verified' },
  { id: 'A30:exercise-index-v1', status: 'verified' },
  { id: 'A30:concept-index-v1', status: 'verified' },
  { id: 'A30:relation-index-v1', status: 'verified' },
  { id: 'A30:terms-index-v1', status: 'verified' },
  { id: 'A30:rights-index-v1', status: 'verified' },
  { id: 'A30:corrections-index-v1', status: 'verified' },
  { id: 'A30:segment-state-summary-v1', status: 'verified' },
  { id: 'A30:native-record-ledger-v1', status: 'verified' },
]);
assert.equal(a30Validation.schema, 'a30-capability-validation/1');
assert.equal(a30Validation.result, 'pass');
assert.equal(a30Validation.course_id, 'A30');
for (const [key, expected] of Object.entries({
  native_records: 220680,
  chapters: 12,
  modules: 87,
  units: 26965,
  segments: 149955,
  relations: 37974,
  exercises: 7250,
  problems: 7250,
  solution_identities: 4183,
  unsupported_exercises: 3067,
  concepts: 497,
  terms: 513,
  corrections: 703,
  component_rights: 1875,
  pdf_pages: 3165,
})) assert.equal(a30Validation.counts[key], expected, `A30 validation count drift: ${key}`);
assert.deepEqual(a30Validation.checks.solution_identity_boundary_preserved, { with_solution_identity: 4183, without_native_solution_support: 3067 });
assert.equal(a30Validation.checks.source_target_and_body_text_absent, true);
assert.equal(a30Validation.checks.standalone_raw_replay_not_claimed, true);
assert.equal(a30Validation.checks.final_derivative_git_commit_or_tree_not_claimed, true);
assert.equal(a30Validation.checks.public_source_receipt_state, 'pass');
assert.equal(a30Validation.checks.public_source_assets, 7);
assert.equal(a30Validation.checks.public_zenodo_assets, 7);
assert.equal(a30Validation.checks.two_run_build_identity.file_count, 49);
assert.equal(a30Validation.checks.two_run_build_identity.tree_sha256, '51b3c1cf9f3709a540fe59c9df63b186968ceb6c41fccce265c504bf970244cd');
assert.equal(a30Capabilities.schema, 'a30-capabilities/1');
assert.equal(a30Capabilities.contract, 'course-learning-capability/1');
assert.equal(a30Capabilities.native_role_id, 'R002');
assert.deepEqual(a30Capabilities.curriculum_graph.prerequisite_course_ids, ['A20']);
assert.deepEqual(a30Capabilities.curriculum_graph.native_prerequisite_ids, []);
assert.equal(a30Capabilities.curriculum_graph.prerequisite_authority, 'central_curriculum_overlay');
assert.equal(a30Capabilities.learner_delivery.module_navigation, true);
assert.equal(a30Capabilities.learner_delivery.partial_solution_identity_coverage, true);
assert.equal(a30Capabilities.learner_delivery.exercise_pdf_destinations_indexed, false);
assert.equal(a30Capabilities.learner_delivery.indonesian_semantic_html, false);
assert.equal(a30Capabilities.educator_delivery.module_selector, true);
assert.equal(a30Capabilities.educator_delivery.official_teacher_manual, false);
assert.equal(a30Capabilities.federation.stable_native_ids_preserved, true);
assert.equal(a30Capabilities.federation.body_content_embedded, false);
assert.equal(a30Capabilities.federation.source_or_target_text_embedded, false);
assert.equal(a30Capabilities.federation.source_companion_required_for_full_replay, true);
assert.equal(a30Capabilities.federation.standalone_raw_replay_claimed, false);
assert.equal(a30LearningMap.schema, 'a30-learner-map/1');
assert.equal(a30LearningMap.modules.length, 87);
assert.equal(a30LearningMap.chapters.length, 12);
assert.equal(a30LearningMap.exercise_identity_count, 7250);
assert.equal(a30LearningMap.solution_identity_count, 4183);
assert.equal(a30LearningMap.unsupported_exercise_count, 3067);
assert.equal(a30LearningMap.indonesian_reader.pdf_pages, 3165);
assert.equal(a30LearningMap.indonesian_reader.module_page_routes, true);
assert.equal(a30LearningMap.indonesian_reader.exercise_pdf_destinations_indexed, false);
assert.equal(a30LearningMap.body_content_embedded, false);
assert.equal(a30LearningMap.source_or_target_text_embedded, false);
assert.equal(a30EducatorMap.schema, 'a30-educator-map/1');
assert.equal(a30EducatorMap.selectable_modules.length, 87);
assert.equal(a30EducatorMap.chapter_summaries.length, 12);
assert.equal(a30EducatorMap.exercise_identity_count, 7250);
assert.equal(a30EducatorMap.solution_identity_count, 4183);
assert.equal(a30EducatorMap.unsupported_exercise_count, 3067);
assert.equal(a30EducatorMap.official_teacher_manual_claimed, false);
assert.equal(a30EducatorMap.solution_bodies_embedded, false);
assert.equal(a30EducatorMap.body_content_embedded, false);
assert.equal(a30EducatorMap.source_or_target_text_embedded, false);
assert.equal(a30PublicEvidence.schema, 'a30-public-evidence/1');
assert.equal(a30PublicEvidence.anonymous_readback, true);
assert.equal(a30PublicEvidence.credentials_used, false);
assert.equal(a30PublicEvidence.repository.tag, 'v1.0.0');
assert.equal(a30PublicEvidence.repository.final_derivative_revision_proved, false);
assert.equal(a30PublicEvidence.indonesian_reader.pdf_pages, 3165);
assert.equal(a30PublicEvidence.indonesian_reader.semantic_html, false);
assert.equal(a30PublicEvidence.indonesian_reader.mathml, false);
assert.equal(a30PublicEvidence.zenodo.record_id, 22290180);
assert.equal(a30PublicEvidence.zenodo.concept_id, 22059757);
assert.equal(a30PublicEvidence.zenodo.access_right, 'open');
assert.equal(a30PublicNativeReadback.schema, 'a30-native-public-readback/1');
assert.equal(a30PublicNativeReadback.state, 'pass');
assert.equal(a30PublicNativeReadback.anonymous, true);
assert.equal(a30PublicNativeReadback.credentials_used, false);
assert.deepEqual(a30PublicNativeReadback.failures, []);
assert.equal(a30PublicNativeReadback.native_backend.records, 220680);
assert.equal(a30PublicNativeReadback.native_backend.modules, 87);
assert.equal(a30PublicNativeReadback.native_backend.chapters, 12);
assert.equal(a30PublicNativeReadback.native_backend.pages, 3165);
assert.equal(a30PublicNativeReadback.repository.public, true);
assert.equal(a30PublicNativeReadback.repository.tag, 'v1.0.0');
assert.equal(a30PublicNativeReadback.github_release.assets.length, 7);
assert.equal(a30PublicNativeReadback.zenodo.assets.length, 7);
assert.equal(a30PublicNativeReadback.zenodo.access_right, 'open');
assert.equal(a30SourceLock.native_export.record_count, 220680);
assert.equal(a30SourceLock.native_export.jsonl_sha256, '4f2f51457adde0516c17b1633327a3bfbbf273a67925514bbb6c390f5e58a054');
assert.equal(a30SourceLock.native_export.source_companion_required_for_full_replay, true);
assert.equal(a30SourceLock.native_export.standalone_full_raw_replay_claimed, false);
assert.equal(a30SourceLock.indonesian_release.complete_public_edition, true);
assert.equal(a30SourceLock.indonesian_release.final_derivative_revision_proved, false);
assert.equal(a30SourceLock.indonesian_release.zenodo_record_id, 22290180);
assert.equal(a30SourceLock.upstream_source.commit, '789b54099106b071d1d32bfcee454fed72eb4768');
assert.equal(a30SourceLock.upstream_source.tree, '05b39123f698772482c0c33a43fa2d2d4ea562ae');
assert.equal(a30ClaimBoundary.schema, 'a30-claim-boundary/1');
for (const key of ['native_bodies_copied', 'all_exercises_claimed_solved', 'native_course_prerequisites_invented', 'exhaustive_exercise_pdf_destinations_claimed', 'final_derivative_git_revision_claimed', 'indonesian_semantic_html_claimed', 'indonesian_mathml_claimed', 'epub_claimed', 'portable_offline_html_claimed', 'pdf_ua_claimed', 'wcag_conformance_claimed', 'interactive_labs_claimed', 'learning_runtime_claimed', 'official_teacher_manual_claimed', 'standalone_raw_replay_claimed', 'reversible_exchange_claimed', 'public_access_state_changed']) assert.equal(a30ClaimBoundary[key], false, `A30 claim-boundary drift: ${key}`);
for (const key of ['source_segment_text_copied', 'target_segment_text_copied', 'term_source_text_copied', 'term_target_text_copied', 'correction_source_or_target_text_copied', 'exercise_or_problem_bodies_copied', 'solution_bodies_copied', 'learner_result_instances']) assert.equal(a30ClaimBoundary[key], 0, `A30 zero-copy boundary drift: ${key}`);
assert.equal(a30ClaimBoundary.unsupported_exercises_preserved, 3067);
assert.equal(a30ClaimBoundary.central_a20_prerequisite_is_overlay, true);
assert.equal(a30ClaimBoundary.segment_state_asymmetry_preserved, true);
assert.equal(docsBytes['backend/a30/data/chapter-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 12);
assert.equal(docsBytes['backend/a30/data/module-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 87);
assert.equal(docsBytes['backend/a30/data/exercise-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 7250);
assert.equal(docsBytes['backend/a30/data/concept-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 497);
assert.equal(docsBytes['backend/a30/data/pedagogical-relation-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 37974);
assert.equal(docsBytes['backend/a30/data/rights-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 1875);
assert.equal(docsBytes['backend/a30/data/corrections-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 703);
assert.equal(docsBytes['backend/a30/data/terms-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 513);
const a30PublicMappings = [
  ['views/A30.html', 'backend/a30/A30.html'],
  ['views/A30-pengajar.html', 'backend/a30/A30-pengajar.html'],
  ['views/capabilities.json', 'backend/a30/capabilities.json'],
  ['data/learner-map.json', 'backend/a30/learning-map.json'],
  ['data/educator-map.json', 'backend/a30/educator-map.json'],
  ['data/public-evidence.json', 'backend/a30/public-evidence.json'],
  ['data/claim-boundary.json', 'backend/a30/claim-boundary.json'],
  ['data/native-record-ledger.json', 'backend/a30/data/native-record-ledger.json'],
  ['data/chapter-index.jsonl', 'backend/a30/data/chapter-index.jsonl'],
  ['data/module-index.jsonl', 'backend/a30/data/module-index.jsonl'],
  ['data/exercise-index.jsonl', 'backend/a30/data/exercise-index.jsonl'],
  ['data/concept-index.jsonl', 'backend/a30/data/concept-index.jsonl'],
  ['data/pedagogical-relation-index.jsonl', 'backend/a30/data/pedagogical-relation-index.jsonl'],
  ['data/terms-index.jsonl', 'backend/a30/data/terms-index.jsonl'],
  ['data/corrections-index.jsonl', 'backend/a30/data/corrections-index.jsonl'],
  ['data/rights-index.jsonl', 'backend/a30/data/rights-index.jsonl'],
  ['data/segment-state-summary.json', 'backend/a30/data/segment-state-summary.json'],
  ['input/source-lock.json', 'backend/a30/source-lock.json'],
  ['input/public-native-readback.json', 'backend/a30/public-native-readback.json'],
  ['validation.json', 'backend/a30/validation.json'],
];
for (const [adapterPath, publicPath] of a30PublicMappings) {
  const expected = a30AdapterManifest.outputs.find(({ path }) => path === adapterPath);
  if (adapterPath !== 'validation.json') assert.ok(expected, `A30 adapter manifest does not bind ${adapterPath}.`);
  const sealedBytes = await readFile(resolve(project, 'backend/course-capsule-v1/adapters/a30-capability-v1', adapterPath));
  let adapterBytes = sealedBytes;
  if (adapterPath === 'views/A30-pengajar.html') adapterBytes = Buffer.from(sealedBytes.toString('utf8').replaceAll('../data/', 'data/'), 'utf8');
  const expectedSource = { path: 'docs/' + publicPath, bytes: adapterBytes.length, sha256: sha256(adapterBytes) };
  const observedHosted = identity('docs/' + publicPath, docsBytes[publicPath]);
  if (adapterPath === 'views/A30.html' || adapterPath === 'views/A30-pengajar.html') {
    const overlay = centralNavigationOverlay.files.find(({ document }) => document === 'docs/' + publicPath);
    assert.ok(overlay, `${publicPath}: hosted navigation overlay is missing.`);
    assert.deepEqual(overlay.source_body, expectedSource, `${publicPath}: navigation overlay does not bind the sealed adapter source body.`);
    assert.deepEqual(overlay.hosted_surface, observedHosted, `${publicPath}: hosted navigation-overlay identity drift.`);
    assert.equal(overlay.source_body_replay_exact, true);
    assert.deepEqual(overlay.placements, ['top', 'bottom']);
    assert.equal(overlay.program_root_return_links_per_placement, 2);
    assert.equal(overlay.course_card_return_links_per_placement, 2);
    assert.equal(overlay.authoritative_original_links_per_placement, 1);
  } else {
    assert.deepEqual(observedHosted, expectedSource, `${publicPath}: public A30 byte identity differs from the sealed adapter.`);
  }
  if (expected) assert.equal(expected.bytes, sealedBytes.length, `${adapterPath}: A30 sealed output byte drift.`);
}
assert.deepEqual(docsBytes['backend/a30/validation.json'], a30AdapterValidationBytes, 'Public A30 validation receipt differs from the sealed adapter.');
for (const a30Page of [docsBytes['backend/a30/A30.html'].toString('utf8'), docsBytes['backend/a30/A30-pengajar.html'].toString('utf8')]) {
  assert.match(a30Page, /<html lang="id">/);
  assert.match(a30Page, /https:\/\/zenodo\.org\/records\/22290180/);
  assert.doesNotMatch(a30Page, /<script\b/i);
}
const d30 = rows.find(({ course_id }) => course_id === 'D30');
assert.equal(d30.course.state, 'published');
assert.equal(d30.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(d30.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(d30.layers.learner.tools.map(({ tool_id, href }) => ({ tool_id, href })), [
  { tool_id: 'd30.open_learner_hub', href: 'backend/d30/D30.html' },
]);
assert.equal(d30.layers.learner.tools[0].page.path, 'docs/backend/d30/D30.html');
assert.equal(d30.layers.learner.tools[0].resource.path, 'docs/backend/d30/learning-map.json');
assert.equal(d30.layers.learner.tools[0].evidence.path, 'docs/backend/d30/validation.json');
assert.equal(d30.layers.curriculum.unit_identity_status, 'verified');
assert.equal(d30.layers.translation.ledger_status, 'verified');
assert.equal(d30.layers.translation.terminology_status, 'verified');
assert.equal(d30.layers.translation.rights_status, 'verified');
assert.equal(d30.layers.translation.corrections_status, 'verified');
assert.equal(d30.layers.production.build_status, 'verified');
assert.equal(d30.layers.production.deterministic_replay_status, 'verified');
assert.equal(d30.layers.educator.status, 'verified');
assert.equal(d30.layers.educator.unit_alignment_status, 'verified');
assert.deepEqual(d30.layers.educator.resources.map(({ id, status }) => ({ id, status })), [
  { id: 'D30:native-educator-observation', status: 'available_unverified' },
  { id: 'D30:educator-hub-v1', status: 'verified' },
  { id: 'D30:educator-map-v1', status: 'verified' },
  { id: 'D30:terms-index-v1', status: 'verified' },
  { id: 'D30:rights-index-v1', status: 'verified' },
  { id: 'D30:corrections-index-v1', status: 'verified' },
  { id: 'D30:relations-index-v1', status: 'verified' },
]);
assert.equal(d30.layers.educator.resources[0].url, 'https://zenodo.org/records/22182655');
assert.equal(d30.layers.learner.primary.url, 'https://kokunoyumeto.github.io/measure-theoretic-probability-stochastic-processes-id/');
assert.equal(d30.layers.learner.pdf.sha256, 'dda34267df928672e03e04b4c8a36d768aab2d33bc1194b269074da0d2d24e40');
assert.equal(d30.layers.learner.portable_html.sha256, 'e32dba5a896fb847192bbe944e7fd3db4d95f61ee57e33751bbff3108fca214a');
assert.equal(d30.layers.learner.capabilities.semantic_html, 'verified');
assert.equal(d30.layers.learner.capabilities.mathml, 'available_unverified');
assert.equal(d30AdapterManifest.course_id, 'D30');
assert.equal(d30AdapterManifest.contract, 'course-learning-capability/1');
assert.equal(d30AdapterManifest.zero_copy, true);
assert.equal(d30AdapterManifest.native_bodies_copied, false);
assert.equal(d30AdapterManifest.component_rights_preserved, true);
assert.equal(d30AdapterManifest.public_state_changed, false);
const d30PublicMappings = [
  ['views/D30.html', 'backend/d30/D30.html'],
  ['views/D30-pengajar.html', 'backend/d30/D30-pengajar.html'],
  ['data/capabilities.json', 'backend/d30/capabilities.json'],
  ['data/learning-map.json', 'backend/d30/learning-map.json'],
  ['data/learner-map.json', 'backend/d30/learner-map.json'],
  ['data/educator-map.json', 'backend/d30/educator-map.json'],
  ['data/public-evidence.json', 'backend/d30/public-evidence.json'],
  ['data/claim-boundary.json', 'backend/d30/claim-boundary.json'],
  ['data/rights-index.jsonl', 'backend/d30/data/rights-index.jsonl'],
  ['data/corrections-index.jsonl', 'backend/d30/data/corrections-index.jsonl'],
  ['data/terms-index.jsonl', 'backend/d30/data/terms-index.jsonl'],
  ['data/relations-index.jsonl', 'backend/d30/data/relations-index.jsonl'],
];
for (const [adapterPath, publicPath] of d30PublicMappings) {
  const expected = d30AdapterManifest.outputs.find(({ path }) => path === adapterPath);
  assert.ok(expected, `D30 adapter manifest does not bind ${adapterPath}.`);
  const expectedSource = { path: 'docs/' + publicPath, bytes: expected.bytes, sha256: expected.sha256 };
  const observedHosted = identity('docs/' + publicPath, docsBytes[publicPath]);
  if (adapterPath.startsWith('views/')) {
    const overlay = centralNavigationOverlay.files.find(({ document }) => document === 'docs/' + publicPath);
    assert.ok(overlay, `${publicPath}: hosted navigation overlay is missing.`);
    assert.deepEqual(overlay.source_body, expectedSource, `${publicPath}: navigation overlay does not bind the sealed adapter source body.`);
    assert.deepEqual(overlay.hosted_surface, observedHosted, `${publicPath}: hosted navigation-overlay identity drift.`);
    assert.equal(overlay.source_body_replay_exact, true);
    assert.deepEqual(overlay.placements, ['top', 'bottom']);
    assert.equal(overlay.program_root_return_links_per_placement, 2);
    assert.equal(overlay.course_card_return_links_per_placement, 2);
    assert.equal(overlay.authoritative_original_links_per_placement, 3);
  } else {
    assert.deepEqual(observedHosted, expectedSource, `${publicPath}: public D30 byte identity differs from the sealed adapter.`);
  }
}
assert.deepEqual(docsBytes['backend/d30/validation.json'], d30AdapterValidationBytes, 'Public D30 validation receipt differs from the sealed adapter.');
assert.equal(d30Validation.result, 'PASS');
assert.equal(Object.values(d30Validation.checks).every(Boolean), true);
assert.equal(d30Validation.counts.entities, 2538);
assert.equal(d30Validation.counts.segments, 6333);
assert.equal(d30Validation.counts.relations, 3256);
assert.equal(d30Validation.counts.high_level_units, 57);
assert.equal(d30Validation.counts.exercise_surfaces, 122);
assert.equal(d30Validation.counts.prerequisite_routes, 142);
assert.equal(d30Validation.counts.labs, 5);
assert.equal(d30Validation.counts.mastery_problems, 36);
assert.equal(d30Validation.counts.assessment_forms, 2);
assert.equal(d30Validation.negative_fixtures.length, 6);
assert.equal(d30LearningMap.units.length, 57);
assert.equal(d30LearningMap.labs.length, 5);
assert.equal(d30LearningMap.prerequisite_routes.length, 142);
assert.equal(d30LearningMap.artifacts.length, 6);
assert.equal(d30LearningMap.sources.length, 42);
assert.equal(d30LearnerMap.units.length, 57);
assert.equal(d30EducatorMap.units.length, 57);
assert.equal(d30EducatorMap.assessment.forms, 2);
assert.equal(d30EducatorMap.assessment.common_outcomes, 26);
assert.equal(d30Capabilities.counts.terms, 249);
assert.equal(d30Capabilities.counts.corrections, 489);
assert.equal(d30Capabilities.rights.component_specific, true);
assert.equal(d30Capabilities.rights.blanket_license_claimed, false);
assert.equal(d30PublicEvidence.record_id, 22182655);
assert.equal(d30PublicEvidence.content_commit, 'd0111bc20dc813f5fde12eb715be4cf6dd5a94bd');
assert.equal(d30PublicEvidence.content_tree, '4bc91cba4fad7cbfbd284267be3d07cafb36251e');
assert.equal(d30PublicEvidence.files.length, 6);
assert.equal(d30PublicEvidence.all_public_sha256_exact, true);
assert.ok(d30ClaimBoundary.not_claimed.includes('copied native bodies'));
assert.equal(docsBytes['backend/d30/data/rights-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 42);
assert.equal(docsBytes['backend/d30/data/corrections-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 489);
assert.equal(docsBytes['backend/d30/data/terms-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 249);
assert.equal(docsBytes['backend/d30/data/relations-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 3256);
for (const d30Page of [d30Html, d30EducatorHtml]) {
  assert.match(d30Page, /<html lang="id">/);
  assert.match(d30Page, /href="\/en\/"/);
  assert.match(d30Page, /href="\/id\/"/);
  assert.match(d30Page, /https:\/\/kokunoyumeto\.github\.io\/measure-theoretic-probability-stochastic-processes-id\//);
  assert.match(d30Page, /https:\/\/github\.com\/KokunoYumeto\/measure-theoretic-probability-stochastic-processes-id\/tree\/d0111bc20dc813f5fde12eb715be4cf6dd5a94bd/);
  assert.match(d30Page, /https:\/\/zenodo\.org\/records\/22182655/);
  assert.match(d30Page, /https:\/\/www\.randomservices\.org\/random\//);
  assert.match(d30Page, /https:\/\/continuous-time-mcs\.quantecon\.org\//);
  assert.match(d30Page, /https:\/\/gordanz\.github\.io\/stochastic-book\//);
  assert.doesNotMatch(d30Page, /<script\b/i);
}
const d40 = rows.find(({ course_id }) => course_id === 'D40');
assert.equal(d40.course.state, 'published');
assert.equal(d40.course_native.repository, undefined);
assert.equal(d40.course_native.zenodo, 'https://doi.org/10.5281/zenodo.22184259');
assert.equal(d40.layers.learner.pdf.sha256, 'c4e4f470eeb096129e7bf7306422d316c93aaeed99d2b12890e08f15777ac13f');
assert.equal(d40.layers.learner.portable_html.sha256, 'a370bba5ddb54081387a484a304b24af92691c3bc167db964c486625a79add59');
assert.equal(d40.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(d40.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.equal(d40.layers.learner.tools.length, 1);
assert.equal(d40.layers.educator.resources.length, 2);
assert.deepEqual(d40.layers.educator.resources.map(({ id, status }) => ({ id, status })), [
  { id: 'D40:native-educator-observation', status: 'available_unverified' },
  { id: 'D40:educator-hub-v1', status: 'verified' },
]);
const d70 = rows.find(({ course_id }) => course_id === 'D70');
assert.equal(d70.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(d70.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(d70.layers.learner.tools.map(({ tool_id, href }) => ({ tool_id, href })), [
  { tool_id: 'd70.open_learner_hub', href: 'backend/d70/D70.html' },
]);
assert.equal(d70.layers.production.build_status, 'available_unverified');
assert.equal(d70.layers.production.deterministic_replay_status, 'available_unverified');
assert.deepEqual(d70.layers.educator.resources.map(({ id, status }) => ({ id, status })), [
  { id: 'D70:native-educator-observation', status: 'available_unverified' },
  { id: 'D70:educator-hub-v1', status: 'verified' },
]);
const d10 = rows.find(({ course_id }) => course_id === 'D10');
assert.equal(d10.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(d10.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(d10.layers.learner.tools.map(({ tool_id, href }) => ({ tool_id, href })), [
  { tool_id: 'd10.open_learner_hub', href: 'backend/d10/D10.html' },
]);
assert.equal(d10.layers.curriculum.unit_identity_status, 'verified');
assert.equal(d10.layers.translation.ledger_status, 'verified');
assert.equal(d10.layers.translation.terminology_status, 'verified');
assert.equal(d10.layers.translation.rights_status, 'verified');
assert.equal(d10.layers.translation.corrections_status, 'verified');
assert.equal(d10.layers.production.build_status, 'verified');
assert.equal(d10.layers.production.deterministic_replay_status, 'verified');
assert.equal(d10.layers.educator.unit_alignment_status, 'verified');
assert.deepEqual(d10.layers.educator.resources.map(({ id, status }) => ({ id, status })), [
  { id: 'D10:educator-hub-v1', status: 'verified' },
  { id: 'D10:educator-map-v1', status: 'verified' },
]);
assert.equal(d10LearningMap.units.length, 94);
assert.equal(d10LearningMap.units.flatMap(({ exercise_ids }) => exercise_ids).length, 1096);
assert.equal(d10LearningMap.supplemental_reader_surfaces.length, 4);
assert.equal(d10EducatorMap.selector.selected_units.length, 94);
assert.equal(d10EducatorMap.selector.selected_units.flatMap(({ exercise_ids }) => exercise_ids).length, 1096);
assert.equal(d10EducatorMap.claim_boundary.complete_solution_layer_available, false);
assert.equal(d10RightsAndTerms.terminology.data_row_count, 132);
assert.equal(d10RightsAndTerms.corrections.length, 420);
assert.equal(d10RightsAndTerms.blanket_license_claimed, false);
assert.equal(d10LedgerReferences.source_target_unit_hashes.length, 94);
assert.equal(d10Validation.state, 'pass');
assert.equal(d10Validation.counts.units, 94);
assert.equal(d10Validation.counts.typed_exercises, 1096);
assert.equal(d10Validation.counts.explicit_hints, 276);
assert.equal(d10Validation.negative_fixtures.length, 22);
const d120 = rows.find(({ course_id }) => course_id === 'D120');
assert.equal(d120.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(d120.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(d120.layers.learner.tools.map(({ tool_id, href }) => ({ tool_id, href })), [
  { tool_id: 'd120.open_learner_hub', href: 'backend/d120/D120.html' },
]);
assert.equal(d120.layers.curriculum.unit_identity_status, 'verified');
assert.equal(d120.layers.translation.ledger_status, 'not_applicable');
assert.equal(d120.layers.translation.terminology_status, 'verified');
assert.equal(d120.layers.translation.rights_status, 'verified');
assert.equal(d120.layers.translation.corrections_status, 'verified');
assert.equal(d120.layers.production.build_status, 'verified');
assert.equal(d120.layers.production.deterministic_replay_status, 'verified');
assert.equal(d120.layers.educator.unit_alignment_status, 'verified');
assert.deepEqual(d120.layers.educator.resources.map(({ id, status }) => ({ id, status })), [
  { id: 'D120:native-delivery-wrapper', status: 'verified' },
  { id: 'D120:educator-hub-v1', status: 'verified' },
]);
assert.equal(d120LearningMap.units.length, 9);
assert.equal(d120LearningMap.units.flatMap(({ outcomes }) => outcomes).length, 71);
assert.equal(d120LearningMap.units.flatMap(({ practice }) => practice).length, 54);
assert.equal(d120EducatorMap.assessments.length, 14);
assert.equal(d120EducatorMap.assessments.flatMap(({ rubric }) => rubric.criteria).length, 79);
assert.equal(d120Validation.counts.learner_attempt_instances ?? 0, 0);
assert.equal(d120Validation.counts.learner_submission_instances ?? 0, 0);
assert.equal(d120Validation.counts.learner_result_instances ?? 0, 0);
assert.equal(d120Validation.counts.credential_assertion_instances ?? 0, 0);
const c120 = rows.find(({ course_id }) => course_id === 'C120');
assert.equal(c120.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(c120.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(c120.layers.learner.tools.map(({ tool_id, href }) => ({ tool_id, href })), [
  { tool_id: 'c120.open_learner_hub', href: 'backend/c120/C120.html' },
]);
assert.equal(c120.layers.curriculum.unit_identity_status, 'verified');
assert.equal(c120.layers.translation.ledger_status, 'verified');
assert.equal(c120.layers.translation.terminology_status, 'verified');
assert.equal(c120.layers.translation.rights_status, 'verified');
assert.equal(c120.layers.translation.corrections_status, 'verified');
assert.equal(c120.layers.production.build_status, 'verified');
assert.equal(c120.layers.production.deterministic_replay_status, 'verified');
assert.equal(c120.layers.educator.unit_alignment_status, 'verified');
assert.deepEqual(c120.layers.educator.resources.map(({ id, status }) => ({ id, status })), [
  { id: 'C120:educator-hub-v1', status: 'verified' },
  { id: 'C120:educator-map-v1', status: 'verified' },
]);
assert.equal(c120LearningMap.units.length, 26);
assert.equal(c120LearningMap.units.filter(({ origin_kind }) => origin_kind === 'source_derived_translation').length, 22);
assert.equal(c120LearningMap.units.filter(({ origin_kind }) => origin_kind === 'independent_supplement').length, 4);
assert.equal(c120LearningMap.units.flatMap(({ problem_ids }) => problem_ids).length, 141);
assert.equal(c120EducatorMap.selector.projects.length, 12);
assert.equal(c120EducatorMap.claim_boundary.worked_solution_records, 126);
assert.equal(c120EducatorMap.claim_boundary.qualitative_rubrics, 14);
assert.equal(c120EducatorMap.claim_boundary.worked_classifications, 1);
assert.equal(c120RightsAndTerms.terminology.length, 321);
assert.equal(c120RightsAndTerms.corrections.length, 160);
assert.equal(c120RightsAndTerms.blanket_license_claimed, false);
assert.equal(c120LedgerReferences.backend_integrity.files, 81);
assert.equal(c120LedgerReferences.common_projection.record_count, 16029);
assert.equal(c120Validation.counts.native_records, 4941);
assert.equal(c120Validation.counts.common_virtual_records, 16029);
assert.equal(c120Validation.negative_fixtures.length, 25);
const c110 = rows.find(({ course_id }) => course_id === 'C110');
assert.equal(c110.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(c110.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(c110.layers.learner.tools.map(({ tool_id, href }) => ({ tool_id, href })), [
  { tool_id: 'c110.open_learner_hub', href: 'backend/c110/C110.html' },
]);
assert.equal(c110.layers.curriculum.unit_identity_status, 'verified');
assert.equal(c110.layers.translation.ledger_status, 'verified');
assert.equal(c110.layers.translation.terminology_status, 'verified');
assert.equal(c110.layers.translation.rights_status, 'verified');
assert.equal(c110.layers.translation.corrections_status, 'verified');
assert.equal(c110.layers.production.build_status, 'verified');
assert.equal(c110.layers.production.deterministic_replay_status, 'verified');
assert.equal(c110.layers.educator.unit_alignment_status, 'verified');
assert.deepEqual(c110.layers.educator.resources.map(({ id, status }) => ({ id, status })), [
  { id: 'C110:educator-hub-v1', status: 'verified' },
  { id: 'C110:educator-map-v1', status: 'verified' },
  { id: 'C110:alignment-index-v1', status: 'verified' },
]);
assert.equal(c110LearningMap.modules.length, 29);
assert.equal(c110LearningMap.units.length, 281);
assert.equal(c110LearningMap.experiments.length, 2);
assert.equal(c110EducatorMap.counts.alignments, 4621);
assert.equal(c110EducatorMap.claim_boundary.exercise_solution_joins_inferred, false);
assert.equal(c110EducatorMap.claim_boundary.native_exercise_entity_records, 0);
assert.equal(c110Alignments.alignment_count, 4621);
assert.equal(c110Alignments.alignments.length, 4621);
assert.equal(c110Alignments.body_content_embedded, false);
assert.equal(c110RightsAndTerms.terminology.length, 593);
assert.equal(c110RightsAndTerms.corrections.length, 325);
assert.equal(c110RightsAndTerms.blanket_license_claimed, false);
assert.equal(c110LedgerReferences.source_files.length, 31);
assert.equal(c110LedgerReferences.common_projection.record_count, 53055);
assert.equal(c110Validation.counts.native_records, 28172);
assert.equal(c110Validation.counts.common_virtual_records, 53055);
assert.equal(c110Validation.negative_fixtures.length, 26);
const c70 = rows.find(({ course_id }) => course_id === 'C70');
assert.equal(c70.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(c70.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(c70.layers.learner.tools.map(({ tool_id, href }) => ({ tool_id, href })), [
  { tool_id: 'c70.open_learner_hub', href: 'backend/c70/C70.html' },
]);
assert.equal(c70.layers.curriculum.unit_identity_status, 'verified');
assert.equal(c70.layers.translation.ledger_status, 'verified');
assert.equal(c70.layers.translation.terminology_status, 'verified');
assert.equal(c70.layers.translation.rights_status, 'verified');
assert.equal(c70.layers.translation.corrections_status, 'verified');
assert.equal(c70.layers.production.build_status, 'verified');
assert.equal(c70.layers.production.deterministic_replay_status, 'verified');
assert.equal(c70.layers.educator.unit_alignment_status, 'verified');
assert.deepEqual(c70.layers.educator.resources.map(({ id, status }) => ({ id, status })), [
  { id: 'C70:educator-hub-v1', status: 'verified' },
  { id: 'C70:educator-map-v1', status: 'verified' },
  { id: 'C70:concept-index-v1', status: 'verified' },
  { id: 'C70:relation-index-v1', status: 'verified' },
]);
assert.equal(c70LearningMap.blocks.length, 19);
assert.equal(c70LearningMap.route.all_unit_ids.length, 1408);
assert.equal(c70EducatorMap.selector.units.length, 1408);
assert.equal(c70EducatorMap.selector.exercise_support.length, 82);
assert.equal(c70ConceptIndex.concepts.length, 701);
assert.equal(c70RelationIndex.relations.length, 6334);
assert.equal(c70RelationIndex.specialized_projection_duplicate_rows_materialized, 0);
assert.equal(c70RightsAndTerms.terminology.length, 633);
assert.equal(c70RightsAndTerms.corrections.length, 354);
assert.equal(c70RightsAndTerms.blanket_license_claimed, false);
assert.equal(c70LedgerReferences.common_projection.exact_reverse_extraction, 19048);
assert.equal(c70LedgerReferences.common_projection.record_count, 19049);
assert.equal(c70PublicEvidence.zenodo.all_records_open, true);
assert.equal(c70Validation.counts.units, 1408);
assert.equal(c70Validation.counts.explicit_support_relations, 82);
assert.equal(c70Validation.negative_fixtures.length, 32);
const b40 = rows.find(({ course_id }) => course_id === 'B40');
assert.equal(b40.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(b40.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(b40.layers.learner.tools.map(({ tool_id, href }) => ({ tool_id, href })), [
  { tool_id: 'b40.open_learner_hub', href: 'backend/b40/B40.html' },
]);
assert.equal(b40.layers.curriculum.unit_identity_status, 'verified');
assert.equal(b40.layers.translation.ledger_status, 'verified');
assert.equal(b40.layers.translation.terminology_status, 'verified');
assert.equal(b40.layers.translation.rights_status, 'verified');
assert.equal(b40.layers.translation.corrections_status, 'verified');
assert.equal(b40.layers.production.build_status, 'verified');
assert.equal(b40.layers.production.deterministic_replay_status, 'verified');
assert.equal(b40.layers.educator.unit_alignment_status, 'verified');
assert.equal(b40.layers.educator.resources.length, 6);
assert.ok(b40.layers.educator.resources.some(({ id, status }) => id === 'B40:educator-hub-v1' && status === 'verified'));
assert.ok(b40.layers.educator.resources.some(({ id, status }) => id === 'B40:educator-map-v1' && status === 'verified'));
assert.equal(b40.layers.learner.pdf.status, 'verified');
assert.equal(b40.layers.learner.pdf.sha256, '0462ddc8ffcc901efbc81205f79a249ae716e838a6ec32eda033444a90b8755e');
assert.equal(b40.layers.learner.online_html.scope, 'release_landing_page_not_full_html_textbook');
assert.equal(b40.layers.learner.capabilities.semantic_html, 'not_yet_produced');
assert.equal(b40.layers.learner.capabilities.mathml, 'not_yet_produced');
assert.equal(b40LearningMap.components.length, 3);
assert.equal(b40LearningMap.route.all_unit_ids.length, 3541);
assert.equal(b40EducatorMap.selector.units.length, 3541);
assert.equal(b40EducatorMap.selector.exercise_answers.length, 1037);
assert.equal(b40EducatorMap.answer_provenance.native_upstream_answer_count, 1035);
assert.equal(b40EducatorMap.answer_provenance.indonesian_edition_supplied_answer_count, 2);
assert.equal(b40ConceptIndex.concepts.length, 114);
assert.equal(b40RelationIndex.relations.length, 13999);
assert.equal(b40RelationIndex.exercise_answer_projection_rows, 1037);
assert.equal(b40RelationIndex.specialized_projection_duplicate_rows_materialized, 0);
assert.equal(b40RightsAndTerms.component_rights.length, 11);
assert.equal(b40ConceptIndex.term_count, 114);
assert.equal(b40LedgerReferences.corrections.length, 307);
assert.deepEqual(b40RightsAndTerms.terminology_reference, {
  canonical_adapter_path: 'data/concept-index.json',
  public_documentation_path: 'docs/backend/b40/concept-index.json',
  schema: 'b40-concept-index/1',
  term_count: 114,
});
assert.deepEqual(b40RightsAndTerms.corrections_reference, {
  canonical_adapter_path: 'data/ledger-references.json',
  correction_count: 307,
  public_documentation_path: 'docs/backend/b40/ledger-references.json',
  schema: 'b40-ledger-references/1',
});
assert.equal(b40RightsAndTerms.redundant_terminology_rows_materialized, 0);
assert.equal(b40RightsAndTerms.redundant_correction_rows_materialized, 0);
assert.equal(b40RightsAndTerms.blanket_license_claimed, false);
assert.equal(b40LedgerReferences.common_projection.exact_reverse_extraction, 22131);
assert.equal(b40LedgerReferences.common_projection.virtual_records_materialized, false);
assert.equal(b40PublicEvidence.reader.scope, 'release_landing_page_not_full_html_textbook');
assert.equal(b40PublicEvidence.zenodo.access_right, 'open');
assert.equal(b40PublicEvidence.native_semantic_html_claimed, false);
assert.equal(b40PublicEvidence.mathml_claimed, false);
assert.equal(b40Validation.counts.units, 3541);
assert.equal(b40Validation.counts.relations, 13999);
assert.equal(b40Validation.negative_fixtures.length, 62);
assert.equal(b40Manifest.validation_path, 'validation.json');
assert.deepEqual(b40Validation.public_documentation, b40Manifest.public_documentation);
assert.equal(b40Manifest.public_documentation.manifest_path, 'docs/backend/b40/manifest.json');
assert.equal(b40Manifest.public_documentation.validation_path, 'docs/backend/b40/validation.json');
assert.equal(b40Validation.manifest.path, 'manifest.json');
assert.equal(b40Validation.manifest.bytes, docsBytes['backend/b40/manifest.json'].length);
assert.equal(b40Validation.manifest.sha256, sha256(docsBytes['backend/b40/manifest.json']));
const b20 = rows.find(({ course_id }) => course_id === 'B20');
const b50 = rows.find(({ course_id }) => course_id === 'B50');
const c100 = rows.find(({ course_id }) => course_id === 'C100');
const c60 = rows.find(({ course_id }) => course_id === 'C60');
const d20 = rows.find(({ course_id }) => course_id === 'D20');
const d90 = rows.find(({ course_id }) => course_id === 'D90');
assert.match(b20.layers.learner.primary.url, /records\/22183943\//);
assert.match(b50.layers.learner.primary.url, /records\/22184443\//);
assert.equal(c100.layers.learner.primary.format, 'text/html');
assert.equal(d20.layers.learner.primary.format, 'text/html');
assert.equal(c60.layers.learner.primary.format, 'text/html');
assert.equal(c60.layers.learner.online_html.status, 'verified');
assert.equal(c60.layers.learner.online_html.inventory_count, 10);
assert.equal(c60.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(c60.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(c60.layers.learner.tools.map(({ tool_id, href }) => ({ tool_id, href })), [
  { tool_id: 'c60.open_learner_hub', href: 'backend/c60/C60.html' },
]);
assert.equal(c60.layers.curriculum.unit_identity_status, 'verified');
assert.equal(c60.layers.translation.ledger_status, 'verified');
assert.equal(c60.layers.translation.terminology_status, 'verified');
assert.equal(c60.layers.translation.rights_status, 'verified');
assert.equal(c60.layers.translation.corrections_status, 'verified');
assert.equal(c60.layers.production.build_status, 'verified');
assert.equal(c60.layers.production.deterministic_replay_status, 'verified');
assert.equal(c60.layers.educator.status, 'verified');
assert.equal(c60.layers.educator.unit_alignment_status, 'verified');
assert.equal(c60.layers.educator.resources.length, 7);
assert.ok(c60.layers.educator.resources.some(({ id, status }) => id === 'C60:educator-hub-v1' && status === 'verified'));
assert.ok(c60.layers.educator.resources.some(({ id, status }) => id === 'C60:native-id-index-v1' && status === 'verified'));
assert.equal(c60.layers.learner.pdf.status, 'verified');
assert.equal(c60.layers.learner.pdf.bytes, 962527);
assert.equal(c60.layers.learner.pdf.sha256, '1ded3c6844b656347259b464bf21526fdc32dc2246c73ac58ab76ed28688eefc');
assert.equal(c60.layers.learner.epub.status, 'not_yet_produced');
assert.equal(c60.layers.learner.portable_html.status, 'not_yet_produced');
assert.equal(c60.layers.learner.capabilities.semantic_html, 'verified');
assert.equal(c60.layers.learner.capabilities.mathml, 'verified');
assert.equal(c60.layers.learner.capabilities.print_profile, 'verified');
assert.equal(c60Validation.state, 'pass');
assert.equal(c60Validation.counts.native_records, 5272);
assert.equal(c60Validation.counts.native_unique_ids, 5272);
assert.equal(c60Validation.counts.units, 548);
assert.equal(c60Validation.counts.concepts, 223);
assert.equal(c60Validation.counts.relations, 3297);
assert.equal(c60Validation.counts.native_exercise_units, 101);
assert.equal(c60Validation.negative_fixtures.length, 41);
assert.equal(c60Validation.migration_receipt_replay_checks, 18);
assert.equal(c60Validation.isolated_two_build_byte_identity.byte_identical, true);
assert.equal(c60Manifest.counts.native_records, c60Validation.counts.native_records);
assert.equal(c60Capabilities.counts.common_virtual_records, 6967);
assert.equal(c60LearningMap.units.length, 5);
assert.equal(c60EducatorMap.selector.units.length, 548);
assert.equal(c60EducatorMap.chapter_routes.length, 5);
assert.equal(c60EducatorMap.section_routes.length, 27);
assert.equal(c60ConceptIndex.concepts.length, 223);
assert.equal(c60RelationIndex.relations.length, 3297);
assert.equal(c60RelationIndex.derived_relations_invented, 0);
assert.equal(c60RightsAndTerms.component_rights.length, 15);
assert.equal(c60RightsAndTerms.terminology.length, 239);
assert.equal(c60RightsAndTerms.corrections.length, 141);
assert.equal(c60RightsAndTerms.blanket_license_claimed, false);
assert.equal(c60LedgerReferences.independent_receipt_replay.state, 'pass');
assert.equal(c60LedgerReferences.common_projection.exact_reverse_extraction, 5272);
assert.equal(c60NativeIdIndex.records.length, 5272);
assert.equal(c60PublicEvidence.github.current_public_head, '66df945d1e5281bfc4758b733c13ac9254f00410');
assert.equal(c60PublicEvidence.reader.mathml_elements_observed, 2791);
assert.equal(c60PublicEvidence.reader.pdf_pages, 138);
assert.equal(c60ClaimBoundary.native_bodies_copied, false);
assert.equal(c60ClaimBoundary.exercise_bodies_copied, false);
assert.equal(c60ClaimBoundary.public_state_changed, false);
assert.equal(d90.layers.learner.primary.format, 'application/pdf');
assert.equal(d90.layers.learner.online_html.status, 'available_unverified');
assert.equal(d90.layers.learner.online_html.url, 'https://kokunoyumeto.github.io/program-matematika-indonesia/readers/d90/original-02/');
assert.equal(d90.layers.learner.online_html.format, 'text/html');
assert.equal(d90.layers.learner.online_html.entry_point, 'index.html');
assert.equal(d90.layers.learner.online_html.scope, 'other');
assert.equal(d90.layers.learner.online_html.inventory_count, 1);
assert.equal(d90.layers.learner.online_html.bytes, 190680);
assert.equal(d90.layers.learner.online_html.sha256, 'd867f4551cf05e531cc6f53336a55b9ba3ee0dfffbc4acede425e1bceae82a24');
assert.equal(d90.layers.interoperability.semantic_adapter.status, 'verified');
assert.equal(d90.layers.interoperability.semantic_adapter.contract_version, 'course-learning-capability/1');
assert.deepEqual(d90.layers.learner.tools.map(({ tool_id, href }) => ({ tool_id, href })), [
  { tool_id: 'd90.open_learner_hub', href: 'backend/d90/D90.html' },
]);
assert.equal(d90.layers.curriculum.unit_identity_status, 'verified');
assert.equal(d90.layers.translation.ledger_status, 'verified');
assert.equal(d90.layers.translation.terminology_status, 'verified');
assert.equal(d90.layers.translation.rights_status, 'verified');
assert.equal(d90.layers.translation.corrections_status, 'verified');
assert.equal(d90.layers.production.build_status, 'verified');
assert.equal(d90.layers.production.deterministic_replay_status, 'verified');
assert.equal(d90.layers.educator.status, 'verified');
assert.equal(d90.layers.educator.unit_alignment_status, 'verified');
assert.equal(d90.layers.educator.resources.length, 6);
assert.ok(d90.layers.educator.resources.some(({ id, status }) => id === 'D90:educator-hub-v1' && status === 'verified'));
assert.ok(d90.layers.educator.resources.some(({ id, status }) => id === 'D90:educator-map-v1' && status === 'verified'));
assert.ok(d90.layers.educator.resources.some(({ id, status }) => id === 'D90:terms-index-v1' && status === 'verified'));
assert.ok(d90.layers.educator.resources.some(({ id, status }) => id === 'D90:rights-index-v1' && status === 'verified'));
assert.ok(d90.layers.educator.resources.some(({ id, status }) => id === 'D90:corrections-index-v1' && status === 'verified'));
assert.equal(d90.layers.learner.pdf.status, 'verified');
assert.equal(d90.layers.learner.pdf.bytes, 1671254);
assert.equal(d90.layers.learner.pdf.sha256, '9deefecf469c9f2aace26bc8ccdedc552debbe9874ae035badaf5cffee0f80e5');
assert.equal(d90.layers.learner.epub.status, 'verified');
assert.equal(d90.layers.learner.epub.bytes, 379901);
assert.equal(d90.layers.learner.epub.sha256, '1bb882a75209adb220de4ee6c6cf92355b5402538c88050e807dc161fa5d9321');
assert.equal(d90.layers.learner.capabilities.semantic_html, 'verified');
assert.equal(d90.layers.learner.capabilities.mathml, 'verified');
assert.equal(d90.layers.learner.capabilities.print_profile, 'verified');
assert.equal(d90Validation.result, 'pass');
assert.equal(d90Validation.counts.native_records, 4877);
assert.equal(d90Validation.counts.original03_surfaces, 438);
assert.equal(d90Validation.counts.staged_relations, 312);
assert.equal(d90Validation.negative_fixtures.length, 13);
assert.equal(d90LearningMap.prompt_chains.length, 54);
assert.equal(d90LearningMap.practice_chains.length, 32);
assert.equal(d90LearningMap.assessment_containers.length, 54);
assert.equal(d90LearningMap.labs.length, 2);
assert.equal(d90LearningMap.capstone.milestones.length, 7);
assert.equal(d90EducatorMap.rubrics.length, 7);
assert.equal(d90Capabilities.counts.component_rights, 93);
assert.equal(d90Capabilities.counts.corrections, 248);
assert.equal(d90Capabilities.counts.terms, 127);
assert.equal(docsBytes['backend/d90/data/rights-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 93);
assert.equal(docsBytes['backend/d90/data/corrections-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 248);
assert.equal(docsBytes['backend/d90/data/terms-index.jsonl'].toString('utf8').trimEnd().split('\n').length, 127);
assert.equal(d90PublicEvidence.accessibility.html.mathml_count, 4535);
assert.equal(d90PublicEvidence.accessibility.epub.mathml_count, 4535);
assert.equal(d90PublicEvidence.accessibility.wcag_conformance_claimed, false);
assert.equal(d90ClaimBoundary.content_bodies_copied, false);
assert.equal(d90ClaimBoundary.reversible_exchange_claimed, false);
assert.equal(d90ClaimBoundary.public_state_changed, false);

assert.deepEqual(judsonValidation.admitted_courses, ['C30', 'C40']);
assert.equal(judsonValidation.state, 'pass');
assert.equal(judsonValidation.native_chapter_joins, 23);
assert.deepEqual(judsonValidation.chapter_counts, { C30: 15, C40: 8 });
assert.equal(judsonValidation.unique_route_ids, 23);
assert.equal(judsonValidation.duplicate_units_created, 0);
assert.equal(judsonValidation.javascript_required, false);
assert.equal(judsonValidation.guessed_descendant_anchors, 0);
assert.equal(judsonValidation.checked_public_package_inputs, 65);
assert.deepEqual(judsonValidation.evidence_document, judsonChapters.evidence_document);
assert.equal(judsonChapters.evidence_document.path, 'route-evidence.json');
assert.equal(judsonChapters.evidence_document.bytes, judsonRouteEvidenceBytes.length);
assert.equal(judsonChapters.evidence_document.sha256, sha256(judsonRouteEvidenceBytes));
assert.equal(judsonChapters.evidence_document.verbatim_copy, true);
assert.equal(judsonRouteEvidence.result, 'offline_routes_verified_live_accessible_not_frozen_byte_identical');
assert.equal(judsonRouteEvidence.summary.canonical_chapter_routes, 23);
assert.equal(judsonChapters.courses.length, 2);
assert.equal(judsonChapters.courses.find(({ course_id }) => course_id === 'C30').chapters.length, 15);
assert.equal(judsonChapters.courses.find(({ course_id }) => course_id === 'C40').chapters.length, 8);
assert.equal((judsonC30Html.match(/data-route-id=/g) ?? []).length, 15);
assert.equal((judsonC40Html.match(/data-route-id=/g) ?? []).length, 8);
assert.doesNotMatch(judsonC30Html + judsonC40Html, /<script\b/i);
assert.match(judsonC30Html, /Keduanya tidak dianggap edisi yang sama/);
assert.match(judsonC40Html, /Keduanya tidak dianggap edisi yang sama/);
assert.equal(v23AdapterIndex.adapters.length, 5);
assert.equal(v23AdapterIndex.summary.proof_roles, 5);
assert.equal(v23AdapterIndex.summary.contract_2_3_1_adapters, 5);
assert.deepEqual(v23AdapterIndex.adapters.map(({ role_id }) => role_id), ['A00', 'B10', 'D20', 'D60', 'D110']);
const adapterPackages = new Set(v23AdapterIndex.adapters.map(({ archive }) => `${archive.bytes}:${archive.sha256}`));
assert.equal(adapterPackages.size, 5);
assert.deepEqual(v23AdapterIndexV2.summary, {
  curriculum_roles: 40,
  distinct_adapter_packages: 8,
  families_without_local_adapter: 25,
  families_without_public_replay_complete_adapter: 25,
  package_deduplicated_canonical_records: 285829,
  pending_adapter_packages: 0,
  pending_role_bindings: 0,
  published_adapter_packages: 8,
  published_role_bindings: 9,
  represented_native_families: 8,
  role_bindings: 9,
  unbound_roles: 31,
});
assert.equal(v23AdapterIndexV2.snapshot.snapshot_id, 'urn:interlanguage:program-matematika-indonesia:v23-adapters:v0.62.14-postpublication:2026-09-01');
assert.equal(v23AdapterIndexV2.snapshot.central_release_version, 'v0.62.14');
assert.equal(v23AdapterIndexV2.snapshot.central_release_record_doi, '10.5281/zenodo.22217240');
assert.equal(v23AdapterIndexV2.snapshot.public_replay_state, 'postpublication_release_assets_readback_complete');
assert.equal(v23AdapterIndexV2.packages.every((row) => row.admission_state === 'published' && row.public_replay_status === 'published_public_asset_readback_verified' && !Object.hasOwn(row, 'planned_release')), true);
const c30Adapter = v23AdapterIndexV2.adapters.find(({ role_id }) => role_id === 'C30');
const c40Adapter = v23AdapterIndexV2.adapters.find(({ role_id }) => role_id === 'C40');
const c80Adapter = v23AdapterIndexV2.adapters.find(({ role_id }) => role_id === 'C80');
const c130Adapter = v23AdapterIndexV2.adapters.find(({ role_id }) => role_id === 'C130');
assert.equal(c30Adapter.adapter_package_id, c40Adapter.adapter_package_id);
assert.notEqual(c80Adapter.adapter_package_id, c30Adapter.adapter_package_id);
assert.equal(c130Adapter.adapter_package_id, 'urn:uuid:a84539b5-455b-5baf-89a4-f4c0336e33ab');
assert.equal(c130Adapter.native_family_id, 'family-20-operations-research');
assert.equal(c130Adapter.learner_runtime_relationship, 'course_link_only_no_adapter_consumption_claim');
assert.equal(c80Adapter.central_learner_projection.path, 'docs/backend/openlogic/C80.html');
for (const adapter of [c30Adapter, c40Adapter, c80Adapter, c130Adapter]) assert.equal(adapter.central_learner_projection.status, 'published');
assert.equal(patternIndexV2.families.length, 33);
assert.equal(patternIndexV2.snapshot.snapshot_id, v23AdapterIndexV2.snapshot.snapshot_id);
assert.equal(featureAdoption.layers.length, 7);
assert.equal(featureAdoption.snapshot_id, v23AdapterIndexV2.snapshot.snapshot_id);
assert.equal(comparisonEvidence.snapshot_id, v23AdapterIndexV2.snapshot.snapshot_id);
assert.equal(snapshotV2Receipt.status, 'pass');
assert.deepEqual(snapshotV2Receipt.summary, v23AdapterIndexV2.summary);
assert.deepEqual(authorityToolsByCourse.C30.map(({ tool_id }) => tool_id), ['judson-c30-chapter-map-v1']);
assert.deepEqual(authorityToolsByCourse.C40.map(({ tool_id }) => tool_id), ['judson-c40-chapter-map-v1']);
assert.deepEqual(authorityToolsByCourse.C80.map(({ tool_id }) => tool_id), ['c80-openlogic-course-map-v1']);
assert.deepEqual(authorityToolsByCourse.C130.map(({ tool_id }) => tool_id), ['c130-operations-research-course-map-v1']);
assert.equal(openLogicValidation.state, 'pass');
assert.equal(openLogicValidation.semantic_counts.native_units, 722);
assert.equal(openLogicValidation.semantic_counts.reader_reachable_units, 642);
assert.equal(openLogicValidation.semantic_counts.retained_non_reader_units, 80);
assert.equal(openLogicValidation.native_html_claimed, false);
assert.equal(openLogicValidation.guessed_descendant_anchors, 0);
assert.equal(openLogicValidation.pdf_is_first_learner_action, true);
assert.equal(openLogicRoute.course_id, 'C80');
assert.equal(openLogicRoute.primary_learner_action.kind, 'linked_pdf');
assert.equal(openLogicRoute.primary_learner_action.pages, 1116);
assert.equal(openLogicRoute.adapter.native_units, 722);
assert.equal(openLogicRoute.adapter.native_html, false);
assert.doesNotMatch(openLogicHtml, /<script\b/i);
assert.equal(c130Validation.state, 'pass');
assert.equal(c130Validation.semantic_counts.canonical_records, 51704);
assert.equal(c130Validation.semantic_counts.units, 1993);
assert.equal(c130Validation.semantic_counts.relations, 9545);
assert.equal(c130Validation.semantic_counts.rights_assignments, 7634);
assert.equal(c130Validation.semantic_counts.identity_crosswalks, 17273);
assert.equal(c130Validation.learner_routes.count, 7);
assert.equal(c130Validation.learner_routes.pages_landing_is_priority_one, true);
assert.equal(c130Validation.learner_routes.linked_pdf_is_only_primary_reader, true);
assert.equal(c130Validation.learner_routes.pdf.pages, 666);
assert.equal(c130Validation.claim_boundaries.native_html_claimed, false);
assert.equal(c130Validation.claim_boundaries.pdf_ua_claimed, false);
assert.equal(c130Validation.claim_boundaries.python_authority_validators_replayed, true);
assert.equal(c130Validation.authority_replay.state, 'pass_postpublication_authority_replay');
assert.equal(c130Route.course_id, 'C130');
assert.equal(c130Route.primary_learner_action.kind, 'pages_learner_landing');
assert.equal(c130Route.primary_reader.format, 'linked_pdf');
assert.equal(c130Route.primary_reader.pages, 666);
assert.equal(c130Route.routes.length, 7);
assert.equal(c130Route.adapter.canonical_records, 51704);
assert.equal(c130Route.adapter.machine_data_is_primary_learner_destination, false);
assert.doesNotMatch(c130Html, /<script\b/i);

const publicText = Buffer.concat(Object.values(docsBytes)).toString('utf8');
for (const pattern of [
  /C:\\\\Users\\\\/i,
  /Authorization:\s*Bearer/i,
  /access[_-]?token/i,
  /api[_-]?token/i,
  /"access"\s*:\s*"(?:private|restricted|embargoed|blocked)"/i,
]) assert.doesNotMatch(publicText, pattern);
// Historical comparative evidence can retain historical terminology. This
// wording check applies to the current learner interface, not archive quotes.
assert.doesNotMatch(html + css + js, /owner[_-]?native/i);

let publicMirror = { checked: false, byte_identical_files: 0 };
if (checkPublic) {
  for (const path of logicalFiles) {
    const publicBytes = await readFile(resolve(project, 'public/hub', path));
    assert.deepEqual(publicBytes, docsBytes[path], 'public/hub/' + path + ': mirror drift.');
  }
  publicMirror = { checked: true, byte_identical_files: logicalFiles.length };
}

const receipt = {
  schema_id: 'interlanguage/open-course-capsule-site-validation/v1',
  schema_version: '1.0.0',
  state: 'pass',
  checks: {
    course_rows: 40,
    static_fallback_rows: 40,
    seven_layer_rows: 40,
    prerequisite_edges: 83,
    prerequisite_dag_visited: 40,
    published_rows: 38,
    production_rows: 2,
    educator_rows: 33,
    semantic_adapter_rows: expectedLiveAdapterRoles.length + expectedCapabilityAdapterRoles.length,
    semantic_adapter_packages: clpSuccessorIndex.packages.length + expectedCapabilityPackageCount,
    contract_2_3_1_roles: expectedLiveAdapterRoles.length,
    course_learning_capability_roles: rows.filter(({ layers }) => layers.interoperability.semantic_adapter.contract_version === 'course-learning-capability/1').length,
    snapshot_v2_public_role_bindings: 9,
    snapshot_v2_pending_role_bindings: 0,
    judson_course_views: 2,
    judson_native_chapter_joins: 23,
    judson_route_evidence: 'pass',
    learner_tool_courses: Object.keys(authorityToolsByCourse).length,
    learner_tools: authorityToolIds.length,
    learner_tool_authority_capsule_public_equality: 'pass',
    learner_tool_html_destination_gate: 'pass',
    design_policy_rows: 40,
    design_policy_public_mirror: 'pass',
    public_baseline_public_mirror: 'pass',
    terminology_policy_public_mirror: 'pass',
    terminology_policy_checksum_closure: 'pass',
    terminology_policy_probability_family_concepts: 9,
    terminology_policy_probability_family_state: 'evidence_required',
    d40_completion_truth: 'pass',
    public_access_rows: 40,
    accessibility_controls: 'pass',
    bahasa_primary_interface: 'pass',
    machine_data_links: 'pass',
    privacy_credential_scan: 'pass',
  },
  artifacts: Object.fromEntries(logicalFiles.map((path) => [path, identity('docs/' + path, docsBytes[path])])),
  public_mirror: publicMirror,
};
const receiptBytes = Buffer.from(canonicalJson(receipt));
const receiptPath = resolve(project, 'backend/course-capsule-v1/validation/SITE_VALIDATION_RECEIPT.json');
await mkdir(dirname(receiptPath), { recursive: true });
await writeFile(receiptPath, receiptBytes);
console.log(JSON.stringify({ status: 'pass', receipt: identity('backend/course-capsule-v1/validation/SITE_VALIDATION_RECEIPT.json', receiptBytes), ...receipt.checks, public_mirror: publicMirror }, null, 2));
