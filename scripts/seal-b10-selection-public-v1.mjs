import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),base='backend/course-capsule-v1/adapters/b10-selection-v1',pub='docs/backend/b10';
const hash=b=>createHash('sha256').update(b).digest('hex');
const identity=(path,b)=>({path,bytes:b.length,sha256:hash(b)});
export async function sealB10(){
 const read=p=>readFile(resolve(root,p));const source=JSON.parse(await read(base+'/manifest.json'));
 let overlay;try{overlay=JSON.parse(await read('backend/authority/central-course-surface-navigation-overlay-v1.json'));}catch(e){if(e.code!=='ENOENT')throw e;}
 const files=[];
 for(const r of [...source.outputs,{path:'manifest.json'},{path:'validation.json'},{path:'package.json'},{path:'B10-selection-offline.zip'}]){
  const sourceBytes=await read(base+'/'+r.path);if(r.sha256)assert.equal(hash(sourceBytes),r.sha256);
  const target=r.path==='manifest.json'?'source-manifest.json':r.path.replace(/^views\//,'');let projected=sourceBytes;
  if(r.path.endsWith('.html'))projected=Buffer.from(sourceBytes.toString().replaceAll('href="../data/','href="data/').replaceAll('href="../B10-selection-offline.zip"','href="B10-selection-offline.zip"'));
  const actual=await read(pub+'/'+target);let transformation='byte-identical';
  if(!actual.equals(projected)){
   const row=overlay?.files.find(x=>x.document===pub+'/'+target);assert.ok(row,'unexplained public-byte transformation '+target);
   assert.equal(row.source_body_replay_exact,true);assert.ok(row.course_ids.includes('B10'));
   assert.deepEqual(row.source_body,identity(pub+'/'+target,projected));assert.deepEqual(row.hosted_surface,identity(pub+'/'+target,actual));transformation='public-link-depth-and-reversible-navigation';
  }else if(!sourceBytes.equals(projected))transformation='public-link-depth';
  files.push({...identity(target,actual),source:identity(base+'/'+r.path,sourceBytes),transformation});
 }
 const model=await read(pub+'/data/model.json'),alias=await read(pub+'/learning-map.json');assert.deepEqual(alias,model);
 files.push({...identity('learning-map.json',alias),source:identity(base+'/data/model.json',model),transformation:'byte-identical-alias'});
 const manifest={schema:'b10-selection-public-manifest/1',course_id:'B10',counts:source.counts,files,source_manifest:'source-manifest.json',
  stage:'current_local_public_projection',public_network_readback:false,whole_course_complete:false};
 await writeFile(resolve(root,pub,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');return {state:'pass',public_files:files.length};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))console.log(JSON.stringify(await sealB10()));
