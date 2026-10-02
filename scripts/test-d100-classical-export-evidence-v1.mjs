import assert from 'node:assert/strict';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadD100ClassicalExport,validateD100ClassicalExport} from './d100-classical-export-evidence-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const {raw}=await loadD100ClassicalExport(root);
let rejected=0;
function mutate(key,edit) {
  const copy={...raw},value=JSON.parse(copy[key]);edit(value);
  copy[key]=Buffer.from(JSON.stringify(value));
  assert.throws(()=>validateD100ClassicalExport(copy));rejected++;
}
const proof='d100ClassicalExportReplay';
for(const key of ['producer_writes','current_backend_used_as_input','tex_launched',
    'network_used','new_semantic_review','whole_backend_complete'])mutate(proof,v=>v[key]=true);
mutate(proof,v=>v.historical_registry_used=false);
mutate(proof,v=>v.runs.pop());
mutate(proof,v=>v.runs[1].label='a');
mutate(proof,v=>v.runs[0].outputs.pop());
mutate(proof,v=>v.runs[1].outputs[0].sha256='0'.repeat(64));
mutate(proof,v=>v.scope_counts.source_course_units=60);
mutate(proof,v=>v.scope_counts.source_files=119);
mutate(proof,v=>v.runs[0].validation.json_schema_validated_records=0);
mutate(proof,v=>v.runs[0].validation.source_projection.segment_record_count=0);
mutate(proof,v=>v.runs[0].validation.ledger_projection.correction_record_count=0);
mutate(proof,v=>v.runs[0].inputs=128);
mutate('d100ClassicalExportBinding',v=>v.inputs.pop());
console.log(JSON.stringify({state:'pass',rejected_mutations:rejected,records:23869,
  scope:'classical data export from current source and explicit historical registry; not BGK/PDF/semantic closure'}));
