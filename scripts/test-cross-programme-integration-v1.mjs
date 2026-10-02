import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,dirname,basename} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const dir=resolve(root,'backend/cross-programme-v1');
const hash=b=>createHash('sha256').update(b).digest('hex');
const load=async p=>JSON.parse(await readFile(resolve(dir,p),'utf8'));
const bridge=await load('bridge.json');let tests=0;
const privateProfileName=basename(process.env.USERPROFILE??'no-private-profile');
function ok(predicate,label){assert.ok(predicate,label);tests++;}
function validate(j){
  ok(j.schema==='open-courses-cross-programme/1','schema');
  const nodes=[...j.courses.core.map(c=>'core:'+c.id),...j.courses.advanced.map(c=>'advanced:'+c.id)];
  ok(new Set(nodes).size===nodes.length,'unique native namespaces');
  ok(j.courses.core.length===40&&j.courses.advanced.length===71,'exact source-snapshot counts');
  const endpoints=new Set(nodes);const ids=new Set();
  for(const e of j.edges){ok(endpoints.has(e.from)&&endpoints.has(e.to),'both native endpoints exist');ok(!ids.has(e.id),'unique edge');ids.add(e.id);ok(e.mathematical_correspondence==='not_checked'&&e.proof_closed===false,'course edge never certifies proof');}
  for(const n of nodes){const expected=j.edges.filter(e=>e.to===n).map(e=>e.from).sort();assert.deepEqual(j.reverse_dependencies[n],expected,'exact reverse relation');tests++;}
  let lessons=0;for(const c of j.courses.advanced){const lessonIds=new Set();for(const l of c.lessons){ok(!lessonIds.has(l.id),'unique native lesson');lessonIds.add(l.id);ok(new URL(l.route).origin==='https://kokunoyumeto.github.io'&&l.route.includes('/open-mathematics-courses/'),'same public advanced programme');lessons++;}ok(c.content_language==='en','actual advanced source language');}
  ok(lessons===951&&j.counts.published_advanced_lessons===951,'951 distinct source-declared lessons');
  for(const c of j.courses.core){ok(c.capsule.id===c.id,'native capsule join');for(const locale of ['en','id'])ok(c.routes[locale].includes('/'+locale+'/'),'locale-specific routing');}
  ok(j.native_phone_exchange.reading_edges.length===48,'48 hash-bound native reading edges');
  for(const e of j.native_phone_exchange.reading_edges){ok(/^[0-9a-f]{64}$/i.test(e.from_source_sha256)&&/^[0-9a-f]{64}$/i.test(e.target_source_sha256),'exact native hash pair');ok(e.proof_closed===false,'native reading is not proof closure');}
  for(const p of j.native_phone_exchange.reported_providers)ok(p.independent_proof_check===false&&p.whole_prerequisite_closure===false&&p.public_route===null,'reported local provider has no fabricated published proof');
  ok(j.counts.independently_verified_cross_programme_proof_matches===0,'no invented completed proof correspondences');
  ok(j.production_provenance.model==='gpt-6.1-sol'&&j.production_provenance.effort==='ultra','actual bounded current-turn attribution');
  return nodes;
}
const nodes=validate(bridge),positiveTests=tests;
const mutations=[['missing endpoint',j=>j.edges[0].to='core:FAKE'],['false proof closure',j=>j.edges[0].proof_closed=true],['false checked statement',j=>j.edges[0].mathematical_correspondence='exact'],['missing reverse edge',j=>j.reverse_dependencies[j.edges[0].to]=[]],['duplicate node',j=>j.courses.advanced[0].id=j.courses.advanced[1].id],['duplicate edge',j=>j.edges.push(j.edges[0])],['language misrepresentation',j=>j.courses.advanced[0].content_language='id'],['made-up proof URL',j=>j.native_phone_exchange.reported_providers[0].public_route='https://example.com/proof'],['bad native source hash',j=>j.native_phone_exchange.reading_edges[0].target_source_sha256='bad'],['count inflation',j=>j.counts.independently_verified_cross_programme_proof_matches=1]];
const negative=[];for(const [name,mutate] of mutations){const j=structuredClone(bridge);mutate(j);assert.throws(()=>validate(j),undefined,name);negative.push({name,rejected:true});}
// Preparation cycles are documentary findings. They are not solved by asserting
// that this graph is a proof DAG; exact preliminary lemmas need separate work.
let index=0;const stack=[],onStack=new Set(),indices=new Map(),low=new Map(),components=[];
function visit(v){indices.set(v,index);low.set(v,index++);stack.push(v);onStack.add(v);for(const w of bridge.edges.filter(e=>e.from===v).map(e=>e.to)){if(!indices.has(w)){visit(w);low.set(v,Math.min(low.get(v),low.get(w)));}else if(onStack.has(w))low.set(v,Math.min(low.get(v),indices.get(w)));}if(low.get(v)===indices.get(v)){const component=[];let w;do{w=stack.pop();onStack.delete(w);component.push(w);}while(w!==v);if(component.length>1)components.push(component.sort());}}
for(const n of nodes)if(!indices.has(n))visit(n);
const pages=[];
for(const locale of ['en','id']){
  const path='docs/'+locale+'/programme/index.html';const b=await readFile(resolve(dir,'public-staging',path));const text=b.toString('utf8');
  const ids=[...text.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);ok(new Set(ids).size===ids.length,'unique rendered anchors');
  const anchors=new Set(ids);for(const m of text.matchAll(/href="#([^"]+)"/g))ok(anchors.has(m[1]),'rendered preparation and reverse anchor exists');
  for(const n of nodes)ok(anchors.has(n.replace(':','-')),'every course in learner outline');
  ok(!/<script\b/i.test(text),'full outline needs no JavaScript');ok(text.includes('GPT-6.1 Sol')&&text.includes('Ultra'),'visible actual model and effort');
  ok(!/[A-Z]:\\|file:\/\/|API_TOKEN|Bearer /.test(text)&&!text.includes(privateProfileName),'no private paths/credentials/public profile attribution');
  pages.push({path,bytes:b.length,sha256:hash(b),course_anchors:111});
}
const reconciled=await load('PUBLIC_BASELINE_RECONCILIATION.json');for(const f of reconciled.outputs){const b=await readFile(resolve(dir,'public-staging',f.path));assert.equal(b.length,f.bytes);assert.equal(hash(b),f.sha256);}
const receipt={schema:'cross-programme-integration-qa/1',status:'pass',positive_structural_assertions:positiveTests,negative_tests:negative,preparation_cycle_components:components,cycle_disposition:'Reading routes only. No cyclic proof dependency is admitted or resolved by these links.',published_snapshot_counts:bridge.counts,pages,public_baseline_roundtrip:'pass',changed_files:reconciled.explicit_changed_paths,proof_correspondence_complete:false};
await writeFile(resolve(dir,'VALIDATION.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({status:'pass',positive_structural_assertions:positiveTests,negative:negative.length,reading_cycles:components.length,exact_staging_files:reconciled.outputs.length}));
