import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/geometry-capability-v1';
const load=async path=>JSON.parse(await readFile(resolve(root,path),'utf8'));
const identity=async path=>{const bytes=await readFile(resolve(root,path));return {path,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')};};
const manifest=await load(base+'/manifest.json'),validation=await load(base+'/validation.json');
assert.equal(validation.state,'pass');assert.equal(validation.manifest_sha256,(await identity(base+'/manifest.json')).sha256);
for(const key of ['schema_validation','all_native_projected_fields_preserved','source_and_pilot_bindings_verified','concept_graph_acyclic','native_pending_states_preserved','learner_teacher_shared_identity','isolated_two_build_byte_identity','reader_byte_identity_preserved'])assert.equal(validation[key],true,key);
for(const item of [...manifest.inputs,...manifest.outputs])assert.deepEqual(await identity(item.path),item);
const evidence=[];
for(const [kind,path] of [['central_adapter_manifest',base+'/manifest.json'],['deterministic_validation_receipt',base+'/validation.json'],['native_metadata_intake',base+'/input/source-lock.json']]){
  const {bytes,sha256}=await identity(path);evidence.push({kind,locator:path,bytes,sha256,verified_date:'2026-09-04'});
}
const target='backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides=await load(target);
assert.ok(!overrides.semantic_adapters.C100||overrides.semantic_adapters.C100.contract_version===manifest.contract);
overrides.semantic_adapters.C100={status:'verified',contract_version:manifest.contract,mapping_scope:'native_concepts_terms_figures_corrections_and_existing_unit_support_with_explicit_precision_and_pending_states',evidence};
overrides.native_capabilities.C100={...overrides.native_capabilities.C100,unit_identity:{status:'verified',evidence},educator_unit_alignment:{status:'verified',evidence},terminology:{status:'verified',evidence}};
const scope='939 unit tetap; 491 konsep, 432 istilah, 214 deskripsi gambar, 285 permukaan latihan (253 soal induk). Status QA dan batas lokasi asli dipertahankan.';
const tools=[];
for(const [suffix,label,filename,action_kind] of [
  ['learning-map','Geometri: bacaan, latihan, konsep dan istilah','C100.html','practice_diagnostic_map'],
  ['educator-map','Susun rencana kegiatan geometri','pengajar.html','reference']
])tools.push({tool_id:'c100-geometry-'+suffix+'-v1',label,href:'backend/geometry/'+filename,action_kind,scope,state:'verified',primary:false,machine_data_is_learner_destination:false,
  page:await identity('docs/backend/geometry/'+filename),resource:await identity('docs/backend/geometry/learning-map.json'),evidence:await identity('docs/backend/geometry/validation.json'),
  limitations:['Bahasa Indonesia; tampilan Inggris tidak mengubah bahasa isi.','348 pemetaan konsep masih berstatus menunggu QA sumber; tiga tujuan konsep adalah bab induk.','Solusi tambahan mandiri memakai PDF lengkap, bukan halaman solusi tertentu.','Pilihan kegiatan lokal; pemetaan bukan asesmen kemampuan tervalidasi.']});
assert.ok(!overrides.learner_tools.C100||overrides.learner_tools.C100.every(t=>tools.some(x=>x.tool_id===t.tool_id)),'Preserve unrelated tools');
overrides.learner_tools.C100=tools;
const old=overrides.educator_evidence.C100;
const teacher=await identity('docs/backend/geometry/pengajar.html');
const url='https://kokunoyumeto.github.io/program-matematika-indonesia/backend/geometry/pengajar.html';
const resources=(old?.resources??[]).filter(r=>r.id!=='C100:geometry-educator-v1');
if(old?.status==='available_unverified'&&old.locator&&!resources.some(r=>r.id==='C100:native-educator-observation'))resources.push({id:'C100:native-educator-observation',title:'Catatan materi pengajar pada edisi sumber',resource_type:'teacher-guide',status:'available_unverified',url:old.locator,scope:'Observasi sumber sebelumnya; fitur kegiatan dan akomodasi belum diverifikasi oleh adapter ini.'});
resources.push({id:'C100:geometry-educator-v1',title:'Penyusun kegiatan geometri berbasis konsep dan latihan',resource_type:'teacher-guide',status:'verified',url,scope,bytes:teacher.bytes,sha256:teacher.sha256});
overrides.educator_evidence.C100={status:'verified',verified_date:'2026-09-04',locator:url,bytes:teacher.bytes,sha256:teacher.sha256,features:['exercise_bank','solution_provenance'],resources};
await writeFile(resolve(root,target),JSON.stringify(overrides,null,2)+'\n');
console.log(JSON.stringify({state:'pass',admitted_roles:['C100'],contract:manifest.contract,public_release_verified:false}));
