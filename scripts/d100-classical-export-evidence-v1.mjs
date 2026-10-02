import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

export const d100ClassicalExportPaths={
  d100ClassicalExportBinding:'backend/course-capsule-v1/authority/d100-classical-export-inputs-v1.json',
  d100ClassicalExportReplay:'backend/course-capsule-v1/adapters/d100-native-production-v1/classical-backend-replay.json',
};
const sha=b=>createHash('sha256').update(b).digest('hex');
const bindingSha='6d3811b7138aeff8cdeaafcd9dbc5246988dead5f52a200dd44004f20d7938a4';
export function validateD100ClassicalExport(raw) {
  const binding=JSON.parse(raw.d100ClassicalExportBinding),proof=JSON.parse(raw.d100ClassicalExportReplay);
  assert.equal(sha(raw.d100ClassicalExportBinding),bindingSha,'Frozen native inputs/outputs changed');
  assert.equal(binding.schema,'d100-classical-native-export-inputs/1');
  assert.equal(binding.state,'bound');assert.equal(binding.course_id,'D100');
  assert.equal(binding.locale,'id-ID');assert.equal(binding.lane,'classical');
  assert.equal(binding.inputs.length,129);assert.equal(binding.outputs.length,19);
  assert.equal(new Set(binding.inputs.map(r=>r.path)).size,129);
  assert.equal(new Set(binding.outputs.map(r=>r.path)).size,19);
  assert.equal(binding.inputs.filter(r=>r.path.startsWith('backend/units-01-30/')).length,3);
  assert.equal(binding.inputs.filter(r=>r.path.startsWith('backend/units-01-30-corr1/')).length,0);
  assert.equal(proof.schema,'d100-classical-native-export-replay/1');
  assert.equal(proof.state,'pass');assert.equal(proof.isolated_runs,2);
  assert.equal(proof.native_outputs_reproduced,true);assert.equal(proof.historical_registry_used,true);
  for(const key of ['producer_writes','current_backend_used_as_input','tex_launched',
      'network_used','new_semantic_review','whole_backend_complete'])assert.equal(proof[key],false,key);
  assert.deepEqual(proof.input_binding,{path:d100ClassicalExportPaths.d100ClassicalExportBinding,
    bytes:raw.d100ClassicalExportBinding.length,sha256:bindingSha});
  assert.deepEqual(proof.scope_counts,binding.scope_counts);
  assert.deepEqual(proof.record_counts,binding.record_counts);
  assert.equal(Object.values(proof.record_counts).reduce((a,b)=>a+b,0),23869);
  assert.equal(proof.scope_counts.source_course_units,30);assert.equal(proof.scope_counts.source_files,120);
  assert.equal(proof.scope_counts.source_segments,8056);assert.equal(proof.scope_counts.preserved_baseline_ids,22752);
  assert.deepEqual(proof.runs.map(r=>r.label),['a','b']);
  for(const run of proof.runs) {
    assert.equal(run.inputs,129);assert.deepEqual(run.outputs,binding.outputs);
    assert.deepEqual(run.validation,binding.validation);
    assert.equal(run.validation.json_schema_validated_records,23869);
    assert.equal(run.validation.source_projection.source_file_count,120);
    assert.equal(run.validation.ledger_projection.terminology_record_count,276);
    assert.equal(run.validation.ledger_projection.correction_record_count,159);
  }
  return proof;
}
export async function loadD100ClassicalExport(root) {
  const raw={};
  for(const [key,path] of Object.entries(d100ClassicalExportPaths))raw[key]=await readFile(resolve(root,path));
  return {report:validateD100ClassicalExport(raw),raw,evidence:Object.entries(d100ClassicalExportPaths).map(([key,path])=>({
    path,bytes:raw[key].length,sha256:sha(raw[key])}))};
}
