import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import { buildModel } from './lebl-capability-model-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const input={};
for(const name of ['units','terms','relations','resources','editions','rights','reader-destinations','volume-entrypoints','native-summary'])input[name]=JSON.parse(await readFile(resolve(root,`backend/course-capsule-v1/adapters/lebl-capability-v1/input/${name}.json`),'utf8'));
const model=buildModel(input);
assert.equal(model.units.length,5932);assert.equal(model.counts.units_with_shared_or_unresolved_book_assignment,4);
const exclusive={};for(const unit of model.units)if(unit.books.length===1)exclusive[unit.books[0]]=(exclusive[unit.books[0]]||0)+1;
assert.deepEqual(exclusive,{'R008':1527,'R007':1732,'R006-volume-1':1613,'R006-volume-2':1055});
assert.equal(model.units.filter(u=>u.books.length===2).length,1);
const byId=new Map(model.units.map(u=>[u.id,u]));
for(const source of input.units){const unit=byId.get(source.id);assert.equal(unit.support_state,source.exercise_metadata?.solution_status??null);assert.deepEqual(unit.source_components,source.manifest_binding.source_components);assert.deepEqual(unit.target_components,source.manifest_binding.target_components);assert.equal(unit.rights_id,source.rights_id);}
const edges=model.units.flatMap(u=>u.support.map(s=>({...s,exercise:u})));
assert.equal(edges.filter(e=>e.kind==='solution').length,251);
assert.equal(edges.filter(e=>e.kind==='hint').length,290);
assert.equal(edges.filter(e=>e.evidence.length===2).length,14);
assert.equal(edges.filter(e=>e.kind==='solution'&&e.exercise.support_state==='unknown').length,251);
assert.equal(model.units.flatMap(u=>u.term_ids).length,179);
assert.equal(model.terms.filter(t=>t.variants.length).length,176);
assert.equal(model.terms.flatMap(t=>t.rejected_forms).length,21);
assert.deepEqual(JSON.parse(JSON.stringify(model)),model,'Serialized projection changed JSON values');
// Relations and typed children are independent evidence; duplicate relations
// must enrich one edge rather than duplicating the linked support record.
const unionInput=structuredClone(input);
const linked=unionInput.relations.find(r=>r.predicate==='hints');
const linkedChild=unionInput.units.find(u=>u.id===linked.subject_id);
linkedChild.parent_id=unionInput.units.find(u=>u.unit_kind==='section'&&u.resource_id===linkedChild.resource_id).id;
unionInput.relations.push({...linked,id:linked.id+'-second-evidence'});
const unionModel=buildModel(unionInput);
const relationOnly=unionModel.units.find(u=>u.id===linked.object_id).support.filter(s=>s.id===linked.subject_id);
assert.equal(relationOnly.length,1);
assert.deepEqual(relationOnly[0].evidence,[{basis:'explicit_native_relation',relation_id:linked.id},{basis:'explicit_native_relation',relation_id:linked.id+'-second-evidence'}]);
assert.equal(unionModel.units.find(u=>u.id===linked.object_id).support_state,model.units.find(u=>u.id===linked.object_id).support_state);
for(const key of ['semantic_aliases','prerequisite_ids','source_binding','status'])assert.ok(model.projection_policy.units.not_copied_whole.includes(key));
for(const key of ['register','status','semantic_aliases','locale'])assert.ok(model.projection_policy.terms.not_copied_whole.includes(key));
for(const key of ['scope_ids','evidence','ledger_binding'])assert.ok(model.projection_policy.terms.copied_fields.includes(key));
let mutations=0;
for(const change of [
  x=>x.units.push(x.units[0]),
  x=>x.units[0].parent_id=x.units[0].id,
  x=>x.units[0].rights_id='urn:missing',
  x=>x.units[0].resource_id=x.units[1].resource_id+'x',
  x=>x.units.find(u=>u.unit_kind==='exercise').exercise_metadata.solution_status='complete',
  x=>x['reader-destinations'][0].outline[0].page=99999,
  x=>x.relations.find(r=>r.predicate==='hints').object_id='urn:missing',
  x=>x.terms.push(x.terms[0]),
  x=>x.units.find(u=>u.manifest_binding.resource_key==='R006'&&u.manifest_binding.target_components[0].path.includes('ch-metric')).manifest_binding.target_components[0].path='translation/ra/ch-multivar-int.tex',
]){const copy=structuredClone(input);change(copy);assert.throws(()=>buildModel(copy));mutations++;}
// Exercise the actual shipped script, using DOM stubs, not a rewritten filter.
const script=await readFile(resolve(root,'docs/backend/lebl/filters.js'),'utf8');
const element=()=>({value:'',textContent:'',events:{},addEventListener(name,fn){this.events[name]=fn;}});
const q=element(),support=element(),count=element(),make=element(),plan=element(),status=element();
const rows=model.units.filter(u=>u.kind==='exercise').slice(0,6).map((u,i)=>({dataset:{id:u.id,title:u.title,section:u.section_title,href:u.destinations[0].href,state:i%2?'hint_only':'unknown',sourceLocalId:u.source_local_id,learner:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/lebl/C50.html#'+u.id,source:JSON.stringify(u.source_components),target:JSON.stringify(u.target_components),supportLabel:i%2?'Petunjuk tersedia menurut metadata':'Dukungan solusi belum dipetakan',destinationScope:i===1?'whole_book_no_heading_match':u.destinations[0].scope},textContent:i%2?'integral':'barisan',hidden:false,checkbox:{checked:i===0},querySelector(){return this.checkbox;}}));
const nodes={'#query':q,'#support':support,'#count':count,'#make-plan':make,'#plan':plan,'#plan-status':status};
vm.runInNewContext(script,{document:{querySelector:s=>nodes[s]??null,querySelectorAll:()=>rows}});
assert.equal(rows.filter(r=>!r.hidden).length,6);
q.value='barisan';q.events.input();assert.equal(rows.filter(r=>!r.hidden).length,3);
support.value='hint_only';support.events.input();assert.equal(rows.filter(r=>!r.hidden).length,0);
q.value='';q.events.input();assert.equal(rows.filter(r=>!r.hidden).length,3);
make.events.click();assert.ok(plan.value.includes(rows[0].dataset.id));assert.ok(!plan.value.includes(rows[1].dataset.id));assert.ok(plan.value.includes('unknown'));
for(const key of ['sourceLocalId','learner','source','target','supportLabel'])assert.ok(plan.value.includes(rows[0].dataset[key]),key);
assert.ok(plan.value.includes('bukan halaman persis latihan'));
rows[1].checkbox.checked=true;make.events.click();assert.ok(plan.value.includes('Tautan buku; lokasi latihan belum dipetakan.'));
assert.ok(plan.value.includes(rows[0].dataset.id),'Hidden checked choice must remain in plan');
rows[1].checkbox.checked=false;
rows[0].checkbox.checked=false;make.events.click();assert.equal(plan.value,'');
console.log(JSON.stringify({state:'pass',rejected_mutations:mutations,filter_and_plan_scenarios:8,support_union_fixture:true,projection_loss_fields_checked:true,typed_support_edges:edges.length,unit_term_pairs:179}));
