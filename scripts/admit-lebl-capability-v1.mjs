import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/lebl-capability-v1';
const load=async path=>JSON.parse(await readFile(resolve(root,path),'utf8'));
const identity=async path=>{const data=await readFile(resolve(root,path));return {path,bytes:data.length,sha256:createHash('sha256').update(data).digest('hex')};};
const manifest=await load(base+'/manifest.json'), validation=await load(base+'/validation.json');
const model=await load('docs/backend/lebl/learning-map.json');
assert.equal(validation.state,'pass');
assert.equal(validation.manifest_sha256,(await identity(base+'/manifest.json')).sha256);
for(const flag of ['schema_validation','isolated_two_build_byte_identity','learner_teacher_shared_identity','frozen_intake_matches_pinned_native_stream','native_support_state_preserved'])assert.equal(validation[flag],true,flag);
for(const fact of [...manifest.inputs,...manifest.outputs])assert.deepEqual(await identity(fact.path),fact);
assert.deepEqual(Object.keys(model.roles),['B70','C10','C20','C50']);
const evidence=[];
for(const [kind,path] of [['central_adapter_manifest',base+'/manifest.json'],['deterministic_validation_receipt',base+'/validation.json'],['pinned_native_stream_projection',base+'/native-evidence-binding.json']]){
  const {bytes,sha256}=await identity(path);evidence.push({kind,locator:path,bytes,sha256,verified_date:'2026-09-04'});
}
const target='backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides=await load(target);
for(const [role,profile] of Object.entries(model.roles)){
  assert.ok(!overrides.semantic_adapters[role]||overrides.semantic_adapters[role].contract_version===model.contract,'Unexpected existing adapter for '+role);
  const exercises=model.units.filter(u=>u.kind==='exercise'&&u.books.some(b=>profile.books.includes(b))).length;
  const scope=`${exercises} rekaman latihan dalam keluarga Lebl; identitas sumber dipertahankan, unit yang bertumpang tindih bukan beban unik`;
  overrides.semantic_adapters[role]={status:'verified',contract_version:model.contract,mapping_scope:'loss_accounted_native_metadata_with_shared_learner_teacher_and_terminology_views',evidence};
  overrides.native_capabilities[role]={...overrides.native_capabilities[role],unit_identity:{status:'verified',evidence},educator_unit_alignment:{status:'verified',evidence},terminology:{status:'verified',evidence}};
  const tools=[];
  for(const [suffix,label,filename,action_kind] of [
    ['exercise-map','Buku, latihan, dan dukungan sumber',role+'.html','practice_diagnostic_map'],
    ['educator-map','Susun rencana kegiatan pengajar',role+'-pengajar.html','reference'],
    ['terminology','Istilah dan alternatif keluarga Lebl','istilah.html','reference'],
  ])tools.push({tool_id:role.toLowerCase()+'-lebl-'+suffix+'-v1',label,href:'backend/lebl/'+filename,action_kind,scope,state:'verified',primary:false,machine_data_is_learner_destination:false,
    page:await identity('docs/backend/lebl/'+filename),resource:await identity('docs/backend/lebl/learning-map.json'),evidence:await identity('docs/backend/lebl/validation.json'),
    limitations:['Bahasa Indonesia; tampilan Inggris tidak mengubah bahasa alat ini.','Tujuan PDF mengikuti judul bagian, bukan lokasi persis latihan.','Solusi belum dipetakan tetap berstatus belum diketahui; tautan bukan sertifikasi solusi lengkap.','Navigasi bisa disimpan luring; unduh PDF secara terpisah.']});
  assert.ok(!overrides.learner_tools[role]||overrides.learner_tools[role].every(t=>tools.some(x=>x.tool_id===t.tool_id)),'Preserve unrelated learner tools');
  overrides.learner_tools[role]=tools;
  const teacher=await identity('docs/backend/lebl/'+role+'-pengajar.html');
  const teacherUrl='https://kokunoyumeto.github.io/program-matematika-indonesia/backend/lebl/'+role+'-pengajar.html';
  assert.ok(!overrides.educator_evidence[role]||overrides.educator_evidence[role].resources.every(r=>r.id===role+':lebl-educator-v1'),'Preserve unrelated educator materials');
  overrides.educator_evidence[role]={status:'verified',verified_date:'2026-09-04',locator:teacherUrl,bytes:teacher.bytes,sha256:teacher.sha256,
    features:['exercise_bank','solution_provenance'],resources:[{id:role+':lebl-educator-v1',title:'Bank latihan dan penyusun kegiatan '+role,resource_type:'teacher-guide',status:'verified',url:teacherUrl,scope,bytes:teacher.bytes,sha256:teacher.sha256}]};
}
await writeFile(resolve(root,target),JSON.stringify(overrides,null,2)+'\n');
console.log(JSON.stringify({state:'pass',admitted_roles:Object.keys(model.roles),contract:model.contract,public_release_verified:false}));
