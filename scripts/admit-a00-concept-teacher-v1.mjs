// Add this consumer to the existing A00 adapter, never replace its native corpus.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/a00-concept-teacher-v1',publicBase='docs/backend/a00';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const load=async path=>JSON.parse(await readFile(resolve(root,path),'utf8'));
const fact=async path=>{const bytes=await readFile(resolve(root,path));return {path,bytes:bytes.length,sha256:hash(bytes)};};
const manifest=await load(base+'/manifest.json'),validation=await load(base+'/validation.json'),pack=await load(base+'/package.json');
assert.equal(validation.result,'pass');assert.equal(validation.manifest.sha256,(await fact(base+'/manifest.json')).sha256);
assert.equal(validation.validator.sha256,(await fact('scripts/validate-a00-concept-teacher-v1.mjs')).sha256);
assert.deepEqual(validation.ui_test_host,await fact('scripts/test_a00_ui_host_v1.mjs'));
assert.equal(validation.checks.actual_ui_host_cases.length,4);
assert.ok(validation.checks.actual_ui_host_cases.every(row=>row.actual_ui_handlers&&row.module_and_solution_and_query_filters));
assert.ok(validation.checks.actual_ui_host_cases.filter(row=>row.teacher).every(row=>row.study_plan_exports));
assert.equal(validation.checks.source_bound_study_plan_cases,35);assert.equal(validation.checks.readable_plan_locales,2);
assert.equal(validation.checks.deterministic_second_build,true);assert.equal(validation.checks.module_category_solution_cases,2250);
assert.ok(validation.checks.negative_fixtures.length>=11);assert.ok(validation.checks.negative_fixtures.every(row=>row.result==='rejected'));
for(const source of manifest.generators)assert.deepEqual(await fact(source.path),source);
assert.equal(pack.result,'pass');assert.equal(pack.sha256,(await fact(base+'/'+pack.path)).sha256);
// Admission verifies the bytes that will actually be copied, not only an older
// successful QA receipt. The read-only replay also checks every ZIP member.
assert.deepEqual(await fact(base+'/input/source-lock.json'),{...manifest.input,path:base+'/input/source-lock.json'});
for(const item of manifest.outputs)assert.deepEqual(await fact(base+'/'+item.path),{...item,path:base+'/'+item.path});
const packageReplay=spawnSync('python',['-B',resolve(root,'scripts/package_a00_concept_teacher_v1.py'),'--verify-only'],
  {cwd:root,encoding:'utf8',timeout:30000,maxBuffer:1024*1024});
assert.equal(packageReplay.status,0,`A00 package/loose-file replay failed: ${packageReplay.stderr||packageReplay.error||''}`);
const outputs=manifest.outputs.map(item=>item.path);
const lock=await load(base+'/input/source-lock.json');
for(const item of lock.snapshots)assert.deepEqual(await fact(base+'/input/'+item.path),{...item,path:base+'/input/'+item.path});
outputs.push(...lock.snapshots.map(item=>'input/'+item.path),'input/source-lock.json','manifest.json','validation.json',pack.path,'package.json');
for(const path of outputs){
  const target=path.startsWith('views/')?path.slice(6):path;
  const source=await readFile(resolve(root,base,path));
  const bytes=path.endsWith('.html')?Buffer.from(source.toString().replaceAll('../data/','data/').replaceAll('../input/','input/')):source;
  await mkdir(dirname(resolve(root,publicBase,target)),{recursive:true});await writeFile(resolve(root,publicBase,target),bytes);
}
await writeFile(resolve(root,publicBase,'learning-map.json'),await readFile(resolve(root,base,'data/learning-map.json')));
const evidence=[];
for(const [kind,path] of [['a00_concept_teacher_manifest',base+'/manifest.json'],['a00_concept_teacher_validation',base+'/validation.json'],['a00_concept_source_lock',base+'/input/source-lock.json']]){
  const {bytes,sha256}=await fact(path);evidence.push({kind,locator:path,bytes,sha256,verified_date:'2026-09-08'});
}
const scope='35 konsep dan 76 prasyarat; 75 modul, 8.105 latihan/contoh, 5.240 solusi sumber dan 2.865 ketiadaan solusi. Pilihan metadata, bukan penilaian penguasaan atau pengaitan otomatis latihan ke konsep.';
const overridePath='backend/course-capsule-v1/authority/integration-overrides-v1.json',override=await load(overridePath);
assert.equal(override.semantic_adapters.A00.contract_version,'2.3.1');
const oldEvidence=override.semantic_adapters.A00.evidence.filter(row=>!evidence.some(e=>e.kind===row.kind));
override.semantic_adapters.A00={...override.semantic_adapters.A00,evidence:[...oldEvidence,...evidence]};
override.native_capabilities.A00??={};
for(const name of ['unit_identity','educator_unit_alignment'])override.native_capabilities.A00[name]={status:'verified',evidence};
const educator=override.educator_evidence.A00??{},resources=(educator.resources??[]).filter(row=>!row.id.startsWith('A00:concept-'));
for(const [id,title,path,type] of [['educator','Pilihan konsep, modul dan latihan A00 untuk pengajar','A00-pengajar.html','educator-data'],
  ['educator-en','A00 concepts, modules and exercise selection for educators','A00-pengajar-en.html','educator-data'],
  ['map','Identitas konsep, prasyarat dan modul A00','data/learning-map.json','curriculum-map'],
  ['offline','Peta dan pemilih A00 untuk penggunaan luring','A00-concept-teacher-offline.zip','offline-metadata-tools']]){
  const identity=await fact(publicBase+'/'+path);resources.push({id:'A00:concept-'+id,title,resource_type:type,status:'verified',
    url:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/a00/'+path,scope,bytes:identity.bytes,sha256:identity.sha256});
}
const teacher=await fact(publicBase+'/A00-pengajar.html');
override.educator_evidence.A00={...educator,status:'verified',verified_date:'2026-09-08',
  locator:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/a00/A00-pengajar.html',
  bytes:teacher.bytes,sha256:teacher.sha256,features:['exercise_bank','solution_provenance','remix_selectors','outcome_evidence_map'],resources};
await writeFile(resolve(root,overridePath),JSON.stringify(override,null,2)+'\n');
const toolsPath='backend/authority/learner-tools-overrides-v1.json',tools=await load(toolsPath);
const course=tools.courses.find(row=>row.course_id==='A00');assert.ok(course.tools.some(row=>row.tool_id==='a00-assessment-map-v1'));
course.tools=[...course.tools.filter(row=>row.tool_id!=='a00-concept-teacher-v1'),{
  tool_id:'a00-concept-teacher-v1',label:'A00 · Konsep, prasyarat dan pilihan belajar',href:'backend/a00/A00.html',
  action_kind:'course_reader',scope,state:'verified',primary:false,machine_data_is_learner_destination:false,
  page_path:publicBase+'/A00.html',resource_path:publicBase+'/learning-map.json',evidence_path:publicBase+'/validation.json',
  limitations:['Buku yang ditautkan berbahasa Indonesia; antarmuka tersedia dalam Bahasa Indonesia dan Inggris.',
    'Prasyarat adalah hubungan konsep, bukan skor atau urutan belajar otomatis.',
    'Latihan dipilih menurut modul; tidak ada pengaitan latihan ke konsep yang disimpulkan.',
    'Paket luring memuat metadata dan pemilih, bukan isi buku.']}];
await writeFile(resolve(root,toolsPath),JSON.stringify(tools,null,2)+'\n');
console.log(JSON.stringify({status:'pass',course:'A00',preserved_adapter:'2.3.1',native_corpus_modified:false,public_files:outputs.length+1}));
