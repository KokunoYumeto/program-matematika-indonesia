// Add a source-bound consumer without replacing the existing native B10 adapter.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {sealB10} from './seal-b10-selection-public-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),base='backend/course-capsule-v1/adapters/b10-selection-v1',pub='docs/backend/b10';
const read=p=>readFile(resolve(root,p)),load=async p=>JSON.parse(await read(p));
const fact=async path=>{const b=await read(path);return {path,bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')};};
const write=async(p,b)=>{await mkdir(dirname(resolve(root,p)),{recursive:true});await writeFile(resolve(root,p),b);};
const manifest=await load(base+'/manifest.json'),qa=await load(base+'/validation.json'),pack=await load(base+'/package.json');
assert.equal(qa.result,'pass');assert.deepEqual(qa.manifest,await fact(base+'/manifest.json'));
assert.deepEqual(qa.validator,await fact('scripts/validate-b10-selection-v1.mjs'));assert.deepEqual(qa.ui_test_host,await fact('scripts/test_b10_ui_host_v1.mjs'));
assert.equal(qa.checks.exercise_closures,768);assert.equal(qa.checks.sections,36);assert.equal(qa.checks.filter_cases,972);
assert.equal(qa.checks.actual_ui_cases.length,4);assert.ok(qa.checks.actual_ui_cases.every(c=>c.actual_handlers&&c.individual_selection&&c.all_exercises_export===768));assert.equal(qa.checks.deterministic_second_build,true);
for(const item of [...manifest.sources,...manifest.generators,...manifest.reader_files])assert.deepEqual(await fact(item.path),item);
for(const item of manifest.outputs)assert.deepEqual(await fact(base+'/'+item.path),{...item,path:base+'/'+item.path});
const replay=spawnSync('python',['-B','scripts/package_b10_selection_v1.py','--verify-only'],{cwd:root,encoding:'utf8',timeout:30000});assert.equal(replay.status,0,replay.stderr);
assert.equal(pack.result,'pass');assert.equal((await fact(base+'/'+pack.path)).sha256,pack.sha256);
for(const path of [...manifest.outputs.map(r=>r.path),'manifest.json','validation.json','package.json',pack.path]){
 const target=path==='manifest.json'?'source-manifest.json':path.startsWith('views/')?path.slice(6):path;let bytes=await read(base+'/'+path);
 if(path.endsWith('.html'))bytes=Buffer.from(bytes.toString().replaceAll('href="../data/','href="data/').replaceAll('href="../B10-selection-offline.zip"','href="B10-selection-offline.zip"'));
 await write(pub+'/'+target,bytes);
}
await write(pub+'/learning-map.json',await read(base+'/data/model.json'));
await sealB10();
const evidence=[];for(const [kind,path] of [['b10_selection_manifest',base+'/manifest.json'],['b10_selection_validation',base+'/validation.json']]){const f=await fact(path);evidence.push({kind,locator:path,bytes:f.bytes,sha256:f.sha256,verified_date:'2026-09-08'});}
const scope='36 bagian, 768 latihan; petunjuk, jawaban dan 337 solusi latihan sumber. Bacaan Inggris; pilihan bagian/latihan dan rencana HTML/JSON. Bukan penilaian penguasaan.';
const path='backend/course-capsule-v1/authority/integration-overrides-v1.json',o=await load(path);assert.equal(o.semantic_adapters.B10.contract_version,'2.3.1');
o.semantic_adapters.B10.evidence=[...o.semantic_adapters.B10.evidence.filter(r=>!evidence.some(e=>e.kind===r.kind)),...evidence];
o.native_capabilities.B10??={};for(const key of ['unit_identity','educator_unit_alignment'])o.native_capabilities.B10[key]={status:'verified',evidence};
const existing=o.educator_evidence.B10??{},resources=(existing.resources??[]).filter(r=>!r.id.startsWith('B10:selection-'));
for(const [id,title,file,type] of [['teacher','Pilihan latihan B10 untuk pengajar','B10-pengajar.html','educator-data'],['teacher-en','B10 exercise selection for educators','B10-pengajar-en.html','educator-data'],['model','Identitas bagian dan latihan B10','data/model.json','curriculum-map'],['offline','Pemilih B10 luring','B10-selection-offline.zip','offline-metadata-tools']]){const f=await fact(pub+'/'+file);resources.push({id:'B10:selection-'+id,title,resource_type:type,status:'verified',scope,url:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/b10/'+file,bytes:f.bytes,sha256:f.sha256});}
const teacher=await fact(pub+'/B10-pengajar.html');o.educator_evidence.B10={...existing,status:'verified',verified_date:'2026-09-08',locator:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/b10/B10-pengajar.html',bytes:teacher.bytes,sha256:teacher.sha256,features:['exercise_bank','solution_provenance','remix_selectors'],resources};
await write(path,JSON.stringify(o,null,2)+'\n');
const tp='backend/authority/learner-tools-overrides-v1.json',t=await load(tp);let course=t.courses.find(r=>r.course_id==='B10');if(!course){course={course_id:'B10',tools:[]};t.courses.push(course);}
course.tools=[...course.tools.filter(r=>r.tool_id!=='b10-selection-v1'),{tool_id:'b10-selection-v1',label:'B10 · Pilihan latihan dan rencana belajar',href:'backend/b10/B10.html',action_kind:'course_reader',scope,state:'verified',primary:false,machine_data_is_learner_destination:false,page_path:pub+'/B10.html',resource_path:pub+'/learning-map.json',evidence_path:pub+'/validation.json',limitations:['Bacaan latihan berbahasa Inggris; tautan buku Indonesia tetap tersedia.','Tautan jawaban menuju unit yang memuatnya, bukan jangkar jawaban tersendiri.','Paket luring memuat pemilih dan metadata, bukan teks buku.','Tidak ada prasyarat konseptual atau penilaian penguasaan yang disimpulkan.']}];
await write(tp,JSON.stringify(t,null,2)+'\n');console.log(JSON.stringify({status:'pass',course:'B10',preserved_native_adapter:'2.3.1',producer_corpus_modified:false,scope}));
