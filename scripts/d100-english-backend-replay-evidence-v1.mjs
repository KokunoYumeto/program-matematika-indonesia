import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const base='backend/course-capsule-v1/adapters/d100-native-production-v1/english';
const lanes=['classical','bgk','original'];
const sourceCounts={classical:120,bgk:122,original:32};
const inputCounts={classical:285,bgk:286,original:286};
const sourceArchive='5f64ad7ca16ca771eec63eee880221d57ae6183b845e7486d0480e104a086a9a';
const backendArchive='38fd910c1e27c9faf66ffc69b3758b44724a2775f4b93ba495da4ea43aedfbbb';
// Exact output inventories read from that published archive, including each
// manifest itself. A self-consistently resealed local receipt cannot change them.
const outputInventoryPins={
  classical:'1ad89e15162fd215cbe1ecf4fdaa5005ffbcf9d26f21639a23c493f4caedfb8c',
  bgk:'0842330cd6d921a6e74a81c6b7de2c3dd90913e530ebc25cfee660dcf8634847',
  original:'f1bceff4e0e75de0aec20f25a4c1bebc5ecc69dbeb54284310d9b0902599e744',
};
const hash=b=>createHash('sha256').update(b).digest('hex');
export const d100EnglishReplayPaths=Object.fromEntries(lanes.flatMap(lane=>[
  [`d100English${lane}Binding`,`${base}/${lane}-inputs.json`],
  [`d100English${lane}Replay`,`${base}/${lane}-replay.json`],
]));
export function validateD100EnglishReplay(raw){
  const summaries=[];
  for(const lane of lanes){
    const bindingBytes=raw[`d100English${lane}Binding`];
    const binding=JSON.parse(bindingBytes), proof=JSON.parse(raw[`d100English${lane}Replay`]);
    assert.equal(binding.schema,'d100-english-backend-inputs/1');assert.equal(binding.lane,lane);
    assert.equal(proof.schema,'d100-english-backend-replay/1');assert.equal(proof.lane,lane);
    assert.equal(proof.state,'pass');assert.equal(proof.language,'en');
    assert.deepEqual(proof.input_binding,{bytes:bindingBytes.length,sha256:hash(bindingBytes)});
    assert.equal(proof.native_english_source_files,sourceCounts[lane]);
    assert.equal(proof.historical_qa_source_closure,274);
    assert.equal(proof.declared_input_files,inputCounts[lane]);
    assert.equal(binding.inputs.length,inputCounts[lane]);
    const inputs=new Map(binding.inputs.map(row=>[row.path,row]));
    assert.equal(inputs.size,binding.inputs.length);
    for(const p of inputs.keys()){
      assert.ok(!p.includes('\\')&&!p.startsWith('/')&&!p.includes(':')&&!p.split('/').includes('..'));
      assert.ok(!p.startsWith('backend/english/release-')&&!p.startsWith('backend/english/final/'),'Existing English output used as input');
    }
    assert.equal(binding.inputs.filter(r=>r.path.startsWith('source/en/')).length,274);
    assert.ok(inputs.has('scripts/english/export_backend_en.py'));
    assert.ok(inputs.has('qa/english/TRANSLATION_INTEGRATION_QA.json'));
    assert.deepEqual(binding.archives,proof.public_archives);
    assert.deepEqual(Object.keys(binding.archives).sort(),['07_English-Edition_source.zip','08_English-Edition_native-backend.zip']);
    for(const [name,sha,bytes] of [['07_English-Edition_source.zip',sourceArchive,1248638],['08_English-Edition_native-backend.zip',backendArchive,9621548]]){
      assert.deepEqual(binding.archives[name],{bytes,sha256:sha,url:'https://github.com/KokunoYumeto/algebraic-geometry-bridge-id/releases/download/en-v1.0.0/'+name});
    }
    for(const key of ['network_used_by_replay','producer_files_changed','tex_or_pdf_build','new_translation_or_semantic_canon_review','overall_backend_complete'])assert.equal(proof[key],false,key);
    assert.equal(proof.historical_review_claim_reproduced_not_independently_endorsed,true);
    assert.equal(proof.hard_memory_limit_bytes,2147483648);
    assert.ok(Number.isSafeInteger(proof.peak_process_commit_bytes)&&proof.peak_process_commit_bytes>0&&proof.peak_process_commit_bytes<=2147483648);
    assert.equal(proof.runs.length,2);assert.deepEqual(proof.runs[0],proof.runs[1]);
    assert.equal(Object.keys(binding.expected_outputs).length,20);
    const ordered=Object.fromEntries(Object.entries(binding.expected_outputs)
      .sort(([a],[b])=>a.localeCompare(b,'en')).map(([p,f])=>[p,{bytes:f.bytes,sha256:f.sha256}]));
    assert.equal(hash(Buffer.from(JSON.stringify(ordered))),outputInventoryPins[lane],'Published output inventory drift');
    for(const run of proof.runs){
      assert.equal(run.exact_public_manifest_match,true);assert.equal(run.native_reverse_equal,true);assert.equal(run.inputs_unchanged,true);
      assert.deepEqual(run.output_files,binding.expected_outputs);
      assert.equal(run.runtime_reads.length,inputs.size);
      assert.equal(new Set(run.runtime_reads.map(r=>r.path)).size,inputs.size);
      for(const fact of run.runtime_reads)assert.deepEqual(fact,inputs.get(fact.path),'Unbound runtime read');
    }
    summaries.push({lane,source_files:sourceCounts[lane],declared_inputs:inputs.size,output_files:20,
      native_records:Object.values(proof.runs[0].counts).reduce((a,b)=>a+b,0),
      peak_process_commit_bytes:proof.peak_process_commit_bytes,byte_identical_runs:2});
  }
  return {schema:'d100-english-production-evidence/1',state:'pass',course_id:'D100',locale:'en',
    lanes:summaries,source_files:274,isolated_runs:6,output_files:60,producer_writes:false,
    semantic_canon_review:false,fresh_html_or_pdf_build:false,whole_backend_complete:false,
    scope:'English native backend exports, including the reversible common-data projection; not rendered-book builds or a new review of historical mathematical claims.'};
}
export async function loadD100EnglishReplay(root){
  const raw={};for(const [key,path] of Object.entries(d100EnglishReplayPaths))raw[key]=await readFile(resolve(root,path));
  return {report:validateD100EnglishReplay(raw),raw,evidence:Object.entries(d100EnglishReplayPaths).map(([key,path])=>({path,bytes:raw[key].length,sha256:hash(raw[key])}))};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
  const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
  const token=process.argv[2];assert.match(token,/^\d+$/,'Supply the exact local replay batch ID');
  const raw={};for(const lane of lanes){
    raw[`d100English${lane}Binding`]=await readFile(resolve(root,`work/d100-english-${lane}-${token}/INPUT_BINDING.json`));
    raw[`d100English${lane}Replay`]=await readFile(resolve(root,`work/d100-english-${lane}-${token}/REPLAY.json`));
  }
  const report=validateD100EnglishReplay(raw);
  await mkdir(resolve(root,base),{recursive:true});
  for(const [key,path] of Object.entries(d100EnglishReplayPaths))await writeFile(resolve(root,path),raw[key]);
  console.log(JSON.stringify(report));
}
