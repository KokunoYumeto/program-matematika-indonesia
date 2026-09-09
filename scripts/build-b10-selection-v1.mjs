import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {labels} from './b10_selection_labels_v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/b10-selection-v1';
const reader='docs/en/courses/B10/reader',native='backend/v2.3/extensions/b10-dmoi-v0.2.0/tables';
const read=p=>readFile(resolve(root,p));
const json=async p=>JSON.parse(await read(p));
const lines=async p=>(await read(p)).toString().trim().split(/\r?\n/).map(JSON.parse);
const sha=b=>createHash('sha256').update(b).digest('hex');
const fact=async p=>{const b=await read(p);return {path:p,bytes:b.length,sha256:sha(b)};};
const put=async(p,b)=>{await mkdir(dirname(resolve(root,base,p)),{recursive:true});await writeFile(resolve(root,base,p),b);};
const esc=x=>String(x).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const routeIndex=await json(reader+'/metadata/pretext-unit-routes.json');
const admission=await json('docs/en/courses/B10/B10_ORIGINAL_ENGLISH_ADMISSION_V1.json');
assert.equal(routeIndex.source_commit,admission.source_revision);
const units=routeIndex.units,byId=new Map(units.map(x=>[x.unit_id,x]));assert.equal(units.length,byId.size);
const nativeUnits=await lines(native+'/units.jsonl'),bindings=await lines(native+'/native_bindings.jsonl'),crosswalks=await lines(native+'/identity_crosswalks.jsonl');
const rights=(await lines(native+'/rights.jsonl')).map(x=>({id:x.id,...x.payload}));
const bindingMap=new Map(bindings.map(x=>[x.payload.subject_id,x.payload]));
const crosswalkMap=new Map(crosswalks.map(x=>[x.payload.target_id,x.payload]));
const sources=await Promise.all([reader+'/metadata/pretext-unit-routes.json','docs/en/courses/B10/B10_ORIGINAL_ENGLISH_ADMISSION_V1.json',...['units','native_bindings','identity_crosswalks','rights'].map(x=>native+'/'+x+'.jsonl')].map(fact));
const readerFiles=new Map();
async function sourcePage(path){if(!readerFiles.has(path)){const bytes=await read(reader+'/'+path);readerFiles.set(path,{bytes:bytes.length,sha256:sha(bytes),text:bytes.toString()});}return readerFiles.get(path).text;}
async function record(u){
 const routes=[];
 for(const route of u.reader_routes){
  assert.match(route,/^[A-Za-z0-9_.\/-]+\.html#[^\s<>"']+$/);assert.ok(!route.includes('..'));
  const [path,anchor]=route.split('#');const html=await sourcePage(path);
  const quoted=anchor.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');assert.match(html,new RegExp('\\bid=["\\\']'+quoted+'["\\\']'));
  routes.push({path,anchor,url:admission.reader+route});
 }
 assert.ok(routes.length,'missing reader route '+u.unit_id);
 return {id:u.unit_id,native_id:u.native_id,kind:u.kind,parent_unit_id:u.parent_unit_id,source_xpath:u.source_xpath,
  source_fragment_sha256:u.source_fragment_sha256,native_id_collision:u.native_id_collision,
  original_id:u.original_id,assembly_id:u.assembly_id,route_granularity:u.route_granularity,containing_unit_id:u.containing_unit_id,routes};
}
function ancestor(u,kind){const seen=new Set();while(u){assert.ok(!seen.has(u.unit_id),'cycle');seen.add(u.unit_id);if(u.kind===kind)return u;u=u.parent_unit_id?byId.get(u.parent_unit_id):null;}return null;}
function owner(u){const seen=new Set();while(u){assert.ok(!seen.has(u.unit_id));seen.add(u.unit_id);if(['exercise','example'].includes(u.kind))return u;u=u.parent_unit_id?byId.get(u.parent_unit_id):null;}return null;}
const sectionRecords=[];
for(const s of units.filter(x=>x.kind==='section')){
 const matches=nativeUnits.filter(x=>x.payload.native_unit_kind==='section'&&[s.authored_xml_id,s.authored_label,s.native_id].filter(Boolean).includes(x.payload.native_locator.identity_anchor));
 assert.equal(matches.length,1,'section join '+s.unit_id);const n=matches[0],p=n.payload;
 assert.equal(bindingMap.get(n.id)?.native_id,p.native_unit_id);assert.equal(crosswalkMap.get(n.id)?.source_id,p.native_unit_id);
 const r=await record(s),html=await sourcePage(r.routes[0].path),title=html.match(/<title>([^<]+)<\/title>/)?.[1];assert.ok(title);
 const start=html.indexOf('id="'+r.routes[0].anchor+'"'),heading=html.slice(start,html.indexOf('</h2>',start));
 const number=heading.match(/<span class="codenumber">([^<]+)<\/span>/)?.[1];assert.ok(number,'missing section number '+s.unit_id);
 sectionRecords.push({...r,projected_unit_id:n.id,native_section_id:p.native_unit_id,native_parent_id:p.parent_native_unit_id,
  native_source_file_sha256:p.source_file_sha256,native_target_file_sha256:p.target_file_sha256,
  source_number:number,titles:{id:number+' · '+p.title,en:number+' · '+title.replaceAll('&amp;','&').replaceAll('&#39;',"'").replaceAll('&quot;','"')},
  rights_id:p.rights_id,indonesian_route:{url:p.learner_route.url,scope:p.learner_route.route_state,exact_unit:false}});
}
const exerciseRecords=[];
for(const e of units.filter(x=>x.kind==='exercise')){
 const s=ancestor(e,'section');assert.ok(s,'exercise outside declared section');
 exerciseRecords.push({...await record(e),section_id:s.unit_id,native_section_id:sectionRecords.find(x=>x.id===s.unit_id).native_section_id,support:{hint:[],answer:[],solution:[]}});
}
const exerciseMap=new Map(exerciseRecords.map(x=>[x.id,x]));let exampleSolutions=0;const unowned=[];
for(const u of units.filter(x=>['hint','answer','solution'].includes(x.kind))){
 const o=owner(byId.get(u.parent_unit_id));
 if(o?.kind==='exercise')exerciseMap.get(o.unit_id).support[u.kind].push(await record(u));
 else if(o?.kind==='example'&&u.kind==='solution')exampleSolutions++;
 else unowned.push({id:u.unit_id,kind:u.kind,owner:o?.unit_id??null});
}
const counts={sections:sectionRecords.length,exercises:exerciseRecords.length,exercise_solution_nodes:exerciseRecords.reduce((n,e)=>n+e.support.solution.length,0),example_solution_nodes:exampleSolutions,
 solution_bearing_exercises:exerciseRecords.filter(e=>e.support.solution.length).length,hint_bearing_exercises:exerciseRecords.filter(e=>e.support.hint.length).length,
 answer_bearing_exercises:exerciseRecords.filter(e=>e.support.answer.length).length,answer_nodes:exerciseRecords.reduce((n,e)=>n+e.support.answer.length,0),
 solution_gaps:exerciseRecords.filter(e=>!e.support.solution.length).length};
assert.deepEqual(counts,{sections:36,exercises:768,exercise_solution_nodes:337,example_solution_nodes:183,solution_bearing_exercises:337,hint_bearing_exercises:127,answer_bearing_exercises:261,answer_nodes:826,solution_gaps:431});
assert.equal(unowned.length,1);assert.equal(unowned[0].kind,'hint');
const model={schema:'b10-exercise-selection/1',course_id:'B10',source_revision:admission.source_revision,source_tree:admission.source_tree,reading_language:'en',
 source_identities:sources,sections:sectionRecords,exercises:exerciseRecords,rights,native_id_collisions:routeIndex.native_id_collisions,counts,
 unassigned_support:unowned,indonesian_course:sectionRecords[0].indonesian_route.url,
 limits:{subsection_identity_mapping:false,source_body_included:false,exact_indonesian_exercise_routes:false,native_capability_parity:false,exercise_solutions_exclude_examples:true,conceptual_prerequisites_inferred:false}};
await put('data/model.json',JSON.stringify(model,null,2)+'\n');
await put('views/b10-model.js','globalThis.B10Model='+JSON.stringify(model).replaceAll('<','\\u003c')+';\n');
for(const [source,target] of [['scripts/b10_selection_controls_v1.js','views/b10-controls.js'],['scripts/b10_selection_ui_v1.js','views/b10-ui.js'],['scripts/a00_concept_styles_v1.css','views/b10.css']])await put(target,await read(source));
for(const locale of ['id','en'])for(const teacher of [false,true]){
 const L=labels[locale],suffix=locale==='en'?'-en':'',name='B10'+(teacher?'-pengajar':'')+suffix+'.html';
 const options=['hint','answer','solution'].map(k=>`<label>${L[k]}<select id="${k}"><option value="all">${L.all}</option><option value="with">${L.with}</option><option value="without">${L.without}</option></select></label>`).join('');
 const sectionList=sectionRecords.map((s,i)=>`<label><input type="checkbox" name="section" value="${esc(s.id)}"${i===0?' checked':''}><span>${esc(s.titles[locale])}</span></label>`).join('');
 const page={locale,teacher,labels:L};
 const fields=Object.entries(L.fields).map(([k,v])=>`<label>${v}<textarea id="intent-${k}" maxlength="2000" rows="2"></textarea></label>`).join('');
 await put('views/'+name,`<!doctype html><html lang="${locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none';script-src 'self';style-src 'self' 'unsafe-inline';base-uri 'none';form-action 'none'"><title>${esc(L.title)}</title><link rel="stylesheet" href="b10.css"></head><body><a class="skip" href="#main">${L.exercises}</a><header><strong>B10 · Discrete Mathematics</strong><nav><a href="https://kokunoyumeto.github.io/program-matematika-indonesia/${locale==='en'?'en/':''}">${L.home}</a><a href="B10${teacher?'':'-pengajar'}${suffix}.html">${teacher?L.learner:L.teacher}</a><a href="B10${teacher?'-pengajar':''}${locale==='en'?'':'-en'}.html" hreflang="${locale==='en'?'id':'en'}">${locale==='en'?'Bahasa Indonesia':'English'}</a></nav></header><main id="main"><h1>${L.title}</h1><p class="intro">${L.boundary}</p><p><a href="${esc(model.indonesian_course)}" hreflang="id">${L.indonesian}</a></p><p>${L.sourceNote}</p><div class="workspace"><section><h2>${L.sections}</h2><div class="module-list">${sectionList}</div></section><section><h2>${L.exercises}</h2><div class="controls">${options}<label>${L.query}<input id="query" type="search"></label></div><p id="count" role="status" aria-live="polite"></p><p>${L.selectionNote}</p><div class="controls"><button id="select-all" type="button">${L.selectAll}</button><button id="clear" type="button">${L.clear}</button></div><ol class="result-list" id="results"></ol><div class="pagination"><button id="previous" type="button">${L.previous}</button><span id="page"></span><button id="next" type="button">${L.next}</button></div></section></div><section><h2>${L.plan}</h2><p>${L.intentNote}</p><div class="study-plan-fields">${fields}</div><div class="controls"><button id="download-json" disabled type="button">${L.downloadJSON}</button><button id="download-html" disabled type="button">${L.downloadHTML}</button></div><p id="error" role="alert"></p><p>${L.planOffline}</p></section><noscript><p>${locale==='en'?'The exercise selector needs JavaScript. Section reading links remain available below.':'Pemilih latihan memerlukan JavaScript. Tautan bagian tersedia di bawah.'}</p></noscript><details><summary>${L.readSection}</summary><ul>${sectionRecords.map(s=>`<li><a href="${esc(s.routes[0].url)}" hreflang="en">${esc(s.titles[locale])}</a></li>`).join('')}</ul></details><section><h2>${L.provenance}</h2><p>Oscar Levin · Discrete Mathematics: An Open Introduction, 4th Edition · CC BY-NC-SA 4.0</p><p>${L.toolOffline}</p><p><a href="https://kokunoyumeto.github.io/program-matematika-indonesia/backend/b10/B10-selection-offline.zip">${L.offline}</a> · <a href="../data/model.json">JSON</a></p></section></main><script type="application/json" id="b10-page-data">${JSON.stringify(page).replaceAll('<','\\u003c')}</script><script src="b10-model.js"></script><script src="b10-controls.js"></script><script src="b10-ui.js"></script></body></html>\n`);
}
const outputs=['data/model.json','views/b10-model.js','views/b10-controls.js','views/b10-ui.js','views/b10.css',...['B10.html','B10-en.html','B10-pengajar.html','B10-pengajar-en.html'].map(x=>'views/'+x)];
const outputFacts=await Promise.all(outputs.map(async path=>({...await fact(base+'/'+path),path})));
await put('manifest.json',JSON.stringify({schema:'b10-selection-manifest/1',counts,source_revision:model.source_revision,
 sources,generators:await Promise.all(['scripts/build-b10-selection-v1.mjs','scripts/b10_selection_controls_v1.js','scripts/b10_selection_ui_v1.js','scripts/b10_selection_labels_v1.mjs','scripts/a00_concept_styles_v1.css'].map(fact)),
 reader_files:[...readerFiles].map(([path,{bytes,sha256}])=>({path:reader+'/'+path,bytes,sha256})).sort((a,b)=>a.path.localeCompare(b.path)),outputs:outputFacts,
 complete_native_parity:false,full_translation_review:false,public_readback:false},null,2)+'\n');
console.log(JSON.stringify({status:'built',counts,reader_pages_verified:readerFiles.size}));
