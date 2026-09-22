import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {root,base,sha,json} from './build-d50-surface-v1.mjs';
const load=async p=>JSON.parse(await readFile(resolve(root,p),'utf8'));
const fact=async path=>{const b=await readFile(resolve(root,path));return {path,bytes:b.length,sha256:sha(b)};};
const tests=await load(base+'/delivery/tests.json');
assert.equal(tests.state,'pass');assert.equal(tests.native_units_preserved,1223);assert.equal(tests.negative_fixtures.length,7);
const validated=await load('docs/backend/d50/validation.json'),map=await load('docs/backend/d50/learning-map.json');
for(const f of validated.files)assert.deepEqual(await fact('docs/backend/d50/'+f.path),{...f,path:'docs/backend/d50/'+f.path});
const evidence=[];
for(const [kind,p] of [['d50_delivery_tests',base+'/delivery/tests.json'],['d50_reader_delivery',base+'/delivery/reader-delivery.json'],['d50_surface_validation','docs/backend/d50/validation.json']]){
  const f=await fact(p);evidence.push({kind,locator:p,bytes:f.bytes,sha256:f.sha256,verified_date:'2026-09-22'});
}
const path='backend/course-capsule-v1/authority/integration-overrides-v1.json',overrides=await load(path),before=structuredClone(overrides);
const scope='1.223 unit dan bagian dapat dipilih; 731 latihan/kemunculan soal; sumber solusi, 24 slot kosong, dan 119 identitas soal ujian tetap dibedakan.';
const tool={tool_id:'d50.open_learner_hub',label:'D50 · Geometri Diferensial',href:'backend/d50/index.html',action_kind:'course_reader',scope,
  state:'verified',primary:false,machine_data_is_learner_destination:false,page:await fact('docs/backend/d50/index.html'),
  resource:await fact('docs/backend/d50/learning-map.json'),evidence:await fact('docs/backend/d50/validation.json'),limitations:map.limitations.id};
overrides.learner_tools.D50=[...(overrides.learner_tools.D50??[]).filter(t=>t.tool_id!==tool.tool_id),tool];
overrides.native_capabilities.D50={...overrides.native_capabilities.D50,unit_identity:{status:'verified',evidence},educator_unit_alignment:{status:'verified',evidence}};
const old=overrides.educator_evidence.D50??{},resources=(old.resources??[]).filter(r=>!['D50:educator-hub-v1','D50:educator-hub-en-v1'].includes(r.id));
for(const lang of ['id','en']){
  const file=lang==='en'?'teacher.en.html':'teacher.html',f=await fact('docs/backend/d50/'+file);
  resources.push({id:lang==='en'?'D50:educator-hub-en-v1':'D50:educator-hub-v1',title:lang==='en'?'D50 teaching-plan selector — English interface, Indonesian reading':'Pemilih unit dan latihan D50 untuk pengajar',
    resource_type:'teacher-guide',status:'verified',url:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d50/'+file,scope,bytes:f.bytes,sha256:f.sha256});
}
const teacher=await fact('docs/backend/d50/teacher.html');
overrides.educator_evidence.D50={...old,status:'verified',verified_date:'2026-09-22',locator:resources.find(r=>r.id==='D50:educator-hub-v1').url,
  bytes:teacher.bytes,sha256:teacher.sha256,features:[...new Set([...(old.features??[]),'exercise_bank','remix_selectors','staged_hints_answers_solutions'])],resources};
for(const section of Object.keys(before)){
  const a=structuredClone(before[section]),b=structuredClone(overrides[section]);
  if(['learner_tools','native_capabilities','educator_evidence'].includes(section)){delete a.D50;delete b.D50;}
  assert.deepEqual(a,b,'Unrelated override changed: '+section);
}
await writeFile(resolve(root,path),json(overrides));
console.log(json({state:'admitted',course:'D50',unrelated_overrides_preserved:true}));
