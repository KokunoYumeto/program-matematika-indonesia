import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

export const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
export const base='backend/course-capsule-v1/adapters/d50-surface-v1';
export const sha=b=>createHash('sha256').update(b).digest('hex');
export const json=x=>JSON.stringify(x,null,2)+'\n';
const esc=x=>String(x??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');

export async function load(){
  const b=await readFile(resolve(root,base,'input/source-lock.json')),lock=JSON.parse(b),files={};
  assert.equal(lock.schema,'d50-consumer-input-lock/1');
  for(const f of [...lock.inputs,lock.authority,lock.witness]){
    assert.ok(f.path.startsWith('backend/')&&!f.path.includes('..'));
    const data=await readFile(resolve(root,f.path));assert.equal(data.length,f.bytes);assert.equal(sha(data),f.sha256,f.path);files[f.path.split('/').at(-1)]=data;
  }
  return {lock,identity:{path:base+'/input/source-lock.json',bytes:b.length,sha256:sha(b)},
    records:files['records.jsonl'].toString('utf8').trim().split('\n').map(JSON.parse),
    witness:JSON.parse(files['reader-witness.json']),manifest:JSON.parse(files['reader-manifest.json'])};
}

export function project(input){
  const {records,witness:w,manifest:m,lock,identity}=input;
  assert.equal(w.schema,'d50-portable-reader-witness/1');assert.equal(w.content_locale,'id-ID');assert.equal(lock.content_locale,'id-ID');
  assert.equal(w.hosted_reader_url,null);assert.equal(w.reader.path,'index.html');
  assert.match(w.archive.url,/^https:\/\/github\.com\/KokunoYumeto\/brenner-differentialgeometrie-id\/releases\/download\/v1\.0\.1\//);
  assert.deepEqual(w.reader,m.files.find(f=>f.path==='index.html'));
  const ids=new Map(records.map(r=>[r.id,r]));assert.equal(ids.size,records.length,'Duplicate native ID');
  const native=records.filter(r=>['unit','segment'].includes(r.entity_type));
  const relations=records.filter(r=>r.entity_type==='relation');
  const rightIds=new Set(records.filter(r=>r.entity_type==='rights').map(r=>r.id));
  const byKind=k=>native.filter(r=>r.unit_kind===k);
  const semantic=byKind('semantic_exam_problem'),placeholders=byKind('exam_placeholder_slot');
  const omitted=new Set([...semantic,...placeholders].map(r=>r.id));
  const units=[],routeFor=(r)=>{
    const direct=[...new Set([r.id,r.reader_anchor].filter(a=>a&&w.anchor_counts[a]===1))];
    assert.ok(direct.length<=1,`Ambiguous direct route: ${r.id}`);
    let anchor=direct[0],state='exact_native_anchor',reason='native_id_or_declared_reader_anchor';
    const exam=/^o011-exam-f(\d{2})(?:-slot-(\d{3})(-source-solution)?|-(learner|solutions))?$/.exec(r.id);
    if(!anchor&&exam){
      const [,form,slot,solution,part]=exam,topology=m.exam_topology[form];assert.ok(topology);
      if(slot){
        assert.ok(topology.actual_occurrence_slots.includes(Number(slot)),`Not an actual exam slot: ${r.id}`);
        anchor=`o011-exam-${form}-p${slot}${solution?'-source-solution':''}`;
        assert.equal(w.anchors[anchor]?.['data-entity'],solution?'source-supplied-exam-solution':'exam-problem');
        if(solution)assert.equal(w.anchors[anchor]['data-solves'],`o011-exam-${form}-p${slot}`);
        state='exact_renderer_crosswalk';reason='producer_exam_slot_rule_and_manifest';
      }else{anchor=`ujian-${form}`;state=part?'enclosing_exam_form':'exact_renderer_crosswalk';reason=part?'subsection_has_no_separate_anchor':'producer_exam_form_rule';}
    }
    if(!anchor&&r.unit_kind==='official_exam_bank'){anchor='bank-ujian';state='exact_renderer_crosswalk';reason='producer_exam_bank_rule';}
    if(!anchor&&r.unit_kind==='original_bridge_assessment'){
      const prefix=r.id.includes('de-rham')?'de-rham-assessment-':'lie-assessment-';
      const candidates=Object.keys(w.anchors).filter(a=>a.startsWith(prefix)&&a.endsWith('latihan-petunjuk-bertahap-dan-solusi'));
      assert.equal(candidates.length,1);anchor=candidates[0];state='exact_renderer_crosswalk';reason='namespaced_assessment_heading';
    }
    if(!anchor&&r.segment_kind==='source_supplied_hint'){
      assert.equal(r.id,'o011-brenner-u05-w05-e013-hint');anchor=r.parent_id;
      state='enclosing_exercise';reason='inline_hint_has_no_separate_anchor';
    }
    assert.ok(anchor,`Unmapped native record: ${r.id}`);assert.equal(w.anchor_counts[anchor],1,`Nonunique anchor: ${r.id}`);
    return {anchor,state,reason,portable_href:`reader/index.html#${anchor}`,reader:w.reader};
  };
  const groupFor=r=>{
    const seen=new Set();let node=r;
    while(node.parent_id!=='o011-course-d50'){
      assert.ok(!seen.has(node.id),'Parent cycle');seen.add(node.id);node=ids.get(node.parent_id);assert.ok(node,`Missing parent: ${r.id}`);
    }
    return node.id;
  };
  for(const r of native){
    assert.equal(r.locale,'id-ID',`Content locale: ${r.id}`);assert.ok(rightIds.has(r.rights_component_id),`Missing rights: ${r.id}`);
    if(omitted.has(r.id))continue;
    const kind=r.unit_kind??r.segment_kind,route=routeFor(r);
    units.push({id:r.id,kind,group:groupFor(r),parent_id:r.parent_id,order:r.order??0,title:r.title??null,
      locale:'id-ID',practice:['exercise','exam_problem_occurrence','original_bridge_exercise','original_bridge_mastery_problem'].includes(kind),
      route,rights_ids:[r.rights_component_id],source_record:r,support:[],concept_ids:[],
      solution_provenance:r.solution_provenance??(['solution','source_supplied_solution','source_supplied_exam_solution'].includes(kind)?'official_source_supplied':null),
      inline_original_solution:r.complete_solution_present===true});
  }
  const projected=new Map(units.map(u=>[u.id,u]));
  const supportRelations=relations.filter(r=>r.relation_type==='solves'||r.relation_type==='annotates');
  const semanticSupports=[];
  for(const r of supportRelations){
    assert.ok(projected.has(r.from_id),`Unknown support source: ${r.id}`);
    const from=projected.get(r.from_id),fact={id:r.id,type:r.relation_type,from:r.from_id,to:r.to_id,
      provenance:from.solution_provenance??'official_source_supplied_hint',source_record:r};
    if(projected.has(r.to_id))projected.get(r.to_id).support.push(fact);
    else{assert.ok(semantic.some(s=>s.id===r.to_id),`Unknown support target: ${r.id}`);semanticSupports.push(fact);}
  }
  const occurrenceEdges=relations.filter(r=>r.relation_type==='occurrence_of');
  const semanticGroups=semantic.map(r=>{
    const occurrenceIds=occurrenceEdges.filter(e=>e.to_id===r.id).map(e=>e.from_id);
    assert.equal(occurrenceIds.length,r.occurrence_count);assert.ok(occurrenceIds.length>0);
    for(const id of occurrenceIds){const u=projected.get(id);assert.equal(u?.source_record.semantic_problem_id,r.id);assert.equal(u.kind,'exam_problem_occurrence');}
    return {id:r.id,source_record:r,occurrence_ids:occurrenceIds,support:semanticSupports.filter(s=>s.to===r.id),
      reason:'shared_semantic_identity_not_an_additional_exercise'};
  });
  assert.equal(occurrenceEdges.length,byKind('exam_problem_occurrence').length);
  for(const r of placeholders){
    assert.equal(r.actual_problem,false);assert.equal(r.point_marker,'0');
    const match=/^o011-exam-f(\d{2})-slot-(\d{3})$/.exec(r.id);assert.ok(match);
    assert.ok(m.exam_topology[match[1]].zero_point_placeholder_slots.includes(Number(match[2])));
    assert.ok(!w.anchors[`o011-exam-${match[1]}-p${match[2]}`]);
  }
  const conceptRecords=records.filter(r=>r.entity_type==='concept'),conceptIds=new Set(conceptRecords.map(c=>c.id));
  const conceptEdges=relations.filter(r=>r.relation_type==='covers');
  for(const r of conceptEdges){assert.ok(projected.has(r.from_id)&&conceptIds.has(r.to_id));projected.get(r.from_id).concept_ids.push(r.to_id);}
  const prerequisites=relations.filter(r=>r.relation_type==='requires');
  for(const r of prerequisites)assert.ok(projected.has(r.from_id)&&projected.has(r.to_id));
  for(const u of units.filter(u=>u.kind==='exercise')){
    const supplied=u.support.filter(s=>s.type==='solves'&&s.provenance==='official_source_supplied');
    assert.equal(supplied.length,u.source_record.has_authority_solution?1:0,`Worksheet solution mismatch: ${u.id}`);
  }
  for(const u of units.filter(u=>u.kind==='exam_problem_occurrence')){
    const solutions=u.support.filter(s=>s.type==='solves');assert.equal(solutions.length,1);
    assert.equal(solutions[0].provenance,u.source_record.has_authority_solution?'official_source_supplied':'original_not_source_supplied');
    assert.equal(projected.get(solutions[0].from).source_record.occurrence_id,u.id);
  }
  const anchorOrder=new Map(Object.keys(w.anchors).map((id,n)=>[id,n]));
  units.sort((a,b)=>anchorOrder.get(a.route.anchor)-anchorOrder.get(b.route.anchor)||a.id.localeCompare(b.id,'en'));
  const counts={native_records:records.length,native_units:native.filter(r=>r.entity_type==='unit').length,
    native_segments:native.filter(r=>r.entity_type==='segment').length,selectable_units:units.length,
    lecture_worksheet_pairs:byKind('lecture_worksheet_pair').length,worksheet_exercises:byKind('exercise').length,
    worksheet_source_solutions:byKind('solution').length+byKind('source_supplied_solution').length,
    exam_occurrences:byKind('exam_problem_occurrence').length,semantic_exam_problems:semantic.length,placeholder_slots:placeholders.length,
    exam_source_solutions:byKind('source_supplied_exam_solution').length,original_exam_repairs:byKind('original_exam_solution_repair').length,
    original_bridge_practice:byKind('original_bridge_exercise').length+byKind('original_bridge_mastery_problem').length,
    selectable_practice:units.filter(u=>u.practice).length,concepts:conceptRecords.length,concept_edges:conceptEdges.length,
    prerequisite_edges:prerequisites.length,native_support_edges:supportRelations.length,
    exact_routes:units.filter(u=>u.route.state.startsWith('exact_')).length,enclosing_routes:units.filter(u=>u.route.state.startsWith('enclosing_')).length};
  return {schema:'d50-portable-study-map/1',course_id:'D50',content_locale:'id-ID',interface_locales:['id','en'],
    identity_namespace:'o011-modular-backend',counts,units,semantic_exam_groups:semanticGroups,placeholder_slots:placeholders,
    concepts:conceptRecords,concept_relations:conceptEdges,prerequisites,occurrence_relations:occurrenceEdges,
    support_relations:supportRelations,rights:records.filter(r=>r.entity_type==='rights'),
    source_witness:identity,inputs:lock.inputs,reader_archive:w.archive,reader:w.reader,hosted_reader_url:null,
    model_disclosure:{original_translation:w.source_model_identification,integration:'OpenAI Codex — GPT-6 Astra, Ultra effort'},
    limitations:{id:['Bacaan berbahasa Indonesia; pilihan English hanya mengubah antarmuka alat.',
      '123 kemunculan soal ujian mewakili 119 soal berbeda. Sebanyak 24 tempat kosong bukan latihan tambahan.',
      '492 latihan lembar kerja tidak memiliki solusi sumber tercatat. Tidak ada solusi baru yang dibuat oleh alat ini.',
      '20 subbagian ujian dan satu petunjuk ditautkan ke bagian induk karena tidak memiliki jangkar tersendiri.',
      'Kaitan konsep hanya tersedia untuk unit yang benar-benar ditandai dalam metadata sumber; ini bukan pemetaan konsep lengkap.',
      'Alat ini menggunakan paket bacaan luring yang sudah diterbitkan. Tidak ada alamat pembaca daring baru yang dinyatakan tersedia.',
      'Identitas semantik, sumber solusi, lisensi komponen, dan catatan asli tetap dibedakan.'],
      en:['Readings are Indonesian; English changes only the tool interface.',
      '123 exam occurrences represent 119 distinct problems. The 24 empty slots are not additional exercises.',
      '492 worksheet exercises have no recorded source solution. This tool generates no new solutions.',
      '20 exam subsections and one hint link to their enclosing section because they have no separate anchor.',
      'Concept links cover only units actually tagged in the source metadata, not the entire curriculum.',
      'The tool uses the already published offline reader package; it claims no new hosted reader address.',
      'Semantic identities, solution provenance, component rights and original records remain distinct.']}};
}

export async function build(){
  const map=project(await load()),out=resolve(root,base,'portable');await mkdir(out,{recursive:true});
  await writeFile(resolve(out,'learning-map.json'),json(map));
  await writeFile(resolve(out,'data.js'),'globalThis.D50_DATA='+JSON.stringify(map)+';\n');
  for(const lang of ['id','en'])for(const teacher of [false,true]){
    const t=(a,b)=>esc(lang==='id'?a:b),title=t('Geometri Diferensial · Rencana belajar dan mengajar','Differential Geometry · Study and teaching plans');
    const filename=`${teacher?'teacher':'index'}${lang==='en'?'.en':''}.html`;
    await writeFile(resolve(out,filename),`<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'"><title>D50 · ${title}</title><link rel="stylesheet" href="style.css"><script defer src="data.js"></script><script defer src="study-plan.js"></script></head><body data-language="${lang}" data-mode="${teacher?'teacher':'learner'}"><a href="#main">${t('Langsung ke isi','Skip to content')}</a><nav><a href="index.html">Bahasa Indonesia</a> · <a href="index.en.html">English</a> · <a href="${teacher?'index':'teacher'}${lang==='en'?'.en':''}.html">${t(teacher?'Untuk pelajar':'Untuk pengajar',teacher?'For learners':'For teachers')}</a> · <a href="https://kokunoyumeto.github.io/program-matematika-indonesia/${lang}/#course-D50">${t('Program matematika','Mathematics program')}</a></nav><main id="main"><h1>D50 · ${title}</h1><p>${t('Pilih bacaan, latihan, atau soal ujian. Simpan rencana beserta ID dan asal sumbernya tanpa mengirimkan data ke server.','Choose readings, exercises or exam problems. Save a plan with its IDs and source information without sending data to a server.')}</p><p class="notice">${t('Gunakan alat ini di dalam paket luring: folder reader harus berada di samping halaman ini. Bacaan tetap dalam Bahasa Indonesia.','Use this tool inside the offline package: the reader folder must be beside this page. Readings remain in Indonesian.')}</p><p>29 ${t('unit kuliah','lecture units')} · 576 ${t('latihan lembar kerja','worksheet exercises')} · 123 ${t('kemunculan soal ujian','exam occurrences')} · 32 ${t('soal jembatan dengan solusi asli','bridge problems with original solutions')}</p><p><a href="reader/index.html">${t('Buka bacaan lengkap','Open the complete reader')}</a></p><section id="controls" hidden><h2>${t('Susun rencana','Build a plan')}</h2><div class="filters"><label>${t('Cari judul atau ID','Search title or ID')}<input id="search" type="search"></label><label>${t('Jenis','Kind')}<select id="kind"></select></label><label>${t('Kelompok','Group')}<select id="group"></select></label><label>${t('Konsep yang tercatat','Recorded concept')}<select id="concept"></select></label></div><div class="toolbar"><button id="select-page">${t('Pilih halaman ini','Select this page')}</button><button id="clear">${t('Kosongkan pilihan','Clear selection')}</button><button id="export">${t('Unduh rencana JSON','Download JSON plan')}</button><span id="selection" role="status"></span></div><p id="results" role="status"></p><div id="items"></div><div class="toolbar"><button id="previous">${t('Sebelumnya','Previous')}</button><button id="next">${t('Berikutnya','Next')}</button></div></section><noscript><p>${t('Bacaan tetap dapat dibuka. Pemilih rencana memerlukan JavaScript.','The reader still opens. Plan selection requires JavaScript.')}</p></noscript><section><h2>${t('Sumber dan batas cakupan','Sources and scope')}</h2><ul>${map.limitations[lang].map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p>${t('Terjemahan dan bahan asli sumber','Source translation and original materials')}: ${esc(map.model_disclosure.original_translation)}. ${t('Integrasi metadata dan alat','Metadata integration and tools')}: ${esc(map.model_disclosure.integration)}.</p><p><a href="${esc(map.reader_archive.url)}">${t('Arsip HTML sumber terverifikasi','Verified original HTML archive')}</a> · <a href="learning-map.json">${t('Data yang dapat digunakan ulang','Reusable data')}</a></p></section></main></body></html>\n`);
  }
  await writeFile(resolve(out,'study-plan.js'),await readFile(resolve(root,'scripts/d50-study-plan-ui-v1.js')));
  await writeFile(resolve(out,'style.css'),`body{font:18px/1.6 system-ui,sans-serif;max-width:1100px;margin:auto;padding:1rem;background:#faf9f6;color:#172a33}a{color:#135875;overflow-wrap:anywhere}nav,.toolbar{display:flex;gap:1rem;flex-wrap:wrap}h1{line-height:1.2}label{display:flex;flex-direction:column}.filters{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem}button,input,select{font:inherit;padding:.4rem;max-width:100%}article{border:1px solid #b8c9cd;border-radius:8px;padding:1rem;margin:1rem 0;overflow-wrap:anywhere}.notice{padding:1rem;background:#e5eff0}pre{white-space:pre-wrap;font-size:14px;overflow-wrap:anywhere}small{display:block}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #bc6200;outline-offset:3px}\n`);
  return map;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))console.log(json({state:'built',counts:(await build()).counts}));
