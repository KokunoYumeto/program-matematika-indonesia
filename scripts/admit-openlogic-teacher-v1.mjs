import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/openlogic-teacher-v1',site='docs/backend/openlogic-teacher';
const load=async p=>JSON.parse(await readFile(resolve(root,p),'utf8'));
const fact=async p=>{const b=await readFile(resolve(root,p));return {path:p,bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')};};
const hosted=await load(site+'/teacher-validation.json');
assert.equal(hosted.schema,'openlogic-teacher-hosted/1');assert.equal(hosted.state,'pass');
assert.deepEqual(hosted.counts,{source_problems:438,printed_occurrences:442,rendered_source_problems:427,main_occurrences:411,supplement_occurrences:31,additional_reused_occurrences:15,tag_disabled:10,missing_deferred_flush:1});
assert.equal(hosted.precise_rendered_exercise_alignment,true);assert.equal(hosted.solutions_audited,false);
for(const f of hosted.files)assert.deepEqual(await fact(site+'/'+f.path),{...f,path:site+'/'+f.path});
for(const [name,f] of Object.entries(hosted.evidence))assert.deepEqual(await fact(base+'/'+name),{...f,path:base+'/'+name});
const evidence=[];
for(const [kind,p] of [['openlogic_exercise_mapping',base+'/mapping-tests.json'],['openlogic_planner_tests',base+'/build-tests.json'],['openlogic_teacher_surface',site+'/teacher-validation.json']]){
 const f=await fact(p);evidence.push({kind,locator:p,bytes:f.bytes,sha256:f.sha256,verified_date:'2026-09-28'});
}
const p='backend/course-capsule-v1/authority/integration-overrides-v1.json';
const raw=await readFile(resolve(root,p),'utf8'),o=JSON.parse(raw),before=structuredClone(o);
const model=await load(site+'/C80.teacher.json');
const scope='442 kemunculan tercetak dari 427 soal sumber; 10 soal dinonaktifkan tag edisi dan satu tidak tercetak dicatat terpisah. Jawaban dan penyelesaian belum diaudit.';
const tool={tool_id:'c80.openlogic_assignment_planner',label:'C80 · Perencana tugas OpenLogic',
 href:'backend/openlogic-teacher/C80.teacher.html',action_kind:'reference',scope,state:'verified',primary:false,
 machine_data_is_learner_destination:false,page:await fact(site+'/C80.teacher.html'),
 resource:await fact(site+'/C80.teacher.json'),evidence:await fact(site+'/teacher-validation.json'),limitations:[model.limitations.id]};
o.learner_tools.C80=[...(o.learner_tools.C80??[]).filter(t=>t.tool_id!==tool.tool_id),tool];
o.native_capabilities.C80={...o.native_capabilities.C80,educator_unit_alignment:{status:'verified',evidence}};
const old=o.educator_evidence.C80??{},ids=['C80:openlogic-teacher-id','C80:openlogic-teacher-en'];
const resources=(old.resources??[]).filter(r=>!ids.includes(r.id));
for(const lang of ['id','en']){
 const name='C80.teacher'+(lang==='en'?'.en':'')+'.html',f=await fact(site+'/'+name);
 resources.push({id:'C80:openlogic-teacher-'+lang,title:lang==='en'?'C80 · OpenLogic assignment planner':'C80 · Perencana tugas OpenLogic',
  resource_type:'teacher-guide',status:'verified',url:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/openlogic-teacher/'+name,
  scope:lang==='en'?'442 printed occurrences from 427 source exercises; ten tag-disabled and one unflushed exercise retained separately. Answers and solutions remain unaudited.':scope,
  bytes:f.bytes,sha256:f.sha256});
}
const primary=resources.find(r=>r.id===ids[0]);
o.educator_evidence.C80={...old,status:'verified',verified_date:'2026-09-28',locator:primary.url,bytes:primary.bytes,sha256:primary.sha256,
 features:[...new Set([...(old.features??[]),'exercise_bank','remix_selectors'])],resources};
for(const key of Object.keys(before)){
 const a=structuredClone(before[key]),c=structuredClone(o[key]);
 if(['learner_tools','native_capabilities','educator_evidence'].includes(key)){delete a.C80;delete c.C80;}
 assert.deepEqual(a,c,'Unrelated override change '+key);
}
assert.equal(await readFile(resolve(root,p),'utf8'),raw,'Concurrent override edit');
await writeFile(resolve(root,p),JSON.stringify(o,null,2)+'\n');
const navPath='backend/authority/central-reader-navigation-v1.json';
const navRaw=await readFile(resolve(root,navPath),'utf8'),nav=JSON.parse(navRaw);
const entry={root:site,locale:'id',state:'current-shared-corpus-capability',documents:[
 {path:'C80.teacher.html',locale:'id',course_ids:['C80'],contents_paths:['C80.teacher.en.html']},
 {path:'C80.teacher.en.html',locale:'en',course_ids:['C80'],contents_paths:['C80.teacher.html']}]};
const i=nav.course_surfaces.findIndex(s=>s.root===site);if(i<0)nav.course_surfaces.push(entry);else nav.course_surfaces[i]=entry;
nav.summary.course_surface_roots=nav.course_surfaces.length;
nav.summary.course_surface_html_documents=nav.course_surfaces.reduce((n,s)=>n+s.documents.length,0);
nav.summary.classified_html_documents=nav.summary.reader_html_documents+nav.summary.gateway_html_documents+nav.summary.course_surface_html_documents+nav.summary.generic_html_documents;
nav.summary.navigation_overlay_documents=nav.summary.reader_html_documents+nav.summary.gateway_html_documents+nav.summary.course_surface_html_documents+nav.generic_surfaces.filter(s=>s.navigation_required).length;
assert.equal(await readFile(resolve(root,navPath),'utf8'),navRaw,'Concurrent navigation edit');
await writeFile(resolve(root,navPath),JSON.stringify(nav,null,2)+'\n');
console.log(JSON.stringify({state:'locally-admitted-pending-publication',role:'C80',counts:hosted.counts}));
