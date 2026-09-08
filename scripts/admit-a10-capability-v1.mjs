// Add consumer capability without replacing the existing A10 v2.3.1 adapter.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/a10-capability-v1';
const publicBase='docs/backend/a10';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const load=async path=>JSON.parse(await readFile(resolve(root,path),'utf8'));
const identity=async path=>{const bytes=await readFile(resolve(root,path));return {path,bytes:bytes.length,sha256:hash(bytes)};};
const manifest=await load(base+'/manifest.json');
const validation=await load(base+'/validation.json');
assert.equal(manifest.schema,'a10-capability-manifest/1');
assert.equal(validation.result,'pass');
assert.equal(validation.manifest_sha256,(await identity(base+'/manifest.json')).sha256);
assert.equal(validation.checks.independent_second_build_byte_identical,true);
assert.equal(validation.checks.generator_source_hashes_verified,true);
assert.equal(validation.validator_sha256,(await identity('scripts/validate_a10_capability_v1.py')).sha256);
for(const generator of manifest.generators) assert.deepEqual(await identity(generator.path),generator);
assert.equal(validation.navigation_tests.result,'pass');
assert.equal(validation.navigation_tests.views,4);
assert.equal(validation.navigation_tests.module_filter_cases,984);
assert.equal(validation.negative_fixtures.length,12);
assert.ok(validation.negative_fixtures.every(row=>row.result==='rejected'));
assert.deepEqual(manifest.counts,validation.counts);
assert.equal(manifest.counts.exercises,9406);
assert.equal(manifest.counts.solutions,6106);
assert.equal(manifest.counts.missing_solutions,3300);
assert.equal(manifest.counts.verified_exercise_reading_routes,0);
const mapped=[];
for(const item of manifest.outputs) {
  assert.deepEqual(await identity(base+'/'+item.path),{...item,path:base+'/'+item.path});
  if(item.path==='README.md') continue;
  let target;
  if(item.path.startsWith('views/')) target=publicBase+'/'+item.path.slice(6);
  else if(item.path==='input/source-lock.json') target=publicBase+'/source-lock.json';
  else if(item.path.startsWith('data/')) target=publicBase+'/'+item.path;
  else throw new Error('Unknown A10 publication mapping: '+item.path);
  const source=await readFile(resolve(root,base,item.path));
  const payload=item.path.endsWith('.html') ? Buffer.from(source.toString('utf8').replaceAll('../data/','data/').replaceAll('../validation.json','validation.json')) : source;
  await mkdir(dirname(resolve(root,target)),{recursive:true});
  await writeFile(resolve(root,target),payload);
  mapped.push({source:base+'/'+item.path,...await identity(target)});
}
for(const [source,target] of [[base+'/manifest.json',publicBase+'/manifest.json'],[base+'/validation.json',publicBase+'/validation.json'],[base+'/data/learning-map.json',publicBase+'/learning-map.json']]) {
  await writeFile(resolve(root,target),await readFile(resolve(root,source)));
  mapped.push({source,...await identity(target)});
}
const limits=[
  '82 rute PDF membuka awal modul, bukan halaman latihan atau solusi tertentu.',
  '9.406 identitas latihan dipertahankan: 6.106 memiliki solusi sumber dan 3.300 tidak. Nomor urutan bukan nomor soal tercetak.',
  '600 catatan istilah terkurasi berbeda dari 460 kemunculan sumber. Riwayat penggantian istilah tetap terlihat.',
  'Pemilih pengajar mengekspor metadata modul dan latihan, bukan buku, panduan guru resmi atau silabus baru.',
  'Hak per komponen dan 678 status koreksi dipertahankan; validasi identitas tidak menyatakan semua isu hak atau terminologi telah selesai.',
  'Antarmuka tersedia dalam Bahasa Indonesia dan Inggris. Buku Inggris adalah cermin sumber asli; tautan modul PDF tetap berbahasa Indonesia.',
];
const evidence=[];
for(const [kind,path] of [['a10_learning_capability_manifest',base+'/manifest.json'],['a10_independent_capability_validation',base+'/validation.json'],['a10_native_record_ledger',base+'/data/native-record-ledger.json'],['a10_terminology_history',base+'/data/terminology-history-index.jsonl']]) {
  const {bytes,sha256}=await identity(path);evidence.push({kind,locator:path,bytes,sha256,verified_date:'2026-09-08'});
}
const target='backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overrides=await load(target);
assert.equal(overrides.semantic_adapters.A10.contract_version,'2.3.1','Preserve the existing common adapter.');
const preservedEvidence=(overrides.semantic_adapters.A10.evidence??[]).filter(row=>!evidence.some(item=>item.kind===row.kind));
overrides.semantic_adapters.A10={...overrides.semantic_adapters.A10,
  mapping_scope:'existing_v231_capsule_plus_native_module_exercise_terminology_correction_rights_and_translation_metadata_consumer',
  evidence:[...preservedEvidence,...evidence]};
overrides.native_capabilities.A10??={};
// These receipts establish identity and consumer alignment. They do not prove
// whole-book build replay, universal lexical correctness or rights clearance.
for(const name of ['unit_identity','translation_ledger','educator_unit_alignment'])
  overrides.native_capabilities.A10[name]={status:'verified',evidence};
for(const name of ['terminology','corrections']) {
  const prior=overrides.native_capabilities.A10[name]??{status:'in_progress',evidence:[]};
  overrides.native_capabilities.A10[name]={...prior,evidence:[...(prior.evidence??[]).filter(row=>!evidence.some(item=>item.kind===row.kind)),...evidence]};
}
const tool={tool_id:'a10.open_learner_hub',label:'A10 · Modul, latihan dan cakupan solusi',
  href:'backend/a10/A10.html',action_kind:'course_reader',scope:'82 modul, 9.406 latihan dan cakupan 6.106 solusi sumber; pemilih modul dapat dipakai kembali.',
  state:'verified',primary:false,machine_data_is_learner_destination:false,
  page:await identity(publicBase+'/A10.html'),resource:await identity(publicBase+'/learning-map.json'),
  evidence:await identity(publicBase+'/validation.json'),limitations:limits};
overrides.learner_tools.A10=[...(overrides.learner_tools.A10??[]).filter(row=>row.tool_id!==tool.tool_id),tool];
const teacher=await identity(publicBase+'/A10-pengajar.html');
const educator=overrides.educator_evidence.A10??{};
const resources=(educator.resources??[]).filter(row=>!row.id.startsWith('A10:capability-'));
for(const [id,title,path,type] of [
  ['educator','Pemilih modul dan latihan A10 untuk pengajar','A10-pengajar.html','educator-data'],
  ['educator-en','A10 module and exercise selection for educators','A10-pengajar-en.html','educator-data'],
  ['exercises','Identitas 9.406 latihan, soal dan cakupan solusi','data/exercise-index.jsonl','exercise-bank'],
  ['terms','Istilah sumber, keputusan dan riwayat penggantian','data/terms-index.jsonl','terminology-register'],
  ['corrections','678 catatan koreksi dengan sasaran native','data/corrections-index.jsonl','correction-ledger'],
  ['rights','4.025 rekaman hak per komponen','data/rights-index.jsonl','rights-ledger'],
]) {
  const fact=await identity(publicBase+'/'+path);
  resources.push({id:'A10:capability-'+id,title,resource_type:type,status:'verified',
    url:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/a10/'+path,
    scope:limits.join(' '),bytes:fact.bytes,sha256:fact.sha256});
}
overrides.educator_evidence.A10={...educator,status:'verified',verified_date:'2026-09-08',
  locator:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/a10/A10-pengajar.html',
  bytes:teacher.bytes,sha256:teacher.sha256,features:['exercise_bank','solution_provenance','remix_selectors'],resources};
await writeFile(resolve(root,target),JSON.stringify(overrides,null,2)+'\n');
console.log(JSON.stringify({state:'pass',course_id:'A10',existing_contract_preserved:'2.3.1',public_files_staged:mapped.length,
  native_text_rewritten:false,public_access_changed:false,native_terminology_completion_promoted:false}));
