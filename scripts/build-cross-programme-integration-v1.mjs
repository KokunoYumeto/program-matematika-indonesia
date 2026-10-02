import assert from 'node:assert/strict';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve, dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {validateD80PrerequisiteRoute,renderD80PrerequisiteRoute} from './d80-prerequisite-route-v1.mjs';
import {validateB40PrerequisiteRoute,renderB40PrerequisiteRoute} from './b40-prerequisite-route-v1.mjs';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const out=resolve(root,'backend/cross-programme-v1');
const freezeName='inputs/20261002-801f1868';
const freeze=resolve(out,freezeName);
const hash=b=>createHash('sha256').update(b).digest('hex');
const json=b=>JSON.parse(b.toString('utf8'));
const fact=(path,b)=>({path,bytes:b.length,sha256:hash(b)});
const serialize=j=>Buffer.from(JSON.stringify(j,null,2)+'\n');
const origin='https://kokunoyumeto.github.io/program-matematika-indonesia/';
const advancedOrigin='https://kokunoyumeto.github.io/open-mathematics-courses/';
const phoneRoot=resolve(root,'../../../kerodon_to_stacks_extension_20260906/reader');
const phoneInputs={catalog:'course_inputs/R36_DG_CHAR_FOUNDATIONS_CATALOG_20261002.json',recipe:'course_inputs/R36_DG_CHAR_FOUNDATIONS_PACKAGE_INPUTS_20261002.json'};
const args=new Set(process.argv.slice(2));
const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
async function exactWrite(path,bytes){
  await mkdir(dirname(path),{recursive:true});
  try{const old=await readFile(path);assert.equal(hash(old),hash(bytes),'Frozen input already exists with different bytes: '+path);return;}
  catch(e){if(e.code!=='ENOENT')throw e;}
  await writeFile(path,bytes,{flag:'wx'});
}
async function download(url){
  const response=await fetch(url,{headers:{'User-Agent':'Open-Courses-bounded-integration'},signal:AbortSignal.timeout(30000)});
  assert.equal(response.status,200,'Required input HTTP '+response.status+': '+url);
  const b=Buffer.from(await response.arrayBuffer());
  return {bytes:b,http:{url,status:response.status,bytes:b.length,sha256:hash(b),etag:response.headers.get('etag')}};
}
if(args.has('--capture')){
  const rows=[];const commits={};
  for(const [key,repo] of [['core','program-matematika-indonesia'],['advanced','open-mathematics-courses']]){
    const r=await download('https://api.github.com/repos/KokunoYumeto/'+repo+'/commits/main');
    const c=json(r.bytes);commits[key]={repository:'https://github.com/KokunoYumeto/'+repo,commit:c.sha,tree:c.commit.tree.sha,commit_date:c.commit.committer.date};
    assert.match(c.sha,/^[0-9a-f]{40}$/);
  }
  const requests=[
    ['advanced-courses.json','open-mathematics-courses',commits.advanced.commit,'docs/courses.json'],
    ['core-courses.js','program-matematika-indonesia',commits.core.commit,'docs/courses.js'],
    ['core-learner-access.json','program-matematika-indonesia',commits.core.commit,'docs/interface/learner-access-manifest.json'],
    ['core-capsules.jsonl','program-matematika-indonesia',commits.core.commit,'docs/data/course-capsule-v1/course-capsules.jsonl'],
  ];
  for(const [name,repo,commit,path] of requests){const r=await download('https://raw.githubusercontent.com/KokunoYumeto/'+repo+'/'+commit+'/'+path);await exactWrite(resolve(freeze,name),r.bytes);rows.push({...fact(freezeName+'/'+name,r.bytes),origin:r.http});}
  for(const [name,path] of Object.entries(phoneInputs)){const b=await readFile(resolve(phoneRoot,path));await exactWrite(resolve(freeze,'phone-'+name+'.json'),b);rows.push({...fact(freezeName+'/phone-'+name+'.json',b),origin:{kind:'local_frozen_phone_component',logical_path:path,published:false}});}
  const metadata={schema:'cross-programme-input-freeze/1',captured_utc:new Date().toISOString(),commits,inputs:rows,no_global_scan:true,no_owner_mutation:true};
  await exactWrite(resolve(freeze,'MANIFEST.json'),serialize(metadata));
  console.log(JSON.stringify({state:'frozen',commits,inputs:rows.map(r=>({path:r.path,bytes:r.bytes,sha256:r.sha256}))}));
  process.exit(0);
}

const manifestBytes=await readFile(resolve(freeze,'MANIFEST.json'));const manifest=json(manifestBytes);
const inputs={};for(const row of manifest.inputs){const b=await readFile(resolve(out,row.path));assert.equal(b.length,row.bytes);assert.equal(hash(b),row.sha256);inputs[row.path.split('/').at(-1)]=b;}
const advanced=json(inputs['advanced-courses.json']);
const coreText=inputs['core-courses.js'].toString('utf8');
const coreMatch=coreText.match(/export const courses = Object\.freeze\((\[.*?\])\);/s);assert.ok(coreMatch,'Core native course projection must remain JSON without executing downloaded code');
const core=JSON.parse(coreMatch[1]);const access=json(inputs['core-learner-access.json']);
const capsules=inputs['core-capsules.jsonl'].toString('utf8').trim().split(/\r?\n/).map(s=>JSON.parse(s));
const phone=json(inputs['phone-catalog.json']);const recipe=json(inputs['phone-recipe.json']);
assert.equal(hash(inputs['phone-catalog.json']).toUpperCase(),recipe.catalog_sha256.toUpperCase());
assert.equal(core.length,40);assert.equal(new Set(core.map(c=>c.id)).size,40);assert.equal(capsules.length,40);
// Labels and route semantics come from the pinned public baseline, not this
// older local interface checkout. The baseline imports were hash-verified by
// stage-cross-programme-public-baseline-v1.mjs before this bounded import.
const baselineManifest=json(await readFile(resolve(out,'current-public-baseline/MANIFEST.json')));
assert.equal(baselineManifest.source_commit,manifest.commits.core.commit);
for(const row of baselineManifest.files.filter(r=>r.path.endsWith('.js'))){const b=await readFile(resolve(out,'current-public-baseline',row.path));assert.equal(b.length,row.bytes);assert.equal(hash(b),row.sha256);}
const {coursePresentation}=await import(pathToFileURL(resolve(out,'current-public-baseline/docs/interface/view.js')));
const provenanceBytes=await readFile(resolve(out,'PRODUCTION_PROVENANCE.json'));const provenance=json(provenanceBytes);
assert.equal(provenance.model,'gpt-6.1-sol');assert.equal(provenance.effort,'ultra');
const scopeFindingBytes=await readFile(resolve(out,'PROOF_SCOPE_FINDINGS.json'));const scopeFindings=json(scopeFindingBytes);
assert.equal(scopeFindings.schema,'cross-programme-proof-scope-findings/1');
const coreById=new Map(core.map(c=>[c.id,c]));const advById=new Map(advanced.courses.map(c=>[c.id,c]));
assert.equal(advById.size,advanced.courses.length);const capsById=new Map(capsules.map(c=>[c.course_id,c]));
const coreCourses=core.map(c=>{
  assert.ok(capsById.has(c.id));assert.ok(access.courses[c.id]);
  return {id:c.id,kind:'core',level:c.level,title:{id:c.title,en:coursePresentation(c,'en').title},prerequisites:c.prerequisites,
    routes:{en:access.courses[c.id].en.locale_route,id:access.courses[c.id].id.locale_route},
    language_access:{en:access.courses[c.id].en,id:access.courses[c.id].id},
    capsule:{id:capsById.get(c.id).course_id,contract:capsById.get(c.id).schema_id,mapping_scope:capsById.get(c.id).layers.interoperability.mapping_scope},
    native_unit_proof_mapping:'not_inferred_from_course_capsule',native_source:c.repository??null};
});
const edges=[];const unresolved=[];const inconsistencies=[];
function edge(from,to,kind,evidence){const row={id:kind+':'+from+'->'+to,from,to,relation:kind,evidence,mathematical_correspondence:'not_checked',proof_closed:false};if(!edges.some(x=>x.id===row.id))edges.push(row);}
for(const c of core)for(const p of c.prerequisites){assert.ok(coreById.has(p));edge('core:'+c.id,'core:'+p,'preparation_course',{input:'core-courses.js',field:'prerequisites',declared_by:'core_programme'});}
const advancedCourses=advanced.courses.map(c=>{
  assert.ok(c.href);const here=c.take_first?.here??[];const secondary=c.courses_here_to_take_first??[];
  if(JSON.stringify([...here].sort())!==JSON.stringify([...secondary].sort()))inconsistencies.push({course:c.id,take_first_here:here,courses_here_to_take_first:secondary,disposition:'union_for_reading_routes_only; no proof-certification'});
  for(const p of c.take_first?.core??[]){if(coreById.has(p))edge('advanced:'+c.id,'core:'+p,'preparation_course',{input:'advanced-courses.json',field:'take_first.core',declared_by:'advanced_course'});else unresolved.push({from:c.id,declared_id:p,kind:'core_course',reason:'native_core_id_not_present'});}
  for(const p of new Set([...here,...secondary])){if(advById.has(p))edge('advanced:'+c.id,'advanced:'+p,'preparation_course',{input:'advanced-courses.json',field:here.includes(p)?'take_first.here':'courses_here_to_take_first',declared_by:'advanced_course'});else unresolved.push({from:c.id,declared_id:p,kind:'advanced_course',reason:'native_advanced_id_not_present'});}
  return {id:c.id,kind:'advanced',title:{en:c.title},summary:c.summary,subject:c.subject,content_language:c.content_language??'en',translations:c.translations??[],route:new URL(c.href,advancedOrigin).href,
    status:c.status,status_note:c.status_note,authorship:c.written_by,licence:c.licence,lessons:c.lessons.map(l=>({id:l.id,title:l.title,route:new URL(l.href,advancedOrigin).href,editable_source:l.markdown?new URL(l.markdown,advancedOrigin).href:null})),
    source_snapshot:manifest.commits.advanced.commit};
});
// Separate complete native lesson locators and reported proof records from broad
// reading routes. Imported evidence never silently becomes an independently
// checked statement/proof correspondence, and local drafts get no public URL.
const nativeUnits=new Map(phone.courses.flatMap(c=>c.units.map(u=>[c.id+'/'+u.id,{course:c,unit:u}])));
const nativeReadingEdges=phone.dependency_locators.map(r=>{
  const a=nativeUnits.get(r.from),b=nativeUnits.get(r.target);assert.ok(a&&b,'Missing exact native reading endpoint');
  assert.equal(a.unit.source_sha256,r.from_source_sha256);assert.equal(b.unit.source_sha256,r.target_source_sha256);
  return {...r,relation:'lesson_reading',mathematical_correspondence:'not_checked',proof_closed:false,source_catalog_sha256:hash(inputs['phone-catalog.json'])};
});
const providerRecords=phone.foundation_proof_records.map(r=>{
  const p=nativeUnits.get(r.proof.unit);assert.ok(p);assert.equal(p.unit.source_sha256,r.proof.source_sha256);
  const anchorDeclared=Array.isArray(p.unit.heading_anchors);
  if(anchorDeclared)assert.ok(p.unit.heading_anchors.some(h=>h.ids.includes(r.proof.anchor)),'Proof anchor not in native lesson');
  return {...r,record_kind:'reported_provider',anchor_state:anchorDeclared?'native_catalog_anchor_declared':'requires_full_source_anchor_readback',independent_proof_check:false,whole_prerequisite_closure:false,source_catalog_sha256:hash(inputs['phone-catalog.json']),public_route:null};
});
const reverse=Object.fromEntries([...core.map(c=>'core:'+c.id),...advancedCourses.map(c=>'advanced:'+c.id)].map(id=>[id,edges.filter(e=>e.to===id).map(e=>e.from).sort()]));
const bridge={schema:'open-courses-cross-programme/1',interface_languages:['en','id'],
  programme_identity:'Open Courses',production_provenance:provenance,policy:{native_ids_preserved:true,zero_copy_content:true,core_and_advanced_one_programme:true,course_route_is_not_proof_provider:true,english_interface_does_not_imply_indonesian_advanced_translation:true,external_citation_does_not_close_internal_proof_dependency:true,stacks_baseline:'KokunoYumeto/unofficial-stacks-project-ai-drafts',no_source_or_proof_rewrites:true},
  input_freeze:fact(freezeName+'/MANIFEST.json',manifestBytes),source_snapshots:manifest.commits,advanced_snapshot_intake:manifest.intake,
  counts:{core_courses:core.length,published_advanced_courses:advancedCourses.length,published_advanced_lessons:advancedCourses.reduce((n,c)=>n+c.lessons.length,0),phone_frozen_courses:phone.courses.length,phone_frozen_lessons:phone.courses.reduce((n,c)=>n+c.units.length,0),preparation_edges:edges.length,cross_programme_course_edges:edges.filter(e=>e.from.startsWith('advanced:')&&e.to.startsWith('core:')).length,native_lesson_reading_edges:nativeReadingEdges.length,reported_proof_providers:providerRecords.length,independently_verified_cross_programme_proof_matches:0,unresolved_routes:unresolved.length},
  courses:{core:coreCourses,advanced:advancedCourses},edges,reverse_dependencies:reverse,
  native_phone_exchange:{schema:'stacks-foundation-proof-exchange/v1',course_snapshot:phone.snapshot,reading_edges:nativeReadingEdges,reported_providers:providerRecords},result_requirement_findings:scopeFindings,unresolved_routes:unresolved,source_field_disagreements:inconsistencies,
  unfinished:['Read exact required downstream statements and full matching core proofs; bind native unit/result/anchor and conditions for every actual mathematical dependency.','Reconcile local phone projection with the separately pinned public advanced edition; counts are distinct snapshots, not additive.','Add proof-provider routes only after actual public source/anchor readback; never manufacture a route for a local draft.']};
const routeRows=Object.fromEntries(coreCourses.map(c=>[c.id,{
  en:origin+'en/programme/#core-'+c.id,
  id:origin+'id/programme/#core-'+c.id,
  advancedCount:reverse['core:'+c.id].filter(x=>x.startsWith('advanced:')).length,
}]));
const moduleText='// Generated additive reading-route crosswalk; this is not proof certification.\nexport const crossProgrammeRoutes = Object.freeze('+JSON.stringify(routeRows)+');\n';
const copy={en:{title:'Open Courses — foundations and further study',notice:'These are source-declared reading routes, not a certificate that every prerequisite proof has been checked. Advanced lessons are currently in English. The foundation interface offers English and Bahasa Indonesia with actual material languages marked.',home:'Programme home',before:'Learn first',after:'What this prepares you for',core:'Foundation courses',advanced:'Further courses',none:'No further course is declared in this snapshot.',lang:'Available reading materials and their languages',data:'Dependency data',limits:'Proof-level integration still being completed',toggle:'Bahasa Indonesia',no:'No course preparation is declared in this snapshot; that does not mean no prerequisites.',lesson:'Lessons',unresolved:'Unresolved source-declared routes'},id:{title:'Open Courses — fondasi dan studi lanjutan',notice:'Jalur belajar ini dinyatakan oleh sumber. Jalur tersebut bukan bukti bahwa semua pembuktian prasyarat telah diperiksa. Pelajaran lanjutan saat ini berbahasa Inggris. Antarmuka fondasi menyediakan English dan Bahasa Indonesia; bahasa bahan ditandai sesuai isinya.',home:'Beranda program',before:'Pelajari terlebih dahulu',after:'Persiapan untuk mempelajari',core:'Mata kuliah fondasi',advanced:'Mata kuliah lanjutan',none:'Belum ada mata kuliah lanjutan yang dinyatakan dalam snapshot ini.',lang:'Bahan bacaan yang tersedia dan bahasanya',data:'Data dependensi',limits:'Integrasi pada tingkat pembuktian masih dikerjakan',toggle:'English',no:'Belum ada jalur prasyarat yang dinyatakan dalam snapshot ini; ini tidak berarti tanpa prasyarat.',lesson:'Pelajaran',unresolved:'Jalur yang dinyatakan sumber tetapi belum ditemukan'}};
function html(locale){const t=copy[locale];const other=locale==='en'?'id':'en';const title=id=>{const [kind,key]=id.split(':');const c=(kind==='core'?coreCourses:advancedCourses).find(c=>c.id===key);return c?.title[locale]??c?.title.en??key;};const href=id=>'#'+id.replace(':','-');const list=ids=>'<ul>'+ids.map(id=>'<li><a href="'+href(id)+'">'+esc(title(id))+'</a></li>').join('')+'</ul>';
  const body=coreCourses.map(c=>{const req=edges.filter(e=>e.from==='core:'+c.id).map(e=>e.to);const next=reverse['core:'+c.id].filter(x=>x.startsWith('advanced:'));const a=c.language_access[locale];const resources=[...a.program_hosted_reader.resources,...a.authoritative_original.resources].filter((r,i,all)=>all.findIndex(x=>x.url===r.url)===i);
    return '<section id="core-'+c.id+'"><h3>'+esc(c.title[locale])+'</h3><p><a href="'+esc(c.routes[locale])+'">'+esc(t.home)+' — '+esc(c.title[locale])+'</a></p><h4>'+esc(t.before)+'</h4>'+list(req)+'<h4>'+esc(t.lang)+'</h4><ul>'+resources.map(r=>'<li><a href="'+esc(r.url)+'">'+(locale==='id'?esc(a.program_hosted_reader.resources.some(x=>x.url===r.url)?'Baca bahan program — ':'Sumber asli — '):'')+'<span lang="'+esc(r.content_language)+'">'+esc(r.label)+'</span></a> <span>'+esc(r.content_language)+'</span></li>').join('')+'</ul><h4>'+esc(t.after)+'</h4>'+(next.length?list(next):'<p>'+esc(t.none)+'</p>')+'</section>';}).join('');
  const adv=advancedCourses.map(c=>{const req=edges.filter(e=>e.from==='advanced:'+c.id).map(e=>e.to);return '<section id="advanced-'+esc(c.id)+'"><h3><a href="'+esc(c.route)+'" lang="en">'+esc(c.title.en)+'</a></h3><p>English · '+esc(c.status)+' · '+esc(c.lessons.length)+' '+esc(t.lesson)+'</p><h4>'+esc(t.before)+'</h4>'+(req.length?list(req):'<p>'+esc(t.no)+'</p>')+'<details><summary>'+esc(t.lesson)+'</summary><ol>'+c.lessons.map(l=>'<li><a href="'+esc(l.route)+'" lang="en">'+esc(l.title)+'</a></li>').join('')+'</ol></details><details><summary>'+(locale==='en'?'Sources and rights':'Sumber dan hak penggunaan')+'</summary><p>'+esc(c.authorship)+'; '+esc(c.licence?.spdx??'source licence applies')+'</p></details><h4>'+esc(t.after)+'</h4>'+list(reverse['advanced:'+c.id])+'</section>';}).join('');
  return '<!doctype html><html lang="'+locale+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(t.title)+'</title><style>body{font:17px/1.65 system-ui,sans-serif;margin:auto;max-width:72rem;padding:1rem;color:#172338;background:#fbfcfe}a{color:#075aaa}nav{display:flex;gap:1rem;flex-wrap:wrap}section{border:1px solid #cbd8e5;border-radius:.7rem;margin:1rem 0;padding:1rem;scroll-margin-top:1rem}h2{margin-top:2rem}.notice{background:#eaf2fa;padding:1rem;border-left:.3rem solid #2466a1}p,li,a{overflow-wrap:anywhere}details{margin:.7rem 0}summary{cursor:pointer}</style></head><body><header><nav><a href="'+origin+locale+'/">'+esc(t.home)+'</a><a href="'+origin+other+'/programme/" hreflang="'+other+'">'+esc(t.toggle)+'</a><a href="../../data/cross-programme-v1/bridge.json">'+esc(t.data)+'</a></nav><h1>'+esc(t.title)+'</h1><p class="notice">'+esc(t.notice)+'</p><p>'+coreCourses.length+' '+esc(t.core)+' · '+advancedCourses.length+' '+esc(t.advanced)+'</p></header><main><h2>'+esc(t.core)+'</h2>'+body+'<h2>'+esc(t.advanced)+'</h2>'+adv+'<section><h2>'+esc(t.limits)+'</h2><p>'+(locale==='en'?'Full statement/proof/generality comparisons are recorded separately. None is certified by this course-level crosswalk. The 58-course local phone projection and the public advanced edition are different evidence snapshots.':'Perbandingan lengkap pernyataan, pembuktian, dan keumuman dicatat terpisah. Peta tingkat mata kuliah ini tidak menyatakan perbandingan tersebut selesai. Proyeksi lokal phone sebanyak 58 mata kuliah dan edisi lanjutan publik merupakan snapshot bukti yang berbeda.')+'</p><p>'+(locale==='en'?'Navigation and dependency integration produced by OpenAI Codex — GPT-6.1 Sol, Ultra effort. Source author credits are preserved. No human proof review is claimed.':'Integrasi navigasi dan dependensi dikerjakan oleh OpenAI Codex — GPT-6.1 Sol, tingkat upaya Ultra. Kredit penulis sumber dipertahankan. Tidak ada klaim peninjauan pembuktian oleh manusia.')+'</p></section></main></body></html>\n';
}
// Reproduce additive, already published reader links without changing the
// frozen course/proof snapshot or copying producer book bodies into it.
const additionsPath='backend/cross-programme-v1/current-navigation-additions.json';
const additionsBytes=await readFile(resolve(root,additionsPath));const additions=json(additionsBytes);
const lessonRoutePath='backend/cross-programme-v1/d80-prerequisite-route-v1.json';
const lessonRouteBytes=await readFile(resolve(root,lessonRoutePath));
const lessonRoute=validateD80PrerequisiteRoute(json(lessonRouteBytes));
assert.ok(coreById.has(lessonRoute.provider_course));
assert.ok(advById.get(lessonRoute.consumer_course)?.lessons.some(l=>l.id===lessonRoute.consumer_lesson));
bridge.source_bound_lesson_routes=[lessonRoute];
const b40RoutePath='backend/cross-programme-v1/b40-prerequisite-route-v1.json';
const b40RouteBytes=await readFile(resolve(root,b40RoutePath));
const b40Route=validateB40PrerequisiteRoute(json(b40RouteBytes));
const b40ManifestBytes=await readFile(resolve(root,b40Route.reader_manifest));
const b40Manifest=json(b40ManifestBytes);validateB40PrerequisiteRoute(b40Route,b40Manifest);
for(const row of b40Manifest.files){
  assert.match(row.path,/^[A-Za-z0-9_.-]+$/);
  const bytes=await readFile(resolve(root,dirname(b40Route.reader_manifest),row.path));
  assert.equal(bytes.length,row.bytes);assert.equal(hash(bytes),row.sha256);
}
assert.ok(coreById.has(b40Route.provider_course));
assert.ok(advById.get(b40Route.consumer_course)?.lessons.some(l=>l.id===b40Route.consumer_lesson));
bridge.source_bound_lesson_routes.push(b40Route);
bridge.b40_prerequisite_reader= fact(b40Route.reader_manifest,b40ManifestBytes);
assert.equal(additions.schema,'cross-programme-current-navigation-additions/1');
const additionKeys=new Set();
// Current resources are additive evidence. Never rewrite the pinned historical
// language_access snapshot or infer a complete book from a partial reader.
for(const course of coreCourses)course.current_reading_resources=[];
bridge.policy.current_reading_resources_are_additive_to_frozen_language_access=true;
for(const resource of additions.resources){
  assert.ok(coreById.has(resource.course_id));
  assert.match(resource.marker,/^data-[a-z0-9-]+="[a-z0-9-]+"$/);
  assert.ok(!additionKeys.has(resource.course_id+' '+resource.marker));additionKeys.add(resource.course_id+' '+resource.marker);
  const target=new URL(resource.href);assert.equal(target.origin,new URL(origin).origin);
  assert.equal(resource.content_language,'en');assert.ok(resource.labels.id&&resource.labels.en);
  const source=resource.source_manifest;assert.match(source.path,/^docs\/en\/readers\/[a-z0-9-]+\/(?:FOUNDATIONS|READER)_MANIFEST\.json$/);
  const bytes=await readFile(resolve(root,source.path));assert.deepEqual(fact(source.path,bytes),source);
  const native=json(bytes);
  if(source.path.endsWith('/READER_MANIFEST.json')){
    assert.equal(native.schema,'b40-expanded-reading-edition/1');
    assert.equal(native.sections.length,32);assert.equal(native.language,'en');
    assert.equal(native.sections.at(-1).section,'projplane');
    assert.equal(resource.course_id,'B40');
  }
  assert.equal(resource.href,origin+source.path.slice(5).replace(/(?:FOUNDATIONS|READER)_MANIFEST\.json$/,''));
  assert.equal(native.language,resource.content_language);
  const sourceCommit=resource.source_commit??additions.source_commit;
  assert.match(sourceCommit,/^[0-9a-f]{40}$/);
  const nativeSections=[];
  for(const section of native.sections){
    const bound={section:section.section,title:section.title,native_units:section.units};
    for(const [key,name] of [['reader','reader'],['public_index','native_unit_index']]){
      const row=section[key];assert.ok(row&&row.path);
      assert.match(row.path,/^[A-Za-z0-9_./-]+$/);assert.ok(!row.path.split('/').includes('..'));
      const path=dirname(source.path)+'/'+row.path;
      const content=await readFile(resolve(root,path));
      assert.deepEqual(fact(row.path,content),row,'Changed current reading resource: '+path);
      bound[name]={...fact(path,content),url:origin+path.slice(5)};
    }
    nativeSections.push(bound);
  }
  assert.equal(nativeSections.length,native.counts.readers);
  assert.equal(nativeSections.reduce((n,s)=>n+s.native_units,0),native.counts.native_units);
  coreCourses.find(c=>c.id===resource.course_id).current_reading_resources.push({
    ...resource,source_commit:sourceCommit,native_source_revision:native.source_revision,
    availability:'program_hosted_partial_reader',
    coverage:{sections:native.counts.readers,native_units:native.counts.native_units,
      full_book:false,proof_dependency_closure:false},native_sections:nativeSections,
  });
}
function currentHtml(locale){
  let body=html(locale);
  const update=locale==='en'
    ?'Advanced catalogue update: OpenAI Codex — GPT-6 Astra, Ultra effort. This snapshot includes 72 public courses and 1,061 lessons; course routes are not proof certification. Local foundation drafts remain separate.'
    :'Pembaruan katalog lanjutan: OpenAI Codex — GPT-6 Astra, tingkat upaya Ultra. Snapshot ini mencakup 72 mata kuliah publik dan 1.061 pelajaran; jalur mata kuliah bukan pengesahan pembuktian. Draf fondasi lokal tetap dicatat terpisah.';
  body=body.replace('</header>','<p data-advanced-snapshot="801f1868">'+esc(update)+'</p></header>');
  const providerAnchor='<section id="core-D80"><h3>'+esc(coreCourses.find(c=>c.id==='D80').title[locale])+'</h3>';
  assert.equal(body.split(providerAnchor).length,2);
  body=body.replace(providerAnchor,providerAnchor+renderD80PrerequisiteRoute(lessonRoute,locale,'provider'));
  const advanced=advancedCourses.find(c=>c.id===lessonRoute.consumer_course);
  const consumerAnchor='<section id="advanced-'+esc(advanced.id)+'"><h3><a href="'+esc(advanced.route)+'" lang="en">'+esc(advanced.title.en)+'</a></h3>';
  assert.equal(body.split(consumerAnchor).length,2);
  body=body.replace(consumerAnchor,consumerAnchor+renderD80PrerequisiteRoute(lessonRoute,locale,'consumer'));
  for(const [kind,courseId,side] of [['core',b40Route.provider_course,'provider'],['advanced',b40Route.consumer_course,'consumer']]){
    const course=(kind==='core'?coreCourses:advancedCourses).find(c=>c.id===courseId);
    const anchor='<section id="'+kind+'-'+courseId+'"><h3>'+(kind==='core'?esc(course.title[locale]):'<a href="'+esc(course.route)+'" lang="en">'+esc(course.title.en)+'</a>')+'</h3>';
    assert.equal(body.split(anchor).length,2);
    body=body.replace(anchor,anchor+renderB40PrerequisiteRoute(b40Route,locale,side));
  }
  for(const resource of coreCourses.flatMap(course=>course.current_reading_resources)){
    const course=coreCourses.find(c=>c.id===resource.course_id);
    const anchor='<section id="core-'+resource.course_id+'"><h3>'+esc(course.title[locale])+'</h3>';
    assert.equal(body.split(anchor).length,2);assert.ok(!body.includes(resource.marker));
    const link='<p><a '+resource.marker+' href="'+esc(resource.href)+'" hreflang="'+esc(resource.content_language)+'">'+esc(resource.labels[locale])+'</a></p>';
    body=body.replace(anchor,anchor+link);
  }
  return body;
}
const outputs=[['backend/cross-programme-v1/bridge.json',serialize(bridge)],['docs/data/cross-programme-v1/bridge.json',serialize(bridge)],['docs/interface/cross-programme-routes.js',Buffer.from(moduleText)],...['en','id'].map(l=>['docs/'+l+'/programme/index.html',Buffer.from(currentHtml(l))])];
for(const [path,b] of outputs){
  const full=resolve(root,path);
  if(args.has('--check')){
    const hosted=await readFile(full);
    if(hosted.equals(b))continue;
    assert.ok(['docs/en/programme/index.html','docs/id/programme/index.html'].includes(path),'Non-HTML output drift: '+path);
    const overlay=json(await readFile(resolve(root,'backend/authority/central-course-surface-navigation-overlay-v1.json')));
    const record=overlay.files.find(r=>r.document===path);
    assert.ok(record && record.source_body_replay_exact);
    assert.deepEqual(record.source_body,fact(path,b));
    assert.deepEqual(record.hosted_surface,fact(path,hosted));
    let body=hosted.toString('utf8');
    assert.equal((body.match(/data-central-surface-navigation="v1"/g)||[]).length,2);
    body=body.replace(/(?:\n[ \t]*)?<nav\b(?=[^>]*data-central-surface-navigation="v1")(?=[^>]*data-placement="top")[^>]*>[\s\S]*?<\/nav>/i,'');
    body=body.replace(/<nav\b(?=[^>]*data-central-surface-navigation="v1")(?=[^>]*data-placement="bottom")[^>]*>[\s\S]*?<\/nav>(?:\n[ \t]*)?/i,'');
    assert.deepEqual(Buffer.from(body),b,'Hosted navigation must reverse to exact source: '+path);
  }else{await mkdir(dirname(full),{recursive:true});await writeFile(full,b);}
}
const receipt={schema:'cross-programme-build/1',state:'local_reading_routes_integrated_proof_correspondence_unfinished',counts:bridge.counts,inputs:manifest.inputs,current_navigation_additions:fact(additionsPath,additionsBytes),source_bound_lesson_route:fact(lessonRoutePath,lessonRouteBytes),outputs:outputs.map(([p,b])=>fact(p,b)),no_native_owner_mutation:true,no_phone_mutation:true,no_mathematical_certification:true,public_deployment:false,script:fact('scripts/build-cross-programme-integration-v1.mjs',await readFile(fileURLToPath(import.meta.url)))};
if(!args.has('--check'))await writeFile(resolve(out,'BUILD_RECEIPT.json'),serialize(receipt));
console.log(JSON.stringify({state:args.has('--check')?'byte_replay_pass':receipt.state,counts:bridge.counts,outputs:receipt.outputs}));
