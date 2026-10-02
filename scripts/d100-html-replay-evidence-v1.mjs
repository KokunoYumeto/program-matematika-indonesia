import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

const base='backend/course-capsule-v1/adapters/d100-native-production-v1';
export const d100HtmlReplayPaths={
  d100HtmlReplay:`${base}/HTML_REPLAY.json`,
  d100ClassicalHtmlReplay:`${base}/classical-html-replay.json`,
  d100BgkHtmlReplay:`${base}/bgk-html-replay.json`,
  d100OriginalHtmlReplay:`${base}/original-html-replay.json`,
};
const pins=[
  ['classical','d100ClassicalHtmlReplay',329,23773577,'ea23c11b6a710a058e9d782eea1a7e0f2971a1551606f6cd51fc45209e9f87b5'],
  ['bgk','d100BgkHtmlReplay',269,6837686,'1805fb6325a12d0400999d5fab5bd4fe101174e088a7a2e54fa47ffb32ce243e'],
  ['original','d100OriginalHtmlReplay',170,1431866,'e901f73948ad7637cf7dfb0212b43acb08157afacb719f25a942199673bf2233'],
];
const sha=b=>createHash('sha256').update(b).digest('hex');
export function validateD100HtmlReplay(raw) {
  const report=JSON.parse(raw.d100HtmlReplay);
  assert.equal(report.schema,'d100-native-html-production-evidence/1');
  assert.equal(report.course_id,'D100');assert.equal(report.locale,'id-ID');
  assert.equal(report.state,'verified_html_only');assert.equal(report.isolated_builds,6);
  assert.equal(report.source_units,60);assert.equal(report.companion_units,32);
  assert.equal(report.runtime_dependencies_added,28);
  for(const key of ['native_data_export_replayed','fresh_pdf_build','semantic_canon_review','whole_backend_complete'])
    assert.equal(report[key],false,`D100 HTML proof cannot establish ${key}`);
  assert.equal(report.readers.length,3);
  for(const [index,[lane,key,inputs,bytes,sha256]] of pins.entries()) {
    const row=report.readers[index], proof=JSON.parse(raw[key]);
    assert.equal(row.lane,lane);assert.equal(row.inputs_per_run,inputs);
    assert.equal(row.source_units,lane==='original'?0:30);
    assert.equal(row.companion_units,lane==='original'?32:0);
    assert.equal(row.proof.path,`${lane}-html-replay.json`);
    assert.equal(row.proof.bytes,raw[key].length);assert.equal(row.proof.sha256,sha(raw[key]));
    assert.equal(proof.state,'pass');assert.equal(proof.course_id,'D100');assert.equal(proof.locale,'id-ID');
    for(const flag of ['producer_writes','tex_launched','pdf_replayed','whole_backend_complete','runtime_producer_sources_used'])
      assert.equal(proof[flag],false);
    assert.equal(proof.byte_identical_to_native,true);
    assert.deepEqual(proof.runs.map(r=>r.label),['a','b']);
    assert.deepEqual(row.html,{bytes,sha256});
    for(const run of proof.runs) {
      assert.deepEqual(run.html,{bytes,sha256});assert.equal(run.source_files,inputs);
      assert.equal(run.tool,'pandoc 3.9.0.2');assert.equal(run.input_bytes_unchanged,true);
    }
    if(lane==='original')for(const run of proof.runs) {
      assert.equal(run.new_source_units,0);assert.equal(run.html_checks.broken_internal_or_bundled_links,0);
      assert.equal(run.html_checks.mathml_nodes,3790);assert.equal(run.html_checks.external_render_resources,0);
      assert.deepEqual(run.bundled_bgk,{bytes:pins[1][3],sha256:pins[1][4]});
    }
  }
  return report;
}
export async function loadD100HtmlReplay(root) {
  const raw={};
  for(const [key,path] of Object.entries(d100HtmlReplayPaths)) raw[key]=await readFile(resolve(root,path));
  return {report:validateD100HtmlReplay(raw),raw,evidence:Object.entries(d100HtmlReplayPaths).map(([key,path])=>({
    path,bytes:raw[key].length,sha256:sha(raw[key])}))};
}
