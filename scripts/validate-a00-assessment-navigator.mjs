import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const root = resolve(project, 'docs/id-ID/courses/A00/latihan');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const readJson = async (path) => JSON.parse(await readFile(path, 'utf8'));

const [data, audit, html, script, style, sourceScript, sourceStyle, cardScript, learnerTools, schema] = await Promise.all([
  readJson(resolve(root, 'assessment-map-v1.json')),
  readJson(resolve(root, 'anchor-audit-v1.json')),
  readFile(resolve(root, 'index.html'), 'utf8'),
  readFile(resolve(root, 'latihan.js')),
  readFile(resolve(root, 'latihan.css')),
  readFile(resolve(project, 'site/a00/latihan.js')),
  readFile(resolve(project, 'site/a00/latihan.css')),
  readFile(resolve(project, 'docs/app.js'), 'utf8'),
  readJson(resolve(project, 'docs/data/learner-tools-v1.json')),
  readJson(resolve(project, 'schemas/v1/a00-assessment-map-v1.schema.json')),
]);

assert.equal(data.$schema, schema.$id);
assert.equal(data.schema_id, 'interlanguage/program-matematika-indonesia/a00-assessment-map/v1');
assert.equal(data.schema_version, '1.0.0');
assert.equal(data.course_id, 'A00');
assert.equal(data.locale, 'id-ID');
assert.deepEqual(data.counts, {
  modules: 75,
  modules_with_assessments: 60,
  assessments: 8105,
  components: 13345,
  explicit_solutions: 5240,
  without_explicit_solution: 2865,
});
assert.equal(data.modules.length, 75);
assert.equal(new Set(data.modules.map(({ module_id }) => module_id)).size, 75);
assert.deepEqual(data.modules.map(({ ordinal }) => ordinal), Array.from({ length: 75 }, (_, index) => index + 1));

const assessments = data.modules.flatMap(({ assessments }) => assessments);
const components = assessments.flatMap(({ statement_anchors, solution_anchors }) => [...statement_anchors, ...solution_anchors]);
assert.equal(assessments.length, 8105);
assert.equal(components.length, 13345);
assert.equal(new Set(assessments.map(({ id }) => id)).size, 8105);
assert.equal(new Set(data.modules.flatMap((module) => module.assessments.map(({ native_id }) => `${module.module_id}\0${native_id}`))).size, 8105);
assert.equal(new Set(components.map(({ id }) => id)).size, 13345);
assert.equal(new Set(data.modules.flatMap((module) => module.assessments.flatMap(({ statement_anchors, solution_anchors }) => [...statement_anchors, ...solution_anchors].map(({ native_id }) => `${module.module_id}\0${native_id}`)))).size, 13345);
assert.equal(assessments.filter(({ has_explicit_solution }) => has_explicit_solution).length, 5240);
assert.equal(assessments.filter(({ has_explicit_solution }) => !has_explicit_solution).length, 2865);

const assessmentKeys = ['id', 'native_id', 'ordinal', 'category', 'category_label', 'has_explicit_solution', 'solution_gap_id', 'route_url', 'statement_anchors', 'solution_anchors'].sort();
const anchorKeys = ['id', 'native_id', 'route_url'].sort();
for (const module of data.modules) {
  assert.match(module.module_id, /^m\d+$/);
  assert.match(module.module_url, new RegExp(`/modules/${module.module_id}/index\\.html$`));
  assert.equal(module.counts.assessments, module.assessments.length);
  assert.equal(module.counts.components, module.assessments.reduce((sum, row) => sum + row.statement_anchors.length + row.solution_anchors.length, 0));
  assert.equal(module.counts.explicit_solutions, module.assessments.filter(({ has_explicit_solution }) => has_explicit_solution).length);
  assert.equal(module.counts.without_explicit_solution, module.assessments.filter(({ has_explicit_solution }) => !has_explicit_solution).length);
  for (const item of module.assessments) {
    assert.deepEqual(Object.keys(item).sort(), assessmentKeys);
    assert.equal(item.statement_anchors.length, 1);
    assert.equal(item.solution_anchors.length, item.has_explicit_solution ? 1 : 0);
    assert.equal(item.solution_gap_id === null, item.has_explicit_solution);
    assert.equal(item.route_url, `${module.module_url}#${item.native_id}`);
    assert.equal(item.category_label, data.category_labels[item.category]);
    for (const anchor of [...item.statement_anchors, ...item.solution_anchors]) {
      assert.deepEqual(Object.keys(anchor).sort(), anchorKeys);
      assert.equal(anchor.route_url, `${module.module_url}#${anchor.native_id}`);
    }
  }
}

assert.equal(audit.status, 'PASS');
assert.deepEqual(audit.counts, {
  modules: 75,
  assessment_anchors: 8105,
  component_anchors: 13345,
  expected_anchors: 21450,
  matched_exactly_once: 21450,
  missing: 0,
  duplicate: 0,
});
assert.equal(audit.files.length, 75);
assert.equal(audit.files.reduce((sum, row) => sum + row.matched_exactly_once, 0), 21450);
assert.ok(audit.files.every(({ missing, duplicate }) => missing === 0 && duplicate === 0));

const auditBytes = await readFile(resolve(root, 'anchor-audit-v1.json'));
assert.deepEqual(data.authority.owner_html_anchor_audit, {
  path: 'id-ID/courses/A00/latihan/anchor-audit-v1.json',
  bytes: auditBytes.length,
  sha256: sha256(auditBytes),
});
assert.deepEqual(script, sourceScript, 'Generated learner script differs from source template.');
assert.deepEqual(style, sourceStyle, 'Generated learner stylesheet differs from source template.');
assert.match(html, /<h1>Latihan &amp; diagnosis<\/h1>/);
assert.match(html, /8\.105/);
assert.match(html, /tanpa solusi eksplisit dalam sumber/i);
assert.match(html, /Peta, bukan mesin kuis/);
assert.doesNotMatch(html, /href="[^"]*(assessment-map|anchor-audit).*\.json/i, 'Machine JSON must not be a learner action.');
assert.doesNotMatch(html, /<noscript>/i, 'Static fallback must remain revealable after a JavaScript fetch failure.');
assert.equal((html.match(/<article class="assessment-module-card">/g) ?? []).length, 75, 'Static fallback must expose all 75 module cards.');
assert.ok(html.indexOf('id="assessment-static-fallback"') < html.indexOf('id="assessment-module-grid"'), 'Static fallback must precede the dynamic grid.');
assert.match(html, /id="atas"/);
assert.match(html, /href="\.\.\/\.\.\/\.\.\/\.\.\/index\.html">← Kembali ke program<\/a>/);
assert.match(html, /href="#atas">↑ Kembali ke atas<\/a>/);
assert.match(script.toString('utf8'), /render\(\);\s*staticFallback\.hidden = true;/, 'Static fallback may hide only after successful dynamic render.');
assert.match(script.toString('utf8'), /assessmentMap\?\.modules\) \|\| assessmentMap\.modules\.length !== 75/);
assert.match(cardScript, /learnerToolsByCourseId\[course\.id\]/);
assert.equal(learnerTools.courses.find(({ course_id }) => course_id === 'A00').tools[0].label, 'Latihan & diagnosis');

for (const [name, text] of [
  ['index.html', html],
  ['latihan.js', script.toString('utf8')],
  ['latihan.css', style.toString('utf8')],
  ['assessment-map-v1.json', JSON.stringify(data)],
  ['anchor-audit-v1.json', JSON.stringify(audit)],
]) {
  assert.doesNotMatch(text, /[A-Za-z]:\\Users\\/i, `${name}: local user path leaked.`);
  assert.doesNotMatch(text, /Authorization\s*:\s*Bearer/i, `${name}: credential header leaked.`);
  assert.doesNotMatch(text, /(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}/, `${name}: GitHub credential leaked.`);
}

console.log(JSON.stringify({
  status: 'PASS',
  counts: data.counts,
  anchor_audit: audit.counts,
  files: {
    html: { bytes: Buffer.byteLength(html), sha256: sha256(Buffer.from(html)) },
    data: { bytes: Buffer.byteLength(`${JSON.stringify(data, null, 2)}\n`), sha256: sha256(Buffer.from(`${JSON.stringify(data, null, 2)}\n`)) },
    script: { bytes: script.length, sha256: sha256(script) },
    style: { bytes: style.length, sha256: sha256(style) },
  },
}, null, 2));
