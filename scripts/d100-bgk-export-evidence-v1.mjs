import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

export const d100BgkExportPaths={
  d100BgkExportBinding:'backend/course-capsule-v1/authority/d100-bgk-export-inputs-v1.json',
  d100BgkExportReplay:'backend/course-capsule-v1/adapters/d100-native-production-v1/bgk-backend-replay.json',
};
const sha=b=>createHash('sha256').update(b).digest('hex');
const bindingSha='15e67daa7ba4659ed4e2b50d007c93eb013798059a48c6f9612aa7ce8d367465';
export function validateD100BgkExport(raw) {
  const binding=JSON.parse(raw.d100BgkExportBinding),proof=JSON.parse(raw.d100BgkExportReplay);
  assert.equal(sha(raw.d100BgkExportBinding),bindingSha,'Frozen native inputs/outputs changed');
  assert.equal(binding.schema,'d100-bgk-native-export-inputs/1');
  assert.equal(binding.state,'bound');assert.equal(binding.course_id,'D100');
  assert.equal(binding.locale,'id-ID');assert.equal(binding.lane,'bgk');
  assert.equal(binding.inputs.length,727);assert.equal(binding.outputs.length,19);
  assert.equal(new Set(binding.inputs.map(r=>r.path)).size,727);
  assert.equal(new Set(binding.outputs.map(r=>r.path)).size,19);
  assert.equal(binding.inputs.filter(r=>r.path.startsWith('backend/bgk-units-01-30/')).length,19);
  assert.equal(binding.inputs.filter(r=>r.path.startsWith('backend/bgk-units-01-30-corr1/')).length,0);
  assert.equal(proof.schema,'d100-bgk-native-export-replay/1');
  assert.equal(proof.state,'pass');assert.equal(proof.isolated_runs,2);
  for(const key of ['native_outputs_reproduced','historical_registry_used','existing_reader_bytes_used'])
    assert.equal(proof[key],true,key);
  for(const key of ['producer_writes','current_backend_used_as_input','tex_launched',
      'network_used','new_semantic_review','whole_backend_complete','fresh_pdf_build'])assert.equal(proof[key],false,key);
  assert.deepEqual(proof.input_binding,{path:d100BgkExportPaths.d100BgkExportBinding,
    bytes:raw.d100BgkExportBinding.length,sha256:bindingSha});
  assert.deepEqual(proof.scope_counts,binding.scope_counts);
  assert.deepEqual(proof.record_counts,binding.record_counts);
  assert.equal(Object.values(proof.record_counts).reduce((a,b)=>a+b,0),21690);
  assert.equal(proof.scope_counts.source_course_units,30);assert.equal(proof.scope_counts.source_files,99);
  assert.equal(proof.scope_counts.source_segments,7506);assert.equal(proof.scope_counts.preserved_baseline_ids,21686);
  assert.equal(proof.scope_counts.exercises,495);assert.equal(proof.scope_counts.public_solutions,25);
  assert.deepEqual(proof.runs.map(r=>r.label),['a','b']);
  for(const run of proof.runs) {
    assert.equal(run.inputs,727);assert.deepEqual(run.outputs,binding.outputs);
    assert.deepEqual(run.validation,binding.validation);
    assert.equal(run.validation.schema_validated_records,21690);
    assert.equal(run.validation.source_projection.record_backed_source_file_count,99);
    assert.equal(run.validation.source_projection.current_source_file_count,90);
    assert.equal(run.validation.counts.exercise,495);assert.equal(run.validation.counts.solution,25);
  }
  return proof;
}
export async function loadD100BgkExport(root) {
  const raw={};
  for(const [key,path] of Object.entries(d100BgkExportPaths))raw[key]=await readFile(resolve(root,path));
  return {report:validateD100BgkExport(raw),raw,evidence:Object.entries(d100BgkExportPaths).map(([key,path])=>({
    path,bytes:raw[key].length,sha256:sha(raw[key])}))};
}
