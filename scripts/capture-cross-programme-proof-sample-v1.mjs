import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const dir=resolve(root,'backend/cross-programme-v1/proof-sample');
const native=resolve(root,'../reader_mirrors/hefferon-original-en-20260909');
const hash=b=>createHash('sha256').update(b).digest('hex');
const fact=(path,b)=>({path,bytes:b.length,sha256:hash(b)});
if(process.argv.includes('--check')){
  const manifest=JSON.parse(await readFile(resolve(dir,'MANIFEST.json'),'utf8'));
  for(const row of manifest.files){const b=await readFile(resolve(dir,row.path));assert.equal(b.length,row.bytes);assert.equal(hash(b),row.sha256);}
  for(const row of manifest.native_locators)for(const f of row.source_fragments){const b=await readFile(resolve(dir,'core',f.path));assert.equal(hash(b.subarray(f.byte_start,f.byte_end)),f.sha256);}
  console.log(JSON.stringify({state:'proof_sample_exact_replay_pass',files:manifest.files.length,native_locators:manifest.native_locators.length,network_calls:0}));process.exit(0);
}
async function frozenWrite(path,b){await mkdir(dirname(path),{recursive:true});try{assert.deepEqual(await readFile(path),b);return;}catch(e){if(e.code!=='ENOENT')throw e;}await writeFile(path,b,{flag:'wx'});}
const freeze=JSON.parse(await readFile(resolve(root,'backend/cross-programme-v1/inputs/20261002/MANIFEST.json'),'utf8'));
const commit=freeze.commits.advanced.commit;
const paths=['courses/RT-FIN/src/RT-FIN-01.md','docs/courses/RT-FIN/representations-and-complete-reducibility.html'];
const files=[];
for(const path of paths){const url='https://raw.githubusercontent.com/KokunoYumeto/open-mathematics-courses/'+commit+'/'+path;const r=await fetch(url,{signal:AbortSignal.timeout(30000)});assert.equal(r.status,200);const b=Buffer.from(await r.arrayBuffer());const local=path.endsWith('.md')?'advanced/RT-FIN-01.md':'advanced/RT-FIN-01.html';await frozenWrite(resolve(dir,local),b);files.push({...fact(local,b),url,commit});}
for(const path of ['src/vs/vs2.tex','src/vs/vs3.tex','src/vs/fields.tex']){const b=await readFile(resolve(native,'authority',path));const local='core/'+path;await frozenWrite(resolve(dir,local),b);files.push({...fact(local,b),source_commit:'df2262e089a02651c127f1dd12649c4622ee1383',native_source_path:path});}
const index=JSON.parse(await readFile(resolve(native,'semantic-pilot-vs3/rendered-unit-index.json'),'utf8'));
const prerequisiteIndex=JSON.parse(await readFile(resolve(native,'semantic-pilot-vs2/rendered-unit-index.json'),'utf8'));
const all=[...index.units,...prerequisiteIndex.units];
const ids=['r005.hefferon-linear-algebra.unit.file.src.vs.vs3.tex.corollary.label.b186ad4cc75572f666a6','r005.hefferon-linear-algebra.unit.file.src.vs.vs3.tex.proof.source-order.0006','r005.hefferon-linear-algebra.unit.file.src.vs.vs3.tex.proof.source-order.0003','r005.hefferon-linear-algebra.unit.file.src.vs.vs3.tex.proof.source-order.0004','r005.hefferon-linear-algebra.unit.file.src.vs.vs3.tex.proof.source-order.0005','r005.hefferon-linear-algebra.unit.file.src.vs.vs2.tex.proof.source-order.0004'];
const locators=[];for(const id of ids){const u=all.find(x=>x.unit_id===id);assert.ok(u);for(const f of u.source_fragments){const b=await readFile(resolve(native,'authority',f.path));assert.equal(hash(b.subarray(f.byte_start,f.byte_end)),f.sha256);}locators.push({native_unit_id:id,kind:u.kind,number:u.number,language:'en',revision:index.source_commit,source_fragments:u.source_fragments,public_proof_anchor:null});}
await frozenWrite(resolve(dir,'MANIFEST.json'),Buffer.from(JSON.stringify({schema:'cross-programme-proof-sample-freeze/1',files,native_locators:locators,reading_scope:'Only the stated downstream lesson and complete selected basis-extension proof/prerequisite chain; not a whole corpus mathematical audit',source_bytes_unchanged:true},null,2)+'\n'));
console.log(JSON.stringify({state:'proof_sample_frozen',files:files.length,native_locators:locators.length}));
