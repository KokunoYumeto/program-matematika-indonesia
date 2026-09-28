import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/judson-teacher-v1',roles=['C30','C40'];
const load=async p=>JSON.parse(await readFile(resolve(root,p),'utf8'));
const fact=async p=>{const b=await readFile(resolve(root,p));return {path:p,bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')};};
const tests=await load(base+'/tests.json'),hosted=await load('docs/backend/judson/teacher-validation.json');
assert.equal(tests.state,'pass');assert.equal(hosted.state,'pass');
assert.equal(tests.native_checks.all_native_exercises,913);
assert.equal(tests.native_checks.all_native_support_edges,329);
assert.equal(tests.native_checks.source_archive_rehashed,true);
assert.deepEqual(hosted.course_counts,{C30:610,C40:303});assert.deepEqual(hosted.course_counts,tests.counts);
assert.deepEqual(hosted.support_counts,{supplied_hints:213,empty_response_slots:116,supplied_responses:0,supplied_solutions:0});
for(const f of hosted.files)assert.deepEqual(await fact('docs/backend/judson/'+f.path),{...f,path:'docs/backend/judson/'+f.path});
const evidence=[];
for(const [kind,path] of [['judson_teacher_mapping_tests',base+'/tests.json'],['judson_teacher_source_lock',base+'/input/source-lock.json'],['judson_teacher_hosted_surface','docs/backend/judson/teacher-validation.json']]){
 const f=await fact(path);evidence.push({kind,locator:path,bytes:f.bytes,sha256:f.sha256,verified_date:'2026-09-28'});
}
const path='backend/course-capsule-v1/authority/integration-overrides-v1.json';
const original=await readFile(resolve(root,path),'utf8'),o=JSON.parse(original),before=structuredClone(o);
for(const role of roles){
 const map=await load(`docs/backend/judson/${role}.teacher.json`);
 const scope=`${map.exercise_count} identitas soal sumber/terjemahan dan lokasi pembaca; ${map.hint_count} petunjuk berisi materi; ${map.response_slot_count} ruang respons kosong, bukan jawaban.`;
 const tool={tool_id:role.toLowerCase()+'.judson_assignment_planner',label:role+' · Perencana tugas aljabar abstrak',href:`backend/judson/${role}.teacher.html`,action_kind:'reference',scope,state:'verified',primary:false,machine_data_is_learner_destination:false,
   page:await fact(`docs/backend/judson/${role}.teacher.html`),resource:await fact(`docs/backend/judson/${role}.teacher.json`),evidence:await fact('docs/backend/judson/teacher-validation.json'),limitations:[map.limitations.id]};
 o.learner_tools[role]=[...(o.learner_tools[role]??[]).filter(t=>t.tool_id!==tool.tool_id),tool];
 o.native_capabilities[role]={...o.native_capabilities[role],unit_identity:{status:'verified',evidence},educator_unit_alignment:{status:'verified',evidence}};
 const old=o.educator_evidence[role]??{},ids=[role+':judson-teacher-id',role+':judson-teacher-en'];
 const resources=(old.resources??[]).filter(r=>!ids.includes(r.id));
 for(const lang of ['id','en']){
   const file=`${role}.teacher${lang==='en'?'.en':''}.html`,f=await fact('docs/backend/judson/'+file);
   resources.push({id:role+':judson-teacher-'+lang,title:lang==='en'?role+' · Abstract algebra assignment planner':role+' · Perencana tugas aljabar abstrak',resource_type:'teacher-guide',status:'verified',
     url:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/judson/'+file,
     scope:lang==='en'?`${map.exercise_count} source/target exercise identities and reader locations; ${map.hint_count} populated hints; ${map.response_slot_count} empty response slots, not supplied answers.`:scope,bytes:f.bytes,sha256:f.sha256});
 }
 const id=resources.find(r=>r.id===ids[0]);
 o.educator_evidence[role]={...old,status:'verified',verified_date:'2026-09-28',locator:id.url,bytes:id.bytes,sha256:id.sha256,
   features:[...new Set([...(old.features??[]),'exercise_bank','remix_selectors'])],resources};
}
for(const key of Object.keys(before)){
 const a=structuredClone(before[key]),c=structuredClone(o[key]);
 if(['learner_tools','native_capabilities','educator_evidence'].includes(key))for(const role of roles){delete a[role];delete c[role];}
 assert.deepEqual(a,c,'Unrelated override changed: '+key);
}
assert.equal(await readFile(resolve(root,path),'utf8'),original,'Concurrent override write; rerun scoped admission');
await writeFile(resolve(root,path),JSON.stringify(o,null,2)+'\n');
const navPath='backend/authority/central-reader-navigation-v1.json';
const navOriginal=await readFile(resolve(root,navPath),'utf8'),nav=JSON.parse(navOriginal);
const entry=nav.course_surfaces.find(s=>s.root==='docs/backend/judson');assert.ok(entry);
for(const role of roles)for(const lang of ['id','en']){
 const filename=`${role}.teacher${lang==='en'?'.en':''}.html`;
 const document={path:filename,locale:lang,course_ids:[role],contents_paths:[`${role}.teacher${lang==='en'?'':'.en'}.html`,role+'.html']};
 const found=entry.documents.findIndex(d=>d.path===filename);
 if(found<0)entry.documents.push(document);else entry.documents[found]=document;
}
for(const role of roles){const d=entry.documents.find(d=>d.path===role+'.html');d.contents_paths=[...new Set([...(d.contents_paths??[]),role+'.teacher.html'])];}
assert.equal(entry.documents.length,6);
nav.summary.course_surface_html_documents=nav.course_surfaces.reduce((n,s)=>n+s.documents.length,0);
nav.summary.classified_html_documents=nav.summary.reader_html_documents+nav.summary.gateway_html_documents+nav.summary.course_surface_html_documents+nav.summary.generic_html_documents;
nav.summary.navigation_overlay_documents=nav.summary.reader_html_documents+nav.summary.gateway_html_documents+nav.summary.course_surface_html_documents+nav.generic_surfaces.filter(s=>s.navigation_required).length;
assert.equal(await readFile(resolve(root,navPath),'utf8'),navOriginal,'Concurrent navigation write; rerun scoped admission');
await writeFile(resolve(root,navPath),JSON.stringify(nav,null,2)+'\n');
console.log(JSON.stringify({state:'admitted-pending-publication',roles,exercises:913,empty_response_slots_not_answers:116}));
