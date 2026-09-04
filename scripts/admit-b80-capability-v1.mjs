import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname,resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { sha256 } from './native-catalog-exchange-v1.mjs';
const project=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/b80-capability-v1';
const identity=async path=>{const bytes=await readFile(resolve(project,path));return {path,bytes:bytes.length,sha256:sha256(bytes)};};
const manifest=JSON.parse(await readFile(resolve(project,base,'manifest.json'),'utf8'));
const receipt=JSON.parse(await readFile(resolve(project,base,'validation.json'),'utf8'));
assert.equal(receipt.state,'pass');assert.equal(receipt.manifest_sha256,(await identity(base+'/manifest.json')).sha256);
assert.equal(receipt.isolated_two_build_byte_identity,true);assert.equal(receipt.learner_teacher_shared_identity,true);
for(const fact of [...manifest.inputs,...manifest.outputs]) assert.deepEqual(await identity(fact.path),fact);
const evidence=[];
for(const [kind,path] of [['central_adapter_manifest',base+'/manifest.json'],['deterministic_validation_receipt',base+'/validation.json']]){
  const {bytes,sha256}=await identity(path);evidence.push({kind,locator:path,bytes,sha256,verified_date:'2026-09-04'});
}
const overridePath=resolve(project,'backend/course-capsule-v1/authority/integration-overrides-v1.json');
const overrides=JSON.parse(await readFile(overridePath,'utf8'));
assert.ok(!overrides.semantic_adapters.B80||overrides.semantic_adapters.B80.contract_version==='course-learning-capability/1','Unexpected B80 adapter: reconcile first');
overrides.semantic_adapters.B80={status:'verified',contract_version:'course-learning-capability/1',
  mapping_scope:'reversible_native_catalog_with_shared_learner_educator_views',evidence};
overrides.native_capabilities.B80={...overrides.native_capabilities.B80,
  unit_identity:{status:'verified',evidence},educator_unit_alignment:{status:'verified',evidence}};
const tools=[];
for(const [tool_id,label,filename,action_kind] of [
  ['b80-exercise-map-v1','Unit, latihan, dan pemeriksaan','B80.html','practice_diagnostic_map'],
  ['b80-educator-map-v1','Panduan kegiatan untuk pengajar','B80-pengajar.html','reference'],
]){
  tools.push({tool_id,label,href:'backend/b80/'+filename,action_kind,
    scope:'14 unit, 75 latihan, 4 laboratorium; identitas dan jalur prasyarat native dipertahankan',
    state:'verified',primary:false,machine_data_is_learner_destination:false,
    page:await identity('docs/backend/b80/'+filename),resource:await identity('docs/backend/b80/learning-map.json'),
    evidence:await identity('docs/backend/b80/validation.json'),
    limitations:['Bukan mesin eksekusi Python/SageMath atau penilaian otomatis.','Pelajaran tetap di pembaca native; tautan eksternal memerlukan koneksi atau unduhan tersendiri.','Hanya Bahasa Indonesia; tidak mengklaim terjemahan Inggris.']});
}
overrides.learner_tools.B80=tools;
const teacher=await identity('docs/backend/b80/B80-pengajar.html');
const teacherUrl='https://kokunoyumeto.github.io/program-matematika-indonesia/backend/b80/B80-pengajar.html';
overrides.educator_evidence.B80={status:'verified',verified_date:'2026-09-04',locator:teacherUrl,bytes:teacher.bytes,sha256:teacher.sha256,
  features:['outcome_evidence_map','lesson_sequences','exercise_bank','staged_hints_answers_solutions','activities_labs','solution_provenance'],
  resources:[{id:'B80:educator-map-v1',title:'Panduan unit dan kegiatan untuk pengajar B80',resource_type:'teacher-guide',
    status:'verified',url:teacherUrl,scope:'14 unit dan 75 latihan dengan identitas bersama serta 4 laboratorium',bytes:teacher.bytes,sha256:teacher.sha256}]};
await writeFile(overridePath,JSON.stringify(overrides,null,2)+'\n');
console.log(JSON.stringify({state:'pass',course:'B80',tool_bindings:tools.length,public_release_verified:false,contract_2_3_1_claimed:false}));
