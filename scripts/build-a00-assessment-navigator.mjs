import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { access, copyFile, mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ownerRoot = resolve(project, '..', 'openstax-prealgebra');
const output = resolve(project, 'docs/id-ID/courses/A00/latihan');
const a00 = resolve(project, 'backend/v2.2/packages/a00-openstax-prealgebra-v0.1.0');
const o001 = resolve(project, 'backend/v2.2/owner-native-shards/o001-a00-assessments-v0.1.0');
const recordedAt = '2026-08-31T00:00:00Z';
const publicRoot = 'https://kokunoyumeto.github.io/openstax-prealgebra-2e-id-ID';
const frozenAnchorAuditSha256 = 'd50bd0203359a13f2eac176e021920635ed07258ee9622ab0d89e09c6ac12926';

const paths = {
  a00Manifest: resolve(a00, 'manifest.json'),
  o001Manifest: resolve(o001, 'manifest.json'),
  modules: resolve(o001, 'summaries/modules.jsonl'),
  assessments: resolve(o001, 'data/assessments.jsonl'),
  components: resolve(o001, 'data/assessment-components.jsonl'),
  gaps: resolve(o001, 'data/solution-gaps.jsonl'),
  units: resolve(a00, 'tables/units.jsonl'),
  memberships: resolve(a00, 'tables/course_unit_memberships.jsonl'),
  crosswalks: resolve(a00, 'tables/identity_crosswalks.jsonl'),
  routes: resolve(a00, 'tables/routes.jsonl'),
  surfaces: resolve(a00, 'tables/reader_surfaces.jsonl'),
  artifacts: resolve(a00, 'tables/artifacts.jsonl'),
  rightsAssignments: resolve(a00, 'tables/rights_assignments.jsonl'),
};

const categoryLabels = Object.freeze({
  'section:practice-perfect': 'Latihan penguasaan',
  'note:try': 'Coba sendiri',
  'section:review-exercises': 'Latihan ulasan',
  example: 'Contoh terpandu',
  'section:practice-test': 'Tes latihan',
  'note:be-prepared': 'Persiapan prasyarat',
  'section:writing': 'Menulis dan menjelaskan',
  'section:everyday': 'Penerapan sehari-hari',
  'section:section-exercises': 'Latihan bagian',
});

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const compact = (value) => JSON.stringify(value);
const pretty = (value) => `${JSON.stringify(value, null, 2)}\n`;
const escapeHtml = (value) => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;');

async function readJsonl(path) {
  const text = await readFile(path, 'utf8');
  const lines = text.split('\n').filter(Boolean);
  return lines.map((line, index) => {
    const row = JSON.parse(line);
    assert.equal(compact(row), line, `${relative(project, path)}:${index + 1} is not canonical JSONL.`);
    return row;
  });
}

async function fileFact(path, logicalPath) {
  const bytes = await readFile(path);
  return { path: logicalPath.split(sep).join('/'), bytes: bytes.length, sha256: sha256(bytes) };
}

function uniqueBy(rows, key, label) {
  const map = new Map();
  for (const row of rows) {
    const value = key(row);
    assert.ok(!map.has(value), `${label}: duplicate ${value}`);
    map.set(value, row);
  }
  return map;
}

function groupBy(rows, key) {
  const map = new Map();
  for (const row of rows) {
    const value = key(row);
    if (!map.has(value)) map.set(value, []);
    map.get(value).push(row);
  }
  return map;
}

function anchorMap(html) {
  const counts = new Map();
  for (const match of html.matchAll(/\bid="([^"]+)"/g)) {
    counts.set(match[1], (counts.get(match[1]) ?? 0) + 1);
  }
  return counts;
}

const [
  moduleRows,
  assessmentRows,
  componentRows,
  gapRows,
  unitRows,
  membershipRows,
  crosswalkRows,
  routeRows,
  surfaceRows,
  artifactRows,
  rightsAssignmentRows,
] = await Promise.all([
  readJsonl(paths.modules),
  readJsonl(paths.assessments),
  readJsonl(paths.components),
  readJsonl(paths.gaps),
  readJsonl(paths.units),
  readJsonl(paths.memberships),
  readJsonl(paths.crosswalks),
  readJsonl(paths.routes),
  readJsonl(paths.surfaces),
  readJsonl(paths.artifacts),
  readJsonl(paths.rightsAssignments),
]);

assert.equal(moduleRows.length, 75);
assert.equal(assessmentRows.length, 8105);
assert.equal(componentRows.length, 13345);
assert.equal(gapRows.length, 2865);
assert.equal(componentRows.filter(({ component_kind }) => component_kind === 'statement').length, 8105);
assert.equal(componentRows.filter(({ component_kind }) => component_kind === 'solution').length, 5240);
assert.deepEqual([...new Set(assessmentRows.map(({ context_classification }) => context_classification))].sort(), Object.keys(categoryLabels).sort());

const modulesById = uniqueBy(moduleRows, ({ module }) => module, 'module summaries');
const unitsById = uniqueBy(unitRows, ({ id }) => id, 'A00 units');
const membershipsByUnit = uniqueBy(membershipRows, ({ payload }) => payload.unit_id, 'A00 memberships');
const routesByUnit = uniqueBy(routeRows, ({ payload }) => payload.unit_id, 'A00 routes');
const surfacesById = uniqueBy(surfaceRows, ({ id }) => id, 'A00 surfaces');
const artifactsById = uniqueBy(artifactRows, ({ id }) => id, 'A00 artifacts');
const assessmentsByModule = groupBy(assessmentRows, ({ module }) => module);
const componentsByModule = groupBy(componentRows, ({ module }) => module);
const componentsByAssessment = groupBy(componentRows, ({ assessment_id }) => assessment_id);
const gapsByAssessment = uniqueBy(gapRows, ({ assessment_id }) => assessment_id, 'O001 gaps');
const assessmentById = uniqueBy(assessmentRows, ({ id }) => id, 'O001 assessments');
const rightsAssignmentSubjects = new Set(rightsAssignmentRows.map(({ payload }) => payload.target_id));

for (const component of componentRows) assert.ok(assessmentById.has(component.assessment_id), `orphan component ${component.id}`);
for (const gap of gapRows) assert.ok(assessmentById.has(gap.assessment_id), `orphan gap ${gap.id}`);

const moduleBindings = new Map();
for (const module of modulesById.keys()) {
  const crosswalk = crosswalkRows.filter(({ semantic_key }) => semantic_key.endsWith(`:crosswalk:${module}`));
  assert.equal(crosswalk.length, 1, `${module}: expected one crosswalk.`);
  const unit = unitsById.get(crosswalk[0].payload.target_id);
  assert.ok(unit, `${module}: projected unit missing.`);
  const membership = membershipsByUnit.get(unit.id);
  const route = routesByUnit.get(unit.id);
  assert.ok(membership && route, `${module}: membership or route missing.`);
  const surface = surfacesById.get(route.payload.surface_id);
  const artifact = surface && artifactsById.get(surface.payload.artifact_id);
  assert.ok(surface && artifact, `${module}: surface or artifact missing.`);
  assert.equal(membership.payload.ordinal, modulesById.get(module).module_ordinal, `${module}: ordinal drift.`);
  assert.equal(route.payload.public_url, `${publicRoot}/modules/${module}/index.html`, `${module}: public route drift.`);
  for (const id of [unit.id, surface.id, artifact.id]) {
    assert.ok(rightsAssignmentSubjects.has(id), `${module}: rights assignment missing for ${id}.`);
  }
  moduleBindings.set(module, { unit, membership, route, surface, artifact });
}

await mkdir(output, { recursive: true });
const anchorAuditPath = resolve(output, 'anchor-audit-v1.json');
let anchorAudit;
try {
  await access(resolve(ownerRoot, 'output/html-id/modules', moduleRows[0].module, 'index.html'));
  const anchorAuditRows = [];
  const compositeAnchors = new Set();
  for (const summary of [...moduleRows].sort((left, right) => left.module_ordinal - right.module_ordinal)) {
    const module = summary.module;
    const htmlPath = resolve(ownerRoot, 'output/html-id/modules', module, 'index.html');
    const htmlBytes = await readFile(htmlPath);
    const ids = anchorMap(htmlBytes.toString('utf8'));
    const expected = [
      ...(assessmentsByModule.get(module) ?? []).map(({ native_id }) => native_id),
      ...(componentsByModule.get(module) ?? []).map(({ native_id }) => native_id),
    ];
    assert.equal(new Set(expected).size, expected.length, `${module}: duplicate expected native anchor.`);
    for (const nativeId of expected) {
      assert.equal(ids.get(nativeId), 1, `${module}: ${nativeId} does not occur exactly once.`);
      const compositeKey = `${module}\0${nativeId}`;
      assert.ok(!compositeAnchors.has(compositeKey), `native anchor repeated within module: ${compositeKey}`);
      compositeAnchors.add(compositeKey);
    }
    anchorAuditRows.push({
      module,
      path: `output/html-id/modules/${module}/index.html`,
      bytes: htmlBytes.length,
      sha256: sha256(htmlBytes),
      expected_assessment_anchors: (assessmentsByModule.get(module) ?? []).length,
      expected_component_anchors: (componentsByModule.get(module) ?? []).length,
      matched_exactly_once: expected.length,
      missing: 0,
      duplicate: 0,
    });
  }
  assert.equal(compositeAnchors.size, 21450);
  anchorAudit = {
    schema_id: 'interlanguage/program-matematika-indonesia/a00-html-anchor-audit/v1',
    recorded_at: recordedAt,
    status: 'PASS',
    owner_reader_root: 'openstax-prealgebra/output/html-id',
    counts: {
      modules: 75,
      assessment_anchors: 8105,
      component_anchors: 13345,
      expected_anchors: 21450,
      matched_exactly_once: 21450,
      missing: 0,
      duplicate: 0,
    },
    files: anchorAuditRows,
  };
  await writeFile(anchorAuditPath, pretty(anchorAudit), 'utf8');
  assert.equal(sha256(await readFile(anchorAuditPath)), frozenAnchorAuditSha256, 'Fresh owner HTML replay differs from the admitted frozen audit.');
} catch (error) {
  if (error?.code !== 'ENOENT') throw error;
  const frozenBytes = await readFile(anchorAuditPath);
  assert.equal(sha256(frozenBytes), frozenAnchorAuditSha256, 'Frozen owner HTML audit identity drift.');
  anchorAudit = JSON.parse(frozenBytes.toString('utf8'));
  assert.equal(anchorAudit.status, 'PASS');
  assert.equal(anchorAudit.files.length, 75);
  for (const [index, summary] of [...moduleRows].sort((left, right) => left.module_ordinal - right.module_ordinal).entries()) {
    const row = anchorAudit.files[index];
    const assessments = (assessmentsByModule.get(summary.module) ?? []).length;
    const components = (componentsByModule.get(summary.module) ?? []).length;
    assert.equal(row.module, summary.module);
    assert.equal(row.expected_assessment_anchors, assessments);
    assert.equal(row.expected_component_anchors, components);
    assert.equal(row.matched_exactly_once, assessments + components);
    assert.equal(row.missing, 0);
    assert.equal(row.duplicate, 0);
  }
}

const modules = [...moduleRows]
  .sort((left, right) => left.module_ordinal - right.module_ordinal)
  .map((summary) => {
    const moduleId = summary.module;
    const binding = moduleBindings.get(moduleId);
    const assessments = [...(assessmentsByModule.get(moduleId) ?? [])]
      .sort((left, right) => left.ordinal - right.ordinal)
      .map((assessment) => {
        const components = [...(componentsByAssessment.get(assessment.id) ?? [])]
          .sort((left, right) => left.ordinal - right.ordinal);
        const statements = components.filter(({ component_kind }) => component_kind === 'statement');
        const solutions = components.filter(({ component_kind }) => component_kind === 'solution');
        assert.equal(statements.length, assessment.problem_component_count);
        assert.equal(solutions.length, assessment.solution_component_count);
        assert.equal(gapsByAssessment.has(assessment.id), solutions.length === 0);
        const toAnchor = ({ id, native_id }) => ({ id, native_id, route_url: `${binding.route.payload.public_url}#${native_id}` });
        return {
          id: assessment.id,
          native_id: assessment.native_id,
          ordinal: assessment.ordinal,
          category: assessment.context_classification,
          category_label: categoryLabels[assessment.context_classification],
          has_explicit_solution: solutions.length === 1,
          solution_gap_id: gapsByAssessment.get(assessment.id)?.id ?? null,
          route_url: `${binding.route.payload.public_url}#${assessment.native_id}`,
          statement_anchors: statements.map(toAnchor),
          solution_anchors: solutions.map(toAnchor),
        };
      });
    const categoryCounts = Object.fromEntries(Object.keys(categoryLabels).map((key) => [key, 0]));
    for (const assessment of assessments) categoryCounts[assessment.category] += 1;
    const components = componentsByModule.get(moduleId) ?? [];
    const explicitSolutions = assessments.filter(({ has_explicit_solution }) => has_explicit_solution).length;
    return {
      module_id: moduleId,
      ordinal: summary.module_ordinal,
      unit_id: binding.unit.id,
      title: binding.unit.payload.title,
      edition_id: binding.unit.payload.edition_id,
      rights_id: binding.unit.payload.rights_id,
      route_id: binding.route.id,
      surface_id: binding.surface.id,
      artifact_id: binding.artifact.id,
      module_url: binding.route.payload.public_url,
      counts: {
        assessments: assessments.length,
        components: components.length,
        explicit_solutions: explicitSolutions,
        without_explicit_solution: assessments.length - explicitSolutions,
      },
      category_counts: categoryCounts,
      assessments,
    };
  });

const data = {
  $schema: 'https://kokunoyumeto.github.io/program-matematika-indonesia/schema/v1/a00-assessment-map-v1.schema.json',
  schema_id: 'interlanguage/program-matematika-indonesia/a00-assessment-map/v1',
  schema_version: '1.0.0',
  recorded_at: recordedAt,
  course_id: 'A00',
  locale: 'id-ID',
  authority: {
    a00_manifest: await fileFact(paths.a00Manifest, 'backend/v2.2/packages/a00-openstax-prealgebra-v0.1.0/manifest.json'),
    o001_manifest: await fileFact(paths.o001Manifest, 'backend/v2.2/owner-native-shards/o001-a00-assessments-v0.1.0/manifest.json'),
    owner_html_anchor_audit: await fileFact(anchorAuditPath, 'id-ID/courses/A00/latihan/anchor-audit-v1.json'),
  },
  counts: {
    modules: modules.length,
    modules_with_assessments: modules.filter(({ counts }) => counts.assessments > 0).length,
    assessments: assessmentRows.length,
    components: componentRows.length,
    explicit_solutions: componentRows.filter(({ component_kind }) => component_kind === 'solution').length,
    without_explicit_solution: gapRows.length,
  },
  category_labels: categoryLabels,
  limitations: [
    'Peta ini menautkan inventaris ke pembaca HTML pemilik; peta pusat tidak menyalin teks matematika atau rumus.',
    'Sebanyak 2.865 latihan tidak mempunyai simpul solusi eksplisit dalam sumber maupun terjemahan; peta ini tidak menciptakan solusi baru.',
    'Peta ini bukan mesin kuis: tidak ada penilaian otomatis, model jawaban, rubrik, atau klaim penguasaan.',
  ],
  modules,
};
assert.deepEqual(data.counts, {
  modules: 75,
  modules_with_assessments: 60,
  assessments: 8105,
  components: 13345,
  explicit_solutions: 5240,
  without_explicit_solution: 2865,
});

const dataPath = resolve(output, 'assessment-map-v1.json');
await writeFile(dataPath, pretty(data), 'utf8');

const staticCards = modules.map((module) => `
        <article class="assessment-module-card">
          <div class="assessment-module-heading"><div><span class="module-code">${String(module.ordinal).padStart(2, '0')} · ${module.module_id}</span><h2>${escapeHtml(module.title)}</h2></div><a class="module-link" href="${module.module_url}" target="_blank" rel="noreferrer">Buka modul ↗</a></div>
          <div class="assessment-module-metrics"><span><strong>${module.counts.assessments.toLocaleString('id-ID')}</strong> latihan</span><span><strong>${module.counts.explicit_solutions.toLocaleString('id-ID')}</strong> dengan solusi</span><span><strong>${module.counts.without_explicit_solution.toLocaleString('id-ID')}</strong> tanpa solusi sumber</span></div>
        </article>`).join('');

const html = `<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Latihan &amp; diagnosis A00 — Program Matematika Indonesia</title>
  <meta name="description" content="Peta 8.105 latihan Prealjabar 2e Bahasa Indonesia dengan 5.240 solusi eksplisit dan tautan langsung ke pembaca HTML.">
  <meta name="theme-color" content="#102b2a">
  <meta property="og:title" content="Latihan &amp; diagnosis A00">
  <meta property="og:description" content="8.105 latihan dalam 75 modul Prealjabar 2e Bahasa Indonesia.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/A00/latihan/">
  <meta property="og:image" content="https://kokunoyumeto.github.io/program-matematika-indonesia/og.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/A00/latihan/">
  <link rel="stylesheet" href="../../../../styles.css">
  <link rel="stylesheet" href="latihan.css">
  <script type="module" src="latihan.js"></script>
</head>
<body class="assessment-page">
  <a class="skip-link" href="#utama">Lewati ke isi utama</a>
  <header class="assessment-header" id="atas">
    <a class="brand" href="../../../../index.html"><span class="brand-mark" aria-hidden="true">∴</span><span>Program Matematika Indonesia</span></a>
    <nav aria-label="Navigasi halaman"><a href="../../../../index.html#course-A00">Kartu A00</a><a href="${publicRoot}/" target="_blank" rel="noreferrer">Pembaca utama ↗</a></nav>
  </header>
  <main id="utama">
    <section class="assessment-hero">
      <div>
        <p class="eyebrow">A00 · Praaljabar dan fondasi kuantitatif</p>
        <h1>Latihan &amp; diagnosis</h1>
        <p class="assessment-lede">Temukan latihan berdasarkan modul, jenis, dan ketersediaan solusi. Setiap tautan membuka bagian yang tepat dalam pembaca Bahasa Indonesia yang sudah ada.</p>
      </div>
      <aside class="assessment-notice"><strong>Peta, bukan mesin kuis.</strong><p>Tidak ada skor otomatis atau klaim penguasaan. “Tanpa solusi” berarti sumber memang tidak menyediakan simpul solusi eksplisit—bukan kesalahan terjemahan.</p></aside>
    </section>
    <section class="assessment-stats" aria-label="Ringkasan inventaris">
      <div><strong>8.105</strong><span>latihan dalam inventaris</span></div>
      <div><strong>5.240</strong><span>solusi eksplisit tersedia</span></div>
      <div><strong>2.865</strong><span>tanpa solusi eksplisit dalam sumber</span></div>
      <div><strong>75</strong><span>modul, 60 berisi latihan</span></div>
    </section>
    <section class="assessment-controls" aria-label="Saring latihan">
      <label><span>Cari modul atau ID latihan</span><input id="assessment-search" type="search" placeholder="Contoh: pecahan, m81243, atau fs-id…" autocomplete="off"></label>
      <label><span>Jenis latihan</span><select id="assessment-category"><option value="all">Semua jenis</option></select></label>
      <label><span>Ketersediaan solusi</span><select id="assessment-solution"><option value="all">Semua</option><option value="with">Dengan solusi eksplisit</option><option value="without">Tanpa solusi eksplisit dalam sumber</option></select></label>
      <button id="assessment-reset" type="button">Hapus saringan</button>
    </section>
    <div class="assessment-result-row"><p id="assessment-result-status" role="status" aria-live="polite">Memuat peta latihan…</p><a href="${publicRoot}/" target="_blank" rel="noreferrer">Mulai belajar dari awal ↗</a></div>
    <section class="assessment-static-fallback" id="assessment-static-fallback" aria-labelledby="assessment-static-heading">
      <div class="assessment-static-intro">
        <p class="eyebrow">Daftar cadangan tanpa JavaScript</p>
        <h2 id="assessment-static-heading">Buka salah satu dari 75 modul</h2>
        <p>Daftar ini tetap dapat dipakai jika peta latihan interaktif gagal dimuat.</p>
      </div>
      <div class="assessment-module-grid" aria-label="Daftar modul statis">${staticCards}</div>
    </section>
    <section class="assessment-module-grid" id="assessment-module-grid" aria-label="Modul dan latihan"></section>
    <section class="assessment-method">
      <p class="eyebrow">Bagaimana halaman ini dibuat</p>
      <h2>Backend tetap modular; pelajar mendapatkan tautan yang bisa dipakai.</h2>
      <p>Inventaris struktural O001 tetap menjadi sumber mesin yang tersegel. Lapisan pusat hanya menghubungkan ID modul dan latihan ke unit, hak, edisi, dan jangkar HTML yang sudah diverifikasi. Tidak ada teks soal atau rumus yang disalin ke halaman pusat.</p>
    </section>
    <nav class="assessment-bottom-actions" aria-label="Tindakan akhir halaman"><a href="../../../../index.html">← Kembali ke program</a><a href="#atas">↑ Kembali ke atas</a></nav>
  </main>
</body>
</html>
`;

await Promise.all([
  writeFile(resolve(output, 'index.html'), html, 'utf8'),
  copyFile(resolve(project, 'site/a00/latihan.js'), resolve(output, 'latihan.js')),
  copyFile(resolve(project, 'site/a00/latihan.css'), resolve(output, 'latihan.css')),
]);

const reportFiles = await Promise.all([
  fileFact(resolve(output, 'index.html'), 'docs/id-ID/courses/A00/latihan/index.html'),
  fileFact(resolve(output, 'latihan.css'), 'docs/id-ID/courses/A00/latihan/latihan.css'),
  fileFact(resolve(output, 'latihan.js'), 'docs/id-ID/courses/A00/latihan/latihan.js'),
  fileFact(dataPath, 'docs/id-ID/courses/A00/latihan/assessment-map-v1.json'),
  fileFact(anchorAuditPath, 'docs/id-ID/courses/A00/latihan/anchor-audit-v1.json'),
]);
console.log(JSON.stringify({ status: 'PASS', counts: data.counts, files: reportFiles }, null, 2));
