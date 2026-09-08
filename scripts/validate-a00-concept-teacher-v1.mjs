import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtemp,readFile,readdir,rm,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {dirname,relative,resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
import {build,loadInputs,base,root} from './build-a00-concept-teacher-v1.mjs';
import {projectA00} from './a00_concept_model_v1.mjs';
import {testA00UI} from './test_a00_ui_host_v1.mjs';

const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const read=path=>readFile(resolve(root,path));
const load=async path=>JSON.parse(await read(path));
const fact=async path=>{const bytes=await read(path);return {path,bytes:bytes.length,sha256:hash(bytes)};};
const inputs=await loadInputs(),manifest=await load(base+'/manifest.json');
const model=await load(base+'/data/learning-map.json');
const sandbox={};vm.createContext(sandbox);
vm.runInContext((await read(base+'/views/a00-controls.js')).toString(),sandbox);
vm.runInContext((await read(base+'/data/assessment-inventory-v1.js')).toString(),sandbox);
model.assessments=JSON.parse(JSON.stringify(sandbox.A00AssessmentInventory));
const helper=sandbox.A00ConceptControls;
const plain=value=>JSON.parse(JSON.stringify(value));
const negatives=[];
const reject=(name,fn)=>{assert.throws(fn,undefined,name);negatives.push({name,result:'rejected'});};
const lock=await load(base+'/input/source-lock.json');
const nativeRoot=resolve(root,'../openstax-prealgebra/modular_backend');
// This validation independently replays the real native source, not only a
// generated manifest that might repeat the generator's mistake.
const rawNative={};
for(const key of ['graph','overlay','nativeConcepts','originalGraph','nativeManifest','rights']){
  const source=lock.sources[key],bytes=await readFile(resolve(nativeRoot,source.path));
  assert.equal(bytes.length,source.bytes);assert.equal(hash(bytes),source.sha256);
  rawNative[key]=['nativeConcepts','rights'].includes(key)?bytes.toString().trim().split('\n').map(JSON.parse):JSON.parse(bytes);
}
assert.deepEqual(model.concept_rights,rawNative.rights.find(row=>row.id===model.concept_rights.id));
assert.ok(model.concepts.every(row=>row.rights_component_id===model.concept_rights.id));
const original=structuredClone(rawNative.originalGraph);
delete original.curriculum_source.path;
original.curriculum_source.authority_id=rawNative.graph.curriculum_source.authority_id;
original.curriculum_source.path_locator=rawNative.graph.curriculum_source.path_locator;
assert.deepEqual(original,rawNative.graph);
assert.equal(rawNative.overlay.neutral_curation.sha256,lock.sources.originalGraph.sha256);
const conceptIds=new Set(),objectiveIds=new Set(),ordinals=new Set();let edges=0;
for(const c of model.concepts){
  assert.ok(!conceptIds.has(c.id));conceptIds.add(c.id);
  const originalConcept=rawNative.graph.concepts.find(row=>row.key===c.key);
  const originalId=rawNative.nativeConcepts.find(row=>row.concept_key===c.key);
  const originalLabel=rawNative.overlay.concepts.find(row=>row.key===c.key);
  assert.equal(c.id,originalId.id);assert.equal(c.role,originalConcept.role);
  assert.deepEqual(c.labels,{id:originalLabel.label,en:originalConcept.label_en_us});
  assert.deepEqual(c.definitions,{id:originalLabel.definition,en:originalConcept.definition_en_us});
  assert.deepEqual(c.prerequisite_keys,originalConcept.prerequisite_keys);
  assert.deepEqual(c.prerequisite_ids,originalId.prerequisite_ids);edges+=c.prerequisite_keys.length;
  assert.deepEqual(c.objective_unit_ids,originalId.objective_unit_ids);
  assert.equal(c.objective_identity_order_is_not_an_ordinal_crosswalk,true);
  for(const id of c.objective_unit_ids){assert.ok(!objectiveIds.has(id));objectiveIds.add(id);}
  assert.equal(c.modules.length,originalConcept.evidence.length);
  for(const [index,evidence] of originalConcept.evidence.entries()){
    const projected=c.modules[index];
    assert.deepEqual(projected.objective_numbers,evidence.objective_numbers);
    assert.equal(projected.module_id,evidence.module_id);assert.equal(projected.module_uuid,evidence.module_uuid);
    assert.equal(projected.source_objective_numbering,'frozen_en_US_not_localized_numbering');
    const crosswalk=inputs.crosswalks.find(row=>row.semantic_key.endsWith(':crosswalk:'+evidence.module_id));
    assert.equal(projected.native_module_unit_id,crosswalk.payload.source_id);
    assert.equal(projected.projected_unit_id,crosswalk.payload.target_id);
    for(const ordinal of evidence.objective_numbers){const key=evidence.module_id+':'+ordinal;assert.ok(!ordinals.has(key));ordinals.add(key);}
  }
}
assert.equal(conceptIds.size,35);assert.equal(objectiveIds.size,245);assert.equal(ordinals.size,245);assert.equal(edges,76);
const expectedRows=inputs.assessments.modules.flatMap(module=>module.assessments.map(row=>({...row,module_id:module.module_id})));
assert.deepEqual(model.assessments,expectedRows);
assert.deepEqual(model.counts,manifest.counts);assert.equal(model.counts.localized_objectives,246);
const categories=['all',...Object.keys(inputs.assessments.category_labels)];let selectionCases=0;
for(const module of inputs.assessments.modules)for(const category of categories)for(const solution of ['all','with','without']){
  const expected=module.assessments.filter(row=>(category==='all'||row.category===category)&&
    (solution==='all'||row.has_explicit_solution===(solution==='with'))).map(row=>row.id);
  const actual=helper.selectAssessments(model,[module.module_id],category,solution).map(row=>row.id);
  assert.deepEqual(plain(actual),expected);selectionCases++;
}
for(const c of model.concepts){
  const required=new Set(),queue=[...c.prerequisite_keys];
  while(queue.length){const key=queue.shift();if(required.has(key))continue;required.add(key);queue.push(...model.concepts.find(row=>row.key===key).prerequisite_keys);}
  assert.deepEqual([...plain(helper.prerequisiteClosure(model,[c.key]))].sort(),[...required].sort());
  const moduleIds=[...new Set(c.modules.map(row=>row.module_id))];
  const selection=plain(helper.makeSelection(model,moduleIds,[c.key]));
  assert.deepEqual(selection.modules.map(row=>row.module_id).sort(),moduleIds.sort());
  assert.equal(selection.assessment_scope,'module_inventory_not_exercise_to_concept_alignment');
  assert.equal(selection.learning_outcome_validated,false);assert.equal(selection.prerequisite_mastery_inferred,false);
  assert.deepEqual(selection.selected_concept_evidence_modules_not_in_selection,[]);
  assert.equal(selection.selected_concepts[0].id,c.id);
  const plan=plain(helper.makeStudyPlan(model,moduleIds,[c.key],{}, {goal:'Authored intention'},'en'));
  assert.deepEqual(plan.selected_source_concepts[0].source_objective_ids,c.objective_unit_ids);
  assert.equal(plan.selected_source_concepts[0].objective_ids_are_not_localized_ordinals,true);
  assert.equal(plan.author_intent_is_source_content,false);
  assert.equal(plan.reading_order,'native_book_order_not_individualized_recommendation');
  assert.equal(plan.delivery.textbook_bodies_included,false);
  assert.equal(plan.learning_gain_estimated,false);assert.equal(plan.learner_population_estimated,false);
  assert.deepEqual(plan.selection,selection);
}
const allModules=model.modules.map(row=>row.module_id);
const complete=plain(helper.makeSelection(model,allModules,model.concepts.map(c=>c.key)));
assert.equal(complete.assessments.length,8105);assert.equal(complete.assessments.filter(row=>row.solution_gap_id).length,2865);
assert.deepEqual(complete.unselected_prerequisite_concepts,[]);
reject('empty selection',()=>helper.makeSelection(model,[],[]));
reject('unknown module',()=>helper.makeSelection(model,['missing'],[]));
reject('duplicate modules',()=>helper.makeSelection(model,[allModules[0],allModules[0]],[]));
reject('unknown concept',()=>helper.prerequisiteClosure(model,['missing']));
reject('invalid category',()=>helper.selectAssessments(model,allModules,'invented'));
reject('invalid solution filter',()=>helper.selectAssessments(model,allModules,'all','invented'));
let changed=structuredClone(inputs);changed.overlay.neutral_curation.sha256='0'.repeat(64);
reject('wrong overlay source binding',()=>projectA00(changed));
changed=structuredClone(inputs);changed.nativeConcepts[0].objective_unit_ids[0]=changed.nativeConcepts[0].objective_unit_ids[1];
reject('duplicated objective identity',()=>projectA00(changed));
changed=structuredClone(inputs);changed.crosswalks[0].payload.target_id='wrong';
reject('wrong module crosswalk',()=>projectA00(changed));
const cycle=structuredClone(model);cycle.concepts[0].prerequisite_keys=[cycle.concepts[0].key];
reject('prerequisite cycle',()=>helper.prerequisiteClosure(cycle,[cycle.concepts[0].key]));
const dangling=structuredClone(model);dangling.concepts[0].prerequisite_keys=['missing'];
reject('dangling prerequisite',()=>helper.prerequisiteClosure(dangling,[dangling.concepts[0].key]));
reject('unsupported plan locale',()=>helper.makeStudyPlan(model,allModules,[],{}, {},'xx'));
reject('unexpected authored field',()=>helper.makeStudyPlan(model,allModules,[],{}, {source_revision:'forged'}));
reject('oversized authored field',()=>helper.makeStudyPlan(model,allModules,[],{}, {goal:'a'.repeat(2001)}));
reject('nontext authored field',()=>helper.makeStudyPlan(model,allModules,[],{}, {goal:{}}));
let checkedPages=0;const uiCases=[];
for(const file of manifest.outputs){
  const bytes=await read(base+'/'+file.path);assert.equal(bytes.length,file.bytes);assert.equal(hash(bytes),file.sha256);
  if(!file.path.endsWith('.html'))continue;
  const html=bytes.toString(),ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(row=>row[1]);
  assert.equal(new Set(ids).size,ids.length,'Duplicate page ID');
  const payload=JSON.parse(html.match(/<script type="application\/json" id="a00-page-data">([\s\S]*?)<\/script>/)[1]);
  const expectedLocale=file.path.includes('-en')?'en':'id';assert.equal(payload.locale,expectedLocale);
  assert.match(html,new RegExp('<html lang="'+expectedLocale+'">'));
  assert.equal(payload.model.reading_language,'id-ID');assert.equal(payload.model.concepts.length,35);
  assert.equal((html.match(/class="concept-card"/g)||[]).length,35);
  assert.equal((html.match(/<li><a href="https:\/\/kokunoyumeto.github.io\/openstax-prealgebra-2e-id-ID\/modules\//g)||[]).length,138);
  for(const key of ['module','category','solution','assessment-query','results','previous','next','concept-query','concept-role'])
    assert.ok(ids.includes(key)||(key==='module'&&payload.teacher));
  if(payload.teacher){
    for(const id of ['download-selection','export-status','prerequisite-status','clear-modules','select-concept-modules','download-study-plan-html','download-study-plan-json','plan-export-status'])assert.ok(ids.includes(id));
    for(const key of Object.keys(payload.labels.planFields))assert.ok(ids.includes('plan-'+key));
    const plan=plain(helper.makeStudyPlan(model,[allModules[0]],[],{}, {title:'<img src=x onerror=alert(1)>'},expectedLocale));
    const rendered=helper.renderStudyPlan(plan,payload.labels);
    assert.ok(rendered.includes('&lt;img src=x onerror=alert(1)&gt;'));assert.doesNotMatch(rendered,/<img\b|<script\b/);
    assert.ok(rendered.includes(payload.labels.planPortableNote));
    assert.ok(!rendered.includes(payload.labels.portableNote),'Standalone plan must describe its own offline scope');
    const badLink=structuredClone(plan);badLink.readings[0].module_url='javascript:alert(1)';
    reject('unsafe exported link '+expectedLocale,()=>helper.renderStudyPlan(badLink,payload.labels));
  }
  for(const match of html.matchAll(/(?:href|src)="([^"]+)"/g)){
    const value=match[1];if(value.startsWith('#')){assert.ok(ids.includes(value.slice(1)));continue;}
    if(value.startsWith('https://'))continue;
    const target=resolve(root,base,dirname(file.path),value);
    const relativeTarget=relative(resolve(root,base),target);assert.ok(!relativeTarget.startsWith('..'));
    await readFile(target);
  }
  new vm.Script((await read(base+'/views/a00-ui.js')).toString());checkedPages++;
  uiCases.push(testA00UI(html,(await read(base+'/views/a00-controls.js')).toString(),
    (await read(base+'/data/assessment-inventory-v1.js')).toString(),(await read(base+'/views/a00-ui.js')).toString()));
}
assert.equal(checkedPages,4);
for(const generator of manifest.generators)assert.deepEqual(await fact(generator.path),generator);
const temp=await mkdtemp(resolve(tmpdir(),'a00-concept-replay-'));
let replay;
try {
  replay=await build(temp);assert.deepEqual(replay,manifest);
  for(const file of manifest.outputs)assert.deepEqual(await readFile(resolve(temp,file.path)),await read(base+'/'+file.path));
}finally{
  // Only this call's mkdtemp directory may be removed.
  assert.ok(resolve(temp).startsWith(resolve(tmpdir())+sep));assert.ok(temp.includes('a00-concept-replay-'));
  await rm(temp,{recursive:true,force:true});
}
const validatorPath='scripts/validate-a00-concept-teacher-v1.mjs';
const receipt={schema:'a00-concept-teacher-validation/1',result:'pass',counts:model.counts,
  manifest:await fact(base+'/manifest.json'),validator:await fact(validatorPath),
  ui_test_host:await fact('scripts/test_a00_ui_host_v1.mjs'),
  checks:{native_source_hashes:true,original_to_emitted_metadata_only:true,concept_definition_labels_exact:true,
    independent_native_objective_identity_replay:true,source_ordinal_evidence_exact:true,prerequisite_closure_cases:35,
    module_category_solution_cases:selectionCases,exercise_identity_replay:8105,negative_fixtures:negatives,
    bilingual_pages:checkedPages,actual_ui_host_cases:uiCases,relative_asset_links:true,deterministic_second_build:true,
    source_bound_study_plan_cases:35,readable_plan_locales:2,
    browser_testing_performed:false,linguistic_certification:false,publication_verified:false}};
await writeFile(resolve(root,base,'validation.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify(receipt));
