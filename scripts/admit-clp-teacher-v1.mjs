import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {clp1EvidencePaths,loadClp1Evidence,validateClp1Evidence} from './clp1-navigation-evidence-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/clp-teacher-v1';
const roles=['B20','B30','B50','B60'];
const load=async p=>JSON.parse(await readFile(resolve(root,p),'utf8'));
const fact=async p=>{const b=await readFile(resolve(root,p));return {path:p,bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')};};
const tests=await load(base+'/tests.json'),hosted=await load('docs/backend/clp/teacher-validation.json');
assert.equal(tests.state,'pass');assert.equal(hosted.state,'pass');
assert.equal(tests.native_exercises_individually_checked,2198);
assert.deepEqual(hosted.course_counts,tests.course_counts);
const navigation=await loadClp1Evidence(root);
validateClp1Evidence(navigation.data,navigation.bytes,hosted,tests);
for(const f of hosted.files)assert.deepEqual(await fact('docs/backend/clp/'+f.path),{...f,path:'docs/backend/clp/'+f.path});
const evidence=[];
for(const [kind,path] of [['clp_teacher_mapping_tests',base+'/tests.json'],['clp_teacher_source_lock',base+'/input/source-lock.json'],['clp_teacher_hosted_surface','docs/backend/clp/teacher-validation.json']]){
  const f=await fact(path);evidence.push({kind,locator:path,bytes:f.bytes,sha256:f.sha256,verified_date:'2026-09-30'});
}
const b20Evidence=[...evidence];
for(const [kind,path] of Object.entries(clp1EvidencePaths)){
  const f=await fact(path);b20Evidence.push({kind,locator:path,bytes:f.bytes,sha256:f.sha256,verified_date:'2026-09-30'});
}
const path='backend/course-capsule-v1/authority/integration-overrides-v1.json';
const o=await load(path),before=structuredClone(o);
for(const role of roles){
  const map=await load(`docs/backend/clp/${role}.teacher.json`);
  const scope=`${map.exercise_count} soal sumber dengan identitas bersama, lokasi sumber dan bantuan tercatat; `+(role==='B20'?'rentang tiap soal dan 2.010 bantuan dalam sumber terjemahan serta halaman awal PDF telah dipetakan. Bukan peninjauan baru atas mutu terjemahan.':'pemetaan struktural Bahasa Indonesia dipertahankan.');
  const tool={tool_id:role.toLowerCase()+'.clp_assignment_planner',label:role+' · Perencana tugas CLP',href:`backend/clp/${role}.teacher.html`,action_kind:'reference',scope,state:'verified',primary:false,machine_data_is_learner_destination:false,
    page:await fact(`docs/backend/clp/${role}.teacher.html`),resource:await fact(`docs/backend/clp/${role}.teacher.json`),evidence:await fact('docs/backend/clp/teacher-validation.json'),limitations:[map.limitations.id]};
  o.learner_tools[role]=[...(o.learner_tools[role]??[]).filter(t=>t.tool_id!==tool.tool_id),tool];
  o.native_capabilities[role]={...o.native_capabilities[role],unit_identity:{status:'verified',evidence},educator_unit_alignment:{status:'verified',evidence:role==='B20'?b20Evidence:evidence}};
  const old=o.educator_evidence[role]??{},ids=[role+':clp-teacher-id',role+':clp-teacher-en'];
  const resources=(old.resources??[]).filter(r=>!ids.includes(r.id));
  for(const lang of ['id','en']){
    const file=`${role}.teacher${lang==='en'?'.en':''}.html`,f=await fact('docs/backend/clp/'+file);
    const resourceScope=lang==='en'?`${map.exercise_count} source exercises with shared identities and recorded support; `+(role==='B20'?'individual translated-source spans and PDF start pages for every question and 2,010 supports. Not a new translation-quality review.':'structural Indonesian target mappings are preserved.'):scope;
    resources.push({id:role+':clp-teacher-'+lang,title:lang==='en'?role+' · CLP assignment planner':role+' · Perencana tugas CLP',resource_type:'teacher-guide',status:'verified',url:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/clp/'+file,scope:resourceScope,bytes:f.bytes,sha256:f.sha256});
  }
  const id=resources.find(r=>r.id===ids[0]);
  o.educator_evidence[role]={...old,status:'verified',verified_date:'2026-09-30',locator:id.url,bytes:id.bytes,sha256:id.sha256,features:[...new Set([...(old.features??[]),'exercise_bank','remix_selectors','staged_hints_answers_solutions'])],resources};
}
for(const key of Object.keys(before)){
  const a=structuredClone(before[key]),c=structuredClone(o[key]);
  if(['learner_tools','native_capabilities','educator_evidence'].includes(key))for(const role of roles){delete a[role];delete c[role];}
  assert.deepEqual(a,c,'Unrelated override changed: '+key);
}
await writeFile(resolve(root,path),JSON.stringify(o,null,2)+'\n');
const navPath='backend/authority/central-reader-navigation-v1.json',nav=await load(navPath);
const entry=nav.course_surfaces.find(s=>s.root==='docs/backend/clp');assert.ok(entry);
const otherSurfaces=structuredClone(nav.course_surfaces.filter(s=>s!==entry));
for(const role of roles)for(const lang of ['id','en']){
  const filename=`${role}.teacher${lang==='en'?'.en':''}.html`;
  const document={path:filename,locale:lang,course_ids:[role],contents_paths:[`${role}.teacher${lang==='en'?'':'.en'}.html`,role+'.html']};
  const found=entry.documents.findIndex(d=>d.path===filename);
  if(found<0)entry.documents.push(document);else entry.documents[found]=document;
}
for(const role of roles){const d=entry.documents.find(d=>d.path===role+'.html');d.contents_paths=[...new Set([...d.contents_paths,role+'.teacher.html'])];}
assert.equal(entry.documents.length,13);
nav.summary.course_surface_html_documents=nav.course_surfaces.reduce((n,s)=>n+s.documents.length,0);
nav.summary.classified_html_documents=nav.summary.reader_html_documents+nav.summary.gateway_html_documents+nav.summary.course_surface_html_documents+nav.summary.generic_html_documents;
nav.summary.navigation_overlay_documents=nav.summary.reader_html_documents+nav.summary.gateway_html_documents+nav.summary.course_surface_html_documents+nav.generic_surfaces.filter(s=>s.navigation_required).length;
assert.deepEqual(nav.course_surfaces.filter(s=>s!==entry),otherSurfaces);
assert.equal(nav.summary.course_surface_html_documents,13+otherSurfaces.reduce((n,s)=>n+s.documents.length,0));
assert.equal(nav.course_surfaces.find(s=>s.root==='docs/backend/judson').documents.length,6);
await writeFile(resolve(root,navPath),JSON.stringify(nav,null,2)+'\n');
console.log(JSON.stringify({state:'admitted-pending-publication',roles,precise_target_alignment_roles:roles,clp1_native_file_boundary_preserved:true,clp1_additive_printed_references:2705}));
