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
  'backend/b80/B80.html',
  'backend/b80/B80-pengajar.html',
  'backend/b80/learning-map.json',
  'backend/b80/validation.json',
  'backend/d70/D70.html',
  'backend/d70/D70-pengajar.html',
  'backend/d70/learning-map.json',
  'backend/d70/validation.json',
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
const expectedLiveAdapterRoles = ['A00', 'B10', 'B20', 'B30', 'B50', 'B60', 'C30', 'C40', 'C80', 'C130', 'D20', 'D60', 'D110'];
const expectedCapabilityAdapterRoles = ['B70', 'B80', 'C10', 'C20', 'C50', 'C90', 'C100', 'D40', 'D70', 'D80'];
const expectedCapabilityPackageCount = 7;
const sortedIds = (ids) => [...ids].sort((a, b) => a.localeCompare(b, 'en', { numeric: true }));
assert.deepEqual(sortedIds(clpSuccessorIndex.adapters.map(({ role_id }) => role_id)), sortedIds(expectedLiveAdapterRoles), 'Live successor adapter role set differs.');
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
assert.equal(rows.filter(({ course }) => course.state === 'published').length, 36);
assert.equal(rows.filter(({ course }) => course.state === 'production').length, 4);
assert.equal(rows.filter((row) => row.layers.educator.features.length || row.layers.educator.resources.length).length, 25);
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
assert.equal(rows.filter((row) => Object.keys(row.layers).sort().join(',') === 'curriculum,educator,federation,interoperability,learner,production,translation').length, 40);
assert.equal(rows.filter((row) => row.learner_directed && row.open_access_policy.public_access_required).length, 40);
for (const row of rows) assert.deepEqual(row.layers.learner.tools, authorityToolsByCourse[row.course_id] ?? [], `${row.course_id}: public capsule learner-tool drift.`);
assert.equal(rows.filter((row) => row.layers.interoperability.design_policy?.profile === 'thin_format_neutral_zero_copy').length, 40);
assert.equal(manifest.summary.course_count, 40);
assert.equal(Object.keys(authorityToolsByCourse).length, 15);
assert.equal(authorityToolIds.length, 25);
assert.equal(manifest.summary.learner_tool_course_count, Object.keys(authorityToolsByCourse).length);
assert.equal(manifest.summary.learner_tool_count, authorityToolIds.length);
assert.equal(manifest.summary.published_count, 36);
assert.equal(manifest.summary.production_count, 4);
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
const b20 = rows.find(({ course_id }) => course_id === 'B20');
const b50 = rows.find(({ course_id }) => course_id === 'B50');
const c100 = rows.find(({ course_id }) => course_id === 'C100');
const d20 = rows.find(({ course_id }) => course_id === 'D20');
const d90 = rows.find(({ course_id }) => course_id === 'D90');
assert.match(b20.layers.learner.primary.url, /records\/22183943\//);
assert.match(b50.layers.learner.primary.url, /records\/22184443\//);
assert.equal(c100.layers.learner.primary.format, 'text/html');
assert.equal(d20.layers.learner.primary.format, 'text/html');
assert.equal(d90.layers.learner.primary.format, 'application/pdf');
assert.equal(d90.layers.learner.online_html.status, 'not_yet_produced');

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
    published_rows: 36,
    production_rows: 4,
    educator_rows: 25,
    semantic_adapter_rows: expectedLiveAdapterRoles.length + expectedCapabilityAdapterRoles.length,
    semantic_adapter_packages: clpSuccessorIndex.packages.length + expectedCapabilityPackageCount,
    contract_2_3_1_roles: expectedLiveAdapterRoles.length,
    course_learning_capability_roles: 4,
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
