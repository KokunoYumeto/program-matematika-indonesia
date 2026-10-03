import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadHumanAnalysisRoutes,validateHumanAnalysis,renderHumanAnalysisRoutes} from './human-analysis-routes-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/cross-programme-v1/inputs/lebl-public-20261003/';
const registry=JSON.parse(await readFile(resolve(root,base+'REGISTRY.json')));
const receipt=JSON.parse(await readFile(resolve(root,base+'READBACK.json')));
const ids=new Set(['C10','C20','B30','C50','C90']);
const data=await loadHumanAnalysisRoutes(root,ids);
assert.equal(data.routes.length,7);assert.equal(data.routes.reduce((n,r)=>n+r.course_ids.length,0),10);
const mutations=[
  (r,c)=>{r.routes.pop();},(r,c)=>{r.routes[0]=r.routes[1];},
  (r,c)=>{r.routes[0].reader=r.routes[0].reader.replace('open-math-courses','open-mathematics-courses');},
  (r,c)=>{c.routes[0].sha256='0'.repeat(64);},(r,c)=>{c.routes[0].source_label='sec:wrong';},
  (r,c)=>{c.routes[0].mathematical_consumer_equivalence='proved';},
  (r,c)=>{r.routes[0].author='AI';},(r,c)=>{r.routes[0].licence='CC0';},
  (r,c)=>{c.routes[0].verified_declared_anchors=0;},(r,c)=>{c.anonymous=false;},
  (r,c)=>{r.routes[0].source_archive_member='../secret.tex';},
  (r,c)=>{c.whole_course_or_dependency_completion_claimed=true;},
];
for(const mutate of mutations){const r=structuredClone(registry),c=structuredClone(receipt);mutate(r,c);assert.throws(()=>validateHumanAnalysis(r,c,ids));}
await assert.rejects(()=>loadHumanAnalysisRoutes(root,ids,async p=>p.endsWith('REGISTRY.json')?Buffer.from(JSON.stringify({...registry,note:'changed'})):readFile(resolve(root,p))));
assert.throws(()=>validateHumanAnalysis(registry,receipt,new Set(['C10'])));
for(const locale of ['en','id'])for(const id of ids){
  const html=renderHumanAnalysisRoutes(data,id,locale);
  assert.ok(html.includes('hreflang="en"'));
  assert.ok(html.includes('Jiří Lebl')&&html.includes('CC-BY-SA-4.0'));
  assert.ok(!html.includes('open-mathematics-courses/'));
  assert.equal((html.match(/data-human-analysis-route=/g)||[]).length,data.routes.filter(r=>r.course_ids.includes(id)).length);
}
assert.equal(renderHumanAnalysisRoutes(data,'A00','en'),'');
console.log(JSON.stringify({state:'pass',routes:7,course_placements:10,localized_panels:10,negative_fixtures:mutations.length+2}));
