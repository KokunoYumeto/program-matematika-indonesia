import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/d110-surface-v1';
const load=async path=>JSON.parse(await readFile(resolve(root,path),'utf8'));
const fact=async path=>{const b=await readFile(resolve(root,path));return {path,bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')};};
const tests=await load(base+'/tests.json'),hosted=await load('docs/backend/d110/validation.json');
assert.equal(tests.state,'pass');assert.equal(hosted.state,'pass');
assert.deepEqual(hosted.counts,tests.counts);assert.equal(tests.native_units_all_accounted,true);
assert.equal(tests.all_native_support_payloads_preserved,true);
assert.equal(tests.counts.units,2177);assert.equal(tests.counts.solution_fragments_with_both_texts,330);
for(const f of hosted.files)assert.deepEqual(await fact('docs/backend/d110/'+f.path),{...f,path:'docs/backend/d110/'+f.path});
const evidence=[];
for(const [kind,path] of [['d110_consumer_tests',base+'/tests.json'],['d110_reader_witness',base+'/input/reader-witness.json'],['d110_hosted_surface','docs/backend/d110/validation.json']]){
  const f=await fact(path);evidence.push({kind,locator:path,bytes:f.bytes,sha256:f.sha256,verified_date:'2026-09-26'});
}
const target='backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides=await load(target),before=structuredClone(overrides);
const map=await load('docs/backend/d110/learning-map.json');
const scope='2.177 unit, 13 bab, 43 bagian dan 243 unit bertanda latihan; 330 relasi solusi/pendukung dipertahankan, termasuk enam unit tanpa relasi solusi.';
const tool={tool_id:'d110.open_learner_hub',label:'D110 · Matematika dalam Lean',href:'backend/d110/index.html',action_kind:'course_reader',scope,state:'verified',primary:false,
  machine_data_is_learner_destination:false,page:await fact('docs/backend/d110/index.html'),resource:await fact('docs/backend/d110/learning-map.json'),evidence:await fact('docs/backend/d110/validation.json'),limitations:map.limitations.id};
overrides.learner_tools.D110=[...(overrides.learner_tools.D110??[]).filter(t=>t.tool_id!==tool.tool_id),tool];
overrides.native_capabilities.D110={...overrides.native_capabilities.D110,unit_identity:{status:'verified',evidence},educator_unit_alignment:{status:'verified',evidence}};
const old=overrides.educator_evidence.D110??{},resources=(old.resources??[]).filter(r=>!['D110:educator-hub-v1','D110:educator-hub-en-v1'].includes(r.id));
for(const lang of ['id','en']){
  const file=lang==='en'?'teacher.en.html':'teacher.html',f=await fact('docs/backend/d110/'+file);
  resources.push({id:lang==='en'?'D110:educator-hub-en-v1':'D110:educator-hub-v1',title:lang==='en'?'D110 study and teaching plans — English':'Pemilih unit dan latihan D110 untuk pengajar',resource_type:'teacher-guide',status:'verified',
    url:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d110/'+file,scope,bytes:f.bytes,sha256:f.sha256});
}
const teacher=await fact('docs/backend/d110/teacher.html');
overrides.educator_evidence.D110={...old,status:'verified',verified_date:'2026-09-26',locator:resources.find(r=>r.id==='D110:educator-hub-v1').url,bytes:teacher.bytes,sha256:teacher.sha256,
  features:[...new Set([...(old.features??[]),'exercise_bank','remix_selectors','staged_hints_answers_solutions'])],resources};
for(const section of Object.keys(before)){
  const a=structuredClone(before[section]),b=structuredClone(overrides[section]);
  if(['learner_tools','native_capabilities','educator_evidence'].includes(section)){delete a.D110;delete b.D110;}
  assert.deepEqual(a,b,'Unrelated override changed: '+section);
}
await writeFile(resolve(root,target),JSON.stringify(overrides,null,2)+'\n');
console.log(JSON.stringify({state:'admitted',course:'D110',unrelated_overrides_preserved:true}));
