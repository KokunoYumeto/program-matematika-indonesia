import assert from 'node:assert/strict';
import {mkdtemp, readFile, readdir, rm, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve, sep} from 'node:path';
import vm from 'node:vm';
import {base, build, json, loadInputs, project, projectMap, sha256} from './build-d20-surface-v1.mjs';

const input=await loadInputs(),map=projectMap(input),byId=new Map(map.units.map(u=>[u.id,u]));
assert.deepEqual(map.counts,{units:1960,chapters:17,semantic_units:1867,exercises:52,original_solutions:62,
  selected_reader_work:10,bridge_units:13,support_relations:184,concepts:15,chapter_concept_links:15,
  concept_prerequisites:6,bridge_prerequisites:5,practice_units:62,exact_routes:1960});
const sourceRows=[...input.tables.units.filter(r=>r.record_type==='unit'),...input.tables.semantic_units,...input.tables.o001_mastery,...input.tables.bridge_units];
for(const r of sourceRows){
  const u=byId.get(r.id);assert.ok(u);assert.deepEqual(u.source_record,r);assert.deepEqual(u.rights_ids,[r.rights_id]);
  assert.equal(u.locale,'id-ID');const route=input.witness.routes.find(w=>w.target_id===u.id&&w.url===u.route.url);
  assert.ok(route);assert.equal(route.occurrences,1);assert.deepEqual(u.route.page,input.witness.pages.find(p=>p.path===route.path));
}
const nativeRelations=new Map([...input.tables.relations,...input.tables.companion_relations].map(r=>[r.id,r]));
for(const u of map.units)for(const r of u.support){const n=nativeRelations.get(r.id);assert.equal(n.from_id,r.from);assert.equal(n.to_id,u.id);assert.equal(n.relation_type,r.type);assert.ok(byId.has(r.from));}
for(const r of input.tables.exercise_support){const u=byId.get(r.exercise_unit_id);assert.equal(u.exercise_support.base.original_solution_state,'queued_in_O001');assert.equal(u.exercise_support.overlay.effective_original_solution_state,'admitted_in_companion_readers');assert.equal(u.support.filter(s=>s.type==='solves').length,1);}
assert.equal(map.historical_scope_records.length,1);assert.equal(map.historical_scope_records[0].authoring_state,'queued');
assert.deepEqual(new Set(map.chapter_concept_links.map(r=>r.from_id)),new Set(['FAOA-2015-CH01']));
assert.equal(map.unresolved_external_course_relations[0].from_id,'COURSE-O007');
assert.deepEqual(map.component_prerequisites.map(r=>r.to_id),['FAOA-2015-CH04','FAOA-2015-CH07','FAOA-2015-CH08','FAOA-2015-CH11','FAOA-2015-CH15']);
// Exact native edge direction is preserved; this does not manufacture a full-course graph.
const visited=new Set(),active=new Set();
function visit(id){assert.ok(!active.has(id),'Concept prerequisite cycle');if(visited.has(id))return;active.add(id);for(const r of map.concept_prerequisites.filter(r=>r.from_id===id))visit(r.to_id);active.delete(id);visited.add(id);}
for(const c of map.concepts)visit(c.id);
const negatives=[];
function reject(name,change){const copy=structuredClone(input);change(copy);assert.throws(()=>projectMap(copy),undefined,name);negatives.push({name,result:'rejected'});}
reject('duplicate_native_unit',x=>x.tables.semantic_units.push(x.tables.semantic_units[0]));
reject('wrong_content_locale',x=>x.lock.content_locale='en');
reject('wrong_route_target',x=>x.witness.routes[0].target_id='invented');
reject('unsafe_route_url',x=>x.witness.routes[0].url='javascript:alert(1)');
reject('duplicate_anchor',x=>x.witness.routes.find(r=>r.target_id==='FAOA-2015-CH01-NODE-0003').occurrences=2);
reject('missing_route',x=>x.witness.routes=x.witness.routes.filter(r=>r.target_id!=='FAOA-2015-CH01-NODE-0003'));
reject('unknown_support_endpoint',x=>x.tables.relations.find(r=>r.relation_type==='hints').from_id='missing');
reject('wrong_status_exercise',x=>x.tables.o001_status[0].exercise_unit_id='wrong');
reject('stale_status_base',x=>x.tables.o001_status[0].base_support_line_sha256='0'.repeat(64));
reject('missing_status_overlay',x=>x.tables.o001_status.pop());
reject('duplicate_status_overlay',x=>x.tables.o001_status.push({...x.tables.o001_status[0],id:'duplicate-overlay'}));
reject('unadmitted_solution',x=>x.tables.o001_mastery[0].admission_state='pending');
reject('unknown_component_rights',x=>x.tables.bridge_units[0].rights_id='unknown');
reject('parent_cycle',x=>x.tables.semantic_units[0].parent_id=x.tables.semantic_units[0].id);
const context=vm.createContext({});vm.runInContext(await readFile(resolve(project,'scripts/study-plan-ui-v1.js'),'utf8'),context);
const api=context.COURSE_PLAN_API, selected=map.units.filter(u=>u.practice).map(u=>u.id);
assert.equal(api.filterUnits(map,'','practice').length,62);assert.equal(api.filterUnits(map,'FAOA-2015-CH01-NODE-0003').length,1);
assert.equal(api.filterUnits(map,'','chapter','','CONCEPT-VECTOR-SPACE').length,1);
assert.equal(api.filterUnits(map,'','chapter','FAOA-2015-CH02','CONCEPT-VECTOR-SPACE').length,0);
const plan=JSON.parse(JSON.stringify(api.makePlan(map,selected,'en')));
assert.equal(plan.units.length,62);assert.equal(plan.supporting_units.filter(u=>u.kind==='original_solution').length,62);
assert.deepEqual(plan.units.map(u=>u.id),selected);assert.deepEqual(plan.units,map.units.filter(u=>u.practice));
assert.deepEqual(new Set(plan.supporting_units.map(u=>u.id)),new Set(plan.units.flatMap(u=>u.support.map(r=>r.from))));
assert.equal(plan.offline_book_included,false);assert.equal(plan.answers_generated,false);assert.equal(plan.content_locale,'id-ID');
assert.throws(()=>api.makePlan(map,['invented'],'en'));assert.throws(()=>api.makePlan(map,[],'invented'));
assert.equal(api.makePlan(map,[selected[0],selected[0]],'id').units.length,1);assert.equal(api.makePlan(map,[],'en').units.length,0);
const parent=resolve(tmpdir()),temp=await mkdtemp(join(parent,'d20-replay-')),replay=[];
assert.ok(temp.startsWith(parent+sep));
try{
  await build(join(temp,'a'));await build(join(temp,'b'));
  for(const file of await readdir(join(temp,'a'))){const a=await readFile(join(temp,'a',file)),b=await readFile(join(temp,'b',file)),c=await readFile(resolve(project,'docs/backend/d20',file));assert.deepEqual(a,b);assert.deepEqual(a,c);replay.push({path:file,bytes:a.length,sha256:sha256(a)});}
}finally{assert.ok(temp.startsWith(parent+sep));await rm(temp,{recursive:true,force:true});}
for(const file of ['D20.html','D20.en.html','D20-pengajar.html','D20-pengajar.en.html']){
  const html=await readFile(resolve(project,'docs/backend/d20',file),'utf8'),ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(new Set(ids).size,ids.length);assert.ok(html.includes('<noscript>'));assert.equal(html.includes('data-program-home'),false);
  assert.ok(html.includes('connect-src \'none\''));assert.ok(html.includes('id="workbench" hidden'));
}
const receipt={schema:'d20-independent-consumer-tests/1',state:'pass',counts:map.counts,negative_fixtures:negatives,
  all_practice_plan:{units:plan.units.length,supporting_units:plan.supporting_units.length,original_solutions:62},
  preservation:{every_projected_native_record:true,all_native_relation_joins:true,base_and_overlay_distinct:true,chapter_concepts_not_invented:true},
  deterministic_replay:{builds:2,outputs:replay},scope:'Full projected metadata, status joins, routes, selection API and replay. Browser tests are separate.'};
await writeFile(resolve(project,base,'tests.json'),json(receipt));console.log(json({state:'pass',counts:map.counts,negative_fixtures:negatives.length,practice_plan:receipt.all_practice_plan}));
