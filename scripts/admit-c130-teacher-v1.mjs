import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/c130-teacher-v1',site='docs/backend/c130-teacher';
const load=async p=>JSON.parse(await readFile(resolve(root,p),'utf8'));
const fact=async p=>{const b=await readFile(resolve(root,p));return {path:p,bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')};};
const hosted=await load(site+'/teacher-validation.json');
assert.equal(hosted.schema,'c130-teacher-hosted/1');assert.equal(hosted.state,'pass');
assert.equal(hosted.counts.selectable_learning_items,227);assert.equal(hosted.counts.selectable_reader_exercises,203);
assert.equal(hosted.precise_selected_exercise_and_activity_alignment,true);
assert.equal(hosted.all_native_solution_alignment,false);assert.equal(hosted.unmapped_other_solution_sources,28);
for(const [name,value] of Object.entries(hosted.files))assert.deepEqual(await fact(site+'/'+name),{path:site+'/'+name,...value});
for(const [name,value] of Object.entries(hosted.evidence))assert.deepEqual(await fact(base+'/'+name),{path:base+'/'+name,...value});
const evidence=[];
for(const [kind,p] of [['c130_source_reader_mapping',base+'/validation.json'],['c130_planner_tests',base+'/ui-tests.json'],['c130_teacher_surface',site+'/teacher-validation.json']]){
 const f=await fact(p);evidence.push({kind,locator:p,bytes:f.bytes,sha256:f.sha256,verified_date:'2026-09-29'});
}
const path='backend/course-capsule-v1/authority/integration-overrides-v1.json';
const raw=await readFile(resolve(root,path),'utf8'),o=JSON.parse(raw),before=structuredClone(o);
const scope='203 latihan, 12 cek pemahaman beserta jawaban dan 12 kegiatan visual dipetakan ke PDF Bahasa Indonesia.';
const limitation='Dari 132 penyelesaian lain, 104 memiliki rujukan bagian teks dan 28 masih belum memiliki pemetaan halaman. Hasil solver tidak dijalankan ulang.';
const tool={tool_id:'c130.assignment_planner',label:'C130 · Perencana tugas Riset Operasi',
 href:'backend/c130-teacher/C130.teacher.html',action_kind:'reference',scope,state:'verified',primary:false,
 machine_data_is_learner_destination:false,page:await fact(site+'/C130.teacher.html'),
 resource:await fact(site+'/planner-model.json'),evidence:await fact(site+'/teacher-validation.json'),limitations:[limitation]};
o.learner_tools.C130=[...(o.learner_tools.C130??[]).filter(t=>t.tool_id!==tool.tool_id),tool];
o.native_capabilities.C130={...o.native_capabilities.C130,educator_unit_alignment:{status:'verified',evidence}};
const old=o.educator_evidence.C130??{},ids=['C130:teacher-id','C130:teacher-en'];
const resources=(old.resources??[]).filter(r=>!ids.includes(r.id));
for(const lang of ['id','en']){
 const name='C130.teacher'+(lang==='en'?'.en':'')+'.html',f=await fact(site+'/'+name);
 resources.push({id:'C130:teacher-'+lang,title:lang==='en'?'C130 · Operations Research assignment planner':'C130 · Perencana tugas Riset Operasi',
  resource_type:'teacher-guide',status:'verified',url:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c130-teacher/'+name,
  scope:lang==='en'?'203 exercises, twelve checkpoints with answers and twelve visual activities in the Indonesian PDF. Another 104 solution passages are mapped; 28 solution sources remain unmapped. No solver re-execution is claimed.':scope+' '+limitation,
  bytes:f.bytes,sha256:f.sha256});
}
const primary=resources.find(r=>r.id===ids[0]);
o.educator_evidence.C130={...old,status:'verified',verified_date:'2026-09-29',locator:primary.url,bytes:primary.bytes,sha256:primary.sha256,
 features:['exercise_bank','remix_selectors','activities_labs'],resources};
for(const key of Object.keys(before)){
 const a=structuredClone(before[key]),b=structuredClone(o[key]);
 if(['learner_tools','native_capabilities','educator_evidence'].includes(key)){delete a.C130;delete b.C130;}
 assert.deepEqual(a,b,'Unrelated override change '+key);
}
assert.equal(await readFile(resolve(root,path),'utf8'),raw,'Concurrent override edit');
await writeFile(resolve(root,path),JSON.stringify(o,null,2)+'\n');
const navPath='backend/authority/central-reader-navigation-v1.json';
const navRaw=await readFile(resolve(root,navPath),'utf8'),nav=JSON.parse(navRaw);
const entry={root:site,locale:'id',state:'current-shared-corpus-capability',documents:[
 {path:'C130.teacher.html',locale:'id',course_ids:['C130'],contents_paths:['C130.teacher.en.html']},
 {path:'C130.teacher.en.html',locale:'en',course_ids:['C130'],contents_paths:['C130.teacher.html']}]};
const index=nav.course_surfaces.findIndex(s=>s.root===site);if(index<0)nav.course_surfaces.push(entry);else nav.course_surfaces[index]=entry;
nav.summary.course_surface_roots=nav.course_surfaces.length;
nav.summary.course_surface_html_documents=nav.course_surfaces.reduce((n,s)=>n+s.documents.length,0);
nav.summary.classified_html_documents=nav.summary.reader_html_documents+nav.summary.gateway_html_documents+nav.summary.course_surface_html_documents+nav.summary.generic_html_documents;
nav.summary.navigation_overlay_documents=nav.summary.reader_html_documents+nav.summary.gateway_html_documents+nav.summary.course_surface_html_documents+nav.generic_surfaces.filter(s=>s.navigation_required).length;
assert.equal(await readFile(resolve(root,navPath),'utf8'),navRaw,'Concurrent navigation edit');
await writeFile(resolve(root,navPath),JSON.stringify(nav,null,2)+'\n');
console.log(JSON.stringify({state:'locally-admitted-pending-publication',role:'C130',selectable_items:227,unmapped_other_solutions:28}));
