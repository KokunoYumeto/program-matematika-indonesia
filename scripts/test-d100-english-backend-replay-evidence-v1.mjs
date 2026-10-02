import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadD100EnglishReplay,validateD100EnglishReplay} from './d100-english-backend-replay-evidence-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const {raw,report}=await loadD100EnglishReplay(root);
assert.equal(report.source_files,274);assert.equal(report.output_files,60);assert.equal(report.whole_backend_complete,false);
const cases=[];
for(const [name,mutate] of [
 ['semantic_upgrade',p=>p.new_translation_or_semantic_canon_review=true],
 ['whole_backend_upgrade',p=>p.overall_backend_complete=true],
 ['rendered_build_upgrade',p=>p.tex_or_pdf_build=true],
 ['wrong_source_scope',p=>p.native_english_source_files=31],
 ['one_run_only',p=>p.runs.pop()],
 ['different_second_run',p=>p.runs[1].output_files['records.jsonl'].sha256='0'.repeat(64)],
 ['no_exact_manifest',p=>p.runs.forEach(r=>r.exact_public_manifest_match=false)],
 ['unbound_native_read',p=>p.runs.forEach(r=>r.runtime_reads[0].path='undeclared')],
 ['unbounded_memory',p=>p.hard_memory_limit_bytes=0],
 ['binding_identity_drift',p=>p.input_binding.sha256='0'.repeat(64)],
 ['invented_reverse_equality',p=>p.runs.forEach(r=>r.native_reverse_equal=false)],
]){
 const changed={...raw},p=JSON.parse(changed.d100EnglishoriginalReplay);mutate(p);
 changed.d100EnglishoriginalReplay=Buffer.from(JSON.stringify(p));
 assert.throws(()=>validateD100EnglishReplay(changed),undefined,name);cases.push(name);
}
// Reseal the binding so the output-as-input rejection is not merely a hash failure.
const changed={...raw},b=JSON.parse(changed.d100EnglishoriginalBinding),p=JSON.parse(changed.d100EnglishoriginalReplay);
b.inputs[0].path='backend/english/final/original/records.jsonl';
changed.d100EnglishoriginalBinding=Buffer.from(JSON.stringify(b));
p.input_binding={bytes:changed.d100EnglishoriginalBinding.length,sha256:createHash('sha256').update(changed.d100EnglishoriginalBinding).digest('hex')};
changed.d100EnglishoriginalReplay=Buffer.from(JSON.stringify(p));
assert.throws(()=>validateD100EnglishReplay(changed),/Existing English output/);cases.push('resealed_output_as_input');
const resealed={...raw},binding=JSON.parse(raw.d100EnglishoriginalBinding),proof=JSON.parse(raw.d100EnglishoriginalReplay);
binding.expected_outputs['unit.jsonl'].sha256='0'.repeat(64);
for(const run of proof.runs)run.output_files['unit.jsonl'].sha256='0'.repeat(64);
resealed.d100EnglishoriginalBinding=Buffer.from(JSON.stringify(binding));
proof.input_binding={bytes:resealed.d100EnglishoriginalBinding.length,sha256:createHash('sha256').update(resealed.d100EnglishoriginalBinding).digest('hex')};
resealed.d100EnglishoriginalReplay=Buffer.from(JSON.stringify(proof));
assert.throws(()=>validateD100EnglishReplay(resealed),/Published output inventory drift/);cases.push('resealed_invented_output_inventory');
console.log(JSON.stringify({state:'pass',lanes:3,source_files:274,negative_fixtures:cases}));
