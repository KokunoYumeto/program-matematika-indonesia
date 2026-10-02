import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

export const d100OriginalExportPaths={
  d100OriginalExportBinding:'backend/course-capsule-v1/authority/d100-original-export-inputs-v1.json',
  d100OriginalExportReplay:'backend/course-capsule-v1/adapters/d100-native-production-v1/original-backend-replay.json',
};
const sha=b=>createHash('sha256').update(b).digest('hex');
const bindingSha='f15e8cfefd0ae8966b207467db722bc74236f937a0fad2c5663ab1babf812012';
export function validateD100OriginalExport(raw) {
  const binding=JSON.parse(raw.d100OriginalExportBinding),proof=JSON.parse(raw.d100OriginalExportReplay);
  assert.equal(sha(raw.d100OriginalExportBinding),bindingSha,'Frozen input/output identities changed');
  assert.equal(binding.schema,'d100-original-native-export-inputs/1');
  assert.equal(binding.state,'bound');assert.equal(binding.course_id,'D100');
  assert.equal(binding.locale,'id-ID');assert.equal(binding.lane,'original');
  assert.equal(binding.inputs.length,213);assert.equal(binding.outputs.length,23);
  assert.equal(new Set(binding.inputs.map(r=>r.path)).size,213);
  assert.equal(new Set(binding.outputs.map(r=>r.path)).size,23);
  assert.equal(proof.schema,'d100-original-native-export-replay/1');
  assert.equal(proof.state,'pass');assert.equal(proof.isolated_runs,2);
  assert.equal(proof.native_outputs_reproduced,true);
  assert.deepEqual(proof.input_binding,{path:d100OriginalExportPaths.d100OriginalExportBinding,
    bytes:raw.d100OriginalExportBinding.length,sha256:bindingSha});
  for(const key of ['producer_writes','existing_backend_used_as_input','tex_launched',
      'network_used','new_semantic_review','whole_backend_complete'])assert.equal(proof[key],false,key);
  assert.deepEqual(proof.scope_counts,binding.scope_counts);
  assert.deepEqual(proof.record_counts,binding.record_counts);
  assert.equal(Object.values(proof.record_counts).reduce((a,b)=>a+b,0),1064);
  assert.equal(proof.scope_counts.new_source_course_units,0);
  assert.equal(proof.scope_counts.formula_spans,3790);
  assert.equal(proof.scope_counts.new_mastery_solutions,44);
  assert.equal(proof.scope_counts.existing_public_mastery_source_solutions,13);
  assert.deepEqual(proof.runs.map(r=>r.label),['a','b']);
  for(const run of proof.runs) {
    assert.equal(run.inputs,213);assert.deepEqual(run.outputs,binding.outputs);
    assert.deepEqual(run.validation,binding.validation);
    assert.equal(run.validation.status,'PASS');assert.equal(run.validation.record_count,1064);
    assert.equal(run.validation.relation_count,560);assert.equal(run.validation.source_reference_count,57);
    assert.ok(Object.values(run.validation.checks).every(v=>v==='PASS'));
  }
  return proof;
}
export async function loadD100OriginalExport(root) {
  const raw={};
  for(const [key,path] of Object.entries(d100OriginalExportPaths))raw[key]=await readFile(resolve(root,path));
  return {report:validateD100OriginalExport(raw),raw,evidence:Object.entries(d100OriginalExportPaths).map(([key,path])=>({
    path,bytes:raw[key].length,sha256:sha(raw[key])}))};
}
