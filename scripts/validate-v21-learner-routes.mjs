import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = (relative) => readFile(resolve(root, relative));
const json = async (relative) => JSON.parse((await read(relative)).toString('utf8'));
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');

const [legacyBytes, d20Bytes, c100, aggregate, c100PilotUnits, readerBytes, styleBytes, solutionBytes, landing] = await Promise.all([
  read('docs/data/unit-route-v2.1.json'),
  read('docs/data/unit-route-D20-v2.1.json'),
  json('docs/data/unit-route-C100-v2.1.json'),
  json('docs/data/unit-routes-v2.1.json'),
  read('backend/v2.1/pilots/c100-geometry/units.jsonl'),
  read('docs/id-ID/courses/C100/reader/index.html'),
  read('docs/id-ID/courses/C100/reader/style.css'),
  read('docs/id-ID/courses/C100/solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf'),
  read('docs/id-ID/courses/C100/index.html'),
]);
assert.deepEqual(legacyBytes, d20Bytes, 'Legacy unit-route-v2.1.json must remain byte-identical to D20 v1.');
const d20 = JSON.parse(d20Bytes.toString('utf8'));
assert.equal(d20.schema_id, 'program-matematika-indonesia/unit-route-v2.1/v1');
assert.equal(d20.course_id, 'D20');
assert.equal(d20.units.length, 17);
assert.equal(c100.schema_id, 'program-matematika-indonesia/unit-route-v2.1/v1');
assert.equal(c100.course_id, 'C100');
assert.equal(c100.units.length, 939);
assert.equal(aggregate.schema_id, 'program-matematika-indonesia/unit-route-v2.1/v2');
assert.deepEqual(aggregate.summary, {course_count: 2, unit_count: 956, chapter_wrapper_count: 37, exact_hosted_reader_count: 1, exact_hosted_solution_pdf_count: 1});
assert.deepEqual(aggregate.courses.map(({ course_id }) => course_id), ['D20', 'C100']);
assert.deepEqual(aggregate.courses, [d20, c100], 'Aggregate route objects must exactly equal the two course manifests.');

assert.equal(readerBytes.length, 3994893);
assert.equal(sha256(readerBytes), 'e20cb2b22e2b3e2691c68cba0ba71352ec81db954d41a98c7bacac6d31708add');
assert.equal(styleBytes.length, 5098);
assert.equal(sha256(styleBytes), '553a606757f117c9edefb0c5c339d490fd55cefd9c10b40e4d60774c30e32887');
assert.equal(solutionBytes.length, 2698925);
assert.equal(sha256(solutionBytes), '01b618884353905e5be06ac7c85249f2aa0b127687a7e93038f5b65d5fddcdc7');
assert.match(landing.toString('utf8'), /Mulai membaca HTML/);
assert.match(landing.toString('utf8'), /href="solutions\/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20\.pdf"/);
assert.doesNotMatch(landing.toString('utf8'), /href="[^"]+\.(?:json|jsonl|csv)(?:[?#"])/i);

const pilotUnits = c100PilotUnits.toString('utf8').trimEnd().split('\n').map((line) => JSON.parse(line));
assert.equal(pilotUnits.length, 939);
assert.deepEqual(c100.units.map(({ id }) => id), pilotUnits.map(({ stable_unit_id }) => stable_unit_id));
const htmlText = readerBytes.toString('utf8');
const htmlIdCounts = new Map();
for (const match of htmlText.matchAll(/\sid="([^"]+)"/g)) {
  htmlIdCounts.set(match[1], (htmlIdCounts.get(match[1]) ?? 0) + 1);
}
for (const [index, unit] of c100.units.entries()) {
  const pilot = pilotUnits[index];
  assert.equal(unit.kind, pilot.native_unit_kind, `${unit.id}: route kind differs from pilot.`);
  assert.equal(unit.order_key, pilot.order_key, `${unit.id}: route order differs from pilot.`);
  assert.equal(unit.title, pilot.title, `${unit.id}: route title differs from pilot.`);
  assert.equal(unit.native_learner_url, pilot.learner_route.url, `${unit.id}: learner URL differs from pilot.`);
  assert.equal(unit.route_state, pilot.learner_route.route_state, `${unit.id}: route state differs from pilot.`);
  assert.doesNotMatch(unit.central_url, /\.(?:json|jsonl|csv)(?:[?#]|$)/i);
  if (unit.kind === 'independent_solution') {
    assert.equal(unit.native_html_url, null, `${unit.id}: a PDF fallback must not be described as native HTML.`);
    assert.equal(unit.central_url, unit.native_learner_url, `${unit.id}: solution central URL must be the exact local PDF.`);
    assert.equal(unit.route_state, 'central_exact_owner_solution_pdf_materialized_course_level_fallback_no_named_destination');
    assert.equal(unit.central_url, 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf');
  } else {
    assert.equal(htmlIdCounts.get(unit.id), 1, `${unit.id}: semantic-reader anchor must occur exactly once.`);
    assert.equal(unit.native_html_url, unit.native_learner_url, `${unit.id}: semantic HTML URL alias mismatch.`);
    assert.match(unit.native_html_url, /^https:\/\/kokunoyumeto\.github\.io\/program-matematika-indonesia\/id-ID\/courses\/C100\/reader\/#/);
    if (!/^o004\.petrunin\.ch\d{2}$/.test(unit.id)) {
      assert.equal(unit.central_url, unit.native_html_url, `${unit.id}: nonchapter route must resolve directly to its semantic-reader anchor.`);
    }
  }
}

for (const number of Array.from({length: 20}, (_, index) => index + 1)) {
  const slug = `bab-${String(number).padStart(2, '0')}`;
  const chapterId = `o004.petrunin.ch${String(number).padStart(2, '0')}`;
  const unit = c100.units.find(({ id }) => id === chapterId);
  assert.ok(unit, `${chapterId}: chapter route record missing.`);
  assert.equal(unit.central_url, `https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/units/${slug}/`);
  const wrapper = (await read(`docs/id-ID/courses/C100/units/${slug}/index.html`)).toString('utf8');
  assert.match(wrapper, /data-program-home href="\.\.\/\.\.\/\.\.\/\.\.\/\.\.\/id\/#course-C100"/, `${slug}: broken course-aware program breadcrumb.`);
  assert.match(wrapper, /href="\.\.\/\.\.\/"/, `${slug}: broken course breadcrumb.`);
  assert.match(wrapper, new RegExp(`rel="canonical" href="${unit.central_url.replaceAll('.', '\\.')}"`));
  assert.match(wrapper, new RegExp(`reader/#o004\\.petrunin\\.ch${String(number).padStart(2, '0')}`));
}
for (const unit of d20.units) {
  const slug = unit.slug;
  const wrapper = (await read(`docs/id-ID/courses/D20/units/${slug}/index.html`)).toString('utf8');
  assert.match(wrapper, /data-program-home href="\.\.\/\.\.\/\.\.\/\.\.\/\.\.\/id\/#course-D20"/, `D20 ${slug}: broken course-aware program breadcrumb.`);
  assert.match(wrapper, /href="\.\.\/\.\.\/"/, `D20 ${slug}: broken course breadcrumb.`);
  assert.match(wrapper, new RegExp(`rel="canonical" href="${unit.central_url.replaceAll('.', '\\.')}"`));
  assert.ok(wrapper.includes(`href="${unit.native_html_url}"`), `D20 ${slug}: native reader link mismatch.`);
}

console.log(JSON.stringify({
  result: 'pass',
  courses: 2,
  route_units: 956,
  c100_stable_units: 939,
  c100_reader_bytes: readerBytes.length,
  c100_reader_sha256: sha256(readerBytes),
  c100_solution_pdf_bytes: solutionBytes.length,
  c100_solution_pdf_sha256: sha256(solutionBytes),
  legacy_d20_manifest_sha256: sha256(legacyBytes),
}, null, 2));
