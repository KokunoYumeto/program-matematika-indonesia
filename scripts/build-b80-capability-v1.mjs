import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { exportCatalog, importCatalog, json, line, sha256 } from './native-catalog-exchange-v1.mjs';

const project=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base='backend/course-capsule-v1/adapters/b80-capability-v1';
const outputOption=process.argv.find(v=>v.startsWith('--output-root='));
const outputRoot=outputOption?resolve(outputOption.slice(14)):project;
const inputBytes=await readFile(resolve(project,base,'input/catalog.json'));
const schemaBytes=await readFile(resolve(project,base,'input/catalog.schema.json'));
const intakeBytes=await readFile(resolve(project,base,'input/public-intake.json'));
const contractSchemas=await Promise.all(['native-catalog-record-v1.schema.json','course-learning-capability-v1.schema.json'].map(async name=>{
  const path='schemas/course-capsule-v1/'+name,bytes=await readFile(resolve(project,path));
  return {path,bytes:bytes.length,sha256:sha256(bytes)};
}));
const intake=JSON.parse(intakeBytes),catalog=JSON.parse(inputBytes);
assert.equal(sha256(inputBytes),intake.catalog.sha256);
assert.equal(inputBytes.length,intake.catalog.bytes);
assert.equal(sha256(schemaBytes),intake.schema_file.sha256);
assert.equal(catalog.schema_version,'o002.backend.v2');
assert.equal(catalog.course.id,'B80');assert.equal(catalog.language,'id-ID');
assert.equal(catalog.units.length,14);assert.equal(catalog.exercises.length,75);
const dataset='family-09-mathematical-computing/B80';
const exchange=exportCatalog(catalog,dataset);
const serializedRecords=exchange.records.map(line).join('\n')+'\n';
const replay=importCatalog(JSON.parse(json(exchange.shape)),serializedRecords.trimEnd().split('\n').map(text=>JSON.parse(text)),dataset);
assert.deepEqual(replay,catalog);
const pages=new Map(intake.pages.map(page=>[page.unit_id,page]));
assert.equal(pages.size,catalog.units.length);
const units=new Map(catalog.units.map(row=>[row.id,row]));
const exercises=new Map(catalog.exercises.map(row=>[row.id,row]));
const components=new Map(catalog.components.map(row=>[row.id,row]));
const artifacts=new Map(catalog.artifacts.map(row=>[row.id,row]));
const environments=new Map(catalog.environments.map(row=>[row.id,row]));
const sources=new Map(catalog.sources.map(row=>[row.id,row]));
const nativeIds=new Set(exchange.records.map(row=>row.native_id).filter(Boolean));
const sourceSections=new Set(catalog.units.flatMap(unit=>unit.sections));
const explicitExternalIds=new Set([catalog.course.prerequisite,...catalog.prerequisite_routes.map(row=>row.prerequisite),
  ...catalog.artifacts.map(row=>row.producer).filter(id=>id.startsWith('pipeline-'))]);
for(const row of catalog.relations){
  for(const id of [row.from,row.to]) assert.ok(nativeIds.has(id)||sourceSections.has(id)||explicitExternalIds.has(id),`Unbound relation ${id}`);
}
const before=catalog.relations.filter(row=>row.type==='precedes');
const visiting=new Set(),visited=new Set();
function visit(id){
  assert.ok(!visiting.has(id),'Cyclic native unit order');if(visited.has(id))return;
  visiting.add(id);for(const edge of before.filter(row=>row.from===id)){assert.ok(units.has(edge.to));visit(edge.to);}
  visiting.delete(id);visited.add(id);
}
for(const id of units.keys())visit(id);
function anchor(unitId,id){
  const page=pages.get(unitId);assert.ok(page);assert.equal(page.anchor_counts[id],1,`Unverified anchor ${unitId}/${id}`);
  return page.url+'#'+encodeURIComponent(id);
}
for(const component of components.values()) assert.ok(sources.has(component.source),'Unbound component source');
const learningUnits=catalog.units.map(unit=>{
  for(const id of unit.components)assert.ok(components.has(id));
  assert.deepEqual([...unit.exercises].sort(),catalog.exercises.filter(row=>row.unit===unit.id).map(row=>row.id).sort());
  for(const section of unit.sections)anchor(unit.id,section);
  const mappedExercises=unit.exercises.map(id=>{
    const exercise=exercises.get(id);assert.ok(exercise);assert.equal(exercise.source_path,unit.reader_path);
    const supports=Object.fromEntries(['hint','check','solution'].map(kind=>{
      const support=exercise[kind];assert.ok(['complete','executable','not_present','pending'].includes(support.status));
      const available=['complete','executable'].includes(support.status);
      return [kind,{...support,href:available?anchor(unit.id,support.source_anchor):null}];
    }));
    return {id,unit_id:unit.id,title:exercise.title,kind:exercise.kind,sequence:exercise.sequence,
      curriculum_status:exercise.curriculum_status,href:anchor(unit.id,id),...supports};
  });
  return {id:unit.id,title:unit.title,href:pages.get(unit.id).url,sections:unit.sections,
    objectives_href:unit.sections.find(id=>id.endsWith('-objectives'))?anchor(unit.id,unit.sections.find(id=>id.endsWith('-objectives'))):null,
    previous_units:before.filter(row=>row.to===unit.id).map(row=>row.from),
    components:unit.components.map(id=>components.get(id)),exercises:mappedExercises};
});
const routes=catalog.prerequisite_routes.map(route=>{
  assert.ok(units.has(route.unit));for(const id of route.exercises)assert.equal(exercises.get(id)?.unit,route.unit);
  for(const id of route.sections)anchor(route.unit,id);
  return {...route,required_for_course:route.required_for_b80,href:anchor(route.unit,route.sections[0])};
});
for(const lab of catalog.labs){
  assert.ok(units.has(lab.unit));assert.ok(environments.has(lab.environment));
  for(const id of lab.exercise_ids)assert.equal(exercises.get(id)?.unit,lab.unit);
  for(const id of lab.artifact_ids)assert.ok(artifacts.has(id));
}
const resource={contract:'course-learning-capability/1',course_id:'B80',locale:'id-ID',native_dataset:dataset,
  source_catalog:{...intake.catalog,url:intake.source.catalog_url},units:learningUnits,prerequisite_routes:routes,
  labs:catalog.labs,environments:catalog.environments,artifacts:catalog.artifacts,sources:catalog.sources,
  external_relation_nodes:[...explicitExternalIds].sort(),
  limitations:['This map routes to the native course; it does not run Python or SageMath in the browser.',
    'Native experimental receipts are preserved, not independently rerun by this adapter.',
    'No English translation is included; Indonesian content is labeled id-ID.',
    'The navigation page works offline; linked lessons and course tools require their own downloads.']};
const outputs=new Map();
const put=(path,value)=>outputs.set(path,Buffer.from(typeof value==='string'?value:json(value)));
put(base+'/exchange/shape.json',exchange.shape);
put(base+'/exchange/records.jsonl',serializedRecords);
put(base+'/exchange/reconstructed-catalog.json',json(replay));
put('docs/backend/b80/learning-map.json',resource);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link=(href,label)=>`<a href="${esc(href)}">${esc(label)}</a>`;
const status={complete:'Tersedia',executable:'Pemeriksaan komputasi',not_present:'Tidak tersedia dalam sumber',pending:'Belum tersedia'};
const support=(row,kind,label)=>row[kind].href?link(row[kind].href,label):`<span>${esc(label)}: ${esc(status[row[kind].status])}</span>`;
const styles=`:root{color-scheme:light;--ink:#152f30;--muted:#476568;--edge:#c8d7d1;--paper:#f5f5ed;--accent:#07665f}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:28px 24px 60px}a{color:var(--accent);text-underline-offset:3px}a:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #e39831;outline-offset:3px}.skip{position:absolute;left:-9999px}.skip:focus{left:16px;top:8px;background:white;padding:8px}nav{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:28px}h1{font-size:clamp(1.9rem,4vw,3rem);line-height:1.15;max-width:850px}h2{margin-top:36px}p{max-width:80ch}.muted,small{color:var(--muted)}.filters{display:flex;gap:16px;flex-wrap:wrap;padding:20px 0;border-block:1px solid var(--edge)}label{display:grid;gap:5px}input,select{font:inherit;padding:9px;max-width:100%;border:1px solid var(--edge);border-radius:4px;background:white}.exercise,.unit{border-top:1px solid var(--edge);padding:18px 0}.exercise h3,.unit h3{margin:0 0 8px}.links{display:flex;gap:18px;flex-wrap:wrap}.badge{font-size:.83rem;padding:2px 7px;border:1px solid var(--edge);border-radius:3px}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;background:#fff}th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid var(--edge)}th{background:#e2ece5}details{padding:10px 0}footer{margin-top:45px;padding-top:18px;border-top:1px solid var(--edge);font-size:.9rem}[hidden]{display:none!important}@media print{nav,.filters,.skip{display:none}body{background:white;font-size:10pt}main{max-width:none;padding:0}a{color:inherit}.exercise,.unit{break-inside:avoid}}`;
function shell(title,body,teacher=false){return `<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Peta 14 unit, 75 latihan, laboratorium, dan prasyarat B80 dari katalog sumber yang diverifikasi."><title>${esc(title)} — B80</title><style>${styles}</style></head><body><a class="skip" href="#main">Lewati ke isi</a><main id="main"><nav>${link('../../id/','Program matematika')}${link(teacher?'B80.html':'B80-pengajar.html',teacher?'Untuk pelajar':'Untuk pengajar')}${link(intake.source.repository,'Sumber terbuka')}</nav><p class="muted">B80 · Komputasi matematis · Bahasa Indonesia</p><h1>${esc(title)}</h1>${body}<footer><p>Peta ini dibangun dari katalog asli, bukan salinan buku. Teks: CC BY-SA 4.0; kode: MIT. Hak komponen tetap mengikuti sumbernya. Tidak ada penilaian otomatis atau data pribadi yang dikirim.</p><details><summary>Provenans dan batas penggunaan</summary><p>Katalog sumber: <code>${esc(intake.catalog.sha256)}</code>. Pemeriksaan tautan: ${esc(intake.recorded_at.slice(0,10))}. Halaman ini dapat disimpan untuk navigasi luring; pelajaran yang ditautkan memerlukan unduhan tersendiri. Bukti eksperimen native dipertahankan, bukan dijalankan ulang oleh peta ini.</p>${link('learning-map.json','Data terbuka')}; ${link('validation.json','Bukti pemetaan')}; ${link(intake.source.catalog_url,'Katalog asli')}</details></footer></main></body></html>\n`;}
const unitMenu=learningUnits.map(unit=>`<option value="${esc(unit.id)}">${esc(unit.title)}</option>`).join('');
const rows=learningUnits.flatMap(unit=>unit.exercises.map(ex=>`<article class="exercise" id="${esc(ex.id)}" data-unit="${esc(unit.id)}" data-kind="${esc(ex.kind)}"><p class="muted">${esc(unit.title)} · <span class="badge">${ex.kind==='mastery'?'Penguasaan':'Latihan inti'}</span>${ex.curriculum_status==='prerequisite_deferred'?' · Lanjutan berprasyarat':''}</p><h3>${link(ex.href,ex.title)}</h3><div class="links">${support(ex,'hint','Petunjuk')}${support(ex,'check','Pemeriksaan')}${support(ex,'solution','Solusi')}</div></article>`)).join('');
const script=`<script>const q=document.querySelector('#query'),unit=document.querySelector('#unit'),kind=document.querySelector('#kind'),rows=[...document.querySelectorAll('.exercise')];function update(){let visible=0;for(const row of rows){const show=(!unit.value||row.dataset.unit===unit.value)&&(!kind.value||row.dataset.kind===kind.value)&&row.textContent.toLocaleLowerCase('id').includes(q.value.toLocaleLowerCase('id').trim());row.hidden=!show;visible+=show?1:0}document.querySelector('#count').textContent=visible+' dari '+rows.length+' latihan ditampilkan.'}for(const control of [q,unit,kind])control.addEventListener('input',update);update();</script>`;
put('docs/backend/b80/B80.html',shell('Baca, berlatih, dan periksa hasil',`<p>14 unit dan 75 latihan dengan tautan langsung ke pelajaran, petunjuk, pemeriksaan, dan solusi sumber.</p><details><summary>Mulai dari unit</summary>${learningUnits.map(unit=>`<p>${link(unit.href,unit.title)}</p>`).join('')}</details><div class="filters"><label>Cari latihan<input id="query" type="search" placeholder="Judul atau topik"></label><label>Unit<select id="unit"><option value="">Semua unit</option>${unitMenu}</select></label><label>Jenis<select id="kind"><option value="">Semua jenis</option><option value="core">Latihan inti</option><option value="mastery">Penguasaan</option></select></label></div><p id="count" role="status" aria-live="polite">75 latihan ditampilkan.</p><section aria-label="Daftar latihan">${rows}</section>${script}`));
const teacherRows=learningUnits.map(unit=>`<tr><th scope="row">${link(unit.href,unit.title)}</th><td>${unit.objectives_href?link(unit.objectives_href,'Tujuan pembelajaran'):'Tujuan khusus belum diindeks'}</td><td>${unit.previous_units.map(id=>link(pages.get(id).url,units.get(id).title)).join('<br>')||'Awal urutan'}</td><td>${unit.exercises.map(ex=>link('B80.html#'+ex.id,ex.title)).join('<br>')}</td></tr>`).join('');
const routeRows=routes.map(route=>`<li>${link(route.href,route.title)} — ${route.required_for_b80?'inti B80':'pengayaan, bukan syarat penyelesaian B80'}; prasyarat ${link('../../id/#course-'+route.prerequisite,route.prerequisite)}.</li>`).join('');
const labs=catalog.labs.map(lab=>`<section class="unit"><h3>${link(pages.get(lab.unit).url,units.get(lab.unit).title)} · ${esc(lab.kind)}</h3><p>${lab.exercise_ids.map(id=>link('B80.html#'+id,exercises.get(id).title)).join(' · ')}</p><p>Lingkungan yang dicatat sumber: ${esc(environments.get(lab.environment).runtime_version)}. Artefak: ${lab.artifact_ids.map(id=>esc(artifacts.get(id).path)).join(', ')}.</p><ul>${lab.requirements.map(text=>`<li lang="en">${esc(text)}</li>`).join('')}</ul></section>`).join('');
const optionalPrerequisites=routes.filter(route=>!route.required_for_b80).map(route=>route.prerequisite);
put('docs/backend/b80/B80-pengajar.html',shell('Panduan unit dan kegiatan untuk pengajar',`<p>Urutan pelajaran, tujuan yang ditautkan ke sumber, latihan dengan dukungan bertahap, ${catalog.labs.length} laboratorium, serta jalur pengayaan. Identitas unit dan latihan sama dengan tampilan pelajar.</p><h2>Rencana unit</h2><div class="scroll"><table><caption>${learningUnits.length} unit dengan tujuan dan latihan sumber</caption><thead><tr><th>Unit</th><th>Tujuan</th><th>Unit sebelumnya</th><th>Latihan</th></tr></thead><tbody>${teacherRows}</tbody></table></div><h2>Prasyarat inti dan pengayaan</h2><p>B80 dimulai setelah ${esc(catalog.course.prerequisite)}. ${optionalPrerequisites.length} jalur tambahan memakai materi ${esc(optionalPrerequisites.join(', '))}; jalur tersebut tidak menjadi syarat untuk menyelesaikan inti B80.</p><ul>${routeRows}</ul><h2>Laboratorium</h2>${labs}`,true));
const manifest={contract:'course-learning-capability/1',course_id:'B80',native_family_id:'family-09-mathematical-computing',
  inputs:[{path:base+'/input/catalog.json',bytes:inputBytes.length,sha256:sha256(inputBytes)},
    {path:base+'/input/catalog.schema.json',bytes:schemaBytes.length,sha256:sha256(schemaBytes)},
    {path:base+'/input/public-intake.json',bytes:intakeBytes.length,sha256:sha256(intakeBytes)},...contractSchemas],
  outputs:[...outputs].map(([path,bytes])=>({path,bytes:bytes.length,sha256:sha256(bytes)})),
  counts:{native_records:exchange.records.length,units:learningUnits.length,exercises:exercises.size,labs:catalog.labs.length,prerequisite_routes:routes.length},
  exchange:{native_ids_preserved:true,array_order_preserved:true,native_values_roundtrip:true,full_reader_copied:false},
  adoption:['unit_and_exercise_identity','structured_support_states','prerequisite_routes','lab_environment_artifact_bindings','component_rights','learner_and_educator_views'],
  public_release_status:'not_yet_published',contract_2_3_1_conformance:'not_claimed',limitations:resource.limitations};
put(base+'/manifest.json',manifest);
for(const [path,bytes] of outputs){await mkdir(dirname(resolve(outputRoot,path)),{recursive:true});await writeFile(resolve(outputRoot,path),bytes);}
console.log(JSON.stringify({state:'pass',...manifest.counts,output_files:outputs.size,manifest_sha256:sha256(outputs.get(base+'/manifest.json'))}));
