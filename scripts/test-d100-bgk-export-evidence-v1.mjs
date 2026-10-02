import assert from 'node:assert/strict';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadD100BgkExport,validateD100BgkExport} from './d100-bgk-export-evidence-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const {raw}=await loadD100BgkExport(root);
let rejected=0;
function mutate(key,edit) {
  const copy={...raw},value=JSON.parse(copy[key]);edit(value);
  copy[key]=Buffer.from(JSON.stringify(value));
  assert.throws(()=>validateD100BgkExport(copy));rejected++;
}
const proof='d100BgkExportReplay';
for(const key of ['producer_writes','current_backend_used_as_input','tex_launched',
    'network_used','new_semantic_review','whole_backend_complete','fresh_pdf_build'])mutate(proof,v=>v[key]=true);
for(const key of ['historical_registry_used','existing_reader_bytes_used','native_outputs_reproduced'])
  mutate(proof,v=>v[key]=false);
mutate(proof,v=>v.runs.pop());
mutate(proof,v=>v.runs[1].label='a');
mutate(proof,v=>v.runs[0].outputs.pop());
mutate(proof,v=>v.runs[1].outputs[0].sha256='0'.repeat(64));
mutate(proof,v=>v.scope_counts.source_course_units=60);
mutate(proof,v=>v.scope_counts.source_files=90);
mutate(proof,v=>v.runs[0].validation.schema_validated_records=0);
mutate(proof,v=>v.runs[0].validation.source_projection.record_backed_source_file_count=0);
mutate(proof,v=>v.runs[0].validation.counts.solution=495);
mutate(proof,v=>v.runs[0].inputs=726);
mutate('d100BgkExportBinding',v=>v.inputs.pop());
console.log(JSON.stringify({state:'pass',rejected_mutations:rejected,records:21690,
  scope:'BGK data from current source, historical registry and existing readers; not new PDF or semantic review'}));
