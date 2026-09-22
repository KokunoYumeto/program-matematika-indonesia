import assert from 'node:assert/strict';
import {readFile,writeFile,readdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import vm from 'node:vm';
import {load,project,build,root,base,json,sha} from './build-d50-surface-v1.mjs';

const input=await load(),map=project(input),byId=new Map(map.units.map(u=>[u.id,u]));
assert.deepEqual(map.counts,{native_records:6912,native_units:1206,native_segments:160,selectable_units:1223,
  lecture_worksheet_pairs:29,worksheet_exercises:576,worksheet_source_solutions:84,exam_occurrences:123,
  semantic_exam_problems:119,placeholder_slots:24,exam_source_solutions:117,original_exam_repairs:6,
  original_bridge_practice:32,selectable_practice:731,concepts:39,concept_edges:39,prerequisite_edges:9,
  native_support_edges:331,exact_routes:1202,enclosing_routes:21});
const units=input.records.filter(r=>['unit','segment'].includes(r.entity_type));
const original=new Map(units.map(r=>[r.id,r]));
assert.equal(map.units.length+map.semantic_exam_groups.length+map.placeholder_slots.length,units.length);
for(const u of map.units){
  assert.deepEqual(u.source_record,original.get(u.id));
  assert.deepEqual(u.rights_ids,[original.get(u.id).rights_component_id]);
  assert.equal(input.witness.anchor_counts[u.route.anchor],1);
  assert.equal(u.route.portable_href,'reader/index.html#'+u.route.anchor);
  assert.deepEqual(u.route.reader,input.witness.reader);
  for(const s of u.support){assert.equal(s.to,u.id);assert.ok(byId.has(s.from));assert.deepEqual(s.source_record,input.records.find(r=>r.id===s.id));}
}
assert.equal(map.units.filter(u=>u.kind==='exercise'&&!u.support.some(r=>r.type==='solves')).length,492);
assert.equal(map.units.filter(u=>u.inline_original_solution).length,32);
assert.equal(map.units.filter(u=>u.support.some(r=>r.provenance==='original_not_source_supplied')).length,6);
for(const s of map.semantic_exam_groups){
  assert.deepEqual(s.source_record,original.get(s.id));
  assert.deepEqual(s.occurrence_ids,input.records.filter(r=>r.relation_type==='occurrence_of'&&r.to_id===s.id).map(r=>r.from_id));
}
assert.equal(new Set(map.semantic_exam_groups.flatMap(s=>s.occurrence_ids)).size,123);
for(const p of map.placeholder_slots)assert.deepEqual(p,original.get(p.id));
// Match exam slots, not occurrence-index positions: forms contain empty slots.
for(const u of map.units.filter(u=>u.kind==='exam_problem_occurrence')){
  const [,form,slot]=/^o011-exam-f(\d+)-slot-(\d+)$/.exec(u.id);
  assert.equal(u.route.anchor,`o011-exam-${form}-p${slot}`);
  assert.equal(input.witness.anchors[u.route.anchor]['data-entity'],'exam-problem');
}
const context=vm.createContext({});vm.runInContext(await readFile(resolve(root,'scripts/d50-study-plan-ui-v1.js'),'utf8'),context);
const api=context.D50_PLAN_API,all=map.units.filter(u=>u.practice).map(u=>u.id);
const plan=JSON.parse(JSON.stringify(api.plan(map,all,'id')));
assert.equal(plan.units.length,731);assert.equal(plan.supporting_units.length,208); // 207 solutions + one inline source hint
assert.equal(plan.semantic_exam_groups.length,119);assert.equal(plan.placeholder_slots_count,24);
assert.equal(plan.placeholder_slots_are_exercises,false);assert.equal(plan.new_solutions_generated,false);
assert.equal(plan.full_reader_in_this_json,false);assert.equal(plan.content_locale,'id-ID');
assert.deepEqual(plan.units,map.units.filter(u=>u.practice));
assert.equal(api.filter(map,'','practice').length,731);assert.equal(api.filter(map,'','lecture_worksheet_pair').length,29);
assert.equal(api.filter(map,'o011-exam-f01-slot-011','exam_problem_occurrence').length,1);
assert.equal(api.plan(map,[all[0],all[0]],'en').units.length,1);
assert.throws(()=>api.plan(map,['o011-exam-f03-slot-003'],'id')); // empty slot
assert.throws(()=>api.plan(map,[map.semantic_exam_groups[0].id],'id')); // not a duplicate exercise
assert.throws(()=>api.plan(map,[],'invented'));
const negatives=[];
function reject(name,mutate){const x=structuredClone(input);mutate(x);assert.throws(()=>project(x),undefined,name);negatives.push(name);}
reject('duplicate_native_id',x=>x.records.push(x.records[0]));
reject('false_english_content',x=>x.lock.content_locale='en');
reject('invented_hosted_reader',x=>x.witness.hosted_reader_url='https://example.com/');
reject('unsafe_archive_url',x=>x.witness.archive.url='javascript:alert(1)');
reject('reader_manifest_hash_drift',x=>x.witness.reader.sha256='0'.repeat(64));
reject('missing_anchor',x=>delete x.witness.anchor_counts['o011-exam-01-p001']);
reject('duplicate_anchor',x=>x.witness.anchor_counts['o011-exam-01-p001']=2);
reject('wrong_exam_solution_binding',x=>x.witness.anchors['o011-exam-01-p001-source-solution']['data-solves']='wrong');
reject('placeholder_as_exercise',x=>x.records.find(r=>r.id==='o011-exam-f03-slot-003').unit_kind='exam_problem_occurrence');
reject('semantic_occurrence_count_drift',x=>x.records.find(r=>r.unit_kind==='semantic_exam_problem').occurrence_count++);
reject('unknown_support_source',x=>x.records.find(r=>r.relation_type==='solves').from_id='missing');
reject('original_solution_misattribution',x=>x.records.find(r=>r.unit_kind==='original_exam_solution_repair').solution_provenance='official_source_supplied');
reject('worksheet_solution_fabrication',x=>x.records.find(r=>r.unit_kind==='exercise'&&!r.has_authority_solution).has_authority_solution=true);
reject('unknown_rights',x=>x.records.find(r=>r.entity_type==='unit').rights_component_id='missing');
reject('parent_cycle',x=>{const r=x.records.find(r=>r.unit_kind==='exercise');r.parent_id=r.id;});
reject('concept_link_unknown_endpoint',x=>x.records.find(r=>r.relation_type==='covers').from_id='missing');
reject('prerequisite_unknown_endpoint',x=>x.records.find(r=>r.relation_type==='requires').to_id='missing');
await build();const a=new Map();for(const f of await readdir(resolve(root,base,'portable')))a.set(f,await readFile(resolve(root,base,'portable',f)));
await build();const replay=[];
for(const [f,b] of a){const c=await readFile(resolve(root,base,'portable',f));assert.deepEqual(c,b);replay.push({path:f,bytes:b.length,sha256:sha(b)});}
const receipt={schema:'d50-independent-consumer-tests/1',state:'pass',counts:map.counts,negative_fixtures:negatives,
  all_practice_plan:{selected:731,supporting:208,semantic_groups:119,placeholders_excluded:24},
  preservation:{every_native_unit_and_segment_accounted:true,exact_original_records:true,component_rights:true,
    official_original_solution_distinction:true,exam_slot_mapping:true,semantic_occurrences_not_duplicated:true},
  deterministic_replay:{builds:2,outputs:replay},browser_verified:false,hosted_reader_claimed:false};
await writeFile(resolve(root,base,'tests.json'),json(receipt));
console.log(json({state:'pass',counts:map.counts,negative_fixtures:negatives.length,all_practice_plan:receipt.all_practice_plan}));
