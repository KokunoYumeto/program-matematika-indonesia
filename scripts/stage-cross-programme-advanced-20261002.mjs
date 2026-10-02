// Capture the exact advanced successor without rewriting the earlier freeze.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,dirname,basename} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const out=resolve(root,'backend/cross-programme-v1');
const previous='inputs/20261002';
const target='inputs/20261002-801f1868';
const commit='801f186833b9811fa826575ef0717e78a5047ab0';
const tree='8eeace06b59e87edf32768851af3ed0d5bf5727a';
const repo='https://github.com/KokunoYumeto/open-mathematics-courses';
const hash=b=>createHash('sha256').update(b).digest('hex');
const encode=o=>Buffer.from(JSON.stringify(o,null,2)+'\n');
// A completed capture is immutable. Resume by checking its exact saved bytes,
// not by issuing requests or inventing a new capture timestamp.
let saved;
try{saved=JSON.parse(await readFile(resolve(out,target,'MANIFEST.json')));}
catch(error){if(error.code!=='ENOENT')throw error;}
if(saved){
  assert.equal(saved.schema,'cross-programme-input-freeze/1');
  assert.equal(saved.commits.advanced.commit,commit);assert.equal(saved.commits.advanced.tree,tree);
  const names=['advanced-courses.json','core-courses.js','core-learner-access.json','core-capsules.jsonl','phone-catalog.json','phone-recipe.json'];
  assert.deepEqual(saved.inputs.map(row=>row.path).sort(),names.map(name=>target+'/'+name).sort());
  for(const row of saved.inputs){
    const bytes=await readFile(resolve(out,row.path));
    assert.equal(bytes.length,row.bytes);assert.equal(hash(bytes),row.sha256);
  }
  const catalogue=JSON.parse(await readFile(resolve(out,target,'advanced-courses.json')));
  assert.equal(catalogue.courses.length,72);
  assert.equal(catalogue.courses.reduce((n,c)=>n+c.lessons.length,0),1061);
  console.log(JSON.stringify({state:'verified_existing_capture',path:target,files:saved.inputs.length,network_requests:0}));
  process.exit(0);
}
const old=JSON.parse(await readFile(resolve(out,previous,'MANIFEST.json')));
const inherited=[];
for(const row of old.inputs){
  const bytes=await readFile(resolve(out,row.path));
  assert.equal(bytes.length,row.bytes);assert.equal(hash(bytes),row.sha256);
  inherited.push({row,bytes});
}
async function freeze(path,bytes){
  await mkdir(dirname(path),{recursive:true});
  try{assert.deepEqual(await readFile(path),bytes);return;}
  catch(error){if(error.code!=='ENOENT')throw error;}
  await writeFile(path,bytes,{flag:'wx'});
}
let last=0;
async function get(url){
  await new Promise(r=>setTimeout(r,Math.max(0,2100-(Date.now()-last))));last=Date.now();
  const response=await fetch(url,{headers:{'User-Agent':'Open-Courses-exact-snapshot'},signal:AbortSignal.timeout(30000)});
  assert.equal(response.status,200,'HTTP '+response.status+' '+url);
  const bytes=Buffer.from(await response.arrayBuffer());
  assert.ok(bytes.length<2*1024*1024,'Bounded metadata/source response expected');
  return {bytes,origin:{url,status:200,bytes:bytes.length,sha256:hash(bytes)}};
}
const evidence=await get('https://api.github.com/repos/KokunoYumeto/open-mathematics-courses/commits/'+commit);
const revision=JSON.parse(evidence.bytes);assert.equal(revision.sha,commit);assert.equal(revision.commit.tree.sha,tree);
const current=await get('https://raw.githubusercontent.com/KokunoYumeto/open-mathematics-courses/'+commit+'/docs/courses.json');
const catalogue=JSON.parse(current.bytes);
assert.equal(catalogue.courses.length,72);
assert.equal(new Set(catalogue.courses.map(c=>c.id)).size,72);
for(const course of catalogue.courses){
  assert.ok(course.href.startsWith('courses/'));
  assert.equal(new Set(course.lessons.map(l=>l.id)).size,course.lessons.length);
  for(const lesson of course.lessons)assert.ok(lesson.href.startsWith('courses/'));
}
const consumer=await get('https://raw.githubusercontent.com/KokunoYumeto/open-mathematics-courses/'+commit+'/courses/RT-FIN/src/RT-FIN-01.md');
const inspectedConsumer='659942bdf47420e6665d59c4e80cf973867730d3b231d7e9c80ab8177bd83712';
const priorCatalogue=JSON.parse(inherited.find(x=>basename(x.row.path)==='advanced-courses.json').bytes);
const oldIds=new Set(priorCatalogue.courses.map(c=>c.id));
const currentIds=new Set(catalogue.courses.map(c=>c.id));
const inputs=[];
for(const {row,bytes} of inherited){
  const name=basename(row.path), path=target+'/'+name;
  const selected=name==='advanced-courses.json'?current.bytes:bytes;
  await freeze(resolve(out,path),selected);
  inputs.push({...row,path,bytes:selected.length,sha256:hash(selected),
    origin:name==='advanced-courses.json'?current.origin:row.origin});
}
const result={...old,captured_utc:new Date().toISOString(),
  commits:{...old.commits,advanced:{repository:repo,commit,tree,commit_date:revision.commit.committer.date}},
  inputs,
  revision_note:'Advanced public catalogue successor; original core and local R36 snapshots retained byte-for-byte. This is not admission of the later local R44 catalogue.',
  intake:{model:'gpt-6-astra',effort:'ultra',source_commit_evidence:hash(evidence.bytes),
    added_public_courses:catalogue.courses.filter(c=>!oldIds.has(c.id)).map(c=>({id:c.id,title:c.title,lessons:c.lessons.length})),
    removed_public_courses:[...oldIds].filter(id=>!currentIds.has(id)),
    courses:72,lessons:catalogue.courses.reduce((n,c)=>n+c.lessons.length,0),
    consumer_source:{...consumer.origin,matching_inspected_proof_snapshot:hash(consumer.bytes)===inspectedConsumer},
    proof_certification:false}};
assert.equal(result.intake.removed_public_courses.length,0,'Reconcile removed course IDs before switching snapshots');
await freeze(resolve(out,target,'MANIFEST.json'),encode(result));
console.log(JSON.stringify({state:'captured',path:target,...result.intake}));
