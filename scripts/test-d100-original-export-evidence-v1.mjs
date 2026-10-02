import assert from 'node:assert/strict';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadD100OriginalExport,validateD100OriginalExport} from './d100-original-export-evidence-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const {raw}=await loadD100OriginalExport(root);
let rejected=0;
function mutate(key,edit) {
  const copy={...raw},value=JSON.parse(copy[key]);edit(value);
  copy[key]=Buffer.from(JSON.stringify(value));
  assert.throws(()=>validateD100OriginalExport(copy));rejected++;
}
const proof='d100OriginalExportReplay';
for(const key of ['producer_writes','existing_backend_used_as_input','tex_launched',
    'network_used','new_semantic_review','whole_backend_complete'])mutate(proof,v=>v[key]=true);
mutate(proof,v=>v.runs.pop());
mutate(proof,v=>v.runs[1].label='a');
mutate(proof,v=>v.runs[0].outputs.pop());
mutate(proof,v=>v.runs[1].outputs[0].sha256='0'.repeat(64));
mutate(proof,v=>v.scope_counts.new_source_course_units=32);
mutate(proof,v=>v.scope_counts.existing_public_mastery_source_solutions=0);
mutate(proof,v=>v.runs[0].validation.checks.markdown_formula_link_reconstruction='FAIL');
mutate(proof,v=>v.runs[0].inputs=212);
mutate('d100OriginalExportBinding',v=>v.inputs.pop());
console.log(JSON.stringify({state:'pass',rejected_mutations:rejected,records:1064,
  scope:'companion data export only; not classical/BGK/PDF/semantic closure'}));
