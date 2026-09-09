import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
import {testUI} from './test_b10_ui_host_v1.mjs';
import {labels} from './b10_selection_labels_v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),base='backend/course-capsule-v1/adapters/b10-selection-v1';
const read=p=>readFile(resolve(root,p));const json=async p=>JSON.parse(await read(p));
const hash=b=>createHash('sha256').update(b).digest('hex');
const fact=async path=>{const b=await read(path);return {path,bytes:b.length,sha256:hash(b)};};
const manifest=await json(base+'/manifest.json'),m=await json(base+'/data/model.json');
for(const r of [...manifest.sources,...manifest.generators,...manifest.reader_files])assert.deepEqual(await fact(r.path),r);
for(const r of manifest.outputs)assert.deepEqual(await fact(base+'/'+r.path),{...r,path:base+'/'+r.path});
const side=await json('docs/en/courses/B10/reader/metadata/pretext-unit-routes.json'),map=new Map(side.units.map(r=>[r.unit_id,r]));
const native=(await read('backend/v2.3/extensions/b10-dmoi-v0.2.0/tables/units.jsonl')).toString().trim().split(/\r?\n/).map(JSON.parse);
const childMap=new Map();for(const r of side.units){if(r.parent_unit_id){assert.ok(map.has(r.parent_unit_id));if(!childMap.has(r.parent_unit_id))childMap.set(r.parent_unit_id,[]);childMap.get(r.parent_unit_id).push(r);}}
assert.deepEqual(m.exercises.map(r=>r.id),side.units.filter(r=>r.kind==='exercise').map(r=>r.unit_id));
assert.deepEqual(m.sections.map(r=>r.id),side.units.filter(r=>r.kind==='section').map(r=>r.unit_id));
function exact(r){const u=map.get(r.id);assert.ok(u);for(const key of ['native_id','kind','parent_unit_id','source_xpath','source_fragment_sha256','native_id_collision','original_id','assembly_id','route_granularity','containing_unit_id'])assert.deepEqual(r[key],u[key]);assert.deepEqual(r.routes.map(x=>x.path+'#'+x.anchor),u.reader_routes);for(const route of r.routes)assert.equal(route.url,'https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/B10/reader/'+route.path+'#'+route.anchor);}
function assertModel(model){
 assert.equal(new Set(model.sections.map(s=>s.titles.en)).size,36);
 for(const s of model.sections){exact(s);const n=native.find(n=>n.id===s.projected_unit_id);assert.equal(n.payload.native_unit_id,s.native_section_id);assert.equal(s.rights_id,n.payload.rights_id);assert.equal(s.titles.id,s.source_number+' · '+n.payload.title);assert.equal(n.payload.native_locator.identity_anchor,map.get(s.id).native_id);assert.equal(s.indonesian_route.exact_unit,false);}
 for(const e of model.exercises){exact(e);let parent=map.get(e.parent_unit_id);while(parent&&parent.kind!=='section')parent=map.get(parent.parent_unit_id);assert.equal(parent.unit_id,e.section_id);assert.equal(model.sections.find(s=>s.id===e.section_id).native_section_id,e.native_section_id);
  const owned={hint:[],answer:[],solution:[]};const descend=id=>{for(const c of childMap.get(id)??[]){if(['exercise','example'].includes(c.kind))continue;if(Object.hasOwn(owned,c.kind))owned[c.kind].push(c.unit_id);descend(c.unit_id);}};descend(e.id);
  for(const k of Object.keys(owned)){assert.deepEqual(e.support[k].map(r=>r.id),owned[k]);e.support[k].forEach(exact);}
 }
 assert.deepEqual(model.native_id_collisions,side.native_id_collisions);assert.equal(model.limits.native_capability_parity,false);
 assert.equal(model.limits.exact_indonesian_exercise_routes,false);assert.equal(model.reading_language,'en');
}
assertModel(m);
assert.deepEqual(m.unassigned_support,[{id:'levin-dmoi4:sec_seq-exponential-4-2-3',kind:'hint',owner:null}]);
const ctx={};vm.createContext(ctx);const controls=(await read('scripts/b10_selection_controls_v1.js')).toString();vm.runInContext(controls,ctx);const C=ctx.B10Selection;
let filterCases=0;for(const s of m.sections)for(const hint of ['all','with','without'])for(const answer of ['all','with','without'])for(const solution of ['all','with','without']){
 const filters={hint,answer,solution},expected=m.exercises.filter(e=>e.section_id===s.id&&Object.entries(filters).every(([k,v])=>v==='all'||Boolean(e.support[k].length)===(v==='with')));
 assert.deepEqual(Array.from(C.select(m,[s.id],filters),e=>e.id),expected.map(e=>e.id));filterCases++;
 if(expected.length)for(const locale of ['id','en']){const p=C.plan(m,[s.id],expected.map(e=>e.id),filters,{},locale);assert.deepEqual(Array.from(p.exercises,e=>e.id),expected.map(e=>e.id));const html=C.renderPlan(p,labels[locale]);assert.ok(html.includes(expected[0].routes[0].url));assert.equal(p.delivery.textbook_bodies_included,false);}
}
const negatives=[];function bad(name,fn){assert.throws(fn);negatives.push(name);}
const first=m.exercises[0],sec=[first.section_id];
bad('unknown section',()=>C.select(m,['unknown']));bad('duplicate section',()=>C.select(m,[...sec,...sec]));bad('invalid filter',()=>C.select(m,sec,{solution:'bad'}));
bad('unknown filter key',()=>C.select(m,sec,{mastery:true}));bad('nontext query',()=>C.select(m,sec,{query:4}));
bad('empty sections',()=>C.plan(m,[],[]));bad('empty exercises',()=>C.plan(m,sec,[]));bad('unknown exercise',()=>C.plan(m,sec,['other']));bad('duplicate exercise',()=>C.plan(m,sec,[first.id,first.id]));
bad('filtered out exercise',()=>C.plan(m,sec,[first.id],{query:'no-hit'}));bad('bad locale',()=>C.plan(m,sec,[first.id],{}, {},'fr'));
bad('bad intent field',()=>C.plan(m,sec,[first.id],{}, {rating:5}));bad('oversized intent',()=>C.plan(m,sec,[first.id],{}, {title:'x'.repeat(2001)}));
const forged=structuredClone(m);forged.exercises[0].section_id=m.sections[2].id;bad('wrong section mapping',()=>assertModel(forged));
const damaged=structuredClone(m);damaged.exercises.find(e=>e.support.solution.length).support.solution[0].source_fragment_sha256='0'.repeat(64);bad('support fragment corruption',()=>assertModel(damaged));
const example=side.units.find(u=>u.kind==='solution'&&map.get(u.parent_unit_id)?.kind==='example');assert.ok(example);const wrong=structuredClone(m);wrong.exercises[0].support.solution.push({id:example.unit_id});bad('example solution assigned to exercise',()=>assertModel(wrong));
const p=C.plan(m,sec,[first.id]);p.exercises[0]=structuredClone(p.exercises[0]);p.exercises[0].routes[0].url='javascript:alert(1)';bad('unsafe HTML route',()=>C.renderPlan(p,labels.id));
const uiCases=[];for(const path of ['B10.html','B10-en.html','B10-pengajar.html','B10-pengajar-en.html'])uiCases.push(testUI((await read(base+'/views/'+path)).toString(),(await read(base+'/views/b10-model.js')).toString(),controls,(await read('scripts/b10_selection_ui_v1.js')).toString()));
const before=hash(await read(base+'/manifest.json'));const rebuild=spawnSync(process.execPath,['scripts/build-b10-selection-v1.mjs'],{cwd:root,encoding:'utf8',timeout:60000});assert.equal(rebuild.status,0,rebuild.stderr);assert.equal(hash(await read(base+'/manifest.json')),before);
const result={schema:'b10-selection-validation/1',result:'pass',manifest:await fact(base+'/manifest.json'),validator:await fact('scripts/validate-b10-selection-v1.mjs'),ui_test_host:await fact('scripts/test_b10_ui_host_v1.mjs'),checks:{source_identities:true,sections:36,exercise_closures:768,filter_cases:filterCases,negative_fixtures:negatives,actual_ui_cases:uiCases,deterministic_second_build:true,public_readback:false,linguistic_review:false,whole_course_complete:false}};
await writeFile(resolve(root,base,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
