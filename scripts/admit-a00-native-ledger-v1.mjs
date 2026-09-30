// Central-only admission: native records remain immutable, semantic review stays open.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/a00-native-ledger-v1';
const publicBase='docs/backend/a00';
const load=async p=>JSON.parse(await readFile(resolve(root,p),'utf8'));
const save=async(p,value)=>{await mkdir(dirname(resolve(root,p)),{recursive:true});await writeFile(resolve(root,p),JSON.stringify(value,null,2)+'\n');};
const fact=async p=>{const b=await readFile(resolve(root,p));return {bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')};};
const tests=spawnSync('python',['-B',resolve(root,'scripts/test-a00-native-ledger-v1.py')],{cwd:root,encoding:'utf8',timeout:30000,maxBuffer:1024*1024});
assert.equal(tests.status,0,tests.stderr);
const manifest=await load(base+'/manifest.json');
assert.deepEqual(manifest.generator,await fact('scripts/a00-native-ledger-v1.py'));
assert.deepEqual(manifest.source_lock,await fact(base+'/input/source-lock.json'));
assert.equal(manifest.scope.semantic_canon_review,false);
for(const item of manifest.outputs)assert.deepEqual({bytes:item.bytes,sha256:item.sha256},await fact(base+'/'+item.path));
const copies=[['views/ledger.html','ledger.html'],['views/ledger-en.html','ledger-en.html'],
  ['data/source.zip','native-ledger/source.zip'],
  ['data/ledger.json','native-ledger/ledger.json'],['input/source-lock.json','native-ledger/source-lock.json'],
  ['input/term-locations.json','native-ledger/term-locations.json'],
  ['manifest.json','native-ledger/manifest.json']];
const lock=await load(base+'/input/source-lock.json');
for(const row of lock.snapshots)copies.push(['input/'+row.path,'native-ledger/'+row.path]);
for(const [source,target] of copies){
  await mkdir(dirname(resolve(root,publicBase,target)),{recursive:true});
  await writeFile(resolve(root,publicBase,target),await readFile(resolve(root,base,source)));
}
const navigationPath='backend/authority/central-reader-navigation-v1.json',nav=await load(navigationPath);
const surface=nav.course_surfaces.find(row=>row.root===publicBase);
assert.ok(surface);
const before=surface.documents.length;
for(const [name,locale,contents] of [['ledger.html','id',['A00.html','A00-pengajar.html','ledger-en.html']],
  ['ledger-en.html','en',['A00-en.html','A00-pengajar-en.html','ledger.html']]]){
  if(!surface.documents.some(row=>row.path===name))surface.documents.push({path:name,locale,course_ids:['A00'],contents_paths:contents});
}
for(const row of surface.documents.filter(row=>row.path.startsWith('A00'))){
  const link=row.locale==='en'?'ledger-en.html':'ledger.html';
  row.contents_paths??=[];if(!row.contents_paths.includes(link))row.contents_paths.push(link);
}
const added=surface.documents.length-before;
nav.summary.course_surface_html_documents=nav.course_surfaces.reduce((n,row)=>n+row.documents.length,0);
nav.summary.navigation_overlay_documents+=added;
nav.summary.classified_html_documents+=added;
await save(navigationPath,nav);
const overridePath='backend/course-capsule-v1/authority/integration-overrides-v1.json',over=await load(overridePath);
const evidence=[];
for(const [name,kind] of [['manifest.json','a00_native_ledger_manifest'],['input/source-lock.json','a00_native_ledger_source_lock']])
  evidence.push({kind,locator:base+'/'+name,...await fact(base+'/'+name),verified_date:'2026-09-30'});
evidence.push({kind:'a00_lexical_target_locations',locator:base+'/input/term-locations.json',...await fact(base+'/input/term-locations.json'),verified_date:'2026-09-30'});
const adapter=over.semantic_adapters.A00;
adapter.evidence=[...adapter.evidence.filter(row=>!evidence.some(e=>e.kind===row.kind)),...evidence];
// Presence and byte identity do not prove every native substantive choice.
for(const capability of ['translation_ledger','terminology','corrections'])
  over.native_capabilities.A00[capability]={status:'available_unverified',evidence};
const educator=over.educator_evidence.A00;
educator.resources=educator.resources.filter(row=>!row.id.startsWith('A00:native-ledger'));
for(const [suffix,title] of [['','Peta sumber dan istilah asli A00'],['-en','A00 native source map and terminology']]){
  const page='ledger'+suffix+'.html';
  educator.resources.push({id:'A00:native-ledger'+suffix,title,resource_type:'educator-data',status:'verified',
    url:'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/a00/'+page,
    scope:suffix ? '75 module identities, 20 native lexical choices with byte-bound target-text locations, 36 metadata labels and 75 correction/issue records. Literal matches do not establish semantic/canon review or native scope applicability.' : '75 identitas modul, 20 pilihan istilah asli dengan lokasi teks target terikat byte, 36 label metadata dan 75 catatan koreksi/masalah. Kecocokan harfiah tidak membuktikan peninjauan makna/kanon atau penerapan cakupan asli.',
    ...await fact(publicBase+'/'+page)});
}
await save(overridePath,over);
console.log(JSON.stringify({status:'pass',course:'A00',hosted_files:copies.length,added_navigation_documents:added,
  semantic_translation_review_claimed:false,native_files_modified:false}));
